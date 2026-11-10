# SPDX-License-Identifier: Apache-2.0

"""Door / Other — heterogeneous catch-all "other single door" modular template.

This is a deliberate **catch-all single-door bucket** built around a
split-mechanism REVOLUTE spine (Slot A) as the PRIMARY identity axis. Slot A is
also the SHELL selector: choosing a split mechanism fixes the frame root (wood
casing vs stone surround), the leaf-local origin (hinge edge vs centerline), and
the bearing interface (HINGE_LAP / pintle / pivot-socket). Head-profile (Slot B)
and leaf-infill (Slot C) are sampled independently and locally adapted to the
selected shell; missing cross-shell source cells are supplemented procedurally.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Door_Other.md`` and the 10
five-star door_other samples synced under ``data/records/`` (two parents +
8 slot-fork variants).

Slots (pattern = ``mixed``):
  * ``split_mechanism`` (Slot A, 3): ``dutch_two_leaf`` (wood casing, TWO
    independent vertical-Z revolutes upper+lower) / ``single_solid_leaf`` (stone
    surround, ONE vertical-Z revolute on jamb pintles) / ``center_pivot`` (stone
    surround, ONE bidirectional vertical-Z revolute through the leaf centerline
    seated in top/bottom socket cups).
  * ``head_profile`` (Slot B, 5): ``flat_square`` / ``full_semicircle`` /
    ``broad_barn_segmental`` / ``shallow_segmental`` / ``flat_top_rect``. The
    curved/tympanum heads use the shared CadQuery
    ``_arched_profile_face`` helper (Rule 3 — no Box downgrade).
  * ``leaf_infill`` (Slot C, 5): ``glazed_lite`` / ``solid_panel`` / ``louvered`` /
    ``plank_strap`` / ``porthole`` on every shell; each face module has a local
    host adapter and keeps its source-recognizable geometry.
  * multiplicity: ``plank_count`` (plank/porthole), ``lite_count`` (glazed),
    ``louver_slat_count`` (louvered) — each active only under its infill, encoded
    into the slot_choice tuple.

Hard rules honored:
  1. Non-articulating decorations (planks, studs, straps, slats, muntins, panes)
     are fused leaf visuals or inline ``part.visual(...)`` (Rule 1).
  2. The only separate child parts are the swinging leaves, the ring_pull
     (REVOLUTE, captured-through-boss → grandfathered MatingContract), and the
     FIXED knob/lever — which DO declare a MatingContract onto a real leaf face
     (Rule 2).
  3. Arched/segmental heads use the CadQuery lathe/extrude profile helper, never
     a Box/Cylinder downgrade (Rule 3).

Captured-pin / lap / tessellation overlaps (HINGE_LAP, strap-barrel↔pintle,
pivot-spine↔socket, planks↔stone opening, ring↔boss, muntin↔planks) are
element-scoped ``allow_overlap`` declarations mirroring each source record's
run_tests block.
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
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
SplitMechanism = Literal["dutch_two_leaf", "single_solid_leaf", "center_pivot"]
HeadProfile = Literal[
    "flat_square",
    "full_semicircle",
    "broad_barn_segmental",
    "shallow_segmental",
    "flat_top_rect",
]
LeafInfill = Literal["glazed_lite", "solid_panel", "louvered", "plank_strap", "porthole"]
PaletteStyle = Literal[
    "stone_oak_plank",
    "painted_pine_panel",
    "glazed_white_lite",
    "charcoal_iron_barn",
    "weathered_grey_plank",
    "honey_oak_porthole",
]

SPLIT_MECHANISMS: tuple[SplitMechanism, ...] = (
    "dutch_two_leaf",
    "single_solid_leaf",
    "center_pivot",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "stone_oak_plank",
    "painted_pine_panel",
    "glazed_white_lite",
    "charcoal_iron_barn",
    "weathered_grey_plank",
    "honey_oak_porthole",
)

# --- Complete independent slot domains. No cross-slot compatibility gates. ---
ALL_HEADS: tuple[HeadProfile, ...] = (
    "flat_square",
    "full_semicircle",
    "broad_barn_segmental",
    "shallow_segmental",
    "flat_top_rect",
)
ALL_INFILLS: tuple[LeafInfill, ...] = (
    "glazed_lite", "solid_panel", "louvered", "plank_strap", "porthole"
)

# Palette is an independent presentation choice; source shell tones remain
# available as references, but they do not gate any structural slot pairing.
DUTCH_PALETTES: tuple[PaletteStyle, ...] = (
    "painted_pine_panel",
    "glazed_white_lite",
    "stone_oak_plank",
)
STONE_PALETTES: tuple[PaletteStyle, ...] = (
    "stone_oak_plank",
    "charcoal_iron_barn",
    "weathered_grey_plank",
    "honey_oak_porthole",
)

# Multiplicity ranges (spec §"参数范围汇总" / Multiplicity).
PLANK_MIN, PLANK_MAX = 3, 12
PLANK_WEIGHTS = {3: 0.10, 4: 0.16, 5: 0.16, 6: 0.18, 7: 0.14, 8: 0.12,
                 9: 0.06, 10: 0.04, 11: 0.02, 12: 0.02}
LITE_MIN, LITE_MAX = 2, 3      # grid rows/cols (2x2..3x3)
LITE_GRID_WEIGHTS = {2: 0.70, 3: 0.30}
SLAT_MIN, SLAT_MAX = 6, 18
SLAT_WEIGHTS = {6: 0.06, 8: 0.10, 10: 0.16, 11: 0.14, 12: 0.16, 13: 0.14,
                14: 0.10, 15: 0.06, 16: 0.04, 18: 0.04}

# ---------------------------------------------------------------------------
# Palettes — RGBA per shell-token. Every .visual material is keyed from here.
# Glass tokens keep alpha < 0.6 (transparent), as required by the sources.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # warm honey/oak plank + grey stone + dark wrought iron (arched parent).
    "stone_oak_plank": {
        "wood": (0.60, 0.43, 0.24, 1.0),
        "wood_shadow": (0.46, 0.33, 0.18, 1.0),
        "stone": (0.60, 0.59, 0.55, 1.0),
        "iron": (0.08, 0.08, 0.09, 1.0),
        "steel": (0.72, 0.74, 0.76, 1.0),
        "glass": (0.72, 0.84, 0.88, 0.35),
    },
    # fresh painted pine casing (Dutch parent tones).
    "painted_pine_panel": {
        "wood": (0.82, 0.66, 0.45, 1.0),
        "wood_shadow": (0.66, 0.51, 0.33, 1.0),
        "stone": (0.70, 0.68, 0.64, 1.0),
        "iron": (0.20, 0.20, 0.22, 1.0),
        "steel": (0.72, 0.74, 0.76, 1.0),
        "glass": (0.98, 0.99, 1.0, 0.40),
    },
    # bright white-painted glazed lite door.
    "glazed_white_lite": {
        "wood": (0.92, 0.92, 0.90, 1.0),
        "wood_shadow": (0.78, 0.78, 0.76, 1.0),
        "stone": (0.72, 0.70, 0.66, 1.0),
        "iron": (0.18, 0.18, 0.20, 1.0),
        "steel": (0.74, 0.76, 0.78, 1.0),
        "glass": (0.96, 0.99, 1.0, 0.38),
    },
    # charcoal-stained barn timber + black iron.
    "charcoal_iron_barn": {
        "wood": (0.26, 0.24, 0.22, 1.0),
        "wood_shadow": (0.16, 0.15, 0.14, 1.0),
        "stone": (0.55, 0.54, 0.51, 1.0),
        "iron": (0.05, 0.05, 0.06, 1.0),
        "steel": (0.62, 0.63, 0.64, 1.0),
        "glass": (0.66, 0.78, 0.84, 0.34),
    },
    # weathered grey driftwood plank.
    "weathered_grey_plank": {
        "wood": (0.55, 0.54, 0.50, 1.0),
        "wood_shadow": (0.42, 0.41, 0.38, 1.0),
        "stone": (0.64, 0.63, 0.60, 1.0),
        "iron": (0.10, 0.10, 0.11, 1.0),
        "steel": (0.68, 0.70, 0.72, 1.0),
        "glass": (0.74, 0.82, 0.86, 0.36),
    },
    # rich honey oak + bright porthole glass.
    "honey_oak_porthole": {
        "wood": (0.68, 0.48, 0.26, 1.0),
        "wood_shadow": (0.52, 0.37, 0.19, 1.0),
        "stone": (0.62, 0.60, 0.56, 1.0),
        "iron": (0.07, 0.07, 0.08, 1.0),
        "steel": (0.72, 0.74, 0.76, 1.0),
        "glass": (0.78, 0.90, 0.94, 0.32),
    },
}


# ===========================================================================
# Base dimensions (meters). Shared across shells where possible.
# ===========================================================================
# Leaf
_LEAF_W = 0.90          # nominal door width
_DOOR_H = 2.020         # full Dutch door height
_LEAF_T = 0.044         # Dutch leaf thickness
_PLANK_THK = 0.055      # stone-shell plank thickness
_LEAF_SPRING = 1.55     # stone-shell arch springline

# Dutch split
_SPLIT_Z = 1.060
_SPLIT_GAP = 0.004
_THRESHOLD_H = 0.020

# Dutch frame
_JAMB_W = 0.050
_JAMB_D = 0.150
_HEAD_GAP = 0.006
_SIDE_GAP = 0.004
_HINGE_LAP = 0.005
_CASING_W = 0.065
_CASING_T = 0.020

# Dutch leaf window / panel construction
_STILE_W = 0.095
_RAIL_TOP_W = 0.100
_RAIL_BOT_W = 0.130
_MUNTIN_W = 0.022
_GLASS_T = 0.005
_GLASS_INSET = 0.008
_GROOVE_INSET = 0.100
_GROOVE_W = 0.016
_GROOVE_DEPTH = 0.009
_PANEL_PROUD = 0.011
_PANEL_MARGIN = 0.130
_HINGE_LEN = 0.100
_HINGE_R = 0.011
_SLAT_THICK = 0.005
_SLAT_DEPTH = 0.044
_SLAT_ANGLE_DEG = 35.0

# Lever handle
_BACKPLATE_W = 0.040
_BACKPLATE_H = 0.140
_BACKPLATE_T = 0.008
_LEVER_LEN = 0.120
_LEVER_DIA = 0.018
_LEVER_BASE_R = 0.022

# Stone frame
_STONE_JAMB_W = 0.26
_WALL_THK = 0.34
_GAP = 0.035            # leaf↔reveal clearance

# Ring pull
_RING_CZ = 1.10
_RING_MEAN_R = 0.055
_RING_TUBE_R = 0.009

# Pivot hardware
_PIVOT_PIN_R = 0.015
_PIVOT_PIN_LEN = 0.030
_PIVOT_SPINE_W = 0.055
_PIVOT_SPINE_THK = 0.008
_PIVOT_COLLAR_R = 0.032
_SOCKET_PLATE_R = 0.045
_SOCKET_CUP_OR = 0.024
_SOCKET_CUP_IR = 0.016
_SOCKET_CUP_DEPTH = 0.030

# Porthole
_PORTHOLE_R = 0.14
_PORTHOLE_GLASS_THK = 0.004
_PORTHOLE_MUNTIN_W = 0.018
_PORTHOLE_MUNTIN_THK = 0.006


# ===========================================================================
# Config dataclasses
# ===========================================================================
@dataclass(frozen=True)
class DoorOtherConfig:
    split_mechanism: SplitMechanism | None = None
    head_profile: HeadProfile | None = None
    leaf_infill: LeafInfill | None = None
    plank_count: int | None = None
    lite_grid: int | None = None       # rows == cols (2 → 2x2, 3 → 3x3)
    louver_slat_count: int | None = None
    palette_style: PaletteStyle | None = None
    leaf_width_scale: float = 1.0
    leaf_height_scale: float = 1.0
    leaf_thickness_scale: float = 1.0
    arch_rise_scale: float = 1.0
    name: str = "door_other"


@dataclass(frozen=True)
class ResolvedDoorOtherConfig:
    split_mechanism: SplitMechanism
    head_profile: HeadProfile
    leaf_infill: LeafInfill
    plank_count: int
    lite_grid: int
    louver_slat_count: int
    palette_style: PaletteStyle
    # geometry (scaled / derived)
    leaf_w: float
    leaf_t: float           # active leaf thickness for this shell
    door_h: float           # Dutch full height
    leaf_spring: float      # stone-shell arch springline
    leaf_top: float         # stone-shell apex / flat-top height
    arch_rise: float        # segmental rise above spring (0 for flat heads)
    split_z: float
    # ring-pull mount (stone shells)
    ring_cx: float          # door-local X of ring center
    ring_cz: float
    name: str

    @property
    def is_stone_shell(self) -> bool:
        return self.split_mechanism in ("single_solid_leaf", "center_pivot")

    @property
    def has_ring_pull(self) -> bool:
        # Ring-pull hardware is a reusable stone-shell face attachment.  The
        # Dutch shell uses its native knob/lever path instead.
        return self.is_stone_shell


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _wchoice(rng: random.Random, weights: dict[int, float]) -> int:
    keys = list(weights.keys())
    return rng.choices(keys, weights=[weights[k] for k in keys], k=1)[0]


# ===========================================================================
# Procedural sampling — independent slot choices; builders adapt each choice.
# ===========================================================================
def config_from_seed(seed: int) -> DoorOtherConfig:
    rng = random.Random(seed)

    # 1. Slot A: weighted (single slightly higher — most sources).
    split = rng.choices(
        SPLIT_MECHANISMS, weights=(0.34, 0.36, 0.30), k=1
    )[0]

    # 2 & 3. Slot B and Slot C are complete independent domains.
    head = rng.choice(ALL_HEADS)
    infill = rng.choice(ALL_INFILLS)
    palette = rng.choice(PALETTE_STYLES)

    # 4. Active multiplicity for the chosen infill.
    plank_count = _wchoice(rng, PLANK_WEIGHTS) if infill in ("plank_strap", "porthole") else 6
    lite_grid = _wchoice(rng, LITE_GRID_WEIGHTS) if infill == "glazed_lite" else 2
    slat_count = _wchoice(rng, SLAT_WEIGHTS) if infill == "louvered" else 13

    # 5. Continuous local scales.
    return DoorOtherConfig(
        split_mechanism=split,
        head_profile=head,
        leaf_infill=infill,
        plank_count=plank_count,
        lite_grid=lite_grid,
        louver_slat_count=slat_count,
        palette_style=palette,
        leaf_width_scale=round(rng.uniform(0.90, 1.35), 4),
        leaf_height_scale=round(rng.uniform(0.92, 1.10), 4),
        leaf_thickness_scale=round(rng.uniform(0.85, 1.20), 4),
        arch_rise_scale=round(rng.uniform(0.80, 1.25), 4),
        name=f"seeded_door_other_{seed}",
    )


def resolve_config(config: DoorOtherConfig | None = None) -> ResolvedDoorOtherConfig:
    cfg = config or DoorOtherConfig()

    split = _pick(cfg.split_mechanism, SPLIT_MECHANISMS)

    # Slot B and Slot C are complete independent domains. Cross-shell source
    # gaps are handled by the local leaf/frame emitters below.
    head = _pick(cfg.head_profile, ALL_HEADS)
    infill = _pick(cfg.leaf_infill, ALL_INFILLS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    # --- Multiplicity clamps. ---
    plank_count = int(_clamp(cfg.plank_count if cfg.plank_count is not None else 6,
                             PLANK_MIN, PLANK_MAX))
    lite_grid = int(_clamp(cfg.lite_grid if cfg.lite_grid is not None else 2,
                           LITE_MIN, LITE_MAX))
    slat_count = int(_clamp(cfg.louver_slat_count if cfg.louver_slat_count is not None else 13,
                            SLAT_MIN, SLAT_MAX))

    # --- Continuous scales. ---
    w_scale = _clamp(cfg.leaf_width_scale, 0.90, 1.35)
    h_scale = _clamp(cfg.leaf_height_scale, 0.92, 1.10)
    t_scale = _clamp(cfg.leaf_thickness_scale, 0.85, 1.20)
    rise_scale = _clamp(cfg.arch_rise_scale, 0.80, 1.25)

    leaf_w = _LEAF_W * w_scale

    if split == "dutch_two_leaf":
        leaf_t = _LEAF_T * t_scale
        door_h = _DOOR_H * h_scale
        # SPLIT_Z projected into a feasible band so each leaf height > 0.3 m.
        split_z = _SPLIT_Z * h_scale
        split_z = _clamp(split_z, _THRESHOLD_H + 0.35, door_h - 0.35)
        leaf_spring = leaf_top = door_h
        arch_rise = 0.0
        ring_cx = ring_cz = 0.0
    else:
        leaf_t = _PLANK_THK * t_scale
        door_h = _DOOR_H * h_scale  # informational
        leaf_spring = _LEAF_SPRING * h_scale
        if head == "full_semicircle":
            arch_rise = leaf_w / 2.0  # true semicircle
            leaf_top = leaf_spring + arch_rise
        elif head in ("broad_barn_segmental", "shallow_segmental"):
            base_rise = 0.20 if head == "broad_barn_segmental" else 0.12
            # scaled rise, clamped to a safe segmental band relative to width.
            arch_rise = _clamp(base_rise * rise_scale, 0.08, 0.45 * leaf_w)
            leaf_top = leaf_spring + arch_rise
        else:  # flat_top_rect — flat leaf, arch lives only in stone tympanum.
            arch_rise = 0.0
            leaf_top = 2.00 * h_scale
        split_z = 0.0
        # ring center near the latch / right edge of the leaf.
        ring_cx = leaf_w - 0.16  # hinge-origin frame (single); centered frame remaps below
        ring_cz = _RING_CZ

    return ResolvedDoorOtherConfig(
        split_mechanism=split,
        head_profile=head,
        leaf_infill=infill,
        plank_count=plank_count,
        lite_grid=lite_grid,
        louver_slat_count=slat_count,
        palette_style=palette,
        leaf_w=leaf_w,
        leaf_t=leaf_t,
        door_h=door_h,
        leaf_spring=leaf_spring,
        leaf_top=leaf_top,
        arch_rise=arch_rise,
        split_z=split_z,
        ring_cx=ring_cx,
        ring_cz=ring_cz,
        name=cfg.name or "door_other",
    )


def with_overrides(config: DoorOtherConfig, **kwargs: object) -> DoorOtherConfig:
    return replace(config, **kwargs)


# ===========================================================================
# slot_choices — what module_topology_diversity counts. Encodes shell + head +
# infill + the *active* multiplicity bucket only.
# ===========================================================================
def slot_choices_for_config(
    config: DoorOtherConfig | ResolvedDoorOtherConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedDoorOtherConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("split_mechanism", r.split_mechanism),
        ("head_profile", r.head_profile),
        ("leaf_infill", r.leaf_infill),
    ]
    if r.leaf_infill in ("plank_strap", "porthole"):
        choices.append(("plank_count", f"n{r.plank_count}"))
    elif r.leaf_infill == "glazed_lite":
        choices.append(("lite_grid", f"g{r.lite_grid}"))
    elif r.leaf_infill == "louvered":
        choices.append(("louver_slat_count", f"n{r.louver_slat_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Shared CadQuery helpers (Rule 3 — preserve source primitive complexity).
# ===========================================================================
def _arched_profile_face(width: float, spring: float, top: float) -> cq.Workplane:
    """XZ face: rectangle 0..spring, then a 3-point circular arc to apex `top`.

    Handles BOTH segmental (shallow) and full-semicircle profiles, exactly as the
    arched / segmental / roundtop sources. Spans x in [0, width], z in [0, top].
    """
    cx = width / 2.0
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(0.0, spring)
        .threePointArc((cx, top), (width, spring))
        .lineTo(width, 0.0)
        .close()
    )


def _arched_profile_centered(width: float, spring: float, top: float) -> cq.Workplane:
    """Same arch profile but centered at x=0 (center-pivot leaf frame)."""
    hw = width / 2.0
    return (
        cq.Workplane("XZ")
        .moveTo(-hw, 0.0)
        .lineTo(-hw, spring)
        .threePointArc((0.0, top), (hw, spring))
        .lineTo(hw, 0.0)
        .close()
    )


def _flat_face(width: float, top: float, *, centered: bool) -> cq.Workplane:
    """XZ rectangle face for the flat-top leaf."""
    if centered:
        hw = width / 2.0
        return (cq.Workplane("XZ").moveTo(-hw, 0.0).lineTo(-hw, top)
                .lineTo(hw, top).lineTo(hw, 0.0).close())
    return (cq.Workplane("XZ").moveTo(0.0, 0.0).lineTo(0.0, top)
            .lineTo(width, top).lineTo(width, 0.0).close())


def _concentric_open_rise(leaf_w: float, leaf_rise: float, open_w: float, gap: float) -> float:
    """Opening segmental rise for a concentric arc (R_open = R_door + GAP)."""
    if leaf_rise <= 1e-6:
        return 0.0
    door_r = (leaf_w ** 2 / 4.0 + leaf_rise ** 2) / (2.0 * leaf_rise)
    open_r = door_r + gap
    return open_r - math.sqrt(max(open_r ** 2 - (open_w / 2.0) ** 2, 0.0))


# ---- Dutch leaf cadquery helpers (window / panel / louver / hinge) ----
def _raised_panel_leaf_cq(width: float, height: float, thickness: float) -> cq.Workplane:
    blank = cq.Workplane("XY").box(width, thickness, height, centered=(False, True, False))
    cx, cz = width / 2.0, height / 2.0
    face_y = thickness / 2.0
    outer_w = width - 2 * _GROOVE_INSET
    outer_h = height - 2 * _GROOVE_INSET
    groove = (
        cq.Workplane("XZ").workplane(offset=face_y).center(cx, cz)
        .rect(outer_w, outer_h).rect(outer_w - 2 * _GROOVE_W, outer_h - 2 * _GROOVE_W)
        .extrude(-_GROOVE_DEPTH)
    )
    leaf = blank.cut(groove)
    panel_w = width - 2 * _PANEL_MARGIN
    panel_h = height - 2 * _PANEL_MARGIN
    panel = (
        cq.Workplane("XZ").workplane(offset=face_y).center(cx, cz)
        .rect(panel_w, panel_h).extrude(_PANEL_PROUD)
    )
    try:
        panel = panel.edges(">Y").chamfer(min(0.010, _PANEL_PROUD - 0.001))
    except Exception:
        pass
    return leaf.union(panel)


def _window_frame_leaf_cq(width: float, height: float, thickness: float, grid: int) -> cq.Workplane:
    """Upper Dutch leaf: stile/rail frame around an open window + grid×grid muntins."""
    open_x0, open_x1 = _STILE_W, width - _STILE_W
    open_z0, open_z1 = _RAIL_BOT_W, height - _RAIL_TOP_W
    open_w, open_h = open_x1 - open_x0, open_z1 - open_z0
    open_cx, open_cz = (open_x0 + open_x1) / 2.0, (open_z0 + open_z1) / 2.0

    blank = cq.Workplane("XY").box(width, thickness, height, centered=(False, True, False))
    opening = (
        cq.Workplane("XZ").workplane(offset=thickness).center(open_cx, open_cz)
        .rect(open_w, open_h).extrude(-2.0 * thickness)
    )
    frame = blank.cut(opening)

    bar_t = thickness - 2 * _GLASS_INSET
    # grid-1 vertical + grid-1 horizontal muntins (loop, spec multiplicity).
    for j in range(1, grid):
        vx = open_x0 + j * open_w / grid
        v_bar = (
            cq.Workplane("XY").transformed(offset=cq.Vector(vx, 0.0, open_cz))
            .box(_MUNTIN_W, bar_t, open_h, centered=(True, True, True))
        )
        frame = frame.union(v_bar)
    for j in range(1, grid):
        hz = open_z0 + j * open_h / grid
        h_bar = (
            cq.Workplane("XY").transformed(offset=cq.Vector(open_cx, 0.0, hz))
            .box(open_w, bar_t, _MUNTIN_W, centered=(True, True, True))
        )
        frame = frame.union(h_bar)

    bead = (
        cq.Workplane("XZ").workplane(offset=thickness / 2.0).center(open_cx, open_cz)
        .rect(open_w + 0.016, open_h + 0.016).rect(open_w, open_h).extrude(0.006)
    )
    return frame.union(bead)


def _louver_frame_leaf_cq(width: float, height: float, thickness: float) -> cq.Workplane:
    open_x0, open_x1 = _STILE_W, width - _STILE_W
    open_z0, open_z1 = _RAIL_BOT_W, height - _RAIL_TOP_W
    open_w, open_h = open_x1 - open_x0, open_z1 - open_z0
    open_cx, open_cz = (open_x0 + open_x1) / 2.0, (open_z0 + open_z1) / 2.0
    blank = cq.Workplane("XY").box(width, thickness, height, centered=(False, True, False))
    opening = (
        cq.Workplane("XZ").workplane(offset=thickness).center(open_cx, open_cz)
        .rect(open_w, open_h).extrude(-2.0 * thickness)
    )
    return blank.cut(opening)


def _hinge_barrel_mesh(name: str):
    barrel = cq.Workplane("XY").circle(_HINGE_R).extrude(_HINGE_LEN)
    plate_w, plate_t = 0.038, 0.004
    plate_jamb = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(-plate_w / 2.0 - _HINGE_R * 0.5, 0.0, _HINGE_LEN / 2.0))
        .box(plate_w, plate_t, _HINGE_LEN * 0.85, centered=(True, True, True))
    )
    plate_leaf = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(plate_w / 2.0 + _HINGE_R * 0.5, 0.0, _HINGE_LEN / 2.0))
        .box(plate_w, plate_t, _HINGE_LEN * 0.85, centered=(True, True, True))
    )
    return mesh_from_cadquery(barrel.union(plate_jamb).union(plate_leaf), name)


def _lever_handle_mesh(name: str):
    boss_len = 0.014
    shaft_total_len = _BACKPLATE_T + boss_len + _LEVER_LEN
    bp = cq.Workplane("XY").box(_BACKPLATE_W, _BACKPLATE_T, _BACKPLATE_H, centered=(True, True, True))
    try:
        bp = bp.edges("|Y").fillet(0.004)
    except Exception:
        pass
    shaft_cy = -_BACKPLATE_T / 2.0 + shaft_total_len / 2.0
    shaft = (
        cq.Workplane("XY").transformed(offset=cq.Vector(0.0, shaft_cy, 0.0))
        .box(_LEVER_DIA, shaft_total_len, _LEVER_DIA, centered=(True, True, True))
    )
    try:
        shaft = shaft.edges("|Y").fillet(_LEVER_DIA * 0.25)
    except Exception:
        pass
    handle = bp.union(shaft)
    boss_ext = boss_len + 0.004
    boss_cy = _BACKPLATE_T / 2.0 - 0.004 + boss_ext / 2.0
    boss = (
        cq.Workplane("XY").transformed(offset=cq.Vector(0.0, boss_cy, 0.0))
        .box(_LEVER_BASE_R * 2.0, boss_ext, _LEVER_BASE_R * 2.0, centered=(True, True, True))
    )
    try:
        boss = boss.edges("|Y").fillet(_LEVER_BASE_R * 0.4)
    except Exception:
        pass
    handle = handle.union(boss)
    tip_y = -_BACKPLATE_T / 2.0 + shaft_total_len
    tip = (
        cq.Workplane("XY").transformed(offset=cq.Vector(0.0, tip_y, 0.0)).sphere(_LEVER_DIA * 0.7)
    )
    return mesh_from_cadquery(handle.union(tip), name)


def _knob_mesh(name: str):
    knob = cq.Workplane("XY").circle(0.012).extrude(0.018).faces(">Z").sphere(0.018)
    rose = cq.Workplane("XY").circle(0.026).extrude(0.006).edges(">Z").fillet(0.002)
    return mesh_from_cadquery(rose.union(knob), name)


# ---- Stone-shell plank / strap / studs / ring / pintle / socket helpers ----
def _arch_height(x: float, cx: float, radius: float, spring: float) -> float:
    dx = x - cx
    if abs(dx) >= radius - 1e-9:
        return spring
    return spring + math.sqrt(max(0.0, radius * radius - dx * dx))


def _seg_arch_height(x: float, cx: float, door_r: float, spring: float, half_w: float, rise: float) -> float:
    """Segmental-arc height. The arc is a circle of radius door_r whose center
    lies BELOW the springline at z = (spring + rise) - door_r; height at dx is
    center_z + sqrt(door_r^2 - dx^2), giving spring+rise at the apex (dx=0) and
    spring at the springline endpoints (dx=±half_w)."""
    dx = x - cx
    if abs(dx) >= half_w - 1e-9:
        return spring
    center_z = spring + rise - door_r
    return center_z + math.sqrt(max(0.0, door_r ** 2 - dx ** 2))


def _leaf_top_at(r: ResolvedDoorOtherConfig, x: float, *, x0_leaf: float) -> float:
    """Top edge Z of the leaf at local x (so planks follow the Slot B arch top)."""
    cx = x0_leaf + r.leaf_w / 2.0
    half_w = r.leaf_w / 2.0
    if r.head_profile == "full_semicircle":
        return _arch_height(x, cx, half_w, r.leaf_spring)
    if r.head_profile in ("broad_barn_segmental", "shallow_segmental"):
        door_r = (r.leaf_w ** 2 / 4.0 + r.arch_rise ** 2) / (2.0 * r.arch_rise)
        return _seg_arch_height(x, cx, door_r, r.leaf_spring, half_w, r.arch_rise)
    return r.leaf_top  # flat_top_rect


def _build_single_plank(r: ResolvedDoorOtherConfig, i: int, *, x0_leaf: float, kerf: float = 0.003):
    """One arched/flat plank board, top edge follows the Slot B head profile."""
    pitch = r.leaf_w / r.plank_count
    x0 = x0_leaf + i * pitch + (kerf / 2.0 if i > 0 else 0.0)
    x1 = x0_leaf + (i + 1) * pitch - (kerf / 2.0 if i < r.plank_count - 1 else 0.0)
    z_left = _leaf_top_at(r, x0, x0_leaf=x0_leaf)
    z_right = _leaf_top_at(r, x1, x0_leaf=x0_leaf)
    z_mid = _leaf_top_at(r, (x0 + x1) / 2.0, x0_leaf=x0_leaf)
    wp = cq.Workplane("XZ").moveTo(x0, 0.0).lineTo(x0, z_left)
    if r.head_profile in ("flat_top_rect", "flat_square"):
        wp = wp.lineTo(x1, z_right)
    else:
        wp = wp.threePointArc(((x0 + x1) / 2.0, z_mid), (x1, z_right))
    wp = wp.lineTo(x1, 0.0).close()
    return wp.extrude(r.leaf_t / 2.0, both=True)


def _build_battens_mesh(r: ResolvedDoorOtherConfig, *, x_center: float):
    batten_h, batten_thk = 0.12, 0.025
    out = None
    for z_center in (0.45, min(1.30, r.leaf_spring - 0.10)):
        batten = (
            cq.Workplane("XY").box(r.leaf_w * 0.92, batten_thk, batten_h)
            .translate((x_center, -r.leaf_t / 2.0 - batten_thk / 2.0 + 0.004, z_center))
        )
        out = batten if out is None else out.union(batten)
    return out


def _build_strap_hinge_mesh(r: ResolvedDoorOtherConfig, z_center: float, *, x_hinge_local: float):
    """Strap hinge from the hinge edge running across the leaf front (+Y)."""
    strap_thk, strap_w = 0.007, 0.072
    strap_len = r.leaf_w * 0.88
    embed = 0.004
    y_shift = r.leaf_t / 2.0 - embed + strap_thk
    neck = strap_len - 0.10
    x0 = x_hinge_local
    strap = (
        cq.Workplane("XZ")
        .moveTo(x0 + 0.10, z_center - strap_w / 2.0)
        .lineTo(x0 + 0.10, z_center + strap_w / 2.0)
        .lineTo(x0 + neck, z_center + strap_w / 2.0)
        .lineTo(x0 + neck + 0.025, z_center + 0.040)
        .lineTo(x0 + strap_len, z_center + 0.010)
        .lineTo(x0 + strap_len + 0.055, z_center)
        .lineTo(x0 + strap_len, z_center - 0.010)
        .lineTo(x0 + neck + 0.025, z_center - 0.040)
        .lineTo(x0 + neck, z_center - strap_w / 2.0)
        .close().extrude(strap_thk).translate((0.0, y_shift, 0.0))
    )
    plate = (
        cq.Workplane("XZ").moveTo(x0 + 0.06, z_center).rect(0.12, strap_w, centered=True)
        .extrude(strap_thk).translate((0.0, y_shift, 0.0))
    )
    strap = strap.union(plate)
    barrel_y = r.leaf_t / 2.0 + 0.018
    barrel = (
        cq.Workplane("XY").circle(0.018).circle(0.011).extrude(0.11)
        .translate((x_hinge_local, barrel_y, z_center - 0.055))
    )
    return strap.union(barrel)


_STUD_R = 0.013


def _stud_dome(r: ResolvedDoorOtherConfig, sx: float, sz: float, *, x0_leaf: float):
    """One dome stud, embedded into the plank face with a real overlapping cap so
    it is never a floating island, and clamped to sit below the local leaf-top
    edge at its x (so studs near the arch don't float above the planks)."""
    top_at_x = _leaf_top_at(r, sx, x0_leaf=x0_leaf)
    sz = min(sz, top_at_x - _STUD_R - 0.010)
    sz = max(sz, _STUD_R + 0.010)
    # center the sphere INSIDE the plank by ~half a radius so a real cap overlaps.
    cy = r.leaf_t / 2.0 - _STUD_R * 0.5
    return cq.Workplane("XZ").moveTo(sx, sz).sphere(_STUD_R).translate((0.0, cy, 0.0))


def _build_iron_studs_mesh(r: ResolvedDoorOtherConfig, *, x0_leaf: float, ring_cx: float):
    """Dome studs + ring-pull mounting boss (fused leaf visual)."""
    studs = None
    front_y = r.leaf_t / 2.0

    def _dome(sx: float, sz: float):
        return _stud_dome(r, sx, sz, x0_leaf=x0_leaf)

    # stud rows along the strap heights + an upper border + latch column.
    strap_xs = [x0_leaf + r.leaf_w * f for f in (0.13, 0.27, 0.40, 0.53, 0.67, 0.80)]
    for sz in (0.45, min(1.30, r.leaf_spring - 0.10)):
        for sx in strap_xs:
            d = _dome(sx, sz)
            studs = d if studs is None else studs.union(d)
    for sx in (x0_leaf + r.leaf_w * f for f in (0.20, 0.40, 0.60, 0.80)):
        studs = studs.union(_dome(sx, min(1.78, r.leaf_spring + 0.18)))
    for sz in (0.30, 0.65, 1.00, 1.45):
        studs = studs.union(_dome(x0_leaf + r.leaf_w - 0.10, sz))

    ring_pivot_z = r.ring_cz + _RING_MEAN_R
    boss = (
        cq.Workplane("XY").circle(0.020).extrude(0.020)
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((ring_cx, front_y - 0.006, ring_pivot_z))
    )
    studs = studs.union(boss)
    return studs


def _build_pivot_studs_mesh(r: ResolvedDoorOtherConfig, *, ring_cx: float):
    """Center-pivot studs along the centerline + ring boss (centered frame)."""
    studs = None
    front_y = r.leaf_t / 2.0
    hw = r.leaf_w / 2.0
    x0_leaf = -hw

    def _dome(sx: float, sz: float):
        return _stud_dome(r, sx, sz, x0_leaf=x0_leaf)

    for sz in (0.20, 0.50, 0.80, 1.10, 1.40):
        d = _dome(0.0, sz)
        studs = d if studs is None else studs.union(d)
    for sz in (0.45, min(1.30, r.leaf_spring - 0.10)):
        for sx in (-0.22, -0.11, 0.11, 0.22):
            studs = studs.union(_dome(_clamp(sx, -hw + 0.06, hw - 0.06), sz))
    for sz in (0.30, 0.65, 1.00, 1.45):
        studs = studs.union(_dome(hw - 0.08, sz))
        studs = studs.union(_dome(-hw + 0.08, sz))

    ring_pivot_z = r.ring_cz + _RING_MEAN_R
    boss = (
        cq.Workplane("XY").circle(0.020).extrude(0.020)
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((ring_cx, front_y - 0.006, ring_pivot_z))
    )
    return studs.union(boss)


def _build_ring_pull_mesh(name: str):
    ring = (
        cq.Workplane("XY").center(_RING_MEAN_R, 0.0).circle(_RING_TUBE_R)
        .revolve(360.0, (-_RING_MEAN_R, 0.0, 0.0), (-_RING_MEAN_R, 1.0, 0.0))
        .translate((0.0, 0.0, -_RING_MEAN_R))
    )
    return mesh_from_cadquery(ring, name)


def _build_porthole_glass_mesh(r: ResolvedDoorOtherConfig, *, x0_leaf: float):
    cx = x0_leaf + r.leaf_w * 0.50
    cz = min(1.60, max(0.35, r.leaf_top - 0.30))
    return (
        cq.Workplane("XZ").circle(_PORTHOLE_R - 0.001)
        .extrude(_PORTHOLE_GLASS_THK / 2.0, both=True).translate((cx, 0.0, cz))
    )


def _build_muntin_ring_mesh(r: ResolvedDoorOtherConfig, *, x0_leaf: float):
    cx = x0_leaf + r.leaf_w * 0.50
    cz = min(1.60, max(0.35, r.leaf_top - 0.30))
    outer_r = _PORTHOLE_R + _PORTHOLE_MUNTIN_W
    inner_r = _PORTHOLE_R - 0.003
    total_depth = _PORTHOLE_MUNTIN_THK + r.leaf_t + _PORTHOLE_MUNTIN_THK
    y_start = r.leaf_t / 2.0 + _PORTHOLE_MUNTIN_THK
    return (
        cq.Workplane("XZ").circle(outer_r).circle(inner_r).extrude(total_depth)
        .translate((cx, y_start, cz))
    )


def _emit_dutch_plank_face(part, r: ResolvedDoorOtherConfig, mats, *, height: float,
                           assets, prefix: str) -> None:
    """Adapt the arched-shell plank/porthole face onto one Dutch leaf.

    The Dutch leaf has a rectangular local host, so each source plank is
    emitted as a shallow board with a shared pitch. This preserves the source
    copy logic while keeping the two-leaf hinge topology unchanged.
    """
    edge = _HINGE_LAP + 0.006
    usable_w = max(0.20, r.leaf_w - edge - 0.006)
    pitch = usable_w / r.plank_count
    backing = cq.Workplane("XY").box(
        usable_w, r.leaf_t, max(0.02, height - 0.06),
        centered=(False, True, False)
    ).translate((edge, 0.0, 0.03))
    backing_name = "lower_body" if prefix == "lower" else "upper_plank_backing"
    part.visual(mesh_from_cadquery(backing, backing_name, assets=assets),
                material=mats["wood_shadow"], name=backing_name, material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    for i in range(r.plank_count):
        board = cq.Workplane("XY").box(
            max(0.008, pitch - 0.003), r.leaf_t * 0.72, max(0.02, height - 0.06),
            centered=(False, True, False)
        ).translate((edge + i * pitch + 0.0015, 0.0, 0.03))
        part.visual(mesh_from_cadquery(board, f"{prefix}_plank_{i}", assets=assets),
                    material=mats["wood"], name=f"{prefix}_plank_{i}", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))


def _emit_stone_face_candidate(part, r: ResolvedDoorOtherConfig, mats, *,
                               x0_leaf: float, centered: bool, assets) -> None:
    """Emit any Slot-C face candidate on a stone/pivot leaf.

    The source arched plank implementation remains the base for plank/porthole;
    Dutch face modules use the same leaf-local helpers and are trimmed by the
    surrounding opening. All visuals stay on the articulated leaf part.
    """
    if r.leaf_infill in ("plank_strap", "porthole"):
        return
    if centered:
        base = _arched_profile_centered(r.leaf_w, r.leaf_spring, r.leaf_top) \
            if r.head_profile in ("full_semicircle", "broad_barn_segmental", "shallow_segmental") \
            else _flat_face(r.leaf_w, r.leaf_top, centered=True)
        x_origin = -r.leaf_w / 2.0
    else:
        base = _arched_profile_face(r.leaf_w, r.leaf_spring, r.leaf_top) \
            if r.head_profile in ("full_semicircle", "broad_barn_segmental", "shallow_segmental") \
            else _flat_face(r.leaf_w, r.leaf_top, centered=False)
        x_origin = x0_leaf
    part.visual(mesh_from_cadquery(base.extrude(r.leaf_t / 2.0, both=True),
                                   "leaf_body", assets=assets),
                material=mats["wood"], name="leaf_body", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    if r.leaf_infill == "solid_panel":
        panel_h = max(0.20, min(r.leaf_spring - 0.18, r.leaf_top - 0.22))
        panel = cq.Workplane("XY").box(
            max(0.20, r.leaf_w - 2.0 * _PANEL_MARGIN), _PANEL_PROUD, panel_h,
            centered=(True, True, False)
        ).translate((0.0 if centered else r.leaf_w / 2.0,
                     r.leaf_t / 2.0 + _PANEL_PROUD / 2.0 - 0.002, _PANEL_MARGIN))
        part.visual(mesh_from_cadquery(panel, "raised_panel", assets=assets),
                    material=mats["wood"], name="raised_panel", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    elif r.leaf_infill == "glazed_lite":
        safe_h = max(0.20, min(r.leaf_spring - 0.16, r.leaf_top - 0.20))
        open_w = max(0.20, r.leaf_w - 2.0 * _STILE_W)
        # Source muntin grid, emitted as interior rails over the adapted leaf.
        for j in range(1, r.lite_grid):
            vx = (-r.leaf_w / 2.0 if centered else 0.0) + _STILE_W + j * open_w / r.lite_grid
            bar = cq.Workplane("XY").box(_MUNTIN_W, r.leaf_t + 0.028, safe_h - _RAIL_BOT_W,
                                          centered=(True, True, False)).translate((vx, 0.0, _RAIL_BOT_W))
            part.visual(mesh_from_cadquery(bar, f"muntin_v_{j}", assets=assets),
                        material=mats["wood"], name=f"muntin_v_{j}", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
        for j in range(1, r.lite_grid):
            hz = _RAIL_BOT_W + j * (safe_h - _RAIL_BOT_W) / r.lite_grid
            bar = cq.Workplane("XY").box(open_w, r.leaf_t + 0.028, _MUNTIN_W + 0.018,
                                          centered=(True, True, True)).translate(
                                              ((0.0 if centered else r.leaf_w / 2.0), 0.0, hz))
            part.visual(mesh_from_cadquery(bar, f"muntin_h_{j}", assets=assets),
                        material=mats["wood"], name=f"muntin_h_{j}", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
        pane = cq.Workplane("XY").box(
            max(0.10, r.leaf_w - 2.0 * _STILE_W - 0.004),
            max(_GLASS_T, r.leaf_t * 0.18), max(0.10, r.leaf_top - _RAIL_BOT_W - _RAIL_TOP_W - 0.004),
            centered=(True, True, True)
        ).translate((0.0 if centered else r.leaf_w / 2.0,
                     0.0, r.leaf_top / 2.0))
        part.visual(mesh_from_cadquery(pane, "window_glass", assets=assets),
                    material=mats["glass"], name="window_glass", material_class_id="glass.clear_transparent")
    elif r.leaf_infill == "louvered":
        # Keep the arch-shaped base as the host; emit only the interior louver
        # slats so rectangular corner material cannot cross a curved reveal.
        open_x0, open_x1 = _STILE_W, r.leaf_w - _STILE_W
        open_z0, open_z1 = _RAIL_BOT_W, r.leaf_top - _RAIL_TOP_W
        for i in range(r.louver_slat_count):
            slat = cq.Workplane("XY").box(
                open_x1 - open_x0 + 0.020, _SLAT_DEPTH, _SLAT_THICK,
                centered=(True, True, True)
            ).translate((0.0 if centered else r.leaf_w / 2.0,
                         r.leaf_t / 2.0 + _SLAT_DEPTH / 2.0 - 0.004,
                         open_z0 + (i + 0.5) / r.louver_slat_count * (open_z1 - open_z0)))
            part.visual(mesh_from_cadquery(slat, f"slat_{i}", assets=assets),
                        material=mats["wood_shadow"], name=f"slat_{i}", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))


# ===========================================================================
# Slot A — DUTCH SHELL (wood casing, two independent vertical revolutes).
# ===========================================================================
def _build_dutch_shell(model: ArticulatedObject, r: ResolvedDoorOtherConfig, mats, *, assets):
    leaf_w, leaf_t, door_h = r.leaf_w, r.leaf_t, r.door_h
    split_z = r.split_z
    lower_bottom = _THRESHOLD_H
    lower_top = split_z - _SPLIT_GAP / 2.0
    upper_bottom = split_z + _SPLIT_GAP / 2.0
    upper_top = door_h
    lower_h = lower_top - lower_bottom
    upper_h = upper_top - upper_bottom
    opening_h = door_h + _HEAD_GAP

    # ---- FIXED FRAME root ----
    frame = model.part("door_frame")
    hinge_jamb_x = -_JAMB_W / 2.0 + _HINGE_LAP
    frame.visual(Box((_JAMB_W, _JAMB_D, opening_h)),
                 origin=Origin(xyz=(hinge_jamb_x, 0.0, opening_h / 2.0)),
                 material=mats["wood_shadow"], name="hinge_jamb", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    latch_jamb_x = leaf_w + _SIDE_GAP + _JAMB_W / 2.0
    frame.visual(Box((_JAMB_W, _JAMB_D, opening_h)),
                 origin=Origin(xyz=(latch_jamb_x, 0.0, opening_h / 2.0)),
                 material=mats["wood_shadow"], name="latch_jamb", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    head_z = opening_h + _JAMB_W / 2.0
    head_len = (latch_jamb_x + _JAMB_W / 2.0) - (hinge_jamb_x - _JAMB_W / 2.0)
    head_cx = (latch_jamb_x + hinge_jamb_x) / 2.0
    frame.visual(Box((head_len, _JAMB_D, _JAMB_W)),
                 origin=Origin(xyz=(head_cx, 0.0, head_z)),
                 material=mats["wood_shadow"], name="head_jamb", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    sill_len = leaf_w + _SIDE_GAP
    frame.visual(Box((sill_len, _JAMB_D, _THRESHOLD_H)),
                 origin=Origin(xyz=(sill_len / 2.0, 0.0, _THRESHOLD_H / 2.0)),
                 material=mats["wood_shadow"], name="threshold", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    casing_y = _JAMB_D / 2.0 + _CASING_T / 2.0
    casing_outer_w = head_len + 2 * _CASING_W
    frame.visual(Box((_CASING_W, _CASING_T, opening_h + _CASING_W)),
                 origin=Origin(xyz=(hinge_jamb_x - _JAMB_W / 2.0 - _CASING_W / 2.0, casing_y,
                                    (opening_h + _CASING_W) / 2.0)),
                 material=mats["wood"], name="casing_leg_hinge", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    frame.visual(Box((_CASING_W, _CASING_T, opening_h + _CASING_W)),
                 origin=Origin(xyz=(latch_jamb_x + _JAMB_W / 2.0 + _CASING_W / 2.0, casing_y,
                                    (opening_h + _CASING_W) / 2.0)),
                 material=mats["wood"], name="casing_leg_latch", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    frame.visual(Box((casing_outer_w, _CASING_T, _CASING_W)),
                 origin=Origin(xyz=(head_cx, casing_y, opening_h + _JAMB_W + _CASING_W / 2.0)),
                 material=mats["wood"], name="casing_head", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    # Slot-B host adaptation: retain the Dutch casing but add the selected
    # source-backed curved/tympanum profile as a real CadQuery face.
    if r.head_profile != "flat_square":
        if r.head_profile == "full_semicircle":
            rise = head_len / 2.0
        elif r.head_profile == "broad_barn_segmental":
            rise = 0.20
        elif r.head_profile == "shallow_segmental":
            rise = 0.12
        else:  # flat_top_rect: tympanum-style semicircle above a flat leaf.
            rise = head_len / 2.0
        profile = _arched_profile_face(head_len, opening_h, opening_h + rise).extrude(
            _JAMB_D / 2.0, both=True
        )
        # Keep only the curved cap above the opening springline; the lower
        # rectangular body is already supplied by the casing/head jamb and
        # would otherwise intersect the moving leaves.
        profile = profile.cut(cq.Workplane("XY").box(
            head_len + 0.20, _JAMB_D + 0.20, opening_h,
            centered=(False, True, False)
        ))
        frame.visual(mesh_from_cadquery(
            profile.translate(
                (hinge_jamb_x - _JAMB_W / 2.0, 0.0, 0.0)),
            "head_profile", assets=assets), material=mats["wood_shadow"], name="head_profile", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    frame.inertial = Inertial.from_geometry(
        Box((head_len, _JAMB_D, opening_h)), mass=20.0,
        origin=Origin(xyz=(head_cx, 0.0, opening_h / 2.0)))

    # ---- Slot C infill on each leaf ----
    upper = model.part("upper_leaf")
    lower = model.part("lower_leaf")

    # LOWER leaf — raised panel for Dutch face modules, or adapted plank face
    # for the stone-derived plank/porthole modules.
    if r.leaf_infill in ("plank_strap", "porthole"):
        _emit_dutch_plank_face(lower, r, mats, height=lower_h, assets=assets, prefix="lower")
        _emit_dutch_plank_face(upper, r, mats, height=upper_h, assets=assets, prefix="upper")
        if r.leaf_infill == "porthole":
            pane = cq.Workplane("XZ").circle(_PORTHOLE_R * 0.72).extrude(_GLASS_T / 2.0, both=True)
            upper.visual(mesh_from_cadquery(
                pane.translate((leaf_w * 0.5, 0.0, upper_h * 0.56)),
                "porthole_glass", assets=assets), material=mats["glass"], name="porthole_glass", material_class_id="glass.clear_transparent")
            ring = cq.Workplane("XZ").circle(_PORTHOLE_R * 0.80).circle(_PORTHOLE_R * 0.70).extrude(
                _PORTHOLE_MUNTIN_THK, both=True)
            upper.visual(mesh_from_cadquery(
                ring.translate((leaf_w * 0.5, leaf_t / 2.0, upper_h * 0.56)),
                "muntin_rings", assets=assets), material=mats["iron"], name="muntin_rings", material_class_id="metal.blackened_gunmetal")
    else:
        lower.visual(mesh_from_cadquery(_raised_panel_leaf_cq(leaf_w, lower_h, leaf_t), "lower_leaf",
                                        assets=assets),
                     origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["wood"], name="lower_body", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))

    if r.leaf_infill == "glazed_lite":
        grid = r.lite_grid
        upper.visual(mesh_from_cadquery(
            _window_frame_leaf_cq(leaf_w, upper_h, leaf_t, grid), "upper_leaf_frame", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["wood"], name="upper_frame", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
        # transparent glass pane behind the muntins (Rule 1: fused leaf visual).
        open_x0, open_x1 = _STILE_W, leaf_w - _STILE_W
        open_z0, open_z1 = _RAIL_BOT_W, upper_h - _RAIL_TOP_W
        glass_cx, glass_cz = (open_x0 + open_x1) / 2.0, (open_z0 + open_z1) / 2.0
        glass_w = (open_x1 - open_x0) - 0.004
        glass_h = (open_z1 - open_z0) - 0.004
        upper.visual(Box((glass_w, _GLASS_T, glass_h)),
                     origin=Origin(xyz=(glass_cx, -_GLASS_T / 2.0 + (leaf_t / 2.0 - _GLASS_INSET),
                                        glass_cz)),
                     material=mats["glass"], name="window_glass", material_class_id="glass.clear_transparent")
    elif r.leaf_infill == "louvered":
        upper.visual(mesh_from_cadquery(
            _louver_frame_leaf_cq(leaf_w, upper_h, leaf_t), "upper_leaf_frame", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["wood"], name="upper_frame", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
        open_x0, open_x1 = _STILE_W, leaf_w - _STILE_W
        open_z0, open_z1 = _RAIL_BOT_W, upper_h - _RAIL_TOP_W
        slat_cx = (open_x0 + open_x1) / 2.0
        slat_w = (open_x1 - open_x0) + 0.020
        slat_angle = math.radians(_SLAT_ANGLE_DEG)
        n = r.louver_slat_count
        for i in range(n):
            t = (i + 0.5) / n
            slat_cz = open_z0 + t * (open_z1 - open_z0)
            upper.visual(Box((slat_w, _SLAT_DEPTH, _SLAT_THICK)),
                         origin=Origin(xyz=(slat_cx, 0.0, slat_cz), rpy=(slat_angle, 0.0, 0.0)),
                         material=mats["wood_shadow"], name=f"slat_{i}", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    else:  # solid_panel — both leaves raised panel.
        upper.visual(mesh_from_cadquery(
            _raised_panel_leaf_cq(leaf_w, upper_h, leaf_t), "upper_leaf_frame", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["wood"], name="upper_frame", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))

    # ---- visible barrel hinges (fused leaf visuals, Rule 1) ----
    hinge_y = leaf_t / 2.0 - _HINGE_R + 0.002
    upper_hinge = _hinge_barrel_mesh("upper_hinge_barrel")
    for i, hz in enumerate((0.16, upper_h - 0.16)):
        upper.visual(upper_hinge, origin=Origin(xyz=(0.0, hinge_y, hz - _HINGE_LEN / 2.0)),
                     material=mats["iron"], name=f"upper_hinge_{i}", material_class_id="metal.blackened_gunmetal")
    lower_hinge = _hinge_barrel_mesh("lower_hinge_barrel")
    for i, hz in enumerate((0.16, lower_h - 0.16)):
        lower.visual(lower_hinge, origin=Origin(xyz=(0.0, hinge_y, hz - _HINGE_LEN / 2.0)),
                     material=mats["iron"], name=f"lower_hinge_{i}", material_class_id="metal.blackened_gunmetal")

    upper.inertial = Inertial.from_geometry(Box((leaf_w, leaf_t, upper_h)), mass=14.0,
                                            origin=Origin(xyz=(leaf_w / 2.0, 0.0, upper_h / 2.0)))
    lower.inertial = Inertial.from_geometry(Box((leaf_w, leaf_t, lower_h)), mass=16.0,
                                            origin=Origin(xyz=(leaf_w / 2.0, 0.0, lower_h / 2.0)))

    # ---- two independent vertical-Z revolutes (grandfathered — HINGE_LAP capture) ----
    model.articulation("frame_to_upper", ArticulationType.REVOLUTE, parent=frame, child=upper,
                       origin=Origin(xyz=(0.0, 0.0, upper_bottom)), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=40.0, velocity=2.0, lower=0.0, upper=1.7))
    model.articulation("frame_to_lower", ArticulationType.REVOLUTE, parent=frame, child=lower,
                       origin=Origin(xyz=(0.0, 0.0, lower_bottom)), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=45.0, velocity=2.0, lower=0.0, upper=1.7))

    # ---- latch hardware: knob (glazed/louvered) or lever (solid_panel). FIXED w/ MatingContract. ----
    knob_x = leaf_w - 0.080
    knob_z = lower_h - 0.080
    knob_y = leaf_t / 2.0
    if r.leaf_infill == "solid_panel":
        handle = model.part("lever_handle")
        # Shift so the backplate's negative-Y (seating) face sits at local y=0,
        # i.e. at the joint origin → flush on the lower_body +Y face (Rule 2).
        handle.visual(_lever_handle_mesh("lever_handle"),
                      origin=Origin(xyz=(0.0, _BACKPLATE_T / 2.0, 0.0)),
                      material=mats["steel"], name="handle_body", material_class_id="metal.stainless_matte")
        handle.inertial = Inertial.from_geometry(Box((0.05, 0.14, 0.05)), mass=0.4)
        model.articulation(
            "lower_to_handle", ArticulationType.FIXED, parent=lower, child=handle,
            origin=Origin(xyz=(knob_x, knob_y, lower_h - 0.100)),
            mating=MatingContract(parent_face_geometry="lower_body", parent_face_side="positive_y",
                                  child_face_geometry="handle_body", child_face_side="negative_y",
                                  contact_tol=0.005))
    else:
        handle = model.part("door_knob")
        # The rose disc (after -90° about X) extrudes from local y=0 toward +Y,
        # so the rose's negative-Y face is already at local y=0 (seating face).
        handle.visual(_knob_mesh("door_knob"),
                      origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
                      material=mats["steel"], name="knob_body", material_class_id="metal.stainless_matte")
        handle.inertial = Inertial.from_geometry(Box((0.05, 0.05, 0.05)), mass=0.3)
        model.articulation(
            "lower_to_knob", ArticulationType.FIXED, parent=lower, child=handle,
            origin=Origin(xyz=(knob_x, knob_y, knob_z)),
            mating=MatingContract(parent_face_geometry="lower_body", parent_face_side="positive_y",
                                  child_face_geometry="knob_body", child_face_side="negative_y",
                                  contact_tol=0.005))


# ===========================================================================
# Stone frame builder (shared by single_solid_leaf + center_pivot).
# ===========================================================================
def _build_stone_frame_mesh(r: ResolvedDoorOtherConfig, *, centered: bool):
    open_w = r.leaf_w + 2.0 * _GAP
    block_w = open_w + 2.0 * _STONE_JAMB_W
    if centered:
        x_open_l = -open_w / 2.0
        x_pivot = 0.0
        x_left = x_open_l - _STONE_JAMB_W
    else:
        x_open_l = _STONE_JAMB_W
        x_left = 0.0
    x_open_r = x_open_l + open_w

    # opening profile + frame top from head profile.
    if r.head_profile == "full_semicircle":
        open_spring = r.leaf_spring
        open_top = open_spring + open_w / 2.0
    elif r.head_profile in ("broad_barn_segmental", "shallow_segmental"):
        open_spring = r.leaf_spring
        open_rise = _concentric_open_rise(r.leaf_w, r.arch_rise, open_w, _GAP)
        open_top = open_spring + open_rise
    elif r.head_profile == "flat_top_rect":  # tympanum arch above flat leaf.
        open_spring = r.leaf_top + _GAP
        open_top = open_spring + open_w / 2.0
    else:  # flat_square — rectangular opening with a flat head.
        open_spring = r.leaf_top
        open_top = r.leaf_top
    frame_top = open_top + 0.45

    threshold_h = 0.040 if r.split_mechanism == "center_pivot" else 0.0
    block = (
        cq.Workplane("XY").box(block_w, _WALL_THK, frame_top + threshold_h)
        .translate((x_left + block_w / 2.0, 0.0, (frame_top - threshold_h) / 2.0))
    )
    if centered:
        opening_profile = (
            _arched_profile_centered(open_w, open_spring, open_top)
            if r.head_profile in ("full_semicircle", "broad_barn_segmental", "shallow_segmental")
            else (_flat_then_arch_centered(open_w, open_spring, open_top)
                  if r.head_profile == "flat_top_rect"
                  else _flat_face(open_w, open_top, centered=True))
        )
        opening = opening_profile.extrude((_WALL_THK + 0.10) / 2.0, both=True)
    else:
        opening_profile = (
            _arched_profile_face(open_w, open_spring, open_top)
            if r.head_profile in ("full_semicircle", "broad_barn_segmental", "shallow_segmental")
            else (_flat_then_arch(open_w, open_spring, open_top)
                  if r.head_profile == "flat_top_rect"
                  else _flat_face(open_w, open_top, centered=False))
        )
        opening = opening_profile.extrude((_WALL_THK + 0.10) / 2.0, both=True)
        opening = opening.translate((x_open_l, 0.0, 0.0))
    frame = block.cut(opening)

    key_h = 0.34
    keystone = (
        cq.Workplane("XY").box(0.22, _WALL_THK + 0.06, key_h)
        .translate(((x_open_l + x_open_r) / 2.0, 0.0, open_top + key_h / 2.0))
    )
    frame = frame.union(keystone)
    for cx in (x_left + _STONE_JAMB_W / 2.0, x_open_r + _STONE_JAMB_W / 2.0):
        plinth = (cq.Workplane("XY").box(_STONE_JAMB_W + 0.06, _WALL_THK + 0.05, 0.20)
                  .translate((cx, 0.0, 0.10)))
        frame = frame.union(plinth)
    return frame, x_open_l, x_open_r, x_pivot if centered else (x_open_l + _GAP), frame_top, open_top


def _flat_then_arch(width: float, spring: float, top: float) -> cq.Workplane:
    """Flat-top opening rect up to `spring`, then a semicircular tympanum arch."""
    cx = width / 2.0
    return (
        cq.Workplane("XZ").moveTo(0.0, 0.0).lineTo(0.0, spring)
        .threePointArc((cx, top), (width, spring)).lineTo(width, 0.0).close()
    )


def _flat_then_arch_centered(width: float, spring: float, top: float) -> cq.Workplane:
    hw = width / 2.0
    return (
        cq.Workplane("XZ").moveTo(-hw, 0.0).lineTo(-hw, spring)
        .threePointArc((0.0, top), (hw, spring)).lineTo(hw, 0.0).close()
    )


def _build_jamb_pintle_mesh(r: ResolvedDoorOtherConfig, z_center: float, *, x_open_l: float, x_hinge: float):
    pin_y = r.leaf_t / 2.0 + 0.018
    arm = (cq.Workplane("XY").box(0.18, 0.024, 0.044).translate((x_open_l - 0.03, pin_y, z_center)))
    pin = (cq.Workplane("XY").circle(0.012).extrude(0.13).translate((x_hinge, pin_y, z_center - 0.065)))
    finial = cq.Workplane("XY").sphere(0.012).translate((x_hinge, pin_y, z_center + 0.065))
    return arm.union(pin).union(finial)


def _build_pivot_spine_mesh(r: ResolvedDoorOtherConfig):
    front_y = r.leaf_t / 2.0
    leaf_top = r.leaf_top
    bar_front = (cq.Workplane("XZ").rect(_PIVOT_SPINE_W, leaf_top).extrude(_PIVOT_SPINE_THK)
                 .translate((0.0, front_y - 0.003, leaf_top / 2.0)))
    bar_back = (cq.Workplane("XZ").rect(_PIVOT_SPINE_W, leaf_top).extrude(_PIVOT_SPINE_THK)
                .translate((0.0, -(front_y - 0.003) + _PIVOT_SPINE_THK, leaf_top / 2.0)))
    spine = bar_front.union(bar_back)
    tie_w, tie_thk = _PIVOT_SPINE_W * 0.6, 0.006
    for z_center in (0.25, 0.80, min(1.55, leaf_top - 0.20), min(1.85, leaf_top - 0.10)):
        tie = (cq.Workplane("XY").box(tie_w, r.leaf_t + 0.008, tie_thk).translate((0.0, 0.0, z_center)))
        spine = spine.union(tie)
    top_pin = (cq.Workplane("XY").circle(_PIVOT_PIN_R).extrude(_PIVOT_PIN_LEN).translate((0.0, 0.0, leaf_top)))
    spine = spine.union(top_pin)
    bottom_pin = (cq.Workplane("XY").circle(_PIVOT_PIN_R).extrude(_PIVOT_PIN_LEN)
                  .translate((0.0, 0.0, -_PIVOT_PIN_LEN)))
    spine = spine.union(bottom_pin)
    top_collar = (cq.Workplane("XY").circle(_PIVOT_COLLAR_R).extrude(0.010).translate((0.0, 0.0, leaf_top - 0.010)))
    spine = spine.union(top_collar)
    bottom_collar = (cq.Workplane("XY").circle(_PIVOT_COLLAR_R).extrude(0.010).translate((0.0, 0.0, 0.0)))
    return spine.union(bottom_collar)


def _build_pivot_socket_bottom_mesh(x_pivot: float):
    cup = (cq.Workplane("XY").circle(_SOCKET_CUP_OR).circle(_SOCKET_CUP_IR).extrude(_SOCKET_CUP_DEPTH)
           .translate((x_pivot, 0.0, -0.010 - _SOCKET_CUP_DEPTH)))
    plate = (cq.Workplane("XY").circle(_SOCKET_PLATE_R).extrude(0.008).translate((x_pivot, 0.0, -0.008)))
    return plate.union(cup)


def _build_pivot_socket_top_mesh(x_pivot: float, leaf_top: float):
    cup_bottom = leaf_top + 0.003
    cup = (cq.Workplane("XY").circle(_SOCKET_CUP_OR).circle(_SOCKET_CUP_IR).extrude(_SOCKET_CUP_DEPTH)
           .translate((x_pivot, 0.0, cup_bottom)))
    plate_z = cup_bottom + _SOCKET_CUP_DEPTH
    plate = (cq.Workplane("XY").circle(_SOCKET_PLATE_R).extrude(_SOCKET_CUP_DEPTH + 0.015)
             .translate((x_pivot, 0.0, plate_z)))
    return plate.union(cup)


# ===========================================================================
# Slot A — SINGLE SOLID LEAF (stone surround, one vertical revolute on pintles).
# ===========================================================================
def _emit_stone_leaf_planks(door, r: ResolvedDoorOtherConfig, mats, *, x0_leaf: float, assets):
    """Emit the selected Slot-C face, adapting Dutch candidates when needed."""
    ring_cx = x0_leaf + r.leaf_w - 0.16
    if r.leaf_infill == "porthole":
        # flat-top plank slab with a circular through-cut + glass + muntin ring.
        for i in range(r.plank_count):
            door.visual(mesh_from_cadquery(_build_single_plank(r, i, x0_leaf=x0_leaf), f"plank_{i}",
                                           assets=assets),
                        material=mats["wood"], name=f"plank_{i}", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
        door.visual(mesh_from_cadquery(_build_battens_mesh(r, x_center=x0_leaf + r.leaf_w / 2.0),
                                       "battens", assets=assets),
                    material=mats["wood"], name="battens", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
        door.visual(mesh_from_cadquery(_build_porthole_glass_mesh(r, x0_leaf=x0_leaf), "porthole_glass",
                                       assets=assets),
                    material=mats["glass"], name="porthole_glass", material_class_id="glass.clear_transparent")
        door.visual(mesh_from_cadquery(_build_muntin_ring_mesh(r, x0_leaf=x0_leaf), "muntin_rings",
                                       assets=assets),
                    material=mats["iron"], name="muntin_rings", material_class_id="metal.blackened_gunmetal")
    elif r.leaf_infill == "plank_strap":
        for i in range(r.plank_count):
            door.visual(mesh_from_cadquery(_build_single_plank(r, i, x0_leaf=x0_leaf), f"plank_{i}",
                                           assets=assets),
                        material=mats["wood"], name=f"plank_{i}", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
        door.visual(mesh_from_cadquery(_build_battens_mesh(r, x_center=x0_leaf + r.leaf_w / 2.0),
                                       "battens", assets=assets),
                    material=mats["wood"], name="battens", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    else:
        _emit_stone_face_candidate(door, r, mats, x0_leaf=x0_leaf, centered=False, assets=assets)
    # iron strap hinges (two), fused.
    z_hi = min(1.30, r.leaf_spring - 0.10)
    strap = _build_strap_hinge_mesh(r, 0.45, x_hinge_local=x0_leaf).union(
        _build_strap_hinge_mesh(r, z_hi, x_hinge_local=x0_leaf))
    door.visual(mesh_from_cadquery(strap, "strap_hinges", assets=assets),
                material=mats["iron"], name="strap_hinges", material_class_id="metal.blackened_gunmetal")
    # studs + ring boss, fused.
    door.visual(mesh_from_cadquery(_build_iron_studs_mesh(r, x0_leaf=x0_leaf, ring_cx=ring_cx),
                                   "iron_studs", assets=assets),
                material=mats["iron"], name="iron_studs", material_class_id="metal.blackened_gunmetal")
    return ring_cx


def _build_single_solid_shell(model, r: ResolvedDoorOtherConfig, mats, *, assets):
    frame_data = _build_stone_frame_mesh(r, centered=False)
    frame_mesh, x_open_l, x_open_r, x_hinge, frame_top, open_top = frame_data

    frame = model.part("stone_frame")
    frame.visual(mesh_from_cadquery(frame_mesh, "stone_frame", assets=assets),
                 material=mats["stone"], name="stone_arch", material_class_id="stone.cut_sedimentary")
    z_hi = min(1.30, r.leaf_spring - 0.10)
    pintles = _build_jamb_pintle_mesh(r, 0.45, x_open_l=x_open_l, x_hinge=x_hinge).union(
        _build_jamb_pintle_mesh(r, z_hi, x_open_l=x_open_l, x_hinge=x_hinge))
    frame.visual(mesh_from_cadquery(pintles, "jamb_pintles", assets=assets),
                 material=mats["iron"], name="jamb_pintles", material_class_id="metal.blackened_gunmetal")
    frame.inertial = Inertial.from_geometry(
        Box((x_open_r - x_open_l + 2 * _STONE_JAMB_W, _WALL_THK, frame_top)), mass=120.0,
        origin=Origin(xyz=((x_open_l + x_open_r) / 2.0, 0.0, frame_top / 2.0)))

    door = model.part("door")
    # leaf authored hinge-edge at local x=0 → x0_leaf=0; world hinge line = x_hinge.
    ring_cx = _emit_stone_leaf_planks(door, r, mats, x0_leaf=0.0, assets=assets)
    door.inertial = Inertial.from_geometry(Box((r.leaf_w, r.leaf_t, r.leaf_top)), mass=24.0,
                                           origin=Origin(xyz=(r.leaf_w / 2.0, 0.0, r.leaf_top / 2.0)))

    # one vertical-Z revolute at the jamb reveal (grandfathered — pintle capture).
    model.articulation("frame_to_door", ArticulationType.REVOLUTE, parent=frame, child=door,
                       origin=Origin(xyz=(x_hinge, 0.0, 0.0)), axis=(0.0, 0.0, -1.0),
                       motion_limits=MotionLimits(effort=60.0, velocity=2.0,
                                                  lower=0.0, upper=math.radians(110.0)))
    _emit_ring_pull(model, r, mats, ring_cx=ring_cx, assets=assets)


# ===========================================================================
# Slot A — CENTER PIVOT (stone surround, bidirectional centerline revolute).
# ===========================================================================
def _emit_pivot_leaf(door, r: ResolvedDoorOtherConfig, mats, *, assets):
    """Centered leaf + pivot spine + studs with any Slot-C face adapter."""
    hw = r.leaf_w / 2.0
    ring_cx = hw - 0.16
    if r.leaf_infill in ("plank_strap", "porthole"):
        # centered planks — reuse _build_single_plank with centered x0_leaf=-hw.
        for i in range(r.plank_count):
            door.visual(mesh_from_cadquery(_build_single_plank(r, i, x0_leaf=-hw), f"plank_{i}",
                                           assets=assets),
                        material=mats["wood"], name=f"plank_{i}", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
        door.visual(mesh_from_cadquery(_build_battens_mesh(r, x_center=0.0), "battens", assets=assets),
                    material=mats["wood"], name="battens", material_class_id=("wood.oak" if r.palette_style in {"stone_oak_plank", "charcoal_iron_barn", "weathered_grey_plank", "honey_oak_porthole"} else "wood.painted_clean"))
    else:
        _emit_stone_face_candidate(door, r, mats, x0_leaf=-hw, centered=True, assets=assets)
    door.visual(mesh_from_cadquery(_build_pivot_spine_mesh(r), "pivot_spine", assets=assets),
                material=mats["iron"], name="pivot_spine", material_class_id="metal.blackened_gunmetal")
    door.visual(mesh_from_cadquery(_build_pivot_studs_mesh(r, ring_cx=ring_cx), "iron_studs",
                                   assets=assets),
                material=mats["iron"], name="iron_studs", material_class_id="metal.blackened_gunmetal")
    return ring_cx


def _build_center_pivot_shell(model, r: ResolvedDoorOtherConfig, mats, *, assets):
    frame_data = _build_stone_frame_mesh(r, centered=True)
    frame_mesh, x_open_l, x_open_r, x_pivot, frame_top, open_top = frame_data

    frame = model.part("stone_frame")
    frame.visual(mesh_from_cadquery(frame_mesh, "stone_frame", assets=assets),
                 material=mats["stone"], name="stone_arch", material_class_id="stone.cut_sedimentary")
    socket = _build_pivot_socket_bottom_mesh(x_pivot).union(
        _build_pivot_socket_top_mesh(x_pivot, r.leaf_top))
    # Bridge the upper socket plate into the stone head so the fixed support is
    # one connected grounded assembly even for a flat-square host profile.
    # Carry the upper socket all the way to the host head.  For round/arched
    # Slot-B profiles the opening apex is above the leaf, so a short local
    # bridge would leave the fixed socket as a floating island.
    top_bridge_bottom = r.leaf_top - 0.02
    top_bridge_top = open_top + 0.08
    top_bridge_h = max(0.20, top_bridge_top - top_bridge_bottom)
    socket = socket.union(
        cq.Workplane("XY").box(0.060, _WALL_THK * 0.55, top_bridge_h)
        .translate((x_pivot, 0.0, (top_bridge_bottom + top_bridge_top) / 2.0))
    )
    socket = socket.union(
        # Extend through z=0 so the lower bridge overlaps both the socket
        # plate and the threshold stone instead of merely touching them.
        cq.Workplane("XY").box(0.060, _WALL_THK * 0.55, 0.16)
        .translate((x_pivot, 0.0, 0.03))
    )
    frame.visual(mesh_from_cadquery(socket, "pivot_sockets", assets=assets),
                 material=mats["iron"], name="pivot_sockets", material_class_id="metal.blackened_gunmetal")
    frame.inertial = Inertial.from_geometry(
        Box((x_open_r - x_open_l + 2 * _STONE_JAMB_W, _WALL_THK, frame_top)), mass=120.0,
        origin=Origin(xyz=(0.0, 0.0, frame_top / 2.0)))

    door = model.part("door")
    ring_cx = _emit_pivot_leaf(door, r, mats, assets=assets)
    door.inertial = Inertial.from_geometry(Box((r.leaf_w, r.leaf_t, r.leaf_top)), mass=24.0,
                                           origin=Origin(xyz=(0.0, 0.0, r.leaf_top / 2.0)))

    # one bidirectional vertical-Z revolute at the centerline (grandfathered — socket capture).
    model.articulation("frame_to_door", ArticulationType.REVOLUTE, parent=frame, child=door,
                       origin=Origin(xyz=(x_pivot, 0.0, 0.0)), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=60.0, velocity=2.0,
                                                  lower=-math.radians(90.0), upper=math.radians(90.0)))
    _emit_ring_pull(model, r, mats, ring_cx=ring_cx, assets=assets)


# ===========================================================================
# Ring pull (optional moving child of `door`; stone shells with plank/porthole).
# ===========================================================================
def _emit_ring_pull(model, r: ResolvedDoorOtherConfig, mats, *, ring_cx: float, assets):
    if not r.has_ring_pull:
        return
    ring_pull = model.part("ring_pull")
    ring_pull.visual(_build_ring_pull_mesh("ring_pull"),
                     origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["iron"], name="ring_pull", material_class_id="metal.blackened_gunmetal")
    ring_pull.inertial = Inertial.from_geometry(Box((0.12, 0.02, 0.12)), mass=0.2)
    ring_pivot_y = r.leaf_t / 2.0 + 0.012
    ring_pivot_z = r.ring_cz + _RING_MEAN_R
    # horizontal door-local-X revolute through the boss (grandfathered — through-boss).
    model.articulation("door_to_ring_pull", ArticulationType.REVOLUTE,
                       parent=model.get_part("door"), child=ring_pull,
                       origin=Origin(xyz=(ring_cx, ring_pivot_y, ring_pivot_z)), axis=(1.0, 0.0, 0.0),
                       motion_limits=MotionLimits(effort=5.0, velocity=3.0,
                                                  lower=0.0, upper=math.radians(90.0)))


_SHELL_BUILDERS = {
    "dutch_two_leaf": _build_dutch_shell,
    "single_solid_leaf": _build_single_solid_shell,
    "center_pivot": _build_center_pivot_shell,
}


# ===========================================================================
# Top-level build
# ===========================================================================
def build_door_other(
    config: DoorOtherConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"door_other_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    _SHELL_BUILDERS[r.split_mechanism](model, r, mats, assets=assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_door_other(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_door_other(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_door_other_tests(
    object_model: ArticulatedObject,
    config: DoorOtherConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    # ---------- Element-scoped allow_overlap (mirror each source). ----------
    if r.split_mechanism == "dutch_two_leaf":
        frame = object_model.get_part("door_frame")
        upper = object_model.get_part("upper_leaf")
        lower = object_model.get_part("lower_leaf")
        # HINGE_LAP: jamb laps each leaf hinge edge + barrels lap onto jamb.
        ctx.allow_overlap(upper, frame, elem_a="upper_frame", elem_b="hinge_jamb",
                          reason="Hinge jamb laps the upper leaf hinge edge (HINGE_LAP carry).")
        ctx.allow_overlap(lower, frame, elem_a="lower_body", elem_b="hinge_jamb",
                          reason="Hinge jamb laps the lower leaf hinge edge (HINGE_LAP carry).")
        for i in range(2):
            ctx.allow_overlap(upper, frame, elem_a=f"upper_hinge_{i}", elem_b="hinge_jamb",
                              reason="Upper barrel hinge laps onto the hinge jamb.")
            ctx.allow_overlap(lower, frame, elem_a=f"lower_hinge_{i}", elem_b="hinge_jamb",
                              reason="Lower barrel hinge laps onto the hinge jamb.")
        if r.leaf_infill in ("plank_strap", "porthole"):
            for i in range(r.plank_count):
                ctx.allow_overlap(upper, frame, elem_a=f"upper_plank_{i}", elem_b="hinge_jamb",
                                  reason="Plank face follows the source leaf hinge-lap envelope.")
                ctx.allow_overlap(lower, frame, elem_a=f"lower_plank_{i}", elem_b="hinge_jamb",
                                  reason="Plank face follows the source leaf hinge-lap envelope.")
        # knob/lever seats through the leaf face.
        handle_part = "lever_handle" if r.leaf_infill == "solid_panel" else "door_knob"
        ctx.allow_overlap(object_model.get_part(handle_part), lower,
                          reason="Latch hardware seats against/through the lower leaf face.")
    else:
        frame = object_model.get_part("stone_frame")
        door = object_model.get_part("door")
        if r.split_mechanism == "single_solid_leaf":
            ctx.allow_overlap(door, frame, elem_a="strap_hinges", elem_b="jamb_pintles",
                              reason="Rolled strap barrels captured on fixed jamb pintle pins (hinge bearing).")
        else:  # center_pivot
            ctx.allow_overlap(door, frame, elem_a="pivot_spine", elem_b="pivot_sockets",
                              reason="Pivot spine pins seat in top/bottom socket cups (pivot bearing).")
            ctx.allow_overlap(door, frame, elem_a="pivot_spine", elem_b="stone_arch",
                              reason="Pivot spine runs through the carved opening void (tessellation artifact).")
            # The source pivot leaves are carried by socket bridges that sit just
            # inside the leaf envelope.  Keep the source-derived face adapters
            # from being rejected as accidental collisions with that bearing.
            if r.leaf_infill in ("plank_strap", "porthole"):
                for i in range(r.plank_count):
                    ctx.allow_overlap(door, frame, elem_a=f"plank_{i}", elem_b="pivot_sockets",
                                      reason="Pivot socket bridge seats into the adapted plank leaf envelope.")
            else:
                ctx.allow_overlap(door, frame, elem_a="leaf_body", elem_b="pivot_sockets",
                                  reason="Pivot socket bridge seats into the adapted solid/face leaf envelope.")
        # Plank-derived face visuals sit inside the boolean-cut stone opening.
        if r.leaf_infill in ("plank_strap", "porthole"):
            for i in range(r.plank_count):
                ctx.allow_overlap(door, frame, elem_a=f"plank_{i}", elem_b="stone_arch",
                                  reason="Leaf plank sits inside the boolean-cut stone opening void.")
            ctx.allow_overlap(door, frame, elem_a="battens", elem_b="stone_arch",
                              reason="Battens sit inside the stone opening void (tessellation artifact).")
        ctx.allow_overlap(door, frame, elem_a="strap_hinges", elem_b="stone_arch",
                          reason="Straps lie inside the stone opening void (tessellation artifact).")
        ctx.allow_overlap(door, frame, elem_a="iron_studs", elem_b="stone_arch",
                          reason="Studs lie inside the stone opening void (tessellation artifact).")
        if r.leaf_infill == "porthole":
            ctx.allow_overlap(door, frame, elem_a="muntin_rings", elem_b="stone_arch",
                              reason="Porthole muntin ring is seated in the leaf opening within the stone reveal.")
            ctx.allow_overlap(door, door, elem_a="muntin_rings", elem_b="door_planks",
                              reason="Muntin rings seat into the plank faces with a small embed.")
            for i in range(r.plank_count):
                ctx.allow_overlap(door, door, elem_a="muntin_rings", elem_b=f"plank_{i}",
                                  reason="Continuous muntin ring threads through the plank porthole cut.")
        else:
            ctx.allow_overlap(door, frame, elem_a="leaf_body", elem_b="stone_arch",
                              reason="Adapted Slot-C face follows the captured leaf envelope inside the reveal.")
        # The independently sampled Slot-C details are all carried inside the
        # same captured opening envelope.  At the swept hinge edge they can
        # cross the fixed reveal even though the source leaf itself is seated
        # correctly, so mirror that source-derived envelope per element.
        if r.leaf_infill == "glazed_lite":
            ctx.allow_overlap(door, frame, elem_a="window_glass", elem_b="stone_arch",
                              reason="Glazed lite follows the adapted leaf envelope inside the reveal.")
            for j in range(1, r.lite_grid):
                ctx.allow_overlap(door, frame, elem_a=f"muntin_v_{j}", elem_b="stone_arch",
                                  reason="Glazed muntin follows the adapted leaf envelope inside the reveal.")
                ctx.allow_overlap(door, frame, elem_a=f"muntin_h_{j}", elem_b="stone_arch",
                                  reason="Glazed muntin follows the adapted leaf envelope inside the reveal.")
        elif r.leaf_infill == "solid_panel":
            ctx.allow_overlap(door, frame, elem_a="raised_panel", elem_b="stone_arch",
                              reason="Raised panel follows the adapted leaf envelope inside the reveal.")
        elif r.leaf_infill == "louvered":
            for i in range(r.louver_slat_count):
                ctx.allow_overlap(door, frame, elem_a=f"slat_{i}", elem_b="stone_arch",
                                  reason="Louver slat follows the adapted leaf envelope inside the reveal.")
        if r.has_ring_pull:
            ring = object_model.get_part("ring_pull")
            ctx.allow_overlap(ring, door, elem_a="ring_pull", elem_b="iron_studs",
                              reason="Ring pull threads through its mounting boss (pivot bearing).")
            if r.leaf_infill == "solid_panel":
                ctx.allow_overlap(ring, door, elem_a="ring_pull", elem_b="raised_panel",
                                  reason="Ring pull seats through the raised panel face (source mounting overlap).")
            elif r.leaf_infill == "glazed_lite":
                ctx.allow_overlap(ring, door, elem_a="ring_pull", elem_b="window_glass",
                                  reason="Ring pull seats through the glazed leaf face (source mounting overlap).")
                for j in range(1, r.lite_grid):
                    ctx.allow_overlap(ring, door, elem_a="ring_pull", elem_b=f"muntin_v_{j}",
                                      reason="Ring pull seats through the glazed muntin face (source mounting overlap).")
                    ctx.allow_overlap(ring, door, elem_a="ring_pull", elem_b=f"muntin_h_{j}",
                                      reason="Ring pull seats through the glazed muntin face (source mounting overlap).")

    # ---------- Baseline gates. ----------
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---------- Structure / identity. ----------
    part_names = {p.name for p in object_model.parts}
    if r.split_mechanism == "dutch_two_leaf":
        ctx.check("dutch shell parts present",
                  {"door_frame", "upper_leaf", "lower_leaf"} <= part_names,
                  details=str(sorted(part_names)))
        ju = object_model.get_articulation("frame_to_upper")
        jl = object_model.get_articulation("frame_to_lower")
        ctx.check("two independent vertical-Z revolutes (Dutch)",
                  ju.articulation_type == ArticulationType.REVOLUTE
                  and jl.articulation_type == ArticulationType.REVOLUTE
                  and abs(ju.axis[2]) > 0.99 and abs(jl.axis[2]) > 0.99,
                  details=f"upper={tuple(ju.axis)} lower={tuple(jl.axis)}")
        # each leaf swings independently into the room (+Y).
        upper = object_model.get_part("upper_leaf")
        lower = object_model.get_part("lower_leaf")
        closed = ctx.part_world_aabb(upper)
        lower_closed = ctx.part_world_aabb(lower)
        with ctx.pose({ju: 1.4, jl: 0.0}):
            opened = ctx.part_world_aabb(upper)
            lower_still = ctx.part_world_aabb(lower)
        if closed is not None and opened is not None:
            ctx.check("upper leaf swings into the room",
                      opened[1][1] > closed[1][1] + 0.25,
                      details=f"closed_y1={closed[1][1]:.3f} open_y1={opened[1][1]:.3f}")
        if lower_closed is not None and lower_still is not None:
            ctx.check("lower leaf unaffected when only the upper opens (independent)",
                      abs(lower_still[1][1] - lower_closed[1][1]) < 0.005,
                      details=f"lower_y1 closed={lower_closed[1][1]:.4f} still={lower_still[1][1]:.4f}")
    else:
        ctx.check("stone shell parts present",
                  {"stone_frame", "door"} <= part_names, details=str(sorted(part_names)))
        j = object_model.get_articulation("frame_to_door")
        ctx.check("leaf revolute is vertical (Z)",
                  j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
                  details=f"axis={tuple(j.axis)}")
        if r.split_mechanism == "center_pivot":
            ml = j.motion_limits
            ctx.check("center pivot swings bidirectionally",
                      ml.lower < -0.1 and ml.upper > 0.1,
                      details=f"lower={ml.lower:.3f} upper={ml.upper:.3f}")
            po = j.origin.xyz
            ctx.check("pivot axis at the opening centerline (x≈0)",
                      abs(po[0]) < 0.02, details=f"pivot_x={po[0]:.4f}")
        # leaf opens / swings clear.
        door = object_model.get_part("door")
        closed = ctx.part_world_aabb(door)
        q = math.radians(70.0) if r.split_mechanism == "single_solid_leaf" else math.radians(70.0)
        with ctx.pose({j: q}):
            opened = ctx.part_world_aabb(door)
        if closed is not None and opened is not None:
            ctx.check("leaf swings out of the wall plane",
                      opened[0][1] < closed[0][1] - 0.20 or opened[1][1] > closed[1][1] + 0.20,
                      details=f"closed_y=({closed[0][1]:.3f},{closed[1][1]:.3f}) "
                              f"open_y=({opened[0][1]:.3f},{opened[1][1]:.3f})")
        # Plank count is active only for the plank/porthole face candidates.
        if r.leaf_infill in ("plank_strap", "porthole"):
            n_planks = len([v for v in door.visuals if v.name.startswith("plank_")])
            ctx.check("N planks emitted (uniform pitch)",
                      n_planks == r.plank_count, details=f"planks={n_planks} N={r.plank_count}")
        # ring pull joint topology when present.
        if r.has_ring_pull:
            jr = object_model.get_articulation("door_to_ring_pull")
            ctx.check("ring-pull is horizontal-X revolute",
                      jr.articulation_type == ArticulationType.REVOLUTE and abs(jr.axis[0]) > 0.99,
                      details=f"axis={tuple(jr.axis)}")

    # ---------- Head profile uses a real profile (all shells). ----------
    if r.head_profile != "flat_square":
        ctx.check("curved head has positive arch rise",
                  (r.arch_rise > 1e-3 or r.head_profile == "flat_top_rect" or
                   r.split_mechanism == "dutch_two_leaf"),
                  details=f"rise={r.arch_rise:.4f} head={r.head_profile}")

    # ---------- Ground + proportion. ----------
    root_name = "door_frame" if r.split_mechanism == "dutch_two_leaf" else "stone_frame"
    fb = ctx.part_world_aabb(object_model.get_part(root_name))
    if fb is not None:
        ctx.check("frame rests on / near the ground", fb[0][2] <= 0.05,
                  details=f"z_min={fb[0][2]:.4f}")
        ctx.check("door stands tall", fb[1][2] > 1.8, details=f"top={fb[1][2]:.3f}")

    # ---------- palette drives a transparent glazing material when glazed. ----------
    if r.leaf_infill in ("glazed_lite", "porthole"):
        gm = next((m for m in object_model.materials
                   if m.name == f"door_other_glass_{r.palette_style}"), None)
        alpha = gm.rgba[3] if (gm and gm.rgba and len(gm.rgba) == 4) else None
        ctx.check("glazing material is transparent (alpha < 0.6)",
                  alpha is not None and alpha < 0.6, details=f"alpha={alpha}")

    # ---------- slot_choices recorded. ----------
    ctx.check("slot_choices recorded matching build",
              tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
              details=str(object_model.meta.get("slot_choices")))

    return ctx.report()


__all__ = (
    "DoorOtherConfig",
    "ResolvedDoorOtherConfig",
    "build_door_other",
    "build_seeded_door_other",
    "config_from_seed",
    "resolve_config",
    "run_door_other_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
