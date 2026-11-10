# SPDX-License-Identifier: Apache-2.0

"""Healthcare / Prosthetic limb — modular procedural template.

Below-knee (trans-tibial) prosthetic LEG, optionally above-knee (trans-femoral)
when a polycentric knee joint is inserted. Serial named-slot chain:

    socket -> [knee] -> pylon/shank -> ankle -> foot

Slots (all source-backed, see specs_modular_v1/Healthcare_Prosthetic_limb.md):

- Slot A foot  (③ Primary Form Family): running_blade / sach_foot / articulated_foot
- Slot B knee: below_knee_none / above_knee_polycentric
- Slot C pylon: exposed_tube_pylon / shock_pylon / foam_cosmesis_cover

Geometry generators are adapted verbatim from the 5-star sources — the mesh
socket shell + host-conformal carbon wraps (S1), the carbon J-blade ribbon (S1),
the SACH section-loft foot (S4), the cadquery skeletal shin frame (S1), the
polycentric knee block (S3), the telescoping shock damper + helical coil (S6),
the lofted foam cosmesis sleeve (S5), and the built-up articulated foot (S2).

Coordinate convention: the socket is the root, authored with its distal cap at
part-local z=0 and the cup rising to z~+0.23. Every downstream part is authored
in its OWN local frame whose origin is the part's top mount face, so each chain
joint's origin sits on real mating hardware. The ankle/knee/shock joints are
captured pin/telescope mechanisms — grandfathered (no MatingContract) with
element-scoped overlap allowances, per AUTHORING.md Rule 2.
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
    Box,
    Cylinder,
    LoftSection,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    SectionLoftSpec,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    section_loft,
    tube_from_spline_points,
)

__modular__ = True


FootModule = Literal["running_blade", "sach_foot", "articulated_foot"]
KneeModule = Literal["below_knee_none", "above_knee_polycentric"]
PylonModule = Literal["exposed_tube_pylon", "shock_pylon", "foam_cosmesis_cover"]
PaletteStyle = Literal[
    "carbon_titanium",
    "clinical_blue",
    "carbon_red",
    "skin_cosmesis",
    "titanium_brushed",
    "foam_liner_tan",
]

FOOT_MODULES: tuple[FootModule, ...] = ("running_blade", "sach_foot", "articulated_foot")
KNEE_MODULES: tuple[KneeModule, ...] = ("below_knee_none", "above_knee_polycentric")
PYLON_MODULES: tuple[PylonModule, ...] = (
    "exposed_tube_pylon",
    "shock_pylon",
    "foam_cosmesis_cover",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "carbon_titanium",
    "clinical_blue",
    "carbon_red",
    "skin_cosmesis",
    "titanium_brushed",
    "foam_liner_tan",
)


# Role keys drive every .visual(material=...). Each palette style provides all.
PROSTHETIC_PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "carbon_titanium": {
        "socket": (0.72, 0.58, 0.40, 1.0),
        "liner": (0.92, 0.84, 0.66, 1.0),
        "carbon": (0.012, 0.014, 0.015, 1.0),
        "blade": (0.006, 0.007, 0.008, 1.0),
        "metal": (0.46, 0.47, 0.45, 1.0),
        "accent": (0.00, 0.24, 0.78, 1.0),
        "foam": (0.85, 0.74, 0.63, 1.0),
        "sole": (0.05, 0.05, 0.055, 1.0),
    },
    "clinical_blue": {
        "socket": (0.04, 0.30, 0.80, 1.0),
        "liner": (0.80, 0.82, 0.85, 1.0),
        "carbon": (0.026, 0.030, 0.038, 1.0),
        "blade": (0.02, 0.02, 0.025, 1.0),
        "metal": (0.62, 0.64, 0.66, 1.0),
        "accent": (0.84, 0.05, 0.04, 1.0),
        "foam": (0.86, 0.75, 0.64, 1.0),
        "sole": (0.016, 0.016, 0.018, 1.0),
    },
    "carbon_red": {
        "socket": (0.10, 0.10, 0.11, 1.0),
        "liner": (0.30, 0.30, 0.32, 1.0),
        "carbon": (0.02, 0.02, 0.022, 1.0),
        "blade": (0.02, 0.02, 0.022, 1.0),
        "metal": (0.55, 0.56, 0.57, 1.0),
        "accent": (0.85, 0.06, 0.05, 1.0),
        "foam": (0.80, 0.68, 0.58, 1.0),
        "sole": (0.05, 0.05, 0.055, 1.0),
    },
    "skin_cosmesis": {
        "socket": (0.86, 0.68, 0.56, 1.0),
        "liner": (0.90, 0.78, 0.68, 1.0),
        "carbon": (0.15, 0.13, 0.12, 1.0),
        "blade": (0.12, 0.10, 0.09, 1.0),
        "metal": (0.60, 0.60, 0.60, 1.0),
        "accent": (0.70, 0.45, 0.40, 1.0),
        "foam": (0.88, 0.72, 0.60, 1.0),
        "sole": (0.10, 0.09, 0.08, 1.0),
    },
    "titanium_brushed": {
        "socket": (0.55, 0.56, 0.58, 1.0),
        "liner": (0.75, 0.76, 0.78, 1.0),
        "carbon": (0.10, 0.11, 0.12, 1.0),
        "blade": (0.10, 0.11, 0.12, 1.0),
        "metal": (0.78, 0.80, 0.82, 1.0),
        "accent": (0.20, 0.55, 0.75, 1.0),
        "foam": (0.82, 0.80, 0.78, 1.0),
        "sole": (0.08, 0.08, 0.09, 1.0),
    },
    "foam_liner_tan": {
        "socket": (0.68, 0.54, 0.36, 1.0),
        "liner": (0.94, 0.86, 0.68, 1.0),
        "carbon": (0.05, 0.05, 0.055, 1.0),
        "blade": (0.05, 0.05, 0.055, 1.0),
        "metal": (0.50, 0.50, 0.48, 1.0),
        "accent": (0.90, 0.62, 0.20, 1.0),
        "foam": (0.92, 0.82, 0.66, 1.0),
        "sole": (0.06, 0.06, 0.065, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ProstheticLegConfig:
    foot_module: FootModule | None = None
    knee_module: KneeModule | None = None
    pylon_module: PylonModule | None = None
    palette_style: PaletteStyle = "carbon_titanium"
    shank_length_scale: float = 1.0
    foot_scale: float = 1.0
    knee_upper: float = 1.4
    palette: dict[str, tuple[float, float, float, float]] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolvedProstheticLegConfig:
    foot_module: FootModule
    knee_module: KneeModule
    pylon_module: PylonModule
    palette_style: PaletteStyle
    shank_length_scale: float
    foot_scale: float
    knee_upper: float
    below_knee: bool
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(float(value), hi))


def config_from_seed(seed: int) -> ProstheticLegConfig:
    rng = random.Random(seed)
    return ProstheticLegConfig(
        foot_module=rng.choice(FOOT_MODULES),
        knee_module=rng.choice(KNEE_MODULES),
        pylon_module=rng.choice(PYLON_MODULES),
        palette_style=rng.choice(PALETTE_STYLES),
        shank_length_scale=round(rng.uniform(0.90, 1.12), 4),
        foot_scale=round(rng.uniform(0.92, 1.10), 4),
        knee_upper=round(rng.uniform(1.15, 1.55), 4),
    )


def resolve_config(config: ProstheticLegConfig) -> ResolvedProstheticLegConfig:
    foot = config.foot_module or "running_blade"
    knee = config.knee_module or "below_knee_none"
    pylon = config.pylon_module or "exposed_tube_pylon"
    if foot not in FOOT_MODULES:
        raise ValueError(f"Unsupported foot_module: {foot}")
    if knee not in KNEE_MODULES:
        raise ValueError(f"Unsupported knee_module: {knee}")
    if pylon not in PYLON_MODULES:
        raise ValueError(f"Unsupported pylon_module: {pylon}")
    if config.palette_style not in PROSTHETIC_PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    palette = dict(config.palette)
    if not palette:
        palette = dict(PROSTHETIC_PALETTES[config.palette_style])

    return ResolvedProstheticLegConfig(
        foot_module=foot,
        knee_module=knee,
        pylon_module=pylon,
        palette_style=config.palette_style,
        shank_length_scale=_clamp(config.shank_length_scale, 0.90, 1.12),
        foot_scale=_clamp(config.foot_scale, 0.92, 1.10),
        knee_upper=_clamp(config.knee_upper, 1.15, 1.55),
        below_knee=(knee == "below_knee_none"),
        palette=palette,
    )


# ---------------------------------------------------------------------------
# Shared low-level mesh helpers (adapted verbatim from S1/S4/S6)
# ---------------------------------------------------------------------------
def _sgn_pow(value: float, power: float) -> float:
    if value == 0.0:
        return 0.0
    return math.copysign(abs(value) ** power, value)


def _add_quad(geom: MeshGeometry, a: int, b: int, c: int, d: int) -> None:
    geom.add_face(a, b, c)
    geom.add_face(a, c, d)


# --- Socket shell + host-conformal carbon wraps (S1) -----------------------
def _socket_top_z(theta: float) -> float:
    side_rise = 0.034 * (abs(math.sin(theta)) ** 1.7)
    front_scoop = 0.031 * max(math.cos(theta), 0.0) ** 3.0
    rear_relief = 0.010 * max(-math.cos(theta), 0.0) ** 2.0
    return 0.231 + side_rise - front_scoop - rear_relief


def _socket_surface_point(theta: float, f: float, offset: float = 0.0) -> tuple[float, float, float]:
    exponent = 2.45
    power = 2.0 / exponent
    eased = f**0.82
    rx = 0.034 + (0.073 - 0.034) * eased + offset
    ry = 0.028 + (0.056 - 0.028) * eased + offset
    cx = 0.006 * f
    c = math.cos(theta)
    s = math.sin(theta)
    return (
        cx + rx * _sgn_pow(c, power),
        ry * _sgn_pow(s, power),
        f * _socket_top_z(theta),
    )


def _socket_shell_geometry() -> MeshGeometry:
    geom = MeshGeometry()
    radial_segments = 72
    levels = 10
    thickness = 0.0045
    exponent = 2.45
    power = 2.0 / exponent
    outer: list[list[int]] = []
    inner: list[list[int]] = []
    for j in range(levels + 1):
        f = j / levels
        eased = f**0.82
        rx = 0.034 + (0.073 - 0.034) * eased
        ry = 0.028 + (0.056 - 0.028) * eased
        cx = 0.006 * f
        row: list[int] = []
        for i in range(radial_segments):
            theta = 2.0 * math.pi * i / radial_segments
            c = math.cos(theta)
            s = math.sin(theta)
            z = f * _socket_top_z(theta)
            row.append(geom.add_vertex(cx + rx * _sgn_pow(c, power), ry * _sgn_pow(s, power), z))
        outer.append(row)
    for j in range(levels + 1):
        f = j / levels
        eased = f**0.82
        rx = max(0.012, 0.034 + (0.073 - 0.034) * eased - thickness)
        ry = max(0.012, 0.028 + (0.056 - 0.028) * eased - thickness)
        cx = 0.006 * f
        row = []
        for i in range(radial_segments):
            theta = 2.0 * math.pi * i / radial_segments
            c = math.cos(theta)
            s = math.sin(theta)
            z = 0.024 + f * (_socket_top_z(theta) - 0.030)
            row.append(geom.add_vertex(cx + rx * _sgn_pow(c, power), ry * _sgn_pow(s, power), z))
        inner.append(row)
    for j in range(levels):
        for i in range(radial_segments):
            ni = (i + 1) % radial_segments
            _add_quad(geom, outer[j][i], outer[j][ni], outer[j + 1][ni], outer[j + 1][i])
            _add_quad(geom, inner[j + 1][i], inner[j + 1][ni], inner[j][ni], inner[j][i])
    for i in range(radial_segments):
        ni = (i + 1) % radial_segments
        _add_quad(geom, outer[-1][i], outer[-1][ni], inner[-1][ni], inner[-1][i])
    outer_center = geom.add_vertex(0.0, 0.0, 0.0)
    inner_center = geom.add_vertex(0.0, 0.0, 0.024)
    for i in range(radial_segments):
        ni = (i + 1) % radial_segments
        geom.add_face(outer_center, outer[0][ni], outer[0][i])
        geom.add_face(inner_center, inner[0][i], inner[0][ni])
    return geom


def _liner_edge_geometry() -> MeshGeometry:
    geom = MeshGeometry()
    radial_segments = 72
    exponent = 2.45
    power = 2.0 / exponent
    outer_top: list[int] = []
    outer_low: list[int] = []
    inner_top: list[int] = []
    inner_low: list[int] = []
    for i in range(radial_segments):
        theta = 2.0 * math.pi * i / radial_segments
        c = math.cos(theta)
        s = math.sin(theta)
        top_z = _socket_top_z(theta) - 0.002
        low_z = top_z - 0.016
        cx = 0.006
        for ring, rx, ry, z in (
            (outer_top, 0.067, 0.050, top_z),
            (outer_low, 0.067, 0.050, low_z),
            (inner_top, 0.058, 0.042, top_z - 0.001),
            (inner_low, 0.058, 0.042, low_z),
        ):
            ring.append(geom.add_vertex(cx + rx * _sgn_pow(c, power), ry * _sgn_pow(s, power), z))
    for i in range(radial_segments):
        ni = (i + 1) % radial_segments
        _add_quad(geom, outer_top[i], outer_top[ni], inner_top[ni], inner_top[i])
        _add_quad(geom, outer_low[ni], outer_low[i], inner_low[i], inner_low[ni])
        _add_quad(geom, outer_top[ni], outer_top[i], outer_low[i], outer_low[ni])
        _add_quad(geom, inner_top[i], inner_top[ni], inner_low[ni], inner_low[i])
    return geom


def _socket_wrap_band_geometry(
    f_lower: float,
    f_upper: float,
    theta_start: float = 0.0,
    theta_end: float = 2.0 * math.pi,
    *,
    radial_segments: int = 72,
) -> MeshGeometry:
    """Carbon wrap laid proud on the socket, derived per-theta from its surface."""
    geom = MeshGeometry()
    span = theta_end - theta_start
    closed = abs(span - 2.0 * math.pi) < 1.0e-6
    count = radial_segments if closed else max(8, int(radial_segments * abs(span) / (2.0 * math.pi)))
    rows: list[list[int]] = []
    for offset in (0.0022, -0.0014):
        for f in (f_lower, f_upper):
            row = []
            steps = count if closed else count + 1
            for i in range(steps):
                theta = theta_start + span * i / count
                if closed and i == count:
                    theta = theta_start
                row.append(geom.add_vertex(*_socket_surface_point(theta, f, offset=offset)))
            rows.append(row)
    outer_low, outer_high, inner_low, inner_high = rows
    last = count if closed else count
    for i in range(last):
        ni = (i + 1) % count if closed else i + 1
        _add_quad(geom, outer_low[i], outer_low[ni], outer_high[ni], outer_high[i])
        _add_quad(geom, inner_low[ni], inner_low[i], inner_high[i], inner_high[ni])
        _add_quad(geom, outer_high[i], outer_high[ni], inner_high[ni], inner_high[i])
        _add_quad(geom, outer_low[ni], outer_low[i], inner_low[i], inner_low[ni])
    if not closed:
        for i in (0, count):
            _add_quad(geom, outer_low[i], outer_high[i], inner_high[i], inner_low[i])
    return geom


def _pyramid_adapter_geometry() -> MeshGeometry:
    geom = MeshGeometry()
    top_z = -0.044
    bottom_z = -0.062
    top = 0.034
    bottom = 0.024
    top_idx = []
    bottom_idx = []
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        top_idx.append(geom.add_vertex(0.5 * top * sx, 0.5 * top * sy, top_z))
        bottom_idx.append(geom.add_vertex(0.5 * bottom * sx, 0.5 * bottom * sy, bottom_z))
    for i in range(4):
        ni = (i + 1) % 4
        _add_quad(geom, top_idx[i], top_idx[ni], bottom_idx[ni], bottom_idx[i])
    _add_quad(geom, top_idx[0], top_idx[1], top_idx[2], top_idx[3])
    _add_quad(geom, bottom_idx[3], bottom_idx[2], bottom_idx[1], bottom_idx[0])
    return geom


# --- Carbon J running blade (S1) -------------------------------------------
def _add_ribbon_section(
    geom: MeshGeometry,
    point: tuple[float, float],
    tangent: tuple[float, float],
    width: float,
    thickness: float,
) -> list[int]:
    x, z = point
    tx, tz = tangent
    mag = math.hypot(tx, tz)
    if mag < 1.0e-9:
        tx, tz = 1.0, 0.0
    else:
        tx, tz = tx / mag, tz / mag
    nx, nz = -tz, tx
    return [
        geom.add_vertex(x + nx * thickness * 0.5, -width * 0.5, z + nz * thickness * 0.5),
        geom.add_vertex(x + nx * thickness * 0.5, width * 0.5, z + nz * thickness * 0.5),
        geom.add_vertex(x - nx * thickness * 0.5, width * 0.5, z - nz * thickness * 0.5),
        geom.add_vertex(x - nx * thickness * 0.5, -width * 0.5, z - nz * thickness * 0.5),
    ]


def _add_ribbon(
    geom: MeshGeometry,
    points: list[tuple[float, float]],
    widths: list[float],
    thickness: float,
    *,
    first_section: list[int] | None = None,
) -> list[list[int]]:
    sections: list[list[int]] = []
    for i, point in enumerate(points):
        if i == 0 and first_section is not None:
            sections.append(first_section)
            continue
        if i == 0:
            tangent = (points[1][0] - point[0], points[1][1] - point[1])
        elif i == len(points) - 1:
            tangent = (point[0] - points[i - 1][0], point[1] - points[i - 1][1])
        else:
            tangent = (points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1])
        sections.append(_add_ribbon_section(geom, point, tangent, widths[i], thickness))
    for j in range(len(sections) - 1):
        for i in range(4):
            _add_quad(
                geom,
                sections[j][i],
                sections[j][(i + 1) % 4],
                sections[j + 1][(i + 1) % 4],
                sections[j + 1][i],
            )
    for cap in (sections[0], sections[-1]):
        geom.add_face(cap[0], cap[1], cap[2])
        geom.add_face(cap[0], cap[2], cap[3])
    return sections


def _running_blade_geometry(scale: float = 1.0) -> MeshGeometry:
    geom = MeshGeometry()
    main_points = [
        (0.000, -0.014),
        (0.006, -0.032),
        (0.000, -0.048),
        (-0.018, -0.060),
        (-0.024, -0.070),
        (-0.004, -0.075),
        (0.050 * scale, -0.073),
        (0.110 * scale, -0.066),
        (0.158 * scale, -0.054),
    ]
    main_widths = [0.036, 0.040, 0.044, 0.046, 0.047, 0.048, 0.046, 0.040, 0.032]
    main_sections = _add_ribbon(geom, main_points, main_widths, 0.0070)
    heel_points = [
        main_points[4],
        (-0.052 * scale, -0.070),
        (-0.090 * scale, -0.064),
        (-0.116 * scale, -0.052),
    ]
    heel_widths = [main_widths[4], 0.044, 0.038, 0.030]
    _add_ribbon(geom, heel_points, heel_widths, 0.0060, first_section=main_sections[4])
    return geom


# --- SACH foot section loft (S4) -------------------------------------------
def _sach_foot_body_geometry(scale: float = 1.0) -> MeshGeometry:
    stations = [
        (-0.062 * scale, 0.024, -0.058, -0.002),
        (-0.030 * scale, 0.028, -0.060, 0.004),
        (0.015 * scale, 0.025, -0.048, 0.002),
        (0.070 * scale, 0.042, -0.060, -0.002),
        (0.110 * scale, 0.036, -0.058, -0.006),
        (0.148 * scale, 0.025, -0.050, -0.012),
        (0.178 * scale, 0.013, -0.044, -0.018),
    ]
    n_points = 24
    sections: list[LoftSection] = []
    for x_pos, hw, sole_z, top_z in stations:
        height = top_z - sole_z
        center_z = 0.5 * (sole_z + top_z)
        half_h = 0.5 * height
        points: list[tuple[float, float, float]] = []
        for i in range(n_points):
            theta = 2.0 * math.pi * i / n_points
            c = math.cos(theta)
            s = math.sin(theta)
            y = hw * c
            if s <= 0.0:
                z_norm = -(abs(s) ** 2.5)
                z = max(center_z + z_norm * half_h, sole_z)
            else:
                z = center_z + (s**0.8) * half_h
            points.append((x_pos, y, z))
        sections.append(LoftSection(points=tuple(points)))
    return section_loft(SectionLoftSpec(sections=tuple(sections), cap=True, solid=True))


# --- Telescoping shock helical coil (S6) -----------------------------------
def _spring_coil_geometry(
    *,
    helix_radius: float = 0.013,
    wire_radius: float = 0.0025,
    num_turns: int = 5,
    height: float = 0.040,
    z_center: float = -0.155,
    path_segments_per_turn: int = 24,
    cross_segments: int = 8,
) -> MeshGeometry:
    geom = MeshGeometry()
    total = num_turns * path_segments_per_turn
    rings: list[list[int]] = []
    centers: list[tuple[float, float, float]] = []
    for i in range(total + 1):
        t = i / total
        angle = t * num_turns * 2.0 * math.pi
        cx = helix_radius * math.cos(angle)
        cy = helix_radius * math.sin(angle)
        cz = z_center + height * (0.5 - t)
        dt = 1.0 / max(total, 1)
        angle_next = (t + dt) * num_turns * 2.0 * math.pi
        tx = helix_radius * math.cos(angle_next) - cx
        ty = helix_radius * math.sin(angle_next) - cy
        tz = -height * dt
        tlen = math.sqrt(tx * tx + ty * ty + tz * tz)
        if tlen < 1.0e-12:
            tx, ty, tz = 0.0, 0.0, -1.0
        else:
            tx, ty, tz = tx / tlen, ty / tlen, tz / tlen
        nx, ny, nz = -math.cos(angle), -math.sin(angle), 0.0
        dot = nx * tx + ny * ty + nz * tz
        nx -= dot * tx
        ny -= dot * ty
        nz -= dot * tz
        nlen = math.sqrt(nx * nx + ny * ny + nz * nz)
        if nlen < 1.0e-12:
            nx, ny, nz = 1.0, 0.0, 0.0
        else:
            nx, ny, nz = nx / nlen, ny / nlen, nz / nlen
        bx = ty * nz - tz * ny
        by = tz * nx - tx * nz
        bz = tx * ny - ty * nx
        ring: list[int] = []
        for j in range(cross_segments):
            phi = j * 2.0 * math.pi / cross_segments
            cos_p = math.cos(phi)
            sin_p = math.sin(phi)
            ring.append(
                geom.add_vertex(
                    cx + wire_radius * (cos_p * nx + sin_p * bx),
                    cy + wire_radius * (cos_p * ny + sin_p * by),
                    cz + wire_radius * (cos_p * nz + sin_p * bz),
                )
            )
        rings.append(ring)
        centers.append((cx, cy, cz))
    for i in range(len(rings) - 1):
        for j in range(cross_segments):
            nj = (j + 1) % cross_segments
            _add_quad(geom, rings[i][j], rings[i][nj], rings[i + 1][nj], rings[i + 1][j])
    for ring, center in ((rings[0], centers[0]), (rings[-1], centers[-1])):
        ci = geom.add_vertex(*center)
        for j in range(cross_segments):
            nj = (j + 1) % cross_segments
            geom.add_face(ci, ring[j], ring[nj])
    return geom


# --- CadQuery bodies (S1 pylon, S3 knee, S5 cosmesis, S2 foot) --------------
def _pylon_frame_cadquery(translate_z: float, height: float) -> cq.Workplane:
    """Sculpted skeletal shin pylon with through lightening windows (S1).

    Windows are placed as fractions of ``height`` so they stay inside the box
    whatever shank length the seed samples.
    """
    body = cq.Workplane("XY").box(0.034, 0.056, height).edges("|Z").fillet(0.004)
    for y, zf, w, hf in (
        (-0.010, 0.28, 0.021, 0.31),
        (0.010, -0.05, 0.024, 0.29),
        (-0.008, -0.36, 0.019, 0.23),
    ):
        body = (
            body.faces(">X")
            .workplane(centerOption="CenterOfBoundBox")
            .center(y, zf * height)
            .rect(w, hf * height)
            .cutThruAll()
        )
    return body.translate((0.0, 0.0, translate_z))


def _knee_block_cadquery() -> cq.Workplane:
    """Polycentric prosthetic knee block (S3)."""
    body = (
        cq.Workplane("XY")
        .box(0.058, 0.044, 0.050)
        .edges("|Z")
        .fillet(0.006)
        .edges(">Z")
        .fillet(0.003)
        .edges("<Z")
        .fillet(0.003)
    )
    top_plate = (
        cq.Workplane("XY")
        .workplane(offset=0.025)
        .rect(0.062, 0.048)
        .extrude(0.006)
        .edges(">Z")
        .fillet(0.002)
    )
    body = body.union(top_plate)
    # Pivot bore through the block (the polycentric axis).
    bore = cq.Workplane("XZ").workplane(offset=-0.035).circle(0.006).extrude(0.070)
    body = body.cut(bore)
    front_recess = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.022, 0.0))
        .rect(0.036, 0.008)
        .extrude(0.034)
        .translate((0.0, 0.0, -0.017))
    )
    body = body.cut(front_recess)
    rear_recess = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, -0.022, 0.0))
        .rect(0.030, 0.008)
        .extrude(0.028)
        .translate((0.0, 0.0, -0.014))
    )
    body = body.cut(rear_recess)
    # Bottom tube clamp — overlap the block bottom (body extends to z=-0.025) so
    # the union fuses into a single solid rather than a face-touching compound.
    tube_clamp = cq.Workplane("XY").workplane(offset=-0.020).circle(0.018).extrude(-0.024)
    body = body.union(tube_clamp)
    clamp_bore = cq.Workplane("XY").workplane(offset=-0.020).circle(0.014).extrude(-0.024)
    body = body.cut(clamp_bore)
    return body


def _cosmesis_cover_shape(ankle_z: float, shank_top_z: float) -> cq.Workplane:
    """Lifelike foam cosmesis sleeve tapered calf->ankle (S5), spanning the shank.

    The bottom trim starts well above the ankle hardware (pin/hub at ankle_z
    +/-0.019) so the hollow sleeve never encloses/collides with the foot.
    """
    cover_bottom = ankle_z + 0.055
    cover_top = shank_top_z - 0.005
    h = max(0.12, cover_top - cover_bottom)
    outer = (
        cq.Workplane("XY")
        .workplane(offset=cover_bottom)
        .ellipse(0.026, 0.030)
        .workplane(offset=0.45 * h)
        .ellipse(0.038, 0.044)
        .workplane(offset=0.35 * h)
        .ellipse(0.040, 0.048)
        .workplane(offset=0.20 * h)
        .ellipse(0.036, 0.042)
        .loft(combine=True)
    )
    w = 0.005
    inner = (
        cq.Workplane("XY")
        .workplane(offset=cover_bottom - 0.005)
        .ellipse(0.026 - w, 0.030 - w)
        .workplane(offset=0.45 * h + 0.005)
        .ellipse(0.038 - w, 0.044 - w)
        .workplane(offset=0.35 * h)
        .ellipse(0.040 - w, 0.048 - w)
        .workplane(offset=0.20 * h + 0.005)
        .ellipse(0.036 - w, 0.042 - w)
        .loft(combine=True)
    )
    shell = outer.cut(inner)
    try:
        shell = shell.edges().fillet(0.002)
    except Exception:
        pass
    return shell


def _rounded_box(size: tuple[float, float, float], radius: float) -> cq.Workplane:
    shape = cq.Workplane("XY").box(*size)
    try:
        shape = shape.edges("|Z").fillet(radius)
    except Exception:
        pass
    return shape


def _soft_box(size: tuple[float, float, float], radius: float) -> cq.Workplane:
    """Box with rounded edges, falling back gracefully (S2)."""
    safe = min(radius, 0.45 * min(size))
    for r in (safe, safe * 0.6, safe * 0.35):
        if r <= 1.0e-4:
            break
        try:
            shape = cq.Workplane("XY").box(*size).edges().fillet(r)
            shape.val().Volume()
            return shape
        except Exception:
            continue
    try:
        return cq.Workplane("XY").box(*size).edges("|Z").fillet(min(radius, 0.45 * min(size[0], size[1])))
    except Exception:
        return cq.Workplane("XY").box(*size)


def _articulated_sole_shape() -> cq.Workplane:
    sole = _soft_box((0.248, 0.090, 0.027), 0.016).translate((0.045, 0.0, -0.112))
    toe_rocker = (
        _soft_box((0.058, 0.086, 0.022), 0.015).rotate((0, 0, 0), (0, 1, 0), 11.0).translate((0.158, 0.0, -0.103))
    )
    heel_pad = _soft_box((0.060, 0.086, 0.022), 0.015).translate((-0.060, 0.0, -0.103))
    return sole.union(toe_rocker).union(heel_pad)


def _articulated_foot_upper_shape() -> cq.Workplane:
    base = _soft_box((0.206, 0.072, 0.018), 0.012).translate((0.042, 0.0, -0.092))
    side_rail_l = _soft_box((0.156, 0.018, 0.024), 0.008).translate((0.040, 0.032, -0.076))
    side_rail_r = _soft_box((0.156, 0.018, 0.024), 0.008).translate((0.040, -0.032, -0.076))
    toe_cap = (
        _soft_box((0.078, 0.066, 0.026), 0.015).rotate((0, 0, 0), (0, 1, 0), 7.0).translate((0.144, 0.0, -0.080))
    )
    midfoot_bridge = _soft_box((0.054, 0.060, 0.032), 0.012).translate((0.006, 0.0, -0.052))
    ankle_pedestal = _rounded_box((0.054, 0.052, 0.082), 0.012).translate((-0.018, 0.0, -0.041))
    heel_counter = _soft_box((0.066, 0.062, 0.046), 0.018).translate((-0.046, 0.0, -0.066))
    return (
        base.union(side_rail_l)
        .union(side_rail_r)
        .union(toe_cap)
        .union(midfoot_bridge)
        .union(ankle_pedestal)
        .union(heel_counter)
    )


def _articulated_spring_coil_mesh():
    """Red energy-return coil for the articulated foot (S2)."""
    p0 = (0.130, 0.0, -0.074)
    p1 = (0.050, 0.0, -0.036)
    turns = 4.5
    coil_radius = 0.0108
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    dz = p1[2] - p0[2]
    length = math.sqrt(dx * dx + dz * dz)
    ux = dx / length
    uz = dz / length
    e2 = (-uz, 0.0, ux)
    steps = 112
    points: list[tuple[float, float, float]] = []
    for i in range(steps + 1):
        t = i / steps
        theta = 2.0 * math.pi * turns * t
        points.append(
            (
                p0[0] + dx * t + coil_radius * math.sin(theta) * e2[0],
                p0[1] + dy * t + coil_radius * math.cos(theta) * 1.0,
                p0[2] + dz * t + coil_radius * math.sin(theta) * e2[2],
            )
        )
    return mesh_from_geometry(
        tube_from_spline_points(points, radius=0.0026, samples_per_segment=3, radial_segments=14, cap_ends=True),
        "red_coil_spring",
    )


# ---------------------------------------------------------------------------
# Layout constants (single-sourced geometric quantities, per Contract 3c)
# ---------------------------------------------------------------------------
ADAPTER_LEN = 0.073  # pyramid coupler stack height (below-knee only)
BASE_SHANK_SPAN = 0.147  # top_collar-top -> ankle, at shank_length_scale=1
KNEE_BLOCK_DZ = -0.029  # translate the S3 block so its top plate sits at knee-local +0.002
KNEE_PIVOT_Z = -0.062  # knee-local z of the knee->pylon flexion revolute (inside the tube clamp)


def _shank_top_z(r: ResolvedProstheticLegConfig) -> float:
    """Pylon-local z of the shank top (top_collar top face)."""
    return -ADAPTER_LEN if r.below_knee else 0.0


def _shank_span(r: ResolvedProstheticLegConfig) -> float:
    return BASE_SHANK_SPAN * r.shank_length_scale


# ---------------------------------------------------------------------------
# Socket (root)
# ---------------------------------------------------------------------------
def _build_socket(model: ArticulatedObject) -> None:
    socket = model.part("socket")
    socket.visual(mesh_from_geometry(_socket_shell_geometry(), "socket_shell"), material="socket", name="socket_shell", material_class_id="plastic.opaque_generic")
    socket.visual(mesh_from_geometry(_liner_edge_geometry(), "liner_edge"), material="liner", name="liner_edge", material_class_id="fabric.flexible_foam")
    socket.visual(
        Cylinder(radius=0.026, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.009)),
        material="metal",
        name="distal_plate", material_class_id="metal.aluminum_bare",
    )
    socket.visual(
        mesh_from_geometry(_socket_wrap_band_geometry(0.56, 0.69), "carbon_mid_band"),
        material="carbon",
        name="carbon_mid_band", material_class_id="fabric.carbon_weave",
    )
    socket.visual(
        mesh_from_geometry(_socket_wrap_band_geometry(0.02, 0.22), "carbon_distal_cup"),
        material="carbon",
        name="carbon_distal_cup", material_class_id="fabric.carbon_weave",
    )
    socket.visual(
        mesh_from_geometry(
            _socket_wrap_band_geometry(0.22, 0.88, 0.72, 2.0 * math.pi - 0.72), "carbon_side_wrap"
        ),
        material="carbon",
        name="carbon_side_wrap", material_class_id="fabric.carbon_weave",
    )


# ---------------------------------------------------------------------------
# Slot B: knee
# ---------------------------------------------------------------------------
def _build_knee(model: ArticulatedObject, r: ResolvedProstheticLegConfig) -> None:
    """Polycentric knee housing, rigid on the socket. The flexion revolute is
    at knee->pylon (KNEE_PIVOT_Z), so the shank swings and the housing stays
    put — nothing sits above the pivot on the moving side to sweep the socket.
    """
    knee = model.part("knee")
    knee.visual(
        mesh_from_cadquery(
            _knee_block_cadquery().translate((0.0, 0.0, KNEE_BLOCK_DZ)), "knee_housing", tolerance=0.0007
        ),
        material="carbon",
        name="knee_housing", material_class_id="fabric.carbon_weave",
    )
    # Flexion axle sits at the tube-clamp / pivot, along y.
    knee.visual(
        Cylinder(radius=0.007, length=0.064),
        origin=Origin(xyz=(0.0, 0.0, KNEE_PIVOT_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="metal",
        name="knee_axle", material_class_id="metal.stainless_matte",
    )
    knee.visual(
        Cylinder(radius=0.016, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, KNEE_PIVOT_Z + 0.006)),
        material="metal",
        name="knee_clamp_ring", material_class_id="metal.aluminum_bare",
    )


# ---------------------------------------------------------------------------
# Slot C helpers: adapter coupler + fork + shank details
# ---------------------------------------------------------------------------
def _emit_adapter(part, r: ResolvedProstheticLegConfig) -> None:
    """Pyramid metal coupler occupying pylon-local z in [-ADAPTER_LEN, 0].

    Only below-knee: above-knee uses the knee tube-clamp as the coupler.
    """
    part.visual(Cylinder(radius=0.028, length=0.012), origin=Origin(xyz=(0.0, 0.0, -0.006)), material="metal", name="adapter_flange", material_class_id="metal.aluminum_bare")
    part.visual(Cylinder(radius=0.019, length=0.018), origin=Origin(xyz=(0.0, 0.0, -0.021)), material="metal", name="adapter_stack", material_class_id="metal.aluminum_bare")
    part.visual(Cylinder(radius=0.0155, length=0.014), origin=Origin(xyz=(0.0, 0.0, -0.037)), material="metal", name="adapter_step", material_class_id="metal.aluminum_bare")
    part.visual(mesh_from_geometry(_pyramid_adapter_geometry(), "adapter_pyramid"), material="metal", name="adapter_pyramid", material_class_id="metal.aluminum_bare")
    part.visual(Cylinder(radius=0.014, length=0.011), origin=Origin(xyz=(0.0, 0.0, -0.0675)), material="metal", name="adapter_plug", material_class_id="metal.aluminum_bare")


def _emit_fork(part, ankle_z: float) -> None:
    """Ankle yoke fork at ankle_z: bridge + two cheek plates capturing the pin.

    The bridge overlaps the fork plates (their top is at ankle_z+0.025) so the
    whole yoke is one connected island.
    """
    part.visual(Box((0.042, 0.080, 0.016)), origin=Origin(xyz=(0.0, 0.0, ankle_z + 0.028)), material="metal", name="fork_bridge", material_class_id="metal.aluminum_bare")
    part.visual(Box((0.040, 0.008, 0.050)), origin=Origin(xyz=(0.0, 0.036, ankle_z)), material="metal", name="fork_plate_0", material_class_id="metal.aluminum_bare")
    part.visual(Box((0.040, 0.008, 0.050)), origin=Origin(xyz=(0.0, -0.036, ankle_z)), material="metal", name="fork_plate_1", material_class_id="metal.aluminum_bare")


def _build_exposed_pylon(model: ArticulatedObject, r: ResolvedProstheticLegConfig, *, with_cosmesis: bool) -> tuple[str, float]:
    """Single skeletal shank part. Returns (ankle_parent_name, ankle_z_local)."""
    pylon = model.part("pylon")
    shank_top = _shank_top_z(r)
    span = _shank_span(r)
    ankle_z = shank_top - span

    if r.below_knee:
        _emit_adapter(pylon, r)

    # Top collar overlaps the coupler/knee above and the skeletal frame below.
    pylon.visual(
        Cylinder(radius=0.015, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, shank_top - 0.005)),
        material="carbon",
        name="top_collar", material_class_id="fabric.carbon_weave",
    )
    # Skeletal frame spans from just under the collar down into the fork bridge,
    # stopping clear of the ankle pin / hub (which sit at ankle_z +/-0.017).
    frame_top = shank_top - 0.004
    frame_bottom = ankle_z + 0.022
    frame_h = frame_top - frame_bottom
    frame_center = 0.5 * (frame_top + frame_bottom)
    pylon.visual(
        mesh_from_cadquery(
            _pylon_frame_cadquery(frame_center, frame_h), "skeletal_shin_frame", tolerance=0.0008
        ),
        material="carbon",
        name="skeletal_shin_frame", material_class_id="fabric.carbon_weave",
    )
    # Accent inserts embedded on the front face of the frame.
    for i, fz in enumerate((0.78, 0.52, 0.26)):
        pylon.visual(
            Box((0.006, 0.014, 0.030)),
            origin=Origin(xyz=(0.015, 0.0, frame_bottom + fz * frame_h)),
            material="accent",
            name=f"accent_insert_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    # Decorative round shin tube on the lower shin, kept clear of the ankle.
    pylon.visual(
        Cylinder(radius=0.016, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, ankle_z + 0.060)),
        material="carbon",
        name="round_shin_tube", material_class_id="fabric.carbon_weave",
    )
    _emit_fork(pylon, ankle_z)

    if with_cosmesis:
        pylon.visual(
            mesh_from_cadquery(_cosmesis_cover_shape(ankle_z, shank_top), "cosmesis_cover", tolerance=0.0009),
            material="foam",
            name="cosmesis_cover", material_class_id="fabric.flexible_foam",
        )
    return ("pylon", ankle_z)


def _build_shock_pylon(model: ArticulatedObject, r: ResolvedProstheticLegConfig) -> tuple[str, float]:
    """Coupler housing (pylon) + telescoping inner (shock_pylon, PRISMATIC).

    Returns (ankle_parent_name='shock_pylon', ankle_z_local_in_shock).
    """
    pylon = model.part("pylon")
    shank_top = _shank_top_z(r)
    if r.below_knee:
        _emit_adapter(pylon, r)
        shock_top = shank_top
    else:
        # Above-knee: a longer fixed damper-mount tube in place of the pyramid
        # adapter, dropping the shock assembly clear of the fixed knee housing so
        # the 20 mm telescoping compression never drives the damper into the knee.
        pylon.visual(
            Cylinder(radius=0.017, length=0.066),
            origin=Origin(xyz=(0.0, 0.0, shank_top - 0.033)),
            material="carbon",
            name="damper_mount_stub", material_class_id="fabric.carbon_weave",
        )
        shock_top = shank_top - 0.063

    shock = model.part("shock_pylon")
    s = r.shank_length_scale
    # shock-local z: damper cap top pokes just above 0 (into the coupler),
    # descending through the damper body/spring/piston to the fork/ankle.
    shock.visual(Cylinder(radius=0.018, length=0.014), origin=Origin(xyz=(0.0, 0.0, -0.005)), material="carbon", name="damper_cap", material_class_id="fabric.carbon_weave")
    shock.visual(Cylinder(radius=0.020, length=0.052 * s), origin=Origin(xyz=(0.0, 0.0, -0.036 * s)), material="carbon", name="damper_body", material_class_id="fabric.carbon_weave")
    shock.visual(Cylinder(radius=0.021, length=0.012), origin=Origin(xyz=(0.0, 0.0, -0.060 * s)), material="carbon", name="damper_lower_ring", material_class_id="fabric.carbon_weave")
    shock.visual(
        mesh_from_geometry(_spring_coil_geometry(z_center=-0.085 * s, height=0.045 * s), "spring_coil"),
        material="metal",
        name="spring_coil", material_class_id="metal.stainless_matte",
    )
    shock.visual(Cylinder(radius=0.011, length=0.070 * s), origin=Origin(xyz=(0.0, 0.0, -0.090 * s)), material="carbon", name="piston_tube", material_class_id="fabric.carbon_weave")
    shock.visual(Cylinder(radius=0.016, length=0.010), origin=Origin(xyz=(0.0, 0.0, -0.118 * s)), material="carbon", name="bump_stop", material_class_id="rubber.smooth_plain")
    ankle_z = -0.150 * s
    _emit_fork(shock, ankle_z)
    return ("shock_pylon", ankle_z, shock_top)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Slot A: feet
# ---------------------------------------------------------------------------
def _emit_ankle_pin(part) -> None:
    part.visual(
        Cylinder(radius=0.011, length=0.064),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="metal",
        name="ankle_pin", material_class_id="metal.stainless_matte",
    )


def _build_running_blade_foot(model: ArticulatedObject, r: ResolvedProstheticLegConfig) -> None:
    foot = model.part("foot")
    foot.visual(mesh_from_geometry(_running_blade_geometry(r.foot_scale), "curved_carbon_blade"), material="blade", name="foot_body", material_class_id="fabric.carbon_weave")
    _emit_ankle_pin(foot)
    foot.visual(Cylinder(radius=0.010, length=0.040), origin=Origin(xyz=(0.0, 0.0, -0.020)), material="blade", name="blade_neck", material_class_id="fabric.carbon_weave")


def _build_sach_foot(model: ArticulatedObject, r: ResolvedProstheticLegConfig) -> None:
    foot = model.part("foot")
    foot.visual(mesh_from_geometry(_sach_foot_body_geometry(r.foot_scale), "sach_foot_body"), material="foam", name="foot_body", material_class_id="fabric.flexible_foam")
    _emit_ankle_pin(foot)


def _build_articulated_foot(model: ArticulatedObject, r: ResolvedProstheticLegConfig) -> None:
    foot = model.part("foot")
    foot.visual(mesh_from_cadquery(_articulated_sole_shape(), "black_rubber_sole", tolerance=0.0009), material="sole", name="foot_body", material_class_id="rubber.smooth_plain")
    foot.visual(mesh_from_cadquery(_articulated_foot_upper_shape(), "blue_foot_frame", tolerance=0.0009), material="accent", name="foot_frame", material_class_id="metal.paint_coated")
    foot.visual(Cylinder(radius=0.017, length=0.052), origin=Origin(rpy=(math.pi / 2, 0.0, 0.0)), material="carbon", name="ankle_hub", material_class_id="fabric.carbon_weave")
    foot.visual(Cylinder(radius=0.0185, length=0.014), origin=Origin(rpy=(math.pi / 2, 0.0, 0.0)), material="metal", name="ankle_bearing_race", material_class_id="metal.chrome_polished")
    # Ankle pin reaches the pylon fork cheeks (y +/-0.037) so the foot is captured.
    foot.visual(Cylinder(radius=0.007, length=0.074), origin=Origin(rpy=(math.pi / 2, 0.0, 0.0)), material="metal", name="ankle_pin", material_class_id="metal.stainless_matte")
    for i, x in enumerate((-0.050, -0.010, 0.030, 0.070, 0.110, 0.150)):
        foot.visual(Box((0.018, 0.078, 0.004)), origin=Origin(xyz=(x, 0.0, -0.126)), material="sole", name=f"tread_{i}", material_class_id="rubber.directional_grooved")
    foot.visual(Box((0.038, 0.034, 0.018)), origin=Origin(xyz=(0.130, 0.0, -0.076)), material="accent", name="spring_lower_mount", material_class_id="metal.paint_coated")
    foot.visual(Box((0.034, 0.034, 0.020)), origin=Origin(xyz=(0.050, 0.0, -0.036)), material="accent", name="spring_upper_mount", material_class_id="metal.paint_coated")
    foot.visual(_articulated_spring_coil_mesh(), material="accent", name="red_coil_spring", material_class_id="metal.paint_coated")


FOOT_BUILDERS = {
    "running_blade": _build_running_blade_foot,
    "sach_foot": _build_sach_foot,
    "articulated_foot": _build_articulated_foot,
}


# ---------------------------------------------------------------------------
# Chain wiring
# ---------------------------------------------------------------------------
def _ankle_limits(r: ResolvedProstheticLegConfig) -> MotionLimits:
    return MotionLimits(effort=60.0, velocity=4.0, lower=-0.30, upper=0.35)


def build_prosthetic_leg(
    config: ProstheticLegConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or ProstheticLegConfig())
    model = ArticulatedObject(name="prosthetic_leg", assets=assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    for name, rgba in r.palette.items():
        model.material(name, rgba=rgba)

    _build_socket(model)

    # Slot B: optional knee inserted between socket and pylon.
    if not r.below_knee:
        _build_knee(model, r)

    # Slot C: pylon / shank.
    shock_top: float | None = None
    if r.pylon_module == "shock_pylon":
        ankle_parent, ankle_z, shock_top = _build_shock_pylon(model, r)
    else:
        ankle_parent, ankle_z = _build_exposed_pylon(
            model, r, with_cosmesis=(r.pylon_module == "foam_cosmesis_cover")
        )

    # Slot A: foot.
    FOOT_BUILDERS[r.foot_module](model, r)

    # --- joints ---
    if r.below_knee:
        model.articulation(
            "socket_to_pylon",
            ArticulationType.FIXED,
            parent="socket",
            child="pylon",
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            mating=MatingContract(
                parent_face_geometry="distal_plate",
                parent_face_side="negative_z",
                child_face_geometry="adapter_flange",
                child_face_side="positive_z",
                contact_tol=0.004,
            ),
        )
    else:
        # Knee housing is rigid on the socket; the shank (pylon) swings about
        # the lower knee pivot so nothing above the pivot sweeps the socket.
        model.articulation(
            "socket_to_knee",
            ArticulationType.FIXED,
            parent="socket",
            child="knee",
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            "knee_flex",
            ArticulationType.REVOLUTE,
            parent="knee",
            child="pylon",
            origin=Origin(xyz=(0.0, 0.0, KNEE_PIVOT_Z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=40.0, velocity=3.5, lower=0.0, upper=r.knee_upper),
        )

    if r.pylon_module == "shock_pylon":
        model.articulation(
            "adapter_to_shock_pylon",
            ArticulationType.PRISMATIC,
            parent="pylon",
            child="shock_pylon",
            origin=Origin(xyz=(0.0, 0.0, shock_top)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=800.0, velocity=0.6, lower=0.0, upper=0.020),
        )

    model.articulation(
        "ankle_pitch",
        ArticulationType.REVOLUTE,
        parent=ankle_parent,
        child="foot",
        origin=Origin(xyz=(0.0, 0.0, ankle_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=_ankle_limits(r),
    )
    return model


def build_seeded_prosthetic_leg(seed: int) -> ArticulatedObject:
    return build_prosthetic_leg(config_from_seed(seed))


def slot_choices_for_config(r: ResolvedProstheticLegConfig) -> list[tuple[str, str]]:
    return [
        ("foot_module", r.foot_module),
        ("knee_module", r.knee_module),
        ("pylon_module", r.pylon_module),
        ("palette_style", r.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _allow_captured_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedProstheticLegConfig) -> None:
    part_names = {p.name for p in model.parts}
    ankle_parent = "shock_pylon" if r.pylon_module == "shock_pylon" else "pylon"
    if "foot" in part_names and ankle_parent in part_names:
        for cheek in ("fork_plate_0", "fork_plate_1"):
            ctx.allow_overlap(
                model.get_part("foot"),
                model.get_part(ankle_parent),
                elem_a="ankle_pin",
                elem_b=cheek,
                reason="ankle pin is captured through the pylon fork yoke cheeks",
            )
    if not r.below_knee and "knee" in part_names and "pylon" in part_names:
        ctx.allow_overlap(
            model.get_part("knee"),
            model.get_part("pylon"),
            reason="polycentric knee tube clamp intentionally wraps the pylon top collar",
        )
    if not r.below_knee and "socket" in part_names and "knee" in part_names:
        ctx.allow_overlap(
            model.get_part("socket"),
            model.get_part("knee"),
            elem_a="distal_plate",
            elem_b="knee_housing",
            reason="knee top plate seats up against the socket distal plate at the knee axis",
        )
    if r.pylon_module == "shock_pylon" and "pylon" in part_names and "shock_pylon" in part_names:
        ctx.allow_overlap(
            model.get_part("pylon"),
            model.get_part("shock_pylon"),
            reason="telescoping shock inner nests inside the damper coupler housing (prismatic capture)",
        )


def run_prosthetic_leg_tests(model: ArticulatedObject, config: ProstheticLegConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    _allow_captured_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    joint_names = {j.name for j in model.articulations}
    ctx.check("ankle_pitch_exists", "ankle_pitch" in joint_names, "missing ankle_pitch")
    ctx.check(
        "foot_is_terminal",
        any(p.name == "foot" for p in model.parts),
        "prosthetic_leg must terminate in a foot part",
    )
    if not r.below_knee:
        ctx.check("above_knee_has_knee_revolute", "knee_flex" in joint_names, "missing knee flexion revolute")
        knee = model.get_articulation("knee_flex")
        lim = knee.motion_limits
        ctx.check(
            "knee_is_one_way_flexion",
            bool(lim and lim.lower >= -1e-6 and lim.upper > 0.4),
            f"knee should be one-way flexion, got {lim!r}",
        )
    if r.pylon_module == "shock_pylon":
        ctx.check("shock_has_prismatic", "adapter_to_shock_pylon" in joint_names, "missing shock prismatic")

    # Overall lower-limb scale.
    socket_aabb = ctx.part_element_world_aabb(model.get_part("socket"), elem="socket_shell")
    foot_aabb = ctx.part_element_world_aabb(model.get_part("foot"), elem="foot_body")
    if socket_aabb is not None and foot_aabb is not None:
        overall_height = socket_aabb[1][2] - foot_aabb[0][2]
        ctx.check(
            "prosthetic lower-limb overall height",
            0.42 <= overall_height <= 0.72,
            details=f"height={overall_height:.3f} m",
        )
    else:
        ctx.fail("prosthetic lower-limb overall height", "missing socket/foot AABB")

    # --- Rule 5: sampled-pose collision + one targeted pose per mechanism ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    ankle = model.get_articulation("ankle_pitch")
    with ctx.pose({ankle: -0.30}):
        plantar = ctx.part_element_world_aabb(model.get_part("foot"), elem="foot_body")
    with ctx.pose({ankle: 0.35}):
        dorsi = ctx.part_element_world_aabb(model.get_part("foot"), elem="foot_body")
    if plantar is not None and dorsi is not None:
        shifts = [abs(dorsi[k][a] - plantar[k][a]) for k in (0, 1) for a in (0, 1, 2)]
        ctx.check("ankle pitch swings the foot", max(shifts) > 0.020, details=f"max_shift={max(shifts):.3f}")
    else:
        ctx.fail("ankle pitch swings the foot", "missing posed foot AABB")

    if not r.below_knee:
        knee = model.get_articulation("knee_flex")
        with ctx.pose({knee: 0.0}):
            straight = ctx.part_world_position(model.get_part("foot"))
        with ctx.pose({knee: min(1.2, r.knee_upper)}):
            flexed = ctx.part_world_position(model.get_part("foot"))
        if straight is not None and flexed is not None:
            ctx.check(
                "knee flexion moves the foot posterior",
                flexed[0] < straight[0] - 0.01,
                details=f"straight_x={straight[0]:.3f}, flexed_x={flexed[0]:.3f}",
            )
        else:
            ctx.fail("knee flexion moves the foot posterior", "missing foot position")

    if r.pylon_module == "shock_pylon":
        damper = model.get_articulation("adapter_to_shock_pylon")
        rest_pos = ctx.part_world_position(model.get_part("shock_pylon"))
        with ctx.pose({damper: 0.020}):
            comp_pos = ctx.part_world_position(model.get_part("shock_pylon"))
        if rest_pos is not None and comp_pos is not None:
            ctx.check(
                "shock pylon compresses on prismatic axis",
                (comp_pos[2] - rest_pos[2]) > 0.015,
                details=f"lift={comp_pos[2] - rest_pos[2]:.4f} m",
            )
        else:
            ctx.fail("shock pylon compresses on prismatic axis", "missing shock position")

    return ctx.report()


__all__ = [
    "ProstheticLegConfig",
    "ResolvedProstheticLegConfig",
    "config_from_seed",
    "resolve_config",
    "build_prosthetic_leg",
    "build_seeded_prosthetic_leg",
    "slot_choices_for_seed",
    "run_prosthetic_leg_tests",
]
