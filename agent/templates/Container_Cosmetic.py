# SPDX-License-Identifier: Apache-2.0

"""Container cosmetic — modular procedural template (concealer / palette compact).

Category identity: a FLAT-lying multi-pan cosmetic compact. The case lies flat
on the XY plane (+X = length, +Y = depth, +Z = thickness ~0.015-0.018 m), far
wider than it is thick. A shallow tray (ROOT) holds a grid / ring of N identical
recessed concealer pans (each in its own egg-crate cell), plus a silver rim
frame and divider grid. A lid/drawer closes over the pans by one of three
mechanisms (the main articulation); a mirror rides on the lid inner face (flip)
or the shell interior ceiling (drawer).

Three axes (spec ``Container_Cosmetic.md``):

  * ``case_footprint`` (3) — Slot A. The ROOT tray mesh + pan-layout policy:
      - rounded_rect:  long rounded-box tray, rectangular ROWS x COLS pan grid.
      - square_rounded: near-square rounded-box tray, square-ish pan grid.
      - round_disc:    circular disc tray + ring frame, radial RING pan layout.
  * ``closure_mechanism`` (3) — Slot B. The ROOT name + active-lid topology
    (each has >=1 non-fixed joint):
      - rear_hinge_flip_lid: ROOT=base, ``base_to_lid`` REVOLUTE -X at rear rim,
        mirror on the lid inner well. 2 parts / 1 joint.
      - slide_out_drawer: ROOT=shell (hollow sleeve, mirror on interior ceiling),
        ``shell_to_drawer`` PRISMATIC +X, pans ride the drawer. 2 parts / 1 joint.
      - flip_lid_with_clasp: ROOT=base + ``base_to_lid`` REVOLUTE -X +
        ``base_to_clasp`` REVOLUTE +X front-edge clasp catching a lid lip.
        3 parts / 2 joints.
  * ``pan_count`` — multiplicity axis N in [2, 24] (weighted small-N). Rect
    footprints factor N into (rows, cols); round footprints lay N out on one
    ring (N<=8) or two rings (N>8). All pans share ``_pan_mesh`` and one
    ``_pan_centers`` loop; each pan seats recessed in its own cell pocket.

Continuous size/proportion variation (length / depth / height / joint-travel
scales + a derived pan_size equation) lives in ``resolve_config`` as clamped
params, never as slot candidates. ``palette_style`` (9 coordinated colorways +
finish) is a palette only, not a slot choice.

Sources (articraft_data ``picture/Container/Cosmetic`` 5-star pool): parent
``f124e974`` (rear-hinge flip, 2x4 pans), forks ``square_body`` / ``round_body``
(footprint), ``slide_drawer`` (prismatic drawer), ``clasp_latch_lid`` (flip +
clasp), ``n4_pans`` / ``n12_pans`` (multiplicity).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Container_Cosmetic.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    CylinderGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
CaseFootprint = Literal["rounded_rect", "square_rounded", "round_disc"]
ClosureMechanism = Literal[
    "rear_hinge_flip_lid",
    "slide_out_drawer",
    "flip_lid_with_clasp",
]
PaletteStyle = Literal[
    "classic_skin_silver",
    "rose_gold_nude",
    "matte_black_jewel",
    "clear_acrylic_pastel",
    "warm_brass_cream",
    "glossy_ivory_gold",
    "pearl_blush_silver",
    "marble_white_rosegold",
    "frosted_mint_silver",
    "graphite_silver_metal",
]

CASE_FOOTPRINTS: tuple[CaseFootprint, ...] = (
    "rounded_rect",
    "square_rounded",
    "round_disc",
)
CLOSURE_MECHANISMS: tuple[ClosureMechanism, ...] = (
    "rear_hinge_flip_lid",
    "slide_out_drawer",
    "flip_lid_with_clasp",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_skin_silver",
    "rose_gold_nude",
    "matte_black_jewel",
    "clear_acrylic_pastel",
    "warm_brass_cream",
    "glossy_ivory_gold",
    "pearl_blush_silver",
    "marble_white_rosegold",
    "frosted_mint_silver",
    "graphite_silver_metal",
)

# Weighted N domain: small N most common (real compacts are mostly a handful of
# pans), large N rare. N in [2, 24]; samples cover {4, 8, 12}.
_PAN_COUNT_WEIGHTS: tuple[tuple[int, float], ...] = (
    (2, 0.06),
    (3, 0.06),
    (4, 0.14),
    (5, 0.06),
    (6, 0.13),
    (8, 0.14),
    (9, 0.09),
    (10, 0.06),
    (12, 0.09),
    (15, 0.04),
    (16, 0.05),
    (18, 0.02),
    (20, 0.02),
    (24, 0.02),
)
_PAN_COUNT_VALUES: tuple[int, ...] = tuple(n for n, _ in _PAN_COUNT_WEIGHTS)
_PAN_COUNT_W: tuple[float, ...] = tuple(w for _, w in _PAN_COUNT_WEIGHTS)

# ---------------------------------------------------------------------------
# Palettes. Each colorway coordinates case body / frame+cell_grid / pan family /
# mirror+accent, with a finish tag (matte / high-gloss / metallic / pearl /
# clear-acrylic / rose-gold / brass / soft-touch / marble). Pan families anchor
# the 5-star PAN_COLORS (skin tones + correctors).
# ---------------------------------------------------------------------------
_PASTEL_PANS = [
    (0.93, 0.78, 0.62, 1.0),  # light beige
    (0.88, 0.70, 0.55, 1.0),  # warm tan
    (0.70, 0.86, 0.70, 1.0),  # green corrector
    (0.92, 0.62, 0.45, 1.0),  # peach corrector
    (0.95, 0.82, 0.68, 1.0),  # fair
    (0.84, 0.74, 0.86, 1.0),  # lavender corrector
    (0.90, 0.66, 0.50, 1.0),  # medium peach
    (0.86, 0.64, 0.42, 1.0),  # deep tan
]
_NUDE_PANS = [
    (0.91, 0.75, 0.58, 1.0),  # natural beige
    (0.86, 0.64, 0.42, 1.0),  # deep tan
    (0.82, 0.60, 0.44, 1.0),  # caramel
    (0.96, 0.86, 0.74, 1.0),  # ivory
    (0.88, 0.70, 0.55, 1.0),  # warm tan
    (0.93, 0.78, 0.62, 1.0),  # light beige
]
_JEWEL_PANS = [
    (0.78, 0.56, 0.38, 1.0),  # espresso
    (0.82, 0.60, 0.44, 1.0),  # caramel
    (0.70, 0.86, 0.70, 1.0),  # green corrector
    (0.84, 0.74, 0.86, 1.0),  # lavender corrector
    (0.86, 0.64, 0.42, 1.0),  # deep tan
    (0.90, 0.66, 0.50, 1.0),  # medium peach
]
_WARM_PANS = [
    (0.88, 0.70, 0.55, 1.0),  # warm tan
    (0.92, 0.62, 0.45, 1.0),  # peach corrector
    (0.90, 0.66, 0.50, 1.0),  # medium peach
    (0.91, 0.75, 0.58, 1.0),  # natural beige
    (0.93, 0.78, 0.62, 1.0),  # light beige
]
_IVORY_PANS = [
    (0.96, 0.86, 0.74, 1.0),  # ivory
    (0.91, 0.75, 0.58, 1.0),  # natural beige
    (0.82, 0.60, 0.44, 1.0),  # caramel
    (0.93, 0.78, 0.62, 1.0),  # light beige
]
_NEUTRAL_PANS = [
    (0.88, 0.70, 0.55, 1.0),  # warm tan
    (0.90, 0.66, 0.50, 1.0),  # medium peach
    (0.86, 0.64, 0.42, 1.0),  # deep tan
    (0.82, 0.60, 0.44, 1.0),  # caramel
]

_SILVER = (0.78, 0.80, 0.83, 1.0)
_ROSE_GOLD = (0.83, 0.62, 0.55, 1.0)
_BRASS = (0.72, 0.62, 0.30, 1.0)
_GOLD = (0.80, 0.66, 0.34, 1.0)
_BRIGHT_SILVER = (0.85, 0.86, 0.88, 1.0)
_MIRROR = (0.82, 0.88, 0.92, 1.0)
_LABEL = (0.95, 0.95, 0.96, 1.0)


@dataclass(frozen=True)
class _Palette:
    case: tuple[float, float, float, float]
    frame: tuple[float, float, float, float]
    pans: list[tuple[float, float, float, float]]
    accent: tuple[float, float, float, float]
    mirror: tuple[float, float, float, float]
    label: tuple[float, float, float, float]


PALETTES: dict[PaletteStyle, _Palette] = {
    "classic_skin_silver": _Palette(
        case=(0.10, 0.10, 0.12, 1.0), frame=_SILVER, pans=_PASTEL_PANS,
        accent=_SILVER, mirror=_MIRROR, label=_LABEL,
    ),
    "rose_gold_nude": _Palette(
        case=(0.93, 0.88, 0.82, 1.0), frame=_ROSE_GOLD, pans=_NUDE_PANS,
        accent=_ROSE_GOLD, mirror=_MIRROR, label=(0.96, 0.92, 0.88, 1.0),
    ),
    "matte_black_jewel": _Palette(
        case=(0.06, 0.06, 0.07, 1.0), frame=(0.20, 0.20, 0.22, 1.0),
        pans=_JEWEL_PANS, accent=_SILVER, mirror=_MIRROR, label=(0.85, 0.85, 0.87, 1.0),
    ),
    "clear_acrylic_pastel": _Palette(
        case=(0.86, 0.90, 0.93, 0.55), frame=_SILVER, pans=_PASTEL_PANS,
        accent=_SILVER, mirror=_MIRROR, label=_LABEL,
    ),
    "warm_brass_cream": _Palette(
        case=(0.94, 0.90, 0.82, 1.0), frame=_BRASS, pans=_WARM_PANS,
        accent=_BRASS, mirror=_MIRROR, label=(0.96, 0.94, 0.88, 1.0),
    ),
    "glossy_ivory_gold": _Palette(
        case=(0.96, 0.86, 0.74, 1.0), frame=_GOLD, pans=_IVORY_PANS,
        accent=_GOLD, mirror=_MIRROR, label=(0.97, 0.93, 0.85, 1.0),
    ),
    "pearl_blush_silver": _Palette(
        case=(0.95, 0.84, 0.82, 1.0), frame=_SILVER, pans=_PASTEL_PANS,
        accent=_SILVER, mirror=_MIRROR, label=(0.97, 0.92, 0.92, 1.0),
    ),
    "marble_white_rosegold": _Palette(
        case=(0.93, 0.92, 0.90, 1.0), frame=_ROSE_GOLD, pans=_NUDE_PANS,
        accent=_ROSE_GOLD, mirror=_MIRROR, label=(0.97, 0.96, 0.95, 1.0),
    ),
    "frosted_mint_silver": _Palette(
        case=(0.80, 0.90, 0.85, 0.60), frame=_SILVER, pans=_PASTEL_PANS,
        accent=_SILVER, mirror=_MIRROR, label=_LABEL,
    ),
    "graphite_silver_metal": _Palette(
        case=(0.32, 0.33, 0.36, 1.0), frame=_BRIGHT_SILVER, pans=_NEUTRAL_PANS,
        accent=_BRIGHT_SILVER, mirror=_MIRROR, label=(0.88, 0.89, 0.91, 1.0),
    ),
}

# ---------------------------------------------------------------------------
# Master dimensions (closed pose). Scaled per-build by resolve_config.
# ---------------------------------------------------------------------------
_RECT_LEN_X = 0.130
_RECT_DEP_Y = 0.060
_SQUARE_LEN = 0.078
_DISC_RADIUS = 0.040
_BASE_H = 0.009     # base tray thickness
_LID_H = 0.006      # lid slab thickness
_WALL = 0.004       # outer wall thickness of the base tray
_FLOOR_TOP = 0.0025  # z of tray interior floor
_SLAB_WELL_TOP = -_LID_H / 2.0 + 0.002

# Egg-crate cell params.
_PAN_DEPTH = 0.0058
_PAN_CLEAR = 0.0006
_CELL_BORDER = 0.002
_CELL_POCKET_FLOOR = 0.0008
_CELL_RECESS = 0.0006  # how far the pan top sits below the cell-grid rim
_PAN_FLOOR_BITE = 0.0004  # how far the pan bottom dips into the pocket-floor solid

# Drawer shell params.
_SHELL_H = 0.018
_CORNER_R = 0.006
_SHELL_WALL_T = 0.002
_SHELL_WALL_S = 0.002
_SHELL_WALL_B = 0.003
_TRAY_H = 0.010
_CAP_TH = 0.003
_SLIDE_UPPER = 0.080

# Clasp params.
_CLASP_W = 0.016
_CLASP_ARM_H = 0.008
_CLASP_ARM_TH = 0.002
_CLASP_HOOK_LEN = 0.005
_CLASP_HOOK_TH = 0.002
_LID_LIP_W = 0.018
_LID_LIP_DEPTH = 0.003
_LID_LIP_H = 0.003


@dataclass(frozen=True)
class ContainerCosmeticConfig:
    case_footprint: CaseFootprint = "rounded_rect"
    closure_mechanism: ClosureMechanism = "rear_hinge_flip_lid"
    pan_count: int = 8
    palette_style: PaletteStyle = "classic_skin_silver"
    case_length_scale: float = 1.0
    case_depth_scale: float = 1.0
    case_height_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_cosmetic"


@dataclass(frozen=True)
class ResolvedContainerCosmeticConfig:
    case_footprint: CaseFootprint
    closure_mechanism: ClosureMechanism
    pan_count: int
    palette_style: PaletteStyle
    case_length_scale: float
    case_depth_scale: float
    case_height_scale: float
    joint_travel_scale: float
    # derived footprint geometry
    is_round: bool
    len_x: float
    dep_y: float
    radius: float
    base_h: float
    lid_h: float
    shell_h: float
    # derived pan layout (rect: rows x cols; round: rings)
    pan_rows: int
    pan_cols: int
    ring_counts: tuple[int, ...]  # round only: pans per ring (outer..inner)
    ring_radii: tuple[float, ...]
    ring_angle_offsets: tuple[float, ...]
    pan_sx: float
    pan_sy: float
    pan_radius: float
    pan_depth: float
    grid_cy: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Pan-count -> layout factorization
# ---------------------------------------------------------------------------
def _factor_grid(n: int, aspect: float) -> tuple[int, int]:
    """Factor N into (rows, cols) closest to the desired cols/rows aspect ratio.

    aspect ~= len_x / dep_y (cols-per-row preference). Picks the (rows, cols)
    whose grid is >= N with minimal waste and aspect close to target.
    """
    best: tuple[int, int] | None = None
    best_score = None
    for rows in range(1, n + 1):
        cols = math.ceil(n / rows)
        if rows * cols < n:
            continue
        waste = rows * cols - n
        # Penalize deviation from target aspect and grid waste.
        grid_aspect = cols / rows
        score = abs(math.log(grid_aspect / aspect)) + 0.6 * waste
        if best_score is None or score < best_score:
            best_score = score
            best = (rows, cols)
    assert best is not None
    return best


def _ring_layout(n: int) -> tuple[int, ...]:
    """Lay N circular pans out on one ring (N<=8) or two rings (N>8)."""
    if n <= 8:
        return (n,)
    # Two rings: more pans on the outer ring.
    outer_n = math.ceil(n * 0.62)
    inner_n = n - outer_n
    return (outer_n, inner_n)


def _round_layout_centers(
    ring_counts: tuple[int, ...],
    ring_radii: tuple[float, ...],
    ring_angle_offsets: tuple[float, ...],
) -> list[tuple[float, float]]:
    centers: list[tuple[float, float]] = []
    for count, ring_r, angle_offset in zip(
        ring_counts, ring_radii, ring_angle_offsets, strict=True
    ):
        if count <= 0:
            continue
        step = 2.0 * math.pi / count
        for idx in range(count):
            angle = angle_offset + idx * step
            centers.append((ring_r * math.cos(angle), ring_r * math.sin(angle)))
    return centers


def _max_round_pan_radius(
    inner_r: float,
    ring_counts: tuple[int, ...],
    ring_radii: tuple[float, ...],
    ring_angle_offsets: tuple[float, ...],
) -> float:
    """Largest pan radius that keeps every round pan inside the tray and
    separated from every other pan by a visible gap."""
    if not ring_counts:
        return 0.0

    pocket_margin = _PAN_CLEAR + 0.0005
    boundary_limit = min(
        inner_r - ring_r - pocket_margin for ring_r in ring_radii
    )
    if boundary_limit <= 0.0:
        return 0.0

    centers = _round_layout_centers(ring_counts, ring_radii, ring_angle_offsets)
    spacing_limit = boundary_limit
    if len(centers) > 1:
        min_center_dist = min(
            math.hypot(ax - bx, ay - by)
            for i, (ax, ay) in enumerate(centers)
            for (bx, by) in centers[i + 1 :]
        )
        spacing_limit = min(
            spacing_limit,
            (min_center_dist - 2.0 * _PAN_CLEAR) / 2.0,
        )
    return max(min(spacing_limit, 0.009), 0.0)


def _solve_round_layout(
    ring_counts: tuple[int, ...],
    inner_r: float,
) -> tuple[tuple[float, ...], tuple[float, ...], float]:
    """Pick ring radii + angular offsets that maximize non-overlapping pan size."""
    if len(ring_counts) == 1:
        best: tuple[float, tuple[float, ...], tuple[float, ...]] | None = None
        count = ring_counts[0]
        for step in range(12):
            frac = 0.38 + 0.025 * step
            ring_r = inner_r * frac
            ring_radii = (ring_r,)
            ring_angle_offsets = (0.0,)
            pan_radius = _max_round_pan_radius(
                inner_r, ring_counts, ring_radii, ring_angle_offsets
            )
            candidate = (pan_radius, ring_radii, ring_angle_offsets)
            if best is None or candidate[0] > best[0]:
                best = candidate
        if best is None:
            fallback_r = inner_r * 0.52
            return (fallback_r,), (0.0,), max(
                0.0028,
                _max_round_pan_radius(
                    inner_r, ring_counts, (fallback_r,), (0.0,)
                ),
            )
        pan_radius, ring_radii, ring_angle_offsets = best
        return ring_radii, ring_angle_offsets, max(pan_radius, 0.0028 if count <= 4 else 0.0025)

    best: tuple[float, tuple[float, ...], tuple[float, ...], float] | None = None
    outer_n, inner_n = ring_counts
    outer_step = 2.0 * math.pi / max(outer_n, 1)
    for outer_idx in range(13):
        outer_frac = 0.48 + 0.02 * outer_idx
        outer_r = inner_r * outer_frac
        for inner_idx in range(13):
            inner_frac = 0.16 + 0.02 * inner_idx
            inner_r2 = inner_r * inner_frac
            if inner_r2 >= outer_r - 0.004:
                continue
            for offset_idx in range(24):
                offset = offset_idx * (outer_step / 12.0)
                ring_radii = (outer_r, inner_r2)
                ring_angle_offsets = (0.0, offset)
                pan_radius = _max_round_pan_radius(
                    inner_r, ring_counts, ring_radii, ring_angle_offsets
                )
                balance_penalty = abs((outer_r / max(inner_r, 1e-6)) - 0.60) + abs(
                    (inner_r2 / max(inner_r, 1e-6)) - 0.28
                )
                candidate = (pan_radius, ring_radii, ring_angle_offsets, -balance_penalty)
                if best is None or candidate > best:
                    best = candidate

    if best is None:
        ring_radii = (inner_r * 0.58, inner_r * 0.26)
        ring_angle_offsets = (0.0, math.pi / max(inner_n, 1))
        pan_radius = _max_round_pan_radius(
            inner_r, ring_counts, ring_radii, ring_angle_offsets
        )
        return ring_radii, ring_angle_offsets, max(pan_radius, 0.0022)

    pan_radius, ring_radii, ring_angle_offsets, _ = best
    return ring_radii, ring_angle_offsets, max(pan_radius, 0.0022)


def _derive_pan_depth(base_h: float) -> float:
    """Pan body height that fits between the pocket floor and the recessed rim.

    The pan bottom dips ~0.4mm into the pocket-floor solid (so the pan is a
    connected island of the tray, not floating) and its top sits below the cell
    rim (= base_h) by ``_CELL_RECESS``. When the base is scaled down, the pan
    shrinks instead of poking through the rim.
    """
    pocket_floor = _FLOOR_TOP + _CELL_POCKET_FLOOR
    avail = (base_h - _CELL_RECESS) - (pocket_floor - _PAN_FLOOR_BITE)
    return _clamp(min(_PAN_DEPTH, avail), 0.0022, _PAN_DEPTH)


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerCosmeticConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    footprint = rng.choice(CASE_FOOTPRINTS)
    closure = rng.choice(CLOSURE_MECHANISMS)
    pan_count = rng.choices(_PAN_COUNT_VALUES, weights=_PAN_COUNT_W, k=1)[0]
    length_scale = round(rng.uniform(0.85, 1.20), 4)
    depth_scale = round(rng.uniform(0.90, 1.15), 4)
    return ContainerCosmeticConfig(
        case_footprint=footprint,
        closure_mechanism=closure,
        pan_count=pan_count,
        palette_style=rng.choice(PALETTE_STYLES),
        case_length_scale=length_scale,
        case_depth_scale=depth_scale,
        case_height_scale=round(rng.uniform(0.85, 1.15), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_cosmetic_{seed}",
    )


def resolve_config(
    config: ContainerCosmeticConfig | None = None,
) -> ResolvedContainerCosmeticConfig:
    cfg = config or ContainerCosmeticConfig()
    footprint = _pick(cfg.case_footprint, CASE_FOOTPRINTS)
    closure = _pick(cfg.closure_mechanism, CLOSURE_MECHANISMS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)
    is_round = footprint == "round_disc"

    n = int(_clamp(cfg.pan_count, 2, 24))

    l_scale = _clamp(cfg.case_length_scale, 0.85, 1.20)
    d_scale = _clamp(cfg.case_depth_scale, 0.90, 1.15)
    h_scale = _clamp(cfg.case_height_scale, 0.85, 1.15)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.10)

    base_h = _BASE_H * h_scale
    lid_h = _LID_H * h_scale
    shell_h = _SHELL_H * h_scale

    if is_round:
        # case_depth_scale locked = case_length_scale to keep the disc round.
        d_scale = l_scale
        radius = _DISC_RADIUS * l_scale
        len_x = 2.0 * radius
        dep_y = 2.0 * radius
        inner_r = radius - _WALL
        ring_counts = _ring_layout(n)
        ring_radii, ring_angle_offsets, pan_radius = _solve_round_layout(ring_counts, inner_r)
        return ResolvedContainerCosmeticConfig(
            case_footprint=footprint,
            closure_mechanism=closure,
            pan_count=n,
            palette_style=palette,
            case_length_scale=l_scale,
            case_depth_scale=d_scale,
            case_height_scale=h_scale,
            joint_travel_scale=jt_scale,
            is_round=True,
            len_x=len_x,
            dep_y=dep_y,
            radius=radius,
            base_h=base_h,
            lid_h=lid_h,
            shell_h=shell_h,
            pan_rows=0,
            pan_cols=0,
            ring_counts=ring_counts,
            ring_radii=ring_radii,
            ring_angle_offsets=ring_angle_offsets,
            pan_sx=2.0 * pan_radius,
            pan_sy=2.0 * pan_radius,
            pan_radius=pan_radius,
            pan_depth=_derive_pan_depth(base_h),
            grid_cy=0.0,
            name=cfg.name or "container_cosmetic",
        )

    # Rectangular footprints.
    if footprint == "square_rounded":
        len_x = _SQUARE_LEN * l_scale
        dep_y = _SQUARE_LEN * d_scale
    else:
        len_x = _RECT_LEN_X * l_scale
        dep_y = _RECT_DEP_Y * d_scale

    aspect = max(len_x / dep_y, 0.2)
    rows, cols = _factor_grid(n, aspect)

    # Available interior region for the pan grid (leave wall + rear label band).
    inner_len = len_x - 2.0 * _WALL - 0.004
    label_band = 0.010
    inner_depth = dep_y - 2.0 * _WALL - label_band
    grid_cy = -(label_band * 0.5)

    # Derive pan size so rows/cols fit with a small gap (pan_size equation).
    gap = 0.0035
    pan_sx = (inner_len - (cols - 1) * gap) / cols
    pan_sy = (inner_depth - (rows - 1) * gap) / rows
    # Keep pans tractable; clamp to a reasonable minimum so the mesh is valid.
    pan_sx = _clamp(pan_sx, 0.004, 0.045)
    pan_sy = _clamp(pan_sy, 0.004, 0.040)

    return ResolvedContainerCosmeticConfig(
        case_footprint=footprint,
        closure_mechanism=closure,
        pan_count=n,
        palette_style=palette,
        case_length_scale=l_scale,
        case_depth_scale=d_scale,
        case_height_scale=h_scale,
        joint_travel_scale=jt_scale,
        is_round=False,
        len_x=len_x,
        dep_y=dep_y,
        radius=0.0,
        base_h=base_h,
        lid_h=lid_h,
        shell_h=shell_h,
        pan_rows=rows,
        pan_cols=cols,
        ring_counts=(),
        ring_radii=(),
        ring_angle_offsets=(),
        pan_sx=pan_sx,
        pan_sy=pan_sy,
        pan_radius=0.0,
        pan_depth=_derive_pan_depth(base_h),
        grid_cy=grid_cy,
        name=cfg.name or "container_cosmetic",
    )


def slot_choices_for_config(
    config: ContainerCosmeticConfig | ResolvedContainerCosmeticConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedContainerCosmeticConfig)
        else resolve_config(config)
    )
    return (
        ("case_footprint", r.case_footprint),
        ("closure_mechanism", r.closure_mechanism),
        ("pan_count", f"n{r.pan_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (shared)
# ---------------------------------------------------------------------------
def _rounded_box(sx: float, sy: float, sz: float, r: float) -> cq.Workplane:
    """Axis-aligned box centered at origin with filleted vertical (Z) edges."""
    wp = cq.Workplane("XY").box(sx, sy, sz)
    r = min(r, sx / 2.0 - 1e-4, sy / 2.0 - 1e-4)
    if r > 0:
        wp = wp.edges("|Z").fillet(r)
    return wp


def _disc(outer_r: float, height: float) -> cq.Workplane:
    """Solid cylinder centered at origin with base at z=0, top at z=height."""
    return cq.Workplane("XY").circle(outer_r).extrude(height)


def _ring(outer_r: float, inner_r: float, height: float) -> cq.Workplane:
    """Annular ring (washer) centered at origin, from z=0 to z=height."""
    return cq.Workplane("XY").circle(outer_r).circle(inner_r).extrude(height)


def _pan_centers(r: ResolvedContainerCosmeticConfig):
    """Yield (key, cx, cy) for every pan.

    Rect footprints: regular ROWS x COLS grid, ``key`` = ``f"{row}_{col}"``.
    Round footprints: one or two radial rings, ``key`` = ``str(i)``.
    """
    if r.is_round:
        idx = 0
        for ring_n, ring_r, angle_offset in zip(
            r.ring_counts, r.ring_radii, r.ring_angle_offsets, strict=True
        ):
            for k in range(ring_n):
                angle = angle_offset + k * (2.0 * math.pi / max(ring_n, 1))
                cx = ring_r * math.cos(angle)
                cy = ring_r * math.sin(angle)
                yield (str(idx), cx, cy)
                idx += 1
        return

    rows, cols = r.pan_rows, r.pan_cols
    gap = 0.0035
    grid_w = cols * r.pan_sx + (cols - 1) * gap
    grid_d = rows * r.pan_sy + (rows - 1) * gap
    x0 = -grid_w / 2.0 + r.pan_sx / 2.0
    y0 = r.grid_cy - grid_d / 2.0 + r.pan_sy / 2.0
    idx = 0
    for row in range(rows):
        for col in range(cols):
            if idx >= r.pan_count:
                return
            cx = x0 + col * (r.pan_sx + gap)
            cy = y0 + row * (r.pan_sy + gap)
            yield (f"{row}_{col}", cx, cy)
            idx += 1


def _pan_mesh(r: ResolvedContainerCosmeticConfig):
    """A single recessed concealer pan (rounded slab for rect, disc for round)."""
    pan_h = r.pan_depth
    if r.is_round:
        pan = _disc(r.pan_radius, pan_h)
        pan = pan.translate((0.0, 0.0, -pan_h / 2.0))
        return mesh_from_cadquery(pan, "pan_cream")
    pan = _rounded_box(r.pan_sx, r.pan_sy, pan_h, min(0.004, r.pan_sx * 0.2))
    return mesh_from_cadquery(pan, "pan_cream")


def _cell_grid_mesh(
    r: ResolvedContainerCosmeticConfig, *, top_z: float, bot_z: float, floor_z: float
):
    """Silver egg-crate divider: a block spanning the pans with one recessed
    pocket cut per pan (bbox-from-centers for rect; disc plate for round)."""
    centers = list(_pan_centers(r))
    block_h = top_z - bot_z
    pocket_floor = floor_z + _CELL_POCKET_FLOOR
    pocket_h = (top_z - pocket_floor) + 0.01

    if r.is_round:
        cav_r = r.radius - _WALL
        block = _disc(cav_r - 0.0005, block_h)
        block = block.translate((0.0, 0.0, bot_z))
        for (_, cx, cy) in centers:
            pocket = _disc(r.pan_radius + _PAN_CLEAR, pocket_h)
            pocket = pocket.translate((cx, cy, pocket_floor))
            block = block.cut(pocket)
        return mesh_from_cadquery(block, "cell_grid")

    xs = [cx for (_, cx, _) in centers]
    ys = [cy for (_, _, cy) in centers]
    block_cx = (min(xs) + max(xs)) / 2.0
    block_cy = (min(ys) + max(ys)) / 2.0
    block_x = (max(xs) - min(xs)) + r.pan_sx + 2.0 * _CELL_BORDER
    block_y = (max(ys) - min(ys)) + r.pan_sy + 2.0 * _CELL_BORDER
    block = _rounded_box(block_x, block_y, block_h, 0.0015)
    block = block.translate((block_cx, block_cy, bot_z + block_h / 2.0))
    for (_, cx, cy) in centers:
        pocket = _rounded_box(
            r.pan_sx + 2.0 * _PAN_CLEAR, r.pan_sy + 2.0 * _PAN_CLEAR, pocket_h, 0.0015
        )
        pocket = pocket.translate((cx, cy, pocket_floor + pocket_h / 2.0))
        block = block.cut(pocket)
    return mesh_from_cadquery(block, "cell_grid")


# ---------------------------------------------------------------------------
# Tray (ROOT) emission for flip / clasp closures (root = base, pans on base).
# ---------------------------------------------------------------------------
def _emit_base_tray(base, r: ResolvedContainerCosmeticConfig, *, mats) -> None:
    """Dark tray + silver rim frame + egg-crate cell grid + label + N pans,
    seated recessed in their cells. Used by flip / clasp closures."""
    base_h = r.base_h
    if r.is_round:
        outer = _disc(r.radius, base_h)
        cav_r = r.radius - _WALL
        cav_h = base_h - _FLOOR_TOP
        cavity = _disc(cav_r, cav_h + 0.02).translate((0.0, 0.0, _FLOOR_TOP))
        tray = outer.cut(cavity)
        base.visual(mesh_from_cadquery(tray, "base_tray"), material=mats["case"], name="base_tray", material_class_id=("plastic.clear_rigid" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "frosted_mint_silver", "graphite_silver_metal"} else "marble.generic"))
        frame = _ring(r.radius, r.radius - _WALL, 0.0018).translate((0.0, 0.0, base_h))
        base.visual(mesh_from_cadquery(frame, "base_frame"), material=mats["frame"], name="base_frame", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"))
    else:
        outer = _rounded_box(r.len_x, r.dep_y, base_h, 0.006).translate((0.0, 0.0, base_h / 2.0))
        cav_x = r.len_x - 2.0 * _WALL
        cav_y = r.dep_y - 2.0 * _WALL
        cav_h = base_h - _FLOOR_TOP
        cavity = _rounded_box(cav_x, cav_y, cav_h + 0.02, 0.004)
        cavity = cavity.translate((0.0, 0.0, _FLOOR_TOP + (cav_h + 0.02) / 2.0))
        tray = outer.cut(cavity)
        base.visual(mesh_from_cadquery(tray, "base_tray"), material=mats["case"], name="base_tray", material_class_id=("plastic.clear_rigid" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "frosted_mint_silver", "graphite_silver_metal"} else "marble.generic"))
        frame = _rounded_box(r.len_x, r.dep_y, 0.0018, 0.006)
        frame_inner = _rounded_box(r.len_x - 2.0 * _WALL, r.dep_y - 2.0 * _WALL, 0.01, 0.004)
        frame = frame.cut(frame_inner).translate((0.0, 0.0, base_h + 0.0009))
        base.visual(mesh_from_cadquery(frame, "base_frame"), material=mats["frame"], name="base_frame", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"))

    cell_top = base_h
    cell_bot = _FLOOR_TOP - 0.0005
    base.visual(
        _cell_grid_mesh(r, top_z=cell_top, bot_z=cell_bot, floor_z=_FLOOR_TOP),
        material=mats["frame"],
        name="cell_grid", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"),
    )

    # Seat the pan bottom biting into the pocket-floor solid (so each pan is a
    # connected island of the tray, never floating) while its top stays recessed
    # below the cell rim. pan_depth is derived so both hold even when base_h is
    # scaled down (the pan shrinks instead of poking above the rim).
    pocket_floor = _FLOOR_TOP + _CELL_POCKET_FLOOR
    pan_center_z = (pocket_floor - _PAN_FLOOR_BITE) + r.pan_depth / 2.0
    for (key, cx, cy) in _pan_centers(r):
        base.visual(
            _pan_mesh(r),
            origin=Origin(xyz=(cx, cy, pan_center_z)),
            material=mats["pans"][key],
            name=f"pan_{key}", material_class_id="organic.wax",
        )

    base.inertial = Inertial.from_geometry(
        Box((r.len_x, r.dep_y, base_h)),
        mass=0.08,
        origin=Origin(xyz=(0.0, 0.0, base_h / 2.0)),
    )


def _pan_color_index(key: str, r: ResolvedContainerCosmeticConfig) -> int:
    """Stable color index from the pan key so adjacent pans differ."""
    if "_" in key:
        row, col = key.split("_")
        idx = int(row) * max(r.pan_cols, 1) + int(col)
    else:
        idx = int(key)
    return idx


def _clamp_channel(value: float) -> float:
    return _clamp(value, 0.0, 1.0)


def _mix_rgb(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    amount: float,
) -> tuple[float, float, float]:
    t = _clamp(amount, 0.0, 1.0)
    return (
        a[0] * (1.0 - t) + b[0] * t,
        a[1] * (1.0 - t) + b[1] * t,
        a[2] * (1.0 - t) + b[2] * t,
    )


def _pan_shade_rgba(
    key: str,
    r: ResolvedContainerCosmeticConfig,
    base_colors: list[tuple[float, float, float, float]],
) -> tuple[float, float, float, float]:
    """Derive a per-pan cosmetic shade so foundation pans do not look identical."""
    idx = _pan_color_index(key, r)
    base = base_colors[idx % max(len(base_colors), 1)]
    total = max(r.pan_count, 1)

    # Golden-ratio stepping keeps adjacent pans from marching through nearly the
    # same shade, while staying deterministic for a given layout.
    shade_rank = (idx * 0.61803398875) % 1.0 if total > 1 else 0.35
    rgb = (base[0], base[1], base[2])
    if shade_rank < 0.5:
        rgb = _mix_rgb(rgb, (0.98, 0.88, 0.74), (0.5 - shade_rank) * 0.34)
    else:
        rgb = _mix_rgb(rgb, (0.42, 0.24, 0.14), (shade_rank - 0.5) * 0.52)

    warmth = ((idx % 4) - 1.5) * 0.025
    peach = (((idx // 2) % 3) - 1.0) * 0.018
    return (
        _clamp_channel(rgb[0] + warmth + peach),
        _clamp_channel(rgb[1] + peach * 0.45),
        _clamp_channel(rgb[2] - warmth * 0.55),
        base[3],
    )


# ---------------------------------------------------------------------------
# Slot B: rear_hinge_flip_lid  (and the shared lid body for clasp)
# ---------------------------------------------------------------------------
def _lid_slab_mesh(r: ResolvedContainerCosmeticConfig):
    if r.is_round:
        slab = _disc(r.radius, r.lid_h).translate((0.0, 0.0, -r.lid_h / 2.0))
        well_r = r.radius - _WALL
        well_h = (_SLAB_WELL_TOP - (-r.lid_h / 2.0)) + 0.01
        well = _disc(well_r, well_h).translate((0.0, 0.0, _SLAB_WELL_TOP - well_h))
        slab = slab.cut(well)
        return mesh_from_cadquery(slab, "lid_slab")
    slab = _rounded_box(r.len_x, r.dep_y, r.lid_h, 0.006)
    well_h = (_SLAB_WELL_TOP - (-r.lid_h / 2.0)) + 0.01
    well = _rounded_box(r.len_x - 2.0 * _WALL, r.dep_y - 2.0 * _WALL, well_h, 0.004)
    well = well.translate((0.0, 0.0, _SLAB_WELL_TOP - well_h / 2.0))
    slab = slab.cut(well)
    return mesh_from_cadquery(slab, "lid_slab")


def _emit_flip_lid(model, base, r: ResolvedContainerCosmeticConfig, *, mats, with_clasp: bool):
    """REVOLUTE -X rear-hinge flip lid; mirror on the lid inner well. The lid
    part frame origin sits on the rear hinge line."""
    base_h = r.base_h
    hinge_y = (r.radius if r.is_round else r.dep_y / 2.0)
    hinge_z = base_h + r.lid_h / 2.0
    open_upper = math.radians(110.0) * r.joint_travel_scale

    # Hinge knuckles grounded on the base near the rear edge. For the round disc
    # the rear rim is a thin ring, so anchor each knuckle slightly inward (over
    # the solid rim band) and bridge it down to the tray top with a small post so
    # the knuckle is a connected island of the base, never a floating cylinder.
    knuckle_r = 0.0022
    hinge_y_anchor = (r.radius - _WALL * 0.5) if r.is_round else hinge_y
    post_top = hinge_z - knuckle_r + 0.0005  # embed slightly into the knuckle
    post_h = max(post_top - base_h, 0.0) + 0.0008  # bridge from below the tray top
    hx_off = min(0.030, (r.len_x / 2.0) * 0.5)
    for i, hx in enumerate((-hx_off, hx_off)):
        geom = CylinderGeometry(knuckle_r, 0.016, radial_segments=24).rotate_y(math.pi / 2.0)
        geom.translate(hx, hinge_y_anchor, hinge_z)
        if post_h > 0.0:
            post = _rounded_box(0.018, 0.0035, post_h, 0.0008)
            post = post.translate((hx, hinge_y_anchor, base_h - 0.0008 + post_h / 2.0))
            base.visual(
                mesh_from_cadquery(post, f"hinge_post_{i}"),
                material=mats["frame"],
                name=f"hinge_post_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"),
            )
        base.visual(
            mesh_from_geometry(geom, f"hinge_knuckle_{i}"),
            material=mats["frame"],
            name=f"hinge_knuckle_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"),
        )

    lid = model.part("lid")
    lid_y = -(r.radius if r.is_round else r.dep_y / 2.0)
    lid_z = r.lid_h / 2.0
    lid.visual(_lid_slab_mesh(r), origin=Origin(xyz=(0.0, lid_y, lid_z)), material=mats["case"], name="lid_slab", material_class_id=("plastic.clear_rigid" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "frosted_mint_silver", "graphite_silver_metal"} else "marble.generic"))

    # Add lid-side hinge geometry so the lid reads as physically attached to the
    # rear hinge axis instead of hovering around it.
    lid_barrel_len = max(0.012, 2.0 * hx_off - 0.018)
    lid_barrel = CylinderGeometry(knuckle_r * 0.92, lid_barrel_len, radial_segments=24).rotate_y(math.pi / 2.0)
    lid.visual(
        mesh_from_geometry(lid_barrel, "lid_hinge_barrel"),
        material=mats["frame"],
        name="lid_hinge_barrel", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"),
    )
    strap_depth = min(0.010, (r.radius if r.is_round else r.dep_y / 2.0) * 0.22)
    strap = _rounded_box(max(lid_barrel_len - 0.004, 0.008), strap_depth, 0.0022, 0.0005)
    strap = strap.translate((0.0, -strap_depth / 2.0 - 0.0008, 0.0011))
    lid.visual(
        mesh_from_cadquery(strap, "lid_hinge_strap"),
        material=mats["frame"],
        name="lid_hinge_strap", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"),
    )

    if r.is_round:
        lid_frame = _ring(r.radius, r.radius - _WALL, 0.0018).translate((0.0, lid_y, r.lid_h - 0.0009))
    else:
        lid_frame = _rounded_box(r.len_x, r.dep_y, 0.0018, 0.006)
        lid_frame_inner = _rounded_box(r.len_x - 2.0 * _WALL, r.dep_y - 2.0 * _WALL, 0.01, 0.004)
        lid_frame = lid_frame.cut(lid_frame_inner).translate((0.0, lid_y, r.lid_h - 0.0009 + 1e-4))
    lid.visual(mesh_from_cadquery(lid_frame, "lid_frame"), material=mats["frame"], name="lid_frame", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"))

    # Mirror on the inner (-Z) face of the lid.
    mirror_th = 0.0020
    well_floor_z = lid_z + _SLAB_WELL_TOP
    if r.is_round:
        mirror = _disc(r.radius - _WALL - 0.002, mirror_th)
        mirror = mirror.translate((0.0, lid_y, well_floor_z - mirror_th + 0.0006))
    else:
        mirror = _rounded_box(r.len_x - 2.0 * _WALL - 0.001, r.dep_y - 2.0 * _WALL - 0.001, mirror_th, 0.003)
        mirror = mirror.translate((0.0, lid_y, well_floor_z - mirror_th / 2.0 + 0.0006))
    lid.visual(mesh_from_cadquery(mirror, "mirror"), material=mats["mirror"], name="mirror", material_class_id="glass.mirror")

    if with_clasp:
        # Catch lip on the lid front-top edge for the clasp hook.
        lip_cy = lid_y - r.dep_y / 2.0 + _LID_LIP_DEPTH / 2.0 + 0.001
        lip_cz = r.lid_h + _LID_LIP_H / 2.0
        lip = _rounded_box(_LID_LIP_W, _LID_LIP_DEPTH, _LID_LIP_H, 0.0006)
        lip = lip.translate((0.0, lip_cy, lip_cz))
        lid.visual(mesh_from_cadquery(lip, "lid_lip"), material=mats["frame"], name="lid_lip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"))

    lid.inertial = Inertial.from_geometry(
        Box((r.len_x, r.dep_y, r.lid_h)), mass=0.04, origin=Origin(xyz=(0.0, lid_y, 0.0))
    )

    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=0.0, upper=open_upper),
    )
    return lid


def _emit_clasp(model, base, lid, r: ResolvedContainerCosmeticConfig, *, mats):
    """REVOLUTE +X front-edge clasp lever that catches the lid lip when latched."""
    base_h = r.base_h
    clasp_pivot_y = -(r.radius if r.is_round else r.dep_y / 2.0)
    clasp_pivot_z = base_h + 0.003
    unlatch_upper = math.radians(85.0) * r.joint_travel_scale

    # Clasp-mount bosses on the base front edge.
    boss_offset = _CLASP_W / 2.0 + 0.005 / 2.0 + 0.001
    for i, bx in enumerate((-boss_offset, boss_offset)):
        boss = CylinderGeometry(0.0020, 0.005, radial_segments=16).rotate_y(math.pi / 2.0)
        boss = boss.translate(bx, clasp_pivot_y, clasp_pivot_z)
        base.visual(mesh_from_geometry(boss, f"clasp_boss_{i}"), material=mats["frame"], name=f"clasp_boss_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"))

    clasp = model.part("clasp")
    # Lever mesh built in the clasp frame (origin at pivot, arm up +Z, hook +Y).
    arm = _rounded_box(_CLASP_W, _CLASP_ARM_TH, _CLASP_ARM_H, 0.0006)
    arm = arm.translate((0.0, -_CLASP_ARM_TH / 2.0, _CLASP_ARM_H / 2.0))
    barrel_r = 0.0015
    barrel = cq.Workplane("YZ").circle(barrel_r).extrude(_CLASP_W + 0.002)
    barrel = barrel.translate((-(_CLASP_W + 0.002) / 2.0, 0.0, 0.0))
    hook = _rounded_box(_CLASP_W - 0.002, _CLASP_HOOK_LEN, _CLASP_HOOK_TH, 0.0004)
    hook = hook.translate((0.0, _CLASP_HOOK_LEN / 2.0, _CLASP_ARM_H - _CLASP_HOOK_TH / 2.0))
    btn = _rounded_box(0.008, 0.003, 0.004, 0.001)
    btn = btn.translate((0.0, -_CLASP_ARM_TH - 0.003 / 2.0, _CLASP_ARM_H * 0.38))
    lever = arm.union(barrel).union(hook).union(btn)
    clasp.visual(mesh_from_cadquery(lever, "clasp_lever"), material=mats["accent"], name="clasp_lever", material_class_id=("metal.chrome_polished" if r.palette_style in {"rose_gold_nude", "warm_brass_cream", "glossy_ivory_gold", "marble_white_rosegold", "graphite_silver_metal"} else "metal.brushed_silver"))
    clasp.inertial = Inertial.from_geometry(
        Box((_CLASP_W, _CLASP_ARM_TH + _CLASP_HOOK_LEN, _CLASP_ARM_H)),
        mass=0.008,
        origin=Origin(xyz=(0.0, 0.0, _CLASP_ARM_H / 2.0)),
    )

    model.articulation(
        "base_to_clasp",
        ArticulationType.REVOLUTE,
        parent=base,
        child=clasp,
        origin=Origin(xyz=(0.0, clasp_pivot_y, clasp_pivot_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.5, velocity=4.0, lower=0.0, upper=unlatch_upper),
    )
    return clasp


# ---------------------------------------------------------------------------
# Slot B: slide_out_drawer  (root = shell sleeve, pans on the drawer)
# ---------------------------------------------------------------------------
def _emit_drawer_closure(model, r: ResolvedContainerCosmeticConfig, *, mats):
    """Hollow rounded-rect (or round) shell sleeve open on +X + a PRISMATIC +X
    drawer carrying the pans. Mirror rides the shell interior ceiling."""
    shell_h = r.shell_h
    len_x = r.len_x
    dep_y = r.dep_y

    shell = model.part("shell")
    # Five-plate hollow sleeve (genuinely empty cavity), open on +X.
    bot = _rounded_box(len_x, dep_y, _SHELL_WALL_T, _CORNER_R)
    bot = bot.translate((0.0, 0.0, -shell_h / 2.0 + _SHELL_WALL_T / 2.0))
    top = _rounded_box(len_x, dep_y, _SHELL_WALL_T, _CORNER_R)
    top = top.translate((0.0, 0.0, shell_h / 2.0 - _SHELL_WALL_T / 2.0))
    wall_h = shell_h - 2.0 * _SHELL_WALL_T + 0.001
    lwall = cq.Workplane("XY").box(len_x, _SHELL_WALL_S, wall_h)
    lwall = lwall.translate((0.0, -dep_y / 2.0 + _SHELL_WALL_S / 2.0, 0.0))
    rwall = cq.Workplane("XY").box(len_x, _SHELL_WALL_S, wall_h)
    rwall = rwall.translate((0.0, dep_y / 2.0 - _SHELL_WALL_S / 2.0, 0.0))
    bwall = cq.Workplane("XY").box(_SHELL_WALL_B, dep_y - _SHELL_WALL_S, wall_h)
    bwall = bwall.translate((-len_x / 2.0 + _SHELL_WALL_B / 2.0, 0.0, 0.0))
    body = bot.union(top).union(lwall).union(rwall).union(bwall)
    shell.visual(mesh_from_cadquery(body, "shell_body"), material=mats["case"], name="shell_body", material_class_id=("plastic.clear_rigid" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "frosted_mint_silver", "graphite_silver_metal"} else "marble.generic"))

    # Silver frame on the shell top.
    frame_h = 0.0012
    outer = _rounded_box(len_x - 0.001, dep_y - 0.001, frame_h, _CORNER_R)
    inner = cq.Workplane("XY").box(len_x - 2.0 * _SHELL_WALL_S - 0.004, dep_y - 2.0 * _SHELL_WALL_S - 0.004, frame_h + 0.010)
    frame = outer.cut(inner).translate((0.0, 0.0, shell_h / 2.0 + frame_h / 2.0 - 0.0003))
    shell.visual(mesh_from_cadquery(frame, "shell_frame"), material=mats["frame"], name="shell_frame", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"))

    # Label strip on the shell top.
    label = _rounded_box(0.040, 0.010, 0.0008, 0.003)
    label = label.translate((-0.020, 0.0, shell_h / 2.0 + 0.0008 / 2.0 - 0.0003))
    shell.visual(mesh_from_cadquery(label, "label_strip"), material=mats["label"], name="label_strip", appearance_only=AppearanceOnlySpec(kind="decal"))

    # Mirror on the interior ceiling.
    cav_y = dep_y - 2.0 * _SHELL_WALL_S
    mirror = _rounded_box(min(0.080, len_x * 0.62), cav_y - 0.006, 0.0015, 0.003)
    mirror_z = shell_h / 2.0 - _SHELL_WALL_T - 0.0015 / 2.0 + 0.0005
    mirror = mirror.translate((0.0, 0.0, mirror_z))
    shell.visual(mesh_from_cadquery(mirror, "mirror"), material=mats["mirror"], name="mirror", material_class_id="glass.mirror")

    shell.inertial = Inertial.from_geometry(
        Box((len_x, dep_y, shell_h)), mass=0.06, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )

    # --- Drawer ---
    tray_z_center = -shell_h / 2.0 + _SHELL_WALL_T + _TRAY_H / 2.0
    tray_top_z = tray_z_center + _TRAY_H / 2.0
    cap_front_x = len_x / 2.0
    cap_back_x = cap_front_x - _CAP_TH
    tray_len = len_x - _SHELL_WALL_B - _CAP_TH - 0.004
    tray_wid = dep_y - 2.0 * _SHELL_WALL_S - 0.003
    tray_front_x = cap_back_x
    tray_back_x = tray_front_x - tray_len
    tray_center_x = (tray_front_x + tray_back_x) / 2.0
    cap_wid = dep_y - 2.0 * _SHELL_WALL_S + 0.001
    cap_hgt = shell_h - 2.0 * _SHELL_WALL_T

    drawer = model.part("drawer")
    tray = _rounded_box(tray_len, tray_wid, _TRAY_H, 0.003).translate((tray_center_x, 0.0, tray_z_center))
    overlap = 0.001
    cap_len = _CAP_TH + overlap
    cap = _rounded_box(cap_len, cap_wid, cap_hgt, 0.001).translate((cap_front_x - cap_len / 2.0, 0.0, 0.0))
    drawer_body = tray.union(cap)
    drawer.visual(mesh_from_cadquery(drawer_body, "drawer_body"), material=mats["case"], name="drawer_body", material_class_id=("plastic.clear_rigid" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "frosted_mint_silver", "graphite_silver_metal"} else "marble.generic"))

    # Silver pull-grip accent on the front cap.
    grip = _rounded_box(0.0008, 0.025, 0.003, 0.001).translate((cap_front_x + 0.0008 / 2.0, 0.0, 0.002))
    drawer.visual(mesh_from_cadquery(grip, "grip_accent"), material=mats["frame"], name="grip_accent", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"))

    # Build drawer-local pan layout: reuse the rect/round centers but recenter on
    # the tray, then emit cell grid + pans onto the drawer.
    cell_top = tray_top_z + 0.0015
    cell_bot = tray_top_z - 0.002
    drawer.visual(
        _drawer_cell_grid_mesh(r, tray_center_x, cell_top, cell_bot, tray_top_z),
        material=mats["frame"],
        name="cell_grid", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"classic_skin_silver", "rose_gold_nude", "matte_black_jewel", "clear_acrylic_pastel", "warm_brass_cream", "glossy_ivory_gold", "pearl_blush_silver", "marble_white_rosegold", "frosted_mint_silver"} else "metal.chrome_polished"),
    )
    pan_z_center = tray_top_z - r.pan_depth / 2.0
    for (key, cx, cy) in _pan_centers(r):
        drawer.visual(
            _pan_mesh(r),
            origin=Origin(xyz=(cx + tray_center_x, cy, pan_z_center)),
            material=mats["pans"][key],
            name=f"pan_{key}", material_class_id="organic.wax",
        )

    drawer.inertial = Inertial.from_geometry(
        Box((tray_len + _CAP_TH, tray_wid, _TRAY_H)),
        mass=0.05,
        origin=Origin(xyz=(tray_center_x, 0.0, tray_z_center)),
    )

    model.articulation(
        "shell_to_drawer",
        ArticulationType.PRISMATIC,
        parent=shell,
        child=drawer,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=5.0, velocity=0.30, lower=0.0, upper=_SLIDE_UPPER * r.joint_travel_scale
        ),
    )
    return shell, drawer


def _drawer_cell_grid_mesh(r, tray_center_x, top_z, bot_z, tray_top_z):
    """Egg-crate cell grid riding on the drawer tray (centers recentered on tray)."""
    centers = list(_pan_centers(r))
    block_h = top_z - bot_z
    pocket_h = block_h + 0.01
    if r.is_round:
        block = _disc((r.radius - _WALL) - 0.0005, block_h).translate((tray_center_x, 0.0, bot_z))
        for (_, cx, cy) in centers:
            pocket = _disc(r.pan_radius + _PAN_CLEAR, pocket_h)
            pocket = pocket.translate((cx + tray_center_x, cy, bot_z + block_h / 2.0))
            block = block.cut(pocket)
        return mesh_from_cadquery(block, "cell_grid")
    xs = [cx for (_, cx, _) in centers]
    ys = [cy for (_, _, cy) in centers]
    block_cx = (min(xs) + max(xs)) / 2.0 + tray_center_x
    block_cy = (min(ys) + max(ys)) / 2.0
    block_x = (max(xs) - min(xs)) + r.pan_sx + 2.0 * _CELL_BORDER
    block_y = (max(ys) - min(ys)) + r.pan_sy + 2.0 * _CELL_BORDER
    block = _rounded_box(block_x, block_y, block_h, 0.0015)
    block = block.translate((block_cx, block_cy, bot_z + block_h / 2.0))
    for (_, cx, cy) in centers:
        pocket = _rounded_box(r.pan_sx + 2.0 * _PAN_CLEAR, r.pan_sy + 2.0 * _PAN_CLEAR, pocket_h, 0.0015)
        pocket = pocket.translate((cx + tray_center_x, cy, bot_z + block_h / 2.0))
        block = block.cut(pocket)
    return mesh_from_cadquery(block, "cell_grid")


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_cosmetic(
    config: ContainerCosmeticConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    pan_mats = {
        key: model.material(
            f"cc_pan_{r.palette_style}_{_pan_color_index(key, r)}",
            rgba=_pan_shade_rgba(key, r, pal.pans),
        )
        for key, _, _ in _pan_centers(r)
    }
    mats = {
        "case": model.material(f"cc_case_{r.palette_style}", rgba=pal.case),
        "frame": model.material(f"cc_frame_{r.palette_style}", rgba=pal.frame),
        "accent": model.material(f"cc_accent_{r.palette_style}", rgba=pal.accent),
        "mirror": model.material(f"cc_mirror_{r.palette_style}", rgba=pal.mirror),
        "label": model.material(f"cc_label_{r.palette_style}", rgba=pal.label),
        "pans": pan_mats,
    }

    if r.closure_mechanism == "slide_out_drawer":
        _emit_drawer_closure(model, r, mats=mats)
    else:
        base = model.part("base")
        _emit_base_tray(base, r, mats=mats)
        lid = _emit_flip_lid(
            model, base, r, mats=mats,
            with_clasp=(r.closure_mechanism == "flip_lid_with_clasp"),
        )
        if r.closure_mechanism == "flip_lid_with_clasp":
            _emit_clasp(model, base, lid, r, mats=mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_cosmetic(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_cosmetic(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (lid frame on base rim, drawer in sleeve,
# cell grid in sleeve, clasp hook over lid lip) are declared so the sweep's
# overlap checks pass; the mechanism actions are exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_cosmetic_tests(
    object_model: ArticulatedObject,
    config: ContainerCosmeticConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    pan_keys = [key for (key, _, _) in _pan_centers(r)]

    # ---- N pans authored, recessed in their cells ----
    if r.closure_mechanism == "slide_out_drawer":
        holder = object_model.get_part("drawer")
        body_elem = "drawer_body"
    else:
        holder = object_model.get_part("base")
        body_elem = "base_tray"

    ctx.check(
        "N concealer pans authored",
        len(pan_keys) == r.pan_count
        and all(holder.get_visual(f"pan_{k}") is not None for k in pan_keys),
        details=f"pan_count={r.pan_count}, keys={len(pan_keys)}",
    )

    cell_aabb = ctx.part_element_world_aabb(holder, elem="cell_grid")
    cell_top = cell_aabb[1][2] if cell_aabb else None
    for k in pan_keys:
        ctx.expect_within(
            holder, holder, axes="xy", inner_elem=f"pan_{k}", outer_elem="cell_grid",
            margin=0.0008, name=f"pan_{k} framed within cell grid",
        )
        p_aabb = ctx.part_element_world_aabb(holder, elem=f"pan_{k}")
        ctx.check(
            f"pan_{k} recessed below cell rim",
            p_aabb is not None and cell_top is not None and p_aabb[1][2] <= cell_top + 0.0003,
            details=f"pan_top={p_aabb[1][2] if p_aabb else None}, cell_top={cell_top}",
        )

    if r.is_round and len(pan_keys) > 1:
        centers = [(cx, cy) for (_key, cx, cy) in _pan_centers(r)]
        min_center_dist = min(
            math.hypot(ax - bx, ay - by)
            for i, (ax, ay) in enumerate(centers)
            for (bx, by) in centers[i + 1 :]
        )
        ctx.check(
            "round pans do not overlap",
            min_center_dist >= (2.0 * r.pan_radius + 2.0 * _PAN_CLEAR) - 1e-6,
            details=(
                f"min_center_dist={min_center_dist:.4f}, "
                f"required={(2.0 * r.pan_radius + 2.0 * _PAN_CLEAR):.4f}, "
                f"pan_radius={r.pan_radius:.4f}"
            ),
        )

    # ---- footprint identity ----
    holder_aabb = ctx.part_world_aabb(holder)
    hext = _ext(holder_aabb)
    if r.is_round:
        ctx.check(
            "round footprint (equal X/Y extents)",
            abs(hext[0] - hext[1]) < 0.006,
            details=f"dx={hext[0]:.4f}, dy={hext[1]:.4f}",
        )
    elif r.case_footprint == "square_rounded":
        ratio = hext[0] / hext[1] if hext[1] > 0 else 0.0
        ctx.check(
            "near-square footprint (L/D ~1.0)",
            0.70 < ratio < 1.40,
            details=f"len_x={hext[0]:.4f}, dep_y={hext[1]:.4f}, ratio={ratio:.3f}",
        )
    # flat-lying: thickness much less than length.
    ctx.check(
        "case lies flat (thickness << length)",
        hext[2] < hext[0] * 0.6,
        details=f"thickness={hext[2]:.4f}, length={hext[0]:.4f}",
    )

    # ---- closure-specific mechanism + captured-fit overlaps ----
    if r.closure_mechanism == "slide_out_drawer":
        shell = object_model.get_part("shell")
        drawer = object_model.get_part("drawer")
        slide = object_model.get_articulation("shell_to_drawer")
        ctx.check(
            "shell_to_drawer is PRISMATIC about +X",
            slide.articulation_type == ArticulationType.PRISMATIC and abs(slide.axis[0]) > 0.99,
            details=f"axis={slide.axis}, type={slide.articulation_type}",
        )
        # mirror on shell interior ceiling (below shell top).
        mir = ctx.part_element_world_aabb(shell, elem="mirror")
        body = ctx.part_element_world_aabb(shell, elem="shell_body")
        ctx.check(
            "mirror on shell interior ceiling",
            mir is not None and body is not None and mir[1][2] < body[1][2] - 0.0005,
            details=f"mirror_top={mir[1][2] if mir else None}, body_top={body[1][2] if body else None}",
        )
        ctx.allow_overlap(
            drawer, shell, elem_a="drawer_body", elem_b="shell_body",
            reason="Drawer body slides inside the hollow shell sleeve; the sleeve is modeled as wall plates but the collision mesh treats the shell volume as filled.",
        )
        ctx.allow_overlap(
            drawer, shell, elem_a="cell_grid", elem_b="shell_body",
            reason="The pan cell-divider grid rides inside the hollow shell sleeve.",
        )
        # drawer slides out along +X.
        rest = ctx.part_world_position(drawer)
        with ctx.pose({slide: _SLIDE_UPPER * r.joint_travel_scale}):
            ext = ctx.part_world_position(drawer)
        ctx.check(
            "drawer slides outward along +X",
            rest is not None and ext is not None and ext[0] > rest[0] + 0.04,
            details=f"rest_x={rest}, ext_x={ext}",
        )

    else:
        base = object_model.get_part("base")
        lid = object_model.get_part("lid")
        hinge = object_model.get_articulation("base_to_lid")
        ctx.check(
            "base_to_lid is REVOLUTE about -X",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.99,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        # mirror on lid inner face.
        mir = ctx.part_element_world_aabb(lid, elem="mirror")
        slab = ctx.part_element_world_aabb(lid, elem="lid_slab")
        ctx.check(
            "mirror on inner face of lid",
            mir is not None and slab is not None and mir[1][2] < slab[1][2] - 0.0005,
            details=f"mirror_top={mir[1][2] if mir else None}, slab_top={slab[1][2] if slab else None}",
        )
        lid_hinge_barrel = ctx.part_element_world_aabb(lid, elem="lid_hinge_barrel")
        knuckle_a = ctx.part_element_world_aabb(base, elem="hinge_knuckle_0")
        knuckle_b = ctx.part_element_world_aabb(base, elem="hinge_knuckle_1")
        knuckles = [aabb for aabb in (knuckle_a, knuckle_b) if aabb is not None]
        barrel_center = (
            (
                (lid_hinge_barrel[0][0] + lid_hinge_barrel[1][0]) / 2.0,
                (lid_hinge_barrel[0][1] + lid_hinge_barrel[1][1]) / 2.0,
                (lid_hinge_barrel[0][2] + lid_hinge_barrel[1][2]) / 2.0,
            )
            if lid_hinge_barrel is not None
            else None
        )
        knuckle_center = (
            (
                sum((aabb[0][0] + aabb[1][0]) / 2.0 for aabb in knuckles) / len(knuckles),
                sum((aabb[0][1] + aabb[1][1]) / 2.0 for aabb in knuckles) / len(knuckles),
                sum((aabb[0][2] + aabb[1][2]) / 2.0 for aabb in knuckles) / len(knuckles),
            )
            if knuckles
            else None
        )
        ctx.check(
            "lid hinge barrel is seated on the rear hinge axis",
            barrel_center is not None
            and knuckle_center is not None
            and abs(barrel_center[1] - knuckle_center[1]) < 0.0025
            and abs(barrel_center[2] - knuckle_center[2]) < 0.0025,
            details=(
                f"lid_barrel_center={barrel_center}, "
                f"base_knuckle_center={knuckle_center}"
            ),
        )
        ctx.allow_overlap(
            lid, base, elem_a="lid_frame", elem_b="base_frame",
            reason="Lid silver frame seats flush onto the base silver rim when closed.",
        )
        # lid flips up about the rear hinge.
        top0 = ctx.part_world_aabb(lid)[1][2]
        with ctx.pose({hinge: math.radians(100.0) * r.joint_travel_scale}):
            top1 = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "lid flips up about rear hinge (top rises)",
            top1 > top0 + 0.015,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )

        if r.closure_mechanism == "flip_lid_with_clasp":
            clasp = object_model.get_part("clasp")
            latch = object_model.get_articulation("base_to_clasp")
            ctx.check(
                "base_to_clasp is REVOLUTE about +X with finite limit",
                latch.articulation_type == ArticulationType.REVOLUTE
                and abs(latch.axis[0]) > 0.99
                and latch.motion_limits is not None
                and latch.motion_limits.upper is not None,
                details=f"axis={latch.axis}, type={latch.articulation_type}",
            )
            ctx.check(
                "clasp lever + lid lip authored",
                clasp.get_visual("clasp_lever") is not None and lid.get_visual("lid_lip") is not None,
                details="clasp_lever or lid_lip missing",
            )
            ctx.allow_overlap(
                clasp, lid, elem_a="clasp_lever", elem_b="lid_lip",
                reason="Clasp hook intentionally catches over the lid lip to latch the compact closed.",
            )
            ctx.allow_overlap(
                clasp, lid, elem_a="clasp_lever", elem_b="lid_slab",
                reason="Clasp pivot barrel sits at the front-edge junction where the lid slab meets the base.",
            )
            # Clasp unlatches: the hook reaches +Y over the lid lip when latched
            # (rest) and swings outward (-Y) away from the lip when unlatched.
            # The pivot barrel stays at the front edge, so the meaningful
            # "clears the lip" signal is the clasp's +Y front reach retracting
            # away from the lip, not an absolute height drop.
            lip0 = ctx.part_element_world_aabb(lid, elem="lid_lip")
            clasp_rest = ctx.part_element_world_aabb(clasp, elem="clasp_lever")
            with ctx.pose({latch: math.radians(75.0) * r.joint_travel_scale}):
                clasp_a = ctx.part_element_world_aabb(clasp, elem="clasp_lever")
            ctx.check(
                "clasp hook clears lid lip when unlatched (front reach retracts)",
                clasp_a is not None
                and clasp_rest is not None
                and lip0 is not None
                and clasp_rest[1][1] >= lip0[0][1] - 0.0005  # latched: hook reaches the lip
                and clasp_a[1][1] < clasp_rest[1][1] - 0.0010,  # unlatched: retreats in -Y
                details=(
                    f"clasp_front_y rest={clasp_rest[1][1] if clasp_rest else None}, "
                    f"unlatch={clasp_a[1][1] if clasp_a else None}, "
                    f"lip_back_y={lip0[0][1] if lip0 else None}"
                ),
            )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed closure joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()
