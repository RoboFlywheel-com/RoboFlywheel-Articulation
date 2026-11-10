# SPDX-License-Identifier: Apache-2.0

"""Container locker — modular procedural template (steel storage locker bank).

Category identity: a row of N upright sheet-metal storage / changing-room
lockers standing side by side. A shared ``carcass`` (ROOT) carries a full-width
floor plinth, ``range(N-1)`` dividers, and per-bay back / side / top / bottom /
shelf panels, all emitted in a single ``for i in range(bank_count)`` loop. Each
bay has a front door that opens by one of several mechanisms (the main
articulation), a door-face ventilation/surface treatment, and a lock/latch
with its own moving part. The whole bank is centered on x=0, sits on z=0, and
its doors face +Y.

Three named slots + one multiplicity axis (spec ``Container_Locker.md``):

  * ``closure_mechanism`` (4) — the per-bay door mechanism:
      - hinged_single_door: one REVOLUTE +Z side-hinged door per bay.
      - double_leaf_doors: two narrow leaves, REVOLUTE +Z / -Z opening from
        the bay centerline.
      - sliding_door: one PRISMATIC ±X door on top/bottom track rails.
      - roll_down_shutter: a corrugated curtain of N_SLATS cadquery slats on a
        PRISMATIC +Z joint rising into a head box along side guide channels.
  * ``door_surface`` (4) — fixed visuals on the door face (no joints):
      louver_vents (VentGrille), perforated_mesh_panel (PerforatedPanel),
      horizontal_slot_vents (looped Box slots), solid_smooth_door (proud rib
      frame). Degenerates to a no-op under roll_down_shutter (the curtain
      defines its own face).
  * ``latch_mechanism`` (3) — the per-bay lock with >=1 non-fixed joint:
      - keypad_buttons: 10 PRISMATIC -Y push-buttons on a keypad plate.
      - padlock_hasp: REVOLUTE +X flip hasp arm + fixed brass padlock/staple.
      - rotary_combo_dial: REVOLUTE +Y face-normal knurled combination dial.
    Parent is the door for hinged/double/sliding; the carcass front panel for
    roll_down_shutter.
  * ``bank_count`` (multiplicity, N in [2, 8]) — number of side-by-side bays;
    weighted toward small N. Copies the entire bay via ``range(N)``.

Continuous size/clearance variation (bank height, bay width, slide travel,
hinge open limit, keypad press) lives in ``resolve_config`` as clamped params,
never as slot candidates. ``palette_style`` (10 colorways x finish) is a
color/material axis only and is NOT a slot choice.

Sources (articraft_data ``picture/Container/Locker`` 5-star pool, all read):
parent ``d0776185`` (hinged + louver + keypad + bank=2), forks
``double_leaf_doors`` / ``sliding_door`` / ``roll_down_shutter`` (closure),
``perforated_mesh_panel`` / ``horizontal_slot_vents`` / ``solid_smooth_door``
(door_surface), ``padlock_hasp`` / ``rotary_combo_dial`` (latch),
``bank_count_3`` / ``bank_count_4`` (multiplicity range loop + N-1 dividers).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Container_Locker.md``
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
    CylinderGeometry,
    ExtrudeWithHolesGeometry,
    Inertial,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    KnobSkirt,
    MotionLimits,
    Origin,
    PerforatedPanelGeometry,
    TestContext,
    TestReport,
    TorusGeometry,
    VentGrilleGeometry,
    VentGrilleSlats,
    VentGrilleSleeve,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
ClosureMechanism = Literal[
    "hinged_single_door",
    "double_leaf_doors",
    "sliding_door",
    "roll_down_shutter",
]
DoorSurface = Literal[
    "louver_vents",
    "perforated_mesh_panel",
    "horizontal_slot_vents",
    "solid_smooth_door",
]
LatchMechanism = Literal[
    "keypad_buttons",
    "padlock_hasp",
    "rotary_combo_dial",
]
PaletteStyle = Literal[
    "locker_offwhite",
    "battleship_grey",
    "locker_blue",
    "forest_green",
    "tan_beige",
    "gloss_red_enamel",
    "brushed_stainless",
    "galvanized_zinc",
    "two_tone_grey_blue",
    "weathered_scuffed",
]

CLOSURE_MECHANISMS: tuple[ClosureMechanism, ...] = (
    "hinged_single_door",
    "double_leaf_doors",
    "sliding_door",
    "roll_down_shutter",
)
DOOR_SURFACES: tuple[DoorSurface, ...] = (
    "louver_vents",
    "perforated_mesh_panel",
    "horizontal_slot_vents",
    "solid_smooth_door",
)
LATCH_MECHANISMS: tuple[LatchMechanism, ...] = (
    "keypad_buttons",
    "padlock_hasp",
    "rotary_combo_dial",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "locker_offwhite",
    "battleship_grey",
    "locker_blue",
    "forest_green",
    "tan_beige",
    "gloss_red_enamel",
    "brushed_stainless",
    "galvanized_zinc",
    "two_tone_grey_blue",
    "weathered_scuffed",
)

# bank_count weighted sampling (small N favored; spec Multiplicity table).
_BANK_COUNTS: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8)
_BANK_WEIGHTS: tuple[float, ...] = (0.30, 0.25, 0.18, 0.12, 0.08, 0.04, 0.03)

# ---------------------------------------------------------------------------
# Palettes: carcass / door / latch+handle / accent (vent, plate, trim) +
# a finish-process annotation (matte_powdercoat / gloss_enamel / brushed_metal
# / galvanized / two_tone_powdercoat / weathered_matte). Anchored to 5-star
# RGBA where noted in the spec. palette-only — never a slot choice.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "locker_offwhite": {
        "carcass": (0.90, 0.90, 0.88, 1.0),
        "door": (0.90, 0.90, 0.88, 1.0),
        "latch": (0.12, 0.12, 0.14, 1.0),
        "accent": (0.18, 0.19, 0.21, 1.0),
        "finish": "matte_powdercoat",
    },
    "battleship_grey": {
        "carcass": (0.62, 0.64, 0.66, 1.0),
        "door": (0.56, 0.58, 0.60, 1.0),
        "latch": (0.12, 0.12, 0.14, 1.0),
        "accent": (0.18, 0.19, 0.21, 1.0),
        "finish": "matte_powdercoat",
    },
    "locker_blue": {
        "carcass": (0.78, 0.79, 0.80, 1.0),
        "door": (0.20, 0.34, 0.55, 1.0),
        "latch": (0.14, 0.15, 0.17, 1.0),
        "accent": (0.62, 0.64, 0.66, 1.0),
        "finish": "matte_powdercoat",
    },
    "forest_green": {
        "carcass": (0.80, 0.80, 0.78, 1.0),
        "door": (0.20, 0.34, 0.24, 1.0),
        "latch": (0.14, 0.15, 0.16, 1.0),
        "accent": (0.48, 0.50, 0.52, 1.0),
        "finish": "matte_powdercoat",
    },
    "tan_beige": {
        "carcass": (0.82, 0.76, 0.64, 1.0),
        "door": (0.74, 0.67, 0.54, 1.0),
        "latch": (0.30, 0.27, 0.22, 1.0),
        "accent": (0.42, 0.44, 0.48, 1.0),
        "finish": "matte_powdercoat",
    },
    "gloss_red_enamel": {
        "carcass": (0.88, 0.88, 0.86, 1.0),
        "door": (0.62, 0.14, 0.13, 1.0),
        "latch": (0.15, 0.15, 0.16, 1.0),
        "accent": (0.20, 0.21, 0.23, 1.0),
        "finish": "gloss_enamel",
    },
    "brushed_stainless": {
        "carcass": (0.70, 0.71, 0.73, 1.0),
        "door": (0.74, 0.75, 0.77, 1.0),
        "latch": (0.42, 0.44, 0.48, 1.0),
        "accent": (0.55, 0.57, 0.59, 1.0),
        "finish": "brushed_metal",
    },
    "galvanized_zinc": {
        "carcass": (0.66, 0.68, 0.70, 1.0),
        "door": (0.72, 0.74, 0.75, 1.0),
        "latch": (0.40, 0.41, 0.44, 1.0),
        "accent": (0.50, 0.52, 0.54, 1.0),
        "finish": "galvanized",
    },
    "two_tone_grey_blue": {
        "carcass": (0.60, 0.62, 0.64, 1.0),
        "door": (0.26, 0.38, 0.52, 1.0),
        "latch": (0.12, 0.12, 0.14, 1.0),
        "accent": (0.84, 0.85, 0.86, 1.0),
        "finish": "two_tone_powdercoat",
    },
    "weathered_scuffed": {
        "carcass": (0.58, 0.57, 0.54, 1.0),
        "door": (0.50, 0.49, 0.46, 1.0),
        "latch": (0.16, 0.16, 0.17, 1.0),
        "accent": (0.34, 0.30, 0.24, 1.0),
        "finish": "weathered_matte",
    },
}

# ---------------------------------------------------------------------------
# Base geometry constants (meters), from the 5-star sources. Nominal LOCKER_W /
# LOCKER_H are scaled per-build by resolve_config.
# ---------------------------------------------------------------------------
_LOCKER_W = 0.30
_LOCKER_D = 0.45
_LOCKER_H = 0.90
_DOOR_TH = 0.018
_WALL = 0.012
# Side reveal between a door/leaf and its bay edge. Widened from the sample's
# 4mm so that adjacent bays' door edges sit 2*_HINGE_GAP apart: a hinged door
# (or double-leaf leaf) swinging to its open limit clears the neighbour bay's
# door instead of grazing it. See _MAX_HINGE_OPEN / _MAX_DOUBLE_LEAF_OPEN.
_HINGE_GAP = 0.014
_CENTER_GAP = 0.003  # gap where double-leaf doors meet

# Neighbour-clearance open-angle caps (single-sourced; motion-QC-derived).
# A door hinged at a bay edge encroaches on the adjacent bay once it swings past
# ~90deg (its free edge crosses the hinge plane) and its proud handle sweeps
# into the neighbour near perpendicular. Single doors cascade one way so they
# clear up to ~88deg; two adjacent double-leaf leaves swing toward the SAME
# divider, so they must stop lower. Values verified with the clearance solver
# (sdk.min_clearance_at_pose) at the worst-case both-open pose for _HINGE_GAP.
_MAX_HINGE_OPEN = math.radians(88.0)
_MAX_DOUBLE_LEAF_OPEN = math.radians(72.0)

# keypad
_BTN_R = 0.011
_BTN_LEN = 0.010
_BTN_PRESS = 0.0015
_BTN_COLS = 5
_BTN_ROWS = 2

# sliding track
_TRACK_H = 0.010
_TRACK_D = 0.004

# shutter
_GUIDE_W = 0.014
_GUIDE_DEPTH = 0.018
_SLAT_H = 0.022
_SLAT_D = 0.010
_SLAT_BULGE = 0.003
_SLAT_GAP = 0.002
_SLAT_PITCH = _SLAT_H + _SLAT_GAP
_HEAD_BOX_H = 0.065

# padlock hasp
_HASP_W = 0.028
_HASP_L = 0.065
_HASP_TH = 0.003
_HASP_SETBACK = 0.025
_SLOT_W = 0.020
_SLOT_L = 0.022
_SLOT_OFFSET = 0.015
_STAPLE_PLATE_W = 0.038
_STAPLE_PLATE_TH = 0.003
_STAPLE_LEG_SPAN = 0.014
_STAPLE_LEG_W = 0.004
_STAPLE_LEG_D = 0.004
_STAPLE_LEG_PROT = 0.025
_STAPLE_BAR_D = 0.004
_STAPLE_BAR_H = 0.004
_PADLOCK_W = 0.038
_PADLOCK_D = 0.015
_PADLOCK_H = 0.030
_SHACKLE_ROD = 0.004
_SHACKLE_SPAN = 0.008
_SHACKLE_H = 0.015

# dial
_DIAL_R = 0.022
_DIAL_HEIGHT = 0.012
_HOUSING_R = 0.028
_HOUSING_DEPTH = 0.008


@dataclass(frozen=True)
class ContainerLockerConfig:
    closure_mechanism: ClosureMechanism = "hinged_single_door"
    door_surface: DoorSurface = "louver_vents"
    latch_mechanism: LatchMechanism = "keypad_buttons"
    bank_count: int = 2
    palette_style: PaletteStyle = "locker_offwhite"
    bank_height_scale: float = 1.0
    bay_width_scale: float = 1.0
    slide_travel_scale: float = 1.0
    hinge_open_limit: float = math.radians(100.0)
    keypad_press_scale: float = 1.0
    name: str = "container_locker"


@dataclass(frozen=True)
class ResolvedContainerLockerConfig:
    closure_mechanism: ClosureMechanism
    door_surface: DoorSurface
    latch_mechanism: LatchMechanism
    bank_count: int
    palette_style: PaletteStyle
    bank_height_scale: float
    bay_width_scale: float
    slide_travel_scale: float
    hinge_open_limit: float
    keypad_press_scale: float
    # derived geometry
    locker_w: float
    locker_h: float
    door_w: float
    door_h: float
    btn_press: float
    # latch parent semantics (door part vs carcass front panel)
    latch_on_door: bool
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerLockerConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    bank_count = rng.choices(_BANK_COUNTS, weights=_BANK_WEIGHTS, k=1)[0]
    closure = rng.choice(CLOSURE_MECHANISMS)
    door_surface = rng.choice(DOOR_SURFACES)
    latch = rng.choice(LATCH_MECHANISMS)
    # Coupling: a bypass sliding door cannot carry a forward-flipping padlock
    # hasp -- when the neighbouring bay's door slides across on the outer plane
    # it would foul the open hasp (which swings tens of mm proud). Real bypass
    # sliding doors use flush/cam locks, so gate the hasp off sliding and draw a
    # flush latch instead. (padlock_hasp stays reachable via the other closures.)
    if closure == "sliding_door" and latch == "padlock_hasp":
        latch = rng.choice(("keypad_buttons", "rotary_combo_dial"))
    palette = rng.choice(PALETTE_STYLES)
    return ContainerLockerConfig(
        closure_mechanism=closure,
        door_surface=door_surface,
        latch_mechanism=latch,
        bank_count=bank_count,
        palette_style=palette,
        bank_height_scale=round(rng.uniform(0.85, 1.15), 4),
        bay_width_scale=round(rng.uniform(0.90, 1.12), 4),
        slide_travel_scale=round(rng.uniform(0.90, 1.10), 4),
        hinge_open_limit=round(rng.uniform(math.radians(72.0), _MAX_HINGE_OPEN), 5),
        keypad_press_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_container_locker_{seed}",
    )


def resolve_config(
    config: ContainerLockerConfig | None = None,
) -> ResolvedContainerLockerConfig:
    cfg = config or ContainerLockerConfig()
    closure = _pick(cfg.closure_mechanism, CLOSURE_MECHANISMS)
    door_surface = _pick(cfg.door_surface, DOOR_SURFACES)
    latch = _pick(cfg.latch_mechanism, LATCH_MECHANISMS)
    # Enforce the bypass-slide / padlock-hasp coupling (see config_from_seed) for
    # any explicit config too, so the builder never sees the fouling combination.
    if closure == "sliding_door" and latch == "padlock_hasp":
        latch = "rotary_combo_dial"
    palette = _pick(cfg.palette_style, PALETTE_STYLES)
    bank_count = int(_clamp(cfg.bank_count, 2, 8))

    h_scale = _clamp(cfg.bank_height_scale, 0.85, 1.15)
    w_scale = _clamp(cfg.bay_width_scale, 0.90, 1.12)
    slide_scale = _clamp(cfg.slide_travel_scale, 0.90, 1.10)
    press_scale = _clamp(cfg.keypad_press_scale, 0.85, 1.15)
    open_limit = _clamp(cfg.hinge_open_limit, math.radians(72.0), _MAX_HINGE_OPEN)

    locker_w = _LOCKER_W * w_scale
    locker_h = _LOCKER_H * h_scale
    # DOOR_W is an equation following LOCKER_W (spec door_width_scale equation).
    door_w = locker_w - 2.0 * _HINGE_GAP
    door_h = locker_h - 2.0 * _HINGE_GAP
    btn_press = _BTN_PRESS * press_scale

    # roll_down_shutter degenerates door_surface to a no-op (curtain defines the
    # face). The latch parents to the carcass front panel only under shutter.
    latch_on_door = closure != "roll_down_shutter"

    return ResolvedContainerLockerConfig(
        closure_mechanism=closure,
        door_surface=door_surface,
        latch_mechanism=latch,
        bank_count=bank_count,
        palette_style=palette,
        bank_height_scale=h_scale,
        bay_width_scale=w_scale,
        slide_travel_scale=slide_scale,
        hinge_open_limit=open_limit,
        keypad_press_scale=press_scale,
        locker_w=locker_w,
        locker_h=locker_h,
        door_w=door_w,
        door_h=door_h,
        btn_press=btn_press,
        latch_on_door=latch_on_door,
        name=cfg.name or "container_locker",
    )


def with_overrides(config: ContainerLockerConfig, **kwargs: object) -> ContainerLockerConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerLockerConfig | ResolvedContainerLockerConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerLockerConfig) else resolve_config(config)
    return (
        ("closure_mechanism", r.closure_mechanism),
        ("door_surface", r.door_surface),
        ("latch_mechanism", r.latch_mechanism),
        ("bank_count", f"bank_{r.bank_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _bay_center_x(i: int, n: int, locker_w: float) -> float:
    """Bay i center X for an N-bay bank centered on x=0 (bank_count source)."""
    return (i - (n - 1) / 2.0) * locker_w


def _emit_carcass_bay_panels(
    carcass,
    cx: float,
    i: int,
    r: ResolvedContainerLockerConfig,
    *,
    carcass_mat,
    accent_mat,
) -> None:
    """Back / side_l / side_r / top / bottom / shelf for one bay (parent P1)."""
    lw, ld, lh, wall = r.locker_w, _LOCKER_D, r.locker_h, _WALL
    carcass.visual(
        Box((lw, wall, lh)),
        origin=Origin(xyz=(cx, -ld / 2.0 + wall / 2.0, lh / 2.0)),
        material=accent_mat,
        name=f"back_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    carcass.visual(
        Box((wall, ld, lh)),
        origin=Origin(xyz=(cx - lw / 2.0 + wall / 2.0, 0.0, lh / 2.0)),
        material=carcass_mat,
        name=f"side_l_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    carcass.visual(
        Box((wall, ld, lh)),
        origin=Origin(xyz=(cx + lw / 2.0 - wall / 2.0, 0.0, lh / 2.0)),
        material=carcass_mat,
        name=f"side_r_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    carcass.visual(
        Box((lw, ld, wall)),
        origin=Origin(xyz=(cx, 0.0, lh - wall / 2.0)),
        material=carcass_mat,
        name=f"top_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    carcass.visual(
        Box((lw, ld, wall)),
        origin=Origin(xyz=(cx, 0.0, wall / 2.0)),
        material=carcass_mat,
        name=f"bottom_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    carcass.visual(
        Box((lw - 2 * wall, ld - wall, wall * 0.7)),
        origin=Origin(xyz=(cx, wall / 2.0, lh * 0.55)),
        material=accent_mat,
        name=f"shelf_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )


# Build-scoped mesh cache so an expensive boolean mesh (perforated panel) is
# computed ONCE and reused across all N bays instead of re-cut per bay. The
# Mesh object is immutable in our usage; reusing it across visuals matches the
# shutter slat pattern in the 5-star source. Reset at the start of each build.
_MESH_CACHE: dict[tuple, object] = {}


def _cached_perforated_mesh(key: str, geom) -> object:
    cached = _MESH_CACHE.get(("perf", key))
    if cached is None:
        cached = mesh_from_geometry(geom, key)
        _MESH_CACHE[("perf", key)] = cached
    return cached


# --- door_surface (fixed visuals on a door panel) --------------------------
def _apply_door_surface(
    door,
    i: int,
    r: ResolvedContainerLockerConfig,
    *,
    face_cx: float,
    front_y: float,
    accent_mat,
    carcass_mat,
    door_mat,
) -> None:
    """Attach the door_surface fixed visuals to a door panel.

    ``face_cx`` is the panel-center X in the door's own local frame (DOOR_W/2
    for hinge-local frames; 0.0 for center frames). ``front_y`` is the door
    front-face local Y (= DOOR_TH/2). No joints. roll_down_shutter never calls
    this (curtain defines its own face).
    """
    door_w, door_h = r.door_w, r.door_h
    surface = r.door_surface

    if surface == "louver_vents":
        vent_w = door_w * 0.55
        vent_h = 0.075
        vent_z = door_h / 2.0 - 0.085
        vent = VentGrilleGeometry(
            (vent_w, vent_h),
            frame=0.008,
            face_thickness=0.0035,
            duct_depth=0.012,
            duct_wall=0.0025,
            slat_pitch=0.012,
            slat_width=0.008,
            slat_angle_deg=35.0,
            corner_radius=0.003,
            slats=VentGrilleSlats(profile="flat", direction="down"),
            sleeve=VentGrilleSleeve(style="short"),
            center=True,
        )
        door.visual(
            mesh_from_geometry(vent, f"vent_{i}"),
            origin=Origin(
                xyz=(face_cx, front_y - 0.006, vent_z),
                rpy=(-math.pi / 2.0, 0.0, 0.0),
            ),
            material=accent_mat,
            name=f"door_vent_{i}", material_class_id=("metal.patterned_sheet_panel" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.patterned_sheet"),
        )
    elif surface == "perforated_mesh_panel":
        mesh_w = door_w * 0.78
        mesh_h = door_h * 0.74
        mesh_th = 0.003
        mesh_cz = 0.065
        # Coarser perforation pitch / larger holes than the source so the
        # boolean hole-cut mesh stays tractable when copied across N bays
        # (the source only built N=2). Still reads as a perforated sheet.
        perf = PerforatedPanelGeometry(
            (mesh_w, mesh_h),
            mesh_th,
            hole_diameter=0.012,
            pitch=(0.032, 0.032),
            frame=0.012,
            corner_radius=0.004,
            stagger=False,
            center=True,
        )
        door.visual(
            _cached_perforated_mesh("door_mesh_panel", perf),
            origin=Origin(
                xyz=(face_cx, front_y + mesh_th / 2.0 - 0.001, mesh_cz),
                rpy=(-math.pi / 2.0, 0.0, 0.0),
            ),
            material=accent_mat,
            name=f"door_mesh_{i}", material_class_id=("metal.mesh_chainmail" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.patterned_sheet"),
        )
    elif surface == "horizontal_slot_vents":
        slot_count = 8
        slot_w = door_w * 0.58
        slot_h = 0.004
        slot_depth = 0.005
        slot_pitch = 0.022
        slot_start_z = door_h / 2.0 - 0.055
        for j in range(slot_count):
            sz = slot_start_z - j * slot_pitch
            door.visual(
                Box((slot_w, slot_depth, slot_h)),
                origin=Origin(xyz=(face_cx, front_y - slot_depth / 2.0 + 0.001, sz)),
                material=accent_mat,
                name=f"door_slot_{i}_{j}", material_class_id=("metal.patterned_sheet_panel" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.patterned_sheet"),
            )
    elif surface == "solid_smooth_door":
        rib_w = 0.012
        rib_h = 0.003
        inset = 0.040
        rib_y = front_y + rib_h / 2.0
        h_span = door_w - 2.0 * inset
        v_span = door_h - 2.0 * inset
        door.visual(
            Box((h_span, rib_h, rib_w)),
            origin=Origin(xyz=(face_cx, rib_y, door_h / 2.0 - inset - rib_w / 2.0)),
            material=door_mat,
            name=f"rib_top_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        door.visual(
            Box((h_span, rib_h, rib_w)),
            origin=Origin(xyz=(face_cx, rib_y, -door_h / 2.0 + inset + rib_w / 2.0)),
            material=door_mat,
            name=f"rib_bot_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        door.visual(
            Box((rib_w, rib_h, v_span)),
            origin=Origin(xyz=(face_cx - door_w / 2.0 + inset + rib_w / 2.0, rib_y, 0.0)),
            material=door_mat,
            name=f"rib_left_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        door.visual(
            Box((rib_w, rib_h, v_span)),
            origin=Origin(xyz=(face_cx + door_w / 2.0 - inset - rib_w / 2.0, rib_y, 0.0)),
            material=door_mat,
            name=f"rib_right_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )

    # number plate (always present, ties the lower face together) below the
    # surface treatment. Coarser perforation than the source so the boolean
    # mesh is cheap when copied across N bays; cached + reused per build.
    plate = PerforatedPanelGeometry(
        (0.045, 0.030),
        0.0025,
        hole_diameter=0.0030,
        pitch=(0.0110, 0.0110),
        frame=0.005,
        corner_radius=0.002,
    )
    plate_z = door_h / 2.0 - 0.160
    door.visual(
        _cached_perforated_mesh("door_plate", plate),
        origin=Origin(xyz=(face_cx, front_y, plate_z)),
        material=accent_mat,
        name=f"door_plate_{i}", material_class_id=("metal.mesh_chainmail" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.patterned_sheet"),
    )


# --- latch on a door panel -------------------------------------------------
def _hasp_arm_mesh(i: int):
    hw = _HASP_W / 2.0
    hl = _HASP_L / 2.0
    outer = [(-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl)]
    slot_cy = hl - _SLOT_OFFSET
    shw = _SLOT_W / 2.0
    shl = _SLOT_L / 2.0
    hole = [
        (-shw, slot_cy - shl),
        (shw, slot_cy - shl),
        (shw, slot_cy + shl),
        (-shw, slot_cy + shl),
    ]
    geom = ExtrudeWithHolesGeometry(outer, [hole], _HASP_TH, cap=True, center=True)
    return mesh_from_geometry(geom, f"hasp_arm_{i}")


def _emit_keypad(
    model,
    parent,
    i: int,
    r: ResolvedContainerLockerConfig,
    *,
    pad_cx: float,
    pad_cz: float,
    plate_front_y: float,
    btn_front_y: float,
    accent_mat,
    latch_mat,
) -> list[str]:
    """Keypad plate visual on the parent + 10 PRISMATIC -Y buttons (parent P1).

    ``plate_front_y`` = local Y of the keypad plate center face. ``btn_front_y``
    = local Y of the button base (proud of the plate). Returns button part
    names. Works for both door-local and carcass-local frames.
    """
    col_pitch = 2 * _BTN_R + 0.004
    row_pitch = 2 * _BTN_R + 0.004
    pad_w = _BTN_COLS * col_pitch + 0.010
    pad_h = _BTN_ROWS * row_pitch + 0.010
    parent.visual(
        Box((pad_w, 0.006, pad_h)),
        origin=Origin(xyz=(pad_cx, plate_front_y, pad_cz)),
        material=accent_mat,
        name=f"lockpad_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    x0 = pad_cx - (_BTN_COLS - 1) * col_pitch / 2.0
    z0 = pad_cz - (_BTN_ROWS - 1) * row_pitch / 2.0
    names: list[str] = []
    n = 0
    for rr in range(_BTN_ROWS):
        for cc in range(_BTN_COLS):
            bx = x0 + cc * col_pitch
            bz = z0 + rr * row_pitch
            btn = model.part(f"lockbtn_{i}_{n}")
            cyl = CylinderGeometry(_BTN_R, _BTN_LEN, radial_segments=20).rotate_x(math.pi / 2.0)
            btn.visual(
                mesh_from_geometry(cyl, f"btn_{i}_{n}"),
                origin=Origin(xyz=(0.0, 0.0, 0.0)),
                material=latch_mat,
                name=f"btn_cap_{i}_{n}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "plastic.weathered_worn"),
            )
            btn.inertial = Inertial.from_geometry(
                Box((2 * _BTN_R, _BTN_LEN, 2 * _BTN_R)), mass=0.004
            )
            model.articulation(
                f"btnjoint_{i}_{n}",
                ArticulationType.PRISMATIC,
                parent=parent,
                child=btn,
                origin=Origin(xyz=(bx, btn_front_y + _BTN_LEN / 2.0, bz)),
                axis=(0.0, -1.0, 0.0),
                motion_limits=MotionLimits(effort=5.0, velocity=0.05, lower=0.0, upper=r.btn_press),
            )
            names.append(f"lockbtn_{i}_{n}")
            n += 1
    return names


def _apply_latch_on_door(
    model,
    door,
    i: int,
    r: ResolvedContainerLockerConfig,
    *,
    face_cx: float,
    front_y: float,
    cx: float,
    carcass,
    accent_mat,
    latch_mat,
    door_mat,
    steel_mat,
    brass_mat,
) -> None:
    """Attach the latch mechanism to a door panel (hinged/double/sliding).

    All values are in the door's own local frame except padlock staple/body
    visuals, which mount on the carcass (passed in)."""
    door_w, door_h = r.door_w, r.door_h

    if r.latch_mechanism == "keypad_buttons":
        pad_cz = -door_h / 2.0 + 0.110
        _emit_keypad(
            model,
            door,
            i,
            r,
            pad_cx=face_cx,
            pad_cz=pad_cz,
            plate_front_y=front_y + 0.003,
            btn_front_y=front_y + 0.006,
            accent_mat=accent_mat,
            latch_mat=latch_mat,
        )

    elif r.latch_mechanism == "padlock_hasp":
        # bracket plate on the door front near the free edge.
        free_local_x = face_cx + door_w / 2.0  # door free-edge X in local frame
        hasp_x = free_local_x - _HASP_SETBACK
        door.visual(
            Box((_HASP_W + 0.012, 0.006, 0.028)),
            origin=Origin(xyz=(hasp_x, front_y + 0.003, 0.0)),
            material=accent_mat,
            name=f"hasp_bracket_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        hasp = model.part(f"hasp_{i}")
        hasp.visual(
            _hasp_arm_mesh(i),
            origin=Origin(xyz=(0.0, 0.0, -_HASP_L / 2.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=steel_mat,
            name=f"hasp_arm_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "galvanized_zinc", "two_tone_grey_blue", "weathered_scuffed"} else "metal.stainless_matte"),
        )
        hasp.inertial = Inertial.from_geometry(
            Box((_HASP_W, _HASP_TH, _HASP_L)),
            mass=0.08,
            origin=Origin(xyz=(0.0, 0.0, -_HASP_L / 2.0)),
        )
        model.articulation(
            f"hasp_{i}",
            ArticulationType.REVOLUTE,
            parent=door,
            child=hasp,
            origin=Origin(xyz=(hasp_x, front_y + 0.006, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=5.0,
                velocity=1.5,
                lower=0.0,
                upper=min(r.hinge_open_limit, math.radians(90.0)),
            ),
        )
        # staple + padlock on the carcass front, aligned with the hasp arm slot.
        staple_x = cx + door_w / 2.0 - _HASP_SETBACK
        staple_z = r.locker_h / 2.0 - _HASP_L + _SLOT_OFFSET
        # Mounting jamb: bridge the staple plate back to the bay's right side wall
        # so the padlock staple rivets to real carcass sheet metal. The widened
        # side reveal (_HINGE_GAP) pulls the staple a few mm off the wall, which
        # would otherwise leave the staple/padlock a floating carcass island.
        carcass_front = _LOCKER_D / 2.0
        wall_inner_x = cx + r.locker_w / 2.0 - _WALL / 2.0
        staple_left_x = staple_x - _STAPLE_PLATE_W / 2.0
        carcass.visual(
            Box((wall_inner_x - staple_left_x, _WALL + _STAPLE_PLATE_TH, _STAPLE_PLATE_W)),
            origin=Origin(
                xyz=(
                    (staple_left_x + wall_inner_x) / 2.0,
                    carcass_front - _WALL / 2.0 + _STAPLE_PLATE_TH / 2.0,
                    staple_z,
                )
            ),
            material=accent_mat,
            name=f"hasp_jamb_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        _emit_padlock_staple(
            carcass,
            i,
            staple_x,
            staple_z,
            steel_mat=steel_mat,
            brass_mat=brass_mat,
        )

    elif r.latch_mechanism == "rotary_combo_dial":
        dial_cx = face_cx
        dial_cz = -door_h / 2.0 + 0.110
        housing_torus = TorusGeometry(
            radius=(_HOUSING_R + _DIAL_R) / 2.0,
            tube=(_HOUSING_R - _DIAL_R) / 2.0 + 0.002,
            radial_segments=12,
            tubular_segments=28,
        ).rotate_x(math.pi / 2.0)
        door.visual(
            mesh_from_geometry(housing_torus, f"dial_housing_{i}"),
            origin=Origin(xyz=(dial_cx, front_y - 0.002, dial_cz)),
            material=accent_mat,
            name=f"dial_housing_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        recess_disk = CylinderGeometry(_HOUSING_R, _HOUSING_DEPTH, radial_segments=28).rotate_x(
            math.pi / 2.0
        )
        door.visual(
            mesh_from_geometry(recess_disk, f"dial_recess_{i}"),
            origin=Origin(xyz=(dial_cx, front_y - _HOUSING_DEPTH / 2.0, dial_cz)),
            material=accent_mat,
            name=f"dial_recess_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        dial = model.part(f"dial_{i}")
        knob = KnobGeometry(
            _DIAL_R * 2.0,
            _DIAL_HEIGHT,
            body_style="cylindrical",
            skirt=KnobSkirt(_DIAL_R * 2.0 + 0.004, 0.003, flare=0.0, chamfer=0.001),
            grip=KnobGrip(style="knurled", count=48, depth=0.0008, helix_angle_deg=25.0),
            indicator=KnobIndicator(style="line", mode="engraved", depth=0.0006),
            center=False,
        )
        dial.visual(
            mesh_from_geometry(knob, f"dial_knob_{i}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=latch_mat,
            name=f"dial_knob_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "galvanized_zinc", "two_tone_grey_blue", "weathered_scuffed"} else "metal.stainless_matte"),
        )
        dial.inertial = Inertial.from_geometry(
            Box((_DIAL_R * 2.0, _DIAL_HEIGHT, _DIAL_R * 2.0)), mass=0.030
        )
        model.articulation(
            f"dialjoint_{i}",
            ArticulationType.REVOLUTE,
            parent=door,
            child=dial,
            origin=Origin(xyz=(dial_cx, front_y + 0.001, dial_cz)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=math.pi * 2.0),
        )


def _emit_padlock_staple(
    carcass,
    i: int,
    staple_x: float,
    staple_z: float,
    *,
    steel_mat,
    brass_mat,
) -> None:
    """Staple loop + brass padlock fixed visuals on the carcass (padlock_hasp)."""
    front_y = _LOCKER_D / 2.0
    carcass.visual(
        Box((_STAPLE_PLATE_W, _STAPLE_PLATE_TH, _STAPLE_PLATE_W)),
        origin=Origin(xyz=(staple_x, front_y + _STAPLE_PLATE_TH / 2.0, staple_z)),
        material=steel_mat,
        name=f"staple_plate_{i}", material_class_id="metal.steel_galvanized",
    )
    leg_base_y = front_y + _STAPLE_PLATE_TH
    carcass.visual(
        Box((_STAPLE_LEG_W, _STAPLE_LEG_PROT, _STAPLE_LEG_D)),
        origin=Origin(
            xyz=(staple_x - _STAPLE_LEG_SPAN / 2.0, leg_base_y + _STAPLE_LEG_PROT / 2.0, staple_z)
        ),
        material=steel_mat,
        name=f"staple_leg_l_{i}", material_class_id="metal.steel_galvanized",
    )
    carcass.visual(
        Box((_STAPLE_LEG_W, _STAPLE_LEG_PROT, _STAPLE_LEG_D)),
        origin=Origin(
            xyz=(staple_x + _STAPLE_LEG_SPAN / 2.0, leg_base_y + _STAPLE_LEG_PROT / 2.0, staple_z)
        ),
        material=steel_mat,
        name=f"staple_leg_r_{i}", material_class_id="metal.steel_galvanized",
    )
    bar_span = _STAPLE_LEG_SPAN + _STAPLE_LEG_W
    crossbar_outer_y = leg_base_y + _STAPLE_LEG_PROT
    carcass.visual(
        Box((bar_span, _STAPLE_BAR_D, _STAPLE_BAR_H)),
        origin=Origin(xyz=(staple_x, crossbar_outer_y - _STAPLE_BAR_D / 2.0, staple_z)),
        material=steel_mat,
        name=f"staple_bar_{i}", material_class_id="metal.steel_galvanized",
    )
    pad_y = crossbar_outer_y + _PADLOCK_D / 2.0 - 0.002
    pad_z = staple_z - _PADLOCK_H / 2.0
    carcass.visual(
        Box((_PADLOCK_W, _PADLOCK_D, _PADLOCK_H)),
        origin=Origin(xyz=(staple_x, pad_y, pad_z)),
        material=brass_mat,
        name=f"padlock_body_{i}", material_class_id="metal.brass_polished",
    )
    shackle_leg_len = _SHACKLE_H + 0.006
    shackle_leg_z = staple_z + _SHACKLE_H / 2.0
    carcass.visual(
        Cylinder(_SHACKLE_ROD / 2.0, shackle_leg_len),
        origin=Origin(xyz=(staple_x - _SHACKLE_SPAN / 2.0, pad_y, shackle_leg_z)),
        material=steel_mat,
        name=f"shackle_leg_l_{i}", material_class_id="metal.steel_galvanized",
    )
    carcass.visual(
        Cylinder(_SHACKLE_ROD / 2.0, shackle_leg_len),
        origin=Origin(xyz=(staple_x + _SHACKLE_SPAN / 2.0, pad_y, shackle_leg_z)),
        material=steel_mat,
        name=f"shackle_leg_r_{i}", material_class_id="metal.steel_galvanized",
    )
    carcass.visual(
        Cylinder(_SHACKLE_ROD / 2.0, _SHACKLE_SPAN + _SHACKLE_ROD),
        origin=Origin(
            xyz=(staple_x, pad_y, staple_z + _SHACKLE_H + 0.003), rpy=(0.0, math.pi / 2.0, 0.0)
        ),
        material=steel_mat,
        name=f"shackle_crown_{i}", material_class_id="metal.steel_galvanized",
    )


# ---------------------------------------------------------------------------
# Closure factories (one per bay). Each emits door part(s), the door_surface
# visuals, a handle, the inertial, the closure joint, and the latch.
# ---------------------------------------------------------------------------
def _front_y_carcass(r: ResolvedContainerLockerConfig) -> float:
    return _LOCKER_D / 2.0


def _slide_dirs_and_planes(n: int) -> tuple[list[int], list[int]]:
    """Per-bay slide direction and bypass track plane for sliding_door banks.

    End bays slide toward the bank interior (a parity direction at a bank end
    would run the track rails and the open door off the carcass into thin air);
    interior bays keep the parity alternation. With inward ends, two doors two
    bays apart can target the same intermediate bay, so a fixed 2-plane bypass
    is not collision-free for n>=3: each door's rest+target interval
    ``[min(i, i+d), max(i, i+d)]`` is greedily colored so interval-overlapping
    doors ride on distinct front planes (interval cliques are <= 3 deep -- rest
    plus one slider from each side -- so 3 planes always suffice).
    """
    dirs: list[int] = []
    for i in range(n):
        if i == 0:
            dirs.append(1)
        elif i == n - 1:
            dirs.append(-1)
        else:
            dirs.append(-1 if (i % 2 == 0) else 1)
    planes: list[int] = []
    for i in range(n):
        lo, hi = min(i, i + dirs[i]), max(i, i + dirs[i])
        used = {
            planes[j]
            for j in range(i)
            if lo <= max(j, j + dirs[j]) and min(j, j + dirs[j]) <= hi
        }
        plane = 0
        while plane in used:
            plane += 1
        planes.append(plane)
    return dirs, planes


def _build_hinged_bay(
    model,
    carcass,
    i: int,
    cx: float,
    r: ResolvedContainerLockerConfig,
    *,
    mats,
) -> None:
    door_w, door_h, lh = r.door_w, r.door_h, r.locker_h
    carcass_front_y = _LOCKER_D / 2.0
    door_front_y = carcass_front_y + _DOOR_TH / 2.0
    front_y = _DOOR_TH / 2.0  # door-local front-face Y

    door = model.part(f"door_{i}")
    door.visual(
        Box((door_w, _DOOR_TH, door_h)),
        origin=Origin(xyz=(door_w / 2.0, 0.0, 0.0)),
        material=mats["door"],
        name=f"door_panel_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    _apply_door_surface(
        door,
        i,
        r,
        face_cx=door_w / 2.0,
        front_y=front_y,
        accent_mat=mats["accent"],
        carcass_mat=mats["carcass"],
        door_mat=mats["door"],
    )
    door.visual(
        Box((0.016, 0.022, 0.16)),
        origin=Origin(xyz=(door_w - 0.030, front_y + 0.011, 0.06)),
        material=mats["latch"],
        name=f"door_handle_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "galvanized_zinc", "two_tone_grey_blue", "weathered_scuffed"} else "metal.stainless_matte"),
    )
    door.inertial = Inertial.from_geometry(
        Box((door_w, _DOOR_TH, door_h)),
        mass=4.0,
        origin=Origin(xyz=(door_w / 2.0, 0.0, 0.0)),
    )
    hinge_x = cx - door_w / 2.0
    model.articulation(
        f"hinge_{i}",
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=door,
        origin=Origin(xyz=(hinge_x, door_front_y, lh / 2.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=2.0, lower=0.0, upper=r.hinge_open_limit),
    )
    _apply_latch_on_door(
        model,
        door,
        i,
        r,
        face_cx=door_w / 2.0,
        front_y=front_y,
        cx=cx,
        carcass=carcass,
        accent_mat=mats["accent"],
        latch_mat=mats["latch"],
        door_mat=mats["door"],
        steel_mat=mats["latch"],
        brass_mat=mats["brass"],
    )


def _build_double_leaf_bay(
    model,
    carcass,
    i: int,
    cx: float,
    r: ResolvedContainerLockerConfig,
    *,
    mats,
) -> None:
    door_w, door_h, lh = r.door_w, r.door_h, r.locker_h
    leaf_w = (door_w - _CENTER_GAP) / 2.0
    carcass_front_y = _LOCKER_D / 2.0
    door_front_y = carcass_front_y + _DOOR_TH / 2.0
    front_y = _DOOR_TH / 2.0
    # Two adjacent leaves swing toward the shared divider from opposite bays;
    # cap their open limit below the single-door limit so they clear each other
    # and their proud handles at the worst-case both-open pose.
    leaf_open = min(r.hinge_open_limit, _MAX_DOUBLE_LEAF_OPEN)

    for leaf_idx in range(2):
        if leaf_idx == 0:
            hinge_x = cx - door_w / 2.0
            panel_cx = leaf_w / 2.0
            axis = (0.0, 0.0, 1.0)
        else:
            hinge_x = cx + door_w / 2.0
            panel_cx = -leaf_w / 2.0
            axis = (0.0, 0.0, -1.0)
        leaf = model.part(f"door_{i}_{leaf_idx}")
        leaf.visual(
            Box((leaf_w, _DOOR_TH, door_h)),
            origin=Origin(xyz=(panel_cx, 0.0, 0.0)),
            material=mats["door"],
            name=f"door_panel_{i}_{leaf_idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        # surface visuals on each leaf (vent + plate scaled to leaf width).
        _apply_double_leaf_surface(
            leaf,
            i,
            leaf_idx,
            r,
            panel_cx=panel_cx,
            front_y=front_y,
            leaf_w=leaf_w,
            accent_mat=mats["accent"],
            door_mat=mats["door"],
        )
        handle_x = (leaf_w - 0.022) if leaf_idx == 0 else -(leaf_w - 0.022)
        leaf.visual(
            Box((0.016, 0.022, 0.16)),
            origin=Origin(xyz=(handle_x, front_y + 0.011, 0.06)),
            material=mats["latch"],
            name=f"door_handle_{i}_{leaf_idx}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "galvanized_zinc", "two_tone_grey_blue", "weathered_scuffed"} else "metal.stainless_matte"),
        )
        leaf.inertial = Inertial.from_geometry(
            Box((leaf_w, _DOOR_TH, door_h)),
            mass=2.0,
            origin=Origin(xyz=(panel_cx, 0.0, 0.0)),
        )
        model.articulation(
            f"hinge_{i}_{leaf_idx}",
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=leaf,
            origin=Origin(xyz=(hinge_x, door_front_y, lh / 2.0)),
            axis=axis,
            motion_limits=MotionLimits(effort=20.0, velocity=2.0, lower=0.0, upper=leaf_open),
        )
    # latch lives on the LEFT leaf only (sample convention). Its local panel
    # center is +leaf_w/2; the free (meeting) edge is at +leaf_w.
    left_leaf = model.get_part(f"door_{i}_0")
    _apply_latch_on_leaf(
        model,
        left_leaf,
        i,
        r,
        panel_cx=leaf_w / 2.0,
        leaf_w=leaf_w,
        front_y=front_y,
        cx=cx,
        carcass=carcass,
        accent_mat=mats["accent"],
        latch_mat=mats["latch"],
        door_mat=mats["door"],
        steel_mat=mats["latch"],
        brass_mat=mats["brass"],
    )


def _apply_double_leaf_surface(
    leaf,
    i: int,
    leaf_idx: int,
    r: ResolvedContainerLockerConfig,
    *,
    panel_cx: float,
    front_y: float,
    leaf_w: float,
    accent_mat,
    door_mat,
) -> None:
    """Door-surface on one leaf. Uses a leaf-width vent / panel so both leaves
    read as the same family. plate only on the left leaf (sample convention)."""
    door_h = r.door_h
    surface = r.door_surface
    if surface == "louver_vents":
        vent_w = leaf_w * 0.70
        vent_h = 0.075
        vent_z = door_h / 2.0 - 0.085
        vent = VentGrilleGeometry(
            (vent_w, vent_h),
            frame=0.008,
            face_thickness=0.0035,
            duct_depth=0.012,
            duct_wall=0.0025,
            slat_pitch=0.012,
            slat_width=0.008,
            slat_angle_deg=35.0,
            corner_radius=0.003,
            slats=VentGrilleSlats(profile="flat", direction="down"),
            sleeve=VentGrilleSleeve(style="short"),
            center=True,
        )
        leaf.visual(
            mesh_from_geometry(vent, f"vent_{i}_{leaf_idx}"),
            origin=Origin(xyz=(panel_cx, front_y - 0.006, vent_z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=accent_mat,
            name=f"door_vent_{i}_{leaf_idx}", material_class_id=("metal.patterned_sheet_panel" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.patterned_sheet"),
        )
    elif surface == "perforated_mesh_panel":
        mesh_w = leaf_w * 0.72
        mesh_h = door_h * 0.74
        mesh_th = 0.003
        perf = PerforatedPanelGeometry(
            (mesh_w, mesh_h),
            mesh_th,
            hole_diameter=0.012,
            pitch=(0.032, 0.032),
            frame=0.012,
            corner_radius=0.004,
            stagger=False,
            center=True,
        )
        leaf.visual(
            _cached_perforated_mesh(f"leaf_mesh_{leaf_idx}", perf),
            origin=Origin(
                xyz=(panel_cx, front_y + mesh_th / 2.0 - 0.001, 0.065),
                rpy=(-math.pi / 2.0, 0.0, 0.0),
            ),
            material=accent_mat,
            name=f"door_mesh_{i}_{leaf_idx}", material_class_id=("metal.mesh_chainmail" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.patterned_sheet"),
        )
    elif surface == "horizontal_slot_vents":
        slot_count = 8
        slot_w = leaf_w * 0.66
        slot_pitch = 0.022
        slot_start_z = door_h / 2.0 - 0.055
        for j in range(slot_count):
            sz = slot_start_z - j * slot_pitch
            leaf.visual(
                Box((slot_w, 0.005, 0.004)),
                origin=Origin(xyz=(panel_cx, front_y - 0.0025 + 0.001, sz)),
                material=accent_mat,
                name=f"door_slot_{i}_{leaf_idx}_{j}", material_class_id=("metal.patterned_sheet_panel" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.patterned_sheet"),
            )
    elif surface == "solid_smooth_door":
        rib_w, rib_h, inset = 0.012, 0.003, 0.030
        rib_y = front_y + rib_h / 2.0
        h_span = leaf_w - 2.0 * inset
        v_span = door_h - 2.0 * inset
        leaf.visual(
            Box((h_span, rib_h, rib_w)),
            origin=Origin(xyz=(panel_cx, rib_y, door_h / 2.0 - inset - rib_w / 2.0)),
            material=door_mat,
            name=f"rib_top_{i}_{leaf_idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        leaf.visual(
            Box((h_span, rib_h, rib_w)),
            origin=Origin(xyz=(panel_cx, rib_y, -door_h / 2.0 + inset + rib_w / 2.0)),
            material=door_mat,
            name=f"rib_bot_{i}_{leaf_idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        leaf.visual(
            Box((rib_w, rib_h, v_span)),
            origin=Origin(xyz=(panel_cx - leaf_w / 2.0 + inset + rib_w / 2.0, rib_y, 0.0)),
            material=door_mat,
            name=f"rib_left_{i}_{leaf_idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        leaf.visual(
            Box((rib_w, rib_h, v_span)),
            origin=Origin(xyz=(panel_cx + leaf_w / 2.0 - inset - rib_w / 2.0, rib_y, 0.0)),
            material=door_mat,
            name=f"rib_right_{i}_{leaf_idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
    # number plate on the left leaf only.
    if leaf_idx == 0:
        plate = PerforatedPanelGeometry(
            (0.045, 0.030),
            0.0025,
            hole_diameter=0.0030,
            pitch=(0.0110, 0.0110),
            frame=0.005,
            corner_radius=0.002,
        )
        leaf.visual(
            _cached_perforated_mesh("door_plate", plate),
            origin=Origin(xyz=(panel_cx, front_y, door_h / 2.0 - 0.160)),
            material=accent_mat,
            name=f"door_plate_{i}", material_class_id=("metal.mesh_chainmail" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.patterned_sheet"),
        )


def _apply_latch_on_leaf(
    model,
    leaf,
    i: int,
    r: ResolvedContainerLockerConfig,
    *,
    panel_cx: float,
    leaf_w: float,
    front_y: float,
    cx: float,
    carcass,
    accent_mat,
    latch_mat,
    door_mat,
    steel_mat,
    brass_mat,
) -> None:
    """Latch on the left leaf of a double-leaf bay. The leaf's free (meeting)
    edge is at local +leaf_w; the hasp/staple anchors near the meeting edge."""
    door_h = r.door_h
    if r.latch_mechanism == "keypad_buttons":
        _emit_keypad(
            model,
            leaf,
            i,
            r,
            pad_cx=panel_cx,
            pad_cz=-door_h / 2.0 + 0.110,
            plate_front_y=front_y + 0.003,
            btn_front_y=front_y + 0.006,
            accent_mat=accent_mat,
            latch_mat=latch_mat,
        )
    elif r.latch_mechanism == "padlock_hasp":
        free_local_x = leaf_w - 0.010  # near meeting edge of left leaf
        hasp_x = free_local_x - _HASP_SETBACK
        leaf.visual(
            Box((_HASP_W + 0.012, 0.006, 0.028)),
            origin=Origin(xyz=(hasp_x, front_y + 0.003, 0.0)),
            material=accent_mat,
            name=f"hasp_bracket_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        hasp = model.part(f"hasp_{i}")
        hasp.visual(
            _hasp_arm_mesh(i),
            origin=Origin(xyz=(0.0, 0.0, -_HASP_L / 2.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=steel_mat,
            name=f"hasp_arm_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "galvanized_zinc", "two_tone_grey_blue", "weathered_scuffed"} else "metal.stainless_matte"),
        )
        hasp.inertial = Inertial.from_geometry(
            Box((_HASP_W, _HASP_TH, _HASP_L)),
            mass=0.08,
            origin=Origin(xyz=(0.0, 0.0, -_HASP_L / 2.0)),
        )
        model.articulation(
            f"hasp_{i}",
            ArticulationType.REVOLUTE,
            parent=leaf,
            child=hasp,
            origin=Origin(xyz=(hasp_x, front_y + 0.006, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=5.0, velocity=1.5, lower=0.0, upper=math.radians(90.0)
            ),
        )
        # staple on carcass near the bay centerline (where the left leaf meets).
        staple_x = cx - _CENTER_GAP / 2.0 - 0.010
        staple_z = r.locker_h / 2.0 - _HASP_L + _SLOT_OFFSET
        # Center astragal post: a thin full-height carcass strip behind the two
        # leaves at the meeting line. It carries the staple/padlock (otherwise
        # the staple would float at the open centerline) and is the realistic
        # center post a double-leaf locker's hasp engages.
        carcass.visual(
            Box((_WALL, _WALL, r.locker_h - 2 * _WALL)),
            origin=Origin(xyz=(staple_x, _LOCKER_D / 2.0 - _WALL / 2.0, r.locker_h / 2.0)),
            material=accent_mat,
            name=f"astragal_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        _emit_padlock_staple(
            carcass, i, staple_x, staple_z, steel_mat=steel_mat, brass_mat=brass_mat
        )
    elif r.latch_mechanism == "rotary_combo_dial":
        _apply_dial(
            model,
            leaf,
            i,
            r,
            dial_cx=panel_cx,
            dial_cz=-door_h / 2.0 + 0.110,
            front_y=front_y,
            accent_mat=accent_mat,
            latch_mat=latch_mat,
        )


def _apply_dial(
    model,
    parent,
    i: int,
    r: ResolvedContainerLockerConfig,
    *,
    dial_cx: float,
    dial_cz: float,
    front_y: float,
    accent_mat,
    latch_mat,
) -> None:
    housing_torus = TorusGeometry(
        radius=(_HOUSING_R + _DIAL_R) / 2.0,
        tube=(_HOUSING_R - _DIAL_R) / 2.0 + 0.002,
        radial_segments=12,
        tubular_segments=28,
    ).rotate_x(math.pi / 2.0)
    parent.visual(
        mesh_from_geometry(housing_torus, f"dial_housing_{i}"),
        origin=Origin(xyz=(dial_cx, front_y - 0.002, dial_cz)),
        material=accent_mat,
        name=f"dial_housing_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    recess_disk = CylinderGeometry(_HOUSING_R, _HOUSING_DEPTH, radial_segments=28).rotate_x(
        math.pi / 2.0
    )
    parent.visual(
        mesh_from_geometry(recess_disk, f"dial_recess_{i}"),
        origin=Origin(xyz=(dial_cx, front_y - _HOUSING_DEPTH / 2.0, dial_cz)),
        material=accent_mat,
        name=f"dial_recess_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    dial = model.part(f"dial_{i}")
    knob = KnobGeometry(
        _DIAL_R * 2.0,
        _DIAL_HEIGHT,
        body_style="cylindrical",
        skirt=KnobSkirt(_DIAL_R * 2.0 + 0.004, 0.003, flare=0.0, chamfer=0.001),
        grip=KnobGrip(style="knurled", count=48, depth=0.0008, helix_angle_deg=25.0),
        indicator=KnobIndicator(style="line", mode="engraved", depth=0.0006),
        center=False,
    )
    dial.visual(
        mesh_from_geometry(knob, f"dial_knob_{i}"),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=latch_mat,
        name=f"dial_knob_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "galvanized_zinc", "two_tone_grey_blue", "weathered_scuffed"} else "metal.stainless_matte"),
    )
    dial.inertial = Inertial.from_geometry(
        Box((_DIAL_R * 2.0, _DIAL_HEIGHT, _DIAL_R * 2.0)), mass=0.030
    )
    model.articulation(
        f"dialjoint_{i}",
        ArticulationType.REVOLUTE,
        parent=parent,
        child=dial,
        origin=Origin(xyz=(dial_cx, front_y + 0.001, dial_cz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=math.pi * 2.0),
    )


def _build_sliding_bay(
    model,
    carcass,
    i: int,
    cx: float,
    r: ResolvedContainerLockerConfig,
    *,
    mats,
) -> None:
    door_w, door_h, lh, lw = r.door_w, r.door_h, r.locker_h, r.locker_w
    carcass_front_y = _LOCKER_D / 2.0
    front_y = _DOOR_TH / 2.0
    slide_dirs, slide_planes = _slide_dirs_and_planes(r.bank_count)
    slide_dir = slide_dirs[i]
    slide_dist = lw * r.slide_travel_scale
    # clear-opening inequality: slide must fully clear the bay opening.
    slide_dist = max(slide_dist, lw)

    # Multi-track bypass: doors whose rest+target slide intervals overlap ride
    # on distinct front planes (_slide_dirs_and_planes) so a door sliding across
    # a neighbour bay passes clear of the neighbour's door and its proud
    # keypad/pull instead of colliding with it. The door child frame stays at
    # its local origin; the slide joint carries the plane offset. Each bay's
    # guide rail is a DEEP channel that spans from the carcass facade out to
    # this bay's door plane, so the proud door still physically rests on
    # carcass sheet metal (find_unsupported_parts wants the door's
    # connected-component rooted) while the rail's back stays welded to the
    # carcass body (no in-part island).
    bay_plane = slide_planes[i] * (_DOOR_TH + 0.022)
    door_y = carcass_front_y + bay_plane

    # guide rails on the carcass: back at the facade, front reaching the door.
    track_len = slide_dist + door_w
    track_cx = cx + slide_dir * (slide_dist / 2.0)
    track_depth = _TRACK_D + bay_plane
    track_y = carcass_front_y + track_depth / 2.0
    carcass.visual(
        Box((track_len, track_depth, _TRACK_H)),
        origin=Origin(xyz=(track_cx, track_y, lh - _WALL - _TRACK_H / 2.0)),
        material=mats["accent"],
        name=f"track_top_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    carcass.visual(
        Box((track_len, track_depth, _TRACK_H)),
        origin=Origin(xyz=(track_cx, track_y, _WALL + _TRACK_H / 2.0)),
        material=mats["accent"],
        name=f"track_bottom_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )

    door = model.part(f"door_{i}")
    door.visual(
        Box((door_w, _DOOR_TH, door_h)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["door"],
        name=f"door_panel_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    _apply_door_surface(
        door,
        i,
        r,
        face_cx=0.0,
        front_y=front_y,
        accent_mat=mats["accent"],
        carcass_mat=mats["carcass"],
        door_mat=mats["door"],
    )
    # Sliding doors use a near-flush recessed pull (not a proud bar): a proud
    # handle would poke forward into the bypass gap and clip the neighbour door
    # on the plane in front. Kept minimal-protrusion so the parity plane offset
    # clears both panels and pulls.
    handle_x = -slide_dir * (door_w / 2.0 - 0.030)
    door.visual(
        Box((0.016, 0.006, 0.16)),
        origin=Origin(xyz=(handle_x, front_y + 0.002, 0.06)),
        material=mats["latch"],
        name=f"door_handle_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "galvanized_zinc", "two_tone_grey_blue", "weathered_scuffed"} else "metal.stainless_matte"),
    )
    door.inertial = Inertial.from_geometry(
        Box((door_w, _DOOR_TH, door_h)),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    # Mid-height carcass face mullion at the bay center: a thin vertical sheet-
    # metal strip behind the door on the front plane. It gives the slide joint
    # origin real parent geometry to sit on at the bay-center front, and reads
    # as the locker face frame behind the sliding panel.
    carcass.visual(
        Box((_WALL, _WALL, lh - 2 * _WALL)),
        origin=Origin(xyz=(cx, carcass_front_y - _WALL / 2.0, lh / 2.0)),
        material=mats["carcass"],
        name=f"face_mullion_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    # Slide joint origin sits on that face mullion (real carcass sheet metal at
    # the bay-center front mid-height); the door child frame already contains
    # its panel at the origin so the door stays centered.
    model.articulation(
        f"slide_{i}",
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=door,
        origin=Origin(xyz=(cx, door_y, lh / 2.0)),
        axis=(float(slide_dir), 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.5, lower=0.0, upper=slide_dist),
    )
    _apply_latch_on_door(
        model,
        door,
        i,
        r,
        face_cx=0.0,
        front_y=front_y,
        cx=cx,
        carcass=carcass,
        accent_mat=mats["accent"],
        latch_mat=mats["latch"],
        door_mat=mats["door"],
        steel_mat=mats["latch"],
        brass_mat=mats["brass"],
    )


def _build_slat_cq(slat_w: float, slat_d: float, slat_h: float, bulge: float):
    hd = slat_d / 2.0
    hh = slat_h / 2.0
    return (
        cq.Workplane("YZ")
        .moveTo(-hd, -hh)
        .lineTo(hd, -hh)
        .lineTo(hd + bulge, 0.0)
        .lineTo(hd, hh)
        .lineTo(-hd, hh)
        .close()
        .extrude(slat_w)
    )


def _build_shutter_bay(
    model,
    carcass,
    i: int,
    cx: float,
    r: ResolvedContainerLockerConfig,
    *,
    mats,
) -> None:
    lw, ld, lh = r.locker_w, _LOCKER_D, r.locker_h
    carcass_front_y = ld / 2.0
    shutter_w = lw - 2 * _WALL - 2 * _GUIDE_W
    opening_bottom_z = 0.160 * r.bank_height_scale
    opening_top_z = lh - _WALL - _HEAD_BOX_H
    opening_h = max(opening_top_z - opening_bottom_z, 0.30)
    n_slats = int(opening_h / _SLAT_PITCH)
    n_slats = max(n_slats, 8)
    slat_stack_h = n_slats * _SLAT_PITCH
    # shutter travel: leave ~4 slats visible; clamp so it never exceeds stack.
    travel = (n_slats - 4) * _SLAT_PITCH * r.slide_travel_scale
    travel = _clamp(travel, _SLAT_PITCH, slat_stack_h - _SLAT_PITCH)

    # front panel below opening
    fp_bottom = 0.030
    fp_h = opening_bottom_z - fp_bottom
    if fp_h > 0.005:
        carcass.visual(
            Box((lw - 2 * _WALL, _WALL, fp_h)),
            origin=Origin(xyz=(cx, carcass_front_y - _WALL / 2.0, fp_bottom + fp_h / 2.0)),
            material=mats["carcass"],
            name=f"front_panel_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
    # head box panel above opening
    hb_cz = opening_top_z + _HEAD_BOX_H / 2.0
    carcass.visual(
        Box((lw - 2 * _WALL, _WALL, _HEAD_BOX_H)),
        origin=Origin(xyz=(cx, carcass_front_y - _WALL / 2.0, hb_cz)),
        material=mats["carcass"],
        name=f"head_box_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    # guide channels
    guide_cz = opening_bottom_z + opening_h / 2.0
    for side_sign, side_name in [(-1, "l"), (1, "r")]:
        gx = cx + side_sign * (lw / 2.0 - _WALL - _GUIDE_W / 2.0)
        carcass.visual(
            Box((_GUIDE_W, _GUIDE_DEPTH, opening_h + _HEAD_BOX_H)),
            origin=Origin(xyz=(gx, carcass_front_y, guide_cz + _HEAD_BOX_H / 2.0)),
            material=mats["accent"],
            name=f"guide_{side_name}_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )

    # shutter part: corrugated slats + backing strip + handle
    shutter = model.part(f"shutter_{i}")
    slat_shape = _build_slat_cq(shutter_w, _SLAT_D, _SLAT_H, _SLAT_BULGE)
    slat_mesh = mesh_from_cadquery(slat_shape, f"slat_{i}")
    for j in range(n_slats):
        slat_z = j * _SLAT_PITCH + _SLAT_H / 2.0
        shutter.visual(
            slat_mesh,
            origin=Origin(xyz=(-shutter_w / 2.0, 0.0, slat_z)),
            material=mats["door"],
            name=f"slat_{i}_{j}", material_class_id=("metal.patterned_sheet_panel" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.patterned_sheet"),
        )
    strip_th = 0.003
    shutter.visual(
        Box((shutter_w * 0.92, strip_th, slat_stack_h)),
        origin=Origin(xyz=(0.0, -_SLAT_D / 2.0 + strip_th / 2.0, slat_stack_h / 2.0)),
        material=mats["accent"],
        name=f"curtain_strip_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    handle_y = _SLAT_D / 2.0 + _SLAT_BULGE + 0.020 / 2.0
    shutter.visual(
        Box((0.100, 0.020, 0.016)),
        origin=Origin(xyz=(0.0, handle_y, _SLAT_H * 0.40)),
        material=mats["latch"],
        name=f"handle_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "galvanized_zinc", "two_tone_grey_blue", "weathered_scuffed"} else "metal.stainless_matte"),
    )
    shutter.inertial = Inertial.from_geometry(
        Box((shutter_w, _SLAT_D, slat_stack_h)),
        mass=6.0,
        origin=Origin(xyz=(0.0, 0.0, slat_stack_h / 2.0)),
    )
    model.articulation(
        f"slide_{i}",
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=shutter,
        origin=Origin(xyz=(cx, carcass_front_y, opening_bottom_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.30, lower=0.0, upper=travel),
    )

    # latch on the carcass front panel (door is the curtain). Mount at the
    # lower front panel.
    pad_cz = max(0.100, fp_bottom + 0.060)
    if r.latch_mechanism == "keypad_buttons":
        plate_front_y = carcass_front_y + 0.003
        _emit_keypad(
            model,
            carcass,
            i,
            r,
            pad_cx=cx,
            pad_cz=pad_cz,
            plate_front_y=plate_front_y,
            btn_front_y=carcass_front_y + 0.006,
            accent_mat=mats["accent"],
            latch_mat=mats["latch"],
        )
    elif r.latch_mechanism == "padlock_hasp":
        # hasp arm hinged on the carcass front panel near the opening edge.
        hasp_x = cx + lw / 2.0 - _WALL - _HASP_SETBACK
        carcass.visual(
            Box((_HASP_W + 0.012, 0.006, 0.028)),
            origin=Origin(xyz=(hasp_x, carcass_front_y + 0.003, pad_cz)),
            material=mats["accent"],
            name=f"hasp_bracket_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
        hasp = model.part(f"hasp_{i}")
        hasp.visual(
            _hasp_arm_mesh(i),
            origin=Origin(xyz=(0.0, 0.0, -_HASP_L / 2.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=mats["latch"],
            name=f"hasp_arm_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "galvanized_zinc", "two_tone_grey_blue", "weathered_scuffed"} else "metal.stainless_matte"),
        )
        hasp.inertial = Inertial.from_geometry(
            Box((_HASP_W, _HASP_TH, _HASP_L)),
            mass=0.08,
            origin=Origin(xyz=(0.0, 0.0, -_HASP_L / 2.0)),
        )
        model.articulation(
            f"hasp_{i}",
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=hasp,
            origin=Origin(xyz=(hasp_x, carcass_front_y + 0.006, pad_cz)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=5.0, velocity=1.5, lower=0.0, upper=math.radians(90.0)
            ),
        )
        staple_x = cx + lw / 2.0 - _WALL - _HASP_SETBACK
        staple_z = pad_cz - _HASP_L + _SLOT_OFFSET
        _emit_padlock_staple(
            carcass, i, staple_x, staple_z, steel_mat=mats["latch"], brass_mat=mats["brass"]
        )
    elif r.latch_mechanism == "rotary_combo_dial":
        _apply_dial(
            model,
            carcass,
            i,
            r,
            dial_cx=cx,
            dial_cz=pad_cz,
            front_y=carcass_front_y,
            accent_mat=mats["accent"],
            latch_mat=mats["latch"],
        )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_locker(
    config: ContainerLockerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    # reset the per-build boolean-mesh cache (perforated panels / plates reused
    # across bays so the boolean is cut once, not N times).
    _MESH_CACHE.clear()

    pal = PALETTES[r.palette_style]
    style = r.palette_style
    mats = {
        "carcass": model.material(f"cl_carcass_{style}", rgba=pal["carcass"]),
        "door": model.material(f"cl_door_{style}", rgba=pal["door"]),
        "latch": model.material(f"cl_latch_{style}", rgba=pal["latch"]),
        "accent": model.material(f"cl_accent_{style}", rgba=pal["accent"]),
        # brass padlock body keeps its identity color but tinted by the palette
        # latch tone toward steel; use a fixed brass anchor so padlocks read.
        "brass": model.material(f"cl_brass_{style}", rgba=(0.72, 0.58, 0.22, 1.0)),
    }

    n = r.bank_count
    lw, ld, lh = r.locker_w, _LOCKER_D, r.locker_h

    # --- ROOT: shared carcass ----------------------------------------------
    carcass = model.part("carcass")
    bank_w = n * lw + 0.004
    carcass.visual(
        Box((bank_w, ld, 0.030)),
        origin=Origin(xyz=(0.0, 0.0, 0.015)),
        material=mats["carcass"],
        name="plinth", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
    )
    for k in range(n - 1):
        div_x = _bay_center_x(k, n, lw) + lw / 2.0
        carcass.visual(
            Box((_WALL, ld, lh)),
            origin=Origin(xyz=(div_x, 0.0, lh / 2.0)),
            material=mats["carcass"],
            name=f"divider_{k}", material_class_id=("metal.paint_coated" if r.palette_style in {"locker_offwhite", "battleship_grey", "locker_blue", "forest_green", "tan_beige", "gloss_red_enamel", "brushed_stainless", "galvanized_zinc", "two_tone_grey_blue"} else "rust.painted_weathered"),
        )
    carcass.inertial = Inertial.from_geometry(
        Box((bank_w, ld, lh)),
        mass=15.0 * n,
        origin=Origin(xyz=(0.0, 0.0, lh / 2.0)),
    )

    # per-bay carcass panels (single range loop, multiplicity contract)
    for i in range(n):
        cx = _bay_center_x(i, n, lw)
        _emit_carcass_bay_panels(
            carcass, cx, i, r, carcass_mat=mats["carcass"], accent_mat=mats["accent"]
        )

    # --- closure + door_surface + latch per bay ----------------------------
    builder = {
        "hinged_single_door": _build_hinged_bay,
        "double_leaf_doors": _build_double_leaf_bay,
        "sliding_door": _build_sliding_bay,
        "roll_down_shutter": _build_shutter_bay,
    }[r.closure_mechanism]
    for i in range(n):
        cx = _bay_center_x(i, n, lw)
        builder(model, carcass, i, cx, r, mats=mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_locker(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_locker(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (door seated reveal, shutter in guides,
# buttons in keypad plate, padlock on staple) are declared element-scoped so
# the sweep's island/overlap checks pass; the mechanisms are exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_locker_tests(
    object_model: ArticulatedObject,
    config: ContainerLockerConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    carcass = object_model.get_part("carcass")
    n = r.bank_count

    # ---- carcass rests on the ground, bank centered on x=0 ----
    aabb = ctx.part_world_aabb(carcass)
    ctx.check(
        "carcass rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.012,
        details=f"carcass min z={aabb[0][2]:.4f}",
    )

    # ---- N-1 dividers exist ----
    for k in range(n - 1):
        ctx.check(
            f"divider_{k} exists between bays",
            carcass.get_visual(f"divider_{k}") is not None,
            details=f"divider_{k}",
        )

    # ---- closure mechanism per bay ----
    closure = r.closure_mechanism
    if closure == "hinged_single_door":
        for i in range(n):
            door = object_model.get_part(f"door_{i}")
            hinge = object_model.get_articulation(f"hinge_{i}")
            # The opened door swings clear of the carcass front.
            ctx.allow_isolated_part(
                door,
                reason="opened locker door swings clear of the carcass front",
            )
            for btn in (p for p in object_model.parts if p.name.startswith(f"lockbtn_{i}_")):
                ctx.allow_isolated_part(
                    btn,
                    reason="lock button rides on the locker door and swings away with it",
                )
            # the latch hardware is joint-retained on the door: once the door
            # swings open the whole door+latch group leaves carcass contact.
            for ridden in (p for p in object_model.parts if p.name in (f"hasp_{i}", f"dial_{i}")):
                ctx.allow_isolated_part(
                    ridden,
                    reason="latch hardware rides on the locker door and swings away with it",
                )
            ctx.allow_overlap(
                door,
                carcass,
                reason="Door panel overlaps the carcass front at the hinge reveal (seated fit).",
            )
            ctx.check(
                f"hinge_{i} is REVOLUTE about +Z",
                hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[2]) > 0.99,
                details=f"axis={hinge.axis}, type={hinge.articulation_type}",
            )
            closed_y = ctx.part_world_aabb(door)[1][1]
            with ctx.pose({hinge: math.radians(90.0)}):
                open_y = ctx.part_world_aabb(door)[1][1]
            ctx.check(
                f"door_{i} free edge swings out when opened",
                open_y > closed_y + 0.08,
                details=f"closed_max_y={closed_y:.4f}, open_max_y={open_y:.4f}",
            )
    elif closure == "double_leaf_doors":
        for i in range(n):
            for leaf_idx in range(2):
                leaf = object_model.get_part(f"door_{i}_{leaf_idx}")
                hinge = object_model.get_articulation(f"hinge_{i}_{leaf_idx}")
                # The opened leaf swings clear of the carcass front.
                ctx.allow_isolated_part(
                    leaf,
                    reason="opened locker leaf swings clear of the carcass front",
                )
                for dial in (p for p in object_model.parts if p.name in (f"dial_{i}", f"hasp_{i}")):
                    ctx.allow_isolated_part(
                        dial,
                        reason="latch hardware rides on the locker leaf and swings away with it",
                    )
                ctx.allow_overlap(
                    leaf,
                    carcass,
                    reason="Door leaf overlaps the carcass front at the hinge reveal (seated fit).",
                )
                ctx.check(
                    f"hinge_{i}_{leaf_idx} is REVOLUTE about +/-Z",
                    hinge.articulation_type == ArticulationType.REVOLUTE
                    and abs(hinge.axis[2]) > 0.99,
                    details=f"axis={hinge.axis}",
                )
                closed_y = ctx.part_world_aabb(leaf)[1][1]
                with ctx.pose({hinge: math.radians(90.0)}):
                    open_y = ctx.part_world_aabb(leaf)[1][1]
                ctx.check(
                    f"door_{i}_{leaf_idx} swings outward when opened",
                    open_y > closed_y + 0.04,
                    details=f"closed={closed_y:.4f}, open={open_y:.4f}",
                )
            # keypad buttons ride on the left leaf and swing away with it.
            for btn in (p for p in object_model.parts if p.name.startswith(f"lockbtn_{i}_")):
                ctx.allow_isolated_part(
                    btn,
                    reason="lock button rides on the locker leaf and swings away with it",
                )
    elif closure == "sliding_door":
        for i in range(n):
            door = object_model.get_part(f"door_{i}")
            slide = object_model.get_articulation(f"slide_{i}")
            ctx.allow_overlap(
                door,
                carcass,
                reason="Sliding door rides in front of the carcass / on its track rails (seated fit).",
            )
            ctx.check(
                f"slide_{i} is PRISMATIC about +/-X",
                slide.articulation_type == ArticulationType.PRISMATIC and abs(slide.axis[0]) > 0.99,
                details=f"axis={slide.axis}, type={slide.articulation_type}",
            )
            closed = ctx.part_world_position(door)
            travel = slide.motion_limits.upper
            with ctx.pose({slide: travel}):
                opened = ctx.part_world_position(door)
            ctx.check(
                f"door_{i} slides clear of the bay opening",
                closed is not None
                and opened is not None
                and abs(opened[0] - closed[0]) > r.locker_w * 0.85,
                details=f"closed={closed}, open={opened}",
            )
    elif closure == "roll_down_shutter":
        for i in range(n):
            shutter = object_model.get_part(f"shutter_{i}")
            slide = object_model.get_articulation(f"slide_{i}")
            ctx.allow_overlap(
                shutter,
                carcass,
                reason="Shutter slats ride inside the carcass guide channels and stack into the head box.",
            )
            ctx.check(
                f"slide_{i} is PRISMATIC about +Z",
                slide.articulation_type == ArticulationType.PRISMATIC and abs(slide.axis[2]) > 0.99,
                details=f"axis={slide.axis}, type={slide.articulation_type}",
            )
            rest_z = ctx.part_world_position(shutter)[2]
            travel = slide.motion_limits.upper
            with ctx.pose({slide: travel}):
                up_z = ctx.part_world_position(shutter)[2]
            ctx.check(
                f"shutter_{i} slides up when opened",
                up_z > rest_z + travel * 0.8,
                details=f"rest_z={rest_z:.4f}, up_z={up_z:.4f}",
            )

    # ---- bays are side by side along X ----
    if n >= 2:
        if closure == "double_leaf_doors":
            p0 = ctx.part_world_position(object_model.get_part("door_0_0"))
            p1 = ctx.part_world_position(object_model.get_part("door_1_0"))
        elif closure == "roll_down_shutter":
            p0 = ctx.part_world_position(object_model.get_part("shutter_0"))
            p1 = ctx.part_world_position(object_model.get_part("shutter_1"))
        else:
            p0 = ctx.part_world_position(object_model.get_part("door_0"))
            p1 = ctx.part_world_position(object_model.get_part("door_1"))
        ctx.check(
            "adjacent bays offset side by side along X",
            p0 is not None and p1 is not None and abs((p1[0] - p0[0]) - r.locker_w) < 0.03,
            details=f"bay0={p0}, bay1={p1}",
        )

    # ---- latch mechanism per bay ----
    latch = r.latch_mechanism

    # the parent that carries the latch on each bay.
    def _latch_parent(i: int):
        if not r.latch_on_door:
            return carcass
        if closure == "double_leaf_doors":
            return object_model.get_part(f"door_{i}_0")
        return object_model.get_part(f"door_{i}")

    if latch == "keypad_buttons":
        for i in range(n):
            parent = _latch_parent(i)
            # Every push-button is a rigid child of the keypad plate: its base is
            # seated into the plate and it co-rotates with the door, so the
            # button<->plate contact is a constant seated interface with no
            # relative sweep (FCL clearance is 0 at every hinge angle). The
            # motion-QC AABB pre-filter only trips it once the whole assembly
            # swings, so declare the seat for all buttons, not just the probed one.
            for b in range(_BTN_COLS * _BTN_ROWS):
                ctx.allow_overlap(
                    object_model.get_part(f"lockbtn_{i}_{b}"),
                    parent,
                    reason=(
                        "Push-button base is seated into the lock keypad plate and "
                        "co-rotates with the door (constant seated contact)."
                    ),
                )
            btn = object_model.get_part(f"lockbtn_{i}_3")
            btnjoint = object_model.get_articulation(f"btnjoint_{i}_3")
            ctx.check(
                f"btnjoint_{i}_3 is PRISMATIC about -Y",
                btnjoint.articulation_type == ArticulationType.PRISMATIC
                and btnjoint.axis[1] < -0.99,
                details=f"axis={btnjoint.axis}",
            )
            rest = ctx.part_world_position(btn)
            with ctx.pose({btnjoint: r.btn_press}):
                pressed = ctx.part_world_position(btn)
            ctx.check(
                f"lockbtn_{i}_3 presses straight in",
                rest is not None
                and pressed is not None
                and (rest[1] - pressed[1]) > r.btn_press * 0.7,
                details=f"rest={rest}, pressed={pressed}",
            )
    elif latch == "padlock_hasp":
        for i in range(n):
            parent = _latch_parent(i)
            hasp = object_model.get_part(f"hasp_{i}")
            hasp_joint = object_model.get_articulation(f"hasp_{i}")
            ctx.allow_overlap(
                hasp,
                carcass,
                reason="Hasp arm slot fits over the staple legs on the carcass (engaged-lock interface).",
            )
            ctx.allow_overlap(
                hasp,
                parent,
                reason="Hasp arm is hinged on its bracket on the parent face (seated fit).",
            )
            ctx.check(
                f"hasp_{i} is REVOLUTE about +X",
                hasp_joint.articulation_type == ArticulationType.REVOLUTE
                and abs(hasp_joint.axis[0]) > 0.99,
                details=f"axis={hasp_joint.axis}",
            )
            rest_aabb = ctx.part_world_aabb(hasp)
            with ctx.pose({hasp_joint: math.radians(80.0)}):
                swung_aabb = ctx.part_world_aabb(hasp)
            ctx.check(
                f"hasp_{i} arm swings up/out when disengaged",
                swung_aabb[0][2] > rest_aabb[0][2] + 0.01,
                details=f"rest_min_z={rest_aabb[0][2]:.4f}, swung_min_z={swung_aabb[0][2]:.4f}",
            )
            ctx.check(
                f"padlock_body_{i} exists on carcass",
                carcass.get_visual(f"padlock_body_{i}") is not None,
            )
    elif latch == "rotary_combo_dial":
        for i in range(n):
            dial = object_model.get_part(f"dial_{i}")
            dialjoint = object_model.get_articulation(f"dialjoint_{i}")
            # The knurled dial knob is seated inside its recessed housing on the
            # door face and is a rigid child of the door: it co-rotates with the
            # door, so knob<->housing is a constant seated contact (FCL clearance
            # 0 at every hinge angle). Declare the seat so the AABB pre-filter's
            # rotation-inflated overlap between them is not misread as a sweep.
            ctx.allow_overlap(
                dial,
                _latch_parent(i),
                reason=(
                    "Dial knob is seated in its recessed door-face housing and "
                    "co-rotates with the door (constant seated contact)."
                ),
            )
            # The dial is an axisymmetric knurled cylinder; a spin about its
            # face-normal does not change its AABB (expected). Assert the
            # articulation semantic instead: a finite-range REVOLUTE about the
            # +Y door face-normal, with the part actually present.
            ctx.check(
                f"dialjoint_{i} is REVOLUTE about +Y (face normal) with finite range",
                dialjoint.articulation_type == ArticulationType.REVOLUTE
                and abs(dialjoint.axis[1]) > 0.99
                and dialjoint.motion_limits is not None
                and dialjoint.motion_limits.upper is not None
                and dialjoint.motion_limits.upper > 0.0,
                details=f"axis={dialjoint.axis}, limits={dialjoint.motion_limits}",
            )
            ctx.check(
                f"dial_{i} knob visual exists",
                dial.get_visual(f"dial_knob_{i}") is not None,
                details=f"dial_{i}",
            )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed count={len(non_fixed)}",
    )

    return ctx.report()
