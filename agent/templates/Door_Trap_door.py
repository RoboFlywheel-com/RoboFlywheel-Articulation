# SPDX-License-Identifier: Apache-2.0

"""Horizontal floor / ceiling access hatch (trap door) modular template.

A **trap door** is a horizontal access hatch set into a floor / deck / ground
plane: a movable leaf that lies FLAT when closed (its hinge axis is horizontal)
and swings UP to expose a vertical shaft / well below. The shared skeleton (every
5-star source has it) is a 3-tier stack rooted on the ground:

  ``well_shaft`` (hollow round or square concrete shaft, base z=0, open bore)
    --[FIXED at z=SHAFT_HEIGHT]--> support coaming (flush mesh collar OR raised
                                   kerb curb), carrying the collar-side hinge
                                   lug plates + pin on the rear band/wall
        --[REVOLUTE axis world -X, range 0..~2.0]--> leaf
              leaf = Slot A fill x Slot C footprint x Slot D grip, carrying a
              coaxial knuckle barrel at the part origin (on the hinge axis).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Door_Trap_Door_Door.md`` and the 5-star
trap-door pool (1 parent + converged single-axis fork variants) under
``data/records/rec_door_trapdoor`` and ``rec_trapdoor_var_*``.

Pattern = ``mixed`` (parallel children: a fixed support chassis with a parallel
movable leaf; the leaf carries an internal multiplicity fill axis
(planks / slats); the hinge slot is either one revolute or two opposite-axis
per-copy revolutes; the grip slot may add a nested revolute).

Slots:
  * Slot A ``leaf_fill`` (4): solid_cast_slab / checker_plate_steel /
    planked_deck (N planks) / barred_grate (N slats). The fill is the leaf body
    geometry; preserves the source primitive (LatheGeometry disc / Box plate +
    diamond tread / N Box planks / border frame + N Box slats).
  * Slot B ``hinge_mechanism`` (2): single_revolute_flap (1 REVOLUTE -X) /
    double_bifold (2 half-disc leaves, each its own opposite-sign REVOLUTE).
  * Slot C ``footprint`` (3): round / square / rectangular (forced by leaf_fill).
  * Slot D ``grip`` (4): cross_wheel_relief / recessed_ring_pull / rope_loop_pull
    (no joint) / folding_bar_handle (nested lid->handle REVOLUTE).
  * Support sub-axis ``support_coaming`` (2): flush_mesh_collar /
    raised_rect_kerb_curb (FIXED, fixed support, no joint).
  * Shaft profile ``shaft_profile`` (2): round_cylinder / hollow_square. Both
    are bottomless wall shells. The mesh collar retains a circular throat ring;
    the bar-free raised curb omits that ring and exposes its square opening.
  * Multiplicity: ``plank_count`` (planked_deck) / ``grate_slat_count``
    (barred_grate) -- N inlined visuals (Rule 1) on the leaf carrier part. N is
    encoded into the slot_choice tuple as ``("plank_count", f"n{N}")`` etc.

Compatibility gating (resolve_config, spec §slot graph):
  * footprint is forced by leaf_fill: cast->round, checker/plank->square,
    grate->rectangular.
  * double_bifold only when leaf_fill=solid_cast_slab AND footprint=round; it
    forces grip=cross_wheel_relief and support=flush_mesh_collar.
  * folding_bar_handle only on a solid face (solid_cast_slab / checker_plate)
    single-flap leaf; never on grate / bifold.
  * barred_grate has no solid face -> grip degrades to cross_wheel_relief
    (a flush recessed visual that needs no solid panel: rendered as a plain
    rim relief at the rear frame bar).
  * raised_rect_kerb_curb gated off double_bifold.

3 hard rules:
  (1) every non-moving decoration (relief, tread, bolts, planks, slats, ring,
      rope, eyelets, pocket) is a parent ``.visual(...)``, not a FIXED part.
  (2) every non-FIXED joint that creates a separate child part declares a
      ``MatingContract`` where the geometry permits, else is grandfathered as a
      captured-pin overlap with an element-scoped ``allow_overlap``.
  (3) no Box/Cylinder downgrade: round hatch + cross-wheel relief use
      LatheGeometry / TorusGeometry / mesh; bifold half-discs use CadQuery.
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
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    ExtrudeGeometry,
    Inertial,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

LeafFill = Literal["solid_cast_slab", "checker_plate_steel", "planked_deck", "barred_grate"]
HingeMechanism = Literal["single_revolute_flap", "double_bifold"]
Footprint = Literal["round", "square", "rectangular"]
Grip = Literal["cross_wheel_relief", "recessed_ring_pull", "rope_loop_pull", "folding_bar_handle"]
SupportCoaming = Literal["flush_mesh_collar", "raised_rect_kerb_curb"]
ShaftProfile = Literal["round_cylinder", "hollow_square"]
PaletteStyle = Literal[
    "cast_iron",
    "checker_plate_steel",
    "weathered_planks",
    "gunmetal_grate",
    "painted_kerb_curb",
]

LEAF_FILLS: tuple[LeafFill, ...] = (
    "solid_cast_slab",
    "checker_plate_steel",
    "planked_deck",
    "barred_grate",
)
HINGE_MECHANISMS: tuple[HingeMechanism, ...] = ("single_revolute_flap", "double_bifold")
GRIPS: tuple[Grip, ...] = (
    "cross_wheel_relief",
    "recessed_ring_pull",
    "rope_loop_pull",
    "folding_bar_handle",
)
SUPPORT_COAMINGS: tuple[SupportCoaming, ...] = ("flush_mesh_collar", "raised_rect_kerb_curb")
SHAFT_PROFILES: tuple[ShaftProfile, ...] = ("round_cylinder", "hollow_square")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "cast_iron",
    "checker_plate_steel",
    "weathered_planks",
    "gunmetal_grate",
    "painted_kerb_curb",
)

# Leaf-fill -> forced footprint (spec sampler order step 2).
FILL_FOOTPRINT: dict[LeafFill, Footprint] = {
    "solid_cast_slab": "round",
    "checker_plate_steel": "square",
    "planked_deck": "square",
    "barred_grate": "rectangular",
}
# Leaf-fill -> the palette style whose colorway matches the fill.
FILL_PALETTE: dict[LeafFill, PaletteStyle] = {
    "solid_cast_slab": "cast_iron",
    "checker_plate_steel": "checker_plate_steel",
    "planked_deck": "weathered_planks",
    "barred_grate": "gunmetal_grate",
}
# Solid (non-see-through) faces that can host a folding_bar_handle pocket.
SOLID_FACE_FILLS: tuple[LeafFill, ...] = ("solid_cast_slab", "checker_plate_steel")

# Multiplicity ranges (spec §params). Product range vs test range; we sample the
# test range so the sweep covers the small-N domain where geometry is exercised.
PLANK_N_MIN, PLANK_N_MAX = 4, 9
GRATE_N_MIN, GRATE_N_MAX = 6, 14
# Weighted small-N draws (4-6 common, 7-9 tail for planks; 6-10 common etc).
PLANK_WEIGHTS = {4: 0.30, 5: 0.22, 6: 0.20, 7: 0.13, 8: 0.09, 9: 0.06}
GRATE_WEIGHTS = {6: 0.18, 7: 0.16, 8: 0.15, 9: 0.13, 10: 0.12, 11: 0.10, 12: 0.08, 13: 0.05, 14: 0.03}

# ---------------------------------------------------------------------------
# Palettes (spec §params; every .visual material is drawn from the active
# palette, mirroring cushion.py). Keys cover every visual role across all slots.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cast_iron": {
        "concrete": (0.70, 0.69, 0.66, 1.0),
        "leaf": (0.46, 0.21, 0.15, 1.0),
        "relief": (0.12, 0.10, 0.09, 1.0),
        "coaming": (0.22, 0.13, 0.10, 1.0),
        "hardware": (0.30, 0.18, 0.12, 1.0),
        "accent": (0.55, 0.50, 0.46, 1.0),
        "rope": (0.74, 0.62, 0.40, 1.0),
    },
    "checker_plate_steel": {
        "concrete": (0.70, 0.69, 0.66, 1.0),
        "leaf": (0.60, 0.62, 0.64, 1.0),
        "relief": (0.40, 0.42, 0.45, 1.0),
        "coaming": (0.22, 0.13, 0.10, 1.0),
        "hardware": (0.50, 0.52, 0.55, 1.0),
        "accent": (0.66, 0.68, 0.70, 1.0),
        "rope": (0.74, 0.62, 0.40, 1.0),
    },
    "weathered_planks": {
        "concrete": (0.70, 0.69, 0.66, 1.0),
        "leaf": (0.55, 0.38, 0.22, 1.0),
        "relief": (0.35, 0.22, 0.12, 1.0),
        "coaming": (0.22, 0.13, 0.10, 1.0),
        "hardware": (0.30, 0.18, 0.12, 1.0),
        "accent": (0.42, 0.28, 0.16, 1.0),
        "rope": (0.78, 0.66, 0.44, 1.0),
    },
    "gunmetal_grate": {
        "concrete": (0.70, 0.69, 0.66, 1.0),
        "leaf": (0.38, 0.40, 0.43, 1.0),
        "relief": (0.28, 0.30, 0.33, 1.0),
        "coaming": (0.22, 0.13, 0.10, 1.0),
        "hardware": (0.46, 0.48, 0.51, 1.0),
        "accent": (0.44, 0.46, 0.49, 1.0),
        "rope": (0.74, 0.62, 0.40, 1.0),
    },
    "painted_kerb_curb": {
        "concrete": (0.66, 0.66, 0.64, 1.0),
        "leaf": (0.30, 0.36, 0.44, 1.0),
        "relief": (0.16, 0.20, 0.26, 1.0),
        "coaming": (0.20, 0.24, 0.30, 1.0),
        "hardware": (0.40, 0.44, 0.50, 1.0),
        "accent": (0.55, 0.58, 0.62, 1.0),
        "rope": (0.74, 0.62, 0.40, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Absolute base dimensions (meters). From rec_door_trapdoor and the variants;
# near-identical across the whole pool.
# ---------------------------------------------------------------------------
_SHAFT_OUTER_R = 0.40
_SHAFT_WALL = 0.085
_SHAFT_INNER_R = _SHAFT_OUTER_R - _SHAFT_WALL  # ~0.315
_SHAFT_HEIGHT = 0.52

_COLLAR_HALF = 0.40
_COLLAR_FRAME = 0.06
_COLLAR_THK = 0.05

_LID_R = 0.36          # round disc radius (also square/rect half base)
_LID_THK = 0.05
_LID_RIM_SEAT = 0.015

_RECESS_OUTER_R = 0.290
_RECESS_DEPTH = 0.026
_RELIEF_TOP_Z = 0.018
_RELIEF_RING_R = 0.245
_HUB_R = 0.070
_SPOKE_HALF_W = 0.050
_N_SPOKES = 4
_BOLT_R = 0.014
_N_BOLTS = 12
_BOLT_RING_R = 0.320

_HINGE_PIN_R = 0.020
_HINGE_KNUCKLE_LEN = 0.17
_HINGE_LUG_X = 0.10
_HINGE_LUG_THK = 0.03

# Curb (raised kerb) base dims.
_CURB_HALF = 0.42
_CURB_WALL = 0.06
_CURB_BASE_THK = 0.025
_CURB_WALL_H = 0.14

# Checker-plate.
_HATCH_PLATE_THK = 0.008
_HATCH_LIP_HEIGHT = 0.010
_HATCH_RIM_SEAT = 0.015
_TREAD_LEN = 0.030
_TREAD_W = 0.010
_TREAD_H = 0.003
_TREAD_SPACING = 0.045
_TREAD_INSET = 0.040

# Planks.
_PLANK_THK = 0.040
_PLANK_GAP = 0.003
_BATTEN_W = 0.060
_BATTEN_THK = 0.025
_BATTEN_INSET = 0.04
_N_BATTENS = 2

# Grate.
_GRATE_W = 0.66
_GRATE_D = 0.70
_FRAME_BAR_W = 0.035
_FRAME_BAR_H = 0.050
_SLAT_W = 0.012
_SLAT_H = 0.030

# Ring pull.
_POCKET_R = 0.080
_POCKET_DEPTH = 0.020
_RING_PULL_R = 0.055
_RING_PULL_TUBE_R = 0.010

# Rope loop.
_ROPE_EYELET_SPACING = 0.16
_ROPE_LOOP_HEIGHT = 0.065
_ROPE_RADIUS = 0.012
_N_EYELETS = 2
_EYELET_R = 0.016
_EYELET_TUBE_R = 0.005

# Folding bar handle.
_POCKET_LEN = 0.22
_POCKET_WID = 0.065
_HANDLE_POCKET_DEPTH = 0.018
_HANDLE_LEN = 0.19
_HANDLE_WID = 0.040
_HANDLE_THK = 0.013
_HANDLE_HINGE_R = 0.007
_HANDLE_HINGE_LEN = 0.038
_N_HANDLE_LUGS = 2
_HANDLE_LUG_WID = 0.010
_HANDLE_LUG_DEPTH = 0.014
_HANDLE_PIN_R = 0.005


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


@dataclass(frozen=True)
class TrapDoorConfig:
    leaf_fill: LeafFill | None = None
    hinge_mechanism: HingeMechanism | None = None
    footprint: Footprint | None = None
    grip: Grip | None = None
    support_coaming: SupportCoaming | None = None
    shaft_profile: ShaftProfile | None = None
    plank_count: int | None = None
    grate_slat_count: int | None = None
    palette_style: PaletteStyle | None = None
    leaf_radius_scale: float = 1.0
    shaft_height_scale: float = 1.0
    hinge_open_upper: float = 2.0
    curb_wall_height_scale: float = 1.0
    name: str = "trap_door"


@dataclass(frozen=True)
class ResolvedTrapDoorConfig:
    leaf_fill: LeafFill
    hinge_mechanism: HingeMechanism
    footprint: Footprint
    grip: Grip
    support_coaming: SupportCoaming
    shaft_profile: ShaftProfile
    plank_count: int
    grate_slat_count: int
    palette_style: PaletteStyle
    # Derived geometry.
    shaft_outer_r: float
    shaft_inner_r: float
    shaft_height: float
    throat_r: float
    # Coaming: top plane that the leaf seats on, throat-lip top plane, hinge Z.
    coaming_top_z: float       # collar frame top OR curb wall top (part-local)
    throat_lip_top: float      # top of throat ring lip (part-local)
    lid_r: float               # leaf radius / square half / rect base
    grate_w: float
    grate_d: float
    hinge_y: float             # rear hinge line Y (collar/curb part frame)
    hinge_z: float             # hinge pin Z (collar/curb part frame)
    hinge_lug_top: float
    hinge_open_upper: float
    curb_wall_h: float
    name: str

    @property
    def is_curb(self) -> bool:
        return self.support_coaming == "raised_rect_kerb_curb"


def config_from_seed(seed: int) -> TrapDoorConfig:
    rng = random.Random(seed)
    # (1) leaf_fill weighted draw.
    leaf_fill: LeafFill = rng.choices(
        list(LEAF_FILLS), weights=[0.34, 0.24, 0.21, 0.21], k=1
    )[0]
    # (2) footprint forced by leaf_fill.
    footprint = FILL_FOOTPRINT[leaf_fill]
    # (3) hinge_mechanism: double_bifold only eligible on cast+round.
    if leaf_fill == "solid_cast_slab":
        hinge_mechanism: HingeMechanism = rng.choices(
            list(HINGE_MECHANISMS), weights=[0.62, 0.38], k=1
        )[0]
    else:
        hinge_mechanism = "single_revolute_flap"
    # (4) grip weighted, gated downstream in resolve.
    if leaf_fill == "barred_grate":
        grip: Grip = "cross_wheel_relief"  # no solid face -> rim relief
    elif hinge_mechanism == "double_bifold":
        grip = "cross_wheel_relief"
    elif leaf_fill == "solid_cast_slab":
        # The cast disc has a recessed panel: it hosts every grip (ring pull /
        # rope loop / fold handle all nest into the recess in the source pool).
        grip = rng.choices(list(GRIPS), weights=[0.30, 0.26, 0.22, 0.22], k=1)[0]
    elif leaf_fill == "checker_plate_steel":
        # The flat checker plate has no recessed panel for a nested grip; its
        # identity feature is the diamond tread itself -> plain rim relief only.
        grip = "cross_wheel_relief"
    else:  # planked_deck: flat timber deck (no recess) -> plain rim relief only
        grip = "cross_wheel_relief"
    # (5) support_coaming weighted (kerb gated off bifold downstream).
    if hinge_mechanism == "double_bifold":
        support_coaming: SupportCoaming = "flush_mesh_collar"
    else:
        support_coaming = rng.choices(
            list(SUPPORT_COAMINGS), weights=[0.62, 0.38], k=1
        )[0]
    # (6) multiplicity N per-axis weighted small-N.
    plank_count = rng.choices(
        list(PLANK_WEIGHTS), weights=list(PLANK_WEIGHTS.values()), k=1
    )[0]
    grate_slat_count = rng.choices(
        list(GRATE_WEIGHTS), weights=list(GRATE_WEIGHTS.values()), k=1
    )[0]
    # (palette) fill-aware; mostly the matching colorway, with variety.
    if rng.random() < 0.62:
        palette_style: PaletteStyle = FILL_PALETTE[leaf_fill]
    elif support_coaming == "raised_rect_kerb_curb" and rng.random() < 0.5:
        palette_style = "painted_kerb_curb"
    else:
        palette_style = rng.choice(list(PALETTE_STYLES))
    # (7) continuous scales. Resolve these before the newly added shaft draw so
    # pre-existing seeds retain their earlier non-shaft dimensions.
    leaf_radius_scale = round(rng.uniform(0.92, 1.10), 4)
    shaft_height_scale = round(rng.uniform(0.85, 1.20), 4)
    hinge_open_upper = round(rng.uniform(1.7, 2.2), 4)
    curb_wall_height_scale = round(rng.uniform(0.8, 1.3), 4)
    # (8) round source shaft or square hollow vault body. The circular mouth is
    # supplied by either coaming candidate for both body profiles.
    shaft_profile: ShaftProfile = rng.choices(
        list(SHAFT_PROFILES), weights=[0.55, 0.45], k=1
    )[0]
    return TrapDoorConfig(
        leaf_fill=leaf_fill,
        hinge_mechanism=hinge_mechanism,
        footprint=footprint,
        grip=grip,
        support_coaming=support_coaming,
        shaft_profile=shaft_profile,
        plank_count=plank_count,
        grate_slat_count=grate_slat_count,
        palette_style=palette_style,
        leaf_radius_scale=leaf_radius_scale,
        shaft_height_scale=shaft_height_scale,
        hinge_open_upper=hinge_open_upper,
        curb_wall_height_scale=curb_wall_height_scale,
        name=f"seeded_trap_door_{seed}",
    )


def resolve_config(config: TrapDoorConfig | None = None) -> ResolvedTrapDoorConfig:
    cfg = config or TrapDoorConfig()

    leaf_fill = _pick(cfg.leaf_fill, LEAF_FILLS)
    footprint = FILL_FOOTPRINT[leaf_fill]  # always forced (ignore stray override)

    # --- Compatibility gating (resolve is the only legalization entry). ---
    hinge_mechanism = _pick(cfg.hinge_mechanism, HINGE_MECHANISMS)
    if hinge_mechanism == "double_bifold" and not (
        leaf_fill == "solid_cast_slab" and footprint == "round"
    ):
        hinge_mechanism = "single_revolute_flap"

    grip = _pick(cfg.grip, GRIPS)
    if hinge_mechanism == "double_bifold":
        grip = "cross_wheel_relief"
    elif leaf_fill == "barred_grate":
        grip = "cross_wheel_relief"  # see-through face -> plain rim relief
    elif leaf_fill != "solid_cast_slab":
        # Only the cast disc has the recessed panel the ring-pull / rope-loop /
        # fold-handle grips nest into; flat checker/plank decks degrade to the
        # plain rim relief (which passes through the body, staying connected).
        grip = "cross_wheel_relief"
    # ring_pull / rope_loop / fold_handle are valid only on the solid_cast_slab
    # single-flap leaf (or cross_wheel on bifold, handled above).

    support_coaming = _pick(cfg.support_coaming, SUPPORT_COAMINGS)
    if hinge_mechanism == "double_bifold":
        support_coaming = "flush_mesh_collar"  # kerb gated off bifold

    shaft_profile = _pick(cfg.shaft_profile, SHAFT_PROFILES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    plank_count = int(cfg.plank_count) if cfg.plank_count is not None else 6
    plank_count = int(_clamp(plank_count, PLANK_N_MIN, PLANK_N_MAX))
    grate_slat_count = (
        int(cfg.grate_slat_count) if cfg.grate_slat_count is not None else 12
    )
    grate_slat_count = int(_clamp(grate_slat_count, GRATE_N_MIN, GRATE_N_MAX))

    # --- Continuous scales (clamp). ---
    leaf_scale = _clamp(cfg.leaf_radius_scale, 0.92, 1.10)
    shaft_scale = _clamp(cfg.shaft_height_scale, 0.85, 1.20)
    hinge_open_upper = _clamp(cfg.hinge_open_upper, 1.7, 2.2)
    curb_scale = _clamp(cfg.curb_wall_height_scale, 0.8, 1.3)

    shaft_outer_r = _SHAFT_OUTER_R
    shaft_inner_r = _SHAFT_INNER_R
    shaft_height = _SHAFT_HEIGHT * shaft_scale
    throat_r = shaft_inner_r + 0.01  # unchanged formula

    lid_r = _LID_R * leaf_scale
    grate_w = _GRATE_W * leaf_scale
    grate_d = _GRATE_D * leaf_scale

    # --- Leaf-seat inequality (spec): the leaf half-extent must clear the throat
    #     by >=0.02 so the rim always seats on the lip and never hangs over the
    #     opening. Grow the leaf if a small leaf_radius_scale shrank it too far. ---
    min_half = throat_r + 0.02
    if lid_r < min_half:
        lid_r = min_half
    if grate_w / 2.0 < min_half:
        grate_w = 2.0 * min_half
    # Keep the grate front span (depth - hinge front) clearing the throat too.
    if grate_d < 2.0 * min_half:
        grate_d = 2.0 * min_half

    # --- Coaming-dependent hinge geometry (re-derived by equation). ---
    if support_coaming == "raised_rect_kerb_curb":
        curb_wall_h = _CURB_WALL_H * curb_scale
        coaming_top_z = _CURB_BASE_THK + curb_wall_h  # top of curb walls
        throat_lip_top = coaming_top_z  # leaf seats on the curb wall tops
        hinge_y = _CURB_HALF - _CURB_WALL  # inner wall face = rear rim (0.36)
    else:
        curb_wall_h = _CURB_WALL_H  # unused
        coaming_top_z = _COLLAR_THK
        throat_lip_top = _COLLAR_THK + 0.015  # top of throat ring lip
        hinge_y = lid_r  # round/cast hinge at the rear rim

    # Per-fill the rear hinge line / leaf thickness used to seat the leaf.
    # For the curb support, the hinge lugs sit on the FIXED curb rear inner wall
    # (CURB_INNER), so the hinge_y MUST stay there for every fill or the pin
    # floats off the lugs. For the flush collar, the hinge sits at the leaf rear
    # rim (fill-dependent leaf half-extent).
    curb = support_coaming == "raised_rect_kerb_curb"
    if leaf_fill == "checker_plate_steel":
        # Square plate: hinge line at the rear edge; plate top dropped below pin.
        hinge_drop = 0.012
        if curb:
            hinge_z = coaming_top_z - 0.002 + hinge_drop + _HATCH_PLATE_THK
        else:
            hinge_y = lid_r
            hinge_z = throat_lip_top - 0.002 + hinge_drop + _HATCH_PLATE_THK
    elif leaf_fill == "planked_deck":
        if curb:
            hinge_z = coaming_top_z + _PLANK_THK - 0.002
        else:
            hinge_y = lid_r
            hinge_z = throat_lip_top + _PLANK_THK - 0.002
    elif leaf_fill == "barred_grate":
        if curb:
            hinge_z = coaming_top_z + _FRAME_BAR_H - 0.002
        else:
            hinge_y = 0.36 * leaf_scale  # rear hinge line, was LID_R in parent
            hinge_z = throat_lip_top + _FRAME_BAR_H - 0.002
    else:  # solid_cast_slab (round)
        hinge_y = hinge_y  # already lid_r / curb inner
        hinge_z = throat_lip_top + _LID_THK - 0.002
        if curb:
            hinge_z = coaming_top_z + _LID_THK - 0.002

    hinge_lug_top = hinge_z + _HINGE_PIN_R + 0.014

    return ResolvedTrapDoorConfig(
        leaf_fill=leaf_fill,
        hinge_mechanism=hinge_mechanism,
        footprint=footprint,
        grip=grip,
        support_coaming=support_coaming,
        shaft_profile=shaft_profile,
        plank_count=plank_count,
        grate_slat_count=grate_slat_count,
        palette_style=palette_style,
        shaft_outer_r=shaft_outer_r,
        shaft_inner_r=shaft_inner_r,
        shaft_height=shaft_height,
        throat_r=throat_r,
        coaming_top_z=coaming_top_z,
        throat_lip_top=throat_lip_top,
        lid_r=lid_r,
        grate_w=grate_w,
        grate_d=grate_d,
        hinge_y=hinge_y,
        hinge_z=hinge_z,
        hinge_lug_top=hinge_lug_top,
        hinge_open_upper=hinge_open_upper,
        curb_wall_h=curb_wall_h,
        name=cfg.name or "trap_door",
    )


def with_overrides(config: TrapDoorConfig, **kwargs: object) -> TrapDoorConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: TrapDoorConfig | ResolvedTrapDoorConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTrapDoorConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("leaf_fill", r.leaf_fill),
        ("hinge_mechanism", r.hinge_mechanism),
        ("footprint", r.footprint),
        ("grip", r.grip),
        ("support_coaming", r.support_coaming),
        ("shaft_profile", r.shaft_profile),
    ]
    if r.leaf_fill == "planked_deck":
        choices.append(("plank_count", f"n{r.plank_count}"))
    elif r.leaf_fill == "barred_grate":
        choices.append(("grate_slat_count", f"n{r.grate_slat_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Shared support geometry (collar / curb / shaft / hinge mount). Verbatim from
# the pool (rec_door_trapdoor + rec_trapdoor_var_raisedcurb), parameterized.
# ===========================================================================
def _disc(radius: float, height: float, segments: int = 64) -> MeshGeometry:
    return CylinderGeometry(radius, height, radial_segments=segments)


def _build_shaft_mesh(r: ResolvedTrapDoorConfig) -> MeshGeometry:
    h = r.shaft_height
    if r.shaft_profile == "hollow_square":
        # Four vertical walls only: no top plate and no bottom plate. The inner
        # square circumscribes the circular throat so the round mouth remains
        # fully open into the square vault below.
        geom = MeshGeometry()
        outer_half = r.shaft_outer_r
        inner_half = r.throat_r
        wall = outer_half - inner_half
        wall_center = (outer_half + inner_half) / 2.0
        for sy in (-1.0, 1.0):
            geom = geom.merge(
                BoxGeometry((2.0 * outer_half, wall, h)).translate(
                    0.0, sy * wall_center, h / 2.0
                )
            )
        for sx in (-1.0, 1.0):
            geom = geom.merge(
                BoxGeometry((wall, 2.0 * inner_half, h)).translate(
                    sx * wall_center, 0.0, h / 2.0
                )
            )
        return geom

    return LatheGeometry.from_shell_profiles(
        [
            (r.shaft_outer_r, 0.0),
            (r.shaft_outer_r, h * 0.85),
            (r.shaft_outer_r - 0.02, h),
        ],
        [
            (r.shaft_inner_r, 0.0),
            (r.shaft_inner_r, h * 0.85),
            (r.shaft_inner_r, h),
        ],
        segments=64,
        start_cap="flat",
        end_cap="flat",
    )


def _vertical_probe_is_clear(geometry: MeshGeometry, x: float, y: float) -> bool:
    """Return whether a vertical line through ``(x, y)`` misses every face.

    This catches accidental horizontal caps without relying on a rendered
    preview. Vertical wall triangles have a degenerate XY projection and are
    intentionally ignored.
    """
    eps = 1e-9
    for ia, ib, ic in geometry.faces:
        ax, ay, _ = geometry.vertices[ia]
        bx, by, _ = geometry.vertices[ib]
        cx, cy, _ = geometry.vertices[ic]
        denom = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(denom) <= eps:
            continue
        wa = ((by - cy) * (x - cx) + (cx - bx) * (y - cy)) / denom
        wb = ((cy - ay) * (x - cx) + (ax - cx) * (y - cy)) / denom
        wc = 1.0 - wa - wb
        if wa >= -eps and wb >= -eps and wc >= -eps:
            return False
    return True


def _fixed_well_path_is_open(r: ResolvedTrapDoorConfig) -> bool:
    """Check a center cross of vertical paths through shaft and coaming."""
    shaft_geometry = _build_shaft_mesh(r)
    coaming_geometry = _build_curb_mesh(r) if r.is_curb else _build_collar_mesh(r)
    probe_r = 0.45 * min(r.shaft_inner_r, r.throat_r)
    probes = (
        (0.0, 0.0),
        (probe_r, 0.0),
        (-probe_r, 0.0),
        (0.0, probe_r),
        (0.0, -probe_r),
    )
    return all(
        _vertical_probe_is_clear(shaft_geometry, x, y)
        and _vertical_probe_is_clear(coaming_geometry, x, y)
        for x, y in probes
    )


def _has_circular_throat_ring(geometry: MeshGeometry, radius: float) -> bool:
    """Recognize a densely sampled circular vertex band near ``radius``."""
    matching_angles = {
        round(math.atan2(y, x), 3)
        for x, y, _ in geometry.vertices
        if abs(math.hypot(x, y) - radius) <= 0.006
    }
    return len(matching_angles) >= 24


def _build_collar_mesh(r: ResolvedTrapDoorConfig) -> MeshGeometry:
    """Square diamond-mesh collar frame + circular throat ring. Base at z=0,
    top at z=COLLAR_THK. Verbatim from rec_door_trapdoor._build_collar_mesh."""
    geom = MeshGeometry()
    inner = _COLLAR_HALF - _COLLAR_FRAME
    for sx in (1.0, -1.0):
        bar = BoxGeometry((_COLLAR_FRAME, 2.0 * _COLLAR_HALF, _COLLAR_THK))
        bar = bar.translate(sx * (_COLLAR_HALF - _COLLAR_FRAME / 2.0), 0.0, _COLLAR_THK / 2.0)
        geom = geom.merge(bar)
    for sy in (1.0, -1.0):
        bar = BoxGeometry((2.0 * inner, _COLLAR_FRAME, _COLLAR_THK))
        bar = bar.translate(0.0, sy * (_COLLAR_HALF - _COLLAR_FRAME / 2.0), _COLLAR_THK / 2.0)
        geom = geom.merge(bar)

    mesh_z = _COLLAR_THK - 0.012
    bar_h = 0.012
    bar_w = 0.009
    n = 11
    pitch = (2.0 * inner) / n
    clear_r = r.throat_r + 0.035
    for fam in (1.0, -1.0):
        ang = fam * math.pi / 4.0
        dx, dy = math.cos(ang), math.sin(ang)
        px, py = -dy, dx
        for k in range(1, n):
            off = -inner + k * pitch
            ts = []
            base_x, base_y = px * off, py * off
            for bound, dcomp, bcomp in (
                (inner, dx, base_x),
                (-inner, dx, base_x),
                (inner, dy, base_y),
                (-inner, dy, base_y),
            ):
                if abs(dcomp) > 1e-9:
                    t = (bound - bcomp) / dcomp
                    x = base_x + dx * t
                    y = base_y + dy * t
                    if -inner - 1e-6 <= x <= inner + 1e-6 and -inner - 1e-6 <= y <= inner + 1e-6:
                        ts.append(t)
            if len(ts) < 2:
                continue
            t0, t1 = min(ts), max(ts)
            if off * off < clear_r * clear_r:
                tc = math.sqrt(clear_r * clear_r - off * off)
                segments = [(t0, -tc), (tc, t1)]
            else:
                segments = [(t0, t1)]
            for s0, s1 in segments:
                length = s1 - s0
                if length < pitch * 0.4:
                    continue
                cx = base_x + dx * (s0 + s1) / 2.0
                cy = base_y + dy * (s0 + s1) / 2.0
                bar = BoxGeometry((length, bar_w, bar_h))
                bar = bar.rotate_z(ang)
                bar = bar.translate(cx, cy, mesh_z + bar_h / 2.0 - 0.001)
                geom = geom.merge(bar)

    throat = LatheGeometry.from_shell_profiles(
        [
            (r.throat_r + 0.03, 0.0),
            (r.throat_r + 0.03, _COLLAR_THK),
            (r.throat_r, _COLLAR_THK + 0.015),
        ],
        [
            (r.throat_r, 0.0),
            (r.throat_r, _COLLAR_THK),
            (r.throat_r - 0.004, _COLLAR_THK + 0.015),
        ],
        segments=64,
        start_cap="flat",
        end_cap="flat",
    )
    geom = geom.merge(throat)
    return geom


def _curb_wall_section(is_x_wall: bool, sign: float, wall_h: float) -> MeshGeometry:
    inner = _CURB_HALF - _CURB_WALL
    if not is_x_wall:
        wall = BoxGeometry((2.0 * _CURB_HALF, _CURB_WALL, wall_h))
        wall = wall.translate(0.0, sign * (_CURB_HALF - _CURB_WALL / 2.0),
                              _CURB_BASE_THK + wall_h / 2.0)
    else:
        wall = BoxGeometry((_CURB_WALL, 2.0 * inner, wall_h))
        wall = wall.translate(sign * (_CURB_HALF - _CURB_WALL / 2.0), 0.0,
                              _CURB_BASE_THK + wall_h / 2.0)
    return wall


def _build_curb_mesh(r: ResolvedTrapDoorConfig) -> MeshGeometry:
    """Raised rectangular kerb coaming: open base frame + four walls.

    The source's full square base slab sealed the well beneath the circular
    throat. Here the base is four bearing rails around a real central void, and
    no circular throat ring is added because this support has no surrounding
    fine mesh bars. Base at z=0, top at coaming_top_z.
    """
    geom = MeshGeometry()
    wall_h = r.curb_wall_h

    # Square frame whose opening clears the former round-throat footprint while
    # remaining visually square and completely open.
    base_inner_half = r.throat_r
    base_rail = _CURB_HALF - base_inner_half
    base_center = (_CURB_HALF + base_inner_half) / 2.0
    for sy in (-1.0, 1.0):
        geom = geom.merge(
            BoxGeometry((2.0 * _CURB_HALF, base_rail, _CURB_BASE_THK)).translate(
                0.0, sy * base_center, _CURB_BASE_THK / 2.0
            )
        )
    for sx in (-1.0, 1.0):
        geom = geom.merge(
            BoxGeometry((base_rail, 2.0 * base_inner_half, _CURB_BASE_THK)).translate(
                sx * base_center, 0.0, _CURB_BASE_THK / 2.0
            )
        )

    wall_specs = [(False, 1.0), (False, -1.0), (True, 1.0), (True, -1.0)]
    for is_x, sign in wall_specs:
        geom = geom.merge(_curb_wall_section(is_x, sign, wall_h))
    return geom


def _build_hinge_mount_mesh(r: ResolvedTrapDoorConfig, *, hinge_y: float, axis_set=None) -> MeshGeometry:
    """Collar/curb-side hinge mount: 2 upright lug plates + a pin along world X
    at (0, hinge_y, hinge_z). For bifold pass axis_set=[(+LID_R), (-LID_R)] to
    double the mount. Authored in the coaming part frame (base z=0)."""
    geom = MeshGeometry()
    ys = axis_set if axis_set is not None else [hinge_y]
    for hy in ys:
        if r.is_curb:
            lug_y0 = (_CURB_HALF - _CURB_WALL) if hy >= 0 else -_CURB_HALF
            lug_y1 = _CURB_HALF if hy >= 0 else -(_CURB_HALF - _CURB_WALL)
            lug_z0 = r.coaming_top_z
            for sx in (1.0, -1.0):
                lug = BoxGeometry((_HINGE_LUG_THK, abs(lug_y1 - lug_y0), r.hinge_lug_top - lug_z0))
                lug = lug.translate(sx * _HINGE_LUG_X, (lug_y0 + lug_y1) / 2.0,
                                    (lug_z0 + r.hinge_lug_top) / 2.0)
                geom = geom.merge(lug)
        else:
            if hy >= 0:
                lug_y0, lug_y1 = 0.345, _COLLAR_HALF
            else:
                lug_y0, lug_y1 = -0.345, -_COLLAR_HALF
            for sx in (1.0, -1.0):
                lug = BoxGeometry((_HINGE_LUG_THK, abs(lug_y1 - lug_y0), r.hinge_lug_top))
                lug = lug.translate(sx * _HINGE_LUG_X, (lug_y0 + lug_y1) / 2.0,
                                    r.hinge_lug_top / 2.0)
                geom = geom.merge(lug)
        pin_len = 2.0 * (_HINGE_LUG_X + _HINGE_LUG_THK / 2.0) + 0.012
        pin = CylinderGeometry(0.013, pin_len, radial_segments=16)
        pin = pin.rotate_y(math.pi / 2.0)
        pin = pin.translate(0.0, hy, r.hinge_z)
        geom = geom.merge(pin)
    return geom


# ===========================================================================
# Slot A: leaf fill meshes.
# ===========================================================================
def _build_solid_lid_body_mesh(r: ResolvedTrapDoorConfig) -> MeshGeometry:
    """Round cast-iron disc: stepped LatheGeometry top + centering seat + rim
    bolt ring. From rec_door_trapdoor._build_lid_body_mesh. Centered on the disc
    axis, rim top at z=0."""
    geom = MeshGeometry()
    profile = [
        (0.0, -_LID_THK),
        (r.lid_r, -_LID_THK),
        (r.lid_r, 0.0),
        (_RECESS_OUTER_R, 0.0),
        (_RECESS_OUTER_R, -_RECESS_DEPTH),
        (0.0, -_RECESS_DEPTH),
    ]
    geom = geom.merge(LatheGeometry(profile, segments=72, closed=True))
    seat = _disc(r.throat_r - 0.02, _LID_RIM_SEAT, segments=64)
    seat = seat.translate(0.0, 0.0, -_LID_THK - _LID_RIM_SEAT / 2.0)
    geom = geom.merge(seat)
    bolt_h = 0.012
    for i in range(_N_BOLTS):
        ang = (2.0 * math.pi / _N_BOLTS) * i
        bolt = CylinderGeometry(_BOLT_R, bolt_h, radial_segments=12)
        bolt = bolt.translate(_BOLT_RING_R, 0.0, bolt_h / 2.0)
        bolt = bolt.rotate_z(ang)
        geom = geom.merge(bolt)
    return geom


def _build_cross_wheel_relief_mesh() -> MeshGeometry:
    """Bold cross-wheel relief: hub + 4 spokes + framing torus. From
    rec_door_trapdoor._build_lid_relief_mesh."""
    geom = MeshGeometry()
    relief_h = _RELIEF_TOP_Z - (-_RECESS_DEPTH)
    base_z = -_RECESS_DEPTH
    hub = CylinderGeometry(_HUB_R, relief_h, radial_segments=48)
    hub = hub.translate(0.0, 0.0, base_z + relief_h / 2.0)
    geom = geom.merge(hub)
    spoke_inner = _HUB_R - 0.010
    spoke_outer = _RELIEF_RING_R + 0.004
    spoke_len = spoke_outer - spoke_inner
    for i in range(_N_SPOKES):
        ang = (math.pi / 2.0) * i + math.pi / 4.0
        bar = BoxGeometry((spoke_len, 2.0 * _SPOKE_HALF_W, relief_h))
        bar = bar.translate(spoke_inner + spoke_len / 2.0, 0.0, base_z + relief_h / 2.0)
        bar = bar.rotate_z(ang)
        geom = geom.merge(bar)
    ring_tube = 0.020
    ring = TorusGeometry(_RELIEF_RING_R, ring_tube, radial_segments=18, tubular_segments=72)
    ring = ring.translate(0.0, 0.0, _RELIEF_TOP_Z - ring_tube + 0.006)
    geom = geom.merge(ring)
    return geom


def _build_checker_plate_mesh(r: ResolvedTrapDoorConfig) -> MeshGeometry:
    """Square steel checker-plate: flat box + folded lips (3 sides) + centering
    boss + diamond tread grid. From rec_trapdoor_var_checkerplate. Centered,
    plate top at z=0."""
    side = 2.0 * r.lid_r
    half = r.lid_r
    geom = MeshGeometry()
    plate = BoxGeometry((side, side, _HATCH_PLATE_THK))
    plate = plate.translate(0.0, 0.0, -_HATCH_PLATE_THK / 2.0)
    geom = geom.merge(plate)
    lip_z_top = -_HATCH_PLATE_THK + 0.001
    lip_z_center = lip_z_top - _HATCH_LIP_HEIGHT / 2.0
    lip_specs = [
        (-1.0, 0.0, side, True),
        (1.0, 0.0, side, True),
        (0.0, -1.0, side - 2.0 * _HATCH_PLATE_THK, False),
    ]
    for sx, sy, length, is_x_edge in lip_specs:
        if is_x_edge:
            lip = BoxGeometry((_HATCH_PLATE_THK, length, _HATCH_LIP_HEIGHT))
            lip = lip.translate(sx * (half - _HATCH_PLATE_THK / 2.0), 0.0, lip_z_center)
        else:
            lip = BoxGeometry((length, _HATCH_PLATE_THK, _HATCH_LIP_HEIGHT))
            lip = lip.translate(0.0, sy * (half - _HATCH_PLATE_THK / 2.0), lip_z_center)
        geom = geom.merge(lip)
    seat = CylinderGeometry(r.throat_r - 0.02, _HATCH_RIM_SEAT, radial_segments=64)
    seat = seat.translate(0.0, 0.0, -_HATCH_PLATE_THK - _HATCH_RIM_SEAT / 2.0 + 0.001)
    geom = geom.merge(seat)
    x_min = -(half - _TREAD_INSET)
    x_max = half - _TREAD_INSET
    y_min = -(half - _TREAD_INSET)
    y_max = half - _TREAD_INSET
    nx = max(1, int((x_max - x_min) / _TREAD_SPACING))
    ny = max(1, int((y_max - y_min) / _TREAD_SPACING))
    for iy in range(ny):
        for ix in range(nx):
            x = x_min + (ix + 0.5) * _TREAD_SPACING
            y = y_min + (iy + 0.5) * _TREAD_SPACING
            ang = math.pi / 4.0 if (ix + iy) % 2 == 0 else -math.pi / 4.0
            bar = BoxGeometry((_TREAD_LEN, _TREAD_W, _TREAD_H))
            bar = bar.rotate_z(ang)
            bar = bar.translate(x, y, _TREAD_H / 2.0 - 0.001)
            geom = geom.merge(bar)
    return geom


def _board(size_x: float, size_y: float, size_z: float) -> MeshGeometry:
    return BoxGeometry((size_x, size_y, size_z))


def _build_grate_frame_mesh(r: ResolvedTrapDoorConfig) -> MeshGeometry:
    """Rectangular border frame (4 bars). From rec_trapdoor_var_grate. Rear edge
    at y=0 (hinge line), front edge at y=-grate_d, top at z=0."""
    geom = MeshGeometry()
    inner_w = r.grate_w - 2.0 * _FRAME_BAR_W
    for sx in (1.0, -1.0):
        bar = BoxGeometry((_FRAME_BAR_W, r.grate_d, _FRAME_BAR_H))
        bar = bar.translate(sx * (r.grate_w / 2.0 - _FRAME_BAR_W / 2.0),
                            -r.grate_d / 2.0, -_FRAME_BAR_H / 2.0)
        geom = geom.merge(bar)
    for y_centre in (-_FRAME_BAR_W / 2.0, -(r.grate_d - _FRAME_BAR_W / 2.0)):
        bar = BoxGeometry((inner_w, _FRAME_BAR_W, _FRAME_BAR_H))
        bar = bar.translate(0.0, y_centre, -_FRAME_BAR_H / 2.0)
        geom = geom.merge(bar)
    return geom


def _build_slat_bar_geometry(r: ResolvedTrapDoorConfig) -> MeshGeometry:
    inner_w = r.grate_w - 2.0 * _FRAME_BAR_W
    slat_length = inner_w + 0.004
    return BoxGeometry((slat_length, _SLAT_W, _SLAT_H))


def _build_knuckle_mesh() -> MeshGeometry:
    return CylinderGeometry(_HINGE_PIN_R, _HINGE_KNUCKLE_LEN, radial_segments=20)


# ===========================================================================
# Bifold half-disc body (CadQuery). From rec_trapdoor_var_biparting.
# ===========================================================================
def _half_cutter(y_sign: float, z_center: float, z_half: float, size: float = 1.0) -> cq.Workplane:
    s = size
    eps = 0.0005
    box = cq.Workplane("XY").box(s * 2, s + eps, z_half * 2 + 0.01)
    if y_sign < 0:
        return box.translate((0, -(s + eps) / 2, z_center))
    return box.translate((0, (s + eps) / 2, z_center))


def _build_leaf_body_cq(r: ResolvedTrapDoorConfig, y_sign: float) -> cq.Workplane:
    R = r.lid_r
    disc = cq.Workplane("XY").circle(R).extrude(_LID_THK).translate((0, 0, -_LID_THK))
    half = disc.cut(_half_cutter(y_sign, -_LID_THK / 2, _LID_THK, R * 2))
    recess = (
        cq.Workplane("XY")
        .circle(_RECESS_OUTER_R)
        .extrude(_RECESS_DEPTH + 0.002)
        .translate((0, 0, -_RECESS_DEPTH))
    )
    recess_half = recess.cut(
        _half_cutter(y_sign, -_RECESS_DEPTH / 2, _RECESS_DEPTH + 0.002, _RECESS_OUTER_R * 2)
    )
    return half.cut(recess_half)


def _semicircle_profile(rad: float, y_sign: float, n: int = 48) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    if y_sign < 0:
        for i in range(n + 1):
            a = math.pi * i / n
            pts.append((rad * math.cos(a), rad * math.sin(a)))
    else:
        for i in range(n + 1):
            a = math.pi * i / n
            pts.append((-rad * math.cos(a), -rad * math.sin(a)))
    return pts


def _build_half_torus_mesh(R: float, r_tube: float, y_sign: float,
                           radial_seg: int = 16, tubular_seg: int = 36) -> MeshGeometry:
    geom = MeshGeometry()
    if y_sign < 0:
        u_start, u_end = 0.0, math.pi
    else:
        u_start, u_end = math.pi, 2 * math.pi
    cols = radial_seg + 1
    for i in range(tubular_seg + 1):
        u = u_start + (u_end - u_start) * i / tubular_seg
        cu, su = math.cos(u), math.sin(u)
        for j in range(cols):
            v = 2 * math.pi * j / radial_seg
            cv, sv = math.cos(v), math.sin(v)
            geom.add_vertex((R + r_tube * cv) * cu, (R + r_tube * cv) * su, r_tube * sv)
    for i in range(tubular_seg):
        for j in range(radial_seg):
            a = i * cols + j
            b = a + 1
            c = a + cols
            d = c + 1
            geom.add_face(a, c, b)
            geom.add_face(b, c, d)
    return geom


def _build_leaf_bolts_mesh(y_sign: float) -> MeshGeometry:
    geom = MeshGeometry()
    bolt_h = 0.012
    for i in range(_N_BOLTS):
        ang = (2.0 * math.pi / _N_BOLTS) * i
        by = _BOLT_RING_R * math.sin(ang)
        if y_sign < 0 and by < 0.010:
            continue
        if y_sign > 0 and by > -0.010:
            continue
        bx = _BOLT_RING_R * math.cos(ang)
        bolt = CylinderGeometry(_BOLT_R, bolt_h, radial_segments=12)
        bolt = bolt.translate(bx, by, bolt_h / 2.0)
        geom = geom.merge(bolt)
    return geom


def _build_leaf_centering_mesh(r: ResolvedTrapDoorConfig, y_sign: float) -> MeshGeometry:
    seat_r = r.throat_r - 0.02
    profile = _semicircle_profile(seat_r, y_sign)
    seat = ExtrudeGeometry.from_z0(profile, _LID_RIM_SEAT, cap=True)
    return seat.translate(0, 0, -_LID_THK - _LID_RIM_SEAT)


def _build_leaf_relief_mesh(y_sign: float) -> MeshGeometry:
    geom = MeshGeometry()
    relief_h = _RELIEF_TOP_Z + _RECESS_DEPTH
    base_z = -_RECESS_DEPTH
    hub_profile = _semicircle_profile(_HUB_R, y_sign)
    hub = ExtrudeGeometry.from_z0(hub_profile, relief_h, cap=True)
    hub = hub.translate(0, 0, base_z)
    geom = geom.merge(hub)
    spoke_inner_r = _HUB_R - 0.010
    spoke_outer_r = _RELIEF_RING_R + 0.004
    spoke_len = spoke_outer_r - spoke_inner_r
    mid_r = spoke_inner_r + spoke_len / 2
    for i in range(_N_SPOKES):
        ang = (math.pi / 2.0) * i + math.pi / 4.0
        dy = math.sin(ang)
        if y_sign < 0 and dy < -0.01:
            continue
        if y_sign > 0 and dy > 0.01:
            continue
        bar = BoxGeometry((spoke_len, 2 * _SPOKE_HALF_W, relief_h))
        bar = bar.translate(mid_r, 0, base_z + relief_h / 2)
        bar = bar.rotate_z(ang)
        geom = geom.merge(bar)
    ring_tube = 0.020
    ring_z = _RELIEF_TOP_Z - ring_tube + 0.006
    ring = _build_half_torus_mesh(_RELIEF_RING_R, ring_tube, y_sign)
    ring = ring.translate(0, 0, ring_z)
    geom = geom.merge(ring)
    return geom


# ===========================================================================
# Slot D grip meshes (inline visuals on the leaf; no joint except fold_handle).
# ===========================================================================
def _build_ring_pull_mesh() -> MeshGeometry:
    """Recessed ring-pull torus seated flush in a shallow pocket. From
    rec_trapdoor_var_ringpull."""
    ring_z = -_RECESS_DEPTH - _POCKET_DEPTH + _RING_PULL_TUBE_R
    ring = TorusGeometry(_RING_PULL_R, _RING_PULL_TUBE_R, radial_segments=16, tubular_segments=64)
    ring = ring.translate(0.0, 0.0, ring_z)
    return ring


def _build_ring_pocket_mesh() -> MeshGeometry:
    """Shallow round pocket the ring sits in (so the ring is supported, not a
    floating island). A short cylinder sunk into the recess floor."""
    pocket = CylinderGeometry(_POCKET_R, _POCKET_DEPTH, radial_segments=48)
    pocket = pocket.translate(0.0, 0.0, -_RECESS_DEPTH - _POCKET_DEPTH / 2.0)
    return pocket


def _build_rope_loop_mesh() -> MeshGeometry:
    """Hemp-rope arch (tube spline). From rec_trapdoor_var_ropeloop."""
    half_span = _ROPE_EYELET_SPACING / 2.0
    base_z = -_RECESS_DEPTH
    n_arc = 9
    points = []
    for i in range(n_arc):
        t = i / (n_arc - 1)
        angle = math.pi * t
        x = half_span * math.cos(angle)
        z = base_z + _ROPE_LOOP_HEIGHT * math.sin(angle)
        points.append((x, 0.0, z))
    return tube_from_spline_points(
        points, radius=_ROPE_RADIUS, samples_per_segment=16, radial_segments=14,
        cap_ends=True, up_hint=(0.0, 1.0, 0.0),
    )


def _build_eyelet_mesh() -> MeshGeometry:
    return TorusGeometry(_EYELET_R, _EYELET_TUBE_R, radial_segments=10, tubular_segments=24)


def _build_pocket_mesh() -> MeshGeometry:
    """Rectangular pocket recess for the folding bar handle. From
    rec_trapdoor_var_foldhandle._build_pocket_mesh."""
    pocket = BoxGeometry((_POCKET_WID, _POCKET_LEN, _HANDLE_POCKET_DEPTH))
    pocket = pocket.translate(0.0, 0.0, -_RECESS_DEPTH - _HANDLE_POCKET_DEPTH / 2.0)
    return pocket


def _handle_lug_h() -> float:
    return _HANDLE_POCKET_DEPTH + _HANDLE_HINGE_R + 0.004


def _handle_lug_geometry() -> MeshGeometry:
    return BoxGeometry((_HANDLE_LUG_WID, _HANDLE_LUG_DEPTH, _handle_lug_h()))


def _handle_lug_position_in_body(lug_index: int) -> tuple[float, float, float]:
    sx = 1.0 if lug_index == 0 else -1.0
    lug_x = sx * (_HANDLE_HINGE_LEN / 2.0 + _HANDLE_LUG_WID / 2.0)
    lug_y = _POCKET_LEN / 2.0 - _HANDLE_LUG_DEPTH / 2.0 - 0.003
    lug_z = -_RECESS_DEPTH - _HANDLE_POCKET_DEPTH + _handle_lug_h() / 2.0
    return (lug_x, lug_y, lug_z)


def _build_handle_bar_mesh() -> MeshGeometry:
    """Flat handle bar + coaxial barrel. From rec_trapdoor_var_foldhandle.
    Origin at the hinge pin axis; bar extends -Y, top at z=0."""
    geom = MeshGeometry()
    bar = BoxGeometry((_HANDLE_WID, _HANDLE_LEN, _HANDLE_THK))
    bar = bar.translate(0.0, -_HANDLE_LEN / 2.0, -_HANDLE_THK / 2.0)
    geom = geom.merge(bar)
    barrel = CylinderGeometry(_HANDLE_HINGE_R, _HANDLE_HINGE_LEN, radial_segments=16)
    barrel = barrel.rotate_y(math.pi / 2.0)
    geom = geom.merge(barrel)
    return geom


# ===========================================================================
# Grip emit (inline visuals + optional nested joint). y0 = leaf-body center Y
# offset in the leaf part frame (so decorations align with the disc center).
# ===========================================================================
def _emit_grip(model, r, leaf, mats, *, y0: float, hinge_open: bool) -> list[str]:
    """Emit the Slot D grip onto the leaf part. Returns extra child part names.
    y0 is the disc-center Y in the leaf part frame (e.g. -lid_r for the round
    disc whose mesh is offset forward)."""
    grip = r.grip
    if grip == "cross_wheel_relief":
        # Rim relief lives ON the leaf body recess (solid faces) or on the rear
        # frame bar (grate). For solid faces, place the cross-wheel in the recess.
        if r.leaf_fill in SOLID_FACE_FILLS or r.leaf_fill == "planked_deck":
            leaf.visual(
                mesh_from_geometry(_build_cross_wheel_relief_mesh(), "lid_relief"),
                origin=Origin(xyz=(0.0, y0, 0.0)),
                material=mats["relief"],
                name="lid_relief", material_class_id=("metal.cast_iron_bare" if r.leaf_fill in {"solid_cast_slab", "checker_plate_steel", "barred_grate"} else "wood.rustic_weathered"),
            )
        # grate: no cross-wheel (see-through); identity is the slats themselves.
        return []
    if grip == "recessed_ring_pull":
        leaf.visual(
            mesh_from_geometry(_build_ring_pocket_mesh(), "ring_pocket"),
            origin=Origin(xyz=(0.0, y0, 0.0)),
            material=mats["relief"],
            name="ring_pocket", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
        )
        leaf.visual(
            mesh_from_geometry(_build_ring_pull_mesh(), "ring_pull"),
            origin=Origin(xyz=(0.0, y0, 0.0)),
            material=mats["hardware"],
            name="ring_pull", material_class_id="metal.steel_bare",
        )
        return []
    if grip == "rope_loop_pull":
        leaf.visual(
            mesh_from_geometry(_build_rope_loop_mesh(), "rope_loop"),
            origin=Origin(xyz=(0.0, y0, 0.0)),
            material=mats["rope"],
            name="rope_loop", material_class_id="organic.woven_plant_fiber",
        )
        for i in range(_N_EYELETS):
            sx = 1.0 if i == 0 else -1.0
            ex = sx * _ROPE_EYELET_SPACING / 2.0
            leaf.visual(
                mesh_from_geometry(_build_eyelet_mesh(), f"eyelet_{i}"),
                origin=Origin(xyz=(ex, y0, -_RECESS_DEPTH)),
                material=mats["hardware"],
                name=f"eyelet_{i}", material_class_id="metal.steel_bare",
            )
        return []
    # folding_bar_handle: pocket + lugs + pin (inline visuals) + nested joint.
    leaf.visual(
        mesh_from_geometry(_build_pocket_mesh(), "lid_pocket"),
        origin=Origin(xyz=(0.0, y0, 0.0)),
        material=mats["relief"],
        name="lid_pocket", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
    )
    for i in range(_N_HANDLE_LUGS):
        lx, ly, lz = _handle_lug_position_in_body(i)
        lug = _handle_lug_geometry().translate(lx, ly, lz)
        leaf.visual(
            mesh_from_geometry(lug, f"handle_lug_{i}"),
            origin=Origin(xyz=(0.0, y0, 0.0)),
            material=mats["hardware"],
            name=f"handle_lug_{i}", material_class_id="metal.steel_bare",
        )
    handle_pin_len = _HANDLE_HINGE_LEN + 2.0 * _HANDLE_LUG_WID + 0.008
    pin = CylinderGeometry(_HANDLE_PIN_R, handle_pin_len, radial_segments=12)
    pin = pin.rotate_y(math.pi / 2.0)
    pin_y_body = _POCKET_LEN / 2.0 - _HANDLE_LUG_DEPTH / 2.0 - 0.003
    pin_z_body = -_RECESS_DEPTH
    pin = pin.translate(0.0, pin_y_body, pin_z_body)
    leaf.visual(
        mesh_from_geometry(pin, "handle_hinge_pin"),
        origin=Origin(xyz=(0.0, y0, 0.0)),
        material=mats["hardware"],
        name="handle_hinge_pin", material_class_id="metal.steel_bare",
    )
    # The handle hinge axis in the leaf part frame.
    handle_hinge_y = y0 + pin_y_body
    handle_hinge_z = pin_z_body
    handle = model.part("lift_handle")
    handle.visual(
        mesh_from_geometry(_build_handle_bar_mesh(), "handle_bar"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="handle_bar", material_class_id="metal.steel_bare",
    )
    handle.inertial = Inertial.from_geometry(
        Box((_HANDLE_WID, _HANDLE_LEN, _HANDLE_THK)),
        mass=0.4,
        origin=Origin(xyz=(0.0, -_HANDLE_LEN / 2.0, -_HANDLE_THK / 2.0)),
    )
    model.articulation(
        "lid_to_handle",
        ArticulationType.REVOLUTE,
        parent=leaf,
        child=handle,
        origin=Origin(xyz=(0.0, handle_hinge_y, handle_hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=3.0, lower=0.0, upper=1.75),
    )
    return ["lift_handle"]


# ===========================================================================
# Support coaming builder (FIXED to shaft). Returns coaming part + name.
# ===========================================================================
def _build_support(model, r, shaft, mats, *, coaming_y: float = 0.0):
    """Build the FIXED support coaming. ``coaming_y`` shifts all coaming-authored
    geometry in Y so that, combined with the FIXED joint origin offset, the
    coaming stays world-centered while the joint origin lands on shaft material."""
    if r.is_curb:
        coaming = model.part("curb_frame")
        coaming.visual(
            mesh_from_geometry(_build_curb_mesh(r), "curb_body"),
            origin=Origin(xyz=(0.0, coaming_y, 0.0)),
            material=mats["coaming"],
            name="curb_body", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
        )
        coaming.inertial = Inertial.from_geometry(
            Box((2.0 * _CURB_HALF, 2.0 * _CURB_HALF, r.coaming_top_z)),
            mass=8.0,
            origin=Origin(xyz=(0.0, coaming_y, r.coaming_top_z / 2.0)),
        )
    else:
        coaming = model.part("mesh_collar")
        coaming.visual(
            mesh_from_geometry(_build_collar_mesh(r), "mesh_collar"),
            origin=Origin(xyz=(0.0, coaming_y, 0.0)),
            material=mats["coaming"],
            name="collar_frame", material_class_id="metal.mesh_chainmail",
        )
        coaming.inertial = Inertial.from_geometry(
            Box((2.0 * _COLLAR_HALF, 2.0 * _COLLAR_HALF, _COLLAR_THK)),
            mass=6.0,
            origin=Origin(xyz=(0.0, coaming_y, _COLLAR_THK / 2.0)),
        )
    return coaming


# ===========================================================================
# Top-level build.
# ===========================================================================
def build_trap_door(
    config: TrapDoorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"trap_door_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    # --- Well shaft (fixed root). ---
    shaft = model.part("well_shaft")
    shaft.visual(
        mesh_from_geometry(_build_shaft_mesh(r), "well_shaft"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["concrete"],
        name="shaft_wall", material_class_id="concrete.smooth_cast",
    )
    shaft.inertial = Inertial.from_geometry(
        (
            Box((2.0 * r.shaft_outer_r, 2.0 * r.shaft_outer_r, r.shaft_height))
            if r.shaft_profile == "hollow_square"
            else Cylinder(radius=r.shaft_outer_r, length=r.shaft_height)
        ),
        mass=20.0,
        origin=Origin(xyz=(0.0, 0.0, r.shaft_height / 2.0)),
    )

    # --- Support coaming (FIXED to shaft top). ---
    # The shaft top center is the open bore (hollow), so a FIXED origin at
    # (0,0,shaft_height) sits ~shaft_inner_r away from any shaft material and
    # trips the baseline articulation-origin check. Anchor the FIXED origin on
    # the rear shaft WALL ring instead, and author the coaming shifted by
    # -mount_y so it stays world-centered (fence_cascade datum-shift pattern).
    shaft_inner_mount = r.throat_r if r.shaft_profile == "hollow_square" else r.shaft_inner_r
    mount_y = 0.5 * (shaft_inner_mount + r.shaft_outer_r)
    coaming = _build_support(model, r, shaft, mats, coaming_y=-mount_y)
    model.articulation(
        "shaft_to_coaming",
        ArticulationType.FIXED,
        parent=shaft,
        child=coaming,
        origin=Origin(xyz=(0.0, mount_y, r.shaft_height)),
    )

    if r.hinge_mechanism == "double_bifold":
        _build_bifold_leaves(model, r, coaming, mats, coaming_y=-mount_y)
    else:
        _build_single_leaf(model, r, coaming, mats, coaming_y=-mount_y)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def _build_single_leaf(model, r, coaming, mats, *, coaming_y: float = 0.0) -> None:
    # Collar-side hinge mount (authored in coaming frame, shifted by coaming_y).
    coaming.visual(
        mesh_from_geometry(_build_hinge_mount_mesh(r, hinge_y=r.hinge_y), "hinge_mount"),
        origin=Origin(xyz=(0.0, coaming_y, 0.0)),
        material=mats["coaming"],
        name="hinge_mount", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
    )

    leaf = model.part("leaf")
    fill = r.leaf_fill

    if fill == "solid_cast_slab":
        y0 = -r.lid_r
        leaf.visual(
            mesh_from_geometry(_build_solid_lid_body_mesh(r), "lid_body"),
            origin=Origin(xyz=(0.0, y0, 0.0)),
            material=mats["leaf"],
            name="lid_disc", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
        )
        _emit_grip(model, r, leaf, mats, y0=y0, hinge_open=True)
        leaf_box = Box((2.0 * r.lid_r, 2.0 * r.lid_r, _LID_THK))
        leaf_box_origin = Origin(xyz=(0.0, y0, -_LID_THK / 2.0))
    elif fill == "checker_plate_steel":
        # Plate centered, offset forward by half and down by hinge_drop so the
        # knuckle embeds and the rear edge lands on the hinge line.
        half = r.lid_r
        hinge_drop = 0.012
        y0 = -half
        leaf.visual(
            mesh_from_geometry(_build_checker_plate_mesh(r), "hatch_plate"),
            origin=Origin(xyz=(0.0, y0, -hinge_drop)),
            material=mats["leaf"],
            name="hatch_plate", material_class_id="metal.patterned_sheet_panel",
        )
        _emit_grip(model, r, leaf, mats, y0=y0, hinge_open=True)
        leaf_box = Box((2.0 * half, 2.0 * half, _HATCH_PLATE_THK))
        leaf_box_origin = Origin(xyz=(0.0, y0, -hinge_drop - _HATCH_PLATE_THK / 2.0))
    elif fill == "planked_deck":
        size = 2.0 * r.lid_r
        n = r.plank_count
        plank_w = (size - (n - 1) * _PLANK_GAP) / n
        for i in range(n):
            y_center = -(plank_w / 2.0) - i * (plank_w + _PLANK_GAP)
            leaf.visual(
                mesh_from_geometry(_board(size, plank_w, _PLANK_THK), f"plank_{i}"),
                origin=Origin(xyz=(0.0, y_center, -_PLANK_THK / 2.0)),
                material=mats["leaf"],
                name=f"plank_{i}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "wood.painted_weathered"),
            )
        batten_len = size - 2.0 * _BATTEN_INSET
        batten_x_off = size * 0.28
        for j in range(_N_BATTENS):
            x_sign = -1.0 if j == 0 else 1.0
            leaf.visual(
                mesh_from_geometry(_board(_BATTEN_W, batten_len, _BATTEN_THK), f"batten_{j}"),
                origin=Origin(xyz=(x_sign * batten_x_off, -size / 2.0, _BATTEN_THK / 2.0)),
                material=mats["relief"],
                name=f"batten_{j}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "wood.painted_weathered"),
            )
        y0 = -size / 2.0
        _emit_grip(model, r, leaf, mats, y0=y0, hinge_open=True)
        leaf_box = Box((size, size, _PLANK_THK))
        leaf_box_origin = Origin(xyz=(0.0, y0, -_PLANK_THK / 2.0))
    else:  # barred_grate
        leaf.visual(
            mesh_from_geometry(_build_grate_frame_mesh(r), "grate_frame"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["leaf"],
            name="grate_frame", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
        )
        n = r.grate_slat_count
        inner_d = r.grate_d - 2.0 * _FRAME_BAR_W
        slat_pitch = inner_d / (n + 1)
        for i in range(n):
            y_pos = -(_FRAME_BAR_W + (i + 1) * slat_pitch)
            leaf.visual(
                mesh_from_geometry(_build_slat_bar_geometry(r), f"slat_{i}"),
                origin=Origin(xyz=(0.0, y_pos, -_SLAT_H / 2.0)),
                material=mats["accent"],
                name=f"slat_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
            )
        y0 = -r.grate_d / 2.0
        leaf_box = Box((r.grate_w, r.grate_d, _FRAME_BAR_H))
        leaf_box_origin = Origin(xyz=(0.0, y0, -_FRAME_BAR_H / 2.0))

    # Leaf-side coaxial knuckle barrel at the part origin (on the hinge axis).
    leaf.visual(
        mesh_from_geometry(_build_knuckle_mesh(), "leaf_knuckle"),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["hardware"],
        name="leaf_knuckle", material_class_id="metal.steel_bare",
    )
    leaf.inertial = Inertial.from_geometry(leaf_box, mass=3.0, origin=leaf_box_origin)

    model.articulation(
        "coaming_to_leaf",
        ArticulationType.REVOLUTE,
        parent=coaming,
        child=leaf,
        origin=Origin(xyz=(0.0, r.hinge_y + coaming_y, r.hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=60.0, velocity=2.0, lower=0.0, upper=r.hinge_open_upper
        ),
    )


def _build_bifold_leaves(model, r, coaming, mats, *, coaming_y: float = 0.0) -> None:
    # Doubled hinge mount (rear + front sets).
    coaming.visual(
        mesh_from_geometry(
            _build_hinge_mount_mesh(r, hinge_y=r.lid_r, axis_set=[r.lid_r, -r.lid_r]),
            "hinge_mount",
        ),
        origin=Origin(xyz=(0.0, coaming_y, 0.0)),
        material=mats["coaming"],
        name="hinge_mount", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
    )
    leaf_configs = [(0, -1), (1, 1)]
    for i, y_sign in leaf_configs:
        hinge_y = -y_sign * r.lid_r
        axis = (float(y_sign), 0.0, 0.0)
        disc_offset = (0.0, y_sign * r.lid_r, 0.0)
        leaf = model.part(f"leaf_{i}")
        leaf.visual(
            mesh_from_cadquery(_build_leaf_body_cq(r, y_sign), f"leaf_body_{i}"),
            origin=Origin(xyz=disc_offset),
            material=mats["leaf"],
            name="body", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
        )
        leaf.visual(
            mesh_from_geometry(_build_leaf_bolts_mesh(y_sign), f"leaf_bolts_{i}"),
            origin=Origin(xyz=disc_offset),
            material=mats["leaf"],
            name="bolts", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
        )
        leaf.visual(
            mesh_from_geometry(_build_leaf_centering_mesh(r, y_sign), f"leaf_seat_{i}"),
            origin=Origin(xyz=disc_offset),
            material=mats["leaf"],
            name="seat", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
        )
        leaf.visual(
            mesh_from_geometry(_build_leaf_relief_mesh(y_sign), f"leaf_relief_{i}"),
            origin=Origin(xyz=disc_offset),
            material=mats["relief"],
            name="relief", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"cast_iron", "checker_plate_steel", "weathered_planks", "gunmetal_grate"} else "metal.paint_coated"),
        )
        leaf.visual(
            mesh_from_geometry(_build_knuckle_mesh(), f"leaf_knuckle_{i}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["hardware"],
            name="knuckle", material_class_id="metal.steel_bare",
        )
        leaf.inertial = Inertial.from_geometry(
            Box((2.0 * r.lid_r, r.lid_r, _LID_THK)),
            mass=1.5,
            origin=Origin(xyz=(0.0, y_sign * r.lid_r / 2.0, -_LID_THK / 2.0)),
        )
        model.articulation(
            f"coaming_to_leaf_{i}",
            ArticulationType.REVOLUTE,
            parent=coaming,
            child=leaf,
            origin=Origin(xyz=(0.0, hinge_y + coaming_y, r.hinge_z)),
            axis=axis,
            motion_limits=MotionLimits(
                effort=60.0, velocity=2.0, lower=0.0, upper=r.hinge_open_upper
            ),
        )


def build_seeded_trap_door(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_trap_door(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests.
# ===========================================================================
def run_trap_door_tests(
    object_model: ArticulatedObject,
    config: TrapDoorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    shaft = object_model.get_part("well_shaft")
    coaming_name = "curb_frame" if r.is_curb else "mesh_collar"
    coaming = object_model.get_part(coaming_name)

    # --- Overlap allowances (captured-pin / seating; element/part scoped). ---
    if r.hinge_mechanism == "double_bifold":
        for i in (0, 1):
            leaf = object_model.get_part(f"leaf_{i}")
            ctx.allow_overlap(
                leaf, coaming,
                reason=f"leaf_{i} knuckle barrel embeds into the collar hinge "
                "mount and the centering step nests inside the throat ring; "
                "local intended seated/hinge overlaps.",
            )
        ctx.allow_overlap(
            object_model.get_part("leaf_0"),
            object_model.get_part("leaf_1"),
            reason="the two bi-fold half-leaves meet at the y=0 center seam when closed.",
        )
    else:
        leaf = object_model.get_part("leaf")
        seat_feature = "raised curb wall tops" if r.is_curb else "throat ring lip"
        ctx.allow_overlap(
            leaf, coaming,
            reason="leaf hinge knuckle embeds into the coaming hinge mount and the "
            f"closed leaf seats ~2mm into the {seat_feature}; local intended overlaps.",
        )
        if r.grip == "folding_bar_handle":
            handle = object_model.get_part("lift_handle")
            ctx.allow_overlap(
                handle, leaf, elem_a="handle_bar", elem_b="lid_pocket",
                reason="the folding handle bar lies flush in the lid pocket at q=0.",
            )
            ctx.allow_overlap(
                handle, leaf, elem_a="handle_bar", elem_b="lid_disc",
                reason="the handle bar/barrel nests into the pocket recessed into "
                "the cast lid disc body at q=0 (intended seating overlap).",
            )
            for i in range(_N_HANDLE_LUGS):
                ctx.allow_overlap(
                    handle, leaf, elem_a="handle_bar", elem_b=f"handle_lug_{i}",
                    reason=f"handle barrel is captured between lid-side handle lug {i}.",
                )
            ctx.allow_overlap(
                handle, leaf, elem_a="handle_bar", elem_b="handle_hinge_pin",
                reason="handle barrel rides on the lid-side handle hinge pin.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # --- Structure / identity. ---
    part_names = {p.name for p in object_model.parts}
    ctx.check("well_shaft root present", "well_shaft" in part_names, details=str(sorted(part_names)))
    ctx.check(f"support coaming '{coaming_name}' present", coaming_name in part_names)

    # Shaft on ground; coaming seats on shaft top (FIXED contact invariant).
    shaft_aabb = ctx.part_world_aabb(shaft)
    coaming_aabb = ctx.part_world_aabb(coaming)
    if shaft_aabb is not None:
        ctx.check("well shaft rests on the ground (z~0)", abs(shaft_aabb[0][2]) < 0.01,
                  details=f"shaft min z={shaft_aabb[0][2]:.4f}")
    if shaft_aabb is not None and coaming_aabb is not None:
        ctx.check("coaming sits at the shaft top (no float)",
                  abs(coaming_aabb[0][2] - shaft_aabb[1][2]) < 0.05,
                  details=f"coaming min z={coaming_aabb[0][2]:.3f}, shaft max z={shaft_aabb[1][2]:.3f}")

    ctx.check("collar throat clears the shaft bore (hollow well)",
              r.throat_r <= r.shaft_inner_r + 0.05 and r.shaft_inner_r > 0.25,
              details=f"throat_r={r.throat_r:.3f}, bore_r={r.shaft_inner_r:.3f}")
    ctx.check(
        "open hatch leaves an unobstructed path through coaming and hollow shaft",
        _fixed_well_path_is_open(r),
        details=f"shaft_profile={r.shaft_profile}, support={r.support_coaming}",
    )
    coaming_geometry = _build_curb_mesh(r) if r.is_curb else _build_collar_mesh(r)
    ctx.check(
        (
            "bar-free raised curb omits the circular throat ring"
            if r.is_curb
            else "mesh collar retains its circular throat ring"
        ),
        (
            not _has_circular_throat_ring(coaming_geometry, r.throat_r)
            if r.is_curb
            else _has_circular_throat_ring(coaming_geometry, r.throat_r)
        ),
        details=f"support={r.support_coaming}",
    )

    # --- Hinge mount reaches the pin (captured). ---
    ctx.check("collar-side hinge mount reaches the hinge axis (pin captured)",
              r.hinge_lug_top > r.hinge_z + _HINGE_PIN_R,
              details=f"lug_top={r.hinge_lug_top:.3f}, hinge_z={r.hinge_z:.3f}")

    # --- Hinge joints: horizontal axis (world ±X), flat-closed range. ---
    if r.hinge_mechanism == "double_bifold":
        j0 = object_model.get_articulation("coaming_to_leaf_0")
        j1 = object_model.get_articulation("coaming_to_leaf_1")
        ctx.check(
            "bifold has 2 opposite-sign horizontal REVOLUTE leaf hinges",
            j0.articulation_type == ArticulationType.REVOLUTE
            and j1.articulation_type == ArticulationType.REVOLUTE
            and abs(j0.axis[0]) > 0.9 and abs(j1.axis[0]) > 0.9
            and j0.axis[0] * j1.axis[0] < 0,
            details=f"axis0={tuple(j0.axis)} axis1={tuple(j1.axis)}",
        )
        leaves = [object_model.get_part("leaf_0"), object_model.get_part("leaf_1")]
        hinges = [j0, j1]
    else:
        j = object_model.get_articulation("coaming_to_leaf")
        ctx.check(
            "leaf hinge is horizontal REVOLUTE about world -X (flat closed)",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.9
            and j.motion_limits.lower == 0.0 and j.motion_limits.upper > 1.5,
            details=f"axis={tuple(j.axis)} range=({j.motion_limits.lower},{j.motion_limits.upper})",
        )
        leaves = [object_model.get_part("leaf")]
        hinges = [j]

    # --- Closed pose: leaf lies FLAT, seats on coaming, covers throat. ---
    pose_closed = {h: 0.0 for h in hinges}
    with ctx.pose(pose_closed):
        for li, leaf in enumerate(leaves):
            aabb = ctx.part_world_aabb(leaf)
            if aabb is not None:
                (x0, y0v, z0), (x1, y1v, z1) = aabb
                x_span, y_span, z_span = x1 - x0, y1v - y0v, z1 - z0
                # Bifold half-leaves are half-depth, so relax the Y span threshold.
                wide_thresh = 0.30 if r.hinge_mechanism == "double_bifold" else 0.5
                ctx.check(
                    f"leaf[{li}] closed lies flat (thin Z, wide X)",
                    z_span < 0.15 and x_span > wide_thresh,
                    details=f"x_span={x_span:.3f} y_span={y_span:.3f} z_span={z_span:.3f}",
                )
                ctx.check(
                    f"leaf[{li}] closed sits at the coaming top, not on the ground",
                    z0 > r.shaft_height - 0.03,
                    details=f"leaf min z={z0:.3f}, shaft height={r.shaft_height:.3f}",
                )
            ctx.expect_contact(
                leaf, coaming, contact_tol=0.010,
                name=f"leaf[{li}] closed seats on the coaming (not floating)",
            )
        # Together the leaves cover the throat in plan.
        min_ov = 0.10 if r.hinge_mechanism == "double_bifold" else 0.20
        for li, leaf in enumerate(leaves):
            ctx.expect_overlap(
                leaf, coaming, axes="xy", min_overlap=min_ov,
                name=f"leaf[{li}] covers the throat in plan when closed",
            )

    # --- Open pose: leaf lifts up well above closed, stands tall. ---
    for li, (leaf, h) in enumerate(zip(leaves, hinges)):
        with ctx.pose({h: 0.0}):
            closed = ctx.part_world_aabb(leaf)
        with ctx.pose({h: r.hinge_open_upper * 0.8}):
            opened = ctx.part_world_aabb(leaf)
        if closed is not None and opened is not None:
            ctx.check(
                f"leaf[{li}] open lifts well above closed",
                opened[1][2] > closed[1][2] + 0.15,
                details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
            )
            ctx.check(
                f"leaf[{li}] open stands tall in Z",
                (opened[1][2] - opened[0][2]) > 0.25,
                details=f"open_z_span={(opened[1][2] - opened[0][2]):.3f}",
            )

    # --- Multiplicity: plank / slat counts + naming + see-through gaps. ---
    if r.leaf_fill == "planked_deck":
        leaf = object_model.get_part("leaf")
        planks = [v.name for v in leaf.visuals if v.name.startswith("plank_")]
        ctx.check(
            "N planks inlined (Rule 1) with plank_i naming",
            len(planks) == r.plank_count,
            details=f"planks={sorted(planks)} expected n={r.plank_count}",
        )
        battens = [v.name for v in leaf.visuals if v.name.startswith("batten_")]
        ctx.check("2 cross battens present", len(battens) == _N_BATTENS, details=str(battens))
    elif r.leaf_fill == "barred_grate":
        leaf = object_model.get_part("leaf")
        slats = [v.name for v in leaf.visuals if v.name.startswith("slat_")]
        ctx.check(
            "N slats inlined (Rule 1) with slat_i naming",
            len(slats) == r.grate_slat_count,
            details=f"slats={sorted(slats)} expected n={r.grate_slat_count}",
        )
        n = r.grate_slat_count
        inner_d = r.grate_d - 2.0 * _FRAME_BAR_W
        slat_pitch = inner_d / (n + 1)
        gap_width = slat_pitch - _SLAT_W
        open_ratio = (n + 1) * gap_width / inner_d
        ctx.check(
            "grate is see-through (open ratio > 0.5)",
            gap_width > 0.0 and open_ratio > 0.5,
            details=f"gap={gap_width:.4f}, open_ratio={open_ratio:.2f}",
        )

    # --- Grip: nested handle joint topology + actuation. ---
    if r.grip == "folding_bar_handle" and r.hinge_mechanism != "double_bifold":
        jh = object_model.get_articulation("lid_to_handle")
        ctx.check(
            "folding handle is a nested REVOLUTE about world -X",
            jh.articulation_type == ArticulationType.REVOLUTE and abs(jh.axis[0]) > 0.9,
            details=f"axis={tuple(jh.axis)}",
        )
        handle = object_model.get_part("lift_handle")
        with ctx.pose({jh: 0.0}):
            hc = ctx.part_world_aabb(handle)
        with ctx.pose({jh: 1.4}):
            ho = ctx.part_world_aabb(handle)
        if hc is not None and ho is not None:
            ctx.check(
                "folding handle lifts out of the pocket",
                ho[1][2] > hc[1][2] + 0.01,
                details=f"closed_top={hc[1][2]:.3f} open_top={ho[1][2]:.3f}",
            )

    # --- Leaf seats on lip (wider than throat). ---
    if r.leaf_fill == "barred_grate":
        seat_ok = r.grate_w / 2.0 >= r.throat_r + 0.005
    else:
        seat_ok = r.lid_r >= r.throat_r + 0.02
    ctx.check("leaf is wider than the throat so it seats on the lip", seat_ok,
              details=f"lid_r={r.lid_r:.3f} grate_w/2={r.grate_w / 2.0:.3f} throat_r={r.throat_r:.3f}")

    # --- slot_choices recorded matches the build. ---
    ctx.check(
        "slot_choices recorded matches build",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "TrapDoorConfig",
    "ResolvedTrapDoorConfig",
    "build_trap_door",
    "build_seeded_trap_door",
    "config_from_seed",
    "resolve_config",
    "run_trap_door_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
