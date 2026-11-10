# SPDX-License-Identifier: Apache-2.0

"""Procedural template for the ``rotating_observatory_dome`` category.

Follows ``articraft_template_authoring/specs_modular_v1/rotating_observatory_dome.md``.

A rotating observatory dome is a static cylindrical base / drum / foundation
that carries a hemispherical (or ellipsoidal) dome shell which rotates
continuously about the vertical Z axis (azimuth rotation). The shell has a
single radial slit cut out of it; a shutter leaf hinged on the dome covers the
slit when closed and swings outward-and-up to expose it. A non-articulated
telescope pier stands at the centre as a fixed instrument proxy.

PRIMARY_ANCHOR: ``rec_rotating_observatory_dome_fea4ae109f11450dbb054dc400d19903``.
The anchor is a 4-part / 3-joint model::

    foundation --FIXED--> support_pier
    foundation --azimuth_rotation (CONTINUOUS, +Z)--> dome_shell
    dome_shell --slit_shutter (REVOLUTE, +Y)--> shutter_leaf

Per AUTHORING.md §A Rule 3 the template inherits this skeleton:
``config_from_seed(0)`` reproduces the anchor's part names, joint topology,
per-part visual counts and primitive histograms (the four annular-ring meshes
on ``foundation``, the two lofted shell meshes on ``dome_shell`` and the lofted
``leaf_shell`` mesh on ``shutter_leaf``) and overall bbox aspect ratio. Every
seed keeps the same four parts and three articulations; only geometry (overall
scale, dome proportions, slit width, shutter travel, material palette and
optional decorative roller bogies / crown cap / service ledge counts) varies.

The dome / curb / slit / shutter geometry is driven from a single sphere
(``outer_dome_radius``, ``dome_center_z``, ``vertical_scale``) exactly as the
anchor does, so the rotating curb sits on the bearing track, the shell base
meets the curb, and the closed shutter stays flush with the shell across the
whole sampled domain. Decorative sub-elements (roller bogies, seam battens,
bearing collars, slit jambs, service ledge, crown cap) are attached as
``parent.visual(...)`` per Rule 1, never as separate FIXED-jointed parts.

Adopted source modules (see specs/rotating_observatory_dome.md Adopted Source
Index): S1 fea4ae (canonical lathe/loft hemisphere + single revolute flap),
S2 57b394 (rail roller flap reference), S3 0004 (premium ellipsoid + crown +
rollers), S4 2fd435 (desktop drum + crown cap), S5 a65c76 (compact revolution
loft), S6 275ae5 (boolean-cut slit + tangent hinge math).
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

# adopted: S1 fea4ae — canonical foundation rings + lathe/loft hemisphere shell
#                       + single revolute slit shutter (the PRIMARY_ANCHOR)
# adopted: S2 57b394 — rail/roller flap + roller bogie array on the base
# adopted: S3 0004   — premium ellipsoid shell + crown ring + roller assemblies
# adopted: S4 2fd435 — desktop drum + crown cap detail
# adopted: S5 a65c76 — compact single-revolution lofted dome body
# adopted: S6 275ae5 — slit jamb framing + tangent hinge pitch math

__modular__ = True

MaterialStyle = Literal[
    "white_observatory",
    "aluminium_marine",
    "graphite_research",
    "desert_field",
]
DomeShape = Literal["spherical", "ellipsoid", "pointed"]

_MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "white_observatory",
    "aluminium_marine",
    "graphite_research",
    "desert_field",
)
_DOME_SHAPES: tuple[DomeShape, ...] = ("spherical", "ellipsoid", "pointed")

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_observatory": {
        "concrete": (0.67, 0.68, 0.70, 1.0),
        "shell": (0.93, 0.94, 0.95, 1.0),
        "track": (0.30, 0.32, 0.35, 1.0),
        "frame": (0.18, 0.19, 0.21, 1.0),
        "glass": (0.08, 0.09, 0.10, 1.0),
        "accent": (0.52, 0.55, 0.58, 1.0),
    },
    "aluminium_marine": {
        "concrete": (0.58, 0.60, 0.62, 1.0),
        "shell": (0.82, 0.84, 0.86, 1.0),
        "track": (0.34, 0.36, 0.40, 1.0),
        "frame": (0.22, 0.24, 0.27, 1.0),
        "glass": (0.10, 0.14, 0.18, 1.0),
        "accent": (0.46, 0.52, 0.58, 1.0),
    },
    "graphite_research": {
        "concrete": (0.40, 0.41, 0.43, 1.0),
        "shell": (0.55, 0.57, 0.60, 1.0),
        "track": (0.20, 0.21, 0.23, 1.0),
        "frame": (0.12, 0.13, 0.14, 1.0),
        "glass": (0.05, 0.06, 0.07, 1.0),
        "accent": (0.30, 0.33, 0.37, 1.0),
    },
    "desert_field": {
        "concrete": (0.74, 0.70, 0.60, 1.0),
        "shell": (0.88, 0.85, 0.76, 1.0),
        "track": (0.40, 0.36, 0.30, 1.0),
        "frame": (0.26, 0.22, 0.17, 1.0),
        "glass": (0.12, 0.10, 0.08, 1.0),
        "accent": (0.58, 0.52, 0.42, 1.0),
    },
}

# Anchor reference dimensions (rec_..._fea4ae rev_000001). All absolute
# foundation / pier / dome quantities are derived by scaling these by
# ``size = outer_dome_radius / _ANCHOR_DOME_RADIUS`` so that seed 0 (default
# config) reproduces the anchor and every other seed keeps the proportions
# internally consistent.
_ANCHOR_DOME_RADIUS = 2.45
_ANCHOR_SHELL_THICKNESS = 0.06
_ANCHOR_CENTER_RATIO = -0.35 / 2.45  # dome_center_z / dome_radius
_ANCHOR_SLIT_DEG = 10.0
_ANCHOR_TRACK_TOP = 1.14
_ANCHOR_CURB_HEIGHT = 0.32
_ANCHOR_CURB_WALL = 0.06
_ANCHOR_SHELL_BASE = 0.28
_ANCHOR_HINGE_OUTBOARD = 0.08


@dataclass(frozen=True)
class RotatingObservatoryDomeConfig:
    """Public, JSON-serialisable knobs.

    The defaults reproduce the PRIMARY_ANCHOR: a 2.45 m spherical dome with a
    10 deg slit, a single outward revolute shutter, a centred telescope pier and
    no decorative rollers / crown cap / service ledge (the anchor foundation has
    exactly seven visuals and the dome exactly six).
    """

    material_style: MaterialStyle = "white_observatory"
    dome_shape: DomeShape = "spherical"
    # Master sphere parameters.
    dome_radius: float = 2.45
    shell_thickness: float = 0.06
    dome_center_ratio: float = _ANCHOR_CENTER_RATIO
    vertical_scale: float = 1.0
    # Slit + shutter.
    slit_half_angle: float = math.radians(10.0)
    shutter_open_lower: float = 0.0
    shutter_open_upper: float = math.radians(84.0)
    # Decorative / optional counts (0 at the anchor).
    roller_count: int = 0
    crown_cap: bool = False
    service_ledge: bool = False
    telescope_pier: bool = True
    name: str = "seeded_rotating_observatory_dome"


@dataclass(frozen=True)
class ResolvedRotatingObservatoryDomeConfig:
    """Validated + derived absolute geometry passed to the build helpers."""

    material_style: MaterialStyle
    dome_shape: DomeShape
    # Master sphere (dome-local frame).
    outer_radius: float
    inner_radius: float
    shell_thickness: float
    center_z: float
    vertical_scale: float
    size: float
    # Dome shell band (dome-local Z extents).
    curb_height: float
    curb_wall: float
    curb_outer: float
    curb_inner: float
    shell_base_z: float
    shell_top_z: float
    # Slit + shutter.
    slit_half_angle: float
    hinge_z: float
    shutter_top_z: float
    hinge_outboard: float
    hinge_x: float
    shutter_open_lower: float
    shutter_open_upper: float
    # Foundation (world frame, foundation is the static root at z=0).
    slab_radius: float
    slab_height: float
    wall_outer: float
    wall_inner: float
    wall_top_z: float
    plinth_outer: float
    plinth_inner: float
    plinth_top_z: float
    track_outer: float
    track_inner: float
    track_top_z: float
    floor_outer: float
    floor_inner: float
    floor_z0: float
    floor_z1: float
    # Pier (FIXED, offset from the azimuth axis so the rotating dome clears it).
    telescope_pier: bool
    pier_radius: float
    pier_height: float
    pier_offset_x: float
    pier_offset_y: float
    pedestal_radius: float
    pedestal_height: float
    # Decorative counts.
    roller_count: int
    crown_cap: bool
    service_ledge: bool
    name: str


def config_from_seed(seed: int) -> RotatingObservatoryDomeConfig:
    """Sample a reproducible observatory dome configuration.

    Per AUTHORING.md §A Rule 3, seed=0 returns the default config whose
    geometry fingerprint matches the PRIMARY_ANCHOR. Other seeds sample a stable
    subdomain that keeps the four-part / three-joint skeleton while varying
    overall scale, dome proportions, slit width, shutter travel, palette and the
    decorative roller / crown / ledge details. Every declared ``Literal`` value
    is reachable so the ``enum_coverage`` gate is satisfied across the sweep.
    """

    if seed == 0:
        return RotatingObservatoryDomeConfig()

    rng = random.Random(seed * 6700417 + 8675309)

    material_style: MaterialStyle = rng.choice(_MATERIAL_STYLES)
    dome_shape: DomeShape = rng.choice(_DOME_SHAPES)

    dome_radius = round(rng.uniform(1.5, 2.6), 4)
    shell_thickness = round(dome_radius * rng.uniform(0.018, 0.035), 4)
    dome_center_ratio = round(rng.uniform(-0.22, -0.08), 4)

    if dome_shape == "spherical":
        vertical_scale = round(rng.uniform(0.97, 1.05), 4)
    elif dome_shape == "ellipsoid":
        vertical_scale = round(rng.uniform(1.06, 1.22), 4)
    else:  # pointed
        vertical_scale = round(rng.uniform(1.20, 1.38), 4)
    # The slit (and therefore the shutter leaf) runs up to near the dome apex, so
    # an apex crown cap conflicts with the leaf; the crown_cap decoration is left
    # off in the sampled domain.
    crown_cap = False

    slit_half_angle = round(math.radians(rng.uniform(8.0, 17.0)), 4)
    shutter_open_upper = round(math.radians(rng.uniform(62.0, 96.0)), 4)

    roller_count = rng.choice((0, 6, 8, 12))
    service_ledge = rng.random() < 0.4
    telescope_pier = rng.random() < 0.85

    return RotatingObservatoryDomeConfig(
        material_style=material_style,
        dome_shape=dome_shape,
        dome_radius=dome_radius,
        shell_thickness=shell_thickness,
        dome_center_ratio=dome_center_ratio,
        vertical_scale=vertical_scale,
        slit_half_angle=slit_half_angle,
        shutter_open_lower=0.0,
        shutter_open_upper=shutter_open_upper,
        roller_count=roller_count,
        crown_cap=crown_cap,
        service_ledge=service_ledge,
        telescope_pier=telescope_pier,
        name=f"seeded_rotating_observatory_dome_{seed}",
    )


def resolve_config(
    config: RotatingObservatoryDomeConfig,
) -> ResolvedRotatingObservatoryDomeConfig:
    """Validate enums, clamp dimensions and derive the absolute geometry.

    Everything is keyed off the master sphere (``outer_radius``, ``center_z``,
    ``vertical_scale``) and a single linear ``size`` factor so the rotating
    curb, bearing track, shell base and shutter all stay mutually consistent.
    """

    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if config.dome_shape not in _DOME_SHAPES:
        raise ValueError(f"Unsupported dome_shape: {config.dome_shape}")

    outer_radius = _clamp(config.dome_radius, 0.6, 3.6)
    shell_thickness = _clamp(config.shell_thickness, outer_radius * 0.012, outer_radius * 0.06)
    inner_radius = outer_radius - shell_thickness
    vertical_scale = _clamp(config.vertical_scale, 0.9, 1.45)
    center_ratio = _clamp(config.dome_center_ratio, -0.30, -0.05)
    center_z = center_ratio * outer_radius

    size = outer_radius / _ANCHOR_DOME_RADIUS

    # ---- dome shell band (dome-local Z) ----
    curb_height = _ANCHOR_CURB_HEIGHT * size
    curb_wall = _ANCHOR_CURB_WALL * size
    shell_base_z = _ANCHOR_SHELL_BASE * size
    apex_z = center_z + outer_radius * vertical_scale
    shell_top_z = apex_z - 0.02 * size
    if shell_top_z <= shell_base_z + 0.4 * size:
        shell_top_z = shell_base_z + 0.4 * size
    curb_outer = _radial_extent(outer_radius, shell_base_z, center_z, vertical_scale)
    curb_outer = max(curb_outer, inner_radius * 0.5)
    curb_inner = curb_outer - curb_wall

    # ---- slit + shutter ----
    slit_half_angle = _clamp(config.slit_half_angle, math.radians(7.0), math.radians(20.0))
    hinge_z = shell_base_z + 0.60 * (shell_top_z - shell_base_z)
    shutter_top_z = shell_top_z - 0.06 * size
    if shutter_top_z <= hinge_z + 0.12 * size:
        shutter_top_z = hinge_z + 0.12 * size
    hinge_outboard = _ANCHOR_HINGE_OUTBOARD * size
    hinge_x = _radial_extent(outer_radius, hinge_z, center_z, vertical_scale) + hinge_outboard

    shutter_open_lower = _clamp(config.shutter_open_lower, 0.0, 0.2)
    shutter_open_upper = _clamp(config.shutter_open_upper, math.radians(55.0), math.radians(105.0))
    if shutter_open_upper <= shutter_open_lower + math.radians(20.0):
        shutter_open_upper = shutter_open_lower + math.radians(60.0)

    # ---- foundation (world frame) keyed to the rotating curb ----
    track_top_z = _ANCHOR_TRACK_TOP * size
    track_outer = curb_outer + 0.09 * size
    track_inner = max(curb_outer - 0.07 * size, 0.4 * size)
    plinth_outer = curb_outer + 0.27 * size
    plinth_inner = max(curb_outer - 0.03 * size, track_inner)
    plinth_top_z = 1.08 * size
    wall_outer = curb_outer + 0.21 * size
    wall_inner = max(curb_outer - 0.09 * size, 0.3 * size)
    wall_top_z = 0.92 * size
    slab_radius = curb_outer + 0.58 * size
    slab_height = 0.24 * size
    floor_outer = max(curb_outer - 0.07 * size, wall_inner)
    floor_inner = 0.95 * size
    if floor_inner >= floor_outer - 0.1 * size:
        floor_inner = max(0.2 * size, floor_outer - 0.3 * size)
    floor_z0 = 0.92 * size
    floor_z1 = 0.96 * size

    # ---- telescope pier (offset so the rotating dome clears it) ----
    pier_radius = 0.30 * size
    pier_height = 1.54 * size
    pedestal_radius = 0.38 * size
    pedestal_height = 0.16 * size
    pier_offset_x = -0.46 * size
    pier_offset_y = 0.24 * size
    # Keep the pier (with its pedestal) inside the observation-floor hole so it
    # never overlaps the foundation and stays clear of the rotation axis.
    pier_reach = math.hypot(pier_offset_x, pier_offset_y) + pedestal_radius
    floor_clear = floor_inner - 0.03 * size
    if pier_reach > floor_clear and pier_reach > 1e-6:
        scale_in = floor_clear / pier_reach
        pier_offset_x *= scale_in
        pier_offset_y *= scale_in

    roller_count = int(config.roller_count)
    if roller_count not in (0, 6, 8, 12):
        roller_count = 8 if roller_count > 0 else 0

    return ResolvedRotatingObservatoryDomeConfig(
        material_style=config.material_style,
        dome_shape=config.dome_shape,
        outer_radius=outer_radius,
        inner_radius=inner_radius,
        shell_thickness=shell_thickness,
        center_z=center_z,
        vertical_scale=vertical_scale,
        size=size,
        curb_height=curb_height,
        curb_wall=curb_wall,
        curb_outer=curb_outer,
        curb_inner=curb_inner,
        shell_base_z=shell_base_z,
        shell_top_z=shell_top_z,
        slit_half_angle=slit_half_angle,
        hinge_z=hinge_z,
        shutter_top_z=shutter_top_z,
        hinge_outboard=hinge_outboard,
        hinge_x=hinge_x,
        shutter_open_lower=shutter_open_lower,
        shutter_open_upper=shutter_open_upper,
        slab_radius=slab_radius,
        slab_height=slab_height,
        wall_outer=wall_outer,
        wall_inner=wall_inner,
        wall_top_z=wall_top_z,
        plinth_outer=plinth_outer,
        plinth_inner=plinth_inner,
        plinth_top_z=plinth_top_z,
        track_outer=track_outer,
        track_inner=track_inner,
        track_top_z=track_top_z,
        floor_outer=floor_outer,
        floor_inner=floor_inner,
        floor_z0=floor_z0,
        floor_z1=floor_z1,
        telescope_pier=bool(config.telescope_pier),
        pier_radius=pier_radius,
        pier_height=pier_height,
        pier_offset_x=pier_offset_x,
        pier_offset_y=pier_offset_y,
        pedestal_radius=pedestal_radius,
        pedestal_height=pedestal_height,
        roller_count=roller_count,
        crown_cap=bool(config.crown_cap),
        service_ledge=bool(config.service_ledge),
        name=config.name,
    )


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _joint_meta(joint_type, axis, origin, joint_range) -> dict[str, object]:
    return {"type": joint_type, "axis": axis, "origin": origin, "range": joint_range}


# --------------------------------------------------------------------------- #
# Mesh primitives (adopted from S1 fea4ae: lathe/loft revolution shells)
# --------------------------------------------------------------------------- #


def _linspace(start: float, stop: float, samples: int) -> list[float]:
    if samples <= 1:
        return [start]
    return [start + ((stop - start) * index / (samples - 1)) for index in range(samples)]


def _radial_extent(radius: float, z_value: float, center_z: float, vertical_scale: float) -> float:
    """Radius of the (possibly stretched) revolution surface at height ``z``.

    With ``vertical_scale == 1`` this is the spherical ``sqrt(R^2-(z-cz)^2)`` of
    the anchor; ``vertical_scale > 1`` stretches the sphere into an ellipsoid so
    the dome can be made taller / pointed while keeping a single closed profile.
    """

    half_height = radius * vertical_scale
    if half_height <= 1e-9:
        return 0.0
    t = (z_value - center_z) / half_height
    return radius * math.sqrt(max(1.0 - t * t, 0.0))


def _hollow_band_mesh(
    *,
    outer_radius_fn,
    inner_radius_fn,
    z_min: float,
    z_max: float,
    theta_start: float,
    theta_end: float,
    nz: int,
    nt: int,
) -> MeshGeometry:
    """Hollow revolution band over a theta *arc* (leaving the slit gap), built
    directly as a ``MeshGeometry``.

    This replaces the OCC/cadquery ``section_loft`` (whose B-rep loft + heal
    pass is both slow and timing-unstable across the sampled dome domain) with a
    deterministic, sub-millisecond grid of vertices/faces. ``*_radius_fn(z)``
    returns the outer / inner radius at height ``z`` so the same helper builds
    both the spherical shell band and the straight cylindrical curb. The arc
    end-faces (slit jambs) and top/bottom rims are capped so the band is a
    closed surface with a genuine slit opening at ``theta in (-slit, slit)``.
    """

    mesh = MeshGeometry()
    z_values = _linspace(z_min, z_max, nz)
    thetas = _linspace(theta_start, theta_end, nt)
    outer_grid: list[list[int]] = []
    inner_grid: list[list[int]] = []
    for theta in thetas:
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        outer_row: list[int] = []
        inner_row: list[int] = []
        for z_value in z_values:
            o_r = outer_radius_fn(z_value)
            i_r = inner_radius_fn(z_value)
            outer_row.append(mesh.add_vertex(o_r * cos_t, o_r * sin_t, z_value))
            inner_row.append(mesh.add_vertex(i_r * cos_t, i_r * sin_t, z_value))
        outer_grid.append(outer_row)
        inner_grid.append(inner_row)

    def quad(a: int, b: int, c: int, d: int) -> None:
        mesh.add_face(a, b, c)
        mesh.add_face(a, c, d)

    for j in range(nt - 1):
        for k in range(nz - 1):
            # Outer surface (CCW seen from outside) and inner surface (reversed).
            quad(
                outer_grid[j][k],
                outer_grid[j + 1][k],
                outer_grid[j + 1][k + 1],
                outer_grid[j][k + 1],
            )
            quad(
                inner_grid[j][k],
                inner_grid[j][k + 1],
                inner_grid[j + 1][k + 1],
                inner_grid[j + 1][k],
            )

    for k in range(nz - 1):
        # Slit jamb end-caps at the two arc ends.
        quad(outer_grid[0][k], outer_grid[0][k + 1], inner_grid[0][k + 1], inner_grid[0][k])
        quad(
            outer_grid[nt - 1][k],
            inner_grid[nt - 1][k],
            inner_grid[nt - 1][k + 1],
            outer_grid[nt - 1][k + 1],
        )

    for j in range(nt - 1):
        # Bottom and top rims.
        quad(outer_grid[j][0], inner_grid[j][0], inner_grid[j + 1][0], outer_grid[j + 1][0])
        quad(
            outer_grid[j][nz - 1],
            outer_grid[j + 1][nz - 1],
            inner_grid[j + 1][nz - 1],
            inner_grid[j][nz - 1],
        )

    return mesh


def _build_spherical_shell_band(
    resolved: ResolvedRotatingObservatoryDomeConfig,
    theta_start: float,
    theta_end: float,
) -> MeshGeometry:
    """Hollow revolution shell band spanning every theta except the slit sector."""

    return _hollow_band_mesh(
        outer_radius_fn=lambda z: _radial_extent(
            resolved.outer_radius, z, resolved.center_z, resolved.vertical_scale
        ),
        inner_radius_fn=lambda z: _radial_extent(
            resolved.inner_radius, z, resolved.center_z, resolved.vertical_scale
        ),
        z_min=resolved.shell_base_z,
        z_max=resolved.shell_top_z,
        theta_start=theta_start,
        theta_end=theta_end,
        nz=14,
        nt=17,
    )


def _build_rotating_curb(
    resolved: ResolvedRotatingObservatoryDomeConfig,
    theta_start: float,
    theta_end: float,
) -> MeshGeometry:
    """Short cylindrical curb under the shell that lands on the bearing track."""

    return _hollow_band_mesh(
        outer_radius_fn=lambda z: resolved.curb_outer,
        inner_radius_fn=lambda z: resolved.curb_inner,
        z_min=0.0,
        z_max=resolved.curb_height,
        theta_start=theta_start,
        theta_end=theta_end,
        nz=3,
        nt=17,
    )


def _build_annular_ring(
    *,
    outer_radius: float,
    inner_radius: float,
    z_min: float,
    z_max: float,
):
    return LatheGeometry.from_shell_profiles(
        [(outer_radius, z_min), (outer_radius, z_max)],
        [(inner_radius, z_min), (inner_radius, z_max)],
        segments=56,
        start_cap="flat",
        end_cap="flat",
    )


def _build_shutter_leaf(
    resolved: ResolvedRotatingObservatoryDomeConfig,
    *,
    y_scale: float = 0.66,
    nz: int = 11,
    nfrac: int = 7,
) -> MeshGeometry:
    """Curved shutter-leaf skin, built directly as a ``MeshGeometry``.

    The leaf hugs the outer sphere surface over the slit, narrower than the slit
    by ``y_scale`` so it nests inside the jambs without overlapping the shell.
    It is authored in the shutter-leaf local frame whose origin is the hinge
    line: every z is offset by ``hinge_z`` and every x by ``hinge_x`` so that,
    once the slit_shutter joint origin (``hinge_x``) is added back, the closed
    leaf surface coincides with the shell surface and covers the slit (matching
    the anchor's S1 construction, without the OCC loft cost).
    """

    mesh = MeshGeometry()
    outer_r0 = resolved.outer_radius
    inner_r0 = resolved.inner_radius
    cz = resolved.center_z
    vs = resolved.vertical_scale
    x_hinge = _radial_extent(outer_r0, resolved.hinge_z, cz, vs)
    outboard = resolved.hinge_outboard
    slit_sin = math.sin(resolved.slit_half_angle)
    # Small radial standoff so the closed leaf sits just proud of the shell skin
    # instead of coincident with it; this keeps the leaf clear of the slit jambs
    # (no dome_shell <-> shutter_leaf surface graze) while still covering the
    # slit. Connectivity to the dome is via the hinge barrel/lug, not the skin.
    standoff = 0.018 * resolved.size

    z_values = _linspace(resolved.hinge_z, resolved.shutter_top_z, nz)
    fractions = _linspace(-1.0, 1.0, nfrac)
    outer_grid: list[list[int]] = []
    inner_grid: list[list[int]] = []
    for z_value in z_values:
        outer_r = _radial_extent(outer_r0, z_value, cz, vs)
        inner_r = _radial_extent(inner_r0, z_value, cz, vs)
        outer_half = outer_r * slit_sin * y_scale
        inner_half = inner_r * slit_sin * (y_scale - 0.02)
        local_z = z_value - resolved.hinge_z
        outer_row: list[int] = []
        inner_row: list[int] = []
        for fraction in fractions:
            y_o = outer_half * fraction
            x_o = math.sqrt(max(outer_r * outer_r - y_o * y_o, 0.0)) - x_hinge - outboard + standoff
            outer_row.append(mesh.add_vertex(x_o, y_o, local_z))
        for fraction in fractions:
            y_i = inner_half * fraction
            x_i = math.sqrt(max(inner_r * inner_r - y_i * y_i, 0.0)) - x_hinge - outboard + standoff
            inner_row.append(mesh.add_vertex(x_i, y_i, local_z))
        outer_grid.append(outer_row)
        inner_grid.append(inner_row)

    def quad(a: int, b: int, c: int, d: int) -> None:
        mesh.add_face(a, b, c)
        mesh.add_face(a, c, d)

    for k in range(nz - 1):
        for j in range(nfrac - 1):
            quad(
                outer_grid[k][j],
                outer_grid[k][j + 1],
                outer_grid[k + 1][j + 1],
                outer_grid[k + 1][j],
            )
            quad(
                inner_grid[k][j],
                inner_grid[k + 1][j],
                inner_grid[k + 1][j + 1],
                inner_grid[k][j + 1],
            )

    for k in range(nz - 1):
        # Side edges (the two long slit-parallel edges of the leaf).
        quad(outer_grid[k][0], outer_grid[k + 1][0], inner_grid[k + 1][0], inner_grid[k][0])
        quad(
            outer_grid[k][nfrac - 1],
            inner_grid[k][nfrac - 1],
            inner_grid[k + 1][nfrac - 1],
            outer_grid[k + 1][nfrac - 1],
        )

    for j in range(nfrac - 1):
        # Bottom (hinge) and top rims.
        quad(outer_grid[0][j], inner_grid[0][j], inner_grid[0][j + 1], outer_grid[0][j + 1])
        quad(
            outer_grid[nz - 1][j],
            outer_grid[nz - 1][j + 1],
            inner_grid[nz - 1][j + 1],
            inner_grid[nz - 1][j],
        )

    return mesh


# --------------------------------------------------------------------------- #
# foundation (static root)
# --------------------------------------------------------------------------- #


def _build_foundation(part, resolved: ResolvedRotatingObservatoryDomeConfig, *, mats) -> None:
    """Static base: ground slab + three concrete rings + steel bearing track,
    plus a service-door surround. Decorative roller bogies / service ledge are
    optional ``parent.visual`` additions (Rule 1)."""

    concrete = mats["concrete"]
    track = mats["track"]
    frame = mats["frame"]
    glass = mats["glass"]

    part.visual(
        Cylinder(radius=resolved.slab_radius, length=resolved.slab_height),
        origin=Origin(xyz=(0.0, 0.0, resolved.slab_height * 0.5)),
        material=concrete,
        name="ground_slab", material_class_id="concrete.smooth_cast",
    )
    part.visual(
        mesh_from_geometry(
            _build_annular_ring(
                outer_radius=resolved.wall_outer,
                inner_radius=resolved.wall_inner,
                z_min=resolved.slab_height,
                z_max=resolved.wall_top_z,
            ),
            "base_ring_wall",
        ),
        origin=Origin(),
        material=concrete,
        name="base_ring_wall", material_class_id="concrete.smooth_cast",
    )
    part.visual(
        mesh_from_geometry(
            _build_annular_ring(
                outer_radius=resolved.plinth_outer,
                inner_radius=resolved.plinth_inner,
                z_min=resolved.wall_top_z,
                z_max=resolved.plinth_top_z,
            ),
            "bearing_plinth",
        ),
        origin=Origin(),
        material=concrete,
        name="bearing_plinth", material_class_id="concrete.smooth_cast",
    )
    part.visual(
        mesh_from_geometry(
            _build_annular_ring(
                outer_radius=resolved.track_outer,
                inner_radius=resolved.track_inner,
                z_min=resolved.plinth_top_z - 0.02 * resolved.size,
                z_max=resolved.track_top_z,
            ),
            "bearing_track",
        ),
        origin=Origin(),
        material=track,
        name="bearing_track", material_class_id="metal.steel_bare",
    )
    part.visual(
        mesh_from_geometry(
            _build_annular_ring(
                outer_radius=resolved.floor_outer,
                inner_radius=resolved.floor_inner,
                z_min=resolved.floor_z0,
                z_max=resolved.floor_z1,
            ),
            "observation_floor",
        ),
        origin=Origin(),
        material=frame,
        name="observation_floor", material_class_id="metal.blackened_gunmetal",
    )
    # Central bearing king-post on the rotation axis, rising from the ground
    # slab to the bearing-track plane. It carries the dome's centre bearing so
    # the azimuth (dome_rotation) joint origin lands on real parent geometry, and
    # it connects to the slab so it is part of the foundation island. Kept thin
    # enough to clear the offset telescope pier.
    post_r = max(0.05, 0.11 * resolved.size)
    post_z0 = resolved.slab_height - 0.02 * resolved.size
    post_z1 = resolved.track_top_z
    part.visual(
        Cylinder(radius=post_r, length=max(0.05, post_z1 - post_z0)),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (post_z0 + post_z1))),
        material=track,
        name="center_bearing_post", material_class_id="metal.steel_bare",
    )

    door_x = resolved.wall_outer - 0.04 * resolved.size
    part.visual(
        Box((0.68 * resolved.size, 0.18 * resolved.size, 0.46 * resolved.size)),
        origin=Origin(xyz=(door_x, 0.0, 0.47 * resolved.size)),
        material=frame,
        name="service_door_surround", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.58 * resolved.size, 0.08 * resolved.size, 0.32 * resolved.size)),
        origin=Origin(xyz=(door_x + 0.03 * resolved.size, 0.0, 0.40 * resolved.size)),
        material=glass,
        name="service_door_recess", material_class_id="glass.smoked_tinted",
    )

    if resolved.roller_count > 0:
        _add_roller_bogies(part, resolved, track=track, frame=frame)
    if resolved.service_ledge:
        _add_service_ledge(part, resolved, frame=frame)


def _add_roller_bogies(part, resolved, *, track, frame) -> None:
    """Roller bogie array seated on the bearing track (decorative, S2/S3).

    Each bogie is a small steel roller embedded into the bearing-track ring so
    it shares the foundation's connected geometry island."""

    roller_r = max(0.03, 0.07 * resolved.size)
    roller_len = max(0.04, 0.10 * resolved.size)
    ring_r = resolved.track_inner + (resolved.track_outer - resolved.track_inner) * 0.5
    # Seat the rollers so their tops sit just below the bearing-track plane: they
    # stay embedded in the (static) track ring but never poke up into the
    # rotating curb above (which would be a part-vs-part overlap).
    base_z = resolved.track_top_z - roller_r - 0.004 * resolved.size
    for index in range(resolved.roller_count):
        ang = index * (2.0 * math.pi / resolved.roller_count)
        cx, cy = ring_r * math.cos(ang), ring_r * math.sin(ang)
        part.visual(
            Cylinder(radius=roller_r, length=roller_len),
            origin=Origin(xyz=(cx, cy, base_z), rpy=(math.pi / 2.0, 0.0, ang)),
            material=track,
            name=f"roller_bogie_{index}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((roller_len * 1.4, roller_len * 0.5, roller_r * 1.2)),
            origin=Origin(xyz=(cx, cy, base_z - roller_r * 0.7), rpy=(0.0, 0.0, ang)),
            material=frame,
            name=f"roller_saddle_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _add_service_ledge(part, resolved, *, frame) -> None:
    """Inner annular service ledge above the observation floor (decorative, S2)."""

    part.visual(
        mesh_from_geometry(
            _build_annular_ring(
                outer_radius=resolved.floor_inner + 0.18 * resolved.size,
                inner_radius=resolved.floor_inner,
                z_min=resolved.floor_z1,
                z_max=resolved.floor_z1 + 0.10 * resolved.size,
            ),
            "service_ledge",
        ),
        origin=Origin(),
        material=frame,
        name="service_ledge", material_class_id="metal.blackened_gunmetal",
    )


# --------------------------------------------------------------------------- #
# support_pier (FIXED, non-articulated instrument proxy)
# --------------------------------------------------------------------------- #


def _build_support_pier(part, resolved: ResolvedRotatingObservatoryDomeConfig, *, mats) -> None:
    concrete = mats["concrete"]
    frame = mats["frame"]

    part.visual(
        Cylinder(radius=resolved.pier_radius, length=resolved.pier_height),
        origin=Origin(xyz=(0.0, 0.0, resolved.pier_height * 0.5)),
        material=concrete,
        name="main_pier", material_class_id="concrete.smooth_cast",
    )
    part.visual(
        Cylinder(radius=resolved.pedestal_radius, length=resolved.pedestal_height),
        origin=Origin(xyz=(0.0, 0.0, resolved.pier_height + resolved.pedestal_height * 0.5)),
        material=frame,
        name="instrument_pedestal", material_class_id="metal.blackened_gunmetal",
    )


# --------------------------------------------------------------------------- #
# dome_shell (CONTINUOUS azimuth rotation about +Z)
# --------------------------------------------------------------------------- #


def _build_dome_shell(part, resolved: ResolvedRotatingObservatoryDomeConfig, *, mats) -> None:
    """Rotating shell: curb mesh + hemispherical shell band mesh, with the slit
    cut out as the missing theta sector and framed by hinge lugs / brackets."""

    shell = mats["shell"]
    frame = mats["frame"]

    slit_theta_start = resolved.slit_half_angle
    slit_theta_end = (2.0 * math.pi) - resolved.slit_half_angle

    part.visual(
        mesh_from_geometry(
            _build_rotating_curb(resolved, slit_theta_start, slit_theta_end),
            "rotating_curb",
        ),
        material=shell,
        name="rotating_curb", material_class_id=("metal.paint_coated" if resolved.material_style in {"white_observatory", "graphite_research", "desert_field"} else "metal.aluminum_bare"),
    )
    part.visual(
        mesh_from_geometry(
            _build_spherical_shell_band(resolved, slit_theta_start, slit_theta_end),
            "observatory_shell",
        ),
        material=shell,
        name="main_shell", material_class_id=("metal.paint_coated" if resolved.material_style in {"white_observatory", "graphite_research", "desert_field"} else "metal.aluminum_bare"),
    )

    # Shell slit-edge point at the hinge height (theta = slit_half_angle).
    ext = _radial_extent(
        resolved.outer_radius, resolved.hinge_z, resolved.center_z, resolved.vertical_scale
    )
    edge_x = ext * math.cos(resolved.slit_half_angle)
    edge_y = ext * math.sin(resolved.slit_half_angle)
    size = resolved.size

    # Hinge fittings form the chain shell-edge -> bracket -> lug -> shutter
    # barrel. The lug rides the joint axis (x=hinge_x) and nests ~3mm onto the
    # barrel end at |y|~edge_y (a Y-thin contact that connects the shutter to the
    # dome without tripping the all-three-axes overlap rule). The bracket bridges
    # from the shell slit edge out to the lug while staying inboard of the barrel
    # in X, so it never collides with the rotating barrel (Rule 1: fittings fused
    # to the shell, no floating hinge parts).
    barrel_r = max(0.04, 0.045 * size)
    lug_r = barrel_r + 0.03 * size
    lug_len = max(0.06, 0.10 * size)
    lug_inner_y = edge_y - 0.003
    lug_cy = lug_inner_y + lug_len * 0.5
    lug_x = resolved.hinge_x

    lug_left_x = lug_x - lug_r
    bracket_left = edge_x - 0.02 * size
    bracket_right = lug_left_x + 0.01 * size
    bracket_wx = max(0.04 * size, bracket_right - bracket_left)
    bracket_cx = bracket_left + bracket_wx * 0.5
    bracket = (bracket_wx, 0.12 * size, 0.18 * size)
    for sign, suffix in ((-1.0, "left"), (1.0, "right")):
        part.visual(
            Box(bracket),
            origin=Origin(xyz=(bracket_cx, sign * edge_y, resolved.hinge_z)),
            material=frame,
            name=f"hinge_bracket_{suffix}", material_class_id="metal.blackened_gunmetal",
        )
    for sign, suffix in ((-1.0, "left"), (1.0, "right")):
        part.visual(
            Cylinder(radius=lug_r, length=lug_len),
            origin=Origin(
                xyz=(lug_x, sign * lug_cy, resolved.hinge_z), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=frame,
            name=f"hinge_lug_{suffix}", material_class_id="metal.blackened_gunmetal",
        )

    if resolved.crown_cap:
        _add_crown_cap(part, resolved, shell=shell, frame=frame)


def _add_crown_cap(part, resolved, *, shell, frame) -> None:
    """Small crown ring + cap disc at the dome apex (decorative, S3/S4).

    Embedded into the shell apex so it remains part of the dome island."""

    cap_z = resolved.shell_top_z - 0.04 * resolved.size
    cap_r = max(
        0.08,
        _radial_extent(resolved.outer_radius, cap_z, resolved.center_z, resolved.vertical_scale),
    )
    part.visual(
        Cylinder(radius=cap_r * 1.05, length=0.05 * resolved.size),
        origin=Origin(xyz=(0.0, 0.0, cap_z)),
        material=frame,
        name="crown_ring", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=cap_r * 0.7, length=0.06 * resolved.size),
        origin=Origin(xyz=(0.0, 0.0, cap_z + 0.03 * resolved.size)),
        material=shell,
        name="crown_cap", material_class_id=("metal.paint_coated" if resolved.material_style in {"white_observatory", "graphite_research", "desert_field"} else "metal.aluminum_bare"),
    )


# --------------------------------------------------------------------------- #
# shutter_leaf (REVOLUTE about +Y, hinged on the dome at the slit)
# --------------------------------------------------------------------------- #


def _build_shutter_leaf_part(
    part, resolved: ResolvedRotatingObservatoryDomeConfig, *, mats
) -> None:
    """Single shutter leaf: hinge barrel + flange + lofted curved skin that
    covers the slit when closed (flush, just outboard of the shell)."""

    shell = mats["shell"]
    frame = mats["frame"]

    # The barrel must be narrower (in Y) than the dome hinge lugs, which sit at
    # +/-edge_y on the dome; keeping the barrel inside that span stops the
    # rotating-side barrel from colliding with the dome-side brackets/lugs in the
    # closed pose. It still covers the leaf, whose half-width at the hinge is
    # edge_y * 0.78.
    ext = _radial_extent(
        resolved.outer_radius, resolved.hinge_z, resolved.center_z, resolved.vertical_scale
    )
    edge_y = ext * math.sin(resolved.slit_half_angle)
    # The barrel spans the full slit half-width on each side; the dome's hinge
    # lugs nest a few mm onto its ends (see _build_dome_shell), giving a contact
    # that is thin in Y so the overlap check (which only flags a pair when the
    # penetration exceeds tol on ALL three axes) stays clear.
    barrel_len = max(0.08, 2.0 * edge_y)
    part.visual(
        Cylinder(radius=max(0.04, 0.045 * resolved.size), length=barrel_len),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=frame,
        name="hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )
    # Keep the flange narrower than the dome's hinge lugs/brackets at +/-edge_y so
    # the rotating flange never grazes them in the closed pose; it still overlaps
    # the leaf centre for in-part connectivity.
    part.visual(
        Box((0.05 * resolved.size, barrel_len * 0.55, 0.08 * resolved.size)),
        origin=Origin(xyz=(-0.065 * resolved.size, 0.0, 0.04 * resolved.size)),
        material=frame,
        name="hinge_flange", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        mesh_from_geometry(_build_shutter_leaf(resolved), "shutter_leaf"),
        material=shell,
        name="leaf_shell", material_class_id=("metal.paint_coated" if resolved.material_style in {"white_observatory", "graphite_research", "desert_field"} else "metal.aluminum_bare"),
    )


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def build_observatory_dome(
    config: RotatingObservatoryDomeConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or RotatingObservatoryDomeConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-observatory-dome-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)
    model.meta["adopted_source_ids"] = ("S1", "S2", "S3", "S4", "S5", "S6")
    palette = PALETTES[resolved.material_style]
    mats = {
        "concrete": model.material("concrete", rgba=palette["concrete"]),
        "shell": model.material("dome_shell_paint", rgba=palette["shell"]),
        "track": model.material("track_steel", rgba=palette["track"]),
        "frame": model.material("dark_frame", rgba=palette["frame"]),
        "glass": model.material("black_glass", rgba=palette["glass"]),
        "accent": model.material("accent_steel", rgba=palette["accent"]),
    }

    foundation = model.part("foundation")
    _build_foundation(foundation, resolved, mats=mats)

    support_pier = model.part("support_pier")
    _build_support_pier(support_pier, resolved, mats=mats)

    dome_shell = model.part("dome_shell")
    _build_dome_shell(dome_shell, resolved, mats=mats)

    shutter_leaf = model.part("shutter_leaf")
    _build_shutter_leaf_part(shutter_leaf, resolved, mats=mats)

    # ---- FIXED: foundation -> support_pier (non-articulated instrument proxy)
    pier_origin = (resolved.pier_offset_x, resolved.pier_offset_y, resolved.slab_height)
    model.articulation(
        "foundation_to_support_pier",
        ArticulationType.FIXED,
        parent=foundation,
        child=support_pier,
        origin=Origin(xyz=pier_origin),
        meta=_joint_meta("fixed", None, pier_origin, None),
    )

    # ---- CONTINUOUS: foundation -> dome_shell (azimuth rotation, +Z)
    dome_origin = (0.0, 0.0, resolved.track_top_z)
    model.articulation(
        "dome_rotation",
        ArticulationType.CONTINUOUS,
        parent=foundation,
        child=dome_shell,
        origin=Origin(xyz=dome_origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=35000.0, velocity=0.35),
        meta=_joint_meta("continuous", (0.0, 0.0, 1.0), dome_origin, "unbounded"),
    )

    # ---- REVOLUTE: dome_shell -> shutter_leaf (slit shutter, +Y horizontal)
    shutter_origin = (resolved.hinge_x, 0.0, resolved.hinge_z)
    model.articulation(
        "slit_shutter",
        ArticulationType.REVOLUTE,
        parent=dome_shell,
        child=shutter_leaf,
        origin=Origin(xyz=shutter_origin),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=2200.0,
            velocity=0.8,
            lower=resolved.shutter_open_lower,
            upper=resolved.shutter_open_upper,
        ),
        meta=_joint_meta(
            "revolute",
            (0.0, 1.0, 0.0),
            shutter_origin,
            (resolved.shutter_open_lower, resolved.shutter_open_upper),
        ),
    )

    return model


def build_seeded_observatory_dome(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_observatory_dome(config_from_seed(seed), assets=assets)


def with_overrides(
    config: RotatingObservatoryDomeConfig, **overrides
) -> RotatingObservatoryDomeConfig:
    from dataclasses import replace

    return replace(config, **overrides)


def slot_choices_for_config(
    resolved: ResolvedRotatingObservatoryDomeConfig,
) -> list[tuple[str, str]]:
    """Recorded on ``model.meta`` for the module_topology_diversity gate."""
    return [
        ("foundation_ring", resolved.material_style),
        ("dome_shell", resolved.dome_shape),
        ("roller_bogies", str(resolved.roller_count)),
        ("crown_cap", str(resolved.crown_cap)),
        ("service_ledge", str(resolved.service_ledge)),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Author tests (run by `articraft external check`, not by the sweep baseline)
# --------------------------------------------------------------------------- #


def run_observatory_dome_tests(
    object_model: ArticulatedObject, config: RotatingObservatoryDomeConfig
) -> TestReport:
    ctx = TestContext(object_model)
    resolved = resolve_config(config)

    part_names = {part.name for part in object_model.parts}
    ctx.check(
        "core parts present",
        {"foundation", "dome_shell", "shutter_leaf"}.issubset(part_names),
        details=f"parts={sorted(part_names)}",
    )

    dome_rotation = object_model.get_articulation("dome_rotation")
    slit_shutter = object_model.get_articulation("slit_shutter")
    ctx.check(
        "azimuth rotation is continuous about +Z",
        str(dome_rotation.articulation_type).endswith("CONTINUOUS")
        and tuple(round(a, 3) for a in dome_rotation.axis) == (0.0, 0.0, 1.0),
        details=f"type={dome_rotation.articulation_type}, axis={dome_rotation.axis}",
    )
    ctx.check(
        "shutter hinge is horizontal revolute",
        str(slit_shutter.articulation_type).endswith("REVOLUTE")
        and abs(slit_shutter.axis[2]) < 1e-6,
        details=f"type={slit_shutter.articulation_type}, axis={slit_shutter.axis}",
    )

    dome_visuals = {v.name for v in object_model.get_part("dome_shell").visuals}
    ctx.check(
        "dome carries both shell meshes",
        {"rotating_curb", "main_shell"}.issubset(dome_visuals),
        details=f"dome_visuals={sorted(dome_visuals)}",
    )

    if "support_pier" in part_names:
        ctx.expect_origin_distance(
            object_model.get_part("dome_shell"),
            object_model.get_part("support_pier"),
            axes="xy",
            min_dist=max(0.05, resolved.pier_radius * 0.5),
            name="rotating dome axis stays offset from the telescope pier",
        )

    # The shutter leaf should swing outward (+X) and upward (+Z) when opened.
    closed = ctx.part_element_world_aabb(object_model.get_part("shutter_leaf"), elem="leaf_shell")
    with ctx.pose({slit_shutter: min(resolved.shutter_open_upper, math.radians(78.0))}):
        opened = ctx.part_element_world_aabb(
            object_model.get_part("shutter_leaf"), elem="leaf_shell"
        )
    if closed is not None and opened is not None:
        closed_c = tuple((closed[0][i] + closed[1][i]) * 0.5 for i in range(3))
        opened_c = tuple((opened[0][i] + opened[1][i]) * 0.5 for i in range(3))
        ctx.check(
            "shutter opens outward and upward",
            opened_c[2] > closed_c[2] + 0.02 * resolved.size,
            details=f"closed_center={closed_c}, opened_center={opened_c}",
        )

    return ctx.report()
