# SPDX-License-Identifier: Apache-2.0

"""Adjustable hospital / treatment bed modular template.

Identity (spec ``specs_modular_v1/Healthcare_Adjustable_hospital_bed.md``): an
adjustable medical bed / treatment couch = a wheeled or legged support base
carrying a multi-section padded deck with at least one REVOLUTE backrest section
(the defining "adjustable" DOF), optionally a central PRISMATIC hi-lo lift
column, optional REVOLUTE drop-down side rails, and tubular / none / molded-panel
head+foot boards. NOT a plain bed/nightstand (no articulating sections), NOT a
stretcher/trolley (no hinged backrest), NOT a sitting surgical_chair.

Sourced from the ``hospital_bed`` 5-star pool (2 parents + 5 converged forks),
all synced under ``data/records/``:
  * S1 rec_a-single-section-adjustable-hospital-bed-... -> caster bed frame,
       single backrest, tubular boards, cushion/caster idioms.
  * S2 rec_an-adjustable-examination-treatment-couch-... -> 4-leg exam couch, open (no boards).
  * S3 rec_hospbed_var_knee_gatch      -> 2-section deck (backrest + knee).
  * S4 rec_hospbed_var_three_section   -> 3-section profiling deck (backrest + thigh + chained calf).
  * S5 rec_hospbed_var_side_rails      -> drop-down REVOLUTE side rails.
  * S6 rec_hospbed_var_hilo_column     -> cruciform wheeled base + PRISMATIC lift column.
  * S7 rec_hospbed_var_footboard_panel -> solid molded end-panel boards.

Structure (pattern = ``mixed``). One shared world convention (bed long axis X,
head -X / foot +X, deck top z=0.62). A ``base`` slot roots the bed on the floor
and returns the deck-carrying part (== the root for caster/four-leg, or a
PRISMATIC-lifted ``lift_column`` for hi-lo). A shared ``_deck_frame`` builds the
tubular under-frame + fixed hip deck + mattress + hinge barrels on that deck
part. Deck sections (backrest always; + knee for N=2; + thigh + chained calf for
N=3) hinge REVOLUTE off the deck part. Head/foot boards are deck-part visuals
(Rule 1). Optional drop-down side rails are a REVOLUTE child pair.

  * base (3): caster_base / four_leg_couch / hi_lo_column.
  * deck_sections (N in {1,2,3}): the multiplicity axis (adjustable deck).
  * boards (3): tubular_rail_boards / open_no_board / solid_panel_boards.
  * side_rails (2): none / dropdown_side_rails.

3 x 3 x 3 x 2 = 54 slot topologies. Cushions are preserved as
``superellipse_side_loft`` meshes and molded boards as ``ExtrudeGeometry`` meshes
(no boxy downgrade). Hinges are captured-pin (barrel + tube) so mating contracts
are grandfathered per AUTHORING Rule 2 (as in the Science_Surgical_bed reference);
the joint origin sits on the deck hinge-barrel hardware.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    superellipse_side_loft,
)

__modular__ = True

BaseSupport = Literal["caster_base", "four_leg_couch", "hi_lo_column"]
Boards = Literal["tubular_rail_boards", "open_no_board", "solid_panel_boards"]
SideRails = Literal["none", "dropdown_side_rails"]
PaletteStyle = Literal[
    "white_blue", "grey_green", "beige_cream", "chrome_teal", "white_burgundy"
]

BASE_SUPPORTS: tuple[BaseSupport, ...] = ("caster_base", "four_leg_couch", "hi_lo_column")
BOARDS: tuple[Boards, ...] = ("tubular_rail_boards", "open_no_board", "solid_panel_boards")
SIDE_RAILS: tuple[SideRails, ...] = ("none", "dropdown_side_rails")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "white_blue", "grey_green", "beige_cream", "chrome_teal", "white_burgundy"
)

N_SECTION_MIN = 1
N_SECTION_MAX = 3
SECTION_WEIGHTS = (0.45, 0.30, 0.25)  # for N = (1, 2, 3): small N high-frequency

# ---------------------------------------------------------------------------
# Palette colorways. Every .visual(material=...) draws from one of these keys.
# painted-steel frame + off-white deck panel + fabric mattress + rubber tire +
# grey caster metal + bright hub + column paint + molded panel plastic.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float]]] = {
    "white_blue": {
        "frame": (0.94, 0.94, 0.90), "deck": (0.86, 0.85, 0.80),
        "fabric": (0.53, 0.68, 0.91), "rubber": (0.05, 0.05, 0.05),
        "metal": (0.56, 0.56, 0.54), "hub": (0.74, 0.74, 0.70),
        "column": (0.72, 0.72, 0.70), "panel": (0.80, 0.83, 0.86),
    },
    "grey_green": {
        "frame": (0.60, 0.62, 0.63), "deck": (0.80, 0.81, 0.80),
        "fabric": (0.28, 0.55, 0.44), "rubber": (0.06, 0.06, 0.07),
        "metal": (0.50, 0.52, 0.53), "hub": (0.68, 0.70, 0.70),
        "column": (0.45, 0.47, 0.48), "panel": (0.70, 0.78, 0.74),
    },
    "beige_cream": {
        "frame": (0.90, 0.87, 0.80), "deck": (0.88, 0.84, 0.75),
        "fabric": (0.80, 0.70, 0.52), "rubber": (0.08, 0.07, 0.06),
        "metal": (0.62, 0.60, 0.55), "hub": (0.76, 0.73, 0.66),
        "column": (0.70, 0.66, 0.58), "panel": (0.85, 0.80, 0.70),
    },
    "chrome_teal": {
        "frame": (0.82, 0.84, 0.86), "deck": (0.74, 0.76, 0.78),
        "fabric": (0.10, 0.45, 0.50), "rubber": (0.05, 0.06, 0.06),
        "metal": (0.80, 0.82, 0.84), "hub": (0.88, 0.90, 0.92),
        "column": (0.62, 0.64, 0.66), "panel": (0.78, 0.82, 0.84),
    },
    "white_burgundy": {
        "frame": (0.93, 0.93, 0.91), "deck": (0.80, 0.78, 0.76),
        "fabric": (0.45, 0.12, 0.20), "rubber": (0.05, 0.05, 0.05),
        "metal": (0.55, 0.55, 0.55), "hub": (0.72, 0.72, 0.70),
        "column": (0.70, 0.70, 0.70), "panel": (0.82, 0.80, 0.80),
    },
}

# ---------------------------------------------------------------------------
# World frame constants (meters). Shared across all bases/boards/sections; from
# the dominant caster-bed convention (S1/S3/S4/S5/S6/S7).
# ---------------------------------------------------------------------------
BED_LEN = 2.0
DECK_TOP_Z = 0.62
BACKREST_HINGE_X = -BED_LEN / 6.0  # -0.3333
CORNER_X = 1.0                     # head/foot board + caster corner (X)
RAIL_Y = 0.47                      # side-rail / corner Y
TUBE_R = 0.018
HEAD_X = -0.96
FOOT_X = 0.96
SIDE_RAIL_TOP_Z = 0.585
SIDE_RAIL_LOW_Z = 0.36
BARREL_Y = 0.49                    # hinge barrel outboard Y

# Backrest raises head (+Y axis), sections raise foot (-Y axis). Nominal upper
# limits are clearance-safe at full travel (sections swing up-and-inward, away
# from the end boards). backrest_range_scale (<=1) only reduces them.
BACKREST_UPPER = 1.15
SECTION_UPPER = 0.70
CALF_UPPER = 0.80
CALF_LOWER = -0.30
LIFT_UPPER = 0.30
RAIL_UPPER = 1.57


# ---------------------------------------------------------------------------
# Config / ResolvedConfig
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HospitalBedConfig:
    base: BaseSupport | None = None
    section_count: int | None = None
    boards: Boards | None = None
    side_rails: SideRails | None = None
    palette_style: PaletteStyle = "white_blue"
    mattress_thickness_scale: float = 1.0
    backrest_range_scale: float = 1.0
    name: str = "hospital_bed"


@dataclass(frozen=True)
class ResolvedHospitalBedConfig:
    base: BaseSupport
    section_count: int
    boards: Boards
    side_rails: SideRails
    palette_style: PaletteStyle
    mattress_thickness_scale: float
    backrest_range_scale: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


def config_from_seed(seed: int) -> HospitalBedConfig:
    rng = random.Random(seed)
    return HospitalBedConfig(
        base=rng.choice(BASE_SUPPORTS),
        section_count=rng.choices((1, 2, 3), weights=SECTION_WEIGHTS, k=1)[0],
        boards=rng.choice(BOARDS),
        side_rails=rng.choices(SIDE_RAILS, weights=(0.5, 0.5), k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        mattress_thickness_scale=round(rng.uniform(0.90, 1.15), 4),
        backrest_range_scale=round(rng.uniform(0.80, 1.00), 4),
        name=f"seeded_hospital_bed_{seed}",
    )


def resolve_config(config: HospitalBedConfig | None = None) -> ResolvedHospitalBedConfig:
    cfg = config or HospitalBedConfig()
    n = int(cfg.section_count) if cfg.section_count is not None else 1
    return ResolvedHospitalBedConfig(
        base=_pick(cfg.base, BASE_SUPPORTS),
        section_count=int(_clamp(n, N_SECTION_MIN, N_SECTION_MAX)),
        boards=_pick(cfg.boards, BOARDS),
        side_rails=_pick(cfg.side_rails, SIDE_RAILS),
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        mattress_thickness_scale=_clamp(cfg.mattress_thickness_scale, 0.90, 1.15),
        backrest_range_scale=_clamp(cfg.backrest_range_scale, 0.80, 1.00),
        name=cfg.name if config is not None else "hospital_bed",
    )


def slot_choices_for_config(r: ResolvedHospitalBedConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("base", r.base),
        ("deck_sections", f"n{r.section_count}"),
        ("boards", r.boards),
        ("side_rails", r.side_rails),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Primitive helpers (verbatim idioms from S1 L32-89 / S7 L62-80).
# ---------------------------------------------------------------------------
def _origin(x: float, y: float, z: float, rpy=(0.0, 0.0, 0.0)) -> Origin:
    return Origin(xyz=(x, y, z), rpy=rpy)


def _cyl_x(part, *, name, x, y, z, length, radius, material):
    part.visual(Cylinder(radius=radius, length=length),
                origin=_origin(x, y, z, rpy=(0.0, math.pi / 2.0, 0.0)),
                material=material, name=name, material_class_id="metal.paint_coated")


def _cyl_y(part, *, name, x, y, z, length, radius, material):
    part.visual(Cylinder(radius=radius, length=length),
                origin=_origin(x, y, z, rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=material, name=name, material_class_id="metal.generic_plain")


def _cyl_z(part, *, name, x, y, z, length, radius, material):
    part.visual(Cylinder(radius=radius, length=length),
                origin=_origin(x, y, z), material=material, name=name, material_class_id="metal.generic_plain")


def _cushion_mesh(*, name, center_x, length, width, z_min, z_max, edge_taper, softness):
    """Soft rounded-crowned cushion (superellipse_side_loft). S1 L59-89 verbatim."""
    half_w = width / 2.0
    sections = [
        (-half_w, z_min + softness, z_max - softness * 0.5, length - edge_taper),
        (-half_w + softness, z_min, z_max, length),
        (0.0, z_min, z_max + softness * 0.35, length),
        (half_w - softness, z_min, z_max, length),
        (half_w, z_min + softness, z_max - softness * 0.5, length - edge_taper),
    ]
    geom = superellipse_side_loft(sections, exponents=3.2, segments=64, cap=True, closed=True)
    geom.translate(center_x, 0.0, 0.0)
    return mesh_from_geometry(geom, name)


def _molded_panel_mesh(*, name, span_z, span_y, thickness, corner_radius):
    """Flat rounded-rect molded end panel, thin along world X. S7 L62-80 verbatim."""
    profile = rounded_rect_profile(span_z, span_y, corner_radius, corner_segments=8)
    geom = ExtrudeGeometry(profile, thickness, center=True, cap=True, closed=True)
    geom.rotate_y(math.pi / 2.0)
    return mesh_from_geometry(geom, name)


def _add_caster(part, *, prefix, x, y, mats):
    """Hospital-bed swivel caster sub-assembly folded into `part` as visuals
    (Rule 1: casters do not articulate). S1 L201-271 / S6 L92-141."""
    _cyl_y(part, name=f"{prefix}_tire", x=x, y=y, z=0.028, length=0.026, radius=0.028, material=mats["rubber"])
    _cyl_z(part, name=f"{prefix}_stem", x=x, y=y, z=0.121, length=0.082, radius=0.010, material=mats["metal"])
    _cyl_z(part, name=f"{prefix}_swivel", x=x, y=y, z=0.076, length=0.012, radius=0.020, material=mats["metal"])
    part.visual(Box((0.046, 0.048, 0.010)), origin=_origin(x, y, 0.069), material=mats["metal"], name=f"{prefix}_fork_bridge", material_class_id="metal.brushed_silver")
    for dy, side in [(-0.018, "0"), (0.018, "1")]:
        part.visual(Box((0.024, 0.006, 0.064)), origin=_origin(x, y + dy, 0.040), material=mats["metal"], name=f"{prefix}_fork_{side}", material_class_id="metal.brushed_silver")
    _cyl_y(part, name=f"{prefix}_axle", x=x, y=y, z=0.028, length=0.050, radius=0.0045, material=mats["metal"])
    _cyl_y(part, name=f"{prefix}_hub", x=x, y=y, z=0.028, length=0.028, radius=0.012, material=mats["hub"])


# ---------------------------------------------------------------------------
# Deck geometry plan (derived from N).
# ---------------------------------------------------------------------------
def _deck_plan(n: int) -> dict:
    """Return fixed-hip-deck extent + foot-side hinge x for a section_count N."""
    hip_start = BACKREST_HINGE_X + 0.033  # -0.30
    if n == 1:
        return {"foot_hinge": None, "hip_start": hip_start, "hip_end": 0.98}
    if n == 2:
        fh = 0.30
        return {"foot_hinge": fh, "hip_start": hip_start, "hip_end": fh - 0.022}
    fh = 0.10  # n == 3
    return {"foot_hinge": fh, "hip_start": hip_start, "hip_end": fh - 0.022}


# ---------------------------------------------------------------------------
# Shared deck under-frame (built on the deck-carrying part for every base).
# S1 L133-199/L273-284 + S3 L300-324 + S6 L262-296.
# ---------------------------------------------------------------------------
def _deck_frame(deck, r: ResolvedHospitalBedConfig, mats) -> None:
    thick = r.mattress_thickness_scale
    plan = _deck_plan(r.section_count)

    # Upper + lower tubular side rails (reach the corner boards at x=+-1.0).
    for y, s in [(-RAIL_Y, "0"), (RAIL_Y, "1")]:
        _cyl_x(deck, name=f"side_rail_{s}", x=0.0, y=y, z=SIDE_RAIL_TOP_Z, length=2.0, radius=TUBE_R, material=mats["frame"])
        _cyl_x(deck, name=f"lower_side_rail_{s}", x=0.0, y=y, z=SIDE_RAIL_LOW_Z, length=2.0, radius=0.014, material=mats["frame"])
        # Vertical struts tie the two side rails together (connectivity for all bases).
        for xs, sn in [(-0.60, "a"), (0.60, "b")]:
            _cyl_z(deck, name=f"rail_strut_{s}_{sn}", x=xs, y=y,
                   z=(SIDE_RAIL_LOW_Z + SIDE_RAIL_TOP_Z) / 2.0,
                   length=SIDE_RAIL_TOP_Z - SIDE_RAIL_LOW_Z, radius=0.012, material=mats["frame"])

    # Cross rails ONLY under the fixed hip-deck region (never under a moving deck
    # section, so a folding/dropping section never sweeps a fixed cross tube). The
    # hip_foot rail (at the fixed deck's foot edge) is raised so the deck panel
    # rests on it; head/backrest rails tie the two side rails together.
    for x, s, z in [(HEAD_X, "head", 0.560), (BACKREST_HINGE_X, "backrest_hinge", 0.560),
                    (plan["hip_end"], "hip_foot", 0.578)]:
        _cyl_y(deck, name=f"{s}_cross_rail", x=x, y=0.0, z=z, length=0.94, radius=TUBE_R, material=mats["frame"])

    # Fixed hip deck panel + hip mattress. The narrow deck panel rests on the
    # raised hip_foot cross rail (keeps the deck+mattress joined to the tube frame).
    hip_center = (plan["hip_start"] + plan["hip_end"]) / 2.0
    hip_len = plan["hip_end"] - plan["hip_start"]
    deck.visual(Box((hip_len, 0.86, 0.030)), origin=_origin(hip_center, 0.0, DECK_TOP_Z - 0.015), material=mats["deck"], name="hip_deck", material_class_id="metal.paint_coated")
    deck.visual(
        _cushion_mesh(name="hip_mattress", center_x=hip_center, length=hip_len - 0.04, width=0.82,
                      z_min=DECK_TOP_Z - 0.002, z_max=(DECK_TOP_Z - 0.002) + 0.077 * thick,
                      edge_taper=0.050, softness=0.024),
        origin=Origin(), material=mats["fabric"], name="hip_mattress", material_class_id="fabric.upholstery_plain",
    )

    # Backrest hinge barrels (outboard Y so they clear the child hinge tube).
    for y, s in [(-BARREL_Y, "0"), (BARREL_Y, "1")]:
        _cyl_y(deck, name=f"backrest_hinge_barrel_{s}", x=BACKREST_HINGE_X, y=y, z=DECK_TOP_Z, length=0.12, radius=0.018, material=mats["frame"])
    # Foot-side hinge barrels (N>=2).
    if plan["foot_hinge"] is not None:
        for y, s in [(-BARREL_Y, "0"), (BARREL_Y, "1")]:
            _cyl_y(deck, name=f"foot_hinge_barrel_{s}", x=plan["foot_hinge"], y=y, z=DECK_TOP_Z, length=0.12, radius=0.018, material=mats["frame"])


# ---------------------------------------------------------------------------
# Base module factories. Each emits the root part(s) grounded on the floor and
# returns (root_part, deck_part). deck_part carries the deck frame / sections /
# boards / rails.
# ---------------------------------------------------------------------------
def _build_base_caster(model, r, mats):
    base = model.part("base_frame")
    for x in (-CORNER_X, CORNER_X):
        for y in (-RAIL_Y, RAIL_Y):
            i = f"{'m' if x < 0 else 'p'}{'m' if y < 0 else 'p'}"
            # Corner leg post floor(caster top) -> deck (connects caster to frame).
            _cyl_z(base, name=f"corner_leg_{i}", x=x, y=y, z=(0.135 + SIDE_RAIL_TOP_Z) / 2.0,
                   length=SIDE_RAIL_TOP_Z - 0.135, radius=0.022, material=mats["frame"])
            _add_caster(base, prefix=f"caster_{i}", x=x, y=y, mats=mats)
    return base, base


def _build_base_four_leg(model, r, mats):
    base = model.part("base_frame")
    for x in (-0.80, 0.80):
        for y in (-RAIL_Y, RAIL_Y):
            i = f"{'m' if x < 0 else 'p'}{'m' if y < 0 else 'p'}"
            base.visual(Box((0.050, 0.050, 0.575)), origin=_origin(x, y, 0.03 + 0.575 / 2.0), material=mats["frame"], name=f"leg_{i}", material_class_id="metal.paint_coated")
            base.visual(Box((0.090, 0.090, 0.030)), origin=_origin(x, y, 0.015), material=mats["metal"], name=f"foot_pad_{i}", material_class_id="metal.brushed_silver")
    return base, base


def _build_base_hi_lo(model, r, mats):
    base = model.part("base")
    _cyl_z(base, name="hub_plate", x=0.0, y=0.0, z=0.090, length=0.050, radius=0.072, material=mats["column"])
    arm_len = 0.50
    for i, (dx, dy) in enumerate([(1, 0), (-1, 0), (0, 1), (0, -1)]):
        cx, cy = dx * arm_len / 2.0, dy * arm_len / 2.0
        size = (arm_len, 0.060, 0.045) if dx != 0 else (0.060, arm_len, 0.045)
        base.visual(Box(size), origin=_origin(cx, cy, 0.090), material=mats["frame"], name=f"cruciform_arm_{i}", material_class_id="metal.paint_coated")
    for cx, cy, pfx in [(arm_len, 0.0, "caster_0"), (-arm_len, 0.0, "caster_1"),
                        (0.0, arm_len, "caster_2"), (0.0, -arm_len, "caster_3")]:
        _add_caster(base, prefix=pfx, x=cx, y=cy, mats=mats)
    _cyl_z(base, name="outer_column", x=0.0, y=0.0, z=0.325, length=0.47, radius=0.050, material=mats["column"])

    lift = model.part("lift_column")
    _cyl_z(lift, name="inner_column", x=0.0, y=0.0, z=0.350, length=0.46, radius=0.040, material=mats["column"])
    lift.visual(Box((0.32, 0.94, 0.012)), origin=_origin(0.0, 0.0, 0.575), material=mats["column"], name="carriage_plate", material_class_id="metal.paint_coated")

    model.articulation(
        "column_to_deck", ArticulationType.PRISMATIC, parent=base, child=lift,
        origin=_origin(0.0, 0.0, 0.0), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=200.0, velocity=0.05, lower=0.0, upper=LIFT_UPPER),
    )
    return base, lift


_BASE_BUILDERS = {
    "caster_base": _build_base_caster,
    "four_leg_couch": _build_base_four_leg,
    "hi_lo_column": _build_base_hi_lo,
}


# ---------------------------------------------------------------------------
# Board module factories (deck-part visuals, Rule 1). Head + foot at x=+-1.0.
# ---------------------------------------------------------------------------
def _board_posts(deck, mats):
    for x in (-CORNER_X, CORNER_X):
        end = "head" if x < 0 else "foot"
        for y in (-RAIL_Y, RAIL_Y):
            s = "0" if y < 0 else "1"
            _cyl_z(deck, name=f"{end}_post_{s}", x=x, y=y, z=(0.58 + 1.16) / 2.0,
                   length=1.16 - 0.58, radius=0.022, material=mats["frame"])


def _build_boards_tubular(deck, r, mats):
    _board_posts(deck, mats)
    for x in (-CORNER_X, CORNER_X):
        end = "head" if x < 0 else "foot"
        for z, bar in [(1.13, "top"), (0.92, "middle"), (0.72, "lower")]:
            _cyl_y(deck, name=f"{end}_{bar}_bar", x=x, y=0.0, z=z, length=0.94,
                   radius=0.020 if bar == "top" else 0.016, material=mats["frame"])


def _build_boards_panel(deck, r, mats):
    _board_posts(deck, mats)
    for x in (-CORNER_X, CORNER_X):
        end = "head" if x < 0 else "foot"
        deck.visual(
            _molded_panel_mesh(name=f"{end}_panel", span_z=0.43, span_y=0.92, thickness=0.018, corner_radius=0.035),
            origin=_origin(x, 0.0, 0.925), material=mats["panel"], name=f"{end}_panel", material_class_id="plastic.opaque_glossy_molded",
        )


def _build_boards_open(deck, r, mats):
    return None  # open exam couch: no end boards


_BOARD_BUILDERS = {
    "tubular_rail_boards": _build_boards_tubular,
    "solid_panel_boards": _build_boards_panel,
    "open_no_board": _build_boards_open,
}


# ---------------------------------------------------------------------------
# Deck section helpers (Slot A). Every section: deck Box + mattress mesh +
# proximal hinge tube/side-tubes/leaves. S3 L327-425 / S4 L385-560.
# ---------------------------------------------------------------------------
def _section_hinge_hardware(part, mats, *, x_local, leaf_x):
    _cyl_y(part, name=f"{part.name}_hinge_tube", x=x_local, y=0.0, z=0.0, length=0.44, radius=0.018, material=mats["frame"])
    for y, s in [(-0.365, "0"), (0.365, "1")]:
        _cyl_y(part, name=f"{part.name}_side_tube_{s}", x=x_local, y=y, z=0.0, length=0.13, radius=0.018, material=mats["frame"])
    for y, s in [(-0.34, "0"), (0.34, "1")]:
        part.visual(Box((0.070, 0.045, 0.018)), origin=_origin(leaf_x, y, -0.006), material=mats["frame"], name=f"{part.name}_leaf_{s}", material_class_id="metal.paint_coated")


def _build_backrest(model, deck, r, mats):
    thick = r.mattress_thickness_scale
    back = model.part("backrest")
    back.visual(Box((0.63, 0.86, 0.030)), origin=_origin(-0.315, 0.0, -0.015), material=mats["deck"], name="back_deck", material_class_id="metal.paint_coated")
    back.visual(
        _cushion_mesh(name="back_mattress", center_x=-0.32, length=0.60, width=0.82,
                      z_min=0.0, z_max=0.078 * thick, edge_taper=0.040, softness=0.023),
        origin=Origin(), material=mats["fabric"], name="back_mattress", material_class_id="fabric.upholstery_plain")
    back.visual(
        _cushion_mesh(name="pillow", center_x=-0.40, length=0.42, width=0.66,
                      z_min=0.055, z_max=0.055 + 0.130 * thick, edge_taper=0.080, softness=0.055),
        origin=Origin(), material=mats["fabric"], name="pillow", material_class_id="fabric.upholstery_plain")
    _section_hinge_hardware(back, mats, x_local=0.0, leaf_x=-0.025)
    upper = BACKREST_UPPER * r.backrest_range_scale
    model.articulation(
        "deck_to_backrest", ArticulationType.REVOLUTE, parent=deck, child=back,
        origin=_origin(BACKREST_HINGE_X, 0.0, DECK_TOP_Z), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.8, lower=0.0, upper=upper))
    return back


def _build_foot_section(model, deck, r, mats, *, name, hinge_x, seg_len):
    """A single foot-side section hinging off the deck (knee / thigh)."""
    thick = r.mattress_thickness_scale
    part = model.part(name)
    part.visual(Box((seg_len, 0.86, 0.030)), origin=_origin(seg_len / 2.0, 0.0, -0.015), material=mats["deck"], name=f"{name}_deck", material_class_id="metal.paint_coated")
    part.visual(
        _cushion_mesh(name=f"{name}_mattress", center_x=seg_len / 2.0, length=seg_len - 0.06, width=0.82,
                      z_min=-0.002, z_max=-0.002 + 0.077 * thick, edge_taper=0.045, softness=0.022),
        origin=Origin(), material=mats["fabric"], name=f"{name}_mattress", material_class_id="fabric.upholstery_plain")
    _section_hinge_hardware(part, mats, x_local=0.0, leaf_x=0.035)
    upper = SECTION_UPPER * r.backrest_range_scale
    model.articulation(
        f"deck_to_{name}", ArticulationType.REVOLUTE, parent=deck, child=part,
        origin=_origin(hinge_x, 0.0, DECK_TOP_Z), axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.8, lower=0.0, upper=upper))
    return part


def _build_calf_section(model, thigh, r, mats, *, thigh_len, calf_len):
    """Calf chains off the thigh's distal end (raised-knee profiling). S4 L483-560."""
    thick = r.mattress_thickness_scale
    # Distal hinge barrels on the thigh (at its far end, local x=thigh_len). Kept
    # narrow / inboard (y=+-0.44) so a raised thigh clears the outboard side rails.
    for y, s in [(-0.44, "0"), (0.44, "1")]:
        _cyl_y(thigh, name=f"calf_hinge_barrel_{s}", x=thigh_len, y=y, z=0.0, length=0.10, radius=0.018, material=mats["frame"])
    calf = model.part("calf_section")
    calf.visual(Box((calf_len, 0.86, 0.030)), origin=_origin(calf_len / 2.0, 0.0, -0.015), material=mats["deck"], name="calf_deck", material_class_id="metal.paint_coated")
    calf.visual(
        _cushion_mesh(name="calf_mattress", center_x=calf_len / 2.0, length=calf_len - 0.04, width=0.82,
                      z_min=-0.002, z_max=-0.002 + 0.077 * thick, edge_taper=0.040, softness=0.022),
        origin=Origin(), material=mats["fabric"], name="calf_mattress", material_class_id="fabric.upholstery_plain")
    _section_hinge_hardware(calf, mats, x_local=0.0, leaf_x=0.035)
    upper = CALF_UPPER * r.backrest_range_scale
    model.articulation(
        "thigh_to_calf", ArticulationType.REVOLUTE, parent=thigh, child=calf,
        origin=_origin(thigh_len, 0.0, 0.0), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.8, lower=CALF_LOWER, upper=upper))
    return calf


def _build_deck_sections(model, deck, r, mats) -> list:
    """Backrest (always) + foot-side sections per N. Returns list of section parts."""
    parts = [_build_backrest(model, deck, r, mats)]
    n = r.section_count
    if n == 2:
        parts.append(_build_foot_section(model, deck, r, mats, name="knee_section", hinge_x=0.30, seg_len=0.96 - 0.30))
    elif n == 3:
        thigh_len = 0.45
        thigh = _build_foot_section(model, deck, r, mats, name="thigh_section", hinge_x=0.10, seg_len=thigh_len)
        parts.append(thigh)
        parts.append(_build_calf_section(model, thigh, r, mats, thigh_len=thigh_len, calf_len=0.42))
    return parts


# ---------------------------------------------------------------------------
# Side-rail module (Slot D). Two drop-down REVOLUTE guards. S5 L334-400.
# ---------------------------------------------------------------------------
# Deck-side rail-mount x positions: clear of struts (+-0.60), the backrest-hinge
# cross rail (-0.333), and every hip_foot cross rail (0.078 / 0.278 / 0.98).
_RAIL_MOUNT_XS = (-0.15, 0.45)


def _build_side_rails(model, deck, r, mats) -> list:
    rail_len = 1.50
    guard_h = 0.30
    parts = []
    for side_name, y_sign, axis_vec in [("left", -1.0, (1.0, 0.0, 0.0)), ("right", 1.0, (-1.0, 0.0, 0.0))]:
        # Outboard mount stubs on the deck side: bridge the deck side rail out to
        # the rail pivot; the rail pivot_tube rests on these (captured pivot).
        for i, mx in enumerate(_RAIL_MOUNT_XS):
            deck.visual(Box((0.050, 0.090, 0.035)), origin=_origin(mx, y_sign * 0.485, 0.585),
                        material=mats["metal"], name=f"rail_mount_{side_name}_{i}", material_class_id="metal.brushed_silver")
        rail = model.part(f"side_rail_{side_name}")
        _cyl_x(rail, name="guard_bar", x=0.0, y=0.0, z=guard_h, length=rail_len, radius=0.014, material=mats["frame"])
        _cyl_x(rail, name="mid_bar", x=0.0, y=0.0, z=guard_h * 0.5, length=rail_len, radius=0.012, material=mats["frame"])
        _cyl_x(rail, name="pivot_tube", x=0.0, y=0.0, z=0.0, length=rail_len, radius=0.012, material=mats["frame"])
        for i, sx in enumerate((-0.60, -0.20, 0.20, 0.60)):
            _cyl_z(rail, name=f"stanchion_{i}", x=sx, y=0.0, z=guard_h / 2.0, length=guard_h, radius=0.012, material=mats["frame"])
        model.articulation(
            f"deck_to_side_rail_{side_name}", ArticulationType.REVOLUTE, parent=deck, child=rail,
            origin=_origin(0.0, y_sign * 0.53, 0.59), axis=axis_vec,
            motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=0.0, upper=RAIL_UPPER))
        parts.append((rail, side_name, y_sign))
    return parts


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_hospital_bed(config: HospitalBedConfig | None = None, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"hbed_{key}_{r.palette_style}", rgba=(*rgb, 1.0))
        for key, rgb in PALETTES[r.palette_style].items()
    }

    root, deck = _BASE_BUILDERS[r.base](model, r, mats)
    _deck_frame(deck, r, mats)
    _BOARD_BUILDERS[r.boards](deck, r, mats)
    _build_deck_sections(model, deck, r, mats)
    if r.side_rails == "dropdown_side_rails":
        _build_side_rails(model, deck, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_hospital_bed(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_hospital_bed(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_hospital_bed_tests(object_model: ArticulatedObject, config: HospitalBedConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    deck_name = "lift_column" if r.base == "hi_lo_column" else "base_frame"
    deck = object_model.get_part(deck_name)

    # ---- Element-scoped structural allowances. ----
    if r.base == "hi_lo_column":
        base = object_model.get_part("base")
        ctx.allow_overlap(base, deck, elem_a="outer_column", elem_b="inner_column",
                          reason="Inner telescoping column nests inside the outer column housing (captured slide).")

    # Section hinge hardware sits on the deck hinge line -> local overlap with the
    # deck barrels / hip deck edge (captured-pin hinge seam).
    section_names = [p for p in ("backrest", "knee_section", "thigh_section", "calf_section") if p in part_names]
    for sn in section_names:
        sect = object_model.get_part(sn)
        for hw in (f"{sn}_hinge_tube", f"{sn}_side_tube_0", f"{sn}_side_tube_1"):
            for db in ("backrest_hinge_barrel_0", "backrest_hinge_barrel_1",
                       "foot_hinge_barrel_0", "foot_hinge_barrel_1", "hip_deck", "hip_mattress"):
                ctx.allow_overlap(sect, deck, elem_a=hw, elem_b=db,
                                  reason="Section hinge hardware meets the deck hinge barrels / hip-deck edge at the seam.")
    # calf chains off thigh: its proximal hinge tube meets the thigh distal barrels/deck.
    if "calf_section" in part_names and "thigh_section" in part_names:
        thigh = object_model.get_part("thigh_section")
        calf = object_model.get_part("calf_section")
        for hw in ("calf_section_hinge_tube", "calf_section_side_tube_0", "calf_section_side_tube_1"):
            for tb in ("calf_hinge_barrel_0", "calf_hinge_barrel_1", "thigh_section_deck", "thigh_section_mattress"):
                ctx.allow_overlap(calf, thigh, elem_a=hw, elem_b=tb,
                                  reason="Calf proximal hinge hardware meets the thigh distal barrels at the knee hinge.")

    # Side-rail pivot tube is captured on the deck-side rail-mount stubs.
    if r.side_rails == "dropdown_side_rails":
        for side_name in ("left", "right"):
            rail = object_model.get_part(f"side_rail_{side_name}")
            for i in range(2):
                ctx.allow_overlap(rail, deck, elem_a="pivot_tube", elem_b=f"rail_mount_{side_name}_{i}",
                                  reason="Drop-down side-rail pivot tube is captured on the deck rail-mount stub.")

    # Adjacent chained calf<->thigh deck panels sweep past each other at the knee
    # knuckle (hinged panels sharing one hinge line) -> element-scoped seam allowance.
    if "calf_section" in part_names and "thigh_section" in part_names:
        thigh = object_model.get_part("thigh_section")
        calf = object_model.get_part("calf_section")
        for ca in ("calf_deck", "calf_mattress", "calf_section_leaf_0", "calf_section_leaf_1"):
            for tb in ("thigh_section_deck", "thigh_section_mattress", "calf_hinge_barrel_0", "calf_hinge_barrel_1"):
                ctx.allow_overlap(calf, thigh, elem_a=ca, elem_b=tb,
                                  reason="Chained calf and thigh deck panels / knuckle barrels meet at the shared knee hinge.")

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure. ----
    ctx.check("backrest section present", "backrest" in part_names, details=str(sorted(part_names)))
    bj = object_model.get_articulation("deck_to_backrest")
    ctx.check("backrest hinge is REVOLUTE", bj.articulation_type == ArticulationType.REVOLUTE, details=str(bj.articulation_type))
    ctx.check("backrest hinge axis is Y", abs(bj.axis[1]) > 0.9 and abs(bj.axis[0]) < 1e-6 and abs(bj.axis[2]) < 1e-6, details=str(tuple(bj.axis)))
    ctx.check("backrest raises head (lower=0)", bj.motion_limits is not None and abs(bj.motion_limits.lower) < 1e-6 and bj.motion_limits.upper > 0.5, details=str(bj.motion_limits))

    # section_count = 1 backrest + (N-1) foot-side sections.
    section_joints = [a for a in object_model.articulations if str(a.name).startswith("deck_to_") and "side_rail" not in str(a.name)]
    section_joints += [a for a in object_model.articulations if str(a.name) == "thigh_to_calf"]
    ctx.check("section joint count matches N", len(section_joints) == r.section_count, details=f"joints={len(section_joints)} N={r.section_count}")

    # base grounded on the floor.
    base_part = object_model.get_part("base") if r.base == "hi_lo_column" else deck
    base_aabb = ctx.part_world_aabb(base_part)
    ctx.check("base sits on the floor", base_aabb is not None and base_aabb[0][2] < 0.02, details=str(base_aabb))

    # hospital-bed scale of the deck.
    deck_aabb = ctx.part_world_aabb(deck)
    ctx.check(
        "deck has hospital-bed scale",
        deck_aabb is not None and 1.90 <= (deck_aabb[1][0] - deck_aabb[0][0]) <= 2.15
        and 0.85 <= (deck_aabb[1][1] - deck_aabb[0][1]) <= 1.12,
        details=str(deck_aabb),
    )

    # 4 casters present for wheeled bases.
    if r.base in ("caster_base", "hi_lo_column"):
        holder = object_model.get_part("base") if r.base == "hi_lo_column" else deck
        tires = [v for v in holder.visuals if v.name.endswith("_tire")]
        ctx.check("4 swivel casters present", len(tires) == 4, details=f"tires={len(tires)}")

    # hi-lo prismatic lift.
    if r.base == "hi_lo_column":
        lj = object_model.get_articulation("column_to_deck")
        ctx.check("hi-lo lift is PRISMATIC on Z", lj.articulation_type == ArticulationType.PRISMATIC and abs(lj.axis[2]) > 0.9, details=str((lj.articulation_type, tuple(lj.axis))))

    # ---- Dynamic motion semantics (Rule 5). ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    # Backrest raises the pillow upward.
    closed_pillow = ctx.part_element_world_aabb(object_model.get_part("backrest"), elem="pillow")
    with ctx.pose({bj: bj.motion_limits.upper}):
        raised_pillow = ctx.part_element_world_aabb(object_model.get_part("backrest"), elem="pillow")
        ctx.check("backrest raises pillow upward when posed",
                  closed_pillow is not None and raised_pillow is not None and raised_pillow[1][2] > closed_pillow[1][2] + 0.25,
                  details=f"closed={closed_pillow}, raised={raised_pillow}")

    # Foot-side section raises the foot upward (N>=2).
    if r.section_count >= 2:
        foot_name = "knee_section" if r.section_count == 2 else "thigh_section"
        fj = object_model.get_articulation(f"deck_to_{foot_name}")
        rest = ctx.part_element_world_aabb(object_model.get_part(foot_name), elem=f"{foot_name}_deck")
        with ctx.pose({fj: fj.motion_limits.upper}):
            up = ctx.part_element_world_aabb(object_model.get_part(foot_name), elem=f"{foot_name}_deck")
            ctx.check("foot-side section raises foot end upward",
                      rest is not None and up is not None and up[1][2] > rest[1][2] + 0.08,
                      details=f"rest={rest}, up={up}")

    # Calf drops the foot end downward relative to the thigh (N=3).
    if r.section_count == 3:
        cj = object_model.get_articulation("thigh_to_calf")
        rest = ctx.part_element_world_aabb(object_model.get_part("calf_section"), elem="calf_deck")
        with ctx.pose({cj: cj.motion_limits.upper}):
            dropped = ctx.part_element_world_aabb(object_model.get_part("calf_section"), elem="calf_deck")
            ctx.check("calf section drops foot end downward",
                      rest is not None and dropped is not None and dropped[0][2] < rest[0][2] - 0.03,
                      details=f"rest={rest}, dropped={dropped}")

    # Hi-lo prismatic raises the whole deck.
    if r.base == "hi_lo_column":
        lj = object_model.get_articulation("column_to_deck")
        rest = ctx.part_element_world_aabb(deck, elem="hip_deck")
        with ctx.pose({lj: lj.motion_limits.upper}):
            raised = ctx.part_element_world_aabb(deck, elem="hip_deck")
            ctx.check("hi-lo lift raises the deck", rest is not None and raised is not None and raised[0][2] > rest[0][2] + 0.15,
                      details=f"rest={rest}, raised={raised}")

    # Side rail drops down when articulated.
    if r.side_rails == "dropdown_side_rails":
        rail = object_model.get_part("side_rail_left")
        rj = object_model.get_articulation("deck_to_side_rail_left")
        up = ctx.part_element_world_aabb(rail, elem="guard_bar")
        with ctx.pose({rj: rj.motion_limits.upper}):
            down = ctx.part_element_world_aabb(rail, elem="guard_bar")
            ctx.check("side rail guard drops down when articulated",
                      up is not None and down is not None and down[1][2] < up[0][2],
                      details=f"up={up}, down={down}")

    # slot_choices recorded.
    ctx.check("slot_choices recorded", tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
              details=str(object_model.meta.get("slot_choices")))

    return ctx.report()


__all__ = (
    "HospitalBedConfig",
    "ResolvedHospitalBedConfig",
    "build_hospital_bed",
    "build_seeded_hospital_bed",
    "config_from_seed",
    "resolve_config",
    "run_hospital_bed_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
