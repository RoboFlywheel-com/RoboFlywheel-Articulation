# SPDX-License-Identifier: Apache-2.0

"""Astronomy / Mars rover — modular procedural template.

A Perseverance / MER-style planetary exploration rover: a boxy white ``body``
chassis (equipment or solar-array deck) carried on a six-wheel rocker-bogie
mobility system, with three deployable science subsystems parented directly to
the body (parallel-children pattern):

  * mobility     — 6 CONTINUOUS-spun cleated wheels + a rocker-bogie running
                   gear (fused / articulated / corner-steered);
  * camera_mast  — a pan/tilt remote-sensing mast (rigid or two-segment folding);
  * robotic_arm  — a front science arm (rigid / elbow / wrist-roll turret);
  * high_gain_antenna — a steerable comms dish (az-only or az-el gimbal).

Slot graph (pattern = parallel_children: root body + 4 parallel-children slots;
the body's own ③ deck form is Slot A):

    chassis body (root; equipment_deck / solar_wing_deck)
        ├─ mobility          (fused_rocker_bogie / articulated_rocker_bogie / steered_corners)
        ├─ camera_mast       (rigid_mast / folding_mast)
        ├─ robotic_arm       (rigid_arm / elbow_arm / turret_roll_arm)
        └─ high_gain_antenna (az_dish / azel_gimbal)

Adapted per AUTHORING.md §A/§B from the confirmed 5-star Mars rover pool
(spec: specs_modular_v1/Astronomy_Mars_rover.md). Sources (model.py:Lx-Ly cited
in the spec Module Source Index):

  S1  origin 母本 rec_a-perseverance-...6a5aa1bc — boxy chassis, equipment deck,
      fused rocker-bogie, 6 CONTINUOUS wheels, rigid pan/tilt mast, rigid arm,
      az-only HGA, all test semantics.
  S2  rocker_bogie_linkage — articulated rocker + bogie REVOLUTE(Y) suspension.
  S3  steering_knuckles    — 4 corner steering-knuckle parts REVOLUTE(Z).
  S4  spoked_wheel_hub      — spring-spoke lattice wheel disc.
  S5  folding_mast          — two-segment deployable mast REVOLUTE(Y).
  S6  multi_joint_arm       — upper_arm + forearm elbow REVOLUTE(Y).
  S7  turret_rotation       — instrument turret on wrist_roll CONTINUOUS(X).
  S8  hga_elevation_gimbal  — az-el 2-DOF antenna gimbal.
  S9  solar_deck            — MER-style flat solar-array wing deck.

Coordinate frame: +X = forward (mast/arm end), +Y = left, +Z = up, ground z=0.
All mirrored pieces straddle y=0.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from math import cos, pi, sin
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
    CylinderGeometry,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireGeometry,
    TireSidewall,
    TireTread,
    TorusGeometry,
    WheelFace,
    WheelGeometry,
    WheelHub,
    clamp_joint_limits,
    mesh_from_geometry,
    tube_from_spline_points,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


DeckForm = Literal["equipment_deck", "solar_wing_deck"]
MobilityModule = Literal[
    "fused_rocker_bogie",
    "articulated_rocker_bogie",
    "steered_corners",
]
WheelHubForm = Literal["solid_disc", "spoked_lattice"]
MastModule = Literal["rigid_mast", "folding_mast"]
ArmModule = Literal["rigid_arm", "elbow_arm", "turret_roll_arm"]
AntennaModule = Literal["az_dish", "azel_gimbal"]
RoverPalette = Literal[
    "nasa_white",
    "mer_gold",
    "dusty_tan",
    "dark_ops",
    "bare_metal",
    "science_blue",
]


# --------------------------------------------------------------------------- #
# Canonical dimensions (origin 母本 rec_a-perseverance-...6a5aa1bc)
# --------------------------------------------------------------------------- #

BODY_CENTER = (0.10, 0.0, 0.95)
BODY_SIZE = (2.20, 1.40, 0.60)
BODY_TOP = BODY_CENTER[2] + BODY_SIZE[2] / 2.0        # 1.25
BODY_HALF_W = BODY_SIZE[1] / 2.0                      # 0.70

DECK_SIZE = (2.00, 1.30, 0.06)
DECK_TOP = BODY_TOP + DECK_SIZE[2]                    # 1.31 (shared mount datum)
DECK_CENTER = (0.10, 0.0, BODY_TOP + DECK_SIZE[2] / 2.0)

NOM_WHEEL_RADIUS = 0.26
WHEEL_WIDTH = 0.20
WHEEL_TRACK_Y = 0.95
WHEEL_ROWS = ("front", "middle", "rear")
WHEEL_ROW_X = (1.05, 0.05, -0.95)
AXLE_RADIUS = 0.030
AXLE_INNER_Y = 0.72
AXLE_TIP_Y = 0.93
AXLE_LEN = AXLE_TIP_Y - (AXLE_INNER_Y - 0.02)
AXLE_MID_OFFSET = AXLE_INNER_Y - 0.02 + AXLE_LEN / 2.0

ROCKER_PIVOT = (0.25, 0.74, 0.95)
BOGIE_PIVOT = (-0.45, 0.80, 0.60)
SUSP_TUBE_R = 0.034

MAST_BASE = (0.75, 0.15, DECK_TOP)
NOM_MAST_HEIGHT = 0.88
ARM_SHOULDER = (1.32, -0.45, 0.85)
HGA_BASE = (0.10, 0.45, DECK_TOP + 0.10)

# Solar wing deck (solar_deck S9).
SOLAR_PANEL_THICKNESS = 0.025
WING_LENGTH = 1.80
WING_WIDTH = 1.00
SOLAR_CELL_SIZE = 0.16

DISH_PROFILE = [
    (0.015, 0.000), (0.140, 0.028), (0.280, 0.095), (0.280, 0.115),
    (0.140, 0.048), (0.030, 0.022), (0.015, 0.030), (0.015, 0.000),
]


# --------------------------------------------------------------------------- #
# Palettes (>=5 colorways; token set covers every .visual reference)
# --------------------------------------------------------------------------- #

_TOKENS = (
    "white_panel", "warm_white", "orange_accent", "gray_metal", "light_gray",
    "dark_gray", "black_tread", "lens_dark", "solar_blue", "grid_silver",
)

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "nasa_white": {
        "white_panel": (0.92, 0.92, 0.90, 1.0),
        "warm_white": (0.88, 0.87, 0.84, 1.0),
        "orange_accent": (0.93, 0.52, 0.12, 1.0),
        "gray_metal": (0.55, 0.56, 0.58, 1.0),
        "light_gray": (0.72, 0.73, 0.75, 1.0),
        "dark_gray": (0.22, 0.23, 0.25, 1.0),
        "black_tread": (0.06, 0.06, 0.07, 1.0),
        "lens_dark": (0.04, 0.04, 0.05, 1.0),
        "solar_blue": (0.11, 0.15, 0.42, 1.0),
        "grid_silver": (0.70, 0.72, 0.76, 1.0),
    },
    "mer_gold": {
        "white_panel": (0.30, 0.31, 0.33, 1.0),
        "warm_white": (0.40, 0.40, 0.42, 1.0),
        "orange_accent": (0.86, 0.62, 0.14, 1.0),
        "gray_metal": (0.60, 0.55, 0.40, 1.0),
        "light_gray": (0.80, 0.72, 0.42, 1.0),
        "dark_gray": (0.18, 0.17, 0.15, 1.0),
        "black_tread": (0.07, 0.06, 0.05, 1.0),
        "lens_dark": (0.04, 0.04, 0.04, 1.0),
        "solar_blue": (0.10, 0.13, 0.34, 1.0),
        "grid_silver": (0.82, 0.74, 0.46, 1.0),
    },
    "dusty_tan": {
        "white_panel": (0.80, 0.72, 0.60, 1.0),
        "warm_white": (0.74, 0.66, 0.55, 1.0),
        "orange_accent": (0.78, 0.42, 0.18, 1.0),
        "gray_metal": (0.56, 0.52, 0.47, 1.0),
        "light_gray": (0.68, 0.63, 0.56, 1.0),
        "dark_gray": (0.28, 0.24, 0.20, 1.0),
        "black_tread": (0.10, 0.08, 0.06, 1.0),
        "lens_dark": (0.05, 0.05, 0.05, 1.0),
        "solar_blue": (0.16, 0.18, 0.36, 1.0),
        "grid_silver": (0.66, 0.62, 0.55, 1.0),
    },
    "dark_ops": {
        "white_panel": (0.16, 0.17, 0.19, 1.0),
        "warm_white": (0.22, 0.23, 0.25, 1.0),
        "orange_accent": (0.72, 0.40, 0.10, 1.0),
        "gray_metal": (0.38, 0.40, 0.43, 1.0),
        "light_gray": (0.48, 0.50, 0.53, 1.0),
        "dark_gray": (0.10, 0.11, 0.12, 1.0),
        "black_tread": (0.04, 0.04, 0.05, 1.0),
        "lens_dark": (0.02, 0.02, 0.03, 1.0),
        "solar_blue": (0.07, 0.09, 0.22, 1.0),
        "grid_silver": (0.44, 0.46, 0.50, 1.0),
    },
    "bare_metal": {
        "white_panel": (0.68, 0.70, 0.73, 1.0),
        "warm_white": (0.62, 0.64, 0.67, 1.0),
        "orange_accent": (0.80, 0.52, 0.20, 1.0),
        "gray_metal": (0.72, 0.74, 0.77, 1.0),
        "light_gray": (0.82, 0.84, 0.86, 1.0),
        "dark_gray": (0.34, 0.35, 0.37, 1.0),
        "black_tread": (0.08, 0.08, 0.09, 1.0),
        "lens_dark": (0.06, 0.06, 0.07, 1.0),
        "solar_blue": (0.18, 0.24, 0.44, 1.0),
        "grid_silver": (0.86, 0.88, 0.90, 1.0),
    },
    "science_blue": {
        "white_panel": (0.90, 0.91, 0.93, 1.0),
        "warm_white": (0.84, 0.86, 0.90, 1.0),
        "orange_accent": (0.94, 0.58, 0.14, 1.0),
        "gray_metal": (0.52, 0.56, 0.62, 1.0),
        "light_gray": (0.70, 0.74, 0.80, 1.0),
        "dark_gray": (0.20, 0.24, 0.30, 1.0),
        "black_tread": (0.05, 0.06, 0.08, 1.0),
        "lens_dark": (0.03, 0.04, 0.06, 1.0),
        "solar_blue": (0.12, 0.20, 0.52, 1.0),
        "grid_silver": (0.72, 0.76, 0.82, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class AstronomyMarsRoverConfig:
    deck_form: DeckForm = "equipment_deck"
    mobility_module: MobilityModule = "fused_rocker_bogie"
    wheel_hub_form: WheelHubForm = "solid_disc"
    mast_module: MastModule = "rigid_mast"
    arm_module: ArmModule = "rigid_arm"
    antenna_module: AntennaModule = "az_dish"
    palette_style: RoverPalette = "nasa_white"

    wheel_radius_scale: float = 1.0
    mast_height_scale: float = 1.0
    arm_reach_scale: float = 1.0
    dish_radius_scale: float = 1.0
    steer_range: float = 0.55            # steered_corners only
    mast_deploy_upper: float = 0.95      # folding_mast only (capped so the folded head clears the HGA)
    hga_elevation_range: float = 0.55    # azel_gimbal only


@dataclass(frozen=True)
class ResolvedAstronomyMarsRoverConfig:
    deck_form: DeckForm
    mobility_module: MobilityModule
    wheel_hub_form: WheelHubForm
    mast_module: MastModule
    arm_module: ArmModule
    antenna_module: AntennaModule
    palette_style: str

    wheel_radius_scale: float
    mast_height_scale: float
    arm_reach_scale: float
    dish_radius_scale: float
    steer_range: float
    mast_deploy_upper: float
    hga_elevation_range: float

    # Derived (single-sourced).
    wheel_radius: float
    axle_z: float
    mast_height: float
    mast_yaw_range: float

    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> AstronomyMarsRoverConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin 母本 combination (equipment_deck +
    fused_rocker_bogie + solid_disc + rigid_mast + rigid_arm + az_dish,
    nasa_white) as a documented regression anchor; every other seed is fully
    procedural.
    """
    if seed == 0:
        return AstronomyMarsRoverConfig()

    rng = random.Random(seed)
    return AstronomyMarsRoverConfig(
        deck_form=rng.choice(("equipment_deck", "solar_wing_deck")),
        mobility_module=rng.choice(
            ("fused_rocker_bogie", "articulated_rocker_bogie", "steered_corners")
        ),
        wheel_hub_form=rng.choice(("solid_disc", "spoked_lattice")),
        mast_module=rng.choice(("rigid_mast", "folding_mast")),
        arm_module=rng.choice(("rigid_arm", "elbow_arm", "turret_roll_arm")),
        antenna_module=rng.choice(("az_dish", "azel_gimbal")),
        palette_style=rng.choice(PALETTE_NAMES),
        wheel_radius_scale=round(rng.uniform(0.92, 1.10), 4),
        mast_height_scale=round(rng.uniform(0.85, 1.20), 4),
        arm_reach_scale=round(rng.uniform(0.90, 1.15), 4),
        dish_radius_scale=round(rng.uniform(0.85, 1.15), 4),
        steer_range=round(rng.uniform(0.35, 0.60), 4),
        mast_deploy_upper=round(rng.uniform(0.80, 1.05), 4),
        hga_elevation_range=round(rng.uniform(0.40, 0.60), 4),
    )


def resolve_config(
    config: AstronomyMarsRoverConfig,
) -> ResolvedAstronomyMarsRoverConfig:
    if str(config.deck_form) not in {"equipment_deck", "solar_wing_deck"}:
        raise ValueError(f"Unsupported deck_form: {config.deck_form}")
    if str(config.mobility_module) not in {
        "fused_rocker_bogie", "articulated_rocker_bogie", "steered_corners"
    }:
        raise ValueError(f"Unsupported mobility_module: {config.mobility_module}")
    if str(config.wheel_hub_form) not in {"solid_disc", "spoked_lattice"}:
        raise ValueError(f"Unsupported wheel_hub_form: {config.wheel_hub_form}")
    if str(config.mast_module) not in {"rigid_mast", "folding_mast"}:
        raise ValueError(f"Unsupported mast_module: {config.mast_module}")
    if str(config.arm_module) not in {"rigid_arm", "elbow_arm", "turret_roll_arm"}:
        raise ValueError(f"Unsupported arm_module: {config.arm_module}")
    if str(config.antenna_module) not in {"az_dish", "azel_gimbal"}:
        raise ValueError(f"Unsupported antenna_module: {config.antenna_module}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    wheel_radius_scale = _clamp(config.wheel_radius_scale, 0.92, 1.10)
    mast_height_scale = _clamp(config.mast_height_scale, 0.85, 1.20)
    arm_reach_scale = _clamp(config.arm_reach_scale, 0.90, 1.15)
    dish_radius_scale = _clamp(config.dish_radius_scale, 0.85, 1.15)
    steer_range = _clamp(config.steer_range, 0.35, 0.60)
    mast_deploy_upper = _clamp(config.mast_deploy_upper, 0.80, 1.05)
    hga_elevation_range = _clamp(config.hga_elevation_range, 0.40, 0.60)

    wheel_radius = NOM_WHEEL_RADIUS * wheel_radius_scale
    mast_height = NOM_MAST_HEIGHT * mast_height_scale
    # A rigid mast head rides ~2.2 m up, clear of everything, so it pans the full
    # +/-2.8. A folding mast can stow its head down to deck-appendage height, so
    # its pan is limited so the folded head cannot swing into the HGA dish.
    mast_yaw_range = 1.9 if config.mast_module == "folding_mast" else 2.8

    return ResolvedAstronomyMarsRoverConfig(
        deck_form=config.deck_form,
        mobility_module=config.mobility_module,
        wheel_hub_form=config.wheel_hub_form,
        mast_module=config.mast_module,
        arm_module=config.arm_module,
        antenna_module=config.antenna_module,
        palette_style=config.palette_style,
        wheel_radius_scale=wheel_radius_scale,
        mast_height_scale=mast_height_scale,
        arm_reach_scale=arm_reach_scale,
        dish_radius_scale=dish_radius_scale,
        steer_range=steer_range,
        mast_deploy_upper=mast_deploy_upper,
        hga_elevation_range=hga_elevation_range,
        wheel_radius=wheel_radius,
        axle_z=wheel_radius,
        mast_height=mast_height,
        mast_yaw_range=mast_yaw_range,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Shared meshes / geometry helpers
# --------------------------------------------------------------------------- #


def _dish_mesh(radius_scale: float):
    """HGA parabolic dish, revolved profile (origin S1 L502-L511)."""
    prof = [(r * radius_scale, z) for (r, z) in DISH_PROFILE]
    return mesh_from_geometry(LatheGeometry(prof, segments=48), "hga_dish")


def _solar_grid_mesh(length: float, width: float, cell: float) -> MeshGeometry:
    """Thin raised cell-grid border lattice for a solar wing (solar_deck S9).

    A shallow lattice of ridge bars over the wing planform, built as raw faces
    so it hugs the flat wing surface (Rule 4, host-conformal)."""
    mesh = MeshGeometry()
    bar_w = 0.012
    bar_h = 0.010
    nx = max(2, int(length / cell))
    ny = max(2, int(width / cell))

    def slab(cx: float, cy: float, lx: float, ly: float) -> None:
        hx, hy = lx / 2.0, ly / 2.0
        z0, z1 = 0.0, bar_h
        corners = [
            (cx - hx, cy - hy), (cx + hx, cy - hy),
            (cx + hx, cy + hy), (cx - hx, cy + hy),
        ]
        top = [mesh.add_vertex(x, y, z1) for (x, y) in corners]
        bot = [mesh.add_vertex(x, y, z0) for (x, y) in corners]
        mesh.add_face(top[0], top[1], top[2])
        mesh.add_face(top[0], top[2], top[3])
        for i in range(4):
            j = (i + 1) % 4
            mesh.add_face(top[i], bot[j], bot[i])
            mesh.add_face(top[i], top[j], bot[j])

    for i in range(nx + 1):
        x = -length / 2.0 + i * (length / nx)
        slab(x, 0.0, bar_w, width)
    for j in range(ny + 1):
        y = -width / 2.0 + j * (width / ny)
        slab(0.0, y, length, bar_w)
    return mesh


def _build_lattice_wheel_disc(
    hub_radius: float = 0.060,
    hub_width: float = 0.14,
    rim_outer_radius: float = 0.195,
    num_spokes: int = 16,
) -> MeshGeometry:
    """Open spring-spoke lattice wheel disc (MER-style flexure wheel,
    spoked_wheel_hub S4). Disc lies in local YZ plane, width along X."""
    spoke_radius = 0.005
    rim_tube_radius = 0.009
    curve_amplitude = 0.022

    hub = CylinderGeometry(radius=hub_radius, height=hub_width, radial_segments=24, closed=True)
    hub.rotate_y(pi / 2)
    combined = hub

    rim_center_r = rim_outer_radius - rim_tube_radius
    rim = TorusGeometry(radius=rim_center_r, tube=rim_tube_radius, radial_segments=10, tubular_segments=48)
    rim.rotate_y(pi / 2)
    combined = combined.merge(rim)

    r_start = hub_radius + 0.004
    r_end = rim_outer_radius - rim_tube_radius - 0.003
    for ring_frac in (0.40, 0.72):
        ring_r = r_start + (r_end - r_start) * ring_frac
        ring = TorusGeometry(radius=ring_r, tube=spoke_radius * 0.65, radial_segments=6, tubular_segments=48)
        ring.rotate_y(pi / 2)
        combined = combined.merge(ring)

    for i in range(num_spokes):
        angle = 2.0 * pi * i / num_spokes
        n_pts = 9
        points = []
        for j in range(n_pts):
            t = j / (n_pts - 1)
            r = r_start + (r_end - r_start) * t
            tang = curve_amplitude * sin(t * pi)
            y = r * cos(angle) - tang * sin(angle)
            z = r * sin(angle) + tang * cos(angle)
            points.append((0.0, y, z))
        spoke_geom = tube_from_spline_points(points, radius=spoke_radius, samples_per_segment=5, radial_segments=8)
        combined = combined.merge(spoke_geom)
    return combined


def _wheel_meshes(r: ResolvedAstronomyMarsRoverConfig):
    """Shared tire + disc meshes reused by all 6 wheels (compile budget)."""
    tire = mesh_from_geometry(
        TireGeometry(
            r.wheel_radius, WHEEL_WIDTH, inner_radius=r.wheel_radius * 0.73,
            tread=TireTread(style="block", depth=0.014, count=24, land_ratio=0.55),
            sidewall=TireSidewall(style="square", bulge=0.02),
        ),
        "rover_tire",
    )
    if r.wheel_hub_form == "spoked_lattice":
        disc = mesh_from_geometry(
            _build_lattice_wheel_disc(
                hub_radius=0.060, hub_width=0.14,
                rim_outer_radius=r.wheel_radius * 0.75, num_spokes=16,
            ),
            "rover_wheel_disc",
        )
    else:
        disc = mesh_from_geometry(
            WheelGeometry(
                r.wheel_radius * 0.75, 0.16,
                hub=WheelHub(radius=0.060, width=0.14, cap_style="domed"),
                face=WheelFace(dish_depth=0.010, front_inset=0.008, rear_inset=0.006),
            ),
            "rover_wheel_disc",
        )
    return tire, disc


def _emit_wheel(model, parent_part, r, *, name: str, side_sign: float,
                origin_xyz: tuple[float, float, float], tire, disc) -> str:
    """A single cleated wheel part on a CONTINUOUS spin (axis Y)."""
    wheel = model.part(name)
    wheel.visual(tire, origin=Origin(rpy=(0.0, 0.0, side_sign * pi / 2.0)),
                 material="black_tread", name="tire", material_class_id="rubber.directional_grooved")
    wheel.visual(disc, origin=Origin(rpy=(0.0, 0.0, side_sign * pi / 2.0)),
                 material="dark_gray", name="wheel_disc", material_class_id="metal.blackened_gunmetal")
    wheel.visual(Cylinder(radius=r.wheel_radius * 0.63, length=0.030),
                 origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)),
                 material="dark_gray", name="wheel_web", material_class_id="metal.blackened_gunmetal")
    jn = f"{name}_spin"
    model.articulation(
        jn, ArticulationType.CONTINUOUS, parent=parent_part, child=wheel,
        origin=Origin(xyz=origin_xyz), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=45.0, velocity=6.0),
    )
    return jn


def _leg_points(kind: str, side_sign: float) -> list[tuple[float, float, float]]:
    """Rocker/bogie suspension leg spline waypoints in WORLD coords (origin
    S1 L176-L252). Single-sourced so fused/articulated share leg shape."""
    rp = (ROCKER_PIVOT[0], side_sign * ROCKER_PIVOT[1], ROCKER_PIVOT[2])
    bp = (BOGIE_PIVOT[0], side_sign * BOGIE_PIVOT[1], BOGIE_PIVOT[2])
    if kind == "rocker_front":
        return [rp, (0.70, side_sign * 0.86, 0.78), (WHEEL_ROW_X[0], side_sign * AXLE_INNER_Y, 0.55)]
    if kind == "rocker_rear":
        return [rp, (-0.12, side_sign * 0.78, 0.80), bp]
    if kind == "bogie_front":
        return [bp, (-0.18, side_sign * 0.78, 0.42), (WHEEL_ROW_X[1], side_sign * AXLE_INNER_Y, NOM_WHEEL_RADIUS)]
    if kind == "bogie_rear":
        return [bp, (-0.72, side_sign * 0.76, 0.58), (WHEEL_ROW_X[2], side_sign * AXLE_INNER_Y, 0.55)]
    raise ValueError(kind)


def _leg_mesh(name: str, pts, radius: float):
    return mesh_from_geometry(
        tube_from_spline_points(pts, radius=radius, samples_per_segment=10, radial_segments=16),
        name,
    )


def _rebase(pts, origin):
    ox, oy, oz = origin
    return [(x - ox, y - oy, z - oz) for (x, y, z) in pts]


# --------------------------------------------------------------------------- #
# Slot A — chassis body (root, ③ deck form)
# --------------------------------------------------------------------------- #


def _body_downstream() -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="body",
        visual_name="chassis_box",
        face_side="positive_z",
        anchor_local=(BODY_CENTER[0], 0.0, BODY_TOP),
        face_extents_uv=(BODY_SIZE[0], BODY_SIZE[1]),
        contact_tol=0.004,
    )


def _build_chassis(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.part("body")

    body.visual(Box(BODY_SIZE), origin=Origin(xyz=BODY_CENTER),
                material="white_panel", name="chassis_box", material_class_id="metal.paint_coated")

    if r.deck_form == "equipment_deck":
        body.visual(Box(DECK_SIZE), origin=Origin(xyz=DECK_CENTER),
                    material="warm_white", name="deck_plate", material_class_id="metal.paint_coated")
        body.visual(Box((0.50, 0.50, 0.14)), origin=Origin(xyz=(-0.40, -0.25, DECK_TOP + 0.07)),
                    material="white_panel", name="deck_equipment_box", material_class_id="metal.paint_coated")
        body.visual(Box((0.35, 0.34, 0.12)), origin=Origin(xyz=(-0.45, 0.30, DECK_TOP + 0.06)),
                    material="warm_white", name="deck_electronics_box", material_class_id="metal.paint_coated")
        body.visual(Box((0.25, 0.18, 0.10)), origin=Origin(xyz=(0.38, -0.40, DECK_TOP + 0.05)),
                    material="orange_accent", name="deck_orange_module", material_class_id="metal.paint_coated")
        body.visual(Box((0.20, 0.20, 0.12)), origin=Origin(xyz=(0.45, 0.45, DECK_TOP + 0.06)),
                    material="gray_metal", name="deck_instrument_box", material_class_id="metal.aluminum_bare")
        body.visual(Box((0.30, 0.20, 0.05)), origin=Origin(xyz=(0.08, -0.08, DECK_TOP + 0.025)),
                    material="lens_dark", name="deck_vent_grille", material_class_id="metal.mesh_chainmail")
    else:  # solar_wing_deck (MER-style flat wings) — ③ Planar Boundary Form
        # Center deck spanning the chassis width, top flush with DECK_TOP.
        body.visual(Box((WING_LENGTH, 2.0 * BODY_HALF_W, DECK_SIZE[2])),
                    origin=Origin(xyz=(BODY_CENTER[0], 0.0, DECK_CENTER[2])),
                    material="warm_white", name="solar_center_deck", material_class_id="metal.paint_coated")
        grid = mesh_from_geometry(_solar_grid_mesh(WING_LENGTH, WING_WIDTH, SOLAR_CELL_SIZE), "solar_grid")
        for side_sign, side_name in ((1.0, "left"), (-1.0, "right")):
            wing_cy = side_sign * (BODY_HALF_W + WING_WIDTH / 2.0)
            body.visual(Box((WING_LENGTH, WING_WIDTH, SOLAR_PANEL_THICKNESS)),
                        origin=Origin(xyz=(BODY_CENTER[0], wing_cy, DECK_TOP - SOLAR_PANEL_THICKNESS / 2.0)),
                        material="solar_blue", name=f"solar_wing_{side_name}", material_class_id="tech.solar_cell")
            body.visual(grid, origin=Origin(xyz=(BODY_CENTER[0], wing_cy, DECK_TOP)),
                        material="grid_silver", name=f"solar_grid_{side_name}", material_class_id="metal.brushed_silver")
            for k, strut_x in enumerate((-0.50, 0.10, 0.70)):
                by = side_sign * (BODY_HALF_W + WING_WIDTH * 0.25)
                body.visual(Box((0.05, WING_WIDTH * 0.55, 0.05)),
                            origin=Origin(xyz=(strut_x, by, BODY_TOP + 0.01)),
                            material="gray_metal", name=f"solar_wing_{side_name}_bracket_{k}", material_class_id="metal.aluminum_bare")

    # --- common body furniture (shared across deck forms) ---
    for cam_y, cam_name in ((0.25, "front_hazcam_left"), (-0.25, "front_hazcam_right")):
        body.visual(Box((0.05, 0.10, 0.08)), origin=Origin(xyz=(1.215, cam_y, 0.78)),
                    material="lens_dark", name=cam_name, material_class_id="glass.smoked_tinted")
    body.visual(Cylinder(radius=0.020, length=0.24), origin=Origin(xyz=(-0.75, 0.45, DECK_TOP + 0.12)),
                material="gray_metal", name="uhf_antenna_pole", material_class_id="metal.aluminum_bare")
    body.visual(Cylinder(radius=0.050, length=0.20), origin=Origin(xyz=(-0.75, 0.45, DECK_TOP + 0.34)),
                material="dark_gray", name="uhf_antenna_can", material_class_id="metal.blackened_gunmetal")
    body.visual(Box((0.14, 0.14, 0.12)), origin=Origin(xyz=(HGA_BASE[0], HGA_BASE[1], DECK_TOP + 0.05)),
                material="light_gray", name="hga_pedestal", material_class_id="metal.stainless_matte")
    # Bracket spans from inside the chassis front face (x=1.20) out past the
    # shoulder-yaw axis (x=ARM_SHOULDER[0]=1.32), so it both stays connected to
    # the chassis AND puts the revolute joint origin on real parent hardware.
    body.visual(Box((0.20, 0.16, 0.22)), origin=Origin(xyz=(1.26, ARM_SHOULDER[1], ARM_SHOULDER[2])),
                material="warm_white", name="arm_shoulder_bracket", material_class_id="metal.paint_coated")
    # Mast mounting boss on the deck (top flush with DECK_TOP so the mast base
    # flange rests on it without penetration).
    body.visual(Cylinder(radius=0.085, length=0.06), origin=Origin(xyz=(MAST_BASE[0], MAST_BASE[1], DECK_TOP - 0.03)),
                material="light_gray", name="mast_mount_boss", material_class_id="metal.stainless_matte")

    return ModuleBuild(
        module_name=r.deck_form,
        parts_emitted=["body"],
        interfaces={"downstream": _body_downstream()},
    )


# --------------------------------------------------------------------------- #
# Slot B — mobility (parallel children)
# --------------------------------------------------------------------------- #


def _emit_pivot_hubs(body, side_sign: float, side_name: str) -> None:
    body.visual(Cylinder(radius=0.060, length=0.12),
                origin=Origin(xyz=(ROCKER_PIVOT[0], side_sign * ROCKER_PIVOT[1], ROCKER_PIVOT[2]), rpy=(pi / 2.0, 0.0, 0.0)),
                material="light_gray", name=f"{side_name}_rocker_pivot_hub", material_class_id="metal.stainless_matte")


def _emit_axle_stub(part, r, *, name: str, row_idx: int, side_sign: float, frame_origin=(0.0, 0.0, 0.0)) -> None:
    ox, oy, oz = frame_origin
    part.visual(
        Cylinder(radius=AXLE_RADIUS, length=AXLE_LEN),
        origin=Origin(xyz=(WHEEL_ROW_X[row_idx] - ox, side_sign * AXLE_MID_OFFSET - oy, r.axle_z - oz),
                      rpy=(pi / 2.0, 0.0, 0.0)),
        material="dark_gray", name=name, material_class_id="metal.steel_bare",
    )


def _build_fused_rocker_bogie(ctx: ModuleBuildContext) -> ModuleBuild:
    """Rocker-bogie legs fused as body visuals; 6 wheels spin on body (S1)."""
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.get_part("body")

    for side_sign, side_name in ((1.0, "left"), (-1.0, "right")):
        _emit_pivot_hubs(body, side_sign, side_name)
        body.visual(_leg_mesh(f"{side_name}_rocker_front_leg", _leg_points("rocker_front", side_sign), SUSP_TUBE_R),
                    material="gray_metal", name=f"{side_name}_rocker_front_leg", material_class_id="metal.aluminum_bare")
        body.visual(_leg_mesh(f"{side_name}_rocker_rear_leg", _leg_points("rocker_rear", side_sign), SUSP_TUBE_R),
                    material="gray_metal", name=f"{side_name}_rocker_rear_leg", material_class_id="metal.aluminum_bare")
        body.visual(Cylinder(radius=0.052, length=0.10),
                    origin=Origin(xyz=(BOGIE_PIVOT[0], side_sign * BOGIE_PIVOT[1], BOGIE_PIVOT[2]), rpy=(pi / 2.0, 0.0, 0.0)),
                    material="light_gray", name=f"{side_name}_bogie_pivot_hub", material_class_id="metal.stainless_matte")
        body.visual(_leg_mesh(f"{side_name}_bogie_front_leg", _leg_points("bogie_front", side_sign), SUSP_TUBE_R * 0.9),
                    material="gray_metal", name=f"{side_name}_bogie_front_leg", material_class_id="metal.aluminum_bare")
        body.visual(_leg_mesh(f"{side_name}_bogie_rear_leg", _leg_points("bogie_rear", side_sign), SUSP_TUBE_R * 0.9),
                    material="gray_metal", name=f"{side_name}_bogie_rear_leg", material_class_id="metal.aluminum_bare")
        for row_idx, row_name in ((0, "front"), (2, "rear")):
            body.visual(Cylinder(radius=0.040, length=0.31),
                        origin=Origin(xyz=(WHEEL_ROW_X[row_idx], side_sign * AXLE_INNER_Y, 0.405)),
                        material="light_gray", name=f"{row_name}_{side_name}_steering_knuckle", material_class_id="metal.stainless_matte")
        for row_idx, row_name in enumerate(WHEEL_ROWS):
            _emit_axle_stub(body, r, name=f"{row_name}_{side_name}_axle", row_idx=row_idx, side_sign=side_sign)

    tire, disc = _wheel_meshes(r)
    joints = []
    for i in range(6):
        row = i % 3
        side_sign = 1.0 if i < 3 else -1.0
        side_name = "left" if side_sign > 0 else "right"
        name = f"{WHEEL_ROWS[row]}_{side_name}_wheel"
        joints.append(_emit_wheel(model, body, r, name=name, side_sign=side_sign,
                                  origin_xyz=(WHEEL_ROW_X[row], side_sign * WHEEL_TRACK_Y, r.axle_z),
                                  tire=tire, disc=disc))
    return ModuleBuild(module_name="fused_rocker_bogie",
                       parts_emitted=[f"{WHEEL_ROWS[i % 3]}_{'left' if i < 3 else 'right'}_wheel" for i in range(6)],
                       internal_articulations=joints,
                       interfaces={"downstream": _body_downstream()})


def _build_articulated_rocker_bogie(ctx: ModuleBuildContext) -> ModuleBuild:
    """Articulated rocker + bogie parts on REVOLUTE(Y) pivots (S2)."""
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.get_part("body")

    rocker_parts: dict[str, object] = {}
    bogie_parts: dict[str, object] = {}
    parts, joints = [], []

    for side_sign, side_name in ((1.0, "left"), (-1.0, "right")):
        rp = (ROCKER_PIVOT[0], side_sign * ROCKER_PIVOT[1], ROCKER_PIVOT[2])
        bp = (BOGIE_PIVOT[0], side_sign * BOGIE_PIVOT[1], BOGIE_PIVOT[2])
        _emit_pivot_hubs(body, side_sign, side_name)

        rocker = model.part(f"{side_name}_rocker")
        rocker_parts[side_name] = rocker
        rocker.visual(_leg_mesh(f"{side_name}_rocker_front_leg", _rebase(_leg_points("rocker_front", side_sign), rp), SUSP_TUBE_R),
                      material="gray_metal", name=f"{side_name}_rocker_front_leg", material_class_id="metal.aluminum_bare")
        rocker.visual(_leg_mesh(f"{side_name}_rocker_rear_leg", _rebase(_leg_points("rocker_rear", side_sign), rp), SUSP_TUBE_R),
                      material="gray_metal", name=f"{side_name}_rocker_rear_leg", material_class_id="metal.aluminum_bare")
        rocker.visual(Cylinder(radius=0.040, length=0.31),
                      origin=Origin(xyz=(WHEEL_ROW_X[0] - rp[0], side_sign * AXLE_INNER_Y - rp[1], 0.405 - rp[2])),
                      material="light_gray", name=f"front_{side_name}_steering_knuckle", material_class_id="metal.stainless_matte")
        _emit_axle_stub(rocker, r, name=f"front_{side_name}_axle", row_idx=0, side_sign=side_sign, frame_origin=rp)
        rocker.visual(Cylinder(radius=0.052, length=0.10),
                      origin=Origin(xyz=(bp[0] - rp[0], bp[1] - rp[1], bp[2] - rp[2]), rpy=(pi / 2.0, 0.0, 0.0)),
                      material="light_gray", name=f"{side_name}_bogie_pivot_hub", material_class_id="metal.stainless_matte")
        model.articulation(f"{side_name}_rocker_pivot", ArticulationType.REVOLUTE,
                           parent=body, child=rocker, origin=Origin(xyz=rp), axis=(0.0, 1.0, 0.0),
                           motion_limits=MotionLimits(effort=30.0, velocity=2.0, lower=-0.20, upper=0.20))
        joints.append(f"{side_name}_rocker_pivot")
        parts.append(f"{side_name}_rocker")

        bogie = model.part(f"{side_name}_bogie")
        bogie_parts[side_name] = bogie
        bogie.visual(_leg_mesh(f"{side_name}_bogie_front_leg", _rebase(_leg_points("bogie_front", side_sign), bp), SUSP_TUBE_R * 0.9),
                     material="gray_metal", name=f"{side_name}_bogie_front_leg", material_class_id="metal.aluminum_bare")
        bogie.visual(_leg_mesh(f"{side_name}_bogie_rear_leg", _rebase(_leg_points("bogie_rear", side_sign), bp), SUSP_TUBE_R * 0.9),
                     material="gray_metal", name=f"{side_name}_bogie_rear_leg", material_class_id="metal.aluminum_bare")
        bogie.visual(Cylinder(radius=0.040, length=0.31),
                     origin=Origin(xyz=(WHEEL_ROW_X[2] - bp[0], side_sign * AXLE_INNER_Y - bp[1], 0.405 - bp[2])),
                     material="light_gray", name=f"rear_{side_name}_steering_knuckle", material_class_id="metal.stainless_matte")
        _emit_axle_stub(bogie, r, name=f"middle_{side_name}_axle", row_idx=1, side_sign=side_sign, frame_origin=bp)
        _emit_axle_stub(bogie, r, name=f"rear_{side_name}_axle", row_idx=2, side_sign=side_sign, frame_origin=bp)
        model.articulation(f"{side_name}_bogie_pivot", ArticulationType.REVOLUTE,
                           parent=rocker, child=bogie,
                           origin=Origin(xyz=(bp[0] - rp[0], bp[1] - rp[1], bp[2] - rp[2])), axis=(0.0, 1.0, 0.0),
                           motion_limits=MotionLimits(effort=25.0, velocity=2.0, lower=-0.25, upper=0.25))
        joints.append(f"{side_name}_bogie_pivot")
        parts.append(f"{side_name}_bogie")

    tire, disc = _wheel_meshes(r)
    link_key = {"front": "rocker", "middle": "bogie", "rear": "bogie"}
    pivot = {"front": ROCKER_PIVOT, "middle": BOGIE_PIVOT, "rear": BOGIE_PIVOT}
    for i in range(6):
        row = i % 3
        side_sign = 1.0 if i < 3 else -1.0
        side_name = "left" if side_sign > 0 else "right"
        row_name = WHEEL_ROWS[row]
        name = f"{row_name}_{side_name}_wheel"
        parent_part = rocker_parts[side_name] if link_key[row_name] == "rocker" else bogie_parts[side_name]
        pv = pivot[row_name]
        local = (WHEEL_ROW_X[row] - pv[0], side_sign * (WHEEL_TRACK_Y - pv[1]), r.axle_z - pv[2])
        joints.append(_emit_wheel(model, parent_part, r, name=name, side_sign=side_sign,
                                  origin_xyz=local, tire=tire, disc=disc))
        parts.append(name)

    # Solve each rocker/bogie pivot's safe travel against the chassis (the legs
    # run just outboard of the chassis wall and rise into it at large angles);
    # the clearance solver clamps to what clears, exempting the captured pivot
    # overlaps (Contract 3d) instead of hand-tuning the range.
    for side_name in ("left", "right"):
        rocker_exempt = [
            ("body", f"{side_name}_rocker", f"{side_name}_rocker_pivot_hub", f"{side_name}_rocker_front_leg"),
            ("body", f"{side_name}_rocker", f"{side_name}_rocker_pivot_hub", f"{side_name}_rocker_rear_leg"),
        ]
        clamp_joint_limits(model, f"{side_name}_rocker_pivot", margin=0.01,
                           keepout=["body"], allowed_pairs=rocker_exempt, scan_steps=10)
        clamp_joint_limits(model, f"{side_name}_bogie_pivot", margin=0.01,
                           keepout=["body"], allowed_pairs=[], scan_steps=10)

    return ModuleBuild(module_name="articulated_rocker_bogie", parts_emitted=parts,
                       internal_articulations=joints, interfaces={"downstream": _body_downstream()})


def _build_steered_corners(ctx: ModuleBuildContext) -> ModuleBuild:
    """Fused legs on body + 4 corner steering-knuckle parts REVOLUTE(Z) (S3)."""
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.get_part("body")

    # Fused suspension legs + pivot hubs on the body (decoration).
    for side_sign, side_name in ((1.0, "left"), (-1.0, "right")):
        _emit_pivot_hubs(body, side_sign, side_name)
        body.visual(_leg_mesh(f"{side_name}_rocker_front_leg", _leg_points("rocker_front", side_sign), SUSP_TUBE_R),
                    material="gray_metal", name=f"{side_name}_rocker_front_leg", material_class_id="metal.aluminum_bare")
        body.visual(_leg_mesh(f"{side_name}_rocker_rear_leg", _leg_points("rocker_rear", side_sign), SUSP_TUBE_R),
                    material="gray_metal", name=f"{side_name}_rocker_rear_leg", material_class_id="metal.aluminum_bare")
        body.visual(Cylinder(radius=0.052, length=0.10),
                    origin=Origin(xyz=(BOGIE_PIVOT[0], side_sign * BOGIE_PIVOT[1], BOGIE_PIVOT[2]), rpy=(pi / 2.0, 0.0, 0.0)),
                    material="light_gray", name=f"{side_name}_bogie_pivot_hub", material_class_id="metal.stainless_matte")
        body.visual(_leg_mesh(f"{side_name}_bogie_front_leg", _leg_points("bogie_front", side_sign), SUSP_TUBE_R * 0.9),
                    material="gray_metal", name=f"{side_name}_bogie_front_leg", material_class_id="metal.aluminum_bare")
        body.visual(_leg_mesh(f"{side_name}_bogie_rear_leg", _leg_points("bogie_rear", side_sign), SUSP_TUBE_R * 0.9),
                    material="gray_metal", name=f"{side_name}_bogie_rear_leg", material_class_id="metal.aluminum_bare")
        # Middle axle stub stays on body (middle wheels are not steered).
        _emit_axle_stub(body, r, name=f"middle_{side_name}_axle", row_idx=1, side_sign=side_sign)

    knuckle_parts: dict[str, object] = {}
    parts, joints = [], []
    for row_name, row_idx, side_sign, side_name in (
        ("front", 0, 1.0, "left"), ("front", 0, -1.0, "right"),
        ("rear", 2, 1.0, "left"), ("rear", 2, -1.0, "right"),
    ):
        kn_name = f"{row_name}_{side_name}_knuckle"
        knuckle = model.part(kn_name)
        knuckle_parts[kn_name] = knuckle
        steer_origin = (WHEEL_ROW_X[row_idx], side_sign * AXLE_INNER_Y, r.axle_z)
        # Post: local origin at pivot, spans up to the fused leg terminus (0.55).
        post_z = 0.405 - r.axle_z
        knuckle.visual(Cylinder(radius=0.040, length=0.31), origin=Origin(xyz=(0.0, 0.0, post_z)),
                       material="light_gray", name=f"{row_name}_{side_name}_knuckle_post", material_class_id="metal.stainless_matte")
        knuckle.visual(Cylinder(radius=AXLE_RADIUS, length=AXLE_LEN),
                       origin=Origin(xyz=(0.0, side_sign * (AXLE_MID_OFFSET - AXLE_INNER_Y), 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
                       material="dark_gray", name=f"{row_name}_{side_name}_axle", material_class_id="metal.steel_bare")
        model.articulation(f"{row_name}_{side_name}_steer", ArticulationType.REVOLUTE,
                           parent=body, child=knuckle, origin=Origin(xyz=steer_origin), axis=(0.0, 0.0, 1.0),
                           motion_limits=MotionLimits(effort=12.0, velocity=1.0, lower=-r.steer_range, upper=r.steer_range))
        joints.append(f"{row_name}_{side_name}_steer")
        parts.append(kn_name)

    tire, disc = _wheel_meshes(r)
    for i in range(6):
        row = i % 3
        side_sign = 1.0 if i < 3 else -1.0
        side_name = "left" if side_sign > 0 else "right"
        row_name = WHEEL_ROWS[row]
        name = f"{row_name}_{side_name}_wheel"
        if row_name in ("front", "rear"):
            parent_part = knuckle_parts[f"{row_name}_{side_name}_knuckle"]
            local = (0.0, side_sign * (WHEEL_TRACK_Y - AXLE_INNER_Y), 0.0)
        else:
            parent_part = body
            local = (WHEEL_ROW_X[row], side_sign * WHEEL_TRACK_Y, r.axle_z)
        joints.append(_emit_wheel(model, parent_part, r, name=name, side_sign=side_sign,
                                  origin_xyz=local, tire=tire, disc=disc))
        parts.append(name)

    return ModuleBuild(module_name="steered_corners", parts_emitted=parts,
                       internal_articulations=joints, interfaces={"downstream": _body_downstream()})


# --------------------------------------------------------------------------- #
# Slot C — camera_mast (parallel child)
# --------------------------------------------------------------------------- #


def _emit_head(model, parent_part, r, *, tilt_origin_local: tuple[float, float, float]) -> str:
    """Stereo camera head on a head_tilt REVOLUTE(Y). Chained to the mast part
    it was passed (origin S1 L379-L414)."""
    head = model.part("mast_camera_head")
    head.visual(Cylinder(radius=0.050, length=0.10), origin=Origin(xyz=(0.0, 0.0, -0.04)),
                material="gray_metal", name="head_neck_collar", material_class_id="metal.stainless_matte")
    head.visual(Box((0.30, 0.20, 0.16)), origin=Origin(xyz=(0.02, 0.0, 0.09)),
                material="white_panel", name="head_box", material_class_id="metal.paint_coated")
    for lens_y, lens_name in ((0.06, "head_lens_left"), (-0.06, "head_lens_right")):
        head.visual(Cylinder(radius=0.032, length=0.030),
                    origin=Origin(xyz=(0.175, lens_y, 0.10), rpy=(0.0, pi / 2.0, 0.0)),
                    material="lens_dark", name=lens_name, material_class_id="glass.smoked_tinted")
    head.visual(Box((0.03, 0.08, 0.03)), origin=Origin(xyz=(0.165, 0.0, 0.025)),
                material="orange_accent", name="head_accent_bar", material_class_id="metal.paint_coated")
    model.articulation("head_tilt", ArticulationType.REVOLUTE, parent=parent_part, child=head,
                       origin=Origin(xyz=tilt_origin_local), axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(effort=6.0, velocity=1.5, lower=-0.45, upper=0.45))
    return "head_tilt"


def _build_rigid_mast(ctx: ModuleBuildContext) -> ModuleBuild:
    """Single pan/tilt mast: yaw column + tilt head (origin S1 L338-L414)."""
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    h = r.mast_height
    col_len = h - 0.04

    mast = model.part("camera_mast")
    mast.visual(Cylinder(radius=0.070, length=0.05), origin=Origin(xyz=(0.0, 0.0, 0.025)),
                material="light_gray", name="mast_base_flange", material_class_id="metal.stainless_matte")
    mast.visual(Cylinder(radius=0.045, length=col_len), origin=Origin(xyz=(0.0, 0.0, col_len / 2.0 + 0.02)),
                material="gray_metal", name="mast_column", material_class_id="metal.aluminum_bare")
    mast.visual(Cylinder(radius=0.016, length=0.26), origin=Origin(xyz=(0.0, 0.0, 0.38 * r.mast_height_scale), rpy=(pi / 2.0, 0.0, 0.0)),
                material="light_gray", name="mast_cross_handle", material_class_id="metal.stainless_matte")
    mast.visual(Box((0.09, 0.07, 0.10)), origin=Origin(xyz=(0.05, 0.0, 0.60 * r.mast_height_scale)),
                material="warm_white", name="mast_electronics_pod", material_class_id="metal.paint_coated")
    mast.visual(Cylinder(radius=0.035, length=0.10), origin=Origin(xyz=(0.0, 0.0, h - 0.03)),
                material="light_gray", name="mast_head_stub", material_class_id="metal.stainless_matte")
    model.articulation("mast_yaw", ArticulationType.REVOLUTE, parent=body, child=mast,
                       origin=Origin(xyz=MAST_BASE), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=10.0, velocity=1.5, lower=-r.mast_yaw_range, upper=r.mast_yaw_range))
    _emit_head(model, mast, r, tilt_origin_local=(0.0, 0.0, h))
    return ModuleBuild(module_name="rigid_mast",
                       parts_emitted=["camera_mast", "mast_camera_head"],
                       internal_articulations=["mast_yaw", "head_tilt"],
                       interfaces={"downstream": _body_downstream()})


def _build_folding_mast(ctx: ModuleBuildContext) -> ModuleBuild:
    """Two-segment deployable mast (folding_mast S5 L346-L456)."""
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    h = r.mast_height
    hinge_z = 0.40 * r.mast_height_scale
    lower_col_len = hinge_z - 0.02
    upper_bottom = 0.04
    upper_top = (h - 0.02) - hinge_z
    upper_col_len = upper_top - upper_bottom
    upper_col_center = (upper_top + upper_bottom) / 2.0

    lower = model.part("lower_mast")
    lower.visual(Cylinder(radius=0.070, length=0.05), origin=Origin(xyz=(0.0, 0.0, 0.025)),
                 material="light_gray", name="mast_base_flange", material_class_id="metal.stainless_matte")
    lower.visual(Cylinder(radius=0.045, length=lower_col_len), origin=Origin(xyz=(0.0, 0.0, 0.02 + lower_col_len / 2.0)),
                 material="gray_metal", name="mast_column_lower", material_class_id="metal.aluminum_bare")
    lower.visual(Cylinder(radius=0.016, length=0.26), origin=Origin(xyz=(0.0, 0.0, hinge_z * 0.55), rpy=(pi / 2.0, 0.0, 0.0)),
                 material="light_gray", name="mast_cross_handle", material_class_id="metal.stainless_matte")
    for dy, kn in ((0.040, "lower_hinge_knuckle_left"), (-0.040, "lower_hinge_knuckle_right")):
        lower.visual(Box((0.065, 0.028, 0.07)), origin=Origin(xyz=(0.0, dy, hinge_z)),
                     material="light_gray", name=kn, material_class_id="metal.stainless_matte")
    model.articulation("mast_yaw", ArticulationType.REVOLUTE, parent=body, child=lower,
                       origin=Origin(xyz=MAST_BASE), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=10.0, velocity=1.5, lower=-r.mast_yaw_range, upper=r.mast_yaw_range))

    upper = model.part("upper_mast")
    upper.visual(Cylinder(radius=0.045, length=upper_col_len), origin=Origin(xyz=(0.0, 0.0, upper_col_center)),
                 material="gray_metal", name="mast_column_upper", material_class_id="metal.aluminum_bare")
    upper.visual(Box((0.09, 0.07, 0.10)), origin=Origin(xyz=(0.05, 0.0, 0.20)),
                 material="warm_white", name="mast_electronics_pod", material_class_id="metal.paint_coated")
    upper.visual(Cylinder(radius=0.035, length=0.10), origin=Origin(xyz=(0.0, 0.0, (h - hinge_z) - 0.03)),
                 material="light_gray", name="mast_head_stub", material_class_id="metal.stainless_matte")
    upper.visual(Box((0.060, 0.050, 0.06)), origin=Origin(xyz=(0.0, 0.0, 0.03)),
                 material="gray_metal", name="upper_hinge_lug", material_class_id="metal.aluminum_bare")
    model.articulation("mast_deploy", ArticulationType.REVOLUTE, parent=lower, child=upper,
                       origin=Origin(xyz=(0.0, 0.0, hinge_z)), axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(effort=12.0, velocity=0.6, lower=0.0, upper=r.mast_deploy_upper))
    _emit_head(model, upper, r, tilt_origin_local=(0.0, 0.0, h - hinge_z))
    return ModuleBuild(module_name="folding_mast",
                       parts_emitted=["lower_mast", "upper_mast", "mast_camera_head"],
                       internal_articulations=["mast_yaw", "mast_deploy", "head_tilt"],
                       interfaces={"downstream": _body_downstream()})


# --------------------------------------------------------------------------- #
# Slot D — robotic_arm (parallel child)
# --------------------------------------------------------------------------- #


def _arm_link_mesh(name: str, pts, radius: float):
    return mesh_from_geometry(
        tube_from_spline_points(pts, radius=radius, samples_per_segment=10, radial_segments=16), name)


def _build_rigid_arm(ctx: ModuleBuildContext) -> ModuleBuild:
    """Single rigid arm w/ fused turret, shoulder yaw only (origin S1 L419-L490)."""
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    s = r.arm_reach_scale
    arm = model.part("robotic_arm")
    arm.visual(Cylinder(radius=0.055, length=0.20), origin=Origin(xyz=(0.0, 0.0, 0.0)),
               material="gray_metal", name="shoulder_hub", material_class_id="metal.stainless_matte")
    arm.visual(_arm_link_mesh("arm_upper_link", [(0.0, 0.0, 0.0), (0.26 * s, 0.0, 0.09), (0.50 * s, 0.0, 0.12)], 0.034),
               material="warm_white", name="upper_arm_link", material_class_id="metal.paint_coated")
    arm.visual(Cylinder(radius=0.050, length=0.10), origin=Origin(xyz=(0.50 * s, 0.0, 0.12), rpy=(pi / 2.0, 0.0, 0.0)),
               material="light_gray", name="elbow_hub", material_class_id="metal.stainless_matte")
    arm.visual(_arm_link_mesh("arm_forearm_link", [(0.50 * s, 0.0, 0.12), (0.72 * s, 0.0, 0.27), (0.88 * s, 0.0, 0.38)], 0.030),
               material="warm_white", name="forearm_link", material_class_id="metal.paint_coated")
    arm.visual(Cylinder(radius=0.045, length=0.09), origin=Origin(xyz=(0.88 * s, 0.0, 0.38), rpy=(pi / 2.0, 0.0, 0.0)),
               material="light_gray", name="wrist_hub", material_class_id="metal.stainless_matte")
    # Turret seats onto the wrist hub (offset derived from wrist_x so the
    # overlap is scale-invariant); drill + sensor derive from the turret.
    turret_x = 0.88 * s + 0.05
    arm.visual(Cylinder(radius=0.095, length=0.16), origin=Origin(xyz=(turret_x, 0.0, 0.38), rpy=(0.0, pi / 2.0, 0.0)),
               material="dark_gray", name="instrument_turret", material_class_id="metal.blackened_gunmetal")
    arm.visual(Cylinder(radius=0.022, length=0.10), origin=Origin(xyz=(turret_x + 0.11, 0.0, 0.38), rpy=(0.0, pi / 2.0, 0.0)),
               material="lens_dark", name="turret_drill_bit", material_class_id="metal.steel_bare")
    arm.visual(Box((0.10, 0.06, 0.06)), origin=Origin(xyz=(turret_x, 0.0, 0.49)),
               material="gray_metal", name="turret_sensor_block", material_class_id="metal.aluminum_bare")
    model.articulation("arm_shoulder_yaw", ArticulationType.REVOLUTE, parent=body, child=arm,
                       origin=Origin(xyz=ARM_SHOULDER), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=20.0, velocity=0.8, lower=-0.35, upper=0.50))
    return ModuleBuild(module_name="rigid_arm", parts_emitted=["robotic_arm"],
                       internal_articulations=["arm_shoulder_yaw"],
                       interfaces={"downstream": _body_downstream()})


def _build_elbow_arm(ctx: ModuleBuildContext) -> ModuleBuild:
    """upper_arm + forearm with an elbow REVOLUTE(Y) (multi_joint_arm S6)."""
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    s = r.arm_reach_scale
    elbow = (0.50 * s, 0.0, 0.12)

    upper = model.part("upper_arm")
    upper.visual(Cylinder(radius=0.055, length=0.20), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                 material="gray_metal", name="shoulder_hub", material_class_id="metal.stainless_matte")
    upper.visual(_arm_link_mesh("arm_upper_link", [(0.0, 0.0, 0.0), (0.26 * s, 0.0, 0.09), (0.50 * s, 0.0, 0.12)], 0.034),
                 material="warm_white", name="upper_arm_link", material_class_id="metal.paint_coated")
    model.articulation("arm_shoulder_yaw", ArticulationType.REVOLUTE, parent=body, child=upper,
                       origin=Origin(xyz=ARM_SHOULDER), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=20.0, velocity=0.8, lower=-0.35, upper=0.50))

    forearm = model.part("forearm")
    forearm.visual(Cylinder(radius=0.050, length=0.10), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
                   material="light_gray", name="elbow_hub", material_class_id="metal.stainless_matte")
    forearm.visual(_arm_link_mesh("arm_forearm_link", [(0.0, 0.0, 0.0), (0.22 * s, 0.0, 0.15), (0.38 * s, 0.0, 0.26)], 0.030),
                   material="warm_white", name="forearm_link", material_class_id="metal.paint_coated")
    forearm.visual(Cylinder(radius=0.045, length=0.09), origin=Origin(xyz=(0.38 * s, 0.0, 0.26), rpy=(pi / 2.0, 0.0, 0.0)),
                   material="light_gray", name="wrist_hub", material_class_id="metal.stainless_matte")
    turret_x = 0.38 * s + 0.05
    forearm.visual(Cylinder(radius=0.095, length=0.16), origin=Origin(xyz=(turret_x, 0.0, 0.26), rpy=(0.0, pi / 2.0, 0.0)),
                   material="dark_gray", name="instrument_turret", material_class_id="metal.blackened_gunmetal")
    forearm.visual(Cylinder(radius=0.022, length=0.10), origin=Origin(xyz=(turret_x + 0.11, 0.0, 0.26), rpy=(0.0, pi / 2.0, 0.0)),
                   material="lens_dark", name="turret_drill_bit", material_class_id="metal.steel_bare")
    forearm.visual(Box((0.10, 0.06, 0.06)), origin=Origin(xyz=(turret_x, 0.0, 0.37)),
                   material="gray_metal", name="turret_sensor_block", material_class_id="metal.aluminum_bare")
    model.articulation("arm_elbow_pitch", ArticulationType.REVOLUTE, parent=upper, child=forearm,
                       origin=Origin(xyz=elbow), axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(effort=15.0, velocity=0.6, lower=-1.4, upper=0.5))
    return ModuleBuild(module_name="elbow_arm", parts_emitted=["upper_arm", "forearm"],
                       internal_articulations=["arm_shoulder_yaw", "arm_elbow_pitch"],
                       interfaces={"downstream": _body_downstream()})


def _build_turret_roll_arm(ctx: ModuleBuildContext) -> ModuleBuild:
    """Rigid arm + separate turret on a wrist_roll CONTINUOUS(X) (turret_rotation S7)."""
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    s = r.arm_reach_scale
    wrist = (0.88 * s, 0.0, 0.38)

    arm = model.part("robotic_arm")
    arm.visual(Cylinder(radius=0.055, length=0.20), origin=Origin(xyz=(0.0, 0.0, 0.0)),
               material="gray_metal", name="shoulder_hub", material_class_id="metal.stainless_matte")
    arm.visual(_arm_link_mesh("arm_upper_link", [(0.0, 0.0, 0.0), (0.26 * s, 0.0, 0.09), (0.50 * s, 0.0, 0.12)], 0.034),
               material="warm_white", name="upper_arm_link", material_class_id="metal.paint_coated")
    arm.visual(Cylinder(radius=0.050, length=0.10), origin=Origin(xyz=(0.50 * s, 0.0, 0.12), rpy=(pi / 2.0, 0.0, 0.0)),
               material="light_gray", name="elbow_hub", material_class_id="metal.stainless_matte")
    arm.visual(_arm_link_mesh("arm_forearm_link", [(0.50 * s, 0.0, 0.12), (0.72 * s, 0.0, 0.27), (0.88 * s, 0.0, 0.38)], 0.030),
               material="warm_white", name="forearm_link", material_class_id="metal.paint_coated")
    arm.visual(Cylinder(radius=0.045, length=0.09), origin=Origin(xyz=wrist, rpy=(pi / 2.0, 0.0, 0.0)),
               material="light_gray", name="wrist_hub", material_class_id="metal.stainless_matte")
    model.articulation("arm_shoulder_yaw", ArticulationType.REVOLUTE, parent=body, child=arm,
                       origin=Origin(xyz=ARM_SHOULDER), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=20.0, velocity=0.8, lower=-0.35, upper=0.50))

    turret = model.part("instrument_turret")
    turret.visual(Cylinder(radius=0.095, length=0.16), origin=Origin(xyz=(0.11, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)),
                  material="dark_gray", name="turret_cylinder", material_class_id="metal.blackened_gunmetal")
    turret.visual(Cylinder(radius=0.022, length=0.10), origin=Origin(xyz=(0.23, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)),
                  material="lens_dark", name="turret_drill_bit", material_class_id="metal.steel_bare")
    turret.visual(Box((0.10, 0.06, 0.06)), origin=Origin(xyz=(0.11, 0.0, 0.11)),
                  material="gray_metal", name="turret_sensor_block", material_class_id="metal.aluminum_bare")
    model.articulation("wrist_roll", ArticulationType.CONTINUOUS, parent=arm, child=turret,
                       origin=Origin(xyz=wrist), axis=(1.0, 0.0, 0.0),
                       motion_limits=MotionLimits(effort=12.0, velocity=4.0))
    return ModuleBuild(module_name="turret_roll_arm", parts_emitted=["robotic_arm", "instrument_turret"],
                       internal_articulations=["arm_shoulder_yaw", "wrist_roll"],
                       interfaces={"downstream": _body_downstream()})


# --------------------------------------------------------------------------- #
# Slot E — high_gain_antenna (parallel child)
# --------------------------------------------------------------------------- #


def _build_az_dish(ctx: ModuleBuildContext) -> ModuleBuild:
    """Az-only dish: gimbal stem + fused LatheGeometry dish (origin S1 L495-L532)."""
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    hga = model.part("high_gain_antenna")
    hga.visual(Cylinder(radius=0.032, length=0.26), origin=Origin(xyz=(0.0, 0.0, 0.10)),
               material="light_gray", name="hga_gimbal_stem", material_class_id="metal.stainless_matte")
    hga.visual(_dish_mesh(r.dish_radius_scale), origin=Origin(xyz=(0.0, 0.0, 0.20), rpy=(0.42, 0.0, 0.0)),
               material="gray_metal", name="hga_dish", material_class_id="metal.aluminum_bare")
    hga.visual(Cylinder(radius=0.030, length=0.05), origin=Origin(xyz=(0.0, 0.0, 0.235), rpy=(0.42, 0.0, 0.0)),
               material="light_gray", name="hga_dish_boss", material_class_id="metal.stainless_matte")
    model.articulation("hga_azimuth", ArticulationType.REVOLUTE, parent=body, child=hga,
                       origin=Origin(xyz=HGA_BASE), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=8.0, velocity=1.0, lower=-2.6, upper=2.6))
    return ModuleBuild(module_name="az_dish", parts_emitted=["high_gain_antenna"],
                       internal_articulations=["hga_azimuth"],
                       interfaces={"downstream": _body_downstream()})


def _build_azel_gimbal(ctx: ModuleBuildContext) -> ModuleBuild:
    """Az-el 2-DOF gimbal: stem azimuth → elevation yoke carrying the dish
    (hga_elevation_gimbal S8 L495-L570)."""
    model = ctx.model
    r: ResolvedAstronomyMarsRoverConfig = ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    hga = model.part("high_gain_antenna")
    hga.visual(Cylinder(radius=0.032, length=0.22), origin=Origin(xyz=(0.0, 0.0, 0.10)),
               material="light_gray", name="hga_gimbal_stem", material_class_id="metal.stainless_matte")
    hga.visual(Cylinder(radius=0.038, length=0.04), origin=Origin(xyz=(0.0, 0.0, 0.23)),
               material="light_gray", name="hga_elevation_bearing", material_class_id="metal.stainless_matte")
    model.articulation("hga_azimuth", ArticulationType.REVOLUTE, parent=body, child=hga,
                       origin=Origin(xyz=HGA_BASE), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=8.0, velocity=1.0, lower=-2.6, upper=2.6))

    yoke = model.part("hga_elevation_yoke")
    yoke.visual(Cylinder(radius=0.018, length=0.52), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
                material="gray_metal", name="hga_yoke_axle", material_class_id="metal.stainless_matte")
    for arm_y, nm in ((0.26, "hga_yoke_arm_left"), (-0.26, "hga_yoke_arm_right")):
        yoke.visual(Cylinder(radius=0.015, length=0.14), origin=Origin(xyz=(0.0, arm_y, 0.07)),
                    material="gray_metal", name=nm, material_class_id="metal.aluminum_bare")
    yoke.visual(_dish_mesh(r.dish_radius_scale), origin=Origin(xyz=(0.0, 0.0, 0.04), rpy=(0.42, 0.0, 0.0)),
                material="gray_metal", name="hga_dish", material_class_id="metal.aluminum_bare")
    yoke.visual(Cylinder(radius=0.030, length=0.05), origin=Origin(xyz=(0.0, 0.0, 0.075), rpy=(0.42, 0.0, 0.0)),
                material="light_gray", name="hga_dish_boss", material_class_id="metal.stainless_matte")
    model.articulation("hga_elevation", ArticulationType.REVOLUTE, parent=hga, child=yoke,
                       origin=Origin(xyz=(0.0, 0.0, 0.23)), axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(effort=6.0, velocity=1.0, lower=-r.hga_elevation_range, upper=r.hga_elevation_range))
    # Solve the elevation tilt against the stem/bearing: at large down-tilt the
    # (dish_radius_scale-sized) dish rim grazes the stem, so clamp to what
    # clears, exempting the captured yoke-axle-on-bearing pivot (Contract 3d).
    clamp_joint_limits(model, "hga_elevation", margin=0.01, keepout=["high_gain_antenna"],
                       allowed_pairs=[("high_gain_antenna", "hga_elevation_yoke",
                                       "hga_elevation_bearing", "hga_yoke_axle")], scan_steps=12)
    return ModuleBuild(module_name="azel_gimbal", parts_emitted=["high_gain_antenna", "hga_elevation_yoke"],
                       internal_articulations=["hga_azimuth", "hga_elevation"],
                       interfaces={"downstream": _body_downstream()})


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

MOBILITY_FACTORIES = {
    "fused_rocker_bogie": _build_fused_rocker_bogie,
    "articulated_rocker_bogie": _build_articulated_rocker_bogie,
    "steered_corners": _build_steered_corners,
}
MAST_FACTORIES = {"rigid_mast": _build_rigid_mast, "folding_mast": _build_folding_mast}
ARM_FACTORIES = {
    "rigid_arm": _build_rigid_arm,
    "elbow_arm": _build_elbow_arm,
    "turret_roll_arm": _build_turret_roll_arm,
}
ANTENNA_FACTORIES = {"az_dish": _build_az_dish, "azel_gimbal": _build_azel_gimbal}


def _slots_for_config(r: ResolvedAstronomyMarsRoverConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="chassis", candidates={r.deck_form: _build_chassis}, anchor_choice=r.deck_form),
        SlotSpec(slot_name="mobility", candidates={r.mobility_module: MOBILITY_FACTORIES[r.mobility_module]}, anchor_choice=r.mobility_module),
        SlotSpec(slot_name="camera_mast", candidates={r.mast_module: MAST_FACTORIES[r.mast_module]}, anchor_choice=r.mast_module),
        SlotSpec(slot_name="robotic_arm", candidates={r.arm_module: ARM_FACTORIES[r.arm_module]}, anchor_choice=r.arm_module),
        SlotSpec(slot_name="high_gain_antenna", candidates={r.antenna_module: ANTENNA_FACTORIES[r.antenna_module]}, anchor_choice=r.antenna_module),
    ]


def build_astronomy_mars_rover(
    config: AstronomyMarsRoverConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="astronomy_mars_rover", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    assemble(
        model,
        slots=_slots_for_config(r),
        rng=random.Random(0),
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_astronomy_mars_rover(seed: int) -> ArticulatedObject:
    return build_astronomy_mars_rover(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("chassis", r.deck_form),
        ("mobility", r.mobility_module),
        ("wheel_hub", r.wheel_hub_form),
        ("camera_mast", r.mast_module),
        ("robotic_arm", r.arm_module),
        ("high_gain_antenna", r.antenna_module),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _wheel_names() -> list[str]:
    return [f"{row}_{side}_wheel" for side in ("left", "right") for row in WHEEL_ROWS]


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject,
                      r: ResolvedAstronomyMarsRoverConfig) -> None:
    parts = {p.name for p in model.parts}
    body = model.get_part("body")

    def part(name: str):
        return model.get_part(name) if name in parts else None

    # Captured drive-axle stub inside every wheel hub (element-scoped). The axle
    # stub lives on whichever link carries the wheel (body / rocker / bogie /
    # knuckle); allow_overlap accepts the parent-of-record for that pair.
    for name in _wheel_names():
        wheel = part(name)
        if wheel is None:
            continue
        row, side = name.split("_")[0], name.split("_")[1]
        axle = f"{row}_{side}_axle"
        # Find the axle's owner (body, a knuckle, a rocker, or a bogie).
        for owner_name in (f"{row}_{side}_knuckle", f"{side}_rocker", f"{side}_bogie", "body"):
            owner = part(owner_name)
            if owner is None:
                continue
            if any(v.name == axle for v in owner.visuals):
                ctx.allow_overlap(owner, wheel, elem_a=axle, elem_b="wheel_disc",
                                  reason="Drive axle stub captured inside the wheel hub.")
                ctx.allow_overlap(owner, wheel, elem_a=axle, elem_b="wheel_web",
                                  reason="Drive axle stub captured inside the wheel hub web.")
                break

    # Mast base flange seated into the deck mount boss.
    for mast_name in ("camera_mast", "lower_mast"):
        m = part(mast_name)
        if m is not None:
            ctx.allow_overlap(body, m, elem_a="mast_mount_boss", elem_b="mast_base_flange",
                              reason="Mast base flange seated into the deck mount boss bearing.")
    # Head neck collar captures the mast head stub (and overlaps the column top).
    head = part("mast_camera_head")
    if head is not None:
        for mast_name in ("camera_mast", "upper_mast"):
            m = part(mast_name)
            if m is None or not any(v.name == "mast_head_stub" for v in m.visuals):
                continue
            col = "mast_column" if mast_name == "camera_mast" else "mast_column_upper"
            for pe in ("mast_head_stub", col):
                for ce in ("head_neck_collar", "head_box"):
                    ctx.allow_overlap(m, head, elem_a=pe, elem_b=ce,
                                      reason="Camera head rides the mast head-tilt bearing at the column top.")
    # Folding hinge: upper lug interleaves the lower knuckles, and the two
    # columns pivot about the shared hinge edge so they graze near the pivot
    # through the fold (captured-hinge overlap, bounded by mast_deploy_upper).
    if part("upper_mast") is not None and part("lower_mast") is not None:
        lo, up = model.get_part("lower_mast"), model.get_part("upper_mast")
        for kn in ("lower_hinge_knuckle_left", "lower_hinge_knuckle_right"):
            for ce in ("upper_hinge_lug", "mast_column_upper"):
                ctx.allow_overlap(lo, up, elem_a=kn, elem_b=ce,
                                  reason="Deploy hinge knuckles interleave the upper lug / graze the upper column at the pivot through the fold.")
        for ce in ("mast_column_upper", "upper_hinge_lug"):
            ctx.allow_overlap(lo, up, elem_a="mast_column_lower", elem_b=ce,
                              reason="Upper/lower mast columns pivot about the shared deploy hinge edge; they graze at the pivot line through the fold.")

    # Shoulder hub captured inside the front shoulder bracket bearing.
    for arm_name in ("robotic_arm", "upper_arm"):
        a = part(arm_name)
        if a is not None and any(v.name == "shoulder_hub" for v in a.visuals):
            for ce in ("shoulder_hub", "upper_arm_link"):
                ctx.allow_overlap(body, a, elem_a="arm_shoulder_bracket", elem_b=ce,
                                  reason="Arm shoulder hub/link emerges from the front bracket bearing mount.")
    # Elbow bearing: forearm hub + forearm link tube meet the upper-arm link tip.
    if part("forearm") is not None and part("upper_arm") is not None:
        for ce in ("elbow_hub", "forearm_link"):
            ctx.allow_overlap(model.get_part("upper_arm"), model.get_part("forearm"),
                              elem_a="upper_arm_link", elem_b=ce,
                              reason="Elbow bearing: forearm meets the upper-arm link tip at the elbow pivot.")
    # Turret cylinder overlaps the wrist hub at the roll bearing.
    if part("instrument_turret") is not None and part("robotic_arm") is not None:
        ctx.allow_overlap(model.get_part("robotic_arm"), model.get_part("instrument_turret"),
                          elem_a="wrist_hub", elem_b="turret_cylinder",
                          reason="Instrument turret captured on the wrist-roll bearing.")

    # HGA gimbal stem seated into the deck pedestal bearing bore.
    hga = part("high_gain_antenna")
    if hga is not None:
        ctx.allow_overlap(body, hga, elem_a="hga_pedestal", elem_b="hga_gimbal_stem",
                          reason="HGA gimbal stem seated into the deck pedestal bearing bore.")
    # Elevation yoke axle captured on the stem elevation bearing.
    yoke = part("hga_elevation_yoke")
    if yoke is not None:
        ctx.allow_overlap(model.get_part("high_gain_antenna"), yoke,
                          elem_a="hga_elevation_bearing", elem_b="hga_yoke_axle",
                          reason="Elevation yoke axle captured on the stem elevation bearing.")

    # Articulated suspension pivot hubs straddle the rocker/bogie link roots.
    for side_name in ("left", "right"):
        rocker = part(f"{side_name}_rocker")
        if rocker is not None:
            for leg in (f"{side_name}_rocker_front_leg", f"{side_name}_rocker_rear_leg"):
                ctx.allow_overlap(body, rocker, elem_a=f"{side_name}_rocker_pivot_hub", elem_b=leg,
                                  reason="Rocker differential pivot hub straddles the rocker link root.")
            bogie = part(f"{side_name}_bogie")
            if bogie is not None:
                for leg in (f"{side_name}_bogie_front_leg", f"{side_name}_bogie_rear_leg"):
                    ctx.allow_overlap(rocker, bogie, elem_a=f"{side_name}_bogie_pivot_hub", elem_b=leg,
                                      reason="Bogie pivot hub straddles the bogie link root.")
                # Rocker rear leg terminates at the bogie pivot where the bogie
                # legs begin; they run alongside and overlap at the shared pivot.
                for leg in (f"{side_name}_bogie_front_leg", f"{side_name}_bogie_rear_leg"):
                    ctx.allow_overlap(rocker, bogie, elem_a=f"{side_name}_rocker_rear_leg", elem_b=leg,
                                      reason="Rocker rear leg meets the bogie legs at the shared bogie pivot.")
    # Steered corner: knuckle post top overlaps the fused leg terminus.
    for row_name in ("front", "rear"):
        for side_name in ("left", "right"):
            kn = part(f"{row_name}_{side_name}_knuckle")
            if kn is not None:
                leg = f"{side_name}_rocker_front_leg" if row_name == "front" else f"{side_name}_bogie_rear_leg"
                ctx.allow_overlap(body, kn, elem_a=leg, elem_b=f"{row_name}_{side_name}_knuckle_post",
                                  reason="Steering knuckle post interleaves the suspension leg terminus at the kingpin.")


def _center_dist(a, b) -> float:
    if a is None or b is None:
        return 0.0
    ca = [(a[0][i] + a[1][i]) / 2.0 for i in range(3)]
    cb = [(b[0][i] + b[1][i]) / 2.0 for i in range(3)]
    return math.dist(ca, cb)


def _expect_mobility(ctx, model, r) -> None:
    names = _wheel_names()
    wheels = [model.get_part(n) for n in names]
    ctx.check("rover has six wheels", len(wheels) == 6, details=f"wheels={names}")
    for name in names:
        spin = model.get_articulation(f"{name}_spin")
        ctx.check(f"{name} spin is continuous",
                  spin.articulation_type == ArticulationType.CONTINUOUS,
                  details=f"type={spin.articulation_type}")
        aabb = ctx.part_world_aabb(name)
        ctx.check(f"{name} rests on the ground plane",
                  aabb is not None and abs(aabb[0][2]) <= 0.03, details=f"aabb={aabb}")

    if r.mobility_module == "articulated_rocker_bogie":
        for side in ("left", "right"):
            rj = model.get_articulation(f"{side}_rocker_pivot")
            bj = model.get_articulation(f"{side}_bogie_pivot")
            ctx.check(f"{side}_rocker_pivot revolute", rj.articulation_type == ArticulationType.REVOLUTE)
            ctx.check(f"{side}_bogie_pivot revolute", bj.articulation_type == ArticulationType.REVOLUTE)
        # targeted: rocker pivot moves the front wheel.
        rj = model.get_articulation("left_rocker_pivot")
        rest = ctx.part_world_aabb("front_left_wheel")
        with ctx.pose({rj: 0.20}):
            moved = ctx.part_world_aabb("front_left_wheel")
        ctx.check("rocker pivot moves the front wheel", _center_dist(rest, moved) > 0.02,
                  details=f"disp={_center_dist(rest, moved):.4f}")
    elif r.mobility_module == "steered_corners":
        for row in ("front", "rear"):
            for side in ("left", "right"):
                sj = model.get_articulation(f"{row}_{side}_steer")
                ctx.check(f"{row}_{side}_steer revolute", sj.articulation_type == ArticulationType.REVOLUTE)
        # targeted: steering yaws the corner wheel.
        sj = model.get_articulation("front_left_steer")
        rest = ctx.part_world_aabb("front_left_wheel")
        with ctx.pose({sj: r.steer_range}):
            moved = ctx.part_world_aabb("front_left_wheel")
        ctx.check("steer yaws the corner wheel", _center_dist(rest, moved) > 0.01,
                  details=f"disp={_center_dist(rest, moved):.4f}")


def _expect_mast(ctx, model, r) -> None:
    for jn, jtype in (("mast_yaw", ArticulationType.REVOLUTE), ("head_tilt", ArticulationType.REVOLUTE)):
        j = model.get_articulation(jn)
        ctx.check(f"{jn} is revolute", j.articulation_type == jtype, details=f"type={j.articulation_type}")
    head = model.get_part("mast_camera_head")
    head_aabb = ctx.part_world_aabb(head)
    ctx.check("camera head sits high above the deck",
              head_aabb is not None and head_aabb[0][2] > DECK_TOP + 0.40, details=f"head={head_aabb}")
    # targeted: mast yaw rotates the forward-pointing head about the (near-coaxial)
    # yaw axis, so its forward extent swings into +Y (Y-span grows).
    yaw = model.get_articulation("mast_yaw")
    rest = ctx.part_world_aabb(head)
    with ctx.pose({yaw: math.pi / 2.0}):
        spun = ctx.part_world_aabb(head)
    ok = (rest is not None and spun is not None
          and (spun[1][1] - spun[0][1]) - (rest[1][1] - rest[0][1]) > 0.05)
    ctx.check("mast yaw slews the head", ok, details=f"rest={rest}, spun={spun}")
    if r.mast_module == "folding_mast":
        dj = model.get_articulation("mast_deploy")
        ctx.check("mast deploy is revolute", dj.articulation_type == ArticulationType.REVOLUTE)
        rest = ctx.part_world_aabb(head)
        with ctx.pose({dj: r.mast_deploy_upper}):
            deployed = ctx.part_world_aabb(head)
        ctx.check("mast deploy folds the upper segment", _center_dist(rest, deployed) > 0.05,
                  details=f"disp={_center_dist(rest, deployed):.4f}")


def _expect_arm(ctx, model, r) -> None:
    sj = model.get_articulation("arm_shoulder_yaw")
    ctx.check("shoulder yaw is revolute", sj.articulation_type == ArticulationType.REVOLUTE)
    arm_part = "upper_arm" if r.arm_module == "elbow_arm" else "robotic_arm"
    rest = ctx.part_world_aabb(arm_part)
    with ctx.pose({sj: 0.45}):
        swung = ctx.part_world_aabb(arm_part)
    ctx.check("shoulder yaw swings the arm laterally",
              rest is not None and swung is not None and (swung[1][1] - rest[1][1]) > 0.05,
              details=f"rest={rest}, swung={swung}")
    if r.arm_module == "elbow_arm":
        ej = model.get_articulation("arm_elbow_pitch")
        ctx.check("elbow is revolute", ej.articulation_type == ArticulationType.REVOLUTE)
        rest = ctx.part_world_aabb("forearm")
        with ctx.pose({ej: -1.0}):
            bent = ctx.part_world_aabb("forearm")
        ctx.check("elbow folds the forearm", _center_dist(rest, bent) > 0.05,
                  details=f"disp={_center_dist(rest, bent):.4f}")
    elif r.arm_module == "turret_roll_arm":
        wj = model.get_articulation("wrist_roll")
        ctx.check("wrist roll is continuous", wj.articulation_type == ArticulationType.CONTINUOUS)


def _expect_antenna(ctx, model, r) -> None:
    az = model.get_articulation("hga_azimuth")
    ctx.check("hga azimuth is revolute", az.articulation_type == ArticulationType.REVOLUTE)
    # Dish clears the mast when slewed toward it.
    mast_part = "lower_mast" if r.mast_module == "folding_mast" else "camera_mast"
    with ctx.pose({az: 2.2}):
        ctx.expect_gap(model.get_part(mast_part), model.get_part("high_gain_antenna"),
                       axis="x", min_gap=0.01, name="antenna dish clears the camera mast when slewed")
    if r.antenna_module == "azel_gimbal":
        el = model.get_articulation("hga_elevation")
        ctx.check("hga elevation is revolute", el.articulation_type == ArticulationType.REVOLUTE)
        yoke = model.get_part("hga_elevation_yoke")
        rest = ctx.part_element_world_aabb(yoke, elem="hga_dish")
        with ctx.pose({el: r.hga_elevation_range}):
            tilted = ctx.part_element_world_aabb(yoke, elem="hga_dish")
        ctx.check("elevation tilts the dish", _center_dist(rest, tilted) > 0.02,
                  details=f"disp={_center_dist(rest, tilted):.4f}")


def run_astronomy_mars_rover_tests(
    model: ArticulatedObject,
    config: AstronomyMarsRoverConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    _expect_mobility(ctx, model, r)
    _expect_mast(ctx, model, r)
    _expect_arm(ctx, model, r)
    _expect_antenna(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses (many DOF -> 32 cap).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "AstronomyMarsRoverConfig",
    "ResolvedAstronomyMarsRoverConfig",
    "DeckForm",
    "MobilityModule",
    "WheelHubForm",
    "MastModule",
    "ArmModule",
    "AntennaModule",
    "RoverPalette",
    "build_astronomy_mars_rover",
    "build_seeded_astronomy_mars_rover",
    "config_from_seed",
    "resolve_config",
    "run_astronomy_mars_rover_tests",
    "slot_choices_for_seed",
]
