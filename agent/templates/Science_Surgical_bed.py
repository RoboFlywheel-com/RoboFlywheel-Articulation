# SPDX-License-Identifier: Apache-2.0

"""Surgical / operating table modular template.

Identity (spec ``articraft_template_authoring/specs_modular_v1/Science_Surgical_bed.md``):
a flat, lying operating table = a multi-section padded mattress on a lifting
support base, with at least one REVOLUTE section hinge per seat. It is NOT a
sitting ``surgical_chair`` (continuous seat-pan + wrap back), NOT a plain
hospital bed (no articulating sections), NOT a bare stretcher / trolley.

Sourced from the ``surgical_bed`` 5-star sample pool (1 parent + 7 slot-fork
variants), all synced under ``data/records/``:
  * S1 pedestal parent  -> base ``pedestal_crossfoot`` + accessory ``arm_rails_horseshoe``
  * S2 ``rec_surgical_bed_var_fourleg``    -> base ``four_leg_splayed``
  * S3 ``rec_surgical_bed_var_casterbase`` -> base ``caster_trolley``
  * S4 ``rec_surgical_bed_var_twincolumn`` -> base ``twin_column_H``
  * S5 ``rec_surgical_bed_var_siderails``  -> accessory ``side_rails_IV``
  * S6 ``rec_surgical_bed_var_armboards``  -> accessory ``padded_arm_boards``
  * S7 ``rec_surgical_bed_var_sections2``  -> section_count N=2 (loop-rewrite paradigm)
  * S8 ``rec_surgical_bed_var_sections4``  -> section_count N=4

Structure (pattern = ``mixed``). A fixed ``seat`` mid-deck (the spine) sits at
table height z=0.98 on the chosen base. The whole tabletop tilts (trendelenburg,
axis Y, +-15 deg) about the base via the ``base_to_seat`` REVOLUTE joint -- the
defining OR-table DOF. Mattress sections hinge in +/-X: the +X back and the
first -X leg hinge *off the fixed seat*; any further -X foot section *chains*
off the leg (a leg->foot chain), so the fixed deck never extends under a movable
section. The two parallel slots both attach to that spine:

  * ``base`` (4): the ROOT support the seat tilts on.
      - ``pedestal_crossfoot``  : beige cross-foot block + tapered grey column.
      - ``four_leg_splayed``    : central hub + 4 splayed tubular legs + foot pads.
      - ``caster_trolley``      : low chassis + 4 fixed swivel casters + column.
      - ``twin_column_H``       : beige floor beam + 2 columns bridged by a cross member.
  * ``accessories`` (3): the FIXED bedside accessory visuals on the seat frame.
      Mounted clear of the sections' swept arcs (IV pole mid-side, head support
      cradled over the fixed spine) so a raised back / folded leg never rams them.
      - ``arm_rails_horseshoe`` : 2 curved tubular arm rails + a horseshoe head support.
      - ``side_rails_IV``       : 2 straight safety rails + a side IV pole.
      - ``padded_arm_boards``   : 2 flat padded arm boards on swing brackets.
  * ``section_count`` (N in [3,4]): the multiplicity axis. 1 fixed seat +
      (N-1) hinged sections: always a +X back AND >= 1 -X leg (N=2's lone back
      stub is rejected). Encoded into the slot_choice tuple as
      ``("section_count", f"n{N}")``.

>= 1 REVOLUTE section hinges off the fixed seat; the outer foot section chains
off the leg. Down-fold limits are tuned so a folded leg/foot clears every base
across the full trendelenburg tilt.

Source geometry is preserved as CadQuery meshes (``mesh_from_cadquery`` deck /
cushion / side-rails / lofted column / swept tubes); no boxy downgrade.

Compatibility: every base x accessory is mutually compatible, and the section
chain is compatible with any base / accessory. A(4) x B(3) = 12 pure slot
topologies (>= the diversity floor of 10), x N{3,4} encoded -> ~24 distinct.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

BaseSupport = Literal[
    "pedestal_crossfoot",
    "four_leg_splayed",
    "caster_trolley",
    "twin_column_H",
]
Accessory = Literal[
    "arm_rails_horseshoe",
    "side_rails_IV",
    "padded_arm_boards",
]
PaletteStyle = Literal[
    "stainless_blue",
    "dark_grey",
    "white_green",
    "chrome_grey",
    "teal",
]

BASE_SUPPORTS: tuple[BaseSupport, ...] = (
    "pedestal_crossfoot",
    "four_leg_splayed",
    "caster_trolley",
    "twin_column_H",
)
ACCESSORIES: tuple[Accessory, ...] = (
    "arm_rails_horseshoe",
    "side_rails_IV",
    "padded_arm_boards",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "stainless_blue",
    "dark_grey",
    "white_green",
    "chrome_grey",
    "teal",
)

N_SECTION_MIN = 3
N_SECTION_MAX = 4
# section_count sampling weights (parent N=3 high-frequency, N=4 common). N<3 is
# rejected: a single +X section over the seat is an incomplete stub (no leg run),
# so the multiplicity axis is {3, 4} -- always a back AND at least one leg.
SECTION_COUNT_WEIGHTS = (0.60, 0.40)  # for (3, 4)

# Trendelenburg tilt of the whole tabletop about the base (axis Y, +-15 deg).
# This is the defining OR-table DOF: the seat pivots head-down / foot-down on the
# support column. Realistic head-down/up tilt is ~+-15 deg.
TRENDELENBURG_TILT = math.radians(15.0)  # +-0.2618 rad


# ---------------------------------------------------------------------------
# Palette colorways (Accessories_Cushion.md idiom). Every .visual(material=...) draws from
# one of these keys; palette never enters the slot_choice tuple.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "stainless_blue": {
        "pad": (0.16, 0.28, 0.46, 1.0),
        "steel": (0.78, 0.80, 0.82, 1.0),
        "column": (0.55, 0.56, 0.58, 1.0),
        "foot": (0.74, 0.66, 0.52, 1.0),
        "tube": (0.80, 0.82, 0.84, 1.0),
        "wheel": (0.12, 0.12, 0.13, 1.0),
    },
    "dark_grey": {
        "pad": (0.16, 0.16, 0.18, 1.0),
        "steel": (0.70, 0.72, 0.74, 1.0),
        "column": (0.34, 0.35, 0.37, 1.0),
        "foot": (0.30, 0.31, 0.33, 1.0),
        "tube": (0.74, 0.76, 0.78, 1.0),
        "wheel": (0.08, 0.08, 0.09, 1.0),
    },
    "white_green": {
        "pad": (0.18, 0.42, 0.34, 1.0),
        "steel": (0.88, 0.89, 0.90, 1.0),
        "column": (0.82, 0.83, 0.84, 1.0),
        "foot": (0.86, 0.87, 0.88, 1.0),
        "tube": (0.84, 0.86, 0.88, 1.0),
        "wheel": (0.14, 0.15, 0.15, 1.0),
    },
    "chrome_grey": {
        "pad": (0.22, 0.22, 0.24, 1.0),
        "steel": (0.86, 0.87, 0.89, 1.0),
        "column": (0.62, 0.63, 0.65, 1.0),
        "foot": (0.58, 0.59, 0.61, 1.0),
        "tube": (0.90, 0.91, 0.92, 1.0),
        "wheel": (0.10, 0.10, 0.11, 1.0),
    },
    "teal": {
        "pad": (0.10, 0.40, 0.44, 1.0),
        "steel": (0.72, 0.76, 0.77, 1.0),
        "column": (0.20, 0.46, 0.50, 1.0),
        "foot": (0.16, 0.38, 0.42, 1.0),
        "tube": (0.78, 0.84, 0.85, 1.0),
        "wheel": (0.07, 0.10, 0.11, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Real-world dimensions (meters). Shared across all bases/accessories — the
# padded deck / column / table height are identical across the source variants;
# only the base swaps the root frame and the accessory swaps the bedside parts.
# ---------------------------------------------------------------------------
TOP_W = 0.500          # cushion width (Y)
PAD_T = 0.060          # cushion thickness (Z)
RAIL_T = 0.022         # stainless side rail thickness (square-ish)
RAIL_H = 0.075         # side rail height (Z)
FRAME_W = TOP_W + 2 * RAIL_T  # outer frame width including side rails

SEAT_LEN = 0.420       # fixed center/seat section length (X)
DECK_T = 0.030         # steel deck plate thickness (Z)

# Table-top height (top surface of the seat cushion) and derived deck top.
TABLE_TOP_Z = 0.980
SEAT_DECK_Z = TABLE_TOP_Z - PAD_T   # top of the steel seat deck under the pad

# Non-seat mattress section length (each hinged section).
SECTION_LEN = 0.560

# Hinge motion limits per fold direction. The down-fold of a -X section swings
# it down-and-inward toward the central base; limits are chosen so a folded
# leg/foot section stays clear of every base across the full trendelenburg tilt.
SECTION_UPPER_UP = 1.05          # +X (head/back) tilt up (~60 deg)
SECTION_UPPER_DOWN = 0.80        # -X leg (off-seat) fold down (~46 deg)
CHAINED_UPPER_DOWN = 0.40        # -X foot (chained off the leg) fold down (~23 deg)
HINGE_AXIS = (0.0, -1.0, 0.0)

# --- pedestal_crossfoot (S1) ---
FOOT_LEN = 0.820
FOOT_W = 0.560
FOOT_H = 0.110
COL_BASE_Z = FOOT_H - 0.060
COL_TOP_Z = SEAT_DECK_Z - DECK_T + 0.018
COL_W = 0.150
COL_TAPER = 0.190

# --- four_leg_splayed (S2) ---
N_LEGS = 4
HUB_R = 0.065
HUB_H = 0.092
# Hub top reaches up near the seat deck top so the central FIXED mount origin
# (at SEAT_DECK_Z) lies on real hub geometry (within the 15 mm tol); the hub
# embeds into the seat deck — an intentional structural mount overlap.
HUB_TOP_Z = SEAT_DECK_Z - 0.006
HUB_BOT_Z = HUB_TOP_Z - HUB_H
LEG_TUBE_R = 0.022
FOOT_SPREAD = 0.380
FOOT_PAD_R = 0.032
FOOT_PAD_H = 0.012
LEG_ANGLES = [math.pi / 4.0 + i * math.pi / 2.0 for i in range(N_LEGS)]

# --- caster_trolley (S3) ---
CHASSIS_LEN = 0.720
CHASSIS_W = 0.520
CHASSIS_H = 0.050
CASTER_WHEEL_R = 0.050
CASTER_WHEEL_W = 0.030
CASTER_FORK_H = 0.080
CASTER_FORK_T = 0.005
CASTER_HOUSING_R = 0.025
CASTER_HOUSING_H = 0.035
CASTER_PLATE_SIZE = 0.058
CASTER_PLATE_T = 0.008
CASTER_TOTAL_H = CASTER_WHEEL_R + CASTER_FORK_H + CASTER_HOUSING_H + CASTER_PLATE_T  # 0.173
CHASSIS_BOT_Z = CASTER_TOTAL_H
CHASSIS_TOP_Z = CHASSIS_BOT_Z + CHASSIS_H
CASTER_INSET_X = 0.065
CASTER_INSET_Y = 0.055
TROLLEY_COL_W = 0.140
TROLLEY_COL_BASE_Z = CHASSIS_TOP_Z - 0.015
TROLLEY_COL_TOP_Z = SEAT_DECK_Z - DECK_T + 0.018

# --- twin_column_H (S4) ---
BEAM_LEN = 0.720       # floor beam length along Y
BEAM_W = 0.180         # floor beam width along X
BEAM_H = 0.100
TC_COL_SIZE = 0.105
TC_COL_SPACING = 0.460
TC_COL_BASE_Z = BEAM_H - 0.040
TC_COL_TOP_Z = SEAT_DECK_Z - DECK_T + 0.018
N_COLUMNS = 2
CROSS_Z = 0.400
CROSS_H = 0.055
CROSS_D = 0.075

# --- arm_rails_horseshoe accessory (S1) ---
HS_TUBE_R = 0.013
HS_OPENING = 0.150
HS_PAD_T = 0.045
HS_REACH = 0.260       # horseshoe head support reach (X)
ARM_TUBE_R = 0.011

# --- side_rails_IV accessory (S5) ---
SAFETY_RAIL_LEN = SEAT_LEN * 0.92
SAFETY_RAIL_H = 0.200
SAFETY_RAIL_BAR_R = 0.012
SAFETY_RAIL_POST_R = 0.010
SAFETY_RAIL_POST_N = 3
IV_POLE_R = 0.014
IV_POLE_H = 1.100
IV_HOOK_R = 0.008
IV_HOOK_LEN = 0.070
IV_HOOK_N = 4

# --- padded_arm_boards accessory (S6) ---
ARM_BOARD_LEN = 0.250
ARM_BOARD_W = 0.120
BRACKET_REACH = 0.090
BRACKET_W = 0.050
BRACKET_T = 0.010
BRACKET_POST_H = 0.035


# ---------------------------------------------------------------------------
# Config / ResolvedConfig
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SurgicalBedConfig:
    base: BaseSupport | None = None
    accessories: Accessory | None = None
    section_count: int | None = None
    palette_style: PaletteStyle = "stainless_blue"
    deck_w_scale: float = 1.0
    column_h_scale: float = 1.0
    name: str = "surgical_bed"


@dataclass(frozen=True)
class ResolvedSurgicalBedConfig:
    base: BaseSupport
    accessories: Accessory
    section_count: int
    palette_style: PaletteStyle
    deck_w_scale: float
    column_h_scale: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> SurgicalBedConfig:
    rng = random.Random(seed)
    return SurgicalBedConfig(
        base=rng.choice(BASE_SUPPORTS),
        accessories=rng.choice(ACCESSORIES),
        section_count=rng.choices((3, 4), weights=SECTION_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        deck_w_scale=round(rng.uniform(0.90, 1.15), 4),
        column_h_scale=round(rng.uniform(0.90, 1.15), 4),
        name=f"seeded_surgical_bed_{seed}",
    )


def resolve_config(config: SurgicalBedConfig | None = None) -> ResolvedSurgicalBedConfig:
    cfg = config or SurgicalBedConfig()
    base = _pick(cfg.base, BASE_SUPPORTS)
    accessories = _pick(cfg.accessories, ACCESSORIES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    n = int(cfg.section_count) if cfg.section_count is not None else 3
    section_count = int(_clamp(n, N_SECTION_MIN, N_SECTION_MAX))

    deck_w_scale = _clamp(cfg.deck_w_scale, 0.90, 1.15)
    column_h_scale = _clamp(cfg.column_h_scale, 0.90, 1.15)

    return ResolvedSurgicalBedConfig(
        base=base,
        accessories=accessories,
        section_count=section_count,
        palette_style=palette_style,
        deck_w_scale=deck_w_scale,
        column_h_scale=column_h_scale,
        name=cfg.name if config is not None else "surgical_bed",
    )


def slot_choices_for_config(
    r: ResolvedSurgicalBedConfig,
) -> tuple[tuple[str, str], ...]:
    return (
        ("base", r.base),
        ("accessories", r.accessories),
        ("section_count", f"n{r.section_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Section layout. The fixed seat is the spine; (N-1) sections each hinge OFF the
# seat (uniform off-seat policy). One +X section (back/head), the rest -X
# (leg/foot...). Each section's hinge seam lies ON the seat deck top (so the
# joint origin sits on real seat geometry), and the section body extends
# outboard from there without overlapping its neighbor.
# ---------------------------------------------------------------------------
def _section_layout(n_sections: int) -> list[dict]:
    """Return the (N-1) hinged-section descriptors for a given section_count N.

    Each descriptor: {name, length, direction (+1 head / -1 foot), parent (the
    part the hinge is on), hinge_x (seam in the PARENT's local X), upper}.

    Layout: index 0 -> +X back (hinges off the fixed seat head edge). The first
    -X (leg) section hinges off the fixed seat foot edge. Any further -X (foot)
    section CHAINS off the previous -X section's far end -- a leg->foot chain --
    so the fixed seat deck never has to extend under a movable section (which
    would create a coincident double-deck / bare shelf). >= 1 section always
    hinges off the fixed seat.
    """
    n_hinged = n_sections - 1
    descs: list[dict] = []
    plus_done = False
    minus_count = 0
    prev_minus_name: str | None = None
    for i in range(n_hinged):
        name = f"section_{i}"
        if not plus_done:
            direction = +1
            plus_done = True
            parent = "seat"
            hinge_x = SEAT_LEN / 2.0  # +X back hinge on the seat head edge
            upper = SECTION_UPPER_UP
        else:
            direction = -1
            if minus_count == 0:
                # first leg section hinges off the fixed seat foot edge
                parent = "seat"
                hinge_x = -SEAT_LEN / 2.0
                upper = SECTION_UPPER_DOWN
            else:
                # foot section(s) chain off the previous -X section's far end.
                # Its down-fold compounds with the leg fold, so it gets a tighter
                # limit to keep the chain clear of the base.
                parent = prev_minus_name  # type: ignore[assignment]
                hinge_x = -SECTION_LEN
                upper = CHAINED_UPPER_DOWN
            prev_minus_name = name
            minus_count += 1
        descs.append(
            {
                "name": name,
                "length": SECTION_LEN,
                "direction": direction,
                "parent": parent,
                "hinge_x": hinge_x,
                "upper": upper,
            }
        )
    return descs


# ---------------------------------------------------------------------------
# Shared CadQuery deck / cushion / side-rail / tube helpers (verbatim from the
# 5-star source records; parameterized on length / deck width scale).
# ---------------------------------------------------------------------------
def _top_w(r: ResolvedSurgicalBedConfig) -> float:
    return TOP_W * r.deck_w_scale


def _frame_w(r: ResolvedSurgicalBedConfig) -> float:
    return _top_w(r) + 2 * RAIL_T


def _cushion_shape(length: float, top_w: float) -> cq.Workplane:
    """Padded cushion slab with a rounded soft top. Section-local frame: deck
    top at z=0, cushion up to +PAD_T, X over [-length/2, +length/2]."""
    return (
        cq.Workplane("XY")
        .box(length, top_w, PAD_T, centered=(True, True, False))
        .edges("|X")
        .fillet(0.018)
        .edges(">Z")
        .fillet(0.012)
    )


def _side_rails_shape(length: float, top_w: float) -> cq.Workplane:
    """Two stainless side rails framing a cushion section. Section-local frame,
    deck top at z=0. Rails run along X on both +/-Y edges."""
    y_off = top_w / 2.0 + RAIL_T / 2.0
    rail_r = (
        cq.Workplane("XY")
        .box(length, RAIL_T, RAIL_H, centered=(True, True, False))
        .translate((0.0, y_off, 0.0))
        .edges("|X")
        .fillet(0.006)
    )
    rail_l = (
        cq.Workplane("XY")
        .box(length, RAIL_T, RAIL_H, centered=(True, True, False))
        .translate((0.0, -y_off, 0.0))
        .edges("|X")
        .fillet(0.006)
    )
    return rail_r.union(rail_l)


def _deck_shape(length: float, top_w: float) -> cq.Workplane:
    """Steel deck plate under a cushion section. Top at z=0, down to -DECK_T."""
    return (
        cq.Workplane("XY")
        .box(length, top_w, DECK_T, centered=(True, True, True))
        .translate((0.0, 0.0, -DECK_T / 2.0))
        .edges("|X")
        .fillet(0.004)
    )


def _tube_from_path(points, radius: float) -> cq.Workplane:
    """Swept circular tube along a 3D spline path (verbatim source helper)."""
    edge_pts = [cq.Vector(*p) for p in points]
    path = cq.Workplane(obj=cq.Edge.makeSpline(edge_pts)).wire()
    p0 = points[0]
    p1 = points[1]
    tangent = cq.Vector(p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]).normalized()
    profile = cq.Workplane(cq.Plane(origin=cq.Vector(*p0), normal=tangent)).circle(radius)
    return profile.sweep(path, transition="round")


# ---------------------------------------------------------------------------
# Base module shapes (one per slot-A candidate).
# ---------------------------------------------------------------------------
def _foot_shape() -> cq.Workplane:
    """Beige cross-foot base on the floor (z=0..FOOT_H) — pedestal_crossfoot."""
    return (
        cq.Workplane("XY")
        .box(FOOT_LEN, FOOT_W, FOOT_H, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.030)
    )


def _column_shape(h_scale: float) -> cq.Workplane:
    """Tapered grey pedestal column, base at COL_BASE_Z, top reaching the seat
    deck underside (h_scale lifts the table-top reach slightly)."""
    top_z = COL_TOP_Z
    h = top_z - COL_BASE_Z
    col = (
        cq.Workplane("XY")
        .workplane(offset=COL_BASE_Z)
        .rect(COL_TAPER, COL_TAPER)
        .workplane(offset=h * 0.45)
        .rect(COL_W, COL_W)
        .workplane(offset=h * 0.55)
        .rect(COL_W, COL_W)
        .loft(combine=True)
    )
    collar = (
        cq.Workplane("XY")
        .box(COL_W + 0.018, COL_W + 0.018, 0.030, centered=(True, True, False))
        .translate((0.0, 0.0, top_z - 0.060))
        .edges("|Z")
        .fillet(0.006)
    )
    return col.union(collar)


def _hub_shape() -> cq.Workplane:
    """Central hub disk under the seat deck — four_leg_splayed."""
    return (
        cq.Workplane("XY")
        .workplane(offset=HUB_BOT_Z)
        .circle(HUB_R)
        .extrude(HUB_H)
        .edges(">Z")
        .fillet(0.005)
    )


def _splayed_leg_shape(index: int) -> cq.Workplane:
    """One splayed tubular leg with a floor foot-pad — four_leg_splayed."""
    angle = LEG_ANGLES[index]
    ca, sa = math.cos(angle), math.sin(angle)
    z_start = HUB_BOT_Z + HUB_H * 0.20
    start = (HUB_R * ca, HUB_R * sa, z_start)
    end = (FOOT_SPREAD * ca, FOOT_SPREAD * sa, FOOT_PAD_H)
    mid = tuple((a + b) * 0.5 for a, b in zip(start, end))
    tube = _tube_from_path([start, mid, end], LEG_TUBE_R)
    foot = (
        cq.Workplane("XY")
        .circle(FOOT_PAD_R)
        .extrude(FOOT_PAD_H)
        .edges(">Z")
        .fillet(0.003)
        .translate((FOOT_SPREAD * ca, FOOT_SPREAD * sa, 0.0))
    )
    return tube.union(foot)


def _chassis_shape() -> cq.Workplane:
    """Low rectangular trolley chassis plate — caster_trolley."""
    return (
        cq.Workplane("XY")
        .box(CHASSIS_LEN, CHASSIS_W, CHASSIS_H, centered=(True, True, False))
        .translate((0.0, 0.0, CHASSIS_BOT_Z))
        .edges("|Z")
        .fillet(0.018)
        .edges(">Z")
        .fillet(0.004)
    )


def _trolley_column_shape() -> cq.Workplane:
    """Tapered grey column from chassis to seat deck — caster_trolley."""
    h = TROLLEY_COL_TOP_Z - TROLLEY_COL_BASE_Z
    col_bot_w = TROLLEY_COL_W + 0.030
    col = (
        cq.Workplane("XY")
        .workplane(offset=TROLLEY_COL_BASE_Z)
        .rect(col_bot_w, col_bot_w)
        .workplane(offset=h * 0.35)
        .rect(TROLLEY_COL_W, TROLLEY_COL_W)
        .workplane(offset=h * 0.65)
        .rect(TROLLEY_COL_W, TROLLEY_COL_W)
        .loft(combine=True)
    )
    collar = (
        cq.Workplane("XY")
        .box(TROLLEY_COL_W + 0.020, TROLLEY_COL_W + 0.020, 0.025, centered=(True, True, False))
        .translate((0.0, 0.0, TROLLEY_COL_TOP_Z - 0.050))
        .edges("|Z")
        .fillet(0.005)
    )
    return col.union(collar)


def _caster_shape(cx: float, cy: float) -> cq.Workplane:
    """One fixed swivel caster (metal fork + housing + rubber wheel + axle) in
    world frame at (cx, cy), mounting plate top at z=CHASSIS_BOT_Z. Folded into
    the chassis part as a fixed decorative caster (Rule 1) with an axle pin for
    metal<->wheel connectivity."""
    z_plate_top = CHASSIS_BOT_Z
    z_plate_bot = z_plate_top - CASTER_PLATE_T
    z_housing_bot = z_plate_bot - CASTER_HOUSING_H
    z_axle = z_housing_bot - CASTER_FORK_H

    plate = (
        cq.Workplane("XY")
        .box(CASTER_PLATE_SIZE, CASTER_PLATE_SIZE, CASTER_PLATE_T, centered=(True, True, False))
        .translate((0.0, 0.0, z_plate_bot))
        .edges("|Z")
        .fillet(0.003)
    )
    housing = (
        cq.Workplane("XY")
        .circle(CASTER_HOUSING_R)
        .extrude(CASTER_HOUSING_H + 0.003)
        .translate((0.0, 0.0, z_housing_bot))
    )
    crown_w = CASTER_WHEEL_W + 2.0 * (CASTER_FORK_T + 0.006)
    crown = (
        cq.Workplane("XY")
        .box(crown_w, 0.040, 0.014, centered=(True, True, False))
        .translate((0.0, 0.0, z_housing_bot - 0.011))
        .edges("|Z")
        .fillet(0.004)
    )
    fork_y = CASTER_WHEEL_W / 2.0 + CASTER_FORK_T / 2.0 + 0.002
    leg_top = z_housing_bot - 0.009
    leg_bot = z_axle - 0.006
    leg_h = leg_top - leg_bot
    leg_cz = (leg_top + leg_bot) / 2.0
    leg_w = 0.034
    leg_r = (
        cq.Workplane("XY")
        .box(leg_w, CASTER_FORK_T, leg_h, centered=(True, True, True))
        .translate((0.0, fork_y, leg_cz))
        .edges("|Y")
        .fillet(0.002)
    )
    leg_l = (
        cq.Workplane("XY")
        .box(leg_w, CASTER_FORK_T, leg_h, centered=(True, True, True))
        .translate((0.0, -fork_y, leg_cz))
        .edges("|Y")
        .fillet(0.002)
    )
    axle_half = fork_y + CASTER_FORK_T / 2.0 + 0.003
    axle = (
        cq.Workplane("XY")
        .circle(0.005)
        .extrude(axle_half * 2.0)
        .translate((0.0, 0.0, -axle_half))
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
        .translate((0.0, 0.0, z_axle))
    )
    metal = plate.union(housing).union(crown).union(leg_r).union(leg_l).union(axle)
    metal = metal.translate((cx, cy, 0.0))
    return metal


def _caster_wheel_shape(cx: float, cy: float) -> cq.Workplane:
    """Rubber wheel of one caster, in world frame at (cx, cy)."""
    z_axle = CHASSIS_BOT_Z - (CASTER_PLATE_T + CASTER_HOUSING_H + CASTER_FORK_H)
    wheel = (
        cq.Workplane("XY")
        .circle(CASTER_WHEEL_R)
        .extrude(CASTER_WHEEL_W)
        .translate((0.0, 0.0, -CASTER_WHEEL_W / 2.0))
        .edges()
        .fillet(0.005)
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
        .translate((0.0, 0.0, z_axle))
    )
    return wheel.translate((cx, cy, 0.0))


def _beam_shape() -> cq.Workplane:
    """Beige floor beam running along Y — twin_column_H."""
    return (
        cq.Workplane("XY")
        .box(BEAM_W, BEAM_LEN, BEAM_H, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.022)
        .edges(">Z")
        .fillet(0.006)
    )


def _tc_column_shape() -> cq.Workplane:
    """One grey vertical column of the H-frame, centered at (0,0) — twin_column_H."""
    h = TC_COL_TOP_Z - TC_COL_BASE_Z
    base_size = TC_COL_SIZE * 1.18
    top_size = TC_COL_SIZE
    col = (
        cq.Workplane("XY")
        .workplane(offset=TC_COL_BASE_Z)
        .rect(base_size, base_size)
        .workplane(offset=h * 0.40)
        .rect(top_size, top_size)
        .workplane(offset=h * 0.60)
        .rect(top_size, top_size)
        .loft(combine=True)
    )
    collar = (
        cq.Workplane("XY")
        .box(top_size + 0.016, top_size + 0.016, 0.025, centered=(True, True, False))
        .translate((0.0, 0.0, TC_COL_TOP_Z - 0.050))
        .edges("|Z")
        .fillet(0.005)
    )
    return col.union(collar)


def _cross_member_shape() -> cq.Workplane:
    """Horizontal cross member bridging the two columns — twin_column_H."""
    span = TC_COL_SPACING + TC_COL_SIZE * 0.4
    return (
        cq.Workplane("XY")
        .box(CROSS_D, span, CROSS_H, centered=(True, True, False))
        .translate((0.0, 0.0, CROSS_Z - CROSS_H / 2.0))
        .edges("|Y")
        .fillet(0.008)
        .edges(">Z")
        .fillet(0.004)
    )


def _tc_top_saddle_shape() -> cq.Workplane:
    """Top mounting saddle of the H-frame: a flat steel plate spanning the two
    column tops at the seat plane (carries the seat deck and gives the central
    FIXED mount real geometry at x=0,y=0). twin_column_H."""
    saddle_w = TC_COL_SPACING + TC_COL_SIZE * 1.2  # spans both column centers (Y)
    saddle_d = TC_COL_SIZE * 1.4                    # along X
    saddle_h = 0.045
    # Top reaches up to the seat deck top plane so the central FIXED mount origin
    # (at SEAT_DECK_Z) sits on real saddle geometry (within the 15 mm tol). The
    # saddle embeds into the seat deck — an intentional structural mount overlap.
    top_z = SEAT_DECK_Z
    return (
        cq.Workplane("XY")
        .box(saddle_d, saddle_w, saddle_h, centered=(True, True, True))
        .translate((0.0, 0.0, top_z - saddle_h / 2.0))
        .edges("|Z")
        .fillet(0.006)
    )


# ---------------------------------------------------------------------------
# Accessory module shapes (one per slot-B candidate).
# ---------------------------------------------------------------------------
def _arm_rail_shape(sign: float, frame_w: float) -> cq.Workplane:
    """One curved tubular arm-support rail — arm_rails_horseshoe. Seat-local
    frame; sign = +1 (patient left) / -1 (right). Starts at the side rail."""
    y0 = sign * (frame_w / 2.0 - RAIL_T / 2.0)
    pts = [
        (0.10, y0, 0.005),
        (0.04, y0 + sign * 0.03, 0.12),
        (-0.02, y0 + sign * 0.07, 0.22),
        (0.06, y0 + sign * 0.05, 0.30),
        (0.17, y0 - sign * 0.01, 0.26),
    ]
    return _tube_from_path(pts, ARM_TUBE_R)


def _horseshoe_shape():
    """Horseshoe (U-shaped) head support. Head-local frame: open mouth +X, closed
    curve -X. Returns (tube_solid, pad_solid)."""
    r = HS_OPENING / 2.0 + HS_TUBE_R
    leg = HS_REACH * 0.9
    path = [
        (leg * 0.50, r, 0.0),
        (-leg * 0.20, r, 0.0),
        (-leg * 0.45, r * 0.60, 0.0),
        (-leg * 0.52, 0.0, 0.0),
        (-leg * 0.45, -r * 0.60, 0.0),
        (-leg * 0.20, -r, 0.0),
        (leg * 0.50, -r, 0.0),
    ]
    tube = _tube_from_path(path, HS_TUBE_R)
    pad = (
        cq.Workplane("XY")
        .box(leg * 0.50, 2.0 * r - 2.0 * HS_TUBE_R, HS_PAD_T, centered=(True, True, False))
        .translate((-leg * 0.10, 0.0, HS_TUBE_R - HS_PAD_T / 2.0))
        .edges("|X")
        .fillet(0.012)
    )
    return tube, pad


def _safety_rail_shape() -> cq.Workplane:
    """One straight stainless safety rail (bar + vertical posts) — side_rails_IV.
    Seat-local frame, deck top at z=0. Bar at z=SAFETY_RAIL_H, runs along X."""
    bar_z = SAFETY_RAIL_H - SAFETY_RAIL_BAR_R
    bar = (
        cq.Workplane("YZ")
        .workplane(offset=-SAFETY_RAIL_LEN / 2.0)
        .circle(SAFETY_RAIL_BAR_R)
        .extrude(SAFETY_RAIL_LEN)
    )
    bar = bar.translate((0.0, 0.0, bar_z))
    result = bar
    post_h = SAFETY_RAIL_H - SAFETY_RAIL_BAR_R
    xs = [-SAFETY_RAIL_LEN * 0.38, 0.0, SAFETY_RAIL_LEN * 0.38][:SAFETY_RAIL_POST_N]
    for px in xs:
        post = (
            cq.Workplane("XY")
            .circle(SAFETY_RAIL_POST_R)
            .extrude(post_h)
            .translate((px, 0.0, 0.0))
        )
        result = result.union(post)
    return result


def _iv_pole_shape() -> cq.Workplane:
    """IV pole: vertical stainless tube + base flange + curved top hooks + cap —
    side_rails_IV. Seat-local frame, deck top at z=0; pole rises along +Z."""
    pole = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, IV_POLE_H / 2.0))
        .cylinder(IV_POLE_H, IV_POLE_R, centered=(True, True, True))
    )
    flange = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, 0.015))
        .cylinder(0.030, IV_POLE_R * 1.8, centered=(True, True, True))
    )
    result = pole.union(flange)
    for i in range(IV_HOOK_N):
        angle = 2.0 * math.pi * i / IV_HOOK_N
        hook_pts = []
        n_seg = 8
        for s in range(n_seg + 1):
            t = s / n_seg
            a = t * math.pi * 0.45
            r_out = IV_HOOK_LEN * math.sin(a)
            z_drop = -IV_HOOK_LEN * (1.0 - math.cos(a))
            hook_pts.append(
                cq.Vector(
                    r_out * math.cos(angle),
                    r_out * math.sin(angle),
                    IV_POLE_H + z_drop,
                )
            )
        path = cq.Workplane(obj=cq.Edge.makeSpline(hook_pts)).wire()
        p0 = hook_pts[0]
        p1 = hook_pts[1]
        tangent = (p1 - p0).normalized()
        profile = cq.Workplane(cq.Plane(origin=p0, normal=tangent)).circle(IV_HOOK_R)
        result = result.union(profile.sweep(path, transition="round"))
    cap = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, IV_POLE_H + 0.012))
        .sphere(0.014)
    )
    return result.union(cap)


def _arm_board_bracket(sign: float, frame_w: float) -> cq.Workplane:
    """Short swing bracket arm for one arm board — padded_arm_boards. Seat-local
    frame, deck top at z=0. sign=+1 (+Y) / -1 (-Y)."""
    y_rail_outer = sign * (frame_w / 2.0)
    y_start = y_rail_outer - sign * RAIL_T
    y_end = y_rail_outer + sign * BRACKET_REACH
    y_center = (y_start + y_end) / 2.0
    arm_len = abs(y_end - y_start)
    arm = (
        cq.Workplane("XY")
        .box(BRACKET_W, arm_len, BRACKET_T, centered=(True, True, False))
        .translate((0.0, y_center, 0.0))
        .edges("|Z")
        .fillet(0.004)
    )
    post = (
        cq.Workplane("XY")
        .box(BRACKET_W, BRACKET_W, BRACKET_POST_H, centered=(True, True, False))
        .translate((0.0, y_end, 0.0))
        .edges("|Z")
        .fillet(0.003)
    )
    gusset = (
        cq.Workplane("XY")
        .box(BRACKET_W * 0.6, BRACKET_REACH * 0.35, BRACKET_T * 1.5, centered=(True, True, False))
        .translate((0.0, y_end - sign * BRACKET_REACH * 0.18, 0.0))
        .edges("|Z")
        .fillet(0.003)
    )
    return arm.union(post).union(gusset)


def _arm_board_pad(sign: float, frame_w: float) -> cq.Workplane:
    """Flat padded arm board on the swing bracket — padded_arm_boards."""
    y_rail_outer = sign * (frame_w / 2.0)
    pad_y_center = y_rail_outer + sign * (ARM_BOARD_W / 2.0 + 0.010)
    pad_z_base = BRACKET_POST_H - 0.005
    return (
        cq.Workplane("XY")
        .box(ARM_BOARD_LEN, ARM_BOARD_W, PAD_T, centered=(True, True, False))
        .translate((0.0, pad_y_center, pad_z_base))
        .edges("|X")
        .fillet(0.010)
        .edges(">Z")
        .fillet(0.006)
    )


# ---------------------------------------------------------------------------
# Base module factories. Each emits the root part(s) and returns the root part
# the seat is FIXED onto, plus the seat-mount joint origin (world).
# ---------------------------------------------------------------------------
def _build_base_pedestal(model, r: ResolvedSurgicalBedConfig, mats):
    base = model.part("base")
    base.visual(
        mesh_from_cadquery(_foot_shape(), "foot_block"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["foot"],
        name="foot_block", material_class_id="metal.paint_coated",
    )
    base.visual(
        mesh_from_cadquery(_column_shape(r.column_h_scale), "column_post"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["column"],
        name="column_post", material_class_id="metal.paint_coated",
    )
    return base


def _build_base_four_leg(model, r: ResolvedSurgicalBedConfig, mats):
    base = model.part("base")
    base.visual(
        mesh_from_cadquery(_hub_shape(), "hub"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["steel"],
        name="hub", material_class_id="metal.stainless_matte",
    )
    for i in range(N_LEGS):
        base.visual(
            mesh_from_cadquery(_splayed_leg_shape(i), f"base_leg_{i}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"base_leg_{i}", material_class_id="metal.stainless_matte",
        )
    return base


def _caster_positions() -> list[tuple[float, float]]:
    return [
        (+CHASSIS_LEN / 2.0 - CASTER_INSET_X, +CHASSIS_W / 2.0 - CASTER_INSET_Y),
        (+CHASSIS_LEN / 2.0 - CASTER_INSET_X, -CHASSIS_W / 2.0 + CASTER_INSET_Y),
        (-CHASSIS_LEN / 2.0 + CASTER_INSET_X, +CHASSIS_W / 2.0 - CASTER_INSET_Y),
        (-CHASSIS_LEN / 2.0 + CASTER_INSET_X, -CHASSIS_W / 2.0 + CASTER_INSET_Y),
    ]


def _build_base_caster(model, r: ResolvedSurgicalBedConfig, mats):
    base = model.part("base")
    base.visual(
        mesh_from_cadquery(_chassis_shape(), "chassis_frame"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["column"],
        name="chassis_frame", material_class_id="metal.paint_coated",
    )
    base.visual(
        mesh_from_cadquery(_trolley_column_shape(), "column_post"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["column"],
        name="column_post", material_class_id="metal.paint_coated",
    )
    # Four fixed swivel casters, folded into the chassis part as visuals (Rule 1:
    # the casters do not articulate, so they are not separate FIXED-joined parts).
    for i, (cx, cy) in enumerate(_caster_positions()):
        base.visual(
            mesh_from_cadquery(_caster_shape(cx, cy), f"caster_metal_{i}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"caster_metal_{i}", material_class_id="metal.stainless_matte",
        )
        base.visual(
            mesh_from_cadquery(_caster_wheel_shape(cx, cy), f"caster_wheel_{i}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["wheel"],
            name=f"caster_wheel_{i}", material_class_id="rubber.smooth_plain",
        )
    return base


def _build_base_twin_column(model, r: ResolvedSurgicalBedConfig, mats):
    base = model.part("base")
    base.visual(
        mesh_from_cadquery(_beam_shape(), "foot_beam"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["foot"],
        name="foot_beam", material_class_id="metal.paint_coated",
    )
    for i in range(N_COLUMNS):
        y_sign = -1.0 + 2.0 * i
        y_pos = y_sign * (TC_COL_SPACING / 2.0)
        base.visual(
            mesh_from_cadquery(_tc_column_shape(), f"column_{i}"),
            origin=Origin(xyz=(0.0, y_pos, 0.0)),
            material=mats["column"],
            name=f"column_{i}", material_class_id="metal.paint_coated",
        )
    base.visual(
        mesh_from_cadquery(_cross_member_shape(), "cross_member"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["column"],
        name="cross_member", material_class_id="metal.paint_coated",
    )
    base.visual(
        mesh_from_cadquery(_tc_top_saddle_shape(), "top_saddle"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["steel"],
        name="top_saddle", material_class_id="metal.stainless_matte",
    )
    return base


_BASE_BUILDERS = {
    "pedestal_crossfoot": _build_base_pedestal,
    "four_leg_splayed": _build_base_four_leg,
    "caster_trolley": _build_base_caster,
    "twin_column_H": _build_base_twin_column,
}


# ---------------------------------------------------------------------------
# Accessory module factories. Each emits FIXED bedside visuals on the seat
# part (Rule 1: non-articulating accessories live as inline seat visuals).
# ---------------------------------------------------------------------------
def _build_accessory_arm_rails(seat, r: ResolvedSurgicalBedConfig, mats):
    frame_w = _frame_w(r)
    seat.visual(
        mesh_from_cadquery(_arm_rail_shape(+1.0, frame_w), "arm_rail_l"),
        origin=Origin(xyz=(0.0, 0.0, -DECK_T)),
        material=mats["tube"],
        name="arm_rail_left", material_class_id="metal.stainless_matte",
    )
    seat.visual(
        mesh_from_cadquery(_arm_rail_shape(-1.0, frame_w), "arm_rail_r"),
        origin=Origin(xyz=(0.0, 0.0, -DECK_T)),
        material=mats["tube"],
        name="arm_rail_right", material_class_id="metal.stainless_matte",
    )
    # Horseshoe head support, cradled over the fixed seat spine (centered on the
    # seat, NOT overhanging the +X back section). If it were placed at the head
    # seam it would sit inside the back section's swept-up arc and the rising
    # backrest would ram it; centered on the fixed deck it clears section_0
    # across the full tilt range.
    hs_tube, hs_pad = _horseshoe_shape()
    hx = 0.0
    seat.visual(
        mesh_from_cadquery(hs_tube, "head_tube"),
        origin=Origin(xyz=(hx, 0.0, PAD_T + HS_TUBE_R)),
        material=mats["tube"],
        name="head_tube", material_class_id="metal.stainless_matte",
    )
    seat.visual(
        mesh_from_cadquery(hs_pad, "head_pad"),
        origin=Origin(xyz=(hx, 0.0, PAD_T + HS_TUBE_R)),
        material=mats["pad"],
        name="head_pad", material_class_id="leather.smooth_plain",
    )


def _build_accessory_side_rails(seat, r: ResolvedSurgicalBedConfig, mats):
    frame_w = _frame_w(r)
    y_rail_offset = frame_w / 2.0 - RAIL_T / 2.0
    safety_rail_mesh = mesh_from_cadquery(_safety_rail_shape(), "safety_rail")
    for i in range(2):
        sign = 1.0 if i == 0 else -1.0
        seat.visual(
            safety_rail_mesh,
            origin=Origin(xyz=(0.0, sign * y_rail_offset, -DECK_T)),
            material=mats["tube"],
            name=f"safety_rail_{i}", material_class_id="metal.stainless_matte",
        )
    # IV pole clamped to the side rail toward the seat center (foot-ward of the
    # back hinge and head-ward of the leg hinge). At the old +X head corner the
    # tall pole sat in the back section's swept-up arc; a mid-side mount clears
    # both the rising back (+X) and the folding leg (-X) across their ranges.
    iv_x = -0.10
    iv_y = frame_w / 2.0 - RAIL_T / 2.0
    seat.visual(
        mesh_from_cadquery(_iv_pole_shape(), "iv_pole"),
        origin=Origin(xyz=(iv_x, iv_y, -DECK_T)),
        material=mats["tube"],
        name="iv_pole", material_class_id="metal.stainless_matte",
    )


def _build_accessory_arm_boards(seat, r: ResolvedSurgicalBedConfig, mats):
    frame_w = _frame_w(r)
    for i, sign in enumerate((+1.0, -1.0)):
        seat.visual(
            mesh_from_cadquery(_arm_board_bracket(sign, frame_w), f"arm_bracket_{i}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"arm_bracket_{i}", material_class_id="metal.stainless_matte",
        )
        seat.visual(
            mesh_from_cadquery(_arm_board_pad(sign, frame_w), f"arm_pad_{i}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["pad"],
            name=f"arm_pad_{i}", material_class_id="leather.smooth_plain",
        )


_ACCESSORY_BUILDERS = {
    "arm_rails_horseshoe": _build_accessory_arm_rails,
    "side_rails_IV": _build_accessory_side_rails,
    "padded_arm_boards": _build_accessory_arm_boards,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_surgical_bed(
    config: SurgicalBedConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"sbed_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    top_w = _top_w(r)
    # Fixed seat deck stays SEAT_LEN: the -X run is covered by hinged leg/foot
    # sections (leg off the seat, foot chained off the leg), so the fixed deck is
    # never extended under a movable section.
    seat_deck_len = SEAT_LEN

    # ---- Root base ----
    base = _BASE_BUILDERS[r.base](model, r, mats)

    # ---- Fixed seat / center section (the spine), FIXED onto the base ----
    seat = model.part("seat")
    seat.visual(
        mesh_from_cadquery(_deck_shape(seat_deck_len, top_w), "seat_deck"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["steel"],
        name="seat_deck", material_class_id="metal.stainless_matte",
    )
    seat.visual(
        mesh_from_cadquery(_side_rails_shape(SEAT_LEN, top_w), "seat_rails"),
        origin=Origin(xyz=(0.0, 0.0, -DECK_T)),
        material=mats["steel"],
        name="seat_rails", material_class_id="metal.stainless_matte",
    )
    seat.visual(
        mesh_from_cadquery(_cushion_shape(SEAT_LEN, top_w), "seat_pad"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["pad"],
        name="seat_pad", material_class_id="leather.smooth_plain",
    )

    # Bedside accessories (FIXED inline visuals on the seat frame).
    _ACCESSORY_BUILDERS[r.accessories](seat, r, mats)

    # Trendelenburg tilt: the whole tabletop pivots head-down / foot-down about
    # the base column top (axis Y, +-15 deg) -- the defining OR-table DOF. The
    # pivot sits at the seat-deck plane on real base hardware, so the seat stays
    # mated to the base across the tilt range.
    model.articulation(
        "base_to_seat",
        ArticulationType.REVOLUTE,
        parent=base,
        child=seat,
        origin=Origin(xyz=(0.0, 0.0, SEAT_DECK_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=400.0,
            velocity=0.2,
            lower=-TRENDELENBURG_TILT,
            upper=TRENDELENBURG_TILT,
        ),
    )

    # ---- Hinged mattress sections (off-seat back + leg; chained foot) ----
    part_by_name: dict[str, object] = {"seat": seat}
    for desc in _section_layout(r.section_count):
        name = desc["name"]
        length = desc["length"]
        direction = desc["direction"]
        section = model.part(name)
        x_off = direction * length / 2.0
        section.visual(
            mesh_from_cadquery(_deck_shape(length, top_w), f"{name}_deck"),
            origin=Origin(xyz=(x_off, 0.0, 0.0)),
            material=mats["steel"],
            name=f"{name}_deck", material_class_id="metal.stainless_matte",
        )
        section.visual(
            mesh_from_cadquery(_side_rails_shape(length, top_w), f"{name}_rails"),
            origin=Origin(xyz=(x_off, 0.0, -DECK_T)),
            material=mats["steel"],
            name=f"{name}_rails", material_class_id="metal.stainless_matte",
        )
        section.visual(
            mesh_from_cadquery(_cushion_shape(length, top_w), f"{name}_pad"),
            origin=Origin(xyz=(x_off, 0.0, 0.0)),
            material=mats["pad"],
            name=f"{name}_pad", material_class_id="leather.smooth_plain",
        )
        parent_part = part_by_name[desc["parent"]]
        model.articulation(
            f"{desc['parent']}_to_{name}",
            ArticulationType.REVOLUTE,
            parent=parent_part,
            child=section,
            origin=Origin(xyz=(desc["hinge_x"], 0.0, 0.0)),
            axis=HINGE_AXIS,
            motion_limits=MotionLimits(
                effort=200.0, velocity=0.5, lower=0.0, upper=desc["upper"]
            ),
        )
        part_by_name[name] = section

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_surgical_bed(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_surgical_bed(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_surgical_bed_tests(
    object_model: ArticulatedObject,
    config: SurgicalBedConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    base = object_model.get_part("base")
    seat = object_model.get_part("seat")

    # ---- Base / seat structural allowances (element-scoped). ----
    # Each base's top hardware embeds into the seat deck underside (pedestal
    # mount). Allow that intentional overlap and the section seam overlaps.
    if r.base == "pedestal_crossfoot":
        for el in ("seat_deck", "seat_rails", "seat_pad"):
            ctx.allow_overlap(
                base, seat, elem_a="column_post", elem_b=el,
                reason="Column top seats into the seat frame underside (pedestal mount).",
            )
    elif r.base == "four_leg_splayed":
        for el in ("seat_deck", "seat_rails", "seat_pad"):
            ctx.allow_overlap(
                base, seat, elem_a="hub", elem_b=el,
                reason="Hub top embeds into the seat frame underside (mount).",
            )
    elif r.base == "caster_trolley":
        for el in ("seat_deck", "seat_rails", "seat_pad"):
            ctx.allow_overlap(
                base, seat, elem_a="column_post", elem_b=el,
                reason="Trolley column top embeds into the seat frame underside (mount).",
            )
    else:  # twin_column_H
        for ba in [f"column_{i}" for i in range(N_COLUMNS)] + ["top_saddle"]:
            for el in ("seat_deck", "seat_rails", "seat_pad"):
                ctx.allow_overlap(
                    base, seat, elem_a=ba, elem_b=el,
                    reason="Twin column / top saddle embeds into the seat frame underside (mount).",
                )

    # Base top hardware meets the seat frame at the mount junction, where the
    # bedside accessory visuals (rails / IV pole / arm boards / horseshoe) also
    # mount. Allow that local junction overlap between base visuals and the
    # seat-mounted accessory visuals (element-scoped).
    _base_top_visuals = [v.name for v in base.visuals]
    _accessory_visuals = [
        v.name
        for v in seat.visuals
        if v.name not in ("seat_deck", "seat_rails", "seat_pad")
    ]
    for ba in _base_top_visuals:
        for ac in _accessory_visuals:
            ctx.allow_overlap(
                base, seat, elem_a=ba, elem_b=ac,
                reason="Base mount hardware meets the seat-frame bedside accessory at the junction.",
            )

    # Section seams: at rest each section meets the seat deck/pad/rails. Allow
    # the seam-region overlaps between seat and each section.
    section_names = [d["name"] for d in _section_layout(r.section_count)]
    _seat_seam = ("seat_deck", "seat_rails", "seat_pad")
    for sn in section_names:
        sect = object_model.get_part(sn)
        for sa in _seat_seam:
            for sb in (f"{sn}_deck", f"{sn}_rails", f"{sn}_pad"):
                ctx.allow_overlap(
                    seat, sect, elem_a=sa, elem_b=sb,
                    reason="Mattress section meets the seat at the hinge seam.",
                )
        # Adjacent -X sections tile end-to-end; allow neighbor seam overlap.
        for sn2 in section_names:
            if sn2 == sn:
                continue
            for sa in (f"{sn}_deck", f"{sn}_rails", f"{sn}_pad"):
                for sb in (f"{sn2}_deck", f"{sn2}_rails", f"{sn2}_pad"):
                    ctx.allow_overlap(
                        sect, object_model.get_part(sn2), elem_a=sa, elem_b=sb,
                        reason="Adjacent mattress sections meet end-to-end at rest.",
                    )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("seat part present", "seat" in part_names, details=str(sorted(part_names)))

    # base_to_seat is the trendelenburg tilt DOF of the tabletop about the base.
    bs = object_model.get_articulation("base_to_seat")
    ctx.check(
        "tabletop tilts (trendelenburg) about the base",
        bs.articulation_type == ArticulationType.REVOLUTE,
        details=str(bs.articulation_type),
    )
    ctx.check(
        "trendelenburg tilt axis is Y",
        abs(bs.axis[1]) > 0.9 and abs(bs.axis[0]) < 1e-6 and abs(bs.axis[2]) < 1e-6,
        details=str(tuple(bs.axis)),
    )
    ctx.check(
        "trendelenburg tilt is a realistic +-15 deg range",
        bs.motion_limits is not None
        and bs.motion_limits.lower < 0.0 < bs.motion_limits.upper
        and abs(bs.motion_limits.upper) <= math.radians(20.0) + 1e-6,
        details=str(bs.motion_limits),
    )

    # Section hinges: >= 1 REVOLUTE section hinges off the fixed seat; outer foot
    # sections chain off their -X predecessor (leg->foot chain).
    section_joints = [
        a for a in object_model.articulations if str(a.child).startswith("section_")
    ]
    ctx.check(
        "at least one REVOLUTE section hinge",
        len(section_joints) >= 1
        and all(j.articulation_type == ArticulationType.REVOLUTE for j in section_joints),
        details=f"n={len(section_joints)}",
    )
    ctx.check(
        "at least one section hinges off the fixed seat",
        any(j.parent == "seat" for j in section_joints),
        details=str([j.parent for j in section_joints]),
    )
    ctx.check(
        "chained sections parent to the seat or another section",
        all(j.parent == "seat" or str(j.parent).startswith("section_") for j in section_joints),
        details=str([j.parent for j in section_joints]),
    )
    ctx.check(
        "section_count = 1 fixed seat + (N-1) hinged sections",
        len(section_joints) == r.section_count - 1,
        details=f"joints={len(section_joints)} N={r.section_count}",
    )
    for j in section_joints:
        ctx.check(
            f"{j.name} axis is Y (hinge)",
            abs(j.axis[1]) > 0.9 and abs(j.axis[0]) < 1e-6 and abs(j.axis[2]) < 1e-6,
            details=str(tuple(j.axis)),
        )

    # caster trolley: 4 fixed casters folded into the chassis part as visuals.
    if r.base == "caster_trolley":
        wheels = [v for v in base.visuals if v.name.startswith("caster_wheel_")]
        ctx.check(
            "4 fixed casters present on the chassis",
            len(wheels) == 4,
            details=f"wheels={len(wheels)}",
        )
    # side_rails accessory: IV pole present.
    if r.accessories == "side_rails_IV":
        ctx.check(
            "IV pole present on the seat",
            any(v.name == "iv_pole" for v in seat.visuals),
            details=str([v.name for v in seat.visuals]),
        )

    # ---- Structural placement at rest. ----
    seat_pad_aabb = ctx.part_element_world_aabb(seat, elem="seat_pad")
    ctx.check(
        "seat cushion top at table height",
        seat_pad_aabb is not None and abs(seat_pad_aabb[1][2] - TABLE_TOP_Z) < 0.03,
        details=str(seat_pad_aabb),
    )
    base_aabb = ctx.part_world_aabb(base)
    ctx.check(
        "base sits on the floor",
        base_aabb is not None and base_aabb[0][2] < 0.01,
        details=str(base_aabb),
    )

    # ---- A section actually folds when actuated. ----
    j0 = section_joints[0]
    sect0 = object_model.get_part(j0.child)
    rest = ctx.part_world_aabb(sect0)
    with ctx.pose({j0: 1.00}):
        posed = ctx.part_world_aabb(sect0)
    if rest is not None and posed is not None:
        # direction +1 (back) tilts up; -1 (leg) folds down -> z-extent moves.
        moved = abs(posed[1][2] - rest[1][2]) > 0.10 or abs(posed[0][2] - rest[0][2]) > 0.10
        ctx.check(
            "a mattress section actually articulates when posed",
            moved,
            details=f"rest_z=({rest[0][2]:.3f},{rest[1][2]:.3f}) "
            f"posed_z=({posed[0][2]:.3f},{posed[1][2]:.3f})",
        )

    # ---- Lock-in: bedside accessories clear the +X back section's swept-up arc.
    # The IV pole / horseshoe head support are FIXED seat visuals; a raised
    # backrest must never ram them. Pose the +X back to its full tilt and assert
    # the accessory elements stay clear of section_0. This is ELEMENT-scoped: the
    # accessories are seat visuals, so the whitelisted seat<->section_0 part-pair
    # allowance would otherwise mask an accessory-into-back penetration.
    back_joint = next((j for j in section_joints if str(j.child) == "section_0"), None)
    if back_joint is not None and back_joint.motion_limits is not None:
        accessory_elems = [
            v.name
            for v in seat.visuals
            if v.name in ("iv_pole", "head_tube", "head_pad")
        ]
        with ctx.pose({back_joint: back_joint.motion_limits.upper}):
            sec0_aabb = ctx.part_world_aabb(object_model.get_part("section_0"))
            for en in accessory_elems:
                el_aabb = ctx.part_element_world_aabb(seat, elem=en)
                clear = True
                if sec0_aabb is not None and el_aabb is not None:
                    clear = any(
                        el_aabb[0][k] - sec0_aabb[1][k] > 0.0
                        or sec0_aabb[0][k] - el_aabb[1][k] > 0.0
                        for k in range(3)
                    )
                ctx.check(
                    f"accessory {en} clears the raised back section",
                    clear,
                    details=f"tilt={back_joint.motion_limits.upper:.3f} "
                    f"elem={el_aabb} section_0={sec0_aabb}",
                )

    # ---- slot_choices recorded with section_count encoded. ----
    ctx.check(
        "slot_choices recorded with section_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "SurgicalBedConfig",
    "ResolvedSurgicalBedConfig",
    "build_surgical_bed",
    "build_seeded_surgical_bed",
    "config_from_seed",
    "resolve_config",
    "run_surgical_bed_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
