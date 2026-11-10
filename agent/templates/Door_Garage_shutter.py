# SPDX-License-Identifier: Apache-2.0

"""Garage shutter (residential garage door) modular template.

A fixed steel surround ``frame`` (two jambs/guide-rails + header + floor sill +
two side guide tracks) holds a curtain of horizontal panel leaves that lift on a
+Z PRISMATIC telescoping chain (``slat_{i}`` loop), OR a single full-height slab
that swings up on a REVOLUTE top hinge. These two lift kinematics are mutually
exclusive motion spines.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Door_Garage_shutter.md`` and the 9
five-star ``data/records/rec_(door_)garage_shutter*`` samples (1 parent + 8
slot-fork variants).

Slot graph (pattern = ``mixed``):

  * TYPE (2): ``sectional_telescoping`` (N>=2 leaves, FIXED top leaf + per-link
    +Z PRISMATIC chain) / ``single_tilt_up`` (1 slab, top-header REVOLUTE -X).
    Mutually-exclusive motion spines (parent L227-244 vs tiltup L217-225).
  * N (multiplicity): ``n{N}`` leaf count. Panel-stack domain [3,14]; tilt-up
    collapses N to 1 (parent L59 / n3 / n10 / tiltup L48).
  * SURFACE (4): ``flat_embossed_pillow`` / ``vertical_ribbed`` /
    ``raised_panel_field`` / ``perforated_grille``. Per-leaf face treatment,
    authored as parent visuals on each leaf (Rule 1). The grille keeps its
    ``ExtrudeWithHolesGeometry`` + ``mesh_from_geometry`` perforated sheet
    (NO Box downgrade) plus full-depth ``edge_rail_{0,1}`` contact rails.
  * WINDOW (2): ``no_windows`` / ``divided_lite_top_row`` (top leaf glazed with
    N_WINDOWS recessed lights + mullions + rails; lower leaves keep SURFACE).
  * FRAME (2): ``slim_surround`` (flat black box jambs + flush guide track) /
    ``bold_square_tube_rails`` (90 mm hollow square-tube rails via
    ``ExtrudeWithHolesGeometry`` mesh + visible track channels). Frame is a
    pure ``frame`` part visual swap, orthogonal to the leaf subgraph.

The 3 hard rules are honoured: (1) SURFACE/WINDOW/decorations are ``parent``
visuals on the leaf/frame part, never FIXED child parts; (2) every non-FIXED
joint declares a ``MatingContract`` pinning the two kissing faces; (3) the
grille keeps its mesh primitive and the bold rails keep their hollow-tube mesh.

palette_style (6 realistic finishes) is sampled per seed and drives every
``.visual`` material.
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
    ExtrudeWithHolesGeometry,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
LiftType = Literal["sectional_telescoping", "single_tilt_up"]
Surface = Literal[
    "flat_embossed_pillow",
    "vertical_ribbed",
    "raised_panel_field",
    "perforated_grille",
]
WindowChoice = Literal["no_windows", "divided_lite_top_row"]
FrameChoice = Literal["slim_surround", "bold_square_tube_rails"]
PaletteStyle = Literal[
    "grey_steel",
    "white",
    "black_framed",
    "dark_bronze",
    "galvanized_silver",
    "cream_almond",
]

LIFT_TYPES: tuple[LiftType, ...] = ("sectional_telescoping", "single_tilt_up")
SURFACES: tuple[Surface, ...] = (
    "flat_embossed_pillow",
    "vertical_ribbed",
    "raised_panel_field",
    "perforated_grille",
)
WINDOW_CHOICES: tuple[WindowChoice, ...] = ("no_windows", "divided_lite_top_row")
FRAME_CHOICES: tuple[FrameChoice, ...] = ("slim_surround", "bold_square_tube_rails")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "grey_steel",
    "white",
    "black_framed",
    "dark_bronze",
    "galvanized_silver",
    "cream_almond",
)

# Panel-stack multiplicity domain (spec §参数范围 / Multiplicity).
N_MIN = 3
N_MAX = 14
# Weighted draw: 3-6 high-freq (residential sectional), 7-10 common (narrow
# rollerlike slats), 11-14 long tail. N=1 belongs to single_tilt_up only.
_N_BUCKETS = ((3, 6), (7, 10), (11, 14))
_N_BUCKET_WEIGHTS = (0.60, 0.30, 0.10)

# Sampling weights: panel-stack dominant, tilt-up is the rarer spine.
_TYPE_WEIGHTS = (0.78, 0.22)

# ---------------------------------------------------------------------------
# Palette: 6 realistic garage-door finishes. Every key drives a .visual mat.
# Derived from the parent material table (parent L94-99): panel / pillow /
# rib / raised / groove / track / handle / glass / mullion + the black frame.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "grey_steel": {
        "frame": (0.09, 0.09, 0.095, 1.0),
        "panel": (0.50, 0.505, 0.51, 1.0),
        "pillow": (0.54, 0.545, 0.55, 1.0),
        "raised": (0.56, 0.565, 0.57, 1.0),
        "groove": (0.30, 0.305, 0.31, 1.0),
        "track": (0.40, 0.41, 0.42, 1.0),
        "handle": (0.13, 0.13, 0.14, 1.0),
        "glass": (0.32, 0.40, 0.46, 0.75),
        "mullion": (0.42, 0.43, 0.44, 1.0),
    },
    "white": {
        "frame": (0.16, 0.16, 0.17, 1.0),
        "panel": (0.92, 0.92, 0.91, 1.0),
        "pillow": (0.96, 0.96, 0.95, 1.0),
        "raised": (0.97, 0.97, 0.96, 1.0),
        "groove": (0.70, 0.70, 0.69, 1.0),
        "track": (0.62, 0.63, 0.64, 1.0),
        "handle": (0.20, 0.20, 0.21, 1.0),
        "glass": (0.40, 0.48, 0.54, 0.72),
        "mullion": (0.82, 0.82, 0.81, 1.0),
    },
    "black_framed": {
        "frame": (0.04, 0.04, 0.045, 1.0),
        "panel": (0.13, 0.13, 0.14, 1.0),
        "pillow": (0.17, 0.17, 0.18, 1.0),
        "raised": (0.19, 0.19, 0.20, 1.0),
        "groove": (0.05, 0.05, 0.055, 1.0),
        "track": (0.30, 0.31, 0.32, 1.0),
        "handle": (0.62, 0.63, 0.64, 1.0),
        "glass": (0.22, 0.28, 0.33, 0.78),
        "mullion": (0.10, 0.10, 0.11, 1.0),
    },
    "dark_bronze": {
        "frame": (0.10, 0.08, 0.06, 1.0),
        "panel": (0.27, 0.21, 0.15, 1.0),
        "pillow": (0.31, 0.24, 0.17, 1.0),
        "raised": (0.34, 0.26, 0.18, 1.0),
        "groove": (0.15, 0.11, 0.08, 1.0),
        "track": (0.36, 0.30, 0.23, 1.0),
        "handle": (0.46, 0.40, 0.30, 1.0),
        "glass": (0.30, 0.33, 0.30, 0.74),
        "mullion": (0.24, 0.19, 0.13, 1.0),
    },
    "galvanized_silver": {
        "frame": (0.34, 0.35, 0.37, 1.0),
        "panel": (0.66, 0.67, 0.69, 1.0),
        "pillow": (0.72, 0.73, 0.75, 1.0),
        "raised": (0.75, 0.76, 0.78, 1.0),
        "groove": (0.46, 0.47, 0.49, 1.0),
        "track": (0.55, 0.56, 0.58, 1.0),
        "handle": (0.24, 0.25, 0.26, 1.0),
        "glass": (0.40, 0.46, 0.52, 0.72),
        "mullion": (0.58, 0.59, 0.61, 1.0),
    },
    "cream_almond": {
        "frame": (0.30, 0.27, 0.22, 1.0),
        "panel": (0.88, 0.83, 0.72, 1.0),
        "pillow": (0.92, 0.87, 0.76, 1.0),
        "raised": (0.94, 0.89, 0.78, 1.0),
        "groove": (0.64, 0.59, 0.49, 1.0),
        "track": (0.60, 0.57, 0.50, 1.0),
        "handle": (0.34, 0.30, 0.24, 1.0),
        "glass": (0.44, 0.50, 0.52, 0.72),
        "mullion": (0.78, 0.73, 0.62, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Shared frame skeleton across all 9
# sources: a near-square ~2.4 m x ~2.13 m residential door.
# ---------------------------------------------------------------------------
_DOOR_W = 2.40  # nominal overall frame outer width
_JAMB_W = 0.06  # slim side jamb width
_JAMB_D = 0.12  # frame depth (front-to-back, Y)
_HEADER_H = 0.06  # top header height
_THRESHOLD_H = 0.05  # floor sill height

_SLAT_D = 0.04  # leaf thickness (Y) = per-leaf depth stagger
_SLAT_LAP = 0.020  # vertical lap (leaf top tucks behind leaf above)
_GROOVE_H = 0.018  # recessed seam-groove height

# Header clearance kept by a fully-raised lower leaf. A non-top leaf is
# pitch+lap tall; raising it a full pitch would push its lap tuck one lap above
# the FIXED top leaf's top edge (= header underside) and punch through the
# lintel. Travel per telescoping link is therefore pitch-lap minus this margin,
# so every leaf's top stays >= _HEADER_CLEAR below the header in any combined
# raised pose (see ResolvedGarageShutterConfig.lift_travel).
_HEADER_CLEAR = 0.008

_RAIL_SIZE = 0.09  # bold square-tube rail cross section
_RAIL_WALL = 0.005  # tube wall thickness

# Grille parameters (grille source L74-77). Mesh primitive, NOT downgraded.
_GRILLE_THICKNESS = 0.005
_GRILLE_HOLE_SIZE = 0.065
_GRILLE_PITCH = 0.090
_GRILLE_FRAME_W = 0.018
_RAIL_W = 0.028  # grille structural edge-rail width

# Window parameters (window_row source L74-80).
_WIN_RECESS = 0.014
_WIN_GLASS_T = 0.005
_MULLION_W = 0.030
_WIN_RAIL_H = 0.025


@dataclass(frozen=True)
class GarageShutterConfig:
    lift_type: LiftType | None = None
    n_slats: int | None = None
    surface: Surface | None = None
    window: WindowChoice | None = None
    frame: FrameChoice | None = None
    palette_style: PaletteStyle = "grey_steel"
    n_windows: int = 5
    n_ribs: int = 5
    opening_w_scale: float = 1.0
    opening_h_scale: float = 1.0
    slat_lap: float = _SLAT_LAP
    slat_depth_scale: float = 1.0
    jamb_w_scale: float = 1.0
    tilt_open_angle: float = 1.3
    name: str = "garage_shutter"


@dataclass(frozen=True)
class ResolvedGarageShutterConfig:
    lift_type: LiftType
    n_slats: int
    surface: Surface
    window: WindowChoice
    frame: FrameChoice
    palette_style: PaletteStyle
    n_windows: int
    n_ribs: int
    # concrete geometry
    door_w: float
    jamb_w: float
    jamb_d: float
    opening_w: float
    opening_h: float
    slat_pitch: float
    slat_lap: float
    slat_d: float
    slat_w: float
    threshold_h: float
    header_h: float
    panel_base_z: float
    frame_front_y: float
    panel_front_y: float
    rail_size: float
    tilt_open_angle: float
    name: str

    @property
    def stack_back_y(self) -> float:
        # back face of the deepest leaf (panel-stack); tilt-up uses N=1 here too.
        n = self.n_slats
        return self.panel_front_y + n * self.slat_d

    @property
    def hinge_z(self) -> float:
        return self.panel_base_z + self.opening_h

    @property
    def lift_travel(self) -> float:
        """Per-link telescoping travel that keeps every raised leaf below the
        header. A non-top leaf spans pitch+lap, so at a full-pitch rise its lap
        tuck would clear the top leaf by exactly ``lap`` and punch the lintel;
        travel = pitch - lap - _HEADER_CLEAR keeps leaf i top at
        opening_h - i*(lap+clear) + lap <= opening_h - _HEADER_CLEAR."""
        return max(0.02, self.slat_pitch - self.slat_lap - _HEADER_CLEAR)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Procedural sampling (Contract 4): deterministic per seed, seed 0 not special.
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> GarageShutterConfig:
    rng = random.Random(seed)
    lift_type = rng.choices(LIFT_TYPES, weights=_TYPE_WEIGHTS, k=1)[0]
    if lift_type == "single_tilt_up":
        n_slats = 1
    else:
        lo, hi = rng.choices(_N_BUCKETS, weights=_N_BUCKET_WEIGHTS, k=1)[0]
        n_slats = rng.randint(lo, hi)
    return GarageShutterConfig(
        lift_type=lift_type,
        n_slats=n_slats,
        surface=rng.choice(SURFACES),
        window=rng.choice(WINDOW_CHOICES),
        frame=rng.choice(FRAME_CHOICES),
        palette_style=rng.choice(PALETTE_STYLES),
        n_windows=rng.randint(3, 6),
        n_ribs=rng.randint(3, 7),
        opening_w_scale=round(rng.uniform(0.85, 1.15), 4),
        opening_h_scale=round(rng.uniform(0.85, 1.20), 4),
        slat_lap=round(rng.uniform(0.012, 0.025), 4),
        slat_depth_scale=round(rng.uniform(0.9, 1.2), 4),
        jamb_w_scale=round(rng.uniform(0.8, 1.4), 4),
        tilt_open_angle=round(rng.uniform(1.0, 1.3), 4),
        name=f"seeded_garage_shutter_{seed}",
    )


def resolve_config(
    config: GarageShutterConfig | None = None,
) -> ResolvedGarageShutterConfig:
    cfg = config or GarageShutterConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    lift_type = _pick(cfg.lift_type, LIFT_TYPES)
    surface = _pick(cfg.surface, SURFACES)
    window = _pick(cfg.window, WINDOW_CHOICES)
    frame = _pick(cfg.frame, FRAME_CHOICES)

    # --- N domain gating (spec compatibility matrix). ---
    if lift_type == "single_tilt_up":
        # tilt-up collapses to a single slab.
        n_slats = 1
    else:
        n_slats = int(cfg.n_slats) if cfg.n_slats is not None else 6
        n_slats = int(_clamp(n_slats, N_MIN, N_MAX))

    # --- Controlled local scales (all clamped). ---
    w_scale = _clamp(cfg.opening_w_scale, 0.85, 1.15)
    h_scale = _clamp(cfg.opening_h_scale, 0.85, 1.20)
    depth_scale = _clamp(cfg.slat_depth_scale, 0.9, 1.2)
    jamb_scale = _clamp(cfg.jamb_w_scale, 0.8, 1.4)
    slat_lap = _clamp(cfg.slat_lap, 0.012, 0.025)
    tilt_open = _clamp(cfg.tilt_open_angle, 1.0, 1.3)

    n_windows = int(_clamp(cfg.n_windows, 3, 6))
    n_ribs = int(_clamp(cfg.n_ribs, 3, 7))

    slat_d = _SLAT_D * depth_scale

    # Frame scaling: bold rails scale rail_size, slim jambs scale jamb width.
    if frame == "bold_square_tube_rails":
        rail_size = _RAIL_SIZE * jamb_scale
        jamb_w = rail_size
    else:
        rail_size = _RAIL_SIZE
        jamb_w = _JAMB_W * jamb_scale

    opening_w = (_DOOR_W - 2.0 * _JAMB_W) * w_scale  # nominal clear opening
    door_w = opening_w + 2.0 * jamb_w
    slat_w = opening_w - 0.012

    base_opening_h = (6 * 0.355) * h_scale  # near-square nominal opening height
    opening_h = base_opening_h

    # --- Pitch equation: pitch = OPENING_H / n_slats (panel-stack). ---
    # Inequality projection: pitch must hold lap + 2*groove (avoid leaf collapse
    # at large N). If violated, shrink lap then grow opening_h.
    if lift_type == "single_tilt_up":
        slat_pitch = opening_h  # single slab owns the whole opening
    else:
        slat_pitch = opening_h / n_slats
        min_pitch = slat_lap + 2.0 * _GROOVE_H + 0.02
        if slat_pitch < min_pitch:
            # First retract lap toward its floor.
            slat_lap = max(0.012, min_pitch - 2.0 * _GROOVE_H - 0.02 + 0.012)
            min_pitch = slat_lap + 2.0 * _GROOVE_H + 0.02
            if slat_pitch < min_pitch:
                # Then grow the opening so every leaf clears the seam stack.
                opening_h = min_pitch * n_slats
                slat_pitch = opening_h / n_slats

    # --- Depth-stagger inequality: stack must not punch through frame depth. ---
    # STACK_BACK_Y = PANEL_FRONT_Y + n*slat_d must stay within the guide
    # depth buffer. Slim frame depth = jamb_d; bold rails are deeper.
    jamb_d = _JAMB_D
    threshold_h = _THRESHOLD_H
    header_h = _HEADER_H
    panel_base_z = threshold_h

    if frame == "bold_square_tube_rails":
        frame_front_y = -slat_d  # parent panel front-most; rails project ahead
        panel_front_y = frame_front_y
    else:
        frame_front_y = -jamb_d / 2.0
        panel_front_y = frame_front_y + 0.02

    # Guard the stack depth: keep STACK_BACK_Y within a sane rear buffer; if
    # n*slat_d would overrun, retract slat_d.
    max_stack_depth = (jamb_d / 2.0) - panel_front_y - 0.005
    if lift_type == "sectional_telescoping" and n_slats * slat_d > max_stack_depth:
        slat_d = max(0.018, max_stack_depth / n_slats)

    # --- Window-row inequality: window zone must fit the leaf width. ---
    # n_windows*WIN_W + (n_windows-1)*MULLION_W <= slat_w. Shrink n_windows /
    # win width to fit.
    if window == "divided_lite_top_row":
        for _ in range(8):
            avail = slat_w - 0.04  # leave a side margin
            win_zone = n_windows * _win_w(slat_w, n_windows) + (n_windows - 1) * _MULLION_W
            if win_zone <= avail:
                break
            if n_windows > 3:
                n_windows -= 1
            else:
                break

    return ResolvedGarageShutterConfig(
        lift_type=lift_type,
        n_slats=n_slats,
        surface=surface,
        window=window,
        frame=frame,
        palette_style=palette_style,
        n_windows=n_windows,
        n_ribs=n_ribs,
        door_w=door_w,
        jamb_w=jamb_w,
        jamb_d=jamb_d,
        opening_w=opening_w,
        opening_h=opening_h,
        slat_pitch=slat_pitch,
        slat_lap=slat_lap,
        slat_d=slat_d,
        slat_w=slat_w,
        threshold_h=threshold_h,
        header_h=header_h,
        panel_base_z=panel_base_z,
        frame_front_y=frame_front_y,
        panel_front_y=panel_front_y,
        rail_size=rail_size,
        tilt_open_angle=tilt_open,
        name=cfg.name or "garage_shutter",
    )


def _win_w(slat_w: float, n_windows: int) -> float:
    """Per-pane glass width derived from the leaf width and pane count."""
    avail = slat_w - 0.06 - (n_windows - 1) * _MULLION_W
    return max(0.12, avail / n_windows)


def with_overrides(config: GarageShutterConfig, **kwargs: object) -> GarageShutterConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# slot_choices_for_seed (Contract 4 / topology gate).
# ---------------------------------------------------------------------------
def slot_choices_for_config(
    config: GarageShutterConfig | ResolvedGarageShutterConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedGarageShutterConfig) else resolve_config(config)
    return (
        ("type", r.lift_type),
        ("n", f"n{r.n_slats}"),
        ("surface", r.surface),
        ("window", r.window),
        ("frame", r.frame),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers — band / depth placement (parent L79-86).
# ---------------------------------------------------------------------------
def _band_center_z(r: ResolvedGarageShutterConfig, i: int) -> float:
    return r.panel_base_z + r.opening_h - r.slat_pitch * (i + 0.5)


def _leaf_center_y(r: ResolvedGarageShutterConfig, i: int) -> float:
    return r.panel_front_y + r.slat_d * i + r.slat_d / 2.0


# ---------------------------------------------------------------------------
# FRAME slot — frame part visual set (Rule 1: frame is one part).
# ---------------------------------------------------------------------------
def _build_hollow_rail(r: ResolvedGarageShutterConfig, height: float) -> ExtrudeWithHolesGeometry:
    """Hollow square-tube cross section extruded along Z (box_rails L97-103).

    Keeps the source mesh primitive (Rule 3, no Box downgrade).
    """
    hs = r.rail_size / 2.0
    outer = [(-hs, -hs), (hs, -hs), (hs, hs), (-hs, hs)]
    hi = (r.rail_size - 2.0 * _RAIL_WALL) / 2.0
    inner = [(-hi, -hi), (hi, -hi), (hi, hi), (-hi, hi)]
    return ExtrudeWithHolesGeometry(outer, [inner], height, center=True)


def _build_frame(model: ArticulatedObject, r: ResolvedGarageShutterConfig, mats) -> "object":
    frame = model.part("frame")
    opening_w = r.opening_w
    opening_h = r.opening_h
    panel_base_z = r.panel_base_z
    header_h = r.header_h
    threshold_h = r.threshold_h
    stack_back_y = r.stack_back_y

    if r.frame == "bold_square_tube_rails":
        # Bold hollow square-tube guide rails (box_rails L124-135).
        rail_height = opening_h + header_h + threshold_h
        rail_center_z = panel_base_z + opening_h / 2.0 + (header_h - threshold_h) / 2.0
        rail_front_y = r.frame_front_y - 0.020  # rails project forward of panel
        rail_center_y = rail_front_y + r.rail_size / 2.0
        for i in range(2):
            rail_geom = _build_hollow_rail(r, rail_height)
            rail_mesh = mesh_from_geometry(rail_geom, f"guide_rail_{i}")
            sign = -1 if i == 0 else 1
            rail_x = sign * (opening_w / 2.0 + r.rail_size / 2.0)
            frame.visual(
                rail_mesh,
                origin=Origin(xyz=(rail_x, rail_center_y, rail_center_z)),
                material=mats["frame"],
                name=f"guide_rail_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
            )
        # Visible track channels on the inner rail faces (box_rails L140-152).
        track_slot_d = 0.006
        track_slot_w = 0.050
        for i in range(2):
            sign = -1 if i == 0 else 1
            track_x = sign * (opening_w / 2.0 - track_slot_d / 2.0)
            frame.visual(
                Box((track_slot_d, track_slot_w, opening_h)),
                origin=Origin(xyz=(track_x, rail_center_y, panel_base_z + opening_h / 2.0)),
                material=mats["track"],
                name=f"track_channel_{i}", material_class_id="metal.steel_galvanized",
            )
        # Header beam across the rail tops.
        frame.visual(
            Box((r.door_w, r.rail_size, header_h)),
            origin=Origin(xyz=(0.0, rail_center_y, panel_base_z + opening_h + header_h / 2.0)),
            material=mats["frame"],
            name="header", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
        )
        # Deep floor sill from rail front rearward past the deepest leaf.
        sill_d = (stack_back_y + 0.01) - rail_front_y
        frame.visual(
            Box((r.door_w, sill_d, threshold_h)),
            origin=Origin(xyz=(0.0, rail_front_y + sill_d / 2.0, threshold_h / 2.0)),
            material=mats["frame"],
            name="threshold", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
        )
    else:
        # Slim surround: flat black box jambs + flush guide track (parent L101-155).
        jamb_full_h = opening_h + header_h + threshold_h
        jamb_cz = panel_base_z + opening_h / 2.0 + (header_h - threshold_h) / 2.0
        frame.visual(
            Box((r.jamb_w, r.jamb_d, jamb_full_h)),
            origin=Origin(xyz=(-(opening_w + r.jamb_w) / 2.0, 0.0, jamb_cz)),
            material=mats["frame"],
            name="jamb_0", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
        )
        frame.visual(
            Box((r.jamb_w, r.jamb_d, jamb_full_h)),
            origin=Origin(xyz=((opening_w + r.jamb_w) / 2.0, 0.0, jamb_cz)),
            material=mats["frame"],
            name="jamb_1", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
        )
        header_d = 0.055
        frame.visual(
            Box((r.door_w, header_d, header_h)),
            origin=Origin(
                xyz=(
                    0.0,
                    r.frame_front_y + header_d / 2.0,
                    panel_base_z + opening_h + header_h / 2.0,
                )
            ),
            material=mats["frame"],
            name="header", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
        )
        sill_d = (stack_back_y + 0.01) - r.frame_front_y
        frame.visual(
            Box((r.door_w, sill_d, threshold_h)),
            origin=Origin(xyz=(0.0, r.frame_front_y + sill_d / 2.0, threshold_h / 2.0)),
            material=mats["frame"],
            name="threshold", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
        )
        channel_d = (stack_back_y + 0.01) - r.frame_front_y
        channel_y = r.frame_front_y + channel_d / 2.0
        channel_z = panel_base_z + opening_h / 2.0
        frame.visual(
            Box((0.04, channel_d, opening_h)),
            origin=Origin(xyz=(-(opening_w / 2.0 + 0.02), channel_y, channel_z)),
            material=mats["track"],
            name="guide_track_0", material_class_id="metal.steel_galvanized",
        )
        frame.visual(
            Box((0.04, channel_d, opening_h)),
            origin=Origin(xyz=(opening_w / 2.0 + 0.02, channel_y, channel_z)),
            material=mats["track"],
            name="guide_track_1", material_class_id="metal.steel_galvanized",
        )
    frame.inertial = Inertial.from_geometry(
        Box((r.door_w, r.jamb_d, opening_h + header_h + threshold_h)),
        mass=20.0,
        origin=Origin(xyz=(0.0, 0.0, (opening_h + header_h + threshold_h) / 2.0)),
    )
    return frame


def _header_front_y(r: ResolvedGarageShutterConfig) -> float:
    """Y of the header front face (used as the tilt-up REVOLUTE mating face)."""
    if r.frame == "bold_square_tube_rails":
        return r.frame_front_y - 0.020
    return r.frame_front_y


# ---------------------------------------------------------------------------
# Leaf visuals are authored about the band-center / panel-center datum
# while the part-frame origin sits on the parent mating edge (so the joint
# origin lands ON parent geometry, satisfying the flat 15 mm articulation-origin
# baseline; fence_cascade pattern). Every leaf visual is shifted by
# (-anchor_dy, -anchor_dz) so authoring stays band-centered but the part origin
# is the parent's bottom-back mating edge.
# ---------------------------------------------------------------------------
def _local_origin(
    origin: Origin | None, offset: tuple[float, float, float]
) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(value - shift for value, shift in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


# ---------------------------------------------------------------------------
# SURFACE slot — per-leaf face visuals (Rule 1: parent visuals on the leaf).
# field_top_local is the +Y front-face Y of the panel field in the leaf frame.
# ---------------------------------------------------------------------------
def _emit_surface(
    leaf,
    offset: tuple[float, float, float],
    r: ResolvedGarageShutterConfig,
    mats,
    *,
    field_cz: float,
    band_h: float,
) -> None:
    """Emit the SURFACE treatment proud of / inset into the leaf front face.

    band_h is the visible band height (the SLAT_PITCH region) the treatment
    occupies, centered at z=0 in the leaf frame.
    """
    slat_d = r.slat_d
    slat_w = r.slat_w
    if r.surface == "flat_embossed_pillow":
        inset_x = 0.04
        inset_z = 0.045
        leaf.visual(
            Box((slat_w - 2.0 * inset_x, 0.014, band_h - 2.0 * inset_z)),
            origin=_local_origin(
                Origin(xyz=(0.0, -slat_d / 2.0 - 0.004, 0.0)), offset
            ),
            material=mats["pillow"],
            name="panel_pillow", material_class_id="metal.patterned_sheet_panel",
        )
    elif r.surface == "vertical_ribbed":
        inset_x = 0.04
        inset_z = 0.045
        n_ribs = r.n_ribs
        rib_h = 0.016
        rib_proud = 0.007
        rib_w = slat_w - 2.0 * inset_x
        rib_band = band_h - 2.0 * inset_z
        rib_spacing = (rib_band - n_ribs * rib_h) / max(n_ribs - 1, 1)
        rib_base_z = -rib_band / 2.0 + rib_h / 2.0
        rib_y = -slat_d / 2.0 - rib_proud / 2.0
        for rr in range(n_ribs):
            rib_cz = rib_base_z + rr * (rib_h + rib_spacing)
            leaf.visual(
                Box((rib_w, rib_proud, rib_h)),
                origin=_local_origin(Origin(xyz=(0.0, rib_y, rib_cz)), offset),
                material=mats["pillow"],
                name=f"rib_{rr}", material_class_id="metal.patterned_sheet_panel",
            )
    elif r.surface == "raised_panel_field":
        border_inset_x = 0.065
        border_inset_z = 0.060
        raised_proud = 0.009
        raised_w = slat_w - 2.0 * border_inset_x
        raised_h = band_h - 2.0 * border_inset_z
        leaf.visual(
            Box((raised_w, raised_proud, raised_h)),
            origin=_local_origin(
                Origin(xyz=(0.0, -slat_d / 2.0 - raised_proud / 2.0, 0.0)),
                offset,
            ),
            material=mats["raised"],
            name="raised_field", material_class_id="metal.patterned_sheet_panel",
        )
    # perforated_grille has no extra proud visual: its field IS the mesh, built
    # by _build_leaf for that branch.


def _build_grille_mesh(r: ResolvedGarageShutterConfig, field_h: float, name: str):
    """Perforated security-grille mesh (grille L90-136). Mesh primitive kept."""
    half_w = r.slat_w / 2.0
    half_h = field_h / 2.0
    outer = [
        (-half_w, -half_h),
        (half_w, -half_h),
        (half_w, half_h),
        (-half_w, half_h),
    ]
    inner_w = r.slat_w - 2.0 * _GRILLE_FRAME_W
    inner_h = field_h - 2.0 * _GRILLE_FRAME_W
    n_cols = max(1, int(inner_w / _GRILLE_PITCH))
    n_rows = max(1, int(inner_h / _GRILLE_PITCH))
    x_spacing = inner_w / n_cols
    y_spacing = inner_h / n_rows
    hs = _GRILLE_HOLE_SIZE / 2.0
    holes = []
    for row in range(n_rows):
        for col in range(n_cols):
            cx = -inner_w / 2.0 + x_spacing / 2.0 + col * x_spacing
            cy = -inner_h / 2.0 + y_spacing / 2.0 + row * y_spacing
            holes.append(
                [
                    (cx - hs, cy - hs),
                    (cx - hs, cy + hs),
                    (cx + hs, cy + hs),
                    (cx + hs, cy - hs),
                ]
            )
    geom = ExtrudeWithHolesGeometry(
        outer, holes, _GRILLE_THICKNESS, cap=True, center=True, closed=True
    )
    geom.rotate_x(math.pi / 2)
    return geom


# ---------------------------------------------------------------------------
# WINDOW slot — top-leaf divided-lite glazing (window_row L197-236).
# ---------------------------------------------------------------------------
def _emit_window_row(
    leaf, offset: tuple[float, float, float], r: ResolvedGarageShutterConfig, mats
) -> None:
    slat_w = r.slat_w
    slat_d = r.slat_d
    n_windows = r.n_windows
    win_w = _win_w(slat_w, n_windows)
    win_h = min(0.22, r.slat_pitch * 0.55)
    frame_depth = _WIN_RECESS + 0.003
    total_zone = n_windows * win_w + (n_windows - 1) * _MULLION_W
    side_margin = (slat_w - total_zone) / 2.0
    panel_front_y = -slat_d / 2.0
    glass_cy = panel_front_y + _WIN_RECESS + _WIN_GLASS_T / 2.0
    frame_cy = panel_front_y + frame_depth / 2.0

    for j in range(n_windows):
        win_cx = -slat_w / 2.0 + side_margin + win_w / 2.0 + j * (win_w + _MULLION_W)
        leaf.visual(
            Box((win_w, _WIN_GLASS_T, win_h)),
            origin=_local_origin(Origin(xyz=(win_cx, glass_cy, 0.0)), offset),
            material=mats["glass"],
            name=f"window_glass_{j}", material_class_id="glass.smoked_tinted",
        )
    for j in range(n_windows - 1):
        mull_cx = -slat_w / 2.0 + side_margin + win_w + _MULLION_W / 2.0 + j * (win_w + _MULLION_W)
        leaf.visual(
            Box((_MULLION_W, frame_depth, win_h)),
            origin=_local_origin(Origin(xyz=(mull_cx, frame_cy, 0.0)), offset),
            material=mats["mullion"],
            name=f"mullion_{j}", material_class_id="metal.paint_coated",
        )
    leaf.visual(
        Box((total_zone, frame_depth, _WIN_RAIL_H)),
        origin=_local_origin(
            Origin(xyz=(0.0, frame_cy, win_h / 2.0 + _WIN_RAIL_H / 2.0)), offset
        ),
        material=mats["mullion"],
        name="top_rail", material_class_id="metal.paint_coated",
    )
    leaf.visual(
        Box((total_zone, frame_depth, _WIN_RAIL_H)),
        origin=_local_origin(
            Origin(xyz=(0.0, frame_cy, -(win_h / 2.0 + _WIN_RAIL_H / 2.0))),
            offset,
        ),
        material=mats["mullion"],
        name="bottom_rail", material_class_id="metal.paint_coated",
    )


# ---------------------------------------------------------------------------
# Leaf builder (shared by panel-stack leaves and the tilt-up slab rows).
# Authored about z=0 (the band center); field spans field_h centered at field_cz.
# ---------------------------------------------------------------------------
def _emit_latch_handle(
    leaf,
    offset: tuple[float, float, float],
    r: ResolvedGarageShutterConfig,
    mats,
    *,
    handle_z: float,
) -> None:
    """Latch handle + 2 bosses proud of the leaf front face (parent L196-217)."""
    if r.surface == "perforated_grille":
        handle_y = -_GRILLE_THICKNESS / 2.0 - 0.010
        boss_y = -_GRILLE_THICKNESS / 2.0 - 0.004
        boss_d = 0.016
    else:
        handle_y = -r.slat_d / 2.0 - 0.018
        boss_y = -r.slat_d / 2.0 - 0.008
        boss_d = 0.02
    leaf.visual(
        Box((0.18, 0.022, 0.032)),
        origin=_local_origin(Origin(xyz=(0.0, handle_y, handle_z)), offset),
        material=mats["handle"],
        name="latch_handle", material_class_id="metal.paint_coated",
    )
    leaf.visual(
        Box((0.02, boss_d, 0.024)),
        origin=_local_origin(Origin(xyz=(-0.07, boss_y, handle_z)), offset),
        material=mats["handle"],
        name="handle_boss_0", material_class_id="metal.paint_coated",
    )
    leaf.visual(
        Box((0.02, boss_d, 0.024)),
        origin=_local_origin(Origin(xyz=(0.07, boss_y, handle_z)), offset),
        material=mats["handle"],
        name="handle_boss_1", material_class_id="metal.paint_coated",
    )


def _build_panel_leaf(
    model: ArticulatedObject,
    r: ResolvedGarageShutterConfig,
    mats,
    *,
    i: int,
    is_top: bool,
    is_bottom: bool,
) -> "object":
    """One panel-stack leaf slat_{i}.

    Visuals are authored about the band-center / panel-center datum but the
    part-frame origin is the parent's bottom-back mating edge (anchor_dy =
    -slat_d/2 back face, anchor_dz = +slat_pitch/2 band-bottom). Each authored
    origin is rebased explicitly so the leaf-to-leaf PRISMATIC origin lands on
    parent geometry.
    """
    slat = model.part(f"slat_{i}")
    anchor_dy = -r.slat_d / 2.0
    anchor_dz = r.slat_pitch / 2.0
    offset = (0.0, anchor_dy, anchor_dz)
    field_h = r.slat_pitch if is_top else r.slat_pitch + r.slat_lap
    field_cz = 0.0 if is_top else r.slat_lap / 2.0
    slat_d = r.slat_d
    slat_w = r.slat_w

    glaze_top = is_top and r.window == "divided_lite_top_row"

    if r.surface == "perforated_grille":
        grille_geom = _build_grille_mesh(r, field_h, f"grille_{i}")
        grille_geom.translate(0.0, 0.0, field_cz)
        slat.visual(
            mesh_from_geometry(grille_geom, f"grille_{i}"),
            origin=_local_origin(Origin(xyz=(0.0, 0.0, 0.0)), offset),
            material=mats["panel"],
            name="grille_panel", material_class_id="metal.mesh_chainmail",
        )
        # Full-depth structural edge rails: the telescoping contact chain that
        # replaces the solid lap (grille L226-241).
        rail_x = slat_w / 2.0 - _RAIL_W / 2.0
        slat.visual(
            Box((_RAIL_W, slat_d, field_h)),
            origin=_local_origin(Origin(xyz=(-rail_x, 0.0, field_cz)), offset),
            material=mats["track"],
            name="edge_rail_0", material_class_id="metal.steel_galvanized",
        )
        slat.visual(
            Box((_RAIL_W, slat_d, field_h)),
            origin=_local_origin(Origin(xyz=(rail_x, 0.0, field_cz)), offset),
            material=mats["track"],
            name="edge_rail_1", material_class_id="metal.steel_galvanized",
        )
        # A grille top leaf cannot be glazed (the field is open mesh); window
        # treatment is suppressed in resolve via compatibility (handled below).
    else:
        # Solid panel field. raised_panel_field names it panel_body in source,
        # but a single field-name keeps the stack/lap checks uniform.
        slat.visual(
            Box((slat_w, slat_d, field_h)),
            origin=_local_origin(Origin(xyz=(0.0, 0.0, field_cz)), offset),
            material=mats["panel"],
            name="panel_field", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
        )
        if glaze_top:
            _emit_window_row(slat, offset, r, mats)
        else:
            _emit_surface(slat, offset, r, mats, field_cz=field_cz, band_h=r.slat_pitch)

    # Seam groove along the bottom edge (all SURFACE share this).
    groove_field_y = -_GRILLE_THICKNESS / 2.0 if r.surface == "perforated_grille" else -slat_d / 2.0
    slat.visual(
        Box((slat_w, 0.018, _GROOVE_H)),
        origin=_local_origin(
            Origin(
                xyz=(
                    0.0,
                    groove_field_y + 0.018 / 2.0 - 0.002,
                    -r.slat_pitch / 2.0 + _GROOVE_H / 2.0,
                )
            ),
            offset,
        ),
        material=mats["groove"],
        name="seam_groove", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
    )

    if is_bottom:
        _emit_latch_handle(
            slat, offset, r, mats, handle_z=-r.slat_pitch / 2.0 + 0.06
        )

    slat.inertial = Inertial.from_geometry(
        Box((slat_w, slat_d, field_h)),
        mass=8.0,
        origin=Origin(xyz=(0.0, 0.0 - anchor_dy, field_cz - anchor_dz)),
    )
    return slat


# ---------------------------------------------------------------------------
# TYPE = sectional_telescoping (panel-stack + PRISMATIC chain).
# ---------------------------------------------------------------------------
def _build_sectional(model: ArticulatedObject, r: ResolvedGarageShutterConfig, mats, frame) -> None:
    n = r.n_slats
    for i in range(n):
        _build_panel_leaf(model, r, mats, i=i, is_top=(i == 0), is_bottom=(i == n - 1))

    # Top leaf FIXED to the frame at the top of the opening (parent L227-233).
    # The top leaf's part-frame origin is its band-top-front edge (anchor_dy=
    # -slat_d/2, anchor_dz=+slat_pitch/2), which lands on the header geometry at
    # x=0, z=hinge_z (so the FIXED origin sits on real frame steel).
    anchor_dy = -r.slat_d / 2.0
    anchor_dz = r.slat_pitch / 2.0
    model.articulation(
        "frame_to_slat_0",
        ArticulationType.FIXED,
        parent=frame,
        child="slat_0",
        origin=Origin(
            xyz=(0.0, _leaf_center_y(r, 0) + anchor_dy, _band_center_z(r, 0) + anchor_dz)
        ),
    )

    # Per-link +Z PRISMATIC telescoping chain (parent L234-244). MatingContract
    # pins the kissing faces: the lower leaf's +Y face touches the upper leaf's
    # -Y face (panel_field, or edge_rail for the open grille).
    contact_geom = "edge_rail_0" if r.surface == "perforated_grille" else "panel_field"
    # Travel is pitch-lap-clearance (not a full pitch): a full-pitch rise pokes
    # each leaf's upward lap one lap above the FIXED top leaf into the header.
    lift_limits = MotionLimits(effort=400.0, velocity=0.30, lower=0.0, upper=r.lift_travel)
    for i in range(1, n):
        model.articulation(
            f"slat_{i - 1}_to_slat_{i}",
            ArticulationType.PRISMATIC,
            parent=f"slat_{i - 1}",
            child=f"slat_{i}",
            origin=Origin(xyz=(0.0, r.slat_d, -r.slat_pitch)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=lift_limits,
            mating=MatingContract(
                parent_face_geometry=contact_geom,
                parent_face_side="positive_y",
                child_face_geometry=contact_geom,
                child_face_side="negative_y",
                contact_tol=0.003,
            ),
        )


# ---------------------------------------------------------------------------
# TYPE = single_tilt_up (single slab + REVOLUTE top hinge).
# ---------------------------------------------------------------------------
def _build_tilt_up(model: ArticulatedObject, r: ResolvedGarageShutterConfig, mats, frame) -> None:
    leaf = model.part("door_leaf")
    opening_h = r.opening_h
    slat_w = r.slat_w
    slat_d = r.slat_d
    hinge_z = r.hinge_z

    # Pivot at the leaf's FRONT (-Y) face, not its centerline: a real tilt-up
    # door hinges on its outer face so the top edge swings DOWN-and-out and
    # never climbs into the header lintel. All leaf material then sits on the
    # +Y side of the pivot, so under the -X swing every leaf point moves to
    # z <= hinge (below the header). The canvas shifts every leaf visual +slat_d/2
    # in Y (front face -> local y=0) while the joint origin drops -slat_d/2 in Y
    # to the front face, so world geometry at rest is unchanged.
    offset = (0.0, -slat_d / 2.0, 0.0)

    # Part origin at the hinge (top-front edge at the header). Field extends
    # downward from z=0 to z=-OPENING_H (tiltup L175-183).
    leaf.visual(
        Box((slat_w, slat_d, opening_h)),
        origin=_local_origin(Origin(xyz=(0.0, 0.0, -opening_h / 2.0)), offset),
        material=mats["panel"],
        name="panel_field", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
    )

    # N_ROWS of inlaid SURFACE rows reframed onto the single slab (spec: tilt-up
    # reframes SURFACE/WINDOW to the single board). Rows match the panel-stack
    # band pitch so identity is preserved.
    n_rows = max(3, min(8, int(round(opening_h / 0.355))))
    row_pitch = opening_h / n_rows
    glaze = r.window == "divided_lite_top_row" and r.surface != "perforated_grille"

    for i in range(n_rows):
        # Local z of row band center (origin at top edge, rows go downward).
        row_cz = -row_pitch * (i + 0.5)
        if i == 0 and glaze:
            _emit_tilt_window_row(
                leaf, offset, r, row_cz=row_cz, row_pitch=row_pitch, mats=mats
            )
        elif r.surface == "perforated_grille":
            _emit_tilt_grille_row(
                leaf,
                offset,
                r,
                row_cz=row_cz,
                row_pitch=row_pitch,
                mats=mats,
                idx=i,
            )
        else:
            _emit_tilt_surface_row(
                leaf, offset, r, row_cz=row_cz, row_pitch=row_pitch, mats=mats
            )
        # Seam groove at the bottom edge of each row band.
        leaf.visual(
            Box((slat_w, 0.018, _GROOVE_H)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        0.0,
                        -slat_d / 2.0 + 0.018 / 2.0 - 0.002,
                        row_cz - row_pitch / 2.0 + _GROOVE_H / 2.0,
                    )
                ),
                offset,
            ),
            material=mats["groove"],
            name=f"seam_groove_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"grey_steel", "white", "black_framed", "dark_bronze", "cream_almond"} else "metal.steel_galvanized"),
        )

    # Latch handle near the bottom of the slab.
    handle_z = -opening_h + 0.06
    leaf.visual(
        Box((0.18, 0.022, 0.032)),
        origin=_local_origin(
            Origin(xyz=(0.0, -slat_d / 2.0 - 0.018, handle_z)), offset
        ),
        material=mats["handle"],
        name="latch_handle", material_class_id="metal.paint_coated",
    )
    leaf.visual(
        Box((0.02, 0.02, 0.024)),
        origin=_local_origin(
            Origin(xyz=(-0.07, -slat_d / 2.0 - 0.008, handle_z)), offset
        ),
        material=mats["handle"],
        name="handle_boss_0", material_class_id="metal.paint_coated",
    )
    leaf.visual(
        Box((0.02, 0.02, 0.024)),
        origin=_local_origin(
            Origin(xyz=(0.07, -slat_d / 2.0 - 0.008, handle_z)), offset
        ),
        material=mats["handle"],
        name="handle_boss_1", material_class_id="metal.paint_coated",
    )
    # Inertial centered on the leaf body; +slat_d/2 keeps it at the true world
    # center under the front-face pivot shift.
    leaf.inertial = Inertial.from_geometry(
        Box((slat_w, slat_d, opening_h)),
        mass=30.0,
        origin=Origin(xyz=(0.0, slat_d / 2.0, -opening_h / 2.0)),
    )

    # REVOLUTE hinge at the header line; axis -X swings the bottom out + up
    # (tiltup L217-225). MatingContract: header bottom face kisses the leaf top
    # face. The header's -Z face sits at the hinge line; the leaf field +Z face
    # is at z=0 in the leaf frame (= hinge), so they kiss.
    model.articulation(
        "frame_to_leaf",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=leaf,
        # Pivot at the leaf front (-Y) face = _leaf_center_y - slat_d/2, the
        # top-front edge; the -X swing then keeps every leaf point at/below the
        # header line instead of climbing into the lintel.
        origin=Origin(xyz=(0.0, _leaf_center_y(r, 0) - slat_d / 2.0, hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=200.0, velocity=0.5, lower=0.0, upper=r.tilt_open_angle),
        mating=MatingContract(
            parent_face_geometry="header",
            parent_face_side="negative_z",
            child_face_geometry="panel_field",
            child_face_side="positive_z",
            contact_tol=0.02,
        ),
    )


def _emit_tilt_surface_row(leaf, offset, r, *, row_cz, row_pitch, mats) -> None:
    slat_w = r.slat_w
    slat_d = r.slat_d
    if r.surface == "vertical_ribbed":
        inset_x = 0.04
        inset_z = 0.045
        n_ribs = r.n_ribs
        rib_h = 0.016
        rib_proud = 0.007
        rib_w = slat_w - 2.0 * inset_x
        rib_band = row_pitch - 2.0 * inset_z
        rib_spacing = (rib_band - n_ribs * rib_h) / max(n_ribs - 1, 1)
        rib_base_z = row_cz - rib_band / 2.0 + rib_h / 2.0
        rib_y = -slat_d / 2.0 - rib_proud / 2.0
        for rr in range(n_ribs):
            rib_cz = rib_base_z + rr * (rib_h + rib_spacing)
            leaf.visual(
                Box((rib_w, rib_proud, rib_h)),
                origin=_local_origin(Origin(xyz=(0.0, rib_y, rib_cz)), offset),
                material=mats["pillow"],
                name=f"rib_{_row_tag(row_cz)}_{rr}", material_class_id="metal.patterned_sheet_panel",
            )
    elif r.surface == "raised_panel_field":
        border_inset_x = 0.065
        border_inset_z = 0.060
        raised_proud = 0.009
        leaf.visual(
            Box((slat_w - 2.0 * border_inset_x, raised_proud, row_pitch - 2.0 * border_inset_z)),
            origin=_local_origin(
                Origin(xyz=(0.0, -slat_d / 2.0 - raised_proud / 2.0, row_cz)),
                offset,
            ),
            material=mats["raised"],
            name=f"raised_field_{_row_tag(row_cz)}", material_class_id="metal.patterned_sheet_panel",
        )
    else:  # flat_embossed_pillow
        inset_x = 0.04
        inset_z = 0.045
        leaf.visual(
            Box((slat_w - 2.0 * inset_x, 0.014, row_pitch - 2.0 * inset_z)),
            origin=_local_origin(
                Origin(xyz=(0.0, -slat_d / 2.0 - 0.004, row_cz)), offset
            ),
            material=mats["pillow"],
            name=f"panel_pillow_{_row_tag(row_cz)}", material_class_id="metal.patterned_sheet_panel",
        )


def _emit_tilt_grille_row(leaf, offset, r, *, row_cz, row_pitch, mats, idx) -> None:
    """A perforated grille window cut into the slab row (mesh kept).

    The grille sits as relief on the solid slab front face, embedded 1 mm into
    ``panel_field`` (its back face at slat front + 0.001) so every row is
    connected to the slab regardless of the row band height — floating it in
    front left thin rows relying on a marginal seam-groove Z-overlap that could
    open a ~1 mm disconnection gap.
    """
    grille_geom = _build_grille_mesh(r, row_pitch * 0.9, f"slab_grille_{idx}")
    grille_geom.translate(0.0, -r.slat_d / 2.0 - _GRILLE_THICKNESS / 2.0 + 0.001, row_cz)
    leaf.visual(
        mesh_from_geometry(grille_geom, f"slab_grille_{idx}"),
        origin=_local_origin(Origin(xyz=(0.0, 0.0, 0.0)), offset),
        material=mats["track"],
        name=f"grille_panel_{idx}", material_class_id="metal.mesh_chainmail",
    )


def _emit_tilt_window_row(leaf, offset, r, *, row_cz, row_pitch, mats) -> None:
    slat_w = r.slat_w
    slat_d = r.slat_d
    n_windows = r.n_windows
    win_w = _win_w(slat_w, n_windows)
    win_h = min(0.22, row_pitch * 0.55)
    frame_depth = _WIN_RECESS + 0.003
    total_zone = n_windows * win_w + (n_windows - 1) * _MULLION_W
    side_margin = (slat_w - total_zone) / 2.0
    panel_front_y = -slat_d / 2.0
    glass_cy = panel_front_y + _WIN_RECESS + _WIN_GLASS_T / 2.0
    frame_cy = panel_front_y + frame_depth / 2.0
    for j in range(n_windows):
        win_cx = -slat_w / 2.0 + side_margin + win_w / 2.0 + j * (win_w + _MULLION_W)
        leaf.visual(
            Box((win_w, _WIN_GLASS_T, win_h)),
            origin=_local_origin(Origin(xyz=(win_cx, glass_cy, row_cz)), offset),
            material=mats["glass"],
            name=f"window_glass_{j}", material_class_id="glass.smoked_tinted",
        )
    for j in range(n_windows - 1):
        mull_cx = -slat_w / 2.0 + side_margin + win_w + _MULLION_W / 2.0 + j * (win_w + _MULLION_W)
        leaf.visual(
            Box((_MULLION_W, frame_depth, win_h)),
            origin=_local_origin(Origin(xyz=(mull_cx, frame_cy, row_cz)), offset),
            material=mats["mullion"],
            name=f"mullion_{j}", material_class_id="metal.paint_coated",
        )
    leaf.visual(
        Box((total_zone, frame_depth, _WIN_RAIL_H)),
        origin=_local_origin(
            Origin(
                xyz=(0.0, frame_cy, row_cz + win_h / 2.0 + _WIN_RAIL_H / 2.0)
            ),
            offset,
        ),
        material=mats["mullion"],
        name="top_rail", material_class_id="metal.paint_coated",
    )
    leaf.visual(
        Box((total_zone, frame_depth, _WIN_RAIL_H)),
        origin=_local_origin(
            Origin(
                xyz=(0.0, frame_cy, row_cz - (win_h / 2.0 + _WIN_RAIL_H / 2.0))
            ),
            offset,
        ),
        material=mats["mullion"],
        name="bottom_rail", material_class_id="metal.paint_coated",
    )


def _row_tag(row_cz: float) -> str:
    return str(abs(int(round(row_cz * 1000))))


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_garage_shutter(
    config: GarageShutterConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"garage_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    frame = _build_frame(model, r, mats)
    if r.lift_type == "single_tilt_up":
        _build_tilt_up(model, r, mats, frame)
    else:
        _build_sectional(model, r, mats, frame)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_garage_shutter(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_garage_shutter(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_garage_shutter_tests(
    object_model: ArticulatedObject,
    config: GarageShutterConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")

    # ---- Intentional overlaps (element-scoped where possible). ----
    if r.lift_type == "sectional_telescoping":
        slats = [object_model.get_part(f"slat_{i}") for i in range(r.n_slats)]
        # Adjacent leaves nest face-to-face when telescoped open.
        for i in range(1, r.n_slats):
            ctx.allow_overlap(
                slats[i - 1],
                slats[i],
                reason=(
                    "Telescoping garage door: each leaf nests flat against the back of "
                    "the leaf above it when raised; faces/surface treatments press into "
                    "that contact plane."
                ),
            )
        # The bottom leaf's proud lift handle nests up INTO the raised stack when
        # the door telescopes open. Its forward projection reaches the leaf
        # immediately in front of it; for thin leaves that is a non-adjacent leaf
        # (adjacent pairs are already whole-part allowed above). Element-scoped so
        # only the handle-vs-leaf-field contact is exempt, not the whole part pair.
        if r.n_slats >= 3:
            bottom = slats[r.n_slats - 1]
            handle_elems = ("latch_handle", "handle_boss_0", "handle_boss_1")
            field_elems = (
                ("grille_panel", "edge_rail_0", "edge_rail_1", "seam_groove")
                if r.surface == "perforated_grille"
                else ("panel_field", "seam_groove")
            )
            for j in range(r.n_slats - 2):  # non-adjacent upper leaves only
                for he in handle_elems:
                    for fe in field_elems:
                        ctx.allow_overlap(
                            bottom,
                            slats[j],
                            elem_a=he,
                            elem_b=fe,
                            reason=(
                                "Telescoping door open: the bottom leaf's proud lift "
                                "handle nests up into the raised leaf stack and presses "
                                "against the back face of an upper leaf."
                            ),
                        )
        if r.window == "divided_lite_top_row" and r.surface != "perforated_grille":
            # Top-leaf glazing is recessed into the panel field (same part).
            top = slats[0]
            for j in range(r.n_windows):
                ctx.allow_overlap(
                    top,
                    top,
                    elem_a="panel_field",
                    elem_b=f"window_glass_{j}",
                    reason="recessed glass light is inset into the top-leaf panel field.",
                )
            for j in range(r.n_windows - 1):
                ctx.allow_overlap(
                    top,
                    top,
                    elem_a="panel_field",
                    elem_b=f"mullion_{j}",
                    reason="mullion divider sits in the glazing recess of the top leaf.",
                )
            for rail in ("top_rail", "bottom_rail"):
                ctx.allow_overlap(
                    top,
                    top,
                    elem_a="panel_field",
                    elem_b=rail,
                    reason="window frame rail sits in the glazing recess of the top leaf.",
                )
    elif r.lift_type == "single_tilt_up" and r.surface == "perforated_grille":
        # Each grille relief row is embedded 1 mm into the slab's solid
        # panel_field so it stays connected to the slab; that intentional
        # embed is a same-part element overlap.
        leaf = object_model.get_part("door_leaf")
        n_rows = max(3, min(8, int(round(r.opening_h / 0.355))))
        for i in range(n_rows):
            ctx.allow_overlap(
                leaf,
                leaf,
                elem_a="panel_field",
                elem_b=f"grille_panel_{i}",
                reason="perforated grille relief row is embedded into the tilt-up slab front face.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    part_names = {p.name for p in object_model.parts}
    ctx.check("frame part present", "frame" in part_names, details=str(sorted(part_names)))

    # ---- TYPE / motion-spine topology. ----
    if r.lift_type == "sectional_telescoping":
        ctx.check(
            "sectional has >=2 leaves",
            r.n_slats >= 2 and all(f"slat_{i}" in part_names for i in range(r.n_slats)),
            details=f"n_slats={r.n_slats}",
        )
        jfix = object_model.get_articulation("frame_to_slat_0")
        ctx.check(
            "top leaf FIXED to frame",
            jfix.articulation_type == ArticulationType.FIXED,
            details=f"type={jfix.articulation_type}",
        )
        # Per-link PRISMATIC +Z chain.
        ok_axis = True
        for i in range(1, r.n_slats):
            j = object_model.get_articulation(f"slat_{i - 1}_to_slat_{i}")
            if j.articulation_type != ArticulationType.PRISMATIC or abs(j.axis[2]) < 0.99:
                ok_axis = False
                break
        ctx.check(
            "leaf-to-leaf chain is PRISMATIC about +Z",
            ok_axis,
            details=f"n_links={r.n_slats - 1}",
        )
    else:
        ctx.check(
            "tilt-up collapses to a single door_leaf",
            r.n_slats == 1 and "door_leaf" in part_names,
            details=f"n_slats={r.n_slats}",
        )
        jr = object_model.get_articulation("frame_to_leaf")
        ctx.check(
            "tilt-up leaf is REVOLUTE about -X",
            jr.articulation_type == ArticulationType.REVOLUTE and abs(jr.axis[0]) > 0.99,
            details=f"type={jr.articulation_type} axis={tuple(jr.axis)}",
        )

    # ---- SURFACE: grille keeps the mesh primitive (Rule 3). ----
    if r.surface == "perforated_grille":
        if r.lift_type == "sectional_telescoping":
            grille_vis = [
                v for v in object_model.get_part("slat_0").visuals if v.name == "grille_panel"
            ]
            ctx.check(
                "grille leaf uses a perforated mesh field (no Box downgrade)",
                len(grille_vis) == 1,
                details=f"grille visuals={[v.name for v in grille_vis]}",
            )
        else:
            leaf = object_model.get_part("door_leaf")
            grille_vis = [v for v in leaf.visuals if v.name.startswith("grille_panel")]
            ctx.check(
                "tilt-up slab has perforated mesh rows (no Box downgrade)",
                len(grille_vis) >= 1,
                details=f"grille visuals={[v.name for v in grille_vis]}",
            )

    # ---- FRAME: bold rails keep the hollow-tube mesh. ----
    if r.frame == "bold_square_tube_rails":
        rail_vis = [v for v in frame.visuals if v.name.startswith("guide_rail_")]
        ctx.check(
            "bold square-tube rails present as hollow-tube mesh visuals",
            len(rail_vis) == 2,
            details=f"rails={[v.name for v in rail_vis]}",
        )
        rail0 = ctx.part_element_world_aabb(frame, elem="guide_rail_0")
        if rail0 is not None:
            ctx.check(
                "bold rail cross section is chunky (>=70 mm)",
                (rail0[1][0] - rail0[0][0]) >= 0.070,
                details=f"rail0_x_extent={rail0[1][0] - rail0[0][0]:.3f}",
            )

    # ---- WINDOW row present when selected (panel-stack, non-grille). ----
    if (
        r.window == "divided_lite_top_row"
        and r.surface != "perforated_grille"
        and r.lift_type == "sectional_telescoping"
    ):
        top = object_model.get_part("slat_0")
        glass = [v.name for v in top.visuals if v.name.startswith("window_glass_")]
        ctx.check(
            "top leaf glazed with the divided-lite window row",
            len(glass) == r.n_windows,
            details=f"glass={sorted(glass)} expected n_windows={r.n_windows}",
        )

    # ---- Leaf stack spans the full opening height. ----
    if r.lift_type == "sectional_telescoping":
        top_elem = "grille_panel" if r.surface == "perforated_grille" else "panel_field"
        top_aabb = ctx.part_element_world_aabb(object_model.get_part("slat_0"), elem=top_elem)
        bot_aabb = ctx.part_element_world_aabb(
            object_model.get_part(f"slat_{r.n_slats - 1}"), elem=top_elem
        )
        ctx.check(
            "leaf stack spans the full opening height",
            top_aabb is not None
            and bot_aabb is not None
            and bot_aabb[0][2] <= r.panel_base_z + 0.02
            and top_aabb[1][2] >= r.panel_base_z + r.opening_h - 0.02,
            details=f"bottom={bot_aabb}, top={top_aabb}",
        )
    else:
        leaf = object_model.get_part("door_leaf")
        leaf_aabb = ctx.part_element_world_aabb(leaf, elem="panel_field")
        ctx.check(
            "tilt-up leaf spans the full opening height",
            leaf_aabb is not None
            and leaf_aabb[0][2] <= r.panel_base_z + 0.02
            and leaf_aabb[1][2] >= r.panel_base_z + r.opening_h - 0.02,
            details=f"leaf_aabb={leaf_aabb}",
        )

    # ---- Actuation. ----
    if r.lift_type == "sectional_telescoping" and r.n_slats >= 2:
        slats = [object_model.get_part(f"slat_{i}") for i in range(r.n_slats)]
        lift_joints = [
            object_model.get_articulation(f"slat_{i - 1}_to_slat_{i}") for i in range(1, r.n_slats)
        ]
        rest = [ctx.part_world_position(s) for s in slats]
        with ctx.pose({j: r.lift_travel for j in lift_joints}):
            opened = [ctx.part_world_position(s) for s in slats]
        chain_ok = all(rest[i] is not None and opened[i] is not None for i in range(r.n_slats))
        if chain_ok:
            for i in range(r.n_slats):
                rise = opened[i][2] - rest[i][2]
                if abs(rise - r.lift_travel * i) > 1e-3:
                    chain_ok = False
                    break
        ctx.check(
            "top leaf fixed; each lower leaf rises one lift-travel per chain link",
            chain_ok,
            details=f"rest={rest}, open={opened}",
        )
        # Fully raised, no leaf top climbs into the header (pitch-lap-clearance
        # travel keeps every leaf >= _HEADER_CLEAR below the header underside).
        top_elem = "grille_panel" if r.surface == "perforated_grille" else "panel_field"
        header_bottom = r.panel_base_z + r.opening_h
        with ctx.pose({j: r.lift_travel for j in lift_joints}):
            tops = [ctx.part_element_world_aabb(s, elem=top_elem) for s in slats[1:]]
        raised_clear = all(
            t is not None and t[1][2] <= header_bottom - _HEADER_CLEAR + 1e-4 for t in tops
        )
        ctx.check(
            "raised lower leaves stay below the header (no lintel punch-through)",
            raised_clear,
            details=f"header_bottom={header_bottom:.4f} tops={[None if t is None else round(t[1][2], 4) for t in tops]}",
        )
    elif r.lift_type == "single_tilt_up":
        leaf = object_model.get_part("door_leaf")
        hinge = object_model.get_articulation("frame_to_leaf")
        rest = ctx.part_element_world_aabb(leaf, elem="panel_field")
        with ctx.pose({hinge: min(1.2, r.tilt_open_angle)}):
            opened = ctx.part_element_world_aabb(leaf, elem="panel_field")
        if rest is not None and opened is not None:
            ctx.check(
                "tilt-up swings the leaf bottom outward and upward",
                opened[0][1] < rest[0][1] - 0.2 and opened[0][2] > rest[0][2] + 0.2,
                details=f"rest={rest}, open={opened}",
            )

    # ---- Bottom leaf seats near the sill / ground. ----
    aabb = ctx.part_world_aabb(frame)
    if aabb is not None:
        ctx.check(
            "frame rests on the ground",
            aabb[0][2] < 0.02,
            details=f"z_min={aabb[0][2]:.4f}",
        )

    # ---- Pitch >= lap + 2*groove inequality proven from authored dims. ----
    if r.lift_type == "sectional_telescoping":
        ctx.check(
            "pitch holds lap + seam (no leaf collapse at large N)",
            r.slat_pitch >= r.slat_lap + 2.0 * _GROOVE_H,
            details=f"pitch={r.slat_pitch:.4f} lap={r.slat_lap:.4f}",
        )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded (type/n/surface/window/frame)",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "GarageShutterConfig",
    "ResolvedGarageShutterConfig",
    "build_garage_shutter",
    "build_seeded_garage_shutter",
    "config_from_seed",
    "resolve_config",
    "run_garage_shutter_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
