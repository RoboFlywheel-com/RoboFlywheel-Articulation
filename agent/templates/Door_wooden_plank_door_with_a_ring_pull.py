# SPDX-License-Identifier: Apache-2.0

"""Rustic ledged-and-braced vertical-plank door — modular procedural template.

A ``plank_ring_door`` is a heavy cottage/castle door: a single vertical-timber
leaf hung on a stone surround by a VERTICAL (Z) hinge, with a real wrought-iron
ring-pull handle that swings on a HORIZONTAL (Y) pivot. Two REVOLUTE joints make
the motion spine; an optional PRISMATIC slide bolt is the gated third DOF.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Door_wooden_plank_door_with_a_ring_pull.md`` and the
``plank_ring_door`` 5-star sample pool (2 parents + 9 slot-fork variants), all
synced under ``data/records/``.

Structure (pattern = ``mixed``): a single root ``stone_surround`` part (two
jambs + lintel + arched/flat head + stoop + iron jamb pintles), with a
``door_leaf`` REVOLUTE child and a ``ring_pull`` REVOLUTE child of the leaf
(plus an optional ``door_bolt`` PRISMATIC child of the leaf). All planks,
bracing iron, clavos studs and the ring escutcheon/boss are inline visuals on
the leaf (Rule 1: non-articulating decoration is parent.visual, never a FIXED
part).

Six named structural axes (slots) + a multiplicity axis + palette:

  * Slot A ``plank_field`` (4): box_per_plank_3 / box_per_plank_5 /
    box_per_plank_9 / groove_cut_single_box — the leaf board topology. The N in
    the box-per-plank modules is the multiplicity axis (``plank_count``); the
    module name encodes N so the topology gate counts each N distinctly.
  * Slot B ``bracing`` (4): horizontal_ledges / strap_hinge_face /
    z_brace_ledged / framed_and_braced — the front iron bracing, each ending in
    a hinge barrel/knuckle that wraps the jamb pintle (the leaf support path).
  * Slot C ``top_profile`` (2): flat_top / arched_top — flat square head vs a
    graduated segmental-arch plank top (needs an arched surround soffit).
  * Slot D ``ring_hardware`` (2): square_plate / star_plate — the escutcheon
    the ring boss mounts on.
  * Slot E ``clavos_field`` (3): no_clavos / clavos_grid / strap_studs_row —
    decorative stud field (a secondary multiplicity axis when present).
  * Slot F ``plank_seam`` (2): flat_butted / v_groove — plank-edge seam profile.
  * ``slide_bolt`` (gated): an optional PRISMATIC door bolt (open-parent subdomain).

The two hinge joints (leaf-to-surround captured-pin barrel, ring-on-boss) and
the slide bolt are captured-pin / captured-slide geometry, so they omit
``MatingContract`` (grandfathered) and are guarded by the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests allow_overlap block).

Compatibility gating (resolve_config, spec §matrix):
  * arched_top REQUIRES arched_surround (else a flat lintel soffit clips the
    round head) — resolve binds surround_style to top_profile.
  * strap_studs_row REQUIRES strap_hinge_face (bolts rivet the strap) — else it
    degrades to no_clavos.
  * v_groove / clavos_grid only apply to box-per-plank leaves (the groove-cut
    single-box leaf has no per-plank boxes to chamfer or align a grid to) — they
    degrade on the groove_cut leaf.
  * slide_bolt is present only on the groove_cut leaf subdomain, and defaults
    off otherwise.
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
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True


# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
PlankField = Literal[
    "box_per_plank_3",
    "box_per_plank_5",
    "box_per_plank_9",
    "groove_cut_single_box",
]
Bracing = Literal[
    "horizontal_ledges",
    "strap_hinge_face",
    "z_brace_ledged",
    "framed_and_braced",
]
TopProfile = Literal[
    "flat_top",
    "arched_top",
    "gothic_lancet_top",
    "shouldered_camber_top",
]
RingHardware = Literal[
    "ring_on_square_plate",
    "ring_on_star_plate",
    "knocker_ring_on_boss",
]
ClavosField = Literal["no_clavos", "clavos_grid", "strap_studs_row"]
PlankSeam = Literal["flat_butted", "v_groove"]
SurroundStyle = Literal["square_header", "arched_surround"]
SlideBolt = Literal["none", "present"]
PaletteStyle = Literal[
    "dark_oak_black_iron",
    "weathered_grey_rust",
    "light_timber_bronze",
    "walnut_pewter",
    "bleached_oak_blacksmith",
    "redwood_castiron",
]

PLANK_FIELDS: tuple[PlankField, ...] = (
    "box_per_plank_3",
    "box_per_plank_5",
    "box_per_plank_9",
    "groove_cut_single_box",
)
BRACINGS: tuple[Bracing, ...] = (
    "horizontal_ledges",
    "strap_hinge_face",
    "z_brace_ledged",
    "framed_and_braced",
)
TOP_PROFILES: tuple[TopProfile, ...] = (
    "flat_top",
    "arched_top",
    "gothic_lancet_top",
    "shouldered_camber_top",
)
RING_HARDWARES: tuple[RingHardware, ...] = (
    "ring_on_square_plate",
    "ring_on_star_plate",
    "knocker_ring_on_boss",
)
CLAVOS_FIELDS: tuple[ClavosField, ...] = (
    "no_clavos",
    "clavos_grid",
    "strap_studs_row",
)
PLANK_SEAMS: tuple[PlankSeam, ...] = ("flat_butted", "v_groove")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "dark_oak_black_iron",
    "weathered_grey_rust",
    "light_timber_bronze",
    "walnut_pewter",
    "bleached_oak_blacksmith",
    "redwood_castiron",
)

# plank_count of each box-per-plank module (the multiplicity axis).
_PLANK_FIELD_N: dict[PlankField, int] = {
    "box_per_plank_3": 3,
    "box_per_plank_5": 5,
    "box_per_plank_9": 9,
    "groove_cut_single_box": 6,  # groove-cut uses N seam lines (parent open = 6)
}
# Plank-field sampling weights (spec axis 1: small N high-frequency, big N rare,
# groove-cut a minority).
_PLANK_FIELD_WEIGHTS = (0.30, 0.34, 0.12, 0.24)

# Clavos / multiplicity ranges.
CLAVOS_ROWS_RANGE = (4, 8)
CLAVOS_COLS_RANGE = (2, 5)
STUDS_PER_STRAP_RANGE = (4, 8)


# ---------------------------------------------------------------------------
# Palette (spec §palette). Each entry maps the four logical materials (wood,
# wood_dark groove/backing, iron, stone) used by EVERY .visual on the model.
# wood_dark is derived per-palette as wood * 0.62 (spec note).
# ---------------------------------------------------------------------------
def _scale(rgba: tuple[float, float, float, float], k: float) -> tuple[float, float, float, float]:
    r, g, b, a = rgba
    return (round(r * k, 4), round(g * k, 4), round(b * k, 4), a)


_PALETTE_BASE: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "dark_oak_black_iron": {
        "wood": (0.28, 0.20, 0.13, 1.0),
        "iron": (0.06, 0.06, 0.07, 1.0),
        "stone": (0.50, 0.49, 0.47, 1.0),
    },
    "weathered_grey_rust": {
        "wood": (0.47, 0.41, 0.32, 1.0),
        "iron": (0.21, 0.18, 0.16, 1.0),
        "stone": (0.56, 0.55, 0.52, 1.0),
    },
    "light_timber_bronze": {
        "wood": (0.74, 0.66, 0.50, 1.0),
        "iron": (0.40, 0.30, 0.16, 1.0),
        "stone": (0.62, 0.60, 0.55, 1.0),
    },
    "walnut_pewter": {
        "wood": (0.33, 0.24, 0.18, 1.0),
        "iron": (0.42, 0.42, 0.45, 1.0),
        "stone": (0.52, 0.51, 0.50, 1.0),
    },
    "bleached_oak_blacksmith": {
        "wood": (0.80, 0.77, 0.70, 1.0),
        "iron": (0.10, 0.10, 0.11, 1.0),
        "stone": (0.60, 0.60, 0.58, 1.0),
    },
    "redwood_castiron": {
        "wood": (0.45, 0.26, 0.18, 1.0),
        "iron": (0.16, 0.15, 0.15, 1.0),
        "stone": (0.55, 0.53, 0.50, 1.0),
    },
}


def _palette_rgba(style: PaletteStyle) -> dict[str, tuple[float, float, float, float]]:
    base = _PALETTE_BASE[style]
    wood = base["wood"]
    stone = base["stone"]
    return {
        "wood": wood,
        "wood_dark": _scale(wood, 0.62),  # groove / backing shadow
        "iron": base["iron"],
        "stone": stone,
        "stone_dark": _scale(stone, 0.86),  # coursing / voussoir
        "stone_step": _scale(stone, 0.90),  # worn stoop
    }


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Mirrors the closed-parent constants.
# Frame: +X is the door facing (front of leaf points +X), +Y is the width
# direction (hinge jamb on -Y), +Z is up from the ground (z=0).
# ---------------------------------------------------------------------------
_DOOR_W = 0.85          # leaf width (Y)
_DOOR_H = 2.00          # leaf height (Z)
_DOOR_T = 0.050         # leaf thickness (X)
_PLANK_GAP = 0.004
_PLANK_T = 0.044        # plank board thickness (front face proud of backing)
_BACK_T = 0.012         # backing board thickness

_LEDGE_T = 0.022        # iron ledge/brace thickness (X)
_LEDGE_W = 0.075        # ledge board width (Z)
_BARREL_R = 0.018       # hinge barrel (knuckle) radius
_BARREL_LEN = 0.10      # barrel length (wraps pintle)
_STILE_W = 0.070        # framed-brace vertical stile width (Y)
_STILE_T = 0.020        # framed-brace stile thickness (X)

# Stone surround.
_JAMB_W = 0.16          # stone jamb width (Y) each side
_JAMB_D = 0.30          # stone jamb depth (X)
_HEADER_H = 0.22        # lintel height (Z)
_STEP_H = 0.12          # stoop top height
_STEP_RUN = 0.34
_LOWER_STEP_H = 0.06
_WALL_T = 0.28
_REVEAL = 0.03
_ARCH_RISE = 0.25       # arched-top rise above springline (segmental round head)
_LANCET_RISE = 0.40     # gothic lancet-top rise above springline (pointed two-arc)
# Shouldered cambered head (low head, square_header-compatible).
_CAMBER_RISE = 0.040    # camber rise at center above the baseline
_SHOULDER_DROP = 0.055  # vertical drop at the chamfered shoulder corners
_SHOULDER_WIDTH = 0.055 # horizontal extent of each shoulder chamfer

# Ring-pull hardware.
_RING_OUT_R = 0.058
_RING_TUBE_R = 0.0095
_PLATE_SIZE = 0.095     # square backplate edge (Y,Z)
_PLATE_T = 0.007        # backplate thickness (X)
_BOSS_R = 0.011
_BOSS_LEN = 0.022
_STRIKE_BOSS_R = 0.022  # knocker strike-boss radius (iron target)
_STRIKE_BOSS_H = 0.018  # knocker strike-boss protrusion from plank face (X)
_QUATREFOIL_D = 0.030   # star-plate lobe offset
_QUATREFOIL_R = 0.028   # star-plate lobe radius
_RIVET_R = 0.005

# Clavos / strap studs.
_CLAVO_R = 0.006
_STUD_Y_MARGIN = 0.12
_STUD_Z_MARGIN = 0.20
_STRAP_STUD_R = 0.009
_STRAP_STUD_H = 0.007

# Slide bolt.
_BOLT_ROD_R = 0.012
_BOLT_ROD_LEN = 0.40
_BOLT_TRAVEL = 0.10
_KEEPER_SPACING = 0.16

# Joint ranges (nominal).
_HINGE_UPPER = 2.0
_RING_UPPER = 1.2


@dataclass(frozen=True)
class PlankRingDoorConfig:
    plank_field: PlankField | None = None
    bracing: Bracing | None = None
    top_profile: TopProfile | None = None
    ring_hardware: RingHardware | None = None
    clavos_field: ClavosField | None = None
    plank_seam: PlankSeam | None = None
    slide_bolt: SlideBolt | None = None
    palette_style: PaletteStyle = "weathered_grey_rust"
    clavos_rows: int | None = None
    clavos_cols: int | None = None
    studs_per_strap: int | None = None
    leaf_width_scale: float = 1.0
    leaf_height_scale: float = 1.0
    ring_radius_scale: float = 1.0
    hinge_upper_scale: float = 1.0
    ring_upper_scale: float = 1.0
    name: str = "plank_ring_door"


@dataclass(frozen=True)
class ResolvedPlankRingDoorConfig:
    plank_field: PlankField
    bracing: Bracing
    top_profile: TopProfile
    ring_hardware: RingHardware
    clavos_field: ClavosField
    plank_seam: PlankSeam
    slide_bolt: SlideBolt
    surround_style: SurroundStyle
    palette_style: PaletteStyle
    plank_count: int
    clavos_rows: int
    clavos_cols: int
    studs_per_strap: int
    # Concrete geometry (scaled).
    door_w: float
    door_h: float
    door_t: float
    plank_w: float
    leaf_z0: float        # LOCAL z base for leaf authoring (== 0.0; leaf frame)
    leaf_world_z0: float  # world z of the leaf bottom (sits above the stoop)
    ring_out_r: float
    ring_tube_r: float
    hinge_upper: float
    ring_upper: float
    ring_lower: float
    name: str

    @property
    def is_box_per_plank(self) -> bool:
        return self.plank_field != "groove_cut_single_box"

    @property
    def is_knocker(self) -> bool:
        return self.ring_hardware == "knocker_ring_on_boss"

    @property
    def is_high_head(self) -> bool:
        """Tall leaf-top profiles (round / pointed peak) that need an arched
        surround soffit. Low heads (flat / shouldered camber) fit a square head."""
        return self.top_profile in ("arched_top", "gothic_lancet_top")


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Procedural sampling (Contract 4: deterministic, seed 0 not special).
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> PlankRingDoorConfig:
    rng = random.Random(seed)
    plank_field = rng.choices(PLANK_FIELDS, weights=_PLANK_FIELD_WEIGHTS, k=1)[0]
    bracing = rng.choice(BRACINGS)
    top_profile = rng.choice(TOP_PROFILES)
    ring_hardware = rng.choice(RING_HARDWARES)
    clavos_field = rng.choice(CLAVOS_FIELDS)
    plank_seam = rng.choice(PLANK_SEAMS)
    # slide bolt: only meaningful on the groove-cut subdomain, and rare there.
    slide_bolt: SlideBolt = (
        "present"
        if plank_field == "groove_cut_single_box" and rng.random() < 0.5
        else "none"
    )
    return PlankRingDoorConfig(
        plank_field=plank_field,
        bracing=bracing,
        top_profile=top_profile,
        ring_hardware=ring_hardware,
        clavos_field=clavos_field,
        plank_seam=plank_seam,
        slide_bolt=slide_bolt,
        palette_style=rng.choice(PALETTE_STYLES),
        clavos_rows=rng.randint(*CLAVOS_ROWS_RANGE),
        clavos_cols=rng.randint(*CLAVOS_COLS_RANGE),
        studs_per_strap=rng.randint(*STUDS_PER_STRAP_RANGE),
        leaf_width_scale=round(rng.uniform(0.92, 1.12), 4),
        leaf_height_scale=round(rng.uniform(0.93, 1.05), 4),
        ring_radius_scale=round(rng.uniform(0.88, 1.12), 4),
        hinge_upper_scale=round(rng.uniform(0.85, 1.15), 4),
        ring_upper_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_plank_ring_door_{seed}",
    )


def resolve_config(
    config: PlankRingDoorConfig | None = None,
) -> ResolvedPlankRingDoorConfig:
    cfg = config or PlankRingDoorConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    plank_field = _pick(cfg.plank_field, PLANK_FIELDS)
    bracing = _pick(cfg.bracing, BRACINGS)
    top_profile = _pick(cfg.top_profile, TOP_PROFILES)
    ring_hardware = _pick(cfg.ring_hardware, RING_HARDWARES)
    clavos_field = _pick(cfg.clavos_field, CLAVOS_FIELDS)
    plank_seam = _pick(cfg.plank_seam, PLANK_SEAMS)
    slide_bolt = _pick(cfg.slide_bolt, ("none", "present"))

    # --- Compatibility gating (spec §matrix). ---
    # (1) high-head profiles (arched_top / gothic_lancet_top) require an
    #     arched_surround soffit; low heads (flat_top / shouldered_camber_top)
    #     fit a square header.
    surround_style: SurroundStyle = (
        "arched_surround"
        if top_profile in ("arched_top", "gothic_lancet_top")
        else "square_header"
    )
    # (2) strap_studs_row requires strap_hinge_face bracing.
    if clavos_field == "strap_studs_row" and bracing != "strap_hinge_face":
        clavos_field = "no_clavos"
    is_box_per_plank = plank_field != "groove_cut_single_box"
    # (3) v_groove / clavos_grid only apply to box-per-plank leaves.
    if not is_box_per_plank:
        if plank_seam == "v_groove":
            plank_seam = "flat_butted"
        if clavos_field == "clavos_grid":
            clavos_field = "no_clavos"
    # (5) slide_bolt only on the groove-cut subdomain (open-parent family), and
    #     only with bracing that leaves the free-side mid band clear. The
    #     z-brace diagonal and framed stiles cross the bolt run, so the bolt is
    #     restricted to the ledged / strap-hinge subdomain (matching the open
    #     parent, which is strap-hinged).
    if plank_field != "groove_cut_single_box" or bracing not in (
        "horizontal_ledges",
        "strap_hinge_face",
    ):
        slide_bolt = "none"

    plank_count = _PLANK_FIELD_N[plank_field]

    # Multiplicity clamps.
    clavos_rows = int(_clamp(cfg.clavos_rows if cfg.clavos_rows is not None else 7, *CLAVOS_ROWS_RANGE))
    clavos_cols = int(_clamp(cfg.clavos_cols if cfg.clavos_cols is not None else 4, *CLAVOS_COLS_RANGE))
    studs_per_strap = int(
        _clamp(cfg.studs_per_strap if cfg.studs_per_strap is not None else 6, *STUDS_PER_STRAP_RANGE)
    )

    width_scale = _clamp(cfg.leaf_width_scale, 0.92, 1.12)
    height_scale = _clamp(cfg.leaf_height_scale, 0.93, 1.05)
    ring_scale = _clamp(cfg.ring_radius_scale, 0.88, 1.12)
    hinge_scale = _clamp(cfg.hinge_upper_scale, 0.85, 1.15)
    ring_upper_scale = _clamp(cfg.ring_upper_scale, 0.85, 1.15)

    door_w = _DOOR_W * width_scale
    door_h = _DOOR_H * height_scale
    # The leaf is authored in its own link frame with local bottom at z=0; the
    # hinge joint origin carries it up to the world bottom (just above the stoop).
    leaf_z0 = 0.0
    leaf_world_z0 = _STEP_H + 0.01

    usable_w = door_w - (plank_count - 1) * _PLANK_GAP
    plank_w = usable_w / plank_count

    # Ring radius (clamped so ring + tube fits the escutcheon footprint).
    ring_out_r = _RING_OUT_R * ring_scale
    if ring_hardware == "ring_on_square_plate":
        max_ring = _PLATE_SIZE / 2.0 - _RING_TUBE_R - 0.004
    else:
        max_ring = (_QUATREFOIL_D + _QUATREFOIL_R) - _RING_TUBE_R - 0.004
    ring_out_r = _clamp(ring_out_r, 0.045, max_ring)

    hinge_upper = _clamp(_HINGE_UPPER * hinge_scale, 1.2, 2.4)
    ring_upper = _clamp(_RING_UPPER * ring_upper_scale, 0.6, 1.4)
    # (4) knocker resolves a bidirectional ring joint range: negative q swings
    #     the ring DOWN to strike the boss. square/star plates only lift (q>=0).
    ring_lower = -1.0 if ring_hardware == "knocker_ring_on_boss" else 0.0

    return ResolvedPlankRingDoorConfig(
        plank_field=plank_field,
        bracing=bracing,
        top_profile=top_profile,
        ring_hardware=ring_hardware,
        clavos_field=clavos_field,
        plank_seam=plank_seam,
        slide_bolt=slide_bolt,
        surround_style=surround_style,
        palette_style=palette_style,
        plank_count=plank_count,
        clavos_rows=clavos_rows,
        clavos_cols=clavos_cols,
        studs_per_strap=studs_per_strap,
        door_w=door_w,
        door_h=door_h,
        door_t=_DOOR_T,
        plank_w=plank_w,
        leaf_z0=leaf_z0,
        leaf_world_z0=leaf_world_z0,
        ring_out_r=ring_out_r,
        ring_tube_r=_RING_TUBE_R,
        hinge_upper=hinge_upper,
        ring_upper=ring_upper,
        ring_lower=ring_lower,
        name=cfg.name or "plank_ring_door",
    )


def with_overrides(config: PlankRingDoorConfig, **kwargs: object) -> PlankRingDoorConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PlankRingDoorConfig | ResolvedPlankRingDoorConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedPlankRingDoorConfig)
        else resolve_config(config)
    )
    choices: list[tuple[str, str]] = [
        ("plank_field", r.plank_field),
        ("bracing", r.bracing),
        ("top_profile", r.top_profile),
        ("ring_hardware", r.ring_hardware),
        ("clavos_field", r.clavos_field),
        ("plank_seam", r.plank_seam),
    ]
    if r.slide_bolt == "present":
        choices.append(("slide_bolt", "present"))
    if r.clavos_field == "clavos_grid":
        choices.append(("clavos_grid", f"r{r.clavos_rows}c{r.clavos_cols}"))
    elif r.clavos_field == "strap_studs_row":
        choices.append(("strap_studs_row", f"k{r.studs_per_strap}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Derived leaf geometry (X positions of each layer in the leaf-local frame).
# The leaf part frame sits on the vertical hinge line (-Y jamb edge, y=0) at the
# door bottom; geometry extends toward +Y. Layers stack in +X:
#   backing (rear slab) -> planks -> bracing iron -> escutcheon -> boss.
# ===========================================================================
def _back_cx_x(r: ResolvedPlankRingDoorConfig) -> float:
    return -r.door_t / 2.0 + _BACK_T / 2.0


def _plank_cx_x(r: ResolvedPlankRingDoorConfig) -> float:
    return -r.door_t / 2.0 + _BACK_T + _PLANK_T / 2.0


def _plank_front_x(r: ResolvedPlankRingDoorConfig) -> float:
    return -r.door_t / 2.0 + _BACK_T + _PLANK_T  # plank front face X


def _ledge_cx_x(r: ResolvedPlankRingDoorConfig) -> float:
    return _plank_front_x(r) + _LEDGE_T / 2.0


# ---------------------------------------------------------------------------
# Arched-top helper (Slot C). Segmental arc top: plank top z graduates with y.
# ---------------------------------------------------------------------------
def _arch_params(r: ResolvedPlankRingDoorConfig):
    half_span = r.door_w / 2.0
    rise = _ARCH_RISE
    radius = (half_span * half_span + rise * rise) / (2.0 * rise)
    center_y = r.door_w / 2.0
    springline_z = r.leaf_z0 + r.door_h - rise
    center_z = springline_z - (radius - rise)
    return radius, center_y, springline_z, center_z


def _arch_z_at(r: ResolvedPlankRingDoorConfig, y: float) -> float:
    radius, center_y, springline_z, center_z = _arch_params(r)
    dist = abs(y - center_y)
    if dist < radius:
        return center_z + math.sqrt(radius * radius - dist * dist)
    return springline_z


# ---------------------------------------------------------------------------
# Gothic lancet-top helper (Slot C). Two circular arcs meeting at a center
# point (pointed peak). Source: gothic_top _lancet_arch_z L106-L129.
# ---------------------------------------------------------------------------
def _lancet_springline_z(r: ResolvedPlankRingDoorConfig) -> float:
    return r.leaf_z0 + r.door_h - _LANCET_RISE


def _lancet_z_at(r: ResolvedPlankRingDoorConfig, y: float) -> float:
    """Z of the lancet arch at span position y (leaf frame). Two arcs whose
    centers sit on the springline, meeting at a sharp peak at y = door_w/2."""
    W = r.door_w
    spring_z = _lancet_springline_z(r)
    rise = _LANCET_RISE
    if rise <= 1e-9 or W <= 1e-9:
        return spring_z
    # Arc center offset c (= radius) from the nearest spring point.
    c = W / 4.0 + rise * rise / W
    R = c
    half = W / 2.0
    dy = (y - c) if y <= half else (y - (W - c))
    val = R * R - dy * dy
    if val <= 0.0:
        return spring_z
    return spring_z + math.sqrt(val)


# ---------------------------------------------------------------------------
# Shouldered cambered-top helper (Slot C). A gentle upward circular arc across
# the leaf width (low head). Source: shoulder_top _camber_z_at L105-L112.
# ---------------------------------------------------------------------------
def _camber_params(r: ResolvedPlankRingDoorConfig):
    half_w = r.door_w / 2.0
    yc = (_CAMBER_RISE * _CAMBER_RISE - half_w * half_w) / (2.0 * _CAMBER_RISE)
    radius = math.sqrt(half_w * half_w + yc * yc)
    baseline_z = r.leaf_z0 + r.door_h - _CAMBER_RISE
    return half_w, yc, radius, baseline_z


def _camber_z_at(r: ResolvedPlankRingDoorConfig, y: float) -> float:
    """Z of the cambered top at span position y (leaf frame). A shallow arc
    through (0, baseline), (W/2, baseline+rise), (W, baseline)."""
    half_w, yc, radius, baseline_z = _camber_params(r)
    dy = y - half_w
    return baseline_z + yc + math.sqrt(max(0.0, radius * radius - dy * dy))


# ---------------------------------------------------------------------------
# Slot A + C + F: leaf body (backing + planks). Plank geometry depends on the
# seam (Slot F: box vs chamfer-cut mesh) and top profile (Slot C: full-height
# box vs graduated segmental-arc mesh).
# ---------------------------------------------------------------------------
def _v_groove_plank_mesh(thickness: float, width: float, height: float, name: str, assets):
    """Box plank with chamfered (V-groove) long edges. Source: vgroove
    _v_groove_plank_mesh L118-177."""
    half_t = thickness / 2.0
    half_w = width / 2.0
    cw = min(0.005, width * 0.3)   # chamfer run along Y
    cd = min(0.006, thickness * 0.45)  # chamfer depth from front (-X here, +half_t)
    plank = (
        cq.Workplane("XY")
        .box(thickness, width, height, centered=(True, True, False))
    )
    # Two chamfer cutter prisms running the full height, at +Y and -Y front edges.
    for sign in (1.0, -1.0):
        edge_y = sign * half_w
        cutter = (
            cq.Workplane("XY")
            .polyline(
                [
                    (half_t, edge_y),
                    (half_t, edge_y - sign * cw),
                    (half_t - cd, edge_y),
                ]
            )
            .close()
            .extrude(height + 0.002)
            .translate((0.0, 0.0, -0.001))
        )
        plank = plank.cut(cutter)
    return mesh_from_cadquery(plank, name, assets=assets)


def _arched_plank_mesh(r: ResolvedPlankRingDoorConfig, cy: float, name: str, assets):
    """A single plank whose top follows the segmental arch. Source: archtop
    graduated plank loop L344-374. Authored z absolute (z0..arch top)."""
    half_w = r.plank_w / 2.0
    z0 = r.leaf_z0
    y_left = cy - half_w
    y_right = cy + half_w
    z_left = _arch_z_at(r, y_left)
    z_right = _arch_z_at(r, y_right)
    z_center = _arch_z_at(r, cy)
    # Sketch in the YZ plane (relative to plank center cy), extrude PLANK_T in X.
    plank = (
        cq.Workplane("YZ")
        .polyline(
            [
                (-half_w, z0),
                (half_w, z0),
                (half_w, z_right),
            ]
        )
        .threePointArc((0.0, z_center), (-half_w, z_left))
        .close()
        .extrude(_PLANK_T)
    )
    # YZ extrude grows along +X starting at x=0; shift so plank front sits right.
    plank = plank.translate((_plank_cx_x(r) - _PLANK_T / 2.0, cy, 0.0))
    return mesh_from_cadquery(plank, name, assets=assets)


def _lancet_plank_mesh(
    r: ResolvedPlankRingDoorConfig, y_left: float, y_right: float, name: str, assets
):
    """A single plank whose top follows the pointed lancet arch, sampled along
    the span (real CadQuery arc faces, polyline-approximated two-arc curve).
    Source: gothic_top _make_arch_plank_solid L132-L172. Authored in absolute
    leaf-Y; the visual origin shifts it to the plank front X (see emit)."""
    z0 = r.leaf_z0
    z_left = _lancet_z_at(r, y_left)
    wp = cq.Workplane("YZ").moveTo(y_left, z0).lineTo(y_left, z_left)
    n_samples = 10
    for k in range(1, n_samples + 1):
        y = y_left + (y_right - y_left) * k / n_samples
        wp = wp.lineTo(y, _lancet_z_at(r, y))
    wp = wp.lineTo(y_right, z0).close()
    plank = wp.extrude(_PLANK_T)
    return mesh_from_cadquery(plank, name, assets=assets)


def _camber_plank_mesh(
    r: ResolvedPlankRingDoorConfig,
    y_left: float,
    y_right: float,
    *,
    shoulder: str,
    name: str,
    assets,
):
    """A single plank whose top follows the gentle camber arc, with an optional
    shoulder chamfer dropping the outer upper corner (shoulder in {"none",
    "left", "right"}). Source: shoulder_top per-plank profile L336-L376."""
    z0 = r.leaf_z0
    z_left = _camber_z_at(r, y_left)
    z_right = _camber_z_at(r, y_right)
    y_mid = (y_left + y_right) / 2.0
    z_mid = _camber_z_at(r, y_mid)
    wp = cq.Workplane("YZ").moveTo(y_left, z0)
    if shoulder == "left":
        # Leftmost plank: chamfer the outer (left) upper corner.
        wp = wp.lineTo(y_left, z_left - _SHOULDER_DROP)
        wp = wp.lineTo(y_left + _SHOULDER_WIDTH, z_left)
        wp = wp.threePointArc((y_mid, z_mid), (y_right, z_right))
    elif shoulder == "right":
        # Rightmost plank: chamfer the outer (right) upper corner.
        wp = wp.lineTo(y_left, z_left)
        wp = wp.threePointArc((y_mid, z_mid), (y_right - _SHOULDER_WIDTH, z_right))
        wp = wp.lineTo(y_right, z_right - _SHOULDER_DROP)
    else:
        wp = wp.lineTo(y_left, z_left)
        wp = wp.threePointArc((y_mid, z_mid), (y_right, z_right))
    wp = wp.lineTo(y_right, z0).close()
    plank = wp.extrude(_PLANK_T)
    return mesh_from_cadquery(plank, name, assets=assets)


def _emit_leaf_body(leaf, r: ResolvedPlankRingDoorConfig, mats, *, assets) -> None:
    z0 = r.leaf_z0
    leaf_h = r.door_h
    back_cy = r.door_w / 2.0
    back_cz = z0 + leaf_h / 2.0
    arched = r.top_profile == "arched_top"

    gothic = r.top_profile == "gothic_lancet_top"
    shoulder = r.top_profile == "shouldered_camber_top"

    # Backing board (Rule: carries planks; wood_dark groove material).
    if arched:
        radius, center_y, springline_z, center_z = _arch_params(r)
        # Arched backing: straight sides to springline then arc across the top.
        back = (
            cq.Workplane("YZ")
            .polyline(
                [
                    (0.0, z0),
                    (r.door_w, z0),
                    (r.door_w, springline_z),
                ]
            )
            .threePointArc((center_y, z0 + leaf_h), (0.0, springline_z))
            .close()
            .extrude(_BACK_T)
        )
        back = back.translate((_back_cx_x(r) - _BACK_T / 2.0, 0.0, 0.0))
        leaf.visual(
            mesh_from_cadquery(back, "backing_board", assets=assets),
            material=mats["wood_dark"],
            name="backing_board", material_class_id=("wood.oak" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "light_timber_bronze", "walnut_pewter", "bleached_oak_blacksmith"} else "wood.mahogany_teak_dark"),
        )
    elif gothic:
        # Lancet backing: straight sides to the springline, then a full-width
        # two-arc pointed curve across the top (source _make_arch_board_solid).
        spring_z = _lancet_springline_z(r)
        pts = [(0.0, z0), (0.0, spring_z)]
        half = r.door_w / 2.0
        n_seg = 16
        seg_half = n_seg // 2
        for k in range(1, seg_half + 1):
            y = half * k / seg_half
            pts.append((y, _lancet_z_at(r, y)))
        for k in range(1, seg_half + 1):
            y = half + half * k / seg_half
            pts.append((y, _lancet_z_at(r, y)))
        pts.append((r.door_w, z0))
        back = cq.Workplane("YZ").polyline(pts).close().extrude(_BACK_T)
        back = back.translate((_back_cx_x(r) - _BACK_T / 2.0, 0.0, 0.0))
        leaf.visual(
            mesh_from_cadquery(back, "backing_board", assets=assets),
            material=mats["wood_dark"],
            name="backing_board", material_class_id=("wood.oak" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "light_timber_bronze", "walnut_pewter", "bleached_oak_blacksmith"} else "wood.mahogany_teak_dark"),
        )
    else:
        # flat_top / shouldered_camber_top: full-height rectangular backing
        # (the shallow camber/shoulder geometry stays within the box top).
        leaf.visual(
            Box((_BACK_T, r.door_w, leaf_h)),
            origin=Origin(xyz=(_back_cx_x(r), back_cy, back_cz)),
            material=mats["wood_dark"],
            name="backing_board", material_class_id=("wood.oak" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "light_timber_bronze", "walnut_pewter", "bleached_oak_blacksmith"} else "wood.mahogany_teak_dark"),
        )

    if r.plank_field == "groove_cut_single_box":
        # Single leaf box with V-seam lines cut between planks (Slot A groove-cut).
        n = r.plank_count
        plank_w = r.plank_w
        leaf_box = (
            cq.Workplane("XY")
            .box(_PLANK_T, r.door_w, leaf_h, centered=(True, True, False))
        )
        groove_w = 0.012
        groove_d = 0.010
        for i in range(1, n):
            gy = -r.door_w / 2.0 + i * (plank_w + _PLANK_GAP)
            cutter = (
                cq.Workplane("XY")
                .box(groove_d + 0.001, groove_w, leaf_h + 0.01, centered=(True, True, False))
                .translate((_PLANK_T / 2.0 - groove_d / 2.0, gy, -0.005))
            )
            leaf_box = leaf_box.cut(cutter)
        leaf_box = leaf_box.translate((_plank_cx_x(r), r.door_w / 2.0, z0))
        leaf.visual(
            mesh_from_cadquery(leaf_box, "leaf_planks", assets=assets),
            material=mats["wood"],
            name="leaf_planks", material_class_id=("wood.oak" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "light_timber_bronze", "walnut_pewter", "bleached_oak_blacksmith"} else "wood.mahogany_teak_dark"),
        )
        return

    # box-per-plank: one Box (or V-groove / arched / lancet / camber mesh) per plank.
    n = r.plank_count
    plank_w = r.plank_w
    # Rear plank face X (lancet/camber meshes are authored from x=0 in absolute Y).
    plank_rear_x = _plank_cx_x(r) - _PLANK_T / 2.0
    for i in range(n):
        cy = plank_w / 2.0 + i * (plank_w + _PLANK_GAP)
        y_left = i * (plank_w + _PLANK_GAP)
        y_right = y_left + plank_w
        if arched:
            leaf.visual(
                _arched_plank_mesh(r, cy, f"plank_{i}", assets),
                material=mats["wood"],
                name=f"plank_{i}", material_class_id=("wood.oak" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "light_timber_bronze", "walnut_pewter", "bleached_oak_blacksmith"} else "wood.mahogany_teak_dark"),
            )
        elif gothic:
            leaf.visual(
                _lancet_plank_mesh(r, y_left, y_right, f"plank_{i}", assets),
                origin=Origin(xyz=(plank_rear_x, 0.0, 0.0)),
                material=mats["wood"],
                name=f"plank_{i}", material_class_id=("wood.oak" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "light_timber_bronze", "walnut_pewter", "bleached_oak_blacksmith"} else "wood.mahogany_teak_dark"),
            )
        elif shoulder:
            which = (
                "left" if i == 0 else "right" if i == n - 1 else "none"
            )
            leaf.visual(
                _camber_plank_mesh(
                    r, y_left, y_right, shoulder=which, name=f"plank_{i}", assets=assets
                ),
                origin=Origin(xyz=(plank_rear_x, 0.0, 0.0)),
                material=mats["wood"],
                name=f"plank_{i}", material_class_id=("wood.oak" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "light_timber_bronze", "walnut_pewter", "bleached_oak_blacksmith"} else "wood.mahogany_teak_dark"),
            )
        elif r.plank_seam == "v_groove":
            mesh = _v_groove_plank_mesh(_PLANK_T, plank_w, leaf_h, f"plank_{i}", assets)
            leaf.visual(
                mesh,
                origin=Origin(xyz=(_plank_cx_x(r), cy, z0)),
                material=mats["wood"],
                name=f"plank_{i}", material_class_id=("wood.oak" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "light_timber_bronze", "walnut_pewter", "bleached_oak_blacksmith"} else "wood.mahogany_teak_dark"),
            )
        else:
            leaf.visual(
                Box((_PLANK_T, plank_w, leaf_h)),
                origin=Origin(xyz=(_plank_cx_x(r), cy, back_cz)),
                material=mats["wood"],
                name=f"plank_{i}", material_class_id=("wood.oak" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "light_timber_bronze", "walnut_pewter", "bleached_oak_blacksmith"} else "wood.mahogany_teak_dark"),
            )


# ---------------------------------------------------------------------------
# Slot B: front bracing. Each variant emits its bracing visuals + a hinge
# barrel/knuckle at the -Y edge (bottom + top) that wraps the jamb pintle. The
# barrel y-center is just past the leaf edge (y<0) so it captures the pin.
# Returns the (bottom_z, top_z) barrel heights for the pintle placement.
# ---------------------------------------------------------------------------
def _emit_hinge_knuckle(leaf, r: ResolvedPlankRingDoorConfig, mats, *, tag: str, cz: float) -> None:
    ledge_cx_x = _ledge_cx_x(r)
    leaf.visual(
        Cylinder(radius=_BARREL_R, length=_BARREL_LEN),
        origin=Origin(xyz=(ledge_cx_x, -0.006, cz)),
        material=mats["iron"],
        name=f"hinge_barrel_{tag}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
    )
    stub_w = 0.075
    leaf.visual(
        Box((_LEDGE_T, stub_w, _LEDGE_W * 0.6)),
        origin=Origin(xyz=(ledge_cx_x, -0.005 + stub_w / 2.0, cz)),
        material=mats["iron"],
        name=f"hinge_stub_{tag}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
    )


def _spade_strap_mesh(r: ResolvedPlankRingDoorConfig, name: str, assets):
    """Tapered spade-tip wrought-iron strap, lying flat on the plank face,
    running along +Y from near the hinge edge to the latch edge. Source:
    strapstud _spade_strap_mesh L291-315 (authored along Y, thin in X)."""
    length = r.door_w - 0.06
    body_w = 0.060   # width along Z
    tip_w = 0.100
    strap_t = _LEDGE_T
    taper_start = length - 0.12
    spade_mid = length - 0.04
    strap = (
        cq.Workplane("XZ")  # sketch in X(->Z plane is XZ); we use Y as sweep -> use YZ
        .polyline(
            [
                (0.0, -body_w / 2.0),
                (taper_start, -body_w / 2.0),
                (spade_mid, -tip_w / 2.0),
                (length, 0.0),
                (spade_mid, tip_w / 2.0),
                (taper_start, body_w / 2.0),
                (0.0, body_w / 2.0),
            ]
        )
        .close()
        .extrude(strap_t)
    )
    # The XZ sketch lays the strap in the X-Z plane and extrudes along +Y; we
    # actually want length along +Y and thickness along +X. Rebuild on YZ:
    strap = (
        cq.Workplane("YZ")
        .polyline(
            [
                (0.0, -body_w / 2.0),
                (taper_start, -body_w / 2.0),
                (spade_mid, -tip_w / 2.0),
                (length, 0.0),
                (spade_mid, tip_w / 2.0),
                (taper_start, body_w / 2.0),
                (0.0, body_w / 2.0),
            ]
        )
        .close()
        .extrude(strap_t)
    )
    return mesh_from_cadquery(strap, name, assets=assets), length


def _emit_bracing(leaf, r: ResolvedPlankRingDoorConfig, mats, *, assets) -> tuple[float, float]:
    z0 = r.leaf_z0
    leaf_h = r.door_h
    ledge_cx_x = _ledge_cx_x(r)
    bottom_z = z0 + 0.20
    top_z = z0 + leaf_h - 0.20

    if r.bracing == "horizontal_ledges":
        strap_y0 = 0.05
        strap_w = r.door_w - strap_y0
        strap_cy = strap_y0 + strap_w / 2.0
        for tag, cz in (("bottom", bottom_z), ("top", top_z)):
            leaf.visual(
                Box((_LEDGE_T, strap_w, _LEDGE_W)),
                origin=Origin(xyz=(ledge_cx_x, strap_cy, cz)),
                material=mats["iron"],
                name=f"ledge_{tag}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
            )
            _emit_hinge_knuckle(leaf, r, mats, tag=tag, cz=cz)

    elif r.bracing == "strap_hinge_face":
        strap_mesh_b, _ = _spade_strap_mesh(r, "strap_bottom", assets)
        strap_mesh_t, _ = _spade_strap_mesh(r, "strap_top", assets)
        for tag, cz, mesh in (("bottom", bottom_z, strap_mesh_b), ("top", top_z, strap_mesh_t)):
            leaf.visual(
                mesh,
                origin=Origin(xyz=(ledge_cx_x, 0.0, cz)),
                material=mats["iron"],
                name=f"strap_{tag}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
            )
            _emit_hinge_knuckle(leaf, r, mats, tag=tag, cz=cz)

    elif r.bracing == "z_brace_ledged":
        strap_y0 = 0.05
        strap_w = r.door_w - strap_y0
        strap_cy = strap_y0 + strap_w / 2.0
        for tag, cz in (("bottom", bottom_z), ("top", top_z)):
            leaf.visual(
                Box((_LEDGE_T, strap_w, _LEDGE_W)),
                origin=Origin(xyz=(ledge_cx_x, strap_cy, cz)),
                material=mats["iron"],
                name=f"ledge_{tag}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
            )
            _emit_hinge_knuckle(leaf, r, mats, tag=tag, cz=cz)
        # Diagonal brace from bottom-hinge to top-latch corner.
        dz = (top_z - _LEDGE_W / 2.0) - (bottom_z + _LEDGE_W / 2.0)
        seg_dy = strap_w - 0.04
        brace_len = math.sqrt(seg_dy * seg_dy + dz * dz)
        brace_angle = math.atan2(dz, seg_dy)
        brace_cy = strap_y0 + seg_dy / 2.0
        brace_cz = (bottom_z + top_z) / 2.0
        leaf.visual(
            Box((_LEDGE_T, brace_len, 0.070)),
            origin=Origin(xyz=(ledge_cx_x, brace_cy, brace_cz), rpy=(brace_angle, 0.0, 0.0)),
            material=mats["iron"],
            name="diagonal_brace", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
        )

    else:  # framed_and_braced
        stile_cx_x = _plank_front_x(r) + _STILE_T / 2.0
        back_cz = z0 + leaf_h / 2.0
        leaf.visual(
            Box((_STILE_T, _STILE_W, leaf_h)),
            origin=Origin(xyz=(stile_cx_x, _STILE_W / 2.0, back_cz)),
            material=mats["iron"],
            name="stile_hinge", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
        )
        leaf.visual(
            Box((_STILE_T, _STILE_W, leaf_h)),
            origin=Origin(xyz=(stile_cx_x, r.door_w - _STILE_W / 2.0, back_cz)),
            material=mats["iron"],
            name="stile_free", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
        )
        ledge_span_y = r.door_w - 2.0 * _STILE_W
        ledge_cy = _STILE_W + ledge_span_y / 2.0
        for i, cz in enumerate((bottom_z, top_z)):
            leaf.visual(
                Box((_LEDGE_T, ledge_span_y, _LEDGE_W)),
                origin=Origin(xyz=(ledge_cx_x, ledge_cy, cz)),
                material=mats["iron"],
                name=f"ledge_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
            )
        for tag, cz in (("bottom", bottom_z), ("top", top_z)):
            _emit_hinge_knuckle(leaf, r, mats, tag=tag, cz=cz)

    return bottom_z, top_z


# ---------------------------------------------------------------------------
# Slot E: clavos field. Inline visuals on the leaf (Rule 1, no joint).
# ---------------------------------------------------------------------------
def _clavo_stud_mesh(name: str, assets):
    """Domed clavo: a short shank + a hemisphere dome. Source: studgrid
    _make_clavo_stud L289-309. Authored proud along +X."""
    r = _CLAVO_R
    shank = (
        cq.Workplane("YZ")
        .circle(r * 0.7)
        .extrude(0.003)
        .translate((-0.003, 0.0, 0.0))
    )
    dome = cq.Workplane("XY").sphere(r).translate((0.0, 0.0, 0.0))
    # Keep the upper (+X) hemisphere by cutting below x=0.
    cut = cq.Workplane("XY").box(0.04, 0.04, 0.04).translate((-0.02, 0.0, 0.0))
    dome = dome.cut(cut)
    stud = shank.union(dome)
    return mesh_from_cadquery(stud, name, assets=assets)


def _emit_clavos(leaf, r: ResolvedPlankRingDoorConfig, mats, *, assets, strap_length: float) -> None:
    if r.clavos_field == "no_clavos":
        return
    stud_face_x = _plank_front_x(r)
    z0 = r.leaf_z0
    leaf_h = r.door_h

    if r.clavos_field == "clavos_grid":
        rows = r.clavos_rows
        cols = min(r.clavos_cols, max(2, r.plank_count))
        stud_y_lo = _STUD_Y_MARGIN
        stud_y_hi = r.door_w - _STUD_Y_MARGIN
        stud_z_lo = z0 + _STUD_Z_MARGIN
        stud_z_hi = z0 + leaf_h - _STUD_Z_MARGIN
        dy = (stud_y_hi - stud_y_lo) / max(cols - 1, 1)
        dz = (stud_z_hi - stud_z_lo) / max(rows - 1, 1)
        mesh = _clavo_stud_mesh("clavo_stud", assets)
        for row in range(rows):
            sz = stud_z_lo + row * dz
            for col in range(cols):
                sy = stud_y_lo + (col * dy if cols > 1 else (stud_y_lo + stud_y_hi) / 2.0 - stud_y_lo)
                leaf.visual(
                    mesh,
                    origin=Origin(xyz=(stud_face_x, sy, sz)),
                    material=mats["iron"],
                    name=f"stud_{row}_{col}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
                )

    else:  # strap_studs_row (only valid with strap_hinge_face)
        k = r.studs_per_strap
        bottom_z = z0 + 0.20
        top_z = z0 + leaf_h - 0.20
        stud_y_start = 0.08
        stud_y_end = strap_length - 0.15
        spacing = (stud_y_end - stud_y_start) / max(k - 1, 1)
        # Strap solid spans X in [ledge_cx_x, ledge_cx_x + _LEDGE_T]; the bolt-head
        # studs are riveted THROUGH the strap, so the shank center sits at the
        # strap mid-thickness and the cylinder length runs from well inside the
        # strap to proud of its front face (guaranteed solid overlap = no island).
        strap_back_x = _ledge_cx_x(r)
        stud_len = _LEDGE_T + _STRAP_STUD_H
        stud_cx_x = strap_back_x + _LEDGE_T / 2.0 + _STRAP_STUD_H / 2.0
        for tag, cz in (("bottom", bottom_z), ("top", top_z)):
            for i in range(k):
                sy = stud_y_start + i * spacing
                leaf.visual(
                    Cylinder(radius=_STRAP_STUD_R, length=stud_len),
                    origin=Origin(
                        xyz=(stud_cx_x, sy, cz),
                        rpy=(0.0, math.pi / 2.0, 0.0),
                    ),
                    material=mats["iron"],
                    name=f"stud_{tag}_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
                )


# ---------------------------------------------------------------------------
# Slot D: ring hardware (escutcheon + boss inline on leaf), and the ring part.
# Returns (boss_pivot_x, hw_cy, boss_pivot_z) for the ring joint.
# ---------------------------------------------------------------------------
def _emit_ring_hardware(leaf, r: ResolvedPlankRingDoorConfig, mats, *, assets):
    plate_x = _plank_front_x(r)
    hw_cy = r.door_w - 0.20
    hw_cz = r.leaf_z0 + 0.98
    boss_z_off = _PLATE_SIZE / 2.0 - 0.020

    if r.ring_hardware in ("ring_on_square_plate", "knocker_ring_on_boss"):
        # Both share a square iron backplate. The knocker adds a strike_boss
        # target below the pivot (handled after the boss is placed).
        leaf.visual(
            Box((_PLATE_T, _PLATE_SIZE, _PLATE_SIZE)),
            origin=Origin(xyz=(plate_x + _PLATE_T / 2.0, hw_cy, hw_cz)),
            material=mats["iron"],
            name="ring_backplate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
        )
    else:  # ring_on_star_plate: quatrefoil mesh + 4 rivets + collar
        quad = None
        for dy, dz in ((0.0, _QUATREFOIL_D), (0.0, -_QUATREFOIL_D), (_QUATREFOIL_D, 0.0), (-_QUATREFOIL_D, 0.0)):
            lobe = (
                cq.Workplane("YZ")
                .circle(_QUATREFOIL_R)
                .extrude(_PLATE_T)
                .translate((0.0, dy, dz))
            )
            quad = lobe if quad is None else quad.union(lobe)
        quad = quad.translate((plate_x, hw_cy, hw_cz))
        leaf.visual(
            mesh_from_cadquery(quad, "ring_escutcheon", assets=assets),
            material=mats["iron"],
            name="ring_escutcheon", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
        )
        # Four rivets at the lobe tips.
        tip = _QUATREFOIL_D + _QUATREFOIL_R - _RIVET_R - 0.002
        for i, (dy, dz) in enumerate(((0.0, tip), (0.0, -tip), (tip, 0.0), (-tip, 0.0))):
            leaf.visual(
                Cylinder(radius=_RIVET_R, length=0.005),
                origin=Origin(
                    xyz=(plate_x + _PLATE_T + 0.0015, hw_cy + dy, hw_cz + dz),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                material=mats["iron"],
                name=f"escutcheon_rivet_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
            )
        # Boss collar (annulus) around the boss base.
        collar = (
            cq.Workplane("YZ")
            .circle(0.016)
            .circle(_BOSS_R + 0.002)
            .extrude(0.003)
            .translate((plate_x + _PLATE_T, hw_cy, hw_cz + boss_z_off))
        )
        leaf.visual(
            mesh_from_cadquery(collar, "boss_collar", assets=assets),
            material=mats["iron"],
            name="boss_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
        )

    # Forward boss/stud the ring hangs from (common to all escutcheons).
    boss_x = plate_x + _PLATE_T + _BOSS_LEN / 2.0
    leaf.visual(
        Cylinder(radius=_BOSS_R, length=_BOSS_LEN),
        origin=Origin(
            xyz=(boss_x, hw_cy, hw_cz + boss_z_off),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["iron"],
        name="ring_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
    )

    boss_pivot_x = plate_x + _PLATE_T + _BOSS_LEN / 2.0
    boss_pivot_z = hw_cz + boss_z_off

    # Knocker: raised iron strike target on the plank face below the pivot. The
    # ring swings DOWN (negative q) to strike it. Aligned with the ring's bottom
    # at rest: strike_z = pivot_z - 2*ring_out_r + ring_tube_r (source S14).
    if r.is_knocker:
        strike_x = plate_x + _STRIKE_BOSS_H / 2.0
        strike_z = boss_pivot_z - 2.0 * r.ring_out_r + r.ring_tube_r
        leaf.visual(
            Cylinder(radius=_STRIKE_BOSS_R, length=_STRIKE_BOSS_H),
            origin=Origin(
                xyz=(strike_x, hw_cy, strike_z),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["iron"],
            name="strike_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
        )

    return boss_pivot_x, hw_cy, boss_pivot_z


def _build_ring_pull(model: ArticulatedObject, r: ResolvedPlankRingDoorConfig, mats, *, assets):
    """The iron pull ring as its own rotatable part. Pivot (boss line) at local
    origin; ring hangs below along -Z so its TOP tube wraps the boss."""
    ring_part = model.part("ring_pull")
    ring_center_r = r.ring_out_r - r.ring_tube_r
    ring = (
        cq.Workplane("XY")
        .moveTo(ring_center_r, 0.0)
        .circle(r.ring_tube_r)
        .revolve(360.0, (0, 0, 0), (0, 1, 0))
    )
    ring_part.visual(
        mesh_from_cadquery(ring, "ring", assets=assets),
        origin=Origin(xyz=(0.0, 0.0, -ring_center_r), rpy=(0.0, 0.0, -math.pi / 2.0)),
        material=mats["iron"],
        name="ring", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
    )
    ring_part.inertial = Inertial.from_geometry(
        Box((0.02, 2.0 * r.ring_out_r, 2.0 * r.ring_out_r)),
        mass=0.4,
        origin=Origin(xyz=(0.0, 0.0, -ring_center_r)),
    )
    return ring_part


# ---------------------------------------------------------------------------
# Optional slide bolt (PRISMATIC). Keepers inline on leaf, rod a separate part.
# ---------------------------------------------------------------------------
def _emit_bolt_keepers(leaf, r: ResolvedPlankRingDoorConfig, mats, *, bolt_cy: float, bolt_cz: float):
    plate_x = _plank_front_x(r)
    rod_x = plate_x + _BOLT_ROD_R + 0.006
    for i, dy in enumerate((-_KEEPER_SPACING / 2.0, _KEEPER_SPACING / 2.0)):
        # Base tab on the leaf face.
        leaf.visual(
            Box((0.010, 0.022, 0.030)),
            origin=Origin(xyz=(plate_x + 0.005, bolt_cy + dy, bolt_cz)),
            material=mats["iron"],
            name=f"bolt_keeper_base_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
        )
        # Loop (tube) around the rod path, bore axis along Y. Authored on the YZ
        # plane so the annulus faces +Y and extrudes a short run along +Y.
        loop = (
            cq.Workplane("XZ")
            .center(rod_x, bolt_cz)
            .circle(_BOLT_ROD_R + 0.006)
            .circle(_BOLT_ROD_R + 0.002)
            .extrude(0.016)
            .translate((0.0, bolt_cy + dy - 0.008, 0.0))
        )
        leaf.visual(
            mesh_from_cadquery(loop, f"bolt_keeper_loop_{i}"),
            material=mats["iron"],
            name=f"bolt_keeper_loop_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
        )
    return rod_x


def _build_bolt_rod(model: ArticulatedObject, r: ResolvedPlankRingDoorConfig, mats, *, rod_x: float, bolt_cz: float):
    bolt = model.part("door_bolt")
    # Rod authored along Y as a Cylinder primitive (long axis +Y via rpy=+X 90deg),
    # centered at the part-local origin spanning +/- LEN/2. The prismatic joint
    # origin sits at the inner keeper; positive q throws the rod toward +Y.
    bolt.visual(
        Cylinder(radius=_BOLT_ROD_R, length=_BOLT_ROD_LEN),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["iron"],
        name="bolt_rod", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
    )
    # Grip knob (sphere) on the -Y (retract) end so it never hits the throw keeper.
    bolt.visual(
        Sphere(radius=0.016),
        origin=Origin(xyz=(0.0, -_BOLT_ROD_LEN / 2.0 - 0.006, 0.0)),
        material=mats["iron"],
        name="bolt_knob", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
    )
    bolt.inertial = Inertial.from_geometry(
        Box((0.03, _BOLT_ROD_LEN, 0.03)),
        mass=0.3,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    return bolt


# ---------------------------------------------------------------------------
# Root: stone surround. Two jambs + lintel + (arched|flat) head + stoop + iron
# jamb pintles whose heights match the leaf hinge barrels.
# ---------------------------------------------------------------------------
def _build_stone_surround(
    model: ArticulatedObject,
    r: ResolvedPlankRingDoorConfig,
    mats,
    *,
    barrel_zs: tuple[float, float],
    assets,
):
    surround = model.part("stone_surround")
    opening_w = r.door_w + 0.02
    # Surround is authored in WORLD z; the leaf bottom sits at leaf_world_z0.
    opening_h = r.leaf_world_z0 + r.door_h + 0.05
    half_open = opening_w / 2.0
    jamb_center_y = half_open + _JAMB_W / 2.0
    wall_top = opening_h + _HEADER_H

    # Two side jambs.
    for sign in (-1.0, 1.0):
        side = "pos" if sign > 0 else "neg"
        surround.visual(
            Box((_JAMB_D, _JAMB_W, wall_top)),
            origin=Origin(xyz=(0.0, sign * jamb_center_y, wall_top / 2.0)),
            material=mats["stone"],
            name=f"jamb_{side}", material_class_id="stone.masonry_wall",
        )
        # Rough block coursing proud of each jamb front.
        course_x = _JAMB_D / 2.0 - 0.012
        n_courses = 6
        course_h = (wall_top - 0.10) / n_courses
        for c in range(n_courses):
            cz = 0.10 + course_h / 2.0 + c * course_h
            mat = mats["stone_dark"] if (c + (1 if sign > 0 else 0)) % 2 == 0 else mats["stone"]
            surround.visual(
                Box((0.030, _JAMB_W - 0.030, course_h - 0.012)),
                origin=Origin(xyz=(course_x, sign * jamb_center_y, cz)),
                material=mat,
                name=f"course_{side}_{c}", material_class_id="stone.masonry_wall",
            )

    # Header / lintel spanning the opening.
    header_span_y = opening_w + 2.0 * _JAMB_W
    surround.visual(
        Box((_JAMB_D, header_span_y, _HEADER_H)),
        origin=Origin(xyz=(0.0, 0.0, opening_h + _HEADER_H / 2.0)),
        material=mats["stone"],
        name="header_lintel", material_class_id="stone.masonry_wall",
    )
    # Voussoir-like coursing blocks proud of the header front.
    head_course_x = _JAMB_D / 2.0 - 0.012
    for k, dy in enumerate((-0.30, 0.0, 0.30)):
        mat = mats["stone_dark"] if k % 2 == 1 else mats["stone"]
        surround.visual(
            Box((0.030, 0.26, _HEADER_H - 0.04)),
            origin=Origin(xyz=(head_course_x, dy, opening_h + _HEADER_H / 2.0)),
            material=mat,
            name=f"head_course_{k}", material_class_id="stone.masonry_wall",
        )

    if r.surround_style == "arched_surround":
        # Half-disc arched head sitting on the lintel, soffit clears the arched leaf.
        arch_r = header_span_y / 2.0
        arch = (
            cq.Workplane("XY")
            .moveTo(-arch_r, 0.0)
            .threePointArc((0.0, arch_r), (arch_r, 0.0))
            .lineTo(-arch_r, 0.0)
            .close()
            .extrude(0.060)
        )
        surround.visual(
            mesh_from_cadquery(arch, "arched_head", assets=assets),
            origin=Origin(
                xyz=(_JAMB_D / 2.0 - 0.030, 0.0, opening_h + _HEADER_H),
                rpy=(math.pi / 2.0, 0.0, math.pi / 2.0),
            ),
            material=mats["stone"],
            name="arched_head", material_class_id="stone.masonry_wall",
        )
        # Keystone wedge.
        keystone = (
            cq.Workplane("YZ")
            .polyline([(-0.060, -0.105), (0.060, -0.105), (0.085, 0.105), (-0.085, 0.105)])
            .close()
            .extrude(0.045)
        )
        surround.visual(
            mesh_from_cadquery(keystone, "keystone", assets=assets),
            origin=Origin(xyz=(_JAMB_D / 2.0 - 0.040, 0.0, opening_h + _HEADER_H + 0.11)),
            material=mats["stone_dark"],
            name="keystone_block", material_class_id="stone.masonry_wall",
        )

    # Stone stoop (upper landing + lower step).
    step_span_y = opening_w + 2.0 * _JAMB_W
    landing_run = _STEP_RUN * 0.60
    surround.visual(
        Box((_JAMB_D + landing_run, step_span_y, _STEP_H)),
        origin=Origin(xyz=(landing_run / 2.0, 0.0, _STEP_H / 2.0)),
        material=mats["stone_step"],
        name="stone_step", material_class_id="stone.floor_tile",
    )
    lower_front_x = _JAMB_D / 2.0 + landing_run
    surround.visual(
        Box((_STEP_RUN, step_span_y - 0.06, _LOWER_STEP_H)),
        origin=Origin(xyz=(lower_front_x + _STEP_RUN / 2.0, 0.0, _LOWER_STEP_H / 2.0)),
        material=mats["stone_step"],
        name="stone_step_lower", material_class_id="stone.floor_tile",
    )

    # Iron pintle pins driven into the hinge (-Y) jamb at the barrel heights.
    jamb_inner = -half_open
    pin_len = 0.034
    pin_y = jamb_inner - 0.020
    barrel_local_x = _plank_front_x(r) + _LEDGE_T / 2.0
    pin_x = _WALL_T / 2.0 - _REVEAL - r.door_t + barrel_local_x
    for tag, cz in (("bottom", barrel_zs[0]), ("top", barrel_zs[1])):
        surround.visual(
            Cylinder(radius=0.008, length=pin_len),
            origin=Origin(xyz=(pin_x, pin_y, cz), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["iron"],
            name=f"jamb_pintle_{tag}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_oak_black_iron", "weathered_grey_rust", "walnut_pewter", "bleached_oak_blacksmith", "redwood_castiron"} else "metal.bronze_cast"),
        )

    surround.inertial = Inertial.from_geometry(
        Box((_JAMB_D, header_span_y, wall_top)),
        mass=40.0,
        origin=Origin(xyz=(0.0, 0.0, wall_top / 2.0)),
    )
    return surround


# ===========================================================================
# Build
# ===========================================================================
def build_plank_ring_door(
    config: PlankRingDoorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"prd_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in _palette_rgba(r.palette_style).items()
    }

    # --- Door leaf (authored in the hinge-edge local frame) ---
    leaf = model.part("door_leaf")
    _emit_leaf_body(leaf, r, mats, assets=assets)
    bottom_z, top_z = _emit_bracing(leaf, r, mats, assets=assets)
    strap_length = r.door_w - 0.06
    _emit_clavos(leaf, r, mats, assets=assets, strap_length=strap_length)
    boss_pivot_x, hw_cy, boss_pivot_z = _emit_ring_hardware(leaf, r, mats, assets=assets)
    leaf.inertial = Inertial.from_geometry(
        Box((r.door_t, r.door_w, r.door_h)),
        mass=22.0,
        origin=Origin(xyz=(0.0, r.door_w / 2.0, r.leaf_z0 + r.door_h / 2.0)),
    )

    # Optional slide bolt keepers (inline) + rod (separate part).
    bolt_cy = r.door_w - 0.24
    bolt_cz = r.leaf_z0 + r.door_h * 0.40
    rod_x = None
    if r.slide_bolt == "present":
        rod_x = _emit_bolt_keepers(leaf, r, mats, bolt_cy=bolt_cy, bolt_cz=bolt_cz)

    # --- Stone surround (root, world z). Pintle heights = leaf world bottom +
    # the leaf-local barrel z (so the world pins line up with the leaf barrels
    # once the hinge joint lifts the leaf to leaf_world_z0). ---
    world_barrel_zs = (r.leaf_world_z0 + bottom_z, r.leaf_world_z0 + top_z)
    surround = _build_stone_surround(model, r, mats, barrel_zs=world_barrel_zs, assets=assets)

    # --- Ring pull part ---
    _build_ring_pull(model, r, mats, assets=assets)

    # --- Optional bolt rod part ---
    if r.slide_bolt == "present":
        _build_bolt_rod(model, r, mats, rod_x=rod_x, bolt_cz=bolt_cz)

    # --- Articulation: vertical (Z) hinge at the -Y jamb ---
    opening_w = r.door_w + 0.02
    half_open = opening_w / 2.0
    hinge_y = -half_open + 0.01
    hinge_x = _WALL_T / 2.0 - _REVEAL - r.door_t
    # The leaf is authored in its own frame with local bottom at z=0, so the
    # hinge joint origin (which the child frame origin coincides with) sits at
    # the world leaf bottom. This keeps the origin on real leaf geometry (the
    # leaf bottom edge), satisfying the flat 15mm articulation-origin baseline.
    hinge_z = r.leaf_world_z0
    model.articulation(
        "surround_to_leaf",
        ArticulationType.REVOLUTE,
        parent=surround,
        child=leaf,
        origin=Origin(xyz=(hinge_x, hinge_y, hinge_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=2.0, lower=0.0, upper=r.hinge_upper),
    )

    # --- Articulation: ring pivots on the boss (horizontal Y axis) ---
    # Ring joint range: square/star plates only lift (lower=0); the knocker
    # resolves a bidirectional range (lower=-1.0) so negative q swings the ring
    # down to strike the strike_boss.
    model.articulation(
        "leaf_to_ring",
        ArticulationType.REVOLUTE,
        parent=leaf,
        child="ring_pull",
        origin=Origin(xyz=(boss_pivot_x, hw_cy, boss_pivot_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=3.0, velocity=2.0, lower=r.ring_lower, upper=r.ring_upper
        ),
    )

    # --- Optional slide bolt PRISMATIC (leaf-local +Y, through the keepers) ---
    if r.slide_bolt == "present":
        model.articulation(
            "leaf_to_bolt",
            ArticulationType.PRISMATIC,
            parent=leaf,
            child="door_bolt",
            origin=Origin(xyz=(rod_x, bolt_cy - _KEEPER_SPACING / 2.0, bolt_cz)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=10.0, velocity=0.2, lower=0.0, upper=_BOLT_TRAVEL),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_plank_ring_door(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_plank_ring_door(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_plank_ring_door_tests(
    object_model: ArticulatedObject,
    config: PlankRingDoorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    surround = object_model.get_part("stone_surround")
    leaf = object_model.get_part("door_leaf")
    ring = object_model.get_part("ring_pull")

    # The plank leaf swings open inside the rough stone surround; through its full
    # (required-wide) opening arc the planks / hinge stile graze the jamb and the
    # flanking stone courses. Treat that leaf<->surround interface as intentional.
    ctx.allow_overlap(
        leaf, surround,
        reason="Plank leaf swings open within the stone surround, grazing the jamb and flanking courses.",
    )
    # The ring pull swings on its boss and rests against / knocks the door face.
    ctx.allow_overlap(
        leaf, ring,
        reason="Ring pull swings on its boss against the door face and backplate.",
    )

    # ---- Captured-pin / ring-on-boss / slide allowances (element-scoped). ----
    for tag in ("bottom", "top"):
        ctx.allow_overlap(
            leaf, surround,
            elem_a=f"hinge_barrel_{tag}", elem_b=f"jamb_pintle_{tag}",
            reason=f"{tag} hinge barrel wraps the iron jamb pintle (captured pin).",
        )
        ctx.allow_overlap(
            leaf, surround,
            elem_a=f"hinge_barrel_{tag}", elem_b="jamb_neg",
            reason=f"{tag} hinge barrel seats against the hinge jamb stone.",
        )
    # Ring captured on its boss.
    ring_boss_elem = "ring_boss"
    ctx.allow_overlap(
        ring, leaf,
        elem_a="ring", elem_b=ring_boss_elem,
        reason="Pull ring is hung on and captured by the iron boss (ring tube wraps boss).",
    )
    if r.ring_hardware == "ring_on_star_plate":
        ctx.allow_overlap(
            ring, leaf,
            elem_a="ring", elem_b="boss_collar",
            reason="Ring tube straddles the boss collar at the escutcheon.",
        )
    if r.is_knocker:
        # Knocker ring rests against the strike boss at q=0 (the functional
        # contact of the knocker mechanism); a small overlap keeps it engaged.
        ctx.allow_overlap(
            ring, leaf,
            elem_a="ring", elem_b="strike_boss",
            reason="Knocker ring rests against the strike boss at rest (knocker contact).",
        )
    # Slide bolt captured in keepers.
    if r.slide_bolt == "present":
        bolt = object_model.get_part("door_bolt")
        for i in range(2):
            ctx.allow_overlap(
                bolt, leaf,
                elem_a="bolt_rod", elem_b=f"bolt_keeper_loop_{i}",
                reason=f"Slide-bolt rod passes through keeper loop {i} (captured slide).",
            )
    # Pintle driven into the jamb stone (within surround).
    for tag in ("bottom", "top"):
        ctx.allow_overlap(
            surround, surround,
            elem_a=f"jamb_pintle_{tag}", elem_b="jamb_neg",
            reason="Iron pintle is driven into the hinge jamb masonry.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity: surround + plank leaf + bracing + ring (two REVOLUTE). ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "stone_surround + door_leaf + ring_pull parts present",
        {"stone_surround", "door_leaf", "ring_pull"} <= part_names,
        details=str(sorted(part_names)),
    )

    # Plank field topology.
    if r.is_box_per_plank:
        plank_visuals = [v.name for v in leaf.visuals if v.name.startswith("plank_")]
        ctx.check(
            "N vertical planks inlined (Rule 1)",
            len(plank_visuals) == r.plank_count,
            details=f"planks={sorted(plank_visuals)} expected N={r.plank_count}",
        )
    else:
        ctx.check(
            "groove-cut single leaf box present",
            leaf.get_visual("leaf_planks") is not None,
            details="leaf_planks single-box mesh",
        )

    # Knocker hardware: a strike boss must be present for the ring to hit.
    if r.is_knocker:
        ctx.check(
            "knocker strike_boss present on the leaf",
            leaf.get_visual("strike_boss") is not None,
            details="strike_boss target for the knocker ring",
        )

    # ---- Hinge joint: vertical Z axis, realistic range. ----
    hinge = object_model.get_articulation("surround_to_leaf")
    ax = hinge.axis
    ctx.check(
        "leaf hinge axis is vertical (Z)",
        abs(ax[2]) > 0.99 and abs(ax[0]) < 1e-6 and abs(ax[1]) < 1e-6,
        details=f"axis={tuple(ax)}",
    )
    lims = hinge.motion_limits
    ctx.check(
        "leaf hinge has a realistic opening range",
        lims is not None and abs(lims.lower) < 1e-6 and 1.2 <= lims.upper <= 2.4,
        details=f"limits=({lims.lower if lims else None},{lims.upper if lims else None})",
    )

    # ---- Ring joint: horizontal Y axis, sensible lift range. ----
    ring_joint = object_model.get_articulation("leaf_to_ring")
    rax = ring_joint.axis
    ctx.check(
        "ring joint axis is horizontal (Y, parallel to door face)",
        abs(rax[1]) > 0.99 and abs(rax[0]) < 1e-6 and abs(rax[2]) < 1e-6,
        details=f"ring axis={tuple(rax)}",
    )
    rlims = ring_joint.motion_limits
    if r.is_knocker:
        # Knocker: bidirectional range (negative q strikes the boss, positive q lifts).
        ctx.check(
            "knocker ring joint allows a downward strike and an upward lift",
            rlims is not None
            and rlims.lower is not None
            and rlims.upper is not None
            and rlims.lower < -0.5
            and 0.6 <= rlims.upper <= 1.4,
            details=f"ring limits=({rlims.lower if rlims else None},{rlims.upper if rlims else None})",
        )
    else:
        ctx.check(
            "ring joint has a sensible lift range",
            rlims is not None and abs(rlims.lower) < 1e-6 and 0.6 <= rlims.upper <= 1.4,
            details=f"ring limits=({rlims.lower if rlims else None},{rlims.upper if rlims else None})",
        )

    # Slide bolt joint topology (if present).
    if r.slide_bolt == "present":
        bj = object_model.get_articulation("leaf_to_bolt")
        ctx.check(
            "slide bolt is PRISMATIC (horizontal across leaf)",
            bj.articulation_type == ArticulationType.PRISMATIC and abs(bj.axis[1]) > 0.99,
            details=f"type={bj.articulation_type} axis={tuple(bj.axis)}",
        )

    # ---- Grounding: surround on the ground; leaf upright above it. ----
    surround_aabb = ctx.part_world_aabb(surround)
    leaf_aabb = ctx.part_world_aabb(leaf)
    if surround_aabb is not None:
        ctx.check(
            "stone surround sits on the ground",
            abs(surround_aabb[0][2]) < 1e-6,
            details=f"surround z-min={surround_aabb[0][2]:.4f}",
        )
    if leaf_aabb is not None:
        ctx.check(
            "leaf is upright and tall, above the ground",
            leaf_aabb[0][2] > 0.0 and (leaf_aabb[1][2] - leaf_aabb[0][2]) > 1.6,
            details=f"leaf z=({leaf_aabb[0][2]:.3f},{leaf_aabb[1][2]:.3f})",
        )

    # ---- Leaf bottom clears the stoop (vertical hinge => never clips). ----
    step_aabb = ctx.part_element_world_aabb(surround, elem="stone_step")
    if leaf_aabb is not None and step_aabb is not None:
        ctx.check(
            "door bottom clears the stone stoop",
            leaf_aabb[0][2] > step_aabb[1][2],
            details=f"leaf z-min={leaf_aabb[0][2]:.3f}, stoop z-max={step_aabb[1][2]:.3f}",
        )

    # ---- Closed leaf body fits between the jambs. ----
    inner_elem = "leaf_planks" if not r.is_box_per_plank else "backing_board"
    ctx.expect_within(
        leaf, surround,
        axes="y",
        inner_elem=inner_elem,
        margin=0.02,
        name="closed leaf body fits between the jambs",
    )

    # ---- Captured-pin contact proof. ----
    for tag in ("bottom", "top"):
        ctx.expect_contact(
            leaf, surround,
            elem_a=f"hinge_barrel_{tag}", elem_b=f"jamb_pintle_{tag}",
            name=f"{tag} hinge barrel contacts its jamb pintle",
        )

    # ---- Ring stands proud of the plank face. ----
    ring_aabb = ctx.part_element_world_aabb(ring, elem="ring")
    plank_ref = "plank_0" if r.is_box_per_plank else "leaf_planks"
    plank_aabb = ctx.part_element_world_aabb(leaf, elem=plank_ref)
    if ring_aabb is not None and plank_aabb is not None:
        ctx.check(
            "ring pull stands proud of the plank face (+X)",
            ring_aabb[1][0] > plank_aabb[1][0],
            details=f"ring xmax={ring_aabb[1][0]:.3f}, plank xmax={plank_aabb[1][0]:.3f}",
        )

    # ---- HERO: hinge opens the free edge forward (+X). ----
    closed = ctx.part_world_aabb(leaf)
    with ctx.pose({hinge: min(1.4, r.hinge_upper)}):
        opened = ctx.part_world_aabb(leaf)
    if closed is not None and opened is not None:
        ctx.check(
            "open pose swings the free edge forward (+X)",
            opened[1][0] > closed[1][0] + 0.2,
            details=f"closed xmax={closed[1][0]:.3f}, open xmax={opened[1][0]:.3f}",
        )

    # ---- HERO: ring rotates out off the door face when lifted. ----
    closed_ring = ctx.part_element_world_aabb(ring, elem="ring")
    with ctx.pose({ring_joint: min(1.0, r.ring_upper)}):
        lifted_ring = ctx.part_element_world_aabb(ring, elem="ring")
    if closed_ring is not None and lifted_ring is not None:
        ctx.check(
            "lifting the ring swings its lower edge away from the door (+X)",
            lifted_ring[1][0] > closed_ring[1][0] + 0.015
            and lifted_ring[0][2] > closed_ring[0][2] + 0.008,
            details=f"closed xmax={closed_ring[1][0]:.3f} lifted xmax={lifted_ring[1][0]:.3f} "
            f"closed zmin={closed_ring[0][2]:.3f} lifted zmin={lifted_ring[0][2]:.3f}",
        )

    # ---- Slide bolt throws and stays engaged (if present). ----
    if r.slide_bolt == "present":
        bj = object_model.get_articulation("leaf_to_bolt")
        bolt = object_model.get_part("door_bolt")
        p0 = ctx.part_world_position(bolt)
        with ctx.pose({bj: _BOLT_TRAVEL}):
            p1 = ctx.part_world_position(bolt)
        if p0 is not None and p1 is not None:
            ctx.check(
                "slide bolt translates when thrown",
                abs(p1[1] - p0[1]) > 0.05,
                details=f"rest y={p0[1]:.3f} thrown y={p1[1]:.3f}",
            )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "PlankRingDoorConfig",
    "ResolvedPlankRingDoorConfig",
    "build_plank_ring_door",
    "build_seeded_plank_ring_door",
    "config_from_seed",
    "resolve_config",
    "run_plank_ring_door_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
