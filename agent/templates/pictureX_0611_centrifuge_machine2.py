# SPDX-License-Identifier: Apache-2.0

"""pictureX/0611/centrifuge_machine2 — modular procedural template.

Manually cranked laboratory hand centrifuge: an EXPOSED (no lid, no motor)
vertical rotor is driven through a gearbox by a hand input (offset crank,
long spline crank, or spoked rim handwheel); the rotor carries swing-out
tube shields/buckets or fixed-angle tube sleeves; the machine stands on a
weighted pedestal, an integral table clamp, or a bench tripod.

Slots (see specs_modular_v1/pictureX_0611_centrifuge_machine2.md):

* Slot A ``support_base`` — weighted_pedestal | table_clamp (+clamp_screw
  PRISMATIC) | bench_tripod                                (① skeleton)
* Slot B ``body_form``    — open_shoulder_mast | enclosed_rounded_gearcase |
  drum_gearbox_crown (+drive_shaft chain)   (③ Primary Form Family, ①② too)
* Slot C ``drive_input``  — offset_crank (+free knob) | spline_crank |
  rim_handwheel (+free rim grip)                           (② mechanism)
* Slot D ``carrier``      — plate_swing (N∈{4,6}) | bar_fork_swing (N∈{2,4})
  | fixed_sleeve (N∈{4,6})                       (② mechanism + multiplicity)

Kinematics per source family: open/enclosed bodies gear the rotor to the
hand input via a Mimic ×4 (001 family); the drum body uses an independent
drive_shaft → rotor CONTINUOUS chain with no mimic (002 family). All eight
5-star sources were read in full; geometry keeps the source primitive
sophistication (cadquery lofts / LatheGeometry / spline tube — no Box
downgrades).

Distinct-identity note vs pictureX_0611_centrifuge_machine1: that template is
the powered, lidded benchtop family. This template must never grow a lid, a
motor, or an enclosing dome; the rotor stays exposed and hand-driven.
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
    LatheGeometry,
    MatingContract,
    Mimic,
    MotionLimits,
    MotionProperties,
    Origin,
    Part,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

RGBA = tuple[float, float, float, float]

SupportBase = Literal["weighted_pedestal", "table_clamp", "bench_tripod"]
BodyForm = Literal["open_shoulder_mast", "enclosed_rounded_gearcase", "drum_gearbox_crown"]
DriveInput = Literal["offset_crank", "spline_crank", "rim_handwheel"]
Carrier = Literal["plate_swing", "bar_fork_swing", "fixed_sleeve"]
PaletteStyle = Literal[
    "mint_enamel", "aged_nickel_wood", "black_japanned_brass", "cream_lab_enamel",
    "hammertone_green",
]

SUPPORT_BASES: tuple[SupportBase, ...] = ("weighted_pedestal", "table_clamp", "bench_tripod")
BODY_FORMS: tuple[BodyForm, ...] = (
    "open_shoulder_mast", "enclosed_rounded_gearcase", "drum_gearbox_crown"
)
DRIVE_INPUTS: tuple[DriveInput, ...] = ("offset_crank", "spline_crank", "rim_handwheel")
CARRIERS: tuple[Carrier, ...] = ("plate_swing", "bar_fork_swing", "fixed_sleeve")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "mint_enamel", "aged_nickel_wood", "black_japanned_brass", "cream_lab_enamel",
    "hammertone_green",
)

# Bucket-count domain per carrier (§8 multiplicity; anchors N=2/4/6).
CARRIER_COUNTS: dict[Carrier, tuple[int, ...]] = {
    "plate_swing": (4, 6),        # 001 origin (4) + n6 fork (6)
    "bar_fork_swing": (2, 4),     # n2 fork (2) + 002 origin (4)
    "fixed_sleeve": (4, 6),       # rigid fork loop (4), same loop at 6
}

# --------------------------------------------------------------------------- #
# Shared layout constants (Contract 3c: single-sourced quantities, metres).
# Support modules top out at SUPPORT_MOUNT_Z and the body form builds upward
# from it; source pairs reproduce exactly (001: pedestal 0.014; 002: 0.150).
# --------------------------------------------------------------------------- #
SUPPORT_MOUNT_Z: dict[SupportBase, float] = {
    "weighted_pedestal": 0.014,
    "table_clamp": 0.150,
    "bench_tripod": 0.150,
}
# 001-family body (open/enclosed): crank boss centre & rotor bearing, relative
# to the body mount plane (001 source: crank z=0.103, rotor z=0.295, m=0.014).
SHOULDER_CRANK_DZ = 0.089
SHOULDER_ROTOR_DZ = 0.281
# 002-family drum body: crank at the drum disc centre; shaft joint at neck top
# (002 source: crank z=0.205, shaft z=0.309, m=0.150).
DRUM_CRANK_DZ = 0.055
DRUM_SHAFT_DZ = 0.159
DRUM_ROTOR_ABOVE_SHAFT = 0.145  # rotor_spin origin in drive_shaft local frame

GEAR_RATIO = 4.0  # rotor mimic multiplier (001/enclosed/handwheel sources)

# --------------------------------------------------------------------------- #
# Gearbox envelope stations: (dz above mount plane, half_x, half_y).
# SINGLE SOURCE (Contract 3c) for each 001-family body form: consumed both by
# the cadquery loft that builds the casting AND by _body_half_extent_in_band()
# below, so the derived crank standoff can never drift from the realized body.
# 001 L41-L50 (shoulder) / enclosed fork L41-L62 (gearcase); cq `.workplane`
# offsets are cumulative, so these dz values are the running sums.
# --------------------------------------------------------------------------- #
_SHOULDER_STATIONS: tuple[tuple[float, float, float], ...] = (
    (0.000, 0.055, 0.040),
    (0.046, 0.047, 0.034),
    (0.088, 0.028, 0.023),
)
_GEARCASE_STATIONS: tuple[tuple[float, float, float], ...] = (
    (0.001, 0.054, 0.042),
    (0.021, 0.064, 0.052),
    (0.049, 0.066, 0.054),
    (0.071, 0.056, 0.044),
    (0.089, 0.036, 0.028),
)
# 002 drum: the input-side face the crank bearing grows from. The gearbox_cover
# disc (L182-L186: centre y=-0.029, length 0.004) is the outermost face at
# |y|=0.031; the drum casting itself ends at |y|=0.028.
_DRUM_FACE_HALF_Y = 0.031
_DRUM_BEARING_ROOT_Y = 0.030  # drum face the bearing collar bridges from

# Crank-boss geometry (001 L64-L71 / enclosed fork L77-L83): the boss root sits
# at x=-0.025 on the gearbox flank and is extruded out to the input spin axis.
_BOSS_ROOT_X = 0.025

# Air gap between the input's rotating envelope and the gearbox casting.
# Basis: back-solved from the 001 source itself — the open shoulder's max
# half_x over the handwheel's swept z-band is 0.0493, the rim roller radius is
# 0.011, and the source's boss puts the spin axis at x=-0.064; 0.064 - 0.0493 -
# 0.011 = 0.0037 ~ 0.004. Deriving with this constant reproduces the source
# standoff for the source's own body and grows it for wider bodies.
_INPUT_BODY_CLEAR = 0.004

# The standoff each body form's source actually authored (001 L28 CRANK_AXIS x;
# 002 L231 crank_rotation origin y). The derivation below is a LOWER bound: a
# body form never pulls its input axis inboard of its own source value.
_SOURCE_STANDOFF: dict[BodyForm, float] = {
    "open_shoulder_mast": 0.064,
    "enclosed_rounded_gearcase": 0.064,
    "drum_gearbox_crown": 0.038,
}

# Drive-input reach (metres at scale 1.0) for the ground-clearance inequality.
# reach(s) = _REACH_A[drive] * s + _REACH_B[drive]  (outermost sweep radius).
_REACH_A: dict[DriveInput, float] = {
    "offset_crank": 0.0556,   # hypot(0.043, 0.035) handle offset (001)
    "spline_crank": 0.243,    # grip centre 0.211 + half grip length (002)
    "rim_handwheel": 0.045,   # rim radius (handwheel fork)
}
_REACH_B: dict[DriveInput, float] = {
    "offset_crank": 0.014,    # knob radius + ribs
    "spline_crank": 0.013,    # grip radius
    "rim_handwheel": 0.015,   # rim tube + grip roller
}

# Carrier pivot radii at scale 1.0.
PLATE_PIVOT_R = 0.058       # 001 ROTOR_RADIUS
PLATE_PIVOT_DZ = 0.042      # 001 BUCKET_PIVOT_Z
BAR_PIVOT_R = 0.092         # 002 pivot spec radius
SLEEVE_TILT = math.radians(35.0)  # rigid fork TUBE_TILT
SLEEVE_HUB_R = 0.015
SLEEVE_ARM_LEN = 0.055
SLEEVE_HUB_Z_MID = 0.041

PLATE_SWING_UPPER = 1.05                # rad (001)
BAR_SWING_UPPER = math.radians(72.0)    # (002)

PALETTES: dict[PaletteStyle, dict[str, RGBA]] = {
    "mint_enamel": {
        "enamel": (0.48, 0.78, 0.76, 1.0),
        "enamel_light": (0.68, 0.88, 0.84, 1.0),
        "metal": (0.66, 0.70, 0.69, 1.0),
        "polished": (0.82, 0.83, 0.80, 1.0),
        "dark_metal": (0.18, 0.22, 0.22, 1.0),
        "glass": (0.83, 0.95, 0.96, 0.34),
        "wood": (0.48, 0.30, 0.17, 1.0),
        "rubber": (0.08, 0.10, 0.10, 1.0),
        "label_white": (0.94, 0.95, 0.92, 1.0),
        "label_red": (0.72, 0.08, 0.08, 1.0),
        "label_blue": (0.04, 0.26, 0.42, 1.0),
    },
    "aged_nickel_wood": {
        "enamel": (0.68, 0.69, 0.67, 1.0),
        "enamel_light": (0.78, 0.79, 0.77, 1.0),
        "metal": (0.66, 0.67, 0.65, 1.0),
        "polished": (0.82, 0.83, 0.80, 1.0),
        "dark_metal": (0.20, 0.21, 0.20, 1.0),
        "glass": (0.80, 0.90, 0.92, 0.30),
        "wood": (0.48, 0.30, 0.17, 1.0),
        "rubber": (0.08, 0.075, 0.065, 1.0),
        "label_white": (0.90, 0.90, 0.87, 1.0),
        "label_red": (0.55, 0.10, 0.08, 1.0),
        "label_blue": (0.08, 0.22, 0.38, 1.0),
    },
    "black_japanned_brass": {
        "enamel": (0.09, 0.09, 0.10, 1.0),
        "enamel_light": (0.62, 0.50, 0.22, 1.0),
        "metal": (0.70, 0.58, 0.28, 1.0),
        "polished": (0.85, 0.74, 0.42, 1.0),
        "dark_metal": (0.14, 0.13, 0.12, 1.0),
        "glass": (0.85, 0.92, 0.90, 0.32),
        "wood": (0.40, 0.24, 0.12, 1.0),
        "rubber": (0.06, 0.06, 0.06, 1.0),
        "label_white": (0.90, 0.88, 0.80, 1.0),
        "label_red": (0.60, 0.10, 0.08, 1.0),
        "label_blue": (0.10, 0.20, 0.35, 1.0),
    },
    "cream_lab_enamel": {
        "enamel": (0.90, 0.87, 0.78, 1.0),
        "enamel_light": (0.95, 0.93, 0.86, 1.0),
        "metal": (0.68, 0.70, 0.70, 1.0),
        "polished": (0.83, 0.84, 0.82, 1.0),
        "dark_metal": (0.24, 0.25, 0.25, 1.0),
        "glass": (0.86, 0.94, 0.95, 0.32),
        "wood": (0.52, 0.34, 0.20, 1.0),
        "rubber": (0.09, 0.09, 0.09, 1.0),
        "label_white": (0.98, 0.97, 0.94, 1.0),
        "label_red": (0.70, 0.14, 0.10, 1.0),
        "label_blue": (0.10, 0.28, 0.48, 1.0),
    },
    "hammertone_green": {
        "enamel": (0.26, 0.40, 0.31, 1.0),
        "enamel_light": (0.44, 0.57, 0.46, 1.0),
        "metal": (0.62, 0.66, 0.64, 1.0),
        "polished": (0.80, 0.82, 0.80, 1.0),
        "dark_metal": (0.15, 0.18, 0.16, 1.0),
        "glass": (0.82, 0.93, 0.92, 0.33),
        "wood": (0.45, 0.28, 0.15, 1.0),
        "rubber": (0.07, 0.08, 0.07, 1.0),
        "label_white": (0.92, 0.93, 0.90, 1.0),
        "label_red": (0.68, 0.12, 0.10, 1.0),
        "label_blue": (0.08, 0.24, 0.42, 1.0),
    },
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _spline_allowed(support: SupportBase, body: BodyForm) -> bool:
    """The long 002 spline crank (sweep radius ~0.25 m) is legal only where its
    sweep matches the sources: hanging off a table clamp (bench-edge overhang,
    002/tripod-fork behaviour) or on a tall side-mounted gearbox with real
    ground clearance (tripod + non-drum body)."""
    if support == "table_clamp":
        return True
    return support == "bench_tripod" and body != "drum_gearbox_crown"


def _body_allowed(support: SupportBase, body: BodyForm) -> bool:
    """drum_gearbox_crown never sits on the weighted pedestal (no source pair;
    the low drum centre would drag the crank sweep across the base)."""
    return not (support == "weighted_pedestal" and body == "drum_gearbox_crown")


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class PictureX0611CentrifugeMachine2Config:
    support_base: SupportBase | None = None
    body_form: BodyForm | None = None
    drive_input: DriveInput | None = None
    carrier: Carrier | None = None
    bucket_count: int | None = None
    palette_style: PaletteStyle = "mint_enamel"
    input_reach_scale: float = 1.0
    carrier_radius_scale: float = 1.0
    tube_length_scale: float = 1.0
    name: str = "picturex_0611_centrifuge_machine2"


@dataclass(frozen=True)
class ResolvedCentrifugeMachine2Config:
    support_base: SupportBase
    body_form: BodyForm
    drive_input: DriveInput
    carrier: Carrier
    bucket_count: int
    palette_style: PaletteStyle
    input_reach_scale: float
    carrier_radius_scale: float
    tube_length_scale: float
    palette: dict[str, RGBA]
    name: str


@dataclass(frozen=True)
class _Layout:
    """Single-sourced world layout derived from support + body form."""

    mount_z: float          # body mount plane (top of the support module)
    input_standoff: float   # body centreline -> input spin axis (boss length)
    crank_pos: tuple[float, float, float]  # input joint origin (world)
    crank_yaw: float        # joint frame yaw: local +x (spin axis) -> world
    input_axis_world: tuple[float, float, float]
    rotor_parent: str       # "body" (geared/mimic) or "drive_shaft" (002 chain)
    rotor_joint_z: float    # world z of rotor_spin origin (body parent) or
    #                         drive_shaft-local z (drive_shaft parent)
    mimic: bool             # rotor mimics the hand input x GEAR_RATIO


def config_from_seed(seed: int) -> PictureX0611CentrifugeMachine2Config:
    rng = random.Random(seed)
    support: SupportBase = rng.choices(SUPPORT_BASES, weights=(2, 2, 1), k=1)[0]
    if support == "weighted_pedestal":
        body: BodyForm = rng.choice(
            ("open_shoulder_mast", "enclosed_rounded_gearcase")
        )
    else:
        # The drum gearbox is the classic clamp/tripod family (002 origin).
        body = rng.choices(BODY_FORMS, weights=(1, 1, 3), k=1)[0]
    if _spline_allowed(support, body):
        drive: DriveInput = rng.choices(DRIVE_INPUTS, weights=(3, 2, 2), k=1)[0]
    else:
        drive = rng.choices(("offset_crank", "rim_handwheel"), weights=(3, 2), k=1)[0]
    carrier: Carrier = rng.choices(CARRIERS, weights=(2, 2, 1), k=1)[0]
    bucket_count = rng.choices(CARRIER_COUNTS[carrier], weights=(3, 2), k=1)[0]
    palette_style: PaletteStyle = rng.choice(PALETTE_STYLES)
    return PictureX0611CentrifugeMachine2Config(
        support_base=support,
        body_form=body,
        drive_input=drive,
        carrier=carrier,
        bucket_count=bucket_count,
        palette_style=palette_style,
        input_reach_scale=round(rng.uniform(0.88, 1.12), 4),
        carrier_radius_scale=round(rng.uniform(0.94, 1.10), 4),
        tube_length_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"picturex_0611_centrifuge_machine2_seed_{seed}",
    )


def _crank_mount_z(support: SupportBase, body: BodyForm) -> float:
    m = SUPPORT_MOUNT_Z[support]
    if body == "drum_gearbox_crown":
        return m + DRUM_CRANK_DZ
    return m + SHOULDER_CRANK_DZ


def resolve_config(
    config: PictureX0611CentrifugeMachine2Config,
) -> ResolvedCentrifugeMachine2Config:
    support = config.support_base or "weighted_pedestal"
    body = config.body_form or "open_shoulder_mast"
    drive = config.drive_input or "offset_crank"
    carrier = config.carrier or "plate_swing"
    palette_style = (
        config.palette_style if config.palette_style in PALETTES else "mint_enamel"
    )
    if support not in SUPPORT_BASES:
        raise ValueError(f"Unsupported support_base: {support!r}")
    if body not in BODY_FORMS:
        raise ValueError(f"Unsupported body_form: {body!r}")
    if drive not in DRIVE_INPUTS:
        raise ValueError(f"Unsupported drive_input: {drive!r}")
    if carrier not in CARRIERS:
        raise ValueError(f"Unsupported carrier: {carrier!r}")

    # Compatibility gating (spec §5): fall back deterministically for
    # hand-written configs; config_from_seed only emits legal combos.
    if not _body_allowed(support, body):
        body = "open_shoulder_mast"
    if drive == "spline_crank" and not _spline_allowed(support, body):
        drive = "offset_crank"

    counts = CARRIER_COUNTS[carrier]
    bucket_count = config.bucket_count if config.bucket_count in counts else counts[0]

    reach_scale = _clamp(config.input_reach_scale, 0.88, 1.12)
    # Ground-clearance inequality: freestanding supports must keep the input
    # sweep above the floor; the table clamp overhangs the bench edge (002
    # source behaviour) and is exempt.
    if support != "table_clamp":
        crank_z = _crank_mount_z(support, body)
        max_reach = crank_z - 0.010
        a, b = _REACH_A[drive], _REACH_B[drive]
        if a * reach_scale + b > max_reach:
            reach_scale = max(0.60, (max_reach - b) / a)

    radius_scale = _clamp(config.carrier_radius_scale, 0.94, 1.10)
    tube_scale = _clamp(config.tube_length_scale, 0.90, 1.10)

    return ResolvedCentrifugeMachine2Config(
        support_base=support,
        body_form=body,
        drive_input=drive,
        carrier=carrier,
        bucket_count=bucket_count,
        palette_style=palette_style,
        input_reach_scale=round(reach_scale, 4),
        carrier_radius_scale=radius_scale,
        tube_length_scale=tube_scale,
        palette=dict(PALETTES[palette_style]),
        name=config.name,
    )


def _input_sweep(r: ResolvedCentrifugeMachine2Config) -> tuple[float, float]:
    """``(sweep_radius, inboard_half_depth)`` of the input's rotating envelope.

    ``sweep_radius`` is how far the input's spinning geometry reaches from its
    spin axis; ``inboard_half_depth`` is how far that geometry extends from the
    wheel/mount plane *toward the body*. Only the handwheel is coplanar with its
    mount plane, which is why only it can sweep into a wide gearbox.
    """
    if r.drive_input == "rim_handwheel":
        # handwheel fork L176-L181 (torus rim, radius `rim_r`, tube r=0.005) and
        # L327-L332 (roller sleeve r=0.011 at the rim): both straddle the wheel
        # plane, so the pair sweeps a disc of radius rim_r+0.011 right at it.
        return (0.045 * r.input_reach_scale + 0.011, 0.011)
    if r.drive_input == "offset_crank":
        # 001 L249-L274: only the hub (r=0.010) sits at the mount plane; the
        # arm, handle pin and knob are all outboard (local x <= -0.018).
        return (0.010, 0.0)
    # spline_crank, 002 L100-L144: hub r=0.011 at the plane, arm sweeps outboard.
    return (0.011, 0.0)


def _stations_half_extent(
    stations: tuple[tuple[float, float, float], ...],
    axis_index: int,
    dz_lo: float,
    dz_hi: float,
) -> float:
    """Max half-extent of a lofted ellipse stack over the band ``[dz_lo, dz_hi]``.

    cadquery lofts ellipse sections with ruled (linear) surfaces, so linear
    interpolation between stations is exact. The extremum over a band is always
    at a band end or at an enclosed station, so those are the only samples.
    """
    half = 1 + axis_index  # station tuple is (dz, half_x, half_y)

    def at(dz: float) -> float:
        if dz <= stations[0][0] or dz >= stations[-1][0]:
            return 0.0
        for (z0, *h0), (z1, *h1) in zip(stations, stations[1:]):
            if z0 <= dz <= z1:
                t = 0.0 if z1 == z0 else (dz - z0) / (z1 - z0)
                return h0[axis_index] + (h1[axis_index] - h0[axis_index]) * t
        return 0.0

    samples = [at(dz_lo), at(dz_hi)]
    samples += [s[half] for s in stations if dz_lo <= s[0] <= dz_hi]
    return max(samples)


def _input_standoff(r: ResolvedCentrifugeMachine2Config) -> float:
    """Distance from the body centreline to the input spin axis (crank boss length).

    Contract 3e: this is a RELATION between the input and the gearbox — the boss
    must hold the input's rotating envelope clear of the casting — not a frozen
    constant. The 001 handwheel fork only ever met the *open shoulder* body, so
    its authored 0.064 silently buried the rim grip inside the wider enclosed
    gearcase and the 002 drum. Derived here, and floored at each body form's own
    source value so a body never pulls its input inboard of what it authored.
    """
    sweep_r, inboard = _input_sweep(r)
    floor = _SOURCE_STANDOFF[r.body_form]
    if r.body_form == "drum_gearbox_crown":
        # The drum's input face is flat and the spin axis sits on the drum's own
        # centreline, so the whole sweep disc faces the cover: clear the cover.
        required = _DRUM_FACE_HALF_Y + inboard + _INPUT_BODY_CLEAR
    else:
        stations = (
            _SHOULDER_STATIONS
            if r.body_form == "open_shoulder_mast"
            else _GEARCASE_STATIONS
        )
        dz = SHOULDER_CRANK_DZ
        required = (
            _stations_half_extent(stations, 0, dz - sweep_r, dz + sweep_r)
            + inboard
            + _INPUT_BODY_CLEAR
        )
    return max(floor, required)


def _layout(r: ResolvedCentrifugeMachine2Config) -> _Layout:
    m = SUPPORT_MOUNT_Z[r.support_base]
    standoff = _input_standoff(r)
    if r.body_form == "drum_gearbox_crown":
        # 002 family: front-face crank (axis y), drive_shaft chain, no mimic.
        return _Layout(
            mount_z=m,
            input_standoff=standoff,
            crank_pos=(0.0, -standoff, m + DRUM_CRANK_DZ),
            crank_yaw=math.pi / 2.0,
            input_axis_world=(0.0, 1.0, 0.0),
            rotor_parent="drive_shaft",
            rotor_joint_z=DRUM_ROTOR_ABOVE_SHAFT,
            mimic=False,
        )
    # 001 family: side crank boss (axis x), rotor geared to the input.
    return _Layout(
        mount_z=m,
        input_standoff=standoff,
        crank_pos=(-standoff, -0.004, m + SHOULDER_CRANK_DZ),
        crank_yaw=0.0,
        input_axis_world=(1.0, 0.0, 0.0),
        rotor_parent="body",
        rotor_joint_z=m + SHOULDER_ROTOR_DZ,
        mimic=True,
    )


# --------------------------------------------------------------------------- #
# Support solids (Slot A) — unioned with the body-form solid into one casting.
# --------------------------------------------------------------------------- #
def _pedestal_solid() -> cq.Workplane:
    """001 L34-L40: low rounded rectangular cast base."""
    return (
        cq.Workplane("XY")
        .rect(0.130, 0.095)
        .extrude(0.018)
        .edges("|Z")
        .fillet(0.012)
    )


def _clamp_solid() -> cq.Workplane:
    """002 L47-L56: compact C-clamp cast into the rear/lower gearbox side."""
    spine = cq.Workplane("XY").box(0.028, 0.050, 0.132).translate((-0.041, 0.0, 0.111))
    upper_jaw = cq.Workplane("XY").box(0.092, 0.052, 0.015).translate((-0.009, 0.0, 0.128))
    lower_arm = cq.Workplane("XY").box(0.092, 0.052, 0.015).translate((-0.009, 0.0, 0.047))
    boss = (
        cq.Workplane("XY")
        .circle(0.012)
        .extrude(0.025)
        .translate((0.018, 0.0, 0.034))
    )
    return spine.union(upper_jaw).union(lower_arm).union(boss)


def _tripod_solid() -> cq.Workplane:
    """tripod fork L46-L68: pedestal column + weighted hub + fillet ring.

    Column extended slightly past the mount plane so it embeds into the body
    form's lowest solid (same part; overlap is intentional, mirrors the 002
    spine∪drum union)."""
    column = (
        cq.Workplane("XY")
        .circle(0.016)
        .extrude(0.115)
        .translate((0.0, 0.0, 0.043))
    )
    hub = (
        cq.Workplane("XY")
        .circle(0.042)
        .extrude(0.020)
        .translate((0.0, 0.0, 0.023))
    )
    fillet_ring = (
        cq.Workplane("XY")
        .circle(0.022)
        .extrude(0.008)
        .translate((0.0, 0.0, 0.043))
    )
    return column.union(hub).union(fillet_ring)


# --------------------------------------------------------------------------- #
# Body-form solids (Slot B) — built above the mount plane ``m``.
# --------------------------------------------------------------------------- #
def _loft_stations(stations: tuple[tuple[float, float, float], ...], m: float) -> cq.Workplane:
    """Loft the shared (dz, half_x, half_y) envelope stations into a solid.

    Single consumer-side of the Contract 3c station data: the same tuples drive
    `_stations_half_extent`, so the crank standoff always reads the real body.
    """
    dz0, hx0, hy0 = stations[0]
    wp = cq.Workplane("XY").workplane(offset=m + dz0).ellipse(hx0, hy0)
    prev_dz = dz0
    for dz, hx, hy in stations[1:]:
        wp = wp.workplane(offset=dz - prev_dz).ellipse(hx, hy)
        prev_dz = dz
    return wp.loft(combine=True)


def _crank_boss_solid(m: float, standoff: float) -> cq.Workplane:
    """001 L64-L71: cast boss carrying the input bearing out to the spin axis.

    Length is derived from the standoff (Contract 3e) so the boss always reaches
    exactly to the input axis; at the source standoff it reproduces the source's
    0.039 extrusion.
    """
    return (
        cq.Workplane("YZ")
        .center(-0.004, m + SHOULDER_CRANK_DZ)
        .circle(0.016)
        .extrude(-(standoff - _BOSS_ROOT_X))
        .translate((-_BOSS_ROOT_X, 0.0, 0.0))
    )


def _shoulder_mast_solid(m: float, standoff: float) -> cq.Workplane:
    """001 L41-L72: elliptical gearbox shoulder + tapered mast + bearing + boss."""
    shoulder = _loft_stations(_SHOULDER_STATIONS, m)
    mast = (
        cq.Workplane("XY")
        .workplane(offset=m + 0.074)
        .rect(0.052, 0.044)
        .workplane(offset=0.198)
        .rect(0.028, 0.030)
        .loft(combine=True)
    )
    bearing = (
        cq.Workplane("XY")
        .workplane(offset=m + 0.270)
        .circle(0.016)
        .extrude(0.011)
    )
    return shoulder.union(mast).union(bearing).union(_crank_boss_solid(m, standoff))


def _enclosed_gearcase_solid(m: float, standoff: float) -> cq.Workplane:
    """enclosed fork L41-L91: fully enclosed rounded cast gearcase + mast."""
    gearcase = _loft_stations(_GEARCASE_STATIONS, m)
    neck = (
        cq.Workplane("XY")
        .workplane(offset=m + 0.086)
        .ellipse(0.034, 0.027)
        .workplane(offset=0.014)
        .ellipse(0.026, 0.022)
        .loft(combine=True)
    )
    mast = (
        cq.Workplane("XY")
        .workplane(offset=m + 0.098)
        .rect(0.048, 0.040)
        .workplane(offset=0.174)
        .rect(0.028, 0.030)
        .loft(combine=True)
    )
    bearing = (
        cq.Workplane("XY")
        .workplane(offset=m + 0.270)
        .circle(0.016)
        .extrude(0.011)
    )
    return (
        gearcase.union(neck)
        .union(mast)
        .union(bearing)
        .union(_crank_boss_solid(m, standoff))
    )


def _drum_crown_solid(m: float) -> cq.Workplane:
    """002 L26-L44: shallow vertical drum gearbox + crown + neck."""
    body = (
        cq.Workplane("XZ")
        .circle(0.052)
        .extrude(0.028, both=True)
        .translate((0.0, 0.0, m + DRUM_CRANK_DZ))
    )
    crown = (
        cq.Workplane("XY")
        .circle(0.020)
        .extrude(0.065)
        .translate((0.0, 0.0, m + 0.092))
    )
    neck = (
        cq.Workplane("XY")
        .circle(0.014)
        .extrude(0.034)
        .translate((0.0, 0.0, m + 0.125))
    )
    return body.union(crown).union(neck)


def _body_casting(r: ResolvedCentrifugeMachine2Config, m: float) -> cq.Workplane:
    if r.support_base == "weighted_pedestal":
        support = _pedestal_solid()
    elif r.support_base == "table_clamp":
        support = _clamp_solid()
    else:
        support = _tripod_solid()
    standoff = _input_standoff(r)
    if r.body_form == "open_shoulder_mast":
        casting = support.union(_shoulder_mast_solid(m, standoff))
    elif r.body_form == "enclosed_rounded_gearcase":
        casting = support.union(_enclosed_gearcase_solid(m, standoff))
    else:
        casting = support.union(_drum_crown_solid(m))
    if r.support_base == "table_clamp":
        # 002 L58-L64: threaded clearance bore for the clamp screw.
        screw_clearance = (
            cq.Workplane("XY")
            .circle(0.0052)
            .extrude(0.050)
            .translate((0.018, 0.0, 0.025))
        )
        casting = casting.cut(screw_clearance)
    return casting.clean()


# --------------------------------------------------------------------------- #
# Body part assembly (root): casting + hardware + ④ decorations + clamp screw
# / drive shaft child parts where the module family emits them.
# --------------------------------------------------------------------------- #
def _add_support_hardware(body: Part, r: ResolvedCentrifugeMachine2Config) -> None:
    if r.support_base == "weighted_pedestal":
        # 001 L196-L209: four embedded rubber feet.
        for index, (x, y) in enumerate(
            ((0.045, 0.028), (0.045, -0.028), (-0.045, 0.028), (-0.045, -0.028))
        ):
            body.visual(
                Cylinder(radius=0.009, length=0.006),
                origin=Origin(xyz=(x, y, -0.001)),
                material="rubber",
                name=f"foot_{index}", material_class_id="rubber.smooth_plain",
            )
    elif r.support_base == "table_clamp":
        # 002 L199-L204: rubber pad under the upper jaw.
        body.visual(
            Box((0.046, 0.038, 0.003)),
            origin=Origin(xyz=(0.018, 0.0, 0.119)),
            material="rubber",
            name="upper_jaw_pad", material_class_id="rubber.smooth_plain",
        )
    else:
        # tripod fork L203-L227: three radial feet with rubber bench pads.
        foot_length = 0.092
        foot_center_r = 0.054
        for i in range(3):
            angle = math.radians(i * 120.0)
            cx = foot_center_r * math.cos(angle)
            cy = foot_center_r * math.sin(angle)
            body.visual(
                Box((foot_length, 0.022, 0.014)),
                origin=Origin(xyz=(cx, cy, 0.016), rpy=(0.0, 0.0, angle)),
                material="dark_metal",
                name=f"tripod_foot_{i}", material_class_id="metal.blackened_gunmetal",
            )
            pad_r = foot_center_r + foot_length * 0.40
            body.visual(
                Cylinder(radius=0.012, length=0.008),
                origin=Origin(xyz=(pad_r * math.cos(angle), pad_r * math.sin(angle), 0.009)),
                material="rubber",
                name=f"foot_pad_{i}", material_class_id="rubber.smooth_plain",
            )


def _add_shoulder_decorations(body: Part, m: float) -> None:
    """001 L211-L237: blank nameplate + colour marks + gearbox fastener.

    Placement constants are tied to the fixed shoulder loft profile (④ is
    derived after ③; the loft is not scaled, so the plate stays conformal)."""
    body.visual(
        Box((0.042, 0.002, 0.020)),
        origin=Origin(xyz=(0.0, -0.0385, m + 0.020)),
        material="label_white",
        name="blank_nameplate", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((0.014, 0.0012, 0.0025)),
        origin=Origin(xyz=(-0.008, -0.0399, m + 0.015)),
        material="label_red",
        name="nameplate_red_mark", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    body.visual(
        Box((0.014, 0.0012, 0.0025)),
        origin=Origin(xyz=(0.008, -0.0399, m + 0.015)),
        material="label_blue",
        name="nameplate_blue_mark", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    body.visual(
        Cylinder(radius=0.0042, length=0.004),
        origin=Origin(xyz=(-0.018, -0.029, m + 0.068), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="metal",
        name="gearbox_fastener", material_class_id="metal.steel_bare",
    )


def _add_enclosed_decorations(body: Part, m: float) -> None:
    """enclosed fork L251-L308: removable cover plate, seams, fasteners, ribs."""
    body.visual(
        Box((0.056, 0.003, 0.044)),
        origin=Origin(xyz=(0.0, 0.0555, m + 0.048)),
        material="enamel",
        name="cover_plate", material_class_id="metal.paint_coated",
    )
    body.visual(
        Box((0.060, 0.0012, 0.002)),
        origin=Origin(xyz=(0.0, 0.0572, m + 0.071)),
        material="dark_metal",
        name="cover_seam_top", material_class_id="metal.blackened_gunmetal",
    )
    body.visual(
        Box((0.060, 0.0012, 0.002)),
        origin=Origin(xyz=(0.0, 0.0572, m + 0.025)),
        material="dark_metal",
        name="cover_seam_bottom", material_class_id="metal.blackened_gunmetal",
    )
    for side, x in (("left", -0.029), ("right", 0.029)):
        body.visual(
            Box((0.002, 0.0012, 0.048)),
            origin=Origin(xyz=(x, 0.0572, m + 0.048)),
            material="dark_metal",
            name=f"cover_seam_{side}", material_class_id="metal.blackened_gunmetal",
        )
    for screw_idx, (sx, dz) in enumerate(
        ((-0.024, 0.066), (0.024, 0.066), (-0.024, 0.030), (0.024, 0.030))
    ):
        body.visual(
            Cylinder(radius=0.003, length=0.003),
            origin=Origin(xyz=(sx, 0.058, m + dz), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="metal",
            name=f"cover_fastener_{screw_idx}", material_class_id="metal.steel_bare",
        )
    for rib_idx, (dz, ry) in enumerate(((0.028, -0.052), (0.048, -0.054), (0.068, -0.045))):
        body.visual(
            Box((0.092, 0.008, 0.005)),
            origin=Origin(xyz=(0.0, ry, m + dz)),
            material="enamel",
            name=f"gearcase_rib_{rib_idx}", material_class_id="metal.paint_coated",
        )


def _add_drum_decorations(body: Part, m: float) -> None:
    """002 L181-L222: layered gearbox cover, maker plate, cover fasteners."""
    drum_z = m + DRUM_CRANK_DZ
    body.visual(
        Cylinder(radius=0.049, length=0.004),
        origin=Origin(xyz=(0.0, -0.029, drum_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="polished",
        name="gearbox_cover", material_class_id="metal.chrome_polished",
    )
    body.visual(
        Box((0.040, 0.003, 0.017)),
        origin=Origin(xyz=(0.0, -0.032, drum_z)),
        material="enamel_light",
        name="blank_maker_plate", material_class_id="metal.paint_coated",
    )
    for index, angle in enumerate((35, 145, 220, 320)):
        a = math.radians(angle)
        body.visual(
            Cylinder(radius=0.0032, length=0.0035),
            origin=Origin(
                xyz=(0.039 * math.cos(a), -0.0325, drum_z + 0.039 * math.sin(a)),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material="dark_metal",
            name=f"cover_fastener_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _build_body(
    model: ArticulatedObject, r: ResolvedCentrifugeMachine2Config, lay: _Layout
) -> None:
    body = model.part(
        "body",
        meta={
            "role": "cast support + gearbox body (root)",
            "support_base": r.support_base,
            "body_form": r.body_form,
        },
    )
    body.visual(
        mesh_from_cadquery(_body_casting(r, lay.mount_z), "body_casting", tolerance=0.001),
        material="enamel",
        name="body_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"mint_enamel", "black_japanned_brass", "cream_lab_enamel", "hammertone_green"} else "metal.brushed_silver"),
    )
    _add_support_hardware(body, r)

    # Input-side crank bearing collar (hardware for crank joint origin honesty).
    if r.body_form == "drum_gearbox_crown":
        # Collar bridges the drum face out to the (derived) input axis, so it
        # stays welded to the casting at any standoff. At the source standoff
        # (0.038) this reproduces 002's length 0.008 @ y=-0.034.
        collar_len = lay.input_standoff - _DRUM_BEARING_ROOT_Y
        body.visual(
            Cylinder(radius=0.0125, length=collar_len),
            origin=Origin(
                xyz=(
                    0.0,
                    -(_DRUM_BEARING_ROOT_Y + lay.input_standoff) * 0.5,
                    lay.mount_z + DRUM_CRANK_DZ,
                ),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material="dark_metal",
            name="crank_bearing", material_class_id="metal.blackened_gunmetal",
        )
        # Top spindle bearing (parent face of shaft_rotation MatingContract).
        body.visual(
            Cylinder(radius=0.018, length=0.010),
            origin=Origin(xyz=(0.0, 0.0, lay.mount_z + DRUM_SHAFT_DZ - 0.005)),
            material="dark_metal",
            name="top_bearing", material_class_id="metal.blackened_gunmetal",
        )
        _add_drum_decorations(body, lay.mount_z)
    else:
        # Collar seats on the outer end of the crank boss, which the derivation
        # extrudes out to the input axis. At the source standoff (0.064) this
        # reproduces 001's collar @ x=-0.061.
        body.visual(
            Cylinder(radius=0.0125, length=0.006),
            origin=Origin(
                xyz=(
                    -lay.input_standoff + 0.003,
                    -0.004,
                    lay.mount_z + SHOULDER_CRANK_DZ,
                ),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material="dark_metal",
            name="crank_bearing", material_class_id="metal.blackened_gunmetal",
        )
        # Bearing cap under the rotor (parent face of rotor_spin MatingContract).
        body.visual(
            Cylinder(radius=0.012, length=0.005),
            origin=Origin(xyz=(0.0, 0.0, lay.rotor_joint_z - 0.0025)),
            material="dark_metal",
            name="bearing_cap", material_class_id="metal.blackened_gunmetal",
        )
        if r.body_form == "open_shoulder_mast":
            _add_shoulder_decorations(body, lay.mount_z)
        else:
            _add_enclosed_decorations(body, lay.mount_z)

    # table_clamp emits the clamp screw (002 L363-L405): a real PRISMATIC child.
    if r.support_base == "table_clamp":
        clamp_screw = model.part(
            "clamp_screw",
            meta={"motion_note": "prismatic approximation of the screw's clamping advance"},
        )
        clamp_screw.visual(
            Cylinder(radius=0.00525, length=0.086),
            origin=Origin(xyz=(0.0, 0.0, 0.028)),
            material="dark_metal",
            name="screw_shank", material_class_id="metal.blackened_gunmetal",
        )
        clamp_screw.visual(
            Cylinder(radius=0.014, length=0.006),
            origin=Origin(xyz=(0.0, 0.0, 0.074)),
            material="polished",
            name="pressure_pad", material_class_id=("metal.chrome_polished" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_polished"),
        )
        clamp_screw.visual(
            Cylinder(radius=0.0038, length=0.052),
            origin=Origin(xyz=(0.0, 0.0, -0.016), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="dark_metal",
            name="tommy_bar", material_class_id="metal.blackened_gunmetal",
        )
        for index, sx in enumerate((0.026, -0.026)):
            clamp_screw.visual(
                Sphere(radius=0.006),
                origin=Origin(xyz=(sx, 0.0, -0.016)),
                material="dark_metal",
                name=f"bar_end_{index}", material_class_id="metal.blackened_gunmetal",
            )
        # Captured screw-in-boss: no clean axis-aligned mating faces -> the
        # MatingContract is omitted (grandfathered captured screw thread).
        model.articulation(
            "clamp_adjustment",
            ArticulationType.PRISMATIC,
            parent=body,
            child=clamp_screw,
            origin=Origin(xyz=(0.018, 0.0, 0.025)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=120.0, velocity=0.03, lower=-0.010, upper=0.015),
            meta={"function": "threaded pressure-pad advance"},
        )

    # drum family emits the exposed vertical drive shaft (002 L237-L259).
    if r.body_form == "drum_gearbox_crown":
        drive_shaft = model.part("drive_shaft", meta={"finish": "polished vertical spindle"})
        drive_shaft.visual(
            Cylinder(radius=0.006, length=0.145),
            origin=Origin(xyz=(0.0, 0.0, 0.0725)),
            material="polished",
            name="shaft", material_class_id=("metal.chrome_polished" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_polished"),
        )
        drive_shaft.visual(
            Cylinder(radius=0.010, length=0.012),
            origin=Origin(xyz=(0.0, 0.0, 0.012)),
            material="dark_metal",
            name="shaft_collar", material_class_id="metal.blackened_gunmetal",
        )
        model.articulation(
            "shaft_rotation",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=drive_shaft,
            origin=Origin(xyz=(0.0, 0.0, lay.mount_z + DRUM_SHAFT_DZ)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=8.0, velocity=30.0),
            mating=MatingContract(
                parent_face_geometry="top_bearing",
                parent_face_side="positive_z",
                child_face_geometry="shaft",
                child_face_side="negative_z",
                contact_tol=0.002,
            ),
            meta={"function": "vertical gearbox output spindle"},
        )


# --------------------------------------------------------------------------- #
# Drive inputs (Slot C). Authored in a local frame whose spin axis is +x and
# whose outward direction is -x; the joint origin yaw maps it onto the body's
# input mount (side x for 001-family, front y for drum, per source).
# --------------------------------------------------------------------------- #
def _build_offset_crank(
    model: ArticulatedObject, r: ResolvedCentrifugeMachine2Config, lay: _Layout
):
    """001 L239-L316: short offset crank + free-spinning fluted knob."""
    s = r.input_reach_scale
    handle_yz = (-0.043 * s, -0.035 * s)
    body = model.get_part("body")
    crank = model.part(
        "crank",
        meta={"construction": "steel input shaft, hub, offset arm, and handle pin"},
    )
    crank.visual(
        Cylinder(radius=0.006, length=0.016),
        origin=Origin(xyz=(-0.008, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="metal",
        name="crank_shaft", material_class_id=("metal.steel_bare" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
    )
    crank.visual(
        Cylinder(radius=0.010, length=0.008),
        origin=Origin(xyz=(-0.018, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="enamel_light",
        name="crank_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
    )
    crank_angle = math.atan2(-handle_yz[0], handle_yz[1])
    crank_length = math.hypot(*handle_yz)
    crank.visual(
        Box((0.006, 0.008, crank_length)),
        origin=Origin(
            xyz=(-0.019, handle_yz[0] / 2.0, handle_yz[1] / 2.0),
            rpy=(crank_angle, 0.0, 0.0),
        ),
        material="metal",
        name="crank_arm", material_class_id=("metal.steel_bare" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
    )
    crank.visual(
        Cylinder(radius=0.0045, length=0.024),
        origin=Origin(
            xyz=(-0.028, handle_yz[0], handle_yz[1]),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material="metal",
        name="handle_pin", material_class_id=("metal.steel_bare" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
    )
    crank_joint = model.articulation(
        "crank_spin",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=crank,
        origin=Origin(xyz=lay.crank_pos, rpy=(0.0, 0.0, lay.crank_yaw)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=8.0),
        motion_properties=MotionProperties(damping=0.02, friction=0.04),
        meta={"type": "continuous", "axis": lay.input_axis_world, "function": "hand input"},
    )

    crank_knob = model.part(
        "crank_knob", meta={"construction": "freely rotating fluted hand grip"}
    )
    crank_knob.visual(
        Cylinder(radius=0.0115, length=0.028),
        origin=Origin(xyz=(-0.014, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="enamel_light",
        name="grip", material_class_id=("metal.paint_coated" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
    )
    for index in range(12):
        angle = index * math.tau / 12.0
        crank_knob.visual(
            Box((0.024, 0.0032, 0.0032)),
            origin=Origin(
                xyz=(-0.014, 0.0113 * math.cos(angle), 0.0113 * math.sin(angle)),
                rpy=(angle, 0.0, 0.0),
            ),
            material="enamel_light",
            name=f"grip_rib_{index}", material_class_id=("metal.paint_coated" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
        )
    model.articulation(
        "crank_knob_spin",
        ArticulationType.CONTINUOUS,
        parent=crank,
        child=crank_knob,
        origin=Origin(xyz=(-0.040, handle_yz[0], handle_yz[1])),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=12.0),
        motion_properties=MotionProperties(damping=0.01, friction=0.01),
        meta={"function": "free-spinning grip sleeve on the handle pin"},
    )
    return crank_joint


_SPLINE_ARM_XZ = (
    (0.000, 0.000),
    (0.018, -0.004),
    (0.065, -0.025),
    (0.105, -0.070),
    (0.145, -0.105),
)


def _build_spline_crank(
    model: ArticulatedObject, r: ResolvedCentrifugeMachine2Config, lay: _Layout
):
    """002 L99-L144 + L224-L235: long spline-tube crank arm with turned wooden
    grip. Source points are authored in the 002 y-axis frame; here they are
    pre-rotated into the local x-axis convention ((sx, sz) -> (0, -sx, sz))."""
    s = r.input_reach_scale
    body = model.get_part("body")
    crank = model.part("crank", meta={"finish": "steel arm with turned wooden grip"})
    arm_points = [(0.0, -sx * s, sz * s) for sx, sz in _SPLINE_ARM_XZ]
    arm_geom = tube_from_spline_points(
        arm_points,
        radius=0.0046,
        samples_per_segment=12,
        radial_segments=16,
        cap_ends=True,
    )
    crank.visual(mesh_from_geometry(arm_geom, "crank_arm_tube"), material="polished", name="crank_arm", material_class_id=("metal.chrome_polished" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_polished"))
    crank.visual(
        Cylinder(radius=0.011, length=0.020),
        origin=Origin(xyz=(-0.010, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="polished",
        name="crank_hub", material_class_id=("metal.chrome_polished" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_polished"),
    )
    # Turned wooden grip along the local (0, -0.060, -0.025) direction.
    d = (0.060, -0.025)
    length = math.hypot(*d)
    center = (0.0, -0.175 * s, -0.1175 * s)
    grip_roll = math.atan2(d[0], d[1])
    crank.visual(
        Cylinder(radius=0.012, length=length),
        origin=Origin(xyz=center, rpy=(grip_roll, 0.0, 0.0)),
        material="wood",
        name="wood_grip", material_class_id="wood.polished_varnished",
    )
    unit = (-d[0] / length, d[1] / length)
    for index, sign in enumerate((-1.0, 1.0)):
        end = (
            0.0,
            center[1] + sign * unit[0] * length * 0.49,
            center[2] + sign * unit[1] * length * 0.49,
        )
        crank.visual(
            Sphere(radius=0.012),
            origin=Origin(xyz=end),
            material="wood",
            name=f"grip_end_{index}", material_class_id="wood.polished_varnished",
        )
    return model.articulation(
        "crank_spin",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=crank,
        origin=Origin(xyz=lay.crank_pos, rpy=(0.0, 0.0, lay.crank_yaw)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=7.0),
        meta={"type": "continuous", "axis": lay.input_axis_world, "function": "hand input"},
    )


def _handwheel_solid(rim_r: float) -> cq.Workplane:
    """handwheel fork L158-L199: hub + torus rim + five radial spokes."""
    hub_r = 0.013
    hub_hl = 0.005
    tube_r = 0.005
    hub = (
        cq.Workplane("YZ")
        .circle(hub_r)
        .extrude(hub_hl)
        .union(cq.Workplane("YZ").circle(hub_r).extrude(-hub_hl))
    )
    rim = (
        cq.Workplane("XY")
        .center(0.0, rim_r)
        .circle(tube_r)
        .revolve(360.0, (0.0, -rim_r), (1.0, -rim_r))
    )
    wheel = hub.union(rim)
    inner_r = hub_r
    outer_r = rim_r - tube_r
    spoke_len = outer_r - inner_r
    spoke_cr = inner_r + spoke_len / 2.0
    for index in range(5):
        angle_deg = index * 360.0 / 5.0
        spoke = (
            cq.Workplane("XY")
            .box(0.005, spoke_len, 0.007)
            .translate((0.0, spoke_cr, 0.0))
            .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), angle_deg)
        )
        wheel = wheel.union(spoke)
    return wheel.clean()


def _build_rim_handwheel(
    model: ArticulatedObject, r: ResolvedCentrifugeMachine2Config, lay: _Layout
):
    """handwheel fork L289-L357: spoked rim wheel + free-spinning rim grip."""
    s = r.input_reach_scale
    rim_r = 0.045 * s
    body = model.get_part("body")
    handwheel = model.part(
        "handwheel",
        meta={"construction": "spoked rim handwheel with input shaft on the geared side"},
    )
    handwheel.visual(
        Cylinder(radius=0.006, length=0.018),
        origin=Origin(xyz=(-0.009, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="metal",
        name="wheel_shaft", material_class_id=("metal.steel_bare" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
    )
    handwheel.visual(
        mesh_from_cadquery(_handwheel_solid(rim_r), "handwheel_body", tolerance=0.0008),
        material="enamel_light",
        name="wheel_body", material_class_id=("metal.paint_coated" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
    )
    wheel_joint = model.articulation(
        "handwheel_spin",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=handwheel,
        origin=Origin(xyz=lay.crank_pos, rpy=(0.0, 0.0, lay.crank_yaw)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=8.0),
        motion_properties=MotionProperties(damping=0.02, friction=0.04),
        meta={"type": "continuous", "axis": lay.input_axis_world, "function": "hand input"},
    )
    rim_grip = model.part(
        "rim_grip",
        meta={"construction": "freely rotating cylindrical roller sleeve on the rim"},
    )
    rim_grip.visual(
        Cylinder(radius=0.011, length=0.032),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="rubber",
        name="grip_roller", material_class_id="rubber.smooth_plain",
    )
    for index in range(10):
        angle = index * math.tau / 10.0
        rim_grip.visual(
            Box((0.003, 0.028, 0.003)),
            origin=Origin(
                xyz=(0.0108 * math.cos(angle), 0.0, 0.0108 * math.sin(angle)),
                rpy=(0.0, angle, 0.0),
            ),
            material="rubber",
            name=f"grip_rib_{index}", material_class_id="rubber.smooth_plain",
        )
    model.articulation(
        "grip_spin",
        ArticulationType.CONTINUOUS,
        parent=handwheel,
        child=rim_grip,
        origin=Origin(xyz=(0.0, 0.0, rim_r)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=12.0),
        motion_properties=MotionProperties(damping=0.01, friction=0.01),
        meta={"function": "free-spinning roller sleeve on the wheel rim"},
    )
    return wheel_joint


def _build_drive(model: ArticulatedObject, r: ResolvedCentrifugeMachine2Config, lay: _Layout):
    if r.drive_input == "offset_crank":
        return _build_offset_crank(model, r, lay)
    if r.drive_input == "spline_crank":
        return _build_spline_crank(model, r, lay)
    return _build_rim_handwheel(model, r, lay)


# --------------------------------------------------------------------------- #
# Rotor carriers (Slot D).
# --------------------------------------------------------------------------- #
def _plate_carrier_solid(n: int, pivot_r: float) -> cq.Workplane:
    """001 L75-L137 (N=4) generalized per the n6 fork L75-L131: hub + N/2
    full-diameter arms + per-station boss / through-opening / swing slot."""
    z0 = 0.034
    hub = cq.Workplane("XY").circle(0.018).extrude(0.014).translate((0.0, 0.0, z0))
    carrier = hub
    for i in range(n // 2):
        arm_deg = i * 360.0 / n
        arm = (
            cq.Workplane("XY")
            .rect(2.0 * pivot_r + 0.004, 0.016)
            .extrude(0.010)
            .translate((0.0, 0.0, z0 + 0.002))
        )
        if arm_deg != 0.0:
            arm = arm.rotate((0, 0, 0), (0, 0, 1), arm_deg)
        carrier = carrier.union(arm)
    for i in range(n):
        angle_deg = i * 360.0 / n
        outer = (
            cq.Workplane("XY")
            .center(pivot_r, 0.0)
            .circle(0.020)
            .extrude(0.014)
            .translate((0.0, 0.0, z0))
        )
        opening = (
            cq.Workplane("XY")
            .center(pivot_r, 0.0)
            .circle(0.013)
            .extrude(0.018)
            .translate((0.0, 0.0, z0 - 0.002))
        )
        slot = (
            cq.Workplane("XY")
            .center(pivot_r + 0.016, 0.0)
            .rect(0.032, 0.024)
            .extrude(0.018)
            .translate((0.0, 0.0, z0 - 0.002))
        )
        if angle_deg != 0.0:
            outer = outer.rotate((0, 0, 0), (0, 0, 1), angle_deg)
            opening = opening.rotate((0, 0, 0), (0, 0, 1), angle_deg)
            slot = slot.rotate((0, 0, 0), (0, 0, 1), angle_deg)
        carrier = carrier.union(outer).cut(opening).cut(slot)
    return carrier.clean()


def _plate_tube_geometry(s_t: float) -> LatheGeometry:
    """001 L140-L152: thin-walled tapered glass shield, z scaled by ⑤."""
    profile = tuple(
        (radius, z * s_t)
        for radius, z in (
            (0.0105, -0.008),
            (0.0104, -0.020),
            (0.0088, -0.108),
            (0.0055, -0.124),
            (0.0012, -0.131),
            (0.0048, -0.108),
            (0.0077, -0.020),
            (0.0078, -0.008),
        )
    )
    return LatheGeometry(profile, segments=40, closed=True)


def _bar_cup_solid(s_t: float) -> cq.Workplane:
    """002 L67-L96: hollow tapered metal bucket with hanger bridge + bored
    pivot sleeve; loft heights scaled by ⑤ tube_length_scale."""
    outer = (
        cq.Workplane("XY")
        .circle(0.0105)
        .workplane(offset=0.076 * s_t)
        .circle(0.0160)
        .loft(combine=True)
        .translate((0.0, 0.0, -0.084 * s_t))
    )
    inner = (
        cq.Workplane("XY")
        .circle(0.0075)
        .workplane(offset=0.074 * s_t)
        .circle(0.0132)
        .loft(combine=True)
        .translate((0.0, 0.0, -0.080 * s_t))
    )
    cup = outer.cut(inner)
    bridge = cq.Workplane("XY").box(0.029, 0.008, 0.012).translate((0.0, 0.0, -0.007))
    stem = cq.Workplane("XY").box(0.010, 0.008, 0.013).translate((0.0, 0.0, -0.002))
    sleeve = (
        cq.Workplane("XZ")
        .circle(0.0045)
        .circle(0.0026)
        .extrude(0.015, both=True)
    )
    return cup.union(bridge).union(stem).union(sleeve)


def _sleeve_carrier_solid(n: int, arm_len: float) -> cq.Workplane:
    """rigid fork L83-L121: hub + N tilted arms + cylindrical tip bosses."""
    z0 = 0.034
    tilt_deg = math.degrees(SLEEVE_TILT)
    hub = cq.Workplane("XY").circle(0.018).extrude(0.014).translate((0.0, 0.0, z0))
    carrier = hub
    arm_r_tip = SLEEVE_HUB_R + arm_len * math.sin(SLEEVE_TILT)
    arm_z_tip = SLEEVE_HUB_Z_MID + arm_len * math.cos(SLEEVE_TILT)
    for i in range(n):
        phi_deg = i * 360.0 / n
        phi = math.radians(phi_deg)
        r_c = SLEEVE_HUB_R + (arm_len / 2.0) * math.sin(SLEEVE_TILT)
        z_c = SLEEVE_HUB_Z_MID + (arm_len / 2.0) * math.cos(SLEEVE_TILT)
        arm = cq.Workplane("XY").box(0.014, 0.009, arm_len)
        arm = arm.rotate((0, 0, 0), (0, 1, 0), tilt_deg)
        arm = arm.rotate((0, 0, 0), (0, 0, 1), phi_deg)
        arm = arm.translate((r_c * math.cos(phi), r_c * math.sin(phi), z_c))
        carrier = carrier.union(arm)
        boss = (
            cq.Workplane("XY")
            .circle(0.014)
            .extrude(0.022)
            .translate((0, 0, -0.011))
        )
        boss = boss.rotate((0, 0, 0), (0, 1, 0), tilt_deg)
        boss = boss.rotate((0, 0, 0), (0, 0, 1), phi_deg)
        boss = boss.translate((arm_r_tip * math.cos(phi), arm_r_tip * math.sin(phi), arm_z_tip))
        carrier = carrier.union(boss)
    return carrier.clean()


def _sleeve_tube_geometry(s_t: float) -> LatheGeometry:
    """rigid fork L124-L137: centred tapered sleeve for fixed-angle mounting."""
    shift = 0.070
    profile = tuple(
        (radius, (z + shift) * s_t)
        for radius, z in (
            (0.0105, -0.008),
            (0.0104, -0.020),
            (0.0088, -0.108),
            (0.0055, -0.124),
            (0.0012, -0.131),
            (0.0048, -0.108),
            (0.0077, -0.020),
            (0.0078, -0.008),
        )
    )
    return LatheGeometry(profile, segments=40, closed=True)


def _rotor_core(rotor: Part, r: ResolvedCentrifugeMachine2Config) -> str:
    """Spindle/hub whose bottom face is the rotor_spin MatingContract child
    face. Returns the child face visual name."""
    if r.carrier == "bar_fork_swing":
        rotor.visual(
            Cylinder(radius=0.014, length=0.018),
            origin=Origin(xyz=(0.0, 0.0, 0.009)),
            material="dark_metal",
            name="rotor_hub", material_class_id="metal.blackened_gunmetal",
        )
        return "rotor_hub"
    rotor.visual(
        Cylinder(radius=0.0045, length=0.038),
        origin=Origin(xyz=(0.0, 0.0, 0.019)),
        material="metal",
        name="spindle", material_class_id=("metal.steel_bare" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
    )
    return "spindle"


def _build_plate_swing(model: ArticulatedObject, r: ResolvedCentrifugeMachine2Config, rotor: Part) -> None:
    n = r.bucket_count
    pivot_r = PLATE_PIVOT_R * r.carrier_radius_scale
    rotor.visual(
        mesh_from_cadquery(_plate_carrier_solid(n, pivot_r), "rotor_carrier", tolerance=0.0009),
        material="enamel_light",
        name="rotor_carrier", material_class_id=("metal.paint_coated" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
    )
    rotor.visual(
        Cylinder(radius=0.011, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.047)),
        material="label_white",
        name="center_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    tube_mesh = mesh_from_geometry(_plate_tube_geometry(r.tube_length_scale), "plate_tube")
    for index in range(n):
        angle = index * math.tau / n
        bucket = model.part(
            f"bucket_{index}",
            meta={"construction": "transparent tapered test-tube shield with transverse pivot"},
        )
        bucket.visual(
            Cylinder(radius=0.0025, length=0.042),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="metal",
            name="pivot_pin", material_class_id=("metal.steel_bare" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
        )
        bucket.visual(
            Cylinder(radius=0.0115, length=0.015),
            origin=Origin(xyz=(0.0, 0.0, -0.0065)),
            material="enamel_light",
            name="bucket_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
        )
        bucket.visual(tube_mesh, material="glass", name="tube_shell", material_class_id="glass.clear_transparent")
        model.articulation(
            f"bucket_swing_{index}",
            ArticulationType.REVOLUTE,
            parent=rotor,
            child=bucket,
            origin=Origin(
                xyz=(pivot_r * math.cos(angle), pivot_r * math.sin(angle), PLATE_PIVOT_DZ),
                rpy=(0.0, 0.0, angle),
            ),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=1.2, velocity=6.0, lower=0.0, upper=PLATE_SWING_UPPER),
            motion_properties=MotionProperties(damping=0.03, friction=0.01),
        )


def _build_bar_fork_swing(model: ArticulatedObject, r: ResolvedCentrifugeMachine2Config, rotor: Part) -> None:
    n = r.bucket_count
    pivot_r = BAR_PIVOT_R * r.carrier_radius_scale
    rotor.visual(
        Box((2.0 * pivot_r, 0.012, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, 0.013)),
        material="polished",
        name="crossbar_x", material_class_id=("metal.chrome_polished" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_polished"),
    )
    if n == 4:
        rotor.visual(
            Box((0.012, 2.0 * pivot_r, 0.006)),
            origin=Origin(xyz=(0.0, 0.0, 0.013)),
            material="polished",
            name="crossbar_y", material_class_id=("metal.chrome_polished" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_polished"),
        )
    cup_mesh = mesh_from_cadquery(_bar_cup_solid(r.tube_length_scale), "bar_cup", tolerance=0.0008)
    for index in range(n):
        phi = index * math.tau / n
        px = pivot_r * math.cos(phi)
        py = pivot_r * math.sin(phi)
        tangent = (-math.sin(phi), math.cos(phi))
        rotor.visual(
            Cylinder(radius=0.0022, length=0.024),
            origin=Origin(xyz=(px, py, 0.0), rpy=(math.pi / 2.0, 0.0, phi)),
            material="dark_metal",
            name=f"pivot_pin_{index}", material_class_id="metal.blackened_gunmetal",
        )
        for cheek_index, side in enumerate((-1.0, 1.0)):
            rotor.visual(
                Box((0.008, 0.006, 0.016)),
                origin=Origin(
                    xyz=(px + tangent[0] * side * 0.009, py + tangent[1] * side * 0.009, 0.005),
                    rpy=(0.0, 0.0, phi),
                ),
                material="polished",
                name=f"fork_{index}_{cheek_index}", material_class_id=("metal.chrome_polished" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_polished"),
            )
        bucket = model.part(
            f"bucket_{index}",
            meta={"construction": "hollow tapered metal tube bucket", "pivot_clearance_m": 0.0004},
        )
        bucket.visual(
            cup_mesh,
            origin=Origin(rpy=(0.0, 0.0, phi)),
            material="polished",
            name="bucket_shell", material_class_id=("metal.chrome_polished" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_polished"),
        )
        model.articulation(
            f"bucket_swing_{index}",
            ArticulationType.REVOLUTE,
            parent=rotor,
            child=bucket,
            origin=Origin(xyz=(px, py, 0.0)),
            axis=(math.sin(phi), -math.cos(phi), 0.0),
            motion_limits=MotionLimits(effort=1.2, velocity=8.0, lower=0.0, upper=BAR_SWING_UPPER),
            meta={"function": "centrifugal swing-out bucket"},
        )


def _build_fixed_sleeve(model: ArticulatedObject, r: ResolvedCentrifugeMachine2Config, rotor: Part) -> None:
    n = r.bucket_count
    arm_len = SLEEVE_ARM_LEN * r.carrier_radius_scale
    arm_r_tip = SLEEVE_HUB_R + arm_len * math.sin(SLEEVE_TILT)
    arm_z_tip = SLEEVE_HUB_Z_MID + arm_len * math.cos(SLEEVE_TILT)
    rotor.visual(
        mesh_from_cadquery(_sleeve_carrier_solid(n, arm_len), "rotor_carrier", tolerance=0.0009),
        material="enamel_light",
        name="rotor_carrier", material_class_id=("metal.paint_coated" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_aged"),
    )
    rotor.visual(
        Cylinder(radius=0.011, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.047)),
        material="label_white",
        name="center_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    sleeve_mesh = mesh_from_geometry(_sleeve_tube_geometry(r.tube_length_scale), "sleeve_tube")
    for index in range(n):
        phi = index * math.tau / n
        sleeve_origin = Origin(
            xyz=(arm_r_tip * math.cos(phi), arm_r_tip * math.sin(phi), arm_z_tip),
            rpy=(0.0, SLEEVE_TILT, phi),
        )
        rotor.visual(
            Cylinder(radius=0.013, length=0.018),
            origin=sleeve_origin,
            material="polished",
            name=f"tube_holder_{index}", material_class_id=("metal.chrome_polished" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_polished"),
        )
        rotor.visual(sleeve_mesh, origin=sleeve_origin, material="polished", name=f"tube_sleeve_{index}", material_class_id=("metal.chrome_polished" if r.palette_style in {"mint_enamel", "aged_nickel_wood", "cream_lab_enamel", "hammertone_green"} else "metal.brass_polished"))


def _build_rotor(
    model: ArticulatedObject,
    r: ResolvedCentrifugeMachine2Config,
    lay: _Layout,
    input_joint,
) -> None:
    rotor = model.part(
        "rotor",
        meta={
            "role": "exposed vertical tube carrier",
            "carrier": r.carrier,
            "bucket_count": r.bucket_count,
            "station_spacing_deg": 360.0 / r.bucket_count,
        },
    )
    child_face = _rotor_core(rotor, r)
    if r.carrier == "plate_swing":
        _build_plate_swing(model, r, rotor)
    elif r.carrier == "bar_fork_swing":
        _build_bar_fork_swing(model, r, rotor)
    else:
        _build_fixed_sleeve(model, r, rotor)

    parent = model.get_part(lay.rotor_parent)
    parent_face = "bearing_cap" if lay.rotor_parent == "body" else "shaft"
    model.articulation(
        "rotor_spin",
        ArticulationType.CONTINUOUS,
        parent=parent,
        child=rotor,
        origin=Origin(xyz=(0.0, 0.0, lay.rotor_joint_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3.0 if lay.mimic else 6.0, velocity=40.0),
        motion_properties=MotionProperties(damping=0.01, friction=0.015),
        mimic=(
            Mimic(joint=input_joint.name, multiplier=GEAR_RATIO, offset=0.0)
            if lay.mimic
            else None
        ),
        mating=MatingContract(
            parent_face_geometry=parent_face,
            parent_face_side="positive_z",
            child_face_geometry=child_face,
            child_face_side="negative_z",
            contact_tol=0.002,
        ),
        meta={
            "type": "continuous",
            "axis": (0.0, 0.0, 1.0),
            "geared": lay.mimic,
        },
    )


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_picturex_0611_centrifuge_machine2(
    config: PictureX0611CentrifugeMachine2Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or PictureX0611CentrifugeMachine2Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    for key, rgba in r.palette.items():
        model.material(key, rgba=rgba)
    lay = _layout(r)
    _build_body(model, r, lay)
    input_joint = _build_drive(model, r, lay)
    _build_rotor(model, r, lay, input_joint)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_picturex_0611_centrifuge_machine2(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_centrifuge_machine2(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedCentrifugeMachine2Config) -> list[tuple[str, str]]:
    return [
        ("support_base", r.support_base),
        ("body_form", r.body_form),
        ("drive_input", r.drive_input),
        ("carrier", r.carrier),
        ("bucket_count", str(r.bucket_count)),
        ("palette_style", r.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _input_joint_name(r: ResolvedCentrifugeMachine2Config) -> str:
    return "handwheel_spin" if r.drive_input == "rim_handwheel" else "crank_spin"


def _center(aabb) -> tuple[float, float, float]:
    return (
        (aabb[0][0] + aabb[1][0]) * 0.5,
        (aabb[0][1] + aabb[1][1]) * 0.5,
        (aabb[0][2] + aabb[1][2]) * 0.5,
    )


def _declare_overlaps(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedCentrifugeMachine2Config
) -> None:
    body = model.get_part("body")
    rotor = model.get_part("rotor")
    # Input shaft is a pin captured in the body's bearing collar / boss.
    input_part_name = "handwheel" if r.drive_input == "rim_handwheel" else "crank"
    input_part = model.get_part(input_part_name)
    shaft_elem = "wheel_shaft" if r.drive_input == "rim_handwheel" else "crank_shaft"
    if r.drive_input == "spline_crank":
        shaft_elem = "crank_hub"
    for b_elem in ("crank_bearing", "body_shell"):
        ctx.allow_overlap(
            input_part, body, elem_a=shaft_elem, elem_b=b_elem,
            reason="input shaft/hub is captured in the gearbox bearing collar",
        )
    if r.drive_input == "rim_handwheel":
        ctx.allow_overlap(
            input_part, body, elem_a="wheel_body", elem_b="body_shell",
            reason="handwheel hub bore seats around the body crank boss (source mount)",
        )
        ctx.allow_overlap(
            input_part, body, elem_a="wheel_body", elem_b="crank_bearing",
            reason="handwheel hub is captured around the input bearing collar",
        )
        rim_grip = model.get_part("rim_grip")
        ctx.allow_overlap(
            rim_grip, input_part, elem_a="grip_roller", elem_b="wheel_body",
            reason="rubber roller sleeve wraps the rim tube (free-spinning rim grip)",
        )
    if r.drive_input == "offset_crank":
        knob = model.get_part("crank_knob")
        ctx.allow_overlap(
            knob, input_part, elem_a="grip", elem_b="handle_pin",
            reason="fluted grip sleeve wraps the crank handle pin",
        )
    if r.support_base == "table_clamp":
        screw = model.get_part("clamp_screw")
        ctx.allow_overlap(
            screw, body, elem_a="screw_shank", elem_b="body_shell",
            reason="clamp screw captured in the cast threaded boss (thread engagement)",
        )
    if r.body_form == "drum_gearbox_crown":
        shaft = model.get_part("drive_shaft")
        ctx.allow_overlap(
            shaft, body, elem_a="shaft", elem_b="top_bearing",
            reason="spindle rides inside the crown top bearing",
        )
        ctx.allow_overlap(
            rotor, shaft, elem_a="rotor_hub" if r.carrier == "bar_fork_swing" else "spindle",
            elem_b="shaft",
            reason="rotor hub keyed onto the drive spindle tip",
        )
    # Swing buckets: captured transverse pivot pins.
    if r.carrier in ("plate_swing", "bar_fork_swing"):
        for index in range(r.bucket_count):
            bucket = model.get_part(f"bucket_{index}")
            if r.carrier == "plate_swing":
                ctx.allow_overlap(
                    rotor, bucket, elem_a="rotor_carrier", elem_b="pivot_pin",
                    reason="transverse bucket pin captured through the carrier ears",
                )
                ctx.allow_overlap(
                    rotor, bucket, elem_a="rotor_carrier", elem_b="bucket_collar",
                    reason="bucket collar seats in the carrier through-opening",
                )
            else:
                for rotor_elem in (
                    f"pivot_pin_{index}", f"fork_{index}_0", f"fork_{index}_1", "crossbar_x",
                ):
                    ctx.allow_overlap(
                        rotor, bucket, elem_a=rotor_elem, elem_b="bucket_shell",
                        reason="bucket sleeve captured between the fork cheeks on its pivot pin",
                    )
                if r.bucket_count == 4:
                    ctx.allow_overlap(
                        rotor, bucket, elem_a="crossbar_y", elem_b="bucket_shell",
                        reason="bucket hanger bridge rides under the crossbar",
                    )


def run_picturex_0611_centrifuge_machine2_tests(
    object_model: ArticulatedObject, config: PictureX0611CentrifugeMachine2Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    parts = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}

    # --- Category identity: exposed hand-driven centrifuge, never machine1. ---
    ctx.check("body_root_present", "body" in parts)
    ctx.check("rotor_present", "rotor" in parts)
    ctx.check(
        "no_lid_no_motor",
        "lid" not in parts and not any(n.startswith("motor") for n in parts),
        details=str(sorted(parts)),
    )
    roots = object_model.root_parts()
    ctx.check(
        "single_body_root",
        len(roots) == 1 and roots[0].name == "body",
        details=f"roots={[p.name for p in roots]}",
    )

    input_name = _input_joint_name(r)
    input_joint = joints.get(input_name)
    ctx.check(
        "hand_input_continuous_horizontal",
        input_joint is not None
        and input_joint.articulation_type == ArticulationType.CONTINUOUS,
        details=f"{input_name}={input_joint}",
    )

    rotor_joint = joints.get("rotor_spin")
    ctx.check(
        "rotor_spin_continuous_z",
        rotor_joint is not None
        and rotor_joint.articulation_type == ArticulationType.CONTINUOUS
        and tuple(rotor_joint.axis) == (0.0, 0.0, 1.0),
        details=str(rotor_joint),
    )
    if r.body_form == "drum_gearbox_crown":
        shaft_joint = joints.get("shaft_rotation")
        ctx.check(
            "drum_drive_shaft_chain",
            "drive_shaft" in parts
            and shaft_joint is not None
            and shaft_joint.articulation_type == ArticulationType.CONTINUOUS
            and rotor_joint.parent == "drive_shaft",
            details=f"shaft={shaft_joint}, rotor_parent={rotor_joint.parent}",
        )
        ctx.check("drum_rotor_independent", rotor_joint.mimic is None)
    else:
        ctx.check(
            "rotor_geared_to_hand_input",
            rotor_joint.mimic is not None
            and rotor_joint.mimic.joint == input_name
            and abs(rotor_joint.mimic.multiplier - GEAR_RATIO) < 1e-9,
            details=f"mimic={rotor_joint.mimic}",
        )

    # --- Multiplicity: carrier station count matches config. ---
    if r.carrier == "fixed_sleeve":
        rotor = object_model.get_part("rotor")
        sleeve_names = {v.name for v in rotor.visuals if v.name and v.name.startswith("tube_sleeve_")}
        ctx.check(
            "sleeve_count_matches_config",
            len(sleeve_names) == r.bucket_count,
            details=f"sleeves={sorted(sleeve_names)}, expected={r.bucket_count}",
        )
        ctx.check(
            "no_bucket_parts_for_rigid_carrier",
            not any(n.startswith("bucket_") for n in parts),
            details=str(sorted(parts)),
        )
    else:
        bucket_parts = [n for n in parts if n.startswith("bucket_")]
        swing_joints = [
            j for j in object_model.articulations
            if j.name.startswith("bucket_swing_")
            and j.articulation_type == ArticulationType.REVOLUTE
        ]
        ctx.check(
            "bucket_multiplicity_matches_config",
            len(bucket_parts) == r.bucket_count and len(swing_joints) == r.bucket_count,
            details=f"parts={len(bucket_parts)} joints={len(swing_joints)} expected={r.bucket_count}",
        )

    if r.support_base == "table_clamp":
        clamp_joint = joints.get("clamp_adjustment")
        ctx.check(
            "clamp_screw_prismatic_z",
            "clamp_screw" in parts
            and clamp_joint is not None
            and clamp_joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(clamp_joint.axis) == (0.0, 0.0, 1.0),
            details=str(clamp_joint),
        )
    if r.support_base == "bench_tripod":
        body = object_model.get_part("body")
        body_visuals = {v.name for v in body.visuals if v.name}
        ctx.check(
            "tripod_feet_present",
            all(f"tripod_foot_{i}" in body_visuals and f"foot_pad_{i}" in body_visuals for i in range(3)),
            details=str(sorted(v for v in body_visuals if "foot" in v)),
        )

    # --- Rule 5: sampled-pose motion QC across all non-FIXED joints. ---
    movable = [
        j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED and j.mimic is None
    ]
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=32 if len(movable) >= 6 else 72,
        ignore_fixed=True,
    )

    # --- Targeted motion semantics. ---
    # 1) The hand input visibly sweeps.
    input_part_name = "rim_grip" if r.drive_input == "rim_handwheel" else "crank"
    sweep_elem = {
        "offset_crank": "handle_pin",
        "spline_crank": "wood_grip",
        "rim_handwheel": "grip_roller",
    }[r.drive_input]
    input_part = object_model.get_part(input_part_name)
    rest_aabb = ctx.part_element_world_aabb(input_part, elem=sweep_elem)
    with ctx.pose({input_joint: math.pi / 2.0}):
        turned_aabb = ctx.part_element_world_aabb(input_part, elem=sweep_elem)
    min_disp = 0.10 if r.drive_input == "spline_crank" else 0.02
    ctx.check(
        "hand_input_visibly_sweeps",
        rest_aabb is not None and turned_aabb is not None
        and math.dist(_center(rest_aabb), _center(turned_aabb)) > min_disp,
        details=f"rest={rest_aabb and _center(rest_aabb)}, turned={turned_aabb and _center(turned_aabb)}",
    )

    # 2) The free-spinning grip (where the module has one) spins on its pin.
    if r.drive_input == "offset_crank":
        knob = object_model.get_part("crank_knob")
        knob_joint = joints["crank_knob_spin"]
        rib0 = ctx.part_element_world_aabb(knob, elem="grip_rib_0")
        with ctx.pose({knob_joint: 1.0}):
            rib1 = ctx.part_element_world_aabb(knob, elem="grip_rib_0")
        ctx.check(
            "crank_knob_spins",
            rib0 is not None and rib1 is not None
            and math.dist(_center(rib0), _center(rib1)) > 0.003,
            details=f"rest={rib0 and _center(rib0)}, spun={rib1 and _center(rib1)}",
        )
    elif r.drive_input == "rim_handwheel":
        grip = object_model.get_part("rim_grip")
        grip_joint = joints["grip_spin"]
        rib0 = ctx.part_element_world_aabb(grip, elem="grip_rib_0")
        with ctx.pose({grip_joint: 1.0}):
            rib1 = ctx.part_element_world_aabb(grip, elem="grip_rib_0")
        ctx.check(
            "rim_grip_spins",
            rib0 is not None and rib1 is not None
            and math.dist(_center(rib0), _center(rib1)) > 0.003,
            details=f"rest={rib0 and _center(rib0)}, spun={rib1 and _center(rib1)}",
        )

    # 3) The rotor responds: geared families through the input joint (mimic),
    #    the drum family through its independent rotor joint.
    rotor = object_model.get_part("rotor")
    if r.carrier == "fixed_sleeve":
        marker = ("rotor", "tube_sleeve_0")
    elif r.carrier == "bar_fork_swing":
        marker = ("rotor", "crossbar_x")
    else:
        marker = ("bucket_0", None)

    def _marker_center():
        if marker[1] is None:
            aabb = ctx.part_world_aabb(object_model.get_part(marker[0]))
        else:
            aabb = ctx.part_element_world_aabb(object_model.get_part(marker[0]), elem=marker[1])
        return None if aabb is None else _center(aabb)

    if r.body_form == "drum_gearbox_crown":
        pose_target = {rotor_joint: math.radians(50.0)}
    else:
        pose_target = {input_joint: 0.30}  # mimic x4 -> rotor 1.2 rad
    c0 = _marker_center()
    with ctx.pose(pose_target):
        c1 = _marker_center()
    if marker[1] == "crossbar_x":
        # A symmetric bar re-centres on itself; compare AABB spans instead.
        aabb_rest = ctx.part_element_world_aabb(rotor, elem="crossbar_x")
        with ctx.pose(pose_target):
            aabb_rot = ctx.part_element_world_aabb(rotor, elem="crossbar_x")
        rest_dy = aabb_rest[1][1] - aabb_rest[0][1] if aabb_rest else None
        rot_dy = aabb_rot[1][1] - aabb_rot[0][1] if aabb_rot else None
        ctx.check(
            "rotor_responds_to_drive",
            rest_dy is not None and rot_dy is not None and rot_dy > rest_dy + 0.03,
            details=f"rest_dy={rest_dy}, rotated_dy={rot_dy}",
        )
    else:
        ctx.check(
            "rotor_responds_to_drive",
            c0 is not None and c1 is not None
            and math.hypot(c1[0] - c0[0], c1[1] - c0[1]) > 0.01,
            details=f"rest={c0}, driven={c1}",
        )

    # 4) Swing buckets hang at rest and swing radially outward + upward.
    if r.carrier in ("plate_swing", "bar_fork_swing"):
        swing0 = joints["bucket_swing_0"]
        bucket0 = object_model.get_part("bucket_0")
        elem = "tube_shell" if r.carrier == "plate_swing" else "bucket_shell"
        rest = ctx.part_element_world_aabb(bucket0, elem=elem)
        with ctx.pose({swing0: swing0.motion_limits.upper * 0.85}):
            swung = ctx.part_element_world_aabb(bucket0, elem=elem)
        rest_c = None if rest is None else _center(rest)
        swung_c = None if swung is None else _center(swung)
        ctx.check(
            "bucket_swings_outward_and_up",
            rest_c is not None and swung_c is not None
            and (swung_c[0] - rest_c[0]) > 0.015  # bucket_0 sits on +x
            and (swung_c[2] - rest_c[2]) > 0.008,
            details=f"rest={rest_c}, swung={swung_c}",
        )

    # 5) Clamp screw advances toward the jaw without touching it.
    if r.support_base == "table_clamp":
        clamp_joint = joints["clamp_adjustment"]
        screw = object_model.get_part("clamp_screw")
        body = object_model.get_part("body")
        jaw = ctx.part_element_world_aabb(body, elem="upper_jaw_pad")
        pad_rest = ctx.part_element_world_aabb(screw, elem="pressure_pad")
        with ctx.pose({clamp_joint: clamp_joint.motion_limits.upper}):
            pad_tight = ctx.part_element_world_aabb(screw, elem="pressure_pad")
        gap_rest = None if jaw is None or pad_rest is None else jaw[0][2] - pad_rest[1][2]
        gap_tight = None if jaw is None or pad_tight is None else jaw[0][2] - pad_tight[1][2]
        ctx.check(
            "clamp_screw_advances",
            gap_rest is not None and gap_tight is not None
            and gap_rest - gap_tight > 0.012 and gap_tight >= 0.0,
            details=f"rest_gap={gap_rest}, tight_gap={gap_tight}",
        )

    return ctx.report()


__all__ = [
    "BodyForm",
    "Carrier",
    "DriveInput",
    "PaletteStyle",
    "PictureX0611CentrifugeMachine2Config",
    "ResolvedCentrifugeMachine2Config",
    "SupportBase",
    "__modular__",
    "build_picturex_0611_centrifuge_machine2",
    "build_seeded_picturex_0611_centrifuge_machine2",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_centrifuge_machine2_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
