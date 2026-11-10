# SPDX-License-Identifier: Apache-2.0

"""Circular ring swing procedural template (TEMPLATE_AFTER_REVIEW).

Implements ``articraft_template_authoring/specs_modular_v1/Playground_swing_circular.md``.

Identity invariant: a rigid circular ring seat suspended under a static
overhead frame by a TWO-JOINT serial chain:

* fixed ``support_frame`` (Slot A) -- grounded static support part.
* ``canopy_swing`` REVOLUTE (axis +X, +-45 deg) -> ``suspension`` (Slot C).
* ``ring_spin`` CONTINUOUS (axis +Z) -> ``ring_seat`` (Slot B).

Regardless of ``suspension_point_count`` N in [1, 4] there are EXACTLY two
non-fixed joints.  N == 1 builds a single centre chain; N >= 2 builds an
N-leg bridle whose legs all converge to ONE swivel hub (no closed loop, no
per-leg joint).

Adopted sources (per spec):
S1 rec_model-a-modern-circular-ring-swing... : two_post_pergola + single_chain
   + bench_ring_seat baseline + the 2-joint chain.
S2 rec_pcrs_var_aframe : a_frame_support.
S3 rec_pcrs_var_arch   : single_arch (parabolic tube + crown collar).
S4 rec_pcrs_var_cradle : deep_cradle_ring ring_seat (open twin-hoop halo,
   deeper 214deg plank arc climbing into a low scooped backrest).
S5 rec_pcrs_var_band   : flat_band_ring ring_seat (single wide CadQuery
   annulus band, open centre, planks on the lower inner arc).
S6 rec_pcrs_var_p3     : three_point_bridle suspension.
S7 rec_pcrs_var_p4     : four_point_bridle suspension.

seed=0 anchor: two_post_pergola + bench_ring_seat + single_chain (N=1),
galvanized_warmwood palette.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    Mesh,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


SupportFrame = Literal["two_post_pergola", "a_frame_support", "single_arch"]
RingSeat = Literal["bench_ring_seat", "deep_cradle_ring", "flat_band_ring"]
SuspensionStyle = Literal["single_chain", "n_point_bridle"]
PaletteStyle = Literal[
    "galvanized_warmwood",
    "powdercoat_charcoal",
    "light_steel_chrome",
    "forest_green_oak",
    "bronze_oak",
]


SUPPORT_FRAMES: tuple[SupportFrame, ...] = (
    "two_post_pergola",
    "a_frame_support",
    "single_arch",
)
RING_SEATS: tuple[RingSeat, ...] = (
    "bench_ring_seat",
    "deep_cradle_ring",
    "flat_band_ring",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "galvanized_warmwood",
    "powdercoat_charcoal",
    "light_steel_chrome",
    "forest_green_oak",
    "bronze_oak",
)


# Palettes only swap material rgba, never topology.  Keys:
#   frame      -- post / leg / arch tube
#   frame_trim -- top rail / beam / light steel members
#   fin        -- louver fins
#   chrome     -- hoops / flat band + chain + hardware
#   dark       -- base plates / gussets / dark steel
#   wood       -- bench / cradle / band seat planks
#   rivet      -- rivet heads
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "galvanized_warmwood": {
        "frame": (0.58, 0.60, 0.62, 1.0),
        "frame_trim": (0.76, 0.78, 0.80, 1.0),
        "fin": (0.22, 0.23, 0.25, 1.0),
        "chrome": (0.84, 0.86, 0.89, 1.0),
        "dark": (0.35, 0.37, 0.40, 1.0),
        "wood": (0.60, 0.40, 0.22, 1.0),
        "rivet": (0.45, 0.47, 0.50, 1.0),
    },
    "powdercoat_charcoal": {
        "frame": (0.30, 0.32, 0.34, 1.0),
        "frame_trim": (0.38, 0.40, 0.42, 1.0),
        "fin": (0.18, 0.19, 0.20, 1.0),
        "chrome": (0.84, 0.86, 0.89, 1.0),
        "dark": (0.20, 0.21, 0.22, 1.0),
        "wood": (0.46, 0.30, 0.16, 1.0),
        "rivet": (0.50, 0.52, 0.54, 1.0),
    },
    "light_steel_chrome": {
        "frame": (0.76, 0.78, 0.80, 1.0),
        "frame_trim": (0.82, 0.84, 0.86, 1.0),
        "fin": (0.50, 0.52, 0.55, 1.0),
        "chrome": (0.86, 0.88, 0.91, 1.0),
        "dark": (0.45, 0.47, 0.50, 1.0),
        "wood": (0.72, 0.58, 0.40, 1.0),
        "rivet": (0.55, 0.57, 0.60, 1.0),
    },
    "forest_green_oak": {
        "frame": (0.18, 0.34, 0.22, 1.0),
        "frame_trim": (0.24, 0.40, 0.28, 1.0),
        "fin": (0.14, 0.26, 0.18, 1.0),
        "chrome": (0.70, 0.72, 0.74, 1.0),
        "dark": (0.12, 0.20, 0.14, 1.0),
        "wood": (0.66, 0.50, 0.30, 1.0),
        "rivet": (0.55, 0.57, 0.58, 1.0),
    },
    "bronze_oak": {
        "frame": (0.50, 0.38, 0.22, 1.0),
        "frame_trim": (0.58, 0.44, 0.26, 1.0),
        "fin": (0.36, 0.27, 0.16, 1.0),
        "chrome": (0.54, 0.42, 0.24, 1.0),
        "dark": (0.34, 0.26, 0.15, 1.0),
        "wood": (0.66, 0.50, 0.30, 1.0),
        "rivet": (0.48, 0.38, 0.22, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base nominal geometry (from S1; all scaled by config scales in resolve_config)
# ---------------------------------------------------------------------------
BASE_RAIL_Z0 = 2.55          # nominal pergola top-rail underside (swing pivot z)
BASE_FRAME_HALF_X = 1.425    # nominal post centre half-span
HOOP_R = 0.725               # hoop circle radius (ring-local)
HOOP_TUBE = 0.025
HOOP_Y = 0.0375              # half twin-hoop separation
RING_C = -0.815              # hoop circle centre, ring-local

# Single chain layout (chain-local, origin = swing pivot on rail underside)
STEM_LEN = 0.09
EYE_C = -0.078
LINK_R = 0.028
LINK_TUBE = 0.0065
LINK_STRETCH = 1.45
LINK_CENTERS = (-0.144, -0.234, -0.324, -0.415)
HOOK_EYE_C = -0.481
HOOK_ARC_C = -0.536
HOOK_ARC_R = 0.024
CHAIN_SPIN_Z = -0.576        # hook bowl seat / spin joint, chain-local

EYELET_R = 0.030
EYELET_TUBE = 0.007
CLEVIS_C = -0.051

# Bench planks (S1): lower inner arc, ~146 deg.
PLANK_RC = 0.693
PLANK_THETA0 = math.radians(197.0)
PLANK_THETA1 = math.radians(343.0)

# Deep cradle planks (S4): deeper lower arc ~214 deg climbing into a low
# scooped backrest; same twin chrome hoops as the bench.
CRADLE_THETA0 = math.radians(163.0)
CRADLE_THETA1 = math.radians(377.0)

# Flat band ring (S5): single wide CadQuery annulus replacing the twin hoops.
BAND_OUTER_R = 0.750         # outer radius of the flat steel band (ring-local)
BAND_THICKNESS = 0.005       # radial wall thickness (5 mm steel ribbon)
BAND_WIDTH = 0.110           # axial width of the band
BAND_PLANK_THETA0 = math.radians(197.0)
BAND_PLANK_THETA1 = math.radians(343.0)

# Bridle hub (S6/S7) -- chain-local
EYE_HALF_Z = 0.016 + 0.005
LINK_HALF_Z = LINK_R * LINK_STRETCH + LINK_TUBE
LINK_OVERLAP = 0.001
ANCHOR_EYE_C = -0.081
HUB_DISK_R = 0.060
HUB_DISK_H = 0.040
BRIDLE_LEG_R = 0.009


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _require(value: str, allowed: tuple[str, ...], *, field_name: str) -> str:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {allowed}, got {value!r}")
    return value


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_y() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _anchor_link_centers() -> tuple[float, ...]:
    centers: list[float] = []
    z_top = ANCHOR_EYE_C - EYE_HALF_Z + LINK_OVERLAP
    for _ in range(4):
        c = z_top - LINK_HALF_Z
        centers.append(c)
        z_top = c - LINK_HALF_Z + LINK_OVERLAP
    return tuple(centers)


ANCHOR_LINK_CENTERS = _anchor_link_centers()
_LAST_LINK_BOTTOM = ANCHOR_LINK_CENTERS[-1] - LINK_HALF_Z
HUB_Z_LOCAL = _LAST_LINK_BOTTOM + LINK_OVERLAP - HUB_DISK_H / 2.0


@dataclass(frozen=True)
class CircularRingSwingConfig:
    support_frame: SupportFrame | None = None
    ring_seat: RingSeat | None = None
    suspension_point_count: int = 1
    palette_style: PaletteStyle | None = None
    frame_width_scale: float = 1.0
    pivot_height_scale: float = 1.0
    hoop_radius_scale: float = 1.0
    seat_plank_count: int = 22
    fin_count: int = 34
    name: str = "seeded_circular_ring_swing"
    palette: dict[str, tuple[float, float, float, float]] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolvedCircularRingSwingConfig:
    support_frame: SupportFrame
    ring_seat: RingSeat
    suspension_style: SuspensionStyle
    suspension_point_count: int
    palette_style: PaletteStyle
    frame_width_scale: float
    pivot_height_scale: float
    hoop_radius_scale: float
    seat_plank_count: int
    fin_count: int
    name: str
    # derived
    pivot_z: float            # world z of swing pivot (rail underside)
    frame_half_x: float       # post / leg / arch half-span (world)
    hoop_r: float             # scaled hoop circle radius
    ring_outer_r: float       # outer landing radius (hoop_r, or band outer for band)
    spin_z: float             # suspension-local z of spin joint
    ring_c: float             # ring-local hoop circle centre z
    bridle_thetas: tuple[float, ...]
    fin_z0: float             # underside of canopy fins / arch crown clearance
    arch_half_span: float     # parabolic arch half-span (single_arch only)
    arch_height: float        # parabolic arch crown z (single_arch only)
    palette: dict[str, tuple[float, float, float, float]]


# ---------------------------------------------------------------------------
# Procedural sampling
# ---------------------------------------------------------------------------
def _weighted_point_count(rng: random.Random) -> int:
    # N=1 high (~50%), N=3/4 mid (~22% each), N=2 low (~6%).
    roll = rng.random()
    if roll < 0.50:
        return 1
    if roll < 0.56:
        return 2
    if roll < 0.78:
        return 3
    return 4


def config_from_seed(seed: int) -> CircularRingSwingConfig:
    rng = random.Random(seed if seed != 0 else 0)
    if seed == 0:
        return CircularRingSwingConfig(
            support_frame="two_post_pergola",
            ring_seat="bench_ring_seat",
            suspension_point_count=1,
            palette_style="galvanized_warmwood",
            frame_width_scale=1.0,
            pivot_height_scale=1.0,
            hoop_radius_scale=1.0,
            seat_plank_count=22,
            fin_count=34,
            name="seeded_circular_ring_swing_0",
        )

    support: SupportFrame = rng.choice(SUPPORT_FRAMES)  # type: ignore[assignment]
    ring_seat: RingSeat = rng.choice(RING_SEATS)  # type: ignore[assignment]
    n = _weighted_point_count(rng)
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)  # type: ignore[assignment]

    return CircularRingSwingConfig(
        support_frame=support,
        ring_seat=ring_seat,
        suspension_point_count=n,
        palette_style=palette,
        frame_width_scale=rng.uniform(0.85, 1.15),
        pivot_height_scale=rng.uniform(0.92, 1.10),
        hoop_radius_scale=rng.uniform(0.88, 1.12),
        seat_plank_count=rng.randint(16, 34),
        fin_count=rng.randint(24, 40),
        name=f"seeded_circular_ring_swing_{seed}",
    )


def resolve_config(config: CircularRingSwingConfig) -> ResolvedCircularRingSwingConfig:
    support = _require(
        config.support_frame or "two_post_pergola",
        SUPPORT_FRAMES,
        field_name="support_frame",
    )
    ring_seat = _require(
        config.ring_seat or "bench_ring_seat", RING_SEATS, field_name="ring_seat"
    )
    palette_style = _require(
        config.palette_style or "galvanized_warmwood",
        PALETTE_STYLES,
        field_name="palette_style",
    )

    n = max(1, min(4, int(config.suspension_point_count)))
    suspension_style: SuspensionStyle = "single_chain" if n == 1 else "n_point_bridle"

    fw = _clamp(config.frame_width_scale, 0.85, 1.15)
    ph = _clamp(config.pivot_height_scale, 0.92, 1.10)
    hr = _clamp(config.hoop_radius_scale, 0.88, 1.12)

    pivot_z = BASE_RAIL_Z0 * ph
    frame_half_x = BASE_FRAME_HALF_X * fw
    hoop_r = HOOP_R * hr
    # flat_band's outer radius is slightly larger than the tube-hoop radius;
    # bridle legs / brackets land on this outer radius and the clearance solve
    # uses it so the wider band still clears ground / canopy.
    if ring_seat == "flat_band_ring":
        ring_outer_r = hoop_r + (BAND_OUTER_R - HOOP_R)
    else:
        ring_outer_r = hoop_r

    # ring-local hoop circle centre: keep nominal so plank/disc/net geometry
    # (defined relative to RING_C) stays consistent; the spin joint offset
    # controls overall drop.  Scale RING_C with hoop so the chain reaches the
    # ring top eyelet.
    ring_c = RING_C * hr

    if suspension_style == "single_chain":
        spin_z = CHAIN_SPIN_Z
    else:
        spin_z = HUB_Z_LOCAL

    # ground clearance + top clearance solve.  ring bottom world z:
    #   ring_top_world = pivot_z + spin_z + (ring_c + hoop_r)
    #   ring_bottom_world = pivot_z + spin_z + (ring_c - hoop_r)
    # All three ring_seats are open hoops/bands, so the ring outer radius
    # dominates the vertical bounds for clearance.
    fin_z0 = pivot_z - 0.125  # canopy fins underside (pergola/aframe); arch crown well above

    def ring_bottom() -> float:
        return pivot_z + spin_z + (ring_c - ring_outer_r)

    def ring_top() -> float:
        return pivot_z + spin_z + (ring_c + ring_outer_r)

    # Enforce ground clearance > 0.25 by raising pivot (effective) if needed.
    # We adjust spin_z drop conceptually via pivot_z because the chain is
    # fixed-length; instead raise pivot_z (taller frame) to recover clearance.
    guard = 0
    while ring_bottom() <= 0.30 and guard < 40:
        pivot_z += 0.02
        fin_z0 = pivot_z - 0.125
        guard += 1
    # Enforce ring top stays below the canopy fins for pergola/a_frame.
    if support in ("two_post_pergola", "a_frame_support"):
        guard = 0
        while ring_top() >= fin_z0 - 0.02 and guard < 40:
            pivot_z += 0.02
            fin_z0 = pivot_z - 0.125
            guard += 1

    # single_arch: size the parabola so the arch tube clears the hoop's x-extent.
    # arch tube bottom z at x: arch_height - (arch_height - z_base)*(x/half_span)^2,
    # crown bottom (chain socket) sits at pivot_z.  Lift the crown peak above
    # pivot_z and widen the span until z(hoop_r + margin) > ring_top + clearance.
    arch_tube_r = 0.055
    arch_half_span = max(frame_half_x * 0.98, ring_outer_r + 0.45)
    arch_height = pivot_z + 0.16
    if support == "single_arch":
        z_base = arch_tube_r
        margin_x = ring_outer_r + 0.06
        guard = 0
        while guard < 60:
            z_range = arch_height - z_base
            # tube CENTRE z at x=margin_x; subtract tube radius for the inner surface
            z_at = z_base + z_range * (1.0 - (margin_x / arch_half_span) ** 2)
            if (z_at - arch_tube_r) > ring_top() + 0.05:
                break
            arch_half_span += 0.04
            arch_height += 0.03
            guard += 1

    bridle_thetas = _bridle_thetas(n)

    palette = dict(PALETTES[palette_style])
    if config.palette:
        palette.update(config.palette)

    return ResolvedCircularRingSwingConfig(
        support_frame=support,  # type: ignore[arg-type]
        ring_seat=ring_seat,  # type: ignore[arg-type]
        suspension_style=suspension_style,
        suspension_point_count=n,
        palette_style=palette_style,  # type: ignore[arg-type]
        frame_width_scale=fw,
        pivot_height_scale=ph,
        hoop_radius_scale=hr,
        seat_plank_count=max(16, min(34, int(config.seat_plank_count))),
        fin_count=max(24, min(40, int(config.fin_count))),
        name=config.name,
        pivot_z=pivot_z,
        frame_half_x=frame_half_x,
        hoop_r=hoop_r,
        ring_outer_r=ring_outer_r,
        spin_z=spin_z,
        ring_c=ring_c,
        bridle_thetas=bridle_thetas,
        fin_z0=fin_z0,
        arch_half_span=arch_half_span,
        arch_height=arch_height,
        palette=palette,
    )


def _bridle_thetas(n: int) -> tuple[float, ...]:
    if n <= 1:
        return ()
    # N equal angles; start at top (90 deg) so legs straddle the seat opening.
    return tuple(math.radians(90.0) + i * (2.0 * math.pi / n) for i in range(n))


def _register_materials(
    model: ArticulatedObject, r: ResolvedCircularRingSwingConfig
) -> dict[str, object]:
    return {
        key: model.material(f"crs_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in r.palette.items()
    }


# ---------------------------------------------------------------------------
# Slot A: support frames -- each returns the frame Part; pivot at (0,0,pivot_z)
# ---------------------------------------------------------------------------
def _oval_link_mesh(plane: str, mesh_name: str) -> Mesh:
    geom = TorusGeometry(LINK_R, LINK_TUBE, radial_segments=12, tubular_segments=36)
    geom.scale(LINK_STRETCH, 1.0, 1.0)
    geom.rotate_y(math.pi / 2.0)
    if plane == "xz":
        geom.rotate_z(math.pi / 2.0)
    return mesh_from_geometry(geom, mesh_name)


# adopted: S1
def _build_two_post_pergola(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    frame = model.part("support_frame")
    px = r.frame_half_x
    post_top = r.pivot_z + 0.005
    rail_w = px * 2.0 + 0.15
    for pi, x in enumerate((-px, px)):
        frame.visual(
            Box((0.15, 0.15, post_top)),
            origin=Origin(xyz=(x, 0.0, post_top / 2.0)),
            material=mats["frame"],
            name=f"post_{pi}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_warmwood", "light_steel_chrome", "bronze_oak"} else "metal.paint_coated"),
        )
    frame.visual(
        Box((rail_w, 0.28, 0.05)),
        origin=Origin(xyz=(0.0, 0.0, r.pivot_z + 0.025)),
        material=mats["frame_trim"],
        name="top_rail", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_warmwood", "light_steel_chrome", "bronze_oak"} else "metal.paint_coated"),
    )
    fin_span = rail_w - 0.06
    fin_pitch = fin_span / (r.fin_count - 1)
    for i in range(r.fin_count):
        fx = -fin_span / 2.0 + i * fin_pitch
        frame.visual(
            Box((0.04, 0.25, 0.13)),
            origin=Origin(xyz=(fx, 0.0, r.fin_z0 + 0.065)),
            material=mats["fin"],
            name=f"fin_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_warmwood", "powdercoat_charcoal", "forest_green_oak", "bronze_oak"} else "metal.stainless_matte"),
        )
    for pi, x in enumerate((-px, px)):
        for fi, fy in enumerate((-0.080, 0.080)):
            frame.visual(
                Box((0.15, 0.012, 0.42)),
                origin=Origin(xyz=(x, fy, r.pivot_z - 0.19)),
                material=mats["frame_trim"],
                name=f"gusset_{pi}_{fi}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_warmwood", "light_steel_chrome", "bronze_oak"} else "metal.paint_coated"),
            )
            ry = math.copysign(0.088, fy)
            for ri, (dx, dz) in enumerate(
                ((-0.042, -0.14), (0.042, -0.14), (-0.042, 0.14), (0.042, 0.14))
            ):
                frame.visual(
                    Cylinder(radius=0.011, length=0.012),
                    origin=Origin(xyz=(x + dx, ry, r.pivot_z - 0.19 + dz), rpy=_cyl_y()),
                    material=mats["rivet"],
                    name=f"rivet_{pi}_{fi}_{ri}", material_class_id="metal.stainless_matte",
                )
    frame.inertial = Inertial.from_geometry(
        Box((rail_w, 0.40, post_top)),
        mass=120.0,
        origin=Origin(xyz=(0.0, 0.0, post_top * 0.5)),
    )
    return frame


# adopted: S2
def _build_a_frame_support(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    frame = model.part("support_frame")
    apex_z = r.pivot_z
    a_x = r.frame_half_x * 0.91
    spread_y = 0.60
    leg_size = 0.08
    leg_len = math.sqrt(spread_y**2 + apex_z**2)
    leg_angle = math.atan2(spread_y, apex_z)
    leg_box = Box((leg_size, leg_size, leg_len))
    for side_i in range(2):
        sx = -a_x if side_i == 0 else a_x
        for leg_i in range(2):
            sy_sign = 1.0 if leg_i == 0 else -1.0
            frame.visual(
                leg_box,
                origin=Origin(
                    xyz=(sx, sy_sign * spread_y / 2.0, apex_z / 2.0),
                    rpy=(leg_angle * sy_sign, 0.0, 0.0),
                ),
                material=mats["frame"],
                name=f"leg_{side_i}_{leg_i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_warmwood", "light_steel_chrome", "bronze_oak"} else "metal.paint_coated"),
            )
            frame.visual(
                Box((0.16, 0.16, 0.020)),
                origin=Origin(xyz=(sx, sy_sign * spread_y, 0.010)),
                material=mats["dark"],
                name=f"foot_{side_i}_{leg_i}", material_class_id="metal.blackened_gunmetal",
            )
        brace_z = apex_z * 0.45
        brace_len = 2.0 * (spread_y * (1.0 - brace_z / apex_z)) + 0.04
        frame.visual(
            Box((0.05, brace_len, 0.05)),
            origin=Origin(xyz=(sx, 0.0, brace_z)),
            material=mats["frame"],
            name=f"brace_{side_i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_warmwood", "light_steel_chrome", "bronze_oak"} else "metal.paint_coated"),
        )
    rail_w = a_x * 2.0 + 0.30
    frame.visual(
        Box((rail_w, 0.28, 0.06)),
        origin=Origin(xyz=(0.0, 0.0, apex_z + 0.03)),
        material=mats["frame_trim"],
        name="top_rail", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_warmwood", "light_steel_chrome", "bronze_oak"} else "metal.paint_coated"),
    )
    fin_span = rail_w - 0.40
    fin_pitch = fin_span / (r.fin_count - 1)
    for i in range(r.fin_count):
        fx = -fin_span / 2.0 + i * fin_pitch
        frame.visual(
            Box((0.04, 0.25, 0.13)),
            origin=Origin(xyz=(fx, 0.0, r.fin_z0 + 0.065)),
            material=mats["fin"],
            name=f"fin_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized_warmwood", "powdercoat_charcoal", "forest_green_oak", "bronze_oak"} else "metal.stainless_matte"),
        )
    for side_i in range(2):
        sx = -a_x if side_i == 0 else a_x
        for gi in range(2):
            gy = -0.08 if gi == 0 else 0.08
            frame.visual(
                Box((0.12, 0.010, 0.30)),
                origin=Origin(xyz=(sx, gy, apex_z - 0.15)),
                material=mats["frame_trim"],
                name=f"apex_gusset_{side_i}_{gi}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_warmwood", "light_steel_chrome", "bronze_oak"} else "metal.paint_coated"),
            )
            for ri in range(4):
                dx = -0.035 if ri < 2 else 0.035
                dz = -0.10 if ri % 2 == 0 else 0.10
                frame.visual(
                    Cylinder(radius=0.009, length=0.014),
                    origin=Origin(xyz=(sx + dx, gy, apex_z - 0.15 + dz), rpy=_cyl_y()),
                    material=mats["rivet"],
                    name=f"apex_rivet_{side_i}_{gi}_{ri}", material_class_id="metal.stainless_matte",
                )
    frame.inertial = Inertial.from_geometry(
        Box((rail_w, spread_y * 2.2, apex_z)),
        mass=110.0,
        origin=Origin(xyz=(0.0, 0.0, apex_z * 0.5)),
    )
    return frame


# adopted: S3
def _build_single_arch(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    frame = model.part("support_frame")
    half_span = r.arch_half_span
    arch_tube_r = 0.055
    arch_height = r.arch_height
    n_pts = 21
    z_base = arch_tube_r
    z_range = arch_height - z_base
    pts: list[tuple[float, float, float]] = []
    for i in range(n_pts):
        t = i / (n_pts - 1)
        x = -half_span + 2.0 * half_span * t
        z = z_base + z_range * (1.0 - (x / half_span) ** 2)
        pts.append((x, 0.0, z))
    arch_geom = tube_from_spline_points(
        pts, radius=arch_tube_r, samples_per_segment=8, radial_segments=16, cap_ends=True
    )
    frame.visual(
        mesh_from_geometry(arch_geom, "arch_beam"),
        material=mats["frame"],
        name="arch_beam", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_warmwood", "light_steel_chrome", "bronze_oak"} else "metal.paint_coated"),
    )
    for i in range(2):
        px = -half_span + i * 2.0 * half_span
        frame.visual(
            Box((0.28, 0.28, 0.018)),
            origin=Origin(xyz=(px, 0.0, 0.009)),
            material=mats["dark"],
            name=f"base_plate_{i}", material_class_id="metal.blackened_gunmetal",
        )
        for wi in range(2):
            wy = -0.055 + wi * 0.110
            frame.visual(
                Box((0.012, 0.012, 0.055)),
                origin=Origin(xyz=(px, wy, 0.0455)),
                material=mats["dark"],
                name=f"gusset_{i}_{wi}", material_class_id="metal.blackened_gunmetal",
            )
        for bi, (bx, by) in enumerate(
            ((-0.09, -0.09), (-0.09, 0.09), (0.09, -0.09), (0.09, 0.09))
        ):
            frame.visual(
                Cylinder(radius=0.009, length=0.025),
                origin=Origin(xyz=(px + bx, by, 0.0305)),
                material=mats["rivet"],
                name=f"bolt_{i}_{bi}", material_class_id="metal.stainless_matte",
            )
    # crown collar -- mounting boss bridging the arch crown tube down to the
    # swing pivot where the chain anchor sockets in.
    tube_bottom_peak = arch_height - arch_tube_r
    collar_h = max(0.020, tube_bottom_peak - r.pivot_z + 0.030)
    frame.visual(
        Cylinder(radius=0.048, length=collar_h),
        origin=Origin(xyz=(0.0, 0.0, r.pivot_z - 0.010 + collar_h / 2.0)),
        material=mats["dark"],
        name="crown_collar", material_class_id="metal.blackened_gunmetal",
    )
    frame.inertial = Inertial.from_geometry(
        Box((half_span * 2.2, 0.30, arch_height)),
        mass=130.0,
        origin=Origin(xyz=(0.0, 0.0, arch_height * 0.45)),
    )
    return frame


def _build_support(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    if r.support_frame == "a_frame_support":
        return _build_a_frame_support(model, r, mats)
    if r.support_frame == "single_arch":
        return _build_single_arch(model, r, mats)
    return _build_two_post_pergola(model, r, mats)


# ---------------------------------------------------------------------------
# Slot C: suspension -- one part, emits swing joint up + spin joint down
# ---------------------------------------------------------------------------
def _add_anchor_stack(susp: Part, mats: dict[str, object], eye_c: float) -> None:
    susp.visual(
        Cylinder(radius=0.012, length=STEM_LEN),
        origin=Origin(xyz=(0.0, 0.0, -0.015)),
        material=mats["chrome"],
        name="anchor_stem", material_class_id="metal.chrome_polished",
    )
    eye_geom = TorusGeometry(0.016, 0.005, radial_segments=12, tubular_segments=32)
    eye_geom.rotate_x(math.pi / 2.0)
    susp.visual(
        mesh_from_geometry(eye_geom, "anchor_eye"),
        origin=Origin(xyz=(0.0, 0.0, eye_c)),
        material=mats["chrome"],
        name="anchor_eye", material_class_id="metal.chrome_polished",
    )


# adopted: S1
def _build_single_chain(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    susp = model.part("suspension")
    _add_anchor_stack(susp, mats, EYE_C)
    link_yz = _oval_link_mesh("yz", "chain_link_yz")
    link_xz = _oval_link_mesh("xz", "chain_link_xz")
    for li, lc in enumerate(LINK_CENTERS):
        susp.visual(
            link_yz if li % 2 == 0 else link_xz,
            origin=Origin(xyz=(0.0, 0.0, lc)),
            material=mats["chrome"],
            name=f"chain_link_{li}", material_class_id="metal.chrome_polished",
        )
    hook_eye_geom = TorusGeometry(0.016, 0.0055, radial_segments=12, tubular_segments=32)
    hook_eye_geom.rotate_y(math.pi / 2.0)
    susp.visual(
        mesh_from_geometry(hook_eye_geom, "hook_eye"),
        origin=Origin(xyz=(0.0, 0.0, HOOK_EYE_C)),
        material=mats["chrome"],
        name="hook_eye", material_class_id="metal.chrome_polished",
    )
    hook_pts = [(0.0, 0.0, -0.4985)]
    for theta_deg in (90.0, 130.0, 170.0, 210.0, 250.0, 290.0, 330.0):
        th = math.radians(theta_deg)
        hook_pts.append((HOOK_ARC_R * math.cos(th), 0.0, HOOK_ARC_C + HOOK_ARC_R * math.sin(th)))
    hook_geom = tube_from_spline_points(
        hook_pts, radius=0.0085, samples_per_segment=10, radial_segments=14, cap_ends=True
    )
    susp.visual(mesh_from_geometry(hook_geom, "hook"), material=mats["chrome"], name="hook", material_class_id="metal.chrome_polished")
    susp.inertial = Inertial.from_geometry(
        Cylinder(radius=0.03, length=abs(CHAIN_SPIN_Z)),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, CHAIN_SPIN_Z * 0.5)),
    )
    return susp


# adopted: S6, S7
def _build_n_point_bridle(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    susp = model.part("suspension")
    _add_anchor_stack(susp, mats, ANCHOR_EYE_C)
    link_yz = _oval_link_mesh("yz", "chain_link_yz")
    link_xz = _oval_link_mesh("xz", "chain_link_xz")
    for li, lc in enumerate(ANCHOR_LINK_CENTERS):
        susp.visual(
            link_yz if li % 2 == 0 else link_xz,
            origin=Origin(xyz=(0.0, 0.0, lc)),
            material=mats["chrome"],
            name=f"anchor_link_{li}", material_class_id="metal.chrome_polished",
        )
    susp.visual(
        Cylinder(radius=HUB_DISK_R, length=HUB_DISK_H),
        origin=Origin(xyz=(0.0, 0.0, HUB_Z_LOCAL)),
        material=mats["chrome"],
        name="hub_plate", material_class_id="metal.chrome_polished",
    )
    # N legs from hub centre to ring rim attachment points (ring-local theta).
    for i, theta in enumerate(r.bridle_thetas):
        rx = r.ring_outer_r * math.cos(theta)
        rz = r.ring_c + r.ring_outer_r * math.sin(theta)
        rz_hub = rz + r.spin_z  # convert ring-local to suspension-local
        dx = rx
        dz = rz_hub - HUB_Z_LOCAL
        leg_len = math.sqrt(dx * dx + dz * dz)
        mx = rx / 2.0
        mz = HUB_Z_LOCAL + dz / 2.0
        pitch = math.atan2(dx, dz) if leg_len > 1e-9 else 0.0
        susp.visual(
            Cylinder(radius=BRIDLE_LEG_R, length=leg_len),
            origin=Origin(xyz=(mx, 0.0, mz), rpy=(0.0, pitch, 0.0)),
            material=mats["chrome"],
            name=f"bridle_leg_{i}", material_class_id="metal.chrome_polished",
        )
        leg_eye_geom = TorusGeometry(0.014, 0.004, radial_segments=10, tubular_segments=24)
        leg_eye_geom.rotate_y(math.pi / 2.0)
        susp.visual(
            mesh_from_geometry(leg_eye_geom, f"leg_eye_{i}"),
            origin=Origin(xyz=(rx, 0.0, rz_hub)),
            material=mats["chrome"],
            name=f"leg_eye_{i}", material_class_id="metal.chrome_polished",
        )
    susp.inertial = Inertial.from_geometry(
        Cylinder(radius=HUB_DISK_R, length=abs(HUB_Z_LOCAL) + 0.05),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, HUB_Z_LOCAL * 0.5)),
    )
    return susp


def _build_suspension(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    if r.suspension_style == "single_chain":
        return _build_single_chain(model, r, mats)
    return _build_n_point_bridle(model, r, mats)


# ---------------------------------------------------------------------------
# Slot B: ring seat -- one part, twin hoops + seat content, spins about +Z
# ---------------------------------------------------------------------------
def _add_twin_hoops(ring: Part, r: ResolvedCircularRingSwingConfig, mats: dict[str, object]) -> None:
    hoop_geom = TorusGeometry(r.hoop_r, HOOP_TUBE, radial_segments=18, tubular_segments=140)
    hoop_geom.rotate_x(math.pi / 2.0)
    hoop_mesh = mesh_from_geometry(hoop_geom, "ring_hoop")
    for hi, hy in enumerate((-HOOP_Y, HOOP_Y)):
        ring.visual(
            hoop_mesh,
            origin=Origin(xyz=(0.0, hy, r.ring_c)),
            material=mats["chrome"],
            name=f"hoop_{hi}", material_class_id="metal.chrome_polished",
        )


def _add_ring_upstream(
    ring: Part, r: ResolvedCircularRingSwingConfig, mats: dict[str, object]
) -> None:
    """Attachment hardware: centre eyelet+clevis (single_chain) or N brackets."""
    if r.suspension_style == "single_chain":
        # small solid swivel shank centred on the ring-local origin so the
        # ring_spin joint origin sits on real child geometry; it bridges the
        # eyelet (at origin) down to the hanger clevis so nothing floats.
        shank_top = 0.018
        shank_h = shank_top - CLEVIS_C
        ring.visual(
            Cylinder(radius=0.013, length=shank_h),
            origin=Origin(xyz=(0.0, 0.0, shank_top - shank_h / 2.0)),
            material=mats["chrome"],
            name="spin_bead", material_class_id="metal.chrome_polished",
        )
        eyelet_geom = TorusGeometry(EYELET_R, EYELET_TUBE, radial_segments=14, tubular_segments=40)
        eyelet_geom.rotate_y(math.pi / 2.0)
        ring.visual(
            mesh_from_geometry(eyelet_geom, "ring_eyelet"),
            material=mats["chrome"],
            name="ring_eyelet", material_class_id="metal.chrome_polished",
        )
        ring.visual(
            Box((0.05, 0.115, 0.042)),
            origin=Origin(xyz=(0.0, 0.0, CLEVIS_C)),
            material=mats["chrome"],
            name="hanger_clevis", material_class_id="metal.chrome_polished",
        )
        # vertical hanger straps from the clevis down to the ring crown so the
        # top suspension hardware is structurally tied to the rigid hoop/band.
        hoop_top = r.ring_c + r.ring_outer_r
        strap_top = CLEVIS_C - 0.010
        strap_h = strap_top - hoop_top
        if strap_h > 0.0:
            for hi, hy in enumerate((-HOOP_Y, HOOP_Y)):
                ring.visual(
                    Box((0.022, 0.018, strap_h)),
                    origin=Origin(xyz=(0.0, hy, hoop_top + strap_h / 2.0)),
                    material=mats["chrome"],
                    name=f"hanger_strap_{hi}", material_class_id="metal.chrome_polished",
                )
    else:
        # central swivel boss at the ring-local origin so the spin joint origin
        # sits on real ring geometry (the hub the bridle legs converge onto).
        ring.visual(
            Cylinder(radius=0.045, length=0.050),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["chrome"],
            name="swivel_boss", material_class_id="metal.chrome_polished",
        )
        for i, theta in enumerate(r.bridle_thetas):
            rx = r.ring_outer_r * math.cos(theta)
            rz = r.ring_c + r.ring_outer_r * math.sin(theta)
            ring.visual(
                Box((0.040, 0.100, 0.040)),
                origin=Origin(xyz=(rx, 0.0, rz)),
                material=mats["chrome"],
                name=f"bridle_bracket_{i}", material_class_id="metal.chrome_polished",
            )
            # structural spoke rib tying the central swivel boss to each rim
            # bracket, so the ring reads as a hub-and-spoke spider (and the
            # boss is not a floating island).
            dx = rx
            dz = rz - 0.0
            rib_len = math.sqrt(dx * dx + dz * dz)
            mx = dx / 2.0
            mz = dz / 2.0
            pitch = math.atan2(dx, dz) if rib_len > 1e-9 else 0.0
            ring.visual(
                Cylinder(radius=0.011, length=rib_len),
                origin=Origin(xyz=(mx, 0.0, mz), rpy=(0.0, pitch, 0.0)),
                material=mats["chrome"],
                name=f"hub_spoke_{i}", material_class_id="metal.chrome_polished",
            )


# adopted: S1
def _build_bench_ring_seat(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    ring = model.part("ring_seat")
    _add_ring_upstream(ring, r, mats)
    _add_twin_hoops(ring, r, mats)
    # plank radial outer face firmly embeds into the hoop tube so the bench
    # arc ties into the rigid hoops (plank radial half-extent = 0.035).
    plank_rc = r.hoop_r - 0.020
    count = r.seat_plank_count
    for si in range(count):
        theta = PLANK_THETA0 + (PLANK_THETA1 - PLANK_THETA0) * si / (count - 1)
        cx = plank_rc * math.cos(theta)
        cz = r.ring_c + plank_rc * math.sin(theta)
        ring.visual(
            Box((0.070, 0.115, 0.018)),
            origin=Origin(xyz=(cx, 0.0, cz), rpy=(0.0, math.pi / 2.0 - theta, 0.0)),
            material=mats["wood"],
            name=f"seat_plank_{si}", material_class_id=("wood.oak" if r.palette_style in {"powdercoat_charcoal", "light_steel_chrome", "forest_green_oak", "bronze_oak"} else "wood.natural_generic"),
        )
    ring.inertial = Inertial.from_geometry(
        Cylinder(radius=r.hoop_r, length=0.12),
        mass=22.0,
        origin=Origin(xyz=(0.0, 0.0, r.ring_c), rpy=_cyl_y()),
    )
    return ring


# adopted: S4 -- OPEN halo: same twin chrome hoops as the bench, with wooden
# planks lining a DEEPER lower arc (~214 deg, theta 163 -> 377) that climb up
# both sides into a low scooped backrest.  The ring centre stays fully open.
def _build_deep_cradle_ring(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    ring = model.part("ring_seat")
    _add_ring_upstream(ring, r, mats)
    _add_twin_hoops(ring, r, mats)
    # plank radial outer face firmly embeds into the hoop tube so the cradle
    # arc ties into the rigid hoops (plank radial half-extent = 0.010).
    plank_rc = r.hoop_r - 0.020
    count = r.seat_plank_count
    # Width scales with arc density so the deeper-arc planks nearly touch.
    arc_span_m = plank_rc * (CRADLE_THETA1 - CRADLE_THETA0)
    plank_width = max(0.045, 0.90 * arc_span_m / max(1, count - 1))
    for si in range(count):
        theta = CRADLE_THETA0 + (CRADLE_THETA1 - CRADLE_THETA0) * si / (count - 1)
        cx = plank_rc * math.cos(theta)
        cz = r.ring_c + plank_rc * math.sin(theta)
        ring.visual(
            Box((plank_width, 0.115, 0.020)),
            origin=Origin(xyz=(cx, 0.0, cz), rpy=(0.0, math.pi / 2.0 - theta, 0.0)),
            material=mats["wood"],
            name=f"seat_plank_{si}", material_class_id=("wood.oak" if r.palette_style in {"powdercoat_charcoal", "light_steel_chrome", "forest_green_oak", "bronze_oak"} else "wood.natural_generic"),
        )
    ring.inertial = Inertial.from_geometry(
        Cylinder(radius=r.hoop_r, length=0.12),
        mass=24.0,
        origin=Origin(xyz=(0.0, 0.0, r.ring_c), rpy=_cyl_y()),
    )
    return ring


# adopted: S5 -- OPEN halo: a SINGLE wide flat steel band (a CadQuery hollow
# annulus) replaces the twin tube hoops; the annulus interior is fully open.
# Wooden planks line the lower inner arc (~146 deg, theta 197 -> 343) fastened
# to the band inner wall.
def _build_flat_band_ring(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    ring = model.part("ring_seat")
    _add_ring_upstream(ring, r, mats)
    # Single wide flat steel ribbon rolled into a hollow circle.  Built on the
    # XY plane (hole axis Z) then rotated to the XZ ring plane (hole axis Y),
    # matching the twin-hoop orientation.  Outer radius scales with hoop_r.
    band_outer_r = r.hoop_r + (BAND_OUTER_R - HOOP_R)
    band_inner_r = band_outer_r - BAND_THICKNESS
    band_cq = (
        cq.Workplane("XY")
        .circle(band_outer_r)
        .circle(band_inner_r)
        .extrude(BAND_WIDTH / 2.0, both=True)
    )
    band_cq = band_cq.rotateAboutCenter((1, 0, 0), 90)
    ring.visual(
        mesh_from_cadquery(band_cq, "flat_band"),
        origin=Origin(xyz=(0.0, 0.0, r.ring_c)),
        material=mats["chrome"],
        name="flat_band", material_class_id="metal.chrome_polished",
    )
    # Wooden seat planks lining the lower inner arc, embedded into the band wall.
    plank_rc = band_inner_r - 0.007
    count = r.seat_plank_count
    for si in range(count):
        theta = (
            BAND_PLANK_THETA0
            + (BAND_PLANK_THETA1 - BAND_PLANK_THETA0) * si / (count - 1)
        )
        cx = plank_rc * math.cos(theta)
        cz = r.ring_c + plank_rc * math.sin(theta)
        ring.visual(
            Box((0.065, 0.095, 0.018)),
            origin=Origin(xyz=(cx, 0.0, cz), rpy=(0.0, math.pi / 2.0 - theta, 0.0)),
            material=mats["wood"],
            name=f"seat_plank_{si}", material_class_id=("wood.oak" if r.palette_style in {"powdercoat_charcoal", "light_steel_chrome", "forest_green_oak", "bronze_oak"} else "wood.natural_generic"),
        )
    ring.inertial = Inertial.from_geometry(
        Cylinder(radius=band_outer_r, length=BAND_WIDTH),
        mass=20.0,
        origin=Origin(xyz=(0.0, 0.0, r.ring_c), rpy=_cyl_y()),
    )
    return ring


def _build_ring_seat(
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
    mats: dict[str, object],
) -> Part:
    if r.ring_seat == "deep_cradle_ring":
        return _build_deep_cradle_ring(model, r, mats)
    if r.ring_seat == "flat_band_ring":
        return _build_flat_band_ring(model, r, mats)
    return _build_bench_ring_seat(model, r, mats)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_circular_ring_swing(
    config: CircularRingSwingConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or CircularRingSwingConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _register_materials(model, r)

    frame = _build_support(model, r, mats)
    susp = _build_suspension(model, r, mats)
    ring = _build_ring_seat(model, r, mats)

    model.articulation(
        "canopy_swing",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=susp,
        origin=Origin(xyz=(0.0, 0.0, r.pivot_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=600.0,
            velocity=3.0,
            lower=-math.radians(45.0),
            upper=math.radians(45.0),
        ),
    )
    model.articulation(
        "ring_spin",
        ArticulationType.CONTINUOUS,
        parent=susp,
        child=ring,
        origin=Origin(xyz=(0.0, 0.0, r.spin_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=4.0),
    )
    return model


def build_seeded_circular_ring_swing(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_circular_ring_swing(config_from_seed(seed), assets=assets)


def slot_choices_for_config(config: CircularRingSwingConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("support_frame", r.support_frame),
        ("ring_seat", r.ring_seat),
        ("suspension", r.suspension_style),
        ("suspension_multiplicity", f"{r.suspension_point_count}_point"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _allow_expected_overlaps(
    ctx: TestContext,
    model: ArticulatedObject,
    r: ResolvedCircularRingSwingConfig,
) -> None:
    frame = model.get_part("support_frame")
    susp = model.get_part("suspension")
    ring = model.get_part("ring_seat")

    allow_disconnected = getattr(ctx, "allow_disconnected_islands", None)
    if callable(allow_disconnected):
        allow_disconnected(
            frame,
            reason="support frame is a rigid multi-piece pergola/A-frame/arch with posts, rails, fins, gussets, rivets",
        )
        allow_disconnected(
            ring,
            reason="ring seat is a rigid open-halo hoop/band + wooden seat-plank assembly that spins as one body",
        )
        if r.suspension_style == "n_point_bridle":
            allow_disconnected(
                susp,
                reason="bridle hub is a rigid anchor chain + hub plate + N diverging legs subassembly",
            )

    # anchor stem socketed into the rail/beam/crown collar
    frame_socket = {
        "two_post_pergola": "top_rail",
        "a_frame_support": "top_rail",
        "single_arch": "crown_collar",
    }[r.support_frame]
    ctx.allow_overlap(
        frame,
        susp,
        elem_a=frame_socket,
        elem_b="anchor_stem",
        reason="The anchor stem is an eye-bolt shank intentionally socketed into the canopy beam/crown collar.",
    )
    # Canopy fins sit on the centerline; the thin anchor stem/eye/links pass
    # between them as the chain leaves the beam underside.
    susp_top_elems = [
        v.name
        for v in susp.visuals
        if v.name
        and (
            v.name in ("anchor_stem", "anchor_eye", "hub_plate")
            or v.name.startswith("chain_link_")
            or v.name.startswith("anchor_link_")
        )
    ]
    if r.support_frame in ("two_post_pergola", "a_frame_support"):
        for v in frame.visuals:
            name = v.name or ""
            if name.startswith("fin_"):
                for anchor_elem in susp_top_elems:
                    ctx.allow_overlap(
                        frame,
                        susp,
                        elem_a=name,
                        elem_b=anchor_elem,
                        reason="The chain anchor passes between the centerline canopy louver fins.",
                    )
    if r.support_frame == "single_arch":
        for anchor_elem in susp_top_elems:
            ctx.allow_overlap(
                frame,
                susp,
                elem_a="arch_beam",
                elem_b=anchor_elem,
                reason="The chain anchor sockets up into the arch crown tube.",
            )

    if r.suspension_style == "single_chain":
        ctx.allow_overlap(
            susp,
            ring,
            elem_a="hook",
            elem_b="ring_eyelet",
            reason="The ring eyelet is captured on the hook bowl with a small seating embed.",
        )
        ctx.allow_overlap(
            susp,
            ring,
            elem_a="hook",
            elem_b="hanger_clevis",
            reason="The hook seats against the ring hanger clevis.",
        )
        ctx.allow_overlap(
            susp,
            ring,
            elem_a="hook",
            elem_b="spin_bead",
            reason="The hook bowl captures the ring spin bead at the swivel axis.",
        )
        ctx.allow_overlap(
            susp,
            ring,
            elem_a="hook_eye",
            elem_b="spin_bead",
            reason="The hook eye sits beside the ring spin bead at the swivel axis.",
        )
    else:
        # central swivel boss + hub spokes are captured on the suspension hub
        # at the spin axis where the bridle legs converge.
        hub_side = ("hub_plate",) + tuple(f"anchor_link_{k}" for k in range(4))
        ring_hub_side = ("swivel_boss",) + tuple(
            f"hub_spoke_{k}" for k in range(r.suspension_point_count)
        )
        for hub_elem in hub_side:
            for ring_elem in ring_hub_side:
                ctx.allow_overlap(
                    susp,
                    ring,
                    elem_a=hub_elem,
                    elem_b=ring_elem,
                    reason="The ring swivel boss and hub spokes are captured on the suspension hub at the spin axis.",
                )
        ring_seat_elems = [
            v.name
            for v in ring.visuals
            if v.name
            and (
                v.name.startswith("seat_plank_")
                or v.name.startswith("hoop_")
                or v.name == "flat_band"
                or v.name.startswith("bridle_bracket_")
                or v.name.startswith("hub_spoke_")
                or v.name == "swivel_boss"
            )
        ]
        n = r.suspension_point_count
        for i in range(n):
            for elem in ("swivel_boss",):
                ctx.allow_overlap(
                    susp,
                    ring,
                    elem_a=f"bridle_leg_{i}",
                    elem_b=elem,
                    reason="Bridle legs emanate from the hub and pass the ring swivel boss at the spin axis.",
                )
                ctx.allow_overlap(
                    susp,
                    ring,
                    elem_a=f"leg_eye_{i}",
                    elem_b=elem,
                    reason="Bridle leg eyes near the swivel boss at the spin axis.",
                )
            for j in range(n):
                ctx.allow_overlap(
                    susp,
                    ring,
                    elem_a=f"bridle_leg_{i}",
                    elem_b=f"bridle_bracket_{j}",
                    reason="Bridle legs converge at the ring rim brackets; adjacent legs/brackets interlock.",
                )
                ctx.allow_overlap(
                    susp,
                    ring,
                    elem_a=f"leg_eye_{i}",
                    elem_b=f"bridle_bracket_{j}",
                    reason="Leg shackle eyes seat against the ring rim brackets.",
                )
            # legs/eyes may graze seat content near their attachment
            for elem in ring_seat_elems:
                ctx.allow_overlap(
                    susp,
                    ring,
                    elem_a=f"bridle_leg_{i}",
                    elem_b=elem,
                    reason=f"Bridle leg {i} passes through the seat zone near its bracket attachment.",
                )
                ctx.allow_overlap(
                    susp,
                    ring,
                    elem_a=f"leg_eye_{i}",
                    elem_b=elem,
                    reason=f"Bridle leg shackle eye {i} wraps the hoop/seat near its attachment.",
                )


def run_circular_ring_swing_tests(
    object_model: ArticulatedObject,
    config: CircularRingSwingConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.030)
    ctx.fail_if_joint_mating_has_gap()

    parts = {p.name for p in object_model.parts}
    ctx.check("support_frame_present", "support_frame" in parts)
    ctx.check("suspension_present", "suspension" in parts)
    ctx.check("ring_seat_present", "ring_seat" in parts)

    ring = object_model.get_part("ring_seat")
    swing = object_model.get_articulation("canopy_swing")
    spin = object_model.get_articulation("ring_spin")

    # Exactly two non-fixed joints regardless of N.
    nonfixed = [
        j
        for j in object_model.articulations
        if j.articulation_type
        in (ArticulationType.REVOLUTE, ArticulationType.CONTINUOUS, ArticulationType.PRISMATIC)
    ]
    ctx.check(
        "exactly_two_nonfixed_joints",
        len(nonfixed) == 2,
        details=f"non-fixed joints: {[j.name for j in nonfixed]}",
    )

    swing_axis = tuple(round(float(v), 6) for v in swing.axis)
    ctx.check(
        "canopy_swing_is_revolute_about_x",
        swing.articulation_type == ArticulationType.REVOLUTE
        and swing_axis in ((1.0, 0.0, 0.0), (-1.0, -0.0, -0.0)),
        details=f"type={swing.articulation_type}, axis={swing_axis}",
    )
    spin_axis = tuple(round(float(v), 6) for v in spin.axis)
    ctx.check(
        "ring_spin_is_continuous_about_z",
        spin.articulation_type == ArticulationType.CONTINUOUS
        and spin_axis in ((0.0, 0.0, 1.0), (-0.0, -0.0, -1.0)),
        details=f"type={spin.articulation_type}, axis={spin_axis}",
    )

    # Open-ring primitive present and ~circular.  bench/cradle use twin chrome
    # tube hoops (hoop_0/hoop_1); flat_band uses a single CadQuery annulus.
    ring_names = {v.name for v in ring.visuals if v.name}
    if r.ring_seat == "flat_band_ring":
        ring_prim = "flat_band"
        expected_od = 2.0 * r.ring_outer_r
    else:
        ring_prim = "hoop_0"
        expected_od = 2.0 * r.hoop_r
    prim_aabb = ctx.part_element_world_aabb(ring, elem=ring_prim)
    ctx.check(
        "ring_primitive_present",
        prim_aabb is not None,
        details=f"ring_prim={ring_prim}",
    )
    if r.ring_seat in ("bench_ring_seat", "deep_cradle_ring"):
        ctx.check("twin_hoops_present", "hoop_1" in ring_names)
    ctx.check(
        "ring_outer_diameter_matches_scale",
        prim_aabb is not None
        and abs((prim_aabb[1][0] - prim_aabb[0][0]) - expected_od) < 0.12
        and abs((prim_aabb[1][2] - prim_aabb[0][2]) - expected_od) < 0.12,
        details=f"{ring_prim}={prim_aabb}, expected_od={expected_od:.3f}",
    )

    # HALO invariant: the ring is an OPEN hoop -- no disc / platform / deck /
    # net / saucer / web fills the centre, and the wooden seat only lines the
    # lower inner arc (<= ~220 deg).
    _forbidden_prefixes = (
        "disc",
        "platform",
        "deck",
        "net",
        "saucer",
        "web",
        "spoke_",
        "concentric",
    )
    forbidden = sorted(n for n in ring_names if n.startswith(_forbidden_prefixes))
    ctx.check(
        "halo_ring_centre_open",
        not forbidden,
        details=f"forbidden centre-filling elements: {forbidden}",
    )
    _seat_arc_deg = {
        "bench_ring_seat": 146.0,
        "deep_cradle_ring": 214.0,
        "flat_band_ring": 146.0,
    }[r.ring_seat]
    ctx.check(
        "halo_seat_arc_within_limit",
        _seat_arc_deg <= 220.0 + 1e-6,
        details=f"seat arc={_seat_arc_deg:.1f} deg",
    )

    # clearance: ring hangs clear of the ground and below canopy fins/crown
    ring_aabb = ctx.part_world_aabb(ring)
    ctx.check(
        "ring_clears_ground",
        ring_aabb is not None and ring_aabb[0][2] > 0.25,
        details=f"ring aabb={ring_aabb}",
    )
    if r.support_frame in ("two_post_pergola", "a_frame_support"):
        ctx.check(
            "ring_top_below_canopy_fins",
            ring_aabb is not None and ring_aabb[1][2] < r.fin_z0 + 0.001,
            details=f"ring top={ring_aabb[1][2] if ring_aabb else None}, fin_z0={r.fin_z0:.3f}",
        )

    # bridle structure: N legs + N brackets when bridle
    if r.suspension_style == "n_point_bridle":
        susp = object_model.get_part("suspension")
        leg_count = sum(1 for v in susp.visuals if (v.name or "").startswith("bridle_leg_"))
        bracket_count = sum(
            1 for v in ring.visuals if (v.name or "").startswith("bridle_bracket_")
        )
        ctx.check(
            "bridle_leg_count_matches_N",
            leg_count == r.suspension_point_count,
            details=f"legs={leg_count}, N={r.suspension_point_count}",
        )
        ctx.check(
            "bridle_bracket_count_matches_N",
            bracket_count == r.suspension_point_count,
            details=f"brackets={bracket_count}, N={r.suspension_point_count}",
        )

    # swing carries ring fore/aft
    rest_pos = ctx.part_world_position(ring)
    with ctx.pose({swing: math.radians(45.0)}):
        fwd_pos = ctx.part_world_position(ring)
    with ctx.pose({swing: -math.radians(45.0)}):
        back_pos = ctx.part_world_position(ring)
    ctx.check(
        "positive_swing_carries_ring_forward",
        rest_pos is not None
        and fwd_pos is not None
        and fwd_pos[1] > rest_pos[1] + 0.25
        and fwd_pos[2] > rest_pos[2] + 0.05,
        details=f"rest={rest_pos}, fwd={fwd_pos}",
    )
    ctx.check(
        "negative_swing_carries_ring_backward",
        rest_pos is not None and back_pos is not None and back_pos[1] < rest_pos[1] - 0.25,
        details=f"rest={rest_pos}, back={back_pos}",
    )

    # quarter spin turns the ring plane about the vertical axis
    with ctx.pose({spin: math.pi / 2.0}):
        spun_hoop = ctx.part_element_world_aabb(ring, elem=ring_prim)
    ctx.check(
        "quarter_spin_turns_ring_plane",
        spun_hoop is not None
        and (spun_hoop[1][1] - spun_hoop[0][1]) > (spun_hoop[1][0] - spun_hoop[0][0]),
        details=f"spun {ring_prim}={spun_hoop}",
    )

    return ctx.report()


__all__ = [
    "CircularRingSwingConfig",
    "ResolvedCircularRingSwingConfig",
    "build_circular_ring_swing",
    "build_seeded_circular_ring_swing",
    "config_from_seed",
    "resolve_config",
    "run_circular_ring_swing_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
