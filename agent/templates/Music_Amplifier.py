# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``guitar_amplifier``.

Follows ``articraft_template_authoring/specs_modular_v1/Music_Amplifier.md``.

A mini guitar amplifier (combo / head / mini half-stack / tilt-back wedge): a
rectangular vinyl/tolex cabinet with a front speaker baffle (perforated / woven
cloth / open-bar+round-drivers / 2x2 grid grille), a control panel (top recess /
front strip / chamfer facet / slanted wedge top) carrying a centered row of
2-6 CONTINUOUS rotary knobs spinning about the panel-mount normal.

World frame convention (shared by all 11 five-star sources):

  * +X is forward — the grille / baffle faces +X.
  * +Y is cabinet width (left/right).
  * +Z is up; the cabinet is centered on the origin (its bottom near -h/2),
    matching every source record.  ``mini_half_stack`` grounds on the speaker
    cabinet, with the head box FIXED on its top face.

Slots (pattern = mixed, root ``body`` / ``speaker_cabinet``):

    cabinet_form (A)            — full_combo / head_unit / mini_half_stack /
                                  tilt_back_wedge
    control_panel_placement (B)— top_recessed / front_faceplate /
                                  angled_chamfer_facet
    grille_style (C)           — perforated_panel / woven_cloth /
                                  dual_round_speakers / quad_grid
    knob_count (N in [2,6])    — multiplicity axis: N CONTINUOUS knob_i

Adopted sources (spec Module Source Index):
S1  rec_marshall-style-mini-guitar-combo-amplifier-black_...34661766 —
    full_combo / top_recessed / perforated_panel + 4-knob CONTINUOUS row.
S2  rec_guitar_amplifier_var_amp_head        — head_unit (front_vent_slots).
S3  rec_guitar_amplifier_var_mini_stack      — mini_half_stack (2-node FIXED).
S4  rec_guitar_amplifier_var_tilt_back_combo — tilt_back_wedge (top-normal axis).
S5  rec_guitar_amplifier_var_front_faceplate — front_faceplate (+X knob axis).
S6  rec_guitar_amplifier_var_angled_chamfer_panel — angled_chamfer_facet.
S7  rec_guitar_amplifier_var_cloth_grille    — woven_cloth basket-weave mesh.
S8  rec_guitar_amplifier_var_dual_round_speakers — open bars + 2 lathe drivers.
S9  rec_guitar_amplifier_var_quad_grille     — 2x2 perforated cells + cross ribs.
S10 rec_guitar_amplifier_var_knobs_n2        — N=2 endpoint (narrow panel).
S11 rec_guitar_amplifier_var_knobs_n6        — N=6 endpoint (wide panel).

Knob joints are intentional press-fit (the knob base seats a hair into the gold
panel).  The two axis-aligned placements (top_recessed +Z, front_faceplate +X)
declare a MatingContract (panel face -> knob base); the two tilted placements
(angled_chamfer_facet, tilt_back_wedge) seat the knob about a non-axis-aligned
normal, so per AUTHORING.md §B they omit the mating field
(grandfathered) and rely on element-scoped allow_overlap + expect_contact —
exactly mirroring each source record's run_tests block.

The PerforatedPanelGeometry boolean is the compile-cost bottleneck, so the
perforation pitch is coarsened (~0.016 m full panel / ~0.013 m quad cell) and
the four quad cells share one boolean-cut mesh (built once, then copied).
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
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    Inertial,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    KnobTopFeature,
    LatheGeometry,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    PerforatedPanelGeometry,
    SlotPatternPanelGeometry,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

CabinetForm = Literal["full_combo", "head_unit", "mini_half_stack", "tilt_back_wedge"]
PanelPlacement = Literal["top_recessed", "front_faceplate", "angled_chamfer_facet"]
GrilleStyle = Literal["perforated_panel", "woven_cloth", "dual_round_speakers", "quad_grid"]
# Resolved grille for the head unit (no speaker section -> vent slots).
ResolvedGrille = Literal[
    "perforated_panel",
    "woven_cloth",
    "dual_round_speakers",
    "quad_grid",
    "front_vent_slots",
]
PaletteStyle = Literal[
    "black_vinyl_gold",
    "tweed_brown",
    "red_tolex_silver",
    "blonde_oxblood",
    "british_blue_gold",
    "silver_face_chrome",
]

CABINET_FORMS: tuple[CabinetForm, ...] = (
    "full_combo",
    "head_unit",
    "mini_half_stack",
    "tilt_back_wedge",
)
PANEL_PLACEMENTS: tuple[PanelPlacement, ...] = (
    "top_recessed",
    "front_faceplate",
    "angled_chamfer_facet",
)
GRILLE_STYLES: tuple[GrilleStyle, ...] = (
    "perforated_panel",
    "woven_cloth",
    "dual_round_speakers",
    "quad_grid",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "black_vinyl_gold",
    "tweed_brown",
    "red_tolex_silver",
    "blonde_oxblood",
    "british_blue_gold",
    "silver_face_chrome",
)

# Slight weighting toward the classic full combo / top panel / perforated /
# 3-4 knob baselines (spec sampler note), but every value keeps real weight so
# the topology pool is exercised within 0-49.
_FORM_WEIGHTS = (0.38, 0.20, 0.22, 0.20)
_PLACEMENT_WEIGHTS = (0.46, 0.28, 0.26)
_GRILLE_WEIGHTS = (0.34, 0.24, 0.21, 0.21)
# knob_count weights per spec section 8: {2:.18, 3:.26, 4:.28, 5:.16, 6:.12}.
_KNOB_COUNTS = (2, 3, 4, 5, 6)
_KNOB_WEIGHTS = (0.18, 0.26, 0.28, 0.16, 0.12)

N_MIN = 2
N_MAX = 6

# tilt_back_wedge only supports the simple Y-rotated planar grilles on its
# tilted baffle; dual_round / quad fall back to perforated_panel (spec sec 11).
_TILT_GRILLES: tuple[ResolvedGrille, ...] = ("perforated_panel", "woven_cloth")

# Knob motion (shared by all 11 sources).
_KNOB_EFFORT = 0.3
_KNOB_VELOCITY = 8.0

# tilt-back wedge baffle tilt (from vertical), from S4.
_BAFFLE_TILT = math.radians(14.0)
# chamfer facet (S6): equal 30 mm cuts -> 45 deg facet.
_CHAMFER_FRAC = 0.30  # chamfer extent as fraction of cabinet depth/height


# --------------------------------------------------------------------------- #
# Palettes (spec section 7). Only material rgba changes between colorways;
# topology / dimensions / interfaces are identical.
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_vinyl_gold": {
        "vinyl": (0.07, 0.07, 0.08, 1.0),
        "panel": (0.86, 0.62, 0.18, 1.0),
        "grille": (0.10, 0.10, 0.11, 1.0),
        "piping": (0.92, 0.92, 0.90, 1.0),
        "logo": (0.95, 0.93, 0.86, 1.0),
        "knob": (0.78, 0.78, 0.80, 1.0),
        "led": (0.85, 0.12, 0.10, 1.0),
        "trim": (0.04, 0.04, 0.05, 1.0),
        "speaker": (0.14, 0.13, 0.12, 1.0),
        "baffle": (0.06, 0.06, 0.07, 1.0),
    },
    "tweed_brown": {
        "vinyl": (0.74, 0.62, 0.38, 1.0),
        "panel": (0.55, 0.55, 0.57, 1.0),
        "grille": (0.30, 0.16, 0.12, 1.0),
        "piping": (0.32, 0.22, 0.12, 1.0),
        "logo": (0.78, 0.60, 0.22, 1.0),
        "knob": (0.10, 0.10, 0.11, 1.0),
        "led": (0.85, 0.12, 0.10, 1.0),
        "trim": (0.20, 0.14, 0.09, 1.0),
        "speaker": (0.16, 0.12, 0.10, 1.0),
        "baffle": (0.18, 0.12, 0.08, 1.0),
    },
    "red_tolex_silver": {
        "vinyl": (0.45, 0.06, 0.07, 1.0),
        "panel": (0.80, 0.81, 0.83, 1.0),
        "grille": (0.55, 0.55, 0.55, 1.0),
        "piping": (0.92, 0.92, 0.90, 1.0),
        "logo": (0.93, 0.93, 0.93, 1.0),
        "knob": (0.82, 0.83, 0.85, 1.0),
        "led": (0.85, 0.12, 0.10, 1.0),
        "trim": (0.06, 0.04, 0.04, 1.0),
        "speaker": (0.18, 0.18, 0.18, 1.0),
        "baffle": (0.10, 0.06, 0.06, 1.0),
    },
    "blonde_oxblood": {
        "vinyl": (0.80, 0.74, 0.58, 1.0),
        "panel": (0.50, 0.50, 0.52, 1.0),
        "grille": (0.34, 0.12, 0.10, 1.0),
        "piping": (0.30, 0.20, 0.12, 1.0),
        "logo": (0.74, 0.58, 0.22, 1.0),
        "knob": (0.10, 0.10, 0.11, 1.0),
        "led": (0.85, 0.12, 0.10, 1.0),
        "trim": (0.22, 0.16, 0.10, 1.0),
        "speaker": (0.20, 0.10, 0.09, 1.0),
        "baffle": (0.22, 0.10, 0.08, 1.0),
    },
    "british_blue_gold": {
        "vinyl": (0.10, 0.16, 0.34, 1.0),
        "panel": (0.86, 0.62, 0.18, 1.0),
        "grille": (0.18, 0.18, 0.20, 1.0),
        "piping": (0.92, 0.92, 0.90, 1.0),
        "logo": (0.95, 0.93, 0.86, 1.0),
        "knob": (0.78, 0.78, 0.80, 1.0),
        "led": (0.85, 0.12, 0.10, 1.0),
        "trim": (0.04, 0.04, 0.06, 1.0),
        "speaker": (0.14, 0.14, 0.16, 1.0),
        "baffle": (0.08, 0.10, 0.16, 1.0),
    },
    "silver_face_chrome": {
        "vinyl": (0.07, 0.07, 0.08, 1.0),
        "panel": (0.85, 0.86, 0.88, 1.0),
        "grille": (0.40, 0.43, 0.50, 1.0),
        "piping": (0.70, 0.70, 0.72, 1.0),
        "logo": (0.90, 0.90, 0.92, 1.0),
        "knob": (0.82, 0.83, 0.85, 1.0),
        "led": (0.10, 0.55, 0.55, 1.0),
        "trim": (0.04, 0.04, 0.05, 1.0),
        "speaker": (0.16, 0.17, 0.18, 1.0),
        "baffle": (0.10, 0.11, 0.13, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Per-form base geometry (meters, pre-scale).
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _FormBase:
    w: float  # cabinet width (Y)
    d: float  # cabinet depth (X)
    h: float  # cabinet height (Z) — main box / speaker cabinet
    head_h: float  # head box height (mini_half_stack only)
    h_front: float  # wedge front height (tilt_back only)
    h_rear: float  # wedge rear height (tilt_back only)
    base_panel_w: float  # nominal gold-panel span (Y)
    panel_x: float  # panel center X (toward the rear)


_FORM_BASE: dict[CabinetForm, _FormBase] = {
    # S1: 0.18 x 0.10 x 0.18 combo.
    "full_combo": _FormBase(0.180, 0.100, 0.180, 0.0, 0.0, 0.0, 0.150, 0.012),
    # S2: 0.24 x 0.14 x 0.095 low/wide/shallow head.
    "head_unit": _FormBase(0.240, 0.140, 0.095, 0.0, 0.0, 0.0, 0.200, 0.020),
    # S3: speaker 0.18x0.10x0.13 + head 0.18x0.10x0.07.
    "mini_half_stack": _FormBase(0.180, 0.100, 0.130, 0.070, 0.0, 0.0, 0.150, 0.012),
    # S4: 0.18 x 0.16 wedge, front 0.155 / rear 0.195.
    "tilt_back_wedge": _FormBase(0.180, 0.160, 0.195, 0.0, 0.155, 0.195, 0.150, 0.0),
}

_PANEL_D = 0.060  # panel extent along X (toward rear) — all forms
_PANEL_THICK = 0.004
_KNOB_DIAM0 = 0.018
_KNOB_H0 = 0.014


# --------------------------------------------------------------------------- #
# Config dataclasses.
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class GuitarAmplifierConfig:
    cabinet_form: CabinetForm = "full_combo"
    control_panel_placement: PanelPlacement = "top_recessed"
    grille_style: GrilleStyle = "perforated_panel"
    knob_count: int = 4
    palette_style: PaletteStyle = "black_vinyl_gold"
    overall_size_scale: float = 1.0
    cabinet_aspect_scale: float = 1.0
    panel_width_scale: float = 1.0
    knob_diam_scale: float = 1.0
    baffle_inset_scale: float = 1.0
    name: str = "reference_guitar_amplifier"


@dataclass(frozen=True)
class ResolvedGuitarAmplifierConfig:
    cabinet_form: CabinetForm
    control_panel_placement: PanelPlacement
    grille_style: ResolvedGrille
    knob_count: int
    palette_style: PaletteStyle
    name: str
    palette: dict[str, tuple[float, float, float, float]]
    # scales
    s: float
    asp: float
    baffle_inset: float
    # cabinet dims (scaled)
    w: float
    d: float
    h: float
    head_h: float
    h_front: float
    h_rear: float
    panel_x: float
    panel_d: float
    panel_thick: float
    # knob row (resolved)
    knob_diam: float
    knob_h: float
    knob_pitch: float
    knob_ys: tuple[float, ...]
    panel_w: float


def _panel_recess(r: ResolvedGuitarAmplifierConfig) -> float:
    """Top-recess depth (the gold panel sits this far below the cabinet top)."""
    return 0.012 * r.s


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


# --------------------------------------------------------------------------- #
# Seed sampling.
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> GuitarAmplifierConfig:
    """Deterministic per-seed sampling. ``seed=0`` is not special.

    Each seed independently samples cabinet_form (A), panel placement (B),
    grille style (C), knob_count (N), a colorway, and the five continuous
    scales. Compatibility gating (A=mini/head/tilt force the panel placement;
    A=head -> vent grille; tilt drops dual/quad; N row-fit) is resolved in
    ``resolve_config``.
    """
    rng = random.Random(seed)
    form = rng.choices(CABINET_FORMS, weights=_FORM_WEIGHTS, k=1)[0]
    placement = rng.choices(PANEL_PLACEMENTS, weights=_PLACEMENT_WEIGHTS, k=1)[0]
    grille = rng.choices(GRILLE_STYLES, weights=_GRILLE_WEIGHTS, k=1)[0]
    knob_count = rng.choices(_KNOB_COUNTS, weights=_KNOB_WEIGHTS, k=1)[0]
    palette = rng.choice(PALETTE_STYLES)
    return GuitarAmplifierConfig(
        cabinet_form=form,
        control_panel_placement=placement,
        grille_style=grille,
        knob_count=knob_count,
        palette_style=palette,
        overall_size_scale=round(rng.uniform(0.85, 1.20), 4),
        cabinet_aspect_scale=round(rng.uniform(0.88, 1.15), 4),
        panel_width_scale=round(rng.uniform(0.90, 1.12), 4),
        knob_diam_scale=round(rng.uniform(0.85, 1.15), 4),
        baffle_inset_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_guitar_amplifier_{seed}",
    )


def _resolve_knob_row(
    knob_count: int,
    knob_diam0: float,
    base_panel_w: float,
    cab_w: float,
    s: float,
) -> tuple[int, float, float, float, tuple[float, ...]]:
    """Solve the centered knob-row layout for N knobs (spec section 7).

    Returns (N, knob_diam, knob_pitch, panel_w, knob_ys). Shrinks the knob
    diameter (then, as a last resort, N) so the row never overflows the gold
    panel or lets adjacent knobs interpenetrate.
    """
    edge = 0.008 * s
    diam = knob_diam0 * s
    diam_floor = 0.011 * s
    max_panel_w = cab_w - 2.0 * 0.015 * s
    n = int(knob_count)

    def needed_width(nn: float, dd: float) -> float:
        pitch = dd + 0.004 * s  # adjacent non-overlap pitch
        return (nn - 1) * pitch + dd + 2.0 * edge

    while needed_width(n, diam) > max_panel_w:
        if diam > diam_floor:
            diam = max(diam_floor, diam * 0.94)
        elif n > N_MIN:
            n -= 1
        else:
            break
    min_pitch = diam + 0.004 * s
    base_pw = base_panel_w * s
    panel_w = _clamp(base_pw, needed_width(n, diam), max_panel_w)
    if n > 1:
        pitch = (panel_w - diam - 2.0 * edge) / (n - 1)
        pitch = max(pitch, min_pitch)
    else:
        pitch = 0.0
    knob_ys = tuple(-0.5 * (n - 1) * pitch + i * pitch for i in range(n))
    return n, diam, pitch, panel_w, knob_ys


def resolve_config(config: GuitarAmplifierConfig | None = None) -> ResolvedGuitarAmplifierConfig:
    cfg = config or GuitarAmplifierConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    form = _pick(cfg.cabinet_form, CABINET_FORMS)
    placement = _pick(cfg.control_panel_placement, PANEL_PLACEMENTS)
    grille: ResolvedGrille = _pick(cfg.grille_style, GRILLE_STYLES)

    base = _FORM_BASE[form]
    s = _clamp(cfg.overall_size_scale, 0.85, 1.20)
    asp = _clamp(cfg.cabinet_aspect_scale, 0.88, 1.15)
    panel_width_scale = _clamp(cfg.panel_width_scale, 0.90, 1.12)
    knob_diam_scale = _clamp(cfg.knob_diam_scale, 0.85, 1.15)
    baffle_inset = _clamp(cfg.baffle_inset_scale, 0.90, 1.10)

    # --- Compatibility gating (spec section 9). ---
    # mini_half_stack: panel rides the head box top -> top_recessed only.
    if form == "mini_half_stack":
        placement = "top_recessed"
    # tilt_back_wedge: the panel is the wedge's own slanted top (knob axis =
    # top-surface normal). Recorded as top_recessed (its equivalent placement).
    if form == "tilt_back_wedge":
        placement = "top_recessed"
        if grille not in _TILT_GRILLES:
            grille = "perforated_panel"
    # head_unit: no speaker section -> front vent slots, panel stays on top.
    if form == "head_unit":
        placement = "top_recessed"
        grille = "front_vent_slots"
    # The two visible round drivers / 2x2 cell grid only read on a full front
    # baffle (their 5-star sources S8/S9 are both top_recessed combos). On the
    # reduced front face under a front strip / chamfer facet they fall back to a
    # single perforated panel (spec sec 11).
    if placement in ("front_faceplate", "angled_chamfer_facet") and grille in (
        "dual_round_speakers",
        "quad_grid",
    ):
        grille = "perforated_panel"

    # --- Cabinet dims (scaled). asp scales heights only (H/W ratio). ---
    w = base.w * s
    d = base.d * s
    h = base.h * s * asp
    head_h = base.head_h * s * asp
    h_front = base.h_front * s * asp
    h_rear = base.h_rear * s * asp
    cab_w = w

    knob_count, knob_diam, knob_pitch, panel_w, knob_ys = _resolve_knob_row(
        cfg.knob_count if cfg.knob_count is not None else 4,
        _KNOB_DIAM0 * knob_diam_scale,
        base.base_panel_w * panel_width_scale,
        cab_w,
        s,
    )

    return ResolvedGuitarAmplifierConfig(
        cabinet_form=form,
        control_panel_placement=placement,
        grille_style=grille,
        knob_count=knob_count,
        palette_style=palette_style,
        name=cfg.name or "guitar_amplifier",
        palette=dict(PALETTES[palette_style]),
        s=s,
        asp=asp,
        baffle_inset=baffle_inset,
        w=w,
        d=d,
        h=h,
        head_h=head_h,
        h_front=h_front,
        h_rear=h_rear,
        panel_x=base.panel_x * s,
        panel_d=_PANEL_D * s,
        panel_thick=_PANEL_THICK * s,
        knob_diam=knob_diam,
        knob_h=_KNOB_H0 * s,
        knob_pitch=knob_pitch,
        knob_ys=knob_ys,
        panel_w=panel_w,
    )


def slot_choices_for_config(
    config: GuitarAmplifierConfig | ResolvedGuitarAmplifierConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedGuitarAmplifierConfig) else resolve_config(config)
    return (
        ("cabinet_form", r.cabinet_form),
        ("control_panel_placement", r.control_panel_placement),
        ("grille_style", r.grille_style),
        ("knob_count", f"n{r.knob_count}"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Materials.
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject, r: ResolvedGuitarAmplifierConfig) -> dict:
    out = {}
    for role, rgba in r.palette.items():
        out[role] = model.material(f"amp_{role}_{r.palette_style}", rgba=rgba)
    return out


# --------------------------------------------------------------------------- #
# Knob geometry (shared across all 11 sources).
# --------------------------------------------------------------------------- #
def _make_knob_geo(r: ResolvedGuitarAmplifierConfig, *, rot_y: float | None = None) -> KnobGeometry:
    s = r.s
    kg = KnobGeometry(
        r.knob_diam,
        r.knob_h,
        body_style="cylindrical",
        edge_radius=0.0008,
        grip=KnobGrip(style="knurled", count=28, depth=0.0008),
        indicator=KnobIndicator(
            style="line", mode="raised", length=0.009 * s, width=0.0014, depth=0.0010
        ),
        top_feature=KnobTopFeature(
            style="recessed_disk",
            diameter=min(0.010 * s, r.knob_diam * 0.6),
            depth=0.0008,
        ),
        center=False,  # mounting face at z=0
    )
    # Off-axis raised pointer tab: makes the knob visibly non-axisymmetric so a
    # CONTINUOUS spin is observable (spec multiplicity contract).
    pointer = BoxGeometry((0.0030 * s, 0.0060 * s, 0.0024 * s))
    pointer.translate(0.0, r.knob_diam / 2.0 - 0.0010 * s, r.knob_h + 0.0008 * s)
    kg.merge(pointer)
    if rot_y is not None:
        kg.rotate_y(rot_y)
    return kg


def _attach_knob_row(
    model: ArticulatedObject,
    parent_part,
    r: ResolvedGuitarAmplifierConfig,
    mats: dict,
    *,
    joint_prefix: str,
    seats: list[tuple[float, float, float]],
    axis: tuple[float, float, float],
    rot_y: float | None,
    mating_parent_side: str | None,
    mating_child_side: str | None,
) -> None:
    """Attach N knob parts, each a CONTINUOUS joint about ``axis``.

    The axis-aligned placements pass a MatingContract (panel face -> knob base);
    tilted placements pass ``mating_parent_side=None`` (grandfathered).
    """
    for i, (ox, oy, oz) in enumerate(seats):
        kg = _make_knob_geo(r, rot_y=rot_y)
        kp = model.part(f"knob_{i}")
        kp.visual(mesh_from_geometry(kg, f"knob_{i}"), material=mats["knob"], name=f"knob_{i}", material_class_id="plastic.opaque_glossy_molded")
        kp.inertial = Inertial.from_geometry(Cylinder(r.knob_diam / 2.0, r.knob_h), mass=0.01)
        mating = None
        if mating_parent_side is not None and mating_child_side is not None:
            mating = MatingContract(
                parent_face_geometry="gold_panel",
                parent_face_side=mating_parent_side,
                child_face_geometry=f"knob_{i}",
                child_face_side=mating_child_side,
                contact_tol=0.0015,
            )
        model.articulation(
            f"{joint_prefix}_to_knob_{i}",
            ArticulationType.CONTINUOUS,
            parent=parent_part,
            child=kp,
            origin=Origin(xyz=(ox, oy, oz)),
            axis=axis,
            motion_limits=MotionLimits(effort=_KNOB_EFFORT, velocity=_KNOB_VELOCITY),
            mating=mating,
        )


# --------------------------------------------------------------------------- #
# CadQuery cabinet solids.
# --------------------------------------------------------------------------- #
def _rounded_box(w_y: float, d_x: float, h_z: float, fillet: float) -> cq.Workplane:
    wp = cq.Workplane("XY").box(d_x, w_y, h_z)
    try:
        wp = wp.edges("|Z").fillet(min(fillet, 0.45 * min(d_x, w_y, h_z)))
    except Exception:
        pass
    return wp


def _box_cabinet_solid(
    r: ResolvedGuitarAmplifierConfig,
    *,
    w: float,
    d: float,
    h: float,
    placement: PanelPlacement,
    front_kind: str,
    z_off: float = 0.0,
):
    """Box cabinet with the panel mount (top recess / chamfer facet / plain top)
    and front treatment (grille pocket / vent recess). ``z_off`` shifts the box
    so a head box sits with its base at z=0."""
    s = r.s
    fillet = 0.010 * s
    front_x = d / 2.0
    top_z = h / 2.0 + z_off
    outer = _rounded_box(w, d, h, fillet).translate((0.0, 0.0, z_off))

    body = outer
    if placement == "top_recessed":
        recess = (
            cq.Workplane("XY")
            .box(r.panel_d, r.panel_w + 0.010 * s, _panel_recess(r) * 2.2)
            .translate((r.panel_x, 0.0, top_z))
        )
        body = body.cut(recess)
    elif placement == "angled_chamfer_facet":
        ch_dx = _CHAMFER_FRAC * d
        ch_dz = _CHAMFER_FRAC * d  # equal -> 45 deg facet
        pad = 0.005 * s
        wedge = (
            cq.Workplane("XZ")
            .moveTo(front_x - ch_dx, top_z)
            .lineTo(front_x + pad, top_z + pad)
            .lineTo(front_x + pad, top_z - ch_dz)
            .close()
            .extrude(w, both=True)
        )
        body = body.cut(wedge)

    if front_kind == "grille":
        grille_pocket = (
            cq.Workplane("XY")
            .box(0.012 * s, w - 0.024 * s, h - 0.024 * s)
            .translate((front_x, 0.0, z_off))
        )
        body = body.cut(grille_pocket)
    elif front_kind == "vent":
        vent_depth = 0.006 * s
        vent_w = min(0.100 * s, w - 0.040 * s)
        vent_h = 0.020 * s
        vent_z = top_z - 0.022 * s
        vent = (
            cq.Workplane("XY")
            .box(vent_depth, vent_w, vent_h)
            .translate((front_x - vent_depth / 2.0, 0.0, vent_z))
        )
        body = body.cut(vent)
    return body


def _wedge_geom(r: ResolvedGuitarAmplifierConfig):
    """Trapezoidal wedge cross-section points + baffle/top normals (S4)."""
    d = r.d
    half_d = d / 2.0
    h_front = r.h_front
    h_rear = r.h_rear
    z_bot = -h_rear / 2.0
    setback = h_front * math.tan(_BAFFLE_TILT)
    pt_a = (-half_d, z_bot)  # rear-bottom
    pt_b = (half_d, z_bot)  # front-bottom
    pt_c = (half_d - setback, z_bot + h_front)  # front-top
    pt_d = (-half_d, z_bot + h_rear)  # rear-top
    # baffle (B->C) outward normal
    bdx, bdz = pt_c[0] - pt_b[0], pt_c[1] - pt_b[1]
    blen = math.hypot(bdx, bdz)
    baffle_nx, baffle_nz = bdz / blen, -bdx / blen
    baffle_cx, baffle_cz = (pt_b[0] + pt_c[0]) / 2.0, (pt_b[1] + pt_c[1]) / 2.0
    # top (C->D) outward normal
    tdx, tdz = pt_d[0] - pt_c[0], pt_d[1] - pt_c[1]
    tlen = math.hypot(tdx, tdz)
    top_nx, top_nz = tdz / tlen, -tdx / tlen
    top_angle = math.atan2(top_nx, top_nz)
    return {
        "pt_a": pt_a,
        "pt_b": pt_b,
        "pt_c": pt_c,
        "pt_d": pt_d,
        "blen": blen,
        "baffle_nx": baffle_nx,
        "baffle_nz": baffle_nz,
        "baffle_cx": baffle_cx,
        "baffle_cz": baffle_cz,
        "top_nx": top_nx,
        "top_nz": top_nz,
        "top_angle": top_angle,
    }


def _wedge_solid(r: ResolvedGuitarAmplifierConfig):
    g = _wedge_geom(r)
    half_w = r.w / 2.0
    profile = (
        cq.Workplane("XY")
        .moveTo(*g["pt_a"])
        .lineTo(*g["pt_b"])
        .lineTo(*g["pt_c"])
        .lineTo(*g["pt_d"])
        .close()
    )
    wedge = profile.extrude(r.w).translate((0, 0, -half_w)).rotate((0, 0, 0), (1, 0, 0), 90)
    try:
        wedge = wedge.edges("|Y").fillet(0.005 * r.s)
    except Exception:
        pass
    return wedge


# --------------------------------------------------------------------------- #
# Carry handle (cadquery arched strap).
# --------------------------------------------------------------------------- #
def _handle_mesh(r: ResolvedGuitarAmplifierConfig, *, strap_x: float, z0: float, span: float):
    s = r.s
    arch = 0.020 * s
    n = 13
    pts = []
    for i in range(n):
        t = i / (n - 1)
        y = -span / 2.0 + t * span
        zz = z0 + arch * (1.0 - (2.0 * t - 1.0) ** 2) + 0.002 * s
        pts.append((strap_x, y, zz))
    path = cq.Workplane().add(cq.Edge.makeSpline([cq.Vector(*p) for p in pts]))
    profile = cq.Workplane("XZ").center(strap_x, pts[0][2]).rect(0.018 * s, 0.007 * s)
    strap = profile.sweep(path, multisection=False, makeSolid=True)
    result = strap
    for y in (-span / 2.0, span / 2.0):
        mount = (
            cq.Workplane("XY")
            .box(0.024 * s, 0.018 * s, 0.014 * s)
            .translate((strap_x, y, z0 - 0.004 * s))
        )
        result = result.union(mount)
    return mesh_from_cadquery(result, "handle")


# --------------------------------------------------------------------------- #
# Front decorations (piping / logo / corner caps). +X facing, planar.
# --------------------------------------------------------------------------- #
def _emit_piping(body, r, mats, *, front_x, span_w, span_h, center_z):
    s = r.s
    pip_t = 0.005 * s
    pip_w = 0.006 * s
    fx = front_x - 0.001 * s
    for i, zc in enumerate((center_z + span_h / 2.0, center_z - span_h / 2.0)):
        bar = BoxGeometry((pip_t, span_w, pip_w))
        bar.translate(fx, 0.0, zc)
        body.visual(
            mesh_from_geometry(bar, f"piping_h_{i}"), material=mats["piping"], name=f"piping_h_{i}", material_class_id="plastic.opaque_glossy_molded"
        )
    for i, yc in enumerate((span_w / 2.0, -span_w / 2.0)):
        bar = BoxGeometry((pip_t, pip_w, span_h))
        bar.translate(fx, yc, center_z)
        body.visual(
            mesh_from_geometry(bar, f"piping_v_{i}"), material=mats["piping"], name=f"piping_v_{i}", material_class_id="plastic.opaque_glossy_molded"
        )


def _emit_logo(body, r, mats, *, x_back, y, z):
    s = r.s
    logo = BoxGeometry((0.004 * s, 0.080 * s, 0.022 * s))
    logo.translate(x_back + 0.002 * s, y, z)
    body.visual(
        mesh_from_geometry(logo, "marshall_logo"), material=mats["logo"], name="marshall_logo", appearance_only=AppearanceOnlySpec(kind="decal")
    )


def _emit_corner_caps(body, r, mats, *, front_x, cap_y, cap_zs):
    s = r.s
    for iy, yc in enumerate((-cap_y, cap_y)):
        for iz, zc in enumerate(cap_zs):
            cap = BoxGeometry((0.018 * s, 0.016 * s, 0.016 * s))
            cap.translate(front_x - 0.006 * s, yc, zc)
            body.visual(
                mesh_from_geometry(cap, f"corner_cap_{iy}_{iz}"),
                material=mats["trim"],
                name=f"corner_cap_{iy}_{iz}", material_class_id="plastic.opaque_glossy_molded",
            )


# --------------------------------------------------------------------------- #
# Woven cloth grille (S7) — direct mesh (no boolean).
# --------------------------------------------------------------------------- #
def _add_rotated_box(mesh, x_c, y_c, z_c, angle, sx, sy, sz):
    c, s = math.cos(angle), math.sin(angle)
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    corners = []
    for dx in (-hx, hx):
        for dy in (-hy, hy):
            for dz in (-hz, hz):
                ry = dy * c - dz * s
                rz = dy * s + dz * c
                corners.append((x_c + dx, y_c + ry, z_c + rz))
    base = len(mesh.vertices)
    for v in corners:
        mesh.add_vertex(*v)
    tris = [
        (0, 2, 1),
        (1, 2, 3),
        (4, 5, 6),
        (5, 7, 6),
        (0, 1, 4),
        (1, 5, 4),
        (2, 6, 3),
        (3, 6, 7),
        (0, 4, 2),
        (2, 4, 6),
        (1, 3, 5),
        (3, 7, 5),
    ]
    for a, b, cc in tris:
        mesh.add_face(base + a, base + b, base + cc)


def _woven_grille_mesh(r, *, cloth_x, cloth_w, cloth_h) -> MeshGeometry:
    s = r.s
    cloth_t = 0.002 * s
    rib_width = 0.0035 * s
    rib_relief = 0.0016 * s
    rib_pitch = 0.022 * s
    seg_frac = 0.94
    sq2 = math.sqrt(2.0)
    half_y, half_z = cloth_w / 2.0, cloth_h / 2.0
    mesh = MeshGeometry()
    _add_rotated_box(mesh, cloth_x - cloth_t / 2.0, 0.0, 0.0, 0.0, cloth_t, cloth_w, cloth_h)
    v_max = (half_y + half_z) / sq2
    n_ribs = int(v_max / rib_pitch) + 1
    seg_len = rib_pitch * seg_frac
    x_over = cloth_x + rib_relief / 2.0
    x_under = cloth_x - rib_relief / 2.0
    clip_y, clip_z = half_y - rib_width, half_z - rib_width
    for i in range(-n_ribs, n_ribs + 1):
        for j in range(-n_ribs, n_ribs):
            yc = ((j + 0.5) - i) * rib_pitch / sq2
            zc = (i + (j + 0.5)) * rib_pitch / sq2
            if abs(yc) > clip_y or abs(zc) > clip_z:
                continue
            xc = x_over if ((i + j) % 2 == 0) else x_under
            _add_rotated_box(mesh, xc, yc, zc, math.pi / 4.0, rib_relief, seg_len, rib_width)
    for j in range(-n_ribs, n_ribs + 1):
        for i in range(-n_ribs, n_ribs):
            yc = (j - (i + 0.5)) * rib_pitch / sq2
            zc = ((i + 0.5) + j) * rib_pitch / sq2
            if abs(yc) > clip_y or abs(zc) > clip_z:
                continue
            xc = x_over if ((i + j) % 2 != 0) else x_under
            _add_rotated_box(mesh, xc, yc, zc, -math.pi / 4.0, rib_relief, seg_len, rib_width)
    return mesh


# --------------------------------------------------------------------------- #
# Dual-round speaker driver (S8).
# --------------------------------------------------------------------------- #
def _speaker_driver_geom() -> LatheGeometry:
    profile = [
        (0.000, 0.000),
        (0.003, 0.001),
        (0.006, 0.002),
        (0.009, 0.004),
        (0.011, 0.005),
        (0.017, 0.008),
        (0.023, 0.011),
        (0.027, 0.014),
        (0.029, 0.013),
        (0.031, 0.010),
        (0.032, 0.007),
        (0.031, 0.011),
        (0.030, 0.015),
        (0.033, 0.015),
        (0.033, 0.022),
        (0.020, 0.022),
        (0.020, 0.028),
        (0.000, 0.028),
    ]
    return LatheGeometry(profile, segments=28)


# --------------------------------------------------------------------------- #
# Front grille cluster (Slot C, +X facing). Used by full_combo & mini speaker.
# --------------------------------------------------------------------------- #
def _grille_dims(r, cab_w, region_h):
    side_margin = 0.015 * r.s * r.baffle_inset
    return cab_w - 2.0 * side_margin, region_h - 2.0 * side_margin


def _emit_front_grille(body, r, mats, *, front_x, gw, gh, center_z, grille_style, logo_z):
    """Emit the Slot-C grille cluster on a +X baffle (gw x gh, centered on Z at
    ``center_z``) and the logo. dual_round / quad only occur at center_z=0
    (full front, top_recessed combos), but center_z is applied uniformly."""
    s = r.s
    pocket_inner_x = front_x - 0.006 * s

    if grille_style == "perforated_panel":
        grille = PerforatedPanelGeometry(
            (gh, gw),
            0.006 * s,
            hole_diameter=0.008 * s,
            pitch=0.016 * s,
            frame=0.006 * s,
            stagger=True,
        )
        grille.rotate_y(math.pi / 2.0)
        grille.translate(front_x - 0.004 * s, 0.0, center_z)
        body.visual(
            mesh_from_geometry(grille, "speaker_grille"),
            material=mats["grille"],
            name="speaker_grille", material_class_id="metal.patterned_sheet_panel",
        )
        logo_back = front_x - 0.001 * s

    elif grille_style == "woven_cloth":
        cloth_x = front_x - 0.004 * s
        mesh = _woven_grille_mesh(r, cloth_x=cloth_x, cloth_w=gw, cloth_h=gh)
        mesh.translate(0.0, 0.0, center_z)
        body.visual(
            mesh_from_geometry(mesh, "speaker_grille"),
            material=mats["grille"],
            name="speaker_grille", material_class_id="fabric.open_mesh",
        )
        logo_back = cloth_x + 0.0016 * s

    elif grille_style == "dual_round_speakers":
        baffle_thick = 0.008 * s
        baffle_x = pocket_inner_x - baffle_thick / 2.0
        baffle = BoxGeometry((baffle_thick, gw, gh))
        baffle.translate(baffle_x, 0.0, center_z)
        body.visual(
            mesh_from_geometry(baffle, "baffle_board"), material=mats["baffle"], name="baffle_board", material_class_id="wood.engineered_board"
        )
        spk_r = 0.033 * s
        spk_y = min(0.037 * s, gw / 2.0 - spk_r - 0.002 * s)
        spk_x = front_x - 0.012 * s
        for i, sy in enumerate((-spk_y, spk_y)):
            spk = _speaker_driver_geom()
            spk.scale(s)
            spk.rotate_y(-math.pi / 2.0)
            spk.translate(spk_x, sy, center_z)
            body.visual(
                mesh_from_geometry(spk, f"speaker_{i}"),
                material=mats["speaker"],
                name=f"speaker_{i}", material_class_id="paper.cardboard",
            )
        bar_thick = 0.004 * s
        bar_h = 0.004 * s
        n_bars = 10
        bar_pitch = gh / n_bars
        bar_x = pocket_inner_x + bar_thick / 2.0
        for i in range(n_bars):
            z_pos = center_z - gh / 2.0 + bar_pitch * (i + 0.5)
            bar = BoxGeometry((bar_thick, gw, bar_h))
            bar.translate(bar_x, 0.0, z_pos)
            body.visual(
                mesh_from_geometry(bar, f"grille_bar_{i}"),
                material=mats["grille"],
                name=f"grille_bar_{i}", material_class_id="metal.paint_coated",
            )
        vbar = BoxGeometry((bar_thick, 0.004 * s, gh))
        vbar.translate(bar_x, 0.0, center_z)
        body.visual(
            mesh_from_geometry(vbar, "grille_vert_0"), material=mats["grille"], name="grille_vert_0", material_class_id="metal.paint_coated"
        )
        logo_back = bar_x + bar_thick / 2.0

    else:  # quad_grid
        cell_gap = 0.010 * s
        cell_w = (gw - cell_gap) / 2.0
        cell_h = (gh - cell_gap) / 2.0
        # Build ONE perforated-cell boolean mesh, then copy/translate it 4x
        # (the boolean cut is the compile-cost bottleneck — pay it once).
        base_cell = PerforatedPanelGeometry(
            (cell_h, cell_w),
            0.005 * s,
            hole_diameter=0.007 * s,
            pitch=0.013 * s,
            frame=0.005 * s,
            stagger=True,
        )
        base_cell.rotate_y(math.pi / 2.0)
        pt, pw = 0.004 * s, 0.004 * s
        fx = front_x - 0.001 * s
        for i in range(4):
            row, col = divmod(i, 2)
            cy = (col - 0.5) * (cell_w + cell_gap)
            cz = center_z + (row - 0.5) * (cell_h + cell_gap)
            cell = base_cell.copy()
            cell.translate(front_x - 0.004 * s, cy, cz)
            body.visual(
                mesh_from_geometry(cell, f"grille_cell_{i}"),
                material=mats["grille"],
                name=f"grille_cell_{i}", material_class_id="metal.patterned_sheet_panel",
            )
            for k, dz in enumerate((cell_h / 2.0, -cell_h / 2.0)):
                bar = BoxGeometry((pt, cell_w + pw, pw))
                bar.translate(fx, cy, cz + dz)
                body.visual(
                    mesh_from_geometry(bar, f"cell_pipe_{i}_h{k}"),
                    material=mats["piping"],
                    name=f"cell_pipe_{i}_h{k}", material_class_id="plastic.opaque_glossy_molded",
                )
            for k, dy in enumerate((-cell_w / 2.0, cell_w / 2.0)):
                bar = BoxGeometry((pt, pw, cell_h + pw))
                bar.translate(fx, cy + dy, cz)
                body.visual(
                    mesh_from_geometry(bar, f"cell_pipe_{i}_v{k}"),
                    material=mats["piping"],
                    name=f"cell_pipe_{i}_v{k}", material_class_id="plastic.opaque_glossy_molded",
                )
        rib_d = 0.010 * s
        rib_x = front_x - 0.005 * s
        h_rib = BoxGeometry((rib_d, gw, cell_gap))
        h_rib.translate(rib_x, 0.0, center_z)
        body.visual(
            mesh_from_geometry(h_rib, "grille_rib_h"), material=mats["vinyl"], name="grille_rib_h", material_class_id=("fabric.canvas" if r.palette_style == "tweed_brown" else "plastic.patterned_textured")
        )
        v_rib = BoxGeometry((rib_d, cell_gap, gh))
        v_rib.translate(rib_x, 0.0, center_z)
        body.visual(
            mesh_from_geometry(v_rib, "grille_rib_v"), material=mats["vinyl"], name="grille_rib_v", material_class_id=("fabric.canvas" if r.palette_style == "tweed_brown" else "plastic.patterned_textured")
        )
        logo_back = fx - pt / 2.0

    _emit_logo(body, r, mats, x_back=logo_back, y=-0.006 * s, z=logo_z)


# --------------------------------------------------------------------------- #
# Gold panel + LED emitters (per placement).
# --------------------------------------------------------------------------- #
def _emit_top_panel(part, r, mats, *, top_z):
    """Flat gold panel in the top recess + LED. Returns (knob_seats, axis,
    rot_y, mating_parent_side, mating_child_side)."""
    s = r.s
    pt = r.panel_thick
    gold_z = top_z - _panel_recess(r)  # recess floor
    panel = BoxGeometry((r.panel_d, r.panel_w, pt))
    panel_top = gold_z + pt
    panel.translate(r.panel_x, 0.0, gold_z + pt / 2.0)
    part.visual(mesh_from_geometry(panel, "gold_panel"), material=mats["panel"], name="gold_panel", material_class_id=("metal.brass_polished" if r.palette_style in {"black_vinyl_gold", "british_blue_gold"} else "metal.brushed_silver"))
    led_y = min(0.072 * s, r.panel_w / 2.0 - 0.008 * s)
    led = CylinderGeometry(0.0035 * s, 0.004 * s)
    led.translate(r.panel_x - 0.004 * s, led_y, panel_top - 0.001 * s)
    part.visual(mesh_from_geometry(led, "power_led"), material=mats["led"], name="power_led", material_class_id="tech.emissive_surface")
    knob_x = r.panel_x + 0.004 * s
    seat_z = panel_top - 0.0006 * s
    seats = [(knob_x, ky, seat_z) for ky in r.knob_ys]
    return seats, (0.0, 0.0, 1.0), None, "positive_z", "negative_z"


def _emit_front_panel(part, r, mats, *, front_x, strip_z):
    """Gold strip on the +X front face + LED. Knobs face +X."""
    s = r.s
    pt = r.panel_thick
    strip_h = 0.030 * s
    panel = BoxGeometry((pt, r.panel_w, strip_h))
    panel_cx = front_x - 0.002 * s
    panel.translate(panel_cx, 0.0, strip_z)
    part.visual(mesh_from_geometry(panel, "gold_panel"), material=mats["panel"], name="gold_panel", material_class_id=("metal.brass_polished" if r.palette_style in {"black_vinyl_gold", "british_blue_gold"} else "metal.brushed_silver"))
    panel_front = panel_cx + pt / 2.0
    led_y = min(0.068 * s, r.panel_w / 2.0 - 0.008 * s)
    led = BoxGeometry((0.004 * s, 0.007 * s, 0.007 * s))
    led.translate(front_x + 0.001 * s, led_y, strip_z)
    part.visual(mesh_from_geometry(led, "power_led"), material=mats["led"], name="power_led", material_class_id="tech.emissive_surface")
    seat_x = panel_front - 0.0006 * s
    seats = [(seat_x, ky, strip_z) for ky in r.knob_ys]
    return seats, (1.0, 0.0, 0.0), math.pi / 2.0, "positive_x", "negative_x"


def _emit_facet_panel(part, r, mats, *, front_x, top_z, d):
    """Gold panel on the 45 deg chamfer facet + LED. Knobs about facet normal."""
    s = r.s
    ch_dx = _CHAMFER_FRAC * d
    ch_dz = _CHAMFER_FRAC * d
    facet_angle = math.atan2(ch_dz, ch_dx)
    facet_len = math.hypot(ch_dx, ch_dz)
    facet_cx = front_x - ch_dx / 2.0
    facet_cz = top_z - ch_dz / 2.0
    nx, nz = math.sin(facet_angle), math.cos(facet_angle)
    pt = r.panel_thick
    panel_along = min(r.panel_d, facet_len * 0.85)
    outset = pt / 2.0 - 0.0005 * s
    panel = BoxGeometry((pt, r.panel_w, panel_along))
    panel.rotate_y(-facet_angle)
    panel.translate(facet_cx + outset * nx, 0.0, facet_cz + outset * nz)
    part.visual(mesh_from_geometry(panel, "gold_panel"), material=mats["panel"], name="gold_panel", material_class_id=("metal.brass_polished" if r.palette_style in {"black_vinyl_gold", "british_blue_gold"} else "metal.brushed_silver"))
    led = CylinderGeometry(0.0035 * s, 0.004 * s)
    led.rotate_y(facet_angle)
    led_y = min(0.072 * s, r.panel_w / 2.0 - 0.008 * s)
    panel_outer = outset + pt / 2.0
    led_off = panel_outer + 0.002 * s - 0.0005 * s
    led.translate(facet_cx + led_off * nx, led_y, facet_cz + led_off * nz)
    part.visual(mesh_from_geometry(led, "power_led"), material=mats["led"], name="power_led", material_class_id="tech.emissive_surface")
    seat_off = panel_outer - 0.0008 * s
    seats = [(facet_cx + seat_off * nx, ky, facet_cz + seat_off * nz) for ky in r.knob_ys]
    # Tilted axis -> grandfather mating (non-axis-aligned).
    return seats, (nx, 0.0, nz), facet_angle, None, None


# --------------------------------------------------------------------------- #
# Cabinet builders.
# --------------------------------------------------------------------------- #
def _build_box_combo(model, r, mats):
    """full_combo / head_unit: single ``body`` box cabinet."""
    s = r.s
    is_head = r.cabinet_form == "head_unit"
    front_kind = "vent" if is_head else "grille"
    front_x = r.d / 2.0
    top_z = r.h / 2.0

    body = model.part("body")
    cab = _box_cabinet_solid(
        r, w=r.w, d=r.d, h=r.h, placement=r.control_panel_placement, front_kind=front_kind
    )
    body.visual(mesh_from_cadquery(cab, "cabinet"), material=mats["vinyl"], name="cabinet", material_class_id=("fabric.canvas" if r.palette_style == "tweed_brown" else "plastic.patterned_textured"))
    body.inertial = Inertial.from_geometry(Box((r.d, r.w, r.h)), mass=2.4)

    # --- Panel + knob mount ---
    if r.control_panel_placement == "top_recessed":
        seats, axis, rot_y, mps, mcs = _emit_top_panel(body, r, mats, top_z=top_z)
        handle_x = r.panel_x - r.panel_d / 2.0 - 0.016 * s
    elif r.control_panel_placement == "front_faceplate":
        strip_z = top_z - 0.027 * s if not is_head else top_z - 0.020 * s
        seats, axis, rot_y, mps, mcs = _emit_front_panel(
            body, r, mats, front_x=front_x, strip_z=strip_z
        )
        handle_x = 0.0
    else:  # angled_chamfer_facet
        seats, axis, rot_y, mps, mcs = _emit_facet_panel(
            body, r, mats, front_x=front_x, top_z=top_z, d=r.d
        )
        handle_x = front_x - _CHAMFER_FRAC * r.d - 0.020 * s

    # --- Front baffle: grille (combo) or vent slots (head) ---
    if is_head:
        vent_z = top_z - 0.022 * s
        vent = SlotPatternPanelGeometry(
            (min(0.096 * s, r.w - 0.044 * s), 0.018 * s),
            0.004 * s,
            slot_size=(0.030 * s, 0.003 * s),
            pitch=(0.036 * s, 0.006 * s),
            frame=0.003 * s,
            stagger=False,
        )
        vent.rotate_y(math.pi / 2.0)
        vent.translate(front_x - 0.004 * s, 0.0, vent_z)
        body.visual(
            mesh_from_geometry(vent, "front_vent_slots"),
            material=mats["baffle"],
            name="front_vent_slots", material_class_id="metal.patterned_sheet_panel",
        )
        _emit_logo(body, r, mats, x_back=front_x - 0.001 * s, y=0.0, z=-0.012 * s)
        _emit_piping(
            body,
            r,
            mats,
            front_x=front_x,
            span_w=r.w - 0.020 * s,
            span_h=r.h - 0.020 * s,
            center_z=0.0,
        )
    elif r.control_panel_placement == "top_recessed":
        gw, gh = _grille_dims(r, r.w, r.h)
        _emit_front_grille(
            body,
            r,
            mats,
            front_x=front_x,
            gw=gw,
            gh=gh,
            center_z=0.0,
            grille_style=r.grille_style,
            logo_z=-0.046 * s,
        )
        _emit_piping(
            body,
            r,
            mats,
            front_x=front_x,
            span_w=r.w - 0.020 * s,
            span_h=r.h - 0.020 * s,
            center_z=0.0,
        )
    elif r.control_panel_placement == "front_faceplate":
        # grille sits below the front strip
        strip_z = top_z - 0.027 * s
        grille_top = strip_z - 0.015 * s - 0.008 * s
        grille_bot = -(r.h / 2.0 - 0.015 * s)
        gcz = (grille_top + grille_bot) / 2.0
        region_h = grille_top - grille_bot
        gw, gh = _grille_dims(r, r.w, region_h)
        _emit_front_grille(
            body,
            r,
            mats,
            front_x=front_x,
            gw=gw,
            gh=gh,
            center_z=gcz,
            grille_style=r.grille_style,
            logo_z=gcz - gh * 0.30,
        )
        _emit_piping(
            body,
            r,
            mats,
            front_x=front_x,
            span_w=gw + 0.012 * s,
            span_h=gh + 0.012 * s,
            center_z=gcz,
        )
    else:  # angled_chamfer_facet
        ch_dz = _CHAMFER_FRAC * r.d
        front_face_h = r.h - ch_dz
        gcz = -ch_dz / 2.0
        gw, gh = _grille_dims(r, r.w, front_face_h)
        _emit_front_grille(
            body,
            r,
            mats,
            front_x=front_x,
            gw=gw,
            gh=gh,
            center_z=gcz,
            grille_style=r.grille_style,
            logo_z=gcz - gh * 0.30,
        )
        _emit_piping(
            body,
            r,
            mats,
            front_x=front_x,
            span_w=r.w - 0.020 * s,
            span_h=front_face_h - 0.020 * s,
            center_z=gcz,
        )

    # corner caps + handle
    cap_y = r.w / 2.0 - 0.006 * s
    cap_z = r.h / 2.0 - 0.006 * s
    if r.control_panel_placement == "angled_chamfer_facet":
        cap_zs = (-(r.h / 2.0) + 0.006 * s, (r.h / 2.0 - _CHAMFER_FRAC * r.d) - 0.006 * s)
    else:
        cap_zs = (-cap_z, cap_z)
    _emit_corner_caps(body, r, mats, front_x=front_x, cap_y=cap_y, cap_zs=cap_zs)
    handle_span = min(0.140 * s if is_head else 0.104 * s, r.w - 0.040 * s)
    handle_z0 = top_z if r.control_panel_placement != "angled_chamfer_facet" else top_z
    body.visual(
        _handle_mesh(r, strap_x=handle_x, z0=handle_z0, span=handle_span),
        material=mats["trim"],
        name="handle", material_class_id="plastic.opaque_glossy_molded",
    )

    _attach_knob_row(
        model,
        body,
        r,
        mats,
        joint_prefix="panel",
        seats=seats,
        axis=axis,
        rot_y=rot_y,
        mating_parent_side=mps,
        mating_child_side=mcs,
    )


def _build_mini_stack(model, r, mats):
    """mini_half_stack: speaker_cabinet (root) + head_box (FIXED child)."""
    s = r.s
    spk_w, spk_d, spk_h = r.w, r.d, r.h
    head_w, head_d, head_h = r.w, r.d, r.head_h
    front_x = spk_d / 2.0

    # --- speaker cabinet (root) ---
    speaker = model.part("speaker_cabinet")
    cab = _rounded_box(spk_w, spk_d, spk_h, 0.008 * s)
    cab_pocket = (
        cq.Workplane("XY")
        .box(0.012 * s, spk_w - 0.024 * s, spk_h - 0.024 * s)
        .translate((front_x, 0.0, 0.0))
    )
    cab = cab.cut(cab_pocket)
    speaker.visual(
        mesh_from_cadquery(cab, "cabinet_shell"), material=mats["vinyl"], name="cabinet_shell", material_class_id=("fabric.canvas" if r.palette_style == "tweed_brown" else "plastic.patterned_textured")
    )
    speaker.inertial = Inertial.from_geometry(Box((spk_d, spk_w, spk_h)), mass=3.0)
    sgw, sgh = _grille_dims(r, spk_w, spk_h)
    _emit_front_grille(
        speaker,
        r,
        mats,
        front_x=front_x,
        gw=sgw,
        gh=sgh,
        center_z=0.0,
        grille_style=r.grille_style,
        logo_z=-0.040 * s,
    )
    _emit_piping(
        speaker,
        r,
        mats,
        front_x=front_x,
        span_w=spk_w - 0.020 * s,
        span_h=spk_h - 0.020 * s,
        center_z=0.0,
    )
    _emit_corner_caps(
        speaker,
        r,
        mats,
        front_x=front_x,
        cap_y=spk_w / 2.0 - 0.006 * s,
        cap_zs=(-(spk_h / 2.0 - 0.006 * s), spk_h / 2.0 - 0.006 * s),
    )

    # --- head box (child), authored with its base at z=0 ---
    head = model.part("head_box")
    head_shell = _rounded_box(head_w, head_d, head_h, 0.006 * s).translate((0.0, 0.0, head_h / 2.0))
    # gold panel recess in head top
    recess = (
        cq.Workplane("XY")
        .box(r.panel_d, r.panel_w + 0.010 * s, _panel_recess(r) * 2.2)
        .translate((r.panel_x, 0.0, head_h))
    )
    head_shell = head_shell.cut(recess)
    head.visual(
        mesh_from_cadquery(head_shell, "head_shell"), material=mats["vinyl"], name="head_shell", material_class_id=("fabric.canvas" if r.palette_style == "tweed_brown" else "plastic.patterned_textured")
    )
    head.inertial = Inertial.from_geometry(
        Box((head_d, head_w, head_h)), mass=1.8, origin=Origin(xyz=(0.0, 0.0, head_h / 2.0))
    )
    # gold panel + LED on head top (top surface at z=head_h)
    seats, axis, rot_y, mps, mcs = _emit_top_panel(head, r, mats, top_z=head_h + _panel_recess(r))
    # carry handle (box arch) on head top
    handle_x = r.panel_x - r.panel_d / 2.0 - 0.016 * s
    span = min(0.104 * s, head_w - 0.040 * s)
    strap = BoxGeometry((0.016 * s, span, 0.006 * s))
    strap.translate(handle_x, 0.0, head_h + 0.018 * s)
    head.visual(
        mesh_from_geometry(strap, "handle_strap"), material=mats["trim"], name="handle_strap", material_class_id="plastic.opaque_glossy_molded"
    )
    for i, y in enumerate((-span / 2.0 + 0.006 * s, span / 2.0 - 0.006 * s)):
        leg = BoxGeometry((0.016 * s, 0.010 * s, 0.018 * s))
        leg.translate(handle_x, y, head_h + 0.009 * s)
        head.visual(
            mesh_from_geometry(leg, f"handle_leg_{i}"),
            material=mats["trim"],
            name=f"handle_leg_{i}", material_class_id="plastic.opaque_glossy_molded",
        )

    # FIXED: head sits on speaker top face
    model.articulation(
        "cabinet_to_head",
        ArticulationType.FIXED,
        parent=speaker,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, spk_h / 2.0)),
        mating=MatingContract(
            parent_face_geometry="cabinet_shell",
            parent_face_side="positive_z",
            child_face_geometry="head_shell",
            child_face_side="negative_z",
            contact_tol=0.002,
        ),
    )
    _attach_knob_row(
        model,
        head,
        r,
        mats,
        joint_prefix="head",
        seats=seats,
        axis=axis,
        rot_y=rot_y,
        mating_parent_side=mps,
        mating_child_side=mcs,
    )


def _build_wedge(model, r, mats):
    """tilt_back_wedge: trapezoidal cabinet, panel on slanted top, knob axis =
    top-surface normal; grille on the tilted baffle (perforated / cloth)."""
    s = r.s
    g = _wedge_geom(r)
    pt_b, pt_c, pt_d = g["pt_b"], g["pt_c"], g["pt_d"]
    top_nx, top_nz, top_angle = g["top_nx"], g["top_nz"], g["top_angle"]
    baffle_nx, baffle_nz = g["baffle_nx"], g["baffle_nz"]
    baffle_cx, baffle_cz, blen = g["baffle_cx"], g["baffle_cz"], g["blen"]
    half_w = r.w / 2.0

    body = model.part("body")
    body.visual(
        mesh_from_cadquery(_wedge_solid(r), "cabinet"), material=mats["vinyl"], name="cabinet", material_class_id=("fabric.canvas" if r.palette_style == "tweed_brown" else "plastic.patterned_textured")
    )
    body.inertial = Inertial.from_geometry(Box((r.d, r.w, r.h_rear)), mass=2.6)

    # --- gold panel on the slanted top surface ---
    pt = r.panel_thick
    kf = 0.35
    base_x = pt_c[0] + kf * (pt_d[0] - pt_c[0])
    base_z = pt_c[1] + kf * (pt_d[1] - pt_c[1])
    panel_cx = base_x + pt * 0.5 * top_nx
    panel_cz = base_z + pt * 0.5 * top_nz
    panel = BoxGeometry((r.panel_d, r.panel_w, pt))
    panel.rotate_y(top_angle)
    panel.translate(panel_cx, 0.0, panel_cz)
    body.visual(mesh_from_geometry(panel, "gold_panel"), material=mats["panel"], name="gold_panel", material_class_id=("metal.brass_polished" if r.palette_style in {"black_vinyl_gold", "british_blue_gold"} else "metal.brushed_silver"))
    # LED
    lf = kf + 0.18
    lx = pt_c[0] + lf * (pt_d[0] - pt_c[0]) + pt * 0.5 * top_nx
    lz = pt_c[1] + lf * (pt_d[1] - pt_c[1]) + pt * 0.5 * top_nz
    led_y = min(0.068 * s, r.panel_w / 2.0 - 0.008 * s)
    led = CylinderGeometry(0.003 * s, 0.004 * s)
    led.rotate_y(top_angle)
    led.translate(lx, led_y, lz)
    body.visual(mesh_from_geometry(led, "power_led"), material=mats["led"], name="power_led", material_class_id="tech.emissive_surface")

    # --- speaker grille on the tilted baffle (perforated / cloth) ---
    gh = blen - 0.030 * s
    gw = r.w - 0.030 * s
    if r.grille_style == "woven_cloth":
        mesh = _woven_grille_mesh(r, cloth_x=0.0, cloth_w=gw, cloth_h=gh)
        mesh.rotate_y(-_BAFFLE_TILT)
        gx = baffle_cx - 0.003 * s * baffle_nx
        gz = baffle_cz - 0.003 * s * baffle_nz
        mesh.translate(gx, 0.0, gz)
        body.visual(
            mesh_from_geometry(mesh, "speaker_grille"),
            material=mats["grille"],
            name="speaker_grille", material_class_id="fabric.open_mesh",
        )
    else:
        grille = PerforatedPanelGeometry(
            (gh, gw),
            0.006 * s,
            hole_diameter=0.008 * s,
            pitch=0.016 * s,
            frame=0.006 * s,
            stagger=True,
        )
        grille.rotate_y(math.pi / 2.0 - _BAFFLE_TILT)
        gx = baffle_cx - 0.003 * s * baffle_nx
        gz = baffle_cz - 0.003 * s * baffle_nz
        grille.translate(gx, 0.0, gz)
        body.visual(
            mesh_from_geometry(grille, "speaker_grille"),
            material=mats["grille"],
            name="speaker_grille", material_class_id="metal.patterned_sheet_panel",
        )

    # piping on the baffle (4 bars, tilted)
    pip_t, pip_w = 0.005 * s, 0.006 * s
    bdx, bdz = pt_c[0] - pt_b[0], pt_c[1] - pt_b[1]
    pn = 0.002 * s
    for frac, nm in ((0.012, "piping_h_0"), (0.988, "piping_h_1")):
        bx = pt_b[0] + frac * bdx + pn * baffle_nx
        bz = pt_b[1] + frac * bdz + pn * baffle_nz
        bar = BoxGeometry((pip_t, r.w - 0.020 * s, pip_w))
        bar.rotate_y(-_BAFFLE_TILT)
        bar.translate(bx, 0.0, bz)
        body.visual(mesh_from_geometry(bar, nm), material=mats["piping"], name=nm, material_class_id="plastic.opaque_glossy_molded")
    for iy, yc in enumerate((-half_w + 0.010 * s, half_w - 0.010 * s)):
        nm = f"piping_v_{iy}"
        bar = BoxGeometry((pip_t, pip_w, blen - 0.020 * s))
        bar.rotate_y(-_BAFFLE_TILT)
        bar.translate(baffle_cx + pn * baffle_nx, yc, baffle_cz + pn * baffle_nz)
        body.visual(mesh_from_geometry(bar, nm), material=mats["piping"], name=nm, material_class_id="plastic.opaque_glossy_molded")

    # logo on lower baffle
    logo_frac = 0.28
    logo = BoxGeometry((0.004 * s, 0.080 * s, 0.022 * s))
    logo.rotate_y(-_BAFFLE_TILT)
    logo.translate(
        pt_b[0] + logo_frac * bdx + 0.001 * s * baffle_nx,
        -0.006 * s,
        pt_b[1] + logo_frac * bdz + 0.001 * s * baffle_nz,
    )
    body.visual(
        mesh_from_geometry(logo, "marshall_logo"), material=mats["logo"], name="marshall_logo", appearance_only=AppearanceOnlySpec(kind="decal")
    )

    # corner caps on baffle corners
    cap_y = half_w - 0.008 * s
    for iy, yc in enumerate((-cap_y, cap_y)):
        for ib, frac in enumerate((0.06, 0.94)):
            cap = BoxGeometry((0.016 * s, 0.016 * s, 0.016 * s))
            cap.rotate_y(-_BAFFLE_TILT)
            cap.translate(
                pt_b[0] + frac * bdx + 0.003 * s * baffle_nx,
                yc,
                pt_b[1] + frac * bdz + 0.003 * s * baffle_nz,
            )
            body.visual(
                mesh_from_geometry(cap, f"corner_cap_{iy}_{ib}"),
                material=mats["trim"],
                name=f"corner_cap_{iy}_{ib}", material_class_id="plastic.opaque_glossy_molded",
            )

    # carry handle on slanted top (cadquery, rotated to follow top)
    hf = 0.12
    handle_cx = pt_c[0] + hf * (pt_d[0] - pt_c[0])
    handle_cz = pt_c[1] + hf * (pt_d[1] - pt_c[1])
    span = min(0.100 * s, r.w - 0.040 * s)
    arch = 0.018 * s
    n = 13
    pts = []
    for i in range(n):
        t = i / (n - 1)
        y = -span / 2.0 + t * span
        zz = arch * (1.0 - (2.0 * t - 1.0) ** 2) + 0.002 * s
        pts.append((0.0, y, zz))
    path = cq.Workplane().add(cq.Edge.makeSpline([cq.Vector(*p) for p in pts]))
    prof = cq.Workplane("XZ").center(0.0, pts[0][2]).rect(0.016 * s, 0.006 * s)
    strap = prof.sweep(path, multisection=False, makeSolid=True)
    result = strap
    for y in (-span / 2.0, span / 2.0):
        mount = (
            cq.Workplane("XY").box(0.022 * s, 0.016 * s, 0.012 * s).translate((0.0, y, -0.003 * s))
        )
        result = result.union(mount)
    result = result.rotate((0, 0, 0), (0, 1, 0), math.degrees(top_angle))
    result = result.translate((handle_cx, 0.0, handle_cz))
    body.visual(mesh_from_cadquery(result, "handle"), material=mats["trim"], name="handle", material_class_id="plastic.opaque_glossy_molded")

    # --- knobs: seat on slanted panel, axis = top-surface normal ---
    panel_outer = pt - 0.001 * s
    seats = [(base_x + panel_outer * top_nx, ky, base_z + panel_outer * top_nz) for ky in r.knob_ys]
    _attach_knob_row(
        model,
        body,
        r,
        mats,
        joint_prefix="panel",
        seats=seats,
        axis=(top_nx, 0.0, top_nz),
        rot_y=top_angle,
        mating_parent_side=None,
        mating_child_side=None,
    )


# --------------------------------------------------------------------------- #
# Top-level build.
# --------------------------------------------------------------------------- #
def build_guitar_amplifier(
    config: GuitarAmplifierConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-guitar-amplifier-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["adopted_source_ids"] = (
        "S1",
        "S2",
        "S3",
        "S4",
        "S5",
        "S6",
        "S7",
        "S8",
        "S9",
        "S10",
        "S11",
    )
    mats = _materials(model, r)

    if r.cabinet_form == "mini_half_stack":
        _build_mini_stack(model, r, mats)
    elif r.cabinet_form == "tilt_back_wedge":
        _build_wedge(model, r, mats)
    else:
        _build_box_combo(model, r, mats)

    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]
    return model


def build_seeded_guitar_amplifier(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_guitar_amplifier(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #
def _knob_parent(object_model, r):
    return object_model.get_part("head_box" if r.cabinet_form == "mini_half_stack" else "body")


def _knob_joint_prefix(r):
    return "head" if r.cabinet_form == "mini_half_stack" else "panel"


def _front_grille_elem(vis_names: set[str]) -> str | None:
    """Representative thin +X front-baffle element across all Slot-C styles."""
    for name in ("speaker_grille", "grille_cell_0", "baffle_board", "front_vent_slots"):
        if name in vis_names:
            return name
    return None


def run_guitar_amplifier_tests(
    object_model: ArticulatedObject, config: GuitarAmplifierConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    n = r.knob_count
    panel_part = _knob_parent(object_model, r)
    prefix = _knob_joint_prefix(r)

    knobs = [object_model.get_part(f"knob_{i}") for i in range(n)]
    joints = [object_model.get_articulation(f"{prefix}_to_knob_{i}") for i in range(n)]

    # ---- Knob press-fit allowances (element-scoped, mirroring every source). ----
    for i in range(n):
        ctx.allow_overlap(
            knobs[i],
            panel_part,
            elem_a=f"knob_{i}",
            elem_b="gold_panel",
            reason="Knob base is press-fit a hair into the gold panel surface.",
        )
    if r.cabinet_form == "mini_half_stack":
        ctx.allow_overlap(
            object_model.get_part("head_box"),
            object_model.get_part("speaker_cabinet"),
            reason="Head box seats on the speaker cabinet top face (FIXED stack).",
        )

    # ---- Baseline checks (also run by the compiler; allowances applied). ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity: a row of >=2 CONTINUOUS knobs about the panel normal. ----
    ctx.check(
        "at least two control knobs present",
        len(knobs) >= 2 and all(k is not None for k in knobs),
        details=f"knob parts={[k.name for k in knobs]}",
    )
    for i, j in enumerate(joints):
        ctx.check(
            f"{prefix}_to_knob_{i} is CONTINUOUS",
            j.articulation_type == ArticulationType.CONTINUOUS,
            details=f"type={j.articulation_type}",
        )
        ctx.expect_contact(knobs[i], panel_part, name=f"knob_{i} rests on panel")

    # ---- Knob spin observable (off-axis pointer moves through the AABB). ----
    for i, (k, j) in enumerate(zip(knobs, joints)):
        ax = ctx.part_world_position(k)
        mn0, mx0 = ctx.part_world_aabb(k)
        cen0 = (
            (mn0[0] + mx0[0]) / 2.0 - ax[0],
            (mn0[1] + mx0[1]) / 2.0 - ax[1],
            (mn0[2] + mx0[2]) / 2.0 - ax[2],
        )
        with ctx.pose({j: math.pi / 2.0}):
            mn1, mx1 = ctx.part_world_aabb(k)
            cen1 = (
                (mn1[0] + mx1[0]) / 2.0 - ax[0],
                (mn1[1] + mx1[1]) / 2.0 - ax[1],
                (mn1[2] + mx1[2]) / 2.0 - ax[2],
            )
        moved = math.sqrt(sum((a - b) ** 2 for a, b in zip(cen0, cen1)))
        ctx.check(
            f"knob_{i} spin is observable",
            moved > 0.0005,
            details=f"rest_off={cen0}, turn_off={cen1}, moved={moved:.4f}",
        )

    # ---- Knob row fits the panel / no adjacent interpenetration. ----
    if n >= 2:
        span = (n - 1) * r.knob_pitch
        ctx.check(
            "knob row fits the gold panel",
            span + r.knob_diam <= r.panel_w + 1e-6,
            details=f"span+diam={span + r.knob_diam:.4f} panel_w={r.panel_w:.4f}",
        )
        ctx.check(
            "adjacent knobs do not interpenetrate",
            r.knob_pitch >= r.knob_diam + 1e-6,
            details=f"pitch={r.knob_pitch:.4f} diam={r.knob_diam:.4f}",
        )

    # ---- Cabinet-form structural assertions. ----
    if r.cabinet_form == "head_unit":
        body = object_model.get_part("body")
        vis = {v.name for v in body.visuals}
        ctx.check(
            "head_unit has no speaker grille", "speaker_grille" not in vis, details=str(sorted(vis))
        )
        ctx.check(
            "head_unit has front vent slots", "front_vent_slots" in vis, details=str(sorted(vis))
        )
        bmn, bmx = ctx.part_world_aabb(body)
        ctx.check(
            "head_unit wider than tall",
            (bmx[1] - bmn[1]) > (bmx[2] - bmn[2]) * 1.4,
            details=f"dy={bmx[1] - bmn[1]:.3f} dz={bmx[2] - bmn[2]:.3f}",
        )
    elif r.cabinet_form == "mini_half_stack":
        speaker = object_model.get_part("speaker_cabinet")
        head = object_model.get_part("head_box")
        spk_mn, spk_mx = ctx.part_world_aabb(speaker)
        head_mn, head_mx = ctx.part_world_aabb(head)
        ctx.check(
            "head box sits on the speaker cabinet top",
            head_mn[2] >= spk_mx[2] - 0.004,
            details=f"speaker_top={spk_mx[2]:.3f} head_bottom={head_mn[2]:.3f}",
        )
        ctx.check(
            "gold panel + knobs parent to the head box",
            all(j.parent == "head_box" for j in joints),
            details=f"parents={[j.parent for j in joints]}",
        )
        spk_grille = _front_grille_elem({v.name for v in speaker.visuals})
        if spk_grille is not None:
            gmn, gmx = ctx.part_element_world_aabb(speaker, elem=spk_grille)
            ctx.check(
                "speaker grille is on the speaker cabinet",
                gmx[2] < spk_mx[2] + 0.005,
                details=f"grille({spk_grille})_top={gmx[2]:.3f} speaker_top={spk_mx[2]:.3f}",
            )
    elif r.cabinet_form == "tilt_back_wedge":
        for i, j in enumerate(joints):
            ax = j.axis
            ctx.check(
                f"knob_{i} axis is the tilted top-surface normal (not vertical)",
                abs(ax[0]) > 0.1 and abs(ax[2]) > 0.5,
                details=f"axis={tuple(ax)}",
            )
        body = object_model.get_part("body")
        cmn, cmx = ctx.part_element_world_aabb(body, elem="cabinet")
        ctx.check(
            "wedge cabinet rear taller than front extent",
            (cmx[2] - cmn[2]) >= r.h_rear - 0.006,
            details=f"cab_dz={cmx[2] - cmn[2]:.3f} h_rear={r.h_rear:.3f}",
        )

    # ---- Front baffle faces +X (grille or vent). ----
    grille_owner = (
        object_model.get_part("speaker_cabinet")
        if r.cabinet_form == "mini_half_stack"
        else object_model.get_part("body")
    )
    owner_vis = {v.name for v in grille_owner.visuals}
    front_elem = _front_grille_elem(owner_vis)
    ctx.check(
        "front baffle / grille / vent present",
        front_elem is not None,
        details=str(sorted(owner_vis)),
    )
    if front_elem is not None:
        fmn, fmx = ctx.part_element_world_aabb(grille_owner, elem=front_elem)
        fx = (fmn[0] + fmx[0]) / 2.0
        fx_ext = fmx[0] - fmn[0]
        ctx.check(
            "front baffle is a thin +X-facing panel",
            fx > 0.0 and fx_ext < (fmx[1] - fmn[1]) and fx_ext < (fmx[2] - fmn[2]),
            details=f"center_x={fx:.3f} extents=({fx_ext:.3f},{fmx[1] - fmn[1]:.3f},{fmx[2] - fmn[2]:.3f})",
        )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(tuple(t) for t in object_model.meta.get("slot_choices", ()))
        == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = [
    "GuitarAmplifierConfig",
    "ResolvedGuitarAmplifierConfig",
    "build_guitar_amplifier",
    "build_seeded_guitar_amplifier",
    "config_from_seed",
    "resolve_config",
    "run_guitar_amplifier_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "__modular__",
]
