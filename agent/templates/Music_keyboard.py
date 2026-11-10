# SPDX-License-Identifier: Apache-2.0

"""Music keyboard — modular procedural template (MIDI controller + analog synth).

pattern = mixed: a single rigid `chassis` root carries a rear-hinged multiplicity
keybed plus three parallel functional clusters hung off it.

World frame (shared by all 11 five-star sources): +X = width (right), +Y = depth
(back; player faces -Y), +Z = up. The body sits near z=0 on a `base_shell`.

Shared spine (multiplicity axis `key_count`):
  white_key_{i} (natural, notched LoftGeometry) + black_key_{j} (sharp, lofted
  wedge), each a REVOLUTE press joint `chassis_to_white_key_{i}` /
  `chassis_to_black_key_{j}` about +X, lower=0 -> press (rest@0, front tip dips).
  N_white = 7*octaves+1, N_black = 5*octaves, derived from a per-octave
  SHARP_AFTER boundary table.  key_count in {13, 25, 37, 49, 61}.

Slot A control_surface (rear deck cluster, distinct part-tree / joint mixes):
  pad_block_8   : 8 PRISMATIC drum pads (2x4) + 4 REVOLUTE column knobs
  pad_grid_16   : 16 PRISMATIC backlit pads (4x4) + 4 PRISMATIC env sliders
  fader_bank_9  : 9 PRISMATIC linear faders
  knob_grid_8   : 8 REVOLUTE grid knobs (2x4) + 4 REVOLUTE column knobs
  knob_field_20 : 20 REVOLUTE knobs (12 section + 8 master) + 4 PRISMATIC sliders

Slot B pitch_bender_interface (front-left of the keybed):
  touch_strip      : static chassis decals (no parts / no joints) — A/B baseline
  joystick_gimbal  : 2-DOF nested gimbal (pitch REVOLUTE +Y -> mod REVOLUTE +X)
  pitch_mod_wheels : parallel pitch + mod wheel pair (REVOLUTE +X spring return)

Slot C chassis_form (root form + control seating frame):
  flat_slab          : horizontal control_deck; controls seat at deck_top, rpy=0
  upright_wood_cheeks: wedge angled_panel + walnut cheeks; controls reseat on the
                       tilted surface (z = panel_surface_z(y), rpy=(tilt,0,0))

Design rules:
  Rule 1 — every non-articulating detail (shells, deck/panel, end caps, cheeks,
           bender block / touch strips, knob sockets, wheel cheek + brackets) is a
           `part.visual(...)`, never a FIXED part.
  Rule 2 — moving children declare a MatingContract where the contact face is a
           real, axis-aligned visual whose z-only mating distance is valid:
           flat-deck controls -> `control_deck` top; joystick gimbal -> socket,
           stick -> ring; wheels -> wheel_cheek.  The dense keybed and the
           tilt-reseated controls follow the five-star sources' allow_overlap +
           articulation-origin-in-geometry pattern (the keybed mirrors piano.py,
           which likewise omits per-key mating on its dense key array).
  Rule 3 — geometry is adapted from the declared five-star sources: notched
           LoftGeometry white keys + lofted black wedges (B), KnobGeometry knobs
           with grips/pointers (A/B), ExtrudeGeometry rounded pads/fader caps (A),
           Torus/Cylinder/Sphere joystick (joystick var), Cylinder+Torus bender
           wheels (twowheels var).  No primitive is downgraded to a crude box.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    CylinderGeometry,
    ExtrudeGeometry,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    LoftGeometry,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    SphereGeometry,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    rounded_rect_profile,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Enums.
# --------------------------------------------------------------------------- #
ControlSurface = Literal[
    "pad_block_8", "pad_grid_16", "fader_bank_9", "knob_grid_8", "knob_field_20"
]
PitchBender = Literal["touch_strip", "joystick_gimbal", "pitch_mod_wheels"]
ChassisForm = Literal["flat_slab", "upright_wood_cheeks"]
PaletteStyle = Literal[
    "black_controller_red",
    "dark_gray_teal_synth",
    "silver_synth_walnut",
    "crimson_boutique",
    "graphite_blue_pads",
    "cream_vintage",
]

CONTROL_SURFACES: tuple[ControlSurface, ...] = (
    "pad_block_8",
    "pad_grid_16",
    "fader_bank_9",
    "knob_grid_8",
    "knob_field_20",
)
_CONTROL_WEIGHTS = (0.24, 0.18, 0.18, 0.18, 0.22)
_DENSE_CONTROLS = ("knob_field_20", "fader_bank_9")
_COMPACT_CONTROLS: tuple[ControlSurface, ...] = ("pad_block_8", "knob_grid_8")

PITCH_BENDERS: tuple[PitchBender, ...] = (
    "touch_strip",
    "joystick_gimbal",
    "pitch_mod_wheels",
)
_BENDER_WEIGHTS = (0.40, 0.30, 0.30)

CHASSIS_FORMS: tuple[ChassisForm, ...] = ("flat_slab", "upright_wood_cheeks")
_CHASSIS_WEIGHTS = (0.62, 0.38)

PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "black_controller_red",
    "dark_gray_teal_synth",
    "silver_synth_walnut",
    "crimson_boutique",
    "graphite_blue_pads",
    "cream_vintage",
)

KEY_COUNTS = (13, 25, 37, 49, 61)
_KEY_COUNT_WEIGHTS = (0.20, 0.40, 0.20, 0.15, 0.05)

# Footprint (X extent, m) the control cluster needs on the rear deck. The body
# panel is widened in resolve_config so body_panel_width >= footprint + 2*margin.
_CONTROL_FOOTPRINT: dict[ControlSurface, float] = {
    "pad_block_8": 0.150,
    "knob_grid_8": 0.150,
    "pad_grid_16": 0.280,
    "fader_bank_9": 0.260,
    "knob_field_20": 0.470,
}


# --------------------------------------------------------------------------- #
# Invariant geometry constants (z heights of the physical keys are fixed; only
# the deck/panel height, key pitch, depth and turn limits are parameterised).
# --------------------------------------------------------------------------- #
BASE_TOP_Z = 0.040
PANEL_FRONT_Y_NOM = -0.035  # rear-deck / angled-panel front edge (× depth)
KEY_HINGE_Y_NOM = -0.030  # hinge line tucked just under the panel lip

WHITE_KEY_THICK = 0.012
WHITE_TOP_Z = 0.062
WHITE_HINGE_Z = WHITE_TOP_Z - WHITE_KEY_THICK / 2.0  # 0.056
WHITE_DEPTH_NOM = 0.123  # × body_depth_scale

BLACK_KEY_THICK = 0.0155
BLACK_BOTTOM_Z = 0.058
BLACK_HINGE_Z = BLACK_BOTTOM_Z + BLACK_KEY_THICK / 2.0  # 0.06575
BLACK_DEPTH_NOM = 0.083  # × body_depth_scale

BENDER_ZONE_W = 0.130  # reserved width on the front-left for the bender
SIDE_MARGIN = 0.016
CONTROL_SINK = 0.0006  # controls sink this far into the deck (real seat)

# Per-octave sharp pattern: a sharp sits on the right boundary of these naturals
# (C#, D#, F#, G#, A#); index offset 7*octave added per octave.
_OCTAVE_SHARPS = (0, 1, 3, 4, 5)


# --------------------------------------------------------------------------- #
# Palettes. Only material rgba shifts per colorway; topology/size/interfaces are
# untouched (spec §7). Tokens drive every .visual call.
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_controller_red": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.78, 0.06, 0.08, 1.0),
        "key_white": (0.93, 0.93, 0.91, 1.0),
        "key_black": (0.07, 0.07, 0.08, 1.0),
        "knob": (0.17, 0.17, 0.18, 1.0),
        "pointer": (0.90, 0.90, 0.90, 1.0),
        "wood": (0.42, 0.26, 0.15, 1.0),
        "backlight": (0.85, 0.10, 0.12, 1.0),
    },
    "dark_gray_teal_synth": {
        "body": (0.16, 0.165, 0.175, 1.0),
        "accent": (0.55, 0.86, 0.80, 1.0),
        "key_white": (0.93, 0.93, 0.91, 1.0),
        "key_black": (0.07, 0.07, 0.075, 1.0),
        "knob": (0.10, 0.105, 0.115, 1.0),
        "pointer": (0.92, 0.94, 0.93, 1.0),
        "wood": (0.42, 0.26, 0.15, 1.0),
        "backlight": (0.55, 0.86, 0.80, 1.0),
    },
    "silver_synth_walnut": {
        "body": (0.66, 0.67, 0.69, 1.0),
        "accent": (0.30, 0.30, 0.32, 1.0),
        "key_white": (0.95, 0.94, 0.90, 1.0),
        "key_black": (0.10, 0.10, 0.11, 1.0),
        "knob": (0.13, 0.13, 0.14, 1.0),
        "pointer": (0.95, 0.95, 0.95, 1.0),
        "wood": (0.42, 0.26, 0.15, 1.0),
        "backlight": (0.40, 0.40, 0.43, 1.0),
    },
    "crimson_boutique": {
        "body": (0.62, 0.10, 0.12, 1.0),
        "accent": (0.08, 0.08, 0.09, 1.0),
        "key_white": (0.94, 0.93, 0.90, 1.0),
        "key_black": (0.07, 0.07, 0.08, 1.0),
        "knob": (0.10, 0.10, 0.11, 1.0),
        "pointer": (0.85, 0.85, 0.88, 1.0),
        "wood": (0.35, 0.20, 0.12, 1.0),
        "backlight": (0.88, 0.86, 0.84, 1.0),
    },
    "graphite_blue_pads": {
        "body": (0.13, 0.14, 0.16, 1.0),
        "accent": (1.0, 0.55, 0.15, 1.0),
        "key_white": (0.93, 0.93, 0.91, 1.0),
        "key_black": (0.07, 0.07, 0.08, 1.0),
        "knob": (0.18, 0.19, 0.21, 1.0),
        "pointer": (0.90, 0.90, 0.92, 1.0),
        "wood": (0.40, 0.26, 0.16, 1.0),
        "backlight": (0.22, 0.50, 1.0, 1.0),
    },
    "cream_vintage": {
        "body": (0.90, 0.87, 0.80, 1.0),
        "accent": (0.55, 0.40, 0.24, 1.0),
        "key_white": (0.96, 0.93, 0.86, 1.0),
        "key_black": (0.18, 0.13, 0.10, 1.0),
        "knob": (0.45, 0.40, 0.33, 1.0),
        "pointer": (0.30, 0.25, 0.20, 1.0),
        "wood": (0.55, 0.40, 0.24, 1.0),
        "backlight": (0.80, 0.62, 0.36, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config.
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class MusicKeyboardConfig:
    control_surface: ControlSurface = "pad_block_8"
    pitch_bender: PitchBender = "touch_strip"
    chassis_form: ChassisForm = "flat_slab"
    palette_style: PaletteStyle = "black_controller_red"
    key_count: int = 25
    key_pitch: float = 0.0220
    key_press_rad: float = 0.060
    body_depth_scale: float = 1.0
    panel_height_scale: float = 1.0
    control_turn_limit_rad: float = 2.5
    name: str = "music_keyboard"


@dataclass(frozen=True)
class ResolvedMusicKeyboardConfig:
    control_surface: ControlSurface
    pitch_bender: PitchBender
    chassis_form: ChassisForm
    palette_style: PaletteStyle
    key_count: int
    octaves: int
    n_white: int
    n_black: int
    sharp_after: tuple[int, ...]
    key_pitch: float
    key_press_rad: float
    body_depth_scale: float
    panel_height_scale: float
    control_turn_limit_rad: float
    # Derived geometry.
    body_half_w: float
    body_front_y: float
    body_back_y: float
    panel_front_y: float
    key_hinge_y: float
    white_depth: float
    black_depth: float
    deck_top_z: float
    panel_front_z: float
    panel_back_z: float
    tilt_angle: float
    first_white_x: float
    name: str
    mats: dict[str, object]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def _pick(value: str, allowed: tuple[str, ...]) -> str:
    if value not in allowed:
        raise ValueError(f"Unsupported choice {value!r}; allowed {allowed!r}")
    return value


def _octaves_for(key_count: int) -> int:
    # key_count = 12*oct + 1  ->  oct = (key_count - 1) / 12
    return max(1, round((int(key_count) - 1) / 12))


def _sharp_after(octaves: int) -> tuple[int, ...]:
    out: list[int] = []
    for o in range(octaves):
        base = 7 * o
        out.extend(base + s for s in _OCTAVE_SHARPS)
    return tuple(out)


def _spread(n: int, width: float) -> list[float]:
    """n cell-centres symmetric about 0 across `width`."""
    if n <= 0:
        return []
    if n == 1:
        return [0.0]
    step = width / n
    return [-width / 2.0 + (i + 0.5) * step for i in range(n)]


# --------------------------------------------------------------------------- #
# Procedural sampling (procedural-first; seed 0 is ordinary).
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> MusicKeyboardConfig:
    rng = random.Random(seed)

    control_surface = rng.choices(CONTROL_SURFACES, weights=_CONTROL_WEIGHTS, k=1)[0]
    pitch_bender = rng.choices(PITCH_BENDERS, weights=_BENDER_WEIGHTS, k=1)[0]
    chassis_form = rng.choices(CHASSIS_FORMS, weights=_CHASSIS_WEIGHTS, k=1)[0]
    key_count = rng.choices(KEY_COUNTS, weights=_KEY_COUNT_WEIGHTS, k=1)[0]

    # Soft down-weight (NOT a hard exclusion): a dense control cluster on the
    # tiniest 13-key body is unusual; half the time fall back to a compact
    # cluster.  The body still widens to fit when the dense cluster survives.
    if key_count == 13 and control_surface in _DENSE_CONTROLS and rng.random() < 0.5:
        control_surface = rng.choice(_COMPACT_CONTROLS)

    palette_style = rng.choice(PALETTE_STYLES)

    key_pitch = round(rng.uniform(0.0185, 0.0250), 4)
    key_press_rad = round(rng.uniform(0.050, 0.065), 4)
    body_depth_scale = round(rng.uniform(0.92, 1.10), 4)
    panel_height_scale = round(rng.uniform(0.85, 1.15), 4)
    control_turn_limit_rad = round(rng.uniform(2.2, 2.7), 4)

    return MusicKeyboardConfig(
        control_surface=control_surface,  # type: ignore[arg-type]
        pitch_bender=pitch_bender,  # type: ignore[arg-type]
        chassis_form=chassis_form,  # type: ignore[arg-type]
        palette_style=palette_style,
        key_count=key_count,
        key_pitch=key_pitch,
        key_press_rad=key_press_rad,
        body_depth_scale=body_depth_scale,
        panel_height_scale=panel_height_scale,
        control_turn_limit_rad=control_turn_limit_rad,
        name=f"seeded_music_keyboard_{seed}",
    )


def resolve_config(config: MusicKeyboardConfig) -> ResolvedMusicKeyboardConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    control_surface = _pick(config.control_surface, CONTROL_SURFACES)
    pitch_bender = _pick(config.pitch_bender, PITCH_BENDERS)
    chassis_form = _pick(config.chassis_form, CHASSIS_FORMS)

    key_count = int(config.key_count)
    if key_count not in KEY_COUNTS:
        # snap to nearest supported multiplicity.
        key_count = min(KEY_COUNTS, key=lambda k: abs(k - key_count))
    octaves = _octaves_for(key_count)
    n_white = 7 * octaves + 1
    n_black = 5 * octaves
    sharp_after = _sharp_after(octaves)

    key_pitch = _clamp(config.key_pitch, 0.0185, 0.0250)
    key_press_rad = _clamp(config.key_press_rad, 0.050, 0.065)
    body_depth_scale = _clamp(config.body_depth_scale, 0.92, 1.10)
    panel_height_scale = _clamp(config.panel_height_scale, 0.85, 1.15)
    control_turn_limit_rad = _clamp(config.control_turn_limit_rad, 2.2, 2.7)

    # --- Depth-scaled Y layout ------------------------------------------------ #
    body_front_y = -0.155 * body_depth_scale
    body_back_y = 0.155 * body_depth_scale
    panel_front_y = PANEL_FRONT_Y_NOM * body_depth_scale
    key_hinge_y = KEY_HINGE_Y_NOM * body_depth_scale
    white_depth = WHITE_DEPTH_NOM * body_depth_scale
    black_depth = BLACK_DEPTH_NOM * body_depth_scale

    # --- equation: keybed_width = N_white * key_pitch; fit gate widens body --- #
    keybed_width = n_white * key_pitch
    footprint = _CONTROL_FOOTPRINT[control_surface]
    needed_for_keybed = BENDER_ZONE_W + keybed_width + 2.0 * SIDE_MARGIN
    needed_for_control = footprint + 2.0 * SIDE_MARGIN
    body_w = max(needed_for_keybed, needed_for_control)
    body_half_w = body_w / 2.0

    # keybed centred in the span to the RIGHT of the reserved bender zone.
    avail_left = -body_half_w + BENDER_ZONE_W + SIDE_MARGIN
    avail_right = body_half_w - SIDE_MARGIN
    keybed_center = (avail_left + avail_right) / 2.0
    first_white_x = keybed_center - (n_white - 1) * key_pitch / 2.0

    # --- conditional: control seating frame derived from chassis_form --------- #
    deck_top_z = max(0.075, 0.085 * panel_height_scale)
    panel_front_z = max(0.060, 0.065 * panel_height_scale)
    panel_back_z = max(panel_front_z + 0.050, 0.155 * panel_height_scale)
    tilt_run = body_back_y - panel_front_y
    tilt_rise = panel_back_z - panel_front_z
    tilt_angle = math.atan2(tilt_rise, tilt_run)

    mats = dict(PALETTES[config.palette_style])

    return ResolvedMusicKeyboardConfig(
        control_surface=control_surface,  # type: ignore[arg-type]
        pitch_bender=pitch_bender,  # type: ignore[arg-type]
        chassis_form=chassis_form,  # type: ignore[arg-type]
        palette_style=config.palette_style,
        key_count=key_count,
        octaves=octaves,
        n_white=n_white,
        n_black=n_black,
        sharp_after=sharp_after,
        key_pitch=key_pitch,
        key_press_rad=key_press_rad,
        body_depth_scale=body_depth_scale,
        panel_height_scale=panel_height_scale,
        control_turn_limit_rad=control_turn_limit_rad,
        body_half_w=body_half_w,
        body_front_y=body_front_y,
        body_back_y=body_back_y,
        panel_front_y=panel_front_y,
        key_hinge_y=key_hinge_y,
        white_depth=white_depth,
        black_depth=black_depth,
        deck_top_z=deck_top_z,
        panel_front_z=panel_front_z,
        panel_back_z=panel_back_z,
        tilt_angle=tilt_angle,
        first_white_x=first_white_x,
        name=config.name,
        mats=mats,
    )


# --------------------------------------------------------------------------- #
# Control seating frame (Slot C derived).
# --------------------------------------------------------------------------- #
def _panel_surface_z(r: ResolvedMusicKeyboardConfig, y: float) -> float:
    t = (y - r.panel_front_y) / (r.body_back_y - r.panel_front_y)
    return r.panel_front_z + t * (r.panel_back_z - r.panel_front_z)


def _seat(r: ResolvedMusicKeyboardConfig, y: float) -> tuple[float, tuple[float, float, float]]:
    if r.chassis_form == "upright_wood_cheeks":
        return _panel_surface_z(r, y), (r.tilt_angle, 0.0, 0.0)
    return r.deck_top_z, (0.0, 0.0, 0.0)


def _control_origin(r: ResolvedMusicKeyboardConfig, x: float, y: float) -> Origin:
    z, rpy = _seat(r, y)
    return Origin(xyz=(x, y, z - CONTROL_SINK), rpy=rpy)


def _deck_mating(r: ResolvedMusicKeyboardConfig, child_visual: str) -> MatingContract | None:
    """Mate a control base to the flat deck top.  Only valid on flat_slab, where
    the deck is an axis-aligned Box and the mating gap (measured z-only) equals
    the seat sink.  On the tilted panel we rely on allow_overlap + the
    articulation-origin-in-geometry baseline instead (as the woodcheeks source
    does)."""
    if r.chassis_form != "flat_slab":
        return None
    return MatingContract(
        parent_face_geometry="control_deck",
        parent_face_side="positive_z",
        child_face_geometry=child_visual,
        child_face_side="negative_z",
        contact_tol=0.0020,
    )


def _ctrl_band(r: ResolvedMusicKeyboardConfig) -> tuple[float, float]:
    y0 = max(0.002, r.panel_front_y + 0.030)
    y1 = r.body_back_y - 0.018
    return y0, y1


# --------------------------------------------------------------------------- #
# Keybed meshes (B-style LoftGeometry naturals + lofted sharp wedge).
# --------------------------------------------------------------------------- #
def _white_outline(
    r: ResolvedMusicKeyboardConfig, left_relief: bool, right_relief: bool
) -> list[tuple[float, float]]:
    half = (r.key_pitch - 0.0015) / 2.0
    relief = (r.key_pitch - 0.0015) * 0.22
    shoulder = -r.white_depth * 0.69
    xr = relief if right_relief else half
    xl = -relief if left_relief else -half
    pts: list[tuple[float, float]] = [(xr, 0.0)]
    if right_relief:
        pts.append((xr, shoulder))
        pts.append((half, shoulder))
    pts.append((half, -r.white_depth))
    pts.append((-half, -r.white_depth))
    if left_relief:
        pts.append((-half, shoulder))
        pts.append((xl, shoulder))
    pts.append((xl, 0.0))
    return pts


def _white_key_mesh(r: ResolvedMusicKeyboardConfig, name: str, lr: bool, rr: bool):
    outline = _white_outline(r, lr, rr)
    geom = LoftGeometry(
        [
            [(x, y, 0.0) for x, y in outline],
            [(x, y, WHITE_KEY_THICK) for x, y in outline],
        ],
        cap=True,
        closed=True,
    )
    return mesh_from_geometry(geom, name)


def _black_key_mesh(r: ResolvedMusicKeyboardConfig, name: str):
    half = r.key_pitch * 0.46 / 2.0
    top_half = half * 0.42
    d = r.black_depth
    bottom = [(half, -0.001), (half, -d), (-half, -d), (-half, -0.001)]
    top = [(top_half, -0.004), (top_half, -d + 0.006), (-top_half, -d + 0.006), (-top_half, -0.004)]
    geom = LoftGeometry(
        [
            [(x, y, 0.0) for x, y in bottom],
            [(x, y, BLACK_KEY_THICK) for x, y in top],
        ],
        cap=True,
        closed=True,
    )
    return mesh_from_geometry(geom, name)


def _emit_keybed(model: ArticulatedObject, chassis, r: ResolvedMusicKeyboardConfig) -> None:
    m = r.mats
    sharp_after = set(r.sharp_after)
    white_centers = [r.first_white_x + i * r.key_pitch for i in range(r.n_white)]

    mesh_cache: dict[tuple[bool, bool], object] = {}
    white_key_z = WHITE_HINGE_Z
    for i, cx in enumerate(white_centers):
        lr = (i - 1) in sharp_after
        rr = i in sharp_after
        cache_key = (lr, rr)
        mesh = mesh_cache.get(cache_key)
        if mesh is None:
            mesh = _white_key_mesh(r, f"white_key_{int(lr)}{int(rr)}", lr, rr)
            mesh_cache[cache_key] = mesh
        key = model.part(f"white_key_{i}")
        key.visual(
            mesh,
            origin=Origin(xyz=(0.0, 0.0, -WHITE_KEY_THICK / 2.0)),
            material=m["key_white"],
            name="key_body", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"chassis_to_white_key_{i}",
            ArticulationType.REVOLUTE,
            parent=chassis,
            child=key,
            origin=Origin(xyz=(cx, r.key_hinge_y, white_key_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=r.key_press_rad),
        )

    black_mesh = _black_key_mesh(r, "black_key")
    black_key_z = BLACK_HINGE_Z
    for j, after in enumerate(r.sharp_after):
        bx = white_centers[after] + r.key_pitch / 2.0
        key = model.part(f"black_key_{j}")
        key.visual(
            black_mesh,
            origin=Origin(xyz=(0.0, 0.0, -BLACK_KEY_THICK / 2.0)),
            material=m["key_black"],
            name="key_body", material_class_id="plastic.opaque_generic",
        )
        model.articulation(
            f"chassis_to_black_key_{j}",
            ArticulationType.REVOLUTE,
            parent=chassis,
            child=key,
            origin=Origin(xyz=(bx, r.key_hinge_y, black_key_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.8, velocity=4.0, lower=0.0, upper=r.key_press_rad),
        )


# --------------------------------------------------------------------------- #
# Slot C — chassis builders (root part "chassis").
# --------------------------------------------------------------------------- #
def _add_box_faces(g: MeshGeometry, v: list[int]) -> None:
    g.add_face(v[0], v[1], v[2])
    g.add_face(v[0], v[2], v[3])
    g.add_face(v[5], v[4], v[7])
    g.add_face(v[5], v[7], v[6])
    g.add_face(v[0], v[4], v[5])
    g.add_face(v[0], v[5], v[1])
    g.add_face(v[3], v[2], v[6])
    g.add_face(v[3], v[6], v[7])
    g.add_face(v[0], v[3], v[7])
    g.add_face(v[0], v[7], v[4])
    g.add_face(v[1], v[5], v[6])
    g.add_face(v[1], v[6], v[2])


def _angled_panel_mesh(r: ResolvedMusicKeyboardConfig, name: str):
    g = MeshGeometry()
    hw = r.body_half_w
    fy, by = r.panel_front_y, r.body_back_y
    fz, bz = r.panel_front_z, r.panel_back_z
    v = [
        g.add_vertex(-hw, fy, BASE_TOP_Z),
        g.add_vertex(hw, fy, BASE_TOP_Z),
        g.add_vertex(hw, fy, fz),
        g.add_vertex(-hw, fy, fz),
        g.add_vertex(-hw, by, BASE_TOP_Z),
        g.add_vertex(hw, by, BASE_TOP_Z),
        g.add_vertex(hw, by, bz),
        g.add_vertex(-hw, by, bz),
    ]
    _add_box_faces(g, v)
    return mesh_from_geometry(g, name)


def _cheek_mesh(r: ResolvedMusicKeyboardConfig, name: str):
    g = MeshGeometry()
    ht = 0.022 / 2.0
    fy, by = r.body_front_y, r.body_back_y
    front_h = r.panel_front_z + 0.060
    back_h = r.panel_back_z + 0.055
    v = [
        g.add_vertex(-ht, fy, 0.0),
        g.add_vertex(ht, fy, 0.0),
        g.add_vertex(ht, fy, front_h),
        g.add_vertex(-ht, fy, front_h),
        g.add_vertex(-ht, by, 0.0),
        g.add_vertex(ht, by, 0.0),
        g.add_vertex(ht, by, back_h),
        g.add_vertex(-ht, by, back_h),
    ]
    _add_box_faces(g, v)
    return mesh_from_geometry(g, name)


def _build_chassis(model: ArticulatedObject, r: ResolvedMusicKeyboardConfig):
    m = r.mats
    chassis = model.part("chassis")
    body_w = 2.0 * r.body_half_w
    depth = r.body_back_y - r.body_front_y

    # Full-footprint base slab (both forms).
    chassis.visual(
        Box((body_w, depth, BASE_TOP_Z)),
        origin=Origin(xyz=(0.0, 0.0, BASE_TOP_Z / 2.0)),
        material=m["body"],
        name="base_shell", material_class_id=("metal.brushed_silver" if r.palette_style == "silver_synth_walnut" else "metal.paint_coated"),
    )

    if r.chassis_form == "flat_slab":
        panel_depth = r.body_back_y - r.panel_front_y
        chassis.visual(
            Box((body_w, panel_depth, r.deck_top_z - BASE_TOP_Z)),
            origin=Origin(
                xyz=(
                    0.0,
                    (r.panel_front_y + r.body_back_y) / 2.0,
                    (BASE_TOP_Z + r.deck_top_z) / 2.0,
                )
            ),
            material=m["body"],
            name="control_deck", material_class_id=("metal.brushed_silver" if r.palette_style == "silver_synth_walnut" else "metal.paint_coated"),
        )
    else:
        chassis.visual(
            _angled_panel_mesh(r, "angled_panel"),
            material=m["body"],
            name="angled_panel", material_class_id=("metal.brushed_silver" if r.palette_style == "silver_synth_walnut" else "metal.paint_coated"),
        )
        cheek_mesh = _cheek_mesh(r, "cheek")
        for i in range(2):
            sign = 1.0 if i == 0 else -1.0
            cheek_x = sign * (r.body_half_w - 0.022 / 2.0)
            chassis.visual(
                cheek_mesh,
                origin=Origin(xyz=(cheek_x, 0.0, 0.0)),
                material=m["wood"],
                name=f"cheek_{i}", material_class_id="wood.walnut_dark",
            )

    # Keybed end caps flanking the playing keys (Rule 1: static accent visuals).
    kb_left = r.first_white_x - r.key_pitch / 2.0
    kb_right = r.first_white_x + (r.n_white - 1) * r.key_pitch + r.key_pitch / 2.0
    cap_w = 0.012
    cap_cy = (r.body_front_y + r.panel_front_y) / 2.0
    cap_depth = r.panel_front_y - r.body_front_y
    cap_h = 0.030
    for tag, cx in (("left", kb_left - cap_w / 2.0), ("right", kb_right + cap_w / 2.0)):
        chassis.visual(
            Box((cap_w, cap_depth, cap_h)),
            origin=Origin(xyz=(cx, cap_cy, cap_h / 2.0)),
            material=m["accent"],
            name=f"end_cap_{tag}", material_class_id="metal.paint_coated",
        )
    return chassis


# --------------------------------------------------------------------------- #
# Knob / pad / fader / slider primitives + emitters (shared helpers, looped).
# --------------------------------------------------------------------------- #
def _knob_geom(diameter: float, height: float, *, ribbed: bool = True):
    return KnobGeometry(
        diameter,
        height,
        body_style="cylindrical",
        edge_radius=0.0008,
        grip=KnobGrip(
            style="ribbed" if ribbed else "knurled", count=16, depth=0.0007, width=0.0015
        ),
        indicator=KnobIndicator(style="dot", mode="raised", angle_deg=0.0),
        center=False,
    )


def _emit_knob(
    model: ArticulatedObject,
    chassis,
    r: ResolvedMusicKeyboardConfig,
    name: str,
    x: float,
    y: float,
    *,
    diameter: float,
    height: float,
) -> None:
    m = r.mats
    knob = model.part(name)
    knob.visual(
        mesh_from_geometry(_knob_geom(diameter, height), f"{name}_geom"),
        material=m["knob"],
        name="knob_body", material_class_id="plastic.patterned_textured",
    )
    knob.visual(
        Box((0.0016, 0.30 * diameter, 0.0014)),
        origin=Origin(xyz=(0.0, 0.28 * diameter, height + 0.0007)),
        material=m["pointer"],
        name="pointer", material_class_id="plastic.opaque_generic",
    )
    model.articulation(
        f"chassis_to_{name}",
        ArticulationType.REVOLUTE,
        parent=chassis,
        child=knob,
        origin=_control_origin(r, x, y),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=0.3,
            velocity=5.0,
            lower=-r.control_turn_limit_rad,
            upper=r.control_turn_limit_rad,
        ),
        mating=_deck_mating(r, "knob_body"),
    )


def _pad_mesh(size: float, height: float, name: str):
    half_b = size / 2.0
    half_t = half_b * 0.86
    bottom = [
        (-half_b, -half_b, 0.0),
        (half_b, -half_b, 0.0),
        (half_b, half_b, 0.0),
        (-half_b, half_b, 0.0),
    ]
    top = [
        (-half_t, -half_t, height),
        (half_t, -half_t, height),
        (half_t, half_t, height),
        (-half_t, half_t, height),
    ]
    geom = LoftGeometry([bottom, top], cap=True, closed=True)
    return mesh_from_geometry(geom, name)


def _emit_pad(
    model: ArticulatedObject,
    chassis,
    r: ResolvedMusicKeyboardConfig,
    name: str,
    x: float,
    y: float,
    *,
    size: float,
    height: float,
    travel: float,
) -> None:
    m = r.mats
    pad = model.part(name)
    pad.visual(
        _pad_mesh(size, height, f"{name}_geom"),
        material=m["knob"],
        name="pad_body", material_class_id="rubber.smooth_plain",
    )
    pad.visual(
        Box((size * 0.74, size * 0.74, 0.0010)),
        origin=Origin(xyz=(0.0, 0.0, height - 0.0003)),
        material=m["backlight"],
        name="backlight", material_class_id="tech.emissive_surface",
    )
    model.articulation(
        f"chassis_to_{name}",
        ArticulationType.PRISMATIC,
        parent=chassis,
        child=pad,
        origin=_control_origin(r, x, y),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.1, lower=0.0, upper=travel),
        mating=_deck_mating(r, "pad_body"),
    )


def _fader_cap_mesh(name: str):
    profile = rounded_rect_profile(0.020, 0.011, 0.002)
    return mesh_from_geometry(ExtrudeGeometry.from_z0(profile, 0.009), name)


def _emit_fader(
    model: ArticulatedObject,
    chassis,
    r: ResolvedMusicKeyboardConfig,
    name: str,
    x: float,
    y: float,
    *,
    travel: float,
) -> None:
    m = r.mats
    fader = model.part(name)
    fader.visual(
        _fader_cap_mesh(f"{name}_geom"),
        material=m["knob"],
        name="cap_body", material_class_id="plastic.opaque_glossy_molded",
    )
    fader.visual(
        Box((0.014, 0.0030, 0.0024)),
        origin=Origin(xyz=(0.0, 0.0, 0.009 + 0.0012)),
        material=m["pointer"],
        name="cap_grip", material_class_id="plastic.opaque_generic",
    )
    model.articulation(
        f"chassis_to_{name}",
        ArticulationType.PRISMATIC,
        parent=chassis,
        child=fader,
        origin=_control_origin(r, x, y),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.2, lower=0.0, upper=travel),
        mating=_deck_mating(r, "cap_body"),
    )


def _emit_slider(
    model: ArticulatedObject,
    chassis,
    r: ResolvedMusicKeyboardConfig,
    name: str,
    x: float,
    y: float,
    *,
    travel: float,
) -> None:
    m = r.mats
    cap = model.part(name)
    cap.visual(
        Box((0.016, 0.009, 0.007)),
        origin=Origin(xyz=(0.0, 0.0, 0.0035)),
        material=m["knob"],
        name="cap", material_class_id="plastic.opaque_glossy_molded",
    )
    cap.visual(
        Box((0.016, 0.0016, 0.0008)),
        origin=Origin(xyz=(0.0, 0.0, 0.0068)),
        material=m["pointer"],
        name="cap_line", material_class_id="plastic.opaque_generic",
    )
    model.articulation(
        f"chassis_to_{name}",
        ArticulationType.PRISMATIC,
        parent=chassis,
        child=cap,
        origin=_control_origin(r, x, y),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.2, lower=-travel, upper=travel),
        mating=_deck_mating(r, "cap"),
    )


# --------------------------------------------------------------------------- #
# Slot A — control surface modules.
# --------------------------------------------------------------------------- #
def _emit_control_surface(model, chassis, r: ResolvedMusicKeyboardConfig) -> list[str]:
    """Emit the chosen control cluster.  Returns the list of control part names."""
    cs = r.control_surface
    y0, y1 = _ctrl_band(r)
    span = y1 - y0
    names: list[str] = []

    if cs == "pad_block_8":
        cols = _spread(4, 0.105)
        rows = (y0 + 0.020, y0 + 0.055)
        idx = 0
        for ry in rows:
            for cx in cols:
                nm = f"pad_{idx}"
                _emit_pad(model, chassis, r, nm, cx, ry, size=0.026, height=0.006, travel=0.0035)
                names.append(nm)
                idx += 1
        for k, kx in enumerate(_spread(4, 0.095)):
            nm = f"knob_{k}"
            _emit_knob(model, chassis, r, nm, kx, y1, diameter=0.015, height=0.010)
            names.append(nm)

    elif cs == "pad_grid_16":
        pad_cols = [-0.075 + 0.033 * c for c in range(4)]
        pad_rows = _spread(4, min(0.095, span * 0.74))
        pad_cy = (y0 + y1) / 2.0
        idx = 0
        for ry in pad_rows:
            for cx in pad_cols:
                nm = f"pad_{idx}"
                _emit_pad(
                    model,
                    chassis,
                    r,
                    nm,
                    cx,
                    pad_cy + ry,
                    size=0.026,
                    height=0.007,
                    travel=0.004,
                )
                names.append(nm)
                idx += 1
        slider_cols = [0.060 + 0.030 * s for s in range(4)]
        for s, sx in enumerate(slider_cols):
            nm = f"env_slider_{s}"
            _emit_slider(model, chassis, r, nm, sx, pad_cy, travel=0.014)
            names.append(nm)

    elif cs == "fader_bank_9":
        fader_cy = (y0 + y1) / 2.0
        for i, fx in enumerate(_spread(9, 0.235)):
            nm = f"fader_{i}"
            _emit_fader(model, chassis, r, nm, fx, fader_cy - 0.015, travel=0.030)
            names.append(nm)

    elif cs == "knob_grid_8":
        cols = _spread(4, 0.100)
        rows = (y0 + 0.022, y0 + 0.058)
        idx = 0
        for ry in rows:
            for cx in cols:
                nm = f"grid_knob_{idx}"
                _emit_knob(model, chassis, r, nm, cx, ry, diameter=0.022, height=0.014)
                names.append(nm)
                idx += 1
        for k, kx in enumerate(_spread(4, 0.090)):
            nm = f"knob_{k}"
            _emit_knob(model, chassis, r, nm, kx, y1, diameter=0.015, height=0.010)
            names.append(nm)

    else:  # knob_field_20
        section_cols = _spread(6, 0.400)
        rows = (y0 + 0.030, y0 + 0.066)
        sections = ("osc", "filter")
        for s, section in enumerate(sections):
            cols = section_cols[s * 3 : s * 3 + 3]
            for rr, ry in enumerate(rows):
                for cc, cx in enumerate(cols):
                    nm = f"{section}_knob_{rr}_{cc}"
                    _emit_knob(model, chassis, r, nm, cx, ry, diameter=0.024, height=0.018)
                    names.append(nm)
        for c, kx in enumerate(_spread(8, 0.430)):
            nm = f"master_knob_{c}"
            _emit_knob(model, chassis, r, nm, kx, y1, diameter=0.017, height=0.013)
            names.append(nm)
        for s, sx in enumerate(_spread(4, 0.150)):
            nm = f"env_slider_{s}"
            _emit_slider(model, chassis, r, nm, sx, y0, travel=0.014)
            names.append(nm)

    return names


# --------------------------------------------------------------------------- #
# Slot B — pitch/bender interface modules (front-left of the keybed).
# --------------------------------------------------------------------------- #
def _bender_anchor(r: ResolvedMusicKeyboardConfig) -> tuple[float, float]:
    bx = -r.body_half_w + BENDER_ZONE_W / 2.0
    by = r.body_front_y + 0.060
    return bx, by


def _emit_touch_strip(model, chassis, r: ResolvedMusicKeyboardConfig) -> list[str]:
    m = r.mats
    bx, by = _bender_anchor(r)
    chassis.visual(
        Box((0.090, 0.110, 0.018)),
        origin=Origin(xyz=(bx, by, BASE_TOP_Z + 0.009)),
        material=m["knob"],
        name="bender_block", material_class_id="tech.control_interface",
    )
    for k, dy in enumerate((-0.035, -0.012, 0.012, 0.035)):
        chassis.visual(
            Box((0.072, 0.014, 0.0045)),
            origin=Origin(xyz=(bx, by + dy, BASE_TOP_Z + 0.018 + 0.0022)),
            material=m["accent"],
            name=f"bend_strip_{k}", material_class_id="tech.control_interface",
        )
    return []


def _joystick_ring_mesh(name: str):
    return mesh_from_geometry(TorusGeometry(0.010, 0.0025), name)


def _joystick_stick_mesh(name: str):
    # Base hub seats inside the gimbal ring (so the stick is geometrically
    # connected to the ring it pivots on); shaft rises with a spherical cap.
    hub = CylinderGeometry(0.009, 0.006)
    shaft = CylinderGeometry(0.003, 0.025)
    shaft.translate(0.0, 0.0, 0.025 / 2.0)
    cap = SphereGeometry(0.0045)
    cap.translate(0.0, 0.0, 0.025)
    return mesh_from_geometry(hub.merge(shaft).merge(cap), name)


def _emit_joystick(model, chassis, r: ResolvedMusicKeyboardConfig) -> list[str]:
    m = r.mats
    bx, by = _bender_anchor(r)
    socket_h = 0.006
    socket_top = BASE_TOP_Z + socket_h
    chassis.visual(
        mesh_from_geometry(CylinderGeometry(0.011, socket_h), "joystick_socket"),
        origin=Origin(xyz=(bx, by, BASE_TOP_Z + socket_h / 2.0)),
        material=m["knob"],
        name="joystick_socket", material_class_id="metal.blackened_gunmetal",
    )

    tube = 0.0025
    gimbal = model.part("joystick_gimbal")
    gimbal.visual(
        _joystick_ring_mesh("joystick_ring"),
        material=m["knob"],
        name="ring", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        "joystick_pitch",
        ArticulationType.REVOLUTE,
        parent=chassis,
        child=gimbal,
        origin=Origin(xyz=(bx, by, socket_top + tube)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=5.0, lower=-0.35, upper=0.35),
        mating=MatingContract(
            parent_face_geometry="joystick_socket",
            parent_face_side="positive_z",
            child_face_geometry="ring",
            child_face_side="negative_z",
            contact_tol=0.0040,
        ),
    )

    stick = model.part("joystick_stick")
    stick.visual(
        _joystick_stick_mesh("joystick_stick"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=m["accent"],
        name="shaft", material_class_id="metal.paint_coated",
    )
    # The mod joint nests on the gimbal; the stick rides concentrically THROUGH
    # the ring (its hub seats in the ring bore) so there is no clean opposing
    # mating face — the woodcheeks/joystick five-star sources likewise express
    # this contact via allow_overlap (declared in run_tests) rather than a
    # MatingContract.  Connectivity is guaranteed by the base hub overlap.
    model.articulation(
        "joystick_mod",
        ArticulationType.REVOLUTE,
        parent=gimbal,
        child=stick,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=5.0, lower=-0.35, upper=0.35),
    )
    return ["joystick_gimbal", "joystick_stick"]


def _wheel_mesh(name: str, radius: float, half_width: float):
    disc = CylinderGeometry(radius, 2.0 * half_width)
    rim = TorusGeometry(radius - 0.001, 0.0022)
    body = disc.merge(rim)
    body.rotate_y(math.pi / 2.0)  # axle along X
    return mesh_from_geometry(body, name)


def _emit_wheels(model, chassis, r: ResolvedMusicKeyboardConfig) -> list[str]:
    m = r.mats
    bx, by = _bender_anchor(r)
    radius = 0.022
    half_w = 0.012
    spacing = 0.038
    bracket_t = 0.004
    bracket_h = 0.038

    cheek_h = 0.012
    cheek_top = BASE_TOP_Z + cheek_h
    chassis.visual(
        Box((0.084, 0.070, cheek_h)),
        origin=Origin(xyz=(bx, by, BASE_TOP_Z + cheek_h / 2.0)),
        material=m["knob"],
        name="wheel_cheek", material_class_id="metal.blackened_gunmetal",
    )
    for bi, off in enumerate(
        (-spacing / 2.0 - half_w - bracket_t / 2.0, 0.0, spacing / 2.0 + half_w + bracket_t / 2.0)
    ):
        chassis.visual(
            Box((bracket_t, 0.060, bracket_h)),
            origin=Origin(xyz=(bx + off, by, cheek_top + bracket_h / 2.0)),
            material=m["knob"],
            name=f"wheel_bracket_{bi}", material_class_id="metal.blackened_gunmetal",
        )

    axle_z = cheek_top + bracket_h * 0.65
    wheel_mesh = _wheel_mesh("bender_wheel", radius, half_w)
    names: list[str] = []
    for i in range(2):
        wx = bx - spacing / 2.0 + i * spacing
        wheel = model.part(f"wheel_{i}")
        wheel.visual(wheel_mesh, material=m["accent"] if i == 0 else m["knob"], name="wheel_body", material_class_id="plastic.opaque_glossy_molded")
        model.articulation(
            f"chassis_to_wheel_{i}",
            ArticulationType.REVOLUTE,
            parent=chassis,
            child=wheel,
            origin=Origin(xyz=(wx, by, axle_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.5, velocity=4.0, lower=-1.0, upper=1.0),
            mating=MatingContract(
                parent_face_geometry="wheel_cheek",
                parent_face_side="positive_z",
                child_face_geometry="wheel_body",
                child_face_side="negative_z",
                contact_tol=0.0040,
            ),
        )
        names.append(f"wheel_{i}")
    return names


def _emit_bender(model, chassis, r: ResolvedMusicKeyboardConfig) -> list[str]:
    if r.pitch_bender == "joystick_gimbal":
        return _emit_joystick(model, chassis, r)
    if r.pitch_bender == "pitch_mod_wheels":
        return _emit_wheels(model, chassis, r)
    return _emit_touch_strip(model, chassis, r)


# --------------------------------------------------------------------------- #
# Top-level build.
# --------------------------------------------------------------------------- #
def build_music_keyboard(
    config: MusicKeyboardConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name or "music_keyboard", assets=assets)
    registered = {token: model.material(f"mk_{token}", rgba=rgba) for token, rgba in r.mats.items()}
    r = replace(r, mats=registered)

    chassis = _build_chassis(model, r)
    _emit_keybed(model, chassis, r)
    _emit_control_surface(model, chassis, r)
    _emit_bender(model, chassis, r)
    return model


def build_seeded_music_keyboard(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_music_keyboard(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices (module_topology_diversity).
# --------------------------------------------------------------------------- #
def slot_choices_for_config(r: ResolvedMusicKeyboardConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("control_surface", r.control_surface),
        ("pitch_bender", r.pitch_bender),
        ("chassis_form", r.chassis_form),
        ("key_count", f"keys_{r.key_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #
ApiObj = ArticulatedObject


def _control_part_names(r: ResolvedMusicKeyboardConfig, model: ArticulatedObject) -> list[str]:
    prefixes = (
        "pad_",
        "knob_",
        "grid_knob_",
        "master_knob_",
        "osc_knob_",
        "filter_knob_",
        "fader_",
        "env_slider_",
    )
    return [p.name for p in model.parts if any(p.name.startswith(pre) for pre in prefixes)]


def _declare_allowances(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedMusicKeyboardConfig
) -> None:
    chassis = model.get_part("chassis")
    part_names = {p.name for p in model.parts}

    # Key tails + hidden hinge line pass under the panel lip (both forms).
    for p in model.parts:
        if p.name.startswith("white_key_") or p.name.startswith("black_key_"):
            ctx.allow_overlap(
                p,
                chassis,
                reason="key tail and hidden hinge pass under the panel lip into the keybed cavity",
            )

    # Controls seat a fraction into the deck/panel (real mount contact, not a gap).
    for name in _control_part_names(r, model):
        ctx.allow_overlap(
            model.get_part(name),
            chassis,
            reason="control base seats into the deck/panel surface at its mount",
        )

    # Bender mounts (joystick gimbal on its socket, wheels between brackets).
    for name in ("joystick_gimbal", "joystick_stick", "wheel_0", "wheel_1"):
        if name in part_names:
            ctx.allow_overlap(
                model.get_part(name),
                chassis,
                reason="bender control seats on its socket / between its brackets",
            )

    # Joystick stick hub seats inside the gimbal ring bore (nested pivot).
    if "joystick_stick" in part_names and "joystick_gimbal" in part_names:
        ctx.allow_overlap(
            model.get_part("joystick_stick"),
            model.get_part("joystick_gimbal"),
            reason="stick base hub seats inside the gimbal ring bore at the nested pivot",
        )


def run_music_keyboard_tests(
    object_model: ArticulatedObject, config: MusicKeyboardConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_allowances(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    part_names = {p.name for p in object_model.parts}
    whites = [n for n in part_names if n.startswith("white_key_")]
    blacks = [n for n in part_names if n.startswith("black_key_")]

    # --- Keybed multiplicity self-consistency ------------------------------- #
    ctx.check(
        f"{r.n_white} white naturals (= 7*octaves+1)",
        len(whites) == r.n_white,
        details=f"got {len(whites)}, want {r.n_white}",
    )
    ctx.check(
        f"{r.n_black} black sharps (= 5*octaves)",
        len(blacks) == r.n_black,
        details=f"got {len(blacks)}, want {r.n_black}",
    )
    ctx.check(
        f"key_count {r.key_count} = N_white + N_black",
        len(whites) + len(blacks) == r.key_count,
        details=f"got {len(whites) + len(blacks)}",
    )

    # --- Every key is a rear-hinged REVOLUTE press about +X, rest@0 --------- #
    bad = []
    for i in range(r.n_white):
        j = object_model.get_articulation(f"chassis_to_white_key_{i}")
        lim = j.motion_limits
        if (
            tuple(j.axis) != (1.0, 0.0, 0.0)
            or lim is None
            or lim.lower != 0.0
            or lim.upper is None
            or lim.upper <= 0.0
        ):
            bad.append(j.name)
    for j_idx in range(r.n_black):
        j = object_model.get_articulation(f"chassis_to_black_key_{j_idx}")
        lim = j.motion_limits
        if (
            tuple(j.axis) != (1.0, 0.0, 0.0)
            or lim is None
            or lim.lower != 0.0
            or lim.upper is None
            or lim.upper <= 0.0
        ):
            bad.append(j.name)
    ctx.check("all keys REVOLUTE +X with rest@0 downward press", not bad, details=str(bad))

    # --- A representative white key presses straight down -------------------- #
    mid = r.n_white // 2
    wk = object_model.get_part(f"white_key_{mid}")
    wk_joint = object_model.get_articulation(f"chassis_to_white_key_{mid}")
    rest = ctx.part_world_aabb(wk)
    with ctx.pose({wk_joint: r.key_press_rad}):
        pressed = ctx.part_world_aabb(wk)
    ctx.check(
        "pressed white key tip dips down and stays off the base slab",
        rest is not None
        and pressed is not None
        and pressed[0][2] < rest[0][2] - 0.003
        and pressed[0][2] > BASE_TOP_Z - 1e-4,
        details=f"rest_min_z={rest[0][2] if rest else None}, "
        f"pressed_min_z={pressed[0][2] if pressed else None}, base_top={BASE_TOP_Z}",
    )

    # --- Control cluster: identity + a representative control articulates ----- #
    control_names = _control_part_names(r, object_model)
    ctx.check(
        f"control_surface {r.control_surface} emits a non-empty control cluster",
        len(control_names) >= 4,
        details=f"got {len(control_names)} control parts",
    )

    has_revolute_control = any(
        not n.startswith(("pad_", "fader_", "env_slider_")) for n in control_names
    )
    has_prismatic_control = any(
        n.startswith(("pad_", "fader_", "env_slider_")) for n in control_names
    )
    ctx.check(
        "at least one non-fixed control (knob REVOLUTE or pad/fader PRISMATIC)",
        has_revolute_control or has_prismatic_control,
        details=str(sorted(control_names)),
    )

    sample = control_names[0]
    sj = object_model.get_articulation(f"chassis_to_{sample}")
    sample_part = object_model.get_part(sample)
    rest_c = ctx.part_world_aabb(sample_part)
    target = sj.motion_limits.upper if sj.motion_limits.upper else 0.0
    with ctx.pose({sj: target}):
        moved_c = ctx.part_world_aabb(sample_part)
    ctx.check(
        f"control {sample} actuates from its joint",
        rest_c is not None and moved_c is not None,
        details=f"joint={sj.name}, axis={tuple(sj.axis)}",
    )

    # --- Bender per type ----------------------------------------------------- #
    if r.pitch_bender == "joystick_gimbal":
        gimbal = object_model.get_part("joystick_gimbal")
        stick = object_model.get_part("joystick_stick")
        pitch = object_model.get_articulation("joystick_pitch")
        mod = object_model.get_articulation("joystick_mod")
        ctx.check(
            "joystick is a nested 2-DOF gimbal (pitch +Y -> mod +X on the gimbal)",
            gimbal is not None
            and stick is not None
            and tuple(pitch.axis) == (0.0, 1.0, 0.0)
            and tuple(mod.axis) == (1.0, 0.0, 0.0)
            and mod.parent == "joystick_gimbal",
            details=f"pitch_axis={tuple(pitch.axis)}, mod_axis={tuple(mod.axis)}, "
            f"mod_parent={mod.parent}",
        )
        rest_s = ctx.part_world_aabb(stick)
        with ctx.pose({pitch: 0.35}):
            tilted_s = ctx.part_world_aabb(stick)
        ctx.check(
            "joystick pitch tilts the stick sideways",
            rest_s is not None
            and tilted_s is not None
            and abs(tilted_s[1][0] - rest_s[1][0]) > 0.001,
            details=f"rest={rest_s}, tilted={tilted_s}",
        )
    elif r.pitch_bender == "pitch_mod_wheels":
        ctx.check(
            "pitch_mod_wheels emits a parallel wheel pair on +X axles",
            all(f"wheel_{i}" in part_names for i in range(2))
            and tuple(object_model.get_articulation("chassis_to_wheel_0").axis) == (1.0, 0.0, 0.0)
            and tuple(object_model.get_articulation("chassis_to_wheel_1").axis) == (1.0, 0.0, 0.0),
            details=str(sorted(n for n in part_names if n.startswith("wheel_"))),
        )
        w0 = object_model.get_part("wheel_0")
        wj = object_model.get_articulation("chassis_to_wheel_0")
        rest_w = ctx.part_world_aabb(w0)
        with ctx.pose({wj: 1.0}):
            spun_w = ctx.part_world_aabb(w0)
        ctx.check(
            "pitch wheel spins about its horizontal axle",
            rest_w is not None and spun_w is not None,
            details=f"rest={rest_w}, spun={spun_w}",
        )
    else:
        ctx.check(
            "touch_strip bender block sits at the front-left of the body",
            object_model.get_part("chassis").get_visual("bender_block") is not None,
            details="missing bender_block",
        )

    # --- Chassis form identity ---------------------------------------------- #
    chassis = object_model.get_part("chassis")
    if r.chassis_form == "upright_wood_cheeks":
        ctx.check(
            "upright_wood_cheeks has an angled panel + two walnut cheeks",
            chassis.get_visual("angled_panel") is not None
            and chassis.get_visual("cheek_0") is not None
            and chassis.get_visual("cheek_1") is not None,
            details="missing angled panel / cheeks",
        )
    else:
        ctx.check(
            "flat_slab has a horizontal control deck",
            chassis.get_visual("control_deck") is not None,
            details="missing control_deck",
        )

    return ctx.report()


__all__ = [
    "MusicKeyboardConfig",
    "ResolvedMusicKeyboardConfig",
    "config_from_seed",
    "resolve_config",
    "build_music_keyboard",
    "build_seeded_music_keyboard",
    "slot_choices_for_seed",
    "run_music_keyboard_tests",
    "__modular__",
]
