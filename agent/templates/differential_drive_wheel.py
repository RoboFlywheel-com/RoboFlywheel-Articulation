# SPDX-License-Identifier: Apache-2.0

"""Differential drive wheel — modular procedural template.

Two disjoint but category-faithful motion spines, selected per seed:

* ``bevel-differential`` family (``carrier`` root, parallel-children):
  an exposed or enclosed bevel differential — orange ring gear, side gear(s),
  yellow input pinion, optional spider cross with N planet pinions — driving two
  coaxial wheels through a CONTINUOUS mimic gear train. Rigid, no chassis swivel.
* ``dual-drive`` family (``mount_plate`` root, linear chain + parallel wheels):
  a top plate or side-flange bracket carries a ``drive_carriage`` through a
  rigid / limited-swivel / continuous-caster steering joint; the carriage runs
  the wheels via a gearbox, timing belt, worm gear, or in-hub direct drive,
  optionally through sprung rocker arms.

Slots (report-only, mirrored in ``slot_choices``):
* ``drive_mechanism``  — bevel_diff_single/spider2/spider4, dual_motor_gearbox,
                          belt_reduction, worm_reduction, hub_direct_drive
* ``chassis_mount``    — rear_bridge_carrier, enclosed_diff_housing,
                          top_mount_plate, side_flange_bracket
* ``steering``         — rigid, limited_swivel, continuous_caster
* ``wheel_travel``     — rigid_axle, sprung_rocker

Every legal slot combination corresponds to a real passing 5-star source; the
only added variation over the sources is the safe steering joint-type toggle.
Sources: rec_use-the-attached-...ed8a6961 (A, open bevel diff),
rec_robotics__differential_drive_wheel__002 (B, AGV dual motor), and the
belt / worm / hubdrive / caster / sideflange / suspension / enclosed_housing /
spider_n2 / spider_n4 variant forks.
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
    BoltPattern,
    Box,
    Cylinder,
    MeshGeometry,
    Mimic,
    MotionLimits,
    MotionProperties,
    Origin,
    SpurGear,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireGroove,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    Worm,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


ROT_Z_TO_X = (0.0, math.pi / 2.0, 0.0)
ROT_Z_TO_Y = (math.pi / 2.0, 0.0, 0.0)
ROT_X_TO_Y = (0.0, 0.0, math.pi / 2.0)


# ---------------------------------------------------------------------------
# Slot literals
# ---------------------------------------------------------------------------

DriveMechanism = Literal[
    "bevel_diff_single",
    "bevel_diff_spider2",
    "bevel_diff_spider4",
    "dual_motor_gearbox",
    "belt_reduction",
    "worm_reduction",
    "hub_direct_drive",
]
ChassisMount = Literal[
    "rear_bridge_carrier",
    "enclosed_diff_housing",
    "top_mount_plate",
    "side_flange_bracket",
]
Steering = Literal["rigid", "limited_swivel", "continuous_caster"]
WheelTravel = Literal["rigid_axle", "sprung_rocker"]
PaletteTheme = Literal["industrial_steel", "gunmetal_orange", "anodized_black"]

DRIVE_MECHANISMS: tuple[DriveMechanism, ...] = (
    "bevel_diff_single",
    "bevel_diff_spider2",
    "bevel_diff_spider4",
    "dual_motor_gearbox",
    "belt_reduction",
    "worm_reduction",
    "hub_direct_drive",
)
BEVEL_MECHANISMS = {"bevel_diff_single", "bevel_diff_spider2", "bevel_diff_spider4"}


def _family(drive: str) -> str:
    return "bevel" if drive in BEVEL_MECHANISMS else "dual"


# ---------------------------------------------------------------------------
# Palettes (⑥ — material class / colour; geometry unchanged)
# ---------------------------------------------------------------------------

# Roles overridden per theme; functional gear/tire colours stay fixed so the
# bevel differential keeps its category-recognisable anodised gear semantics.
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "industrial_steel": {
        "machined": (0.70, 0.72, 0.70, 1.0),
        "dark_metal": (0.12, 0.13, 0.14, 1.0),
        "steel": (0.50, 0.52, 0.51, 1.0),
        "dark_anodized": (0.08, 0.085, 0.085, 1.0),
        "tan_poly": (0.91, 0.62, 0.25, 1.0),
    },
    "gunmetal_orange": {
        "machined": (0.55, 0.57, 0.58, 1.0),
        "dark_metal": (0.16, 0.14, 0.10, 1.0),
        "steel": (0.42, 0.44, 0.46, 1.0),
        "dark_anodized": (0.10, 0.07, 0.05, 1.0),
        "tan_poly": (0.86, 0.50, 0.14, 1.0),
    },
    "anodized_black": {
        "machined": (0.30, 0.31, 0.33, 1.0),
        "dark_metal": (0.05, 0.05, 0.06, 1.0),
        "steel": (0.34, 0.35, 0.37, 1.0),
        "dark_anodized": (0.03, 0.03, 0.035, 1.0),
        "tan_poly": (0.20, 0.20, 0.20, 1.0),
    },
}

# Fixed (theme-independent) material colours.
FIXED_MATERIALS: dict[str, tuple[float, float, float, float]] = {
    "rubber": (0.008, 0.008, 0.007, 1.0),
    "cast_iron": (0.28, 0.28, 0.30, 1.0),
    "blue": (0.02, 0.12, 0.54, 1.0),
    "green": (0.0, 0.78, 0.22, 1.0),
    "red": (0.78, 0.06, 0.05, 1.0),
    "orange": (1.0, 0.36, 0.05, 1.0),
    "brass": (0.88, 0.62, 0.20, 1.0),
    "yellow": (1.0, 0.74, 0.12, 1.0),
    "bolt_black": (0.015, 0.015, 0.014, 1.0),
    "black_rubber": (0.015, 0.014, 0.012, 1.0),
    "copper": (0.72, 0.45, 0.20, 1.0),
    "belt_rubber": (0.04, 0.04, 0.03, 1.0),
    "spring_steel": (0.38, 0.40, 0.38, 1.0),
    "zinc_yellow": (0.85, 0.72, 0.12, 1.0),
}


def _register_materials(model: ArticulatedObject, theme: str) -> dict:
    """Register every material exactly once; return name -> Material."""
    out: dict = {}
    for name, rgba in FIXED_MATERIALS.items():
        out[name] = model.material(name, rgba=rgba)
    for name, rgba in PALETTES[theme].items():
        out[name] = model.material(name, rgba=rgba)
    return out


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DifferentialDriveWheelConfig:
    drive_mechanism: DriveMechanism | None = None
    chassis_mount: ChassisMount | None = None
    steering: Steering | None = None
    wheel_travel: WheelTravel | None = None
    palette_theme: PaletteTheme = "industrial_steel"
    swivel_limit: float = 0.35
    wheel_radius_scale: float = 1.0
    tire_tread_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedDifferentialDriveWheelConfig:
    drive_mechanism: DriveMechanism
    chassis_mount: ChassisMount
    steering: Steering
    wheel_travel: WheelTravel
    palette_theme: PaletteTheme
    swivel_limit: float
    wheel_radius_scale: float
    tire_tread_scale: float
    family: str
    planet_pinions: int


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def config_from_seed(seed: int) -> DifferentialDriveWheelConfig:
    """Deterministic procedural sampling for every ordinary seed (seed 0 is NOT special)."""
    rng = random.Random(seed)
    drive: DriveMechanism = rng.choice(DRIVE_MECHANISMS)  # type: ignore[assignment]
    fam = _family(drive)

    if fam == "bevel":
        mount: ChassisMount = rng.choice(  # type: ignore[assignment]
            ("rear_bridge_carrier", "enclosed_diff_housing")
        )
        steering: Steering = "rigid"
        travel: WheelTravel = "rigid_axle"
    else:
        if drive == "dual_motor_gearbox":
            mount = rng.choice(("top_mount_plate", "side_flange_bracket"))  # type: ignore[assignment]
            if mount == "side_flange_bracket":
                steering = rng.choice(("rigid", "limited_swivel"))  # type: ignore[assignment]
                travel = "rigid_axle"
            else:
                steering = rng.choice(  # type: ignore[assignment]
                    ("rigid", "limited_swivel", "continuous_caster")
                )
                if steering == "continuous_caster":
                    travel = "rigid_axle"
                else:
                    travel = rng.choice(("rigid_axle", "sprung_rocker"))  # type: ignore[assignment]
        else:  # belt / worm / hub only mount on the top plate, rigid or limited swivel
            mount = "top_mount_plate"
            steering = rng.choice(("rigid", "limited_swivel"))  # type: ignore[assignment]
            travel = "rigid_axle"

    return DifferentialDriveWheelConfig(
        drive_mechanism=drive,
        chassis_mount=mount,
        steering=steering,
        wheel_travel=travel,
        palette_theme=rng.choice(tuple(PALETTES.keys())),  # type: ignore[arg-type]
        swivel_limit=round(rng.uniform(0.25, 0.5), 3),
        wheel_radius_scale=round(rng.uniform(0.92, 1.08), 3),
        tire_tread_scale=round(rng.uniform(0.55, 1.45), 3),
    )


def resolve_config(
    config: DifferentialDriveWheelConfig,
) -> ResolvedDifferentialDriveWheelConfig:
    drive = config.drive_mechanism or "dual_motor_gearbox"
    if drive not in DRIVE_MECHANISMS:
        raise ValueError(f"Unsupported drive_mechanism: {drive!r}")
    fam = _family(drive)

    mount = config.chassis_mount
    steering = config.steering
    travel = config.wheel_travel

    if fam == "bevel":
        if mount not in ("rear_bridge_carrier", "enclosed_diff_housing"):
            mount = "rear_bridge_carrier"
        steering = "rigid"
        travel = "rigid_axle"
        planet = {"bevel_diff_spider2": 2, "bevel_diff_spider4": 4}.get(drive, 0)
    else:
        planet = 0
        if drive == "dual_motor_gearbox":
            if mount not in ("top_mount_plate", "side_flange_bracket"):
                mount = "top_mount_plate"
        else:
            mount = "top_mount_plate"
        # Steering gating.
        if steering not in ("rigid", "limited_swivel", "continuous_caster"):
            steering = "limited_swivel"
        if mount == "side_flange_bracket" and steering == "continuous_caster":
            steering = "limited_swivel"
        if drive != "dual_motor_gearbox" and steering == "continuous_caster":
            steering = "limited_swivel"
        # Travel gating: sprung rocker only on the dual-motor gearbox top plate.
        if travel not in ("rigid_axle", "sprung_rocker"):
            travel = "rigid_axle"
        sprung_ok = (
            drive == "dual_motor_gearbox"
            and mount == "top_mount_plate"
            and steering != "continuous_caster"
        )
        if travel == "sprung_rocker" and not sprung_ok:
            travel = "rigid_axle"

    return ResolvedDifferentialDriveWheelConfig(
        drive_mechanism=drive,
        chassis_mount=mount,  # type: ignore[arg-type]
        steering=steering,  # type: ignore[arg-type]
        wheel_travel=travel,  # type: ignore[arg-type]
        palette_theme=config.palette_theme
        if config.palette_theme in PALETTES
        else "industrial_steel",
        swivel_limit=_clamp(config.swivel_limit, 0.20, 0.60),
        wheel_radius_scale=_clamp(config.wheel_radius_scale, 0.92, 1.08),
        tire_tread_scale=_clamp(config.tire_tread_scale, 0.55, 1.45),
        family=fam,
        planet_pinions=planet,
    )


def slot_choices_for_config(
    r: ResolvedDifferentialDriveWheelConfig,
) -> list[tuple[str, str]]:
    return [
        ("drive_mechanism", r.drive_mechanism),
        ("chassis_mount", r.chassis_mount),
        ("steering", r.steering),
        ("wheel_travel", r.wheel_travel),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Shared mesh helpers
# ---------------------------------------------------------------------------


def _add_cyl(part, radius, length, xyz, *, rpy=(0.0, 0.0, 0.0), material=None, name=None) -> None:
    part.visual(
        Cylinder(radius=radius, length=length), origin=Origin(xyz=xyz, rpy=rpy),
        material=material, name=name, material_class_id="metal.generic_plain",
    )


def _add_quad(mesh: MeshGeometry, a: int, b: int, c: int, d: int) -> None:
    mesh.add_face(a, b, c)
    mesh.add_face(a, c, d)


def _annular_cylinder_mesh(*, inner_radius, outer_radius, width, segments=64) -> MeshGeometry:
    """Hollow cylinder centered on local X (bearings, gear hubs)."""
    mesh = MeshGeometry()
    outer_loops: list[list[int]] = []
    inner_loops: list[list[int]] = []
    for x in (-width / 2.0, width / 2.0):
        outer: list[int] = []
        inner: list[int] = []
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            ct, st = math.cos(theta), math.sin(theta)
            outer.append(mesh.add_vertex(x, outer_radius * ct, outer_radius * st))
            inner.append(mesh.add_vertex(x, inner_radius * ct, inner_radius * st))
        outer_loops.append(outer)
        inner_loops.append(inner)
    for i in range(segments):
        j = (i + 1) % segments
        _add_quad(mesh, outer_loops[0][i], outer_loops[0][j], outer_loops[1][j], outer_loops[1][i])
        _add_quad(mesh, inner_loops[0][j], inner_loops[0][i], inner_loops[1][i], inner_loops[1][j])
        _add_quad(mesh, outer_loops[0][j], outer_loops[0][i], inner_loops[0][i], inner_loops[0][j])
        _add_quad(mesh, outer_loops[1][i], outer_loops[1][j], inner_loops[1][j], inner_loops[1][i])
    return mesh


def _toothed_bevel_mesh(
    *, inner_radius, root_radius, tooth_height, width, teeth, cone_delta, samples_per_tooth=8
) -> MeshGeometry:
    """Annular, visibly toothed bevel gear centered on local X."""
    segments = teeth * samples_per_tooth
    mesh = MeshGeometry()
    outer_loops: list[list[int]] = []
    inner_loops: list[list[int]] = []
    for side, x in enumerate((-width / 2.0, width / 2.0)):
        cone = -cone_delta if side == 0 else cone_delta
        outer: list[int] = []
        inner: list[int] = []
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            tooth_phase = (i % samples_per_tooth) / samples_per_tooth
            centered = abs(tooth_phase - 0.5) * 2.0
            tooth = max(0.0, 1.0 - centered / 0.72)
            tooth *= 0.92 + 0.08 * math.cos(4.0 * math.pi * tooth_phase)
            outer_radius = root_radius + cone + tooth_height * tooth
            ct, st = math.cos(theta), math.sin(theta)
            outer.append(mesh.add_vertex(x, outer_radius * ct, outer_radius * st))
            inner.append(mesh.add_vertex(x, inner_radius * ct, inner_radius * st))
        outer_loops.append(outer)
        inner_loops.append(inner)
    for i in range(segments):
        j = (i + 1) % segments
        _add_quad(mesh, outer_loops[0][i], outer_loops[0][j], outer_loops[1][j], outer_loops[1][i])
        _add_quad(mesh, inner_loops[0][j], inner_loops[0][i], inner_loops[1][i], inner_loops[1][j])
        _add_quad(mesh, outer_loops[0][j], outer_loops[0][i], inner_loops[0][i], inner_loops[0][j])
        _add_quad(mesh, outer_loops[1][i], outer_loops[1][j], inner_loops[1][j], inner_loops[1][i])
    return mesh


# ---- bevel-family tire / rim (chevron, source A) ----


def _make_tire_mesh_a(name: str, *, radius_scale: float = 1.0, tread_scale: float = 1.0):
    geom = TireGeometry(
        0.135, 0.082, inner_radius=0.092,
        carcass=TireCarcass(belt_width_ratio=0.72, sidewall_bulge=0.08),
        tread=TireTread(style="chevron", depth=0.008 * tread_scale, count=26, angle_deg=28.0, land_ratio=0.56),
        grooves=(
            TireGroove(center_offset=-0.020, width=0.004, depth=0.003),
            TireGroove(center_offset=0.020, width=0.004, depth=0.003),
        ),
        sidewall=TireSidewall(style="rounded", bulge=0.04),
        shoulder=TireShoulder(width=0.008, radius=0.004),
    )
    # Radial (YZ) scaling only: the axle stays along X, so the tyre width and
    # the bead interface to the unchanged hub/shaft stack are preserved.
    geom.scale(1.0, radius_scale, radius_scale)
    return mesh_from_geometry(geom, name)


def _make_rim_mesh_a(name: str, *, radius_scale: float = 1.0):
    geom = WheelGeometry(
        0.096, 0.076,
        rim=WheelRim(inner_radius=0.060, flange_height=0.008, flange_thickness=0.004, bead_seat_depth=0.003),
        hub=WheelHub(radius=0.030, width=0.052, cap_style="domed",
                     bolt_pattern=BoltPattern(count=5, circle_diameter=0.043, hole_diameter=0.005)),
        face=WheelFace(dish_depth=0.010, front_inset=0.003, rear_inset=0.003),
        spokes=WheelSpokes(style="split_y", count=5, thickness=0.004, window_radius=0.014),
        bore=WheelBore(style="round", diameter=0.015),
    )
    geom.scale(1.0, radius_scale, radius_scale)
    return mesh_from_geometry(geom, name)


# ---- dual-family tire (block, source B) ----


def _make_tire_mesh_b(name: str, *, radius_scale: float = 1.0, tread_scale: float = 1.0):
    geom = TireGeometry(
        0.132, 0.078, inner_radius=0.099,
        carcass=TireCarcass(belt_width_ratio=0.78, sidewall_bulge=0.030),
        tread=TireTread(style="block", depth=0.0045 * tread_scale, count=28, land_ratio=0.62),
        grooves=(
            TireGroove(center_offset=-0.018, width=0.0045, depth=0.0025),
            TireGroove(center_offset=0.018, width=0.0045, depth=0.0025),
        ),
        sidewall=TireSidewall(style="square", bulge=0.018),
        shoulder=TireShoulder(width=0.007, radius=0.003),
    )
    geom.scale(1.0, radius_scale, radius_scale)
    return mesh_from_geometry(geom, f"{name}_polyurethane_tire")


# ---- dual-family cadquery mount helpers ----


def _mounting_plate_mesh(*, center_hole=0.105, bearing_bolt_r=0.078, bearing_bolt_n=10) -> object:
    plate = cq.Workplane("XY").box(0.620, 0.430, 0.018).edges("|Z").fillet(0.035)
    plate = plate.faces(">Z").workplane().hole(center_hole)
    perimeter = [
        (-0.265, -0.165), (0.265, -0.165), (-0.265, 0.165), (0.265, 0.165),
        (-0.160, -0.185), (0.160, -0.185), (-0.160, 0.185), (0.160, 0.185),
    ]
    plate = plate.faces(">Z").workplane().pushPoints(perimeter).hole(0.012)
    holes = [(bearing_bolt_r * math.cos(2 * math.pi * i / bearing_bolt_n),
              bearing_bolt_r * math.sin(2 * math.pi * i / bearing_bolt_n)) for i in range(bearing_bolt_n)]
    plate = plate.faces(">Z").workplane().pushPoints(holes).hole(0.007)
    return plate


def _bearing_ring_mesh() -> object:
    outer = cq.Workplane("XY").circle(0.090).extrude(0.024, both=True)
    inner_cut = cq.Workplane("XY").circle(0.052).extrude(0.030, both=True)
    return outer.cut(inner_cut)


def _slew_ring_bearing_mesh() -> object:
    outer_r, inner_r, h = 0.140, 0.085, 0.028
    ring = cq.Workplane("XY").circle(outer_r).circle(inner_r).extrude(h)
    tooth_count, tooth_depth = 48, 0.006
    tw = 2.0 * math.pi / tooth_count
    for i in range(tooth_count):
        a = tw * i
        cx = (outer_r + 0.001) * math.cos(a)
        cy = (outer_r + 0.001) * math.sin(a)
        slot = (cq.Workplane("XY").center(cx, cy).rect(tooth_depth * 2, tooth_depth)
                .extrude(h + 0.004).translate((0.0, 0.0, -0.002)))
        slot = slot.rotate((0, 0, 0), (0, 0, 1), math.degrees(a))
        ring = ring.cut(slot)
    for i in range(12):
        a = 2.0 * math.pi * i / 12.0
        hole = cq.Workplane("XY").circle(0.006).extrude(h + 0.010).translate(
            (0.112 * math.cos(a), 0.112 * math.sin(a), -0.005))
        ring = ring.cut(hole)
    return ring


def _slew_ring_flange_mesh() -> object:
    fo, fi, fh = 0.132, 0.082, 0.014
    flange = cq.Workplane("XY").circle(fo).circle(fi).extrude(fh)
    for i in range(12):
        a = 2.0 * math.pi * i / 12.0
        pocket = cq.Workplane("XY").circle(0.009).extrude(0.008).translate(
            (0.112 * math.cos(a), 0.112 * math.sin(a), fh - 0.008))
        flange = flange.cut(pocket)
    return flange


def _eye_bolt_mesh() -> object:
    ring = (cq.Workplane("XZ").circle(0.014).circle(0.008).extrude(0.005, both=True)
            .translate((0.0, 0.0, 0.036)))
    stem = cq.Workplane("XY").circle(0.003).extrude(0.028)
    base = cq.Workplane("XY").circle(0.007).extrude(0.004)
    return ring.union(stem).union(base)


def _l_bracket_mesh() -> object:
    flange = cq.Workplane("XY").box(0.380, 0.014, 0.300).translate((0.0, -0.150, 0.150))
    seat = cq.Workplane("XY").box(0.340, 0.290, 0.014).translate((0.0, -0.001, -0.005))
    bracket = flange.union(seat)
    for x_sign in (-1, 1):
        gusset = cq.Workplane("XY").box(0.012, 0.136, 0.120).translate((x_sign * 0.145, -0.079, 0.060))
        bracket = bracket.union(gusset)
    seat_hole = cq.Workplane("XY").circle(0.052).extrude(0.040, both=True).translate((0.0, 0.0, -0.005))
    return bracket.cut(seat_hole)


def _seat_bearing_ring_mesh() -> object:
    outer = cq.Workplane("XY").circle(0.080).extrude(0.016)
    inner_cut = cq.Workplane("XY").circle(0.048).extrude(0.022)
    return outer.cut(inner_cut)


def _make_diff_housing_shell() -> object:
    R, t = 0.125, 0.008
    shell = cq.Workplane("XY").sphere(R).cut(cq.Workplane("XY").sphere(R - t))
    axle_bore = cq.Workplane("XY").transformed(rotate=(0, 90, 0)).circle(0.038).extrude(R * 3, both=True)
    shell = shell.cut(axle_bore)
    pinion_bore = (cq.Workplane("XY").transformed(offset=(0.0, 0.0, 0.092), rotate=(90, 0, 0))
                   .circle(0.048).extrude(R * 3, both=True))
    return shell.cut(pinion_bore)


def _toothed_pulley_mesh(radius, width, n_teeth=20, tooth_depth=0.0015) -> object:
    pts = []
    for i in range(n_teeth * 2):
        angle = 2.0 * math.pi * i / (n_teeth * 2)
        rr = radius + (tooth_depth if i % 2 == 0 else -tooth_depth)
        pts.append((rr * math.cos(angle), rr * math.sin(angle)))
    wp = cq.Workplane("XY").moveTo(pts[0][0], pts[0][1])
    for p in pts[1:]:
        wp = wp.lineTo(p[0], p[1])
    body = wp.close().extrude(width).translate((0.0, 0.0, -width / 2.0))
    flange_h, flange_r = 0.002, radius + 0.004
    f1 = cq.Workplane("XY").circle(flange_r).extrude(flange_h).translate((0.0, 0.0, -width / 2.0))
    f2 = cq.Workplane("XY").circle(flange_r).extrude(flange_h).translate((0.0, 0.0, width / 2.0 - flange_h))
    bore = cq.Workplane("XY").circle(radius * 0.25).extrude(width + 0.004).translate((0.0, 0.0, -(width + 0.004) / 2.0))
    return body.union(f1).union(f2).cut(bore)


def _belt_loop_mesh(x_pos, y_m, z_m, r_m, y_w, z_w, r_w, width=0.012, thickness=0.004) -> object:
    dy, dz = y_w - y_m, z_w - z_m
    d = math.sqrt(dy * dy + dz * dz)
    phi = math.atan2(dz, dy)
    alpha = math.asin(max(-1.0, min(1.0, (r_w - r_m) / d)))
    beta_top = phi + math.pi / 2.0 + alpha
    beta_bot = phi - math.pi / 2.0 - alpha
    beta_top_m = phi + math.pi / 2.0 - alpha
    beta_bot_m = phi - math.pi / 2.0 + alpha
    ht = thickness / 2.0
    mt_y, mt_z = y_m + r_m * math.cos(beta_top_m), z_m + r_m * math.sin(beta_top_m)
    mb_y, mb_z = y_m + r_m * math.cos(beta_bot_m), z_m + r_m * math.sin(beta_bot_m)
    wt_y, wt_z = y_w + r_w * math.cos(beta_top), z_w + r_w * math.sin(beta_top)
    wb_y, wb_z = y_w + r_w * math.cos(beta_bot), z_w + r_w * math.sin(beta_bot)

    def _thin_rect(y1, z1, y2, z2, w, t):
        seg_len = math.sqrt((y2 - y1) ** 2 + (z2 - z1) ** 2)
        seg_angle = math.atan2(z2 - z1, y2 - y1)
        return (cq.Workplane("XY").box(w, seg_len, t)
                .rotate((0, 0, 0), (1, 0, 0), math.degrees(seg_angle))
                .translate((0.0, (y1 + y2) / 2.0, (z1 + z2) / 2.0)))

    top_strip = _thin_rect(mt_y, mt_z, wt_y, wt_z, width, thickness)
    bot_strip = _thin_rect(wb_y, wb_z, mb_y, mb_z, width, thickness)
    motor_arc = (cq.Workplane("YZ").center(y_m, z_m).circle(r_m + ht).circle(r_m - ht)
                 .extrude(width).translate((-width / 2.0, 0.0, 0.0)))
    wheel_arc = (cq.Workplane("YZ").center(y_w, z_w).circle(r_w + ht).circle(r_w - ht)
                 .extrude(width).translate((-width / 2.0, 0.0, 0.0)))
    return motor_arc.union(wheel_arc).union(top_strip).union(bot_strip).translate((x_pos, 0.0, 0.0))


def _worm_screw_mesh() -> object:
    worm = Worm(module=2.0, lead_angle=14.0, n_threads=2, length=36.0)
    shape = worm.build(bore_d=6.0)
    shape = shape.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
    return shape.scale(0.001)


def _worm_wheel_disc_mesh() -> object:
    ww = SpurGear(module=2.0, teeth_number=22, width=18.0)
    shape = ww.build(bore_d=12.0)
    shape = shape.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
    return shape.scale(0.001)


def _worm_housing_mesh() -> object:
    body = cq.Workplane("XY").box(0.070, 0.078, 0.078).edges("|Z").fillet(0.006)
    flange = (cq.Workplane("XY").transformed(offset=(0.0, 0.0, 0.040)).box(0.086, 0.092, 0.008)
              .edges("|Z").fillet(0.004))
    body = body.union(flange)
    boss = cq.Workplane("XY").transformed(offset=(0.0, -0.045, 0.0)).box(0.040, 0.024, 0.040)
    body = body.union(boss)
    rib = cq.Workplane("XY").transformed(offset=(0.0, 0.0, -0.040)).box(0.060, 0.068, 0.006)
    return body.union(rib)


def _carriage_body_mesh() -> object:
    web = cq.Workplane("XY").transformed(offset=(0.0, 0.0, -0.060)).box(0.030, 0.080, 0.120)
    column = cq.Workplane("XY").circle(0.050).extrude(0.078).translate((0.0, 0.0, -0.060))
    web = web.union(column)
    beam = cq.Workplane("XY").transformed(offset=(0.0, 0.0, -0.120)).box(0.420, 0.040, 0.028)
    web = web.union(beam)
    for x_sign in (-1.0, 1.0):
        side_web = cq.Workplane("XY").transformed(offset=(x_sign * 0.200, 0.0, -0.096)).box(0.030, 0.040, 0.076)
        web = web.union(side_web)
    top_plate = cq.Workplane("XY").transformed(offset=(0.0, 0.0, 0.017)).box(0.260, 0.260, 0.010)
    return web.union(top_plate)


def _stator_drum_cq(radius_scale: float = 1.0) -> object:
    # Inner bore keeps fitting the unscaled stub axle (r=0.015); the radial
    # envelope scales with the wheel so the rotor shell still covers it.
    body = cq.Workplane("XY").circle(0.062 * radius_scale).circle(0.018).extrude(0.024, both=True)
    for j in range(14):
        fin = (cq.Workplane("XY").center(0.068 * radius_scale, 0.0)
               .rect(0.016 * radius_scale, 0.004).extrude(0.024, both=True)
               .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 360.0 * j / 14))
        body = body.union(fin)
    return body


def _cross_bar_cq() -> object:
    beam = cq.Workplane("XY").box(0.420, 0.050, 0.028)
    rear_arm = cq.Workplane("XY").box(0.055, 0.110, 0.028).translate((0.0, -0.080, 0.0))
    return beam.union(rear_arm)


def _rim_shell_cq(radius_scale: float = 1.0) -> object:
    # Bore scales with the carriage hub bearing (0.081*radius_scale) so the
    # 0.001 interference fit is preserved in both directions; only the outer
    # diameter grows/shrinks relative to the stator envelope.
    return (
        cq.Workplane("XY")
        .circle(0.100 * radius_scale)
        .circle(0.080 * radius_scale)
        .extrude(0.034, both=True)
    )


# ---- suspension helpers ----

_PIVOT_X_OFFSET = 0.205
_PIVOT_Z = -0.050
_WHEEL_X = 0.294
_WHEEL_Z = -0.105
_ARM_DX = _WHEEL_X - _PIVOT_X_OFFSET
_ARM_DZ = _WHEEL_Z - _PIVOT_Z
_ARM_LENGTH = math.sqrt(_ARM_DX ** 2 + _ARM_DZ ** 2)
_ARM_ANGLE_DEG = math.degrees(math.atan2(_ARM_DZ, _ARM_DX))
_SPRING_SEAT_T = 0.65


def _make_rocker_arm_mesh(side: int) -> object:
    sign = -1.0 if side == 0 else 1.0
    ax, az = sign * _ARM_DX, _ARM_DZ
    # Tilt the beam so it runs from the pivot (origin) down to the wheel end
    # (ax, az) with az<0: +Y rotation takes +X toward -Z, so the outboard side
    # needs -_ARM_ANGLE_DEG and the inboard side 180+_ARM_ANGLE_DEG.
    rot_angle = -_ARM_ANGLE_DEG if sign > 0 else (180.0 + _ARM_ANGLE_DEG)
    beam = cq.Workplane("XY").box(_ARM_LENGTH + 0.010, 0.038, 0.016).edges("|Y").fillet(0.004)
    beam = beam.rotate((0, 0, 0), (0, 1, 0), rot_angle).translate((ax / 2.0, 0.0, az / 2.0))
    # Workplane("XZ") extrudes toward -Y here, so translate +half to center the
    # pivot boss on the beam (y=0) instead of hanging it off one side.
    pivot_outer = cq.Workplane("XZ").circle(0.022).extrude(0.046).translate((0, 0.023, 0))
    pivot_bore = cq.Workplane("XZ").circle(0.015).extrude(0.056).translate((0, 0.028, 0))
    pivot = pivot_outer.cut(pivot_bore)
    # The axle housing sits at the beam's wheel end (x=ax, z=az); build it in the
    # YZ plane then drop it to the beam tip so it fuses with the beam.
    axle_outer = cq.Workplane("YZ").workplane(offset=ax - sign * 0.024).circle(0.026).extrude(sign * 0.048).translate((0.0, 0.0, az))
    axle_bore = cq.Workplane("YZ").workplane(offset=ax - sign * 0.030).circle(0.016).extrude(sign * 0.060).translate((0.0, 0.0, az))
    axle_housing = axle_outer.cut(axle_bore)
    return beam.union(pivot).union(axle_housing)


def _make_spring_mesh() -> object:
    n_coils, spring_radius, wire_radius, height = 6, 0.013, 0.0025, 0.058
    pts_per_coil = 28
    total_pts = n_coils * pts_per_coil + 1
    points = []
    for i in range(total_pts):
        t = i / (total_pts - 1)
        angle = 2.0 * math.pi * n_coils * t
        points.append((spring_radius * math.cos(angle), spring_radius * math.sin(angle), height * (t - 0.5)))
    tube_geo = tube_from_spline_points(points, radius=wire_radius, samples_per_segment=4,
                                       radial_segments=10, cap_ends=True, spline="catmull_rom")
    return mesh_from_geometry(tube_geo, "suspension_spring_coil")


# ===========================================================================
# Bevel-differential family
# ===========================================================================


def _emit_bevel_carrier_open(model, M) -> None:
    carrier = model.get_part("carrier")
    dm, mach, blue, bolt = M["dark_metal"], M["machined"], M["blue"], M["bolt_black"]
    carrier.visual(Box((0.300, 0.045, 0.030)), origin=Origin(xyz=(0.0, 0.135, 0.045)), material=dm, name="lower_bridge", material_class_id="metal.blackened_gunmetal")
    carrier.visual(Box((0.280, 0.030, 0.160)), origin=Origin(xyz=(0.0, 0.155, 0.130)), material=dm, name="rear_plate", material_class_id="metal.blackened_gunmetal")
    carrier.visual(Box((0.200, 0.045, 0.026)), origin=Origin(xyz=(0.0, 0.135, 0.272)), material=dm, name="top_bridge", material_class_id="metal.blackened_gunmetal")
    for sx in (-1.0, 1.0):
        x = sx * 0.155
        s = 0 if sx < 0 else 1
        carrier.visual(Box((0.018, 0.052, 0.190)), origin=Origin(xyz=(x, 0.102, 0.135)), material=dm, name=f"cheek_plate_{s}", material_class_id="metal.blackened_gunmetal")
        carrier.visual(Box((0.034, 0.064, 0.020)), origin=Origin(xyz=(x, 0.060, 0.130)), material=dm, name=f"bearing_lug_{s}", material_class_id="metal.blackened_gunmetal")
        carrier.visual(Box((0.034, 0.018, 0.075)), origin=Origin(xyz=(x, 0.023, 0.074)), material=dm, name=f"bearing_pedestal_{s}", material_class_id="metal.blackened_gunmetal")
        carrier.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.012, outer_radius=0.036, width=0.030), f"bearing_cap_{s}"),
                       origin=Origin(xyz=(x, 0.0, 0.130)), material=mach, name=f"bearing_cap_{s}", material_class_id="metal.aluminum_bare")
        # Axle sleeve/journal tube from the bearing out toward the wheel hub, on
        # the axle centerline: this is the carrier hardware that the wheel spin
        # axis rides on (the enclosed housing gets this from its axle_tube; the
        # open frame needs it explicitly so the wheel_spin axis is anchored).
        carrier.visual(Cylinder(radius=0.016, length=0.135), origin=Origin(xyz=(sx * 0.2375, 0.0, 0.130), rpy=ROT_Z_TO_X),
                       material=mach, name=f"axle_sleeve_{s}", material_class_id="metal.aluminum_bare")
        for z in (0.087, 0.173):
            carrier.visual(Cylinder(radius=0.006, length=0.005), origin=Origin(xyz=(x, 0.077, z), rpy=ROT_Z_TO_Y),
                           material=bolt, name=f"cap_bolt_{s}_{0 if z < 0.13 else 1}", material_class_id="metal.blackened_gunmetal")
    _emit_bevel_motor(carrier, M)
    for sx in (-1.0, 1.0):
        s = 0 if sx < 0 else 1
        carrier.visual(Box((0.018, 0.345, 0.018)), origin=Origin(xyz=(sx * 0.075, -0.020, 0.246)), material=dm, name=f"motor_support_rail_{s}", material_class_id="metal.blackened_gunmetal")
        carrier.visual(Cylinder(radius=0.005, length=0.006), origin=Origin(xyz=(sx * 0.075, -0.178, 0.246), rpy=ROT_Z_TO_Y), material=bolt, name=f"motor_mount_bolt_{s}", material_class_id="metal.blackened_gunmetal")
        carrier.visual(Box((0.020, 0.030, 0.072)), origin=Origin(xyz=(sx * 0.090, 0.145, 0.235)), material=dm, name=f"top_bridge_post_{s}", material_class_id="metal.blackened_gunmetal")


def _emit_bevel_motor(carrier, M) -> None:
    blue, dm = M["blue"], M["dark_metal"]
    carrier.visual(Cylinder(radius=0.050, length=0.120), origin=Origin(xyz=(0.0, -0.255, 0.235), rpy=ROT_Z_TO_Y), material=blue, name="motor_can", material_class_id="metal.paint_coated")
    carrier.visual(Cylinder(radius=0.054, length=0.014), origin=Origin(xyz=(0.0, -0.188, 0.235), rpy=ROT_Z_TO_Y), material=blue, name="motor_front_cap", material_class_id="metal.paint_coated")
    carrier.visual(Cylinder(radius=0.040, length=0.018), origin=Origin(xyz=(0.0, -0.320, 0.235), rpy=ROT_Z_TO_Y), material=blue, name="motor_rear_cap", material_class_id="metal.paint_coated")
    for i, z in enumerate((0.195, 0.215, 0.255, 0.275)):
        carrier.visual(Box((0.092, 0.012, 0.006)), origin=Origin(xyz=(0.0, -0.255, z)), material=blue, name=f"motor_cooling_fin_{i}", material_class_id="metal.paint_coated")
    carrier.visual(Box((0.160, 0.016, 0.030)), origin=Origin(xyz=(0.0, -0.187, 0.235)), material=dm, name="motor_saddle", material_class_id="metal.blackened_gunmetal")


def _emit_bevel_carrier_enclosed(model, M) -> None:
    carrier = model.get_part("carrier")
    cast, mach, dm, bolt = M["cast_iron"], M["machined"], M["dark_metal"], M["bolt_black"]
    carrier.visual(mesh_from_cadquery(_make_diff_housing_shell(), "diff_housing_shell"),
                   origin=Origin(xyz=(0.0, 0.0, 0.130)), material=cast, name="diff_housing", material_class_id="metal.cast_iron_bare")
    for i, sx in enumerate((-1.0, 1.0)):
        tube_cx = sx * 0.205
        carrier.visual(Cylinder(radius=0.040, length=0.170), origin=Origin(xyz=(tube_cx, 0.0, 0.130), rpy=ROT_Z_TO_X), material=cast, name=f"axle_tube_{i}", material_class_id="metal.cast_iron_bare")
        carrier.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.038, outer_radius=0.054, width=0.014), f"axle_flange_{i}"),
                       origin=Origin(xyz=(sx * 0.118, 0.0, 0.130)), material=cast, name=f"axle_flange_{i}", material_class_id="metal.cast_iron_bare")
        end_x = sx * 0.282
        carrier.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.034, outer_radius=0.050, width=0.012), f"axle_end_flange_{i}"),
                       origin=Origin(xyz=(end_x, 0.0, 0.130)), material=cast, name=f"axle_end_flange_{i}", material_class_id="metal.cast_iron_bare")
        for j, angle_deg in enumerate((0, 90, 180, 270)):
            a = math.radians(angle_deg)
            carrier.visual(Cylinder(radius=0.004, length=0.006), origin=Origin(xyz=(end_x + sx * 0.008, 0.042 * math.cos(a), 0.130 + 0.042 * math.sin(a)), rpy=ROT_Z_TO_X), material=bolt, name=f"axle_bolt_{i}_{j}", material_class_id="metal.blackened_gunmetal")
    carrier.visual(Cylinder(radius=0.055, length=0.098), origin=Origin(xyz=(0.0, -0.134, 0.222), rpy=ROT_Z_TO_Y), material=cast, name="pinion_nose", material_class_id="metal.cast_iron_bare")
    carrier.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.053, outer_radius=0.068, width=0.012), "pinion_flange"),
                   origin=Origin(xyz=(0.0, -0.082, 0.222), rpy=ROT_X_TO_Y), material=cast, name="pinion_flange", material_class_id="metal.cast_iron_bare")
    carrier.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.053, outer_radius=0.068, width=0.010), "pinion_end_flange"),
                   origin=Origin(xyz=(0.0, -0.180, 0.222), rpy=ROT_X_TO_Y), material=cast, name="pinion_end_flange", material_class_id="metal.cast_iron_bare")
    cover_y = 0.122
    carrier.visual(Cylinder(radius=0.068, length=0.006), origin=Origin(xyz=(0.0, cover_y, 0.130), rpy=ROT_Z_TO_Y), material=mach, name="inspection_cover", material_class_id="metal.aluminum_bare")
    carrier.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.054, outer_radius=0.068, width=0.002), "cover_gasket"),
                   origin=Origin(xyz=(0.0, cover_y - 0.004, 0.130), rpy=ROT_X_TO_Y), material=dm, name="cover_gasket", material_class_id="metal.blackened_gunmetal")
    for i in range(8):
        a = 2.0 * math.pi * i / 8.0
        carrier.visual(Cylinder(radius=0.005, length=0.010), origin=Origin(xyz=(0.056 * math.cos(a), cover_y + 0.005, 0.130 + 0.056 * math.sin(a)), rpy=ROT_Z_TO_Y), material=bolt, name=f"cover_bolt_{i}", material_class_id="metal.blackened_gunmetal")
    for i, angle_deg in enumerate((45, 135, 225, 315)):
        a = math.radians(angle_deg)
        carrier.visual(Box((0.006, 0.080, 0.010)), origin=Origin(xyz=(0.120 * math.cos(a), 0.0, 0.130 + 0.120 * math.sin(a)), rpy=(0.0, 0.0, a)), material=cast, name=f"housing_rib_{i}", material_class_id="metal.cast_iron_bare")
    _emit_bevel_motor(carrier, M)
    for i, sx in enumerate((-1.0, 1.0)):
        carrier.visual(Box((0.026, 0.100, 0.020)), origin=Origin(xyz=(sx * 0.068, -0.140, 0.228)), material=dm, name=f"motor_bracket_{i}", material_class_id="metal.blackened_gunmetal")
        carrier.visual(Cylinder(radius=0.005, length=0.006), origin=Origin(xyz=(sx * 0.068, -0.186, 0.228), rpy=ROT_Z_TO_Y), material=bolt, name=f"motor_mount_bolt_{i}", material_class_id="metal.blackened_gunmetal")
    carrier.visual(Box((0.110, 0.014, 0.018)), origin=Origin(xyz=(0.0, -0.155, 0.228)), material=dm, name="motor_cross_brace", material_class_id="metal.blackened_gunmetal")


def _emit_bevel_wheels(model, M, *, spider: bool, radius_scale: float, tread_scale: float) -> None:
    rubber, mach, green, red = M["rubber"], M["machined"], M["green"], M["red"]
    left = model.part("left_wheel")
    left.visual(_make_tire_mesh_a("left_tire", radius_scale=radius_scale, tread_scale=tread_scale), material=rubber, name="treaded_tire", material_class_id="rubber.directional_grooved")
    left.visual(_make_rim_mesh_a("left_rim", radius_scale=radius_scale), material=mach, name="split_spoke_rim", material_class_id="metal.aluminum_bare")
    # spider variant extends the green half shaft to reach the left side gear.
    if spider:
        left.visual(Cylinder(radius=0.013, length=0.370), origin=Origin(xyz=(0.185, 0.0, 0.0), rpy=ROT_Z_TO_X), material=green, name="green_half_shaft", material_class_id="metal.paint_coated")
    else:
        left.visual(Cylinder(radius=0.013, length=0.310), origin=Origin(xyz=(0.155, 0.0, 0.0), rpy=ROT_Z_TO_X), material=green, name="green_half_shaft", material_class_id="metal.paint_coated")
    left.visual(Cylinder(radius=0.022, length=0.020), origin=Origin(xyz=(0.180, 0.0, 0.0), rpy=ROT_Z_TO_X), material=mach, name="shaft_collar", material_class_id="metal.aluminum_bare")
    right = model.part("right_wheel")
    right.visual(_make_tire_mesh_a("right_tire", radius_scale=radius_scale, tread_scale=tread_scale), material=rubber, name="treaded_tire", material_class_id="rubber.directional_grooved")
    right.visual(_make_rim_mesh_a("right_rim", radius_scale=radius_scale), material=mach, name="split_spoke_rim", material_class_id="metal.aluminum_bare")
    right.visual(Cylinder(radius=0.013, length=0.405), origin=Origin(xyz=(-0.2025, 0.0, 0.0), rpy=ROT_Z_TO_X), material=red, name="red_half_shaft", material_class_id="metal.paint_coated")
    right.visual(Cylinder(radius=0.022, length=0.020), origin=Origin(xyz=(-0.180, 0.0, 0.0), rpy=ROT_Z_TO_X), material=mach, name="shaft_collar", material_class_id="metal.aluminum_bare")


def _emit_bevel_gears_single(model, M) -> None:
    orange, brass, yellow = M["orange"], M["brass"], M["yellow"]
    og = model.part("orange_gear")
    og.visual(mesh_from_geometry(_toothed_bevel_mesh(inner_radius=0.024, root_radius=0.086, tooth_height=0.016, width=0.036, teeth=34, cone_delta=0.010), "orange_bevel_teeth"), material=orange, name="orange_bevel_teeth", material_class_id="metal.paint_coated")
    og.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.011, outer_radius=0.034, width=0.056), "orange_hub"), material=orange, name="orange_hub", material_class_id="metal.paint_coated")
    bg = model.part("brass_side_gear")
    bg.visual(mesh_from_geometry(_toothed_bevel_mesh(inner_radius=0.018, root_radius=0.045, tooth_height=0.010, width=0.030, teeth=18, cone_delta=0.006), "brass_side_teeth"), material=brass, name="brass_side_teeth", material_class_id="metal.brass_polished")
    bg.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.011, outer_radius=0.026, width=0.046), "brass_hub"), material=brass, name="brass_hub", material_class_id="metal.brass_polished")
    _emit_input_pinion(model, M)


def _emit_bevel_gears_spider(model, M, n: int) -> None:
    orange, brass, dm, mach = M["orange"], M["brass"], M["dark_metal"], M["machined"]
    og = model.part("orange_gear")
    og.visual(mesh_from_geometry(_toothed_bevel_mesh(inner_radius=0.024, root_radius=0.086, tooth_height=0.016, width=0.036, teeth=34, cone_delta=0.010), "orange_bevel_teeth"), material=orange, name="orange_bevel_teeth", material_class_id="metal.paint_coated")
    og.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.011, outer_radius=0.034, width=0.056), "orange_hub"), material=orange, name="orange_hub", material_class_id="metal.paint_coated")
    planet_r = 0.052
    for i in range(n):
        angle = 2.0 * math.pi * i / n
        y = planet_r * math.cos(angle)
        z = planet_r * math.sin(angle)
        # Radial arm from center to the planet position (cylinder axis rotated
        # about X so its local +Z points along the radial (0, cos, sin) direction).
        og.visual(Cylinder(radius=0.007, length=planet_r), origin=Origin(xyz=(0.0, y / 2.0, z / 2.0), rpy=(angle - math.pi / 2.0, 0.0, 0.0)), material=dm, name=f"spider_arm_{i}", material_class_id="metal.blackened_gunmetal")
        og.visual(Cylinder(radius=0.005, length=0.026), origin=Origin(xyz=(0.0, y, z)), material=mach, name=f"spider_pin_{i}", material_class_id="metal.aluminum_bare")
    og.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.012, outer_radius=0.020, width=0.040), "spider_hub"), material=dm, name="spider_hub", material_class_id="metal.blackened_gunmetal")
    for gear_name, x_off in (("left_side_gear", 0.005), ("right_side_gear", 0.043)):
        side = model.part(gear_name)
        side.visual(mesh_from_geometry(_toothed_bevel_mesh(inner_radius=0.018, root_radius=0.045, tooth_height=0.010, width=0.024, teeth=18, cone_delta=0.006), f"{gear_name}_teeth"), origin=Origin(xyz=(x_off, 0.0, 0.0)), material=brass, name=f"{gear_name}_teeth", material_class_id="metal.brass_polished")
        side.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.011, outer_radius=0.026, width=0.040), f"{gear_name}_hub"), origin=Origin(xyz=(x_off, 0.0, 0.0)), material=brass, name=f"{gear_name}_hub", material_class_id="metal.brass_polished")
    for i in range(n):
        planet = model.part(f"planet_pinion_{i}")
        planet.visual(mesh_from_geometry(_toothed_bevel_mesh(inner_radius=0.008, root_radius=0.022, tooth_height=0.008, width=0.020, teeth=12, cone_delta=0.004), f"planet_pinion_{i}_teeth"), origin=Origin(rpy=(0.0, -math.pi / 2.0, 0.0)), material=brass, name=f"planet_pinion_{i}_teeth", material_class_id="metal.brass_polished")
        planet.visual(mesh_from_geometry(_annular_cylinder_mesh(inner_radius=0.006, outer_radius=0.014, width=0.026), f"planet_pinion_{i}_hub"), origin=Origin(rpy=(0.0, -math.pi / 2.0, 0.0)), material=brass, name=f"planet_pinion_{i}_hub", material_class_id="metal.brass_polished")
    _emit_input_pinion(model, M)


def _emit_input_pinion(model, M) -> None:
    yellow, brass = M["yellow"], M["brass"]
    ip = model.part("input_pinion")
    ip.visual(mesh_from_geometry(_toothed_bevel_mesh(inner_radius=0.006, root_radius=0.039, tooth_height=0.008, width=0.038, teeth=14, cone_delta=0.003), "input_pinion_teeth"), origin=Origin(rpy=(0.0, 0.0, math.pi / 2.0)), material=yellow, name="input_pinion_teeth", material_class_id="metal.paint_coated")
    ip.visual(Cylinder(radius=0.009, length=0.190), origin=Origin(xyz=(0.0, -0.058, 0.0), rpy=ROT_Z_TO_Y), material=yellow, name="input_shaft", material_class_id="metal.paint_coated")
    ip.visual(Cylinder(radius=0.017, length=0.018), origin=Origin(xyz=(0.0, -0.010, 0.0), rpy=ROT_Z_TO_Y), material=brass, name="pinion_collar", material_class_id="metal.brass_polished")


def _wire_bevel_single(model) -> None:
    carrier = model.get_part("carrier")
    spin = MotionLimits(effort=12.0, velocity=20.0)
    model.articulation("left_wheel_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("left_wheel"), origin=Origin(xyz=(-0.360, 0.0, 0.130)), axis=(1.0, 0.0, 0.0), motion_limits=spin)
    model.articulation("right_wheel_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("right_wheel"), origin=Origin(xyz=(0.360, 0.0, 0.130)), axis=(1.0, 0.0, 0.0), motion_limits=spin, mimic=Mimic(joint="orange_gear_spin", multiplier=1.0))
    model.articulation("orange_gear_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("orange_gear"), origin=Origin(xyz=(0.024, 0.0, 0.130)), axis=(1.0, 0.0, 0.0), motion_limits=spin, mimic=Mimic(joint="input_pinion_spin", multiplier=-0.42))
    model.articulation("brass_gear_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("brass_side_gear"), origin=Origin(xyz=(-0.050, 0.0, 0.130)), axis=(1.0, 0.0, 0.0), motion_limits=spin, mimic=Mimic(joint="orange_gear_spin", multiplier=-1.0))
    model.articulation("input_pinion_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("input_pinion"), origin=Origin(xyz=(0.0, -0.115, 0.222)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=8.0, velocity=25.0))


def _wire_bevel_spider(model, n: int) -> None:
    carrier = model.get_part("carrier")
    spin = MotionLimits(effort=12.0, velocity=20.0)
    model.articulation("left_wheel_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("left_wheel"), origin=Origin(xyz=(-0.360, 0.0, 0.130)), axis=(1.0, 0.0, 0.0), motion_limits=spin, mimic=Mimic(joint="left_side_gear_spin", multiplier=1.0))
    model.articulation("right_wheel_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("right_wheel"), origin=Origin(xyz=(0.360, 0.0, 0.130)), axis=(1.0, 0.0, 0.0), motion_limits=spin, mimic=Mimic(joint="right_side_gear_spin", multiplier=1.0))
    model.articulation("orange_gear_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("orange_gear"), origin=Origin(xyz=(0.024, 0.0, 0.130)), axis=(1.0, 0.0, 0.0), motion_limits=spin, mimic=Mimic(joint="input_pinion_spin", multiplier=-0.42))
    model.articulation("left_side_gear_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("left_side_gear"), origin=Origin(xyz=(0.005, 0.0, 0.130)), axis=(1.0, 0.0, 0.0), motion_limits=spin, mimic=Mimic(joint="orange_gear_spin", multiplier=-1.0))
    model.articulation("right_side_gear_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("right_side_gear"), origin=Origin(xyz=(0.043, 0.0, 0.130)), axis=(1.0, 0.0, 0.0), motion_limits=spin, mimic=Mimic(joint="orange_gear_spin", multiplier=-1.0))
    orange_gear = model.get_part("orange_gear")
    for i in range(n):
        angle = 2.0 * math.pi * i / n
        y = 0.052 * math.cos(angle)
        z = 0.052 * math.sin(angle)
        # Planet spins about its radial spider pin (0, cos, sin). The pinion is
        # carried by the spider cross, which is part of the rotating ring-gear
        # cage (orange_gear); parenting the joint there anchors its axis on the
        # real journal pin and lets the pinion orbit with the cage.
        axis = (0.0, math.cos(angle), math.sin(angle))
        model.articulation(f"planet_pinion_{i}_spin", ArticulationType.CONTINUOUS, parent=orange_gear, child=model.get_part(f"planet_pinion_{i}"), origin=Origin(xyz=(0.0, y, z)), axis=axis, motion_limits=spin, mimic=Mimic(joint="orange_gear_spin", multiplier=-1.5))
    model.articulation("input_pinion_spin", ArticulationType.CONTINUOUS, parent=carrier, child=model.get_part("input_pinion"), origin=Origin(xyz=(0.0, -0.115, 0.222)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=8.0, velocity=25.0))


def _build_bevel_family(model, r, M) -> None:
    model.part("carrier")
    if r.chassis_mount == "enclosed_diff_housing":
        _emit_bevel_carrier_enclosed(model, M)
    else:
        _emit_bevel_carrier_open(model, M)
    spider = r.planet_pinions > 0
    _emit_bevel_wheels(
        model, M, spider=spider,
        radius_scale=r.wheel_radius_scale, tread_scale=r.tire_tread_scale,
    )
    if spider:
        _emit_bevel_gears_spider(model, M, r.planet_pinions)
        _wire_bevel_spider(model, r.planet_pinions)
    else:
        _emit_bevel_gears_single(model, M)
        _wire_bevel_single(model)


# ===========================================================================
# Dual-drive family
# ===========================================================================

_STEER_Z = {"top_mount_plate": 0.235, "side_flange_bracket": 0.0}


def _build_top_mount_plate(model, M, *, slew: bool, rigid: bool = False) -> None:
    plate = model.get_part("mount_plate")
    ba, da, steel = M["machined"], M["dark_anodized"], M["steel"]
    if slew:
        plate.visual(mesh_from_cadquery(_mounting_plate_mesh(center_hole=0.082, bearing_bolt_r=0.112, bearing_bolt_n=12), "rounded_mount_plate", tolerance=0.0008),
                     origin=Origin(xyz=(0.0, 0.0, 0.300)), material=ba, name="rounded_plate", material_class_id="metal.aluminum_bare")
        plate.visual(mesh_from_cadquery(_slew_ring_bearing_mesh(), "slew_ring_bearing", tolerance=0.0008),
                     origin=Origin(xyz=(0.0, 0.0, 0.263)), material=da, name="outer_bearing_ring", material_class_id="metal.blackened_gunmetal")
        bolt_r, bolt_n = 0.112, 12
    else:
        plate.visual(mesh_from_cadquery(_mounting_plate_mesh(), "rounded_mount_plate", tolerance=0.0008),
                     origin=Origin(xyz=(0.0, 0.0, 0.300)), material=ba, name="rounded_plate", material_class_id="metal.aluminum_bare")
        plate.visual(mesh_from_cadquery(_bearing_ring_mesh(), "outer_swivel_bearing", tolerance=0.0008),
                     origin=Origin(xyz=(0.0, 0.0, 0.277)), material=da, name="outer_bearing_ring", material_class_id="metal.blackened_gunmetal")
        bolt_r, bolt_n = 0.078, 10
    for i, (x, y) in enumerate([(-0.265, -0.165), (0.265, -0.165), (-0.265, 0.165), (0.265, 0.165), (-0.160, -0.185), (0.160, -0.185), (-0.160, 0.185), (0.160, 0.185)]):
        _add_cyl(plate, 0.010, 0.004, (x, y, 0.311), material=steel, name=f"plate_screw_{i}")
    for i in range(bolt_n):
        a = 2.0 * math.pi * i / bolt_n
        _add_cyl(plate, 0.0055, 0.003, (bolt_r * math.cos(a), bolt_r * math.sin(a), 0.3105), material=steel, name=f"bearing_screw_{i}")
    for i, (x, y, yaw) in enumerate([(-0.095, 0.075, 0.0), (0.105, 0.075, 0.45), (0.000, -0.105, -0.35)]):
        plate.visual(mesh_from_cadquery(_eye_bolt_mesh(), f"lift_eye_{i}", tolerance=0.0006), origin=Origin(xyz=(x, y, 0.309), rpy=(0.0, 0.0, yaw)), material=da, name=f"lift_eye_{i}", material_class_id="metal.blackened_gunmetal")
    # Rigid mounts weld the carriage directly to the plate: drop a central boss
    # (wider than the center hole so it fuses to the plate rim / bearing ring)
    # down to the steering-joint plane so the FIXED joint origin sits on real
    # plate metal. Swivel/caster variants keep the open bearing bore instead.
    if rigid:
        _add_cyl(plate, 0.056, 0.058, (0.0, 0.0, 0.264), material=da, name="king_pin_boss")


def _build_side_flange(model, M, *, rigid: bool = False) -> None:
    plate = model.get_part("mount_plate")
    ba, da, steel = M["machined"], M["dark_anodized"], M["steel"]
    plate.visual(mesh_from_cadquery(_l_bracket_mesh(), "l_bracket_body", tolerance=0.0008), origin=Origin(xyz=(0.0, 0.0, 0.0)), material=ba, name="bracket_body", material_class_id="metal.aluminum_bare")
    plate.visual(mesh_from_cadquery(_seat_bearing_ring_mesh(), "seat_swivel_bearing", tolerance=0.0008), origin=Origin(xyz=(0.0, 0.0, 0.002)), material=da, name="seat_bearing_ring", material_class_id="metal.blackened_gunmetal")
    for i in range(8):
        x = -0.130 + (i % 2) * 0.260
        z = 0.060 + (i // 2) * 0.070
        _add_cyl(plate, 0.008, 0.005, (x, -0.141, z), rpy=(math.pi / 2.0, 0.0, 0.0), material=steel, name=f"flange_screw_{i}")
    for i, (x, yaw) in enumerate([(-0.080, 0.0), (0.080, 0.0)]):
        plate.visual(mesh_from_cadquery(_eye_bolt_mesh(), f"lift_eye_{i}", tolerance=0.0006), origin=Origin(xyz=(x, -0.150, 0.300), rpy=(0.0, 0.0, yaw)), material=da, name=f"lift_eye_{i}", material_class_id="metal.blackened_gunmetal")
    # Rigid mount: central boss (wider than the seat bore) at the steering-joint
    # plane (steer_z = 0.0) so the FIXED joint origin sits on real seat metal.
    if rigid:
        _add_cyl(plate, 0.056, 0.024, (0.0, 0.0, 0.008), material=da, name="king_pin_boss")


def _emit_std_swivel_interface(carriage, M, *, attach: str, caster: bool, post_bottom_z: float = -0.074) -> None:
    """Swivel post + bearing chain + attachment (posts / standoffs / slew flange).

    ``post_bottom_z`` sets how far the top-plate support posts reach down so they
    land on the carriage body (thin carriages, e.g. the hub-drive cross bar, need
    longer posts than the tall gearbox/belt/worm bodies).
    """
    da, steel = M["dark_anodized"], M["steel"]
    if caster:
        carriage.visual(mesh_from_cadquery(_slew_ring_flange_mesh(), "slew_ring_flange", tolerance=0.0008), origin=Origin(xyz=(0.0, 0.0, 0.014)), material=steel, name="inner_bearing_flange", material_class_id="metal.steel_bare")
        _add_cyl(carriage, 0.082, 0.054, (0.0, 0.0, 0.005), material=da, name="swivel_post")
        _add_cyl(carriage, 0.068, 0.060, (0.0, 0.0, -0.048), material=steel, name="bearing_pedestal")
        return
    _add_cyl(carriage, 0.049, 0.050, (0.0, 0.0, 0.006), material=da, name="swivel_post")
    _add_cyl(carriage, 0.066, 0.012, (0.0, 0.0, -0.023), material=steel, name="inner_bearing_flange")
    _add_cyl(carriage, 0.055, 0.055, (0.0, 0.0, -0.045), material=steel, name="bearing_pedestal")
    if attach == "seat":
        for i, (x, y_pos) in enumerate([(-0.100, -0.020), (0.100, -0.020), (-0.050, -0.060), (0.050, -0.060)]):
            _add_cyl(carriage, 0.010, 0.058, (x, y_pos, -0.040), material=steel, name=f"seat_standoff_{i}")
    else:  # top plate posts
        post_top_z = 0.046
        post_len = post_top_z - post_bottom_z
        post_cz = 0.5 * (post_top_z + post_bottom_z)
        for i, (x, y) in enumerate([(-0.120, 0.0), (0.120, 0.0), (0.0, -0.120)]):
            _add_cyl(carriage, 0.010, post_len, (x, y, post_cz), material=steel, name=f"top_support_post_{i}")
            _add_cyl(carriage, 0.014, 0.020, (x, y, 0.046), material=steel, name=f"top_support_pad_{i}")


def _emit_gearbox_body(carriage, M) -> None:
    ba, steel = M["machined"], M["steel"]
    carriage.visual(Box((0.300, 0.135, 0.078)), origin=Origin(xyz=(0.0, -0.010, -0.108)), material=ba, name="center_gearbox", material_class_id="metal.aluminum_bare")
    carriage.visual(Box((0.105, 0.155, 0.120)), origin=Origin(xyz=(-0.180, -0.012, -0.112)), material=ba, name="side_gearbox_0", material_class_id="metal.aluminum_bare")
    carriage.visual(Box((0.105, 0.155, 0.120)), origin=Origin(xyz=(0.180, -0.012, -0.112)), material=ba, name="side_gearbox_1", material_class_id="metal.aluminum_bare")
    carriage.visual(Box((0.175, 0.030, 0.125)), origin=Origin(xyz=(-0.105, 0.070, -0.112)), material=steel, name="front_yoke_0", material_class_id="metal.steel_bare")
    carriage.visual(Box((0.175, 0.030, 0.125)), origin=Origin(xyz=(0.105, 0.070, -0.112)), material=steel, name="front_yoke_1", material_class_id="metal.steel_bare")
    carriage.visual(Box((0.255, 0.034, 0.035)), origin=Origin(xyz=(0.0, 0.076, -0.046)), material=steel, name="upper_cross_brace", material_class_id="metal.steel_bare")


def _emit_gearbox_motor_axles(carriage, M, *, outboard_axle: bool = True) -> None:
    da, steel, blackr = M["dark_anodized"], M["steel"], M["black_rubber"]
    motor_rpy = ROT_Z_TO_X
    _add_cyl(carriage, 0.047, 0.205, (0.0, -0.107, -0.106), rpy=motor_rpy, material=da, name="motor_can")
    _add_cyl(carriage, 0.050, 0.010, (-0.108, -0.107, -0.106), rpy=motor_rpy, material=steel, name="motor_endcap_0")
    _add_cyl(carriage, 0.050, 0.010, (0.108, -0.107, -0.106), rpy=motor_rpy, material=steel, name="motor_endcap_1")
    for i, z in enumerate([-0.128, -0.106, -0.084]):
        carriage.visual(Box((0.226, 0.007, 0.007)), origin=Origin(xyz=(0.0, -0.156, z)), material=blackr, name=f"motor_fin_{i}", material_class_id="rubber.smooth_plain")
    # Fixed outboard axle stubs reach toward the wheels; on the sprung rocker the
    # wheels are carried by the rockers (which articulate), so these are dropped
    # to avoid the fixed stubs colliding with the swinging wheels.
    if outboard_axle:
        _add_cyl(carriage, 0.014, 0.031, (-0.237, 0.0, -0.105), rpy=motor_rpy, material=steel, name="axle_stub_0")
        _add_cyl(carriage, 0.014, 0.031, (0.237, 0.0, -0.105), rpy=motor_rpy, material=steel, name="axle_stub_1")
        _add_cyl(carriage, 0.024, 0.014, (-0.220, 0.0, -0.105), rpy=motor_rpy, material=steel, name="axle_bearing_0")
        _add_cyl(carriage, 0.024, 0.014, (0.220, 0.0, -0.105), rpy=motor_rpy, material=steel, name="axle_bearing_1")
    for side, x_face in enumerate([-0.2325, 0.2325]):
        sign = -1.0 if x_face < 0 else 1.0
        for j, (y, z) in enumerate([(-0.055, -0.070), (0.045, -0.070), (-0.055, -0.145), (0.045, -0.145)]):
            _add_cyl(carriage, 0.006, 0.004, (x_face + sign * 0.002, y, z), rpy=motor_rpy, material=da, name=f"gearbox_screw_{side}_{j}")


def _emit_carriage_gearbox(model, r, M) -> None:
    carriage = model.get_part("drive_carriage")
    _emit_gearbox_body(carriage, M)
    caster = r.steering == "continuous_caster"
    attach = "seat" if r.chassis_mount == "side_flange_bracket" else "top"
    _emit_std_swivel_interface(carriage, M, attach=attach, caster=caster)
    _emit_gearbox_motor_axles(carriage, M, outboard_axle=(r.wheel_travel != "sprung_rocker"))


def _emit_carriage_belt(model, r, M) -> None:
    carriage = model.get_part("drive_carriage")
    ba, da, steel, blackr = M["machined"], M["dark_anodized"], M["steel"], M["black_rubber"]
    belt_rubber = M["belt_rubber"]
    motor_rpy = ROT_Z_TO_X
    carriage.visual(Box((0.240, 0.090, 0.008)), origin=Origin(xyz=(0.0, -0.015, -0.062)), material=ba, name="carriage_base", material_class_id="metal.aluminum_bare")
    carriage.visual(Box((0.060, 0.080, 0.070)), origin=Origin(xyz=(-0.108, -0.050, -0.025)), material=ba, name="motor_mount_0", material_class_id="metal.aluminum_bare")
    carriage.visual(Box((0.060, 0.080, 0.070)), origin=Origin(xyz=(0.108, -0.050, -0.025)), material=ba, name="motor_mount_1", material_class_id="metal.aluminum_bare")
    carriage.visual(Box((0.140, 0.045, 0.085)), origin=Origin(xyz=(-0.105, 0.047, -0.058)), material=steel, name="front_yoke_0", material_class_id="metal.steel_bare")
    carriage.visual(Box((0.140, 0.045, 0.085)), origin=Origin(xyz=(0.105, 0.047, -0.058)), material=steel, name="front_yoke_1", material_class_id="metal.steel_bare")
    carriage.visual(Box((0.200, 0.032, 0.028)), origin=Origin(xyz=(0.0, 0.065, -0.018)), material=steel, name="upper_cross_brace", material_class_id="metal.steel_bare")
    _emit_std_swivel_interface(carriage, M, attach="top", caster=False)
    carriage.visual(Box((0.024, 0.066, 0.008)), origin=Origin(xyz=(0.0, -0.087, -0.062)), material=ba, name="rear_bracket", material_class_id="metal.aluminum_bare")
    belt_plane_x = 0.236
    motor_y, motor_z = -0.050, 0.000
    axle_y, axle_z = 0.0, -0.105
    r_motor_pulley, r_wheel_pulley = 0.018, 0.048
    motor_outer_end = 0.205
    for side, sx in enumerate([-1.0, 1.0]):
        mx = sx * 0.155
        _add_cyl(carriage, 0.038, 0.100, (mx, motor_y, motor_z), rpy=motor_rpy, material=da, name=f"motor_can_{side}")
        _add_cyl(carriage, 0.040, 0.008, (mx - sx * 0.054, motor_y, motor_z), rpy=motor_rpy, material=steel, name=f"motor_endcap_{side}")
        for fi, fz in enumerate([-0.022, 0.0, 0.022]):
            carriage.visual(Box((0.090, 0.006, 0.006)), origin=Origin(xyz=(mx, motor_y - 0.035, motor_z + fz)), material=blackr, name=f"motor_fin_{side}_{fi}", material_class_id="rubber.smooth_plain")
        shaft_len = belt_plane_x - motor_outer_end
        shaft_cx = sx * (motor_outer_end + belt_plane_x) / 2.0
        _add_cyl(carriage, 0.008, shaft_len, (shaft_cx, motor_y, motor_z), rpy=motor_rpy, material=steel, name=f"motor_shaft_{side}")
    for side, sx in enumerate([-1.0, 1.0]):
        px = sx * belt_plane_x
        carriage.visual(mesh_from_cadquery(_toothed_pulley_mesh(r_motor_pulley, 0.014, n_teeth=16), f"motor_pulley_{side}_mesh", tolerance=0.0005), origin=Origin(xyz=(px, motor_y, motor_z), rpy=motor_rpy), material=da, name=f"motor_pulley_{side}", material_class_id="metal.blackened_gunmetal")
    for side, sx in enumerate([-1.0, 1.0]):
        px = sx * belt_plane_x
        carriage.visual(mesh_from_cadquery(_belt_loop_mesh(px, motor_y, motor_z, r_motor_pulley, axle_y, axle_z, r_wheel_pulley, width=0.012, thickness=0.004), f"belt_loop_{side}_mesh", tolerance=0.0005), material=belt_rubber, name=f"belt_loop_{side}", material_class_id="rubber.directional_grooved")
    for side, sx in enumerate([-1.0, 1.0]):
        px = sx * belt_plane_x
        _add_cyl(carriage, 0.012, 0.014, (px, -0.068, -0.058), rpy=motor_rpy, material=steel, name=f"idler_boss_{side}")
        _add_cyl(carriage, 0.006, 0.020, (px, -0.068, -0.058), rpy=motor_rpy, material=da, name=f"idler_pin_{side}")
    for side, sx in enumerate([-1.0, 1.0]):
        # Inboard of the wheel pulley (world x=+-0.236) so the fixed bearing does
        # not intersect the rotating pulley disc.
        bx = sx * 0.190
        _add_cyl(carriage, 0.028, 0.018, (bx, 0.0, -0.105), rpy=motor_rpy, material=steel, name=f"axle_bearing_{side}")
        carriage.visual(Box((0.055, 0.035, 0.012)), origin=Origin(xyz=(sx * 0.193, 0.035, -0.090)), material=ba, name=f"axle_arm_{side}", material_class_id="metal.aluminum_bare")
    for side, sx in enumerate([-1.0, 1.0]):
        bx = sx * 0.108
        for j, (dy, dz) in enumerate([(0.025, 0.015), (-0.025, 0.015), (0.025, -0.035), (-0.025, -0.035)]):
            _add_cyl(carriage, 0.005, 0.004, (bx + sx * 0.032, motor_y + dy, motor_z + dz), rpy=motor_rpy, material=da, name=f"motor_bolt_{side}_{j}")


def _emit_carriage_worm(model, r, M) -> None:
    carriage = model.get_part("drive_carriage")
    ba, da, steel, blackr, cast = M["machined"], M["dark_anodized"], M["steel"], M["black_rubber"], M["cast_iron"]
    carriage.visual(mesh_from_cadquery(_carriage_body_mesh(), "carriage_frame", tolerance=0.0008), origin=Origin(xyz=(0.0, 0.0, 0.0)), material=ba, name="carriage_frame", material_class_id="metal.aluminum_bare")
    _emit_std_swivel_interface(carriage, M, attach="top", caster=False)
    worm_wheel_z = -0.105
    worm_z = worm_wheel_z - 0.032
    housing_z = (worm_wheel_z + worm_z) / 2.0
    side_x = [-0.200, 0.200]
    motor_y_rpy = (-math.pi / 2.0, 0.0, 0.0)
    for i, x_h in enumerate(side_x):
        carriage.visual(mesh_from_cadquery(_worm_housing_mesh(), f"worm_housing_{i}", tolerance=0.0006), origin=Origin(xyz=(x_h, 0.0, housing_z)), material=cast, name=f"worm_gear_housing_{i}", material_class_id="metal.cast_iron_bare")
        carriage.visual(mesh_from_cadquery(_worm_screw_mesh(), f"worm_thread_{i}", tolerance=0.0004), origin=Origin(xyz=(x_h, 0.0, worm_z)), material=steel, name=f"worm_{i}", material_class_id="metal.steel_bare")
        motor_y_center = -0.103
        _add_cyl(carriage, 0.042, 0.092, (x_h, motor_y_center, worm_z), rpy=motor_y_rpy, material=da, name=f"motor_can_{i}")
        _add_cyl(carriage, 0.044, 0.008, (x_h, motor_y_center - 0.048, worm_z), rpy=motor_y_rpy, material=steel, name=f"motor_endcap_{i}")
        for j, dy in enumerate([-0.025, 0.000, 0.025]):
            carriage.visual(Box((0.090, 0.005, 0.005)), origin=Origin(xyz=(x_h, motor_y_center + dy, worm_z - 0.042)), material=blackr, name=f"motor_fin_{i}_{j}", material_class_id="rubber.smooth_plain")
        for j, (dx, dy) in enumerate([(-0.032, -0.032), (0.032, -0.032), (-0.032, 0.032), (0.032, 0.032)]):
            _add_cyl(carriage, 0.005, 0.004, (x_h + dx, dy, housing_z + 0.044), material=da, name=f"housing_screw_{i}_{j}")


def _emit_carriage_hub(model, r, M) -> None:
    carriage = model.get_part("drive_carriage")
    ba, da, steel, copper = M["machined"], M["dark_anodized"], M["steel"], M["copper"]
    carriage.visual(mesh_from_cadquery(_cross_bar_cq(), "cross_bar", tolerance=0.0008), origin=Origin(xyz=(0.0, 0.0, -0.105)), material=ba, name="cross_bar", material_class_id="metal.aluminum_bare")
    _add_cyl(carriage, 0.030, 0.085, (0.0, 0.0, -0.063), material=ba, name="vertical_column")
    # Thin cross-bar body sits low, so the support posts must reach down to it.
    _emit_std_swivel_interface(carriage, M, attach="top", caster=False, post_bottom_z=-0.093)
    motor_rpy = ROT_Z_TO_X
    ws = r.wheel_radius_scale
    for i, x_pos in enumerate([-0.294, 0.294]):
        axle_cx = (x_pos + (-0.210 if i == 0 else 0.210)) / 2.0
        axle_len = abs(x_pos - (-0.210 if i == 0 else 0.210))
        _add_cyl(carriage, 0.015, axle_len, (axle_cx, 0.0, -0.105), rpy=motor_rpy, material=steel, name=f"stub_axle_{i}")
        carriage.visual(mesh_from_cadquery(_stator_drum_cq(ws), f"stator_drum_{i}", tolerance=0.001), origin=Origin(xyz=(x_pos, 0.0, -0.105), rpy=motor_rpy), material=da, name=f"stator_drum_{i}", material_class_id="metal.blackened_gunmetal")
        _add_cyl(carriage, 0.052 * ws, 0.010, (x_pos + (0.022 if i == 0 else -0.022), 0.0, -0.105), rpy=motor_rpy, material=copper, name=f"stator_winding_{i}")
        _add_cyl(carriage, 0.064 * ws, 0.005, (x_pos + (0.028 if i == 0 else -0.028), 0.0, -0.105), rpy=motor_rpy, material=steel, name=f"stator_endcap_{i}")
        _add_cyl(carriage, 0.081 * ws, 0.005, (x_pos + (0.026 if i == 0 else -0.026), 0.0, -0.105), rpy=motor_rpy, material=steel, name=f"hub_bearing_{i}")


# ---- dual-family wheels ----


def _emit_wheel_common_b(wheel_part, i, M, *, radius_scale: float, tread_scale: float) -> None:
    ba, steel, da = M["machined"], M["steel"], M["dark_anodized"]
    motor_rpy = ROT_Z_TO_X
    wheel_part.visual(_make_tire_mesh_b(f"wheel_{i}", radius_scale=radius_scale, tread_scale=tread_scale), material=M["tan_poly"], name="treaded_tire", material_class_id="rubber.directional_grooved")
    _add_cyl(wheel_part, 0.100 * radius_scale, 0.073, (0.0, 0.0, 0.0), rpy=motor_rpy, material=ba, name="rim_shell")
    _add_cyl(wheel_part, 0.041, 0.083, (0.0, 0.0, 0.0), rpy=motor_rpy, material=steel, name="hub_drum")
    cap_x = -0.0395 if i == 0 else 0.0395
    _add_cyl(wheel_part, 0.036, 0.006, (cap_x, 0.0, 0.0), rpy=motor_rpy, material=steel, name="outer_hub_cap")
    screw_x = -0.044 if i == 0 else 0.044
    for j in range(10):
        a = 2.0 * math.pi * j / 10.0
        _add_cyl(wheel_part, 0.0032, 0.003, (screw_x, 0.026 * math.cos(a), 0.026 * math.sin(a)), rpy=motor_rpy, material=da, name=f"hub_screw_{j}")


def _emit_wheels_gearbox(model, M, *, radius_scale: float, tread_scale: float) -> list:
    wheels = []
    for i in range(2):
        w = model.part(f"wheel_{i}")
        _emit_wheel_common_b(w, i, M, radius_scale=radius_scale, tread_scale=tread_scale)
        wheels.append(w)
    return wheels


def _emit_wheels_belt(model, M, *, radius_scale: float, tread_scale: float) -> list:
    da, steel = M["dark_anodized"], M["steel"]
    motor_rpy = ROT_Z_TO_X
    wheels = []
    for i in range(2):
        w = model.part(f"wheel_{i}")
        _emit_wheel_common_b(w, i, M, radius_scale=radius_scale, tread_scale=tread_scale)
        pulley_x = 0.058 if i == 0 else -0.058
        shaft_half = (abs(pulley_x) - 0.0415) / 2.0
        shaft_center = 0.0415 + shaft_half if i == 0 else -(0.0415 + shaft_half)
        _add_cyl(w, 0.020, abs(pulley_x) - 0.0415, (shaft_center, 0.0, 0.0), rpy=motor_rpy, material=steel, name="pulley_shaft")
        w.visual(mesh_from_cadquery(_toothed_pulley_mesh(0.048, 0.014, n_teeth=28), f"wheel_{i}_pulley_mesh", tolerance=0.0005), origin=Origin(xyz=(pulley_x, 0.0, 0.0), rpy=motor_rpy), material=da, name="wheel_pulley", material_class_id="metal.blackened_gunmetal")
        wheels.append(w)
    return wheels


def _emit_wheels_worm(model, M, *, radius_scale: float, tread_scale: float) -> list:
    ba, steel, da = M["machined"], M["steel"], M["dark_anodized"]
    motor_rpy = ROT_Z_TO_X
    wheels = []
    for i in range(2):
        w = model.part(f"wheel_{i}")
        w.visual(_make_tire_mesh_b(f"wheel_{i}", radius_scale=radius_scale, tread_scale=tread_scale), material=M["tan_poly"], name="treaded_tire", material_class_id="rubber.directional_grooved")
        _add_cyl(w, 0.041, 0.168, (0.0, 0.0, 0.0), rpy=motor_rpy, material=steel, name="hub_drum")
        _add_cyl(w, 0.100 * radius_scale, 0.073, (0.0, 0.0, 0.0), rpy=motor_rpy, material=ba, name="rim_shell")
        cap_x = -0.056 if i == 0 else 0.056
        _add_cyl(w, 0.036, 0.006, (cap_x, 0.0, 0.0), rpy=motor_rpy, material=steel, name="outer_hub_cap")
        screw_x = -0.060 if i == 0 else 0.060
        for j in range(10):
            a = 2.0 * math.pi * j / 10.0
            _add_cyl(w, 0.0032, 0.003, (screw_x, 0.026 * math.cos(a), 0.026 * math.sin(a)), rpy=motor_rpy, material=da, name=f"hub_screw_{j}")
        ww_offset_x = 0.084 if i == 0 else -0.084
        w.visual(mesh_from_cadquery(_worm_wheel_disc_mesh(), f"worm_wheel_disc_{i}", tolerance=0.0004), origin=Origin(xyz=(ww_offset_x, 0.0, 0.0)), material=steel, name="worm_wheel", material_class_id="metal.steel_bare")
        wheels.append(w)
    return wheels


def _emit_wheels_hub(model, M, *, radius_scale: float, tread_scale: float) -> list:
    ba, da, steel = M["machined"], M["dark_anodized"], M["steel"]
    motor_rpy = ROT_Z_TO_X
    wheels = []
    for i in range(2):
        w = model.part(f"wheel_{i}")
        w.visual(_make_tire_mesh_b(f"wheel_{i}", radius_scale=radius_scale, tread_scale=tread_scale), material=M["tan_poly"], name="treaded_tire", material_class_id="rubber.directional_grooved")
        w.visual(mesh_from_cadquery(_rim_shell_cq(radius_scale), f"rim_shell_{i}", tolerance=0.0008), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=motor_rpy), material=ba, name="rim_shell", material_class_id="metal.aluminum_bare")
        cap_x = -0.038 if i == 0 else 0.038
        _add_cyl(w, 0.098 * radius_scale, 0.006, (cap_x, 0.0, 0.0), rpy=motor_rpy, material=da, name="end_cover")
        logo_x = cap_x + (-0.004 if i == 0 else 0.004)
        _add_cyl(w, 0.032, 0.003, (logo_x, 0.0, 0.0), rpy=motor_rpy, material=steel, name="hub_logo_disc")
        for j in range(8):
            a = 2.0 * math.pi * j / 8.0
            _add_cyl(w, 0.004, 0.004, (logo_x, 0.082 * radius_scale * math.cos(a), 0.082 * radius_scale * math.sin(a)), rpy=motor_rpy, material=steel, name=f"rotor_bolt_{j}")
        wheels.append(w)
    return wheels


def _emit_rocker_arms(model, M) -> list:
    steel, zinc = M["steel"], M["zinc_yellow"]
    spring_mesh = _make_spring_mesh()
    rockers = []
    for i in range(2):
        sign = -1.0 if i == 0 else 1.0
        rocker = model.part(f"rocker_arm_{i}")
        rocker.visual(mesh_from_cadquery(_make_rocker_arm_mesh(i), f"rocker_arm_body_{i}", tolerance=0.0008), material=steel, name="arm_body", material_class_id="metal.steel_bare")
        seat_x = _SPRING_SEAT_T * sign * _ARM_DX
        seat_z = _SPRING_SEAT_T * _ARM_DZ
        spring_mid_z = seat_z + 0.029
        rocker.visual(spring_mesh, origin=Origin(xyz=(seat_x, 0.0, spring_mid_z)), material=zinc, name="spring_coil", material_class_id="metal.steel_galvanized")
        # Damper rod runs from the arm seat up through the coil (self-contained
        # coil-over on the arm), so it fuses to both the arm and the spring.
        shaft_bottom = seat_z
        shaft_top = spring_mid_z + 0.045
        shaft_len = shaft_top - shaft_bottom
        _add_cyl(rocker, 0.007, shaft_len, (seat_x, 0.0, 0.5 * (shaft_bottom + shaft_top)), material=steel, name="shock_shaft")
        rockers.append(rocker)
    return rockers


def _build_dual_family(model, r, M) -> None:
    model.part("mount_plate")
    rigid_mount = r.steering == "rigid"
    if r.chassis_mount == "side_flange_bracket":
        _build_side_flange(model, M, rigid=rigid_mount)
    else:
        _build_top_mount_plate(model, M, slew=(r.steering == "continuous_caster"), rigid=rigid_mount)

    model.part("drive_carriage")
    rs, ts = r.wheel_radius_scale, r.tire_tread_scale
    if r.drive_mechanism == "belt_reduction":
        _emit_carriage_belt(model, r, M)
        wheels = _emit_wheels_belt(model, M, radius_scale=rs, tread_scale=ts)
    elif r.drive_mechanism == "worm_reduction":
        _emit_carriage_worm(model, r, M)
        wheels = _emit_wheels_worm(model, M, radius_scale=rs, tread_scale=ts)
    elif r.drive_mechanism == "hub_direct_drive":
        _emit_carriage_hub(model, r, M)
        wheels = _emit_wheels_hub(model, M, radius_scale=rs, tread_scale=ts)
    else:  # dual_motor_gearbox
        _emit_carriage_gearbox(model, r, M)
        wheels = _emit_wheels_gearbox(model, M, radius_scale=rs, tread_scale=ts)

    # Steering joint: mount_plate -> drive_carriage.
    mount_plate = model.get_part("mount_plate")
    carriage = model.get_part("drive_carriage")
    steer_z = _STEER_Z[r.chassis_mount]
    if r.steering == "rigid":
        model.articulation("mount_to_carriage", ArticulationType.FIXED, parent=mount_plate, child=carriage, origin=Origin(xyz=(0.0, 0.0, steer_z)))
    elif r.steering == "continuous_caster":
        model.articulation("mount_to_carriage", ArticulationType.CONTINUOUS, parent=mount_plate, child=carriage, origin=Origin(xyz=(0.0, 0.0, steer_z)), axis=(0.0, 0.0, 1.0), motion_limits=MotionLimits(effort=35.0, velocity=1.8), motion_properties=MotionProperties(damping=0.3, friction=0.1))
    else:  # limited_swivel
        lim = r.swivel_limit
        model.articulation("mount_to_carriage", ArticulationType.REVOLUTE, parent=mount_plate, child=carriage, origin=Origin(xyz=(0.0, 0.0, steer_z)), axis=(0.0, 0.0, 1.0), motion_limits=MotionLimits(effort=35.0, velocity=1.2, lower=-lim, upper=lim), motion_properties=MotionProperties(damping=0.3, friction=0.1))

    spin = MotionLimits(effort=12.0, velocity=18.0)
    spin_props = MotionProperties(damping=0.02, friction=0.01)
    if r.wheel_travel == "sprung_rocker":
        rockers = _emit_rocker_arms(model, M)
        for i in range(2):
            sign = -1.0 if i == 0 else 1.0
            pivot_axis = (0.0, 1.0, 0.0) if i == 0 else (0.0, -1.0, 0.0)
            model.articulation(f"rocker_pivot_{i}", ArticulationType.REVOLUTE, parent=carriage, child=rockers[i], origin=Origin(xyz=(sign * _PIVOT_X_OFFSET, 0.0, _PIVOT_Z)), axis=pivot_axis, motion_limits=MotionLimits(effort=25.0, velocity=4.0, lower=-0.12, upper=0.18), motion_properties=MotionProperties(damping=1.2, friction=0.15))
        for i in range(2):
            sign = -1.0 if i == 0 else 1.0
            model.articulation(f"carriage_to_wheel_{i}", ArticulationType.CONTINUOUS, parent=rockers[i], child=wheels[i], origin=Origin(xyz=(sign * _ARM_DX, 0.0, _ARM_DZ)), axis=(1.0, 0.0, 0.0), motion_limits=spin, motion_properties=spin_props)
    else:
        positions = [(-0.294, 0.0, -0.105), (0.294, 0.0, -0.105)]
        for i in range(2):
            model.articulation(f"carriage_to_wheel_{i}", ArticulationType.CONTINUOUS, parent=carriage, child=wheels[i], origin=Origin(xyz=positions[i]), axis=(1.0, 0.0, 0.0), motion_limits=spin, motion_properties=spin_props)


# ===========================================================================
# Top-level build
# ===========================================================================


def build_differential_drive_wheel(
    config: DifferentialDriveWheelConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="differential_drive_wheel", assets=assets)
    M = _register_materials(model, r.palette_theme)

    if r.family == "bevel":
        _build_bevel_family(model, r, M)
    else:
        _build_dual_family(model, r, M)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_differential_drive_wheel(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_differential_drive_wheel(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================


def _has_visual(part, name: str) -> bool:
    return any(getattr(v, "name", None) == name for v in part.visuals)


def _free_root_joint(joints: dict, name: str):
    """Follow the mimic chain from ``name`` to the free (non-mimic) driver joint.

    Mimic-driven joints cannot be posed directly, so any motion test must drive
    the free root that ultimately spins the target part (mimics propagate).
    """
    j = joints.get(name)
    seen: set[str] = set()
    while j is not None and getattr(j, "mimic", None) is not None:
        nxt = j.mimic.joint
        if nxt in seen:
            break
        seen.add(nxt)
        j = joints.get(nxt)
    return j


def _allow(ctx, model, a, b, *, reason, elem_a=None, elem_b=None) -> None:
    names = {p.name for p in model.parts}
    if a not in names or b not in names:
        return
    pa, pb = model.get_part(a), model.get_part(b)
    if elem_a is not None and not _has_visual(pa, elem_a):
        return
    if elem_b is not None and not _has_visual(pb, elem_b):
        return
    ctx.allow_overlap(pa, pb, reason=reason, elem_a=elem_a, elem_b=elem_b)


def _declare_bevel_overlaps(ctx, model, r) -> None:
    spider = r.planet_pinions > 0
    # Motor / input shaft.
    for elem_a in ("motor_can", "motor_front_cap", "motor_saddle", "motor_cooling_fin_1"):
        _allow(ctx, model, "carrier", "input_pinion", elem_a=elem_a, elem_b="input_shaft",
               reason="The rotating input shaft is seated into / passes through the motor housing.")
    # Open-carrier axle journal bearings / sleeves ride directly on the half shafts.
    _allow(ctx, model, "carrier", "left_wheel", elem_a="bearing_cap_0", elem_b="green_half_shaft",
           reason="Left axle journal bearing rides on the green half shaft.")
    _allow(ctx, model, "carrier", "right_wheel", elem_a="bearing_cap_1", elem_b="red_half_shaft",
           reason="Right axle journal bearing rides on the red half shaft.")
    for wheel, shaft, s in (("left_wheel", "green_half_shaft", 0), ("right_wheel", "red_half_shaft", 1)):
        _allow(ctx, model, "carrier", wheel, elem_a=f"axle_sleeve_{s}", elem_b=shaft,
               reason="Half shaft runs inside the carrier axle journal sleeve.")
        _allow(ctx, model, "carrier", wheel, elem_a=f"axle_sleeve_{s}", elem_b="shaft_collar",
               reason="Shaft collar seats against the carrier axle journal sleeve.")
    if r.chassis_mount == "enclosed_diff_housing":
        gears = ["orange_gear", "brass_side_gear", "left_side_gear", "right_side_gear", "input_pinion"]
        gears += [f"planet_pinion_{i}" for i in range(r.planet_pinions)]
        for gear in gears:
            _allow(ctx, model, "carrier", gear, reason="Gear rotates inside the sealed cast differential housing.")
        for wheel in ("left_wheel", "right_wheel"):
            _allow(ctx, model, "carrier", wheel, reason="Half shaft and collar pass through the axle tube assembly.")
    if not spider:
        _allow(ctx, model, "brass_side_gear", "left_wheel", elem_a="brass_hub", elem_b="green_half_shaft", reason="Brass side gear hub is a splined sliding fit on the green half shaft.")
        _allow(ctx, model, "orange_gear", "right_wheel", elem_a="orange_hub", elem_b="red_half_shaft", reason="Orange ring gear hub is a captured fit around the red half shaft.")
        _allow(ctx, model, "brass_side_gear", "right_wheel", elem_a="brass_hub", elem_b="red_half_shaft", reason="Red half shaft extends into the side gear hub so the axle reads continuous.")
    else:
        _allow(ctx, model, "left_wheel", "orange_gear", elem_a="green_half_shaft", elem_b="orange_hub", reason="Green half shaft passes through the orange gear bore.")
        _allow(ctx, model, "left_wheel", "orange_gear", elem_a="green_half_shaft", elem_b="spider_hub", reason="Green half shaft passes through the spider cross central hub bore.")
        _allow(ctx, model, "left_wheel", "right_wheel", elem_a="green_half_shaft", elem_b="red_half_shaft", reason="The two coaxial half shafts meet at the differential center.")
        _allow(ctx, model, "orange_gear", "right_wheel", elem_a="spider_hub", elem_b="red_half_shaft", reason="Red half shaft passes through the spider cross central bore.")
        _allow(ctx, model, "orange_gear", "right_wheel", elem_a="orange_hub", elem_b="red_half_shaft", reason="Orange ring gear hub is captured on the red half shaft.")
        for i in range(r.planet_pinions):
            _allow(ctx, model, "orange_gear", "right_wheel", elem_a=f"spider_arm_{i}", elem_b="red_half_shaft", reason="Spider cross arm crosses the coaxial axle path.")
        _allow(ctx, model, "left_side_gear", "left_wheel", elem_a="left_side_gear_hub", elem_b="green_half_shaft", reason="Left side gear hub is a splined sliding fit on the green half shaft.")
        _allow(ctx, model, "right_side_gear", "right_wheel", elem_a="right_side_gear_hub", elem_b="red_half_shaft", reason="Right side gear hub is a splined sliding fit on the red half shaft.")
        _allow(ctx, model, "left_side_gear", "right_wheel", elem_a="left_side_gear_hub", elem_b="red_half_shaft", reason="Red half shaft passes through the left side gear bore.")
        _allow(ctx, model, "orange_gear", "left_side_gear", reason="Left side gear sits inside the orange ring gear envelope.")
        _allow(ctx, model, "orange_gear", "right_side_gear", reason="Right side gear sits inside the orange ring gear envelope.")
        for i in range(r.planet_pinions):
            pn = f"planet_pinion_{i}"
            _allow(ctx, model, "orange_gear", pn, reason="Planet pinion sits inside the orange ring gear envelope.")
            _allow(ctx, model, "left_side_gear", pn, reason="Planet pinion teeth intermesh with the left side gear.")
            _allow(ctx, model, "right_side_gear", pn, reason="Planet pinion teeth intermesh with the right side gear.")


def _declare_dual_overlaps(ctx, model, r) -> None:
    # The carriage is welded onto the plate's central king-pin boss (only present
    # for the rigid mount); the post and the worm carriage frame envelope it.
    _allow(ctx, model, "drive_carriage", "mount_plate", elem_a="swivel_post", elem_b="king_pin_boss",
           reason="Carriage swivel post is captured on the plate king-pin boss.")
    _allow(ctx, model, "drive_carriage", "mount_plate", elem_a="carriage_frame", elem_b="king_pin_boss",
           reason="Rigid king-pin boss is welded into the carriage top-plate frame.")
    caster = r.steering == "continuous_caster"
    if caster:
        _allow(ctx, model, "drive_carriage", "mount_plate", elem_a="inner_bearing_flange", elem_b="outer_bearing_ring", reason="Slew-ring flange rides against the plate slew bearing (rotational interface).")
        _allow(ctx, model, "drive_carriage", "mount_plate", elem_a="swivel_post", elem_b="outer_bearing_ring", reason="Enlarged swivel post is captured in the slew-ring inner bore.")
    if r.chassis_mount == "side_flange_bracket":
        _allow(ctx, model, "drive_carriage", "mount_plate", elem_a="swivel_post", elem_b="seat_bearing_ring", reason="Carriage swivel post is captured inside the seat bearing ring as a steering bearing.")
    if r.drive_mechanism == "belt_reduction":
        for side in (0, 1):
            _allow(ctx, model, "drive_carriage", f"wheel_{side}", elem_a=f"belt_loop_{side}", elem_b="wheel_pulley", reason="Belt loop wraps around the wheel pulley.")
            _allow(ctx, model, "drive_carriage", "drive_carriage", elem_a=f"belt_loop_{side}", elem_b=f"motor_pulley_{side}", reason="Belt loop wraps around the motor pulley.")
    if r.drive_mechanism == "worm_reduction":
        for side in (0, 1):
            _allow(ctx, model, "drive_carriage", f"wheel_{side}", elem_a=f"worm_gear_housing_{side}", elem_b="worm_wheel", reason="Worm wheel disc meshes with the worm inside the housing.")
            _allow(ctx, model, "drive_carriage", f"wheel_{side}", elem_a=f"worm_gear_housing_{side}", elem_b="hub_drum", reason="Hub drum axle passes through the worm-gear housing.")
            _allow(ctx, model, "drive_carriage", f"wheel_{side}", elem_a=f"worm_{side}", elem_b="hub_drum", reason="Worm wraps the axle where it meshes the worm wheel.")
            _allow(ctx, model, "drive_carriage", f"wheel_{side}", elem_a="carriage_frame", elem_b="hub_drum", reason="Hub drum passes through the carriage frame side webs.")
            _allow(ctx, model, "drive_carriage", f"wheel_{side}", elem_a="carriage_frame", elem_b="worm_wheel", reason="Worm wheel disc extends into the carriage frame gear area.")
    if r.drive_mechanism == "hub_direct_drive":
        for side in (0, 1):
            _allow(ctx, model, "drive_carriage", f"wheel_{side}", elem_a=f"hub_bearing_{side}", elem_b="rim_shell", reason="Hub motor bearing seal seated inside the rotor bore.")
    if r.wheel_travel == "sprung_rocker":
        for i in range(2):
            gb = f"side_gearbox_{i}"
            rocker = f"rocker_arm_{i}"
            wheel = f"wheel_{i}"
            _allow(ctx, model, "drive_carriage", rocker, elem_a=gb, elem_b="arm_body", reason="Rocker arm pivot boss is bolted to the gearbox side face.")
            _allow(ctx, model, rocker, wheel, elem_a="arm_body", elem_b="treaded_tire", reason="Rocker arm axle housing sits inside the wheel tire bore.")
            _allow(ctx, model, rocker, wheel, elem_a="arm_body", elem_b="rim_shell", reason="Rocker arm axle housing nests inside the wheel rim bore.")
            _allow(ctx, model, rocker, wheel, elem_a="arm_body", elem_b="hub_drum", reason="Rocker arm bearing housing nests inside the wheel hub drum.")
            # The coil-over (spring + damper rod) is a self-contained pack on the
            # rocker; its outer edge may skim the wheel bore as the arm travels.
            for elem_a in ("spring_coil", "shock_shaft"):
                for elem_b in ("hub_drum", "rim_shell", "treaded_tire"):
                    _allow(ctx, model, rocker, wheel, elem_a=elem_a, elem_b=elem_b, reason="Suspension element extends past the wheel edge due to suspension geometry.")


def run_differential_drive_wheel_tests(
    object_model: ArticulatedObject, config: DifferentialDriveWheelConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    if r.family == "bevel":
        _declare_bevel_overlaps(ctx, object_model, r)
    else:
        _declare_dual_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    parts = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}

    # --- Category identity: two coaxial CONTINUOUS wheels about X ---
    if r.family == "bevel":
        wheel_names = ("left_wheel", "right_wheel")
        spin_names = ("left_wheel_spin", "right_wheel_spin")
    else:
        wheel_names = ("wheel_0", "wheel_1")
        spin_names = ("carriage_to_wheel_0", "carriage_to_wheel_1")
    ctx.check("two_wheels_present", all(w in parts for w in wheel_names), details=f"parts={sorted(parts)}")
    spins = [joints.get(n) for n in spin_names]
    ctx.check(
        "two_continuous_wheel_spins",
        all(j is not None and j.articulation_type == ArticulationType.CONTINUOUS for j in spins),
        details=f"spins={[getattr(j,'articulation_type',None) for j in spins]}",
    )
    ctx.check(
        "wheel_spin_axes_collinear_x",
        all(j is not None and j.axis == (1.0, 0.0, 0.0) for j in spins),
        details=f"axes={[getattr(j,'axis',None) for j in spins]}",
    )

    # --- Wheel spin keeps axle centers fixed (targeted pose) ---
    # In the bevel family the wheel spins are mimic-driven (they cannot be posed
    # directly), so drive each wheel through its free root joint; mimics
    # propagate. In the dual family the wheel spins are themselves the free
    # roots, so this drives them directly.
    if all(j is not None for j in spins):
        centers_ok = True
        detail_bits = []
        for wn, sp in zip(wheel_names, spins):
            root = _free_root_joint(joints, sp.name)
            part = object_model.get_part(wn)
            rest = ctx.part_world_position(part)
            if root is None or rest is None:
                centers_ok = False
                continue
            with ctx.pose({root: 1.2}):
                spun = ctx.part_world_position(part)
            if spun is None or max(abs(rest[i] - spun[i]) for i in range(3)) >= 1e-6:
                centers_ok = False
            detail_bits.append(f"{wn}:rest={rest} spun={spun} via {root.name}")
        ctx.check("wheel_spin_keeps_axle_centers_fixed", centers_ok, details="; ".join(detail_bits))

    if r.family == "bevel":
        # --- Gear train identity ---
        og = joints.get("orange_gear_spin")
        ip = joints.get("input_pinion_spin")
        ctx.check("input_pinion_is_driver", ip is not None and ip.articulation_type == ArticulationType.CONTINUOUS and ip.mimic is None, details=f"input={ip}")
        ctx.check(
            "input_pinion_drives_orange_opposite",
            og is not None and og.mimic is not None and og.mimic.joint == "input_pinion_spin" and og.mimic.multiplier < 0.0,
            details=f"orange mimic={getattr(og,'mimic',None)}",
        )
        if r.planet_pinions > 0:
            ctx.check("side_gears_present", {"left_side_gear", "right_side_gear"} <= parts)
            ctx.check("planet_pinions_present", all(f"planet_pinion_{i}" in parts for i in range(r.planet_pinions)), details=f"n={r.planet_pinions}")
            # Drive the whole mimic train from the pinion. The ring gear and the
            # two side gears spin about the axle line, so their centers stay put.
            # The planet pinions are carried by the rotating cage, so their
            # centers orbit — check that instead.
            drive = joints.get("input_pinion_spin")
            if drive is not None:
                fixed_ok = True
                for pn in ["orange_gear", "left_side_gear", "right_side_gear"]:
                    part = object_model.get_part(pn)
                    rest = ctx.part_world_position(part)
                    with ctx.pose({drive: 1.37}):
                        spun = ctx.part_world_position(part)
                    if rest is None or spun is None or max(abs(rest[i] - spun[i]) for i in range(3)) >= 1e-6:
                        fixed_ok = False
                ctx.check("spider_train_axle_gears_centers_fixed", fixed_ok)
                orbit_ok = True
                for i in range(r.planet_pinions):
                    part = object_model.get_part(f"planet_pinion_{i}")
                    rest = ctx.part_world_position(part)
                    with ctx.pose({drive: 1.37}):
                        spun = ctx.part_world_position(part)
                    if rest is None or spun is None or max(abs(rest[k] - spun[k]) for k in range(3)) <= 1e-5:
                        orbit_ok = False
                ctx.check("spider_planets_orbit_with_cage", orbit_ok)
        else:
            ctx.check("brass_side_gear_present", "brass_side_gear" in parts)
        # Every rotating joint is continuous.
        rot = [j for n, j in joints.items() if n.endswith("_spin")]
        ctx.check("all_spin_joints_continuous", all(j.articulation_type == ArticulationType.CONTINUOUS for j in rot), details=f"n={len(rot)}")
    else:
        # --- Chassis mount + steering identity ---
        ctx.check("mount_plate_present", "mount_plate" in parts)
        ctx.check("drive_carriage_present", "drive_carriage" in parts)
        swivel = joints.get("mount_to_carriage")
        ctx.check("steering_joint_present", swivel is not None)
        if swivel is not None:
            if r.steering == "rigid":
                ctx.check("rigid_steering_is_fixed", swivel.articulation_type == ArticulationType.FIXED, details=f"{swivel.articulation_type}")
            elif r.steering == "limited_swivel":
                ml = swivel.motion_limits
                ctx.check("limited_swivel_is_bounded_revolute", swivel.articulation_type == ArticulationType.REVOLUTE and ml is not None and ml.lower is not None and ml.upper is not None and ml.lower < 0.0 < ml.upper, details=f"limits={ml}")
                # Steering rotates the carriage.
                rest = ctx.part_world_position(object_model.get_part(wheel_names[0]))
                with ctx.pose({swivel: r.swivel_limit}):
                    turned = ctx.part_world_position(object_model.get_part(wheel_names[0]))
                ctx.check("limited_swivel_moves_wheel", rest is not None and turned is not None and max(abs(rest[i] - turned[i]) for i in range(2)) > 1e-4, details=f"rest={rest} turned={turned}")
            else:  # continuous_caster
                ml = swivel.motion_limits
                ctx.check("caster_is_continuous", swivel.articulation_type == ArticulationType.CONTINUOUS, details=f"{swivel.articulation_type}")
                ctx.check("caster_has_no_hard_limits", ml is None or (ml.lower is None and ml.upper is None), details=f"limits={ml}")
                rest = ctx.part_world_position(object_model.get_part("drive_carriage"))
                with ctx.pose({swivel: 2.0 * math.pi}):
                    turned = ctx.part_world_position(object_model.get_part("drive_carriage"))
                ctx.check("caster_full_turn_returns_to_rest", rest is not None and turned is not None and max(abs(rest[i] - turned[i]) for i in range(3)) < 1e-4, details=f"rest={rest} turned={turned}")
        # Wheels align to the axle line (YZ overlap) and clear the carriage in X.
        for wn in wheel_names:
            ctx.expect_overlap(object_model.get_part(wn), object_model.get_part("drive_carriage"), axes="yz", min_overlap=0.060, name=f"{wn} aligns to axle supports")
        if r.wheel_travel == "sprung_rocker":
            for i in range(2):
                rp = joints.get(f"rocker_pivot_{i}")
                ctx.check(f"rocker_pivot_{i}_bounded_revolute", rp is not None and rp.articulation_type == ArticulationType.REVOLUTE and rp.motion_limits is not None and rp.motion_limits.lower < 0.0 < rp.motion_limits.upper, details=f"{rp}")
            # Positive rocker pose lifts the wheels.
            rp0, rp1 = joints.get("rocker_pivot_0"), joints.get("rocker_pivot_1")
            if rp0 is not None and rp1 is not None:
                w0 = object_model.get_part("wheel_0")
                rest_z = ctx.part_world_position(w0)[2]
                with ctx.pose({rp0: 0.12, rp1: 0.12}):
                    lift = ctx.part_world_position(w0)
                ctx.check("rocker_positive_pose_lifts_wheel", lift is not None and lift[2] > rest_z + 0.002, details=f"rest_z={rest_z} lift={lift}")

    return ctx.report()


__all__ = [
    "ChassisMount",
    "DifferentialDriveWheelConfig",
    "DriveMechanism",
    "PaletteTheme",
    "ResolvedDifferentialDriveWheelConfig",
    "Steering",
    "WheelTravel",
    "__modular__",
    "build_differential_drive_wheel",
    "build_seeded_differential_drive_wheel",
    "config_from_seed",
    "resolve_config",
    "run_differential_drive_wheel_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
