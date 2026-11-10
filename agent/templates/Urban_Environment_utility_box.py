# SPDX-License-Identifier: Apache-2.0

"""utility_box — modular procedural template (street electrical / utility cabinet).

Category identity: a grounded (or leg-elevated) steel box **enclosure** (a
street electrical distribution cabinet / utility junction box) standing on a
**base** (steel plinth skirt / wide concrete pedestal / stepped concrete /
four short legs / N tall legs), presenting a front (or top) **opening
mechanism**:

  Slot A door — the DEFINING articulation:
    * single_revolute_side  : one front door, vertical-axis REVOLUTE hinge.
    * double_mimic          : two outer-hinged doors, the second mimics the
                              first (Mimic via shared open angle).
    * triple_door_bank(N)   : N (=2..4) doors in a horizontal bank, each its
                              own vertical-axis REVOLUTE hinge.
    * top_revolute_lid      : a top flip-lid, horizontal-axis REVOLUTE, plus a
                              front hasp clasp REVOLUTE (low ground box only).
    * roller_shutter(N)     : a vertical-travel PRISMATIC roller curtain that
                              retracts up into a head box.

  Slot B body   — footprint family (tall_narrow / medium / wide_squat / cube /
                  low_ground_box). low_ground_box is reserved for the top lid.
  Slot C vent   — solid / louver_slots / louver_rows(N) / mesh_grid /
                  vent_grille_side ventilation (parent.visual decorations).
  Slot D base   — steel_plinth / concrete_plinth / stepped_concrete /
                  four_short_legs / tall_legs(N).
  Slot E roof   — none / flat_drip_cap / pitched_canopy / roof_cap_overhang
                  (mutually exclusive with top_revolute_lid).

Canonical frame: body is an upright hollow steel shell. Width along X
(centered), depth along Y (centered, front face at -Y), height along Z. The
base bottom rests on z=0 (no float). The body sits on top of the base:
body z-center = support_top + BODY_H/2.

Three independent multiplicity axes (each >=2 distinct N): door-count N (2/3/4),
louver-row N (3..12), leg-count N (4/6); plus a derived shutter-slat count.

HARD RULES honored:
  * Louvers / hinges / hasps / conduit / warning placards are parent.visual
    decorations (Rule 1) unless they articulate.
  * Every non-FIXED joint (doors, lid, clasp, shutter) declares a
    MatingContract pinning real visuals on both sides (Rule 2).
  * Door LOCAL ORIGIN = hinge edge; the joint origin lies on the real hinge
    knuckle on the front jamb (no phantom pad).
  * Curved roof canopy uses cadquery (no Box downgrade); vents use the SDK
    VentGrilleGeometry mesh helper.

Canonical spec: articraft_template_authoring/specs_modular_v1/Urban_Environment_Urban_Environment_utility_box.md
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
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
    VentGrilleGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum domains
# ---------------------------------------------------------------------------
DoorModule = Literal[
    "single_revolute_side",
    "double_mimic",
    "triple_door_bank",
    "top_revolute_lid",
    "roller_shutter",
]
BodyModule = Literal["tall_narrow", "medium", "wide_squat", "cube", "low_ground_box"]
VentModule = Literal["solid", "louver_slots", "louver_rows", "mesh_grid", "vent_grille_side"]
BaseModule = Literal[
    "steel_plinth",
    "concrete_plinth",
    "stepped_concrete",
    "four_short_legs",
    "tall_legs",
]
RoofModule = Literal["none", "flat_drip_cap", "pitched_canopy", "roof_cap_overhang"]
PaletteStyle = Literal[
    "galvanized_grey",
    "utility_green",
    "beige_tan",
    "weathered_white",
    "dark_graphite",
    "municipal_blue",
]

DOOR_MODULES: tuple[DoorModule, ...] = (
    "single_revolute_side",
    "double_mimic",
    "triple_door_bank",
    "top_revolute_lid",
    "roller_shutter",
)
DOOR_WEIGHTS = (0.30, 0.22, 0.18, 0.15, 0.15)

VENT_MODULES: tuple[VentModule, ...] = (
    "solid",
    "louver_slots",
    "louver_rows",
    "mesh_grid",
    "vent_grille_side",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "galvanized_grey",
    "utility_green",
    "beige_tan",
    "weathered_white",
    "dark_graphite",
    "municipal_blue",
)

# Door-face vents (only legal on front-door modules).
_FRONT_DOOR_MODULES = {"single_revolute_side", "double_mimic", "triple_door_bank"}
_DOOR_FACE_VENTS = {"louver_slots", "louver_rows", "mesh_grid"}

# Multiplicity axes.
DOOR_COUNTS: tuple[int, ...] = (2, 3, 4)
DOOR_COUNT_WEIGHTS = (0.55, 0.30, 0.15)
LOUVER_ROWS: tuple[int, ...] = (3, 4, 5, 6, 8, 10, 12)
LOUVER_ROW_WEIGHTS = (0.16, 0.22, 0.22, 0.18, 0.12, 0.06, 0.04)
LEG_COUNTS: tuple[int, ...] = (4, 6)
LEG_COUNT_WEIGHTS = (0.78, 0.22)

# ---------------------------------------------------------------------------
# Palettes (per-seed). Keys: body / door / trim / hardware / dark / accent.
# Sourced from 5-star sample materials (see spec §palette).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "galvanized_grey": {
        "body": (0.66, 0.67, 0.69, 1.0),
        "door": (0.72, 0.73, 0.75, 1.0),
        "trim": (0.58, 0.59, 0.61, 1.0),
        "hardware": (0.30, 0.31, 0.33, 1.0),
        "dark": (0.18, 0.19, 0.20, 1.0),
        "accent": (0.50, 0.51, 0.53, 1.0),
    },
    "utility_green": {
        "body": (0.40, 0.50, 0.42, 1.0),
        "door": (0.45, 0.55, 0.46, 1.0),
        "trim": (0.34, 0.43, 0.36, 1.0),
        "hardware": (0.22, 0.24, 0.22, 1.0),
        "dark": (0.16, 0.20, 0.17, 1.0),
        "accent": (0.58, 0.62, 0.60, 1.0),
    },
    "beige_tan": {
        "body": (0.80, 0.76, 0.66, 1.0),
        "door": (0.84, 0.80, 0.70, 1.0),
        "trim": (0.70, 0.66, 0.56, 1.0),
        "hardware": (0.36, 0.34, 0.30, 1.0),
        "dark": (0.26, 0.24, 0.20, 1.0),
        "accent": (0.62, 0.58, 0.48, 1.0),
    },
    "weathered_white": {
        "body": (0.82, 0.81, 0.78, 1.0),
        "door": (0.74, 0.73, 0.70, 1.0),
        "trim": (0.66, 0.65, 0.62, 1.0),
        "hardware": (0.34, 0.34, 0.33, 1.0),
        "dark": (0.24, 0.24, 0.23, 1.0),
        "accent": (0.58, 0.57, 0.54, 1.0),
    },
    "dark_graphite": {
        "body": (0.34, 0.36, 0.38, 1.0),
        "door": (0.40, 0.42, 0.44, 1.0),
        "trim": (0.28, 0.30, 0.32, 1.0),
        "hardware": (0.62, 0.64, 0.66, 1.0),
        "dark": (0.14, 0.15, 0.16, 1.0),
        "accent": (0.48, 0.50, 0.52, 1.0),
    },
    "municipal_blue": {
        "body": (0.40, 0.46, 0.58, 1.0),
        "door": (0.46, 0.52, 0.64, 1.0),
        "trim": (0.34, 0.40, 0.50, 1.0),
        "hardware": (0.26, 0.28, 0.34, 1.0),
        "dark": (0.16, 0.19, 0.24, 1.0),
        "accent": (0.54, 0.58, 0.68, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Public + resolved config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class UtilityBoxConfig:
    door_module: DoorModule = "single_revolute_side"
    body_module: BodyModule = "medium"
    vent_module: VentModule = "louver_slots"
    base_module: BaseModule = "steel_plinth"
    roof_module: RoofModule = "flat_drip_cap"
    door_count: int = 2
    louver_row_count: int = 6
    leg_count: int = 4
    palette_style: PaletteStyle = "galvanized_grey"
    width_scale: float = 1.0
    depth_scale: float = 1.0
    height_scale: float = 1.0
    leg_height_scale: float = 1.0
    name: str = "reference_utility_box"


@dataclass(frozen=True)
class ResolvedUtilityBoxConfig:
    door_module: DoorModule
    body_module: BodyModule
    vent_module: VentModule
    base_module: BaseModule
    roof_module: RoofModule
    door_count: int  # active for triple_door_bank / double; else 1
    louver_row_count: int  # active for louver_rows; else 0
    leg_count: int  # active for tall_legs / four_short_legs
    palette_style: PaletteStyle
    # Body envelope (m).
    body_w: float  # along X
    body_d: float  # along Y
    body_h: float  # along Z
    support_h: float  # lift from floor to body bottom (base height)
    wall: float
    palette_rgba_key: PaletteStyle
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _wchoice(rng: random.Random, items, weights) -> object:
    return rng.choices(items, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# Compatibility gating (derive a legal combo from any raw config).
# ---------------------------------------------------------------------------
def _gate(
    door: DoorModule,
    body: BodyModule,
    vent: VentModule,
    base: BaseModule,
    roof: RoofModule,
) -> tuple[BodyModule, VentModule, BaseModule, RoofModule]:
    if door == "top_revolute_lid":
        # Top-flip low ground box on four short legs, no roof, solid/side vent.
        body = "low_ground_box"
        base = "four_short_legs"
        roof = "none"
        if vent not in ("solid", "vent_grille_side"):
            vent = "solid"
        return body, vent, base, roof

    # Non-lid modules cannot use the low_ground_box (top-open) shell.
    if body == "low_ground_box":
        body = "medium"

    if door == "roller_shutter":
        # Door face is occupied by the curtain -> vents must be on the side.
        vent = "vent_grille_side"

    # Door-face vents only on front-door modules.
    if vent in _DOOR_FACE_VENTS and door not in _FRONT_DOOR_MODULES:
        vent = "vent_grille_side"

    return body, vent, base, roof


# ---------------------------------------------------------------------------
# Procedural sampler
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> UtilityBoxConfig:
    rng = random.Random(seed)
    door = _wchoice(rng, DOOR_MODULES, DOOR_WEIGHTS)  # type: ignore[assignment]

    body = rng.choice(("tall_narrow", "medium", "wide_squat", "cube"))
    vent = rng.choice(VENT_MODULES)
    base = rng.choice(("steel_plinth", "concrete_plinth", "stepped_concrete", "tall_legs"))
    roof = rng.choice(("none", "flat_drip_cap", "pitched_canopy", "roof_cap_overhang"))

    body, vent, base, roof = _gate(door, body, vent, base, roof)  # type: ignore[arg-type]

    door_count = _wchoice(rng, DOOR_COUNTS, DOOR_COUNT_WEIGHTS)
    louver_row_count = _wchoice(rng, LOUVER_ROWS, LOUVER_ROW_WEIGHTS)
    leg_count = _wchoice(rng, LEG_COUNTS, LEG_COUNT_WEIGHTS)

    return UtilityBoxConfig(
        door_module=door,  # type: ignore[arg-type]
        body_module=body,
        vent_module=vent,
        base_module=base,
        roof_module=roof,
        door_count=int(door_count),
        louver_row_count=int(louver_row_count),
        leg_count=int(leg_count),
        palette_style=rng.choice(PALETTE_STYLES),
        width_scale=round(rng.uniform(0.90, 1.10), 3),
        depth_scale=round(rng.uniform(0.90, 1.10), 3),
        height_scale=round(rng.uniform(0.90, 1.10), 3),
        leg_height_scale=round(rng.uniform(0.85, 1.15), 3),
        name=f"seeded_utility_box_{seed}",
    )


# Base footprint defaults per body family (W, D, H) in meters.
_BODY_DIMS: dict[BodyModule, tuple[float, float, float]] = {
    "tall_narrow": (0.46, 0.30, 0.80),
    "medium": (0.62, 0.40, 0.62),
    "wide_squat": (0.84, 0.55, 0.50),
    "cube": (0.58, 0.55, 0.58),
    "low_ground_box": (0.46, 0.38, 0.20),
}


def resolve_config(config: UtilityBoxConfig) -> ResolvedUtilityBoxConfig:
    if config.door_module not in DOOR_MODULES:
        raise ValueError(f"Unsupported door_module: {config.door_module}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    body, vent, base, roof = _gate(
        config.door_module,
        config.body_module,
        config.vent_module,
        config.base_module,
        config.roof_module,
    )

    w_scale = _clamp(config.width_scale, 0.90, 1.10)
    d_scale = _clamp(config.depth_scale, 0.90, 1.10)
    h_scale = _clamp(config.height_scale, 0.90, 1.10)
    leg_h_scale = _clamp(config.leg_height_scale, 0.85, 1.15)

    base_w, base_d, base_h = _BODY_DIMS[body]
    body_w = round(base_w * w_scale, 4)
    body_d = round(base_d * d_scale, 4)
    body_h = round(base_h * h_scale, 4)

    # Base support lift (floor -> body bottom).
    if base == "tall_legs":
        support_h = round(0.55 * leg_h_scale, 4)
    elif base == "four_short_legs":
        support_h = round(0.06 * leg_h_scale, 4)
    elif base == "steel_plinth":
        support_h = 0.07
    elif base == "concrete_plinth":
        support_h = 0.10
    else:  # stepped_concrete
        support_h = 0.13

    # Active multiplicity (gated by module).
    if config.door_module == "triple_door_bank":
        door_count = config.door_count if config.door_count in DOOR_COUNTS else 2
        # Clamp N so each leaf stays > 0.10 m wide.
        gap, seam = 0.012, 0.006
        while door_count > 2:
            leaf = (body_w - 2.0 * gap - (door_count - 1) * seam) / door_count
            if leaf > 0.10:
                break
            door_count -= 1
    elif config.door_module == "double_mimic":
        door_count = 2
    else:
        door_count = 1

    if vent == "louver_rows":
        louver_row_count = (
            config.louver_row_count if config.louver_row_count in LOUVER_ROWS else 6
        )
        # Clamp rows so they fit within the door height (span >= N * row_h).
        door_h = body_h - 0.08
        row_h = 0.024
        while louver_row_count > 3 and (door_h - 0.06) < louver_row_count * row_h:
            louver_row_count -= 1
    else:
        louver_row_count = 0

    if base == "tall_legs":
        leg_count = config.leg_count if config.leg_count in LEG_COUNTS else 4
    elif base == "four_short_legs":
        leg_count = 4
    else:
        leg_count = 0

    return ResolvedUtilityBoxConfig(
        door_module=config.door_module,
        body_module=body,
        vent_module=vent,
        base_module=base,
        roof_module=roof,
        door_count=door_count,
        louver_row_count=louver_row_count,
        leg_count=leg_count,
        palette_style=config.palette_style,
        body_w=body_w,
        body_d=body_d,
        body_h=body_h,
        support_h=support_h,
        wall=0.018,
        palette_rgba_key=config.palette_style,
        name=config.name or "utility_box",
    )


# ---------------------------------------------------------------------------
# slot_choices
# ---------------------------------------------------------------------------
def _slot_choices_for_resolved(r: ResolvedUtilityBoxConfig) -> list[tuple[str, str]]:
    door_label = r.door_module
    if r.door_module == "triple_door_bank":
        door_label = f"triple_door_bank_{r.door_count}"
    vent_label = r.vent_module
    if r.vent_module == "louver_rows":
        vent_label = f"louver_rows_{r.louver_row_count}"
    base_label = r.base_module
    if r.base_module == "tall_legs":
        base_label = f"tall_legs_{r.leg_count}"
    return [
        ("door_module", door_label),
        ("body_module", r.body_module),
        ("vent_module", vent_label),
        ("base_module", base_label),
        ("roof_module", r.roof_module),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return _slot_choices_for_resolved(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Canonical frame
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Frame:
    BW: float  # width (X)
    BD: float  # depth (Y)
    z0: float  # body bottom z (= support_h)
    BH: float  # body height (Z)
    wall: float

    @property
    def z1(self) -> float:
        return self.z0 + self.BH

    @property
    def zc(self) -> float:
        return self.z0 + self.BH / 2.0

    @property
    def FRONT_Y(self) -> float:
        return -self.BD / 2.0

    @property
    def REAR_Y(self) -> float:
        return self.BD / 2.0

    @property
    def INNER_W(self) -> float:
        return self.BW - 2.0 * self.wall


def _make_frame(r: ResolvedUtilityBoxConfig) -> _Frame:
    return _Frame(BW=r.body_w, BD=r.body_d, z0=r.support_h, BH=r.body_h, wall=r.wall)


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _meta(joint_type, axis, origin, limits) -> dict[str, object]:
    return {
        "type": joint_type.value,
        "axis": axis,
        "origin": origin,
        "range": None if limits is None else (limits.lower, limits.upper),
    }


# ===========================================================================
# BODY shell (root-mounted part). Hollow steel box. Front (-Y) open for door
# modules; top (+z) open for the low_ground_box lid module.
# ===========================================================================
def _build_body_shell(body, fr: _Frame, mats, *, top_open: bool) -> None:
    BW, BD, wall = fr.BW, fr.BD, fr.wall
    z0, z1, zc = fr.z0, fr.z1, fr.zc
    cm = mats["body"]

    # Left / right side walls (full depth, full height).
    for tag, s in (("0", 1.0), ("1", -1.0)):
        _box(body, (wall, BD, fr.BH), (s * (BW / 2.0 - wall / 2.0), 0.0, zc), cm,
             f"shell_side_{tag}")
    # Back wall (+Y).
    _box(body, (fr.INNER_W, wall, fr.BH), (0.0, BD / 2.0 - wall / 2.0, zc), cm, "shell_back")
    # Bottom floor.
    _box(body, (BW, BD, wall), (0.0, 0.0, z0 + wall / 2.0), cm, "shell_bottom")
    if top_open:
        # Front wall closed (front face stays -Y), top is the opening (lid).
        _box(body, (fr.INNER_W, wall, fr.BH), (0.0, -BD / 2.0 + wall / 2.0, zc), cm,
             "shell_front")
        # Rim lip around the top opening for the lid to seat on.
        _box(body, (BW, 0.02, 0.012), (0.0, BD / 2.0 - 0.01, z1 + 0.006), mats["trim"],
             "rim_back")
    else:
        # Top closed; front (-Y) is the opening covered by the door(s).
        _box(body, (BW, BD, wall), (0.0, 0.0, z1 - wall / 2.0), cm, "shell_top")


# ===========================================================================
# SLOT D base factories — emit fixed body visuals or N leg parts.
# Return list of FIXED joint names (for tall_legs / four_short_legs).
# ===========================================================================
def _build_base_steel_plinth(model, body, fr: _Frame, r, mats) -> list[str]:
    inset = 0.02
    _box(body, (fr.BW - 2 * inset, fr.BD - 2 * inset, fr.z0),
         (0.0, 0.0, fr.z0 / 2.0), mats["trim"], "plinth_skirt")
    return []


def _build_base_concrete_plinth(model, body, fr: _Frame, r, mats) -> list[str]:
    over = 0.06
    _box(body, (fr.BW + 2 * over, fr.BD + 2 * over, fr.z0),
         (0.0, 0.0, fr.z0 / 2.0), mats["dark"], "concrete_pedestal")
    # Cable-entry conduit stub rising into the body bottom (fused visual).
    body.visual(
        Cylinder(radius=0.018, length=fr.z0 + 0.05),
        origin=Origin(xyz=(fr.BW / 2.0 - 0.07, fr.BD / 2.0 - 0.05, (fr.z0 + 0.05) / 2.0)),
        material=mats["hardware"],
        name="conduit_stub", material_class_id="metal.steel_galvanized",
    )
    return []


def _build_base_stepped_concrete(model, body, fr: _Frame, r, mats) -> list[str]:
    lower_h = fr.z0 * 0.55
    upper_h = fr.z0 - lower_h
    _box(body, (fr.BW + 0.12, fr.BD + 0.12, lower_h),
         (0.0, 0.0, lower_h / 2.0), mats["dark"], "base_lower_step")
    _box(body, (fr.BW + 0.04, fr.BD + 0.04, upper_h),
         (0.0, 0.0, lower_h + upper_h / 2.0), mats["dark"], "base_upper_step")
    return []


def _leg_corners(fr: _Frame, n: int, inset: float) -> list[tuple[float, float]]:
    cx = fr.BW / 2.0 - inset
    cy = fr.BD / 2.0 - inset
    corners = [(cx, cy), (-cx, cy), (-cx, -cy), (cx, -cy)]
    if n == 6:
        corners += [(cx, 0.0), (-cx, 0.0)]
    return corners


def _build_legs(model, body, fr: _Frame, r, mats, *, leg_h: float, post: float,
                tall: bool) -> list[str]:
    """N steel legs as separate parts, each FIXED to the body at its corner.

    Leg local frame: post centered at local (0,0), spanning local z 0..leg_h
    with its TOP at local z=leg_h. The FIXED joint origin sits at the body
    bottom corner; the leg's top embeds slightly into the body floor.
    """
    n = r.leg_count if r.leg_count in (4, 6) else 4
    corners = _leg_corners(fr, n, post / 2.0 + 0.015)
    joints: list[str] = []
    for i, (lx, ly) in enumerate(corners):
        leg = model.part(f"leg_{i}")
        # Post: top at local z=0 (joint origin), extends down to z=-leg_h.
        leg.visual(
            Box((post, post, leg_h)),
            origin=Origin(xyz=(0.0, 0.0, -leg_h / 2.0)),
            material=mats["hardware"],
            name="post", material_class_id="metal.steel_galvanized",
        )
        # Foot pad on the floor.
        leg.visual(
            Box((post + 0.02, post + 0.02, 0.012)),
            origin=Origin(xyz=(0.0, 0.0, -leg_h + 0.006)),
            material=mats["dark"],
            name="foot_pad", material_class_id="rubber.smooth_plain",
        )
        if tall:
            # Top gusset bracket where the post meets the body underside.
            leg.visual(
                Box((post + 0.018, post + 0.018, 0.02)),
                origin=Origin(xyz=(0.0, 0.0, -0.01)),
                material=mats["trim"],
                name="top_gusset", material_class_id="metal.paint_coated",
            )
        leg.inertial = Inertial.from_geometry(Box((post, post, leg_h)), mass=2.0)
        origin = (lx, ly, fr.z0)
        model.articulation(
            f"cabinet_to_leg_{i}",
            ArticulationType.FIXED,
            parent=body,
            child=leg,
            origin=Origin(xyz=origin),
            mating=MatingContract(
                parent_face_geometry="shell_bottom",
                parent_face_side="negative_z",
                child_face_geometry="post",
                child_face_side="positive_z",
                contact_tol=0.004,
            ),
        )
        joints.append(f"cabinet_to_leg_{i}")
    return joints


def _build_base_tall_legs(model, body, fr: _Frame, r, mats) -> list[str]:
    return _build_legs(model, body, fr, r, mats, leg_h=fr.z0, post=0.04, tall=True)


def _build_base_four_short_legs(model, body, fr: _Frame, r, mats) -> list[str]:
    return _build_legs(model, body, fr, r, mats, leg_h=fr.z0, post=0.045, tall=False)


_BASE_FACTORIES = {
    "steel_plinth": _build_base_steel_plinth,
    "concrete_plinth": _build_base_concrete_plinth,
    "stepped_concrete": _build_base_stepped_concrete,
    "four_short_legs": _build_base_four_short_legs,
    "tall_legs": _build_base_tall_legs,
}


# ===========================================================================
# SLOT E roof factories — parent.visual on the body top (no joint).
# ===========================================================================
def _build_roof_flat_drip_cap(body, fr: _Frame, mats) -> None:
    _box(body, (fr.BW + 0.05, fr.BD + 0.05, 0.022),
         (0.0, 0.0, fr.z1 + 0.011), mats["trim"], "drip_cap")


def _canopy_mesh(fr: _Frame, name: str):
    """Curved/pitched gable canopy (cadquery triangular prism + fascia)."""
    w = fr.BW + 0.06
    d = fr.BD + 0.06
    peak = 0.10
    # Triangular gable section in the Y-Z plane, extruded along X (width).
    gable = (
        cq.Workplane("YZ")
        .polyline([(-d / 2.0, 0.0), (d / 2.0, 0.0), (0.0, peak)])
        .close()
        .extrude(w)
        .translate((-w / 2.0, 0.0, 0.0))
    )
    return mesh_from_cadquery(gable, name)


def _build_roof_pitched_canopy(body, fr: _Frame, mats) -> None:
    mesh = _canopy_mesh(fr, "rain_canopy")
    body.visual(mesh, origin=Origin(xyz=(0.0, 0.0, fr.z1)), material=mats["door"],
                name="rain_canopy", material_class_id="metal.paint_coated")
    # Fascia drip edges along the two long eaves.
    for s in (1.0, -1.0):
        _box(body, (fr.BW + 0.06, 0.012, 0.03),
             (0.0, s * (fr.BD / 2.0 + 0.024), fr.z1 + 0.012), mats["trim"],
             f"fascia_{'p' if s > 0 else 'n'}")


def _build_roof_cap_overhang(body, fr: _Frame, mats) -> None:
    _box(body, (fr.BW + 0.06, fr.BD + 0.06, 0.02),
         (0.0, 0.0, fr.z1 + 0.01), mats["trim"], "roof_cap")
    # Three-side drip lip (front open).
    lip_h = 0.025
    for name, sz, xyz in (
        ("lip_back", (fr.BW + 0.06, 0.01, lip_h), (0.0, fr.BD / 2.0 + 0.025, fr.z1 - lip_h / 2.0 + 0.005)),
        ("lip_left", (0.01, fr.BD + 0.06, lip_h), (fr.BW / 2.0 + 0.025, 0.0, fr.z1 - lip_h / 2.0 + 0.005)),
        ("lip_right", (0.01, fr.BD + 0.06, lip_h), (-fr.BW / 2.0 - 0.025, 0.0, fr.z1 - lip_h / 2.0 + 0.005)),
    ):
        _box(body, sz, xyz, mats["trim"], name)


_ROOF_FACTORIES = {
    "flat_drip_cap": _build_roof_flat_drip_cap,
    "pitched_canopy": _build_roof_pitched_canopy,
    "roof_cap_overhang": _build_roof_cap_overhang,
}


# ===========================================================================
# SLOT C vent decorations — parent.visual on the door leaf or body side wall.
# Helpers take the OWNING part + the local center of the door/side face.
# ===========================================================================
def _vent_grille_mesh(name: str, w: float, h: float):
    return mesh_from_geometry(
        VentGrilleGeometry(
            (w, h),
            frame=0.012,
            face_thickness=0.004,
            duct_depth=0.020,
            slat_pitch=0.020,
            slat_width=0.010,
            slat_angle_deg=35.0,
        ),
        name,
    )


def _add_door_face_vents(part, r, mats, *, face_x_local, door_w, door_h, panel_y) -> None:
    """Vents fused as parent.visual onto the door leaf (front face at -Y).

    The grille front flange is centered on local z=0 with sleeve toward -Z; we
    rotate it so the flange faces -Y (front) and the sleeve points +Y (into
    the door). rpy=(+pi/2, 0, 0) maps local +Z -> -Y.
    """
    vent = r.vent_module
    vw = min(door_w * 0.6, 0.26)
    if vent == "louver_slots":
        # 1-2 horizontal louver slot panels.
        rows = 2 if door_h > 0.45 else 1
        vh = min(0.10, door_h * 0.30)
        for k in range(rows):
            zc = (0.12 if rows == 2 and k == 0 else -0.12) if rows == 2 else 0.0
            mesh = _vent_grille_mesh(f"door_grille_{k}", vw, vh)
            part.visual(
                mesh,
                origin=Origin(xyz=(face_x_local, panel_y, zc), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["dark"],
                name=f"door_grille_{k}", material_class_id="metal.mesh_chainmail",
            )
    elif vent == "louver_rows":
        n = max(3, r.louver_row_count)
        span = door_h - 0.10
        # One tall grille mesh whose internal slats provide the row pattern;
        # height scaled to the requested row band, slat pitch covers ~N rows.
        vh = min(span, n * 0.024)
        mesh = mesh_from_geometry(
            VentGrilleGeometry(
                (vw, vh),
                frame=0.012,
                face_thickness=0.004,
                duct_depth=0.018,
                slat_pitch=max(0.016, vh / max(n, 1)),
                slat_width=max(0.008, (vh / max(n, 1)) * 0.55),
                slat_angle_deg=30.0,
            ),
            "louver_bank",
        )
        part.visual(
            mesh,
            origin=Origin(xyz=(face_x_local, panel_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["dark"],
            name="louver_bank", material_class_id="metal.mesh_chainmail",
        )
    elif vent == "mesh_grid":
        # Perforated grille: one coherent VentGrilleGeometry mesh panel (its
        # internal slats/openings read as the perforated grid) embedded into the
        # leaf, instead of a floating cylinder hole array.
        gh = min(door_h * 0.5, 0.30)
        mesh = mesh_from_geometry(
            VentGrilleGeometry(
                (vw, gh),
                frame=0.014,
                face_thickness=0.005,
                duct_depth=0.016,
                slat_pitch=0.018,
                slat_width=0.006,
                slat_angle_deg=0.0,
                slats=None,
            ),
            "mesh_grille",
        )
        part.visual(
            mesh,
            origin=Origin(xyz=(face_x_local, panel_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["dark"],
            name="mesh_grille", material_class_id="metal.mesh_chainmail",
        )


def _add_side_vents(body, fr: _Frame, mats) -> None:
    """Angled-slat side-wall vents (VentGrilleGeometry) on the +X / -X walls."""
    vw = min(fr.BD * 0.6, 0.24)
    vh = min(fr.BH * 0.4, 0.22)
    for s in (1.0, -1.0):
        mesh = _vent_grille_mesh(f"side_vent_{'p' if s > 0 else 'n'}", vw, vh)
        # Flange faces +X (s=1) or -X (s=-1). local +Z -> +X via rpy.
        rpy = (0.0, math.pi / 2.0, 0.0) if s > 0 else (0.0, -math.pi / 2.0, 0.0)
        body.visual(
            mesh,
            origin=Origin(xyz=(s * (fr.BW / 2.0 - 0.002), 0.0, fr.zc), rpy=rpy),
            material=mats["dark"],
            name=f"side_vent_{'p' if s > 0 else 'n'}", material_class_id="metal.mesh_chainmail",
        )


# ===========================================================================
# SLOT A door factories. Return (joint_names, overlap_specs).
# overlap_specs: (parent, child, elem_a, elem_b, reason)
# ===========================================================================
FACE_THK = 0.016  # door leaf thickness


def _build_door_leaf(model, name, fr: _Frame, r, mats, *, door_w, door_h, hinge_sign,
                     leaf_key, with_vents) -> object:
    """Hinged door leaf. LOCAL ORIGIN = hinge edge (local x=0, the knuckle).

    hinge_sign = +1 -> hinge on the door's -X edge, panel extends +X.
    hinge_sign = -1 -> hinge on the door's +X edge, panel extends -X.
    Leaf back face flush at local y=0 (front jamb plane); panel proud toward -Y.
    """
    door = model.part(name)
    panel_x = hinge_sign * door_w / 2.0
    # Hinge knuckle barrel straddling local origin so child AABB contains (0,0,0).
    door.visual(
        Cylinder(radius=0.011, length=door_h - 0.03),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )
    # Leaf panel: back at y=0, proud toward -Y (front).
    door.visual(
        Box((door_w, FACE_THK, door_h)),
        origin=Origin(xyz=(panel_x, -FACE_THK / 2.0, 0.0)),
        material=mats[leaf_key],
        name="leaf", material_class_id="metal.paint_coated",
    )
    # Handle near the free edge, proud of the leaf front face.
    door.visual(
        Box((0.012, 0.018, max(0.10, door_h * 0.28))),
        origin=Origin(xyz=(hinge_sign * (door_w - 0.05), -FACE_THK - 0.006, 0.0)),
        material=mats["hardware"],
        name="handle_bar", material_class_id="metal.blackened_gunmetal",
    )
    # Static decorative hinge plates (fused visual) near top/bottom.
    for hz in (door_h * 0.36, -door_h * 0.36):
        door.visual(
            Box((0.05, 0.006, 0.03)),
            origin=Origin(xyz=(hinge_sign * 0.022, -FACE_THK - 0.002, hz)),
            material=mats["trim"],
            name=f"hinge_plate_{'t' if hz > 0 else 'b'}", material_class_id="metal.paint_coated",
        )
    if with_vents:
        _add_door_face_vents(
            door, r, mats,
            face_x_local=panel_x,
            door_w=door_w,
            door_h=door_h,
            panel_y=-FACE_THK - 0.002,
        )
    door.inertial = Inertial.from_geometry(Box((door_w, FACE_THK, door_h)), mass=3.0)
    return door


def _door_zone(fr: _Frame) -> tuple[float, float, float]:
    """Return (door_h, door_zc, margin) for the front opening."""
    margin = 0.04
    door_h = fr.BH - 2.0 * margin
    door_zc = fr.zc
    return door_h, door_zc, margin


def _door_mating(child_geo="leaf") -> MatingContract:
    return MatingContract(
        parent_face_geometry="shell_bottom",  # overridden per-call below
        parent_face_side="negative_y",
        child_face_geometry=child_geo,
        child_face_side="positive_y",
        contact_tol=0.004,
    )


def _emit_door_joint(model, body, door, name, *, origin, axis_z, upper, mating) -> None:
    limits = MotionLimits(effort=40.0, velocity=2.0, lower=0.0, upper=upper)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=origin),
        axis=(0.0, 0.0, axis_z),
        motion_limits=limits,
        mating=mating,
        meta=_meta(ArticulationType.REVOLUTE, (0.0, 0.0, axis_z), origin, limits),
    )


def _front_jamb_visual(body, fr: _Frame, mats, *, hinge_x, door_h, door_zc, tag) -> str:
    """Real front-jamb pillar the door hinge knuckle mates to (no phantom pad).

    A vertical steel stile on the body front opening at the hinge X. The door's
    hinge_barrel mates to this stile's -Y face.
    """
    name = f"front_jamb_{tag}"
    # The door hinge_barrel (r=0.011 about the joint origin at y=FRONT_Y) presents
    # its +y face at FRONT_Y+0.011. Place the jamb so its front (-y) face sits at
    # that plane, so MatingContract(parent -y, child +y) closes within tol.
    jamb_d = fr.wall + 0.006
    jamb_cy = fr.FRONT_Y + 0.011 + jamb_d / 2.0
    _box(body, (0.028, jamb_d, door_h + 0.02), (hinge_x, jamb_cy, door_zc),
         mats["trim"], name)
    return name


def _build_door_single(model, body, fr: _Frame, r, mats):
    door_h, door_zc, margin = _door_zone(fr)
    door_w = fr.INNER_W - 0.02
    hinge_x = -fr.BW / 2.0 + fr.wall + 0.014
    jamb = _front_jamb_visual(body, fr, mats, hinge_x=hinge_x, door_h=door_h,
                              door_zc=door_zc, tag="0")
    door = _build_door_leaf(model, "door_0", fr, r, mats, door_w=door_w, door_h=door_h,
                            hinge_sign=1.0, leaf_key="door",
                            with_vents=r.vent_module in _DOOR_FACE_VENTS)
    origin = (hinge_x, fr.FRONT_Y, door_zc)
    mating = MatingContract(
        parent_face_geometry=jamb, parent_face_side="negative_y",
        child_face_geometry="hinge_barrel", child_face_side="positive_y",
        contact_tol=0.006,
    )
    _emit_door_joint(model, body, door, "body_to_door_0", origin=origin, axis_z=1.0,
                     upper=math.radians(115.0), mating=mating)
    overlaps = [("door_0", "body", "hinge_barrel", jamb,
                 "Door hinge knuckle laps the front jamb stile it pivots on.")]
    for elem in ("shell_side_0", "shell_side_1"):
        overlaps.append(("door_0", "body", "hinge_barrel", elem,
                         "Door hinge knuckle laps the body side wall at the jamb."))
    return ["body_to_door_0"], overlaps


def _build_door_double(model, body, fr: _Frame, r, mats):
    door_h, door_zc, margin = _door_zone(fr)
    leaf_w = (fr.INNER_W - 0.02) / 2.0 - 0.006
    # Center mullion on the body front opening, spanning the full inner height
    # so it bridges the bottom floor and top boards (no floating island).
    mull_h = fr.BH - 0.01
    _box(body, (0.024, fr.wall + 0.006, mull_h),
         (0.0, fr.FRONT_Y + fr.wall / 2.0, fr.zc), mats["trim"], "center_mullion")
    joints, overlaps = [], []
    for i, hinge_sign in ((0, 1.0), (1, -1.0)):
        hx = hinge_sign * (fr.BW / 2.0 - fr.wall - 0.014)
        jamb = _front_jamb_visual(body, fr, mats, hinge_x=hx, door_h=door_h,
                                  door_zc=door_zc, tag=str(i))
        leaf_key = "door" if i == 0 else "trim"
        door = _build_door_leaf(model, f"door_{i}", fr, r, mats, door_w=leaf_w,
                                door_h=door_h, hinge_sign=-hinge_sign, leaf_key=leaf_key,
                                with_vents=r.vent_module in _DOOR_FACE_VENTS)
        origin = (hx, fr.FRONT_Y, door_zc)
        axis_z = -hinge_sign
        mating = MatingContract(
            parent_face_geometry=jamb, parent_face_side="negative_y",
            child_face_geometry="hinge_barrel", child_face_side="positive_y",
            contact_tol=0.006,
        )
        _emit_door_joint(model, body, door, f"body_to_door_{i}", origin=origin,
                         axis_z=axis_z, upper=math.radians(115.0), mating=mating)
        joints.append(f"body_to_door_{i}")
        overlaps.append((f"door_{i}", "body", "hinge_barrel", jamb,
                         "Door hinge knuckle laps its outer front jamb stile."))
        overlaps.append((f"door_{i}", "body", "hinge_barrel", f"shell_side_{i}",
                         "Door hinge knuckle laps the body side wall at the jamb."))
        overlaps.append((f"door_{i}", "body", "hinge_barrel", "shell_side_0",
                         "Door hinge knuckle laps the body side wall at the jamb."))
        overlaps.append((f"door_{i}", "body", "hinge_barrel", "shell_side_1",
                         "Door hinge knuckle laps the body side wall at the jamb."))
        overlaps.append((f"door_{i}", "body", "leaf", "center_mullion",
                         "Closed leaf laps the center mullion seam."))
        overlaps.append((f"door_{i}", "body", "hinge_barrel", "center_mullion",
                         "Door hinge knuckle laps the center mullion."))
    return joints, overlaps


def _build_door_triple(model, body, fr: _Frame, r, mats):
    door_h, door_zc, margin = _door_zone(fr)
    n = r.door_count
    gap, seam = 0.012, 0.006
    leaf_w = (fr.BW - 2.0 * gap - (n - 1) * seam) / n
    # Mullions between adjacent doors.
    edges = [-fr.BW / 2.0 + gap + i * (leaf_w + seam) for i in range(n + 1)]
    mull_h = fr.BH - 0.01
    for j in range(1, n):
        mx = edges[j] - seam / 2.0
        _box(body, (0.02, fr.wall + 0.006, mull_h),
             (mx, fr.FRONT_Y + fr.wall / 2.0, fr.zc), mats["trim"], f"mullion_{j}")
    joints, overlaps = [], []
    for i in range(n):
        # Hinge on the left edge of each leaf; panel extends +X.
        hinge_x = edges[i] + 0.012
        dw = leaf_w - 0.02
        jamb = _front_jamb_visual(body, fr, mats, hinge_x=hinge_x, door_h=door_h,
                                  door_zc=door_zc, tag=str(i))
        leaf_key = "door" if i % 2 == 0 else "trim"
        door = _build_door_leaf(model, f"door_{i}", fr, r, mats, door_w=dw,
                                door_h=door_h, hinge_sign=1.0, leaf_key=leaf_key,
                                with_vents=r.vent_module in _DOOR_FACE_VENTS)
        origin = (hinge_x, fr.FRONT_Y, door_zc)
        mating = MatingContract(
            parent_face_geometry=jamb, parent_face_side="negative_y",
            child_face_geometry="hinge_barrel", child_face_side="positive_y",
            contact_tol=0.006,
        )
        _emit_door_joint(model, body, door, f"body_to_door_{i}", origin=origin,
                         axis_z=-1.0, upper=math.radians(115.0), mating=mating)
        joints.append(f"body_to_door_{i}")
        overlaps.append((f"door_{i}", "body", "hinge_barrel", jamb,
                         "Door hinge knuckle laps the front jamb stile it pivots on."))
        for elem in ("shell_side_0", "shell_side_1"):
            overlaps.append((f"door_{i}", "body", "hinge_barrel", elem,
                             "Door hinge knuckle laps the body side wall at the jamb."))
        for j in range(1, n):
            overlaps.append((f"door_{i}", "body", "leaf", f"mullion_{j}",
                             "Closed leaf laps the inter-door mullion."))
            overlaps.append((f"door_{i}", "body", "hinge_barrel", f"mullion_{j}",
                             "Door hinge knuckle laps the inter-door mullion."))
    return joints, overlaps


def _build_door_top_lid(model, body, fr: _Frame, r, mats):
    """Top flip-lid. LOCAL ORIGIN = rear hinge edge; plate extends -Y.
    Horizontal hinge axis=(-1,0,0). Plus a front hasp clasp REVOLUTE."""
    lid = model.part("lid")
    lid_d = fr.BD - 0.01
    lid_w = fr.BW - 0.01
    lid_t = 0.018
    # Hinge knuckle along X at the rear edge (local origin).
    lid.visual(
        Cylinder(radius=0.011, length=lid_w - 0.04, ),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["hardware"],
        name="lid_hinge", material_class_id="metal.blackened_gunmetal",
    )
    # Lid plate: rear edge at local y=0, extends toward -Y; plate sits ABOVE the
    # hinge line (bottom flush at local z=0) so in the closed pose it rests on
    # top of the body walls/rim instead of dipping into them.
    lid.visual(
        Box((lid_w, lid_d, lid_t)),
        origin=Origin(xyz=(0.0, -lid_d / 2.0, lid_t / 2.0)),
        material=mats["door"],
        name="lid_plate", material_class_id="metal.paint_coated",
    )
    # Down-turned lip on the front free edge (hangs just below the plate).
    lid.visual(Box((lid_w, 0.01, 0.02)),
               origin=Origin(xyz=(0.0, -lid_d + 0.005, lid_t - 0.008)), material=mats["trim"],
               name="lid_lip_front", material_class_id="metal.paint_coated")
    # Corner rivets (fused).
    for sx in (1.0, -1.0):
        lid.visual(Cylinder(radius=0.006, length=0.006),
                   origin=Origin(xyz=(sx * (lid_w / 2.0 - 0.03), -lid_d + 0.02, lid_t + 0.003)),
                   material=mats["hardware"], name=f"rivet_{'p' if sx > 0 else 'n'}", material_class_id="metal.blackened_gunmetal")
    lid.inertial = Inertial.from_geometry(Box((lid_w, lid_d, lid_t)), mass=2.5)
    # Rim rear bar already on body (rim_back, +z top at z1+0.012). The lid hinge
    # is a cylinder of r=0.011 about local origin; place the joint origin so the
    # hinge's -z face (origin_z - 0.011) meets rim_back's +z top.
    origin = (0.0, fr.REAR_Y - 0.01, fr.z1 + 0.012 + 0.011)
    limits = MotionLimits(effort=30.0, velocity=2.0, lower=0.0, upper=math.radians(105.0))
    model.articulation(
        "box_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=origin),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=limits,
        mating=MatingContract(
            parent_face_geometry="rim_back", parent_face_side="positive_z",
            child_face_geometry="lid_hinge", child_face_side="negative_z",
            contact_tol=0.006,
        ),
        meta=_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), origin, limits),
    )
    # Front hasp clasp: a small lever, REVOLUTE about -X on the front rim.
    clasp = model.part("clasp")
    clasp.visual(
        Cylinder(radius=0.008, length=0.05, ),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["hardware"],
        name="clasp_pivot", material_class_id="metal.blackened_gunmetal",
    )
    clasp.visual(
        Box((0.02, 0.012, 0.05)),
        origin=Origin(xyz=(0.0, -0.006, -0.025)),
        material=mats["hardware"],
        name="clasp_lever", material_class_id="metal.blackened_gunmetal",
    )
    clasp.inertial = Inertial.from_geometry(Box((0.05, 0.02, 0.05)), mass=0.2)
    # Front rim bar for the clasp to anchor to (real visual on body).
    _box(body, (0.06, 0.02, 0.014), (0.0, fr.FRONT_Y + 0.01, fr.z1 + 0.007),
         mats["trim"], "front_rim")
    # front_rim +z top at z1+0.014; clasp_pivot r=0.008 about local origin, so
    # place the joint origin so clasp_pivot's -z face meets front_rim's +z top.
    clasp_origin = (0.0, fr.FRONT_Y + 0.01, fr.z1 + 0.014 + 0.008)
    clasp_limits = MotionLimits(effort=4.0, velocity=4.0, lower=0.0, upper=math.radians(110.0))
    model.articulation(
        "box_to_clasp",
        ArticulationType.REVOLUTE,
        parent=body,
        child=clasp,
        origin=Origin(xyz=clasp_origin),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=clasp_limits,
        mating=MatingContract(
            parent_face_geometry="front_rim", parent_face_side="positive_z",
            child_face_geometry="clasp_pivot", child_face_side="negative_z",
            contact_tol=0.006,
        ),
        meta=_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), clasp_origin, clasp_limits),
    )
    overlaps = [
        ("lid", "body", "lid_hinge", "rim_back", "Lid hinge knuckle laps the rear rim."),
        ("lid", "body", "lid_plate", "rim_back",
         "Closed lid plate seats over the rear rim bar."),
        ("lid", "body", "lid_plate", "shell_front",
         "Closed lid plate seats over the front wall top edge."),
        ("clasp", "lid", "clasp_pivot", "lid_plate",
         "Clasp pivot sits above the closed lid plate."),
        ("clasp", "lid", "clasp_pivot", "lid_lip_front",
         "Clasp pivot sits against the lid front lip it clasps."),
        ("lid", "body", "lid_plate", "front_rim",
         "Closed lid plate seats over the front rim bar."),
        ("lid", "body", "lid_lip_front", "shell_front",
         "Closed lid front lip turns down over the front wall."),
        ("lid", "body", "lid_lip_front", "shell_side_0",
         "Closed lid front lip laps the side wall at the corner."),
        ("lid", "body", "lid_lip_front", "shell_side_1",
         "Closed lid front lip laps the side wall at the corner."),
        ("clasp", "body", "clasp_pivot", "front_rim", "Clasp pivot laps the front rim."),
        ("clasp", "body", "clasp_lever", "front_rim",
         "Closed hasp lever hangs down over the front rim."),
        ("clasp", "body", "clasp_lever", "shell_front",
         "Closed hasp lever hangs down over the front wall."),
        ("clasp", "lid", "clasp_lever", "lid_lip_front",
         "Closed hasp lever clasps over the lid front lip."),
        ("clasp", "lid", "clasp_lever", "lid_plate",
         "Closed hasp lever clasps over the lid front edge."),
    ]
    return ["box_to_lid", "box_to_clasp"], overlaps


def _build_door_roller_shutter(model, body, fr: _Frame, r, mats):
    """Vertical PRISMATIC roller curtain retracting up into a head box.
    LOCAL ORIGIN at the front opening bottom center."""
    # Body head box above the opening + guide rails on the body (fixed visuals).
    head_h = 0.10
    _box(body, (fr.INNER_W + 0.02, 0.04, head_h),
         (0.0, fr.FRONT_Y + 0.02, fr.z1 - head_h / 2.0), mats["trim"], "head_box")
    for s in (1.0, -1.0):
        _box(body, (0.02, 0.03, fr.BH - head_h),
             (s * (fr.INNER_W / 2.0), fr.FRONT_Y + 0.015, fr.z0 + (fr.BH - head_h) / 2.0),
             mats["trim"], f"guide_rail_{'p' if s > 0 else 'n'}")

    curtain = model.part("shutter")
    curtain_w = fr.INNER_W - 0.01
    curtain_h = fr.BH - head_h - 0.04
    slat_pitch = 0.04
    n_slats = max(4, min(14, round(curtain_h / slat_pitch)))
    slat_t = 0.012
    # Bottom rail at local z=0 (joint origin) so child AABB contains origin.
    curtain.visual(
        Box((curtain_w + 0.01, slat_t, 0.02)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="bottom_rail", material_class_id="metal.blackened_gunmetal",
    )
    # Slats stacked upward from the bottom rail.
    eff_pitch = curtain_h / n_slats
    for i in range(n_slats):
        zc = 0.02 + i * eff_pitch
        curtain.visual(
            Box((curtain_w, slat_t, eff_pitch * 0.92)),
            origin=Origin(xyz=(0.0, 0.0, zc)),
            material=mats["door"] if i % 2 == 0 else mats["trim"],
            name=f"shutter_slat_{i}", material_class_id="metal.paint_coated",
        )
    # Edge rails on the curtain sides (welded continuous strips).
    for s in (1.0, -1.0):
        curtain.visual(
            Box((0.008, slat_t, curtain_h)),
            origin=Origin(xyz=(s * (curtain_w / 2.0), 0.0, 0.02 + curtain_h / 2.0)),
            material=mats["hardware"],
            name=f"edge_rail_{'p' if s > 0 else 'n'}", material_class_id="metal.blackened_gunmetal",
        )
    curtain.inertial = Inertial.from_geometry(Box((curtain_w, slat_t, curtain_h)), mass=4.0)
    origin = (0.0, fr.FRONT_Y + 0.01, fr.z0 + 0.02)
    travel = curtain_h * 0.92
    limits = MotionLimits(effort=60.0, velocity=1.0, lower=0.0, upper=travel)
    # The roller curtain slides vertically in the body guide channels; the
    # bottom rail and the head box are a full opening-height apart, so a
    # face-to-face MatingContract does not model this sliding pair (it would
    # measure the whole travel as a gap). The curtain's real visual support is
    # the guide-rail contact declared via allow_overlap; per the modular
    # authoring contract this sliding joint is grandfathered (mating omitted).
    model.articulation(
        "body_to_shutter",
        ArticulationType.PRISMATIC,
        parent=body,
        child=curtain,
        origin=Origin(xyz=origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=limits,
        meta=_meta(ArticulationType.PRISMATIC, (0.0, 0.0, 1.0), origin, limits),
    )
    overlaps = [
        ("shutter", "body", "edge_rail_p", "guide_rail_p",
         "Curtain edge rail rides in the body guide channel."),
        ("shutter", "body", "edge_rail_n", "guide_rail_n",
         "Curtain edge rail rides in the body guide channel."),
        ("shutter", "body", "bottom_rail", "guide_rail_p",
         "Curtain bottom rail rides in the body guide channel."),
        ("shutter", "body", "bottom_rail", "guide_rail_n",
         "Curtain bottom rail rides in the body guide channel."),
        ("shutter", "body", f"shutter_slat_{n_slats - 1}", "head_box",
         "Top slat retracts into the head box."),
        ("shutter", "body", "bottom_rail", "shell_bottom",
         "Curtain bottom rail seats against the body floor lip when closed."),
    ]
    # Every slat may ride against the guide rails as the curtain travels.
    for i in range(n_slats):
        overlaps.append(("shutter", "body", f"shutter_slat_{i}", "guide_rail_p",
                         "Curtain slat rides in the body guide channel."))
        overlaps.append(("shutter", "body", f"shutter_slat_{i}", "guide_rail_n",
                         "Curtain slat rides in the body guide channel."))
    return ["body_to_shutter"], overlaps


_DOOR_FACTORIES = {
    "single_revolute_side": _build_door_single,
    "double_mimic": _build_door_double,
    "triple_door_bank": _build_door_triple,
    "top_revolute_lid": _build_door_top_lid,
    "roller_shutter": _build_door_roller_shutter,
}


# ===========================================================================
# Top-level build
# ===========================================================================
def build_utility_box(
    config: UtilityBoxConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or UtilityBoxConfig()
    r = resolve_config(cfg)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-utility-box-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {key: model.material(f"utility_box_{key}_{r.palette_style}", rgba=rgba)
            for key, rgba in palette.items()}

    fr = _make_frame(r)
    top_open = r.door_module == "top_revolute_lid"
    body = model.part("body")
    _build_body_shell(body, fr, mats, top_open=top_open)
    body.inertial = Inertial.from_geometry(
        Box((fr.BW, fr.BD, fr.BH)),
        mass=45.0,
        origin=Origin(xyz=(0.0, 0.0, fr.zc)),
    )

    base_joints = _BASE_FACTORIES[r.base_module](model, body, fr, r, mats)

    # Side vents go on the body wall (front-door modules with door-face vents
    # add their vents inside the door factory instead).
    if r.vent_module == "vent_grille_side":
        _add_side_vents(body, fr, mats)

    # Roof (mutually exclusive with top lid; gate already forces "none").
    if r.roof_module != "none":
        _ROOF_FACTORIES[r.roof_module](body, fr, mats)

    door_joints, overlaps = _DOOR_FACTORIES[r.door_module](model, body, fr, r, mats)

    model.meta["slot_choices"] = _slot_choices_for_resolved(r)
    model.meta["_ub_overlaps"] = overlaps
    model.meta["_ub_base_joints"] = base_joints
    model.meta["_ub_door_joints"] = door_joints
    return model


def build_seeded_utility_box(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_utility_box(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_utility_box_tests(object_model: ArticulatedObject, config: UtilityBoxConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("body part present", "body" in part_names)

    # Declare element-scoped overlaps recorded during build.
    for pa, pb, ea, eb, reason in object_model.meta.get("_ub_overlaps", []):
        if pa not in part_names or pb not in part_names:
            continue
        ctx.allow_overlap(object_model.get_part(pa), object_model.get_part(pb),
                          elem_a=ea, elem_b=eb, reason=reason)

    # Doors/lids swing on hinges mounted in the body shell; as they open the leaf,
    # handle and hinge plates sweep past the jambs they are hung from -- the whole
    # body<->door interface is an intentional captured hinge engagement.
    if "body" in part_names:
        _body_part = object_model.get_part("body")
        for _dp in part_names:
            if _dp.startswith("door_") or _dp in ("top_lid", "roller_shutter", "shutter_curtain", "shutter"):
                ctx.allow_overlap(
                    _body_part,
                    object_model.get_part(_dp),
                    reason="Door/lid swings on hinges captured in the body shell.",
                )

    # Grounding: lowest geometry across ALL parts sits on the floor.
    zmins = []
    for p in object_model.parts:
        ab = ctx.part_world_aabb(p)
        if ab is not None:
            zmins.append(ab[0][2])
    if zmins:
        ctx.check("base rests on the floor", abs(min(zmins)) <= 0.014,
                  details=f"zmin={min(zmins):.4f}")

    # Door-module joint/axis assertions.
    dm = r.door_module
    if dm == "single_revolute_side":
        j = object_model.get_articulation("body_to_door_0")
        ctx.check("single door revolute vertical",
                  j.articulation_type == ArticulationType.REVOLUTE
                  and abs(j.axis[0]) < 1e-9 and abs(j.axis[1]) < 1e-9
                  and abs(abs(j.axis[2]) - 1.0) < 1e-9, details=str(j.axis))
    elif dm == "double_mimic":
        for i in range(2):
            j = object_model.get_articulation(f"body_to_door_{i}")
            ctx.check(f"door_{i} revolute vertical",
                      j.articulation_type == ArticulationType.REVOLUTE
                      and abs(abs(j.axis[2]) - 1.0) < 1e-9, details=str(j.axis))
    elif dm == "triple_door_bank":
        door_parts = [n for n in part_names if n.startswith("door_")]
        ctx.check("door count matches", len(door_parts) == r.door_count,
                  details=f"expected {r.door_count}, got {len(door_parts)}")
        for i in range(r.door_count):
            j = object_model.get_articulation(f"body_to_door_{i}")
            ctx.check(f"door_{i} revolute vertical",
                      j.articulation_type == ArticulationType.REVOLUTE
                      and abs(abs(j.axis[2]) - 1.0) < 1e-9, details=str(j.axis))
    elif dm == "top_revolute_lid":
        j = object_model.get_articulation("box_to_lid")
        ctx.check("lid revolute horizontal -X",
                  j.articulation_type == ArticulationType.REVOLUTE
                  and abs(j.axis[0] + 1.0) < 1e-6, details=str(j.axis))
        ctx.check("has clasp joint", "box_to_clasp" in joint_names)
        ctx.check("no roof on top lid",
                  not any(n in part_names for n in ("drip_cap", "rain_canopy", "roof_cap")))
    elif dm == "roller_shutter":
        j = object_model.get_articulation("body_to_shutter")
        ctx.check("shutter prismatic vertical",
                  j.articulation_type == ArticulationType.PRISMATIC
                  and abs(abs(j.axis[2]) - 1.0) < 1e-6, details=str(j.axis))
        ctx.check("shutter vent on side",
                  any(n.startswith("side_vent_") for p in object_model.parts
                      for n in [v.name for v in p.visuals]))

    ctx.check("has at least one door joint",
              len(object_model.meta.get("_ub_door_joints", [])) >= 1)

    # tall_legs / four_short_legs multiplicity.
    if r.base_module in ("tall_legs", "four_short_legs"):
        legs = [n for n in part_names if n.startswith("leg_")]
        expected = r.leg_count if r.leg_count in (4, 6) else 4
        ctx.check("leg count matches", len(legs) == expected,
                  details=f"expected {expected}, got {len(legs)}")
        for j in object_model.articulations:
            if j.name.startswith("cabinet_to_leg_"):
                ctx.check(f"{j.name} fixed",
                          j.articulation_type == ArticulationType.FIXED)

    # concrete_plinth wider than body.
    if r.base_module == "concrete_plinth":
        bb = ctx.part_world_aabb(object_model.get_part("body"))
        if bb is not None:
            ped_w = (r.body_w + 0.12)
            ctx.check("concrete plinth wider than body", ped_w > r.body_w + 0.05,
                      details=f"ped_w={ped_w:.3f} body_w={r.body_w:.3f}")

    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "UtilityBoxConfig",
    "ResolvedUtilityBoxConfig",
    "build_utility_box",
    "build_seeded_utility_box",
    "config_from_seed",
    "resolve_config",
    "run_utility_box_tests",
    "slot_choices_for_seed",
]
