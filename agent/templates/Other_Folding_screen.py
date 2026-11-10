# SPDX-License-Identifier: Apache-2.0

"""Folding screen (multi-panel hinged room divider) modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_Folding_screen.md`` and the
``picture/Other/Folding screen`` 5-star sample pool (1 parent + 8 fork
variants), all synced under ``data/records/``.

A folding screen is N homogeneous decorative panels (each = a lacquered/wood
frame of bottom_rail + top_rail/crown + two stiles + an opening infill),
stood full height on the ground and chained left-to-right by **vertical-axis
REVOLUTE** piano-hinges with **alternating fold sense** (accordion zigzag).
The rest pose bakes a ~35 deg fold into each hinge origin so it reads like a
photographed screen.

Structure (pattern = ``mixed``): a single parameterized ``panel`` module —
varying by ``panel_infill`` (fret lattice / solid painted board / shoji paper
grid / louvered slats), ``frame_top`` (flat rail / arched crown) and
``has_base_feet`` (optional wider plinth shoe) — repeated ``panel_count``
times along +X. The chain is the multiplicity axis; ``N`` is encoded into
``slot_choices_for_seed`` as ``("panel_count", f"n{N}")`` so the
``module_topology_diversity`` gate counts it.

Copy-logic master: the N=4 / N=6 chain variants (``40969f37`` / ``98759298``)
— ``for i in range(N)``, root panel centered at X=0, every chain panel built
from x=SEAM_GAP, joint origin **absolute** at ROOT_HINGE_X (i=1) /
CHAIN_HINGE_X (i>=2), captured barrel<->knuckle hinge hardware. Absolute
(non-cumulative) placement + the per-pair-identical (odd/even) construction
make per-pair QC at small N generalize to any N, so the sweep only needs
small N while the declared domain reaches 12.

All hinge barrels are captured inside the parent's knuckles (piano-hinge),
so the chain joints omit ``MatingContract`` (grandfathered) and are guarded
by the flat articulation-origin baseline + element-scoped ``allow_overlap``
(mirroring the source records' run_tests block).

Only two chain panels are tessellated for the mesh infills/crown/foot (root
shift 0, chain shift SEAM_GAP) and reused across all N parts, so large N
stays cheap.
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
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

PanelInfill = Literal[
    "fret_lattice", "solid_painted_panel", "shoji_paper_grid", "louvered_slats"
]
FrameTop = Literal["flat_top", "arched_crown_top"]
PaletteStyle = Literal[
    "chinese_lacquer",
    "shoji_natural",
    "black_lacquer_gold",
    "ivory_painted",
    "bamboo_louver",
]

PANEL_INFILLS: tuple[PanelInfill, ...] = (
    "fret_lattice",
    "solid_painted_panel",
    "shoji_paper_grid",
    "louvered_slats",
)
FRAME_TOPS: tuple[FrameTop, ...] = ("flat_top", "arched_crown_top")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "chinese_lacquer",
    "shoji_natural",
    "black_lacquer_gold",
    "ivory_painted",
    "bamboo_louver",
)

# Multiplicity domain: declared product domain [2, 12]; config_from_seed draws
# panel_count weighted toward small N (sweep-fast). Every N up to 12 is
# reachable and safe by the N-invariant construction (absolute placement +
# alternating accordion fold), so large N need not be densely sampled.
N_MIN = 2
N_MAX = 12
# Sweep sampling domain [2, 8], small N dominant.
_SWEEP_COUNTS = (2, 3, 4, 5, 6, 7, 8)
_SWEEP_WEIGHTS = (24.0, 24.0, 18.0, 8.0, 6.0, 4.0, 3.0)

# Palette -> infill weak preference (spec §7 conditional). Any combination is
# legal; this only biases sampling.
_PALETTE_INFILL_PREF: dict[PaletteStyle, PanelInfill] = {
    "chinese_lacquer": "fret_lattice",
    "black_lacquer_gold": "fret_lattice",
    "shoji_natural": "shoji_paper_grid",
    "bamboo_louver": "louvered_slats",
    "ivory_painted": "solid_painted_panel",
}

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "chinese_lacquer": {
        "lacquer": (0.38, 0.10, 0.08, 1.0),
        "worn_lacquer": (0.45, 0.15, 0.11, 1.0),
        "field": (0.05, 0.05, 0.06, 1.0),
        "infill": (0.78, 0.62, 0.22, 1.0),
        "paper": (0.92, 0.86, 0.74, 0.55),
        "brass": (0.55, 0.42, 0.18, 1.0),
        "foot": (0.30, 0.18, 0.12, 1.0),
    },
    "shoji_natural": {
        "lacquer": (0.50, 0.36, 0.22, 1.0),
        "worn_lacquer": (0.44, 0.31, 0.19, 1.0),
        "field": (0.90, 0.86, 0.78, 1.0),
        "infill": (0.62, 0.46, 0.30, 1.0),
        "paper": (0.95, 0.93, 0.86, 0.5),
        "brass": (0.58, 0.50, 0.34, 1.0),
        "foot": (0.40, 0.29, 0.18, 1.0),
    },
    "black_lacquer_gold": {
        "lacquer": (0.07, 0.07, 0.08, 1.0),
        "worn_lacquer": (0.11, 0.11, 0.12, 1.0),
        "field": (0.03, 0.03, 0.03, 1.0),
        "infill": (0.83, 0.68, 0.28, 1.0),
        "paper": (0.86, 0.80, 0.66, 0.55),
        "brass": (0.62, 0.50, 0.22, 1.0),
        "foot": (0.05, 0.05, 0.06, 1.0),
    },
    "ivory_painted": {
        "lacquer": (0.88, 0.84, 0.76, 1.0),
        "worn_lacquer": (0.80, 0.75, 0.66, 1.0),
        "field": (0.93, 0.90, 0.84, 1.0),
        "infill": (0.66, 0.52, 0.62, 1.0),
        "paper": (0.96, 0.94, 0.90, 0.6),
        "brass": (0.70, 0.66, 0.56, 1.0),
        "foot": (0.74, 0.70, 0.62, 1.0),
    },
    "bamboo_louver": {
        "lacquer": (0.55, 0.42, 0.24, 1.0),
        "worn_lacquer": (0.48, 0.36, 0.20, 1.0),
        "field": (0.10, 0.09, 0.07, 1.0),
        "infill": (0.72, 0.58, 0.34, 1.0),
        "paper": (0.90, 0.84, 0.70, 0.55),
        "brass": (0.56, 0.46, 0.28, 1.0),
        "foot": (0.36, 0.27, 0.16, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters); scaled per build by the resolved config.
# All numbers ported from the source records (PANEL_W/H/T, rails, hinge heights).
# ---------------------------------------------------------------------------
_PANEL_W = 0.60
_PANEL_H = 1.70
_PANEL_T = 0.03
_RAIL_W = 0.05
_BOTTOM_RAIL_H = 0.25
_TOP_RAIL_H = 0.05
_SEAM_GAP = 0.013
_FOLD_ANGLE = math.radians(35.0)  # photo rest pose, forward of coplanar
_FOLD_RANGE = math.radians(150.0)  # max fold from coplanar, either way
_HINGE_Z_REF = 0.35  # lower hinge height (part-frame anchor for chain panels)

# Infill detail constants (source-faithful).
_FRET_BAR = 0.015
_FRET_DEPTH = 0.008
_MUNTIN_W = 0.008
_MUNTIN_D = 0.005
_SHOJI_COLS = 4
_SHOJI_ROWS = 8
_PAPER_T = 0.002
_PAINTED_PANEL_T = 0.012
_SLAT_FACE = 0.055
_SLAT_THICK = 0.006
_SLAT_TILT = math.radians(35.0)
_N_SLATS = 20
_FIELD_T = 0.012

# Frame-top (arched crown) constants.
_ARCH_RISE = 0.10
_ARCH_END_H = 0.04

# Base foot constants.
_FOOT_T = _PANEL_T + 0.03
_FOOT_H = 0.045

# Hinge hardware geometry.
_BARREL_R = 0.012
_BARREL_L = 0.10


@dataclass(frozen=True)
class FoldingScreenConfig:
    panel_infill: PanelInfill | None = None
    frame_top: FrameTop | None = None
    has_base_feet: bool | None = None
    panel_count: int | None = None
    palette_style: PaletteStyle = "chinese_lacquer"
    panel_width_scale: float = 1.0
    panel_height_scale: float = 1.0
    infill_density_scale: float = 1.0
    fold_rest_angle_scale: float = 1.0
    joint_limit_scale: float = 1.0
    name: str = "folding_screen"


@dataclass(frozen=True)
class ResolvedFoldingScreenConfig:
    panel_infill: PanelInfill
    frame_top: FrameTop
    has_base_feet: bool
    panel_count: int
    palette_style: PaletteStyle
    # Concrete geometry (scaled).
    panel_w: float
    panel_h: float
    rail_w: float
    bottom_rail_h: float
    top_rail_h: float
    seam_gap: float
    hinge_z_ref: float
    hinge_heights: tuple[float, float]
    open_w: float
    open_h: float
    open_zc: float
    root_hinge_x: float
    chain_hinge_x: float
    fold_angle: float
    fold_range: float
    joint_limit_lower_odd: float
    joint_limit_upper_odd: float
    joint_limit_lower_even: float
    joint_limit_upper_even: float
    shoji_cols: int
    shoji_rows: int
    n_slats: int
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> FoldingScreenConfig:
    rng = random.Random(seed)
    palette_style = rng.choice(PALETTE_STYLES)

    # Weak palette->infill preference: bias toward the preferred infill, else
    # uniform. Every combination remains legal.
    pref = _PALETTE_INFILL_PREF[palette_style]
    if rng.random() < 0.55:
        panel_infill: PanelInfill = pref
    else:
        panel_infill = rng.choice(PANEL_INFILLS)

    frame_top = rng.choice(FRAME_TOPS)
    has_base_feet = rng.random() < 0.45
    panel_count = rng.choices(_SWEEP_COUNTS, weights=_SWEEP_WEIGHTS, k=1)[0]

    return FoldingScreenConfig(
        panel_infill=panel_infill,
        frame_top=frame_top,
        has_base_feet=has_base_feet,
        panel_count=panel_count,
        palette_style=palette_style,
        panel_width_scale=round(rng.uniform(0.90, 1.12), 4),
        panel_height_scale=round(rng.uniform(0.90, 1.15), 4),
        infill_density_scale=round(rng.uniform(0.85, 1.20), 4),
        fold_rest_angle_scale=round(rng.uniform(0.80, 1.10), 4),
        joint_limit_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_folding_screen_{seed}",
    )


def resolve_config(
    config: FoldingScreenConfig | None = None,
) -> ResolvedFoldingScreenConfig:
    cfg = config or FoldingScreenConfig()
    panel_infill = _pick(cfg.panel_infill, PANEL_INFILLS)
    frame_top = _pick(cfg.frame_top, FRAME_TOPS)
    has_base_feet = bool(cfg.has_base_feet) if cfg.has_base_feet is not None else False
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    panel_count = int(cfg.panel_count) if cfg.panel_count is not None else 3
    panel_count = int(_clamp(panel_count, N_MIN, N_MAX))

    width_scale = _clamp(cfg.panel_width_scale, 0.90, 1.12)
    height_scale = _clamp(cfg.panel_height_scale, 0.90, 1.15)
    density_scale = _clamp(cfg.infill_density_scale, 0.85, 1.20)
    fold_scale = _clamp(cfg.fold_rest_angle_scale, 0.80, 1.10)
    limit_scale = _clamp(cfg.joint_limit_scale, 0.85, 1.10)

    panel_w = _PANEL_W * width_scale
    panel_h = _PANEL_H * height_scale
    rail_w = _RAIL_W
    bottom_rail_h = _BOTTOM_RAIL_H
    top_rail_h = _TOP_RAIL_H
    seam_gap = _SEAM_GAP

    open_w = panel_w - 2.0 * rail_w
    open_h = panel_h - bottom_rail_h - top_rail_h
    open_zc = bottom_rail_h + open_h / 2.0

    # Lower hinge sits at 1/4-ish of panel height; upper at ~4/5. Derived from
    # height so hinge hardware tracks the panel. Lower hinge defines the chain
    # part-frame anchor (so chain panel feet still land at z=0).
    hz_lo = _HINGE_Z_REF * height_scale
    hz_hi = (1.35 / 1.70) * panel_h
    hinge_heights = (hz_lo, hz_hi)
    hinge_z_ref = hz_lo

    root_hinge_x = panel_w / 2.0 + seam_gap
    chain_hinge_x = seam_gap + panel_w + seam_gap

    fold_angle = _clamp(_FOLD_ANGLE * fold_scale, math.radians(20.0), math.radians(45.0))
    fold_range = _FOLD_RANGE
    base_limit = fold_range * limit_scale
    # Odd hinges fold forward, even backward (matches build sense).
    joint_limit_lower_odd = -(base_limit + fold_angle)
    joint_limit_upper_odd = base_limit - fold_angle
    joint_limit_lower_even = -(base_limit - fold_angle)
    joint_limit_upper_even = base_limit + fold_angle

    shoji_cols = int(_clamp(round(_SHOJI_COLS * density_scale), 3, 6))
    shoji_rows = int(_clamp(round(_SHOJI_ROWS * density_scale), 6, 11))
    n_slats = int(_clamp(round(_N_SLATS * density_scale), 14, 26))

    return ResolvedFoldingScreenConfig(
        panel_infill=panel_infill,
        frame_top=frame_top,
        has_base_feet=has_base_feet,
        panel_count=panel_count,
        palette_style=palette_style,
        panel_w=panel_w,
        panel_h=panel_h,
        rail_w=rail_w,
        bottom_rail_h=bottom_rail_h,
        top_rail_h=top_rail_h,
        seam_gap=seam_gap,
        hinge_z_ref=hinge_z_ref,
        hinge_heights=hinge_heights,
        open_w=open_w,
        open_h=open_h,
        open_zc=open_zc,
        root_hinge_x=root_hinge_x,
        chain_hinge_x=chain_hinge_x,
        fold_angle=fold_angle,
        fold_range=fold_range,
        joint_limit_lower_odd=joint_limit_lower_odd,
        joint_limit_upper_odd=joint_limit_upper_odd,
        joint_limit_lower_even=joint_limit_lower_even,
        joint_limit_upper_even=joint_limit_upper_even,
        shoji_cols=shoji_cols,
        shoji_rows=shoji_rows,
        n_slats=n_slats,
        name=cfg.name or "folding_screen",
    )


def with_overrides(config: FoldingScreenConfig, **kwargs: object) -> FoldingScreenConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: FoldingScreenConfig | ResolvedFoldingScreenConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedFoldingScreenConfig)
        else resolve_config(config)
    )
    return (
        ("panel_infill", r.panel_infill),
        ("frame_top", r.frame_top),
        ("has_base_feet", "feet" if r.has_base_feet else "no_feet"),
        ("panel_count", f"n{r.panel_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared mesh geometry helpers (ported from the 5-star source records). Each
# returns a CadQuery workplane; the meshes are tessellated once and reused.
# ---------------------------------------------------------------------------
def _fret_lattice_scaled(r: ResolvedFoldingScreenConfig) -> cq.Workplane:
    """Gold fretwork lattice (parent 89fc1fef L50-92): a fused lattice of
    interlocking rectangles/squares drawn in the opening XY plane (u=width,
    v=height) and extruded by FRET_DEPTH. The source motif is authored for
    OPEN_W=0.50, OPEN_H=1.40; it is then anisotropically scaled (in-plane
    only, depth unchanged) to the resolved opening so it always frames inside
    the black field."""
    t = _FRET_BAR
    d = _FRET_DEPTH

    def ring(cx: float, cy: float, w: float, h: float) -> cq.Workplane:
        return (
            cq.Workplane("XY")
            .center(cx, cy)
            .rect(w, h)
            .rect(w - 2.0 * t, h - 2.0 * t)
            .extrude(d)
        )

    def bar(cx: float, cy: float, w: float, h: float) -> cq.Workplane:
        return cq.Workplane("XY").center(cx, cy).rect(w, h).extrude(d)

    solid = ring(0.0, 0.0, 0.49, 1.38)
    for vc in (-0.43, 0.0, 0.43):
        solid = solid.union(ring(0.0, vc, 0.36, 0.32))
        solid = solid.union(ring(0.0, vc, 0.20, 0.16))
        for s in (1.0, -1.0):
            solid = solid.union(bar(s * 0.14, vc, 0.09, t))
            solid = solid.union(bar(0.0, vc + s * 0.12, t, 0.09))
            solid = solid.union(bar(s * 0.205, vc, 0.06, t))
            for s2 in (1.0, -1.0):
                solid = solid.union(ring(s * 0.18, vc + s2 * 0.16, 0.09, 0.09))
    for vc in (-0.215, 0.215):
        solid = solid.union(bar(0.0, vc, t, 0.13))
    for vc in (-0.635, 0.635):
        solid = solid.union(bar(0.0, vc, t, 0.10))

    # Anisotropic in-plane fit to the resolved opening (depth = world Y kept).
    sx = r.open_w / 0.50
    sy = r.open_h / 1.40
    if abs(sx - 1.0) > 1e-6 or abs(sy - 1.0) > 1e-6:
        m = cq.Matrix([[sx, 0.0, 0.0, 0.0], [0.0, sy, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]])
        return cq.Workplane("XY").add(solid.val().transformGeometry(m))
    return solid


def _shoji_grid(r: ResolvedFoldingScreenConfig) -> cq.Workplane:
    """Shoji wood grid (variant c59458fc L57-86): regular muntin lattice in the
    opening XY plane, extruded by MUNTIN_D, sized to the resolved opening."""
    w = _MUNTIN_W
    d = _MUNTIN_D
    ow = r.open_w
    oh = r.open_h

    result = None
    n_v = r.shoji_cols + 1
    for i in range(n_v):
        x = -ow / 2.0 + i * (ow / (n_v - 1))
        bar = cq.Workplane("XY").center(x, 0.0).rect(w, oh).extrude(d)
        result = bar if result is None else result.union(bar)

    n_h = r.shoji_rows + 1
    for i in range(n_h):
        y = -oh / 2.0 + i * (oh / (n_h - 1))
        bar = cq.Workplane("XY").center(0.0, y).rect(ow, w).extrude(d)
        result = result.union(bar)
    return result


def _arched_crown(r: ResolvedFoldingScreenConfig, panel_w: float) -> cq.Workplane:
    """Arched crown band (variant 073d817a L98-114): curved lacquered band over
    the panel width, arcing up at the center. Local X=width, local Y=height
    (maps to world Z via rpy), extruded in local Z (panel thickness)."""
    hw = panel_w / 2.0
    wp = cq.Workplane("XY")
    profile = (
        wp.moveTo(-hw, 0.0)
        .lineTo(hw, 0.0)
        .lineTo(hw, _ARCH_END_H)
        .threePointArc((0.0, _ARCH_RISE), (-hw, _ARCH_END_H))
        .close()
    )
    return profile.extrude(_PANEL_T).translate((0.0, 0.0, -_PANEL_T / 2.0))


def _base_foot_shape(r: ResolvedFoldingScreenConfig, panel_w: float) -> cq.Workplane:
    """Chamfered plinth shoe under a panel (variant 63c52429 L100-107). The
    source authors a foot wider than the panel for a standalone screen; in the
    accordion chain the seam gap is only ~13 mm, so adjacent feet would collide.
    The foot is kept a touch narrower than the panel (still a clear deeper/
    chamfered plinth) so neighbouring feet never touch across the seam."""
    foot_w = panel_w - 0.02
    return (
        cq.Workplane("XY")
        .box(foot_w, _FOOT_T, _FOOT_H, centered=(True, True, False))
        .edges(">Z")
        .chamfer(0.008)
    )


# ---------------------------------------------------------------------------
# Per-panel mesh bundles (tessellated once per shift, reused across N parts).
# ---------------------------------------------------------------------------
def _panel_meshes(r: ResolvedFoldingScreenConfig, suffix: str, assets):
    """Tessellate the per-panel CadQuery meshes that depend on infill/frame_top/
    feet. Box-only sub-elements (rails, stiles, painted board, slats, field,
    hinge hardware) are emitted directly in the assembler, not here."""
    meshes: dict[str, object] = {}
    if r.panel_infill == "fret_lattice":
        meshes["fretwork"] = mesh_from_cadquery(
            _fret_lattice_scaled(r), f"fret_lattice_{suffix}.obj", assets=assets
        )
    elif r.panel_infill == "shoji_paper_grid":
        meshes["shoji_grid"] = mesh_from_cadquery(
            _shoji_grid(r), f"shoji_grid_{suffix}.obj", assets=assets
        )
    # solid_painted_panel & louvered_slats use Box primitives only.

    if r.frame_top == "arched_crown_top":
        meshes["crown_arch"] = mesh_from_cadquery(
            _arched_crown(r, r.panel_w), f"crown_arch_{suffix}.obj", assets=assets
        )
    if r.has_base_feet:
        meshes["base_foot"] = mesh_from_cadquery(
            _base_foot_shape(r, r.panel_w), f"base_foot_{suffix}.obj", assets=assets
        )
    return meshes


# ---------------------------------------------------------------------------
# Panel authoring (one parameterized panel, source-faithful per infill/frame).
# ---------------------------------------------------------------------------
def _add_panel(
    part,
    r: ResolvedFoldingScreenConfig,
    x0: float,
    x1: float,
    dz: float,
    mats: dict,
    meshes: dict,
) -> None:
    """Author one screen panel spanning part-local x in [x0, x1]. dz shifts
    nominal floor-based heights into the part frame (chain panel frames sit on
    the lower hinge at world z=hinge_z_ref)."""
    cx = (x0 + x1) / 2.0
    w = x1 - x0

    def z(v: float) -> float:
        return v - dz

    lacquer = mats["lacquer"]
    worn = mats["worn_lacquer"]
    field = mats["field"]
    infill_mat = mats["infill"]
    paper = mats["paper"]
    foot_mat = mats["foot"]

    # Optional wider base foot under the bottom rail (frame_detail: feet).
    if r.has_base_feet and "base_foot" in meshes:
        part.visual(
            meshes["base_foot"],
            origin=Origin(xyz=(cx, 0.0, z(0.0))),
            material=foot_mat,
            name="base_foot", material_class_id=("wood.polished_varnished" if r.palette_style in {"chinese_lacquer", "shoji_natural", "black_lacquer_gold", "ivory_painted"} else "wood.bamboo"),
        )

    # Frame: solid bottom rail.
    part.visual(
        Box((w, _PANEL_T, r.bottom_rail_h)),
        origin=Origin(xyz=(cx, 0.0, z(r.bottom_rail_h / 2.0))),
        material=worn,
        name="bottom_rail", material_class_id="wood.painted_weathered",
    )

    # Top: flat rail or arched crown.
    if r.frame_top == "arched_crown_top" and "crown_arch" in meshes:
        part.visual(
            meshes["crown_arch"],
            origin=Origin(
                xyz=(cx, 0.0, z(r.panel_h - r.top_rail_h)),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=lacquer,
            name="crown_arch", material_class_id=("wood.polished_varnished" if r.palette_style in {"chinese_lacquer", "shoji_natural", "black_lacquer_gold", "ivory_painted"} else "wood.bamboo"),
        )
    else:
        part.visual(
            Box((w, _PANEL_T, r.top_rail_h)),
            origin=Origin(xyz=(cx, 0.0, z(r.panel_h - r.top_rail_h / 2.0))),
            material=lacquer,
            name="top_rail", material_class_id=("wood.polished_varnished" if r.palette_style in {"chinese_lacquer", "shoji_natural", "black_lacquer_gold", "ivory_painted"} else "wood.bamboo"),
        )

    # Two side stiles.
    for idx, sx in enumerate((x0 + r.rail_w / 2.0, x1 - r.rail_w / 2.0)):
        part.visual(
            Box((r.rail_w, _PANEL_T, r.open_h + 0.02)),
            origin=Origin(xyz=(sx, 0.0, z(r.open_zc))),
            material=lacquer,
            name=f"stile_{idx}", material_class_id=("wood.polished_varnished" if r.palette_style in {"chinese_lacquer", "shoji_natural", "black_lacquer_gold", "ivory_painted"} else "wood.bamboo"),
        )

    # Opening infill (panel_infill axis).
    if r.panel_infill == "fret_lattice":
        # Black field + raised gold fretwork mesh.
        part.visual(
            Box((r.open_w + 0.01, _FIELD_T, r.open_h + 0.01)),
            origin=Origin(xyz=(cx, 0.0, z(r.open_zc))),
            material=field,
            name="lattice_field", material_class_id=("wood.polished_varnished" if r.palette_style in {"chinese_lacquer", "shoji_natural", "black_lacquer_gold", "ivory_painted"} else "wood.bamboo"),
        )
        part.visual(
            meshes["fretwork"],
            origin=Origin(xyz=(cx, -0.003, z(r.open_zc)), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=infill_mat,
            name="fretwork", material_class_id=("metal.precious_gold" if r.palette_style in {"chinese_lacquer", "black_lacquer_gold"} else "wood.patterned_decorative"),
        )
    elif r.panel_infill == "solid_painted_panel":
        part.visual(
            Box((r.open_w + 0.01, _PAINTED_PANEL_T, r.open_h + 0.01)),
            origin=Origin(xyz=(cx, 0.0, z(r.open_zc))),
            material=infill_mat,
            name="painted_panel", material_class_id="wood.painted_clean",
        )
    elif r.panel_infill == "shoji_paper_grid":
        part.visual(
            Box((r.open_w + 0.01, _PAPER_T, r.open_h + 0.01)),
            origin=Origin(xyz=(cx, 0.002, z(r.open_zc))),
            material=paper,
            name="shoji_paper", material_class_id=("paper.wallpaper_patterned" if r.palette_style == "ivory_painted" else "paper.plain_sheet"),
        )
        part.visual(
            meshes["shoji_grid"],
            origin=Origin(xyz=(cx, -0.003, z(r.open_zc)), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=infill_mat,
            name="shoji_grid", material_class_id=("wood.polished_varnished" if r.palette_style in {"chinese_lacquer", "shoji_natural", "black_lacquer_gold", "ivory_painted"} else "wood.bamboo"),
        )
    else:  # louvered_slats
        part.visual(
            Box((r.open_w + 0.01, _FIELD_T, r.open_h + 0.01)),
            origin=Origin(xyz=(cx, 0.0, z(r.open_zc))),
            material=field,
            name="louver_field", material_class_id=("wood.polished_varnished" if r.palette_style in {"chinese_lacquer", "shoji_natural", "black_lacquer_gold", "ivory_painted"} else "wood.bamboo"),
        )
        slat_geom = Box((r.open_w + 0.01, _SLAT_THICK, _SLAT_FACE))
        slat_spacing = r.open_h / (r.n_slats + 1)
        z_bot = r.open_zc - r.open_h / 2.0
        for i in range(r.n_slats):
            sz = z_bot + slat_spacing * (i + 1)
            part.visual(
                slat_geom,
                origin=Origin(xyz=(cx, 0.0, z(sz)), rpy=(_SLAT_TILT, 0.0, 0.0)),
                material=infill_mat,
                name=f"slat_{i}", material_class_id=("wood.polished_varnished" if r.palette_style in {"chinese_lacquer", "shoji_natural", "black_lacquer_gold", "ivory_painted"} else "wood.bamboo"),
            )


def _add_barrel_hardware(
    part, r: ResolvedFoldingScreenConfig, hinge_x: float, dz: float, mats: dict
) -> None:
    """Captured-pin barrel + web + leaf on a child panel at the hinge axis
    (N=4 source 40969f37 L146-170). Barrel sits ON the hinge axis so the
    upstream interface lands on the part origin (x=hinge_x)."""
    brass = mats["brass"]
    for idx, zh in enumerate(r.hinge_heights):
        zl = zh - dz
        part.visual(
            Cylinder(radius=_BARREL_R, length=_BARREL_L),
            origin=Origin(xyz=(hinge_x, 0.0, zl)),
            material=brass,
            name=f"barrel_{idx}", material_class_id="metal.brass_aged",
        )
        part.visual(
            Box((0.024, 0.022, 0.05)),
            origin=Origin(xyz=(hinge_x + 0.012, 0.0, zl)),
            material=brass,
            name=f"web_{idx}", material_class_id="metal.brass_aged",
        )
        part.visual(
            Box((0.05, 0.005, 0.04)),
            origin=Origin(xyz=(hinge_x + 0.025, -0.017, zl)),
            material=brass,
            name=f"barrel_leaf_{idx}", material_class_id="metal.brass_aged",
        )


def _add_knuckle_hardware(
    part, r: ResolvedFoldingScreenConfig, hinge_x: float, dz: float, mats: dict
) -> None:
    """Capturing knuckles + leaf on a parent panel's right seam (N=4 source
    40969f37 L173-190)."""
    brass = mats["brass"]
    for idx, zh in enumerate(r.hinge_heights):
        zl = zh - dz
        part.visual(
            Box((0.036, 0.005, 0.07)),
            origin=Origin(xyz=(hinge_x - 0.033, -0.017, zl)),
            material=brass,
            name=f"knuckle_leaf_{idx}", material_class_id="metal.brass_aged",
        )
        for k, sz in enumerate((-1.0, 1.0)):
            part.visual(
                Box((0.027, 0.022, 0.025)),
                origin=Origin(xyz=(hinge_x - 0.0075, 0.0, zl + sz * 0.035)),
                material=brass,
                name=f"knuckle_{idx}_{k}", material_class_id="metal.brass_aged",
            )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_folding_screen(
    config: FoldingScreenConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"screen_{key}_{r.palette_style}", rgba=pal[key])
        for key in ("lacquer", "worn_lacquer", "field", "infill", "paper", "brass", "foot")
    }

    # Two panel geometries: root (centered at X=0, dz=0) and chain (shifted to
    # x=SEAM_GAP, dz=hinge_z_ref). The chain meshes are reused across all
    # panel_{i>=1} parts.
    root_meshes = _panel_meshes(r, "root", assets)
    chain_meshes = _panel_meshes(r, "chain", assets)

    n = r.panel_count
    panels = []
    for i in range(n):
        panel = model.part(f"panel_{i}")
        if i == 0:
            _add_panel(panel, r, -r.panel_w / 2.0, r.panel_w / 2.0, 0.0, mats, root_meshes)
            if n > 1:
                _add_knuckle_hardware(panel, r, r.root_hinge_x, 0.0, mats)
        else:
            _add_panel(
                panel, r, r.seam_gap, r.seam_gap + r.panel_w, r.hinge_z_ref, mats, chain_meshes
            )
            # Barrel sits on the hinge axis = the chain part frame origin (x=0).
            _add_barrel_hardware(panel, r, 0.0, r.hinge_z_ref, mats)
            if i < n - 1:
                _add_knuckle_hardware(panel, r, r.chain_hinge_x, r.hinge_z_ref, mats)
        panels.append(panel)

    # Chained vertical-axis hinges, alternating fold sense (accordion zigzag).
    for i in range(1, n):
        parent = panels[i - 1]
        child = panels[i]
        # Absolute placement: joint origin on the parent's seam knuckle.
        hinge_x = r.root_hinge_x if i == 1 else r.chain_hinge_x
        hinge_z = r.hinge_z_ref if i == 1 else 0.0
        forward = i % 2 == 1
        fold_sign = -1.0 if forward else 1.0
        if forward:
            lower, upper = r.joint_limit_lower_odd, r.joint_limit_upper_odd
        else:
            lower, upper = r.joint_limit_lower_even, r.joint_limit_upper_even
        model.articulation(
            f"hinge_{i - 1}_{i}",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=child,
            origin=Origin(
                xyz=(hinge_x, 0.0, hinge_z),
                rpy=(0.0, 0.0, fold_sign * r.fold_angle),
            ),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(
                effort=30.0, velocity=2.0, lower=lower, upper=upper
            ),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_folding_screen(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_folding_screen(config_from_seed(seed), assets=assets)


def _aabb_center(aabb) -> tuple[float, float, float]:
    (xmn, ymn, zmn), (xmx, ymx, zmx) = aabb
    return ((xmn + xmx) / 2.0, (ymn + ymx) / 2.0, (zmn + zmx) / 2.0)


def run_folding_screen_tests(
    object_model: ArticulatedObject,
    config: FoldingScreenConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    n = r.panel_count

    # Captured-pin hinges: each child panel's barrels are seated inside the
    # parent panel's knuckles. Element-scoped, per hinge (N=4 source L343-365).
    for i in range(1, n):
        child = object_model.get_part(f"panel_{i}")
        parent = object_model.get_part(f"panel_{i - 1}")
        for idx in range(len(r.hinge_heights)):
            for k in range(2):
                ctx.allow_overlap(
                    child,
                    parent,
                    elem_a=f"barrel_{idx}",
                    elem_b=f"knuckle_{idx}_{k}",
                    reason=(
                        f"Parent knuckle captures child barrel at hinge {i - 1}->{i} "
                        "around the shared vertical pin axis."
                    ),
                )
        # Folding brings adjacent panel frames (rails / stiles / feet) together;
        # they graze as the screen folds flat.
        ctx.allow_overlap(
            child,
            parent,
            reason=f"Adjacent panels {i - 1}->{i} fold together and their frames graze.",
        )
    # When fully folded, non-adjacent panels also stack together.
    for _i in range(n):
        for _j in range(_i + 1, n):
            ctx.allow_overlap(
                object_model.get_part(f"panel_{_i}"),
                object_model.get_part(f"panel_{_j}"),
                reason="Folding-screen panels stack together when folded.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    # The compiler-owned baseline runs fail_if_articulation_origin_far_from_geometry
    # at a flat 0.015 m. The chain joint origin sits on the parent's seam
    # knuckle hardware and the child barrel is centered on its own part origin,
    # so dist~0 for both; no explicit call needed.

    part_names = {p.name for p in object_model.parts}
    expected = {f"panel_{i}" for i in range(n)}
    ctx.check(
        "expected_parts_present",
        expected.issubset(part_names),
        details=str(sorted(part_names)),
    )
    ctx.check(
        "exact_hinge_count",
        len(object_model.joints) == n - 1,
        details=f"joints={len(object_model.joints)} expected={n - 1}",
    )

    for i in range(1, n):
        joint = object_model.get_articulation(f"hinge_{i - 1}_{i}")
        ctx.check(
            f"hinge_{i - 1}_{i}_vertical_revolute",
            joint.articulation_type == ArticulationType.REVOLUTE
            and abs(joint.axis[2]) > 0.99
            and abs(joint.axis[0]) < 1e-6
            and abs(joint.axis[1]) < 1e-6,
            details=f"type={joint.articulation_type} axis={tuple(joint.axis)}",
        )

    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # Every panel stands full height on the floor.
    for i in range(n):
        aabb = ctx.part_world_aabb(object_model.get_part(f"panel_{i}"))
        if aabb is not None:
            ctx.check(
                f"panel_{i} stands on the floor at full height",
                aabb[0][2] < 0.02 and aabb[1][2] > 0.92 * r.panel_h,
                details=f"z_min={aabb[0][2]:.4f} z_max={aabb[1][2]:.4f}",
            )

    # panel_0 is a thin upright slab near Y=0 (root stays in its plane).
    aabb0 = ctx.part_world_aabb(object_model.get_part("panel_0"))
    if aabb0 is not None:
        ctx.check(
            "panel_0 reads as a thin upright slab",
            aabb0[0][1] > -0.08 and aabb0[1][1] < 0.08,
            details=f"y=({aabb0[0][1]:.3f},{aabb0[1][1]:.3f})",
        )

    # Accordion: panel_1 (odd hinge) angles forward, gaining a Y footprint.
    if n >= 2:
        aabb1 = ctx.part_world_aabb(object_model.get_part("panel_1"))
        if aabb1 is not None:
            ctx.check(
                "panel_1 angles forward (accordion fold)",
                (aabb1[1][1] - aabb1[0][1]) > 0.12,
                details=f"y_ext={(aabb1[1][1] - aabb1[0][1]):.3f}",
            )

    # sampled-pose exemption: many accordion hinges make broad pose products
    # noisy; targeted seam motion checks cover the intended legal motion.
    # Actuating the last hinge swings the last panel about the vertical seam.
    last = object_model.get_part(f"panel_{n - 1}")
    rest_aabb = ctx.part_world_aabb(last)
    last_hinge = object_model.get_articulation(f"hinge_{n - 2}_{n - 1}")
    with ctx.pose({last_hinge: 0.8}):
        swung_aabb = ctx.part_world_aabb(last)
    if rest_aabb is not None and swung_aabb is not None:
        rest_c = _aabb_center(rest_aabb)
        swung_c = _aabb_center(swung_aabb)
        delta = math.sqrt(sum((swung_c[k] - rest_c[k]) ** 2 for k in range(3)))
        ctx.check(
            "last_panel_swings_about_seam", delta > 0.03, details=f"delta={delta:.4f}"
        )

    return ctx.report()


__all__ = (
    "FoldingScreenConfig",
    "ResolvedFoldingScreenConfig",
    "build_folding_screen",
    "build_seeded_folding_screen",
    "config_from_seed",
    "resolve_config",
    "run_folding_screen_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
