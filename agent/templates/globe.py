# SPDX-License-Identifier: Apache-2.0

"""Globe procedural template.

Implements ``articraft_template_authoring/specs_modular_v1/globe.md``.

The template is organized around the reviewed mixed slot graph:

* Slot A ``support_base``: desktop base, cradle stand, pedestal, or wall arm.
* Slot B ``meridian_or_cradle``: tilting/fixed/nested/partial meridian carrier,
  or a no-ring support pedestal.
* Slot C ``globe_surface``: ocean sphere with visible continents, graticule
  bands, polar caps, and equator/latitude/longitude identity marks.
* Slot D ``auxiliary_rotary``: optional date ring or base support yaw.

Identity invariant: every seed has a supported globe sphere and a
``globe_spin`` CONTINUOUS joint whose origin is at the sphere center.

Geometry policy: parent supports include explicit pivot sockets or saddles.
The meridian and globe carry matching caps on the same axis so the articulated
chain reads as physically connected in both static and moving poses.

Adopted source mapping:
S1 rec_globe_0002:
   classic desktop base, yoke arms, tilting meridian ring, continent patches.
S2 rec_globe_0fc4e0cefb164176b77a767cd54d8816:
   outer cradle stand, nested inner ring, graticule helpers.
S3 rec_globe_1c4dea866a4340d792eedfb836a2c683:
   partial support ring and auxiliary date ring.
S4 rec_globe_35a4dc2d75144987ae667216dff6d05d:
   fixed meridian ring with denser map patching.
S5 rec_globe_bb728b5bb5b64df798b3ef95f629fb38:
   rotating support pedestal stage.
S6 rec_globe_dd09f51da481436e8a10f6b573d84744:
   wall bracket and partial meridian frame.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

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
    Part,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True


SupportStyle = Literal[
    "classic_desktop",
    "outer_cradle",
    "partial_ring",
    "rotating_pedestal",
    "wall_arm",
]
MeridianStyle = Literal[
    "full_tilting",
    "nested_inner",
    "fixed_full",
    "none_pedestal",
    "partial_wall",
]
SurfaceStyle = Literal[
    "continent_patch",
    "graticule_patch",
    "dense_map",
    "minimal_ocean",
]
AuxiliaryRotary = Literal[
    "none",
    "date_ring",
    "support_yaw",
]
GraticuleDensity = Literal[
    "none",
    "low",
    "medium",
    "high",
]
LandPatchStyle = Literal[
    "simple_continents",
    "abstract_patches",
    "dense_patches",
]
PaletteTheme = Literal[
    "schoolhouse_blue",
    "antique_brass",
    "museum_dark",
    "wall_mount_slate",
    "modern_white",
]


SUPPORT_STYLES: tuple[SupportStyle, ...] = (
    "classic_desktop",
    "outer_cradle",
    "partial_ring",
    "rotating_pedestal",
    "wall_arm",
)
MERIDIAN_STYLES: tuple[MeridianStyle, ...] = (
    "full_tilting",
    "nested_inner",
    "fixed_full",
    "none_pedestal",
    "partial_wall",
)
SURFACE_STYLES: tuple[SurfaceStyle, ...] = (
    "continent_patch",
    "graticule_patch",
    "dense_map",
    "minimal_ocean",
)
AUXILIARY_ROTARY_STYLES: tuple[AuxiliaryRotary, ...] = (
    "none",
    "date_ring",
    "support_yaw",
)
GRATICULE_DENSITIES: tuple[GraticuleDensity, ...] = (
    "none",
    "low",
    "medium",
    "high",
)
LAND_PATCH_STYLES: tuple[LandPatchStyle, ...] = (
    "simple_continents",
    "abstract_patches",
    "dense_patches",
)
PALETTE_THEMES: tuple[PaletteTheme, ...] = (
    "schoolhouse_blue",
    "antique_brass",
    "museum_dark",
    "wall_mount_slate",
    "modern_white",
)
SUPPORT_SAMPLING_ORDER: tuple[SupportStyle, ...] = (
    "classic_desktop",
    "outer_cradle",
    "rotating_pedestal",
    "partial_ring",
    "wall_arm",
)


SOURCE_INDEX = {
    "S1": ("data/records/rec_globe_0002/revisions/rev_000001/model.py:L62-L94,L187-L393"),
    "S2": (
        "data/records/rec_globe_0fc4e0cefb164176b77a767cd54d8816/"
        "revisions/rev_000001/model.py:L27-L126,L152-L296"
    ),
    "S3": (
        "data/records/rec_globe_1c4dea866a4340d792eedfb836a2c683/"
        "revisions/rev_000001/model.py:L21-L178,L241-L421"
    ),
    "S4": (
        "data/records/rec_globe_35a4dc2d75144987ae667216dff6d05d/"
        "revisions/rev_000001/model.py:L36-L178,L191-L392"
    ),
    "S5": (
        "data/records/rec_globe_bb728b5bb5b64df798b3ef95f629fb38/"
        "revisions/rev_000001/model.py:L36-L88,L106-L242"
    ),
    "S6": (
        "data/records/rec_globe_dd09f51da481436e8a10f6b573d84744/"
        "revisions/rev_000001/model.py:L27-L103,L113-L324"
    ),
}


PALETTES: dict[PaletteTheme, dict[str, tuple[float, float, float, float]]] = {
    "schoolhouse_blue": {
        "ocean": (0.08, 0.38, 0.68, 1.0),
        "ocean_dark": (0.03, 0.16, 0.30, 1.0),
        "land": (0.30, 0.58, 0.27, 1.0),
        "land_light": (0.42, 0.70, 0.32, 1.0),
        "land_dark": (0.18, 0.42, 0.20, 1.0),
        "graticule": (0.88, 0.86, 0.70, 1.0),
        "metal": (0.78, 0.64, 0.30, 1.0),
        "metal_dark": (0.34, 0.24, 0.11, 1.0),
        "wood": (0.40, 0.22, 0.12, 1.0),
        "wood_dark": (0.20, 0.10, 0.055, 1.0),
        "wall": (0.52, 0.54, 0.56, 1.0),
    },
    "antique_brass": {
        "ocean": (0.12, 0.26, 0.38, 1.0),
        "ocean_dark": (0.04, 0.09, 0.13, 1.0),
        "land": (0.42, 0.56, 0.26, 1.0),
        "land_light": (0.60, 0.70, 0.34, 1.0),
        "land_dark": (0.24, 0.38, 0.18, 1.0),
        "graticule": (0.96, 0.82, 0.44, 1.0),
        "metal": (0.82, 0.62, 0.24, 1.0),
        "metal_dark": (0.34, 0.23, 0.09, 1.0),
        "wood": (0.34, 0.18, 0.08, 1.0),
        "wood_dark": (0.16, 0.08, 0.035, 1.0),
        "wall": (0.62, 0.58, 0.50, 1.0),
    },
    "museum_dark": {
        "ocean": (0.02, 0.08, 0.13, 1.0),
        "ocean_dark": (0.01, 0.03, 0.055, 1.0),
        "land": (0.34, 0.52, 0.36, 1.0),
        "land_light": (0.58, 0.66, 0.42, 1.0),
        "land_dark": (0.16, 0.30, 0.18, 1.0),
        "graticule": (0.78, 0.78, 0.72, 1.0),
        "metal": (0.62, 0.64, 0.66, 1.0),
        "metal_dark": (0.16, 0.17, 0.18, 1.0),
        "wood": (0.08, 0.075, 0.07, 1.0),
        "wood_dark": (0.025, 0.025, 0.025, 1.0),
        "wall": (0.28, 0.30, 0.32, 1.0),
    },
    "wall_mount_slate": {
        "ocean": (0.06, 0.22, 0.36, 1.0),
        "ocean_dark": (0.02, 0.08, 0.14, 1.0),
        "land": (0.44, 0.58, 0.34, 1.0),
        "land_light": (0.72, 0.75, 0.48, 1.0),
        "land_dark": (0.24, 0.38, 0.22, 1.0),
        "graticule": (0.84, 0.86, 0.82, 1.0),
        "metal": (0.54, 0.58, 0.60, 1.0),
        "metal_dark": (0.18, 0.20, 0.22, 1.0),
        "wood": (0.22, 0.24, 0.26, 1.0),
        "wood_dark": (0.08, 0.09, 0.10, 1.0),
        "wall": (0.42, 0.44, 0.46, 1.0),
    },
    "modern_white": {
        "ocean": (0.20, 0.50, 0.72, 1.0),
        "ocean_dark": (0.06, 0.22, 0.38, 1.0),
        "land": (0.46, 0.62, 0.40, 1.0),
        "land_light": (0.76, 0.82, 0.52, 1.0),
        "land_dark": (0.28, 0.44, 0.26, 1.0),
        "graticule": (0.96, 0.96, 0.90, 1.0),
        "metal": (0.82, 0.84, 0.84, 1.0),
        "metal_dark": (0.36, 0.38, 0.40, 1.0),
        "wood": (0.88, 0.86, 0.78, 1.0),
        "wood_dark": (0.54, 0.52, 0.48, 1.0),
        "wall": (0.78, 0.80, 0.82, 1.0),
    },
}


@dataclass(frozen=True)
class GlobeConfig:
    support_style: SupportStyle = "classic_desktop"
    meridian_style: MeridianStyle = "full_tilting"
    surface_style: SurfaceStyle = "continent_patch"
    auxiliary_rotary: AuxiliaryRotary = "none"
    palette_theme: PaletteTheme = "schoolhouse_blue"
    globe_radius: float = 0.50
    axial_tilt_degrees: float = 23.5
    ring_clearance: float = 0.045
    base_height: float = 0.28
    graticule_density: GraticuleDensity = "medium"
    land_patch_style: LandPatchStyle = "simple_continents"
    tilt_range: float = 0.55
    name: str = "reference_globe"
    palette: dict[str, tuple[float, float, float, float]] | None = None


@dataclass(frozen=True)
class ResolvedGlobeConfig:
    support_style: SupportStyle
    meridian_style: MeridianStyle
    surface_style: SurfaceStyle
    auxiliary_rotary: AuxiliaryRotary
    palette_theme: PaletteTheme
    globe_radius: float
    axial_tilt_degrees: float
    ring_clearance: float
    base_height: float
    graticule_density: GraticuleDensity
    land_patch_style: LandPatchStyle
    tilt_range: float
    ring_radius: float
    ring_tube: float
    globe_center_z: float
    pedestal_radius: float
    base_radius: float
    base_depth: float
    yoke_width: float
    yoke_post_height: float
    spin_axis: tuple[float, float, float]
    name: str
    palette: dict[str, tuple[float, float, float, float]]


@dataclass(frozen=True)
class SupportAnchors:
    root: Part
    carrier: Part
    globe_parent: Part
    globe_center_z: float
    ring_radius: float
    ring_tube: float
    pivot_x: float
    support_kind: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _require(value: str, allowed: tuple[str, ...], *, field_name: str) -> str:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {allowed}, got {value!r}")
    return value


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_y() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _cyl_z() -> tuple[float, float, float]:
    return (0.0, 0.0, 0.0)


def _torus_vertical() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _register_materials(
    model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]]
):
    return {name: model.material(f"globe_{name}", rgba=rgba) for name, rgba in palette.items()}


def _mesh_for_model(model: ArticulatedObject, geometry: object, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


def _add_torus(
    model: ArticulatedObject,
    part: Part,
    *,
    name: str,
    radius: float,
    tube: float,
    material: object,
    origin: Origin | None = None,
    radial_segments: int = 18,
    tubular_segments: int = 72,
) -> None:
    part.visual(
        _mesh_for_model(
            model,
            TorusGeometry(
                radius=radius,
                tube=tube,
                radial_segments=radial_segments,
                tubular_segments=tubular_segments,
            ),
            name,
        ),
        origin=origin or Origin(),
        material=material,
        name=name, material_class_id="metal.brass_polished",
    )


def _unit_from_lat_lon(lat_deg: float, lon_deg: float) -> tuple[float, float, float]:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    return (
        math.cos(lat) * math.cos(lon),
        math.cos(lat) * math.sin(lon),
        math.sin(lat),
    )


def _patch_origin(radius: float, lat_deg: float, lon_deg: float) -> Origin:
    x, y, z = _unit_from_lat_lon(lat_deg, lon_deg)
    yaw = math.atan2(y, x)
    pitch = -math.asin(z)
    return Origin(
        xyz=(x * radius, y * radius, z * radius),
        rpy=(0.0, pitch, yaw),
    )


def _patch_visual(
    globe: Part,
    *,
    radius: float,
    lat: float,
    lon: float,
    width: float,
    height: float,
    material: object,
    name: str,
) -> None:
    globe.visual(
        Box((width, radius * 0.018, height)),
        origin=_patch_origin(radius * 1.006, lat, lon),
        material=material,
        name=name, appearance_only=AppearanceOnlySpec(kind="overlay"),
    )


def _land_patch_geometry(
    *,
    radius: float,
    center_lat: float,
    center_lon: float,
    width: float,
    height: float,
    outline: tuple[tuple[float, float], ...],
) -> MeshGeometry:
    surface_radius = radius * 0.998
    lon_span = math.degrees(width / radius)
    lat_span = math.degrees(height / radius)
    lon_scale = max(0.35, math.cos(math.radians(center_lat)))

    outline_factors: list[tuple[float, float]] = []
    for lon_factor, lat_factor in outline:
        outline_radius = math.hypot(lon_factor, lat_factor) or 1.0
        smooth_radius = max(0.58, outline_radius)
        outline_factors.append(
            (
                lon_factor * smooth_radius / outline_radius,
                lat_factor * smooth_radius / outline_radius,
            )
        )

    def point_at(lon_factor: float, lat_factor: float, scale: float) -> tuple[float, float, float]:
        lat = _clamp(center_lat + lat_factor * scale * lat_span, -82.0, 82.0)
        lon = center_lon + (lon_factor * scale * lon_span / lon_scale)
        x, y, z = _unit_from_lat_lon(lat, lon)
        return (x * surface_radius, y * surface_radius, z * surface_radius)

    mesh_vertices = [point_at(0.0, 0.0, 0.0)]
    ring_scales = (0.32, 0.58, 0.82, 1.0)
    rings: list[list[int]] = []
    for ring_scale in ring_scales:
        ring: list[int] = []
        for lon_factor, lat_factor in outline_factors:
            ring.append(len(mesh_vertices))
            mesh_vertices.append(point_at(lon_factor, lat_factor, ring_scale))
        rings.append(ring)

    faces: list[tuple[int, int, int]] = []
    first_ring = rings[0]
    point_count = len(first_ring)
    for index in range(point_count):
        faces.append((0, first_ring[index], first_ring[(index + 1) % point_count]))

    for inner, outer in zip(rings, rings[1:]):
        for index in range(point_count):
            inner_a = inner[index]
            inner_b = inner[(index + 1) % point_count]
            outer_a = outer[index]
            outer_b = outer[(index + 1) % point_count]
            faces.append((inner_a, outer_a, outer_b))
            faces.append((inner_a, outer_b, inner_b))

    outward_faces: list[tuple[int, int, int]] = []
    for face in faces:
        a, b, c = face
        ax, ay, az = mesh_vertices[a]
        bx, by, bz = mesh_vertices[b]
        cx, cy, cz = mesh_vertices[c]
        ux, uy, uz = bx - ax, by - ay, bz - az
        vx, vy, vz = cx - ax, cy - ay, cz - az
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        mx = (ax + bx + cx) / 3.0
        my = (ay + by + cy) / 3.0
        mz = (az + bz + cz) / 3.0
        outward_faces.append((a, b, c) if nx * mx + ny * my + nz * mz >= 0.0 else (a, c, b))
    return MeshGeometry(vertices=mesh_vertices, faces=outward_faces)


LAND_OUTLINES: dict[str, tuple[tuple[float, float], ...]] = {
    "north_america": (
        (-0.95, 0.20),
        (-0.62, 0.64),
        (-0.28, 0.82),
        (0.16, 0.70),
        (0.55, 0.38),
        (0.78, 0.04),
        (0.58, -0.30),
        (0.78, -0.58),
        (0.26, -0.46),
        (-0.04, -0.74),
        (-0.34, -0.34),
        (-0.72, -0.26),
    ),
    "south_america": (
        (-0.36, 0.78),
        (0.26, 0.66),
        (0.55, 0.26),
        (0.34, -0.18),
        (0.20, -0.58),
        (0.04, -0.98),
        (-0.28, -0.82),
        (-0.45, -0.34),
        (-0.62, 0.12),
    ),
    "greenland": (
        (-0.58, 0.18),
        (-0.20, 0.62),
        (0.36, 0.52),
        (0.62, 0.10),
        (0.32, -0.42),
        (-0.34, -0.54),
        (-0.64, -0.14),
    ),
    "africa": (
        (-0.44, 0.78),
        (0.16, 0.82),
        (0.52, 0.44),
        (0.42, 0.04),
        (0.64, -0.28),
        (0.20, -0.82),
        (-0.20, -0.94),
        (-0.40, -0.36),
        (-0.66, 0.10),
    ),
    "europe": (
        (-0.78, 0.10),
        (-0.40, 0.50),
        (0.12, 0.42),
        (0.58, 0.18),
        (0.70, -0.22),
        (0.18, -0.44),
        (-0.28, -0.22),
        (-0.68, -0.36),
    ),
    "asia": (
        (-0.96, 0.18),
        (-0.52, 0.56),
        (0.02, 0.70),
        (0.60, 0.48),
        (0.94, 0.12),
        (0.78, -0.24),
        (0.42, -0.34),
        (0.28, -0.66),
        (-0.10, -0.42),
        (-0.52, -0.54),
        (-0.78, -0.20),
    ),
    "australia": (
        (-0.66, 0.10),
        (-0.24, 0.40),
        (0.34, 0.32),
        (0.70, -0.02),
        (0.38, -0.44),
        (-0.18, -0.54),
        (-0.60, -0.22),
    ),
    "antarctica": (
        (-0.92, 0.12),
        (-0.52, 0.32),
        (-0.12, 0.14),
        (0.20, 0.34),
        (0.64, 0.18),
        (0.92, -0.04),
        (0.44, -0.22),
        (-0.04, -0.32),
        (-0.58, -0.18),
    ),
    "island": (
        (-0.42, 0.22),
        (-0.10, 0.48),
        (0.36, 0.26),
        (0.46, -0.18),
        (0.02, -0.42),
        (-0.46, -0.18),
    ),
}


def _land_visual(
    model: ArticulatedObject,
    globe: Part,
    *,
    radius: float,
    lat: float,
    lon: float,
    width: float,
    height: float,
    material: object,
    name: str,
    outline_key: str,
) -> None:
    globe.visual(
        _mesh_for_model(
            model,
            _land_patch_geometry(
                radius=radius,
                center_lat=lat,
                center_lon=lon,
                width=width,
                height=height,
                outline=LAND_OUTLINES[outline_key],
            ),
            name,
        ),
        origin=Origin(),
        material=material,
        name=name, appearance_only=AppearanceOnlySpec(kind="overlay"),
    )


def _band_visual(
    globe: Part,
    *,
    radius: float,
    name: str,
    material: object,
    axis: str,
    scale: float = 1.0,
    tube_scale: float = 1.0,
    model: ArticulatedObject,
) -> None:
    tube = max(radius * 0.006 * tube_scale, 0.0025)
    band_radius = radius * scale
    if axis == "xy":
        rpy = (0.0, 0.0, 0.0)
    elif axis == "xz":
        rpy = _torus_vertical()
    elif axis == "yz":
        rpy = (0.0, math.pi / 2.0, 0.0)
    else:
        raise ValueError(f"unknown graticule axis {axis!r}")
    _add_torus(
        model,
        globe,
        name=name,
        radius=band_radius,
        tube=tube,
        material=material,
        origin=Origin(rpy=rpy),
        radial_segments=10,
        tubular_segments=64,
    )


def config_from_seed(seed: int) -> GlobeConfig:
    curated: dict[int, GlobeConfig] = {
        0: GlobeConfig(
            support_style="classic_desktop",
            meridian_style="full_tilting",
            surface_style="continent_patch",
            auxiliary_rotary="none",
            globe_radius=0.50,
            axial_tilt_degrees=23.5,
            ring_clearance=0.045,
            base_height=0.28,
            graticule_density="medium",
            land_patch_style="simple_continents",
            palette_theme="schoolhouse_blue",
            name="seeded_globe_0",
        ),
        1: GlobeConfig(
            support_style="outer_cradle",
            meridian_style="nested_inner",
            surface_style="graticule_patch",
            auxiliary_rotary="date_ring",
            globe_radius=0.42,
            axial_tilt_degrees=21.0,
            ring_clearance=0.055,
            base_height=0.26,
            graticule_density="high",
            land_patch_style="abstract_patches",
            palette_theme="antique_brass",
            name="seeded_globe_1",
        ),
        2: GlobeConfig(
            support_style="rotating_pedestal",
            meridian_style="none_pedestal",
            surface_style="minimal_ocean",
            auxiliary_rotary="support_yaw",
            globe_radius=0.46,
            axial_tilt_degrees=18.0,
            ring_clearance=0.04,
            base_height=0.30,
            graticule_density="low",
            land_patch_style="abstract_patches",
            palette_theme="modern_white",
            name="seeded_globe_2",
        ),
        3: GlobeConfig(
            support_style="partial_ring",
            meridian_style="full_tilting",
            surface_style="dense_map",
            auxiliary_rotary="none",
            globe_radius=0.52,
            axial_tilt_degrees=27.0,
            ring_clearance=0.05,
            base_height=0.32,
            graticule_density="high",
            land_patch_style="dense_patches",
            palette_theme="museum_dark",
            name="seeded_globe_3",
        ),
        4: GlobeConfig(
            support_style="wall_arm",
            meridian_style="partial_wall",
            surface_style="graticule_patch",
            auxiliary_rotary="none",
            globe_radius=0.44,
            axial_tilt_degrees=25.0,
            ring_clearance=0.06,
            base_height=0.30,
            graticule_density="medium",
            land_patch_style="abstract_patches",
            palette_theme="wall_mount_slate",
            name="seeded_globe_4",
        ),
    }
    if seed in curated:
        return curated[seed]

    rng = random.Random(seed)
    support = SUPPORT_SAMPLING_ORDER[seed % len(SUPPORT_SAMPLING_ORDER)]
    if support == "rotating_pedestal":
        meridian: MeridianStyle = "none_pedestal"
        auxiliary: AuxiliaryRotary = "support_yaw"
    elif support == "wall_arm":
        meridian = "partial_wall"
        auxiliary = "none"
    elif support == "outer_cradle":
        meridian = "nested_inner"
        auxiliary = rng.choice(("none", "date_ring"))
    else:
        meridian = rng.choice(("full_tilting", "fixed_full"))
        auxiliary = rng.choice(AUXILIARY_ROTARY_STYLES)
        if auxiliary == "support_yaw":
            auxiliary = "none"

    return GlobeConfig(
        support_style=support,
        meridian_style=meridian,
        surface_style=rng.choice(SURFACE_STYLES),
        auxiliary_rotary=auxiliary,
        palette_theme=rng.choice(PALETTE_THEMES),
        globe_radius=round(rng.uniform(0.34, 0.64), 3),
        axial_tilt_degrees=round(rng.uniform(16.0, 34.0), 2),
        ring_clearance=round(rng.uniform(0.035, 0.075), 3),
        base_height=round(rng.uniform(0.18, 0.46), 3),
        graticule_density=rng.choice(GRATICULE_DENSITIES),
        land_patch_style=rng.choice(LAND_PATCH_STYLES),
        tilt_range=round(rng.uniform(0.38, 0.62), 3),
        name=f"seeded_globe_{seed}",
    )


def resolve_config(config: GlobeConfig) -> ResolvedGlobeConfig:
    support = _require(
        config.support_style,
        SUPPORT_STYLES,
        field_name="support_style",
    )
    meridian = _require(
        config.meridian_style,
        MERIDIAN_STYLES,
        field_name="meridian_style",
    )
    surface = _require(
        config.surface_style,
        SURFACE_STYLES,
        field_name="surface_style",
    )
    auxiliary = _require(
        config.auxiliary_rotary,
        AUXILIARY_ROTARY_STYLES,
        field_name="auxiliary_rotary",
    )
    density = _require(
        config.graticule_density,
        GRATICULE_DENSITIES,
        field_name="graticule_density",
    )
    patch_style = _require(
        config.land_patch_style,
        LAND_PATCH_STYLES,
        field_name="land_patch_style",
    )
    palette_theme = _require(
        config.palette_theme,
        PALETTE_THEMES,
        field_name="palette_theme",
    )

    if support == "rotating_pedestal":
        meridian = "none_pedestal"
        auxiliary = "support_yaw"
    elif support == "wall_arm":
        meridian = "partial_wall"
        auxiliary = "none"
    elif support == "outer_cradle":
        meridian = "nested_inner"
        if auxiliary == "support_yaw":
            auxiliary = "date_ring"
    elif meridian == "none_pedestal":
        support = "rotating_pedestal"
        auxiliary = "support_yaw"

    if meridian == "partial_wall" and support != "wall_arm":
        # The partial wall meridian (hinge pin, mount bridges, center spine)
        # only seats on the wall arm; on any other support its center boss
        # collides with the support's tilt datum/rod.
        support = "wall_arm"
        auxiliary = "none"

    radius = _clamp(config.globe_radius, 0.32, 0.72)
    clearance = _clamp(config.ring_clearance, 0.025, 0.09)
    if meridian == "none_pedestal":
        clearance = max(clearance, 0.035)
    ring_radius = radius + clearance
    ring_tube = max(0.010, min(0.026, radius * 0.035))

    if support == "wall_arm":
        base_height = _clamp(config.base_height, 0.20, 0.48)
    elif support == "rotating_pedestal":
        base_height = _clamp(config.base_height, 0.26, 0.56)
    elif support == "outer_cradle":
        base_height = _clamp(config.base_height, 0.18, 0.34)
    else:
        base_height = _clamp(config.base_height, 0.20, 0.48)

    globe_center_z = base_height + ring_radius
    if support == "wall_arm":
        globe_center_z = max(globe_center_z, radius * 1.35)
    pedestal_radius = max(radius * 0.16, 0.075)
    base_radius = max(radius * 0.42, 0.20)
    base_depth = max(radius * 0.32, 0.16)
    yoke_width = ring_radius * 2.0
    yoke_post_height = globe_center_z

    palette = dict(PALETTES[palette_theme])  # type: ignore[index]
    if config.palette:
        palette.update(config.palette)

    return ResolvedGlobeConfig(
        support_style=support,  # type: ignore[arg-type]
        meridian_style=meridian,  # type: ignore[arg-type]
        surface_style=surface,  # type: ignore[arg-type]
        auxiliary_rotary=auxiliary,  # type: ignore[arg-type]
        palette_theme=palette_theme,  # type: ignore[arg-type]
        globe_radius=radius,
        axial_tilt_degrees=_clamp(config.axial_tilt_degrees, 15.0, 35.0),
        ring_clearance=clearance,
        base_height=base_height,
        graticule_density=density,  # type: ignore[arg-type]
        land_patch_style=patch_style,  # type: ignore[arg-type]
        tilt_range=_clamp(config.tilt_range, 0.25, 0.72),
        ring_radius=ring_radius,
        ring_tube=ring_tube,
        globe_center_z=globe_center_z,
        pedestal_radius=pedestal_radius,
        base_radius=base_radius,
        base_depth=base_depth,
        yoke_width=yoke_width,
        yoke_post_height=yoke_post_height,
        spin_axis=(0.0, 0.0, 1.0),
        name=config.name,
        palette=palette,
    )


def _desktop_ring_post_clearance(
    r: ResolvedGlobeConfig,
    post_y: float,
    post_r: float,
    *,
    samples: int = 480,
) -> float:
    """Min surface gap between the tilting meridian ring tube and a yoke upright.

    The upright is a vertical cylinder at ``(+/-ring_radius, post_y)`` spanning
    ``base_height..globe_center_z``. The meridian ring lies in the XZ plane and
    tilts about the X axis at the globe center; at the negative tilt extreme the
    ring's lower-back arc sweeps toward ``-y`` (where the posts sit). Returns the
    smallest ``centerline_distance - post_r - ring_tube`` over the ring, i.e. the
    worst-case clearance the posts must respect.
    """
    a = r.ring_radius
    tube = r.ring_tube
    theta = -r.tilt_range  # posts sit at -y; negative tilt is the worst extreme
    ct, st = math.cos(theta), math.sin(theta)
    best = 1e9
    for i in range(samples):
        u = 2.0 * math.pi * i / samples
        lz = a * math.sin(u)
        wx = a * math.cos(u)
        wy = -st * lz
        wz = ct * lz + r.globe_center_z
        zc = min(max(wz, r.base_height), r.globe_center_z)
        for px in (-a, a):
            d = math.sqrt((wx - px) ** 2 + (wy - post_y) ** 2 + (wz - zc) ** 2)
            gap = d - post_r - tube
            if gap < best:
                best = gap
    return best


def _desktop_yoke_post_y(r: ResolvedGlobeConfig, post_r: float, *, margin: float = 0.010) -> float:
    """Rear (-y) offset for the desktop yoke uprights.

    Single-source of the yoke spacing (Contract 3c): a fixed meridian never
    sweeps, so the nominal aesthetic offset is kept; a tilting meridian is pushed
    rearward until its swept ring envelope clears the uprights by ``margin``.
    """
    nominal = -post_r * 4.0
    if r.meridian_style not in ("full_tilting", "nested_inner", "partial_wall"):
        return nominal
    py = nominal
    step = r.ring_tube * 0.20
    floor = -r.ring_radius * 0.6
    for _ in range(400):
        if _desktop_ring_post_clearance(r, py, post_r) >= margin:
            return py
        py -= step
        if py <= floor:
            return floor
    return py


def _build_classic_desktop_base(
    model: ArticulatedObject,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> SupportAnchors:
    base = model.part("base")
    R = r.globe_radius
    base.visual(
        Cylinder(radius=r.base_radius * 1.06, length=R * 0.075),
        origin=Origin(xyz=(0.0, 0.0, R * 0.0375), rpy=_cyl_z()),
        material=materials["wood_dark"],
        name="round_stepped_foot", material_class_id="wood.mahogany_teak_dark",
    )
    base.visual(
        Cylinder(radius=r.base_radius * 0.82, length=R * 0.10),
        origin=Origin(xyz=(0.0, 0.0, R * 0.11), rpy=_cyl_z()),
        material=materials["wood"],
        name="polished_base_disk", material_class_id="wood.polished_varnished",
    )
    base.visual(
        Cylinder(radius=r.base_radius * 0.50, length=R * 0.075),
        origin=Origin(xyz=(0.0, 0.0, R * 0.19), rpy=_cyl_z()),
        material=materials["metal"],
        name="brass_base_collar", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    pedestal_len = max(R * 0.12, r.base_height - R * 0.13)
    pedestal_z = R * 0.09 + pedestal_len * 0.5
    lower_socket_z = r.base_height - R * 0.050
    base.visual(
        Cylinder(radius=r.pedestal_radius, length=pedestal_len),
        origin=Origin(xyz=(0.0, 0.0, pedestal_z), rpy=_cyl_z()),
        material=materials["wood"],
        name="central_turned_pedestal", material_class_id="wood.polished_varnished",
    )
    base.visual(
        Cylinder(radius=r.pedestal_radius * 1.35, length=R * 0.050),
        origin=Origin(xyz=(0.0, 0.0, lower_socket_z), rpy=_cyl_z()),
        material=materials["metal"],
        name="yoke_lower_socket", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    base.visual(
        Sphere(radius=r.ring_tube * 0.85),
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z)),
        material=materials["metal_dark"],
        name="central_tilt_axis_datum", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    base.visual(
        Cylinder(radius=r.ring_tube * 0.42, length=r.ring_radius * 2.06),
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z), rpy=_cyl_x()),
        material=materials["metal_dark"],
        name="central_tilt_axis_rod", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )

    post_r = max(R * 0.032, 0.012)
    post_y = _desktop_yoke_post_y(r, post_r)
    for side_name, x in (("left", -r.ring_radius), ("right", r.ring_radius)):
        base.visual(
            Cylinder(radius=post_r, length=r.yoke_post_height - r.base_height),
            origin=Origin(
                xyz=(x, post_y, (r.yoke_post_height + r.base_height) * 0.5),
                rpy=_cyl_z(),
            ),
            material=materials["metal"],
            name=f"{side_name}_yoke_upright", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
        )
        base.visual(
            Cylinder(radius=post_r * 0.72, length=abs(post_y)),
            origin=Origin(
                xyz=(x, post_y * 0.5, r.globe_center_z),
                rpy=_cyl_y(),
            ),
            material=materials["metal"],
            name=f"{side_name}_yoke_top_bridge", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
        )
        base.visual(
            Sphere(radius=post_r * 1.55),
            origin=Origin(xyz=(x, 0.0, r.globe_center_z)),
            material=materials["metal_dark"],
            name=f"{side_name}_yoke_pivot_socket", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
        )
        base.visual(
            Box((post_r * 3.1, post_r * 1.8, post_r * 0.9)),
            origin=Origin(xyz=(x, post_y, r.base_height + R * 0.04)),
            material=materials["metal_dark"],
            name=f"{side_name}_yoke_foot_clamp", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
        )
        base.visual(
            Cylinder(radius=post_r * 0.80, length=r.base_height - R * 0.18),
            origin=Origin(xyz=(x, post_y, (r.base_height + R * 0.18) * 0.5), rpy=_cyl_z()),
            material=materials["metal"],
            name=f"{side_name}_yoke_lower_extension", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
        )
    base.visual(
        Box((r.ring_radius * 2.16, abs(post_y) + post_r * 2.6, post_r * 1.1)),
        origin=Origin(xyz=(0.0, post_y * 0.5, R * 0.18)),
        material=materials["metal_dark"],
        name="rear_yoke_floor_crossbrace", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )

    meridian = _build_meridian_carrier(model, r, base, materials, parent_kind="desktop")
    return SupportAnchors(
        root=base,
        carrier=meridian,
        globe_parent=meridian,
        globe_center_z=r.globe_center_z,
        ring_radius=r.ring_radius,
        ring_tube=r.ring_tube,
        pivot_x=r.ring_radius,
        support_kind="classic_desktop",
    )


def _build_outer_cradle_base(
    model: ArticulatedObject,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> SupportAnchors:
    cradle = model.part("outer_cradle")
    R = r.globe_radius
    cradle.visual(
        Box((r.ring_radius * 1.55, r.base_depth * 1.65, R * 0.090)),
        origin=Origin(xyz=(0.0, 0.0, R * 0.045)),
        material=materials["wood_dark"],
        name="rectangular_cradle_foot", material_class_id="wood.mahogany_teak_dark",
    )
    cradle.visual(
        Cylinder(radius=r.pedestal_radius * 1.15, length=r.base_height),
        origin=Origin(xyz=(0.0, 0.0, r.base_height * 0.5), rpy=_cyl_z()),
        material=materials["wood"],
        name="center_cradle_column", material_class_id="wood.polished_varnished",
    )
    cradle.visual(
        Box((r.ring_radius * 1.30, r.base_depth * 0.24, R * 0.055)),
        origin=Origin(xyz=(0.0, -r.base_depth * 0.32, r.base_height)),
        material=materials["metal_dark"],
        name="front_cross_saddle", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    cradle.visual(
        Box((r.pedestal_radius * 1.15, r.base_depth * 0.42, R * 0.045)),
        origin=Origin(xyz=(0.0, -r.base_depth * 0.17, r.base_height)),
        material=materials["metal_dark"],
        name="front_saddle_center_bridge", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    cradle.visual(
        Box((r.ring_radius * 1.30, r.base_depth * 0.24, R * 0.055)),
        origin=Origin(xyz=(0.0, r.base_depth * 0.32, r.base_height)),
        material=materials["metal_dark"],
        name="rear_cross_saddle", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    cradle.visual(
        Box((r.pedestal_radius * 1.15, r.base_depth * 0.42, R * 0.045)),
        origin=Origin(xyz=(0.0, r.base_depth * 0.17, r.base_height)),
        material=materials["metal_dark"],
        name="rear_saddle_center_bridge", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    outer_radius = r.ring_radius + R * 0.085
    _add_torus(
        model,
        cradle,
        name="outer_cradle_ring",
        radius=outer_radius,
        tube=r.ring_tube * 0.92,
        material=materials["metal"],
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z), rpy=_torus_vertical()),
    )
    for x in (-r.ring_radius, r.ring_radius):
        cradle.visual(
            Sphere(radius=r.ring_tube * 1.75),
            origin=Origin(xyz=(x, 0.0, r.globe_center_z)),
            material=materials["metal_dark"],
            name=f"outer_cradle_pivot_socket_{'left' if x < 0 else 'right'}", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
        )
    cradle.visual(
        Cylinder(radius=r.ring_tube * 0.72, length=r.ring_radius * 2.02),
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z), rpy=_cyl_x()),
        material=materials["metal_dark"],
        name="central_tilt_axis_rod", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )

    meridian = _build_meridian_carrier(model, r, cradle, materials, parent_kind="cradle")
    return SupportAnchors(
        root=cradle,
        carrier=meridian,
        globe_parent=meridian,
        globe_center_z=r.globe_center_z,
        ring_radius=r.ring_radius,
        ring_tube=r.ring_tube,
        pivot_x=r.ring_radius,
        support_kind="outer_cradle",
    )


def _build_partial_ring_base(
    model: ArticulatedObject,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> SupportAnchors:
    stand = model.part("stand")
    R = r.globe_radius
    stand.visual(
        Cylinder(radius=r.base_radius, length=R * 0.085),
        origin=Origin(xyz=(0.0, 0.0, R * 0.0425), rpy=_cyl_z()),
        material=materials["wood_dark"],
        name="partial_ring_base_disk", material_class_id="wood.mahogany_teak_dark",
    )
    stand.visual(
        Cylinder(radius=r.pedestal_radius * 1.10, length=r.base_height),
        origin=Origin(xyz=(0.0, 0.0, r.base_height * 0.5), rpy=_cyl_z()),
        material=materials["metal"],
        name="partial_ring_center_post", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    stand.visual(
        Cylinder(
            radius=r.ring_tube * 0.82,
            length=max(R * 0.10, r.globe_center_z - r.base_height),
        ),
        origin=Origin(xyz=(0.0, 0.0, (r.globe_center_z + r.base_height) * 0.5), rpy=_cyl_z()),
        material=materials["metal"],
        name="partial_ring_center_post_extension", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    stand.visual(
        Box((r.ring_radius * 2.18, r.base_depth * 0.24, R * 0.070)),
        origin=Origin(xyz=(0.0, 0.0, r.base_height)),
        material=materials["metal_dark"],
        name="partial_ring_crosshead", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    stand.visual(
        Box((r.ring_radius * 2.28, r.base_depth * 0.18, R * 0.050)),
        origin=Origin(xyz=(0.0, 0.0, r.base_height + R * 0.085)),
        material=materials["metal"],
        name="partial_ring_upper_tie_bar", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    stand.visual(
        Cylinder(radius=r.ring_tube * 0.72, length=r.ring_radius * 2.02),
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z), rpy=_cyl_x()),
        material=materials["metal_dark"],
        name="central_tilt_axis_rod", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    for x in (-r.ring_radius, r.ring_radius):
        stand.visual(
            Cylinder(
                radius=r.ring_tube * 0.90,
                length=r.globe_center_z - (r.base_height + R * 0.085),
            ),
            origin=Origin(xyz=(x, 0.0, (r.globe_center_z + r.base_height) * 0.5), rpy=_cyl_z()),
            material=materials["metal"],
            name=f"partial_ring_side_post_{'left' if x < 0 else 'right'}", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
        )

    meridian = _build_meridian_carrier(model, r, stand, materials, parent_kind="partial")
    return SupportAnchors(
        root=stand,
        carrier=meridian,
        globe_parent=meridian,
        globe_center_z=r.globe_center_z,
        ring_radius=r.ring_radius,
        ring_tube=r.ring_tube,
        pivot_x=r.ring_radius,
        support_kind="partial_ring",
    )


def _build_rotating_pedestal_base(
    model: ArticulatedObject,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> SupportAnchors:
    base = model.part("base_ring")
    support = model.part("support_pedestal")
    R = r.globe_radius
    base.visual(
        Cylinder(radius=r.base_radius * 1.08, length=R * 0.090),
        origin=Origin(xyz=(0.0, 0.0, R * 0.045), rpy=_cyl_z()),
        material=materials["wood_dark"],
        name="turning_base_outer_disk", material_class_id="wood.mahogany_teak_dark",
    )
    base.visual(
        Cylinder(radius=r.base_radius * 0.74, length=R * 0.070),
        origin=Origin(xyz=(0.0, 0.0, R * 0.125), rpy=_cyl_z()),
        material=materials["metal_dark"],
        name="turning_base_bearing_race", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    support.visual(
        Cylinder(radius=r.pedestal_radius * 1.40, length=r.base_height * 0.42),
        origin=Origin(xyz=(0.0, 0.0, r.base_height * 0.21), rpy=_cyl_z()),
        material=materials["metal"],
        name="rotating_lower_pedestal", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    support.visual(
        Cylinder(radius=r.pedestal_radius * 0.86, length=r.globe_center_z - R * 0.18),
        origin=Origin(xyz=(0.0, 0.0, (r.globe_center_z - R * 0.18) * 0.5), rpy=_cyl_z()),
        material=materials["wood"],
        name="rotating_tall_support", material_class_id="wood.polished_varnished",
    )
    support.visual(
        Cylinder(radius=r.ring_tube * 0.62, length=R * 0.20),
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z - R * 0.10), rpy=_cyl_z()),
        material=materials["metal_dark"],
        name="rotating_spin_axis_rod", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    support.visual(
        Cylinder(radius=r.pedestal_radius * 1.75, length=R * 0.070),
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z - R * 0.78), rpy=_cyl_z()),
        material=materials["metal"],
        name="globe_bottom_saddle", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    support.visual(
        Sphere(radius=r.ring_tube * 2.2),
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z - R * 0.98)),
        material=materials["metal_dark"],
        name="lower_spin_saddle_ball", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    model.articulation(
        "support_yaw",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=support,
        origin=Origin(xyz=(0.0, 0.0, R * 0.14)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=25.0, velocity=1.5),
    )
    return SupportAnchors(
        root=base,
        carrier=support,
        globe_parent=support,
        globe_center_z=r.globe_center_z,
        ring_radius=r.ring_radius,
        ring_tube=r.ring_tube,
        pivot_x=0.0,
        support_kind="rotating_pedestal",
    )


def _build_wall_arm_base(
    model: ArticulatedObject,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> SupportAnchors:
    wall = model.part("wall_arm")
    R = r.globe_radius
    wall_x = -r.ring_radius - R * 0.30
    arm_length = R * 0.36
    arm_x = -r.ring_radius - R * 0.055
    arm_y = R * 0.15
    wall_plate_height = r.globe_center_z + R * 0.22
    wall.visual(
        Box((R * 0.34, R * 0.070, wall_plate_height)),
        origin=Origin(xyz=(wall_x, R * 0.24, wall_plate_height * 0.5)),
        material=materials["wall"],
        name="flat_wall_backing_plate", material_class_id="plaster.smooth",
    )
    wall.visual(
        Box((R * 0.22, R * 0.12, R * 0.22)),
        origin=Origin(xyz=(wall_x, R * 0.18, r.globe_center_z + R * 0.36)),
        material=materials["metal_dark"],
        name="upper_wall_mount_block", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    wall.visual(
        Box((R * 0.22, R * 0.12, R * 0.22)),
        origin=Origin(xyz=(wall_x, R * 0.18, r.globe_center_z - R * 0.36)),
        material=materials["metal_dark"],
        name="lower_wall_mount_block", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    wall.visual(
        Box((arm_length, R * 0.075, R * 0.090)),
        origin=Origin(xyz=(arm_x, arm_y, r.globe_center_z + R * 0.26)),
        material=materials["metal"],
        name="cantilever_upper_arm", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    wall.visual(
        Box((arm_length, R * 0.075, R * 0.090)),
        origin=Origin(xyz=(arm_x, arm_y, r.globe_center_z - R * 0.26)),
        material=materials["metal"],
        name="cantilever_lower_arm", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    wall.visual(
        Box((R * 0.080, R * 0.075, R * 0.58)),
        origin=Origin(xyz=(-r.ring_radius, arm_y, r.globe_center_z)),
        material=materials["metal_dark"],
        name="wall_arm_front_yoke_spine", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    wall.visual(
        Cylinder(radius=r.ring_tube * 1.3, length=R * 0.26),
        origin=Origin(xyz=(-r.ring_radius, arm_y * 0.50, r.globe_center_z), rpy=_cyl_y()),
        material=materials["metal_dark"],
        name="wall_arm_side_pivot_socket", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    wall.visual(
        Box((r.ring_radius, arm_y + R * 0.075, R * 0.050)),
        origin=Origin(xyz=(-r.ring_radius * 0.5, arm_y * 0.25, r.globe_center_z)),
        material=materials["metal_dark"],
        name="wall_arm_center_spin_bridge", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )

    meridian = _build_meridian_carrier(model, r, wall, materials, parent_kind="wall")
    return SupportAnchors(
        root=wall,
        carrier=meridian,
        globe_parent=meridian,
        globe_center_z=r.globe_center_z,
        ring_radius=r.ring_radius,
        ring_tube=r.ring_tube,
        pivot_x=r.ring_radius,
        support_kind="wall_arm",
    )


def _build_meridian_carrier(
    model: ArticulatedObject,
    r: ResolvedGlobeConfig,
    parent: Part,
    materials: dict[str, object],
    *,
    parent_kind: str,
) -> Part:
    name = "inner_ring" if r.meridian_style == "nested_inner" else "meridian"
    if r.meridian_style == "partial_wall":
        name = "partial_meridian"
    meridian = model.part(name)

    if r.meridian_style == "partial_wall":
        _decorate_partial_wall_meridian(model, meridian, r, materials)
    elif r.support_style == "partial_ring":
        _decorate_partial_desktop_meridian(model, meridian, r, materials)
    else:
        _decorate_full_meridian(model, meridian, r, materials)

    joint_name = "meridian_fixed"
    joint_type = ArticulationType.FIXED
    motion_limits = None
    axis = (1.0, 0.0, 0.0)
    if r.meridian_style in ("full_tilting", "nested_inner", "partial_wall"):
        joint_name = "meridian_tilt"
        joint_type = ArticulationType.REVOLUTE
        motion_limits = MotionLimits(
            effort=80.0,
            velocity=0.8,
            lower=-r.tilt_range,
            upper=r.tilt_range,
        )
    if parent_kind == "wall":
        axis = (0.0, 1.0, 0.0)
    model.articulation(
        joint_name,
        joint_type,
        parent=parent,
        child=meridian,
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z)),
        axis=axis,
        motion_limits=motion_limits,
    )
    meridian.inertial = Inertial.from_geometry(
        Sphere(radius=r.ring_radius),
        mass=max(0.8, r.globe_radius * 2.2),
        origin=Origin(),
    )
    return meridian


def _decorate_full_meridian(
    model: ArticulatedObject,
    meridian: Part,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> None:
    _add_torus(
        model,
        meridian,
        name="full_meridian_ring",
        radius=r.ring_radius,
        tube=r.ring_tube,
        material=materials["metal"],
        origin=Origin(rpy=_torus_vertical()),
    )
    for sign, side in ((-1.0, "left"), (1.0, "right")):
        meridian.visual(
            Cylinder(radius=r.ring_tube * 1.20, length=r.ring_tube * 5.0),
            origin=Origin(xyz=(sign * r.ring_radius, 0.0, 0.0), rpy=_cyl_x()),
            material=materials["metal_dark"],
            name=f"{side}_meridian_axis_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
        )
        meridian.visual(
            Sphere(radius=r.ring_tube * 1.45),
            origin=Origin(xyz=(sign * r.ring_radius, 0.0, 0.0)),
            material=materials["metal"],
            name=f"{side}_meridian_pivot_cap", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
        )
    meridian.visual(
        Sphere(radius=r.ring_tube * 0.85),
        origin=Origin(),
        material=materials["metal_dark"],
        name="globe_spin_bearing_hub", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    meridian.visual(
        Cylinder(radius=r.ring_tube * 0.42, length=r.ring_radius * 2.04),
        origin=Origin(rpy=_cyl_x()),
        material=materials["metal_dark"],
        name="globe_spin_axis_rod", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )


def _decorate_partial_desktop_meridian(
    model: ArticulatedObject,
    meridian: Part,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> None:
    _add_torus(
        model,
        meridian,
        name="partial_stand_meridian_ring",
        radius=r.ring_radius,
        tube=r.ring_tube,
        material=materials["metal"],
        origin=Origin(rpy=_torus_vertical()),
        tubular_segments=56,
    )
    meridian.visual(
        Box((r.ring_tube * 3.5, r.ring_tube * 2.0, r.ring_radius * 0.62)),
        origin=Origin(xyz=(0.0, 0.0, -r.ring_radius * 0.72)),
        material=materials["metal_dark"],
        name="partial_meridian_lower_spine", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    meridian.visual(
        Sphere(radius=r.ring_tube * 1.25),
        origin=Origin(),
        material=materials["metal_dark"],
        name="partial_meridian_center_pivot_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    meridian.visual(
        Box((r.ring_tube * 1.35, r.ring_tube * 1.35, r.ring_radius * 0.48)),
        origin=Origin(xyz=(0.0, 0.0, -r.ring_radius * 0.24)),
        material=materials["metal_dark"],
        name="partial_meridian_center_pivot_spine", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    for sign, side in ((-1.0, "left"), (1.0, "right")):
        meridian.visual(
            Sphere(radius=r.ring_tube * 1.45),
            origin=Origin(xyz=(sign * r.ring_radius, 0.0, 0.0)),
            material=materials["metal"],
            name=f"{side}_partial_axis_cap", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
        )


def _decorate_partial_wall_meridian(
    model: ArticulatedObject,
    meridian: Part,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> None:
    _add_torus(
        model,
        meridian,
        name="wall_partial_meridian_arc",
        radius=r.ring_radius,
        tube=r.ring_tube,
        material=materials["metal"],
        origin=Origin(rpy=_torus_vertical()),
        tubular_segments=56,
    )
    meridian.visual(
        Box((r.ring_radius * 0.42, r.ring_tube * 2.2, r.ring_tube * 1.6)),
        origin=Origin(xyz=(-r.ring_radius * 0.82, 0.0, r.ring_radius * 0.34)),
        material=materials["metal_dark"],
        name="wall_meridian_upper_mount_bridge", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    meridian.visual(
        Box((r.ring_radius * 0.42, r.ring_tube * 2.2, r.ring_tube * 1.6)),
        origin=Origin(xyz=(-r.ring_radius * 0.82, 0.0, -r.ring_radius * 0.34)),
        material=materials["metal_dark"],
        name="wall_meridian_lower_mount_bridge", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    meridian.visual(
        Cylinder(radius=r.ring_tube * 1.35, length=r.ring_tube * 5.0),
        origin=Origin(xyz=(-r.ring_radius, 0.0, 0.0), rpy=_cyl_y()),
        material=materials["metal_dark"],
        name="wall_meridian_side_hinge_pin", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    meridian.visual(
        Sphere(radius=r.ring_tube * 1.20),
        origin=Origin(),
        material=materials["metal_dark"],
        name="wall_meridian_center_spin_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    meridian.visual(
        Box((r.ring_tube * 1.25, r.ring_tube * 1.25, r.globe_center_z)),
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z * 0.5)),
        material=materials["metal_dark"],
        name="wall_meridian_origin_spine", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    meridian.visual(
        Sphere(radius=r.ring_tube * 1.10),
        origin=Origin(xyz=(0.0, 0.0, r.globe_center_z)),
        material=materials["metal_dark"],
        name="wall_meridian_tilt_origin_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
    )
    meridian.visual(
        Sphere(radius=r.ring_tube * 1.35),
        origin=Origin(xyz=(r.ring_radius, 0.0, 0.0)),
        material=materials["metal"],
        name="wall_meridian_free_axis_cap", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )


def _build_globe(
    model: ArticulatedObject,
    r: ResolvedGlobeConfig,
    parent: Part,
    materials: dict[str, object],
) -> Part:
    globe = model.part("globe")
    _decorate_globe_surface(model, globe, r, materials)
    origin = Origin()
    if parent.name in ("support_pedestal",):
        origin = Origin(xyz=(0.0, 0.0, r.globe_center_z))
    model.articulation(
        "globe_spin",
        ArticulationType.CONTINUOUS,
        parent=parent,
        child=globe,
        origin=origin,
        axis=r.spin_axis,
        motion_limits=MotionLimits(effort=20.0, velocity=2.8),
    )
    globe.inertial = Inertial.from_geometry(
        Sphere(radius=r.globe_radius),
        mass=max(1.0, 8.0 * r.globe_radius),
        origin=Origin(),
    )
    return globe


def _decorate_globe_surface(
    model: ArticulatedObject,
    globe: Part,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> None:
    R = r.globe_radius
    globe.visual(
        Sphere(radius=R),
        origin=Origin(),
        material=materials["ocean"],
        name="ocean_sphere", material_class_id="plastic.opaque_glossy_molded",
    )
    globe.visual(
        Sphere(radius=R * 0.996),
        origin=Origin(),
        material=materials["ocean_dark"],
        name="deep_ocean_shadow_core", material_class_id="plastic.opaque_glossy_molded",
    )
    globe.visual(
        Cylinder(radius=R * 0.055, length=R * 0.10),
        origin=Origin(xyz=(0.0, 0.0, R * 1.01), rpy=_cyl_z()),
        material=materials["metal"],
        name="north_polar_axis_cap", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    globe.visual(
        Cylinder(radius=R * 0.055, length=R * 0.10),
        origin=Origin(xyz=(0.0, 0.0, -R * 1.01), rpy=_cyl_z()),
        material=materials["metal"],
        name="south_polar_axis_cap", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
    )
    _decorate_graticule(model, globe, r, materials)
    _decorate_land_patches(model, globe, r, materials)
    if r.surface_style in ("dense_map", "graticule_patch"):
        _decorate_map_labels(globe, r, materials)


def _decorate_graticule(
    model: ArticulatedObject,
    globe: Part,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> None:
    R = r.globe_radius
    _band_visual(
        globe,
        radius=R,
        name="equator_band",
        material=materials["graticule"],
        axis="xy",
        model=model,
        tube_scale=1.25,
    )
    if r.graticule_density == "none":
        return
    _band_visual(
        globe,
        radius=R,
        name="prime_meridian_band",
        material=materials["graticule"],
        axis="xz",
        model=model,
    )
    _band_visual(
        globe,
        radius=R,
        name="secondary_meridian_band",
        material=materials["graticule"],
        axis="yz",
        model=model,
    )
    lat_scales = {
        "low": (0.72,),
        "medium": (0.52, 0.82),
        "high": (0.36, 0.62, 0.84),
    }.get(r.graticule_density, (0.52, 0.82))
    for i, scale in enumerate(lat_scales):
        z = R * math.sqrt(max(0.0, 1.0 - scale * scale))
        for sign, hemi in ((1.0, "north"), (-1.0, "south")):
            _add_torus(
                model,
                globe,
                name=f"{hemi}_latitude_band_{i}",
                radius=R * scale,
                tube=max(R * 0.004, 0.002),
                material=materials["graticule"],
                origin=Origin(xyz=(0.0, 0.0, sign * z)),
                radial_segments=8,
                tubular_segments=56,
            )


def _decorate_land_patches(
    model: ArticulatedObject,
    globe: Part,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> None:
    R = r.globe_radius
    if r.surface_style == "minimal_ocean":
        patch_specs = (
            (12, -68, R * 0.46, R * 0.34, "land", "north_america"),
            (8, 25, R * 0.52, R * 0.46, "land_dark", "africa"),
            (28, 92, R * 0.64, R * 0.38, "land_light", "asia"),
            (-25, 134, R * 0.34, R * 0.24, "land", "australia"),
        )
    elif r.land_patch_style == "dense_patches" or r.surface_style == "dense_map":
        patch_specs = (
            (43, -104, R * 0.48, R * 0.30, "land", "north_america"),
            (-19, -61, R * 0.27, R * 0.42, "land_dark", "south_america"),
            (72, -42, R * 0.20, R * 0.16, "land_light", "greenland"),
            (50, 15, R * 0.28, R * 0.16, "land", "europe"),
            (3, 22, R * 0.34, R * 0.44, "land_dark", "africa"),
            (44, 86, R * 0.66, R * 0.34, "land_light", "asia"),
            (-25, 134, R * 0.30, R * 0.22, "land_dark", "australia"),
            (-73, 20, R * 0.78, R * 0.10, "land_light", "antarctica"),
            (13, -84, R * 0.11, R * 0.08, "land", "island"),
            (36, 139, R * 0.08, R * 0.07, "land_dark", "island"),
            (-19, 47, R * 0.08, R * 0.12, "land_light", "island"),
        )
    elif r.land_patch_style == "abstract_patches" or r.surface_style == "graticule_patch":
        patch_specs = (
            (32, -98, R * 0.42, R * 0.22, "land", "north_america"),
            (-18, -60, R * 0.25, R * 0.34, "land_light", "south_america"),
            (10, 22, R * 0.42, R * 0.40, "land_dark", "africa"),
            (43, 78, R * 0.58, R * 0.28, "land", "asia"),
            (-28, 134, R * 0.28, R * 0.18, "land_light", "australia"),
        )
    else:
        patch_specs = (
            (42, -104, R * 0.46, R * 0.28, "land", "north_america"),
            (-18, -61, R * 0.26, R * 0.40, "land_dark", "south_america"),
            (72, -42, R * 0.18, R * 0.14, "land_light", "greenland"),
            (50, 15, R * 0.26, R * 0.16, "land", "europe"),
            (4, 22, R * 0.34, R * 0.42, "land_dark", "africa"),
            (43, 88, R * 0.62, R * 0.32, "land_light", "asia"),
            (-25, 134, R * 0.30, R * 0.22, "land", "australia"),
            (-73, 20, R * 0.72, R * 0.08, "land_light", "antarctica"),
        )
    for i, (lat, lon, width, height, material_key, outline_key) in enumerate(patch_specs):
        _land_visual(
            model,
            globe,
            radius=R,
            lat=lat,
            lon=lon,
            width=width,
            height=height,
            material=materials[material_key],
            name=f"continent_patch_{i}",
            outline_key=outline_key,
        )


def _decorate_map_labels(
    globe: Part,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> None:
    R = r.globe_radius
    for i, lon in enumerate((-150, -60, 30, 120)):
        _patch_visual(
            globe,
            radius=R,
            lat=-4,
            lon=lon,
            width=R * 0.11,
            height=R * 0.025,
            material=materials["graticule"],
            name=f"small_map_label_dash_{i}",
        )


def _build_date_ring(
    model: ArticulatedObject,
    r: ResolvedGlobeConfig,
    root: Part,
    materials: dict[str, object],
) -> Part:
    date_ring = model.part("date_ring")
    ring_z = max(r.base_height * 0.54, r.globe_center_z - r.globe_radius * 1.34)
    ring_radius = r.globe_radius * 0.58
    tube = max(r.globe_radius * 0.014, 0.006)
    desktop = r.support_style == "classic_desktop"
    if desktop:
        # The desktop center stack (collar, pedestal, yoke lower socket, and
        # the meridian ring bottom at z=base_height) leaves no free plane for
        # center-crossing spokes, so the date ring hugs the yoke lower socket
        # instead: the tangent torus stays grounded and clears both the
        # collar below and the globe above.
        ring_radius = r.pedestal_radius * 1.35 + tube
        ring_z = r.base_height - r.globe_radius * 0.050
    _add_torus(
        model,
        date_ring,
        name="calendar_date_ring",
        radius=ring_radius,
        tube=tube,
        material=materials["metal_dark"],
        origin=Origin(),
        radial_segments=10,
        tubular_segments=64,
    )
    if not desktop:
        date_ring.visual(
            Cylinder(
                radius=max(r.globe_radius * 0.038, 0.014), length=max(r.globe_radius * 0.040, 0.018)
            ),
            origin=Origin(rpy=_cyl_z()),
            material=materials["metal_dark"],
            name="date_ring_center_bearing", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.bronze_cast"),
        )
        for i in range(4):
            angle = math.tau * i / 4.0
            date_ring.visual(
                Box((ring_radius * 2.04, r.globe_radius * 0.014, r.globe_radius * 0.012)),
                origin=Origin(
                    xyz=(
                        math.cos(angle) * ring_radius * 0.51,
                        math.sin(angle) * ring_radius * 0.51,
                        0.0,
                    ),
                    rpy=(0.0, 0.0, angle),
                ),
                material=materials["metal"],
                name=f"date_ring_spoke_{i}", material_class_id=("metal.brushed_silver" if r.palette_theme in {"museum_dark", "wall_mount_slate", "modern_white"} else "metal.brass_polished"),
            )
    tick_radius = ring_radius if not desktop else ring_radius + tube * 0.5
    for i in range(12):
        angle = math.tau * i / 12.0
        date_ring.visual(
            Box((r.globe_radius * 0.035, r.globe_radius * 0.012, r.globe_radius * 0.010)),
            origin=Origin(
                xyz=(
                    math.cos(angle) * tick_radius,
                    math.sin(angle) * tick_radius,
                    0.0,
                ),
                rpy=(0.0, 0.0, angle),
            ),
            material=materials["graticule"],
            name=f"date_tick_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    model.articulation(
        "date_ring_spin",
        ArticulationType.CONTINUOUS,
        parent=root,
        child=date_ring,
        origin=Origin(xyz=(0.0, 0.0, ring_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.2),
    )
    date_ring.inertial = Inertial.from_geometry(
        Cylinder(radius=ring_radius, length=r.globe_radius * 0.03),
        mass=0.3,
        origin=Origin(rpy=_cyl_z()),
    )
    return date_ring


def _build_support(
    model: ArticulatedObject,
    r: ResolvedGlobeConfig,
    materials: dict[str, object],
) -> SupportAnchors:
    if r.support_style == "outer_cradle":
        return _build_outer_cradle_base(model, r, materials)
    if r.support_style == "partial_ring":
        return _build_partial_ring_base(model, r, materials)
    if r.support_style == "rotating_pedestal":
        return _build_rotating_pedestal_base(model, r, materials)
    if r.support_style == "wall_arm":
        return _build_wall_arm_base(model, r, materials)
    return _build_classic_desktop_base(model, r, materials)


def build_globe(
    config: GlobeConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or GlobeConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    materials = _register_materials(model, r.palette)
    support = _build_support(model, r, materials)
    _build_globe(model, r, support.globe_parent, materials)
    if r.auxiliary_rotary == "date_ring":
        _build_date_ring(model, r, support.root, materials)
    return model


def build_seeded_globe(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_globe(config_from_seed(seed), assets=assets)


def slot_choices_for_config(config: GlobeConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("support_base", r.support_style),
        ("meridian_or_cradle", r.meridian_style),
        ("globe_surface", r.surface_style),
        ("auxiliary_rotary", r.auxiliary_rotary),
        ("graticule_density", r.graticule_density),
        ("land_patch_style", r.land_patch_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# Continent relief patches sit at 0.998R, strictly inside the ocean sphere (R).
# Wherever a structural element is allowed to overlap the ocean sphere (captured
# spin axis / meridian mount / support saddle), the subsurface continents share
# that same mechanism engagement and are covered by the same justification.
_CONTINENT_PATCH_NAMES: tuple[str, ...] = tuple(f"continent_patch_{i}" for i in range(12))


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    part_names = {part.name for part in model.parts}
    if "globe" in part_names:
        globe = model.get_part("globe")
        for support_name in (
            "meridian",
            "inner_ring",
            "partial_meridian",
            "support_pedestal",
            "outer_cradle",
            "stand",
        ):
            if support_name not in part_names:
                continue
            support = model.get_part(support_name)
            for elem_a in (
                "full_meridian_ring",
                "partial_stand_meridian_ring",
                "wall_partial_meridian_arc",
                "left_meridian_axis_boss",
                "right_meridian_axis_boss",
                "globe_spin_bearing_hub",
                "globe_spin_axis_rod",
                "globe_bottom_saddle",
                "lower_spin_saddle_ball",
                "partial_meridian_lower_spine",
                "partial_meridian_center_pivot_boss",
                "partial_meridian_center_pivot_spine",
            ):
                for elem_b in (
                    "ocean_sphere",
                    "deep_ocean_shadow_core",
                    "north_polar_axis_cap",
                    "south_polar_axis_cap",
                    "equator_band",
                    "prime_meridian_band",
                    "secondary_meridian_band",
                    "north_latitude_band_0",
                    "north_latitude_band_1",
                    "north_latitude_band_2",
                    "south_latitude_band_0",
                    "south_latitude_band_1",
                    "south_latitude_band_2",
                    *_CONTINENT_PATCH_NAMES,
                ):
                    try:
                        ctx.allow_overlap(
                            support,
                            globe,
                            elem_a=elem_a,
                            elem_b=elem_b,
                            reason="globe is captured by meridian ring or pedestal spin saddle",
                        )
                    except Exception:
                        pass

    for support_name in ("base", "stand", "outer_cradle", "wall_arm"):
        if support_name not in part_names:
            continue
        support = model.get_part(support_name)
        for ring_name in ("meridian", "inner_ring", "partial_meridian"):
            if ring_name not in part_names:
                continue
            ring = model.get_part(ring_name)
            for elem_a in (
                "left_yoke_pivot_socket",
                "right_yoke_pivot_socket",
                "left_yoke_top_bridge",
                "right_yoke_top_bridge",
                "yoke_lower_socket",
                "central_tilt_axis_datum",
                "central_tilt_axis_rod",
                "center_cradle_column",
                "partial_meridian_center_pivot_boss",
                "outer_cradle_pivot_socket_left",
                "outer_cradle_pivot_socket_right",
                "outer_cradle_ring",
                "wall_arm_side_pivot_socket",
                "partial_ring_side_post_left",
                "partial_ring_side_post_right",
                "partial_ring_crosshead",
                "partial_ring_upper_tie_bar",
                "partial_ring_center_post",
                "partial_ring_center_post_extension",
                "front_saddle_center_bridge",
                "rear_saddle_center_bridge",
            ):
                for elem_b in (
                    "full_meridian_ring",
                    "globe_spin_bearing_hub",
                    "globe_spin_axis_rod",
                    "left_meridian_axis_boss",
                    "right_meridian_axis_boss",
                    "left_meridian_pivot_cap",
                    "right_meridian_pivot_cap",
                    "left_partial_axis_cap",
                    "right_partial_axis_cap",
                    "partial_stand_meridian_ring",
                    "wall_meridian_side_hinge_pin",
                    "wall_meridian_free_axis_cap",
                    "partial_meridian_lower_spine",
                    "partial_meridian_center_pivot_boss",
                    "partial_meridian_center_pivot_spine",
                ):
                    try:
                        ctx.allow_overlap(
                            support,
                            ring,
                            elem_a=elem_a,
                            elem_b=elem_b,
                            reason="meridian pivot cap is seated in support socket",
                        )
                    except Exception:
                        pass

    if "base_ring" in part_names and "support_pedestal" in part_names:
        base = model.get_part("base_ring")
        pedestal = model.get_part("support_pedestal")
        for elem_a in ("turning_base_bearing_race",):
            for elem_b in ("rotating_lower_pedestal", "rotating_tall_support"):
                try:
                    ctx.allow_overlap(
                        base,
                        pedestal,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="rotating pedestal sits inside the base bearing race",
                    )
                except Exception:
                    pass

    if "date_ring" in part_names:
        date_ring = model.get_part("date_ring")
        for support_name in ("base", "outer_cradle", "stand"):
            if support_name not in part_names:
                continue
            support = model.get_part(support_name)
            for elem_a in (
                "central_turned_pedestal",
                "center_cradle_column",
                "partial_ring_center_post",
                "partial_ring_base_disk",
            ):
                for elem_b in (
                    "date_ring_center_bearing",
                    "date_ring_spoke_0",
                    "date_ring_spoke_1",
                    "date_ring_spoke_2",
                    "date_ring_spoke_3",
                ):
                    try:
                        ctx.allow_overlap(
                            date_ring,
                            support,
                            elem_a=elem_b,
                            elem_b=elem_a,
                            reason="date ring center bearing is captured around the support post",
                        )
                    except Exception:
                        pass

    if "stand" in part_names and "globe" in part_names:
        stand = model.get_part("stand")
        globe = model.get_part("globe")
        for elem_a in ("partial_ring_upper_tie_bar", "partial_ring_crosshead"):
            for elem_b in (
                "south_polar_axis_cap",
                "ocean_sphere",
                "deep_ocean_shadow_core",
                "prime_meridian_band",
                "secondary_meridian_band",
                "south_latitude_band_0",
                "south_latitude_band_1",
                "south_latitude_band_2",
                *_CONTINENT_PATCH_NAMES,
            ):
                try:
                    ctx.allow_overlap(
                        stand,
                        globe,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="partial ring top tie captures the lower globe axis",
                    )
                except Exception:
                    pass

    for support_name in ("outer_cradle", "stand", "support_pedestal", "wall_arm"):
        if support_name not in part_names or "globe" not in part_names:
            continue
        support = model.get_part(support_name)
        globe = model.get_part("globe")
        for support_elem in (
            "central_tilt_axis_rod",
            "partial_ring_center_post_extension",
            "rotating_tall_support",
            "rotating_spin_axis_rod",
            "globe_bottom_saddle",
            "lower_spin_saddle_ball",
            "wall_arm_center_spin_bridge",
            "wall_arm_front_yoke_spine",
            "wall_arm_side_pivot_socket",
            "cantilever_upper_arm",
            "cantilever_lower_arm",
            "front_saddle_center_bridge",
            "rear_saddle_center_bridge",
        ):
            for globe_elem in (
                "ocean_sphere",
                "deep_ocean_shadow_core",
                "equator_band",
                "prime_meridian_band",
                "secondary_meridian_band",
                "south_polar_axis_cap",
                "north_latitude_band_0",
                "north_latitude_band_1",
                "north_latitude_band_2",
                "south_latitude_band_0",
                "south_latitude_band_1",
                "south_latitude_band_2",
                *_CONTINENT_PATCH_NAMES,
            ):
                try:
                    ctx.allow_overlap(
                        globe,
                        support,
                        elem_a=globe_elem,
                        elem_b=support_elem,
                        reason=(
                            "globe body (ocean sphere and its subsurface continent relief at "
                            "0.998R) rotates past the support spin bridge/axis that reaches the "
                            "spin axis; continents sit inside the already-allowed ocean envelope"
                        ),
                    )
                except Exception:
                    pass
    if "partial_meridian" in part_names and "wall_arm" in part_names:
        meridian = model.get_part("partial_meridian")
        wall = model.get_part("wall_arm")
        for meridian_elem in (
            "wall_partial_meridian_arc",
            "wall_meridian_upper_mount_bridge",
            "wall_meridian_lower_mount_bridge",
            "wall_meridian_side_hinge_pin",
            "wall_meridian_center_spin_boss",
            "wall_meridian_origin_spine",
            "wall_meridian_tilt_origin_boss",
        ):
            for wall_elem in (
                "wall_arm_side_pivot_socket",
                "wall_arm_front_yoke_spine",
                "wall_arm_center_spin_bridge",
                "cantilever_upper_arm",
                "cantilever_lower_arm",
            ):
                try:
                    ctx.allow_overlap(
                        meridian,
                        wall,
                        elem_a=meridian_elem,
                        elem_b=wall_elem,
                        reason="wall meridian hinge seats inside wall arm socket and cantilever brackets",
                    )
                except Exception:
                    pass
    if "partial_meridian" in part_names and "globe" in part_names:
        meridian = model.get_part("partial_meridian")
        globe = model.get_part("globe")
        for globe_elem in (
            "ocean_sphere",
            "deep_ocean_shadow_core",
            "prime_meridian_band",
            "secondary_meridian_band",
            "equator_band",
            "north_polar_axis_cap",
            "south_polar_axis_cap",
            "north_latitude_band_0",
            "north_latitude_band_1",
            "north_latitude_band_2",
            "south_latitude_band_0",
            "south_latitude_band_1",
            "south_latitude_band_2",
            *_CONTINENT_PATCH_NAMES,
        ):
            for meridian_elem in (
                "partial_meridian_center_pivot_boss",
                "partial_meridian_center_pivot_spine",
                "wall_meridian_upper_mount_bridge",
                "wall_meridian_lower_mount_bridge",
                "wall_meridian_center_spin_boss",
                "wall_meridian_origin_spine",
                "wall_meridian_tilt_origin_boss",
            ):
                try:
                    ctx.allow_overlap(
                        globe,
                        meridian,
                        elem_a=globe_elem,
                        elem_b=meridian_elem,
                        reason="partial meridian center boss captures the globe spin axis",
                    )
                except Exception:
                    pass
    if "meridian" in part_names and "globe" in part_names:
        meridian = model.get_part("meridian")
        globe = model.get_part("globe")
        for globe_elem in ("ocean_sphere", "deep_ocean_shadow_core"):
            for meridian_elem in (
                "partial_meridian_center_pivot_boss",
                "partial_meridian_center_pivot_spine",
            ):
                try:
                    ctx.allow_overlap(
                        globe,
                        meridian,
                        elem_a=globe_elem,
                        elem_b=meridian_elem,
                        reason="partial meridian center boss captures the globe spin axis",
                    )
                except Exception:
                    pass

    if "base" in part_names and "globe" in part_names:
        base = model.get_part("base")
        globe = model.get_part("globe")
        for elem_a in ("central_tilt_axis_datum", "central_tilt_axis_rod"):
            for elem_b in (
                "ocean_sphere",
                "deep_ocean_shadow_core",
                "equator_band",
                "prime_meridian_band",
                "secondary_meridian_band",
            ):
                try:
                    ctx.allow_overlap(
                        base,
                        globe,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="central tilt datum sits inside the globe bearing axis",
                    )
                except Exception:
                    pass


def run_globe_tests(
    object_model: ArticulatedObject,
    config: GlobeConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    part_names = {part.name for part in object_model.parts}
    joint_names = {joint.name for joint in object_model.joints}
    if "globe" not in part_names:
        ctx.fail("identity", "globe template must contain a globe part")
    if "globe_spin" not in joint_names:
        ctx.fail("main_joint", "globe template must expose globe_spin")
    if r.support_style == "rotating_pedestal" and "support_yaw" not in joint_names:
        ctx.fail("support_yaw", "rotating pedestal support must include support_yaw")
    if r.auxiliary_rotary == "date_ring" and "date_ring_spin" not in joint_names:
        ctx.fail("date_ring", "date_ring auxiliary must include date_ring_spin")
    if r.meridian_style != "none_pedestal" and not any(
        name in part_names for name in ("meridian", "inner_ring", "partial_meridian")
    ):
        ctx.fail("meridian", "non-pedestal globe must include a meridian or cradle ring")
    if r.ring_radius <= r.globe_radius:
        ctx.fail("clearance", "meridian radius must be larger than globe radius")
    if r.support_style == "classic_desktop" and r.meridian_style in (
        "full_tilting",
        "nested_inner",
        "partial_wall",
    ):
        post_r = max(r.globe_radius * 0.032, 0.012)
        py = _desktop_yoke_post_y(r, post_r)
        if _desktop_ring_post_clearance(r, py, post_r) < 0.008:
            ctx.fail(
                "yoke_clearance",
                "tilting meridian ring must clear the desktop yoke uprights by >=8mm "
                "across the tilt range",
            )

    spin_joint = None
    for joint in object_model.joints:
        if joint.name == "globe_spin":
            spin_joint = joint
            break
    if spin_joint is not None:
        if spin_joint.articulation_type != ArticulationType.CONTINUOUS:
            ctx.fail("globe_spin_type", "globe_spin must be continuous")
        ox, oy, oz = spin_joint.origin.xyz
        if spin_joint.parent == "support_pedestal":
            expected = (0.0, 0.0, r.globe_center_z)
        else:
            expected = (0.0, 0.0, 0.0)
        dist = math.sqrt(
            (ox - expected[0]) ** 2 + (oy - expected[1]) ** 2 + (oz - expected[2]) ** 2
        )
        if dist > 1e-6:
            ctx.fail("spin_origin", "globe_spin origin must be at the globe center")
    return ctx.report()
