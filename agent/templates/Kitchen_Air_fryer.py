# SPDX-License-Identifier: Apache-2.0

"""Countertop pull-out-basket air fryer modular template.

NOTE on the slug name: "air_fryer" here = **countertop pull-out-basket air
fryer** (a floor-standing/counter body with one or more cooking-basket drawers
that slide out along +X), NOT a microwave (side/down glass door + turntable),
NOT a rice cooker (round keep-warm pot + top-flip lid + inner pot), NOT a
toaster oven (front drop-down glass door + rack). The defining motion is the
basket drawer sliding out (PRISMATIC +X); the clamshell candidate reparents the
basket onto the body and swaps the defining motion to a top-opening REVOLUTE
lid.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Kitchen_Air_fryer.md`` and the
``picture/Kitchen/Air fryer`` 5-star sample pool (1 parent + 7 slot-fork
variants), all synced under ``data/records/``.

Structure (pattern = ``mixed``): a single root ``body`` part (main shell mesh
chosen by ``body_silhouette``), with three named module axes attaching as
parallel children / inline visuals, plus a basket-count multiplicity axis:

  * ``body_silhouette`` (3): rounded_taper (filleted-rect loft) / square_tower
    (box + edge fillet, taller 0.36) / cylindrical_drum (revolve + flat front
    facet). A mesh-helper dimension; it does not add a joint. (S1/S2/S3)
  * ``control`` (3): digital_touch (smoked-glass panel visual, 0 joint, Rule 1)
    / rotary_dials (timer_knob + temp_knob, 2 REVOLUTE about +Z) / push_buttons
    (2x3 grid of pad visuals, 0 joint, Rule 1). (S1/S4/S5)
  * ``basket_opening`` (3): windowed_drawer (face with cut-through viewing
    window + tinted glass) / solid_drawer (opaque face, no window_glass) /
    clamshell_lid (COUPLED: split body bowl + top-opening REVOLUTE lid, basket
    fixed on body, no drawer/rail/PRISMATIC). (S1/S6/S7)
  * ``basket_count`` (N in [1,3]): a multiplicity axis — N side-by-side drawers
    each with an independent PRISMATIC slide. Only valid for windowed/solid
    drawers; encoded into the slot_choice tuple as ``("basket_count", f"n{N}")``.
    clamshell locks N=1 (no drawer subtree to replicate). (S8)

All hinge pins / sliders / dial shafts are captured-pin/slide geometry, so those
joints omit ``MatingContract`` (grandfathered) and are guarded by the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests allow_overlap block).

Compatibility gating (resolve_config, spec §9), first-version policy:
  * clamshell_lid removes the drawer subtree + rails + PRISMATIC and fixes the
    basket inside the body bowl -> N is locked to 1, and the control panel must
    sit on the lid top, so clamshell forces control=digital_touch (lid-top
    panel; dials/buttons + clamshell would need lid-deck anchor reparenting).
  * cylindrical_drum's narrow front facet only fits a single pocket -> cylindrical
    locks N=1.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    KnobSkirt,
    KnobTopFeature,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

BodySilhouette = Literal["rounded_taper", "square_tower", "cylindrical_drum"]
Control = Literal["digital_touch", "rotary_dials", "push_buttons"]
BasketOpening = Literal["windowed_drawer", "solid_drawer", "clamshell_lid"]
PaletteStyle = Literal[
    "inox_copper", "matte_graphite", "retro_cream", "stainless_steel", "glass_black"
]

BODY_SILHOUETTES: tuple[BodySilhouette, ...] = (
    "rounded_taper",
    "square_tower",
    "cylindrical_drum",
)
CONTROLS: tuple[Control, ...] = ("digital_touch", "rotary_dials", "push_buttons")
BASKET_OPENINGS: tuple[BasketOpening, ...] = (
    "windowed_drawer",
    "solid_drawer",
    "clamshell_lid",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "inox_copper",
    "matte_graphite",
    "retro_cream",
    "stainless_steel",
    "glass_black",
)

DRAWER_OPENINGS: tuple[BasketOpening, ...] = ("windowed_drawer", "solid_drawer")

N_MIN = 1
N_MAX = 3
# Basket-count sampling weights (spec §8: 1 high-frequency, 2 common, 3 long tail).
BASKET_COUNT_WEIGHTS = (0.55, 0.30, 0.15)

# ---------------------------------------------------------------------------
# Palette colorways (5 sets, from the 8 5-star source materials, spec §7).
# Keys: shell, trim (copper/accent), glass (panel), window (tinted),
# basket (metal), fries (gold), knob (dial cap), shaft (dial shaft),
# panel (matte button panel), button (button pad), hinge (clamshell barrel).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "inox_copper": {
        "shell": (0.06, 0.06, 0.065, 1.0),
        "trim": (0.76, 0.44, 0.30, 1.0),
        "glass": (0.03, 0.03, 0.035, 1.0),
        "window": (0.12, 0.085, 0.06, 1.0),
        "basket": (0.16, 0.16, 0.16, 1.0),
        "fries": (0.88, 0.62, 0.24, 1.0),
        "knob": (0.08, 0.08, 0.09, 1.0),
        "shaft": (0.52, 0.52, 0.54, 1.0),
        "panel": (0.09, 0.09, 0.095, 1.0),
        "button": (0.16, 0.155, 0.15, 1.0),
        "hinge": (0.22, 0.22, 0.22, 1.0),
    },
    "matte_graphite": {
        "shell": (0.09, 0.09, 0.095, 1.0),
        "trim": (0.40, 0.41, 0.42, 1.0),
        "glass": (0.03, 0.03, 0.035, 1.0),
        "window": (0.10, 0.10, 0.11, 1.0),
        "basket": (0.16, 0.16, 0.16, 1.0),
        "fries": (0.86, 0.60, 0.22, 1.0),
        "knob": (0.13, 0.13, 0.14, 1.0),
        "shaft": (0.52, 0.52, 0.54, 1.0),
        "panel": (0.07, 0.07, 0.075, 1.0),
        "button": (0.16, 0.155, 0.15, 1.0),
        "hinge": (0.30, 0.30, 0.31, 1.0),
    },
    "retro_cream": {
        "shell": (0.90, 0.88, 0.82, 1.0),
        "trim": (0.76, 0.44, 0.30, 1.0),
        "glass": (0.05, 0.05, 0.055, 1.0),
        "window": (0.14, 0.10, 0.07, 1.0),
        "basket": (0.18, 0.18, 0.18, 1.0),
        "fries": (0.88, 0.62, 0.24, 1.0),
        "knob": (0.08, 0.08, 0.09, 1.0),
        "shaft": (0.55, 0.55, 0.57, 1.0),
        "panel": (0.82, 0.80, 0.74, 1.0),
        "button": (0.30, 0.29, 0.27, 1.0),
        "hinge": (0.45, 0.45, 0.46, 1.0),
    },
    "stainless_steel": {
        "shell": (0.74, 0.75, 0.77, 1.0),
        "trim": (0.58, 0.59, 0.61, 1.0),
        "glass": (0.04, 0.04, 0.045, 1.0),
        "window": (0.12, 0.085, 0.06, 1.0),
        "basket": (0.20, 0.20, 0.20, 1.0),
        "fries": (0.88, 0.62, 0.24, 1.0),
        "knob": (0.30, 0.30, 0.32, 1.0),
        "shaft": (0.52, 0.52, 0.54, 1.0),
        "panel": (0.62, 0.63, 0.65, 1.0),
        "button": (0.34, 0.34, 0.36, 1.0),
        "hinge": (0.50, 0.50, 0.52, 1.0),
    },
    "glass_black": {
        "shell": (0.02, 0.02, 0.025, 1.0),
        "trim": (0.70, 0.40, 0.27, 1.0),
        "glass": (0.03, 0.03, 0.035, 1.0),
        "window": (0.12, 0.085, 0.06, 1.0),
        "basket": (0.14, 0.14, 0.14, 1.0),
        "fries": (0.90, 0.64, 0.26, 1.0),
        "knob": (0.05, 0.05, 0.06, 1.0),
        "shaft": (0.48, 0.48, 0.50, 1.0),
        "panel": (0.04, 0.04, 0.045, 1.0),
        "button": (0.12, 0.12, 0.13, 1.0),
        "hinge": (0.18, 0.18, 0.19, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), from the parent/dual/clamshell sources.
# Frame: +X front (drawer slides out), +Y left, +Z up, body grounded at z=0.
# ---------------------------------------------------------------------------
_BODY_H = 0.33  # rounded/cylindrical height
_SQUARE_BODY_H = 0.36  # square tower is taller (spec §A)
_BODY_DEPTH_TOP = 0.32  # X extent at the top rim
_BODY_DEPTH_BOT = 0.30  # X extent at the base (rounded taper)
_SINGLE_WIDTH_TOP = 0.28  # Y extent (single basket)
_SINGLE_WIDTH_BOT = 0.26
_CORNER_R = 0.040
_EDGE_R = 0.003  # square-tower vertical edge break

# Drum (cylindrical) geometry.
_DRUM_RADIUS = 0.160
_FLAT_FRONT_X = 0.110

# Drawer pocket (parent dims). The back is cut a little deeper than the parent
# (-0.100) so the rearward-shifted drawer/basket/fries keep clearance behind the
# pocket void (the joint frame moved back from X=0.152 to anchor on the sill).
_POCKET_X_BACK = -0.130
_POCKET_X_FRONT = 0.180
_POCKET_HW = 0.078  # half-width of EACH pocket opening (dual source)
_SINGLE_POCKET_HALF_W = 0.1125  # single basket pocket half-width (parent)
_POCKET_Z0 = 0.018
_POCKET_Z1 = 0.158
_DIVIDER_HALF = 0.012  # half-thickness of the center divider (dual)

# Prismatic joint frame. The pocket front is cut open beyond the body wall, so
# the natural front-center point sits in open air. We anchor the joint onto a
# real pocket-floor sill (see _emit_drawers) at the pocket floor instead, so the
# articulation origin lands on body mesh (baseline tol 15mm). The drawer-local
# geometry is authored relative to this joint frame, so world positions are
# independent of _JOINT_Z.
_JOINT_X = 0.130  # within the pocket-floor sill footprint
_JOINT_Z = 0.024  # on the pocket-floor sill/rail top
_TRAVEL = 0.160

# Pocket-floor sill: a real body lip running along the pocket floor that carries
# the drawer and gives the PRISMATIC origin real geometry to anchor to. Its top
# (z 0.024) matches the slide-rail tops; the basket seats 2 mm into it.
_SILL_X_BACK = -0.060
_SILL_X_FRONT = 0.150  # reaches the body front wall
_SILL_Z0 = 0.018  # pocket floor
_SILL_Z1 = 0.024  # sill top (joint origin sits here)

# The drawer subtree (face / basket / fries) was authored in the parent against
# a joint at X=0.152. We anchor the joint onto the pocket-floor sill at a smaller
# X, so we shift the drawer-local X authoring by this delta to keep the world
# placement identical (face flush at the front, basket inside the pocket void).
_JOINT_X_AUTHOR = 0.152
_JOINT_Z_AUTHOR = 0.088
_DRAWER_DX = _JOINT_X_AUTHOR - _JOINT_X  # add to drawer-local X coords
_DRAWER_DZ = _JOINT_Z_AUTHOR - _JOINT_Z  # add to drawer-local Z coords

# Drawer face (drawer-local; origin at the joint frame).
_FACE_X0, _FACE_X1 = -0.006, 0.008
_SINGLE_FACE_W = 0.221
_MULTI_FACE_W = 0.152
_FACE_H = 0.136
_SINGLE_WINDOW_W = 0.150
_MULTI_WINDOW_W = 0.100
_WINDOW_H = 0.085

# Cooking basket (drawer-local).
_BASKET_LEN = 0.240
_SINGLE_BASKET_W = 0.210
_MULTI_BASKET_W = 0.138
_BASKET_H = 0.105
_BASKET_X1 = -0.004
_BASKET_CLEARANCE = 0.004

_TOP_GLASS_Z = 0.3265  # center of the top touch panel (rounded/square)

# Slide rails (parent / dual).
_RAIL_LEN = 0.253
_RAIL_W = 0.012
_RAIL_H = 0.006
_RAIL_CX = 0.0285
_SINGLE_RAIL_Y = 0.085  # single: rails at ±0.085
_RAIL_OFFSET = 0.050  # dual: rails at cy ± 0.050

# Rotary dials.
_DIAL_X = 0.040
_DIAL_Y_OFFSET = 0.040
_DIAL_SHAFT_R = 0.004
_DIAL_SHAFT_H = 0.018
_TIMER_SWEEP = 5.24
_TEMP_SWEEP = 4.71

# Push-button grid.
_BUTTON_ROWS = 2
_BUTTON_COLS = 3
_BUTTON_DIAMETER = 0.022
_BUTTON_HEIGHT = 0.005
_BUTTON_SPACING_X = 0.050
_BUTTON_SPACING_Y = 0.055

# Clamshell.
_SPLIT_Z = 0.195
_WALL_T = 0.008
_BARREL_R = 0.007
_BARREL_LEN = 0.038
_BARREL_Y_OFFSET = 0.058
_LID_OPEN = 1.8


# ---------------------------------------------------------------------------
# Tessellation budget. Air-fryer parts are ~0.3 m scale, so a 1 mm linear /
# 0.1 rad default triangulates the lofted clamshell/drum shells and the union
# food props into very dense meshes -- which makes the collision-inclusive
# compile + fcl/trimesh QC slow enough to risk the wall-time SIGKILL on the
# dials-heavy / clamshell / cylindrical seeds. Coarser triangles (4 mm linear,
# 0.5 rad angular) read identically at this scale but cut triangle counts
# several-fold, giving every seed a large headroom under the budget. This only
# changes mesh DENSITY, never the primitive TYPE or topology.
_MESH_TOL = 0.004
_MESH_ANG = 0.5
# Slightly finer for the small dial bezels/shafts/handles so tiny radii still
# round cleanly (still far coarser than the default).
_FINE_TOL = 0.0025
_FINE_ANG = 0.35


def _mesh(model, name, *, assets, tol: float = _MESH_TOL, ang: float = _MESH_ANG):
    """mesh_from_cadquery with the coarsened air-fryer tessellation budget."""
    return mesh_from_cadquery(model, name, assets=assets, tolerance=tol, angular_tolerance=ang)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AirFryerConfig:
    body_silhouette: BodySilhouette | None = None
    control: Control | None = None
    basket_opening: BasketOpening | None = None
    basket_count: int | None = None
    palette_style: PaletteStyle = "inox_copper"
    body_depth_scale: float = 1.0
    body_height_scale: float = 1.0
    basket_width_scale: float = 1.0
    drawer_travel_scale: float = 1.0
    lid_open_angle_scale: float = 1.0
    dial_sweep_scale: float = 1.0
    pocket_spacing_scale: float = 1.0
    name: str = "air_fryer"


@dataclass(frozen=True)
class ResolvedAirFryerConfig:
    body_silhouette: BodySilhouette
    control: Control
    basket_opening: BasketOpening
    basket_count: int
    palette_style: PaletteStyle
    # Concrete derived geometry.
    body_h: float
    body_depth_top: float
    body_depth_bot: float
    pocket_cys: tuple[float, ...]  # Y center of each drawer pocket
    pocket_hw: float  # half-width of each pocket opening
    body_width_top: float
    body_width_bot: float
    face_w: float
    window_w: float
    basket_w: float
    travel: float
    lid_open: float
    timer_sweep: float
    temp_sweep: float
    split_z: float
    lid_height: float
    name: str

    @property
    def is_drawer(self) -> bool:
        return self.basket_opening in DRAWER_OPENINGS

    @property
    def is_clamshell(self) -> bool:
        return self.basket_opening == "clamshell_lid"


def config_from_seed(seed: int) -> AirFryerConfig:
    rng = random.Random(seed)
    return AirFryerConfig(
        body_silhouette=rng.choice(BODY_SILHOUETTES),
        control=rng.choice(CONTROLS),
        basket_opening=rng.choice(BASKET_OPENINGS),
        basket_count=rng.choices((1, 2, 3), weights=BASKET_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        body_depth_scale=round(rng.uniform(0.92, 1.10), 4),
        body_height_scale=round(rng.uniform(0.90, 1.12), 4),
        basket_width_scale=round(rng.uniform(0.92, 1.08), 4),
        drawer_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        lid_open_angle_scale=round(rng.uniform(0.85, 1.10), 4),
        dial_sweep_scale=round(rng.uniform(0.90, 1.05), 4),
        pocket_spacing_scale=round(rng.uniform(0.92, 1.10), 4),
        name=f"seeded_air_fryer_{seed}",
    )


def resolve_config(config: AirFryerConfig | None = None) -> ResolvedAirFryerConfig:
    cfg = config or AirFryerConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    body_silhouette = _pick(cfg.body_silhouette, BODY_SILHOUETTES)
    control = _pick(cfg.control, CONTROLS)
    basket_opening = _pick(cfg.basket_opening, BASKET_OPENINGS)

    basket_count = int(cfg.basket_count) if cfg.basket_count is not None else 1
    basket_count = int(_clamp(basket_count, N_MIN, N_MAX))

    # --- Compatibility gating (spec §9, first-version policy). ---
    # (1) clamshell removes the drawer subtree (basket fixed on body) and moves
    #     the control panel onto the lid top -> lock N=1 and force digital_touch.
    if basket_opening == "clamshell_lid":
        basket_count = 1
        control = "digital_touch"
    # (3) cylindrical drum's narrow front facet only fits a single pocket.
    if body_silhouette == "cylindrical_drum":
        basket_count = 1

    # --- Scales (clamped). ---
    depth_scale = _clamp(cfg.body_depth_scale, 0.92, 1.10)
    height_scale = _clamp(cfg.body_height_scale, 0.90, 1.12)
    width_scale = _clamp(cfg.basket_width_scale, 0.92, 1.08)
    travel_scale = _clamp(cfg.drawer_travel_scale, 0.85, 1.10)
    angle_scale = _clamp(cfg.lid_open_angle_scale, 0.85, 1.10)
    sweep_scale = _clamp(cfg.dial_sweep_scale, 0.90, 1.05)
    spacing_scale = _clamp(cfg.pocket_spacing_scale, 0.92, 1.10)

    base_h = _SQUARE_BODY_H if body_silhouette == "square_tower" else _BODY_H
    body_h = base_h * height_scale
    body_depth_top = _BODY_DEPTH_TOP * depth_scale
    body_depth_bot = _BODY_DEPTH_BOT * depth_scale

    pocket_hw = _POCKET_HW * width_scale if basket_count >= 2 else _SINGLE_POCKET_HALF_W
    face_w = (_MULTI_FACE_W if basket_count >= 2 else _SINGLE_FACE_W) * (
        width_scale if basket_count >= 2 else 1.0
    )
    window_w = _MULTI_WINDOW_W if basket_count >= 2 else _SINGLE_WINDOW_W
    basket_w = (_MULTI_BASKET_W if basket_count >= 2 else _SINGLE_BASKET_W) * (
        width_scale if basket_count >= 2 else 1.0
    )

    # --- Absolute side-by-side pocket placement (N-invariant). ---
    if basket_count == 1:
        pocket_cys: tuple[float, ...] = (0.0,)
        body_width_top = _SINGLE_WIDTH_TOP
        body_width_bot = _SINGLE_WIDTH_BOT
    else:
        # Center span between adjacent pocket centers (dual source: ±0.090).
        span = (_DIVIDER_HALF + pocket_hw) * spacing_scale
        # Clearance inequality (spec §7): pockets must not collide; widen the
        # span so adjacent pocket inner edges keep a >= margin gap.
        min_span = pocket_hw + _DIVIDER_HALF + 0.002
        span = max(span, min_span)
        if basket_count == 2:
            pocket_cys = (span, -span)
        else:  # N == 3
            pocket_cys = (2.0 * span, 0.0, -2.0 * span)
        # Body width must wrap the outermost pocket + a wall margin.
        wall = 0.020
        half_width = abs(pocket_cys[0]) + pocket_hw + wall
        body_width_top = 2.0 * half_width
        body_width_bot = body_width_top - 0.020

    travel = _clamp(_TRAVEL * travel_scale, 0.120, 0.180)
    lid_open = _clamp(_LID_OPEN * angle_scale, 1.5, math.pi * 0.95)
    timer_sweep = _clamp(_TIMER_SWEEP * sweep_scale, 3.1, 6.2)
    temp_sweep = _clamp(_TEMP_SWEEP * sweep_scale, 3.1, 6.2)

    split_z = _SPLIT_Z * height_scale
    lid_height = body_h - split_z

    return ResolvedAirFryerConfig(
        body_silhouette=body_silhouette,
        control=control,
        basket_opening=basket_opening,
        basket_count=basket_count,
        palette_style=palette_style,
        body_h=body_h,
        body_depth_top=body_depth_top,
        body_depth_bot=body_depth_bot,
        pocket_cys=pocket_cys,
        pocket_hw=pocket_hw,
        body_width_top=body_width_top,
        body_width_bot=body_width_bot,
        face_w=face_w,
        window_w=window_w,
        basket_w=basket_w,
        travel=travel,
        lid_open=lid_open,
        timer_sweep=timer_sweep,
        temp_sweep=temp_sweep,
        split_z=split_z,
        lid_height=lid_height,
        name=cfg.name or "air_fryer",
    )


def with_overrides(config: AirFryerConfig, **kwargs: object) -> AirFryerConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: AirFryerConfig | ResolvedAirFryerConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedAirFryerConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("body_silhouette", r.body_silhouette),
        ("control", r.control),
        ("basket_opening", r.basket_opening),
    ]
    # N is a topology dimension only for the drawer openings (clamshell locks 1).
    if r.is_drawer:
        choices.append(("basket_count", f"n{r.basket_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _rounded_rect_sketch(wp: cq.Workplane, dx: float, dy: float, r: float) -> cq.Workplane:
    return wp.sketch().rect(dx, dy).vertices().fillet(r).finalize()


# ---------------------------------------------------------------------------
# Body shell mesh helpers (body_silhouette). Each preserves the source
# primitive (loft / box / revolve). All cut N drawer pockets + a top recess.
# ---------------------------------------------------------------------------
def _cut_pockets(shell: cq.Workplane, r: ResolvedAirFryerConfig) -> cq.Workplane:
    for cy in r.pocket_cys:
        pocket = (
            cq.Workplane("XY")
            .box(
                _POCKET_X_FRONT - _POCKET_X_BACK,
                2.0 * r.pocket_hw,
                _POCKET_Z1 - _POCKET_Z0,
            )
            .translate(
                (
                    (_POCKET_X_FRONT + _POCKET_X_BACK) / 2.0,
                    cy,
                    (_POCKET_Z0 + _POCKET_Z1) / 2.0,
                )
            )
        )
        shell = shell.cut(pocket)
    return shell


def _build_rounded_shell(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Tapered rounded-corner shell (loft). Source: parent _build_body_shell."""
    bottom = cq.Sketch().rect(r.body_depth_bot, r.body_width_bot).vertices().fillet(_CORNER_R)
    top = cq.Sketch().rect(r.body_depth_top, r.body_width_top).vertices().fillet(_CORNER_R)
    shell = (
        cq.Workplane("XY")
        .placeSketch(bottom, top.moved(cq.Location(cq.Vector(0.0, 0.0, r.body_h))))
        .loft()
    )
    shell = _cut_pockets(shell, r)
    recess = (
        cq.Workplane("XY")
        .box(0.240, max(0.200, r.body_width_top - 0.06), 0.015)
        .translate((0.0, 0.0, r.body_h + 0.0025))
    )
    return shell.cut(recess)


def _build_square_shell(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Square-tower shell (box + vertical edge fillet). Source: square."""
    shell = (
        cq.Workplane("XY")
        .box(r.body_depth_top, r.body_width_top, r.body_h)
        .translate((0.0, 0.0, r.body_h / 2.0))
    )
    shell = shell.edges("|Z").fillet(_EDGE_R)
    shell = _cut_pockets(shell, r)
    recess = (
        cq.Workplane("XY")
        .box(0.240, max(0.200, r.body_width_top - 0.06), 0.015)
        .translate((0.0, 0.0, r.body_h + 0.0025))
    )
    return shell.cut(recess)


def _build_drum_shell(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Cylindrical drum shell (revolve + flat front facet). Source: cylindrical."""
    drum = (
        cq.Workplane("XZ")
        .moveTo(0.001, 0)
        .lineTo(_DRUM_RADIUS, 0)
        .lineTo(_DRUM_RADIUS, r.body_h)
        .lineTo(0.001, r.body_h)
        .close()
        .revolve(360, (0, 0), (0, 1))
    )
    cut_w = _DRUM_RADIUS + 0.010
    flat_cut = (
        cq.Workplane("XY")
        .box(cut_w, 2.0 * _DRUM_RADIUS + 0.020, r.body_h + 0.020)
        .translate((_FLAT_FRONT_X + cut_w / 2.0, 0, r.body_h / 2.0))
    )
    drum = drum.cut(flat_cut)
    drum = _cut_pockets(drum, r)
    recess = (
        cq.Workplane("XY", origin=(0, 0, r.body_h - 0.012))
        .circle(_DRUM_RADIUS - 0.018)
        .extrude(0.015)
    )
    return drum.cut(recess)


def _build_rounded_trim(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Filleted-rect copper trim ring at the upper rim. Source: parent/dual."""
    z_outer = r.body_h - 0.014
    z_inner = r.body_h - 0.030
    outer = _rounded_rect_sketch(
        cq.Workplane("XY", origin=(0.0, 0.0, z_outer)),
        r.body_depth_top + 0.010,
        r.body_width_top + 0.010,
        _CORNER_R + 0.005,
    ).extrude(0.014)
    inner = _rounded_rect_sketch(
        cq.Workplane("XY", origin=(0.0, 0.0, z_inner)),
        r.body_depth_top - 0.018,
        r.body_width_top - 0.018,
        max(_CORNER_R - 0.004, 0.005),
    ).extrude(0.040)
    return outer.cut(inner)


def _build_square_trim(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Sharp rectangular copper trim ring. Source: square _build_trim_band."""
    band_z0 = r.body_h - 0.014
    outer = (
        cq.Workplane("XY", origin=(0.0, 0.0, band_z0))
        .sketch()
        .rect(r.body_depth_top + 0.010, r.body_width_top + 0.010)
        .finalize()
        .extrude(0.014)
    )
    inner = (
        cq.Workplane("XY", origin=(0.0, 0.0, band_z0 - 0.016))
        .sketch()
        .rect(r.body_depth_top - 0.018, r.body_width_top - 0.018)
        .finalize()
        .extrude(0.040)
    )
    return outer.cut(inner)


def _build_drum_trim(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """D-shaped copper trim ring. Source: cylindrical _build_trim_band."""
    z0 = r.body_h - 0.014
    outer = cq.Workplane("XY", origin=(0, 0, z0)).circle(_DRUM_RADIUS + 0.004).extrude(0.014)
    inner = (
        cq.Workplane("XY", origin=(0, 0, z0 - 0.016)).circle(_DRUM_RADIUS - 0.008).extrude(0.040)
    )
    band = outer.cut(inner)
    cut_w = _DRUM_RADIUS + 0.005
    flat_cut = (
        cq.Workplane("XY")
        .box(cut_w, 2.0 * _DRUM_RADIUS + 0.020, 0.050)
        .translate((_FLAT_FRONT_X + cut_w / 2.0, 0, z0 + 0.009))
    )
    return band.cut(flat_cut)


def _build_drum_top_glass(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """D-trimmed circular glass touch panel. Source: cylindrical _build_top_glass."""
    top_z = r.body_h - 0.009
    glass = (
        cq.Workplane("XY", origin=(0, 0, top_z - 0.003)).circle(_DRUM_RADIUS - 0.022).extrude(0.006)
    )
    cut_w = _DRUM_RADIUS
    flat_cut = (
        cq.Workplane("XY")
        .box(cut_w, 2.0 * _DRUM_RADIUS + 0.020, 0.020)
        .translate((_FLAT_FRONT_X + cut_w / 2.0, 0, top_z))
    )
    return glass.cut(flat_cut)


# ---------------------------------------------------------------------------
# Drawer subtree mesh helpers (windowed/solid). Drawer-local frame; origin at
# the prismatic joint. Source: parent _build_drawer_face/_handle/_basket/_fries.
# ---------------------------------------------------------------------------
def _build_drawer_face(r: ResolvedAirFryerConfig, *, windowed: bool) -> cq.Workplane:
    """Rounded drawer front panel; window cut-through only when windowed."""
    face = cq.Workplane("XY").box(_FACE_X1 - _FACE_X0, r.face_w, _FACE_H).edges("|X").fillet(0.020)
    if windowed:
        window = cq.Workplane("XY").box(0.050, r.window_w, _WINDOW_H)
        face = face.cut(window)
    return face.translate(((_FACE_X0 + _FACE_X1) / 2.0 + _DRAWER_DX, 0.0, _DRAWER_DZ))


def _build_handle() -> cq.Workplane:
    """Flat vertical copper handle on a boss, angled slightly forward/down."""
    boss = cq.Workplane("XY").box(0.024, 0.034, 0.014).translate((0.018, 0.0, 0.052))
    bar = (
        cq.Workplane("XY")
        .box(0.008, 0.036, 0.140)
        .rotate((0, 0, 0), (0, 1, 0), -17.0)
        .translate((0.0465, 0.0, -0.0149))
    )
    return boss.union(bar).translate((_DRAWER_DX, 0.0, _DRAWER_DZ))


def _basket_cz(r: ResolvedAirFryerConfig) -> float:
    return (_POCKET_Z0 - _JOINT_Z) + _BASKET_CLEARANCE + _BASKET_H / 2.0


def _build_drawer_basket(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Open-top hollow cooking basket (drawer-local). Source: parent _build_basket."""
    basket_cx = _BASKET_X1 - _BASKET_LEN / 2.0 + _DRAWER_DX
    outer = cq.Workplane("XY").box(_BASKET_LEN, r.basket_w, _BASKET_H).edges("|Z").fillet(0.015)
    cavity = (
        cq.Workplane("XY")
        .box(_BASKET_LEN - 0.010, r.basket_w - 0.010, 0.120)
        .edges("|Z")
        .fillet(0.012)
        .translate((0.0, 0.0, 0.0125))
    )
    return outer.cut(cavity).translate((basket_cx, 0.0, _basket_cz(r)))


# Two coarse criss-crossed fry sticks resting on the food bed. The fries_heap
# is a non-structural visual food prop (Rule 1, no joint), so we keep it light:
# a bed slab + 2 angled sticks read as "fries in the basket" while avoiding the
# heavy ~11-box boolean union that dominated the dials/drawer compile time.
# (dx_frac, dy_frac, yaw_deg, length): positions are fractions of the bed.
_FRIES = [
    (-0.30, -0.20, 25.0, 0.110),
    (0.20, 0.25, -35.0, 0.110),
]


def _build_drawer_fries(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Light golden-fries prop inside the open-top basket (drawer-local).

    Authored relative to the basket center so the bed rests on the basket floor
    regardless of the joint frame (the basket self-adjusts to a fixed world Z).
    """
    basket_cx = _BASKET_X1 - _BASKET_LEN / 2.0 + _DRAWER_DX
    bed_y = min(r.basket_w - 0.040, 0.170)
    half_x = 0.195 / 2.0
    half_y = bed_y / 2.0
    # The basket inner floor sits ~_BASKET_H/2 - 0.005 below the basket center;
    # the fries bed rests just above it.
    bed_z = _basket_cz(r) - (_BASKET_H / 2.0 - 0.014)
    heap = cq.Workplane("XY").box(0.195, bed_y, 0.018).translate((basket_cx, 0.0, bed_z))
    # Seat the sticks low enough that their underside dips into the bed slab
    # (slab top ~bed_z+0.009; stick centered at bed_z+0.008 -> bottom bed_z+0.001
    # overlaps the slab) so the prop is a single connected island, not floaters.
    for dx_frac, dy_frac, yaw, length in _FRIES:
        fry = (
            cq.Workplane("XY")
            .box(min(length, _BASKET_LEN - 0.05), 0.014, 0.014)
            .rotate((0, 0, 0), (0, 0, 1), yaw)
            .translate((basket_cx + dx_frac * half_x, dy_frac * half_y, bed_z + 0.008))
        )
        heap = heap.union(fry)
    return heap


# ---------------------------------------------------------------------------
# Rotary-dial helpers (control = rotary_dials). Source: dial variant.
# ---------------------------------------------------------------------------
def _build_timer_knob() -> KnobGeometry:
    return KnobGeometry(
        0.044,
        0.022,
        body_style="skirted",
        top_diameter=0.036,
        skirt=KnobSkirt(0.054, 0.005, flare=0.06, chamfer=0.001),
        # 18 knurls (down from 48): the knurled-skirt read survives but the
        # per-grip boolean cut count -- the dominant cost on dials seeds -- drops
        # ~2.7x, keeping the dials seeds well under the wall-time budget.
        grip=KnobGrip(style="knurled", count=18, depth=0.0010, helix_angle_deg=18.0),
        indicator=KnobIndicator(style="line", mode="engraved", depth=0.0008),
        top_feature=KnobTopFeature(style="recessed_dot", diameter=0.004, depth=0.0008),
        center=False,
    )


def _build_temp_knob() -> KnobGeometry:
    return KnobGeometry(
        0.038,
        0.020,
        body_style="skirted",
        top_diameter=0.032,
        skirt=KnobSkirt(0.048, 0.005, flare=0.05, chamfer=0.001),
        # 14 ribs (down from 24): same ribbed read, fewer boolean cuts.
        grip=KnobGrip(style="ribbed", count=14, depth=0.0009, width=0.0014),
        indicator=KnobIndicator(style="wedge", mode="raised", angle_deg=0.0),
        center=False,
    )


def _build_dial_shaft() -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .cylinder(_DIAL_SHAFT_H, _DIAL_SHAFT_R)
        .translate((0.0, 0.0, _DIAL_SHAFT_H / 2.0))
    )


def _build_escutcheon_plate(deck_z: float) -> cq.Workplane:
    # Thick enough to straddle the deck top: bottom embeds into the deepest
    # recess floor (drum recess floor ~deck_z-0.012), top stands ~2mm proud.
    plate = (
        cq.Workplane("XY")
        .box(0.154, 0.114, 0.020)
        .edges("|Z")
        .fillet(0.012)
        .translate((_DIAL_X, 0.0, deck_z - 0.008))
    )
    for hole_y in (-_DIAL_Y_OFFSET, _DIAL_Y_OFFSET):
        hole = (
            cq.Workplane("XY")
            .cylinder(0.020, _DIAL_SHAFT_R * 1.8)
            .translate((_DIAL_X, hole_y, deck_z))
        )
        plate = plate.cut(hole)
    return plate


def _build_dial_bezel(y_offset: float, deck_z: float) -> cq.Workplane:
    # Bezel rim sits on top of the escutcheon plate (plate top ~deck_z+0.002).
    outer = cq.Workplane("XY").cylinder(0.006, 0.030).translate((_DIAL_X, y_offset, deck_z + 0.003))
    inner = (
        cq.Workplane("XY")
        .cylinder(0.008, _DIAL_SHAFT_R * 1.6)
        .translate((_DIAL_X, y_offset, deck_z + 0.003))
    )
    return outer.cut(inner)


def _build_push_button(cx: float, cy: float, base_z: float) -> cq.Workplane:
    """Single recessed tactile push-button pad. Source: buttons _build_push_button."""
    rad = _BUTTON_DIAMETER / 2.0
    h = _BUTTON_HEIGHT
    pad = cq.Workplane("XY").circle(rad).extrude(h).edges(">Z").fillet(0.0015)
    dish = cq.Workplane("XY").circle(rad - 0.002).extrude(0.001).translate((0.0, 0.0, h - 0.0005))
    pad = pad.cut(dish)
    return pad.translate((cx, cy, base_z))


# ---------------------------------------------------------------------------
# Clamshell helpers (basket_opening = clamshell_lid). Source: clamshell variant.
# ---------------------------------------------------------------------------
def _build_clamshell_body_shell(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Lower body bowl: tapered rounded loft 0..split_z, hollowed from top."""
    t = r.split_z / r.body_h
    depth_at_split = r.body_depth_bot + t * (r.body_depth_top - r.body_depth_bot)
    width_at_split = r.body_width_bot + t * (r.body_width_top - r.body_width_bot)
    bottom = cq.Sketch().rect(r.body_depth_bot, r.body_width_bot).vertices().fillet(_CORNER_R)
    top = cq.Sketch().rect(depth_at_split, width_at_split).vertices().fillet(_CORNER_R)
    shell = (
        cq.Workplane("XY")
        .placeSketch(bottom, top.moved(cq.Location(cq.Vector(0.0, 0.0, r.split_z))))
        .loft()
    )
    inner_r = max(_CORNER_R - _WALL_T, 0.005)
    cav_bot = (
        cq.Sketch()
        .rect(r.body_depth_bot - 2 * _WALL_T, r.body_width_bot - 2 * _WALL_T)
        .vertices()
        .fillet(inner_r)
    )
    cav_top = (
        cq.Sketch()
        .rect(depth_at_split - 2 * _WALL_T, width_at_split - 2 * _WALL_T)
        .vertices()
        .fillet(inner_r)
    )
    cavity = (
        cq.Workplane("XY")
        .placeSketch(
            cav_bot.moved(cq.Location(cq.Vector(0.0, 0.0, _WALL_T))),
            cav_top.moved(cq.Location(cq.Vector(0.0, 0.0, r.split_z + 0.002))),
        )
        .loft()
    )
    return shell.cut(cavity)


def _build_clamshell_trim(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Copper trim ring at the split-line seam. Source: clamshell _build_trim_band."""
    t = r.split_z / r.body_h
    depth_at_split = r.body_depth_bot + t * (r.body_depth_top - r.body_depth_bot)
    width_at_split = r.body_width_bot + t * (r.body_width_top - r.body_width_bot)
    outer = _rounded_rect_sketch(
        cq.Workplane("XY", origin=(0.0, 0.0, r.split_z - 0.007)),
        depth_at_split + 0.012,
        width_at_split + 0.012,
        _CORNER_R + 0.006,
    ).extrude(0.016)
    inner = _rounded_rect_sketch(
        cq.Workplane("XY", origin=(0.0, 0.0, r.split_z - 0.014)),
        depth_at_split - 0.002,
        width_at_split - 0.002,
        max(_CORNER_R - 0.001, 0.005),
    ).extrude(0.034)
    return outer.cut(inner)


def _build_fixed_basket(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Open-top cooking basket FIXED inside the lower bowl (body/world coords)."""
    floor_z = _WALL_T - 0.002
    basket_cz = floor_z + _BASKET_H / 2.0
    outer = (
        cq.Workplane("XY").box(_BASKET_LEN, _SINGLE_BASKET_W, _BASKET_H).edges("|Z").fillet(0.015)
    )
    cavity = (
        cq.Workplane("XY")
        .box(_BASKET_LEN - 0.010, _SINGLE_BASKET_W - 0.010, 0.120)
        .edges("|Z")
        .fillet(0.012)
        .translate((0.0, 0.0, 0.0125))
    )
    return outer.cut(cavity).translate((0.0, 0.0, basket_cz))


# Two coarse criss-crossed sticks (cf. _FRIES): the same light food-prop policy
# as the drawer fries, applied to the fixed bowl basket of the clamshell.
_CLAM_FRIES = [
    (-0.035, -0.030, 25.0, 0.100),
    (0.030, 0.035, -35.0, 0.100),
]


def _build_fixed_fries(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Light fries prop fixed in the bowl basket (body/world coords)."""
    floor_z = _WALL_T - 0.002
    bed_z = floor_z + 0.009
    heap = cq.Workplane("XY").box(0.180, 0.160, 0.018).translate((0.0, 0.0, bed_z))
    # Embed sticks into the bed slab (slab top ~bed_z+0.009) so the prop stays a
    # single connected island after the 11->2 box simplification.
    stick_z = bed_z + 0.008
    for fx, fy, yaw, length in _CLAM_FRIES:
        fry = (
            cq.Workplane("XY")
            .box(length, 0.014, 0.014)
            .rotate((0, 0, 0), (0, 0, 1), yaw)
            .translate((fx, fy, stick_z))
        )
        heap = heap.union(fry)
    return heap


def _build_hinge_barrel() -> cq.Workplane:
    """Cylindrical hinge barrel along Y. Source: clamshell _build_hinge_barrel."""
    cyl = (
        cq.Workplane("XY")
        .circle(_BARREL_R)
        .extrude(_BARREL_LEN)
        .translate((0.0, 0.0, -_BARREL_LEN / 2.0))
    )
    return cyl.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)


def _build_lid_shell(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Upper lid dome (lid-local, origin at hinge). Source: clamshell _build_lid_shell."""
    t = r.split_z / r.body_h
    depth_at_split = r.body_depth_bot + t * (r.body_depth_top - r.body_depth_bot)
    width_at_split = r.body_width_bot + t * (r.body_width_top - r.body_width_bot)
    half_ds = depth_at_split / 2.0
    bottom = cq.Sketch().rect(depth_at_split, width_at_split).vertices().fillet(_CORNER_R)
    top = cq.Sketch().rect(r.body_depth_top, r.body_width_top).vertices().fillet(_CORNER_R)
    shell = (
        cq.Workplane("XY")
        .placeSketch(
            bottom.moved(cq.Location(cq.Vector(half_ds, 0.0, 0.0))),
            top.moved(cq.Location(cq.Vector(half_ds, 0.0, r.lid_height))),
        )
        .loft()
    )
    inner_r = max(_CORNER_R - _WALL_T, 0.005)
    cav_bot = (
        cq.Sketch()
        .rect(depth_at_split - 2 * _WALL_T, width_at_split - 2 * _WALL_T)
        .vertices()
        .fillet(inner_r)
    )
    cav_top = (
        cq.Sketch()
        .rect(r.body_depth_top - 2 * _WALL_T, r.body_width_top - 2 * _WALL_T)
        .vertices()
        .fillet(inner_r)
    )
    cavity = (
        cq.Workplane("XY")
        .placeSketch(
            cav_bot.moved(cq.Location(cq.Vector(half_ds, 0.0, -0.002))),
            cav_top.moved(cq.Location(cq.Vector(half_ds, 0.0, r.lid_height - _WALL_T))),
        )
        .loft()
    )
    return shell.cut(cavity)


def _build_lid_handle(r: ResolvedAirFryerConfig) -> cq.Workplane:
    """Horizontal copper bar handle on the lid front face (lid-local)."""
    t = r.split_z / r.body_h
    depth_at_split = r.body_depth_bot + t * (r.body_depth_top - r.body_depth_bot)
    front_x = depth_at_split - 0.006
    handle_z = r.lid_height * 0.60
    boss_sep = 0.052
    boss = cq.Workplane("XY").box(0.018, 0.026, 0.018)
    b0 = boss.translate((front_x + 0.009, -boss_sep, handle_z))
    b1 = boss.translate((front_x + 0.009, boss_sep, handle_z))
    bar = (
        cq.Workplane("XY")
        .box(0.010, 2.0 * boss_sep + 0.026, 0.012)
        .edges("|Y")
        .fillet(0.004)
        .translate((front_x + 0.023, 0.0, handle_z))
    )
    return b0.union(b1).union(bar)


# ---------------------------------------------------------------------------
# Body part assembly (root). Shell mesh + trim band + brand logo + (drawer)
# rails + control hardware. The control panel anchors on the body top deck for
# drawers, and on the lid top for clamshell.
# ---------------------------------------------------------------------------
def _shell_mesh(r: ResolvedAirFryerConfig, assets):
    if r.is_clamshell:
        return _mesh(_build_clamshell_body_shell(r), "body_shell", assets=assets)
    if r.body_silhouette == "square_tower":
        return _mesh(_build_square_shell(r), "body_shell", assets=assets)
    if r.body_silhouette == "cylindrical_drum":
        return _mesh(_build_drum_shell(r), "body_shell", assets=assets)
    return _mesh(_build_rounded_shell(r), "body_shell", assets=assets)


def _trim_mesh(r: ResolvedAirFryerConfig, assets):
    if r.is_clamshell:
        return _mesh(_build_clamshell_trim(r), "rim_trim_band", assets=assets)
    if r.body_silhouette == "square_tower":
        return _mesh(_build_square_trim(r), "rim_trim_band", assets=assets)
    if r.body_silhouette == "cylindrical_drum":
        return _mesh(_build_drum_trim(r), "rim_trim_band", assets=assets)
    return _mesh(_build_rounded_trim(r), "rim_trim_band", assets=assets)


def _emit_top_panel(part, r: ResolvedAirFryerConfig, mats, *, deck_z: float, assets):
    """Control hardware on a deck at deck_z (Rule 1: panels/buttons are visuals;
    only the rotary knobs become REVOLUTE parts, emitted separately)."""
    if r.control == "digital_touch":
        if r.body_silhouette == "cylindrical_drum" and not r.is_clamshell:
            part.visual(
                _mesh(_build_drum_top_glass(r), "top_glass_panel", assets=assets),
                material=mats["glass"],
                name="top_glass_panel", material_class_id="glass.smoked_tinted",
            )
        else:
            part.visual(
                Box((0.220, min(0.180, r.body_width_top - 0.06), 0.006)),
                origin=Origin(xyz=(0.0, 0.0, deck_z - 0.0035)),
                material=mats["glass"],
                name="top_glass_panel", material_class_id="glass.smoked_tinted",
            )
    elif r.control == "push_buttons":
        part.visual(
            Box((0.238, min(0.198, r.body_width_top - 0.04), 0.006)),
            origin=Origin(xyz=(0.0, 0.0, deck_z - 0.0035)),
            material=mats["panel"],
            name="control_panel", material_class_id="plastic.opaque_generic",
        )
        base_z = deck_z - 0.001
        for i in range(_BUTTON_ROWS * _BUTTON_COLS):
            row = i // _BUTTON_COLS
            col = i % _BUTTON_COLS
            cx = (row - (_BUTTON_ROWS - 1) / 2.0) * _BUTTON_SPACING_X
            cy = (col - (_BUTTON_COLS - 1) / 2.0) * _BUTTON_SPACING_Y
            part.visual(
                _mesh(
                    _build_push_button(cx, cy, base_z),
                    f"push_button_{i}",
                    assets=assets,
                    tol=_FINE_TOL,
                    ang=_FINE_ANG,
                ),
                material=mats["button"],
                name=f"push_button_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
    else:  # rotary_dials (escutcheon + bezels are body visuals; knobs are parts)
        part.visual(
            _mesh(_build_escutcheon_plate(deck_z), "escutcheon_plate", assets=assets),
            material=mats["trim"],
            name="escutcheon_plate", material_class_id=("metal.copper_bare" if r.palette_style in {"inox_copper", "retro_cream", "glass_black"} else "metal.brushed_silver"),
        )
        for i, y_off in enumerate((-_DIAL_Y_OFFSET, _DIAL_Y_OFFSET)):
            part.visual(
                _mesh(
                    _build_dial_bezel(y_off, deck_z),
                    f"dial_bezel_{i}",
                    assets=assets,
                    tol=_FINE_TOL,
                    ang=_FINE_ANG,
                ),
                material=mats["trim"],
                name=f"dial_bezel_{i}", material_class_id=("metal.copper_bare" if r.palette_style in {"inox_copper", "retro_cream", "glass_black"} else "metal.brushed_silver"),
            )


def _emit_dial_knobs(model, body, r: ResolvedAirFryerConfig, mats, *, deck_z: float, assets):
    """Two REVOLUTE rotary dials (vertical axis). Source: dial variant."""
    timer = model.part("timer_knob")
    timer.visual(
        mesh_from_geometry(_build_timer_knob(), "timer_knob_cap"),
        material=mats["knob"],
        name="knob_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    timer.visual(
        _mesh(_build_dial_shaft(), "timer_shaft", assets=assets, tol=_FINE_TOL, ang=_FINE_ANG),
        material=mats["shaft"],
        name="shaft", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        "body_to_timer_knob",
        ArticulationType.REVOLUTE,
        parent=body,
        child=timer,
        origin=Origin(xyz=(_DIAL_X, -_DIAL_Y_OFFSET, deck_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=r.timer_sweep),
    )
    temp = model.part("temp_knob")
    temp.visual(
        mesh_from_geometry(_build_temp_knob(), "temp_knob_cap"),
        material=mats["knob"],
        name="knob_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    temp.visual(
        _mesh(_build_dial_shaft(), "temp_shaft", assets=assets, tol=_FINE_TOL, ang=_FINE_ANG),
        material=mats["shaft"],
        name="shaft", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        "body_to_temp_knob",
        ArticulationType.REVOLUTE,
        parent=body,
        child=temp,
        origin=Origin(xyz=(_DIAL_X, _DIAL_Y_OFFSET, deck_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=r.temp_sweep),
    )


# ---------------------------------------------------------------------------
# Drawer population (multiplicity). One drawer subtree per basket.
# ---------------------------------------------------------------------------
def _populate_drawer(part, r: ResolvedAirFryerConfig, mats, meshes, *, windowed: bool):
    face_mesh, handle_mesh, basket_mesh, fries_mesh = meshes
    part.visual(face_mesh, material=mats["shell"], name="drawer_face", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "plastic.opaque_glossy_molded"))
    if windowed:
        part.visual(
            Box((0.005, r.window_w + 0.012, _WINDOW_H + 0.012)),
            origin=Origin(xyz=(-0.0035 + _DRAWER_DX, 0.0, _DRAWER_DZ)),
            material=mats["window"],
            name="window_glass", material_class_id="glass.smoked_tinted",
        )
    part.visual(handle_mesh, material=mats["trim"], name="handle", material_class_id=("metal.copper_bare" if r.palette_style in {"inox_copper", "retro_cream", "glass_black"} else "metal.brushed_silver"))
    part.visual(basket_mesh, material=mats["basket"], name="basket", material_class_id="metal.mesh_chainmail")
    part.visual(fries_mesh, material=mats["fries"], name="fries_heap", material_class_id="organic.biological_surface")


def _emit_drawers(model, body, r: ResolvedAirFryerConfig, mats, *, assets):
    """Emit N drawer subtrees + body rails + per-basket PRISMATIC slides."""
    windowed = r.basket_opening == "windowed_drawer"
    n = r.basket_count

    # Body slide rails (one pair per pocket) + a center pocket-floor sill that
    # carries the drawer and anchors the PRISMATIC origin to real body geometry.
    rail_cz = _POCKET_Z0 + _RAIL_H / 2.0
    sill_w = min(2.0 * r.pocket_hw - 0.012, 2.0 * _SINGLE_RAIL_Y - 0.020)
    for i, cy in enumerate(r.pocket_cys):
        body.visual(
            Box((_SILL_X_FRONT - _SILL_X_BACK, sill_w, _SILL_Z1 - _SILL_Z0)),
            origin=Origin(
                xyz=(
                    (_SILL_X_FRONT + _SILL_X_BACK) / 2.0,
                    cy,
                    (_SILL_Z0 + _SILL_Z1) / 2.0,
                )
            ),
            material=mats["basket"],
            name=f"pocket_sill_{i}", material_class_id="metal.paint_coated",
        )
        if n == 1:
            for j, ry in enumerate((_SINGLE_RAIL_Y, -_SINGLE_RAIL_Y)):
                body.visual(
                    Box((_RAIL_LEN, _RAIL_W, _RAIL_H)),
                    origin=Origin(xyz=(_RAIL_CX, ry, rail_cz)),
                    material=mats["basket"],
                    name=f"slide_rail_{i}_{j}", material_class_id="metal.steel_galvanized",
                )
        else:
            for j, dy in enumerate((_RAIL_OFFSET, -_RAIL_OFFSET)):
                body.visual(
                    Box((_RAIL_LEN, _RAIL_W, _RAIL_H)),
                    origin=Origin(xyz=(_RAIL_CX, cy + dy, rail_cz)),
                    material=mats["basket"],
                    name=f"slide_rail_{i}_{j}", material_class_id="metal.steel_galvanized",
                )

    # Pre-build shared drawer meshes (identical geometry per basket).
    meshes = (
        _mesh(_build_drawer_face(r, windowed=windowed), "drawer_face", assets=assets),
        _mesh(_build_handle(), "drawer_handle", assets=assets),
        _mesh(_build_drawer_basket(r), "cooking_basket", assets=assets),
        _mesh(_build_drawer_fries(r), "fries_heap", assets=assets),
    )

    for i, cy in enumerate(r.pocket_cys):
        drawer = model.part(f"drawer_{i}")
        _populate_drawer(drawer, r, mats, meshes, windowed=windowed)
        model.articulation(
            f"drawer_slide_{i}",
            ArticulationType.PRISMATIC,
            parent=body,
            child=drawer,
            origin=Origin(xyz=(_JOINT_X, cy, _JOINT_Z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=30.0, velocity=0.3, lower=0.0, upper=r.travel),
        )


def _emit_clamshell(model, body, r: ResolvedAirFryerConfig, mats, *, assets):
    """Top-opening clamshell lid (REVOLUTE) + fixed basket on the body bowl."""
    t = r.split_z / r.body_h
    depth_at_split = r.body_depth_bot + t * (r.body_depth_top - r.body_depth_bot)
    half_ds = depth_at_split / 2.0
    hinge_x = -half_ds
    hinge_z = r.split_z

    # Fixed basket + fries inside the bowl (Rule 1: no joint, body visuals).
    body.visual(
        _mesh(_build_fixed_basket(r), "cooking_basket", assets=assets),
        material=mats["basket"],
        name="basket", material_class_id="metal.mesh_chainmail",
    )
    body.visual(
        _mesh(_build_fixed_fries(r), "fries_heap", assets=assets),
        material=mats["fries"],
        name="fries_heap", material_class_id="organic.biological_surface",
    )

    # Hinge barrels at the rear upper edge (captured pivot hardware).
    barrel_mesh = _mesh(
        _build_hinge_barrel(), "hinge_barrel", assets=assets, tol=_FINE_TOL, ang=_FINE_ANG
    )
    for i, y_sign in enumerate((1, -1)):
        body.visual(
            barrel_mesh,
            origin=Origin(xyz=(hinge_x + 0.004, y_sign * _BARREL_Y_OFFSET, hinge_z)),
            material=mats["hinge"],
            name=f"hinge_barrel_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"inox_copper", "matte_graphite", "glass_black"} else "metal.brushed_silver"),
        )

    # Lid part: shell + top glass panel + front handle.
    lid = model.part("lid")
    lid.visual(
        _mesh(_build_lid_shell(r), "lid_shell", assets=assets),
        material=mats["shell"],
        name="lid_shell", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "plastic.opaque_glossy_molded"),
    )
    lid.visual(
        Box((0.220, min(0.180, r.body_width_top - 0.06), 0.006)),
        origin=Origin(xyz=(half_ds, 0.0, r.lid_height + 0.003)),
        material=mats["glass"],
        name="top_glass_panel", material_class_id="glass.smoked_tinted",
    )
    lid.visual(
        _mesh(_build_lid_handle(r), "lid_handle", assets=assets, tol=_FINE_TOL, ang=_FINE_ANG),
        material=mats["trim"],
        name="lid_handle", material_class_id=("metal.copper_bare" if r.palette_style in {"inox_copper", "retro_cream", "glass_black"} else "metal.brushed_silver"),
    )
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=r.lid_open),
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_air_fryer(
    config: AirFryerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"air_fryer_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    # Root body part: shell + trim + brand logo.
    body = model.part("body")
    body.visual(_shell_mesh(r, assets), material=mats["shell"], name="shell", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "plastic.opaque_glossy_molded"))
    body.visual(_trim_mesh(r, assets), material=mats["trim"], name="rim_trim_band", material_class_id=("metal.copper_bare" if r.palette_style in {"inox_copper", "retro_cream", "glass_black"} else "metal.brushed_silver"))
    # Brand logo on the front face, embedded ~3mm into the front wall so it is a
    # supported visual (not a floating island). The front wall x at the logo
    # height: tapered body interpolates depth_bot..depth_top; cylindrical uses
    # the flat front facet; clamshell uses the bowl front below the split.
    logo_z = 0.155 if r.is_clamshell else 0.210
    if r.body_silhouette == "cylindrical_drum" and not r.is_clamshell:
        wall_x = _FLAT_FRONT_X
    elif r.body_silhouette == "square_tower" and not r.is_clamshell:
        # No taper: the front wall is uniformly at depth_top/2.
        wall_x = r.body_depth_top / 2.0
    elif r.is_clamshell:
        wall_x = r.body_depth_bot / 2.0
    else:
        frac = min(max(logo_z / r.body_h, 0.0), 1.0)
        wall_x = (r.body_depth_bot + frac * (r.body_depth_top - r.body_depth_bot)) / 2.0
    body.visual(
        Box((0.008, 0.070, 0.016)),
        origin=Origin(xyz=(wall_x - 0.001, 0.0, logo_z)),
        material=mats["trim"],
        name="brand_logo", appearance_only=AppearanceOnlySpec(kind="decal"),
    )

    if r.is_clamshell:
        # Control panel lives on the LID top (digital_touch only, gated).
        _emit_clamshell(model, body, r, mats, assets=assets)
    else:
        deck_z = r.body_h
        _emit_top_panel(body, r, mats, deck_z=deck_z, assets=assets)
        if r.control == "rotary_dials":
            _emit_dial_knobs(model, body, r, mats, deck_z=deck_z, assets=assets)
        _emit_drawers(model, body, r, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_air_fryer(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_air_fryer(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_air_fryer_tests(
    object_model: ArticulatedObject,
    config: AirFryerConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")

    # ---- Captured-slide / pin / shaft allowances (element-scoped). ----
    if r.is_drawer:
        for i in range(r.basket_count):
            drawer = object_model.get_part(f"drawer_{i}")
            for j in range(2):
                rail = f"slide_rail_{i}_{j}"
                ctx.allow_overlap(
                    drawer,
                    body,
                    elem_a="basket",
                    elem_b=rail,
                    reason=(
                        "Basket bottom seats 2 mm into the slide-rail tops so the "
                        "sliding drawer is mechanically carried by the body rails."
                    ),
                )
                ctx.expect_overlap(
                    drawer,
                    body,
                    axes="z",
                    elem_a="basket",
                    elem_b=rail,
                    min_overlap=0.001,
                    name=f"drawer_{i} basket seats on {rail}",
                )
            sill = f"pocket_sill_{i}"
            ctx.allow_overlap(
                drawer,
                body,
                elem_a="basket",
                elem_b=sill,
                reason="Basket bottom seats 2 mm into the pocket-floor sill that carries it.",
            )
            ctx.allow_overlap(
                drawer,
                body,
                elem_a="fries_heap",
                elem_b=sill,
                reason="The fries-bed underside grazes the pocket-floor sill inside the basket.",
            )
    elif r.is_clamshell:
        lid = object_model.get_part("lid")
        for i in range(2):
            ctx.allow_overlap(
                body,
                lid,
                elem_a=f"hinge_barrel_{i}",
                elem_b="lid_shell",
                reason=f"Hinge barrel {i} is captured inside the lid rear wall for the pivot.",
            )
            ctx.expect_overlap(
                body,
                lid,
                axes="z",
                elem_a=f"hinge_barrel_{i}",
                elem_b="lid_shell",
                min_overlap=0.001,
                name=f"hinge_barrel_{i} nests inside lid rear wall",
            )
        ctx.allow_overlap(
            body,
            lid,
            elem_a="rim_trim_band",
            elem_b="lid_shell",
            reason="Copper trim band wraps around the split seam into the lid shell wall.",
        )
        ctx.expect_overlap(
            body,
            lid,
            axes="z",
            elem_a="rim_trim_band",
            elem_b="lid_shell",
            min_overlap=0.001,
            name="trim band overlaps the lid seam region",
        )
        ctx.allow_overlap(
            body,
            lid,
            reason="closed lid seats on the body bowl at the split seam.",
        )

    if r.control == "rotary_dials":
        for idx, kpart in enumerate(("timer_knob", "temp_knob")):
            ctx.allow_overlap(
                object_model.get_part(kpart),
                body,
                elem_a="shaft",
                reason="Dial shaft is intentionally seated through the deck shaft hole.",
            )
            ctx.allow_overlap(
                object_model.get_part(kpart),
                body,
                elem_a="knob_cap",
                elem_b=f"dial_bezel_{idx}",
                reason="The knob cap/skirt overhangs the copper bezel ring around its shaft.",
            )
            ctx.allow_overlap(
                object_model.get_part(kpart),
                body,
                elem_a="knob_cap",
                elem_b="escutcheon_plate",
                reason="The knob skirt rests over the escutcheon plate around the shaft hole.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("body part present (root)", "body" in part_names, details=str(sorted(part_names)))

    # Body grounded near z=0 with a realistic countertop footprint.
    aabb = ctx.part_world_aabb(body)
    if aabb is not None:
        (xmn, ymn, zmn), (xmx, ymx, zmx) = aabb
        ctx.check("body grounded at z=0", zmn < 0.01, details=f"zmin={zmn:.4f}")
        ctx.check(
            "body depth in countertop range",
            0.26 <= (xmx - xmn) <= 0.40,
            details=f"depth={xmx - xmn:.3f}",
        )
        ctx.check(
            "body width grows with basket count",
            0.22 <= (ymx - ymn) <= 0.72,
            details=f"width={ymx - ymn:.3f} N={r.basket_count}",
        )

    # ---- Defining-motion joint topology. ----
    if r.is_drawer:
        for i in range(r.basket_count):
            slide = object_model.get_articulation(f"drawer_slide_{i}")
            ctx.check(
                f"drawer_{i} slide is PRISMATIC about +X",
                slide.articulation_type == ArticulationType.PRISMATIC
                and abs(slide.axis[0] - 1.0) < 1e-6
                and abs(slide.axis[1]) < 1e-6
                and abs(slide.axis[2]) < 1e-6,
                details=f"type={slide.articulation_type} axis={tuple(slide.axis)}",
            )
            lim = slide.motion_limits
            ctx.check(
                f"drawer_{i} travel is positive and bounded",
                lim is not None and abs(lim.lower) < 1e-9 and 0.10 < lim.upper < 0.20,
                details=f"limits={lim}",
            )

        # solid_drawer has no window glass.
        d0 = object_model.get_part("drawer_0")
        d0_visuals = {v.name for v in d0.visuals}
        if r.basket_opening == "solid_drawer":
            ctx.check(
                "solid drawer has no window_glass",
                "window_glass" not in d0_visuals,
                details=str(sorted(d0_visuals)),
            )
        else:
            ctx.check(
                "windowed drawer has window_glass",
                "window_glass" in d0_visuals,
                details=str(sorted(d0_visuals)),
            )

        # Drawer slides forward and basket retains insertion at full travel.
        for i in range(r.basket_count):
            drawer = object_model.get_part(f"drawer_{i}")
            slide = object_model.get_articulation(f"drawer_slide_{i}")
            closed = ctx.part_world_position(drawer)
            with ctx.pose({slide: r.travel}):
                opened = ctx.part_world_position(drawer)
                ctx.expect_overlap(
                    drawer,
                    body,
                    axes="x",
                    elem_a="basket",
                    min_overlap=0.04,
                    name=f"drawer_{i} basket retains insertion at full travel",
                )
            if closed is not None and opened is not None:
                ctx.check(
                    f"drawer_{i} slides forward by full travel",
                    abs((opened[0] - closed[0]) - r.travel) < 1e-6
                    and abs(opened[1] - closed[1]) < 1e-9,
                    details=f"closed={closed} open={opened}",
                )

        # Independence: opening drawer_0 leaves drawer_1 in place.
        if r.basket_count >= 2:
            d1_rest = ctx.part_world_position(object_model.get_part("drawer_1"))
            with ctx.pose({object_model.get_articulation("drawer_slide_0"): r.travel}):
                d1_open = ctx.part_world_position(object_model.get_part("drawer_1"))
            ctx.check(
                "drawer_1 stays put when drawer_0 opens",
                d1_rest is not None and d1_open is not None and abs(d1_open[0] - d1_rest[0]) < 1e-6,
                details=f"d1_rest={d1_rest} d1_open={d1_open}",
            )
    else:  # clamshell
        hinge = object_model.get_articulation("lid_hinge")
        ctx.check(
            "lid hinge is REVOLUTE about -Y",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[0]) < 1e-6
            and abs(hinge.axis[1] + 1.0) < 1e-6
            and abs(hinge.axis[2]) < 1e-6,
            details=f"type={hinge.articulation_type} axis={tuple(hinge.axis)}",
        )
        lim = hinge.motion_limits
        ctx.check(
            "lid hinge sweeps upward to a realistic open angle",
            lim is not None and abs(lim.lower) < 1e-9 and 1.4 < lim.upper < math.pi,
            details=f"limits={lim}",
        )
        # Basket is FIXED on the body (no drawer part, no PRISMATIC).
        basket_aabb = ctx.part_element_world_aabb(body, elem="basket")
        ctx.check("clamshell basket fixed on body", basket_aabb is not None)
        ctx.check(
            "clamshell has no drawer part",
            not any(p.name.startswith("drawer_") for p in object_model.parts),
            details=str(sorted(p.name for p in object_model.parts)),
        )
        # Lid rises above the body when opened.
        lid = object_model.get_part("lid")
        closed = ctx.part_world_aabb(lid)
        with ctx.pose({hinge: r.lid_open * 0.8}):
            opened = ctx.part_world_aabb(lid)
        if closed is not None and opened is not None:
            ctx.check(
                "lid rises above the body when opened",
                opened[1][2] > closed[1][2] + 0.04,
                details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
            )

    # ---- Control joint topology. ----
    if r.control == "rotary_dials":
        for name in ("body_to_timer_knob", "body_to_temp_knob"):
            j = object_model.get_articulation(name)
            ctx.check(
                f"{name} is REVOLUTE about +Z",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2] - 1.0) < 1e-6,
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
            lim = j.motion_limits
            ctx.check(
                f"{name} has a realistic sweep",
                lim is not None and 3.0 < lim.upper < 6.3,
                details=f"limits={lim}",
            )
        # Knob rotates in place (pure rotation, no translation).
        timer = object_model.get_part("timer_knob")
        rest = ctx.part_world_position(timer)
        with ctx.pose({object_model.get_articulation("body_to_timer_knob"): 2.5}):
            turned = ctx.part_world_position(timer)
        if rest is not None and turned is not None:
            ctx.check(
                "timer dial rotates in place",
                all(abs(turned[k] - rest[k]) < 1e-6 for k in range(3)),
                details=f"rest={rest} turned={turned}",
            )
    elif r.control == "push_buttons":
        btn_visuals = [v.name for v in body.visuals if v.name.startswith("push_button")]
        ctx.check(
            "push-button 2x3 grid present (6 pads, Rule 1)",
            len(btn_visuals) == _BUTTON_ROWS * _BUTTON_COLS,
            details=f"buttons={sorted(btn_visuals)}",
        )

    # ---- Copper trim band wraps the rim. ----
    band = ctx.part_element_world_aabb(body, elem="rim_trim_band")
    ctx.check("copper trim band present", band is not None)

    # ---- slot_choices recorded with N encoded for drawers. ----
    ctx.check(
        "slot_choices recorded and consistent with build",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "AirFryerConfig",
    "ResolvedAirFryerConfig",
    "build_air_fryer",
    "build_seeded_air_fryer",
    "config_from_seed",
    "resolve_config",
    "run_air_fryer_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
