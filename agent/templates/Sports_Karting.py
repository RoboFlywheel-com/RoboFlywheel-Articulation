# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for the ``go_kart`` 小类 (Sports / Karting).

A single-seat low racing / rental / off-road go-kart: a low chassis (tubular
steel frame, sheet deck, or raised buggy cage), four fat slick tires (smaller
narrower front, bigger wider rear), a single molded bucket seat, a small tilted
steering wheel, an exposed live rear axle, and an optional engine / chain drive.

Frame convention (from the 5★ parent ``…dbb0d663``):
  +Y = forward (front of the kart), -Y = rear.
  +X = kart's left, -X = kart's right.
  +Z = up; ground at z=0, wheel centers at z = tire_radius.

Pattern: ``mixed`` (parallel_children + multiplicity) — like ``sports_car`` the
template builds DIRECTLY (no ``_modular`` assembler). One ``chassis`` root part
carries the Slot A frame form + Slot D rear-drive visuals + the cross_tube
ladder (multiplicity). The seat (FIXED), steering wheel (CONTINUOUS), four
wheels (CONTINUOUS roll) and two front knuckles (REVOLUTE steer) all parent to
the chassis.

LOCKED core articulation (never a slot axis, every variant identical):
  4 wheels        : CONTINUOUS roll about local X
  2 front knuckles: REVOLUTE king-pin steer about Z (±0.52); front wheel rolls
                    off its knuckle, rear wheels roll off the chassis.
  steering wheel  : CONTINUOUS spin about its tilted column axis (local −Z)
  seat            : FIXED to the chassis

5★ sources adapted (AUTHORING.md §A Rule 3 — geometry never downgraded):
  parent  rec_racing-go-kart-…_dbb0d663  — baseline tubular frame, wheels,
          knuckles, molded bucket, round 3-spoke wheel, bare axle, kinematics.
  flatdeck  rec_go_kart_var_flatdeck   — Slot A flat sheet deck + bumper rail.
  buggy     rec_go_kart_var_buggy      — Slot A raised cage + down-bars.
  bodywork  rec_go_kart_var_bodywork   — Slot A continuous CIK shroud shell.
  flatsling rec_go_kart_var_flatsling  — Slot B low sling seat.
  highback  rec_go_kart_var_highback   — Slot B full-wrap section-loft shell.
  butterfly rec_go_kart_var_butterfly  — Slot C open D-cut spline rim.
  qrhub     rec_go_kart_var_qrhub      — Slot C quick-release boss + flat rim.
  sideengine rec_go_kart_var_sideengine — Slot D finned engine pod.
  chaindrive rec_go_kart_var_chaindrive — Slot D sprocket + chain loop.
  crosstubes6 rec_go_kart_var_crosstubes6 — cross_tube multiplicity helper.

Structural diversity axes (slot_choices_for_seed records these):
  A frame_chassis_form (4) × B seat_form (3) × C steering_wheel_form (3)
  × D rear_drive_form (3) × cross_tube_count (multiplicity, gated off flat_deck)
  + palette_style (5, orthogonal, drives every .visual material).
Structural floor A × C = 12 ≫ 10.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from math import atan2, cos, pi, sin
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    section_loft,
    superellipse_side_loft,
    tube_from_spline_points,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums
# --------------------------------------------------------------------------- #
FrameChassisForm = Literal["open_tubular", "bodywork_shroud", "flat_deck", "offroad_buggy"]
SeatForm = Literal["molded_bucket", "flat_sling", "high_back_shell"]
SteeringWheelForm = Literal["round_3spoke", "butterfly_open", "quick_release_hub"]
RearDriveForm = Literal["bare_axle", "side_engine_pod", "chain_sprocket_drive"]
PaletteStyle = Literal[
    "race_pink_red",
    "rental_charcoal",
    "offroad_green",
    "bare_steel",
    "brass_drive",
]

FRAME_CHASSIS_FORMS: tuple[FrameChassisForm, ...] = (
    "open_tubular",
    "bodywork_shroud",
    "flat_deck",
    "offroad_buggy",
)
SEAT_FORMS: tuple[SeatForm, ...] = ("molded_bucket", "flat_sling", "high_back_shell")
STEERING_WHEEL_FORMS: tuple[SteeringWheelForm, ...] = (
    "round_3spoke",
    "butterfly_open",
    "quick_release_hub",
)
REAR_DRIVE_FORMS: tuple[RearDriveForm, ...] = (
    "bare_axle",
    "side_engine_pod",
    "chain_sprocket_drive",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "race_pink_red",
    "rental_charcoal",
    "offroad_green",
    "bare_steel",
    "brass_drive",
)

CROSS_TUBE_MIN = 2
CROSS_TUBE_MAX = 10

# --------------------------------------------------------------------------- #
# Palette presets (Slot palette) — every colorway resolves to a `mats` dict with
# the SAME token set so the builder is colorway-agnostic. Tokens:
#   body   — body shell / shroud paint      frame  — main frame steel
#   dark   — dark steel / brackets          seat   — seat upholstery
#   rim    — wheel rim silver               rubber — tires
#   marker — yellow marker lug              decal  — white number decal
#   engine — engine block alloy             drive  — sprocket / chain accent
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "race_pink_red": {
        "body": (0.92, 0.28, 0.42, 1.0),
        "accent": (0.80, 0.14, 0.16, 1.0),
        "frame": (0.72, 0.73, 0.76, 1.0),
        "dark": (0.26, 0.27, 0.29, 1.0),
        "seat": (0.82, 0.82, 0.84, 1.0),
        "rim": (0.60, 0.61, 0.64, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
        "marker": (0.95, 0.80, 0.15, 1.0),
        "decal": (0.96, 0.96, 0.97, 1.0),
        "engine": (0.35, 0.37, 0.35, 1.0),
        "drive": (0.42, 0.43, 0.45, 1.0),
    },
    "rental_charcoal": {
        "body": (0.16, 0.17, 0.19, 1.0),
        "accent": (0.34, 0.35, 0.38, 1.0),
        "frame": (0.72, 0.73, 0.76, 1.0),
        "dark": (0.26, 0.27, 0.29, 1.0),
        "seat": (0.82, 0.82, 0.84, 1.0),
        "rim": (0.60, 0.61, 0.64, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
        "marker": (0.95, 0.80, 0.15, 1.0),
        "decal": (0.92, 0.93, 0.95, 1.0),
        "engine": (0.30, 0.31, 0.33, 1.0),
        "drive": (0.40, 0.41, 0.43, 1.0),
    },
    "offroad_green": {
        "body": (0.22, 0.52, 0.28, 1.0),
        "accent": (0.12, 0.12, 0.13, 1.0),
        "frame": (0.70, 0.72, 0.74, 1.0),
        "dark": (0.24, 0.25, 0.27, 1.0),
        "seat": (0.80, 0.80, 0.82, 1.0),
        "rim": (0.58, 0.59, 0.62, 1.0),
        "rubber": (0.07, 0.07, 0.08, 1.0),
        "marker": (0.95, 0.80, 0.15, 1.0),
        "decal": (0.94, 0.95, 0.96, 1.0),
        "engine": (0.33, 0.35, 0.33, 1.0),
        "drive": (0.40, 0.41, 0.43, 1.0),
    },
    "bare_steel": {
        "body": (0.66, 0.67, 0.70, 1.0),
        "accent": (0.40, 0.41, 0.43, 1.0),
        "frame": (0.72, 0.73, 0.76, 1.0),
        "dark": (0.26, 0.27, 0.29, 1.0),
        "seat": (0.82, 0.82, 0.84, 1.0),
        "rim": (0.62, 0.63, 0.66, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
        "marker": (0.95, 0.80, 0.15, 1.0),
        "decal": (0.95, 0.96, 0.97, 1.0),
        "engine": (0.40, 0.42, 0.40, 1.0),
        "drive": (0.50, 0.51, 0.53, 1.0),
    },
    "brass_drive": {
        "body": (0.90, 0.26, 0.40, 1.0),
        "accent": (0.78, 0.14, 0.16, 1.0),
        "frame": (0.50, 0.51, 0.54, 1.0),
        "dark": (0.22, 0.22, 0.24, 1.0),
        "seat": (0.80, 0.80, 0.82, 1.0),
        "rim": (0.62, 0.63, 0.66, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
        "marker": (0.95, 0.80, 0.15, 1.0),
        "decal": (0.95, 0.96, 0.97, 1.0),
        "engine": (0.62, 0.63, 0.66, 1.0),
        "drive": (0.72, 0.56, 0.22, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Nominal kinematic constants (from the 5★ parent dbb0d663 L36-L50).
# --------------------------------------------------------------------------- #
FRONT_AXLE_Y = 0.74
REAR_AXLE_Y = -0.74
FRONT_TRACK_X = 0.46  # half-track to each front wheel center
REAR_TRACK_X = 0.50  # half-track to each rear wheel center (wider rear)

FRONT_TIRE_R = 0.115
FRONT_TIRE_W = 0.140
# rear_tire_bias equation: rear恒大恒宽.
REAR_TIRE_K_R = 1.22
REAR_TIRE_K_W = 1.64

FRAME_Z_LOW = 0.085
FRAME_Z_BUGGY = 0.20
COLUMN_TILT_NOMINAL = 0.55
STEER_LOCK = 0.52


@dataclass(frozen=True)
class GoKartConfig:
    frame_chassis_form: FrameChassisForm | None = None
    seat_form: SeatForm | None = None
    steering_wheel_form: SteeringWheelForm | None = None
    rear_drive_form: RearDriveForm | None = None
    cross_tube_count: int | None = None
    palette_style: PaletteStyle = "race_pink_red"

    ride_height_scale: float = 1.0
    track_width_scale: float = 1.0
    tire_radius_scale: float = 1.0
    column_tilt: float = COLUMN_TILT_NOMINAL
    seat_back_height_scale: float = 1.0
    qr_boss_height: float = 0.06
    name: str = "go_kart"


@dataclass(frozen=True)
class ResolvedGoKartConfig:
    frame_chassis_form: FrameChassisForm
    seat_form: SeatForm
    steering_wheel_form: SteeringWheelForm
    rear_drive_form: RearDriveForm
    cross_tube_count: int  # effective (0 when gated off under flat_deck)
    palette_style: PaletteStyle

    # resolved derived kinematics
    frame_z: float
    front_track_x: float
    rear_track_x: float
    front_tire_r: float
    front_tire_w: float
    rear_tire_r: float
    rear_tire_w: float
    axle_z_front: float
    axle_z_rear: float
    column_tilt: float
    seat_back_height_scale: float
    qr_boss_height: float
    name: str


# --------------------------------------------------------------------------- #
# Sampling
# --------------------------------------------------------------------------- #


def _weighted_cross_tube_count(rng: random.Random) -> int:
    """Small N high-frequency (real karts have few cross-tubes), large N rare."""
    buckets = list(range(CROSS_TUBE_MIN, CROSS_TUBE_MAX + 1))
    # 2,3,4 most common; 5,6 medium; 7-10 rare tail.
    weights = [0.26, 0.22, 0.16, 0.10, 0.09, 0.06, 0.045, 0.04, 0.0]
    # weights len 9 covers 2..10
    return rng.choices(buckets, weights=weights, k=1)[0]


def config_from_seed(seed: int) -> GoKartConfig:
    """Deterministic per-seed procedural sampling (seed 0 not special)."""
    rng = random.Random(seed)

    frame_chassis_form = rng.choice(FRAME_CHASSIS_FORMS)
    seat_form = rng.choice(SEAT_FORMS)
    steering_wheel_form = rng.choice(STEERING_WHEEL_FORMS)
    rear_drive_form = rng.choice(REAR_DRIVE_FORMS)
    cross_tube_count = _weighted_cross_tube_count(rng)
    palette_style = rng.choice(PALETTE_STYLES)

    # seat_back_height_scale range conditional on seat_form.
    if seat_form == "flat_sling":
        sbh = round(rng.uniform(0.7, 0.9), 4)
    elif seat_form == "high_back_shell":
        sbh = round(rng.uniform(1.1, 1.4), 4)
    else:  # molded_bucket
        sbh = round(rng.uniform(0.9, 1.1), 4)

    return GoKartConfig(
        frame_chassis_form=frame_chassis_form,
        seat_form=seat_form,
        steering_wheel_form=steering_wheel_form,
        rear_drive_form=rear_drive_form,
        cross_tube_count=cross_tube_count,
        palette_style=palette_style,
        ride_height_scale=round(rng.uniform(0.9, 1.15), 4),
        track_width_scale=round(rng.uniform(0.92, 1.08), 4),
        tire_radius_scale=round(rng.uniform(0.9, 1.12), 4),
        column_tilt=round(rng.uniform(0.45, 0.62), 4),
        seat_back_height_scale=sbh,
        qr_boss_height=round(rng.uniform(0.04, 0.09), 4),
        name=f"seeded_go_kart_{seed}",
    )


def _pick(value, choices):
    return value if value in choices else choices[0]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def resolve_config(config: GoKartConfig | None = None) -> ResolvedGoKartConfig:
    cfg = config or GoKartConfig()

    frame_chassis_form = _pick(cfg.frame_chassis_form, FRAME_CHASSIS_FORMS)
    seat_form = _pick(cfg.seat_form, SEAT_FORMS)
    steering_wheel_form = _pick(cfg.steering_wheel_form, STEERING_WHEEL_FORMS)
    rear_drive_form = _pick(cfg.rear_drive_form, REAR_DRIVE_FORMS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # cross_tube_count: clamp to [2,10], then gate OFF (0) under flat_deck
    # (the deck pan carries lateral stiffness — spec §Multiplicity gating).
    raw_ct = cfg.cross_tube_count if cfg.cross_tube_count is not None else 2
    cross_tube_count = int(_clamp(float(raw_ct), CROSS_TUBE_MIN, CROSS_TUBE_MAX))
    if frame_chassis_form == "flat_deck":
        cross_tube_count = 0

    # frame_z conditional: raised for buggy. ride_height_scale multiplies.
    ride_height_scale = _clamp(float(cfg.ride_height_scale), 0.9, 1.15)
    base_frame_z = FRAME_Z_BUGGY if frame_chassis_form == "offroad_buggy" else FRAME_Z_LOW
    frame_z = base_frame_z * ride_height_scale

    # track_width_scale: keep REAR_TRACK_X > FRONT_TRACK_X.
    track_width_scale = _clamp(float(cfg.track_width_scale), 0.92, 1.08)
    front_track_x = FRONT_TRACK_X * track_width_scale
    rear_track_x = REAR_TRACK_X * track_width_scale  # already > front by construction

    # tire_radius equation: rear恒大恒宽 (run_tests hard constraint).
    tire_radius_scale = _clamp(float(cfg.tire_radius_scale), 0.9, 1.12)
    front_tire_r = FRONT_TIRE_R * tire_radius_scale
    front_tire_w = FRONT_TIRE_W * tire_radius_scale
    rear_tire_r = front_tire_r * REAR_TIRE_K_R
    rear_tire_w = front_tire_w * REAR_TIRE_K_W
    axle_z_front = front_tire_r
    axle_z_rear = rear_tire_r

    column_tilt = _clamp(float(cfg.column_tilt), 0.45, 0.62)

    # seat_back_height_scale conditional clamp by form.
    if seat_form == "flat_sling":
        sbh = _clamp(float(cfg.seat_back_height_scale), 0.7, 0.9)
    elif seat_form == "high_back_shell":
        sbh = _clamp(float(cfg.seat_back_height_scale), 1.1, 1.4)
    else:
        sbh = _clamp(float(cfg.seat_back_height_scale), 0.9, 1.1)

    qr_boss_height = _clamp(float(cfg.qr_boss_height), 0.04, 0.09)

    return ResolvedGoKartConfig(
        frame_chassis_form=frame_chassis_form,
        seat_form=seat_form,
        steering_wheel_form=steering_wheel_form,
        rear_drive_form=rear_drive_form,
        cross_tube_count=cross_tube_count,
        palette_style=palette_style,
        frame_z=frame_z,
        front_track_x=front_track_x,
        rear_track_x=rear_track_x,
        front_tire_r=front_tire_r,
        front_tire_w=front_tire_w,
        rear_tire_r=rear_tire_r,
        rear_tire_w=rear_tire_w,
        axle_z_front=axle_z_front,
        axle_z_rear=axle_z_rear,
        column_tilt=column_tilt,
        seat_back_height_scale=sbh,
        qr_boss_height=qr_boss_height,
        name=cfg.name,
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Per-seed (slot, module) tuples consumed by module_topology_diversity.

    Records the post-resolution choices (after flat_deck → ladder gating) so the
    reported topology matches what is actually built. Includes the four
    structural axes (A/B/C/D, A×C=12 floor) plus the cross_tube_count
    multiplicity to lift the distinct count well past ≥10.
    """
    r = resolve_config(config_from_seed(seed))
    return [
        ("frame_chassis_form", r.frame_chassis_form),
        ("seat_form", r.seat_form),
        ("steering_wheel_form", r.steering_wheel_form),
        ("rear_drive_form", r.rear_drive_form),
        ("cross_tube_count", f"ct{r.cross_tube_count}"),
    ]


# --------------------------------------------------------------------------- #
# Geometry helpers (adapted from the 5★ sources)
# --------------------------------------------------------------------------- #


def _save(name: str, geom):
    return mesh_from_geometry(geom, name)


# ---- shared steering-column axis ------------------------------------------- #
# The lower-mount sleeve and the steering joint origin sit on ONE collinear
# tilted axis so the column shaft plugs straight down the sleeve and the big
# steering rim ring rides ABOVE the sleeve (the sleeve passes through the rim's
# central hole, never the rim tube). Both derive from frame_z so they track the
# ride height together — the old fixed col_top crashed the rim into the sleeve
# when frame_z climbed (buggy + tall ride height).
_COLUMN_BASE_Y = 0.295
_COLUMN_MOUNT_LEN = 0.30
_COLUMN_JOINT_PARAM = _COLUMN_MOUNT_LEN + 0.015  # rim center just above mount top
#   (≤ origin-far-from-geometry tol 0.02; the rim ring rides clear at radius
#    0.105 while the sleeve passes through the rim's central hole)


def _column_axis(r: ResolvedGoKartConfig):
    """Return (base_y, base_z, dir_y, dir_z) of the tilted column axis."""
    tilt = r.column_tilt
    base_y = _COLUMN_BASE_Y
    # base sits embedded in the floor_pan top (z-span fz-0.005..fz+0.025 at this
    # x,y) so the sleeve's lower end is fused to the frame, not a floating island.
    base_z = r.frame_z + 0.02
    return base_y, base_z, -math.sin(tilt), math.cos(tilt)


def _column_point(r: ResolvedGoKartConfig, param: float):
    base_y, base_z, dy, dz = _column_axis(r)
    return base_y + dy * param, base_z + dz * param


def _mirror_x(points):
    return [(-x, y, z) for x, y, z in points]


def _tube(name, pts, material, part, radius=0.022, samples=12, radial=14):
    part.visual(
        _save(name, tube_from_spline_points(pts, radius=radius, samples_per_segment=samples, radial_segments=radial)),
        material=material,
        name=name[:-4] if name.endswith(".obj") else name, material_class_id="metal.paint_coated",
    )


# ---- tires + wheels (parent dbb0d663 L61-L121) ----------------------------- #


def _tire_mesh(name, tire_radius, tire_width):
    hw = tire_width * 0.5
    profile = [
        (tire_radius * 0.46, -hw * 0.98),
        (tire_radius * 0.74, -hw * 1.00),
        (tire_radius * 0.92, -hw * 0.86),
        (tire_radius * 0.99, -hw * 0.50),
        (tire_radius, -hw * 0.14),
        (tire_radius, hw * 0.14),
        (tire_radius * 0.99, hw * 0.50),
        (tire_radius * 0.92, hw * 0.86),
        (tire_radius * 0.74, hw * 1.00),
        (tire_radius * 0.46, hw * 0.98),
        (tire_radius * 0.40, hw * 0.30),
        (tire_radius * 0.38, 0.0),
        (tire_radius * 0.40, -hw * 0.30),
        (tire_radius * 0.46, -hw * 0.98),
    ]
    return _save(name, LatheGeometry(profile, segments=56).rotate_y(pi / 2.0))


def _wheel_visuals(part, prefix, tire_radius, tire_width, mats):
    spin_rpy = Origin(rpy=(0.0, pi / 2.0, 0.0))  # cylinder axis -> local X
    part.visual(_tire_mesh(f"{prefix}_tire.obj", tire_radius, tire_width), material=mats["rubber"], name=f"{prefix}_tire", material_class_id="rubber.smooth_plain")
    part.visual(
        Cylinder(radius=tire_radius * 0.58, length=tire_width * 0.80),
        origin=spin_rpy,
        material=mats["rim"],
        name=f"{prefix}_rim", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Cylinder(radius=tire_radius * 0.30, length=tire_width * 0.92),
        origin=spin_rpy,
        material=mats["dark"],
        name=f"{prefix}_hub", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=tire_radius * 0.13, length=tire_width * 1.6),
        origin=spin_rpy,
        material=mats["dark"],
        name=f"{prefix}_axle", material_class_id="metal.steel_bare",
    )
    mr = tire_radius * 0.62
    part.visual(
        Box((tire_width * 0.55, tire_radius * 0.12, tire_radius * 0.12)),
        origin=Origin(xyz=(0.0, mr, 0.0)),
        material=mats["marker"],
        name=f"{prefix}_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )


# ---- cross_tube ladder (crosstubes6 L62-L102) ------------------------------ #


def _rail_left_pts(r: ResolvedGoKartConfig):
    fz = r.frame_z
    ftx, rtx = r.front_track_x, r.rear_track_x
    return [
        (ftx - 0.10, FRONT_AXLE_Y, fz),
        (0.30, 0.45, fz),
        (0.30, -0.10, fz),
        (0.32, -0.50, fz),
        (rtx - 0.06, REAR_AXLE_Y, fz + 0.02),
    ]


def _rail_xz_at_y(r: ResolvedGoKartConfig, y_pos: float):
    pts = _rail_left_pts(r)
    ys = [p[1] for p in pts]
    xs = [p[0] for p in pts]
    zs = [p[2] for p in pts]
    if y_pos >= ys[0]:
        return xs[0], zs[0]
    if y_pos <= ys[-1]:
        return xs[-1], zs[-1]
    for j in range(len(ys) - 1):
        if ys[j + 1] <= y_pos <= ys[j]:
            t = (ys[j] - y_pos) / (ys[j] - ys[j + 1]) if ys[j] != ys[j + 1] else 0.0
            x = xs[j] + t * (xs[j + 1] - xs[j])
            z = zs[j] + t * (zs[j + 1] - zs[j])
            return x, z
    return xs[0], zs[0]


def _lateral_cross_tube(r: ResolvedGoKartConfig, y_pos: float, radius=0.018):
    x_left, z_rail = _rail_xz_at_y(r, y_pos)
    pts = [
        (-x_left, y_pos, z_rail + 0.01),
        (0.0, y_pos, z_rail + 0.03),
        (x_left, y_pos, z_rail + 0.01),
    ]
    return tube_from_spline_points(pts, radius=radius, samples_per_segment=12, radial_segments=14)


def _add_cross_tubes(chassis, r: ResolvedGoKartConfig, mats) -> None:
    n = r.cross_tube_count
    if n <= 0:
        return
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0.0
        y = FRONT_AXLE_Y + t * (REAR_AXLE_Y - FRONT_AXLE_Y)
        ct = _lateral_cross_tube(r, y)
        chassis.visual(_save(f"cross_tube_{i}.obj", ct), material=mats["frame"], name=f"cross_tube_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"race_pink_red", "rental_charcoal", "offroad_green", "brass_drive"} else "metal.steel_bare"))


# --------------------------------------------------------------------------- #
# Slot A — frame_chassis_form (chassis visuals)
# --------------------------------------------------------------------------- #


def _add_common_frame_anchors(chassis, r: ResolvedGoKartConfig, mats) -> None:
    """floor_pan + seat_tray + column_lower_mount — the downstream mount faces
    every Slot A form must provide (seat FIXED / steering套接)."""
    fz = r.frame_z
    chassis.visual(
        Box((0.46, 0.52, 0.03)),
        origin=Origin(xyz=(0.0, 0.34, fz + 0.01)),
        material=mats["dark"],
        name="floor_pan", material_class_id="metal.blackened_gunmetal",
    )
    chassis.visual(
        Box((0.60, 0.40, 0.03)),
        origin=Origin(xyz=(0.0, -0.06, fz + 0.05 - 0.015)),
        material=mats["dark"],
        name="seat_tray", material_class_id="metal.blackened_gunmetal",
    )
    # Tilted column lower-mount sleeve on the shared collinear column axis; the
    # steering column plugs straight down it. Centered at half the sleeve length
    # along the axis from its base so the rim (mounted at _COLUMN_JOINT_PARAM,
    # beyond the sleeve top) rides clear above it.
    mc_y, mc_z = _column_point(r, _COLUMN_MOUNT_LEN * 0.5)
    chassis.visual(
        Cylinder(radius=0.024, length=_COLUMN_MOUNT_LEN),
        origin=Origin(xyz=(0.0, mc_y, mc_z), rpy=(r.column_tilt, 0.0, 0.0)),
        material=mats["dark"],
        name="column_lower_mount", material_class_id="metal.blackened_gunmetal",
    )
    # Front king-pin mount bosses straddle each front steer joint origin
    # (±front_track_x, FRONT_AXLE_Y, axle_z_front) so the REVOLUTE origin always
    # has real chassis geometry within tol on EVERY Slot A frame (flat_deck has
    # no front cross tube, the raised frames sit far above the axle line).
    kp_h = 0.06
    for nm, sx in (("left_kingpin_mount", 1.0), ("right_kingpin_mount", -1.0)):
        chassis.visual(
            Cylinder(radius=0.020, length=kp_h),
            origin=Origin(xyz=(sx * r.front_track_x, FRONT_AXLE_Y, r.axle_z_front)),
            material=mats["dark"],
            name=nm, material_class_id="metal.cast_iron_bare",
        )
        # short tie from the kingpin boss inboard to the front cross-tube line so
        # the boss is not a floating island on frames without a full front tube.
        _tube(
            f"{nm}_tie.obj",
            [
                (sx * r.front_track_x, FRONT_AXLE_Y, r.axle_z_front + 0.01),
                (sx * (r.front_track_x - 0.08), FRONT_AXLE_Y, fz + 0.01),
            ],
            mats["dark"], chassis, radius=0.012, samples=4, radial=10,
        )


def _frame_open_tubular(chassis, r: ResolvedGoKartConfig, mats) -> None:
    """Exposed welded tubular frame (parent dbb0d663 L145-L293)."""
    fz = r.frame_z
    rail = _rail_left_pts(r)
    _tube("left_main_rail.obj", rail, mats["frame"], chassis, radius=0.022)
    _tube("right_main_rail.obj", _mirror_x(rail), mats["frame"], chassis, radius=0.022)
    _tube(
        "center_spine.obj",
        [(0.0, 0.70, fz + 0.01), (0.0, 0.20, fz), (0.0, -0.30, fz), (0.0, REAR_AXLE_Y, fz + 0.02)],
        mats["frame"], chassis, radius=0.020, samples=14,
    )
    _front_rear_cross(chassis, r, mats)
    for nm, pts in (
        ("left_brace.obj", [(0.30, 0.20, fz), (0.16, 0.05, fz), (0.0, -0.05, fz)]),
        ("right_brace.obj", [(-0.30, 0.20, fz), (-0.16, 0.05, fz), (0.0, -0.05, fz)]),
    ):
        _tube(nm, pts, mats["frame"], chassis, radius=0.014, samples=8, radial=12)

    # pink side pods (bodywork)
    pod_sections = [
        (0.30, fz - 0.01, fz + 0.12, 0.22),
        (0.02, fz - 0.02, fz + 0.15, 0.26),
        (-0.26, fz - 0.01, fz + 0.12, 0.22),
    ]
    left_pod = superellipse_side_loft(pod_sections, exponents=2.6, segments=40).translate(0.40, 0.0, 0.0)
    right_pod = superellipse_side_loft(pod_sections, exponents=2.6, segments=40).translate(-0.40, 0.0, 0.0)
    chassis.visual(_save("left_side_pod.obj", left_pod), material=mats["body"], name="left_side_pod", material_class_id="plastic.opaque_glossy_molded")
    chassis.visual(_save("right_side_pod.obj", right_pod), material=mats["body"], name="right_side_pod", material_class_id="plastic.opaque_glossy_molded")
    for sx, nm in ((0.515, "left_number_5"), (-0.515, "right_number_5")):
        chassis.visual(
            Box((0.02, 0.10, 0.12)),
            origin=Origin(xyz=(sx, 0.02, fz + 0.06)),
            material=mats["decal"],
            name=nm, appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    # red front/rear fairing
    nose = superellipse_side_loft(
        [
            (FRONT_AXLE_Y - 0.02, fz - 0.01, fz + 0.10, 0.60),
            (FRONT_AXLE_Y + 0.16, fz - 0.01, fz + 0.11, 0.70),
            (FRONT_AXLE_Y + 0.32, fz + 0.00, fz + 0.09, 0.42),
        ],
        exponents=2.8, segments=44,
    )
    chassis.visual(_save("front_fairing.obj", nose), material=mats["accent"], name="front_fairing", material_class_id="plastic.opaque_glossy_molded")
    rear_fairing = superellipse_side_loft(
        [
            (REAR_AXLE_Y - 0.04, fz + 0.00, fz + 0.10, 0.58),
            (REAR_AXLE_Y - 0.20, fz + 0.00, fz + 0.10, 0.70),
            (REAR_AXLE_Y - 0.34, fz + 0.01, fz + 0.08, 0.52),
        ],
        exponents=2.6, segments=40,
    )
    chassis.visual(_save("rear_fairing.obj", rear_fairing), material=mats["accent"], name="rear_fairing", material_class_id="plastic.opaque_glossy_molded")


def _front_rear_cross(chassis, r: ResolvedGoKartConfig, mats, rail_r=0.020) -> None:
    fz = r.frame_z
    ftx, rtx = r.front_track_x, r.rear_track_x
    _tube(
        "front_cross_tube.obj",
        [(-ftx, FRONT_AXLE_Y, fz + 0.01), (0.0, FRONT_AXLE_Y + 0.02, fz + 0.03), (ftx, FRONT_AXLE_Y, fz + 0.01)],
        mats["frame"], chassis, radius=rail_r,
    )
    _tube(
        "rear_cross_tube.obj",
        [(-rtx, REAR_AXLE_Y, fz + 0.02), (0.0, REAR_AXLE_Y - 0.02, fz + 0.02), (rtx, REAR_AXLE_Y, fz + 0.02)],
        mats["frame"], chassis, radius=0.022,
    )


def _frame_bodywork_shroud(chassis, r: ResolvedGoKartConfig, mats) -> None:
    """Continuous CIK molded shroud shell (bodywork L141-L195) over the rails."""
    fz = r.frame_z
    rail = _rail_left_pts(r)
    _tube("left_main_rail.obj", rail, mats["frame"], chassis, radius=0.022)
    _tube("right_main_rail.obj", _mirror_x(rail), mats["frame"], chassis, radius=0.022)
    _tube(
        "center_spine.obj",
        [(0.0, 0.70, fz + 0.01), (0.0, 0.20, fz), (0.0, -0.30, fz), (0.0, REAR_AXLE_Y, fz + 0.02)],
        mats["frame"], chassis, radius=0.020, samples=14,
    )
    _front_rear_cross(chassis, r, mats)
    shell_sections = [
        (0.96, fz - 0.02, fz + 0.08, 0.44),
        (0.90, fz - 0.02, fz + 0.10, 0.66),
        (0.82, fz - 0.02, fz + 0.12, 0.80),
        (0.74, fz - 0.03, fz + 0.11, 0.86),
        (0.45, fz - 0.03, fz + 0.12, 0.96),
        (0.05, fz - 0.03, fz + 0.04, 0.92),
        (-0.30, fz - 0.03, fz + 0.04, 0.96),
        (-0.74, fz - 0.03, fz + 0.11, 1.00),
        (-0.92, fz - 0.02, fz + 0.10, 1.06),
        (-1.08, fz - 0.01, fz + 0.08, 0.72),
    ]
    bodywork_shell = superellipse_side_loft(shell_sections, exponents=2.6, segments=64)
    chassis.visual(_save("bodywork_shell.obj", bodywork_shell), material=mats["body"], name="bodywork_shell", material_class_id="plastic.opaque_glossy_molded")
    for sx, nm in ((0.44, "left_number_5"), (-0.44, "right_number_5")):
        chassis.visual(
            Box((0.02, 0.10, 0.12)),
            origin=Origin(xyz=(sx, 0.02, fz + 0.02)),
            material=mats["decal"],
            name=nm, appearance_only=AppearanceOnlySpec(kind="overlay"),
        )


def _frame_flat_deck(chassis, r: ResolvedGoKartConfig, mats) -> None:
    """Flat sheet deck pan + closed bumper-rail loop (flatdeck L148-L286)."""
    fz = r.frame_z
    deck_half_length = 0.80
    deck_half_width = 0.44
    deck_thickness = 0.025
    deck_top_z = fz + deck_thickness
    chassis.visual(
        Box((deck_half_width * 2.0, deck_half_length * 2.0, deck_thickness)),
        origin=Origin(xyz=(0.0, 0.0, fz + deck_thickness * 0.5)),
        material=mats["body"],
        name="deck_pan", material_class_id=("metal.paint_coated" if r.palette_style in {"race_pink_red", "rental_charcoal", "offroad_green", "brass_drive"} else "metal.steel_bare"),
    )
    rail_z = deck_top_z + 0.10
    front_ext, rear_ext = 0.14, 0.12
    hw, hl = deck_half_width, deck_half_length
    bumper_points = [
        (0.0, hl + front_ext, rail_z),
        (hw * 0.65, hl + front_ext * 0.80, rail_z),
        (hw, hl, rail_z),
        (hw, hl * 0.40, rail_z),
        (hw, -hl * 0.40, rail_z),
        (hw, -hl, rail_z),
        (hw * 0.65, -(hl + rear_ext * 0.80), rail_z),
        (0.0, -(hl + rear_ext), rail_z),
        (-hw * 0.65, -(hl + rear_ext * 0.80), rail_z),
        (-hw, -hl, rail_z),
        (-hw, -hl * 0.40, rail_z),
        (-hw, hl * 0.40, rail_z),
        (-hw, hl, rail_z),
        (-hw * 0.65, hl + front_ext * 0.80, rail_z),
        (0.0, hl + front_ext, rail_z),
    ]
    bumper_tube = tube_from_spline_points(bumper_points, radius=0.024, samples_per_segment=10, radial_segments=14)
    chassis.visual(_save("bumper_rail.obj", bumper_tube), material=mats["frame"], name="bumper_rail", material_class_id=("metal.paint_coated" if r.palette_style in {"race_pink_red", "rental_charcoal", "offroad_green", "brass_drive"} else "metal.steel_bare"))
    stanchion_positions = [
        (hw, hl, rail_z), (hw, 0.0, rail_z), (hw, -hl, rail_z),
        (0.0, -(hl + rear_ext), rail_z), (-hw, -hl, rail_z),
        (-hw, 0.0, rail_z), (-hw, hl, rail_z), (0.0, hl + front_ext, rail_z),
    ]
    for i, (sx, sy, sz) in enumerate(stanchion_positions):
        sh = sz - deck_top_z
        chassis.visual(
            Cylinder(radius=0.014, length=sh),
            origin=Origin(xyz=(sx, sy, deck_top_z + sh * 0.5)),
            material=mats["frame"],
            name=f"stanchion_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"race_pink_red", "rental_charcoal", "offroad_green", "brass_drive"} else "metal.steel_bare"),
        )
    for i, sign in enumerate((1.0, -1.0)):
        chassis.visual(
            Box((0.02, 0.12, 0.10)),
            origin=Origin(xyz=(sign * (deck_half_width + 0.001), 0.02, fz + deck_thickness * 0.5)),
            material=mats["decal"],
            name=f"number_5_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    # rear axle bearing mounts bridge deck -> live axle line.
    for i, sign in enumerate((1.0, -1.0)):
        bearing_x = sign * (r.rear_track_x - 0.12)
        bearing_height = max(0.02, r.axle_z_rear - deck_top_z)
        chassis.visual(
            Box((0.06, 0.08, bearing_height)),
            origin=Origin(xyz=(bearing_x, REAR_AXLE_Y, deck_top_z + bearing_height * 0.5)),
            material=mats["dark"],
            name=f"rear_bearing_mount_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _frame_offroad_buggy(chassis, r: ResolvedGoKartConfig, mats) -> None:
    """Raised tubular frame + roll cage hoop + down-bars (buggy L142-L260)."""
    fz = r.frame_z
    ftx, rtx = r.front_track_x, r.rear_track_x
    cage_rail_x = 0.30
    cage_half_width = 0.32
    cage_peak_z = fz + 0.62
    cage_hoop_y = -0.10
    cage_front_y = 0.50

    rail_pts = [
        (cage_rail_x, FRONT_AXLE_Y, fz),
        (0.32, 0.45, fz),
        (0.32, -0.10, fz),
        (0.34, -0.50, fz),
        (rtx - 0.06, REAR_AXLE_Y, fz + 0.02),
    ]
    _tube("left_main_rail.obj", rail_pts, mats["frame"], chassis, radius=0.024)
    _tube("right_main_rail.obj", _mirror_x(rail_pts), mats["frame"], chassis, radius=0.024)
    _tube(
        "center_spine.obj",
        [(0.0, 0.70, fz + 0.01), (0.0, 0.20, fz), (0.0, -0.30, fz), (0.0, REAR_AXLE_Y, fz + 0.02)],
        mats["frame"], chassis, radius=0.022,
    )
    _front_rear_cross(chassis, r, mats, rail_r=0.022)

    # vertical frame risers tie the raised frame down to the axle lines (no float).
    for nm, x, y, z_bot, z_top in (
        ("left_front_riser", ftx - 0.06, FRONT_AXLE_Y, r.axle_z_front + 0.04, fz),
        ("right_front_riser", -(ftx - 0.06), FRONT_AXLE_Y, r.axle_z_front + 0.04, fz),
        ("left_rear_riser", rtx - 0.06, REAR_AXLE_Y, r.axle_z_rear + 0.04, fz + 0.02),
        ("right_rear_riser", -(rtx - 0.06), REAR_AXLE_Y, r.axle_z_rear + 0.04, fz + 0.02),
    ):
        _tube(
            f"{nm}.obj",
            [(x, y, z_bot), (x, y, (z_bot + z_top) * 0.5), (x, y, z_top)],
            mats["frame"], chassis, radius=0.018, samples=6, radial=12,
        )

    # roll cage hoop (lands on side rail real face at fz, no floating island).
    hoop_left_base = (cage_rail_x, cage_hoop_y, fz)
    hoop_left_top = (cage_half_width, cage_hoop_y, cage_peak_z)
    hoop_center = (0.0, cage_hoop_y, cage_peak_z + 0.02)
    hoop_right_top = (-cage_half_width, cage_hoop_y, cage_peak_z)
    hoop_right_base = (-cage_rail_x, cage_hoop_y, fz)
    _tube(
        "roll_cage_hoop.obj",
        [
            hoop_left_base,
            (cage_rail_x, cage_hoop_y, fz + 0.30),
            hoop_left_top,
            hoop_center,
            hoop_right_top,
            (-cage_rail_x, cage_hoop_y, fz + 0.30),
            hoop_right_base,
        ],
        mats["body"], chassis, radius=0.026, samples=16, radial=16,
    )
    # front + rear down-bars from hoop top to frame rails.
    for nm, pts in (
        ("cage_front_left_bar", [hoop_left_top, (cage_half_width + 0.02, 0.20, cage_peak_z - 0.18), (cage_rail_x + 0.02, cage_front_y, fz + 0.04)]),
        ("cage_front_right_bar", [hoop_right_top, (-cage_half_width - 0.02, 0.20, cage_peak_z - 0.18), (-cage_rail_x - 0.02, cage_front_y, fz + 0.04)]),
        ("cage_rear_left_bar", [hoop_left_top, (cage_half_width + 0.01, cage_hoop_y - 0.20, cage_peak_z - 0.20), (cage_rail_x, -0.52, fz + 0.04)]),
        ("cage_rear_right_bar", [hoop_right_top, (-cage_half_width - 0.01, cage_hoop_y - 0.20, cage_peak_z - 0.20), (-cage_rail_x, -0.52, fz + 0.04)]),
    ):
        _tube(f"{nm}.obj", pts, mats["body"], chassis, radius=0.026, samples=14, radial=16)


_FRAME_BUILDERS = {
    "open_tubular": _frame_open_tubular,
    "bodywork_shroud": _frame_bodywork_shroud,
    "flat_deck": _frame_flat_deck,
    "offroad_buggy": _frame_offroad_buggy,
}


# --------------------------------------------------------------------------- #
# Slot D — rear_drive_form (chassis visuals on the rear, no joint)
# --------------------------------------------------------------------------- #


def _rear_axle_bar(chassis, r: ResolvedGoKartConfig, mats) -> None:
    chassis.visual(
        Cylinder(radius=0.018, length=r.rear_track_x * 2.0 - 0.02),
        origin=Origin(xyz=(0.0, REAR_AXLE_Y, r.axle_z_rear), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["dark"],
        name="rear_axle_bar", material_class_id="metal.steel_bare",
    )
    # short hanger brackets tie the axle bar up to the frame (connectivity).
    for nm, x in (("left_axle_hanger", 0.18), ("right_axle_hanger", -0.18)):
        _tube(
            f"{nm}.obj",
            [(x, REAR_AXLE_Y, r.axle_z_rear + 0.018), (x, REAR_AXLE_Y, r.frame_z + 0.01)],
            mats["dark"], chassis, radius=0.012, samples=4, radial=10,
        )


def _drive_bare_axle(chassis, r: ResolvedGoKartConfig, mats) -> None:
    _rear_axle_bar(chassis, r, mats)


def _drive_side_engine_pod(chassis, r: ResolvedGoKartConfig, mats) -> None:
    """Right-rear finned single-cylinder engine pod (sideengine L522-L686)."""
    _rear_axle_bar(chassis, r, mats)
    fz = r.frame_z
    eng_x = -0.18
    eng_y = REAR_AXLE_Y + 0.04
    eng_z_top = fz + 0.06
    block_w, block_d, block_h = 0.12, 0.14, 0.10

    for nm, pts in (
        ("engine_mount_inner", [(-0.06, REAR_AXLE_Y, fz + 0.02), (-0.10, eng_y, eng_z_top - 0.01)]),
        ("engine_mount_outer", [(-0.34, REAR_AXLE_Y, fz + 0.02), (-0.24, eng_y, eng_z_top - 0.01)]),
    ):
        _tube(f"{nm}.obj", pts, mats["frame"], chassis, radius=0.014, samples=6, radial=10)
    chassis.visual(
        Box((0.24, 0.18, 0.012)),
        origin=Origin(xyz=(eng_x + 0.02, eng_y, eng_z_top - 0.006)),
        material=mats["dark"],
        name="engine_mount_plate", material_class_id="metal.blackened_gunmetal",
    )
    chassis.visual(
        Box((block_w, block_d, block_h)),
        origin=Origin(xyz=(eng_x, eng_y, eng_z_top + block_h * 0.5)),
        material=mats["engine"],
        name="engine_block", material_class_id="metal.aluminum_bare",
    )
    chassis.visual(
        Cylinder(radius=0.048, length=block_w + 0.02),
        origin=Origin(xyz=(eng_x, eng_y, eng_z_top + 0.01), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["engine"],
        name="crankcase", material_class_id="metal.aluminum_bare",
    )
    # finned cylinder head (stacked lathe discs).
    cyl_r, fin_r = 0.032, 0.048
    n_fins, fin_t, fin_gap, base_h = 10, 0.003, 0.005, 0.008
    fin_profile = [(0.002, 0.0), (cyl_r * 1.2, 0.0), (cyl_r * 1.2, base_h), (cyl_r, base_h)]
    fzf = base_h
    for i in range(n_fins):
        fin_profile.append((fin_r, fzf))
        fin_profile.append((fin_r, fzf + fin_t))
        fin_profile.append((cyl_r, fzf + fin_t))
        fzf += fin_t + fin_gap
        if i < n_fins - 1:
            fin_profile.append((cyl_r, fzf))
    fin_profile.append((cyl_r, fzf))
    fin_profile.append((cyl_r * 0.7, fzf + 0.008))
    fin_profile.append((0.002, fzf + 0.010))
    cyl_base_z = eng_z_top + block_h
    chassis.visual(
        _save("finned_cylinder.obj", LatheGeometry(fin_profile, segments=36)),
        origin=Origin(xyz=(eng_x, eng_y, cyl_base_z)),
        material=mats["engine"],
        name="finned_cylinder", material_class_id="metal.aluminum_bare",
    )
    chassis.visual(
        Cylinder(radius=0.007, length=0.04),
        origin=Origin(xyz=(eng_x + 0.035, eng_y, cyl_base_z + fzf * 0.7), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["rim"],
        name="spark_plug", material_class_id="metal.stainless_matte",
    )
    exh_start_z = cyl_base_z + fzf * 0.75
    exhaust_pts = [
        (eng_x - 0.04, eng_y + 0.01, exh_start_z),
        (eng_x - 0.08, eng_y - 0.02, exh_start_z + 0.06),
        (eng_x - 0.10, eng_y - 0.10, exh_start_z + 0.12),
        (eng_x - 0.08, eng_y - 0.20, exh_start_z + 0.10),
    ]
    _tube("exhaust_header.obj", exhaust_pts, mats["accent"], chassis, radius=0.013, samples=10, radial=12)
    chassis.visual(
        Cylinder(radius=0.035, length=0.08),
        origin=Origin(xyz=(eng_x + 0.09, eng_y, cyl_base_z + fzf * 0.45)),
        material=mats["dark"],
        name="airbox", material_class_id="plastic.opaque_generic",
    )
    chassis.visual(
        Cylinder(radius=0.030, length=0.010),
        origin=Origin(xyz=(eng_x - block_w * 0.5 - 0.005, eng_y, eng_z_top + 0.04), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["drive"],
        name="drive_sprocket", material_class_id=("metal.steel_bare" if r.palette_style in {"race_pink_red", "rental_charcoal", "offroad_green", "bare_steel"} else "metal.brass_polished"),
    )


def _sprocket_mesh(name, outer_r, bore_r, width, n_segments=48):
    hw = width * 0.5
    hub_r = bore_r * 2.2
    web_r = (hub_r + outer_r * 0.82) * 0.5
    root_r = outer_r * 0.88
    tip_hw = hw * 0.58
    profile = [
        (bore_r, -hw), (bore_r, hw), (hub_r, hw), (hub_r, hw * 0.65),
        (web_r, hw * 0.38), (root_r, hw * 0.55), (root_r, tip_hw),
        (outer_r, tip_hw * 0.72), (outer_r, -tip_hw * 0.72), (root_r, -tip_hw),
        (root_r, -hw * 0.55), (web_r, -hw * 0.38), (hub_r, -hw * 0.65), (hub_r, -hw),
    ]
    return _save(name, LatheGeometry(profile, segments=n_segments).rotate_y(pi / 2.0))


def _drive_chain_sprocket(chassis, r: ResolvedGoKartConfig, mats) -> None:
    """Exposed chain-and-sprocket drivetrain (chaindrive L300-L430)."""
    _rear_axle_bar(chassis, r, mats)
    fz = r.frame_z
    sprocket_x = -0.25
    rear_sprocket_r, rear_sprocket_bore, rear_sprocket_w = 0.074, 0.019, 0.012
    engine_sprocket_r, engine_sprocket_bore, engine_sprocket_w = 0.026, 0.010, 0.009
    clutch_drum_r, clutch_drum_w, clutch_x = 0.040, 0.032, -0.20
    shaft_x_min, shaft_x_max = -0.18, -0.26
    ex, ey, ez = (-0.12, -0.54, max(0.22, fz + 0.135))
    crankshaft_z = max(0.19, fz + 0.105)
    engine_sprocket_y = -0.54
    rear_sprocket_y = REAR_AXLE_Y
    rear_sprocket_z = r.axle_z_rear

    chassis.visual(
        Box((0.22, 0.24, 0.04)),
        origin=Origin(xyz=(ex - 0.02, ey, fz)),
        material=mats["frame"],
        name="engine_mount_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"race_pink_red", "rental_charcoal", "offroad_green", "brass_drive"} else "metal.steel_bare"),
    )
    # Tie the engine mount plate back to the always-present rear_axle_bar so the
    # whole drivetrain cluster stays welded to the frame on EVERY Slot A form
    # (raised buggy / flat_deck have no rail at the plate's y/x, leaving the
    # cluster a floating island otherwise).
    for i, tx in enumerate((-0.06, -0.18)):
        _tube(
            f"engine_frame_tie_{i}.obj",
            [
                (tx, ey - 0.10, fz + 0.01),
                (tx, REAR_AXLE_Y, r.axle_z_rear),
            ],
            mats["frame"], chassis, radius=0.012, samples=6, radial=10,
        )
    for i, bx in enumerate((-0.06, -0.18)):
        bracket_h = max(0.02, ez - 0.07 - (fz + 0.02))
        chassis.visual(
            Box((0.03, 0.03, bracket_h)),
            origin=Origin(xyz=(bx, ey, (fz + 0.02 + ez - 0.07) * 0.5)),
            material=mats["frame"],
            name=f"engine_mount_bracket_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"race_pink_red", "rental_charcoal", "offroad_green", "brass_drive"} else "metal.steel_bare"),
        )
    chassis.visual(
        Box((0.13, 0.15, 0.14)),
        origin=Origin(xyz=(ex, ey, ez)),
        material=mats["engine"],
        name="engine_block", material_class_id="metal.aluminum_bare",
    )
    chassis.visual(
        Cylinder(radius=0.042, length=0.08),
        origin=Origin(xyz=(ex + 0.01, ey + 0.02, ez + 0.11)),
        material=mats["engine"],
        name="cylinder_barrel", material_class_id="metal.aluminum_bare",
    )
    for i in range(5):
        chassis.visual(
            Cylinder(radius=0.052, length=0.003),
            origin=Origin(xyz=(ex + 0.01, ey + 0.02, ez + 0.08 + i * 0.014)),
            material=mats["engine"],
            name=f"cooling_fin_{i}", material_class_id="metal.aluminum_bare",
        )
    chassis.visual(
        Cylinder(radius=0.046, length=0.022),
        origin=Origin(xyz=(ex + 0.01, ey + 0.02, ez + 0.15)),
        material=mats["engine"],
        name="cylinder_head", material_class_id="metal.aluminum_bare",
    )
    chassis.visual(
        Cylinder(radius=0.032, length=0.045),
        origin=Origin(xyz=(ex + 0.01, ey + 0.04, ez + 0.18)),
        material=mats["dark"],
        name="air_filter", material_class_id="plastic.opaque_generic",
    )
    exhaust_pts = [
        (ex + 0.01, ey - 0.01, ez + 0.08),
        (ex - 0.02, ey - 0.12, ez + 0.05),
        (ex - 0.06, ey - 0.26, ez + 0.025),
        (ex - 0.09, ey - 0.40, ez + 0.015),
    ]
    _tube("exhaust_pipe.obj", exhaust_pts, mats["dark"], chassis, radius=0.014, samples=10, radial=10)

    shaft_len = abs(shaft_x_max - shaft_x_min)
    shaft_cx = (shaft_x_min + shaft_x_max) * 0.5
    chassis.visual(
        Cylinder(radius=0.012, length=shaft_len),
        origin=Origin(xyz=(shaft_cx, engine_sprocket_y, crankshaft_z), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["dark"],
        name="output_shaft", material_class_id="metal.stainless_matte",
    )
    chassis.visual(
        Cylinder(radius=clutch_drum_r, length=clutch_drum_w),
        origin=Origin(xyz=(clutch_x, engine_sprocket_y, crankshaft_z), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["dark"],
        name="clutch_drum", material_class_id="metal.blackened_gunmetal",
    )
    chassis.visual(
        _sprocket_mesh("engine_sprocket.obj", engine_sprocket_r, engine_sprocket_bore, engine_sprocket_w),
        origin=Origin(xyz=(sprocket_x, engine_sprocket_y, crankshaft_z)),
        material=mats["drive"],
        name="engine_sprocket", material_class_id=("metal.steel_bare" if r.palette_style in {"race_pink_red", "rental_charcoal", "offroad_green", "bare_steel"} else "metal.brass_polished"),
    )
    chassis.visual(
        _sprocket_mesh("rear_sprocket.obj", rear_sprocket_r, rear_sprocket_bore, rear_sprocket_w),
        origin=Origin(xyz=(sprocket_x, rear_sprocket_y, rear_sprocket_z)),
        material=mats["drive"],
        name="rear_sprocket", material_class_id=("metal.steel_bare" if r.palette_style in {"race_pink_red", "rental_charcoal", "offroad_green", "bare_steel"} else "metal.brass_polished"),
    )
    chain_pts = _chain_loop_points(
        sprocket_x, rear_sprocket_y, rear_sprocket_z, rear_sprocket_r,
        engine_sprocket_y, crankshaft_z, engine_sprocket_r,
    )
    chain_tube = tube_from_spline_points(
        chain_pts, radius=0.005, samples_per_segment=6, radial_segments=8,
        closed_spline=False, cap_ends=False,
    )
    chassis.visual(_save("drive_chain.obj", chain_tube), material=mats["drive"], name="drive_chain", material_class_id=("metal.steel_bare" if r.palette_style in {"race_pink_red", "rental_charcoal", "offroad_green", "bare_steel"} else "metal.brass_polished"))


def _chain_loop_points(x, rcy, rcz, rear_r, ecy, ecz, eng_r):
    rr = rear_r * 0.93
    er = eng_r * 0.93
    dy = ecy - rcy
    dz = ecz - rcz
    base_ang = atan2(dz, dy)
    d = (dy * dy + dz * dz) ** 0.5
    delta = atan2(rr - er, d) if d > abs(rr - er) else 0.0
    u_ang = base_ang + pi / 2.0 + delta
    l_ang = base_ang - pi / 2.0 - delta
    pts = []
    n_arc = 16
    rear_sweep = u_ang - l_ang
    if rear_sweep < 0.0:
        rear_sweep += 2.0 * pi
    for i in range(n_arc + 1):
        t = i / n_arc
        ang = u_ang - t * rear_sweep
        pts.append((x, rcy + rr * cos(ang), rcz + rr * sin(ang)))
    pts.append((x, ecy + er * cos(u_ang), ecz + er * sin(u_ang)))
    eng_sweep = 2.0 * pi - rear_sweep
    for i in range(n_arc + 1):
        t = i / n_arc
        ang = u_ang + t * eng_sweep
        pts.append((x, ecy + er * cos(ang), ecz + er * sin(ang)))
    pts.append(pts[0])
    return pts


_DRIVE_BUILDERS = {
    "bare_axle": _drive_bare_axle,
    "side_engine_pod": _drive_side_engine_pod,
    "chain_sprocket_drive": _drive_chain_sprocket,
}


# --------------------------------------------------------------------------- #
# Slot B — seat_form (FIXED child part)
# --------------------------------------------------------------------------- #


def _build_seat(model, r: ResolvedGoKartConfig, mats):
    seat = model.part("seat")
    sbh = r.seat_back_height_scale
    if r.seat_form == "molded_bucket":
        seat.inertial = Inertial.from_geometry(Box((0.42, 0.46, 0.40)), mass=4.0, origin=Origin(xyz=(0.0, 0.0, 0.16)))
        seat_pan = superellipse_side_loft(
            [(0.20, 0.02, 0.07, 0.30), (0.02, 0.00, 0.06, 0.40), (-0.14, 0.01, 0.07, 0.36)],
            exponents=2.4, segments=40,
        )
        seat.visual(_save("seat_pan.obj", seat_pan), material=mats["seat"], name="seat_pan", material_class_id="fabric.upholstery_plain")
        bz = lambda v: v * sbh  # noqa: E731
        backrest = superellipse_side_loft(
            [(-0.14, 0.02, bz(0.34), 0.36), (-0.20, 0.02, bz(0.38), 0.34), (-0.25, 0.02, bz(0.32), 0.30)],
            exponents=2.6, segments=40,
        )
        seat.visual(_save("seat_back.obj", backrest), material=mats["seat"], name="seat_back", material_class_id="fabric.upholstery_plain")
        seat.visual(Box((0.04, 0.34, 0.14)), origin=Origin(xyz=(0.19, 0.0, 0.10)), material=mats["seat"], name="left_bolster", material_class_id="fabric.upholstery_plain")
        seat.visual(Box((0.04, 0.34, 0.14)), origin=Origin(xyz=(-0.19, 0.0, 0.10)), material=mats["seat"], name="right_bolster", material_class_id="fabric.upholstery_plain")
    elif r.seat_form == "flat_sling":
        seat.inertial = Inertial.from_geometry(Box((0.40, 0.44, 0.16)), mass=2.5, origin=Origin(xyz=(0.0, 0.0, 0.06)))
        seat_pan = superellipse_side_loft(
            [(0.18, 0.000, 0.022, 0.30), (0.02, 0.000, 0.018, 0.38), (-0.16, 0.000, 0.022, 0.34)],
            exponents=2.4, segments=40,
        )
        seat.visual(_save("seat_pan.obj", seat_pan), material=mats["seat"], name="seat_pan", material_class_id="fabric.canvas")
        bz = lambda v: v * sbh  # noqa: E731
        backrest = superellipse_side_loft(
            [(-0.15, 0.015, bz(0.13), 0.34), (-0.19, 0.010, bz(0.14), 0.32), (-0.22, 0.010, bz(0.12), 0.28)],
            exponents=2.6, segments=40,
        )
        seat.visual(_save("seat_back.obj", backrest), material=mats["seat"], name="seat_back", material_class_id="fabric.canvas")
    else:  # high_back_shell
        seat.inertial = Inertial.from_geometry(Box((0.46, 0.36, 0.68)), mass=5.2, origin=Origin(xyz=(0.0, -0.04, 0.34)))
        # full-wrap section-loft shell; z stations scaled by seat_back_height.
        shell_sections = [
            _seat_shell_section(0.00 * sbh, half_w=0.20, d_front=0.18, d_back=0.12, wing=0.00, y_off=0.03),
            _seat_shell_section(0.05 * sbh, half_w=0.19, d_front=0.14, d_back=0.10, wing=0.00, y_off=0.00),
            _seat_shell_section(0.11 * sbh, half_w=0.19, d_front=0.10, d_back=0.08, wing=0.00, y_off=-0.04),
            _seat_shell_section(0.20 * sbh, half_w=0.17, d_front=0.08, d_back=0.06, wing=0.00, y_off=-0.06),
            _seat_shell_section(0.32 * sbh, half_w=0.18, d_front=0.09, d_back=0.06, wing=0.04, y_off=-0.06),
            _seat_shell_section(0.44 * sbh, half_w=0.22, d_front=0.12, d_back=0.07, wing=0.10, y_off=-0.05),
            _seat_shell_section(0.54 * sbh, half_w=0.20, d_front=0.10, d_back=0.06, wing=0.06, y_off=-0.05),
            _seat_shell_section(0.64 * sbh, half_w=0.15, d_front=0.08, d_back=0.05, wing=0.02, y_off=-0.06),
        ]
        seat.visual(_save("seat_shell.obj", section_loft(shell_sections)), material=mats["seat"], name="seat_shell", material_class_id="plastic.opaque_glossy_molded")
        seat.visual(
            Box((0.14, 0.02, 0.44 * sbh)),
            origin=Origin(xyz=(0.0, -0.11, 0.30 * sbh)),
            material=mats["dark"],
            name="seat_padding", material_class_id="fabric.flexible_foam",
        )

    model.articulation(
        "seat_mount",
        ArticulationType.FIXED,
        parent=model.get_part("chassis"),
        child=seat,
        origin=Origin(xyz=(0.0, -0.06, r.frame_z + 0.05)),
    )
    return seat


def _seat_shell_section(z, half_w, d_front, d_back, wing, n=36, y_off=0.0):
    pts = []
    for i in range(n):
        theta = 2.0 * pi * i / n
        c, s = cos(theta), sin(theta)
        x = half_w * c
        if s >= 0.0:
            side = abs(c)
            y = (d_front + wing * side) * s + y_off
        else:
            y = d_back * s + y_off
        pts.append((x, y, z))
    return pts


# --------------------------------------------------------------------------- #
# Slot C — steering_wheel_form (CONTINUOUS child part)
# --------------------------------------------------------------------------- #


def _build_steering(model, r: ResolvedGoKartConfig, mats):
    steering = model.part("steering_wheel")
    tilt = r.column_tilt
    # The steering geometry is authored in a frame whose local Z = the tilted
    # column axis; spin axis = local −Z. Column shaft plugs DOWN (−Z) into the
    # chassis column_lower_mount sleeve.
    steering.visual(
        Cylinder(radius=0.015, length=0.20),
        origin=Origin(xyz=(0.0, 0.0, -0.10)),
        material=mats["dark"],
        name="steering_column", material_class_id="metal.blackened_gunmetal",
    )

    if r.steering_wheel_form == "round_3spoke":
        steering.inertial = Inertial.from_geometry(Box((0.24, 0.06, 0.24)), mass=0.8)
        ring_profile = [
            (0.105 - 0.014, -0.014), (0.105 + 0.014, -0.014),
            (0.105 + 0.014, 0.014), (0.105 - 0.014, 0.014), (0.105 - 0.014, -0.014),
        ]
        steering.visual(_save("steering_rim.obj", LatheGeometry(ring_profile, segments=48)), material=mats["dark"], name="steering_rim", material_class_id="plastic.opaque_glossy_molded")
        steering.visual(Cylinder(radius=0.026, length=0.03), material=mats["dark"], name="steering_hub", material_class_id="metal.blackened_gunmetal")
        for ang in (0.0, 2.0 * pi / 3.0, 4.0 * pi / 3.0):
            steering.visual(
                Box((0.10, 0.018, 0.012)),
                origin=Origin(xyz=(0.05 * cos(ang), 0.05 * sin(ang), 0.0), rpy=(0.0, 0.0, ang)),
                material=mats["dark"],
                name=f"steering_spoke_{int(round(ang * 100))}", material_class_id="metal.blackened_gunmetal",
            )
        steering.visual(
            Box((0.02, 0.02, 0.04)),
            origin=Origin(xyz=(0.0, 0.105, 0.0)),
            material=mats["marker"],
            name="steering_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    elif r.steering_wheel_form == "butterfly_open":
        steering.inertial = Inertial.from_geometry(Box((0.24, 0.06, 0.24)), mass=0.8)
        rim_r = 0.105
        by = -rim_r * 0.5
        rim_path = []
        for deg in (30, 20, 10, 0, -10, -20, -30):
            a = deg * pi / 180.0
            rim_path.append((rim_r * cos(a), rim_r * sin(a), 0.0))
        rim_path.append((0.045, by, 0.0))
        rim_path.append((0.0, by, 0.0))
        rim_path.append((-0.045, by, 0.0))
        for deg in (-150, -160, -170, -180, -190, -200, -210):
            a = deg * pi / 180.0
            rim_path.append((rim_r * cos(a), rim_r * sin(a), 0.0))
        steering.visual(
            _save("butterfly_rim.obj", tube_from_spline_points(rim_path, radius=0.016, samples_per_segment=10, radial_segments=14)),
            material=mats["dark"],
            name="butterfly_rim", material_class_id="plastic.opaque_glossy_molded",
        )
        steering.visual(Cylinder(radius=0.026, length=0.03), material=mats["dark"], name="steering_hub", material_class_id="metal.blackened_gunmetal")
        spoke_len = rim_r - 0.026
        for i in range(2):
            sign = 1.0 if i == 0 else -1.0
            steering.visual(
                Box((spoke_len, 0.018, 0.012)),
                origin=Origin(xyz=(sign * (0.026 + spoke_len * 0.5), 0.0, 0.0)),
                material=mats["dark"],
                name=f"spoke_{i}", material_class_id="metal.blackened_gunmetal",
            )
        steering.visual(
            Box((0.02, 0.02, 0.04)),
            origin=Origin(xyz=(0.0, by, 0.025)),
            material=mats["marker"],
            name="steering_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    else:  # quick_release_hub
        steering.inertial = Inertial.from_geometry(Box((0.24, 0.12, 0.24)), mass=1.1, origin=Origin(xyz=(0.0, 0.0, 0.03)))
        boss_h = r.qr_boss_height
        # stacked boss: base collar + spline body (height scaled) + top flange.
        body_len = _clamp(boss_h * 0.5, 0.02, 0.05)
        steering.visual(Cylinder(radius=0.030, length=0.014), origin=Origin(xyz=(0.0, 0.0, 0.007)), material=mats["dark"], name="qr_base_collar", material_class_id="metal.blackened_gunmetal")
        steering.visual(Cylinder(radius=0.024, length=body_len), origin=Origin(xyz=(0.0, 0.0, 0.014 + body_len * 0.5)), material=mats["dark"], name="qr_spline_body", material_class_id="metal.blackened_gunmetal")
        flange_z = 0.014 + body_len + 0.005
        steering.visual(Cylinder(radius=0.034, length=0.010), origin=Origin(xyz=(0.0, 0.0, flange_z)), material=mats["dark"], name="qr_top_flange", material_class_id="metal.blackened_gunmetal")
        rim_r = 0.105
        tube_r = 0.014
        flat_y = 0.065
        wheel_z = flange_z + 0.007
        torus_geom = TorusGeometry(rim_r, tube_r, radial_segments=20, tubular_segments=56)
        flat_thresh = -flat_y
        flat_verts = [(x, max(y, flat_thresh) if y < flat_thresh else y, z) for x, y, z in torus_geom.vertices]
        flat_rim_geom = MeshGeometry(vertices=flat_verts, faces=list(torus_geom.faces))
        steering.visual(_save("steering_rim.obj", flat_rim_geom), origin=Origin(xyz=(0.0, 0.0, wheel_z)), material=mats["dark"], name="steering_rim", material_class_id="plastic.opaque_glossy_molded")
        hub_r = 0.028
        spoke_defs = [
            ("upper_left", 2.0 * pi / 3.0, rim_r - hub_r),
            ("upper_right", pi / 3.0, rim_r - hub_r),
            ("bottom", -pi / 2.0, flat_y - hub_r),
        ]
        for nm, ang, spoke_len in spoke_defs:
            mid_r = hub_r + spoke_len * 0.5
            steering.visual(
                Box((spoke_len, 0.016, 0.012)),
                origin=Origin(xyz=(mid_r * cos(ang), mid_r * sin(ang), wheel_z), rpy=(0.0, 0.0, ang)),
                material=mats["dark"],
                name=f"steering_spoke_{nm}", material_class_id="metal.blackened_gunmetal",
            )
        steering.visual(Cylinder(radius=hub_r, length=0.018), origin=Origin(xyz=(0.0, 0.0, wheel_z)), material=mats["dark"], name="steering_hub", material_class_id="metal.blackened_gunmetal")
        flat_bar_half_width = (rim_r ** 2 - flat_y ** 2) ** 0.5
        steering.visual(
            Box((flat_bar_half_width * 1.7, 0.016, 0.012)),
            origin=Origin(xyz=(0.0, -flat_y, wheel_z)),
            material=mats["dark"],
            name="steering_flat_bar", material_class_id="metal.blackened_gunmetal",
        )
        steering.visual(
            Box((0.02, 0.02, 0.04)),
            origin=Origin(xyz=(0.0, rim_r, wheel_z)),
            material=mats["marker"],
            name="steering_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )

    jo_y, jo_z = _column_point(r, _COLUMN_JOINT_PARAM)
    col_top = (0.0, jo_y, jo_z)
    model.articulation(
        "steering_spin",
        ArticulationType.CONTINUOUS,
        parent=model.get_part("chassis"),
        child=steering,
        origin=Origin(xyz=col_top, rpy=(tilt, 0.0, 0.0)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=8.0),
    )
    return steering


# --------------------------------------------------------------------------- #
# Knuckles + wheels (shared, identical across all variants)
# --------------------------------------------------------------------------- #


def _build_knuckle(model, name: str, sign: float, mats):
    part = model.part(name)
    part.inertial = Inertial.from_geometry(Box((0.10, 0.10, 0.16)), mass=1.2)
    part.visual(Box((0.05, 0.05, 0.14)), material=mats["dark"], name="knuckle_upright", material_class_id="metal.cast_iron_bare")
    part.visual(
        Box((0.10, 0.04, 0.03)),
        origin=Origin(xyz=(-0.05 * sign, -0.04, 0.02)),
        material=mats["dark"],
        name="knuckle_arm", material_class_id="metal.cast_iron_bare",
    )
    return part


def _build_wheel(model, name: str, prefix: str, tire_r, tire_w, mats):
    w = model.part(name)
    w.inertial = Inertial.from_geometry(
        Cylinder(radius=tire_r, length=tire_w), mass=4.0, origin=Origin(rpy=(0.0, pi / 2.0, 0.0))
    )
    _wheel_visuals(w, prefix, tire_r, tire_w, mats)
    return w


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def build_go_kart(
    config: GoKartConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    mats: dict[str, object] = {}
    for token, rgba in PALETTES[r.palette_style].items():
        mats[token] = model.material(token, rgba=rgba)

    # ------------------------------------------------------------- chassis (root)
    chassis = model.part("chassis")
    chassis.inertial = Inertial.from_geometry(
        Box((1.00, 1.70, 0.40)), mass=85.0, origin=Origin(xyz=(0.0, -0.05, max(0.18, r.frame_z + 0.1)))
    )
    _FRAME_BUILDERS[r.frame_chassis_form](chassis, r, mats)
    _add_common_frame_anchors(chassis, r, mats)
    _add_cross_tubes(chassis, r, mats)
    _DRIVE_BUILDERS[r.rear_drive_form](chassis, r, mats)

    # ------------------------------------------------------------------ seat
    _build_seat(model, r, mats)

    # -------------------------------------------------------- steering wheel
    _build_steering(model, r, mats)

    # ------------------------------------------------------ knuckles + wheels
    knuckle_fl = _build_knuckle(model, "front_left_knuckle", 1.0, mats)
    knuckle_fr = _build_knuckle(model, "front_right_knuckle", -1.0, mats)

    fl_wheel = _build_wheel(model, "front_left_wheel", "fl_wheel", r.front_tire_r, r.front_tire_w, mats)
    fr_wheel = _build_wheel(model, "front_right_wheel", "fr_wheel", r.front_tire_r, r.front_tire_w, mats)
    rl_wheel = _build_wheel(model, "rear_left_wheel", "rl_wheel", r.rear_tire_r, r.rear_tire_w, mats)
    rr_wheel = _build_wheel(model, "rear_right_wheel", "rr_wheel", r.rear_tire_r, r.rear_tire_w, mats)

    # Front knuckle steer joints (vertical king-pin Z, ±0.52).
    model.articulation(
        "front_left_steer", ArticulationType.REVOLUTE, parent=chassis, child=knuckle_fl,
        origin=Origin(xyz=(r.front_track_x, FRONT_AXLE_Y, r.axle_z_front)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=15.0, velocity=2.0, lower=-STEER_LOCK, upper=STEER_LOCK),
    )
    model.articulation(
        "front_right_steer", ArticulationType.REVOLUTE, parent=chassis, child=knuckle_fr,
        origin=Origin(xyz=(-r.front_track_x, FRONT_AXLE_Y, r.axle_z_front)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=15.0, velocity=2.0, lower=-STEER_LOCK, upper=STEER_LOCK),
    )
    # Front wheels roll about local X off their knuckle (origin 0).
    model.articulation(
        "front_left_roll", ArticulationType.CONTINUOUS, parent=knuckle_fl, child=fl_wheel,
        origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=30.0),
    )
    model.articulation(
        "front_right_roll", ArticulationType.CONTINUOUS, parent=knuckle_fr, child=fr_wheel,
        origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=30.0),
    )
    # Rear wheels roll about local X off the chassis.
    model.articulation(
        "rear_left_roll", ArticulationType.CONTINUOUS, parent=chassis, child=rl_wheel,
        origin=Origin(xyz=(r.rear_track_x, REAR_AXLE_Y, r.axle_z_rear)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=30.0),
    )
    model.articulation(
        "rear_right_roll", ArticulationType.CONTINUOUS, parent=chassis, child=rr_wheel,
        origin=Origin(xyz=(-r.rear_track_x, REAR_AXLE_Y, r.axle_z_rear)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=30.0),
    )

    return model


def build_seeded_go_kart(seed: int) -> ArticulatedObject:
    return build_go_kart(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Author tests
# --------------------------------------------------------------------------- #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_go_kart_tests(model: ArticulatedObject, config: GoKartConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    chassis = model.get_part("chassis")
    seat = model.get_part("seat")
    steering = model.get_part("steering_wheel")
    fl_knuckle = model.get_part("front_left_knuckle")
    fr_knuckle = model.get_part("front_right_knuckle")
    fl_wheel = model.get_part("front_left_wheel")
    fr_wheel = model.get_part("front_right_wheel")
    rl_wheel = model.get_part("rear_left_wheel")
    rr_wheel = model.get_part("rear_right_wheel")

    steering_spin = model.get_articulation("steering_spin")
    fl_steer = model.get_articulation("front_left_steer")
    fr_steer = model.get_articulation("front_right_steer")
    fl_roll = model.get_articulation("front_left_roll")
    fr_roll = model.get_articulation("front_right_roll")
    rl_roll = model.get_articulation("rear_left_roll")
    rr_roll = model.get_articulation("rear_right_roll")

    # ---- Intentional mounting overlaps -------------------------------------
    ctx.allow_overlap(fl_knuckle, fl_wheel, reason="Front-left wheel hub/axle captured on the knuckle stub axle.")
    ctx.allow_overlap(fr_knuckle, fr_wheel, reason="Front-right wheel hub/axle captured on the knuckle stub axle.")
    for w in (fl_wheel, fr_wheel, rl_wheel, rr_wheel):
        ctx.allow_overlap(chassis, w, reason="Wheel hub/axle passes through the chassis axle line / frame tube at its mount.")
    ctx.allow_overlap(chassis, fl_knuckle, reason="Front-left knuckle straddles the front cross tube at its kingpin mount.")
    ctx.allow_overlap(chassis, fr_knuckle, reason="Front-right knuckle straddles the front cross tube at its kingpin mount.")
    ctx.allow_overlap(
        chassis, steering, elem_a="column_lower_mount", elem_b="steering_column",
        reason="Steering shaft is intentionally inserted into the column lower-mount sleeve.",
    )
    # Seat seats onto the seat_tray / deck / shroud tub; thin embed intentional.
    ctx.allow_overlap(chassis, seat, reason="Seat seats flush on the chassis seat tray / deck / shroud tub.")

    # ---- Baseline gates ----------------------------------------------------
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.02)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Category identity: chassis form present ---------------------------
    vis_names = {v.name for v in chassis.visuals}
    form_markers = {
        "open_tubular": "left_main_rail",
        "bodywork_shroud": "bodywork_shell",
        "flat_deck": "deck_pan",
        "offroad_buggy": "roll_cage_hoop",
    }
    ctx.check(
        f"{r.frame_chassis_form} chassis form present",
        form_markers[r.frame_chassis_form] in vis_names,
        details=f"chassis visuals sample={sorted(vis_names)[:6]}",
    )

    # ---- cross_tube ladder: naming + count + flat_deck gating --------------
    ct_names = sorted(n for n in vis_names if n.startswith("cross_tube_"))
    if r.frame_chassis_form == "flat_deck":
        ctx.check("flat_deck emits NO cross-tube ladder", len(ct_names) == 0, details=f"ct={ct_names}")
    else:
        ctx.check(
            "cross_tube ladder count + naming",
            len(ct_names) == r.cross_tube_count
            and CROSS_TUBE_MIN <= r.cross_tube_count <= CROSS_TUBE_MAX
            and ct_names == [f"cross_tube_{i}" for i in range(r.cross_tube_count)],
            details=f"n={r.cross_tube_count}, names={ct_names}",
        )

    # ---- All four wheels rest on the ground (z≈0) --------------------------
    for nm, w in (("FL", fl_wheel), ("FR", fr_wheel), ("RL", rl_wheel), ("RR", rr_wheel)):
        mn, _ = ctx.part_world_aabb(w)
        ctx.check(f"{nm} wheel sits on the ground", mn[2] <= 0.03, details=f"{nm} wheel min z={mn[2]:.4f}")

    # ---- rear wheels larger AND wider than front ---------------------------
    fl_ext = _ext(ctx.part_world_aabb(fl_wheel))
    rl_ext = _ext(ctx.part_world_aabb(rl_wheel))
    ctx.check("rear tire is larger diameter than front", rl_ext[2] > fl_ext[2] + 0.01,
              details=f"front dia(z)={fl_ext[2]:.3f}, rear dia(z)={rl_ext[2]:.3f}")
    ctx.check("rear tire is wider than front", rl_ext[0] > fl_ext[0] + 0.02,
              details=f"front width(x)={fl_ext[0]:.3f}, rear width(x)={rl_ext[0]:.3f}")

    # ---- steering wheel spins about its angled column ----------------------
    rest = ctx.part_element_world_aabb(steering, elem="steering_marker")
    rmid = [(rest[0][i] + rest[1][i]) * 0.5 for i in range(3)]
    with ctx.pose({steering_spin: pi}):
        half = ctx.part_element_world_aabb(steering, elem="steering_marker")
        hmid = [(half[0][i] + half[1][i]) * 0.5 for i in range(3)]
    moved = max(abs(hmid[i] - rmid[i]) for i in range(3))
    ctx.check("steering wheel marker moves when column spins", moved > 0.05,
              details=f"moved={moved:.4f}")
    ctx.check(
        "steering spin axis is column axis (local -Z) + continuous",
        tuple(steering_spin.axis) == (0.0, 0.0, -1.0)
        and steering_spin.articulation_type == ArticulationType.CONTINUOUS,
        details=f"axis={steering_spin.axis}, type={steering_spin.articulation_type}",
    )
    ctx.expect_overlap(
        steering, chassis, axes="z",
        elem_a="steering_column", elem_b="column_lower_mount",
        min_overlap=0.02, name="steering shaft seated in column mount",
    )

    # ---- front knuckles steer (REVOLUTE about Z, ±0.52) --------------------
    for nm, wheel, steer in (("front_left", fl_wheel, fl_steer), ("front_right", fr_wheel, fr_steer)):
        ax = tuple(steer.axis)
        ml = steer.motion_limits
        ctx.check(
            f"{nm} steer axis vertical Z REVOLUTE ±0.52",
            abs(ax[2]) > 0.9 and abs(ax[0]) < 1e-6 and abs(ax[1]) < 1e-6
            and steer.articulation_type == ArticulationType.REVOLUTE
            and ml is not None and abs(abs(ml.lower) - STEER_LOCK) < 1e-6 and abs(ml.upper - STEER_LOCK) < 1e-6,
            details=f"axis={ax}, limits=({ml.lower if ml else None},{ml.upper if ml else None})",
        )
        straight = _ext(ctx.part_world_aabb(wheel))
        with ctx.pose({steer: 0.5}):
            turned = _ext(ctx.part_world_aabb(wheel))
        ctx.check(f"{nm} knuckle steers the wheel (heading changes)", turned[1] > straight[1] + 0.02,
                  details=f"{nm} straight Y-ext={straight[1]:.3f}, steered Y-ext={turned[1]:.3f}")

    # ---- all four wheels roll about their axles ----------------------------
    def marker_swing(wheel, prefix, roll_joint):
        elem = f"{prefix}_marker"
        rest_a = ctx.part_element_world_aabb(wheel, elem=elem)
        rmid_ = [(rest_a[0][i] + rest_a[1][i]) * 0.5 for i in range(3)]
        with ctx.pose({roll_joint: pi}):
            roll_a = ctx.part_element_world_aabb(wheel, elem=elem)
            rmid2_ = [(roll_a[0][i] + roll_a[1][i]) * 0.5 for i in range(3)]
        return max(abs(rmid2_[1] - rmid_[1]), abs(rmid2_[2] - rmid_[2]))

    for nm, wheel, prefix, roll in (
        ("front_left", fl_wheel, "fl_wheel", fl_roll),
        ("front_right", fr_wheel, "fr_wheel", fr_roll),
        ("rear_left", rl_wheel, "rl_wheel", rl_roll),
        ("rear_right", rr_wheel, "rr_wheel", rr_roll),
    ):
        j = model.get_articulation(f"{nm}_roll")
        ctx.check(
            f"{nm} roll axis lateral X + continuous",
            tuple(j.axis) == (1.0, 0.0, 0.0) and j.articulation_type == ArticulationType.CONTINUOUS,
            details=f"axis={j.axis}, type={j.articulation_type}",
        )
        swing = marker_swing(wheel, prefix, roll)
        ctx.check(f"{nm} wheel rolls about its axle", swing > 0.05, details=f"{nm} marker swing={swing:.4f}")

    # ---- seat mounted centrally + FIXED + contacts chassis -----------------
    sp = ctx.part_world_position(seat)
    ctx.check(
        "seat mounted near kart center",
        sp is not None and abs(sp[0]) < 0.05 and -0.3 < sp[1] < 0.2,
        details=f"seat origin={sp}",
    )
    seat_mount = model.get_articulation("seat_mount")
    ctx.check("seat FIXED to chassis", seat_mount.articulation_type == ArticulationType.FIXED)
    ctx.expect_contact(seat, chassis, name="seat attached to chassis")

    # ---- front wheels carried by their knuckles (no floating) --------------
    ctx.expect_contact(fl_wheel, fl_knuckle, name="front-left wheel on its knuckle")
    ctx.expect_contact(fr_wheel, fr_knuckle, name="front-right wheel on its knuckle")

    # ---- palette diversity sanity ------------------------------------------
    matset = {m.name: m for m in model.materials}
    if "body" in matset and "rubber" in matset:
        ctx.check(
            "tire rubber darker than body",
            sum(matset["rubber"].rgba[:3]) <= sum(matset["body"].rgba[:3]) + 0.1,
            details=f"body={matset['body'].rgba}, rubber={matset['rubber'].rgba}",
        )

    return ctx.report()


__all__ = [
    "FrameChassisForm",
    "SeatForm",
    "SteeringWheelForm",
    "RearDriveForm",
    "PaletteStyle",
    "GoKartConfig",
    "ResolvedGoKartConfig",
    "config_from_seed",
    "resolve_config",
    "build_go_kart",
    "build_seeded_go_kart",
    "slot_choices_for_seed",
    "run_go_kart_tests",
    "__modular__",
]
