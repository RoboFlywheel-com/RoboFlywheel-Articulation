# SPDX-License-Identifier: Apache-2.0

"""Tripod turnstile procedural template (picture 小类 ``Other/Tripod Turnstile``).

Implements ``articraft_template_authoring/specs_modular_v1/Other_Tripod_Turnstile.md``.

Identity invariant
------------------
Every seed is a waist-high (~1 m) access-control tripod turnstile: a fixed
ground-mounted ``cabinet`` (frame) carries one or more rotor hubs, each bearing
``arm_count`` evenly-spaced radial cone arms that spin CONTINUOUSLY about an
inclined axis so a pedestrian pushes the arms round to pass.  The canonical
seed is the three-arm single hub.

Two structurally distinct mount families (both real, from the two root seeds):

* ``side_face_outward`` (S1 stainless, ``rec_stainless-…_ea880fc3``): the central
  head carries a hub on its LEFT and/or RIGHT side face; the hub axis points
  outward sideways and tilts UP ~28 deg.  hub_count ∈ {1, 2} (a side has only
  two faces).
* ``front_face_downforward`` (S2 model-a, ``rec_model-a-…_35b5d879``): one (or a
  row of) pedestal(s) each carry a hub on the FRONT 45-deg chamfer face; the
  hub axis points forward and tilts DOWN ~45 deg.  hub_count ∈ [1, 6] (a row of
  pedestals).  Distinct mount math — never reuse the side-mount rpy here.

Slots (spec ``pattern = mixed``)
--------------------------------
* Slot A ``pedestal_form``  -> the static ``cabinet`` root geometry
  (rect_cabinet_head S1 / stepped_chamfer_cabinet S2 / round_post S3 /
  slanted_optical_head S4).  All non-articulating structure is fused as
  ``cabinet.visual(...)`` per Rule 1.
* Slot B ``rotor_mount``    -> boss face(s) + the hub axis (side / front above).
* Slot C ``arm_mechanism``  -> the hub part (continuous_rotation S1) optionally
  with an anti-panic drop carrier (anti_panic_drop_arm S7, +REVOLUTE drop).
* Slot D ``barrier``        -> optional self-standing lane guides (tube_railings
  S1 / extended_guide_railings S6 / glass_swing_panel S5 REVOLUTE Z / none).

Adopted sources
---------------
S1 rec_stainless-…_ea880fc3 : core base, side-mount hub, cone arms, tube
   railings, rpy math (``_axis_rpy`` / ``_rpy_to_matrix``).
S2 rec_model-a-…_35b5d879   : stepped chamfer cabinet, front-mount hub, granite
   overhang top, side card reader (model-a appearance fold-in).
S3 round_post / S4 slanted_optical_head : extra pedestal forms.
S5 glass_swing_panel / S6 extended_guide_railings : extra barriers.
S7 anti_panic_drop_arm : drop carrier REVOLUTE on top of the CONTINUOUS spin.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    DomeGeometry,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Enum domains
# --------------------------------------------------------------------------- #

PedestalForm = Literal[
    "rect_cabinet_head",
    "stepped_chamfer_cabinet",
    "round_post",
    "slanted_optical_head",
]
RotorMount = Literal["side_face_outward", "front_face_downforward"]
BankStyle = Literal["uniform_single", "twin", "ends_in_middle_double"]
ArmMechanism = Literal["continuous_rotation", "anti_panic_drop_arm"]
ArmSplay = Literal["up", "down"]
Barrier = Literal[
    "tube_railings",
    "glass_swing_panel",
    "extended_guide_railings",
    "none",
]
TopPlate = Literal["dark_sloped_cap", "granite_overhang", "flat_steel"]
ReaderModule = Literal["front_fascia_rfid", "side_card_reader"]
PaletteStyle = Literal[
    "brushed_stainless",
    "stainless_granite",
    "painted_dark",
    "polished_chrome",
    "white_powdercoat",
]

PEDESTAL_FORMS: tuple[PedestalForm, ...] = (
    "rect_cabinet_head",
    "stepped_chamfer_cabinet",
    "round_post",
    "slanted_optical_head",
)
ROTOR_MOUNTS: tuple[RotorMount, ...] = (
    "side_face_outward",
    "front_face_downforward",
)
BANK_STYLES: tuple[BankStyle, ...] = (
    "uniform_single",
    "twin",
    "ends_in_middle_double",
)
ARM_MECHANISMS: tuple[ArmMechanism, ...] = (
    "continuous_rotation",
    "anti_panic_drop_arm",
)
BARRIERS: tuple[Barrier, ...] = (
    "tube_railings",
    "glass_swing_panel",
    "extended_guide_railings",
    "none",
)
TOP_PLATES: tuple[TopPlate, ...] = (
    "dark_sloped_cap",
    "granite_overhang",
    "flat_steel",
)
READER_MODULES: tuple[ReaderModule, ...] = (
    "front_fascia_rfid",
    "side_card_reader",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_stainless",
    "stainless_granite",
    "painted_dark",
    "polished_chrome",
    "white_powdercoat",
)


SOURCE_INDEX = {
    "S1": (
        "data/records/rec_stainless-steel-waist-high-tripod-turnstile-acce_"
        "20260612_133446_998781_ea880fc3/revisions/rev_000001/model.py:L102-L425"
    ),
    "S2": (
        "data/records/rec_model-a-waist-high-tripod-turnstile-for-access-c_"
        "20260610_084635_596430_35b5d879/revisions/rev_000001/model.py:L39-L210"
    ),
    "S3": (
        "data/records/rec_variant-pedestal-form-round-post-replace-the-rec_"
        "20260617_130720_143696_fccb7b6c/revisions/rev_000001/model.py:L93-L131"
    ),
    "S4": (
        "data/records/rec_variant-pedestal-form-slanted-optical-head-repla_"
        "20260617_130720_147451_e0cb8f21/revisions/rev_000001/model.py:L127-L159"
    ),
    "S5": (
        "data/records/rec_variant-barrier-glass-swing-panel-replace-the-tu_"
        "20260617_131222_754305_091848cd/revisions/rev_000001/model.py:L330-L423"
    ),
    "S6": (
        "data/records/rec_variant-barrier-extended-guide-railings-extend-t_"
        "20260617_131841_641231_dcc77210/revisions/rev_000001/model.py:L172-L431"
    ),
    "S7": (
        "data/records/rec_variant-arm-mechanism-anti-panic-drop-arm-make-t_"
        "20260617_131919_219282_e7cf9f83/revisions/rev_000001/model.py:L178-L445"
    ),
}


# --------------------------------------------------------------------------- #
# Palettes — drive every material=mats[...] off the per-seed palette_style.
# Colors are drawn from S1 (L270-276) and S2 (L131-136).
# --------------------------------------------------------------------------- #

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_stainless": {
        "body": (0.64, 0.65, 0.665, 1.0),
        "body_dark": (0.40, 0.41, 0.43, 1.0),
        "chrome": (0.79, 0.81, 0.835, 1.0),
        "top": (0.17, 0.18, 0.19, 1.0),
        "reader": (0.045, 0.045, 0.05, 1.0),
        "led": (0.15, 0.84, 0.28, 1.0),
        "glass": (0.55, 0.72, 0.78, 0.42),
        "arm": (0.79, 0.81, 0.835, 1.0),
    },
    "stainless_granite": {
        "body": (0.615, 0.625, 0.635, 1.0),
        "body_dark": (0.36, 0.37, 0.39, 1.0),
        "chrome": (0.84, 0.86, 0.88, 1.0),
        "top": (0.13, 0.13, 0.14, 1.0),
        "reader": (0.055, 0.055, 0.06, 1.0),
        "led": (0.82, 0.16, 0.10, 1.0),
        "glass": (0.52, 0.70, 0.76, 0.42),
        "arm": (0.84, 0.86, 0.88, 1.0),
    },
    "painted_dark": {
        "body": (0.16, 0.17, 0.19, 1.0),
        "body_dark": (0.085, 0.09, 0.10, 1.0),
        "chrome": (0.70, 0.72, 0.75, 1.0),
        "top": (0.07, 0.07, 0.08, 1.0),
        "reader": (0.03, 0.03, 0.035, 1.0),
        "led": (0.84, 0.62, 0.12, 1.0),
        "glass": (0.40, 0.55, 0.62, 0.40),
        "arm": (0.74, 0.76, 0.79, 1.0),
    },
    "polished_chrome": {
        "body": (0.80, 0.82, 0.85, 1.0),
        "body_dark": (0.50, 0.52, 0.55, 1.0),
        "chrome": (0.88, 0.90, 0.93, 1.0),
        "top": (0.20, 0.21, 0.22, 1.0),
        "reader": (0.05, 0.05, 0.055, 1.0),
        "led": (0.18, 0.62, 0.90, 1.0),
        "glass": (0.58, 0.74, 0.80, 0.40),
        "arm": (0.88, 0.90, 0.93, 1.0),
    },
    "white_powdercoat": {
        "body": (0.90, 0.90, 0.89, 1.0),
        "body_dark": (0.62, 0.63, 0.63, 1.0),
        "chrome": (0.82, 0.84, 0.86, 1.0),
        "top": (0.22, 0.23, 0.25, 1.0),
        "reader": (0.06, 0.06, 0.065, 1.0),
        "led": (0.15, 0.78, 0.34, 1.0),
        "glass": (0.55, 0.72, 0.78, 0.42),
        "arm": (0.82, 0.84, 0.86, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Shared geometry constants (from the source seeds).
# World frame: +X = right, +Y = toward the walker (lane along Y), +Z = up.
# --------------------------------------------------------------------------- #

# Cone arms (S1 / S2 share the 45 deg cone, tube + dome cap).
CONE = math.radians(45.0)
_CB = math.cos(CONE)
_SB = math.sin(CONE)
ARM_R = 0.020
ARM_L_BASE = 0.45
ARM_START_Z = 0.030  # local along hub +Z, just outboard of the collar face

# Hub collar / disc (S1 _hub_mesh).
HUB_COLLAR_R = 0.034
HUB_DISC_R = 0.052

# Pawl/boss seating geometry.
BOSS_R = 0.040
# Anti-panic drop tilts the whole rotor about a horizontal axis through the hub
# centre, so the arm cone sweeps across the FIXED bearing boss at its outboard
# rim.  Recess the boss face this far into the pedestal for the drop mechanism
# so the fully-dropped arms clear the rim; the hub collar/disc still cover it and
# the captured drop-carrier barrel still seats on the (recessed) boss face.
BOSS_RECESS = 0.012

# Granite top slab overhang past the head band (per side).  A flush outer rail
# has to clear this, so it is a single-sourced constant shared by _add_top_plate
# and _ped_base_half.
GRANITE_OVERHANG = 0.035

# --------------------------------------------------------------------------- #
# Lane semantics.  A tripod turnstile is a CONTROLLED SINGLE-PERSON PASSAGE: a
# person-width lane (gap along X) that the blocking arm crosses at waist height,
# with an opposing fixed element (guide rail / adjacent pedestal) across the
# lane.  Guide rails ALWAYS run with long axis along Y (the travel direction).
# --------------------------------------------------------------------------- #
LANE_W = 0.55  # target person-width lane gap (along X); accepted band 0.45-0.65
LANE_W_MIN = 0.45
LANE_W_MAX = 0.65
WAIST_Z_LO = 0.70
WAIST_Z_HI = 1.00
# Glass swing gate: centered hinge post placed this far IN FRONT (+Y) of the
# turnstile; leaves swing across the lane.
GATE_FRONT_Y = 0.42
BASE_PLATE_Z = 0.022  # thin floor/installation base plate the whole bank sits on

# Side-mount hub band.  arm_splay="up": hub mid-height, arms splay UP (cross-arm
# reaches waist).  arm_splay="down": hub raised near the pedestal top so the
# (near-horizontal) cross-arm blocks at waist while the other arms angle DOWN.
SIDE_HUB_Z = 0.66
SIDE_HUB_Z_DOWN = 0.70  # down-splay: on the upper body, NOT at the cap
SIDE_STANDOFF = 0.055

# Front-mount chamfer-face anchor (model-a S2).
_C45 = math.sqrt(0.5)
FRONT_ANCHOR = (0.0, 0.14, 0.81)
FRONT_STANDOFF = 0.055
FRONT_ROT_RPY = (-3.0 * math.pi / 4.0, 0.0, 0.0)  # maps local +Z -> (0,c,-c)


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TripodTurnstileConfig:
    pedestal_form: PedestalForm = "rect_cabinet_head"
    rotor_mount: RotorMount = "side_face_outward"
    bank_style: BankStyle = "uniform_single"
    arm_mechanism: ArmMechanism = "continuous_rotation"
    barrier: Barrier = "tube_railings"
    top_plate: TopPlate = "dark_sloped_cap"
    reader_module: ReaderModule = "front_fascia_rfid"
    palette_style: PaletteStyle = "brushed_stainless"
    hub_count: int = 2
    arm_count: int = 3
    hub_tilt_deg: float = 28.0
    arm_rest_phase_deg: float = 0.0
    pedestal_width_scale: float = 1.0
    arm_reach_scale: float = 1.0  # arm FILL fraction of the feasible lane reach
    lane_width: float = 0.55  # single-arm lane width; double-arm lanes use 2x this
    arm_splay: ArmSplay = "up"  # whole-rotor orientation: arms splay up / down
    name: str = "reference_tripod_turnstile"


@dataclass(frozen=True)
class ResolvedTripodTurnstileConfig:
    pedestal_form: PedestalForm
    rotor_mount: RotorMount
    bank_style: BankStyle
    arm_mechanism: ArmMechanism
    barrier: Barrier
    top_plate: TopPlate
    reader_module: ReaderModule
    palette_style: PaletteStyle
    hub_count: int
    arm_count: int
    hub_tilt_deg: float
    arm_rest_phase_deg: float
    pedestal_width_scale: float
    arm_reach_scale: float
    lane_width: float
    arm_splay: ArmSplay
    # derived
    arm_l: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]
    hub_world: list[dict] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _require(value: str, allowed: tuple[str, ...], *, field_name: str) -> str:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {allowed}, got {value!r}")
    return value


def _rpy_to_matrix(rpy: tuple[float, float, float]) -> list[list[float]]:
    r, p, y = rpy
    cr, sr = math.cos(r), math.sin(r)
    cp, sp = math.cos(p), math.sin(p)
    cy, sy = math.cos(y), math.sin(y)
    return [
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr],
    ]


def _matvec(m: list[list[float]], v: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
    )


def _axis_rpy(axis: tuple[float, float, float]) -> tuple[float, float, float]:
    """RPY (Rz*Ry*Rx) that maps local +Z onto the given unit axis."""
    ax, ay, az = axis
    pitch = math.acos(max(-1.0, min(1.0, az)))
    yaw = math.atan2(ay, ax)
    return (0.0, pitch, yaw)


def _register_materials(
    model: ArticulatedObject,
    palette: dict[str, tuple[float, float, float, float]],
) -> dict[str, object]:
    return {name: model.material(f"tt_{name}", color=rgba) for name, rgba in palette.items()}


def _arm_phases(count: int) -> list[float]:
    """Evenly-spaced arm phases (deg).  arm_0 is the blocking arm."""
    return [90.0 + 360.0 * i / count for i in range(count)]


# --------------------------------------------------------------------------- #
# Cached meshes for the cone arm + hub (these are the most expensive bits).
# --------------------------------------------------------------------------- #


def _arm_mesh(name: str, arm_l: float):
    """One tube arm with a domed end cap, authored along local +Z (S1/S2)."""
    tube = cq.Solid.makeCylinder(ARM_R, arm_l, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    cap = cq.Solid.makeSphere(ARM_R, cq.Vector(0.0, 0.0, arm_l), angleDegrees1=-90)
    solid = cq.Workplane(obj=tube).union(cq.Workplane(obj=cap))
    return mesh_from_cadquery(solid, name, tolerance=0.0007, angular_tolerance=0.1)


def _hub_mesh(name: str):
    """Rotor hub: seating collar + front cover disc, along local +Z (S1)."""
    collar = cq.Workplane("XY", origin=(0.0, 0.0, -0.004)).circle(HUB_COLLAR_R).extrude(0.030)
    disc = cq.Workplane("XY", origin=(0.0, 0.0, 0.026)).circle(HUB_DISC_R).extrude(0.032)
    return mesh_from_cadquery(collar.union(disc), name, tolerance=0.0007, angular_tolerance=0.1)


# --------------------------------------------------------------------------- #
# config_from_seed — deterministic procedural sampling (Contract 4)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> TripodTurnstileConfig:
    rng = random.Random(seed)

    # (1) rotor_mount: side_face_outward is the ONLY valid lane mount — the
    # pedestal sits BESIDE the lane and the arm reaches ACROSS it, so a person
    # walks the lane past the pedestal.  (front_face_downforward put the pedestal
    # in the MIDDLE of the corridor, blocking the walk path, so it is not sampled.)
    rotor_mount = "side_face_outward"

    # (2) hub_count = number of LANES (weighted toward small N).
    hub_count = rng.choices((1, 2, 3, 4, 5), weights=(0.34, 0.30, 0.16, 0.12, 0.08), k=1)[0]
    hub_tilt_deg = round(rng.uniform(20.0, 35.0), 2)

    # (2b) bank composition style (all in ONE straight row, no Y stagger):
    #   uniform_single       = N single-side turnstiles all facing one way; each
    #     lane crossed by exactly ONE arm.
    #   twin                 = ONE central double-side pedestal serving a lane on
    #     each side (the classic two-lane unit); only for K=2.
    #   ends_in_middle_double = two single-side ends facing inward + double-side
    #     middles.  Each lane is bordered by TWO opposing arms that meet at the
    #     lane centre forming ONE barrier (the person still passes once); the arms
    #     are reach-capped so their sweep disks never overlap.
    if hub_count >= 2:
        opts = ["uniform_single", "ends_in_middle_double"]
        if hub_count == 2:
            opts.append("twin")
        bank_style = rng.choice(opts)
    else:
        bank_style = "uniform_single"

    # (3) structural enums.
    pedestal_form = rng.choice(PEDESTAL_FORMS)
    arm_mechanism = rng.choices(ARM_MECHANISMS, weights=(0.7, 0.3), k=1)[0]

    # barrier = the DECORATIVE style of the lane-defining elements.  A lane rail
    # is ALWAYS built (see _build_barrier) so the passage always reads; this only
    # picks how the opposing element looks.  glass_swing reads best on 1-2 lanes;
    # wide banks bias toward plain/extended rails.
    if hub_count >= 3:
        barrier = rng.choices(
            ("tube_railings", "extended_guide_railings", "none"), weights=(0.45, 0.35, 0.20), k=1
        )[0]
    else:
        barrier = rng.choice(BARRIERS)

    # (4) arm_count (typical three-arm tripod).
    arm_count = rng.choices((3, 4), weights=(0.7, 0.3), k=1)[0]

    # (5) appearance.
    top_plate = rng.choice(TOP_PLATES)
    # reader: front-fascia RFID (S1) or side card reader (model-a S2 appearance).
    reader_module = rng.choice(READER_MODULES)
    palette_style = rng.choice(PALETTE_STYLES)

    # (6) continuous scale (independent):
    #   lane_width  -> the person-passage; drives the derived arm length, the pitch
    #                  and (for ends_double) the doubled gap.
    #   pedestal_width_scale -> the turnstile footprint/size (width).
    #   arm_reach_scale -> FILL fraction of the feasible reach (slight variety).
    lane_width = round(rng.uniform(0.50, 0.72), 3)
    pedestal_width_scale = round(rng.uniform(0.85, 1.25), 3)
    arm_reach_scale = round(rng.uniform(0.90, 1.0), 3)
    # whole-rotor orientation: arms splay up (hub mid-height) or down (hub raised).
    arm_splay = rng.choice(("up", "down"))

    # (7) a SINGLE rotor rest phase per seed, applied to every hub so the whole
    # bank looks uniform/aligned (mirrored faces stay mirror-consistent).
    arm_rest_phase_deg = round(rng.uniform(0.0, 360.0 / arm_count), 2)

    return TripodTurnstileConfig(
        pedestal_form=pedestal_form,
        rotor_mount=rotor_mount,
        bank_style=bank_style,
        arm_mechanism=arm_mechanism,
        barrier=barrier,
        top_plate=top_plate,
        reader_module=reader_module,
        palette_style=palette_style,
        hub_count=hub_count,
        arm_count=arm_count,
        hub_tilt_deg=hub_tilt_deg,
        arm_rest_phase_deg=arm_rest_phase_deg,
        pedestal_width_scale=pedestal_width_scale,
        arm_reach_scale=arm_reach_scale,
        lane_width=lane_width,
        arm_splay=arm_splay,
        name=f"seeded_tripod_turnstile_{seed}",
    )


# --------------------------------------------------------------------------- #
# resolve_config — clamp / derive / project the cross-part dependencies.
# --------------------------------------------------------------------------- #


def resolve_config(config: TripodTurnstileConfig) -> ResolvedTripodTurnstileConfig:
    pedestal_form = _require(config.pedestal_form, PEDESTAL_FORMS, field_name="pedestal_form")
    rotor_mount = _require(config.rotor_mount, ROTOR_MOUNTS, field_name="rotor_mount")
    bank_style = _require(config.bank_style, BANK_STYLES, field_name="bank_style")
    arm_mechanism = _require(config.arm_mechanism, ARM_MECHANISMS, field_name="arm_mechanism")
    barrier = _require(config.barrier, BARRIERS, field_name="barrier")
    top_plate = _require(config.top_plate, TOP_PLATES, field_name="top_plate")
    reader_module = _require(config.reader_module, READER_MODULES, field_name="reader_module")
    palette_style = _require(config.palette_style, PALETTE_STYLES, field_name="palette_style")

    arm_count = int(config.arm_count)
    if arm_count not in (3, 4):
        arm_count = 3

    hub_count = int(config.hub_count)

    # hub_count range is derived from rotor_mount (compatibility matrix):
    #  - front_face_downforward forms ONE centered corridor lane only.
    #  - side_face_outward is the multi-lane pattern: 1 side lane, a twin, or a
    #    gap-separated bank of up to 5 lanes.
    # front_face_downforward placed the pedestal in the MIDDLE of the corridor
    # (blocking the walk path); route any such config to the canonical side mount
    # where the pedestal sits beside the lane and the arm reaches across it.
    if rotor_mount == "front_face_downforward":
        rotor_mount = "side_face_outward"
    hub_count = max(1, min(5, hub_count))
    hub_tilt_deg = _clamp(config.hub_tilt_deg, 20.0, 35.0)

    # twin = ONE central double-side pedestal -> only valid for exactly K=2 side-mount.
    if bank_style == "twin" and not (rotor_mount == "side_face_outward" and hub_count == 2):
        bank_style = "uniform_single"

    # glass_swing is a centered gate IN FRONT of each turnstile (1 leaf per arm
    # face) — it generalizes to every side-mount config, so no degrade is needed.

    pedestal_width_scale = _clamp(config.pedestal_width_scale, 0.85, 1.25)
    arm_fill = _clamp(config.arm_reach_scale, 0.85, 1.0)
    lane_width = _clamp(config.lane_width, 0.45, 0.85)

    arm_splay = config.arm_splay if config.arm_splay in ("up", "down") else "up"
    # arm_splay="down" raises the hub near the pedestal top and points the spin axis
    # out+DOWN, so the rotor reads "1 cross-arm at waist + others angled down".
    z_sign = 1.0 if arm_splay == "up" else -1.0
    hub_z = SIDE_HUB_Z if arm_splay == "up" else SIDE_HUB_Z_DOWN

    # --- arm_l DERIVED from the lane width (so it always fills its lane), the floor
    # budget (arms must not sweep into the ground) and a fill fraction.  The per-arm
    # reach budget is ONE lane width either way (double-arm lanes use a 2x gap so the
    # two arms each reach a full lane-width and meet at the centre, sweep disks just
    # not overlapping). ---
    st = math.sin(math.radians(hub_tilt_deg))
    ct = math.cos(math.radians(hub_tilt_deg))
    mm = _rpy_to_matrix(_axis_rpy((ct, 0.0, z_sign * st)))
    cb, sb = math.cos(CONE), math.sin(CONE)
    dirs = [
        (cb * math.cos(math.radians(d)), cb * math.sin(math.radians(d)), sb)
        for d in range(0, 360, 10)
    ]
    k = max(abs(_matvec(mm, d)[0]) for d in dirs)  # horizontal X reach per unit
    down_reach = max(max(-_matvec(mm, d)[2] for d in dirs), 1e-3)  # most-downward per unit
    extra = 0.06 if pedestal_form == "round_post" else 0.0
    standoff = SIDE_STANDOFF + extra
    reach_budget = lane_width - standoff - 0.06  # how far the arm reaches from hub
    arm_l_lane = reach_budget / max(k, 1e-3) - ARM_R
    arm_l_floor = (hub_z - 0.05) / down_reach - ARM_R  # keep down-arm tips off the floor
    arm_l = _clamp(arm_fill * min(arm_l_lane, arm_l_floor), 0.18, 0.55)
    arm_reach_scale = arm_fill

    palette = dict(PALETTES[palette_style])

    return ResolvedTripodTurnstileConfig(
        pedestal_form=pedestal_form,  # type: ignore[arg-type]
        rotor_mount=rotor_mount,  # type: ignore[arg-type]
        bank_style=bank_style,  # type: ignore[arg-type]
        arm_mechanism=arm_mechanism,  # type: ignore[arg-type]
        barrier=barrier,  # type: ignore[arg-type]
        top_plate=top_plate,  # type: ignore[arg-type]
        reader_module=reader_module,  # type: ignore[arg-type]
        palette_style=palette_style,  # type: ignore[arg-type]
        hub_count=hub_count,
        arm_count=arm_count,
        hub_tilt_deg=hub_tilt_deg,
        arm_rest_phase_deg=float(config.arm_rest_phase_deg) % (360.0 / arm_count),
        pedestal_width_scale=pedestal_width_scale,
        arm_reach_scale=arm_reach_scale,
        lane_width=lane_width,
        arm_splay=arm_splay,  # type: ignore[arg-type]
        arm_l=arm_l,
        name=config.name,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Hub placement plan (derived).  Returns a list of per-hub dicts with the world
# joint origin xyz, the joint rpy, the world spin axis, and the local pedestal
# center-x (front-mount only).  This is the single source of truth shared by
# the cabinet boss visuals, the hub joints, and the tests.
# --------------------------------------------------------------------------- #


def _ped_half_width(r: ResolvedTripodTurnstileConfig) -> float:
    """Half-width (X) of one pedestal's head/post mounting band."""
    if r.pedestal_form == "round_post":
        return 0.075 * r.pedestal_width_scale
    if r.pedestal_form == "stepped_chamfer_cabinet":
        return 0.46 / 2.0 * r.pedestal_width_scale
    # rect / slanted share the wedge head box.
    return 0.34 / 2.0 * r.pedestal_width_scale


def _ped_base_half(r: ResolvedTripodTurnstileConfig) -> float:
    """Widest half-footprint (X) a flush curb/rail must clear.

    A flush rail is a TALL element spanning floor->top, so it has to clear the
    widest pedestal element at ANY height — usually the plinth/base plate, but a
    ``granite_overhang`` top slab juts ~0.035 past the head band and on the
    stepped cabinet (narrow column, wide head) that overhang is the true widest
    thing at rail height, so account for it here."""
    if r.pedestal_form == "round_post":
        base = BASE_PLATE_R * r.pedestal_width_scale
    elif r.pedestal_form == "stepped_chamfer_cabinet":
        base = M_COLUMN_W / 2.0 * r.pedestal_width_scale
    else:
        base = PLINTH_FOOT[0] / 2.0 * r.pedestal_width_scale
    top_half = _ped_half_width(r) + (GRANITE_OVERHANG if r.top_plate == "granite_overhang" else 0.0)
    return max(base, top_half)


def pedestal_plan(r: ResolvedTripodTurnstileConfig) -> list[dict]:
    """Pedestals along X with their arm faces (single source of truth).

    A FACE sign (+1 = arm reaches +X, -1 = arm reaches -X) means a rotor hub on
    that face guards a passage on that side.  A pedestal with one face is a
    single-side turnstile; with two faces a double-side turnstile.

    hub_count == number of LANES (K):
      front_face_downforward : one centered corridor pedestal (no ±X faces; the
        arm points +Y/-Z across the +Y corridor); always 1.
      side_face_outward, K=1 : one standalone single-side pedestal, arm OUTWARD
        (+X); passage on +X, flush on -X.
      side_face_outward, twin (K=2): ONE central double-side pedestal, one lane on
        each side (+X and -X), an outer rail across each lane.
      side_face_outward, uniform_single (K>=2): a straight row of K pedestals, ALL
        arms facing +X.  K pedestals = K lanes, each crossed by exactly ONE arm
        (the next pedestal's back is the opposing element; the last pedestal's +X
        arm faces an outer rail; the first pedestal's -X back is flush).

    ALL pedestals sit in ONE straight row at cy=0 (no Y stagger); every lane is
    crossed by exactly one arm so a person passes a single turnstile.
    """
    half = _ped_half_width(r)
    peds: list[dict] = []
    if r.rotor_mount == "front_face_downforward":
        peds.append({"cx": 0.0, "cy": 0.0, "half": half, "faces": [], "front": True})
        return peds
    if r.hub_count <= 1:
        peds.append({"cx": 0.0, "cy": 0.0, "half": half, "faces": [1], "front": False})
        return peds

    if r.bank_style == "twin":
        # ONE central double-side pedestal serving a lane on each side.
        peds.append({"cx": 0.0, "cy": 0.0, "half": half, "faces": [1, -1], "front": False})
        return peds

    pitch = 2.0 * half + r.lane_width
    if r.bank_style == "ends_in_middle_double":
        # K lanes = K+1 pedestals in ONE straight row: the two END pedestals are
        # single-side facing INWARD, the middles are double-side.  Each lane is
        # bordered by two opposing arms; the gap is DOUBLED (2x lane_width) so each
        # arm keeps a full lane-width reach and the two meet at the centre with
        # their sweep disks just not overlapping.
        pitch = 2.0 * half + 2.0 * r.lane_width
        p = r.hub_count + 1
        x0 = -(p - 1) * pitch / 2.0
        for i in range(p):
            if i == 0:
                faces = [1]  # left end faces inward (+X)
            elif i == p - 1:
                faces = [-1]  # right end faces inward (-X)
            else:
                faces = [1, -1]  # middle double-side
            peds.append(
                {"cx": x0 + i * pitch, "cy": 0.0, "half": half, "faces": faces, "front": False}
            )
        return peds

    # uniform_single: N single-side pedestals in a straight row, ALL arms facing
    # +X.  N pedestals = N lanes; each lane crossed by exactly ONE arm.
    n = r.hub_count
    x0 = -(n - 1) * pitch / 2.0
    for i in range(n):
        peds.append(
            {
                "cx": x0 + i * pitch,
                "cy": 0.0,
                "half": half,
                "faces": [1],
                "front": False,
            }
        )
    return peds


def hub_plan(r: ResolvedTripodTurnstileConfig) -> list[dict]:
    """Per-hub placement derived from pedestal_plan (one entry per arm face).

    Single source of truth for the cabinet bosses, the spin joints and the
    tests.  Every hub shares ``r.arm_rest_phase`` so the bank reads uniform;
    -X faces are mirrored so left/right faces line up consistently.
    """
    plan: list[dict] = []
    idx = 0
    if r.rotor_mount == "front_face_downforward":
        tilt = math.radians(r.hub_tilt_deg)
        ct, st = math.cos(tilt), math.sin(tilt)
        axis = (0.0, ct, -st)  # forward + down
        # anchor on the pedestal FRONT surface so the boss buries into the body.
        # round_post has no chamfer face — sit the anchor on the cylinder front
        # and stand the hub further off so it clears the fat cylinder.
        if r.pedestal_form == "round_post":
            anchor_y = POST_R * r.pedestal_width_scale - 0.005
            standoff = FRONT_STANDOFF + 0.10
        else:
            anchor_y = FRONT_ANCHOR[1]
            standoff = FRONT_STANDOFF
        anchor = (FRONT_ANCHOR[0], anchor_y, FRONT_ANCHOR[2])
        xyz = (
            anchor[0] + standoff * axis[0],
            anchor[1] + standoff * axis[1],
            anchor[2] + standoff * axis[2],
        )
        # boss must span from inside the pedestal body out to the hub seat.
        boss_l = standoff + 0.05
        plan.append(
            {
                "index": 0,
                "tag": "p0",
                "sign": 1.0,
                "face": 0,
                "axis": axis,
                "rpy": _axis_rpy(axis),
                "xyz": xyz,
                "anchor": anchor,
                "ped_cx": 0.0,
                "ped_half": _ped_half_width(r),
                "boss_l": boss_l,
                "boss_recess": BOSS_RECESS if r.arm_mechanism == "anti_panic_drop_arm" else 0.0,
            }
        )
        return plan
    tilt = math.radians(r.hub_tilt_deg)
    ct, st = math.cos(tilt), math.sin(tilt)
    # arm_splay: "up" → axis out+UP at mid-height hub; "down" → axis out+DOWN at a
    # raised hub (cross-arm at waist, others angle down).
    z_sign = 1.0 if r.arm_splay == "up" else -1.0
    hub_z = SIDE_HUB_Z if r.arm_splay == "up" else SIDE_HUB_Z_DOWN
    # A fat ROUND post (small half but full-depth cylinder) needs extra standoff
    # so the inboard-splaying rest arm clears the cylindrical body behind the hub.
    extra = 0.06 if r.pedestal_form == "round_post" else 0.0
    standoff = SIDE_STANDOFF + extra
    boss_l = 0.11 + extra * 2.0  # longer boss so it still buries into the body
    boss_recess = BOSS_RECESS if r.arm_mechanism == "anti_panic_drop_arm" else 0.0
    for ped in pedestal_plan(r):
        cy = ped.get("cy", 0.0)
        for face in ped["faces"]:
            sign = float(face)
            axis = (sign * ct, 0.0, z_sign * st)
            plan.append(
                {
                    "index": idx,
                    "tag": f"h{idx}",
                    "sign": sign,
                    "face": face,
                    "axis": axis,
                    "rpy": _axis_rpy(axis),
                    "xyz": (ped["cx"] + sign * (ped["half"] + standoff), cy, hub_z),
                    "ped_cx": ped["cx"],
                    "ped_cy": cy,
                    "ped_half": ped["half"],
                    "boss_l": boss_l,
                    "boss_recess": boss_recess,
                }
            )
            idx += 1
    return plan


def lane_plan(r: ResolvedTripodTurnstileConfig) -> list[dict]:
    """Lanes + flush edges derived from the pedestal faces.

    GENERAL PRINCIPLE: a turnstile<->railing gap is a walking passage iff a rotor
    arm reaches that side.  So for every pedestal face direction we emit a rail
    placed either a LANE_W gap out (arm faces that side -> passage) or flush
    against the pedestal (no arm that side -> outer boundary).  Inter-pedestal
    lanes (both bordering faces carry arms) are opposed by the neighbour pedestal
    and need no rail.

    Each lane dict: kind, gap=(x_lo,x_hi) walkable span, rail_x (None if the
    opposing element is an adjacent pedestal), is_passage (bool), rail_len.
    Single source of truth for _build_barrier AND the lane invariant tests.
    """
    lanes: list[dict] = []
    if r.rotor_mount == "front_face_downforward":
        # corridor half = arm X-sweep envelope (centerline + AABB padding) +
        # clearance; rails sit just outside the sweep so the arm guards the
        # corridor without clipping them.
        ct = math.cos(math.radians(r.hub_tilt_deg))
        sweep_x = (r.arm_l + ARM_R) * ct + ARM_R
        rail_x = sweep_x + 0.03
        # walkable corridor = rail-inner to rail-inner span.
        x = rail_x - RAIL_TUBE_R
        lanes.append(
            {
                "kind": "corridor",
                "gap": (-x, x),
                "rail_xs": (-rail_x, rail_x),
                "is_passage": True,
                "rail_len": 1.10,
            }
        )
        return lanes

    peds = pedestal_plan(r)
    # Mark, per pedestal, whether each ±X side carries an arm.
    for i, ped in enumerate(peds):
        cx, hf = ped["cx"], ped["half"]
        has_pos = 1 in ped["faces"]
        has_neg = -1 in ped["faces"]
        left_neighbor = peds[i - 1] if i > 0 else None
        right_neighbor = peds[i + 1] if i < len(peds) - 1 else None

        # +X side
        if right_neighbor is not None:
            # interior gap between this pedestal and the next: a lane if either
            # bordering face carries an arm (it always does in our composition).
            if has_pos or (-1 in right_neighbor["faces"]):
                edge = cx + hf
                opp_edge = right_neighbor["cx"] - right_neighbor["half"]
                lanes.append(
                    {
                        "kind": "between",
                        "gap": (edge, opp_edge),
                        "rail_x": None,
                        "is_passage": True,
                        "rail_len": 0.90,
                        "arm_edge": edge,
                        "hinge_x": opp_edge,
                    }
                )
        else:
            # outer +X side: passage iff this pedestal's +X face has an arm.
            edge = cx + hf
            if has_pos:
                rail_x = edge + (r.lane_width + RAIL_TUBE_R)
                lanes.append(
                    {
                        "kind": "outer",
                        "gap": (edge, rail_x),
                        "rail_x": rail_x,
                        "is_passage": True,
                        "rail_len": 0.90,
                        "arm_edge": edge,
                        "hinge_x": rail_x,
                    }
                )
            else:
                # flush: curb just clears the (wider) base footprint; flush gap
                # is measured off the base it abuts (no walking space).
                base_edge = cx + _ped_base_half(r)
                rail_x = base_edge + 0.06
                lanes.append(
                    {
                        "kind": "flush",
                        "gap": (base_edge, rail_x),
                        "rail_x": rail_x,
                        "is_passage": False,
                        "rail_len": 0.90,
                    }
                )

        # -X outer side (only for the leftmost pedestal; interior -X handled by
        # the left neighbour's +X pass above).
        if left_neighbor is None:
            edge = cx - hf
            if has_neg:
                rail_x = edge - (r.lane_width + RAIL_TUBE_R)
                lanes.append(
                    {
                        "kind": "outer",
                        "gap": (rail_x, edge),
                        "rail_x": rail_x,
                        "is_passage": True,
                        "rail_len": 0.90,
                        "arm_edge": edge,
                        "hinge_x": rail_x,
                    }
                )
            else:
                base_edge = cx - _ped_base_half(r)
                rail_x = base_edge - 0.06
                lanes.append(
                    {
                        "kind": "flush",
                        "gap": (rail_x, base_edge),
                        "rail_x": rail_x,
                        "is_passage": False,
                        "rail_len": 0.90,
                    }
                )
    return lanes


# --------------------------------------------------------------------------- #
# Slot A — cabinet (frame) builders.  All fused as visuals on `cabinet`.
# --------------------------------------------------------------------------- #

# ---- rect / slanted wedge head (S1 / S4) ----
PLINTH_FOOT = (0.46, 0.36)
PLINTH_TOP = (0.19, 0.16)
PLINTH_H = 0.115
COLUMN_BOT = (0.175, 0.15)
COLUMN_TOP = (0.14, 0.125)
COLUMN_Z0 = 0.105
COLUMN_Z1 = 0.50
HEAD_NECK = (0.138, 0.123)
HEAD_BOX = (0.34, 0.26)
HEAD_Z_NECK = 0.495
HEAD_Z_SHOULDER = 0.64


def _rect_plinth_mesh(sx: float):
    solid = (
        cq.Workplane("XY")
        .rect(PLINTH_FOOT[0] * sx, PLINTH_FOOT[1])
        .workplane(offset=PLINTH_H)
        .rect(PLINTH_TOP[0] * sx, PLINTH_TOP[1])
        .loft(ruled=True)
    )
    return mesh_from_cadquery(solid, "base_plinth", tolerance=0.001, angular_tolerance=0.15)


def _rect_column_mesh(sx: float):
    solid = (
        cq.Workplane("XY", origin=(0.0, 0.0, COLUMN_Z0))
        .rect(COLUMN_BOT[0] * sx, COLUMN_BOT[1])
        .workplane(offset=COLUMN_Z1 - COLUMN_Z0)
        .rect(COLUMN_TOP[0] * sx, COLUMN_TOP[1])
        .loft(ruled=True)
    )
    return mesh_from_cadquery(solid, "column", tolerance=0.001, angular_tolerance=0.15)


def _rect_head_mesh(sx: float):
    """Wedge head: neck -> wide reader box -> chamfered top (S1)."""
    solid = (
        cq.Workplane("XY", origin=(0.0, 0.0, HEAD_Z_NECK))
        .rect(HEAD_NECK[0] * sx, HEAD_NECK[1])
        .workplane(offset=HEAD_Z_SHOULDER - HEAD_Z_NECK)
        .rect(HEAD_BOX[0] * sx, HEAD_BOX[1])
        .workplane(offset=0.92 - HEAD_Z_SHOULDER)
        .rect(HEAD_BOX[0] * sx, HEAD_BOX[1])
        .workplane(offset=0.96 - 0.92)
        .rect(0.315 * sx, 0.235)
        .loft(ruled=True)
    )
    return mesh_from_cadquery(solid, "head_shell", tolerance=0.001, angular_tolerance=0.15)


def _slanted_head_mesh(sx: float):
    """Slanted optical head raking toward the walker (+Y) (S4)."""
    front_top, back_top = 1.00, 0.86
    alpha = math.atan2(front_top - back_top, HEAD_BOX[1])
    center_z = (front_top + back_top) / 2.0
    tilted_hy = (HEAD_BOX[1] / 2.0) / math.cos(alpha)
    solid = (
        cq.Workplane("XY", origin=(0.0, 0.0, HEAD_Z_NECK))
        .rect(HEAD_NECK[0] * sx, HEAD_NECK[1])
        .workplane(offset=HEAD_Z_SHOULDER - HEAD_Z_NECK)
        .rect(HEAD_BOX[0] * sx, HEAD_BOX[1])
        .workplane(offset=center_z - HEAD_Z_SHOULDER)
        .transformed(rotate=(math.degrees(alpha), 0.0, 0.0))
        .rect(HEAD_BOX[0] * sx, 2.0 * tilted_hy)
        .loft(ruled=True)
    )
    return mesh_from_cadquery(solid, "head_shell", tolerance=0.001, angular_tolerance=0.15)


# ---- stepped chamfer cabinet (S2 model-a) ----
M_COLUMN_W = 0.42
M_COLUMN_D = 0.18
M_COLUMN_H = 0.76
M_HEAD_W = 0.46
M_HEAD_D = 0.28
M_HEAD_Y = 0.05
M_HEAD_Z0 = 0.855
M_HEAD_Z1 = 0.98
M_LOFT_Z0 = 0.755
M_LOFT_Z1 = 0.86


def _stepped_column_mesh(sx: float):
    """Hollow thin-wall lower column (model-a S2)."""
    col = (
        cq.Workplane("XY")
        .box(M_COLUMN_W * sx, M_COLUMN_D, M_COLUMN_H, centered=(True, True, False))
        .faces("<Z")
        .shell(-0.006)
    )
    return mesh_from_cadquery(col, "column_shell", tolerance=0.001, angular_tolerance=0.15)


def _stepped_transition_mesh(sx: float):
    """Chamfer loft from the slim column to the deeper head box (S2)."""
    loft = (
        cq.Workplane("XY", origin=(0.0, 0.0, M_LOFT_Z0))
        .rect(M_COLUMN_W * sx, M_COLUMN_D)
        .workplane(offset=M_LOFT_Z1 - M_LOFT_Z0)
        .center(0.0, M_HEAD_Y)
        .rect(M_HEAD_W * sx, M_HEAD_D)
        .loft()
    )
    return mesh_from_cadquery(loft, "head_transition", tolerance=0.001, angular_tolerance=0.15)


# ---- round post (S3) ----
POST_R = 0.075
POST_Z1 = 0.96
POST_COLLAR_R = 0.085
POST_COLLAR_Z0 = 0.60
POST_COLLAR_Z1 = 0.72
BASE_PLATE_R = 0.20
BASE_PLATE_H = 0.028


def _round_post_mesh(sx: float):
    """Round cylindrical post + base plate + collar ring via LatheGeometry."""
    pr = POST_R * sx
    cr = POST_COLLAR_R * sx
    br = BASE_PLATE_R * sx
    profile = [
        (0.0, 0.0),
        (br, 0.0),
        (br, BASE_PLATE_H * 0.4),
        (br - 0.01, BASE_PLATE_H),
        (pr + 0.005, BASE_PLATE_H + 0.01),
        (pr, BASE_PLATE_H + 0.03),
        (pr, POST_COLLAR_Z0 - 0.01),
        (pr + 0.003, POST_COLLAR_Z0),
        (cr, POST_COLLAR_Z0 + 0.008),
        (cr, POST_COLLAR_Z1 - 0.008),
        (pr + 0.003, POST_COLLAR_Z1),
        (pr, POST_COLLAR_Z1 + 0.01),
        (pr, POST_Z1 - 0.01),
        (pr + 0.004, POST_Z1),
        (pr + 0.004, POST_Z1 + 0.008),
        (pr - 0.005, POST_Z1 + 0.015),
        (0.0, POST_Z1 + 0.015),
    ]
    geom = LatheGeometry(profile, segments=40)
    return mesh_from_geometry(geom, "post_body")


def _round_dome_mesh(sx: float):
    dome = DomeGeometry(POST_R * sx, radial_segments=28, height_segments=8, closed=True)
    return mesh_from_geometry(dome, "dome_cap")


# ---- top plate appearance (visual) ----


def _add_top_plate(
    cabinet: Part, r: ResolvedTripodTurnstileConfig, m: dict, *, cx: float, cy: float, top_z: float
) -> None:
    """Top plate appearance variant; pure visual, no joint (Rule 1)."""
    half = _ped_half_width(r)
    # Each plate's bottom sits a few mm BELOW the head top so it embeds into the
    # head (connectivity at tol=1e-6 needs real contact, not a hover gap).
    if r.top_plate == "granite_overhang":
        thk = 0.022
        cabinet.visual(
            Box((2.0 * (half + GRANITE_OVERHANG), 0.31, thk)),
            origin=Origin(xyz=(cx, cy + 0.05, top_z - 0.005 + thk / 2.0)),
            material=m["top"],
            name=f"granite_top_{cx:+.2f}", material_class_id="stone.polished_granite",
        )
    elif r.top_plate == "flat_steel":
        thk = 0.014
        cabinet.visual(
            Box((2.0 * half - 0.01, 0.24, thk)),
            origin=Origin(xyz=(cx, cy, top_z - 0.005 + thk / 2.0)),
            material=m["body"],
            name=f"flat_top_{cx:+.2f}", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_granite", "painted_dark", "polished_chrome", "white_powdercoat"} else "metal.brushed_silver"),
        )
    else:  # dark_sloped_cap (S1)
        thk = 0.018
        cabinet.visual(
            Box((2.0 * half - 0.02, 0.236, thk)),
            origin=Origin(
                xyz=(cx, cy - 0.01, top_z - 0.004 + thk / 2.0), rpy=(math.radians(5.0), 0.0, 0.0)
            ),
            material=m["top"],
            name=f"sloped_cap_{cx:+.2f}", material_class_id="metal.paint_coated",
        )


def _add_reader(
    cabinet: Part, r: ResolvedTripodTurnstileConfig, m: dict, *, cx: float, cy: float, top_z: float
) -> None:
    """Reader module appearance variant; pure visual (Rule 1)."""
    half = _ped_half_width(r)
    # On a round post there is no flat fascia at y=0.12, so the side reader hugs
    # the post side surface at y=0 (where the post wall is at x=+/-half); for the
    # rectangular forms it sits forward at y=0.12 on the flat side face.  Either
    # way its inboard edge embeds a few mm into the body for connectivity.
    reader_y = cy + (0.0 if r.pedestal_form == "round_post" else 0.12)
    if r.reader_module == "side_card_reader":
        # side-mounted card reader + LED (model-a S2).
        reader_w = 0.018
        reader_cx = cx - half + reader_w / 2.0 - 0.006  # inboard edge ~6mm inside the body
        cabinet.visual(
            Box((reader_w, 0.085, 0.055)),
            origin=Origin(xyz=(reader_cx, reader_y, top_z - 0.05)),
            material=m["reader"],
            name=f"card_reader_{cx:+.2f}", material_class_id="tech.control_interface",
        )
        cabinet.visual(
            Box((0.006, 0.050, 0.010)),
            origin=Origin(xyz=(reader_cx - reader_w / 2.0 - 0.002, reader_y, top_z - 0.035)),
            material=m["led"],
            name=f"reader_led_{cx:+.2f}", material_class_id="tech.emissive_surface",
        )
    else:  # front_fascia_rfid (S1)
        panel_y = cy + (
            (POST_R * r.pedestal_width_scale - 0.005) if r.pedestal_form == "round_post" else 0.131
        )
        cabinet.visual(
            Box((0.10, 0.012, 0.10)),
            origin=Origin(xyz=(cx, panel_y, top_z - 0.12)),
            material=m["reader"],
            name=f"reader_panel_{cx:+.2f}", material_class_id="tech.control_interface",
        )
        cabinet.visual(
            Cylinder(radius=0.024, length=0.012),
            origin=Origin(xyz=(cx, cy - 0.02, top_z - 0.002)),
            material=m["led"],
            name=f"reader_led_{cx:+.2f}", material_class_id="tech.emissive_surface",
        )


def _add_boss(cabinet: Part, hub: dict, m: dict) -> None:
    """Chrome bearing boss whose outer end-face seats the hub collar.

    The boss is centered inboard of the joint origin along the hub axis, long
    enough to bury its inner end in the pedestal and reach the hub collar.
    """
    axis = hub["axis"]
    xyz = hub["xyz"]
    boss_l = hub.get("boss_l", 0.11)
    # Recess the outboard boss face inboard by boss_recess (anti-panic only) so the
    # dropped arm cone clears the boss rim; the cylinder centre shifts inboard too.
    off = boss_l / 2.0 + hub.get("boss_recess", 0.0)
    bc = (
        xyz[0] - off * axis[0],
        xyz[1] - off * axis[1],
        xyz[2] - off * axis[2],
    )
    cabinet.visual(
        Cylinder(radius=BOSS_R, length=boss_l),
        origin=Origin(xyz=bc, rpy=hub["rpy"]),
        material=m["chrome"],
        name=f"rotor_boss_{hub['index']}", material_class_id="metal.chrome_polished",
    )


def _build_one_pedestal(
    cabinet: Part, r: ResolvedTripodTurnstileConfig, m: dict, *, cx: float, cy: float = 0.0
) -> float:
    """Build one pedestal's fixed geometry at center (cx, cy); return its top_z."""
    sx = r.pedestal_width_scale
    if r.pedestal_form == "round_post":
        cabinet.visual(
            _round_post_mesh(sx),
            origin=Origin(xyz=(cx, cy, 0.0)),
            material=m["body"],
            name=f"post_body_{cx:+.2f}", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_granite", "painted_dark", "polished_chrome", "white_powdercoat"} else "metal.brushed_silver"),
        )
        cabinet.visual(
            _round_dome_mesh(sx),
            origin=Origin(xyz=(cx, cy, POST_Z1 + 0.005)),
            material=m["body_dark"],
            name=f"dome_cap_{cx:+.2f}", material_class_id="metal.paint_coated",
        )
        return POST_Z1
    if r.pedestal_form == "stepped_chamfer_cabinet":
        cabinet.visual(
            _stepped_column_mesh(sx),
            origin=Origin(xyz=(cx, cy, 0.0)),
            material=m["body"],
            name=f"column_shell_{cx:+.2f}", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_granite", "painted_dark", "polished_chrome", "white_powdercoat"} else "metal.brushed_silver"),
        )
        cabinet.visual(
            _stepped_transition_mesh(sx),
            origin=Origin(xyz=(cx, cy, 0.0)),
            material=m["body"],
            name=f"head_transition_{cx:+.2f}", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_granite", "painted_dark", "polished_chrome", "white_powdercoat"} else "metal.brushed_silver"),
        )
        cabinet.visual(
            Box((M_HEAD_W * sx, M_HEAD_D, M_HEAD_Z1 - M_HEAD_Z0)),
            origin=Origin(xyz=(cx, cy + M_HEAD_Y, (M_HEAD_Z0 + M_HEAD_Z1) / 2.0)),
            material=m["body"],
            name=f"head_housing_{cx:+.2f}", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_granite", "painted_dark", "polished_chrome", "white_powdercoat"} else "metal.brushed_silver"),
        )
        return M_HEAD_Z1
    # rect / slanted wedge head.
    cabinet.visual(
        _rect_plinth_mesh(sx),
        origin=Origin(xyz=(cx, cy, 0.0)),
        material=m["body"],
        name=f"base_plinth_{cx:+.2f}", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_granite", "painted_dark", "polished_chrome", "white_powdercoat"} else "metal.brushed_silver"),
    )
    cabinet.visual(
        _rect_column_mesh(sx),
        origin=Origin(xyz=(cx, cy, 0.0)),
        material=m["body"],
        name=f"column_{cx:+.2f}", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_granite", "painted_dark", "polished_chrome", "white_powdercoat"} else "metal.brushed_silver"),
    )
    if r.pedestal_form == "slanted_optical_head":
        cabinet.visual(
            _slanted_head_mesh(sx),
            origin=Origin(xyz=(cx, cy, 0.0)),
            material=m["body"],
            name=f"head_shell_{cx:+.2f}", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_granite", "painted_dark", "polished_chrome", "white_powdercoat"} else "metal.brushed_silver"),
        )
        return 0.96
    cabinet.visual(
        _rect_head_mesh(sx),
        origin=Origin(xyz=(cx, cy, 0.0)),
        material=m["body"],
        name=f"head_shell_{cx:+.2f}", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_granite", "painted_dark", "polished_chrome", "white_powdercoat"} else "metal.brushed_silver"),
    )
    return 0.96


def _assembly_footprint(r: ResolvedTripodTurnstileConfig, peds: list[dict]) -> tuple[float, ...]:
    """XY bounds of the whole installation (pedestals + rails + front glass gates)
    so the single base plate can span everything and provide the mount geometry."""
    base_half = _ped_base_half(r)
    xs: list[float] = []
    ys: list[float] = []
    for p in peds:
        xs += [p["cx"] - base_half, p["cx"] + base_half]
        ys += [-0.22, 0.22]
    rl_max = 0.0
    for lane in lane_plan(r):
        if lane.get("rail_x") is not None:
            rl = 1.50 if r.barrier == "extended_guide_railings" else 0.90
            rl_max = max(rl_max, rl)
            xs += [lane["rail_x"] - 0.07, lane["rail_x"] + 0.07]
            ys += [-rl / 2.0 - 0.06, rl / 2.0 + 0.06]
    if r.barrier == "glass_swing_panel":
        # front-centered gate posts extend +Y; leaves span ~LANE_W around each post.
        ys += [GATE_FRONT_Y + 0.10]
        for p in peds:
            xs += [p["cx"] - r.lane_width, p["cx"] + r.lane_width]
    return (min(xs) - 0.06, max(xs) + 0.06, min(ys) - 0.06, max(ys) + 0.06)


def _build_cabinet(
    model: ArticulatedObject, r: ResolvedTripodTurnstileConfig, m: dict, plan: list[dict]
) -> Part:
    cabinet = model.part("cabinet")

    peds = pedestal_plan(r)
    cxs = [p["cx"] for p in peds]
    cys = [p.get("cy", 0.0) for p in peds]

    # A single thin FLOOR/INSTALLATION BASE PLATE the whole bank sits on (pedestals,
    # rails and front glass gates all bolt onto it).  This makes the model one
    # connected tree + provides the mount geometry under every FIXED joint, WITHOUT
    # any bar-like connectors between the separate units.
    x0, x1, y0, y1 = _assembly_footprint(r, peds)
    cabinet.visual(
        Box((x1 - x0, y1 - y0, BASE_PLATE_Z)),
        origin=Origin(xyz=((x0 + x1) / 2.0, (y0 + y1) / 2.0, BASE_PLATE_Z / 2.0)),
        material=m["body_dark"],
        name="base_plate", material_class_id="metal.paint_coated",
    )

    top_z = 0.96
    for p in peds:
        top_z = _build_one_pedestal(cabinet, r, m, cx=p["cx"], cy=p.get("cy", 0.0))
        _add_top_plate(cabinet, r, m, cx=p["cx"], cy=p.get("cy", 0.0), top_z=top_z)
        _add_reader(cabinet, r, m, cx=p["cx"], cy=p.get("cy", 0.0), top_z=top_z)

    for hub in plan:
        _add_boss(cabinet, hub, m)

    cabinet.inertial = Inertial.from_geometry(
        Box((max(0.4, (cxs[-1] - cxs[0]) + 0.5), max(0.4, (max(cys) - min(cys)) + 0.4), 1.0)),
        mass=200.0,
        origin=Origin(xyz=((cxs[0] + cxs[-1]) / 2.0, (max(cys) + min(cys)) / 2.0, 0.5)),
    )
    return cabinet


# --------------------------------------------------------------------------- #
# Slot C — hub (rotor) + optional anti-panic drop carrier.
# Local frame: hub +Z = the spin axis; arms splay on the 45 deg cone.
# --------------------------------------------------------------------------- #


def _build_hub_part(
    model: ArticulatedObject, r: ResolvedTripodTurnstileConfig, m: dict, hub: dict
) -> Part:
    part = model.part(f"tripod_hub_{hub['index']}")
    part.visual(
        _hub_mesh(f"hub_core_{hub['index']}"),
        origin=Origin(),
        material=m["chrome"],
        name="hub_core", material_class_id="metal.chrome_polished",
    )
    rest = r.arm_rest_phase_deg  # uniform rest offset across every hub in a seed
    for j, phase in enumerate(_arm_phases(r.arm_count)):
        part.visual(
            _arm_mesh(f"arm_{hub['index']}_{j}", r.arm_l),
            origin=Origin(
                xyz=(0.0, 0.0, ARM_START_Z),
                rpy=(0.0, math.pi / 2.0 - CONE, math.radians(phase + rest)),
            ),
            material=m["arm"],
            name=f"arm_{j}", material_class_id="metal.chrome_polished",
        )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=r.arm_l, length=0.10),
        mass=10.0,
        origin=Origin(xyz=(0.0, 0.0, ARM_START_Z)),
    )
    return part


def _build_carrier_part(model: ArticulatedObject, m: dict, hub: dict) -> Part:
    """Anti-panic drop carrier bracket (S7): hinge barrel along local Y."""
    carrier = model.part(f"arm_carrier_{hub['index']}")
    barrel = cq.Workplane("XZ").circle(0.013).extrude(0.045, both=True)
    carrier.visual(
        mesh_from_cadquery(
            barrel, f"carrier_barrel_{hub['index']}", tolerance=0.0008, angular_tolerance=0.1
        ),
        origin=Origin(),
        material=m["chrome"],
        name="bracket", material_class_id="metal.chrome_polished",
    )
    carrier.inertial = Inertial.from_geometry(
        Cylinder(radius=0.02, length=0.12),
        mass=2.0,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    return carrier


def _emit_hub_joints(
    model: ArticulatedObject,
    cabinet: Part,
    r: ResolvedTripodTurnstileConfig,
    m: dict,
    plan: list[dict],
) -> None:
    for hub in plan:
        hub_part = _build_hub_part(model, r, m, hub)
        if r.arm_mechanism == "anti_panic_drop_arm":
            carrier = _build_carrier_part(model, m, hub)
            # drop joint: cabinet -> carrier, horizontal REVOLUTE about the
            # axis perpendicular to the hub axis lying in the horizontal plane.
            # horizontal axis perpendicular to the vertical-plane spin axis:
            # for side-mount use Y; for front-mount also use X-horizontal.
            # The FOLD SENSE about Y is derived so the inboard arms swing AWAY
            # from the pedestal body instead of plunging into it: with the arms
            # already splayed UP the safe sense is +sign*Y, splayed DOWN it is
            # -sign*Y (the opposite sense drives the inboard arm cone straight
            # into the fat post / column — verified by swept-arm-vs-body
            # clearance over the full 0-60 deg drop).
            if r.rotor_mount == "side_face_outward":
                drop_z_sign = 1.0 if r.arm_splay == "up" else -1.0
                drop_axis = (0.0, hub["sign"] * drop_z_sign, 0.0)
            else:
                drop_axis = (1.0, 0.0, 0.0)
            model.articulation(
                f"arm_drop_{hub['index']}",
                ArticulationType.REVOLUTE,
                parent=cabinet,
                child=carrier,
                origin=Origin(xyz=hub["xyz"]),
                axis=drop_axis,
                motion_limits=MotionLimits(
                    effort=80.0, velocity=2.0, lower=0.0, upper=math.radians(60.0)
                ),
            )
            # hub spin: carrier -> hub (CONTINUOUS about hub local +Z), the
            # drop pivot passes through the hub center so the hub stays put.
            model.articulation(
                f"rotor_spin_{hub['index']}",
                ArticulationType.CONTINUOUS,
                parent=carrier,
                child=hub_part,
                origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=hub["rpy"]),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=40.0, velocity=8.0),
            )
        else:
            model.articulation(
                f"rotor_spin_{hub['index']}",
                ArticulationType.CONTINUOUS,
                parent=cabinet,
                child=hub_part,
                origin=Origin(xyz=hub["xyz"], rpy=hub["rpy"]),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=40.0, velocity=8.0),
            )


# --------------------------------------------------------------------------- #
# Slot D — barrier (self-standing lane guides) / glass swing.
# --------------------------------------------------------------------------- #

RAIL_TUBE_R = 0.015
RAIL_TOP_Z = 1.00
RAIL_CORNER_R = 0.07
RAIL_LEG_BOT_Z = 0.012
RAIL_BOT_Z = 0.13
RAIL_N_BAL = 5


def _railing_frame_mesh(name: str, rail_len: float):
    """Rectangular frame with rounded TOP corners (S1 / S6 spline tube)."""
    y0 = -rail_len / 2.0
    y1 = rail_len / 2.0
    z_top = RAIL_TOP_Z
    rr = RAIL_CORNER_R
    z_corner = z_top - rr
    cy0 = y0 + rr
    cy1 = y1 - rr
    pts: list[tuple[float, float, float]] = []
    for z in (RAIL_LEG_BOT_Z, 0.25 * z_corner, 0.55 * z_corner, 0.8 * z_corner, z_corner):
        pts.append((0.0, y0, z))
    for deg in range(15, 91, 15):
        a = math.radians(deg)
        pts.append((0.0, cy0 - rr * math.cos(a), z_corner + rr * math.sin(a)))
    pts.append((0.0, (y0 + y1) / 2.0, z_top))
    for deg in range(15, 91, 15):
        a = math.radians(deg)
        pts.append((0.0, cy1 + rr * math.sin(a), z_corner + rr * math.cos(a)))
    for z in (z_corner, 0.8 * z_corner, 0.55 * z_corner, 0.25 * z_corner, RAIL_LEG_BOT_Z):
        pts.append((0.0, y1, z))
    frame = tube_from_spline_points(
        pts, radius=RAIL_TUBE_R, samples_per_segment=8, radial_segments=14, cap_ends=True
    )
    return mesh_from_geometry(frame, name)


def _build_one_railing(
    model: ArticulatedObject, m: dict, *, index: int, rail_x: float, rail_len: float
) -> Part:
    railing = model.part(f"side_railing_{index}")
    railing.visual(
        _railing_frame_mesh(f"railing_frame_{index}", rail_len),
        origin=Origin(),
        material=m["chrome"],
        name="frame", material_class_id="metal.chrome_polished",
    )
    railing.visual(
        Cylinder(radius=RAIL_TUBE_R, length=rail_len + 0.004),
        origin=Origin(xyz=(0.0, 0.0, RAIL_BOT_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=m["chrome"],
        name="bottom_rail", material_class_id="metal.chrome_polished",
    )
    bal_z0 = RAIL_BOT_Z - RAIL_TUBE_R
    bal_z1 = RAIL_TOP_Z + RAIL_TUBE_R
    bal_len = bal_z1 - bal_z0
    bal_zc = (bal_z0 + bal_z1) / 2.0
    n_bal = max(RAIL_N_BAL, int(rail_len / 0.18))
    for b in range(n_bal):
        frac = (b + 1) / (n_bal + 1)
        by = -rail_len / 2.0 + rail_len * frac
        railing.visual(
            Cylinder(radius=0.0075, length=bal_len),
            origin=Origin(xyz=(0.0, by, bal_zc)),
            material=m["chrome"],
            name=f"baluster_{b}", material_class_id="metal.chrome_polished",
        )
    for f, fy in enumerate((-rail_len / 2.0, rail_len / 2.0)):
        railing.visual(
            Cylinder(radius=0.046, length=0.016),
            origin=Origin(xyz=(0.0, fy, 0.008)),
            material=m["chrome"],
            name=f"floor_flange_{f}", material_class_id="metal.chrome_polished",
        )
        railing.visual(
            Cylinder(radius=0.026, length=0.04),
            origin=Origin(xyz=(0.0, fy, 0.028)),
            material=m["chrome"],
            name=f"flange_collar_{f}", material_class_id="metal.chrome_polished",
        )
    # Mounting foot at the railing local origin (0,0,0): a low floor pad bolted onto
    # the shared base plate (which provides the parent geometry under the FIXED
    # mount joint — no separate connector bar).
    railing.visual(
        Cylinder(radius=0.05, length=0.03),
        origin=Origin(xyz=(0.0, 0.0, 0.015)),
        material=m["chrome"],
        name="mount_pad", material_class_id="metal.chrome_polished",
    )
    railing.visual(
        Cylinder(radius=0.012, length=RAIL_BOT_Z),
        origin=Origin(xyz=(0.0, 0.0, RAIL_BOT_Z / 2.0)),
        material=m["chrome"],
        name="mount_stub", material_class_id="metal.chrome_polished",
    )
    railing.inertial = Inertial.from_geometry(
        Box((0.1, rail_len, RAIL_TOP_Z)),
        mass=12.0,
        origin=Origin(xyz=(0.0, 0.0, RAIL_TOP_Z / 2.0)),
    )
    model.articulation(
        f"railing_mount_{index}",
        ArticulationType.FIXED,
        parent=model.get_part("cabinet"),
        child=railing,
        origin=Origin(xyz=(rail_x, 0.0, 0.015)),
    )
    return railing


# glass swing (S5)
GP_POST_R = 0.035
GP_POST_H = 1.02
GP_PANEL_W = 0.42
GP_PANEL_H = 0.74
GP_PANEL_THK = 0.012
GP_PANEL_BOT_Z = 0.18
GP_CLEAR = 0.012
GP_FRAME_BAR = 0.022
# Twin gate: both leaves open forward (+Y) and converge; cap their travel short of
# the +Y axis so the two thin panes never touch (each stays > this gap apart).
TWIN_LEAF_CAP = math.radians(68.0)


def _build_glass_gate(
    model: ArticulatedObject,
    r: ResolvedTripodTurnstileConfig,
    m: dict,
    *,
    gate_index: int,
    leaf_start: int,
    post_cx: float,
    sides: list[int],
) -> None:
    """A glass swing gate placed IN FRONT of one turnstile: a single hinge post
    CENTERED on the turnstile (post_cx) and standing GATE_FRONT_Y ahead of it on
    the base plate, carrying one leaf per arm face (single-side -> 1 leaf, twin ->
    2 leaves).  The post is FIXED to the cabinet (the base plate provides the mount
    geometry — no connector bar); each leaf is its REVOLUTE child spanning its lane.
    """
    cabinet = model.get_part("cabinet")
    glass_cz = GP_PANEL_BOT_Z + GP_PANEL_H / 2.0
    panel_top_z = GP_PANEL_BOT_Z + GP_PANEL_H
    leaf_w = r.lane_width - GP_CLEAR - GP_FRAME_BAR

    # --- centered hinge post in front of the turnstile, on the base plate. ---
    post = model.part(f"glass_post_{gate_index}")
    post.visual(
        Cylinder(radius=GP_POST_R, length=GP_POST_H),
        origin=Origin(xyz=(0.0, 0.0, GP_POST_H / 2.0)),
        material=m["chrome"],
        name="hinge_post", material_class_id="metal.chrome_polished",
    )
    post.visual(
        Cylinder(radius=GP_POST_R + 0.004, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, GP_POST_H - 0.006)),
        material=m["chrome"],
        name="post_cap", material_class_id="metal.chrome_polished",
    )
    post.visual(
        Cylinder(radius=0.052, length=0.02),
        origin=Origin(xyz=(0.0, 0.0, 0.01)),
        material=m["chrome"],
        name="post_flange", material_class_id="metal.chrome_polished",
    )
    post.inertial = Inertial.from_geometry(
        Cylinder(radius=GP_POST_R, length=GP_POST_H),
        mass=8.0,
        origin=Origin(xyz=(0.0, 0.0, GP_POST_H / 2.0)),
    )
    model.articulation(
        f"glass_post_mount_{gate_index}",
        ArticulationType.FIXED,
        parent=cabinet,
        child=post,
        origin=Origin(xyz=(post_cx, GATE_FRONT_Y, 0.0)),
    )

    # --- one leaf per arm face, spanning its lane; REVOLUTE child of the post. ---
    # A twin gate carries TWO leaves on ONE shared post.  Both open FORWARD (+Y,
    # away from the pedestal that sits behind the post); driving them the SAME
    # sense to opposite +Y/-Y sides would swing the rear leaf into the pedestal
    # body, so instead both converge toward +Y and their travel is CAPPED short
    # of the +Y axis (TWIN_LEAF_CAP) so the two panes never meet.
    twin = len(sides) == 2
    for k, face in enumerate(sides):
        sign = float(face)
        leaf = model.part(f"glass_leaf_{leaf_start + k}")
        glass_cx = sign * (GP_POST_R + GP_CLEAR + leaf_w / 2.0)
        leaf.visual(
            Box((leaf_w + 0.008, GP_PANEL_THK, GP_PANEL_H + 0.008)),
            origin=Origin(xyz=(glass_cx, 0.0, glass_cz)),
            material=m["glass"],
            name="glass_pane", material_class_id="glass.clear_transparent",
        )
        leaf.visual(
            Box((leaf_w, GP_FRAME_BAR, GP_FRAME_BAR)),
            origin=Origin(xyz=(glass_cx, 0.0, panel_top_z + GP_FRAME_BAR / 2.0)),
            material=m["chrome"],
            name="frame_top", material_class_id="metal.chrome_polished",
        )
        leaf.visual(
            Box((leaf_w, GP_FRAME_BAR, GP_FRAME_BAR)),
            origin=Origin(xyz=(glass_cx, 0.0, GP_PANEL_BOT_Z - GP_FRAME_BAR / 2.0)),
            material=m["chrome"],
            name="frame_bottom", material_class_id="metal.chrome_polished",
        )
        leaf.visual(
            Box((GP_FRAME_BAR, GP_FRAME_BAR, GP_PANEL_H + 2.0 * GP_FRAME_BAR)),
            origin=Origin(
                xyz=(sign * (GP_POST_R + GP_CLEAR + leaf_w + GP_FRAME_BAR / 2.0), 0.0, glass_cz)
            ),
            material=m["chrome"],
            name="frame_free_edge", material_class_id="metal.chrome_polished",
        )
        # hinge clips wrap the post (captured hinge) + a low foot at the pivot.
        clip_r = GP_POST_R + GP_CLEAR + GP_FRAME_BAR
        z_stagger = 0.0 if sign > 0 else 0.045
        for i, clip_z in enumerate(
            (
                GP_PANEL_BOT_Z + 0.07 + z_stagger,
                glass_cz + z_stagger,
                panel_top_z - 0.09 + z_stagger,
            )
        ):
            leaf.visual(
                Box((clip_r, GP_FRAME_BAR, 0.04)),
                origin=Origin(xyz=(sign * clip_r / 2.0, 0.0, clip_z)),
                material=m["chrome"],
                name=f"hinge_clip_{i}", material_class_id="metal.chrome_polished",
            )
        leaf.visual(
            Cylinder(radius=GP_POST_R + GP_CLEAR + 0.006, length=GP_PANEL_BOT_Z + 0.06),
            origin=Origin(xyz=(0.0, 0.0, (GP_PANEL_BOT_Z + 0.06) / 2.0)),
            material=m["chrome"],
            name="hinge_foot", material_class_id="metal.chrome_polished",
        )
        leaf.inertial = Inertial.from_geometry(
            Box((leaf_w, GP_PANEL_THK, GP_PANEL_H)),
            mass=6.0,
            origin=Origin(xyz=(glass_cx, 0.0, glass_cz)),
        )
        if twin:
            lower, upper = (0.0, TWIN_LEAF_CAP) if sign > 0 else (-TWIN_LEAF_CAP, 0.0)
        else:
            lower, upper = (0.0, math.pi / 2.0) if sign > 0 else (-math.pi / 2.0, 0.0)
        model.articulation(
            f"glass_leaf_swing_{leaf_start + k}",
            ArticulationType.REVOLUTE,
            parent=post,
            child=leaf,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=20.0, velocity=2.0, lower=lower, upper=upper),
        )


def _build_lane_curb_post(
    model: ArticulatedObject,
    r: ResolvedTripodTurnstileConfig,
    m: dict,
    *,
    index: int,
    rail_x: float,
) -> Part:
    """Minimal Y-running curb post: the lane-defining opposing element that is
    always built even when barrier='none', so the passage always reads.  Long
    axis is Y (parallel to travel) to satisfy the rails-along-Y invariant.
    """
    post = model.part(f"side_railing_{index}")
    curb_len = 0.50
    post.visual(
        Box((0.05, curb_len, 0.10)),
        origin=Origin(xyz=(0.0, 0.0, 0.05)),
        material=m["body_dark"],
        name="frame", material_class_id="metal.paint_coated",
    )
    for f, fy in enumerate((-curb_len / 2.0 + 0.04, curb_len / 2.0 - 0.04)):
        post.visual(
            Box((0.07, 0.06, 0.02)),
            origin=Origin(xyz=(0.0, fy, 0.01)),
            material=m["body_dark"],
            name=f"curb_foot_{f}", material_class_id="metal.paint_coated",
        )
    post.visual(
        Cylinder(radius=0.05, length=0.03),
        origin=Origin(xyz=(0.0, 0.0, 0.015)),
        material=m["body_dark"],
        name="mount_pad", material_class_id="metal.paint_coated",
    )
    post.inertial = Inertial.from_geometry(
        Box((0.05, curb_len, 0.10)), mass=6.0, origin=Origin(xyz=(0.0, 0.0, 0.05))
    )
    # bolted onto the shared base plate (provides parent geometry under the joint —
    # no connector bar).
    model.articulation(
        f"railing_mount_{index}",
        ArticulationType.FIXED,
        parent=model.get_part("cabinet"),
        child=post,
        origin=Origin(xyz=(rail_x, 0.0, 0.015)),
    )
    return post


def _build_barrier(
    model: ArticulatedObject, r: ResolvedTripodTurnstileConfig, m: dict, plan: list[dict]
) -> None:
    """Build the lane-defining opposing elements.  Guide rails ALWAYS run with
    long axis Y (parallel to travel).  A rail/curb is placed across every lane
    whose opposing element is NOT an adjacent pedestal, so the passage always
    reads — even when ``barrier == 'none'`` (then a minimal curb post)."""
    lanes = lane_plan(r)

    if r.barrier == "glass_swing_panel":
        # A glass swing gate IN FRONT of each turnstile: one hinge post CENTERED on
        # the turnstile, GATE_FRONT_Y ahead of it, with one leaf per arm face (1:1:
        # single-side -> 1 leaf, twin -> 2 leaves).  (glass is only sampled for K=1 /
        # twin, i.e. a single pedestal.)  Flush (non-arm) ends still get a curb.
        gate_idx = 0
        leaf_idx = 0
        curb_idx = 0
        for ped in pedestal_plan(r):
            if not ped["faces"]:
                continue
            _build_glass_gate(
                model,
                r,
                m,
                gate_index=gate_idx,
                leaf_start=leaf_idx,
                post_cx=ped["cx"],
                sides=ped["faces"],
            )
            leaf_idx += len(ped["faces"])
            gate_idx += 1
        for lane in lanes:
            if not lane.get("is_passage") and lane.get("rail_x") is not None:
                _build_lane_curb_post(model, r, m, index=curb_idx, rail_x=lane["rail_x"])
                curb_idx += 1
        return

    idx = 0
    for lane in lanes:
        if lane["kind"] == "corridor":
            # front-mount: two Y-running rails flanking the +Y corridor.
            for rx in lane["rail_xs"]:
                _build_lane_rail(
                    model, r, m, index=idx, rail_x=rx, rail_len=lane["rail_len"], is_passage=True
                )
                idx += 1
            continue
        if lane.get("rail_x") is None:
            # bank interior lane: opposing element is the next pedestal, no rail.
            continue
        _build_lane_rail(
            model,
            r,
            m,
            index=idx,
            rail_x=lane["rail_x"],
            rail_len=lane["rail_len"],
            is_passage=lane.get("is_passage", True),
        )
        idx += 1


def _build_lane_rail(
    model: ArticulatedObject,
    r: ResolvedTripodTurnstileConfig,
    m: dict,
    *,
    index: int,
    rail_x: float,
    rail_len: float,
    is_passage: bool,
) -> None:
    """One opposing lane element.  With a railing barrier (tube/extended) BOTH the
    passage sides AND the flush (non-arm) outer ends get a full Y-running guide rail
    so the whole bank is closed off by railings at both ends (the user's "leftmost
    side also needs a railing").  With barrier=none, a flush side gets a minimal
    curb post."""
    if r.barrier == "none":
        _build_lane_curb_post(model, r, m, index=index, rail_x=rail_x)
        return
    length = 1.50 if r.barrier == "extended_guide_railings" else rail_len
    _build_one_railing(model, m, index=index, rail_x=rail_x, rail_len=length)


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #


def build_tripod_turnstile(
    config: TripodTurnstileConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or TripodTurnstileConfig()
    r = resolve_config(cfg)
    plan = hub_plan(r)
    object.__setattr__(r, "hub_world", plan)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _register_materials(model, r.palette)
    cabinet = _build_cabinet(model, r, mats, plan)
    _emit_hub_joints(model, cabinet, r, mats, plan)
    _build_barrier(model, r, mats, plan)
    return model


def build_seeded_tripod_turnstile(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_tripod_turnstile(config_from_seed(seed), assets=assets)


def slot_choices_for_config(config: TripodTurnstileConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    bank = r.bank_style if (r.rotor_mount == "side_face_outward" and r.hub_count >= 2) else "na"
    return [
        ("pedestal_form", r.pedestal_form),
        ("rotor_mount", r.rotor_mount),
        ("bank_style", bank),
        ("arm_mechanism", r.arm_mechanism),
        ("arm_splay", r.arm_splay),
        ("barrier", r.barrier),
        ("hub_count", f"n{r.hub_count}"),
        ("arm_count", f"a{r.arm_count}"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests / QC
# --------------------------------------------------------------------------- #


def _arm_local_dir(phase_deg: float, q: float) -> tuple[float, float, float]:
    ph = math.radians(phase_deg) + q
    return (_CB * math.cos(ph), _CB * math.sin(ph), _SB)


def run_tripod_turnstile_tests(
    object_model: ArticulatedObject,
    config: TripodTurnstileConfig,
) -> TestReport:
    r = resolve_config(config)
    plan = hub_plan(r)
    ctx = TestContext(object_model)

    cabinet = object_model.get_part("cabinet")

    # ---- captured hub-collar -> boss seat (element-scoped, Rule 2). ----
    for hub in plan:
        hub_part = object_model.get_part(f"tripod_hub_{hub['index']}")
        hub_core = hub_part.get_visual("hub_core")
        boss = cabinet.get_visual(f"rotor_boss_{hub['index']}")
        ctx.allow_overlap(
            hub_part,
            cabinet,
            elem_a=hub_core,
            elem_b=boss,
            reason=(
                f"hub {hub['index']} collar seats flush on the bearing boss "
                "face; the interface plane is tilted so AABBs overlap without "
                "real penetration"
            ),
        )
        # For the anti-panic mechanism the boss is recessed and the hub rides on
        # the captured drop carrier (bracket↔boss + hub↔bracket contact checked
        # below), so the hub core does not need to touch the boss directly.
        if r.arm_mechanism != "anti_panic_drop_arm":
            ctx.expect_contact(hub_part, cabinet, elem_a=hub_core, elem_b=boss, contact_tol=5e-4)

    # ---- anti-panic carrier captured at the boss/hub seat (drop pivot). ----
    if r.arm_mechanism == "anti_panic_drop_arm":
        for hub in plan:
            carrier = object_model.get_part(f"arm_carrier_{hub['index']}")
            hub_part = object_model.get_part(f"tripod_hub_{hub['index']}")
            bracket = carrier.get_visual("bracket")
            boss = cabinet.get_visual(f"rotor_boss_{hub['index']}")
            # carrier hinge barrel is captured at the cabinet boss seat.
            ctx.allow_overlap(
                carrier,
                cabinet,
                elem_a=bracket,
                elem_b=boss,
                reason="drop carrier hinge barrel is captured at the boss seat",
            )
            ctx.expect_contact(carrier, cabinet, elem_a=bracket, elem_b=boss, contact_tol=5e-4)
            # hub assembly rides on the carrier barrel: the drop pivot passes
            # through the hub center, so the hub collar and the inboard arm roots
            # both wrap the captured barrel.
            for vis in hub_part.visuals:
                ctx.allow_overlap(
                    hub_part,
                    carrier,
                    elem_a=vis,
                    elem_b=bracket,
                    reason="hub collar / arm roots wrap the captured drop-carrier hinge barrel",
                )
            ctx.expect_contact(
                hub_part,
                carrier,
                elem_a=hub_part.get_visual("hub_core"),
                elem_b=bracket,
                contact_tol=5e-4,
            )

    plate = cabinet.get_visual("base_plate")

    # ---- glass swing gate: hinge posts stand IN FRONT on the base plate; leaves
    # wrap their post (captured hinge); twin leaves share the hinge line. ----
    if r.barrier == "glass_swing_panel":
        glass_posts = [p for p in object_model.parts if p.name.startswith("glass_post_")]
        glass_leaves = [p for p in object_model.parts if p.name.startswith("glass_leaf_")]
        for post in glass_posts:
            for pe in ("post_flange", "hinge_post"):
                ctx.allow_overlap(
                    post,
                    cabinet,
                    elem_a=post.get_visual(pe),
                    elem_b=plate,
                    reason="glass hinge post is bolted onto the base plate",
                )
        for leaf in glass_leaves:
            for vis in leaf.visuals:
                if not vis.name.startswith(("hinge_clip", "hinge_foot")):
                    continue
                for post in glass_posts:
                    for pe in ("hinge_post", "post_cap", "post_flange"):
                        ctx.allow_overlap(
                            leaf,
                            post,
                            elem_a=vis,
                            elem_b=post.get_visual(pe),
                            reason="glass leaf hinge clip/foot wraps its hinge post",
                        )
                if vis.name == "hinge_foot":
                    ctx.allow_overlap(
                        leaf,
                        cabinet,
                        elem_a=vis,
                        elem_b=plate,
                        reason="glass leaf hinge foot sits on the base plate",
                    )
        # twin: two leaves co-located at the same post — allow any pairing where
        # either side is a hinge element (a pane meets the other leaf's hinge foot).
        for i in range(len(glass_leaves)):
            for j in range(i + 1, len(glass_leaves)):
                a, b = glass_leaves[i], glass_leaves[j]
                for va in a.visuals:
                    for vb in b.visuals:
                        if va.name.startswith(("hinge_clip", "hinge_foot")) or vb.name.startswith(
                            ("hinge_clip", "hinge_foot")
                        ):
                            ctx.allow_overlap(
                                a,
                                b,
                                elem_a=va,
                                elem_b=vb,
                                reason="twin glass leaves share the hinge line on the post",
                            )

    # ---- rails / curbs sit on the shared base plate (no connector bar). ----
    base_vis = [
        v
        for v in cabinet.visuals
        if v.name.startswith(
            ("base_plate", "base_plinth", "post_body", "column_shell", "head_shell")
        )
    ]
    for p in object_model.parts:
        if not p.name.startswith("side_railing_"):
            continue
        feet = [
            v
            for v in p.visuals
            if v.name in ("mount_pad", "mount_stub", "frame")
            or v.name.startswith(("curb_foot", "floor_flange", "flange_collar", "baluster"))
        ]
        for ev in feet:
            for tgt in base_vis:
                ctx.allow_overlap(
                    p,
                    cabinet,
                    elem_a=ev,
                    elem_b=tgt,
                    reason="rail/curb foot is bolted onto the base plate / abuts the pedestal base",
                )
        try:
            ctx.expect_contact(
                p, cabinet, elem_a=p.get_visual("mount_pad"), elem_b=plate, contact_tol=5e-4
            )
        except Exception:
            pass

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}

    # ---- identity: cabinet + >=1 hub + a continuous spin per hub. ----
    if "cabinet" not in part_names:
        ctx.fail("identity_cabinet", "turnstile must have a fixed `cabinet` part")
    if not any(n.startswith("tripod_hub_") for n in part_names):
        ctx.fail("identity_hub", "turnstile must have at least one `tripod_hub_*` part")

    spin_joints = [
        object_model.get_articulation(j) for j in joint_names if j.startswith("rotor_spin_")
    ]
    ctx.check(
        "one continuous spin joint per hub (one per arm face)",
        len(spin_joints) == len(plan)
        and all(
            j.articulation_type == ArticulationType.CONTINUOUS and j.axis == (0.0, 0.0, 1.0)
            for j in spin_joints
        ),
        details=f"n_spin={len(spin_joints)}, n_hubs={len(plan)}, hub_count(K)={r.hub_count}",
    )

    # ---- spin axis world orientation matches the mount family. ----
    for hub in plan:
        spin = object_model.get_articulation(f"rotor_spin_{hub['index']}")
        if r.arm_mechanism == "anti_panic_drop_arm":
            # spin origin is in the carrier frame (rpy only); the carrier's drop
            # joint contributes the cabinet-level placement, so check axis only.
            ctx.check(
                f"hub {hub['index']} spin is continuous about local +Z",
                spin.axis == (0.0, 0.0, 1.0),
                details=f"axis={spin.axis}",
            )
            drop = object_model.get_articulation(f"arm_drop_{hub['index']}")
            ctx.check(
                f"hub {hub['index']} drop is a bounded horizontal REVOLUTE",
                drop.articulation_type == ArticulationType.REVOLUTE
                and abs(drop.axis[2]) < 1e-9
                and drop.motion_limits is not None
                and drop.motion_limits.upper is not None,
                details=f"drop_axis={drop.axis}, limits={drop.motion_limits}",
            )
        else:
            mm = _rpy_to_matrix(spin.origin.rpy)
            world_axis = _matvec(mm, (0.0, 0.0, 1.0))
            exp = hub["axis"]
            ctx.check(
                f"hub {hub['index']} spin axis points along the mount direction",
                abs(world_axis[0] - exp[0]) < 1e-6
                and abs(world_axis[1] - exp[1]) < 1e-6
                and abs(world_axis[2] - exp[2]) < 1e-6,
                details=f"world_axis={world_axis}, expected={exp}",
            )

    # ---- each hub carries arm_count arms, spaced evenly, moving with hub. ----
    for hub in plan:
        hub_part = object_model.get_part(f"tripod_hub_{hub['index']}")
        arms = [v for v in hub_part.visuals if v.name.startswith("arm_")]
        ctx.check(
            f"hub {hub['index']} has exactly {r.arm_count} arms",
            len(arms) == r.arm_count,
            details=f"arms={[v.name for v in arms]}",
        )

    # arm motion: pick hub 0 and verify arm_0 tip moves under a spin pose.
    hub0 = object_model.get_part("tripod_hub_0")
    spin0 = object_model.get_articulation("rotor_spin_0")

    def _arm0_center() -> tuple[float, float, float] | None:
        aabb = ctx.part_element_world_aabb(hub0, elem="arm_0")
        if aabb is None:
            return None
        (x0, y0, z0), (x1, y1, z1) = aabb
        return ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)

    rest = _arm0_center()
    spin_amt = (2.0 * math.pi / r.arm_count) * 0.5
    with ctx.pose({spin0: spin_amt}):
        rotated = _arm0_center()
    if rest is not None and rotated is not None:
        moved = math.dist(rest, rotated) > 0.05
        ctx.check(
            "arm_0 moves with the rotor when spun",
            moved,
            details=f"rest={rest}, rotated={rotated}",
        )

    # ---- arm sweep clearance: every arm tip stays above the floor over a
    # full rotation (derived from the cone kinematics). ----
    for hub in plan:
        mm = _rpy_to_matrix(hub["rpy"])
        axis_world = _matvec(mm, (0.0, 0.0, 1.0))
        start_z = hub["xyz"][2] + ARM_START_Z * axis_world[2]
        worst_floor = None
        for step in range(72):
            q = step * math.radians(5.0)
            for phase in _arm_phases(r.arm_count):
                d_world = _matvec(mm, _arm_local_dir(phase, q))
                tip_z = start_z + (r.arm_l + ARM_R) * d_world[2]
                worst_floor = tip_z if worst_floor is None else min(worst_floor, tip_z)
        ctx.check(
            f"hub {hub['index']} arm tips clear the floor over the full sweep",
            worst_floor is not None and worst_floor > 0.03,
            details=f"worst_floor={worst_floor:.4f}",
        )

    # ===================================================================== #
    # LANE SEMANTICS INVARIANTS — a tripod turnstile is a controlled single-
    # person passage.  These enforce that the geometry actually reads as lanes,
    # not "posts with spinning arms" (the topology gate alone does not).
    # ===================================================================== #
    lanes = lane_plan(r)
    peds = pedestal_plan(r)

    def _railing_parts():
        return [p for p in object_model.parts if p.name.startswith("side_railing_")]

    # ---- Test C: every railing/curb part runs PARALLEL to travel (long axis Y):
    # span_y > 2 * span_x. ----
    for rail in _railing_parts():
        aabb = ctx.part_world_aabb(rail)
        ok = False
        if aabb is not None:
            (x0, y0, _), (x1, y1, _) = aabb
            span_x = x1 - x0
            span_y = y1 - y0
            ok = span_y > 2.0 * span_x
        ctx.check(
            f"{rail.name} runs parallel to travel (long axis Y, span_y > 2*span_x)",
            ok,
            details=f"aabb={aabb}",
        )

    # ---- Test A: every PASSAGE lane is person-width — ~lane_width for a single-
    # arm lane, ~2x lane_width for a double-arm (ends_double) lane. ----
    lw = r.lane_width
    for li, lane in enumerate(lanes):
        if not lane.get("is_passage"):
            continue
        width = lane["gap"][1] - lane["gap"][0]
        double = r.bank_style == "ends_in_middle_double" and lane["kind"] == "between"
        target = 2.0 * lw if double else lw
        ctx.check(
            f"passage lane {li} ({lane['kind']}) is person-width (~{target:.2f} m)",
            target - 0.10 <= width <= target + 0.10,
            details=f"width={width:.3f}, target={target:.3f}, gap={lane['gap']}",
        )

    # ---- General rail-gap principle: a turnstile<->rail gap is a passage iff a
    # rotor arm reaches that side; otherwise the rail is FLUSH (<= ~0.12 m).
    # 'flush' lanes are the non-arm sides; their gap must be small. ----
    for li, lane in enumerate(lanes):
        if lane["kind"] != "flush":
            continue
        width = lane["gap"][1] - lane["gap"][0]
        ctx.check(
            f"non-arm side {li} rail sits flush against the pedestal (<= 0.12 m)",
            width <= 0.12,
            details=f"flush_gap={width:.3f}",
        )

    # ---- Test B: at rest (q=0) the blocking arm crosses its lane gap at waist
    # height — its world X-extent overlaps the lane span, z in [0.70,1.00]. ----
    if r.rotor_mount == "side_face_outward":
        # Map each side hub to the passage lane it guards (the lane whose gap is
        # immediately outboard of the hub's face in its arm direction).
        passage_lanes = [
            lane for lane in lanes if lane.get("is_passage") and lane["kind"] != "corridor"
        ]
        for hub in plan:
            sign = hub["sign"]
            face_x = hub["ped_cx"] + sign * hub["ped_half"]
            # the lane this arm guards starts at face_x and extends in +sign.
            guarded = None
            for lane in passage_lanes:
                lo, hi = lane["gap"]
                near = lo if sign > 0 else hi
                if abs(near - face_x) < 0.06:
                    guarded = lane
                    break
            if guarded is None:
                continue
            hub_part = object_model.get_part(f"tripod_hub_{hub['index']}")
            # union the arm-tip AABBs to get the rotor's world X reach at rest.
            xs: list[float] = []
            zc: list[float] = []
            for j in range(r.arm_count):
                ab = ctx.part_element_world_aabb(hub_part, elem=f"arm_{j}")
                if ab is not None:
                    xs.extend([ab[0][0], ab[1][0]])
                    zc.append((ab[0][2] + ab[1][2]) / 2.0)
            if not xs:
                continue
            arm_x_lo, arm_x_hi = min(xs), max(xs)
            lo, hi = guarded["gap"]
            overlaps = arm_x_hi >= lo and arm_x_lo <= hi
            # up-splay: a cross-arm reaches waist (0.70-1.00). down-splay: arms sit
            # lower on the body and angle down (intentionally NOT waist), so just
            # require a blocking-height arm in [0.35, 1.05].
            z_lo = WAIST_Z_LO if r.arm_splay == "up" else 0.35
            z_hi = WAIST_Z_HI if r.arm_splay == "up" else 1.05
            at_height = any(z_lo <= z <= z_hi for z in zc)
            ctx.check(
                f"hub {hub['index']} arm crosses its lane gap at blocking height",
                overlaps and at_height,
                details=(
                    f"splay={r.arm_splay} arm_x=[{arm_x_lo:.3f},{arm_x_hi:.3f}] "
                    f"lane={guarded['gap']} arm_zc={[round(z, 2) for z in zc]}"
                ),
            )
    else:  # front corridor: the blocking arm projects +Y across the corridor.
        hub_part = object_model.get_part("tripod_hub_0")
        ab = ctx.part_element_world_aabb(hub_part, elem="arm_0")
        if ab is not None:
            arm_x_lo, arm_x_hi = ab[0][0], ab[1][0]
            lo, hi = lanes[0]["gap"]
            ctx.check(
                "front corridor blocking arm crosses the corridor span in X",
                arm_x_hi >= lo and arm_x_lo <= hi and ab[1][1] > 0.20,
                details=f"arm_x=[{arm_x_lo:.3f},{arm_x_hi:.3f}] corridor={lanes[0]['gap']}",
            )

    # ---- Test: all pedestals sit in ONE straight row (same Y, no stagger). ----
    cys = [p.get("cy", 0.0) for p in peds]
    ctx.check(
        "all pedestals are in one straight row (same Y, no stagger)",
        (max(cys) - min(cys)) < 0.02,
        details=f"cys={cys}",
    )

    # ---- Test: arms per passage lane.  uniform_single/twin -> exactly ONE arm
    # per lane.  ends_in_middle_double -> TWO opposing arms per lane that meet at
    # the lane centre forming one barrier (still passed once); both are aligned at
    # the same Y (enforced by the one-straight-row test above). ----
    if r.rotor_mount == "side_face_outward":
        n_faces = sum(len(p["faces"]) for p in peds)
        n_pass = sum(1 for lane in lanes if lane.get("is_passage"))
        expected = 2 * n_pass if r.bank_style == "ends_in_middle_double" else n_pass
        ctx.check(
            "arms-per-lane matches the bank style (1 for uniform/twin, 2 for ends_double)",
            n_faces == expected,
            details=f"passage_lanes={n_pass}, arm_faces={n_faces}, bank={r.bank_style}",
        )

    # ---- Test D: multi-lane gaps are walkable — adjacent pedestals are
    # separated by >= LANE_W_MIN. ----
    if len(peds) >= 2:
        cxs = [p["cx"] for p in peds]
        for i in range(len(peds) - 1):
            gap = (cxs[i + 1] - peds[i + 1]["half"]) - (cxs[i] + peds[i]["half"])
            ctx.check(
                f"bank pedestals {i},{i + 1} are separated by a walkable gap",
                gap >= LANE_W_MIN - 1e-6,
                details=f"gap={gap:.3f}",
            )
        # bank composition matches the sampled style.
        if r.bank_style == "ends_in_middle_double":
            ctx.check(
                "ends_in_middle_double: single-side ends facing inward, double-side middles",
                peds[0]["faces"] == [1]
                and peds[-1]["faces"] == [-1]
                and all(set(p["faces"]) == {1, -1} for p in peds[1:-1]),
                details=f"faces={[p['faces'] for p in peds]}",
            )
        else:  # uniform_single
            ctx.check(
                "uniform_single: every pedestal is single-side facing the same way",
                all(p["faces"] == [1] for p in peds),
                details=f"faces={[p['faces'] for p in peds]}",
            )

    # ---- Uniform rest-phase: every hub shares the same rest arm phase so the
    # bank reads orderly.  Same-facing hubs must show the same arm orientation. ----
    same_face = {}
    for hub in plan:
        hub_part = object_model.get_part(f"tripod_hub_{hub['index']}")
        ab = ctx.part_element_world_aabb(hub_part, elem="arm_0")
        if ab is None:
            continue
        # angle of arm_0 about the hub center in the dominant sweep plane.
        cx = (ab[0][0] + ab[1][0]) / 2.0 - hub["xyz"][0]
        cz = (ab[0][2] + ab[1][2]) / 2.0 - hub["xyz"][2]
        ang = round(math.atan2(cz, cx), 2)
        same_face.setdefault(hub["face"], []).append(ang)
    for face, angs in same_face.items():
        if len(angs) < 2:
            continue
        spread = max(angs) - min(angs)
        ctx.check(
            f"all face={face} hubs share the same rest arm orientation",
            spread < 0.05,
            details=f"angles={angs}",
        )

    # ---- barrier joints + glass 1:1 correspondence with the turnstile arms. ----
    if r.barrier == "glass_swing_panel":
        leaves = [p for p in object_model.parts if p.name.startswith("glass_leaf_")]
        n_faces = sum(len(p["faces"]) for p in peds)
        ctx.check(
            "one glass leaf per turnstile arm (single-side->1, twin->2)",
            len(leaves) == n_faces,
            details=f"glass_leaves={len(leaves)}, arm_faces={n_faces}",
        )
        swing_joints = [j for j in joint_names if j.startswith("glass_leaf_swing_")]
        for jn in swing_joints:
            j = object_model.get_articulation(jn)
            ctx.check(
                f"{jn} is a vertical-axis REVOLUTE",
                j.articulation_type == ArticulationType.REVOLUTE and j.axis == (0.0, 0.0, 1.0),
                details=f"type={j.articulation_type}, axis={j.axis}",
            )
        # free-standing: there must be NO foot-strut/connector tying glass to a pedestal.
        ctx.check(
            "glass gate has no bottom connector strut back to the pedestal",
            not any(v.name == "post_foot_strut" for v in cabinet.visuals),
            details="post_foot_strut must not exist",
        )

    # ---- overall sanity: waist-high. ----
    cab_aabb = ctx.part_world_aabb(cabinet)
    ctx.check(
        "cabinet tops out near waist height (~1 m)",
        cab_aabb is not None and 0.85 < cab_aabb[1][2] < 1.12 and cab_aabb[0][2] > -0.01,
        details=f"cabinet_aabb={cab_aabb}",
    )

    return ctx.report()


__all__ = [
    "TripodTurnstileConfig",
    "ResolvedTripodTurnstileConfig",
    "build_tripod_turnstile",
    "build_seeded_tripod_turnstile",
    "config_from_seed",
    "resolve_config",
    "run_tripod_turnstile_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
