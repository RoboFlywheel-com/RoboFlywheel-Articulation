# SPDX-License-Identifier: Apache-2.0

"""Folding / bi-fold / accordion (concertina) door — modular procedural template.

A folding door is a linear-chain concertina of N rigid hinged leaves. Each leaf
hinges on the vertical meeting edge of the previous leaf, with ALTERNATING ±Z
fold signs so the chain zig-zags (concertinas) when driven. The chain hangs from
a static root frame (header track + left/right jamb + floor track). Every leaf
carries a steel perimeter frame, an infill layer (glass / wood / louver / muntin),
hinge knuckles down a vertical edge, and (track-dependent) end hardware.

DRIVE COUPLING: the fold is a ONE-parameter motion per chain, exactly like the
physical door (the track + panels constrain all hinges together). The jamb
hinge is the driver (limit ``_fold_limit``, derived from the folded-stack
clearance geometry); every interior leaf-to-leaf hinge carries a
``Mimic(driver, multiplier=2.0)`` on the alternating ±Z axes so leaf world
angles alternate exactly ±q. This intentionally replaces the earlier N
independent hinges: independent joint combos reach unphysical poses where
non-adjacent leaves pass through each other (motion QC 穿模), while the coupled
trajectory is exactly the set of physical accordion poses. The N-revolute chain
topology, joint count, and every module/multiplicity axis are unchanged.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Door_folding_Door_Door.md`` and its
``data/records/rec_folding_door_*`` 5-star pool (1 center-biparting parent +
9 slot-fork variants: n2/n6/n8 chains, frameless/solid/louvered/muntin infills,
perimeter/bottom-track suspensions), all synced under ``data/records/``.

Structure (pattern = ``mixed``): a single static root ``frame`` part (mesh chosen
by ``top_track``) + N ``leaf_{i}`` parts in a revolute hinge chain. Three named
module axes plus one multiplicity axis:

  * ``leaf_count`` (N in [2,100]): the multiplicity axis — N leaves emitted in a
    loop, each a part. N drives the chain length / joint count / part count and
    is the dominant topology axis. Encoded into slot_choices as ("leaf_count",
    f"n{N}"). Per-N weighted sampling (small N high-frequency, large N rare).
  * ``leaf_infill`` (5): framed_glass_midrail / frameless_full_glass /
    solid_panel / louvered_slats / muntin_grid_glass — the leaf-local fill layer.
    Swaps the leaf's part visual set; does not touch the hinge frame / topology.
  * ``folding_kinematics`` (2): single_direction_stack (one continuous chain
    stacking against the left jamb) vs center_biparting_bifold (two symmetric
    half-chains hinging the two jambs and biparting at center; even N only).
  * ``top_track`` (3): flush_header_pivot / perimeter_cased_U_channel /
    bottom_track_floor_guided — root mesh + per-leaf end hardware + hinge z_anchor.

3 HARD RULES honored:
  (1) Infill panes / knuckles / handle / pivot pins / rollers are all
      ``leaf.visual(...)`` (Rule 1: non-moving decoration is not a part).
  (2) Every non-FIXED joint is a captured-pin hinge (pin/knuckle through the
      shared meeting edge or jamb), which cannot be modeled as two axis-aligned
      faces in contact, so per AUTHORING.md §B they OMIT
      MatingContract (grandfathered) and are guarded by the flat
      articulation-origin baseline + element-scoped ``allow_overlap``.
  (3) The leaf frame / glass / wood panel are CadQuery meshes
      (``mesh_from_cadquery``); louvered slats use a rotated CadQuery plank;
      no Box/Cylinder downgrade of the sculpted source primitives.

Compatibility gating (resolve_config, spec §"compatibility matrix"):
  * center_biparting_bifold requires even N -> odd N is projected up to N+1.
  * frameless_full_glass ignores mid_rail_fraction (single full opening).
  * bottom_track_floor_guided shifts hinge z_anchor to the guide-rail top.
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
    Inertial,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

LeafInfill = Literal[
    "framed_glass_midrail",
    "frameless_full_glass",
    "solid_panel",
    "louvered_slats",
    "muntin_grid_glass",
]
FoldingKinematics = Literal["single_direction_stack", "center_biparting_bifold"]
TopTrack = Literal[
    "flush_header_pivot",
    "perimeter_cased_U_channel",
    "bottom_track_floor_guided",
]
PaletteStyle = Literal[
    "charcoal_framed_glass",
    "clear_frameless_glass",
    "walnut_solid_panel",
    "oak_louvered",
    "colonial_white_muntin",
    "bronze_framed_glass",
]

LEAF_INFILLS: tuple[LeafInfill, ...] = (
    "framed_glass_midrail",
    "frameless_full_glass",
    "solid_panel",
    "louvered_slats",
    "muntin_grid_glass",
)
FOLDING_KINEMATICS: tuple[FoldingKinematics, ...] = (
    "single_direction_stack",
    "center_biparting_bifold",
)
TOP_TRACKS: tuple[TopTrack, ...] = (
    "flush_header_pivot",
    "perimeter_cased_U_channel",
    "bottom_track_floor_guided",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "charcoal_framed_glass",
    "clear_frameless_glass",
    "walnut_solid_panel",
    "oak_louvered",
    "colonial_white_muntin",
    "bronze_framed_glass",
)

# Infills whose fill material is wood-toned (vs glass).
WOOD_INFILLS: tuple[LeafInfill, ...] = ("solid_panel", "louvered_slats")

N_MIN = 2
N_MAX = 100
# Minimum per-leaf width: below this the cadquery boolean that cuts the framed
# opening goes degenerate (opening width <= 0). resolve_config projects N down so
# leaf_w stays >= this for any opening_width.
_MIN_LEAF_W = 0.050


# ---------------------------------------------------------------------------
# Per-N weighted sampling (spec §Multiplicity): small N high-frequency
# (common 2-8 leaf interior doors), mid N moderate, large N rare and
# strongly down-weighted (accordion partition walls). Mirrors the memory
# note that config_from_seed is a per-N weighted draw over the full range.
# ---------------------------------------------------------------------------
def _leaf_count_population_weights() -> tuple[list[int], list[float]]:
    pop: list[int] = []
    wts: list[float] = []
    for n in range(N_MIN, N_MAX + 1):
        pop.append(n)
        if n <= 8:
            w = 6.0
        elif n <= 16:
            w = 1.6
        elif n <= 32:
            w = 0.35
        else:
            w = 0.06
        wts.append(w)
    return pop, wts


_LEAF_POP, _LEAF_WTS = _leaf_count_population_weights()

# ---------------------------------------------------------------------------
# Palettes. Every .visual material is driven by palette_style. Keys:
#   steel   — leaf perimeter frame + muntin glazing bars + (flush) frame mesh
#   fill    — glass / wood panel / louver slat fill
#   knuckle — bright hinge knuckles + pivot pins + rollers (machined hardware)
#   handle  — pull bar + standoffs
#   frame   — the static root frame mesh (header/jamb/floor)
# Glass fills carry an alpha < 1; wood fills are opaque.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "charcoal_framed_glass": {
        "steel": (0.09, 0.09, 0.10, 1.0),
        "fill": (0.42, 0.50, 0.56, 0.30),
        "knuckle": (0.78, 0.80, 0.82, 1.0),
        "handle": (0.20, 0.21, 0.23, 1.0),
        "frame": (0.12, 0.12, 0.13, 1.0),
    },
    "clear_frameless_glass": {
        "steel": (0.62, 0.64, 0.66, 1.0),
        "fill": (0.60, 0.70, 0.78, 0.24),
        "knuckle": (0.85, 0.87, 0.89, 1.0),
        "handle": (0.40, 0.42, 0.45, 1.0),
        "frame": (0.55, 0.57, 0.60, 1.0),
    },
    "walnut_solid_panel": {
        "steel": (0.26, 0.16, 0.10, 1.0),
        "fill": (0.36, 0.22, 0.13, 1.0),
        "knuckle": (0.72, 0.66, 0.52, 1.0),
        "handle": (0.18, 0.12, 0.08, 1.0),
        "frame": (0.30, 0.19, 0.11, 1.0),
    },
    "oak_louvered": {
        "steel": (0.55, 0.42, 0.27, 1.0),
        "fill": (0.72, 0.55, 0.35, 1.0),
        "knuckle": (0.80, 0.82, 0.84, 1.0),
        "handle": (0.32, 0.24, 0.16, 1.0),
        "frame": (0.60, 0.46, 0.30, 1.0),
    },
    "colonial_white_muntin": {
        "steel": (0.93, 0.93, 0.91, 1.0),
        "fill": (0.66, 0.74, 0.80, 0.26),
        "knuckle": (0.80, 0.80, 0.78, 1.0),
        "handle": (0.50, 0.50, 0.48, 1.0),
        "frame": (0.90, 0.90, 0.88, 1.0),
    },
    "bronze_framed_glass": {
        "steel": (0.30, 0.22, 0.12, 1.0),
        "fill": (0.40, 0.45, 0.42, 0.32),
        "knuckle": (0.74, 0.62, 0.40, 1.0),
        "handle": (0.24, 0.18, 0.10, 1.0),
        "frame": (0.34, 0.25, 0.14, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), from the parent + variant sources.
# World frame: opening centered on X=0; Z from 0 (floor) to OPENING_HEIGHT.
# Leaves hang in the X/Z plane; the bi-fold swings into ±Y. Closed pose: all
# leaves coplanar at Y≈0.
# ---------------------------------------------------------------------------
_OPENING_WIDTH = 2.20
_OPENING_HEIGHT = 2.10

_FRAME_T = 0.035  # steel perimeter / mullion profile width (in-plane)
_FRAME_DEPTH = 0.040  # steel profile depth (along Y / thickness)
_GLASS_T = 0.010  # glass pane thickness (along Y)
_PANEL_T = 0.012  # wood panel insert thickness (along Y)
_MID_RAIL_FRACTION = 0.66

# Header / jamb (shared across tracks).
_HEADER_H = 0.080
_HEADER_DEPTH = 0.060
_JAMB_W = 0.060
_JAMB_DEPTH = 0.060
# Where the leaf_0 / right-jamb hinge line sits relative to the jamb inner face.
# A small NEGATIVE value tucks the hinge line just inside the jamb so (a) the
# leaf_0 hinge stile overlaps the jamb -> geometric contact (fail_if_isolated_parts
# passes), and (b) the frame->leaf jamb joint origin sits on the jamb's
# exact-collision surface, ~|inset| from it, well within the 15mm
# articulation-origin tolerance.
_HINGE_INSET = -0.004

# flush_header_pivot floor track.
_FLOOR_H = 0.030
_FLOOR_DEPTH = 0.060
_HEAD_CLEARANCE = 0.012
_FLOOR_CLEARANCE = 0.012

# perimeter_cased_U_channel.
_PERIM_FLOOR_H = 0.060
_CHANNEL_DEPTH = 0.028
_CHANNEL_W = _FRAME_DEPTH + 0.010
_PIVOT_PIN_R = 0.008
_PIVOT_PIN_LEN = 0.016
_PIVOT_PIN_EMBED = 0.005

# bottom_track_floor_guided.
_BT_FLOOR_H = 0.065
_BT_FLOOR_DEPTH = 0.070
_GUIDE_RAIL_H = 0.014
_GUIDE_RAIL_T = 0.008
_GUIDE_CHANNEL_GAP = 0.028
_ROLLER_R = 0.013
_ROLLER_LEN = 0.028
_ROLLER_STEM_R = 0.006
_BT_HEAD_CLEARANCE = 0.015
_BT_FLOOR_CLEARANCE = 0.004

# Hinge knuckles: slim vertical hinge barrels plus thin leaves. The barrel axis
# is Z-aligned in leaf-local coordinates; keep this hardware small so it reads
# as a hinge, not as large side-mounted rollers.
_KNUCKLE_R = 0.006
_KNUCKLE_LEN = 0.140
_KNUCKLE_COUNT = 5
_HINGE_LEAF_W = 0.018
_HINGE_LEAF_T = 0.003

# Pull handle.
_HANDLE_R = 0.011
_HANDLE_LEN = 0.700
_HANDLE_STANDOFF = 0.040

# Louver slats.
_SLAT_FACE = 0.072
_SLAT_THICK = 0.005
_SLAT_ANGLE_DEG = 35.0
_SLAT_PITCH_TARGET = 0.062

# Muntin grid.
_MUNTIN_BAR_W = 0.008
_MUNTIN_COLS = 3
_MUNTIN_ROWS_UPPER = 3
_MUNTIN_ROWS_LOWER = 2

# ---------------------------------------------------------------------------
# Concertina drive coupling (single-source; AUTHORING.md §B Contract
# 3c). A real bi-fold/accordion door is NOT N independent hinges: the track and
# the panels constrain the chain to a one-parameter fold. Each chain therefore
# has exactly ONE driver joint (the jamb hinge, folding to q) and every interior
# hinge MIMICS the driver at 2q on the alternating +/-Z axes, so the leaf world
# angles alternate exactly +/-q — the physical track-constrained concertina.
# (Previously all N hinges were independent [0, 2.5] revolutes; motion QC then
# legitimately found non-adjacent leaf_i/leaf_j 穿模 at unphysical joint combos
# — a modeling bug, not a tolerance bug.)
# ---------------------------------------------------------------------------
_FOLD_MIMIC_MULTIPLIER = 2.0
# Extra perpendicular margin on top of the two frame half-depths + handle
# standoff/bar protrusion when budgeting the folded stack clearance.
_FOLD_STACK_MARGIN = 0.015
# Longitudinal margin for the handle bar overhanging its leaf free edge.
_FOLD_BAR_MARGIN = 0.004
# Safety backoff (rad) below the analytic self-contact angle.
_FOLD_LIMIT_EPS = 0.05


def _fold_limit(r: ResolvedFoldingDoorConfig) -> float:
    """Upper MotionLimit (rad) of each chain's DRIVER joint (single source).

    On the coupled fold trajectory (leaf world angles alternate +/-q) the only
    self-collision risk is between alternate leaves (i, i+2), which stay
    parallel with:
      * perpendicular separation  = leaf_w * sin(2q)
      * longitudinal stagger: leaf_{i+2} starts at 2*leaf_w*cos(q)^2 along the
        leaf direction, vs leaf_i spanning [0, leaf_w].
    A fold angle q is safe if the pair is longitudinally staggered
    (2*cos(q)^2 >= 1 + bar/leaf_w, i.e. up to ~pi/4) OR perpendicularly clear
    (leaf_w*sin(2q) >= t_eff). t_eff budgets two frame half-depths plus the
    pull-handle standoff+bar protrusion; ``bar`` budgets the handle bar
    overhanging its leaf's free edge into the staggered gap. Wide leaves fold
    nearly flat (q -> ~1.5 rad); narrow leaves cap near pi/4 where the stagger
    still guarantees clearance.
    """
    t_eff = r.frame_depth + _HANDLE_STANDOFF + _HANDLE_R + _FOLD_STACK_MARGIN
    bar = _HANDLE_R + _FOLD_BAR_MARGIN
    stagger_end = math.acos(_clamp(bar / r.leaf_w, 0.0, 1.0)) / 2.0
    k = t_eff / r.leaf_w
    if k < 1.0 and math.asin(k) / 2.0 <= stagger_end:
        # Perpendicular-clearance regime takes over before the stagger runs out.
        q_max = (math.pi - math.asin(k)) / 2.0
    else:
        q_max = stagger_end
    return min(q_max - _FOLD_LIMIT_EPS, 1.50)


@dataclass(frozen=True)
class FoldingDoorConfig:
    leaf_infill: LeafInfill | None = None
    folding_kinematics: FoldingKinematics | None = None
    top_track: TopTrack | None = None
    leaf_count: int | None = None
    palette_style: PaletteStyle = "charcoal_framed_glass"
    opening_width: float = _OPENING_WIDTH
    opening_height: float = _OPENING_HEIGHT
    frame_t: float = _FRAME_T
    mid_rail_fraction: float = _MID_RAIL_FRACTION
    handle_len: float = _HANDLE_LEN
    glass_tint_alpha: float = 0.30
    name: str = "folding_door"


@dataclass(frozen=True)
class ResolvedFoldingDoorConfig:
    leaf_infill: LeafInfill
    folding_kinematics: FoldingKinematics
    top_track: TopTrack
    leaf_count: int
    palette_style: PaletteStyle
    # Concrete geometry.
    opening_width: float
    opening_height: float
    frame_t: float
    frame_depth: float
    mid_rail_fraction: float
    leaf_w: float
    leaf_h: float
    leaf_bottom_z: float
    leaf_top_z: float
    # Leaf-local Z is centered: local z=0 is the leaf vertical MID-height, so the
    # hinge joint origin (at local z=0) lands on the solid mid-jamb rather than on
    # the floor/threshold/channel zone (which is far from frame collision surface
    # for the perimeter / bottom-track roots). lz0 = local z of the leaf bottom.
    lz0: float
    z_anchor: float  # world Z where each leaf-local z=0 maps (hinge origin Z = mid-height)
    left_hinge_x: float
    handle_len: float
    glass_tint_alpha: float
    name: str

    @property
    def hinge_x(self) -> list[float]:
        return [self.left_hinge_x + i * self.leaf_w for i in range(self.leaf_count + 1)]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> FoldingDoorConfig:
    rng = random.Random(seed)
    leaf_count = rng.choices(_LEAF_POP, weights=_LEAF_WTS, k=1)[0]
    return FoldingDoorConfig(
        leaf_infill=rng.choice(LEAF_INFILLS),
        folding_kinematics=rng.choice(FOLDING_KINEMATICS),
        top_track=rng.choice(TOP_TRACKS),
        leaf_count=leaf_count,
        palette_style=rng.choice(PALETTE_STYLES),
        opening_width=round(rng.uniform(1.0, 6.0), 4),
        opening_height=round(rng.uniform(2.0, 2.4), 4),
        frame_t=round(rng.uniform(0.025, 0.050), 4),
        mid_rail_fraction=round(rng.uniform(0.55, 0.72), 4),
        handle_len=round(rng.uniform(0.50, 0.90), 4),
        glass_tint_alpha=round(rng.uniform(0.22, 0.40), 4),
        name=f"seeded_folding_door_{seed}",
    )


def resolve_config(config: FoldingDoorConfig | None = None) -> ResolvedFoldingDoorConfig:
    cfg = config or FoldingDoorConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    leaf_infill = _pick(cfg.leaf_infill, LEAF_INFILLS)
    folding_kinematics = _pick(cfg.folding_kinematics, FOLDING_KINEMATICS)
    top_track = _pick(cfg.top_track, TOP_TRACKS)

    leaf_count = int(cfg.leaf_count) if cfg.leaf_count is not None else 4
    leaf_count = int(_clamp(leaf_count, N_MIN, N_MAX))

    # --- Compatibility gating. ---
    # center_biparting requires even N (two equal half-chains); project odd up.
    if folding_kinematics == "center_biparting_bifold" and leaf_count % 2 == 1:
        leaf_count = min(N_MAX, leaf_count + 1)
        if leaf_count % 2 == 1:  # hit the ceiling at an odd value
            leaf_count -= 1

    opening_width = _clamp(cfg.opening_width, 1.0, 6.0)
    opening_height = _clamp(cfg.opening_height, 2.0, 2.4)
    frame_t = _clamp(cfg.frame_t, 0.025, 0.050)
    mid_rail_fraction = _clamp(cfg.mid_rail_fraction, 0.55, 0.72)
    handle_len = _clamp(cfg.handle_len, 0.50, 0.90)
    glass_tint_alpha = _clamp(cfg.glass_tint_alpha, 0.22, 0.40)

    # --- Track-dependent vertical layout (leaf top/bottom Z). ---
    if top_track == "perimeter_cased_U_channel":
        header_bottom_z = opening_height - _HEADER_H
        threshold_top_z = _PERIM_FLOOR_H
        leaf_top_z = header_bottom_z + _CHANNEL_DEPTH - 0.005
        leaf_bottom_z = threshold_top_z - _CHANNEL_DEPTH + 0.005
    elif top_track == "bottom_track_floor_guided":
        leaf_top_z = (opening_height - _HEADER_H) - _BT_HEAD_CLEARANCE
        leaf_bottom_z = _BT_FLOOR_H + _GUIDE_RAIL_H + _BT_FLOOR_CLEARANCE
    else:  # flush_header_pivot
        leaf_top_z = (opening_height - _HEADER_H) - _HEAD_CLEARANCE
        leaf_bottom_z = _FLOOR_H + _FLOOR_CLEARANCE

    leaf_h = leaf_top_z - leaf_bottom_z
    # Center the leaf-local Z origin at mid-height (see ResolvedConfig.lz0).
    lz0 = -leaf_h / 2.0
    z_anchor = leaf_bottom_z + leaf_h / 2.0

    # --- Leaf width (equation) + inequality projection. ---
    # The chain fills the clear opening between the jambs. The first/last hinge
    # lines sit HINGE_INSET inboard of each jamb's INNER face: that puts the
    # frame->leaf jamb joint origin a few mm inside the opening, where the
    # frame's (slightly inset) exact-collision surface is within the 15mm
    # articulation-origin tolerance — anchoring the hinge on real frame material
    # rather than the jamb center (which is ~30mm from the nearest frame surface).
    left_hinge_x = -opening_width / 2.0 + _JAMB_W + _HINGE_INSET
    hinge_span = 2.0 * abs(left_hinge_x)

    # Inequality (spec): N must "回缩" (back off) so each leaf is wide enough to
    # cut a valid framed opening. Below _MIN_LEAF_W the cadquery boolean that
    # carves the glass/panel opening out of the frame goes degenerate (the
    # opening width drops to <=0). Project N down to the largest count that keeps
    # leaf_w >= _MIN_LEAF_W; for center-biparting keep N even.
    max_n_for_width = max(N_MIN, int(hinge_span / _MIN_LEAF_W))
    if leaf_count > max_n_for_width:
        leaf_count = max_n_for_width
        if folding_kinematics == "center_biparting_bifold" and leaf_count % 2 == 1:
            leaf_count = max(N_MIN, leaf_count - 1)
    leaf_w = hinge_span / leaf_count

    # Inequality: a leaf must hold two side stiles + an opening: LEAF_W >= 4*FRAME_T.
    # If too thin (large N + wide frame), shrink frame_t first, then clamp it.
    for _ in range(20):
        if leaf_w >= 4.0 * frame_t:
            break
        frame_t = max(0.012, frame_t - 0.003)
    if leaf_w < 4.0 * frame_t:
        frame_t = max(0.008, leaf_w / 4.0 - 0.0005)

    return ResolvedFoldingDoorConfig(
        leaf_infill=leaf_infill,
        folding_kinematics=folding_kinematics,
        top_track=top_track,
        leaf_count=leaf_count,
        palette_style=palette_style,
        opening_width=opening_width,
        opening_height=opening_height,
        frame_t=frame_t,
        frame_depth=_FRAME_DEPTH,
        mid_rail_fraction=mid_rail_fraction,
        leaf_w=leaf_w,
        leaf_h=leaf_h,
        leaf_bottom_z=leaf_bottom_z,
        leaf_top_z=leaf_top_z,
        lz0=lz0,
        z_anchor=z_anchor,
        left_hinge_x=left_hinge_x,
        handle_len=min(handle_len, leaf_h * 0.6),
        glass_tint_alpha=glass_tint_alpha,
        name=cfg.name or "folding_door",
    )


def with_overrides(config: FoldingDoorConfig, **kwargs: object) -> FoldingDoorConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: FoldingDoorConfig | ResolvedFoldingDoorConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedFoldingDoorConfig) else resolve_config(config)
    return (
        ("leaf_infill", r.leaf_infill),
        ("folding_kinematics", r.folding_kinematics),
        ("top_track", r.top_track),
        ("leaf_count", f"n{r.leaf_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Leaf-local CadQuery geometry (shared across infills). Authored in the
# leaf-local hinge frame: local X 0..LEAF_W (hinge edge x=0, free edge
# x=LEAF_W), local Z 0..LEAF_H, local Y = thickness centered at y=0.
# ---------------------------------------------------------------------------
def _leaf_frame_shape(r: ResolvedFoldingDoorConfig, *, midrail: bool) -> cq.Workplane:
    """Steel perimeter frame, optionally with a horizontal mid-rail.

    midrail=True -> two openings (upper + lower split by the mid-rail).
    midrail=False -> one large edge-to-edge opening (frameless).
    """
    w, h, t, d = r.leaf_w, r.leaf_h, r.frame_t, r.frame_depth
    outer = cq.Workplane("XY").box(w, d, h, centered=(False, True, False))

    if not midrail:
        cx0, cx1 = t, w - t
        cz0, cz1 = t, h - t
        cut = (
            cq.Workplane("XY")
            .transformed(offset=((cx0 + cx1) / 2.0, 0.0, (cz0 + cz1) / 2.0))
            .box(cx1 - cx0, d + 0.01, cz1 - cz0)
        )
        return outer.cut(cut).translate((0.0, 0.0, r.lz0))

    mid_z = h * r.mid_rail_fraction
    half_rail = t / 2.0
    up_x0, up_x1 = t, w - t
    up_z0, up_z1 = mid_z + half_rail, h - t
    upper_cut = (
        cq.Workplane("XY")
        .transformed(offset=((up_x0 + up_x1) / 2.0, 0.0, (up_z0 + up_z1) / 2.0))
        .box(up_x1 - up_x0, d + 0.01, up_z1 - up_z0)
    )
    lo_x0, lo_x1 = t, w - t
    lo_z0, lo_z1 = t, mid_z - half_rail
    lower_cut = (
        cq.Workplane("XY")
        .transformed(offset=((lo_x0 + lo_x1) / 2.0, 0.0, (lo_z0 + lo_z1) / 2.0))
        .box(lo_x1 - lo_x0, d + 0.01, lo_z1 - lo_z0)
    )
    return outer.cut(upper_cut).cut(lower_cut).translate((0.0, 0.0, r.lz0))


def _glass_two_pane_shape(r: ResolvedFoldingDoorConfig) -> cq.Workplane:
    """Upper + (short) lower glass panes for the midrail frame, rebated."""
    w, h, t = r.leaf_w, r.leaf_h, r.frame_t
    mid_z = h * r.mid_rail_fraction
    half_rail = t / 2.0
    rebate = min(0.006, t * 0.4)
    up_x0, up_x1 = t - rebate, w - t + rebate
    up_z0, up_z1 = mid_z + half_rail - rebate, h - t + rebate
    upper = (
        cq.Workplane("XY")
        .transformed(offset=((up_x0 + up_x1) / 2.0, 0.0, (up_z0 + up_z1) / 2.0))
        .box(up_x1 - up_x0, _GLASS_T, up_z1 - up_z0)
    )
    lo_x0, lo_x1 = t - rebate, w - t + rebate
    lo_z0, lo_z1 = t - rebate, mid_z - half_rail + rebate
    lower = (
        cq.Workplane("XY")
        .transformed(offset=((lo_x0 + lo_x1) / 2.0, 0.0, (lo_z0 + lo_z1) / 2.0))
        .box(lo_x1 - lo_x0, _GLASS_T, lo_z1 - lo_z0)
    )
    return upper.union(lower).translate((0.0, 0.0, r.lz0))


def _glass_full_pane_shape(r: ResolvedFoldingDoorConfig) -> cq.Workplane:
    """Single full edge-to-edge glass pane (frameless), rebated under the rail."""
    w, h, t = r.leaf_w, r.leaf_h, r.frame_t
    rebate = min(0.006, t * 0.4)
    px0, px1 = t - rebate, w - t + rebate
    pz0, pz1 = t - rebate, h - t + rebate
    return (
        cq.Workplane("XY")
        .transformed(offset=((px0 + px1) / 2.0, 0.0, (pz0 + pz1) / 2.0))
        .box(px1 - px0, _GLASS_T, pz1 - pz0)
        .translate((0.0, 0.0, r.lz0))
    )


def _wood_panel_shape(r: ResolvedFoldingDoorConfig) -> cq.Workplane:
    """Solid opaque wood panel insert filling the whole opening, rebated."""
    w, h, t = r.leaf_w, r.leaf_h, r.frame_t
    rebate = min(0.006, t * 0.4)
    px0, px1 = t - rebate, w - t + rebate
    pz0, pz1 = t - rebate, h - t + rebate
    return (
        cq.Workplane("XY")
        .transformed(offset=((px0 + px1) / 2.0, 0.0, (pz0 + pz1) / 2.0))
        .box(px1 - px0, _PANEL_T, pz1 - pz0)
        .translate((0.0, 0.0, r.lz0))
    )


def _slat_shape(width: float) -> cq.Workplane:
    """One louver slat: a thin plank tilted SLAT_ANGLE about X, centered."""
    return (
        cq.Workplane("XY")
        .transformed(rotate=(_SLAT_ANGLE_DEG, 0.0, 0.0))
        .box(width, _SLAT_FACE, _SLAT_THICK)
    )


# ---------------------------------------------------------------------------
# Root frame meshes (top_track axis). Each is a single CadQuery union of
# header track + left/right jamb + floor track (+ track-specific channels /
# rails). The leaf_0 / right-jamb hinge lines sit _HINGE_INSET inboard of the
# jamb inner faces (see resolve_config) so each jamb joint origin lands on the
# frame's exact-collision surface.
# ---------------------------------------------------------------------------
def _root_flush(r: ResolvedFoldingDoorConfig) -> cq.Workplane:
    half_w = r.opening_width / 2.0
    oh = r.opening_height
    header = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, oh - _HEADER_H / 2.0))
        .box(r.opening_width, _HEADER_DEPTH, _HEADER_H)
    )
    left_jamb = (
        cq.Workplane("XY")
        .transformed(offset=(-half_w + _JAMB_W / 2.0, 0.0, oh / 2.0))
        .box(_JAMB_W, _JAMB_DEPTH, oh)
    )
    right_jamb = (
        cq.Workplane("XY")
        .transformed(offset=(half_w - _JAMB_W / 2.0, 0.0, oh / 2.0))
        .box(_JAMB_W, _JAMB_DEPTH, oh)
    )
    floor = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, _FLOOR_H / 2.0))
        .box(r.opening_width, _FLOOR_DEPTH, _FLOOR_H)
    )
    root = header.union(left_jamb).union(right_jamb).union(floor)
    return root


def _root_perimeter(r: ResolvedFoldingDoorConfig) -> cq.Workplane:
    half_w = r.opening_width / 2.0
    oh = r.opening_height
    header_bottom_z = oh - _HEADER_H
    threshold_top_z = _PERIM_FLOOR_H
    header = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, oh - _HEADER_H / 2.0))
        .box(r.opening_width, _HEADER_DEPTH, _HEADER_H)
    )
    # Channel runs between the two jambs (clear span), stopping inside each jamb
    # so its cut edge never coincides with the leaf_0 hinge line at the jamb
    # center (which would leave the hinge origin in cut air at a coincident face).
    channel_w_x = max(0.05, r.opening_width - 3.0 * _JAMB_W)
    header_channel = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, header_bottom_z + _CHANNEL_DEPTH / 2.0))
        .box(channel_w_x, _CHANNEL_W, _CHANNEL_DEPTH)
    )
    header = header.cut(header_channel)
    left_jamb = (
        cq.Workplane("XY")
        .transformed(offset=(-half_w + _JAMB_W / 2.0, 0.0, oh / 2.0))
        .box(_JAMB_W, _JAMB_DEPTH, oh)
    )
    right_jamb = (
        cq.Workplane("XY")
        .transformed(offset=(half_w - _JAMB_W / 2.0, 0.0, oh / 2.0))
        .box(_JAMB_W, _JAMB_DEPTH, oh)
    )
    threshold = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, _PERIM_FLOOR_H / 2.0))
        .box(r.opening_width, _FLOOR_DEPTH, _PERIM_FLOOR_H)
    )
    threshold_channel = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, threshold_top_z - _CHANNEL_DEPTH / 2.0))
        .box(channel_w_x, _CHANNEL_W, _CHANNEL_DEPTH)
    )
    threshold = threshold.cut(threshold_channel)
    root = header.union(left_jamb).union(right_jamb).union(threshold)
    return root


def _root_bottom_track(r: ResolvedFoldingDoorConfig) -> cq.Workplane:
    half_w = r.opening_width / 2.0
    oh = r.opening_height
    header = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, oh - _HEADER_H / 2.0))
        .box(r.opening_width, _HEADER_DEPTH, _HEADER_H)
    )
    left_jamb = (
        cq.Workplane("XY")
        .transformed(offset=(-half_w + _JAMB_W / 2.0, 0.0, oh / 2.0))
        .box(_JAMB_W, _JAMB_DEPTH, oh)
    )
    right_jamb = (
        cq.Workplane("XY")
        .transformed(offset=(half_w - _JAMB_W / 2.0, 0.0, oh / 2.0))
        .box(_JAMB_W, _JAMB_DEPTH, oh)
    )
    floor_base = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, _BT_FLOOR_H / 2.0))
        .box(r.opening_width, _BT_FLOOR_DEPTH, _BT_FLOOR_H)
    )
    half_gap = _GUIDE_CHANNEL_GAP / 2.0
    rail_len = (r.opening_width - _JAMB_W) - _GUIDE_CHANNEL_GAP
    rail_len = max(0.05, rail_len)
    left_rail = (
        cq.Workplane("XY")
        .transformed(
            offset=(-half_gap - _GUIDE_RAIL_T / 2.0, 0.0, _BT_FLOOR_H + _GUIDE_RAIL_H / 2.0)
        )
        .box(rail_len, _GUIDE_RAIL_T, _GUIDE_RAIL_H)
    )
    right_rail = (
        cq.Workplane("XY")
        .transformed(
            offset=(half_gap + _GUIDE_RAIL_T / 2.0, 0.0, _BT_FLOOR_H + _GUIDE_RAIL_H / 2.0)
        )
        .box(rail_len, _GUIDE_RAIL_T, _GUIDE_RAIL_H)
    )
    root = (
        header.union(left_jamb)
        .union(right_jamb)
        .union(floor_base)
        .union(left_rail)
        .union(right_rail)
    )
    return root


_ROOT_BUILDERS = {
    "flush_header_pivot": _root_flush,
    "perimeter_cased_U_channel": _root_perimeter,
    "bottom_track_floor_guided": _root_bottom_track,
}


def _build_frame(model: ArticulatedObject, r: ResolvedFoldingDoorConfig, mats, *, assets):
    frame = model.part("frame")
    frame.visual(
        mesh_from_cadquery(_ROOT_BUILDERS[r.top_track](r), "frame_shell", assets=assets),
        material=mats["frame"],
        name="frame_shell", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "bronze_framed_glass"} else "wood.oak"),
    )
    frame.inertial = Inertial.from_geometry(
        Box((r.opening_width, _HEADER_DEPTH, r.opening_height)),
        mass=20.0,
        origin=Origin(xyz=(0.0, 0.0, r.opening_height / 2.0)),
    )
    return frame


# ---------------------------------------------------------------------------
# Infill emission (Rule 1: inline visuals on the leaf part). The frame mesh
# (one per N) is shared by passing the prebuilt cadquery shape in.
# ---------------------------------------------------------------------------
def _emit_infill(leaf, name: str, r: ResolvedFoldingDoorConfig, mats, *, assets):
    infill = r.leaf_infill
    midrail = infill != "frameless_full_glass"

    leaf.visual(
        mesh_from_cadquery(_leaf_frame_shape(r, midrail=midrail), f"{name}_frame", assets=assets),
        material=mats["steel"],
        name=f"{name}_frame", material_class_id=("metal.stainless_matte" if r.palette_style in {"clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin", "bronze_framed_glass"} else "metal.blackened_gunmetal"),
    )

    if infill == "framed_glass_midrail":
        leaf.visual(
            mesh_from_cadquery(_glass_two_pane_shape(r), f"{name}_glass", assets=assets),
            material=mats["fill"],
            name=f"{name}_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin"} else "glass.smoked_tinted"),
        )
    elif infill == "frameless_full_glass":
        leaf.visual(
            mesh_from_cadquery(_glass_full_pane_shape(r), f"{name}_glass", assets=assets),
            material=mats["fill"],
            name=f"{name}_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin"} else "glass.smoked_tinted"),
        )
    elif infill == "solid_panel":
        leaf.visual(
            mesh_from_cadquery(_wood_panel_shape(r), f"{name}_wood_panel", assets=assets),
            material=mats["fill"],
            name=f"{name}_wood_panel", material_class_id=("wood.oak" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "oak_louvered", "colonial_white_muntin", "bronze_framed_glass"} else "wood.walnut_dark"),
        )
    elif infill == "louvered_slats":
        _emit_louver_slats(leaf, name, r, mats, assets=assets)
    elif infill == "muntin_grid_glass":
        _emit_muntin_grid(leaf, name, r, mats)


def _emit_louver_slats(leaf, name: str, r: ResolvedFoldingDoorConfig, mats, *, assets):
    """Horizontal tilted louver slats filling the upper + lower openings."""
    slat_mesh = mesh_from_cadquery(
        _slat_shape(r.leaf_w - 2.0 * r.frame_t), f"{name}_slat", assets=assets
    )
    mid_z = r.leaf_h * r.mid_rail_fraction
    half_rail = r.frame_t / 2.0
    slat_center_x = r.leaf_w / 2.0
    for tag, z_lo, z_hi in (
        ("upper", mid_z + half_rail, r.leaf_h - r.frame_t),
        ("lower", r.frame_t, mid_z - half_rail),
    ):
        opening_h = z_hi - z_lo
        if opening_h <= 0:
            continue
        n = max(3, round(opening_h / _SLAT_PITCH_TARGET))
        pitch = opening_h / n
        for i in range(n):
            z = z_lo + pitch * (i + 0.5)
            leaf.visual(
                slat_mesh,
                origin=Origin(xyz=(slat_center_x, 0.0, z + r.lz0)),
                material=mats["fill"],
                name=f"{name}_slat_{tag}_{i}", material_class_id=("wood.oak" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "oak_louvered", "colonial_white_muntin", "bronze_framed_glass"} else "wood.walnut_dark"),
            )


def _emit_muntin_grid(leaf, name: str, r: ResolvedFoldingDoorConfig, mats):
    """Muntin glazing bars + small glass lites dividing each opening."""
    w, h, t = r.leaf_w, r.leaf_h, r.frame_t
    mid_z = h * r.mid_rail_fraction
    half_rail = t / 2.0
    for tag, x0, x1, z0, z1, n_cols, n_rows in (
        ("upper", t, w - t, mid_z + half_rail, h - t, _MUNTIN_COLS, _MUNTIN_ROWS_UPPER),
        ("lower", t, w - t, t, mid_z - half_rail, _MUNTIN_COLS, _MUNTIN_ROWS_LOWER),
    ):
        width = x1 - x0
        height = z1 - z0
        if width <= 0 or height <= 0:
            continue
        col_spacing = width / n_cols
        row_spacing = height / n_rows
        for i in range(1, n_rows):
            z_bar = z0 + i * row_spacing
            leaf.visual(
                Box((width, r.frame_depth * 0.8, _MUNTIN_BAR_W)),
                origin=Origin(xyz=((x0 + x1) / 2.0, 0.0, z_bar + r.lz0)),
                material=mats["steel"],
                name=f"{name}_muntin_h_{tag}_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "bronze_framed_glass"} else "metal.paint_coated"),
            )
        for j in range(1, n_cols):
            x_bar = x0 + j * col_spacing
            leaf.visual(
                Box((_MUNTIN_BAR_W, r.frame_depth * 0.8, height)),
                origin=Origin(xyz=(x_bar, 0.0, (z0 + z1) / 2.0 + r.lz0)),
                material=mats["steel"],
                name=f"{name}_muntin_v_{tag}_{j}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "bronze_framed_glass"} else "metal.paint_coated"),
            )
        lite_inset = 0.001
        for i in range(n_rows):
            for j in range(n_cols):
                cx0 = x0 + j * col_spacing + lite_inset
                cx1 = x0 + (j + 1) * col_spacing - lite_inset
                cz0 = z0 + i * row_spacing + lite_inset
                cz1 = z0 + (i + 1) * row_spacing - lite_inset
                leaf.visual(
                    Box((cx1 - cx0, _GLASS_T, cz1 - cz0)),
                    origin=Origin(xyz=((cx0 + cx1) / 2.0, 0.0, (cz0 + cz1) / 2.0 + r.lz0)),
                    material=mats["fill"],
                    name=f"{name}_lite_{tag}_{i}_{j}", material_class_id=("glass.clear_transparent" if r.palette_style in {"clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin"} else "glass.smoked_tinted"),
                )


# ---------------------------------------------------------------------------
# End hardware (top_track axis): knuckles always; perimeter -> pivot pins;
# bottom_track -> roller + stem. All inline visuals on the leaf (Rule 1).
# ---------------------------------------------------------------------------
def _emit_knuckles(leaf, name: str, r: ResolvedFoldingDoorConfig, mats, *, edge_x: float):
    span = r.leaf_h - 2.0 * r.frame_t
    z0 = r.frame_t + _KNUCKLE_LEN / 2.0
    leaf_w = min(_HINGE_LEAF_W, max(0.006, r.frame_t * 0.55))
    plate_depth = min(r.frame_depth * 0.74, _KNUCKLE_R * 2.0 + 0.010)
    for k in range(_KNUCKLE_COUNT):
        frac = k / (_KNUCKLE_COUNT - 1)
        z = z0 + frac * max(0.0, span - _KNUCKLE_LEN)
        side = -1.0 if edge_x > r.leaf_w / 2.0 else 1.0
        plate_x = edge_x + side * leaf_w / 2.0
        leaf.visual(
            Cylinder(radius=_KNUCKLE_R, length=_KNUCKLE_LEN),
            origin=Origin(xyz=(edge_x, 0.0, z + r.lz0)),
            material=mats["knuckle"],
            name=f"{name}_hinge_barrel_{k}", material_class_id=("metal.chrome_polished" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin"} else "metal.bronze_cast"),
        )
        leaf.visual(
            Box((leaf_w, _HINGE_LEAF_T, _KNUCKLE_LEN * 0.86)),
            origin=Origin(xyz=(plate_x, -plate_depth / 2.0, z + r.lz0)),
            material=mats["knuckle"],
            name=f"{name}_hinge_leaf_front_{k}", material_class_id=("metal.chrome_polished" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin"} else "metal.bronze_cast"),
        )
        leaf.visual(
            Box((leaf_w, _HINGE_LEAF_T, _KNUCKLE_LEN * 0.86)),
            origin=Origin(xyz=(plate_x, plate_depth / 2.0, z + r.lz0)),
            material=mats["knuckle"],
            name=f"{name}_hinge_leaf_back_{k}", material_class_id=("metal.chrome_polished" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin"} else "metal.bronze_cast"),
        )


def _emit_track_hardware(leaf, name: str, r: ResolvedFoldingDoorConfig, mats, *, edge_x: float):
    # Leaf-local Z is centered (z=0 = mid-height); leaf bottom = r.lz0, top = r.lz0 + leaf_h.
    leaf_bot = r.lz0
    leaf_top = r.lz0 + r.leaf_h
    if r.top_track == "perimeter_cased_U_channel":
        exposed = _PIVOT_PIN_LEN - _PIVOT_PIN_EMBED
        leaf.visual(
            Cylinder(radius=_PIVOT_PIN_R, length=_PIVOT_PIN_LEN),
            origin=Origin(xyz=(edge_x, 0.0, leaf_top + exposed / 2.0)),
            material=mats["knuckle"],
            name=f"{name}_pivot_top", material_class_id=("metal.chrome_polished" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin"} else "metal.bronze_cast"),
        )
        leaf.visual(
            Cylinder(radius=_PIVOT_PIN_R, length=_PIVOT_PIN_LEN),
            origin=Origin(xyz=(edge_x, 0.0, leaf_bot - exposed / 2.0)),
            material=mats["knuckle"],
            name=f"{name}_pivot_bot", material_class_id=("metal.chrome_polished" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin"} else "metal.bronze_cast"),
        )
    elif r.top_track == "bottom_track_floor_guided":
        roller_x = r.frame_t / 2.0
        roller_z = leaf_bot - _ROLLER_R
        stem_top = leaf_bot + 0.002
        stem_bot = roller_z
        stem_len = stem_top - stem_bot
        leaf.visual(
            Cylinder(radius=_ROLLER_STEM_R, length=stem_len),
            origin=Origin(xyz=(roller_x, 0.0, (stem_top + stem_bot) / 2.0)),
            material=mats["knuckle"],
            name=f"{name}_roller_stem", material_class_id=("metal.chrome_polished" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin"} else "metal.bronze_cast"),
        )
        leaf.visual(
            Cylinder(radius=_ROLLER_R, length=_ROLLER_LEN),
            origin=Origin(xyz=(roller_x, 0.0, roller_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["knuckle"],
            name=f"{name}_roller", material_class_id=("metal.chrome_polished" if r.palette_style in {"charcoal_framed_glass", "clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin"} else "metal.bronze_cast"),
        )


def _emit_handle(leaf, name: str, r: ResolvedFoldingDoorConfig, mats):
    """Slim vertical pull bar on the leaf's free (meeting) edge, on standoffs."""
    handle_x = r.leaf_w - r.frame_t / 2.0
    handle_y = -(r.frame_depth / 2.0 + _HANDLE_STANDOFF)
    handle_z = r.lz0 + r.leaf_h * 0.46
    handle_len = r.handle_len
    for dz, sfx in ((handle_len / 2.0 - 0.05, "top"), (-(handle_len / 2.0 - 0.05), "bot")):
        leaf.visual(
            Cylinder(radius=0.006, length=_HANDLE_STANDOFF + r.frame_depth / 2.0),
            origin=Origin(
                xyz=(handle_x, handle_y / 2.0, handle_z + dz), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=mats["handle"],
            name=f"{name}_handle_standoff_{sfx}", material_class_id=("metal.brushed_silver" if r.palette_style in {"clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin", "bronze_framed_glass"} else "metal.blackened_gunmetal"),
        )
    leaf.visual(
        Cylinder(radius=_HANDLE_R, length=handle_len),
        origin=Origin(xyz=(handle_x, handle_y, handle_z)),
        material=mats["handle"],
        name=f"{name}_handle_bar", material_class_id=("metal.brushed_silver" if r.palette_style in {"clear_frameless_glass", "walnut_solid_panel", "oak_louvered", "colonial_white_muntin", "bronze_framed_glass"} else "metal.blackened_gunmetal"),
    )


def _build_leaf(
    model: ArticulatedObject,
    name: str,
    r: ResolvedFoldingDoorConfig,
    mats,
    *,
    assets,
    knuckle_edge_x: float,
    with_handle: bool,
):
    leaf = model.part(name)
    _emit_infill(leaf, name, r, mats, assets=assets)
    _emit_knuckles(leaf, name, r, mats, edge_x=knuckle_edge_x)
    _emit_track_hardware(leaf, name, r, mats, edge_x=0.0)
    if with_handle:
        _emit_handle(leaf, name, r, mats)
    leaf.inertial = Inertial.from_geometry(
        Box((r.leaf_w, r.frame_depth, r.leaf_h)),
        mass=max(2.0, 6.0 * r.leaf_w),
        origin=Origin(xyz=(r.leaf_w / 2.0, 0.0, 0.0)),  # local z=0 is leaf mid-height
    )
    return leaf


# ---------------------------------------------------------------------------
# Kinematics (folding_kinematics axis). Emits N leaves + N revolute joints.
# ---------------------------------------------------------------------------
def _build_single_chain(model, r: ResolvedFoldingDoorConfig, frame, mats, *, assets) -> dict:
    """One continuous chain: frame -> leaf_0 -> ... -> leaf_{N-1}, stacking the
    whole door against the left jamb. axis alternates +Z(even)/-Z(odd).

    Drive-coupled: ``frame_to_leaf_0`` is the single driver (limit
    ``_fold_limit``); every interior hinge mimics it at 2x on the alternating
    axes, so leaf world angles alternate exactly +/-q (track concertina)."""
    n = r.leaf_count
    hinge_x = r.hinge_x
    q_max = _fold_limit(r)
    # Handle on the leaf whose free edge is nearest world X=0 (center).
    handle_idx = _nearest_free_edge_to_center(r, hinge_x)
    for i in range(n):
        _build_leaf(
            model,
            f"leaf_{i}",
            r,
            mats,
            assets=assets,
            knuckle_edge_x=r.leaf_w,  # free-edge meeting line
            with_handle=(i == handle_idx),
        )
    for i in range(n):
        sign = 1.0 if i % 2 == 0 else -1.0
        if i == 0:
            model.articulation(
                "frame_to_leaf_0",
                ArticulationType.REVOLUTE,
                parent="frame",
                child="leaf_0",
                origin=Origin(xyz=(hinge_x[0], 0.0, r.z_anchor)),
                axis=(0.0, 0.0, sign),
                motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=0.0, upper=q_max),
            )
        else:
            model.articulation(
                f"leaf_{i - 1}_to_leaf_{i}",
                ArticulationType.REVOLUTE,
                parent=f"leaf_{i - 1}",
                child=f"leaf_{i}",
                origin=Origin(xyz=(r.leaf_w, 0.0, 0.0)),
                axis=(0.0, 0.0, sign),
                motion_limits=MotionLimits(
                    effort=40.0,
                    velocity=1.5,
                    lower=0.0,
                    upper=_FOLD_MIMIC_MULTIPLIER * q_max,
                ),
                mimic=Mimic(joint="frame_to_leaf_0", multiplier=_FOLD_MIMIC_MULTIPLIER),
            )
    return {
        "handle_idx": handle_idx,
        "joint_names": _single_joint_names(n),
        "driver_joints": ["frame_to_leaf_0"],
    }


def _build_biparting_chain(model, r: ResolvedFoldingDoorConfig, frame, mats, *, assets) -> dict:
    """Two symmetric half-chains: left half hinges the left jamb (leaf_0..),
    right half hinges the right jamb (leaf_{N-1}..) with rpy=(0,0,pi) so its
    body reaches back toward center; the two halves bipart at the middle.
    N is even; each half has N/2 leaves.

    Drive-coupled per half: the two jamb hinges are the drivers (limit
    ``_fold_limit``); every interior hinge mimics its half's driver at 2x on
    the alternating axes (see ``_fold_limit`` docstring)."""
    n = r.leaf_count
    half = n // 2
    hinge_x = r.hinge_x
    q_max = _fold_limit(r)
    # Center-meeting leaves: leaf_{half-1} (left) and leaf_half (right).
    for i in range(n):
        _build_leaf(
            model,
            f"leaf_{i}",
            r,
            mats,
            assets=assets,
            knuckle_edge_x=r.leaf_w,
            with_handle=(i == half - 1),  # left center-meeting leaf carries the handle
        )

    joint_names: list[str] = []
    follower_limits = MotionLimits(
        effort=40.0, velocity=1.5, lower=0.0, upper=_FOLD_MIMIC_MULTIPLIER * q_max
    )
    # LEFT half: frame -> leaf_0 (left jamb) -> leaf_1 -> ... -> leaf_{half-1}.
    for i in range(half):
        sign = 1.0 if i % 2 == 0 else -1.0
        if i == 0:
            model.articulation(
                "left_jamb_to_leaf_0",
                ArticulationType.REVOLUTE,
                parent="frame",
                child="leaf_0",
                origin=Origin(xyz=(hinge_x[0], 0.0, r.z_anchor)),
                axis=(0.0, 0.0, sign),
                motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=0.0, upper=q_max),
            )
            joint_names.append("left_jamb_to_leaf_0")
        else:
            jn = f"leaf_{i - 1}_to_leaf_{i}"
            model.articulation(
                jn,
                ArticulationType.REVOLUTE,
                parent=f"leaf_{i - 1}",
                child=f"leaf_{i}",
                origin=Origin(xyz=(r.leaf_w, 0.0, 0.0)),
                axis=(0.0, 0.0, sign),
                motion_limits=follower_limits,
                mimic=Mimic(joint="left_jamb_to_leaf_0", multiplier=_FOLD_MIMIC_MULTIPLIER),
            )
            joint_names.append(jn)
    # RIGHT half: frame -> leaf_{N-1} (right jamb, rpy=pi) -> leaf_{N-2} -> ...
    right_driver = f"right_jamb_to_leaf_{n - 1}"
    for k in range(half):
        i = n - 1 - k  # leaf index, descending from the right jamb inward
        sign = 1.0 if k % 2 == 0 else -1.0
        if k == 0:
            model.articulation(
                right_driver,
                ArticulationType.REVOLUTE,
                parent="frame",
                child=f"leaf_{i}",
                origin=Origin(xyz=(hinge_x[n], 0.0, r.z_anchor), rpy=(0.0, 0.0, math.pi)),
                axis=(0.0, 0.0, sign),
                motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=0.0, upper=q_max),
            )
            joint_names.append(right_driver)
        else:
            parent_i = n - k  # the previous (more-outboard) leaf
            jn = f"leaf_{parent_i}_to_leaf_{i}"
            model.articulation(
                jn,
                ArticulationType.REVOLUTE,
                parent=f"leaf_{parent_i}",
                child=f"leaf_{i}",
                origin=Origin(xyz=(r.leaf_w, 0.0, 0.0)),
                axis=(0.0, 0.0, sign),
                motion_limits=follower_limits,
                mimic=Mimic(joint=right_driver, multiplier=_FOLD_MIMIC_MULTIPLIER),
            )
            joint_names.append(jn)
    return {
        "handle_idx": half - 1,
        "joint_names": joint_names,
        "half": half,
        "driver_joints": ["left_jamb_to_leaf_0", right_driver],
    }


def _single_joint_names(n: int) -> list[str]:
    names = ["frame_to_leaf_0"]
    names += [f"leaf_{i - 1}_to_leaf_{i}" for i in range(1, n)]
    return names


def _nearest_free_edge_to_center(r: ResolvedFoldingDoorConfig, hinge_x: list[float]) -> int:
    """Index of the leaf whose free edge (hinge_x[i+1]) is nearest world X=0."""
    best_i, best_d = 0, float("inf")
    for i in range(r.leaf_count):
        d = abs(hinge_x[i + 1])
        if d < best_d:
            best_d, best_i = d, i
    return best_i


_KINEMATICS_BUILDERS = {
    "single_direction_stack": _build_single_chain,
    "center_biparting_bifold": _build_biparting_chain,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_folding_door(
    config: FoldingDoorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"folding_door_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    # Apply the per-seed glass tint alpha to glass fills (cosmetic only).
    if r.leaf_infill not in WOOD_INFILLS:
        base = PALETTES[r.palette_style]["fill"]
        mats["fill"] = model.material(
            f"folding_door_fill_tint_{r.palette_style}_{r.glass_tint_alpha:.3f}",
            rgba=(base[0], base[1], base[2], r.glass_tint_alpha),
        )

    frame = _build_frame(model, r, mats, assets=assets)
    layout = _KINEMATICS_BUILDERS[r.folding_kinematics](model, r, frame, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["handle_idx"] = layout["handle_idx"]
    model.meta["joint_names"] = layout["joint_names"]
    model.meta["driver_joints"] = layout["driver_joints"]
    return model


def build_seeded_folding_door(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_folding_door(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_folding_door_tests(
    object_model: ArticulatedObject,
    config: FoldingDoorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    n = r.leaf_count
    leaf_names = [f"leaf_{i}" for i in range(n)]
    joint_names = list(object_model.meta.get("joint_names", []))

    # ---- Intentional overlaps (element-scoped, replicated for all N). ----
    for lf in leaf_names:
        # Glass / wood fill is rebated under the steel frame lip.
        if r.leaf_infill == "framed_glass_midrail" or r.leaf_infill == "frameless_full_glass":
            ctx.allow_overlap(
                lf,
                lf,
                elem_a=f"{lf}_glass",
                elem_b=f"{lf}_frame",
                reason="Glass pane is rebated under the steel frame lip (captured, not floating).",
            )
        elif r.leaf_infill == "solid_panel":
            ctx.allow_overlap(
                lf,
                lf,
                elem_a=f"{lf}_wood_panel",
                elem_b=f"{lf}_frame",
                reason="Wood panel is rebated under the steel frame lip (captured, not floating).",
            )
        # Per-leaf hinge knuckles / pivot pins / rollers seat into the leaf frame
        # and into neighbours; declare a broad per-leaf-vs-frame allowance for the
        # track hardware that embeds into the leaf perimeter.

    # Adjacent leaves share the hinge line; knuckles + frame edges meet there.
    if r.folding_kinematics == "single_direction_stack":
        for i in range(n - 1):
            ctx.allow_overlap(
                leaf_names[i],
                leaf_names[i + 1],
                reason=f"leaf_{i} and leaf_{i + 1} share a hinge line; knuckles/edges meet at the fold edge.",
            )
        ctx.allow_overlap("frame", "leaf_0", reason="leaf_0 hinges at the left jamb.")
        ctx.allow_overlap(
            "frame", f"leaf_{n - 1}", reason="last leaf free-edge knuckles meet the right jamb."
        )
    else:  # center_biparting_bifold
        half = n // 2
        # Left half adjacency.
        for i in range(half - 1):
            ctx.allow_overlap(
                leaf_names[i],
                leaf_names[i + 1],
                reason=f"left-half leaf_{i}/leaf_{i + 1} share a hinge line.",
            )
        # Right half adjacency (descending indices).
        for k in range(half - 1):
            i = n - 1 - k
            ctx.allow_overlap(
                leaf_names[i],
                leaf_names[i - 1],
                reason=f"right-half leaf_{i}/leaf_{i - 1} share a hinge line.",
            )
        ctx.allow_overlap("frame", "leaf_0", reason="left-half first leaf hinges the left jamb.")
        ctx.allow_overlap(
            "frame", f"leaf_{n - 1}", reason="right-half first leaf hinges the right jamb."
        )
        # The two halves meet at the center parting line when closed.
        ctx.allow_overlap(
            leaf_names[half - 1],
            leaf_names[half],
            reason="the two bi-fold halves meet at the center parting line when closed.",
        )

    # Track hardware (pivot pins / rollers) embed into the leaf frame and ride in
    # the root channel/rail; and the closed leaves sit against the jamb/header.
    if r.top_track == "perimeter_cased_U_channel":
        for lf in leaf_names:
            for pin in (f"{lf}_pivot_top", f"{lf}_pivot_bot"):
                ctx.allow_overlap(
                    lf,
                    lf,
                    elem_a=pin,
                    elem_b=f"{lf}_frame",
                    reason="Pivot guide pin is seated into the leaf frame edge.",
                )
            ctx.allow_overlap(
                "frame",
                lf,
                reason="Leaf top/bottom edges + pivot pins ride inside the header/threshold U-channels.",
            )
    elif r.top_track == "bottom_track_floor_guided":
        for lf in leaf_names:
            ctx.allow_overlap(
                lf,
                lf,
                elem_a=f"{lf}_roller_stem",
                elem_b=f"{lf}_frame",
                reason="Roller stem is seated into the leaf bottom rail.",
            )
            ctx.allow_overlap(
                "frame",
                lf,
                reason="Leaf-bottom roller rides on the floor track guide rails.",
            )

    # Handle standoffs penetrate the carrying leaf's frame.
    handle_idx = int(object_model.meta.get("handle_idx", 0))
    hlf = f"leaf_{handle_idx}"
    for sfx in ("top", "bot"):
        ctx.allow_overlap(
            hlf,
            hlf,
            elem_a=f"{hlf}_handle_standoff_{sfx}",
            elem_b=f"{hlf}_frame",
            reason="Handle standoff is seated into the leaf frame to mount the pull bar.",
        )

    # ---- Baseline connectivity / overlap / mating checks. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("frame root present", "frame" in part_names, details=str(sorted(part_names))[:200])
    ctx.check(
        "N leaf parts present",
        all(name in part_names for name in leaf_names) and len(leaf_names) == n,
        details=f"expected N={n} leaves",
    )
    ctx.check(
        "N revolute hinge joints",
        len(joint_names) == n,
        details=f"joints={len(joint_names)} expected N={n}",
    )
    joints = [object_model.get_articulation(jn) for jn in joint_names]
    ctx.check(
        "all hinge joints are REVOLUTE about Z",
        all(
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99
            for j in joints
        ),
        details=str([(j.name, tuple(j.axis)) for j in joints[:4]]),
    )

    # ---- Drive coupling: one driver per chain, followers mimic it at 2:1. ----
    driver_names = [str(x) for x in object_model.meta.get("driver_joints", [])]
    expected_drivers = 1 if r.folding_kinematics == "single_direction_stack" else 2
    ctx.check(
        "one driver joint per chain",
        len(driver_names) == expected_drivers and all(dn in joint_names for dn in driver_names),
        details=f"drivers={driver_names}",
    )
    drivers = [j for j in joints if j.name in driver_names]
    followers = [j for j in joints if j.name not in driver_names]
    ctx.check(
        "drivers are free joints (no mimic)",
        all(getattr(j, "mimic", None) is None for j in drivers),
        details=str([j.name for j in drivers]),
    )
    ctx.check(
        "interior hinges mimic their chain driver at 2:1 (track concertina)",
        all(
            getattr(j, "mimic", None) is not None
            and j.mimic.joint in driver_names
            and abs(j.mimic.multiplier - _FOLD_MIMIC_MULTIPLIER) < 1e-9
            and abs(j.mimic.offset) < 1e-9
            for j in followers
        ),
        details=str(
            [(j.name, getattr(getattr(j, "mimic", None), "joint", None)) for j in followers[:4]]
        ),
    )
    # Single-source fold limit: the driver upper limit must match _fold_limit,
    # the analytic no-self-intersection bound for the coupled trajectory.
    q_max = _fold_limit(r)
    ctx.check(
        "driver fold limit derives from the stack-clearance geometry",
        all(
            j.motion_limits is not None
            and abs(float(j.motion_limits.lower)) < 1e-9
            and abs(float(j.motion_limits.upper) - q_max) < 1e-9
            for j in drivers
        ),
        details=f"q_max={q_max:.4f}",
    )
    ctx.check(
        "fold limit keeps alternate leaves clear over the whole drive range",
        0.15 < q_max <= 1.50 + 1e-9,
        details=f"q_max={q_max:.4f} leaf_w={r.leaf_w:.4f}",
    )

    # Closed pose: all leaves coplanar at Y≈0 and ordered L->R filling the span.
    # Pose the DRIVERS only; mimic followers are derived by the SDK.
    zero_pose = {j: 0.0 for j in drivers}
    with ctx.pose(zero_pose):
        aabbs = [ctx.part_world_aabb(object_model.get_part(lf)) for lf in leaf_names]
        y_centers = [(lo[1] + hi[1]) / 2.0 for lo, hi in aabbs]
        x_centers = [(lo[0] + hi[0]) / 2.0 for lo, hi in aabbs]
        # +Y-side extent only: the pull handle protrudes on -Y and its world-Y
        # reach shrinks as its leaf tilts, which would mask the fold signal on
        # narrow-leaf chains. Leaves concertina into +Y (leaf tips at +w*sin q).
        closed_y_max = max(hi[1] for _, hi in aabbs)
        closed_x_span = max(hi[0] for _, hi in aabbs) - min(lo[0] for lo, _ in aabbs)
        ctx.check(
            "leaves coplanar at closed pose",
            max(y_centers) - min(y_centers) < 0.06,
            details=f"Y spread={max(y_centers) - min(y_centers):.4f}",
        )
        # In closed pose, leaves should span left-to-right filling the opening.
        ordered_xs = sorted(x_centers)
        span = ordered_xs[-1] - ordered_xs[0]
        ctx.check(
            "leaves fill the opening left-to-right",
            span > 0.5 * r.opening_width - 0.10 if n >= 2 else True,
            details=f"closed X span={span:.3f} opening={r.opening_width:.3f}",
        )

    # Header is the topmost element and spans wider than a single leaf.
    frame = object_model.get_part("frame")
    frame_aabb = ctx.part_world_aabb(frame)
    leaf0_aabb = ctx.part_world_aabb(object_model.get_part("leaf_0"))
    if frame_aabb is not None and leaf0_aabb is not None:
        ctx.check(
            "header is topmost element",
            frame_aabb[1][2] >= leaf0_aabb[1][2] - 1e-3,
            details=f"frame_top={frame_aabb[1][2]:.3f} leaf_top={leaf0_aabb[1][2]:.3f}",
        )
        ctx.check(
            "frame rests near the ground",
            frame_aabb[0][2] < 0.03,
            details=f"frame_z_min={frame_aabb[0][2]:.4f}",
        )

    # Hero: driving the chain(s) to the fold limit concertinas the leaves out
    # of the closed plane (Y extent grows ~ leaf_w*sin(q)) and, for the single
    # chain, retracts the door along X toward the stacking jamb.
    fold_pose = {j: q_max for j in drivers}
    with ctx.pose(fold_pose):
        folded = [ctx.part_world_aabb(object_model.get_part(lf)) for lf in leaf_names]
        folded_y_max = max(hi[1] for _, hi in folded)
        folded_x_span = max(hi[0] for _, hi in folded) - min(lo[0] for lo, _ in folded)
        y_gain = folded_y_max - closed_y_max
        ctx.check(
            "folding concertinas leaves out of the closed plane",
            y_gain > 0.5 * r.leaf_w * math.sin(q_max),
            details=(
                f"folded +Y reach={folded_y_max:.4f} closed={closed_y_max:.4f} "
                f"gain={y_gain:.4f} q_max={q_max:.3f}"
            ),
        )
        if r.folding_kinematics == "single_direction_stack":
            ctx.check(
                "folding retracts the chain toward the stacking jamb",
                folded_x_span < closed_x_span * math.cos(q_max) + r.leaf_w + 0.25,
                details=f"folded X span={folded_x_span:.3f} closed={closed_x_span:.3f}",
            )

    # Equal leaf widths (regular placement) — sampled from a couple of leaves.
    leaf_widths = [(a[1][0] - a[0][0]) for a in aabbs]
    if leaf_widths:
        ctx.check(
            "leaves have ~equal width",
            max(leaf_widths) - min(leaf_widths) < 0.02,
            details=f"width spread={max(leaf_widths) - min(leaf_widths):.4f}",
        )

    # LEAF_W >= 4*FRAME_T (the inequality enforced in resolve_config).
    ctx.check(
        "leaf holds two stiles + opening (LEAF_W >= 4*FRAME_T)",
        r.leaf_w >= 4.0 * r.frame_t - 1e-6,
        details=f"leaf_w={r.leaf_w:.4f} 4*frame_t={4.0 * r.frame_t:.4f}",
    )

    # biparting requires even N.
    if r.folding_kinematics == "center_biparting_bifold":
        ctx.check(
            "center-biparting has even N",
            n % 2 == 0,
            details=f"N={n}",
        )

    # slot_choices recorded with leaf_count encoded.
    ctx.check(
        "slot_choices recorded with leaf_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "FoldingDoorConfig",
    "ResolvedFoldingDoorConfig",
    "build_folding_door",
    "build_seeded_folding_door",
    "config_from_seed",
    "resolve_config",
    "run_folding_door_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
