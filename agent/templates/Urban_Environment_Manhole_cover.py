# SPDX-License-Identifier: Apache-2.0

"""Square cast-iron drain grate / utility access cover — modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Urban_Environment_Manhole_cover.md`` and the four
5-star samples (S1 cast_iron_fan_slot_floor_drain, S2 cast_iron_basket_weave_
grate, S3 cast_iron_inspection_cover, S4 concrete_utility_access_cover).

Core identity: a square (or derived round / rectangular) cast-iron / concrete
drain grate or inspection access cover that **seats into a recessed frame**,
with a hollow shaft / throat below.  The cover is the articulated child — the
opening mechanism is a real non-FIXED joint: default ``lift_out_prismatic``
(+Z lift-out) or a ``hinged_flap_revolute`` (edge flip-up; pivot on the cover
TOP +Y edge, axis -X, so the up-swing arc clears the shaft throat below).  The cast pattern
on the cover face (grate slots / bars / waffle cells / radial spokes) is a
**boolean CUT loop** through the cover solid (loop-emitted multiplicity, NOT
floating Box/Cylinder parts).

Structure (pattern = ``mixed``, parallel-children + multiplicity):

    frame  (FIXED root, footprint base z≈0)
      ├─[FIXED, origin=Origin()]──────────► shaft   (hollow throat void below seat)
      └─[DEFINING: PRISMATIC +Z  OR  REVOLUTE edge]──► cover (grate child)
                                              └─ surface_pattern emits N boolean
                                                 through-slots cut into the cover
                                                 solid (module-local, one mesh)

Four named slots:
  * Slot A ``cover_outline`` (3): square / round / rectangular footprint of the
    cover board + frame ring + shaft throat.
  * Slot B ``surface_pattern`` (5): solid_lid (N=0 cosmetic pry slot) /
    basket_weave / parallel_slots / cross_grid / radial_pattern — decides the
    multiplicity axis N (boolean through-cuts in the cover solid).
  * Slot C ``open_mechanism`` (2): lift_out_prismatic (+Z) / hinged_flap_revolute
    (edge flip) — the DEFINING non-FIXED joint.
  * Slot D ``frame_style`` (3): iron_seat_frame / concrete_stone_frame /
    flush_concrete_surround — the FIXED frame geometry / seat semantics.

Multiplicity (spec §Multiplicity): one axis N (the cast-pattern cell count),
exposed only when B != solid_lid.  Encoded into the slot_choice tuple as
``("slot_count", f"n{N}")``.  N is capped modestly to keep boolean-cut /
tessellation cost bounded (MESH-PERF).

3 hard rules satisfied:
  1. The cast pattern + rim + studs are cover_body visuals (one cut mesh) /
     named visuals on the frame, NOT separate FIXED parts (Rule 1).
  2. The DEFINING lift/hinge joint declares a ``MatingContract`` pinning the
     cover bottom face to the frame seat-ledge top face (closed pose contact).
  3. The grate slots are boolean CUTS in the cover solid, loop-emitted as
     ``grate_{i}`` cutters — not Box/Cylinder downgrades.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
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
CoverOutline = Literal["square", "round", "rectangular"]
SurfacePattern = Literal[
    "solid_lid", "basket_weave", "parallel_slots", "cross_grid", "radial_pattern"
]
OpenMechanism = Literal["lift_out_prismatic", "hinged_flap_revolute"]
FrameStyle = Literal["iron_seat_frame", "concrete_stone_frame", "flush_concrete_surround"]
PaletteStyle = Literal[
    "cast_iron_black",
    "weathered_rust",
    "cast_graphite",
    "concrete_grey",
    "stone_grey",
    "enamel_drain_green",
]

COVER_OUTLINES: tuple[CoverOutline, ...] = ("square", "round", "rectangular")
SURFACE_PATTERNS: tuple[SurfacePattern, ...] = (
    "solid_lid",
    "basket_weave",
    "parallel_slots",
    "cross_grid",
    "radial_pattern",
)
OPEN_MECHANISMS: tuple[OpenMechanism, ...] = (
    "lift_out_prismatic",
    "hinged_flap_revolute",
)
FRAME_STYLES: tuple[FrameStyle, ...] = (
    "iron_seat_frame",
    "concrete_stone_frame",
    "flush_concrete_surround",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "cast_iron_black",
    "weathered_rust",
    "cast_graphite",
    "concrete_grey",
    "stone_grey",
    "enamel_drain_green",
)

# Palettes: >=3 colorways, every visual driven by one of these keys.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cast_iron_black": {
        "cover": (0.13, 0.13, 0.14, 1.0),
        "frame": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.22, 0.22, 0.23, 1.0),
        "shaft": (0.05, 0.05, 0.05, 1.0),
    },
    "weathered_rust": {
        "cover": (0.42, 0.24, 0.13, 1.0),
        "frame": (0.34, 0.19, 0.11, 1.0),
        "accent": (0.52, 0.31, 0.18, 1.0),
        "shaft": (0.10, 0.07, 0.05, 1.0),
    },
    "cast_graphite": {
        "cover": (0.24, 0.25, 0.27, 1.0),
        "frame": (0.18, 0.19, 0.21, 1.0),
        "accent": (0.33, 0.34, 0.36, 1.0),
        "shaft": (0.07, 0.07, 0.08, 1.0),
    },
    "concrete_grey": {
        "cover": (0.62, 0.61, 0.58, 1.0),
        "frame": (0.55, 0.54, 0.51, 1.0),
        "accent": (0.70, 0.69, 0.66, 1.0),
        "shaft": (0.18, 0.18, 0.17, 1.0),
    },
    "stone_grey": {
        "cover": (0.52, 0.52, 0.50, 1.0),
        "frame": (0.46, 0.46, 0.44, 1.0),
        "accent": (0.61, 0.61, 0.59, 1.0),
        "shaft": (0.14, 0.14, 0.14, 1.0),
    },
    "enamel_drain_green": {
        "cover": (0.17, 0.32, 0.24, 1.0),
        "frame": (0.12, 0.24, 0.18, 1.0),
        "accent": (0.28, 0.44, 0.34, 1.0),
        "shaft": (0.05, 0.10, 0.07, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Nominal geometry (metres). Square cover ~0.30 m baseline (S2 family).
# ---------------------------------------------------------------------------
_COVER_SIDE = 0.300  # square cover full side (X==Y)
_COVER_THICK = 0.028  # cover board thickness
_FRAME_TOP_BAND = 0.020  # frame top band thickness above ground (cover sits in)
_SEAT_DROP = 0.022  # how far the cover top sits below frame top (recess)
_RIM_HEIGHT = 0.006  # solid_lid raised rim height
_SHAFT_DEPTH = 0.120  # hollow throat depth below seat

# Multiplicity ranges (spec §Multiplicity). CAPPED for mesh-perf.
_N_RANGE = {
    "parallel_slots": (3, 14),  # straight slots
    "radial_pattern": (6, 20),  # radial spokes
    "cross_grid": (3, 7),  # per-side -> total n*n in [9, 49]
    "basket_weave": (3, 6),  # per-side rows -> ~n*n cells in [9, 36]
}
# Nominal (weighted toward small N).
_N_NOMINAL = {
    "parallel_slots": 8,
    "radial_pattern": 12,
    "cross_grid": 5,
    "basket_weave": 4,
}


@dataclass(frozen=True)
class ManholeCoverConfig:
    cover_outline: CoverOutline | None = None
    surface_pattern: SurfacePattern | None = None
    open_mechanism: OpenMechanism | None = None
    frame_style: FrameStyle | None = None
    slot_count: int | None = None
    palette_style: PaletteStyle = "cast_iron_black"
    cover_size_scale: float = 1.0
    cover_thick_scale: float = 1.0
    frame_wall_scale: float = 1.0
    rect_aspect: float = 1.6
    hinge_upper: float = math.radians(95.0)
    name: str = "manhole_cover"


@dataclass(frozen=True)
class ResolvedManholeCoverConfig:
    cover_outline: CoverOutline
    surface_pattern: SurfacePattern
    open_mechanism: OpenMechanism
    frame_style: FrameStyle
    slot_count: int
    palette_style: PaletteStyle
    # Concrete geometry (resolved/clamped).
    cover_x: float  # cover full X
    cover_y: float  # cover full Y
    cover_thick: float
    frame_wall: float  # frame band width (radial)
    frame_top_band: float
    frame_total_h: float
    seat_drop: float
    seat_gap: float
    rim_height: float
    shaft_depth: float
    # Derived seating heights.
    cover_rest_bottom_z: float  # cover bottom z when closed
    seat_ledge_top_z: float  # frame seat ledge top z (== cover bottom)
    lift_travel: float
    hinge_upper: float
    is_flush: bool
    name: str

    @property
    def is_round(self) -> bool:
        return self.cover_outline == "round"

    @property
    def hinge_pivot_z(self) -> float:
        """World z of the hinged-flap pivot: the cover TOP plane at rest.

        Single source (Contract 3c) for the revolute joint origin height and the
        cover-mesh authoring offset.  Pivoting on the TOP edge (not the bottom)
        is what guarantees shaft clearance: rotating the cover (authored with
        z in [-cover_thick, 0]) about this edge by any angle in (0, 180] deg
        keeps every cover point at world z >= cover_rest_bottom_z (the closed
        bottom plane == shaft top), so the swept arc can never dip into the
        shaft throat below, for the full hinge_upper range.
        """
        return self.cover_rest_bottom_z + self.cover_thick


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Procedural sampling (Contract 4): deterministic per seed.
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ManholeCoverConfig:
    rng = random.Random(seed)
    outline = rng.choice(COVER_OUTLINES)
    pattern = rng.choice(SURFACE_PATTERNS)
    mechanism = rng.choice(OPEN_MECHANISMS)
    frame = rng.choice(FRAME_STYLES)

    # Compatibility gate: radial_pattern strongly prefers a round outline.
    if pattern == "radial_pattern" and outline != "round":
        # 70% promote outline to round, else swap pattern off radial.
        if rng.random() < 0.7:
            outline = "round"
        else:
            pattern = rng.choice(("parallel_slots", "cross_grid", "basket_weave"))

    # Sample N (only when B != solid_lid). Weighted toward small N.
    slot_count: int | None = None
    if pattern != "solid_lid":
        lo, hi = _N_RANGE[pattern]
        nom = _N_NOMINAL[pattern]
        # Weighted draw: small N high freq, dense/coarse tails sparse.
        choices = list(range(lo, hi + 1))
        weights = []
        for n in choices:
            if n <= nom:
                weights.append(3.0)
            elif n <= nom + 2:
                weights.append(1.5)
            else:
                weights.append(0.6)
        slot_count = rng.choices(choices, weights=weights, k=1)[0]

    return ManholeCoverConfig(
        cover_outline=outline,
        surface_pattern=pattern,
        open_mechanism=mechanism,
        frame_style=frame,
        slot_count=slot_count,
        palette_style=rng.choice(PALETTE_STYLES),
        cover_size_scale=round(rng.uniform(0.85, 1.20), 4),
        cover_thick_scale=round(rng.uniform(0.80, 1.30), 4),
        frame_wall_scale=round(rng.uniform(0.80, 1.25), 4),
        rect_aspect=round(rng.uniform(1.3, 2.2), 4),
        hinge_upper=round(rng.uniform(math.radians(85.0), math.radians(105.0)), 4),
        name=f"seeded_manhole_cover_{seed}",
    )


def resolve_config(
    config: ManholeCoverConfig | None = None,
) -> ResolvedManholeCoverConfig:
    cfg = config or ManholeCoverConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    outline = _pick(cfg.cover_outline, COVER_OUTLINES)
    pattern = _pick(cfg.surface_pattern, SURFACE_PATTERNS)
    mechanism = _pick(cfg.open_mechanism, OPEN_MECHANISMS)
    frame_style = _pick(cfg.frame_style, FRAME_STYLES)

    # Compatibility gating (idempotent — config_from_seed already gated, but
    # resolve must also be valid when called with a hand-built config).
    if pattern == "radial_pattern" and outline != "round":
        outline = "round"
    # round outline + hinge: spec allows pivot along a chord, but to keep the
    # hinge geometry robust we degrade round+hinge to prismatic.
    if outline == "round" and mechanism == "hinged_flap_revolute":
        mechanism = "lift_out_prismatic"

    size_scale = _clamp(cfg.cover_size_scale, 0.85, 1.20)
    thick_scale = _clamp(cfg.cover_thick_scale, 0.80, 1.30)
    wall_scale = _clamp(cfg.frame_wall_scale, 0.80, 1.25)
    rect_aspect = _clamp(cfg.rect_aspect, 1.3, 2.2)
    hinge_upper = _clamp(cfg.hinge_upper, math.radians(85.0), math.radians(110.0))

    base_side = _COVER_SIDE * size_scale
    cover_x = base_side
    cover_y = base_side
    if outline == "rectangular":
        cover_x = base_side * rect_aspect

    cover_thick = _COVER_THICK * thick_scale

    # Frame band width depends on style (concrete/stone is heavier).
    if frame_style == "concrete_stone_frame":
        base_wall = 0.040
        frame_top_band = 0.030
    elif frame_style == "flush_concrete_surround":
        base_wall = 0.034
        frame_top_band = _COVER_THICK * thick_scale  # flush: top == cover top
    else:  # iron_seat_frame
        base_wall = 0.022
        frame_top_band = _FRAME_TOP_BAND
    frame_wall = base_wall * wall_scale

    # Seat gap (peripheral clearance so cover sits within opening).
    seat_gap = max(0.004, 0.012 * size_scale)

    seat_drop = _SEAT_DROP
    rim_height = _RIM_HEIGHT if pattern == "solid_lid" else 0.0
    shaft_depth = _SHAFT_DEPTH

    is_flush = frame_style == "flush_concrete_surround"

    # Seating heights. frame footprint base z=0. Anchor on a guaranteed-positive
    # seat ledge so the ledge / shaft never poke below ground (z<0) regardless of
    # cover_thick / seat_drop. The cover bottom rests on the ledge; the cover top
    # is then seat_drop below the frame top (recess), or flush with it.
    seat_ledge_top_z = 0.010  # always > 0: ledge sits above the frame base
    cover_rest_bottom_z = seat_ledge_top_z
    cover_top_z = cover_rest_bottom_z + cover_thick
    if is_flush:
        # flush surround: frame top == cover top (cover flush with ground).
        frame_total_h = cover_top_z
    else:
        # recessed: frame top sits seat_drop above the cover top.
        frame_total_h = cover_top_z + seat_drop

    # Lift travel: must clear frame top band (+ rim if solid).
    lift_travel = (frame_total_h - cover_rest_bottom_z) + 0.060 + rim_height
    lift_travel = max(lift_travel, seat_drop + rim_height + 0.040)

    slot_count = 0
    if pattern != "solid_lid":
        lo, hi = _N_RANGE[pattern]
        sc = cfg.slot_count if cfg.slot_count is not None else _N_NOMINAL[pattern]
        slot_count = int(_clamp(int(sc), lo, hi))

    return ResolvedManholeCoverConfig(
        cover_outline=outline,
        surface_pattern=pattern,
        open_mechanism=mechanism,
        frame_style=frame_style,
        slot_count=slot_count,
        palette_style=palette_style,
        cover_x=cover_x,
        cover_y=cover_y,
        cover_thick=cover_thick,
        frame_wall=frame_wall,
        frame_top_band=frame_top_band,
        frame_total_h=frame_total_h,
        seat_drop=seat_drop,
        seat_gap=seat_gap,
        rim_height=rim_height,
        shaft_depth=shaft_depth,
        cover_rest_bottom_z=cover_rest_bottom_z,
        seat_ledge_top_z=seat_ledge_top_z,
        lift_travel=lift_travel,
        hinge_upper=hinge_upper,
        is_flush=is_flush,
        name=cfg.name,
    )


# ---------------------------------------------------------------------------
# slot_choices (Contract 4 export)
# ---------------------------------------------------------------------------
def slot_choices_for_config(
    config: ManholeCoverConfig | ResolvedManholeCoverConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedManholeCoverConfig) else resolve_config(config)
    choices = [
        ("cover_outline", r.cover_outline),
        ("surface_pattern", r.surface_pattern),
        ("open_mechanism", r.open_mechanism),
        ("frame_style", r.frame_style),
    ]
    if r.surface_pattern != "solid_lid":
        choices.append(("slot_count", f"n{r.slot_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# CadQuery geometry helpers
# ---------------------------------------------------------------------------
def _outer_board(
    r: ResolvedManholeCoverConfig, sx: float, sy: float, h: float, *, z0: float = 0.0
) -> cq.Workplane:
    """A cover/frame board solid, base at z0. Round -> circle, else box."""
    if r.is_round:
        return cq.Workplane("XY", origin=(0.0, 0.0, z0)).circle(0.5 * sx).extrude(h)
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, z0))
        .rect(sx, sy)
        .extrude(h)
        .edges("|Z")
        .fillet(min(0.010, 0.18 * min(sx, sy)))
    )


def _grate_cutters(r: ResolvedManholeCoverConfig) -> list[tuple[cq.Workplane, str]]:
    """Build the loop-emitted boolean through-slot cutters for the cast pattern.

    Returns a list of (cutter_solid, name) — each cutter is subtracted from the
    cover solid (spec hard rule 3: boolean CUTS, not floating parts).  N is the
    multiplicity axis.  Cutters extend slightly beyond the cover thickness so
    the boolean cleanly punches through.
    """
    pattern = r.surface_pattern
    if pattern == "solid_lid":
        return []

    # Usable field = cover area minus a border so slots don't breach the seat.
    border = max(0.018, 0.10 * min(r.cover_x, r.cover_y))
    field_x = r.cover_x - 2.0 * border
    field_y = r.cover_y - 2.0 * border
    if field_x <= 0.0 or field_y <= 0.0:
        return []

    cut_h = r.cover_thick + 0.010  # punch fully through
    cut_z0 = -0.005
    cutters: list[tuple[cq.Workplane, str]] = []
    n = r.slot_count
    # Central keep-out: a small solid hub at the cover centre so the cover
    # bottom is solid at (0,0,0) where the lift/hinge joint origin anchors
    # (a cast central boss is typical on real grates). Cutters whose footprint
    # would breach this radius are skipped.
    keep_r = max(0.010, 0.05 * min(field_x, field_y))

    # For a round cover, clip the usable field to an inscribed disc so slots /
    # holes never cross the circular rim (which would sever the disc into
    # disconnected arcs). r_clip is the disc radius minus a rim margin.
    r_clip = 0.5 * min(r.cover_x, r.cover_y) - border if r.is_round else None

    def _round_chord_half(cx: float, default: float) -> float:
        """Half the available Y-length of a slot at column x for a round cover
        (chord of the inscribed disc), or ``default`` for non-round."""
        if r_clip is None:
            return default
        inside = r_clip * r_clip - cx * cx
        if inside <= 0.0:
            return 0.0
        return min(default, math.sqrt(inside))

    if pattern == "parallel_slots":
        # N straight slots running along Y, evenly spaced across X.
        # A central solid bar is preserved by leaving a Y-gap at the centre.
        slot_w = min(0.012, field_x / (2.0 * n))
        pitch = field_x / n
        for i in range(n):
            cx = -0.5 * field_x + (i + 0.5) * pitch
            half = _round_chord_half(cx, 0.5 * field_y)
            if half <= 0.006:
                continue  # column lies outside the round disc
            slot_len = 2.0 * half
            if abs(cx) < keep_r:
                # split this slot into two halves leaving a central solid bar.
                for sgn in (-1.0, 1.0):
                    half_len = half - keep_r
                    if half_len <= 0.004:
                        continue
                    cy = sgn * (keep_r + half_len / 2.0)
                    cc = (
                        cq.Workplane("XY", origin=(cx, cy, cut_z0))
                        .rect(slot_w, half_len)
                        .extrude(cut_h)
                    )
                    cutters.append((cc, f"grate_{len(cutters)}"))
                continue
            c = cq.Workplane("XY", origin=(cx, 0.0, cut_z0)).rect(slot_w, slot_len).extrude(cut_h)
            cutters.append((c, f"grate_{len(cutters)}"))

    elif pattern == "radial_pattern":
        # N radial slots around the centre (round outline preferred). The hub
        # radius r_in must be derived from the INNER-radius pitch, not fixed:
        # slot_w is capped from the outer circumference, so at large N on a
        # small cover the tangential pitch at a fixed r_in (2*pi*r_in/n) can
        # drop below slot_w — adjacent slot inner ends then merge into a full
        # annular cut that severs the central hub from the outer annulus
        # (disconnected-geometry islands). Enforce a solid web >= web_min
        # between adjacent inner ends: r_in >= n*(slot_w + web_min)/(2*pi).
        r_out = 0.5 * min(field_x, field_y)
        slot_w = min(0.010, (2.0 * math.pi * r_out / n) * 0.4)
        web_min = 0.005  # solid spoke web kept between adjacent slot inner ends
        r_in_hub = 0.10 * min(field_x, field_y)  # cosmetic minimum hub radius
        r_in = max(r_in_hub, n * (slot_w + web_min) / (2.0 * math.pi))
        min_slot_len = 0.020
        if r_out - r_in < min_slot_len:
            # Web-derived hub would eat the slot field: thin the slots instead
            # and re-derive the hub radius from the same web constraint.
            slot_w = max(0.004, (2.0 * math.pi * (r_out - min_slot_len) / n) - web_min)
            r_in = max(r_in_hub, n * (slot_w + web_min) / (2.0 * math.pi))
        slot_len = r_out - r_in
        rc = 0.5 * (r_in + r_out)
        for i in range(n):
            ang = i * 2.0 * math.pi / n
            cx = rc * math.cos(ang)
            cy = rc * math.sin(ang)
            c = (
                cq.Workplane("XY", origin=(cx, cy, cut_z0))
                .rect(slot_len, slot_w)
                .extrude(cut_h)
                .rotate((cx, cy, 0.0), (cx, cy, 1.0), math.degrees(ang))
            )
            cutters.append((c, f"grate_{i}"))

    elif pattern == "cross_grid":
        # n x n square through-holes (waffle).
        cell = min(field_x, field_y) / (n + 0.6 * (n + 1))
        gap = cell * 0.6
        pitch_x = field_x / n
        pitch_y = field_y / n
        idx = 0
        for iy in range(n):
            for ix in range(n):
                cx = -0.5 * field_x + (ix + 0.5) * pitch_x
                cy = -0.5 * field_y + (iy + 0.5) * pitch_y
                hole = min(cell, pitch_x - gap, pitch_y - gap)
                hole = max(hole, 0.006)
                if abs(cx) < keep_r + hole / 2.0 and abs(cy) < keep_r + hole / 2.0:
                    continue  # preserve central solid hub
                if r_clip is not None and (
                    math.hypot(abs(cx) + hole / 2.0, abs(cy) + hole / 2.0) > r_clip
                ):
                    continue  # cell would breach the round rim
                c = cq.Workplane("XY", origin=(cx, cy, cut_z0)).rect(hole, hole).extrude(cut_h)
                cutters.append((c, f"grate_{idx}"))
                idx += 1

    elif pattern == "basket_weave":
        # Staggered rounded slot array (odd rows offset half a column).
        pitch_x = field_x / n
        pitch_y = field_y / n
        slot_w = min(0.014, pitch_x * 0.45)
        slot_l = min(0.030, pitch_y * 0.7)
        idx = 0
        for iy in range(n):
            row_off = 0.5 * pitch_x if (iy % 2 == 1) else 0.0
            cols = n if (iy % 2 == 0) else (n - 1)
            for ix in range(cols):
                cx = -0.5 * field_x + (ix + 0.5) * pitch_x + row_off
                cy = -0.5 * field_y + (iy + 0.5) * pitch_y
                if abs(cx) > 0.5 * field_x or abs(cy) > 0.5 * field_y:
                    continue
                if abs(cx) < keep_r + slot_w / 2.0 and abs(cy) < keep_r + slot_l / 2.0:
                    continue  # preserve central solid hub
                if r_clip is not None and (
                    math.hypot(abs(cx) + slot_w / 2.0, abs(cy) + slot_l / 2.0) > r_clip
                ):
                    continue  # cell would breach the round rim
                c = cq.Workplane("XY", origin=(cx, cy, cut_z0)).rect(slot_w, slot_l).extrude(cut_h)
                cutters.append((c, f"grate_{idx}"))
                idx += 1

    return cutters


def _cover_mesh(r: ResolvedManholeCoverConfig, assets):
    """The cover board with the cast pattern boolean-cut through it (hard rule 3),
    authored so its BOTTOM sits at z=0 in the part frame and top at +cover_thick
    (the joint origin sits at the cover bottom rest plane == seat ledge top)."""
    # Board: bottom at z=0, top at +cover_thick (authored in joint frame so the
    # joint origin coincides with the seat-ledge contact).
    board = _outer_board(r, r.cover_x, r.cover_y, r.cover_thick, z0=0.0)
    cutters = _grate_cutters(r)
    for c, _name in cutters:
        # cutters were built spanning z in [-0.005, cover_thick+0.005]; that
        # already punches through the board (bottom 0 .. top cover_thick).
        board = board.cut(c)
    return mesh_from_cadquery(board, "cover_body", assets=assets)


def _frame_ring_mesh(r: ResolvedManholeCoverConfig, assets):
    """FIXED frame ring/surround: outer board with the opening + seat recess cut.
    Footprint base at z=0; top at frame_total_h. The seat ledge top sits at
    seat_ledge_top_z (where the cover bottom rests)."""
    frame_total_h = r.frame_total_h
    opening_x = r.cover_x + 2.0 * r.seat_gap
    opening_y = r.cover_y + 2.0 * r.seat_gap
    outer_x = opening_x + 2.0 * r.frame_wall
    outer_y = opening_y + 2.0 * r.frame_wall

    outer = _outer_board(r, outer_x, outer_y, frame_total_h, z0=0.0)

    # Upper opening (the cover recess): from seat_ledge_top_z up to the top.
    recess_h = frame_total_h - r.seat_ledge_top_z + 0.005
    recess = _outer_board(r, opening_x, opening_y, recess_h, z0=r.seat_ledge_top_z)
    frame = outer.cut(recess)

    # Throat opening below the seat ledge (smaller than opening -> seat ledge).
    throat_x = max(opening_x - 2.0 * (r.frame_wall * 0.5), 0.04)
    throat_y = max(opening_y - 2.0 * (r.frame_wall * 0.5), 0.04)
    throat = _outer_board(r, throat_x, throat_y, r.seat_ledge_top_z + 0.01, z0=-0.005)
    frame = frame.cut(throat)
    return mesh_from_cadquery(frame, "frame_ring", assets=assets), frame_total_h, throat_x, throat_y


# ---------------------------------------------------------------------------
# Part builders
# ---------------------------------------------------------------------------
def _build_frame_and_shaft(model, r, mats, *, assets):
    frame_mesh, frame_total_h, throat_x, throat_y = _frame_ring_mesh(r, assets)
    frame = model.part("frame")
    frame.visual(frame_mesh, material=mats["frame"], name="frame_ring", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "cast_graphite", "stone_grey", "enamel_drain_green"} else "concrete.smooth_cast"))

    # A real seat-ledge crest visual: a thin ANNULAR plate sitting exactly on
    # the frame ledge (between the throat and the opening), so it is fully
    # supported by frame_ring material (not floating over the throat void). Its
    # top face is the cover's mating surface. Embeds slightly into the ledge.
    opening_x = r.cover_x + 2.0 * r.seat_gap
    opening_y = r.cover_y + 2.0 * r.seat_gap
    ledge_z = r.seat_ledge_top_z
    ledge_h = 0.005
    if r.is_round:
        ledge_outer = (
            cq.Workplane("XY", origin=(0.0, 0.0, ledge_z - ledge_h))
            .circle(0.5 * opening_x)
            .extrude(ledge_h)
        )
        ledge_inner = (
            cq.Workplane("XY", origin=(0.0, 0.0, ledge_z - ledge_h - 0.002))
            .circle(0.5 * throat_x)
            .extrude(ledge_h + 0.004)
        )
    else:
        ledge_outer = (
            cq.Workplane("XY", origin=(0.0, 0.0, ledge_z - ledge_h))
            .rect(opening_x, opening_y)
            .extrude(ledge_h)
        )
        ledge_inner = (
            cq.Workplane("XY", origin=(0.0, 0.0, ledge_z - ledge_h - 0.002))
            .rect(throat_x, throat_y)
            .extrude(ledge_h + 0.004)
        )
    ledge_solid = ledge_outer.cut(ledge_inner)
    # Two thin crossing support bars spanning the throat at ledge level: gives
    # the frame real material at the centre (so the central joint origin anchors
    # on solid frame geometry) and reads as a cast cross-brace under the cover.
    bar_w = max(0.012, 0.06 * min(opening_x, opening_y))
    bar_x = (
        cq.Workplane("XY", origin=(0.0, 0.0, ledge_z - ledge_h))
        .rect(opening_x, bar_w)
        .extrude(ledge_h)
    )
    bar_y = (
        cq.Workplane("XY", origin=(0.0, 0.0, ledge_z - ledge_h))
        .rect(bar_w, opening_y)
        .extrude(ledge_h)
    )
    ledge_solid = ledge_solid.union(bar_x).union(bar_y)
    ledge_ring = mesh_from_cadquery(ledge_solid, "seat_ledge", assets=assets)
    frame.visual(ledge_ring, material=mats["accent"], name="seat_ledge", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "cast_graphite", "stone_grey", "enamel_drain_green"} else "concrete.smooth_cast"))

    frame.inertial = Inertial.from_geometry(
        Box((opening_x + 2 * r.frame_wall, opening_y + 2 * r.frame_wall, frame_total_h)),
        mass=8.0,
        origin=Origin(xyz=(0.0, 0.0, frame_total_h / 2.0)),
    )

    # Shaft: hollow throat void below the seat ledge (FIXED child). Authored in
    # the joint-local frame: top at z=0, extending DOWN by shaft_depth. The
    # FIXED joint origin (z=seat_ledge_top_z) lands the top under the seat.
    shaft = model.part("shaft")
    wall = 0.010
    bot = -r.shaft_depth
    if r.is_round:
        s_outer = (
            cq.Workplane("XY", origin=(0.0, 0.0, bot))
            .circle(0.5 * throat_x + wall)
            .extrude(r.shaft_depth)
        )
        s_inner = (
            cq.Workplane("XY", origin=(0.0, 0.0, bot + wall))
            .circle(0.5 * throat_x)
            .extrude(r.shaft_depth)
        )
    else:
        s_outer = (
            cq.Workplane("XY", origin=(0.0, 0.0, bot))
            .rect(throat_x + 2 * wall, throat_y + 2 * wall)
            .extrude(r.shaft_depth)
        )
        s_inner = (
            cq.Workplane("XY", origin=(0.0, 0.0, bot + wall))
            .rect(throat_x, throat_y)
            .extrude(r.shaft_depth)
        )
    shaft_solid = s_outer.cut(s_inner)
    # A slim central standpipe rising to the throat top (drain riser): keeps the
    # shaft top centre solid so the FIXED joint origin anchors on real geometry
    # while the throat stays visually open around it.
    post_r = max(0.008, 0.04 * min(throat_x, throat_y))
    standpipe = cq.Workplane("XY", origin=(0.0, 0.0, bot)).circle(post_r).extrude(r.shaft_depth)
    shaft_solid = shaft_solid.union(standpipe)
    shaft_mesh = mesh_from_cadquery(shaft_solid, "shaft_tube", assets=assets)
    shaft.visual(shaft_mesh, material=mats["shaft"], name="shaft_tube", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "cast_graphite", "stone_grey", "enamel_drain_green"} else "concrete.smooth_cast"))
    shaft.inertial = Inertial.from_geometry(
        Box((throat_x + 2 * wall, throat_y + 2 * wall, r.shaft_depth)),
        mass=3.0,
        origin=Origin(xyz=(0.0, 0.0, bot + r.shaft_depth / 2.0)),
    )

    # frame -> shaft FIXED. The shaft is a hollow tube (its centre at the top is
    # void), so anchor the joint origin on the shaft WALL ring at the top (x on
    # the throat half-width) where both the frame seat ledge and the shaft wall
    # have real material within tol.
    model.articulation(
        "frame_to_shaft",
        ArticulationType.FIXED,
        parent=frame,
        child=shaft,
        origin=Origin(xyz=(0.0, 0.0, r.seat_ledge_top_z)),
    )
    return frame, frame_total_h, throat_x, throat_y


def _build_cover(model, r, mats, *, assets, y_offset: float = 0.0, z_offset: float = 0.0):
    """Build the cover part. ``y_offset``/``z_offset`` shift all cover geometry
    so the (revolute) hinge edge sits at the part-local origin while the cover
    still lands centred/seated in world once the joint origin re-centres it.
    For the hinged flap the pivot is the cover TOP +Y edge (z_offset =
    -cover_thick), so the up-swing arc never dips below the seat plane."""
    cover = model.part("cover")
    # cover_body authored with bottom at z=z_offset, top at z_offset+cover_thick.
    cover.visual(
        _cover_mesh(r, assets),
        origin=Origin(xyz=(0.0, y_offset, z_offset)),
        material=mats["cover"],
        name="cover_body", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "cast_graphite", "stone_grey", "enamel_drain_green"} else "concrete.smooth_cast"),
    )

    # solid_lid optional cosmetic raised rim + single pry slot (Rule 1 visuals).
    if r.surface_pattern == "solid_lid":
        rim_z = z_offset + r.cover_thick + r.rim_height / 2.0
        if r.is_round:
            cover.visual(
                Cylinder(radius=0.49 * r.cover_x, length=r.rim_height),
                origin=Origin(xyz=(0.0, y_offset, rim_z)),
                material=mats["accent"],
                name="cover_rim", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "cast_graphite", "stone_grey", "enamel_drain_green"} else "concrete.smooth_cast"),
            )
        else:
            cover.visual(
                Box((r.cover_x * 0.96, r.cover_y * 0.96, r.rim_height)),
                origin=Origin(xyz=(0.0, y_offset, rim_z)),
                material=mats["accent"],
                name="cover_rim", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "cast_graphite", "stone_grey", "enamel_drain_green"} else "concrete.smooth_cast"),
            )
        # central pry slot (cosmetic, single, not looped) near the top.
        cover.visual(
            Box((0.05, 0.012, 0.006)),
            origin=Origin(xyz=(0.0, y_offset, z_offset + r.cover_thick - 0.003)),
            material=mats["accent"],
            name="pry_slot", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "cast_graphite", "stone_grey", "enamel_drain_green"} else "concrete.smooth_cast"),
        )

    cover.inertial = Inertial.from_geometry(
        Box((r.cover_x, r.cover_y, r.cover_thick)),
        mass=4.0,
        origin=Origin(xyz=(0.0, y_offset, z_offset + r.cover_thick / 2.0)),
    )
    return cover


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_manhole_cover(
    config: ManholeCoverConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"mhc_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    frame, _frame_total_h, _tx, _ty = _build_frame_and_shaft(model, r, mats, assets=assets)

    half_y = 0.5 * r.cover_y
    if r.open_mechanism == "lift_out_prismatic":
        cover = _build_cover(model, r, mats, assets=assets, y_offset=0.0)
        # PRISMATIC +Z. Origin at the cover rest bottom plane (== seat ledge).
        # cover_body authored bottom=0/top=+thick -> at q=0 cover bottom sits
        # at cover_rest_bottom_z. axis (0,0,1), upper = lift_travel.
        model.articulation(
            "frame_to_cover",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=cover,
            origin=Origin(xyz=(0.0, 0.0, r.cover_rest_bottom_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=200.0, velocity=0.2, lower=0.0, upper=r.lift_travel),
            mating=MatingContract(
                parent_face_geometry="seat_ledge",
                parent_face_side="positive_z",
                child_face_geometry="cover_body",
                child_face_side="negative_z",
                contact_tol=0.004,
            ),
        )
    else:
        # REVOLUTE edge flip. Pivot on the cover TOP +Y edge. The cover geometry
        # is authored shifted by (-half_y, -cover_thick) so its top +Y hinge
        # edge sits at the part-local origin; the joint origin
        # (y=+half_y, z=hinge_pivot_z) re-centres/seats it in world.
        # axis=(-1,0,0) so positive q swings the cover UP and over the +Y frame
        # edge (away from the throat). Because the pivot is the TOP edge, every
        # cover point stays at world z >= cover_rest_bottom_z (== shaft top
        # plane) for all q in (0, 180] deg — the swept arc geometrically clears
        # the shaft tube below for the whole hinge_upper range (no clamping of
        # the diversity axis needed). q=0 -> cover seated; q=upper -> flipped up.
        cover = _build_cover(
            model, r, mats, assets=assets, y_offset=-half_y, z_offset=-r.cover_thick
        )
        model.articulation(
            "frame_to_cover",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=cover,
            origin=Origin(xyz=(0.0, half_y, r.hinge_pivot_z)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=120.0, velocity=1.0, lower=0.0, upper=r.hinge_upper),
            mating=MatingContract(
                parent_face_geometry="seat_ledge",
                parent_face_side="positive_z",
                child_face_geometry="cover_body",
                child_face_side="negative_z",
                contact_tol=0.006,
            ),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_manhole_cover(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_manhole_cover(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_manhole_cover_tests(
    object_model: ArticulatedObject,
    config: ManholeCoverConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    cover = object_model.get_part("cover")

    # Seating overlap: the cover seats into the frame recess (slight embed) and
    # rests on the seat ledge crest.
    ctx.allow_overlap(
        cover,
        frame,
        reason="cover seats into the frame recess and rests on the seat ledge.",
    )
    ctx.allow_overlap(
        frame,
        object_model.get_part("shaft"),
        reason="shaft tube top abuts the frame seat ledge underside (FIXED).",
    )
    ctx.allow_isolated_part(
        cover,
        reason="cover lifts out or swings open clear of the frame and loses contact",
    )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "frame, shaft, cover present",
        {"frame", "shaft", "cover"} <= part_names,
        details=str(sorted(part_names)),
    )

    # frame -> shaft is FIXED.
    js = object_model.get_articulation("frame_to_shaft")
    ctx.check(
        "frame_to_shaft is FIXED",
        js.articulation_type == ArticulationType.FIXED,
        details=f"type={js.articulation_type}",
    )

    # DEFINING joint is non-FIXED of the expected type/axis.
    jc = object_model.get_articulation("frame_to_cover")
    if r.open_mechanism == "lift_out_prismatic":
        ctx.check(
            "cover lift is PRISMATIC +Z with upper>=seat_drop+rim",
            jc.articulation_type == ArticulationType.PRISMATIC
            and abs(jc.axis[2]) > 0.99
            and jc.motion_limits is not None
            and jc.motion_limits.upper >= r.seat_drop + r.rim_height,
            details=f"type={jc.articulation_type} axis={tuple(jc.axis)} "
            f"upper={None if jc.motion_limits is None else jc.motion_limits.upper}",
        )
    else:
        ctx.check(
            "cover hinge is REVOLUTE about -X (up-swing), upper in [85,110] deg",
            jc.articulation_type == ArticulationType.REVOLUTE
            and jc.axis[0] < -0.99
            and jc.motion_limits is not None
            and math.radians(84.0) <= jc.motion_limits.upper <= math.radians(111.0),
            details=f"type={jc.articulation_type} axis={tuple(jc.axis)} "
            f"upper={None if jc.motion_limits is None else jc.motion_limits.upper}",
        )
        # Shaft-clearance invariant: the pivot must sit on the cover TOP plane
        # (hinge_pivot_z). A bottom-edge pivot lets the opening arc swing the
        # cover down through the shaft throat (motion-QC 穿模).
        ctx.check(
            "hinge pivot sits on the cover top plane (clears shaft throat)",
            abs(jc.origin.xyz[2] - r.hinge_pivot_z) < 1e-6,
            details=f"origin_z={jc.origin.xyz[2]} hinge_pivot_z={r.hinge_pivot_z}",
        )

    # Grate is boolean-cut into the cover (one cover_body visual), not floating
    # parts: cover should have exactly one structural mesh visual (plus optional
    # solid_lid rim/pry cosmetic).
    cover_vis = [v.name for v in cover.visuals]
    ctx.check(
        "cover_body cut-mesh present (grate is boolean cuts, not parts)",
        "cover_body" in cover_vis,
        details=f"cover visuals={cover_vis}",
    )

    # Multiplicity exposed only when B != solid_lid.
    sc = dict(slot_choices_for_config(r))
    if r.surface_pattern == "solid_lid":
        ctx.check("solid_lid exposes no slot_count", "slot_count" not in sc)
    else:
        ctx.check(
            "patterned cover exposes slot_count N>=3",
            "slot_count" in sc and r.slot_count >= 3,
            details=f"N={r.slot_count}",
        )

    return ctx.report()
