# SPDX-License-Identifier: Apache-2.0

"""Apollo-class lunar roving vehicle (LRV) - modular procedural template.

An open flat-deck ``chassis`` (root) rolls on N wire-mesh / balloon wheels, each
on an always-on CONTINUOUS roll joint (axis Y) - the category-defining motion.
The deck carries all non-moving furniture as fused visuals (Rule 1): dust
fenders, two webbed seats, a center console, battery/LCRU boxes, a TV camera and
a low-gain antenna staff. Parallel-children appendages parent directly to the
chassis: the running gear (wheels + optional front steering knuckles), a
high-gain antenna dish on a REVOLUTE mount mast, a hand controller (REVOLUTE
tilt or PRISMATIC throttle), and a rear equipment rack / tool pallet (FIXED or
REVOLUTE fold-down). One chassis candidate splits the deck into ``chassis``
(forward) + ``aft_deck`` on a REVOLUTE tri-fold hinge (a 2-hop chain for
anything aft-mounted).

Slot graph (pattern = mixed: root parallel children + wheel/tool multiplicity +
optional 2-hop steer / fold chains):

    chassis (root; rigid_deck | folding_deck[+aft_deck via deck_fold_hinge])
        -> running_gear   (N wheels CONTINUOUS roll; +2 front steer knuckles)
        -> antenna        (high_gain_antenna on REVOLUTE mount; umbrella|parabolic dish)
        -> hand_controller(REVOLUTE tilt | PRISMATIC throttle)
        -> rear_rack      (FIXED | REVOLUTE fold-down; N tool handles)

Coordinate frame: +X forward, +Y left, +Z up, ground at z=0.

Adopted sources (see spec Module Source Index):
  S1  origin Apollo LRV - rigid deck, 4 chevron wheels, umbrella HGA azimuth,
      tilt controller, fixed rack, arch fenders.
  S2  antenna_elevation - HGA mount axis Z -> Y.
  S3  controller_throttle - controller REVOLUTE -> PRISMATIC.
  S4  dish_parabolic - solid parabolic bowl dish.
  S5  fender_flat_plate - flat rectangular mudguard plate.
  S6  fold_chassis - split forward/aft deck + REVOLUTE tri-fold hinge.
  S7  rack_folddown - rack FIXED -> REVOLUTE fold-down.
  S8  steering_knuckle - front REVOLUTE-Z steer knuckles, 2-hop front wheels.
  S9  tire_solid - smooth balloon LatheGeometry tire.
  S10 tool_handles_n - 3..5 rear tool handles.
  S11 wheels_six - 6 wheels (mid axle row).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
)
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    LatheGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
)

# Modular template: sweep coverage uses per-slot module realization.
__modular__ = True


# --------------------------------------------------------------------------- #
# Module enums
# --------------------------------------------------------------------------- #

ChassisModule = Literal["rigid_deck", "folding_deck"]
GearModule = Literal["roll_four", "roll_six", "steered_four"]
AntennaModule = Literal["azimuth_dish", "elevation_dish"]
ControllerModule = Literal["tilt_control", "throttle_control"]
RackModule = Literal["fixed_rack", "folddown_rack"]
DishForm = Literal["umbrella", "parabolic"]
TireForm = Literal["chevron", "balloon"]
FenderForm = Literal["arch", "flat_plate"]
LunarRoverPalette = Literal[
    "apollo_lrv",
    "bare_alloy",
    "dust_tan",
    "charcoal_service",
    "white_thermal",
    "gunmetal",
]


# --------------------------------------------------------------------------- #
# Fixed real dimensions (constants with a one-line basis; Contract 3e)
# --------------------------------------------------------------------------- #

WHEEL_RADIUS = 0.41        # LRV tire outer radius (real ~0.41 m); axle height = radius
WHEEL_WIDTH = 0.23
AXLE_Z = WHEEL_RADIUS      # ground contact: wheel center height = radius
DECK_TOP = 0.445           # top plane of the deck pan (real deck sits ~0.44 m up)

NOM_HALF_WHEELBASE = 1.145  # half of 2.29 m wheelbase
NOM_HALF_TRACK = 0.915      # half of 1.83 m track
FLOOR_LEN_RATIO = 1.135     # deck pan length / wheelbase (2.6 / 2.29)

FENDER_R_IN = 0.44
FENDER_R_OUT = 0.475
FENDER_WIDTH = 0.30
DISH_TILT = -0.5           # pitch of the dish (leans back toward Earth)

# Fraction-of-track anchors for the wheel-station furniture (from origin values
# 0.7375 / 0.85 / 0.72 divided by NOM_HALF_TRACK=0.915 so they scale with track).
SUSP_Y_FRAC = 0.7375 / NOM_HALF_TRACK   # suspension arm + steer kingpin y
AXLE_Y_FRAC = 0.85 / NOM_HALF_TRACK     # axle stub / fender stay y
POST_Y_FRAC = 0.72 / NOM_HALF_TRACK     # fender post y


# --------------------------------------------------------------------------- #
# Palette presets (>=3 colorways, here 6). Same 7 tokens for every colorway so
# every .visual references a registered material.
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "apollo_lrv": {
        "frame_alum": (0.72, 0.73, 0.76, 1.0),
        "wheel_mesh": (0.82, 0.83, 0.86, 1.0),
        "tire_rubber": (0.16, 0.16, 0.18, 1.0),
        "fender": (0.80, 0.62, 0.38, 1.0),
        "seat": (0.85, 0.78, 0.62, 1.0),
        "box_dark": (0.11, 0.11, 0.12, 1.0),
        "dish": (0.87, 0.87, 0.90, 1.0),
    },
    "bare_alloy": {
        "frame_alum": (0.78, 0.79, 0.82, 1.0),
        "wheel_mesh": (0.86, 0.87, 0.90, 1.0),
        "tire_rubber": (0.20, 0.20, 0.22, 1.0),
        "fender": (0.66, 0.67, 0.70, 1.0),
        "seat": (0.60, 0.61, 0.64, 1.0),
        "box_dark": (0.30, 0.31, 0.33, 1.0),
        "dish": (0.90, 0.91, 0.93, 1.0),
    },
    "dust_tan": {
        "frame_alum": (0.68, 0.64, 0.56, 1.0),
        "wheel_mesh": (0.74, 0.70, 0.62, 1.0),
        "tire_rubber": (0.18, 0.16, 0.14, 1.0),
        "fender": (0.82, 0.68, 0.44, 1.0),
        "seat": (0.80, 0.72, 0.55, 1.0),
        "box_dark": (0.24, 0.20, 0.16, 1.0),
        "dish": (0.86, 0.82, 0.72, 1.0),
    },
    "charcoal_service": {
        "frame_alum": (0.34, 0.35, 0.37, 1.0),
        "wheel_mesh": (0.50, 0.51, 0.53, 1.0),
        "tire_rubber": (0.07, 0.07, 0.08, 1.0),
        "fender": (0.40, 0.41, 0.43, 1.0),
        "seat": (0.28, 0.29, 0.31, 1.0),
        "box_dark": (0.12, 0.12, 0.13, 1.0),
        "dish": (0.70, 0.71, 0.74, 1.0),
    },
    "white_thermal": {
        "frame_alum": (0.88, 0.89, 0.91, 1.0),
        "wheel_mesh": (0.80, 0.81, 0.84, 1.0),
        "tire_rubber": (0.14, 0.14, 0.16, 1.0),
        "fender": (0.90, 0.90, 0.92, 1.0),
        "seat": (0.78, 0.80, 0.82, 1.0),
        "box_dark": (0.20, 0.21, 0.23, 1.0),
        "dish": (0.94, 0.95, 0.97, 1.0),
    },
    "gunmetal": {
        "frame_alum": (0.46, 0.48, 0.52, 1.0),
        "wheel_mesh": (0.58, 0.60, 0.64, 1.0),
        "tire_rubber": (0.09, 0.09, 0.10, 1.0),
        "fender": (0.52, 0.48, 0.40, 1.0),
        "seat": (0.40, 0.42, 0.46, 1.0),
        "box_dark": (0.14, 0.15, 0.17, 1.0),
        "dish": (0.74, 0.76, 0.80, 1.0),
    },
}

PALETTE_NAMES: tuple[str, ...] = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class LunarRoverConfig:
    """Public lunar_rover config. Module fields left ``None`` fall back to the
    origin-consistent anchor in ``resolve_config``."""

    chassis_module: ChassisModule | None = None
    gear_module: GearModule | None = None
    antenna_module: AntennaModule | None = None
    controller_module: ControllerModule | None = None
    rack_module: RackModule | None = None
    dish_form: DishForm | None = None
    tire_form: TireForm | None = None
    fender_form: FenderForm | None = None
    tool_handle_count: int = 3
    palette_style: LunarRoverPalette = "apollo_lrv"

    # Continuous scales (independent unless noted).
    deck_len_scale: float = 1.0
    track_scale: float = 1.0
    dish_scale: float = 1.0
    # Joint ranges (conditional on the chosen module).
    steer_range: float = 0.07
    hga_az: float = 2.6
    ctrl_tilt: float = 0.35
    fold_upper: float = 1.5
    rack_fold_upper: float = math.pi / 2.0


@dataclass(frozen=True)
class ResolvedLunarRoverConfig:
    """Clamped + gated config consumed by builders."""

    chassis_module: ChassisModule
    gear_module: GearModule
    antenna_module: AntennaModule
    controller_module: ControllerModule
    rack_module: RackModule
    dish_form: DishForm
    tire_form: TireForm
    fender_form: FenderForm
    tool_handle_count: int
    palette_style: str

    deck_len_scale: float
    track_scale: float
    dish_scale: float
    steer_range: float
    hga_az: float
    ctrl_tilt: float
    fold_upper: float
    rack_fold_upper: float

    # Derived geometry.
    half_wheelbase: float
    half_track: float
    deck_len: float
    aft_part_name: str          # "chassis" (rigid) | "aft_deck" (folding)
    # Ordered wheel stations: (name, x, y, kind) with kind in {front,mid,rear}.
    wheel_positions: tuple[tuple[str, float, float, str], ...]

    palette: dict[str, tuple[float, float, float, float]]

    @property
    def steered(self) -> bool:
        return self.gear_module == "steered_four"

    @property
    def folding(self) -> bool:
        return self.chassis_module == "folding_deck"

    @property
    def wheel_count(self) -> int:
        return len(self.wheel_positions)


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first; compatibility-gated)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> LunarRoverConfig:
    """Deterministic procedural sampling.

    seed 0 is the canonical origin LRV (rigid deck + 4 chevron wheels + umbrella
    HGA azimuth + tilt controller + fixed rack + arch fenders + 3 tool handles).
    Other seeds draw the chassis first (which gates the gear), then the other
    modules / forms / multiplicity / palette / continuous scales.
    """
    if seed == 0:
        return LunarRoverConfig(
            chassis_module="rigid_deck",
            gear_module="roll_four",
            antenna_module="azimuth_dish",
            controller_module="tilt_control",
            rack_module="fixed_rack",
            dish_form="umbrella",
            tire_form="chevron",
            fender_form="arch",
            tool_handle_count=3,
            palette_style="apollo_lrv",
        )

    rng = random.Random(seed)

    chassis = rng.choices(("rigid_deck", "folding_deck"), weights=(0.6, 0.4))[0]

    # folding_deck cannot carry a mid axle row (it sits on the fold hinge line).
    if chassis == "folding_deck":
        gear = rng.choice(("roll_four", "steered_four"))
    else:
        gear = rng.choices(
            ("roll_four", "roll_six", "steered_four"), weights=(0.45, 0.30, 0.25)
        )[0]

    antenna = rng.choice(("azimuth_dish", "elevation_dish"))
    controller = rng.choice(("tilt_control", "throttle_control"))
    rack = rng.choice(("fixed_rack", "folddown_rack"))
    dish_form = rng.choice(("umbrella", "parabolic"))
    tire_form = rng.choice(("chevron", "balloon"))
    fender_form = rng.choice(("arch", "flat_plate"))
    tool_handle_count = rng.choices((3, 4, 5), weights=(0.5, 0.2, 0.3))[0]
    palette = rng.choice(PALETTE_NAMES)

    return LunarRoverConfig(
        chassis_module=chassis,
        gear_module=gear,
        antenna_module=antenna,
        controller_module=controller,
        rack_module=rack,
        dish_form=dish_form,
        tire_form=tire_form,
        fender_form=fender_form,
        tool_handle_count=tool_handle_count,
        palette_style=palette,
        deck_len_scale=round(rng.uniform(0.90, 1.15), 4),
        track_scale=round(rng.uniform(0.90, 1.15), 4),
        dish_scale=round(rng.uniform(0.85, 1.15), 4),
        steer_range=round(rng.uniform(0.05, 0.08), 4),
        hga_az=round(rng.uniform(1.8, 2.8), 4),
        ctrl_tilt=round(rng.uniform(0.25, 0.40), 4),
        fold_upper=round(rng.uniform(1.2, 1.6), 4),
        rack_fold_upper=round(rng.uniform(1.3, 1.6), 4),
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(config: LunarRoverConfig) -> ResolvedLunarRoverConfig:
    """Validate enums, gate combos, clamp/derive geometry."""
    chassis = config.chassis_module or "rigid_deck"
    if chassis not in ("rigid_deck", "folding_deck"):
        chassis = "rigid_deck"

    gear = config.gear_module or "roll_four"
    if gear not in ("roll_four", "roll_six", "steered_four"):
        gear = "roll_four"
    # Compatibility gate: folding deck excludes the six-wheel mid axle row.
    if chassis == "folding_deck" and gear == "roll_six":
        gear = "roll_four"

    antenna = config.antenna_module or "azimuth_dish"
    if antenna not in ("azimuth_dish", "elevation_dish"):
        antenna = "azimuth_dish"
    controller = config.controller_module or "tilt_control"
    if controller not in ("tilt_control", "throttle_control"):
        controller = "tilt_control"
    rack = config.rack_module or "fixed_rack"
    if rack not in ("fixed_rack", "folddown_rack"):
        rack = "fixed_rack"
    dish_form = config.dish_form or "umbrella"
    if dish_form not in ("umbrella", "parabolic"):
        dish_form = "umbrella"
    tire_form = config.tire_form or "chevron"
    if tire_form not in ("chevron", "balloon"):
        tire_form = "chevron"
    fender_form = config.fender_form or "arch"
    if fender_form not in ("arch", "flat_plate"):
        fender_form = "arch"
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    tool_handle_count = int(_clamp(config.tool_handle_count, 3, 5))

    # --- continuous scales ---
    deck_len_scale = _clamp(config.deck_len_scale, 0.90, 1.15)
    track_scale = _clamp(config.track_scale, 0.90, 1.15)
    dish_scale = _clamp(config.dish_scale, 0.85, 1.15)
    # Steer capped to a band where the yawed front tire clears the (deck-width)
    # pan/side-rail edge across the full range; the deck is as wide as the track
    # so a bigger swing sweeps the wide tire into the deck (Rule 5 clearance).
    steer_range = _clamp(config.steer_range, 0.05, 0.08)
    hga_az = _clamp(config.hga_az, 1.8, 2.8)
    ctrl_tilt = _clamp(config.ctrl_tilt, 0.25, 0.40)
    fold_upper = _clamp(config.fold_upper, 1.2, 1.6)
    rack_fold_upper = _clamp(config.rack_fold_upper, 1.3, 1.6)

    # --- derived geometry (single-sourced; Contract 3c) ---
    half_wheelbase = NOM_HALF_WHEELBASE * deck_len_scale
    half_track = NOM_HALF_TRACK * track_scale
    deck_len = 2.0 * half_wheelbase * FLOOR_LEN_RATIO

    # Wheel stations: front & rear rows always; mid row only for roll_six.
    stations: list[tuple[str, float, float, str]] = [
        ("front_left", half_wheelbase, half_track, "front"),
        ("front_right", half_wheelbase, -half_track, "front"),
        ("rear_left", -half_wheelbase, half_track, "rear"),
        ("rear_right", -half_wheelbase, -half_track, "rear"),
    ]
    if gear == "roll_six":
        stations.extend(
            [
                ("mid_left", 0.0, half_track, "mid"),
                ("mid_right", 0.0, -half_track, "mid"),
            ]
        )

    aft_part_name = "aft_deck" if chassis == "folding_deck" else "chassis"

    palette = dict(PALETTES[config.palette_style])

    return ResolvedLunarRoverConfig(
        chassis_module=chassis,
        gear_module=gear,
        antenna_module=antenna,
        controller_module=controller,
        rack_module=rack,
        dish_form=dish_form,
        tire_form=tire_form,
        fender_form=fender_form,
        tool_handle_count=tool_handle_count,
        palette_style=config.palette_style,
        deck_len_scale=deck_len_scale,
        track_scale=track_scale,
        dish_scale=dish_scale,
        steer_range=steer_range,
        hga_az=hga_az,
        ctrl_tilt=ctrl_tilt,
        fold_upper=fold_upper,
        rack_fold_upper=rack_fold_upper,
        half_wheelbase=half_wheelbase,
        half_track=half_track,
        deck_len=deck_len,
        aft_part_name=aft_part_name,
        wheel_positions=tuple(stations),
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Shared geometry helpers
# --------------------------------------------------------------------------- #


def _fender_profile() -> list[tuple[float, float]]:
    """Annular arch sector in XY (later rotated into the XZ wheel plane)."""
    a0, a1 = math.radians(-15.0), math.radians(195.0)
    n = 28
    pts: list[tuple[float, float]] = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append((FENDER_R_OUT * math.cos(a), FENDER_R_OUT * math.sin(a)))
    for i in range(n + 1):
        a = a1 - (a1 - a0) * i / n
        pts.append((FENDER_R_IN * math.cos(a), FENDER_R_IN * math.sin(a)))
    return pts


def _dish_axis_point(dist: float, scale: float) -> tuple[float, float, float]:
    """Point on the tilted dish axis, ``dist`` above the dish apex (part-local).

    ``scale`` is accepted for API symmetry with the dish-mesh helpers; the feed
    stalk length is a fixed hardware dimension and does not scale with aperture.
    """
    apex = 0.87
    return (
        math.sin(DISH_TILT) * dist,
        0.0,
        apex + math.cos(DISH_TILT) * dist,
    )


def _umbrella_dish_mesh(scale: float):
    """Thin revolved umbrella wire-mesh shell (origin form)."""
    inner = [(0.015, 0.0), (0.10, 0.032), (0.20, 0.072), (0.31, 0.125)]
    outer = [(0.015, 0.007), (0.10, 0.039), (0.20, 0.079), (0.31, 0.132)]
    inner = [(r * scale, z * scale) for (r, z) in inner]
    outer = [(r * scale, z * scale) for (r, z) in outer]
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(inner, outer, segments=40),
        "lrv_hga_umbrella",
    )


def _parabolic_bowl_profile(scale: float) -> list[tuple[float, float]]:
    """Cross-section of a solid deep parabolic bowl for LatheGeometry.

    Concave reflecting face from hub to rim, a rim lip, then the convex back
    face rim -> hub offset inward by the shell wall thickness.
    """
    R = 0.31 * scale
    depth = 0.125 * scale
    wall = 0.020 * scale
    r0 = 0.015 * scale
    k = depth / (R * R)
    n = 12
    pts: list[tuple[float, float]] = []
    for i in range(n + 1):  # front concave face hub -> rim
        r = r0 + (R - r0) * i / n
        pts.append((r, k * r * r))
    pts.append((R, k * R * R - wall))  # rim lip down
    for i in range(n + 1):  # convex back face rim -> hub
        r = R - (R - r0) * i / n
        pts.append((r, k * r * r - wall))
    return pts


def _parabolic_dish_mesh(scale: float):
    return mesh_from_geometry(
        LatheGeometry(_parabolic_bowl_profile(scale), segments=48),
        "lrv_hga_parabolic",
    )


def _chevron_tire_mesh():
    return mesh_from_geometry(
        TireGeometry(
            WHEEL_RADIUS,
            WHEEL_WIDTH,
            inner_radius=0.30,
            carcass=TireCarcass(belt_width_ratio=0.70, sidewall_bulge=0.05),
            tread=TireTread(style="chevron", depth=0.014, count=24, angle_deg=30.0, land_ratio=0.55),
            sidewall=TireSidewall(style="rounded", bulge=0.05),
            shoulder=TireShoulder(width=0.012, radius=0.006),
        ),
        "lrv_tire_chevron",
    )


def _balloon_tire_profile() -> list[tuple[float, float]]:
    """Closed elliptical profile revolved about Z to form a smooth balloon tire."""
    inner_r = 0.30
    r_center = (WHEEL_RADIUS + inner_r) / 2.0
    r_half = (WHEEL_RADIUS - inner_r) / 2.0
    z_half = WHEEL_WIDTH / 2.0
    n = 36
    pts: list[tuple[float, float]] = []
    for i in range(n):
        a = 2.0 * math.pi * i / n
        pts.append((r_center + r_half * math.cos(a), z_half * math.sin(a)))
    return pts


def _balloon_tire_mesh():
    return mesh_from_geometry(
        LatheGeometry(_balloon_tire_profile(), segments=48),
        "lrv_tire_balloon",
    )


def _disc_mesh():
    return mesh_from_geometry(
        WheelGeometry(
            0.31,
            0.20,
            rim=WheelRim(
                inner_radius=0.27,
                flange_height=0.012,
                flange_thickness=0.006,
                bead_seat_depth=0.004,
            ),
            hub=WheelHub(radius=0.06, width=0.14, cap_style="domed"),
            face=WheelFace(dish_depth=0.02, front_inset=0.01, rear_inset=0.01),
            spokes=WheelSpokes(style="split_y", count=8, thickness=0.012, window_radius=0.04),
        ),
        "lrv_wheel_disc",
    )


def _add_wheel_visuals(wheel, r: ResolvedLunarRoverConfig, tire_mesh, disc_mesh) -> None:
    """Tire + disc, hub centered on (0,0,0); spin axis along part-frame Y."""
    if r.tire_form == "balloon":
        # LatheGeometry revolves about Z; roll -90deg maps Z -> the Y axle.
        wheel.visual(tire_mesh, origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
                     material="tire_rubber", name="tire", material_class_id="rubber.smooth_plain")
    else:
        # SDK tire helper spins about local X; yaw +90deg aligns it to the Y axle.
        wheel.visual(tire_mesh, origin=Origin(rpy=(0.0, 0.0, math.pi / 2)),
                     material="tire_rubber", name="tire", material_class_id="rubber.directional_grooved")
    wheel.visual(disc_mesh, origin=Origin(rpy=(0.0, 0.0, math.pi / 2)),
                 material="wheel_mesh", name="wheel_disc", material_class_id="metal.mesh_chainmail")


# --------------------------------------------------------------------------- #
# Slot A - chassis (root). Emits all fused deck furniture; folding adds aft_deck.
# --------------------------------------------------------------------------- #


def _chassis_downstream(r: ResolvedLunarRoverConfig) -> InterfaceSpec:
    """Chassis downstream face (informational; parallel children wire manually)."""
    return InterfaceSpec(
        interface_name="downstream",
        part_name="chassis",
        visual_name="floor_pan",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, DECK_TOP),
        contact_tol=0.004,
    )


def _add_wheel_station(
    part,
    r: ResolvedLunarRoverConfig,
    wname: str,
    wx: float,
    wy: float,
    *,
    z_off: float,
    include_axle_stub: bool,
    fender_mesh,
) -> None:
    """Suspension arm, axle stub, fender (arch|plate), fender post + stay."""
    s = 1.0 if wy > 0 else -1.0
    susp_y = s * SUSP_Y_FRAC * r.half_track
    post_y = s * POST_Y_FRAC * r.half_track
    stay_y = s * AXLE_Y_FRAC * r.half_track

    part.visual(
        Box((0.10, 0.105, 0.06)),
        origin=Origin(xyz=(wx, susp_y, AXLE_Z + z_off)),
        material="frame_alum",
        name=f"suspension_arm_{wname}", material_class_id="metal.aluminum_bare",
    )
    if include_axle_stub:
        # Axle stub bridges the suspension arm out to the wheel hub: derive its
        # length + center from both endpoints so it always overlaps the arm
        # (connectivity) and reaches the hub (captured pivot) at any track.
        inner = susp_y  # overlap the suspension arm
        outer = wy      # reach the wheel hub
        axle_len = abs(outer - inner) + 0.09
        axle_cy = (inner + outer) / 2.0
        part.visual(
            Cylinder(radius=0.03, length=axle_len),
            origin=Origin(xyz=(wx, axle_cy, AXLE_Z + z_off), rpy=(math.pi / 2, 0.0, 0.0)),
            material="frame_alum",
            name=f"axle_{wname}", material_class_id="metal.aluminum_bare",
        )
    if r.fender_form == "flat_plate":
        # Flat rectangular mudguard plate offset rearward, above the tire crown.
        part.visual(
            Box((0.55, FENDER_WIDTH, 0.015)),
            origin=Origin(xyz=(wx - 0.12, wy, 0.88 + z_off)),
            material="fender",
            name=f"fender_{wname}", material_class_id="metal.paint_coated",
        )
    else:
        part.visual(
            fender_mesh,
            origin=Origin(xyz=(wx, wy, AXLE_Z + z_off), rpy=(math.pi / 2, 0.0, 0.0)),
            material="fender",
            name=f"fender_{wname}", material_class_id="metal.paint_coated",
        )
    part.visual(
        Box((0.05, 0.05, 0.44)),
        origin=Origin(xyz=(wx, post_y, 0.665 + z_off)),
        material="frame_alum",
        name=f"fender_post_{wname}", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.05, 0.26, 0.05)),
        origin=Origin(xyz=(wx, stay_y, 0.875 + z_off)),
        material="frame_alum",
        name=f"fender_stay_{wname}", material_class_id="metal.aluminum_bare",
    )


def _add_seats(part, *, z_off: float, seat_x: float = -0.15) -> None:
    for side, sy in (("left", 1.0), ("right", -1.0)):
        part.visual(
            Box((0.45, 0.42, 0.04)),
            origin=Origin(xyz=(seat_x, sy * 0.35, 0.72 + z_off)),
            material="seat",
            name=f"seat_pan_{side}", material_class_id="fabric.webbing",
        )
        part.visual(
            Box((0.05, 0.42, 0.52)),
            origin=Origin(xyz=(seat_x - 0.235, sy * 0.35, 0.98 + z_off)),
            material="seat",
            name=f"seat_back_{side}", material_class_id="fabric.webbing",
        )
        for j, (lx, ly) in enumerate(((0.18, 0.17), (0.18, -0.17), (-0.18, 0.17), (-0.18, -0.17))):
            part.visual(
                Box((0.04, 0.04, 0.26)),
                origin=Origin(xyz=(seat_x + lx, sy * 0.35 + ly, 0.5725 + z_off)),
                material="frame_alum",
                name=f"seat_leg_{side}_{j}", material_class_id="metal.aluminum_bare",
            )


def _add_forward_furniture(part) -> None:
    """Console, battery boxes, low-gain staff, TV camera (forward deck items)."""
    part.visual(Box((0.30, 0.25, 0.35)), origin=Origin(xyz=(0.30, 0.0, 0.6175)),
                material="box_dark", name="console_body", material_class_id="metal.blackened_gunmetal")
    part.visual(Box((0.16, 0.22, 0.02)), origin=Origin(xyz=(0.24, 0.0, 0.80)),
                material="wheel_mesh", name="console_panel", material_class_id="tech.control_interface")
    for side, sy in (("left", 1.0), ("right", -1.0)):
        part.visual(Box((0.34, 0.44, 0.18)), origin=Origin(xyz=(0.80, sy * 0.34, 0.53)),
                    material="seat", name=f"battery_box_{side}", material_class_id="metal.paint_coated")
    part.visual(Cylinder(radius=0.012, length=0.55), origin=Origin(xyz=(0.85, -0.45, 0.72)),
                material="frame_alum", name="lowgain_mast", material_class_id="metal.aluminum_bare")
    part.visual(Cylinder(radius=0.025, length=0.10), origin=Origin(xyz=(0.85, -0.45, 0.95)),
                material="box_dark", name="lowgain_head", material_class_id="metal.blackened_gunmetal")
    part.visual(Cylinder(radius=0.015, length=0.30), origin=Origin(xyz=(1.18, -0.12, 0.595)),
                material="frame_alum", name="camera_post", material_class_id="metal.aluminum_bare")
    part.visual(Box((0.12, 0.12, 0.14)), origin=Origin(xyz=(1.18, -0.12, 0.79)),
                material="box_dark", name="camera_body", material_class_id="metal.blackened_gunmetal")
    part.visual(Cylinder(radius=0.03, length=0.05),
                origin=Origin(xyz=(1.25, -0.12, 0.80), rpy=(0.0, math.pi / 2, 0.0)),
                material="box_dark", name="camera_lens", material_class_id="glass.clear_transparent")


def _build_chassis(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedLunarRoverConfig = ctx.config  # type: ignore[assignment]
    chassis = model.part("chassis")

    fender_mesh = mesh_from_geometry(
        ExtrudeGeometry.centered(_fender_profile(), FENDER_WIDTH), "lrv_fender_arch"
    ) if r.fender_form == "arch" else None

    side_rail_y = 0.69 * r.track_scale
    floor_w = 1.44 * r.track_scale

    front_mid = [ws for ws in r.wheel_positions if ws[3] in ("front", "mid")]
    rear = [ws for ws in r.wheel_positions if ws[3] == "rear"]

    if not r.folding:
        # --- single flat deck ---
        chassis.visual(Box((r.deck_len, floor_w, 0.05)), origin=Origin(xyz=(0.0, 0.0, 0.42)),
                       material="frame_alum", name="floor_pan", material_class_id="metal.aluminum_bare")
        for side, sy in (("left", 1.0), ("right", -1.0)):
            chassis.visual(Box((r.deck_len, 0.06, 0.10)),
                           origin=Origin(xyz=(0.0, sy * side_rail_y, 0.42)),
                           material="frame_alum", name=f"side_rail_{side}", material_class_id="metal.aluminum_bare")
        # Forward rail kept inboard (0.60*hwb) so it clears the HGA mast at x=1.05.
        for i, cx in enumerate((-r.half_wheelbase * 0.85, 0.0, r.half_wheelbase * 0.45)):
            chassis.visual(Box((0.06, floor_w * 0.96, 0.08)),
                           origin=Origin(xyz=(cx, 0.0, 0.40)),
                           material="frame_alum", name=f"cross_rail_{i}", material_class_id="metal.aluminum_bare")
        for (wname, wx, wy, kind) in r.wheel_positions:
            _add_wheel_station(chassis, r, wname, wx, wy, z_off=0.0,
                               include_axle_stub=not (kind == "front" and r.steered),
                               fender_mesh=fender_mesh)
        _add_forward_furniture(chassis)
        _add_seats(chassis, z_off=0.0)
        internal_joints: list[str] = []
        parts = ["chassis"]
    else:
        # --- forward deck (root "chassis") ---
        # Only the two floor pans bridge the fold seam (x=0); every rail stays
        # >=`seam`m off the seam so the aft deck's pan is the sole overlap there.
        seam = 0.06
        fwd_len = r.deck_len * 0.5
        fwd_cx = r.deck_len * 0.25
        chassis.visual(Box((fwd_len, floor_w, 0.05)), origin=Origin(xyz=(fwd_cx, 0.0, 0.42)),
                       material="frame_alum", name="floor_pan", material_class_id="metal.aluminum_bare")
        for side, sy in (("left", 1.0), ("right", -1.0)):
            chassis.visual(Box((fwd_len - seam, 0.06, 0.10)),
                           origin=Origin(xyz=(fwd_cx + seam / 2.0, sy * side_rail_y, 0.42)),
                           material="frame_alum", name=f"side_rail_{side}_fwd", material_class_id="metal.aluminum_bare")
        # Forward rail kept inboard (0.60*hwb) so it clears the HGA mast at x=1.05.
        for i, cx in enumerate((0.10, r.half_wheelbase * 0.45)):
            chassis.visual(Box((0.06, floor_w * 0.96, 0.08)),
                           origin=Origin(xyz=(cx, 0.0, 0.40)),
                           material="frame_alum", name=f"cross_rail_fwd_{i}", material_class_id="metal.aluminum_bare")
        for (wname, wx, wy, kind) in front_mid:
            _add_wheel_station(chassis, r, wname, wx, wy, z_off=0.0,
                               include_axle_stub=not (kind == "front" and r.steered),
                               fender_mesh=fender_mesh)
        _add_forward_furniture(chassis)

        # --- aft deck (local frame origin at world (0,0,DECK_TOP)) ---
        aft_deck = model.part("aft_deck")
        zo = -DECK_TOP
        aft_len = r.deck_len * 0.5
        # Aft floor pan: rear edge at -deck_len/2, front edge extended +0.02 past
        # the seam to overlap the forward pan (the sole declared seam overlap).
        aft_deck.visual(Box((aft_len + 0.02, floor_w, 0.05)),
                        origin=Origin(xyz=(-r.deck_len * 0.25 + 0.01, 0.0, 0.42 + zo)),
                        material="frame_alum", name="floor_pan_aft", material_class_id="metal.aluminum_bare")
        # Aft side rails stop `seam`m short of the seam (front edge at -0.06).
        for side, sy in (("left", 1.0), ("right", -1.0)):
            aft_deck.visual(Box((aft_len - seam, 0.06, 0.10)),
                            origin=Origin(xyz=(-r.deck_len * 0.25 - seam / 2.0,
                                               sy * side_rail_y, 0.42 + zo)),
                            material="frame_alum", name=f"side_rail_{side}_aft", material_class_id="metal.aluminum_bare")
        aft_deck.visual(Box((0.06, floor_w * 0.96, 0.08)),
                        origin=Origin(xyz=(-r.half_wheelbase * 0.85, 0.0, 0.40 + zo)),
                        material="frame_alum", name="cross_rail_aft", material_class_id="metal.aluminum_bare")
        for (wname, wx, wy, kind) in rear:
            _add_wheel_station(aft_deck, r, wname, wx, wy, z_off=zo,
                               include_axle_stub=True, fender_mesh=fender_mesh)
        # Seats moved aft so their front legs sit behind the hinge (deck-fold
        # swings them clear of the forward deck) yet forward of the rack's
        # fold-down swing arc.
        _add_seats(aft_deck, z_off=zo, seat_x=-0.35)

        model.articulation(
            "deck_fold_hinge",
            ArticulationType.REVOLUTE,
            parent=chassis,
            child=aft_deck,
            origin=Origin(xyz=(0.0, 0.0, DECK_TOP)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=50.0, velocity=0.5, lower=0.0, upper=r.fold_upper),
        )
        internal_joints = ["deck_fold_hinge"]
        parts = ["chassis", "aft_deck"]

    return ModuleBuild(
        module_name=r.chassis_module,
        parts_emitted=parts,
        internal_articulations=internal_joints,
        interfaces={"downstream": _chassis_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B - running_gear (wheels + optional front steering knuckles).
# --------------------------------------------------------------------------- #


def _passthrough_downstream(ctx: ModuleBuildContext) -> InterfaceSpec:
    r: ResolvedLunarRoverConfig = ctx.config  # type: ignore[assignment]
    return _chassis_downstream(r)


def _build_running_gear(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedLunarRoverConfig = ctx.config  # type: ignore[assignment]
    chassis = model.get_part("chassis")
    aft = model.get_part(r.aft_part_name)
    aft_zoff = -DECK_TOP if r.folding else 0.0

    tire_mesh = _balloon_tire_mesh() if r.tire_form == "balloon" else _chevron_tire_mesh()
    disc_mesh = _disc_mesh()

    parts: list[str] = []
    joints: list[str] = []
    knuckle_pivot_y = SUSP_Y_FRAC * r.half_track  # kingpin at the suspension arm

    for (wname, wx, wy, kind) in r.wheel_positions:
        s = 1.0 if wy > 0 else -1.0
        wheel = model.part(f"wheel_{wname}")
        _add_wheel_visuals(wheel, r, tire_mesh, disc_mesh)
        parts.append(f"wheel_{wname}")

        if kind == "front" and r.steered:
            # 2-hop chain: chassis --REVOLUTE(Z) steer--> knuckle --CONT(Y)--> wheel
            knuckle = model.part(f"steering_knuckle_{wname}")
            arm_len = (AXLE_Y_FRAC * r.half_track) - knuckle_pivot_y  # pivot -> axle bearing
            knuckle.visual(Box((0.07, 0.03, 0.06)), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                           material="frame_alum", name="knuckle_pivot", material_class_id="metal.aluminum_bare")
            knuckle.visual(Box((0.06, abs(arm_len), 0.06)),
                           origin=Origin(xyz=(0.0, s * arm_len / 2.0, 0.0)),
                           material="frame_alum", name="knuckle_arm", material_class_id="metal.aluminum_bare")
            knuckle.visual(Cylinder(radius=0.03, length=0.10),
                           origin=Origin(xyz=(0.0, s * arm_len, 0.0), rpy=(math.pi / 2, 0.0, 0.0)),
                           material="frame_alum", name=f"axle_{wname}", material_class_id="metal.aluminum_bare")
            model.articulation(
                f"chassis_to_steer_{wname}",
                ArticulationType.REVOLUTE,
                parent=chassis,
                child=knuckle,
                origin=Origin(xyz=(wx, s * knuckle_pivot_y, AXLE_Z)),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=10.0, velocity=2.0,
                                           lower=-r.steer_range, upper=r.steer_range),
            )
            model.articulation(
                f"knuckle_to_wheel_{wname}",
                ArticulationType.CONTINUOUS,
                parent=knuckle,
                child=wheel,
                origin=Origin(xyz=(0.0, s * (r.half_track - knuckle_pivot_y), 0.0)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=30.0, velocity=10.0),
            )
            parts.append(f"steering_knuckle_{wname}")
            joints.append(f"chassis_to_steer_{wname}")
            joints.append(f"knuckle_to_wheel_{wname}")
        else:
            parent = aft if kind == "rear" else chassis
            z = AXLE_Z + (aft_zoff if kind == "rear" else 0.0)
            model.articulation(
                f"chassis_to_wheel_{wname}",
                ArticulationType.CONTINUOUS,
                parent=parent,
                child=wheel,
                origin=Origin(xyz=(wx, wy, z)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=30.0, velocity=10.0),
            )
            joints.append(f"chassis_to_wheel_{wname}")

    return ModuleBuild(
        module_name=r.gear_module,
        parts_emitted=parts,
        internal_articulations=joints,
        interfaces={"downstream": _passthrough_downstream(ctx)},
    )


# --------------------------------------------------------------------------- #
# Slot C - antenna (high-gain dish on a REVOLUTE mount).
# --------------------------------------------------------------------------- #


def _build_antenna(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedLunarRoverConfig = ctx.config  # type: ignore[assignment]
    chassis = model.get_part("chassis")
    ds = r.dish_scale

    hga = model.part("high_gain_antenna")
    hga.visual(Cylinder(radius=0.02, length=0.80), origin=Origin(xyz=(0.0, 0.0, 0.355)),
               material="frame_alum", name="hga_mast", material_class_id="metal.aluminum_bare")
    hga.visual(Box((0.06, 0.06, 0.10)), origin=Origin(xyz=(0.0, 0.0, 0.79)),
               material="box_dark", name="hga_gimbal", material_class_id="metal.blackened_gunmetal")
    dish_mesh = _parabolic_dish_mesh(ds) if r.dish_form == "parabolic" else _umbrella_dish_mesh(ds)
    hga.visual(dish_mesh, origin=Origin(xyz=(0.0, 0.0, 0.87), rpy=(0.0, DISH_TILT, 0.0)),
               material="dish", name="hga_dish", material_class_id="metal.aluminum_bare")
    hga.visual(Cylinder(radius=0.02, length=0.12),
               origin=Origin(xyz=_dish_axis_point(-0.03, ds), rpy=(0.0, DISH_TILT, 0.0)),
               material="frame_alum", name="hga_hub_stub", material_class_id="metal.aluminum_bare")
    hga.visual(Cylinder(radius=0.007, length=0.30),
               origin=Origin(xyz=_dish_axis_point(0.15, ds), rpy=(0.0, DISH_TILT, 0.0)),
               material="frame_alum", name="hga_feed_rod", material_class_id="metal.aluminum_bare")
    hga.visual(Sphere(radius=0.02), origin=Origin(xyz=_dish_axis_point(0.30, ds)),
               material="box_dark", name="hga_feed_tip", material_class_id="metal.blackened_gunmetal")

    if r.antenna_module == "elevation_dish":
        model.articulation(
            "chassis_to_high_gain_antenna",
            ArticulationType.REVOLUTE,
            parent=chassis,
            child=hga,
            origin=Origin(xyz=(1.05, 0.0, DECK_TOP)),
            axis=(0.0, 1.0, 0.0),
            # lower=0: the dish already rests at DISH_TILT=-0.5 (leaning back);
            # elevating further back lays it flat over the deck (crew/console
            # collision), so the actuator only pitches it up toward zenith.
            motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=0.0, upper=1.0),
        )
    else:
        model.articulation(
            "chassis_to_high_gain_antenna",
            ArticulationType.REVOLUTE,
            parent=chassis,
            child=hga,
            origin=Origin(xyz=(1.05, 0.0, DECK_TOP)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=-r.hga_az, upper=r.hga_az),
        )

    return ModuleBuild(
        module_name=r.antenna_module,
        parts_emitted=["high_gain_antenna"],
        internal_articulations=["chassis_to_high_gain_antenna"],
        interfaces={"downstream": _passthrough_downstream(ctx)},
    )


# --------------------------------------------------------------------------- #
# Slot D - hand_controller (REVOLUTE tilt | PRISMATIC throttle).
# --------------------------------------------------------------------------- #


def _build_hand_controller(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedLunarRoverConfig = ctx.config  # type: ignore[assignment]
    chassis = model.get_part("chassis")

    controller = model.part("hand_controller")
    controller.visual(Cylinder(radius=0.015, length=0.18), origin=Origin(xyz=(0.0, 0.0, 0.07)),
                      material="box_dark", name="controller_stem", material_class_id="metal.blackened_gunmetal")
    controller.visual(Box((0.04, 0.14, 0.035)), origin=Origin(xyz=(0.0, 0.0, 0.175)),
                      material="box_dark", name="controller_grip", material_class_id="rubber.smooth_plain")

    if r.controller_module == "throttle_control":
        model.articulation(
            "chassis_to_hand_controller",
            ArticulationType.PRISMATIC,
            parent=chassis,
            child=controller,
            origin=Origin(xyz=(0.40, 0.0, 0.78)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=0.5, lower=-0.04, upper=0.05),
        )
    else:
        model.articulation(
            "chassis_to_hand_controller",
            ArticulationType.REVOLUTE,
            parent=chassis,
            child=controller,
            origin=Origin(xyz=(0.40, 0.0, 0.78)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0,
                                       lower=-r.ctrl_tilt, upper=r.ctrl_tilt),
        )

    return ModuleBuild(
        module_name=r.controller_module,
        parts_emitted=["hand_controller"],
        internal_articulations=["chassis_to_hand_controller"],
        interfaces={"downstream": _passthrough_downstream(ctx)},
    )


# --------------------------------------------------------------------------- #
# Slot E - rear_rack (FIXED | REVOLUTE fold-down; N tool handles).
# --------------------------------------------------------------------------- #


def _build_rear_rack(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedLunarRoverConfig = ctx.config  # type: ignore[assignment]
    parent = model.get_part(r.aft_part_name)
    aft_zoff = -DECK_TOP if r.folding else 0.0

    rack = model.part("rear_equipment_rack")
    for side, sy in (("left", 1.0), ("right", -1.0)):
        rack.visual(Box((0.30, 0.05, 0.04)), origin=Origin(xyz=(0.08, sy * 0.45, 0.015)),
                    material="frame_alum", name=f"rack_base_rail_{side}", material_class_id="metal.aluminum_bare")
        rack.visual(Box((0.05, 0.05, 0.55)), origin=Origin(xyz=(-0.05, sy * 0.45, 0.29)),
                    material="frame_alum", name=f"rack_post_{side}", material_class_id="metal.aluminum_bare")
        rack.visual(Box((0.08, 0.05, 0.05)), origin=Origin(xyz=(-0.09, sy * 0.45, 0.455)),
                    material="frame_alum", name=f"rack_pallet_stub_{side}", material_class_id="metal.aluminum_bare")
    rack.visual(Box((0.30, 0.95, 0.04)), origin=Origin(xyz=(0.08, 0.0, 0.015)),
                material="frame_alum", name="rack_base_rail_center", material_class_id="metal.aluminum_bare")
    rack.visual(Box((0.05, 0.95, 0.05)), origin=Origin(xyz=(-0.05, 0.0, 0.555)),
                material="frame_alum", name="rack_top_rail", material_class_id="metal.aluminum_bare")
    rack.visual(Box((0.04, 0.95, 0.50)), origin=Origin(xyz=(-0.12, 0.0, 0.355)),
                material="frame_alum", name="tool_pallet_plate", material_class_id="metal.aluminum_bare")
    # N tool handles racked on the pallet, evenly spread along the rack Y.
    n = r.tool_handle_count
    span = 0.40
    for i in range(n):
        ty = -span + (2.0 * span) * i / (n - 1) if n > 1 else 0.0
        rack.visual(Cylinder(radius=0.012, length=0.45), origin=Origin(xyz=(-0.14, ty, 0.615)),
                    material="box_dark", name=f"tool_handle_{i}", material_class_id="metal.blackened_gunmetal")
    rack.visual(Box((0.10, 0.18, 0.22)), origin=Origin(xyz=(-0.07, -0.30, 0.495)),
                material="seat", name="sample_bag", material_class_id="fabric.canvas")

    # Anchor the fold pivot to the deck's rear-top edge (single-sourced from
    # deck_len) so the origin sits on the pan face at every deck_len_scale
    # (dist~0). Keeping it exactly on the edge (no inward inset) leaves all rack
    # hardware behind the pivot, so the fold-down arc never clips the deck pan.
    rack_x = -(r.deck_len / 2.0)
    origin_xyz = (rack_x, 0.0, DECK_TOP + aft_zoff)
    if r.rack_module == "folddown_rack":
        model.articulation(
            "chassis_to_rear_rack",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=rack,
            origin=Origin(xyz=origin_xyz),
            # Folds rearward/down (-Y) so the pallet swings away from the aft
            # seats rather than forward into the crew station.
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=0.0, upper=r.rack_fold_upper),
        )
    else:
        model.articulation(
            "chassis_to_rear_rack",
            ArticulationType.FIXED,
            parent=parent,
            child=rack,
            origin=Origin(xyz=origin_xyz),
        )

    return ModuleBuild(
        module_name=r.rack_module,
        parts_emitted=["rear_equipment_rack"],
        internal_articulations=["chassis_to_rear_rack"],
        interfaces={"downstream": _passthrough_downstream(ctx)},
    )


# --------------------------------------------------------------------------- #
# Slot graph + entry points
# --------------------------------------------------------------------------- #


def _slots_for_config(r: ResolvedLunarRoverConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="chassis",
                 candidates={r.chassis_module: _build_chassis},
                 anchor_choice=r.chassis_module),
        SlotSpec(slot_name="running_gear",
                 candidates={r.gear_module: _build_running_gear},
                 anchor_choice=r.gear_module),
        SlotSpec(slot_name="antenna",
                 candidates={r.antenna_module: _build_antenna},
                 anchor_choice=r.antenna_module),
        SlotSpec(slot_name="hand_controller",
                 candidates={r.controller_module: _build_hand_controller},
                 anchor_choice=r.controller_module),
        SlotSpec(slot_name="rear_rack",
                 candidates={r.rack_module: _build_rear_rack},
                 anchor_choice=r.rack_module),
    ]


def build_astronomy_lunar_rover(
    config: LunarRoverConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="apollo_lunar_roving_vehicle", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    rng = random.Random(0)
    assemble(
        model,
        slots=_slots_for_config(r),
        rng=rng,
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_astronomy_lunar_rover(seed: int) -> ArticulatedObject:
    return build_astronomy_lunar_rover(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("chassis", r.chassis_module),
        ("running_gear", r.gear_module),
        ("antenna_mount", r.antenna_module),
        ("controller", r.controller_module),
        ("rack", r.rack_module),
        ("dish_form", r.dish_form),
        ("tire_form", r.tire_form),
        ("fender_form", r.fender_form),
        ("wheel_count", str(r.wheel_count)),
        ("tool_handle_count", str(r.tool_handle_count)),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedLunarRoverConfig) -> None:
    parts = {p.name for p in model.parts}

    def _ov(a: str, b: str, *, reason: str, elem_a=None, elem_b=None) -> None:
        if a in parts and b in parts:
            ctx.allow_overlap(model.get_part(a), model.get_part(b),
                              reason=reason, elem_a=elem_a, elem_b=elem_b)

    # Wheel hub captured on its axle stub (chassis / aft_deck / knuckle).
    for (wname, _wx, _wy, kind) in r.wheel_positions:
        owner = "chassis"
        if kind == "rear":
            owner = r.aft_part_name
        if kind == "front" and r.steered:
            kn = f"steering_knuckle_{wname}"
            _ov(kn, f"wheel_{wname}",
                reason="Knuckle axle stub is captured inside the spinning hub.",
                elem_a=f"axle_{wname}", elem_b="wheel_disc")
            _ov(kn, f"wheel_{wname}",
                reason="Knuckle arm reaches into the wheel inner cavity to the hub bearing.",
                elem_a="knuckle_arm", elem_b="wheel_disc")
            # Kingpin bearing is nested into the deck structure at the suspension
            # arm end (captured steer bearing) - element-scoped to the pivot/arm.
            side_rail = f"side_rail_{'left' if _wy > 0 else 'right'}"
            side_rail = side_rail + ("_fwd" if r.folding else "")
            deck_pan = "floor_pan"
            for host in (f"suspension_arm_{wname}", side_rail, deck_pan):
                for elem in ("knuckle_pivot", "knuckle_arm"):
                    _ov("chassis", kn,
                        reason="Kingpin bearing block/arm is nested into the deck structure "
                               "at the suspension mount (captured steer bearing).",
                        elem_a=host, elem_b=elem)
            _ov("chassis", kn,
                reason="Knuckle axle stub overlaps the suspension arm end at the kingpin.",
                elem_a=f"suspension_arm_{wname}", elem_b=f"axle_{wname}")
            # The arch fender wraps the tire crown; the 210deg arch's convex
            # collision hull encloses the tire (and hub disc). This proximity is
            # intended and adjacent in the rolling topology -- it is only flagged
            # here because the steer knuckle makes chassis<->wheel a 2-hop
            # (unrelated) pair. Real mesh surfaces keep a ~20 mm radial gap.
            if r.fender_form == "arch":
                for tgt in ("tire", "wheel_disc"):
                    _ov("chassis", f"wheel_{wname}",
                        reason="Arch fender wraps the tire crown; its convex "
                               "hull encloses the wheel (adjacent in the rolling "
                               "topology, flagged only across the steer knuckle).",
                        elem_a=f"fender_{wname}", elem_b=tgt)
        else:
            _ov(owner, f"wheel_{wname}",
                reason="Axisymmetric axle stub is captured inside the spinning hub.",
                elem_a=f"axle_{wname}", elem_b="wheel_disc")

    # Antenna mast socketed into the deck pan.
    fp = "floor_pan"
    _ov("chassis", "high_gain_antenna",
        reason="Antenna mast root is socketed into the deck pan.",
        elem_a=fp, elem_b="hga_mast")
    # Hand controller stem captured in the console.
    _ov("chassis", "hand_controller",
        reason="Controller stem is a captured pivot/slide shaft inside the console.",
        elem_a="console_body", elem_b="controller_stem")
    # Rear rack base rails seat into the deck pan.
    rack_owner = r.aft_part_name
    rack_pan = "floor_pan_aft" if r.folding else "floor_pan"
    for side in ("left", "right"):
        _ov(rack_owner, "rear_equipment_rack",
            reason="Rack base rail seats a few mm into the deck pan as a bolted mount proxy.",
            elem_a=rack_pan, elem_b=f"rack_base_rail_{side}")
    _ov(rack_owner, "rear_equipment_rack",
        reason="Center rack rail seats a few mm into the deck pan as a bolted mount proxy.",
        elem_a=rack_pan, elem_b="rack_base_rail_center")

    # Folding deck: forward and aft pans abut/overlap slightly at the fold line.
    if r.folding:
        _ov("chassis", "aft_deck",
            reason="Forward and aft deck pans overlap ~1 cm at the tri-fold hinge line.",
            elem_a="floor_pan", elem_b="floor_pan_aft")


def run_astronomy_lunar_rover_tests(
    model: ArticulatedObject,
    config: LunarRoverConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_overlaps(ctx, model, r)

    # --- compiler baseline ---
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # --- category identity asserts ---
    wheel_joints = [
        j for j in getattr(model, "articulations", [])
        if j.articulation_type == ArticulationType.CONTINUOUS
    ]
    ctx.check(
        "has_rolling_wheel_joints",
        len(wheel_joints) == r.wheel_count,
        details=f"continuous={[j.name for j in wheel_joints]} expected={r.wheel_count}",
    )
    for j in wheel_joints:
        ctx.check(
            f"{j.name} spins about the lateral Y axle",
            abs(j.axis[1]) > 0.99,
            details=f"axis={j.axis}",
        )
    for (wname, _wx, _wy, _kind) in r.wheel_positions:
        aabb = ctx.part_world_aabb(model.get_part(f"wheel_{wname}"))
        ctx.check(
            f"wheel {wname} touches the lunar surface at rest",
            aabb is not None and abs(aabb[0][2]) <= 0.03,
            details=f"aabb={aabb}",
        )

    # --- Rule 5: sampled-pose overlap across all joints ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    # --- targeted per-mechanism poses ---
    # Wheel spin: assert the roll joint is CONTINUOUS about Y (a rotationally
    # symmetric wheel disc shows no AABB change under spin, so a displacement
    # test is meaningless here - the axis/type check is the real semantic).
    w0 = r.wheel_positions[0][0]
    spin_name = f"knuckle_to_wheel_{w0}" if (r.steered and r.wheel_positions[0][3] == "front") \
        else f"chassis_to_wheel_{w0}"
    spin = model.get_articulation(spin_name)
    ctx.check(
        "front wheel roll joint is CONTINUOUS about the lateral Y axle",
        spin.articulation_type == ArticulationType.CONTINUOUS and abs(spin.axis[1]) > 0.99,
        details=f"type={spin.articulation_type} axis={spin.axis}",
    )

    # HGA mount points the dish - test the off-axis feed tip (the dish centroid
    # sits almost on the azimuth axis, so use the feed tip at full range).
    hga_j = model.get_articulation("chassis_to_high_gain_antenna")
    if r.antenna_module == "elevation_dish":
        ctx.check("HGA elevation pivots about lateral Y", abs(hga_j.axis[1]) > 0.99,
                  details=f"axis={hga_j.axis}")
        hga_q = 0.8
    else:
        ctx.check("HGA azimuth swivels about vertical Z", abs(hga_j.axis[2]) > 0.99,
                  details=f"axis={hga_j.axis}")
        hga_q = r.hga_az
    tip_rest = ctx.part_element_world_aabb(model.get_part("high_gain_antenna"), elem="hga_feed_tip")
    with ctx.pose({hga_j: hga_q}):
        tip_posed = ctx.part_element_world_aabb(model.get_part("high_gain_antenna"), elem="hga_feed_tip")
        rc = None if tip_rest is None else tuple((a + b) / 2 for a, b in zip(tip_rest[0], tip_rest[1]))
        pc = None if tip_posed is None else tuple((a + b) / 2 for a, b in zip(tip_posed[0], tip_posed[1]))
        ctx.check("HGA mount slews the dish/feed", rc is not None and pc is not None
                  and math.dist(rc, pc) > 0.03, details=f"rest={rc}, posed={pc}")

    # Hand controller tilt / throttle displaces the grip.
    ctrl_j = model.get_articulation("chassis_to_hand_controller")
    grip_rest = ctx.part_element_world_aabb(model.get_part("hand_controller"), elem="controller_grip")
    ctrl_q = 0.05 if r.controller_module == "throttle_control" else r.ctrl_tilt
    with ctx.pose({ctrl_j: ctrl_q}):
        grip_posed = ctx.part_element_world_aabb(model.get_part("hand_controller"), elem="controller_grip")
        ctx.check("hand controller moves the grip",
                  grip_rest is not None and grip_posed is not None
                  and abs(grip_posed[0][0] - grip_rest[0][0]) > 0.02,
                  details=f"rest={grip_rest}, posed={grip_posed}")

    # Steering swings the front wheels laterally.
    if r.steered:
        for wname in ("front_left", "front_right"):
            steer = model.get_articulation(f"chassis_to_steer_{wname}")
            ctx.check(f"steer {wname} pivots about vertical Z", abs(steer.axis[2]) > 0.99,
                      details=f"axis={steer.axis}")
        steer_l = model.get_articulation("chassis_to_steer_front_left")
        wl_rest = ctx.part_world_aabb(model.get_part("wheel_front_left"))
        with ctx.pose({steer_l: r.steer_range}):
            wl_posed = ctx.part_world_aabb(model.get_part("wheel_front_left"))
            ctx.check("front steer swings the wheel laterally",
                      wl_rest is not None and wl_posed is not None
                      and abs(wl_posed[0][1] - wl_rest[0][1]) > 0.02,
                      details=f"rest={wl_rest}, posed={wl_posed}")

    # Deck fold raises the aft deck.
    if r.folding:
        fold = model.get_articulation("deck_fold_hinge")
        ctx.check("deck fold hinge pivots about lateral Y", abs(fold.axis[1]) > 0.99,
                  details=f"axis={fold.axis}")
        aft_rest = ctx.part_world_aabb(model.get_part("aft_deck"))
        with ctx.pose({fold: r.fold_upper}):
            aft_posed = ctx.part_world_aabb(model.get_part("aft_deck"))
            ctx.check("deck fold raises the aft deck for stowage",
                      aft_rest is not None and aft_posed is not None
                      and aft_posed[1][2] > aft_rest[1][2] + 0.2,
                      details=f"rest={aft_rest}, posed={aft_posed}")

    # Rear rack folds down.
    if r.rack_module == "folddown_rack":
        rack_j = model.get_articulation("chassis_to_rear_rack")
        ctx.check("rear rack fold-down is REVOLUTE about lateral Y", abs(rack_j.axis[1]) > 0.99,
                  details=f"axis={rack_j.axis}")
        pallet_rest = ctx.part_element_world_aabb(model.get_part("rear_equipment_rack"),
                                                  elem="tool_pallet_plate")
        with ctx.pose({rack_j: r.rack_fold_upper}):
            pallet_posed = ctx.part_element_world_aabb(model.get_part("rear_equipment_rack"),
                                                       elem="tool_pallet_plate")
            ctx.check("rear rack folds down for loading",
                      pallet_rest is not None and pallet_posed is not None
                      and pallet_posed[1][2] < pallet_rest[1][2] - 0.10,
                      details=f"rest={pallet_rest}, posed={pallet_posed}")

    return ctx.report()


__all__ = [
    "LunarRoverConfig",
    "ResolvedLunarRoverConfig",
    "LunarRoverPalette",
    "ChassisModule",
    "GearModule",
    "AntennaModule",
    "ControllerModule",
    "RackModule",
    "DishForm",
    "TireForm",
    "FenderForm",
    "build_astronomy_lunar_rover",
    "build_seeded_astronomy_lunar_rover",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_astronomy_lunar_rover_tests",
]
