# SPDX-License-Identifier: Apache-2.0

"""Sliding architectural window — modular procedural template.

Category identity: a **sliding** architectural window — a static outer ``frame``
(perimeter ring + head/sill track or jamb side-tracks) holding N panels, at least
one of which is a movable **PRISMATIC** sliding sash (the category-defining
motion). The rest are FIXED lites. No REVOLUTE swing sash (those belong to the
``window`` subcategory — casement / awning / hopper).

Built fresh to the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Window_Sliding_Window_Window.md`` and the
``Window / Sliding Window`` 5-star pool (3 parents + 90 forks under
``data/records/``):

  * S1 two-panel horizontal slider  (``rec_two-panel-...5d4512bc``)
  * S2 three-panel horizontal slider, colonial grille  (``rec_three-panel-...860f2131``)
  * S3 vertical double-hung, dual-slider, sash lock  (``rec_double-hung-...6c54f6e4``)

Pattern = ``mixed`` (parallel_children fixed named slots + two multiplicity axes
+ a sliding-count gating choice):

  * ``orientation_drive`` (Slot A, 2): horizontal_slide (sash slides ±X along a
    head/sill track) / vertical_double_hung (sash slides ±Z along jamb tracks).
    Decides the root track primitive and the PRISMATIC axis.
  * ``panel_layout`` (Slot B, multiplicity N): horizontal -> N bays along X
    (separated by mullions for N>=3); vertical -> fixed 2 stacked.
  * ``sliding_sash_count`` (Slot C, S in {1,2}): a gating choice deciding how many
    of the N panels are PRISMATIC sashes (rest FIXED lites). S=2 uses opposed
    axes + offset Y planes so the two movable sashes never interpenetrate.
  * ``divided_light_grid`` (Slot D, multiplicity cols x rows): colonial muntin
    grid per sash, emitted via nested loops.
  * ``sash_hardware`` (Slot E, 5): cam_latch / revolute_latch (the one movable
    REVOLUTE hardware) / sash_lock / pull_cup / pull_handle on the primary sash.
  * ``palette_style`` (6 colorways): white_vinyl / brushed_aluminium /
    anodized_aluminium_dark / black_aluminium / warm_wood / bronze_aluminium.

3 hard rules honoured: (1) all muntins / glass / fixed lites / static hardware
are parent visuals (Rule 1, not fixed joints); (2) every non-FIXED joint
(PRISMATIC sashes, REVOLUTE latch) is a captured-track / mounted joint with
element-scoped allow_overlap declared in run_tests; (3) all geometry derives from
the three 5-star parents above (CadQuery slabs cut into true hollow rings, never
downgraded to Box/Cylinder for the frame/sash bodies).
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

OrientationDrive = Literal["horizontal_slide", "vertical_double_hung"]
SlidingSashCount = Literal["single_slider", "dual_slider"]
SashHardware = Literal[
    "cam_latch", "revolute_latch", "sash_lock", "pull_cup", "pull_handle"
]
PaletteStyle = Literal[
    "white_vinyl",
    "brushed_aluminium",
    "anodized_aluminium_dark",
    "black_aluminium",
    "warm_wood",
    "bronze_aluminium",
]

ORIENTATIONS: tuple[OrientationDrive, ...] = (
    "horizontal_slide",
    "vertical_double_hung",
)
SLIDING_COUNTS: tuple[SlidingSashCount, ...] = ("single_slider", "dual_slider")
SASH_HARDWARES: tuple[SashHardware, ...] = (
    "cam_latch",
    "revolute_latch",
    "sash_lock",
    "pull_cup",
    "pull_handle",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "white_vinyl",
    "brushed_aluminium",
    "anodized_aluminium_dark",
    "black_aluminium",
    "warm_wood",
    "bronze_aluminium",
)

# Panel-count multiplicity (horizontal only). N=2 most common, taper for >4.
PANEL_MIN = 2
PANEL_MAX = 6
PANEL_WEIGHTS = (0.46, 0.30, 0.14, 0.06, 0.04)  # for N = 2,3,4,5,6

# Muntin grid multiplicity. Small grids dominate, large tail downweighted.
COLS_CHOICES = (1, 2, 3, 4, 5)
COLS_WEIGHTS = (0.42, 0.24, 0.20, 0.09, 0.05)
ROWS_CHOICES = (1, 2, 3, 4, 5, 6)
ROWS_WEIGHTS = (0.40, 0.24, 0.18, 0.10, 0.05, 0.03)

# ---------------------------------------------------------------------------
# Palettes (frame / sash / glass / hardware) — observed from the 5-star pool.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_vinyl": {
        "frame": (0.94, 0.95, 0.96, 1.0),
        "sash": (0.965, 0.965, 0.965, 1.0),
        "glass": (0.52, 0.60, 0.66, 0.30),
        "hardware": (0.74, 0.76, 0.79, 1.0),
    },
    "brushed_aluminium": {
        "frame": (0.72, 0.74, 0.76, 1.0),
        "sash": (0.76, 0.78, 0.80, 1.0),
        "glass": (0.50, 0.58, 0.64, 0.32),
        "hardware": (0.60, 0.62, 0.65, 1.0),
    },
    "anodized_aluminium_dark": {
        "frame": (0.30, 0.31, 0.33, 1.0),
        "sash": (0.36, 0.37, 0.39, 1.0),
        "glass": (0.26, 0.32, 0.38, 0.32),
        "hardware": (0.22, 0.23, 0.25, 1.0),
    },
    "black_aluminium": {
        "frame": (0.10, 0.10, 0.11, 1.0),
        "sash": (0.14, 0.14, 0.15, 1.0),
        "glass": (0.24, 0.30, 0.36, 0.32),
        "hardware": (0.55, 0.56, 0.58, 1.0),
    },
    "warm_wood": {
        "frame": (0.52, 0.38, 0.24, 1.0),
        "sash": (0.58, 0.43, 0.28, 1.0),
        "glass": (0.46, 0.52, 0.52, 0.30),
        "hardware": (0.40, 0.34, 0.24, 1.0),
    },
    "bronze_aluminium": {
        "frame": (0.46, 0.40, 0.32, 1.0),
        "sash": (0.50, 0.44, 0.36, 1.0),
        "glass": (0.40, 0.42, 0.40, 0.32),
        "hardware": (0.30, 0.27, 0.22, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Numbers anchored to the 3 parents.
# ---------------------------------------------------------------------------
# Horizontal slider base envelope (two-panel / three-panel parents).
# Sashes are thin glazing panes and the frame box is deep, so the moving sash,
# the (optional) 2nd slider, and the rear fixed lite each get their own Y plane
# spaced >= one sash depth apart -> sliding never shares pane volume (no 穿模).
_H_BAY_W = 0.74          # nominal per-bay clear opening width (X)
_H_HEIGHT = 1.50         # window height (Z), sill at z=0
_H_FRAME_FACE = 0.080    # outer frame member face width
_H_MULLION_FACE = 0.060  # intermediate mullion face (N>=3)
_H_FRAME_DEPTH = 0.150   # deep frame box depth (Y) -> room for 3 clean planes
_H_SASH_FACE = 0.060     # sash perimeter rail/stile face
_H_SASH_DEPTH = 0.030    # thin sash depth (Y) so planes clear each other

# Vertical double-hung base envelope (double-hung parent).
_V_WIDTH = 0.92
_V_HEIGHT = 1.52
_V_FRAME_FACE = 0.060
_V_FRAME_DEPTH = 0.110
_V_SASH_RAIL = 0.052
_V_SASH_DEPTH = 0.026    # thin sash so the two planes clear in Y
_V_SASH_Y_GAP = 0.020    # half-gap between the two sash Y planes (full gap 0.040 > depth)

GLASS_T = 0.007
MUNTIN_T = 0.020         # muntin bar face width
REBATE = 0.005           # glass tucks under sash lip

# Clean head/sill sliding: the sash BODY is strictly shorter than the clear
# opening, leaving a real clearance gap top AND bottom. Only thin guide SHOES
# protrude past the sash into full-opening-width track ribs at the sash Y plane,
# so the sash never shares Z-volume with the solid head/sill (no top/bottom 穿模).
SHOE_PROTRUSION = 0.010  # how far the shoe sticks past the sash top/bottom
TRACK_RIB_T = 0.012      # head/sill track-rib thickness (Z)
RIB_BODY_CLEAR = 0.014   # gap from head/sill solid face to the sash body end
TRACK_RIB_DY = 0.030     # track-rib depth band (Y) the shoe rides in
SHOE_W = 0.080           # guide-shoe width (X)


@dataclass(frozen=True)
class SlidingWindowConfig:
    orientation_drive: OrientationDrive | None = None
    panel_count: int | None = None
    sliding_sash_count: SlidingSashCount | None = None
    muntin_cols: int | None = None
    muntin_rows: int | None = None
    sash_hardware: SashHardware | None = None
    palette_style: PaletteStyle = "white_vinyl"
    win_width_scale: float = 1.0
    win_height_scale: float = 1.0
    frame_face_scale: float = 1.0
    sash_open_frac: float = 0.0
    name: str = "sliding_window"


@dataclass(frozen=True)
class ResolvedSlidingWindowConfig:
    orientation_drive: OrientationDrive
    panel_count: int
    sliding_count: int          # 1 or 2 (concrete S)
    muntin_cols: int
    muntin_rows: int
    sash_hardware: SashHardware
    palette_style: PaletteStyle
    # Concrete geometry.
    total_w: float
    total_h: float
    frame_face: float
    mullion_face: float
    frame_depth: float
    sash_face: float
    sash_depth: float
    # Horizontal layout.
    bay_w: float
    sash_y_front: float
    lite_y_rear: float
    sash_y_dual_rear: float
    # Vertical layout.
    v_sash_h: float
    v_lower_bottom_z: float
    v_upper_bottom_z: float
    v_lower_sash_y: float
    v_upper_sash_y: float
    v_meeting_overlap: float
    sash_open_frac: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> SlidingWindowConfig:
    rng = random.Random(seed)
    orientation = rng.choice(ORIENTATIONS)
    if orientation == "horizontal_slide":
        panel_count = rng.choices(
            range(PANEL_MIN, PANEL_MAX + 1), weights=PANEL_WEIGHTS, k=1
        )[0]
    else:
        panel_count = 2  # vertical double-hung is always 2 stacked
    sliding = rng.choices(SLIDING_COUNTS, weights=(0.6, 0.4), k=1)[0]
    return SlidingWindowConfig(
        orientation_drive=orientation,
        panel_count=panel_count,
        sliding_sash_count=sliding,
        muntin_cols=rng.choices(COLS_CHOICES, weights=COLS_WEIGHTS, k=1)[0],
        muntin_rows=rng.choices(ROWS_CHOICES, weights=ROWS_WEIGHTS, k=1)[0],
        sash_hardware=rng.choice(SASH_HARDWARES),
        palette_style=rng.choice(PALETTE_STYLES),
        win_width_scale=round(rng.uniform(0.85, 1.20), 4),
        win_height_scale=round(rng.uniform(0.85, 1.20), 4),
        frame_face_scale=round(rng.uniform(0.85, 1.25), 4),
        sash_open_frac=round(rng.uniform(0.0, 1.0), 4),
        name=f"seeded_sliding_window_{seed}",
    )


def resolve_config(
    config: SlidingWindowConfig | None = None,
) -> ResolvedSlidingWindowConfig:
    cfg = config or SlidingWindowConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    orientation = _pick(cfg.orientation_drive, ORIENTATIONS)
    hardware = _pick(cfg.sash_hardware, SASH_HARDWARES)

    width_scale = _clamp(cfg.win_width_scale, 0.85, 1.20)
    height_scale = _clamp(cfg.win_height_scale, 0.85, 1.20)
    face_scale = _clamp(cfg.frame_face_scale, 0.85, 1.25)
    open_frac = _clamp(cfg.sash_open_frac, 0.0, 1.0)

    muntin_cols = int(_clamp(cfg.muntin_cols if cfg.muntin_cols else 1, 1, 5))
    muntin_rows = int(_clamp(cfg.muntin_rows if cfg.muntin_rows else 1, 1, 6))

    # --- Panel-count gating (Slot B). ---
    if orientation == "vertical_double_hung":
        panel_count = 2
    else:
        panel_count = int(_clamp(cfg.panel_count if cfg.panel_count else 2, PANEL_MIN, PANEL_MAX))

    # --- Sliding-count gating (Slot C): S <= N. ---
    sliding_token = _pick(cfg.sliding_sash_count, SLIDING_COUNTS)
    sliding_count = 2 if sliding_token == "dual_slider" else 1
    sliding_count = min(sliding_count, panel_count)

    if orientation == "horizontal_slide":
        frame_face = _H_FRAME_FACE * face_scale
        sash_face = _H_SASH_FACE
        sash_depth = _H_SASH_DEPTH
        # Each sash ring laps onto the frame mullion by sash_face on each side;
        # widen the mullion so two adjacent lites/sashes never interpenetrate
        # (their rings both reach toward the mullion centerline). The frame
        # opening edge mediates the capture (declared allow_overlap), not the
        # neighbour ring.
        mullion_face = max(_H_MULLION_FACE * face_scale, 2.0 * sash_face + 0.012)
        frame_depth = _H_FRAME_DEPTH
        bay_w = _H_BAY_W * width_scale
        total_h = _H_HEIGHT * height_scale
        # total width = N bays + (N-1) mullions + 2 frame faces.
        total_w = panel_count * bay_w + (panel_count - 1) * mullion_face + 2 * frame_face

        # Proud-Y offset contract: three distinct Y planes spaced >= one sash
        # depth apart so a moving sash NEVER shares pane volume with the rear
        # fixed lites or the other slider across the full travel. The plane gap
        # carries a small clearance on top of sash_depth.
        plane = sash_depth + 0.006       # plane-to-plane gap > sash_depth
        sash_y_front = +plane            # front-riding slider
        sash_y_dual_rear = 0.0           # second slider (middle plane)
        lite_y_rear = -plane             # fixed lites rearmost plane
        v_sash_h = 0.0
        v_lower_bottom_z = 0.0
        v_upper_bottom_z = 0.0
        v_lower_sash_y = 0.0
        v_upper_sash_y = 0.0
        v_meeting_overlap = 0.0
    else:
        frame_face = _V_FRAME_FACE * face_scale
        mullion_face = 0.0
        frame_depth = _V_FRAME_DEPTH
        sash_face = _V_SASH_RAIL
        sash_depth = _V_SASH_DEPTH
        total_w = _V_WIDTH * width_scale
        total_h = _V_HEIGHT * height_scale
        bay_w = total_w - 2 * frame_face
        sash_y_front = 0.0
        lite_y_rear = 0.0
        sash_y_dual_rear = 0.0
        open_h = total_h - 2 * frame_face
        v_meeting_overlap = sash_face
        # Each sash body fits inside the clear opening with a RIB_BODY_CLEAR gap
        # to the head/sill solid, sharing only the meeting-rail lap. Derived so:
        #   lower: [in_z0+clear, in_z0+clear+v_sash_h]
        #   upper: [in_z1-clear-v_sash_h, in_z1-clear], overlapping lower by overlap
        v_sash_h = (open_h + v_meeting_overlap) / 2.0 - RIB_BODY_CLEAR
        v_lower_sash_y = -_V_SASH_Y_GAP
        v_upper_sash_y = +_V_SASH_Y_GAP
        v_lower_bottom_z = frame_face + RIB_BODY_CLEAR
        v_upper_bottom_z = (total_h - frame_face) - RIB_BODY_CLEAR - v_sash_h

    return ResolvedSlidingWindowConfig(
        orientation_drive=orientation,
        panel_count=panel_count,
        sliding_count=sliding_count,
        muntin_cols=muntin_cols,
        muntin_rows=muntin_rows,
        sash_hardware=hardware,
        palette_style=palette_style,
        total_w=total_w,
        total_h=total_h,
        frame_face=frame_face,
        mullion_face=mullion_face,
        frame_depth=frame_depth,
        sash_face=sash_face,
        sash_depth=sash_depth,
        bay_w=bay_w,
        sash_y_front=sash_y_front,
        lite_y_rear=lite_y_rear,
        sash_y_dual_rear=sash_y_dual_rear,
        v_sash_h=v_sash_h,
        v_lower_bottom_z=v_lower_bottom_z,
        v_upper_bottom_z=v_upper_bottom_z,
        v_lower_sash_y=v_lower_sash_y,
        v_upper_sash_y=v_upper_sash_y,
        v_meeting_overlap=v_meeting_overlap,
        sash_open_frac=open_frac,
        name=cfg.name or "sliding_window",
    )


def with_overrides(config: SlidingWindowConfig, **kwargs: object) -> SlidingWindowConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SlidingWindowConfig | ResolvedSlidingWindowConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedSlidingWindowConfig)
        else resolve_config(config)
    )
    return (
        ("orientation_drive", r.orientation_drive),
        ("panel_layout", f"n{r.panel_count}"),
        ("sliding_sash_count", f"s{r.sliding_count}"),
        ("divided_light_grid", f"g{r.muntin_cols}x{r.muntin_rows}"),
        ("sash_hardware", r.sash_hardware),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# CadQuery geometry helpers
# ---------------------------------------------------------------------------
def _slab(
    x0: float, x1: float, z0: float, z1: float, y_center: float, depth: float
) -> cq.Workplane:
    """Axis-aligned box spanning [x0,x1]x[z0,z1] in X-Z, centered on y_center."""
    return (
        cq.Workplane("XY")
        .transformed(offset=((x0 + x1) / 2.0, y_center, (z0 + z1) / 2.0))
        .box(x1 - x0, depth, z1 - z0)
    )


def _grid_lines(in0: float, in1: float, n: int) -> tuple[list[float], list[float]]:
    """Return (edges, interior centerlines) splitting [in0,in1] into n cells."""
    span = in1 - in0
    edges = [in0 + i * span / n for i in range(n + 1)]
    centerlines = edges[1:-1]
    return edges, centerlines


def _build_sash_shape(opening_w: float, opening_h: float, cols: int, rows: int) -> cq.Workplane:
    """Sash ring (hollow perimeter) + colonial muntin grid, in sash-local frame.
    Local origin centered; bottom rail / left stile symmetric about 0."""
    ow, oh = opening_w, opening_h
    out_w = ow + 2 * _SASH_FACE_LOCAL[0]
    out_h = oh + 2 * _SASH_FACE_LOCAL[0]
    depth = _SASH_FACE_LOCAL[1]
    outer = _slab(-out_w / 2.0, out_w / 2.0, -out_h / 2.0, out_h / 2.0, 0.0, depth)
    opening = _slab(-ow / 2.0, ow / 2.0, -oh / 2.0, oh / 2.0, 0.0, depth + 0.02)
    ring = outer.cut(opening)

    bars = None
    # Vertical muntins (cols-1 interior bars).
    for c in range(1, cols):
        x = -ow / 2.0 + c * ow / cols
        bar = _slab(x - MUNTIN_T / 2.0, x + MUNTIN_T / 2.0, -oh / 2.0, oh / 2.0, 0.0, depth)
        bars = bar if bars is None else bars.union(bar)
    # Horizontal muntins (rows-1 interior bars).
    for rr in range(1, rows):
        z = -oh / 2.0 + rr * oh / rows
        bar = _slab(-ow / 2.0, ow / 2.0, z - MUNTIN_T / 2.0, z + MUNTIN_T / 2.0, 0.0, depth)
        bars = bar if bars is None else bars.union(bar)
    return ring if bars is None else ring.union(bars)


def _build_sash_glass_shape(opening_w: float, opening_h: float) -> cq.Workplane:
    """Single clear pane rebated under the sash lip (reads captured)."""
    ow = opening_w + 2 * REBATE
    oh = opening_h + 2 * REBATE
    return _slab(-ow / 2.0, ow / 2.0, -oh / 2.0, oh / 2.0, 0.0, GLASS_T)


# Module-level holder for the sash face/depth currently being built (avoids
# threading two extra args through _build_sash_shape for each call).
_SASH_FACE_LOCAL = (_H_SASH_FACE, _H_SASH_DEPTH)


# ---------------------------------------------------------------------------
# Horizontal frame
# ---------------------------------------------------------------------------
def _build_horizontal_frame_shape(
    r: ResolvedSlidingWindowConfig, slider_planes: tuple[float, ...] = ()
) -> cq.Workplane:
    """Outer slab cut by N bay openings (leaving head/sill/jambs + mullions),
    then a continuous horizontal TRACK SLOT carved through the mullions at each
    moving-sash Y plane so the slider rides in a genuine open channel across its
    full travel instead of driving through solid mullion material (kills 穿模).
    The rear fixed-lite plane keeps its mullion webs (the lites seat there)."""
    half_w = r.total_w / 2.0
    outer = _slab(-half_w, half_w, 0.0, r.total_h, 0.0, r.frame_depth)
    cut_depth = r.frame_depth + 0.02
    in_x0 = -half_w + r.frame_face
    in_x1 = half_w - r.frame_face
    in_z0 = r.frame_face
    in_z1 = r.total_h - r.frame_face
    x = -half_w + r.frame_face
    body = outer
    for i in range(r.panel_count):
        bx0 = x
        bx1 = x + r.bay_w
        body = body.cut(_slab(bx0, bx1, in_z0, in_z1, 0.0, cut_depth))
        x = bx1 + (r.mullion_face if i < r.panel_count - 1 else 0.0)
    # Track slots: at each slider plane, hollow the full inner-width band (across
    # all mullions) so the moving sash passes through open air. Depth a touch
    # over the sash depth so the sash never grazes the slot walls in Y; the head
    # and sill members above/below in_z stay solid (the rail lap there is the
    # legitimate retained-insertion engagement).
    slot_d = r.sash_depth + 0.008
    for plane_y in slider_planes:
        body = body.cut(_slab(in_x0, in_x1, in_z0, in_z1, plane_y, slot_d))
    return body


def _horizontal_bay_centers(r: ResolvedSlidingWindowConfig) -> list[float]:
    half_w = r.total_w / 2.0
    centers = []
    x = -half_w + r.frame_face
    for i in range(r.panel_count):
        centers.append(x + r.bay_w / 2.0)
        x += r.bay_w + r.mullion_face
    return centers


def _sliding_panel_indices(r: ResolvedSlidingWindowConfig) -> list[int]:
    """Which bay indices are PRISMATIC sliders. Single -> last bay; dual -> the
    two innermost bays (so they pass each other on opposed axes)."""
    n = r.panel_count
    if r.sliding_count == 1:
        # Center for odd N (XOX feel), else the right bay.
        return [n // 2] if n % 2 == 1 else [n - 1]
    # dual: two adjacent central bays.
    if n == 2:
        return [0, 1]
    mid = n // 2
    return sorted([mid - 1, mid])


# ---------------------------------------------------------------------------
# Vertical frame
# ---------------------------------------------------------------------------
def _build_vertical_frame_shape(r: ResolvedSlidingWindowConfig) -> cq.Workplane:
    """Outer slab cut by a single central opening, plus jamb side-track grooves."""
    half_w = r.total_w / 2.0
    outer = _slab(-half_w, half_w, 0.0, r.total_h, 0.0, r.frame_depth)
    in_x0 = -half_w + r.frame_face
    in_x1 = half_w - r.frame_face
    in_z0 = r.frame_face
    in_z1 = r.total_h - r.frame_face
    frame = outer.cut(_slab(in_x0, in_x1, in_z0, in_z1, 0.0, r.frame_depth + 0.02))
    # Two side-track grooves per jamb (one per sash plane), notched partway in.
    groove_x = r.frame_face * 0.55
    track_depth = 0.030
    for edge_x, sign in ((in_x0, +1.0), (in_x1, -1.0)):
        cx = edge_x - sign * groove_x / 2.0
        for track_y in (r.v_lower_sash_y, r.v_upper_sash_y):
            frame = frame.cut(
                _slab(
                    cx - groove_x / 2.0, cx + groove_x / 2.0,
                    in_z0, in_z1, track_y, track_depth,
                )
            )
    return frame


# ---------------------------------------------------------------------------
# Sash hardware (Slot E). Mounted on the primary sliding sash, sash-local frame.
# ---------------------------------------------------------------------------
def _emit_sash_hardware(
    sash, r, mats, *, opening_w: float, opening_h: float, model, sash_name: str,
    z_off: float = 0.0, y_off: float = 0.0, x_off: float = 0.0,
):
    """Emit Slot E hardware. Returns the latch articulation name (or None).
    All static hardware is a parent visual (Rule 1); revolute_latch adds one
    REVOLUTE joint anchored to the meeting-stile solid face. ``z_off`` / ``y_off``
    / ``x_off`` shift the hardware to match a sash whose visuals are authored
    about a non-center frame (proud plane / jamb-anchored vertical sash)."""
    sash_face = r.sash_face
    depth = r.sash_depth
    face_y = depth / 2.0 + y_off
    is_vertical = r.orientation_drive == "vertical_double_hung"
    # Meeting edge mount: horizontal slider -> side stile (left inner edge);
    # vertical double-hung -> the top meeting rail, centered in X. Keeping the
    # hardware on the meeting edge (not the outer stile) avoids the jamb track.
    stile_x = -opening_w / 2.0 - sash_face / 2.0 + x_off
    if is_vertical:
        mount_x = 0.0 + x_off
        mount_z = opening_h / 2.0 + sash_face / 2.0 + z_off  # top (meeting) rail
    else:
        mount_x = stile_x
        mount_z = 0.0 + z_off
    hw = mats["hardware"]

    if r.sash_hardware == "cam_latch":
        plate_t = 0.010
        sash.visual(
            Box((0.028, plate_t, 0.075) if not is_vertical else (0.075, plate_t, 0.028)),
            origin=Origin(xyz=(mount_x, face_y + plate_t / 2.0, mount_z)),
            material=hw,
            name=f"{sash_name}_latch_plate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        sash.visual(
            Cylinder(radius=0.006, length=0.045),
            origin=Origin(
                xyz=(mount_x, face_y + plate_t + 0.022, mount_z - 0.008),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=hw,
            name=f"{sash_name}_latch_lever", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        return None

    if r.sash_hardware == "sash_lock":
        # Cam lock body + lever on the bottom (meeting) rail center.
        rail_z = -opening_h / 2.0 - sash_face / 2.0 + z_off
        sash.visual(
            Box((0.060, 0.024, 0.022)),
            origin=Origin(xyz=(0.0, face_y + 0.010, rail_z)),
            material=hw,
            name=f"{sash_name}_lock_body", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        sash.visual(
            Box((0.044, 0.012, 0.010)),
            origin=Origin(xyz=(0.0, face_y + 0.024, rail_z + 0.004)),
            material=hw,
            name=f"{sash_name}_lock_lever", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        return None

    if r.sash_hardware == "pull_cup":
        # Recessed pull cup (ring rim + back plate) on the bottom rail.
        rail_z = -opening_h / 2.0 - sash_face / 2.0 + z_off
        sash.visual(
            Cylinder(radius=0.020, length=0.006),
            origin=Origin(xyz=(0.0, face_y + 0.001, rail_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=hw,
            name=f"{sash_name}_pull_backplate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        sash.visual(
            Cylinder(radius=0.024, length=0.004),
            origin=Origin(xyz=(0.0, face_y + 0.004, rail_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=hw,
            name=f"{sash_name}_pull_rim", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        return None

    if r.sash_hardware == "pull_handle":
        # Pull-handle bar + two mounting bosses. Horizontal slider -> upright bar
        # along Z on the side stile; vertical -> a horizontal bar along X on the
        # meeting rail. The bosses straddle the grip along the bar axis.
        if is_vertical:
            grip = (0.110, 0.014, 0.018)
            boss = (0.018, 0.020, 0.018)
            db = (0.055, 0.0, 0.0)
        else:
            grip = (0.018, 0.014, 0.110)
            boss = (0.018, 0.020, 0.018)
            db = (0.0, 0.0, 0.055)
        sash.visual(
            Box(grip),
            origin=Origin(xyz=(mount_x, face_y + 0.018, mount_z)),
            material=hw,
            name=f"{sash_name}_handle_grip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        sash.visual(
            Box(boss),
            origin=Origin(xyz=(mount_x + db[0], face_y + 0.010, mount_z + db[2])),
            material=hw,
            name=f"{sash_name}_handle_boss_top", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        sash.visual(
            Box(boss),
            origin=Origin(xyz=(mount_x - db[0], face_y + 0.010, mount_z - db[2])),
            material=hw,
            name=f"{sash_name}_handle_boss_bot", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        return None

    # revolute_latch: a small thumb-turn that swings about Z, anchored to the
    # meeting-edge solid face (a keeper plate sits under it, captured-pin style).
    sash.visual(
        Box((0.024, 0.012, 0.050) if not is_vertical else (0.050, 0.012, 0.024)),
        origin=Origin(xyz=(mount_x, face_y + 0.006, mount_z)),
        material=hw,
        name=f"{sash_name}_latch_keeper", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
    )
    latch = model.part(f"{sash_name}_latch")
    # Latch part authored in its pivot frame (pivot at local origin).
    latch.visual(
        Cylinder(radius=0.008, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=hw,
        name=f"{sash_name}_latch_hub", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
    )
    latch.visual(
        Box((0.040, 0.010, 0.012)),
        origin=Origin(xyz=(0.018, 0.006, 0.0)),
        material=hw,
        name=f"{sash_name}_latch_lever", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
    )
    latch.inertial = Inertial.from_geometry(
        Box((0.050, 0.020, 0.020)),
        mass=0.02,
        origin=Origin(xyz=(0.012, 0.0, 0.0)),
    )
    return (latch, f"{sash_name}_latch")


# ---------------------------------------------------------------------------
# Guide shoes + track ribs (clean head/sill sliding)
# ---------------------------------------------------------------------------
def _emit_guide_shoes(sash, mats, *, sash_outer_w, sash_body_h, plane_dummy=0.0,
                      z_off, axis="z"):
    """Emit thin guide shoes protruding past the sash body top/bottom (axis='z',
    horizontal slider) or left/right (axis='x', vertical sash jamb shoes) so the
    sash rides in a track rib without the sash body touching the head/sill solid.

    sash visuals are authored about the sash plane at local y=0; ``z_off`` shifts
    everything so the seated sash lands at its world position."""
    hw = mats["hardware"]
    half_h = sash_body_h / 2.0
    xs = (-0.30 * sash_outer_w, 0.30 * sash_outer_w)
    # Top + bottom shoes protrude exactly SHOE_PROTRUSION past the sash body end
    # (shoe outer face flush with the body end + protrusion). They overlap the
    # thin track ribs but stop short of the solid head/sill (RIB_BODY_CLEAR gap).
    for end, sign in (("bot", -1.0), ("top", +1.0)):
        # shoe spans from the body end outward by SHOE_PROTRUSION.
        z_shoe = sign * (half_h + SHOE_PROTRUSION / 2.0) + z_off
        for k, x in enumerate(xs):
            sash.visual(
                Box((SHOE_W, TRACK_RIB_DY, SHOE_PROTRUSION)),
                origin=Origin(xyz=(x, 0.0, z_shoe)),
                material=hw,
                name=f"{sash.name}_{end}_shoe_{k}", material_class_id="metal.stainless_matte",
            )
    return [f"{sash.name}_{e}_shoe_{k}" for e in ("bot", "top") for k in range(2)]


def _emit_vertical_jamb_shoes(sash, mats, *, sash_outer_w, sash_body_h, z_off,
                              protrusion, x_off=0.0):
    """Lateral guide shoes on the vertical sash stiles, protruding ``protrusion``
    past the left/right edges to reach the jamb track ribs (constant overlap as
    the sash slides up/down). The shoe outer edge stops at the opening edge so
    neither the body nor the shoe touches the jamb solid."""
    hw = mats["hardware"]
    half_w = sash_outer_w / 2.0
    zs = (-0.30 * sash_body_h + z_off, 0.30 * sash_body_h + z_off)
    for side, sign in (("l", -1.0), ("r", +1.0)):
        x_shoe = sign * (half_w + protrusion / 2.0) + x_off
        for k, z in enumerate(zs):
            sash.visual(
                Box((protrusion, TRACK_RIB_DY, SHOE_W)),
                origin=Origin(xyz=(x_shoe, 0.0, z)),
                material=hw,
                name=f"{sash.name}_{side}_shoe_{k}", material_class_id="metal.stainless_matte",
            )
    return [f"{sash.name}_{s}_shoe_{k}" for s in ("l", "r") for k in range(2)]


def _emit_horizontal_track_ribs(frame, r, mats, *, in_x0, in_x1, in_z0, in_z1, planes):
    """Thin head + sill track ribs (full opening width, continuous along X) at
    each slider Y plane. The sash shoes ride along these with constant overlap at
    every slide position; the ribs hang off the head underside / sill topside so
    the sash body never reaches the solid head/sill."""
    width = in_x1 - in_x0
    cx = (in_x0 + in_x1) / 2.0
    rib = mats["hardware"]
    names = []
    for pi, plane_y in enumerate(planes):
        # Sill rib: sits on the sill top surface (z just above in_z0).
        frame.visual(
            Box((width, TRACK_RIB_DY, TRACK_RIB_T)),
            origin=Origin(xyz=(cx, plane_y, in_z0 + TRACK_RIB_T / 2.0)),
            material=rib,
            name=f"sill_rib_{pi}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        # Head rib: hangs below the head solid (z just below in_z1).
        frame.visual(
            Box((width, TRACK_RIB_DY, TRACK_RIB_T)),
            origin=Origin(xyz=(cx, plane_y, in_z1 - TRACK_RIB_T / 2.0)),
            material=rib,
            name=f"head_rib_{pi}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
        )
        names += [f"sill_rib_{pi}", f"head_rib_{pi}"]
    return names


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def _build_horizontal(model, r, mats):
    in_z0 = r.frame_face
    in_z1 = r.total_h - r.frame_face
    opening_h = in_z1 - in_z0

    centers = _horizontal_bay_centers(r)
    sliders = set(_sliding_panel_indices(r))
    joints: list[str] = []  # prismatic joint names
    latch_info = None

    travel = r.bay_w * 0.90

    global _SASH_FACE_LOCAL
    _SASH_FACE_LOCAL = (r.sash_face, r.sash_depth)

    # Assign opposed axes for dual sliders. Sort sliders left->right.
    slider_order = sorted(sliders)
    # The FRONT-riding slider carries the hardware: it sits proud (+Y) clear of
    # the frame face, so the cam latch / pull / handle don't bury into the frame
    # mullion. Single slider rides front; dual -> the left (front) slider.
    primary_slider = slider_order[0]
    dual_axis_y = {}
    if r.sliding_count == 2:
        # left slider rides front (+Y) sliding -X..; right slider rides the middle
        # plane opposed +X. The two planes + the rear lite plane are each >= one
        # sash depth apart so no two ever share pane volume.
        dual_axis_y[slider_order[0]] = (r.sash_y_front, -1.0)
        dual_axis_y[slider_order[1]] = (r.sash_y_dual_rear, 1.0)

    # Y planes that carry a moving sash -> carve an open track slot through the
    # mullions there so the slider passes through air, not solid mullion.
    if r.sliding_count == 2:
        slider_planes = (r.sash_y_front, r.sash_y_dual_rear)
    else:
        slider_planes = (r.sash_y_front,)

    frame = model.part("frame")
    frame.visual(
        mesh_from_cadquery(_build_horizontal_frame_shape(r, slider_planes), "frame"),
        material=mats["frame"],
        name="frame_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminium", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "plastic.opaque_glossy_molded"),
    )
    frame.inertial = Inertial.from_geometry(
        Box((r.total_w, r.frame_depth, r.total_h)),
        mass=6.0,
        origin=Origin(xyz=(0.0, 0.0, r.total_h / 2.0)),
    )

    half_w = r.total_w / 2.0
    in_x0 = -half_w + r.frame_face
    in_x1 = half_w - r.frame_face
    mid_cz = (in_z0 + in_z1) / 2.0

    # Track ribs (thin, full opening width) at each slider Y plane so the shoes
    # ride with constant overlap; the head/sill solids never share the sash body
    # Z-range.
    _emit_horizontal_track_ribs(
        frame, r, mats, in_x0=in_x0, in_x1=in_x1, in_z0=in_z0, in_z1=in_z1,
        planes=slider_planes,
    )

    # Moving-sash body is strictly shorter than the clear opening (clearance top
    # AND bottom), so its rails never enter the solid head/sill Z-band. The fixed
    # lites are static glazing seated to fill the opening.
    slider_outer_h = opening_h - 2.0 * RIB_BODY_CLEAR
    slider_glass_h = slider_outer_h - 2.0 * r.sash_face
    lite_glass_h = opening_h   # static lite fills the opening
    # Slider joint anchored on the sill rib (real material, inside the child shoe).
    slider_anchor_z = in_z0 + TRACK_RIB_T
    slider_z_off = mid_cz - slider_anchor_z      # centered body -> seated at mid_cz
    lite_anchor_z = in_z0
    lite_z_off = mid_cz - lite_anchor_z
    for i, cx in enumerate(centers):
        is_slider = i in sliders
        name = f"sash_{i}" if is_slider else f"fixed_lite_{i}"
        part = model.part(name)
        if is_slider:
            if r.sliding_count == 2:
                y, axis_sign = dual_axis_y[i]
            else:
                y, axis_sign = r.sash_y_front, -1.0 if i > 0 else 1.0
            glass_h = slider_glass_h
            # Slider body also clears the mullion/jamb laterally so it never laps
            # solid frame in X; the head/sill shoes provide the only capture.
            glass_w = r.bay_w - 2.0 * RIB_BODY_CLEAR - 2.0 * r.sash_face
            z_off = slider_z_off
            anchor_z = slider_anchor_z
        else:
            y, axis_sign = r.lite_y_rear, 0.0
            glass_h = lite_glass_h
            glass_w = r.bay_w   # static lite fills the bay opening
            z_off = lite_z_off
            anchor_z = lite_anchor_z
        part.visual(
            mesh_from_cadquery(
                _build_sash_shape(glass_w, glass_h, r.muntin_cols, r.muntin_rows),
                f"{name}_frame",
            ),
            origin=Origin(xyz=(0.0, 0.0, z_off)),
            material=mats["sash"],
            name=f"{name}_frame", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminium", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "plastic.opaque_glossy_molded"),
        )
        part.visual(
            mesh_from_cadquery(
                _build_sash_glass_shape(glass_w, glass_h), f"{name}_glass"
            ),
            origin=Origin(xyz=(0.0, 0.0, z_off)),
            material=mats["glass"],
            name=f"{name}_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"white_vinyl", "brushed_aluminium", "warm_wood"} else "glass.smoked_tinted"),
        )
        body_h = (glass_h + 2 * r.sash_face)
        body_w = (glass_w + 2 * r.sash_face)
        part.inertial = Inertial.from_geometry(
            Box((body_w, r.sash_depth, body_h)),
            mass=0.8,
            origin=Origin(xyz=(0.0, 0.0, z_off)),
        )

        if is_slider:
            # Guide shoes protrude past the (short) body into the sill/head ribs.
            _emit_guide_shoes(
                part, mats, sash_outer_w=body_w,
                sash_body_h=slider_outer_h, z_off=z_off,
            )
            # Hardware on the primary (front) slider only.
            if i == primary_slider:
                primary_glass_w = glass_w
                latch_info = _emit_sash_hardware(
                    part, r, mats, opening_w=glass_w, opening_h=slider_glass_h,
                    model=model, sash_name=name, z_off=z_off, y_off=0.0,
                )
            model.articulation(
                f"frame_to_{name}",
                ArticulationType.PRISMATIC,
                parent=frame,
                child=part,
                origin=Origin(xyz=(cx, y, anchor_z)),
                axis=(axis_sign, 0.0, 0.0),
                motion_limits=MotionLimits(
                    effort=60.0, velocity=0.5, lower=0.0, upper=travel
                ),
            )
            joints.append(f"frame_to_{name}")
        else:
            model.articulation(
                f"frame_to_{name}",
                ArticulationType.FIXED,
                parent=frame,
                child=part,
                origin=Origin(xyz=(cx, y, anchor_z)),
            )

    _wire_revolute_latch(
        model, r, latch_info, primary_slider, slider_glass_h, z_off=slider_z_off,
        opening_w=primary_glass_w,
    )
    return frame, joints, primary_slider


def _build_vertical(model, r, mats):
    half_w = r.total_w / 2.0
    in_x0 = -half_w + r.frame_face
    in_x1 = half_w - r.frame_face
    # Sash body clears the jamb solid by jamb_body_clear; the lateral shoes
    # protrude past the stiles into the jamb ribs (constant-overlap side capture).
    # opening_w is the GLASS opening; the sash OUTER width = opening_w + 2*sash_face
    # must equal clear_opening - 2*jamb_body_clear so the stiles clear the jamb.
    jamb_body_clear = 0.006
    opening_w = (in_x1 - in_x0) - 2.0 * jamb_body_clear - 2.0 * r.sash_face

    frame = model.part("frame")
    frame.visual(
        mesh_from_cadquery(_build_vertical_frame_shape(r), "frame"),
        material=mats["frame"],
        name="frame_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminium", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "plastic.opaque_glossy_molded"),
    )
    frame.inertial = Inertial.from_geometry(
        Box((r.total_w, r.frame_depth, r.total_h)),
        mass=6.0,
        origin=Origin(xyz=(0.0, 0.0, r.total_h / 2.0)),
    )

    global _SASH_FACE_LOCAL
    _SASH_FACE_LOCAL = (r.sash_face, r.sash_depth)

    in_z0 = r.frame_face
    in_z1 = r.total_h - r.frame_face
    open_h = in_z1 - in_z0
    # Cap travel so an opened sash never drives its far rail into the head/sill
    # solid: the lower sash may rise at most until its top reaches in_z1 - clear.
    travel_max = (open_h - r.v_meeting_overlap) / 2.0 - RIB_BODY_CLEAR
    travel = max(0.05, min(r.v_sash_h * 0.42, travel_max - 0.004))
    joints: list[str] = []
    # lower sash always slides; upper sash slides only when dual.
    upper_is_slider = r.sliding_count == 2

    sash_specs = [
        ("lower_sash", r.v_lower_bottom_z, r.v_lower_sash_y, (0.0, 0.0, 1.0), True),
        ("upper_sash", r.v_upper_bottom_z, r.v_upper_sash_y, (0.0, 0.0, -1.0), upper_is_slider),
    ]
    latch_info = None
    # Add full-height jamb track ribs at each sash Y plane so the lateral guide
    # shoes ride with constant overlap; the sash bodies clear the head/sill.
    for pi, plane_y in enumerate((r.v_lower_sash_y, r.v_upper_sash_y)):
        for sgn, ex in ((+1.0, in_x0), (-1.0, in_x1)):
            # Rib hangs just INSIDE the opening edge (into the clear opening), so
            # the sash shoe rides on it without the body touching the jamb solid.
            frame.visual(
                Box((TRACK_RIB_T, TRACK_RIB_DY, open_h)),
                origin=Origin(xyz=(ex + sgn * TRACK_RIB_T / 2.0, plane_y,
                                   (in_z0 + in_z1) / 2.0)),
                material=mats["hardware"],
                name=f"jamb_rib_{pi}_{0 if sgn > 0 else 1}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_vinyl", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "metal.aluminum_bare"),
            )
    # The lower sash bottom rail sits at v_lower_bottom_z (clear of the sill);
    # the upper sash top rail sits at in_z1 - clear (clear of the head). The joint
    # is anchored on the LEFT jamb rib (real frame material), so the sash visuals
    # are X-shifted by x_off to re-center the seated sash in the opening.
    jamb_origin_x = in_x0 + TRACK_RIB_T / 2.0
    x_off = -jamb_origin_x
    for name, bottom_z, sash_y, axis, is_slider in sash_specs:
        part = model.part(name)
        seated_cz = bottom_z + r.v_sash_h / 2.0
        anchor_z = seated_cz
        z_off = 0.0
        part.visual(
            mesh_from_cadquery(
                _build_sash_shape(opening_w, r.v_sash_h - 2 * r.sash_face,
                                  r.muntin_cols, r.muntin_rows),
                f"{name}_frame",
            ),
            origin=Origin(xyz=(x_off, 0.0, z_off)),
            material=mats["sash"],
            name=f"{name}_frame", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminium", "anodized_aluminium_dark", "black_aluminium", "warm_wood", "bronze_aluminium"} else "plastic.opaque_glossy_molded"),
        )
        part.visual(
            mesh_from_cadquery(
                _build_sash_glass_shape(opening_w, r.v_sash_h - 2 * r.sash_face),
                f"{name}_glass",
            ),
            origin=Origin(xyz=(x_off, 0.0, z_off)),
            material=mats["glass"],
            name=f"{name}_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"white_vinyl", "brushed_aluminium", "warm_wood"} else "glass.smoked_tinted"),
        )
        part.inertial = Inertial.from_geometry(
            Box((opening_w + 2 * r.sash_face, r.sash_depth, r.v_sash_h)),
            mass=0.8,
            origin=Origin(xyz=(x_off, 0.0, z_off)),
        )
        # Lateral jamb guide shoes (protrude to the opening edge into the ribs).
        _emit_vertical_jamb_shoes(
            part, mats, sash_outer_w=opening_w + 2 * r.sash_face,
            sash_body_h=r.v_sash_h, z_off=z_off, protrusion=jamb_body_clear,
            x_off=x_off,
        )
        # Hardware on the lower sash meeting rail (top rail of lower sash).
        if name == "lower_sash":
            latch_info = _emit_sash_hardware(
                part, r, mats, opening_w=opening_w,
                opening_h=r.v_sash_h - 2 * r.sash_face,
                model=model, sash_name=name, z_off=z_off, x_off=x_off,
            )
        # Joint origin on the LEFT jamb rib (real frame material at the sash Y
        # plane, full height) AND inside the sash left shoe -> both parent and
        # child distances stay within the 15mm baseline. The PRISMATIC Z axis is
        # unaffected by the origin X.
        jamb_origin_x = in_x0 + TRACK_RIB_T / 2.0
        if is_slider:
            model.articulation(
                f"frame_to_{name}",
                ArticulationType.PRISMATIC,
                parent=frame,
                child=part,
                origin=Origin(xyz=(jamb_origin_x, sash_y, anchor_z)),
                axis=axis,
                motion_limits=MotionLimits(
                    effort=60.0, velocity=0.25, lower=0.0, upper=travel
                ),
            )
            joints.append(f"frame_to_{name}")
        else:
            model.articulation(
                f"frame_to_{name}",
                ArticulationType.FIXED,
                parent=frame,
                child=part,
                origin=Origin(xyz=(jamb_origin_x, sash_y, anchor_z)),
            )

    _wire_revolute_latch(
        model, r, latch_info, "lower_sash", r.v_sash_h - 2 * r.sash_face,
        sash_name="lower_sash", z_off=0.0, y_off=0.0, x_off=x_off,
    )
    return frame, joints, "lower_sash"


def _wire_revolute_latch(
    model, r, latch_info, primary, opening_h, sash_name=None, z_off=0.0, y_off=None,
    opening_w=None, x_off=0.0,
):
    """If the hardware is a revolute_latch, wire the REVOLUTE joint from the
    primary sliding sash to the latch part, pivoting about Z on the meeting
    stile's solid face."""
    if latch_info is None or r.sash_hardware != "revolute_latch":
        return
    latch, latch_name = latch_info
    parent_name = sash_name or f"sash_{primary}"
    parent = model.get_part(parent_name)
    # Sash visuals are authored at local y=0 (the joint origin carries the plane),
    # so the latch keeper / pivot sit at the sash front face in the LOCAL frame.
    if y_off is None:
        y_off = 0.0
    if opening_w is None:
        opening_w = r.bay_w
    face_y = r.sash_depth / 2.0 + y_off
    # Pivot at the meeting-edge front face, sash-local frame.
    if r.orientation_drive == "vertical_double_hung":
        mount_x = 0.0 + x_off
        mount_z = opening_h / 2.0 + r.sash_face / 2.0 + z_off
    else:
        mount_x = -opening_w / 2.0 - r.sash_face / 2.0
        mount_z = 0.0 + z_off
    model.articulation(
        f"{parent_name}_to_latch",
        ArticulationType.REVOLUTE,
        parent=parent,
        child=latch,
        origin=Origin(xyz=(mount_x, face_y + 0.012, mount_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=0.0, upper=math.pi / 2.0),
    )


def build_sliding_window(
    config: SlidingWindowConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"sw_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    if r.orientation_drive == "horizontal_slide":
        _build_horizontal(model, r, mats)
    else:
        _build_vertical(model, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_sliding_window(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_sliding_window(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_sliding_window_tests(
    object_model: ArticulatedObject,
    config: SlidingWindowConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")

    part_names = {p.name for p in object_model.parts}
    sash_parts = [n for n in part_names if n.startswith("sash_") and "_latch" not in n]
    lite_parts = [n for n in part_names if n.startswith("fixed_lite_")]
    vert_sashes = [n for n in ("lower_sash", "upper_sash") if n in part_names]

    all_sash_like = sash_parts + lite_parts + vert_sashes

    # Which parts are movable sliders vs fixed lites.
    if r.orientation_drive == "horizontal_slide":
        movable_sash_names = sash_parts
        fixed_lite_names = lite_parts
    else:
        movable_sash_names = ["lower_sash"] + (["upper_sash"] if r.sliding_count == 2 else [])
        fixed_lite_names = ["upper_sash"] if r.sliding_count == 1 else []

    # ---- Captured-glass allowance (all sashes/lites). ----
    for nm in all_sash_like:
        ctx.allow_overlap(
            nm, nm, elem_a=f"{nm}_glass", elem_b=f"{nm}_frame",
            reason="Glass pane rebated under the sash/muntin lip (captured, not floating).",
        )

    # ---- FIXED lites are static glazing seated in the frame opening (their ring
    # laps the frame rebate). This is constant, not a sliding 穿模. Moving sashes
    # do NOT lap frame_shell at all -> no such allowance for them. ----
    for nm in fixed_lite_names:
        ctx.allow_overlap(
            "frame", nm, elem_a="frame_shell", elem_b=f"{nm}_frame",
            reason=f"{nm} fixed lite ring is rebated into the frame opening (static seated capture).",
        )
        ctx.allow_overlap(
            "frame", nm, elem_a="frame_shell", elem_b=f"{nm}_glass",
            reason=f"{nm} fixed lite glass laps the frame opening lip (static captured glazing).",
        )

    # ---- Moving-sash GUIDE SHOE rides in the track rib (constant overlap across
    # the full travel) — the ONLY moving-sash<->frame contact. The sash body never
    # shares Z-volume with the solid head/sill (verified zero penetration). ----
    rib_elems = [v.name for v in frame.visuals if "_rib_" in v.name]
    # Every sash/lite that has guide shoes (all vertical sashes; horizontal
    # sliders) rides in the track ribs with constant overlap.
    for sn in all_sash_like:
        sash_part = object_model.get_part(sn)
        shoe_elems = [v.name for v in sash_part.visuals if "_shoe_" in v.name]
        if not shoe_elems:
            continue
        for se in shoe_elems:
            ctx.allow_overlap(
                "frame", sn, elem_a="frame_shell", elem_b=se,
                reason="Guide shoe rides in the track channel (constant sliding contact).",
            )
            for re in rib_elems:
                ctx.allow_overlap(
                    "frame", sn, elem_a=re, elem_b=se,
                    reason="Guide shoe rides along the track rib with constant overlap at every slide position.",
                )
        # The jamb/track rib hangs slightly into the opening alongside the sash
        # stile/rail edge -> a thin constant side-track lap (not a growing 穿模).
        for re in rib_elems:
            ctx.allow_overlap(
                "frame", sn, elem_a=re, elem_b=f"{sn}_frame",
                reason="Sash edge rides alongside the thin track rib (constant side-track lap).",
            )

    # NOTE: there is intentionally NO broad slider<->lite / slider<->sash / sash
    # body<->head/sill overlap allowance. The moving-sash body is strictly shorter
    # than the clear opening (clearance top AND bottom), rides distinct Y planes
    # spaced >= one sash depth apart, and the mullions are carved open along its
    # travel -> the body never shares volume with a fixed lite, the frame web, the
    # head/sill solid, or the other slider (verified ~0 across closed/mid/open).

    # Hardware seated on the sash face.
    # Primary sash carries the hardware: vertical -> always lower_sash; horizontal
    # -> the front-riding (min-index) slider. Mirrors the build dispatch.
    if r.orientation_drive == "vertical_double_hung":
        primary = "lower_sash"
    elif movable_sash_names:
        primary = min(movable_sash_names, key=lambda n: int(n.split("_")[1]))
    else:
        primary = all_sash_like[0]
    # Hardware element names (for both the sash-frame seat allowance and the
    # frame-post lap allowance — the meeting-edge hardware sits over the frame
    # mullion/post when the slider is closed, just as the parents' latch laps the
    # frame face).
    hw_elems: list[str] = []
    if r.sash_hardware == "cam_latch":
        hw_elems = [f"{primary}_latch_plate", f"{primary}_latch_lever"]
    elif r.sash_hardware == "sash_lock":
        hw_elems = [f"{primary}_lock_body", f"{primary}_lock_lever"]
    elif r.sash_hardware == "pull_cup":
        hw_elems = [f"{primary}_pull_rim", f"{primary}_pull_backplate"]
    elif r.sash_hardware == "pull_handle":
        hw_elems = [
            f"{primary}_handle_grip",
            f"{primary}_handle_boss_top",
            f"{primary}_handle_boss_bot",
        ]
    else:  # revolute_latch
        hw_elems = [f"{primary}_latch_keeper"]
        latch_part = f"{primary}_latch"
        ctx.allow_overlap(latch_part, primary, elem_a=f"{primary}_latch_hub", elem_b=f"{primary}_latch_keeper",
                          reason="Latch hub pivots against the keeper plate (captured pin).")
        ctx.allow_overlap(latch_part, primary, elem_a=f"{primary}_latch_hub", elem_b=f"{primary}_frame",
                          reason="Latch hub seated on the sash meeting stile (captured pin).")
        ctx.allow_overlap("frame", latch_part, elem_a="frame_shell", elem_b=f"{primary}_latch_hub",
                          reason="Latch hub laps the frame post at the meeting edge (closed pose).")
        ctx.allow_overlap("frame", latch_part, elem_a="frame_shell", elem_b=f"{primary}_latch_lever",
                          reason="Latch lever laps the frame post at the meeting edge (closed pose).")
        # Vertical: the latch on the lower-sash meeting rail laps the upper sash
        # (the two sashes overlap by one rail at the meeting rail).
        if r.orientation_drive == "vertical_double_hung":
            ctx.allow_overlap("upper_sash", latch_part,
                              reason="Lower-sash latch sits at the meeting rail where the upper sash overlaps.")
    for elem in hw_elems:
        ctx.allow_overlap(primary, primary, elem_a=elem, elem_b=f"{primary}_frame",
                          reason="Hardware seated on the sash meeting edge (mounted, not floating).")
        ctx.allow_overlap("frame", primary, elem_a="frame_shell", elem_b=elem,
                          reason="Meeting-edge hardware laps the frame post/mullion at the closed pose.")
        # Meeting-rail hardware near a stile end can graze the thin track rib.
        for re in rib_elems:
            ctx.allow_overlap("frame", primary, elem_a=re, elem_b=elem,
                              reason="Meeting-rail hardware grazes the thin track rib (few-mm constant lap).")
        # Vertical: static meeting-rail hardware on the lower sash laps the upper
        # sash (frame + glass) by a few mm where the two sashes meet.
        if r.orientation_drive == "vertical_double_hung":
            for ue in ("upper_sash_frame", "upper_sash_glass"):
                ctx.allow_overlap("upper_sash", primary, elem_a=ue, elem_b=elem,
                                  reason="Meeting-rail hardware on the lower sash laps the overlapping upper sash by a few mm.")

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    ctx.check("frame root present", "frame" in part_names, details=str(sorted(part_names)))

    # At least one PRISMATIC sliding sash (category identity).
    prismatics = [
        a for a in object_model.articulations
        if a.articulation_type == ArticulationType.PRISMATIC
    ]
    ctx.check(
        "has >=1 PRISMATIC sliding sash (category identity)",
        len(prismatics) >= 1,
        details=f"prismatic joints={[a.name for a in prismatics]}",
    )
    ctx.check(
        "sliding sash count matches S",
        len(prismatics) == r.sliding_count,
        details=f"S={r.sliding_count} prismatics={len(prismatics)}",
    )
    # No REVOLUTE swing sash (only the optional revolute_latch hardware allowed).
    revolutes = [
        a for a in object_model.articulations
        if a.articulation_type == ArticulationType.REVOLUTE
    ]
    expected_rev = 1 if r.sash_hardware == "revolute_latch" else 0
    ctx.check(
        "no swing sash; revolute only for revolute_latch",
        len(revolutes) == expected_rev,
        details=f"revolutes={[a.name for a in revolutes]} expected={expected_rev}",
    )

    # ---- Closed pose (q=0): window stands, sill near floor. ----
    f_aabb = ctx.part_world_aabb(frame)
    if f_aabb is not None:
        (fxmn, fymn, fzmn), (fxmx, fymx, fzmx) = f_aabb
        ctx.check("sill near z=0", abs(fzmn) < 0.03, details=f"z_min={fzmn:.4f}")
        ctx.check("frame stands tall", (fzmx - fzmn) > 0.6, details=f"h={fzmx - fzmn:.3f}")
        # Frame wider/taller than deep (stands, not lying down).
        depth = fymx - fymn
        ctx.check(
            "frame is a standing window (depth < height)",
            depth < (fzmx - fzmn),
            details=f"depth={depth:.3f} height={fzmx - fzmn:.3f}",
        )

    # ---- Sliding sash actuation + retention. ----
    if r.orientation_drive == "horizontal_slide":
        # Pick the primary slider joint.
        sj = object_model.get_articulation(f"frame_to_{primary}")
        sash = object_model.get_part(primary)
        with ctx.pose({sj: 0.0}):
            closed = ctx.part_world_aabb(sash)
        rest_cx = (closed[0][0] + closed[1][0]) / 2.0
        rest_cz = (closed[0][2] + closed[1][2]) / 2.0
        travel = sj.motion_limits.upper
        with ctx.pose({sj: travel}):
            opened = ctx.part_world_aabb(sash)
        open_cx = (opened[0][0] + opened[1][0]) / 2.0
        open_cz = (opened[0][2] + opened[1][2]) / 2.0
        ctx.check(
            "horizontal sash slides along X by ~travel",
            abs(abs(open_cx - rest_cx) - travel) < 0.02,
            details=f"rest_x={rest_cx:.3f} open_x={open_cx:.3f} travel={travel:.3f}",
        )
        ctx.check(
            "horizontal slide is purely horizontal (no Z drift)",
            abs(open_cz - rest_cz) < 0.02,
            details=f"open_z={open_cz:.3f} rest_z={rest_cz:.3f}",
        )
        with ctx.pose({sj: travel}):
            ctx.expect_overlap(
                sash, frame, axes="z", min_overlap=0.08,
                name="sash retains head/sill track engagement at full travel",
            )
        # Proud-Y contract: sliding sash front of a fixed lite (if any).
        if fixed_lite_names:
            lite = object_model.get_part(fixed_lite_names[0])
            with ctx.pose({sj: 0.0}):
                s_ab = ctx.part_world_aabb(sash)
                l_ab = ctx.part_world_aabb(lite)
            sy = (s_ab[0][1] + s_ab[1][1]) / 2.0
            ly = (l_ab[0][1] + l_ab[1][1]) / 2.0
            ctx.check(
                "sliding sash proud (offset Y) of fixed lite",
                abs(sy - ly) > 0.015,
                details=f"sash_y={sy:.3f} lite_y={ly:.3f}",
            )
        # Dual sliders ride offset Y planes + opposed axes.
        if r.sliding_count == 2 and len(sash_parts) >= 2:
            ax_signs = []
            ys = []
            for sn in movable_sash_names:
                jj = object_model.get_articulation(f"frame_to_{sn}")
                ax_signs.append(jj.axis[0])
                ab = ctx.part_world_aabb(object_model.get_part(sn))
                ys.append((ab[0][1] + ab[1][1]) / 2.0)
            ctx.check(
                "dual sliders use opposed X axes",
                ax_signs[0] * ax_signs[1] < 0,
                details=f"axes={ax_signs}",
            )
            ctx.check(
                "dual sliders ride offset Y planes",
                abs(ys[0] - ys[1]) > 0.010,
                details=f"ys={ys}",
            )
    else:
        # Vertical: lower sash slides up.
        lj = object_model.get_articulation("frame_to_lower_sash")
        lower = object_model.get_part("lower_sash")
        with ctx.pose({lj: 0.0}):
            closed = ctx.part_world_aabb(lower)
        rest_cz = (closed[0][2] + closed[1][2]) / 2.0
        rest_cx = (closed[0][0] + closed[1][0]) / 2.0
        travel = lj.motion_limits.upper
        with ctx.pose({lj: travel}):
            opened = ctx.part_world_aabb(lower)
        open_cz = (opened[0][2] + opened[1][2]) / 2.0
        open_cx = (opened[0][0] + opened[1][0]) / 2.0
        ctx.check(
            "lower sash slides UP by ~travel",
            (open_cz - rest_cz) > travel * 0.8,
            details=f"rest_z={rest_cz:.3f} open_z={open_cz:.3f} travel={travel:.3f}",
        )
        ctx.check(
            "vertical slide has no X drift",
            abs(open_cx - rest_cx) < 0.02,
            details=f"open_x={open_cx:.3f} rest_x={rest_cx:.3f}",
        )
        with ctx.pose({lj: travel}):
            ctx.expect_overlap(
                lower, frame, axes="x", min_overlap=0.04,
                name="lower sash retained in jamb tracks at full travel",
            )
        # Two sashes ride offset Y planes (pass each other). Use the sash BODY
        # (_frame element) AABB so proud hardware doesn't skew the Y center.
        with ctx.pose({lj: 0.0}):
            lo = ctx.part_world_aabb(lower)
            up = ctx.part_world_aabb(object_model.get_part("upper_sash"))
            lo_f = ctx.part_element_world_aabb(lower, elem="lower_sash_frame")
            up_f = ctx.part_element_world_aabb(
                object_model.get_part("upper_sash"), elem="upper_sash_frame"
            )
        lo_cy = (lo_f[0][1] + lo_f[1][1]) / 2.0
        up_cy = (up_f[0][1] + up_f[1][1]) / 2.0
        ctx.check(
            "stacked sashes ride offset Y planes",
            abs(lo_cy - up_cy) > 0.010,
            details=f"lower_y={lo_cy:.3f} upper_y={up_cy:.3f}",
        )
        lo_cz = (lo[0][2] + lo[1][2]) / 2.0
        up_cz = (up[0][2] + up[1][2]) / 2.0
        ctx.check(
            "lower sash below upper sash at closed pose",
            lo_cz < up_cz - 0.2,
            details=f"lower_cz={lo_cz:.3f} upper_cz={up_cz:.3f}",
        )
        if r.sliding_count == 2:
            uj = object_model.get_articulation("frame_to_upper_sash")
            upper = object_model.get_part("upper_sash")
            with ctx.pose({uj: 0.0}):
                uc = ctx.part_world_aabb(upper)
            urest = (uc[0][2] + uc[1][2]) / 2.0
            with ctx.pose({uj: uj.motion_limits.upper}):
                uo = ctx.part_world_aabb(upper)
            uopen = (uo[0][2] + uo[1][2]) / 2.0
            ctx.check(
                "upper sash slides DOWN when dual",
                uopen < urest - travel * 0.8,
                details=f"rest_z={urest:.3f} open_z={uopen:.3f}",
            )

    # ---- revolute_latch joint topology. ----
    if r.sash_hardware == "revolute_latch":
        jname = f"{primary}_to_latch"
        rj = object_model.get_articulation(jname)
        ctx.check(
            "revolute_latch is REVOLUTE about Z",
            rj.articulation_type == ArticulationType.REVOLUTE and abs(rj.axis[2]) > 0.99,
            details=f"type={rj.articulation_type} axis={tuple(rj.axis)}",
        )

    # ---- HEAD/SILL CLEAN-SLIDE CHECK (closed / mid / FULL-OPEN). ----
    # The MOVING sash body (its _frame ring incl. top/bottom rails) must stay
    # within the clear opening at every slide position: its z-range must NOT enter
    # the solid head (z >= in_z1) or sill (z <= in_z0) Z-band. Only the thin guide
    # shoes bridge to the track ribs. This catches sash-rail<->head/sill 穿模 that
    # a sash<->fixed-lite check misses.
    in_z0 = r.frame_face
    in_z1 = r.total_h - r.frame_face
    moving = []
    if r.orientation_drive == "horizontal_slide":
        moving = [(sn, object_model.get_articulation(f"frame_to_{sn}")) for sn in sash_parts]
    else:
        moving = [("lower_sash", object_model.get_articulation("frame_to_lower_sash"))]
        if r.sliding_count == 2:
            moving.append(("upper_sash", object_model.get_articulation("frame_to_upper_sash")))
    for sn, jt in moving:
        sp = object_model.get_part(sn)
        for q in (0.0, 0.5, 1.0):
            with ctx.pose({jt: jt.motion_limits.upper * q}):
                ab = ctx.part_element_world_aabb(sp, elem=f"{sn}_frame")
            if ab is None:
                continue
            body_lo, body_hi = ab[0][2], ab[1][2]
            ctx.check(
                f"{sn} body clears sill solid (q={q})",
                body_lo > in_z0 - 1e-4,
                details=f"body_z_min={body_lo:.4f} sill_top={in_z0:.4f} gap={body_lo - in_z0:+.4f}",
            )
            ctx.check(
                f"{sn} body clears head solid (q={q})",
                body_hi < in_z1 + 1e-4,
                details=f"body_z_max={body_hi:.4f} head_bot={in_z1:.4f} gap={in_z1 - body_hi:+.4f}",
            )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "SlidingWindowConfig",
    "ResolvedSlidingWindowConfig",
    "build_sliding_window",
    "build_seeded_sliding_window",
    "config_from_seed",
    "resolve_config",
    "run_sliding_window_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
