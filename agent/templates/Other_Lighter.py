# SPDX-License-Identifier: Apache-2.0

"""Disposable / flint / piezo pocket lighter (BIC-style) — modular template.

This is the one-time-use plastic-shell pocket lighter family (NOT zippo_lighter,
which is a windproof metal flip-top with a permanent lid + fuel insert + cam).
Identity: a hollow translucent reservoir body (stadium / round / rectangular
cross-section) with a recessed valve deck, chrome flame nozzle, and a chrome
wind-guard hood band, plus a top ignition mechanism that is either a flint
spark wheel (CONTINUOUS) + fuel lever (REVOLUTE), or a single electronic piezo
push-button (PRISMATIC). Optional nozzle cap (REVOLUTE flip-top / PRISMATIC
sliding) and optional flame-height adjust thumb wheel (CONTINUOUS).

Slot graph (parallel children of root ``body``):

  body (root; body_shape decides reservoir/deck/hood cross-section)
    ├── [ignition_mechanism]  (mutually exclusive — primary mechanism)
    │     ├─ flint_spark_wheel : spark_wheel CONTINUOUS +X
    │     │                      fuel_lever  REVOLUTE  -X   (+ hood_cheeks)
    │     └─ piezo_push_button : piezo_button PRISMATIC -Z  (drops wheel+lever
    │                            +cheeks; hood gets a top plate + button_guide)
    ├── [cap]  (optional, mutually exclusive)
    │     ├─ open_hood            : (no cap part)
    │     ├─ flip_top_cap         : flip_top_cap REVOLUTE +X  (+ cap_hinge_pin)
    │     └─ sliding_nozzle_cover : nozzle_cover PRISMATIC +Y (+ slide_rail_0/1)
    └── [flame_adjust]  (optional)
          ├─ none                      : (no part)
          └─ flame_height_thumb_wheel  : flame_adjust CONTINUOUS +Z

Topology axes: ignition(2) × cap(3) × flame_adjust(2) = 12 joint-topology
classes; × body_shape(3) = 36 distinct slot-choice tuples. Captured-pin /
slide / sleeve mating is grandfathered (no MatingContract) and guarded by the
flat baseline articulation-origin check + element-scoped allow_overlap.
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
    Box,
    Cylinder,
    KnobGeometry,
    KnobGrip,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True


BodyShapeModule = Literal["stadium_oval", "round_cylindrical", "rectangular_slab"]
IgnitionModule = Literal["flint_spark_wheel", "piezo_push_button"]
CapModule = Literal["open_hood", "flip_top_cap", "sliding_nozzle_cover"]
FlameAdjustModule = Literal["none", "flame_height_thumb_wheel"]
PaletteStyle = Literal[
    "royal_blue_chrome",
    "black_chrome",
    "safety_red_piezo",
    "translucent_amber",
    "gunmetal_grey",
]

BODY_SHAPES: tuple[BodyShapeModule, ...] = (
    "stadium_oval",
    "round_cylindrical",
    "rectangular_slab",
)
IGNITIONS: tuple[IgnitionModule, ...] = ("flint_spark_wheel", "piezo_push_button")
CAPS: tuple[CapModule, ...] = ("open_hood", "flip_top_cap", "sliding_nozzle_cover")
FLAME_ADJUSTS: tuple[FlameAdjustModule, ...] = ("none", "flame_height_thumb_wheel")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "royal_blue_chrome",
    "black_chrome",
    "safety_red_piezo",
    "translucent_amber",
    "gunmetal_grey",
)


# Material role -> rgba, per palette colorway. Roles are stable across palettes
# and every .visual(material=...) references one of them via ``mats``.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "royal_blue_chrome": {
        "shell": (0.08, 0.13, 0.82, 0.88),
        "chrome": (0.82, 0.84, 0.87, 1.0),
        "steel": (0.45, 0.46, 0.48, 1.0),
        "dark": (0.27, 0.27, 0.29, 1.0),
        "deck": (0.55, 0.55, 0.56, 1.0),
        "button": (0.72, 0.12, 0.10, 1.0),
    },
    "black_chrome": {
        "shell": (0.06, 0.06, 0.07, 0.96),
        "chrome": (0.80, 0.82, 0.85, 1.0),
        "steel": (0.40, 0.41, 0.43, 1.0),
        "dark": (0.14, 0.14, 0.16, 1.0),
        "deck": (0.34, 0.34, 0.36, 1.0),
        "button": (0.85, 0.55, 0.10, 1.0),
    },
    "safety_red_piezo": {
        "shell": (0.78, 0.10, 0.10, 0.92),
        "chrome": (0.83, 0.85, 0.88, 1.0),
        "steel": (0.44, 0.45, 0.47, 1.0),
        "dark": (0.20, 0.20, 0.22, 1.0),
        "deck": (0.52, 0.52, 0.54, 1.0),
        "button": (0.10, 0.10, 0.12, 1.0),
    },
    "translucent_amber": {
        "shell": (0.86, 0.55, 0.12, 0.80),
        "chrome": (0.84, 0.86, 0.88, 1.0),
        "steel": (0.47, 0.48, 0.50, 1.0),
        "dark": (0.30, 0.22, 0.10, 1.0),
        "deck": (0.58, 0.52, 0.42, 1.0),
        "button": (0.74, 0.16, 0.12, 1.0),
    },
    "gunmetal_grey": {
        "shell": (0.30, 0.33, 0.36, 0.94),
        "chrome": (0.78, 0.80, 0.83, 1.0),
        "steel": (0.50, 0.51, 0.53, 1.0),
        "dark": (0.18, 0.19, 0.21, 1.0),
        "deck": (0.46, 0.47, 0.49, 1.0),
        "button": (0.66, 0.14, 0.12, 1.0),
    },
}

# ---- tessellation (mm-scale object: default 1 mm tolerance is far too coarse)
TOL = 5.0e-5
ANG = 0.25

# ---- nominal key dimensions (meters), shared with all 5-star sources ----
BODY_LEN = 0.0250  # plan long axis (Y)
BODY_DEP = 0.0120  # plan short axis (X)
BODY_H = 0.0640  # top rim of the reservoir
WALL = 0.0012  # reservoir wall thickness at the open top
CAVITY_DEPTH = 0.0040  # visible hollow below the rim

DECK_Z0 = 0.0595
DECK_Z1 = 0.0610

HOOD_Z0 = 0.0630
HOOD_Z1 = 0.0780

WHEEL_R = 0.0050
WHEEL_W = 0.0080
WHEEL_Y = -0.0030
WHEEL_Z = 0.0755

CHEEK_X0 = 0.0058
CHEEK_X1 = 0.0068

NOZZLE_Y = 0.0050
NOZZLE_R = 0.0015
NOZZLE_TOP = 0.0745

LEVER_PIVOT = (0.0, -0.0092, 0.0712)
LEVER_PRESS = -0.21

# flip-top cap (cap-local frame, origin at the hinge barrel centre)
HOOD_OUTER_X = BODY_DEP + 0.0012
CAP_CLEARANCE = 0.0005
CAP_WALL = 0.0010
CAP_TOP_T = 0.0012
CAP_SKIRT = 0.004
CAP_LENGTH = 0.015
CAP_X = HOOD_OUTER_X + 2 * (CAP_CLEARANCE + CAP_WALL)
CAP_OPEN_ANGLE = 2.1
HINGE_Y = 0.003
HINGE_Z = HOOD_Z1 + 0.0005
CAP_BODY_Z_TOP = -0.001
CAP_BODY_Z_BOT = CAP_BODY_Z_TOP - CAP_SKIRT

# sliding nozzle cover
COVER_L = 0.0120
COVER_W = 0.0100
COVER_T = 0.0008
SLIDE_ORIGIN_Y = 0.003
SLIDE_UPPER = 0.010
RAIL_W = 0.0010
RAIL_L = 0.0140
RAIL_H = 0.0010
RAIL_X = 0.0059
RAIL_Y = 0.006

# piezo
PLATE_THICKNESS = 0.0010
PLATE_HOLE_R = 0.0020
BUTTON_CAP_D = 0.0080
BUTTON_CAP_H = 0.0030
BUTTON_STEM_R = 0.0015
BUTTON_STEM_H = 0.0140
BUTTON_REST_GAP = 0.0020
BUTTON_TRAVEL = 0.0020
GUIDE_BOSS_R = 0.0010
GUIDE_BOSS_TOP = 0.0660

# flame adjust thumb wheel
ADJUST_Z = 0.0612
ADJUST_R_INNER = 0.00255
ADJUST_R_OUTER = 0.0044
ADJUST_H = 0.0030
ADJUST_N_TEETH = 16


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class LighterConfig:
    body_shape: BodyShapeModule | None = None
    ignition_mechanism: IgnitionModule | None = None
    cap: CapModule | None = None
    flame_adjust: FlameAdjustModule | None = None

    palette_style: PaletteStyle = "royal_blue_chrome"
    body_len_scale: float = 1.0
    body_dep_scale: float = 1.0
    body_height_scale: float = 1.0
    lid_open_angle_scale: float = 1.0
    slide_travel_scale: float = 1.0
    name: str = "lighter"


@dataclass(frozen=True)
class ResolvedLighterConfig:
    body_shape: BodyShapeModule
    ignition_mechanism: IgnitionModule
    cap: CapModule
    flame_adjust: FlameAdjustModule
    palette_style: PaletteStyle
    body_len_scale: float
    body_dep_scale: float
    body_height_scale: float
    lid_open_angle_scale: float
    slide_travel_scale: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]

    # derived dimensions
    body_len: float
    body_dep: float
    body_r: float
    hood_z1: float


# ---------------------------------------------------------------------------
# Procedural sampling — deterministic per seed
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> LighterConfig:
    rng = random.Random(seed)
    body_shape = rng.choice(BODY_SHAPES)
    ignition = rng.choice(IGNITIONS)
    cap = rng.choice(CAPS)
    flame_adjust = rng.choice(FLAME_ADJUSTS)

    body_len_scale = round(rng.uniform(0.90, 1.12), 4)
    body_dep_scale = round(rng.uniform(0.90, 1.12), 4)
    body_height_scale = round(rng.uniform(0.90, 1.10), 4)
    lid_open_angle_scale = round(rng.uniform(0.85, 1.05), 4)
    slide_travel_scale = round(rng.uniform(0.85, 1.10), 4)
    palette_style = rng.choice(PALETTE_STYLES)

    return LighterConfig(
        body_shape=body_shape,
        ignition_mechanism=ignition,
        cap=cap,
        flame_adjust=flame_adjust,
        palette_style=palette_style,
        body_len_scale=body_len_scale,
        body_dep_scale=body_dep_scale,
        body_height_scale=body_height_scale,
        lid_open_angle_scale=lid_open_angle_scale,
        slide_travel_scale=slide_travel_scale,
        name=f"seeded_lighter_{seed}",
    )


def resolve_config(config: LighterConfig) -> ResolvedLighterConfig:
    body_shape = config.body_shape or "stadium_oval"
    ignition = config.ignition_mechanism or "flint_spark_wheel"
    cap = config.cap or "open_hood"
    flame_adjust = config.flame_adjust or "none"

    if body_shape not in BODY_SHAPES:
        raise ValueError(f"Unsupported body_shape: {body_shape}")
    if ignition not in IGNITIONS:
        raise ValueError(f"Unsupported ignition_mechanism: {ignition}")
    if cap not in CAPS:
        raise ValueError(f"Unsupported cap: {cap}")
    if flame_adjust not in FLAME_ADJUSTS:
        raise ValueError(f"Unsupported flame_adjust: {flame_adjust}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    len_scale = max(0.90, min(float(config.body_len_scale), 1.12))
    dep_scale = max(0.90, min(float(config.body_dep_scale), 1.12))
    height_scale = max(0.90, min(float(config.body_height_scale), 1.10))
    # round cross-section must stay circular: X == Y footprint.
    if body_shape == "round_cylindrical":
        dep_scale = len_scale

    lid_scale = max(0.85, min(float(config.lid_open_angle_scale), 1.05))
    slide_scale = max(0.85, min(float(config.slide_travel_scale), 1.10))

    body_len = BODY_LEN * len_scale
    body_dep = BODY_DEP * dep_scale
    body_r = 0.5 * body_dep  # round body radius (X == Y)
    hood_z1 = HOOD_Z1  # height scale is applied uniformly inside builders

    return ResolvedLighterConfig(
        body_shape=body_shape,  # type: ignore[arg-type]
        ignition_mechanism=ignition,  # type: ignore[arg-type]
        cap=cap,  # type: ignore[arg-type]
        flame_adjust=flame_adjust,  # type: ignore[arg-type]
        palette_style=config.palette_style,
        body_len_scale=len_scale,
        body_dep_scale=dep_scale,
        body_height_scale=height_scale,
        lid_open_angle_scale=lid_scale,
        slide_travel_scale=slide_scale,
        name=config.name,
        palette=dict(PALETTES[config.palette_style]),
        body_len=body_len,
        body_dep=body_dep,
        body_r=body_r,
        hood_z1=hood_z1,
    )


# ---------------------------------------------------------------------------
# Shape-aware 2D profiles (reservoir / deck / hood share a profile family)
# ---------------------------------------------------------------------------
def _plan_profile(
    r: ResolvedLighterConfig, wp: cq.Workplane, long_y: float, short_x: float
) -> cq.Workplane:
    """Return a closed 2D wire on ``wp`` for the body's cross section.

    long_y / short_x are the nominal stadium long(Y)/short(X) spans; round uses
    the mean radius, rect uses square corners.
    """
    if r.body_shape == "round_cylindrical":
        return wp.circle(0.5 * short_x)
    if r.body_shape == "rectangular_slab":
        return wp.rect(short_x, long_y)
    return wp.slot2D(long_y, short_x, 90)


def _reservoir_shell(r: ResolvedLighterConfig) -> cq.Workplane:
    outer = _plan_profile(
        r, cq.Workplane("XY"), r.body_len, r.body_dep
    ).extrude(BODY_H)
    cavity = _plan_profile(
        r,
        cq.Workplane("XY").workplane(offset=BODY_H - CAVITY_DEPTH),
        r.body_len - 2 * WALL,
        r.body_dep - 2 * WALL,
    ).extrude(CAVITY_DEPTH + 0.002)
    return outer.cut(cavity)


def _valve_deck(r: ResolvedLighterConfig) -> cq.Workplane:
    return _plan_profile(
        r,
        cq.Workplane("XY").workplane(offset=DECK_Z0),
        r.body_len - 2 * WALL - 0.0004,
        r.body_dep - 2 * WALL - 0.0004,
    ).extrude(DECK_Z1 - DECK_Z0)


def _hood_band(r: ResolvedLighterConfig, *, top_plate: bool) -> cq.Workplane:
    band = _plan_profile(
        r,
        cq.Workplane("XY").workplane(offset=HOOD_Z0),
        r.body_len + 0.0012,
        r.body_dep + 0.0012,
    ).extrude(HOOD_Z1 - HOOD_Z0)
    cavity = _plan_profile(
        r,
        cq.Workplane("XY").workplane(offset=HOOD_Z0 - 0.0005),
        r.body_len - 0.0016,
        r.body_dep - 0.0016,
    ).extrude(HOOD_Z1 - HOOD_Z0 + 0.0010)
    band = band.cut(cavity)

    # Front flame notch.
    notch = cq.Workplane("XY").box(0.0070, 0.0080, 0.0090).translate((0.0, 0.0120, 0.0745))
    band = band.cut(notch)

    if not top_plate:
        # Rear band cut down so the lever pad sits exposed (flint branch).
        rear = cq.Workplane("XY").box(0.0240, 0.0070, 0.0080).translate((0.0, -0.0120, 0.0750))
        band = band.cut(rear)
    else:
        # Piezo branch: close the top with a plate drilled for the button stem.
        plate = _plan_profile(
            r,
            cq.Workplane("XY").workplane(offset=HOOD_Z1 - PLATE_THICKNESS),
            r.body_len + 0.0012,
            r.body_dep + 0.0012,
        ).extrude(PLATE_THICKNESS)
        plate_hole = (
            cq.Workplane("XY")
            .workplane(offset=HOOD_Z1 - PLATE_THICKNESS - 0.0005)
            .circle(PLATE_HOLE_R)
            .extrude(PLATE_THICKNESS + 0.001)
        )
        band = band.union(plate.cut(plate_hole))

    # Side vent perforations through both broad walls.
    vent_span = (r.body_dep + 0.004) if r.body_shape != "round_cylindrical" else 0.0120
    vents = (
        cq.Workplane("YZ")
        .pushPoints([(0.0040, 0.0735), (0.0062, 0.0735)])
        .circle(0.0007)
        .extrude(vent_span, both=True)
    )
    return band.cut(vents)


def _hood_cheeks(r: ResolvedLighterConfig) -> cq.Workplane:
    plate = cq.Workplane("XY").box(CHEEK_X1 - CHEEK_X0, 0.0125, 0.0090)
    plate = plate.edges("|X and >Z").fillet(0.0015)
    xc = 0.5 * (CHEEK_X0 + CHEEK_X1)
    return plate.translate((xc, -0.00375, 0.0745)).union(
        plate.translate((-xc, -0.00375, 0.0745))
    )


def _lever_pad() -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .polyline([(-0.0002, 0.0010), (-0.0030, 0.0010), (-0.0030, 0.0024)])
        .sagittaArc((-0.0002, 0.0028), -0.0004)
        .close()
        .extrude(0.0036, both=True)
    )


def _lever_fork() -> cq.Workplane:
    web = cq.Workplane("XY").box(0.0040, 0.0026, 0.0032).translate((0.0, 0.0015, -0.0024))
    arm = cq.Workplane("XY").box(0.0052, 0.0040, 0.0010).translate((0.0, 0.0022, -0.0041))
    prong_l = cq.Workplane("XY").box(0.0012, 0.0120, 0.0010).translate((0.0024, 0.0098, -0.0041))
    prong_r = cq.Workplane("XY").box(0.0012, 0.0120, 0.0010).translate((-0.0024, 0.0098, -0.0041))
    return web.union(arm).union(prong_l).union(prong_r)


def _flip_cap_shell() -> cq.Workplane:
    outer_z = (CAP_BODY_Z_TOP + CAP_TOP_T) - CAP_BODY_Z_BOT
    outer_zc = 0.5 * ((CAP_BODY_Z_TOP + CAP_TOP_T) + CAP_BODY_Z_BOT)
    outer = (
        cq.Workplane("XY")
        .box(CAP_X, CAP_LENGTH, outer_z)
        .translate((0.0, CAP_LENGTH / 2.0, outer_zc))
    )
    outer = outer.edges("|Z").fillet(0.002)
    inner_z = CAP_BODY_Z_TOP - CAP_BODY_Z_BOT
    inner_zc = 0.5 * (CAP_BODY_Z_TOP + CAP_BODY_Z_BOT)
    inner = (
        cq.Workplane("XY")
        .box(CAP_X - 2 * CAP_WALL, CAP_LENGTH - 2 * CAP_WALL, inner_z + 0.0002)
        .translate((0.0, CAP_LENGTH / 2.0, inner_zc - 0.0001))
    )
    shell = outer.cut(inner)
    relief_z = inner_z + 0.001
    relief_zc = 0.5 * (CAP_BODY_Z_BOT + CAP_BODY_Z_TOP)
    relief = (
        cq.Workplane("XY")
        .box(CAP_X + 0.004, 0.006, relief_z)
        .translate((0.0, 0.002, relief_zc))
    )
    return shell.cut(relief)


def _grip_ridge() -> cq.Workplane:
    return cq.Workplane("XY").box(0.0006, 0.0006, 0.0020)


def _nozzle_cover_plate() -> cq.Workplane:
    plate = cq.Workplane("XY").slot2D(COVER_L, COVER_W, 90).extrude(COVER_T)
    ridge = (
        cq.Workplane("XY")
        .workplane(offset=COVER_T)
        .rect(COVER_W * 0.45, 0.0018)
        .extrude(0.0005)
    )
    ridge = ridge.edges(">Z").fillet(0.0003)
    return plate.union(ridge.translate((0.0, 0.003, 0.0)))


def _adjust_ring() -> cq.Workplane:
    outer = cq.Workplane("XY").circle(ADJUST_R_OUTER).extrude(ADJUST_H)
    bore = cq.Workplane("XY").circle(ADJUST_R_INNER).extrude(ADJUST_H)
    ring = outer.cut(bore)
    return ring.edges(">Z or <Z").chamfer(0.0003)


def _adjust_tooth() -> cq.Workplane:
    return cq.Workplane("XY").box(0.0008, 0.0005, ADJUST_H * 0.88)


# ---------------------------------------------------------------------------
# Body builder (root) — shape + ignition decide the body part-set
# ---------------------------------------------------------------------------
def _build_body(
    model: ArticulatedObject,
    r: ResolvedLighterConfig,
    mats: dict[str, str],
    assets: AssetContext | None,
) -> None:
    piezo = r.ignition_mechanism == "piezo_push_button"
    body = model.part("body")

    body.visual(
        mesh_from_cadquery(_reservoir_shell(r), "reservoir_shell", assets=assets,
                           tolerance=TOL, angular_tolerance=ANG),
        material=mats["shell"],
        name="reservoir_shell", material_class_id="plastic.frosted_translucent",
    )
    body.visual(
        mesh_from_cadquery(_valve_deck(r), "valve_deck", assets=assets,
                           tolerance=TOL, angular_tolerance=ANG),
        material=mats["deck"],
        name="valve_deck", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Cylinder(radius=NOZZLE_R, length=NOZZLE_TOP - 0.0600),
        origin=Origin(xyz=(0.0, NOZZLE_Y, 0.5 * (NOZZLE_TOP + 0.0600))),
        material=mats["chrome"],
        name="flame_nozzle", material_class_id="metal.chrome_polished",
    )
    body.visual(
        Cylinder(radius=0.0026, length=0.0045),
        origin=Origin(xyz=(0.0, NOZZLE_Y, 0.0600 + 0.00225)),
        material=mats["chrome"],
        name="nozzle_collar", material_class_id="metal.chrome_polished",
    )
    # Flint tube directly under the spark wheel (flint branch only).
    if not piezo:
        body.visual(
            Cylinder(radius=0.0015, length=0.0098),
            origin=Origin(xyz=(0.0, WHEEL_Y, 0.0600 + 0.0049)),
            material=mats["steel"],
            name="flint_tube", material_class_id="metal.steel_bare",
        )
    body.visual(
        mesh_from_cadquery(_hood_band(r, top_plate=piezo), "hood_band", assets=assets,
                           tolerance=TOL, angular_tolerance=ANG),
        material=mats["chrome"],
        name="hood_band", material_class_id="metal.chrome_polished",
    )

    if piezo:
        # Electrode wire near the nozzle.
        electrode_len = 0.0710 - DECK_Z1
        body.visual(
            Cylinder(radius=0.0004, length=electrode_len),
            origin=Origin(xyz=(0.0030, NOZZLE_Y - 0.0020, DECK_Z1 + electrode_len / 2.0)),
            material=mats["steel"],
            name="piezo_electrode", material_class_id="metal.steel_bare",
        )
        # Guide boss on the deck (sleeve bearing for the button stem).
        guide_h = GUIDE_BOSS_TOP - DECK_Z1
        body.visual(
            Cylinder(radius=GUIDE_BOSS_R, length=guide_h),
            origin=Origin(xyz=(0.0, 0.0, DECK_Z1 + guide_h / 2.0)),
            material=mats["deck"],
            name="button_guide", material_class_id="plastic.opaque_glossy_molded",
        )
        # Vent slot decorations visible through the hood vents. Span the full
        # hood width so both ends embed into the chrome hood walls (no island).
        # Keep the Y spread small so the slots stay inside the hood footprint
        # for every body shape (the round hood is only ~body_r deep in Y).
        vent_len = r.body_dep + 0.0030
        vent_y_spread = min(0.0040, r.body_r * 0.55)
        for i in range(3):
            y = -vent_y_spread + i * vent_y_spread
            body.visual(
                Cylinder(radius=0.0006 * 0.85, length=vent_len),
                origin=Origin(xyz=(0.0, y, 0.0710), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["dark"],
                name=f"vent_slot_{i}", material_class_id="plastic.opaque_generic",
            )
    else:
        body.visual(
            mesh_from_cadquery(_hood_cheeks(r), "hood_cheeks", assets=assets,
                               tolerance=TOL, angular_tolerance=ANG),
            material=mats["chrome"],
            name="hood_cheeks", material_class_id="metal.chrome_polished",
        )


# ---------------------------------------------------------------------------
# Ignition builders
# ---------------------------------------------------------------------------
def _build_flint_spark_wheel(
    model: ArticulatedObject,
    r: ResolvedLighterConfig,
    mats: dict[str, str],
    assets: AssetContext | None,
) -> None:
    body = model.get_part("body")

    wheel = model.part("spark_wheel")
    knurl = KnobGeometry(
        2 * WHEEL_R,
        WHEEL_W,
        body_style="cylindrical",
        grip=KnobGrip(style="knurled", count=28, depth=0.0005, helix_angle_deg=25.0),
    )
    wheel.visual(
        mesh_from_geometry(knurl, "spark_wheel_knurl"),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name="wheel_knurl", material_class_id="metal.steel_bare",
    )
    wheel.visual(
        Cylinder(radius=0.0010, length=0.0136),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name="wheel_axle", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "body_to_spark_wheel",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=wheel,
        origin=Origin(xyz=(0.0, WHEEL_Y, WHEEL_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=20.0),
    )

    lever = model.part("fuel_lever")
    lever.visual(
        mesh_from_cadquery(_lever_pad(), "lever_pad", assets=assets,
                           tolerance=TOL, angular_tolerance=ANG),
        material=mats["dark"],
        name="lever_pad", material_class_id="plastic.opaque_generic",
    )
    lever.visual(
        mesh_from_cadquery(_lever_fork(), "lever_fork", assets=assets,
                           tolerance=TOL, angular_tolerance=ANG),
        material=mats["dark"],
        name="lever_fork", material_class_id="plastic.opaque_generic",
    )
    lever.visual(
        Cylinder(radius=0.0016, length=0.0052),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name="lever_boss", material_class_id="plastic.opaque_generic",
    )
    lever.visual(
        Cylinder(radius=0.0009, length=0.0134),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name="lever_pin", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "body_to_fuel_lever",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lever,
        origin=Origin(xyz=LEVER_PIVOT),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=LEVER_PRESS, upper=0.0),
    )


def _build_piezo_push_button(
    model: ArticulatedObject,
    r: ResolvedLighterConfig,
    mats: dict[str, str],
    assets: AssetContext | None,
) -> None:
    del assets
    body = model.get_part("body")
    button = model.part("piezo_button")
    button.visual(
        mesh_from_geometry(
            KnobGeometry(
                BUTTON_CAP_D, BUTTON_CAP_H, body_style="domed",
                edge_radius=0.0003, center=False,
            ),
            "button_cap",
        ),
        origin=Origin(xyz=(0.0, 0.0, BUTTON_REST_GAP)),
        material=mats["button"],
        name="button_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    stem_center_z = BUTTON_REST_GAP - BUTTON_STEM_H / 2.0
    button.visual(
        Cylinder(radius=BUTTON_STEM_R, length=BUTTON_STEM_H),
        origin=Origin(xyz=(0.0, 0.0, stem_center_z)),
        material=mats["dark"],
        name="button_stem", material_class_id="plastic.opaque_generic",
    )
    model.articulation(
        "body_to_piezo_button",
        ArticulationType.PRISMATIC,
        parent=body,
        child=button,
        origin=Origin(xyz=(0.0, 0.0, HOOD_Z1)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.5, lower=0.0, upper=BUTTON_TRAVEL),
    )


# ---------------------------------------------------------------------------
# Cap builders
# ---------------------------------------------------------------------------
def _build_open_hood(
    model: ArticulatedObject,
    r: ResolvedLighterConfig,
    mats: dict[str, str],
    assets: AssetContext | None,
) -> None:
    del model, r, mats, assets
    # No cap part — the fixed hood band is the (half-)cover.


def _build_flip_top_cap(
    model: ArticulatedObject,
    r: ResolvedLighterConfig,
    mats: dict[str, str],
    assets: AssetContext | None,
) -> None:
    body = model.get_part("body")
    # Hinge pin on the body, captured through the hood walls.
    body.visual(
        Cylinder(radius=0.0009, length=CAP_X - 0.004),
        origin=Origin(xyz=(0.0, HINGE_Y, HINGE_Z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name="cap_hinge_pin", material_class_id="metal.steel_bare",
    )
    cap = model.part("flip_top_cap")
    cap.visual(
        mesh_from_cadquery(_flip_cap_shell(), "cap_shell", assets=assets,
                           tolerance=TOL, angular_tolerance=ANG),
        material=mats["chrome"],
        name="cap_shell", material_class_id="metal.chrome_polished",
    )
    cap.visual(
        Cylinder(radius=0.0014, length=CAP_X - 0.002),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["chrome"],
        name="cap_barrel", material_class_id="metal.chrome_polished",
    )
    ridge_xs = [-0.005, -0.002, 0.002, 0.005]
    ridge_geom = _grip_ridge()
    for i, rx in enumerate(ridge_xs):
        cap.visual(
            mesh_from_cadquery(ridge_geom, f"cap_grip_{i}", assets=assets,
                               tolerance=TOL, angular_tolerance=ANG),
            origin=Origin(xyz=(rx, CAP_LENGTH + 0.0003, CAP_BODY_Z_TOP - CAP_SKIRT / 2)),
            material=mats["chrome"],
            name=f"cap_grip_{i}", material_class_id="metal.chrome_polished",
        )
    upper = min(CAP_OPEN_ANGLE * r.lid_open_angle_scale, math.pi * 0.7)
    model.articulation(
        "body_to_flip_cap",
        ArticulationType.REVOLUTE,
        parent=body,
        child=cap,
        origin=Origin(xyz=(0.0, HINGE_Y, HINGE_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=upper),
    )


def _build_sliding_nozzle_cover(
    model: ArticulatedObject,
    r: ResolvedLighterConfig,
    mats: dict[str, str],
    assets: AssetContext | None,
) -> None:
    body = model.get_part("body")
    for sign, idx in ((+1.0, 0), (-1.0, 1)):
        body.visual(
            Box((RAIL_W, RAIL_L, RAIL_H)),
            origin=Origin(xyz=(sign * RAIL_X, RAIL_Y, HOOD_Z1 + RAIL_H / 2.0)),
            material=mats["chrome"],
            name=f"slide_rail_{idx}", material_class_id="metal.chrome_polished",
        )
    cover = model.part("nozzle_cover")
    cover.visual(
        mesh_from_cadquery(_nozzle_cover_plate(), "nozzle_cover_plate", assets=assets,
                           tolerance=TOL, angular_tolerance=ANG),
        material=mats["chrome"],
        name="cover_plate", material_class_id="metal.chrome_polished",
    )
    upper = SLIDE_UPPER * r.slide_travel_scale
    model.articulation(
        "body_to_nozzle_cover",
        ArticulationType.PRISMATIC,
        parent=body,
        child=cover,
        origin=Origin(xyz=(0.0, SLIDE_ORIGIN_Y, HOOD_Z1)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.5, lower=0.0, upper=upper),
    )


# ---------------------------------------------------------------------------
# Flame-adjust builders
# ---------------------------------------------------------------------------
def _build_flame_adjust_none(
    model: ArticulatedObject,
    r: ResolvedLighterConfig,
    mats: dict[str, str],
    assets: AssetContext | None,
) -> None:
    del model, r, mats, assets


def _build_flame_height_thumb_wheel(
    model: ArticulatedObject,
    r: ResolvedLighterConfig,
    mats: dict[str, str],
    assets: AssetContext | None,
) -> None:
    body = model.get_part("body")
    flame_adjust = model.part("flame_adjust")
    flame_adjust.visual(
        mesh_from_cadquery(_adjust_ring(), "adjust_ring", assets=assets,
                           tolerance=TOL, angular_tolerance=ANG),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["steel"],
        name="adjust_ring", material_class_id="metal.steel_bare",
    )
    tooth_mesh = mesh_from_cadquery(_adjust_tooth(), "adjust_tooth", assets=assets,
                                    tolerance=TOL, angular_tolerance=ANG)
    for i in range(ADJUST_N_TEETH):
        angle = 2.0 * math.pi * i / ADJUST_N_TEETH
        rad = ADJUST_R_OUTER - 0.0002
        tx = rad * math.cos(angle)
        ty = rad * math.sin(angle)
        flame_adjust.visual(
            tooth_mesh,
            origin=Origin(xyz=(tx, ty, ADJUST_H / 2.0), rpy=(0.0, 0.0, angle)),
            material=mats["steel"],
            name=f"adjust_tooth_{i}", material_class_id="metal.steel_bare",
        )
    model.articulation(
        "body_to_flame_adjust",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=flame_adjust,
        origin=Origin(xyz=(0.0, NOZZLE_Y, ADJUST_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.5, velocity=10.0),
    )


IGNITION_FACTORIES = {
    "flint_spark_wheel": _build_flint_spark_wheel,
    "piezo_push_button": _build_piezo_push_button,
}
CAP_FACTORIES = {
    "open_hood": _build_open_hood,
    "flip_top_cap": _build_flip_top_cap,
    "sliding_nozzle_cover": _build_sliding_nozzle_cover,
}
FLAME_ADJUST_FACTORIES = {
    "none": _build_flame_adjust_none,
    "flame_height_thumb_wheel": _build_flame_height_thumb_wheel,
}


def _slot_choices_for_resolved(r: ResolvedLighterConfig) -> list[tuple[str, str]]:
    return [
        ("body_shape", r.body_shape),
        ("ignition_mechanism", r.ignition_mechanism),
        ("cap", r.cap),
        ("flame_adjust", r.flame_adjust),
    ]


def build_lighter(
    config: LighterConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    mats: dict[str, str] = {}
    for role, rgba in r.palette.items():
        mats[role] = model.material(f"lighter_{role}", rgba=rgba)

    _build_body(model, r, mats, assets)
    IGNITION_FACTORIES[r.ignition_mechanism](model, r, mats, assets)
    CAP_FACTORIES[r.cap](model, r, mats, assets)
    FLAME_ADJUST_FACTORIES[r.flame_adjust](model, r, mats, assets)

    model.meta["slot_choices"] = _slot_choices_for_resolved(r)
    return model


def build_seeded_lighter(seed: int) -> ArticulatedObject:
    return build_lighter(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return _slot_choices_for_resolved(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _visual_names(part) -> set[str]:
    return {v.name for v in part.visuals if v.name}


def _allow_if_present(
    ctx: TestContext,
    model: ArticulatedObject,
    parent_name: str,
    child_name: str,
    elem_a: str,
    elem_b: str,
    *,
    reason: str,
) -> None:
    part_names = {p.name for p in model.parts}
    if parent_name not in part_names or child_name not in part_names:
        return
    parent = model.get_part(parent_name)
    child = model.get_part(child_name)
    if elem_a in _visual_names(parent) and elem_b in _visual_names(child):
        ctx.allow_overlap(parent, child, elem_a=elem_a, elem_b=elem_b, reason=reason)


def _declare_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    # Flint spark-wheel axle captured between the chrome cheek plates / hood walls.
    _allow_if_present(ctx, model, "spark_wheel", "body", "wheel_axle", "hood_cheeks",
                      reason="spark-wheel axle pin press-fit into the chrome cheek plates")
    _allow_if_present(ctx, model, "spark_wheel", "body", "wheel_axle", "hood_band",
                      reason="axle ends pass through the hood side walls behind the cheeks")
    # The knurled wheel is captured in the hood opening, flanked by the cheeks;
    # on the narrow round hood its rim grazes the chrome hood/cheek walls.
    _allow_if_present(ctx, model, "spark_wheel", "body", "wheel_knurl", "hood_cheeks",
                      reason="knurled spark wheel is captured between the chrome cheek plates")
    _allow_if_present(ctx, model, "spark_wheel", "body", "wheel_knurl", "hood_band",
                      reason="knurled spark wheel sits in the hood opening, grazing the hood wall")
    # Fuel-lever pivot pin captured in the cheeks / hood walls.
    _allow_if_present(ctx, model, "fuel_lever", "body", "lever_pin", "hood_cheeks",
                      reason="fuel-lever pivot pin captured in the cheek plates")
    _allow_if_present(ctx, model, "fuel_lever", "body", "lever_pin", "hood_band",
                      reason="lever pivot pin passes through the hood wall behind the cheeks")
    # Piezo stem slides over the deck guide boss (sleeve bearing).
    _allow_if_present(ctx, model, "piezo_button", "body", "button_stem", "button_guide",
                      reason="button stem slides over the guide post (sleeve bearing fit)")
    # Flip cap hinge barrel wraps the body hinge pin / hood wall (captured pin).
    _allow_if_present(ctx, model, "flip_top_cap", "body", "cap_barrel", "cap_hinge_pin",
                      reason="flip-cap hinge barrel wraps around the body hinge pin")
    _allow_if_present(ctx, model, "flip_top_cap", "body", "cap_barrel", "hood_band",
                      reason="cap hinge barrel passes through the hood wall at the hinge line")
    # Sliding cover plate rests flush on the hood top (sliding contact).
    _allow_if_present(ctx, model, "nozzle_cover", "body", "cover_plate", "hood_band",
                      reason="nozzle cover plate slides flush on the hood top ring")
    _allow_if_present(ctx, model, "nozzle_cover", "body", "cover_plate", "slide_rail_0",
                      reason="cover plate is guided between the slide rails")
    _allow_if_present(ctx, model, "nozzle_cover", "body", "cover_plate", "slide_rail_1",
                      reason="cover plate is guided between the slide rails")
    # Flame-adjust ring sleeves over the nozzle collar (captured sleeve).
    _allow_if_present(ctx, model, "flame_adjust", "body", "adjust_ring", "nozzle_collar",
                      reason="adjust ring bore sleeves over the nozzle collar")


def _expect_identity(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedLighterConfig
) -> None:
    part_names = {p.name for p in model.parts}
    ctx.check("has_body", "body" in part_names, str(part_names))

    if r.ignition_mechanism == "flint_spark_wheel":
        ctx.check("flint_has_wheel_lever",
                  {"spark_wheel", "fuel_lever"} <= part_names, str(part_names))
        ctx.check("flint_has_no_button", "piezo_button" not in part_names, str(part_names))
        wj = model.get_articulation("body_to_spark_wheel")
        lj = model.get_articulation("body_to_fuel_lever")
        ctx.check("spark_wheel_continuous_x",
                  wj.articulation_type == ArticulationType.CONTINUOUS
                  and abs(wj.axis[0]) > 0.99,
                  f"type={wj.articulation_type} axis={wj.axis}")
        lim = lj.motion_limits
        ctx.check("fuel_lever_revolute",
                  lj.articulation_type == ArticulationType.REVOLUTE
                  and lim is not None and lim.lower is not None
                  and abs(lim.lower + 0.21) < 1e-6 and abs(lj.axis[0]) > 0.99,
                  f"type={lj.articulation_type} axis={lj.axis} lower={lim.lower if lim else None}")
    else:
        ctx.check("piezo_has_button", "piezo_button" in part_names, str(part_names))
        ctx.check("piezo_drops_wheel_lever_cheeks",
                  "spark_wheel" not in part_names and "fuel_lever" not in part_names
                  and "hood_cheeks" not in _visual_names(model.get_part("body")),
                  str(part_names))
        bj = model.get_articulation("body_to_piezo_button")
        lim = bj.motion_limits
        ctx.check("piezo_prismatic_negz",
                  bj.articulation_type == ArticulationType.PRISMATIC
                  and abs(bj.axis[2] + 1.0) < 1e-6,
                  f"type={bj.articulation_type} axis={bj.axis}")
        ctx.check("piezo_travel",
                  lim is not None and lim.upper is not None and 0.001 <= lim.upper <= 0.005,
                  f"upper={lim.upper if lim else None}")

    if r.cap == "flip_top_cap":
        cj = model.get_articulation("body_to_flip_cap")
        lim = cj.motion_limits
        ctx.check("flip_cap_revolute_x",
                  cj.articulation_type == ArticulationType.REVOLUTE
                  and abs(cj.axis[0]) > 0.99
                  and lim is not None and lim.upper is not None and lim.upper > 1.5,
                  f"type={cj.articulation_type} axis={cj.axis} upper={lim.upper if lim else None}")
    elif r.cap == "sliding_nozzle_cover":
        nj = model.get_articulation("body_to_nozzle_cover")
        lim = nj.motion_limits
        ctx.check("slide_prismatic_y",
                  nj.articulation_type == ArticulationType.PRISMATIC
                  and abs(nj.axis[1] - 1.0) < 1e-6
                  and lim is not None and lim.upper is not None and lim.upper >= 0.008,
                  f"type={nj.articulation_type} axis={nj.axis} upper={lim.upper if lim else None}")

    if r.flame_adjust == "flame_height_thumb_wheel":
        aj = model.get_articulation("body_to_flame_adjust")
        ctx.check("adjust_continuous_z",
                  aj.articulation_type == ArticulationType.CONTINUOUS
                  and abs(aj.axis[2] - 1.0) < 1e-6,
                  f"type={aj.articulation_type} axis={aj.axis}")


def _expect_size(ctx: TestContext, model: ArticulatedObject) -> None:
    body = model.get_part("body")
    shell = ctx.part_element_world_aabb(body, elem="reservoir_shell")
    if shell is None:
        return
    sx = shell[1][0] - shell[0][0]
    sy = shell[1][1] - shell[0][1]
    sz = shell[1][2] - shell[0][2]
    ctx.check(
        "pocket_lighter_scale",
        0.009 <= sx <= 0.020 and 0.009 <= sy <= 0.030 and 0.055 <= sz <= 0.075,
        f"shell extents x={sx:.4f} y={sy:.4f} z={sz:.4f}",
    )


def run_lighter_tests(
    model: ArticulatedObject,
    config: LighterConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    _declare_expected_overlaps(ctx, model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    _expect_identity(ctx, model, r)
    _expect_size(ctx, model)
    return ctx.report()


__all__ = [
    "__modular__",
    "LighterConfig",
    "ResolvedLighterConfig",
    "config_from_seed",
    "resolve_config",
    "build_lighter",
    "build_seeded_lighter",
    "slot_choices_for_seed",
    "run_lighter_tests",
]
