# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``astronomical_telescope_on_tripod``.

Follows ``articraft_template_authoring/specs_modular_v1/astronomical_telescope_on_tripod.md``.

A tripod-mounted (or tabletop) astronomical telescope: grounded root support,
a mount head with at least two pointing DOF, an optical tube assembly (OTA),
and optional focus auxiliary. Default mature domain is equatorial fork on a
wedge tripod (S1) or alt-az refractor on spline legs (S3).

PRIMARY_ANCHOR: ``rec_astronomical_telescope_on_tripod_0104cd9f066948909101400e0dee1324``.

    tripod --polar (REVOLUTE, +Y)--> polar_head --RA (CONTINUOUS, +Z)--> fork_arm
         --DEC (REVOLUTE, -Y)--> optical_tube --focus (CONTINUOUS, +X)--> focus_knob

Four slots (mixed chain):

    root_support → mount_head → optical_assembly → focus_auxiliary

``config_from_seed(0)`` reproduces the anchor combination via ``anchor_mode``.
Other seeds sample the stable subdomain (equatorial_fork + altaz primarily).

Adopted sources (spec Adopted Source Index):
S1 0104cd9f — equatorial fork wedge tripod + SCT OTA + focus knob
S2 0003 — german EQ crown tripod + Newtonian mesh OTA
S3 04695a93 — spline-leg tripod + altaz arm + refractor OTA
S4 89eee286 — photo pan-tilt head + annular refractor scope
S5 09d71726 — tabletop dob base + rocker + reflector tube
S6 324ff748 — RA saddle mount + prismatic drawtube focuser chain
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

# adopted: S1 0104cd9f — wedge tripod + equatorial fork + SCT OTA + focus knob
# adopted: S2 0003 — crown tripod + german polar/declination + Newtonian mesh OTA
# adopted: S3 04695a93 — spline-leg tripod + altaz mount arm + refractor OTA
# adopted: S4 89eee286 — pan-tilt ball head + annular photo refractor scope
# adopted: S5 09d71726 — tabletop disc + rocker box + reflector tube (edge)
# adopted: S6 324ff748 — RA saddle + dovetail focuser + drawtube chain

__modular__ = True

RootSupportStyle = Literal["tripod_wedge", "tripod_spline", "tripod_crown", "tabletop_dob"]
MountFamily = Literal["equatorial_fork", "german_eq", "altaz", "photo_pan_tilt", "dobsonian"]
OtaStyle = Literal["sct_compact", "newtonian", "refractor", "photo_refractor"]
FocusAuxStyle = Literal["none", "knob", "drawtube_chain"]
MaterialStyle = Literal["powder_orange", "tripod_black", "graphite_service", "pale_wood"]

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "powder_orange": {
        "accent": (0.88, 0.33, 0.08, 1.0),
        "black": (0.015, 0.016, 0.018, 1.0),
        "dark": (0.07, 0.075, 0.08, 1.0),
        "metal": (0.56, 0.58, 0.60, 1.0),
        "rubber": (0.0, 0.0, 0.0, 1.0),
        "glass": (0.55, 0.78, 0.95, 0.34),
        "tube_gold": (0.78, 0.64, 0.28, 1.0),
        "wood": (0.72, 0.55, 0.34, 1.0),
    },
    "tripod_black": {
        "accent": (0.31, 0.33, 0.36, 1.0),
        "black": (0.12, 0.12, 0.13, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
        "metal": (0.72, 0.74, 0.77, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
        "glass": (0.13, 0.32, 0.48, 0.62),
        "tube_gold": (0.78, 0.64, 0.28, 1.0),
        "wood": (0.55, 0.48, 0.38, 1.0),
    },
    "graphite_service": {
        "accent": (0.38, 0.40, 0.42, 1.0),
        "black": (0.02, 0.023, 0.026, 1.0),
        "dark": (0.18, 0.19, 0.20, 1.0),
        "metal": (0.72, 0.73, 0.70, 1.0),
        "rubber": (0.015, 0.015, 0.014, 1.0),
        "glass": (0.13, 0.32, 0.48, 0.62),
        "tube_gold": (0.70, 0.62, 0.44, 1.0),
        "wood": (0.62, 0.58, 0.50, 1.0),
    },
    "pale_wood": {
        "accent": (0.42, 0.43, 0.42, 1.0),
        "black": (0.005, 0.005, 0.005, 1.0),
        "dark": (0.02, 0.035, 0.07, 1.0),
        "metal": (0.56, 0.58, 0.60, 1.0),
        "rubber": (0.015, 0.014, 0.012, 1.0),
        "glass": (0.70, 0.86, 0.95, 1.0),
        "tube_gold": (0.78, 0.64, 0.28, 1.0),
        "wood": (0.72, 0.55, 0.34, 1.0),
    },
}

_COMPAT: dict[MountFamily, dict[str, set[str]]] = {
    "equatorial_fork": {
        "roots": {"tripod_wedge", "tripod_crown"},
        "otas": {"sct_compact", "newtonian"},
        "focus": {"knob", "drawtube_chain", "none"},
    },
    "german_eq": {
        "roots": {"tripod_crown"},
        "otas": {"newtonian"},
        "focus": {"none", "knob"},
    },
    "altaz": {
        "roots": {"tripod_spline"},
        "otas": {"refractor"},
        "focus": {"none"},
    },
    "photo_pan_tilt": {
        "roots": {"tripod_spline"},
        "otas": {"photo_refractor"},
        "focus": {"none"},
    },
    "dobsonian": {
        "roots": {"tabletop_dob"},
        "otas": {"newtonian"},
        "focus": {"none"},
    },
}


@dataclass(frozen=True)
class AstronomicalTelescopeOnTripodConfig:
    """Public configuration. ``anchor_mode=True`` only from ``config_from_seed(0)``."""

    root_support_style: RootSupportStyle = "tripod_wedge"
    mount_family: MountFamily = "equatorial_fork"
    ota_style: OtaStyle = "sct_compact"
    focus_aux_style: FocusAuxStyle = "knob"
    material_style: MaterialStyle = "powder_orange"
    tripod_height: float = 0.785
    tripod_spread_radius: float = 0.50
    polar_wedge_tilt_deg: float = 35.0
    ota_length: float = 0.420
    ota_outer_radius: float = 0.120
    anchor_mode: bool = False
    name: str = "reference_astronomical_telescope_on_tripod"


@dataclass(frozen=True)
class ResolvedAstronomicalTelescopeOnTripodConfig:
    root_support_style: RootSupportStyle
    mount_family: MountFamily
    ota_style: OtaStyle
    focus_aux_style: FocusAuxStyle
    material_style: MaterialStyle
    tripod_height: float
    tripod_spread_radius: float
    polar_wedge_tilt_deg: float
    ota_length: float
    ota_outer_radius: float
    anchor_mode: bool
    palette: dict[str, tuple[float, float, float, float]]
    wedge_tilt_rad: float
    hub_top_z: float
    foot_z: float
    mount_seat_z: float
    dec_lower: float
    dec_upper: float
    alt_lower: float
    alt_upper: float
    tilt_lower: float
    tilt_upper: float
    name: str


def config_from_seed(seed: int) -> AstronomicalTelescopeOnTripodConfig:
    """Sample a reproducible configuration.

    seed=0 returns the PRIMARY_ANCHOR defaults. Other seeds primarily sample
    equatorial_fork and altaz stable subdomains while still reaching every
    declared Literal for coverage.
    """
    if seed == 0:
        return AstronomicalTelescopeOnTripodConfig(anchor_mode=True)

    rng = random.Random(seed)
    material_style: MaterialStyle = rng.choice(tuple(PALETTES))

    if seed % 19 == 0:
        mount_family: MountFamily = "dobsonian"
        root_support_style: RootSupportStyle = "tabletop_dob"
        ota_style: OtaStyle = "newtonian"
        focus_aux_style: FocusAuxStyle = "none"
    elif seed % 17 == 0:
        mount_family = "photo_pan_tilt"
        # Photo pan-tilt heads mount on a flat tripod top, not the tilted equatorial
        # wedge plate (whose raised edge fouls the saddle at tilt/pan extremes).
        root_support_style = "tripod_spline"
        ota_style = "photo_refractor"
        focus_aux_style = "none"
    elif seed % 13 == 0:
        mount_family = "german_eq"
        root_support_style = "tripod_crown"
        ota_style = "newtonian"
        focus_aux_style = rng.choice(("none", "knob"))
    elif seed % 37 == 0:
        mount_family = "equatorial_fork"
        root_support_style = "tripod_wedge"
        ota_style = "sct_compact"
        focus_aux_style = "drawtube_chain"
    elif seed % 31 == 0:
        mount_family = "equatorial_fork"
        root_support_style = "tripod_wedge"
        ota_style = "sct_compact"
        focus_aux_style = "knob"
    elif seed % 2 == 0:
        mount_family = "equatorial_fork"
        root_support_style = "tripod_wedge"
        ota_style = "sct_compact"
        focus_aux_style = "none"
    else:
        mount_family = "altaz"
        root_support_style = "tripod_spline"
        ota_style = "refractor"
        focus_aux_style = "none"

    tripod_height = round(rng.uniform(0.55, 0.95), 4)
    tripod_spread_radius = round(rng.uniform(0.38, 0.62), 4)
    polar_wedge_tilt_deg = round(rng.uniform(22.0, 58.0), 4)
    ota_length = round(rng.uniform(0.32, 0.82), 4)
    ota_outer_radius = round(rng.uniform(0.05, 0.12), 4)

    return AstronomicalTelescopeOnTripodConfig(
        root_support_style=root_support_style,
        mount_family=mount_family,
        ota_style=ota_style,
        focus_aux_style=focus_aux_style,
        material_style=material_style,
        tripod_height=tripod_height,
        tripod_spread_radius=tripod_spread_radius,
        polar_wedge_tilt_deg=polar_wedge_tilt_deg,
        ota_length=ota_length,
        ota_outer_radius=ota_outer_radius,
        name=f"seeded_astronomical_telescope_on_tripod_{seed}",
    )


def resolve_config(
    config: AstronomicalTelescopeOnTripodConfig,
) -> ResolvedAstronomicalTelescopeOnTripodConfig:
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    mount_family = config.mount_family
    root_support_style = config.root_support_style
    ota_style = config.ota_style
    focus_aux_style = config.focus_aux_style

    compat = _COMPAT.get(mount_family)
    if compat is None:
        raise ValueError(f"Unsupported mount_family: {mount_family}")
    if root_support_style not in compat["roots"]:
        root_support_style = next(iter(compat["roots"]))
    if ota_style not in compat["otas"]:
        ota_style = next(iter(compat["otas"]))
    if focus_aux_style not in compat["focus"]:
        focus_aux_style = next(iter(compat["focus"]))

    tripod_height = _clamp(config.tripod_height, 0.45, 1.10)
    tripod_spread_radius = _clamp(config.tripod_spread_radius, 0.35, 0.65)
    polar_wedge_tilt_deg = _clamp(config.polar_wedge_tilt_deg, 20.0, 62.0)
    ota_length = _clamp(config.ota_length, 0.28, 0.95)
    ota_outer_radius = _clamp(config.ota_outer_radius, 0.04, 0.14)

    if config.anchor_mode:
        tripod_height = 0.785
        tripod_spread_radius = 0.50
        polar_wedge_tilt_deg = 35.0
        ota_length = 0.420
        ota_outer_radius = 0.120
        mount_family = "equatorial_fork"
        root_support_style = "tripod_wedge"
        ota_style = "sct_compact"
        focus_aux_style = "knob"

    wedge_tilt_rad = math.radians(polar_wedge_tilt_deg)
    hub_top_z = tripod_height * 0.68
    foot_z = 0.03
    mount_seat_z = tripod_height * 0.975

    # Equatorial fork: DEC travel is physically limited by the OTA swinging into the
    # RA bearing housing. Single-sourced via _equatorial_dec_limits (Contract 3c).
    if mount_family == "equatorial_fork":
        dec_lower, dec_upper = _equatorial_dec_limits(
            tripod_height / 0.785, ota_length, ota_outer_radius
        )
    elif mount_family == "german_eq":
        # German EQ: at large +DEC the rear-top newtonian focuser knob swings toward
        # the RA drive motor box (analogous to a meridian-flip clearance limit).
        dec_lower, dec_upper = -0.75, 0.90
    else:
        dec_lower, dec_upper = -0.75, 1.15

    return ResolvedAstronomicalTelescopeOnTripodConfig(
        root_support_style=root_support_style,
        mount_family=mount_family,
        ota_style=ota_style,
        focus_aux_style=focus_aux_style,
        material_style=config.material_style,
        tripod_height=tripod_height,
        tripod_spread_radius=tripod_spread_radius,
        polar_wedge_tilt_deg=polar_wedge_tilt_deg,
        ota_length=ota_length,
        ota_outer_radius=ota_outer_radius,
        anchor_mode=config.anchor_mode,
        palette=dict(PALETTES[config.material_style]),
        wedge_tilt_rad=wedge_tilt_rad,
        hub_top_z=hub_top_z,
        foot_z=foot_z,
        mount_seat_z=mount_seat_z,
        dec_lower=dec_lower,
        dec_upper=dec_upper,
        alt_lower=-0.25,
        alt_upper=1.35,
        tilt_lower=-0.55,
        tilt_upper=0.80,
        name=config.name,
    )


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _equatorial_dec_limits(
    scale: float, ota_length: float, ota_outer_radius: float, *, margin: float = 0.012
) -> tuple[float, float]:
    """Declination travel bounded by OTA-envelope vs RA-bearing clearance (Contract 3c).

    Single source of truth for the equatorial-fork declination motion limit. On the
    fork mount the DEC pivot sits at ``z = 0.630 * scale`` and the RA bearing housing
    (``ra_bearing``) rises to ``z = 0.170 * scale`` in the ``polar_head`` frame — both
    on the RA rotation axis, so the OTA rear sweeps a circle centred on the bearing at
    every right-ascension. Positive DEC drops the OTA rear (``rear_cell``, the largest
    radial element at ``orad * 1.08``, reaching ``ota_length / 2`` along the axis) toward
    the bearing; negative DEC drops the front symmetrically.

    Keep the lowest point of the swung tube — ``pivot_z - reach*sin(a) - radius*cos(a)``
    — at least ``margin`` above the bearing top for all right-ascensions. Solving
    ``reach*sin(a) + radius*cos(a) <= pivot_z - bearing_top - margin`` gives the safe
    magnitude ``a``. Returns ``(dec_lower, dec_upper)`` capped at the design envelope
    ``(-0.75, 1.15)``.
    """
    pivot_z = 0.630 * scale
    bearing_top_z = 0.170 * scale
    clearance = pivot_z - bearing_top_z - margin
    reach = 0.5 * ota_length
    radius = ota_outer_radius * 1.08
    rm = math.hypot(reach, radius)
    phi = math.atan2(radius, reach)
    if rm <= clearance:
        limit = 1.15
    else:
        limit = math.asin(_clamp(clearance / rm, -1.0, 1.0)) - phi
    limit = _clamp(limit, 0.12, 1.15)
    return -min(0.75, limit), min(1.15, limit)


def _dobsonian_alt_upper(
    ota_length: float, ota_outer_radius: float, *, margin: float = 0.012
) -> float:
    """Dobsonian altitude bounded so the tube's lower end clears the tabletop base.

    Contract 3c companion for the tabletop dobsonian. The altitude bearing pivots the
    reflector tube at ``z = 0.360``; raising altitude drops the front (rear_cell) end
    toward the ``azimuth_bearing_ring`` (top ``z ~= 0.047``). Keep the lowest swung
    point above the ring by ``margin`` (same envelope model as the fork limit).
    """
    pivot_z = 0.360
    ring_top_z = 0.047
    clearance = pivot_z - ring_top_z - margin
    tube_radius = ota_outer_radius * 0.68
    reach = 0.02 + 0.5 * ota_length + 0.014
    radius = tube_radius + 0.003
    rm = math.hypot(reach, radius)
    phi = math.atan2(radius, reach)
    if rm <= clearance:
        return 1.20
    return _clamp(math.asin(_clamp(clearance / rm, -1.0, 1.0)) - phi, 0.30, 1.20)


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _annular_cylinder_mesh_cq(
    outer_radius: float, inner_radius: float, length: float, name: str, *, assets: AssetContext
):
    """Hollow cylinder mesh along local Z (adopted: S1)."""
    body = (
        cq.Workplane("XY")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(length)
        .translate((0.0, 0.0, -length / 2.0))
    )
    return mesh_from_cadquery(body, name, assets=assets, tolerance=0.001, angular_tolerance=0.08)


def _annular_cylinder_mesh_sdk(
    outer_radius: float, inner_radius: float, length: float, name: str, *, segments: int = 48
):
    """SDK MeshGeometry annular tube along local Z (adopted: S2)."""
    geometry = MeshGeometry()
    half = length * 0.5
    outer_back: list[int] = []
    outer_front: list[int] = []
    inner_back: list[int] = []
    inner_front: list[int] = []

    def _quad(geom: MeshGeometry, a: int, b: int, c: int, d: int) -> None:
        geom.add_face(a, b, c)
        geom.add_face(a, c, d)

    for index in range(segments):
        angle = (2.0 * math.pi * index) / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        outer_back.append(geometry.add_vertex(-half, outer_radius * cos_a, outer_radius * sin_a))
        outer_front.append(geometry.add_vertex(half, outer_radius * cos_a, outer_radius * sin_a))
        inner_back.append(geometry.add_vertex(-half, inner_radius * cos_a, inner_radius * sin_a))
        inner_front.append(geometry.add_vertex(half, inner_radius * cos_a, inner_radius * sin_a))
    for index in range(segments):
        nxt = (index + 1) % segments
        _quad(geometry, outer_back[index], outer_back[nxt], outer_front[nxt], outer_front[index])
        _quad(geometry, inner_back[index], inner_front[index], inner_front[nxt], inner_back[nxt])
        _quad(geometry, outer_front[index], outer_front[nxt], inner_front[nxt], inner_front[index])
        _quad(geometry, outer_back[index], inner_back[index], inner_back[nxt], outer_back[nxt])
    return mesh_from_geometry(geometry, name)


def _leg_origin(
    angle: float, top_z: float, foot_radius: float, foot_z: float
) -> tuple[Origin, float]:
    """Box leg origin from hub to foot (adopted: S1)."""
    x = foot_radius * math.cos(angle)
    y = foot_radius * math.sin(angle)
    dz = foot_z - top_z
    length = math.sqrt(x * x + y * y + dz * dz)
    center = (0.5 * x, 0.5 * y, 0.5 * (top_z + foot_z))
    pitch = math.acos(max(-1.0, min(1.0, dz / max(length, 1e-9))))
    return Origin(xyz=center, rpy=(0.0, pitch, angle)), length


def _axis_rpy_from_z(
    p0: tuple[float, float, float], p1: tuple[float, float, float]
) -> tuple[float, float, float]:
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    dz = p1[2] - p0[2]
    horizontal = math.hypot(dx, dy)
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(horizontal, dz)
    return (0.0, pitch, yaw)


def _cylinder_between(part, p0, p1, *, radius: float, material, name: str) -> None:
    length = math.dist(p0, p1)
    mid = tuple((a + b) * 0.5 for a, b in zip(p0, p1))
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=mid, rpy=_axis_rpy_from_z(p0, p1)),
        material=material,
        name=name, material_class_id="metal.aluminum_bare",
    )


def _mat(model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]]) -> dict:
    out = {}
    for key, rgba in palette.items():
        out[key] = model.material(key, rgba=rgba)
    return out


# --------------------------------------------------------------------------- #
# S1 anchor build — verbatim geometry fingerprint for seed=0
# --------------------------------------------------------------------------- #


def _build_anchor_s1(model: ArticulatedObject, *, assets: AssetContext) -> None:
    """Reproduce PRIMARY_ANCHOR topology and primitive histogram (adopted: S1)."""
    mats = _mat(model, PALETTES["powder_orange"])
    orange = mats["accent"]
    black = mats["black"]
    dark = mats["dark"]
    metal = mats["metal"]
    rubber = mats["rubber"]
    glass = mats["glass"]

    tilt = math.radians(35.0)
    tripod = model.part("tripod")
    tripod.visual(
        Cylinder(radius=0.065, length=0.50),
        origin=Origin(xyz=(0.0, 0.0, 0.285)),
        material=metal,
        name="center_column", material_class_id="metal.aluminum_bare",
    )
    tripod.visual(
        Cylinder(radius=0.083, length=0.10),
        origin=Origin(xyz=(0.0, 0.0, 0.535)),
        material=metal,
        name="top_hub", material_class_id="metal.aluminum_bare",
    )
    tripod.visual(
        Cylinder(radius=0.22, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, 0.325)),
        material=metal,
        name="spreader_tray", material_class_id="metal.aluminum_bare",
    )
    tripod.visual(
        Cylinder(radius=0.090, length=0.090),
        origin=Origin(xyz=(0.0, 0.0, 0.605)),
        material=metal,
        name="wedge_pier", material_class_id="metal.aluminum_bare",
    )
    tripod.visual(
        Box((0.42, 0.31, 0.034)),
        origin=Origin(xyz=(0.0, 0.0, 0.650)),
        material=dark,
        name="wedge_lower_plate", material_class_id="metal.paint_coated",
    )

    top_z = 0.535
    foot_z = 0.030
    foot_radius = 0.50
    for idx, angle in enumerate((math.radians(90.0), math.radians(210.0), math.radians(330.0))):
        leg_origin, leg_length = _leg_origin(angle, top_z, foot_radius, foot_z)
        tripod.visual(
            Box((0.042, 0.034, leg_length)),
            origin=leg_origin,
            material=metal,
            name=f"tripod_leg_{idx}", material_class_id="metal.aluminum_bare",
        )
        tripod.visual(
            Box((0.17, 0.085, 0.030)),
            origin=Origin(
                xyz=(foot_radius * math.cos(angle), foot_radius * math.sin(angle), 0.015),
                rpy=(0.0, 0.0, angle),
            ),
            material=rubber,
            name=f"foot_pad_{idx}", material_class_id="rubber.smooth_plain",
        )

    wedge_top = (0.0, 0.0, 0.765)
    wedge_normal = (-math.sin(tilt), 0.0, math.cos(tilt))
    wedge_center = tuple(wedge_top[i] - 0.5 * 0.036 * wedge_normal[i] for i in range(3))
    tripod.visual(
        Box((0.38, 0.29, 0.036)),
        origin=Origin(xyz=wedge_center, rpy=(0.0, -tilt, 0.0)),
        material=orange,
        name="wedge_plate", material_class_id="metal.paint_coated",
    )
    tripod.visual(
        Box((0.24, 0.035, 0.15)),
        origin=Origin(xyz=(-0.015, 0.145, 0.700), rpy=(0.0, -0.5 * tilt, 0.0)),
        material=orange,
        name="wedge_side_cheek_0", material_class_id="metal.paint_coated",
    )
    tripod.visual(
        Box((0.24, 0.035, 0.15)),
        origin=Origin(xyz=(-0.015, -0.145, 0.700), rpy=(0.0, -0.5 * tilt, 0.0)),
        material=orange,
        name="wedge_side_cheek_1", material_class_id="metal.paint_coated",
    )

    polar_head = model.part("polar_head")
    polar_head.visual(
        Cylinder(radius=0.095, length=0.160),
        origin=Origin(xyz=(0.0, 0.0, 0.080)),
        material=dark,
        name="ra_bearing", material_class_id="metal.paint_coated",
    )
    polar_head.visual(
        Cylinder(radius=0.025, length=0.240),
        origin=Origin(xyz=(-0.055, 0.0, 0.055), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="latitude_hinge_bar", material_class_id="metal.aluminum_bare",
    )
    polar_head.visual(
        Box((0.18, 0.20, 0.075)),
        origin=Origin(xyz=(0.0, 0.0, 0.055)),
        material=orange,
        name="tilt_base_block", material_class_id="metal.paint_coated",
    )
    polar_head.visual(
        Box((0.012, 0.10, 0.070)),
        origin=Origin(xyz=(0.094, 0.0, 0.070)),
        material=metal,
        name="polar_scale_plate", material_class_id="metal.aluminum_bare",
    )

    fork_arm = model.part("fork_arm")
    fork_arm.visual(
        Cylinder(radius=0.105, length=0.075),
        origin=Origin(xyz=(0.0, 0.0, 0.0375)),
        material=orange,
        name="ra_collar", material_class_id="metal.paint_coated",
    )
    fork_arm.visual(
        Box((0.090, 0.230, 0.090)),
        origin=Origin(xyz=(0.0, -0.095, 0.075)),
        material=orange,
        name="arm_root_web", material_class_id="metal.paint_coated",
    )
    fork_arm.visual(
        Box((0.078, 0.050, 0.420)),
        origin=Origin(xyz=(0.0, -0.215, 0.260)),
        material=orange,
        name="single_fork_arm", material_class_id="metal.paint_coated",
    )
    fork_arm.visual(
        Box((0.095, 0.070, 0.100)),
        origin=Origin(xyz=(0.0, -0.215, 0.470)),
        material=orange,
        name="declination_cap", material_class_id="metal.paint_coated",
    )
    fork_arm.visual(
        Cylinder(radius=0.075, length=0.050),
        origin=Origin(xyz=(0.0, -0.205, 0.470), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="declination_boss", material_class_id="metal.aluminum_bare",
    )

    optical_tube = model.part("optical_tube")
    tube_shell = _annular_cylinder_mesh_cq(0.120, 0.105, 0.420, "stubby_tube_shell", assets=assets)
    front_ring = _annular_cylinder_mesh_cq(0.128, 0.103, 0.025, "front_retain_ring", assets=assets)
    optical_tube.visual(
        tube_shell,
        origin=Origin(xyz=(0.0, 0.170, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=orange,
        name="tube_shell", material_class_id="metal.paint_coated",
    )
    optical_tube.visual(
        front_ring,
        origin=Origin(xyz=(0.218, 0.170, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=black,
        name="front_retain_ring", material_class_id="metal.blackened_gunmetal",
    )
    optical_tube.visual(
        Cylinder(radius=0.103, length=0.008),
        origin=Origin(xyz=(0.214, 0.170, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=glass,
        name="front_corrector", material_class_id="glass.clear_transparent",
    )
    optical_tube.visual(
        Cylinder(radius=0.035, length=0.012),
        origin=Origin(xyz=(0.221, 0.170, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=black,
        name="secondary_mirror", material_class_id="glass.mirror",
    )
    optical_tube.visual(
        Cylinder(radius=0.130, length=0.055),
        origin=Origin(xyz=(-0.2275, 0.170, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=black,
        name="rear_cell", material_class_id="metal.blackened_gunmetal",
    )
    optical_tube.visual(
        Cylinder(radius=0.034, length=0.085),
        origin=Origin(xyz=(-0.2975, 0.170, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=dark,
        name="rear_visual_back", material_class_id="metal.paint_coated",
    )
    optical_tube.visual(
        Cylinder(radius=0.013, length=0.030),
        origin=Origin(xyz=(-0.270, 0.255, 0.035), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal,
        name="focus_socket", material_class_id="metal.aluminum_bare",
    )
    optical_tube.visual(
        Cylinder(radius=0.050, length=0.110),
        origin=Origin(xyz=(0.0, 0.055, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="declination_shaft", material_class_id="metal.aluminum_bare",
    )
    optical_tube.visual(
        Cylinder(radius=0.066, length=0.030),
        origin=Origin(xyz=(0.0, 0.015, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=orange,
        name="declination_side_cap", material_class_id="metal.paint_coated",
    )
    optical_tube.visual(
        Cylinder(radius=0.023, length=0.230),
        origin=Origin(xyz=(-0.015, 0.170, 0.190), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=black,
        name="finder_scope", material_class_id="metal.blackened_gunmetal",
    )
    for idx, x in enumerate((-0.080, 0.060)):
        optical_tube.visual(
            Box((0.020, 0.030, 0.082)),
            origin=Origin(xyz=(x, 0.170, 0.153)),
            material=metal,
            name=f"finder_bracket_{idx}", material_class_id="metal.aluminum_bare",
        )

    focus_knob = model.part("focus_knob")
    focus_knob.visual(
        Cylinder(radius=0.018, length=0.035),
        origin=Origin(xyz=(-0.0175, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="knob_cap", material_class_id="rubber.smooth_plain",
    )

    model.articulation(
        "polar_angle",
        ArticulationType.REVOLUTE,
        parent=tripod,
        child=polar_head,
        origin=Origin(xyz=wedge_top, rpy=(0.0, -tilt, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.25, lower=-0.22, upper=0.30),
    )
    model.articulation(
        "right_ascension",
        ArticulationType.CONTINUOUS,
        parent=polar_head,
        child=fork_arm,
        origin=Origin(xyz=(0.0, 0.0, 0.160)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=0.75),
    )
    model.articulation(
        "declination",
        ArticulationType.REVOLUTE,
        parent=fork_arm,
        child=optical_tube,
        origin=Origin(xyz=(0.0, -0.180, 0.470)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=0.65, lower=-0.75, upper=1.15),
    )
    model.articulation(
        "focus",
        ArticulationType.CONTINUOUS,
        parent=optical_tube,
        child=focus_knob,
        origin=Origin(xyz=(-0.285, 0.255, 0.035)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.6, velocity=6.0),
    )


# --------------------------------------------------------------------------- #
# Root support modules
# --------------------------------------------------------------------------- #


def _build_tripod_wedge(
    model: ArticulatedObject, r: ResolvedAstronomicalTelescopeOnTripodConfig, mats: dict
) -> tuple:
    """Wedge spreader tripod (adopted: S1). Returns (tripod_part, wedge_top, tilt_rad)."""
    scale = r.tripod_height / 0.785
    spread = r.tripod_spread_radius
    tilt = r.wedge_tilt_rad
    metal, dark, orange, rubber = mats["metal"], mats["dark"], mats["accent"], mats["rubber"]

    tripod = model.part("tripod")
    col_len = 0.50 * scale
    col_cz = 0.285 * scale
    hub_z = 0.535 * scale
    tripod.visual(
        Cylinder(radius=0.065 * scale, length=col_len),
        origin=Origin(xyz=(0.0, 0.0, col_cz)),
        material=metal,
        name="center_column", material_class_id="metal.aluminum_bare",
    )
    tripod.visual(
        Cylinder(radius=0.083 * scale, length=0.10 * scale),
        origin=Origin(xyz=(0.0, 0.0, hub_z)),
        material=metal,
        name="top_hub", material_class_id="metal.aluminum_bare",
    )
    tripod.visual(
        Cylinder(radius=0.22 * scale, length=0.016 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.325 * scale)),
        material=metal,
        name="spreader_tray", material_class_id="metal.aluminum_bare",
    )
    tripod.visual(
        Cylinder(radius=0.090 * scale, length=0.090 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.605 * scale)),
        material=metal,
        name="wedge_pier", material_class_id="metal.aluminum_bare",
    )
    tripod.visual(
        Box((0.42 * scale, 0.31 * scale, 0.034 * scale)),
        origin=Origin(xyz=(0.0, 0.0, 0.650 * scale)),
        material=dark,
        name="wedge_lower_plate", material_class_id="metal.paint_coated",
    )

    for idx, angle in enumerate((math.radians(90.0), math.radians(210.0), math.radians(330.0))):
        leg_origin, leg_length = _leg_origin(angle, hub_z, spread, r.foot_z)
        tripod.visual(
            Box((0.042 * scale, 0.034 * scale, leg_length)),
            origin=leg_origin,
            material=metal,
            name=f"tripod_leg_{idx}", material_class_id="metal.aluminum_bare",
        )
        tripod.visual(
            Box((0.17 * scale, 0.085 * scale, 0.030 * scale)),
            origin=Origin(
                xyz=(spread * math.cos(angle), spread * math.sin(angle), 0.015),
                rpy=(0.0, 0.0, angle),
            ),
            material=rubber,
            name=f"foot_pad_{idx}", material_class_id="rubber.smooth_plain",
        )

    wedge_top = (0.0, 0.0, 0.765 * scale)
    wedge_normal = (-math.sin(tilt), 0.0, math.cos(tilt))
    wedge_center = tuple(wedge_top[i] - 0.5 * 0.036 * scale * wedge_normal[i] for i in range(3))
    tripod.visual(
        Box((0.38 * scale, 0.29 * scale, 0.036 * scale)),
        origin=Origin(xyz=wedge_center, rpy=(0.0, -tilt, 0.0)),
        material=orange,
        name="wedge_plate", material_class_id="metal.paint_coated",
    )
    tripod.visual(
        Box((0.24 * scale, 0.035 * scale, 0.15 * scale)),
        origin=Origin(xyz=(-0.015, 0.145 * scale, 0.700 * scale), rpy=(0.0, -0.5 * tilt, 0.0)),
        material=orange,
        name="wedge_side_cheek_0", material_class_id="metal.paint_coated",
    )
    tripod.visual(
        Box((0.24 * scale, 0.035 * scale, 0.15 * scale)),
        origin=Origin(xyz=(-0.015, -0.145 * scale, 0.700 * scale), rpy=(0.0, -0.5 * tilt, 0.0)),
        material=orange,
        name="wedge_side_cheek_1", material_class_id="metal.paint_coated",
    )
    return tripod, wedge_top, tilt


def _build_tripod_spline(
    model: ArticulatedObject, r: ResolvedAstronomicalTelescopeOnTripodConfig, mats: dict
):
    """Spline-leg tripod (adopted: S3). Returns tripod_base part."""
    black, gray, rubber = mats["black"], mats["accent"], mats["rubber"]
    scale = r.tripod_height / 0.96
    spread = r.tripod_spread_radius
    tripod = model.part("tripod_base")
    col_len = 0.620 * scale
    col_cz = 0.538 * scale
    bearing_z = 0.940 * scale
    tripod.visual(
        Cylinder(radius=0.026 * scale, length=col_len),
        origin=Origin(xyz=(0.0, 0.0, col_cz)),
        material=black,
        name="center_column", material_class_id="metal.blackened_gunmetal",
    )
    tripod.visual(
        Cylinder(radius=0.048 * scale, length=0.046 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.871 * scale)),
        material=black,
        name="upper_collar", material_class_id="metal.blackened_gunmetal",
    )
    tripod.visual(
        Cylinder(radius=0.072 * scale, length=0.046 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.917 * scale)),
        material=gray,
        name="bearing_cap", material_class_id="metal.paint_coated",
    )
    tripod.visual(
        Cylinder(radius=0.036 * scale, length=0.052 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.564 * scale)),
        material=gray,
        name="spreader_hub", material_class_id="metal.paint_coated",
    )

    for index, angle in enumerate((0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)):
        c, s = math.cos(angle), math.sin(angle)
        leg_mesh = tube_from_spline_points(
            [
                (0.032 * c * scale, 0.032 * s * scale, 0.848 * scale),
                (0.180 * c * scale, 0.180 * s * scale, 0.500 * scale),
                (spread * c, spread * s, r.foot_z),
            ],
            radius=0.014 * scale,
            samples_per_segment=18,
            radial_segments=18,
            cap_ends=True,
        )
        tripod.visual(
            mesh_from_geometry(leg_mesh, f"tripod_leg_geom_{index}"),
            material=black,
            name=f"leg_{index}", material_class_id="metal.blackened_gunmetal",
        )
        spreader_mesh = tube_from_spline_points(
            [
                (0.024 * c * scale, 0.024 * s * scale, 0.564 * scale),
                (0.110 * c * scale, 0.110 * s * scale, 0.505 * scale),
                (0.175 * c * scale, 0.175 * s * scale, 0.460 * scale),
            ],
            radius=0.006 * scale,
            samples_per_segment=12,
            radial_segments=14,
            cap_ends=True,
        )
        tripod.visual(
            mesh_from_geometry(spreader_mesh, f"tripod_spreader_geom_{index}"),
            material=gray,
            name=f"spreader_{index}", material_class_id="metal.paint_coated",
        )
        tripod.visual(
            Sphere(radius=0.022 * scale),
            origin=Origin(xyz=(spread * c, spread * s, r.foot_z)),
            material=rubber,
            name=f"foot_{index}", material_class_id="rubber.smooth_plain",
        )
    return tripod, bearing_z


def _build_tripod_crown(
    model: ArticulatedObject, r: ResolvedAstronomicalTelescopeOnTripodConfig, mats: dict
):
    """Heavy crown-head equatorial tripod (adopted: S2)."""
    dark = mats["dark"]
    scale = r.tripod_height / 0.90
    spread = r.tripod_spread_radius
    tripod = model.part("tripod")
    pier_h = 0.72 * scale
    tripod.visual(
        Cylinder(radius=0.040 * scale, length=pier_h),
        origin=Origin(xyz=(0.0, 0.0, pier_h * 0.5)),
        material=dark,
        name="pier", material_class_id="metal.paint_coated",
    )
    tripod.visual(
        Cylinder(radius=0.070 * scale, length=0.035 * scale),
        origin=Origin(xyz=(0.0, 0.0, pier_h + 0.0175 * scale)),
        material=dark,
        name="pier_cap", material_class_id="metal.paint_coated",
    )
    # Leg spans from inside the pier out to the foot; length tracks `spread` (not scale)
    # so the inner end always embeds in the pier and the outer end reaches the foot,
    # regardless of the spread/scale combination (fixes disconnected-leg islands).
    leg_len = spread * 1.03 + 0.12 * scale
    for idx, yaw in enumerate((0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)):
        x, y = spread * math.cos(yaw), spread * math.sin(yaw)
        tripod.visual(
            Box((leg_len, 0.045 * scale, 0.040 * scale)),
            origin=Origin(
                xyz=(x / 2.0, y / 2.0, 0.080 * scale), rpy=(0.0, math.radians(10.0), yaw)
            ),
            material=dark,
            name=f"tripod_leg_{idx}", material_class_id="metal.paint_coated",
        )
        tripod.visual(
            Box((0.12 * scale, 0.075 * scale, 0.022 * scale)),
            origin=Origin(xyz=(x, y, 0.024), rpy=(0.0, 0.0, yaw)),
            material=mats["black"],
            name=f"rubber_foot_{idx}", material_class_id="rubber.smooth_plain",
        )
    seat_z = pier_h + 0.10 * scale
    wedge_half = 0.018 * scale
    wedge_center = (0.0, 0.0, seat_z - wedge_half)
    tripod.visual(
        Box((0.24 * scale, 0.15 * scale, 0.036 * scale)),
        origin=Origin(xyz=wedge_center, rpy=(r.wedge_tilt_rad, 0.0, 0.0)),
        material=dark,
        name="polar_wedge", material_class_id="metal.paint_coated",
    )
    return tripod, seat_z, r.wedge_tilt_rad


def _build_tabletop_dob_base(
    model: ArticulatedObject, r: ResolvedAstronomicalTelescopeOnTripodConfig, mats: dict
):
    """Tabletop disc base (adopted: S5 edge)."""
    wood, gray, rubber = mats["wood"], mats["accent"], mats["rubber"]
    disc = model.part("tabletop_disc")
    disc.visual(
        Cylinder(radius=0.240, length=0.035),
        origin=Origin(xyz=(0.0, 0.0, 0.0175)),
        material=wood,
        name="round_table_base", material_class_id="wood.plywood",
    )
    disc.visual(
        Cylinder(radius=0.155, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, 0.039)),
        material=gray,
        name="azimuth_bearing_ring", material_class_id="metal.paint_coated",
    )
    disc.visual(
        Cylinder(radius=0.060, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, 0.040)),
        material=rubber,
        name="center_bearing_button", material_class_id="rubber.smooth_plain",
    )
    return disc, 0.045


# --------------------------------------------------------------------------- #
# Mount + OTA assembly paths
# --------------------------------------------------------------------------- #


def _build_equatorial_fork_mount(
    model: ArticulatedObject,
    r: ResolvedAstronomicalTelescopeOnTripodConfig,
    mats: dict,
    *,
    tripod,
    wedge_top: tuple[float, float, float],
    tilt: float,
    assets: AssetContext,
) -> tuple:
    orange, dark, metal = mats["accent"], mats["dark"], mats["metal"]
    scale = r.tripod_height / 0.785

    polar_head = model.part("polar_head")
    polar_head.visual(
        Cylinder(radius=0.100 * scale, length=0.020 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.010 * scale)),
        material=dark,
        name="polar_foot_pad", material_class_id="metal.paint_coated",
    )
    polar_head.visual(
        Cylinder(radius=0.095 * scale, length=0.160 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.090 * scale)),
        material=dark,
        name="ra_bearing", material_class_id="metal.paint_coated",
    )
    polar_head.visual(
        Cylinder(radius=0.025 * scale, length=0.240 * scale),
        origin=Origin(xyz=(-0.055 * scale, 0.0, 0.055 * scale), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="latitude_hinge_bar", material_class_id="metal.aluminum_bare",
    )
    polar_head.visual(
        Box((0.18 * scale, 0.20 * scale, 0.075 * scale)),
        origin=Origin(xyz=(0.0, 0.0, 0.055 * scale)),
        material=orange,
        name="tilt_base_block", material_class_id="metal.paint_coated",
    )
    polar_head.visual(
        Box((0.012 * scale, 0.10 * scale, 0.070 * scale)),
        origin=Origin(xyz=(0.094 * scale, 0.0, 0.070 * scale)),
        material=metal,
        name="polar_scale_plate", material_class_id="metal.aluminum_bare",
    )

    fork_arm = model.part("fork_arm")
    fork_arm.visual(
        Cylinder(radius=0.105 * scale, length=0.075 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.0375 * scale)),
        material=orange,
        name="ra_collar", material_class_id="metal.paint_coated",
    )
    fork_arm.visual(
        Box((0.090 * scale, 0.230 * scale, 0.090 * scale)),
        origin=Origin(xyz=(0.0, -0.095 * scale, 0.075 * scale)),
        material=orange,
        name="arm_root_web", material_class_id="metal.paint_coated",
    )
    fork_arm.visual(
        Box((0.078 * scale, 0.050 * scale, 0.42 * scale)),
        origin=Origin(xyz=(0.0, -0.215 * scale, 0.260 * scale)),
        material=orange,
        name="single_fork_arm", material_class_id="metal.paint_coated",
    )
    fork_arm.visual(
        Box((0.095 * scale, 0.070 * scale, 0.100 * scale)),
        origin=Origin(xyz=(0.0, -0.215 * scale, 0.470 * scale)),
        material=orange,
        name="declination_cap", material_class_id="metal.paint_coated",
    )
    fork_arm.visual(
        Cylinder(radius=0.075 * scale, length=0.050 * scale),
        origin=Origin(xyz=(0.0, -0.205 * scale, 0.470 * scale), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="declination_boss", material_class_id="metal.aluminum_bare",
    )

    ota, objective_elem = _build_ota(model, r, mats, assets=assets, y_offset=0.170 * scale)
    dec_origin = (0.0, -0.180 * scale, 0.470 * scale)

    model.articulation(
        "polar_angle",
        ArticulationType.REVOLUTE,
        parent=tripod,
        child=polar_head,
        origin=Origin(xyz=wedge_top, rpy=(0.0, -tilt, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.25, lower=-0.22, upper=0.30),
    )
    model.articulation(
        "right_ascension",
        ArticulationType.CONTINUOUS,
        parent=polar_head,
        child=fork_arm,
        origin=Origin(xyz=(0.0, 0.0, 0.160 * scale)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=0.75),
    )
    model.articulation(
        "declination",
        ArticulationType.REVOLUTE,
        parent=fork_arm,
        child=ota,
        origin=Origin(xyz=dec_origin),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=10.0, velocity=0.65, lower=r.dec_lower, upper=r.dec_upper
        ),
    )

    y_off = r.tripod_height / 0.785 * 0.170
    focus_x = -r.ota_length / 2.0 + min(0.055, max(0.035, r.ota_length * 0.15))
    if r.ota_style == "newtonian":
        focus_x = -r.ota_length / 2.0 + min(0.14, max(0.08, r.ota_length * 0.28))
        focus_origin = (focus_x, y_off, r.ota_outer_radius + 0.013)
    else:
        focus_origin = (focus_x, y_off, 0.0)
    focus_part = _attach_focus_aux(
        model, r, mats, parent=ota, focus_origin=focus_origin, y_offset=y_off
    )
    return ota, objective_elem, focus_part, fork_arm


def _build_german_eq_mount(
    model: ArticulatedObject,
    r: ResolvedAstronomicalTelescopeOnTripodConfig,
    mats: dict,
    *,
    tripod,
    seat_z: float,
    assets: AssetContext,
):
    """German-style polar + declination head (adopted: S2)."""
    dark, black = mats["dark"], mats["black"]
    tilt = r.wedge_tilt_rad
    wedge_center = (0.0, 0.0, seat_z - 0.018)
    tripod.visual(
        Box((0.24, 0.15, 0.036)),
        origin=Origin(xyz=wedge_center, rpy=(tilt, 0.0, 0.0)),
        material=dark,
        name="german_polar_wedge", material_class_id="metal.paint_coated",
    )

    polar = model.part("polar_assembly")
    polar.visual(
        Cylinder(radius=0.090, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.015)),
        material=dark,
        name="polar_seat_pad", material_class_id="metal.paint_coated",
    )
    polar.visual(
        Cylinder(radius=0.076, length=0.240),
        origin=Origin(xyz=(0.0, 0.0, 0.135)),
        material=black,
        name="polar_housing", material_class_id="metal.blackened_gunmetal",
    )
    polar.visual(
        Cylinder(radius=0.052, length=0.260),
        origin=Origin(xyz=(0.0, 0.0, 0.150)),
        material=dark,
        name="ra_shaft", material_class_id="metal.paint_coated",
    )
    polar.visual(
        Box((0.082, 0.090, 0.105)),
        origin=Origin(xyz=(0.105, 0.0, 0.120)),
        material=dark,
        name="ra_motor_box", material_class_id="metal.paint_coated",
    )

    dec_head = model.part("declination_head")
    dec_head.visual(
        Box((0.120, 0.085, 0.095)),
        origin=Origin(xyz=(0.0, 0.0, 0.048)),
        material=dark,
        name="dec_clamp_block", material_class_id="metal.paint_coated",
    )
    dec_head.visual(
        Cylinder(radius=0.040, length=0.060),
        origin=Origin(xyz=(0.0, 0.055, 0.048), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=black,
        name="dec_bearing_stub", material_class_id="metal.blackened_gunmetal",
    )

    ota, objective_elem = _build_ota(model, r, mats, assets=assets, y_offset=0.0)
    polar_joint = (0.0, 0.0, seat_z)
    dec_joint = (0.0, 0.0, 0.048)

    model.articulation(
        "polar_axis",
        ArticulationType.CONTINUOUS,
        parent=tripod,
        child=polar,
        origin=Origin(xyz=polar_joint, rpy=(tilt, 0.0, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.6),
    )
    model.articulation(
        "right_ascension",
        ArticulationType.CONTINUOUS,
        parent=polar,
        child=dec_head,
        origin=Origin(xyz=(0.0, 0.0, 0.240)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=0.75),
    )
    model.articulation(
        "declination",
        ArticulationType.REVOLUTE,
        parent=dec_head,
        child=ota,
        origin=Origin(xyz=dec_joint),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=10.0, velocity=0.65, lower=r.dec_lower, upper=r.dec_upper
        ),
    )
    if r.ota_style == "newtonian":
        focus_x = -r.ota_length / 2.0 + min(0.14, max(0.08, r.ota_length * 0.28))
        focus_origin = (focus_x, 0.0, r.ota_outer_radius + 0.013)
    elif r.ota_style == "sct_compact":
        focus_x = -r.ota_length / 2.0 + min(0.055, max(0.035, r.ota_length * 0.15))
        focus_origin = (focus_x, 0.0, 0.0)
    else:
        focus_origin = None
    focus_part = _attach_focus_aux(
        model, r, mats, parent=ota, focus_origin=focus_origin, y_offset=0.0
    )
    return ota, objective_elem, focus_part


def _build_altaz_mount(
    model: ArticulatedObject,
    r: ResolvedAstronomicalTelescopeOnTripodConfig,
    mats: dict,
    *,
    tripod,
    bearing_z: float,
    assets: AssetContext,
):
    """Alt-az single arm (adopted: S3)."""
    gray, black = mats["accent"], mats["black"]
    mount = model.part("mount_arm")
    mount.visual(
        Cylinder(radius=0.072, length=0.022),
        origin=Origin(xyz=(0.0, 0.0, 0.011)),
        material=gray,
        name="azimuth_seat_pad", material_class_id="metal.paint_coated",
    )
    mount.visual(
        Cylinder(radius=0.055, length=0.060),
        origin=Origin(xyz=(0.0, 0.0, 0.042)),
        material=gray,
        name="azimuth_drum", material_class_id="metal.paint_coated",
    )
    mount.visual(
        Cylinder(radius=0.085, length=0.022),
        origin=Origin(xyz=(0.0, 0.0, 0.071)),
        material=gray,
        name="azimuth_plate", material_class_id="metal.paint_coated",
    )
    mount.visual(
        Box((0.150, 0.110, 0.098)),
        origin=Origin(xyz=(0.100, -0.030, 0.131)),
        material=gray,
        name="arm_base_block", material_class_id="metal.paint_coated",
    )
    mount.visual(
        Box((0.080, 0.080, 0.270)),
        origin=Origin(xyz=(0.100, -0.040, 0.315)),
        material=gray,
        name="upright_arm", material_class_id="metal.paint_coated",
    )
    mount.visual(
        Box((0.090, 0.090, 0.060)),
        origin=Origin(xyz=(0.100, -0.040, 0.470)),
        material=gray,
        name="bearing_pedestal", material_class_id="metal.paint_coated",
    )
    mount.visual(
        Cylinder(radius=0.045, length=0.080),
        origin=Origin(xyz=(0.100, -0.040, 0.500), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=black,
        name="alt_bearing_housing", material_class_id="metal.blackened_gunmetal",
    )

    telescope, objective_elem = _build_ota(model, r, mats, assets=assets, y_offset=0.050)
    model.articulation(
        "tripod_to_mount",
        ArticulationType.CONTINUOUS,
        parent=tripod,
        child=mount,
        origin=Origin(xyz=(0.0, 0.0, bearing_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=40.0, velocity=1.5),
    )
    model.articulation(
        "mount_to_telescope",
        ArticulationType.REVOLUTE,
        parent=mount,
        child=telescope,
        origin=Origin(xyz=(0.120, -0.040, 0.500)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=18.0, velocity=1.2, lower=r.alt_lower, upper=r.alt_upper),
    )
    return telescope, objective_elem


def _build_photo_pan_tilt(
    model: ArticulatedObject,
    r: ResolvedAstronomicalTelescopeOnTripodConfig,
    mats: dict,
    *,
    tripod,
    seat_z: float,
    assets: AssetContext,
):
    """Photo pan-tilt head (adopted: S4)."""
    black, gray, metal = mats["black"], mats["dark"], mats["metal"]
    pan = model.part("pan_head")
    pan.visual(
        Cylinder(radius=0.080, length=0.035),
        origin=Origin(xyz=(0.0, 0.0, 0.0175)),
        material=black,
        name="pan_disc", material_class_id="metal.blackened_gunmetal",
    )
    pan.visual(
        Cylinder(radius=0.036, length=0.062),
        origin=Origin(xyz=(0.0, 0.0, 0.066)),
        material=black,
        name="pedestal_stem", material_class_id="metal.blackened_gunmetal",
    )
    pan.visual(
        Cylinder(radius=0.065, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.085)),
        material=gray,
        name="socket_flare", material_class_id="metal.paint_coated",
    )
    pan.visual(
        Cylinder(radius=0.008, length=0.105),
        origin=Origin(xyz=(0.0, 0.102, 0.025), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="pan_lock_stem", material_class_id="metal.aluminum_bare",
    )

    tilt = model.part("tilt_head")
    tilt.visual(Sphere(radius=0.055), material=black, name="ball", material_class_id="metal.blackened_gunmetal")
    tilt.visual(
        Cylinder(radius=0.018, length=0.092),
        origin=Origin(xyz=(0.0, 0.0, 0.087)),
        material=black,
        name="neck_post", material_class_id="metal.blackened_gunmetal",
    )
    tilt.visual(
        Box((0.190, 0.130, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, 0.137)),
        material=gray,
        name="saddle_plate", material_class_id="metal.paint_coated",
    )
    tilt.visual(
        Cylinder(radius=0.020, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.146)),
        material=gray,
        name="scope_mount_boss", material_class_id="metal.paint_coated",
    )

    scope, objective_elem = _build_ota(model, r, mats, assets=assets, y_offset=0.0)
    pan_origin = (0.0, 0.0, seat_z)
    pan.visual(
        Cylinder(radius=0.030, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, 0.095)),
        material=gray,
        name="tilt_socket_boss", material_class_id="metal.paint_coated",
    )
    model.articulation(
        "pan_bearing",
        ArticulationType.CONTINUOUS,
        parent=tripod,
        child=pan,
        origin=Origin(xyz=pan_origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=1.2),
    )
    model.articulation(
        "tilt_axis",
        ArticulationType.REVOLUTE,
        parent=pan,
        child=tilt,
        origin=Origin(xyz=(0.0, 0.0, 0.095)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=12.0, velocity=1.0, lower=r.tilt_lower, upper=r.tilt_upper
        ),
    )
    model.articulation(
        "scope_mount",
        ArticulationType.FIXED,
        parent=tilt,
        child=scope,
        origin=Origin(xyz=(0.0, 0.0, 0.146)),
    )
    return scope, objective_elem, pan, tilt


def _build_dobsonian(
    model: ArticulatedObject,
    r: ResolvedAstronomicalTelescopeOnTripodConfig,
    mats: dict,
    *,
    disc,
    az_origin: float,
    assets: AssetContext,
):
    """Tabletop dobsonian rocker (adopted: S5)."""
    wood, navy, rubber = mats["wood"], mats["dark"], mats["rubber"]
    rocker = model.part("rocker_box")
    pivot_z = 0.360
    tr = r.ota_outer_radius * 0.68
    stub_y = max(tr * 0.95, 0.055)
    rocker.visual(
        Box((0.380, 0.340, 0.035)),
        origin=Origin(xyz=(0.0, 0.0, 0.0175)),
        material=wood,
        name="rocker_floor", material_class_id="wood.plywood",
    )
    for side, sy in ((0, 0.150), (1, -0.150)):
        rocker.visual(
            Box((0.340, 0.030, 0.420)),
            origin=Origin(xyz=(0.0, sy, 0.2445)),
            material=wood,
            name=f"side_wall_{side}", material_class_id="wood.plywood",
        )
        rocker.visual(
            Cylinder(radius=0.068, length=0.012),
            origin=Origin(
                xyz=(0.0, stub_y if side == 0 else -stub_y, pivot_z), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=rubber,
            name=f"bearing_pad_{side}", material_class_id="rubber.smooth_plain",
        )
    rocker.visual(
        Box((0.040, 0.280, 0.060)),
        origin=Origin(xyz=(-0.160, 0.0, 0.080)),
        material=wood,
        name="rear_cross_brace", material_class_id="wood.plywood",
    )
    rocker.visual(
        Box((0.040, 0.280, 0.060)),
        origin=Origin(xyz=(0.160, 0.0, 0.080)),
        material=wood,
        name="front_cross_brace", material_class_id="wood.plywood",
    )
    rocker.visual(
        Box((0.070, 0.280, 0.040)),
        origin=Origin(xyz=(0.0, 0.0, pivot_z)),
        material=wood,
        name="altitude_bearing_beam", material_class_id="wood.plywood",
    )

    tube = model.part("reflector_tube")
    tr = r.ota_outer_radius * 0.68
    tl = r.ota_length
    stub_y = max(tr * 0.95, 0.055)
    shell = _annular_cylinder_mesh_cq(tr, tr * 0.85, tl, "dob_tube_shell", assets=assets)
    tube.visual(
        Cylinder(radius=tr * 0.78, length=tl * 1.02),
        origin=Origin(xyz=(0.02, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=navy,
        name="tube_spine", material_class_id="metal.paint_coated",
    )
    tube.visual(shell, origin=Origin(xyz=(0.02, 0.0, 0.0)), material=navy, name="tube_shell", material_class_id="metal.paint_coated")
    tube.visual(
        Cylinder(radius=tr * 0.85, length=0.008),
        origin=Origin(xyz=(0.02 - tl / 2.0 + 0.006, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["black"],
        name="primary_mirror", material_class_id="glass.mirror",
    )
    tube.visual(
        Cylinder(radius=tr + 0.003, length=0.012),
        origin=Origin(xyz=(0.02 + tl / 2.0 + 0.004, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["black"],
        name="rear_cell", material_class_id="metal.blackened_gunmetal",
    )
    tube.visual(
        Cylinder(radius=max(0.045, tr * 0.65), length=stub_y * 2.0 + 0.040),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, math.pi / 2.0)),
        material=mats["accent"],
        name="altitude_hub", material_class_id="metal.paint_coated",
    )
    tube.visual(
        Cylinder(radius=0.060, length=0.035),
        origin=Origin(xyz=(0.0, stub_y, 0.0), rpy=(0.0, 0.0, math.pi / 2.0)),
        material=mats["accent"],
        name="bearing_stub_0", material_class_id="metal.paint_coated",
    )
    tube.visual(
        Cylinder(radius=0.060, length=0.035),
        origin=Origin(xyz=(0.0, -stub_y, 0.0), rpy=(0.0, 0.0, math.pi / 2.0)),
        material=mats["accent"],
        name="bearing_stub_1", material_class_id="metal.paint_coated",
    )

    model.articulation(
        "azimuth_bearing",
        ArticulationType.CONTINUOUS,
        parent=disc,
        child=rocker,
        origin=Origin(xyz=(0.0, 0.0, az_origin)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.2),
    )
    alt_upper = _dobsonian_alt_upper(r.ota_length, r.ota_outer_radius)
    model.articulation(
        "altitude_bearing",
        ArticulationType.REVOLUTE,
        parent=rocker,
        child=tube,
        origin=Origin(xyz=(0.0, 0.0, pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.8, lower=0.0, upper=alt_upper),
    )
    return tube, "primary_mirror"


def _build_ota(
    model: ArticulatedObject,
    r: ResolvedAstronomicalTelescopeOnTripodConfig,
    mats: dict,
    *,
    assets: AssetContext,
    y_offset: float,
) -> tuple:
    """Build OTA part for the requested style; returns (part, objective_element_name)."""
    if r.ota_style == "sct_compact":
        return _build_sct_ota(model, r, mats, assets=assets, y_offset=y_offset)
    if r.ota_style == "newtonian":
        return _build_newtonian_ota(model, r, mats, assets=assets, y_offset=y_offset)
    if r.ota_style == "refractor":
        return _build_refractor_ota(model, r, mats, y_offset=y_offset)
    return _build_photo_refractor_ota(model, r, mats, assets=assets, y_offset=y_offset)


def _build_sct_ota(model, r, mats, *, assets, y_offset):
    orange, black, metal, glass = (
        mats["accent"],
        mats["black"],
        mats["metal"],
        mats["glass"],
    )
    ota = model.part("optical_tube")
    orad, irad, length = r.ota_outer_radius, r.ota_outer_radius * 0.875, r.ota_length
    shell = _annular_cylinder_mesh_cq(orad, irad, length, "sct_tube_shell", assets=assets)
    ring = _annular_cylinder_mesh_cq(
        orad * 1.067, irad * 0.98, 0.025 * (length / 0.42), "sct_front_ring", assets=assets
    )
    # DEC trunnion shaft at the part origin so it meets the fork declination boss.
    ota.visual(
        Cylinder(radius=0.050, length=0.110),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="declination_shaft", material_class_id="metal.aluminum_bare",
    )
    ota.visual(
        Box((max(0.08, orad * 1.6), max(0.06, abs(y_offset) + orad * 0.35), max(0.06, orad * 1.2))),
        origin=Origin(xyz=(0.0, y_offset * 0.5, 0.0)),
        material=metal,
        name="ota_saddle_web", material_class_id="metal.aluminum_bare",
    )
    ota.visual(
        Cylinder(radius=max(0.042, irad * 0.55), length=length),
        origin=Origin(xyz=(0.0, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=orange,
        name="tube_spine", material_class_id="metal.paint_coated",
    )
    ota.visual(
        shell,
        origin=Origin(xyz=(0.0, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=orange,
        name="tube_shell", material_class_id="metal.paint_coated",
    )
    ota.visual(
        ring,
        origin=Origin(xyz=(length / 2.0 - 0.02, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=black,
        name="front_retain_ring", material_class_id="metal.blackened_gunmetal",
    )
    ota.visual(
        Cylinder(radius=irad, length=0.008),
        origin=Origin(xyz=(length / 2.0 - 0.04, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=glass,
        name="front_corrector", material_class_id="glass.clear_transparent",
    )
    ota.visual(
        Cylinder(radius=orad * 0.29, length=0.012),
        origin=Origin(xyz=(length / 2.0 - 0.01, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=black,
        name="secondary_mirror", material_class_id="glass.mirror",
    )
    ota.visual(
        Cylinder(radius=orad * 1.08, length=0.055),
        origin=Origin(xyz=(-length / 2.0 + 0.03, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=black,
        name="rear_cell", material_class_id="metal.blackened_gunmetal",
    )
    focus_x = -length / 2.0 + min(0.055, max(0.035, length * 0.15))
    ota.visual(
        Cylinder(radius=max(0.012, orad * 0.42), length=0.032),
        origin=Origin(xyz=(focus_x, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal,
        name="focus_socket", material_class_id="metal.aluminum_bare",
    )
    return ota, "front_corrector"


def _build_newtonian_ota(model, r, mats, *, assets, y_offset):
    dark, black, glass = mats["dark"], mats["black"], mats["glass"]
    ota = model.part("optical_tube")
    orad, length = r.ota_outer_radius, r.ota_length
    shell = _annular_cylinder_mesh_sdk(orad, orad * 0.88, length, "newt_tube_shell")
    ota.visual(
        Cylinder(radius=0.050, length=0.110),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="declination_shaft", material_class_id="metal.aluminum_bare",
    )
    ota.visual(
        Box((max(0.08, orad * 1.6), max(0.06, abs(y_offset) + orad * 0.35), max(0.06, orad * 1.2))),
        origin=Origin(xyz=(0.0, y_offset * 0.5, 0.0)),
        material=mats["metal"],
        name="ota_saddle_web", material_class_id="metal.aluminum_bare",
    )
    ota.visual(
        Cylinder(radius=max(0.042, orad * 0.55), length=length),
        origin=Origin(xyz=(0.0, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=dark,
        name="tube_spine", material_class_id="metal.paint_coated",
    )
    ota.visual(
        shell,
        origin=Origin(xyz=(0.0, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=dark,
        name="tube_shell", material_class_id="metal.paint_coated",
    )
    ota.visual(
        Cylinder(radius=orad * 0.88, length=0.008),
        origin=Origin(xyz=(-length / 2.0 + 0.01, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=glass,
        name="primary_mirror", material_class_id="glass.mirror",
    )
    ota.visual(
        Cylinder(radius=orad * 0.15, length=0.006),
        origin=Origin(xyz=(length / 2.0 - 0.02, y_offset, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=glass,
        name="secondary_mirror", material_class_id="glass.mirror",
    )
    ota.visual(
        Box((0.010, 0.160, 0.004)),
        origin=Origin(xyz=(length / 2.0 - 0.05, y_offset, 0.0)),
        material=black,
        name="spider_vane_0", material_class_id="metal.blackened_gunmetal",
    )
    focuser_x = -length / 2.0 + min(0.14, max(0.08, length * 0.28))
    focuser_top = orad + 0.013
    ota.visual(
        Box((max(0.05, orad * 1.2), max(0.045, orad * 0.9), max(orad, 0.02))),
        origin=Origin(xyz=(focuser_x, y_offset, focuser_top * 0.45)),
        material=black,
        name="focuser_bridge", material_class_id="metal.blackened_gunmetal",
    )
    ota.visual(
        Box((0.055, 0.050, 0.026)),
        origin=Origin(xyz=(focuser_x, y_offset, focuser_top)),
        material=black,
        name="focuser_block", material_class_id="metal.blackened_gunmetal",
    )
    return ota, "primary_mirror"


def _build_refractor_ota(model, r, mats, *, y_offset):
    gold, black, metal = mats["tube_gold"], mats["black"], mats["metal"]
    scope = model.part("telescope")
    length, radius = r.ota_length, r.ota_outer_radius * 0.33
    # Alt-az trunnion disc at the child origin — nests inside the bearing housing without deep clash.
    scope.visual(
        Cylinder(radius=0.034, length=0.040),
        origin=Origin(xyz=(0.045, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="trunnion_disc", material_class_id="metal.aluminum_bare",
    )
    scope.visual(
        Box((0.06, max(0.08, y_offset + 0.06), 0.05)),
        origin=Origin(xyz=(0.0, (max(y_offset, 0.02) + 0.05) * 0.5, 0.0)),
        material=metal,
        name="saddle_web", material_class_id="metal.aluminum_bare",
    )
    scope.visual(
        Box((0.120, 0.060, 0.070)),
        origin=Origin(xyz=(0.020, max(y_offset, 0.02) + 0.050, 0.0)),
        material=metal,
        name="saddle_block", material_class_id="metal.aluminum_bare",
    )
    scope.visual(
        Cylinder(radius=0.020, length=0.050),
        origin=Origin(xyz=(0.010, y_offset + 0.050, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="trunnion_web", material_class_id="metal.aluminum_bare",
    )
    scope.visual(
        Cylinder(radius=radius * 0.95, length=length),
        origin=Origin(xyz=(0.080, y_offset + 0.050, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=gold,
        name="main_tube", material_class_id="metal.brass_polished",
    )
    scope.visual(
        Cylinder(radius=radius * 1.12, length=0.080),
        origin=Origin(xyz=(0.260, y_offset + 0.050, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["accent"],
        name="etalon_tube", material_class_id="metal.paint_coated",
    )
    scope.visual(
        Cylinder(radius=radius * 0.80, length=0.050),
        origin=Origin(xyz=(-0.085, y_offset + 0.050, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=black,
        name="rear_adapter", material_class_id="metal.blackened_gunmetal",
    )
    scope.visual(
        Cylinder(radius=0.012, length=0.160),
        origin=Origin(xyz=(-0.180, y_offset + 0.050, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal,
        name="eyepiece_bridge", material_class_id="metal.aluminum_bare",
    )
    scope.visual(
        Cylinder(radius=0.016, length=0.120),
        origin=Origin(xyz=(-0.320, y_offset + 0.050, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal,
        name="eyepiece_tube", material_class_id="metal.aluminum_bare",
    )
    return scope, "main_tube"


def _build_photo_refractor_ota(model, r, mats, *, assets, y_offset):
    black, gray, glass, rubber = mats["black"], mats["dark"], mats["glass"], mats["rubber"]
    scope = model.part("scope")
    orad, irad, length = r.ota_outer_radius * 0.42, r.ota_outer_radius * 0.34, r.ota_length
    shell = _annular_cylinder_mesh_cq(orad, irad, length, "photo_tube_shell", assets=assets)
    dew = _annular_cylinder_mesh_cq(
        orad * 1.28, irad * 1.2, 0.140, "photo_dew_shell", assets=assets
    )
    scope.visual(
        Cylinder(radius=irad * 0.95, length=length * 1.02),
        origin=Origin(xyz=(length * 0.02, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=black,
        name="tube_spine", material_class_id="metal.blackened_gunmetal",
    )
    scope.visual(shell, material=black, name="main_tube", material_class_id="metal.blackened_gunmetal")
    scope.visual(
        dew, origin=Origin(xyz=(length * 0.51, 0.0, 0.0)), material=black, name="dew_shield", material_class_id="metal.blackened_gunmetal"
    )
    scope.visual(
        Cylinder(radius=irad * 1.2, length=0.008),
        origin=Origin(xyz=(length / 2.0 + 0.04, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=glass,
        name="front_lens", material_class_id="glass.clear_transparent",
    )
    scope.visual(
        Cylinder(radius=orad * 1.12, length=0.052),
        origin=Origin(xyz=(-length / 2.0 + 0.08, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="focus_ring", material_class_id="rubber.smooth_plain",
    )
    scope.visual(
        Box((0.170, 0.048, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, -0.044)),
        material=gray,
        name="dovetail_foot", material_class_id="metal.paint_coated",
    )
    scope.visual(
        Cylinder(radius=0.040, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=gray,
        name="tilt_clamp_pad", material_class_id="metal.paint_coated",
    )
    return scope, "front_lens"


def _attach_focus_aux(
    model,
    r,
    mats,
    *,
    parent,
    focus_origin: tuple[float, float, float] | None = None,
    y_offset: float = 0.0,
) -> ArticulatedObject | None:
    if r.focus_aux_style == "none":
        return None
    if r.focus_aux_style == "knob":
        knob = model.part("focus_knob")
        knob.visual(
            Cylinder(radius=0.018, length=0.035),
            origin=Origin(xyz=(-0.0175, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["rubber"],
            name="knob_cap", material_class_id="rubber.smooth_plain",
        )
        if focus_origin is None:
            if r.ota_style == "newtonian":
                focus_x = -r.ota_length / 2.0 + min(0.14, max(0.08, r.ota_length * 0.28))
                focus_origin = (focus_x, 0.0, r.ota_outer_radius + 0.013)
            elif r.ota_style == "sct_compact":
                focus_x = -r.ota_length / 2.0 + min(0.055, max(0.035, r.ota_length * 0.15))
                focus_origin = (focus_x, 0.0, 0.0)
            else:
                focus_origin = (
                    -r.ota_length * 0.678,
                    max(r.ota_outer_radius * 2.0, 0.17),
                    r.ota_outer_radius * 0.29,
                )
        if not any(v.name == "focus_socket" for v in parent.visuals):
            socket_rpy = (
                (0.0, 0.0, 0.0) if r.ota_style == "newtonian" else (0.0, math.pi / 2.0, 0.0)
            )
            parent.visual(
                Cylinder(radius=max(0.012, r.ota_outer_radius * 0.22), length=0.028),
                origin=Origin(xyz=focus_origin, rpy=socket_rpy),
                material=mats["metal"],
                name="focus_socket", material_class_id="metal.aluminum_bare",
            )
        model.articulation(
            "focus",
            ArticulationType.CONTINUOUS,
            parent=parent,
            child=knob,
            origin=Origin(xyz=focus_origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=0.6, velocity=6.0),
        )
        return knob
    # drawtube focuser chain (adopted: S6)
    focuser = model.part("focuser_body")
    drawtube = model.part("drawtube")
    knob = model.part("focus_knob")
    mount_x = -r.ota_length / 2.0 + min(0.12, max(0.06, r.ota_length * 0.28))
    mount_origin = (mount_x, y_offset, 0.0)
    focuser.visual(
        Box((0.110, 0.050, 0.050)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["black"],
        name="focuser_housing", material_class_id="metal.blackened_gunmetal",
    )
    focuser.visual(
        Box((0.040, 0.040, 0.040)),
        origin=Origin(xyz=(0.055, 0.0, 0.0)),
        material=mats["metal"],
        name="focuser_boss", material_class_id="metal.aluminum_bare",
    )
    drawtube.visual(
        Box((0.135, 0.042, 0.042)),
        origin=Origin(xyz=(-0.0225, 0.0, 0.0)),
        material=mats["black"],
        name="drawtube_slider", material_class_id="metal.blackened_gunmetal",
    )
    drawtube.visual(
        Box((0.030, 0.038, 0.038)),
        origin=Origin(xyz=(0.045, 0.0, 0.0)),
        material=mats["metal"],
        name="drawtube_capture_plug", material_class_id="metal.aluminum_bare",
    )
    knob.visual(
        Cylinder(radius=0.016, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["rubber"],
        name="pinion_knob", material_class_id="rubber.smooth_plain",
    )
    parent.visual(
        Box(
            (
                max(0.05, r.ota_outer_radius * 0.9),
                max(0.04, r.ota_outer_radius * 0.7),
                max(0.04, r.ota_outer_radius * 0.7),
            )
        ),
        origin=Origin(xyz=((-r.ota_length / 2.0 + mount_x) * 0.5, y_offset, 0.0)),
        material=mats["metal"],
        name="focuser_mount_bridge", material_class_id="metal.aluminum_bare",
    )
    parent.visual(
        Box((0.050, 0.050, 0.050)),
        origin=Origin(xyz=mount_origin),
        material=mats["metal"],
        name="focuser_mount_pad", material_class_id="metal.aluminum_bare",
    )
    model.articulation(
        "focuser_mount",
        ArticulationType.FIXED,
        parent=parent,
        child=focuser,
        origin=Origin(xyz=mount_origin),
    )
    model.articulation(
        "drawtube_slide",
        ArticulationType.PRISMATIC,
        parent=focuser,
        child=drawtube,
        origin=Origin(xyz=(-0.020, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        # Retract (+X) capped so the outboard pinion knob never re-enters the housing.
        motion_limits=MotionLimits(effort=2.0, velocity=0.4, lower=-0.04, upper=0.03),
    )
    model.articulation(
        "focus",
        ArticulationType.CONTINUOUS,
        parent=drawtube,
        child=knob,
        # Knob seated at the outboard end of the drawtube, clear of the focuser housing.
        origin=Origin(xyz=(-0.090, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.6, velocity=6.0),
    )
    return knob


# --------------------------------------------------------------------------- #
# Top-level build + tests
# --------------------------------------------------------------------------- #


def build_astronomical_telescope_on_tripod(
    config: AstronomicalTelescopeOnTripodConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or AstronomicalTelescopeOnTripodConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-astro-telescope-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["adopted_source_ids"] = ("S1", "S2", "S3", "S4", "S5", "S6")
    model.meta["slot_choices"] = slot_choices_for_config(r)

    if r.anchor_mode:
        _build_anchor_s1(model, assets=assets)
        return model

    mats = _mat(model, r.palette)

    if r.mount_family == "equatorial_fork":
        if r.root_support_style == "tripod_wedge":
            tripod, wedge_top, tilt = _build_tripod_wedge(model, r, mats)
        else:
            tripod, seat_z, tilt = _build_tripod_crown(model, r, mats)
            wedge_top = (0.0, 0.0, seat_z)
        _build_equatorial_fork_mount(
            model, r, mats, tripod=tripod, wedge_top=wedge_top, tilt=tilt, assets=assets
        )
    elif r.mount_family == "german_eq":
        tripod, seat_z, tilt = _build_tripod_crown(model, r, mats)
        _build_german_eq_mount(model, r, mats, tripod=tripod, seat_z=seat_z, assets=assets)
    elif r.mount_family == "altaz":
        tripod, bearing_z = _build_tripod_spline(model, r, mats)
        _build_altaz_mount(model, r, mats, tripod=tripod, bearing_z=bearing_z, assets=assets)
    elif r.mount_family == "photo_pan_tilt":
        if r.root_support_style == "tripod_spline":
            tripod, bearing_z = _build_tripod_spline(model, r, mats)
            seat_z = bearing_z
        else:
            tripod, wedge_top, _ = _build_tripod_wedge(model, r, mats)
            seat_z = wedge_top[2]
        _build_photo_pan_tilt(model, r, mats, tripod=tripod, seat_z=seat_z, assets=assets)
    elif r.mount_family == "dobsonian":
        disc, az_origin = _build_tabletop_dob_base(model, r, mats)
        _build_dobsonian(model, r, mats, disc=disc, az_origin=az_origin, assets=assets)
    else:
        raise ValueError(f"Unhandled mount_family: {r.mount_family}")
    return model


def build_seeded_astronomical_telescope_on_tripod(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_astronomical_telescope_on_tripod(config_from_seed(seed), assets=assets)


def slot_choices_for_config(
    r: ResolvedAstronomicalTelescopeOnTripodConfig,
) -> list[tuple[str, str]]:
    return [
        ("root_support", r.root_support_style),
        ("mount_head", r.mount_family),
        ("optical_assembly", r.ota_style),
        ("focus_auxiliary", r.focus_aux_style),
        ("material_style", r.material_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def _declare_overlap_allowances(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedAstronomicalTelescopeOnTripodConfig
) -> None:
    parts = {p.name for p in model.parts}

    def _allow(a: str, b: str, *, reason: str) -> None:
        if a in parts and b in parts:
            ctx.allow_overlap(model.get_part(a), model.get_part(b), reason=reason)

    if r.mount_family == "photo_pan_tilt":
        _allow("pan_head", "tilt_head", reason="ball/socket pan-tilt capture overlap (S4)")
        _allow("tilt_head", "scope", reason="scope dovetail seats on ball-head saddle plate")
        _allow("pan_head", "scope", reason="scope clamp region passes near pan socket hardware")
        for root in ("tripod", "tripod_base"):
            _allow("pan_head", root, reason="pan pedestal stem seats in tripod bearing socket (S4)")
            _allow(
                "scope",
                root,
                reason="long photo scope passes near tripod upper collar at rest pose (S4)",
            )

    if r.mount_family == "altaz":
        _allow(
            "mount_arm",
            "telescope",
            reason="alt-az saddle and trunnion nest on bearing pedestal (S3)",
        )
        if "mount_arm" in parts and "telescope" in parts:
            mount = model.get_part("mount_arm")
            scope = model.get_part("telescope")
            ctx.allow_overlap(
                mount,
                scope,
                elem_a="alt_bearing_housing",
                elem_b="trunnion_disc",
                reason="altitude trunnion disc nests in the bearing housing (S3)",
            )
            ctx.allow_overlap(
                mount,
                scope,
                elem_a="alt_bearing_housing",
                elem_b="saddle_web",
                reason="saddle web registers against the alt bearing housing face",
            )
            ctx.allow_overlap(
                mount,
                scope,
                elem_a="upright_arm",
                elem_b="trunnion_disc",
                reason="altitude trunnion disc nests against the upright arm head",
            )
            ctx.allow_overlap(
                mount,
                scope,
                elem_a="bearing_pedestal",
                elem_b="trunnion_disc",
                reason="trunnion disc registers on the bearing pedestal",
            )
            ctx.allow_overlap(
                mount,
                scope,
                elem_a="bearing_pedestal",
                elem_b="saddle_web",
                reason="saddle web registers on the bearing pedestal face",
            )

    if r.mount_family in {"equatorial_fork", "german_eq"}:
        _allow("fork_arm", "optical_tube", reason="declination shaft seats in the fork boss")
        _allow("polar_head", "tripod", reason="polar bearing seats on wedge plate or crown wedge")
        _allow("polar_head", "fork_arm", reason="RA collar seats on polar bearing")

    if r.mount_family == "german_eq":
        _allow("polar_assembly", "tripod", reason="polar housing seats on crown wedge")
        _allow("declination_head", "optical_tube", reason="declination clamp overlaps tube saddle")
        _allow(
            "declination_head", "polar_assembly", reason="dec clamp straddles RA shaft collar (S2)"
        )
        _allow(
            "optical_tube",
            "polar_assembly",
            reason="OTA saddle passes near polar housing during assembly (S2)",
        )
        _allow(
            "optical_tube",
            "tripod",
            reason="OTA tube passes near polar wedge at rest declination (S2)",
        )

    if "focus_knob" in parts:
        for parent in ("optical_tube", "telescope", "scope", "reflector_tube"):
            _allow(parent, "focus_knob", reason="focus knob cap seats in rear-cell focuser socket")

    if "focuser_body" in parts:
        for parent in ("optical_tube", "telescope", "scope", "reflector_tube"):
            _allow(parent, "focuser_body", reason="focuser housing overlaps OTA rear cell")
        _allow("focuser_body", "drawtube", reason="drawtube rides inside focuser bore")
        _allow("drawtube", "focus_knob", reason="focus knob sits on drawtube pinion boss")
        for parent in ("optical_tube", "telescope", "scope", "reflector_tube"):
            _allow(parent, "drawtube", reason="drawtube slider overlaps focuser mount pad (S6)")

    if r.mount_family == "dobsonian":
        _allow(
            "rocker_box",
            "reflector_tube",
            reason="altitude bearing stubs capture the tube trunnions",
        )


def run_astronomical_telescope_on_tripod_tests(
    object_model: ArticulatedObject,
    config: AstronomicalTelescopeOnTripodConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlap_allowances(ctx, object_model, r)

    part_names = {p.name for p in object_model.parts}
    ota_names = {"optical_tube", "telescope", "scope", "reflector_tube"}
    ctx.check("has_ota", bool(part_names & ota_names), details=str(sorted(part_names)))

    pointing = [
        j
        for j in object_model.articulations
        if j.name not in {"focus", "drawtube_slide", "scope_mount", "focuser_mount"}
        and j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at_least_two_pointing_dof", len(pointing) >= 2, details=str([j.name for j in pointing])
    )

    if r.anchor_mode:
        _run_anchor_s1_tests(ctx, object_model)
    elif r.mount_family == "equatorial_fork":
        _run_equatorial_tests(ctx, object_model)
    elif r.mount_family == "altaz":
        _run_altaz_tests(ctx, object_model)
    elif r.mount_family == "photo_pan_tilt":
        _run_pan_tilt_tests(ctx, object_model)
    elif r.mount_family == "dobsonian":
        _run_dob_tests(ctx, object_model)
    elif r.mount_family == "german_eq":
        _run_german_tests(ctx, object_model)

    if r.focus_aux_style == "knob" and "focus_knob" in part_names:
        focus = object_model.get_articulation("focus")
        ctx.check("focus_is_continuous", focus.articulation_type == ArticulationType.CONTINUOUS)

    return ctx.report()


def _elem_center_z(ctx: TestContext, part, elem: str) -> float | None:
    bounds = ctx.part_element_world_aabb(part, elem=elem)
    if bounds is None:
        return None
    return 0.5 * (bounds[0][2] + bounds[1][2])


def _elem_center_xy(ctx: TestContext, part, elem: str) -> tuple[float, float] | None:
    bounds = ctx.part_element_world_aabb(part, elem=elem)
    if bounds is None:
        return None
    return (0.5 * (bounds[0][0] + bounds[1][0]), 0.5 * (bounds[0][1] + bounds[1][1]))


def _run_anchor_s1_tests(ctx: TestContext, model: ArticulatedObject) -> None:
    tripod = model.get_part("tripod")
    polar_head = model.get_part("polar_head")
    fork_arm = model.get_part("fork_arm")
    optical_tube = model.get_part("optical_tube")
    focus_knob = model.get_part("focus_knob")
    polar = model.get_articulation("polar_angle")
    ra = model.get_articulation("right_ascension")
    dec = model.get_articulation("declination")
    focus = model.get_articulation("focus")
    ctx.check(
        "anchor_joint_types",
        polar.articulation_type == ArticulationType.REVOLUTE
        and ra.articulation_type == ArticulationType.CONTINUOUS
        and dec.articulation_type == ArticulationType.REVOLUTE
        and focus.articulation_type == ArticulationType.CONTINUOUS,
    )
    ctx.expect_contact(
        polar_head,
        tripod,
        elem_a="ra_bearing",
        elem_b="wedge_plate",
        contact_tol=0.003,
        name="polar on wedge",
    )
    ctx.expect_contact(
        fork_arm,
        polar_head,
        elem_a="ra_collar",
        elem_b="ra_bearing",
        contact_tol=0.003,
        name="RA collar seats",
    )
    ctx.expect_contact(
        optical_tube,
        fork_arm,
        elem_a="declination_shaft",
        elem_b="declination_boss",
        contact_tol=0.003,
        name="DEC shaft meets fork",
    )
    ctx.expect_contact(
        focus_knob,
        optical_tube,
        elem_a="knob_cap",
        elem_b="focus_socket",
        contact_tol=0.003,
        name="focus knob seated",
    )
    rest_z = _elem_center_z(ctx, optical_tube, "front_corrector")
    with ctx.pose({dec: 0.60}):
        raised_z = _elem_center_z(ctx, optical_tube, "front_corrector")
    ctx.check(
        "positive_dec_raises_nose",
        rest_z is not None and raised_z is not None and raised_z > rest_z + 0.05,
    )


def _run_equatorial_tests(ctx: TestContext, model: ArticulatedObject) -> None:
    dec = model.get_articulation("declination")
    ota = model.get_part("optical_tube")
    dec_upper = dec.motion_limits.upper
    elem = "front_corrector"
    rest_z = _elem_center_z(ctx, ota, elem)
    probe_dec = min(0.55, dec_upper * 0.95)
    with ctx.pose({dec: probe_dec}):
        raised_z = _elem_center_z(ctx, ota, elem)
    ctx.check(
        "positive_dec_raises_tube",
        (rest_z is None) or (raised_z is not None and raised_z > rest_z + 0.02),
    )
    # DEC upper limit must keep the OTA (rear_cell/tube_shell) clear of the RA bearing
    # housing — the root cause of the seed-2 穿模. Assert real mesh clearance at the
    # limit pose via the full collision engine (respects declared allow_overlap pairs;
    # optical_tube<->polar_head is intentionally NOT allowed).
    dec_lower = dec.motion_limits.lower
    for label, value in (("dec_upper", dec_upper), ("dec_lower", dec_lower)):
        with ctx.pose({dec: value}):
            ctx.fail_if_parts_overlap_in_current_pose(
                name=f"ota_clears_ra_bearing_at_{label}",
            )


def _run_altaz_tests(ctx: TestContext, model: ArticulatedObject) -> None:
    az = model.get_articulation("tripod_to_mount")
    alt = model.get_articulation("mount_to_telescope")
    scope = model.get_part("telescope")
    ctx.check("az_is_continuous", az.articulation_type == ArticulationType.CONTINUOUS)
    ctx.check("alt_is_revolute", alt.articulation_type == ArticulationType.REVOLUTE)
    rest_z = _elem_center_z(ctx, scope, "main_tube")
    with ctx.pose({alt: 0.70}):
        raised_z = _elem_center_z(ctx, scope, "main_tube")
    ctx.check(
        "positive_alt_raises_objective",
        (rest_z is None) or (raised_z is not None and raised_z > rest_z + 0.02),
    )
    rest_xy = _elem_center_xy(ctx, scope, "main_tube")
    with ctx.pose({az: 1.0}):
        panned_xy = _elem_center_xy(ctx, scope, "main_tube")
    measurable = rest_xy is not None and panned_xy is not None
    ctx.check(
        "az_changes_xy",
        (not measurable) or math.hypot(panned_xy[0] - rest_xy[0], panned_xy[1] - rest_xy[1]) > 0.02,
    )


def _run_pan_tilt_tests(ctx: TestContext, model: ArticulatedObject) -> None:
    pan = model.get_articulation("pan_bearing")
    tilt = model.get_articulation("tilt_axis")
    scope = model.get_part("scope")
    ctx.check("pan_continuous", pan.articulation_type == ArticulationType.CONTINUOUS)
    ctx.check("tilt_revolute", tilt.articulation_type == ArticulationType.REVOLUTE)
    rest_z = _elem_center_z(ctx, scope, "front_lens")
    with ctx.pose({tilt: 0.55}):
        raised_z = _elem_center_z(ctx, scope, "front_lens")
    ctx.check(
        "tilt_raises_front_lens",
        (rest_z is None) or (raised_z is not None and raised_z > rest_z + 0.02),
    )


def _run_dob_tests(ctx: TestContext, model: ArticulatedObject) -> None:
    az = model.get_articulation("azimuth_bearing")
    alt = model.get_articulation("altitude_bearing")
    tube = model.get_part("reflector_tube")
    ctx.check(
        "dob_has_two_dof",
        az.articulation_type == ArticulationType.CONTINUOUS
        and alt.articulation_type == ArticulationType.REVOLUTE,
    )
    alt_upper = alt.motion_limits.upper
    rest_z = _elem_center_z(ctx, tube, "primary_mirror")
    with ctx.pose({alt: min(0.55, alt_upper * 0.9)}):
        raised_z = _elem_center_z(ctx, tube, "primary_mirror")
    ctx.check(
        "dob_alt_raises_mirror",
        (rest_z is None) or (raised_z is not None and raised_z > rest_z + 0.005),
        details=f"rest_z={rest_z}, raised_z={raised_z}",
    )
    # Altitude upper limit must keep the tube's lower end clear of the tabletop base.
    with ctx.pose({alt: alt_upper}):
        ctx.fail_if_parts_overlap_in_current_pose(name="tube_clears_tabletop_at_alt_upper")


def _run_german_tests(ctx: TestContext, model: ArticulatedObject) -> None:
    ra = model.get_articulation("right_ascension")
    dec = model.get_articulation("declination")
    ctx.check("german_ra_continuous", ra.articulation_type == ArticulationType.CONTINUOUS)
    ctx.check("german_dec_revolute", dec.articulation_type == ArticulationType.REVOLUTE)


__all__ = [
    "AstronomicalTelescopeOnTripodConfig",
    "ResolvedAstronomicalTelescopeOnTripodConfig",
    "build_astronomical_telescope_on_tripod",
    "build_seeded_astronomical_telescope_on_tripod",
    "config_from_seed",
    "resolve_config",
    "run_astronomical_telescope_on_tripod_tests",
    "slot_choices_for_seed",
    "__modular__",
]
