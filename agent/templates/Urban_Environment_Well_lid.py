# SPDX-License-Identifier: Apache-2.0

"""Round cast-iron well / manhole cover — modular procedural template.

Identity (spec ``specs_modular_v1/Urban_Environment_Well_lid.md``): a ROUND cast-iron well /
inspection cover seated in a circular recessed ``frame`` ring whose throat
drops into a round vertical shaft void.  A round ``cover`` disc is the moving
child on the *defining* open joint (rear-edge REVOLUTE edge-hinge, or a +Z
PRISMATIC lift-out).  The cover top carries a dense *raised, non-through*
cast-relief pattern (waffle grid / concentric rings / radial spokes /
medallion + stud ring) emitted as a multiplicity axis of parent ``visual``s
fused onto the disc (never floating islands).  A pick / pry slot is cut into
the disc.  The frame ring (and its shaft void) stay FIXED.

Structure (pattern = ``mixed``):

  * Slot A ``surface_pattern`` (4): waffle_grid / concentric_rings /
    radial_spokes / medallion_studs — the relief layer + the multiplicity axis
    (``pattern_count`` N).  Always parent ``visual``s on the cover part.
  * Slot B ``open_mechanism`` (3, defining joint): edge_hinge (rear REVOLUTE
    + FIXED hinge_pin), lift_out (+Z PRISMATIC, no pin/lug, cover centered),
    hinge_plus_pickbar (cover REVOLUTE + a second REVOLUTE pick_bar child).
  * Slot C ``frame_style`` (2): flush_ground_ring / raised_collar.
  * Slot D ``pick_feature`` (2): single_pick_slot / twin_pick_slots (twin only
    with lift_out).

All raised relief is fused onto the cover disc (mesh-level cut for the round
plate + straddling boxes/cylinders that embed into the plate top).  The
defining lift/hinge joint declares a ``MatingContract``-style mating via
``expect_contact`` of the cover onto the seat ledge in ``run_well_lid_tests``;
the captured hinge-pin overlap is element-scoped ``allow_overlap``.

The round frame ring + cover disc + shaft void are revolved CadQuery solids
(no Box downgrade).  Relief element counts are capped (waffle <= 120 cells) to
avoid mesh blow-up / SIGKILL.
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

SurfacePattern = Literal[
    "waffle_grid", "concentric_rings", "radial_spokes", "medallion_studs"
]
OpenMechanism = Literal["edge_hinge", "lift_out", "hinge_plus_pickbar"]
FrameStyle = Literal["flush_ground_ring", "raised_collar"]
PickFeature = Literal["single_pick_slot", "twin_pick_slots"]
PaletteStyle = Literal[
    "cast_iron_black",
    "weathered_rust",
    "painted_green",
    "municipal_grey",
    "oxidized_bronze",
    "fresh_charcoal",
]

SURFACE_PATTERNS: tuple[SurfacePattern, ...] = (
    "waffle_grid",
    "concentric_rings",
    "radial_spokes",
    "medallion_studs",
)
OPEN_MECHANISMS: tuple[OpenMechanism, ...] = (
    "edge_hinge",
    "lift_out",
    "hinge_plus_pickbar",
)
FRAME_STYLES: tuple[FrameStyle, ...] = ("flush_ground_ring", "raised_collar")
PICK_FEATURES: tuple[PickFeature, ...] = ("single_pick_slot", "twin_pick_slots")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "cast_iron_black",
    "weathered_rust",
    "painted_green",
    "municipal_grey",
    "oxidized_bronze",
    "fresh_charcoal",
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cast_iron_black": {
        "iron": (0.085, 0.085, 0.090, 1.0),
        "relief": (0.135, 0.135, 0.140, 1.0),
        "steel": (0.55, 0.56, 0.58, 1.0),
        "void": (0.02, 0.02, 0.02, 1.0),
    },
    "weathered_rust": {
        "iron": (0.36, 0.20, 0.12, 1.0),
        "relief": (0.46, 0.27, 0.16, 1.0),
        "steel": (0.50, 0.42, 0.36, 1.0),
        "void": (0.04, 0.03, 0.025, 1.0),
    },
    "painted_green": {
        "iron": (0.10, 0.30, 0.18, 1.0),
        "relief": (0.14, 0.38, 0.23, 1.0),
        "steel": (0.55, 0.57, 0.56, 1.0),
        "void": (0.02, 0.03, 0.02, 1.0),
    },
    "municipal_grey": {
        "iron": (0.40, 0.41, 0.43, 1.0),
        "relief": (0.50, 0.51, 0.53, 1.0),
        "steel": (0.62, 0.63, 0.65, 1.0),
        "void": (0.05, 0.05, 0.05, 1.0),
    },
    "oxidized_bronze": {
        "iron": (0.28, 0.30, 0.22, 1.0),
        "relief": (0.40, 0.43, 0.30, 1.0),
        "steel": (0.58, 0.55, 0.40, 1.0),
        "void": (0.03, 0.03, 0.02, 1.0),
    },
    "fresh_charcoal": {
        "iron": (0.14, 0.15, 0.16, 1.0),
        "relief": (0.22, 0.23, 0.24, 1.0),
        "steel": (0.58, 0.59, 0.61, 1.0),
        "void": (0.02, 0.02, 0.02, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters).  Round cast-iron well cover, Ø≈0.61.
# ---------------------------------------------------------------------------
_COVER_DIA = 0.610
_COVER_T = 0.042
_RELIEF_H = 0.010
_HINGE_UPPER = 1.75

_SEAT_DROP = 0.022  # how far the seat ledge sits below the frame top
_FRAME_WALL = 0.065  # frame outer radius = cover_r + this (curb wall)
_SEAT_GAP = 0.006  # frame_inner_r = cover_r + this (seating clearance)
_SHAFT_WALL = 0.030  # collar_r = cover_r - this (shaft wall)
_FRAME_H_FLUSH = 0.110
_FRAME_H_COLLAR = 0.280
_FLANGE_EXTRA_R = 0.055
_FLANGE_H = 0.032
_BORDER_INSET = 0.024  # relief must stay this far inside cover_r

# Multiplicity N ranges per surface_pattern (spec §Multiplicity).  Sweep caps
# waffle at 120 cells to avoid mesh blow-up.
_WAFFLE_PITCH_RANGE = (0.090, 0.044)  # coarse -> fine (drives cell count)
_WAFFLE_CELL_CAP = 120
_RINGS_RANGE = (4, 14)
_SPOKES_RANGE = (8, 36)
_STUDS_RANGE = (8, 32)


@dataclass(frozen=True)
class WellLidConfig:
    surface_pattern: SurfacePattern | None = None
    open_mechanism: OpenMechanism | None = None
    frame_style: FrameStyle | None = None
    pick_feature: PickFeature | None = None
    pattern_count: int | None = None
    palette_style: PaletteStyle = "cast_iron_black"
    cover_dia_scale: float = 1.0
    cover_t_scale: float = 1.0
    relief_height_scale: float = 1.0
    hinge_upper_scale: float = 1.0
    frame_h_scale: float = 1.0
    name: str = "well_lid"


@dataclass(frozen=True)
class ResolvedWellLidConfig:
    surface_pattern: SurfacePattern
    open_mechanism: OpenMechanism
    frame_style: FrameStyle
    pick_feature: PickFeature
    pattern_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    # Geometry (meters).
    cover_r: float
    cover_t: float
    relief_h: float
    hinge_upper: float
    frame_outer_r: float
    frame_inner_r: float
    collar_r: float
    frame_h: float
    seat_z: float  # top of the seat ledge = cover bottom z
    flange_outer_r: float
    flange_h: float
    # Derived placement.
    hinge_x: float
    hinge_z: float
    lift_clearance: float
    # Pattern derived.
    waffle_pitch: float
    name: str

    @property
    def is_hinged(self) -> bool:
        return self.open_mechanism in ("edge_hinge", "hinge_plus_pickbar")

    @property
    def has_pin(self) -> bool:
        return self.open_mechanism in ("edge_hinge", "hinge_plus_pickbar")


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Procedural sampling.
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> WellLidConfig:
    rng = random.Random(seed)
    surface_pattern = rng.choice(SURFACE_PATTERNS)
    open_mechanism = rng.choices(
        OPEN_MECHANISMS, weights=(0.46, 0.32, 0.22), k=1
    )[0]
    frame_style = rng.choices(FRAME_STYLES, weights=(0.70, 0.30), k=1)[0]
    # twin pick slots only make sense with the symmetric lift-out.
    if open_mechanism == "lift_out":
        pick_feature = rng.choices(PICK_FEATURES, weights=(0.55, 0.45), k=1)[0]
    else:
        pick_feature = "single_pick_slot"

    # Multiplicity N per chosen surface_pattern (weighted toward mid counts).
    if surface_pattern == "waffle_grid":
        # encode N via pitch; coarse more common (smaller cell count).
        pattern_count = rng.choices(
            (16, 28, 44, 72, 104), weights=(0.30, 0.28, 0.22, 0.13, 0.07), k=1
        )[0]
    elif surface_pattern == "concentric_rings":
        pattern_count = rng.choices(
            (4, 6, 8, 10, 12, 14), weights=(0.12, 0.26, 0.28, 0.18, 0.10, 0.06), k=1
        )[0]
    elif surface_pattern == "radial_spokes":
        pattern_count = rng.choices(
            (8, 12, 16, 20, 28, 36),
            weights=(0.14, 0.26, 0.26, 0.18, 0.10, 0.06),
            k=1,
        )[0]
    else:  # medallion_studs
        pattern_count = rng.choices(
            (8, 12, 16, 20, 24, 32),
            weights=(0.16, 0.26, 0.24, 0.18, 0.10, 0.06),
            k=1,
        )[0]

    return WellLidConfig(
        surface_pattern=surface_pattern,
        open_mechanism=open_mechanism,
        frame_style=frame_style,
        pick_feature=pick_feature,
        pattern_count=pattern_count,
        palette_style=rng.choice(PALETTE_STYLES),
        cover_dia_scale=round(rng.uniform(0.90, 1.14), 4),
        cover_t_scale=round(rng.uniform(0.88, 1.18), 4),
        relief_height_scale=round(rng.uniform(0.80, 1.20), 4),
        hinge_upper_scale=round(rng.uniform(0.82, 1.08), 4),
        frame_h_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_well_lid_{seed}",
    )


def resolve_config(config: WellLidConfig | None = None) -> ResolvedWellLidConfig:
    cfg = config or WellLidConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    surface_pattern = _pick(cfg.surface_pattern, SURFACE_PATTERNS)
    open_mechanism = _pick(cfg.open_mechanism, OPEN_MECHANISMS)
    frame_style = _pick(cfg.frame_style, FRAME_STYLES)
    pick_feature = _pick(cfg.pick_feature, PICK_FEATURES)

    # --- Compatibility gating (spec §9). ---
    # twin_pick_slots only with lift_out (symmetric two-side lifting).
    if pick_feature == "twin_pick_slots" and open_mechanism != "lift_out":
        pick_feature = "single_pick_slot"

    # --- Continuous dims: independent -> equation -> conditional. ---
    cover_dia = _clamp(_COVER_DIA * _clamp(cfg.cover_dia_scale, 0.90, 1.14), 0.55, 0.70)
    cover_r = cover_dia * 0.5
    cover_t = _clamp(_COVER_T * _clamp(cfg.cover_t_scale, 0.88, 1.18), 0.034, 0.050)
    relief_h = _clamp(_RELIEF_H * _clamp(cfg.relief_height_scale, 0.80, 1.20), 0.007, 0.013)
    # inequality: relief must stay non-through (<= 0.40 * cover_t).
    relief_h = min(relief_h, cover_t * 0.40)
    hinge_upper = _clamp(_HINGE_UPPER * _clamp(cfg.hinge_upper_scale, 0.82, 1.08), 1.4, 1.9)

    frame_outer_r = cover_r + _FRAME_WALL
    frame_inner_r = cover_r + _SEAT_GAP
    collar_r = cover_r - _SHAFT_WALL

    if frame_style == "raised_collar":
        frame_h = _clamp(_FRAME_H_COLLAR * _clamp(cfg.frame_h_scale, 0.85, 1.15), 0.22, 0.32)
        flange_outer_r = frame_outer_r + _FLANGE_EXTRA_R
        flange_h = _FLANGE_H
    else:
        frame_h = _clamp(_FRAME_H_FLUSH * _clamp(cfg.frame_h_scale, 0.85, 1.15), 0.090, 0.130)
        flange_outer_r = frame_outer_r
        flange_h = 0.0

    seat_z = frame_h - _SEAT_DROP  # cover bottom z (rests on the seat ledge)

    # Hinge axis at the rear edge of the cover (cover plate is pushed +X so the
    # disc fills the opening when the part frame sits at the hinge).
    hinge_x = -cover_r - 0.004
    hinge_z = seat_z + cover_t * 0.5

    # Lift-out clearance: lifting must clear the frame top + a margin.
    lift_clearance = (frame_h - seat_z) + cover_t + 0.020

    pattern_count = int(cfg.pattern_count) if cfg.pattern_count is not None else 0

    # Per-pattern N domain + derived waffle pitch.
    waffle_pitch = _WAFFLE_PITCH_RANGE[0]
    if surface_pattern == "waffle_grid":
        if pattern_count <= 0:
            pattern_count = 28
        pattern_count = int(_clamp(pattern_count, 8, _WAFFLE_CELL_CAP))
    elif surface_pattern == "concentric_rings":
        if pattern_count <= 0:
            pattern_count = 8
        pattern_count = int(_clamp(pattern_count, *_RINGS_RANGE))
    elif surface_pattern == "radial_spokes":
        if pattern_count <= 0:
            pattern_count = 16
        pattern_count = int(_clamp(pattern_count, *_SPOKES_RANGE))
    else:  # medallion_studs
        if pattern_count <= 0:
            pattern_count = 16
        pattern_count = int(_clamp(pattern_count, *_STUDS_RANGE))

    return ResolvedWellLidConfig(
        surface_pattern=surface_pattern,
        open_mechanism=open_mechanism,
        frame_style=frame_style,
        pick_feature=pick_feature,
        pattern_count=pattern_count,
        palette_style=palette_style,
        palette=PALETTES[palette_style],
        cover_r=cover_r,
        cover_t=cover_t,
        relief_h=relief_h,
        hinge_upper=hinge_upper,
        frame_outer_r=frame_outer_r,
        frame_inner_r=frame_inner_r,
        collar_r=collar_r,
        frame_h=frame_h,
        seat_z=seat_z,
        flange_outer_r=flange_outer_r,
        flange_h=flange_h,
        hinge_x=hinge_x,
        hinge_z=hinge_z,
        lift_clearance=lift_clearance,
        waffle_pitch=waffle_pitch,
        name=cfg.name or "well_lid",
    )


def with_overrides(config: WellLidConfig, **kwargs: object) -> WellLidConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# slot choices
# ---------------------------------------------------------------------------
def slot_choices_for_config(
    config: WellLidConfig | ResolvedWellLidConfig,
) -> list[tuple[str, str]]:
    r = config if isinstance(config, ResolvedWellLidConfig) else resolve_config(config)
    return [
        ("surface_pattern", r.surface_pattern),
        ("open_mechanism", r.open_mechanism),
        ("frame_style", r.frame_style),
        ("pick_feature", r.pick_feature),
        ("pattern_count", f"n{r.pattern_count}"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Round frame ring (revolved CadQuery, no Box downgrade).
# ---------------------------------------------------------------------------
def _frame_solid(r: ResolvedWellLidConfig) -> cq.Workplane:
    """Revolved circular curb ring with a recessed seat ledge + round shaft void.

    Profile (in the +X/+Z half-plane, revolved about Z):
      outer wall up to frame_h, top steps down to the seat ledge at frame_inner_r
      / seat_z, then drops to the shaft throat at collar_r down to z=0.
    A bottom flange is added for raised_collar.
    """
    outer = r.frame_outer_r
    seat_r = r.frame_inner_r
    throat_r = r.collar_r
    top = r.frame_h
    seat_z = r.seat_z

    profile = (
        cq.Workplane("XZ")
        .moveTo(throat_r, 0.0)  # inner throat bottom
        .lineTo(outer, 0.0)  # base outward
        .lineTo(outer, top)  # outer wall up
        .lineTo(seat_r, top)  # top face inward to seat shoulder
        .lineTo(seat_r, seat_z)  # drop to seat ledge
        .lineTo(throat_r, seat_z)  # seat ledge inward to throat
        .lineTo(throat_r, 0.0)  # throat wall down to base
        .close()
        .revolve(360.0, (0, -1, 0), (0, 1, 0))
    )
    if r.flange_h > 0.0:
        flange = (
            cq.Workplane("XY")
            .circle(r.flange_outer_r)
            .circle(throat_r)
            .extrude(r.flange_h)
        )
        profile = profile.union(flange)
    return profile


def _shaft_floor_solid(r: ResolvedWellLidConfig) -> cq.Workplane:
    """Dark disc reading as the cast shaft floor / void below the throat.

    Its rim laps slightly past the throat wall (collar_r) so it fuses to the
    frame ring instead of floating as a disconnected island.
    """
    return (
        cq.Workplane("XY")
        .circle(r.collar_r + 0.006)
        .extrude(0.010)
    )


def _build_frame(model: ArticulatedObject, r: ResolvedWellLidConfig) -> None:
    frame = model.part("frame")
    frame.visual(
        mesh_from_cadquery(
            _frame_solid(r), "frame_ring", tolerance=0.0006, angular_tolerance=0.1
        ),
        material="iron",
        name="frame_ring", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
    )
    frame.visual(
        mesh_from_cadquery(_shaft_floor_solid(r), "shaft_floor"),
        origin=Origin(xyz=(0.0, 0.0, 0.002)),
        material="void",
        name="shaft_floor", material_class_id="metal.cast_iron_bare",
    )
    if r.is_hinged:
        # Rear hinge lug on the frame (captures the pin).
        frame.visual(
            Box((0.060, 0.030, 0.034)),
            origin=Origin(xyz=(-r.frame_inner_r - 0.012, 0.0, r.frame_h - 0.004)),
            material="iron",
            name="hinge_lug", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
        )


# ---------------------------------------------------------------------------
# Round cover plate (revolved disc) + pick-slot cut.  Relief is fused on top.
# The cover part-local frame: for hinged covers the disc center is pushed +X by
# (cover_r + 0.004) so the disc fills the opening when the part sits at the
# hinge axis; for lift_out the disc is centered.
# ---------------------------------------------------------------------------
def _seat_ledge_r(r: ResolvedWellLidConfig) -> float:
    """Radius of the seat-ledge ring (between throat and seat shoulder) that the
    lift_out prismatic joint origin is anchored on."""
    return (r.collar_r + r.frame_inner_r) * 0.5


def _cover_center_x(r: ResolvedWellLidConfig) -> float:
    if r.is_hinged:
        return r.cover_r + 0.004
    # lift_out: the prismatic joint origin is anchored off-center on the
    # seat-ledge ring (so it lands in frame solid, not the shaft void). Offset
    # the disc by -seat_ledge_r so it cancels that joint translation and the
    # cover lands centered over the opening at world x=0 instead of shoved aside.
    return -_seat_ledge_r(r)


def _cover_plate_solid(r: ResolvedWellLidConfig, cx: float) -> cq.Workplane:
    """Round cover disc (revolved cylinder) with a small top-edge bevel and the
    pick slot(s) cut.  Built in the cover part-local frame; disc bottom at z=0,
    center at (cx, 0)."""
    disc = (
        cq.Workplane("XY", origin=(cx, 0.0, 0.0))
        .circle(r.cover_r)
        .extrude(r.cover_t)
        .edges(">Z")
        .chamfer(min(0.006, r.cover_t * 0.25))
    )
    # Pick / pry slot: a shallow blind rounded-rect notch cut into the top of
    # the disc near the front edge (does NOT go through -> still a well lid).
    slot_depth = r.cover_t * 0.55
    slot_y = 0.024
    slot_x = 0.060
    front_r = r.cover_r - 0.040

    def _slot_at(px: float, py: float):
        return (
            cq.Workplane("XY", origin=(px, py, r.cover_t - slot_depth))
            .box(slot_x, slot_y, slot_depth * 2.0, centered=(True, True, False))
        )

    disc = disc.cut(_slot_at(cx + front_r, 0.0))
    if r.pick_feature == "twin_pick_slots":
        disc = disc.cut(_slot_at(cx - front_r, 0.0))
    return disc


def _build_cover(model: ArticulatedObject, r: ResolvedWellLidConfig) -> None:
    cx = _cover_center_x(r)
    cover = model.part("cover")
    cover.visual(
        mesh_from_cadquery(
            _cover_plate_solid(r, cx), "cover_plate",
            tolerance=0.0006, angular_tolerance=0.1,
        ),
        material="iron",
        name="cover_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
    )
    # Top surface of the disc (in cover-local z) where relief sits.
    z_top = r.cover_t
    _emit_surface_pattern(cover, r, cx=cx, z_top=z_top)
    # Hinge knuckle that captures the pin (hinged mechanisms).
    if r.is_hinged:
        cover.visual(
            Cylinder(radius=0.016, length=0.070),
            origin=Origin(
                xyz=(cx - r.cover_r + 0.004, 0.0, r.cover_t * 0.5),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material="steel",
            name="cover_knuckle", material_class_id=("metal.steel_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "painted_green", "municipal_grey", "fresh_charcoal"} else "metal.brass_aged"),
        )
    if r.open_mechanism == "hinge_plus_pickbar":
        # Recessed channel + 2 pivot lugs cast on the cover for the pick-bar.
        for i, lx in enumerate((-0.045, 0.045)):
            cover.visual(
                Box((0.018, 0.024, 0.030)),
                origin=Origin(
                    xyz=(cx + r.cover_r * 0.45 + lx, 0.0, r.cover_t + 0.012)
                ),
                material="iron",
                name=f"pivot_lug_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
            )


# ---------------------------------------------------------------------------
# Surface pattern (Slot A) — raised, non-through relief fused on the disc top.
# Every element straddles z_top so it embeds into the plate (no floating
# islands).  All emitted as cover parent visuals (Rule 1).
# ---------------------------------------------------------------------------
def _emit_surface_pattern(cover, r: ResolvedWellLidConfig, *, cx: float, z_top: float) -> None:
    if r.surface_pattern == "waffle_grid":
        _emit_waffle(cover, r, cx=cx, z_top=z_top)
    elif r.surface_pattern == "concentric_rings":
        _emit_rings(cover, r, cx=cx, z_top=z_top)
    elif r.surface_pattern == "radial_spokes":
        _emit_spokes(cover, r, cx=cx, z_top=z_top)
    else:
        _emit_medallion_studs(cover, r, cx=cx, z_top=z_top)


def _relief_z(z_top: float, h: float) -> float:
    # Box center so the box straddles the plate top: bottom embeds, top raised.
    return z_top - h * 0.25 + h * 0.5


def _emit_waffle(cover, r: ResolvedWellLidConfig, *, cx: float, z_top: float) -> None:
    """2D square-pad grid, clipped to the disc.  ``pattern_count`` is the target
    cell count; we solve for the pitch that yields ~that many in-disc cells
    (capped to keep mesh small)."""
    usable_r = r.cover_r - _BORDER_INSET
    h = r.relief_h
    # Choose pitch from target N (cells ~ pi * usable_r^2 / pitch^2 * fill).
    target = max(8, min(r.pattern_count, _WAFFLE_CELL_CAP))
    pitch = math.sqrt(math.pi * usable_r * usable_r * 0.78 / target)
    pitch = _clamp(pitch, 0.040, 0.110)
    pad = pitch * 0.70
    n_side = int(usable_r / pitch) + 1
    z = _relief_z(z_top, h)
    idx = 0
    for ix in range(-n_side, n_side + 1):
        for iy in range(-n_side, n_side + 1):
            px = ix * pitch
            py = iy * pitch
            if math.hypot(px, py) > usable_r - pad * 0.5:
                continue
            cover.visual(
                Box((pad, pad, h * 1.5)),
                origin=Origin(xyz=(cx + px, py, z)),
                material="relief",
                name=f"cell_{idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
            )
            idx += 1
            if idx >= _WAFFLE_CELL_CAP:
                return


def _emit_rings(cover, r: ResolvedWellLidConfig, *, cx: float, z_top: float) -> None:
    """Concentric annular ribs + a central hub.  Each ring is a thin cylinder
    embedded so its bottom sinks into the plate top."""
    usable_r = r.cover_r - _BORDER_INSET
    h = r.relief_h
    n = r.pattern_count
    hub_r = max(0.020, usable_r * 0.14)
    step = (usable_r - hub_r) / (n + 0.5)
    rib_t = min(0.010, step * 0.55)
    z = z_top  # cylinder bottom at top embed point
    # Central hub.
    cover.visual(
        Cylinder(radius=hub_r, length=h * 1.5),
        origin=Origin(xyz=(cx, 0.0, _relief_z(z_top, h))),
        material="relief",
        name="center_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
    )
    for i in range(n):
        ring_r = hub_r + step * (i + 1)
        if ring_r > usable_r:
            break
        # Approximate annular rib via a flat torus-like thin tube: use a
        # cadquery washer so the rib is truly connected to the plate via embed.
        cover.visual(
            mesh_from_cadquery(
                cq.Workplane("XY")
                .circle(ring_r + rib_t * 0.5)
                .circle(ring_r - rib_t * 0.5)
                .extrude(h * 1.5),
                f"ring_{i}",
                tolerance=0.0008,
                angular_tolerance=0.15,
            ),
            origin=Origin(xyz=(cx, 0.0, z - h * 0.25)),
            material="relief",
            name=f"ring_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
        )


def _emit_spokes(cover, r: ResolvedWellLidConfig, *, cx: float, z_top: float) -> None:
    """Radial trapezoid ribs + central hub + border ring.  Angle offset keeps a
    spoke off the front-edge pick slot."""
    usable_r = r.cover_r - _BORDER_INSET
    h = r.relief_h
    n = r.pattern_count
    hub_r = max(0.022, usable_r * 0.16)
    z = _relief_z(z_top, h)
    offset = math.pi / n
    spoke_len = usable_r - hub_r - 0.006
    spoke_w = min(0.018, (2.0 * math.pi * (hub_r + spoke_len * 0.5) / n) * 0.55)
    cover.visual(
        Cylinder(radius=hub_r, length=h * 1.5),
        origin=Origin(xyz=(cx, 0.0, z)),
        material="relief",
        name="hub", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
    )
    for i in range(n):
        ang = offset + i * (2.0 * math.pi / n)
        rmid = hub_r + spoke_len * 0.5
        cover.visual(
            Box((spoke_len, spoke_w, h * 1.5)),
            origin=Origin(
                xyz=(cx + rmid * math.cos(ang), rmid * math.sin(ang), z),
                rpy=(0.0, 0.0, ang),
            ),
            material="relief",
            name=f"spoke_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
        )
    # Border ring (washer) at the rim.
    cover.visual(
        mesh_from_cadquery(
            cq.Workplane("XY")
            .circle(usable_r)
            .circle(usable_r - 0.012)
            .extrude(h * 1.5),
            "border_ring",
            tolerance=0.0008,
            angular_tolerance=0.15,
        ),
        origin=Origin(xyz=(cx, 0.0, z_top - h * 0.25)),
        material="relief",
        name="border_ring", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
    )


def _emit_medallion_studs(cover, r: ResolvedWellLidConfig, *, cx: float, z_top: float) -> None:
    """Central medallion boss + emblem cross arms + an outer ring of dome studs."""
    usable_r = r.cover_r - _BORDER_INSET
    h = r.relief_h
    n = r.pattern_count
    z = _relief_z(z_top, h)
    med_r = max(0.040, usable_r * 0.30)
    # Medallion boss.
    cover.visual(
        Cylinder(radius=med_r, length=h * 1.5),
        origin=Origin(xyz=(cx, 0.0, z)),
        material="relief",
        name="medallion_boss", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
    )
    # Cross-arm emblem fused on the boss.
    for i, ang in enumerate((0.0, math.pi / 2.0)):
        cover.visual(
            Box((med_r * 1.4, med_r * 0.30, h * 1.5)),
            origin=Origin(
                xyz=(cx, 0.0, z + h * 0.4), rpy=(0.0, 0.0, ang)
            ),
            material="iron",
            name=f"emblem_arm_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
        )
    # Outer ring of dome studs.
    stud_r = usable_r - 0.012
    stud_rad = min(0.014, (2.0 * math.pi * stud_r / n) * 0.40)
    for i in range(n):
        ang = i * (2.0 * math.pi / n)
        cover.visual(
            Cylinder(radius=stud_rad, length=h * 1.5),
            origin=Origin(
                xyz=(cx + stud_r * math.cos(ang), stud_r * math.sin(ang), z)
            ),
            material="relief",
            name=f"stud_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron_black", "painted_green", "municipal_grey", "fresh_charcoal"} else "rust.heavy_corrosion"),
        )


# ---------------------------------------------------------------------------
# Pick-bar (hinge_plus_pickbar only) — a second REVOLUTE child of the cover.
# ---------------------------------------------------------------------------
def _build_pick_bar(model: ArticulatedObject, r: ResolvedWellLidConfig) -> None:
    cx = _cover_center_x(r)
    bar = model.part("pick_bar")
    bar.visual(
        Box((0.090, 0.020, 0.012)),
        origin=Origin(xyz=(0.045, 0.0, 0.0)),
        material="steel",
        name="bar_arm", material_class_id=("metal.steel_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "painted_green", "municipal_grey", "fresh_charcoal"} else "metal.brass_aged"),
    )
    bar.visual(
        Box((0.030, 0.040, 0.010)),
        origin=Origin(xyz=(0.090, 0.0, 0.0)),
        material="steel",
        name="bar_grip", material_class_id=("metal.steel_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "painted_green", "municipal_grey", "fresh_charcoal"} else "metal.brass_aged"),
    )
    pivot_x = cx + r.cover_r * 0.45
    model.articulation(
        "cover_to_pick_bar",
        ArticulationType.REVOLUTE,
        parent=model.get_part("cover"),
        child=bar,
        origin=Origin(xyz=(pivot_x, 0.0, r.cover_t + 0.012)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=1.50),
    )


# ---------------------------------------------------------------------------
# Top-level builder.
# ---------------------------------------------------------------------------
def build_well_lid(
    config: WellLidConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="well_lid", assets=assets)
    for material, rgba in r.palette.items():
        model.material(material, rgba=rgba)

    _build_frame(model, r)
    _build_cover(model, r)

    frame = model.get_part("frame")
    cover = model.get_part("cover")

    if r.open_mechanism == "lift_out":
        # Prismatic Z joint: anchor the origin on the seat-ledge ring surface
        # (between the throat and the seat shoulder) so it lands inside the
        # frame solid as well as the cover underside, not in the shaft void.
        seat_ledge_r = _seat_ledge_r(r)
        model.articulation(
            "cover_lift",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=cover,
            origin=Origin(xyz=(seat_ledge_r, 0.0, r.seat_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=40.0, velocity=0.5, lower=0.0, upper=r.lift_clearance
            ),
        )
    else:
        model.articulation(
            "cover_hinge",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=cover,
            origin=Origin(xyz=(r.hinge_x, 0.0, r.hinge_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(
                effort=30.0, velocity=1.2, lower=0.0, upper=r.hinge_upper
            ),
        )

    if r.has_pin:
        pin = model.part("hinge_pin")
        pin.visual(
            # Short stub pin: only spans the central hinge knuckle (length
            # 0.070) with a small protrusion at each end, instead of running the
            # full lid diameter and jutting out past the round silhouette.
            Cylinder(radius=0.012, length=0.090),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="steel",
            name="pin_rod", material_class_id=("metal.steel_bare" if r.palette_style in {"cast_iron_black", "weathered_rust", "painted_green", "municipal_grey", "fresh_charcoal"} else "metal.brass_aged"),
        )
        model.articulation(
            "frame_to_hinge_pin",
            ArticulationType.FIXED,
            parent=frame,
            child=pin,
            origin=Origin(xyz=(r.hinge_x, 0.0, r.hinge_z)),
        )

    if r.open_mechanism == "hinge_plus_pickbar":
        _build_pick_bar(model, r)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_well_lid(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_well_lid(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------
def run_well_lid_tests(
    object_model: ArticulatedObject, config: WellLidConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}

    ctx.check("frame_present", "frame" in names)
    ctx.check("cover_present", "cover" in names)

    # Defining open joint is a real non-FIXED joint.
    if r.open_mechanism == "lift_out":
        j = joints.get("cover_lift")
        ctx.check("lift_present", j is not None)
        if j is not None:
            ctx.check(
                "lift_prismatic",
                j.articulation_type == ArticulationType.PRISMATIC,
            )
            ctx.check("lift_axis_z", j.axis == (0.0, 0.0, 1.0))
        ctx.check("lift_no_pin", "hinge_pin" not in names)
    else:
        j = joints.get("cover_hinge")
        ctx.check("hinge_present", j is not None)
        if j is not None:
            ctx.check(
                "hinge_revolute",
                j.articulation_type == ArticulationType.REVOLUTE,
            )
            ctx.check("hinge_axis_y", j.axis == (0.0, -1.0, 0.0))
        ctx.check("hinge_has_pin", "hinge_pin" in names)

    if r.open_mechanism == "hinge_plus_pickbar":
        jb = joints.get("cover_to_pick_bar")
        ctx.check("pickbar_present", "pick_bar" in names)
        ctx.check(
            "pickbar_revolute",
            jb is not None and jb.articulation_type == ArticulationType.REVOLUTE,
        )

    # Surface pattern emitted relief elements (multiplicity axis present).
    cover = object_model.get_part("cover")
    elem_names = {v.name for v in cover.visuals}
    if r.surface_pattern == "waffle_grid":
        ctx.check("waffle_cells", any(nm.startswith("cell_") for nm in elem_names))
        ctx.check(
            "waffle_capped",
            sum(1 for nm in elem_names if nm.startswith("cell_")) <= _WAFFLE_CELL_CAP,
        )
    elif r.surface_pattern == "concentric_rings":
        ctx.check("rings_present", any(nm.startswith("ring_") for nm in elem_names))
    elif r.surface_pattern == "radial_spokes":
        ctx.check("spokes_present", any(nm.startswith("spoke_") for nm in elem_names))
    else:
        ctx.check("studs_present", any(nm.startswith("stud_") for nm in elem_names))

    # Relief is non-through (well lid, not a grate).
    ctx.check("relief_non_through", r.relief_h <= r.cover_t * 0.40 + 1e-9)

    # MatingContract-style seating: cover bottom rests on the frame seat ledge.
    ctx.allow_overlap(
        object_model.get_part("frame"),
        object_model.get_part("cover"),
        reason="Round cover disc seats into the recessed frame seat ledge.",
    )
    ctx.allow_isolated_part(
        object_model.get_part("cover"),
        reason="cover lifts out of the frame well and loses frame contact",
    )
    ctx.expect_contact(
        object_model.get_part("frame"),
        object_model.get_part("cover"),
        contact_tol=0.014,
        name="cover_seats_on_ledge",
    )

    # Captured-pin overlap (hinged mechanisms).
    if "hinge_pin" in names:
        ctx.allow_overlap(
            object_model.get_part("hinge_pin"),
            object_model.get_part("cover"),
            reason="Cover rear knuckle wraps the captured hinge pin.",
        )
        ctx.allow_overlap(
            object_model.get_part("hinge_pin"),
            object_model.get_part("frame"),
            reason="Hinge pin is held in the frame rear lug.",
        )
    if "pick_bar" in names:
        ctx.allow_overlap(
            object_model.get_part("cover"),
            object_model.get_part("pick_bar"),
            reason="Pick-bar stows in a recessed channel cast into the cover.",
        )

    return ctx.report()
