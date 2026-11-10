# SPDX-License-Identifier: Apache-2.0

"""Arcade cabinet (standing / tabletop arcade game console) modular template.

NOTE on scope: this is a **stand-up / tabletop arcade cabinet** — a static
cabinet body carrying a screen + marquee and a control face on which one or
more movable primary control mechanisms (ball-top joystick / trackball /
spinner knob / linear slider) stand up. It is NOT a handheld game console
(PSP / gamepad) and NOT a casino slot machine.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Equipment_Game_console.md`` and the
``picture/Equipment/Game console`` 5-star sample pool (1 parent + 8 slot-fork
variants), read from ``articraft_data/data/records/`` (workbench-only forks of
parent ``a5689b50``).

Structure (pattern = ``mixed``): a single static root ``cabinet_body`` part
(its shell mesh chosen by ``body_style``), with two further axes attaching as
parallel movable children of the body:

  * ``body_style`` (4): wedge_cabinet / upright_box / cocktail_flattop /
    bartop_crown — the cabinet shell mesh + screen + control face. A static
    root part; all of its decoration (shell, pedestal, screen, marquee text,
    keypad clusters, control plates, control seats) are ``parent.visual(...)``
    per Rule 1.
  * ``control_style`` (4): the primary control mechanism mounted on each
    station — ball_top_joystick (1 REVOLUTE -X), trackball (1 REVOLUTE +Z),
    spinner_knob (1 CONTINUOUS +Z), linear_slider (1 PRISMATIC +X).
  * ``station_count`` (N in [1,6]): a multiplicity axis — N identical player
    stations evenly spaced along X, each a full copy of the control mechanism
    with its own control seat + joint. N is encoded into the slot_choice tuple
    as ``("stations", f"n{N}")``.

Every control mechanism stands vertically out of a real anchoring **seat**
visual on the cabinet (collar / cup / bearing / slider rail). Each non-FIXED
joint declares a ``MatingContract`` pinning the seat's top face to the
control's base face (Rule 2). Captured-fit interpenetration (boot/shaft in
collar, sphere/hub in cup, stem in bearing, runner in rail) is declared
element-scoped via ``allow_overlap`` in ``run_arcade_cabinet_tests``, mirroring
each source record's run_tests block.

Adopted 5-star sources (record_id -> use):
  * a5689b50 (parent)              -> wedge_cabinet body + ball_top_joystick + N=1
  * game_console_var_body_upright_box  -> upright_box body
  * game_console_var_body_cocktail     -> cocktail_flattop body
  * game_console_var_body_bartop_crown -> bartop_crown body
  * game_console_var_ctrl_trackball    -> trackball control
  * game_console_var_ctrl_spinner      -> spinner_knob control
  * game_console_var_ctrl_slider       -> linear_slider control
  * game_console_var_stations_x2 / _x4 -> station multiplicity copy-logic
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

BodyStyle = Literal["wedge_cabinet", "upright_box", "cocktail_flattop", "bartop_crown"]
ControlStyle = Literal["ball_top_joystick", "trackball", "spinner_knob", "linear_slider"]
PaletteStyle = Literal[
    "weathered_blue",
    "arcade_red",
    "midnight_black",
    "retro_teal",
    "cream_yellow",
]

BODY_STYLES: tuple[BodyStyle, ...] = (
    "wedge_cabinet",
    "upright_box",
    "cocktail_flattop",
    "bartop_crown",
)
CONTROL_STYLES: tuple[ControlStyle, ...] = (
    "ball_top_joystick",
    "trackball",
    "spinner_knob",
    "linear_slider",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "weathered_blue",
    "arcade_red",
    "midnight_black",
    "retro_teal",
    "cream_yellow",
)

N_MIN = 1
N_MAX = 6
# Station-count sampling weights: small N high-frequency, large N rare (real
# arcade cabinets are mostly 1-4 player; spec §8).
STATION_COUNT_WEIGHTS = (0.34, 0.28, 0.18, 0.12, 0.05, 0.03)

# ---------------------------------------------------------------------------
# Palettes — realistic arcade colorways. Roles drawn from the 5-star sources
# (blue sheet-metal shell, dark trim, dark screen, gold marquee/keypad, red
# control plate, metal seats, a colored hero control + darker control stem).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "weathered_blue": {  # parent / source colorway
        "shell": (0.16, 0.24, 0.62, 1.0),
        "trim": (0.10, 0.10, 0.12, 1.0),
        "screen": (0.06, 0.06, 0.07, 1.0),
        "marquee": (0.80, 0.66, 0.12, 1.0),
        "keypad": (0.72, 0.60, 0.20, 1.0),
        "plate": (0.62, 0.10, 0.10, 1.0),
        "access": (0.18, 0.16, 0.15, 1.0),
        "screw": (0.55, 0.55, 0.58, 1.0),
        "seat": (0.45, 0.45, 0.48, 1.0),
        "control_primary": (0.12, 0.32, 0.85, 1.0),
        "control_stem": (0.20, 0.20, 0.22, 1.0),
    },
    "arcade_red": {
        "shell": (0.66, 0.12, 0.12, 1.0),
        "trim": (0.09, 0.09, 0.10, 1.0),
        "screen": (0.05, 0.05, 0.06, 1.0),
        "marquee": (0.94, 0.86, 0.30, 1.0),
        "keypad": (0.92, 0.82, 0.24, 1.0),
        "plate": (0.10, 0.10, 0.12, 1.0),
        "access": (0.16, 0.14, 0.14, 1.0),
        "screw": (0.60, 0.60, 0.62, 1.0),
        "seat": (0.50, 0.50, 0.53, 1.0),
        "control_primary": (0.96, 0.94, 0.20, 1.0),
        "control_stem": (0.18, 0.18, 0.20, 1.0),
    },
    "midnight_black": {
        "shell": (0.10, 0.10, 0.12, 1.0),
        "trim": (0.04, 0.04, 0.05, 1.0),
        "screen": (0.03, 0.03, 0.05, 1.0),
        "marquee": (0.30, 0.78, 0.92, 1.0),
        "keypad": (0.78, 0.20, 0.22, 1.0),
        "plate": (0.16, 0.16, 0.18, 1.0),
        "access": (0.08, 0.08, 0.09, 1.0),
        "screw": (0.52, 0.52, 0.55, 1.0),
        "seat": (0.40, 0.40, 0.44, 1.0),
        "control_primary": (0.30, 0.78, 0.92, 1.0),
        "control_stem": (0.14, 0.14, 0.16, 1.0),
    },
    "retro_teal": {
        "shell": (0.10, 0.52, 0.50, 1.0),
        "trim": (0.08, 0.10, 0.10, 1.0),
        "screen": (0.05, 0.06, 0.06, 1.0),
        "marquee": (0.95, 0.55, 0.18, 1.0),
        "keypad": (0.92, 0.78, 0.30, 1.0),
        "plate": (0.86, 0.30, 0.16, 1.0),
        "access": (0.14, 0.16, 0.16, 1.0),
        "screw": (0.58, 0.58, 0.58, 1.0),
        "seat": (0.46, 0.48, 0.48, 1.0),
        "control_primary": (0.95, 0.42, 0.14, 1.0),
        "control_stem": (0.18, 0.20, 0.20, 1.0),
    },
    "cream_yellow": {
        "shell": (0.90, 0.84, 0.58, 1.0),
        "trim": (0.20, 0.16, 0.12, 1.0),
        "screen": (0.06, 0.06, 0.07, 1.0),
        "marquee": (0.78, 0.20, 0.30, 1.0),
        "keypad": (0.84, 0.36, 0.20, 1.0),
        "plate": (0.30, 0.34, 0.66, 1.0),
        "access": (0.36, 0.30, 0.22, 1.0),
        "screw": (0.50, 0.48, 0.44, 1.0),
        "seat": (0.55, 0.52, 0.46, 1.0),
        "control_primary": (0.86, 0.24, 0.32, 1.0),
        "control_stem": (0.24, 0.22, 0.20, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base geometry (meters). Body floor sits at z = BASE_H (pedestal beneath).
# ---------------------------------------------------------------------------
BASE_H = 0.045
WALL = 0.014

# Tall-family cabinet (wedge / upright / bartop) base dims; cocktail is its own.
TALL_W = 0.420
TALL_D = 0.460
TALL_H = 0.560
COCKTAIL_W = 0.780
COCKTAIL_D = 0.560
COCKTAIL_H = 0.320

LOWER_FRONT_H = 0.250
CONTROL_BAND_H = 0.085
SLOPE_TOP_BACK_Y = -0.060
CONTROL_SETBACK = 0.055

# Station / control-deck geometry.
STATION_W = 0.150  # red station plate width (X)
STATION_D = 0.064  # station plate depth (Y)
PLATE_T = 0.012
DECK_MARGIN = 0.045
STATION_SPACING_BASE = 0.178

BODY_BASE_W: dict[str, float] = {
    "wedge_cabinet": TALL_W,
    "upright_box": TALL_W,
    "cocktail_flattop": COCKTAIL_W,
    "bartop_crown": TALL_W,
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ArcadeCabinetConfig:
    body_style: BodyStyle | None = None
    control_style: ControlStyle | None = None
    station_count: int | None = None
    palette_style: PaletteStyle = "weathered_blue"
    cab_width_scale: float = 1.0
    station_spacing_scale: float = 1.0
    control_travel_scale: float = 1.0
    name: str = "arcade_cabinet"


@dataclass(frozen=True)
class ResolvedArcadeCabinetConfig:
    body_style: BodyStyle
    control_style: ControlStyle
    station_count: int
    palette_style: PaletteStyle
    cab_w: float
    cab_d: float
    cab_h: float
    station_spacing: float
    control_travel_scale: float
    name: str


def config_from_seed(seed: int) -> ArcadeCabinetConfig:
    rng = random.Random(seed)
    return ArcadeCabinetConfig(
        body_style=rng.choice(BODY_STYLES),
        control_style=rng.choice(CONTROL_STYLES),
        station_count=rng.choices(
            range(N_MIN, N_MAX + 1), weights=STATION_COUNT_WEIGHTS, k=1
        )[0],
        palette_style=rng.choice(PALETTE_STYLES),
        cab_width_scale=round(rng.uniform(0.88, 1.22), 4),
        station_spacing_scale=round(rng.uniform(0.88, 1.14), 4),
        control_travel_scale=round(rng.uniform(0.82, 1.18), 4),
        name=f"seeded_arcade_cabinet_{seed}",
    )


def resolve_config(config: ArcadeCabinetConfig | None = None) -> ResolvedArcadeCabinetConfig:
    cfg = config or ArcadeCabinetConfig()
    body_style = _pick(cfg.body_style, BODY_STYLES)
    control_style = _pick(cfg.control_style, CONTROL_STYLES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    n = int(cfg.station_count) if cfg.station_count is not None else 1
    n = int(_clamp(n, N_MIN, N_MAX))

    spacing = _clamp(STATION_SPACING_BASE * float(cfg.station_spacing_scale), 0.150, 0.220)
    width_scale = _clamp(float(cfg.cab_width_scale), 0.85, 1.25)
    travel_scale = _clamp(float(cfg.control_travel_scale), 0.8, 1.2)

    base_w = BODY_BASE_W[body_style]
    cab_w = base_w * width_scale
    # Conditional inequality (spec §7): the N-station row must fit on the deck.
    # row_width = (N-1)*spacing + STATION_W; required cab_w >= row + 2*margin.
    needed_w = (n - 1) * spacing + STATION_W + 2.0 * DECK_MARGIN
    if cab_w < needed_w:
        cab_w = needed_w

    if body_style == "cocktail_flattop":
        cab_d, cab_h = COCKTAIL_D, COCKTAIL_H
    else:
        cab_d, cab_h = TALL_D, TALL_H

    return ResolvedArcadeCabinetConfig(
        body_style=body_style,
        control_style=control_style,
        station_count=n,
        palette_style=palette_style,
        cab_w=cab_w,
        cab_d=cab_d,
        cab_h=cab_h,
        station_spacing=spacing,
        control_travel_scale=travel_scale,
        name=cfg.name or "arcade_cabinet",
    )


def slot_choices_for_config(
    config: ArcadeCabinetConfig | ResolvedArcadeCabinetConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedArcadeCabinetConfig)
        else resolve_config(config)
    )
    return (
        ("body", r.body_style),
        ("control", r.control_style),
        ("stations", f"n{r.station_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Cabinet shell meshes (Rule 3: keep the source CadQuery shell topology).
# Built in a frame whose origin is the body floor center; z measured from floor.
# ---------------------------------------------------------------------------
def _wedge_shell(W: float, D: float, H: float) -> cq.Workplane:
    """Hollow wedge shell (parent a5689b50 _build_cabinet_shell)."""
    front_y = D / 2.0
    back_y = -D / 2.0
    lower_top = LOWER_FRONT_H
    control_top = lower_top + CONTROL_BAND_H
    side = [
        (back_y, 0.0),
        (back_y, H),
        (SLOPE_TOP_BACK_Y, H),
        (front_y - CONTROL_SETBACK, control_top),
        (front_y - CONTROL_SETBACK, lower_top),
        (front_y, lower_top),
        (front_y, 0.0),
    ]
    outer = cq.Workplane("YZ").polyline(side).close().extrude(W / 2.0, both=True)
    inner_side = [
        (back_y + WALL, WALL),
        (back_y + WALL, H - WALL),
        (SLOPE_TOP_BACK_Y, H - WALL),
        (front_y - CONTROL_SETBACK - WALL, control_top - WALL),
        (front_y - CONTROL_SETBACK - WALL, lower_top + WALL),
        (front_y - WALL, lower_top + WALL),
        (front_y - WALL, WALL),
    ]
    inner = cq.Workplane("YZ").polyline(inner_side).close().extrude((W / 2.0) - WALL, both=True)
    return outer.cut(inner).edges("|X").fillet(0.006)


def _upright_shell(W: float, D: float, H: float) -> cq.Workplane:
    """Hollow rectilinear box shell (upright_box _build_cabinet_shell)."""
    front_y = D / 2.0
    back_y = -D / 2.0
    side = [(back_y, 0.0), (back_y, H), (front_y, H), (front_y, 0.0)]
    outer = cq.Workplane("YZ").polyline(side).close().extrude(W / 2.0, both=True)
    inner_side = [
        (back_y + WALL, -WALL),
        (back_y + WALL, H - WALL),
        (front_y - WALL, H - WALL),
        (front_y - WALL, -WALL),
    ]
    inner = cq.Workplane("YZ").polyline(inner_side).close().extrude((W / 2.0) - WALL, both=True)
    return outer.cut(inner).edges("|X").fillet(0.006)


def _cocktail_shell(W: float, D: float, H: float) -> cq.Workplane:
    """Hollow low wide cocktail-table shell (cocktail _build_cabinet_shell)."""
    outer = (
        cq.Workplane("XY")
        .box(W, D, H, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.012)
    )
    inner = (
        cq.Workplane("XY")
        .box(W - 2 * WALL, D - 2 * WALL, H - WALL + 0.006, centered=(True, True, False))
        .translate((0.0, 0.0, -0.003))
    )
    return outer.cut(inner)


# bartop screen-face geometry constants.
SCREEN_FACE_TOP_LOCAL = 0.492
CROWN_PEAK_RISE = 0.034


def _bartop_shell(W: float, D: float, H: float) -> cq.Workplane:
    """Hollow bartop shell with arc marquee crown (bartop _build_cabinet_shell)."""
    front_y = D / 2.0
    back_y = -D / 2.0
    screen_face_y = front_y - CONTROL_SETBACK
    lower_top = LOWER_FRONT_H
    control_top = lower_top + CONTROL_BAND_H
    screen_top = SCREEN_FACE_TOP_LOCAL
    crown_mid = ((back_y + screen_face_y) / 2.0, H + CROWN_PEAK_RISE)
    outer = (
        cq.Workplane("YZ")
        .moveTo(back_y, 0.0)
        .lineTo(back_y, H)
        .threePointArc(crown_mid, (screen_face_y, screen_top))
        .lineTo(screen_face_y, control_top)
        .lineTo(screen_face_y, lower_top)
        .lineTo(front_y, lower_top)
        .lineTo(front_y, 0.0)
        .close()
        .extrude(W / 2.0, both=True)
    )
    inner_crown_mid = (crown_mid[0], crown_mid[1] - WALL * 1.4)
    inner = (
        cq.Workplane("YZ")
        .moveTo(back_y + WALL, WALL)
        .lineTo(back_y + WALL, H - WALL)
        .threePointArc(inner_crown_mid, (screen_face_y - WALL, screen_top - WALL))
        .lineTo(screen_face_y - WALL, control_top + WALL)
        .lineTo(screen_face_y - WALL, lower_top + WALL)
        .lineTo(front_y - WALL, lower_top + WALL)
        .lineTo(front_y - WALL, WALL)
        .close()
        .extrude((W / 2.0) - WALL, both=True)
    )
    return outer.cut(inner).edges("|X").fillet(0.006)


def _bartop_crown(W: float, D: float, H: float) -> cq.Workplane:
    """Raised dark trim following the rounded marquee crown arc."""
    front_y = D / 2.0
    back_y = -D / 2.0
    screen_face_y = front_y - CONTROL_SETBACK
    screen_top = SCREEN_FACE_TOP_LOCAL
    outer_mid = ((back_y + screen_face_y) / 2.0, H + CROWN_PEAK_RISE + 0.006)
    inner_mid = (outer_mid[0], outer_mid[1] - 0.018)
    rear_outer = (back_y + 0.018, H + 0.002)
    front_outer = (screen_face_y + 0.006, screen_top + 0.004)
    front_inner = (screen_face_y - 0.002, screen_top - 0.012)
    rear_inner = (back_y + 0.030, H - 0.015)
    return (
        cq.Workplane("YZ")
        .moveTo(*rear_outer)
        .threePointArc(outer_mid, front_outer)
        .lineTo(*front_inner)
        .threePointArc(inner_mid, rear_inner)
        .close()
        .extrude((W / 2.0) - 0.018, both=True)
        .edges("|X")
        .fillet(0.003)
    )


_SHELL_BUILDERS = {
    "wedge_cabinet": _wedge_shell,
    "upright_box": _upright_shell,
    "cocktail_flattop": _cocktail_shell,
    "bartop_crown": _bartop_shell,
}


# ---------------------------------------------------------------------------
# Control-face descriptor per body style. The control deck is a horizontal
# mounting surface; stations stand vertically on it (axis-aligned seats), so
# the MatingContract is clean for every body style.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ControlFace:
    deck_top_z: float  # world Z of the deck top surface (stations sit on it)
    face_y: float  # world Y center of the station row
    shelf_depth: float


def _control_face(r: ResolvedArcadeCabinetConfig) -> ControlFace:
    z_floor = BASE_H
    if r.body_style == "cocktail_flattop":
        deck_top = z_floor + r.cab_h  # top deck
        return ControlFace(deck_top_z=deck_top, face_y=0.120, shelf_depth=0.180)
    # tall family: control band / shelf height.
    deck_top = z_floor + LOWER_FRONT_H + CONTROL_BAND_H  # Z_CONTROL_TOP
    front_y = r.cab_d / 2.0
    if r.body_style == "upright_box":
        face_y = front_y + 0.045  # shelf projects forward of the flat front
    elif r.body_style == "bartop_crown":
        # Bartop screen is vertical directly above the band, so the control row
        # must sit well forward of the screen plane to clear tall controls.
        face_y = front_y - 0.010
    else:  # wedge: recessed control band under the sloped screen
        face_y = front_y - CONTROL_SETBACK + 0.020
    return ControlFace(deck_top_z=deck_top, face_y=face_y, shelf_depth=0.150)


# ---------------------------------------------------------------------------
# Screen + marquee (parent visuals on the cabinet body, per body style).
# ---------------------------------------------------------------------------
def _screen_face_w(r: ResolvedArcadeCabinetConfig) -> float:
    return min(r.cab_w - 0.060, 0.380)


def _emit_screen(cabinet, r: ResolvedArcadeCabinetConfig, mats) -> None:
    z_floor = BASE_H
    front_y = r.cab_d / 2.0
    face_w = _screen_face_w(r)

    if r.body_style == "wedge_cabinet":
        y_top, z_top = SLOPE_TOP_BACK_Y, r.cab_h
        y_bot = front_y - CONTROL_SETBACK
        z_bot = LOWER_FRONT_H + CONTROL_BAND_H
        cy = (y_top + y_bot) / 2.0
        cz = z_floor + (z_top + z_bot) / 2.0
        length = math.hypot(y_bot - y_top, z_bot - z_top) * 0.92
        pitch = math.atan2(z_bot - z_top, y_bot - y_top)
        n_y, n_z = -math.sin(pitch), math.cos(pitch)
        cabinet.visual(
            Box((face_w + 0.024, length, 0.010)),
            origin=Origin(xyz=(0.0, cy, cz), rpy=(pitch, 0.0, 0.0)),
            material=mats["trim"],
            name="screen_bezel", material_class_id="metal.paint_coated",
        )
        cabinet.visual(
            Box((face_w, length - 0.020, 0.008)),
            origin=Origin(xyz=(0.0, cy + 0.004 * n_y, cz + 0.004 * n_z), rpy=(pitch, 0.0, 0.0)),
            material=mats["screen"],
            name="screen_glass", material_class_id="glass.smoked_tinted",
        )
        ty = -length * 0.12 * math.cos(pitch)
        tz = -length * 0.12 * math.sin(pitch)
        cabinet.visual(
            Box((face_w * 0.60, length * 0.16, 0.004)),
            origin=Origin(
                xyz=(face_w * 0.05, cy + ty + 0.009 * n_y, cz + tz + 0.009 * n_z),
                rpy=(pitch, 0.0, 0.0),
            ),
            material=mats["marquee"],
            name="game_over_text", appearance_only=AppearanceOnlySpec(kind="screen", text="GAME OVER", emission_strength=1.0),
        )

    elif r.body_style == "upright_box":
        z_control_top = z_floor + LOWER_FRONT_H + CONTROL_BAND_H
        z_top = z_floor + r.cab_h
        screen_h = min(0.205, z_top - z_control_top - 0.030)
        cz = z_control_top + 0.020 + screen_h / 2.0
        cabinet.visual(
            Box((face_w + 0.030, 0.010, screen_h + 0.030)),
            origin=Origin(xyz=(0.0, front_y, cz)),
            material=mats["trim"],
            name="screen_bezel", material_class_id="metal.paint_coated",
        )
        cabinet.visual(
            Box((face_w - 0.012, 0.008, screen_h - 0.012)),
            origin=Origin(xyz=(0.0, front_y + 0.003, cz)),
            material=mats["screen"],
            name="screen_glass", material_class_id="glass.smoked_tinted",
        )
        cabinet.visual(
            Box((face_w * 0.60, 0.004, screen_h * 0.15)),
            origin=Origin(xyz=(face_w * 0.05, front_y + 0.008, cz + screen_h * 0.12)),
            material=mats["marquee"],
            name="game_over_text", appearance_only=AppearanceOnlySpec(kind="screen", text="GAME OVER", emission_strength=1.0),
        )

    elif r.body_style == "cocktail_flattop":
        deck_z = z_floor + r.cab_h
        screen_w = min(face_w + 0.10, r.cab_w - 0.20)
        screen_d = 0.270
        scy = -0.070
        cabinet.visual(
            Box((screen_w + 0.040, screen_d + 0.040, 0.006)),
            origin=Origin(xyz=(0.0, scy, deck_z - 0.004)),
            material=mats["trim"],
            name="screen_bezel", material_class_id="metal.paint_coated",
        )
        cabinet.visual(
            Box((screen_w, screen_d, 0.006)),
            origin=Origin(xyz=(0.0, scy, deck_z - 0.0015)),
            material=mats["screen"],
            name="screen_glass", material_class_id="glass.smoked_tinted",
        )
        cabinet.visual(
            Box((screen_w * 0.55, screen_d * 0.13, 0.0025)),
            origin=Origin(xyz=(screen_w * 0.04, scy - screen_d * 0.12, deck_z + 0.0008)),
            material=mats["marquee"],
            name="game_over_text", appearance_only=AppearanceOnlySpec(kind="screen", text="GAME OVER", emission_strength=1.0),
        )

    else:  # bartop_crown — vertical screen on the setback face
        screen_face_y = front_y - CONTROL_SETBACK
        z_control_top = z_floor + LOWER_FRONT_H + CONTROL_BAND_H
        screen_top = z_floor + SCREEN_FACE_TOP_LOCAL
        screen_h = (screen_top - z_control_top) * 0.92
        cz = (z_control_top + screen_top) / 2.0
        cabinet.visual(
            Box((face_w + 0.024, 0.010, screen_h + 0.018)),
            origin=Origin(xyz=(0.0, screen_face_y + 0.006, cz)),
            material=mats["trim"],
            name="screen_bezel", material_class_id="metal.paint_coated",
        )
        cabinet.visual(
            Box((face_w - 0.010, 0.006, screen_h - 0.022)),
            origin=Origin(xyz=(0.0, screen_face_y + 0.011, cz)),
            material=mats["screen"],
            name="screen_glass", material_class_id="glass.smoked_tinted",
        )
        cabinet.visual(
            Box((face_w * 0.58, 0.004, screen_h * 0.16)),
            origin=Origin(xyz=(face_w * 0.05, screen_face_y + 0.015, cz + screen_h * 0.18)),
            material=mats["marquee"],
            name="game_over_text", appearance_only=AppearanceOnlySpec(kind="screen", text="GAME OVER", emission_strength=1.0),
        )


# ---------------------------------------------------------------------------
# Lower-front access panel + corner screws (parent visuals).
# ---------------------------------------------------------------------------
def _emit_access_panel(cabinet, r: ResolvedArcadeCabinetConfig, mats) -> None:
    z_floor = BASE_H
    front_y = r.cab_d / 2.0
    if r.body_style == "cocktail_flattop":
        panel_w = min(r.cab_w - 0.34, 0.42)
        panel_h = r.cab_h - 0.160
        panel_cz = z_floor + r.cab_h / 2.0
    else:
        panel_w = min(r.cab_w - 0.110, 0.40)
        panel_h = LOWER_FRONT_H - 0.090
        panel_cz = z_floor + LOWER_FRONT_H / 2.0
    cabinet.visual(
        Box((panel_w, 0.010, panel_h)),
        origin=Origin(xyz=(0.0, front_y - 0.001, panel_cz)),
        material=mats["access"],
        name="access_panel", material_class_id="metal.paint_coated",
    )
    for i, (sx, sz) in enumerate(((-1, 1), (1, 1), (-1, -1), (1, -1))):
        scx = sx * (panel_w / 2.0 - 0.018)
        scz = panel_cz + sz * (panel_h / 2.0 - 0.018)
        cabinet.visual(
            Cylinder(radius=0.0045, length=0.010),
            origin=Origin(xyz=(scx, front_y + 0.003, scz), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["screw"],
            name=f"access_screw_{i}", material_class_id="metal.stainless_matte",
        )


# ---------------------------------------------------------------------------
# Reusable control-mechanism geometry (built once per type, reused per station).
# ---------------------------------------------------------------------------
def _knurled_spinner_body(assets):
    """One-piece knurled spinner knob + paddle (spinner _build_knurled_spinner_body)."""
    radius = 0.025
    height = 0.026
    rib_count = 16
    knob = cq.Workplane("XY").circle(radius).extrude(height)
    for i in range(rib_count):
        angle = 360.0 * i / rib_count
        rib = (
            cq.Workplane("XY")
            .box(0.005, 0.0032, 0.021)
            .translate((radius + 0.005 / 2.0 - 0.0012, 0.0, 0.004 + 0.021 / 2.0))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        )
        knob = knob.union(rib)
    top_boss = cq.Workplane("XY").circle(0.018).extrude(0.006).translate((0.0, 0.0, height - 0.001))
    paddle = (
        cq.Workplane("XY")
        .box(0.066, 0.008, 0.008)
        .edges("|Z")
        .fillet(0.002)
        .translate((0.0, 0.0, height + 0.002))
    )
    knob = knob.union(top_boss).union(paddle)
    return mesh_from_cadquery(knob, "spinner_body", assets=assets)


def _joystick_boot(assets):
    boot = cq.Workplane("XY").circle(0.013).workplane(offset=0.012).circle(0.007).loft()
    return mesh_from_cadquery(boot, "joystick_boot", assets=assets)


def _slider_thumb(assets):
    thumb = (
        cq.Workplane("XY")
        .box(0.034, 0.026, 0.016, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.006)
    )
    return mesh_from_cadquery(thumb, "slider_thumb", assets=assets)


# ---------------------------------------------------------------------------
# Per-station emission. Emits the station's parent visuals (bezel / plate /
# buttons / seat) onto the cabinet, plus the movable control child part + joint.
# Returns a dict with joint name + element-overlap pairs for run_tests.
# ---------------------------------------------------------------------------
def _emit_station(
    model: ArticulatedObject,
    cabinet,
    r: ResolvedArcadeCabinetConfig,
    mats,
    *,
    i: int,
    station_x: float,
    face: ControlFace,
    shared,
    assets,
) -> dict:
    deck_top = face.deck_top_z
    fy = face.face_y
    plate_top = deck_top + PLATE_T

    # Dark inset bezel under the station plate (reads as a mounted control module).
    cabinet.visual(
        Box((STATION_W + 0.014, STATION_D + 0.012, 0.006)),
        origin=Origin(xyz=(station_x, fy, deck_top + 0.003)),
        material=mats["trim"],
        name=f"station_bezel_{i}", material_class_id="metal.paint_coated",
    )
    # Red control plate.
    cabinet.visual(
        Box((STATION_W, STATION_D, PLATE_T)),
        origin=Origin(xyz=(station_x, fy, deck_top + PLATE_T / 2.0)),
        material=mats["plate"],
        name=f"station_plate_{i}", material_class_id="metal.paint_coated",
    )
    # Gold pushbutton cluster on the plate (reuse the shared mesh).
    cabinet.visual(
        shared["buttons"],
        origin=Origin(xyz=(station_x + 0.043, fy - 0.004, plate_top)),
        material=mats["keypad"],
        name=f"station_buttons_{i}", material_class_id="plastic.opaque_glossy_molded",
    )

    ctrl = r.control_style
    seat_x = station_x - 0.034  # control sits on the player's left of the plate

    if ctrl == "ball_top_joystick":
        seat_h = 0.010
        seat_top = plate_top + seat_h
        cabinet.visual(
            Cylinder(radius=0.014, length=seat_h),
            origin=Origin(xyz=(seat_x, fy, plate_top + seat_h / 2.0)),
            material=mats["seat"],
            name=f"collar_{i}", material_class_id="metal.stainless_matte",
        )
        part = model.part(f"joystick_{i}")
        shaft_len = 0.055
        part.visual(
            Cylinder(radius=0.006, length=shaft_len),
            origin=Origin(xyz=(0.0, 0.0, shaft_len / 2.0)),
            material=mats["control_stem"],
            name=f"shaft_{i}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            shared["boot"],
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["seat"],
            name=f"boot_{i}", material_class_id="rubber.smooth_plain",
        )
        part.visual(
            Sphere(radius=0.018),
            origin=Origin(xyz=(0.0, 0.0, shaft_len + 0.012)),
            material=mats["control_primary"],
            name=f"ball_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        part.inertial = Inertial.from_geometry(
            Box((0.040, 0.040, shaft_len + 0.030)),
            mass=0.08,
            origin=Origin(xyz=(0.0, 0.0, (shaft_len + 0.030) / 2.0)),
        )
        lim = 0.45 * r.control_travel_scale
        model.articulation(
            f"deck_to_joystick_{i}",
            ArticulationType.REVOLUTE,
            parent=cabinet,
            child=part,
            origin=Origin(xyz=(seat_x, fy, seat_top)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=4.0, lower=-lim, upper=lim),
            mating=MatingContract(
                parent_face_geometry=f"collar_{i}",
                parent_face_side="positive_z",
                child_face_geometry=f"boot_{i}",
                child_face_side="negative_z",
                contact_tol=0.004,
            ),
        )
        overlaps = [(f"boot_{i}", f"collar_{i}"), (f"shaft_{i}", f"collar_{i}")]
        return {"joint": f"deck_to_joystick_{i}", "part": f"joystick_{i}", "overlaps": overlaps}

    if ctrl == "trackball":
        seat_h = 0.008
        seat_top = plate_top + seat_h
        cabinet.visual(
            Cylinder(radius=0.030, length=seat_h),
            origin=Origin(xyz=(seat_x, fy, plate_top + seat_h / 2.0)),
            material=mats["seat"],
            name=f"cup_{i}", material_class_id="metal.stainless_matte",
        )
        part = model.part(f"trackball_{i}")
        part.visual(
            Cylinder(radius=0.016, length=0.005),
            origin=Origin(xyz=(0.0, 0.0, 0.0025)),
            material=mats["control_stem"],
            name=f"hub_{i}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Sphere(radius=0.022),
            origin=Origin(xyz=(0.0, 0.0, 0.020)),
            material=mats["control_primary"],
            name=f"sphere_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        part.inertial = Inertial.from_geometry(
            Cylinder(radius=0.022, length=0.044),
            mass=0.05,
            origin=Origin(xyz=(0.0, 0.0, 0.020)),
        )
        model.articulation(
            f"deck_to_trackball_{i}",
            ArticulationType.REVOLUTE,
            parent=cabinet,
            child=part,
            origin=Origin(xyz=(seat_x, fy, seat_top)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=1.0, velocity=8.0, lower=-math.pi, upper=math.pi),
            mating=MatingContract(
                parent_face_geometry=f"cup_{i}",
                parent_face_side="positive_z",
                child_face_geometry=f"hub_{i}",
                child_face_side="negative_z",
                contact_tol=0.004,
            ),
        )
        overlaps = [(f"sphere_{i}", f"cup_{i}"), (f"hub_{i}", f"cup_{i}")]
        return {"joint": f"deck_to_trackball_{i}", "part": f"trackball_{i}", "overlaps": overlaps}

    if ctrl == "spinner_knob":
        seat_h = 0.026
        seat_top = plate_top + seat_h
        cabinet.visual(
            Cylinder(radius=0.017, length=seat_h),
            origin=Origin(xyz=(seat_x, fy, plate_top + seat_h / 2.0)),
            material=mats["seat"],
            name=f"bearing_{i}", material_class_id="metal.stainless_matte",
        )
        part = model.part(f"spinner_{i}")
        part.visual(
            Cylinder(radius=0.0065, length=0.014),
            origin=Origin(xyz=(0.0, 0.0, -0.005)),
            material=mats["control_stem"],
            name=f"stem_{i}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            shared["spinner_body"],
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["control_primary"],
            name=f"spinner_body_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        part.inertial = Inertial.from_geometry(
            Cylinder(radius=0.033, length=0.034),
            mass=0.06,
            origin=Origin(xyz=(0.0, 0.0, 0.016)),
        )
        model.articulation(
            f"deck_to_spinner_{i}",
            ArticulationType.CONTINUOUS,
            parent=cabinet,
            child=part,
            origin=Origin(xyz=(seat_x, fy, seat_top)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=18.0),
            mating=MatingContract(
                parent_face_geometry=f"bearing_{i}",
                parent_face_side="positive_z",
                child_face_geometry=f"spinner_body_{i}",
                child_face_side="negative_z",
                contact_tol=0.004,
            ),
        )
        overlaps = [(f"stem_{i}", f"bearing_{i}"), (f"spinner_body_{i}", f"bearing_{i}")]
        return {"joint": f"deck_to_spinner_{i}", "part": f"spinner_{i}", "overlaps": overlaps}

    # linear_slider
    seat_h = 0.006
    seat_top = plate_top + seat_h
    rail_w = STATION_W * 0.55
    cabinet.visual(
        Box((rail_w, 0.024, seat_h)),
        origin=Origin(xyz=(seat_x, fy, plate_top + seat_h / 2.0)),
        material=mats["seat"],
        name=f"rail_{i}", material_class_id="metal.stainless_matte",
    )
    part = model.part(f"slider_{i}")
    part.visual(
        Box((0.028, 0.014, 0.008)),
        origin=Origin(xyz=(0.0, 0.0, -0.002)),
        material=mats["control_stem"],
        name=f"runner_{i}", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        shared["thumb"],
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["control_primary"],
        name=f"thumb_{i}", material_class_id="plastic.opaque_glossy_molded",
    )
    part.inertial = Inertial.from_geometry(
        Box((0.034, 0.026, 0.024)),
        mass=0.04,
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
    )
    travel = 0.018 * r.control_travel_scale
    model.articulation(
        f"deck_to_slider_{i}",
        ArticulationType.PRISMATIC,
        parent=cabinet,
        child=part,
        origin=Origin(xyz=(seat_x, fy, seat_top)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=0.18, lower=-travel, upper=travel),
        mating=MatingContract(
            parent_face_geometry=f"rail_{i}",
            parent_face_side="positive_z",
            child_face_geometry=f"thumb_{i}",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )
    overlaps = [(f"runner_{i}", f"rail_{i}"), (f"thumb_{i}", f"rail_{i}")]
    return {"joint": f"deck_to_slider_{i}", "part": f"slider_{i}", "overlaps": overlaps}


def _station_x_positions(r: ResolvedArcadeCabinetConfig) -> list[float]:
    n = r.station_count
    spacing = r.station_spacing
    return [(-0.5 * (n - 1) + i) * spacing for i in range(n)]


def _shared_buttons(assets):
    buttons = (
        cq.Workplane("XY")
        .rarray(0.016, 0.016, 3, 2)
        .box(0.010, 0.010, 0.004, centered=(True, True, False))
    )
    return mesh_from_cadquery(buttons, "station_buttons", assets=assets)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_arcade_cabinet(
    config: ArcadeCabinetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"arcade_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    cabinet = model.part("cabinet_body")

    # Shell mesh (Rule 3: keep the source CadQuery shell topology).
    shell = _SHELL_BUILDERS[r.body_style](r.cab_w, r.cab_d, r.cab_h)
    cabinet.visual(
        mesh_from_cadquery(shell, "cabinet_shell", assets=assets),
        origin=Origin(xyz=(0.0, 0.0, BASE_H)),
        material=mats["shell"],
        name="cabinet_shell", material_class_id="metal.paint_coated",
    )
    if r.body_style == "bartop_crown":
        cabinet.visual(
            mesh_from_cadquery(_bartop_crown(r.cab_w, r.cab_d, r.cab_h), "marquee_crown", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, BASE_H)),
            material=mats["trim"],
            name="marquee_crown", material_class_id="metal.paint_coated",
        )

    # Base pedestal. Top embeds slightly into the shell bottom so it is always a
    # supported visual; cocktail has an open-bottom shell, so its pedestal must
    # reach the wall ring (small inset), not float under the cavity opening.
    if r.body_style == "upright_box":
        inset = 0.0
    elif r.body_style == "cocktail_flattop":
        inset = 0.006
    else:
        inset = 0.030
    ped_h = BASE_H + 0.006
    cabinet.visual(
        Box((r.cab_w - 2 * inset, r.cab_d - 2 * inset, ped_h)),
        origin=Origin(xyz=(0.0, 0.0, ped_h / 2.0)),
        material=mats["trim"],
        name="base_pedestal", material_class_id="metal.paint_coated",
    )

    cabinet.inertial = Inertial.from_geometry(
        Box((r.cab_w, r.cab_d, r.cab_h + BASE_H)),
        mass=18.0,
        origin=Origin(xyz=(0.0, 0.0, (r.cab_h + BASE_H) / 2.0)),
    )

    _emit_screen(cabinet, r, mats)
    _emit_access_panel(cabinet, r, mats)

    face = _control_face(r)

    # Control deck/shelf — a horizontal mounting surface that the stations rest
    # on; its back edge embeds into the shell so it is a supported visual.
    deck_w = r.cab_w - 2 * DECK_MARGIN
    cabinet.visual(
        Box((deck_w, face.shelf_depth, 0.020)),
        origin=Origin(xyz=(0.0, face.face_y, face.deck_top_z - 0.010)),
        material=mats["shell"],
        name="control_deck", material_class_id="metal.paint_coated",
    )

    # Shared (identical-per-station) control geometry, built once.
    shared = {"buttons": _shared_buttons(assets)}
    if r.control_style == "ball_top_joystick":
        shared["boot"] = _joystick_boot(assets)
    elif r.control_style == "spinner_knob":
        shared["spinner_body"] = _knurled_spinner_body(assets)
    elif r.control_style == "linear_slider":
        shared["thumb"] = _slider_thumb(assets)

    stations = []
    for i, sx in enumerate(_station_x_positions(r)):
        stations.append(
            _emit_station(
                model, cabinet, r, mats, i=i, station_x=sx, face=face, shared=shared, assets=assets
            )
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["stations"] = stations
    return model


def build_seeded_arcade_cabinet(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_arcade_cabinet(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_arcade_cabinet_tests(
    object_model: ArticulatedObject,
    config: ArcadeCabinetConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    cabinet = object_model.get_part("cabinet_body")

    stations = list(object_model.meta.get("stations", []))

    # ---- Captured-fit allowances (element-scoped, per spec / source). ----
    for st in stations:
        child = object_model.get_part(st["part"])
        for child_elem, parent_elem in st["overlaps"]:
            ctx.allow_overlap(
                child,
                cabinet,
                elem_a=child_elem,
                elem_b=parent_elem,
                reason="Captured-fit control mechanism seated into its cabinet seat by design.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("cabinet_body root present", "cabinet_body" in part_names, details=str(sorted(part_names)))
    ctx.check(
        "N control stations present",
        len(stations) == r.station_count,
        details=f"stations={len(stations)} expected N={r.station_count}",
    )

    shell_names = {v.name for v in cabinet.visuals}
    ctx.check("screen glass present", "screen_glass" in shell_names, details=str(sorted(shell_names)))
    ctx.check("cabinet shell present", "cabinet_shell" in shell_names, details="")

    # ---- Joint topology per control style. ----
    expected = {
        "ball_top_joystick": (ArticulationType.REVOLUTE, 0),
        "trackball": (ArticulationType.REVOLUTE, 2),
        "spinner_knob": (ArticulationType.CONTINUOUS, 2),
        "linear_slider": (ArticulationType.PRISMATIC, 0),
    }
    exp_type, exp_axis_idx = expected[r.control_style]
    for st in stations:
        j = object_model.get_articulation(st["joint"])
        ctx.check(
            f"{st['joint']} type",
            j.articulation_type == exp_type,
            details=f"type={j.articulation_type}",
        )
        ctx.check(
            f"{st['joint']} axis",
            abs(abs(j.axis[exp_axis_idx]) - 1.0) < 1e-6,
            details=f"axis={tuple(j.axis)}",
        )

    # ---- Multiplicity layout: stations spaced along X. ----
    if r.station_count >= 2:
        xs = []
        for st in stations:
            part = object_model.get_part(st["part"])
            aabb = ctx.part_world_aabb(part)
            if aabb is not None:
                xs.append((aabb[0][0] + aabb[1][0]) / 2.0)
        if len(xs) >= 2:
            ctx.check(
                "stations are distinct along X",
                all(xs[k + 1] - xs[k] > 0.04 for k in range(len(xs) - 1)),
                details=f"xs={['%.3f' % x for x in xs]}",
            )

    # ---- Decisive articulation pose per control style. ----
    if stations:
        st = stations[0]
        j = object_model.get_articulation(st["joint"])
        part = object_model.get_part(st["part"])
        if r.control_style == "ball_top_joystick":
            rest = ctx.part_element_world_aabb(part, elem=f"ball_0")
            with ctx.pose({j: 0.40 * r.control_travel_scale}):
                fwd = ctx.part_element_world_aabb(part, elem=f"ball_0")
            if rest is not None and fwd is not None:
                ry = (rest[0][1] + rest[1][1]) / 2.0
                fy = (fwd[0][1] + fwd[1][1]) / 2.0
                ctx.check("joystick deflects forward", fy > ry + 0.005, details=f"ry={ry:.3f} fy={fy:.3f}")
        elif r.control_style == "linear_slider":
            p0 = ctx.part_world_position(part)
            with ctx.pose({j: 0.018 * r.control_travel_scale}):
                p1 = ctx.part_world_position(part)
            if p0 is not None and p1 is not None:
                ctx.check("slider travels along X", p1[0] - p0[0] > 0.008, details=f"dx={p1[0]-p0[0]:.4f}")
        elif r.control_style == "trackball":
            rest = ctx.part_element_world_aabb(part, elem=f"sphere_0")
            with ctx.pose({j: 1.2}):
                spun = ctx.part_element_world_aabb(part, elem=f"sphere_0")
            if rest is not None and spun is not None:
                rc = (rest[0][2] + rest[1][2]) / 2.0
                sc = (spun[0][2] + spun[1][2]) / 2.0
                ctx.check("trackball spins in place", abs(sc - rc) < 0.002, details=f"rc={rc:.3f} sc={sc:.3f}")

    # ---- slot_choices recorded with N encoded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "ArcadeCabinetConfig",
    "ResolvedArcadeCabinetConfig",
    "build_arcade_cabinet",
    "build_seeded_arcade_cabinet",
    "config_from_seed",
    "resolve_config",
    "run_arcade_cabinet_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
