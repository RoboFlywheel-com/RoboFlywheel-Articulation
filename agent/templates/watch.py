# SPDX-License-Identifier: Apache-2.0

"""Wristwatch modular procedural template.

Slot graph (pattern=parallel_children, single-root `case`):

    case (Slot A, case_form)
     ├── bezel        (Slot B, bezel_style; REV/CONT about +z)
     ├── hour_hand    (Slot D dial_layout base; CONT about +z)
     ├── minute_hand  (base; CONT +z)
     ├── second_hand  (base; CONT +z)
     ├── [subdial_hand or balance_wheel] (Slot D extras; CONT +z)
     ├── crown        (M2 crown_control_count>=1; REV/CONT/PRIS about +x)
     ├── pusher_0     (M2>=2; PRIS +x)
     ├── pusher_1     (M2==3; PRIS +x)
     ├── top_strap_0..N-1   (Slot C, chain of REV hinges about +x, M1)
     └── bottom_strap_0..N-1

Structure derived from `articraft_template_authoring/specs_modular_v1/watch.md`
(5-star sources: rec_watch__watch__001..005 + rec_0611_watch_var_*). Primitive
choices intentionally stay simple (Cylinder / Box / lathe-style annular sector
meshes) so the mesh generator stays within the spec's 20 s/seed compile budget
across all sampled scales.

Palette diversity (Rule ⑥): six realistic colorways sampled per seed
(steel_blue_dive / black_ceramic_chrono / orange_dive / stainless_bracelet /
blue_dial_gold_hands / black_leather_dress). Every part.visual reads from the
resolved `mats[...]` map — no bare RGB colors in the factory.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True

TAU = math.tau

# --------------------------------------------------------------------------- #
# Slot alphabets
# --------------------------------------------------------------------------- #

CaseForm = Literal["round_dive", "stainless_round", "cushion", "square", "tonneau"]
BezelStyle = Literal[
    "dive_rotating_60",
    "smooth_polished_ring",
    "unidirectional_chrono",
    "bidirectional_gmt",
    "raised_numeral_bezel",
]
StrapTopology = Literal[
    "ribbed_rubber",
    "brushed_steel_bracelet",
    "articulated_ceramic_link",
    "orange_rubber_holed",
    "metal_bracelet_bent",
    "fabric_flat_strap",
]
DialLayout = Literal["simple_indices", "three_subdials_chrono", "open_heart_aperture"]
PaletteStyle = Literal[
    "steel_blue_dive",
    "black_ceramic_chrono",
    "orange_dive",
    "stainless_bracelet",
    "blue_dial_gold_hands",
    "black_leather_dress",
]

CASE_FORMS: tuple[CaseForm, ...] = (
    "round_dive",
    "stainless_round",
    "cushion",
    "square",
    "tonneau",
)
BEZEL_STYLES: tuple[BezelStyle, ...] = (
    "dive_rotating_60",
    "smooth_polished_ring",
    "unidirectional_chrono",
    "bidirectional_gmt",
    "raised_numeral_bezel",
)
STRAP_TOPOLOGIES: tuple[StrapTopology, ...] = (
    "ribbed_rubber",
    "brushed_steel_bracelet",
    "articulated_ceramic_link",
    "orange_rubber_holed",
    "metal_bracelet_bent",
    "fabric_flat_strap",
)
DIAL_LAYOUTS: tuple[DialLayout, ...] = (
    "simple_indices",
    "three_subdials_chrono",
    "open_heart_aperture",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "steel_blue_dive",
    "black_ceramic_chrono",
    "orange_dive",
    "stainless_bracelet",
    "blue_dial_gold_hands",
    "black_leather_dress",
)

# Bezel candidate → joint type (② diversity axis).
_BEZEL_JOINT_TYPE: dict[BezelStyle, ArticulationType] = {
    "dive_rotating_60": ArticulationType.REVOLUTE,
    "smooth_polished_ring": ArticulationType.CONTINUOUS,
    "unidirectional_chrono": ArticulationType.REVOLUTE,
    "bidirectional_gmt": ArticulationType.CONTINUOUS,
    "raised_numeral_bezel": ArticulationType.REVOLUTE,
}

# Crown joint type varies with `crown_control_count` and stylistic origin
# (② diversity axis: origin 3 uses PRISMATIC, origins 1/2/4/5 use REV/CONT).
_CROWN_JOINT_BY_STRAP: dict[StrapTopology, ArticulationType] = {
    "ribbed_rubber": ArticulationType.REVOLUTE,
    "brushed_steel_bracelet": ArticulationType.CONTINUOUS,
    "articulated_ceramic_link": ArticulationType.CONTINUOUS,
    "orange_rubber_holed": ArticulationType.PRISMATIC,
    "metal_bracelet_bent": ArticulationType.CONTINUOUS,
    "fabric_flat_strap": ArticulationType.REVOLUTE,
}

# --------------------------------------------------------------------------- #
# Palette table (⑥). Six realistic colorways covering metal/plastic/glass/enamel.
# Every part.visual downstream reads from mats[key].
# --------------------------------------------------------------------------- #

_PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "steel_blue_dive": {
        "case": (0.78, 0.78, 0.76, 1.0),
        "case_dark": (0.38, 0.38, 0.40, 1.0),
        "dial": (0.015, 0.035, 0.14, 1.0),
        "bezel_ring": (0.03, 0.12, 0.34, 1.0),
        "bezel_accent": (0.55, 0.06, 0.09, 1.0),
        "hand": (0.86, 0.88, 0.88, 1.0),
        "hand_accent": (0.94, 0.95, 0.90, 1.0),
        "marker": (0.88, 0.90, 0.78, 1.0),
        "crystal": (0.60, 0.82, 1.0, 0.32),
        "strap": (0.004, 0.004, 0.005, 1.0),
        "strap_accent": (0.72, 0.74, 0.74, 1.0),
    },
    "black_ceramic_chrono": {
        "case": (0.72, 0.70, 0.66, 1.0),
        "case_dark": (0.24, 0.24, 0.24, 1.0),
        "dial": (0.015, 0.017, 0.018, 1.0),
        "bezel_ring": (0.005, 0.005, 0.006, 1.0),
        "bezel_accent": (0.96, 0.96, 0.92, 1.0),
        "hand": (0.88, 0.84, 0.66, 1.0),
        "hand_accent": (1.0, 0.72, 0.04, 1.0),
        "marker": (0.88, 0.84, 0.66, 1.0),
        "crystal": (0.74, 0.91, 1.0, 0.24),
        "strap": (0.05, 0.05, 0.06, 1.0),
        "strap_accent": (0.30, 0.30, 0.30, 1.0),
    },
    "orange_dive": {
        "case": (0.72, 0.70, 0.66, 1.0),
        "case_dark": (0.24, 0.24, 0.24, 1.0),
        "dial": (0.015, 0.017, 0.018, 1.0),
        "bezel_ring": (0.005, 0.005, 0.006, 1.0),
        "bezel_accent": (1.0, 0.43, 0.02, 1.0),
        "hand": (1.0, 0.43, 0.02, 1.0),
        "hand_accent": (0.96, 0.96, 0.92, 1.0),
        "marker": (1.0, 0.29, 0.035, 1.0),
        "crystal": (0.74, 0.91, 1.0, 0.24),
        "strap": (1.0, 0.29, 0.035, 1.0),
        "strap_accent": (1.0, 0.43, 0.02, 1.0),
    },
    "stainless_bracelet": {
        "case": (0.76, 0.78, 0.78, 1.0),
        "case_dark": (0.10, 0.11, 0.12, 1.0),
        "dial": (0.02, 0.17, 0.34, 1.0),
        "bezel_ring": (0.01, 0.04, 0.12, 1.0),
        "bezel_accent": (0.96, 0.96, 0.92, 1.0),
        "hand": (1.0, 0.74, 0.13, 1.0),
        "hand_accent": (0.96, 0.96, 0.92, 1.0),
        "marker": (0.86, 0.94, 0.88, 1.0),
        "crystal": (0.72, 0.90, 1.0, 0.36),
        "strap": (0.55, 0.57, 0.58, 1.0),
        "strap_accent": (0.10, 0.11, 0.12, 1.0),
    },
    "blue_dial_gold_hands": {
        "case": (0.86, 0.72, 0.42, 1.0),
        "case_dark": (0.55, 0.44, 0.16, 1.0),
        "dial": (0.02, 0.15, 0.42, 1.0),
        "bezel_ring": (0.78, 0.62, 0.24, 1.0),
        "bezel_accent": (0.96, 0.90, 0.66, 1.0),
        "hand": (1.0, 0.82, 0.20, 1.0),
        "hand_accent": (0.94, 0.86, 0.44, 1.0),
        "marker": (1.0, 0.82, 0.20, 1.0),
        "crystal": (0.72, 0.90, 1.0, 0.32),
        "strap": (0.22, 0.13, 0.06, 1.0),
        "strap_accent": (0.78, 0.62, 0.24, 1.0),
    },
    "black_leather_dress": {
        "case": (0.78, 0.78, 0.76, 1.0),
        "case_dark": (0.34, 0.34, 0.34, 1.0),
        "dial": (0.94, 0.92, 0.86, 1.0),
        "bezel_ring": (0.78, 0.78, 0.76, 1.0),
        "bezel_accent": (0.34, 0.34, 0.34, 1.0),
        "hand": (0.06, 0.06, 0.08, 1.0),
        "hand_accent": (0.20, 0.20, 0.22, 1.0),
        "marker": (0.06, 0.06, 0.08, 1.0),
        "crystal": (0.72, 0.90, 1.0, 0.30),
        "strap": (0.05, 0.04, 0.04, 1.0),
        "strap_accent": (0.34, 0.32, 0.30, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Reference geometry constants (all in meters, real wristwatch scale).
# --------------------------------------------------------------------------- #

_CASE_R = 0.024  # base case outer radius (bezel inner)
_CASE_H = 0.010  # case body Z extent
_BEZEL_RING_WIDTH = 0.005  # bezel ring outer minus inner
_BEZEL_H = 0.003  # bezel Z extent (added above case top)
_DIAL_INNER_R = 0.019  # dial usable inner radius (< case_r)
_LUG_REACH = 0.006  # extra Y past case body where spring bar sits
_STRAP_LEN = 0.020  # per-link Y extent
_STRAP_W_BASE = 0.028  # first strap link width
_STRAP_H = 0.005  # strap link Z extent
_CROWN_OFFSET = 0.005  # crown center X past case rim
_CROWN_R = 0.0035  # crown radius
_PUSHER_R = 0.0025
_PUSHER_Y = 0.017  # pusher offset in Y from center
_HAND_R = 0.0011  # hand hub radius
_HAND_H = 0.0004  # hand thickness

# Z-stack for the coaxial hands.  Dial support posts must stop below the
# lowest visible face of the second hand; otherwise the dark support hardware
# reads as a column rising through the hands in low-angle renders.  Keep these
# offsets single-sourced because the hand joints and the support geometry must
# share the same vertical envelope.
_HAND_Z_HOUR = 0.0012
_HAND_Z_MINUTE = 0.0020
_HAND_Z_SECOND = 0.0028
_SUBDIAL_HAND_Z = 0.00035
_DIAL_FEATURE_H = 0.00012

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class WatchConfig:
    case_form: CaseForm | None = None
    bezel_style: BezelStyle | None = None
    strap_topology: StrapTopology | None = None
    dial_layout: DialLayout | None = None
    palette_style: PaletteStyle | None = None
    strap_link_count: int | None = None
    crown_control_count: int | None = None
    case_radius_scale: float = 1.0
    case_height_scale: float = 1.0
    bezel_height_scale: float = 1.0
    hand_length_scale: float = 1.0
    strap_link_length_scale: float = 1.0
    crown_size_scale: float = 1.0
    name: str = "watch"


@dataclass(frozen=True)
class ResolvedWatchConfig:
    case_form: CaseForm
    bezel_style: BezelStyle
    strap_topology: StrapTopology
    dial_layout: DialLayout
    palette_style: PaletteStyle
    strap_link_count: int
    crown_control_count: int
    case_outer_r: float  # base case outer radius after scale
    case_h: float
    dial_inner_r: float
    bezel_inner_r: float
    bezel_outer_r: float
    bezel_h: float
    bezel_z_bottom: float  # world z where bezel underside sits (== case top)
    hand_len_hour: float
    hand_len_minute: float
    hand_len_second: float
    strap_len: float
    strap_w_base: float
    strap_h: float
    lug_y_top: float  # world Y of top-side lug spring bar
    lug_y_bottom: float  # symmetric bottom
    crown_r: float
    crown_x: float  # world X of crown center
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _pick(v, choices):
    return v if v in choices else choices[0]


def config_from_seed(seed: int) -> WatchConfig:
    rng = random.Random(seed)
    return WatchConfig(
        case_form=rng.choice(CASE_FORMS),
        bezel_style=rng.choice(BEZEL_STYLES),
        strap_topology=rng.choice(STRAP_TOPOLOGIES),
        dial_layout=rng.choice(DIAL_LAYOUTS),
        palette_style=rng.choice(PALETTE_STYLES),
        strap_link_count=rng.randint(3, 6),
        crown_control_count=rng.randint(1, 3),
        case_radius_scale=round(rng.uniform(0.90, 1.15), 4),
        case_height_scale=round(rng.uniform(0.90, 1.12), 4),
        bezel_height_scale=round(rng.uniform(0.85, 1.15), 4),
        hand_length_scale=round(rng.uniform(0.85, 1.10), 4),
        strap_link_length_scale=round(rng.uniform(0.85, 1.15), 4),
        crown_size_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_watch_{seed}",
    )


def resolve_config(config: WatchConfig | None = None) -> ResolvedWatchConfig:
    cfg = config or WatchConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    case_form = _pick(cfg.case_form, CASE_FORMS)
    bezel_style = _pick(cfg.bezel_style, BEZEL_STYLES)
    strap_topology = _pick(cfg.strap_topology, STRAP_TOPOLOGIES)
    dial_layout = _pick(cfg.dial_layout, DIAL_LAYOUTS)

    strap_link_count = int(_clamp(cfg.strap_link_count or 5, 3, 6))
    crown_control_count = int(_clamp(cfg.crown_control_count or 1, 1, 3))

    r_scale = _clamp(cfg.case_radius_scale, 0.90, 1.15)
    h_scale = _clamp(cfg.case_height_scale, 0.90, 1.12)
    bh_scale = _clamp(cfg.bezel_height_scale, 0.85, 1.15)
    hand_scale = _clamp(cfg.hand_length_scale, 0.85, 1.10)
    strap_scale = _clamp(cfg.strap_link_length_scale, 0.85, 1.15)
    crown_scale = _clamp(cfg.crown_size_scale, 0.85, 1.15)

    case_outer_r = _CASE_R * r_scale
    case_h = _CASE_H * h_scale
    dial_inner_r = min(_DIAL_INNER_R * r_scale, case_outer_r - 0.003)
    bezel_inner_r = case_outer_r * 0.95  # sit slightly inset from case outer
    bezel_outer_r = case_outer_r + _BEZEL_RING_WIDTH * r_scale
    bezel_h = _BEZEL_H * bh_scale
    bezel_z_bottom = case_h  # top of case = bottom of bezel

    dial_reach = dial_inner_r - 0.002
    hand_len_hour = min(dial_reach * 0.55, 0.9 * dial_inner_r) * hand_scale
    hand_len_minute = min(dial_reach * 0.75, 0.95 * dial_inner_r) * hand_scale
    hand_len_second = min(dial_reach * 0.85, 0.98 * dial_inner_r) * hand_scale

    strap_len = _STRAP_LEN * strap_scale
    # Enforce inequality: chain total <= 0.100 per side. Shrink strap_len first.
    max_total = 0.100
    if strap_len * strap_link_count > max_total:
        strap_len = max(0.012, max_total / strap_link_count)
    # If still overshoot after clamping strap_len min, drop N.
    while strap_len * strap_link_count > max_total and strap_link_count > 3:
        strap_link_count -= 1

    strap_w_base = min(_STRAP_W_BASE, 2.0 * case_outer_r * 0.85)
    strap_h = _STRAP_H

    # Lug spring bar Y: just past case edge in Y direction.
    lug_y_top = case_outer_r + _LUG_REACH * r_scale
    lug_y_bottom = -lug_y_top

    crown_r = _CROWN_R * crown_scale
    # Crown flank in +X: crown center sits so stem overlaps the case flank.
    crown_x = case_outer_r + crown_r * 0.4  # partial embed

    palette = dict(_PALETTES[palette_style])

    return ResolvedWatchConfig(
        case_form=case_form,
        bezel_style=bezel_style,
        strap_topology=strap_topology,
        dial_layout=dial_layout,
        palette_style=palette_style,
        strap_link_count=strap_link_count,
        crown_control_count=crown_control_count,
        case_outer_r=case_outer_r,
        case_h=case_h,
        dial_inner_r=dial_inner_r,
        bezel_inner_r=bezel_inner_r,
        bezel_outer_r=bezel_outer_r,
        bezel_h=bezel_h,
        bezel_z_bottom=bezel_z_bottom,
        hand_len_hour=hand_len_hour,
        hand_len_minute=hand_len_minute,
        hand_len_second=hand_len_second,
        strap_len=strap_len,
        strap_w_base=strap_w_base,
        strap_h=strap_h,
        lug_y_top=lug_y_top,
        lug_y_bottom=lug_y_bottom,
        crown_r=crown_r,
        crown_x=crown_x,
        palette=palette,
        name=cfg.name or "watch",
    )


def slot_choices_for_config(
    r: ResolvedWatchConfig,
) -> list[tuple[str, str]]:
    return [
        ("case_form", r.case_form),
        ("bezel_style", r.bezel_style),
        ("strap_topology", r.strap_topology),
        ("dial_layout", r.dial_layout),
        ("strap_link_count", f"n{r.strap_link_count}"),
        ("crown_control_count", f"n{r.crown_control_count}"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Case body mesh helpers (Slot A). Each candidate emits a different Primary
# Form Family: round (revolved cylinder), stainless_round (round + integrated
# shoulder plate), cushion (rounded square via Box + corner clip), square (Box),
# tonneau (elliptical super-ellipse approximation via oriented Boxes).
# --------------------------------------------------------------------------- #


def _annular_sector(
    inner_radius: float,
    outer_radius: float,
    z0: float,
    z1: float,
    angle0: float,
    angle1: float,
    *,
    segments: int = 48,
) -> MeshGeometry:
    """Closed raised annular wedge in the local XY plane (from origin 1 L25-71)."""
    geom = MeshGeometry()
    for i in range(segments + 1):
        t = angle0 + (angle1 - angle0) * i / segments
        c = math.cos(t)
        s = math.sin(t)
        geom.add_vertex(outer_radius * c, outer_radius * s, z1)
        geom.add_vertex(inner_radius * c, inner_radius * s, z1)
        geom.add_vertex(outer_radius * c, outer_radius * s, z0)
        geom.add_vertex(inner_radius * c, inner_radius * s, z0)
    for i in range(segments):
        a = 4 * i
        b = 4 * (i + 1)
        geom.add_face(a, b, a + 1)
        geom.add_face(a + 1, b, b + 1)
        geom.add_face(a + 2, a + 3, b + 2)
        geom.add_face(a + 3, b + 3, b + 2)
        geom.add_face(a, a + 2, b)
        geom.add_face(a + 2, b + 2, b)
        geom.add_face(a + 1, b + 1, a + 3)
        geom.add_face(a + 3, b + 1, b + 3)
    # radial end walls (only visible if not full ring)
    if abs((angle1 - angle0) - TAU) > 1e-4:
        a = 0
        geom.add_face(a, a + 1, a + 2)
        geom.add_face(a + 1, a + 3, a + 2)
        b = 4 * segments
        geom.add_face(b, b + 2, b + 1)
        geom.add_face(b + 1, b + 2, b + 3)
    return geom


def _emit_case_body(case, r: ResolvedWatchConfig, mats) -> None:
    """Emit the case body visuals per Slot A candidate.

    Every candidate keeps the same interfaces (bezel-seat annulus on top,
    central arbor at (0,0), spring bars at ±lug_y, crown flank at +X), only
    the primary form family changes.
    """
    outer_r = r.case_outer_r
    case_h = r.case_h
    if r.case_form == "round_dive":
        # Volumetric Envelope Form: revolved cylinder.
        case.visual(
            Cylinder(radius=outer_r, length=case_h),
            origin=Origin(xyz=(0.0, 0.0, case_h / 2.0)),
            material=mats["case"],
            name="case_body", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
        )
    elif r.case_form == "stainless_round":
        # Round + integrated upper shoulder plate (origin 2 L200-L218).
        case.visual(
            Cylinder(radius=outer_r * 0.98, length=case_h * 0.80),
            origin=Origin(xyz=(0.0, 0.0, case_h * 0.40)),
            material=mats["case"],
            name="case_body", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
        )
        case.visual(
            Cylinder(radius=outer_r, length=case_h * 0.30),
            origin=Origin(xyz=(0.0, 0.0, case_h * 0.85)),
            material=mats["case_dark"],
            name="case_shoulder_plate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
        )
    elif r.case_form == "cushion":
        # Planar Boundary Form: rounded square (from cushion variant L21-L177).
        # Keep lobes strictly inside the case body so they never extend past
        # the case boundary into the lug/strap span.
        side = outer_r * 1.7
        case.visual(
            Box((side, side, case_h)),
            origin=Origin(xyz=(0.0, 0.0, case_h / 2.0)),
            material=mats["case"],
            name="case_body", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
        )
        # Corner-softening lobes at the four corners (inset, not on edge mids).
        # Radius chosen so the lobe rides inside the body box.
        lobe_r = side * 0.30
        corner = side * 0.5 - lobe_r * 0.60
        for i, (x, y) in enumerate(
            ((corner, corner), (-corner, corner), (-corner, -corner), (corner, -corner))
        ):
            case.visual(
                Cylinder(radius=lobe_r, length=case_h * 0.95),
                origin=Origin(xyz=(x, y, case_h * 0.475)),
                material=mats["case"],
                name=f"case_cushion_lobe_{i}", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
            )
    elif r.case_form == "square":
        # Planar Boundary Form: square.
        side = outer_r * 1.7
        case.visual(
            Box((side, side, case_h)),
            origin=Origin(xyz=(0.0, 0.0, case_h / 2.0)),
            material=mats["case"],
            name="case_body", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
        )
    else:  # tonneau
        # Planar Boundary Form: barrel / super-ellipse — long Y, short X.
        # Keep body + bulges strictly inside the ±lug_y_top span in Y so the
        # first strap link stays clear when rotated through its full range.
        case.visual(
            Box((outer_r * 1.5, outer_r * 1.8, case_h)),
            origin=Origin(xyz=(0.0, 0.0, case_h / 2.0)),
            material=mats["case"],
            name="case_body", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
        )
        # Barrel side bulges — inset so their Y_max stays below lug_y_top.
        for sy in (-1.0, 1.0):
            case.visual(
                Cylinder(radius=outer_r * 0.55, length=case_h * 0.95),
                origin=Origin(xyz=(0.0, sy * outer_r * 0.30, case_h * 0.475)),
                material=mats["case"],
                name=f"case_tonneau_bulge_{0 if sy < 0 else 1}", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
            )

    # --- Shared decorations (④ inline visuals, host-conformal). ---
    _emit_case_deco(case, r, mats)

    # --- Shared downstream-interface hardware. ---
    # Keep a slender hidden axle reaching the raised hand hubs so the hands
    # remain mechanically supported.  It is dial-coloured and narrow rather
    # than a visible black column between the dial and the three pointers.
    arbor_top = case_h + _HAND_Z_SECOND + 0.7 * _HAND_H
    arbor_len = arbor_top - case_h
    case.visual(
        Cylinder(radius=0.00028, length=arbor_len),
        origin=Origin(xyz=(0.0, 0.0, case_h + 0.5 * arbor_len)),
        material=mats["dial"],
        name="central_arbor", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "orange_dive", "stainless_bracelet", "blue_dial_gold_hands"} else "ceramic.porcelain_glazed_plain"),
    )
    # Bezel seat annulus: a thin annular ring on top of the case that visually
    # marks (and MatingContract-anchors) the bezel underside.
    seat = _annular_sector(
        max(0.0002, r.bezel_inner_r - 0.0003),
        r.bezel_outer_r * 0.98,
        case_h - 0.0004,
        case_h,
        0.0,
        TAU,
        segments=64,
    )
    case.visual(
        mesh_from_geometry(seat, "case_bezel_seat"),
        material=mats["case_dark"],
        name="case_bezel_seat", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
    )
    # Spring bars at ±Y for strap chains.
    for side, sy in (("top", r.lug_y_top), ("bottom", r.lug_y_bottom)):
        case.visual(
            Cylinder(radius=0.0011, length=min(r.strap_w_base, 2 * r.case_outer_r) * 0.95),
            origin=Origin(xyz=(0.0, sy, case_h * 0.35), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["case_dark"],
            name=f"{side}_spring_bar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
        )
        # Lug bridge (real visual for MatingContract on the strap parent side).
        case.visual(
            Box(
                (
                    min(r.strap_w_base * 1.05, r.case_outer_r * 1.7),
                    abs(sy) - r.case_outer_r * 0.7,
                    case_h * 0.7,
                )
            ),
            origin=Origin(xyz=(0.0, sy * 0.85, case_h * 0.35)),
            material=mats["case"],
            name=f"{side}_lug_bridge", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
        )
    # Crown flank pad — a long X strip whose base half embeds into case_body
    # (starts at X=outer_r*0.5, ends past the case rim) so the tip supports
    # the crown stem while the base stays welded to the case.
    flank_len_x = r.case_outer_r * 0.55
    flank_x = r.case_outer_r * 0.5 + flank_len_x / 2.0
    case.visual(
        Box((flank_len_x, r.crown_r * 2.5, r.crown_r * 2.5)),
        origin=Origin(xyz=(flank_x, 0.0, case_h * 0.45)),
        material=mats["case"],
        name="case_crown_flank", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
    )
    # Optional pusher-tube stubs for M2 controls (only visible when pushers exist,
    # but always emitting them keeps the case visuals stable across N and provides
    # real geometry for pusher MatingContract). Placed on +X flank at ±pusher_y.
    for i, py in enumerate((_PUSHER_Y * 0.35, -_PUSHER_Y * 0.35)):
        py_clamped = py * (r.case_outer_r / _CASE_R)  # scale with case
        # Pad is a long X strip whose inner half embeds inside the case body
        # (case_body is a cylinder of radius=outer_r for the round variants and
        # a box for square/cushion/tonneau — all of them contain (0,0)+X=+outer_r*0.5
        # so a pad starting at X=outer_r*0.5 and ending at X=outer_r*1.05 keeps
        # its base half fused to case_body and the tip proud of the flank).
        pad_len_x = r.case_outer_r * 0.55
        pad_x = r.case_outer_r * 0.5 + pad_len_x / 2.0
        case.visual(
            Box((pad_len_x, _PUSHER_R * 2.0, _PUSHER_R * 2.0)),
            origin=Origin(xyz=(pad_x, py_clamped, case_h * 0.45)),
            material=mats["case_dark"],
            name=f"case_pusher_pad_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
        )


def _emit_case_deco(case, r: ResolvedWatchConfig, mats) -> None:
    """Host-conformal ④ decoration: chapter ring + minute/hour ticks + dial disc.

    Every tick sits on the dial-inner-radius circle (derived from the resolved
    dial_inner_r), so the decoration wraps every case_form / scale (Rule 4).
    """
    case_h = r.case_h
    dial_r = r.dial_inner_r
    # Recessed dial disc (colored slightly to give the dial its identity).
    case.visual(
        Cylinder(radius=dial_r, length=0.0004),
        origin=Origin(xyz=(0.0, 0.0, case_h - 0.0002)),
        material=mats["dial"],
        name="dial_disc", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "orange_dive", "stainless_bracelet", "blue_dial_gold_hands"} else "ceramic.porcelain_glazed_plain"),
    )
    # Chapter ring — inline annular sector for the dial rehaut.
    chapter = _annular_sector(
        dial_r * 0.88,
        dial_r * 0.96,
        case_h,
        case_h + 0.00004,
        0.0,
        TAU,
        segments=48,
    )
    case.visual(
        mesh_from_geometry(chapter, "chapter_ring"),
        material=mats["case_dark"],
        name="chapter_ring", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
    )
    # 12 hour markers + minute ticks — deliberately ultra-low, below the
    # raised hand stack so the three pointers can sweep over them freely.
    for i in range(12):
        a = math.pi / 2.0 - i * TAU / 12.0
        marker_r = dial_r * 0.80
        is_cardinal = i % 3 == 0
        case.visual(
            Box(
                (
                    0.0008 if not is_cardinal else 0.0012,
                    0.0028 if not is_cardinal else 0.0038,
                    _DIAL_FEATURE_H,
                )
            ),
            origin=Origin(
                xyz=(
                    marker_r * math.cos(a),
                    marker_r * math.sin(a),
                    case_h + 0.5 * _DIAL_FEATURE_H,
                ),
                rpy=(0.0, 0.0, a - math.pi / 2.0),
            ),
            material=mats["marker"],
            name=f"hour_marker_{i:02d}", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.precious_gold"),
        )
    for i in range(60):
        if i % 5 == 0:
            continue
        a = math.pi / 2.0 - i * TAU / 60.0
        tick_r = dial_r * 0.90
        case.visual(
            Box((0.00035, 0.0018, _DIAL_FEATURE_H * 0.70)),
            origin=Origin(
                xyz=(
                    tick_r * math.cos(a),
                    tick_r * math.sin(a),
                    case_h + 0.35 * _DIAL_FEATURE_H,
                ),
                rpy=(0.0, 0.0, a - math.pi / 2.0),
            ),
            material=mats["marker"],
            name=f"minute_tick_{i:02d}", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.precious_gold"),
        )
    # Dial-layout specific subdial rings.
    if r.dial_layout == "three_subdials_chrono":
        for i, (dx, dy) in enumerate(
            ((0.0, -dial_r * 0.45), (-dial_r * 0.45, 0.15 * dial_r), (dial_r * 0.45, 0.15 * dial_r))
        ):
            ring = _annular_sector(
                dial_r * 0.11,
                dial_r * 0.18,
                case_h,
                case_h + _DIAL_FEATURE_H,
                0.0,
                TAU,
                segments=32,
            )
            case.visual(
                mesh_from_geometry(ring, f"subdial_ring_{i}"),
                origin=Origin(xyz=(dx, dy, 0.0)),
                material=mats["bezel_accent"],
                name=f"subdial_ring_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.precious_gold"),
            )
            # Keep the support almost flush with the dial.  The subdial hand
            # itself is placed low enough to retain a small captured overlap.
            case.visual(
                Cylinder(radius=0.0006, length=_DIAL_FEATURE_H),
                origin=Origin(xyz=(dx, dy, case_h + 0.5 * _DIAL_FEATURE_H)),
                material=mats["case_dark"],
                name=f"subdial_post_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
            )
    elif r.dial_layout == "open_heart_aperture":
        # Aperture ring + balance-wheel pivot post at 6 o'clock.
        ring = _annular_sector(
            dial_r * 0.20,
            dial_r * 0.28,
            case_h,
            case_h + _DIAL_FEATURE_H,
            0.0,
            TAU,
            segments=48,
        )
        case.visual(
            mesh_from_geometry(ring, "aperture_ring"),
            origin=Origin(xyz=(0.0, -dial_r * 0.45, 0.0)),
            material=mats["bezel_accent"],
            name="aperture_ring", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.precious_gold"),
        )
        case.visual(
            Cylinder(radius=0.0006, length=_DIAL_FEATURE_H),
            origin=Origin(xyz=(0.0, -dial_r * 0.45, case_h + 0.5 * _DIAL_FEATURE_H)),
            material=mats["case_dark"],
            name="balance_pivot_post", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
        )


# --------------------------------------------------------------------------- #
# Slot B — bezel builders. Each candidate emits `bezel` with the same
# bezel_ring visual + candidate-specific accent geometry.
# --------------------------------------------------------------------------- #


def _emit_bezel(bezel, r: ResolvedWatchConfig, mats) -> None:
    """Emit bezel visuals + candidate accents. Origin at (0,0,bezel_z_bottom)."""
    bh = r.bezel_h
    z0 = 0.0
    z1 = bh
    # Core annular ring — every candidate.
    ring = _annular_sector(r.bezel_inner_r, r.bezel_outer_r, z0, z1, 0.0, TAU, segments=64)
    bezel.visual(
        mesh_from_geometry(ring, "bezel_ring"),
        material=mats["bezel_ring"],
        name="bezel_ring", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "orange_dive", "stainless_bracelet", "blue_dial_gold_hands", "black_leather_dress"} else "ceramic.decorative_glazed"),
    )
    style = r.bezel_style
    if style == "dive_rotating_60":
        # 60 minute ticks around the outer edge. Center embeds into the ring
        # top surface so every tick shares geometry with bezel_ring.
        for i in range(60):
            a = i * TAU / 60.0
            major = i % 5 == 0
            b_r = (r.bezel_inner_r + r.bezel_outer_r) * 0.5
            bezel.visual(
                Box(
                    (
                        0.0006 if not major else 0.0010,
                        0.0018 if not major else 0.0030,
                        0.0006,
                    )
                ),
                origin=Origin(
                    xyz=(b_r * math.cos(a), b_r * math.sin(a), z1 - 0.0001),
                    rpy=(0.0, 0.0, a - math.pi / 2.0),
                ),
                material=mats["bezel_accent"],
                name=f"dive_tick_{i:02d}", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.precious_gold"),
            )
    elif style == "smooth_polished_ring":
        # Polished chamfer straddling the ring top so it embeds into it
        # (avoids the disconnected-islands warning on the chamfer layer).
        chamfer = _annular_sector(
            r.bezel_inner_r,
            r.bezel_outer_r,
            z1 - 0.0002,
            z1 + 0.0004,
            0.0,
            TAU,
            segments=48,
        )
        bezel.visual(
            mesh_from_geometry(chamfer, "bezel_chamfer"),
            material=mats["bezel_accent"],
            name="bezel_chamfer", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.precious_gold"),
        )
    elif style == "unidirectional_chrono":
        # 48 external teeth (coin-edge grip). Overlap the tooth's inner face
        # with the bezel_ring's outer radius so the teeth stay welded to the
        # ring across all case_form scales.
        for i in range(48):
            a = i * TAU / 48.0
            tooth_r = r.bezel_outer_r - 0.0002
            bezel.visual(
                Box((0.0012, 0.0018, 0.0016)),
                origin=Origin(
                    xyz=(tooth_r * math.cos(a), tooth_r * math.sin(a), z1 - 0.0008),
                    rpy=(0.0, 0.0, a),
                ),
                material=mats["case_dark"],
                name=f"bezel_tooth_{i:02d}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
            )
    elif style == "bidirectional_gmt":
        # 24 GMT hour markers (dual-color: 12 day / 12 night alternating).
        for i in range(24):
            a = i * TAU / 24.0
            b_r = (r.bezel_inner_r + r.bezel_outer_r) * 0.5
            bezel.visual(
                Box((0.0009, 0.0028, 0.0008)),
                origin=Origin(
                    xyz=(b_r * math.cos(a), b_r * math.sin(a), z1 - 0.0001),
                    rpy=(0.0, 0.0, a - math.pi / 2.0),
                ),
                material=(mats["bezel_accent"] if i < 12 else mats["marker"]),
                name=f"gmt_tick_{i:02d}", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.precious_gold"),
            )
    else:  # raised_numeral_bezel
        # 12 raised numeral stroke pairs — 2 boxes per position.
        for i in range(12):
            a = i * TAU / 12.0
            b_r = (r.bezel_inner_r + r.bezel_outer_r) * 0.5
            for k, off in enumerate((-0.0008, 0.0008)):
                bezel.visual(
                    Box((0.0009, 0.0020, 0.0010)),
                    origin=Origin(
                        xyz=(
                            b_r * math.cos(a) + off * math.cos(a + math.pi / 2.0),
                            b_r * math.sin(a) + off * math.sin(a + math.pi / 2.0),
                            z1 - 0.0001,
                        ),
                        rpy=(0.0, 0.0, a - math.pi / 2.0),
                    ),
                    material=mats["bezel_accent"],
                    name=f"numeral_{i:02d}_{k}", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.precious_gold"),
                )


# --------------------------------------------------------------------------- #
# Hand builder (Slot D base).
# --------------------------------------------------------------------------- #


def _emit_hand(part, *, length: float, width: float, angle: float, material, hub_mat) -> None:
    """Emit a watch hand — blade + hub — centered at part origin."""
    part.visual(
        Box((width, length, _HAND_H)),
        origin=Origin(
            xyz=(0.5 * length * math.cos(angle), 0.5 * length * math.sin(angle), 0.0),
            rpy=(0.0, 0.0, angle - math.pi / 2.0),
        ),
        material=material,
        name="blade", material_class_id="metal.paint_coated",
    )
    part.visual(
        Cylinder(radius=_HAND_R, length=_HAND_H * 1.4),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=hub_mat,
        name="hub", material_class_id="metal.paint_coated",
    )


# --------------------------------------------------------------------------- #
# Strap link builders (Slot C).
# --------------------------------------------------------------------------- #


def _emit_strap_link(part, r: ResolvedWatchConfig, mats, *, idx: int, direction: int) -> None:
    """Emit a single strap link visual family for the current strap_topology.

    All candidates keep the same footprint (width, length, thickness) and same
    upstream face (mating spring bar + previous link at part origin), varying
    only the surface geometry family (Rule 3).
    """
    style = r.strap_topology
    # Per-link tapering width (mimics origin 1 L414 taper).
    width = max(r.strap_w_base - idx * 0.0015, r.strap_w_base * 0.6)
    length = r.strap_len
    thick = r.strap_h
    y_center = direction * length / 2.0
    # Base body — every candidate emits this.
    part.visual(
        Box((width, length, thick)),
        origin=Origin(xyz=(0.0, y_center, 0.0)),
        material=mats["strap"],
        name="strap_body", material_class_id=("ceramic.decorative_glazed" if r.strap_topology in {"ribbed_rubber", "brushed_steel_bracelet", "articulated_ceramic_link", "orange_rubber_holed", "metal_bracelet_bent"} else "fabric.webbing"),
    )
    if style == "ribbed_rubber":
        for k, frac in enumerate((0.23, 0.50, 0.77)):
            part.visual(
                Box((width * 0.90, length * 0.08, thick * 0.35)),
                origin=Origin(xyz=(0.0, direction * length * frac, thick * 0.55)),
                material=mats["strap"],
                name=f"rib_{k}", material_class_id="rubber.directional_grooved",
            )
    elif style == "brushed_steel_bracelet":
        # Center polished panel + dark hinge groove.
        part.visual(
            Box((width * 0.44, length * 0.78, thick * 0.30)),
            origin=Origin(xyz=(0.0, y_center, thick * 0.55)),
            material=mats["strap_accent"],
            name="center_panel", material_class_id="metal.brushed_silver",
        )
    elif style == "articulated_ceramic_link":
        # Dark center + polished side plates (origin 5).
        part.visual(
            Box((width * 0.38, length * 0.85, thick * 0.42)),
            origin=Origin(xyz=(0.0, y_center, thick * 0.55)),
            material=mats["strap_accent"],
            name="dark_center", material_class_id="ceramic.decorative_glazed",
        )
        for side_sign in (-1.0, 1.0):
            part.visual(
                Box((width * 0.20, length * 0.85, thick * 0.42)),
                origin=Origin(
                    xyz=(side_sign * width * 0.37, y_center, thick * 0.55),
                ),
                material=mats["strap"],
                name=f"side_plate_{'a' if side_sign < 0 else 'b'}", material_class_id="metal.chrome_polished",
            )
    elif style == "orange_rubber_holed":
        for k, off in enumerate((-width * 0.35, width * 0.35)):
            part.visual(
                Box((width * 0.15, length * 0.82, thick * 0.35)),
                origin=Origin(xyz=(off, y_center, thick * 0.55)),
                material=mats["strap_accent"],
                name=f"rib_{k}", material_class_id="rubber.pebbled",
            )
    elif style == "metal_bracelet_bent":
        # Three raised plates (origin 4 L82-99).
        for k, dx in enumerate((-width * 0.35, 0.0, width * 0.35)):
            plate_w = width * (0.22 if k != 1 else 0.30)
            part.visual(
                Box((plate_w, length * 0.86, thick * 0.35)),
                origin=Origin(xyz=(dx, y_center, thick * 0.55)),
                material=mats["strap_accent"],
                name=f"raised_plate_{k}", material_class_id="metal.stainless_matte",
            )
    else:  # fabric_flat_strap
        # Single center stitching rib.
        part.visual(
            Box((width * 0.04, length * 0.90, thick * 0.15)),
            origin=Origin(xyz=(0.0, y_center, thick * 0.55)),
            material=mats["strap_accent"],
            name="stitch", material_class_id="fabric.thread_yarn",
        )


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #


def build_watch(
    config: WatchConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"watch_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in r.palette.items()
    }

    # --- Case (root) -----------------------------------------------------
    case = model.part("case")
    _emit_case_body(case, r, mats)

    # --- Bezel (Slot B) --------------------------------------------------
    bezel = model.part("bezel")
    _emit_bezel(bezel, r, mats)
    # Joint at the bezel_seat annulus on the case top (real geometry).
    model.articulation(
        "case_to_bezel",
        _BEZEL_JOINT_TYPE[r.bezel_style],
        parent=case,
        child=bezel,
        origin=Origin(xyz=(0.0, 0.0, r.bezel_z_bottom)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=(
            MotionLimits(effort=1.0, velocity=1.8, lower=0.0, upper=TAU)
            if _BEZEL_JOINT_TYPE[r.bezel_style] == ArticulationType.REVOLUTE
            else MotionLimits(effort=1.0, velocity=1.8)
        ),
        mating=MatingContract(
            parent_face_geometry="case_bezel_seat",
            parent_face_side="positive_z",
            child_face_geometry="bezel_ring",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )

    # --- Hands (Slot D base) --------------------------------------------
    # Three coaxial hands on the central arbor (CONTINUOUS +z).
    hand_specs = (
        (
            "hour_hand",
            r.hand_len_hour,
            0.0016,
            math.radians(60.0),
            "hand",
            "case_dark",
            r.case_h + _HAND_Z_HOUR,
        ),
        (
            "minute_hand",
            r.hand_len_minute,
            0.0012,
            math.radians(160.0),
            "hand",
            "case_dark",
            r.case_h + _HAND_Z_MINUTE,
        ),
        (
            "second_hand",
            r.hand_len_second,
            0.0006,
            math.radians(250.0),
            "hand_accent",
            "hand_accent",
            r.case_h + _HAND_Z_SECOND,
        ),
    )
    for name, length, width, angle, blade_key, hub_key, z in hand_specs:
        part = model.part(name)
        _emit_hand(
            part,
            length=length,
            width=width,
            angle=angle,
            material=mats[blade_key],
            hub_mat=mats[hub_key],
        )
        model.articulation(
            f"case_to_{name}",
            ArticulationType.CONTINUOUS,
            parent=case,
            child=part,
            origin=Origin(xyz=(0.0, 0.0, z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.05, velocity=6.0),
        )

    # --- Dial extras (Slot D variants) -----------------------------------
    if r.dial_layout == "three_subdials_chrono":
        # Add ONE articulated subdial_hand (matches origin 3 L266-L292).
        subhand = model.part("subdial_hand")
        _emit_hand(
            subhand,
            length=r.dial_inner_r * 0.11,
            width=0.0007,
            angle=math.radians(45.0),
            material=mats["hand_accent"],
            hub_mat=mats["hand_accent"],
        )
        # Attach subdial at 6-o'clock subdial center (0, -dial_r*0.45).
        sub_dx = 0.0
        sub_dy = -r.dial_inner_r * 0.45
        model.articulation(
            "case_to_subdial_hand",
            ArticulationType.CONTINUOUS,
            parent=case,
            child=subhand,
            origin=Origin(xyz=(sub_dx, sub_dy, r.case_h + _SUBDIAL_HAND_Z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.02, velocity=4.0),
        )
    elif r.dial_layout == "open_heart_aperture":
        # Add a balance_wheel (small rotating disc + spoke) at the aperture.
        wheel = model.part("balance_wheel")
        wheel.visual(
            Cylinder(radius=r.dial_inner_r * 0.20, length=0.0006),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["hand_accent"],
            name="wheel_disc", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.precious_gold"),
        )
        wheel.visual(
            Box((r.dial_inner_r * 0.34, 0.0006, 0.0008)),
            origin=Origin(xyz=(0.0, 0.0, 0.0004)),
            material=mats["case_dark"],
            name="wheel_spoke", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
        )
        model.articulation(
            "case_to_balance_wheel",
            ArticulationType.CONTINUOUS,
            parent=case,
            child=wheel,
            origin=Origin(xyz=(0.0, -r.dial_inner_r * 0.45, r.case_h + _SUBDIAL_HAND_Z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.01, velocity=8.0),
        )

    # --- Crown + pushers (M2) --------------------------------------------
    # Crown always present.
    crown = model.part("crown")
    crown.visual(
        Cylinder(radius=r.crown_r * 0.4, length=r.crown_r * 2.4),
        origin=Origin(xyz=(-r.crown_r * 1.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["case_dark"],
        name="crown_stem", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
    )
    crown.visual(
        Cylinder(radius=r.crown_r, length=r.crown_r * 1.8),
        origin=Origin(xyz=(r.crown_r * 0.3, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["case"],
        name="crown_body", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
    )
    crown_joint_type = _CROWN_JOINT_BY_STRAP[r.strap_topology]
    if crown_joint_type == ArticulationType.PRISMATIC:
        crown_limits = MotionLimits(effort=3.0, velocity=0.05, lower=0.0, upper=0.004)
    elif crown_joint_type == ArticulationType.REVOLUTE:
        crown_limits = MotionLimits(effort=0.5, velocity=5.0, lower=0.0, upper=TAU)
    else:
        crown_limits = MotionLimits(effort=0.5, velocity=5.0)
    # Crown is a captured stem penetrating the case flank — grandfathered
    # (no MatingContract): the coaxial stem/case overlap is declared via
    # element-scoped allow_overlap in run_watch_tests.
    model.articulation(
        "case_to_crown",
        crown_joint_type,
        parent=case,
        child=crown,
        origin=Origin(xyz=(r.case_outer_r * 0.90, 0.0, r.case_h * 0.45)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=crown_limits,
    )

    # Pushers.
    for pi in range(2):
        if pi + 1 >= r.crown_control_count:
            continue
        py = _PUSHER_Y * 0.9 * (1 if pi == 0 else -1)
        py_scaled = py * (r.case_outer_r / _CASE_R)
        pusher = model.part(f"pusher_{pi}")
        pusher.visual(
            Cylinder(radius=_PUSHER_R * 0.6, length=_PUSHER_R * 3.0),
            origin=Origin(xyz=(-_PUSHER_R * 1.4, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["case_dark"],
            name="pusher_stem", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_blue_dive", "black_ceramic_chrono", "orange_dive", "stainless_bracelet", "black_leather_dress"} else "metal.brass_aged"),
        )
        pusher.visual(
            Cylinder(radius=_PUSHER_R, length=_PUSHER_R * 1.8),
            origin=Origin(xyz=(_PUSHER_R * 0.4, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["case"],
            name="pusher_button", material_class_id=("metal.precious_gold" if r.palette_style == "blue_dial_gold_hands" else "metal.stainless_matte"),
        )
        # Pusher stem is captured in the case pad (grandfathered).
        model.articulation(
            f"case_to_pusher_{pi}",
            ArticulationType.PRISMATIC,
            parent=case,
            child=pusher,
            origin=Origin(xyz=(r.case_outer_r * 0.90, py_scaled, r.case_h * 0.45)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=0.1, lower=0.0, upper=0.0018),
        )

    # --- Strap chains (Slot C + M1) --------------------------------------
    N = r.strap_link_count
    for side, direction, root_y, side_key in (
        ("top", 1, r.lug_y_top, "top"),
        ("bottom", -1, r.lug_y_bottom, "bottom"),
    ):
        prev_part = case
        prev_prefix = "case"
        for i in range(N):
            link = model.part(f"{side}_strap_{i}")
            _emit_strap_link(link, r, mats, idx=i, direction=direction)
            if i == 0:
                origin = Origin(xyz=(0.0, root_y, r.case_h * 0.35))
                parent = case
                # Mating: strap_body touches the spring_bar cylinder (grandfathered
                # via captured-pin `allow_overlap`; MatingContract omitted).
                mating = None
            else:
                origin = Origin(xyz=(0.0, direction * r.strap_len, 0.0))
                parent = prev_part
                # Chain hinges: mate strap_body to previous strap_body along Y.
                mating = MatingContract(
                    parent_face_geometry="strap_body",
                    parent_face_side="positive_y" if direction > 0 else "negative_y",
                    child_face_geometry="strap_body",
                    child_face_side="negative_y" if direction > 0 else "positive_y",
                    contact_tol=0.0020,
                )
            joint_name = f"{prev_prefix}_to_{side}_strap_{i}"
            model.articulation(
                joint_name,
                ArticulationType.REVOLUTE,
                parent=parent,
                child=link,
                origin=origin,
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=0.5, velocity=2.0, lower=-0.75, upper=0.75),
                mating=mating,
            )
            prev_part = link
            prev_prefix = f"{side}_strap_{i}"

    model.meta["slot_choices"] = tuple(slot_choices_for_config(r))
    return model


def build_seeded_watch(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_watch(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests — motion coverage + captured-pin allowances.
# --------------------------------------------------------------------------- #


def _allow_captured_overlaps(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedWatchConfig
) -> None:
    """Element-scoped captured-pin/press-fit allowances (real watch mechanics)."""
    part_names = {p.name for p in model.parts}

    def _get(name: str):
        return model.get_part(name) if name in part_names else None

    case = model.get_part("case")
    bezel = model.get_part("bezel")
    ctx.allow_overlap(
        case,
        bezel,
        elem_a="case_bezel_seat",
        elem_b="bezel_ring",
        reason="Bezel is captured on the case shoulder as a dive-watch ring (press-fit annular seat).",
    )
    # Hands press-fit on central arbor.
    for name in ("hour_hand", "minute_hand", "second_hand"):
        part = model.get_part(name)
        if part is None:
            continue
        ctx.allow_overlap(
            case,
            part,
            elem_a="central_arbor",
            elem_b="hub",
            reason=f"{name} hub is press-fit on the central arbor (coaxial pin).",
        )
    if r.dial_layout == "three_subdials_chrono":
        subhand = _get("subdial_hand")
        if subhand is not None:
            ctx.allow_overlap(
                case,
                subhand,
                elem_a="subdial_post_0",
                elem_b="hub",
                reason="Subdial hand hub press-fit on the subdial post.",
            )
    elif r.dial_layout == "open_heart_aperture":
        wheel = _get("balance_wheel")
        if wheel is not None:
            ctx.allow_overlap(
                case,
                wheel,
                elem_a="balance_pivot_post",
                elem_b="wheel_disc",
                reason="Balance wheel spins on the balance pivot post.",
            )
    # Crown stem penetrates the case flank pad.
    crown = _get("crown")
    if crown is not None:
        ctx.allow_overlap(
            case,
            crown,
            elem_a="case_crown_flank",
            elem_b="crown_stem",
            reason="Crown stem penetrates the case flank (captured stem, grandfathered).",
        )
    # Pushers likewise.
    for pi in range(2):
        pusher = _get(f"pusher_{pi}")
        if pusher is not None:
            ctx.allow_overlap(
                case,
                pusher,
                elem_a=f"case_pusher_pad_{pi}",
                elem_b="pusher_stem",
                reason=f"Pusher {pi} stem is captured in the pusher tube.",
            )
    # First strap link's body wraps around the spring bar.
    for side in ("top", "bottom"):
        first = _get(f"{side}_strap_0")
        if first is not None:
            ctx.allow_overlap(
                case,
                first,
                elem_a=f"{side}_spring_bar",
                elem_b="strap_body",
                reason=f"{side} strap link 0 wraps around the spring bar (spring-bar capture).",
            )
            ctx.allow_overlap(
                case,
                first,
                elem_a=f"{side}_lug_bridge",
                elem_b="strap_body",
                reason=f"{side} strap link 0 seats between the lugs.",
            )


def run_watch_tests(
    model: ArticulatedObject,
    config: WatchConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    _allow_captured_overlaps(ctx, model, r)

    # Baseline (compiler runs these anyway; harmless duplication for author QC).
    ctx.check_model_valid()

    # Identity checks.
    parts = {p.name for p in model.parts}
    joints = {j.name for j in model.articulations}
    ctx.check(
        "watch_has_case_and_bezel",
        "case" in parts and "bezel" in parts and "case_to_bezel" in joints,
        "Watch must have a case + rotating/fixed bezel joint.",
    )
    ctx.check(
        "watch_has_three_hands",
        {"hour_hand", "minute_hand", "second_hand"}.issubset(parts)
        and {"case_to_hour_hand", "case_to_minute_hand", "case_to_second_hand"}.issubset(joints),
        "Watch must have three coaxial central hands.",
    )
    ctx.check(
        "watch_has_strap_chains",
        all(
            f"top_strap_{i}" in parts and f"bottom_strap_{i}" in parts
            for i in range(r.strap_link_count)
        ),
        f"Watch must have {r.strap_link_count} strap links per side.",
    )
    ctx.check(
        "watch_has_crown",
        "crown" in parts and "case_to_crown" in joints,
        "Watch must have a crown control.",
    )
    if r.crown_control_count >= 2:
        ctx.check("watch_has_pusher_0", "pusher_0" in parts, "Chrono config must have pusher_0.")
    if r.crown_control_count >= 3:
        ctx.check("watch_has_pusher_1", "pusher_1" in parts, "Chrono config must have pusher_1.")
    if r.dial_layout == "three_subdials_chrono":
        ctx.check(
            "watch_has_subdial_hand", "subdial_hand" in parts, "Chrono dial must have subdial_hand."
        )
    elif r.dial_layout == "open_heart_aperture":
        ctx.check(
            "watch_has_balance_wheel",
            "balance_wheel" in parts,
            "Open-heart dial must have balance_wheel.",
        )

    # Rule 5 — sampled-pose collision + targeted motion checks.
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=32,
        ignore_fixed=True,
    )
    # Targeted poses to prove semantics (Rule 5).
    minute_joint = model.get_articulation("case_to_minute_hand")
    minute_hand = model.get_part("minute_hand")
    rest_min = ctx.part_world_position(minute_hand)
    with ctx.pose({minute_joint: math.pi / 2.0}):
        moved_min = ctx.part_world_position(minute_hand)
    ctx.check(
        "minute_hand_rotates_about_fixed_center",
        rest_min is not None
        and moved_min is not None
        and abs(rest_min[0] - moved_min[0]) < 1e-6
        and abs(rest_min[1] - moved_min[1]) < 1e-6,
        "Minute hand must rotate about the central arbor.",
    )
    # Bezel rotates in place.
    bezel_joint = model.get_articulation("case_to_bezel")
    bezel = model.get_part("bezel")
    rest_bez = ctx.part_world_position(bezel)
    with ctx.pose({bezel_joint: math.pi / 4.0}):
        moved_bez = ctx.part_world_position(bezel)
    ctx.check(
        "bezel_rotates_in_place",
        rest_bez is not None
        and moved_bez is not None
        and abs(rest_bez[0] - moved_bez[0]) < 1e-4
        and abs(rest_bez[1] - moved_bez[1]) < 1e-4,
        "Bezel joint must rotate around case center.",
    )
    # Strap hinge chain — the second link's world position swings when the
    # first hinge rotates (the first link's part-frame origin coincides with
    # the joint origin so it stays fixed under rotation about that axis).
    if r.strap_link_count >= 2:
        strap_joint_0 = model.get_articulation("case_to_top_strap_0")
        top_strap_1 = model.get_part("top_strap_1")
        rest_strap = ctx.part_world_position(top_strap_1)
        with ctx.pose({strap_joint_0: 0.5}):
            moved_strap = ctx.part_world_position(top_strap_1)
        ctx.check(
            "top_strap_hinge_opens",
            rest_strap is not None
            and moved_strap is not None
            and (
                abs(rest_strap[1] - moved_strap[1]) > 1e-5
                or abs(rest_strap[2] - moved_strap[2]) > 1e-5
            ),
            "Strap hinge must swing the downstream link under rotation.",
        )

    return ctx.report()


__all__ = [
    "CaseForm",
    "BezelStyle",
    "StrapTopology",
    "DialLayout",
    "PaletteStyle",
    "WatchConfig",
    "ResolvedWatchConfig",
    "config_from_seed",
    "resolve_config",
    "build_watch",
    "build_seeded_watch",
    "slot_choices_for_seed",
    "run_watch_tests",
    "__modular__",
]
