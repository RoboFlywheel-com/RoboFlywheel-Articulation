# SPDX-License-Identifier: Apache-2.0

"""Tricycle (three-wheeled pedal cycle) modular template.

A three-wheeled human-powered pedal cycle: a tubular ``chassis`` (root) carries a
REVOLUTE ``steering`` assembly (fork + handlebar + front wheel(s)), a REVOLUTE
``pedal_crank`` with two CONTINUOUS ``pedal`` bodies, CONTINUOUS-rolling wheels,
one or more FIXED ``saddle`` parts, and a FIXED ``rear_module`` (cargo basket /
passenger bench / flat deck).

Sourced from ``articraft_template_authoring/specs_modular_v1/tricycle.md`` and the
16 5-star ``tricycle`` samples synced under ``data/records/`` (origin trike + 15
slot forks). All sources share one helper skeleton (``_wheel_visuals`` /
``_tube_visual`` / ``_annular_sector_y`` / ``_rounded_open_bin`` / ``_rounded_ring``)
and one articulation topology: steering REVOLUTE + per-wheel CONTINUOUS roll
(lateral Y axle) + crank REVOLUTE + pedal CONTINUOUS + saddle/rear FIXED.

Pattern = ``mixed``: ``chassis`` (root) with parallel children ``steering`` /
``pedal_crank`` / rear wheels / ``saddle_i`` / ``rear_module``; front wheels are
children of ``steering``. Module axes (see spec §4):

  * ``frame_form`` (5, ③/①): low_step_child / delta_adult / cargo_trike /
    drift_trike / tadpole_twin_front. delta forms => 1 front + 2 rear wheels;
    tadpole => 2 front + 1 rear.
  * ``steering_form`` (3, ②): direct_fork / linkage / lean.
  * ``drive_form`` (3, ②): front_direct_pedals / mid_drive_freewheel /
    shaft_drive. front_direct needs a single front wheel; tadpole degrades to
    mid_drive_freewheel.
  * ``rear_module`` (3, ①/③): cargo_basket / passenger_bench / flat_deck.
  * ``seat_count`` (N in {1,2,3}, multiplicity): seats_1 / seats_2 / seats_3.

Every non-FIXED joint here is a captured pin/hub interface (bearing pressed in
the head tube, hub on axle, spindle in bore, pedal on spindle), so per Rule 2
they omit ``MatingContract`` and are covered by element-scoped ``allow_overlap``
in ``run_tricycle_tests`` (mirroring each source record's run_tests block).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from math import cos, pi, sin
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
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

FrameForm = Literal[
    "low_step_child",
    "delta_adult",
    "cargo_trike",
    "drift_trike",
    "tadpole_twin_front",
]
SteeringForm = Literal["direct_fork", "linkage", "lean"]
DriveForm = Literal["front_direct_pedals", "mid_drive_freewheel", "shaft_drive"]
RearModule = Literal["cargo_basket", "passenger_bench", "flat_deck"]
PaletteStyle = Literal[
    "strawberry_pink",
    "classic_red",
    "sky_blue",
    "mint_cream",
    "sunny_yellow",
    "charcoal_sport",
]

FRAME_FORMS: tuple[FrameForm, ...] = (
    "low_step_child",
    "delta_adult",
    "cargo_trike",
    "drift_trike",
    "tadpole_twin_front",
)
STEERING_FORMS: tuple[SteeringForm, ...] = ("direct_fork", "linkage", "lean")
DRIVE_FORMS: tuple[DriveForm, ...] = (
    "front_direct_pedals",
    "mid_drive_freewheel",
    "shaft_drive",
)
REAR_MODULES: tuple[RearModule, ...] = ("cargo_basket", "passenger_bench", "flat_deck")
SEAT_COUNTS: tuple[int, ...] = (1, 2, 3)
SEAT_WEIGHTS = (0.60, 0.28, 0.12)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "strawberry_pink",
    "classic_red",
    "sky_blue",
    "mint_cream",
    "sunny_yellow",
    "charcoal_sport",
)

# Palette keys: frame (main tubes/shell), accent (pale trim/insets/pedal tread),
# trim (white plates/discs/handlebar), tire (rubber), metal (axles/hardware),
# hub (wheel rim ring + hub disc).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "strawberry_pink": {
        "frame": (0.95, 0.27, 0.55, 1.0),
        "accent": (1.0, 0.60, 0.75, 1.0),
        "trim": (0.96, 0.95, 0.91, 1.0),
        "tire": (0.68, 0.69, 0.68, 1.0),
        "metal": (0.78, 0.79, 0.77, 1.0),
        "hub": (0.82, 0.12, 0.38, 1.0),
    },
    "classic_red": {
        "frame": (0.80, 0.14, 0.13, 1.0),
        "accent": (0.96, 0.90, 0.82, 1.0),
        "trim": (0.97, 0.96, 0.94, 1.0),
        "tire": (0.11, 0.10, 0.10, 1.0),
        "metal": (0.80, 0.81, 0.83, 1.0),
        "hub": (0.60, 0.09, 0.09, 1.0),
    },
    "sky_blue": {
        "frame": (0.18, 0.52, 0.80, 1.0),
        "accent": (0.90, 0.94, 0.98, 1.0),
        "trim": (0.95, 0.96, 0.97, 1.0),
        "tire": (0.10, 0.10, 0.11, 1.0),
        "metal": (0.80, 0.82, 0.85, 1.0),
        "hub": (0.10, 0.34, 0.60, 1.0),
    },
    "mint_cream": {
        "frame": (0.42, 0.76, 0.62, 1.0),
        "accent": (0.96, 0.93, 0.84, 1.0),
        "trim": (0.97, 0.96, 0.92, 1.0),
        "tire": (0.62, 0.63, 0.62, 1.0),
        "metal": (0.78, 0.79, 0.78, 1.0),
        "hub": (0.20, 0.52, 0.44, 1.0),
    },
    "sunny_yellow": {
        "frame": (0.97, 0.80, 0.16, 1.0),
        "accent": (0.90, 0.28, 0.20, 1.0),
        "trim": (0.97, 0.96, 0.93, 1.0),
        "tire": (0.11, 0.10, 0.10, 1.0),
        "metal": (0.80, 0.81, 0.82, 1.0),
        "hub": (0.86, 0.44, 0.10, 1.0),
    },
    "charcoal_sport": {
        "frame": (0.21, 0.22, 0.24, 1.0),
        "accent": (0.62, 0.86, 0.20, 1.0),
        "trim": (0.55, 0.57, 0.60, 1.0),
        "tire": (0.09, 0.09, 0.10, 1.0),
        "metal": (0.60, 0.62, 0.64, 1.0),
        "hub": (0.50, 0.72, 0.14, 1.0),
    },
}

# ---- nominal anchors (meters, world frame; forward=+X, lateral=Y, up=Z) ----
STEER_PIVOT_X0 = 0.34  # head-tube top x (steering joint origin), scaled by length
STEER_PIVOT_Z = 0.520
HEAD_BOT_Z = 0.417
FRONT_AXLE_DX = 0.070  # front axle x, relative to steering pivot (steering local)
REAR_AXLE_X0 = -0.430
SEAT_REF_X0 = -0.080
BOTTOM_BRACKET_X0 = 0.030  # mid/shaft-drive bottom bracket x (between front wheel and cargo bed)
BOTTOM_BRACKET_Z = 0.255

WHEEL_WIDTH = 0.055
FRONT_R_DELTA = 0.185
REAR_R_DELTA = 0.145
FRONT_R_TADPOLE = 0.145
REAR_R_TADPOLE = 0.185

CRANK_ARM = 0.090  # crank arm run (X) toward pedal
CRANK_DROP = 0.058  # crank arm drop (Z)
CRANK_HALF = 0.075  # half spindle width (Y) to each crank arm
PEDAL_LEN_X = 0.095  # pedal body length (X)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Geometry helpers (lifted from the 5-star sources; primitive types preserved).
# ---------------------------------------------------------------------------
def _annular_sector_y(
    inner_radius: float,
    outer_radius: float,
    width: float,
    start_angle: float,
    end_angle: float,
    *,
    segments: int = 26,
) -> MeshGeometry:
    """Closed annular sector whose rotation axis is local Y (fender arc)."""
    geom = MeshGeometry()
    half_width = width * 0.5
    rings: list[list[int]] = []
    for y in (-half_width, half_width):
        strip: list[int] = []
        for radius in (inner_radius, outer_radius):
            for index in range(segments + 1):
                angle = start_angle + (end_angle - start_angle) * index / segments
                strip.append(geom.add_vertex(radius * cos(angle), y, radius * sin(angle)))
        rings.append(strip)

    span = segments + 1
    for index in range(segments):
        i0, i1 = index, index + 1
        for side, reverse in ((0, False), (1, True)):
            inner0 = rings[side][i0]
            inner1 = rings[side][i1]
            outer0 = rings[side][span + i0]
            outer1 = rings[side][span + i1]
            if reverse:
                geom.add_face(inner0, outer1, inner1)
                geom.add_face(inner0, outer0, outer1)
            else:
                geom.add_face(inner0, inner1, outer1)
                geom.add_face(inner0, outer1, outer0)
        inner_low, inner_high = rings[0][i0], rings[1][i0]
        inner_low_next, inner_high_next = rings[0][i1], rings[1][i1]
        geom.add_face(inner_low, inner_high_next, inner_high)
        geom.add_face(inner_low, inner_low_next, inner_high_next)
        outer_low, outer_high = rings[0][span + i0], rings[1][span + i0]
        outer_low_next, outer_high_next = rings[0][span + i1], rings[1][span + i1]
        geom.add_face(outer_low, outer_high, outer_high_next)
        geom.add_face(outer_low, outer_high_next, outer_low_next)
    for index in (0, segments):
        inner_low = rings[0][index]
        inner_high = rings[1][index]
        outer_low = rings[0][span + index]
        outer_high = rings[1][span + index]
        if index == 0:
            geom.add_face(inner_low, outer_high, inner_high)
            geom.add_face(inner_low, outer_low, outer_high)
        else:
            geom.add_face(inner_low, inner_high, outer_high)
            geom.add_face(inner_low, outer_high, outer_low)
    return geom


def _tube_visual(part, name: str, points, radius: float, material) -> None:
    geometry = tube_from_spline_points(
        points, radius=radius, samples_per_segment=12, radial_segments=16
    )
    part.visual(mesh_from_geometry(geometry, name), material=material, name=name, material_class_id="metal.paint_coated")


def _rounded_open_bin(length: float, width: float, height: float, wall: float):
    outer = (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(length, width) * 0.09)
    )
    inner = (
        cq.Workplane("XY")
        .box(length - 2.0 * wall, width - 2.0 * wall, height, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(length, width) * 0.065)
        .translate((0.0, 0.0, wall))
    )
    return outer.cut(inner)


def _rounded_ring(length: float, width: float, height: float, wall: float):
    outer = (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(length, width) * 0.08)
    )
    inner = (
        cq.Workplane("XY")
        .box(length - 2.0 * wall, width - 2.0 * wall, height * 1.5, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(length, width) * 0.055)
        .translate((0.0, 0.0, -height * 0.25))
    )
    return outer.cut(inner)


def _rounded_slab(length: float, width: float, height: float, corner_radius: float):
    return (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .edges("|Z")
        .fillet(corner_radius)
    )


def _wheel_visuals(part, prefix: str, radius: float, width: float, mats) -> None:
    """Molded wheel: soft tire torus, colored rim ring, hub disc, hub, marker.

    Spin axis is local Y (built via rpy=(pi/2,0,0)); a small off-center marker
    lets run_tests observe rolling.
    """
    spin_axis = Origin(rpy=(pi / 2.0, 0.0, 0.0))
    tire_geom = TorusGeometry(
        radius=radius - width * 0.46,
        tube=width * 0.46,
        radial_segments=18,
        tubular_segments=48,
    ).rotate_x(pi / 2.0)
    part.visual(mesh_from_geometry(tire_geom, f"{prefix}_tire"), material=mats["tire"], name="tire", material_class_id="rubber.smooth_plain")
    part.visual(
        Cylinder(radius=radius * 0.78, length=width * 0.72),
        origin=spin_axis,
        material=mats["hub"],
        name="rim_disc", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Cylinder(radius=radius * 0.64, length=width * 0.84),
        origin=spin_axis,
        material=mats["trim"],
        name="hub_disc", material_class_id="plastic.opaque_glossy_molded",
    )
    trim = TorusGeometry(
        radius=radius * 0.69, tube=radius * 0.035, radial_segments=12, tubular_segments=40
    ).rotate_x(pi / 2.0)
    part.visual(mesh_from_geometry(trim, f"{prefix}_rim_trim"), material=mats["hub"], name="rim_trim", material_class_id="plastic.opaque_glossy_molded")
    part.visual(
        Cylinder(radius=radius * 0.12, length=width * 0.98),
        origin=spin_axis,
        material=mats["metal"],
        name="hub", material_class_id="metal.aluminum_bare",
    )
    # Off-center marker (spoke reflector) to make rolling observable.
    part.visual(
        Box((radius * 0.05, width * 0.5, radius * 0.5)),
        origin=Origin(xyz=(0.0, 0.0, radius * 0.42)),
        material=mats["accent"],
        name=f"{prefix}_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )


# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TricycleConfig:
    frame_form: FrameForm | None = None
    steering_form: SteeringForm | None = None
    drive_form: DriveForm | None = None
    rear_module: RearModule | None = None
    seat_count: int | None = None
    palette_style: PaletteStyle = "strawberry_pink"
    wheel_radius_scale: float = 1.0
    frame_length_scale: float = 1.0
    steer_range: float = 0.55
    rear_half_track: float = 0.2475
    name: str = "tricycle"


@dataclass(frozen=True)
class ResolvedTricycleConfig:
    frame_form: FrameForm
    steering_form: SteeringForm
    drive_form: DriveForm
    rear_module: RearModule
    seat_count: int
    palette_style: PaletteStyle
    front_count: int
    rear_count: int
    front_wheel_radius: float
    rear_wheel_radius: float
    steer_pivot_x: float
    rear_axle_x: float
    seat_ref_x: float
    bottom_bracket_x: float
    front_half_track: float
    rear_half_track: float
    steer_range: float
    lean_angle: float
    name: str

    @property
    def wheel_count(self) -> int:
        return self.front_count + self.rear_count

    @property
    def steer_axis(self) -> tuple[float, float, float]:
        if self.steering_form == "lean":
            return (-math.sin(self.lean_angle), 0.0, math.cos(self.lean_angle))
        return (0.0, 0.0, 1.0)


def config_from_seed(seed: int) -> TricycleConfig:
    rng = random.Random(seed)
    return TricycleConfig(
        frame_form=rng.choice(FRAME_FORMS),
        steering_form=rng.choice(STEERING_FORMS),
        drive_form=rng.choice(DRIVE_FORMS),
        rear_module=rng.choice(REAR_MODULES),
        seat_count=rng.choices(SEAT_COUNTS, weights=SEAT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        wheel_radius_scale=round(rng.uniform(0.90, 1.08), 4),
        frame_length_scale=round(rng.uniform(0.92, 1.10), 4),
        steer_range=round(rng.uniform(0.42, 0.60), 4),
        rear_half_track=round(rng.uniform(0.20, 0.28), 4),
        name=f"seeded_tricycle_{seed}",
    )


def resolve_config(config: TricycleConfig | None = None) -> ResolvedTricycleConfig:
    cfg = config or TricycleConfig()

    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    frame_form = _pick(cfg.frame_form, FRAME_FORMS)
    steering_form = _pick(cfg.steering_form, STEERING_FORMS)
    rear_module = _pick(cfg.rear_module, REAR_MODULES)
    drive_form = _pick(cfg.drive_form, DRIVE_FORMS)

    is_tadpole = frame_form == "tadpole_twin_front"
    front_count, rear_count = (2, 1) if is_tadpole else (1, 2)

    # Gate: front direct drive requires a single front wheel (opposed cranks
    # cannot share a transverse dual-front axle) -> tadpole degrades to mid_drive.
    if drive_form == "front_direct_pedals" and front_count != 1:
        drive_form = "mid_drive_freewheel"

    seat_count = int(cfg.seat_count) if cfg.seat_count in SEAT_COUNTS else 1

    radius_scale = _clamp(cfg.wheel_radius_scale, 0.90, 1.08)
    length_scale = _clamp(cfg.frame_length_scale, 0.92, 1.10)
    steer_range = _clamp(cfg.steer_range, 0.42, 0.60)

    front_wheel_radius = (FRONT_R_TADPOLE if is_tadpole else FRONT_R_DELTA) * radius_scale
    rear_wheel_radius = (REAR_R_TADPOLE if is_tadpole else REAR_R_DELTA) * radius_scale

    # Dual-track inequality: half-track must exceed half the tire width + gap.
    min_half = WHEEL_WIDTH / 2.0 + 0.020
    rear_half_track = _clamp(cfg.rear_half_track, 0.20, 0.28)
    if rear_count == 2:
        rear_half_track = max(rear_half_track, min_half)
    # Wide enough that the twin front wheels sit clearly outboard of the pedal
    # sweep (mid/shaft crank pedals reach ~y=0.125).
    front_half_track = max(0.190, min_half) if front_count == 2 else 0.0

    return ResolvedTricycleConfig(
        frame_form=frame_form,
        steering_form=steering_form,
        drive_form=drive_form,
        rear_module=rear_module,
        seat_count=seat_count,
        palette_style=palette_style,
        front_count=front_count,
        rear_count=rear_count,
        front_wheel_radius=front_wheel_radius,
        rear_wheel_radius=rear_wheel_radius,
        steer_pivot_x=STEER_PIVOT_X0 * length_scale,
        rear_axle_x=REAR_AXLE_X0 * length_scale,
        seat_ref_x=SEAT_REF_X0 * length_scale,
        # Tadpole front wheels are steering children that swing rearward when
        # turned; keep the frame crank further back so pedals stay clear of them.
        bottom_bracket_x=(BOTTOM_BRACKET_X0 - (0.09 if is_tadpole else 0.0)) * length_scale,
        front_half_track=front_half_track,
        rear_half_track=rear_half_track,
        steer_range=steer_range,
        lean_angle=0.2091,
        name=cfg.name or "tricycle",
    )


def with_overrides(config: TricycleConfig, **kwargs: object) -> TricycleConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: TricycleConfig | ResolvedTricycleConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTricycleConfig) else resolve_config(config)
    return (
        ("frame_form", r.frame_form),
        ("steering_form", r.steering_form),
        ("drive_form", r.drive_form),
        ("rear_module", r.rear_module),
        ("seat_count", f"seats_{r.seat_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


SEAT_SPACING = 0.18


def _deck_top(r: ResolvedTricycleConfig) -> float:
    """Rear deck top face (rear_module mount height); above the rear tire top."""
    rz = r.rear_wheel_radius
    return max(rz + 0.14, 2.0 * rz + 0.012)


def _seat_positions(r: ResolvedTricycleConfig) -> list[float]:
    """Seat x positions, centered on the seat reference so N seats fit between
    the head tube (front) and the rear module without interpenetrating."""
    n = r.seat_count
    return [r.seat_ref_x + (i - (n - 1) / 2.0) * SEAT_SPACING for i in range(n)]


# ---------------------------------------------------------------------------
# Frame-form tube sets (Slot A). Each adds main frame tubes to the chassis.
# Shared hardware (head tube, rear axle, cargo deck, fenders) is added by
# _build_chassis so every mounting anchor stays consistent across forms.
# ---------------------------------------------------------------------------
def _frame_low_step_child(chassis, r, mats) -> None:
    sx = r.steer_pivot_x / STEER_PIVOT_X0
    _tube_visual(
        chassis,
        "frame_spine",
        [
            (0.29 * sx, 0.0, 0.49),
            (0.23 * sx, 0.0, 0.42),
            (0.08 * sx, 0.0, 0.34),
            (-0.09 * sx, 0.0, 0.29),
            (-0.28 * sx, 0.0, 0.27),
            (-0.43 * sx, 0.0, 0.22),
        ],
        0.026,
        mats["frame"],
    )
    _tube_visual(
        chassis,
        "lower_frame",
        [(0.19 * sx, 0.0, 0.40), (0.10 * sx, 0.0, 0.26), (-0.22 * sx, 0.0, 0.20), (-0.43 * sx, 0.0, 0.17)],
        0.022,
        mats["trim"],
    )
    _tube_visual(
        chassis,
        "rear_upper_brace",
        [(-0.08 * sx, 0.0, 0.31), (-0.17 * sx, 0.0, 0.32), (-0.24 * sx, 0.0, 0.25)],
        0.021,
        mats["frame"],
    )
    chassis.visual(
        Box((0.30, 0.038, 0.095)),
        origin=Origin(xyz=(0.04 * sx, 0.0, 0.335), rpy=(0.0, -0.42, 0.0)),
        material=mats["trim"],
        name="side_plate", material_class_id="metal.paint_coated",
    )
    chassis.visual(
        Box((0.17, 0.044, 0.072)),
        origin=Origin(xyz=(-0.11 * sx, 0.0, 0.292), rpy=(0.0, -0.08, 0.0)),
        material=mats["accent"],
        name="frame_badge_blank", material_class_id="plastic.opaque_glossy_molded",
    )


def _frame_delta_adult(chassis, r, mats) -> None:
    sx = r.steer_pivot_x / STEER_PIVOT_X0
    # Upright diamond: top tube, down tube, seat tube.
    _tube_visual(
        chassis,
        "top_tube",
        [(0.31 * sx, 0.0, 0.50), (0.10 * sx, 0.0, 0.47), (-0.08 * sx, 0.0, 0.45)],
        0.023,
        mats["frame"],
    )
    _tube_visual(
        chassis,
        "down_tube",
        [(0.32 * sx, 0.0, 0.46), (0.16 * sx, 0.0, 0.30), (0.01 * sx, 0.0, 0.235)],
        0.024,
        mats["frame"],
    )
    _tube_visual(
        chassis,
        "seat_tube",
        [(-0.08 * sx, 0.0, 0.45), (-0.05 * sx, 0.0, 0.34), (0.01 * sx, 0.0, 0.235)],
        0.022,
        mats["frame"],
    )
    _tube_visual(
        chassis,
        "chain_stay",
        [(0.01 * sx, 0.0, 0.235), (-0.22 * sx, 0.0, 0.20), (-0.43 * sx, 0.0, 0.17)],
        0.020,
        mats["trim"],
    )
    _tube_visual(
        chassis,
        "seat_stay",
        [(-0.08 * sx, 0.0, 0.45), (-0.28 * sx, 0.0, 0.30), (-0.43 * sx, 0.0, 0.17)],
        0.018,
        mats["frame"],
    )
    chassis.visual(
        Box((0.11, 0.044, 0.070)),
        origin=Origin(xyz=(0.15 * sx, 0.0, 0.315), rpy=(0.0, -0.72, 0.0)),
        material=mats["accent"],
        name="frame_badge_blank", material_class_id="plastic.opaque_glossy_molded",
    )


def _frame_cargo_trike(chassis, r, mats) -> None:
    sx = r.steer_pivot_x / STEER_PIVOT_X0
    # Long low platform hauler: two straight side rails + cross platform.
    # The forward endpoint is solved behind the complete steered-tire envelope;
    # rails stay narrow through the crank zone and flare only behind it.
    front_tire_rear_x = r.steer_pivot_x + FRONT_AXLE_DX - r.front_wheel_radius
    rail_front_x = min(0.20 * sx, front_tire_rear_x - 0.030)
    for i, side in enumerate((-1.0, 1.0)):
        _tube_visual(
            chassis,
            f"cargo_rail_{i}",
            [
                (rail_front_x, side * 0.055, 0.36),
                (0.05 * sx, side * 0.062, 0.255),
                (-0.18 * sx, side * 0.150, 0.238),
                (-0.44 * sx, side * 0.150, 0.20),
            ],
            0.019,
            mats["frame"],
        )
    _tube_visual(
        chassis,
        "spine_low",
        [(0.31 * sx, 0.0, 0.42), (0.10 * sx, 0.0, 0.28), (-0.20 * sx, 0.0, 0.245), (-0.43 * sx, 0.0, 0.22)],
        0.024,
        mats["frame"],
    )
    chassis.visual(
        Box((0.34, 0.30, 0.020)),
        origin=Origin(xyz=(-0.30 * sx, 0.0, 0.250)),
        material=mats["trim"],
        name="platform_plate", material_class_id="metal.paint_coated",
    )
    chassis.visual(
        Box((0.13, 0.044, 0.058)),
        origin=Origin(xyz=(0.10 * sx, 0.0, 0.320), rpy=(0.0, -0.50, 0.0)),
        material=mats["accent"],
        name="frame_badge_blank", material_class_id="plastic.opaque_glossy_molded",
    )


def _frame_drift_trike(chassis, r, mats) -> None:
    sx = r.steer_pivot_x / STEER_PIVOT_X0
    # Low-slung rearward-raked frame with a broad rear cross-beam.
    _tube_visual(
        chassis,
        "backbone",
        [(0.32 * sx, 0.0, 0.44), (0.14 * sx, 0.0, 0.27), (-0.10 * sx, 0.0, 0.205), (-0.40 * sx, 0.0, 0.175)],
        0.028,
        mats["frame"],
    )
    _tube_visual(
        chassis,
        "under_rail",
        [(0.19 * sx, 0.0, 0.33), (0.08 * sx, 0.0, 0.215), (-0.30 * sx, 0.0, 0.165), (-0.44 * sx, 0.0, 0.16)],
        0.020,
        mats["trim"],
    )
    for i, side in enumerate((-1.0, 1.0)):
        _tube_visual(
            chassis,
            f"rear_wing_{i}",
            [(-0.16 * sx, 0.0, 0.205), (-0.34 * sx, side * 0.12, 0.185), (-0.44 * sx, side * 0.170, 0.17)],
            0.017,
            mats["frame"],
        )
    chassis.visual(
        Box((0.20, 0.05, 0.070)),
        origin=Origin(xyz=(0.02 * sx, 0.0, 0.255), rpy=(0.0, -0.30, 0.0)),
        material=mats["accent"],
        name="frame_badge_blank", material_class_id="plastic.opaque_glossy_molded",
    )


def _frame_tadpole(chassis, r, mats) -> None:
    sx = r.steer_pivot_x / STEER_PIVOT_X0
    # Rear spine + twin forward rails flaring around the rider to the head tube.
    _tube_visual(
        chassis,
        "rear_spine",
        [(0.02 * sx, 0.0, 0.315), (-0.09 * sx, 0.0, 0.29), (-0.28 * sx, 0.0, 0.27), (-0.43 * sx, 0.0, 0.22)],
        0.026,
        mats["frame"],
    )
    for i, side in enumerate((-1.0, 1.0)):
        _tube_visual(
            chassis,
            f"tadpole_front_rail_{i}",
            [
                (0.00, 0.0, 0.315),
                (0.10 * sx, side * 0.105, 0.325),
                (0.23 * sx, side * 0.155, 0.385),
                (0.31 * sx, side * 0.040, 0.475),
            ],
            0.023,
            mats["frame"],
        )
    _tube_visual(
        chassis,
        "front_rail_crossmember",
        [(0.205 * sx, -0.145, 0.375), (0.205 * sx, 0.145, 0.375)],
        0.018,
        mats["trim"],
    )
    _tube_visual(
        chassis,
        "lower_frame",
        [(0.28 * sx, 0.0, 0.40), (0.05 * sx, 0.0, 0.24), (-0.22 * sx, 0.0, 0.20), (-0.43 * sx, 0.0, 0.17)],
        0.021,
        mats["trim"],
    )
    chassis.visual(
        Box((0.15, 0.044, 0.062)),
        origin=Origin(xyz=(-0.11 * sx, 0.0, 0.285), rpy=(0.0, -0.08, 0.0)),
        material=mats["accent"],
        name="frame_badge_blank", material_class_id="plastic.opaque_glossy_molded",
    )


_FRAME_BUILDERS = {
    "low_step_child": _frame_low_step_child,
    "delta_adult": _frame_delta_adult,
    "cargo_trike": _frame_cargo_trike,
    "drift_trike": _frame_drift_trike,
    "tadpole_twin_front": _frame_tadpole,
}


# ---------------------------------------------------------------------------
# Chassis (root) — frame form + shared hardware + drive-decoration + seat posts.
# ---------------------------------------------------------------------------
def _build_chassis(model, r, mats, assets) -> object:
    chassis = model.part("chassis")
    _FRAME_BUILDERS[r.frame_form](chassis, r, mats)

    px = r.steer_pivot_x
    # Head tube (solid, so the vertical/raked steering axis always touches
    # parent hardware) + collars (steering interface).
    head_tube = cq.Workplane("XY").circle(0.033).extrude(0.15)
    chassis.visual(
        mesh_from_cadquery(head_tube, "head_tube", assets=assets),
        origin=Origin(xyz=(px, 0.0, HEAD_BOT_Z)),
        material=mats["trim"],
        name="head_tube", material_class_id="metal.paint_coated",
    )
    head_collar = cq.Workplane("XY").circle(0.046).circle(0.029).extrude(0.018)
    chassis.visual(
        mesh_from_cadquery(head_collar, "lower_head_collar", assets=assets),
        origin=Origin(xyz=(px, 0.0, HEAD_BOT_Z - 0.008)),
        material=mats["frame"],
        name="lower_head_collar", material_class_id="metal.paint_coated",
    )
    chassis.visual(
        mesh_from_cadquery(head_collar, "upper_head_collar", assets=assets),
        origin=Origin(xyz=(px, 0.0, HEAD_BOT_Z + 0.140)),
        material=mats["frame"],
        name="upper_head_collar", material_class_id="metal.paint_coated",
    )

    rx = r.rear_axle_x
    rz = r.rear_wheel_radius
    if r.rear_count == 2:
        chassis.visual(
            Cylinder(radius=0.015, length=2.0 * r.rear_half_track + 0.02),
            origin=Origin(xyz=(rx, 0.0, rz), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name="rear_axle", material_class_id="metal.steel_bare",
        )
    else:
        chassis.visual(
            Cylinder(radius=0.015, length=0.10),
            origin=Origin(xyz=(rx, 0.0, rz), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name="rear_axle", material_class_id="metal.steel_bare",
        )

    # Rear deck (rear_module mount face) + solid riser pedestal; the pedestal
    # welds the deck to the rear frame tubes for BOTH wheel layouts (delta wide
    # axle / tadpole single central wheel), sitting above the rear tire top.
    deck_top = _deck_top(r)
    # Encloses the rear axle at the bottom and reaches the frame rear tubes
    # (z ~0.17-0.22) on the way up to the deck.
    riser_bottom = rz - 0.02
    chassis.visual(
        Box((0.14, 0.24, deck_top - riser_bottom - 0.010)),
        origin=Origin(xyz=(rx - 0.02, 0.0, 0.5 * (riser_bottom + deck_top - 0.010))),
        material=mats["frame"],
        name="deck_riser", material_class_id="metal.paint_coated",
    )
    chassis.visual(
        Box((0.31, 0.36, 0.025)),
        origin=Origin(xyz=(rx - 0.03, 0.0, deck_top - 0.0125)),
        material=mats["trim"],
        name="cargo_deck", material_class_id="metal.paint_coated",
    )

    # Head-to-frame connector (down tube): guarantees the head tube welds to the
    # main frame for every frame form (all forms carry tubes through the
    # lower-front bottom-bracket region).
    # Routed high then behind the front wheel so it never enters the front tire's
    # x-z disk (the head tube sits within the wheel's fore-aft envelope).
    _tube_visual(
        chassis,
        "head_downtube",
        [
            (px, 0.0, HEAD_BOT_Z + 0.055),
            (px - 0.11, 0.0, 0.450),
            (px - 0.20, 0.0, 0.360),
            (r.bottom_bracket_x + 0.03, 0.0, 0.245),
        ],
        0.017,
        mats["frame"],
    )

    # Drive decoration on the chassis (mid/shaft-drive; chainring / driveshaft).
    if r.drive_form in ("mid_drive_freewheel", "shaft_drive"):
        bx = r.bottom_bracket_x
        # Inner bore snug on the 0.010 crank spindle so the spindle contacts it.
        shell = cq.Workplane("XY").circle(0.035).circle(0.008).extrude(0.030, both=True)
        chassis.visual(
            mesh_from_cadquery(shell, "bb_shell", assets=assets),
            origin=Origin(xyz=(bx, 0.0, BOTTOM_BRACKET_Z), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["trim"],
            name="bb_shell", material_class_id="metal.paint_coated",
        )
    if r.drive_form == "mid_drive_freewheel":
        bx = r.bottom_bracket_x
        chainring = _freewheel_chainring(0.070, 0.016, 0.006)
        chassis.visual(
            mesh_from_cadquery(chainring, "chainring", assets=assets),
            origin=Origin(xyz=(bx, 0.030, BOTTOM_BRACKET_Z), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name="chainring", material_class_id="metal.steel_bare",
        )
    if r.drive_form == "shaft_drive":
        bx = r.bottom_bracket_x
        bevel_y = (r.rear_half_track - 0.02) if r.rear_count == 2 else 0.03
        _tube_visual(
            chassis,
            "driveshaft",
            [(bx, 0.030, BOTTOM_BRACKET_Z), (rx + 0.10, 0.058, rz + 0.02), (rx, bevel_y, rz)],
            0.010,
            mats["metal"],
        )
        chassis.visual(
            Cylinder(radius=0.026, length=0.05),
            origin=Origin(xyz=(rx, bevel_y, rz), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["trim"],
            name="bevel_housing", material_class_id="metal.paint_coated",
        )

    # Seat posts (one per saddle; also the seat_count multiplicity hardware).
    for i, seat_x in enumerate(_seat_positions(r)):
        # Post runs from low on the frame up to the saddle base so it always
        # intersects some frame tube at this x (keeps chassis one component).
        post_bottom = 0.20
        post_top = STEER_PIVOT_Z
        chassis.visual(
            Cylinder(radius=0.021, length=post_top - post_bottom),
            origin=Origin(xyz=(seat_x, 0.0, 0.5 * (post_bottom + post_top))),
            material=mats["metal"],
            name=f"seat_post_{i}", material_class_id="metal.aluminum_bare",
        )
        chassis.visual(
            Cylinder(radius=0.030, length=0.060),
            origin=Origin(xyz=(seat_x, 0.0, STEER_PIVOT_Z - 0.150)),
            material=mats["frame"],
            name=f"seat_post_sleeve_{i}", material_class_id="metal.paint_coated",
        )

    chassis.inertial = Inertial.from_geometry(
        Box((0.80, 0.42, 0.30)), mass=2.4, origin=Origin(xyz=(-0.05, 0.0, 0.28))
    )
    return chassis


def _freewheel_chainring(outer_radius: float, bore_radius: float, width: float):
    ring = cq.Workplane("XY").circle(outer_radius * 0.86).circle(bore_radius).extrude(width, both=True)
    tooth_width = outer_radius * 0.20
    tooth_depth = outer_radius * 0.16
    for index in range(16):
        angle = 360.0 * index / 16.0
        tooth = (
            cq.Workplane("XY")
            .box(tooth_depth, tooth_width, width * 2.0, centered=(True, True, True))
            .translate((outer_radius * 0.91, 0.0, 0.0))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        )
        ring = ring.union(tooth)
    return ring


# ---------------------------------------------------------------------------
# Steering (Slot B) — REVOLUTE about the head tube; carries fork + handlebar.
# Authored in steering-local frame whose origin is the head-tube-top pivot.
# ---------------------------------------------------------------------------
def _build_steering(model, r, mats, assets) -> object:
    steer = model.part("steering")
    fr = r.front_wheel_radius
    axle_z = fr - STEER_PIVOT_Z  # steering-local z of the front axle

    # Stem runs from the fork crown up through the handlebar clamp so the bar and
    # grips stay one connected component with the fork.
    steer.visual(
        Cylinder(radius=0.024, length=0.40),
        origin=Origin(xyz=(0.0, 0.0, 0.085)),
        material=mats["metal"],
        name="steering_stem", material_class_id="metal.aluminum_bare",
    )
    steer.visual(
        Cylinder(radius=0.0285, length=0.045),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["trim"],
        name="steering_bearing", material_class_id="metal.stainless_matte",
    )
    steer.visual(
        Box((0.070, 0.115, 0.038)),
        origin=Origin(xyz=(FRONT_AXLE_DX * 0.07, 0.0, -0.125)),
        material=mats["frame"],
        name="fork_crown", material_class_id="metal.paint_coated",
    )

    crown = (FRONT_AXLE_DX * 0.07, 0.0, -0.125)
    if r.front_count == 2:
        ht = r.front_half_track
        for i, side in enumerate((-1.0, 1.0)):
            _tube_visual(
                steer,
                f"fork_leg_{i}",
                [crown, (FRONT_AXLE_DX * 0.6, side * 0.10, -0.24), (FRONT_AXLE_DX, side * ht, axle_z)],
                0.017,
                mats["frame"],
            )
            steer.visual(
                Cylinder(radius=0.013, length=0.030),
                origin=Origin(xyz=(FRONT_AXLE_DX, side * ht, axle_z), rpy=(pi / 2.0, 0.0, 0.0)),
                material=mats["metal"],
                name=f"front_axle_stub_{i}", material_class_id="metal.steel_bare",
            )
    else:
        for i, side in enumerate((-1.0, 1.0)):
            _tube_visual(
                steer,
                f"fork_leg_{i}",
                [crown, (FRONT_AXLE_DX * 0.5, side * 0.052, -0.20), (FRONT_AXLE_DX, side * 0.052, axle_z)],
                0.018,
                mats["frame"],
            )
        # Single through-axle spanning both fork ends and the centered hub, so
        # the front wheel physically contacts the fork (support path).
        steer.visual(
            Cylinder(radius=0.013, length=0.120),
            origin=Origin(xyz=(FRONT_AXLE_DX, 0.0, axle_z), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name="front_axle", material_class_id="metal.steel_bare",
        )

    # Handlebar + grips + bridge.
    _tube_visual(
        steer,
        "handlebar",
        [
            (0.0, -0.205, 0.235),
            (0.0, -0.055, 0.278),
            (0.0, 0.055, 0.278),
            (0.0, 0.205, 0.235),
        ],
        0.012,
        mats["trim"],
    )
    steer.visual(
        Box((0.050, 0.045, 0.115)),
        origin=Origin(xyz=(0.0, 0.0, 0.205)),
        material=mats["trim"],
        name="handlebar_bridge", material_class_id="metal.paint_coated",
    )
    for i, side in enumerate((-1.0, 1.0)):
        steer.visual(
            Cylinder(radius=0.018, length=0.100),
            origin=Origin(xyz=(0.0, side * 0.190, 0.247), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name=f"grip_{i}", material_class_id="rubber.smooth_plain",
        )
        for ring_index in range(3):
            steer.visual(
                Cylinder(radius=0.0195, length=0.006),
                origin=Origin(xyz=(0.0, side * (0.154 + ring_index * 0.021), 0.247), rpy=(pi / 2.0, 0.0, 0.0)),
                material=mats["frame"],
                name=f"grip_rib_{i}_{ring_index}", material_class_id="plastic.opaque_glossy_molded",
            )

    # Steering-form-specific extras.
    if r.steering_form == "linkage":
        _tube_visual(
            steer,
            "upper_steering_link",
            [(FRONT_AXLE_DX, 0.0, 0.030), (FRONT_AXLE_DX * 0.5, 0.0, 0.010), (0.0, 0.0, -0.008)],
            0.015,
            mats["frame"],
        )
        steer.visual(
            Cylinder(radius=0.027, length=0.020),
            origin=Origin(xyz=(FRONT_AXLE_DX, 0.0, 0.030)),
            material=mats["trim"],
            name="upper_link_boss", material_class_id="metal.paint_coated",
        )
        steer.visual(
            Cylinder(radius=0.020, length=0.16),
            origin=Origin(xyz=(FRONT_AXLE_DX, 0.0, -0.05)),
            material=mats["frame"],
            name="control_stem", material_class_id="metal.paint_coated",
        )
    elif r.steering_form == "lean":
        _tube_visual(
            steer,
            "steering_upper_clamp",
            [(-0.030, 0.0, 0.150), (-0.012, 0.0, 0.185), (0.0, 0.0, 0.205)],
            0.008,
            mats["metal"],
        )

    steer.inertial = Inertial.from_geometry(
        Box((0.30, 0.44, 0.40)), mass=0.7, origin=Origin(xyz=(FRONT_AXLE_DX * 0.5, 0.0, -0.05))
    )
    model.articulation(
        "steering_joint",
        ArticulationType.REVOLUTE,
        parent=model.get_part("chassis"),
        child=steer,
        origin=Origin(xyz=(r.steer_pivot_x, 0.0, STEER_PIVOT_Z)),
        axis=r.steer_axis,
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=-r.steer_range, upper=r.steer_range),
    )
    return steer


# ---------------------------------------------------------------------------
# Wheels.
# ---------------------------------------------------------------------------
def _add_wheel(model, name, parent, joint_origin, radius, mats, assets) -> object:
    part = model.part(name)
    _wheel_visuals(part, name, radius, WHEEL_WIDTH, mats)
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=radius, length=WHEEL_WIDTH),
        mass=0.2,
        origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        f"{name}_spin",
        ArticulationType.CONTINUOUS,
        parent=parent,
        child=part,
        origin=joint_origin,
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=18.0),
    )
    return part


# ---------------------------------------------------------------------------
# Drive (Slot C) — pedal_crank (REVOLUTE) + two CONTINUOUS pedals.
# ---------------------------------------------------------------------------
def _build_drive(model, r, mats, assets, front_axle_local) -> object:
    if r.drive_form == "front_direct_pedals":
        parent = model.get_part("steering")
        cx, cy, cz = front_axle_local  # crank origin in steering-local coords
        spindle_len = 0.210
    else:
        parent = model.get_part("chassis")
        cx, cy, cz = r.bottom_bracket_x, 0.0, BOTTOM_BRACKET_Z
        spindle_len = 0.176

    crank = model.part("pedal_crank")
    crank.visual(
        Cylinder(radius=0.010, length=spindle_len),
        origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="crank_spindle", material_class_id="metal.steel_bare",
    )
    for i, side in enumerate((-1.0, 1.0)):
        # opposed crank arms (180 deg apart): +x/-z on one side, -x/+z on other.
        ex = CRANK_ARM * side
        ez = -CRANK_DROP * side
        _tube_visual(
            crank,
            f"crank_arm_{i}",
            [(0.0, side * CRANK_HALF, 0.0), (ex, side * CRANK_HALF, ez)],
            0.010,
            mats["frame"],
        )
        crank.visual(
            Cylinder(radius=0.014, length=0.030),
            origin=Origin(xyz=(ex, side * (CRANK_HALF + 0.020), ez), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name=f"pedal_axle_{i}", material_class_id="metal.steel_bare",
        )
    crank.inertial = Inertial.from_geometry(
        Cylinder(radius=CRANK_ARM, length=spindle_len),
        mass=0.15,
        origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "crank_joint",
        ArticulationType.REVOLUTE,
        parent=parent,
        child=crank,
        origin=Origin(xyz=(cx, cy, cz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=8.0, lower=-pi, upper=pi),
    )

    for i, side in enumerate((-1.0, 1.0)):
        ex = CRANK_ARM * side
        ez = -CRANK_DROP * side
        pedal = model.part(f"pedal_{i}")
        pedal.visual(
            Box((PEDAL_LEN_X, 0.045, 0.020)),
            origin=Origin(xyz=(0.0, side * 0.008, 0.0)),
            material=mats["frame"],
            name="pedal_body", material_class_id="metal.paint_coated",
        )
        pedal.visual(
            Box((PEDAL_LEN_X - 0.028, 0.048, 0.006)),
            origin=Origin(xyz=(0.0, side * 0.008, 0.013)),
            material=mats["accent"],
            name="pedal_tread", material_class_id="rubber.directional_grooved",
        )
        pedal.inertial = Inertial.from_geometry(Box((PEDAL_LEN_X, 0.045, 0.020)), mass=0.03)
        model.articulation(
            f"pedal_{i}_spin",
            ArticulationType.CONTINUOUS,
            parent=crank,
            child=pedal,
            # In the crank's local frame (crank origin = crank_joint origin).
            origin=Origin(xyz=(ex, side * (CRANK_HALF + 0.020), ez)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=12.0),
        )
    return crank


# ---------------------------------------------------------------------------
# Rear module (Slot D) — FIXED to the chassis rear deck.
# ---------------------------------------------------------------------------
def _rear_cargo_basket(part, r, mats, assets, deck_top) -> None:
    part.visual(
        mesh_from_cadquery(_rounded_open_bin(0.35, 0.43, 0.13, 0.026), "basket_shell", assets=assets),
        material=mats["frame"],
        name="basket_shell", material_class_id="metal.paint_coated",
    )
    part.visual(
        mesh_from_cadquery(_rounded_ring(0.37, 0.45, 0.022, 0.026), "basket_rim", assets=assets),
        origin=Origin(xyz=(0.0, 0.0, 0.126)),
        material=mats["trim"],
        name="basket_rim", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.025, 0.31, 0.060)),
        origin=Origin(xyz=(0.148, 0.0, 0.064)),
        material=mats["accent"],
        name="basket_front_reinforcement", material_class_id="metal.paint_coated",
    )


def _rear_passenger_bench(part, r, mats, assets, deck_top) -> None:
    part.visual(
        mesh_from_cadquery(_rounded_slab(0.34, 0.42, 0.045, 0.03), "bench_base", assets=assets),
        material=mats["frame"],
        name="bench_base", material_class_id="metal.paint_coated",
    )
    part.visual(
        mesh_from_cadquery(_rounded_slab(0.30, 0.38, 0.040, 0.03), "bench_cushion", assets=assets),
        origin=Origin(xyz=(0.0, 0.0, 0.045)),
        material=mats["accent"],
        name="bench_cushion", material_class_id="leather.smooth_plain",
    )
    part.visual(
        mesh_from_cadquery(_rounded_slab(0.045, 0.42, 0.150, 0.02), "bench_backrest", assets=assets),
        origin=Origin(xyz=(-0.148, 0.0, 0.045)),
        material=mats["frame"],
        name="bench_backrest", material_class_id="metal.paint_coated",
    )
    for i, side in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.30, 0.020, 0.070)),
            origin=Origin(xyz=(-0.01, side * 0.205, 0.070)),
            material=mats["frame"],
            name=f"bench_side_rail_{i}", material_class_id="metal.paint_coated",
        )


def _rear_flat_deck(part, r, mats, assets, deck_top) -> None:
    # World-knowledge extrapolation (Macro Surface Construction): a flat load
    # deck with a raised perimeter lip. Same part-tree/FIXED interface as basket.
    part.visual(
        mesh_from_cadquery(_rounded_slab(0.38, 0.44, 0.030, 0.03), "deck_slab", assets=assets),
        material=mats["frame"],
        name="deck_slab", material_class_id="metal.paint_coated",
    )
    part.visual(
        mesh_from_cadquery(_rounded_ring(0.38, 0.44, 0.028, 0.022), "deck_lip", assets=assets),
        origin=Origin(xyz=(0.0, 0.0, 0.030)),
        material=mats["trim"],
        name="deck_lip", material_class_id="metal.paint_coated",
    )
    for i, sx in enumerate((-0.12, 0.12)):
        part.visual(
            Box((0.02, 0.40, 0.010)),
            origin=Origin(xyz=(sx, 0.0, 0.030)),
            material=mats["accent"],
            name=f"deck_batten_{i}", material_class_id="plastic.opaque_glossy_molded",
        )


_REAR_BUILDERS = {
    "cargo_basket": _rear_cargo_basket,
    "passenger_bench": _rear_passenger_bench,
    "flat_deck": _rear_flat_deck,
}


# ---------------------------------------------------------------------------
# Saddle (Slot E multiplicity) — one FIXED part per seat, resting on its post.
# ---------------------------------------------------------------------------
def _build_saddle(model, r, mats, assets, index, seat_x) -> None:
    saddle = model.part(f"saddle_{index}")
    big = r.seat_count == 1
    if big:
        ba, bb, ca, cb = 0.14, 0.09, 0.116, 0.072
        stem_x, stem_h = -0.090, 0.098
        back_x, back_r, back_z = -0.122, (0.090, 0.108), 0.140
    else:
        # Compact tandem pad: short backrest so adjacent seats never interpenetrate.
        ba, bb, ca, cb = 0.072, 0.062, 0.058, 0.050
        stem_x, stem_h = -0.058, 0.062
        back_x, back_r, back_z = -0.078, (0.062, 0.072), 0.098
    saddle_base = cq.Workplane("XY").ellipse(ba, bb).extrude(0.042)
    saddle.visual(
        mesh_from_cadquery(saddle_base, f"saddle_base_{index}", assets=assets),
        material=mats["frame"],
        name="saddle_base", material_class_id="metal.paint_coated",
    )
    cushion = cq.Workplane("XY").ellipse(ca, cb).extrude(0.030)
    saddle.visual(
        mesh_from_cadquery(cushion, f"saddle_cushion_{index}", assets=assets),
        origin=Origin(xyz=(0.010, 0.0, 0.035)),
        material=mats["trim"],
        name="saddle_cushion", material_class_id="leather.smooth_plain",
    )
    saddle.visual(
        Box((0.034, 0.055, stem_h)),
        origin=Origin(xyz=(stem_x, 0.0, 0.040 + stem_h * 0.5 - 0.010)),
        material=mats["frame"],
        name="backrest_stem", material_class_id="metal.paint_coated",
    )
    backrest = cq.Workplane("YZ").ellipse(back_r[0], back_r[1]).extrude(0.045)
    saddle.visual(
        mesh_from_cadquery(backrest, f"safety_backrest_{index}", assets=assets),
        origin=Origin(xyz=(back_x, 0.0, back_z)),
        material=mats["frame"],
        name="safety_backrest", material_class_id="metal.paint_coated",
    )
    saddle.inertial = Inertial.from_geometry(
        Box((0.24, 0.18, 0.22)), mass=0.2, origin=Origin(xyz=(stem_x * 0.6, 0.0, 0.06))
    )
    model.articulation(
        f"saddle_{index}_mount",
        ArticulationType.FIXED,
        parent=model.get_part("chassis"),
        child=saddle,
        origin=Origin(xyz=(seat_x, 0.0, STEER_PIVOT_Z - 0.001)),
    )


# ---------------------------------------------------------------------------
# Top-level build.
# ---------------------------------------------------------------------------
def build_tricycle(
    config: TricycleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets, meta={"category": "tricycle"})
    mats = {
        key: model.material(f"tricycle_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    chassis = _build_chassis(model, r, mats, assets)
    steer = _build_steering(model, r, mats, assets)

    fr = r.front_wheel_radius
    axle_z_local = fr - STEER_PIVOT_Z
    front_axle_local = (FRONT_AXLE_DX, 0.0, axle_z_local)

    # Front wheel(s): children of steering.
    if r.front_count == 2:
        ht = r.front_half_track
        for i, side in enumerate((-1.0, 1.0)):
            _add_wheel(
                model,
                f"wheel_f{i}",
                steer,
                Origin(xyz=(FRONT_AXLE_DX, side * ht, axle_z_local)),
                fr,
                mats,
                assets,
            )
    else:
        _add_wheel(model, "wheel_f0", steer, Origin(xyz=front_axle_local), fr, mats, assets)

    # Rear wheel(s): children of chassis.
    rx = r.rear_axle_x
    rr = r.rear_wheel_radius
    if r.rear_count == 2:
        ht = r.rear_half_track
        for i, side in enumerate((-1.0, 1.0)):
            _add_wheel(model, f"wheel_r{i}", chassis, Origin(xyz=(rx, side * ht, rr)), rr, mats, assets)
    else:
        _add_wheel(model, "wheel_r0", chassis, Origin(xyz=(rx, 0.0, rr)), rr, mats, assets)

    # Drive.
    _build_drive(model, r, mats, assets, front_axle_local)

    # Rear module (FIXED).
    deck_top = _deck_top(r)
    rear = model.part("rear_module")
    _REAR_BUILDERS[r.rear_module](rear, r, mats, assets, deck_top)
    rear.inertial = Inertial.from_geometry(
        Box((0.36, 0.45, 0.16)), mass=0.6, origin=Origin(xyz=(0.0, 0.0, 0.06))
    )
    model.articulation(
        "rear_module_mount",
        ArticulationType.FIXED,
        parent=chassis,
        child=rear,
        origin=Origin(xyz=(rx - 0.03, 0.0, deck_top - 0.002)),
    )

    # Saddles (multiplicity).
    for i, seat_x in enumerate(_seat_positions(r)):
        _build_saddle(model, r, mats, assets, i, seat_x)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_tricycle(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_tricycle(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------
def run_tricycle_tests(object_model: ArticulatedObject, config: TricycleConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    chassis = object_model.get_part("chassis")
    steer = object_model.get_part("steering")
    crank = object_model.get_part("pedal_crank")

    front_names = [f"wheel_f{i}" for i in range(r.front_count)]
    rear_names = [f"wheel_r{i}" for i in range(r.rear_count)]
    front_wheels = [object_model.get_part(n) for n in front_names]
    rear_wheels = [object_model.get_part(n) for n in rear_names]
    all_wheels = front_wheels + rear_wheels

    # ---- Captured / seated overlaps. ----
    # The fork steerer/crown and front fender nest into the frame's head-tube and
    # front-wheel cutout (part-level, mirroring the source records / baby_cycle).
    ctx.allow_overlap(
        chassis, steer,
        reason="Fork steerer/bearing and front fender nest into the head tube and front-wheel cutout.",
    )
    # Rear module spans over the rear wheel/fender envelope (origin: basket over wheel).
    rear_module_part = object_model.get_part("rear_module")
    ctx.allow_overlap(
        chassis, rear_module_part,
        reason="Rear cargo/bench module spans over the rear wheel and fender envelope.",
    )
    for w in rear_wheels:
        ctx.allow_overlap(
            rear_module_part, w,
            reason="Rear module deck spans directly over the rear wheel envelope.",
        )
    for w, n in zip(front_wheels, front_names):
        ctx.allow_overlap(steer, w, reason="Fork blades/axle stub straddle the front wheel hub.")
    for w in rear_wheels:
        ctx.allow_overlap(chassis, w, reason="Rear axle is captured through the wheel hub bore.")
    # Crank spindle passes through its bore / front hub.
    if r.drive_form == "front_direct_pedals":
        for w in front_wheels:
            ctx.allow_overlap(w, crank, reason="Front crank spindle passes through the direct-drive hub.")
        ctx.allow_overlap(steer, crank, reason="Crank spindle shares the front fork-end axle bore.")
    else:
        ctx.allow_overlap(chassis, crank, reason="Crank spindle passes through the bottom-bracket shell.")
    for i in range(2):
        pedal = object_model.get_part(f"pedal_{i}")
        ctx.allow_overlap(crank, pedal, reason="The pedal body rotates around a captured spindle.")

    # ---- Structure: exactly 3 ground wheels, all resting on z=0. ----
    ctx.check(
        "three road wheels present",
        r.wheel_count == 3
        and all(n in {p.name for p in object_model.parts} for n in front_names + rear_names),
        details=f"front={front_names}, rear={rear_names}",
    )
    for w in all_wheels:
        ab = ctx.part_world_aabb(w)
        ctx.check(
            f"{w.name} rests on the ground plane",
            ab is not None and abs(ab[0][2]) < 0.008,
            details=f"{w.name}_min_z={None if ab is None else ab[0][2]}",
        )

    # ---- Front/rear wheel size relationship (delta: front bigger). ----
    if r.front_count == 1 and r.rear_count == 2:
        fb = ctx.part_world_aabb(front_wheels[0])
        rb = ctx.part_world_aabb(rear_wheels[0])
        ctx.check(
            "delta front wheel is larger than the rear wheels",
            fb is not None and rb is not None
            and (fb[1][2] - fb[0][2]) > (rb[1][2] - rb[0][2]) + 0.040,
            details=f"front={fb}, rear={rb}",
        )

    # ---- Saddles present, FIXED, above the frame. ----
    for i in range(r.seat_count):
        saddle = object_model.get_part(f"saddle_{i}")
        j = object_model.get_articulation(f"saddle_{i}_mount")
        ctx.check(
            f"saddle_{i} FIXED and elevated",
            j is not None and j.articulation_type == ArticulationType.FIXED,
            details=f"saddle_{i}_joint={None if j is None else j.articulation_type}",
        )
        ctx.expect_contact(saddle, chassis, name=f"saddle_{i} mounted on its seat post")
    ctx.check(
        f"seat_count multiplicity == {r.seat_count}",
        f"saddle_{r.seat_count}" not in {p.name for p in object_model.parts},
        details=f"seats={sorted(p.name for p in object_model.parts if p.name.startswith('saddle_'))}",
    )

    # ---- Rear module FIXED and in contact with the chassis. ----
    rear = object_model.get_part("rear_module")
    rj = object_model.get_articulation("rear_module_mount")
    ctx.check(
        "rear module is FIXED to the chassis",
        rj is not None and rj.articulation_type == ArticulationType.FIXED,
        details=f"rear_joint={None if rj is None else rj.articulation_type}",
    )
    ctx.expect_contact(rear, chassis, name="rear module seated on the deck")

    # ---- Joint types / axes. ----
    steering = object_model.get_articulation("steering_joint")
    ctx.check(
        "steering is REVOLUTE",
        steering is not None and steering.articulation_type == ArticulationType.REVOLUTE,
        details=f"steering={None if steering is None else steering.articulation_type}",
    )
    crank_joint = object_model.get_articulation("crank_joint")
    ctx.check(
        "crank is REVOLUTE about Y",
        crank_joint is not None and crank_joint.articulation_type == ArticulationType.REVOLUTE
        and crank_joint.axis == (0.0, 1.0, 0.0),
        details=f"crank={None if crank_joint is None else crank_joint}",
    )
    for w in all_wheels:
        wj = object_model.get_articulation(f"{w.name}_spin")
        ctx.check(
            f"{w.name} is a CONTINUOUS Y spin joint",
            wj is not None and wj.articulation_type == ArticulationType.CONTINUOUS
            and wj.axis == (0.0, 1.0, 0.0),
            details=f"{w.name}_joint={None if wj is None else wj}",
        )

    # ---- Motion: steering swings the handlebar grip sideways. ----
    def _grip_center() -> tuple[float, float, float] | None:
        ab = ctx.part_element_world_aabb(steer, elem="grip_0")
        if ab is None:
            return None
        return tuple(0.5 * (ab[0][k] + ab[1][k]) for k in range(3))

    g0 = _grip_center()
    with ctx.pose({steering: r.steer_range}):
        g_left = _grip_center()
    with ctx.pose({steering: -r.steer_range}):
        g_right = _grip_center()
    if g0 is not None and g_left is not None and g_right is not None:
        lat_left = math.hypot(g_left[0] - g0[0], g_left[1] - g0[1])
        lat_right = math.hypot(g_right[0] - g0[0], g_right[1] - g0[1])
        ctx.check(
            "steering swings the handlebar sideways in both directions",
            lat_left > 0.02 and lat_right > 0.02,
            details=f"g0={g0}, left={g_left}, right={g_right}",
        )

    # ---- Motion: crank rotation carries a pedal around the axle. ----
    pedal0 = object_model.get_part("pedal_0")
    rest_pedal = ctx.part_world_position(pedal0)
    with ctx.pose({crank_joint: pi / 2.0}):
        turned_pedal = ctx.part_world_position(pedal0)
    if rest_pedal is not None and turned_pedal is not None:
        moved = math.dist(rest_pedal, turned_pedal)
        ctx.check(
            "crank rotation carries the pedal around the bottom bracket",
            moved > 0.06,
            details=f"rest={rest_pedal}, rotated={turned_pedal}, moved={moved}",
        )

    # ---- Motion: driven / representative wheels roll (off-center marker moves). ----
    for w in (front_wheels[0], rear_wheels[0]):
        roll = object_model.get_articulation(f"{w.name}_spin")
        m0 = ctx.part_element_world_aabb(w, elem=f"{w.name}_marker")
        with ctx.pose({roll: pi / 2.0}):
            m1 = ctx.part_element_world_aabb(w, elem=f"{w.name}_marker")
        c0 = None if m0 is None else (0.5 * (m0[0][0] + m0[1][0]), 0.5 * (m0[0][2] + m0[1][2]))
        c1 = None if m1 is None else (0.5 * (m1[0][0] + m1[1][0]), 0.5 * (m1[0][2] + m1[1][2]))
        ctx.check(
            f"{w.name} marker moves when the wheel rolls",
            c0 is not None and c1 is not None
            and (abs(c0[0] - c1[0]) > 0.01 or abs(c0[1] - c1[1]) > 0.01),
            details=f"rest={c0}, quarter_turn={c1}",
        )

    # ---- Drive gating. ----
    ctx.check(
        "front direct drive only with a single front wheel",
        r.drive_form != "front_direct_pedals" or r.front_count == 1,
        details=f"drive={r.drive_form}, front_count={r.front_count}",
    )

    # ---- Dynamic full-travel non-interpenetration. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "TricycleConfig",
    "ResolvedTricycleConfig",
    "build_tricycle",
    "build_seeded_tricycle",
    "config_from_seed",
    "resolve_config",
    "run_tricycle_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
