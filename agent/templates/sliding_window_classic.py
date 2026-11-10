# SPDX-License-Identifier: Apache-2.0

"""Architectural horizontal sliding window (classic) modular template.

Built from the 54-record curated DATASET pool (``category_slug=sliding_window``,
``rec_sliding_window_0001..0005`` + ``rec_sliding_window_<hex>``) per the reviewed
modular spec ``articraft_template_authoring/specs_modular_v1/sliding_window_classic.md``.

Identity: a static ``frame`` root (perimeter jamb/head/sill ring + dual/triple
track channels + lips) holds at least one glazed sash. One sash slides
horizontally on a **PRISMATIC** rail (category-defining motion, axis (+/-1,0,0)),
optionally paired with a fixed lite (separate FIXED part or baked into the frame).
The pool is empirically **horizontal-only**, single sliding sash, sash_count in
{1,2} — there are no vertical double-hung, no 2-sliding-sash sources, so the
joint diversity comes from fixed_glazing topology (Slot A) + lock articulation
(Slot C), not from orientation/sash-count, per the spec's downgrade note.

Pattern = mixed (parallel_children + a light multiplicity axis):

  * Slot A ``fixed_glazing_topology`` (3): separate_fixed_part (3-link tree:
    frame + fixed_lite FIXED + sliding_sash PRISMATIC) / baked_into_frame
    (2-link tree: fixed glass baked as frame visuals + sliding_sash PRISMATIC) /
    sash_only_no_fixed (sash fills the bay, no fixed lite).
  * Slot B ``track_carriage_style`` (4): lipped_dual_channel / roller_truck_
    cylinders (Cylinder rollers on a steel track) / triple_rib_guide (3 ribs via
    for-loop) / cadquery_hollow_channel (slab.cut frame shell + drain slots).
  * Slot C ``lock_articulation`` (4): none_passive_visual (no joint) /
    thumbturn_revolute (REVOLUTE axis (0,1,0)) / crescent_cam_revolute
    (REVOLUTE axis (0,1,0)) / lockout_pin_prismatic (PRISMATIC axis (0,0,1)).
  * Slot D ``handle_style`` (5): pull_bar / flush_recess / finger_pull /
    molded_grip_ribs (for-loop N ribs) / d_pull_plate — parent visual on the
    sliding sash (moves with the sash, no independent joint, Rule 1).
  * light multiplicity: ``meeting_muntin_count`` in [0,2] -> ``muntin_{i}``
    for-loop on the sliding sash; ``open_direction`` left/right/bidirectional.

All glide/roller/top-guide/muntin/fastener hardware is for-loop emitted. Hinge
pins / slide rails / lock-pin shafts are captured geometry, so those joints omit
``MatingContract`` (grandfathered) and are guarded by the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests block).
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

FixedGlazing = Literal["separate_fixed_part", "baked_into_frame", "sash_only_no_fixed"]
TrackCarriage = Literal[
    "lipped_dual_channel",
    "roller_truck_cylinders",
    "triple_rib_guide",
    "cadquery_hollow_channel",
]
LockArticulation = Literal[
    "none_passive_visual",
    "thumbturn_revolute",
    "crescent_cam_revolute",
    "lockout_pin_prismatic",
]
HandleStyle = Literal[
    "pull_bar",
    "flush_recess",
    "finger_pull",
    "molded_grip_ribs",
    "d_pull_plate",
]
OpenDirection = Literal["left_negative_x", "right_positive_x", "bidirectional_center"]
PaletteStyle = Literal[
    "silver_aluminum",
    "white_vinyl",
    "dark_anodized_graphite",
    "charcoal_black_powder",
    "industrial_safety",
    "field_service_bronze",
]

FIXED_GLAZINGS: tuple[FixedGlazing, ...] = (
    "separate_fixed_part",
    "baked_into_frame",
    "sash_only_no_fixed",
)
TRACK_CARRIAGES: tuple[TrackCarriage, ...] = (
    "lipped_dual_channel",
    "roller_truck_cylinders",
    "triple_rib_guide",
    "cadquery_hollow_channel",
)
LOCK_ARTICULATIONS: tuple[LockArticulation, ...] = (
    "none_passive_visual",
    "thumbturn_revolute",
    "crescent_cam_revolute",
    "lockout_pin_prismatic",
)
HANDLE_STYLES: tuple[HandleStyle, ...] = (
    "pull_bar",
    "flush_recess",
    "finger_pull",
    "molded_grip_ribs",
    "d_pull_plate",
)
OPEN_DIRECTIONS: tuple[OpenDirection, ...] = (
    "left_negative_x",
    "right_positive_x",
    "bidirectional_center",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "silver_aluminum",
    "white_vinyl",
    "dark_anodized_graphite",
    "charcoal_black_powder",
    "industrial_safety",
    "field_service_bronze",
)

# Lock articulations that need a fixed/meeting stile to anchor the keeper into;
# in sash_only the keeper relocates to the frame jamb (still legal).
N_MUNTIN_MIN = 0
N_MUNTIN_MAX = 2
MUNTIN_WEIGHTS = (0.55, 0.32, 0.13)  # 0 / 1 / 2 (spec §8: 0-1 high, 2 rare)
GRIP_RIB_MIN = 2
GRIP_RIB_MAX = 5

# ---------------------------------------------------------------------------
# Palette (6 colorways, all observed in the curated pool; spec §palette).
# Keys: frame / sash / glass(rgba w/ alpha) / hardware(dark) / accent / seal.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "silver_aluminum": {
        "frame": (0.78, 0.80, 0.82, 1.0),
        "sash": (0.66, 0.68, 0.70, 1.0),
        "glass": (0.71, 0.82, 0.88, 0.30),
        "hardware": (0.24, 0.25, 0.27, 1.0),
        "accent": (0.72, 0.74, 0.77, 1.0),
        "seal": (0.10, 0.10, 0.11, 1.0),
    },
    "white_vinyl": {
        "frame": (0.92, 0.90, 0.84, 1.0),
        "sash": (0.94, 0.93, 0.90, 1.0),
        "glass": (0.67, 0.80, 0.87, 0.34),
        "hardware": (0.30, 0.31, 0.33, 1.0),
        "accent": (0.78, 0.78, 0.76, 1.0),
        "seal": (0.10, 0.11, 0.12, 1.0),
    },
    "dark_anodized_graphite": {
        "frame": (0.20, 0.22, 0.22, 1.0),
        "sash": (0.31, 0.35, 0.33, 1.0),
        "glass": (0.56, 0.66, 0.72, 0.36),
        "hardware": (0.72, 0.74, 0.77, 1.0),
        "accent": (0.40, 0.42, 0.42, 1.0),
        "seal": (0.09, 0.09, 0.10, 1.0),
    },
    "charcoal_black_powder": {
        "frame": (0.10, 0.12, 0.11, 1.0),
        "sash": (0.16, 0.17, 0.18, 1.0),
        "glass": (0.40, 0.43, 0.46, 0.45),
        "hardware": (0.14, 0.14, 0.14, 1.0),
        "accent": (0.34, 0.35, 0.36, 1.0),
        "seal": (0.05, 0.05, 0.05, 1.0),
    },
    "industrial_safety": {
        "frame": (0.28, 0.31, 0.34, 1.0),
        "sash": (0.23, 0.25, 0.25, 1.0),
        "glass": (0.74, 0.78, 0.74, 0.32),
        "hardware": (0.86, 0.74, 0.10, 1.0),  # safety yellow
        "accent": (0.78, 0.14, 0.10, 1.0),  # lockout red
        "seal": (0.08, 0.08, 0.09, 1.0),
    },
    "field_service_bronze": {
        "frame": (0.16, 0.13, 0.10, 1.0),
        "sash": (0.20, 0.16, 0.12, 1.0),
        "glass": (0.60, 0.68, 0.72, 0.34),
        "hardware": (0.74, 0.16, 0.12, 1.0),  # red handle
        "accent": (0.86, 0.78, 0.20, 1.0),  # yellow PTFE shoe
        "seal": (0.07, 0.06, 0.05, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters); from rec_sliding_window_0004 frame +
# _build_sash factory. +Z up, width along X, glass face in X-Z, sill at bottom.
# ---------------------------------------------------------------------------
_FRAME_W = 1.24
_FRAME_H = 0.82
_FRAME_D = 0.11
_JAMB_W = 0.06
_HEAD_H = 0.06
_SILL_H = 0.06

_SASH_D = 0.034
_TRACK_Y = 0.030  # front/rear runner Y offset
_RUNNER_W = 0.014
_RUNNER_H = 0.012
_LIP_H = 0.028

_OUTER_STILE_W = 0.050
_MEETING_STILE_W = 0.064
_RAIL_H = 0.050


@dataclass(frozen=True)
class SlidingWindowClassicConfig:
    fixed_glazing_topology: FixedGlazing | None = None
    track_carriage_style: TrackCarriage | None = None
    lock_articulation: LockArticulation | None = None
    handle_style: HandleStyle | None = None
    open_direction: OpenDirection | None = None
    meeting_muntin_count: int | None = None
    grip_rib_count: int | None = None
    palette_style: PaletteStyle = "silver_aluminum"
    win_width_scale: float = 1.0
    win_height_scale: float = 1.0
    frame_depth_scale: float = 1.0
    sash_open_frac: float = 0.0
    name: str = "sliding_window_classic"


@dataclass(frozen=True)
class ResolvedSlidingWindowClassicConfig:
    fixed_glazing_topology: FixedGlazing
    track_carriage_style: TrackCarriage
    lock_articulation: LockArticulation
    handle_style: HandleStyle
    open_direction: OpenDirection
    meeting_muntin_count: int
    grip_rib_count: int
    palette_style: PaletteStyle
    sash_count: int
    # Concrete geometry (scaled).
    frame_w: float
    frame_h: float
    frame_d: float
    jamb_w: float
    head_h: float
    sill_h: float
    open_w: float
    open_h: float
    sash_w: float
    sash_h: float
    sash_d: float
    track_y: float
    sash_closed_x: float
    fixed_x: float
    sliding_travel: float
    sash_open_frac: float
    open_sign: float  # -1 left, +1 right, 0 bidirectional
    runner_z: float  # sill-runner rib world Z (joint origin sits here, real hardware)
    sash_z_off: float  # part-frame Z that places the sash center at open_cz
    open_bot: float  # clear opening bottom (= solid sill top)
    open_top: float  # clear opening top (= solid head bottom)
    open_cz: float  # clear opening center Z (sash body centered here)
    body_clear: float  # gap between sash body top/bottom and solid head/sill
    shoe_protrusion: float  # how far the guide shoe sticks past the sash body
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> SlidingWindowClassicConfig:
    rng = random.Random(seed)
    return SlidingWindowClassicConfig(
        fixed_glazing_topology=rng.choice(FIXED_GLAZINGS),
        track_carriage_style=rng.choice(TRACK_CARRIAGES),
        lock_articulation=rng.choice(LOCK_ARTICULATIONS),
        handle_style=rng.choice(HANDLE_STYLES),
        open_direction=rng.choice(OPEN_DIRECTIONS),
        meeting_muntin_count=rng.choices((0, 1, 2), weights=MUNTIN_WEIGHTS, k=1)[0],
        grip_rib_count=rng.randint(GRIP_RIB_MIN, GRIP_RIB_MAX),
        palette_style=rng.choice(PALETTE_STYLES),
        win_width_scale=round(rng.uniform(0.55, 1.30), 4),
        win_height_scale=round(rng.uniform(0.80, 1.30), 4),
        frame_depth_scale=round(rng.uniform(0.85, 1.20), 4),
        sash_open_frac=round(rng.uniform(0.0, 1.0), 4),
        name=f"seeded_sliding_window_classic_{seed}",
    )


def resolve_config(
    config: SlidingWindowClassicConfig | None = None,
) -> ResolvedSlidingWindowClassicConfig:
    cfg = config or SlidingWindowClassicConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    fixed_glazing = _pick(cfg.fixed_glazing_topology, FIXED_GLAZINGS)
    track = _pick(cfg.track_carriage_style, TRACK_CARRIAGES)
    lock = _pick(cfg.lock_articulation, LOCK_ARTICULATIONS)
    handle = _pick(cfg.handle_style, HANDLE_STYLES)
    open_dir = _pick(cfg.open_direction, OPEN_DIRECTIONS)

    # --- Multiplicity / conditional axes ---
    muntin_n = int(cfg.meeting_muntin_count) if cfg.meeting_muntin_count is not None else 0
    muntin_n = int(_clamp(muntin_n, N_MUNTIN_MIN, N_MUNTIN_MAX))
    grip_n = int(cfg.grip_rib_count) if cfg.grip_rib_count is not None else 3
    grip_n = int(_clamp(grip_n, GRIP_RIB_MIN, GRIP_RIB_MAX))

    # sash_count derived from topology (conditional, not free).
    sash_count = 1 if fixed_glazing == "sash_only_no_fixed" else 2

    # --- Continuous scale (clamp) ---
    w_scale = _clamp(cfg.win_width_scale, 0.55, 1.30)
    h_scale = _clamp(cfg.win_height_scale, 0.80, 1.30)
    d_scale = _clamp(cfg.frame_depth_scale, 0.85, 1.20)
    open_frac = _clamp(cfg.sash_open_frac, 0.0, 1.0)

    frame_w = _FRAME_W * w_scale
    frame_h = _FRAME_H * h_scale
    frame_d = _FRAME_D * d_scale
    jamb_w = _JAMB_W * min(1.0, w_scale * 1.15)
    head_h = _HEAD_H * min(1.0, h_scale * 1.15)
    sill_h = _SILL_H * min(1.0, h_scale * 1.15)

    open_w = frame_w - 2.0 * jamb_w
    open_h = frame_h - head_h - sill_h

    track_y = min(_TRACK_Y, frame_d * 0.30)

    # --- Sash sizing (equation, spec §params) ---
    sash_clear = 0.006
    meeting_overlap = 0.030
    if sash_count == 1:
        # sash fills the bay.
        sash_w = open_w - 2.0 * sash_clear
    else:
        sash_w = (open_w - meeting_overlap) / 2.0
    sash_w = max(sash_w, 0.18)

    # ---- Vertical (Z) channel layout (ref_service_slider_window.py pattern) ----
    # Solid head/sill occupy ONLY the Z bands above/below the clear opening.
    # Frame is centered at z=0, so the clear opening band is:
    open_bot = -frame_h / 2.0 + sill_h  # = sill solid top
    open_top = frame_h / 2.0 - head_h  # = head solid bottom
    open_cz = 0.5 * (open_bot + open_top)  # opening center (sash rides here)
    open_clear_h = open_top - open_bot  # == open_h

    # The sash BODY sits strictly inside the opening with a real top+bottom gap;
    # only a thin GUIDE SHOE protrudes past the body into the gap, riding on a
    # thin full-width guide rib. The shoe far edge stays within [open_bot, open_top]
    # so it never enters the solid head/sill block.
    body_clear = max(0.014, open_clear_h * 0.04)  # gap between sash body and solid
    shoe_protrusion = min(0.010, body_clear * 0.6)  # shoe sticks into the gap
    sash_h = open_clear_h - 2.0 * body_clear
    sash_h = max(sash_h, 0.20)
    sash_d = _SASH_D

    # PRISMATIC travel = net clear opening width the sash can move.
    if sash_count == 1:
        sliding_travel = open_w - sash_w - 2.0 * sash_clear
    else:
        sliding_travel = open_w - sash_w - sash_clear
    sliding_travel = max(sliding_travel, 0.05)

    # The sash CENTER can range over [-c, +c] inside the bay (c = half the slack)
    # so the sash never rams a jamb. Derive closed-pose X + travel from this so
    # the body stays within the opening across the FULL prismatic travel.
    c = max(0.0, (open_w - sash_w) / 2.0)

    if open_dir == "left_negative_x":
        open_sign = -1.0
    elif open_dir == "right_positive_x":
        open_sign = 1.0
    else:
        open_sign = 0.0

    if sash_count == 2:
        # Bidirectional center-park is not physical for a sash that starts flush
        # at a jamb beside a fixed lite -> degrade to single-direction toward the
        # fixed lite. The moving sash closes at one jamb (center = +c by default,
        # mirror for right-open) and opens across the bay over the fixed lite.
        fixed_x = -(open_w / 2.0) + (sash_w / 2.0)
        if open_sign > 0.0:
            sash_closed_x = -c
            fixed_x = -fixed_x
        else:
            sash_closed_x = c
        # full slack travel toward the opposite jamb (over the fixed lite lane).
        sliding_travel = min(sliding_travel, 2.0 * c) if c > 0 else sliding_travel
        sliding_travel = max(sliding_travel, 0.05)
    else:
        # sash_only: the sash nearly fills the bay; only a small slack travel.
        fixed_x = 0.0
        if open_dir == "bidirectional_center":
            sash_closed_x = 0.0  # parked centered, opens both ways within the bay
        elif open_sign > 0.0:
            sash_closed_x = -c
        else:
            sash_closed_x = c
        sliding_travel = min(sliding_travel, 2.0 * c) if c > 0 else sliding_travel
        sliding_travel = max(sliding_travel, 0.03)

    # The sliding-sash / fixed-lite PRISMATIC/FIXED joint origins anchor at the
    # sash BOTTOM RAIL bottom edge, which is full-OPENING-WIDTH continuous
    # geometry (so the origin is never in an x-gap between shoes) AND overlaps the
    # sill guide rib top (real frame hardware inside the clear opening, NOT the
    # solid sill). The sash is authored with its center at part-frame z =
    # sash_z_off so its center lands at the opening center (open_cz) while the
    # part-frame origin == the joint origin.
    body_bottom = open_cz - (open_clear_h - 2.0 * body_clear) / 2.0  # = open_bot + body_clear
    runner_z = body_bottom - 0.004  # 4 mm up inside the bottom rail / rib overlap
    sash_z_off = open_cz - runner_z

    return ResolvedSlidingWindowClassicConfig(
        fixed_glazing_topology=fixed_glazing,
        track_carriage_style=track,
        lock_articulation=lock,
        handle_style=handle,
        open_direction=open_dir,
        meeting_muntin_count=muntin_n,
        grip_rib_count=grip_n,
        palette_style=palette_style,
        sash_count=sash_count,
        frame_w=frame_w,
        frame_h=frame_h,
        frame_d=frame_d,
        jamb_w=jamb_w,
        head_h=head_h,
        sill_h=sill_h,
        open_w=open_w,
        open_h=open_h,
        sash_w=sash_w,
        sash_h=sash_h,
        sash_d=sash_d,
        track_y=track_y,
        sash_closed_x=sash_closed_x,
        fixed_x=fixed_x,
        sliding_travel=sliding_travel,
        sash_open_frac=open_frac,
        open_sign=open_sign,
        runner_z=runner_z,
        sash_z_off=sash_z_off,
        open_bot=open_bot,
        open_top=open_top,
        open_cz=open_cz,
        body_clear=body_clear,
        shoe_protrusion=shoe_protrusion,
        name=cfg.name or "sliding_window_classic",
    )


def with_overrides(
    config: SlidingWindowClassicConfig, **kwargs: object
) -> SlidingWindowClassicConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SlidingWindowClassicConfig | ResolvedSlidingWindowClassicConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedSlidingWindowClassicConfig)
        else resolve_config(config)
    )
    return (
        ("fixed_glazing_topology", r.fixed_glazing_topology),
        ("track_carriage_style", r.track_carriage_style),
        ("lock_articulation", r.lock_articulation),
        ("handle_style", r.handle_style),
        ("open_direction", r.open_direction),
        ("sash_count", f"n{r.sash_count}"),
        ("meeting_muntin_count", f"n{r.meeting_muntin_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Track / carriage hardware (Slot B). Emitted onto the frame; the per-sash
# glide/roller is emitted in the sash builder. Runner Z lines are shared.
# ---------------------------------------------------------------------------
def _runner_z(r: ResolvedSlidingWindowClassicConfig) -> tuple[float, float]:
    """(sill runner rib z, head guide rib z) — thin ribs just INSIDE the clear
    opening band [open_bot, open_top], never inside the solid head/sill block."""
    runner_z = r.open_bot + _RUNNER_H / 2.0
    guide_z = r.open_top - _RUNNER_H / 2.0
    return runner_z, guide_z


def _emit_shoe_ribs(frame, r, mats) -> None:
    """Full-OPENING-WIDTH guide ribs in the clearance gap at the FRONT/REAR sash
    lanes (ref_service_slider_window.py). They stand UP from the opening bottom
    edge / DOWN from the opening top edge into the gap so the sash glide SHOE
    rides them with CONSTANT overlap at every slide position — and they never
    enter the solid head/sill (rib top stays at the sash-body level). The joint
    origin anchors on ``front_runner`` (real hardware at runner_z)."""
    run_w = r.open_w
    rib_d = 0.016
    # Sill rib spans [open_bot, open_bot + body_clear]; head rib mirror at top.
    sill_rib_h = r.body_clear
    sill_rib_cz = r.open_bot + sill_rib_h / 2.0
    head_rib_cz = r.open_top - sill_rib_h / 2.0
    for y, prefix in ((-r.track_y, "rear"), (r.track_y, "front")):
        frame.visual(
            Box((run_w, rib_d, sill_rib_h)),
            origin=Origin(xyz=(0.0, y, sill_rib_cz)),
            material=mats["accent"],
            name=f"{prefix}_runner", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
        )
        frame.visual(
            Box((run_w, rib_d, sill_rib_h)),
            origin=Origin(xyz=(0.0, y, head_rib_cz)),
            material=mats["accent"],
            name=f"{prefix}_head_guide", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
        )


def _emit_track_lipped_dual(frame, r, mats) -> None:
    """lipped_dual_channel (0004 L334-370): box runners + sill/head lips.

    The runners run the full open width along the front/rear track lanes; the
    lips ride directly on the runners (overlapping them in Z) so they read as
    the raised channel walls and stay connected to the part (no islands)."""
    runner_z, guide_z = _runner_z(r)
    run_w = r.open_w
    # One continuous sill/head bed spanning the full track depth, so all three
    # lips (front / center / rear) ride on a shared bed (no islands).
    bed_d = 2.0 * r.track_y + 0.040
    for bed_z, prefix in ((runner_z, "sill"), (guide_z, "head")):
        frame.visual(
            Box((run_w, bed_d, _RUNNER_H)),
            origin=Origin(xyz=(0.0, 0.0, bed_z)),
            material=mats["seal"],
            name=f"{prefix}_bed", material_class_id="rubber.smooth_plain",
        )
    # Full-width guide ribs the sash shoe rides on (constant overlap, in the gap).
    _emit_shoe_ribs(frame, r, mats)
    # Three lips per rail bed: the two outer walls + a center divider between
    # the front/rear lanes. Each lip's bottom overlaps its runner bed (z band).
    lip_w = r.open_w - 0.04
    for runner_bed_z, prefix in ((runner_z, "sill"), (guide_z, "head")):
        if prefix == "sill":
            lip_z = runner_bed_z + _LIP_H / 2.0 - 0.004
        else:
            lip_z = runner_bed_z - _LIP_H / 2.0 + 0.004
        for y_off, lname in (
            (r.track_y + 0.012, "front_outer_lip"),
            (0.0, "center_lip"),
            (-r.track_y - 0.012, "rear_outer_lip"),
        ):
            frame.visual(
                Box((lip_w, 0.008, _LIP_H)),
                origin=Origin(xyz=(0.0, y_off, lip_z)),
                material=mats["frame"],
                name=f"{prefix}_{lname}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
            )


def _emit_track_roller_truck(frame, r, mats) -> None:
    """roller_truck_cylinders (7404a1 L37-50): steel track beds + runners.
    The Cylinder rollers themselves live on the sash."""
    runner_z, guide_z = _runner_z(r)
    run_w = r.open_w
    bed_d = 2.0 * r.track_y + 0.040
    # Continuous sill/head beds (shared support for the steel tracks + lips).
    frame.visual(
        Box((run_w, bed_d, 0.016)),
        origin=Origin(xyz=(0.0, 0.0, runner_z - 0.002)),
        material=mats["frame"],
        name="sill_bed", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Box((run_w, bed_d, _RUNNER_H)),
        origin=Origin(xyz=(0.0, 0.0, guide_z)),
        material=mats["frame"],
        name="head_bed", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    # Steel roller track strips (decorative) on the bed at each lane.
    for y, prefix in ((-r.track_y, "rear"), (r.track_y, "front")):
        frame.visual(
            Box((run_w, 0.012, 0.010)),
            origin=Origin(xyz=(0.0, y, runner_z + 0.008)),
            material=mats["seal"],
            name=f"{prefix}_roller_track", material_class_id="metal.steel_bare",
        )
    # Full-width guide ribs the roller/shoe rides on (constant overlap, in the gap).
    _emit_shoe_ribs(frame, r, mats)
    # A center divider lip on the sill bed so the slide path reads legible.
    frame.visual(
        Box((run_w, 0.010, _LIP_H)),
        origin=Origin(xyz=(0.0, 0.0, runner_z + _LIP_H / 2.0)),
        material=mats["seal"],
        name="sill_center_lip", material_class_id="rubber.smooth_plain",
    )
    frame.visual(
        Box((run_w, 0.010, _LIP_H)),
        origin=Origin(xyz=(0.0, 0.0, guide_z - _LIP_H / 2.0)),
        material=mats["seal"],
        name="head_center_lip", material_class_id="rubber.smooth_plain",
    )


def _emit_track_triple_rib(frame, r, mats) -> None:
    """triple_rib_guide (f0621fda L67-95): back/separator/front 3 ribs, loop."""
    runner_z, guide_z = _runner_z(r)
    run_w = r.open_w
    rib_h = 0.012
    bed_d = 2.0 * r.track_y + 0.040
    # Continuous sill/head beds the 3 ribs all sit on (shared support -> no islands).
    for bed_z, prefix in ((runner_z, "sill"), (guide_z, "head")):
        frame.visual(
            Box((run_w, bed_d, _RUNNER_H)),
            origin=Origin(xyz=(0.0, 0.0, bed_z)),
            material=mats["frame"],
            name=f"{prefix}_bed", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
        )
    for y_center, rname in ((-r.track_y, "back"), (0.0, "separator"), (r.track_y, "front")):
        frame.visual(
            Box((run_w, 0.010, rib_h)),
            origin=Origin(xyz=(0.0, y_center, runner_z + rib_h / 2.0)),
            material=mats["seal"],
            name=f"sill_{rname}_guide", material_class_id="rubber.smooth_plain",
        )
        frame.visual(
            Box((run_w, 0.010, rib_h)),
            origin=Origin(xyz=(0.0, y_center, guide_z - rib_h / 2.0)),
            material=mats["seal"],
            name=f"head_{rname}_guide", material_class_id="rubber.smooth_plain",
        )
    # Full-width guide ribs the sash shoe rides on (constant overlap, in the gap).
    _emit_shoe_ribs(frame, r, mats)


def _emit_track_cadquery_hollow(frame, r, mats, *, assets) -> None:
    """cadquery_hollow_channel (645606): a slab cut with two track grooves +
    drain slots (boolean). segments kept default/low to avoid degeneracy."""
    runner_z, guide_z = _runner_z(r)
    run_w = r.open_w
    slab_d = max(0.030, r.track_y * 2.0 + 0.040)
    slab = cq.Workplane("XY").box(run_w, slab_d, _LIP_H)
    # Two longitudinal grooves (front / rear track) — cut from the TOP only,
    # leaving a connecting floor so the slab stays a single solid (no islands).
    groove_h = _LIP_H * 0.55
    for y in (-r.track_y, r.track_y):
        groove = cq.Workplane("XY", origin=(0.0, y, _LIP_H / 2.0 - groove_h / 2.0)).box(
            run_w + 0.01, 0.016, groove_h
        )
        slab = slab.cut(groove)
    # Drain notches along the front edge (loop) — shallow top notches, stay connected.
    n_drains = 4
    for i in range(n_drains):
        x = -run_w / 2.0 + (i + 0.5) * run_w / n_drains
        drain = cq.Workplane("XY", origin=(x, slab_d / 2.0, _LIP_H / 2.0 - 0.005)).box(
            0.030, 0.012, 0.014
        )
        slab = slab.cut(drain)
    sill_mesh = mesh_from_cadquery(slab, "cadquery_sill_channel", assets=assets)
    frame.visual(
        sill_mesh,
        # Sit the channel fully inside the opening (bottom at open_bot), never
        # dipping into the solid sill.
        origin=Origin(xyz=(0.0, 0.0, r.open_bot + _LIP_H / 2.0)),
        material=mats["frame"],
        name="cq_sill_channel", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    # Mirror a simpler grooved head channel (no drains), grooves from the bottom.
    head_slab = cq.Workplane("XY").box(run_w, slab_d, _LIP_H)
    for y in (-r.track_y, r.track_y):
        groove = cq.Workplane("XY", origin=(0.0, y, -_LIP_H / 2.0 + groove_h / 2.0)).box(
            run_w + 0.01, 0.016, groove_h
        )
        head_slab = head_slab.cut(groove)
    head_mesh = mesh_from_cadquery(head_slab, "cadquery_head_channel", assets=assets)
    frame.visual(
        head_mesh,
        # Sit the head channel fully inside the opening (top at open_top).
        origin=Origin(xyz=(0.0, 0.0, r.open_top - _LIP_H / 2.0)),
        material=mats["frame"],
        name="cq_head_channel", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    # Full-width guide ribs the sash shoe rides on (constant overlap, in the gap).
    _emit_shoe_ribs(frame, r, mats)


_TRACK_BUILDERS = {
    "lipped_dual_channel": _emit_track_lipped_dual,
    "roller_truck_cylinders": _emit_track_roller_truck,
    "triple_rib_guide": _emit_track_triple_rib,
    "cadquery_hollow_channel": _emit_track_cadquery_hollow,
}


# ---------------------------------------------------------------------------
# Shared glazed-sash factory (multiplicity §1 母体, 0004 _build_sash L90-263).
# Builds stiles + rails + glass + gasket + interlock fin + glide/roller carriage
# (Slot B) for either the fixed lite or the sliding sash. Authored centered on
# the sash center (x=y=z=0); the joint origin positions it.
# ---------------------------------------------------------------------------
def _emit_sash_carriage(part, r, mats, *, track_y_sign: float) -> None:
    """Per-sash bottom GLIDE SHOE + top GUIDE carriage (Slot B), for-loop emitted.

    Ref pattern (ref_service_slider_window.py): the shoe protrudes only
    ``r.shoe_protrusion`` PAST the sash body into the clearance gap, riding on a
    thin full-width guide rib — it must never reach the solid head/sill block.
    The shoe far edge stays strictly inside [open_bot, open_top]. Z is authored
    about the sash center at part-frame z = r.sash_z_off (= world open_cz)."""
    shoe_x = min(0.175, r.sash_w * 0.30)
    zc = r.sash_z_off
    body_half = r.sash_h / 2.0  # sash body top/bottom in part frame about zc
    # The shoe bridges from the sash rail DOWN/UP into the clearance gap, reaching
    # the guide rib (and the joint origin at the rib mid-gap), but its far edge
    # stays a hair INSIDE the opening so it never enters the solid head/sill.
    # body bottom (part frame) = zc - body_half  (= world open_bot + body_clear)
    # opening bottom (part frame) = -zc... use world via r: shoe far edge world
    # must be >= open_bot + edge_keep.
    edge_keep = 0.004  # clearance the shoe keeps from the solid sill/head face
    # shoe far edge world (bottom) target = open_bot + edge_keep
    body_bot_world = r.open_cz - body_half
    body_top_world = r.open_cz + body_half
    bottom_shoe_bot_w = r.open_bot + edge_keep
    top_shoe_top_w = r.open_top - edge_keep
    bottom_shoe_h = body_bot_world - bottom_shoe_bot_w  # spans gap, rides the rib
    top_shoe_h = top_shoe_top_w - body_top_world
    bottom_shoe_cz = zc - body_half - bottom_shoe_h / 2.0  # part-frame center
    top_shoe_cz = zc + body_half + top_shoe_h / 2.0
    if r.track_carriage_style == "roller_truck_cylinders":
        # Nylon rollers (7404a1) on a bracket that BRIDGES the rail down to the
        # roller (no island), the roller bottom riding the rib inside the gap.
        roller_r = max(0.005, min(0.012, bottom_shoe_h * 0.4))
        for i, sx in enumerate((-shoe_x, shoe_x)):
            # Bracket spans the full gap so it touches the rail (top) and reaches
            # the roller (bottom) — one connected carriage.
            part.visual(
                Box((0.066, 0.026, bottom_shoe_h)),
                origin=Origin(xyz=(sx, 0.0, bottom_shoe_cz)),
                material=mats["frame"],
                name=f"roller_bracket_{i}", material_class_id="metal.steel_galvanized",
            )
            # Roller axle at the bracket bottom; the wheel just protrudes below it,
            # staying above the solid sill (roller bottom > open_bot).
            roller_cz = zc - body_half - bottom_shoe_h + roller_r
            part.visual(
                Cylinder(radius=roller_r, length=0.024),
                origin=Origin(xyz=(sx, 0.0, roller_cz), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["hardware"],
                name=f"roller_{i}", material_class_id="plastic.opaque_generic",
            )
            part.visual(
                Box((0.060, _RUNNER_W, top_shoe_h)),
                origin=Origin(xyz=(sx, 0.0, top_shoe_cz)),
                material=mats["hardware"],
                name=f"top_guide_{i}", material_class_id="plastic.opaque_generic",
            )
    else:
        # Box glide shoes (0004 L176-201) bridging the rail to the guide rib.
        for i, sx in enumerate((-shoe_x, shoe_x)):
            part.visual(
                Box((0.085, _RUNNER_W, bottom_shoe_h)),
                origin=Origin(xyz=(sx, 0.0, bottom_shoe_cz)),
                material=mats["hardware"],
                name=f"bottom_glide_{i}", material_class_id="plastic.opaque_generic",
            )
            part.visual(
                Box((0.070, _RUNNER_W, top_shoe_h)),
                origin=Origin(xyz=(sx, 0.0, top_shoe_cz)),
                material=mats["hardware"],
                name=f"top_guide_{i}", material_class_id="plastic.opaque_generic",
            )


def _emit_muntins(part, r, mats) -> None:
    """meeting/muntin divider bars (light multiplicity §2), for-loop emitted."""
    n = r.meeting_muntin_count
    if n <= 0:
        return
    glass_w = r.sash_w - 2.0 * _OUTER_STILE_W - 0.020
    glass_h = r.sash_h - 2.0 * _RAIL_H - 0.020
    zc = r.sash_z_off
    # Vertical muntins evenly dividing the glass width.
    for i in range(n):
        frac = (i + 1) / (n + 1)
        x = -glass_w / 2.0 + frac * glass_w
        part.visual(
            Box((0.012, r.sash_d * 0.7, glass_h)),
            origin=Origin(xyz=(x, 0.0, zc)),
            material=mats["sash"],
            name=f"muntin_{i}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
        )


def _build_sash(
    part,
    r,
    mats,
    *,
    meeting_left: bool,
    moving: bool,
    track_y_sign: float,
    add_keeper: bool = False,
) -> None:
    """Shared glazed-panel factory. The sash CENTER sits at part-frame
    z = r.sash_z_off (so the part-frame origin = the on-runner joint origin and
    the sash still sits centered in the opening)."""
    outer_stile_w = _OUTER_STILE_W
    meeting_stile_w = _MEETING_STILE_W
    rail_h = _RAIL_H
    glass_y = -0.003 if moving else 0.003
    glass_w = r.sash_w - outer_stile_w - meeting_stile_w
    glass_h = r.sash_h - 2.0 * rail_h
    zc = r.sash_z_off  # sash center in part frame

    left_w = meeting_stile_w if meeting_left else outer_stile_w
    right_w = outer_stile_w if meeting_left else meeting_stile_w

    part.visual(
        Box((left_w, r.sash_d, r.sash_h)),
        origin=Origin(xyz=(-r.sash_w / 2.0 + left_w / 2.0, 0.0, zc)),
        material=mats["sash"],
        name="left_stile", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    part.visual(
        Box((right_w, r.sash_d, r.sash_h)),
        origin=Origin(xyz=(r.sash_w / 2.0 - right_w / 2.0, 0.0, zc)),
        material=mats["sash"],
        name="right_stile", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    # Inner span between the two stiles; center it on the true midpoint so the
    # rails touch BOTH stiles regardless of stile-width asymmetry (no islands).
    inner_w = r.sash_w - left_w - right_w
    inner_cx = (left_w - right_w) / 2.0
    part.visual(
        Box((inner_w, r.sash_d, rail_h)),
        origin=Origin(xyz=(inner_cx, 0.0, zc + r.sash_h / 2.0 - rail_h / 2.0)),
        material=mats["sash"],
        name="top_rail", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    part.visual(
        Box((inner_w, r.sash_d, rail_h)),
        origin=Origin(xyz=(inner_cx, 0.0, zc - r.sash_h / 2.0 + rail_h / 2.0)),
        material=mats["sash"],
        name="bottom_rail", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    part.visual(
        Box((glass_w, 0.008, glass_h)),
        origin=Origin(xyz=(inner_cx, glass_y, zc)),
        material=mats["glass"],
        name="glass", material_class_id="glass.clear_transparent",
    )
    part.visual(
        Box((glass_w + 0.012, 0.004, glass_h + 0.012)),
        origin=Origin(xyz=(inner_cx, glass_y + 0.002, zc)),
        material=mats["seal"],
        name="glazing_gasket", material_class_id="rubber.smooth_plain",
    )

    # Meeting interlock fin + seal at the meeting stile.
    interlock_w = 0.016
    interlock_h = min(0.58, r.sash_h - 2.0 * rail_h - 0.02)
    if meeting_left:
        interlock_x = -r.sash_w / 2.0 + meeting_stile_w + interlock_w / 2.0
        interlock_y = -0.010
    else:
        interlock_x = r.sash_w / 2.0 - meeting_stile_w - interlock_w / 2.0
        interlock_y = 0.010
    part.visual(
        Box((interlock_w, 0.012, interlock_h)),
        origin=Origin(xyz=(interlock_x, interlock_y, zc)),
        material=mats["accent"],
        name="interlock_fin", material_class_id="rubber.smooth_plain",
    )

    # Carriage (Slot B) + muntins (multiplicity §2).
    _emit_sash_carriage(part, r, mats, track_y_sign=track_y_sign)
    _emit_muntins(part, r, mats)

    if moving:
        _emit_handle(part, r, mats)
    if add_keeper:
        # Passive keeper block on the fixed/meeting stile.
        keeper_x = (
            r.sash_w / 2.0 - 0.040 if not meeting_left else -r.sash_w / 2.0 + 0.040
        )
        part.visual(
            Box((0.042, 0.010, 0.050)),
            origin=Origin(xyz=(keeper_x, 0.020, zc - 0.060)),
            material=mats["hardware"],
            name="keeper_block", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
        )


# ---------------------------------------------------------------------------
# Handle styles (Slot D) — parent visual on the sliding sash, no joint (Rule 1).
# Authored about the meeting stile of the moving sash (interior face +Y).
# ---------------------------------------------------------------------------
def _emit_handle(part, r, mats) -> None:
    style = r.handle_style
    hx = -r.sash_w / 2.0 + 0.040  # near the meeting (left) stile of the moving sash
    face_y = r.sash_d / 2.0
    zc = r.sash_z_off  # sash center in part frame
    if style == "pull_bar":
        part.visual(
            Box((0.066, 0.012, 0.130)),
            origin=Origin(xyz=(hx, face_y + 0.006, zc)),
            material=mats["hardware"],
            name="pull_base", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
        )
        part.visual(
            Box((0.030, 0.016, 0.100)),
            origin=Origin(xyz=(hx, face_y + 0.016, zc)),
            material=mats["accent"],
            name="pull_grip", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
        )
    elif style == "flush_recess":
        # Recess plate flush in the stile face + a lip.
        part.visual(
            Box((0.040, 0.008, 0.120)),
            origin=Origin(xyz=(hx, face_y, zc)),
            material=mats["hardware"],
            name="flush_pull_recess", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
        )
        part.visual(
            Box((0.040, 0.006, 0.014)),
            origin=Origin(xyz=(hx, face_y + 0.004, zc + 0.050)),
            material=mats["accent"],
            name="pull_lip", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
        )
    elif style == "finger_pull":
        part.visual(
            Cylinder(radius=0.010, length=0.090),
            origin=Origin(xyz=(hx, face_y + 0.006, zc)),
            material=mats["hardware"],
            name="finger_pull", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
        )
    elif style == "molded_grip_ribs":
        n = r.grip_rib_count
        z0 = -0.5 * (n - 1) * 0.024
        # A grip base so the ribs are not a floating island row.
        part.visual(
            Box((0.030, 0.008, (n - 1) * 0.024 + 0.030)),
            origin=Origin(xyz=(hx, face_y + 0.002, zc)),
            material=mats["hardware"],
            name="grip_base", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
        )
        for i in range(n):
            z = z0 + i * 0.024
            part.visual(
                Box((0.026, 0.012, 0.014)),
                origin=Origin(xyz=(hx, face_y + 0.008, zc + z)),
                material=mats["accent"],
                name=f"grip_rib_{i}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
            )
    else:  # d_pull_plate
        part.visual(
            Box((0.050, 0.010, 0.150)),
            origin=Origin(xyz=(hx, face_y + 0.005, zc)),
            material=mats["hardware"],
            name="pull_plate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
        )
        for i, z in enumerate((-0.060, 0.060)):
            part.visual(
                Box((0.026, 0.022, 0.026)),
                origin=Origin(xyz=(hx, face_y + 0.020, zc + z)),
                material=mats["hardware"],
                name=f"d_mount_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
            )
        part.visual(
            Box((0.020, 0.040, 0.110)),
            origin=Origin(xyz=(hx, face_y + 0.035, zc)),
            material=mats["accent"],
            name="d_pull_bar", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
        )


# ---------------------------------------------------------------------------
# Frame (root). Perimeter ring + track (Slot B) + baked fixed glass (Slot A
# baked) or nothing (separate / sash_only).
# ---------------------------------------------------------------------------
def _build_frame(model, r, mats, *, assets):
    frame = model.part("frame")
    frame.inertial = Inertial.from_geometry(
        Box((r.frame_w, r.frame_d, r.frame_h)), mass=30.0
    )
    frame.visual(
        Box((r.jamb_w, r.frame_d, r.frame_h)),
        origin=Origin(xyz=(-r.frame_w / 2.0 + r.jamb_w / 2.0, 0.0, 0.0)),
        material=mats["frame"],
        name="left_jamb", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Box((r.jamb_w, r.frame_d, r.frame_h)),
        origin=Origin(xyz=(r.frame_w / 2.0 - r.jamb_w / 2.0, 0.0, 0.0)),
        material=mats["frame"],
        name="right_jamb", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Box((r.open_w, r.frame_d, r.head_h)),
        origin=Origin(xyz=(0.0, 0.0, r.frame_h / 2.0 - r.head_h / 2.0)),
        material=mats["frame"],
        name="head", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Box((r.open_w, r.frame_d, r.sill_h)),
        origin=Origin(xyz=(0.0, 0.0, -r.frame_h / 2.0 + r.sill_h / 2.0)),
        material=mats["frame"],
        name="sill", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    # Perimeter fasteners (for-loop emitted).
    fx = r.frame_w / 2.0 - r.jamb_w * 0.45
    fz = r.frame_h / 2.0 - 0.04
    idx = 0
    for x in (-fx, fx):
        for z in (-fz, fz):
            frame.visual(
                Cylinder(radius=0.007, length=0.006),
                origin=Origin(xyz=(x, r.frame_d / 2.0 + 0.002, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["accent"],
                name=f"frame_bolt_{idx}", material_class_id="metal.stainless_matte",
            )
            idx += 1

    # Vertical jamb track liners at the front/rear track Y, spanning the full
    # open height. They read as the channel side liners the sash outer stile laps
    # against at the closing jamb, and connect the sill/head track beds to the
    # jamb ring. (The joint origins now anchor on the sill runner — see
    # _emit_sliding_sash / _emit_fixed_lite_part — so no horizontal mid-rail is
    # needed; this avoids drawing a dark cross-bar across the panes.)
    liner_z_h = r.open_h
    for y, prefix in ((-r.track_y, "rear"), (r.track_y, "front")):
        for x_sign, jname in ((-1.0, "left"), (1.0, "right")):
            frame.visual(
                Box((0.012, _RUNNER_W, liner_z_h)),
                origin=Origin(
                    xyz=(x_sign * (r.open_w / 2.0 - 0.006), y, 0.0)
                ),
                material=mats["seal"],
                name=f"{prefix}_{jname}_jamb_liner", material_class_id="rubber.smooth_plain",
            )

    # Track / carriage (Slot B).
    builder = _TRACK_BUILDERS[r.track_carriage_style]
    if r.track_carriage_style == "cadquery_hollow_channel":
        builder(frame, r, mats, assets=assets)
    else:
        builder(frame, r, mats)

    # Slot A = baked_into_frame: fixed glass + meeting stile as frame visuals.
    if r.fixed_glazing_topology == "baked_into_frame":
        _emit_baked_fixed_glazing(frame, r, mats)
    return frame


def _emit_baked_fixed_glazing(frame, r, mats) -> None:
    """Baked fixed lite (0001/0002 L177-206): fixed glass + meeting stile +
    side stile as frame visuals (no separate part)."""
    fx = r.fixed_x
    fixed_w = r.sash_w
    fixed_h = r.sash_h
    fixed_y = -r.track_y  # rear lane
    rail_h = _RAIL_H
    stile_w = _OUTER_STILE_W
    glass_w = fixed_w - 2.0 * stile_w
    glass_h = fixed_h - 2.0 * rail_h
    frame.visual(
        Box((glass_w, 0.008, glass_h)),
        origin=Origin(xyz=(fx, fixed_y, 0.0)),
        material=mats["glass"],
        name="fixed_glass", material_class_id="glass.clear_transparent",
    )
    frame.visual(
        Box((glass_w + 0.010, 0.004, glass_h + 0.010)),
        origin=Origin(xyz=(fx, fixed_y + 0.003, 0.0)),
        material=mats["seal"],
        name="fixed_gasket", material_class_id="rubber.smooth_plain",
    )
    # Meeting stile (toward the center) + outer side stile (toward the jamb).
    meeting_sign = 1.0 if r.open_sign <= 0.0 else -1.0
    frame.visual(
        Box((stile_w, r.sash_d, fixed_h)),
        origin=Origin(xyz=(fx + meeting_sign * (fixed_w / 2.0 - stile_w / 2.0), fixed_y, 0.0)),
        material=mats["sash"],
        name="fixed_meeting_stile", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Box((stile_w, r.sash_d, fixed_h)),
        origin=Origin(xyz=(fx - meeting_sign * (fixed_w / 2.0 - stile_w / 2.0), fixed_y, 0.0)),
        material=mats["sash"],
        name="fixed_side_stile", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Box((glass_w, r.sash_d, rail_h)),
        origin=Origin(xyz=(fx, fixed_y, fixed_h / 2.0 - rail_h / 2.0)),
        material=mats["sash"],
        name="fixed_top_rail", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    frame.visual(
        Box((glass_w, r.sash_d, rail_h)),
        origin=Origin(xyz=(fx, fixed_y, -fixed_h / 2.0 + rail_h / 2.0)),
        material=mats["sash"],
        name="fixed_bottom_rail", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )


# ---------------------------------------------------------------------------
# Slot A: fixed glazing topology — emits fixed_lite part (separate) or nothing.
# ---------------------------------------------------------------------------
def _emit_fixed_lite_part(model, r, mats, frame) -> list[str]:
    """separate_fixed_part (0004 L422-455): independent FIXED fixed_lite."""
    fixed_lite = model.part("fixed_lite")
    fixed_lite.inertial = Inertial.from_geometry(
        Box((r.sash_w, r.sash_d, r.sash_h)), mass=10.0,
        origin=Origin(xyz=(0.0, 0.0, r.sash_z_off)),
    )
    # The fixed lite's meeting stile faces the moving sash (center). For default
    # left-open: moving sash is on the right, fixed on the left -> fixed meeting
    # stile is on the RIGHT (meeting_left=False).
    meeting_left = r.open_sign > 0.0
    _build_sash(
        fixed_lite, r, mats,
        meeting_left=meeting_left, moving=False, track_y_sign=-1.0, add_keeper=True,
    )
    model.articulation(
        "frame_to_fixed_lite",
        ArticulationType.FIXED,
        parent=frame,
        child=fixed_lite,
        # Origin on the rear sill runner (real hardware); sash authored at z=sash_z_off.
        origin=Origin(xyz=(r.fixed_x, -r.track_y, r.runner_z)),
    )
    return ["fixed_lite"]


# ---------------------------------------------------------------------------
# Sliding sash (category-defining PRISMATIC) — always present.
# ---------------------------------------------------------------------------
def _emit_sliding_sash(model, r, mats, frame) -> str:
    sliding = model.part("sliding_sash")
    sliding.inertial = Inertial.from_geometry(
        Box((r.sash_w, r.sash_d, r.sash_h)), mass=11.0,
        origin=Origin(xyz=(0.0, 0.0, r.sash_z_off)),
    )
    if r.sash_count == 1:
        # sash_only: full-bay sash, meeting stile toward opening side is just a
        # second outer stile; keep meeting_left=True for the handle anchor.
        _build_sash(sliding, r, mats, meeting_left=True, moving=True, track_y_sign=1.0)
    else:
        # The moving sash meets the fixed lite at the center. For default
        # left-open: moving sash on the right -> its meeting stile is on the LEFT.
        meeting_left = r.open_sign <= 0.0
        _build_sash(sliding, r, mats, meeting_left=meeting_left, moving=True, track_y_sign=1.0)

    # PRISMATIC travel / limits derived from the closed-pose X so the sash center
    # always stays within [-c, +c] (the in-bay slack) — never rams a jamb.
    axis = (1.0, 0.0, 0.0)
    c = max(0.0, (r.open_w - r.sash_w) / 2.0)
    if r.sash_count == 1 and r.open_direction == "bidirectional_center":
        # Parked centered (closed_x≈0); opens both ways within the bay.
        half = min(r.sliding_travel / 2.0, c)
        lower = -half
        upper = half
    elif r.sash_closed_x >= 0.0:
        # Closed at the +c (right) jamb -> opens toward -X.
        lower = -min(r.sliding_travel, r.sash_closed_x + c)
        upper = 0.0
    else:
        # Closed at the -c (left) jamb -> opens toward +X.
        lower = 0.0
        upper = min(r.sliding_travel, c - r.sash_closed_x)

    model.articulation(
        "frame_to_sliding_sash",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=sliding,
        # Origin on the front sill runner (real hardware) at the closed-sash X;
        # the sash is authored with its center at part-frame z=sash_z_off so it
        # still sits centered in the opening (no horizontal mid-rail needed).
        origin=Origin(xyz=(r.sash_closed_x, r.track_y, r.runner_z)),
        axis=axis,
        motion_limits=MotionLimits(effort=60.0, velocity=0.5, lower=lower, upper=upper),
    )
    return "sliding_sash"


# ---------------------------------------------------------------------------
# Slot C: lock articulation.
# ---------------------------------------------------------------------------
def _emit_lock_none(model, r, mats, frame, sliding) -> list[str]:
    """none_passive_visual: passive keeper visual on the sash, no joint."""
    sash = model.get_part(sliding)
    hx = -r.sash_w / 2.0 + 0.040
    sash.visual(
        Box((0.034, 0.012, 0.044)),
        origin=Origin(xyz=(hx + 0.010, r.sash_d / 2.0 + 0.006, r.sash_z_off - 0.080)),
        material=mats["hardware"],
        name="passive_keeper", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
    )
    return []


def _emit_lock_thumbturn(model, r, mats, frame, sliding) -> list[str]:
    """thumbturn_revolute (0005 L388-453): independent latch part, REVOLUTE Y."""
    sash = model.get_part(sliding)
    latch = model.part("latch")
    latch.inertial = Inertial.from_geometry(
        Box((0.040, 0.020, 0.110)), mass=0.15, origin=Origin(xyz=(0.0, -0.008, -0.028))
    )
    # Latch authored about its pivot (part origin); escutcheon + thumbturn extend
    # toward -Y (interior) and down.
    latch.visual(
        Box((0.032, 0.006, 0.096)),
        origin=Origin(xyz=(0.0, -0.004, -0.018)),
        material=mats["hardware"],
        name="escutcheon", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
    )
    latch.visual(
        Cylinder(radius=0.009, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="pivot_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
    )
    latch.visual(
        Box((0.012, 0.020, 0.060)),
        origin=Origin(xyz=(0.0, -0.010, -0.030)),
        material=mats["accent"],
        name="thumbturn", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
    )
    latch.visual(
        Box((0.020, 0.014, 0.016)),
        origin=Origin(xyz=(0.0, -0.012, -0.056)),
        material=mats["accent"],
        name="thumb_pad", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
    )
    # Anchor on the moving sash meeting stile (visible interior face +Y).
    hx = -r.sash_w / 2.0 + 0.040
    model.articulation(
        "sliding_sash_to_latch",
        ArticulationType.REVOLUTE,
        parent=sash,
        child=latch,
        origin=Origin(xyz=(hx, r.sash_d / 2.0 + 0.004, r.sash_z_off + 0.020)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=2.0, lower=-1.05, upper=0.15),
    )
    return ["latch"]


def _emit_lock_crescent(model, r, mats, frame, sliding) -> list[str]:
    """crescent_cam_revolute (43f22f89 L228-256): pivot hub + latch bar, REVOLUTE Y."""
    sash = model.get_part(sliding)
    # A jamb/stile keeper plate on the sash (so the cam has something to latch into).
    hx = -r.sash_w / 2.0 + 0.040
    # Keeper plate embedded into the sash stile face at the latch column (the
    # left stile is always >= 0.050 wide, so hx sits on solid stile material).
    sash.visual(
        Box((0.020, 0.016, 0.060)),
        origin=Origin(xyz=(hx, r.sash_d / 2.0 - 0.004, r.sash_z_off + 0.020)),
        material=mats["hardware"],
        name="keeper_plate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
    )
    latch = model.part("latch")
    latch.inertial = Inertial.from_geometry(
        Box((0.100, 0.020, 0.040)), mass=0.10, origin=Origin(xyz=(0.040, 0.004, 0.0))
    )
    # Crescent cam authored about pivot (part origin): hub at origin, bar extends +X.
    latch.visual(
        Cylinder(radius=0.014, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="pivot_hub", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"silver_aluminum", "white_vinyl", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "metal.stainless_matte"),
    )
    latch.visual(
        Box((0.092, 0.008, 0.018)),
        origin=Origin(xyz=(0.047, 0.004, 0.0)),
        material=mats["accent"],
        name="latch_bar", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
    )
    latch.visual(
        Cylinder(radius=0.006, length=0.008),
        origin=Origin(xyz=(0.0, 0.008, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["accent"],
        name="cam_screw", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        "sliding_sash_to_latch",
        ArticulationType.REVOLUTE,
        parent=sash,
        child=latch,
        origin=Origin(xyz=(hx, r.sash_d / 2.0 + 0.006, r.sash_z_off + 0.020)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=1.35),
    )
    return ["latch"]


def _emit_lock_lockout_pin(model, r, mats, frame, sliding) -> list[str]:
    """lockout_pin_prismatic (b5bb4681 L145-159): vertical lift-out lock pin,
    independent part, PRISMATIC axis (0,0,1) on the frame jamb. Distinct
    axis/origin from the sash X-slide -> no kinematic crosstalk."""
    lock_pin = model.part("lock_pin")
    pin_len = 0.180 * (r.frame_h / _FRAME_H)
    lock_pin.inertial = Inertial.from_geometry(
        Box((0.040, 0.040, pin_len + 0.060)), mass=0.30
    )
    # Pin authored about its part origin (shaft straddles 0 so origin is in geometry).
    lock_pin.visual(
        Cylinder(radius=0.012, length=pin_len),
        origin=Origin(),
        material=mats["hardware"],
        name="pin_shaft", material_class_id="metal.stainless_matte",
    )
    lock_pin.visual(
        Cylinder(radius=0.014, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, pin_len / 2.0 + 0.020)),
        material=mats["hardware"],
        name="handle_neck", material_class_id="metal.stainless_matte",
    )
    lock_pin.visual(
        Cylinder(radius=0.016, length=0.120),
        origin=Origin(xyz=(0.0, 0.0, pin_len / 2.0 + 0.040), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["accent"],
        name="tee_handle", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
    )
    lock_pin.visual(
        Box((0.030, 0.012, 0.040)),
        origin=Origin(xyz=(0.0, -0.018, -pin_len / 2.0 + 0.020)),
        material=mats["accent"],
        name="lockout_flag", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder"} else "plastic.opaque_generic"),
    )
    # Frame keeper boss seated in the HEAD, just above the opening, at the
    # closing-jamb edge (over the sash's outer stile column, NOT the glass) so
    # the sash body slides clear of it; the pin drops down through the boss into
    # the sash top-rail keeper (captured pin). Boss center sits mostly in the
    # solid head; the joint origin lands on the boss + on the pin shaft.
    sash_outer_edge = r.sash_closed_x + (
        -r.sash_w / 2.0 + 0.020 if r.open_sign <= 0.0 else r.sash_w / 2.0 - 0.020
    )
    pin_x = sash_outer_edge
    boss_z = r.open_h / 2.0 + 0.010  # mostly in the head, above the sash top
    frame.visual(
        Box((0.044, 0.044, 0.090)),
        origin=Origin(xyz=(pin_x, r.track_y, boss_z)),
        material=mats["frame"],
        name="lock_keeper_boss", material_class_id=("metal.aluminum_bare" if r.palette_style in {"silver_aluminum", "dark_anodized_graphite", "charcoal_black_powder", "industrial_safety", "field_service_bronze"} else "plastic.opaque_generic"),
    )
    model.articulation(
        "frame_to_lock_pin",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=lock_pin,
        origin=Origin(xyz=(pin_x, r.track_y, boss_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.20, lower=0.0, upper=0.060),
    )
    return ["lock_pin"]


_LOCK_BUILDERS = {
    "none_passive_visual": _emit_lock_none,
    "thumbturn_revolute": _emit_lock_thumbturn,
    "crescent_cam_revolute": _emit_lock_crescent,
    "lockout_pin_prismatic": _emit_lock_lockout_pin,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_sliding_window_classic(
    config: SlidingWindowClassicConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"swc_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    frame = _build_frame(model, r, mats, assets=assets)

    # Slot A: separate fixed lite part (else baked/sash_only handled in frame).
    if r.fixed_glazing_topology == "separate_fixed_part":
        _emit_fixed_lite_part(model, r, mats, frame)

    # Category-defining sliding sash (PRISMATIC).
    sliding = _emit_sliding_sash(model, r, mats, frame)

    # Slot C: lock articulation.
    _LOCK_BUILDERS[r.lock_articulation](model, r, mats, frame, sliding)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_sliding_window_classic(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_sliding_window_classic(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_sliding_window_classic_tests(
    object_model: ArticulatedObject,
    config: SlidingWindowClassicConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    sliding = object_model.get_part("sliding_sash")

    # ---- Captured-pin / slide / mount allowances (element-scoped). ----
    # The moving sash slides in its own front-lane track channel on a distinct
    # depth (Y) plane from the rear-lane fixed lite / baked glass. The sash BODY
    # sits strictly INSIDE the clear opening (body_clear gap top & bottom); only a
    # thin GUIDE SHOE protrudes into the gap to ride a full-width guide rib. The
    # SOLID head/sill blocks are intentionally NOT in the allowance list, so any
    # sash element entering the solid head/sill is a hard FAIL, not masked.
    # The only allowed sash<->frame overlaps are the shoe/roller/stile riding the
    # thin track ribs/lips/beds/liners (constant shoe-in-channel contact).
    sash_contact_elems = [
        "bottom_glide_0", "bottom_glide_1", "top_guide_0", "top_guide_1",
        "roller_0", "roller_1", "roller_bracket_0", "roller_bracket_1",
        "left_stile", "right_stile", "top_rail", "bottom_rail",
    ]
    frame_track_elems = [
        # NOTE: the solid "sill"/"head" blocks are deliberately EXCLUDED here.
        "sill_bed", "head_bed",
        "front_runner", "rear_runner", "front_head_guide", "rear_head_guide",
        "front_roller_track", "rear_roller_track",
        "sill_front_guide", "head_front_guide", "sill_back_guide", "head_back_guide",
        "sill_separator_guide", "head_separator_guide",
        "sill_front_outer_lip", "sill_rear_outer_lip", "sill_center_lip",
        "head_front_outer_lip", "head_rear_outer_lip", "head_center_lip",
        "front_left_jamb_liner", "front_right_jamb_liner",
        "rear_left_jamb_liner", "rear_right_jamb_liner",
        "cq_sill_channel", "cq_head_channel",
        "lock_keeper_boss",
    ]
    sash_vis = {v.name for v in sliding.visuals}
    frame_vis = {v.name for v in frame.visuals}
    for se in sash_contact_elems:
        if se not in sash_vis:
            continue
        for fe in frame_track_elems:
            if fe not in frame_vis:
                continue
            ctx.allow_overlap(
                sliding, frame, elem_a=se, elem_b=fe,
                reason="sash carriage/stile rides the frame track runner/bed/guide/liner (sliding fit).",
            )
    if r.fixed_glazing_topology == "separate_fixed_part":
        fixed_lite = object_model.get_part("fixed_lite")
        ctx.allow_overlap(
            fixed_lite, frame, reason="fixed lite glides seat in the rear track / against jamb.",
        )
        ctx.allow_overlap(
            sliding, fixed_lite,
            reason="closed sliding sash overlaps the fixed lite in projection at the meeting stile.",
        )

    if r.lock_articulation in ("thumbturn_revolute", "crescent_cam_revolute"):
        latch = object_model.get_part("latch")
        ctx.allow_overlap(
            latch, sliding,
            reason="latch pivot boss/escutcheon seats on the sash meeting stile face.",
        )
        # The latch is small hardware on the meeting stile; as the sash slides it
        # can sweep past the frame jamb/track edge -> allow that grazing overlap.
        ctx.allow_overlap(
            latch, frame,
            reason="sash-mounted latch sweeps past the frame jamb / track lip as the sash slides.",
        )
    elif r.lock_articulation == "lockout_pin_prismatic":
        lock_pin = object_model.get_part("lock_pin")
        ctx.allow_overlap(
            lock_pin, frame,
            reason="lock pin shaft slides through the frame keeper boss (captured slide).",
        )
        ctx.allow_overlap(
            lock_pin, sliding,
            reason="lock pin drops through the sash stile keeper hole to lock it (captured pin).",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("frame root present", "frame" in part_names, details=str(sorted(part_names)))
    ctx.check(
        "sliding_sash present",
        "sliding_sash" in part_names,
        details=str(sorted(part_names)),
    )

    # Slot A: part-tree topology.
    if r.fixed_glazing_topology == "separate_fixed_part":
        ctx.check("separate fixed lite part present", "fixed_lite" in part_names)
        jf = object_model.get_articulation("frame_to_fixed_lite")
        ctx.check(
            "fixed lite is FIXED to frame",
            jf.articulation_type == ArticulationType.FIXED,
            details=str(jf.articulation_type),
        )
    else:
        ctx.check(
            "no separate fixed lite part (baked / sash_only)",
            "fixed_lite" not in part_names,
        )

    # Category-defining PRISMATIC sash.
    js = object_model.get_articulation("frame_to_sliding_sash")
    ctx.check(
        "sliding sash is PRISMATIC about X",
        js.articulation_type == ArticulationType.PRISMATIC and abs(js.axis[0]) > 0.99,
        details=f"type={js.articulation_type} axis={tuple(js.axis)}",
    )

    # Slot C: lock joint topology.
    if r.lock_articulation in ("thumbturn_revolute", "crescent_cam_revolute"):
        jl = object_model.get_articulation("sliding_sash_to_latch")
        ctx.check(
            "latch is REVOLUTE about Y",
            jl.articulation_type == ArticulationType.REVOLUTE and abs(jl.axis[1]) > 0.99,
            details=f"type={jl.articulation_type} axis={tuple(jl.axis)}",
        )
    elif r.lock_articulation == "lockout_pin_prismatic":
        jp = object_model.get_articulation("frame_to_lock_pin")
        ctx.check(
            "lock pin is PRISMATIC about Z (distinct from sash X-slide)",
            jp.articulation_type == ArticulationType.PRISMATIC and abs(jp.axis[2]) > 0.99,
            details=f"type={jp.articulation_type} axis={tuple(jp.axis)}",
        )

    # Handle present on the moving sash (Slot D, Rule 1: parent visual).
    handle_names = {
        "pull_bar": "pull_base",
        "flush_recess": "flush_pull_recess",
        "finger_pull": "finger_pull",
        "molded_grip_ribs": "grip_rib_0",
        "d_pull_plate": "pull_plate",
    }
    hname = handle_names[r.handle_style]
    sash_visuals = {v.name for v in sliding.visuals}
    ctx.check(
        f"handle '{r.handle_style}' visual on sliding sash",
        hname in sash_visuals,
        details=f"looking for {hname} in {sorted(sash_visuals)}",
    )
    if r.handle_style == "molded_grip_ribs":
        ribs = [n for n in sash_visuals if n.startswith("grip_rib_")]
        ctx.check(
            "N grip ribs for-loop emitted",
            len(ribs) == r.grip_rib_count,
            details=f"ribs={sorted(ribs)} expected N={r.grip_rib_count}",
        )

    # Muntin multiplicity (light axis §2).
    muntins = [n for n in sash_visuals if n.startswith("muntin_")]
    ctx.check(
        "N muntins for-loop emitted",
        len(muntins) == r.meeting_muntin_count,
        details=f"muntins={sorted(muntins)} expected N={r.meeting_muntin_count}",
    )

    # ---- Sliding sash actuates along X and stays supported / in the bay. ----
    limits = js.motion_limits
    assert limits is not None
    p0 = ctx.part_world_position(sliding)
    open_q = limits.lower if (limits.lower is not None and abs(limits.lower) > 1e-6) else limits.upper
    if open_q is not None and abs(open_q) > 1e-6:
        with ctx.pose({js: open_q}):
            p1 = ctx.part_world_position(sliding)
            ctx.fail_if_parts_overlap_in_current_pose(name="sash_open_pose_no_overlap")
            ctx.fail_if_isolated_parts(name="sash_open_pose_no_floating")
        if p0 is not None and p1 is not None:
            # The X displacement should track the commanded prismatic q (axis +X).
            ctx.check(
                "sliding sash translates along X by the commanded amount",
                abs(abs(p1[0] - p0[0]) - abs(open_q)) < 0.005,
                details=f"dx={p1[0]-p0[0]:.4f} commanded={open_q:.4f}",
            )
            ctx.check(
                "sliding sash stays in the bay (no Y/Z drift)",
                abs(p1[1] - p0[1]) < 0.005 and abs(p1[2] - p0[2]) < 0.005,
                details=f"dy={p1[1]-p0[1]:.4f} dz={p1[2]-p0[2]:.4f}",
            )

    # ---- MANDATORY: sash rails clear the SOLID head/sill over the FULL travel. ----
    # (ref_service_slider_window.py pattern) The solid head/sill occupy only the Z
    # bands above/below the clear opening; the sash body (top_rail/bottom_rail/glass)
    # must keep a real Z gap to them at closed / mid / fully-open — never 穿模 the
    # top/bottom. We measure the real interpenetration of the sash top_rail with the
    # solid head and the bottom_rail with the solid sill at each pose.
    def _sash_elem_world_z(part, elem_name, dx):
        """(z_min, z_max) of a named sash visual in world, sash shifted by dx in X.
        Z is unaffected by the X slide, so just read the local Z extent + sash
        center placement (joint origin runner_z + part-local z)."""
        for v in part.visuals:
            if v.name == elem_name:
                g = v.geometry
                sz = g.size[2] if hasattr(g, "size") else 2.0 * getattr(g, "radius", 0.0)
                local_z = v.origin.xyz[2]
                world_cz = r.runner_z + local_z  # part frame origin sits at runner_z
                return world_cz - sz / 2.0, world_cz + sz / 2.0
        return None

    solid_head_bottom = r.open_top  # solid head occupies z >= open_top
    solid_sill_top = r.open_bot     # solid sill occupies z <= open_bot
    sash_vis_now = {v.name for v in sliding.visuals}
    if "top_rail" in sash_vis_now and "bottom_rail" in sash_vis_now:
        tr = _sash_elem_world_z(sliding, "top_rail", 0.0)
        br = _sash_elem_world_z(sliding, "bottom_rail", 0.0)
        if tr is not None and br is not None:
            top_gap = solid_head_bottom - tr[1]
            bot_gap = br[0] - solid_sill_top
            ctx.check(
                "sash top_rail clears the SOLID head (z gap > 0 over full travel)",
                top_gap > 0.002,
                details=(
                    f"top_rail.z_max={tr[1]:.4f} < head_solid.z_min={solid_head_bottom:.4f} "
                    f"(gap={top_gap:.4f})"
                ),
            )
            ctx.check(
                "sash bottom_rail clears the SOLID sill (z gap > 0 over full travel)",
                bot_gap > 0.002,
                details=(
                    f"bottom_rail.z_min={br[0]:.4f} > sill_solid.z_max={solid_sill_top:.4f} "
                    f"(gap={bot_gap:.4f})"
                ),
            )
    # And explicitly: at closed / mid / fully-open, the top_rail<->head and
    # bottom_rail<->sill interpenetration must be ~0 (only shoe-in-channel contact).
    poses_to_check = [("closed", 0.0)]
    if limits is not None:
        lo = limits.lower if limits.lower is not None else 0.0
        hi = limits.upper if limits.upper is not None else 0.0
        poses_to_check.append(("mid", 0.5 * (lo + hi)))
        poses_to_check.append(("open", lo if abs(lo) > abs(hi) else hi))
    for label, q in poses_to_check:
        with ctx.pose({js: q}):
            ctx.fail_if_parts_overlap_in_current_pose(
                name=f"sash_no_solid_head_sill_penetration_{label}"
            )

    # ---- Lock actuation moves. ----
    if r.lock_articulation in ("thumbturn_revolute", "crescent_cam_revolute"):
        jl = object_model.get_articulation("sliding_sash_to_latch")
        latch = object_model.get_part("latch")
        a0 = ctx.part_world_aabb(latch)
        with ctx.pose({jl: 1.0}):
            a1 = ctx.part_world_aabb(latch)
        if a0 is not None and a1 is not None:
            moved = (
                abs(a1[0][0] - a0[0][0])
                + abs(a1[1][2] - a0[1][2])
                + abs(a1[0][2] - a0[0][2])
            )
            ctx.check("latch rotates (AABB shifts)", moved > 0.010, details=f"moved={moved:.4f}")
    elif r.lock_articulation == "lockout_pin_prismatic":
        jp = object_model.get_articulation("frame_to_lock_pin")
        lock_pin = object_model.get_part("lock_pin")
        z0 = ctx.part_world_position(lock_pin)
        with ctx.pose({jp: 0.055}):
            z1 = ctx.part_world_position(lock_pin)
        if z0 is not None and z1 is not None:
            ctx.check(
                "lock pin lifts straight up",
                z1[2] > z0[2] + 0.030,
                details=f"seated_z={z0[2]:.3f} lifted_z={z1[2]:.3f}",
            )

    # ---- Footprint / ground / proportion. ----
    fb = ctx.part_world_aabb(frame)
    if fb is not None:
        depth = fb[1][1] - fb[0][1]
        height = fb[1][2] - fb[0][2]
        ctx.check(
            "window stands (depth < height, not lying down)",
            depth < height,
            details=f"depth={depth:.3f} height={height:.3f}",
        )

    ctx.fail_if_articulation_overlaps(max_pose_samples=20)
    return ctx.report()


# Generic-wrapper aliases (CLI imports these exact names).
SlidingWindowClassicConfigT = SlidingWindowClassicConfig
