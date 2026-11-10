# SPDX-License-Identifier: Apache-2.0

"""Sci-fi satellite dish procedural template.

Reauthored from the source records instead of patching the previous template:

* non-flat dish forms are always a continuous circular parabolic reflector;
* segmented / petal / hex variants are thin surface panels attached to that
  reflector, not boxy blocks behind it;
* flat phased array is the only rectangular aperture and forces feed=none;
* azimuth and elevation REVOLUTE joints are preserved for every variant.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
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
    Part,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True


DishForm = Literal[
    "segmented_parabolic",
    "hex_faceted",
    "petal_segmented",
    "flat_phased_array",
]
MountGimbal = Literal["single_rear_yoke", "dual_arm_fork", "tilt_tripod"]
Feed = Literal["center_fed_horn", "cassegrain_sub", "offset_feed_arm", "none"]
PaletteStyle = Literal["dark_teal", "military_green", "desert_tan", "deep_navy"]

DISH_FORMS: tuple[DishForm, ...] = (
    "segmented_parabolic",
    "hex_faceted",
    "petal_segmented",
    "flat_phased_array",
)
MOUNT_GIMBALS: tuple[MountGimbal, ...] = (
    "single_rear_yoke",
    "dual_arm_fork",
    "tilt_tripod",
)
REAL_FEEDS: tuple[Feed, ...] = ("center_fed_horn", "cassegrain_sub", "offset_feed_arm")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("dark_teal", "military_green", "desert_tan", "deep_navy")

SEGMENT_COUNTS = (8, 16, 24)
PETAL_COUNTS = (8, 12, 16)
HEX_RING_COUNTS = (3, 4, 5)
GRID_COLS = (6, 8)
GRID_ROWS = (4, 5, 6)

_BOX_W = 0.50
_BOX_D = 0.40
_BOX_H = 0.32
_REST_TILT = -0.58

_PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "dark_teal": {
        "box": (0.08, 0.09, 0.10, 1.0),
        "box_dark": (0.035, 0.040, 0.046, 1.0),
        "mount": (0.24, 0.26, 0.28, 1.0),
        "reflector": (0.24, 0.28, 0.31, 1.0),
        "reflector_inner": (0.15, 0.17, 0.19, 1.0),
        "rim": (0.62, 0.88, 0.18, 1.0),
        "feed": (0.70, 0.74, 0.76, 1.0),
        "glow": (0.05, 0.86, 0.78, 1.0),
        "accent": (0.92, 0.56, 0.10, 1.0),
        "hot": (0.94, 0.22, 0.16, 1.0),
    },
    "military_green": {
        "box": (0.20, 0.24, 0.17, 1.0),
        "box_dark": (0.10, 0.13, 0.09, 1.0),
        "mount": (0.27, 0.30, 0.22, 1.0),
        "reflector": (0.35, 0.39, 0.30, 1.0),
        "reflector_inner": (0.23, 0.26, 0.20, 1.0),
        "rim": (0.18, 0.22, 0.15, 1.0),
        "feed": (0.64, 0.66, 0.58, 1.0),
        "glow": (0.34, 0.82, 0.30, 1.0),
        "accent": (0.82, 0.56, 0.14, 1.0),
        "hot": (0.86, 0.24, 0.16, 1.0),
    },
    "desert_tan": {
        "box": (0.58, 0.50, 0.36, 1.0),
        "box_dark": (0.32, 0.26, 0.18, 1.0),
        "mount": (0.50, 0.45, 0.33, 1.0),
        "reflector": (0.72, 0.66, 0.50, 1.0),
        "reflector_inner": (0.46, 0.38, 0.26, 1.0),
        "rim": (0.42, 0.36, 0.24, 1.0),
        "feed": (0.28, 0.26, 0.22, 1.0),
        "glow": (0.20, 0.76, 0.72, 1.0),
        "accent": (0.86, 0.52, 0.16, 1.0),
        "hot": (0.84, 0.22, 0.15, 1.0),
    },
    "deep_navy": {
        "box": (0.06, 0.08, 0.15, 1.0),
        "box_dark": (0.03, 0.04, 0.08, 1.0),
        "mount": (0.12, 0.16, 0.25, 1.0),
        "reflector": (0.16, 0.20, 0.30, 1.0),
        "reflector_inner": (0.10, 0.13, 0.20, 1.0),
        "rim": (0.28, 0.62, 0.94, 1.0),
        "feed": (0.66, 0.70, 0.78, 1.0),
        "glow": (0.18, 0.82, 0.90, 1.0),
        "accent": (0.94, 0.62, 0.16, 1.0),
        "hot": (0.90, 0.26, 0.30, 1.0),
    },
}


@dataclass(frozen=True)
class SatelliteDishConfig:
    dish_form: DishForm = "segmented_parabolic"
    mount_gimbal: MountGimbal = "single_rear_yoke"
    feed: Feed = "center_fed_horn"
    panel_count: int = 16
    dish_radius: float = 0.30
    focal: float = 0.165
    mount_lift: float = 0.34
    palette_style: PaletteStyle = "dark_teal"
    name: str = "reference_satellite_dish"


@dataclass(frozen=True)
class ResolvedSatelliteDishConfig:
    dish_form: DishForm
    mount_gimbal: MountGimbal
    feed: Feed
    panel_count: int
    dish_radius: float
    focal: float
    rim_depth: float
    mount_lift: float
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    name: str


@dataclass(frozen=True)
class GimbalAnchors:
    yoke: Part
    hinge_z: float
    knuckle_x: float


def _require(value: str, allowed: tuple[str, ...], *, field_name: str) -> str:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {allowed}, got {value!r}")
    return value


def _resolve_feed(dish_form: DishForm, feed: Feed) -> Feed:
    if dish_form == "flat_phased_array":
        return "none"
    return "center_fed_horn" if feed == "none" else feed


def _panel_count_for(dish_form: DishForm, rng: random.Random) -> int:
    if dish_form == "segmented_parabolic":
        return rng.choice(SEGMENT_COUNTS)
    if dish_form == "petal_segmented":
        return rng.choice(PETAL_COUNTS)
    if dish_form == "hex_faceted":
        rings = rng.choice(HEX_RING_COUNTS)
        return 1 + sum(6 * i for i in range(1, rings + 1))
    return rng.choice(GRID_COLS) * rng.choice(GRID_ROWS)


def config_from_seed(seed: int) -> SatelliteDishConfig:
    rng = random.Random(seed)
    dish_form = rng.choice(DISH_FORMS)
    feed = _resolve_feed(dish_form, rng.choice(REAL_FEEDS))
    return SatelliteDishConfig(
        dish_form=dish_form,
        mount_gimbal=rng.choice(MOUNT_GIMBALS),
        feed=feed,
        panel_count=_panel_count_for(dish_form, rng),
        dish_radius=rng.uniform(0.27, 0.34),
        focal=rng.uniform(0.145, 0.190),
        mount_lift=rng.uniform(0.30, 0.38),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"seeded_satellite_dish_{seed}",
    )


def resolve_config(config: SatelliteDishConfig) -> ResolvedSatelliteDishConfig:
    dish_form = _require(config.dish_form, DISH_FORMS, field_name="dish_form")
    mount_gimbal = _require(config.mount_gimbal, MOUNT_GIMBALS, field_name="mount_gimbal")
    palette_style = _require(config.palette_style, PALETTE_STYLES, field_name="palette_style")
    feed = _resolve_feed(dish_form, config.feed)
    if feed not in ("center_fed_horn", "cassegrain_sub", "offset_feed_arm", "none"):
        raise ValueError(f"feed must be a known feed, got {feed!r}")

    radius = max(0.22, min(0.42, float(config.dish_radius)))
    focal = max(radius * 0.42, min(radius * 0.72, float(config.focal)))
    if dish_form == "segmented_parabolic":
        panel_count = min(24, max(8, int(config.panel_count)))
    elif dish_form == "petal_segmented":
        panel_count = min(18, max(8, int(config.panel_count)))
    elif dish_form == "hex_faceted":
        panel_count = max(19, min(91, int(config.panel_count)))
    else:
        panel_count = max(16, min(48, int(config.panel_count)))

    return ResolvedSatelliteDishConfig(
        dish_form=dish_form,  # type: ignore[arg-type]
        mount_gimbal=mount_gimbal,  # type: ignore[arg-type]
        feed=feed,
        panel_count=panel_count,
        dish_radius=radius,
        focal=focal,
        rim_depth=(radius * radius) / (4.0 * focal),
        mount_lift=max(0.22, min(0.46, float(config.mount_lift))),
        palette_style=palette_style,  # type: ignore[arg-type]
        palette=_PALETTES[palette_style],  # type: ignore[index]
        name=config.name,
    )


def _mesh_for_model(model: ArticulatedObject, geometry: object, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


def _register_materials(model: ArticulatedObject, r: ResolvedSatelliteDishConfig):
    return {name: model.material(f"satdish_{name}_{r.palette_style}", rgba=rgba)
            for name, rgba in r.palette.items()}


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_y() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _tilt_pt(r: ResolvedSatelliteDishConfig, x: float, y: float, z: float) -> tuple[float, float, float]:
    ca, sa = math.cos(_REST_TILT), math.sin(_REST_TILT)
    return (x * ca + z * sa, y, -x * sa + z * ca + r.mount_lift)


def _tilt_origin(r: ResolvedSatelliteDishConfig) -> Origin:
    return Origin(xyz=(0.0, 0.0, r.mount_lift), rpy=(0.0, _REST_TILT, 0.0))


def _tilt_cyl_x(r: ResolvedSatelliteDishConfig, x: float, y: float, z: float) -> Origin:
    return Origin(xyz=_tilt_pt(r, x, y, z), rpy=(0.0, math.pi / 2.0 + _REST_TILT, 0.0))


def _strut_between(
    part: Part,
    p0: tuple[float, float, float],
    p1: tuple[float, float, float],
    radius: float,
    material: object,
    name: str,
) -> None:
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-6:
        return
    pitch = math.atan2(math.sqrt(dx * dx + dy * dy), dz)
    yaw = math.atan2(dy, dx)
    mid = ((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5)
    part.visual(Cylinder(radius=radius, length=length), origin=Origin(xyz=mid, rpy=(0.0, pitch, yaw)),
                material=material, name=name, material_class_id="metal.paint_coated")


def _parabolic_shell_geometry(radius: float, focal: float, wall: float):
    outer: list[tuple[float, float]] = []
    inner: list[tuple[float, float]] = []
    for i in range(11):
        rr = max(radius * 0.04, radius * i / 10.0)
        z = (rr * rr) / (4.0 * focal)
        outer.append((rr, z))
        inner.append((max(radius * 0.03, rr - wall), max(0.0, z - wall)))
    return LatheGeometry.from_shell_profiles(
        outer, inner, segments=72, start_cap="round", end_cap="round", lip_samples=4
    ).rotate_y(math.pi / 2.0)


def _parabolic_panel_geometry(
    panel_idx: int,
    n_panels: int,
    radius: float,
    focal: float,
    wall: float,
    gap: float,
    *,
    r_inner_frac: float = 0.05,
    n_r: int = 9,
    n_a: int = 5,
) -> MeshGeometry:
    geom = MeshGeometry()
    seg = math.tau / n_panels
    theta0 = seg * panel_idx + gap * 0.5
    theta1 = seg * (panel_idx + 1) - gap * 0.5
    r_inner = radius * r_inner_frac
    outer: list[int] = []
    inner: list[int] = []
    for ja in range(n_a + 1):
        theta = theta0 + (theta1 - theta0) * ja / n_a
        ct, st = math.cos(theta), math.sin(theta)
        for ir in range(n_r + 1):
            rr = r_inner + (radius - r_inner) * ir / n_r
            z = (rr * rr) / (4.0 * focal) + 0.004
            x, y = rr * ct, rr * st
            outer.append(geom.add_vertex(x, y, z))
            inner.append(geom.add_vertex(x, y, z - wall))

    cols = n_r + 1
    for ja in range(n_a):
        for ir in range(n_r):
            o00 = outer[ja * cols + ir]
            o10 = outer[ja * cols + ir + 1]
            o01 = outer[(ja + 1) * cols + ir]
            o11 = outer[(ja + 1) * cols + ir + 1]
            i00 = inner[ja * cols + ir]
            i10 = inner[ja * cols + ir + 1]
            i01 = inner[(ja + 1) * cols + ir]
            i11 = inner[(ja + 1) * cols + ir + 1]
            geom.add_face(o00, o01, o10)
            geom.add_face(o10, o01, o11)
            geom.add_face(i00, i10, i01)
            geom.add_face(i10, i11, i01)
    for ir in range(n_r):
        o0, o1 = outer[ir], outer[ir + 1]
        i0, i1 = inner[ir], inner[ir + 1]
        geom.add_face(o0, o1, i0)
        geom.add_face(o1, i1, i0)
        base = n_a * cols
        o0, o1 = outer[base + ir], outer[base + ir + 1]
        i0, i1 = inner[base + ir], inner[base + ir + 1]
        geom.add_face(o0, i0, o1)
        geom.add_face(o1, i0, i1)
    for ja in range(n_a):
        o0 = outer[ja * cols + n_r]
        o1 = outer[(ja + 1) * cols + n_r]
        i0 = inner[ja * cols + n_r]
        i1 = inner[(ja + 1) * cols + n_r]
        geom.add_face(o0, i0, o1)
        geom.add_face(o1, i0, i1)
        o0 = outer[ja * cols]
        o1 = outer[(ja + 1) * cols]
        i0 = inner[ja * cols]
        i1 = inner[(ja + 1) * cols]
        geom.add_face(o0, o1, i0)
        geom.add_face(o1, i1, i0)
    return geom.rotate_y(math.pi / 2.0)


def _hex_facet_geometry(
    center_y: float,
    center_z: float,
    hex_radius: float,
    thickness: float,
    focal: float,
) -> MeshGeometry:
    r_sq = center_y * center_y + center_z * center_z
    depth = r_sq / (4.0 * focal)
    nx, ny, nz = 1.0, -center_y / (2.0 * focal), -center_z / (2.0 * focal)
    n_len = math.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / n_len, ny / n_len, nz / n_len
    cx, cy, cz = depth + 0.001 * nx, center_y + 0.001 * ny, center_z + 0.001 * nz

    geom = MeshGeometry()
    top: list[int] = []
    bot: list[int] = []
    for i in range(6):
        angle = math.pi / 6.0 + i * math.pi / 3.0
        hx = hex_radius * math.cos(angle)
        hy = hex_radius * math.sin(angle)
        top.append(geom.add_vertex(hx, hy, thickness * 0.5))
        bot.append(geom.add_vertex(hx, hy, -thickness * 0.5))
    tc = geom.add_vertex(0.0, 0.0, thickness * 0.5)
    bc = geom.add_vertex(0.0, 0.0, -thickness * 0.5)
    for i in range(6):
        j = (i + 1) % 6
        geom.add_face(tc, top[i], top[j])
        geom.add_face(bc, bot[j], bot[i])
        geom.add_face(top[i], bot[i], bot[j])
        geom.add_face(top[i], bot[j], top[j])

    cos_a = nz
    if cos_a < -0.9999:
        geom.rotate((0.0, 1.0, 0.0), math.pi)
    elif cos_a < 0.9999:
        ax, ay = -ny, nx
        axis_len = math.sqrt(ax * ax + ay * ay)
        if axis_len > 1e-10:
            geom.rotate((ax / axis_len, ay / axis_len, 0.0), math.acos(max(-1.0, min(1.0, cos_a))))
    return geom.translate(cx, cy, cz)


def _hex_grid_centers(hex_size: float, rings: int, max_radius: float) -> list[tuple[float, float]]:
    dirs = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    axial = [(0, 0)]
    for ring in range(1, rings + 1):
        q, rr = dirs[4][0] * ring, dirs[4][1] * ring
        for d in range(6):
            for _ in range(ring):
                axial.append((q, rr))
                q += dirs[d][0]
                rr += dirs[d][1]
    centers = []
    for q, rr in axial:
        y = hex_size * 1.5 * q
        z = hex_size * math.sqrt(3.0) * (rr + q * 0.5)
        if math.sqrt(y * y + z * z) <= max_radius:
            centers.append((y, z))
    return centers


def _build_base_box(model: ArticulatedObject, materials: dict[str, object]) -> Part:
    base = model.part("pedestal_base")
    base.visual(Box((_BOX_W, _BOX_D, _BOX_H)), origin=Origin(xyz=(0.0, 0.0, _BOX_H * 0.5)),
                material=materials["box"], name="equipment_box_body", material_class_id="metal.paint_coated")
    base.visual(Box((_BOX_W * 1.08, _BOX_D * 1.08, 0.035)), origin=Origin(xyz=(0.0, 0.0, 0.0175)),
                material=materials["box_dark"], name="ground_plinth", material_class_id="metal.paint_coated")
    base.visual(Box((_BOX_W * 0.94, 0.010, 0.012)), origin=Origin(xyz=(0.0, -_BOX_D * 0.5 - 0.004, _BOX_H * 0.86)),
                material=materials["glow"], name="front_glow_strip", material_class_id="tech.emissive_surface")
    for i in range(5):
        base.visual(Box((_BOX_W * 0.38, 0.010, 0.012)),
                    origin=Origin(xyz=(-_BOX_W * 0.20, -_BOX_D * 0.5 - 0.004, _BOX_H * (0.30 + i * 0.09))),
                    material=materials["glow"], name=f"front_grille_slat_{i}", material_class_id="tech.emissive_surface")
    for i in range(3):
        base.visual(Cylinder(radius=0.014, length=0.016),
                    origin=Origin(xyz=(_BOX_W * (0.18 + i * 0.10), _BOX_D * 0.5 + 0.006, _BOX_H * 0.42),
                                  rpy=_cyl_y()),
                    material=materials["accent"], name=f"rear_port_{i}", material_class_id="metal.paint_coated")
    base.visual(Cylinder(radius=0.052, length=0.105), origin=Origin(xyz=(0.0, 0.0, _BOX_H + 0.0525)),
                material=materials["mount"], name="pedestal_post", material_class_id="metal.paint_coated")
    base.visual(Cylinder(radius=0.088, length=0.030), origin=Origin(xyz=(0.0, 0.0, _BOX_H + 0.120)),
                material=materials["rim"], name="azimuth_bearing_race", material_class_id="metal.paint_coated")
    base.inertial = Inertial.from_geometry(Box((_BOX_W, _BOX_D, _BOX_H)), mass=42.0,
                                           origin=Origin(xyz=(0.0, 0.0, _BOX_H * 0.5)))
    return base


def _azimuth_z() -> float:
    return _BOX_H + 0.135


def _build_single_rear_yoke(model: ArticulatedObject, base: Part, materials: dict[str, object]) -> GimbalAnchors:
    yoke = model.part("azimuth_yoke")
    hinge_z = 0.235
    knuckle_x = 0.055
    yoke.visual(Cylinder(radius=0.052, length=0.050), origin=Origin(xyz=(0.0, 0.0, 0.025)),
                material=materials["mount"], name="yoke_collar", material_class_id="metal.paint_coated")
    yoke.visual(Cylinder(radius=0.030, length=hinge_z - 0.020),
                origin=Origin(xyz=(0.0, 0.0, hinge_z * 0.5 + 0.010)),
                material=materials["mount"], name="yoke_post", material_class_id="metal.paint_coated")
    _strut_between(yoke, (0.0, 0.0, hinge_z), (knuckle_x, 0.0, hinge_z), 0.022,
                   materials["mount"], "yoke_head_link")
    yoke.visual(Cylinder(radius=0.045, length=0.070),
                origin=Origin(xyz=(knuckle_x, 0.0, hinge_z), rpy=_cyl_y()),
                material=materials["rim"], name="yoke_knuckle", material_class_id="metal.paint_coated")
    yoke.inertial = Inertial.from_geometry(Box((0.16, 0.12, 0.30)), mass=4.0,
                                           origin=Origin(xyz=(0.02, 0.0, 0.14)))
    model.articulation("azimuth_rotation", ArticulationType.REVOLUTE, parent=base, child=yoke,
                       origin=Origin(xyz=(0.0, 0.0, _azimuth_z())), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=120.0, velocity=0.8, lower=-math.pi, upper=math.pi))
    return GimbalAnchors(yoke=yoke, hinge_z=hinge_z, knuckle_x=knuckle_x)


def _build_dual_arm_fork(model: ArticulatedObject, base: Part, materials: dict[str, object]) -> GimbalAnchors:
    yoke = model.part("azimuth_yoke")
    hinge_z = 0.240
    spread = 0.165
    yoke.visual(Cylinder(radius=0.056, length=0.050), origin=Origin(xyz=(0.0, 0.0, 0.025)),
                material=materials["mount"], name="yoke_collar", material_class_id="metal.paint_coated")
    yoke.visual(Box((0.16, spread * 1.35, 0.030)), origin=Origin(xyz=(0.0, 0.0, 0.065)),
                material=materials["mount"], name="fork_base_bridge", material_class_id="metal.paint_coated")
    for side, yy in enumerate((-spread * 0.5, spread * 0.5)):
        yoke.visual(Cylinder(radius=0.024, length=hinge_z - 0.070),
                    origin=Origin(xyz=(0.0, yy, (hinge_z + 0.070) * 0.5)),
                    material=materials["mount"], name=f"fork_arm_{side}", material_class_id="metal.paint_coated")
        yoke.visual(Cylinder(radius=0.044, length=0.045),
                    origin=Origin(xyz=(0.0, yy, hinge_z), rpy=_cyl_y()),
                    material=materials["rim"], name=f"bearing_housing_{side}", material_class_id="metal.paint_coated")
    yoke.visual(Cylinder(radius=0.020, length=spread * 0.92),
                origin=Origin(xyz=(0.0, 0.0, hinge_z), rpy=_cyl_y()),
                material=materials["rim"], name="shared_trunnion_socket", material_class_id="metal.paint_coated")
    yoke.inertial = Inertial.from_geometry(Box((0.18, 0.26, 0.30)), mass=5.0,
                                           origin=Origin(xyz=(0.0, 0.0, 0.15)))
    model.articulation("azimuth_rotation", ArticulationType.REVOLUTE, parent=base, child=yoke,
                       origin=Origin(xyz=(0.0, 0.0, _azimuth_z())), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=140.0, velocity=0.8, lower=-math.pi, upper=math.pi))
    return GimbalAnchors(yoke=yoke, hinge_z=hinge_z, knuckle_x=0.0)


def _build_tilt_tripod(model: ArticulatedObject, base: Part, materials: dict[str, object]) -> GimbalAnchors:
    yoke = model.part("azimuth_yoke")
    hinge_z = 0.285
    for i in range(3):
        ang = math.tau * i / 3.0 + math.pi / 6.0
        foot = (math.cos(ang) * 0.19, math.sin(ang) * 0.15, _BOX_H + 0.010)
        top = (math.cos(ang) * 0.055, math.sin(ang) * 0.045, _BOX_H + 0.115)
        _strut_between(base, foot, top, 0.015, materials["mount"], f"tripod_leg_bar_{i}")
        base.visual(Sphere(radius=0.020), origin=Origin(xyz=foot), material=materials["rim"], name=f"tripod_foot_{i}", material_class_id="metal.paint_coated")
    yoke.visual(Cylinder(radius=0.040, length=hinge_z), origin=Origin(xyz=(0.0, 0.0, hinge_z * 0.5)),
                material=materials["mount"], name="mast_shaft", material_class_id="metal.paint_coated")
    yoke.visual(Cylinder(radius=0.052, length=0.066), origin=Origin(xyz=(0.045, 0.0, hinge_z), rpy=_cyl_y()),
                material=materials["rim"], name="tilt_knuckle", material_class_id="metal.paint_coated")
    yoke.inertial = Inertial.from_geometry(Cylinder(radius=0.05, length=hinge_z), mass=4.0,
                                           origin=Origin(xyz=(0.0, 0.0, hinge_z * 0.5)))
    model.articulation("azimuth_rotation", ArticulationType.REVOLUTE, parent=base, child=yoke,
                       origin=Origin(xyz=(0.0, 0.0, _azimuth_z())), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=120.0, velocity=0.8, lower=-math.pi, upper=math.pi))
    return GimbalAnchors(yoke=yoke, hinge_z=hinge_z, knuckle_x=0.045)


def _build_mount_gimbal(
    model: ArticulatedObject,
    r: ResolvedSatelliteDishConfig,
    base: Part,
    materials: dict[str, object],
) -> GimbalAnchors:
    if r.mount_gimbal == "dual_arm_fork":
        return _build_dual_arm_fork(model, base, materials)
    if r.mount_gimbal == "tilt_tripod":
        return _build_tilt_tripod(model, base, materials)
    return _build_single_rear_yoke(model, base, materials)


def _add_reflector_core(model: ArticulatedObject, dish: Part, r: ResolvedSatelliteDishConfig,
                        materials: dict[str, object], *, inner_mat: str = "reflector_inner") -> None:
    shell = _parabolic_shell_geometry(r.dish_radius, r.focal, max(0.007, r.dish_radius * 0.026))
    dish.visual(_mesh_for_model(model, shell, "reflector_shell"), origin=_tilt_origin(r),
                material=materials[inner_mat], name="reflector_shell", material_class_id="metal.paint_coated")
    rim = TorusGeometry(radius=r.dish_radius, tube=max(0.006, r.dish_radius * 0.018),
                        radial_segments=12, tubular_segments=96)
    dish.visual(_mesh_for_model(model, rim, "reflector_rim"),
                origin=_tilt_cyl_x(r, r.rim_depth, 0.0, 0.0), material=materials["rim"], name="reflector_rim", material_class_id="metal.paint_coated")


def _add_dish_skeleton(dish: Part, r: ResolvedSatelliteDishConfig, materials: dict[str, object]) -> None:
    dish.visual(Cylinder(radius=0.020, length=0.18), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=_cyl_y()),
                material=materials["rim"], name="trunnion_shaft", material_class_id="metal.paint_coated")
    dish.visual(Sphere(radius=0.030), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                material=materials["rim"], name="trunnion_hub", material_class_id="metal.paint_coated")
    vertex = _tilt_pt(r, 0.0, 0.0, 0.0)
    _strut_between(dish, (0.0, 0.0, 0.0), vertex, 0.026, materials["mount"], "dish_neck")
    dish.visual(Cylinder(radius=r.dish_radius * 0.14, length=0.030), origin=_tilt_cyl_x(r, -0.010, 0.0, 0.0),
                material=materials["box_dark"], name="dish_back_hub", material_class_id="metal.paint_coated")


def _build_segmented_parabolic(model: ArticulatedObject, dish: Part, r: ResolvedSatelliteDishConfig,
                               materials: dict[str, object]) -> None:
    _add_reflector_core(model, dish, r, materials)
    n = max(8, min(24, r.panel_count))
    wall = max(0.004, r.dish_radius * 0.012)
    gap = min(0.018, math.tau / n * 0.10)
    for i in range(n):
        panel = _parabolic_panel_geometry(i, n, r.dish_radius * 0.98, r.focal, wall, gap)
        dish.visual(_mesh_for_model(model, panel, f"panel_{i}"), origin=_tilt_origin(r),
                    material=materials["reflector"], name=f"panel_{i}", material_class_id="metal.aluminum_bare")
        ang = math.tau * i / n
        p0 = _tilt_pt(r, 0.010, math.cos(ang) * r.dish_radius * 0.08, math.sin(ang) * r.dish_radius * 0.08)
        rr = r.dish_radius * 0.95
        p1 = _tilt_pt(r, (rr * rr) / (4.0 * r.focal) + 0.001, math.cos(ang) * rr, math.sin(ang) * rr)
        _strut_between(dish, p0, p1, max(0.0035, r.dish_radius * 0.010), materials["rim"], f"seam_{i}")


def _build_petal_segmented(model: ArticulatedObject, dish: Part, r: ResolvedSatelliteDishConfig,
                           materials: dict[str, object]) -> None:
    _add_reflector_core(model, dish, r, materials)
    n = max(8, min(18, r.panel_count))
    gap = min(0.034, math.tau / n * 0.16)
    for i in range(n):
        panel = _parabolic_panel_geometry(
            i, n, r.dish_radius * 0.99, r.focal, max(0.005, r.dish_radius * 0.014),
            gap, r_inner_frac=0.16, n_r=10, n_a=4
        )
        dish.visual(_mesh_for_model(model, panel, f"panel_{i}"), origin=_tilt_origin(r),
                    material=materials["reflector"], name=f"panel_{i}", material_class_id="metal.aluminum_bare")
        ang = math.tau * (i + 0.5) / n
        rr = r.dish_radius * 0.18
        bx = (rr * rr) / (4.0 * r.focal) + 0.010
        dish.visual(Sphere(radius=max(0.006, r.dish_radius * 0.022)),
                    origin=Origin(xyz=_tilt_pt(r, bx, math.cos(ang) * rr, math.sin(ang) * rr)),
                    material=materials["accent"], name=f"bolt_{i}", material_class_id="metal.paint_coated")


def _build_hex_faceted(model: ArticulatedObject, dish: Part, r: ResolvedSatelliteDishConfig,
                       materials: dict[str, object]) -> None:
    _add_reflector_core(model, dish, r, materials, inner_mat="box_dark")
    rings = 3
    for candidate in HEX_RING_COUNTS:
        if 1 + sum(6 * i for i in range(1, candidate + 1)) <= r.panel_count:
            rings = candidate
    hex_size = r.dish_radius * 0.128
    facet_radius = hex_size * 0.88
    centers = _hex_grid_centers(hex_size, rings, r.dish_radius - facet_radius * 0.85)
    for i, (yy, zz) in enumerate(centers):
        facet = _hex_facet_geometry(yy, zz, facet_radius, max(0.007, r.dish_radius * 0.024), r.focal)
        dish.visual(_mesh_for_model(model, facet, f"panel_{i}"), origin=_tilt_origin(r),
                    material=materials["reflector"], name=f"panel_{i}", material_class_id="metal.aluminum_bare")


def _build_flat_phased_array(model: ArticulatedObject, dish: Part, r: ResolvedSatelliteDishConfig,
                             materials: dict[str, object]) -> None:
    cols = 8 if r.panel_count % 8 == 0 else 6
    rows = max(3, min(6, r.panel_count // cols))
    width = r.dish_radius * 1.80
    height = width * rows / cols
    px = 0.035
    dish.visual(Box((0.028, width, height)), origin=Origin(xyz=_tilt_pt(r, px, 0.0, 0.0),
                                                           rpy=(0.0, _REST_TILT, 0.0)),
                material=materials["box_dark"], name="array_plate", material_class_id="tech.scifi_panel")
    dish.visual(Box((0.024, width * 0.64, height * 0.42)),
                origin=Origin(xyz=_tilt_pt(r, px - 0.032, 0.0, 0.0), rpy=(0.0, _REST_TILT, 0.0)),
                material=materials["mount"], name="back_housing", material_class_id="metal.paint_coated")
    _strut_between(dish, (0.0, 0.0, 0.0), _tilt_pt(r, px - 0.042, 0.0, 0.0),
                   0.028, materials["mount"], "array_neck")
    front_x = px + 0.014
    for name, yy, zz, sy, sz in (
        ("trim_top", 0.0, height * 0.50, width, 0.012),
        ("trim_bottom", 0.0, -height * 0.50, width, 0.012),
        ("trim_left", -width * 0.50, 0.0, 0.012, height),
        ("trim_right", width * 0.50, 0.0, 0.012, height),
    ):
        dish.visual(Box((0.010, sy, sz)), origin=Origin(xyz=_tilt_pt(r, front_x + 0.0045, yy, zz),
                                                        rpy=(0.0, _REST_TILT, 0.0)),
                    material=materials["glow"], name=name, material_class_id="tech.emissive_surface")
    idx = 0
    cell_w = width / (cols + 1)
    cell_h = height / (rows + 1)
    for row in range(rows):
        for col in range(cols):
            yy = (col - (cols - 1) * 0.5) * cell_w
            zz = (row - (rows - 1) * 0.5) * cell_h
            dish.visual(Box((0.007, cell_w * 0.62, cell_h * 0.62)),
                        origin=Origin(xyz=_tilt_pt(r, front_x + 0.0030, yy, zz), rpy=(0.0, _REST_TILT, 0.0)),
                        material=materials["reflector"], name=f"panel_{idx}", material_class_id="tech.scifi_panel")
            idx += 1


def _build_center_fed_horn(dish: Part, r: ResolvedSatelliteDishConfig, materials: dict[str, object]) -> None:
    focus_x = r.focal + 0.02
    _strut_between(dish, _tilt_pt(r, 0.0, 0.0, 0.0), _tilt_pt(r, focus_x, 0.0, 0.0),
                   0.012, materials["feed"], "feed_boom")
    dish.visual(Cylinder(radius=r.dish_radius * 0.09, length=0.070), origin=_tilt_cyl_x(r, focus_x, 0.0, 0.0),
                material=materials["feed"], name="feed_horn", material_class_id="metal.paint_coated")
    dish.visual(Sphere(radius=r.dish_radius * 0.040), origin=Origin(xyz=_tilt_pt(r, focus_x + 0.045, 0.0, 0.0)),
                material=materials["hot"], name="feed_tip", material_class_id="tech.emissive_surface")


def _build_cassegrain_sub(dish: Part, r: ResolvedSatelliteDishConfig, materials: dict[str, object]) -> None:
    sub_x = r.focal * 0.78
    sub = _tilt_pt(r, sub_x, 0.0, 0.0)
    dish.visual(Cylinder(radius=r.dish_radius * 0.22, length=0.018), origin=_tilt_cyl_x(r, sub_x, 0.0, 0.0),
                material=materials["feed"], name="subreflector_disc", material_class_id="metal.aluminum_bare")
    for i in range(4):
        ang = math.tau * i / 4.0 + math.pi / 4.0
        rr = r.dish_radius * 0.90
        rim = _tilt_pt(r, (rr * rr) / (4.0 * r.focal), math.cos(ang) * rr, math.sin(ang) * rr)
        _strut_between(dish, rim, sub, 0.0065, materials["mount"], f"subreflector_strut_{i}")
    dish.visual(Cylinder(radius=r.dish_radius * 0.065, length=0.050), origin=_tilt_cyl_x(r, 0.035, 0.0, 0.0),
                material=materials["hot"], name="vertex_feed_horn", material_class_id="tech.emissive_surface")


def _build_offset_feed_arm(dish: Part, r: ResolvedSatelliteDishConfig, materials: dict[str, object]) -> None:
    offset_z = -r.dish_radius * 0.48
    feed_x = r.focal + 0.09
    rim = _tilt_pt(r, r.rim_depth, 0.0, -r.dish_radius * 0.92)
    feed = _tilt_pt(r, feed_x, 0.0, offset_z)
    _strut_between(dish, rim, feed, 0.012, materials["feed"], "offset_arm")
    dish.visual(Box((0.038, 0.050, 0.050)), origin=Origin(xyz=rim, rpy=(0.0, _REST_TILT, 0.0)),
                material=materials["mount"], name="arm_rim_bracket", material_class_id="metal.paint_coated")
    for i in range(4):
        t = (i + 1) / 5.0
        cp = tuple(rim[k] + (feed[k] - rim[k]) * t for k in range(3))
        dish.visual(Sphere(radius=0.010), origin=Origin(xyz=cp), material=materials["accent"], name=f"arm_clamp_{i}", material_class_id="metal.paint_coated")
    dish.visual(Cylinder(radius=r.dish_radius * 0.075, length=0.060), origin=_tilt_cyl_x(r, feed_x, 0.0, offset_z),
                material=materials["feed"], name="offset_feed_horn", material_class_id="metal.paint_coated")


def _build_dish_assembly(
    model: ArticulatedObject,
    r: ResolvedSatelliteDishConfig,
    anchors: GimbalAnchors,
    materials: dict[str, object],
) -> Part:
    dish = model.part("dish_assembly")
    _add_dish_skeleton(dish, r, materials)
    if r.dish_form == "segmented_parabolic":
        _build_segmented_parabolic(model, dish, r, materials)
    elif r.dish_form == "petal_segmented":
        _build_petal_segmented(model, dish, r, materials)
    elif r.dish_form == "hex_faceted":
        _build_hex_faceted(model, dish, r, materials)
    else:
        _build_flat_phased_array(model, dish, r, materials)

    if r.feed == "center_fed_horn":
        _build_center_fed_horn(dish, r, materials)
    elif r.feed == "cassegrain_sub":
        _build_cassegrain_sub(dish, r, materials)
    elif r.feed == "offset_feed_arm":
        _build_offset_feed_arm(dish, r, materials)

    model.articulation("elevation_tilt", ArticulationType.REVOLUTE, parent=anchors.yoke, child=dish,
                       origin=Origin(xyz=(anchors.knuckle_x, 0.0, anchors.hinge_z)),
                       axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(effort=90.0, velocity=0.7, lower=-0.55, upper=0.85))
    dish.inertial = Inertial.from_geometry(Sphere(radius=max(0.12, r.dish_radius)), mass=6.0,
                                           origin=Origin(xyz=_tilt_pt(r, r.rim_depth * 0.35, 0.0, 0.0)))
    return dish


def build_satellite_dish(
    config: SatelliteDishConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or SatelliteDishConfig())
    model = ArticulatedObject(name=r.name, assets=assets)
    materials = _register_materials(model, r)
    base = _build_base_box(model, materials)
    anchors = _build_mount_gimbal(model, r, base, materials)
    _build_dish_assembly(model, r, anchors, materials)
    return model


def build_seeded_satellite_dish(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_satellite_dish(config_from_seed(seed), assets=assets)


def build_object_model() -> ArticulatedObject:
    return build_satellite_dish()


def slot_choices_for_config(config: SatelliteDishConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("dish_form", r.dish_form),
        ("mount_gimbal", r.mount_gimbal),
        ("feed", r.feed),
        ("panel_count", f"n{r.panel_count}"),
        ("palette_style", r.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def _visual_names(model: ArticulatedObject, part_name: str) -> set[str]:
    if part_name not in {part.name for part in model.parts}:
        return set()
    return {vis.name for vis in model.get_part(part_name).visuals if vis.name}


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    part_names = {part.name for part in model.parts}

    allow_islands = getattr(ctx, "allow_disconnected_islands", None)
    if "dish_assembly" in part_names and callable(allow_islands):
        allow_islands(
            model.get_part("dish_assembly"),
            reason="Source-backed rigid multi-piece aperture panels move as one dish head.",
        )

    def allow(pa: str, pb: str, reason: str) -> None:
        if pa not in part_names or pb not in part_names:
            return
        a = model.get_part(pa)
        b = model.get_part(pb)
        for ea in (v.name for v in a.visuals if v.name):
            for eb in (v.name for v in b.visuals if v.name):
                try:
                    ctx.allow_overlap(a, b, elem_a=ea, elem_b=eb, reason=reason)
                except Exception:
                    pass

    allow("pedestal_base", "azimuth_yoke", "azimuth collar seated in bearing")
    allow("azimuth_yoke", "dish_assembly", "elevation trunnion captured by yoke")


def run_satellite_dish_tests(object_model: ArticulatedObject, config: SatelliteDishConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, overlap_tol=0.006,
                                               overlap_volume_tol=0.0, ignore_adjacent=False,
                                               ignore_fixed=True)

    part_names = {part.name for part in object_model.parts}
    joint_names = {joint.name for joint in object_model.joints}
    if not {"pedestal_base", "azimuth_yoke", "dish_assembly"}.issubset(part_names):
        ctx.fail("identity_parts", "satellite dish must have base, azimuth_yoke, and dish_assembly")
    if not {"azimuth_rotation", "elevation_tilt"}.issubset(joint_names):
        ctx.fail("aiming_joints", "satellite dish must preserve azimuth and elevation revolute joints")
    for joint in object_model.joints:
        if joint.name == "azimuth_rotation" and joint.axis != (0.0, 0.0, 1.0):
            ctx.fail("azimuth_axis", "azimuth_rotation must rotate around +Z")
        if joint.name == "elevation_tilt" and joint.axis not in ((0.0, -1.0, 0.0), (0.0, 1.0, 0.0)):
            ctx.fail("elevation_axis", "elevation_tilt must rotate around horizontal Y")

    dish_visuals = _visual_names(object_model, "dish_assembly")
    if not any(name.startswith("panel_") for name in dish_visuals):
        ctx.fail("panel_loop", "dish aperture must loop-emit panel_{i}")
    if r.dish_form == "flat_phased_array":
        if "array_plate" not in dish_visuals:
            ctx.fail("flat_array_identity", "flat phased array must include array_plate")
        if any(name in dish_visuals for name in ("reflector_shell", "feed_horn", "subreflector_disc", "offset_feed_horn")):
            ctx.fail("flat_array_gate", "flat phased array must not use concave bowl or external feed")
    else:
        if not {"reflector_shell", "reflector_rim"}.issubset(dish_visuals):
            ctx.fail("round_dish_identity", "non-flat forms must include a continuous circular reflector shell and rim")
        if r.feed == "none":
            ctx.fail("feed_gate", "non-flat reflector must use a real feed")
        if r.dish_form == "hex_faceted" and len([n for n in dish_visuals if n.startswith("panel_")]) < 19:
            ctx.fail("hex_facets", "hex form should use concentric hex facet panels")

    return ctx.report()


__all__ = [
    "SatelliteDishConfig",
    "build_object_model",
    "build_satellite_dish",
    "build_seeded_satellite_dish",
    "config_from_seed",
    "resolve_config",
    "run_satellite_dish_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
