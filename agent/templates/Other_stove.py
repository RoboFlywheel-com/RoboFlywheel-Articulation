# SPDX-License-Identifier: Apache-2.0

"""Stove — modular procedural template (freestanding gas range / cooktop).

NOTE on category: "stove" here = a **freestanding floor-standing gas range /
cooktop** — a grounded cabinet ``body`` whose TOP is a cooktop (N gas burners
with silver caps + cast-iron/wire pan grates), a front control fascia carrying N
rotary ``knob`` controls, a front-opening ``oven_door`` (or french double), and a
plinth / storage drawer / retro legs at the base. The CORE IDENTITY = the top
cooktop (burner + grate) + control knobs. This is what distinguishes a stove from
a ``built_in_oven`` (embedded box, no burners).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_Other_stove.md`` and the
``picture/Other/stove`` 5-star sample pool (2 parents + 6 slot fork variants), all
synced under ``data/records/``.

UNIFIED COORDINATE CONVENTION (both parents + all variants): +X = front of the
range (toward the user), width along Y, height along Z, grounded at z=0.

Structure (pattern = ``mixed``): a single root ``body`` part, three fixed named
slots (the real joint-topology axes) plus one burner-count multiplicity axis,
each encoded into the slot_choice tuple:

  * ``door_mechanism`` (3): drop_down_front (1 REVOLUTE +Y bottom hinge) /
    side_hinged_swing (1 REVOLUTE -Z left jamb) / french_double (2 REVOLUTE
    mirrored ∓Z).
  * ``cooktop`` (3): open_burners (Nb burners + grates, body visual / FIXED
    grate) / glass_lift_lid (a REVOLUTE -Y rear-hinged glass lid over the
    burners) / griddle_flat_top (a FIXED cadquery hotplate replacing the
    burners; forces Nb=0).
  * ``base`` (3): plinth_kickbase (solid plinth, body visual) / storage_drawer
    (a PRISMATIC +X pull-out drawer) / raised_legs (four LatheGeometry retro
    legs raising the whole machine, body visual, Rule 1).
  * ``burner_count`` (Nb in [1,6], or 0 when griddle): N burner units on the
    cooktop deck along an XY grid + N derived rotary knobs on the fascia, each a
    REVOLUTE front-normal (+X) dial. Encoded as ``("burner_count", f"b{Nb}")``.

All hinge arms / pins / lugs / drawer slides / knob caps / burners / grates /
legs are captured-pin / rail-on-rail / cap-on-panel / seated-contact geometry, so
those joints omit ``MatingContract`` (grandfathered) and are guarded by the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests allow_overlap block). Burners / grates / legs are
non-moving (Rule 1) -> body visual / FIXED, never independent moving parts.

Compatibility gating (resolve_config, spec §9):
  * cooktop=griddle_flat_top -> Nb forced to 0 (no open burners), but knobs
    retained (oven + griddle temperature control, default 2).
  * Nb / scales clamped to declared domains, re-shrunk by clearance
    inequalities (burner grid <= cooktop deck, knob row <= fascia width, drawer
    travel <= drawer depth - retained insertion).
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
    BezelGeometry,
    Box,
    Cylinder,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    KnobSkirt,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    find_geometry_overlaps_in_poses,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

DoorMechanism = Literal["drop_down_front", "side_hinged_swing", "french_double"]
Cooktop = Literal["open_burners", "glass_lift_lid", "griddle_flat_top"]
Base = Literal["plinth_kickbase", "storage_drawer", "raised_legs"]
PaletteStyle = Literal[
    "white_enamel",
    "brushed_stainless",
    "matte_black_steel",
    "cream_retro",
    "glossy_red",
]

DOOR_MECHANISMS: tuple[DoorMechanism, ...] = (
    "drop_down_front",
    "side_hinged_swing",
    "french_double",
)
COOKTOPS: tuple[Cooktop, ...] = ("open_burners", "glass_lift_lid", "griddle_flat_top")
BASES: tuple[Base, ...] = ("plinth_kickbase", "storage_drawer", "raised_legs")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "white_enamel",
    "brushed_stainless",
    "matte_black_steel",
    "cream_retro",
    "glossy_red",
)

# Burner-count multiplicity declared / sampling domains (spec §8).
BURNER_COUNT_MIN, BURNER_COUNT_MAX = 1, 6
BURNER_COUNT_CHOICES = (1, 2, 3, 4, 5, 6)
BURNER_COUNT_WEIGHTS = (0.08, 0.27, 0.10, 0.32, 0.08, 0.15)
GRIDDLE_KNOB_COUNT = 2  # knobs retained on a griddle stove (oven + plate temp)

# ---------------------------------------------------------------------------
# Palette colorways (spec §palette). white_enamel / brushed_stainless come
# straight from the P1 / P2 sources; matte_black_steel / cream_retro / glossy_red
# are synthesized real-world range colorways from the same material families.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_enamel": {
        "body": (0.93, 0.93, 0.91, 1.0),
        "door": (0.93, 0.93, 0.91, 1.0),
        "glass": (0.05, 0.06, 0.07, 0.93),
        "panel": (0.95, 0.95, 0.94, 1.0),
        "knob": (0.96, 0.96, 0.95, 1.0),
        "metal": (0.76, 0.77, 0.78, 1.0),
        "cap": (0.82, 0.83, 0.84, 1.0),
        "burner": (0.60, 0.61, 0.62, 1.0),
        "iron": (0.07, 0.07, 0.08, 1.0),
        "cavity": (0.20, 0.19, 0.18, 1.0),
        "rack": (0.68, 0.69, 0.70, 1.0),
        "leg": (0.78, 0.79, 0.80, 1.0),
        "foot": (0.12, 0.12, 0.12, 1.0),
    },
    "brushed_stainless": {
        "body": (0.72, 0.73, 0.75, 1.0),
        "door": (0.35, 0.36, 0.38, 1.0),
        "glass": (0.13, 0.14, 0.16, 0.85),
        "panel": (0.65, 0.66, 0.68, 1.0),
        "knob": (0.11, 0.11, 0.12, 1.0),
        "metal": (0.74, 0.75, 0.77, 1.0),
        "cap": (0.80, 0.81, 0.82, 1.0),
        "burner": (0.35, 0.36, 0.38, 1.0),
        "iron": (0.10, 0.10, 0.11, 1.0),
        "cavity": (0.22, 0.22, 0.23, 1.0),
        "rack": (0.62, 0.63, 0.65, 1.0),
        "leg": (0.74, 0.75, 0.77, 1.0),
        "foot": (0.14, 0.14, 0.15, 1.0),
    },
    "matte_black_steel": {
        "body": (0.13, 0.13, 0.14, 1.0),
        "door": (0.10, 0.10, 0.11, 1.0),
        "glass": (0.05, 0.05, 0.06, 0.90),
        "panel": (0.16, 0.16, 0.17, 1.0),
        "knob": (0.82, 0.82, 0.84, 1.0),
        "metal": (0.70, 0.71, 0.73, 1.0),
        "cap": (0.66, 0.67, 0.69, 1.0),
        "burner": (0.30, 0.30, 0.32, 1.0),
        "iron": (0.08, 0.08, 0.09, 1.0),
        "cavity": (0.10, 0.10, 0.11, 1.0),
        "rack": (0.55, 0.55, 0.57, 1.0),
        "leg": (0.70, 0.71, 0.73, 1.0),
        "foot": (0.06, 0.06, 0.07, 1.0),
    },
    "cream_retro": {
        "body": (0.92, 0.90, 0.85, 1.0),
        "door": (0.92, 0.90, 0.85, 1.0),
        "glass": (0.09, 0.09, 0.10, 0.92),
        "panel": (0.94, 0.92, 0.87, 1.0),
        "knob": (0.80, 0.80, 0.82, 1.0),
        "metal": (0.80, 0.80, 0.82, 1.0),
        "cap": (0.78, 0.79, 0.80, 1.0),
        "burner": (0.55, 0.55, 0.57, 1.0),
        "iron": (0.10, 0.09, 0.08, 1.0),
        "cavity": (0.24, 0.22, 0.20, 1.0),
        "rack": (0.74, 0.72, 0.68, 1.0),
        "leg": (0.82, 0.82, 0.84, 1.0),
        "foot": (0.30, 0.26, 0.22, 1.0),
    },
    "glossy_red": {
        "body": (0.62, 0.10, 0.10, 1.0),
        "door": (0.10, 0.10, 0.11, 1.0),
        "glass": (0.05, 0.06, 0.07, 0.92),
        "panel": (0.14, 0.14, 0.15, 1.0),
        "knob": (0.82, 0.82, 0.84, 1.0),
        "metal": (0.78, 0.79, 0.80, 1.0),
        "cap": (0.82, 0.83, 0.84, 1.0),
        "burner": (0.58, 0.59, 0.60, 1.0),
        "iron": (0.07, 0.07, 0.08, 1.0),
        "cavity": (0.18, 0.16, 0.16, 1.0),
        "rack": (0.68, 0.69, 0.70, 1.0),
        "leg": (0.78, 0.79, 0.80, 1.0),
        "foot": (0.12, 0.12, 0.12, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), calibrated to P1 compact range.
# +X = front (user), width along Y, height along Z, grounded at z=0.
# ---------------------------------------------------------------------------
_HALF_D = 0.30  # half depth (X); front face at x=+0.30
_HALF_W = 0.25  # half width (Y)
_BODY_W = 0.50  # body width along Y
_BODY_D = 0.60  # body depth along X

_PLINTH_TOP = 0.10  # top of the plinth / oven cavity floor (no-legs case)
_DOOR_TOP = 0.62  # oven door / cavity top
_TOP_HOUSING_Z0 = 0.619  # under-cooktop housing bottom
_DECK_TOP = 0.785  # cooktop well floor z
_RIM_TOP = 0.805  # raised cooktop rim top z

_DOOR_T = 0.04

_KNOB_Z = 0.71  # knob row height on the fascia
_KNOB_D = 0.038
_KNOB_H = 0.024
_KNOB_PITCH = 0.075  # base center-to-center spacing along Y

_GRATE_BAR = 0.008

_DRAWER_H = 0.14  # drawer front panel height
_DRAWER_TRAVEL = 0.30
_DRAWER_RETAIN = 0.04

_LEG_H = 0.14  # how high the legs raise the body
_LEG_SPLAY = 0.14  # leg splay angle (rad)


@dataclass(frozen=True)
class StoveConfig:
    door_mechanism: DoorMechanism | None = None
    cooktop: Cooktop | None = None
    base: Base | None = None
    burner_count: int | None = None
    palette_style: PaletteStyle = "white_enamel"
    cooktop_width_scale: float = 1.0
    body_height_scale: float = 1.0
    body_depth_scale: float = 1.0
    door_open_angle_scale: float = 1.0
    lid_open_angle_scale: float = 1.0
    drawer_travel_scale: float = 1.0
    burner_spacing_scale: float = 1.0
    name: str = "stove"


@dataclass(frozen=True)
class ResolvedStoveConfig:
    door_mechanism: DoorMechanism
    cooktop: Cooktop
    base: Base
    burner_count: int
    knob_count: int
    palette_style: PaletteStyle
    # concrete geometry (scaled)
    body_w: float
    body_d: float
    half_w: float
    half_d: float
    base_lift: float  # z offset added to the whole cabinet (legs)
    plinth_top: float  # cavity floor z (absolute, includes base_lift)
    door_top: float
    deck_top: float
    rim_top: float
    door_h: float
    door_open_angle: float
    lid_open_angle: float
    drawer_travel: float
    knob_z: float
    knob_pitch: float
    burner_spacing: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> StoveConfig:
    """Procedural sampling; seed=0 is NOT special."""
    rng = random.Random(seed)
    return StoveConfig(
        door_mechanism=rng.choice(DOOR_MECHANISMS),
        cooktop=rng.choice(COOKTOPS),
        base=rng.choice(BASES),
        burner_count=rng.choices(BURNER_COUNT_CHOICES, weights=BURNER_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        cooktop_width_scale=round(rng.uniform(0.92, 1.10), 4),
        body_height_scale=round(rng.uniform(0.90, 1.12), 4),
        body_depth_scale=round(rng.uniform(0.92, 1.10), 4),
        door_open_angle_scale=round(rng.uniform(0.88, 1.05), 4),
        lid_open_angle_scale=round(rng.uniform(0.85, 1.10), 4),
        drawer_travel_scale=round(rng.uniform(0.85, 1.05), 4),
        burner_spacing_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_stove_{seed}",
    )


def resolve_config(config: StoveConfig | None = None) -> ResolvedStoveConfig:
    cfg = config or StoveConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    door_mechanism = _pick(cfg.door_mechanism, DOOR_MECHANISMS)
    cooktop = _pick(cfg.cooktop, COOKTOPS)
    base = _pick(cfg.base, BASES)

    burner_count = int(cfg.burner_count) if cfg.burner_count is not None else 4
    burner_count = int(_clamp(burner_count, BURNER_COUNT_MIN, BURNER_COUNT_MAX))

    # --- Compatibility gating (spec §9). ---
    # cooktop=griddle_flat_top: one flat hotplate, no open burners -> Nb=0.
    if cooktop == "griddle_flat_top":
        burner_count = 0
        knob_count = GRIDDLE_KNOB_COUNT
    else:
        knob_count = burner_count

    width_scale = _clamp(cfg.cooktop_width_scale, 0.92, 1.10)
    height_scale = _clamp(cfg.body_height_scale, 0.90, 1.12)
    depth_scale = _clamp(cfg.body_depth_scale, 0.92, 1.10)
    angle_scale = _clamp(cfg.door_open_angle_scale, 0.88, 1.05)
    lid_angle_scale = _clamp(cfg.lid_open_angle_scale, 0.85, 1.10)
    travel_scale = _clamp(cfg.drawer_travel_scale, 0.85, 1.05)
    spacing_scale = _clamp(cfg.burner_spacing_scale, 0.90, 1.10)

    body_w = _BODY_W * width_scale
    half_w = body_w / 2.0
    body_d = _BODY_D * depth_scale
    half_d = body_d / 2.0

    base_lift = _LEG_H if base == "raised_legs" else 0.0
    plinth_top = _PLINTH_TOP + base_lift
    door_top = _DOOR_TOP + base_lift
    deck_top = _DECK_TOP * height_scale + base_lift
    rim_top = deck_top + 0.020
    door_h = door_top - plinth_top

    # Door open angle never exceeds horizontal (pi/2) for the drop-down family.
    door_open_angle = _clamp((math.pi / 2.0) * angle_scale, math.pi / 3.0, math.pi / 2.0)
    lid_open_angle = _clamp(math.radians(85.0) * lid_angle_scale, math.radians(60.0), math.radians(95.0))

    # Drawer travel <= drawer box depth - retained insertion (spec §7).
    drawer_travel = _DRAWER_TRAVEL * travel_scale
    drawer_travel = min(drawer_travel, body_d - _DRAWER_RETAIN - 0.16)
    drawer_travel = max(drawer_travel, 0.12)

    burner_spacing = spacing_scale  # multiplier applied to grid spacings

    # --- burner-grid clearance clamp (spec §9): the burner grid + its cast-iron
    #     grates must fit inside the cooktop deck. Shrink the spacing until the
    #     outer grate edge stays inside the deck on both axes (fixes overhang for
    #     Nb=6 + high burner_spacing + low cooktop_width). ---
    if burner_count > 0:
        b_margin = 0.012
        for _ in range(80):
            centers = _burner_centers(burner_count, burner_spacing)
            gh = _grate_half_for_centers(centers)
            max_cx = max((abs(cx) for cx, _cy in centers), default=0.0)
            max_cy = max((abs(cy) for _cx, cy in centers), default=0.0)
            if (max_cy + gh <= half_w - b_margin) and (max_cx + gh <= half_d - b_margin):
                break
            if burner_spacing > 0.55:
                burner_spacing = max(0.55, burner_spacing - 0.01)
            else:
                break

    # --- knob clearance inequality (spec §7): the knob row must fit the body
    #     width. row_w = (Nk-1)*pitch + KNOB_D <= body_w - 2*margin. ---
    knob_pitch = _KNOB_PITCH * spacing_scale
    margin = 0.020
    if knob_count >= 2:
        max_row = body_w - 2.0 * margin
        for _ in range(60):
            row_w = (knob_count - 1) * knob_pitch + _KNOB_D
            if row_w <= max_row:
                break
            if knob_pitch > 0.045:
                knob_pitch = max(0.045, knob_pitch - 0.002)
            else:
                break

    # Knob row centered on the fascia band (door_top -> deck_top); derived from
    # the band so it scales with body_height_scale (via deck_top) and never
    # rides above the cooktop deck at low heights (was a fixed _KNOB_Z).
    knob_z = door_top + (deck_top - door_top) * 0.5

    return ResolvedStoveConfig(
        door_mechanism=door_mechanism,
        cooktop=cooktop,
        base=base,
        burner_count=burner_count,
        knob_count=knob_count,
        palette_style=palette_style,
        body_w=body_w,
        body_d=body_d,
        half_w=half_w,
        half_d=half_d,
        base_lift=base_lift,
        plinth_top=plinth_top,
        door_top=door_top,
        deck_top=deck_top,
        rim_top=rim_top,
        door_h=door_h,
        door_open_angle=door_open_angle,
        lid_open_angle=lid_open_angle,
        drawer_travel=drawer_travel,
        knob_z=knob_z,
        knob_pitch=knob_pitch,
        burner_spacing=burner_spacing,
        name=cfg.name or "stove",
    )


def with_overrides(config: StoveConfig, **kwargs: object) -> StoveConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: StoveConfig | ResolvedStoveConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedStoveConfig) else resolve_config(config)
    return (
        ("door_mechanism", r.door_mechanism),
        ("cooktop", r.cooktop),
        ("base", r.base),
        ("burner_count", f"b{r.burner_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Burner grid layout helper (absolute XY centers on the deck, by Nb).
# Source: P1 BURNER_XY 2x2 / P2 BURNER_XS x BURNER_YS grid.
# ---------------------------------------------------------------------------
def _burner_centers(n: int, spacing: float) -> list[tuple[float, float]]:
    """Absolute (x, y) burner centers on the cooktop, parameterized by Nb."""
    if n <= 0:
        return []
    dx = 0.13 * spacing  # front/back row offset along X
    dy = 0.115 * spacing  # left/right column offset along Y
    if n == 1:
        return [(0.0, 0.0)]
    if n == 2:
        return [(0.0, dy), (0.0, -dy)]
    if n == 3:
        return [(0.0, dy * 1.3), (0.0, 0.0), (0.0, -dy * 1.3)]
    if n == 4:
        return [(dx, dy), (dx, -dy), (-dx, dy), (-dx, -dy)]
    if n == 5:
        return [(dx, dy), (dx, -dy), (-dx, dy), (-dx, -dy), (0.0, 0.0)]
    # n == 6: two rows of three
    return [
        (dx, dy * 1.4), (dx, 0.0), (dx, -dy * 1.4),
        (-dx, dy * 1.4), (-dx, 0.0), (-dx, -dy * 1.4),
    ]


def _grate_half_for_centers(centers: list[tuple[float, float]]) -> float:
    """Grate half-size that tiles adjacent burners without mutual overlap."""
    min_sep = 0.30
    for a in range(len(centers)):
        for b in range(a + 1, len(centers)):
            d = math.hypot(
                centers[a][0] - centers[b][0], centers[a][1] - centers[b][1]
            )
            min_sep = min(min_sep, d)
    return min(0.075, max(0.040, min_sep / 2.0 - 0.006))


def _burner_xy(r: ResolvedStoveConfig) -> list[tuple[float, float]]:
    """Absolute (x, y) burner centers on the cooktop, parameterized by Nb."""
    return _burner_centers(r.burner_count, r.burner_spacing)


def _knob_ys(r: ResolvedStoveConfig) -> list[float]:
    """Absolute knob Y centers on the fascia (centered row of Nk knobs)."""
    n = r.knob_count
    if n <= 0:
        return []
    y0 = -0.5 * (n - 1) * r.knob_pitch
    return [y0 + i * r.knob_pitch for i in range(n)]


# ---------------------------------------------------------------------------
# body (root): plinth / base, cabinet shell, cavity walls, top housing,
# cooktop deck + rim, control fascia, fixed oven rack.
# base / cooktop slots modify the bottom and top geometry respectively.
# ---------------------------------------------------------------------------
def _build_body(model: ArticulatedObject, r: ResolvedStoveConfig, mats) -> object:
    body = model.part("body")
    bw = r.body_w
    bd = r.body_d
    z_lift = r.base_lift

    # ---- base region ----
    if r.base == "raised_legs":
        # Base plate sits at plinth_top - small, raised by legs; legs reach floor.
        body.visual(
            Box((bd, bw, 0.03)),
            origin=Origin(xyz=(0.0, 0.0, z_lift - 0.015)),
            material=mats["body"],
            name="base_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        leg_profile = [
            (0.012, -_LEG_H),
            (0.020, -_LEG_H + 0.004),
            (0.019, -_LEG_H + 0.010),
            (0.016, -_LEG_H + 0.030),
            (0.014, -_LEG_H + 0.060),
            (0.013, -_LEG_H + 0.090),
            (0.014, -0.020),
            (0.018, -0.006),
            (0.020, 0.0),
        ]
        leg_geom = LatheGeometry(leg_profile, segments=24, closed=True)
        for i, (lx, ly) in enumerate(
            [(0.26, 0.21), (0.26, -0.21), (-0.26, 0.21), (-0.26, -0.21)]
        ):
            sx = 1.0 if lx > 0 else -1.0
            sy = 1.0 if ly > 0 else -1.0
            body.visual(
                mesh_from_geometry(leg_geom.clone(), f"leg_{i}"),
                origin=Origin(
                    xyz=(lx, ly, z_lift),
                    rpy=(-sy * _LEG_SPLAY, -sx * _LEG_SPLAY, 0.0),
                ),
                material=mats["leg"],
                name=f"leg_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
            )
    elif r.base == "storage_drawer":
        # Drawer compartment enclosure: bottom plate + lower panels + oven floor
        # raised above the drawer zone. Feet at the corners.
        for i, (fx, fy) in enumerate(
            [(0.26, 0.21), (0.26, -0.21), (-0.26, 0.21), (-0.26, -0.21)]
        ):
            body.visual(
                Cylinder(radius=0.022, length=0.051),
                origin=Origin(xyz=(fx, fy, 0.0255)),
                material=mats["foot"],
                name=f"foot_{i}", material_class_id="rubber.smooth_plain",
            )
        body.visual(
            Box((bd - 0.02, bw - 0.01, 0.005)),
            origin=Origin(xyz=(0.0, 0.0, 0.048)),
            material=mats["body"],
            name="bottom_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        lower_h = r.plinth_top - 0.048
        lower_zc = 0.048 + lower_h / 2.0
        body.visual(
            Box((bd, 0.015, lower_h)),
            origin=Origin(xyz=(0.0, -r.half_w + 0.0075, lower_zc)),
            material=mats["body"],
            name="lower_panel_left", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        body.visual(
            Box((bd, 0.015, lower_h)),
            origin=Origin(xyz=(0.0, r.half_w - 0.0075, lower_zc)),
            material=mats["body"],
            name="lower_panel_right", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        body.visual(
            Box((0.015, bw - 0.03, lower_h)),
            origin=Origin(xyz=(-r.half_d + 0.0075, 0.0, lower_zc)),
            material=mats["body"],
            name="lower_panel_rear", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        body.visual(
            Box((bd - 0.04, bw - 0.03, 0.012)),
            origin=Origin(xyz=(0.0, 0.0, r.plinth_top - 0.006)),
            material=mats["body"],
            name="oven_floor", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
    else:  # plinth_kickbase
        body.visual(
            Box((bd, bw, r.plinth_top - 0.05)),
            origin=Origin(xyz=(0.0, 0.0, (r.plinth_top - 0.05) / 2.0 + 0.05)),
            material=mats["body"],
            name="plinth", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        for i, (fx, fy) in enumerate(
            [(0.26, 0.21), (0.26, -0.21), (-0.26, 0.21), (-0.26, -0.21)]
        ):
            body.visual(
                Cylinder(radius=0.022, length=0.051),
                origin=Origin(xyz=(fx, fy, 0.0255)),
                material=mats["foot"],
                name=f"foot_{i}", material_class_id="rubber.smooth_plain",
            )

    # ---- oven cavity walls (hollow box open at the front +X) ----
    # When raised on legs, extend the walls DOWN to the raised base plate so the
    # base plate + legs connect to the cabinet (no floating island).
    wall_bottom = (z_lift - 0.03) if r.base == "raised_legs" else (r.plinth_top - 0.005)
    wall_top = r.plinth_top + r.door_h
    wall_h = wall_top - wall_bottom
    wall_zc = (wall_bottom + wall_top) / 2.0
    body.visual(
        Box((bd, 0.05, wall_h)),
        origin=Origin(xyz=(0.0, -r.half_w + 0.025, wall_zc)),
        material=mats["body"],
        name="wall_left", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
    )
    body.visual(
        Box((bd, 0.05, wall_h)),
        origin=Origin(xyz=(0.0, r.half_w - 0.025, wall_zc)),
        material=mats["body"],
        name="wall_right", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
    )
    body.visual(
        Box((0.05, bw - 0.10, wall_h)),
        origin=Origin(xyz=(-r.half_d + 0.025, 0.0, wall_zc)),
        material=mats["body"],
        name="wall_rear", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
    )
    # ---- front bottom sill across the cavity opening: this is the real hinge
    #      hardware the drop-down / side / french doors anchor onto. ----
    body.visual(
        Box((0.04, bw, 0.03)),
        origin=Origin(xyz=(r.half_d - 0.02, 0.0, r.plinth_top)),
        material=mats["body"],
        name="front_sill", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
    )

    # ---- dark oven cavity liners ----
    liner_h = r.door_h
    liner_zc = r.plinth_top + liner_h / 2.0
    body.visual(
        Box((bd - 0.05, 0.005, liner_h)),
        origin=Origin(xyz=(0.0, -r.half_w + 0.0515, liner_zc)),
        material=mats["cavity"],
        name="liner_left", material_class_id="metal.blackened_gunmetal",
    )
    body.visual(
        Box((bd - 0.05, 0.005, liner_h)),
        origin=Origin(xyz=(0.0, r.half_w - 0.0515, liner_zc)),
        material=mats["cavity"],
        name="liner_right", material_class_id="metal.blackened_gunmetal",
    )
    body.visual(
        Box((0.005, bw - 0.10, liner_h)),
        origin=Origin(xyz=(-r.half_d + 0.0515, 0.0, liner_zc)),
        material=mats["cavity"],
        name="liner_rear", material_class_id="metal.blackened_gunmetal",
    )

    # ---- fixed chrome oven rack shelf inside the cavity ----
    # Spans wall-to-wall so its side edges embed into the side liners (real
    # support contact, not a floating island).
    body.visual(
        Box((bd - 0.12, 2.0 * (r.half_w - 0.050), 0.008)),
        origin=Origin(xyz=(0.0, 0.0, r.plinth_top + liner_h * 0.40)),
        material=mats["rack"],
        name="oven_rack", material_class_id="metal.chrome_polished",
    )

    # ---- top housing (under-cooktop burner box + control fascia band) ----
    housing_z0 = r.door_top + 0.0
    housing_z1 = r.deck_top
    housing_h = housing_z1 - housing_z0
    body.visual(
        Box((bd, bw, housing_h)),
        origin=Origin(xyz=(0.0, 0.0, housing_z0 + housing_h / 2.0)),
        material=mats["body"],
        name="top_housing", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
    )

    # ---- control fascia (front face of the housing, carries the knobs) ----
    body.visual(
        Box((0.012, bw * 0.96, housing_h * 0.96)),
        origin=Origin(xyz=(r.half_d - 0.006, 0.0, housing_z0 + housing_h / 2.0)),
        material=mats["panel"],
        name="control_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
    )

    # ---- cooktop deck + raised rim around the well ----
    if r.cooktop != "griddle_flat_top":
        # Recessed well: deck floor + raised perimeter rim.
        body.visual(
            Box((bd, bw, 0.008)),
            origin=Origin(xyz=(0.0, 0.0, r.deck_top - 0.004)),
            material=mats["body"],
            name="cooktop_deck", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        rim_zc = (r.deck_top + r.rim_top) / 2.0
        rim_h = r.rim_top - r.deck_top
        body.visual(
            Box((0.03, bw, rim_h)),
            origin=Origin(xyz=(r.half_d - 0.015, 0.0, rim_zc)),
            material=mats["body"],
            name="rim_front", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        body.visual(
            Box((0.03, bw, rim_h)),
            origin=Origin(xyz=(-r.half_d + 0.015, 0.0, rim_zc)),
            material=mats["body"],
            name="rim_rear", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        body.visual(
            Box((bd - 0.06, 0.03, rim_h)),
            origin=Origin(xyz=(0.0, -r.half_w + 0.015, rim_zc)),
            material=mats["body"],
            name="rim_left", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        body.visual(
            Box((bd - 0.06, 0.03, rim_h)),
            origin=Origin(xyz=(0.0, r.half_w - 0.015, rim_zc)),
            material=mats["body"],
            name="rim_right", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
    else:
        # Flat deck with a shallow recess that the griddle plate seats into.
        body.visual(
            Box((bd, bw, 0.008)),
            origin=Origin(xyz=(0.0, 0.0, r.deck_top - 0.004)),
            material=mats["body"],
            name="cooktop_deck", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )

    return body


# ---------------------------------------------------------------------------
# cooktop slot: open_burners (burners + grates) / glass_lift_lid / griddle.
# Burners + grates are body visual / FIXED grates (Rule 1, non-moving).
# ---------------------------------------------------------------------------
def _build_open_burners(model, r, body, mats) -> None:
    """Burner units (body visual) + per-burner cast-iron grate (FIXED part)."""
    centers = _burner_xy(r)
    deck = r.deck_top
    # Grate half-size adapts to the nearest neighbor spacing so adjacent grates
    # tile without overlapping each other (grid+grate deck-fit clamped in
    # resolve_config via r.burner_spacing).
    grate_h = _grate_half_for_centers(centers)
    for i, (bx, by) in enumerate(centers):
        body.visual(
            Cylinder(radius=0.055, length=0.006),
            origin=Origin(xyz=(bx, by, deck + 0.003)),
            material=mats["burner"],
            name=f"drip_cup_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        body.visual(
            Cylinder(radius=0.030, length=0.010),
            origin=Origin(xyz=(bx, by, deck + 0.011)),
            material=mats["metal"],
            name=f"burner_body_{i}", material_class_id="metal.brushed_silver",
        )
        body.visual(
            Cylinder(radius=0.022, length=0.004),
            origin=Origin(xyz=(bx, by, deck + 0.018)),
            material=mats["cap"],
            name=f"burner_cap_{i}", material_class_id="metal.brushed_silver",
        )
        # Per-burner square wire/iron grate, FIXED (non-moving, separate frame).
        # Authored in a LOCAL frame whose origin is the FIXED joint origin
        # (bx, by, rim_top): bars sit just above the rim (local z ~ 0), legs
        # reach DOWN into the deck so the grate visibly rests on the cooktop.
        grate = model.part(f"grate_{i}")
        h = grate_h
        bar_z = _GRATE_BAR / 2.0  # just above the rim, local frame
        leg_h = (r.rim_top - r.deck_top) + 0.006  # rim down into the deck
        for sx in (-h, h):
            grate.visual(
                Box((_GRATE_BAR, 2.0 * h, _GRATE_BAR)),
                origin=Origin(xyz=(sx, 0.0, bar_z)),
                material=mats["iron"],
                name=f"frame_bar_x_{'p' if sx > 0 else 'n'}", material_class_id="metal.cast_iron_bare",
            )
        for sy in (-h, h):
            grate.visual(
                Box((2.0 * h, _GRATE_BAR, _GRATE_BAR)),
                origin=Origin(xyz=(0.0, sy, bar_z)),
                material=mats["iron"],
                name=f"frame_bar_y_{'p' if sy > 0 else 'n'}", material_class_id="metal.cast_iron_bare",
            )
        for fi, fy in enumerate((-h * 0.5, 0.0, h * 0.5)):
            grate.visual(
                Box((2.0 * h, _GRATE_BAR, _GRATE_BAR)),
                origin=Origin(xyz=(0.0, fy, bar_z)),
                material=mats["iron"],
                name=f"finger_{fi}", material_class_id="metal.cast_iron_bare",
            )
        # Four short legs down to the rim so the grate visibly rests on the deck.
        for li, (lx, ly) in enumerate([(-h, -h), (-h, h), (h, -h), (h, h)]):
            grate.visual(
                Box((_GRATE_BAR, _GRATE_BAR, leg_h)),
                origin=Origin(xyz=(lx, ly, -leg_h / 2.0 + 0.002)),
                material=mats["iron"],
                name=f"leg_{li}", material_class_id="metal.cast_iron_bare",
            )
        model.articulation(
            f"grate_{i}_mount",
            ArticulationType.FIXED,
            parent=body,
            child=grate,
            origin=Origin(xyz=(bx, by, r.rim_top)),
        )


def _build_glass_lift_lid(model, r, body, mats) -> None:
    """Open burners PLUS a rear-hinged glass lift lid covering the cooktop."""
    _build_open_burners(model, r, body, mats)

    lid_depth = r.body_d * 0.86
    lid_width = r.body_w * 0.80
    lid_thick = 0.004
    trim_w = 0.006
    bracket_h = 0.015
    hinge_x = -r.half_d + 0.012
    hinge_z = r.rim_top + bracket_h

    # Hinge bracket on the rear rim (real visible steel support).
    body.visual(
        Box((0.014, lid_width + 0.02, bracket_h)),
        origin=Origin(xyz=(hinge_x, 0.0, r.rim_top + bracket_h / 2.0)),
        material=mats["metal"],
        name="lid_hinge_bracket", material_class_id="metal.brushed_silver",
    )

    lid = model.part("cooktop_lid")
    # Glass panel extends forward (+X) from the hinge in lid-local frame.
    lid.visual(
        Box((lid_depth, lid_width, lid_thick)),
        origin=Origin(xyz=(lid_depth / 2.0, 0.0, lid_thick / 2.0)),
        material=mats["glass"],
        name="lid_glass", material_class_id="glass.smoked_tinted",
    )
    lid.visual(
        Box((trim_w, lid_width + 2.0 * trim_w, trim_w)),
        origin=Origin(xyz=(lid_depth + trim_w / 2.0, 0.0, trim_w / 2.0)),
        material=mats["metal"],
        name="lid_trim_front", material_class_id="metal.brushed_silver",
    )
    lid.visual(
        Box((trim_w, lid_width + 2.0 * trim_w, trim_w)),
        origin=Origin(xyz=(-trim_w / 2.0, 0.0, trim_w / 2.0)),
        material=mats["metal"],
        name="lid_trim_rear", material_class_id="metal.brushed_silver",
    )
    lid.visual(
        Box((lid_depth + 2.0 * trim_w, trim_w, trim_w)),
        origin=Origin(xyz=(lid_depth / 2.0, -(lid_width / 2.0 + trim_w / 2.0), trim_w / 2.0)),
        material=mats["metal"],
        name="lid_trim_left", material_class_id="metal.brushed_silver",
    )
    lid.visual(
        Box((lid_depth + 2.0 * trim_w, trim_w, trim_w)),
        origin=Origin(xyz=(lid_depth / 2.0, (lid_width / 2.0 + trim_w / 2.0), trim_w / 2.0)),
        material=mats["metal"],
        name="lid_trim_right", material_class_id="metal.brushed_silver",
    )
    lid.visual(
        Box((0.012, 0.08, 0.012)),
        origin=Origin(xyz=(lid_depth + trim_w + 0.006, 0.0, lid_thick / 2.0 + 0.006)),
        material=mats["metal"],
        name="lid_handle", material_class_id="metal.brushed_silver",
    )
    model.articulation(
        "cooktop_lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        # axis -Y: positive q lifts the front edge up to expose the burners.
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=r.lid_open_angle),
    )


def _build_griddle_flat_top(model, r, body, mats) -> None:
    """A single flat teppanyaki hotplate (FIXED) replacing the burners."""
    griddle = model.part("griddle_plate")
    gw = r.body_w * 0.88
    gd = r.body_d * 0.90
    griddle_shape = (
        cq.Workplane("XY")
        .box(gd, gw, 0.012)
        .edges("|Z").fillet(0.008)
        .faces(">Z").workplane()
        .rect(gd - 0.04, gw - 0.04, forConstruction=True)
        .vertices()
        .circle(0.003)
        .cutThruAll()
    )
    # Authored in the LOCAL (FIXED joint) frame: plate centered at z=0, joint
    # origin places it on the deck so the plate seats into the recess.
    griddle.visual(
        mesh_from_cadquery(griddle_shape, "griddle_plate"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["iron"],
        name="griddle_surface", material_class_id="metal.cast_iron_bare",
    )
    model.articulation(
        "griddle_mount",
        ArticulationType.FIXED,
        parent=body,
        child=griddle,
        origin=Origin(xyz=(0.0, 0.0, r.deck_top + 0.004)),
    )


_COOKTOP_BUILDERS = {
    "open_burners": _build_open_burners,
    "glass_lift_lid": _build_glass_lift_lid,
    "griddle_flat_top": _build_griddle_flat_top,
}


# ---------------------------------------------------------------------------
# door_mechanism slot: drop_down_front / side_hinged_swing / french_double.
# All door-local frames; +X = front, door panel thickness along +X.
# ---------------------------------------------------------------------------
def _emit_drop_door(model, r, body, mats) -> None:
    """Drop-down door, bottom hinge line at the front of the plinth (REVOLUTE +Y)."""
    door = model.part("oven_door")
    door_frame = BezelGeometry(
        (r.body_w * 0.72, r.door_h * 0.62),
        (r.body_w, r.door_h),
        _DOOR_T,
        opening_shape="rounded_rect",
        outer_shape="rect",
        opening_corner_radius=0.012,
    )
    # Hinge line at the door's OUTER-bottom edge (panel authored in local
    # -X from the pivot). At open the panel swings UP-and-over the pivot instead
    # of dipping below it, so it never enters the low-front storage-drawer band
    # (drawer top < plinth_top = hinge z). All door-local X shifted back by
    # _DOOR_T vs a proud panel; handle stays proud of the front face.
    door.visual(
        mesh_from_geometry(door_frame, "oven_door_frame"),
        # bezel local X->door Y (width), Y->door Z (height), Z->door X (thickness).
        origin=Origin(xyz=(-_DOOR_T / 2.0, 0.0, r.door_h / 2.0), rpy=(math.pi / 2, 0.0, math.pi / 2)),
        material=mats["door"],
        name="door_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
    )
    door.visual(
        Box((0.012, r.body_w * 0.78, r.door_h * 0.56)),
        origin=Origin(xyz=(0.018 - _DOOR_T, 0.0, r.door_h / 2.0)),
        material=mats["glass"],
        name="window_glass", material_class_id="glass.smoked_tinted",
    )
    for si, hy in enumerate((-r.body_w * 0.36, r.body_w * 0.36)):
        door.visual(
            Cylinder(radius=0.009, length=0.030),
            origin=Origin(xyz=(0.053 - _DOOR_T, hy, r.door_h - 0.05), rpy=(0.0, math.pi / 2, 0.0)),
            material=mats["metal"],
            name=f"handle_standoff_{si}", material_class_id="metal.brushed_silver",
        )
    door.visual(
        Cylinder(radius=0.011, length=r.body_w * 0.88),
        origin=Origin(xyz=(0.072 - _DOOR_T, 0.0, r.door_h - 0.05), rpy=(math.pi / 2, 0.0, 0.0)),
        material=mats["metal"],
        name="handle_bar", material_class_id="metal.brushed_silver",
    )
    model.articulation(
        "oven_door_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=(r.half_d, 0.0, r.plinth_top)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=1.5, lower=0.0, upper=r.door_open_angle),
    )


def _emit_side_door(model, r, body, mats) -> None:
    """Side-hinged single door, left vertical jamb hinge (REVOLUTE -Z)."""
    door = model.part("oven_door")
    z_mid = r.plinth_top + r.door_h / 2.0
    hinge_y = -r.half_w + 0.005
    door_frame = BezelGeometry(
        (r.body_w * 0.72, r.door_h * 0.62),
        (r.body_w, r.door_h),
        _DOOR_T,
        opening_shape="rounded_rect",
        outer_shape="rect",
        opening_corner_radius=0.012,
    )
    # door-local: hinge line at local origin (left edge, y=0), panel extends +Y.
    door.visual(
        mesh_from_geometry(door_frame, "oven_door_frame"),
        origin=Origin(xyz=(_DOOR_T / 2.0, r.body_w / 2.0, 0.0), rpy=(math.pi / 2, 0.0, math.pi / 2)),
        material=mats["door"],
        name="door_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
    )
    door.visual(
        Box((0.012, r.body_w * 0.78, r.door_h * 0.62)),
        origin=Origin(xyz=(0.018, r.body_w / 2.0, 0.0)),
        material=mats["glass"],
        name="window_glass", material_class_id="glass.smoked_tinted",
    )
    # hinge plate + pins on the left edge engaging the body jamb cup.
    door.visual(
        Box((0.012, 0.024, r.door_h * 0.9)),
        origin=Origin(xyz=(0.012, 0.0, 0.0)),
        material=mats["metal"],
        name="hinge_plate", material_class_id="metal.brushed_silver",
    )
    for j, dz in enumerate((-r.door_h * 0.32, r.door_h * 0.32)):
        door.visual(
            Cylinder(radius=0.008, length=0.03),
            origin=Origin(xyz=(0.012, 0.0, dz)),
            material=mats["metal"],
            name=f"door_hinge_pin_{j}", material_class_id="metal.brushed_silver",
        )
    # vertical handle near the free (right) edge.
    hx = r.body_w - 0.04
    door.visual(
        Cylinder(radius=0.010, length=r.door_h * 0.5),
        origin=Origin(xyz=(0.062, hx, 0.0)),
        material=mats["metal"],
        name="handle_bar", material_class_id="metal.brushed_silver",
    )
    for j, pz in enumerate((0.08, -0.08)):
        door.visual(
            Cylinder(radius=0.007, length=0.025),
            origin=Origin(xyz=(0.04, hx, pz), rpy=(0.0, math.pi / 2, 0.0)),
            material=mats["metal"],
            name=f"handle_standoff_{j}", material_class_id="metal.brushed_silver",
        )
    # body jamb cups (real anchoring visuals on the left jamb).
    for j in range(2):
        body.visual(
            Box((0.024, 0.022, 0.05)),
            origin=Origin(xyz=(r.half_d - 0.015, hinge_y + 0.006, z_mid + (0.16 if j else -0.16))),
            material=mats["metal"],
            name=f"door_hinge_cup_{j}", material_class_id="metal.brushed_silver",
        )
    model.articulation(
        "oven_door_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=(r.half_d, hinge_y, z_mid)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=0.0, upper=r.door_open_angle),
    )


def _emit_french_door(model, r, body, mats) -> None:
    """French double door: two mirrored leaves, vertical jamb hinges (2 REVOLUTE)."""
    z_mid = r.plinth_top + r.door_h / 2.0
    leaf_w = (r.body_w - 0.003) / 2.0
    for leaf_idx in range(2):
        side = 1 if leaf_idx == 0 else -1  # +1 left (-Y jamb), -1 right (+Y jamb)
        hinge_y = -side * (r.half_w)
        axis_z = -1.0 if leaf_idx == 0 else 1.0
        name = f"door_{leaf_idx}"
        leaf = model.part(name)
        leaf_frame = BezelGeometry(
            (leaf_w * 0.62, r.door_h * 0.62),
            (leaf_w, r.door_h),
            _DOOR_T,
            opening_shape="rounded_rect",
            outer_shape="rect",
            opening_corner_radius=0.010,
        )
        # leaf-local: hinge edge at local origin; panel extends toward center.
        leaf.visual(
            mesh_from_geometry(leaf_frame, f"door_frame_{leaf_idx}"),
            origin=Origin(xyz=(_DOOR_T / 2.0, side * leaf_w / 2.0, 0.0), rpy=(math.pi / 2, 0.0, math.pi / 2)),
            material=mats["door"],
            name="door_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
        )
        leaf.visual(
            Box((0.012, leaf_w * 0.66, r.door_h * 0.6)),
            origin=Origin(xyz=(0.018, side * leaf_w / 2.0, 0.0)),
            material=mats["glass"],
            name="window_glass", material_class_id="glass.smoked_tinted",
        )
        # hinge pin on the jamb edge engaging the body barrel.
        leaf.visual(
            Cylinder(radius=0.009, length=r.door_h * 0.9),
            origin=Origin(xyz=(0.010, 0.0, 0.0)),
            material=mats["metal"],
            name="hinge_pin", material_class_id="metal.brushed_silver",
        )
        # vertical handle near the free (center) edge.
        hy = side * (leaf_w - 0.035)
        leaf.visual(
            Cylinder(radius=0.010, length=r.door_h * 0.5),
            origin=Origin(xyz=(0.062, hy, 0.0)),
            material=mats["metal"],
            name="handle_bar", material_class_id="metal.brushed_silver",
        )
        for j, pz in enumerate((0.08, -0.08)):
            leaf.visual(
                Cylinder(radius=0.007, length=0.025),
                origin=Origin(xyz=(0.04, hy, pz), rpy=(0.0, math.pi / 2, 0.0)),
                material=mats["metal"],
                name=f"handle_standoff_{j}", material_class_id="metal.brushed_silver",
            )
        # body hinge barrel on the jamb (real anchoring visual).
        body.visual(
            Cylinder(radius=0.010, length=r.door_h * 0.92),
            origin=Origin(xyz=(r.half_d - 0.010, hinge_y + side * 0.010, z_mid)),
            material=mats["metal"],
            name=f"door_hinge_barrel_{leaf_idx}", material_class_id="metal.brushed_silver",
        )
        model.articulation(
            f"door_{leaf_idx}_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=leaf,
            origin=Origin(xyz=(r.half_d, hinge_y, z_mid)),
            axis=(0.0, 0.0, axis_z),
            motion_limits=MotionLimits(effort=30.0, velocity=1.5, lower=0.0, upper=r.door_open_angle),
        )


_DOOR_EMITTERS = {
    "drop_down_front": _emit_drop_door,
    "side_hinged_swing": _emit_side_door,
    "french_double": _emit_french_door,
}


def _door_part_names(r: ResolvedStoveConfig) -> list[str]:
    if r.door_mechanism == "french_double":
        return ["door_0", "door_1"]
    return ["oven_door"]


# ---------------------------------------------------------------------------
# base slot: storage_drawer adds a PRISMATIC pull-out drawer (other bases are
# pure body visual handled in _build_body).
# ---------------------------------------------------------------------------
def _build_storage_drawer(model, r, body, mats) -> None:
    drawer = model.part("storage_drawer")
    drawer_h = r.plinth_top - 0.06
    drawer_cz = 0.048 + drawer_h / 2.0 + 0.005
    # Front panel (visible face, flush with body front).
    drawer.visual(
        Box((0.020, r.body_w - 0.05, drawer_h)),
        origin=Origin(xyz=(-0.010, 0.0, 0.0)),
        material=mats["body"],
        name="drawer_front", material_class_id=("metal.paint_coated" if r.palette_style in {"white_enamel", "matte_black_steel", "cream_retro", "glossy_red"} else "metal.stainless_matte"),
    )
    box_depth = r.body_d - 0.16
    box_width = r.body_w - 0.14
    # Box top must stay UNDER the oven floor (plinth_top): the french/side-hinged
    # door leaves have their bottom edge at plinth_top, so a box poking above it
    # gets clipped as the drawer noses out. Box top (world) = 0.058 + box_height.
    box_height = max(0.02, min(drawer_h - 0.005, r.plinth_top - 0.058 - 0.008))
    box_cx = -0.020 - box_depth / 2.0
    box_cz = -drawer_h / 2.0 + 0.005 + box_height / 2.0
    drawer.visual(
        Box((box_depth, box_width, 0.005)),
        origin=Origin(xyz=(box_cx, 0.0, -drawer_h / 2.0 + 0.0075)),
        material=mats["cavity"],
        name="drawer_bottom", material_class_id="metal.blackened_gunmetal",
    )
    for nm, dsy in (("left", -box_width / 2.0), ("right", box_width / 2.0)):
        drawer.visual(
            Box((box_depth, 0.005, box_height)),
            origin=Origin(xyz=(box_cx, dsy, box_cz)),
            material=mats["cavity"],
            name=f"drawer_side_{nm}", material_class_id="metal.blackened_gunmetal",
        )
    drawer.visual(
        Box((0.005, box_width, box_height)),
        origin=Origin(xyz=(box_cx - box_depth / 2.0 + 0.0025, 0.0, box_cz)),
        material=mats["cavity"],
        name="drawer_back", material_class_id="metal.blackened_gunmetal",
    )
    dh_z = drawer_h / 2.0 - 0.025
    for si, hy in enumerate((-0.10, 0.10)):
        drawer.visual(
            Cylinder(radius=0.007, length=0.020),
            origin=Origin(xyz=(0.010, hy, dh_z), rpy=(0.0, math.pi / 2, 0.0)),
            material=mats["metal"],
            name=f"drawer_handle_standoff_{si}", material_class_id="metal.brushed_silver",
        )
    drawer.visual(
        Cylinder(radius=0.008, length=0.24),
        origin=Origin(xyz=(0.022, 0.0, dh_z), rpy=(math.pi / 2, 0.0, 0.0)),
        material=mats["metal"],
        name="drawer_handle_bar", material_class_id="metal.brushed_silver",
    )
    # Drawer slide rails on the body (real visible support). box_cx is a
    # DRAWER-local X; the drawer joint origin sits at world x=r.half_d, so the
    # body-frame rail x = r.half_d + box_cx (else the rails project out the rear).
    # Each rail bridges from just under the drawer box side (support) outward
    # into the compartment lower side panel so it stays fixed to the body.
    rail_y_in = box_width / 2.0 - 0.006
    rail_y_out = r.half_w - 0.010  # embeds into lower_panel (inner face half_w-0.015)
    rail_w = max(0.012, rail_y_out - rail_y_in)
    rail_cy = (rail_y_in + rail_y_out) / 2.0
    for si, sy in enumerate((-1.0, 1.0)):
        body.visual(
            Box((box_depth, rail_w, 0.010)),
            origin=Origin(xyz=(r.half_d + box_cx, sy * rail_cy, drawer_cz - box_height / 2.0)),
            material=mats["metal"],
            name=f"drawer_rail_{si}", material_class_id="metal.brushed_silver",
        )
    model.articulation(
        "drawer_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=drawer,
        origin=Origin(xyz=(r.half_d, 0.0, drawer_cz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.5, lower=0.0, upper=r.drawer_travel),
    )


# ---------------------------------------------------------------------------
# burner_count multiplicity: N rotary knobs on the fascia (REVOLUTE about +X).
# Burner units themselves are emitted by the cooktop slot (body visual).
# ---------------------------------------------------------------------------
def _build_knobs(model, r, body, mats) -> None:
    ys = _knob_ys(r)
    if not ys:
        return
    knob_geo = KnobGeometry(
        _KNOB_D,
        _KNOB_H,
        body_style="skirted",
        top_diameter=0.030,
        skirt=KnobSkirt(0.048, 0.006, flare=0.08, chamfer=0.001),
        grip=KnobGrip(style="fluted", count=16, depth=0.0012),
        indicator=KnobIndicator(style="line", mode="engraved", depth=0.0008),
        center=False,  # mounting face at z=0
    )
    for i, ky in enumerate(ys):
        knob = model.part(f"knob_{i}")
        knob.visual(
            mesh_from_geometry(knob_geo.clone(), f"range_knob_{i}"),
            # knob mesh built along +Z; rotate so cap points out the front (+X).
            origin=Origin(rpy=(0.0, math.pi / 2, 0.0)),
            material=mats["knob"],
            name="knob_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        # off-axis pointer near the cap front (proves rotation).
        knob.visual(
            Box((0.004, 0.009, 0.005)),
            origin=Origin(xyz=(_KNOB_H - 0.0005, 0.0, 0.011)),
            material=mats["iron"],
            name="knob_pointer", material_class_id="metal.blackened_gunmetal",
        )
        model.articulation(
            f"knob_{i}_dial",
            ArticulationType.REVOLUTE,
            parent=body,
            child=knob,
            origin=Origin(xyz=(r.half_d, ky, r.knob_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=6.0, lower=0.0, upper=math.radians(270.0)),
        )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_stove(
    config: StoveConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"stove_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats)
    _COOKTOP_BUILDERS[r.cooktop](model, r, body, mats)
    _DOOR_EMITTERS[r.door_mechanism](model, r, body, mats)
    if r.base == "storage_drawer":
        _build_storage_drawer(model, r, body, mats)
    _build_knobs(model, r, body, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_stove(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_stove(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_stove_tests(
    object_model: ArticulatedObject,
    config: StoveConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")
    part_names = {p.name for p in object_model.parts}

    # ---- Captured-pin / cup / barrel / rail / cap overlap allowances. ----
    if r.door_mechanism == "drop_down_front":
        door = object_model.get_part("oven_door")
        ctx.allow_overlap(
            door, body,
            reason="closed drop-down door seats in the cabinet front opening.",
        )
    elif r.door_mechanism == "side_hinged_swing":
        door = object_model.get_part("oven_door")
        for pin in ("door_hinge_pin_0", "door_hinge_pin_1", "hinge_plate"):
            for j in range(2):
                ctx.allow_overlap(
                    door, body, elem_a=pin, elem_b=f"door_hinge_cup_{j}",
                    reason=f"side-hinge {pin} is captured in the left jamb cup {j}.",
                )
        ctx.allow_overlap(
            door, body,
            reason="closed side-hinge door seats in the cabinet front opening.",
        )
    else:  # french_double
        for leaf_idx in range(2):
            leaf = object_model.get_part(f"door_{leaf_idx}")
            ctx.allow_overlap(
                leaf, body, elem_a="hinge_pin", elem_b=f"door_hinge_barrel_{leaf_idx}",
                reason=f"french leaf {leaf_idx} pin is captured in its jamb barrel.",
            )
            ctx.allow_overlap(
                leaf, body,
                reason=f"closed french leaf {leaf_idx} seats in the cabinet front opening.",
            )

    # grates rest on the cooktop deck / rim, bars over the burners.
    if r.cooktop in ("open_burners", "glass_lift_lid"):
        for i in range(r.burner_count):
            grate = object_model.get_part(f"grate_{i}")
            ctx.allow_overlap(
                grate, body,
                reason=f"grate_{i} legs seat into the deck rim and bars pass over the burner cap.",
            )

    # glass lift lid seats over the cooktop footprint; trims overlap rim.
    if r.cooktop == "glass_lift_lid":
        lid = object_model.get_part("cooktop_lid")
        ctx.allow_overlap(
            lid, body,
            reason="closed lid covers the cooktop footprint and rests over the rim/grates.",
        )

    # griddle plate seats into the deck recess (laps the deck + housing top).
    if r.cooktop == "griddle_flat_top":
        griddle = object_model.get_part("griddle_plate")
        for elem_b in ("cooktop_deck", "top_housing"):
            ctx.allow_overlap(
                griddle, body, elem_a="griddle_surface", elem_b=elem_b,
                reason=f"griddle hotplate seats into the recessed cooktop {elem_b}.",
            )

    # storage drawer rides the body rails.
    if r.base == "storage_drawer":
        drawer = object_model.get_part("storage_drawer")
        ctx.allow_overlap(
            drawer, body,
            reason="storage drawer slides on its body rails and seats in the compartment.",
        )

    # knob caps seat into the fascia control panel.
    for i in range(r.knob_count):
        knob = object_model.get_part(f"knob_{i}")
        for elem_b in ("control_panel", "top_housing"):
            ctx.allow_overlap(
                knob, body, elem_a="knob_cap", elem_b=elem_b,
                reason=f"knob_{i} cap seats over its shaft boss into the fascia {elem_b}.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    ctx.check("body present", "body" in part_names, details=str(sorted(part_names)))
    aabb = ctx.part_world_aabb(body)
    if aabb is not None:
        ctx.check(
            "stove grounded at z=0",
            abs(aabb[0][2]) < 0.02,
            details=f"z_min={aabb[0][2]:.4f}",
        )

    # ---- Cooktop identity: burners OR griddle present on top. ----
    if r.cooktop == "griddle_flat_top":
        ctx.check("griddle plate present (flat top)", "griddle_plate" in part_names)
        j = object_model.get_articulation("griddle_mount")
        ctx.check(
            "griddle is FIXED",
            j.articulation_type == ArticulationType.FIXED,
            details=f"type={j.articulation_type}",
        )
    else:
        ctx.check(
            f"burner_count={r.burner_count} burner caps on the deck",
            all(
                ctx.part_element_world_aabb(body, elem=f"burner_cap_{i}") is not None
                for i in range(r.burner_count)
            ),
            details=f"Nb={r.burner_count}",
        )
        # caps sit above the deck.
        if r.burner_count >= 1:
            cap = ctx.part_element_world_aabb(body, elem="burner_cap_0")
            ctx.check(
                "burner cap sits above the cooktop deck",
                cap is not None and cap[0][2] > r.deck_top - 0.001,
                details=f"cap={cap!r} deck={r.deck_top:.3f}",
            )

    # ---- Glass lift lid: REVOLUTE -Y, lifts to expose burners. ----
    if r.cooktop == "glass_lift_lid":
        j = object_model.get_articulation("cooktop_lid_hinge")
        ctx.check(
            "cooktop lid is REVOLUTE about -Y",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        lid = object_model.get_part("cooktop_lid")
        closed = ctx.part_world_aabb(lid)
        with ctx.pose({j: r.lid_open_angle * 0.95}):
            opened = ctx.part_world_aabb(lid)
        if closed is not None and opened is not None:
            ctx.check(
                "lid lifts up to expose the burners",
                opened[1][2] > closed[1][2] + 0.05,
                details=f"closed_zmax={closed[1][2]:.3f} open_zmax={opened[1][2]:.3f}",
            )

    # ---- Door mechanism joint topology. ----
    if r.door_mechanism == "drop_down_front":
        j = object_model.get_articulation("oven_door_hinge")
        ctx.check(
            "oven door is REVOLUTE about +Y (drop-down)",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        door = object_model.get_part("oven_door")
        closed = ctx.part_world_aabb(door)
        with ctx.pose({j: r.door_open_angle * 0.95}):
            opened = ctx.part_world_aabb(door)
        if closed is not None and opened is not None:
            ctx.check(
                "drop-down door swings forward (+X) and down",
                opened[1][0] > closed[1][0] + 0.05 and opened[1][2] < closed[1][2] - 0.20,
                details=f"closed={closed!r} open={opened!r}",
            )
    elif r.door_mechanism == "side_hinged_swing":
        j = object_model.get_articulation("oven_door_hinge")
        ctx.check(
            "oven door is REVOLUTE about -Z (side hinge)",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    else:  # french_double
        j0 = object_model.get_articulation("door_0_hinge")
        j1 = object_model.get_articulation("door_1_hinge")
        ctx.check(
            "french double = 2 mirrored REVOLUTE leaves about ∓Z",
            j0.articulation_type == ArticulationType.REVOLUTE
            and j1.articulation_type == ArticulationType.REVOLUTE
            and abs(j0.axis[2]) > 0.99 and abs(j1.axis[2]) > 0.99
            and j0.axis[2] * j1.axis[2] < 0,
            details=f"l0={tuple(j0.axis)} l1={tuple(j1.axis)}",
        )

    # ---- Base: storage drawer PRISMATIC +X pulls out / legs raise body. ----
    if r.base == "storage_drawer":
        j = object_model.get_articulation("drawer_slide")
        ctx.check(
            "drawer is PRISMATIC about +X",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        drawer = object_model.get_part("storage_drawer")
        p0 = ctx.part_world_position(drawer)
        with ctx.pose({j: r.drawer_travel * 0.9}):
            p1 = ctx.part_world_position(drawer)
        if p0 is not None and p1 is not None:
            ctx.check(
                "drawer pulls out toward the user (+X)",
                p1[0] > p0[0] + 0.05,
                details=f"closed_x={p0[0]:.3f} open_x={p1[0]:.3f}",
            )
        # ---- Lock-in: the oven door(s) must never interpenetrate the storage
        #      drawer across the door swing x drawer slide (regression guard for
        #      the de-conflicted low-front door/drawer volumes). ----
        door_parts = set(_door_part_names(r))
        door_joint_names = (
            ["door_0_hinge", "door_1_hinge"]
            if r.door_mechanism == "french_double"
            else ["oven_door_hinge"]
        )
        dd_poses = []
        for da in (0.6, 0.95):
            for ds in (0.5, 1.0):
                pose = {"drawer_slide": r.drawer_travel * ds}
                for dj in door_joint_names:
                    pose[dj] = r.door_open_angle * da
                dd_poses.append(pose)
        dd_overlaps = find_geometry_overlaps_in_poses(
            object_model, poses=dd_poses, overlap_tol=0.002, validate_model=False,
        )
        dd_bad = [
            o
            for o in dd_overlaps
            if ("storage_drawer" in (o.link_a, o.link_b))
            and (o.link_a in door_parts or o.link_b in door_parts)
        ]
        ctx.check(
            "oven door clears the storage drawer across swing + slide",
            not dd_bad,
            details="; ".join(
                f"{o.link_a}/{o.link_b} depth={min(o.overlap_depth):.4f} pose={o.pose}"
                for o in dd_bad[:3]
            )
            or "no door<->drawer overlap across sampled swing+slide poses",
        )
    elif r.base == "raised_legs":
        ctx.check(
            "four retro legs raise the cabinet",
            all(f"leg_{i}" in {v.name for v in body.visuals} for i in range(4)),
            details=str(sorted(v.name for v in body.visuals if v.name.startswith("leg_"))),
        )
        if aabb is not None:
            ctx.check(
                "cabinet body bottom raised by the legs",
                aabb[0][2] < 0.03,
                details=f"z_min={aabb[0][2]:.4f}",
            )

    # ---- burner_count knobs: REVOLUTE front-normal dials in a Y row. ----
    for i in range(r.knob_count):
        j = object_model.get_articulation(f"knob_{i}_dial")
        ctx.check(
            f"knob_{i} is REVOLUTE about +X (front normal)",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    if r.knob_count >= 2:
        k0 = ctx.part_world_position(object_model.get_part("knob_0"))
        kl = ctx.part_world_position(object_model.get_part(f"knob_{r.knob_count - 1}"))
        if k0 is not None and kl is not None:
            ctx.check(
                "knobs form a horizontal row along Y",
                abs(kl[1] - k0[1]) > 0.05,
                details=f"k0_y={k0[1]:.3f} kl_y={kl[1]:.3f}",
            )
    # knob pointer swings on a half turn (proves rotation).
    if r.knob_count >= 1:
        j = object_model.get_articulation("knob_0_dial")
        knob = object_model.get_part("knob_0")
        rest = ctx.part_element_world_aabb(knob, elem="knob_pointer")
        with ctx.pose({j: math.pi}):
            flip = ctx.part_element_world_aabb(knob, elem="knob_pointer")
        if rest is not None and flip is not None:
            rest_z = (rest[0][2] + rest[1][2]) / 2.0
            flip_z = (flip[0][2] + flip[1][2]) / 2.0
            ctx.check(
                "off-axis knob pointer swings across after a half turn",
                abs(flip_z - rest_z) > 0.008,
                details=f"rest_z={rest_z:.4f} flip_z={flip_z:.4f}",
            )

    # ---- slot_choices recorded with the multiplicity axis encoded. ----
    ctx.check(
        "slot_choices recorded with door/cooktop/base/burner encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "StoveConfig",
    "ResolvedStoveConfig",
    "build_stove",
    "build_seeded_stove",
    "config_from_seed",
    "resolve_config",
    "run_stove_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
