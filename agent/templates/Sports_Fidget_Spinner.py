# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Modular fidget_spinner template.
#
# Identity: a hand-held multi-arm spinning toy lying flat in the XY plane,
# thickness along +Z, centered on the origin.
#   - center_cap  (Slot C, ROOT / held part): the central pinch assembly. Stays
#     still while the body spins. Modules: flat_button / domed_cap / knurled_cap.
#   - spinner_body (Slot A): an N-lobe rotating plate. CONTINUOUS spin about the
#     central +Z axis relative to the cap (cap_to_body). Modules: round_pods /
#     solid_disc / gear_edge.
#   - lobe_weight_i (Slot B) x arm_count: each lobe carries a press-fit
#     bearing/weight that spins CONTINUOUSLY about its own lobe +Z axis relative
#     to the body (body_to_*_i). Modules: open_bearing / domed_weight / hex_weight.
#
# Multiplicity main axis = arm_count: the lobe disc + web + lobe-weight child +
# its spin joint are replicated equal-spacing around the center.

import math
import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Cylinder,
    CylinderGeometry,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    sample_catmull_rom_spline_2d,
)

__modular__ = True

BodyOutline = Literal["round_pods", "solid_disc", "gear_edge"]
LobeWeight = Literal["open_bearing", "domed_weight", "hex_weight"]
CenterCap = Literal["flat_button", "domed_cap", "knurled_cap"]
PaletteStyle = Literal[
    "classic_red_silver",
    "gunmetal_steel",
    "brass_machined",
    "chrome_polished",
    "neon_acid",
    "stealth_black",
]

BODY_OUTLINES: tuple[BodyOutline, ...] = ("round_pods", "solid_disc", "gear_edge")
LOBE_WEIGHTS: tuple[LobeWeight, ...] = ("open_bearing", "domed_weight", "hex_weight")
CENTER_CAPS: tuple[CenterCap, ...] = ("flat_button", "domed_cap", "knurled_cap")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_red_silver",
    "gunmetal_steel",
    "brass_machined",
    "chrome_polished",
    "neon_acid",
    "stealth_black",
)

# Per-seed weighted arm_count domain (small N high frequency, tail rare).
ARM_COUNT_CHOICES: tuple[int, ...] = (2, 3, 4, 5)
ARM_COUNT_WEIGHTS: tuple[float, ...] = (0.20, 0.36, 0.24, 0.20)

# ---- nominal key dimensions (meters), from the 5-star sources ----
BASE_BODY_THICK = 0.011
BASE_LOBE_R = 0.0150
BASE_LOBE_DIST = 0.0250
HUB_R = 0.0098

CAP_HUB_R = 0.0072
CAP_DISC_R = 0.0090
CAP_DISC_T = 0.0020

POCKET_WALL_MIN = 0.0020  # min wall between pocket rim and lobe rim
PRESS_FIT = 0.0003        # bearing outer radius interference past pocket
HUB_WEB_CLEAR = 0.0010    # min clearance so the hub doesn't eat the pocket

# gear tooth dimensions
NUM_TEETH_PER_LOBE = 14
TOOTH_HEIGHT = 0.0030
TOOTH_BASE_W = 0.0038
TOOTH_TIP_W = 0.0018


# palette_style -> material rgba mapping (observed 5-star materials).
def _palette_mats(style: PaletteStyle) -> dict[str, tuple[float, float, float, float]]:
    silver = (0.78, 0.80, 0.83, 1.0)
    gunmetal = (0.38, 0.40, 0.43, 1.0)
    knurl_steel = (0.50, 0.52, 0.55, 1.0)
    rubber_black = (0.06, 0.06, 0.07, 1.0)
    glossy_red = (0.82, 0.07, 0.09, 1.0)
    brass = (0.76, 0.60, 0.12, 1.0)
    chrome = (0.85, 0.87, 0.90, 1.0)

    if style == "classic_red_silver":
        return {
            "body": glossy_red,
            "hub": silver,
            "cap_accent": glossy_red,
            "ring": rubber_black,
            "race": silver,
            "weight": chrome,
            "knurl": knurl_steel,
        }
    if style == "gunmetal_steel":
        return {
            "body": silver,
            "hub": silver,
            "cap_accent": gunmetal,
            "ring": rubber_black,
            "race": silver,
            "weight": gunmetal,
            "knurl": knurl_steel,
        }
    if style == "brass_machined":
        return {
            "body": glossy_red,
            "hub": silver,
            "cap_accent": brass,
            "ring": rubber_black,
            "race": brass,
            "weight": brass,
            "knurl": brass,
        }
    if style == "chrome_polished":
        return {
            "body": silver,
            "hub": silver,
            "cap_accent": chrome,
            "ring": gunmetal,
            "race": chrome,
            "weight": chrome,
            "knurl": chrome,
        }
    if style == "neon_acid":
        return {
            "body": (0.40, 0.85, 0.10, 1.0),
            "hub": silver,
            "cap_accent": (0.65, 0.10, 0.85, 1.0),
            "ring": rubber_black,
            "race": silver,
            "weight": (0.95, 0.65, 0.05, 1.0),
            "knurl": knurl_steel,
        }
    # stealth_black
    return {
        "body": rubber_black,
        "hub": gunmetal,
        "cap_accent": gunmetal,
        "ring": rubber_black,
        "race": silver,
        "weight": silver,
        "knurl": knurl_steel,
    }


@dataclass(frozen=True)
class FidgetSpinnerConfig:
    body_outline: BodyOutline = "round_pods"
    lobe_weight: LobeWeight = "open_bearing"
    center_cap: CenterCap = "flat_button"
    palette_style: PaletteStyle = "classic_red_silver"
    arm_count: int = 3
    body_thick_scale: float = 1.0
    lobe_dist_scale: float = 1.0
    lobe_r_scale: float = 1.0
    name: str = "reference_fidget_spinner"


@dataclass(frozen=True)
class ResolvedFidgetSpinnerConfig:
    body_outline: BodyOutline
    lobe_weight: LobeWeight
    center_cap: CenterCap
    palette_style: PaletteStyle
    arm_count: int
    body_thick: float
    lobe_dist: float
    lobe_r: float
    pocket_r: float
    bearing_outer_r: float
    name: str


def config_from_seed(seed: int) -> FidgetSpinnerConfig:
    rng = random.Random(seed)
    # slot order A -> B -> C -> arm_count -> palette -> scales
    body_outline = rng.choice(BODY_OUTLINES)
    lobe_weight = rng.choice(LOBE_WEIGHTS)
    center_cap = rng.choice(CENTER_CAPS)
    arm_count = rng.choices(ARM_COUNT_CHOICES, weights=ARM_COUNT_WEIGHTS, k=1)[0]
    palette_style = rng.choice(PALETTE_STYLES)
    return FidgetSpinnerConfig(
        body_outline=body_outline,
        lobe_weight=lobe_weight,
        center_cap=center_cap,
        palette_style=palette_style,
        arm_count=arm_count,
        body_thick_scale=round(rng.uniform(0.85, 1.20), 3),
        lobe_dist_scale=round(rng.uniform(0.90, 1.20), 3),
        lobe_r_scale=round(rng.uniform(0.85, 1.10), 3),
        name=f"seeded_fidget_spinner_{seed}",
    )


def resolve_config(config: FidgetSpinnerConfig) -> ResolvedFidgetSpinnerConfig:
    if config.body_outline not in BODY_OUTLINES:
        raise ValueError(f"Unsupported body_outline: {config.body_outline}")
    if config.lobe_weight not in LOBE_WEIGHTS:
        raise ValueError(f"Unsupported lobe_weight: {config.lobe_weight}")
    if config.center_cap not in CENTER_CAPS:
        raise ValueError(f"Unsupported center_cap: {config.center_cap}")
    if config.palette_style not in PALETTE_STYLES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")
    if not 2 <= config.arm_count <= 8:
        raise ValueError("arm_count must be in [2, 8]")

    body_outline = config.body_outline
    lobe_weight = config.lobe_weight
    center_cap = config.center_cap
    arm_count = config.arm_count

    # Compatibility gate: knurled_cap on a 2-bar dumbbell is fine here because
    # the cap hub and caps seat OUTSIDE the body z-range (no interference with
    # bar thickness); the only concern in the spec was hub-vs-bar-thickness,
    # which our cap geometry avoids by construction. Keep all combos legal.

    body_thick = max(0.0085, min(0.0135, BASE_BODY_THICK * config.body_thick_scale))
    lobe_dist = max(0.0210, min(0.0320, BASE_LOBE_DIST * config.lobe_dist_scale))
    lobe_r = max(0.0120, min(0.0170, BASE_LOBE_R * config.lobe_r_scale))

    # Inequality 1: arms must not overlap.
    #   lobe_r <= lobe_dist * sin(pi/arm_count) * k
    k = 0.95
    max_lobe_r_arms = lobe_dist * math.sin(math.pi / arm_count) * k
    lobe_r = min(lobe_r, max_lobe_r_arms)

    # Inequality 3: hub must not eat the pocket.
    #   hub_r + web_clear + pocket_r <= lobe_dist  => pocket_r <= lobe_dist - hub_r - clear
    max_pocket_from_hub = lobe_dist - HUB_R - HUB_WEB_CLEAR

    # Inequality 2: pocket contained in lobe.
    #   pocket_r + wall_min <= lobe_r => pocket_r <= lobe_r - wall_min
    pocket_r = min(lobe_r - POCKET_WALL_MIN, max_pocket_from_hub)
    # Keep pocket physically sensible.
    if pocket_r < 0.0060:
        # Geometry too cramped for this combination: nudge lobe_r up within its
        # arm-overlap ceiling so a real pocket survives.
        lobe_r = min(max_lobe_r_arms, 0.0060 + POCKET_WALL_MIN)
        pocket_r = min(lobe_r - POCKET_WALL_MIN, max_pocket_from_hub)
        if pocket_r < 0.0040:
            raise ValueError(
                f"arm_count={arm_count} too crowded for a valid lobe pocket "
                f"(pocket_r={pocket_r:.5f})"
            )

    bearing_outer_r = pocket_r + PRESS_FIT

    return ResolvedFidgetSpinnerConfig(
        body_outline=body_outline,
        lobe_weight=lobe_weight,
        center_cap=center_cap,
        palette_style=config.palette_style,
        arm_count=arm_count,
        body_thick=body_thick,
        lobe_dist=lobe_dist,
        lobe_r=lobe_r,
        pocket_r=pocket_r,
        bearing_outer_r=bearing_outer_r,
        name=config.name,
    )


def slot_choices_for_seed(seed: int):
    r = resolve_config(config_from_seed(seed))
    return [
        ("body_outline", r.body_outline),
        ("lobe_weight", r.lobe_weight),
        ("center_cap", r.center_cap),
        ("arm_count", str(r.arm_count)),
    ]


# ---------------------------------------------------------------------------
# Geometry helpers (parameterized over the resolved config)
# ---------------------------------------------------------------------------


def _lobe_angles(n: int) -> list[float]:
    base = math.pi / 2.0
    return [base + i * 2.0 * math.pi / n for i in range(n)]


def _lobe_centers(r: ResolvedFidgetSpinnerConfig) -> list[tuple[float, float]]:
    return [
        (r.lobe_dist * math.cos(a), r.lobe_dist * math.sin(a))
        for a in _lobe_angles(r.arm_count)
    ]


def _cut_pockets_and_bore(body: cq.Workplane, r: ResolvedFidgetSpinnerConfig) -> cq.Workplane:
    for cx, cy in _lobe_centers(r):
        pocket = (
            cq.Workplane("XY")
            .center(cx, cy)
            .circle(r.pocket_r)
            .extrude(r.body_thick + 0.004)
            .translate((0.0, 0.0, -0.002))
        )
        body = body.cut(pocket)
    center_bore = (
        cq.Workplane("XY")
        .circle(CAP_HUB_R + 0.0004)
        .extrude(r.body_thick + 0.004)
        .translate((0.0, 0.0, -0.002))
    )
    body = body.cut(center_bore)
    return body


def _base_lobes_and_webs(r: ResolvedFidgetSpinnerConfig) -> cq.Workplane:
    """Central hub disc fused with N lobe discs + tapered web bridges."""
    body = cq.Workplane("XY").circle(HUB_R).extrude(r.body_thick)
    for ang in _lobe_angles(r.arm_count):
        cx = r.lobe_dist * math.cos(ang)
        cy = r.lobe_dist * math.sin(ang)
        lobe = cq.Workplane("XY").center(cx, cy).circle(r.lobe_r).extrude(r.body_thick)
        body = body.union(lobe)
        web = (
            cq.Workplane("XY")
            .center(cx / 2.0, cy / 2.0)
            .transformed(rotate=(0.0, 0.0, math.degrees(ang)))
            .rect(r.lobe_dist, 2.0 * (HUB_R * 0.92))
            .extrude(r.body_thick)
        )
        body = body.union(web)
    return body


def _inject_axle_spider(body: cq.Workplane, r: ResolvedFidgetSpinnerConfig) -> cq.Workplane:
    """Add a central axle pin + 2 cross-spokes inside each lobe pocket so a hex
    weight has something to ride on (used only with lobe_weight=hex_weight)."""
    pin_r = 0.0032
    spoke_w = 0.0012
    for cx, cy in _lobe_centers(r):
        pin = cq.Workplane("XY").center(cx, cy).circle(pin_r).extrude(r.body_thick)
        body = body.union(pin)
        spoke_half_len = (r.pocket_r + 0.0008) / 2.0
        for sa in (0.0, math.pi / 2.0):
            mid_r = spoke_half_len
            sx = cx + mid_r * math.cos(sa)
            sy = cy + mid_r * math.sin(sa)
            spoke = (
                cq.Workplane("XY")
                .center(sx, sy)
                .transformed(rotate=(0.0, 0.0, math.degrees(sa)))
                .rect(spoke_half_len * 2.0, spoke_w)
                .extrude(r.body_thick)
            )
            body = body.union(spoke)
    return body


def _round_pods_body(r: ResolvedFidgetSpinnerConfig) -> cq.Workplane:
    body = _base_lobes_and_webs(r)
    if r.lobe_weight == "hex_weight":
        body = _cut_pockets_and_bore(body, r)
        body = _inject_axle_spider(body, r)
    else:
        body = _cut_pockets_and_bore(body, r)
    try:
        body = body.edges("|Z").fillet(0.0012)
    except Exception:
        pass
    return body


def _solid_disc_body(r: ResolvedFidgetSpinnerConfig) -> cq.Workplane:
    pts = _lobe_centers(r)
    body = cq.Workplane("XY").center(pts[0][0], pts[0][1]).circle(r.lobe_r).extrude(r.body_thick)
    for i in range(1, len(pts)):
        lobe = (
            cq.Workplane("XY").center(pts[i][0], pts[i][1]).circle(r.lobe_r).extrude(r.body_thick)
        )
        body = body.union(lobe)
    hub = cq.Workplane("XY").circle(HUB_R).extrude(r.body_thick)
    body = body.union(hub)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        mx = (pts[i][0] + pts[j][0]) / 2.0
        my = (pts[i][1] + pts[j][1]) / 2.0
        dx = pts[j][0] - pts[i][0]
        dy = pts[j][1] - pts[i][1]
        angle_rad = math.atan2(dy, dx)
        bridge_len = math.hypot(dx, dy) + 2.0 * r.lobe_r
        bridge_width = 2.0 * r.lobe_r
        bridge = (
            cq.Workplane("XY")
            .center(mx, my)
            .transformed(rotate=(0.0, 0.0, math.degrees(angle_rad)))
            .rect(bridge_len, bridge_width)
            .extrude(r.body_thick)
        )
        body = body.union(bridge)
    if r.lobe_weight == "hex_weight":
        body = _cut_pockets_and_bore(body, r)
        body = _inject_axle_spider(body, r)
    else:
        body = _cut_pockets_and_bore(body, r)
    return body


def _make_tooth(base_width: float, tip_width: float, height: float, thickness: float):
    hb = base_width / 2.0
    ht = tip_width / 2.0
    return (
        cq.Workplane("XY")
        .moveTo(-hb, 0.0)
        .lineTo(hb, 0.0)
        .lineTo(ht, height)
        .lineTo(-ht, height)
        .close()
        .extrude(thickness)
    )


def _gear_edge_body(r: ResolvedFidgetSpinnerConfig) -> cq.Workplane:
    body = _base_lobes_and_webs(r)
    for ang in _lobe_angles(r.arm_count):
        cx = r.lobe_dist * math.cos(ang)
        cy = r.lobe_dist * math.sin(ang)
        for i in range(NUM_TEETH_PER_LOBE):
            theta = 2.0 * math.pi * i / NUM_TEETH_PER_LOBE
            tooth = _make_tooth(TOOTH_BASE_W, TOOTH_TIP_W, TOOTH_HEIGHT, r.body_thick)
            tooth = tooth.translate((0.0, r.lobe_r, 0.0))
            tooth = tooth.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(theta))
            tooth = tooth.translate((cx, cy, 0.0))
            body = body.union(tooth)
    if r.lobe_weight == "hex_weight":
        body = _cut_pockets_and_bore(body, r)
        body = _inject_axle_spider(body, r)
    else:
        body = _cut_pockets_and_bore(body, r)
    # small fillet so teeth tips survive; guarded.
    try:
        body = body.edges("|Z").fillet(0.0005)
    except Exception:
        pass
    return body


_BODY_BUILDERS = {
    "round_pods": _round_pods_body,
    "solid_disc": _solid_disc_body,
    "gear_edge": _gear_edge_body,
}
_BODY_VISUAL_NAME = {
    "round_pods": "tri_lobe_body",
    "solid_disc": "solid_plate",
    "gear_edge": "gear_body",
}


# ---- Slot B: lobe weights ----


def _bearing_ring_mesh(name: str, r: ResolvedFidgetSpinnerConfig):
    outer_r = r.bearing_outer_r
    inner_r = max(0.0040, outer_r - 0.0047)
    thick = min(0.010, r.body_thick - 0.001)
    outer = cq.Workplane("XY").circle(outer_r).extrude(thick)
    hole = (
        cq.Workplane("XY")
        .circle(inner_r)
        .extrude(thick + 0.004)
        .translate((0.0, 0.0, -0.002))
    )
    ring = outer.cut(hole)
    return mesh_from_cadquery(ring, name), thick, inner_r


def _bearing_race_mesh(name: str, inner_r: float, thick: float):
    race_hole = max(0.0024, inner_r - 0.0030)
    race = cq.Workplane("XY").circle(inner_r).extrude(thick)
    hole = (
        cq.Workplane("XY")
        .circle(race_hole)
        .extrude(thick + 0.004)
        .translate((0.0, 0.0, -0.002))
    )
    race = race.cut(hole)
    marker = (
        cq.Workplane("XY")
        .center(inner_r - 0.0008, 0.0)
        .box(0.0026, 0.0014, thick + 0.0010, centered=(True, True, True))
        .translate((0.0, 0.0, thick / 2.0))
    )
    race = race.union(marker)
    return mesh_from_cadquery(race, name)


def _dome_weight_mesh(name: str, r: ResolvedFidgetSpinnerConfig):
    dome_r = r.bearing_outer_r
    sphere_r = dome_r + 0.0041
    half_t = r.body_thick / 2.0
    h_offset = math.sqrt(sphere_r**2 - dome_r**2)
    plug = (
        cq.Workplane("XY").circle(dome_r).extrude(r.body_thick).translate((0.0, 0.0, -half_t))
    )
    sphere_top = cq.Workplane("XY").sphere(sphere_r).translate((0.0, 0.0, half_t - h_offset))
    cut_top = (
        cq.Workplane("XY")
        .box(sphere_r * 4, sphere_r * 4, sphere_r * 2)
        .translate((0.0, 0.0, half_t - sphere_r))
    )
    dome_top = sphere_top.cut(cut_top)
    sphere_bot = cq.Workplane("XY").sphere(sphere_r).translate((0.0, 0.0, -half_t + h_offset))
    cut_bot = (
        cq.Workplane("XY")
        .box(sphere_r * 4, sphere_r * 4, sphere_r * 2)
        .translate((0.0, 0.0, -half_t + sphere_r))
    )
    dome_bot = sphere_bot.cut(cut_bot)
    result = plug.union(dome_top).union(dome_bot)
    # off-axis flat facet to break symmetry.
    facet_x = dome_r - 0.003
    cut_w = dome_r + 0.006 - facet_x
    total_z = r.body_thick + 2.0 * (sphere_r - h_offset) + 0.01
    facet_cutter = (
        cq.Workplane("XY")
        .box(cut_w, sphere_r * 4, total_z)
        .translate((facet_x + cut_w / 2.0, 0.0, 0.0))
    )
    result = result.cut(facet_cutter)
    return mesh_from_cadquery(result, name)


def _hex_nut_mesh(name: str, r: ResolvedFidgetSpinnerConfig):
    hex_r = min(0.0110, r.pocket_r - 0.0004)
    hex_thick = min(0.010, r.body_thick - 0.001)
    hole_r = 0.0030
    pts = [
        (hex_r * math.cos(i * 2.0 * math.pi / 6.0), hex_r * math.sin(i * 2.0 * math.pi / 6.0))
        for i in range(6)
    ]
    hex_prism = (
        cq.Workplane("XY").moveTo(pts[0][0], pts[0][1]).polyline(pts[1:]).close().extrude(hex_thick)
    )
    hole = (
        cq.Workplane("XY")
        .circle(hole_r)
        .extrude(hex_thick + 0.004)
        .translate((0.0, 0.0, -0.002))
    )
    nut = hex_prism.cut(hole)
    try:
        nut = nut.edges("|Z").chamfer(0.0006)
    except Exception:
        pass
    return mesh_from_cadquery(nut, name), hex_thick


# ---- Slot C: center caps ----


def _spin_cap_body(name: str, radius: float, height: float):
    cap = cq.Workplane("XY").circle(radius).extrude(height)
    try:
        cap = cap.edges(">Z or <Z").chamfer(0.0005)
    except Exception:
        pass
    return mesh_from_cadquery(cap, name)


def _knurl_ridge(name: str, width: float, depth: float, height: float):
    ridge = cq.Workplane("XY").box(depth, width, height, centered=(True, True, False))
    return mesh_from_cadquery(ridge, name)


def _pinch_dome_profile():
    dome_max_r = 0.0095
    dome_height = 0.0050
    flange_r = 0.0086
    flange_t = 0.0004
    dome_ctrl = [
        (flange_r, flange_t),
        (dome_max_r * 0.92, flange_t + (dome_height - flange_t) * 0.15),
        (dome_max_r, flange_t + (dome_height - flange_t) * 0.35),
        (dome_max_r * 0.80, flange_t + (dome_height - flange_t) * 0.62),
        (dome_max_r * 0.38, flange_t + (dome_height - flange_t) * 0.87),
        (0.0, dome_height),
    ]
    dome_curve = sample_catmull_rom_spline_2d(dome_ctrl, samples_per_segment=10)
    profile = [
        (0.0, 0.0),
        (flange_r, 0.0),
        (flange_r, flange_t),
    ]
    profile.extend(dome_curve)
    return profile


def _pinch_dome_mesh(name: str, flipped: bool = False):
    dome = LatheGeometry(_pinch_dome_profile(), segments=48, closed=True)
    if flipped:
        dome.rotate_x(math.pi)
    return mesh_from_geometry(dome, name)


# ---------------------------------------------------------------------------
# Part builders
# ---------------------------------------------------------------------------


def _build_cap(cap, r: ResolvedFidgetSpinnerConfig, mats: dict[str, object]) -> None:
    half_t = r.body_thick / 2.0
    hub_mat = mats["hub"]
    accent_mat = mats["cap_accent"]
    knurl_mat = mats["knurl"]

    body_top_z = half_t + r.body_thick
    body_bot_z = half_t

    if r.center_cap == "flat_button":
        hub_len = r.body_thick + 0.003
        cap.visual(
            mesh_from_geometry(CylinderGeometry(CAP_HUB_R, hub_len, radial_segments=48), "cap_hub"),
            origin=Origin(xyz=(0.0, 0.0, half_t)),
            material=hub_mat,
            name="cap_hub", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red_silver", "gunmetal_steel", "brass_machined", "chrome_polished", "neon_acid"} else "metal.blackened_gunmetal"),
        )
        cap.visual(
            Cylinder(radius=CAP_DISC_R, length=CAP_DISC_T),
            origin=Origin(xyz=(0.0, 0.0, r.body_thick + CAP_DISC_T / 2.0)),
            material=accent_mat,
            name="cap_button_top", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_steel", "brass_machined", "chrome_polished", "stealth_black"} else "plastic.opaque_glossy_molded"),
        )
        cap.visual(
            Cylinder(radius=CAP_DISC_R, length=CAP_DISC_T),
            origin=Origin(xyz=(0.0, 0.0, -CAP_DISC_T / 2.0)),
            material=accent_mat,
            name="cap_button_bottom", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_steel", "brass_machined", "chrome_polished", "stealth_black"} else "plastic.opaque_glossy_molded"),
        )
        cap.inertial = Inertial.from_geometry(
            Cylinder(radius=CAP_DISC_R, length=hub_len + 2.0 * CAP_DISC_T),
            mass=0.004,
            origin=Origin(xyz=(0.0, 0.0, half_t)),
        )

    elif r.center_cap == "domed_cap":
        hub_len = r.body_thick
        cap.visual(
            mesh_from_geometry(CylinderGeometry(CAP_HUB_R, hub_len, radial_segments=48), "cap_hub"),
            origin=Origin(xyz=(0.0, 0.0, r.body_thick)),
            material=hub_mat,
            name="cap_hub", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red_silver", "gunmetal_steel", "brass_machined", "chrome_polished", "neon_acid"} else "metal.blackened_gunmetal"),
        )
        cap.visual(
            _pinch_dome_mesh("cap_dome_top"),
            origin=Origin(xyz=(0.0, 0.0, body_top_z)),
            material=accent_mat,
            name="cap_dome_top", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_steel", "brass_machined", "chrome_polished", "stealth_black"} else "plastic.opaque_glossy_molded"),
        )
        cap.visual(
            _pinch_dome_mesh("cap_dome_bottom", flipped=True),
            origin=Origin(xyz=(0.0, 0.0, body_bot_z)),
            material=accent_mat,
            name="cap_dome_bottom", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_steel", "brass_machined", "chrome_polished", "stealth_black"} else "plastic.opaque_glossy_molded"),
        )
        cap.inertial = Inertial.from_geometry(
            Cylinder(radius=0.0095, length=hub_len + 0.010),
            mass=0.004,
            origin=Origin(xyz=(0.0, 0.0, r.body_thick)),
        )

    else:  # knurled_cap
        top_cap_r = 0.0110
        top_cap_t = 0.0140
        bottom_cap_r = 0.0110
        bottom_cap_t = 0.0070
        knurl_count = 24
        knurl_w = 0.0010
        knurl_d = 0.0008
        hub_len = r.body_thick + top_cap_t + bottom_cap_t
        hub_center_z = (body_top_z + top_cap_t + (body_bot_z - bottom_cap_t)) / 2.0
        cap.visual(
            mesh_from_geometry(CylinderGeometry(CAP_HUB_R, hub_len, radial_segments=48), "cap_hub"),
            origin=Origin(xyz=(0.0, 0.0, hub_center_z)),
            material=hub_mat,
            name="cap_hub", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red_silver", "gunmetal_steel", "brass_machined", "chrome_polished", "neon_acid"} else "metal.blackened_gunmetal"),
        )
        cap.visual(
            _spin_cap_body("top_cap_body", top_cap_r, top_cap_t),
            origin=Origin(xyz=(0.0, 0.0, body_top_z)),
            material=accent_mat,
            name="top_cap_body", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_steel", "brass_machined", "chrome_polished", "stealth_black"} else "plastic.opaque_glossy_molded"),
        )
        cap.visual(
            _spin_cap_body("bottom_cap_body", bottom_cap_r, bottom_cap_t),
            origin=Origin(xyz=(0.0, 0.0, body_bot_z - bottom_cap_t)),
            material=accent_mat,
            name="bottom_cap_body", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_steel", "brass_machined", "chrome_polished", "stealth_black"} else "plastic.opaque_glossy_molded"),
        )
        top_ridge = _knurl_ridge("top_knurl_ridge", knurl_w, knurl_d, top_cap_t)
        for i in range(knurl_count):
            angle = 2.0 * math.pi * i / knurl_count
            cap.visual(
                top_ridge,
                origin=Origin(
                    xyz=(top_cap_r * math.cos(angle), top_cap_r * math.sin(angle), body_top_z),
                    rpy=(0.0, 0.0, angle),
                ),
                material=knurl_mat,
                name=f"top_ridge_{i}", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_red_silver", "gunmetal_steel", "chrome_polished", "neon_acid", "stealth_black"} else "metal.brass_polished"),
            )
        bot_ridge = _knurl_ridge("bottom_knurl_ridge", knurl_w, knurl_d, bottom_cap_t)
        for i in range(knurl_count):
            angle = 2.0 * math.pi * i / knurl_count
            cap.visual(
                bot_ridge,
                origin=Origin(
                    xyz=(
                        bottom_cap_r * math.cos(angle),
                        bottom_cap_r * math.sin(angle),
                        body_bot_z - bottom_cap_t,
                    ),
                    rpy=(0.0, 0.0, angle),
                ),
                material=knurl_mat,
                name=f"bottom_ridge_{i}", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_red_silver", "gunmetal_steel", "chrome_polished", "neon_acid", "stealth_black"} else "metal.brass_polished"),
            )
        cap.inertial = Inertial.from_geometry(
            Cylinder(radius=top_cap_r, length=hub_len),
            mass=0.008,
            origin=Origin(xyz=(0.0, 0.0, hub_center_z)),
        )


def _build_body(body, r: ResolvedFidgetSpinnerConfig, mats: dict[str, object], assets) -> None:
    half_t = r.body_thick / 2.0
    builder = _BODY_BUILDERS[r.body_outline]
    vname = _BODY_VISUAL_NAME[r.body_outline]
    body.visual(
        mesh_from_cadquery(builder(r), vname),
        material=mats["body"],
        name=vname, material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_red_silver", "brass_machined", "neon_acid", "stealth_black"} else "metal.chrome_polished"),
    )
    body.inertial = Inertial.from_geometry(
        Cylinder(radius=r.lobe_dist + r.lobe_r, length=r.body_thick),
        mass=0.045,
        origin=Origin(xyz=(0.0, 0.0, half_t)),
    )


def _weight_part_name(r: ResolvedFidgetSpinnerConfig, i: int) -> str:
    return {
        "open_bearing": f"bearing_{i}",
        "domed_weight": f"weight_{i}",
        "hex_weight": f"hex_weight_{i}",
    }[r.lobe_weight]


def _weight_elem_name(r: ResolvedFidgetSpinnerConfig, i: int) -> str:
    return {
        "open_bearing": f"bearing_{i}_race",
        "domed_weight": f"weight_{i}_dome",
        "hex_weight": f"hex_weight_{i}_nut",
    }[r.lobe_weight]


def _build_weight(part, r: ResolvedFidgetSpinnerConfig, i: int, mats: dict[str, object]) -> None:
    name = _weight_part_name(r, i)
    if r.lobe_weight == "open_bearing":
        ring_mesh, thick, inner_r = _bearing_ring_mesh(f"{name}_ring", r)
        part.visual(
            ring_mesh,
            origin=Origin(xyz=(0.0, 0.0, -thick / 2.0)),
            material=mats["ring"],
            name=f"{name}_ring", material_class_id=("rubber.smooth_plain" if r.palette_style in {"classic_red_silver", "gunmetal_steel", "brass_machined", "neon_acid", "stealth_black"} else "metal.blackened_gunmetal"),
        )
        part.visual(
            _bearing_race_mesh(f"{name}_race", inner_r, thick),
            origin=Origin(xyz=(0.0, 0.0, -thick / 2.0)),
            material=mats["race"],
            name=f"{name}_race", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red_silver", "gunmetal_steel", "chrome_polished", "neon_acid", "stealth_black"} else "metal.brass_polished"),
        )
        part.inertial = Inertial.from_geometry(
            Cylinder(radius=r.bearing_outer_r, length=thick), mass=0.006
        )
    elif r.lobe_weight == "domed_weight":
        part.visual(
            _dome_weight_mesh(f"{name}_dome", r),
            material=mats["weight"],
            name=f"{name}_dome", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_red_silver", "brass_machined", "chrome_polished", "neon_acid", "stealth_black"} else "metal.blackened_gunmetal"),
        )
        part.inertial = Inertial.from_geometry(
            Cylinder(radius=r.bearing_outer_r, length=r.body_thick + 0.008), mass=0.008
        )
    else:  # hex_weight
        nut_mesh, hex_thick = _hex_nut_mesh(f"{name}_nut", r)
        part.visual(
            nut_mesh,
            origin=Origin(xyz=(0.0, 0.0, -hex_thick / 2.0)),
            material=mats["weight"],
            name=f"{name}_nut", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_red_silver", "brass_machined", "chrome_polished", "neon_acid", "stealth_black"} else "metal.blackened_gunmetal"),
        )
        part.inertial = Inertial.from_geometry(
            Cylinder(radius=0.0110, length=hex_thick), mass=0.008
        )


# ---------------------------------------------------------------------------
# Public build entry points
# ---------------------------------------------------------------------------


def build_fidget_spinner(
    config: FidgetSpinnerConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or FidgetSpinnerConfig()
    r = resolve_config(config)
    assets = assets or AssetContext(
        Path(tempfile.mkdtemp(prefix="articraft-fidget-spinner-assets-"))
    )
    model = ArticulatedObject(name=r.name, assets=assets)

    rgba = _palette_mats(r.palette_style)
    mats = {
        key: model.material(f"fidget_{key}_{r.palette_style}", rgba=value)
        for key, value in rgba.items()
    }

    half_t = r.body_thick / 2.0

    cap = model.part("center_cap")
    _build_cap(cap, r, mats)

    body = model.part("spinner_body")
    _build_body(body, r, mats, assets)
    model.articulation(
        "cap_to_body",
        ArticulationType.CONTINUOUS,
        parent=cap,
        child=body,
        origin=Origin(xyz=(0.0, 0.0, half_t)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.2, velocity=80.0),
        meta={
            "type": "continuous",
            "axis": (0.0, 0.0, 1.0),
            "origin": "central +Z hub axis at plate mid-thickness",
            "range": "continuous",
        },
    )

    for i, (cx, cy) in enumerate(_lobe_centers(r)):
        name = _weight_part_name(r, i)
        part = model.part(name)
        _build_weight(part, r, i, mats)
        model.articulation(
            f"body_to_{name}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=part,
            origin=Origin(xyz=(cx, cy, half_t)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.1, velocity=80.0),
            meta={
                "type": "continuous",
                "axis": (0.0, 0.0, 1.0),
                "origin": "lobe +Z axis at plate mid-thickness",
                "range": "continuous",
            },
        )

    return model


def build_seeded_fidget_spinner(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_fidget_spinner(config_from_seed(seed), assets=assets)


def with_overrides(config: FidgetSpinnerConfig, **kwargs: object) -> FidgetSpinnerConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_fidget_spinner_tests(
    object_model: ArticulatedObject, config: FidgetSpinnerConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    n = r.arm_count

    cap = object_model.get_part("center_cap")
    body = object_model.get_part("spinner_body")
    weight_names = [_weight_part_name(r, i) for i in range(n)]
    weights = [object_model.get_part(nm) for nm in weight_names]
    spin = object_model.get_articulation("cap_to_body")
    body_vis = _BODY_VISUAL_NAME[r.body_outline]

    # --- Cap is on the central axis and is the held root. ---
    cap_pos = ctx.part_world_position(cap)
    ctx.check(
        "center cap on the central axis",
        cap_pos is not None and abs(cap_pos[0]) < 1e-4 and abs(cap_pos[1]) < 1e-4,
        details=f"cap origin={cap_pos}",
    )

    # --- cap_to_body is a CONTINUOUS +Z spin joint. ---
    ctx.check(
        "cap_to_body is continuous about +Z",
        spin.articulation_type == ArticulationType.CONTINUOUS
        and tuple(round(v, 6) for v in spin.axis) == (0.0, 0.0, 1.0),
        details=f"type={spin.articulation_type}, axis={spin.axis}",
    )

    # --- N lobes equal-spaced around the center. ---
    angs = []
    for i, w in enumerate(weights):
        p = ctx.part_world_position(w)
        rad = math.hypot(p[0], p[1])
        ctx.check(
            f"{weight_names[i]} sits out on a lobe",
            abs(rad - r.lobe_dist) < 0.002,
            details=f"radius={rad}, lobe_dist={r.lobe_dist}",
        )
        angs.append(math.atan2(p[1], p[0]))

    def sep(a, b):
        d = abs((a - b) % (2.0 * math.pi))
        return min(d, 2.0 * math.pi - d)

    expected = 2.0 * math.pi / n
    sorted_angs = sorted(angs)
    gaps = [sep(sorted_angs[i], sorted_angs[(i + 1) % n]) for i in range(n)]
    ctx.check(
        f"{n} lobes spaced ~{math.degrees(expected):.0f}deg apart",
        all(abs(g - expected) < 0.12 for g in gaps),
        details=f"gaps_deg={[round(math.degrees(g), 1) for g in gaps]}",
    )

    ctx.check(
        "weight/joint count matches arm_count",
        len(weights) == n
        and sum(1 for j in object_model.articulations if j.name.startswith("body_to_")) == n,
        details=f"weights={len(weights)}, n={n}",
    )

    # --- The body spins about the center relative to the cap (lobe swings). ---
    rest = ctx.part_world_position(weights[0])
    with ctx.pose({spin: math.pi / 3.0}):
        turned = ctx.part_world_position(weights[0])
    moved = math.hypot(turned[0] - rest[0], turned[1] - rest[1])
    ctx.check(
        "spinning the body swings a lobe around the center",
        moved > 0.008,
        details=f"rest={rest}, turned={turned}, moved={moved}",
    )
    # Cap must NOT move when the body spins (it is the held root).
    with ctx.pose({spin: math.pi / 3.0}):
        cap_turned = ctx.part_world_position(cap)
    ctx.check(
        "center cap stays put while body spins",
        cap_turned is not None and math.hypot(cap_turned[0], cap_turned[1]) < 1e-4,
        details=f"cap_turned={cap_turned}",
    )

    # --- Each lobe weight spins about its own lobe axis (AABB swaps x/y). ---
    for i in range(n):
        joint = object_model.get_articulation(f"body_to_{weight_names[i]}")
        elem = _weight_elem_name(r, i)
        ext0 = _ext(ctx.part_element_world_aabb(weights[i], elem=elem))
        with ctx.pose({joint: math.pi / 2.0}):
            ext90 = _ext(ctx.part_element_world_aabb(weights[i], elem=elem))
        ctx.check(
            f"{weight_names[i]} spins detectably about its lobe axis",
            abs(ext0[0] - ext90[1]) < 1.5e-3 and abs(ext0[0] - ext0[1]) > 1e-4,
            details=f"ext0={ext0}, ext90={ext90}",
        )

    # --- Each weight is seated in its lobe pocket (intentional press-fit). ---
    for i in range(n):
        if r.lobe_weight == "hex_weight":
            # axle pin + spider (part of body mesh) passes through hex bore.
            ctx.allow_overlap(
                body,
                weights[i],
                elem_a=body_vis,
                elem_b=_weight_elem_name(r, i),
                reason="Integrated axle pin + spider pass through hex weight center bore.",
            )
        else:
            ctx.allow_overlap(
                weights[i],
                body,
                elem_a=_weight_elem_name(r, i) if r.lobe_weight == "domed_weight" else f"{weight_names[i]}_ring",
                elem_b=body_vis,
                reason="Weight is press-fit into the lobe pocket.",
            )
        ctx.expect_overlap(
            weights[i],
            body,
            axes="z",
            min_overlap=0.003,
            name=f"{weight_names[i]} seated in lobe pocket (thickness)",
        )

    # --- Cap hub seats through the central body bore (intentional). ---
    ctx.allow_overlap(
        cap,
        body,
        elem_a="cap_hub",
        elem_b=body_vis,
        reason="Silver cap hub passes through the central bore of the spinner body.",
    )
    ctx.expect_overlap(
        cap,
        body,
        axes="z",
        min_overlap=0.005,
        name="cap hub passes through body center",
    )

    # --- Body-outline specific identity checks. ---
    body_aabb = ctx.part_world_aabb(body)
    body_dims = [body_aabb[1][k] - body_aabb[0][k] for k in range(3)]
    if r.body_outline == "solid_disc":
        min_span = 2.0 * r.lobe_dist - 2.0 * r.lobe_r
        ctx.check(
            "solid plate spans inter-arm regions (no open gaps)",
            body_dims[0] > min_span and body_dims[1] > min_span,
            details=f"body_dims={body_dims}, min_span={min_span:.4f}",
        )
    elif r.body_outline == "gear_edge":
        smooth_r = r.lobe_dist + r.lobe_r
        max_reach = max(abs(body_aabb[0][1]), abs(body_aabb[1][1]))
        ctx.check(
            "gear teeth protrude beyond smooth lobe radius",
            max_reach > smooth_r + 0.0008,
            details=f"max_reach={max_reach}, smooth_r={smooth_r}",
        )

    ctx.check(
        f"body visual {body_vis} exists",
        body.get_visual(body_vis) is not None,
    )

    return ctx.report()


object_model = build_fidget_spinner()
