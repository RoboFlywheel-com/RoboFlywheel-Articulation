# SPDX-License-Identifier: Apache-2.0

"""Double door modular template.

A **double door** is a fixed frame/surround root carrying TWO mirror-symmetric
operable leaves that meet at a central reveal. Authored from the reviewed modular
spec ``articraft_template_authoring/specs_modular_v1/Door_Double_Door.md`` and the 14
5-star ``double_door`` records (6 parents + 8 slot-fork variants), all synced under
``data/records/``.

Structure (pattern = ``mixed``): a single root ``frame`` part (two jambs + head
member [Slot B] + base/threshold + doorstop beads) with two mirror leaves
attaching as parallel children via two mirrored REVOLUTE / SPRING hinges (the
spine), and per-leaf infill that is itself a multiplicity of stacked panels /
divided lites / louver slats / boards [Slot A multiplicity axes].

Three slots (2-8 candidates each):

  * ``infill_style`` (Slot A, 8): the replaceable structural/visual content of one
    leaf, mirrored to the other --- raised_panel / vision_window_pushbar /
    carved_circle_motif / upper_glass_muntin_lower_xbrace / louvered_slat /
    full_glass_single_pane / divided_lite_glass / cross_buck_board. Each has a
    distinct part-tree / cut-union topology. Four of them carry a variable
    multiplicity (panel_count / lite grid / slat_count / board_count) loop-emitted
    via a shared per-feature helper.
  * ``head_style`` (Slot B, 6): where the arch/crown/transom lives ---
    flat_head / arched_stone_head / scalloped_crown_head / transom_over_flat_head
    / arched_leaf_top / solid_semicircle_head. flat/stone/transom/solid-semicircle
    heads are FRAME-surround members;
    scalloped_crown + arched_leaf_top reprofile the LEAF body (arched_leaf_top also
    adds a matching frame ring header on the SAME circle).
  * ``swing_mode`` (Slot C, 2): both_revolute_opposite (2 REVOLUTE +Z/-Z),
    double_acting_spring (2 REVOLUTE both +Z, symmetric +/-limits, rest 0).
    Both modes always keep two independent operable leaves. The former
    ``active_inactive_astragal`` input is accepted only as a backward-compatible
    alias for ``both_revolute_opposite``.

All hinge hardware is captured-pin geometry, so the spine hinge joints omit
``MatingContract`` (grandfathered, guarded by the flat articulation-origin
baseline + element-scoped ``allow_overlap``). The per-leaf lever sub-joint
(optional, hardware-bearing wood leaves) declares a MatingContract on the rose
collar (Rule 2).

Compatibility gating (resolve_config, spec compatibility matrix):
  * ``arched_leaf_top`` (LEAF arch) excludes ``arched_stone_head`` /
    ``transom_over_flat_head`` (FRAME arches) and ``scalloped_crown_head`` (a
    second LEAF head) --- it is forced to pair with ``flat_head``.
  * ``scalloped_crown_head`` (batwing short leaf) requires a reprofile-friendly
    infill --- restricted to louvered_slat / full_glass_single_pane.
  * ``arched_leaf_top`` requires a glass-pane infill (full_glass_single_pane /
    divided_lite_glass) so the leaf arch reads as one glazed arched opening.
  * ``arched_leaf_top`` resolves to the outward-only paired hinge mode: an inward
    double-action sweep would carry the tall curved cap through the fixed arch.
  * the per-leaf lever sub-joint is only added on solid wood infills with a
    meeting stile (raised_panel / cross_buck_board) and only in revolute modes.
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

InfillStyle = Literal[
    "raised_panel",
    "vision_window_pushbar",
    "carved_circle_motif",
    "upper_glass_muntin_lower_xbrace",
    "louvered_slat",
    "full_glass_single_pane",
    "divided_lite_glass",
    "cross_buck_board",
]
HeadStyle = Literal[
    "flat_head",
    "arched_stone_head",
    "scalloped_crown_head",
    "transom_over_flat_head",
    "arched_leaf_top",
    "solid_semicircle_head",
]
SwingMode = Literal[
    "both_revolute_opposite",
    "double_acting_spring",
    "active_inactive_astragal",
]
PaletteStyle = Literal[
    "dark_walnut",
    "honey_brown_wood",
    "warm_wood_stone",
    "off_white_steel",
    "anodized_aluminum",
    "wrought_iron_oak",
]

INFILL_STYLES: tuple[InfillStyle, ...] = (
    "raised_panel",
    "vision_window_pushbar",
    "carved_circle_motif",
    "upper_glass_muntin_lower_xbrace",
    "louvered_slat",
    "full_glass_single_pane",
    "divided_lite_glass",
    "cross_buck_board",
)
HEAD_STYLES: tuple[HeadStyle, ...] = (
    "flat_head",
    "arched_stone_head",
    "scalloped_crown_head",
    "transom_over_flat_head",
    "arched_leaf_top",
    "solid_semicircle_head",
)
SWING_MODES: tuple[SwingMode, ...] = (
    "both_revolute_opposite",
    "double_acting_spring",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "dark_walnut",
    "honey_brown_wood",
    "warm_wood_stone",
    "off_white_steel",
    "anodized_aluminum",
    "wrought_iron_oak",
)

# --- Slot A multiplicity axes (only the matching *_count is live). ---
PANEL_MIN, PANEL_MAX = 1, 6
LITE_ROW_MIN, LITE_ROW_MAX = 1, 4
LITE_COL_MIN, LITE_COL_MAX = 1, 3
SLAT_MIN, SLAT_MAX = 8, 28
BOARD_MIN, BOARD_MAX = 4, 9

# Weighted small-N draws (spec Multiplicity sampling domain).
PANEL_CHOICES = (1, 2, 3, 4, 5, 6)
PANEL_WEIGHTS = (0.10, 0.26, 0.30, 0.18, 0.10, 0.06)
LITE_ROW_CHOICES = (1, 2, 3, 4)
LITE_ROW_WEIGHTS = (0.20, 0.45, 0.25, 0.10)
LITE_COL_CHOICES = (1, 2, 3)
LITE_COL_WEIGHTS = (0.25, 0.35, 0.40)
SLAT_CHOICES = tuple(range(SLAT_MIN, SLAT_MAX + 1))
BOARD_CHOICES = (4, 5, 6, 7, 8, 9)
BOARD_WEIGHTS = (0.12, 0.18, 0.24, 0.24, 0.14, 0.08)

# --- Compatibility sets (spec compatibility matrix). ---
GLASS_INFILLS: tuple[InfillStyle, ...] = (
    "vision_window_pushbar",
    "upper_glass_muntin_lower_xbrace",
    "full_glass_single_pane",
    "divided_lite_glass",
)
# Leaf-arch reads as one glazed arched opening -> single-pane / lite-grid glass.
ARCHED_LEAF_INFILLS: tuple[InfillStyle, ...] = (
    "full_glass_single_pane",
    "divided_lite_glass",
)
# Scalloped batwing crown -> short open louver / glass leaves (saloon family).
SCALLOPED_INFILLS: tuple[InfillStyle, ...] = (
    "louvered_slat",
    "full_glass_single_pane",
)
# Solid wood leaves with a meeting stile carry the optional lever sub-joint.
LEVER_INFILLS: tuple[InfillStyle, ...] = (
    "raised_panel",
    "cross_buck_board",
)

# Palette colorways (spec palette note; rgba). Every .visual material is keyed
# from a colorway here. Keys: frame, leaf, accent, glass, metal, stone.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "dark_walnut": {
        "frame": (0.20, 0.11, 0.06, 1.0),
        "leaf": (0.28, 0.16, 0.09, 1.0),
        "accent": (0.78, 0.60, 0.22, 1.0),
        "glass": (0.62, 0.72, 0.78, 0.45),
        "metal": (0.78, 0.60, 0.22, 1.0),
        "stone": (0.72, 0.70, 0.66, 1.0),
    },
    "honey_brown_wood": {
        "frame": (0.20, 0.22, 0.24, 1.0),
        "leaf": (0.78, 0.47, 0.22, 1.0),
        "accent": (0.28, 0.24, 0.20, 1.0),
        "glass": (0.30, 0.42, 0.46, 0.45),
        "metal": (0.40, 0.36, 0.30, 1.0),
        "stone": (0.82, 0.80, 0.74, 1.0),
    },
    "warm_wood_stone": {
        "frame": (0.60, 0.34, 0.16, 1.0),
        "leaf": (0.80, 0.48, 0.24, 1.0),
        "accent": (0.08, 0.08, 0.09, 1.0),
        "glass": (0.30, 0.42, 0.46, 0.45),
        "metal": (0.10, 0.10, 0.11, 1.0),
        "stone": (0.82, 0.80, 0.74, 1.0),
    },
    "off_white_steel": {
        "frame": (0.80, 0.80, 0.78, 1.0),
        "leaf": (0.90, 0.89, 0.85, 1.0),
        "accent": (0.40, 0.55, 0.72, 1.0),
        "glass": (0.78, 0.85, 0.88, 0.45),
        "metal": (0.75, 0.76, 0.78, 1.0),
        "stone": (0.86, 0.86, 0.84, 1.0),
    },
    "anodized_aluminum": {
        "frame": (0.74, 0.75, 0.76, 1.0),
        "leaf": (0.82, 0.83, 0.84, 1.0),
        "accent": (0.55, 0.56, 0.58, 1.0),
        "glass": (0.62, 0.72, 0.78, 0.45),
        "metal": (0.70, 0.71, 0.72, 1.0),
        "stone": (0.80, 0.80, 0.80, 1.0),
    },
    "wrought_iron_oak": {
        "frame": (0.10, 0.10, 0.11, 1.0),
        "leaf": (0.52, 0.34, 0.18, 1.0),
        "accent": (0.08, 0.08, 0.09, 1.0),
        "glass": (0.30, 0.42, 0.46, 0.45),
        "metal": (0.12, 0.12, 0.13, 1.0),
        "stone": (0.80, 0.78, 0.72, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Classic parent (3b44fd42) drives the
# canonical opening + frame; all 14 sources share OPENING_W=1.70, OPENING_H=2.10,
# LEAF_T=0.045, leaf-local hinge edge at X=0, body toward sign, front face +Y.
# ---------------------------------------------------------------------------
_OPENING_W = 1.70
_OPENING_H = 2.10
_LEAF_T = 0.045
_JAMB_W = 0.12
_JAMB_D = 0.18
_HEAD_H = 0.14
_BASE_H = 0.16
_CENTER_REVEAL = 0.006
_JAMB_REVEAL = 0.006
_FLOOR_Z = 0.0
_ARCH_CLEARANCE = 0.012

_SCALLOPED_LEAF_FRAC = 0.62  # scalloped batwing leaves are short (saloon family)


@dataclass(frozen=True)
class DoubleDoorConfig:
    infill_style: InfillStyle | None = None
    head_style: HeadStyle | None = None
    swing_mode: SwingMode | None = None
    palette_style: PaletteStyle = "dark_walnut"
    panel_count: int | None = None
    lite_rows: int | None = None
    lite_cols: int | None = None
    slat_count: int | None = None
    board_count: int | None = None
    opening_width_scale: float = 1.0
    opening_height_scale: float = 1.0
    leaf_thickness_scale: float = 1.0
    jamb_width_scale: float = 1.0
    swing_open_angle: float = 1.4
    name: str = "double_door"


@dataclass(frozen=True)
class ResolvedDoubleDoorConfig:
    infill_style: InfillStyle
    head_style: HeadStyle
    swing_mode: SwingMode
    palette_style: PaletteStyle
    panel_count: int
    lite_rows: int
    lite_cols: int
    slat_count: int
    board_count: int
    has_lever: bool
    # Concrete geometry (scaled, derived).
    opening_w: float
    opening_h: float
    leaf_t: float
    jamb_w: float
    jamb_d: float
    head_h: float
    base_h: float
    center_reveal: float
    jamb_reveal: float
    leaf_w: float
    leaf_h: float  # full structural leaf height (square top)
    arch_r: float
    spring_h: float
    swing_open: float
    spring_limit: float
    name: str

    @property
    def half_open(self) -> float:
        return self.opening_w / 2.0

    @property
    def left_hinge_x(self) -> float:
        return -(self.half_open - self.jamb_reveal)

    @property
    def right_hinge_x(self) -> float:
        return self.half_open - self.jamb_reveal

    @property
    def hinge_y(self) -> float:
        """Front-mounted pivot plane, just clear of the surround's front face."""
        return self.jamb_d / 2.0 + self.leaf_t / 2.0 + 0.0005

    @property
    def frame_outer_w(self) -> float:
        return self.opening_w + 2.0 * self.jamb_w

    @property
    def is_arched_leaf(self) -> bool:
        return self.head_style == "arched_leaf_top"

    @property
    def is_scalloped(self) -> bool:
        return self.head_style == "scalloped_crown_head"

    @property
    def is_spring(self) -> bool:
        return self.swing_mode == "double_acting_spring"

    @property
    def frame_arch_spring_h(self) -> float:
        """Spring line of the fixed arch, above the moving leaf by its clearance."""
        return self.spring_h + (_ARCH_CLEARANCE if self.is_arched_leaf else 0.0)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Procedural sampling (deterministic; seed 0 not special).
# Order per spec: swing_mode -> head_style (gated) -> infill_style (gated) ->
# matching *_count (weighted small-N) -> palette -> continuous scales.
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> DoubleDoorConfig:
    rng = random.Random(seed)
    swing_mode = rng.choice(SWING_MODES)
    head_style = rng.choice(HEAD_STYLES)
    infill_style = rng.choice(INFILL_STYLES)
    # Decorrelated palette stream so colorways spread evenly across consecutive
    # seeds (the main rng is consumed by the structural slots first).
    palette_style = random.Random(seed * 2654435761 + 0x9E37).choice(PALETTE_STYLES)
    return DoubleDoorConfig(
        swing_mode=swing_mode,
        head_style=head_style,
        infill_style=infill_style,
        palette_style=palette_style,
        panel_count=rng.choices(PANEL_CHOICES, weights=PANEL_WEIGHTS, k=1)[0],
        lite_rows=rng.choices(LITE_ROW_CHOICES, weights=LITE_ROW_WEIGHTS, k=1)[0],
        lite_cols=rng.choices(LITE_COL_CHOICES, weights=LITE_COL_WEIGHTS, k=1)[0],
        slat_count=rng.choice(SLAT_CHOICES),
        board_count=rng.choices(BOARD_CHOICES, weights=BOARD_WEIGHTS, k=1)[0],
        opening_width_scale=round(rng.uniform(0.92, 1.08), 4),
        opening_height_scale=round(rng.uniform(0.95, 1.05), 4),
        leaf_thickness_scale=round(rng.uniform(0.85, 1.25), 4),
        jamb_width_scale=round(rng.uniform(0.8, 1.4), 4),
        swing_open_angle=round(rng.uniform(1.2, 1.92), 4),
        name=f"seeded_double_door_{seed}",
    )


def resolve_config(config: DoubleDoorConfig | None = None) -> ResolvedDoubleDoorConfig:
    cfg = config or DoubleDoorConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # Historical configs may still request the one-active-leaf mode. Double-door
    # identity now requires both leaves to articulate, so resolve that old value
    # to the ordinary paired hinge mode rather than dropping door_1.
    swing_mode = (
        "both_revolute_opposite"
        if cfg.swing_mode == "active_inactive_astragal"
        else _pick(cfg.swing_mode, SWING_MODES)
    )
    head_style = _pick(cfg.head_style, HEAD_STYLES)
    infill_style = _pick(cfg.infill_style, INFILL_STYLES)

    # --- Compatibility gating (spec compatibility matrix). ---
    # arched_leaf_top is a LEAF head -> force flat_head as the frame head and a
    # glass infill so the leaf arch reads as one glazed arched opening.
    if head_style == "arched_leaf_top" and infill_style not in ARCHED_LEAF_INFILLS:
        infill_style = "full_glass_single_pane"
    if head_style == "arched_leaf_top" and swing_mode == "double_acting_spring":
        swing_mode = "both_revolute_opposite"
    # scalloped batwing crown needs a short, reprofile-friendly open leaf.
    if head_style == "scalloped_crown_head" and infill_style not in SCALLOPED_INFILLS:
        infill_style = "louvered_slat"

    has_lever = infill_style in LEVER_INFILLS and swing_mode != "double_acting_spring"

    # --- Multiplicity counts (only the matching one is live). ---
    panel_count = int(_clamp(cfg.panel_count if cfg.panel_count is not None else 3,
                             PANEL_MIN, PANEL_MAX))
    lite_rows = int(_clamp(cfg.lite_rows if cfg.lite_rows is not None else 2,
                           LITE_ROW_MIN, LITE_ROW_MAX))
    lite_cols = int(_clamp(cfg.lite_cols if cfg.lite_cols is not None else 3,
                           LITE_COL_MIN, LITE_COL_MAX))
    slat_count = int(_clamp(cfg.slat_count if cfg.slat_count is not None else 18,
                            SLAT_MIN, SLAT_MAX))
    board_count = int(_clamp(cfg.board_count if cfg.board_count is not None else 7,
                             BOARD_MIN, BOARD_MAX))

    # --- Continuous scales (clamped). ---
    w_scale = _clamp(cfg.opening_width_scale, 0.92, 1.08)
    h_scale = _clamp(cfg.opening_height_scale, 0.95, 1.05)
    t_scale = _clamp(cfg.leaf_thickness_scale, 0.85, 1.25)
    j_scale = _clamp(cfg.jamb_width_scale, 0.8, 1.4)

    opening_w = _OPENING_W * w_scale
    opening_h = _OPENING_H * h_scale
    leaf_t = _LEAF_T * t_scale
    jamb_w = _JAMB_W * j_scale
    head_h = _HEAD_H
    base_h = _BASE_H
    center_reveal = _CENTER_REVEAL
    # The pivot lies on the leaf's hinge edge. Its setback must clear the swept
    # half-thickness at large swing angles; a fixed 6 mm reveal lets thick leaves
    # cut through the jamb as soon as they rotate.
    jamb_reveal = max(_JAMB_REVEAL, leaf_t / 2.0 + 0.010)

    # --- Derived equations (spec parameter table). ---
    # LEAF_W = (OPENING_W - CENTER_REVEAL - 2*JAMB_REVEAL)/2 (each leaf half opening)
    leaf_w = (opening_w - center_reveal - 2.0 * jamb_reveal) / 2.0
    leaf_h = opening_h - 0.02  # leaf slightly shorter than the opening (square top)

    # arch coherence: arched_leaf_top -> each leaf arch is a quarter circle of
    # radius ARCH_R centered at the meeting edge; the two meeting edges sit at
    # world X~=0 so the closed pair completes one round arch (radius ARCH_R, same
    # circle as the matching frame ring header). ARCH_R = leaf_w so the arc spans
    # the leaf width. The moving leaf circle sits _ARCH_CLEARANCE below the fixed
    # frame circle so neither leaf touches or penetrates the arch ring.
    arch_r = leaf_w
    if head_style == "arched_leaf_top":
        leaf_h = max(1.2, (opening_h - 0.02) - arch_r - _ARCH_CLEARANCE)
    elif head_style == "scalloped_crown_head":
        # Short batwing leaves (saloon). Keep base at floor; reduce height.
        leaf_h = (opening_h - 0.02) * _SCALLOPED_LEAF_FRAC
    spring_h = leaf_h  # leaf arch springs at the square-top height

    swing_open = _clamp(cfg.swing_open_angle, 1.2, 1.92)
    spring_limit = _clamp(cfg.swing_open_angle, 1.0, 1.3)

    return ResolvedDoubleDoorConfig(
        infill_style=infill_style,
        head_style=head_style,
        swing_mode=swing_mode,
        palette_style=palette_style,
        panel_count=panel_count,
        lite_rows=lite_rows,
        lite_cols=lite_cols,
        slat_count=slat_count,
        board_count=board_count,
        has_lever=has_lever,
        opening_w=opening_w,
        opening_h=opening_h,
        leaf_t=leaf_t,
        jamb_w=jamb_w,
        jamb_d=_JAMB_D,
        head_h=head_h,
        base_h=base_h,
        center_reveal=center_reveal,
        jamb_reveal=jamb_reveal,
        leaf_w=leaf_w,
        leaf_h=leaf_h,
        arch_r=arch_r,
        spring_h=spring_h,
        swing_open=swing_open,
        spring_limit=spring_limit,
        name=cfg.name or "double_door",
    )


def with_overrides(config: DoubleDoorConfig, **kwargs: object) -> DoubleDoorConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# Slot-choice export (consumed by module_topology_diversity + attribution).
# Encodes the live multiplicity into the tuple so distinct-N shows up.
# ---------------------------------------------------------------------------
def _multiplicity_tag(r: ResolvedDoubleDoorConfig) -> str | None:
    if r.infill_style == "raised_panel":
        return f"p{r.panel_count}"
    if r.infill_style == "divided_lite_glass":
        return f"r{r.lite_rows}c{r.lite_cols}"
    if r.infill_style == "louvered_slat":
        return f"s{r.slat_count}"
    if r.infill_style == "cross_buck_board":
        return f"b{r.board_count}"
    return None


def slot_choices_for_config(
    config: DoubleDoorConfig | ResolvedDoubleDoorConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedDoubleDoorConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("infill_style", r.infill_style),
        ("head_style", r.head_style),
        ("swing_mode", r.swing_mode),
    ]
    tag = _multiplicity_tag(r)
    if tag is not None:
        choices.append(("infill_count", tag))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Frame (root) builders.
# ===========================================================================
def _build_frame_members(r: ResolvedDoubleDoorConfig) -> dict[str, cq.Workplane]:
    """Fixed frame as separate members so exact collisions do not bridge the
    opening. Two jambs + head jamb + carved base rail + three doorstop beads.
    Source: classic _build_frame_members L73-L132.
    """
    half_open = r.half_open
    jw, jd, oh = r.jamb_w, r.jamb_d, r.opening_h
    head_h, base_h, leaf_t = r.head_h, r.base_h, r.leaf_t
    fow = r.frame_outer_w
    members: dict[str, cq.Workplane] = {}

    members["jamb_left"] = (
        cq.Workplane("XY").box(jw, jd, oh)
        .translate((-(half_open + jw / 2.0), 0.0, oh / 2.0))
    )
    members["jamb_right"] = (
        cq.Workplane("XY").box(jw, jd, oh)
        .translate((half_open + jw / 2.0, 0.0, oh / 2.0))
    )
    # Carved base rail with two decorative grooves on the front face.
    base = (
        cq.Workplane("XY").box(fow, jd, base_h)
        .translate((0.0, 0.0, -base_h / 2.0))
    )
    groove = (
        cq.Workplane("XY").box(fow - 0.04, 0.02, 0.018)
        .translate((0.0, jd / 2.0 - 0.01, -base_h / 2.0 + 0.04))
    )
    base = base.cut(groove).cut(groove.translate((0.0, 0.0, 0.05)))
    members["base_rail"] = base

    # Doorstop beads behind the closed leaves (negative Y).
    stop_t = 0.014
    stop_proud = 0.02
    stop_y = -leaf_t / 2.0 - stop_t / 2.0 - 0.001
    members["stop_left"] = (
        cq.Workplane("XY").box(stop_proud, stop_t, oh - 0.02)
        .translate((-half_open + stop_proud / 2.0, stop_y, oh / 2.0))
    )
    members["stop_right"] = (
        cq.Workplane("XY").box(stop_proud, stop_t, oh - 0.02)
        .translate((half_open - stop_proud / 2.0, stop_y, oh / 2.0))
    )
    # A straight stop across an arched opening reads as the stray line visible in
    # the reference image. Arched heads rely on the side stops and their shaped
    # surround instead; square/transom/cafe heads retain the horizontal stop.
    if r.head_style not in (
        "arched_stone_head",
        "arched_leaf_top",
        "solid_semicircle_head",
    ):
        members["stop_head"] = (
            cq.Workplane("XY").box(r.opening_w, stop_t, stop_proud)
            .translate((0.0, stop_y, oh - stop_proud / 2.0))
        )

    # --- Slot B: head member (FRAME-surround heads). ---
    if r.head_style == "transom_over_flat_head":
        # Lower head rail + a fixed transom band above it (ornate L222-L302).
        members["head_rail"] = (
            cq.Workplane("XY").box(fow, jd, head_h)
            .translate((0.0, 0.0, oh + head_h / 2.0))
        )
        transom_h = 0.34
        members["transom_panel"] = (
            cq.Workplane("XY").box(r.opening_w, jd * 0.8, transom_h)
            .translate((0.0, 0.0, oh + head_h + transom_h / 2.0))
        )
        # Transom muntin cross (a slim mullion + transom bar).
        members["transom_mullion"] = (
            cq.Workplane("XY").box(0.03, jd * 0.85, transom_h)
            .translate((0.0, 0.0, oh + head_h + transom_h / 2.0))
        )
    elif r.head_style == "arched_stone_head":
        # Semicircular stone arch ring + keystone over the doorway
        # (carriage _stone_surround L254-L331).
        spring = oh
        r_outer = half_open + jw
        r_inner = half_open
        outer = (
            cq.Workplane("XZ", origin=(0.0, 0.0, spring))
            .circle(r_outer).extrude(jd / 2.0, both=True)
        )
        inner = (
            cq.Workplane("XZ", origin=(0.0, 0.0, spring))
            .circle(r_inner).extrude(jd * 2.0, both=True)
        )
        ring = outer.cut(inner)
        upper_clip = (
            cq.Workplane("XY")
            .box(2.0 * r_outer + 0.1, jd * 2.2, r_outer + 0.1)
            .translate((0.0, 0.0, spring + (r_outer + 0.1) / 2.0))
        )
        members["arch_ring"] = ring.intersect(upper_clip)
        members["keystone"] = (
            cq.Workplane("XY").box(0.10, jd, 0.18)
            .translate((0.0, 0.0, spring + r_inner + 0.02))
        )
    elif r.head_style == "solid_semicircle_head":
        # Fully filled semicircular tympanum above the spring line. This is the
        # solid alternative to the hollow arched-stone ring requested for fig. 3.
        spring = oh
        radius = half_open + jw
        disk = (
            cq.Workplane("XZ", origin=(0.0, 0.0, spring))
            .circle(radius)
            .extrude(jd / 2.0, both=True)
        )
        upper_clip = (
            cq.Workplane("XY")
            .box(2.0 * radius + 0.1, jd * 2.2, radius + 0.1)
            .translate((0.0, 0.0, spring + (radius + 0.1) / 2.0))
        )
        members["solid_semicircle"] = disk.intersect(upper_clip)
    elif r.head_style in ("flat_head", "scalloped_crown_head"):
        # flat_head / scalloped_crown_head: a flat head jamb.
        members["head_jamb"] = (
            cq.Workplane("XY").box(fow, jd, head_h)
            .translate((0.0, 0.0, oh + head_h / 2.0))
        )

    return members


def _arched_frame_header(r: ResolvedDoubleDoorConfig) -> cq.Workplane:
    """Semicircular ring band header on the SAME circle as the leaf arches
    (arched_glazed _arched_frame_header L221-L253). r_inner = ARCH_R, centered at
    the opening midpoint at the spring line (leaf_h).
    """
    r_outer = r.arch_r + r.jamb_w * 0.6
    r_inner = r.arch_r
    spring = r.frame_arch_spring_h
    outer = (
        cq.Workplane("XZ", origin=(0.0, 0.0, spring))
        .circle(r_outer).extrude(r.jamb_d / 2.0, both=True)
    )
    inner = (
        cq.Workplane("XZ", origin=(0.0, 0.0, spring))
        .circle(r_inner).extrude(r.jamb_d * 2.0, both=True)
    )
    ring = outer.cut(inner)
    upper_clip = (
        cq.Workplane("XY")
        .box(2.0 * r_outer + 0.1, r.jamb_d * 2.2, r_outer + 0.1)
        .translate((0.0, 0.0, spring + (r_outer + 0.1) / 2.0))
    )
    return ring.intersect(upper_clip)


# ===========================================================================
# Leaf-local geometry helpers.
# Convention (all infills): hinge edge at leaf-local X=0; body toward `sign`;
# thickness along Y centered; front face = +Y; base at z=0; meeting edge at
# X = sign*leaf_w.
# ===========================================================================
def _leaf_blank(r: ResolvedDoubleDoorConfig, sign: float) -> cq.Workplane:
    cx = sign * r.leaf_w / 2.0
    return (
        cq.Workplane("XY")
        .box(r.leaf_w, r.leaf_t, r.leaf_h, centered=(True, True, False))
        .translate((cx, 0.0, 0.0))
    )


def _leaf_hinge_sleeves(r: ResolvedDoubleDoorConfig) -> cq.Workplane:
    """Three annular leaf knuckles concentric with the revolute joint axis."""
    outer_r = 0.018
    bore_r = 0.0105
    segment_h = min(0.18, r.leaf_h * 0.12)
    centers = (0.18, r.leaf_h * 0.5, r.leaf_h - 0.18)
    sleeves = None
    for center_z in centers:
        sleeve = (
            cq.Workplane("XY")
            .circle(outer_r)
            .circle(bore_r)
            .extrude(segment_h)
            .translate((0.0, 0.0, center_z - segment_h / 2.0))
        )
        sleeves = sleeve if sleeves is None else sleeves.union(sleeve)
    assert sleeves is not None
    return sleeves


def _frame_hinge_pin(r: ResolvedDoubleDoorConfig, idx: int) -> cq.Workplane:
    """Fixed pin anchored to the threshold by a shoe below the moving leaf."""
    pin_r = 0.010
    hinge_x = r.left_hinge_x if idx == 0 else r.right_hinge_x
    pin_bottom = -0.060
    pin_top = r.leaf_h - 0.040
    pin_h = pin_top - pin_bottom
    pin = (
        cq.Workplane("XY")
        .cylinder(pin_h, pin_r)
        .translate((hinge_x, r.hinge_y, (pin_bottom + pin_top) / 2.0))
    )
    shoe_y0 = r.jamb_d / 2.0 - 0.020
    shoe_y1 = r.hinge_y + pin_r
    shoe = (
        cq.Workplane("XY")
        .box(0.032, shoe_y1 - shoe_y0, 0.059)
        .translate(
            (
                hinge_x,
                (shoe_y0 + shoe_y1) / 2.0,
                -0.0305,
            )
        )
    )
    return pin.union(shoe)


def _scalloped_crown_clip(r: ResolvedDoubleDoorConfig, leaf: cq.Workplane, sign: float) -> cq.Workplane:
    """Keep the leaf below the saloon source's smooth cyma crown.

    The source profile is lowest at the hinge-side shoulder and eases upward
    to the meeting stile, where the mirrored pair forms one rounded central
    hump.  Intersecting with the sampled profile avoids the old rotated-box
    cut, whose overhanging corners read as long pointed "wings".
    """
    rise = min(0.18, r.leaf_h * 0.14)
    points = [(0.0, 0.0), (sign * r.leaf_w, 0.0)]
    # Trace the crown from its high meeting edge back to the low hinge edge.
    # This is the same cosine-eased cyma used by the saloon source asset.
    samples = 32
    for i in range(samples + 1):
        t = 1.0 - i / samples  # 1 at meeting edge, 0 at hinge edge
        x = sign * r.leaf_w * t
        crown = rise * (0.15 + 0.85 * (0.5 - 0.5 * math.cos(math.pi * t)))
        z = r.leaf_h - rise + crown
        points.append((x, z))
    keep = (
        cq.Workplane("XZ")
        .polyline(points)
        .close()
        .extrude(r.leaf_t * 1.8, both=True)
    )
    return leaf.intersect(keep)


# ---------------------------------------------------------------------------
# Slot A infill builders. Each returns a list of (visual_name, shape, mat_key)
# tuples for the leaf-`idx` part (visual names prefixed door_{idx}_).
# `glass` material is used for translucent panes.
# ---------------------------------------------------------------------------
def _infill_raised_panel(r, sign, idx):
    """Stacked raised/fielded panels (panels_six _add_raised_panel L138-L204;
    panel loop L247-L260). panel_count panels merged into the leaf solid."""
    leaf = _leaf_blank(r, sign)
    cx = sign * r.leaf_w / 2.0
    stile = min(0.11, r.leaf_w * 0.13)
    rail = 0.06 if r.panel_count >= 4 else 0.10
    field_inset_y = 0.014
    molding_proud = 0.006
    pad_proud = 0.010
    face_y = r.leaf_t / 2.0
    floor_y = face_y - field_inset_y
    n = r.panel_count
    usable_h = r.leaf_h - 2 * rail - (n - 1) * rail
    panel_h = usable_h / n
    panel_w = r.leaf_w - 2 * stile
    for i in range(n):
        cz = rail + panel_h / 2.0 + i * (panel_h + rail)
        margin_w = min(0.05, panel_w * 0.18)
        margin_h = min(0.05, panel_h * 0.18)
        pad_inset_w = min(0.08, panel_w * 0.28)
        pad_inset_h = min(0.08, panel_h * 0.28)
        field = (cq.Workplane("XY").box(panel_w, field_inset_y * 2.0, panel_h)
                 .translate((cx, face_y, cz)))
        leaf = leaf.cut(field)
        mold_outer = (cq.Workplane("XY").box(panel_w, molding_proud * 2.0, panel_h)
                      .translate((cx, floor_y + molding_proud, cz)))
        mold_inner = (cq.Workplane("XY").box(panel_w - margin_w, molding_proud * 4.0, panel_h - margin_h)
                      .translate((cx, floor_y + molding_proud, cz)))
        leaf = leaf.union(mold_outer.cut(mold_inner))
        pad = (cq.Workplane("XY")
               .box(panel_w - pad_inset_w, pad_proud + (face_y - floor_y), panel_h - pad_inset_h)
               .translate((cx, floor_y + (pad_proud + (face_y - floor_y)) / 2.0, cz)))
        leaf = leaf.union(pad)
    try:
        leaf = leaf.edges("|Z").fillet(0.004)
    except Exception:
        pass
    return [(f"door_{idx}_leaf", leaf, "leaf")]


def _infill_vision_window_pushbar(r, sign, idx):
    """Vision-window cut + glass pane + stainless push-bar + bumper stripes
    (hospital _leaf_body L93-L171)."""
    cx = sign * r.leaf_w / 2.0
    win_w = min(0.42, r.leaf_w * 0.55)
    win_h = 0.46
    win_cz = r.leaf_h * 0.74
    leaf = _leaf_blank(r, sign)
    window_cut = (cq.Workplane("XY").box(win_w, r.leaf_t + 0.02, win_h)
                  .translate((cx, 0.0, win_cz)))
    leaf = leaf.cut(window_cut)
    try:
        leaf = leaf.edges("|Z").fillet(0.003)
    except Exception:
        pass
    out = [(f"door_{idx}_leaf", leaf, "leaf")]
    # Glass pane laps slightly past the opening edge into the rabbet so it is
    # supported by (not floating inside) the leaf opening.
    glass = (cq.Workplane("XY").box(win_w + 0.014, 0.006, win_h + 0.014)
             .translate((cx, 0.0, win_cz)))
    out.append((f"door_{idx}_glass", glass, "glass"))
    # Push bar (horizontal stainless cylinder on two standoffs).
    face_y = r.leaf_t / 2.0
    bar_len = min(0.62, r.leaf_w * 0.78)
    bar_z = r.leaf_h * 0.46
    standoff = 0.05
    bar = (cq.Workplane("XY").cylinder(bar_len, 0.013)
           .rotate((0, 0, 0), (0, 1, 0), 90)
           .translate((cx, face_y + standoff, bar_z)))
    half_bar = bar_len / 2.0 - 0.04
    for so_x in (cx - sign * half_bar, cx + sign * half_bar):
        so = (cq.Workplane("XY").cylinder(standoff + 0.01, 0.012)
              .rotate((0, 0, 0), (1, 0, 0), 90)
              .translate((so_x, face_y + standoff / 2.0, bar_z)))
        bar = bar.union(so)
    out.append((f"door_{idx}_push_bar", bar, "metal"))
    for j, sz in enumerate((r.leaf_h * 0.30, r.leaf_h * 0.20)):
        stripe = (cq.Workplane("XY").box(r.leaf_w, r.leaf_t + 0.006, 0.07)
                  .translate((cx, 0.0, sz)))
        out.append((f"door_{idx}_stripe_{j}", stripe, "accent"))
    return out


def _infill_carved_circle_motif(r, sign, idx):
    """Recessed field + raised concentric molding half-ring forming a central
    circle at the meeting edge + dark inset half-disc (ornate _leaf_body /
    _leaf_inset L85-L188)."""
    leaf = _leaf_blank(r, sign)
    cx = sign * r.leaf_w / 2.0
    face_y = r.leaf_t / 2.0
    field_inset_y = 0.012
    # Recessed flat field (cut into the front face).
    field_w = r.leaf_w - 2 * min(0.10, r.leaf_w * 0.13)
    field_h = r.leaf_h - 0.30
    field = (cq.Workplane("XY").box(field_w, field_inset_y * 2.0, field_h)
             .translate((cx, face_y, r.leaf_h / 2.0)))
    leaf = leaf.cut(field)
    floor_y = face_y - field_inset_y
    # Concentric raised molding ring (a torus-like annulus) centered mid-leaf.
    ring_r = min(0.22, r.leaf_w * 0.30)
    ring_z = r.leaf_h * 0.62
    ring_outer = (cq.Workplane("XY").cylinder(0.008, ring_r)
                  .rotate((0, 0, 0), (1, 0, 0), 90)
                  .translate((cx, floor_y + 0.004, ring_z)))
    ring_inner = (cq.Workplane("XY").cylinder(0.05, ring_r - 0.03)
                  .rotate((0, 0, 0), (1, 0, 0), 90)
                  .translate((cx, floor_y + 0.004, ring_z)))
    leaf = leaf.union(ring_outer.cut(ring_inner))
    try:
        leaf = leaf.edges("|Z").fillet(0.004)
    except Exception:
        pass
    out = [(f"door_{idx}_leaf", leaf, "leaf")]
    # Dark recessed inset disc inside the ring.
    disc = (cq.Workplane("XY").cylinder(0.006, ring_r - 0.04)
            .rotate((0, 0, 0), (1, 0, 0), 90)
            .translate((cx, floor_y + 0.003, ring_z)))
    out.append((f"door_{idx}_inset", disc, "accent"))
    # Vertical pull handle on standoffs (near meeting edge). Standoffs embed
    # into the leaf face (start ~5mm inside) so the handle is supported.
    hx = sign * (r.leaf_w - 0.08)
    handle = (cq.Workplane("XY").cylinder(0.40, 0.012)
              .translate((hx, face_y + 0.05, r.leaf_h * 0.46)))
    for hz in (r.leaf_h * 0.46 - 0.18, r.leaf_h * 0.46 + 0.18):
        so = (cq.Workplane("XY").cylinder(0.062, 0.010)
              .rotate((0, 0, 0), (1, 0, 0), 90)
              .translate((hx, face_y + 0.019, hz)))
        handle = handle.union(so)
    out.append((f"door_{idx}_handle", handle, "metal"))
    return out


def _infill_upper_glass_muntin_lower_xbrace(r, sign, idx):
    """Upper divided-glass window (1 vertical + 2 horizontal muntins) over a
    lower ledged-and-X-braced board panel (carriage _leaf_frame_and_panels
    L101-L198)."""
    cx = sign * r.leaf_w / 2.0
    face_y = r.leaf_t / 2.0
    stile = min(0.09, r.leaf_w * 0.11)
    leaf = _leaf_blank(r, sign)
    # Upper window cut (top ~45% of leaf).
    win_w = r.leaf_w - 2 * stile
    win_h = r.leaf_h * 0.40
    win_cz = r.leaf_h * 0.72
    window_cut = (cq.Workplane("XY").box(win_w, r.leaf_t + 0.02, win_h)
                  .translate((cx, 0.0, win_cz)))
    leaf = leaf.cut(window_cut)
    try:
        leaf = leaf.edges("|Z").fillet(0.004)
    except Exception:
        pass
    out = [(f"door_{idx}_leaf", leaf, "leaf")]
    # Glass pane laps past the opening edge so it is seated in the rabbet.
    glass = (cq.Workplane("XY").box(win_w + 0.012, 0.006, win_h + 0.012)
             .translate((cx, 0.0, win_cz)))
    out.append((f"door_{idx}_glass", glass, "glass"))
    # Muntin grid: 1 vertical + 2 horizontal bars across the window.
    muntins = None
    vbar = (cq.Workplane("XY").box(0.012, 0.012, win_h)
            .translate((cx, 0.0, win_cz)))
    muntins = vbar
    for hz in (win_cz - win_h / 3.0, win_cz + win_h / 3.0):
        hbar = (cq.Workplane("XY").box(win_w, 0.012, 0.012)
                .translate((cx, 0.0, hz)))
        muntins = muntins.union(hbar)
    out.append((f"door_{idx}_muntins", muntins, "leaf"))
    # Lower X-braced board panel: two diagonal straps on the front face.
    lower_h = win_cz - win_h / 2.0
    diag_len = math.hypot(win_w, lower_h - 0.10)
    angle = math.degrees(math.atan2(lower_h - 0.10, win_w))
    for bi, slope in enumerate((1.0, -1.0)):
        brace = (cq.Workplane("XY").box(diag_len, 0.012, 0.05)
                 .rotate((0, 0, 0), (0, 1, 0), angle * slope)
                 .translate((cx, face_y + 0.006, lower_h / 2.0 + 0.05)))
        out.append((f"door_{idx}_brace_{bi}", brace, "accent"))
    return out


def _infill_louvered_slat(r, sign, idx):
    """Framed full-height field of horizontal angled louver slats
    (louvered_infill _build_louver_slat L179-L191; slat loop L311-L320)."""
    cx = sign * r.leaf_w / 2.0
    stile = min(0.11, r.leaf_w * 0.13)
    rail = 0.13
    leaf = _leaf_blank(r, sign)
    louver_w = r.leaf_w - 2 * stile
    louver_h = r.leaf_h - 2 * rail
    louver_cz = rail + louver_h / 2.0
    opening = (cq.Workplane("XY").box(louver_w, r.leaf_t * 1.2, louver_h)
               .translate((cx, 0.0, louver_cz)))
    leaf = leaf.cut(opening)
    try:
        leaf = leaf.edges("|Z").fillet(0.004)
    except Exception:
        pass
    out = [(f"door_{idx}_leaf", leaf, "leaf")]
    n = r.slat_count
    slat_w = louver_w + 0.006  # slight embed into stiles for connectivity
    spacing = louver_h / n
    for i in range(n):
        slat_z = rail + spacing * (i + 0.5)
        slat = (cq.Workplane("XY").box(slat_w, 0.009, 0.040)
                .rotate((0, 0, 0), (1, 0, 0), 35.0)
                .translate((cx, 0.0, slat_z)))
        out.append((f"door_{idx}_slat_{i}", slat, "leaf"))
    return out


def _infill_full_glass_single_pane(r, sign, idx):
    """Narrow-stile frame (two stiles + top/bottom rails) around one large single
    glass pane (storefront _leaf_frame_body L74-L117)."""
    cx = sign * r.leaf_w / 2.0
    stile = min(0.06, r.leaf_w * 0.08)
    top_rail = 0.10
    bot_rail = 0.16
    leaf = _leaf_blank(r, sign)
    glass_w = r.leaf_w - 2 * stile
    glass_h = r.leaf_h - top_rail - bot_rail
    glass_cz = bot_rail + glass_h / 2.0
    opening = (cq.Workplane("XY").box(glass_w, r.leaf_t + 0.02, glass_h)
               .translate((cx, 0.0, glass_cz)))
    leaf = leaf.cut(opening)
    try:
        leaf = leaf.edges("|Z").fillet(0.003)
    except Exception:
        pass
    out = [(f"door_{idx}_leaf", leaf, "leaf")]
    # Glass pane laps past the opening edge into the stile/rail rabbet.
    glass = (cq.Workplane("XY").box(glass_w + 0.012, 0.010, glass_h + 0.012)
             .translate((cx, 0.0, glass_cz)))
    out.append((f"door_{idx}_glass", glass, "glass"))
    # Vertical push bar near the meeting edge; its inner end embeds into the
    # stile face (straddles face_y) so it is supported, not floating.
    face_y = r.leaf_t / 2.0
    bar = (cq.Workplane("XY").box(0.024, 0.05, r.leaf_h * 0.5)
           .translate((sign * (r.leaf_w - 0.07), face_y + 0.018, bot_rail + glass_h / 2.0)))
    out.append((f"door_{idx}_push_bar", bar, "metal"))
    return out


def _infill_divided_lite_glass(r, sign, idx):
    """Full-window glazed leaf with a divided lite GRID + muntin bars
    (six_light_glazed _glass_lite / _muntin_grid L128-L172)."""
    cx = sign * r.leaf_w / 2.0
    stile = min(0.06, r.leaf_w * 0.08)
    top_rail = 0.10
    bot_rail = 0.16
    leaf = _leaf_blank(r, sign)
    win_w = r.leaf_w - 2 * stile
    win_h = r.leaf_h - top_rail - bot_rail
    win_cz = bot_rail + win_h / 2.0
    opening = (cq.Workplane("XY").box(win_w, r.leaf_t + 0.02, win_h)
               .translate((cx, 0.0, win_cz)))
    leaf = leaf.cut(opening)
    try:
        leaf = leaf.edges("|Z").fillet(0.003)
    except Exception:
        pass
    out = [(f"door_{idx}_leaf", leaf, "leaf")]
    n_rows, n_cols = r.lite_rows, r.lite_cols
    muntin_w = 0.012
    lite_w = (win_w - (n_cols - 1) * muntin_w) / n_cols
    lite_h = (win_h - (n_rows - 1) * muntin_w) / n_rows
    win_left = cx - win_w / 2.0
    win_bot = win_cz - win_h / 2.0
    # Muntin grid bars.
    muntins = None
    for rr in range(n_rows - 1):
        z = win_bot + (rr + 1) * lite_h + (rr + 0.5) * muntin_w
        bar = (cq.Workplane("XY").box(win_w, 0.010, muntin_w).translate((cx, 0.0, z)))
        muntins = bar if muntins is None else muntins.union(bar)
    for cc in range(n_cols - 1):
        x = win_left + (cc + 1) * lite_w + (cc + 0.5) * muntin_w
        bar = (cq.Workplane("XY").box(muntin_w, 0.010, win_h).translate((x, 0.0, win_cz)))
        muntins = bar if muntins is None else muntins.union(bar)
    if muntins is not None:
        out.append((f"door_{idx}_muntins", muntins, "leaf"))
    # Nested lite grid. Each lite laps under the muntins / frame rabbet
    # (oversized by muntin_w) so it is seated, not floating in the opening.
    for row in range(n_rows):
        for col in range(n_cols):
            lx = win_left + col * (lite_w + muntin_w) + lite_w / 2.0
            lz = win_bot + row * (lite_h + muntin_w) + lite_h / 2.0
            lite = (cq.Workplane("XY")
                    .box(lite_w + 2.0 * muntin_w, 0.006, lite_h + 2.0 * muntin_w)
                    .translate((lx, 0.0, lz)))
            out.append((f"door_{idx}_lite_{row}_{col}", lite, "glass"))
    return out


def _infill_cross_buck_board(r, sign, idx):
    """Full-height ledged-and-X-braced tongue-and-groove board field
    (x_brace_solid _make_tg_board L196-L212; board loop L360-L367)."""
    cx = sign * r.leaf_w / 2.0
    face_y = r.leaf_t / 2.0
    stile_w = min(0.08, r.leaf_w * 0.10)
    ledger_h = 0.08
    board_gap = 0.003
    board_t = 0.012
    leaf = _leaf_blank(r, sign)
    try:
        leaf = leaf.edges("|Z").fillet(0.003)
    except Exception:
        pass
    out = [(f"door_{idx}_leaf", leaf, "leaf")]
    infill_w = r.leaf_w - 2 * stile_w
    infill_h = r.leaf_h - 2 * ledger_h
    n = r.board_count
    board_w = (infill_w - (n - 1) * board_gap) / n
    board_cz = ledger_h + infill_h / 2.0
    for i in range(n):
        bx = sign * (stile_w + board_w / 2.0 + i * (board_w + board_gap))
        board = (cq.Workplane("XY").box(board_w, board_t, infill_h)
                 .translate((bx, face_y + board_t / 2.0, board_cz)))
        out.append((f"door_{idx}_board_{i}", board, "accent"))
    # Top + bottom ledger rails (span full width).
    for pos, cz in (("top", r.leaf_h - ledger_h / 2.0), ("bottom", ledger_h / 2.0)):
        ledger = (cq.Workplane("XY").box(r.leaf_w, 0.018, ledger_h)
                  .translate((cx, face_y + 0.009, cz)))
        out.append((f"door_{idx}_ledger_{pos}", ledger, "frame"))
    # Two diagonal X-braces on top of the boards.
    diag_len = math.hypot(infill_w, infill_h)
    angle = math.degrees(math.atan2(infill_h, infill_w))
    brace_y = face_y + board_t + 0.0075
    for bi, slope in enumerate((1.0, -1.0)):
        brace = (cq.Workplane("XY").box(diag_len, 0.015, 0.055)
                 .rotate((0, 0, 0), (0, 1, 0), angle * slope)
                 .translate((cx, brace_y, ledger_h + infill_h / 2.0)))
        out.append((f"door_{idx}_brace_{bi}", brace, "frame"))
    return out


_INFILL_BUILDERS = {
    "raised_panel": _infill_raised_panel,
    "vision_window_pushbar": _infill_vision_window_pushbar,
    "carved_circle_motif": _infill_carved_circle_motif,
    "upper_glass_muntin_lower_xbrace": _infill_upper_glass_muntin_lower_xbrace,
    "louvered_slat": _infill_louvered_slat,
    "full_glass_single_pane": _infill_full_glass_single_pane,
    "divided_lite_glass": _infill_divided_lite_glass,
    "cross_buck_board": _infill_cross_buck_board,
}


# ---------------------------------------------------------------------------
# Lever sub-joint (optional; solid wood leaves, revolute modes). Source:
# classic _build_handle_fixed / _build_lever L240-L294, lever joint L346-L354.
# ---------------------------------------------------------------------------
def _plate_x(r: ResolvedDoubleDoorConfig, sign: float) -> float:
    return sign * (r.leaf_w - 0.055)


def _handle_z(r: ResolvedDoubleDoorConfig) -> float:
    return r.leaf_h * 0.45


def _spindle_z(r: ResolvedDoubleDoorConfig) -> float:
    return _handle_z(r) + 0.03


def _build_handle_fixed(r: ResolvedDoubleDoorConfig, sign: float) -> cq.Workplane:
    plate_x = _plate_x(r, sign)
    face_y = r.leaf_t / 2.0
    hz = _handle_z(r)
    escutcheon = (cq.Workplane("XY").box(0.04, 0.010, 0.18)
                  .translate((plate_x, face_y + 0.003, hz)))
    # Rose collar straddles the spindle axis at the leaf face (y=0): it runs from
    # just inside the leaf (y<0) out past the face so the lever joint origin
    # (at y=0) sits on real rose hardware.
    rose = (cq.Workplane("XY").cylinder(face_y + 0.040, 0.012)
            .rotate((0, 0, 0), (1, 0, 0), 90)
            .translate((plate_x, 0.012, _spindle_z(r))))
    return escutcheon.union(rose)


def _build_lever(r: ResolvedDoubleDoorConfig, sign: float) -> cq.Workplane:
    """Lever bar + neck in lever-local coords. The child frame origin sits ON the
    spindle axis at the leaf face (y=0); the neck runs along +Y from the origin
    out to the bar so the joint origin lies on the neck geometry.
    """
    face_y = r.leaf_t / 2.0
    neck_out = face_y + 0.030
    # Neck: cylinder along Y from y~=0 to y=neck_out (contains the origin).
    neck = (cq.Workplane("XY").cylinder(neck_out, 0.014)
            .rotate((0, 0, 0), (1, 0, 0), 90)
            .translate((0.0, neck_out / 2.0, 0.0)))
    lever = (cq.Workplane("XY").box(0.085, 0.016, 0.016)
             .translate((-sign * 0.05, neck_out, 0.0)))
    return neck.union(lever)


# ===========================================================================
# Leaf part emit (one leaf -> a `door_{idx}` part with all infill visuals +
# optional handle/lever). Returns the part.
# ===========================================================================
def _emit_leaf_part(model, r, mats, *, idx: int, sign: float, assets):
    leaf = model.part(f"door_{idx}")
    builder = _INFILL_BUILDERS[r.infill_style]
    pieces = builder(r, sign, idx)
    pin_clearance = (
        cq.Workplane("XY")
        .cylinder(r.leaf_h + r.arch_r + 0.20, 0.0105)
        .translate((0.0, 0.0, (r.leaf_h + r.arch_r) / 2.0))
    )
    # Slot B leaf-profile heads: reprofile the leaf-body visual only.
    for name, shape, mat_key in pieces:
        if name == f"door_{idx}_leaf":
            if r.is_arched_leaf:
                shape = _apply_arched_leaf_top(r, shape, sign)
            elif r.is_scalloped:
                shape = _scalloped_crown_clip(r, shape, sign)
        elif r.is_scalloped and r.infill_style == "louvered_slat":
            # The source saloon door keeps every louver below the crown rather
            # than allowing the upper slats to poke through the curved top rail.
            shape = _scalloped_crown_clip(r, shape, sign)
        # The captured frame pin occupies the joint axis. Cut its running bore
        # through every leaf-local feature so no decoration seals the hinge path.
        shape = shape.cut(pin_clearance)
        leaf.visual(
            mesh_from_cadquery(shape, name),
            material=mats[mat_key],
            name=name, material_class_id=("glass.clear_transparent" if r.infill_style in {"vision_window_pushbar", "upper_glass_muntin_lower_xbrace", "full_glass_single_pane", "divided_lite_glass"} else "wood.patterned_decorative"),
        )
    leaf.visual(
        mesh_from_cadquery(_leaf_hinge_sleeves(r), f"door_{idx}_hinge_sleeves"),
        material=mats["metal"],
        name=f"door_{idx}_hinge_sleeves", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_walnut", "honey_brown_wood", "warm_wood_stone", "off_white_steel", "wrought_iron_oak"} else "metal.aluminum_bare"),
    )
    leaf.inertial = Inertial.from_geometry(
        Box((r.leaf_w, r.leaf_t, r.leaf_h)),
        mass=18.0,
        origin=Origin(xyz=(sign * r.leaf_w / 2.0, 0.0, r.leaf_h / 2.0)),
    )
    return leaf


def _apply_arched_leaf_top(r: ResolvedDoubleDoorConfig, leaf: cq.Workplane, sign: float) -> cq.Workplane:
    """Carve a quarter-circle arched top into the leaf so the closed pair
    completes one round arch on the circle r_inner=ARCH_R centered at the
    opening midpoint (arched_glazed L78-L174). The arch center lands at world
    X=0 after the hinge places the leaf, i.e. leaf-local x = sign*ARCH_R... but
    here the leaf body only spans [0, sign*leaf_w] which is narrower than ARCH_R,
    so we clip the top corner using a large cylinder whose center is at the
    meeting edge to give a rising arched profile toward the center.
    """
    # The arch is the quarter circle centered at the MEETING edge corner
    # (x = sign*leaf_w, z = spring), radius leaf_w: it rises from the hinge edge
    # (low, z<=spring) to the meeting/center edge (peak z = spring+leaf_w). After
    # the hinge places the leaf, the two meeting edges sit at world X=0 so the
    # two leaf arches share ONE circle and the closed pair completes the arch.
    # All arch material is bounded strictly to [hinge_edge .. meeting_edge] so it
    # never crosses the center reveal (no door_0/door_1 overlap).
    cx = sign * r.leaf_w / 2.0
    arch_cx = sign * r.leaf_w  # meeting edge (arch circle center)
    # Use a true inward radial offset from the fixed frame circle. Translating an
    # equal-radius circle downward makes the two circles cross near the shoulders;
    # shrinking the moving circle about the fixed center keeps a continuous real
    # clearance around the whole arched cap.
    arch_r = r.arch_r - _ARCH_CLEARANCE
    spring = r.frame_arch_spring_h
    base_top = r.spring_h
    arc_cap_h = arch_r + _ARCH_CLEARANCE + 0.02
    # Block over the spring line, bounded exactly to the leaf body in X (no pad
    # past the meeting edge); pad only the hinge side, which chops nothing extra.
    block = (cq.Workplane("XY").box(r.leaf_w, r.leaf_t * 1.3, arc_cap_h)
             .translate((cx, 0.0, base_top + arc_cap_h / 2.0)))
    keep_cyl = (cq.Workplane("XZ", origin=(arch_cx, 0.0, spring))
                .circle(arch_r).extrude(r.leaf_t * 1.3, both=True))
    arch_block = block.intersect(keep_cyl)
    # Remove everything above the spring line (bounded to the leaf body), then
    # add the arched cap back.
    chop = (cq.Workplane("XY").box(r.leaf_w, r.leaf_t * 1.4, arc_cap_h + 0.04)
            .translate((cx, 0.0, base_top + (arc_cap_h + 0.04) / 2.0)))
    base = leaf.cut(chop)
    try:
        return base.union(arch_block)
    except Exception:
        return leaf


# ===========================================================================
# Hinge wiring (Slot C). Returns list of hinge articulation names.
# ===========================================================================
def _wire_hinge(model, r, frame, leaf, *, idx: int, axis_z: float, spring: bool):
    name = f"frame_to_door_{idx}"
    hinge_x = r.left_hinge_x if idx == 0 else r.right_hinge_x
    if spring:
        limits = MotionLimits(effort=40.0, velocity=2.0,
                              lower=-r.spring_limit, upper=r.spring_limit)
    else:
        limits = MotionLimits(effort=40.0, velocity=2.0, lower=0.0, upper=r.swing_open)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=frame,
        child=leaf,
        origin=Origin(xyz=(hinge_x, r.hinge_y, _FLOOR_Z)),
        axis=(0.0, 0.0, axis_z),
        motion_limits=limits,
    )
    return name


def _wire_lever(model, r, mats, leaf, *, idx: int, sign: float):
    """Optional per-leaf lever sub-joint (REVOLUTE about leaf-local Y spindle).
    Declares a MatingContract on the rose collar (Rule 2)."""
    leaf.visual(
        mesh_from_cadquery(_build_handle_fixed(r, sign), f"door_{idx}_handle"),
        material=mats["metal"],
        name=f"door_{idx}_handle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_walnut", "honey_brown_wood", "warm_wood_stone", "off_white_steel", "wrought_iron_oak"} else "metal.aluminum_bare"),
    )
    lever = model.part(f"door_{idx}_lever")
    lever.visual(
        mesh_from_cadquery(_build_lever(r, sign), f"door_{idx}_lever_bar"),
        material=mats["metal"],
        name=f"door_{idx}_lever_bar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_walnut", "honey_brown_wood", "warm_wood_stone", "off_white_steel", "wrought_iron_oak"} else "metal.aluminum_bare"),
    )
    lever.inertial = Inertial.from_geometry(
        Box((0.10, 0.04, 0.04)), mass=0.2,
        origin=Origin(xyz=(-sign * 0.04, r.leaf_t / 2.0 + 0.02, 0.0)),
    )
    model.articulation(
        f"door_{idx}_to_lever",
        ArticulationType.REVOLUTE,
        parent=leaf,
        child=lever,
        origin=Origin(xyz=(_plate_x(r, sign), 0.0, _spindle_z(r))),
        axis=(0.0, -sign, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=3.0, lower=0.0, upper=0.7),
        mating=MatingContract(
            parent_face_geometry=f"door_{idx}_handle",
            parent_face_side="positive_y",
            child_face_geometry=f"door_{idx}_lever_bar",
            child_face_side="negative_y",
            contact_tol=0.05,
        ),
    )


# ===========================================================================
# Build
# ===========================================================================
def build_double_door(
    config: DoubleDoorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"double_door_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    # --- Frame (root) ---
    frame = model.part("frame")
    for mname, mshape in _build_frame_members(r).items():
        mat_key = "stone" if mname in ("arch_ring", "keystone") else "frame"
        frame.visual(
            mesh_from_cadquery(mshape, f"frame_{mname}"),
            material=mats[mat_key],
            name=f"frame_{mname}", material_class_id=("wood.natural_generic" if r.head_style in {"flat_head", "scalloped_crown_head", "transom_over_flat_head", "arched_leaf_top", "solid_semicircle_head"} else "stone.cut_sedimentary"),
        )
    for idx in (0, 1):
        frame.visual(
            mesh_from_cadquery(_frame_hinge_pin(r, idx), f"frame_hinge_pin_{idx}"),
            material=mats["metal"],
            name=f"frame_hinge_pin_{idx}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_walnut", "honey_brown_wood", "warm_wood_stone", "off_white_steel", "wrought_iron_oak"} else "metal.aluminum_bare"),
        )
    if r.is_arched_leaf:
        frame.visual(
            mesh_from_cadquery(_arched_frame_header(r), "frame_arch_header"),
            material=mats["frame"],
            name="frame_arch_header", material_class_id=("metal.aluminum_bare" if r.palette_style in {"off_white_steel", "anodized_aluminum", "wrought_iron_oak"} else "wood.mahogany_teak_dark"),
        )
    frame.inertial = Inertial.from_geometry(
        Box((r.frame_outer_w, r.jamb_d, r.opening_h + r.head_h + r.base_h)),
        mass=60.0,
        origin=Origin(xyz=(0.0, 0.0, r.opening_h / 2.0)),
    )

    # Both leaves are always real articulated parts. door_0 = +Z hinge at the
    # left jamb; door_1 = -Z at the right jamb. Double-acting spring uses +Z for
    # both with symmetric +/- limits.
    spring = r.is_spring
    leaf0 = _emit_leaf_part(model, r, mats, idx=0, sign=1.0, assets=assets)
    leaf1 = _emit_leaf_part(model, r, mats, idx=1, sign=-1.0, assets=assets)
    _wire_hinge(model, r, frame, leaf0, idx=0, axis_z=1.0, spring=spring)
    axis1_z = 1.0 if spring else -1.0
    _wire_hinge(model, r, frame, leaf1, idx=1, axis_z=axis1_z, spring=spring)
    if r.has_lever:
        _wire_lever(model, r, mats, leaf0, idx=0, sign=1.0)
        _wire_lever(model, r, mats, leaf1, idx=1, sign=-1.0)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_double_door(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_double_door(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_double_door_tests(
    object_model: ArticulatedObject,
    config: DoubleDoorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")

    door0 = object_model.get_part("door_0")
    door1 = object_model.get_part("door_1")
    hinge0 = object_model.get_articulation("frame_to_door_0")
    hinge1 = object_model.get_articulation("frame_to_door_1")

    # ---- Intra-leaf intentional embeddings (infill seated in the leaf). ----
    def _allow_infill_overlaps(door, idx: int):
        leaf_v = f"door_{idx}_leaf"
        names = {v.name for v in door.visuals}
        for vn in names:
            if vn == leaf_v:
                continue
            ctx.allow_overlap(
                door, door, elem_a=vn, elem_b=leaf_v,
                reason="infill feature (glass/muntin/slat/board/brace/handle) seated into the leaf opening or face.",
            )
        # cross-feature overlaps among infill pieces (muntins<->lites, braces<->boards).
        feature_names = sorted(n for n in names if n != leaf_v)
        for i in range(len(feature_names)):
            for j in range(i + 1, len(feature_names)):
                ctx.allow_overlap(
                    door, door, elem_a=feature_names[i], elem_b=feature_names[j],
                    reason="adjacent infill features share glazing/bracing seams.",
                )

    _allow_infill_overlaps(door0, 0)
    _allow_infill_overlaps(door1, 1)

    # ---- Lever captured-shaft overlap + closed-pose leaf/frame seating. ----
    leaf_indices = [0, 1]
    if r.has_lever:
        for idx in leaf_indices:
            lever = object_model.get_part(f"door_{idx}_lever")
            door = object_model.get_part(f"door_{idx}")
            ctx.allow_overlap(
                door, lever, elem_a=f"door_{idx}_handle", elem_b=f"door_{idx}_lever_bar",
                reason="lever neck rides on/through the rose collar as a captured spindle.",
            )
            ctx.allow_overlap(
                door, lever, elem_a=f"door_{idx}_leaf", elem_b=f"door_{idx}_lever_bar",
                reason="lever spindle neck passes through the leaf face into the rose bore (captured spindle).",
            )

    # ---- Baseline connectivity / overlap / mating gates. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity: exactly two independently operable leaves. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("frame root present", "frame" in part_names, details=str(sorted(part_names)))
    ctx.check("door_0 leaf present", "door_0" in part_names)
    ctx.check("door_1 leaf present (second operable leaf)", "door_1" in part_names)

    # ---- Spine: hinge joint topology. ----
    ctx.check(
        "frame_to_door_0 is REVOLUTE about vertical Z at left jamb",
        hinge0.articulation_type == ArticulationType.REVOLUTE and abs(hinge0.axis[2]) > 0.99,
        details=f"type={hinge0.articulation_type} axis={tuple(hinge0.axis)}",
    )
    ctx.check(
        "frame_to_door_0 origin on the left jamb face",
        abs(hinge0.origin.xyz[0] - r.left_hinge_x) < 1e-6,
        details=f"x={hinge0.origin.xyz[0]:.4f} expected={r.left_hinge_x:.4f}",
    )
    if hinge1 is not None:
        ctx.check(
            "frame_to_door_1 is REVOLUTE about vertical Z at right jamb",
            hinge1.articulation_type == ArticulationType.REVOLUTE and abs(hinge1.axis[2]) > 0.99,
            details=f"type={hinge1.articulation_type} axis={tuple(hinge1.axis)}",
        )
        if r.is_spring:
            ctx.check(
                "double-acting spring: both hinges +Z with symmetric +/- limits, rest 0",
                hinge0.axis[2] > 0.99 and hinge1.axis[2] > 0.99
                and hinge0.motion_limits.lower < 0 < hinge0.motion_limits.upper,
                details=f"a0={hinge0.axis[2]} a1={hinge1.axis[2]} lo={hinge0.motion_limits.lower}",
            )
        else:
            ctx.check(
                "both-revolute-opposite: hinges have mirrored +Z / -Z axes",
                hinge0.axis[2] * hinge1.axis[2] < 0,
                details=f"a0={hinge0.axis[2]} a1={hinge1.axis[2]}",
            )

    # ---- Multiplicity present (live count only). ----
    leaf0_names = {v.name for v in door0.visuals}
    if r.infill_style == "raised_panel":
        ctx.check("raised_panel leaf present", "door_0_leaf" in leaf0_names)
    elif r.infill_style == "louvered_slat":
        slats = [n for n in leaf0_names if n.startswith("door_0_slat_")]
        ctx.check(
            "louver slats loop-emitted on door_0",
            len(slats) == r.slat_count,
            details=f"slats={len(slats)} expected={r.slat_count}",
        )
    elif r.infill_style == "divided_lite_glass":
        lites = [n for n in leaf0_names if n.startswith("door_0_lite_")]
        ctx.check(
            "divided lite grid emitted (rows x cols)",
            len(lites) == r.lite_rows * r.lite_cols,
            details=f"lites={len(lites)} expected={r.lite_rows * r.lite_cols}",
        )
    elif r.infill_style == "cross_buck_board":
        boards = [n for n in leaf0_names if n.startswith("door_0_board_")]
        ctx.check(
            "cross-buck boards loop-emitted on door_0",
            len(boards) == r.board_count,
            details=f"boards={len(boards)} expected={r.board_count}",
        )

    # ---- Slot B head present. ----
    frame_names = {v.name for v in frame.visuals}
    if r.head_style == "transom_over_flat_head":
        ctx.check("transom head present", "frame_transom_panel" in frame_names)
    elif r.head_style == "arched_stone_head":
        ctx.check("stone arch ring + keystone present",
                  "frame_arch_ring" in frame_names and "frame_keystone" in frame_names)
    elif r.head_style == "arched_leaf_top":
        ctx.check("arched leaf ring header present (same ARCH_R circle)",
                  "frame_arch_header" in frame_names)
        ctx.check(
            "arched leaves keep a positive clearance below the fixed arch",
            r.frame_arch_spring_h - r.spring_h >= 0.01,
            details=(
                f"frame_spring={r.frame_arch_spring_h:.4f} "
                f"leaf_spring={r.spring_h:.4f}"
            ),
        )
        ctx.check(
            "arched opening has no straight stop-head line",
            "frame_stop_head" not in frame_names,
        )
    elif r.head_style == "solid_semicircle_head":
        ctx.check(
            "filled semicircular head present without straight stop-head line",
            "frame_solid_semicircle" in frame_names
            and "frame_stop_head" not in frame_names,
        )
    else:
        ctx.check("flat head jamb present", "frame_head_jamb" in frame_names)

    # ---- Leaf sizing + ground contact. ----
    leaf0_aabb = ctx.part_element_world_aabb(door0, elem=door0.get_visual("door_0_leaf"))
    if leaf0_aabb is not None:
        (lo, hi) = leaf0_aabb
        w = hi[0] - lo[0]
        h = hi[2] - lo[2]
        ctx.check("door_0 leaf width plausible", 0.6 <= w <= 1.0, details=f"w={w:.3f}")
        ctx.check("door_0 leaf height plausible", 1.0 <= h <= 2.6, details=f"h={h:.3f}")
        ctx.check("door_0 base near floor", lo[2] <= 0.03, details=f"zmin={lo[2]:.4f}")

    # ---- Closed-pose center reveal (MatingContract: leaves meet, no interpenetration). ----
    with ctx.pose({hinge0: 0.0, hinge1: 0.0}):
        leaf0_elem = door0.get_visual("door_0_leaf")
        leaf1_elem = door1.get_visual("door_1_leaf")
        ctx.expect_gap(
            door1, door0, axis="x",
            positive_elem=leaf1_elem, negative_elem=leaf0_elem,
            min_gap=0.0, max_gap=0.06,
            name="closed leaves meet with small center reveal",
        )
        ctx.expect_contact(door0, frame, contact_tol=0.03,
                           name="door_0 hinge edge meets jamb")
        ctx.expect_contact(door1, frame, contact_tol=0.03,
                           name="door_1 hinge edge meets jamb")

    # ---- Independent open poses: each leaf moves while its sibling stays shut. ----
    with ctx.pose({hinge0: 0.0, hinge1: 0.0}):
        c0 = ctx.part_world_aabb(door0)
        c1 = ctx.part_world_aabb(door1)
    open_q = r.swing_open * 0.8 if not r.is_spring else r.spring_limit * 0.8
    with ctx.pose({hinge0: open_q, hinge1: 0.0}):
        o0 = ctx.part_world_aabb(door0)
        still1 = ctx.part_world_aabb(door1)
    with ctx.pose({hinge0: 0.0, hinge1: open_q}):
        still0 = ctx.part_world_aabb(door0)
        o1 = ctx.part_world_aabb(door1)
    if c0 and c1 and o0 and o1 and still0 and still1:
        ctx.check(
            "door_0 opens independently while door_1 stays shut",
            (
                abs(o0[1][1] - c0[1][1]) > 0.2
                or abs(o0[0][1] - c0[0][1]) > 0.2
            )
            and max(
                abs(still1[0][axis] - c1[0][axis])
                for axis in range(3)
            ) < 1e-6,
            details=f"door_0 closed_y={c0[1][1]:.3f} open_y={o0[1][1]:.3f}",
        )
        ctx.check(
            "door_1 opens independently while door_0 stays shut",
            (
                abs(o1[1][1] - c1[1][1]) > 0.2
                or abs(o1[0][1] - c1[0][1]) > 0.2
            )
            and max(
                abs(still0[0][axis] - c0[0][axis])
                for axis in range(3)
            ) < 1e-6,
            details=f"door_1 closed_y={c1[1][1]:.3f} open_y={o1[1][1]:.3f}",
        )

    # ---- Optional lever rotates on the spindle. ----
    if r.has_lever:
        lever_j0 = object_model.get_articulation("door_0_to_lever")
        lever0 = object_model.get_part("door_0_lever")
        with ctx.pose({lever_j0: 0.0}):
            rest = ctx.part_world_aabb(lever0)
        with ctx.pose({lever_j0: 0.7}):
            pressed = ctx.part_world_aabb(lever0)
        if rest is not None and pressed is not None:
            ctx.check(
                "lever tip swings down when pressed",
                pressed[0][2] < rest[0][2] - 0.015,
                details=f"rest={rest[0][2]:.3f} pressed={pressed[0][2]:.3f}",
            )

    # ---- slot_choices recorded with multiplicity encoded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "DoubleDoorConfig",
    "ResolvedDoubleDoorConfig",
    "build_double_door",
    "build_seeded_double_door",
    "config_from_seed",
    "resolve_config",
    "run_double_door_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
