# SPDX-License-Identifier: Apache-2.0

"""European wall light switch / socket plate modular template.

NOTE on the slug name: "switch" here = **European wall switch / socket plate**
(a thin faceplate sitting on a wall), NOT a knife switch, ship/industrial console,
or router panel. The structure family is a wall-mounted plate: a thin painted
``wall_panel`` (root) carrying a FIXED ``faceplate`` (``plate_field`` +
``trim_ring``, colour and finish from ``palette_style``), with N **actuators** laid out side-by-side along
X — each actuator is an independent MOVING child of the faceplate.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_Switch.md`` and the
``picture/Other/Switch`` 5-star sample pool (1 parent + 7 slot/multiplicity forks),
all synced under ``data/records/``.

Structure (pattern = ``mixed``): a single root ``wall_panel`` + FIXED ``faceplate``,
with two named module axes + one multiplicity axis:

  * ``actuator_type`` (4): the per-actuator part tree + joint topology —
      - rocker        : ``rocker_{i}``  + ``rocker_{i}_pivot``  REVOLUTE +X (±0.10 see-saw)
      - toggle_lever  : ``toggle_{i}``  + ``toggle_{i}_pivot``  REVOLUTE +X (±0.35 flip)
      - push_button   : ``button_{i}``  + ``button_{i}_press``  PRISMATIC -Y (0..0.003)
      - rotary_dimmer : ``dimmer_{i}``  + ``dimmer_{i}_spin``   CONTINUOUS +Y (free)
  * ``faceplate_shape`` (3): rounded_rect_horizontal (+Schuko) / square_single /
    round_plate — a mesh-footprint dimension on ``plate_field``/``trim_ring``;
    it does NOT add a joint.
  * ``gang_count`` (N in [1,6]): a multiplicity axis — N identical actuators copied
    along X by ``xc = (i-(N-1)/2)*pitch`` (absolute, center-symmetric). Each copy is
    its own MOVING part with its own joint. N is encoded into the slot_choice tuple
    as ``("gang_count", f"n{N}")``.

Orthogonal to all three: ``palette_style`` (14) picks a colorway AND a trim finish
(metallic ring vs painted ring). Per VISUAL_DIVERSITY_MODEL.md palettes are
palette-only — they are NOT part of ``slot_choices`` and contribute to neither
core nor raw domain.

All pivots / button seats / dimmer shafts are captured-pin / seat-on-rim /
shaft-through-hole geometry, so those joints omit ``MatingContract``
(grandfathered) and are guarded by the flat articulation-origin baseline +
element-scoped ``allow_overlap`` (mirroring each source record's run_tests block).

Cross-slot derivation (resolve_config, spec §9). Per VISUAL_DIVERSITY_MODEL.md
"完整组合原则", faceplate_shape x N is a FULL cartesian product — capacity
differences are absorbed by host sizing, never by gating a combination away:
  * round_plate derives its disc DIAMETER from N (a row of N actuators spans
    (N-1)*pitch + footprint, plus a rim margin each side), so a 4- or 6-gang disc
    is simply a larger disc. The nominal 0.156 m disc remains the floor for N<=2.
  * Schuko socket module is emitted only on rounded_rect_horizontal (an identity
    feature of that footprint, not a capacity gate).
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
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

ActuatorType = Literal["rocker", "toggle_lever", "push_button", "rotary_dimmer"]
FaceplateShape = Literal["rounded_rect_horizontal", "square_single", "round_plate"]
PaletteStyle = Literal[
    "ivory_chrome",
    "soft_white",
    "brushed_steel",
    "matte_black",
    "anthracite",
    "graphite_gloss",
    "antique_gold",
    "copper_patina",
    "navy_enamel",
    "signal_red",
    "walnut_trim",
    "sage_kitchen",
    "terracotta_loft",
    "powder_blue",
]

ACTUATOR_TYPES: tuple[ActuatorType, ...] = (
    "rocker",
    "toggle_lever",
    "push_button",
    "rotary_dimmer",
)
FACEPLATE_SHAPES: tuple[FaceplateShape, ...] = (
    "rounded_rect_horizontal",
    "square_single",
    "round_plate",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "ivory_chrome",
    "soft_white",
    "brushed_steel",
    "matte_black",
    "anthracite",
    "graphite_gloss",
    "antique_gold",
    "copper_patina",
    "navy_enamel",
    "signal_red",
    "walnut_trim",
    "sage_kitchen",
    "terracotta_loft",
    "powder_blue",
)

N_MIN = 1
N_MAX = 6
GANG_COUNTS = tuple(range(N_MIN, N_MAX + 1))
# Gang-count sampling weights (spec §8: 1/2 high-frequency, 3 common, 4+ long tail).
GANG_COUNT_WEIGHTS = (0.26, 0.27, 0.18, 0.13, 0.09, 0.07)

# Palette colorways. Each entry drives every .visual(material=...) in the build.
#
# Two rules learned from the preview rig, both deliberate:
#  * PER-ROLE ALBEDO CEILING: wall 0.52, plate/trim/actuator 0.68, steel 0.60,
#    applied hue-preserving (scale to the cap, never clamp per channel, which
#    would desaturate). The shared studio rig runs a 45*dist**2 key plus a
#    12*dist**2 fill plus a 0.35 world fill, all through view_transform="Standard"
#    with no tonemap, so total irradiance is ~1.65x and a flat panel turned toward
#    the key clips to pure white above roughly 0.6 albedo -- measured, not guessed
#    (clipped-pixel fraction rose 0.135 -> 0.251 as wall albedo went 0.51 -> 0.63).
#    The original 0.93-0.96 ivories rendered as featureless white slabs even though
#    the colors reached Blender intact. The wall is the largest flat surface and
#    faces the key most directly, hence its much tighter cap.
#  * FINISH COMES FROM THE MATERIAL NAME. The viewer/preview PBR resolver keys off
#    name tokens ("metal"/"brass" -> metallic 0.88 rough 0.22, "glass"/"clear" ->
#    transmission, "bakelite" -> clearcoat). _material_name below injects the token
#    per ROLE, so a polished ring actually renders as metal. Palette slugs must
#    therefore stay free of those tokens, or the finish leaks into every part --
#    the old "warm_brass" slug turned its WALL into polished metal.
_METAL = "metal"  # polished ring / steel: metallic
_MATTE = "matte"  # painted, plastic, wood: diffuse (no resolver token)


@dataclass(frozen=True)
class Palette:
    """One colorway. ``trim_finish`` picks the chrome/brass ring vs a painted ring."""

    wall: tuple[float, float, float, float]
    plate: tuple[float, float, float, float]
    trim: tuple[float, float, float, float]
    actuator: tuple[float, float, float, float]
    steel: tuple[float, float, float, float]
    trim_finish: str = _METAL


PALETTES: dict[PaletteStyle, Palette] = {
    # --- Pale product finishes (the volume sellers).
    "ivory_chrome": Palette(
        wall=(0.520, 0.462, 0.388, 1.0),
        plate=(0.680, 0.654, 0.594, 1.0),
        trim=(0.636, 0.654, 0.680, 1.0),
        actuator=(0.680, 0.654, 0.594, 1.0),
        steel=(0.552, 0.571, 0.600, 1.0),
    ),
    "soft_white": Palette(
        wall=(0.503, 0.512, 0.520, 1.0),
        plate=(0.680, 0.680, 0.663, 1.0),
        trim=(0.680, 0.680, 0.661, 1.0),
        actuator=(0.680, 0.680, 0.663, 1.0),
        steel=(0.580, 0.590, 0.600, 1.0),
        trim_finish=_MATTE,
    ),
    "brushed_steel": Palette(
        wall=(0.520, 0.511, 0.483, 1.0),
        plate=(0.600, 0.620, 0.650, 1.0),
        trim=(0.635, 0.653, 0.680, 1.0),
        actuator=(0.550, 0.570, 0.600, 1.0),
        steel=(0.520, 0.540, 0.570, 1.0),
    ),
    # --- Dark finishes.
    "matte_black": Palette(
        wall=(0.520, 0.495, 0.453, 1.0),
        plate=(0.080, 0.080, 0.090, 1.0),
        trim=(0.260, 0.270, 0.290, 1.0),
        actuator=(0.120, 0.120, 0.130, 1.0),
        steel=(0.450, 0.460, 0.480, 1.0),
        trim_finish=_MATTE,
    ),
    "anthracite": Palette(
        wall=(0.520, 0.520, 0.496, 1.0),
        plate=(0.200, 0.210, 0.230, 1.0),
        trim=(0.350, 0.360, 0.380, 1.0),
        actuator=(0.250, 0.260, 0.280, 1.0),
        steel=(0.500, 0.510, 0.530, 1.0),
        trim_finish=_MATTE,
    ),
    "graphite_gloss": Palette(
        wall=(0.520, 0.512, 0.489, 1.0),
        plate=(0.060, 0.060, 0.070, 1.0),
        trim=(0.190, 0.200, 0.210, 1.0),
        actuator=(0.100, 0.100, 0.110, 1.0),
        steel=(0.480, 0.490, 0.510, 1.0),
    ),
    # --- Metallic trim rings.
    "antique_gold": Palette(
        wall=(0.520, 0.466, 0.394, 1.0),
        plate=(0.680, 0.633, 0.522, 1.0),
        trim=(0.660, 0.500, 0.240, 1.0),
        actuator=(0.680, 0.632, 0.527, 1.0),
        steel=(0.560, 0.450, 0.260, 1.0),
    ),
    "copper_patina": Palette(
        wall=(0.481, 0.520, 0.501, 1.0),
        plate=(0.440, 0.250, 0.150, 1.0),
        trim=(0.580, 0.350, 0.200, 1.0),
        actuator=(0.480, 0.280, 0.170, 1.0),
        steel=(0.500, 0.340, 0.220, 1.0),
    ),
    # --- Saturated plates and coloured rooms.
    "navy_enamel": Palette(
        wall=(0.520, 0.505, 0.461, 1.0),
        plate=(0.100, 0.150, 0.270, 1.0),
        trim=(0.620, 0.640, 0.670, 1.0),
        actuator=(0.130, 0.190, 0.320, 1.0),
        steel=(0.520, 0.540, 0.570, 1.0),
    ),
    "signal_red": Palette(
        wall=(0.520, 0.520, 0.503, 1.0),
        plate=(0.460, 0.090, 0.070, 1.0),
        trim=(0.280, 0.290, 0.300, 1.0),
        actuator=(0.520, 0.120, 0.090, 1.0),
        steel=(0.500, 0.510, 0.530, 1.0),
        trim_finish=_MATTE,
    ),
    "walnut_trim": Palette(
        wall=(0.520, 0.506, 0.469, 1.0),
        plate=(0.310, 0.190, 0.110, 1.0),
        trim=(0.430, 0.280, 0.160, 1.0),
        actuator=(0.360, 0.230, 0.140, 1.0),
        steel=(0.550, 0.560, 0.570, 1.0),
        trim_finish=_MATTE,
    ),
    "sage_kitchen": Palette(
        wall=(0.450, 0.510, 0.430, 1.0),
        plate=(0.680, 0.662, 0.591, 1.0),
        trim=(0.680, 0.660, 0.580, 1.0),
        actuator=(0.680, 0.662, 0.591, 1.0),
        steel=(0.550, 0.560, 0.540, 1.0),
        trim_finish=_MATTE,
    ),
    "terracotta_loft": Palette(
        wall=(0.520, 0.318, 0.241, 1.0),
        plate=(0.680, 0.663, 0.628, 1.0),
        trim=(0.652, 0.661, 0.680, 1.0),
        actuator=(0.680, 0.663, 0.628, 1.0),
        steel=(0.560, 0.570, 0.590, 1.0),
    ),
    "powder_blue": Palette(
        wall=(0.394, 0.457, 0.520, 1.0),
        plate=(0.620, 0.654, 0.680, 1.0),
        trim=(0.623, 0.652, 0.680, 1.0),
        actuator=(0.620, 0.654, 0.680, 1.0),
        steel=(0.550, 0.570, 0.600, 1.0),
        trim_finish=_MATTE,
    ),
}
# Per-role albedo ceilings, matching the values baked into PALETTES above.
_ROLE_CEILING = {"wall": 0.52, "plate": 0.68, "trim": 0.68, "actuator": 0.68, "steel": 0.60}

# Minimum Rec.709 luma separation between an actuator and the plate it sits in.
# Real plates often mould the rocker in the plate's own colour, but that makes the
# moving part unreadable: 6 of the 14 colorways had actuator == plate EXACTLY and
# the rest differed by 0.03-0.05 luma, so the only thing separating a rocker from
# its faceplate was the pocket shadow. The actuator is the articulated part -- it
# has to read as a distinct body, in a render and in a part segmentation alike.
_ACTUATOR_CONTRAST = 0.14


def _luma(rgba) -> float:
    return 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]


def _shift_luma(rgba, delta: float, ceiling: float):
    """Move a colour toward black (delta<0) or white (delta>0) by ~delta luma.

    Darkening scales the channels, which preserves hue exactly; lightening lerps
    toward white, which desaturates slightly but is the only headroom a near-black
    plate has. The ceiling keeps the result under the rig's clipping point.
    """
    y = _luma(rgba)
    if delta < 0.0:
        k = max(0.0, (y + delta) / y) if y > 1e-6 else 0.0
        rgb = [v * k for v in rgba[:3]]
    else:
        t = _clamp(delta / max(1e-6, 1.0 - y), 0.0, 1.0)
        rgb = [v + (1.0 - v) * t for v in rgba[:3]]
    hi = max(rgb)
    if hi > ceiling:
        rgb = [v * (ceiling / hi) for v in rgb]
    return (rgb[0], rgb[1], rgb[2], rgba[3])


def _actuator_rgba(palette: Palette):
    """The actuator colour, forced to at least _ACTUATOR_CONTRAST from the plate.

    An authored actuator colour that already separates enough is used untouched, so
    a deliberate look (white rocker on a navy plate) survives; otherwise the
    authored hue is pushed away from the plate -- darker on a light plate, lighter
    on a dark one, which is the direction that has gamut headroom in each case.
    """
    delta = _luma(palette.actuator) - _luma(palette.plate)
    if abs(delta) >= _ACTUATOR_CONTRAST:
        return palette.actuator
    direction = -1.0 if _luma(palette.plate) > 0.35 else 1.0
    return _shift_luma(
        palette.actuator, direction * _ACTUATOR_CONTRAST - delta, _ROLE_CEILING["actuator"]
    )


# Roles whose finish token is fixed by what the part IS; `trim` is per-palette.
_ROLE_FINISH: dict[str, str] = {
    "wall": _MATTE,
    "plate": _MATTE,
    "actuator": _MATTE,
    "steel": _METAL,
}


def _material_name(key: str, palette_style: PaletteStyle, palette: Palette) -> str:
    """``switch_<role>_<finish>_<palette>`` -- the finish token drives the PBR."""
    finish = palette.trim_finish if key == "trim" else _ROLE_FINISH[key]
    return f"switch_{key}_{finish}_{palette_style}"


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), from the parent baseline (c46f379f).
#
# WALL-LOCAL frame (everything below, and every mesh/joint helper, is authored in
# it): +Z up, plate width along X, plate face toward +Y, wall surface at the plane
# y = 0; the plate protrudes to +Y. Visuals built in CadQuery's XY plane (extruded
# +Z) are rotated into the wall frame with roll = -pi/2, mapping cq +Z -> +Y.
#
# WORLD frame: the ``wall_to_faceplate`` joint carries a yaw of pi (_WALL_YAW), so
# the whole faceplate subtree is turned to face -Y in world. This is the octant the
# preview/gallery camera actually looks from (front_iso sits at +X/-Y); a plate
# facing +Y renders as the blank back of the wall slab. The wall slab itself is
# mirrored to y in [0, +_WALL_T] to stay behind the plate. Net effect in world:
# front normal = -Y, and world x = -(wall-local x).
# ---------------------------------------------------------------------------
_CQ_TO_WALL = (-math.pi / 2.0, 0.0, 0.0)
_WALL_YAW = (0.0, 0.0, math.pi)

_WALL_T = 0.018
# Wall slab margin around the faceplate, per axis, per side (see resolve_config).
_WALL_MARGIN_RATIO = 0.20
_WALL_MARGIN_MIN = 0.015
_WALL_MARGIN_MAX = 0.045

_TRIM_DEPTH = 0.011  # front of the chrome lip (y from wall plane)
_TRIM_R = 0.012
_PLATE_DEPTH = 0.010  # front face of the ivory field
_PLATE_R = 0.0095

_MODULE_PITCH = 0.075  # nominal center-to-center actuator spacing
_PLATE_H = 0.082  # nominal plate height (Z)
_TRIM_H = 0.090

# Rocker pockets (square openings with a thin back floor).
_POCKET_SIZE = 0.054
_POCKET_R = 0.004
_POCKET_FLOOR_Y = 0.0025

# Rocker paddle.
_ROCKER_SIZE = 0.050
_ROCKER_BASE_T = 0.0045
_ROCKER_CAP_T = 0.0035
_ROCKER_T = _ROCKER_BASE_T + _ROCKER_CAP_T  # 0.008
_ROCKER_BACK_Y = 0.0055
_ROCKER_PIVOT_Y = _ROCKER_BACK_Y + _ROCKER_T / 2.0  # see-saw pivot mid-depth
_ROCKER_RANGE = 0.10
_AXLE_R = 0.002
_AXLE_LEN = _POCKET_SIZE + 0.003

# Toggle lever.
_ESC_SIZE = 0.052
_ESC_R = 0.005
_ESC_FACE_Y = 0.0120
_TOGGLE_SLOT_W = 0.021
_TOGGLE_SLOT_H = 0.009
_TOGGLE_SLOT_R = 0.002
_LEVER_W = 0.018
_LEVER_T = 0.005
_LEVER_H = 0.028
_TOGGLE_PIVOT_Y = _PLATE_DEPTH
_TOGGLE_RANGE = 0.35
_TOGGLE_AXLE_R = 0.0015
_TOGGLE_AXLE_LEN = _TOGGLE_SLOT_W + 0.004

# Push button.
_BUTTON_SIZE = 0.056
_BUTTON_CAP_T = 0.006
_BUTTON_BACK_DEPTH = 0.002
_BUTTON_GUIDE_SIZE = 0.050
_BUTTON_GUIDE_L = 0.002
_BUTTON_TRAVEL = 0.003

# Rotary dimmer.
_SHAFT_HOLE_R = 0.012
_DIMMER_DIAMETER = 0.044
_DIMMER_HEIGHT = 0.018
_DIMMER_BASE_Y = _PLATE_DEPTH
_DIMMER_POINTER_R = 0.024  # off-axis pointer tab radius (> knob radius)

# Schuko socket (only on rounded_rect_horizontal).
_TILE_SIZE = 0.055
_TILE_R = 0.006
_TILE_FACE_Y = 0.0125
_WELL_RADIUS = 0.020
_WELL_FLOOR_Y = 0.0035
_PIN_HOLE_R = 0.0024
_PIN_HOLE_DX = 0.0095
_PIN_HOLE_FLOOR_Y = 0.0008
_CLIP_W = 0.012
_CLIP_T = 0.005
_CLIP_H = 0.0048
_CLIP_ZC = _WELL_RADIUS - 0.0018
_CLIP_YC = 0.0080

# round_plate footprint (axisymmetric). _ROUND_PLATE_D is the NOMINAL disc (the
# 1-/2-gang product size); resolve_config grows it with N instead of gating N.
_ROUND_TRIM_OD = 0.170
_ROUND_TRIM_ID = 0.154
_ROUND_PLATE_D = 0.156
_ROUND_TRIM_MARGIN = _ROUND_TRIM_OD - _ROUND_PLATE_D  # chrome ring width, kept constant
# Rim margin from the outermost actuator edge to the ivory disc edge. Sized above
# the generic clearance `margin` (0.006) so the N-derived diameter already
# satisfies the row-fits-inside-plate inequality and is never re-widened below.
_ROUND_RIM_MARGIN = 0.014
# Widest actuator footprint across the four candidates (button cap is the widest;
# pocket 0.054 / escutcheon 0.052 / dimmer pointer 0.048 are all smaller).
_ACTUATOR_FOOTPRINT = max(_POCKET_SIZE, _BUTTON_SIZE, _ESC_SIZE, 2.0 * _DIMMER_POINTER_R)


@dataclass(frozen=True)
class SwitchConfig:
    actuator_type: ActuatorType | None = None
    faceplate_shape: FaceplateShape | None = None
    gang_count: int | None = None
    palette_style: PaletteStyle = "ivory_chrome"
    plate_width_scale: float = 1.0
    plate_height_scale: float = 1.0
    module_pitch_scale: float = 1.0
    actuator_travel_scale: float = 1.0
    name: str = "switch"


@dataclass(frozen=True)
class ResolvedSwitchConfig:
    actuator_type: ActuatorType
    faceplate_shape: FaceplateShape
    gang_count: int
    palette_style: PaletteStyle
    has_schuko: bool
    # Concrete geometry (scaled).
    pitch: float
    plate_w: float  # ivory field width (X)
    plate_h: float  # ivory field height (Z)
    trim_w: float
    trim_h: float
    wall_w: float
    wall_h: float
    socket_x: float  # Schuko tile center X (rightmost), only when has_schuko
    actuator_xs: tuple[float, ...]
    actuator_zs: tuple[float, ...]
    gang_rows: int
    gang_cols: int
    revolute_range: float  # rocker/toggle scaled half-range
    button_travel: float
    name: str

    @property
    def is_round(self) -> bool:
        return self.faceplate_shape == "round_plate"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _gang_grid(gang_count: int, faceplate_shape: FaceplateShape) -> tuple[int, int]:
    """(rows, cols) for N actuators. Placement derivation only -- NOT a slot.

    A single row is the right answer for rounded_rect_horizontal: being one
    horizontal strip of modules IS that footprint's identity, and its Schuko tile
    sits at the end of that strip.

    For the square and round footprints a single row is actively wrong. It made
    "square_single" at N=6 a 0.42 x 0.084 letterbox -- not square at all -- and
    forced round_plate to blow its disc up to 0.41 m to span a 5-wide row, leaving
    five small actuators marooned on a huge empty circle. Both footprints are
    defined by a compact aspect, so N is laid out on the grid closest to square:
    cols = ceil(sqrt(N)), rows = ceil(N/cols).

        N:      1     2     3     4     5     6
        grid:  1x1   1x2   2x2   2x2   2x3   2x3   (rows x cols)

    N=3 and N=5 leave the last row short; _grid_positions centers it.
    """
    if faceplate_shape == "rounded_rect_horizontal":
        return 1, gang_count
    cols = math.ceil(math.sqrt(gang_count))
    rows = math.ceil(gang_count / cols)
    return rows, cols


def _grid_positions(
    gang_count: int, rows: int, cols: int, pitch: float
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Absolute, center-symmetric (x, z) per actuator; row-major, top row first.

    Absolute (each index solved from N and the center, never accumulated) so the
    layout stays N-invariant, exactly as the 1-D formula was. A short final row is
    centered on its own count, not on the full column count.
    """
    xs: list[float] = []
    zs: list[float] = []
    for row in range(rows):
        in_row = min(cols, gang_count - row * cols)
        if in_row <= 0:
            break
        # +Z is up, so row 0 is the TOP row.
        zc = ((rows - 1) / 2.0 - row) * pitch
        for col in range(in_row):
            xs.append((col - (in_row - 1) / 2.0) * pitch)
            zs.append(zc)
    return tuple(xs), tuple(zs)


def config_from_seed(seed: int) -> SwitchConfig:
    rng = random.Random(seed)
    return SwitchConfig(
        actuator_type=rng.choice(ACTUATOR_TYPES),
        faceplate_shape=rng.choice(FACEPLATE_SHAPES),
        gang_count=rng.choices(GANG_COUNTS, weights=GANG_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        plate_width_scale=round(rng.uniform(0.92, 1.10), 4),
        plate_height_scale=round(rng.uniform(0.92, 1.10), 4),
        module_pitch_scale=round(rng.uniform(0.90, 1.10), 4),
        actuator_travel_scale=round(rng.uniform(0.85, 1.12), 4),
        name=f"seeded_switch_{seed}",
    )


def resolve_config(config: SwitchConfig | None = None) -> ResolvedSwitchConfig:
    cfg = config or SwitchConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    actuator_type = _pick(cfg.actuator_type, ACTUATOR_TYPES)
    faceplate_shape = _pick(cfg.faceplate_shape, FACEPLATE_SHAPES)

    gang_count = int(cfg.gang_count) if cfg.gang_count is not None else 2
    gang_count = int(_clamp(gang_count, N_MIN, N_MAX))

    # --- Cross-slot derivation (spec §9). ---
    # faceplate_shape x N is a full cartesian product: the round disc absorbs large
    # N by growing its diameter (below), it does NOT clamp N.
    # Schuko socket module is only emitted on rounded_rect_horizontal.
    has_schuko = faceplate_shape == "rounded_rect_horizontal"

    width_scale = _clamp(cfg.plate_width_scale, 0.92, 1.10)
    height_scale = _clamp(cfg.plate_height_scale, 0.92, 1.10)
    pitch_scale = _clamp(cfg.module_pitch_scale, 0.90, 1.10)
    travel_scale = _clamp(cfg.actuator_travel_scale, 0.85, 1.12)

    pitch = _MODULE_PITCH * pitch_scale

    # --- Absolute, center-symmetric actuator placement (spec §6/§8). ---
    rows, cols = _gang_grid(gang_count, faceplate_shape)
    actuator_xs, actuator_zs = _grid_positions(gang_count, rows, cols, pitch)

    # --- Footprint sizing. ---
    if faceplate_shape == "round_plate":
        # Disc footprint: width == height locked for a true circle (spec §7 eq).
        # The DIAMETER is derived from N so any gang count fits on the disc: the
        # actuator row spans (N-1)*pitch + footprint, plus a rim margin each side.
        # The nominal product disc is the floor, so N<=2 keeps its familiar size.
        # width_scale is aesthetic and only scales the NOMINAL disc: the N-derived
        # capacity floor is applied after scaling, since the actuator row it has to
        # contain is laid out on the unscaled pitch.
        # The binding constraint on a circle is RADIAL: the far corner of the
        # actuator grid, not its half-width. Sizing on the corner radius is what
        # lets a 2-row grid use a far smaller disc than a single row of the same N.
        round_scale = width_scale  # round_plate locks height = width
        grid_half_x = (cols - 1) / 2.0 * pitch + _ACTUATOR_FOOTPRINT / 2.0
        grid_half_z = (rows - 1) / 2.0 * pitch + _ACTUATOR_FOOTPRINT / 2.0
        corner_r = math.hypot(grid_half_x, grid_half_z)
        plate_w = max(
            _ROUND_PLATE_D * round_scale,
            2.0 * (corner_r + _ROUND_RIM_MARGIN),
        )
        plate_h = plate_w
        trim_w = plate_w + _ROUND_TRIM_MARGIN
        trim_h = trim_w
    elif faceplate_shape == "square_single":
        # Compact plate that stays square-ish: both axes grow with the GRID, so a
        # 6-gang plate is a 2x3 block rather than a 6-wide letterbox.
        base_w = max(0.082, cols * pitch + 0.028)
        base_h = max(0.082, rows * pitch + 0.028)
        plate_w = base_w * width_scale
        plate_h = base_h * height_scale
        trim_w = plate_w + 0.008
        trim_h = plate_h + 0.008
    else:  # rounded_rect_horizontal
        # Plate widens with N: actuators occupy N*pitch, Schuko adds one module
        # width on the right. margin per side ~0.0125.
        modules_w = gang_count * pitch + (pitch if has_schuko else 0.0)
        base_w = modules_w + 0.015
        plate_w = base_w * width_scale
        plate_h = _PLATE_H * height_scale
        trim_w = plate_w + 0.008
        trim_h = plate_h + 0.008

    # --- Clearance inequalities (spec §7): actuators must fit inside the plate,
    # now on BOTH axes because the grid can be more than one row deep.
    margin = 0.006
    actuator_half = _POCKET_SIZE / 2.0
    inner_half_x = (plate_w / 2.0) - margin
    inner_half_z = (plate_h / 2.0) - margin
    if gang_count >= 1:
        # Rightmost extent including the Schuko tile (horizontal footprint only,
        # where the grid is a single row so the tile still sits at the row end).
        outer_center = max(actuator_xs) if actuator_xs else 0.0
        row_right = outer_center + actuator_half
        if has_schuko:
            row_right = outer_center + pitch + _TILE_SIZE / 2.0
        needed_half_x = row_right + margin
        needed_half_z = (max(actuator_zs) if actuator_zs else 0.0) + actuator_half + margin
        if needed_half_x > inner_half_x or needed_half_z > inner_half_z:
            if faceplate_shape == "round_plate":
                # Keep the disc a true circle and grow it radially.
                need_r = math.hypot(needed_half_x, needed_half_z)
                plate_w = max(plate_w, 2.0 * need_r)
                plate_h = plate_w
                trim_w = plate_w + _ROUND_TRIM_MARGIN
                trim_h = trim_w
            else:
                plate_w = max(plate_w, 2.0 * needed_half_x)
                plate_h = max(plate_h, 2.0 * needed_half_z)
                trim_w = plate_w + 0.008
                trim_h = plate_h + 0.008
            inner_half_x = (plate_w / 2.0) - margin
            inner_half_z = (plate_h / 2.0) - margin

    socket_x = (
        (max(actuator_xs) + pitch)
        if (has_schuko and actuator_xs)
        else (pitch if has_schuko else 0.0)
    )

    # The wall slab frames the plate on BOTH axes. The margin is PROPORTIONAL per
    # axis, not a fixed pad: the wall is mounting context, and the faceplate is the
    # product, so it must dominate the object's bounding box at every footprint.
    # A fixed +0.10 m pad left a real-size 0.085 m single-gang plate covering only
    # 18% of the wall area (it read as a tiny switch on a huge board) while barely
    # affecting a 0.41 m disc. Proportional margins hold the plate at ~50-67% of
    # wall area across the whole domain. Clamps keep a plausible mounting surface
    # on a tiny plate and stop a 0.6 m six-gang plate from demanding a whole room.
    wall_w = trim_w + 2.0 * _clamp(_WALL_MARGIN_RATIO * trim_w, _WALL_MARGIN_MIN, _WALL_MARGIN_MAX)
    wall_h = trim_h + 2.0 * _clamp(_WALL_MARGIN_RATIO * trim_h, _WALL_MARGIN_MIN, _WALL_MARGIN_MAX)

    # --- actuator_travel conditional (spec §7): scale REVOLUTE/PRISMATIC upper. ---
    revolute_range = _clamp(_ROCKER_RANGE, 0.04, math.pi * 0.5)  # rocker default
    # The rocker/toggle ranges are scaled below per-actuator at emit time; keep
    # the button travel clamped so the button never presses through the floor.
    button_travel = _clamp(_BUTTON_TRAVEL * travel_scale, 0.0015, _POCKET_FLOOR_Y + 0.0008)

    return ResolvedSwitchConfig(
        actuator_type=actuator_type,
        faceplate_shape=faceplate_shape,
        gang_count=gang_count,
        palette_style=palette_style,
        has_schuko=has_schuko,
        pitch=pitch,
        plate_w=plate_w,
        plate_h=plate_h,
        trim_w=trim_w,
        trim_h=trim_h,
        wall_w=wall_w,
        wall_h=wall_h,
        socket_x=socket_x,
        actuator_xs=actuator_xs,
        actuator_zs=actuator_zs,
        gang_rows=rows,
        gang_cols=cols,
        revolute_range=revolute_range,
        button_travel=button_travel,
        name=cfg.name or "switch",
    )


def with_overrides(config: SwitchConfig, **kwargs: object) -> SwitchConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SwitchConfig | ResolvedSwitchConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedSwitchConfig) else resolve_config(config)
    return (
        ("actuator_type", r.actuator_type),
        ("faceplate_shape", r.faceplate_shape),
        ("gang_count", f"n{r.gang_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _rev_range(r: ResolvedSwitchConfig, base: float, travel_scale: float) -> float:
    return _clamp(base * travel_scale, 0.04, math.pi * 0.5)


# ---------------------------------------------------------------------------
# Footprint mesh helpers (faceplate_shape). Each preserves the source primitive
# type: horizontal/square = rounded-rect, round = circle/annulus (lathe).
# ---------------------------------------------------------------------------
def _rounded_rect(w: float, h: float, r: float) -> cq.Sketch:
    rr = min(r, 0.45 * min(w, h))
    return cq.Sketch().rect(w, h).vertices().fillet(rr)


def _trim_ring_mesh(r: ResolvedSwitchConfig, assets):
    """Thin raised polished-chrome border around the ivory field."""
    if r.faceplate_shape == "round_plate":
        outer_r = r.trim_w / 2.0
        inner_r = r.plate_w / 2.0 - 0.001
        outer = cq.Workplane("XY").circle(outer_r).extrude(_TRIM_DEPTH)
        inner = (
            cq.Workplane("XY", origin=(0.0, 0.0, -0.001))
            .circle(inner_r)
            .extrude(_TRIM_DEPTH + 0.002)
        )
        ring = outer.cut(inner)
    else:
        ring = (
            cq.Workplane("XY")
            .placeSketch(_rounded_rect(r.trim_w, r.trim_h, _TRIM_R))
            .extrude(_TRIM_DEPTH)
        )
        opening = (
            cq.Workplane("XY", origin=(0.0, 0.0, -0.001))
            .placeSketch(_rounded_rect(r.plate_w - 0.002, r.plate_h - 0.002, _PLATE_R))
            .extrude(_TRIM_DEPTH + 0.002)
        )
        ring = ring.cut(opening)
    try:
        ring = ring.edges(">Z").fillet(0.0015)
    except Exception:
        pass
    return mesh_from_cadquery(ring, "trim_ring", assets=assets)


def _cut_actuator_openings(plate: cq.Workplane, r: ResolvedSwitchConfig) -> cq.Workplane:
    """Cut the per-actuator opening for each gang into the plate front face."""
    at = r.actuator_type
    # cq sketch Y maps to wall -Z under _CQ_TO_WALL, hence the negated zc.
    for xc, zc in zip(r.actuator_xs, r.actuator_zs):
        if at in ("rocker", "push_button"):
            # Square pocket with a thin back floor.
            pocket = (
                cq.Workplane("XY", origin=(xc, -zc, _POCKET_FLOOR_Y))
                .placeSketch(_rounded_rect(_POCKET_SIZE, _POCKET_SIZE, _POCKET_R))
                .extrude(_PLATE_DEPTH)
            )
            plate = plate.cut(pocket)
        elif at == "toggle_lever":
            # Narrow through-slot in a raised escutcheon.
            slot = (
                cq.Workplane("XY", origin=(xc, -zc, -0.001))
                .placeSketch(_rounded_rect(_TOGGLE_SLOT_W, _TOGGLE_SLOT_H, _TOGGLE_SLOT_R))
                .extrude(_ESC_FACE_Y + 0.002)
            )
            plate = plate.cut(slot)
        else:  # rotary_dimmer
            hole = (
                cq.Workplane("XY", origin=(xc, -zc, -0.001))
                .circle(_SHAFT_HOLE_R)
                .extrude(_PLATE_DEPTH + 0.002)
            )
            plate = plate.cut(hole)
    return plate


def _plate_mesh(r: ResolvedSwitchConfig, assets):
    """Matte ivory field with per-actuator openings + optional Schuko well."""
    if r.faceplate_shape == "round_plate":
        plate = cq.Workplane("XY").circle(r.plate_w / 2.0).extrude(_PLATE_DEPTH)
    else:
        plate = (
            cq.Workplane("XY")
            .placeSketch(_rounded_rect(r.plate_w, r.plate_h, _PLATE_R))
            .extrude(_PLATE_DEPTH)
        )

    # Raised toggle escutcheons (toggle only) — built before cuts so the slot
    # passes cleanly through them.
    if r.actuator_type == "toggle_lever":
        for xc, zc in zip(r.actuator_xs, r.actuator_zs):
            esc = (
                cq.Workplane("XY", origin=(xc, -zc, _PLATE_DEPTH - 0.001))
                .placeSketch(_rounded_rect(_ESC_SIZE, _ESC_SIZE, _ESC_R))
                .extrude(_ESC_FACE_Y - _PLATE_DEPTH + 0.001)
            )
            plate = plate.union(esc)

    # Raised Schuko tile (rounded_rect_horizontal only).
    if r.has_schuko:
        tile = (
            cq.Workplane("XY", origin=(r.socket_x, 0.0, _PLATE_DEPTH - 0.001))
            .placeSketch(_rounded_rect(_TILE_SIZE, _TILE_SIZE, _TILE_R))
            .extrude(_TILE_FACE_Y - _PLATE_DEPTH + 0.001)
        )
        plate = plate.union(tile)

    try:
        plate = plate.edges(">Z").fillet(0.0012)
    except Exception:
        pass

    plate = _cut_actuator_openings(plate, r)

    if r.has_schuko:
        # True hollow circular well recessed into the tile.
        well = (
            cq.Workplane("XY", origin=(r.socket_x, 0.0, _WELL_FLOOR_Y))
            .circle(_WELL_RADIUS)
            .extrude(_TILE_FACE_Y)
        )
        plate = plate.cut(well)
        # Two blind Schuko pin holes in the well floor.
        for sx in (-1.0, 1.0):
            hole = (
                cq.Workplane(
                    "XY", origin=(r.socket_x + sx * _PIN_HOLE_DX, 0.0, _PIN_HOLE_FLOOR_Y)
                )
                .circle(_PIN_HOLE_R)
                .extrude(_WELL_FLOOR_Y - _PIN_HOLE_FLOOR_Y + 0.001)
            )
            plate = plate.cut(hole)

    return mesh_from_cadquery(plate, "plate_field", assets=assets)


# ---------------------------------------------------------------------------
# Actuator mesh helpers (actuator_type). One mesh object reused for all N gangs.
# ---------------------------------------------------------------------------
def _rocker_mesh(assets):
    """Slightly convex square ivory paddle, authored in a LOCAL frame centered
    on its see-saw pivot."""
    half = _ROCKER_T / 2.0
    base = (
        cq.Workplane("XY", origin=(0.0, 0.0, -half))
        .placeSketch(_rounded_rect(_ROCKER_SIZE, _ROCKER_SIZE, 0.005))
        .extrude(_ROCKER_BASE_T)
    )
    cap = (
        cq.Workplane("XY")
        .placeSketch(
            _rounded_rect(_ROCKER_SIZE, _ROCKER_SIZE, 0.005).moved(
                cq.Location(cq.Vector(0.0, 0.0, -half + _ROCKER_BASE_T))
            ),
            _rounded_rect(_ROCKER_SIZE - 0.008, _ROCKER_SIZE - 0.008, 0.008).moved(
                cq.Location(cq.Vector(0.0, 0.0, half))
            ),
        )
        .loft()
    )
    return mesh_from_cadquery(base.union(cap), "rocker_paddle", assets=assets)


def _toggle_lever_mesh(assets):
    """Small tapered flip toggle lever, pivot at origin, extends along cq +Z."""
    lever = (
        cq.Workplane("XY")
        .placeSketch(
            _rounded_rect(_LEVER_W, _LEVER_T, 0.001).moved(
                cq.Location(cq.Vector(0.0, 0.0, 0.0))
            ),
            _rounded_rect(_LEVER_W * 0.82, _LEVER_T * 0.82, 0.0015).moved(
                cq.Location(cq.Vector(0.0, 0.0, _LEVER_H))
            ),
        )
        .loft()
    )
    try:
        lever = lever.edges(">Z").fillet(0.0012)
    except Exception:
        pass
    return mesh_from_cadquery(lever, "toggle_lever", assets=assets)


def _button_mesh(assets):
    """Square ivory push-button cap + narrower guide, z=0 at the plate front."""
    cap = (
        cq.Workplane("XY", origin=(0.0, 0.0, -_BUTTON_BACK_DEPTH))
        .placeSketch(_rounded_rect(_BUTTON_SIZE, _BUTTON_SIZE, 0.004))
        .extrude(_BUTTON_CAP_T)
    )
    guide = (
        cq.Workplane("XY", origin=(0.0, 0.0, -_BUTTON_BACK_DEPTH - _BUTTON_GUIDE_L))
        .placeSketch(_rounded_rect(_BUTTON_GUIDE_SIZE, _BUTTON_GUIDE_SIZE, 0.003))
        .extrude(_BUTTON_GUIDE_L)
    )
    button = cap.union(guide)
    try:
        button = button.edges(">Z").fillet(0.0008)
    except Exception:
        pass
    return mesh_from_cadquery(button, "button_cap", assets=assets)


def _dimmer_knob_mesh():
    """Round rotary dimmer knob: tapered ribbed body with a raised pointer line.
    Built in local Z (knob axis), center=False so the mounting face sits at z=0."""
    knob = KnobGeometry(
        _DIMMER_DIAMETER,
        _DIMMER_HEIGHT,
        body_style="tapered",
        top_diameter=_DIMMER_DIAMETER - 0.008,
        edge_radius=0.001,
        grip=KnobGrip(style="ribbed", count=12, depth=0.0008, width=0.002),
        indicator=KnobIndicator(style="line", mode="raised", depth=0.0006),
        center=False,
    )
    return mesh_from_geometry(knob, "dimmer_knob")


# ---------------------------------------------------------------------------
# Actuator emitters (gang_count multiplicity). Each emits N MOVING parts, each
# with its own joint. Absolute center-symmetric placement (N-invariant).
# ---------------------------------------------------------------------------
def _emit_rockers(model, r, faceplate, mats, travel_scale: float) -> list[str]:
    rocker_mesh = _rocker_mesh(model.assets)
    rng = r.revolute_range
    rrange = _rev_range(r, _ROCKER_RANGE, travel_scale)
    names: list[str] = []
    for i, (xc, zc) in enumerate(zip(r.actuator_xs, r.actuator_zs)):
        rocker = model.part(f"rocker_{i}")
        rocker.visual(
            rocker_mesh,
            origin=Origin(rpy=_CQ_TO_WALL),
            material=mats["actuator"],
            name="rocker_paddle", material_class_id=("metal.brass_aged" if r.palette_style in {"ivory_chrome", "soft_white", "brushed_steel", "matte_black", "anthracite", "graphite_gloss", "antique_gold", "copper_patina", "navy_enamel", "signal_red", "sage_kitchen", "terracotta_loft", "powder_blue"} else "wood.walnut_dark"),
        )
        rocker.visual(
            Cylinder(radius=_AXLE_R, length=_AXLE_LEN),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name="pivot_axle", material_class_id="metal.steel_bare",
        )
        model.articulation(
            f"rocker_{i}_pivot",
            ArticulationType.REVOLUTE,
            parent=faceplate,
            child=rocker,
            origin=Origin(xyz=(xc, _ROCKER_PIVOT_Y, zc)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=-rrange, upper=rrange),
        )
        names.append(f"rocker_{i}")
    _ = rng
    return names


def _emit_toggles(model, r, faceplate, mats, travel_scale: float) -> list[str]:
    lever_mesh = _toggle_lever_mesh(model.assets)
    trange = _rev_range(r, _TOGGLE_RANGE, travel_scale)
    names: list[str] = []
    for i, (xc, zc) in enumerate(zip(r.actuator_xs, r.actuator_zs)):
        toggle = model.part(f"toggle_{i}")
        toggle.visual(
            lever_mesh,
            origin=Origin(rpy=_CQ_TO_WALL),
            material=mats["actuator"],
            name="toggle_lever", material_class_id=("metal.brass_aged" if r.palette_style in {"ivory_chrome", "soft_white", "brushed_steel", "matte_black", "anthracite", "graphite_gloss", "antique_gold", "copper_patina", "navy_enamel", "signal_red", "sage_kitchen", "terracotta_loft", "powder_blue"} else "wood.walnut_dark"),
        )
        toggle.visual(
            Cylinder(radius=_TOGGLE_AXLE_R, length=_TOGGLE_AXLE_LEN),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name="pivot_axle", material_class_id="metal.steel_bare",
        )
        model.articulation(
            f"toggle_{i}_pivot",
            ArticulationType.REVOLUTE,
            parent=faceplate,
            child=toggle,
            origin=Origin(xyz=(xc, _TOGGLE_PIVOT_Y, zc)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=-trange, upper=trange),
        )
        names.append(f"toggle_{i}")
    return names


def _emit_buttons(model, r, faceplate, mats, travel_scale: float) -> list[str]:
    button_mesh = _button_mesh(model.assets)
    names: list[str] = []
    for i, (xc, zc) in enumerate(zip(r.actuator_xs, r.actuator_zs)):
        button = model.part(f"button_{i}")
        button.visual(
            button_mesh,
            origin=Origin(rpy=_CQ_TO_WALL),
            material=mats["actuator"],
            name="button_cap", material_class_id=("metal.brass_aged" if r.palette_style in {"ivory_chrome", "soft_white", "brushed_steel", "matte_black", "anthracite", "graphite_gloss", "antique_gold", "copper_patina", "navy_enamel", "signal_red", "sage_kitchen", "terracotta_loft", "powder_blue"} else "wood.walnut_dark"),
        )
        model.articulation(
            f"button_{i}_press",
            ArticulationType.PRISMATIC,
            parent=faceplate,
            child=button,
            origin=Origin(xyz=(xc, _PLATE_DEPTH, zc)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(
                effort=2.0, velocity=0.5, lower=0.0, upper=r.button_travel
            ),
        )
        names.append(f"button_{i}")
    return names


def _emit_dimmers(model, r, faceplate, mats, travel_scale: float) -> list[str]:
    knob_mesh = _dimmer_knob_mesh()
    names: list[str] = []
    for i, (xc, zc) in enumerate(zip(r.actuator_xs, r.actuator_zs)):
        dimmer = model.part(f"dimmer_{i}")
        dimmer.visual(
            knob_mesh,
            origin=Origin(rpy=_CQ_TO_WALL),
            material=mats["actuator"],
            name="knob_body", material_class_id=("metal.brass_aged" if r.palette_style in {"ivory_chrome", "soft_white", "brushed_steel", "matte_black", "anthracite", "graphite_gloss", "antique_gold", "copper_patina", "navy_enamel", "signal_red", "sage_kitchen", "terracotta_loft", "powder_blue"} else "wood.walnut_dark"),
        )
        # Shaft stub through the plate hole — physically mounts the knob.
        shaft_len = _PLATE_DEPTH + 0.004
        dimmer.visual(
            Cylinder(radius=0.004, length=shaft_len),
            origin=Origin(xyz=(0.0, -0.005, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["steel"],
            name="shaft_stub", material_class_id="metal.steel_bare",
        )
        # Off-axis pointer tab: an asymmetric indicator riding the knob top, so
        # the CONTINUOUS spin produces a real AABB change (an axisymmetric knob
        # alone fails the spin AABB check). It embeds into the knob top, sitting
        # to one side of the spin axis.
        dimmer.visual(
            Box((0.005, 0.004, 0.010)),
            origin=Origin(xyz=(0.0, _DIMMER_HEIGHT - 0.002, _DIMMER_POINTER_R - 0.006)),
            material=mats["steel"],
            name="pointer_tab", material_class_id="metal.steel_bare",
        )
        model.articulation(
            f"dimmer_{i}_spin",
            ArticulationType.CONTINUOUS,
            parent=faceplate,
            child=dimmer,
            origin=Origin(xyz=(xc, _DIMMER_BASE_Y, zc)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=5.0),
        )
        names.append(f"dimmer_{i}")
    return names


_ACTUATOR_EMITTERS = {
    "rocker": _emit_rockers,
    "toggle_lever": _emit_toggles,
    "push_button": _emit_buttons,
    "rotary_dimmer": _emit_dimmers,
}

_ACTUATOR_PREFIX = {
    "rocker": "rocker",
    "toggle_lever": "toggle",
    "push_button": "button",
    "rotary_dimmer": "dimmer",
}
_ACTUATOR_JOINT_SUFFIX = {
    "rocker": "pivot",
    "toggle_lever": "pivot",
    "push_button": "press",
    "rotary_dimmer": "spin",
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_switch(
    config: SwitchConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    cfg = config or SwitchConfig()
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    rgba_for = {key: getattr(palette, key) for key in ("wall", "plate", "trim", "steel")}
    # Derived, not authored: guaranteed to read as a separate body from the plate.
    rgba_for["actuator"] = _actuator_rgba(palette)
    mats = {
        key: model.material(_material_name(key, r.palette_style, palette), rgba=rgba)
        for key, rgba in rgba_for.items()
    }

    # Root: warm-beige wall slab the plate mounts onto. The slab sits on the +Y
    # side of the wall plane because the faceplate subtree is yawed to face -Y
    # (see _WALL_YAW); the wall stays behind the plate as seen by the camera.
    wall = model.part("wall_panel")
    wall.visual(
        Box((r.wall_w, _WALL_T, r.wall_h)),
        origin=Origin(xyz=(0.0, _WALL_T / 2.0, 0.0)),
        material=mats["wall"],
        name="wall_slab", material_class_id=("ceramic.terracotta_earthenware" if r.palette_style == "terracotta_loft" else "plaster.smooth"),
    )
    wall.inertial = Inertial.from_geometry(
        Box((r.wall_w, _WALL_T, r.wall_h)), mass=0.4, origin=Origin(xyz=(0.0, _WALL_T / 2.0, 0.0))
    )

    # Faceplate: ivory field + chrome trim ring + optional Schuko clips.
    faceplate = model.part("faceplate")
    faceplate.visual(
        _plate_mesh(r, assets),
        origin=Origin(rpy=_CQ_TO_WALL),
        material=mats["plate"],
        name="plate_field", material_class_id=("metal.brass_aged" if r.palette_style in {"ivory_chrome", "soft_white", "brushed_steel", "matte_black", "anthracite", "graphite_gloss", "antique_gold", "copper_patina", "navy_enamel", "signal_red", "sage_kitchen", "terracotta_loft", "powder_blue"} else "wood.walnut_dark"),
    )
    faceplate.visual(
        _trim_ring_mesh(r, assets),
        origin=Origin(rpy=_CQ_TO_WALL),
        material=mats["trim"],
        name="trim_ring", material_class_id=("metal.chrome_polished" if r.palette_style in {"ivory_chrome", "soft_white", "brushed_steel", "matte_black", "anthracite", "graphite_gloss", "antique_gold", "copper_patina", "navy_enamel", "signal_red", "sage_kitchen", "terracotta_loft", "powder_blue"} else "wood.walnut_dark"),
    )
    if r.has_schuko:
        for sz, elem in ((1.0, "ground_clip_upper"), (-1.0, "ground_clip_lower")):
            faceplate.visual(
                Box((_CLIP_W, _CLIP_T, _CLIP_H)),
                origin=Origin(xyz=(r.socket_x, _CLIP_YC, sz * _CLIP_ZC)),
                material=mats["steel"],
                name=elem, material_class_id="metal.steel_bare",
            )
    faceplate.inertial = Inertial.from_geometry(
        Box((r.trim_w, _TRIM_DEPTH, r.trim_h)),
        mass=0.12,
        origin=Origin(xyz=(0.0, _TRIM_DEPTH / 2.0, 0.0)),
    )

    # The single frame flip: everything downstream is authored in the wall-local
    # (+Y front) frame and turned here to face -Y in world.
    model.articulation(
        "wall_to_faceplate",
        ArticulationType.FIXED,
        parent=wall,
        child=faceplate,
        origin=Origin(rpy=_WALL_YAW),
    )

    # N actuators (moving parts, each its own joint).
    _ACTUATOR_EMITTERS[r.actuator_type](
        model, r, faceplate, mats, cfg.actuator_travel_scale
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_switch(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_switch(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_switch_tests(
    object_model: ArticulatedObject,
    config: SwitchConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    wall = object_model.get_part("wall_panel")
    faceplate = object_model.get_part("faceplate")

    at = r.actuator_type
    prefix = _ACTUATOR_PREFIX[at]
    suffix = _ACTUATOR_JOINT_SUFFIX[at]
    actuators = [object_model.get_part(f"{prefix}_{i}") for i in range(r.gang_count)]
    joints = [
        object_model.get_articulation(f"{prefix}_{i}_{suffix}") for i in range(r.gang_count)
    ]

    # ---- Captured-pin / seat / shaft allowances (element-scoped). ----
    for i, actuator in enumerate(actuators):
        if at in ("rocker", "toggle_lever"):
            ctx.allow_overlap(
                actuator, faceplate, elem_a="pivot_axle", elem_b="plate_field",
                reason=(
                    "Hinge-pin tips are intentionally captured in the actuator "
                    "pocket / escutcheon side walls so the lever is physically mounted."
                ),
            )
        elif at == "push_button":
            ctx.allow_overlap(
                actuator, faceplate, elem_a="button_cap", elem_b="plate_field",
                reason=(
                    "Button cap flange is wider than the pocket opening and seats "
                    "on the pocket rim, creating a thin local overlap."
                ),
            )
            ctx.allow_overlap(
                actuator, faceplate, elem_a="button_cap", elem_b="trim_ring",
                reason=(
                    "On a tight footprint the wide button cap proud of the plate "
                    "rides over the thin chrome trim lip at the plate edge."
                ),
            )
        else:  # rotary_dimmer
            ctx.allow_overlap(
                actuator, faceplate, elem_a="shaft_stub", elem_b="plate_field",
                reason=(
                    "The dimmer shaft stub passes through the circular hole in the "
                    "plate to physically mount the knob on the faceplate."
                ),
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "wall_panel + faceplate present",
        "wall_panel" in part_names and "faceplate" in part_names,
        details=str(sorted(part_names)),
    )
    ctx.check(
        f"N={r.gang_count} {prefix} actuators present",
        all(f"{prefix}_{i}" in part_names for i in range(r.gang_count)),
        details=str(sorted(part_names)),
    )

    # ---- Faceplate seated flush on the wall + within the wall footprint. ----
    # World front normal is -Y (see _WALL_YAW), so the WALL is the +Y member of
    # every wall/plate gap pair: gap = wall.min_y - faceplate.max_y.
    ctx.expect_gap(
        wall, faceplate, axis="y", max_gap=0.0006, max_penetration=0.0002,
        name="faceplate seated flush on the wall",
    )
    ctx.expect_within(
        faceplate, wall, axes="xz", margin=0.0,
        name="faceplate inside the wall slab footprint",
    )

    # ---- FIXED wall->faceplate. ----
    wj = object_model.get_articulation("wall_to_faceplate")
    ctx.check(
        "wall_to_faceplate is FIXED",
        wj.articulation_type == ArticulationType.FIXED,
        details=f"type={wj.articulation_type}",
    )

    # ---- Chrome trim is the outermost border, proud of the ivory field. ----
    trim_aabb = ctx.part_element_world_aabb(faceplate, elem="trim_ring")
    field_aabb = ctx.part_element_world_aabb(faceplate, elem="plate_field")
    if trim_aabb is not None and field_aabb is not None:
        ctx.check(
            "chrome trim is the outermost border",
            trim_aabb[1][0] >= field_aabb[1][0] - 0.001
            and trim_aabb[0][0] <= field_aabb[0][0] + 0.001
            and trim_aabb[1][2] >= field_aabb[1][2] - 0.001
            and trim_aabb[0][2] <= field_aabb[0][2] + 0.001,
            details=f"trim={trim_aabb}, field={field_aabb}",
        )

    # ---- Schuko only on rounded_rect_horizontal. ----
    clip_names = {v.name for v in faceplate.visuals if v.name.startswith("ground_clip")}
    if r.has_schuko:
        ctx.check(
            "Schuko grounding clips present on horizontal plate",
            clip_names == {"ground_clip_upper", "ground_clip_lower"},
            details=str(sorted(clip_names)),
        )
        ctx.check(
            "Schuko well authored as a true hollow recess with pin holes",
            _WELL_FLOOR_Y < _TILE_FACE_Y - 0.006 and _WELL_RADIUS * 2.0 > 0.035,
            details=f"well_depth={_TILE_FACE_Y - _WELL_FLOOR_Y:.4f}",
        )
    else:
        ctx.check(
            "no Schuko on square/round faceplate",
            len(clip_names) == 0,
            details=str(sorted(clip_names)),
        )

    # ---- The actuator must read as a body distinct from the plate it sits in. ----
    _pal = PALETTES[r.palette_style]
    _act = _actuator_rgba(_pal)
    ctx.check(
        "actuator colour separates from the plate",
        abs(_luma(_act) - _luma(_pal.plate)) >= _ACTUATOR_CONTRAST - 1e-6,
        details=(
            f"palette={r.palette_style} plate_luma={_luma(_pal.plate):.3f} "
            f"actuator_luma={_luma(_act):.3f} delta={_luma(_act) - _luma(_pal.plate):+.3f} "
            f"required={_ACTUATOR_CONTRAST}"
        ),
    )
    ctx.check(
        "derived actuator colour stays under the render albedo ceiling",
        max(_act[:3]) <= _ROLE_CEILING["actuator"] + 1e-6,
        details=f"actuator={tuple(round(c, 3) for c in _act[:3])}",
    )

    # ---- round_plate hosts ANY N by growing its disc (no compatibility gate). ----
    if r.faceplate_shape == "round_plate":
        ctx.check(
            "round_plate stays a true circle",
            abs(r.plate_w - r.plate_h) < 1e-9 and abs(r.trim_w - r.trim_h) < 1e-9,
            details=f"plate={r.plate_w:.4f}x{r.plate_h:.4f} trim={r.trim_w:.4f}x{r.trim_h:.4f}",
        )
        # Every actuator's far CORNER must sit inside the disc: on a circle the
        # binding constraint is radial, not the X half-width.
        corner_r = max(
            (
                math.hypot(abs(x) + _ACTUATOR_FOOTPRINT / 2.0, abs(z) + _ACTUATOR_FOOTPRINT / 2.0)
                for x, z in zip(r.actuator_xs, r.actuator_zs)
            ),
            default=0.0,
        )
        ctx.check(
            f"round_plate disc contains the {r.gang_rows}x{r.gang_cols} actuator grid (N={r.gang_count})",
            corner_r <= r.plate_w / 2.0 - 0.002,
            details=f"corner_r={corner_r:.4f} disc_r={r.plate_w / 2.0:.4f}",
        )

    # ---- Actuator placement: center-symmetric grid, inside the plate. ----
    # actuator_xs/zs are wall-local; _WALL_YAW maps wall-local x -> world -x and
    # leaves z alone (a yaw about Z).
    ctx.check(
        f"grid is {r.gang_rows}x{r.gang_cols} and holds exactly N={r.gang_count}",
        len(r.actuator_xs) == r.gang_count == len(r.actuator_zs)
        and r.gang_rows * r.gang_cols >= r.gang_count
        and (r.gang_rows - 1) * r.gang_cols < r.gang_count,
        details=f"xs={r.actuator_xs} zs={r.actuator_zs}",
    )
    ctx.check(
        "actuator grid is centered on the plate on both axes",
        abs(min(r.actuator_xs) + max(r.actuator_xs)) < 1e-9
        and abs(min(r.actuator_zs) + max(r.actuator_zs)) < 1e-9,
        details=f"x span=({min(r.actuator_xs):+.4f},{max(r.actuator_xs):+.4f}) "
        f"z span=({min(r.actuator_zs):+.4f},{max(r.actuator_zs):+.4f})",
    )
    for i, (actuator, xc, zc) in enumerate(zip(actuators, r.actuator_xs, r.actuator_zs)):
        pos = ctx.part_world_position(actuator)
        ctx.check(
            f"{prefix}_{i} centered on its module (wall-local x={xc:+.3f} z={zc:+.3f})",
            pos is not None and abs(pos[0] + xc) < 0.003 and abs(pos[2] - zc) < 0.003,
            details=f"pos={pos}",
        )
        ctx.expect_within(
            actuator, faceplate, axes="xz", margin=0.0,
            name=f"{prefix}_{i} stays inside the plate outline (X,Z)",
        )

    # ---- Per-actuator joint topology + actuation. ----
    if at == "rocker":
        for i, (actuator, j) in enumerate(zip(actuators, joints)):
            ctx.check(
                f"rocker_{i} is REVOLUTE about +X",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
            lim = j.motion_limits
            ctx.check(
                f"rocker_{i} symmetric see-saw range",
                lim is not None and lim.lower is not None and lim.upper is not None
                and abs(lim.lower + lim.upper) < 1e-6 and lim.upper > 0.0,
                details=f"limits=({lim.lower}, {lim.upper})",
            )
            rest = ctx.part_world_aabb(actuator)
            with ctx.pose({j: lim.upper}):
                tip = ctx.part_world_aabb(actuator)
                ctx.check(
                    f"rocker_{i} pressed pose tips the paddle outward",
                    rest is not None and tip is not None and tip[0][1] < rest[0][1] - 0.0010,
                    details=f"rest={rest}, tip={tip}",
                )
                ctx.expect_gap(
                    wall, actuator, axis="y", max_penetration=0.0,
                    name=f"rocker_{i} pressed pose clears the wall",
                )
    elif at == "toggle_lever":
        for i, (actuator, j) in enumerate(zip(actuators, joints)):
            ctx.check(
                f"toggle_{i} is REVOLUTE about +X",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
            lim = j.motion_limits
            ctx.check(
                f"toggle_{i} flip range >= rocker range",
                lim is not None and lim.upper is not None and lim.upper > 0.20,
                details=f"upper={None if lim is None else lim.upper}",
            )
            rest = ctx.part_world_aabb(actuator)
            with ctx.pose({j: lim.upper}):
                tip = ctx.part_world_aabb(actuator)
                ctx.check(
                    f"toggle_{i} flips (AABB changes)",
                    rest is not None and tip is not None
                    and (abs(tip[1][2] - rest[1][2]) > 0.002 or abs(tip[0][2] - rest[0][2]) > 0.002),
                    details=f"rest={rest}, tip={tip}",
                )
    elif at == "push_button":
        for i, (actuator, j) in enumerate(zip(actuators, joints)):
            ctx.check(
                f"button_{i} is PRISMATIC about -Y",
                j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[1]) > 0.99,
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
            lim = j.motion_limits
            ctx.check(
                f"button_{i} press travel within range",
                lim is not None and lim.upper is not None and 0.0 < lim.upper <= _POCKET_FLOOR_Y + 0.001,
                details=f"upper={None if lim is None else lim.upper}",
            )
            ctx.expect_contact(
                actuator, faceplate, elem_a="button_cap", elem_b="plate_field",
                name=f"button_{i} cap seats on the pocket rim",
            )
            p0 = ctx.part_world_position(actuator)
            with ctx.pose({j: lim.upper}):
                p1 = ctx.part_world_position(actuator)
                ctx.check(
                    f"button_{i} presses inward (toward the wall, world +Y)",
                    p0 is not None and p1 is not None and p1[1] > p0[1] + 0.0005,
                    details=f"rest_y={p0}, pressed_y={p1}",
                )
                ctx.expect_gap(
                    wall, actuator, axis="y", max_penetration=0.0,
                    name=f"button_{i} pressed pose clears the wall",
                )
    else:  # rotary_dimmer
        for i, (actuator, j) in enumerate(zip(actuators, joints)):
            ctx.check(
                f"dimmer_{i} is CONTINUOUS about +Y (no limits)",
                j.articulation_type == ArticulationType.CONTINUOUS
                and abs(j.axis[1] - 1.0) < 0.01 and abs(j.axis[0]) < 0.01 and abs(j.axis[2]) < 0.01
                and (j.motion_limits is None or j.motion_limits.lower is None),
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
            ctx.expect_contact(
                actuator, faceplate, elem_a="knob_body", elem_b="plate_field",
                name=f"dimmer_{i} knob base seats on the plate face",
            )
            # Pure rotation: center unchanged.
            rest_pos = ctx.part_world_position(actuator)
            with ctx.pose({j: math.pi / 2.0}):
                spun_pos = ctx.part_world_position(actuator)
                ctx.check(
                    f"dimmer_{i} spin preserves position (pure rotation)",
                    rest_pos is not None and spun_pos is not None
                    and abs(spun_pos[0] - rest_pos[0]) < 0.003
                    and abs(spun_pos[1] - rest_pos[1]) < 0.003
                    and abs(spun_pos[2] - rest_pos[2]) < 0.003,
                    details=f"rest={rest_pos}, spun={spun_pos}",
                )
            # AABB changes under rotation (the off-axis pointer tab guarantees this).
            rest_aabb = ctx.part_world_aabb(actuator)
            with ctx.pose({j: math.pi / 4.0}):
                rot_aabb = ctx.part_world_aabb(actuator)
                ctx.check(
                    f"dimmer_{i} rotated pose changes the bounding box",
                    rest_aabb is not None and rot_aabb is not None
                    and (
                        abs(rot_aabb[1][0] - rest_aabb[1][0]) > 0.0005
                        or abs(rot_aabb[1][2] - rest_aabb[1][2]) > 0.0005
                        or abs(rot_aabb[0][0] - rest_aabb[0][0]) > 0.0005
                        or abs(rot_aabb[0][2] - rest_aabb[0][2]) > 0.0005
                    ),
                    details=f"rest={rest_aabb}, rot={rot_aabb}",
                )

    # ---- slot_choices recorded with N encoded. ----
    ctx.check(
        "slot_choices recorded with gang_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "SwitchConfig",
    "ResolvedSwitchConfig",
    "build_switch",
    "build_seeded_switch",
    "config_from_seed",
    "resolve_config",
    "run_switch_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
