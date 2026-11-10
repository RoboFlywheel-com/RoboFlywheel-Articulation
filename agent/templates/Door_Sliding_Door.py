# SPDX-License-Identifier: Apache-2.0

"""Sliding door — multi-leaf horizontal PRISMATIC slider (modular template).

Object identity (spec ``articraft_template_authoring/specs_modular_v1/Door_Sliding_Door.md``):
a set of glazed / panelled leaves that slide horizontally (PRISMATIC, axis ~ +/-X)
inside a static frame / rail to clear an opening — a residential / storefront patio
slider ~2.8-4.0 m wide, ~2.0-2.4 m tall, standing on the ground (z=0 up). The main
opening motion is ALWAYS prismatic translation; nothing rotates on a hinge (that
would be a hinged / French / folding / garage door — explicitly out of category).

Structure (pattern = ``mixed``): one static root part (``frame`` for concealed
header track, or ``barn_rail`` for exposed barn-rail) carries every permanent
fixed pane plus the track hardware; N-1 (telescoping), 1 (bypass) or 2
(center-biparting) sliding leaves hang off it via PRISMATIC joints, each on its own
Y track lane so the leaves overlap in X projection without interpenetrating.

Slots (per-seed module swaps; each sourced from a 5-star ``model.py`` snippet):

  * ``kinematics`` (3): telescoping (1 fixed + N-1 same-direction nesting sliders,
    travel ``slot*pitch - i*NEST``; src rec_door_slide_5panel_tele L250-281) /
    bypass (1 fixed + 1 slider on a forward depth plane, N=2; src
    rec_door_slide_2panel L232-243) / center_biparting (2 fixed side panes + 2
    center sliders, door_1 ``Mimic``-couples door_0 with opposite axis; src
    rec_door_slide_4panel_center L321-343).
  * ``panel_count`` (N, multiplicity axis [2,12]): the number of glazed/panelled
    leaves. Encoded into the slot_choice tuple as ``("panel_count", f"n{N}")``.
    Loop-emission baseline (``for i in range(N-1)``) from the 5/6-panel gold sources.
  * ``track_style`` (2): concealed_header (perimeter frame + hidden head/sill track
    channels that capture each leaf rail; src 5panel L196-207, 2panel L120-142) /
    exposed_barn (no perimeter frame: exposed steel rail bar + wall brackets + top
    roller hangers + floor guide; src rec_sliding_door_var_barn_rail L122-274).
  * ``infill`` (4): full_glass (transparent sheet; 5panel L103-108) /
    muntin_grid (2x3 divided lites + glazing bars; src rec_sliding_door_var_muntin_grid
    L66-118) / raised_panel (opaque Shaker stile-and-rail + recessed field; src
    rec_sliding_door_var_raised_panel L63-96) / slatted_louver (>=N tilted blades;
    src rec_sliding_door_var_slatted_louver L66-101).
  * ``handle`` (4): flush_bar (thin proud bar; 2panel L210-222) / curved_C_pull
    (bowed tube C-pull + 2 necks; src 4panel_center L131-184) / proud_D_loop (round
    tube grip + 2 standoff necks; src rec_sliding_door_var_d_loop_handle L213-247) /
    finger_pocket (CadQuery cutBlind flush pocket in the leading stile, no proud
    handle; src rec_sliding_door_var_flush_finger_pull L64-105).
  * ``framing`` (2): slim_black_alu (slim dark members) / wide_white_vinyl (wider
    white uPVC members). Modulates member face/depth + material only; no topology.
  * ``palette_style`` (6): material colorway (frame RGBA + glass tint + wood color),
    sampled per seed, driving every ``.visual`` material.

Rule 1: every non-moving detail (infill, handle, fixed panes, track hardware,
roller wheels) is a ``parent.visual`` of an existing part, never a FIXED child.
Rule 2: every PRISMATIC leaf joint declares a ``MatingContract`` pinning the leaf
top-rail top face to the track / rail bottom face (concealed = head_track,
exposed_barn = rail_bar), within ``contact_tol``.
Rule 3: source primitives preserved — muntin/Shaker/louver stay Box grids, the
finger pocket stays a CadQuery ``mesh_from_cadquery`` solid, the barn roller stays
a ``mesh_from_geometry(CylinderGeometry)`` curved wheel; nothing is downgraded.

Compatibility gating (``resolve_config``, spec §sampling / reject cases):
  * bypass <=> N=2 (force N=2 when bypass selected).
  * center_biparting <=> even N; baseline N=4 (force to 4 when odd, since the
    center source only proves the 2-fixed + 2-center layout).
  * exposed_barn only with (N=2, bypass) — the only landed barn source is a single
    leaf_slide; otherwise fall back to concealed_header.
  * oak_warm_wood palette only when infill in {raised_panel, slatted_louver}.
  * finger_pocket requires CadQuery; if unavailable it degrades to flush_bar.
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
    CylinderGeometry,
    Inertial,
    MatingContract,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

try:  # CadQuery is used only for the finger-pocket flush stile (source S12).
    import cadquery as cq  # noqa: F401

    from sdk import mesh_from_cadquery

    _HAS_CADQUERY = True
except Exception:  # pragma: no cover - environment without cadquery
    _HAS_CADQUERY = False

__modular__ = True

Kinematics = Literal["telescoping", "bypass", "center_biparting"]
TrackStyle = Literal["concealed_header", "exposed_barn"]
Infill = Literal["full_glass", "muntin_grid", "raised_panel", "slatted_louver"]
Handle = Literal["flush_bar", "curved_C_pull", "proud_D_loop", "finger_pocket"]
Framing = Literal["slim_black_alu", "wide_white_vinyl"]
PaletteStyle = Literal[
    "charcoal_black_alu",
    "anodized_dark_bronze",
    "warm_white_vinyl",
    "clear_glass_neutral",
    "tinted_grey_glass",
    "oak_warm_wood",
]

KINEMATICS: tuple[Kinematics, ...] = ("telescoping", "bypass", "center_biparting")
TRACK_STYLES: tuple[TrackStyle, ...] = ("concealed_header", "exposed_barn")
INFILLS: tuple[Infill, ...] = ("full_glass", "muntin_grid", "raised_panel", "slatted_louver")
HANDLES: tuple[Handle, ...] = ("flush_bar", "curved_C_pull", "proud_D_loop", "finger_pocket")
FRAMINGS: tuple[Framing, ...] = ("slim_black_alu", "wide_white_vinyl")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "charcoal_black_alu",
    "anodized_dark_bronze",
    "warm_white_vinyl",
    "clear_glass_neutral",
    "tinted_grey_glass",
    "oak_warm_wood",
)

N_MIN = 2
N_MAX = 12
# Multiplicity weights (spec §Multiplicity): small N high frequency, large N rare.
# Index 0 == N=2 .. index 10 == N=12.
PANEL_COUNT_WEIGHTS = (
    0.22,  # 2
    0.20,  # 3
    0.22,  # 4
    0.16,  # 5
    0.10,  # 6
    0.030,  # 7
    0.025,  # 8
    0.025,  # 9
    0.008,  # 10
    0.007,  # 11
    0.005,  # 12
)

# Infills compatible with the oak_warm_wood palette (wood reads only on
# opaque panelled / louvered leaves; spec §palette).
OAK_INFILLS: tuple[Infill, ...] = ("raised_panel", "slatted_louver")

# Palettes: frame (member metal/vinyl/wood), trim (slightly lighter frame),
# glass (transparent tint, alpha < 0.5), wood_center (raised-panel field /
# louver blade), handle (pull metal). Every .visual material draws from this.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "charcoal_black_alu": {
        "frame": (0.09, 0.09, 0.10, 1.0),
        "trim": (0.13, 0.13, 0.14, 1.0),
        "glass": (0.62, 0.70, 0.72, 0.22),
        "wood_center": (0.40, 0.26, 0.14, 1.0),
        "handle": (0.16, 0.16, 0.17, 1.0),
    },
    "anodized_dark_bronze": {
        "frame": (0.16, 0.12, 0.08, 1.0),
        "trim": (0.22, 0.17, 0.11, 1.0),
        "glass": (0.55, 0.52, 0.45, 0.26),
        "wood_center": (0.34, 0.22, 0.12, 1.0),
        "handle": (0.30, 0.24, 0.16, 1.0),
    },
    "warm_white_vinyl": {
        "frame": (0.93, 0.94, 0.94, 1.0),
        "trim": (0.88, 0.89, 0.90, 1.0),
        "glass": (0.78, 0.84, 0.88, 0.16),
        "wood_center": (0.86, 0.80, 0.70, 1.0),
        "handle": (0.96, 0.96, 0.97, 1.0),
    },
    "clear_glass_neutral": {
        "frame": (0.10, 0.10, 0.11, 1.0),
        "trim": (0.15, 0.15, 0.16, 1.0),
        "glass": (0.78, 0.82, 0.84, 0.12),
        "wood_center": (0.44, 0.30, 0.18, 1.0),
        "handle": (0.20, 0.20, 0.22, 1.0),
    },
    "tinted_grey_glass": {
        "frame": (0.11, 0.11, 0.12, 1.0),
        "trim": (0.16, 0.16, 0.17, 1.0),
        "glass": (0.42, 0.46, 0.48, 0.34),
        "wood_center": (0.40, 0.28, 0.16, 1.0),
        "handle": (0.18, 0.18, 0.19, 1.0),
    },
    "oak_warm_wood": {
        "frame": (0.46, 0.32, 0.18, 1.0),
        "trim": (0.40, 0.27, 0.15, 1.0),
        "glass": (0.62, 0.70, 0.72, 0.22),
        "wood_center": (0.58, 0.42, 0.26, 1.0),
        "handle": (0.30, 0.20, 0.12, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Width along X, height along Z, depth Y.
# The frame stands on the ground (z=0..FRAME_H). Numbers follow the 5-star
# parents (5panel: FRAME_W=3.0, MEMBER=0.070; 4panel_center: white wide).
# ---------------------------------------------------------------------------
_FRAME_W = 3.20          # outer frame width (X)
_FRAME_H = 2.30          # outer frame height (Z)
_MEMBER_SLIM = 0.055     # slim_black_alu frame member face
_MEMBER_WIDE = 0.070     # wide_white_vinyl frame member face
_STILE_SLIM = 0.038      # slim leaf stile/rail face
_STILE_WIDE = 0.055      # wide leaf stile/rail face
_LEAF_T = 0.024          # leaf member thickness (Y)
_GLASS_T = 0.007         # glazing thickness (Y)
_LANE_GAP = 0.044        # center-to-center Y spacing between adjacent lanes
_TRACK_T = 0.024         # head/sill track channel height (Z)
_TRACK_ENGAGE = 0.008    # how far the leaf rail tucks into the track channel
_NEST = 0.045            # X engagement kept between nested telescoping leaves
_MEET_OVERLAP = 0.030    # closed meeting-stile interlock width

# Barn-rail hardware (exposed_barn track_style; src barn_rail L48-95).
_RAIL_H = 0.060
_RAIL_D = 0.040
_RAIL_GAP = 0.050        # rail bottom above the opening
_HANGER_H = 0.080
_HANGER_W = 0.050
_HANGER_T = 0.008
_ROLLER_R = 0.018
_ROLLER_W = 0.025


@dataclass(frozen=True)
class SlidingDoorConfig:
    kinematics: Kinematics | None = None
    panel_count: int | None = None
    track_style: TrackStyle | None = None
    infill: Infill | None = None
    handle: Handle | None = None
    framing: Framing | None = None
    palette_style: PaletteStyle = "charcoal_black_alu"
    opening_width_scale: float = 1.0
    opening_height_scale: float = 1.0
    frame_face_scale: float = 1.0
    lane_gap_scale: float = 1.0
    name: str = "sliding_door"


@dataclass(frozen=True)
class ResolvedSlidingDoorConfig:
    kinematics: Kinematics
    panel_count: int
    track_style: TrackStyle
    infill: Infill
    handle: Handle
    framing: Framing
    palette_style: PaletteStyle
    # Concrete (scaled / derived) geometry.
    frame_w: float
    frame_h: float
    member: float
    stile: float
    leaf_t: float
    glass_t: float
    lane_gap: float
    track_t: float
    track_engage: float
    nest: float
    meet_overlap: float
    # Derived opening / leaf layout.
    open_w: float           # clear glazed width inside members
    open_h: float           # clear glazed height inside members
    open_x0: float          # left edge of the clear opening
    open_z0: float          # bottom of the clear opening (above sill)
    open_zc: float          # vertical center of the glazed area
    panes_across: int       # leaves tiling the opening width (drives pitch)
    pane_pitch: float       # one slot width / center spacing
    pane_w: float           # leaf width incl. meeting-stile overlap
    pane_h: float           # leaf height (rails reach into the tracks)
    n_sliders: int          # number of moving leaves
    name: str

    @property
    def lane0_y(self) -> float:
        """Y center of the rearmost lane (fixed pane)."""
        n_lanes = max(2, self.panel_count)
        return -0.5 * (n_lanes - 1) * self.lane_gap

    @property
    def frame_d(self) -> float:
        """Frame depth spanning every track lane (inequality: depth >= lanes)."""
        n_lanes = max(2, self.panel_count)
        return (n_lanes - 1) * self.lane_gap + 2.0 * self.leaf_t + 0.04


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> SlidingDoorConfig:
    rng = random.Random(seed)
    n = rng.choices(range(N_MIN, N_MAX + 1), weights=PANEL_COUNT_WEIGHTS, k=1)[0]
    return SlidingDoorConfig(
        kinematics=rng.choice(KINEMATICS),
        panel_count=n,
        track_style=rng.choice(TRACK_STYLES),
        infill=rng.choice(INFILLS),
        handle=rng.choice(HANDLES),
        framing=rng.choice(FRAMINGS),
        palette_style=rng.choice(PALETTE_STYLES),
        opening_width_scale=round(rng.uniform(0.85, 1.20), 4),
        opening_height_scale=round(rng.uniform(0.90, 1.15), 4),
        frame_face_scale=round(rng.uniform(0.85, 1.25), 4),
        lane_gap_scale=round(rng.uniform(0.90, 1.30), 4),
        name=f"seeded_sliding_door_{seed}",
    )


def resolve_config(config: SlidingDoorConfig | None = None) -> ResolvedSlidingDoorConfig:
    cfg = config or SlidingDoorConfig()

    kinematics = _pick(cfg.kinematics, KINEMATICS)
    track_style = _pick(cfg.track_style, TRACK_STYLES)
    infill = _pick(cfg.infill, INFILLS)
    handle = _pick(cfg.handle, HANDLES)
    framing = _pick(cfg.framing, FRAMINGS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    panel_count = int(cfg.panel_count) if cfg.panel_count is not None else 3
    panel_count = int(_clamp(panel_count, N_MIN, N_MAX))

    # --- Compatibility gating (spec §sampling / reject cases). ---
    # bypass only proves a single-slider N=2 layout.
    if kinematics == "bypass":
        panel_count = 2
    # center_biparting only proves 2 fixed + 2 center sliders -> even N, baseline 4.
    elif kinematics == "center_biparting":
        if panel_count % 2 != 0:
            panel_count = 4
        else:
            panel_count = 4  # the landed center source is the N=4 layout
    # telescoping covers N in [3, 12]; if it sampled N=2, lift to 3 (1 fixed + 2).
    else:  # telescoping
        if panel_count < 3:
            panel_count = 3

    # exposed_barn only landed for (N=2, bypass); otherwise concealed_header.
    if track_style == "exposed_barn" and not (kinematics == "bypass" and panel_count == 2):
        track_style = "concealed_header"

    # finger_pocket needs CadQuery (mesh-backed stile); degrade if unavailable.
    if handle == "finger_pocket" and not _HAS_CADQUERY:
        handle = "flush_bar"

    # oak_warm_wood reads only on opaque panelled / louvered infill.
    if palette_style == "oak_warm_wood" and infill not in OAK_INFILLS:
        palette_style = "charcoal_black_alu"

    # --- Continuous scales (clamped). ---
    w_scale = _clamp(cfg.opening_width_scale, 0.85, 1.20)
    h_scale = _clamp(cfg.opening_height_scale, 0.90, 1.15)
    face_scale = _clamp(cfg.frame_face_scale, 0.85, 1.25)
    lane_scale = _clamp(cfg.lane_gap_scale, 0.90, 1.30)

    base_member = _MEMBER_WIDE if framing == "wide_white_vinyl" else _MEMBER_SLIM
    base_stile = _STILE_WIDE if framing == "wide_white_vinyl" else _STILE_SLIM
    member = base_member * face_scale
    stile = base_stile * face_scale
    leaf_t = _LEAF_T
    glass_t = _GLASS_T
    track_t = _TRACK_T
    track_engage = _TRACK_ENGAGE
    nest = _NEST
    lane_gap = _LANE_GAP * lane_scale

    frame_w = _FRAME_W * w_scale
    frame_h = _FRAME_H * h_scale

    open_w = frame_w - 2.0 * member
    open_h = frame_h - 2.0 * member
    open_x0 = -open_w / 2.0
    open_z0 = member
    open_zc = open_z0 + open_h / 2.0

    # panes_across drives the per-slot pitch (telescoping = N, center = 4,
    # bypass = 2). meeting overlap derived from stile (spec: meet_overlap=k*STILE).
    if kinematics == "telescoping":
        panes_across = panel_count
        n_sliders = panel_count - 1
    elif kinematics == "bypass":
        panes_across = 2
        n_sliders = 1
    else:  # center_biparting
        panes_across = 4
        n_sliders = 2

    meet_overlap = _clamp(0.8 * stile, 0.018, 0.060)
    pane_pitch = open_w / panes_across
    pane_w = pane_pitch + meet_overlap

    # Leaf height: rails reach track_engage into the head/sill channels.
    pane_h = open_h - 2.0 * (track_t - track_engage)

    return ResolvedSlidingDoorConfig(
        kinematics=kinematics,
        panel_count=panel_count,
        track_style=track_style,
        infill=infill,
        handle=handle,
        framing=framing,
        palette_style=palette_style,
        frame_w=frame_w,
        frame_h=frame_h,
        member=member,
        stile=stile,
        leaf_t=leaf_t,
        glass_t=glass_t,
        lane_gap=lane_gap,
        track_t=track_t,
        track_engage=track_engage,
        nest=nest,
        meet_overlap=meet_overlap,
        open_w=open_w,
        open_h=open_h,
        open_x0=open_x0,
        open_z0=open_z0,
        open_zc=open_zc,
        panes_across=panes_across,
        pane_pitch=pane_pitch,
        pane_w=pane_w,
        pane_h=pane_h,
        n_sliders=n_sliders,
        name=cfg.name or "sliding_door",
    )


def with_overrides(config: SlidingDoorConfig, **kwargs: object) -> SlidingDoorConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SlidingDoorConfig | ResolvedSlidingDoorConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedSlidingDoorConfig) else resolve_config(config)
    return (
        ("kinematics", r.kinematics),
        ("panel_count", f"n{r.panel_count}"),
        ("track_style", r.track_style),
        ("infill", r.infill),
        ("handle", r.handle),
        ("framing", r.framing),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Lane / placement helpers (loop-emission baseline; src 5panel L76-89).
# ---------------------------------------------------------------------------
def _lane_y(r: ResolvedSlidingDoorConfig, index: int) -> float:
    """Y center of track lane ``index`` (0 = rearmost / fixed)."""
    return r.lane0_y + index * r.lane_gap


def _pane_center_x_closed(r: ResolvedSlidingDoorConfig, slot: int) -> float:
    """X center of the leaf filling opening slot ``slot`` (closed pose).

    The leaf is slightly wider than its slot; the extra width is carried on the
    leading (-X) side so the trailing edge stays at the slot boundary.
    """
    return r.open_x0 + (slot + 0.5) * r.pane_pitch - r.meet_overlap / 2.0


# ---------------------------------------------------------------------------
# Infill helpers (Rule 1 visuals; Rule 3 source primitives preserved). Each
# fills a glazing region (cx, cy, cz) of size (glass_w, glass_h) on the part.
# ---------------------------------------------------------------------------
_MUNTIN_COLS = 2
_MUNTIN_ROWS = 3
_MUNTIN_W = 0.016   # glazing bar width (src muntin L50)
_MUNTIN_D = 0.012   # glazing bar depth (proud of glass; MUNTIN_D > GLASS_T)
_SLAT_DEPTH = 0.040
_SLAT_THICK = 0.005
_SLAT_SPACING = 0.060
_SLAT_ANGLE = 0.52  # ~30 deg tilt (src louver L47)
_PANEL_RECESS = 0.006


def _emit_full_glass(part, r, mats, *, cx, cy, cz, glass_w, glass_h, prefix):
    """Single transparent sheet (src 5panel L103-108)."""
    part.visual(
        Box((glass_w, r.glass_t, glass_h)),
        origin=Origin(xyz=(cx, cy, cz)),
        material=mats["glass"],
        name=f"{prefix}_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"charcoal_black_alu", "warm_white_vinyl", "clear_glass_neutral", "oak_warm_wood"} else "glass.smoked_tinted"),
    )


def _emit_muntin_grid(part, r, mats, *, cx, cy, cz, glass_w, glass_h, prefix):
    """2x3 divided-lite grid of glass lites + proud glazing bars (src muntin L66-118)."""
    n_vbars = _MUNTIN_COLS - 1
    n_hbars = _MUNTIN_ROWS - 1
    lite_w = (glass_w - n_vbars * _MUNTIN_W) / _MUNTIN_COLS
    lite_h = (glass_h - n_hbars * _MUNTIN_W) / _MUNTIN_ROWS
    x0 = cx - glass_w / 2.0
    z0 = cz - glass_h / 2.0
    idx = 0
    for row in range(_MUNTIN_ROWS):
        for col in range(_MUNTIN_COLS):
            lx = x0 + lite_w / 2.0 + col * (lite_w + _MUNTIN_W)
            lz = z0 + lite_h / 2.0 + row * (lite_h + _MUNTIN_W)
            part.visual(
                Box((lite_w, r.glass_t, lite_h)),
                origin=Origin(xyz=(lx, cy, lz)),
                material=mats["glass"],
                name=f"{prefix}_lite_{idx}", material_class_id=("glass.clear_transparent" if r.palette_style in {"charcoal_black_alu", "warm_white_vinyl", "clear_glass_neutral", "oak_warm_wood"} else "glass.smoked_tinted"),
            )
            idx += 1
    for i in range(n_vbars):
        bx = x0 + lite_w + _MUNTIN_W / 2.0 + i * (lite_w + _MUNTIN_W)
        part.visual(
            Box((_MUNTIN_W, _MUNTIN_D, glass_h)),
            origin=Origin(xyz=(bx, cy, cz)),
            material=mats["trim"],
            name=f"{prefix}_vbar_{i}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    for i in range(n_hbars):
        bz = z0 + lite_h + _MUNTIN_W / 2.0 + i * (lite_h + _MUNTIN_W)
        part.visual(
            Box((glass_w, _MUNTIN_D, _MUNTIN_W)),
            origin=Origin(xyz=(cx, cy, bz)),
            material=mats["trim"],
            name=f"{prefix}_hbar_{i}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )


def _emit_raised_panel(part, r, mats, *, cx, cy, cz, glass_w, glass_h, prefix):
    """Opaque Shaker stile-and-rail border + recessed flat center field
    (src raised_panel add_shaker_panel L63-96). Border is proud of the center."""
    border_w = min(0.065, glass_w * 0.18, glass_h * 0.12)
    border_d = r.glass_t + 0.010
    center_d = r.glass_t
    center_cy = cy - _PANEL_RECESS / 2.0
    inner_w = glass_w - 2.0 * border_w
    inner_h = glass_h - 2.0 * border_w
    for i in range(2):
        sx = cx + (2 * i - 1) * (glass_w / 2.0 - border_w / 2.0)
        part.visual(
            Box((border_w, border_d, glass_h)),
            origin=Origin(xyz=(sx, cy, cz)),
            material=mats["trim"],
            name=f"{prefix}_pstile_{i}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    for i in range(2):
        rz = cz + (2 * i - 1) * (glass_h / 2.0 - border_w / 2.0)
        part.visual(
            Box((inner_w, border_d, border_w)),
            origin=Origin(xyz=(cx, cy, rz)),
            material=mats["trim"],
            name=f"{prefix}_prail_{i}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    part.visual(
        Box((inner_w, center_d, inner_h)),
        origin=Origin(xyz=(cx, center_cy, cz)),
        material=mats["wood_center"],
        name=f"{prefix}_center", material_class_id=("wood.oak" if r.palette_style == "oak_warm_wood" else "wood.natural_generic"),
    )


def _emit_slatted_louver(part, r, mats, *, cx, cy, cz, glass_w, glass_h, prefix):
    """Horizontal tilted louver blades (src louver _add_louver_slats L66-101).
    n = max(2, height/spacing) blades sharing a uniform roll tilt."""
    n = max(2, int(glass_h / _SLAT_SPACING))
    total_span = (n - 1) * _SLAT_SPACING
    z_start = cz - total_span / 2.0
    for i in range(n):
        z = z_start + i * _SLAT_SPACING
        part.visual(
            Box((glass_w, _SLAT_DEPTH, _SLAT_THICK)),
            origin=Origin(xyz=(cx, cy, z), rpy=(_SLAT_ANGLE, 0.0, 0.0)),
            material=mats["wood_center"],
            name=f"{prefix}_slat_{i}", material_class_id=("wood.oak" if r.palette_style == "oak_warm_wood" else "wood.natural_generic"),
        )


_INFILL_EMITTERS = {
    "full_glass": _emit_full_glass,
    "muntin_grid": _emit_muntin_grid,
    "raised_panel": _emit_raised_panel,
    "slatted_louver": _emit_slatted_louver,
}


# ---------------------------------------------------------------------------
# Pocket-stile CadQuery mesh (finger_pocket handle; src finger_pull L64-81).
# ---------------------------------------------------------------------------
def _pocket_stile_mesh(r: ResolvedSlidingDoorConfig, assets, *, name: str):
    """A leading stile with a flush finger-pull pocket cut into its -X face."""
    sx, sy, sz = r.stile, r.leaf_t, r.pane_h
    solid = cq.Workplane("XY").box(sx, sy, sz)
    pocket_depth = min(0.014, sx * 0.6)
    pocket_w_y = min(0.018, sy * 0.7)
    pocket_h_z = min(0.120, sz * 0.4)
    solid = (
        solid.faces("<X")
        .workplane()
        .rect(pocket_w_y, pocket_h_z)
        .cutBlind(-pocket_depth)
    )
    return mesh_from_cadquery(solid, name, assets=assets)


# ---------------------------------------------------------------------------
# Handle helpers (Rule 1 leaf-local visuals). handle_x is the local X of the
# leading stile center; face_y is the room-side (+Y) face of the leaf.
# ---------------------------------------------------------------------------
def _emit_flush_bar(part, r, mats, *, handle_x, face_y, z0, prefix):
    """Thin proud vertical bar pull (src 2panel L210-222)."""
    part.visual(
        Box((0.012, 0.016, min(0.30, r.pane_h * 0.4))),
        origin=Origin(xyz=(handle_x, face_y + 0.008, z0)),
        material=mats["handle"],
        name=f"{prefix}_handle_bar", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )


def _emit_curved_C_pull(part, r, mats, *, handle_x, face_y, z0, prefix):
    """Bowed tube C-pull + two angled mounting necks (src 4panel_center L131-184)."""
    handle_h = min(0.21, r.pane_h * 0.32)
    bow_x_out = 0.055
    bow_y_out = 0.030
    tube_r = 0.011
    neck_r = 0.009
    anchor_x = handle_x
    anchor_y = face_y - 0.012
    grip_x = handle_x + bow_x_out
    grip_y = face_y + bow_y_out
    neck_dx = grip_x - anchor_x
    neck_dy = grip_y - anchor_y
    neck_len = math.hypot(neck_dx, neck_dy) + 0.004
    neck_yaw = math.atan2(neck_dy, neck_dx)
    for sign, suffix in ((1.0, "neck_top"), (-1.0, "neck_bottom")):
        zc = z0 + sign * (handle_h / 2.0 - 0.022)
        part.visual(
            Cylinder(radius=neck_r, length=neck_len),
            origin=Origin(
                xyz=((anchor_x + grip_x) / 2.0, (anchor_y + grip_y) / 2.0, zc),
                rpy=(0.0, math.pi / 2.0, neck_yaw),
            ),
            material=mats["handle"],
            name=f"{prefix}_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    part.visual(
        Cylinder(radius=tube_r, length=handle_h),
        origin=Origin(xyz=(grip_x, grip_y, z0)),
        material=mats["handle"],
        name=f"{prefix}_grip", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )


def _emit_proud_D_loop(part, r, mats, *, handle_x, face_y, z0, prefix):
    """Round tube grip standing proud, tied by two standoff necks (src d_loop L213-247)."""
    grip_r = 0.010
    grip_len = min(0.26, r.pane_h * 0.4)
    neck_r = 0.006
    neck_len = 0.030
    grip_cy = face_y + neck_len + grip_r
    part.visual(
        Cylinder(radius=grip_r, length=grip_len),
        origin=Origin(xyz=(handle_x, grip_cy, z0)),
        material=mats["handle"],
        name=f"{prefix}_grip", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    neck_cy = face_y + neck_len / 2.0
    for i, dz in enumerate((grip_len / 2.0 - 0.025, -(grip_len / 2.0 - 0.025))):
        part.visual(
            Cylinder(radius=neck_r, length=neck_len),
            origin=Origin(xyz=(handle_x, neck_cy, z0 + dz), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=mats["handle"],
            name=f"{prefix}_neck_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )


# finger_pocket emits no proud handle (the pocket lives in the leading stile mesh).
def _emit_finger_pocket(part, r, mats, *, handle_x, face_y, z0, prefix):
    return None


_HANDLE_EMITTERS = {
    "flush_bar": _emit_flush_bar,
    "curved_C_pull": _emit_curved_C_pull,
    "proud_D_loop": _emit_proud_D_loop,
    "finger_pocket": _emit_finger_pocket,
}


# ---------------------------------------------------------------------------
# Leaf builder (one glazed/panelled leaf, authored centered at part origin).
# leading_sign: which stile (-1 = -X, +1 = +X) carries the handle / pocket.
# ---------------------------------------------------------------------------
def _leaf_body_cz(r: ResolvedSlidingDoorConfig) -> float:
    """Z of the leaf vertical center in the leaf-local frame.

    The leaf part origin (0,0,0) is placed at the BOTTOM-RAIL center so the
    PRISMATIC joint origin can be anchored on the sill track (real geometry),
    satisfying ``fail_if_articulation_origin_far_from_geometry``: both the
    parent sill track and the child bottom rail contain the origin. The leaf
    body therefore sits ``body_cz`` above its own part origin.
    """
    rail = r.stile
    return r.pane_h / 2.0 - rail / 2.0


def _build_leaf(part, r, mats, assets, *, leading_sign: float, prefix: str):
    half_w = r.pane_w / 2.0
    rail = r.stile
    body_cz = _leaf_body_cz(r)
    half_h = r.pane_h / 2.0
    stile_h = r.pane_h - 2.0 * rail
    glass_w = r.pane_w - 2.0 * r.stile + 0.004
    glass_h = r.pane_h - 2.0 * rail + 0.004
    top_rail_cz = body_cz + (half_h - rail / 2.0)
    bot_rail_cz = body_cz - (half_h - rail / 2.0)  # == 0.0 (part origin)

    # Top / bottom rails — these are the members captured by the head/sill track.
    part.visual(
        Box((r.pane_w, r.leaf_t, rail)),
        origin=Origin(xyz=(0.0, 0.0, top_rail_cz)),
        material=mats["frame"],
        name=f"{prefix}_rail_top", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    part.visual(
        Box((r.pane_w, r.leaf_t, rail)),
        origin=Origin(xyz=(0.0, 0.0, bot_rail_cz)),
        material=mats["frame"],
        name=f"{prefix}_rail_bottom", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    # Stiles run between the rails (clear of the track bands). The leading stile
    # becomes the CadQuery pocket mesh when handle == finger_pocket.
    lead_x = leading_sign * (half_w - r.stile / 2.0)
    trail_x = -leading_sign * (half_w - r.stile / 2.0)
    if r.handle == "finger_pocket" and _HAS_CADQUERY:
        part.visual(
            _pocket_stile_mesh(r, assets, name=f"{prefix}_stile_lead"),
            origin=Origin(xyz=(lead_x, 0.0, body_cz)),
            material=mats["frame"],
            name=f"{prefix}_stile_lead", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    else:
        part.visual(
            Box((r.stile, r.leaf_t, stile_h)),
            origin=Origin(xyz=(lead_x, 0.0, body_cz)),
            material=mats["frame"],
            name=f"{prefix}_stile_lead", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    part.visual(
        Box((r.stile, r.leaf_t, stile_h)),
        origin=Origin(xyz=(trail_x, 0.0, body_cz)),
        material=mats["frame"],
        name=f"{prefix}_stile_trail", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    # Infill (full-glass / muntin / raised-panel / louver).
    _INFILL_EMITTERS[r.infill](
        part, r, mats, cx=0.0, cy=0.0, cz=body_cz,
        glass_w=glass_w, glass_h=glass_h, prefix=prefix,
    )
    # Handle on the leading stile, room-side (+Y) face.
    face_y = r.leaf_t / 2.0
    handle_x = lead_x - leading_sign * (r.stile / 2.0 - 0.004)
    _HANDLE_EMITTERS[r.handle](
        part, r, mats, handle_x=handle_x, face_y=face_y, z0=body_cz, prefix=prefix,
    )
    part.inertial = Inertial.from_geometry(
        Box((r.pane_w, r.leaf_t, r.pane_h)),
        mass=18.0,
        origin=Origin(xyz=(0.0, 0.0, body_cz)),
    )


# ---------------------------------------------------------------------------
# Fixed pane (built into the frame root at a given lane / slot, centered cz).
# ---------------------------------------------------------------------------
def _emit_fixed_pane(frame, r, mats, assets, *, cx, cy, cz, prefix):
    half_w = r.pane_w / 2.0
    half_h = r.pane_h / 2.0
    rail = r.stile
    stile_h = r.pane_h - 2.0 * rail
    glass_w = r.pane_w - 2.0 * r.stile + 0.004
    glass_h = r.pane_h - 2.0 * rail + 0.004
    frame.visual(
        Box((r.pane_w, r.leaf_t, rail)),
        origin=Origin(xyz=(cx, cy, cz + half_h - rail / 2.0)),
        material=mats["frame"],
        name=f"{prefix}_rail_top", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Box((r.pane_w, r.leaf_t, rail)),
        origin=Origin(xyz=(cx, cy, cz - (half_h - rail / 2.0))),
        material=mats["frame"],
        name=f"{prefix}_rail_bottom", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    for j, sx in enumerate((-(half_w - r.stile / 2.0), half_w - r.stile / 2.0)):
        frame.visual(
            Box((r.stile, r.leaf_t, stile_h)),
            origin=Origin(xyz=(cx + sx, cy, cz)),
            material=mats["frame"],
            name=f"{prefix}_stile_{j}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    _INFILL_EMITTERS[r.infill](
        frame, r, mats, cx=cx, cy=cy, cz=cz,
        glass_w=glass_w, glass_h=glass_h, prefix=prefix,
    )


# ---------------------------------------------------------------------------
# Track hardware. Concealed: perimeter members + head/sill channels (capturing
# the leaf rails). The head track bottom face is aligned to the leaf rail-top so
# the MatingContract (leaf rail_top +Z <-> head_track -Z) is tight.
# ---------------------------------------------------------------------------
def _emit_concealed_frame(frame, r, mats):
    half_w = r.frame_w / 2.0
    fd = r.frame_d
    # Sill (on ground), head (top), two jambs.
    frame.visual(
        Box((r.frame_w, fd, r.member)),
        origin=Origin(xyz=(0.0, 0.0, r.member / 2.0)),
        material=mats["frame"],
        name="sill", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Box((r.frame_w, fd, r.member)),
        origin=Origin(xyz=(0.0, 0.0, r.frame_h - r.member / 2.0)),
        material=mats["frame"],
        name="head", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    jamb_h = r.frame_h - 2.0 * r.member
    frame.visual(
        Box((r.member, fd, jamb_h)),
        origin=Origin(xyz=(-(half_w - r.member / 2.0), 0.0, r.member + jamb_h / 2.0)),
        material=mats["frame"],
        name="jamb_0", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Box((r.member, fd, jamb_h)),
        origin=Origin(xyz=(half_w - r.member / 2.0, 0.0, r.member + jamb_h / 2.0)),
        material=mats["frame"],
        name="jamb_1", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    # Head & sill track channels spanning the opening across all lanes (Y).
    # The leaf rail tops sit at open_zc + pane_h/2; align the head track bottom
    # to that line (the rail tucks track_engage up into the channel). The sill
    # track is tall enough to enclose both the leaf bottom rail AND the joint
    # origin (= bottom-rail center, ``_leaf_body_cz``) so the PRISMATIC joint
    # origin lands on real geometry (anchored on the sill track).
    rail_top_z = r.open_zc + r.pane_h / 2.0
    rail_bot_z = r.open_zc - r.pane_h / 2.0  # leaf bottom-rail bottom == joint base
    head_bottom = rail_top_z - r.track_engage
    frame.visual(
        Box((r.open_w, fd - 0.02, r.track_t)),
        origin=Origin(xyz=(0.0, 0.0, head_bottom + r.track_t / 2.0)),
        material=mats["trim"],
        name="head_track", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    # Sill track: a shallow channel hugging the leaf bottom rail, tall enough to
    # enclose the joint origin (= bottom-rail center at rail_bot_z + stile/2)
    # while staying clear of the glass above. It overlaps only the leaf bottom
    # rail (element-scoped allowance) and rests above the sill member.
    sill_bottom = max(r.member, rail_bot_z - 0.014)
    sill_top = rail_bot_z + r.stile / 2.0 + 0.005
    sill_h = sill_top - sill_bottom
    frame.visual(
        Box((r.open_w, fd - 0.02, sill_h)),
        origin=Origin(xyz=(0.0, 0.0, sill_bottom + sill_h / 2.0)),
        material=mats["trim"],
        name="sill_track", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )


def _emit_barn_rail(frame, r, mats, assets):
    """Exposed barn rail + wall brackets + floor guide (src barn_rail L122-178).
    The leaf hangs from the rail via roller hangers (built on the leaf)."""
    rail_w = r.frame_w + 0.20
    rail_bottom_z = r.frame_h + _RAIL_GAP
    frame.visual(
        Box((rail_w, _RAIL_D, _RAIL_H)),
        origin=Origin(xyz=(0.0, 0.0, rail_bottom_z + _RAIL_H / 2.0)),
        material=mats["frame"],
        name="rail_bar", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    bracket_xs = (-rail_w / 2.0 + 0.20, rail_w / 2.0 - 0.20)
    plate_full_h = rail_bottom_z + _RAIL_H
    for i, bx in enumerate(bracket_xs):
        frame.visual(
            Box((_HANGER_W + 0.010, 0.006, plate_full_h)),
            origin=Origin(xyz=(bx, -(_RAIL_D / 2.0 + 0.003), plate_full_h / 2.0)),
            material=mats["frame"],
            name=f"bracket_plate_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
        frame.visual(
            Box((_HANGER_W + 0.010, _RAIL_D, 0.006)),
            origin=Origin(xyz=(bx, 0.0, rail_bottom_z - 0.003)),
            material=mats["frame"],
            name=f"bracket_arm_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    # Floor guide at the base of the left bracket.
    gx = bracket_xs[0]
    frame.visual(
        Box((0.040, 0.040, 0.004)),
        origin=Origin(xyz=(gx, -0.001, 0.002)),
        material=mats["frame"],
        name="floor_guide_base", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Cylinder(radius=0.010, length=0.050),
        origin=Origin(xyz=(gx, -0.001, 0.004 + 0.025)),
        material=mats["handle"],
        name="floor_guide_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )


def _build_roller_mesh(assets):
    geom = CylinderGeometry(_ROLLER_R, _ROLLER_W, radial_segments=32, closed=True)
    geom.rotate_x(math.pi / 2.0)  # CylinderGeometry is +Z; align axle with Y.
    return mesh_from_geometry(geom, "roller_wheel")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_sliding_door(
    config: SlidingDoorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"sliding_door_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    if r.track_style == "exposed_barn":
        _build_barn(model, r, mats, assets)
    elif r.kinematics == "center_biparting":
        _build_center_biparting(model, r, mats, assets)
    else:  # telescoping (concealed)
        _build_telescoping(model, r, mats, assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def _leaf_mating(*, child_rail: str, parent_track: str) -> MatingContract:
    """Leaf top rail (+Z face) kisses the head track / rail bottom (-Z face)."""
    return MatingContract(
        parent_face_geometry=parent_track,
        parent_face_side="negative_z",
        child_face_geometry=child_rail,
        child_face_side="positive_z",
        contact_tol=0.012,
    )


def _build_telescoping(model, r, mats, assets):
    """1 fixed pane (slot 0, rear lane) + (N-1) telescoping sliders (src 5panel)."""
    frame = model.part("frame")
    _emit_concealed_frame(frame, r, mats)
    # Fixed pane in opening slot 0, rearmost lane.
    fixed_cx = _pane_center_x_closed(r, 0)
    fixed_cy = _lane_y(r, 0)
    _emit_fixed_pane(frame, r, mats, assets, cx=fixed_cx, cy=fixed_cy, cz=r.open_zc, prefix="fixed")
    frame.inertial = Inertial.from_geometry(
        Box((r.frame_w, r.frame_d, r.frame_h)),
        mass=80.0,
        origin=Origin(xyz=(0.0, 0.0, r.frame_h / 2.0)),
    )
    for i in range(r.n_sliders):
        slot = i + 1
        leaf = model.part(f"pane_{i}")
        _build_leaf(leaf, r, mats, assets, leading_sign=-1.0, prefix=f"pane_{i}")
        lane_y = _lane_y(r, slot)
        cx = _pane_center_x_closed(r, slot)
        # Travel toward -X; each successive leaf travels one extra pitch minus
        # NEST so the leaves telescope and stay nested (inequality: travel within
        # the opening). Clamp so the leaf never exits the frame footprint.
        travel = slot * r.pane_pitch - i * r.nest
        max_travel = r.open_w - r.pane_w + r.nest
        travel = _clamp(travel, r.pane_pitch * 0.5, max(r.pane_pitch * 0.5, max_travel))
        model.articulation(
            f"pane_{i}_slide",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=leaf,
            origin=Origin(xyz=(cx, lane_y, r.open_zc - _leaf_body_cz(r))),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=400.0, velocity=0.6, lower=0.0, upper=travel),
            mating=_leaf_mating(child_rail=f"pane_{i}_rail_top", parent_track="head_track"),
        )


def _build_center_biparting(model, r, mats, assets):
    """2 fixed side panes (bays 0,3) + 2 center sliders (door_0/-X, door_1/+X
    Mimic-coupled). Baseline N=4 (src 4panel_center)."""
    frame = model.part("frame")
    _emit_concealed_frame(frame, r, mats)
    # Four bays across the opening; slots 0 and 3 are fixed side panes (rear lane),
    # slots 1 and 2 are the center sliders (forward lanes).
    for slot, prefix in ((0, "fixed_0"), (3, "fixed_1")):
        cx = _pane_center_x_closed(r, slot)
        _emit_fixed_pane(frame, r, mats, assets, cx=cx, cy=_lane_y(r, 0), cz=r.open_zc, prefix=prefix)
    frame.inertial = Inertial.from_geometry(
        Box((r.frame_w, r.frame_d, r.frame_h)),
        mass=80.0,
        origin=Origin(xyz=(0.0, 0.0, r.frame_h / 2.0)),
    )
    meet_reveal = 0.004
    travel = r.pane_pitch - 0.010
    # door_0 fills slot 1, slides -X; door_1 fills slot 2, slides +X (mimic).
    door_0 = model.part("pane_0")
    _build_leaf(door_0, r, mats, assets, leading_sign=1.0, prefix="pane_0")  # handle on +X meeting stile
    cx0 = _pane_center_x_closed(r, 1)
    j0 = model.articulation(
        "pane_0_slide",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=door_0,
        origin=Origin(xyz=(cx0 - meet_reveal, _lane_y(r, 1), r.open_zc - _leaf_body_cz(r))),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=180.0, velocity=0.5, lower=0.0, upper=travel),
        mating=_leaf_mating(child_rail="pane_0_rail_top", parent_track="head_track"),
    )
    door_1 = model.part("pane_1")
    _build_leaf(door_1, r, mats, assets, leading_sign=-1.0, prefix="pane_1")  # handle on -X meeting stile
    cx1 = _pane_center_x_closed(r, 2)
    model.articulation(
        "pane_1_slide",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=door_1,
        origin=Origin(xyz=(cx1 + meet_reveal, _lane_y(r, 2), r.open_zc - _leaf_body_cz(r))),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=180.0, velocity=0.5, lower=0.0, upper=travel),
        mimic=Mimic(joint=j0.name, multiplier=1.0, offset=0.0),
        mating=_leaf_mating(child_rail="pane_1_rail_top", parent_track="head_track"),
    )


def _build_barn(model, r, mats, assets):
    """Exposed barn rail (N=2 bypass): 1 fixed pane + 1 top-hung slider on the
    rail. The single leaf hangs from the rail via roller hangers (src barn_rail)."""
    rail = model.part("barn_rail")
    _emit_barn_rail(rail, r, mats, assets)
    rail_bottom_z = r.frame_h + _RAIL_GAP
    fixed_y = _lane_y(r, 0)
    slider_y = _lane_y(r, 1)
    # Fixed pane (left bay) authored built into the rail root, hanging below.
    # Keep it on the rear lane so the sliding barn leaf can pass on the forward
    # lane instead of occupying the exact same door plane.
    fixed_cx = _pane_center_x_closed(r, 0)
    fixed_cz = rail_bottom_z - _HANGER_H - r.pane_h / 2.0
    _emit_fixed_pane(rail, r, mats, assets, cx=fixed_cx, cy=fixed_y, cz=fixed_cz, prefix="fixed")
    # Fixed-pane hangers bridging the pane top up to the rail bar, so the fixed
    # pane is mechanically tied to the rail island (not a floating sub-island).
    fixed_top_z = fixed_cz + r.pane_h / 2.0
    for k, dx in enumerate((-r.pane_w * 0.3, r.pane_w * 0.3)):
        rail.visual(
            Box((_HANGER_W, _HANGER_T, _HANGER_H + _RAIL_H)),
            origin=Origin(xyz=(fixed_cx + dx, fixed_y, fixed_top_z + (_HANGER_H + _RAIL_H) / 2.0 - 0.004)),
            material=mats["trim"],
            name=f"fixed_hanger_{k}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    rail.inertial = Inertial.from_geometry(
        Box((r.frame_w + 0.20, _RAIL_D, rail_bottom_z + _RAIL_H)),
        mass=60.0,
        origin=Origin(xyz=(0.0, 0.0, (rail_bottom_z + _RAIL_H) / 2.0)),
    )
    # Single sliding leaf (slot 1), authored so its part origin sits on the rail
    # bottom face (joint origin). Leaf body hangs HANGER_H below; rollers on top.
    leaf = model.part("pane_0")
    _build_barn_leaf(leaf, r, mats, assets)
    cx = _pane_center_x_closed(r, 1)
    travel = r.pane_pitch - 0.010
    model.articulation(
        "pane_0_slide",
        ArticulationType.PRISMATIC,
        parent=rail,
        child=leaf,
        origin=Origin(xyz=(cx, slider_y, rail_bottom_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.8, lower=0.0, upper=travel),
        mating=MatingContract(
            parent_face_geometry="rail_bar",
            parent_face_side="negative_z",
            child_face_geometry="pane_0_roller_0",
            child_face_side="positive_z",
            contact_tol=0.012,
        ),
    )


def _build_barn_leaf(part, r, mats, assets):
    """Barn leaf: same glazed leaf, shifted so the part origin is at the rail
    bottom; rollers / hangers on top contacting the rail."""
    half_w = r.pane_w / 2.0
    rail = r.stile
    stile_h = r.pane_h - 2.0 * rail
    glass_w = r.pane_w - 2.0 * r.stile + 0.004
    glass_h = r.pane_h - 2.0 * rail + 0.004
    mid_cz = -(_HANGER_H + r.pane_h / 2.0)
    top_rail_cz = -(_HANGER_H + rail / 2.0)
    bot_rail_cz = -(_HANGER_H + r.pane_h - rail / 2.0)

    part.visual(
        Box((r.pane_w, r.leaf_t, rail)),
        origin=Origin(xyz=(0.0, 0.0, top_rail_cz)),
        material=mats["frame"],
        name="pane_0_rail_top", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    part.visual(
        Box((r.pane_w, r.leaf_t, rail)),
        origin=Origin(xyz=(0.0, 0.0, bot_rail_cz)),
        material=mats["frame"],
        name="pane_0_rail_bottom", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    lead_x = -(half_w - r.stile / 2.0)
    if r.handle == "finger_pocket" and _HAS_CADQUERY:
        part.visual(
            _pocket_stile_mesh(r, assets, name="pane_0_stile_lead"),
            origin=Origin(xyz=(lead_x, 0.0, mid_cz)),
            material=mats["frame"],
            name="pane_0_stile_lead", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    else:
        part.visual(
            Box((r.stile, r.leaf_t, stile_h)),
            origin=Origin(xyz=(lead_x, 0.0, mid_cz)),
            material=mats["frame"],
            name="pane_0_stile_lead", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    part.visual(
        Box((r.stile, r.leaf_t, stile_h)),
        origin=Origin(xyz=(half_w - r.stile / 2.0, 0.0, mid_cz)),
        material=mats["frame"],
        name="pane_0_stile_trail", material_class_id=("metal.aluminum_bare" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    _INFILL_EMITTERS[r.infill](
        part, r, mats, cx=0.0, cy=0.0, cz=mid_cz,
        glass_w=glass_w, glass_h=glass_h, prefix="pane_0",
    )
    face_y = r.leaf_t / 2.0
    handle_x = lead_x + (r.stile / 2.0 - 0.004)
    # handle authored about z=mid_cz: shift emitter output by translating face anchor.
    _emit_barn_handle(part, r, mats, handle_x=handle_x, face_y=face_y, z0=mid_cz)
    # Top carrier strip spanning the leaf width, tying the two roller hangers
    # together. Its top face sits at the part origin (z=0 = joint origin) so the
    # child geometry contains the joint origin (articulation-origin baseline).
    part.visual(
        Box((r.pane_w * 0.7, r.leaf_t, _HANGER_T)),
        origin=Origin(xyz=(0.0, 0.0, -_HANGER_T / 2.0)),
        material=mats["trim"],
        name="pane_0_carrier", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
    )
    # Roller hangers + wheels on top (loop, src barn_rail L242-257).
    hanger_spacing = r.pane_w * 0.6
    roller_mesh = _build_roller_mesh(assets)
    for i, hx in enumerate((-hanger_spacing / 2.0, hanger_spacing / 2.0)):
        part.visual(
            Box((_HANGER_W, _HANGER_T, _HANGER_H)),
            origin=Origin(xyz=(hx, 0.0, -_HANGER_H / 2.0)),
            material=mats["trim"],
            name=f"pane_0_hanger_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
        part.visual(
            roller_mesh,
            origin=Origin(xyz=(hx, 0.0, -_ROLLER_R)),
            material=mats["trim"],
            name=f"pane_0_roller_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    part.inertial = Inertial.from_geometry(
        Box((r.pane_w, r.leaf_t, r.pane_h)),
        mass=18.0,
        origin=Origin(xyz=(0.0, 0.0, mid_cz)),
    )


def _emit_barn_handle(part, r, mats, *, handle_x, face_y, z0):
    """Barn-leaf handle: same emitters but authored about z0 (leaf body center).
    Reuses the leaf handle emitters by temporarily building about origin then
    re-emits with z offset via a thin wrapper (only flush/C/D-loop are proud)."""
    if r.handle == "flush_bar":
        part.visual(
            Box((0.012, 0.016, min(0.30, r.pane_h * 0.4))),
            origin=Origin(xyz=(handle_x, face_y + 0.008, z0)),
            material=mats["handle"],
            name="pane_0_handle_bar", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    elif r.handle == "curved_C_pull":
        handle_h = min(0.21, r.pane_h * 0.32)
        bow_x_out = 0.055
        bow_y_out = 0.030
        anchor_x, anchor_y = handle_x, face_y - 0.012
        grip_x, grip_y = handle_x + bow_x_out, face_y + bow_y_out
        neck_len = math.hypot(grip_x - anchor_x, grip_y - anchor_y) + 0.004
        neck_yaw = math.atan2(grip_y - anchor_y, grip_x - anchor_x)
        for sign, suffix in ((1.0, "neck_top"), (-1.0, "neck_bottom")):
            zc = z0 + sign * (handle_h / 2.0 - 0.022)
            part.visual(
                Cylinder(radius=0.009, length=neck_len),
                origin=Origin(
                    xyz=((anchor_x + grip_x) / 2.0, (anchor_y + grip_y) / 2.0, zc),
                    rpy=(0.0, math.pi / 2.0, neck_yaw),
                ),
                material=mats["handle"],
                name=f"pane_0_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
            )
        part.visual(
            Cylinder(radius=0.011, length=handle_h),
            origin=Origin(xyz=(grip_x, grip_y, z0)),
            material=mats["handle"],
            name="pane_0_grip", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
    elif r.handle == "proud_D_loop":
        grip_len = min(0.26, r.pane_h * 0.4)
        grip_cy = face_y + 0.030 + 0.010
        part.visual(
            Cylinder(radius=0.010, length=grip_len),
            origin=Origin(xyz=(handle_x, grip_cy, z0)),
            material=mats["handle"],
            name="pane_0_grip", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
        )
        neck_cy = face_y + 0.030 / 2.0
        for i, dz in enumerate((grip_len / 2.0 - 0.025, -(grip_len / 2.0 - 0.025))):
            part.visual(
                Cylinder(radius=0.006, length=0.030),
                origin=Origin(xyz=(handle_x, neck_cy, z0 + dz), rpy=(-math.pi / 2.0, 0.0, 0.0)),
                material=mats["handle"],
                name=f"pane_0_neck_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"charcoal_black_alu", "anodized_dark_bronze", "clear_glass_neutral", "tinted_grey_glass", "oak_warm_wood"} else "plastic.opaque_generic"),
            )
    # finger_pocket: nothing proud.


def build_seeded_sliding_door(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_sliding_door(config_from_seed(seed), assets=assets)


def _fixed_pane_prefixes(r: ResolvedSlidingDoorConfig) -> tuple[str, ...]:
    if r.kinematics == "center_biparting":
        return ("fixed_0", "fixed_1")
    return ("fixed",)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_sliding_door_tests(
    object_model: ArticulatedObject,
    config: SlidingDoorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    root_name = "barn_rail" if r.track_style == "exposed_barn" else "frame"
    root = object_model.get_part(root_name)
    slider_names = [f"pane_{i}" for i in range(r.n_sliders)]
    sliders = [object_model.get_part(n) for n in slider_names]
    slides = [object_model.get_articulation(f"pane_{i}_slide") for i in range(r.n_sliders)]

    # ---- Captured engagement allowances (element-scoped). ----
    if r.track_style == "exposed_barn":
        leaf = sliders[0]
        for i in range(2):
            ctx.allow_overlap(
                leaf, root, elem_a=f"pane_0_roller_{i}", elem_b="rail_bar",
                reason="roller wheel rides captured on the rail bottom face.",
            )
        ctx.allow_overlap(
            leaf, root,
            reason="closed barn leaf overlaps the fixed pane / rail hardware in X projection.",
        )
    else:
        for i, leaf in enumerate(sliders):
            ctx.allow_overlap(
                leaf, root, elem_a=f"pane_{i}_rail_top", elem_b="head_track",
                reason="leaf top rail tucks into the head track channel (captured engagement).",
            )
            ctx.allow_overlap(
                leaf, root, elem_a=f"pane_{i}_rail_bottom", elem_b="sill_track",
                reason="leaf bottom rail tucks into the sill track channel (captured engagement).",
            )
            ctx.allow_overlap(
                leaf, root,
                reason="closed leaf overlaps the fixed pane / frame in X projection (meeting interlock).",
            )
        # Telescoping nested leaves overlap each other in X (separate Y lanes).
        if r.kinematics == "telescoping":
            for i in range(1, r.n_sliders):
                ctx.allow_overlap(
                    sliders[i], sliders[i - 1],
                    reason="telescoping leaves interlock / nest in X (separated by Y lanes).",
                )
        elif r.kinematics == "center_biparting":
            ctx.allow_overlap(
                sliders[0], sliders[1],
                reason="bi-parting center leaves meet at the centerline when closed.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Lane separation: leaves may overlap in X projection, never in the
    # exact same Y door plane. This catches fully coincident sliding/fixed panes.
    min_lane_gap = 0.004
    for i, leaf in enumerate(sliders):
        for fixed_prefix in _fixed_pane_prefixes(r):
            ctx.expect_gap(
                leaf,
                root,
                axis="y",
                min_gap=min_lane_gap,
                positive_elem=f"pane_{i}_rail_top",
                negative_elem=f"{fixed_prefix}_rail_top",
                name=f"pane_{i} is offset in Y from {fixed_prefix}",
            )
    for upper_i in range(1, len(sliders)):
        for lower_i in range(upper_i):
            ctx.expect_gap(
                sliders[upper_i],
                sliders[lower_i],
                axis="y",
                min_gap=min_lane_gap,
                positive_elem=f"pane_{upper_i}_rail_top",
                negative_elem=f"pane_{lower_i}_rail_top",
                name=f"pane_{upper_i} is offset in Y from pane_{lower_i}",
            )

    # ---- Single static root. ----
    roots = object_model.root_parts()
    ctx.check(
        "single static root carries the door",
        len(roots) == 1 and roots[0].name == root_name,
        details=f"roots={[p.name for p in roots]}",
    )

    # ---- N sliders present, all PRISMATIC along X. ----
    ctx.check(
        "expected number of sliding leaves present",
        all(s is not None for s in sliders) and len(sliders) == r.n_sliders,
        details=f"sliders={slider_names} n_sliders={r.n_sliders}",
    )
    for i, j in enumerate(slides):
        ctx.check(
            f"pane_{i}_slide is PRISMATIC along X",
            j.articulation_type == ArticulationType.PRISMATIC
            and abs(j.axis[0]) > 0.99
            and j.motion_limits.upper > 0.0,
            details=f"type={j.articulation_type} axis={tuple(j.axis)} upper={j.motion_limits.upper}",
        )

    # ---- Kinematics-specific topology. ----
    if r.kinematics == "center_biparting":
        j0 = object_model.get_articulation("pane_0_slide")
        j1 = object_model.get_articulation("pane_1_slide")
        ctx.check(
            "center-biparting has opposite-axis mimic-coupled sliders",
            j0.axis[0] * j1.axis[0] < 0 and j1.mimic is not None,
            details=f"a0={tuple(j0.axis)} a1={tuple(j1.axis)} mimic={j1.mimic}",
        )
    elif r.kinematics == "bypass":
        ctx.check(
            "bypass has exactly one slider (N=2)",
            r.n_sliders == 1 and r.panel_count == 2,
            details=f"n_sliders={r.n_sliders} N={r.panel_count}",
        )

    # ---- Infill present on each leaf (Rule 1 inline visuals; Rule 3 primitives). ----
    for i, leaf in enumerate(sliders):
        names = {v.name for v in leaf.visuals}
        if r.infill == "full_glass":
            ok = f"pane_{i}_glass" in names
        elif r.infill == "muntin_grid":
            ok = sum(1 for n in names if n.startswith(f"pane_{i}_lite_")) == _MUNTIN_COLS * _MUNTIN_ROWS
        elif r.infill == "raised_panel":
            ok = f"pane_{i}_center" in names
        else:  # slatted_louver
            ok = sum(1 for n in names if n.startswith(f"pane_{i}_slat_")) >= 2
        ctx.check(
            f"pane_{i} carries {r.infill} infill",
            ok,
            details=f"visuals={sorted(names)}",
        )

    # ---- Glass transparency (glazed infills). ----
    if r.infill in ("full_glass", "muntin_grid"):
        gmat = next((m for m in object_model.materials if m.name.startswith("sliding_door_glass")), None)
        alpha = gmat.rgba[3] if gmat is not None and gmat.rgba else 1.0
        ctx.check(
            "glass material is transparent (alpha < 0.5)",
            gmat is not None and alpha < 0.5,
            details=f"glass alpha={alpha}",
        )

    # ---- Handle topology (proud handles present; finger_pocket has none). ----
    lead = sliders[0]
    lead_names = {v.name for v in lead.visuals}
    if r.handle == "flush_bar":
        ctx.check("flush bar handle present", "pane_0_handle_bar" in lead_names, details=str(sorted(lead_names)))
    elif r.handle == "curved_C_pull":
        ctx.check("curved C-pull grip present", "pane_0_grip" in lead_names, details=str(sorted(lead_names)))
    elif r.handle == "proud_D_loop":
        ctx.check(
            "D-loop grip + necks present",
            "pane_0_grip" in lead_names and "pane_0_neck_0" in lead_names,
            details=str(sorted(lead_names)),
        )
    else:  # finger_pocket
        ctx.check(
            "finger pocket has no proud handle (flush mesh stile)",
            "pane_0_handle_bar" not in lead_names and "pane_0_grip" not in lead_names
            and "pane_0_stile_lead" in lead_names,
            details=str(sorted(lead_names)),
        )

    # ---- Door stands on the ground. ----
    aabb = ctx.part_world_aabb(root)
    if aabb is not None:
        ctx.check(
            "door rests on the ground (z_min near 0)",
            aabb[0][2] < 0.03,
            details=f"z_min={aabb[0][2]:.4f}",
        )

    # ---- Each slider actually opens toward its axis direction. ----
    # Mimic-driven joints (center-biparting follower) cannot be posed directly;
    # drive the source joint instead and observe the follower's induced motion.
    for i, (leaf, j) in enumerate(zip(sliders, slides)):
        drive = j
        if j.mimic is not None:
            drive = object_model.get_articulation(j.mimic.joint)
        rest = ctx.part_world_position(leaf)
        with ctx.pose({drive: drive.motion_limits.upper}):
            opened = ctx.part_world_position(leaf)
        if rest is not None and opened is not None:
            sign = -1.0 if j.axis[0] < 0 else 1.0
            moved = (opened[0] - rest[0]) * sign
            ctx.check(
                f"pane_{i} slides open along its axis",
                moved > 0.10,
                details=f"rest_x={rest[0]:.3f} open_x={opened[0]:.3f} sign={sign}",
            )

    # ---- Telescoping nest stays engaged at full open. ----
    if r.kinematics == "telescoping" and r.n_sliders >= 2:
        open_pose = {j: j.motion_limits.upper for j in slides}
        with ctx.pose(open_pose):
            for i in range(1, r.n_sliders):
                ctx.expect_overlap(
                    sliders[i], sliders[i - 1],
                    axes="x",
                    min_overlap=r.nest - 0.020,
                    name=f"pane_{i} stays nested with pane_{i-1} when fully open",
                )

    # ---- Inequality: lane stack fits in the frame depth. ----
    n_lanes = max(2, r.panel_count)
    lane_depth = (n_lanes - 1) * r.lane_gap + 2.0 * r.leaf_t
    ctx.check(
        "lane stack fits inside the frame depth",
        lane_depth <= r.frame_d + 1e-6,
        details=f"lane_depth={lane_depth:.4f} frame_d={r.frame_d:.4f}",
    )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded with panel_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "SlidingDoorConfig",
    "ResolvedSlidingDoorConfig",
    "build_sliding_door",
    "build_seeded_sliding_door",
    "config_from_seed",
    "resolve_config",
    "run_sliding_door_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
