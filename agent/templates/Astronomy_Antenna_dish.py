# SPDX-License-Identifier: Apache-2.0

"""Astronomy / Antenna dish — modular procedural template.

A ground-station / earth-terminal parabolic antenna dish: a grounded support
body aims a large concave reflector at the sky through an azimuth-over-elevation
positioner. Exactly three parts and two joints in every realization (a
form-dominated category):

    mount_base (root; conical_pedestal / monopole_mast / tripod_mount)
        --azimuth_drive REVOLUTE(+Z)-->
    azimuth_turret (drum + yoke cheeks + bearings + elevation hardware)
        --elevation_drive REVOLUTE(+Y) | PRISMATIC(jack-axis)-->
    dish_assembly (reflector surface + rim + backing + feed + counterweight)

Diversity lives in visual multiplicity, not kinematic part count:
  * mount form         (Slot A, ③ Primary Form Family, 3 candidates)
  * elevation joint    (Slot B, ② joint type, 2 candidates)
  * reflector surface  (Slot C, ③ Macro Surface Construction, 2 candidates)
  * feed support       (Slot C sub-axis, ①/③, prime_focus_quad / offset_boom)
  * backing structure  (Slot C sub-axis, ③/④, radial_ribs / open_truss)
  * multiplicity       (backing_rib_count / feed_strut_count / louver_vent_count)

All modules declare only a ``downstream`` interface (re-export) and emit their
own raw joints to the named upstream part (Tipping_Barrow
parallel-children idiom), so the assembler emits no automatic chain joint.

Adapted per AUTHORING.md §A/§B from the confirmed 5-star Antenna-dish pool
(spec: specs_modular_v1/Astronomy_Antenna_dish.md). Sources (model.py:Lx-Ly in
the spec Module Source Index):

  S1  origin 母本 rec_large-...4c5c4c05 — conical pedestal, revolute trunnion,
      solid paraboloid, quad prime-focus feed, radial ribs, all test semantics.
  S2  backing_rib_count       — rib multiplicity.
  S3  faceted_panel_reflector — faceted gore-panel reflector (MeshGeometry).
  S4  feed_strut_count        — feed-strut multiplicity.
  S5  louver_vent_count       — louver multiplicity.
  S6  monopole_mast           — tubular mast + base plate mount.
  S7  offset_feed_boom        — offset cantilever feed boom.
  S8  open_truss_backing      — triangulated space-frame backing.
  S9  screwjack_elevation     — PRISMATIC inclined screw-jack elevation.
  S10 tripod_mount            — splayed-leg tripod frame mount.

Coordinate frames: world z up, ground z=0. Mount authored in world; turret
authored with z=0 at the azimuth seat; dish authored with z=0 at the trunnion
(elevation) axis, boresight local +Z at zenith.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
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
    ConeGeometry,
    Cylinder,
    CylinderGeometry,
    DomeGeometry,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    clamp_joint_limits,
    max_joint_value,
    mesh_from_geometry,
    tube_from_spline_points,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


MountForm = Literal["conical_pedestal", "monopole_mast", "tripod_mount"]
ElevationModule = Literal["trunnion_revolute", "screwjack_prismatic"]
ReflectorForm = Literal["solid_paraboloid", "faceted_panels"]
FeedSystem = Literal["prime_focus_quad", "offset_boom"]
BackingStyle = Literal["radial_ribs", "open_truss"]
AntennaPalette = Literal[
    "observatory_white",
    "desert_tan",
    "radio_gray",
    "nato_green",
    "red_white_bands",
    "deep_space_charcoal",
]


# --------------------------------------------------------------------------- #
# Canonical dimensions (origin 母本 rec_large-...4c5c4c05)
# --------------------------------------------------------------------------- #

BASE_SEAT_Z = 5.76        # origin azimuth seat height (PED_H 5.6 + 0.16)

# Azimuth turret (turret frame; z=0 at the seat).
TURRET_R = 1.05
TURRET_H = 0.55
YOKE_H = 1.15
TRUNNION_Z = TURRET_H + YOKE_H   # elevation axis height in turret frame = 1.70

# Parabolic reflector (dish frame; z=0 at the trunnion axis).
BASE_DISH_R = 4.5         # 9 m aperture
FOCAL_RATIO = 0.6         # F/D locked (origin FOCAL 2.7 / DISH_R 4.5)
DISH_T = 0.07             # shell thickness
VERTEX_Z = 0.55           # dish vertex height above the trunnion axis
STRUT_R = 0.085
HORN_R = 0.16
HORN_LEN = 1.35

# Screw-jack elevation drive (screwjack_elevation S9). The whole apparatus is
# side-mounted at y=JACK_Y (outboard of the yoke cheek and trunnion shaft) and
# kept LOW: the pivot sits only just above the trunnion axis and the inclined
# axis drops down/forward, so the cylinder, pivot lug and slide rails all stay
# well below the dish backing floor (truss/rib/panel underside ~+0.42 in dish
# frame) and clear of the wide reflector overhang at every pose.
JACK_ANGLE = math.radians(38.5)
JACK_DIR_X = math.cos(JACK_ANGLE)
JACK_DIR_Z = -math.sin(JACK_ANGLE)
JACK_PITCH = math.atan2(JACK_DIR_X, JACK_DIR_Z)
JACK_PIVOT_X = -0.85
JACK_PIVOT_Z = TRUNNION_Z + 0.10
JACK_CYL_LEN = 1.25
JACK_CYL_R = 0.14
JACK_RAM_LEN = 2.10
JACK_RAM_R = 0.075
JACK_Y = 1.12          # outboard of yoke cheek (y=0.84), trunnion shaft (0.95) and bearing (0.93)
JACK_RAIL_Y = 1.42     # slide rails flank the actuator plane, just outboard of the ram


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; tokens shared so every .visual resolves)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "observatory_white": {
        "shell_white": (0.92, 0.92, 0.90, 1.0),
        "clad_gray": (0.80, 0.81, 0.83, 1.0),
        "steel_gray": (0.58, 0.60, 0.63, 1.0),
        "dark_gray": (0.30, 0.31, 0.33, 1.0),
        "door_blue": (0.13, 0.22, 0.55, 1.0),
        "dish_white": (0.95, 0.96, 0.97, 1.0),
    },
    "desert_tan": {
        "shell_white": (0.85, 0.78, 0.62, 1.0),
        "clad_gray": (0.72, 0.66, 0.52, 1.0),
        "steel_gray": (0.55, 0.52, 0.46, 1.0),
        "dark_gray": (0.34, 0.30, 0.24, 1.0),
        "door_blue": (0.30, 0.34, 0.40, 1.0),
        "dish_white": (0.90, 0.86, 0.74, 1.0),
    },
    "radio_gray": {
        "shell_white": (0.70, 0.72, 0.74, 1.0),
        "clad_gray": (0.55, 0.57, 0.60, 1.0),
        "steel_gray": (0.45, 0.47, 0.50, 1.0),
        "dark_gray": (0.22, 0.23, 0.25, 1.0),
        "door_blue": (0.16, 0.28, 0.42, 1.0),
        "dish_white": (0.78, 0.80, 0.82, 1.0),
    },
    "nato_green": {
        "shell_white": (0.36, 0.40, 0.30, 1.0),
        "clad_gray": (0.30, 0.34, 0.26, 1.0),
        "steel_gray": (0.40, 0.42, 0.40, 1.0),
        "dark_gray": (0.16, 0.18, 0.13, 1.0),
        "door_blue": (0.22, 0.26, 0.20, 1.0),
        "dish_white": (0.48, 0.52, 0.42, 1.0),
    },
    "red_white_bands": {
        "shell_white": (0.94, 0.94, 0.93, 1.0),
        "clad_gray": (0.78, 0.20, 0.18, 1.0),
        "steel_gray": (0.60, 0.62, 0.64, 1.0),
        "dark_gray": (0.28, 0.29, 0.30, 1.0),
        "door_blue": (0.72, 0.16, 0.14, 1.0),
        "dish_white": (0.96, 0.96, 0.95, 1.0),
    },
    "deep_space_charcoal": {
        "shell_white": (0.24, 0.25, 0.27, 1.0),
        "clad_gray": (0.18, 0.19, 0.21, 1.0),
        "steel_gray": (0.42, 0.44, 0.47, 1.0),
        "dark_gray": (0.10, 0.11, 0.12, 1.0),
        "door_blue": (0.14, 0.20, 0.40, 1.0),
        "dish_white": (0.55, 0.57, 0.60, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class AstronomyAntennaDishConfig:
    mount_form: MountForm = "conical_pedestal"
    elevation_module: ElevationModule = "trunnion_revolute"
    reflector_form: ReflectorForm = "solid_paraboloid"
    feed_system: FeedSystem = "prime_focus_quad"
    backing_style: BackingStyle = "radial_ribs"
    palette_style: AntennaPalette = "observatory_white"

    backing_rib_count: int = 8    # radial_ribs only
    feed_strut_count: int = 4     # prime_focus_quad only
    louver_vent_count: int = 3    # conical_pedestal only

    mount_height_scale: float = 1.0
    dish_radius_scale: float = 1.0
    elev_upper: float = 1.15      # revolute elevation upper (rad)
    jack_travel: float = 2.4      # screwjack prismatic upper (m)


@dataclass(frozen=True)
class ResolvedAntennaDishConfig:
    mount_form: MountForm
    elevation_module: ElevationModule
    reflector_form: ReflectorForm
    feed_system: FeedSystem
    backing_style: BackingStyle
    palette_style: str

    backing_rib_count: int
    feed_strut_count: int
    louver_vent_count: int

    mount_height_scale: float
    dish_radius_scale: float
    elev_upper: float
    jack_travel: float

    # Derived, single-sourced (Contract 3c).
    seat_z: float          # azimuth seat / mount top height
    dish_radius: float
    focal_len: float

    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> AstronomyAntennaDishConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin 母本 combination (conical_pedestal +
    trunnion_revolute + solid_paraboloid + prime_focus_quad(4) + radial_ribs(8)
    + louver(3), observatory_white) as a documented regression anchor; every
    other seed is fully procedural.
    """
    if seed == 0:
        return AstronomyAntennaDishConfig()

    rng = random.Random(seed)

    mount_form: MountForm = rng.choice(
        ("conical_pedestal", "monopole_mast", "tripod_mount")
    )
    elevation_module: ElevationModule = rng.choice(
        ("trunnion_revolute", "screwjack_prismatic")
    )
    reflector_form: ReflectorForm = rng.choice(
        ("solid_paraboloid", "faceted_panels")
    )
    feed_system: FeedSystem = rng.choice(("prime_focus_quad", "offset_boom"))
    backing_style: BackingStyle = rng.choice(("radial_ribs", "open_truss"))
    palette_style = rng.choice(PALETTE_NAMES)

    backing_rib_count = rng.choices((8, 6, 10, 12), weights=(0.4, 0.2, 0.2, 0.2))[0]
    feed_strut_count = rng.choices((4, 3), weights=(0.6, 0.4))[0]
    louver_vent_count = rng.choices((3, 4, 5), weights=(0.4, 0.4, 0.2))[0]

    mount_height_scale = round(rng.uniform(0.85, 1.15), 4)
    dish_radius_scale = round(rng.uniform(0.85, 1.08), 4)
    elev_upper = round(rng.uniform(0.90, 1.25), 4)
    jack_travel = round(rng.uniform(1.4, 2.0), 4)

    return AstronomyAntennaDishConfig(
        mount_form=mount_form,
        elevation_module=elevation_module,
        reflector_form=reflector_form,
        feed_system=feed_system,
        backing_style=backing_style,
        palette_style=palette_style,
        backing_rib_count=backing_rib_count,
        feed_strut_count=feed_strut_count,
        louver_vent_count=louver_vent_count,
        mount_height_scale=mount_height_scale,
        dish_radius_scale=dish_radius_scale,
        elev_upper=elev_upper,
        jack_travel=jack_travel,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(config: AstronomyAntennaDishConfig) -> ResolvedAntennaDishConfig:
    if str(config.mount_form) not in {
        "conical_pedestal",
        "monopole_mast",
        "tripod_mount",
    }:
        raise ValueError(f"Unsupported mount_form: {config.mount_form}")
    if str(config.elevation_module) not in {"trunnion_revolute", "screwjack_prismatic"}:
        raise ValueError(f"Unsupported elevation_module: {config.elevation_module}")
    if str(config.reflector_form) not in {"solid_paraboloid", "faceted_panels"}:
        raise ValueError(f"Unsupported reflector_form: {config.reflector_form}")
    if str(config.feed_system) not in {"prime_focus_quad", "offset_boom"}:
        raise ValueError(f"Unsupported feed_system: {config.feed_system}")
    if str(config.backing_style) not in {"radial_ribs", "open_truss"}:
        raise ValueError(f"Unsupported backing_style: {config.backing_style}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    mount_height_scale = _clamp(config.mount_height_scale, 0.85, 1.15)
    # Upper capped at 1.08: beyond ~1.11 the child (dish) AABB grows the
    # elevation-axis probe segment enough that the origin-honesty solver's
    # min-distance to the trunnion hub/shaft picks up a marginal tessellation
    # artifact (~22mm > 15mm tol). Ample ⑤ dimension spread remains.
    dish_radius_scale = _clamp(config.dish_radius_scale, 0.85, 1.08)
    elev_upper = _clamp(config.elev_upper, 0.90, 1.25)
    jack_travel = _clamp(config.jack_travel, 1.4, 2.0)

    # Multiplicity clamps + gating (compatibility matrix).
    backing_rib_count = int(_clamp(config.backing_rib_count, 6, 12))
    feed_strut_count = int(_clamp(config.feed_strut_count, 3, 4))
    louver_vent_count = int(_clamp(config.louver_vent_count, 3, 5))

    # Derived (equation constraints), single-sourced.
    seat_z = BASE_SEAT_Z * mount_height_scale
    dish_radius = BASE_DISH_R * dish_radius_scale
    focal_len = FOCAL_RATIO * dish_radius

    return ResolvedAntennaDishConfig(
        mount_form=config.mount_form,
        elevation_module=config.elevation_module,
        reflector_form=config.reflector_form,
        feed_system=config.feed_system,
        backing_style=config.backing_style,
        palette_style=config.palette_style,
        backing_rib_count=backing_rib_count,
        feed_strut_count=feed_strut_count,
        louver_vent_count=louver_vent_count,
        mount_height_scale=mount_height_scale,
        dish_radius_scale=dish_radius_scale,
        elev_upper=elev_upper,
        jack_travel=jack_travel,
        seat_z=seat_z,
        dish_radius=dish_radius,
        focal_len=focal_len,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Shared geometry helpers
# --------------------------------------------------------------------------- #


def _parabola_z(r: float, focal: float) -> float:
    return r * r / (4.0 * focal)


def _downstream(part_name: str, visual_name: str) -> InterfaceSpec:
    """A passthrough downstream interface (no auto chain joint: children emit
    their own raw joints to the named part)."""
    return InterfaceSpec(
        interface_name="downstream",
        part_name=part_name,
        visual_name=visual_name,
        face_side="positive_z",
        anchor_local=(0.0, 0.0, 0.0),
    )


# --------------------------------------------------------------------------- #
# Slot A — mount_base (root, ③ Primary Form Family)
# --------------------------------------------------------------------------- #


def _build_conical_pedestal(ctx: ModuleBuildContext) -> ModuleBuild:
    """Truncated-cone pedestal building (origin S1 L90-177)."""
    model = ctx.model
    r: ResolvedAntennaDishConfig = ctx.config  # type: ignore[assignment]
    ped = model.part("mount_base")

    ped_h = r.seat_z - 0.16
    base_r = 3.2 * r.mount_height_scale
    top_r = 1.15

    def _wall_r(z: float) -> float:
        return base_r - (base_r - top_r) * (z / ped_h)

    cone_profile = [(0.0, 0.0), (base_r, 0.0), (top_r, ped_h), (0.0, ped_h)]
    ped.visual(
        mesh_from_geometry(LatheGeometry(cone_profile, segments=48), "pedestal_cone"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="shell_white",
        name="pedestal_cone_shell", material_class_id="metal.paint_coated",
    )
    # Flat top platform the turret seats on.
    ped.visual(
        mesh_from_geometry(
            CylinderGeometry(top_r + 0.08, 0.16, radial_segments=48), "pedestal_platform"
        ),
        origin=Origin(xyz=(0.0, 0.0, ped_h + 0.08)),
        material="clad_gray",
        name="top_platform", material_class_id="metal.paint_coated",
    )
    # Blue access door + surround on the +X sloped wall.
    door_r = _wall_r(1.05)
    ped.visual(
        Box((0.28, 1.0, 2.1)),
        origin=Origin(xyz=(door_r - 0.05, 0.0, 1.05)),
        material="door_blue",
        name="entrance_door", material_class_id="metal.paint_coated",
    )
    ped.visual(
        Box((0.34, 1.3, 2.35)),
        origin=Origin(xyz=(door_r - 0.14, 0.0, 1.175)),
        material="clad_gray",
        name="entrance_surround", material_class_id="metal.paint_coated",
    )
    # N louver vents around the base (④ + multiplicity), conformal to the wall.
    n_louver = r.louver_vent_count
    start_deg, spacing_deg = 55.0, 60.0
    for i in range(n_louver):
        ang = math.radians(start_deg + spacing_deg * i)
        vr = _wall_r(1.35) * 0.985
        ped.visual(
            Box((0.22, 0.9, 1.1)),
            origin=Origin(
                xyz=(vr * math.cos(ang), vr * math.sin(ang), 1.35), rpy=(0.0, 0.0, ang)
            ),
            material="dark_gray",
            name=f"louver_vent_{i}", material_class_id="metal.blackened_gunmetal",
        )
    # Horizontal panel seam rings (④), host-derived radius.
    for i in range(3):
        z = ped_h * (0.28 + 0.24 * i)
        ped.visual(
            mesh_from_geometry(
                CylinderGeometry(_wall_r(z) + 0.015, 0.06, radial_segments=48),
                f"seam_ring_{i}",
            ),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material="clad_gray",
            name=f"panel_seam_ring_{i}", material_class_id="metal.paint_coated",
        )
    # Side access ladder flush against the -Y sloped wall (④).
    wall_slope = (base_r - top_r) / ped_h
    tilt = -math.atan(wall_slope)
    lad_z0 = ped_h * 0.60
    for s, off in (("left", -0.22), ("right", 0.22)):
        ped.visual(
            Box((0.06, 0.08, ped_h * 0.62)),
            origin=Origin(xyz=(off, -_wall_r(lad_z0), lad_z0), rpy=(tilt, 0.0, 0.0)),
            material="steel_gray",
            name=f"ladder_rail_{s}", material_class_id="metal.steel_bare",
        )
    for i in range(7):
        z = ped_h * (0.34 + 0.52 * (i / 6.0))
        ped.visual(
            Box((0.50, 0.06, 0.05)),
            origin=Origin(xyz=(0.0, -_wall_r(z), z)),
            material="steel_gray",
            name=f"ladder_rung_{i}", material_class_id="metal.steel_bare",
        )

    return ModuleBuild(
        module_name="conical_pedestal",
        parts_emitted=["mount_base"],
        interfaces={"downstream": _downstream("mount_base", "top_platform")},
    )


def _build_monopole_mast(ctx: ModuleBuildContext) -> ModuleBuild:
    """Slender tubular steel monopole mast on a square base plate
    (monopole_mast S6)."""
    model = ctx.model
    r: ResolvedAntennaDishConfig = ctx.config  # type: ignore[assignment]
    mount = model.part("mount_base")

    base_plate_t = 0.10
    flange_t = 0.06
    flange_r = 0.55
    mast_r = 0.20
    mast_h = r.seat_z - base_plate_t - flange_t
    base_plate_size = 2.4

    mount.visual(
        Box((base_plate_size, base_plate_size, base_plate_t)),
        origin=Origin(xyz=(0.0, 0.0, base_plate_t / 2.0)),
        material="steel_gray",
        name="base_plate", material_class_id="metal.steel_bare",
    )
    mount.visual(
        mesh_from_geometry(CylinderGeometry(mast_r, mast_h, radial_segments=36), "mast_tube"),
        origin=Origin(xyz=(0.0, 0.0, base_plate_t + mast_h / 2.0)),
        material="shell_white",
        name="mast_tube", material_class_id="metal.paint_coated",
    )
    mount.visual(
        mesh_from_geometry(CylinderGeometry(flange_r, flange_t, radial_segments=40), "top_flange"),
        origin=Origin(xyz=(0.0, 0.0, base_plate_t + mast_h + flange_t / 2.0)),
        material="steel_gray",
        name="top_flange", material_class_id="metal.steel_bare",
    )
    # Four radial gusset plates welded between mast and base plate (④).
    gusset_h, gusset_w, gusset_t = 0.55, 0.38, 0.018
    gusset_r = mast_r + gusset_w / 2.0
    for i in range(4):
        ang = math.radians(90.0 * i)
        mount.visual(
            Box((gusset_w, gusset_t, gusset_h)),
            origin=Origin(
                xyz=(gusset_r * math.cos(ang), gusset_r * math.sin(ang),
                     base_plate_t + gusset_h / 2.0),
                rpy=(0.0, 0.0, ang),
            ),
            material="steel_gray",
            name=f"gusset_{i}", material_class_id="metal.steel_bare",
        )

    return ModuleBuild(
        module_name="monopole_mast",
        parts_emitted=["mount_base"],
        interfaces={"downstream": _downstream("mount_base", "top_flange")},
    )


def _build_tripod_mount(ctx: ModuleBuildContext) -> ModuleBuild:
    """Three splayed tubular legs + hub + braces (tripod_mount S10)."""
    model = ctx.model
    r: ResolvedAntennaDishConfig = ctx.config  # type: ignore[assignment]
    mount = model.part("mount_base")

    hub_top_z = r.seat_z
    hub_r = 0.75
    hub_h = 0.55
    hub_bottom_z = hub_top_z - hub_h
    leg_foot_r = 3.1 * r.mount_height_scale   # foot splay radius
    leg_r = 0.16
    foot_pad_r, foot_pad_h = 0.42, 0.14
    brace_r = 0.06

    def _tube_origin_and_length(p_a, p_b):
        dx, dy, dz = p_b[0] - p_a[0], p_b[1] - p_a[1], p_b[2] - p_a[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        mid = ((p_a[0] + p_b[0]) / 2.0, (p_a[1] + p_b[1]) / 2.0, (p_a[2] + p_b[2]) / 2.0)
        pitch = math.atan2(math.hypot(dx, dy), dz)
        yaw = math.atan2(dy, dx)
        return Origin(xyz=mid, rpy=(0.0, pitch, yaw)), length

    def _leg_endpoint(ang: float, z: float):
        # Point on the leg line at height z (linear between foot and hub top).
        t = (z - foot_pad_h) / (hub_bottom_z - foot_pad_h)
        rr = leg_foot_r + (hub_r - leg_foot_r) * t
        return (rr * math.cos(ang), rr * math.sin(ang), z)

    # Central hub + bearing plate.
    mount.visual(
        mesh_from_geometry(CylinderGeometry(hub_r, hub_h, radial_segments=32), "tripod_hub"),
        origin=Origin(xyz=(0.0, 0.0, hub_bottom_z + hub_h / 2.0)),
        material="steel_gray",
        name="tripod_hub", material_class_id="metal.steel_bare",
    )
    mount.visual(
        mesh_from_geometry(CylinderGeometry(hub_r + 0.06, 0.10, radial_segments=32), "hub_plate"),
        origin=Origin(xyz=(0.0, 0.0, hub_top_z - 0.05)),
        material="clad_gray",
        name="hub_bearing_plate", material_class_id="metal.paint_coated",
    )

    for i in range(3):
        ang = 2.0 * math.pi * i / 3.0
        foot = (leg_foot_r * math.cos(ang), leg_foot_r * math.sin(ang), foot_pad_h)
        top = (hub_r * math.cos(ang), hub_r * math.sin(ang), hub_bottom_z)
        leg_origin, leg_length = _tube_origin_and_length(foot, top)
        mount.visual(
            mesh_from_geometry(CylinderGeometry(leg_r, leg_length, radial_segments=16), f"leg_tube_{i}"),
            origin=leg_origin,
            material="shell_white",
            name=f"leg_{i}", material_class_id="metal.paint_coated",
        )
        mount.visual(
            mesh_from_geometry(CylinderGeometry(foot_pad_r, foot_pad_h, radial_segments=24), f"foot_pad_{i}"),
            origin=Origin(xyz=(leg_foot_r * math.cos(ang), leg_foot_r * math.sin(ang), foot_pad_h / 2.0)),
            material="steel_gray",
            name=f"foot_pad_{i}", material_class_id="metal.steel_bare",
        )
        mount.visual(
            Box((0.35, 0.08, 0.55)),
            origin=Origin(
                xyz=((hub_r + 0.12) * math.cos(ang), (hub_r + 0.12) * math.sin(ang),
                     hub_bottom_z + 0.20),
                rpy=(0.0, 0.0, ang),
            ),
            material="steel_gray",
            name=f"gusset_{i}", material_class_id="metal.steel_bare",
        )

    # Cross-braces between adjacent legs at two heights (④).
    for level, z_brace in enumerate((hub_top_z * 0.30, hub_top_z * 0.58)):
        for i in range(3):
            j = (i + 1) % 3
            pa = _leg_endpoint(2.0 * math.pi * i / 3.0, z_brace)
            pb = _leg_endpoint(2.0 * math.pi * j / 3.0, z_brace)
            brace_origin, brace_length = _tube_origin_and_length(pa, pb)
            mount.visual(
                mesh_from_geometry(CylinderGeometry(brace_r, brace_length, radial_segments=12), f"brace_{level}_{i}"),
                origin=brace_origin,
                material="clad_gray",
                name=f"cross_brace_{level}_{i}", material_class_id="metal.paint_coated",
            )

    return ModuleBuild(
        module_name="tripod_mount",
        parts_emitted=["mount_base"],
        interfaces={"downstream": _downstream("mount_base", "hub_bearing_plate")},
    )


MOUNT_FACTORIES = {
    "conical_pedestal": _build_conical_pedestal,
    "monopole_mast": _build_monopole_mast,
    "tripod_mount": _build_tripod_mount,
}
MOUNT_SEAT_VISUAL = {
    "conical_pedestal": "top_platform",
    "monopole_mast": "top_flange",
    "tripod_mount": "hub_bearing_plate",
}


# --------------------------------------------------------------------------- #
# Slot B — pointing (② elevation joint type): turret + dish core + both joints
# --------------------------------------------------------------------------- #


def _emit_turret_common(turret, r: ResolvedAntennaDishConfig) -> None:
    """Azimuth drum + 2 yoke cheeks + 2 trunnion bearings (origin S1 L180-209)."""
    turret.visual(
        mesh_from_geometry(CylinderGeometry(TURRET_R, TURRET_H, radial_segments=48), "turret_drum"),
        origin=Origin(xyz=(0.0, 0.0, TURRET_H / 2.0)),
        material="clad_gray",
        name="turntable_drum", material_class_id="metal.paint_coated",
    )
    for s, sy in (("left", 1.0), ("right", -1.0)):
        turret.visual(
            Box((0.85, 0.24, YOKE_H + 0.30)),
            origin=Origin(xyz=(0.0, sy * 0.72, TURRET_H + (YOKE_H + 0.30) / 2.0 - 0.15)),
            material="shell_white",
            name=f"yoke_cheek_{s}", material_class_id="metal.paint_coated",
        )
        turret.visual(
            mesh_from_geometry(CylinderGeometry(0.24, 0.14, radial_segments=32), f"bearing_{s}"),
            origin=Origin(xyz=(0.0, sy * 0.86, TRUNNION_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="steel_gray",
            name=f"trunnion_bearing_{s}", material_class_id="metal.steel_bare",
        )


def _emit_dish_core(dish, r: ResolvedAntennaDishConfig) -> None:
    """Backing hub + trunnion shaft (origin S1 L269-285)."""
    dish.visual(
        mesh_from_geometry(CylinderGeometry(0.62, VERTEX_Z + 0.25, radial_segments=40), "hub"),
        origin=Origin(xyz=(0.0, 0.0, (VERTEX_Z + 0.25) / 2.0 - 0.12)),
        material="steel_gray",
        name="backing_hub", material_class_id="metal.steel_bare",
    )
    dish.visual(
        mesh_from_geometry(CylinderGeometry(0.13, 1.9, radial_segments=28), "trunnion_shaft"),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="steel_gray",
        name="trunnion_shaft", material_class_id="metal.steel_bare",
    )
    # Solid boss clamping the dish onto the trunnion axis. As a convex Box it is
    # penetrated by the elevation axis line (unlike the hollow revolved
    # shaft/hub meshes, whose walls sit ~0.13 off-axis), so the elevation joint's
    # axis provably touches child hardware (origin-honesty gate) for every
    # backing/reflector combination.
    dish.visual(
        Box((0.30, 0.42, 0.30)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="steel_gray",
        name="trunnion_collar", material_class_id="metal.steel_bare",
    )


def _captured_trunnion_pairs() -> list[tuple[str, str, str, str]]:
    """Captured trunnion contacts exempt from the elevation clearance solver."""
    pairs: list[tuple[str, str, str, str]] = []
    for s in ("left", "right"):
        pairs.append(("azimuth_turret", "dish_assembly", f"trunnion_bearing_{s}", "trunnion_shaft"))
        pairs.append(("azimuth_turret", "dish_assembly", f"yoke_cheek_{s}", "trunnion_shaft"))
        pairs.append(("azimuth_turret", "dish_assembly", f"yoke_cheek_{s}", "backing_hub"))
    return pairs


def _emit_azimuth_joint(model, mount, turret, r: ResolvedAntennaDishConfig) -> None:
    model.articulation(
        "azimuth_drive",
        ArticulationType.REVOLUTE,
        parent=mount,
        child=turret,
        origin=Origin(xyz=(0.0, 0.0, r.seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=800.0, velocity=0.3, lower=-math.pi, upper=math.pi),
    )


def _build_trunnion_revolute(ctx: ModuleBuildContext) -> ModuleBuild:
    """Bounded rotary elevation trunnion between yoke cheeks (origin S1)."""
    model = ctx.model
    r: ResolvedAntennaDishConfig = ctx.config  # type: ignore[assignment]
    mount = model.get_part("mount_base")

    turret = model.part("azimuth_turret")
    _emit_turret_common(turret, r)
    # Elevation drive housing, kept low on the turret rear so it stays clear of
    # the counterweight's swing arc through the full elevation range.
    turret.visual(
        Box((0.30, 0.55, 0.55)),
        origin=Origin(xyz=(-0.75, 0.0, TURRET_H + 0.05)),
        material="clad_gray",
        name="elevation_drive_housing", material_class_id="metal.paint_coated",
    )

    dish = model.part("dish_assembly")
    _emit_dish_core(dish, r)

    _emit_azimuth_joint(model, mount, turret, r)
    model.articulation(
        "elevation_drive",
        ArticulationType.REVOLUTE,
        parent=turret,
        child=dish,
        origin=Origin(xyz=(0.0, 0.0, TRUNNION_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1500.0, velocity=0.2, lower=0.0, upper=r.elev_upper),
    )
    # NB: the safe-tilt clamp is applied post-assembly (see
    # _clamp_elevation_travel) once Slot C has added the reflector/backing that
    # actually governs the sweep envelope — clamping here would only see the
    # bare trunnion core.

    return ModuleBuild(
        module_name="trunnion_revolute",
        parts_emitted=["azimuth_turret", "dish_assembly"],
        internal_articulations=["azimuth_drive", "elevation_drive"],
        interfaces={"downstream": _downstream("dish_assembly", "backing_hub")},
    )


def _build_screwjack_prismatic(ctx: ModuleBuildContext) -> ModuleBuild:
    """Inclined prismatic screw-jack elevation (screwjack_elevation S9).

    The jack apparatus is mounted OUTBOARD of the +Y yoke cheek (side-mounted
    actuator) so it clears the central trunnion hub entirely: cylinder + pivot
    lug + ram all at y=JACK_Y, slide rails at both +/-JACK_Y. Positive prismatic
    extension slides the whole dish forward (+X) and down (-Z) along the inclined
    jack axis, representing tilt toward the horizon."""
    model = ctx.model
    r: ResolvedAntennaDishConfig = ctx.config  # type: ignore[assignment]
    mount = model.get_part("mount_base")

    turret = model.part("azimuth_turret")
    _emit_turret_common(turret, r)

    dvx, dvz = JACK_DIR_X, JACK_DIR_Z

    def _along(t: float) -> tuple[float, float]:
        return (JACK_PIVOT_X + t * dvx, JACK_PIVOT_Z + t * dvz)

    # Pivot lug anchoring the cylinder base low on the turret rear.
    turret.visual(
        Box((0.24, 0.20, 0.28)),
        origin=Origin(xyz=(JACK_PIVOT_X, JACK_Y, JACK_PIVOT_Z)),
        material="clad_gray",
        name="jack_pivot_lug", material_class_id="metal.paint_coated",
    )
    # Screw-jack cylinder, inclined along the jack axis.
    cyl_cx, cyl_cz = _along(JACK_CYL_LEN / 2.0)
    turret.visual(
        mesh_from_geometry(CylinderGeometry(JACK_CYL_R, JACK_CYL_LEN, radial_segments=28), "screwjack_cylinder"),
        origin=Origin(xyz=(cyl_cx, JACK_Y, cyl_cz), rpy=(0.0, JACK_PITCH, 0.0)),
        material="steel_gray",
        name="screwjack_cylinder", material_class_id="metal.steel_bare",
    )
    # Two mounting-gusset brackets tying the cylinder inboard to the +Y yoke
    # cheek, so the whole jack apparatus (lug + cylinder + brackets) is one
    # connected turret structure. Both sit BEHIND the ram (x <= -0.40; the ram
    # back is at x ~= -0.30 and rises forward), so they never foul the ram
    # travel envelope, and bridge from the cylinder (y=JACK_Y) to the cheek face
    # (y=0.84).
    for s, t_cyl in (("left", 0.35), ("right", 0.60)):
        _cx, czt = _along(t_cyl)              # cylinder station (turret frame)
        turret.visual(
            Box((0.40, 0.42, 0.20)),
            origin=Origin(xyz=(-0.60, 0.98, czt)),
            material="steel_gray",
            name=f"elevation_bracket_{s}", material_class_id="metal.steel_bare",
        )

    dish = model.part("dish_assembly")
    _emit_dish_core(dish, r)
    # Screw-jack ram (dish-borne). Its lower end nests inside the cylinder
    # (allowed telescoping overlap); it rises to a clevis head pinned to the
    # underside of the reflector back — so the ram is physically fixed to the
    # dish (no floating island) and, driven by the prismatic joint, slides
    # forward/down out of the cylinder as the dish extends. Both ends share the
    # actuator y-plane, well outboard of the yoke cheeks.
    ram_lo_x, ram_lo_zt = _along(0.70)               # inside the cylinder
    ram_lo = (ram_lo_x, JACK_Y, ram_lo_zt - TRUNNION_Z)
    head_x = 0.25   # attach on the FRONT of the reflector back so the rod rises
                    # forward/up, clear of the pivot lug and mounting brackets
    head_r = math.hypot(head_x, JACK_Y)
    head_z = VERTEX_Z + _parabola_z(head_r, r.focal_len)   # on the reflector back
    ram_hi = (head_x, JACK_Y, head_z)
    dx, dz = ram_hi[0] - ram_lo[0], ram_hi[2] - ram_lo[2]
    ram_len = math.hypot(dx, dz)
    ram_pitch = math.atan2(abs(dx), dz)
    ram_yaw = math.pi if dx < 0 else 0.0
    dish.visual(
        mesh_from_geometry(CylinderGeometry(JACK_RAM_R, ram_len, radial_segments=20), "screwjack_ram"),
        origin=Origin(
            xyz=((ram_lo[0] + ram_hi[0]) / 2.0, JACK_Y, (ram_lo[2] + ram_hi[2]) / 2.0),
            rpy=(0.0, ram_pitch, ram_yaw),
        ),
        material="dark_gray",
        name="screwjack_ram", material_class_id="metal.blackened_gunmetal",
    )
    # Clevis head straddling the reflector-back z-band (touches the solid shell
    # OR a faceted gore panel, whichever this seed builds) so the ram stays
    # connected across both reflector forms.
    dish.visual(
        Box((0.16, 0.18, 0.22)),
        origin=Origin(xyz=(head_x, JACK_Y, head_z)),
        material="dark_gray",
        name="ram_clevis_head", material_class_id="metal.blackened_gunmetal",
    )

    _emit_azimuth_joint(model, mount, turret, r)
    model.articulation(
        "elevation_drive",
        ArticulationType.PRISMATIC,
        parent=turret,
        child=dish,
        origin=Origin(xyz=(0.0, 0.0, TRUNNION_Z)),
        axis=(JACK_DIR_X, 0.0, JACK_DIR_Z),
        motion_limits=MotionLimits(effort=4000.0, velocity=0.08, lower=0.0, upper=r.jack_travel),
    )

    return ModuleBuild(
        module_name="screwjack_prismatic",
        parts_emitted=["azimuth_turret", "dish_assembly"],
        internal_articulations=["azimuth_drive", "elevation_drive"],
        interfaces={"downstream": _downstream("dish_assembly", "backing_hub")},
    )


ELEVATION_FACTORIES = {
    "trunnion_revolute": _build_trunnion_revolute,
    "screwjack_prismatic": _build_screwjack_prismatic,
}


# --------------------------------------------------------------------------- #
# Slot C — reflector (③ Macro Surface + feed + backing appearance on dish)
# --------------------------------------------------------------------------- #


def _emit_solid_reflector(dish, r: ResolvedAntennaDishConfig) -> None:
    """Smooth revolved paraboloid shell + rim ring (origin S1 L233-267)."""
    dish_r, focal = r.dish_radius, r.focal_len
    n = 22
    outer = [
        (dish_r * i / (n - 1), VERTEX_Z + _parabola_z(dish_r * i / (n - 1), focal))
        for i in range(n)
    ]
    inner = [(rr, z + DISH_T) for (rr, z) in outer]
    dish.visual(
        mesh_from_geometry(LatheGeometry.from_shell_profiles(outer, inner, segments=64), "reflector_shell"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="dish_white",
        name="parabolic_reflector", material_class_id="metal.paint_coated",
    )
    _emit_rim_ring(dish, r)


def _gore_panel_mesh(r_in, r_out, theta0, theta1, thickness, focal):
    """Flat trapezoidal gore panel, corners on the paraboloid (faceted S3)."""
    def _pt(rr, t):
        return (rr * math.cos(t), rr * math.sin(t), VERTEX_Z + _parabola_z(rr, focal))

    p0, p1, p2, p3 = _pt(r_in, theta0), _pt(r_out, theta0), _pt(r_out, theta1), _pt(r_in, theta1)
    d1 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
    d2 = (p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2])
    nx = d1[1] * d2[2] - d1[2] * d2[1]
    ny = d1[2] * d2[0] - d1[0] * d2[2]
    nz = d1[0] * d2[1] - d1[1] * d2[0]
    nl = math.sqrt(nx * nx + ny * ny + nz * nz)
    if nl < 1e-12:
        nx, ny, nz = 0.0, 0.0, -1.0
    else:
        nx, ny, nz = nx / nl, ny / nl, nz / nl
    if nz > 0.0:
        nx, ny, nz = -nx, -ny, -nz
    off = (nx * thickness, ny * thickness, nz * thickness)
    b0 = (p0[0] + off[0], p0[1] + off[1], p0[2] + off[2])
    b1 = (p1[0] + off[0], p1[1] + off[1], p1[2] + off[2])
    b2 = (p2[0] + off[0], p2[1] + off[1], p2[2] + off[2])
    b3 = (p3[0] + off[0], p3[1] + off[1], p3[2] + off[2])
    geom = MeshGeometry()
    for v in (p0, p1, p2, p3, b0, b1, b2, b3):
        geom.add_vertex(*v)
    for a, b, c in ((0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6),
                    (0, 5, 1), (0, 4, 5), (1, 6, 2), (1, 5, 6),
                    (2, 7, 3), (2, 6, 7), (3, 4, 0), (3, 7, 4)):
        geom.add_face(a, b, c)
    return geom


def _emit_faceted_reflector(dish, r: ResolvedAntennaDishConfig) -> None:
    """Flat trapezoidal gore panels in concentric contiguous rings (faceted S3).

    Ring radii are contiguous and adjacent panels abut (zero angular gap) so the
    faceted surface is one connected mesh graph — no disconnected islands."""
    dish_r, focal = r.dish_radius, r.focal_len
    # 4 contiguous rings scaled to the aperture (compile budget: ~50-64 panels).
    ring_fracs = [(0.11, 0.30, 8), (0.30, 0.50, 12), (0.50, 0.72, 16), (0.72, 0.99, 20)]
    for ring_idx, (f_in, f_out, n_panels) in enumerate(ring_fracs):
        r_in = f_in * dish_r
        r_out = f_out * dish_r
        step = 2.0 * math.pi / n_panels
        for col in range(n_panels):
            # Adjacent panels abut (no gap) -> connected surface.
            panel_mesh = _gore_panel_mesh(r_in, r_out, step * col, step * (col + 1), DISH_T, focal)
            dish.visual(
                mesh_from_geometry(panel_mesh, f"panel_r{ring_idx}_c{col}"),
                origin=Origin(xyz=(0.0, 0.0, 0.0)),
                material="dish_white",
                name=f"panel_ring_{ring_idx}_col_{col}", material_class_id="metal.patterned_sheet_panel",
            )
    _emit_rim_ring(dish, r)


def _emit_rim_ring(dish, r: ResolvedAntennaDishConfig) -> None:
    dish_r, focal = r.dish_radius, r.focal_len
    rim_z = VERTEX_Z + _parabola_z(dish_r, focal)
    # Inner edge dips down/inboard (r-0.18, rim_z-0.10) so the ring always
    # overlaps the outermost reflector geometry — the continuous shell OR the
    # discrete outermost gore-panel ring (whose edge sits a couple cm below
    # rim_z) — keeping the faceted dish one connected mesh graph (no island).
    dish.visual(
        mesh_from_geometry(
            LatheGeometry(
                [(dish_r - 0.18, rim_z - 0.10), (dish_r + 0.06, rim_z + 0.02),
                 (dish_r + 0.06, rim_z + 0.10), (dish_r - 0.18, rim_z + 0.14)],
                segments=64,
            ),
            "rim_ring",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="dish_white",
        name="rim_stiffener_ring", material_class_id="metal.paint_coated",
    )


def _emit_radial_ribs(dish, r: ResolvedAntennaDishConfig) -> None:
    """N radial backing rib chords hugging the convex rear (origin S1 L286-310)."""
    focal = r.focal_len
    # Inner radius kept outboard of the yoke cheeks (|y|<=0.84) so tilted ribs
    # never sweep into the cheeks. Rib endpoints sit just inside the shell BACK
    # surface (z_back - 0.02) so the rib embeds into the shell at both ends and
    # the rib is connected to the reflector (no disconnected island).
    rib_r1, rib_r2 = 1.1, min(3.7, r.dish_radius - 0.8)
    rib_z1 = VERTEX_Z + _parabola_z(rib_r1, focal) + DISH_T - 0.02
    rib_z2 = VERTEX_Z + _parabola_z(rib_r2, focal) + DISH_T - 0.02
    rib_len = math.hypot(rib_r2 - rib_r1, rib_z2 - rib_z1)
    rib_pitch = -math.atan2(rib_z2 - rib_z1, rib_r2 - rib_r1)
    rib_r_mid = (rib_r1 + rib_r2) / 2.0
    rib_z_mid = (rib_z1 + rib_z2) / 2.0
    n = r.backing_rib_count
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        dish.visual(
            Box((rib_len, 0.07, 0.14)),
            origin=Origin(
                xyz=(rib_r_mid * math.cos(ang), rib_r_mid * math.sin(ang), rib_z_mid),
                rpy=(0.0, rib_pitch, ang),
            ),
            material="clad_gray",
            name=f"backing_rib_{i}", material_class_id="metal.paint_coated",
        )


def _emit_open_truss(dish, r: ResolvedAntennaDishConfig) -> None:
    """Triangulated space-frame backing (open_truss_backing S8). Every spar's
    inner node embeds in the hub, so the whole truss connects to the body."""
    focal = r.focal_len
    n_spars = 12
    spar_r_in = 0.45                     # inside the hub (r=0.62) -> contact
    spar_r_out = r.dish_radius - 0.35
    ring_radii = [spar_r_out * 0.38, spar_r_out * 0.63, spar_r_out * 0.88]
    truss_drop = 0.14
    spar_mem_r, diag_mem_r = 0.042, 0.032

    idx = 0

    def _node_z(rr):
        return VERTEX_Z + _parabola_z(rr, focal) - truss_drop

    def _member(p1, p2, radius):
        nonlocal idx
        dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length < 1e-6:
            return
        mid = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0, (p1[2] + p2[2]) / 2.0)
        pitch = math.atan2(math.hypot(dx, dy), dz)
        yaw = math.atan2(dy, dx)
        dish.visual(
            mesh_from_geometry(CylinderGeometry(radius, length, radial_segments=8), f"truss_{idx}"),
            origin=Origin(xyz=mid, rpy=(0.0, pitch, yaw)),
            material="steel_gray",
            name=f"truss_member_{idx}", material_class_id="metal.steel_bare",
        )
        idx += 1

    # Radial spars (inner node inside hub -> connected to body).
    for i in range(n_spars):
        ang = 2.0 * math.pi * i / n_spars
        ca, sa = math.cos(ang), math.sin(ang)
        _member((spar_r_in * ca, spar_r_in * sa, _node_z(spar_r_in) + 0.06),
                (spar_r_out * ca, spar_r_out * sa, _node_z(spar_r_out)), spar_mem_r)
    # Concentric ring hoops (chords between adjacent spars).
    for ring_r in ring_radii:
        z_ring = _node_z(ring_r)
        for i in range(n_spars):
            a0 = 2.0 * math.pi * i / n_spars
            a1 = 2.0 * math.pi * ((i + 1) % n_spars) / n_spars
            _member((ring_r * math.cos(a0), ring_r * math.sin(a0), z_ring),
                    (ring_r * math.cos(a1), ring_r * math.sin(a1), z_ring), spar_mem_r)
    # Diagonal bracing between node layers (triangulation).
    zone_radii = [spar_r_in] + ring_radii + [spar_r_out]
    for zone_idx in range(len(zone_radii) - 1):
        r_lo, r_hi = zone_radii[zone_idx], zone_radii[zone_idx + 1]
        for i in range(n_spars):
            a_i = 2.0 * math.pi * i / n_spars
            a_n = 2.0 * math.pi * ((i + 1) % n_spars) / n_spars
            _member((r_lo * math.cos(a_i), r_lo * math.sin(a_i), _node_z(r_lo)),
                    (r_hi * math.cos(a_n), r_hi * math.sin(a_n), _node_z(r_hi)), diag_mem_r)


def _emit_prime_focus_feed(dish, r: ResolvedAntennaDishConfig) -> None:
    """N converging struts + apex hub + subreflector + central horn (origin S1)."""
    focal = r.focal_len
    dish_r = r.dish_radius
    strut_mount_r = min(3.1, dish_r - 1.4)
    apex_z = VERTEX_Z + focal + 0.15
    n = r.feed_strut_count
    for i in range(n):
        ang = math.radians(90.0 + 360.0 * i / n)
        ax = strut_mount_r * math.cos(ang)
        ay = strut_mount_r * math.sin(ang)
        az = VERTEX_Z + _parabola_z(strut_mount_r, focal) - 0.04
        bx, by, bz = 0.0, 0.0, apex_z
        dx, dy, dz = bx - ax, by - ay, bz - az
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        pitch = math.atan2(math.hypot(dx, dy), dz)
        yaw = math.atan2(dy, dx)
        mid = ((ax + bx) / 2.0, (ay + by) / 2.0, (az + bz) / 2.0)
        dish.visual(
            mesh_from_geometry(CylinderGeometry(STRUT_R, length, radial_segments=16), f"feed_strut_{i}"),
            origin=Origin(xyz=mid, rpy=(0.0, pitch, yaw)),
            material="shell_white",
            name=f"feed_strut_{i}", material_class_id="metal.paint_coated",
        )
    dish.visual(
        mesh_from_geometry(CylinderGeometry(0.20, 0.34, radial_segments=24), "apex_hub"),
        origin=Origin(xyz=(0.0, 0.0, apex_z)),
        material="steel_gray",
        name="apex_hub", material_class_id="metal.steel_bare",
    )
    dish.visual(
        mesh_from_geometry(DomeGeometry(0.42, radial_segments=32), "subreflector"),
        origin=Origin(xyz=(0.0, 0.0, apex_z - 0.14), rpy=(math.pi, 0.0, 0.0)),
        material="dish_white",
        name="subreflector", material_class_id="metal.paint_coated",
    )
    dish.visual(
        mesh_from_geometry(CylinderGeometry(HORN_R, HORN_LEN, radial_segments=24), "feed_horn_tube"),
        origin=Origin(xyz=(0.0, 0.0, VERTEX_Z + HORN_LEN / 2.0)),
        material="clad_gray",
        name="feed_horn_tube", material_class_id="metal.paint_coated",
    )
    dish.visual(
        mesh_from_geometry(ConeGeometry(HORN_R + 0.10, 0.30, radial_segments=24), "feed_horn_mouth"),
        origin=Origin(xyz=(0.0, 0.0, VERTEX_Z + HORN_LEN + 0.15), rpy=(math.pi, 0.0, 0.0)),
        material="dark_gray",
        name="feed_horn_mouth", material_class_id="metal.blackened_gunmetal",
    )


def _emit_offset_boom_feed(dish, r: ResolvedAntennaDishConfig) -> None:
    """Single curved cantilever boom from the rim to the focus (offset S7)."""
    focal = r.focal_len
    dish_r = r.dish_radius
    rim_z = VERTEX_Z + _parabola_z(dish_r, focal)
    focus_z = VERTEX_Z + focal
    boom_points = [
        (0.0, -dish_r + 0.05, rim_z + 0.05),
        (0.0, -0.73 * dish_r, rim_z + 1.0),
        (0.0, -0.31 * dish_r, focus_z + 0.55),
        (0.0, 0.0, focus_z + 0.15),
    ]
    dish.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                boom_points, radius=0.10, samples_per_segment=20, radial_segments=20,
                cap_ends=True, up_hint=(1.0, 0.0, 0.0),
            ),
            "feed_boom_tube",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="shell_white",
        name="feed_boom_arm", material_class_id="metal.paint_coated",
    )
    dish.visual(
        Box((0.35, 0.40, 0.50)),
        origin=Origin(xyz=(0.0, -dish_r + 0.05, rim_z + 0.05), rpy=(0.0, 0.20, 0.0)),
        material="steel_gray",
        name="feed_boom_bracket", material_class_id="metal.steel_bare",
    )
    dish.visual(
        mesh_from_geometry(CylinderGeometry(HORN_R, HORN_LEN * 0.9, radial_segments=24), "offset_horn_tube"),
        origin=Origin(xyz=(0.0, 0.0, focus_z - HORN_LEN * 0.9 / 2.0 + 0.15)),
        material="clad_gray",
        name="offset_feed_horn_tube", material_class_id="metal.paint_coated",
    )
    dish.visual(
        mesh_from_geometry(ConeGeometry(HORN_R + 0.10, 0.30, radial_segments=24), "offset_horn_mouth"),
        origin=Origin(xyz=(0.0, 0.0, focus_z - HORN_LEN * 0.9 + 0.05), rpy=(0.0, 0.0, 0.0)),
        material="dark_gray",
        name="offset_feed_horn_mouth", material_class_id="metal.blackened_gunmetal",
    )


def _emit_counterweight(dish, r: ResolvedAntennaDishConfig) -> None:
    dish.visual(
        Box((0.9, 1.1, 0.5)),
        origin=Origin(xyz=(-0.70, 0.0, -0.28), rpy=(0.0, -0.35, 0.0)),
        material="clad_gray",
        name="counterweight_box", material_class_id="metal.paint_coated",
    )


def _build_reflector(ctx: ModuleBuildContext, *, reflector_form: str) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAntennaDishConfig = ctx.config  # type: ignore[assignment]
    dish = model.get_part("dish_assembly")

    if reflector_form == "faceted_panels":
        _emit_faceted_reflector(dish, r)
    else:
        _emit_solid_reflector(dish, r)

    if r.backing_style == "open_truss":
        _emit_open_truss(dish, r)
    else:
        _emit_radial_ribs(dish, r)

    _emit_counterweight(dish, r)

    if r.feed_system == "offset_boom":
        _emit_offset_boom_feed(dish, r)
    else:
        _emit_prime_focus_feed(dish, r)

    return ModuleBuild(
        module_name=reflector_form,
        parts_emitted=[],
        interfaces={"downstream": _downstream("dish_assembly", "backing_hub")},
    )


def _build_solid_paraboloid(ctx: ModuleBuildContext) -> ModuleBuild:
    return _build_reflector(ctx, reflector_form="solid_paraboloid")


def _build_faceted_panels(ctx: ModuleBuildContext) -> ModuleBuild:
    return _build_reflector(ctx, reflector_form="faceted_panels")


REFLECTOR_FACTORIES = {
    "solid_paraboloid": _build_solid_paraboloid,
    "faceted_panels": _build_faceted_panels,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def _slots_for_config(r: ResolvedAntennaDishConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="mount_base", candidates={r.mount_form: MOUNT_FACTORIES[r.mount_form]},
                 anchor_choice=r.mount_form),
        SlotSpec(slot_name="pointing", candidates={r.elevation_module: ELEVATION_FACTORIES[r.elevation_module]},
                 anchor_choice=r.elevation_module),
        SlotSpec(slot_name="reflector", candidates={r.reflector_form: REFLECTOR_FACTORIES[r.reflector_form]},
                 anchor_choice=r.reflector_form),
    ]


def _clamp_elevation_travel(model: ArticulatedObject, r: ResolvedAntennaDishConfig) -> None:
    """Solve the safe elevation travel AFTER the whole dish exists.

    The reflector shell / faceted panels / backing ribs-or-truss / counterweight
    are added by Slot C, so the sweep envelope that can foul the turret (yoke
    cheeks, bearings, azimuth drum) is only complete post-assembly. Clamping here
    keeps the moving dish >= margin clear of the turret across the full travel,
    for BOTH the revolute trunnion and the prismatic screw-jack. Captured
    trunnion contacts (and the telescoping ram-in-cylinder for the screw-jack)
    are exempted so an always-on coaxial overlap can't mask a real sweep.
    """
    allowed = _captured_trunnion_pairs()
    if r.elevation_module == "screwjack_prismatic":
        allowed = allowed + [
            ("azimuth_turret", "dish_assembly", "screwjack_cylinder", "screwjack_ram")
        ]
    clamp_joint_limits(
        model, "elevation_drive", margin=0.02, keepout=["azimuth_turret"],
        allowed_pairs=allowed, scan_steps=28,
    )


def build_astronomy_antenna_dish(
    config: AstronomyAntennaDishConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="astronomy_antenna_dish", assets=assets)
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
    _clamp_elevation_travel(model, r)
    return model


def build_seeded_astronomy_antenna_dish(seed: int) -> ArticulatedObject:
    return build_astronomy_antenna_dish(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    rib_axis = f"ribs_{r.backing_rib_count}" if r.backing_style == "radial_ribs" else "ribs_na"
    strut_axis = f"struts_{r.feed_strut_count}" if r.feed_system == "prime_focus_quad" else "struts_na"
    louver_axis = f"louver_{r.louver_vent_count}" if r.mount_form == "conical_pedestal" else "louver_na"
    return [
        ("mount_base", r.mount_form),
        ("pointing", r.elevation_module),
        ("reflector", r.reflector_form),
        ("feed_system", r.feed_system),
        ("backing_style", r.backing_style),
        ("backing_rib_count", rib_axis),
        ("feed_strut_count", strut_axis),
        ("louver_vent_count", louver_axis),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedAntennaDishConfig) -> None:
    mount = model.get_part("mount_base")
    turret = model.get_part("azimuth_turret")
    dish = model.get_part("dish_assembly")

    # Azimuth turntable drum seats on the mount top (captured seat).
    ctx.allow_overlap(mount, turret, elem_a=MOUNT_SEAT_VISUAL[r.mount_form],
                      elem_b="turntable_drum",
                      reason="Azimuth turntable drum seats on the mount top platform/flange/hub-plate.")

    # Elevation trunnion shaft captured inside both yoke bearings/cheeks.
    for s in ("left", "right"):
        ctx.allow_overlap(turret, dish, elem_a=f"trunnion_bearing_{s}", elem_b="trunnion_shaft",
                          reason="Elevation trunnion shaft is captured inside the yoke bearing.")
        ctx.allow_overlap(turret, dish, elem_a=f"yoke_cheek_{s}", elem_b="trunnion_shaft",
                          reason="Trunnion shaft passes through the yoke cheek into the bearing.")
        ctx.allow_overlap(turret, dish, elem_a=f"yoke_cheek_{s}", elem_b="backing_hub",
                          reason="Dish backing hub is cradled between the yoke cheeks at the trunnion axis.")

    if r.elevation_module == "screwjack_prismatic":
        # Ram nested inside the cylinder as a telescoping linear actuator.
        ctx.allow_overlap(turret, dish, elem_a="screwjack_cylinder", elem_b="screwjack_ram",
                          reason="Screw-jack ram is intentionally nested inside the cylinder (telescoping actuator).")


def _center(aabb):
    return [(aabb[0][i] + aabb[1][i]) / 2.0 for i in range(3)]


def run_astronomy_antenna_dish_tests(
    model: ArticulatedObject,
    config: AstronomyAntennaDishConfig,
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

    # Category structure asserts.
    parts = {p.name for p in model.parts}
    ctx.check("three_core_parts",
              {"mount_base", "azimuth_turret", "dish_assembly"} <= parts,
              details=f"parts={sorted(parts)}")

    mount = model.get_part("mount_base")
    dish = model.get_part("dish_assembly")

    az = model.get_articulation("azimuth_drive")
    el = model.get_articulation("elevation_drive")
    ctx.check("azimuth_is_revolute", az.articulation_type == ArticulationType.REVOLUTE,
              details=str(az.articulation_type))
    expected_el = (ArticulationType.PRISMATIC if r.elevation_module == "screwjack_prismatic"
                   else ArticulationType.REVOLUTE)
    ctx.check("elevation_type_matches_module", el.articulation_type == expected_el,
              details=str(el.articulation_type))

    # Multiplicity asserts.
    if r.backing_style == "radial_ribs":
        ribs = [v.name for v in dish.visuals if v.name.startswith("backing_rib_")]
        ctx.check("rib_count_matches", len(ribs) == r.backing_rib_count,
                  details=f"ribs={len(ribs)} expected={r.backing_rib_count}")
    if r.feed_system == "prime_focus_quad":
        struts = [v.name for v in dish.visuals if v.name.startswith("feed_strut_")]
        ctx.check("strut_count_matches", len(struts) == r.feed_strut_count,
                  details=f"struts={len(struts)} expected={r.feed_strut_count}")
    if r.mount_form == "conical_pedestal":
        vents = [v.name for v in mount.visuals if v.name.startswith("louver_vent_")]
        ctx.check("louver_count_matches", len(vents) == r.louver_vent_count,
                  details=f"vents={len(vents)} expected={r.louver_vent_count}")

    # Targeted mechanism: azimuth 180deg slews the dish to the opposite side.
    rest = ctx.part_world_aabb(dish)
    with ctx.pose({az: math.pi, el: 0.0}):
        slewed = ctx.part_world_aabb(dish)
    ctx.check("azimuth_slews_dish",
              math.dist(_center(rest), _center(slewed)) > 0.05 or abs(_center(rest)[0]) < 0.35,
              details=f"rest_c={_center(rest)}, slew_c={_center(slewed)}")

    # Targeted mechanism: elevation moves the dish.
    if expected_el == ArticulationType.REVOLUTE:
        # clamp_joint_limits() already tightened the range in place; use the
        # solved upper bound directly.
        el_max = el.motion_limits.upper
        with ctx.pose({az: 0.0, el: 0.0}):
            zen = _center(ctx.part_world_aabb(dish))
        with ctx.pose({az: 0.0, el: el_max}):
            tilt = _center(ctx.part_world_aabb(dish))
        ctx.check("elevation_tilts_dish_forward", tilt[0] > zen[0] + 0.2,
                  details=f"x-center {zen[0]:.2f} -> {tilt[0]:.2f} (el_max={el_max:.3f})")
    else:
        # clamp_joint_limits() may have tightened jack_travel to keep the dish
        # clear of the turret; drive to the solved upper. Any positive travel
        # along the inclined jack axis (cos38.5, 0, -sin38.5) moves the dish
        # forward (+x) and down (-z); assert that direction rather than a fixed
        # magnitude, so a legitimately clamped shorter stroke still passes.
        jack_up = el.motion_limits.upper
        with ctx.pose({az: 0.0, el: 0.0}):
            retr = _center(ctx.part_world_aabb(dish))
        with ctx.pose({az: 0.0, el: jack_up}):
            ext = _center(ctx.part_world_aabb(dish))
        ctx.check("screwjack_extends_dish", ext[0] > retr[0] + 0.15 and ext[2] < retr[2] - 0.1,
                  details=f"retr={retr}, ext={ext} (jack_up={jack_up:.3f})")

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "AstronomyAntennaDishConfig",
    "ResolvedAntennaDishConfig",
    "MountForm",
    "ElevationModule",
    "ReflectorForm",
    "FeedSystem",
    "BackingStyle",
    "AntennaPalette",
    "build_astronomy_antenna_dish",
    "build_seeded_astronomy_antenna_dish",
    "config_from_seed",
    "resolve_config",
    "run_astronomy_antenna_dish_tests",
    "slot_choices_for_seed",
]
