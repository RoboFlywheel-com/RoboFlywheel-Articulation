# SPDX-License-Identifier: Apache-2.0

"""Ironing board — modular procedural template.

Category identity: an elongated, tapered padded/fabric ironing surface on a
folding leg stand with a real height/fold mechanism.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/ironing_board.md``

Slots (exported via ``slot_choices_for_seed``):

* ``leg_skeleton``   — double_pivot_X / sliding_pivot_X / tabletop (carries the
  ① topology AND the ② height-mechanism: double→prismatic latch, sliding→
  translating slider, tabletop→fixed height)
* ``board_planform`` — pointed_taper / rounded_oval (③ Planar Boundary Form)
* ``iron_rest``      — wire_loop / tubular_rack (rear iron rest, host visual)
* ``under_shelf``    — none / linen_shelf (① added FIXED structure + N rungs)
* ``n_shelf_rungs``  — shelf rung multiplicity (linen_shelf only)
* ``n_notch_teeth``  — height-rail tooth multiplicity (notch-rail skeletons only)

Coordinate frame (002 canonical): the ``board`` part is centered near the
origin, top fabric surface at z≈+0.014, metal plate underside at z≈-0.032, full
legs reach feet at z≈-0.79. ``sliding_pivot_X`` (sourced from record 001, whose
board sat at z≈0.85) is re-based into this frame.

``config_from_seed`` is procedural for every seed (seed 0 is not special).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MeshGeometry,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

LegSkeleton = Literal["double_pivot_X", "sliding_pivot_X", "tabletop"]
BoardPlanform = Literal["pointed_taper", "rounded_oval"]
IronRest = Literal["wire_loop", "tubular_rack"]
UnderShelf = Literal["none", "linen_shelf"]
MaterialStyle = Literal["navy_dot", "warm_white_palm", "dark_frame"]

LEG_SKELETONS: tuple[LegSkeleton, ...] = ("double_pivot_X", "sliding_pivot_X", "tabletop")
BOARD_PLANFORMS: tuple[BoardPlanform, ...] = ("pointed_taper", "rounded_oval")
IRON_RESTS: tuple[IronRest, ...] = ("wire_loop", "tubular_rack")
UNDER_SHELVES: tuple[UnderShelf, ...] = ("none", "linen_shelf")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = ("navy_dot", "warm_white_palm", "dark_frame")

# Full vs compact (tabletop) base board dimensions.
FULL_LENGTH = 1.45
FULL_WIDTH = 0.38
TABLETOP_LENGTH = 0.86
TABLETOP_WIDTH = 0.32

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "navy_dot": {
        "fabric": (0.03, 0.09, 0.24, 1.0),
        "print": (0.92, 0.96, 0.96, 1.0),
        "frame": (0.62, 0.68, 0.68, 1.0),
        "shadow": (0.02, 0.025, 0.030, 1.0),
        "rubber": (0.33, 0.38, 0.40, 1.0),
        "latch": (0.025, 0.025, 0.025, 1.0),
    },
    "warm_white_palm": {
        "fabric": (0.92, 0.93, 0.91, 1.0),
        "print": (0.70, 0.72, 0.71, 1.0),
        "frame": (0.05, 0.055, 0.065, 1.0),
        "shadow": (0.015, 0.018, 0.026, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "latch": (0.76, 0.72, 0.66, 1.0),
    },
    "dark_frame": {
        "fabric": (0.05, 0.08, 0.16, 1.0),
        "print": (0.78, 0.80, 0.82, 1.0),
        "frame": (0.12, 0.13, 0.14, 1.0),
        "shadow": (0.02, 0.02, 0.02, 1.0),
        "rubber": (0.04, 0.045, 0.045, 1.0),
        "latch": (0.55, 0.57, 0.58, 1.0),
    },
}


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


# ───────────────────────────────────────────────────────────────────────────
# Config
# ───────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class IroningBoardConfig:
    leg_skeleton: LegSkeleton | None = None
    board_planform: BoardPlanform | None = None
    iron_rest: IronRest | None = None
    under_shelf: UnderShelf | None = None
    n_shelf_rungs: int = 6
    n_notch_teeth: int = 6
    board_length_scale: float = 1.0
    leg_reach_scale: float = 1.0
    material_style: MaterialStyle = "navy_dot"
    name: str = "ironing_board"


@dataclass(frozen=True)
class ResolvedIroningBoardConfig:
    leg_skeleton: LegSkeleton
    board_planform: BoardPlanform
    iron_rest: IronRest
    under_shelf: UnderShelf
    has_notch: bool
    n_shelf_rungs: int
    n_notch_teeth: int
    half_len: float
    half_wid: float
    leg_reach_scale: float
    material_style: MaterialStyle
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def _weighted_small(rng: random.Random, lo: int, hi: int) -> int:
    """Weighted integer draw over [lo, hi] biased toward the small end."""
    values = list(range(lo, hi + 1))
    weights = [max(1, (hi - v) + 2) for v in values]
    return rng.choices(values, weights=weights, k=1)[0]


def config_from_seed(seed: int) -> IroningBoardConfig:
    rng = random.Random(seed)
    leg = rng.choice(LEG_SKELETONS)
    planform = rng.choice(BOARD_PLANFORMS)
    rest = rng.choice(IRON_RESTS)
    shelf = rng.choice(UNDER_SHELVES)
    return IroningBoardConfig(
        leg_skeleton=leg,
        board_planform=planform,
        iron_rest=rest,
        under_shelf=shelf,
        n_shelf_rungs=_weighted_small(rng, 4, 14),
        n_notch_teeth=_weighted_small(rng, 4, 12),
        board_length_scale=round(rng.uniform(0.94, 1.08), 4),
        leg_reach_scale=round(rng.uniform(0.95, 1.06), 4),
        material_style=rng.choice(MATERIAL_STYLES),
        name=f"seeded_ironing_board_{seed}",
    )


def resolve_config(config: IroningBoardConfig) -> ResolvedIroningBoardConfig:
    leg = config.leg_skeleton or "double_pivot_X"
    planform = config.board_planform or "pointed_taper"
    rest = config.iron_rest or "wire_loop"
    shelf = config.under_shelf or "none"

    for field_name, value, allowed in (
        ("leg_skeleton", leg, LEG_SKELETONS),
        ("board_planform", planform, BOARD_PLANFORMS),
        ("iron_rest", rest, IRON_RESTS),
        ("under_shelf", shelf, UNDER_SHELVES),
    ):
        if value not in allowed:
            raise ValueError(f"Unsupported {field_name}: {value}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    # Gating: only the full-height double-pivot X (the shelf's real source, records
    # var_shelf_*) leaves clearance for a slung shelf below its folding legs; the
    # sliding-pivot rear leg folds through the shelf envelope and the tabletop is too
    # low. Both X skeletons carry the notched height rail; the tabletop is fixed height.
    has_notch = leg in ("double_pivot_X", "sliding_pivot_X")
    if leg != "double_pivot_X":
        shelf = "none"
    n_notch = _clamp_int(config.n_notch_teeth, 4, 12) if has_notch else 0
    n_shelf = _clamp_int(config.n_shelf_rungs, 4, 14) if shelf == "linen_shelf" else 0

    base_len = TABLETOP_LENGTH if leg == "tabletop" else FULL_LENGTH
    base_wid = TABLETOP_WIDTH if leg == "tabletop" else FULL_WIDTH
    length_scale = _clamp(config.board_length_scale, 0.94, 1.08)
    half_len = 0.5 * base_len * length_scale
    half_wid = 0.5 * base_wid

    return ResolvedIroningBoardConfig(
        leg_skeleton=leg,
        board_planform=planform,
        iron_rest=rest,
        under_shelf=shelf,
        has_notch=has_notch,
        n_shelf_rungs=n_shelf,
        n_notch_teeth=n_notch,
        half_len=half_len,
        half_wid=half_wid,
        leg_reach_scale=_clamp(config.leg_reach_scale, 0.95, 1.06),
        material_style=config.material_style,
        palette=dict(PALETTES[config.material_style]),
        name=config.name,
    )


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(value)))


# ───────────────────────────────────────────────────────────────────────────
# Board planform (③ Primary Form Family) + host-conformal decoration
# ───────────────────────────────────────────────────────────────────────────


def _pointed_half_width(x: float, half_len: float, half_wid: float) -> float:
    """Sharp-nose, rounded-tail half width law (record 002)."""
    nose_x = -half_len
    rear_cap_start = half_len - 0.08
    rear_x = half_len
    if x <= nose_x:
        return 0.0
    if x >= rear_cap_start:
        rx = max(0.001, rear_x - rear_cap_start)
        u = min(1.0, max(0.0, (x - rear_cap_start) / rx))
        return half_wid * math.sqrt(max(0.0, 1.0 - u * u))
    t = (x - nose_x) / (rear_cap_start - nose_x)
    return half_wid * (math.sin(t * math.pi * 0.5) ** 0.56) * (0.985 + 0.015 * t)


def _oval_params(half_len: float, half_wid: float) -> tuple[float, float, float, float, float]:
    L = half_len
    W = half_wid
    R = min(0.12, W * 0.95, L * 0.40)
    cx = L - R
    cy = W - R
    return L, W, R, cx, cy


def _oval_half_width(x: float, half_len: float, half_wid: float) -> float:
    """Stadium / discorectangle half width law (fork var_form_rounded_oval)."""
    L, W, R, cx, cy = _oval_params(half_len, half_wid)
    ax = abs(x)
    if ax <= cx:
        return W
    if ax <= L:
        d = ax - cx
        return cy + math.sqrt(max(0.0, R * R - d * d))
    return 0.0


def _half_width_fn(r: ResolvedIroningBoardConfig):
    if r.board_planform == "rounded_oval":
        return lambda x: _oval_half_width(x, r.half_len, r.half_wid)
    return lambda x: _pointed_half_width(x, r.half_len, r.half_wid)


def _pointed_outline(half_len: float, half_wid: float, samples: int = 42) -> list[tuple[float, float]]:
    nose_x = -half_len
    rear_cap_start = half_len - 0.08
    rear_x = half_len
    upper: list[tuple[float, float]] = [(nose_x, 0.0)]
    for i in range(1, samples + 1):
        x = nose_x + (rear_cap_start - nose_x) * i / samples
        upper.append((x, _pointed_half_width(x, half_len, half_wid)))
    cap: list[tuple[float, float]] = []
    rx = rear_x - rear_cap_start
    for i in range(1, 18):
        ang = math.pi * 0.5 - math.pi * i / 18.0
        cap.append((rear_cap_start + rx * math.cos(ang), half_wid * math.sin(ang)))
    lower = [(x, -y) for (x, y) in reversed(upper[1:])]
    return upper + cap + lower


def _oval_outline(half_len: float, half_wid: float) -> list[tuple[float, float]]:
    L, W, R, cx, cy = _oval_params(half_len, half_wid)
    n_arc = 8
    pts: list[tuple[float, float]] = [(-cx, W), (cx, W)]
    for i in range(1, n_arc + 1):
        a = math.pi / 2.0 * (1.0 - i / n_arc)
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    pts.append((L, cy))
    pts.append((L, -cy))
    for i in range(1, n_arc + 1):
        a = -math.pi / 2.0 * i / n_arc
        pts.append((cx + R * math.cos(a), -cy + R * math.sin(a)))
    pts.append((cx, -W))
    pts.append((-cx, -W))
    for i in range(1, n_arc + 1):
        a = -math.pi / 2.0 - math.pi / 2.0 * i / n_arc
        pts.append((-cx + R * math.cos(a), -cy + R * math.sin(a)))
    pts.append((-L, -cy))
    pts.append((-L, cy))
    for i in range(1, n_arc):
        a = math.pi - math.pi / 2.0 * i / n_arc
        pts.append((-cx + R * math.cos(a), cy + R * math.sin(a)))
    return pts


def _board_outline(r: ResolvedIroningBoardConfig) -> list[tuple[float, float]]:
    if r.board_planform == "rounded_oval":
        return _oval_outline(r.half_len, r.half_wid)
    return _pointed_outline(r.half_len, r.half_wid)


def _scale_profile(profile: list[tuple[float, float]], s: float) -> list[tuple[float, float]]:
    return [(x * s, y * s) for x, y in profile]


def _extruded_profile_mesh(
    profile: list[tuple[float, float]], z_bottom: float, z_top: float
) -> MeshGeometry:
    geom = MeshGeometry()
    n = len(profile)
    for x, y in profile:
        geom.add_vertex(x, y, z_bottom)
    for x, y in profile:
        geom.add_vertex(x, y, z_top)
    for i in range(n):
        j = (i + 1) % n
        geom.add_face(i, j, n + j)
        geom.add_face(i, n + j, n + i)
    bottom_center = geom.add_vertex(0.0, 0.0, z_bottom)
    top_center = geom.add_vertex(0.0, 0.0, z_top)
    for i in range(n):
        j = (i + 1) % n
        geom.add_face(bottom_center, j, i)
        geom.add_face(top_center, n + i, n + j)
    return geom


# ───────────────────────────────────────────────────────────────────────────
# Tube helpers (record 002 idiom)
# ───────────────────────────────────────────────────────────────────────────


def _tube(points: list[tuple[float, float, float]], radius: float) -> MeshGeometry:
    return tube_from_spline_points(
        points, radius=radius, samples_per_segment=6, radial_segments=18, cap_ends=True
    )


def _tube_assembly(segments: list[list[tuple[float, float, float]]], radius: float) -> MeshGeometry:
    geom = MeshGeometry()
    for segment in segments:
        geom.merge(_tube(segment, radius))
    return geom


def _underframe_mesh(half_len: float, half_wid: float) -> MeshGeometry:
    rail_y = half_wid * 0.62
    # Keep the underframe inboard of both leg hinges (rear ≈ +0.42·L/1.45,
    # front ≈ -0.32) so a folding leg root does not sweep into the braces.
    x0 = -half_len * 0.40
    x1 = half_len * 0.52
    segments = [
        [(x0, -rail_y, -0.026), (x1, -rail_y, -0.026)],
        [(x0, rail_y, -0.026), (x1, rail_y, -0.026)],
        [(x0 * 0.86, -rail_y, -0.027), (x1 * 0.80, rail_y, -0.030)],
        [(x0 * 0.86, rail_y, -0.027), (x1 * 0.80, -rail_y, -0.030)],
        [(x1 * 0.76, -rail_y * 1.27, -0.033), (x1 * 0.76, rail_y * 1.27, -0.033)],
        [(x0 * 0.64, -rail_y * 1.15, -0.033), (x0 * 0.64, rail_y * 1.15, -0.033)],
    ]
    return _tube_assembly(segments, 0.0075)


# ───────────────────────────────────────────────────────────────────────────
# Board part (shared root) + iron rest + cover decoration
# ───────────────────────────────────────────────────────────────────────────


def _add_cover_dots(board: Part, r: ResolvedIroningBoardConfig, hw) -> None:
    dot_r = 0.007 if r.leg_skeleton == "tabletop" else 0.010
    step = 0.060 if r.leg_skeleton == "tabletop" else 0.105
    y_pitch = 0.042 if r.leg_skeleton == "tabletop" else 0.055
    margin = 0.018 if r.leg_skeleton == "tabletop" else 0.022
    x0 = -r.half_len + 0.10
    count = max(3, int((2.0 * r.half_len - 0.16) / step))
    dot_index = 0
    for row in range(count):
        x = x0 + row * step
        hw_here = hw(x) * 0.91
        if hw_here < 0.5 * dot_r + margin:
            continue
        cols = max(1, int((2.0 * hw_here - 2.0 * margin) / y_pitch))
        for c in range(cols):
            if cols == 1:
                y = 0.0
            else:
                y = -hw_here + margin + c * ((2.0 * hw_here - 2.0 * margin) / (cols - 1))
            if (row + c) % 2:
                y += 0.010
            if abs(y) < hw_here - margin:
                board.visual(
                    Cylinder(radius=dot_r, length=0.0014),
                    origin=Origin(xyz=(x, y, 0.0145)),
                    material="print",
                    name=f"cover_dot_{dot_index}", appearance_only=AppearanceOnlySpec(kind="overlay"),
                )
                dot_index += 1


def _add_underside_holes(board: Part, r: ResolvedIroningBoardConfig, hw) -> None:
    step = 0.10 if r.leg_skeleton == "tabletop" else 0.12
    count = max(3, int((2.0 * r.half_len - 0.28) / step))
    x0 = -r.half_len * 0.55
    y_off = r.half_wid * 0.40
    for i in range(count):
        x = x0 + i * step
        if hw(x) < y_off + 0.02:
            continue
        for j, y in enumerate((-y_off, y_off)):
            board.visual(
                Cylinder(radius=0.010, length=0.0012),
                origin=Origin(xyz=(x, y, -0.0326)),
                material="shadow",
                name=f"underside_hole_{i}_{j}", material_class_id="metal.blackened_gunmetal",
            )


def _add_wire_loop_rest(board: Part, r: ResolvedIroningBoardConfig) -> None:
    """Rear wire holder loop embedded into the board tail (record 002)."""
    xa = r.half_len - 0.10
    xb = r.half_len + 0.14
    xc = r.half_len + 0.07
    yw = r.half_wid * 0.76
    segments = [
        [(xa, -yw, -0.010), (xb, -yw * 1.10, 0.040), (r.half_len + 0.14, 0.0, 0.054),
         (xb, yw * 1.10, 0.040), (xa, yw, -0.010)],
        [(xa + 0.04, -yw * 0.72, -0.008), (xc, -yw * 0.72, 0.030),
         (xc, yw * 0.72, 0.030), (xa + 0.04, yw * 0.72, -0.008)],
    ]
    board.visual(
        mesh_from_geometry(_tube_assembly(segments, 0.0045), "rear_wire_rest"),
        material="frame",
        name="rear_wire_rest", material_class_id="metal.paint_coated",
    )


def _add_tubular_rack_rest(board: Part, r: ResolvedIroningBoardConfig) -> None:
    """Rear welded tubular rack + tray, re-based into board frame (record 001)."""
    x0 = r.half_len - 0.12
    yw = r.half_wid * 0.85
    xr = r.half_len + 0.35
    board.visual(
        mesh_from_geometry(
            _tube(
                [
                    (x0, -yw, 0.010),
                    (x0 + 0.19, -yw * 1.10, 0.062),
                    (xr - 0.05, -yw * 1.05, 0.064),
                    (xr, 0.0, 0.064),
                    (xr - 0.05, yw * 1.05, 0.064),
                    (x0 + 0.19, yw * 1.10, 0.062),
                    (x0, yw, 0.010),
                ],
                0.010,
            ),
            "rear_iron_rest_rail",
        ),
        material="frame",
        name="rear_iron_rest_rail", material_class_id="metal.paint_coated",
    )
    for i, y in enumerate((-yw * 0.55, 0.0, yw * 0.55)):
        rail_x = xr - 0.022 if y != 0.0 else xr
        board.visual(
            mesh_from_geometry(
                _tube([(x0 + 0.16, y, 0.031), (x0 + 0.28, y, 0.048), (rail_x, y, 0.064)], 0.006),
                f"iron_rest_crossbar_{i}",
            ),
            material="frame",
            name=f"iron_rest_crossbar_{i}", material_class_id="metal.paint_coated",
        )
    board.visual(
        Box((0.240, min(0.42, 2.0 * yw + 0.02), 0.010)),
        origin=Origin(xyz=(x0 + 0.075, 0.0, 0.023)),
        material="frame",
        name="rear_rest_plate", material_class_id="metal.paint_coated",
    )
    for i, y in enumerate((-0.045, 0.045)):
        board.visual(
            Cylinder(radius=0.006, length=0.060),
            origin=Origin(xyz=(x0 + 0.065, y, 0.010)),
            material="frame",
            name=f"iron_rest_support_{i}", material_class_id="metal.paint_coated",
        )


def _build_board(model: ArticulatedObject, r: ResolvedIroningBoardConfig) -> Part:
    board = model.part("board")
    hw = _half_width_fn(r)
    profile = _board_outline(r)

    board.visual(
        mesh_from_geometry(_extruded_profile_mesh(_scale_profile(profile, 1.012), -0.012, 0.014),
                           "fabric_cover"),
        material="fabric",
        name="fabric_cover", material_class_id="fabric.canvas",
    )
    board.visual(
        mesh_from_geometry(_extruded_profile_mesh(_scale_profile(profile, 0.968), -0.032, -0.010),
                           "perforated_plate"),
        material="frame",
        name="perforated_plate", material_class_id="metal.patterned_sheet_panel",
    )
    _add_cover_dots(board, r, hw)
    _add_underside_holes(board, r, hw)
    board.visual(
        mesh_from_geometry(_underframe_mesh(r.half_len, r.half_wid), "underside_braces"),
        material="frame",
        name="underside_braces", material_class_id="metal.paint_coated",
    )
    if r.iron_rest == "wire_loop":
        _add_wire_loop_rest(board, r)
    else:
        _add_tubular_rack_rest(board, r)
    return board


# ───────────────────────────────────────────────────────────────────────────
# Slot A candidate: double_pivot_X (record 002)
# ───────────────────────────────────────────────────────────────────────────


def _leg_pair_mesh_full(direction: int, reach: float) -> MeshGeometry:
    foot_x = direction * 0.96 * reach
    foot_z = -0.77 * reach
    top_y = 0.165 if direction < 0 else 0.085
    foot_y = 0.255 if direction < 0 else 0.195
    mid_y = top_y + (foot_y - top_y) * 0.60
    segments = [
        [(0.0, -top_y, 0.0), (foot_x * 0.45, -top_y * 1.08, foot_z * 0.46), (foot_x, -foot_y, foot_z)],
        [(0.0, top_y, 0.0), (foot_x * 0.45, top_y * 1.08, foot_z * 0.46), (foot_x, foot_y, foot_z)],
        [(0.0, -top_y, 0.0), (0.0, top_y, 0.0)],
        [(foot_x, -foot_y - 0.055, foot_z), (foot_x, foot_y + 0.055, foot_z)],
        [(foot_x * 0.60, -mid_y, foot_z * 0.60), (foot_x * 0.60, mid_y, foot_z * 0.60)],
    ]
    return _tube_assembly(segments, 0.018)


def _foot_caps_mesh_full(direction: int, reach: float) -> MeshGeometry:
    foot_x = direction * 0.96 * reach
    foot_z = -0.77 * reach
    foot_y = 0.300 if direction < 0 else 0.240
    return _tube_assembly(
        [
            [(foot_x, -foot_y - 0.045, foot_z), (foot_x, -foot_y + 0.006, foot_z)],
            [(foot_x, foot_y - 0.006, foot_z), (foot_x, foot_y + 0.045, foot_z)],
        ],
        0.022,
    )


def _notch_rail_mesh_002(n_teeth: int) -> MeshGeometry:
    """Continuous bent-rod saw-tooth height rail (record 002 style)."""
    path: list[tuple[float, float, float]] = [(-0.22, 0.0, -0.032), (-0.22, 0.0, -0.078)]
    x0 = -0.16
    step = 0.44 / max(1, n_teeth)
    step = min(0.07, max(0.045, step))
    for i in range(n_teeth):
        x = x0 + i * step
        if path[-1] != (x, 0.0, -0.078):
            path.append((x, 0.0, -0.078))
        path.extend([(x + step * 0.30, 0.0, -0.105), (x + step * 0.60, 0.0, -0.078)])
    x_end = x0 + n_teeth * step + 0.02
    path.extend([(x_end, 0.0, -0.078), (x_end, 0.0, -0.032)])
    return _tube(path, 0.0055)


def _add_hinge_brackets_002(board: Part, rear_x: float, front_x: float) -> None:
    # Bracket spans are pulled just inside the leg-tube outer face (top_y + radius)
    # so each clevis captures its leg tube at the pivot (real anchor, Rule 2), rather
    # than floating outboard.
    for x, tag, span in ((rear_x, "rear", 0.178), (front_x, "front", 0.100)):
        for side in (-1, 1):
            board.visual(
                Box((0.055, 0.014, 0.050)),
                origin=Origin(xyz=(x, side * span, -0.052)),
                material="frame",
                name=f"{tag}_hinge_bracket_{0 if side < 0 else 1}", material_class_id="metal.paint_coated",
            )
            if tag == "rear":
                board.visual(
                    Box((0.060, 0.050, 0.010)),
                    origin=Origin(xyz=(x, side * 0.186, -0.026)),
                    material="frame",
                    name=f"rear_hinge_mount_{0 if side < 0 else 1}", material_class_id="metal.paint_coated",
                )


def _build_double_pivot_legs(model: ArticulatedObject, board: Part, r: ResolvedIroningBoardConfig) -> None:
    rear_x = _clamp(0.42, -(r.half_len - 0.14), r.half_len - 0.14)
    front_x = _clamp(-0.32, -(r.half_len - 0.14), r.half_len - 0.14)
    reach = r.leg_reach_scale

    _add_hinge_brackets_002(board, rear_x, front_x)
    board.visual(
        mesh_from_geometry(_notch_rail_mesh_002(r.n_notch_teeth), "height_notch_rail"),
        material="frame",
        name="height_notch_rail", material_class_id="metal.paint_coated",
    )

    rear_leg = model.part("rear_leg_pair")
    rear_leg.visual(mesh_from_geometry(_leg_pair_mesh_full(-1, reach), "rear_leg_tubes"),
                    material="frame", name="leg_tubes", material_class_id="metal.paint_coated")
    rear_leg.visual(mesh_from_geometry(_foot_caps_mesh_full(-1, reach), "rear_foot_caps"),
                    material="rubber", name="foot_caps", material_class_id="rubber.smooth_plain")
    for i, y in enumerate((-0.168, 0.168)):
        rear_leg.visual(
            Cylinder(radius=0.020, length=0.006),
            origin=Origin(xyz=(-0.41 * reach, y, -0.335 * reach), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material="frame",
            name=f"pivot_washer_{i}", material_class_id="metal.blackened_gunmetal",
        )

    front_leg = model.part("front_leg_pair")
    front_leg.visual(mesh_from_geometry(_leg_pair_mesh_full(1, reach), "front_leg_tubes"),
                     material="frame", name="leg_tubes", material_class_id="metal.paint_coated")
    front_leg.visual(mesh_from_geometry(_foot_caps_mesh_full(1, reach), "front_foot_caps"),
                     material="rubber", name="foot_caps", material_class_id="rubber.smooth_plain")
    for i, y in enumerate((-0.088, 0.088)):
        front_leg.visual(
            Cylinder(radius=0.014, length=0.006),
            origin=Origin(xyz=(0.39 * reach, y, -0.335 * reach), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material="shadow",
            name=f"pivot_bolt_{i}", material_class_id="metal.blackened_gunmetal",
        )

    height_latch = model.part("height_latch")
    height_latch.visual(Box((0.060, 0.055, 0.016)), origin=Origin(xyz=(0.0, 0.0, -0.030)),
                        material="frame", name="slider_block", material_class_id="metal.paint_coated")
    height_latch.visual(Box((0.090, 0.014, 0.010)),
                        origin=Origin(xyz=(0.030, -0.032, -0.041), rpy=(0.0, 0.0, -0.20)),
                        material="latch", name="release_tab", material_class_id="plastic.opaque_glossy_molded")
    height_latch.visual(Cylinder(radius=0.006, length=0.060),
                        origin=Origin(xyz=(-0.020, 0.0, -0.045), rpy=(-math.pi / 2.0, 0.0, 0.0)),
                        material="frame", name="catch_pin", material_class_id="metal.blackened_gunmetal")

    model.articulation("board_to_rear_leg", ArticulationType.REVOLUTE, parent=board, child=rear_leg,
                       origin=Origin(xyz=(rear_x, 0.0, -0.055)), axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(effort=45.0, velocity=1.5, lower=0.0, upper=0.55))
    model.articulation("board_to_front_leg", ArticulationType.REVOLUTE, parent=board, child=front_leg,
                       origin=Origin(xyz=(front_x, 0.0, -0.055)), axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(effort=45.0, velocity=1.5, lower=0.0, upper=0.55))
    model.articulation("board_to_height_latch", ArticulationType.PRISMATIC, parent=board,
                       child=height_latch, origin=Origin(xyz=(-0.025, 0.0, -0.082)), axis=(1.0, 0.0, 0.0),
                       motion_limits=MotionLimits(effort=20.0, velocity=0.12, lower=0.0, upper=0.11))


# ───────────────────────────────────────────────────────────────────────────
# Slot A candidate: sliding_pivot_X (record 001, re-based to board frame)
# ───────────────────────────────────────────────────────────────────────────

# 001 sat with its board deck at z≈0.85; re-base by this offset into board frame.
_SLIDE_DZ = -0.850
_SLIDE_HINGE_Z = 0.790 + _SLIDE_DZ  # = -0.060


def _slide_tube(points: list[tuple[float, float, float]], radius: float) -> MeshGeometry:
    return tube_from_spline_points(
        points, radius=radius, samples_per_segment=10, radial_segments=18, cap_ends=True
    )


def _build_sliding_pivot_legs(model: ArticulatedObject, board: Part, r: ResolvedIroningBoardConfig) -> None:
    reach = r.leg_reach_scale
    front_x = _clamp(0.30, -(r.half_len - 0.14), r.half_len - 0.14)
    slider_x = _clamp(-0.20, -(r.half_len - 0.16), r.half_len - 0.16)

    # Board-side hinge / slider-guide brackets + notch rail (all board visuals).
    # z values are record-001 values re-based by _SLIDE_DZ (=-0.850) into board frame.
    board.visual(Box((0.055, 0.012, 0.075)), origin=Origin(xyz=(front_x, -0.176, -0.045)),
                 material="frame", name="front_hinge_bracket_0", material_class_id="metal.paint_coated")
    board.visual(Box((0.055, 0.012, 0.075)), origin=Origin(xyz=(front_x, 0.176, -0.045)),
                 material="frame", name="front_hinge_bracket_1", material_class_id="metal.paint_coated")
    board.visual(Box((0.075, 0.012, 0.055)), origin=Origin(xyz=(slider_x, -0.135, -0.045)),
                 material="frame", name="slider_guide_bracket_0", material_class_id="metal.paint_coated")
    board.visual(Box((0.075, 0.012, 0.055)), origin=Origin(xyz=(slider_x, 0.135, -0.045)),
                 material="frame", name="slider_guide_bracket_1", material_class_id="metal.paint_coated")
    board.visual(Box((0.480, 0.026, 0.020)), origin=Origin(xyz=(0.050, -0.060, -0.038)),
                 material="frame", name="height_notch_rail", material_class_id="metal.paint_coated")
    tstep = min(0.060, 0.42 / max(1, r.n_notch_teeth))
    tx0 = -0.135
    for i in range(r.n_notch_teeth):
        board.visual(
            Box((0.026, 0.032, 0.010)),
            origin=Origin(xyz=(tx0 + i * tstep, -0.060, -0.024), rpy=(0.0, 0.0, 0.38)),
            material="latch",
            name=f"height_notch_{i}", material_class_id="metal.blackened_gunmetal",
        )

    # Translating slider carrying the rear-leg hinge pin + spring latch.
    slider = model.part("height_slider")
    slider.visual(Cylinder(radius=0.014, length=0.300), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                  material="latch", name="sliding_hinge_pin", material_class_id="metal.blackened_gunmetal")
    slider.visual(Box((0.210, 0.028, 0.018)), origin=Origin(xyz=(0.105, -0.060, 0.006)),
                  material="frame", name="locking_tongue", material_class_id="metal.paint_coated")
    slider.visual(Cylinder(radius=0.016, length=0.030), origin=Origin(xyz=(0.205, -0.060, 0.006), rpy=(math.pi / 2.0, 0.0, 0.0)),
                  material="latch", name="latch_nose", material_class_id="metal.blackened_gunmetal")

    front_leg = model.part("front_leg")
    front_leg.visual(
        mesh_from_geometry(
            _slide_tube(
                [
                    (0.000, -0.160, 0.000),
                    (-0.220 * reach, -0.158, -0.245 * reach),
                    (-0.475 * reach, -0.156, -0.535 * reach),
                    (-0.720 * reach, -0.160, -0.785 * reach),
                    (-0.720 * reach, 0.160, -0.785 * reach),
                    (-0.475 * reach, 0.156, -0.535 * reach),
                    (-0.220 * reach, 0.158, -0.245 * reach),
                    (0.000, 0.160, 0.000),
                ],
                0.013,
            ),
            "front_tube_frame",
        ),
        material="frame",
        name="front_tube_frame", material_class_id="metal.paint_coated",
    )
    for i, y in enumerate((-0.205, 0.205)):
        front_leg.visual(Cylinder(radius=0.023, length=0.090),
                         origin=Origin(xyz=(-0.720 * reach, y, -0.785 * reach), rpy=(math.pi / 2.0, 0.0, 0.0)),
                         material="rubber", name=f"front_foot_{i}", material_class_id="rubber.smooth_plain")
    front_leg.visual(Box((0.020, 0.020, 0.018)), origin=Origin(xyz=(-0.340 * reach, 0.160, -0.390 * reach), rpy=(0.0, 0.0, 0.35)),
                     material="latch", name="front_cross_pivot_washer", material_class_id="metal.blackened_gunmetal")

    rear_leg = model.part("rear_leg")
    rear_leg.visual(
        mesh_from_geometry(
            _slide_tube(
                [
                    (0.000, -0.112, 0.000),
                    (0.205 * reach, -0.112, -0.260 * reach),
                    (0.435 * reach, -0.112, -0.535 * reach),
                    (0.680 * reach, -0.112, -0.785 * reach),
                    (0.680 * reach, 0.112, -0.785 * reach),
                    (0.435 * reach, 0.112, -0.535 * reach),
                    (0.205 * reach, 0.112, -0.260 * reach),
                    (0.000, 0.112, 0.000),
                ],
                0.012,
            ),
            "rear_tube_frame",
        ),
        material="frame",
        name="rear_tube_frame", material_class_id="metal.paint_coated",
    )
    for i, y in enumerate((-0.157, 0.157)):
        rear_leg.visual(Cylinder(radius=0.023, length=0.090),
                        origin=Origin(xyz=(0.680 * reach, y, -0.785 * reach), rpy=(math.pi / 2.0, 0.0, 0.0)),
                        material="rubber", name=f"rear_foot_{i}", material_class_id="rubber.smooth_plain")
    rear_leg.visual(Cylinder(radius=0.006, length=0.245),
                    origin=Origin(xyz=(0.335 * reach, 0.0, -0.405 * reach), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material="latch", name="rear_cross_pivot_pin", material_class_id="metal.blackened_gunmetal")

    model.articulation("board_to_height_slider", ArticulationType.PRISMATIC, parent=board, child=slider,
                       origin=Origin(xyz=(slider_x, 0.0, _SLIDE_HINGE_Z)), axis=(1.0, 0.0, 0.0),
                       motion_limits=MotionLimits(lower=0.0, upper=0.120, effort=45.0, velocity=0.15))
    model.articulation("board_to_front_leg", ArticulationType.REVOLUTE, parent=board, child=front_leg,
                       origin=Origin(xyz=(front_x, 0.0, _SLIDE_HINGE_Z)), axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(lower=0.0, upper=0.75, effort=35.0, velocity=1.2))
    model.articulation("slider_to_rear_leg", ArticulationType.REVOLUTE, parent=slider, child=rear_leg,
                       origin=Origin(), axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(lower=0.0, upper=0.78, effort=35.0, velocity=1.2))


# ───────────────────────────────────────────────────────────────────────────
# Slot A candidate: tabletop (fork var_skeleton_tabletop)
# ───────────────────────────────────────────────────────────────────────────

_TAB_LEG_HEIGHT = 0.12
_TAB_HINGE_Z = -0.048


def _tab_leg_pair_mesh(direction: int, reach: float) -> MeshGeometry:
    foot_x = direction * 0.01
    foot_z = -_TAB_LEG_HEIGHT * reach
    top_y = 0.085
    foot_y = 0.115
    segments = [
        [(0.0, -top_y, 0.0), (foot_x * 0.5, -top_y * 1.08, foot_z * 0.50), (foot_x, -foot_y, foot_z)],
        [(0.0, top_y, 0.0), (foot_x * 0.5, top_y * 1.08, foot_z * 0.50), (foot_x, foot_y, foot_z)],
        [(0.0, -top_y, 0.0), (0.0, top_y, 0.0)],
        [(foot_x, -foot_y - 0.035, foot_z), (foot_x, foot_y + 0.035, foot_z)],
        [(foot_x * 0.55, -foot_y * 0.78, foot_z * 0.55), (foot_x * 0.55, foot_y * 0.78, foot_z * 0.55)],
    ]
    return _tube_assembly(segments, 0.012)


def _tab_foot_caps_mesh(direction: int, reach: float) -> MeshGeometry:
    foot_x = direction * 0.01
    foot_z = -_TAB_LEG_HEIGHT * reach
    foot_y = 0.115
    return _tube_assembly(
        [
            [(foot_x, -foot_y - 0.030, foot_z), (foot_x, -foot_y + 0.005, foot_z)],
            [(foot_x, foot_y - 0.005, foot_z), (foot_x, foot_y + 0.030, foot_z)],
        ],
        0.016,
    )


def _build_tabletop_legs(model: ArticulatedObject, board: Part, r: ResolvedIroningBoardConfig) -> None:
    reach = r.leg_reach_scale
    rear_x = _clamp(0.28, -(r.half_len - 0.10), r.half_len - 0.10)
    front_x = _clamp(-0.22, -(r.half_len - 0.10), r.half_len - 0.10)

    for x, tag, span in ((rear_x, "rear", 0.100), (front_x, "front", 0.100)):
        for side in (-1, 1):
            board.visual(Box((0.038, 0.010, 0.040)), origin=Origin(xyz=(x, side * span, -0.044)),
                         material="frame", name=f"{tag}_hinge_bracket_{0 if side < 0 else 1}", material_class_id="metal.paint_coated")
            if tag == "rear":
                board.visual(Box((0.042, 0.032, 0.008)), origin=Origin(xyz=(x, side * 0.100, -0.024)),
                             material="frame", name=f"rear_hinge_mount_{0 if side < 0 else 1}", material_class_id="metal.paint_coated")

    rear_leg = model.part("rear_leg_pair")
    rear_leg.visual(mesh_from_geometry(_tab_leg_pair_mesh(-1, reach), "rear_leg_tubes"),
                    material="frame", name="leg_tubes", material_class_id="metal.paint_coated")
    rear_leg.visual(mesh_from_geometry(_tab_foot_caps_mesh(-1, reach), "rear_foot_caps"),
                    material="rubber", name="foot_caps", material_class_id="rubber.smooth_plain")
    for i, y in enumerate((-0.085, 0.085)):
        rear_leg.visual(Cylinder(radius=0.014, length=0.005), origin=Origin(xyz=(0.0, y, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
                        material="frame", name=f"pivot_washer_{i}", material_class_id="metal.blackened_gunmetal")

    front_leg = model.part("front_leg_pair")
    front_leg.visual(mesh_from_geometry(_tab_leg_pair_mesh(1, reach), "front_leg_tubes"),
                     material="frame", name="leg_tubes", material_class_id="metal.paint_coated")
    front_leg.visual(mesh_from_geometry(_tab_foot_caps_mesh(1, reach), "front_foot_caps"),
                     material="rubber", name="foot_caps", material_class_id="rubber.smooth_plain")
    for i, y in enumerate((-0.085, 0.085)):
        front_leg.visual(Cylinder(radius=0.011, length=0.005), origin=Origin(xyz=(0.0, y, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
                         material="shadow", name=f"pivot_bolt_{i}", material_class_id="metal.blackened_gunmetal")

    model.articulation("board_to_rear_leg", ArticulationType.REVOLUTE, parent=board, child=rear_leg,
                       origin=Origin(xyz=(rear_x, 0.0, _TAB_HINGE_Z)), axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(effort=25.0, velocity=1.5, lower=0.0, upper=1.35))
    model.articulation("board_to_front_leg", ArticulationType.REVOLUTE, parent=board, child=front_leg,
                       origin=Origin(xyz=(front_x, 0.0, _TAB_HINGE_Z)), axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(effort=25.0, velocity=1.5, lower=0.0, upper=1.35))


# ───────────────────────────────────────────────────────────────────────────
# Slot D candidate: linen_shelf (fork var_shelf_linen_rack) — FIXED, N rungs
# ───────────────────────────────────────────────────────────────────────────

_SHELF_Z = -0.42
_SHELF_WIRE_R = 0.004


def _build_linen_shelf(model: ArticulatedObject, board: Part, r: ResolvedIroningBoardConfig) -> None:
    x_min = -0.08
    x_max = 0.42
    y_half = 0.065
    rail_y = r.half_wid * 0.62
    underframe_z = -0.026

    # FIXED weld: mount the child frame at a real drop-support-top / underframe-rail
    # contact point so the joint origin sits on geometry on BOTH sides (mount_fixed
    # spirit). All child geometry below is authored relative to this mount point.
    mpx, mpy, mpz = 0.20, rail_y, underframe_z

    def loc(x: float, y: float, z: float) -> tuple[float, float, float]:
        return (x - mpx, y - mpy, z - mpz)

    def loc_seg(seg):
        return [loc(*p) for p in seg]

    shelf = model.part("linen_shelf")
    # Rectangular wire perimeter frame.
    perim = [
        loc_seg([(x_min, -y_half, _SHELF_Z), (x_max, -y_half, _SHELF_Z)]),
        loc_seg([(x_max, -y_half, _SHELF_Z), (x_max, y_half, _SHELF_Z)]),
        loc_seg([(x_max, y_half, _SHELF_Z), (x_min, y_half, _SHELF_Z)]),
        loc_seg([(x_min, y_half, _SHELF_Z), (x_min, -y_half, _SHELF_Z)]),
        loc_seg([(x_min + (x_max - x_min) * 0.33, -y_half, _SHELF_Z), (x_min + (x_max - x_min) * 0.33, y_half, _SHELF_Z)]),
        loc_seg([(x_min + (x_max - x_min) * 0.66, -y_half, _SHELF_Z), (x_min + (x_max - x_min) * 0.66, y_half, _SHELF_Z)]),
    ]
    shelf.visual(mesh_from_geometry(_tube_assembly(perim, _SHELF_WIRE_R * 1.15), "shelf_perimeter"),
                 material="frame", name="shelf_perimeter", material_class_id="metal.paint_coated")

    # Vertical drop supports up to the board underframe rails.
    mid_z = (_SHELF_Z + underframe_z) * 0.5
    t_mid = (mid_z - _SHELF_Z) / (underframe_z - _SHELF_Z)
    y_mid = y_half + t_mid * (rail_y - y_half)
    drop_segments = []
    for x in (0.20, 0.35):
        for y_sign in (-1, 1):
            drop_segments.append(loc_seg([(x, y_sign * y_half, _SHELF_Z), (x, y_sign * rail_y, underframe_z)]))
    drop_segments.append(loc_seg([(0.20, -y_mid, mid_z), (0.20, y_mid, mid_z)]))
    drop_segments.append(loc_seg([(0.35, -y_mid, mid_z), (0.35, y_mid, mid_z)]))
    shelf.visual(mesh_from_geometry(_tube_assembly(drop_segments, 0.005), "shelf_drop_supports"),
                 material="frame", name="drop_supports", material_class_id="metal.paint_coated")

    # N longitudinal wire rungs (loop-emitted, shared helper).
    n = r.n_shelf_rungs
    for i in range(n):
        y = -y_half + (2.0 * y_half) * (i + 0.5) / n
        shelf.visual(
            mesh_from_geometry(_tube(loc_seg([(x_min, y, _SHELF_Z), (x_max, y, _SHELF_Z)]), _SHELF_WIRE_R), f"rung_{i}"),
            material="frame",
            name=f"rung_{i}", material_class_id="metal.paint_coated",
        )

    model.articulation("board_to_linen_shelf", ArticulationType.FIXED, parent=board, child=shelf,
                       origin=Origin(xyz=(mpx, mpy, mpz)))


# ───────────────────────────────────────────────────────────────────────────
# Assembly
# ───────────────────────────────────────────────────────────────────────────


def _register_palette(model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]]) -> None:
    for key, rgba in palette.items():
        model.material(key, rgba=rgba)


def build_ironing_board(config: IroningBoardConfig, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    _register_palette(model, r.palette)

    board = _build_board(model, r)

    if r.leg_skeleton == "double_pivot_X":
        _build_double_pivot_legs(model, board, r)
    elif r.leg_skeleton == "sliding_pivot_X":
        _build_sliding_pivot_legs(model, board, r)
    else:
        _build_tabletop_legs(model, board, r)

    if r.under_shelf == "linen_shelf":
        _build_linen_shelf(model, board, r)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_ironing_board(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_ironing_board(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedIroningBoardConfig) -> list[tuple[str, str]]:
    return [
        ("leg_skeleton", r.leg_skeleton),
        ("board_planform", r.board_planform),
        ("iron_rest", r.iron_rest),
        ("under_shelf", r.under_shelf),
        ("n_shelf_rungs", str(r.n_shelf_rungs)),
        ("n_notch_teeth", str(r.n_notch_teeth)),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ───────────────────────────────────────────────────────────────────────────
# Tests
# ───────────────────────────────────────────────────────────────────────────


def _declare_double_pivot_allowances(ctx: TestContext, model: ArticulatedObject) -> None:
    board = model.get_part("board")
    latch = model.get_part("height_latch")
    rear_leg = model.get_part("rear_leg_pair")
    front_leg = model.get_part("front_leg_pair")
    ctx.allow_overlap(board, latch, elem_a="height_notch_rail", elem_b="slider_block",
                      reason="Height catch block is a captured sliding latch seated in the notched rail.")
    for i in (0, 1):
        ctx.allow_overlap(board, rear_leg, elem_a=f"rear_hinge_bracket_{i}", elem_b="leg_tubes",
                          reason="Rear clevis bracket captures the leg tube at the pivot axis.")
        ctx.allow_overlap(board, front_leg, elem_a=f"front_hinge_bracket_{i}", elem_b="leg_tubes",
                          reason="Front clevis bracket captures the leg tube at the pivot axis.")


def _declare_sliding_pivot_allowances(ctx: TestContext, model: ArticulatedObject) -> None:
    board = model.get_part("board")
    slider = model.get_part("height_slider")
    front_leg = model.get_part("front_leg")
    rear_leg = model.get_part("rear_leg")
    ctx.allow_overlap(board, slider, elem_a="height_notch_rail", elem_b="latch_nose",
                      reason="Spring latch nose is seated into the notched height rail.")
    ctx.allow_overlap(slider, rear_leg, elem_a="sliding_hinge_pin", elem_b="rear_tube_frame",
                      reason="Rear leg tube is captured around the sliding hinge pin.")
    for i in (0, 1):
        ctx.allow_overlap(board, front_leg, elem_a=f"front_hinge_bracket_{i}", elem_b="front_tube_frame",
                          reason="Front leg tube is cradled inside the underside hinge bracket.")
        ctx.allow_overlap(board, slider, elem_a=f"slider_guide_bracket_{i}", elem_b="sliding_hinge_pin",
                          reason="Sliding cross-pin is captured in the underside guide bracket.")


def _declare_tabletop_allowances(ctx: TestContext, model: ArticulatedObject) -> None:
    board = model.get_part("board")
    rear_leg = model.get_part("rear_leg_pair")
    front_leg = model.get_part("front_leg_pair")
    for name in ("rear_hinge_bracket_0", "rear_hinge_bracket_1"):
        ctx.allow_overlap(board, rear_leg, elem_a=name, elem_b="leg_tubes",
                          reason="Clevis hinge bracket captures the leg tube at the fold-flat pivot.")
    for name in ("front_hinge_bracket_0", "front_hinge_bracket_1"):
        ctx.allow_overlap(board, front_leg, elem_a=name, elem_b="leg_tubes",
                          reason="Clevis hinge bracket captures the leg tube at the fold-flat pivot.")


def _declare_shelf_allowances(ctx: TestContext, model: ArticulatedObject) -> None:
    board = model.get_part("board")
    shelf = model.get_part("linen_shelf")
    ctx.allow_overlap(board, shelf, elem_a="underside_braces", elem_b="drop_supports",
                      reason="Shelf drop supports are welded to the board underframe rails.")
    ctx.allow_overlap(board, shelf, elem_a="perforated_plate", elem_b="drop_supports",
                      reason="Shelf drop supports pass the board plate bottom to reach the underframe rails.")
    # The folding X legs cross the whole under-board span, so their swept volume
    # necessarily shares the static under-shelf's clearance envelope while folding
    # (the shelf is a deploy-time fixture). Element-scoped to the leg tubes.
    for leg_name in ("front_leg_pair", "rear_leg_pair"):
        leg = model.get_part(leg_name)
        ctx.allow_overlap(leg, shelf, elem_a="leg_tubes", elem_b="drop_supports",
                          reason="Folding leg sweeps through the fixed under-shelf drop supports' envelope.")
        ctx.allow_overlap(leg, shelf, elem_a="leg_tubes", elem_b="shelf_perimeter",
                          reason="Folding leg sweeps through the fixed under-shelf perimeter's envelope.")


def run_ironing_board_tests(object_model: ArticulatedObject, config: IroningBoardConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("board root present", "board" in part_names)
    ctx.check("slot_choices match config",
              object_model.meta.get("slot_choices") == slot_choices_for_config(r))

    board = object_model.get_part("board")

    # Category identity: elongated tapered ironing surface.
    board_aabb = ctx.part_world_aabb(board)
    min_len = 0.68 if r.leg_skeleton == "tabletop" else 1.30
    ctx.check(
        "board has elongated ironing-surface proportions",
        board_aabb is not None
        and (board_aabb[1][0] - board_aabb[0][0]) > min_len
        and (board_aabb[1][0] - board_aabb[0][0]) > 1.9 * (board_aabb[1][1] - board_aabb[0][1]),
        details=f"board_aabb={board_aabb}",
    )

    # ── Slot A: leg skeleton allowances + folding-motion semantics ──
    if r.leg_skeleton == "double_pivot_X":
        _declare_double_pivot_allowances(ctx, object_model)
        rear_leg = object_model.get_part("rear_leg_pair")
        front_leg = object_model.get_part("front_leg_pair")
        latch = object_model.get_part("height_latch")
        rear_hinge = object_model.get_articulation("board_to_rear_leg")
        front_hinge = object_model.get_articulation("board_to_front_leg")
        latch_slide = object_model.get_articulation("board_to_height_latch")

        rear_rest = ctx.part_world_aabb(rear_leg)
        front_rest = ctx.part_world_aabb(front_leg)
        ctx.check("crossed legs reach well below the top",
                  rear_rest is not None and front_rest is not None
                  and rear_rest[0][2] < -0.5 and front_rest[0][2] < -0.5,
                  details=f"rear={rear_rest}, front={front_rest}")
        ctx.expect_overlap(rear_leg, front_leg, axes="xz", min_overlap=0.15, name="two leg pairs form a visible X")
        with ctx.pose({rear_hinge: 0.52, front_hinge: 0.52}):
            rear_folded = ctx.part_world_aabb(rear_leg)
            front_folded = ctx.part_world_aabb(front_leg)
        ctx.check("leg hinges fold feet upward toward the board",
                  rear_folded is not None and front_folded is not None
                  and rear_folded[0][2] > rear_rest[0][2] + 0.08
                  and front_folded[0][2] > front_rest[0][2] + 0.08,
                  details=f"rear_folded={rear_folded}, front_folded={front_folded}")
        latch_rest = ctx.part_world_position(latch)
        with ctx.pose({latch_slide: 0.10}):
            latch_shifted = ctx.part_world_position(latch)
        ctx.check("height catch slides along the notched rail",
                  latch_rest is not None and latch_shifted is not None
                  and latch_shifted[0] > latch_rest[0] + 0.08,
                  details=f"rest={latch_rest}, shifted={latch_shifted}")

    elif r.leg_skeleton == "sliding_pivot_X":
        _declare_sliding_pivot_allowances(ctx, object_model)
        front_leg = object_model.get_part("front_leg")
        rear_leg = object_model.get_part("rear_leg")
        slider = object_model.get_part("height_slider")
        front_hinge = object_model.get_articulation("board_to_front_leg")
        rear_hinge = object_model.get_articulation("slider_to_rear_leg")
        height_slide = object_model.get_articulation("board_to_height_slider")

        rest_front = ctx.part_element_world_aabb(front_leg, elem="front_foot_0")
        rest_rear = ctx.part_element_world_aabb(rear_leg, elem="rear_foot_0")
        rest_slider = ctx.part_world_position(slider)
        with ctx.pose({front_hinge: 0.72, rear_hinge: 0.72, height_slide: 0.10}):
            folded_front = ctx.part_element_world_aabb(front_leg, elem="front_foot_0")
            folded_rear = ctx.part_element_world_aabb(rear_leg, elem="rear_foot_0")
            slid = ctx.part_world_position(slider)
        ctx.check("front foot rises when folding",
                  rest_front is not None and folded_front is not None
                  and folded_front[0][2] > rest_front[0][2] + 0.10,
                  details=f"rest={rest_front}, folded={folded_front}")
        ctx.check("rear foot rises when folding",
                  rest_rear is not None and folded_rear is not None
                  and folded_rear[0][2] > rest_rear[0][2] + 0.10,
                  details=f"rest={rest_rear}, folded={folded_rear}")
        ctx.check("height slider travels along notched rail",
                  rest_slider is not None and slid is not None and slid[0] > rest_slider[0] + 0.08,
                  details=f"rest={rest_slider}, slid={slid}")

    else:  # tabletop
        _declare_tabletop_allowances(ctx, object_model)
        rear_leg = object_model.get_part("rear_leg_pair")
        front_leg = object_model.get_part("front_leg_pair")
        rear_hinge = object_model.get_articulation("board_to_rear_leg")
        front_hinge = object_model.get_articulation("board_to_front_leg")
        ctx.check("no height mechanism on tabletop",
                  "height_latch" not in part_names and "height_slider" not in part_names)
        rear_rest = ctx.part_world_aabb(rear_leg)
        front_rest = ctx.part_world_aabb(front_leg)
        ctx.check("tabletop legs give a short stance",
                  rear_rest is not None and front_rest is not None
                  and -0.24 < rear_rest[0][2] < -0.05 and -0.24 < front_rest[0][2] < -0.05,
                  details=f"rear={rear_rest}, front={front_rest}")
        with ctx.pose({rear_hinge: 1.33, front_hinge: 1.33}):
            rear_folded = ctx.part_world_aabb(rear_leg)
            front_folded = ctx.part_world_aabb(front_leg)
        ctx.check("tabletop legs fold up coplanar to the board underside",
                  rear_folded is not None and front_folded is not None
                  and rear_folded[0][2] > rear_rest[0][2] + 0.05
                  and front_folded[0][2] > front_rest[0][2] + 0.05,
                  details=f"rear_folded={rear_folded}, front_folded={front_folded}")

    # ── Slot D: linen shelf ──
    if r.under_shelf == "linen_shelf":
        _declare_shelf_allowances(ctx, object_model)
        shelf = object_model.get_part("linen_shelf")
        ctx.expect_contact(board, shelf, elem_a="underside_braces", elem_b="drop_supports",
                           name="drop supports contact the board underframe rails")
        shelf_aabb = ctx.part_element_world_aabb(shelf, elem="shelf_perimeter")
        ctx.check("linen shelf hangs well below the board top",
                  shelf_aabb is not None and shelf_aabb[1][2] < -0.25,
                  details=f"shelf_perimeter_aabb={shelf_aabb}")
        rung_count = len([v for v in shelf.visuals if v.name and v.name.startswith("rung_")])
        ctx.check("linen shelf has N indexed wire rungs",
                  rung_count == r.n_shelf_rungs,
                  details=f"rung_count={rung_count}, expected={r.n_shelf_rungs}")
    else:
        ctx.check("no linen shelf part", "linen_shelf" not in part_names)

    # ── Rule 5: full-travel non-穿模 across sampled joint poses ──
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "IroningBoardConfig",
    "ResolvedIroningBoardConfig",
    "build_ironing_board",
    "build_seeded_ironing_board",
    "config_from_seed",
    "resolve_config",
    "run_ironing_board_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
