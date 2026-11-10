# SPDX-License-Identifier: Apache-2.0

"""cabinet — modular procedural template (standing storage-cabinet furniture).

Category identity: a grounded hollow box **carcass** (thin-wall steel locker /
thick-board wooden dresser / lacquered nightstand) sits on a **base_support**
(splayed legs / square legs / plinth toe-kick / solid toe-kick box / hairpin
legs / casters) and presents a front **storage_mechanism**: 1..N hinged doors
(vertical-axis REVOLUTE + optional quarter-turn latch), 1..N drawers
(PRISMATIC), 2 bypass sliding doors (PRISMATIC), a single drop-down flap
(horizontal-axis REVOLUTE), a single hinged door, an upper-door/lower-drawer
combo, or an open niche over one drawer.

Canonical frame (unified across both 5-star coordinate families): back wall at
x=0, **front face at x=BD (front = +X)**, width along Y (centered), height +Z,
grounded at z=0. The steel-locker family (originally front=+Y) and the
dresser/bedside family (front=+X) are both mapped into this one canonical
frame by the carcass-aware geometry helpers; storage/base module factories only
ever consume the canonical frame.

5-star module sources (all synced under data/records/, rating=5):
  Slot A storage:
    hinged_doors        — rec_...steel-locker...76107d7e (P1)
    drawers             — rec_...wooden-dresser...58f0953c (P2)
    sliding_doors       — rec_...sliding-doors...503dd3bb
    door_over_drawers   — rec_...door-over-drawers...73ab06e1
    flap_door           — rec_...drop-down-flap...2bf8cef6
    hinged_single_door  — rec_...hinged-cabinet-door...02643395
    niche_over_drawer   — rec_...open-niche-over-drawer...bd3941ca
  Slot B base:
    splayed_legs        — rec_...four-splayed-legs...65751baf (LatheGeometry)
    square_legs         — P2 leg loop
    plinth_toe_kick     — rec_...plinth-toe-kick...0c11ba6d (cadquery)
    solid_toe_kick_box  — rec_...solid-toe-kick-box...6dddcda5
    hairpin_legs        — rec_...hairpin-metal-legs...dcdcb159 (mesh)
    casters             — rec_...casters...8bf476d7 (cadquery fork + WheelGeometry + CONTINUOUS)

Canonical spec: articraft_template_authoring/specs_modular_v1/Other_Cabinet.md
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum domains
# ---------------------------------------------------------------------------
StorageMechanism = Literal[
    "hinged_doors",
    "drawers",
    "sliding_doors",
    "door_over_drawers",
    "flap_door",
    "hinged_single_door",
    "niche_over_drawer",
]
BaseSupport = Literal[
    "splayed_legs",
    "square_legs",
    "plinth_toe_kick",
    "solid_toe_kick_box",
    "hairpin_legs",
    "casters",
]
PaletteStyle = Literal[
    "industrial_steel",
    "matte_black_wood",
    "lacquered_gray",
    "warm_oak",
    "charcoal_satin",
]

STORAGE_MECHANISMS: tuple[StorageMechanism, ...] = (
    "hinged_doors",
    "drawers",
    "sliding_doors",
    "door_over_drawers",
    "flap_door",
    "hinged_single_door",
    "niche_over_drawer",
)
BASE_SUPPORTS: tuple[BaseSupport, ...] = (
    "splayed_legs",
    "square_legs",
    "plinth_toe_kick",
    "solid_toe_kick_box",
    "hairpin_legs",
    "casters",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "industrial_steel",
    "matte_black_wood",
    "lacquered_gray",
    "warm_oak",
    "charcoal_satin",
)

# Storage families that natively want a tall/wide steel locker footprint vs a
# lower wooden dresser/nightstand footprint. Both are expressed in the SAME
# canonical +X frame; the distinction only drives default proportions.
_LOCKER_FAMILY = {"hinged_doors", "sliding_doors"}
_NIGHTSTAND_FAMILY = {"flap_door", "hinged_single_door", "niche_over_drawer"}
# (drawers / door_over_drawers -> dresser family)

DOOR_COUNTS: tuple[int, ...] = (2, 4, 6)
DOOR_COUNT_WEIGHTS = (0.45, 0.35, 0.20)
DRAWER_COUNTS: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8)
DRAWER_COUNT_WEIGHTS = (0.20, 0.13, 0.20, 0.15, 0.10, 0.09, 0.07, 0.06)

# ---------------------------------------------------------------------------
# Compatibility matrix (coordinate-family <-> base binding, casters gating).
# Both families share one canonical frame, but caster proportions only suit
# large standing cabinets (not the small nightstand footprint), per spec.
# ---------------------------------------------------------------------------
_LARGE_BASES: tuple[BaseSupport, ...] = (
    "splayed_legs",
    "square_legs",
    "plinth_toe_kick",
    "solid_toe_kick_box",
    "hairpin_legs",
    "casters",
)
_NIGHTSTAND_BASES: tuple[BaseSupport, ...] = (
    "splayed_legs",
    "square_legs",
    "plinth_toe_kick",
    "solid_toe_kick_box",
    "hairpin_legs",
)  # casters excluded for nightstand footprint


def _compatible_bases(storage: StorageMechanism) -> tuple[BaseSupport, ...]:
    if storage in _NIGHTSTAND_FAMILY:
        return _NIGHTSTAND_BASES
    return _LARGE_BASES


# ---------------------------------------------------------------------------
# Palettes (per-seed). Keys: carcass / front / trim / hardware / accent.
# Sourced from 5-star sample materials (see spec §palette).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "industrial_steel": {
        "carcass": (0.60, 0.61, 0.63, 1.0),
        "front": (0.55, 0.56, 0.58, 1.0),
        "front_b": (0.50, 0.51, 0.54, 1.0),
        "trim": (0.46, 0.47, 0.49, 1.0),
        "hardware": (0.18, 0.18, 0.20, 1.0),
        "dark": (0.07, 0.07, 0.08, 1.0),
    },
    "matte_black_wood": {
        "carcass": (0.075, 0.075, 0.08, 1.0),
        "front": (0.055, 0.055, 0.06, 1.0),
        "front_b": (0.10, 0.10, 0.11, 1.0),
        "trim": (0.72, 0.73, 0.75, 1.0),
        "hardware": (0.90, 0.91, 0.93, 1.0),
        "dark": (0.13, 0.13, 0.14, 1.0),
    },
    "lacquered_gray": {
        "carcass": (0.50, 0.52, 0.55, 1.0),
        "front": (0.85, 0.87, 0.88, 1.0),
        "front_b": (0.78, 0.80, 0.82, 1.0),
        "trim": (0.55, 0.57, 0.60, 1.0),
        "hardware": (0.80, 0.82, 0.85, 1.0),
        "dark": (0.20, 0.21, 0.23, 1.0),
    },
    "warm_oak": {
        "carcass": (0.62, 0.46, 0.30, 1.0),
        "front": (0.70, 0.54, 0.38, 1.0),
        "front_b": (0.58, 0.42, 0.27, 1.0),
        "trim": (0.50, 0.36, 0.22, 1.0),
        "hardware": (0.72, 0.60, 0.32, 1.0),
        "dark": (0.30, 0.21, 0.13, 1.0),
    },
    "charcoal_satin": {
        "carcass": (0.27, 0.28, 0.30, 1.0),
        "front": (0.40, 0.42, 0.45, 1.0),
        "front_b": (0.34, 0.36, 0.39, 1.0),
        "trim": (0.22, 0.23, 0.25, 1.0),
        "hardware": (0.14, 0.14, 0.16, 1.0),
        "dark": (0.10, 0.10, 0.12, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Public + resolved config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CabinetConfig:
    storage_mechanism: StorageMechanism = "hinged_doors"
    base_support: BaseSupport = "splayed_legs"
    door_count: int = 4
    drawer_count: int = 4
    palette_style: PaletteStyle = "industrial_steel"
    carcass_width_scale: float = 1.0
    carcass_height_scale: float = 1.0
    door_open_scale: float = 1.0
    drawer_travel_scale: float = 1.0
    name: str = "reference_cabinet"


@dataclass(frozen=True)
class ResolvedCabinetConfig:
    storage_mechanism: StorageMechanism
    base_support: BaseSupport
    door_count: int  # active count for hinged_doors; else derived/fixed
    drawer_count: int  # active count for drawers; else fixed
    palette_style: PaletteStyle
    # Canonical carcass envelope (back x=0, front face at x=carcass_depth).
    carcass_width: float  # along Y
    carcass_depth: float  # along X (back->front)
    carcass_height: float  # along Z (overall incl. base)
    base_height: float  # lift from floor to carcass bottom
    wall_thickness: float
    door_open_upper: float  # radians
    drawer_travel: float  # meters
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ---------------------------------------------------------------------------
# Procedural sampler
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> CabinetConfig:
    rng = random.Random(seed)
    storage = rng.choice(STORAGE_MECHANISMS)
    base = rng.choice(_compatible_bases(storage))

    door_count = rng.choices(DOOR_COUNTS, weights=DOOR_COUNT_WEIGHTS, k=1)[0]
    drawer_count = rng.choices(DRAWER_COUNTS, weights=DRAWER_COUNT_WEIGHTS, k=1)[0]

    return CabinetConfig(
        storage_mechanism=storage,
        base_support=base,
        door_count=door_count,
        drawer_count=drawer_count,
        palette_style=rng.choice(PALETTE_STYLES),
        carcass_width_scale=round(rng.uniform(0.85, 1.15), 3),
        carcass_height_scale=round(rng.uniform(0.85, 1.20), 3),
        door_open_scale=round(rng.uniform(0.7, 1.0), 3),
        drawer_travel_scale=round(rng.uniform(0.7, 1.0), 3),
        name=f"seeded_cabinet_{seed}",
    )


def resolve_config(config: CabinetConfig) -> ResolvedCabinetConfig:
    if config.storage_mechanism not in STORAGE_MECHANISMS:
        raise ValueError(f"Unsupported storage_mechanism: {config.storage_mechanism}")
    if config.base_support not in BASE_SUPPORTS:
        raise ValueError(f"Unsupported base_support: {config.base_support}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    storage = config.storage_mechanism
    base = config.base_support

    # Compatibility gate: clamp casters off the nightstand footprint family.
    if base not in _compatible_bases(storage):
        base = "splayed_legs"

    w_scale = _clamp(config.carcass_width_scale, 0.85, 1.15)
    h_scale = _clamp(config.carcass_height_scale, 0.85, 1.20)

    # Base footprint defaults by family (canonical +X frame).
    if storage in _LOCKER_FAMILY:
        base_w, base_d, base_h = 1.60, 0.50, 1.80
        base_lift = 0.15
    elif storage in _NIGHTSTAND_FAMILY:
        base_w, base_d, base_h = 0.46, 0.42, 0.62
        base_lift = 0.12
    else:  # dresser family (drawers / door_over_drawers)
        base_w, base_d, base_h = 1.70, 0.50, 0.85
        base_lift = 0.15

    carcass_width = round(base_w * w_scale, 4)
    carcass_height = round(base_h * h_scale, 4)
    carcass_depth = base_d

    # Active multiplicity (mutually-exclusive; gated by storage).
    if storage == "hinged_doors":
        door_count = config.door_count if config.door_count in DOOR_COUNTS else 4
        # Clamp N so each leaf is >= ~0.18 m wide on this carcass width.
        inner_w = carcass_width - 2.0 * 0.02
        while door_count > 2 and inner_w / door_count < 0.18:
            door_count -= 2
        drawer_count = 0
    elif storage == "drawers":
        drawer_count = config.drawer_count if config.drawer_count in DRAWER_COUNTS else 4
        door_count = 0
    elif storage == "door_over_drawers":
        door_count = 2
        drawer_count = 2
    elif storage == "sliding_doors":
        door_count = 2
        drawer_count = 0
    elif storage in ("flap_door", "hinged_single_door"):
        door_count = 1
        drawer_count = 0
    else:  # niche_over_drawer
        door_count = 0
        drawer_count = 1

    door_open_upper = math.radians(110.0) * _clamp(config.door_open_scale, 0.7, 1.0)
    drawer_travel = 0.40 * _clamp(config.drawer_travel_scale, 0.7, 1.0)
    if storage in _NIGHTSTAND_FAMILY:
        drawer_travel = min(drawer_travel, 0.36)

    return ResolvedCabinetConfig(
        storage_mechanism=storage,
        base_support=base,
        door_count=door_count,
        drawer_count=drawer_count,
        palette_style=config.palette_style,
        carcass_width=carcass_width,
        carcass_depth=carcass_depth,
        carcass_height=carcass_height,
        base_height=base_lift,
        wall_thickness=0.02,
        door_open_upper=door_open_upper,
        drawer_travel=drawer_travel,
        name=config.name or "cabinet",
    )


# ---------------------------------------------------------------------------
# slot_choices
# ---------------------------------------------------------------------------
def _slot_choices_for_resolved(r: ResolvedCabinetConfig) -> list[tuple[str, str]]:
    storage_label = r.storage_mechanism
    if r.storage_mechanism == "hinged_doors":
        storage_label = f"hinged_doors_{r.door_count}"
    elif r.storage_mechanism == "drawers":
        storage_label = f"drawers_{r.drawer_count}"
    return [
        ("storage_mechanism", storage_label),
        ("base_support", r.base_support),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return _slot_choices_for_resolved(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.engineered_board")


def _meta(joint_type, axis, origin, limits) -> dict[str, object]:
    return {
        "type": joint_type.value,
        "axis": axis,
        "origin": origin,
        "range": None if limits is None else (limits.lower, limits.upper),
    }


@dataclass(frozen=True)
class _Frame:
    """Canonical carcass frame (back x=0, front at FRONT_X)."""

    BW: float  # body width (Y)
    BD: float  # body depth (X) — back at 0, front face at BD
    z0: float  # carcass bottom z (= base_height)
    z1: float  # carcass top z
    wall: float

    @property
    def FRONT_X(self) -> float:
        return self.BD

    @property
    def INNER_W(self) -> float:
        return self.BW - 2.0 * self.wall

    @property
    def BH(self) -> float:
        return self.z1 - self.z0


def _make_frame(r: ResolvedCabinetConfig) -> _Frame:
    return _Frame(
        BW=r.carcass_width,
        BD=r.carcass_depth,
        z0=r.base_height,
        z1=r.carcass_height,
        wall=r.wall_thickness,
    )


# ===========================================================================
# CARCASS shell (root part). Hollow box with a front (+X) opening, derived from
# the P1 steel-locker / P2 dresser shells, normalized to the +X canonical frame.
# ===========================================================================
def _build_carcass_shell(carcass, fr: _Frame, mats) -> None:
    BW, BD, wall = fr.BW, fr.BD, fr.wall
    z0, z1, BH = fr.z0, fr.z1, fr.BH
    zc = z0 + BH / 2.0
    cm = mats["carcass"]

    # Side panels (full depth, full carcass height).
    for tag, s in (("0", 1.0), ("1", -1.0)):
        _box(carcass, (BD, wall, BH), (BD / 2.0, s * (BW / 2.0 - wall / 2.0), zc), cm,
             f"side_panel_{tag}")
    # Back panel.
    _box(carcass, (wall, fr.INNER_W, BH), (wall / 2.0, 0.0, zc), cm, "back_panel")
    # Bottom + top boards.
    _box(carcass, (BD, fr.INNER_W, 0.018), (BD / 2.0, 0.0, z0 + 0.009), cm, "bottom_board")
    _box(carcass, (BD, fr.INNER_W, 0.018), (BD / 2.0, 0.0, z1 - 0.009), cm, "top_stretcher")
    # Thin top slab with overhang (dresser-style trim cap reads as identity).
    _box(carcass, (BD + 0.04, BW + 0.04, 0.022), (BD / 2.0, 0.0, z1 + 0.011), mats["trim"],
         "top_slab")


def _build_front_frame_rails(carcass, fr: _Frame, mats, *, zone_bot, zone_top) -> None:
    """Front-opening frame: bottom rail below the opening, top rail above."""
    BD, wall = fr.BD, fr.wall
    cm = mats["carcass"]
    if zone_bot - fr.z0 > 0.004:
        _box(carcass, (wall, fr.INNER_W, zone_bot - fr.z0),
             (BD - wall / 2.0, 0.0, (fr.z0 + zone_bot) / 2.0), cm, "front_bottom_rail")
    if fr.z1 - zone_top > 0.004:
        _box(carcass, (wall, fr.INNER_W, fr.z1 - zone_top),
             (BD - wall / 2.0, 0.0, (zone_top + fr.z1) / 2.0), cm, "front_top_rail")


# ===========================================================================
# SLOT B base_support factories. Most emit fixed carcass visuals; casters emit
# CONTINUOUS wheel children.
# ===========================================================================
def _splayed_leg_mesh(i: int, dx: float, dy: float, leg_h: float, assets: AssetContext):
    """LatheGeometry tapered leg splayed outward (source 65751baf)."""
    splay = math.radians(8.0)
    leg_len = leg_h / math.cos(splay)
    profile = [
        (0.001, 0.0),
        (0.012, 0.0),
        (0.020, leg_len),
        (0.001, leg_len),
    ]
    geom = LatheGeometry(profile, segments=16)
    inv = 1.0 / math.sqrt(2.0)
    geom.rotate((dy * inv, -dx * inv, 0.0), splay, origin=(0.0, 0.0, leg_len))
    z_drop = leg_len * (1.0 - math.cos(splay)) - 0.002
    geom.translate(0.0, 0.0, -z_drop)
    return mesh_from_geometry(geom, assets.mesh_path(f"leg_{i}.obj"))


def _build_base_splayed_legs(carcass, fr: _Frame, mats, assets: AssetContext) -> None:
    inset = 0.06
    corners = [
        (fr.BD - inset, fr.BW / 2.0 - inset, 1.0, 1.0),
        (inset, fr.BW / 2.0 - inset, -1.0, 1.0),
        (inset, -(fr.BW / 2.0 - inset), -1.0, -1.0),
        (fr.BD - inset, -(fr.BW / 2.0 - inset), 1.0, -1.0),
    ]
    for i, (lx, ly, dx, dy) in enumerate(corners):
        # Leg mesh spans local z 0..leg_len (foot near floor, top at carcass
        # bottom). Place origin at z=0 so the foot rests on the floor and the
        # top embeds ~2mm into the carcass bottom.
        mesh = _splayed_leg_mesh(i, dx, dy, fr.z0, assets)
        carcass.visual(mesh, origin=Origin(xyz=(lx, ly, 0.0)), material=mats["hardware"],
                       name=f"leg_{i}", material_class_id="wood.polished_varnished")


def _build_base_square_legs(carcass, fr: _Frame, mats) -> None:
    sq = 0.05
    inset = sq / 2.0 + 0.012
    h = fr.z0 + 0.004
    corners = [
        (fr.BD - inset, fr.BW / 2.0 - inset),
        (inset, fr.BW / 2.0 - inset),
        (inset, -(fr.BW / 2.0 - inset)),
        (fr.BD - inset, -(fr.BW / 2.0 - inset)),
    ]
    for i, (lx, ly) in enumerate(corners):
        _box(carcass, (sq, sq, h), (lx, ly, h / 2.0), mats["carcass"], f"leg_{i}")


def _plinth_mesh(fr: _Frame, name: str, assets: AssetContext):
    plinth_w = fr.BW - 0.04
    plinth_d = fr.BD - 0.07
    h = fr.z0
    ch = 0.008
    plinth = (
        cq.Workplane("XY")
        .box(plinth_d, plinth_w, h, centered=(True, True, False))
        .edges("|Z")
        .chamfer(ch)
        .edges("<Z")
        .chamfer(ch * 0.6)
    )
    return mesh_from_cadquery(plinth, name, assets=assets)


def _build_base_plinth(carcass, fr: _Frame, mats, assets: AssetContext) -> None:
    mesh = _plinth_mesh(fr, "plinth", assets)
    # Centered on the recessed footprint: back flush, front set back 0.07.
    cx = (fr.BD - 0.07) / 2.0 + 0.0
    carcass.visual(mesh, origin=Origin(xyz=(cx + 0.0, 0.0, 0.0)), material=mats["dark"],
                   name="plinth", material_class_id="wood.painted_clean")


def _build_base_toe_kick_box(carcass, fr: _Frame, mats) -> None:
    h = fr.z0
    upper_h = h * 0.62
    kick_h = h - upper_h
    # Upper full box.
    _box(carcass, (fr.BD - 0.03, fr.BW - 0.03, upper_h),
         ((fr.BD) / 2.0, 0.0, kick_h + upper_h / 2.0), mats["dark"], "base_upper")
    # Recessed toe-kick block (set back from front).
    _box(carcass, (fr.BD - 0.10, fr.BW - 0.06, kick_h),
         ((fr.BD - 0.04) / 2.0, 0.0, kick_h / 2.0), mats["dark"], "base_toekick")


def _hairpin_leg_mesh(name: str, leg_h: float, assets: AssetContext):
    """Two bent steel rods forming a hairpin leg (source dcdcb159 style).

    The two rods share a continuous top horizontal segment (the hairpin bend)
    so the whole leg is one welded solid (no disconnected components).
    """
    rod_r = 0.006
    spread = 0.06
    top = leg_h - rod_r
    # A single continuous polyline: up the left rod, across the top bend, down
    # the right rod. Consecutive segments overlap at shared endpoints (welded).
    chain = [
        (-spread, 0.0, 0.0),          # left foot on floor
        (0.0, 0.0, top),              # up to apex (left)
        (0.0, 0.0, top),              # apex (degenerate guard removed below)
        (spread, 0.0, 0.0),           # down to right foot
    ]
    # Build: left-rod, a short top cross bar, right-rod.
    segments = [
        ((-spread, 0.0, 0.0), (-0.004, 0.0, top)),
        ((-0.006, 0.0, top), (0.006, 0.0, top)),
        ((0.004, 0.0, top), (spread, 0.0, 0.0)),
    ]
    result = None
    for a, b in segments:
        seg = _rod_segment(a, b, rod_r)
        result = seg if result is None else result.union(seg)
    _ = chain
    return mesh_from_cadquery(result, name, assets=assets)


def _rod_segment(a, b, r):
    ax, ay, az = a
    bx, by, bz = b
    dx, dy, dz = bx - ax, by - ay, bz - az
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    seg = cq.Workplane("XY").circle(r).extrude(length)
    # Orient +Z extrusion onto the (a->b) direction.
    if length > 1e-9:
        zx, zy, zz = dx / length, dy / length, dz / length
        # rotation axis = z_hat x dir
        ax_r, ay_r, az_r = -zy, zx, 0.0
        norm = math.sqrt(ax_r * ax_r + ay_r * ay_r + az_r * az_r)
        if norm > 1e-9:
            angle = math.degrees(math.acos(max(-1.0, min(1.0, zz))))
            seg = seg.rotate((0, 0, 0), (ax_r, ay_r, az_r), angle)
    return seg.translate((ax, ay, az))


def _build_base_hairpin_legs(carcass, fr: _Frame, mats, assets: AssetContext) -> None:
    inset = 0.06
    corners = [
        (fr.BD - inset, fr.BW / 2.0 - inset),
        (inset, fr.BW / 2.0 - inset),
        (inset, -(fr.BW / 2.0 - inset)),
        (fr.BD - inset, -(fr.BW / 2.0 - inset)),
    ]
    for i, (lx, ly) in enumerate(corners):
        # Mounting plate flush under carcass.
        _box(carcass, (0.05, 0.05, 0.006), (lx, ly, fr.z0 - 0.003), mats["hardware"],
             f"mount_plate_{i}")
        mesh = _hairpin_leg_mesh(f"hairpin_leg_{i}", fr.z0, assets)
        carcass.visual(mesh, origin=Origin(xyz=(lx, ly, 0.0)), material=mats["hardware"],
                       name=f"hairpin_leg_{i}", material_class_id="metal.steel_bare")


def _caster_fork_mesh(name: str, leg_h: float, axle_local_z: float, assets: AssetContext):
    plate_sz, plate_t = 0.060, 0.006
    housing_r, housing_h = 0.015, 0.018
    fork_gap, arm_t = 0.036, 0.006
    plate = cq.Workplane("XY").box(plate_sz, plate_sz, plate_t).translate((0, 0, -plate_t / 2.0))
    housing = (
        cq.Workplane("XY").circle(housing_r).extrude(housing_h)
        .translate((0, 0, -plate_t - housing_h))
    )
    crossbar_w = fork_gap + 2.0 * arm_t
    crossbar_d, crossbar_t = 0.034, 0.008
    crossbar_z_top = -plate_t - housing_h
    crossbar = (
        cq.Workplane("XY").box(crossbar_w, crossbar_d, crossbar_t)
        .translate((0, 0, crossbar_z_top - crossbar_t / 2.0))
    )
    arm_drop = abs(axle_local_z) + 0.016 - (plate_t + housing_h + crossbar_t)
    arm_drop = max(arm_drop, 0.01)
    for sign in (-1.0, 1.0):
        ax = sign * (fork_gap / 2.0 + arm_t / 2.0)
        arm = (
            cq.Workplane("XY").box(arm_t, crossbar_d, arm_drop)
            .translate((ax, 0, crossbar_z_top - crossbar_t - arm_drop / 2.0))
        )
        crossbar = crossbar.union(arm)
    # Axle pin spanning the fork gap at the axle height, so the CONTINUOUS axle
    # joint origin lies on real fork geometry (passes the 15 mm origin check).
    axle_pin = (
        cq.Workplane("YZ").circle(0.004)
        .extrude((fork_gap / 2.0 + arm_t), both=True)
        .translate((0.0, 0.0, axle_local_z))
    )
    return mesh_from_cadquery(plate.union(housing).union(crossbar).union(axle_pin), name, assets=assets)


def _caster_wheel_mesh(name: str, assets: AssetContext):
    fork_gap = 0.036
    # Solid disc wheel (flat faces, hub width == rim width so the hub stays
    # welded to the rim as one mesh component; no through-bore).
    _ = (WheelBore, fork_gap)  # retained imports for source fidelity
    wheel = WheelGeometry(
        0.035,
        0.030,
        hub=WheelHub(radius=0.014, width=0.030, cap_style="flat"),
        # Flat solid web (no dish) connecting rim and hub into one component.
        face=WheelFace(dish_depth=0.0, front_inset=0.0, rear_inset=0.0),
    )
    return mesh_from_geometry(wheel, assets.mesh_path(f"{name}.obj"))


def _build_base_casters(model, carcass, fr: _Frame, mats) -> list[str]:
    wheel_r = 0.035
    axle_z = wheel_r  # world axle z (wheel bottom on floor)
    axle_local_z = axle_z - fr.z0
    fork_mesh = _caster_fork_mesh("caster_fork", fr.z0, axle_local_z, model.assets)
    wheel_mesh = _caster_wheel_mesh("caster_wheel", model.assets)
    inset = 0.08
    corners = [
        (fr.BD - inset, fr.BW / 2.0 - inset),
        (inset, fr.BW / 2.0 - inset),
        (inset, -(fr.BW / 2.0 - inset)),
        (fr.BD - inset, -(fr.BW / 2.0 - inset)),
    ]
    joints: list[str] = []
    for i, (cx, cy) in enumerate(corners):
        carcass.visual(fork_mesh, origin=Origin(xyz=(cx, cy, fr.z0)), material=mats["hardware"],
                       name=f"caster_fork_{i}", material_class_id="metal.steel_galvanized")
        wheel_part = model.part(f"caster_wheel_{i}")
        wheel_part.visual(wheel_mesh, material=mats["dark"], name="wheel", material_class_id="rubber.smooth_plain")
        # Solid web disc bridging the rim and hub (welds the WheelGeometry's
        # separate rim/hub mesh components into one connected support graph).
        wheel_part.visual(
            Cylinder(radius=0.033, length=0.026),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["dark"], name="wheel_web", material_class_id="rubber.smooth_plain",
        )
        # Axle stub along the spin axis (+X), spanning the fork gap; its AABB
        # contains the joint origin (0,0,0).
        wheel_part.visual(
            Cylinder(radius=0.0065, length=0.052),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["hardware"], name="axle_stub", material_class_id="metal.stainless_matte",
        )
        wheel_part.inertial = Inertial.from_geometry(
            Cylinder(radius=wheel_r, length=0.03), mass=0.5
        )
        limits = MotionLimits(effort=2.0, velocity=10.0)
        origin = (cx, cy, axle_z)
        model.articulation(
            f"caster_{i}_axle",
            ArticulationType.CONTINUOUS,
            parent=carcass,
            child=wheel_part,
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_meta(ArticulationType.CONTINUOUS, (1.0, 0.0, 0.0), origin, limits),
        )
        joints.append(f"caster_{i}_axle")
    return joints


def _build_base(model, carcass, fr: _Frame, r: ResolvedCabinetConfig, mats) -> list[str]:
    b = r.base_support
    if b == "splayed_legs":
        _build_base_splayed_legs(carcass, fr, mats, model.assets)
    elif b == "square_legs":
        _build_base_square_legs(carcass, fr, mats)
    elif b == "plinth_toe_kick":
        _build_base_plinth(carcass, fr, mats, model.assets)
    elif b == "solid_toe_kick_box":
        _build_base_toe_kick_box(carcass, fr, mats)
    elif b == "hairpin_legs":
        _build_base_hairpin_legs(carcass, fr, mats, model.assets)
    elif b == "casters":
        return _build_base_casters(model, carcass, fr, mats)
    return []


# ===========================================================================
# Shared drawer / door helpers (canonical +X front frame).
# ===========================================================================
FACE_THK = 0.018
FACE_PROUD = 0.0005
TRAY_T = 0.012


def _build_drawer_part(
    model, name, fr: _Frame, *, front_w, front_h, tray_w, tray_h, knob_ys, mats,
    local_y=0.0
):
    """Drawer in local frame: front panel outer face at local x=0, panel spans
    x in [-FACE_THK,0], hollow open-top tray extends toward -X (source P2)."""
    drawer = model.part(name)
    tray_d = min(fr.BD - 0.06, 0.42)
    drawer.visual(
        Box((FACE_THK, front_w, front_h)),
        origin=Origin(xyz=(-FACE_THK / 2.0, local_y, 0.0)),
        material=mats["front"],
        name="front_panel", material_class_id="wood.veneer_panel",
    )
    tray_back_x = -(FACE_THK + tray_d)
    tray_cx = -(FACE_THK + tray_d / 2.0)
    tray_bot = -front_h / 2.0 + 0.012
    drawer.visual(Box((tray_d, tray_w, TRAY_T)), origin=Origin(xyz=(tray_cx, local_y, tray_bot + TRAY_T / 2.0)),
                  material=mats["dark"], name="tray_bottom", material_class_id="wood.engineered_board")
    wall_h = tray_h - TRAY_T + 0.002
    wall_cz = tray_bot + TRAY_T - 0.002 + wall_h / 2.0
    drawer.visual(Box((TRAY_T, tray_w, wall_h)),
                  origin=Origin(xyz=(tray_back_x + TRAY_T / 2.0, local_y, wall_cz)),
                  material=mats["dark"], name="tray_back_wall", material_class_id="wood.engineered_board")
    side_len = tray_d + 0.002
    for tag, s in (("0", 1), ("1", -1)):
        drawer.visual(Box((side_len, TRAY_T, wall_h)),
                      origin=Origin(xyz=(-FACE_THK + 0.002 - side_len / 2.0,
                                         local_y + s * (tray_w / 2.0 - TRAY_T / 2.0), wall_cz)),
                      material=mats["dark"], name=f"tray_side_wall_{tag}", material_class_id="wood.engineered_board")
    drawer.visual(Box((TRAY_T, tray_w, wall_h)),
                  origin=Origin(xyz=(-FACE_THK - TRAY_T / 2.0 + 0.002, local_y, wall_cz)),
                  material=mats["dark"], name="tray_front_wall", material_class_id="wood.engineered_board")
    # Knobs (silver ball on a short stem along +X).
    for i, ky in enumerate(knob_ys):
        drawer.visual(
            Cylinder(radius=0.0055, length=0.018),
            origin=Origin(xyz=(0.007, local_y + ky, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["hardware"], name=f"knob_stem_{i}", material_class_id="metal.brushed_silver",
        )
        drawer.visual(
            Sphere(radius=0.0125),
            origin=Origin(xyz=(0.0125 + 0.010, local_y + ky, 0.0)),
            material=mats["hardware"], name=f"knob_ball_{i}", material_class_id="metal.chrome_polished",
        )
    drawer.inertial = Inertial.from_geometry(Box((tray_d, tray_w, max(tray_h, 0.05))), mass=4.0)
    return drawer


def _build_hinged_door_part(model, name, fr: _Frame, *, door_w, door_h, direction, mats,
                            leaf_mat_key="front", with_latch=False):
    """Hinged door leaf in local frame: hinge axis = local Z at local (0,0).
    Panel extends toward direction*+Y; outer face flush at local x=0, thickness
    toward -X (interior). Source P1 leaf + dresser door."""
    door = model.part(name)
    sign = float(direction)
    panel_y = sign * door_w / 2.0
    # Leaf back face at local x=0 (= carcass front frame plane when the hinge
    # origin is at FRONT_X); the leaf extends FORWARD (+X) so it sits proud of
    # the front frame/stiles and never shares their X-plane.
    door.visual(
        Box((FACE_THK, door_w, door_h)),
        origin=Origin(xyz=(FACE_THK / 2.0, panel_y, 0.0)),
        material=mats[leaf_mat_key],
        name="leaf", material_class_id="wood.veneer_panel",
    )
    # Vent backing strip (dark, lower) — P1 identity detail (fused visual).
    door.visual(
        Box((0.005, 0.030, min(0.36, door_h * 0.4))),
        origin=Origin(xyz=(FACE_THK - 0.0006, panel_y, -door_h * 0.22)),
        material=mats["dark"],
        name="vent_backing", material_class_id="metal.paint_coated",
    )
    # Piano-hinge knuckle column on the hinge edge (local Y near 0), straddling
    # the front frame plane so the child AABB contains the joint origin (0,0,0).
    door.visual(
        Cylinder(radius=0.0095, length=door_h - 0.03),
        origin=Origin(xyz=(0.004, 0.0, 0.0)),
        material=mats["trim"],
        name="hinge_barrel", material_class_id="metal.stainless_matte",
    )
    # Bar handle near the free edge (proud of the leaf outer face).
    door.visual(
        Box((0.016, 0.010, max(0.10, door_h * 0.30))),
        origin=Origin(xyz=(FACE_THK + 0.005, sign * (door_w - 0.06), 0.0)),
        material=mats["hardware"],
        name="handle_bar", material_class_id="metal.brushed_silver",
    )
    door.inertial = Inertial.from_geometry(Box((FACE_THK, door_w, door_h)), mass=3.0)
    return door


# ===========================================================================
# SLOT A storage_mechanism factories. Return (joint_names, allow_overlap_specs).
# allow_overlap_specs: list of (parent_name, child_name, elem_a, elem_b, reason)
# ===========================================================================
def _build_storage_hinged_doors(model, carcass, fr: _Frame, r: ResolvedCabinetConfig, mats):
    n = r.door_count
    zone_bot = fr.z0 + 0.06
    zone_top = fr.z1 - 0.06
    _build_front_frame_rails(carcass, fr, mats, zone_bot=zone_bot, zone_top=zone_top)
    door_h = zone_top - zone_bot - 0.01
    door_zc = (zone_bot + zone_top) / 2.0
    open_w = fr.INNER_W
    leaf_w = open_w / n
    stile_w = 0.03

    # Center stiles between adjacent door pairs (fixed carcass visuals).
    edges = [-open_w / 2.0 + j * leaf_w for j in range(n + 1)]
    for j in range(1, n):
        _box(carcass, (fr.wall, stile_w, zone_top - zone_bot),
             (fr.BD - fr.wall / 2.0, edges[j], door_zc), mats["trim"], f"front_stile_{j}")

    joints, overlaps = [], []
    for i in range(n):
        # Hinge stays at the slot edge (on the side panel / stile that anchors
        # it). The leaf is narrowed from the FREE edge so it clears the stile at
        # the opposite edge; the leaf sits proud of the frame plane (+X) so it
        # never shares the stile X-plane.
        slot_y0, slot_y1 = edges[i], edges[i + 1]
        if (slot_y0 + slot_y1) / 2.0 < 0:
            hinge_y = slot_y0 + 0.001
            direction = 1.0
            axis_z = -1.0
        else:
            hinge_y = slot_y1 - 0.001
            direction = -1.0
            axis_z = 1.0
        # Leaf width = slot minus a full stile-width of clearance at the free edge.
        dw = leaf_w - stile_w - 0.006
        leaf_key = "front" if i % 2 == 0 else "front_b"
        door = _build_hinged_door_part(model, f"door_{i}", fr, door_w=dw, door_h=door_h,
                                       direction=direction, mats=mats, leaf_mat_key=leaf_key)
        origin = (fr.FRONT_X, hinge_y, door_zc)
        limits = MotionLimits(effort=40.0, velocity=2.0, lower=0.0, upper=r.door_open_upper)
        model.articulation(
            f"door_{i}_hinge",
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=door,
            origin=Origin(xyz=origin),
            axis=(0.0, 0.0, axis_z),
            motion_limits=limits,
            meta=_meta(ArticulationType.REVOLUTE, (0.0, 0.0, axis_z), origin, limits),
        )
        joints.append(f"door_{i}_hinge")
        # The piano-hinge knuckle column intentionally laps whichever fixed
        # frame edge it pivots on (a side panel for the outer doors, a stile for
        # interior doors). Declare against every candidate edge element.
        frame_elems = ["side_panel_0", "side_panel_1"] + [f"front_stile_{j}" for j in range(1, n)]
        for elem in frame_elems:
            overlaps.append((f"door_{i}", "carcass", "hinge_barrel", elem,
                             "Piano-hinge knuckle laps the fixed frame edge it pivots on."))

        # Quarter-turn latch knob (source P1).
        # Knob part frame origin is at the latch joint = the door's outer face
        # (door-local x=0). Knob geometry extends along +X (door normal, the
        # latch axis), so the child AABB contains the joint origin (0,0,0).
        knob = model.part(f"latch_knob_{i}")
        knob.visual(Cylinder(radius=0.018, length=0.008),
                    origin=Origin(xyz=(0.004, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material=mats["hardware"], name="backplate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"industrial_steel", "warm_oak", "charcoal_satin"} else "metal.brushed_silver"))
        knob.visual(Box((0.014, 0.010, 0.034)),
                    origin=Origin(xyz=(0.010, 0.0, 0.0)),
                    material=mats["hardware"], name="handle_bar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"industrial_steel", "warm_oak", "charcoal_satin"} else "metal.brushed_silver"))
        knob.visual(Sphere(radius=0.006),
                    origin=Origin(xyz=(0.014, 0.0, -0.017)),
                    material=mats["hardware"], name="handle_tip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"industrial_steel", "warm_oak", "charcoal_satin"} else "metal.brushed_silver"))
        knob.inertial = Inertial.from_geometry(Box((0.04, 0.04, 0.04)), mass=0.1)
        latch_limits = MotionLimits(effort=4.0, velocity=4.0, lower=0.0, upper=math.pi / 2.0)
        # Latch joint origin on the leaf FRONT face (door-local x=FACE_THK); the
        # knob extends +X (proud) so the child AABB contains the origin.
        model.articulation(
            f"latch_{i}",
            ArticulationType.REVOLUTE,
            parent=door,
            child=knob,
            origin=Origin(xyz=(FACE_THK, direction * (dw - 0.10), 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=latch_limits,
            meta=_meta(ArticulationType.REVOLUTE, (1.0, 0.0, 0.0),
                       (FACE_THK, direction * (dw - 0.10), 0.0), latch_limits),
        )
        joints.append(f"latch_{i}")
        overlaps.append((f"latch_knob_{i}", f"door_{i}", "backplate", "leaf",
                         "Latch backplate seats flush on the door leaf face."))
    return joints, overlaps


def _drawer_rows(n: int, zone_bot: float, zone_top: float, inner_w: float):
    """Return list of (name, cy, cz, front_w, front_h, tray_w, tray_h, knob_ys).
    Even N>=4 -> dresser row/col grid; small N -> single stacked column."""
    rows = []
    reveal = 0.008
    if n >= 4 and n % 2 == 0:
        # Top row of (n-... ) -> use dresser-style: 4 small over (n-4)/2 wide pairs.
        # Simplify: split into rows of 2 wide drawers, with a top row of small if n in {4,6,8}.
        if n == 4:
            layout = [("wide", 2), ("wide", 2)]
        elif n == 6:
            layout = [("small", 2), ("wide", 2), ("wide", 2)]
        else:  # 8
            layout = [("small", 4), ("wide", 2), ("wide", 2)]
        nrows = len(layout)
        row_h = (zone_top - zone_bot) / nrows
        idx = 0
        for ri, (kind, cols) in enumerate(layout):
            cz = zone_top - row_h * (ri + 0.5)
            fh = row_h - reveal
            if kind == "small":
                fw = (inner_w - (cols + 1) * reveal) / cols
                for ci in range(cols):
                    cy = -inner_w / 2.0 + reveal + fw / 2.0 + ci * (fw + reveal)
                    rows.append((f"drawer_{idx}", cy, cz, fw, fh, fw - 0.02,
                                 max(fh * 0.7, 0.05), [0.0]))
                    idx += 1
            else:
                fw = (inner_w - 3 * reveal) / 2.0
                for ci in range(2):
                    cy = (-1 if ci == 0 else 1) * (fw / 2.0 + reveal / 2.0)
                    rows.append((f"drawer_{idx}", cy, cz, fw, fh, fw - 0.02,
                                 max(fh * 0.7, 0.05), [-fw * 0.25, fw * 0.25]))
                    idx += 1
    else:
        # Single stacked column.
        row_h = (zone_top - zone_bot) / n
        fw = inner_w - 0.02
        for i in range(n):
            cz = zone_bot + row_h * (i + 0.5)
            fh = row_h - reveal
            knob_ys = [0.0] if fw < 0.5 else [-fw * 0.25, fw * 0.25]
            rows.append((f"drawer_{i}", 0.0, cz, fw, fh, fw - 0.02,
                         max(fh * 0.7, 0.05), knob_ys))
    return rows


def _emit_drawer(model, carcass, fr: _Frame, r, mats, spec, joints, overlaps):
    name, cy, cz, fw, fh, tw, th, knob_ys = spec
    anchor_sign = -1.0 if cy >= 0.0 else 1.0
    anchor_y = cy + anchor_sign * (fw / 2.0 - 0.006)
    local_y = cy - anchor_y
    d = _build_drawer_part(model, name, fr, front_w=fw, front_h=fh, tray_w=tw,
                           tray_h=th, knob_ys=knob_ys, mats=mats, local_y=local_y)
    # Short side socket at the drawer's opening edge. This keeps the prismatic
    # joint anchored on real parent geometry without drawing a horizontal bar
    # across the drawer cavity.
    idx = name.split("_")[-1]
    _box(carcass, (fr.wall, 0.032, fh * 0.8),
         (fr.FRONT_X - fr.wall / 2.0, anchor_y, cz - 0.04),
         mats["carcass"], f"drawer_slide_socket_{idx}")
    joint_x = fr.FRONT_X
    origin = (joint_x, anchor_y, cz)
    limits = MotionLimits(effort=50.0, velocity=0.5, lower=0.0, upper=r.drawer_travel)
    model.articulation(
        f"carcass_to_{name}",
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=d,
        origin=Origin(xyz=origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=limits,
        meta=_meta(ArticulationType.PRISMATIC, (1.0, 0.0, 0.0), origin, limits),
    )
    joints.append(f"carcass_to_{name}")
    overlaps.append((name, "carcass", None, None,
                     "Drawer tray slides inside the carcass cavity; closed front seats on the opening."))


def _build_storage_drawers(model, carcass, fr: _Frame, r, mats):
    n = r.drawer_count
    zone_bot = fr.z0 + 0.03
    zone_top = fr.z1 - 0.02
    _build_front_frame_rails(carcass, fr, mats, zone_bot=zone_bot, zone_top=zone_top)
    joints, overlaps = [], []
    for spec in _drawer_rows(n, zone_bot, zone_top, fr.INNER_W):
        _emit_drawer(model, carcass, fr, r, mats, spec, joints, overlaps)
    return joints, overlaps


def _build_storage_sliding_doors(model, carcass, fr: _Frame, r, mats):
    """Two bypass sliding doors on top/bottom tracks, sliding along ±Y (width).
    Source 503dd3bb (remapped: width axis is Y in canonical frame)."""
    zone_bot = fr.z0 + 0.05
    zone_top = fr.z1 - 0.05
    _build_front_frame_rails(carcass, fr, mats, zone_bot=zone_bot, zone_top=zone_top)
    door_h = zone_top - zone_bot - 0.02
    door_zc = (zone_bot + zone_top) / 2.0
    # Top + bottom track rails on the front plane (full inner width so they
    # bridge to both side panels; the slide joints anchor on the top track).
    track_z_top = zone_top - 0.012
    track_z_bot = zone_bot + 0.012
    _box(carcass, (fr.wall, fr.INNER_W, 0.018), (fr.FRONT_X - fr.wall / 2.0, 0.0, track_z_top),
         mats["trim"], "top_track")
    _box(carcass, (fr.wall, fr.INNER_W, 0.018), (fr.FRONT_X - fr.wall / 2.0, 0.0, track_z_bot),
         mats["trim"], "bottom_track")
    # Each leaf covers slightly more than half the opening (overlap when closed).
    leaf_w = fr.INNER_W * 0.55
    travel = min(0.75, fr.INNER_W * 0.42)
    joints, overlaps = [], []
    # door_0 rides the proud front track; door_1 sits one leaf-thickness deeper
    # so the two bypass without colliding. The depth difference is realized via
    # each door's JOINT ORIGIN x (both within the track rail depth), while both
    # leaves are authored identically (local x in [-FACE_THK, 0]) so the child
    # frame origin (0,0,0) is contained in each leaf AABB.
    specs = [
        ("door_0", -fr.INNER_W / 2.0 + leaf_w / 2.0, fr.FRONT_X, 1.0),
        ("door_1", fr.INNER_W / 2.0 - leaf_w / 2.0, fr.FRONT_X - FACE_THK - 0.002, -1.0),
    ]
    # Child frame origin sits at the top track; the leaf body hangs down so its
    # center is at the opening center (door_zc).
    leaf_dz = door_zc - track_z_top
    for name, cy_closed, joint_x, axis_sign in specs:
        door = model.part(name)
        door.visual(
            Box((FACE_THK, leaf_w, door_h)),
            origin=Origin(xyz=(-FACE_THK / 2.0, 0.0, leaf_dz)),
            material=mats["front"],
            name="leaf", material_class_id=("wood.painted_clean" if r.palette_style in {"matte_black_wood", "lacquered_gray", "warm_oak", "charcoal_satin"} else "metal.paint_coated"),
        )
        # Recessed finger-grip flush in the leaf front face (does NOT protrude
        # past the leaf, so the rear bypass leaf never collides with it).
        door.visual(
            Box((FACE_THK * 0.6, 0.012, door_h * 0.4)),
            origin=Origin(xyz=(-FACE_THK * 0.5, axis_sign * (leaf_w / 2.0 - 0.03), leaf_dz)),
            material=mats["hardware"], name="grip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"industrial_steel", "warm_oak", "charcoal_satin"} else "metal.brushed_silver"),
        )
        door.inertial = Inertial.from_geometry(Box((FACE_THK, leaf_w, door_h)), mass=3.0)
        origin = (joint_x, cy_closed, track_z_top)
        limits = MotionLimits(effort=30.0, velocity=0.5, lower=0.0, upper=travel)
        model.articulation(
            f"{name}_slide",
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=door,
            origin=Origin(xyz=origin),
            axis=(0.0, axis_sign, 0.0),
            motion_limits=limits,
            meta=_meta(ArticulationType.PRISMATIC, (0.0, axis_sign, 0.0), origin, limits),
        )
        joints.append(f"{name}_slide")
    overlaps.append(("door_0", "door_1", "leaf", "leaf",
                     "Bypass sliding doors overlap in Y when closed; they ride different X-depth tracks."))
    for name in ("door_0", "door_1"):
        for track in ("top_track", "bottom_track"):
            overlaps.append((name, "carcass", "leaf", track,
                             "Sliding leaf laps the track rail by <2mm."))
    return joints, overlaps


def _build_storage_door_over_drawers(model, carcass, fr: _Frame, r, mats):
    """Upper 2 hinged doors (REVOLUTE Z) + lower 2 drawers (PRISMATIC X)."""
    divider_z = fr.z0 + (fr.z1 - fr.z0) * 0.52
    zone_bot = fr.z0 + 0.03
    zone_top = fr.z1 - 0.02
    _build_front_frame_rails(carcass, fr, mats, zone_bot=zone_bot, zone_top=zone_top)
    # Divider rail.
    _box(carcass, (fr.wall, fr.INNER_W, 0.02), (fr.BD - fr.wall / 2.0, 0.0, divider_z),
         mats["carcass"], "divider_rail")
    joints, overlaps = [], []
    # Upper doors.
    door_h = zone_top - divider_z - 0.012
    door_zc = (divider_z + zone_top) / 2.0
    half = fr.INNER_W / 2.0
    for i, (hinge_y, direction, axis_z) in enumerate(
        [(-half + 0.001, 1.0, -1.0), (half - 0.001, -1.0, 1.0)]
    ):
        dw = half - 0.006
        door = _build_hinged_door_part(model, f"door_{i}", fr, door_w=dw, door_h=door_h,
                                       direction=direction, mats=mats,
                                       leaf_mat_key="front" if i == 0 else "front_b")
        origin = (fr.FRONT_X, hinge_y, door_zc)
        limits = MotionLimits(effort=20.0, velocity=1.5, lower=0.0, upper=min(1.4, r.door_open_upper))
        model.articulation(
            f"carcass_to_door_{i}",
            ArticulationType.REVOLUTE,
            parent=carcass, child=door,
            origin=Origin(xyz=origin), axis=(0.0, 0.0, axis_z),
            motion_limits=limits,
            meta=_meta(ArticulationType.REVOLUTE, (0.0, 0.0, axis_z), origin, limits),
        )
        joints.append(f"carcass_to_door_{i}")
        for elem in ("side_panel_0", "side_panel_1"):
            overlaps.append((f"door_{i}", "carcass", "hinge_barrel", elem,
                             "Hinge knuckle laps the carcass side edge it pivots on."))
    # Lower drawers.
    drow_bot = zone_bot
    drow_top = divider_z - 0.012
    row_h = (drow_top - drow_bot)
    fw = (fr.INNER_W - 3 * 0.008) / 2.0
    fh = row_h - 0.01
    cz = (drow_bot + drow_top) / 2.0
    for ci in range(2):
        cy = (-1 if ci == 0 else 1) * (fw / 2.0 + 0.004)
        spec = (f"drawer_{ci}", cy, cz, fw, fh, fw - 0.02, max(fh * 0.7, 0.05),
                [-fw * 0.25, fw * 0.25])
        _emit_drawer(model, carcass, fr, r, mats, spec, joints, overlaps)
    return joints, overlaps


def _build_storage_flap_door(model, carcass, fr: _Frame, r, mats):
    """Single drop-down flap, REVOLUTE about +Y at the bottom front edge."""
    zone_bot = fr.z0 + 0.02
    zone_top = fr.z1 - 0.02
    _build_front_frame_rails(carcass, fr, mats, zone_bot=zone_bot, zone_top=zone_top)
    door_h = zone_top - zone_bot - 0.006
    door_w = fr.INNER_W - 0.01
    flap = model.part("flap_door")
    flap.visual(
        Box((FACE_THK, door_w, door_h)),
        origin=Origin(xyz=(-FACE_THK / 2.0, 0.0, door_h / 2.0)),
        material=mats["front"], name="door_slab", material_class_id=("wood.painted_clean" if r.palette_style in {"matte_black_wood", "lacquered_gray", "warm_oak", "charcoal_satin"} else "metal.paint_coated"),
    )
    # Chrome bar handle near the top edge (stands proud of the slab outer face,
    # overlapping it slightly so it stays connected to the door part).
    flap.visual(
        Box((0.016, door_w * 0.4, 0.012)),
        origin=Origin(xyz=(-FACE_THK - 0.005, 0.0, door_h - 0.04)),
        material=mats["hardware"], name="handle_bar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"industrial_steel", "warm_oak", "charcoal_satin"} else "metal.brushed_silver"),
    )
    flap.inertial = Inertial.from_geometry(Box((FACE_THK, door_w, door_h)), mass=3.0)
    hinge_z = zone_bot
    origin = (fr.FRONT_X, 0.0, hinge_z)
    limits = MotionLimits(effort=10.0, velocity=1.5, lower=0.0, upper=1.50)
    model.articulation(
        "carcass_to_flap_door",
        ArticulationType.REVOLUTE,
        parent=carcass, child=flap,
        origin=Origin(xyz=origin), axis=(0.0, 1.0, 0.0),
        motion_limits=limits,
        meta=_meta(ArticulationType.REVOLUTE, (0.0, 1.0, 0.0), origin, limits),
    )
    return ["carcass_to_flap_door"], []


def _build_storage_hinged_single_door(model, carcass, fr: _Frame, r, mats):
    """Single side-hinged door (REVOLUTE +Z) + fixed interior shelf."""
    zone_bot = fr.z0 + 0.02
    zone_top = fr.z1 - 0.02
    _build_front_frame_rails(carcass, fr, mats, zone_bot=zone_bot, zone_top=zone_top)
    door_h = zone_top - zone_bot - 0.006
    door_zc = (zone_bot + zone_top) / 2.0
    dw = fr.INNER_W - 0.01
    # Interior shelf (fixed carcass visual). Span the full inner width and from
    # the back panel forward so it bridges to the carcass shell (no island).
    _box(carcass, (fr.BD - fr.wall, fr.INNER_W + 0.004, 0.015),
         ((fr.BD + fr.wall) / 2.0, 0.0, door_zc), mats["carcass"], "interior_shelf")
    door = _build_hinged_door_part(model, "door", fr, door_w=dw, door_h=door_h,
                                   direction=1.0, mats=mats)
    hinge_y = -fr.INNER_W / 2.0 + 0.001
    origin = (fr.FRONT_X, hinge_y, door_zc)
    limits = MotionLimits(effort=20.0, velocity=1.5, lower=0.0, upper=1.50)
    model.articulation(
        "carcass_to_door",
        ArticulationType.REVOLUTE,
        parent=carcass, child=door,
        origin=Origin(xyz=origin), axis=(0.0, 0.0, -1.0),
        motion_limits=limits,
        meta=_meta(ArticulationType.REVOLUTE, (0.0, 0.0, -1.0), origin, limits),
    )
    overlaps = [("door", "carcass", "hinge_barrel", elem,
                 "Hinge knuckle laps the carcass side edge it pivots on.")
                for elem in ("side_panel_0", "side_panel_1", "interior_shelf")]
    return ["carcass_to_door"], overlaps


def _build_storage_niche_over_drawer(model, carcass, fr: _Frame, r, mats):
    """Upper fixed open display niche (no joint) + single lower PRISMATIC drawer."""
    divider_z = fr.z0 + (fr.z1 - fr.z0) * 0.45
    zone_bot = fr.z0 + 0.03
    _build_front_frame_rails(carcass, fr, mats, zone_bot=zone_bot, zone_top=divider_z)
    # Niche divider shelf + back (fixed carcass visuals).
    _box(carcass, (fr.BD - 0.04, fr.INNER_W, 0.016), ((fr.BD) / 2.0, 0.0, divider_z),
         mats["carcass"], "divider_shelf")
    _box(carcass, (fr.BD - 0.06, fr.INNER_W + 0.004, 0.014),
         ((fr.BD) / 2.0, 0.0, fr.z1 - 0.04), mats["carcass"], "niche_top_shelf")
    joints, overlaps = [], []
    row_h = divider_z - zone_bot - 0.012
    fw = fr.INNER_W - 0.02
    fh = row_h
    cz = zone_bot + row_h / 2.0
    knob_ys = [0.0] if fw < 0.5 else [-fw * 0.25, fw * 0.25]
    spec = ("drawer_0", 0.0, cz, fw, fh, fw - 0.02, max(fh * 0.7, 0.05), knob_ys)
    # niche drawer travel is shorter
    spec_r = r
    _emit_drawer(model, carcass, fr, spec_r, mats, spec, joints, overlaps)
    return joints, overlaps


_STORAGE_FACTORIES = {
    "hinged_doors": _build_storage_hinged_doors,
    "drawers": _build_storage_drawers,
    "sliding_doors": _build_storage_sliding_doors,
    "door_over_drawers": _build_storage_door_over_drawers,
    "flap_door": _build_storage_flap_door,
    "hinged_single_door": _build_storage_hinged_single_door,
    "niche_over_drawer": _build_storage_niche_over_drawer,
}


# ===========================================================================
# Top-level builder
# ===========================================================================
def build_cabinet(
    config: CabinetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or CabinetConfig()
    r = resolve_config(cfg)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-cabinet-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {key: model.material(f"cabinet_{key}_{r.palette_style}", rgba=rgba)
            for key, rgba in palette.items()}

    fr = _make_frame(r)
    carcass = model.part("carcass")
    _build_carcass_shell(carcass, fr, mats)
    carcass.inertial = Inertial.from_geometry(
        Box((fr.BD, fr.BW, fr.BH)),
        mass=40.0,
        origin=Origin(xyz=(fr.BD / 2.0, 0.0, fr.z0 + fr.BH / 2.0)),
    )

    base_joints = _build_base(model, carcass, fr, r, mats)
    storage_joints, overlaps = _STORAGE_FACTORIES[r.storage_mechanism](
        model, carcass, fr, r, mats
    )

    model.meta["slot_choices"] = _slot_choices_for_resolved(r)
    model.meta["_cabinet_overlaps"] = overlaps
    model.meta["_cabinet_base_joints"] = base_joints
    model.meta["_cabinet_storage_joints"] = storage_joints
    return model


def build_seeded_cabinet(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_cabinet(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_cabinet_tests(object_model: ArticulatedObject, config: CabinetConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("carcass part present", "carcass" in part_names)

    # Declare element-scoped overlaps recorded during build.
    overlaps = object_model.meta.get("_cabinet_overlaps", [])
    for pa, pb, ea, eb, reason in overlaps:
        if pa not in part_names or pb not in part_names:
            continue
        if ea is None:
            ctx.allow_overlap(object_model.get_part(pa), object_model.get_part(pb), reason=reason)
        else:
            ctx.allow_overlap(object_model.get_part(pa), object_model.get_part(pb),
                              elem_a=ea, elem_b=eb, reason=reason)

    # Caster wheel hub press-fit into fork arms.
    for jn in object_model.meta.get("_cabinet_base_joints", []):
        if jn.startswith("caster_") and jn.endswith("_axle"):
            i = jn.split("_")[1]
            wp = f"caster_wheel_{i}"
            if wp in part_names:
                for elem in ("wheel", "axle_stub", "wheel_web"):
                    ctx.allow_overlap(object_model.get_part(wp), object_model.get_part("carcass"),
                                      elem_a=elem, elem_b=f"caster_fork_{i}",
                                      reason="Caster wheel/axle press-fits into the fork bearing arms.")

    # Grounding: the lowest geometry across ALL parts sits on the floor (for
    # casters the wheels — separate parts — are what touch the ground).
    cb = ctx.part_world_aabb(object_model.get_part("carcass"))
    ctx.check("carcass has bounds", cb is not None, details=str(cb))
    zmins = []
    for p in object_model.parts:
        ab = ctx.part_world_aabb(p)
        if ab is not None:
            zmins.append(ab[0][2])
    if zmins:
        ctx.check("base rests on the floor", abs(min(zmins)) <= 0.012,
                  details=f"zmin={min(zmins):.4f}")

    storage_joints = object_model.meta.get("_cabinet_storage_joints", [])

    # Storage-specific joint-type / axis assertions.
    sm = r.storage_mechanism
    if sm == "hinged_doors":
        door_parts = [n for n in part_names if n.startswith("door_")]
        ctx.check("door count matches", len(door_parts) == r.door_count,
                  details=f"expected {r.door_count}, got {len(door_parts)}")
        for i in range(r.door_count):
            j = object_model.get_articulation(f"door_{i}_hinge")
            ctx.check(f"door_{i} revolute vertical",
                      j.articulation_type == ArticulationType.REVOLUTE
                      and abs(j.axis[0]) < 1e-9 and abs(j.axis[1]) < 1e-9
                      and abs(abs(j.axis[2]) - 1.0) < 1e-9,
                      details=str(j.axis))
    elif sm == "drawers":
        d_parts = [n for n in part_names if n.startswith("drawer_")]
        ctx.check("drawer count matches", len(d_parts) == r.drawer_count,
                  details=f"expected {r.drawer_count}, got {len(d_parts)}")
        for j in object_model.articulations:
            if j.name.startswith("carcass_to_drawer_"):
                ctx.check(f"{j.name} prismatic +X",
                          j.articulation_type == ArticulationType.PRISMATIC
                          and j.axis[0] > 0.99,
                          details=str(j.axis))
    elif sm == "sliding_doors":
        for j in object_model.articulations:
            if j.name.endswith("_slide"):
                ctx.check(f"{j.name} prismatic along Y",
                          j.articulation_type == ArticulationType.PRISMATIC
                          and abs(abs(j.axis[1]) - 1.0) < 1e-6,
                          details=str(j.axis))
    elif sm == "flap_door":
        j = object_model.get_articulation("carcass_to_flap_door")
        ctx.check("flap revolute about +Y",
                  j.articulation_type == ArticulationType.REVOLUTE
                  and abs(abs(j.axis[1]) - 1.0) < 1e-6, details=str(j.axis))
    elif sm == "hinged_single_door":
        j = object_model.get_articulation("carcass_to_door")
        ctx.check("single door revolute vertical",
                  j.articulation_type == ArticulationType.REVOLUTE
                  and abs(abs(j.axis[2]) - 1.0) < 1e-9, details=str(j.axis))
    elif sm == "door_over_drawers":
        ctx.check("has both door and drawer joints",
                  any(n.startswith("carcass_to_door_") for n in joint_names)
                  and any(n.startswith("carcass_to_drawer_") for n in joint_names))
    elif sm == "niche_over_drawer":
        ctx.check("niche has exactly one drawer joint",
                  sum(1 for n in joint_names if n.startswith("carcass_to_drawer_")) == 1)

    ctx.check("has at least one storage joint", len(storage_joints) >= 1)

    # Base support: casters add CONTINUOUS wheels.
    if r.base_support == "casters":
        wheels = [n for n in part_names if n.startswith("caster_wheel_")]
        ctx.check("four caster wheels", len(wheels) == 4, details=str(wheels))
        for j in object_model.articulations:
            if j.name.startswith("caster_") and j.name.endswith("_axle"):
                ctx.check(f"{j.name} continuous",
                          j.articulation_type == ArticulationType.CONTINUOUS)

    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "CabinetConfig",
    "ResolvedCabinetConfig",
    "build_cabinet",
    "build_seeded_cabinet",
    "config_from_seed",
    "resolve_config",
    "run_cabinet_tests",
    "slot_choices_for_seed",
]
