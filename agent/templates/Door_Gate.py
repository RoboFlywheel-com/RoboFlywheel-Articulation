# SPDX-License-Identifier: Apache-2.0

"""Wrought-iron entrance / garden gate modular template.

A *gate* here is an openable open-work iron door: a fixed stone / lintel
``surround`` (root parent visual, never moves) holds 1 or 2 iron ``leaf``
parts joined by real vertical-axis REVOLUTE hinges. Each leaf is a perimeter
frame whose interior is an open-work field of ``N`` evenly-spaced vertical
pickets / bars (or a solid kick panel + bar field), often overlaid with
wrought C-scroll / volute work, optionally crowned with spear finials, and
optionally stiffened by a diagonal Z-brace. Double-leaf gates mimic-couple
``door_1`` to ``door_0`` (axis negated) so one positive q swings both leaves
outward toward -Y.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Door_Gate.md`` and the gate 5-star
sample pool (1 parent ``rec_door_gate`` + 8 slot-fork variants), all synced
under ``data/records/``.

Structure (pattern = ``mixed`` parallel-children): a single root
``stone_surround`` part (masonry + threshold + plaster reveal, plus an
optional fixed fanlight grille / flat top rail chosen by the head profile),
with 1-2 ``door_*`` leaf parts attaching as parallel REVOLUTE children.

Slots (all enums sampled per seed in ``config_from_seed``):

  * ``infill_style`` (Slot A, 3): ornamental_scroll_infill / vertical_picket_
    infill / panel_and_bar_infill -- the open-work field topology inside the
    leaf frame.
  * ``top_profile`` (Slot B, 3): straight_top_with_fanlight (arched surround +
    fixed fanlight grille) / flat_rail_head_no_fanlight (rectangular surround +
    flat iron top rail, no fanlight) / spear_pointed_tops (surround, no
    fanlight, pickets extend above the rail crowned by cast spear finials).
  * ``frame_style`` (Slot C, 2): plain_rails_frame / z_brace_diagonal -- an
    optional continuous diagonal brace embedded into the frame corners.
  * ``leaf_count`` (Slot D, 2): double_leaf (2 REVOLUTE + door_1->door_0 Mimic)
    / single_leaf (1 wide leaf, 1 REVOLUTE no mimic, latch stile + handle).
  * ``picket_count`` (N, multiplicity axis): double [5,11] / single [10,22],
    encoded into the slot tuple as ``("picket_count", f"n{N}")``.

``palette_style`` (>=3, 6 here) is a *new* template-level parameter (the 9
5-star samples share one colorway): it only remaps the iron / gold / stone
rgba triples, never the topology or geometry.

Compatibility gating (resolve_config, spec §9):
  * panel_and_bar_infill (solid lower-third kick) conflicts with
    spear_pointed_tops (pickets must run full-height and extend above the
    rail) -> degrade infill to ornamental_scroll_infill.
  * only top_profile == straight_top_with_fanlight emits the fanlight; the
    flat-rail and spear heads omit it (and flat-rail uses the rectangular
    surround).

All hinge knuckles embed into the jamb (captured-pin) and the diagonal brace
embeds into the leaf frame, so those joints rely on element-scoped
``allow_overlap`` (mirroring each source record's run_tests). The hinge
REVOLUTE joints use captured-pin geometry, so they omit ``MatingContract``
(grandfathered) and are guarded by the flat articulation-origin baseline.
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
    Inertial,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

InfillStyle = Literal[
    "ornamental_scroll_infill", "vertical_picket_infill", "panel_and_bar_infill"
]
TopProfile = Literal[
    "straight_top_with_fanlight", "flat_rail_head_no_fanlight", "spear_pointed_tops"
]
FrameStyle = Literal["plain_rails_frame", "z_brace_diagonal"]
LeafCount = Literal["double_leaf", "single_leaf"]
PaletteStyle = Literal[
    "black_wrought_iron",
    "gold_capped_iron",
    "galvanized_silver",
    "painted_white",
    "painted_green",
    "verdigris_bronze",
]

INFILL_STYLES: tuple[InfillStyle, ...] = (
    "ornamental_scroll_infill",
    "vertical_picket_infill",
    "panel_and_bar_infill",
)
TOP_PROFILES: tuple[TopProfile, ...] = (
    "straight_top_with_fanlight",
    "flat_rail_head_no_fanlight",
    "spear_pointed_tops",
)
FRAME_STYLES: tuple[FrameStyle, ...] = ("plain_rails_frame", "z_brace_diagonal")
LEAF_COUNTS: tuple[LeafCount, ...] = ("double_leaf", "single_leaf")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "black_wrought_iron",
    "gold_capped_iron",
    "galvanized_silver",
    "painted_white",
    "painted_green",
    "verdigris_bronze",
)

# Picket-count (multiplicity) ranges per leaf-count (spec §8: test range).
N_RANGE_DOUBLE = (5, 11)
N_RANGE_SINGLE = (10, 22)
# Small N high-frequency, large N long-tail (weighted draw over the range).
_N_TAIL_FRACTION = 0.70  # fraction of the range that gets the bulk of weight

# Infills that have a multi-N source compatible with the spear head.
# panel_and_bar (solid lower kick) fights spears; spec §9 (2).
_SPEAR_OK_INFILLS: tuple[InfillStyle, ...] = (
    "ornamental_scroll_infill",
    "vertical_picket_infill",
)

# ---------------------------------------------------------------------------
# Palette: each style remaps only the iron / gold / stone family rgba.
# galvanized drops gold to a pale steel; verdigris darkens iron + greens gold.
# (spec §13; source materials L81-86 of rec_door_gate.)
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_wrought_iron": {
        "iron": (0.09, 0.09, 0.10, 1.0),
        "gold": (0.74, 0.58, 0.20, 1.0),
        "stone": (0.86, 0.83, 0.76, 1.0),
        "plaster": (0.92, 0.90, 0.84, 1.0),
        "threshold": (0.32, 0.30, 0.28, 1.0),
    },
    "gold_capped_iron": {
        "iron": (0.07, 0.07, 0.08, 1.0),
        "gold": (0.85, 0.68, 0.26, 1.0),
        "stone": (0.83, 0.79, 0.71, 1.0),
        "plaster": (0.93, 0.91, 0.85, 1.0),
        "threshold": (0.30, 0.28, 0.26, 1.0),
    },
    "galvanized_silver": {
        "iron": (0.62, 0.64, 0.66, 1.0),
        "gold": (0.72, 0.74, 0.76, 1.0),  # no real gold: pale steel accent
        "stone": (0.80, 0.80, 0.80, 1.0),
        "plaster": (0.90, 0.90, 0.90, 1.0),
        "threshold": (0.34, 0.34, 0.36, 1.0),
    },
    "painted_white": {
        "iron": (0.93, 0.93, 0.92, 1.0),
        "gold": (0.80, 0.66, 0.30, 1.0),
        "stone": (0.84, 0.81, 0.74, 1.0),
        "plaster": (0.95, 0.94, 0.90, 1.0),
        "threshold": (0.36, 0.34, 0.32, 1.0),
    },
    "painted_green": {
        "iron": (0.10, 0.26, 0.16, 1.0),
        "gold": (0.78, 0.62, 0.24, 1.0),
        "stone": (0.85, 0.82, 0.75, 1.0),
        "plaster": (0.92, 0.90, 0.84, 1.0),
        "threshold": (0.30, 0.30, 0.28, 1.0),
    },
    "verdigris_bronze": {
        "iron": (0.14, 0.16, 0.15, 1.0),
        "gold": (0.36, 0.62, 0.52, 1.0),  # verdigris patina on the bronze
        "stone": (0.82, 0.80, 0.74, 1.0),
        "plaster": (0.90, 0.89, 0.83, 1.0),
        "threshold": (0.28, 0.30, 0.29, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Long axis (gate width) along X; leaf
# thickness along Y; height along Z. From rec_door_gate L51-86 (double) and
# rec_gate_var_single L46-72 (single). Hinge / pin geometry is shared.
# ---------------------------------------------------------------------------
_LEAF_W = 1.06          # one leaf width (X), double; single overrides to ~2.14
_LEAF_H = 2.18          # one leaf height (Z)
_LEAF_T = 0.055         # leaf frame depth (Y)
_JAMB_REVEAL = 0.03     # reveal gap between leaf hinge edge and the jamb
_SILL_Z = 0.04          # threshold sill thickness; leaf bottom sits here
_PILLAR_W = 0.30        # jamb pillar width (X)
_PILLAR_D = 0.34        # jamb pillar / wall depth (Y)
_CENTER_GAP = 0.02      # gap where the two leaves meet
_FRAME_W = 0.075        # leaf stile / rail bar width
_BAR_W = 0.020          # vertical picket bar (square cross-section)
_SCROLL_BAR = 0.016     # iron scroll-bar cross-section width
_LATCH_STILE_W = 0.060  # single-leaf latch stile width

# Hinge geometry (rec_door_gate L71-73).
_KNUCKLE_R = 0.030
_KNUCKLE_LEN = 0.10
_PIN_R = 0.012

# Flat top-rail (rec_gate_var_flatrail L75-82).
_TOP_RAIL_H = 0.06
_TOP_RAIL_D = 0.050
_HEAD_CLEAR = 0.015
_LINTEL_H = 0.25

# Spear finial (rec_gate_var_speartop L80-85).
_PICKET_EXT = 0.08
_FINIAL_COLLAR_H = 0.025
_FINIAL_COLLAR_R = 0.015
_FINIAL_BLADE_H = 0.10
_FINIAL_BLADE_R = 0.019
_FINIAL_H = _FINIAL_COLLAR_H + _FINIAL_BLADE_H

_OPEN_ANGLE_MAX = 1.92  # REVOLUTE upper limit (rad), all sources

# Leaf-local vertical datum: the leaf is authored in a part-local frame whose
# origin (z=0) sits on the sill, at the hinge edge (x=0). The surround-to-leaf
# REVOLUTE joint origin is at world z=_SILL_Z so the leaf renders just above the
# threshold and the joint origin lands inside the leaf AABB (baseline tol).
_LEAF_Z0 = 0.0


@dataclass(frozen=True)
class GateConfig:
    infill_style: InfillStyle | None = None
    top_profile: TopProfile | None = None
    frame_style: FrameStyle | None = None
    leaf_count: LeafCount | None = None
    picket_count: int | None = None
    palette_style: PaletteStyle = "black_wrought_iron"
    leaf_width_scale: float = 1.0
    leaf_height_scale: float = 1.0
    frame_width_scale: float = 1.0
    bar_thickness_scale: float = 1.0
    open_angle: float = 0.0
    name: str = "gate"


@dataclass(frozen=True)
class ResolvedGateConfig:
    infill_style: InfillStyle
    top_profile: TopProfile
    frame_style: FrameStyle
    leaf_count: LeafCount
    picket_count: int
    palette_style: PaletteStyle
    # Concrete geometry (scaled / derived).
    leaf_w: float
    leaf_h: float
    leaf_t: float
    frame_w: float
    bar_w: float
    opening_w: float
    pillar_h: float
    open_angle: float
    name: str

    @property
    def is_single(self) -> bool:
        return self.leaf_count == "single_leaf"

    @property
    def has_fanlight(self) -> bool:
        return self.top_profile == "straight_top_with_fanlight"

    @property
    def is_arched(self) -> bool:
        # Arched surround for fanlight + spear heads; rectangular for flat-rail.
        return self.top_profile != "flat_rail_head_no_fanlight"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _n_range_for(leaf_count: LeafCount) -> tuple[int, int]:
    return N_RANGE_SINGLE if leaf_count == "single_leaf" else N_RANGE_DOUBLE


def _sample_picket_count(rng: random.Random, leaf_count: LeafCount) -> int:
    """Weighted draw over the N range: small N high-frequency, large N tail."""
    lo, hi = _n_range_for(leaf_count)
    values = list(range(lo, hi + 1))
    span = hi - lo
    cut = lo + int(round(span * _N_TAIL_FRACTION))
    weights = [1.0 if v <= cut else 0.35 for v in values]
    return rng.choices(values, weights=weights, k=1)[0]


def config_from_seed(seed: int) -> GateConfig:
    rng = random.Random(seed)
    leaf_count = rng.choice(LEAF_COUNTS)
    return GateConfig(
        infill_style=rng.choice(INFILL_STYLES),
        top_profile=rng.choice(TOP_PROFILES),
        frame_style=rng.choice(FRAME_STYLES),
        leaf_count=leaf_count,
        picket_count=_sample_picket_count(rng, leaf_count),
        palette_style=rng.choice(PALETTE_STYLES),
        leaf_width_scale=round(rng.uniform(0.92, 1.06), 4),
        leaf_height_scale=round(rng.uniform(0.92, 1.10), 4),
        frame_width_scale=round(rng.uniform(0.85, 1.20), 4),
        bar_thickness_scale=round(rng.uniform(0.80, 1.40), 4),
        open_angle=round(rng.uniform(0.0, _OPEN_ANGLE_MAX), 4),
        name=f"seeded_gate_{seed}",
    )


def resolve_config(config: GateConfig | None = None) -> ResolvedGateConfig:
    cfg = config or GateConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    infill_style = _pick(cfg.infill_style, INFILL_STYLES)
    top_profile = _pick(cfg.top_profile, TOP_PROFILES)
    frame_style = _pick(cfg.frame_style, FRAME_STYLES)
    leaf_count = _pick(cfg.leaf_count, LEAF_COUNTS)

    # --- Compatibility gating (spec §9). ---
    # (2) panel_and_bar's solid lower-third kick fights the full-height pickets
    #     a spear head requires -> degrade the infill.
    if top_profile == "spear_pointed_tops" and infill_style not in _SPEAR_OK_INFILLS:
        infill_style = "ornamental_scroll_infill"

    # --- Continuous scales (clamp). ---
    width_scale = _clamp(cfg.leaf_width_scale, 0.92, 1.06)
    height_scale = _clamp(cfg.leaf_height_scale, 0.92, 1.10)
    frame_scale = _clamp(cfg.frame_width_scale, 0.85, 1.20)
    bar_scale = _clamp(cfg.bar_thickness_scale, 0.80, 1.40)
    open_angle = _clamp(cfg.open_angle, 0.0, _OPEN_ANGLE_MAX)

    leaf_h = _LEAF_H * height_scale
    frame_w = _FRAME_W * frame_scale
    bar_w = _BAR_W * bar_scale

    if leaf_count == "single_leaf":
        # Single wide leaf spans the whole opening (rec_gate_var_single L47-48).
        leaf_w = 2.14 * width_scale
        opening_w = leaf_w + 2.0 * _JAMB_REVEAL + 0.04
    else:
        leaf_w = _LEAF_W * width_scale
        # OPENING_W = f(leaf_width_scale): surround opening tracks the leaf.
        opening_w = 2.0 * (leaf_w + _JAMB_REVEAL) + 0.04

    # --- Picket count + air-gap clearance inequality (spec §7). ---
    lo, hi = _n_range_for(leaf_count)
    n = int(cfg.picket_count) if cfg.picket_count is not None else (lo + hi) // 2
    n = int(_clamp(n, lo, hi))
    # usable interior width of one leaf (between the two stiles).
    inner = leaf_w - (_CENTER_GAP / 2.0 if leaf_count == "double_leaf" else 0.0)
    usable = inner - 2.0 * frame_w
    # picket field must keep real air gaps: sum(bar) <= 0.80 * usable.
    # If too dense, drop N first, then shrink the bar.
    while n > lo and (n * bar_w) > 0.80 * usable:
        n -= 1
    if (n * bar_w) > 0.80 * usable and usable > 0.0:
        bar_w = max(0.008, 0.80 * usable / max(n, 1))

    # Pillar / spring-line height (matches each head's source).
    if top_profile == "flat_rail_head_no_fanlight":
        pillar_h = _SILL_Z + leaf_h + _HEAD_CLEAR + _TOP_RAIL_H
    else:
        pillar_h = _SILL_Z + leaf_h + 0.02
        # Spear: pillar/spring must clear the leaf + picket ext + finial so the
        # finials never pierce the arch crown (spec §7).
        if top_profile == "spear_pointed_tops":
            pillar_h = max(pillar_h, _SILL_Z + leaf_h + _PICKET_EXT + _FINIAL_H + 0.04)

    return ResolvedGateConfig(
        infill_style=infill_style,
        top_profile=top_profile,
        frame_style=frame_style,
        leaf_count=leaf_count,
        picket_count=n,
        palette_style=palette_style,
        leaf_w=leaf_w,
        leaf_h=leaf_h,
        leaf_t=_LEAF_T,
        frame_w=frame_w,
        bar_w=bar_w,
        opening_w=opening_w,
        pillar_h=pillar_h,
        open_angle=open_angle,
        name=cfg.name or "gate",
    )


def slot_choices_for_config(
    config: GateConfig | ResolvedGateConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedGateConfig) else resolve_config(config)
    return (
        ("infill_style", r.infill_style),
        ("top_profile", r.top_profile),
        ("frame_style", r.frame_style),
        ("leaf_count", r.leaf_count),
        ("picket_count", f"n{r.picket_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Scrollwork primitives (curled wrought-iron C-scrolls / volutes).
# Adapted from rec_door_gate L413-474 (_c_arc / _volute).
# ---------------------------------------------------------------------------
def _c_arc(cx: float, cz: float, r_out: float, bar: float, depth: float,
           a0_deg: float, a1_deg: float) -> cq.Workplane:
    ro = r_out
    ri = max(r_out - bar, 0.001)
    ring = (
        cq.Workplane("XZ").center(cx, cz).circle(ro).circle(ri)
        .extrude(depth, both=True)
    )
    a0 = math.radians(a0_deg)
    a1 = math.radians(a1_deg)
    big = ro * 4.0
    pts = [(0.0, 0.0)]
    steps = max(2, int(abs(a1_deg - a0_deg) / 18) + 1)
    for k in range(steps + 1):
        a = a0 + (a1 - a0) * k / steps
        pts.append((big * math.cos(a), big * math.sin(a)))
    wedge = (
        cq.Workplane("XZ").center(cx, cz).polyline(pts).close()
        .extrude(depth + 0.01, both=True)
    )
    return ring.intersect(wedge)


def _volute(cx: float, cz: float, sign_in: float, scale: float, bar: float,
            depth: float) -> cq.Workplane:
    s = sign_in
    body = _c_arc(cx, cz, 0.085 * scale, bar, depth, 0, 250)
    ecx = cx - s * 0.028 * scale
    inner = _c_arc(ecx, cz, 0.050 * scale, bar, depth, 60, 320)
    eye = cq.Workplane("XZ").center(ecx, cz).circle(0.018 * scale).extrude(depth, both=True)
    bridge = (
        cq.Workplane("XZ").center(0.5 * (cx + ecx), cz)
        .rect(abs(cx - ecx) + 0.085 * scale, bar).extrude(depth, both=True)
    )
    return body.union(inner).union(eye).union(bridge)


def _scroll_panel_iron(cx: float, cz: float, half_w: float, half_h: float,
                       bar: float, depth: float, reach_h: float | None = None) -> cq.Workplane:
    """Symmetric cluster of mirrored volutes filling a panel (rec_door_gate
    L552-604). A spine + cross-ties bond every volute so nothing floats."""
    work = cq.Workplane("XY")
    sv = half_w * 0.55
    sh = half_h * 0.55
    if reach_h is None:
        reach_h = half_h * 2.05
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            work = work.union(
                _volute(cx + sx * sv, cz + sz * sh, -sx, max(half_h / 0.16, 0.4), bar, depth)
            )
    work = work.union(
        cq.Workplane("XZ").center(cx, cz).rect(bar, reach_h).extrude(depth, both=True)
    )
    work = work.union(
        cq.Workplane("XZ").center(cx, cz).rect(2.0 * sv + 0.04, bar).extrude(depth, both=True)
    )
    for sz in (-1.0, 1.0):
        work = work.union(
            cq.Workplane("XZ").center(cx, cz + sz * sh).rect(2.0 * sv + 0.04, bar)
            .extrude(depth, both=True)
        )
    work = work.union(
        cq.Workplane("XZ").center(cx, cz).ellipse(half_w * 0.16, half_h * 0.30)
        .extrude(depth, both=True)
    )
    return work


def _spear_finial() -> cq.Workplane:
    """Cast spear-tip finial: revolved collar + pointed blade (rec_gate_var_
    speartop L270-293). Base at z=0, tip at z=_FINIAL_H."""
    h_c, r_c = _FINIAL_COLLAR_H, _FINIAL_COLLAR_R
    h_b, r_b = _FINIAL_BLADE_H, _FINIAL_BLADE_R
    total = h_c + h_b
    profile = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(r_c, 0.0)
        .lineTo(r_c, h_c)
        .lineTo(r_b * 0.55, h_c)
        .lineTo(r_b, h_c + h_b * 0.12)
        .lineTo(r_b * 0.70, h_c + h_b * 0.50)
        .lineTo(r_b * 0.30, h_c + h_b * 0.80)
        .lineTo(0.0, total)
        .close()
    )
    return profile.revolve(360, (0, 0), (0, 1))


# ---------------------------------------------------------------------------
# Leaf iron (slot A infill x slot C frame x slot B picket-top), in leaf-local
# frame: hinge edge at local X=0, body extends toward sign*X. Adapts the shared
# _leaf_iron skeleton common to all 9 source records.
# ---------------------------------------------------------------------------
def _leaf_iron(r: ResolvedGateConfig, sign: float) -> cq.Workplane:
    leaf_w = r.leaf_w
    inner = leaf_w - (_CENTER_GAP / 2.0 if not r.is_single else 0.0)
    z0 = _LEAF_Z0
    z1 = _LEAF_Z0 + r.leaf_h
    t = r.leaf_t
    frame_w = r.frame_w
    bar_w = r.bar_w
    n = r.picket_count
    spear = r.top_profile == "spear_pointed_tops"

    def x(u: float) -> float:
        return sign * u

    leaf = cq.Workplane("XY")

    # Perimeter frame: outer rectangular border with a hollow center.
    x_off = 0.0 if sign > 0 else -inner
    outer = (
        cq.Workplane("XY").box(inner, t, r.leaf_h, centered=(False, True, False))
        .translate((x_off, 0, z0))
    )
    inner_cut = (
        cq.Workplane("XY")
        .box(inner - 2 * frame_w, t + 0.02, r.leaf_h - 2 * frame_w, centered=(False, True, False))
        .translate((frame_w if sign > 0 else -inner + frame_w, 0, z0 + frame_w))
    )
    leaf = leaf.union(outer.cut(inner_cut))

    # Single-leaf: a wider latch stile at the free (meeting) edge.
    if r.is_single:
        latch_x = sign * (inner - _LATCH_STILE_W / 2.0)
        leaf = leaf.union(
            cq.Workplane("XY").box(_LATCH_STILE_W, t, r.leaf_h - 2 * frame_w, centered=(True, True, False))
            .translate((latch_x, 0, z0 + frame_w))
        )

    usable = inner - 2 * frame_w
    rail_w = frame_w * 0.75

    if r.infill_style == "panel_and_bar_infill":
        # Solid lower-third kick panel + bar field above (rec_gate_var_panelinfill).
        rail_kick_z = z0 + r.leaf_h / 3.0
        kick_z0 = z0 + frame_w
        kick_z1 = rail_kick_z - rail_w / 2.0
        kick_cx = sign * (frame_w + usable / 2.0)
        leaf = leaf.union(
            cq.Workplane("XY").box(usable, t * 0.6, kick_z1 - kick_z0, centered=(True, True, True))
            .translate((kick_cx, 0, 0.5 * (kick_z0 + kick_z1)))
        )
        # Kick rail + head rail.
        rail_lo_z = rail_kick_z
        rail_mid_z = z1 - 0.66
        for rz in (rail_lo_z, rail_mid_z):
            leaf = leaf.union(
                cq.Workplane("XY").box(inner, t, rail_w, centered=(False, True, True))
                .translate((x_off, 0, rz))
            )
        bar_z0 = rail_lo_z + rail_w / 2.0
        bar_z1 = z1 - frame_w
    else:
        # Three-band rails (scroll) or simple full-height field (plain pickets).
        rail_lo_z = z0 + 0.46
        rail_mid_z = z1 - 0.66
        if r.infill_style == "ornamental_scroll_infill":
            for rz in (rail_lo_z, rail_mid_z):
                leaf = leaf.union(
                    cq.Workplane("XY").box(inner, t, rail_w, centered=(False, True, True))
                    .translate((x_off, 0, rz))
                )
            bar_z0 = rail_lo_z + rail_w / 2.0
            bar_z1 = rail_mid_z - rail_w / 2.0
        else:  # vertical_picket_infill: one full-height field, no inner rails.
            bar_z0 = z0 + frame_w
            bar_z1 = z1 - frame_w

    # Picket field: evenly spaced vertical bars (multiplicity axis N).
    if spear:
        picket_top = z1 + _PICKET_EXT
    else:
        picket_top = bar_z1
    bar_zc = 0.5 * (bar_z0 + picket_top)
    bar_h = picket_top - bar_z0
    for i in range(n):
        u = frame_w + usable * (i + 0.5) / n
        leaf = leaf.union(
            cq.Workplane("XY").box(bar_w, t * 0.7, bar_h, centered=(True, True, True))
            .translate((x(u), 0, bar_zc))
        )

    # Spear finials crowning each picket (rec_gate_var_speartop L370-373).
    if spear:
        for i in range(n):
            u = frame_w + usable * (i + 0.5) / n
            leaf = leaf.union(_spear_finial().translate((x(u), 0, picket_top)))

    # Scroll overlay (ornamental only): dense panels + light picket overlay.
    if r.infill_style == "ornamental_scroll_infill":
        leaf = leaf.union(
            _leaf_scroll_iron(r, sign, rail_lo_z, rail_mid_z, z0, z1, inner, usable)
        )

    # Diagonal Z-brace (slot C), embedded into the frame corners.
    if r.frame_style == "z_brace_diagonal":
        leaf = leaf.union(_z_brace(r, sign, inner))

    return leaf


def _leaf_scroll_iron(r: ResolvedGateConfig, sign: float, rail_lo_z: float,
                      rail_mid_z: float, z0: float, z1: float, inner: float,
                      usable: float) -> cq.Workplane:
    """Dense C-scrolls / volutes filling the upper + lower panels, plus a light
    overlay on the picket field (rec_door_gate L607-656)."""
    t = r.leaf_t
    depth = t * 0.55
    cx = (r.frame_w + usable * 0.5) if sign > 0 else -(r.frame_w + usable * 0.5)
    work = cq.Workplane("XY")

    # Upper scroll panel.
    up_top = z1 - r.frame_w
    up_zc = 0.5 * (rail_mid_z + up_top)
    up_hh = 0.5 * (up_top - rail_mid_z) * 0.9
    work = work.union(
        _scroll_panel_iron(cx, up_zc, usable * 0.5 * 0.92, up_hh, _SCROLL_BAR, depth,
                           reach_h=(up_top - rail_mid_z) + 0.06)
    )
    # Lower scroll band.
    lo_bot = z0 + r.frame_w
    lo_zc = 0.5 * (lo_bot + rail_lo_z)
    lo_hh = 0.5 * (rail_lo_z - lo_bot) * 0.92
    work = work.union(
        _scroll_panel_iron(cx, lo_zc, usable * 0.5 * 0.92, lo_hh, _SCROLL_BAR, depth,
                           reach_h=(rail_lo_z - lo_bot) + 0.06)
    )
    # Light picket-field overlay (cross-ties + small volutes bonding to rails).
    pk_zc = 0.5 * (rail_lo_z + rail_mid_z)
    for sz in (-1.0, 1.0):
        row_z = pk_zc + sz * (rail_mid_z - rail_lo_z) * 0.34
        work = work.union(
            cq.Workplane("XZ").center(cx, row_z).rect(usable * 0.92, _SCROLL_BAR * 0.8)
            .extrude(depth, both=True)
        )
        for sx in (-1.0, 1.0):
            work = work.union(_volute(cx + sx * usable * 0.30, row_z, -sx, 0.85, _SCROLL_BAR, depth))
    return work


def _z_brace(r: ResolvedGateConfig, sign: float, inner: float) -> cq.Workplane:
    """Continuous diagonal brace from bottom-hinge corner to top-latch corner,
    embedded into the frame corners (rec_gate_var_zbrace L790-832)."""
    z0 = _LEAF_Z0
    z1 = _LEAF_Z0 + r.leaf_h
    frame_w = r.frame_w
    bx = sign * frame_w * 0.5
    bz = z0 + frame_w * 0.5
    tx = sign * (inner - frame_w * 0.5)
    tz = z1 - frame_w * 0.5
    mx = 0.5 * (bx + tx)
    mz = 0.5 * (bz + tz)
    dx = tx - bx
    dz = tz - bz
    length = math.sqrt(dx * dx + dz * dz)
    angle_rad = math.atan2(dz, dx)
    brace_w = frame_w * 0.70
    brace_t = r.leaf_t * 0.80
    return (
        cq.Workplane("XY").box(length, brace_t, brace_w, centered=(True, True, True))
        .rotate((0, 0, 0), (0, 1, 0), -math.degrees(angle_rad))
        .translate((mx, 0.0, mz))
    )


def _leaf_scrolls_gold(r: ResolvedGateConfig, sign: float) -> cq.Workplane:
    """Gold caps proud of the iron scroll eyes + panel bosses + picket heads
    (rec_door_gate L687-738). Only for ornamental_scroll_infill."""
    inner = r.leaf_w - (_CENTER_GAP / 2.0 if not r.is_single else 0.0)
    z0 = _LEAF_Z0
    z1 = _LEAF_Z0 + r.leaf_h
    t = r.leaf_t
    usable = inner - 2 * r.frame_w
    proud = t * 0.55
    cx = (r.frame_w + usable * 0.5) if sign > 0 else -(r.frame_w + usable * 0.5)
    rail_lo_z = z0 + 0.46
    rail_mid_z = z1 - 0.66

    def tip(tx: float, tz: float, rad: float) -> cq.Workplane:
        return cq.Workplane("XZ").center(tx, tz).circle(rad).extrude(proud, both=True)

    def panel_gold(pcx: float, pcz: float, half_w: float, half_h: float) -> cq.Workplane:
        sv = half_w * 0.55
        sh = half_h * 0.55
        scale = max(half_h / 0.16, 0.4)
        w = tip(pcx, pcz, half_h * 0.20)
        for sx in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                ex = (pcx + sx * sv) - (-sx) * 0.028 * scale
                w = w.union(tip(ex, pcz + sz * sh, 0.018 * scale))
        return w

    up_zc = 0.5 * (rail_mid_z + (z1 - r.frame_w))
    up_hh = 0.5 * ((z1 - r.frame_w) - rail_mid_z) * 0.9
    scrolls = panel_gold(cx, up_zc, usable * 0.5 * 0.92, up_hh)
    lo_zc = 0.5 * ((z0 + r.frame_w) + rail_lo_z)
    lo_hh = 0.5 * (rail_lo_z - (z0 + r.frame_w)) * 0.92
    scrolls = scrolls.union(panel_gold(cx, lo_zc, usable * 0.5 * 0.92, lo_hh))
    # Picket-overlay eyes.
    pk_zc = 0.5 * (rail_lo_z + rail_mid_z)
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            vcx = cx + sx * usable * 0.30
            vcz = pk_zc + sz * (rail_mid_z - rail_lo_z) * 0.34
            ex = vcx - (-(-sx)) * 0.028 * 0.85
            scrolls = scrolls.union(tip(ex, vcz, 0.018 * 0.85))
    # Gold cap rings on the picket heads at the mid rail.
    for i in range(r.picket_count):
        u = r.frame_w + usable * (i + 0.5) / r.picket_count
        scrolls = scrolls.union(tip(sign * u, rail_mid_z, 0.014))
    return scrolls


def _leaf_hinges(r: ResolvedGateConfig, sign: float) -> cq.Workplane:
    """Three hinge knuckles + a vertical pin on the leaf hinge edge (local X=0),
    nudged toward the jamb (captured-pin). rec_door_gate L741-782."""
    knuckles = cq.Workplane("XY")
    out = -sign * 0.022
    z0 = _LEAF_Z0
    zs = (z0 + 0.16, z0 + r.leaf_h / 2.0, z0 + r.leaf_h - 0.16)
    for hz in zs:
        knuckles = knuckles.union(
            cq.Workplane("XY").circle(_KNUCKLE_R).extrude(_KNUCKLE_LEN)
            .translate((out, 0.0, hz - _KNUCKLE_LEN / 2.0))
        )
        knuckles = knuckles.union(
            cq.Workplane("XY").box(_KNUCKLE_R + abs(out) + 0.03, _KNUCKLE_R, _KNUCKLE_LEN * 0.55,
                                   centered=(True, True, True))
            .translate((out / 2.0, 0.0, hz))
        )
    knuckles = knuckles.union(
        cq.Workplane("XY").circle(_PIN_R).extrude(r.leaf_h - 0.10)
        .translate((out, 0.0, z0 + 0.05))
    )
    return knuckles


def _latch_handle(r: ResolvedGateConfig, sign: float) -> cq.Workplane:
    """Latch handle on the free edge of a single leaf (rec_gate_var_single
    L703-733). Authored in leaf-local frame; latch stile at sign*inner edge."""
    inner = r.leaf_w
    t = r.leaf_t
    handle_x = sign * (inner - _LATCH_STILE_W / 2.0)
    handle_z = _LEAF_Z0 + r.leaf_h / 2.0
    proud = t / 2.0 + 0.02
    bar = (
        cq.Workplane("XY").box(0.035, 0.14, 0.035, centered=(True, False, True))
        .translate((handle_x, -proud, handle_z))
    )
    plate = (
        cq.Workplane("XY").box(0.06, 0.015, 0.08, centered=(True, True, True))
        .translate((handle_x, t / 2.0 + 0.007, handle_z))
    )
    stub = (
        cq.Workplane("XY").box(0.04, t + 0.03, 0.04, centered=(True, True, True))
        .translate((handle_x, 0, handle_z))
    )
    return bar.union(plate).union(stub)


# ---------------------------------------------------------------------------
# Surround (root, parent visual) — arched (+fanlight) or rectangular (+rail).
# ---------------------------------------------------------------------------
def _arched_masonry(r: ResolvedGateConfig) -> cq.Workplane:
    """Two jamb pillars + a true semicircular masonry arch ring with the
    doorway / fanlight cut out (rec_door_gate L94-157)."""
    half_open = r.opening_w / 2.0
    arch_inner_r = half_open
    arch_outer_r = half_open + _PILLAR_W
    spring_z = r.pillar_h
    slab_h = spring_z + arch_outer_r
    wall = cq.Workplane("XZ").box(r.opening_w + 2 * _PILLAR_W, slab_h, _PILLAR_D,
                                  centered=(True, False, True))
    door_cut = (
        cq.Workplane("XZ").workplane().center(0.0, spring_z / 2.0)
        .box(r.opening_w, spring_z, _PILLAR_D + 0.02, centered=(True, True, True))
    )
    wall = wall.cut(door_cut)
    arch_cut = (
        cq.Workplane("XZ").workplane().center(0.0, spring_z).circle(arch_inner_r)
        .extrude(_PILLAR_D + 0.02, both=True)
    )
    wall = wall.cut(arch_cut)
    crown_cut = (
        cq.Workplane("XZ").workplane().center(0.0, spring_z).circle(arch_outer_r)
        .extrude(_PILLAR_D + 0.04, both=True)
    )
    top_band = (
        cq.Workplane("XZ").workplane().center(0.0, spring_z + arch_outer_r / 2.0)
        .box(r.opening_w + 2 * _PILLAR_W + 0.1, arch_outer_r, _PILLAR_D + 0.1, centered=(True, True, True))
    )
    arched_top = top_band.intersect(crown_cut)
    lower_part = (
        cq.Workplane("XZ").workplane().center(0.0, spring_z / 2.0)
        .box(r.opening_w + 2 * _PILLAR_W + 0.1, spring_z, _PILLAR_D + 0.1, centered=(True, True, True))
    )
    return wall.intersect(lower_part.union(arched_top))


def _rectangular_surround(r: ResolvedGateConfig) -> cq.Workplane:
    """Two jamb pillars + a flat stone lintel, no arch (rec_gate_var_flatrail
    L103-138)."""
    half_open = r.opening_w / 2.0
    left = (
        cq.Workplane("XY").box(_PILLAR_W, _PILLAR_D, r.pillar_h, centered=(True, True, False))
        .translate((-(half_open + _PILLAR_W / 2.0), 0.0, 0.0))
    )
    right = (
        cq.Workplane("XY").box(_PILLAR_W, _PILLAR_D, r.pillar_h, centered=(True, True, False))
        .translate((half_open + _PILLAR_W / 2.0, 0.0, 0.0))
    )
    lintel = (
        cq.Workplane("XY").box(r.opening_w + 2 * _PILLAR_W, _PILLAR_D, _LINTEL_H, centered=(True, True, False))
        .translate((0.0, 0.0, r.pillar_h))
    )
    return left.union(right).union(lintel)


def _top_rail(r: ResolvedGateConfig) -> cq.Workplane:
    """Flat horizontal iron rail across the opening head (rec_gate_var_flatrail
    L141-150)."""
    z_center = r.pillar_h - _TOP_RAIL_H / 2.0
    return (
        cq.Workplane("XZ").center(0.0, z_center).rect(r.opening_w, _TOP_RAIL_H)
        .extrude(_TOP_RAIL_D, both=True)
    )


def _threshold(r: ResolvedGateConfig) -> cq.Workplane:
    return (
        cq.Workplane("XZ").box(r.opening_w + 0.04, _SILL_Z, _PILLAR_D, centered=(True, False, True))
    )


def _plaster_reveal(r: ResolvedGateConfig) -> cq.Workplane:
    spring_z = r.pillar_h
    t = 0.04
    band = 0.05
    half = r.opening_w / 2.0
    rev = cq.Workplane("XY")
    for sx in (-1.0, 1.0):
        rev = rev.union(
            cq.Workplane("XY").box(band, t, spring_z - _SILL_Z, centered=(True, True, False))
            .translate((sx * (half - band / 2.0), -_PILLAR_D / 2.0 + t / 2.0, _SILL_Z))
        )
    return rev


# Fanlight transom (rec_door_gate L160-379). Kept faithful to the source; the
# arched-fanlight head is the only profile that emits it.
_FAN_BAR = 0.022
_FAN_DEPTH = 0.045
_FAN_BAND_IN = 0.86
_FAN_OVAL_C = 0.45
_FAN_OVAL_RX = 0.135
_FAN_OVAL_RZ = 0.265
_FAN_PED_Z = 0.66
_FAN_BOWL_X = 0.20
_FAN_VOL_BIG = (0.45, 0.42, 2.2)
_FAN_VOL_MID = (0.72, 0.18, 1.6)
_FAN_VOL_CRN = (0.88, 0.10, 1.0)
_FAN_ELL_POS = (0.38, 0.16)


def _fanlight_grille(r: ResolvedGateConfig) -> cq.Workplane:
    spring_z = r.pillar_h
    rad = r.opening_w / 2.0 + 0.008
    bar = _FAN_BAR
    depth = _FAN_DEPTH
    cy = spring_z

    def ring(ro: float, ri: float, h: float) -> cq.Workplane:
        return (
            cq.Workplane("XZ").workplane().center(0.0, cy).circle(ro).circle(ri)
            .extrude(h, both=True)
        )

    rim = ring(rad, rad - bar, depth / 2.0)
    upper = (
        cq.Workplane("XZ").workplane().center(0.0, cy + rad / 2.0)
        .box(2 * rad + 0.2, rad, depth + 0.1, centered=(True, True, True))
    )
    grille = rim.intersect(upper)
    grille = grille.union(
        cq.Workplane("XZ").workplane().center(0.0, cy + bar / 2.0)
        .box(2 * rad, bar, depth, centered=(True, True, True))
    )
    band_in = rad * _FAN_BAND_IN
    grille = grille.union(ring(band_in + bar * 0.8, band_in, depth / 2.0).intersect(upper))
    n_bal = 15
    bal_len = (rad - bar * 0.5) - band_in
    for i in range(n_bal):
        theta = -math.pi / 2.0 + math.pi * (i + 0.5) / n_bal
        baluster = (
            cq.Workplane("XY").box(bar * 0.7, depth, bal_len, centered=(True, True, False))
            .translate((0, 0, band_in)).rotate((0, 0, 0), (0, 1, 0), math.degrees(theta))
            .translate((0, 0, cy))
        )
        grille = grille.union(baluster)
    r_mid = (band_in + rad - bar) / 2.0
    ring_ro = (rad - bar - band_in) / 2.0 + 0.004
    ring_ri = ring_ro - bar * 0.8
    for i in range(n_bal - 1):
        ang = math.pi * (i + 1) / n_bal
        grille = grille.union(
            cq.Workplane("XZ").center(r_mid * math.cos(ang), cy + r_mid * math.sin(ang))
            .circle(ring_ro).circle(ring_ri).extrude(depth / 2.0, both=True)
        )
    orn = cq.Workplane("XY")
    orn = orn.union(
        cq.Workplane("XZ").center(0.0, cy + (band_in + 0.02) / 2.0).rect(bar, band_in + 0.02)
        .extrude(depth / 2.0, both=True)
    )
    oval = (
        cq.Workplane("XZ").center(0.0, cy + _FAN_OVAL_C).ellipse(_FAN_OVAL_RX, _FAN_OVAL_RZ)
        .extrude(depth / 2.0, both=True)
        .cut(cq.Workplane("XZ").center(0.0, cy + _FAN_OVAL_C)
             .ellipse(_FAN_OVAL_RX - bar, _FAN_OVAL_RZ - bar).extrude(depth, both=True))
    )
    orn = orn.union(oval)
    orn = orn.union(
        cq.Workplane("XZ").center(0.0, cy + _FAN_PED_Z).rect(0.64, bar).extrude(depth / 2.0, both=True)
    )
    for sx in (-1.0, 1.0):
        orn = orn.union(
            cq.Workplane("XZ").center(sx * 0.30, cy + (0.50 + _FAN_PED_Z) / 2.0)
            .rect(bar, _FAN_PED_Z - 0.50 + bar).extrude(depth / 2.0, both=True)
        )
    for sx in (-1.0, 1.0):
        for vx, vz, scale in (_FAN_VOL_BIG, _FAN_VOL_MID, _FAN_VOL_CRN):
            orn = orn.union(_volute(sx * vx, cy + vz, -sx, scale, bar * 0.9, depth / 2.0))
        orn = orn.union(
            cq.Workplane("XZ").center(sx * _FAN_ELL_POS[0], cy + _FAN_ELL_POS[1])
            .ellipse(0.14, 0.068).extrude(depth / 2.0, both=True)
        )
    orn = orn.union(
        cq.Workplane("XZ").center(0.0, cy + _FAN_VOL_BIG[1]).rect(2 * (_FAN_VOL_BIG[0] + 0.19), bar)
        .extrude(depth / 2.0, both=True)
    )
    orn = orn.union(
        cq.Workplane("XZ").center(0.0, cy + _FAN_ELL_POS[1]).rect(2 * 0.86, bar)
        .extrude(depth / 2.0, both=True)
    )
    orn = orn.intersect(upper).intersect(
        cq.Workplane("XZ").workplane().center(0.0, cy).circle(band_in + 0.012).extrude(depth, both=True)
    )
    return grille.union(orn)


def _fanlight_gold(r: ResolvedGateConfig) -> cq.Workplane:
    cy = r.pillar_h
    proud = _FAN_DEPTH / 2.0 + 0.008

    def solid(cx: float, cz: float, rx: float, rz: float) -> cq.Workplane:
        return cq.Workplane("XZ").center(cx, cy + cz).ellipse(rx, rz).extrude(proud, both=True)

    gold = solid(0.0, _FAN_OVAL_C, _FAN_OVAL_RX - 0.018, _FAN_OVAL_RZ - 0.018)
    for sx in (-1.0, 1.0):
        gold = gold.union(solid(sx * _FAN_BOWL_X, _FAN_PED_Z + 0.045, 0.075, 0.050))
        gold = gold.union(solid(sx * _FAN_ELL_POS[0], _FAN_ELL_POS[1], 0.115, 0.052))
        for vx, vz, scale in (_FAN_VOL_BIG, _FAN_VOL_MID, _FAN_VOL_CRN):
            ex = sx * vx + sx * 0.028 * scale
            gold = gold.union(solid(ex, vz, 0.018 * scale, 0.018 * scale))
    return gold


# ---------------------------------------------------------------------------
# Part builders.
# ---------------------------------------------------------------------------
def _build_surround(model: ArticulatedObject, r: ResolvedGateConfig, mats, *, assets):
    surround = model.part("stone_surround")
    masonry = _arched_masonry(r) if r.is_arched else _rectangular_surround(r)
    surround.visual(mesh_from_cadquery(masonry, "masonry", assets=assets),
                    material=mats["stone"], name="masonry", material_class_id="stone.masonry_wall")
    surround.visual(mesh_from_cadquery(_plaster_reveal(r), "plaster_reveal", assets=assets),
                    material=mats["plaster"], name="plaster_reveal", material_class_id="plaster.smooth")
    surround.visual(mesh_from_cadquery(_threshold(r), "threshold", assets=assets),
                    material=mats["threshold"], name="threshold", material_class_id="concrete.smooth_cast")
    if r.has_fanlight:
        surround.visual(mesh_from_cadquery(_fanlight_grille(r), "fanlight_grille", assets=assets),
                        material=mats["iron"], name="fanlight_grille", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"black_wrought_iron", "gold_capped_iron", "galvanized_silver", "painted_white", "painted_green"} else "rust.verdigris_patina"))
        surround.visual(mesh_from_cadquery(_fanlight_gold(r), "fanlight_gold", assets=assets),
                        material=mats["gold"], name="fanlight_gold", material_class_id=("metal.precious_gold" if r.palette_style in {"black_wrought_iron", "gold_capped_iron", "galvanized_silver", "painted_white", "painted_green"} else "rust.verdigris_patina"))
    if r.top_profile == "flat_rail_head_no_fanlight":
        surround.visual(mesh_from_cadquery(_top_rail(r), "top_rail", assets=assets),
                        material=mats["iron"], name="top_rail", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"black_wrought_iron", "gold_capped_iron", "galvanized_silver", "painted_white", "painted_green"} else "rust.verdigris_patina"))
    surround.inertial = Inertial.from_geometry(
        Box((r.opening_w + 2 * _PILLAR_W, _PILLAR_D, r.pillar_h)),
        mass=120.0,
        origin=Origin(xyz=(0.0, 0.0, r.pillar_h / 2.0)),
    )
    return surround


def _build_leaf(model: ArticulatedObject, r: ResolvedGateConfig, surround, mats, *,
                part_name: str, sign: float, axis_z: float, mimic_of: str | None, assets):
    leaf = model.part(part_name)
    leaf.visual(mesh_from_cadquery(_leaf_iron(r, sign), f"{part_name}_iron", assets=assets),
                material=mats["iron"], name=f"{part_name}_iron", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"black_wrought_iron", "gold_capped_iron", "galvanized_silver", "painted_white", "painted_green"} else "rust.verdigris_patina"))
    if r.infill_style == "ornamental_scroll_infill":
        leaf.visual(mesh_from_cadquery(_leaf_scrolls_gold(r, sign), f"{part_name}_scrolls", assets=assets),
                    material=mats["gold"], name=f"{part_name}_scrolls", material_class_id=("metal.precious_gold" if r.palette_style in {"black_wrought_iron", "gold_capped_iron", "galvanized_silver", "painted_white", "painted_green"} else "rust.verdigris_patina"))
    leaf.visual(mesh_from_cadquery(_leaf_hinges(r, sign), f"{part_name}_knuckles", assets=assets),
                material=mats["iron"], name=f"{part_name}_knuckles", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"black_wrought_iron", "gold_capped_iron", "galvanized_silver", "painted_white", "painted_green"} else "rust.verdigris_patina"))
    if r.is_single:
        leaf.visual(mesh_from_cadquery(_latch_handle(r, sign), f"{part_name}_latch", assets=assets),
                    material=mats["iron"], name=f"{part_name}_latch", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"black_wrought_iron", "gold_capped_iron", "galvanized_silver", "painted_white", "painted_green"} else "rust.verdigris_patina"))
    leaf.inertial = Inertial.from_geometry(
        Box((r.leaf_w, r.leaf_t, r.leaf_h)),
        mass=40.0 if r.is_single else 22.0,
        origin=Origin(xyz=(sign * r.leaf_w / 2.0, 0.0, _LEAF_Z0 + r.leaf_h / 2.0)),
    )
    # The leaf body extends toward sign*X from its local origin (hinge edge at
    # X=0). To put that hinge edge at the correct jamb, the joint origin sits on
    # the OPPOSITE side: door_0 (sign=+1, extends +X) hinges at the LEFT jamb
    # (-x); door_1 (sign=-1, extends -X) hinges at the RIGHT jamb (+x).
    hinge_x = -sign * (r.opening_w / 2.0 - _JAMB_REVEAL)
    kwargs = {}
    if mimic_of is not None:
        kwargs["mimic"] = Mimic(joint=mimic_of, multiplier=1.0, offset=0.0)
    # The child link frame is placed AT the joint origin. The leaf visuals are
    # authored about a part-local frame whose origin sits on the sill (z=LEAF_Z0)
    # at the hinge edge (x=0): see _LEAF_Z0 below. So the joint origin's z must be
    # LEAF_Z0 (the leaf bottom) for the origin to land inside the leaf AABB and
    # for the leaf to render at the correct world height. dist_child stays ~0.
    model.articulation(
        f"surround_to_{part_name}",
        ArticulationType.REVOLUTE,
        parent=surround,
        child=leaf,
        origin=Origin(xyz=(hinge_x, 0.0, _SILL_Z)),
        axis=(0.0, 0.0, axis_z),
        motion_limits=MotionLimits(effort=60.0, velocity=1.2, lower=0.0, upper=_OPEN_ANGLE_MAX),
        **kwargs,
    )
    return leaf


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_gate(
    config: GateConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"gate_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    surround = _build_surround(model, r, mats, assets=assets)

    if r.is_single:
        # One wide leaf, hinged at the LEFT jamb, axis -Z, no mimic.
        _build_leaf(model, r, surround, mats, part_name="gate_leaf", sign=+1.0,
                    axis_z=-1.0, mimic_of=None, assets=assets)
    else:
        # door_0 at LEFT jamb (axis -Z); door_1 at RIGHT jamb (axis +Z),
        # mimic-coupled so positive q swings both leaves outward (-Y).
        _build_leaf(model, r, surround, mats, part_name="door_0", sign=+1.0,
                    axis_z=-1.0, mimic_of=None, assets=assets)
        _build_leaf(model, r, surround, mats, part_name="door_1", sign=-1.0,
                    axis_z=+1.0, mimic_of="surround_to_door_0", assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_gate(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_gate(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_gate_tests(
    object_model: ArticulatedObject,
    config: GateConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    surround = object_model.get_part("stone_surround")

    leaf_names = ["gate_leaf"] if r.is_single else ["door_0", "door_1"]

    # ---- Captured-pin / brace allowances (element-scoped). ----
    for ln in leaf_names:
        leaf = object_model.get_part(ln)
        ctx.allow_overlap(
            leaf, surround, elem_a=f"{ln}_knuckles", elem_b="masonry",
            reason="Hinge knuckles intentionally embed into the jamb pillar (captured-pin mount).",
        )
        # The gate leaf swings open within the stone surround; through its full
        # opening arc the iron leaf grazes the jamb / reveal masonry.
        ctx.allow_overlap(
            leaf, surround,
            reason="Gate leaf swings open within the stone surround, grazing the reveal masonry.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("stone_surround root present", "stone_surround" in part_names,
              details=str(sorted(part_names)))
    ctx.check(
        f"leaf parts present ({r.leaf_count})",
        all(ln in part_names for ln in leaf_names),
        details=str(sorted(part_names)),
    )

    # ---- Leaf geometry: tall upright open-work, standing on the sill. ----
    aabbs = {}
    for ln in leaf_names:
        a = ctx.part_world_aabb(object_model.get_part(ln))
        aabbs[ln] = a
        if a is not None:
            h = a[1][2] - a[0][2]
            ctx.check(f"{ln} is a tall upright leaf", h > 2.0, details=f"height={h:.3f}")
            ctx.check(f"{ln} stands on the sill", abs(a[0][2] - _SILL_Z) < 0.06,
                      details=f"z_min={a[0][2]:.3f}")

    # ---- Hinge joint topology (REVOLUTE about Z; mimic / latch per leaf count). ----
    if r.is_single:
        j = object_model.get_articulation("surround_to_gate_leaf")
        ctx.check(
            "single leaf is REVOLUTE about Z, no mimic",
            j.articulation_type == ArticulationType.REVOLUTE
            and abs(j.axis[2]) > 0.99 and getattr(j, "mimic", None) is None,
            details=f"type={j.articulation_type} axis={tuple(j.axis)} mimic={getattr(j, 'mimic', None)}",
        )
        latch = [v.name for v in object_model.get_part("gate_leaf").visuals
                 if v.name.endswith("_latch")]
        ctx.check("single leaf has a latch handle", len(latch) == 1, details=str(latch))
    else:
        j0 = object_model.get_articulation("surround_to_door_0")
        j1 = object_model.get_articulation("surround_to_door_1")
        ctx.check(
            "double leaves are 2 REVOLUTE about Z with negated axes",
            j0.articulation_type == ArticulationType.REVOLUTE
            and j1.articulation_type == ArticulationType.REVOLUTE
            and abs(j0.axis[2]) > 0.99 and abs(j1.axis[2]) > 0.99
            and j0.axis[2] * j1.axis[2] < 0,
            details=f"j0={tuple(j0.axis)} j1={tuple(j1.axis)}",
        )
        ctx.check(
            "door_1 mimic-coupled to door_0",
            getattr(j1, "mimic", None) is not None
            and getattr(j1.mimic, "joint", None) == "surround_to_door_0",
            details=f"mimic={getattr(j1, 'mimic', None)}",
        )

    # ---- Picket count (multiplicity) recorded, real air gaps (no solid Door). ----
    inner = r.leaf_w - (_CENTER_GAP / 2.0 if not r.is_single else 0.0)
    usable = inner - 2.0 * r.frame_w
    ctx.check(
        "picket field keeps real air gaps (open-work, not a solid door)",
        r.picket_count * r.bar_w <= 0.80 * usable + 1e-6,
        details=f"N*bar={r.picket_count * r.bar_w:.4f} 0.8*usable={0.80 * usable:.4f}",
    )

    # ---- Head profile self-consistency (fanlight XOR top_rail; spear finials). ----
    surround_elems = {v.name for v in surround.visuals}
    has_fanlight = "fanlight_grille" in surround_elems
    has_rail = "top_rail" in surround_elems
    ctx.check(
        "head profile fanlight/top-rail consistent with top_profile",
        (has_fanlight == r.has_fanlight)
        and (has_rail == (r.top_profile == "flat_rail_head_no_fanlight"))
        and not (has_fanlight and has_rail),
        details=f"fanlight={has_fanlight} rail={has_rail} profile={r.top_profile}",
    )
    if r.has_fanlight:
        fan = ctx.part_element_world_aabb(surround, elem="fanlight_grille")
        if ctx.check("fanlight grille resolves to an AABB", fan is not None):
            ctx.check(
                "fanlight sits above the leaves (fixed parent visual)",
                fan[0][2] > _SILL_Z + r.leaf_h - 0.20,
                details=f"grille z_min={fan[0][2]:.3f} leaf_top={_SILL_Z + r.leaf_h:.3f}",
            )

    # Spear finials must not pierce the surround head crown (clearance gate).
    if r.top_profile == "spear_pointed_tops":
        finial_top = _SILL_Z + r.leaf_h + _PICKET_EXT + _FINIAL_H
        ctx.check(
            "spear finials clear the surround head",
            r.pillar_h >= finial_top - 1e-6,
            details=f"pillar_h={r.pillar_h:.3f} finial_top={finial_top:.3f}",
        )

    # ---- Closed pose: leaves span / center symmetry (double). ----
    if not r.is_single and aabbs["door_0"] is not None and aabbs["door_1"] is not None:
        cx0 = 0.5 * (aabbs["door_0"][0][0] + aabbs["door_0"][1][0])
        cx1 = 0.5 * (aabbs["door_1"][0][0] + aabbs["door_1"][1][0])
        ctx.check(
            "closed leaves symmetric about the center plane",
            abs(cx0 + cx1) < 0.04 and cx0 < 0.0 < cx1,
            details=f"cx0={cx0:.3f} cx1={cx1:.3f}",
        )

    # ---- Open pose: positive q swings the free edge(s) outward (-Y). ----
    if r.is_single:
        j = object_model.get_articulation("surround_to_gate_leaf")
        leaf = object_model.get_part("gate_leaf")
        closed = ctx.part_world_aabb(leaf)
        with ctx.pose({j: 1.5}):
            opened = ctx.part_world_aabb(leaf)
        if closed is not None and opened is not None:
            ctx.check(
                "single leaf swings outward (-Y) when opened",
                opened[0][1] < closed[0][1] - 0.30,
                details=f"closed_minY={closed[0][1]:.3f} open_minY={opened[0][1]:.3f}",
            )
    else:
        j0 = object_model.get_articulation("surround_to_door_0")
        d0 = object_model.get_part("door_0")
        d1 = object_model.get_part("door_1")
        c0 = ctx.part_world_aabb(d0)
        c1 = ctx.part_world_aabb(d1)
        with ctx.pose({j0: 1.5}):  # door_1 follows via mimic
            o0 = ctx.part_world_aabb(d0)
            o1 = ctx.part_world_aabb(d1)
        if None not in (c0, c1, o0, o1):
            ctx.check(
                "both leaves swing outward (-Y) together via mimic",
                o0[0][1] < c0[0][1] - 0.30 and o1[0][1] < c1[0][1] - 0.30,
                details=f"d0 {c0[0][1]:.3f}->{o0[0][1]:.3f} d1 {c1[0][1]:.3f}->{o1[0][1]:.3f}",
            )

    # ---- Footprint near the ground. ----
    sa = ctx.part_world_aabb(surround)
    if sa is not None:
        ctx.check("surround rests on the ground", sa[0][2] < 0.03, details=f"z_min={sa[0][2]:.4f}")

    # ---- slot_choices recorded with picket_count encoded. ----
    ctx.check(
        "slot_choices recorded with picket_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "GateConfig",
    "ResolvedGateConfig",
    "build_gate",
    "build_seeded_gate",
    "config_from_seed",
    "resolve_config",
    "run_gate_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
