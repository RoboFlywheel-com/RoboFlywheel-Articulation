# SPDX-License-Identifier: Apache-2.0

"""Source-backed articulated makeup compacts (0611 / Makeup3 pool).

One shallow case body (round / rounded-rectangular / hexagonal footprint) with a
real cavity, a cover that either flips on a rear revolute hinge or slides on a
guided prismatic track, a front closure that is either a push-slide button
captured in a wall pocket or a toggle latch on a captured pivot pin, and ``N``
powder inserts built as real metal-cup + pressed-cake sub-assemblies.

Frame: +X right, +Y back (hinge side), -Y front (closure side), +Z up. The case
footprint is centred on the origin, floor at z=0. Both cover motions use
``lower=0`` for the closed pose.
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
    AxisInterface,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    MeshGeometry,
    MotionLimits,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_cadquery,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
    rounded_rect_profile,
    sample_catmull_rom_spline_2d,
)

# The compact opens toward -Y (closure edge), so a view named front_iso must
# look at the closure/cavity side rather than the hinge slab.
__preview_front_axis__ = "-y"

CaseForm = Literal["round", "rounded_rect", "hexagonal"]
LidMotion = Literal["flip_hinge", "guided_slide"]
LidModule = Literal["lacquer_inlay", "engraved_plaque", "fitted_inner_mirror"]
Closure = Literal["push_slide_button", "toggle_latch"]
PowderInsert = Literal["round_metal_cup", "petal_pressed_pan"]
Palette = Literal[
    "polished_gold_champagne",
    "gloss_black_peach",
    "pearl_rose",
    "brushed_silver_mauve",
    "matte_navy_terracotta",
]

PALETTES: tuple[Palette, ...] = (
    "polished_gold_champagne",
    "gloss_black_peach",
    "pearl_rose",
    "brushed_silver_mauve",
    "matte_navy_terracotta",
)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("case_form", ("round", "rounded_rect", "hexagonal")),
        component_slot("lid_motion", ("flip_hinge", "guided_slide")),
        component_slot(
            "lid_module",
            ("lacquer_inlay", "engraved_plaque", "fitted_inner_mirror"),
        ),
        component_slot("closure", ("push_slide_button", "toggle_latch")),
        component_slot("powder_insert", ("round_metal_cup", "petal_pressed_pan")),
        multiplicity_slot("well_count", (1, 2, 3, 4), item_slot="powder_insert"),
    )
)

# Seating interference used where two different parts must physically bear on
# each other (cover on rim, pan cup on cavity floor, knuckle/boss axial seat).
# It models a real press/seat fit and is two orders of magnitude below the QC
# overlap depth budget; it is not a suppressed intersection.
_SEAT_BITE_M = 5.0e-5
# Intra-part join interference so every part stays one connected solid.
_JOIN_BITE_M = 2.0e-4
_COS30 = math.cos(math.radians(30.0))
_GRID_BY_N: dict[int, tuple[int, int]] = {1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (2, 2)}

# Normalised petal control points from origin 001 `_petal_shape`
# (model.py:L23-L34), divided by its 0.0415 m outer reach. The narrow end points
# at the case centre.
_PETAL_UNIT: tuple[tuple[float, float], ...] = (
    (-0.139759, 0.132530),
    (-0.277108, 0.253012),
    (-0.361446, 0.493976),
    (-0.337349, 0.759036),
    (-0.204819, 0.939759),
    (0.000000, 1.000000),
    (0.204819, 0.939759),
    (0.337349, 0.759036),
    (0.361446, 0.493976),
    (0.277108, 0.253012),
    (0.139759, 0.132530),
)
# Radial mid-point of the unit petal, used to centre a pan on its own outline.
_PETAL_MID = 0.566
# Half the unit petal's radial span; used as the pan's characteristic half-size.
_PETAL_REACH = 0.434


@dataclass(frozen=True)
class Config:
    case_form: CaseForm = "round"
    lid_motion: LidMotion = "flip_hinge"
    lid_module: LidModule = "lacquer_inlay"
    closure: Closure = "push_slide_button"
    powder_insert: PowderInsert = "round_metal_cup"
    well_count: int = 1
    case_span_m: float | None = None
    case_height_m: float | None = None
    lid_open_angle_rad: float | None = None
    slide_travel_ratio: float | None = None
    button_travel_m: float | None = None
    latch_lock_angle_rad: float | None = None
    well_fill_ratio: float | None = None
    palette: Palette = "polished_gold_champagne"
    name: str = "makeup3"


@dataclass(frozen=True)
class ResolvedConfig:
    case_form: CaseForm
    lid_motion: LidMotion
    lid_module: LidModule
    closure: Closure
    powder_insert: PowderInsert
    well_count: int
    palette: Palette
    name: str
    case_span_m: float
    case_height_m: float
    lid_open_angle_rad: float
    slide_travel_ratio: float
    button_travel_m: float
    latch_lock_angle_rad: float
    well_fill_ratio: float
    hx_m: float
    hy_m: float
    corner_r_m: float
    wall_thk_m: float
    floor_h_m: float
    rim_h_m: float
    rim_lip_m: float
    cav_hx_m: float
    cav_hy_m: float
    cav_corner_r_m: float
    tray_thk_m: float
    profile_segments: int
    front_band_lo_m: float
    front_band_hi_m: float
    closure_z_m: float
    closure_h_m: float
    lid_hx_m: float
    lid_hy_m: float
    lid_corner_r_m: float
    lid_over_m: float
    panel_thk_m: float
    skirt_thk_m: float
    skirt_drop_m: float
    skirt_cut_y_m: float
    lid_front_y_m: float
    engage_z_m: float
    hinge_r_m: float
    pin_r_m: float
    bore_r_m: float
    hinge_y_m: float
    hinge_z_m: float
    barrel_half_m: float
    knuckle_in_m: float
    knuckle_out_m: float
    slide_travel_m: float
    post_r_m: float
    post_head_r_m: float
    post_x_m: float
    post_y_m: float
    slot_half_w_m: float
    btn_cap_w_m: float
    btn_cap_h_m: float
    btn_cap_out_m: float
    btn_stem_w_m: float
    btn_stem_h_m: float
    btn_lug_w_m: float
    btn_lug_h_m: float
    btn_lug_thk_m: float
    btn_cbore_depth_m: float
    btn_clearance_m: float
    latch_pivot_y_m: float
    latch_pivot_z_m: float
    latch_boss_r_m: float
    latch_bore_r_m: float
    latch_pin_r_m: float
    latch_boss_half_m: float
    latch_lug_in_m: float
    latch_lug_out_m: float
    latch_bar_hw_m: float
    latch_bar_thk_m: float
    latch_len_m: float
    latch_hook_len_m: float
    latch_hook_thk_m: float
    latch_recess_hw_m: float
    latch_gap_m: float
    well_outer_r_m: float
    well_wall_thk_m: float
    well_floor_thk_m: float
    well_depth_m: float
    cake_r_m: float
    cake_h_m: float
    petal_scale_m: float
    well_centers: tuple[tuple[float, float], ...]
    well_angles_deg: tuple[float, ...]
    well_open_gap_m: float
    cav_margin_m: float


# --------------------------------------------------------------------------- #
# footprint helpers
# --------------------------------------------------------------------------- #


def _extents_offset(
    form: CaseForm, hx: float, hy: float, corner_r: float, delta: float
) -> tuple[float, float, float]:
    """Offset a footprint outward by ``delta`` (negative insets it)."""

    if form == "hexagonal":
        return (hx + delta / _COS30, hy + delta, corner_r)
    return (hx + delta, hy + delta, max(0.0004, corner_r + delta))


def _footprint_profile(
    form: CaseForm, hx: float, hy: float, corner_r: float, segments: int
) -> list[tuple[float, float]]:
    if form == "round":
        return [
            (
                hx * math.cos(2.0 * math.pi * i / segments),
                hy * math.sin(2.0 * math.pi * i / segments),
            )
            for i in range(segments)
        ]
    if form == "hexagonal":
        return [
            (
                hx * math.cos(math.radians(60.0 * i)),
                hx * math.sin(math.radians(60.0 * i)),
            )
            for i in range(6)
        ]
    return list(rounded_rect_profile(2.0 * hx, 2.0 * hy, min(corner_r, 0.45 * min(hx, hy))))


def _footprint_x_at_y(form: CaseForm, hx: float, hy: float, corner_r: float, y: float) -> float:
    ay = min(abs(y), hy)
    if form == "round":
        return hx * math.sqrt(max(0.0, 1.0 - (ay / hy) ** 2))
    if form == "hexagonal":
        return max(0.0, hx - ay / math.sqrt(3.0))
    radius = min(corner_r, 0.45 * min(hx, hy))
    flat = hy - radius
    if ay <= flat:
        return hx
    return hx - radius + math.sqrt(max(0.0, radius * radius - (ay - flat) ** 2))


def _boundary_clearance(
    form: CaseForm, hx: float, hy: float, corner_r: float, cx: float, cy: float
) -> float:
    """Perpendicular distance from ``(cx, cy)`` to the footprint boundary."""

    if form == "round":
        return hx - math.hypot(cx, cy * hx / hy)
    if form == "hexagonal":
        best = float("inf")
        for phi_deg in (30.0, 90.0, 150.0):
            phi = math.radians(phi_deg)
            best = min(best, hy - abs(cx * math.cos(phi) + cy * math.sin(phi)))
        return best
    radius = min(corner_r, 0.45 * min(hx, hy))
    dx = hx - radius
    dy = hy - radius
    if abs(cx) > dx and abs(cy) > dy:
        return radius - math.hypot(abs(cx) - dx, abs(cy) - dy)
    return min(hx - abs(cx), hy - abs(cy))


def _inradius(form: CaseForm, hx: float, hy: float) -> float:
    if form == "round":
        return hx
    if form == "hexagonal":
        return hy
    return min(hx, hy)


def _clip_profile_y_max(
    points: list[tuple[float, float]], y_max: float
) -> list[tuple[float, float]]:
    """Open polyline of a closed convex loop restricted to ``y <= y_max``.

    The walk deliberately starts at a removed vertex so the result begins at the
    entry crossing and ends at the exit crossing; concatenating one such polyline
    with the reverse of another then yields a valid crescent band.
    """

    count = len(points)
    start = next((i for i, p in enumerate(points) if p[1] > y_max), None)
    if start is None:
        return list(points)
    kept: list[tuple[float, float]] = []
    for offset in range(count):
        index = (start + offset) % count
        cur = points[index]
        nxt = points[(index + 1) % count]
        cur_in = cur[1] <= y_max
        nxt_in = nxt[1] <= y_max
        if cur_in:
            kept.append(cur)
        if cur_in != nxt_in:
            span = nxt[1] - cur[1]
            if abs(span) > 1e-12:
                kept.append(
                    (
                        cur[0] + (y_max - cur[1]) / span * (nxt[0] - cur[0]),
                        y_max,
                    )
                )
    return kept


def _circle_polygon(radius: float, segments: int = 28) -> list[tuple[float, float]]:
    return [
        (
            radius * math.cos(2.0 * math.pi * i / segments),
            radius * math.sin(2.0 * math.pi * i / segments),
        )
        for i in range(segments)
    ]


def _slot_polygon(half_w: float, half_len: float, segments: int = 8) -> list[tuple[float, float]]:
    """Elongated guide slot running along local Y."""

    straight = max(half_len - half_w, 1e-5)
    points: list[tuple[float, float]] = []
    for i in range(segments + 1):
        angle = math.pi * i / segments
        points.append((half_w * math.cos(angle), straight + half_w * math.sin(angle)))
    for i in range(segments + 1):
        angle = math.pi * i / segments
        points.append((-half_w * math.cos(angle), -straight - half_w * math.sin(angle)))
    return points


def _petal_polygon(
    scale: float, angle_deg: float, offset: tuple[float, float] = (0.0, 0.0)
) -> list[tuple[float, float]]:
    smooth = sample_catmull_rom_spline_2d(
        [(x * scale, y * scale + offset[1]) for x, y in _PETAL_UNIT],
        samples_per_segment=4,
        closed=False,
    )
    angle = math.radians(angle_deg)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return [(x * cos_a - y * sin_a + offset[0], x * sin_a + y * cos_a) for x, y in smooth]


def _point_segment_distance(
    p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]
) -> float:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length_sq = dx * dx + dy * dy
    if length_sq <= 1e-18:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length_sq))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def _min_polygon_gap(poly_a: list[tuple[float, float]], poly_b: list[tuple[float, float]]) -> float:
    """Minimum separation between two closed polygon outlines."""

    best = float("inf")
    for src, dst in ((poly_a, poly_b), (poly_b, poly_a)):
        count = len(dst)
        for point in src:
            for index in range(count):
                best = min(
                    best,
                    _point_segment_distance(point, dst[index], dst[(index + 1) % count]),
                )
    return best


def _polygon_bounds(
    points: list[tuple[float, float]],
) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def _cq_prism(points: list[tuple[float, float]], z0: float, height: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .polyline([(x, y) for x, y in points])
        .close()
        .extrude(height)
        .translate((0.0, 0.0, z0))
    )


def _cq_box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=(True, True, True))
        .translate(((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0))
    )


def _mesh_box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> MeshGeometry:
    profile = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return ExtrudeGeometry(profile, z1 - z0, cap=True, center=False).translate(0.0, 0.0, z0)


def _mesh_tube_x(
    outer_r: float, inner_r: float, x0: float, x1: float, y: float, z: float
) -> MeshGeometry:
    geom = ExtrudeWithHolesGeometry(
        _circle_polygon(outer_r, 24),
        [_circle_polygon(inner_r, 24)],
        x1 - x0,
        cap=True,
        center=False,
    )
    geom.rotate_y(math.pi / 2.0)
    return geom.translate(x0, y, z)


def _mesh_cyl_z(radius: float, z0: float, z1: float, x: float, y: float) -> MeshGeometry:
    return ExtrudeGeometry(_circle_polygon(radius, 20), z1 - z0, cap=True, center=False).translate(
        x, y, z0
    )


def _mesh_cyl_x(radius: float, x0: float, x1: float, y: float, z: float) -> MeshGeometry:
    geom = ExtrudeGeometry(_circle_polygon(radius, 20), x1 - x0, cap=True, center=False)
    geom.rotate_y(math.pi / 2.0)
    return geom.translate(x0, y, z)


# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x3A11C3)
    return Config(
        case_form=choices["case_form"],
        lid_motion=choices["lid_motion"],
        lid_module=choices["lid_module"],
        closure=choices["closure"],
        powder_insert=choices["powder_insert"],
        well_count=choices["well_count"],
        case_span_m=round(rng.uniform(0.070, 0.104), 5),
        case_height_m=round(rng.uniform(0.0135, 0.0235), 5),
        lid_open_angle_rad=round(rng.uniform(1.25, 1.85), 4),
        slide_travel_ratio=round(rng.uniform(0.34, 0.52), 4),
        button_travel_m=round(rng.uniform(0.0010, 0.0022), 5),
        latch_lock_angle_rad=round(rng.uniform(1.00, 1.32), 4),
        well_fill_ratio=round(rng.uniform(0.80, 0.94), 4),
        palette=PALETTES[rng.randrange(len(PALETTES))],
    )


def _pack_round_wells(
    form: CaseForm,
    chx: float,
    chy: float,
    ccr: float,
    count: int,
    margin: float,
    rib_gap: float,
) -> tuple[float, tuple[tuple[float, float], ...]]:
    """Maximise the well radius of an ``N`` grid against the real cavity."""

    cols, rows = _GRID_BY_N[count]
    best_r = -1.0
    best_centers: tuple[tuple[float, float], ...] = ((0.0, 0.0),)
    for step in range(1, 65):
        t = step / 64.0
        pitch_x = 2.0 * chx * t / cols
        pitch_y = 2.0 * chy * t / rows
        centers = tuple(
            (
                (col - (cols - 1) / 2.0) * pitch_x,
                (row - (rows - 1) / 2.0) * pitch_y,
            )
            for row in range(rows)
            for col in range(cols)
        )
        limits: list[float] = []
        if cols > 1:
            limits.append(pitch_x / 2.0 - rib_gap)
        if rows > 1:
            limits.append(pitch_y / 2.0 - rib_gap)
        cell_limit = min(limits) if limits else 1.0
        bound_limit = (
            min(_boundary_clearance(form, chx, chy, ccr, cx, cy) for cx, cy in centers) - margin
        )
        radius = min(cell_limit, bound_limit)
        if radius > best_r:
            best_r = radius
            best_centers = centers
    return best_r, best_centers


def _pack_petal_wells(
    count: int, r_lim: float
) -> tuple[float, float, tuple[tuple[float, float], ...], tuple[float, ...]]:
    """Solve an ``N``-fold petal rosette against the real cavity inradius.

    ``ring_u`` is the dimensionless radius (in petal-scale units) at which each
    petal outline is centred.  It is pushed outward until adjacent petals keep a
    real gap; the uniform scale then follows from the cavity inradius, so the
    pack never relies on fixed well radius/spacing constants.
    """

    base = _petal_polygon(1.0, 0.0)
    centred = [(x, y - _PETAL_MID) for x, y in base]
    if count == 1:
        reach = max(math.hypot(x, y) for x, y in centred)
        return r_lim / reach, _PETAL_MID, ((0.0, 0.0),), (0.0,)

    start = 90.0 if count == 2 else 0.0
    angles = tuple(start + 360.0 * index / count for index in range(count))
    best_gap = -1.0
    best_ring = _PETAL_MID
    best_scale = 0.0
    for step in range(48):
        ring_u = _PETAL_MID + 0.018 * step
        placed = [(x, y + ring_u) for x, y in centred]
        scale = r_lim / max(math.hypot(x, y) for x, y in placed)
        outlines = []
        for angle in angles:
            radians = math.radians(angle)
            cos_a = math.cos(radians)
            sin_a = math.sin(radians)
            outlines.append(
                [
                    ((x * cos_a - y * sin_a) * scale, (x * sin_a + y * cos_a) * scale)
                    for x, y in placed
                ]
            )
        gap = min(
            _min_polygon_gap(outlines[i], outlines[j])
            for i in range(count)
            for j in range(i + 1, count)
        )
        if gap > best_gap:
            best_gap = gap
            best_ring = ring_u
            best_scale = scale
        if gap >= 0.0010:
            break
    ring = best_ring * best_scale
    centers = tuple(
        (-ring * math.sin(math.radians(angle)), ring * math.cos(math.radians(angle)))
        for angle in angles
    )
    return best_scale, best_ring, centers, angles


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "case_form": config.case_form,
            "lid_motion": config.lid_motion,
            "lid_module": config.lid_module,
            "closure": config.closure,
            "powder_insert": config.powder_insert,
            "well_count": config.well_count,
        }
    )
    span = 0.088 if config.case_span_m is None else float(config.case_span_m)
    height = 0.0180 if config.case_height_m is None else float(config.case_height_m)
    open_angle = 1.62 if config.lid_open_angle_rad is None else float(config.lid_open_angle_rad)
    travel_ratio = 0.43 if config.slide_travel_ratio is None else float(config.slide_travel_ratio)
    button_travel = 0.0015 if config.button_travel_m is None else float(config.button_travel_m)
    lock_angle = 1.18 if config.latch_lock_angle_rad is None else float(config.latch_lock_angle_rad)
    fill = 0.88 if config.well_fill_ratio is None else float(config.well_fill_ratio)
    if not 0.070 <= span <= 0.104:
        raise ValueError("case_span_m must be in [0.070, 0.104]")
    if not 0.0135 <= height <= 0.0235:
        raise ValueError("case_height_m must be in [0.0135, 0.0235]")
    if not 1.25 <= open_angle <= 1.85:
        raise ValueError("lid_open_angle_rad must be in [1.25, 1.85]")
    if not 0.34 <= travel_ratio <= 0.52:
        raise ValueError("slide_travel_ratio must be in [0.34, 0.52]")
    if not 0.0010 <= button_travel <= 0.0022:
        raise ValueError("button_travel_m must be in [0.0010, 0.0022]")
    if not 1.00 <= lock_angle <= 1.32:
        raise ValueError("latch_lock_angle_rad must be in [1.00, 1.32]")
    if not 0.80 <= fill <= 0.94:
        raise ValueError("well_fill_ratio must be in [0.80, 0.94]")
    if config.palette not in PALETTES:
        raise ValueError(f"unknown palette {config.palette!r}")

    form = config.case_form
    hx = span / 2.0
    if form == "round":
        hy = hx
    elif form == "hexagonal":
        hy = hx * _COS30
    else:
        hy = hx * 0.82
    corner_r = 0.18 * min(hx, hy)
    segments = 48 if form == "round" else 6 if form == "hexagonal" else 4
    wall_thk = max(0.0019, 0.045 * hx)
    floor_h = max(0.0022, 0.22 * height)
    rim_h = max(0.0016, 0.16 * height)
    rim_lip = max(0.0008, 0.30 * wall_thk)
    tray_thk = max(0.0006, 0.05 * height)
    cav_hx, cav_hy, cav_cr = _extents_offset(form, hx, hy, corner_r, -wall_thk)

    panel_thk = max(0.0019, 0.26 * height)
    lid_over = max(0.0018, 0.036 * hx)
    skirt_thk = 0.52 * lid_over
    skirt_drop = 0.26 * height
    front_band_lo = floor_h + tray_thk + 0.0005
    front_band_hi = height - skirt_drop - 0.0009
    front_band = front_band_hi - front_band_lo
    if front_band < 0.0028:
        raise ValueError("derived front closure band is too shallow for the case")
    closure_h = min(0.0060, 0.92 * front_band)
    closure_z = 0.5 * (front_band_lo + front_band_hi)

    lid_hx, lid_hy, lid_cr = _extents_offset(form, hx, hy, corner_r, lid_over)
    lid_front_y = -lid_hy
    skirt_cut_y = hy - wall_thk - 0.0012

    hinge_r = max(0.0018, 0.055 * hx)
    pin_r = max(0.00065, 0.34 * hinge_r)
    bore_r = pin_r + max(0.00034, 0.12 * pin_r)
    hinge_z = height + panel_thk + 0.35 * hinge_r
    hinge_y = hy + hinge_r + lid_over + 0.0009
    barrel_half = max(0.0062, 0.28 * hx)
    # The knuckles start exactly where the barrel ends so the barrel's end faces
    # seat axially against them (see _SEAT_BITE_M) instead of floating on the pin.
    knuckle_in = barrel_half
    knuckle_out = min(knuckle_in + max(0.0055, 0.20 * hx), 0.92 * lid_hx)

    slide_travel = travel_ratio * 2.0 * hy
    post_r = max(0.0011, 0.026 * hx)
    post_head_r = post_r + max(0.0009, 0.55 * post_r)
    slot_half_w = post_r + 0.00050
    mid_hx, mid_hy, mid_cr = _extents_offset(form, hx, hy, corner_r, -(wall_thk + rim_lip) / 2.0)
    post_y = 0.60 * mid_hy
    post_x = _footprint_x_at_y(form, mid_hx, mid_hy, mid_cr, post_y)
    room = lid_hy - 0.0026
    if post_y + slot_half_w > room or post_y - slide_travel - slot_half_w < -room:
        raise ValueError("derived slide travel does not fit the cover guide slots")
    if post_x + post_head_r > lid_hx - 0.0004:
        raise ValueError("derived guide posts do not fit inside the cover plan")

    btn_clearance = 0.00040
    # The cap always stays outside the front wall: at rest it stands off by the
    # full travel plus a bottoming gap, so pressing it seats the cap instead of
    # driving it through the wall.
    btn_cbore_depth = button_travel + 0.00030
    # The retainer lug is both wider and taller than the guide pocket, so the
    # button cannot be pulled out or dropped through it.
    btn_lug_h = closure_h
    btn_stem_h = btn_lug_h - 0.0012
    btn_cap_h = btn_lug_h
    btn_stem_w = max(0.0040, 0.13 * hx)
    btn_cap_w = btn_stem_w + max(0.0030, 0.055 * hx)
    btn_lug_w = btn_stem_w + 0.0022
    btn_lug_thk = 0.0009
    if btn_stem_h < 0.0012:
        raise ValueError("derived push button stem is too thin for its pocket")
    btn_cap_out = max(0.0012, 0.30 * btn_cap_h)

    engage_z = (
        height + 0.5 * panel_thk
        if config.lid_motion == "guided_slide"
        else height - 0.5 * skirt_drop
    )
    latch_gap = 0.00055
    latch_hook_thk = 0.0013
    latch_boss_r = max(0.0016, 0.030 * hx)
    latch_pin_r = max(0.00062, 0.34 * latch_boss_r)
    latch_bore_r = latch_pin_r + max(0.00034, 0.12 * latch_pin_r)
    latch_bar_thk = min(0.0016, 1.5 * latch_boss_r)
    latch_boss_half = max(0.0032, 0.075 * hx)
    latch_bar_hw = latch_boss_half - 0.0009
    latch_recess_hw = latch_boss_half
    # The pivot boss is the lever's most inboard feature; standing it off by the
    # boss radius plus the engagement gap puts the ENTIRE swept lever outboard of
    # the cover edge and therefore outboard of the front wall as well.
    latch_pivot_y = lid_front_y - latch_gap - latch_boss_r
    latch_pivot_z = front_band_hi - latch_boss_r - 0.0003
    latch_lug_in = latch_boss_half
    latch_lug_out = latch_lug_in + max(0.0022, 0.035 * hx)
    sin_lock = math.sin(lock_angle)
    cos_lock = math.cos(lock_angle)
    # Solve the lever so that at the locked angle the hook's most inboard corner
    # sits exactly on the cover engagement plane (y = lid_front - gap,
    # z = engage_z). With A = lever reach and B = hook rise:
    #   -A*cos + B*sin = boss_r   and   A*sin + B*cos = engage_z - pivot_z
    reach_span = engage_z - latch_pivot_z
    latch_arm = reach_span * sin_lock - cos_lock * latch_boss_r
    latch_rise = reach_span * cos_lock + sin_lock * latch_boss_r
    latch_len = latch_arm + latch_hook_thk
    latch_hook_len = latch_rise - 0.5 * latch_bar_thk
    if latch_arm < 0.0012 or latch_hook_len < 0.0006:
        raise ValueError("derived toggle lever geometry is degenerate")
    if latch_pivot_z - latch_boss_r < front_band_lo:
        raise ValueError("derived latch pivot does not fit the front closure band")

    cav_margin = 0.0026
    well_open_gap = 0.00045
    if config.powder_insert == "round_metal_cup":
        well_r, centers = _pack_round_wells(
            form, cav_hx, cav_hy, cav_cr, config.well_count, cav_margin, 0.0011
        )
        if well_r < 0.0030:
            raise ValueError("derived cavity cannot host the requested well count")
        angles = tuple(0.0 for _ in centers)
        petal_scale = 0.0
    else:
        r_lim = _inradius(form, cav_hx, cav_hy) - cav_margin
        petal_scale, _petal_ring_u, centers, angles = _pack_petal_wells(config.well_count, r_lim)
        if petal_scale < 0.006:
            raise ValueError("derived cavity cannot host the requested petal pack")
        well_r = _PETAL_REACH * petal_scale
    centers = tuple(centers)
    well_wall_thk = max(0.0007, 0.075 * well_r)
    well_floor_thk = max(0.00055, 0.05 * well_r)
    well_depth = min(max(0.0028, 0.42 * height), front_band_lo - floor_h + 0.0030)
    cake_r = well_r - well_wall_thk - 0.00025
    cake_h = max(0.0012, fill * (well_depth - well_floor_thk))
    if cake_r <= 0.0012:
        raise ValueError("derived pressed cake radius is degenerate")
    if cake_h >= well_depth:
        raise ValueError("derived pressed cake stands above its metal cup")

    return ResolvedConfig(
        case_form=form,
        lid_motion=config.lid_motion,
        lid_module=config.lid_module,
        closure=config.closure,
        powder_insert=config.powder_insert,
        well_count=int(config.well_count),
        palette=config.palette,
        name=config.name,
        case_span_m=span,
        case_height_m=height,
        lid_open_angle_rad=open_angle,
        slide_travel_ratio=travel_ratio,
        button_travel_m=button_travel,
        latch_lock_angle_rad=lock_angle,
        well_fill_ratio=fill,
        hx_m=hx,
        hy_m=hy,
        corner_r_m=corner_r,
        wall_thk_m=wall_thk,
        floor_h_m=floor_h,
        rim_h_m=rim_h,
        rim_lip_m=rim_lip,
        cav_hx_m=cav_hx,
        cav_hy_m=cav_hy,
        cav_corner_r_m=cav_cr,
        tray_thk_m=tray_thk,
        profile_segments=segments,
        front_band_lo_m=front_band_lo,
        front_band_hi_m=front_band_hi,
        closure_z_m=closure_z,
        closure_h_m=closure_h,
        lid_hx_m=lid_hx,
        lid_hy_m=lid_hy,
        lid_corner_r_m=lid_cr,
        lid_over_m=lid_over,
        panel_thk_m=panel_thk,
        skirt_thk_m=skirt_thk,
        skirt_drop_m=skirt_drop,
        skirt_cut_y_m=skirt_cut_y,
        lid_front_y_m=lid_front_y,
        engage_z_m=engage_z,
        hinge_r_m=hinge_r,
        pin_r_m=pin_r,
        bore_r_m=bore_r,
        hinge_y_m=hinge_y,
        hinge_z_m=hinge_z,
        barrel_half_m=barrel_half,
        knuckle_in_m=knuckle_in,
        knuckle_out_m=knuckle_out,
        slide_travel_m=slide_travel,
        post_r_m=post_r,
        post_head_r_m=post_head_r,
        post_x_m=post_x,
        post_y_m=post_y,
        slot_half_w_m=slot_half_w,
        btn_cap_w_m=btn_cap_w,
        btn_cap_h_m=btn_cap_h,
        btn_cap_out_m=btn_cap_out,
        btn_stem_w_m=btn_stem_w,
        btn_stem_h_m=btn_stem_h,
        btn_lug_w_m=btn_lug_w,
        btn_lug_h_m=btn_lug_h,
        btn_lug_thk_m=btn_lug_thk,
        btn_cbore_depth_m=btn_cbore_depth,
        btn_clearance_m=btn_clearance,
        latch_pivot_y_m=latch_pivot_y,
        latch_pivot_z_m=latch_pivot_z,
        latch_boss_r_m=latch_boss_r,
        latch_bore_r_m=latch_bore_r,
        latch_pin_r_m=latch_pin_r,
        latch_boss_half_m=latch_boss_half,
        latch_lug_in_m=latch_lug_in,
        latch_lug_out_m=latch_lug_out,
        latch_bar_hw_m=latch_bar_hw,
        latch_bar_thk_m=latch_bar_thk,
        latch_len_m=latch_len,
        latch_hook_len_m=latch_hook_len,
        latch_hook_thk_m=latch_hook_thk,
        latch_recess_hw_m=latch_recess_hw,
        latch_gap_m=latch_gap,
        well_outer_r_m=well_r,
        well_wall_thk_m=well_wall_thk,
        well_floor_thk_m=well_floor_thk,
        well_depth_m=well_depth,
        cake_r_m=cake_r,
        cake_h_m=cake_h,
        petal_scale_m=petal_scale,
        well_centers=centers,
        well_angles_deg=tuple(angles),
        well_open_gap_m=well_open_gap,
        cav_margin_m=cav_margin,
    )


# --------------------------------------------------------------------------- #
# materials
# --------------------------------------------------------------------------- #

_PALETTE_SPECS: dict[str, dict[str, object]] = {
    "polished_gold_champagne": {
        "case": (0.92, 0.69, 0.27, 1.0),
        "accent": (0.96, 0.83, 0.54, 1.0),
        "lid": (0.90, 0.67, 0.26, 1.0),
        "inlay": (0.025, 0.022, 0.024, 1.0),
        "plaque": (0.48, 0.34, 0.16, 1.0),
        "mirror": (0.85, 0.87, 0.90, 1.0),
        "cup": (0.62, 0.47, 0.24, 1.0),
        "powders": (
            (0.86, 0.68, 0.49, 1.0),
            (0.68, 0.23, 0.42, 1.0),
            (0.77, 0.46, 0.38, 1.0),
            (0.25, 0.16, 0.17, 1.0),
        ),
    },
    "gloss_black_peach": {
        "case": (0.030, 0.032, 0.036, 1.0),
        "accent": (0.13, 0.14, 0.16, 1.0),
        "lid": (0.055, 0.058, 0.062, 1.0),
        "inlay": (0.10, 0.28, 0.30, 1.0),
        "plaque": (0.10, 0.28, 0.30, 1.0),
        "mirror": (0.83, 0.86, 0.89, 1.0),
        "cup": (0.36, 0.24, 0.20, 1.0),
        "powders": (
            (0.93, 0.64, 0.52, 1.0),
            (0.88, 0.72, 0.56, 1.0),
            (0.95, 0.82, 0.72, 1.0),
            (0.85, 0.60, 0.55, 1.0),
        ),
    },
    "pearl_rose": {
        "case": (0.94, 0.83, 0.83, 1.0),
        "accent": (0.99, 0.93, 0.92, 1.0),
        "lid": (0.91, 0.76, 0.77, 1.0),
        "inlay": (0.55, 0.31, 0.34, 1.0),
        "plaque": (0.72, 0.52, 0.42, 1.0),
        "mirror": (0.88, 0.90, 0.92, 1.0),
        "cup": (0.72, 0.62, 0.58, 1.0),
        "powders": (
            (0.90, 0.55, 0.55, 1.0),
            (0.83, 0.40, 0.46, 1.0),
            (0.94, 0.76, 0.68, 1.0),
            (0.70, 0.32, 0.36, 1.0),
        ),
    },
    "brushed_silver_mauve": {
        "case": (0.74, 0.76, 0.78, 1.0),
        "accent": (0.86, 0.88, 0.90, 1.0),
        "lid": (0.68, 0.70, 0.73, 1.0),
        "inlay": (0.30, 0.26, 0.32, 1.0),
        "plaque": (0.42, 0.38, 0.46, 1.0),
        "mirror": (0.90, 0.92, 0.95, 1.0),
        "cup": (0.55, 0.56, 0.58, 1.0),
        "powders": (
            (0.66, 0.48, 0.56, 1.0),
            (0.78, 0.62, 0.66, 1.0),
            (0.52, 0.36, 0.44, 1.0),
            (0.86, 0.74, 0.74, 1.0),
        ),
    },
    "matte_navy_terracotta": {
        "case": (0.11, 0.15, 0.24, 1.0),
        "accent": (0.20, 0.26, 0.38, 1.0),
        "lid": (0.09, 0.13, 0.21, 1.0),
        "inlay": (0.74, 0.40, 0.27, 1.0),
        "plaque": (0.80, 0.56, 0.30, 1.0),
        "mirror": (0.84, 0.87, 0.90, 1.0),
        "cup": (0.34, 0.30, 0.28, 1.0),
        "powders": (
            (0.79, 0.42, 0.29, 1.0),
            (0.88, 0.60, 0.40, 1.0),
            (0.62, 0.30, 0.24, 1.0),
            (0.92, 0.76, 0.58, 1.0),
        ),
    },
}


def _materials(model: ArticulatedObject, palette: str) -> dict[str, object]:
    spec = _PALETTE_SPECS[palette]
    mats: dict[str, object] = {}
    for key in ("case", "accent", "lid", "inlay", "plaque", "mirror", "cup"):
        mats[key] = model.material(f"{palette}_{key}", rgba=spec[key])
    mats["powders"] = [
        model.material(f"{palette}_powder_{index}", rgba=rgba)
        for index, rgba in enumerate(spec["powders"])
    ]
    return mats


# --------------------------------------------------------------------------- #
# case_form builders
# --------------------------------------------------------------------------- #


def _case_shell_solid(r: ResolvedConfig) -> cq.Workplane:
    outer = _footprint_profile(r.case_form, r.hx_m, r.hy_m, r.corner_r_m, r.profile_segments)
    shell = _cq_prism(outer, 0.0, r.case_height_m)

    rim_hx, rim_hy, rim_cr = _extents_offset(
        r.case_form, r.hx_m, r.hy_m, r.corner_r_m, -(r.wall_thk_m + r.rim_lip_m)
    )
    shell = shell.cut(
        _cq_prism(
            _footprint_profile(r.case_form, rim_hx, rim_hy, rim_cr, r.profile_segments),
            r.floor_h_m,
            r.case_height_m - r.floor_h_m + 0.002,
        )
    )
    shell = shell.cut(
        _cq_prism(
            _footprint_profile(
                r.case_form, r.cav_hx_m, r.cav_hy_m, r.cav_corner_r_m, r.profile_segments
            ),
            r.floor_h_m,
            max(0.0004, r.case_height_m - r.rim_h_m - r.floor_h_m),
        )
    )

    if r.closure == "push_slide_button":
        # Real through-pocket for the button stem plus a shallow bezel recess for
        # the cap so the closure reads as let into the wall.
        bezel_hw = 0.5 * r.btn_cap_w_m + r.btn_clearance_m
        bezel_hh = 0.5 * r.btn_cap_h_m + r.btn_clearance_m
        shell = shell.cut(
            _cq_box(
                -bezel_hw,
                bezel_hw,
                -r.hy_m - 0.0012,
                -r.hy_m + 0.35 * r.wall_thk_m,
                r.closure_z_m - bezel_hh,
                r.closure_z_m + bezel_hh,
            )
        )
        # The pocket guides the stem on its top/bottom faces (a real slide-button
        # housing), so the button keeps bearing contact through the whole stroke;
        # running clearance is taken on the two side faces only.
        pocket_hw = 0.5 * r.btn_stem_w_m + r.btn_clearance_m
        pocket_hh = 0.5 * r.btn_stem_h_m - _SEAT_BITE_M
        shell = shell.cut(
            _cq_box(
                -pocket_hw,
                pocket_hw,
                -r.hy_m - 0.0012,
                -r.hy_m + r.wall_thk_m + 0.0006,
                r.closure_z_m - pocket_hh,
                r.closure_z_m + pocket_hh,
            )
        )
    else:
        # Shallow seat recess in the front wall that the two pivot lugs root into.
        recess_hh = r.latch_boss_r_m + 0.0008
        shell = shell.cut(
            _cq_box(
                -r.latch_lug_out_m,
                r.latch_lug_out_m,
                -r.hy_m - 0.0012,
                -r.hy_m + 0.45 * r.wall_thk_m,
                r.latch_pivot_z_m - recess_hh,
                r.latch_pivot_z_m + recess_hh,
            )
        )
    return shell


def _petal_outline(
    r: ResolvedConfig, angle_deg: float, scale: float | None = None
) -> list[tuple[float, float]]:
    """Petal outline rotated into place and centred on its own radial midpoint."""

    use_scale = r.petal_scale_m if scale is None else scale
    return _petal_polygon(use_scale, angle_deg, (0.0, -_PETAL_MID * use_scale))


def _well_world_outline(r: ResolvedConfig, index: int) -> list[tuple[float, float]]:
    """Each pan's real outline in case coordinates."""

    cx, cy = r.well_centers[index]
    if r.powder_insert == "round_metal_cup":
        base = _circle_polygon(r.well_outer_r_m, 26)
    else:
        base = _petal_outline(r, r.well_angles_deg[index])
    return [(x + cx, y + cy) for x, y in base]


def _tray_hole_profiles(r: ResolvedConfig) -> list[list[tuple[float, float]]]:
    holes: list[list[tuple[float, float]]] = []
    if r.powder_insert == "round_metal_cup":
        for cx, cy in r.well_centers:
            holes.append(
                [
                    (x + cx, y + cy)
                    for x, y in _circle_polygon(r.well_outer_r_m + r.well_open_gap_m, 24)
                ]
            )
    else:
        grow = 1.0 + r.well_open_gap_m / max(r.well_outer_r_m, 1e-4)
        for index, (cx, cy) in enumerate(r.well_centers):
            base = _petal_outline(r, r.well_angles_deg[index], scale=r.petal_scale_m * grow)
            holes.append([(x + cx, y + cy) for x, y in base])
    return holes


def _build_case_body(case: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    candidate = r.case_form
    case.visual(
        mesh_from_cadquery(
            _case_shell_solid(r), f"makeup3_{candidate}_case_shell", tolerance=0.00028
        ),
        material=mats["case"],
        name=f"case_form__{candidate}__shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette in {"gloss_black_peach", "pearl_rose"} else "metal.brushed_silver"),
    )
    floor_hx, floor_hy, floor_cr = _extents_offset(
        r.case_form, r.hx_m, r.hy_m, r.corner_r_m, -(r.wall_thk_m - _JOIN_BITE_M)
    )
    case.visual(
        mesh_from_geometry(
            ExtrudeGeometry(
                _footprint_profile(r.case_form, floor_hx, floor_hy, floor_cr, r.profile_segments),
                r.floor_h_m,
                cap=True,
                center=False,
            ),
            f"makeup3_{candidate}_case_floor",
        ),
        material=mats["case"],
        name=f"case_form__{candidate}__floor", material_class_id=("plastic.opaque_glossy_molded" if r.palette in {"gloss_black_peach", "pearl_rose"} else "metal.brushed_silver"),
    )
    tray = ExtrudeWithHolesGeometry(
        _footprint_profile(
            r.case_form, r.cav_hx_m, r.cav_hy_m, r.cav_corner_r_m, r.profile_segments
        ),
        _tray_hole_profiles(r),
        r.tray_thk_m + _JOIN_BITE_M,
        cap=True,
        center=False,
    ).translate(0.0, 0.0, r.floor_h_m - _JOIN_BITE_M)
    case.visual(
        mesh_from_geometry(tray, f"makeup3_{candidate}_well_tray"),
        material=mats["accent"],
        name=f"case_form__{candidate}__well_tray", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )


def _case_form_round_build(case: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    _build_case_body(case, r, mats)


def _case_form_rounded_rect_build(case: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    _build_case_body(case, r, mats)


def _case_form_hexagonal_build(case: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    _build_case_body(case, r, mats)


_CASE_BUILDERS = {
    "round": _case_form_round_build,
    "rounded_rect": _case_form_rounded_rect_build,
    "hexagonal": _case_form_hexagonal_build,
}


# --------------------------------------------------------------------------- #
# cover panel and lid modules
# --------------------------------------------------------------------------- #


def _module_recess(r: ResolvedConfig) -> tuple[float, float, float, float]:
    """Inner-face module recess: (depth, hx, hy, corner_r)."""

    depth = 0.34 * r.panel_thk_m
    inset = 0.10 * min(r.hx_m, r.hy_m)
    rx, ry, rc = _extents_offset(r.case_form, r.hx_m, r.hy_m, r.corner_r_m, r.lid_over_m - inset)
    return depth, rx, ry, rc


def _plaque_pocket(r: ResolvedConfig) -> tuple[float, float, float]:
    """Top-face plaque pocket: (depth, half width, half height)."""

    return 0.32 * r.panel_thk_m, 0.24 * r.hx_m, 0.075 * r.hx_m


def _lid_panel_solid(r: ResolvedConfig, off: tuple[float, float]) -> cq.Workplane:
    """Cover panel already expressed in the lid's local frame.

    The offset is folded into every station instead of being applied as a
    trailing ``Workplane.translate``: translating the boolean result compound
    perturbs its tessellation, which showed up as phantom geometry at z=0.
    """

    dy = -off[0]
    z0 = r.case_height_m - _SEAT_BITE_M - off[1]
    profile = [
        (x, y + dy)
        for x, y in _footprint_profile(
            r.case_form, r.lid_hx_m, r.lid_hy_m, r.lid_corner_r_m, r.profile_segments
        )
    ]
    panel = _cq_prism(profile, z0, r.panel_thk_m + _SEAT_BITE_M)

    if r.lid_module == "engraved_plaque":
        depth, hw, hh = _plaque_pocket(r)
        panel = panel.cut(
            _cq_box(
                -hw,
                hw,
                -hh + dy,
                hh + dy,
                z0 + r.panel_thk_m + _SEAT_BITE_M - depth,
                z0 + r.panel_thk_m + 0.001,
            )
        )
    else:
        depth, rx, ry, rc = _module_recess(r)
        panel = panel.cut(
            _cq_prism(
                [
                    (x, y + dy)
                    for x, y in _footprint_profile(r.case_form, rx, ry, rc, r.profile_segments)
                ],
                z0 - 0.001,
                depth + 0.001,
            )
        )
    if r.lid_motion == "guided_slide":
        half_len = 0.5 * r.slide_travel_m + r.slot_half_w_m
        centre_y = r.post_y_m - 0.5 * r.slide_travel_m + dy
        slot = _slot_polygon(r.slot_half_w_m, half_len)
        for sign in (-1.0, 1.0):
            panel = panel.cut(
                _cq_prism(
                    [(x + sign * r.post_x_m, y + centre_y) for x, y in slot],
                    z0 - 0.001,
                    r.panel_thk_m + 0.003,
                )
            )
    return panel


def _lid_module_lacquer_inlay_build(
    lid: object, r: ResolvedConfig, mats: dict[str, object], off: tuple[float, float]
) -> None:
    depth, rx, ry, rc = _module_recess(r)
    z0 = r.case_height_m - _SEAT_BITE_M
    inlay = ExtrudeGeometry(
        _footprint_profile(r.case_form, rx, ry, rc, r.profile_segments),
        depth + _JOIN_BITE_M,
        cap=True,
        center=False,
    ).translate(0.0, -off[0], z0 - off[1])
    lid.visual(
        mesh_from_geometry(inlay, "makeup3_lacquer_inlay_panel"),
        material=mats["inlay"],
        name="lid_module__lacquer_inlay__inlay_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    motif_r = max(0.0012, 0.030 * r.hx_m)
    ring = 0.52 * min(r.hx_m, r.hy_m)
    top = z0 + r.panel_thk_m + _SEAT_BITE_M
    for index in range(8):
        angle = math.radians(45.0 * index)
        cx = ring * math.cos(angle)
        cy = ring * math.sin(angle)
        motif: MeshGeometry | None = None
        for dx, dy in ((-0.9, 0.0), (0.9, 0.0), (0.0, -0.9), (0.0, 0.9)):
            lobe = _mesh_cyl_z(
                motif_r,
                top - _JOIN_BITE_M,
                top + 0.45 * motif_r,
                cx + dx * motif_r,
                cy + dy * motif_r,
            )
            motif = lobe if motif is None else motif.merge(lobe)
        assert motif is not None
        lid.visual(
            mesh_from_geometry(motif.translate(0.0, -off[0], -off[1]), f"makeup3_clover_{index}"),
            material=mats["plaque"],
            name=f"lid_module__lacquer_inlay__clover_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"polished_gold_champagne", "gloss_black_peach", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_aged"),
        )


def _lid_module_engraved_plaque_build(
    lid: object, r: ResolvedConfig, mats: dict[str, object], off: tuple[float, float]
) -> None:
    z0 = r.case_height_m - _SEAT_BITE_M
    top = z0 + r.panel_thk_m + _SEAT_BITE_M
    depth, hw, hh = _plaque_pocket(r)
    plaque = _mesh_box(
        -hw + 0.0004,
        hw - 0.0004,
        -hh + 0.0004,
        hh - 0.0004,
        top - depth - _JOIN_BITE_M,
        top - 0.15 * depth,
    ).translate(0.0, -off[0], -off[1])
    lid.visual(
        mesh_from_geometry(plaque, "makeup3_label_plaque"),
        material=mats["plaque"],
        name="lid_module__engraved_plaque__label_plaque", material_class_id=("metal.blackened_gunmetal" if r.palette in {"polished_gold_champagne", "gloss_black_peach", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_aged"),
    )
    rib_h = max(0.00035, 0.045 * r.panel_thk_m)
    rib_w = max(0.00050, 0.011 * r.hx_m)
    rib_len = 0.34 * min(r.hx_m, r.hy_m)
    rows = 4
    per_row = 5
    for row in range(rows):
        for col in range(per_row):
            cx = (col - (per_row - 1) / 2.0) * (2.0 * r.hx_m * 0.70 / per_row)
            cy = (row - (rows - 1) / 2.0) * (2.0 * r.hy_m * 0.66 / rows)
            if abs(cy) < hh + 0.0012 and abs(cx) < hw + 0.0012:
                continue
            angle = math.radians(38.0 if (row + col) % 2 == 0 else -38.0)
            bar = _mesh_box(
                -0.5 * rib_len,
                0.5 * rib_len,
                -0.5 * rib_w,
                0.5 * rib_w,
                top - _JOIN_BITE_M,
                top + rib_h,
            )
            bar.rotate((0.0, 0.0, 1.0), angle)
            lid.visual(
                mesh_from_geometry(
                    bar.translate(cx, cy - off[0], -off[1]),
                    f"makeup3_herringbone_{row}_{col}",
                ),
                material=mats["accent"],
                name=f"lid_module__engraved_plaque__ridge_{row}_{col}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
            )


def _lid_module_fitted_inner_mirror_build(
    lid: object, r: ResolvedConfig, mats: dict[str, object], off: tuple[float, float]
) -> None:
    depth, rx, ry, rc = _module_recess(r)
    inset = 0.10 * min(r.hx_m, r.hy_m)
    bx, by, bc = _extents_offset(r.case_form, rx, ry, rc, -0.30 * inset)
    z0 = r.case_height_m - _SEAT_BITE_M
    bezel = ExtrudeWithHolesGeometry(
        _footprint_profile(r.case_form, rx, ry, rc, r.profile_segments),
        [_footprint_profile(r.case_form, bx, by, bc, r.profile_segments)],
        depth + _JOIN_BITE_M,
        cap=True,
        center=False,
    ).translate(0.0, -off[0], z0 - off[1])
    lid.visual(
        mesh_from_geometry(bezel, "makeup3_mirror_bezel"),
        material=mats["accent"],
        name="lid_module__fitted_inner_mirror__bezel_ring", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )
    pane_t = max(0.00045, 0.30 * depth)
    pane = ExtrudeGeometry(
        _footprint_profile(r.case_form, bx, by, bc, r.profile_segments),
        pane_t + _JOIN_BITE_M,
        cap=True,
        center=False,
    ).translate(0.0, -off[0], z0 + depth - pane_t - off[1])
    lid.visual(
        mesh_from_geometry(pane, "makeup3_mirror_pane"),
        material=mats["mirror"],
        name="lid_module__fitted_inner_mirror__mirror_pane", material_class_id="glass.mirror",
    )


_LID_MODULE_BUILDERS = {
    "lacquer_inlay": _lid_module_lacquer_inlay_build,
    "engraved_plaque": _lid_module_engraved_plaque_build,
    "fitted_inner_mirror": _lid_module_fitted_inner_mirror_build,
}


def _lid_skirt_geometry(r: ResolvedConfig, off: tuple[float, float]) -> MeshGeometry:
    seg = max(r.profile_segments, 24)
    outer = _footprint_profile(r.case_form, r.lid_hx_m, r.lid_hy_m, r.lid_corner_r_m, seg)
    ix, iy, ic = _extents_offset(
        r.case_form, r.lid_hx_m, r.lid_hy_m, r.lid_corner_r_m, -r.skirt_thk_m
    )
    inner = _footprint_profile(r.case_form, ix, iy, ic, seg)
    profile = _clip_profile_y_max(outer, r.skirt_cut_y_m) + list(
        reversed(_clip_profile_y_max(inner, r.skirt_cut_y_m))
    )
    z0 = r.case_height_m - r.skirt_drop_m
    z1 = r.case_height_m + r.panel_thk_m
    return ExtrudeGeometry(profile, z1 - z0, cap=True, center=False).translate(
        0.0, -off[0], z0 - off[1]
    )


# --------------------------------------------------------------------------- #
# lid_motion builders
# --------------------------------------------------------------------------- #


def _lid_motion_flip_hinge_build(
    model: ArticulatedObject, case: object, r: ResolvedConfig, mats: dict[str, object]
) -> tuple[object, dict[str, object]]:
    off = (r.hinge_y_m, r.hinge_z_m)
    case.visual(
        mesh_from_geometry(
            _mesh_box(
                -r.knuckle_out_m,
                r.knuckle_out_m,
                r.hy_m - r.wall_thk_m - _JOIN_BITE_M,
                r.hinge_y_m + r.hinge_r_m,
                0.40 * r.case_height_m,
                r.case_height_m,
            ),
            "makeup3_flip_hinge_ledge",
        ),
        material=mats["case"],
        name="lid_motion__flip_hinge__hinge_ledge", material_class_id=("plastic.opaque_glossy_molded" if r.palette in {"gloss_black_peach", "pearl_rose"} else "metal.brushed_silver"),
    )
    for index, sign in enumerate((-1.0, 1.0)):
        x0 = min(sign * r.knuckle_in_m, sign * r.knuckle_out_m)
        x1 = max(sign * r.knuckle_in_m, sign * r.knuckle_out_m)
        case.visual(
            mesh_from_geometry(
                _mesh_box(
                    x0,
                    x1,
                    r.hinge_y_m - r.hinge_r_m,
                    r.hinge_y_m + r.hinge_r_m,
                    r.case_height_m - _JOIN_BITE_M,
                    r.hinge_z_m,
                ),
                f"makeup3_flip_hinge_tower_{index}",
            ),
            material=mats["case"],
            name=f"lid_motion__flip_hinge__tower_{index}", material_class_id=("plastic.opaque_glossy_molded" if r.palette in {"gloss_black_peach", "pearl_rose"} else "metal.brushed_silver"),
        )
        case.visual(
            mesh_from_geometry(
                _mesh_tube_x(r.hinge_r_m, r.bore_r_m, x0, x1, r.hinge_y_m, r.hinge_z_m),
                f"makeup3_flip_hinge_knuckle_{index}",
            ),
            material=mats["accent"],
            name=f"lid_motion__flip_hinge__knuckle_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
        )
    case.visual(
        mesh_from_geometry(
            _mesh_cyl_x(r.pin_r_m, -r.knuckle_out_m, r.knuckle_out_m, r.hinge_y_m, r.hinge_z_m),
            "makeup3_flip_hinge_pin",
        ),
        material=mats["accent"],
        name="lid_motion__flip_hinge__hinge_pin", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )

    lid = model.part(
        "lid",
        meta={
            "role": "lid",
            "slot": "lid_motion",
            "candidate": "flip_hinge",
            "captured_hinge": True,
        },
    )
    lid.visual(
        mesh_from_cadquery(_lid_panel_solid(r, off), "makeup3_flip_hinge_panel", tolerance=0.00028),
        material=mats["lid"],
        name="lid_motion__flip_hinge__panel", material_class_id=("plastic.opaque_glossy_molded" if r.palette in {"gloss_black_peach", "pearl_rose"} else "metal.brushed_silver"),
    )
    lid.visual(
        mesh_from_geometry(_lid_skirt_geometry(r, off), "makeup3_flip_hinge_skirt"),
        material=mats["lid"],
        name="lid_motion__flip_hinge__skirt", material_class_id=("plastic.opaque_glossy_molded" if r.palette in {"gloss_black_peach", "pearl_rose"} else "metal.brushed_silver"),
    )
    lid.visual(
        mesh_from_geometry(
            _mesh_box(
                -r.barrel_half_m,
                r.barrel_half_m,
                r.lid_hy_m - 0.0016 - off[0],
                r.hinge_y_m - off[0],
                r.case_height_m + r.panel_thk_m - 0.55 * r.hinge_r_m - off[1],
                r.case_height_m + r.panel_thk_m - off[1],
            ),
            "makeup3_flip_hinge_strap",
        ),
        material=mats["lid"],
        name="lid_motion__flip_hinge__hinge_strap", material_class_id=("plastic.opaque_glossy_molded" if r.palette in {"gloss_black_peach", "pearl_rose"} else "metal.brushed_silver"),
    )
    lid.visual(
        mesh_from_geometry(
            _mesh_tube_x(
                r.hinge_r_m,
                r.bore_r_m,
                -r.barrel_half_m - _SEAT_BITE_M,
                r.barrel_half_m + _SEAT_BITE_M,
                0.0,
                0.0,
            ),
            "makeup3_flip_hinge_barrel",
        ),
        material=mats["accent"],
        name="lid_motion__flip_hinge__hinge_barrel", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )
    _LID_MODULE_BUILDERS[r.lid_module](lid, r, mats, off)

    mate = mate_axes(
        AxisInterface(
            name="case_form.hinge_line",
            point=(0.0, r.hinge_y_m, r.hinge_z_m),
            axis=(-1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=r.bore_r_m,
        ),
        AxisInterface(
            name="lid_motion.hinge_barrel_bore",
            point=(0.0, 0.0, 0.0),
            axis=(-1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=r.pin_r_m,
        ),
    )
    return lid, {
        "name": "case_to_lid",
        "type": ArticulationType.REVOLUTE,
        "mate": mate,
        "limits": MotionLimits(effort=1.2, velocity=2.2, lower=0.0, upper=r.lid_open_angle_rad),
        "axis": mate.axis,
    }


def _lid_motion_guided_slide_build(
    model: ArticulatedObject, case: object, r: ResolvedConfig, mats: dict[str, object]
) -> tuple[object, dict[str, object]]:
    off = (0.0, 0.0)
    head_z0 = r.case_height_m + r.panel_thk_m + 0.00035
    for index, sign in enumerate((-1.0, 1.0)):
        cx = sign * r.post_x_m
        case.visual(
            mesh_from_geometry(
                _mesh_cyl_z(r.post_r_m, r.case_height_m - 0.0016, head_z0, cx, r.post_y_m),
                f"makeup3_guided_slide_post_{index}",
            ),
            material=mats["accent"],
            name=f"lid_motion__guided_slide__guide_post_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
        )
        case.visual(
            mesh_from_geometry(
                _mesh_cyl_z(
                    r.post_head_r_m,
                    head_z0 - _JOIN_BITE_M,
                    head_z0 + max(0.0008, 0.45 * r.post_r_m),
                    cx,
                    r.post_y_m,
                ),
                f"makeup3_guided_slide_head_{index}",
            ),
            material=mats["accent"],
            name=f"lid_motion__guided_slide__retainer_head_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
        )

    lid = model.part(
        "lid",
        meta={
            "role": "lid",
            "slot": "lid_motion",
            "candidate": "guided_slide",
            "captured_slide": True,
        },
    )
    lid.visual(
        mesh_from_cadquery(
            _lid_panel_solid(r, off), "makeup3_guided_slide_panel", tolerance=0.00028
        ),
        material=mats["lid"],
        name="lid_motion__guided_slide__panel", material_class_id=("plastic.opaque_glossy_molded" if r.palette in {"gloss_black_peach", "pearl_rose"} else "metal.brushed_silver"),
    )
    bead_hw = 0.20 * r.hx_m
    bead_h = max(0.0007, 0.30 * r.panel_thk_m)
    top = r.case_height_m - _SEAT_BITE_M + r.panel_thk_m + _SEAT_BITE_M
    lid.visual(
        mesh_from_geometry(
            _mesh_box(
                -bead_hw,
                bead_hw,
                -r.lid_hy_m + 0.0006,
                -r.lid_hy_m + 0.0006 + max(0.0016, 0.05 * r.hy_m),
                top - _JOIN_BITE_M,
                top + bead_h,
            ),
            "makeup3_guided_slide_thumb_bead",
        ),
        material=mats["accent"],
        name="lid_motion__guided_slide__thumb_bead", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )
    _LID_MODULE_BUILDERS[r.lid_module](lid, r, mats, off)

    rim_hx, rim_hy, _ = _extents_offset(
        r.case_form, r.hx_m, r.hy_m, r.corner_r_m, -(r.wall_thk_m + r.rim_lip_m) / 2.0
    )
    mate = mate_planes(
        PlaneInterface(
            name="case_form.rim_seat",
            point=(0.0, 0.0, r.case_height_m),
            normal=(0.0, 0.0, 1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(2.0 * rim_hx, 2.0 * rim_hy),
        ),
        PlaneInterface(
            name="lid_motion.slide_underside",
            point=(0.0, 0.0, r.case_height_m),
            normal=(0.0, 0.0, -1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(2.0 * rim_hx * 0.98, 2.0 * rim_hy * 0.98),
        ),
        gap=-_SEAT_BITE_M,
    )
    return lid, {
        "name": "case_to_lid",
        "type": ArticulationType.PRISMATIC,
        "mate": mate,
        "limits": MotionLimits(effort=3.0, velocity=0.10, lower=0.0, upper=r.slide_travel_m),
        "axis": (0.0, 1.0, 0.0),
    }


_LID_MOTION_BUILDERS = {
    "flip_hinge": _lid_motion_flip_hinge_build,
    "guided_slide": _lid_motion_guided_slide_build,
}


# --------------------------------------------------------------------------- #
# closure builders
# --------------------------------------------------------------------------- #


def _closure_push_slide_button_build(
    model: ArticulatedObject, case: object, r: ResolvedConfig, mats: dict[str, object]
) -> tuple[object, dict[str, object]]:
    button = model.part(
        "closure",
        meta={
            "role": "closure",
            "slot": "closure",
            "candidate": "push_slide_button",
            "captured_in_pocket": True,
        },
    )
    stem_len = r.wall_thk_m - _SEAT_BITE_M + r.btn_lug_thk_m
    cap_inner = -r.btn_cbore_depth_m
    button.visual(
        mesh_from_geometry(
            _mesh_box(
                -0.5 * r.btn_cap_w_m,
                0.5 * r.btn_cap_w_m,
                cap_inner - r.btn_cap_out_m,
                cap_inner,
                -0.5 * r.btn_cap_h_m,
                0.5 * r.btn_cap_h_m,
            ),
            "makeup3_button_cap",
        ),
        material=mats["accent"],
        name="closure__push_slide_button__cap", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )
    button.visual(
        mesh_from_geometry(
            _mesh_box(
                -0.5 * r.btn_stem_w_m,
                0.5 * r.btn_stem_w_m,
                cap_inner - _JOIN_BITE_M,
                stem_len,
                -0.5 * r.btn_stem_h_m,
                0.5 * r.btn_stem_h_m,
            ),
            "makeup3_button_stem",
        ),
        material=mats["accent"],
        name="closure__push_slide_button__stem", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )
    button.visual(
        mesh_from_geometry(
            _mesh_box(
                -0.5 * r.btn_lug_w_m,
                0.5 * r.btn_lug_w_m,
                stem_len - r.btn_lug_thk_m,
                stem_len,
                -0.5 * r.btn_lug_h_m,
                0.5 * r.btn_lug_h_m,
            ),
            "makeup3_button_retainer",
        ),
        material=mats["accent"],
        name="closure__push_slide_button__retainer_lug", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )
    mate = mate_axes(
        AxisInterface(
            name="case_form.closure_pocket_axis",
            point=(0.0, -r.hy_m, r.closure_z_m),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
        ),
        AxisInterface(
            name="closure.button_stem_axis",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
        ),
    )
    return button, {
        "name": "case_to_closure",
        "type": ArticulationType.PRISMATIC,
        "mate": mate,
        "limits": MotionLimits(effort=8.0, velocity=0.04, lower=0.0, upper=r.button_travel_m),
        "axis": (0.0, 1.0, 0.0),
    }


def _closure_toggle_latch_build(
    model: ArticulatedObject, case: object, r: ResolvedConfig, mats: dict[str, object]
) -> tuple[object, dict[str, object]]:
    for index, sign in enumerate((-1.0, 1.0)):
        x0 = min(sign * r.latch_lug_in_m, sign * r.latch_lug_out_m)
        x1 = max(sign * r.latch_lug_in_m, sign * r.latch_lug_out_m)
        case.visual(
            mesh_from_geometry(
                _mesh_box(
                    x0,
                    x1,
                    r.latch_pivot_y_m - r.latch_boss_r_m,
                    -r.hy_m + 0.45 * r.wall_thk_m + _JOIN_BITE_M,
                    r.latch_pivot_z_m - r.latch_boss_r_m - 0.0004,
                    r.latch_pivot_z_m + r.latch_boss_r_m + 0.0004,
                ),
                f"makeup3_latch_lug_{index}",
            ),
            material=mats["case"],
            name=f"closure__toggle_latch__mount_lug_{index}", material_class_id=("plastic.opaque_glossy_molded" if r.palette in {"gloss_black_peach", "pearl_rose"} else "metal.brushed_silver"),
        )
    case.visual(
        mesh_from_geometry(
            _mesh_cyl_x(
                r.latch_pin_r_m,
                -r.latch_lug_out_m,
                r.latch_lug_out_m,
                r.latch_pivot_y_m,
                r.latch_pivot_z_m,
            ),
            "makeup3_latch_pivot_pin",
        ),
        material=mats["accent"],
        name="closure__toggle_latch__pivot_pin", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )

    lever = model.part(
        "closure",
        meta={
            "role": "closure",
            "slot": "closure",
            "candidate": "toggle_latch",
            "captured_pivot": True,
        },
    )
    lever.visual(
        mesh_from_geometry(
            _mesh_tube_x(
                r.latch_boss_r_m,
                r.latch_bore_r_m,
                -r.latch_boss_half_m - _SEAT_BITE_M,
                r.latch_boss_half_m + _SEAT_BITE_M,
                0.0,
                0.0,
            ),
            "makeup3_latch_boss",
        ),
        material=mats["accent"],
        name="closure__toggle_latch__pivot_boss", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )
    lever.visual(
        mesh_from_geometry(
            _mesh_box(
                -r.latch_bar_hw_m,
                r.latch_bar_hw_m,
                -r.latch_len_m,
                0.0,
                -0.5 * r.latch_bar_thk_m,
                0.5 * r.latch_bar_thk_m,
            ),
            "makeup3_latch_bar",
        ),
        material=mats["accent"],
        name="closure__toggle_latch__lever_bar", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )
    lever.visual(
        mesh_from_geometry(
            _mesh_box(
                -r.latch_bar_hw_m,
                r.latch_bar_hw_m,
                -r.latch_len_m,
                -r.latch_len_m + r.latch_hook_thk_m,
                0.5 * r.latch_bar_thk_m - _JOIN_BITE_M,
                0.5 * r.latch_bar_thk_m + r.latch_hook_len_m,
            ),
            "makeup3_latch_hook",
        ),
        material=mats["accent"],
        name="closure__toggle_latch__hook_tab", material_class_id=("metal.blackened_gunmetal" if r.palette in {"gloss_black_peach", "pearl_rose", "brushed_silver_mauve", "matte_navy_terracotta"} else "metal.brass_polished"),
    )
    mate = mate_axes(
        AxisInterface(
            name="case_form.latch_pivot_line",
            point=(0.0, r.latch_pivot_y_m, r.latch_pivot_z_m),
            axis=(-1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=r.latch_bore_r_m,
        ),
        AxisInterface(
            name="closure.pivot_boss_bore",
            point=(0.0, 0.0, 0.0),
            axis=(-1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=r.latch_pin_r_m,
        ),
    )
    return lever, {
        "name": "case_to_closure",
        "type": ArticulationType.REVOLUTE,
        "mate": mate,
        "limits": MotionLimits(effort=2.0, velocity=1.5, lower=0.0, upper=r.latch_lock_angle_rad),
        "axis": mate.axis,
    }


_CLOSURE_BUILDERS = {
    "push_slide_button": _closure_push_slide_button_build,
    "toggle_latch": _closure_toggle_latch_build,
}


# --------------------------------------------------------------------------- #
# powder_insert builders
# --------------------------------------------------------------------------- #


def _powder_pan_part(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, object],
    index: int,
    candidate: str,
) -> tuple[object, tuple[float, float], tuple[float, float]]:
    pan = model.part(
        f"powder_pan_{index}",
        meta={
            "role": "powder_pan",
            "slot": "powder_insert",
            "candidate": candidate,
            "well_index": index,
        },
    )
    if candidate == "round_metal_cup":
        outer = _circle_polygon(r.well_outer_r_m, 26)
        inner = _circle_polygon(r.well_outer_r_m - r.well_wall_thk_m, 26)
        cake = _circle_polygon(r.cake_r_m, 26)
    else:
        angle = r.well_angles_deg[index]
        outer = _petal_outline(r, angle)
        shrink = 1.0 - r.well_wall_thk_m / max(r.well_outer_r_m, 1e-4)
        inner = _petal_outline(r, angle, scale=r.petal_scale_m * shrink)
        cake_shrink = 1.0 - (r.well_wall_thk_m + 0.00025) / max(r.well_outer_r_m, 1e-4)
        cake = _petal_outline(r, angle, scale=r.petal_scale_m * cake_shrink)
    pan.visual(
        mesh_from_geometry(
            ExtrudeGeometry(outer, r.well_floor_thk_m, cap=True, center=False),
            f"makeup3_{candidate}_cup_floor_{index}",
        ),
        material=mats["cup"],
        name=f"powder_insert__{candidate}__cup_floor_{index}", material_class_id=("metal.aluminum_bare" if r.palette in {"polished_gold_champagne", "gloss_black_peach", "pearl_rose", "brushed_silver_mauve"} else "metal.blackened_gunmetal"),
    )
    pan.visual(
        mesh_from_geometry(
            ExtrudeWithHolesGeometry(outer, [inner], r.well_depth_m, cap=True, center=False),
            f"makeup3_{candidate}_cup_wall_{index}",
        ),
        material=mats["cup"],
        name=f"powder_insert__{candidate}__cup_wall_{index}", material_class_id=("metal.aluminum_bare" if r.palette in {"polished_gold_champagne", "gloss_black_peach", "pearl_rose", "brushed_silver_mauve"} else "metal.blackened_gunmetal"),
    )
    powders = mats["powders"]
    pan.visual(
        mesh_from_geometry(
            ExtrudeGeometry(cake, r.cake_h_m + _JOIN_BITE_M, cap=True, center=False).translate(
                0.0, 0.0, r.well_floor_thk_m - _JOIN_BITE_M
            ),
            f"makeup3_{candidate}_cake_{index}",
        ),
        material=powders[index % len(powders)],
        name=f"powder_insert__{candidate}__pressed_cake_{index}", material_class_id="organic.wax",
    )
    bounds = _polygon_bounds(outer)
    size = (bounds[2] - bounds[0], bounds[3] - bounds[1])
    centre = (0.5 * (bounds[0] + bounds[2]), 0.5 * (bounds[1] + bounds[3]))
    return pan, size, centre


def _build_powder_pans(
    model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, object], candidate: str
) -> list[tuple[object, dict[str, object]]]:
    out: list[tuple[object, dict[str, object]]] = []
    for index in range(r.well_count):
        cx, cy = r.well_centers[index]
        pan, size, centre = _powder_pan_part(model, r, mats, index, candidate)
        mate = mate_planes(
            PlaneInterface(
                name=f"case_form.well_seat_{index}",
                point=(cx + centre[0], cy + centre[1], r.floor_h_m),
                normal=(0.0, 0.0, 1.0),
                tangent_u=(1.0, 0.0, 0.0),
                extent=(size[0] + 0.0012, size[1] + 0.0012),
            ),
            PlaneInterface(
                name=f"powder_insert.cup_underside_{index}",
                point=(centre[0], centre[1], 0.0),
                normal=(0.0, 0.0, -1.0),
                tangent_u=(1.0, 0.0, 0.0),
                extent=(max(size[0], 1e-4), max(size[1], 1e-4)),
            ),
            gap=-_SEAT_BITE_M,
        )
        out.append(
            (
                pan,
                {
                    "name": f"case_to_powder_pan_{index}",
                    "type": ArticulationType.FIXED,
                    "mate": mate,
                    "limits": None,
                    "axis": None,
                },
            )
        )
    return out


def _powder_insert_round_metal_cup_build(
    model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, object]
) -> list[tuple[object, dict[str, object]]]:
    return _build_powder_pans(model, r, mats, "round_metal_cup")


def _powder_insert_petal_pressed_pan_build(
    model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, object]
) -> list[tuple[object, dict[str, object]]]:
    return _build_powder_pans(model, r, mats, "petal_pressed_pan")


_POWDER_BUILDERS = {
    "round_metal_cup": _powder_insert_round_metal_cup_build,
    "petal_pressed_pan": _powder_insert_petal_pressed_pan_build,
}


# --------------------------------------------------------------------------- #
# assembly
# --------------------------------------------------------------------------- #


def _apply_joint(
    model: ArticulatedObject, parent: object, child: object, spec: dict[str, object]
) -> None:
    mate = spec["mate"]
    kwargs: dict[str, object] = {"origin": mate.origin}
    if spec["axis"] is not None:
        kwargs["axis"] = spec["axis"]
    if spec["limits"] is not None:
        kwargs["motion_limits"] = spec["limits"]
    model.articulation(spec["name"], spec["type"], parent=parent, child=child, **kwargs)
    register_interface_mate(model, spec["name"], mate)


def build_makeup3(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "makeup3",
            "slot_choices": (
                ("case_form", r.case_form),
                ("lid_motion", r.lid_motion),
                ("lid_module", r.lid_module),
                ("closure", r.closure),
                ("powder_insert", r.powder_insert),
                ("well_count", r.well_count),
            ),
            "source_identity": (
                "shallow makeup compact case, covering lid on a hinge or guided "
                "slide, front closure, and pressed powder inserts"
            ),
            "derived_clearances": {
                "well_outer_r_m": r.well_outer_r_m,
                "cav_margin_m": r.cav_margin_m,
                "skirt_drop_m": r.skirt_drop_m,
                "front_band_lo_m": r.front_band_lo_m,
                "front_band_hi_m": r.front_band_hi_m,
            },
        },
    )
    mats = _materials(model, r.palette)
    case = model.part(
        "case",
        meta={
            "role": "case_body",
            "slot": "case_form",
            "candidate": r.case_form,
            "real_cavity": True,
            "case_span_m": r.case_span_m,
        },
    )
    _CASE_BUILDERS[r.case_form](case, r, mats)
    lid, lid_joint = _LID_MOTION_BUILDERS[r.lid_motion](model, case, r, mats)
    closure, closure_joint = _CLOSURE_BUILDERS[r.closure](model, case, r, mats)
    pans = _POWDER_BUILDERS[r.powder_insert](model, r, mats)

    _apply_joint(model, case, lid, lid_joint)
    _apply_joint(model, case, closure, closure_joint)
    for pan, spec in pans:
        _apply_joint(model, case, pan, spec)
    return model


# --------------------------------------------------------------------------- #
# author tests
# --------------------------------------------------------------------------- #


def _parts_by_role(model: ArticulatedObject, role: str) -> list[object]:
    return [part for part in model.parts if part.meta.get("role") == role]


def run_makeup3_tests(model: ArticulatedObject, config: Config | None = None) -> TestReport:
    r = resolve_config(config or Config())
    ctx = TestContext(model)
    cases = _parts_by_role(model, "case_body")
    lids = _parts_by_role(model, "lid")
    closures = _parts_by_role(model, "closure")
    pans = _parts_by_role(model, "powder_pan")
    case = cases[0] if cases else None
    lid = lids[0] if lids else None
    closure = closures[0] if closures else None
    lid_joint = model.get_articulation("case_to_lid")
    closure_joint = model.get_articulation("case_to_closure")

    ctx.check(
        "category_anchor: makeup compact identity",
        len(cases) == 1
        and len(lids) == 1
        and len(closures) == 1
        and len(pans) == r.well_count
        and len(model.parts) == 3 + r.well_count
        and len(model.articulations) == 2 + r.well_count
        and case is not None
        and lid is not None
        and closure is not None
        and lid_joint.parent == "case"
        and lid_joint.child == "lid"
        and closure_joint.parent == "case"
        and closure_joint.child == "closure",
        details=(
            f"case={len(cases)}, lid={len(lids)}, closure={len(closures)}, "
            f"pans={len(pans)}/{r.well_count}, parts={len(model.parts)}, "
            f"joints={len(model.articulations)}"
        ),
    )
    expected_lid_type = (
        ArticulationType.REVOLUTE if r.lid_motion == "flip_hinge" else ArticulationType.PRISMATIC
    )
    expected_closure_type = (
        ArticulationType.PRISMATIC
        if r.closure == "push_slide_button"
        else ArticulationType.REVOLUTE
    )
    ctx.check(
        "category_anchor: cover and closure mechanisms",
        lid_joint.articulation_type == expected_lid_type
        and closure_joint.articulation_type == expected_closure_type
        and lid_joint.motion_limits is not None
        and math.isclose(lid_joint.motion_limits.lower, 0.0)
        and lid_joint.motion_limits.upper is not None
        and lid_joint.motion_limits.upper > 0.0
        and closure_joint.motion_limits is not None
        and math.isclose(closure_joint.motion_limits.lower, 0.0)
        and closure_joint.motion_limits.upper is not None
        and closure_joint.motion_limits.upper > 0.0,
        details=f"lid={lid_joint}, closure={closure_joint}",
    )
    pan_visuals_ok = True
    for index, pan in enumerate(pans):
        for stem in ("cup_floor", "cup_wall", "pressed_cake"):
            if pan.get_visual(f"powder_insert__{r.powder_insert}__{stem}_{index}") is None:
                pan_visuals_ok = False
    ctx.check(
        "category_anchor: every well is a metal cup plus pressed cake",
        pan_visuals_ok
        and len(pans) >= 1
        and r.cake_r_m < r.well_outer_r_m - r.well_wall_thk_m
        and r.cake_h_m < r.well_depth_m
        and all(
            joint.articulation_type == ArticulationType.FIXED and joint.parent == "case"
            for joint in model.articulations
            if joint.name.startswith("case_to_powder_pan_")
        ),
        details=(
            f"insert={r.powder_insert}, wells={len(pans)}, "
            f"well_r={r.well_outer_r_m:.5f}, cake_r={r.cake_r_m:.5f}, "
            f"cake_h={r.cake_h_m:.5f}, depth={r.well_depth_m:.5f}"
        ),
    )

    outlines = [_well_world_outline(r, index) for index in range(r.well_count)]
    worst = min(
        _boundary_clearance(r.case_form, r.cav_hx_m, r.cav_hy_m, r.cav_corner_r_m, x, y)
        for outline in outlines
        for x, y in outline
    )
    min_pair = None
    if len(outlines) > 1:
        min_pair = min(
            _min_polygon_gap(outlines[i], outlines[j])
            for i in range(len(outlines))
            for j in range(i + 1, len(outlines))
        )
    ctx.check(
        "derived well pack keeps real cavity and inter-well clearance",
        worst >= 0.0008 and (min_pair is None or min_pair >= 0.0005),
        details=(
            f"cavity_clearance={worst:.5f}, pair_clearance="
            f"{'n/a' if min_pair is None else format(min_pair, '.5f')}, "
            f"form={r.case_form}, insert={r.powder_insert}, n={r.well_count}"
        ),
    )

    if r.lid_motion == "flip_hinge":
        ctx.check(
            "flip hinge is a captured pin/knuckle/barrel set on the real axis",
            case is not None
            and case.get_visual("lid_motion__flip_hinge__knuckle_0") is not None
            and case.get_visual("lid_motion__flip_hinge__knuckle_1") is not None
            and case.get_visual("lid_motion__flip_hinge__hinge_pin") is not None
            and lid is not None
            and lid.get_visual("lid_motion__flip_hinge__hinge_barrel") is not None
            and r.bore_r_m - r.pin_r_m >= 0.00030
            and tuple(lid_joint.axis) == (-1.0, 0.0, 0.0)
            and math.isclose(lid_joint.origin.xyz[1], r.hinge_y_m, abs_tol=1e-9)
            and math.isclose(lid_joint.origin.xyz[2], r.hinge_z_m, abs_tol=1e-9)
            and r.hinge_y_m > r.lid_hy_m
            and r.hinge_z_m >= r.case_height_m + r.panel_thk_m,
            details=(
                f"bore-pin={r.bore_r_m - r.pin_r_m:.5f}, axis={tuple(lid_joint.axis)}, "
                f"hinge=({r.hinge_y_m:.5f}, {r.hinge_z_m:.5f}), "
                f"lid_hy={r.lid_hy_m:.5f}"
            ),
        )
        ctx.check(
            "closed cover skirt clears the front closure hardware",
            r.skirt_drop_m > 0.0012
            and r.case_height_m - r.skirt_drop_m > r.front_band_hi_m
            and r.lid_over_m - r.skirt_thk_m >= 0.0006
            and r.skirt_cut_y_m < r.hy_m - r.wall_thk_m,
            details=(
                f"skirt_drop={r.skirt_drop_m:.5f}, band_hi={r.front_band_hi_m:.5f}, "
                f"lid_over={r.lid_over_m:.5f}, skirt_thk={r.skirt_thk_m:.5f}"
            ),
        )
    else:
        ctx.check(
            "guided slide is captured by real posts riding in real cover slots",
            case is not None
            and case.get_visual("lid_motion__guided_slide__guide_post_0") is not None
            and case.get_visual("lid_motion__guided_slide__retainer_head_1") is not None
            and lid is not None
            and r.slot_half_w_m - r.post_r_m >= 0.00040
            and r.post_head_r_m > r.slot_half_w_m
            and tuple(lid_joint.axis) == (0.0, 1.0, 0.0)
            and r.slide_travel_m > 0.008
            and r.post_y_m + r.slot_half_w_m < r.lid_hy_m - 0.0025
            and r.post_y_m - r.slide_travel_m - r.slot_half_w_m > -(r.lid_hy_m - 0.0025)
            and r.post_x_m + r.post_head_r_m < r.lid_hx_m,
            details=(
                f"slot-post={r.slot_half_w_m - r.post_r_m:.5f}, "
                f"head_r={r.post_head_r_m:.5f}, travel={r.slide_travel_m:.5f}, "
                f"post=({r.post_x_m:.5f}, {r.post_y_m:.5f})"
            ),
        )

    if r.closure == "push_slide_button":
        ctx.check(
            "push button is captured by a real wall pocket and retainer lug",
            closure is not None
            and closure.get_visual("closure__push_slide_button__cap") is not None
            and closure.get_visual("closure__push_slide_button__retainer_lug") is not None
            and r.btn_cap_w_m > r.btn_stem_w_m + 2.0 * r.btn_clearance_m
            and r.btn_lug_w_m > r.btn_stem_w_m + 2.0 * r.btn_clearance_m
            and r.btn_cbore_depth_m > r.button_travel_m
            and r.btn_lug_h_m > r.btn_stem_h_m + 4.0 * _SEAT_BITE_M
            and r.closure_z_m + 0.5 * r.btn_cap_h_m <= r.front_band_hi_m + 1e-9
            and r.closure_z_m - 0.5 * r.btn_lug_h_m >= r.front_band_lo_m - 1e-9,
            details=(
                f"cap_w={r.btn_cap_w_m:.5f}, stem_w={r.btn_stem_w_m:.5f}, "
                f"lug_w={r.btn_lug_w_m:.5f}, cbore={r.btn_cbore_depth_m:.5f}, "
                f"travel={r.button_travel_m:.5f}, band="
                f"({r.front_band_lo_m:.5f}, {r.front_band_hi_m:.5f})"
            ),
        )
    else:
        arm = r.latch_len_m - r.latch_hook_thk_m
        rise = r.latch_hook_len_m + 0.5 * r.latch_bar_thk_m
        hook_y = (
            r.latch_pivot_y_m
            - arm * math.cos(r.latch_lock_angle_rad)
            + rise * math.sin(r.latch_lock_angle_rad)
        )
        hook_z = (
            r.latch_pivot_z_m
            + arm * math.sin(r.latch_lock_angle_rad)
            + rise * math.cos(r.latch_lock_angle_rad)
        )
        # Sweep safety: the lever's whole envelope must stay outboard of the cover
        # front face for every angle it can reach.
        sweep_y = -1.0
        for step in range(25):
            angle = r.latch_lock_angle_rad * step / 24.0
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            for y_l, z_l in (
                (0.0, 0.5 * r.latch_bar_thk_m),
                (-r.latch_len_m, 0.5 * r.latch_bar_thk_m),
                (-arm, rise),
                (-r.latch_len_m, rise),
            ):
                sweep_y = max(sweep_y, y_l * cos_a + z_l * sin_a)
        sweep_y = r.latch_pivot_y_m + max(sweep_y, r.latch_boss_r_m)
        ctx.check(
            "toggle latch pivots on a captured pin and its hook engages the cover",
            closure is not None
            and closure.get_visual("closure__toggle_latch__pivot_boss") is not None
            and closure.get_visual("closure__toggle_latch__hook_tab") is not None
            and case is not None
            and case.get_visual("closure__toggle_latch__mount_lug_0") is not None
            and case.get_visual("closure__toggle_latch__pivot_pin") is not None
            and r.latch_bore_r_m - r.latch_pin_r_m >= 0.00030
            and tuple(closure_joint.axis) == (-1.0, 0.0, 0.0)
            and r.latch_lug_in_m >= r.latch_boss_half_m
            and sweep_y <= r.lid_front_y_m - 0.5 * r.latch_gap_m
            and sweep_y < -r.hy_m - 0.0008
            and abs(hook_y - (r.lid_front_y_m - r.latch_gap_m)) <= 5e-5
            and abs(hook_z - r.engage_z_m) <= 5e-5
            and r.engage_z_m > r.front_band_hi_m,
            details=(
                f"bore-pin={r.latch_bore_r_m - r.latch_pin_r_m:.5f}, "
                f"sweep_y={sweep_y:.5f}, lid_front={r.lid_front_y_m:.5f}, "
                f"case_front={-r.hy_m:.5f}, hook=({hook_y:.5f}, {hook_z:.5f}), "
                f"engage_z={r.engage_z_m:.5f}, lever={r.latch_len_m:.5f}, "
                f"hook_len={r.latch_hook_len_m:.5f}"
            ),
        )

    if lid is not None and case is not None:
        closed_lid = ctx.part_world_aabb(lid)
        case_box = ctx.part_world_aabb(case)
        upper = lid_joint.motion_limits.upper if lid_joint.motion_limits else 0.0
        with ctx.pose({lid_joint: upper}):
            open_lid = ctx.part_world_aabb(lid)
        if r.lid_motion == "flip_hinge":
            opened = (
                closed_lid is not None
                and open_lid is not None
                and open_lid[1][2] > closed_lid[1][2] + 0.5 * r.hy_m
            )
        else:
            opened = (
                closed_lid is not None
                and open_lid is not None
                and open_lid[0][1] > closed_lid[0][1] + 0.5 * r.slide_travel_m
            )
        ctx.check(
            "cover closes over the cavity and really opens it",
            closed_lid is not None
            and case_box is not None
            and closed_lid[0][0] <= -r.hx_m + 1e-6
            and closed_lid[1][0] >= r.hx_m - 1e-6
            and closed_lid[0][2]
            >= r.case_height_m
            - (r.skirt_drop_m if r.lid_motion == "flip_hinge" else 0.0)
            - 3.0 * _SEAT_BITE_M
            and opened,
            details=f"closed={closed_lid}, open={open_lid}, case={case_box}",
        )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "tight_rect_four_petal_slide_button",
        {
            "case_form": "rounded_rect",
            "lid_motion": "guided_slide",
            "lid_module": "engraved_plaque",
            "closure": "push_slide_button",
            "powder_insert": "petal_pressed_pan",
            "well_count": 4,
            "case_span_m": 0.070,
            "case_height_m": 0.0135,
            "slide_travel_ratio": 0.52,
            "button_travel_m": 0.0022,
            "well_fill_ratio": 0.94,
        },
        reason="tightest footprint and shortest case with the densest petal pack",
    ),
    corner_case(
        "min_round_four_cups_slide_toggle",
        {
            "case_form": "round",
            "lid_motion": "guided_slide",
            "lid_module": "fitted_inner_mirror",
            "closure": "toggle_latch",
            "powder_insert": "round_metal_cup",
            "well_count": 4,
            "case_span_m": 0.070,
            "case_height_m": 0.0135,
            "slide_travel_ratio": 0.52,
            "latch_lock_angle_rad": 1.32,
            "well_fill_ratio": 0.94,
        },
        reason="sliding cover and toggle lever coexist on the smallest round case",
    ),
    corner_case(
        "max_open_hex_single_petal_hinge",
        {
            "case_form": "hexagonal",
            "lid_motion": "flip_hinge",
            "lid_module": "lacquer_inlay",
            "closure": "push_slide_button",
            "powder_insert": "petal_pressed_pan",
            "well_count": 1,
            "case_span_m": 0.104,
            "case_height_m": 0.0235,
            "lid_open_angle_rad": 1.85,
            "button_travel_m": 0.0022,
            "well_fill_ratio": 0.80,
        },
        reason="widest hexagon at full hinge sweep over a single large petal pan",
    ),
    corner_case(
        "rect_hinge_plaque_toggle_min_lock",
        {
            "case_form": "rounded_rect",
            "lid_motion": "flip_hinge",
            "lid_module": "engraved_plaque",
            "closure": "toggle_latch",
            "powder_insert": "petal_pressed_pan",
            "well_count": 2,
            "case_span_m": 0.074,
            "case_height_m": 0.0135,
            "lid_open_angle_rad": 1.25,
            "latch_lock_angle_rad": 1.00,
            "well_fill_ratio": 0.80,
        },
        reason="shallow skirt with the shallowest latch angle and a short lever",
    ),
    corner_case(
        "hex_slide_mirror_three_cups_max",
        {
            "case_form": "hexagonal",
            "lid_motion": "guided_slide",
            "lid_module": "fitted_inner_mirror",
            "closure": "toggle_latch",
            "powder_insert": "round_metal_cup",
            "well_count": 3,
            "case_span_m": 0.104,
            "case_height_m": 0.0235,
            "slide_travel_ratio": 0.52,
            "latch_lock_angle_rad": 1.00,
            "well_fill_ratio": 0.88,
        },
        reason="hexagonal apothem limits a three-in-a-row cup pack under a slide",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_makeup3",
    "config_from_seed",
    "resolve_config",
    "run_makeup3_tests",
]
