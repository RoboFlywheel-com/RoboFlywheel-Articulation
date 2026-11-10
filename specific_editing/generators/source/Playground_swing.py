# SPDX-License-Identifier: Apache-2.0

"""Playground swing set modular template.

Reviewed spec:
``articraft_template_authoring/specs_modular_v1/Playground_swing.md``.

Identity = an upright, free-standing multi-seat playground swing array: a fixed
support frame holds an overhead top rail / crossbeam ~2.0-2.4 m up, and N
identical hung swing seats are evenly spaced along that rail. Each seat is one
rigid pendulum (chains / ropes / rods suspension + child seat) swinging
fore/aft about its own REVOLUTE pivot on the top rail. Seat motions are
independent (one independent REVOLUTE per seat).

Three structural slots plus a multiplicity axis:

* ``frame_type``   — red_steel_A_frame / rustic_log_frame / single_arch_frame /
  straight_H_frame.  The frame is the grounded root, exports the top pivot line
  and (per type) the pivot axis: rustic_log's crossbeam runs along Y so its
  pivot axis is (0,1,0); the A / arch / H rails run along X so their pivot axis
  is (1,0,0).
* ``suspension``   — oval_link_chains (loop-emitted oval links) / tapered_ropes
  (cone rope + wrap ring + knots) / rigid_rods (straight cylinder rods).
* ``seat_type``    — rubber_belt_seat (swept shallow-U belt) / plank_seat
  (chamfered plank + back rail) / tire_seat (horizontal torus + 4 ropes).

Multiplicity ``swing_count`` N in [1,4]; secondary sweep-only
``chain_link_count`` rides the chain loop (only when suspension=oval_link_chains).

Following ``wood_swing`` / ``playground_swing``: the frame is the grounded root
and every swing seat parts directly to ``frame`` so each REVOLUTE pivot lands on
real visible frame hinge hardware (clevis cheeks + pin + saddle).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True


FrameType = Literal[
    "red_steel_A_frame",
    "rustic_log_frame",
    "single_arch_frame",
    "straight_H_frame",
]
SuspensionModule = Literal[
    "oval_link_chains",
    "tapered_ropes",
    "rigid_rods",
]
SeatType = Literal[
    "rubber_belt_seat",
    "plank_seat",
    "tire_seat",
]
PaletteStyle = Literal[
    "red_steel_galv_rubber",
    "natural_log_tan_rope_brass",
    "arch_blue_galv",
    "green_steel_tire",
    "weathered_cedar_rope",
    "safety_yellow_steel",
]

FRAME_TYPES: tuple[FrameType, ...] = (
    "red_steel_A_frame",
    "rustic_log_frame",
    "single_arch_frame",
    "straight_H_frame",
)
SUSPENSION_MODULES: tuple[SuspensionModule, ...] = (
    "oval_link_chains",
    "tapered_ropes",
    "rigid_rods",
)
SEAT_TYPES: tuple[SeatType, ...] = (
    "rubber_belt_seat",
    "plank_seat",
    "tire_seat",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "red_steel_galv_rubber",
    "natural_log_tan_rope_brass",
    "arch_blue_galv",
    "green_steel_tire",
    "weathered_cedar_rope",
    "safety_yellow_steel",
)


# Each palette names >=3 distinct material tokens fed to every .visual(...).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "red_steel_galv_rubber": {
        "frame": (0.74, 0.09, 0.06, 1.0),
        "frame_dark": (0.30, 0.05, 0.04, 1.0),
        "steel": (0.66, 0.68, 0.70, 1.0),
        "dark": (0.09, 0.09, 0.10, 1.0),
        "seat": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.95, 0.70, 0.07, 1.0),
        "rope": (0.80, 0.64, 0.40, 1.0),
        "wood": (0.58, 0.40, 0.22, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
    },
    "natural_log_tan_rope_brass": {
        "frame": (0.55, 0.38, 0.20, 1.0),
        "frame_dark": (0.36, 0.24, 0.12, 1.0),
        "steel": (0.74, 0.60, 0.30, 1.0),
        "dark": (0.20, 0.13, 0.07, 1.0),
        "seat": (0.50, 0.34, 0.18, 1.0),
        "accent": (0.80, 0.66, 0.30, 1.0),
        "rope": (0.78, 0.63, 0.39, 1.0),
        "wood": (0.60, 0.42, 0.24, 1.0),
        "rubber": (0.12, 0.10, 0.08, 1.0),
    },
    "arch_blue_galv": {
        "frame": (0.07, 0.27, 0.66, 1.0),
        "frame_dark": (0.03, 0.10, 0.24, 1.0),
        "steel": (0.68, 0.70, 0.72, 1.0),
        "dark": (0.10, 0.11, 0.12, 1.0),
        "seat": (0.06, 0.07, 0.09, 1.0),
        "accent": (0.95, 0.68, 0.08, 1.0),
        "rope": (0.74, 0.60, 0.38, 1.0),
        "wood": (0.55, 0.38, 0.20, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
    },
    "green_steel_tire": {
        "frame": (0.13, 0.40, 0.22, 1.0),
        "frame_dark": (0.06, 0.18, 0.10, 1.0),
        "steel": (0.62, 0.64, 0.65, 1.0),
        "dark": (0.07, 0.08, 0.07, 1.0),
        "seat": (0.05, 0.05, 0.05, 1.0),
        "accent": (0.90, 0.62, 0.06, 1.0),
        "rope": (0.30, 0.30, 0.30, 1.0),
        "wood": (0.52, 0.36, 0.18, 1.0),
        "rubber": (0.035, 0.035, 0.035, 1.0),
    },
    "weathered_cedar_rope": {
        "frame": (0.46, 0.40, 0.32, 1.0),
        "frame_dark": (0.30, 0.26, 0.20, 1.0),
        "steel": (0.58, 0.56, 0.52, 1.0),
        "dark": (0.18, 0.15, 0.12, 1.0),
        "seat": (0.42, 0.30, 0.18, 1.0),
        "accent": (0.72, 0.58, 0.34, 1.0),
        "rope": (0.70, 0.58, 0.36, 1.0),
        "wood": (0.50, 0.38, 0.24, 1.0),
        "rubber": (0.14, 0.11, 0.09, 1.0),
    },
    "safety_yellow_steel": {
        "frame": (0.93, 0.74, 0.06, 1.0),
        "frame_dark": (0.40, 0.32, 0.04, 1.0),
        "steel": (0.64, 0.66, 0.67, 1.0),
        "dark": (0.10, 0.10, 0.10, 1.0),
        "seat": (0.05, 0.16, 0.55, 1.0),
        "accent": (0.85, 0.10, 0.07, 1.0),
        "rope": (0.78, 0.64, 0.40, 1.0),
        "wood": (0.58, 0.40, 0.22, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
    },
}


# swing_count weighted draw: small N high frequency (spec Multiplicity).
_SWING_COUNT_CHOICES: tuple[int, ...] = (1, 1, 2, 2, 2, 2, 3, 3, 3, 4)


@dataclass(frozen=True)
class PlaygroundSwingSetConfig:
    frame_type: FrameType = "red_steel_A_frame"
    suspension: SuspensionModule = "oval_link_chains"
    seat_type: SeatType = "rubber_belt_seat"
    palette_style: PaletteStyle = "red_steel_galv_rubber"
    swing_count: int = 2
    chain_link_count: int = 34
    swing_spacing_m: float = 0.80
    frame_scale: float = 1.0
    hanger_drop_m: float = 1.485
    swing_limit_rad: float = 1.0
    name: str = "playground_swing_set"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["red_steel_galv_rubber"])
    )


@dataclass(frozen=True)
class ResolvedPlaygroundSwingSetConfig:
    frame_type: FrameType
    suspension: SuspensionModule
    seat_type: SeatType
    palette_style: PaletteStyle
    swing_count: int
    chain_link_count: int
    frame_scale: float
    swing_limit_rad: float
    drop: float
    # Derived geometry. The top rail runs along the "rail axis": X for A / arch /
    # H frames, Y for the rustic-log crossbeam. ``along`` selects which world
    # axis is the rail axis; ``cross`` is the horizontal fore/aft axis.
    rail_along: Literal["x", "y"]
    pivot_axis: tuple[float, float, float]
    top_z: float
    pivot_z: float
    rail_length: float
    end_apex: float
    foot_half: float
    swing_centers: tuple[float, ...]
    hanger_half: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


# ---------------------------------------------------------------------------
# Procedural sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> PlaygroundSwingSetConfig:
    """Deterministic procedural sampling for every seed (seed 0 not special)."""
    rng = random.Random(seed * 2654435761 + 40503)

    frame_type = rng.choice(FRAME_TYPES)
    suspension = rng.choice(SUSPENSION_MODULES)
    seat_type = rng.choice(SEAT_TYPES)
    palette = rng.choice(PALETTE_STYLES)
    swing_count = rng.choice(_SWING_COUNT_CHOICES)

    chain_links = rng.randint(8, 40)
    spacing = round(rng.uniform(0.70, 0.95), 4)
    frame_scale = round(rng.uniform(0.92, 1.10), 4)
    drop = round(rng.uniform(1.30, 1.65), 4)
    swing_limit = round(rng.uniform(0.7, 1.0), 4)

    return PlaygroundSwingSetConfig(
        frame_type=frame_type,
        suspension=suspension,
        seat_type=seat_type,
        palette_style=palette,
        swing_count=swing_count,
        chain_link_count=chain_links,
        swing_spacing_m=spacing,
        frame_scale=frame_scale,
        hanger_drop_m=drop,
        swing_limit_rad=swing_limit,
        name=f"playground_swing_set_{seed}",
        palette=dict(PALETTES[palette]),
    )


def resolve_config(config: PlaygroundSwingSetConfig) -> ResolvedPlaygroundSwingSetConfig:
    if config.frame_type not in FRAME_TYPES:
        raise ValueError(f"Unknown frame_type {config.frame_type!r}")
    if config.suspension not in SUSPENSION_MODULES:
        raise ValueError(f"Unknown suspension {config.suspension!r}")
    if config.seat_type not in SEAT_TYPES:
        raise ValueError(f"Unknown seat_type {config.seat_type!r}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unknown palette_style {config.palette_style!r}")

    scale = _clamp(config.frame_scale, 0.92, 1.10)
    swing_count = int(_clamp(config.swing_count, 1, 4))
    chain_links = int(_clamp(config.chain_link_count, 8, 40))
    spacing = _clamp(config.swing_spacing_m, 0.70, 0.95)
    drop = _clamp(config.hanger_drop_m, 1.30, 1.65) * scale

    top_z = 2.30 * scale
    pivot_z = top_z - 0.12 * scale

    # Orientation convention: a playground swing FACES FRONT (+X). The top rail /
    # crossbeam always runs LEFT-RIGHT along world Y, the end support frames splay
    # fore/aft along world X, and each seat swings fore/aft about a left-right (Y)
    # pivot axis. This holds for every frame type (the rustic-log crossbeam already
    # ran Y; the A / arch / H rails are reoriented from X to Y here so the two end
    # frames face front instead of sideways).
    rail_along: Literal["x", "y"] = "y"
    pivot_axis = (0.0, 1.0, 0.0)

    # Rail length grows with N: equation rail = 2*end_margin + (N-1)*spacing +
    # swing_footprint (spec). swing_footprint ~ seat half-width spread.
    end_margin = 0.62 * scale
    swing_footprint = 0.78 * scale
    rail_length = 2.0 * end_margin + (swing_count - 1) * spacing + swing_footprint
    rail_length = _clamp(rail_length, 1.6 * scale, 6.0)
    end_apex = rail_length / 2.0 - 0.12 * scale
    foot_half = (0.80 if config.frame_type != "straight_H_frame" else 0.52) * scale

    # Evenly spaced seat centres along the rail: spec var_n3 formula.
    centers = tuple(
        (i - (swing_count - 1) / 2.0) * spacing for i in range(swing_count)
    )

    # full-travel floor clearance: seat lowest z at +-swing_limit must clear 0.
    # seat hangs at pivot_z - drop; at angle theta the bottom rises in z by
    # drop*(1-cos) but the seat plate centre dips. Conservatively clamp drop so
    # pivot_z - drop - 0.10 > 0.12.
    max_drop = pivot_z - 0.34
    drop = _clamp(drop, 1.05, max_drop)
    swing_limit = _clamp(config.swing_limit_rad, 0.7, 1.0)

    palette = dict(config.palette) if config.palette else dict(PALETTES[config.palette_style])

    return ResolvedPlaygroundSwingSetConfig(
        frame_type=config.frame_type,
        suspension=config.suspension,
        seat_type=config.seat_type,
        palette_style=config.palette_style,
        swing_count=swing_count,
        chain_link_count=chain_links,
        frame_scale=scale,
        swing_limit_rad=swing_limit,
        drop=drop,
        rail_along=rail_along,
        pivot_axis=pivot_axis,
        top_z=top_z,
        pivot_z=pivot_z,
        rail_length=rail_length,
        end_apex=end_apex,
        foot_half=foot_half,
        swing_centers=centers,
        hanger_half=0.20 * scale,
        name=config.name,
        palette=palette,
    )


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _mat(model: ArticulatedObject, key: str, rgba: tuple[float, float, float, float]):
    return model.material(key, rgba=rgba)


def _segment_pose(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
) -> tuple[Origin, float]:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-9:
        return Origin(xyz=start), 0.0
    yaw = math.atan2(dy, dx)
    pitch = math.acos(max(-1.0, min(1.0, dz / length)))
    return (
        Origin(
            xyz=((start[0] + end[0]) * 0.5, (start[1] + end[1]) * 0.5, (start[2] + end[2]) * 0.5),
            rpy=(0.0, pitch, yaw),
        ),
        length,
    )


def _add_tube(part, name: str, start, end, radius: float, material, *, material_class_id: str = "metal.paint_coated") -> None:
    origin, length = _segment_pose(start, end)
    part.visual(Cylinder(radius=radius, length=length), origin=origin, material=material, name=name, material_class_id=material_class_id)


def _rail_xy(r: ResolvedPlaygroundSwingSetConfig, along: float, cross: float) -> tuple[float, float]:
    """Map (along-rail, cross-rail) coords into world (x, y).

    For X-rail frames the rail axis is X, the fore/aft axis is Y.
    For the rustic-log Y-rail frame the rail axis is Y, fore/aft is X.
    """
    if r.rail_along == "x":
        return along, cross
    return cross, along


# ---------------------------------------------------------------------------
# Slot A — support frame (grounded root); exports the top pivot line
# ---------------------------------------------------------------------------
def _end_positions(r: ResolvedPlaygroundSwingSetConfig) -> tuple[float, ...]:
    """Along-rail positions of the two end structures (and a mid support for N>=4)."""
    ends = [-r.end_apex, r.end_apex]
    if r.swing_count >= 4:
        ends.insert(1, 0.0)
    return tuple(ends)


def _build_frame(model: ArticulatedObject, r: ResolvedPlaygroundSwingSetConfig) -> None:
    frame_mat = _mat(model, "frame_paint", r.palette["frame"])
    frame_dark = _mat(model, "frame_brace", r.palette["frame_dark"])
    steel = _mat(model, "pivot_steel", r.palette["steel"])

    frame = model.part("frame")
    frame.inertial = Inertial.from_geometry(
        Box((max(r.rail_length, 2.0 * r.foot_half), max(2.0 * r.foot_half, 1.0), r.top_z + 0.12)),
        mass=80.0 + 16.0 * r.swing_count,
        origin=Origin(xyz=(0.0, 0.0, (r.top_z + 0.12) * 0.5)),
    )

    # --- Top rail / crossbeam running along the rail axis ---
    rail_a0 = _rail_xy(r, -r.rail_length / 2.0, 0.0)
    rail_a1 = _rail_xy(r, r.rail_length / 2.0, 0.0)
    if r.frame_type == "rustic_log_frame":
        _add_tube(frame, "crossbeam", (*rail_a0, r.top_z), (*rail_a1, r.top_z), 0.075, frame_mat, material_class_id=("wood.bark" if r.palette_style in {"natural_log_tan_rope_brass", "weathered_cedar_rope"} else "metal.paint_coated"))
    elif r.frame_type == "single_arch_frame":
        _add_tube(frame, "top_rail", (*rail_a0, r.top_z), (*rail_a1, r.top_z), 0.050, frame_mat)
    else:
        # Box top rail (A-frame / H-frame).
        if r.rail_along == "x":
            rail_dims = (r.rail_length, 0.10, 0.10)
        else:
            rail_dims = (0.10, r.rail_length, 0.10)
        frame.visual(
            Box(rail_dims),
            origin=Origin(xyz=(0.0, 0.0, r.top_z)),
            material=frame_mat,
            name="top_rail", material_class_id=("metal.paint_coated" if r.palette_style in {"red_steel_galv_rubber", "natural_log_tan_rope_brass", "green_steel_tire", "weathered_cedar_rope", "safety_yellow_steel"} else "metal.steel_galvanized"),
        )

    ends = _end_positions(r)
    foot = r.foot_half
    for ei, a in enumerate(ends):
        if r.frame_type == "red_steel_A_frame":
            _build_a_frame_end(frame, r, ei, a, foot, frame_mat, frame_dark)
        elif r.frame_type == "rustic_log_frame":
            _build_log_frame_end(frame, r, ei, a, foot, frame_mat, frame_dark, steel)
        elif r.frame_type == "single_arch_frame":
            _build_arch_frame_end(frame, r, ei, a, foot, frame_mat, frame_dark)
        else:
            _build_h_frame_end(frame, r, ei, a, foot, frame_mat, frame_dark)

    # --- Per-swing pivot hardware on the rail (saddle bridges rail -> pin) ---
    # The hanger saddle is a tall block spanning from the top-rail underside down
    # past the pivot pin so there is a continuous support path
    # rail -> saddle -> pin -> swing hub. Clevis cheeks straddle the pin and
    # overlap both the saddle and the pin.
    rail_bottom = r.top_z - 0.05
    block_top = rail_bottom + 0.02  # bite into the rail
    block_bot = r.pivot_z - 0.045
    block_h = block_top - block_bot
    block_cz = (block_top + block_bot) * 0.5
    for index, center in enumerate(r.swing_centers):
        sx, sy = _rail_xy(r, center, 0.0)
        if r.rail_along == "x":
            sad_dims = (0.14, 0.10, block_h)
        else:
            sad_dims = (0.10, 0.14, block_h)
        frame.visual(
            Box(sad_dims),
            origin=Origin(xyz=(sx, sy, block_cz)),
            material=frame_dark,
            name=f"swing_{index}_pivot_saddle", material_class_id="metal.blackened_gunmetal",
        )
        for sgn, tag in ((-1.0, "front"), (1.0, "rear")):
            cx, cy = _rail_xy(r, center, sgn * 0.060)
            if r.rail_along == "x":
                cheek_dims = (0.090, 0.045, 0.135)
            else:
                cheek_dims = (0.045, 0.090, 0.135)
            frame.visual(
                Box(cheek_dims),
                origin=Origin(xyz=(cx, cy, r.pivot_z)),
                material=frame_mat,
                name=f"swing_{index}_{tag}_clevis_cheek", material_class_id=("metal.paint_coated" if r.palette_style in {"red_steel_galv_rubber", "arch_blue_galv", "green_steel_tire", "weathered_cedar_rope", "safety_yellow_steel"} else "metal.brass_aged"),
            )
        pin_a0 = _rail_xy(r, center - 0.16, 0.0)
        pin_a1 = _rail_xy(r, center + 0.16, 0.0)
        _add_tube(
            frame,
            f"swing_{index}_pivot_pin",
            (*pin_a0, r.pivot_z),
            (*pin_a1, r.pivot_z),
            0.018,
            steel,
        )


def _build_a_frame_end(frame, r, ei, a, foot, frame_mat, frame_dark) -> None:
    apex = _rail_xy(r, a, 0.0)
    apex_pt = (*apex, r.top_z - 0.01)
    for sgn, side in ((-1.0, "front"), (1.0, "rear")):
        fx, fy = _rail_xy(r, a, sgn * foot)
        _add_tube(frame, f"end{ei}_leg_{side}", apex_pt, (fx, fy, 0.05), 0.045, frame_mat)
        # landing foot plate
        frame.visual(
            Box((0.16, 0.16, 0.09)),
            origin=Origin(xyz=(fx, fy, 0.045)),
            material=frame_dark,
            name=f"end{ei}_foot_{side}", material_class_id="metal.blackened_gunmetal",
        )
    f0 = _rail_xy(r, a, -foot * 0.66)
    f1 = _rail_xy(r, a, foot * 0.66)
    _add_tube(frame, f"end{ei}_upper_brace", (*f0, r.top_z - 0.45), (*f1, r.top_z - 0.45), 0.026, frame_dark)
    g0 = _rail_xy(r, a, -foot - 0.06)
    g1 = _rail_xy(r, a, foot + 0.06)
    _add_tube(frame, f"end{ei}_lower_brace", (*g0, 0.16), (*g1, 0.16), 0.030, frame_dark)


def _build_h_frame_end(frame, r, ei, a, foot, frame_mat, frame_dark) -> None:
    for sgn, side in ((-1.0, "front"), (1.0, "rear")):
        px, py = _rail_xy(r, a, sgn * foot)
        _add_tube(frame, f"end{ei}_post_{side}", (px, py, 0.05), (px, py, r.top_z - 0.01), 0.050, frame_mat)
        frame.visual(
            Box((0.17, 0.17, 0.08)),
            origin=Origin(xyz=(px, py, 0.05)),
            material=frame_dark,
            name=f"end{ei}_foot_{side}", material_class_id="metal.blackened_gunmetal",
        )
    f0 = _rail_xy(r, a, -foot)
    f1 = _rail_xy(r, a, foot)
    # Top header at the rail level ties the two posts together AND bridges them
    # to the central top rail (continuous support path post -> header -> rail).
    _add_tube(frame, f"end{ei}_top_header", (*f0, r.top_z), (*f1, r.top_z), 0.040, frame_mat)
    _add_tube(frame, f"end{ei}_upper_brace", (*f0, r.top_z - 0.30), (*f1, r.top_z - 0.30), 0.028, frame_dark)
    _add_tube(frame, f"end{ei}_lower_brace", (*f0, 0.65), (*f1, 0.65), 0.026, frame_dark)


def _build_arch_frame_end(frame, r, ei, a, foot, frame_mat, frame_dark) -> None:
    # Inverted-U swept arch: foot -> apex -> foot approximated by short tube
    # segments along a half-ellipse in the (cross, z) plane at along-rail = a.
    n_seg = 8
    apex_z = r.top_z - 0.01
    pts: list[tuple[float, float, float]] = []
    for k in range(n_seg + 1):
        t = k / n_seg
        ang = math.pi * t  # 0..pi
        cross = -foot + (1.0 - math.cos(ang)) * foot  # -foot..+foot via 0
        cross = -foot * math.cos(ang)
        z = 0.06 + (apex_z - 0.06) * math.sin(ang)
        px, py = _rail_xy(r, a, cross)
        pts.append((px, py, z))
    for k in range(n_seg):
        _add_tube(frame, f"end{ei}_arch_seg_{k}", pts[k], pts[k + 1], 0.044, frame_mat)
    for sgn, side in ((-1.0, "front"), (1.0, "rear")):
        fx, fy = _rail_xy(r, a, sgn * foot)
        frame.visual(
            Box((0.17, 0.17, 0.10)),
            origin=Origin(xyz=(fx, fy, 0.05)),
            material=frame_dark,
            name=f"end{ei}_foot_{side}", material_class_id="metal.blackened_gunmetal",
        )


def _build_log_frame_end(frame, r, ei, a, foot, frame_mat, frame_dark, steel) -> None:
    # Splayed log posts (a pair) + brass finial; rail axis is Y so along=a is Y.
    apex = _rail_xy(r, a, 0.0)
    apex_pt = (*apex, r.top_z - 0.02)
    for sgn, side in ((-1.0, "front"), (1.0, "rear")):
        fx, fy = _rail_xy(r, a, sgn * foot)
        _add_tube(frame, f"end{ei}_post_{side}", apex_pt, (fx, fy, 0.06), 0.060, frame_mat)
        frame.visual(
            Box((0.18, 0.18, 0.10)),
            origin=Origin(xyz=(fx, fy, 0.05)),
            material=frame_dark,
            name=f"end{ei}_foot_{side}", material_class_id="metal.blackened_gunmetal",
        )
    # lashing band where posts meet the beam
    frame.visual(
        Sphere(radius=0.075),
        origin=Origin(xyz=apex_pt),
        material=frame_dark,
        name=f"end{ei}_lashing_band", material_class_id="organic.woven_plant_fiber",
    )
    # brass finial above the apex
    fx, fy = apex
    _add_tube(frame, f"end{ei}_finial_stem", (fx, fy, r.top_z + 0.02), (fx, fy, r.top_z + 0.14), 0.022, steel)
    frame.visual(
        Sphere(radius=0.045),
        origin=Origin(xyz=(fx, fy, r.top_z + 0.17)),
        material=steel,
        name=f"end{ei}_finial_ball", material_class_id=("metal.steel_galvanized" if r.palette_style in {"red_steel_galv_rubber", "arch_blue_galv", "green_steel_tire", "weathered_cedar_rope", "safety_yellow_steel"} else "metal.brass_aged"),
    )


# ---------------------------------------------------------------------------
# Slot B + C — one rigid pendulum part per swing seat
# ---------------------------------------------------------------------------
def _motion(r: ResolvedPlaygroundSwingSetConfig, effort: float) -> MotionLimits:
    return MotionLimits(
        effort=effort, velocity=1.8, lower=-r.swing_limit_rad, upper=r.swing_limit_rad
    )


def _local_axes(r: ResolvedPlaygroundSwingSetConfig):
    """Return (along_unit, cross_unit) as the swing part's local geometry frame.

    The swing part frame is world-aligned (joint has no rpy), so along/cross map
    the same way as the frame helper. We author seat geometry in (along, cross,
    z-from-pivot) and convert to world (x, y, z)."""

    def to_local(along: float, cross: float, z: float) -> tuple[float, float, float]:
        x, y = _rail_xy(r, along, cross)
        return (x, y, z)

    return to_local


def _make_oval_link_mesh():
    return mesh_from_geometry(
        TorusGeometry(radius=0.028, tube=0.0080, radial_segments=8, tubular_segments=14),
        "oval_chain_link_ring",
    )


def _build_chain_pair(swing, r, center, to_local, hub_top_z, seat_z, mat, link_mesh) -> None:
    """Two oval-link chains, loop-emitted, hanging from hub to the seat clamps."""
    drop = hub_top_z - seat_z
    for sgn, side in ((-1.0, "left"), (1.0, "right")):
        hanger_along = sgn * r.hanger_half
        # The two hangers should land at the two top ends along the rail/seat
        # width, not front/back of the seat.
        c0 = to_local(hanger_along, 0.0, hub_top_z)
        c1 = to_local(hanger_along, 0.0, seat_z)
        # core radius >= link torus inner radius (0.028-0.008=0.020) so every
        # threaded oval link overlaps it -> one connected chain island.
        _add_tube(swing, f"chain_{side}_core", c0, c1, 0.022, mat)
        pitch = drop / max(r.chain_link_count, 1)
        for k in range(r.chain_link_count):
            z = hub_top_z - (0.5 * pitch) - k * pitch
            lx, ly = _rail_xy(r, center + hanger_along, 0.0)
            rot_z = 0.0 if k % 2 == 0 else math.pi / 2.0
            swing.visual(
                link_mesh,
                origin=Origin(xyz=(lx, ly, z), rpy=(0.0, 0.0, rot_z)),
                material=mat,
                name=f"chain_{side}_link_{k}", material_class_id="metal.mesh_chainmail",
            )


def _build_rope_pair(swing, r, center, to_local, hub_top_z, seat_z, mat) -> None:
    """Two tapered (cone) ropes + a wrap ring per side near the hub."""
    for sgn, side in ((-1.0, "left"), (1.0, "right")):
        hanger_along = sgn * r.hanger_half
        c0 = to_local(hanger_along, 0.0, hub_top_z)
        c1 = to_local(hanger_along * 0.92, 0.0, seat_z)
        # rope column (slim, slightly tapered look via two stacked cylinders)
        origin, length = _segment_pose(c0, c1)
        swing.visual(
            Cylinder(radius=0.013, length=length * 0.55),
            origin=Origin(
                xyz=(
                    c0[0] * 0.72 + c1[0] * 0.28,
                    c0[1] * 0.72 + c1[1] * 0.28,
                    c0[2] * 0.72 + c1[2] * 0.28,
                ),
                rpy=origin.rpy,
            ),
            material=mat,
            name=f"rope_{side}_upper", material_class_id="organic.woven_plant_fiber",
        )
        swing.visual(
            Cylinder(radius=0.0095, length=length * 0.62),
            origin=Origin(
                xyz=(
                    c0[0] * 0.26 + c1[0] * 0.74,
                    c0[1] * 0.26 + c1[1] * 0.74,
                    c0[2] * 0.26 + c1[2] * 0.74,
                ),
                rpy=origin.rpy,
            ),
            material=mat,
            name=f"rope_{side}_lower", material_class_id="organic.woven_plant_fiber",
        )
        # wrap ring near the hub (snugs the beam axis)
        rx, ry = _rail_xy(r, center + hanger_along, 0.0)
        ring_rpy = (math.pi / 2.0, 0.0, 0.0) if r.rail_along == "x" else (0.0, math.pi / 2.0, 0.0)
        swing.visual(
            mesh_from_geometry(
                TorusGeometry(radius=0.030, tube=0.010, radial_segments=10, tubular_segments=20),
                f"rope_{side}_ring_mesh",
            ),
            origin=Origin(xyz=(rx, ry, hub_top_z - 0.02), rpy=ring_rpy),
            material=mat,
            name=f"rope_{side}_ring", material_class_id="organic.woven_plant_fiber",
        )


def _build_rod_pair(swing, r, center, to_local, hub_top_z, seat_z, mat) -> None:
    """Two straight rigid rods + lower clamps."""
    for sgn, side in ((-1.0, "left"), (1.0, "right")):
        hanger_along = sgn * r.hanger_half
        c0 = to_local(hanger_along, 0.0, hub_top_z)
        c1 = to_local(hanger_along, 0.0, seat_z)
        _add_tube(swing, f"rod_{side}", c0, c1, 0.016, mat)
        clamp_rpy = (0.0, math.pi / 2.0, 0.0) if r.rail_along == "x" else (math.pi / 2.0, 0.0, 0.0)
        swing.visual(
            Cylinder(radius=0.026, length=0.07),
            origin=Origin(xyz=c1, rpy=clamp_rpy),
            material=mat,
            name=f"rod_{side}_clamp", material_class_id=("metal.steel_galvanized" if r.palette_style in {"red_steel_galv_rubber", "arch_blue_galv", "green_steel_tire", "weathered_cedar_rope", "safety_yellow_steel"} else "metal.brass_aged"),
        )


def _build_belt_seat(swing, r, center, to_local, seat_z, seat_mat, dark) -> None:
    width = 2.0 * r.hanger_half + 0.16
    if r.rail_along == "x":
        seat_dims = (width, 0.22, 0.040)
        pad_dims = (width * 0.86, 0.18, 0.014)
        brk = (0.06, 0.20, 0.07)
    else:
        seat_dims = (0.22, width, 0.040)
        pad_dims = (0.18, width * 0.86, 0.014)
        brk = (0.20, 0.06, 0.07)
    cx, cy = _rail_xy(r, center, 0.0)
    swing.visual(Box(seat_dims), origin=Origin(xyz=(cx, cy, seat_z - 0.03)), material=seat_mat, name="belt_seat", material_class_id="rubber.smooth_plain")
    swing.visual(Box(pad_dims), origin=Origin(xyz=(cx, cy, seat_z - 0.006)), material=dark, name="belt_pad", material_class_id="rubber.smooth_plain")
    for sgn, side in ((-1.0, "left"), (1.0, "right")):
        bx, by = _rail_xy(r, center + sgn * r.hanger_half, 0.0)
        swing.visual(Box(brk), origin=Origin(xyz=(bx, by, seat_z)), material=dark, name=f"belt_clamp_{side}", material_class_id="metal.blackened_gunmetal")


def _build_plank_seat(swing, r, center, to_local, seat_z, wood, dark, steel) -> None:
    width = 2.0 * r.hanger_half + 0.18
    if r.rail_along == "x":
        plank_dims = (width, 0.26, 0.045)
    else:
        plank_dims = (0.26, width, 0.045)
    cx, cy = _rail_xy(r, center, 0.0)
    swing.visual(Box(plank_dims), origin=Origin(xyz=(cx, cy, seat_z - 0.022)), material=wood, name="plank_seat", material_class_id=("wood.rustic_weathered" if r.palette_style in {"natural_log_tan_rope_brass", "weathered_cedar_rope"} else "wood.natural_generic"))
    # back rail along the rail axis at the rear cross edge
    br0 = _rail_xy(r, center - width * 0.46, 0.11)
    br1 = _rail_xy(r, center + width * 0.46, 0.11)
    _add_tube(swing, "back_rail", (*br0, seat_z + 0.16), (*br1, seat_z + 0.16), 0.018, wood)
    for sgn in (-1.0, 1.0):
        p0 = _rail_xy(r, center + sgn * width * 0.40, 0.11)
        _add_tube(swing, f"back_post_{sgn:+.0f}", (*p0, seat_z), (*p0, seat_z + 0.17), 0.014, wood)
    # 4 corner brass fittings
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            fx, fy = _rail_xy(r, center + sx * width * 0.44, sy * 0.11)
            swing.visual(
                Sphere(radius=0.022),
                origin=Origin(xyz=(fx, fy, seat_z)),
                material=steel,
                name=f"corner_fitting_{sx:+.0f}_{sy:+.0f}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"red_steel_galv_rubber", "arch_blue_galv", "green_steel_tire", "weathered_cedar_rope", "safety_yellow_steel"} else "metal.brass_aged"),
            )


def _build_tire_seat(swing, r, center, to_local, seat_z, rubber, steel, accent) -> None:
    radius = 0.22 * r.frame_scale
    tube = 0.065 * r.frame_scale
    cx, cy = _rail_xy(r, center, 0.0)
    # horizontal tire (torus axis = Z, lying flat)
    swing.visual(
        mesh_from_geometry(
            TorusGeometry(radius=radius, tube=tube, radial_segments=16, tubular_segments=40),
            "tire_torus_mesh",
        ),
        origin=Origin(xyz=(cx, cy, seat_z - 0.02)),
        material=rubber,
        name="tire_shell", material_class_id="rubber.smooth_plain",
    )
    # spider plate just above tire
    swing.visual(
        Box((radius * 1.6, radius * 1.6, 0.05)),
        origin=Origin(xyz=(cx, cy, seat_z + 0.10)),
        material=steel,
        name="tire_spider_plate", material_class_id=("metal.steel_galvanized" if r.palette_style in {"red_steel_galv_rubber", "arch_blue_galv", "green_steel_tire", "weathered_cedar_rope", "safety_yellow_steel"} else "metal.brass_aged"),
    )
    # 4 converging ropes from the hub region down to 4 tire-face points
    hub_z = seat_z + 0.10
    anchors = (
        (radius * 0.70, 0.0),
        (-radius * 0.70, 0.0),
        (0.0, radius * 0.70),
        (0.0, -radius * 0.70),
    )
    for k, (aa, ac) in enumerate(anchors):
        ax, ay = _rail_xy(r, center + aa, ac)
        top = to_local(0.0, 0.0, hub_z + 0.04)
        _add_tube(swing, f"tire_rope_{k}", top, (ax, ay, seat_z), 0.011, accent)
        swing.visual(
            Sphere(radius=0.026),
            origin=Origin(xyz=(ax, ay, seat_z - 0.01)),
            material=accent,
            name=f"tire_stopper_{k}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"red_steel_galv_rubber", "arch_blue_galv", "green_steel_tire", "weathered_cedar_rope", "safety_yellow_steel"} else "metal.brass_aged"),
        )


def _build_swing(model: ArticulatedObject, r: ResolvedPlaygroundSwingSetConfig, index: int) -> str:
    steel = _mat(model, f"swing_{index}_steel", r.palette["steel"])
    dark = _mat(model, f"swing_{index}_dark", r.palette["dark"])
    seat_mat = _mat(model, f"swing_{index}_seat", r.palette["seat"])
    accent = _mat(model, f"swing_{index}_accent", r.palette["accent"])
    rope_mat = _mat(model, f"swing_{index}_rope", r.palette["rope"])
    wood = _mat(model, f"swing_{index}_wood", r.palette["wood"])
    rubber = _mat(model, f"swing_{index}_rubber", r.palette["rubber"])

    center = r.swing_centers[index]
    swing = model.part(f"swing_{index}")
    to_local = _local_axes(r)

    # The swing part frame == its REVOLUTE joint frame (origin at the pivot,
    # world-aligned axes). All swing geometry is authored in this LOCAL frame:
    # along-rail 0 at the pivot, z measured DOWN from the pivot (negative).
    # Top hub straddles the pivot pin so the REVOLUTE origin lies on geometry.
    hub_rpy = (0.0, math.pi / 2.0, 0.0) if r.rail_along == "x" else (math.pi / 2.0, 0.0, 0.0)
    swing.visual(
        Cylinder(radius=0.030, length=2.0 * r.hanger_half + 0.10),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=hub_rpy),
        material=steel,
        name="upper_hub", material_class_id=("metal.steel_galvanized" if r.palette_style in {"red_steel_galv_rubber", "arch_blue_galv", "green_steel_tire", "weathered_cedar_rope", "safety_yellow_steel"} else "metal.brass_aged"),
    )
    # Yoke bar spanning the seat width at the hub: visually exposes the two top
    # hanger ends that the suspension drops from.
    yoke0 = to_local(-r.hanger_half - 0.02, 0.0, -0.02)
    yoke1 = to_local(r.hanger_half + 0.02, 0.0, -0.02)
    _add_tube(swing, "upper_yoke_bar", yoke0, yoke1, 0.022, steel)

    hub_top_z = -0.03  # just below the pivot, where the suspension tops out
    seat_z = -r.drop

    # local==0 along-rail (pivot is the part origin); helpers take center=0.0.
    if r.suspension == "oval_link_chains":
        _build_chain_pair(swing, r, 0.0, to_local, hub_top_z, seat_z, steel, _make_oval_link_mesh())
    elif r.suspension == "tapered_ropes":
        _build_rope_pair(swing, r, 0.0, to_local, hub_top_z, seat_z, rope_mat)
    else:
        _build_rod_pair(swing, r, 0.0, to_local, hub_top_z, seat_z, steel)

    if r.seat_type == "rubber_belt_seat":
        _build_belt_seat(swing, r, 0.0, to_local, seat_z, seat_mat, dark)
    elif r.seat_type == "plank_seat":
        _build_plank_seat(swing, r, 0.0, to_local, seat_z, wood, dark, steel)
    else:
        _build_tire_seat(swing, r, 0.0, to_local, seat_z, rubber, steel, accent)

    # Lower spreader bar: bridges both suspension bottoms across the seat width
    # and embeds into the seat, so the suspension column and the seat assembly form
    # a single connected island (mirrors upper_yoke_bar; reads as a seat support).
    sb0 = to_local(-r.hanger_half, 0.0, seat_z)
    sb1 = to_local(r.hanger_half, 0.0, seat_z)
    _add_tube(swing, "seat_spreader_bar", sb0, sb1, 0.030, steel)

    px, py = _rail_xy(r, center, 0.0)
    model.articulation(
        f"swing_{index}_pivot",
        ArticulationType.REVOLUTE,
        parent="frame",
        child=swing,
        origin=Origin(xyz=(px, py, r.pivot_z)),
        axis=r.pivot_axis,
        motion_limits=_motion(r, effort=110.0),
    )
    return swing.name


# ---------------------------------------------------------------------------
# Top-level builders
# ---------------------------------------------------------------------------
def build_playground_swing_set(
    config: PlaygroundSwingSetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or PlaygroundSwingSetConfig())
    model = ArticulatedObject(name=r.name, assets=assets)
    _build_frame(model, r)
    for index in range(r.swing_count):
        _build_swing(model, r, index)
    model.meta["template_slug"] = "playground_swing_set"
    model.meta["frame_type"] = r.frame_type
    model.meta["suspension"] = r.suspension
    model.meta["seat_type"] = r.seat_type
    model.meta["swing_count"] = r.swing_count
    return model


def build_seeded_playground_swing_set(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_playground_swing_set(config_from_seed(seed), assets=assets)


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    choices: list[tuple[str, str]] = [
        ("frame_type", r.frame_type),
        ("suspension", r.suspension),
        ("seat_type", r.seat_type),
        ("swing_count", f"{r.swing_count}_swings"),
    ]
    if r.suspension == "oval_link_chains":
        choices.append(("chain_links", f"{r.chain_link_count}_links"))
    return choices


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_playground_swing_set_tests(
    object_model: ArticulatedObject,
    config: PlaygroundSwingSetConfig,
) -> TestReport:
    def _aabb_center(aabb):
        return tuple((aabb[0][i] + aabb[1][i]) * 0.5 for i in range(3))

    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_by_name = {part.name: part for part in object_model.parts}
    frame = object_model.get_part("frame")

    for index in range(r.swing_count):
        swing = part_by_name.get(f"swing_{index}")
        if swing is None:
            continue
        ctx.allow_overlap(
            frame,
            swing,
            reason="The swing upper hub is captured inside the frame clevis cheeks / saddle around the shared top pivot.",
        )
        ctx.allow_overlap(
            frame,
            swing,
            elem_a=f"swing_{index}_pivot_pin",
            elem_b="upper_hub",
            reason="The swing upper hub is intentionally captured on the frame pivot pin.",
        )
        ctx.allow_overlap(
            frame,
            swing,
            elem_a=f"swing_{index}_pivot_saddle",
            elem_b="upper_hub",
            reason="The saddle visibly supports the captured hub around the same top pivot.",
        )
        if r.suspension == "tapered_ropes":
            # wrap rings snug the crossbeam/top rail near the hub
            for side in ("left", "right"):
                rail_elem = "crossbeam" if r.frame_type == "rustic_log_frame" else "top_rail"
                ctx.allow_overlap(
                    frame,
                    swing,
                    elem_a=rail_elem,
                    elem_b=f"rope_{side}_ring",
                    reason="The rope wrap ring intentionally snugs the top rail / crossbeam around the pivot.",
                )

    ctx.check_model_valid()

    parts = {part.name for part in object_model.parts}
    joints = {joint.name: joint for joint in object_model.articulations}

    ctx.check("frame_present", "frame" in parts)
    ctx.check(
        "swing_count_matches_config",
        sum(1 for n in parts if n.startswith("swing_") and "_pivot" not in n) == r.swing_count,
        details=str(r.swing_count),
    )

    for index in range(r.swing_count):
        ctx.check(f"swing_{index}_present", f"swing_{index}" in parts)
        pivot = joints.get(f"swing_{index}_pivot")
        ctx.check(f"swing_{index}_pivot_present", pivot is not None)
        if pivot is not None:
            ctx.check(
                f"swing_{index}_pivot_is_revolute",
                pivot.articulation_type == ArticulationType.REVOLUTE,
                details=str(pivot.articulation_type),
            )
            ctx.check(
                f"swing_{index}_pivot_axis_matches_frame",
                tuple(round(a, 3) for a in pivot.axis) == r.pivot_axis,
                details=f"{pivot.axis} vs {r.pivot_axis}",
            )

    # Independent joints: each swing has its own REVOLUTE (no Mimic coupling).
    pivot_joints = [j for n, j in joints.items() if n.startswith("swing_") and n.endswith("_pivot")]
    ctx.check(
        "all_swings_independent_revolute",
        len(pivot_joints) == r.swing_count
        and all(j.mimic is None for j in pivot_joints),
        details=str(len(pivot_joints)),
    )

    suspension_elems = {
        "oval_link_chains": ("chain_left_core", "chain_right_core"),
        "tapered_ropes": ("rope_left_upper", "rope_right_upper"),
        "rigid_rods": ("rod_left", "rod_right"),
    }
    left_elem, right_elem = suspension_elems[r.suspension]
    for index in range(r.swing_count):
        swing = object_model.get_part(f"swing_{index}")
        left_box = ctx.part_element_world_aabb(swing, elem=left_elem)
        right_box = ctx.part_element_world_aabb(swing, elem=right_elem)
        if left_box is None or right_box is None:
            continue
        left_ctr = _aabb_center(left_box)
        right_ctr = _aabb_center(right_box)
        if r.rail_along == "x":
            along_delta = abs(left_ctr[0] - right_ctr[0])
            cross_delta = abs(left_ctr[1] - right_ctr[1])
        else:
            along_delta = abs(left_ctr[1] - right_ctr[1])
            cross_delta = abs(left_ctr[0] - right_ctr[0])
        ctx.check(
            f"swing_{index}_hanger_spread_runs_along_rail",
            along_delta > 0.30 * r.frame_scale and cross_delta < along_delta * 0.35,
            details=(
                f"left={tuple(round(v, 4) for v in left_ctr)}, "
                f"right={tuple(round(v, 4) for v in right_ctr)}"
            ),
        )

    # Chain copy-logic: loop-emitted oval links.
    if r.suspension == "oval_link_chains":
        swing0 = object_model.get_part("swing_0")
        link_names = [
            v.name for v in swing0.visuals if v.name and v.name.startswith("chain_left_link_")
        ]
        ctx.check(
            "chain_links_follow_loop_naming",
            len(link_names) == r.chain_link_count,
            details=f"{len(link_names)} vs {r.chain_link_count}",
        )

    return ctx.report()


__all__ = [
    "PlaygroundSwingSetConfig",
    "ResolvedPlaygroundSwingSetConfig",
    "build_playground_swing_set",
    "build_seeded_playground_swing_set",
    "config_from_seed",
    "resolve_config",
    "run_playground_swing_set_tests",
    "slot_choices_for_seed",
    "__modular__",
]
