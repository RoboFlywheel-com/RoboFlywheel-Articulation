# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``skincare_roller``.

Follows ``articraft_template_authoring/specs_modular_v1/Sports_Skincare_Roller.md``.

A hand-held jade / germanium facial massage roller.  World frame:

- The static stone handle (grip) axis runs along +Z (vertical), centered on
  x=0, y=0.  Each end of the handle carries a polished metal collar/ferrule.
- A metal fork / yoke rises from each working collar end and captures a stone
  roller head's cross axle (axle along X).
- Each roller head is a SEPARATE part jointed to the body with one CONTINUOUS
  spin joint about +X — the only moving parts.

Slots (pattern = mixed: parallel children on a shared static handle body +
``roller_count`` multiplicity):

    roller_head_form (A) — smooth_oval / faceted_gem / spiky_germanium / textured_ridged
    handle_form      (B) — straight_stone_bar / contoured_waisted / flat_paddle_bar
    fork_yoke_form   (C) — u_wire_fork / flat_blade_yoke / single_cantilever_arm

``roller_count`` ∈ {1, 2}:
- N=2 (twin-ended): a SMALL roller at +Z and a LARGE roller at -Z.
- N=1 (single-ended): one LARGE roller at -Z, and a static rounded ``stone_tip``
  + collar at +Z (no fork, no second moving part).

Adopted sources (spec Module Source Index):
S1 rec_jade-facial-massage-roller-...d964a399 — parent twin oval roller +
   straight stone bar + U-wire fork + collars (N=2 baseline).
S2 rec_skincare_roller_var_faceted_gem — MeshGeometry briolette barrel roller.
S3 rec_skincare_roller_var_spiky_ball — SphereGeometry + nub field germanium ball.
S4 rec_skincare_roller_var_ridged — LatheGeometry wavy ridged barrel roller.
S5 rec_skincare_roller_var_waisted — cosine-blend LatheGeometry waisted handle.
S6 rec_skincare_roller_var_paddle — superellipse extrude flat paddle handle.
S7 rec_skincare_roller_var_blade_yoke — flat stamped Y-blade yoke (XZ extrude).
S8 rec_skincare_roller_var_cantilever / var_single_ended — single cantilever arm +
   stub axle (joint origin (-reach,0,z)) and the N=1 stone_tip termination.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    CylinderGeometry,
    ExtrudeGeometry,
    Inertial,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    SphereGeometry,
    TestContext,
    TestReport,
    mesh_from_geometry,
    superellipse_profile,
    tube_from_spline_points,
)

# adopted: S1 d964a399 — twin oval roller + straight bar + U-fork + collars
# adopted: S2 faceted_gem — MeshGeometry briolette barrel roller head
# adopted: S3 spiky_ball — SphereGeometry core + nested nub field germanium ball
# adopted: S4 ridged — LatheGeometry wavy ridged barrel roller head
# adopted: S5 waisted — cosine-blend LatheGeometry contoured waisted handle
# adopted: S6 paddle — superellipse extrude flat paddle handle
# adopted: S7 blade_yoke — flat stamped Y-blade yoke (XZ profile extruded along Y)
# adopted: S8 cantilever/single_ended — single cantilever arm + stub axle, N=1 stone_tip

__modular__ = True

RollerHeadForm = Literal["smooth_oval", "faceted_gem", "spiky_germanium", "textured_ridged"]
HandleForm = Literal["straight_stone_bar", "contoured_waisted", "flat_paddle_bar"]
ForkYokeForm = Literal["u_wire_fork", "flat_blade_yoke", "single_cantilever_arm"]
PaletteStyle = Literal[
    "classic_jade",
    "rose_quartz",
    "amethyst",
    "dark_germanium",
    "obsidian_steel",
    "white_marble_gold",
]

ROLLER_HEAD_FORMS: tuple[RollerHeadForm, ...] = (
    "smooth_oval",
    "faceted_gem",
    "spiky_germanium",
    "textured_ridged",
)
HANDLE_FORMS: tuple[HandleForm, ...] = (
    "straight_stone_bar",
    "contoured_waisted",
    "flat_paddle_bar",
)
FORK_YOKE_FORMS: tuple[ForkYokeForm, ...] = (
    "u_wire_fork",
    "flat_blade_yoke",
    "single_cantilever_arm",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_jade",
    "rose_quartz",
    "amethyst",
    "dark_germanium",
    "obsidian_steel",
    "white_marble_gold",
)

_HEAD_WEIGHTS = (0.32, 0.24, 0.22, 0.22)
_HANDLE_WEIGHTS = (0.40, 0.32, 0.28)
# u_wire and blade share the bulk; cantilever is gated toward N=1 (lower weight).
_YOKE_WEIGHTS = (0.42, 0.36, 0.22)
# roller_count: near-uniform, slight bias toward the twin-ended class signature.
_COUNT_VALUES = (1, 2)
_COUNT_WEIGHTS = (0.45, 0.55)


# --------------------------------------------------------------------------- #
# Nominal geometry constants (pre-scale, meters). Shared with the 5★ sources.
# --------------------------------------------------------------------------- #

HANDLE_R = 0.0095            # straight handle radius (slim stone shaft)
HANDLE_HALF = 0.052          # handle half-length along Z (handle spans ~0.104)
COLLAR_R = 0.0115            # metal collar/ferrule radius
COLLAR_H = 0.012             # metal collar height

# waisted handle (S5)
HANDLE_R_END = 0.0095
HANDLE_R_WAIST = 0.0062
# flat paddle handle (S6)
HANDLE_W = 0.026             # paddle width along X
HANDLE_T = 0.0085            # paddle thickness along Y

FORK_ROD_R = 0.0018          # thin metal U-fork rod radius
ARM_ROD_R = 0.0020           # cantilever arm tube radius

TOP_AXLE_Z = 0.094           # z of the +Z (small) roller axle
BOT_AXLE_Z = -0.094          # z of the -Z (large) roller axle

# Nominal roller head sizes (large end; small is derived via SMALL_LARGE_RATIO).
LARGE_HALF_X = 0.025         # large roller half-length along axle (X) -> ~0.050 long
LARGE_RY = 0.018             # large roller cross radius
SMALL_LARGE_RATIO = 0.70     # small head = ratio * large head (form-preserving)

AXLE_CLEARANCE = 0.004       # fork_span = roller_half_x + clearance
SPIKY_NUB_R_RATIO = 0.155    # nub radius as fraction of ball radius
SPIKY_FORK_PAD = 0.003       # extra fork_span pad past nub for blade/cantilever

FACET_N_RADIAL_NOM = 10
FACET_N_AXIAL = 7
RIDGE_COUNT_NOM = 9

# blade yoke (S7)
YOKE_PLATE_THICK = 0.0020
YOKE_STEM_HW = 0.0030
YOKE_ARM_W = 0.0050
YOKE_SPLIT_FRAC = 0.40


# --------------------------------------------------------------------------- #
# Palettes — stone + metal colorways (≥3, target 4-6).
# --------------------------------------------------------------------------- #

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_jade": {
        "stone": (0.62, 0.78, 0.60, 1.0),
        "metal": (0.78, 0.77, 0.74, 1.0),
    },
    "rose_quartz": {
        "stone": (0.92, 0.74, 0.78, 1.0),
        "metal": (0.86, 0.72, 0.50, 1.0),  # rose-gold ferrules
    },
    "amethyst": {
        "stone": (0.58, 0.44, 0.74, 1.0),
        "metal": (0.80, 0.80, 0.82, 1.0),
    },
    "dark_germanium": {
        "stone": (0.22, 0.23, 0.26, 1.0),
        "metal": (0.70, 0.70, 0.72, 1.0),
    },
    "obsidian_steel": {
        "stone": (0.10, 0.10, 0.12, 1.0),
        "metal": (0.55, 0.56, 0.60, 1.0),
    },
    "white_marble_gold": {
        "stone": (0.93, 0.92, 0.88, 1.0),
        "metal": (0.84, 0.70, 0.40, 1.0),  # gold ferrules
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class SkincareRollerConfig:
    """Public configuration sampled by ``config_from_seed`` or supplied directly."""

    roller_head_form: RollerHeadForm = "smooth_oval"
    handle_form: HandleForm = "straight_stone_bar"
    fork_yoke_form: ForkYokeForm = "u_wire_fork"
    roller_count: int = 2
    palette_style: PaletteStyle = "classic_jade"
    handle_half_scale: float = 1.0
    roller_size_scale: float = 1.0
    ridge_count: int = RIDGE_COUNT_NOM
    facet_n_radial: int = FACET_N_RADIAL_NOM
    name: str = "reference_skincare_roller"


@dataclass(frozen=True)
class ResolvedSkincareRollerConfig:
    roller_head_form: RollerHeadForm
    handle_form: HandleForm
    fork_yoke_form: ForkYokeForm
    roller_count: int
    palette_style: PaletteStyle
    handle_half_scale: float
    roller_size_scale: float
    ridge_count: int
    facet_n_radial: int
    name: str
    # derived
    palette: dict[str, tuple[float, float, float, float]]
    handle_half: float
    large_half_x: float
    large_ry: float
    small_half_x: float
    small_ry: float


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> SkincareRollerConfig:
    """Deterministic per-seed sampling of all three slots, count, palette, scales.

    ``seed=0`` is not special. Every seed independently samples Slot A/B/C, the
    ``roller_count`` multiplicity (near-uniform), a colorway, and the continuous
    scales. The cantilever×N=2 down-weighting and spiky clearance handling are
    enforced in ``resolve_config`` / the builder.
    """
    rng = random.Random(seed)

    head: RollerHeadForm = rng.choices(ROLLER_HEAD_FORMS, weights=_HEAD_WEIGHTS, k=1)[0]
    handle: HandleForm = rng.choices(HANDLE_FORMS, weights=_HANDLE_WEIGHTS, k=1)[0]
    yoke: ForkYokeForm = rng.choices(FORK_YOKE_FORMS, weights=_YOKE_WEIGHTS, k=1)[0]
    count: int = rng.choices(_COUNT_VALUES, weights=_COUNT_WEIGHTS, k=1)[0]

    # Compatibility gate (sampler side): single_cantilever_arm strongly favors a
    # single-ended tool. If a cantilever happens to draw N=2, re-roll the count
    # toward N=1 most of the time so the rare twin-cantilever stays sparse.
    if yoke == "single_cantilever_arm" and count == 2:
        if rng.random() < 0.7:
            count = 1

    palette: PaletteStyle = rng.choice(PALETTE_STYLES)

    handle_half_scale = round(rng.uniform(0.90, 1.10), 4)
    roller_size_scale = round(rng.uniform(0.85, 1.15), 4)
    ridge_count = rng.randint(6, 12)
    facet_n_radial = rng.randint(8, 12)

    return SkincareRollerConfig(
        roller_head_form=head,
        handle_form=handle,
        fork_yoke_form=yoke,
        roller_count=count,
        palette_style=palette,
        handle_half_scale=handle_half_scale,
        roller_size_scale=roller_size_scale,
        ridge_count=ridge_count,
        facet_n_radial=facet_n_radial,
        name=f"seeded_skincare_roller_{seed}",
    )


def resolve_config(config: SkincareRollerConfig) -> ResolvedSkincareRollerConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    head = _pick(config.roller_head_form, ROLLER_HEAD_FORMS)
    handle = _pick(config.handle_form, HANDLE_FORMS)
    yoke = _pick(config.fork_yoke_form, FORK_YOKE_FORMS)
    count = config.roller_count if config.roller_count in (1, 2) else 2

    handle_half_scale = _clamp(config.handle_half_scale, 0.90, 1.10)
    roller_size_scale = _clamp(config.roller_size_scale, 0.85, 1.15)
    ridge_count = int(_clamp(config.ridge_count, 6, 12))
    facet_n_radial = int(_clamp(config.facet_n_radial, 8, 12))

    # Derived size chain. Large head from roller_size_scale; small head is the
    # form-preserving ratio of the large head (SMALL_LARGE_RATIO).
    large_half_x = LARGE_HALF_X * roller_size_scale
    large_ry = LARGE_RY * roller_size_scale
    small_half_x = SMALL_LARGE_RATIO * large_half_x
    small_ry = SMALL_LARGE_RATIO * large_ry

    handle_half = HANDLE_HALF * handle_half_scale

    return ResolvedSkincareRollerConfig(
        roller_head_form=head,
        handle_form=handle,
        fork_yoke_form=yoke,
        roller_count=count,
        palette_style=config.palette_style,
        handle_half_scale=handle_half_scale,
        roller_size_scale=roller_size_scale,
        ridge_count=ridge_count,
        facet_n_radial=facet_n_radial,
        name=config.name,
        palette=dict(PALETTES[config.palette_style]),
        handle_half=handle_half,
        large_half_x=large_half_x,
        large_ry=large_ry,
        small_half_x=small_half_x,
        small_ry=small_ry,
    )


# --------------------------------------------------------------------------- #
# Per-unit geometry resolution.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _RollerUnit:
    """Resolved per-roller-unit geometry (one fork + roller + spin joint)."""

    index: int
    is_small: bool
    half_x: float          # half-length along axle (X); for spiky = ball_r
    ry: float              # cross radius
    fork_span: float       # half-spacing of fork tips along X
    z_root: float          # collar end where the fork roots
    z_axle: float          # axle height
    mass: float
    effort: float


def _spiky_geom(r: ResolvedSkincareRollerConfig, half_x: float, ry: float) -> tuple[float, float]:
    """For spiky_germanium the head is a near-sphere: ball_r = max cross extent.

    Returns ``(ball_r, nub_r)``. The ball radius is taken from the cross radius
    (round Y≈Z), the axial extent matches via the same ball_r.
    """
    ball_r = ry
    nub_r = ball_r * SPIKY_NUB_R_RATIO
    return ball_r, nub_r


def _resolve_units(r: ResolvedSkincareRollerConfig) -> list[_RollerUnit]:
    """Resolve the roller units to emit.

    N=2 → unit 0 = small (+Z), unit 1 = large (-Z).
    N=1 → single large unit at -Z (+Z gets a static stone_tip, no unit).
    fork_span is derived per head form; spiky widens it past the nub field and
    the blade/cantilever variants add an extra pad so nubs never hit the arms.
    """
    units: list[_RollerUnit] = []
    is_spiky = r.roller_head_form == "spiky_germanium"
    pad_for_yoke = SPIKY_FORK_PAD if r.fork_yoke_form in ("flat_blade_yoke", "single_cantilever_arm") else 0.0

    def span_for(half_x: float, ry: float) -> float:
        if is_spiky:
            ball_r, nub_r = _spiky_geom(r, half_x, ry)
            return ball_r + nub_r + AXLE_CLEARANCE + pad_for_yoke
        return half_x + AXLE_CLEARANCE

    if r.roller_count == 2:
        # small (+Z)
        s_hx, s_ry = r.small_half_x, r.small_ry
        units.append(
            _RollerUnit(
                index=0,
                is_small=True,
                half_x=(s_ry if is_spiky else s_hx),
                ry=s_ry,
                fork_span=span_for(s_hx, s_ry),
                # Root the fork stem INSIDE the collar (collar center) so its
                # base solidly overlaps the collar/handle solid — never outboard
                # of the collar's outer face (that left a ~0.002 m floating gap
                # for the blade/u-wire stems).
                z_root=(r.handle_half - COLLAR_H * 0.25),
                z_axle=TOP_AXLE_Z,
                mass=0.02,
                effort=0.2,
            )
        )
    # large (-Z) is always present (both N=1 and N=2)
    l_hx, l_ry = r.large_half_x, r.large_ry
    units.append(
        _RollerUnit(
            index=(1 if r.roller_count == 2 else 0),
            is_small=False,
            half_x=(l_ry if is_spiky else l_hx),
            ry=l_ry,
            fork_span=span_for(l_hx, l_ry),
            z_root=-(r.handle_half - COLLAR_H * 0.25),
            z_axle=BOT_AXLE_Z,
            mass=0.045,
            effort=0.3,
        )
    )
    return units


# --------------------------------------------------------------------------- #
# Slot B — handle geometry (static body visual).
# --------------------------------------------------------------------------- #


def _asset_mesh_from_geometry(geometry, name: str, assets: AssetContext):
    return mesh_from_geometry(geometry, assets.mesh_path(f"{name}.obj"))


def _handle_mesh(r: ResolvedSkincareRollerConfig, assets: AssetContext):
    hh = r.handle_half
    if r.handle_form == "contoured_waisted":
        n_profile = 48
        profile = []
        for i in range(n_profile + 1):
            t = -1.0 + 2.0 * i / n_profile
            z = t * hh
            blend = (1.0 - math.cos(math.pi * abs(t))) * 0.5
            rr = HANDLE_R_WAIST + (HANDLE_R_END - HANDLE_R_WAIST) * blend
            profile.append((rr, z))
        profile.insert(0, (0.0, -hh))
        profile.append((0.0, hh))
        geom = LatheGeometry(profile, segments=40)
        return _asset_mesh_from_geometry(geom, "handle", assets)
    if r.handle_form == "flat_paddle_bar":
        prof = superellipse_profile(HANDLE_W, HANDLE_T, exponent=2.0, segments=48)
        geom = ExtrudeGeometry(prof, 2.0 * hh, cap=True, center=True)
        return _asset_mesh_from_geometry(geom, "handle", assets)
    # straight_stone_bar (S1)
    handle = CylinderGeometry(HANDLE_R, 2.0 * hh, radial_segments=40)
    bulge = SphereGeometry(1.0, width_segments=36, height_segments=20)
    bulge.scale(HANDLE_R * 1.07, HANDLE_R * 1.07, hh * 0.62)
    handle.merge(bulge)
    return _asset_mesh_from_geometry(handle, "handle", assets)


def _handle_inertial(r: ResolvedSkincareRollerConfig) -> Inertial:
    if r.handle_form == "flat_paddle_bar":
        return Inertial.from_geometry(
            Box((HANDLE_W, HANDLE_T, 2.0 * r.handle_half + 0.06)),
            mass=0.18,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
    return Inertial.from_geometry(
        Box((0.06, 0.025, 0.20)), mass=0.18, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )


def _stone_tip_mesh(r: ResolvedSkincareRollerConfig, assets: AssetContext):
    """Rounded static stone cap for the +Z end when N=1 (adopted: S8)."""
    cap_r = HANDLE_R * 1.05
    dome = SphereGeometry(cap_r, width_segments=28, height_segments=18)
    dome.scale(1.0, 1.0, 0.72)
    z_collar_top = r.handle_half - COLLAR_H * 0.25 + COLLAR_H * 0.5
    dome.translate(0.0, 0.0, z_collar_top + cap_r * 0.72 * 0.35)
    return _asset_mesh_from_geometry(dome, "stone_tip", assets)


# --------------------------------------------------------------------------- #
# Slot C — fork / yoke geometry (static body visual).
# --------------------------------------------------------------------------- #


def _u_fork_mesh(z_root: float, z_axle: float, span: float, name: str, assets: AssetContext):
    """U-shaped continuous bent-tube fork, two arms to ±X tips (adopted: S1)."""
    direction = 1.0 if z_axle > z_root else -1.0
    z_tip = z_axle
    pts = [
        (span, 0.0, z_tip),
        (span, 0.0, z_tip - direction * (z_tip - z_root) * 0.45),
        (span * 0.55, 0.0, z_root + direction * 0.010),
        (0.0, 0.0, z_root),
        (-span * 0.55, 0.0, z_root + direction * 0.010),
        (-span, 0.0, z_tip - direction * (z_tip - z_root) * 0.45),
        (-span, 0.0, z_tip),
    ]
    geom = tube_from_spline_points(
        pts, radius=FORK_ROD_R, samples_per_segment=16, radial_segments=14, cap_ends=True
    )
    # Fixed bearing axle-pin spanning the two fork tips through the centerline at
    # z_axle. This is the real mechanism: the stone roller spins ABOUT this fixed
    # fork pin (the pin is parent/body geometry; the stone is the child). It also
    # anchors the spin-joint origin (x=0, z=z_axle) to real fork geometry — the U
    # mouth is otherwise open at the centerline. The pin sits inside the stone
    # (declared fork↔stone overlap in the test allowances).
    pin = CylinderGeometry(FORK_ROD_R * 0.9, 2.0 * span, radial_segments=14)
    pin.rotate_y(math.pi / 2.0)
    pin.translate(0.0, 0.0, z_tip)
    geom.merge(pin)
    return _asset_mesh_from_geometry(geom, name, assets)


def _blade_yoke_mesh(
    z_root: float,
    z_axle: float,
    span: float,
    name: str,
    assets: AssetContext,
):
    """Flat stamped Y-blade yoke: XZ profile extruded along Y (adopted: S7)."""
    direction = 1.0 if z_axle > z_root else -1.0
    total_h = abs(z_axle - z_root)
    z_split = z_root + direction * total_h * YOKE_SPLIT_FRAC

    sw = YOKE_STEM_HW
    aw = YOKE_ARM_W * 0.5

    dx_l, dz_l = -span, z_axle - z_split
    arm_len = math.sqrt(dx_l * dx_l + dz_l * dz_l)
    nx, nz = -dz_l / arm_len, dx_l / arm_len

    pts = [
        (sw, z_root),
        (sw, z_split),
        (span + aw * nx, z_axle + aw * nz),
        (span, z_axle + aw * 0.5 * direction),
        (span - aw * nx, z_axle - aw * nz),
        (aw * 0.3, z_split + direction * aw * 0.5),
        (-aw * 0.3, z_split + direction * aw * 0.5),
        (-span + aw * nx, z_axle - aw * nz),
        (-span, z_axle + aw * 0.5 * direction),
        (-span - aw * nx, z_axle + aw * nz),
        (-sw, z_split),
        (-sw, z_root),
    ]
    xy_profile = [(p[0], p[1]) for p in pts]
    yoke = ExtrudeGeometry(xy_profile, YOKE_PLATE_THICK, cap=True, center=True)
    yoke.rotate_x(math.pi / 2.0)
    # Fixed centerline bearing pin between the blade tips at z_axle: the stone
    # spins about it and it anchors the x=0 spin-joint origin to real fork
    # geometry (the blade Y splits open at the centerline near the axle).
    pin = CylinderGeometry(FORK_ROD_R * 0.9, 2.0 * span, radial_segments=14)
    pin.rotate_y(math.pi / 2.0)
    pin.translate(0.0, 0.0, z_axle)
    yoke.merge(pin)
    return _asset_mesh_from_geometry(yoke, name, assets)


def _cantilever_arm_mesh(
    z_root: float,
    z_axle: float,
    reach: float,
    name: str,
    assets: AssetContext,
):
    """Single cantilever bent-tube arm from collar to a -X tip (adopted: S8)."""
    dz = z_axle - z_root
    direction = 1.0 if dz > 0.0 else -1.0
    z_embed = z_root - direction * COLLAR_H * 0.5
    pts = [
        (0.0, 0.0, z_embed),
        (0.0, 0.0, z_root),
        (0.0, 0.0, z_root + dz * 0.40),
        (-reach * 0.30, 0.0, z_root + dz * 0.70),
        (-reach * 0.68, 0.0, z_root + dz * 0.90),
        (-reach, 0.0, z_axle),
    ]
    geom = tube_from_spline_points(
        pts, radius=ARM_ROD_R, samples_per_segment=18, radial_segments=14, cap_ends=True
    )
    return _asset_mesh_from_geometry(geom, name, assets)


# --------------------------------------------------------------------------- #
# Slot A — roller head geometry (roller part visual).
# --------------------------------------------------------------------------- #


def _oval_roller_geom(half_x: float, ry: float):
    body = SphereGeometry(1.0, width_segments=36, height_segments=24)
    body.scale(half_x, ry, ry)
    marker = SphereGeometry(0.0028, width_segments=12, height_segments=8)
    marker.translate(0.0, ry * 0.96, 0.0)
    body.merge(marker)
    return body


def _faceted_roller_geom(half_x: float, ry: float, n_radial: int):
    mesh = MeshGeometry()
    n_ax = FACET_N_AXIAL
    n_rd = n_radial
    ring_verts: list[list[int]] = []
    for i in range(n_ax):
        t = i / (n_ax - 1)
        x = -half_x + t * 2.0 * half_x
        rr = ry * (0.45 + 0.55 * math.sin(t * math.pi))
        ring: list[int] = []
        for j in range(n_rd):
            angle = 2.0 * math.pi * j / n_rd
            y = rr * math.cos(angle)
            z = rr * math.sin(angle)
            idx = mesh.add_vertex(x, y, z)
            ring.append(idx)
        ring_verts.append(ring)
    for i in range(n_ax - 1):
        for j in range(n_rd):
            jn = (j + 1) % n_rd
            a = ring_verts[i][j]
            b = ring_verts[i][jn]
            c = ring_verts[i + 1][j]
            d = ring_verts[i + 1][jn]
            mesh.add_face(a, b, d)
            mesh.add_face(a, d, c)
    cap_lo = mesh.add_vertex(-half_x, 0.0, 0.0)
    for j in range(n_rd):
        jn = (j + 1) % n_rd
        mesh.add_face(cap_lo, ring_verts[0][jn], ring_verts[0][j])
    cap_hi = mesh.add_vertex(half_x, 0.0, 0.0)
    for j in range(n_rd):
        jn = (j + 1) % n_rd
        mesh.add_face(cap_hi, ring_verts[-1][j], ring_verts[-1][jn])
    geom = mesh
    # Asymmetric table-facet marker on +Y so a quarter spin visibly changes the
    # YZ silhouette (a regular n-gon barrel is otherwise near-axisymmetric).
    marker = SphereGeometry(max(0.0030, ry * 0.22), width_segments=12, height_segments=8)
    marker.translate(0.0, ry * 0.92, 0.0)
    geom.merge(marker)
    return geom


def _spiky_ball_geom(ball_r: float, nub_r: float, n_lat: int, n_lon: int):
    core = SphereGeometry(ball_r, width_segments=36, height_segments=24)
    for i in range(n_lat):
        theta = math.pi * (0.14 + 0.72 * (i + 0.5) / n_lat)
        phi_offset = (math.pi / n_lon) if (i % 2 == 1) else 0.0
        for j in range(n_lon):
            phi = 2.0 * math.pi * j / n_lon + phi_offset
            nx = math.cos(theta)
            ny = math.sin(theta) * math.cos(phi)
            nz = math.sin(theta) * math.sin(phi)
            offset = ball_r + nub_r * 0.35
            nub = SphereGeometry(nub_r, width_segments=10, height_segments=8)
            nub.translate(offset * nx, offset * ny, offset * nz)
            core.merge(nub)
    # One prominent asymmetric crown nub on +Y so a quarter spin visibly changes
    # the YZ silhouette (the lat/lon nub field is otherwise near-axisymmetric).
    crown = SphereGeometry(nub_r * 1.6, width_segments=12, height_segments=8)
    crown.translate(0.0, ball_r + nub_r * 0.9, 0.0)
    core.merge(crown)
    return core


def _ridged_roller_geom(half_x: float, ry: float, num_ridges: int):
    ridge_depth = ry * 0.16
    n_samples = num_ridges * 14 + 1
    profile = [(0.0, -half_x)]
    for j in range(n_samples):
        t = j / (n_samples - 1)
        z = -half_x + t * 2.0 * half_x
        rr = ry - ridge_depth * 0.5 * (1.0 - math.cos(2.0 * math.pi * num_ridges * t))
        profile.append((max(rr, 0.001), z))
    profile.append((0.0, half_x))
    barrel = LatheGeometry(profile, segments=48, closed=True)
    barrel.rotate_y(math.pi / 2.0)
    marker = SphereGeometry(0.0028, width_segments=12, height_segments=8)
    marker.translate(0.0, ry * 0.92, 0.0)
    barrel.merge(marker)
    return barrel


def _roller_head_geom(r: ResolvedSkincareRollerConfig, unit: _RollerUnit):
    """Return the roller head geometry (centered at origin, axle along X)."""
    if r.roller_head_form == "faceted_gem":
        return _faceted_roller_geom(unit.half_x, unit.ry, r.facet_n_radial)
    if r.roller_head_form == "spiky_germanium":
        ball_r, nub_r = _spiky_geom(r, unit.half_x, unit.ry)
        n_lat = 4 if unit.is_small else 5
        n_lon = 7 if unit.is_small else 8
        return _spiky_ball_geom(ball_r, nub_r, n_lat, n_lon)
    if r.roller_head_form == "textured_ridged":
        nr = max(6, r.ridge_count - (2 if unit.is_small else 0))
        return _ridged_roller_geom(unit.half_x, unit.ry, nr)
    return _oval_roller_geom(unit.half_x, unit.ry)


# --------------------------------------------------------------------------- #
# Builders.
# --------------------------------------------------------------------------- #


def _stone_elem(r: ResolvedSkincareRollerConfig, i: int) -> str:
    return f"roller_stone_{i}"


def _build_roller_unit(
    model: ArticulatedObject,
    body,
    r: ResolvedSkincareRollerConfig,
    unit: _RollerUnit,
    mats: dict,
) -> None:
    """Emit one fork (body visual) + roller part + CONTINUOUS spin joint."""
    metal = mats["metal"]
    stone = mats["stone"]
    i = unit.index
    fork_name = f"fork_{i}"
    is_cantilever = r.fork_yoke_form == "single_cantilever_arm"

    # --- Slot C: fork / yoke (static body visual) --------------------------- #
    if is_cantilever:
        reach = unit.half_x + 0.003
        body.visual(
            _cantilever_arm_mesh(unit.z_root, unit.z_axle, reach, fork_name, model.assets),
            material=metal,
            name=fork_name, material_class_id=("metal.precious_gold" if r.palette_style in {"classic_jade", "amethyst", "dark_germanium", "obsidian_steel", "white_marble_gold"} else "metal.copper_bare"),
        )
    elif r.fork_yoke_form == "flat_blade_yoke":
        body.visual(
            _blade_yoke_mesh(unit.z_root, unit.z_axle, unit.fork_span, fork_name, model.assets),
            material=metal,
            name=fork_name, material_class_id=("metal.precious_gold" if r.palette_style in {"classic_jade", "amethyst", "dark_germanium", "obsidian_steel", "white_marble_gold"} else "metal.copper_bare"),
        )
    else:  # u_wire_fork
        body.visual(
            _u_fork_mesh(unit.z_root, unit.z_axle, unit.fork_span, fork_name, model.assets),
            material=metal,
            name=fork_name, material_class_id=("metal.precious_gold" if r.palette_style in {"classic_jade", "amethyst", "dark_germanium", "obsidian_steel", "white_marble_gold"} else "metal.copper_bare"),
        )

    # --- Slot A: roller head part ------------------------------------------- #
    roller = model.part(f"roller_{i}")
    stone_geom = _roller_head_geom(r, unit)
    axle_r = (ARM_ROD_R * 0.8) if is_cantilever else (FORK_ROD_R * 0.85)

    if is_cantilever:
        # Stone centered at world x=0 -> local +reach offset; stub from arm tip.
        reach = unit.half_x + 0.003
        stub_len = reach + unit.half_x * 0.65
        stone_geom.translate(reach, 0.0, 0.0)
        roller.visual(
            _asset_mesh_from_geometry(stone_geom, _stone_elem(r, i), model.assets),
            material=stone,
            name=_stone_elem(r, i), material_class_id=("marble.generic" if r.palette_style == "white_marble_gold" else "stone.polished_granite"),
        )
        stub = CylinderGeometry(axle_r, stub_len, radial_segments=16)
        stub.rotate_y(math.pi / 2.0)
        stub.translate(stub_len / 2.0, 0.0, 0.0)
        roller.visual(
            _asset_mesh_from_geometry(stub, f"axle_{i}", model.assets),
            material=metal,
            name=f"axle_{i}", material_class_id=("metal.precious_gold" if r.palette_style in {"classic_jade", "amethyst", "dark_germanium", "obsidian_steel", "white_marble_gold"} else "metal.copper_bare"),
        )
        joint_origin = Origin(xyz=(-reach, 0.0, unit.z_axle))
    else:
        roller.visual(
            _asset_mesh_from_geometry(stone_geom, _stone_elem(r, i), model.assets),
            material=stone,
            name=_stone_elem(r, i), material_class_id=("marble.generic" if r.palette_style == "white_marble_gold" else "stone.polished_granite"),
        )
        axle = CylinderGeometry(
            axle_r, 2.0 * unit.fork_span + 0.004, radial_segments=16
        ).rotate_y(math.pi / 2.0)
        roller.visual(
            _asset_mesh_from_geometry(axle, f"axle_{i}", model.assets),
            material=metal,
            name=f"axle_{i}", material_class_id=("metal.precious_gold" if r.palette_style in {"classic_jade", "amethyst", "dark_germanium", "obsidian_steel", "white_marble_gold"} else "metal.copper_bare"),
        )
        joint_origin = Origin(xyz=(0.0, 0.0, unit.z_axle))

    roller.inertial = Inertial.from_geometry(
        Box((2.0 * unit.half_x, 2.0 * unit.ry, 2.0 * unit.ry)), mass=unit.mass
    )

    model.articulation(
        f"roller_spin_{i}",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=roller,
        origin=joint_origin,
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=unit.effort, velocity=8.0),
    )


def _materials(model: ArticulatedObject, r: ResolvedSkincareRollerConfig) -> dict:
    out = {}
    for key, rgba in r.palette.items():
        out[key] = model.material(f"skincare_roller_{key}_{r.palette_style}", rgba=rgba)
    return out


def build_skincare_roller(
    config: SkincareRollerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or SkincareRollerConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-skincare-roller-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["adopted_source_ids"] = ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8")
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    mats = _materials(model, r)
    stone = mats["stone"]
    metal = mats["metal"]

    # --- Static handle body ------------------------------------------------- #
    body = model.part("body")
    body.visual(_handle_mesh(r, model.assets), material=stone, name="handle", material_class_id=("marble.generic" if r.palette_style == "white_marble_gold" else "stone.polished_granite"))

    # Collars at both ends (static decoration on the handle).
    top_collar = CylinderGeometry(COLLAR_R, COLLAR_H, radial_segments=40)
    top_collar.translate(0.0, 0.0, r.handle_half - COLLAR_H * 0.25)
    body.visual(
        _asset_mesh_from_geometry(top_collar, "top_collar", model.assets),
        material=metal,
        name="top_collar", material_class_id=("metal.precious_gold" if r.palette_style in {"classic_jade", "amethyst", "dark_germanium", "obsidian_steel", "white_marble_gold"} else "metal.copper_bare"),
    )

    bot_collar = CylinderGeometry(COLLAR_R, COLLAR_H, radial_segments=40)
    bot_collar.translate(0.0, 0.0, -(r.handle_half - COLLAR_H * 0.25))
    body.visual(
        _asset_mesh_from_geometry(bot_collar, "bottom_collar", model.assets),
        material=metal,
        name="bottom_collar", material_class_id=("metal.precious_gold" if r.palette_style in {"classic_jade", "amethyst", "dark_germanium", "obsidian_steel", "white_marble_gold"} else "metal.copper_bare"),
    )

    # N=1: static rounded stone tip caps the +Z end (no fork, no moving part).
    if r.roller_count == 1:
        body.visual(_stone_tip_mesh(r, model.assets), material=stone, name="stone_tip", material_class_id=("marble.generic" if r.palette_style == "white_marble_gold" else "stone.polished_granite"))

    body.inertial = _handle_inertial(r)

    # --- Roller units (parallel children + multiplicity) -------------------- #
    for unit in _resolve_units(r):
        _build_roller_unit(model, body, r, unit, mats)

    return model


def build_seeded_skincare_roller(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_skincare_roller(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices.
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedSkincareRollerConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("roller_head_form", r.roller_head_form),
        ("handle_form", r.handle_form),
        ("fork_yoke_form", r.fork_yoke_form),
        ("roller_count", str(r.roller_count)),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _declare_overlap_allowances(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedSkincareRollerConfig
) -> None:
    body = model.get_part("body")
    for unit in _resolve_units(r):
        i = unit.index
        roller = model.get_part(f"roller_{i}")
        ctx.allow_overlap(
            roller,
            body,
            elem_a=f"axle_{i}",
            elem_b=f"fork_{i}",
            reason=f"Roller {i} axle ends are intentionally seated through the fork tips.",
        )
        # The u-wire fork and blade yoke each carry a fixed centerline bearing
        # pin that the stone roller spins about; the pin is intentionally inside
        # the stone body.
        if r.fork_yoke_form in ("u_wire_fork", "flat_blade_yoke"):
            ctx.allow_overlap(
                roller,
                body,
                elem_a=_stone_elem(r, i),
                elem_b=f"fork_{i}",
                reason=f"Roller {i} stone spins about the fork's fixed centerline bearing pin.",
            )


def run_skincare_roller_tests(
    object_model: ArticulatedObject, config: SkincareRollerConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlap_allowances(ctx, object_model, r)

    body = object_model.get_part("body")
    part_names = {p.name for p in object_model.parts}
    joint_names = {a.name for a in object_model.articulations}
    units = _resolve_units(r)
    bp = ctx.part_world_position(body)

    # --- Roller count identity ---------------------------------------------- #
    roller_parts = sorted(n for n in part_names if n.startswith("roller_"))
    ctx.check(
        f"exactly {r.roller_count} roller part(s)",
        len(roller_parts) == r.roller_count,
        details=f"roller parts: {roller_parts}",
    )

    if r.roller_count == 1:
        body_visuals = {v.name for v in body.visuals}
        ctx.check(
            "single-ended: top end has a static stone_tip and no top fork",
            "stone_tip" in body_visuals and "fork_1" not in body_visuals,
            details=f"body visuals: {sorted(body_visuals)}",
        )
        tip_aabb = ctx.part_element_world_aabb(body, elem="stone_tip")
        ctx.check(
            "stone tip sits above the handle center",
            tip_aabb is not None and tip_aabb[0][2] > bp[2],
            details=f"tip_min_z={tip_aabb[0][2]:.4f}, body_z={bp[2]:.4f}",
        )
    else:
        ctx.check(
            "twin-ended: no static stone_tip",
            "stone_tip" not in {v.name for v in body.visuals},
            details=str(sorted(v.name for v in body.visuals)),
        )

    # --- Per-unit checks: capture, placement, CONTINUOUS spin --------------- #
    for unit in units:
        i = unit.index
        roller = object_model.get_part(f"roller_{i}")
        spin = object_model.get_articulation(f"roller_spin_{i}")
        stone_elem = _stone_elem(r, i)

        # Roller axle captured by its fork.
        ctx.expect_contact(roller, body, name=f"roller_{i} captured by its fork")

        # Spin joint is CONTINUOUS about +X.
        ctx.check(
            f"roller_spin_{i} is CONTINUOUS about +X",
            spin.articulation_type == ArticulationType.CONTINUOUS
            and abs(spin.axis[0]) > 0.99,
            details=f"type={spin.articulation_type}, axis={spin.axis}",
        )

        # Cantilever joint origin is offset to (-reach,0,z), not (0,0,z).
        if r.fork_yoke_form == "single_cantilever_arm":
            ox = spin.origin.xyz[0]
            ctx.check(
                f"cantilever roller_spin_{i} origin offset off-axis (-reach)",
                ox < -0.005,
                details=f"origin_x={ox:.4f}",
            )
        else:
            ox = spin.origin.xyz[0]
            ctx.check(
                f"roller_spin_{i} origin on the handle axis (x=0)",
                abs(ox) < 1e-6,
                details=f"origin_x={ox:.4f}",
            )

        # Roller placement along Z relative to the handle center.
        rp = ctx.part_world_position(roller)
        if unit.z_axle < 0:
            ctx.check(
                f"roller_{i} sits at the -Z (bottom) end below the handle center",
                rp is not None and rp[2] < bp[2],
                details=f"roller_z={rp[2]:.4f}, body_z={bp[2]:.4f}",
            )
        else:
            ctx.check(
                f"roller_{i} sits at the +Z (top) end above the handle center",
                rp is not None and rp[2] > bp[2],
                details=f"roller_z={rp[2]:.4f}, body_z={bp[2]:.4f}",
            )

        # Spin changes the YZ silhouette (proves a real free roll).
        r0 = _ext(ctx.part_world_aabb(roller))
        with ctx.pose({spin: math.pi / 2.0}):
            r90 = _ext(ctx.part_world_aabb(roller))
        ctx.check(
            f"roller_{i} spin changes its YZ silhouette",
            abs(r90[1] - r0[1]) > 0.0008 or abs(r90[2] - r0[2]) > 0.0008,
            details=f"rest={r0}, quarter={r90}",
        )

    # --- Twin-ended: small head at +Z, large head at -Z --------------------- #
    if r.roller_count == 2:
        small = object_model.get_part("roller_0")
        large = object_model.get_part("roller_1")
        small_ext = _ext(ctx.part_element_world_aabb(small, elem=_stone_elem(r, 0)))
        large_ext = _ext(ctx.part_element_world_aabb(large, elem=_stone_elem(r, 1)))
        ctx.check(
            "bottom (-Z) roller head wider in cross-section than top (+Z)",
            large_ext[2] > small_ext[2] + 0.002,
            details=f"small_cross={small_ext[2]:.4f}, large_cross={large_ext[2]:.4f}",
        )

    # --- Handle sits between / above the rollers ---------------------------- #
    bottom_roller = object_model.get_part(f"roller_{units[-1].index}")
    brp = ctx.part_world_position(bottom_roller)
    ctx.check(
        "handle body center is above the bottom roller",
        brp is not None and bp[2] > brp[2],
        details=f"body_z={bp[2]:.4f}, bottom_roller_z={brp[2]:.4f}",
    )

    # --- Fork/yoke is a static body visual, not a separate part ------------- #
    ctx.check(
        "forks/yokes are static body visuals (no separate fork parts)",
        not any(n.startswith("fork_") for n in part_names),
        details=str(sorted(part_names)),
    )
    ctx.check(
        f"one spin joint per roller ({r.roller_count})",
        sum(1 for n in joint_names if n.startswith("roller_spin_")) == r.roller_count,
        details=str(sorted(joint_names)),
    )

    # --- Ground / rest sanity: object is roughly handle-length tall --------- #
    aabbs = [ctx.part_world_aabb(p) for p in object_model.parts]
    hi_z = max(a[1][2] for a in aabbs)
    lo_z = min(a[0][2] for a in aabbs)
    ctx.check(
        "overall vertical extent within the mature hand-tool domain",
        0.10 <= (hi_z - lo_z) <= 0.40,
        details=f"extent_z={hi_z - lo_z:.4f}",
    )

    return ctx.report()


__all__ = [
    "SkincareRollerConfig",
    "ResolvedSkincareRollerConfig",
    "build_skincare_roller",
    "build_seeded_skincare_roller",
    "config_from_seed",
    "resolve_config",
    "run_skincare_roller_tests",
    "slot_choices_for_seed",
    "__modular__",
]
