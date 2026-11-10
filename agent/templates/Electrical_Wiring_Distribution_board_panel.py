# SPDX-License-Identifier: Apache-2.0

"""distribution_board_panel — modular procedural template.

Category identity: an electrical **distribution board / load-center / panelboard**.
A grounded sheet-metal **enclosure** (or an open backplate chassis) carries a
loop-emitted **breaker FIELD** (DIN rails or vertical columns of MCB modules, a
few of which carry a real revolute toggle, the rest decorative) plus a **mains
assembly** (full power bay / bus bars only / MCB-only sub-board). The defining
articulation is the hinged deadfront door(s); the breaker toggles are the other
moving joints (and the ONLY moving joints for the doorless open backplate form).

Slots (see specs_modular_v1/distribution_board_panel.md):
  A form_module     (③ Primary Form Family + door count):
      single_door       one hinged front door  (Volumetric Envelope Form)
      two_door          two outer-hinged doors  (Volumetric Envelope Form, mullion)
      open_backplate    flat mounting plate, NO door  (Planar Boundary Form)
  B topology_module (breaker field):
      stacked_din_rails rail_count∈{2,3} horizontal DIN rails
      single_din_rail   one horizontal DIN rail
      two_vertical_columns  two vertical breaker columns
  C breaker_per_group / rail_count  (multiplicity — total 6..42 ways)
  D mains_module    (full_main_bay / bus_bars_only / mcb_only_subboard)

Canonical frame: width along X (centered), height along Z (board bottom at z=0),
depth along Y — interior back plane at y=0, front opening toward -Y at
FRONT_Y=-BOARD_D. All STATIC geometry (shell, breaker field, busbars, mains) is
authored as visuals on the single grounded `enclosure` part (Rule 1: it does not
move, so it is not a separate part). Only the door(s) and the real breaker
toggles are separate REVOLUTE parts. Doors are authored CLOSED (hinge q=0 = shut,
opens outward toward -Y) — the S2 convention, NOT S1's baked-open anti-pattern.

Adapted 5-star sources: S1 c548199a (two-column load-center),
S2 4cb00767 (two-bay DIN board), forks open_backplate / single_din_rail /
eight_way / eighteen_way / mcb_only_subboard.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

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
    TestContext,
    TestReport,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum domains
# ---------------------------------------------------------------------------
FormModule = Literal["single_door", "two_door", "open_backplate"]
TopologyModule = Literal["stacked_din_rails", "single_din_rail", "two_vertical_columns"]
MainsModule = Literal["full_main_bay", "bus_bars_only", "mcb_only_subboard"]
PaletteStyle = Literal[
    "industrial_grey",
    "light_grey_powder",
    "municipal_beige",
    "graphite_dark",
    "safety_blue",
]

FORM_MODULES: tuple[FormModule, ...] = ("single_door", "two_door", "open_backplate")
FORM_WEIGHTS = (0.44, 0.34, 0.22)

TOPOLOGY_MODULES: tuple[TopologyModule, ...] = (
    "stacked_din_rails",
    "single_din_rail",
    "two_vertical_columns",
)
TOPOLOGY_WEIGHTS = (0.45, 0.22, 0.33)

MAINS_MODULES: tuple[MainsModule, ...] = (
    "full_main_bay",
    "bus_bars_only",
    "mcb_only_subboard",
)
MAINS_WEIGHTS = (0.34, 0.40, 0.26)

PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "industrial_grey",
    "light_grey_powder",
    "municipal_beige",
    "graphite_dark",
    "safety_blue",
)

# Multiplicity axes.
RAIL_COUNTS: tuple[int, ...] = (2, 3)
RAIL_COUNT_WEIGHTS = (0.55, 0.45)
# breaker_per_group weighted toward small N (a compact 8-12 way board is common).
PER_GROUP_CHOICES: tuple[int, ...] = (4, 6, 8, 9, 10, 12, 14, 16)
PER_GROUP_WEIGHTS = (0.10, 0.16, 0.20, 0.14, 0.14, 0.12, 0.08, 0.06)

MAX_TOTAL_BREAKERS = 42
MAX_TOGGLES = 3

# ---------------------------------------------------------------------------
# Palettes (per-seed). Keys sampled from the 5-star sources' materials.
#   sheet     powder-coated / painted sheet metal (dominant body + door)
#   deadfront dark recessed deadfront / channel
#   white_mcb molded white MCB plastic
#   black     molded black plastic (toggles, wells, channels)
#   copper    exposed copper busbar
#   brass     brass terminal bar
#   galv      galvanized hardware (hinge barrels, glands, knuckles, screws)
#   label     white printed label
#   accent    circuit / phase accent (blue-ish)
#   green     green device label
#   glass     smoked transparent door window
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "industrial_grey": {
        "sheet": (0.44, 0.47, 0.49, 1.0),
        "deadfront": (0.25, 0.28, 0.29, 1.0),
        "white_mcb": (0.92, 0.92, 0.88, 1.0),
        "black": (0.05, 0.05, 0.05, 1.0),
        "copper": (0.86, 0.40, 0.18, 1.0),
        "brass": (0.80, 0.60, 0.27, 1.0),
        "galv": (0.72, 0.74, 0.72, 1.0),
        "label": (0.94, 0.93, 0.89, 1.0),
        "accent": (0.05, 0.20, 0.72, 1.0),
        "green": (0.13, 0.66, 0.42, 1.0),
        "glass": (0.55, 0.66, 0.71, 0.36),
    },
    "light_grey_powder": {
        "sheet": (0.82, 0.81, 0.76, 1.0),
        "deadfront": (0.34, 0.36, 0.35, 1.0),
        "white_mcb": (0.95, 0.95, 0.92, 1.0),
        "black": (0.04, 0.04, 0.04, 1.0),
        "copper": (0.85, 0.39, 0.15, 1.0),
        "brass": (0.86, 0.65, 0.29, 1.0),
        "galv": (0.60, 0.62, 0.60, 1.0),
        "label": (0.96, 0.95, 0.92, 1.0),
        "accent": (0.03, 0.22, 0.80, 1.0),
        "green": (0.14, 0.70, 0.46, 1.0),
        "glass": (0.68, 0.83, 0.90, 0.34),
    },
    "municipal_beige": {
        "sheet": (0.80, 0.75, 0.63, 1.0),
        "deadfront": (0.33, 0.30, 0.25, 1.0),
        "white_mcb": (0.93, 0.91, 0.85, 1.0),
        "black": (0.06, 0.05, 0.04, 1.0),
        "copper": (0.84, 0.42, 0.17, 1.0),
        "brass": (0.82, 0.62, 0.26, 1.0),
        "galv": (0.66, 0.64, 0.58, 1.0),
        "label": (0.95, 0.93, 0.86, 1.0),
        "accent": (0.10, 0.28, 0.62, 1.0),
        "green": (0.20, 0.60, 0.36, 1.0),
        "glass": (0.66, 0.72, 0.66, 0.34),
    },
    "graphite_dark": {
        "sheet": (0.24, 0.26, 0.28, 1.0),
        "deadfront": (0.13, 0.14, 0.15, 1.0),
        "white_mcb": (0.90, 0.90, 0.87, 1.0),
        "black": (0.03, 0.03, 0.03, 1.0),
        "copper": (0.88, 0.42, 0.18, 1.0),
        "brass": (0.84, 0.63, 0.28, 1.0),
        "galv": (0.62, 0.64, 0.66, 1.0),
        "label": (0.90, 0.90, 0.88, 1.0),
        "accent": (0.10, 0.34, 0.86, 1.0),
        "green": (0.16, 0.72, 0.48, 1.0),
        "glass": (0.40, 0.50, 0.56, 0.36),
    },
    "safety_blue": {
        "sheet": (0.22, 0.34, 0.52, 1.0),
        "deadfront": (0.14, 0.20, 0.30, 1.0),
        "white_mcb": (0.93, 0.93, 0.90, 1.0),
        "black": (0.04, 0.05, 0.06, 1.0),
        "copper": (0.86, 0.40, 0.16, 1.0),
        "brass": (0.85, 0.64, 0.28, 1.0),
        "galv": (0.66, 0.70, 0.74, 1.0),
        "label": (0.94, 0.94, 0.92, 1.0),
        "accent": (0.90, 0.62, 0.06, 1.0),
        "green": (0.15, 0.68, 0.44, 1.0),
        "glass": (0.58, 0.70, 0.80, 0.34),
    },
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _wchoice(rng: random.Random, items, weights):
    return rng.choices(items, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# Public + resolved config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DistributionBoardPanelConfig:
    form_module: FormModule = "single_door"
    topology_module: TopologyModule = "stacked_din_rails"
    mains_module: MainsModule = "bus_bars_only"
    rail_count: int = 3
    breaker_per_group: int = 12
    palette_style: PaletteStyle = "industrial_grey"
    width_scale: float = 1.0
    height_scale: float = 1.0
    depth_scale: float = 1.0
    name: str = "reference_distribution_board_panel"


@dataclass(frozen=True)
class ResolvedDistributionBoardPanelConfig:
    form_module: FormModule
    topology_module: TopologyModule
    mains_module: MainsModule
    rail_count: int          # groups for stacked (2/3); 1 single; 2 columns
    breaker_per_group: int   # MCBs per rail / breakers per column
    n_toggles: int
    has_left_bay: bool
    palette_style: PaletteStyle
    width_scale: float
    height_scale: float
    depth_scale: float
    name: str

    @property
    def total_breakers(self) -> int:
        groups = 2 if self.topology_module == "two_vertical_columns" else (
            1 if self.topology_module == "single_din_rail" else self.rail_count
        )
        return groups * self.breaker_per_group


# ---------------------------------------------------------------------------
# Procedural sampler
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> DistributionBoardPanelConfig:
    rng = random.Random(seed)
    form = _wchoice(rng, FORM_MODULES, FORM_WEIGHTS)
    topo = _wchoice(rng, TOPOLOGY_MODULES, TOPOLOGY_WEIGHTS)
    mains = _wchoice(rng, MAINS_MODULES, MAINS_WEIGHTS)
    rail_count = _wchoice(rng, RAIL_COUNTS, RAIL_COUNT_WEIGHTS)
    per_group = _wchoice(rng, PER_GROUP_CHOICES, PER_GROUP_WEIGHTS)
    return DistributionBoardPanelConfig(
        form_module=form,
        topology_module=topo,
        mains_module=mains,
        rail_count=int(rail_count),
        breaker_per_group=int(per_group),
        palette_style=rng.choice(PALETTE_STYLES),
        width_scale=round(rng.uniform(0.92, 1.08), 3),
        height_scale=round(rng.uniform(0.92, 1.10), 3),
        depth_scale=round(rng.uniform(0.92, 1.10), 3),
        name=f"seeded_distribution_board_panel_{seed}",
    )


def resolve_config(
    config: DistributionBoardPanelConfig,
) -> ResolvedDistributionBoardPanelConfig:
    if config.form_module not in FORM_MODULES:
        raise ValueError(f"Unsupported form_module: {config.form_module}")
    if config.topology_module not in TOPOLOGY_MODULES:
        raise ValueError(f"Unsupported topology_module: {config.topology_module}")
    if config.mains_module not in MAINS_MODULES:
        raise ValueError(f"Unsupported mains_module: {config.mains_module}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    topo = config.topology_module
    # Gate: a two-door board with a single DIN rail is unrealistically sparse.
    if config.form_module == "two_door" and topo == "single_din_rail":
        topo = "stacked_din_rails"

    rail_count = config.rail_count if config.rail_count in RAIL_COUNTS else 3

    # Clamp per-group count to the topology's realistic band.
    if topo == "two_vertical_columns":
        per_group = int(_clamp(config.breaker_per_group, 4, 12))
        groups = 2
    elif topo == "single_din_rail":
        per_group = int(_clamp(config.breaker_per_group, 6, 16))
        rail_count = 1
        groups = 1
    else:  # stacked_din_rails
        per_group = int(_clamp(config.breaker_per_group, 6, 16))
        groups = rail_count

    # Keep the total tractable (compile budget) — shrink per_group if needed.
    while groups * per_group > MAX_TOTAL_BREAKERS and per_group > 4:
        per_group -= 1

    has_left_bay = config.mains_module == "full_main_bay"
    # Real toggles live in one articulated group; cap for the motion budget.
    n_toggles = max(1, min(MAX_TOGGLES, per_group))

    return ResolvedDistributionBoardPanelConfig(
        form_module=config.form_module,
        topology_module=topo,
        mains_module=config.mains_module,
        rail_count=rail_count,
        breaker_per_group=per_group,
        n_toggles=n_toggles,
        has_left_bay=has_left_bay,
        palette_style=config.palette_style,
        width_scale=_clamp(config.width_scale, 0.92, 1.08),
        height_scale=_clamp(config.height_scale, 0.92, 1.10),
        depth_scale=_clamp(config.depth_scale, 0.92, 1.10),
        name=config.name or "distribution_board_panel",
    )


# ---------------------------------------------------------------------------
# slot_choices
# ---------------------------------------------------------------------------
def _slot_choices_for_resolved(r: ResolvedDistributionBoardPanelConfig):
    if r.topology_module == "stacked_din_rails":
        topo_label = f"stacked_din_rails_{r.rail_count}"
    else:
        topo_label = r.topology_module
    return [
        ("form_module", r.form_module),
        ("topology_module", topo_label),
        ("mains_module", r.mains_module),
        ("breaker_per_group", str(r.breaker_per_group)),
    ]


def slot_choices_for_seed(seed: int):
    return _slot_choices_for_resolved(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Canonical frame / layout (single-sourced geometry — Contract 3c)
# ---------------------------------------------------------------------------
WALL = 0.014
PAN_FRONT = -0.068       # front face of the interior mounting pan (device backs reach here)
DIN_PITCH_X = 0.034      # MCB module pitch along X (horizontal rail)
COL_PITCH_Z = 0.042      # breaker pitch along Z (vertical column)
RAIL_PITCH_Z = 0.155     # vertical spacing between stacked DIN rails
COL_DX = 0.090           # half-spacing between the two vertical columns
FACE_THK = 0.016         # door leaf thickness
DOOR_MARGIN = 0.045
LEFT_BAY_W = 0.30        # width of the full_main_bay left power bay


@dataclass(frozen=True)
class _Layout:
    board_w: float
    board_h: float
    board_d: float       # interior depth (front opening at y=-board_d)
    front_y: float       # = -board_d
    field_w: float
    field_h: float
    field_cx: float
    field_cz: float
    has_left_bay: bool
    left_bay_cx: float
    divider_x: float     # mullion / bay divider x
    interior_left: float
    interior_right: float
    top_zone_z: float    # z of the top busbar row
    bot_zone_z: float    # z of the neutral bar row


def _field_footprint(r: ResolvedDistributionBoardPanelConfig) -> tuple[float, float]:
    n = r.breaker_per_group
    if r.topology_module == "two_vertical_columns":
        field_w = 2.0 * COL_DX + 0.090
        field_h = (n - 1) * COL_PITCH_Z + 0.080
    else:
        groups = 1 if r.topology_module == "single_din_rail" else r.rail_count
        rail_w = n * DIN_PITCH_X + 0.050
        field_w = rail_w + 0.040
        field_h = (groups - 1) * RAIL_PITCH_Z + 0.110
    return field_w, field_h


def _make_layout(r: ResolvedDistributionBoardPanelConfig) -> _Layout:
    field_w, field_h = _field_footprint(r)
    board_d = round(0.160 * r.depth_scale, 4)

    h_margin = 0.070 * r.width_scale
    left_bay_w = LEFT_BAY_W if r.has_left_bay else 0.0
    mullion_gap = 0.030 if r.has_left_bay else 0.0

    interior_w = left_bay_w + mullion_gap + field_w + 2.0 * h_margin
    board_w = round(interior_w + 2.0 * WALL, 4)
    interior_left = -board_w / 2.0 + WALL
    interior_right = board_w / 2.0 - WALL

    top_zone = 0.075 * r.height_scale
    bot_zone = 0.120 * r.height_scale
    board_h = round(2.0 * WALL + bot_zone + field_h + top_zone + 0.02, 4)

    if r.has_left_bay:
        divider_x = interior_left + left_bay_w + mullion_gap / 2.0
        left_bay_cx = interior_left + left_bay_w / 2.0
        field_cx = (divider_x + interior_right) / 2.0
    else:
        divider_x = 0.0  # only used by two_door split
        left_bay_cx = 0.0
        field_cx = 0.0

    field_cz = WALL + bot_zone + field_h / 2.0 + 0.01
    top_zone_z = field_cz + field_h / 2.0 + top_zone * 0.5
    bot_zone_z = WALL + bot_zone * 0.55

    return _Layout(
        board_w=board_w,
        board_h=board_h,
        board_d=board_d,
        front_y=-board_d,
        field_w=field_w,
        field_h=field_h,
        field_cx=field_cx,
        field_cz=field_cz,
        has_left_bay=r.has_left_bay,
        left_bay_cx=left_bay_cx,
        divider_x=divider_x,
        interior_left=interior_left,
        interior_right=interior_right,
        top_zone_z=top_zone_z,
        bot_zone_z=bot_zone_z,
    )


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.steel_galvanized",
    )


# ===========================================================================
# ENCLOSURE shell / open backplate (Slot A form, static visuals on the root).
# ===========================================================================
def _build_enclosure_shell(enclosure, lay: _Layout, mats) -> None:
    """Hollow steel cabinet: back sheet, four walls, deadfront frame lips."""
    sheet = mats["sheet"]
    galv = mats["galv"]
    BW, BH, BD = lay.board_w, lay.board_h, lay.board_d
    fy = lay.front_y

    # Back sheet (behind interior, +Y) and side / top / bottom walls.
    _box(enclosure, (BW, WALL, BH), (0.0, WALL / 2.0, BH / 2.0), sheet, "back_sheet")
    for tag, s in (("0", -1.0), ("1", 1.0)):
        _box(enclosure, (WALL, BD, BH), (s * (BW / 2.0 - WALL / 2.0), fy / 2.0, BH / 2.0),
             sheet, f"side_wall_{tag}")
    _box(enclosure, (BW, BD, WALL), (0.0, fy / 2.0, BH - WALL / 2.0), sheet, "top_wall")
    _box(enclosure, (BW, BD, WALL), (0.0, fy / 2.0, WALL / 2.0), sheet, "bottom_wall")

    # Raised deadfront frame lips around the front opening.
    lip_y = fy + 0.008
    _box(enclosure, (BW, 0.016, 0.032), (0.0, lip_y, BH - 0.016), sheet, "front_top_lip")
    _box(enclosure, (BW, 0.016, 0.032), (0.0, lip_y, 0.016), sheet, "front_bottom_lip")
    _box(enclosure, (0.034, 0.016, BH), (lay.interior_left + 0.003, lip_y, BH / 2.0),
         sheet, "front_left_lip")
    _box(enclosure, (0.034, 0.016, BH), (lay.interior_right - 0.003, lip_y, BH / 2.0),
         sheet, "front_right_lip")

    _add_shell_hardware(enclosure, lay, mats, galv)


def _build_backplate(enclosure, lay: _Layout, mats) -> None:
    """Open backplate chassis: flat mounting plate + short bent flanges, no door."""
    sheet = mats["sheet"]
    galv = mats["galv"]
    brass = mats["brass"]
    green = mats["green"]
    BW, BH = lay.board_w, lay.board_h
    flange_d = 0.026

    _box(enclosure, (BW, WALL, BH), (0.0, WALL / 2.0, BH / 2.0), sheet, "back_sheet")
    _box(enclosure, (BW, flange_d, 0.018), (0.0, -flange_d / 2.0 + WALL, BH - 0.009),
         sheet, "top_flange")
    _box(enclosure, (BW, flange_d, 0.018), (0.0, -flange_d / 2.0 + WALL, 0.009),
         sheet, "bottom_flange")
    _box(enclosure, (0.018, flange_d, BH), (-BW / 2.0 + 0.009, -flange_d / 2.0 + WALL, BH / 2.0),
         sheet, "left_flange")
    _box(enclosure, (0.018, flange_d, BH), (BW / 2.0 - 0.009, -flange_d / 2.0 + WALL, BH / 2.0),
         sheet, "right_flange")
    # Prominent earth bonding stud on the plate.
    _cyl(enclosure, 0.008, 0.016, (-BW / 2.0 + 0.05, -0.008, 0.06), brass,
         "earth_bonding_stud", rpy=(math.pi / 2.0, 0.0, 0.0))
    _box(enclosure, (0.040, 0.002, 0.018), (-BW / 2.0 + 0.05, -0.018, 0.06), green,
         "earth_label")
    _add_shell_hardware(enclosure, lay, mats, galv, backplate=True)


def _add_shell_hardware(enclosure, lay: _Layout, mats, galv, *, backplate: bool = False) -> None:
    """Top conduit knockouts + glands, corner wall-mounting holes (loop-emitted)."""
    screw = mats["black"]
    rubber = mats["black"]
    BW, BH = lay.board_w, lay.board_h
    y_top = WALL if backplate else lay.front_y / 2.0
    # Top conduit stubs + glands (3, evenly spaced across the usable width).
    span = BW * 0.62
    for i in range(3):
        x = -span / 2.0 + i * span / 2.0
        _cyl(enclosure, 0.017, 0.10, (x, y_top, BH + 0.050), galv, f"conduit_stub_{i}",
             rpy=(0.0, 0.0, 0.0))
        _cyl(enclosure, 0.023, 0.016, (x, y_top, BH), rubber, f"top_gland_{i}")
    # Corner mounting holes on the back sheet.
    for i, (sx, sz) in enumerate(((-1, 1), (1, 1), (-1, 0), (1, 0))):
        x = sx * (BW / 2.0 - 0.035)
        z = BH - 0.045 if sz else 0.045
        _box(enclosure, (0.016, 0.006, 0.016), (x, -0.003, z), screw, f"mounting_hole_{i}")


# ===========================================================================
# BREAKER FIELD (Slot B topology + Slot C multiplicity), loop-emitted.
# Returns the world (x, z) of every real-toggle slot in the articulated group.
# ===========================================================================
def _add_breaker_run(enclosure, mats, group_name, *, count, orientation, x0, z0,
                     articulated_slots) -> list[tuple[float, float, float, str]]:
    """One rail-run (orientation='x', MCBs along X) or column (orientation='z',
    breakers stacked along Z). Bodies span the whole run; per-module detail is
    a seam + a screw head + a decorative toggle. Where a real toggle goes we
    emit a proud pivot boss instead (the toggle part's barrel laps only it).
    Returns (x, y_pivot, z, boss_name) per real-toggle slot. All small hardware
    is Box (cheap tessellation)."""
    white = mats["white_mcb"]
    dark = mats["black"]
    galv = mats["galv"]
    green = mats["green"]
    accent = mats["accent"]
    shadow = mats["deadfront"]
    screw = mats["galv"]
    toggle_world: list[tuple[float, float, float, str]] = []

    if orientation == "x":
        run_w = count * DIN_PITCH_X + 0.050
        cx = x0 + run_w / 2.0
        _box(enclosure, (run_w + 0.060, 0.012, 0.018), (cx, -0.006, z0), galv,
             f"{group_name}_din_rail")
        _box(enclosure, (run_w, 0.046, 0.044), (cx, -0.040, z0 + 0.028), white,
             f"{group_name}_upper_body")
        _box(enclosure, (run_w, 0.046, 0.044), (cx, -0.040, z0 - 0.028), white,
             f"{group_name}_lower_body")
        _box(enclosure, (run_w, 0.010, 0.012), (cx, -0.062, z0), white,
             f"{group_name}_center_step")
        _box(enclosure, (run_w * 0.86, 0.003, 0.008), (cx, -0.066, z0 + 0.004), green,
             f"{group_name}_label_strip")
        _box(enclosure, (0.018, 0.048, 0.066), (x0 + run_w + 0.020, -0.036, z0), accent,
             f"{group_name}_end_terminal")
        for i in range(count):
            x = x0 + 0.040 + i * DIN_PITCH_X
            _box(enclosure, (0.0022, 0.004, 0.082), (x - 0.017, -0.065, z0), shadow,
                 f"{group_name}_seam_{i}")
            _box(enclosure, (0.006, 0.006, 0.006), (x, -0.067, z0 + 0.042), screw,
                 f"{group_name}_screw_{i}")
            if i in articulated_slots:
                boss = f"{group_name}_toggle_boss_{i}"
                _box(enclosure, (0.016, 0.014, 0.024), (x, -0.074, z0), dark, boss)
                toggle_world.append((x, -0.074, z0, boss))
            else:
                _box(enclosure, (0.014, 0.012, 0.028), (x, -0.070, z0 - 0.005), dark,
                     f"{group_name}_toggle_{i}")
    else:  # vertical column
        run_h = (count - 1) * COL_PITCH_Z + 0.070
        z_bot = z0 - (count - 1) * COL_PITCH_Z / 2.0
        _box(enclosure, (0.078, 0.018, run_h), (x0, -0.076, z0), dark,
             f"{group_name}_well")
        _box(enclosure, (0.006, 0.022, run_h + 0.02), (x0 - 0.043, -0.078, z0), dark,
             f"{group_name}_side_rail_0")
        _box(enclosure, (0.006, 0.022, run_h + 0.02), (x0 + 0.043, -0.078, z0), dark,
             f"{group_name}_side_rail_1")
        for i in range(count):
            z = z_bot + i * COL_PITCH_Z
            _box(enclosure, (0.071, 0.015, 0.030), (x0, -0.090, z), white,
                 f"{group_name}_body_{i}")
            _box(enclosure, (0.010, 0.004, 0.004), (x0 + 0.030, -0.098, z + 0.008), green,
                 f"{group_name}_tick_{i}")
            if i in articulated_slots:
                # Proud pivot boss: sits in front of the deep column body so the
                # toggle barrel laps only the boss (never the body behind it).
                boss = f"{group_name}_toggle_boss_{i}"
                _box(enclosure, (0.026, 0.022, 0.020), (x0, -0.099, z), dark, boss)
                toggle_world.append((x0, -0.104, z, boss))
            else:
                _box(enclosure, (0.024, 0.010, 0.020), (x0, -0.099, z), dark,
                     f"{group_name}_toggle_{i}")
    return toggle_world


def _build_field(enclosure, lay: _Layout, r, mats) -> list[tuple[float, float]]:
    """Build all breaker groups; return the real-toggle world positions."""
    n = r.breaker_per_group
    n_tog = r.n_toggles
    # Real toggles occupy the middle indices of the articulated group.
    start = max(0, (n - n_tog) // 2)
    art = set(range(start, start + n_tog))

    all_toggles: list[tuple[float, float]] = []
    if r.topology_module == "two_vertical_columns":
        for c in range(2):
            cx = lay.field_cx + (c - 0.5) * 2.0 * COL_DX
            slots = art if c == 0 else set()
            tog = _add_breaker_run(enclosure, mats, f"col_{c}", count=n, orientation="z",
                                   x0=cx, z0=lay.field_cz, articulated_slots=slots)
            all_toggles.extend(tog)
    else:
        groups = 1 if r.topology_module == "single_din_rail" else r.rail_count
        run_w = n * DIN_PITCH_X + 0.050
        x0 = lay.field_cx - run_w / 2.0
        art_group = groups // 2
        for g in range(groups):
            z = lay.field_cz + (groups - 1) * RAIL_PITCH_Z / 2.0 - g * RAIL_PITCH_Z
            slots = art if g == art_group else set()
            tog = _add_breaker_run(enclosure, mats, f"rail_{g}", count=n, orientation="x",
                                   x0=x0, z0=z, articulated_slots=slots)
            all_toggles.extend(tog)
    return all_toggles


# ===========================================================================
# MAINS assembly (Slot D), static visuals on the enclosure.
# ===========================================================================
def _build_mains(enclosure, lay: _Layout, r, mats) -> None:
    if r.mains_module == "full_main_bay":
        _build_full_main_bay(enclosure, lay, mats)
    elif r.mains_module == "bus_bars_only":
        _build_bus_bars_only(enclosure, lay, mats)
    else:
        _build_mcb_only(enclosure, lay, mats)


def _build_full_main_bay(enclosure, lay: _Layout, mats) -> None:
    """Left power bay: two main MCCB cases, four phase busbars, aux + meter."""
    gray = mats["deadfront"]
    dark = mats["black"]
    white = mats["white_mcb"]
    copper = mats["copper"]
    brass = mats["brass"]
    accent = mats["accent"]
    green = mats["green"]
    screw = mats["galv"]
    cx = lay.left_bay_cx
    bay_h = lay.board_h - 2 * WALL - 0.04
    cz = lay.board_h / 2.0

    for idx, dz in enumerate((0.20, -0.14)):
        z = cz + dz * bay_h
        _box(enclosure, (0.150, 0.058, 0.130), (cx - 0.03, -0.044, z), gray,
             f"main_breaker_{idx}_case")
        _box(enclosure, (0.030, 0.016, 0.070), (cx - 0.03, -0.080, z - 0.005), dark,
             f"main_breaker_{idx}_handle")
        _box(enclosure, (0.055, 0.003, 0.040), (cx - 0.05, -0.072, z + 0.020), green,
             f"main_breaker_{idx}_label")
        for sx in (-0.045, 0.045):
            _box(enclosure, (0.007, 0.010, 0.007), (cx - 0.03 + sx, -0.070, z + 0.072),
                 screw, f"main_breaker_{idx}_screw_{'p' if sx > 0 else 'n'}")

    # Phase busbars reach back to the mounting pan; a colored sleeve caps the front.
    bar_xs = [cx + 0.055 + i * 0.024 for i in range(4)]
    sleeve = [mats["accent"], mats["white_mcb"], mats["green"], mats["copper"]]
    for i, x in enumerate(bar_xs):
        _box(enclosure, (0.016, 0.036, 0.200), (x, -0.050, cz + 0.02),
             copper if i != 3 else brass, f"phase_busbar_{i}")
        _box(enclosure, (0.022, 0.008, 0.165), (x, -0.070, cz + 0.02), sleeve[i],
             f"phase_sleeve_{i}")

    _box(enclosure, (0.100, 0.052, 0.070), (cx, -0.044, cz - 0.30 * bay_h), accent,
         "meter_body")
    for i in range(3):
        _box(enclosure, (0.010, 0.006, 0.050), (cx - 0.030 + i * 0.024, -0.068,
             cz - 0.30 * bay_h), white, f"meter_fin_{i}")


def _build_bus_bars_only(enclosure, lay: _Layout, mats) -> None:
    """Horizontal copper bus at top + neutral/earth brass bars at bottom."""
    copper = mats["copper"]
    brass = mats["brass"]
    dark = mats["deadfront"]
    screw = mats["galv"]
    gray = mats["deadfront"]
    accent = mats["accent"]
    fx = lay.field_cx
    fw = min(lay.field_w, lay.board_w - 2 * WALL - 0.06)

    # Small incoming main breaker centered above the field.
    _box(enclosure, (0.090, 0.050, 0.052), (fx, -0.046, lay.top_zone_z), gray,
         "main_breaker_case")
    _box(enclosure, (0.024, 0.016, 0.036), (fx, -0.076, lay.top_zone_z), dark,
         "main_breaker_handle")
    # Copper bus below the main.
    _box(enclosure, (fw * 0.9, 0.008, 0.016), (fx, -0.070, lay.top_zone_z - 0.055),
         copper, "copper_bus_bar")
    # Neutral + earth brass bars at the bottom, with standoffs + screw heads.
    _build_terminal_bars(enclosure, lay, mats, fx, fw, brass, dark, screw, accent)


def _build_mcb_only(enclosure, lay: _Layout, mats) -> None:
    """MCB-only sub-board: no main / copper bus; neutral+earth + a sub-feed block."""
    brass = mats["brass"]
    dark = mats["deadfront"]
    screw = mats["galv"]
    accent = mats["accent"]
    black = mats["black"]
    fx = lay.field_cx
    fw = min(lay.field_w, lay.board_w - 2 * WALL - 0.06)
    # Incoming sub-feed terminal block where the upstream supply lands.
    _box(enclosure, (0.110, 0.018, 0.028), (fx, -0.070, lay.top_zone_z), black,
         "sub_feed_terminal_block")
    for i in range(3):
        _box(enclosure, (0.007, 0.008, 0.007), (fx - 0.036 + i * 0.036, -0.080,
             lay.top_zone_z), screw, f"sub_feed_screw_{i}")
    _build_terminal_bars(enclosure, lay, mats, fx, fw, brass, dark, screw, accent)


def _build_terminal_bars(enclosure, lay: _Layout, mats, fx, fw, brass, dark, screw, accent) -> None:
    """Shared neutral + earth brass bars at the bottom zone."""
    for j, (nm, dz, mat) in enumerate((("neutral", 0.028, brass), ("earth", 0.0, accent))):
        z = lay.bot_zone_z + dz
        _box(enclosure, (fw * 0.9, 0.008, 0.014), (fx, -0.078, z), mat, f"{nm}_bar")
        ncl = max(4, min(10, int(fw / 0.05)))
        for i in range(ncl):
            x = fx - fw * 0.42 + i * (fw * 0.84) / max(1, ncl - 1)
            _box(enclosure, (0.014, 0.010, 0.018), (x, -0.070, z), dark,
                 f"{nm}_standoff_{i}")
            _box(enclosure, (0.006, 0.006, 0.006), (x, -0.084, z), screw,
                 f"{nm}_screw_{i}")


# ===========================================================================
# DOORS (Slot A), REVOLUTE parts authored CLOSED. LOCAL ORIGIN = hinge edge.
# ===========================================================================
def _front_jamb(enclosure, lay: _Layout, mats, *, hinge_x, door_h, door_zc, tag) -> str:
    """Real front-jamb stile the door hinge barrel mates to (no phantom pad).
    The door hinge_barrel (r=0.010 about the joint origin at y=front_y) presents
    its +y face at front_y+0.010; place the jamb so its -y face sits there."""
    name = f"front_jamb_{tag}"
    jamb_d = WALL + 0.006
    jamb_cy = lay.front_y + 0.010 + jamb_d / 2.0
    _box(enclosure, (0.026, jamb_d, door_h + 0.02), (hinge_x, jamb_cy, door_zc),
         mats["sheet"], name)
    return name


def _build_door_leaf(model, name, lay: _Layout, mats, *, door_w, door_h, door_zc,
                     hinge_x, hinge_sign, with_window) -> tuple[object, list]:
    """Hinged door leaf, closed rest pose. hinge_sign=+1 -> hinge on -X edge,
    panel extends +X; -1 -> hinge on +X edge, panel extends -X. Opens toward -Y."""
    door = model.part(name)
    panel_x = hinge_sign * door_w / 2.0
    sheet = mats["sheet"]
    galv = mats["galv"]

    # Hinge knuckle barrel straddling local origin (child AABB contains (0,0,0)).
    door.visual(Cylinder(radius=0.010, length=door_h - 0.03),
                origin=Origin(xyz=(0.0, 0.0, 0.0)), material=galv, name="hinge_barrel", material_class_id="metal.steel_galvanized")
    # Leaf panel: back face at local y=0 (front-jamb plane), proud toward -Y.
    door.visual(Box((door_w, FACE_THK, door_h)),
                origin=Origin(xyz=(panel_x, -FACE_THK / 2.0, 0.0)), material=sheet,
                name="leaf", material_class_id="metal.paint_coated")
    if with_window:
        door.visual(Box((door_w - 0.10, 0.004, door_h - 0.14)),
                    origin=Origin(xyz=(panel_x, -FACE_THK - 0.002, 0.0)),
                    material=mats["glass"], name="window_glass", material_class_id="glass.smoked_tinted")
        for edge, ez in (("top", (door_h - 0.14) / 2.0 + 0.03), ("bot", -(door_h - 0.14) / 2.0 - 0.03)):
            door.visual(Box((door_w - 0.06, 0.012, 0.024)),
                        origin=Origin(xyz=(panel_x, -FACE_THK - 0.004, ez)),
                        material=sheet, name=f"window_rail_{edge}", material_class_id="metal.paint_coated")
    # Latch handle near the free edge + round lock core.
    free_x = hinge_sign * (door_w - 0.04)
    door.visual(Box((0.014, 0.020, max(0.10, door_h * 0.24))),
                origin=Origin(xyz=(free_x, -FACE_THK - 0.008, 0.0)), material=galv,
                name="latch_handle", material_class_id="metal.steel_galvanized")
    door.visual(Cylinder(radius=0.011, length=0.010),
                origin=Origin(xyz=(free_x, -FACE_THK - 0.010, door_h * 0.06),
                              rpy=(math.pi / 2.0, 0.0, 0.0)), material=galv,
                name="round_lock", material_class_id="metal.steel_galvanized")
    # Nameplate label (host-derived: embedded into the leaf face so it stays supported).
    door.visual(Box((0.11, 0.005, 0.045)),
                origin=Origin(xyz=(panel_x, -FACE_THK - 0.0005, -door_h * 0.28)),
                material=mats["label"], name="door_nameplate", appearance_only=AppearanceOnlySpec(kind="decal"))
    door.inertial = Inertial.from_geometry(Box((door_w, FACE_THK, door_h)), mass=4.0)

    origin = (hinge_x, lay.front_y, door_zc)
    axis_z = -hinge_sign
    limits = MotionLimits(effort=30.0, velocity=1.6, lower=0.0, upper=math.radians(100.0))
    mating = MatingContract(
        parent_face_geometry=f"front_jamb_{name}", parent_face_side="negative_y",
        child_face_geometry="hinge_barrel", child_face_side="positive_y",
        contact_tol=0.006,
    )
    joint_name = f"{name}_hinge"
    model.articulation(joint_name, ArticulationType.REVOLUTE, parent=model.get_part("enclosure"),
                       child=door, origin=Origin(xyz=origin), axis=(0.0, 0.0, axis_z),
                       motion_limits=limits, mating=mating)
    overlaps = [
        (name, "enclosure", "hinge_barrel", f"front_jamb_{name}",
         "Door hinge knuckle laps the front jamb stile it pivots on."),
    ]
    return door, overlaps


def _build_doors(model, enclosure, lay: _Layout, r, mats) -> tuple[list[str], list]:
    """Emit door part(s) for the form; return (door_joint_names, overlap_specs)."""
    if r.form_module == "open_backplate":
        return [], []
    door_h = lay.board_h - 2 * DOOR_MARGIN
    door_zc = lay.board_h / 2.0
    joints: list[str] = []
    overlaps: list = []

    if r.form_module == "single_door":
        hinge_x = lay.interior_left + 0.016
        door_w = (lay.interior_right - lay.interior_left) - 0.02
        _front_jamb(enclosure, lay, mats, hinge_x=hinge_x, door_h=door_h,
                    door_zc=door_zc, tag="front_door")
        _, ov = _build_door_leaf(model, "front_door", lay, mats, door_w=door_w,
                                 door_h=door_h, door_zc=door_zc, hinge_x=hinge_x,
                                 hinge_sign=1.0, with_window=False)
        joints.append("front_door_hinge")
        overlaps.extend(ov)
        overlaps.append(("front_door", "enclosure", "hinge_barrel", "side_wall_0",
                         "Door hinge knuckle laps the body side wall at the jamb."))
        overlaps.append(("front_door", "enclosure", "hinge_barrel", "front_left_lip",
                         "Door hinge knuckle laps the front deadfront lip at the jamb."))
    else:  # two_door
        divider_x = lay.divider_x if lay.has_left_bay else 0.0
        # Center mullion (full interior height so it never floats).
        _box(enclosure, (0.022, WALL + 0.006, lay.board_h - 0.008),
             (divider_x, lay.front_y + WALL / 2.0, lay.board_h / 2.0), mats["sheet"],
             "center_mullion")
        specs = [
            ("left_door", lay.interior_left + 0.016, 1.0,
             (divider_x - lay.interior_left) - 0.024),
            ("right_door", lay.interior_right - 0.016, -1.0,
             (lay.interior_right - divider_x) - 0.024),
        ]
        for nm, hinge_x, hsign, dw in specs:
            with_window = True
            _front_jamb(enclosure, lay, mats, hinge_x=hinge_x, door_h=door_h,
                        door_zc=door_zc, tag=nm)
            _, ov = _build_door_leaf(model, nm, lay, mats, door_w=dw, door_h=door_h,
                                     door_zc=door_zc, hinge_x=hinge_x, hinge_sign=hsign,
                                     with_window=with_window)
            joints.append(f"{nm}_hinge")
            overlaps.extend(ov)
            side = "side_wall_0" if hsign > 0 else "side_wall_1"
            lip = "front_left_lip" if hsign > 0 else "front_right_lip"
            overlaps.append((nm, "enclosure", "hinge_barrel", side,
                             "Door hinge knuckle laps the body side wall at the jamb."))
            overlaps.append((nm, "enclosure", "hinge_barrel", lip,
                             "Door hinge knuckle laps the front deadfront lip at the jamb."))
            overlaps.append((nm, "enclosure", "leaf", "center_mullion",
                             "Closed leaf laps the center mullion seam."))
    return joints, overlaps


# ===========================================================================
# BREAKER TOGGLES (real REVOLUTE controls, parent = enclosure).
# ===========================================================================
def _build_toggles(model, enclosure, lay: _Layout, mats,
                   toggle_world) -> tuple[list[str], list]:
    joints: list[str] = []
    overlaps: list = []
    dark = mats["black"]
    galv = mats["galv"]
    for idx, (x, y_pivot, z, boss) in enumerate(toggle_world):
        tog = model.part(f"breaker_toggle_{idx}")
        # Local frame: pivot axis along X at local origin; barrel straddles it
        # (child AABB contains (0,0,0)); the paddle hangs proud toward -Y / -Z.
        tog.visual(Cylinder(radius=0.005, length=0.030),
                   origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                   material=galv, name="pivot_barrel", material_class_id="metal.steel_galvanized")
        tog.visual(Box((0.012, 0.012, 0.030)),
                   origin=Origin(xyz=(0.0, -0.008, -0.012)), material=dark,
                   name="toggle_paddle", material_class_id="plastic.opaque_glossy_molded")
        tog.inertial = Inertial.from_geometry(Box((0.02, 0.02, 0.03)), mass=0.05)
        origin = (x, y_pivot, z)
        joint_name = f"toggle_pivot_{idx}"
        model.articulation(joint_name, ArticulationType.REVOLUTE, parent=enclosure,
                           child=tog, origin=Origin(xyz=origin), axis=(1.0, 0.0, 0.0),
                           motion_limits=MotionLimits(effort=1.0, velocity=4.0,
                                                      lower=-0.42, upper=0.42))
        joints.append(joint_name)
        reason = "Captured breaker rocker pivots on its module pivot boss."
        overlaps.append((f"breaker_toggle_{idx}", "enclosure", "pivot_barrel", boss, reason))
        overlaps.append((f"breaker_toggle_{idx}", "enclosure", "toggle_paddle", boss, reason))
    return joints, overlaps


# ===========================================================================
# Assembly
# ===========================================================================
def build_distribution_board_panel(
    config: DistributionBoardPanelConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or DistributionBoardPanelConfig()
    r = resolve_config(cfg)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-dbp-assets-")))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "domain": "Electrical_Wiring",
            "small_class": "Distribution board panel",
            "description": "Modular electrical distribution board / load-center: enclosure "
            "or open backplate + loop-emitted breaker field + mains assembly + hinged door(s).",
        },
    )

    palette = PALETTES[r.palette_style]
    mats = {key: model.material(f"dbp_{key}_{r.palette_style}", rgba=rgba)
            for key, rgba in palette.items()}

    lay = _make_layout(r)

    enclosure = model.part("enclosure", meta={"role": "root sheet-metal cabinet / backplate"})
    if r.form_module == "open_backplate":
        _build_backplate(enclosure, lay, mats)
    else:
        _build_enclosure_shell(enclosure, lay, mats)
    enclosure.inertial = Inertial.from_geometry(
        Box((lay.board_w, max(lay.board_d, 0.10), lay.board_h)),
        mass=28.0, origin=Origin(xyz=(0.0, lay.front_y / 2.0, lay.board_h / 2.0)),
    )

    # Interior mounting pan (deadfront chassis): the single supporting surface the
    # breaker field and mains devices all mount on — it bridges every device back
    # to the back sheet so nothing floats as a disconnected island. Its front face
    # (y=PAN_FRONT) sits just behind the breaker fronts (device back faces reach
    # past it) and clear of the proud toggle pivots.
    interior_w = lay.board_w - 2 * WALL
    interior_h = lay.board_h - 2 * WALL
    _box(enclosure, (interior_w, -PAN_FRONT, interior_h),
         (0.0, PAN_FRONT / 2.0, lay.board_h / 2.0), mats["deadfront"], "mounting_pan")

    # Static field + mains authored as visuals on the enclosure (Rule 1).
    toggle_world = _build_field(enclosure, lay, r, mats)
    _build_mains(enclosure, lay, r, mats)

    # Moving parts.
    door_joints, door_overlaps = _build_doors(model, enclosure, lay, r, mats)
    toggle_joints, toggle_overlaps = _build_toggles(model, enclosure, lay, mats, toggle_world)

    model.meta["slot_choices"] = _slot_choices_for_resolved(r)
    model.meta["_dbp_overlaps"] = door_overlaps + toggle_overlaps
    model.meta["_dbp_door_joints"] = door_joints
    model.meta["_dbp_toggle_joints"] = toggle_joints
    return model


def build_seeded_distribution_board_panel(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_distribution_board_panel(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_distribution_board_panel_tests(
    object_model: ArticulatedObject, config: DistributionBoardPanelConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}
    enclosure = object_model.get_part("enclosure")
    enc_vis = {v.name for v in enclosure.visuals}  # get_visual() raises on missing names

    ctx.check("small class is distribution board panel",
              object_model.meta.get("small_class") == "Distribution board panel",
              details=f"meta={object_model.meta.get('small_class')}")
    ctx.check("enclosure part present", "enclosure" in part_names)
    ctx.check("enclosure has back sheet", "back_sheet" in enc_vis)

    # Declare element-scoped overlaps recorded during build.
    for pa, pb, ea, eb, reason in object_model.meta.get("_dbp_overlaps", []):
        if pa not in part_names or pb not in part_names:
            continue
        ctx.allow_overlap(object_model.get_part(pa), object_model.get_part(pb),
                          elem_a=ea, elem_b=eb, reason=reason)

    # Grounding: lowest geometry sits on the floor.
    zmins = [ctx.part_world_aabb(p)[0][2] for p in object_model.parts
             if ctx.part_world_aabb(p) is not None]
    if zmins:
        ctx.check("board rests on the floor", abs(min(zmins)) <= 0.02,
                  details=f"zmin={min(zmins):.4f}")

    # --- Form-specific door topology ---
    door_joints = object_model.meta.get("_dbp_door_joints", [])
    if r.form_module == "open_backplate":
        ctx.check("open backplate has no door parts",
                  not any(n.endswith("_door") for n in part_names),
                  details=f"parts={sorted(part_names)}")
        ctx.check("open backplate has no door hinge",
                  not any("door_hinge" in n for n in joint_names))
        ctx.check("backplate has bent flanges",
                  "top_flange" in enc_vis and "left_flange" in enc_vis)
    else:
        expected = 1 if r.form_module == "single_door" else 2
        ctx.check("door joint count matches form", len(door_joints) == expected,
                  details=f"expected {expected}, got {len(door_joints)}")
        for jn in door_joints:
            j = object_model.get_articulation(jn)
            ctx.check(f"{jn} revolute vertical",
                      j.articulation_type == ArticulationType.REVOLUTE
                      and abs(j.axis[0]) < 1e-9 and abs(j.axis[1]) < 1e-9
                      and abs(abs(j.axis[2]) - 1.0) < 1e-9, details=str(j.axis))

    # --- Breaker field identity ---
    field_visuals = [v.name for v in enclosure.visuals]
    n_bodies = sum(1 for n in field_visuals if ("_upper_body" in n or "_body_" in n))
    ctx.check("breaker field emitted",
              any("din_rail" in n for n in field_visuals)
              or any("_well" in n for n in field_visuals),
              details=f"n_body_visuals={n_bodies}")

    # --- Real toggles (the moving joints for every form) ---
    toggle_joints = object_model.meta.get("_dbp_toggle_joints", [])
    ctx.check("has at least one real breaker toggle", len(toggle_joints) >= 1,
              details=f"toggles={toggle_joints}")
    ctx.check("has a non-fixed mechanism",
              any(object_model.get_articulation(n).articulation_type
                  == ArticulationType.REVOLUTE
                  for n in joint_names),
              details=f"joints={sorted(joint_names)}")
    tj0 = object_model.get_articulation(toggle_joints[0])
    ctx.check("toggle pivots about X",
              abs(abs(tj0.axis[0]) - 1.0) < 1e-9
              and tj0.motion_limits.lower < 0.0 < tj0.motion_limits.upper,
              details=str(tj0.axis))

    # --- Mains identity ---
    if r.mains_module == "bus_bars_only":
        ctx.check("has copper bus bar", "copper_bus_bar" in enc_vis)
    elif r.mains_module == "mcb_only_subboard":
        ctx.check("mcb-only has sub-feed block, no copper bus",
                  "sub_feed_terminal_block" in enc_vis and "copper_bus_bar" not in enc_vis)
    else:  # full_main_bay
        ctx.check("full main bay has main breaker + phase busbars",
                  "main_breaker_0_case" in enc_vis and "phase_busbar_0" in enc_vis)

    # --- Targeted motion: a door swings outward toward -Y ---
    if door_joints:
        dj = object_model.get_articulation(door_joints[0])
        door_part = object_model.get_part(door_joints[0].replace("_hinge", ""))
        closed = ctx.part_world_aabb(door_part)
        with ctx.pose({dj: 1.20}):
            opened = ctx.part_world_aabb(door_part)
        ctx.check("door opens outward toward the front (-Y)",
                  closed is not None and opened is not None
                  and opened[0][1] < closed[0][1] - 0.10,
                  details=f"closed={closed}, open={opened}")

    # --- Targeted motion: a breaker toggle rocks visibly ---
    tog_part = object_model.get_part("breaker_toggle_0")
    rest = ctx.part_world_aabb(tog_part)
    with ctx.pose({tj0: 0.40}):
        thrown = ctx.part_world_aabb(tog_part)
    ctx.check("breaker toggle rocks visibly",
              rest is not None and thrown is not None
              and (abs(thrown[0][1] - rest[0][1]) > 0.003
                   or abs(thrown[0][2] - rest[0][2]) > 0.003),
              details=f"rest={rest}, thrown={thrown}")

    # --- Dynamic non-穿模 across sampled joint poses (Rule 5) ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "DistributionBoardPanelConfig",
    "ResolvedDistributionBoardPanelConfig",
    "build_distribution_board_panel",
    "build_seeded_distribution_board_panel",
    "config_from_seed",
    "resolve_config",
    "run_distribution_board_panel_tests",
    "slot_choices_for_seed",
]
