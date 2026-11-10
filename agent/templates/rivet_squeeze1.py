# SPDX-License-Identifier: Apache-2.0

"""Hand rivet-squeezer modular template (0611 / rivet_squeeze1).

Sourced from ``articraft_template_authoring/specs_modular_v1/rivet_squeeze1.md``
and the 14 synced 5-star records (origin seed
``rec_use-the-attached-reference-image-as-the-primary-_...f3961d86`` + 13
``rec_rivet_squeeze1_var_*`` slot forks).

Structure (pattern = ``parallel_children``, structural twin of ``nutcracker``):
a central ``head`` chassis part holds all head/nose/bottle visuals; two mirrored
handles ``handle_0`` (side=-1) and ``handle_1`` (side=+1) attach as REVOLUTE
children of the head. ``head_to_handle_1`` is a MIMIC of ``head_to_handle_0`` —
a symmetric two-handle squeeze. Every 5-star record keeps this exact
3-part / 2-REVOLUTE identity; each variant swaps ONE slot's geometry.

Slots (all source-backed, all keep the 2-revolute squeeze):

  * ``handle_topology`` (4): wide_v / long_straight / compact_short / cranked_offset
  * ``head_form`` (4, ③ Primary Form Family): enclosed_cast / inline_steel_linkage /
    squared_cast / round_barrel (lathe revolve)
  * ``nosepiece_form`` (2): single_stack / long_mandrel_stem
  * ``return_mechanism`` (2): none_static / two_handle_return_coils (per-handle coil)
  * ``grip_construction`` (3): two_tone_overmold / single_ribbed_sleeve / closed_loop_ring
  * ``collection_bottle`` (3): compact_underslung / large_canister / angled_side_mount
  * ``spare_tip_count`` (N=3..8): rack/magazine holder with N seated nose tips (handle_0)

The pivot is captured-pin geometry (round ``pivot_lug`` seated inside the machined
cover pocket): the two squeeze REVOLUTE joints OMIT ``MatingContract`` (grandfathered,
AUTHORING Rule 2 captured-pin exception) and are guarded by the flat
articulation-origin baseline + element-scoped ``ctx.allow_overlap`` /
``ctx.expect_overlap`` for the lug/cap seating — mirroring the seed record and the
reviewed ``nutcracker`` sibling. All slot geometry is emitted as inline
``part.visual(...)`` (Rule 1); source cadquery primitives (revolve / helix sweep /
loft / polyline extrude / boolean) are preserved (Rule 3).
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
    Inertial,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot vocabularies
# ---------------------------------------------------------------------------
HandleTopology = Literal["wide_v", "long_straight", "compact_short", "cranked_offset"]
HeadForm = Literal["enclosed_cast", "inline_steel_linkage", "squared_cast", "round_barrel"]
NosepieceForm = Literal["single_stack", "long_mandrel_stem"]
ReturnMechanism = Literal["none_static", "two_handle_return_coils"]
GripConstruction = Literal["two_tone_overmold", "single_ribbed_sleeve", "closed_loop_ring"]
CollectionBottle = Literal["compact_underslung", "large_canister", "angled_side_mount"]
PaletteStyle = Literal[
    "red_cast",
    "orange_industrial",
    "blue_anodized",
    "green_cast",
    "yellow_safety",
    "gunmetal_steel",
]

HANDLE_TOPOLOGIES: tuple[HandleTopology, ...] = (
    "wide_v",
    "long_straight",
    "compact_short",
    "cranked_offset",
)
HEAD_FORMS: tuple[HeadForm, ...] = (
    "enclosed_cast",
    "inline_steel_linkage",
    "squared_cast",
    "round_barrel",
)
NOSEPIECE_FORMS: tuple[NosepieceForm, ...] = ("single_stack", "long_mandrel_stem")
RETURN_MECHANISMS: tuple[ReturnMechanism, ...] = ("none_static", "two_handle_return_coils")
GRIP_CONSTRUCTIONS: tuple[GripConstruction, ...] = (
    "two_tone_overmold",
    "single_ribbed_sleeve",
    "closed_loop_ring",
)
COLLECTION_BOTTLES: tuple[CollectionBottle, ...] = (
    "compact_underslung",
    "large_canister",
    "angled_side_mount",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "red_cast",
    "orange_industrial",
    "blue_anodized",
    "green_cast",
    "yellow_safety",
    "gunmetal_steel",
)

SPARE_TIP_MIN = 3
SPARE_TIP_MAX = 8

# ---------------------------------------------------------------------------
# ⑥ Palette pool (colourways drawn from the 13 observed across the variant set).
# Semantic keys: body_metal (black frame), cover (hero anodized colourway),
# grip_core (black rubber), grip_overmold (coloured rubber), dark_steel, steel,
# bottle (translucent white), badge, spring, panel_dark (recessed panels).
# ---------------------------------------------------------------------------
_COMMON_MATS: dict[str, tuple[float, float, float, float]] = {
    "body_metal": (0.035, 0.040, 0.045, 1.0),
    "grip_core": (0.020, 0.022, 0.024, 1.0),
    "dark_steel": (0.12, 0.14, 0.16, 1.0),
    "steel": (0.48, 0.50, 0.50, 1.0),
    "bottle": (0.92, 0.95, 0.96, 0.48),
    "badge": (0.74, 0.76, 0.76, 1.0),
    "spring": (0.22, 0.24, 0.25, 1.0),
    "panel_dark": (0.10, 0.11, 0.12, 1.0),
}
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "red_cast": {"cover": (0.72, 0.025, 0.030, 1.0), "grip_overmold": (0.82, 0.035, 0.045, 1.0)},
    "orange_industrial": {
        "cover": (0.92, 0.24, 0.025, 1.0),
        "grip_overmold": (0.96, 0.30, 0.035, 1.0),
    },
    "blue_anodized": {"cover": (0.025, 0.20, 0.72, 1.0), "grip_overmold": (0.035, 0.24, 0.78, 1.0)},
    "green_cast": {"cover": (0.055, 0.46, 0.19, 1.0), "grip_overmold": (0.060, 0.065, 0.068, 1.0)},
    "yellow_safety": {"cover": (0.95, 0.72, 0.05, 1.0), "grip_overmold": (0.10, 0.10, 0.11, 1.0)},
    "gunmetal_steel": {"cover": (0.34, 0.37, 0.41, 1.0), "grip_overmold": (0.05, 0.055, 0.06, 1.0)},
}


def _palette_rgba(style: PaletteStyle) -> dict[str, tuple[float, float, float, float]]:
    merged = dict(_COMMON_MATS)
    merged.update(PALETTES[style])
    return merged


# ---------------------------------------------------------------------------
# Shared geometry helpers (ported from the source records; primitive types kept).
# ---------------------------------------------------------------------------
def _beam_between(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    depth: float,
    width: float,
    fillet: float = 0.0,
) -> cq.Workplane:
    """Rounded rectangular member between two points in the XZ plane (seed L19-40)."""
    dx = end[0] - start[0]
    dz = end[2] - start[2]
    length = math.hypot(dx, dz)
    angle = -math.degrees(math.atan2(dz, dx))
    beam = cq.Workplane("XY").box(length, depth, width)
    if fillet > 0.0:
        try:
            beam = beam.edges().fillet(fillet)
        except Exception:
            pass
    return beam.rotate((0, 0, 0), (0, 1, 0), angle).translate(
        ((start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0, (start[2] + end[2]) / 2.0)
    )


def _hex_prism(diameter: float, height: float) -> cq.Workplane:
    return cq.Workplane("XY").polygon(6, diameter).extrude(height)


def _socket_screw() -> cq.Workplane:
    head = cq.Workplane("XZ").circle(0.0062).extrude(0.0038, both=True)
    socket = cq.Workplane("XZ").polygon(6, 0.0055).extrude(0.005, both=True)
    return head.cut(socket)


def _knurled_collar(*, tall: bool = False) -> cq.Workplane:
    """Short seed collar (L53-64) or the tall long-stem chuck collar."""
    if not tall:
        collar = cq.Workplane("XY").circle(0.0145).extrude(0.020)
        ribs, rib_box, rib_z = 16, (0.0026, 0.0040, 0.017), 0.010
    else:
        collar = cq.Workplane("XY").circle(0.0145).extrude(0.052)
        collar = collar.union(
            cq.Workplane("XY").circle(0.0115).extrude(0.007).translate((0.0, 0.0, 0.052))
        )
        ribs, rib_box, rib_z = 20, (0.0023, 0.0038, 0.043), 0.024
    step = 360.0 / ribs
    for i in range(ribs):
        rib = (
            cq.Workplane("XY")
            .box(rib_box[0], rib_box[1], rib_box[2], centered=(True, True, True))
            .translate((0.0, 0.0147, rib_z))
            .rotate((0, 0, 0), (0, 0, 1), i * step)
        )
        collar = collar.union(rib)
    return collar


def _bottle(body_height: float = 0.132, outer_radius: float = 0.028, *, hoops: bool = False):
    """Open-necked thin-wall catch bottle with thread rings (seed L67-98, parametric)."""
    inner_radius = outer_radius - 0.0026
    outer = cq.Workplane("XY").circle(outer_radius).circle(inner_radius).extrude(body_height)
    bottom = cq.Workplane("XY").circle(outer_radius).extrude(0.004)
    shoulder = (
        cq.Workplane("XY")
        .circle(outer_radius)
        .circle(0.015)
        .extrude(0.010)
        .translate((0, 0, body_height - 0.010))
    )
    neck = (
        cq.Workplane("XY")
        .circle(0.018)
        .circle(0.015)
        .extrude(0.026)
        .translate((0, 0, body_height - 0.004))
    )
    outer = outer.union(bottom).union(shoulder).union(neck)
    for z in (body_height + 0.002, body_height + 0.008, body_height + 0.014):
        thread = (
            cq.Workplane("XY").circle(0.0200).circle(0.0176).extrude(0.0018).translate((0, 0, z))
        )
        outer = outer.union(thread)
    if hoops:
        for z in (0.014, 0.032):
            hoop = (
                cq.Workplane("XY")
                .circle(outer_radius + 0.0015)
                .circle(inner_radius)
                .extrude(0.0022)
                .translate((0, 0, z))
            )
            outer = outer.union(hoop)
    return outer


def _revolved_barrel(radius: float, half_depth: float, edge_roll: float, z_center: float):
    """Short lathe-turned barrel with rolled shoulders (round_barrel L53-79). Lathe revolve."""
    profile = [
        (0.0, -half_depth),
        (radius - edge_roll, -half_depth),
        (radius - 0.35 * edge_roll, -half_depth + 0.28 * edge_roll),
        (radius, -half_depth + edge_roll),
        (radius, half_depth - edge_roll),
        (radius - 0.35 * edge_roll, half_depth - 0.28 * edge_roll),
        (radius - edge_roll, half_depth),
        (0.0, half_depth),
    ]
    return (
        cq.Workplane("XY")
        .moveTo(*profile[0])
        .polyline(profile[1:])
        .close()
        .revolve(360.0, (0.0, -half_depth), (0.0, half_depth))
        .translate((0.0, 0.0, z_center))
    )


def _round_rod(start, end, radius: float) -> cq.Workplane:
    direction = cq.Vector(end[0] - start[0], end[1] - start[1], end[2] - start[2])
    solid = cq.Solid.makeCylinder(radius, direction.Length, cq.Vector(*start), direction.normalized())
    return cq.Workplane("XY").newObject([solid])


def _handle_return_spring(side: int) -> cq.Workplane:
    """Per-handle return coil + L-anchor wire near the pivot (return_spring L112-145).

    Mounted on the handle so it swings with it (helix sweep — not downgraded)."""
    sx = float(side)
    a = (sx * 0.010, 0.0, -0.010)
    b = (-sx * 0.038, 0.0, -0.026)
    length = math.hypot(b[0] - a[0], b[2] - a[2])
    angle = -math.degrees(math.atan2(b[2] - a[2], b[0] - a[0]))
    path = cq.Wire.makeHelix(0.005, length, 0.0055)
    coil = (
        cq.Workplane("XZ")
        .center(0.0055, 0.0)
        .circle(0.0013)
        .sweep(path, isFrenet=True)
        .rotate((0, 0, 0), (0, 1, 0), 90.0)
        .translate((-length / 2.0, 0.0, 0.0))
        .rotate((0, 0, 0), (0, 1, 0), angle)
        .translate(((a[0] + b[0]) / 2.0, -0.024, (a[2] + b[2]) / 2.0))
    )
    ul = math.hypot(a[0] - b[0], a[2] - b[2])
    ux, uz = (a[0] - b[0]) / ul, (a[2] - b[2]) / ul
    aend = (sx * 0.010, -0.024, -0.010)
    p0 = (aend[0] - 0.006 * ux, -0.029, aend[2] - 0.006 * uz)
    p1 = (aend[0] + 0.006 * ux, -0.029, aend[2] + 0.006 * uz)
    p2 = (sx * 0.004, -0.013, 0.003)
    l_wire = _round_rod(p0, p1, 0.0015).union(_round_rod(p1, p2, 0.0014))
    return coil.union(l_wire)


def _d_ring_grip(start, end, outer_radius: float = 0.048, wall: float = 0.013, depth: float = 0.034):
    """Closed D-ring loop grip + distal rubber pads (grip_closed_loop_ring L101-154)."""
    dx = end[0] - start[0]
    dz = end[2] - start[2]
    length = math.hypot(dx, dz)
    angle = -math.degrees(math.atan2(dz, dx))

    def ring_section(radius: float, ring_wall: float, extrusion: float) -> cq.Workplane:
        inner_radius = radius - ring_wall
        outer = (
            cq.Workplane("XZ")
            .moveTo(0.0, -radius)
            .lineTo(length - radius, -radius)
            .threePointArc((length, 0.0), (length - radius, radius))
            .lineTo(0.0, radius)
            .close()
            .extrude(extrusion / 2.0, both=True)
        )
        inner = (
            cq.Workplane("XZ")
            .moveTo(ring_wall, -inner_radius)
            .lineTo(length - radius, -inner_radius)
            .threePointArc((length - ring_wall, 0.0), (length - radius, inner_radius))
            .lineTo(ring_wall, inner_radius)
            .close()
            .extrude(extrusion, both=True)
        )
        return outer.cut(inner)

    core = ring_section(outer_radius, wall, depth)
    pad = ring_section(outer_radius + 0.0025, wall + 0.0045, 0.0045)
    pad_start = length * 0.43
    selector = (
        cq.Workplane("XY")
        .box(length - pad_start + 0.012, depth + 0.012, 2.0 * outer_radius + 0.012)
        .translate(((pad_start + length + 0.012) / 2.0, 0.0, 0.0))
    )
    pad = pad.intersect(selector)
    panel_front = pad.translate((0.0, -(depth / 2.0), 0.0))
    panel_back = pad.translate((0.0, depth / 2.0, 0.0))

    def place(shape: cq.Workplane) -> cq.Workplane:
        return shape.rotate((0, 0, 0), (0, 1, 0), angle).translate(start)

    return place(core), place(panel_front), place(panel_back)


def _spare_nose_tip(index: int) -> cq.Workplane:
    """Machined interchangeable nose tip for the magazine (tip_magazine_six L67-103)."""
    outer_radius = 0.0060 + 0.0004 * (index % 3)
    bore_radius = 0.0022
    mounting_stem = (
        cq.Workplane("XZ").circle(0.0040).extrude(0.010, both=True).translate((0.0, -0.006, 0.0))
    )
    hex_flange = (
        cq.Workplane("XZ").polygon(6, 0.0118).extrude(0.004, both=True).translate((0.0, -0.015, 0.0))
    )
    shoulder = (
        cq.Workplane("XZ").circle(0.0050).extrude(0.006, both=True).translate((0.0, -0.021, 0.0))
    )
    nose = (
        cq.Workplane("XZ").circle(outer_radius).extrude(0.014, both=True).translate((0.0, -0.029, 0.0))
    )
    tip = mounting_stem.union(hex_flange).union(shoulder).union(nose)
    bore = cq.Workplane("XZ").circle(bore_radius).extrude(0.024, both=True).translate((0.0, -0.028, 0.0))
    return tip.cut(bore)


# ---------------------------------------------------------------------------
# Handle topology table.  Points are (x, z) magnitudes in a pivot-centered
# local frame; ``side`` mirrors x, ``reach`` scales everything past the pivot
# shoulder (p[0]) so the captured-pivot seating is invariant.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _HandleShape:
    pts: tuple[tuple[float, float], ...]  # p0..pN chained arm segments
    knuckles: tuple[tuple[int, float], ...]  # (point index, radius) forged bends
    grip: tuple[tuple[float, float], tuple[float, float]]  # (g0, g1) grip anchor
    rack: tuple[tuple[float, float], tuple[float, float]]  # rack beam start/end on arm
    rack_y: float
    rack_depth: float
    tip_y: float


_HANDLE_SHAPES: dict[HandleTopology, _HandleShape] = {
    "wide_v": _HandleShape(
        pts=((0.022, -0.009), (0.115, -0.055), (0.245, -0.112)),
        knuckles=(),
        grip=((0.225, -0.104), (0.390, -0.160)),
        rack=((0.152, -0.072), (0.218, -0.102)),
        rack_y=0.0,
        rack_depth=0.027,
        tip_y=0.0,
    ),
    "long_straight": _HandleShape(
        pts=((0.022, -0.009), (0.135, -0.075), (0.173, -0.390)),
        knuckles=((1, 0.0135),),
        grip=((0.165, -0.340), (0.185, -0.550)),
        rack=((0.142, -0.130), (0.153, -0.220)),
        rack_y=0.0,
        rack_depth=0.027,
        tip_y=0.0,
    ),
    "compact_short": _HandleShape(
        pts=((0.018, -0.010), (0.060, -0.060), (0.122, -0.136)),
        knuckles=(),
        grip=((0.105, -0.118), (0.190, -0.214)),
        rack=((0.065, -0.069), (0.112, -0.122)),
        rack_y=0.0,
        rack_depth=0.027,
        tip_y=0.0,
    ),
    "cranked_offset": _HandleShape(
        pts=((0.022, -0.009), (0.108, -0.040), (0.151, -0.105), (0.257, -0.132)),
        knuckles=((1, 0.016), (2, 0.016)),
        grip=((0.232, -0.126), (0.398, -0.158)),
        rack=((0.164, -0.111), (0.226, -0.126)),
        rack_y=-0.013,
        rack_depth=0.006,
        tip_y=-0.020,
    ),
}

# Per-topology squeeze upper (rad), each the empirically-measured travel that
# keeps the whole moving handle (arm + grip) clear of BOTH the centerline (the
# mirror handle) and the static head body, evaluated at the max arm_reach_scale
# (1.10 — the worst case) so the value is safe across the whole reach range.
# Long near-parallel arms sweep a large arc per radian (deep moment arm), so
# their travel is tightly bounded; wide/cranked arms have room; the short
# compact arm's mid-section would swing into the lower housing past ~0.24.
# These are geometric feasibility bounds, not sweep-tuned pass constants.
_TOPOLOGY_BASE_UPPER: dict[HandleTopology, float] = {
    "wide_v": 0.32,
    "long_straight": 0.12,
    "compact_short": 0.22,
    "cranked_offset": 0.30,
}
_GRIP_HALF_WIDTH: dict[GripConstruction, float] = {
    "two_tone_overmold": 0.030,
    "single_ribbed_sleeve": 0.032,
    "closed_loop_ring": 0.050,
}

# Head pivot (world) on the cover, per side.  handle_0 uses -x, handle_1 +x.
_PIVOT_X = 0.050
_PIVOT_Z = 0.012


def _scaled_pts(shape: _HandleShape, reach: float) -> tuple[tuple[float, float], ...]:
    """Scale arm points past the pivot shoulder by ``reach`` (p0 fixed)."""
    out = [shape.pts[0]]
    for x, z in shape.pts[1:]:
        out.append((x * reach, z * reach))
    return tuple(out)


def _scaled_grip(shape: _HandleShape, reach: float):
    (g0x, g0z), (g1x, g1z) = shape.grip
    return ((g0x * reach, g0z * reach), (g1x * reach, g1z * reach))


def _safe_squeeze_upper(r: "ResolvedRivetSqueeze1Config") -> float:
    """Feasible squeeze travel for the resolved handle topology + grip.

    The per-topology base (``_TOPOLOGY_BASE_UPPER``) is the empirically measured
    max-reach-safe travel keeping the whole moving handle clear of the centerline
    and the head; the bulky closed-loop ring shaves a little more off the widest
    arms whose loops crowd the head at full squeeze.
    """
    base = _TOPOLOGY_BASE_UPPER[r.handle_topology]
    if r.grip_construction == "closed_loop_ring" and r.handle_topology in ("wide_v", "cranked_offset"):
        base = min(base, 0.28)
    return round(max(0.10, base), 4)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RivetSqueeze1Config:
    handle_topology: HandleTopology | None = None
    head_form: HeadForm | None = None
    nosepiece_form: NosepieceForm | None = None
    return_mechanism: ReturnMechanism | None = None
    grip_construction: GripConstruction | None = None
    collection_bottle: CollectionBottle | None = None
    spare_tip_count: int | None = None
    palette_style: PaletteStyle = "red_cast"
    arm_reach_scale: float = 1.0
    head_scale: float = 1.0
    nose_scale: float = 1.0
    bottle_scale: float = 1.0
    name: str = "rivet_squeeze1"


@dataclass(frozen=True)
class ResolvedRivetSqueeze1Config:
    handle_topology: HandleTopology
    head_form: HeadForm
    nosepiece_form: NosepieceForm
    return_mechanism: ReturnMechanism
    grip_construction: GripConstruction
    collection_bottle: CollectionBottle
    spare_tip_count: int
    palette_style: PaletteStyle
    arm_reach_scale: float
    head_scale: float
    nose_scale: float
    bottle_scale: float
    squeeze_upper: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> RivetSqueeze1Config:
    rng = random.Random(seed)
    # Weighted procedural sampling: keep the mature baselines a plurality while
    # every source-backed form still appears.
    handle = rng.choices(HANDLE_TOPOLOGIES, weights=[5, 3, 3, 3], k=1)[0]
    head = rng.choices(HEAD_FORMS, weights=[5, 3, 3, 3], k=1)[0]
    nose = rng.choices(NOSEPIECE_FORMS, weights=[5, 3], k=1)[0]
    ret = rng.choices(RETURN_MECHANISMS, weights=[5, 3], k=1)[0]
    grip = rng.choices(GRIP_CONSTRUCTIONS, weights=[5, 3, 3], k=1)[0]
    bottle = rng.choices(COLLECTION_BOTTLES, weights=[5, 3, 3], k=1)[0]
    # small-N common, large-N rare
    n_choices = list(range(SPARE_TIP_MIN, SPARE_TIP_MAX + 1))
    n_weights = [6, 6, 4, 3, 2, 1][: len(n_choices)]
    spare = rng.choices(n_choices, weights=n_weights, k=1)[0]
    return RivetSqueeze1Config(
        handle_topology=handle,
        head_form=head,
        nosepiece_form=nose,
        return_mechanism=ret,
        grip_construction=grip,
        collection_bottle=bottle,
        spare_tip_count=spare,
        palette_style=rng.choice(PALETTE_STYLES),
        arm_reach_scale=round(rng.uniform(0.92, 1.10), 4),
        head_scale=round(rng.uniform(0.94, 1.08), 4),
        nose_scale=round(rng.uniform(0.92, 1.10), 4),
        bottle_scale=round(rng.uniform(0.92, 1.12), 4),
        name=f"seeded_rivet_squeeze1_{seed}",
    )


def resolve_config(config: RivetSqueeze1Config | None = None) -> ResolvedRivetSqueeze1Config:
    cfg = config or RivetSqueeze1Config()
    handle = _pick(cfg.handle_topology, HANDLE_TOPOLOGIES)
    head = _pick(cfg.head_form, HEAD_FORMS)
    nose = _pick(cfg.nosepiece_form, NOSEPIECE_FORMS)
    ret = _pick(cfg.return_mechanism, RETURN_MECHANISMS)
    grip = _pick(cfg.grip_construction, GRIP_CONSTRUCTIONS)
    bottle = _pick(cfg.collection_bottle, COLLECTION_BOTTLES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    spare = int(cfg.spare_tip_count if cfg.spare_tip_count is not None else SPARE_TIP_MIN)
    spare = int(_clamp(spare, SPARE_TIP_MIN, SPARE_TIP_MAX))

    partial = ResolvedRivetSqueeze1Config(
        handle_topology=handle,
        head_form=head,
        nosepiece_form=nose,
        return_mechanism=ret,
        grip_construction=grip,
        collection_bottle=bottle,
        spare_tip_count=spare,
        palette_style=palette_style,
        arm_reach_scale=_clamp(cfg.arm_reach_scale, 0.92, 1.10),
        head_scale=_clamp(cfg.head_scale, 0.94, 1.08),
        nose_scale=_clamp(cfg.nose_scale, 0.92, 1.10),
        bottle_scale=_clamp(cfg.bottle_scale, 0.92, 1.12),
        squeeze_upper=0.30,
        name=cfg.name or "rivet_squeeze1",
    )
    upper = _safe_squeeze_upper(partial)
    return replace(partial, squeeze_upper=round(upper, 4))


def with_overrides(config: RivetSqueeze1Config, **kwargs: object) -> RivetSqueeze1Config:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: RivetSqueeze1Config | ResolvedRivetSqueeze1Config,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedRivetSqueeze1Config) else resolve_config(config)
    return (
        ("handle_topology", r.handle_topology),
        ("head_form", r.head_form),
        ("nosepiece_form", r.nosepiece_form),
        ("return_mechanism", r.return_mechanism),
        ("grip_construction", r.grip_construction),
        ("collection_bottle", r.collection_bottle),
        ("spare_tip_count", str(r.spare_tip_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Head form (Slot B) — inline visuals on ``head``.
# ---------------------------------------------------------------------------
def _emit_head_form(head, r: ResolvedRivetSqueeze1Config, mats) -> None:
    hs = r.head_scale
    form = r.head_form

    # --- Center spine (sealed cassette for the inline steel form). ---
    if form == "inline_steel_linkage":
        spine = cq.Workplane("XY").box(0.052, 0.018, 0.122).translate((0.0, 0.0, 0.009))
    else:
        spine = cq.Workplane("XY").box(0.052, 0.034, 0.075)
        spine = spine.translate((0.0, 0.0, 0.0325))
    try:
        spine = spine.edges().fillet(0.006)
    except Exception:
        pass
    head.visual(mesh_from_cadquery(spine, "rs_head_spine", tolerance=0.0007), material=mats["body_metal"], name="head_spine", material_class_id="metal.blackened_gunmetal")

    # --- Diagonal side links (bridge cover <-> lower housing; shared). ---
    link_specs = []
    link_cutters = []
    for lside, ltag in ((-1, "left"), (1, "right")):
        ltop = (0.033 * lside, 0.0, -0.006)
        lbot = (0.015 * lside, 0.0, -0.062)
        link_specs.append((ltag, _beam_between(ltop, lbot, 0.021, 0.017, 0.004)))
        link_cutters.append(_beam_between(ltop, lbot, 0.023, 0.019, 0.0))

    plate_points = [
        (-0.045 * hs, -0.028),
        (-0.055 * hs, 0.010),
        (-0.042 * hs, 0.050),
        (-0.021 * hs, 0.073),
        (0.021 * hs, 0.073),
        (0.042 * hs, 0.050),
        (0.055 * hs, 0.010),
        (0.045 * hs, -0.028),
    ]

    # --- Upper cover + lower housing per ③ form family. ---
    if form == "enclosed_cast":
        red_body = cq.Workplane("XZ").polyline(plate_points).close().extrude(0.013, both=True)
        try:
            red_body = red_body.edges("|Y").fillet(0.004)
        except Exception:
            pass
        for cutter in link_cutters:
            red_body = red_body.cut(cutter)
        head.visual(mesh_from_cadquery(red_body, "rs_red_head_body", tolerance=0.0007), material=mats["cover"], name="red_head_body", material_class_id=("metal.paint_coated" if r.palette_style in {"red_cast", "orange_industrial", "green_cast", "yellow_safety", "gunmetal_steel"} else "metal.aluminum_bare"))

        lower = cq.Workplane("XY").box(0.057 * hs, 0.038, 0.056).translate((0.0, 0.0, -0.078))
        try:
            lower = lower.edges("|Y").fillet(0.006)
        except Exception:
            pass
        for cutter in link_cutters:
            lower = lower.cut(cutter)
        head.visual(mesh_from_cadquery(lower, "rs_lower_housing", tolerance=0.0007), material=mats["body_metal"], name="lower_housing", material_class_id="metal.blackened_gunmetal")

    elif form == "inline_steel_linkage":
        inner_points = [
            (-0.033, -0.016), (-0.041, 0.011), (-0.032, 0.041), (-0.014, 0.060),
            (0.014, 0.060), (0.032, 0.041), (0.041, 0.011), (0.033, -0.016),
        ]
        front_plate = cq.Workplane("XZ").polyline(plate_points).close().extrude(0.002, both=True).translate((0.0, -0.012, 0.0))
        rear_plate = cq.Workplane("XZ").polyline(plate_points).close().extrude(0.002, both=True).translate((0.0, 0.012, 0.0))
        plate_bridge = (
            cq.Workplane("XZ").polyline(plate_points).close().extrude(0.0105, both=True)
            .cut(cq.Workplane("XZ").polyline(inner_points).close().extrude(0.012, both=True))
        )
        plate_bridge = plate_bridge.union(
            cq.Workplane("XY").box(0.008, 0.021, 0.100).translate((0.0, 0.0, 0.023))
        )
        for pivot_x in (-_PIVOT_X, _PIVOT_X):
            lug_clearance = cq.Workplane("XZ").rect(0.040, 0.046).extrude(0.016, both=True).translate((pivot_x, 0.0, 0.005))
            plate_bridge = plate_bridge.cut(lug_clearance)
        for cutter in link_cutters:
            front_plate = front_plate.cut(cutter)
            rear_plate = rear_plate.cut(cutter)
            plate_bridge = plate_bridge.cut(cutter)
        head.visual(mesh_from_cadquery(front_plate, "rs_red_head_body", tolerance=0.0007), material=mats["cover"], name="red_head_body", material_class_id=("metal.paint_coated" if r.palette_style in {"red_cast", "orange_industrial", "green_cast", "yellow_safety", "gunmetal_steel"} else "metal.aluminum_bare"))
        head.visual(mesh_from_cadquery(rear_plate, "rs_rear_head_plate", tolerance=0.0007), material=mats["cover"], name="rear_head_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"red_cast", "orange_industrial", "green_cast", "yellow_safety", "gunmetal_steel"} else "metal.aluminum_bare"))
        head.visual(mesh_from_cadquery(plate_bridge, "rs_head_plate_bridge", tolerance=0.0007), material=mats["dark_steel"], name="head_plate_bridge", material_class_id="metal.blackened_gunmetal")

        lower = cq.Workplane("XY").box(0.057 * hs, 0.038, 0.056).translate((0.0, 0.0, -0.078))
        try:
            lower = lower.edges("|Y").fillet(0.006)
        except Exception:
            pass
        for cutter in link_cutters:
            lower = lower.cut(cutter)
        head.visual(mesh_from_cadquery(lower, "rs_lower_housing", tolerance=0.0007), material=mats["body_metal"], name="lower_housing", material_class_id="metal.blackened_gunmetal")

    elif form == "squared_cast":
        red_body = cq.Workplane("XY").box(0.112 * hs, 0.026, 0.098).translate((0.0, 0.0, 0.022))
        try:
            red_body = red_body.edges().chamfer(0.004)
        except Exception:
            pass
        upper_panel_blank = cq.Workplane("XZ").rect(0.084, 0.066).extrude(0.0010, both=True)
        for panel_y in (-0.013, 0.013):
            red_body = red_body.cut(upper_panel_blank.translate((0.0, panel_y, 0.025)))
        head.visual(mesh_from_cadquery(red_body, "rs_red_head_body", tolerance=0.0007), material=mats["cover"], name="red_head_body", material_class_id=("metal.paint_coated" if r.palette_style in {"red_cast", "orange_industrial", "green_cast", "yellow_safety", "gunmetal_steel"} else "metal.aluminum_bare"))
        upper_panel = cq.Workplane("XZ").rect(0.084, 0.066).extrude(0.0004, both=True)
        for pname, panel_y in (("head_side_panel_front", -0.0125), ("head_side_panel_rear", 0.0125)):
            head.visual(mesh_from_cadquery(upper_panel.translate((0.0, panel_y, 0.025)), f"rs_{pname}", tolerance=0.0005), material=mats["panel_dark"], name=pname, material_class_id="metal.blackened_gunmetal")

        lower = cq.Workplane("XY").box(0.060 * hs, 0.038, 0.058).translate((0.0, 0.0, -0.078))
        try:
            lower = lower.edges().chamfer(0.004)
        except Exception:
            pass
        lower_panel_blank = cq.Workplane("XZ").rect(0.052, 0.030).extrude(0.0015, both=True)
        for panel_y in (-0.019, 0.019):
            lower = lower.cut(lower_panel_blank.translate((0.0, panel_y, -0.064)))
        head.visual(mesh_from_cadquery(lower, "rs_lower_housing", tolerance=0.0007), material=mats["body_metal"], name="lower_housing", material_class_id="metal.blackened_gunmetal")
        lower_panel = cq.Workplane("XZ").rect(0.052, 0.030).extrude(0.0006, both=True)
        for pname, panel_y in (("lower_side_panel_front", -0.0181), ("lower_side_panel_rear", 0.0181)):
            head.visual(mesh_from_cadquery(lower_panel.translate((0.0, panel_y, -0.064)), f"rs_{pname}", tolerance=0.0005), material=mats["dark_steel"], name=pname, material_class_id="metal.blackened_gunmetal")

    else:  # round_barrel — lathe revolve (must not downgrade)
        red_body = _revolved_barrel(0.054 * hs, 0.016, 0.007, 0.018)
        for side in (-1, 1):
            pivot_boss = cq.Workplane("XZ").circle(0.015).extrude(0.018, both=True).translate((_PIVOT_X * side, 0.0, _PIVOT_Z))
            red_body = red_body.union(pivot_boss)
        for x in (-0.036, 0.036):
            screw_sleeve = cq.Workplane("XZ").circle(0.0058).circle(0.0032).extrude(0.016, both=True).translate((x, 0.0, 0.012))
            red_body = red_body.union(screw_sleeve)
        head.visual(mesh_from_cadquery(red_body, "rs_red_head_body", tolerance=0.0010), material=mats["cover"], name="red_head_body", material_class_id=("metal.paint_coated" if r.palette_style in {"red_cast", "orange_industrial", "green_cast", "yellow_safety", "gunmetal_steel"} else "metal.aluminum_bare"))

        lower = _revolved_barrel(0.038 * hs, 0.022, 0.006, -0.074)
        for x in (-0.020, 0.020):
            screw_sleeve = cq.Workplane("XZ").circle(0.0058).circle(0.0032).extrude(0.022, both=True).translate((x, 0.0, -0.064))
            lower = lower.union(screw_sleeve)
        head.visual(mesh_from_cadquery(lower, "rs_lower_housing", tolerance=0.0010), material=mats["body_metal"], name="lower_housing", material_class_id="metal.blackened_gunmetal")

    # --- Side links (all forms). ---
    for ltag, link in link_specs:
        head.visual(mesh_from_cadquery(link, f"rs_side_plate_{ltag}", tolerance=0.0007), material=mats["body_metal"], name=f"side_plate_{ltag}", material_class_id="metal.blackened_gunmetal")

    # --- Central mandrel pull rod (rooted in housing, enclosed by spine). ---
    pull_rod = cq.Workplane("XY").circle(0.0065).extrude(0.120).translate((0.0, 0.0, -0.056))
    head.visual(mesh_from_cadquery(pull_rod, "rs_pull_rod", tolerance=0.0006), material=mats["dark_steel"], name="pull_rod", material_class_id="metal.blackened_gunmetal")


def _emit_head_hardware(head, r: ResolvedRivetSqueeze1Config, mats) -> None:
    """Recessed flush hex fasteners + brand plate/marks (④ host decorations).

    The screw disks straddle the host body's Y-face so their surface touches the
    cover/housing surface (no buried island).  The round barrel's flat Y-ends sit
    deeper (±half_depth) than the flat covers, so its screw seat-y is bumped."""
    if r.head_form == "round_barrel":
        cover_sy, housing_sy = 0.016, 0.022
    else:
        cover_sy, housing_sy = 0.013, 0.019
    for positions, sy, grp in (
        (((-0.036, 0.012), (0.036, 0.012)), cover_sy, "cover"),
        (((-0.020, -0.064), (0.020, -0.064)), housing_sy, "housing"),
    ):
        for j, (sx, sz) in enumerate(positions):
            for sgn, ftag in ((-1, "front"), (1, "rear")):
                yf = sgn * sy
                bolt = cq.Workplane("XZ").circle(0.0060).extrude(0.0013, both=True).translate((sx, yf, sz))
                socket = cq.Workplane("XZ").polygon(6, 0.0052).extrude(0.0011, both=True).translate((sx, yf + sgn * 0.0016, sz))
                shead = bolt.cut(socket)
                head.visual(mesh_from_cadquery(shead, f"rs_{grp}_{ftag}_screw_{j}", tolerance=0.0005), material=mats["dark_steel"], name=f"{grp}_{ftag}_screw_{j}", material_class_id="metal.blackened_gunmetal")

    brand_plate = _beam_between((-0.024, 0, 0.022), (0.024, 0, 0.022), 0.003, 0.019, 0.005).translate((0, -0.0150, 0))
    head.visual(mesh_from_cadquery(brand_plate, "rs_branded_plate", tolerance=0.0006), material=mats["body_metal"], name="branded_plate", material_class_id="metal.blackened_gunmetal")
    for i, width in enumerate((0.014, 0.010, 0.006)):
        mark = cq.Workplane("XY").box(width, 0.0022, 0.0025).translate((0, -0.0170, 0.017 + i * 0.005))
        head.visual(mesh_from_cadquery(mark, f"rs_brand_mark_{i}", tolerance=0.0005), material=mats["badge"], name=f"brand_mark_{i}", material_class_id="metal.brushed_silver")


# ---------------------------------------------------------------------------
# Nosepiece (Slot C) — inline visuals on ``head``.
# ---------------------------------------------------------------------------
def _emit_nosepiece(head, r: ResolvedRivetSqueeze1Config, mats) -> None:
    """Vertical mandrel-pull stack, built with a running z-cursor so each element
    always overlaps the one below (connectivity invariant under nose_scale)."""
    ns = r.nose_scale
    embed = 0.002  # each element seats this far into the one below
    base_z = 0.069  # head top face

    washer = cq.Workplane("XY").circle(0.021).extrude(0.004).translate((0, 0, base_z))
    head.visual(mesh_from_cadquery(washer, "rs_nose_washer", tolerance=0.0005), material=mats["dark_steel"], name="nose_washer", material_class_id="metal.blackened_gunmetal")
    top = base_z + 0.004  # running top of the stack

    if r.nosepiece_form == "single_stack":
        cz = top - embed
        collar_h = 0.020
        collar = _knurled_collar(tall=False).translate((0, 0, cz))
        head.visual(mesh_from_cadquery(collar, "rs_knurled_collar", tolerance=0.0007), material=mats["body_metal"], name="knurled_collar", material_class_id="metal.blackened_gunmetal")
        top = cz + collar_h

        nz = top - embed
        nut_h = 0.026
        lock_nut = _hex_prism(0.035, nut_h).translate((0, 0, nz))
        head.visual(mesh_from_cadquery(lock_nut, "rs_hex_lock_nut", tolerance=0.0005), material=mats["body_metal"], name="hex_lock_nut", material_class_id="metal.blackened_gunmetal")
        top = nz + nut_h

        mz = top - embed
        tip_len = 0.020 * ns  # scale the topmost element's own length (can't open a gap below)
        mandrel_tip = cq.Workplane("XY").rect(0.009, 0.009).extrude(tip_len).translate((0, 0, mz))
        head.visual(mesh_from_cadquery(mandrel_tip, "rs_mandrel_tip", tolerance=0.0004), material=mats["steel"], name="mandrel_tip", material_class_id="metal.steel_bare")
    else:  # long_mandrel_stem — tall ribbed chuck + threaded steel stem
        nz = top - embed
        nut_h = 0.018
        lock_nut = _hex_prism(0.035, nut_h).translate((0, 0, nz))
        head.visual(mesh_from_cadquery(lock_nut, "rs_hex_lock_nut", tolerance=0.0005), material=mats["body_metal"], name="hex_lock_nut", material_class_id="metal.blackened_gunmetal")
        top = nz + nut_h

        cz = top - embed
        collar_h = 0.059  # 0.052 body + 0.007 shoulder
        collar = _knurled_collar(tall=True).translate((0, 0, cz))
        head.visual(mesh_from_cadquery(collar, "rs_knurled_collar", tolerance=0.0007), material=mats["body_metal"], name="knurled_collar", material_class_id="metal.blackened_gunmetal")
        top = cz + collar_h

        # Threaded steel stem built bottom-up from z=0; nose_scale stretches the
        # stem length while the hex chuck + square drive stay stacked on its top.
        stem_len = 0.100 * ns
        mandrel_tip = cq.Workplane("XY").circle(0.0052).extrude(stem_len)
        for i in range(11):
            z = 0.006 + i * 0.007
            if z > stem_len - 0.004:
                break
            crest = cq.Workplane("XY").circle(0.0062).circle(0.0050).extrude(0.0022).translate((0, 0, z))
            mandrel_tip = mandrel_tip.union(crest)
        chuck_z = stem_len - 0.022
        mandrel_tip = mandrel_tip.union(_hex_prism(0.019, 0.024).translate((0, 0, chuck_z)))
        mandrel_tip = mandrel_tip.union(
            cq.Workplane("XY").rect(0.008, 0.008).extrude(0.016).translate((0, 0, chuck_z + 0.020))
        )
        mandrel_tip = mandrel_tip.translate((0, 0, top - embed))
        head.visual(mesh_from_cadquery(mandrel_tip, "rs_mandrel_tip", tolerance=0.0008), material=mats["steel"], name="mandrel_tip", material_class_id="metal.steel_bare")


# ---------------------------------------------------------------------------
# Collection bottle (Slot F) — inline visuals on ``head``.
# ---------------------------------------------------------------------------
def _emit_bottle(head, r: ResolvedRivetSqueeze1Config, mats) -> None:
    bs = r.bottle_scale
    form = r.collection_bottle
    if form == "angled_side_mount":
        bottle_angle = -35.0
        bottle_axis = (0.0, -math.sin(math.radians(bottle_angle)), math.cos(math.radians(bottle_angle)))
        adapter_length = 0.036
        adapter_socket = (0.0, -0.016, -0.074)
        adapter_base = tuple(adapter_socket[i] - bottle_axis[i] * adapter_length for i in range(3))
        bottle_adapter = cq.Workplane("XY").circle(0.015).extrude(adapter_length)
        bottle_adapter = bottle_adapter.union(cq.Workplane("XY").circle(0.022).extrude(0.009).translate((0.0, 0.0, adapter_length - 0.009)))
        for z in (0.002, 0.007, 0.012):
            bottle_adapter = bottle_adapter.union(cq.Workplane("XY").circle(0.018).extrude(0.0018).translate((0.0, 0.0, z)))
        bottle_adapter = bottle_adapter.rotate((0, 0, 0), (1, 0, 0), bottle_angle).translate(adapter_base)
        head.visual(mesh_from_cadquery(bottle_adapter, "rs_bottle_adapter", tolerance=0.0006), material=mats["body_metal"], name="bottle_adapter", material_class_id="metal.blackened_gunmetal")

        body_height = 0.132 * bs
        bottle_top = tuple(adapter_base[i] + bottle_axis[i] * 0.018 for i in range(3))
        bottle_origin = tuple(bottle_top[i] - bottle_axis[i] * (body_height + 0.022) for i in range(3))
        bottle = _bottle(body_height=body_height, outer_radius=0.028).rotate((0, 0, 0), (1, 0, 0), bottle_angle).translate(bottle_origin)
        head.visual(mesh_from_cadquery(bottle, "rs_collection_bottle", tolerance=0.0007), material=mats["bottle"], name="collection_bottle", material_class_id="plastic.frosted_translucent")
        return

    # Straight underslung adapter + bottle.
    bottle_adapter = cq.Workplane("XY").circle(0.021).extrude(0.022).translate((0, 0, -0.104))
    head.visual(mesh_from_cadquery(bottle_adapter, "rs_bottle_adapter", tolerance=0.0006), material=mats["body_metal"], name="bottle_adapter", material_class_id="metal.blackened_gunmetal")

    if form == "large_canister":
        body_height = 0.180 * bs
        outer_radius = 0.035
        hoops = True
    else:  # compact_underslung
        body_height = 0.132 * bs
        outer_radius = 0.028
        hoops = False
    # Derive the drop so the neck threads always meet the adapter (z ~ -0.090).
    threads_top = body_height + 0.014
    translate_z = -0.090 - threads_top
    bottle = _bottle(body_height=body_height, outer_radius=outer_radius, hoops=hoops).translate((0, 0, translate_z))
    head.visual(mesh_from_cadquery(bottle, "rs_collection_bottle", tolerance=0.0007), material=mats["bottle"], name="collection_bottle", material_class_id="plastic.frosted_translucent")


# ---------------------------------------------------------------------------
# Handle (Slots A, D, E, G) — inline visuals on each handle part.
# ---------------------------------------------------------------------------
def _build_arm(shape: _HandleShape, side: int, reach: float):
    sx = float(side)
    pts = _scaled_pts(shape, reach)
    p3d = [(x * sx, 0.0, z) for (x, z) in pts]
    arm = _beam_between(p3d[0], p3d[1], 0.020, 0.024, 0.003)
    for i in range(1, len(p3d) - 1):
        arm = arm.union(_beam_between(p3d[i], p3d[i + 1], 0.020, 0.024, 0.003))
    # A forged knuckle at every interior bend fuses the angled box beams into one
    # continuous member (source: long_straight elbow, L123-129) and prevents the
    # thin-wedge junction from tessellating into a separate mesh island.
    knuckle_map = dict(shape.knuckles)
    for idx in range(1, len(p3d) - 1):
        radius = knuckle_map.get(idx, 0.014)
        knuckle = cq.Workplane("XZ").circle(radius).extrude(0.011, both=True).translate(p3d[idx])
        try:
            knuckle = knuckle.edges().fillet(0.0025)
        except Exception:
            pass
        arm = arm.union(knuckle)

    pivot = (0.0, 0.0, 0.0)
    lug = cq.Workplane("XZ").circle(0.014).extrude(0.012, both=True)
    lug = lug.union(_beam_between(pivot, p3d[0], 0.018, 0.014, 0.0))
    return arm, lug


def _emit_grip(handle, r: ResolvedRivetSqueeze1Config, side: int, tag: str, mats) -> None:
    shape = _HANDLE_SHAPES[r.handle_topology]
    sx = float(side)
    (g0x, g0z), (g1x, g1z) = _scaled_grip(shape, r.arm_reach_scale)
    g0 = (g0x * sx, 0.0, g0z)
    g1 = (g1x * sx, 0.0, g1z)

    # Grip run + unit axis (g0 -> g1, pointing away from the pivot).
    run_x = g1[0] - g0[0]
    run_z = g1[2] - g0[2]
    run_len = math.hypot(run_x, run_z)
    ux, uz = run_x / run_len, run_z / run_len
    # Every grip's proximal end is extended back along the arm axis so it always
    # overlaps the arm's last segment (one connected handle island) even at the
    # extreme reach draws — the arm/grip mesh proximity, not the pivot, is what
    # the compile-sweep island check enforces.
    g0e = (g0[0] - ux * 0.032, 0.0, g0[2] - uz * 0.032)

    if r.grip_construction == "closed_loop_ring":
        core, panel_front, panel_back = _d_ring_grip(g0e, g1)
        handle.visual(mesh_from_cadquery(core, f"rs_{tag}_grip_core", tolerance=0.0008), material=mats["grip_core"], name="grip_core", material_class_id="rubber.smooth_plain")
        handle.visual(mesh_from_cadquery(panel_front, f"rs_{tag}_grip_overmold", tolerance=0.0007), material=mats["grip_overmold"], name="grip_overmold", material_class_id="rubber.smooth_plain")
        handle.visual(mesh_from_cadquery(panel_back, f"rs_{tag}_grip_overmold_back", tolerance=0.0007), material=mats["grip_overmold"], name="grip_overmold_back", material_class_id="rubber.smooth_plain")
        return

    grip = _beam_between(g0e, g1, 0.038, 0.052, 0.010)

    if r.grip_construction == "single_ribbed_sleeve":
        # One continuous molded sleeve: transverse rib bands + a flared butt
        # collar (no separate circular finger ridges — the bands ARE the ribs;
        # keeping the union count low avoids export-time mesh fragmentation).
        for i in range(7):
            t = 0.12 + i * 0.12
            cx = g0[0] + run_x * t
            cz = g0[2] + run_z * t
            hb = 0.0042
            grip = grip.union(_beam_between((cx - ux * hb, 0.0, cz - uz * hb), (cx + ux * hb, 0.0, cz + uz * hb), 0.042, 0.056, 0.003))
        collar_start = (g1[0] - ux * 0.014, 0.0, g1[2] - uz * 0.014)
        grip = grip.union(_beam_between(collar_start, g1, 0.044, 0.058, 0.005))
        handle.visual(mesh_from_cadquery(grip, f"rs_{tag}_ribbed_grip", tolerance=0.0008), material=mats["grip_overmold"], name="ribbed_grip", material_class_id="rubber.directional_grooved")
        return

    # two_tone_overmold: black core (molded finger ridges) + coloured panels.
    for i in range(5):
        t = 0.20 + i * 0.145
        x = g0[0] + run_x * t
        z = g0[2] + run_z * t - 0.021
        grip = grip.union(cq.Workplane("XZ").circle(0.0063).extrude(0.020, both=True).translate((x, 0.0, z)))
    handle.visual(mesh_from_cadquery(grip, f"rs_{tag}_grip_core", tolerance=0.0008), material=mats["grip_core"], name="grip_core", material_class_id="rubber.directional_grooved")
    ps = (g0[0] + run_x * 0.08, 0.0, g0[2] + run_z * 0.08)
    pe = (g0[0] + run_x * 0.93, 0.0, g0[2] + run_z * 0.93)
    panel = _beam_between(ps, pe, 0.0045, 0.030, 0.006)
    handle.visual(mesh_from_cadquery(panel.translate((0.0, -0.0200, 0.003)), f"rs_{tag}_grip_overmold", tolerance=0.0007), material=mats["grip_overmold"], name="grip_overmold", material_class_id="rubber.smooth_plain")
    handle.visual(mesh_from_cadquery(panel.translate((0.0, 0.0200, 0.003)), f"rs_{tag}_grip_overmold_back", tolerance=0.0007), material=mats["grip_overmold"], name="grip_overmold_back", material_class_id="rubber.smooth_plain")


def _emit_spare_tips(handle, r: ResolvedRivetSqueeze1Config, side: int, mats) -> None:
    """Rack/magazine holder + N seated nose tips on handle_0 (Slot G multiplicity)."""
    shape = _HANDLE_SHAPES[r.handle_topology]
    sx = float(side)
    reach = r.arm_reach_scale
    (rs_x, rs_z), (re_x, re_z) = shape.rack
    rack_start = (rs_x * reach * sx, shape.rack_y, rs_z * reach)
    rack_end = (re_x * reach * sx, shape.rack_y, re_z * reach)
    n = r.spare_tip_count
    magazine = n >= 6  # higher counts use the indexed magazine block (source: N=6 magazine)
    # Holder beam.
    if magazine:
        rack = _beam_between(rack_start, rack_end, 0.030, 0.018, 0.004)
    else:
        rack = _beam_between(rack_start, rack_end, shape.rack_depth, 0.010, 0.002)

    tip_frac = [0.12 + (0.76) * (i / max(n - 1, 1)) for i in range(n)]
    tip_positions = []
    for i, t in enumerate(tip_frac):
        x = rack_start[0] + (rack_end[0] - rack_start[0]) * t
        z = rack_start[2] + (rack_end[2] - rack_start[2]) * t
        tip_positions.append((x, z))
        if magazine:
            socket = cq.Workplane("XZ").circle(0.00415).extrude(0.036, both=True).translate((x, 0.0, z))
            index_ring = cq.Workplane("XZ").circle(0.0060).circle(0.00425).extrude(0.0030, both=True).translate((x, -0.0145, z))
            rack = rack.cut(socket).union(index_ring)

    holder_name = "spare_tip_magazine" if magazine else "spare_tip_rack"
    handle.visual(mesh_from_cadquery(rack, "rs_" + holder_name, tolerance=0.0006), material=mats["body_metal"], name=holder_name, material_class_id="metal.blackened_gunmetal")

    for i, (x, z) in enumerate(tip_positions):
        if magazine:
            tip = _spare_nose_tip(i).translate((x, 0.0, z))
        else:
            tip = cq.Workplane("XZ").polygon(6, 0.010).extrude(0.018, both=True).translate((x, shape.tip_y, z - 0.001))
        handle.visual(mesh_from_cadquery(tip, f"rs_spare_tip_{i}", tolerance=0.0005), material=mats["steel"], name=f"spare_tip_{i}", material_class_id="metal.steel_bare")


def _emit_handle(model, r: ResolvedRivetSqueeze1Config, side: int, name: str, tag: str, mats):
    shape = _HANDLE_SHAPES[r.handle_topology]
    handle = model.part(name, meta={"side_index": 0 if side < 0 else 1})
    arm, lug = _build_arm(shape, side, r.arm_reach_scale)
    handle.visual(mesh_from_cadquery(arm, f"rs_{tag}_metal_arm", tolerance=0.0008), material=mats["body_metal"], name="metal_arm", material_class_id="metal.blackened_gunmetal")
    handle.visual(mesh_from_cadquery(lug, f"rs_{tag}_pivot_lug", tolerance=0.0006), material=mats["body_metal"], name="pivot_lug", material_class_id="metal.blackened_gunmetal")

    _emit_grip(handle, r, side, tag, mats)

    pivot_cap = _socket_screw().translate((0, -0.011, 0))
    handle.visual(mesh_from_cadquery(pivot_cap, f"rs_{tag}_pivot_cap", tolerance=0.0005), material=mats["dark_steel"], name="pivot_cap", material_class_id="metal.blackened_gunmetal")

    if r.return_mechanism == "two_handle_return_coils":
        handle.visual(mesh_from_cadquery(_handle_return_spring(side), f"rs_{tag}_return_spring", tolerance=0.00045), material=mats["spring"], name="return_spring", material_class_id="metal.steel_bare")

    if side < 0:  # handle_0 carries the spare-tip holder
        _emit_spare_tips(handle, r, side, mats)

    handle.inertial = Inertial.from_geometry(
        Box((0.06, 0.03, 0.30)),
        mass=0.06,
        origin=Origin(xyz=(side * 0.12, 0.0, -0.12)),
    )
    return handle


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_rivet_squeeze1(
    config: RivetSqueeze1Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets, meta={"category": "0611", "class": "rivet_squeeze1"})
    palette = _palette_rgba(r.palette_style)
    mats = {key: model.material(f"rivet_{key}_{r.palette_style}", rgba=rgba) for key, rgba in palette.items()}

    # --- Root head chassis. ---
    head = model.part("head")
    _emit_head_form(head, r, mats)
    _emit_head_hardware(head, r, mats)
    _emit_nosepiece(head, r, mats)
    _emit_bottle(head, r, mats)
    head.inertial = Inertial.from_geometry(Box((0.11, 0.05, 0.20)), mass=0.35, origin=Origin(xyz=(0.0, 0.0, -0.01)))

    # --- Two mirrored handle children. ---
    _emit_handle(model, r, -1, "handle_0", "h0", mats)
    _emit_handle(model, r, +1, "handle_1", "h1", mats)
    head_0 = model.get_part("handle_0")
    head_1 = model.get_part("handle_1")

    # --- Two REVOLUTE squeeze joints; handle_1 mimics handle_0 (symmetric). ---
    upper = r.squeeze_upper
    left_joint = model.articulation(
        "head_to_handle_0",
        ArticulationType.REVOLUTE,
        parent=head,
        child=head_0,
        origin=Origin(xyz=(-_PIVOT_X, 0.0, _PIVOT_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=420.0, velocity=1.6, lower=0.0, upper=upper),
    )
    model.articulation(
        "head_to_handle_1",
        ArticulationType.REVOLUTE,
        parent=head,
        child=head_1,
        origin=Origin(xyz=(_PIVOT_X, 0.0, _PIVOT_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=420.0, velocity=1.6, lower=0.0, upper=upper),
        mimic=Mimic(joint=left_joint.name, multiplier=1.0, offset=0.0),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_rivet_squeeze1(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_rivet_squeeze1(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_rivet_squeeze1_tests(object_model: ArticulatedObject, config: RivetSqueeze1Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    head = object_model.get_part("head")
    handle_0 = object_model.get_part("handle_0")
    handle_1 = object_model.get_part("handle_1")
    squeeze = object_model.get_articulation("head_to_handle_0")
    follower = object_model.get_articulation("head_to_handle_1")

    # --- Captured pivot allowances (round lug + socket cap seated in the cover). ---
    for handle in (handle_0, handle_1):
        ctx.allow_overlap(head, handle, elem_a="red_head_body", elem_b="pivot_lug",
                          reason="The moving handle lug is captured through the close-fitting head cover pocket.")
        ctx.expect_overlap(head, handle, axes="xz", elem_a="red_head_body", elem_b="pivot_lug",
                           min_overlap=0.006, name=f"{handle.name} pivot is seated in the head")
        ctx.allow_overlap(head, handle, elem_a="red_head_body", elem_b="pivot_cap",
                          reason="The recessed socket cap seats into the handle pivot counterbore on the head face.")
        ctx.expect_overlap(head, handle, axes="xz", elem_a="red_head_body", elem_b="pivot_cap",
                           min_overlap=0.004, name=f"{handle.name} pivot cap is seated on the head face")
        if r.return_mechanism == "two_handle_return_coils":
            ctx.allow_overlap(head, handle, elem_a="red_head_body", elem_b="return_spring",
                              reason="The return coil's L-anchor wire seats into the handle pivot region beneath the cover.")

    # --- Compiler baseline + Rule 5 motion QC. ---
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()  # captured-pin joints omit MatingContract (grandfathered)
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # --- Structural identity: 3 parts, 2 revolute squeeze, mimic follower. ---
    ctx.check(
        "exact three-part topology (head + handle_0 + handle_1)",
        len(object_model.parts) == 3
        and squeeze.parent == "head" and follower.parent == "head"
        and {squeeze.child, follower.child} == {"handle_0", "handle_1"},
        details=f"parts={[p.name for p in object_model.parts]}",
    )
    ctx.check(
        "symmetric revolute squeeze (handle_1 mimics handle_0)",
        squeeze.articulation_type == ArticulationType.REVOLUTE
        and follower.articulation_type == ArticulationType.REVOLUTE
        and squeeze.mimic is None
        and follower.mimic is not None,
        details=f"squeeze={squeeze.articulation_type}, follower_mimic={follower.mimic}",
    )

    # --- Handle open V + squeeze semantics (Rule 5 targeted poses). ---
    aabb_0 = ctx.part_world_aabb(handle_0)
    aabb_1 = ctx.part_world_aabb(handle_1)
    red_head_aabb = ctx.part_element_world_aabb(head, elem="red_head_body")
    open_centers = None
    if aabb_0 and aabb_1 and red_head_aabb:
        c0 = tuple((aabb_0[0][i] + aabb_0[1][i]) / 2 for i in range(3))
        c1 = tuple((aabb_1[0][i] + aabb_1[1][i]) / 2 for i in range(3))
        open_centers = (c0, c1)
        ctx.check(
            "handles open as a symmetric V below the head",
            c0[0] < -0.06 and c1[0] > 0.06
            and aabb_0[0][2] < red_head_aabb[0][2]
            and aabb_1[0][2] < red_head_aabb[0][2],
            details=f"open_centers={open_centers}, red_head_aabb={red_head_aabb}",
        )
    else:
        ctx.fail("handles open as a symmetric V below the head", "missing world AABB data")

    with ctx.pose({squeeze: r.squeeze_upper}):
        closed_0 = ctx.part_world_aabb(handle_0)
        closed_1 = ctx.part_world_aabb(handle_1)
        if open_centers and closed_0 and closed_1:
            cc0 = tuple((closed_0[0][i] + closed_0[1][i]) / 2 for i in range(3))
            cc1 = tuple((closed_1[0][i] + closed_1[1][i]) / 2 for i in range(3))
            ctx.check(
                "squeezing brings both grips inward",
                abs(cc0[0]) < abs(open_centers[0][0]) - 0.004
                and abs(cc1[0]) < abs(open_centers[1][0]) - 0.004,
                details=f"open={open_centers}, squeezed={(cc0, cc1)}",
            )
            # The two handles must stay clear across the centerline at full squeeze.
            ctx.check(
                "squeezed handles stay clear of the centerline",
                closed_0[1][0] < closed_1[0][0],
                details=f"h0_max_x={closed_0[1][0]:.4f}, h1_min_x={closed_1[0][0]:.4f}",
            )

    # --- Category identity visuals. ---
    head_names = {v.name for v in head.visuals}
    ctx.check(
        "complete top nosepiece + mandrel assembly",
        {"nose_washer", "knurled_collar", "hex_lock_nut", "mandrel_tip"}.issubset(head_names),
        details=f"head visuals={sorted(head_names)}",
    )
    ctx.check(
        "under-head collection bottle + adapter",
        {"bottle_adapter", "collection_bottle"}.issubset(head_names),
        details="Bottle and threaded adapter must both be authored on the head.",
    )
    ctx.check(
        "enclosed head cover + lower housing + side links + pull rod",
        {"red_head_body", "lower_housing", "side_plate_left", "side_plate_right", "pull_rod"}.issubset(head_names),
        details=f"head visuals={sorted(head_names)}",
    )

    # --- Grip construction present on each handle. ---
    for handle in (handle_0, handle_1):
        names = {v.name for v in handle.visuals}
        if r.grip_construction == "single_ribbed_sleeve":
            ok = "ribbed_grip" in names
        else:
            ok = {"grip_core", "grip_overmold", "grip_overmold_back"}.issubset(names)
        ctx.check(f"{handle.name} carries the {r.grip_construction} grip", ok, details=f"visuals={sorted(names)}")

    # --- Return mechanism per-handle coil (if present). ---
    if r.return_mechanism == "two_handle_return_coils":
        ctx.check(
            "both handles carry a return coil that swings with the handle",
            all("return_spring" in {v.name for v in h.visuals} for h in (handle_0, handle_1)),
            details="each handle must carry its own return_spring",
        )
        rest_spring = ctx.part_element_world_aabb(handle_0, elem="return_spring")
        with ctx.pose({squeeze: r.squeeze_upper}):
            moved_spring = ctx.part_element_world_aabb(handle_0, elem="return_spring")
        ctx.check(
            "the return spring moves with its handle",
            rest_spring is not None and moved_spring is not None
            and math.dist(
                [(rest_spring[0][i] + rest_spring[1][i]) / 2 for i in range(3)],
                [(moved_spring[0][i] + moved_spring[1][i]) / 2 for i in range(3)],
            ) > 0.0015,
            details=f"rest={rest_spring}, moved={moved_spring}",
        )

    # --- Spare-tip multiplicity on handle_0. ---
    h0_names = {v.name for v in handle_0.visuals}
    expected_tips = {f"spare_tip_{i}" for i in range(r.spare_tip_count)}
    ctx.check(
        f"handle_0 carries a spare-tip holder + {r.spare_tip_count} seated tips",
        ({"spare_tip_rack"} <= h0_names or {"spare_tip_magazine"} <= h0_names)
        and expected_tips.issubset(h0_names),
        details=f"handle_0 visuals={sorted(h0_names)}",
    )

    # --- Palette diversity: materials carry the palette style tag. ---
    ctx.check(
        "materials carry the palette style tag",
        any(r.palette_style in m.name for m in object_model.materials),
        details=f"materials={[m.name for m in object_model.materials]}",
    )
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "RivetSqueeze1Config",
    "ResolvedRivetSqueeze1Config",
    "build_rivet_squeeze1",
    "build_seeded_rivet_squeeze1",
    "config_from_seed",
    "resolve_config",
    "run_rivet_squeeze1_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
