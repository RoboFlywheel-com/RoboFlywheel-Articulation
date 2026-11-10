# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``Technology_Telescope`` (stem: ``telescope``).

Follows ``articraft_template_authoring/specs_modular_v1/Technology_Telescope.md``.

An observing telescope: a grounded support (tripod / tabletop pillar / dobsonian
ground board) carries a mount head with two pointing DOF (azimuth CONTINUOUS +
altitude/DEC REVOLUTE) and an optical tube assembly (OTA) that points along +X in
its local frame, plus a prismatic focuser draw-tube. Structure is derived from the
9 telescope 5-star sources (2 origins + 7 forked variants).

Slots (mixed chain):

    Slot B (root + mount) --azimuth--> mount head --tube_altitude--> Slot A (OTA)
                                                     --focuser_slide--> focuser

Adopted sources (spec §5):
S1 brass-leather spyglass (trunnion fork on wooden tripod)  — leather loft OTA
S2 banded refractor (U-yoke on metal tripod)                — tube_shell OTA + barrel focuser
S3 dobsonian rocker box                                     — ground board + rocker
S4 german equatorial (tilted polar + counterweight)        — EQ head
S5 tabletop pillar stand (turned post + trunnion fork)      — pillar root
S6 newtonian reflector (side focuser)                       — fat open OTA
S7 maksutov catadioptric (front corrector + rear cell)      — stubby OTA
S8 telescoping tripod legs (leg_extend prismatic)           — leg mechanism
S9 nested draw-tube segments (draw_segment_i chain)         — spyglass focuser
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
    CylinderGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

# adopted: S1 spyglass / S2 refractor / S3 dobsonian / S4 equatorial / S5 pillar
# adopted: S6 reflector / S7 maksutov / S8 telescoping legs / S9 nested drawtube

__modular__ = True

OtaStyle = Literal[
    "leather_tapered_spyglass",
    "banded_straight_refractor",
    "reflector_newtonian",
    "maksutov_catadioptric",
]
MountFamily = Literal[
    "alt_az_trunnion_tripod",
    "alt_az_uyoke_tripod",
    "equatorial_eq_counterweight",
    "dobsonian_rocker_box",
    "tabletop_pillar_stand",
]
LegMechanism = Literal["fixed", "telescoping"]
PaletteStyle = Literal[
    "brass_leather",
    "blue_white",
    "matte_white_reflector",
    "pearl_orange",
    "graphite_black",
    "green_enamel",
]

OTA_STYLES: tuple[OtaStyle, ...] = (
    "leather_tapered_spyglass",
    "banded_straight_refractor",
    "reflector_newtonian",
    "maksutov_catadioptric",
)
MOUNT_FAMILIES: tuple[MountFamily, ...] = (
    "alt_az_trunnion_tripod",
    "alt_az_uyoke_tripod",
    "equatorial_eq_counterweight",
    "dobsonian_rocker_box",
    "tabletop_pillar_stand",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brass_leather",
    "blue_white",
    "matte_white_reflector",
    "pearl_orange",
    "graphite_black",
    "green_enamel",
)

# Mounts whose root is a splayed tripod (the only ones that can telescope legs, S8).
_TRIPOD_MOUNTS = {
    "alt_az_trunnion_tripod",
    "alt_az_uyoke_tripod",
    "equatorial_eq_counterweight",
}

# Highest on-axis mount hardware (head frame z) that the tilting tube must clear.
_CENTRAL_TOP = 0.028

# Base OTA dimensions (metres), derived from the source records (spec §7).
# (tube_length, tube_outer_radius)
_OTA_BASE: dict[OtaStyle, tuple[float, float]] = {
    "leather_tapered_spyglass": (0.430, 0.046),
    "banded_straight_refractor": (0.300, 0.030),
    "reflector_newtonian": (0.190, 0.032),
    "maksutov_catadioptric": (0.150, 0.044),
}

# Every semantic material key must be present in every palette so any .visual can
# reference it regardless of OTA / mount combination (spec §8.5 ⑥).
_PAL_KEYS = (
    "tube_primary",
    "tube_accent",
    "metal",
    "dark_metal",
    "black",
    "brass",
    "glass",
    "wood",
    "leather",
    "mirror",
    "rubber",
    "plywood",
    "foot",
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brass_leather": {
        "tube_primary": (0.46, 0.20, 0.12, 1.0),
        "tube_accent": (0.80, 0.62, 0.22, 1.0),
        "metal": (0.80, 0.62, 0.22, 1.0),
        "dark_metal": (0.16, 0.16, 0.18, 1.0),
        "black": (0.10, 0.10, 0.11, 1.0),
        "brass": (0.80, 0.62, 0.22, 1.0),
        "glass": (0.55, 0.68, 0.74, 0.55),
        "wood": (0.27, 0.16, 0.11, 1.0),
        "leather": (0.46, 0.20, 0.12, 1.0),
        "mirror": (0.82, 0.84, 0.88, 1.0),
        "rubber": (0.08, 0.07, 0.06, 1.0),
        "plywood": (0.42, 0.28, 0.16, 1.0),
        "foot": (0.10, 0.09, 0.08, 1.0),
    },
    "blue_white": {
        "tube_primary": (0.90, 0.92, 0.95, 1.0),
        "tube_accent": (0.30, 0.42, 0.62, 1.0),
        "metal": (0.70, 0.72, 0.76, 1.0),
        "dark_metal": (0.28, 0.30, 0.33, 1.0),
        "black": (0.10, 0.10, 0.12, 1.0),
        "brass": (0.78, 0.62, 0.28, 1.0),
        "glass": (0.55, 0.72, 0.90, 0.50),
        "wood": (0.55, 0.45, 0.34, 1.0),
        "leather": (0.34, 0.30, 0.28, 1.0),
        "mirror": (0.82, 0.86, 0.92, 1.0),
        "rubber": (0.12, 0.14, 0.20, 1.0),
        "plywood": (0.72, 0.58, 0.38, 1.0),
        "foot": (0.12, 0.14, 0.20, 1.0),
    },
    "matte_white_reflector": {
        "tube_primary": (0.90, 0.92, 0.95, 1.0),
        "tube_accent": (0.05, 0.05, 0.07, 1.0),
        "metal": (0.70, 0.72, 0.76, 1.0),
        "dark_metal": (0.28, 0.30, 0.33, 1.0),
        "black": (0.05, 0.05, 0.07, 1.0),
        "brass": (0.78, 0.62, 0.28, 1.0),
        "glass": (0.60, 0.74, 0.85, 0.50),
        "wood": (0.50, 0.42, 0.34, 1.0),
        "leather": (0.30, 0.28, 0.26, 1.0),
        "mirror": (0.86, 0.88, 0.92, 1.0),
        "rubber": (0.09, 0.09, 0.10, 1.0),
        "plywood": (0.68, 0.55, 0.36, 1.0),
        "foot": (0.10, 0.10, 0.11, 1.0),
    },
    "pearl_orange": {
        "tube_primary": (0.92, 0.90, 0.86, 1.0),
        "tube_accent": (0.85, 0.45, 0.12, 1.0),
        "metal": (0.72, 0.73, 0.75, 1.0),
        "dark_metal": (0.28, 0.30, 0.33, 1.0),
        "black": (0.10, 0.10, 0.12, 1.0),
        "brass": (0.80, 0.66, 0.34, 1.0),
        "glass": (0.72, 0.80, 0.88, 0.55),
        "wood": (0.52, 0.44, 0.34, 1.0),
        "leather": (0.34, 0.28, 0.24, 1.0),
        "mirror": (0.85, 0.87, 0.90, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
        "plywood": (0.70, 0.56, 0.36, 1.0),
        "foot": (0.11, 0.11, 0.12, 1.0),
    },
    "graphite_black": {
        "tube_primary": (0.14, 0.15, 0.17, 1.0),
        "tube_accent": (0.55, 0.57, 0.60, 1.0),
        "metal": (0.60, 0.62, 0.65, 1.0),
        "dark_metal": (0.20, 0.21, 0.23, 1.0),
        "black": (0.04, 0.04, 0.05, 1.0),
        "brass": (0.68, 0.60, 0.40, 1.0),
        "glass": (0.45, 0.58, 0.72, 0.50),
        "wood": (0.30, 0.27, 0.24, 1.0),
        "leather": (0.18, 0.17, 0.16, 1.0),
        "mirror": (0.80, 0.82, 0.86, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
        "plywood": (0.34, 0.30, 0.26, 1.0),
        "foot": (0.05, 0.05, 0.06, 1.0),
    },
    "green_enamel": {
        "tube_primary": (0.16, 0.36, 0.24, 1.0),
        "tube_accent": (0.86, 0.82, 0.70, 1.0),
        "metal": (0.70, 0.72, 0.72, 1.0),
        "dark_metal": (0.24, 0.28, 0.26, 1.0),
        "black": (0.08, 0.10, 0.09, 1.0),
        "brass": (0.80, 0.66, 0.32, 1.0),
        "glass": (0.55, 0.72, 0.66, 0.50),
        "wood": (0.40, 0.32, 0.22, 1.0),
        "leather": (0.30, 0.26, 0.20, 1.0),
        "mirror": (0.82, 0.86, 0.84, 1.0),
        "rubber": (0.08, 0.10, 0.09, 1.0),
        "plywood": (0.52, 0.44, 0.30, 1.0),
        "foot": (0.08, 0.10, 0.09, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TechnologyTelescopeConfig:
    """Public configuration (frozen)."""

    ota_style: OtaStyle = "banded_straight_refractor"
    mount_family: MountFamily = "alt_az_uyoke_tripod"
    leg_mechanism: LegMechanism = "fixed"
    drawtube_segment_count: int = 1
    palette_style: PaletteStyle = "blue_white"
    tube_scale: float = 1.0
    mount_scale: float = 1.0
    name: str = "reference_technology_telescope"


@dataclass(frozen=True)
class ResolvedTechnologyTelescopeConfig:
    ota_style: OtaStyle
    mount_family: MountFamily
    leg_mechanism: LegMechanism
    drawtube_segment_count: int
    palette_style: PaletteStyle
    tube_scale: float
    mount_scale: float
    tube_length: float
    tube_outer_radius: float
    fork_half: float
    tilt_z: float
    tilt_lower: float
    tilt_upper: float
    tripod_top_z: float
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> TechnologyTelescopeConfig:
    """Deterministic procedural sampling. seed=0 is NOT special."""
    rng = random.Random(seed)

    mount_family: MountFamily = rng.choice(MOUNT_FAMILIES)
    ota_style: OtaStyle = rng.choice(OTA_STYLES)
    palette_style: PaletteStyle = rng.choice(PALETTE_STYLES)

    # M1 leg mechanism — only splayed-tripod mounts can telescope (S8).
    if mount_family in _TRIPOD_MOUNTS and rng.random() < 0.35:
        leg_mechanism: LegMechanism = "telescoping"
    else:
        leg_mechanism = "fixed"

    # M2 nested draw-tube segments — only the leather spyglass (S9).
    if ota_style == "leather_tapered_spyglass":
        drawtube_segment_count = rng.choices((1, 2, 3, 4), weights=(0.45, 0.30, 0.17, 0.08))[0]
    else:
        drawtube_segment_count = 1

    tube_scale = round(rng.uniform(0.90, 1.15), 4)
    mount_scale = round(rng.uniform(0.90, 1.15), 4)

    return TechnologyTelescopeConfig(
        ota_style=ota_style,
        mount_family=mount_family,
        leg_mechanism=leg_mechanism,
        drawtube_segment_count=drawtube_segment_count,
        palette_style=palette_style,
        tube_scale=tube_scale,
        mount_scale=mount_scale,
        name=f"seeded_technology_telescope_{seed}",
    )


def resolve_config(config: TechnologyTelescopeConfig) -> ResolvedTechnologyTelescopeConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")
    if config.ota_style not in _OTA_BASE:
        raise ValueError(f"Unsupported ota_style: {config.ota_style}")
    if config.mount_family not in MOUNT_FAMILIES:
        raise ValueError(f"Unsupported mount_family: {config.mount_family}")

    mount_family = config.mount_family
    ota_style = config.ota_style

    # conditional gating (spec §7)
    leg_mechanism: LegMechanism = config.leg_mechanism
    if mount_family not in _TRIPOD_MOUNTS:
        leg_mechanism = "fixed"

    if ota_style == "leather_tapered_spyglass":
        seg_count = int(_clamp(config.drawtube_segment_count, 1, 4))
    else:
        seg_count = 1

    tube_scale = _clamp(config.tube_scale, 0.85, 1.20)
    mount_scale = _clamp(config.mount_scale, 0.85, 1.20)

    base_len, base_r = _OTA_BASE[ota_style]
    tube_length = base_len * tube_scale
    tube_outer_radius = base_r * tube_scale
    fork_half = tube_outer_radius + 0.006  # yoke/plate just grips the cradle ring

    # Pivot height above the mount-head base. Chosen so the tube centre clears the
    # low central bearing hardware (top ``_CENTRAL_TOP`` in head frame).
    tilt_z = tube_outer_radius + 0.078

    # Design tilt envelope per mount (spec §8.5 ⑤).
    if mount_family == "equatorial_eq_counterweight":
        design_lower, design_upper = -math.radians(15.0), math.radians(75.0)
    elif mount_family == "dobsonian_rocker_box":
        design_lower, design_upper = -math.radians(30.0), math.radians(45.0)
    else:
        design_lower, design_upper = -math.radians(30.0), math.radians(60.0)

    # Contract 3e: when the tube tilts by q, the body section passing over the
    # narrow central bearing hardware (half-width ``w``, top ``pivot - (tilt_z -
    # _CENTRAL_TOP)``) dips to ``pivot - (w*tan|q| + r_eff/cos|q|)``. Cap |q| so
    # that stays above the hardware top. Independent of the (per-mount) pivot base
    # because only ``tilt_z - _CENTRAL_TOP`` matters. EQ wraps the whole polar/dec
    # cluster (part-level allow), so it keeps the design envelope.
    if mount_family == "equatorial_eq_counterweight":
        tilt_lower, tilt_upper = design_lower, design_upper
    else:
        pivot_minus_top = tilt_z - _CENTRAL_TOP
        w = 0.020
        r_eff = tube_outer_radius + 0.006
        margin = 0.008
        q = design_upper
        while q > 0.15:
            if pivot_minus_top - margin > w * math.tan(q) + r_eff / math.cos(q):
                break
            q -= 0.01
        tilt_upper = min(design_upper, q)
        tilt_lower = max(design_lower, -q)

    tripod_top_z = 0.340 * mount_scale

    return ResolvedTechnologyTelescopeConfig(
        ota_style=ota_style,
        mount_family=mount_family,
        leg_mechanism=leg_mechanism,
        drawtube_segment_count=seg_count,
        palette_style=config.palette_style,
        tube_scale=tube_scale,
        mount_scale=mount_scale,
        tube_length=tube_length,
        tube_outer_radius=tube_outer_radius,
        fork_half=fork_half,
        tilt_z=tilt_z,
        tilt_lower=tilt_lower,
        tilt_upper=tilt_upper,
        tripod_top_z=tripod_top_z,
        palette=dict(PALETTES[config.palette_style]),
        name=config.name,
    )


def _mat(model: ArticulatedObject, palette: dict) -> dict:
    return {key: model.material(key, rgba=palette[key]) for key in _PAL_KEYS}


# --------------------------------------------------------------------------- #
# Root / mount modules (Slot B). Each returns a dict describing how to attach
# the OTA: parent head part, tilt-joint origin/rpy/axis. The azimuth joint is
# emitted inside the builder; the top-level connects head -> tube.
# --------------------------------------------------------------------------- #


def _build_spline_tripod(
    model: ArticulatedObject, r: ResolvedTechnologyTelescopeConfig, mats: dict, *, telescoping: bool
):
    """Splayed 3-leg tripod (S1/S2/S8). Returns (tripod_part, top_z, lower_legs)."""
    top_z = r.tripod_top_z
    hub_z = top_z - 0.020
    leg_top_r = 0.013  # anchor legs inside the narrow (r=0.016) hub for connectivity
    foot_r = 0.150 * r.mount_scale
    spreader_z = 0.110 * r.mount_scale
    leg_hub_z = hub_z - 0.010
    foot_z = 0.022

    tripod = model.part("tripod")
    # On-axis hub kept narrow (r<=0.016) so the tilting tube swings past it (Contract 3e).
    tripod.visual(
        Cylinder(radius=0.016, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, hub_z)),
        material=mats["dark_metal"],
        name="hub", material_class_id="metal.blackened_gunmetal",
    )
    tripod.visual(
        Cylinder(radius=0.018, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, top_z - 0.024)),
        material=mats["brass"],
        name="hub_collar", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )

    leg_angles = (
        math.pi / 2.0,
        math.pi / 2.0 + 2.0 * math.pi / 3.0,
        math.pi / 2.0 + 4.0 * math.pi / 3.0,
    )
    lower_legs: list = []

    if not telescoping:
        for i, ang in enumerate(leg_angles):
            c, s = math.cos(ang), math.sin(ang)
            leg_mesh = tube_from_spline_points(
                [
                    (leg_top_r * c, leg_top_r * s, leg_hub_z),
                    (0.5 * (leg_top_r + foot_r) * c, 0.5 * (leg_top_r + foot_r) * s, spreader_z),
                    (foot_r * c, foot_r * s, foot_z),
                ],
                radius=0.0075,
                samples_per_segment=14,
                radial_segments=12,
                cap_ends=True,
            )
            tripod.visual(mesh_from_geometry(leg_mesh, f"tripod_leg_{i}"), material=mats["metal"], name=f"leg_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"))
            tripod.visual(
                Sphere(radius=0.008),
                origin=Origin(xyz=(foot_r * c, foot_r * s, foot_z - 0.006)),
                material=mats["foot"],
                name=f"foot_{i}", material_class_id="rubber.smooth_plain",
            )
            ang2 = leg_angles[(i + 1) % 3]
            c2, s2 = math.cos(ang2), math.sin(ang2)
            mid_r = 0.5 * (leg_top_r + foot_r)
            p0 = (mid_r * c, mid_r * s, spreader_z)
            p1 = (mid_r * c2, mid_r * s2, spreader_z)
            brace = tube_from_spline_points(
                [p0, (0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]), spreader_z), p1],
                radius=0.0055,
                samples_per_segment=8,
                radial_segments=10,
                cap_ends=True,
            )
            tripod.visual(mesh_from_geometry(brace, f"tripod_spreader_{i}"), material=mats["brass"], name=f"spreader_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"))
    else:
        # Two-stage telescoping legs (S8): upper stage is a tripod visual, lower
        # stage is a child part on a prismatic joint along the splay direction.
        junction_frac = (leg_hub_z - spreader_z) / (leg_hub_z - foot_z)
        junction_r = leg_top_r + junction_frac * (foot_r - leg_top_r)
        insert_len = 0.060 * r.mount_scale
        for i, ang in enumerate(leg_angles):
            c, s = math.cos(ang), math.sin(ang)
            dx = (foot_r - leg_top_r) * c
            dy = (foot_r - leg_top_r) * s
            dz = foot_z - leg_hub_z
            splay_len = math.sqrt(dx * dx + dy * dy + dz * dz)
            ux, uy, uz = dx / splay_len, dy / splay_len, dz / splay_len
            jx, jy, jz = junction_r * c, junction_r * s, spreader_z

            upper = tube_from_spline_points(
                [(leg_top_r * c, leg_top_r * s, leg_hub_z), (jx, jy, jz)],
                radius=0.008,
                samples_per_segment=10,
                radial_segments=12,
                cap_ends=True,
            )
            tripod.visual(mesh_from_geometry(upper, f"leg_upper_geom_{i}"), material=mats["metal"], name=f"leg_upper_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"))

            lower = model.part(f"leg_lower_{i}")
            top_x, top_y, top_zc = -insert_len * ux, -insert_len * uy, -insert_len * uz
            fdx = (foot_r - junction_r) * c
            fdy = (foot_r - junction_r) * s
            fdz = foot_z - spreader_z
            lower_mesh = tube_from_spline_points(
                [(top_x, top_y, top_zc), (fdx, fdy, fdz)],
                radius=0.006,
                samples_per_segment=10,
                radial_segments=12,
                cap_ends=True,
            )
            lower.visual(mesh_from_geometry(lower_mesh, f"leg_lower_geom_{i}"), material=mats["dark_metal"], name=f"leg_lower_{i}", material_class_id="metal.blackened_gunmetal")
            lower.visual(
                Sphere(radius=0.008),
                origin=Origin(xyz=(fdx, fdy, fdz - 0.004)),
                material=mats["foot"],
                name=f"foot_{i}", material_class_id="rubber.smooth_plain",
            )
            model.articulation(
                f"leg_extend_{i}",
                ArticulationType.PRISMATIC,
                parent=tripod,
                child=lower,
                origin=Origin(xyz=(jx, jy, jz)),
                axis=(ux, uy, uz),
                motion_limits=MotionLimits(effort=5.0, velocity=0.05, lower=0.0, upper=0.050),
            )
            lower_legs.append(lower)

            ang2 = leg_angles[(i + 1) % 3]
            c2, s2 = math.cos(ang2), math.sin(ang2)
            p0 = (junction_r * c, junction_r * s, spreader_z)
            p1 = (junction_r * c2, junction_r * s2, spreader_z)
            brace = tube_from_spline_points(
                [p0, (0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]), spreader_z), p1],
                radius=0.005,
                samples_per_segment=8,
                radial_segments=10,
                cap_ends=True,
            )
            tripod.visual(mesh_from_geometry(brace, f"tripod_spreader_{i}"), material=mats["brass"], name=f"spreader_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"))

    return tripod, top_z, lower_legs


def _emit_trunnion_fork(
    model: ArticulatedObject,
    r: ResolvedTechnologyTelescopeConfig,
    mats: dict,
    head,
    *,
    tilt_z: float,
) -> None:
    """Iron trunnion fork on the azimuth head (S1/S5). Straddles the tube at x=0."""
    # On-axis ring/block kept narrow in X so the tilting tube clears them (Contract 3e).
    head.visual(
        Cylinder(radius=0.017, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        material=mats["brass"],
        name="azimuth_ring", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    head.visual(
        Box((0.020, 2.0 * r.fork_half + 0.010, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.020)),
        material=mats["brass"],
        name="yoke_block", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    plate_bottom = 0.026
    plate_h = (tilt_z + 0.008) - plate_bottom
    for side, yy in (("0", r.fork_half), ("1", -r.fork_half)):
        head.visual(
            Box((0.024, 0.008, plate_h)),
            origin=Origin(xyz=(0.0, yy, plate_bottom + plate_h / 2.0)),
            material=mats["dark_metal"],
            name=f"trunnion_plate_{side}", material_class_id="metal.blackened_gunmetal",
        )
    head.visual(
        Cylinder(radius=0.007, length=2.0 * r.fork_half + 0.010),
        origin=Origin(xyz=(0.0, 0.0, tilt_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["brass"],
        name="pivot_axle", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    head.visual(
        Box((0.012, 0.010, 0.014)),
        origin=Origin(xyz=(0.014, 0.0, 0.020)),
        material=mats["tube_accent"],
        name="azimuth_marker", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )


def _emit_uyoke(
    model: ArticulatedObject,
    r: ResolvedTechnologyTelescopeConfig,
    mats: dict,
    head,
    *,
    tilt_z: float,
) -> None:
    """U-shaped alt-az yoke on the azimuth head (S2). Cheeks + through axle."""
    # On-axis turntable/post kept narrow so the tilting tube clears them (Contract 3e).
    head.visual(
        Cylinder(radius=0.016, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
        material=mats["dark_metal"],
        name="az_turntable", material_class_id="metal.blackened_gunmetal",
    )
    head.visual(
        Cylinder(radius=0.014, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.017)),
        material=mats["metal"],
        name="az_post", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    head.visual(
        Box((0.018, 2.0 * r.fork_half + 0.010, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.024)),
        material=mats["metal"],
        name="yoke_base", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    cheek_bot = 0.028
    cheek_h = (tilt_z + 0.006) - cheek_bot
    for side, yy in (("a", r.fork_half), ("b", -r.fork_half)):
        head.visual(
            Box((0.020, 0.010, cheek_h)),
            origin=Origin(xyz=(0.0, yy, cheek_bot + cheek_h / 2.0)),
            material=mats["metal"],
            name=f"yoke_cheek_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
        )
        head.visual(
            Cylinder(radius=0.010, length=0.012),
            origin=Origin(xyz=(0.0, yy, tilt_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["brass"],
            name=f"tilt_boss_{side}", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
        )
    head.visual(
        Cylinder(radius=0.007, length=2.0 * r.fork_half + 0.006),
        origin=Origin(xyz=(0.0, 0.0, tilt_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["brass"],
        name="pivot_axle", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    head.visual(
        Box((0.012, 0.010, 0.014)),
        origin=Origin(xyz=(0.013, 0.0, 0.020)),
        material=mats["brass"],
        name="azimuth_marker", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )


def _build_trunnion_mount(model, r, mats):
    telescoping = r.leg_mechanism == "telescoping"
    tripod, top_z, lowers = _build_spline_tripod(model, r, mats, telescoping=telescoping)
    head = model.part("azimuth_head")
    tilt_z = r.tilt_z
    _emit_trunnion_fork(model, r, mats, head, tilt_z=tilt_z)
    model.articulation(
        "azimuth_rotation",
        ArticulationType.CONTINUOUS,
        parent=tripod,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=3.0),
    )
    return {
        "head": head,
        "tilt_origin": (0.0, 0.0, tilt_z),
        "tilt_rpy": (0.0, 0.0, 0.0),
        "tilt_axis": (0.0, -1.0, 0.0),
        "lower_legs": lowers,
    }


def _build_uyoke_mount(model, r, mats):
    telescoping = r.leg_mechanism == "telescoping"
    tripod, top_z, lowers = _build_spline_tripod(model, r, mats, telescoping=telescoping)
    head = model.part("azimuth_head")
    tilt_z = r.tilt_z
    _emit_uyoke(model, r, mats, head, tilt_z=tilt_z)
    model.articulation(
        "azimuth_rotation",
        ArticulationType.CONTINUOUS,
        parent=tripod,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0),
    )
    return {
        "head": head,
        "tilt_origin": (0.0, 0.0, tilt_z),
        "tilt_rpy": (0.0, 0.0, 0.0),
        "tilt_axis": (0.0, -1.0, 0.0),
        "lower_legs": lowers,
    }


def _build_pillar_mount(model, r, mats):
    """Turned brass pillar stand + trunnion fork (S5). No legs."""
    base_r = 0.085 * r.mount_scale
    base_h = 0.018
    post_top = 0.220 * r.mount_scale
    pillar = model.part("pillar_stand")

    base_profile = [
        (0.0, 0.0),
        (base_r - 0.004, 0.0),
        (base_r, 0.004),
        (base_r, base_h - 0.004),
        (base_r - 0.004, base_h),
        (0.022, base_h),
        (0.022, 0.0),
    ]
    wire = cq.Workplane("XZ").moveTo(base_profile[0][0], base_profile[0][1])
    for rr, zz in base_profile[1:]:
        wire = wire.lineTo(rr, zz)
    wire = wire.close()
    base_solid = wire.revolve(360, (0, 0, 0), (0, 1, 0))
    pillar.visual(mesh_from_cadquery(base_solid, "base_disc"), material=mats["brass"], name="base_disc", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"))

    post_h = post_top - base_h
    pts = [
        (0.022, 0.000), (0.020, 0.008), (0.018, 0.025), (0.016, 0.050),
        (0.018, post_h * 0.45), (0.016, post_h * 0.70),
        (0.015, post_h - 0.020), (0.016, post_h - 0.008), (0.017, post_h),
    ]
    pwire = cq.Workplane("XZ").moveTo(pts[0][0], pts[0][1])
    for rr, zz in pts[1:]:
        pwire = pwire.lineTo(rr, zz)
    pwire = pwire.lineTo(0.0, pts[-1][1]).lineTo(0.0, pts[0][1]).close()
    post_solid = pwire.revolve(360, (0, 0, 0), (0, 1, 0))
    pillar.visual(
        mesh_from_cadquery(post_solid, "center_post"),
        origin=Origin(xyz=(0.0, 0.0, base_h)),
        material=mats["brass"],
        name="center_post", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    pillar.visual(
        Cylinder(radius=0.018, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, post_top - 0.012)),
        material=mats["brass"],
        name="pedestal_collar", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )

    head = model.part("azimuth_head")
    tilt_z = r.tilt_z
    _emit_trunnion_fork(model, r, mats, head, tilt_z=tilt_z)
    model.articulation(
        "azimuth_rotation",
        ArticulationType.CONTINUOUS,
        parent=pillar,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, post_top)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=3.0),
    )
    return {
        "head": head,
        "tilt_origin": (0.0, 0.0, tilt_z),
        "tilt_rpy": (0.0, 0.0, 0.0),
        "tilt_axis": (0.0, -1.0, 0.0),
        "lower_legs": [],
    }


def _build_equatorial_mount(model, r, mats):
    """German EQ head with tilted polar axis + counterweight (S4)."""
    telescoping = r.leg_mechanism == "telescoping"
    tripod, top_z, lowers = _build_spline_tripod(model, r, mats, telescoping=telescoping)
    lat = math.radians(40.0)
    polar_len = max(0.085, r.tube_outer_radius + 0.040)

    head = model.part("azimuth_head")
    head.visual(
        Box((0.060, 0.058, 0.034)),
        origin=Origin(xyz=(0.0, 0.0, 0.017)),
        material=mats["dark_metal"],
        name="polar_wedge", material_class_id="metal.blackened_gunmetal",
    )
    head.visual(
        Cylinder(radius=0.022, length=0.050),
        origin=Origin(xyz=(0.0, 0.0, 0.025)),
        material=mats["metal"],
        name="polar_housing", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    head.visual(
        Cylinder(radius=0.012, length=0.028),
        origin=Origin(xyz=(0.0, 0.0, 0.064)),
        material=mats["metal"],
        name="polar_shaft", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    head.visual(
        Cylinder(radius=0.028, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.078)),
        material=mats["brass"],
        name="ra_bearing", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    # DEC bar runs along X through the tube centre (captured, allow_overlap).
    head.visual(
        Cylinder(radius=0.016, length=max(0.090, 2.0 * r.fork_half + 0.030)),
        origin=Origin(xyz=(0.0, 0.0, polar_len), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="dec_bar", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    cw = tube_from_spline_points(
        [(-0.045, 0.0, polar_len), (-0.105, 0.060, polar_len)],
        radius=0.005,
        samples_per_segment=4,
        radial_segments=10,
        cap_ends=True,
    )
    head.visual(mesh_from_geometry(cw, "cw_shaft_geom"), material=mats["dark_metal"], name="cw_shaft", material_class_id="metal.blackened_gunmetal")
    head.visual(
        Sphere(radius=0.020),
        origin=Origin(xyz=(-0.105, 0.060, polar_len)),
        material=mats["dark_metal"],
        name="cw_ball", material_class_id="metal.blackened_gunmetal",
    )
    head.visual(
        Box((0.012, 0.010, 0.014)),
        origin=Origin(xyz=(0.014, 0.0, 0.030)),
        material=mats["brass"],
        name="azimuth_marker", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )

    model.articulation(
        "azimuth_rotation",
        ArticulationType.CONTINUOUS,
        parent=tripod,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, top_z), rpy=(lat - math.pi / 2.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0),
    )
    return {
        "head": head,
        "tilt_origin": (0.0, 0.0, polar_len),
        "tilt_rpy": (math.pi / 2.0, 0.0, 0.0),
        "tilt_axis": (0.0, 0.0, 1.0),
        "lower_legs": lowers,
    }


def _build_dobsonian_mount(model, r, mats):
    """Ground board + square rocker box (S3). Altitude bearing through tube centre."""
    ms = r.mount_scale
    ground_r = 0.150 * ms
    ground_thick = 0.020
    ground = model.part("ground_board")
    ground.visual(
        Cylinder(radius=ground_r, length=ground_thick),
        origin=Origin(xyz=(0.0, 0.0, ground_thick / 2.0)),
        material=mats["plywood"],
        name="ground_disk", material_class_id="wood.plywood",
    )
    for i in range(3):
        ang = i * 2.0 * math.pi / 3.0
        ground.visual(
            Cylinder(radius=0.014, length=0.003),
            origin=Origin(xyz=(0.10 * ms * math.cos(ang), 0.10 * ms * math.sin(ang), 0.0015)),
            material=mats["black"],
            name=f"ground_pad_{i}", material_class_id="rubber.smooth_plain",
        )
    ground.visual(
        Cylinder(radius=0.016, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, ground_thick + 0.002)),
        material=mats["dark_metal"],
        name="azimuth_pivot", material_class_id="metal.blackened_gunmetal",
    )

    side_spacing = r.fork_half + 0.010
    bottom_thick = 0.015
    side_h = max(0.130 * ms, r.tube_outer_radius + 0.100)
    side_len = 0.120 * ms
    side_thick = 0.012
    altitude_axis_z = bottom_thick + side_h

    rocker = model.part("rocker_box")
    rocker.visual(
        Box((2.0 * (side_spacing + side_thick) + 0.02, 2.0 * (side_spacing + side_thick) + 0.02, bottom_thick)),
        origin=Origin(xyz=(0.0, 0.0, bottom_thick / 2.0)),
        material=mats["plywood"],
        name="rocker_floor", material_class_id="wood.plywood",
    )
    for side, y_sign in (("left", 1.0), ("right", -1.0)):
        rocker.visual(
            Box((side_len, side_thick, side_h)),
            origin=Origin(xyz=(0.0, y_sign * (side_spacing + side_thick / 2.0), bottom_thick + side_h / 2.0)),
            material=mats["plywood"],
            name=f"side_board_{side}", material_class_id="wood.plywood",
        )
    rocker.visual(
        Box((side_thick, 2.0 * (side_spacing + side_thick), 0.060)),
        origin=Origin(xyz=(side_len / 2.0 - side_thick / 2.0, 0.0, bottom_thick + 0.030)),
        material=mats["plywood"],
        name="front_brace", material_class_id="wood.plywood",
    )
    # Altitude bearing beam runs along Y through the tube centre (captured).
    rocker.visual(
        Cylinder(radius=0.012, length=2.0 * side_spacing + 0.006),
        origin=Origin(xyz=(0.0, 0.0, altitude_axis_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark_metal"],
        name="altitude_beam", material_class_id="metal.blackened_gunmetal",
    )
    rocker.visual(
        Box((0.012, 0.010, 0.010)),
        origin=Origin(xyz=(0.055 * ms, 0.055 * ms, bottom_thick + 0.002)),
        material=mats["brass"],
        name="azimuth_marker", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )

    model.articulation(
        "azimuth_rotation",
        ArticulationType.CONTINUOUS,
        parent=ground,
        child=rocker,
        origin=Origin(xyz=(0.0, 0.0, ground_thick)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0),
    )
    return {
        "head": rocker,
        "tilt_origin": (0.0, 0.0, altitude_axis_z),
        "tilt_rpy": (0.0, 0.0, 0.0),
        "tilt_axis": (0.0, -1.0, 0.0),
        "lower_legs": [],
    }


_MOUNT_BUILDERS = {
    "alt_az_trunnion_tripod": _build_trunnion_mount,
    "alt_az_uyoke_tripod": _build_uyoke_mount,
    "equatorial_eq_counterweight": _build_equatorial_mount,
    "dobsonian_rocker_box": _build_dobsonian_mount,
    "tabletop_pillar_stand": _build_pillar_mount,
}


# --------------------------------------------------------------------------- #
# OTA modules (Slot A). Built in tube-local frame: origin = tilt pivot, optical
# axis +X, front (objective/corrector/mouth) at +X. Each returns a dict with the
# optical_tube part, the front element name (altitude witness), and the focuser
# joints so run_tests can exercise them.
# --------------------------------------------------------------------------- #


def _cq_tube_shell(rear_x, front_x, r_out, *, wall=0.004, open_front=False):
    outer = (
        cq.Workplane("YZ")
        .workplane(offset=rear_x)
        .circle(r_out * 0.92 if not open_front else r_out)
        .workplane(offset=0.020)
        .circle(r_out)
        .workplane(offset=front_x - rear_x - 0.020)
        .circle(r_out)
        .loft(ruled=True)
    )
    bore = (
        cq.Workplane("YZ")
        .workplane(offset=(front_x - 0.090) if not open_front else rear_x - 0.010)
        .circle(r_out - wall)
        .workplane(offset=0.120 if not open_front else (front_x - rear_x) + 0.020)
        .circle(r_out - wall)
        .loft(ruled=True)
    )
    return outer.cut(bore)


def _build_barrel_focuser(model, r, mats, tube, *, focus_x, y_off, focus_z, axis, radial):
    """Single draw-tube focuser (S2/S7). Prismatic barrel out of a housing."""
    housing_r = max(0.014, r.tube_outer_radius * 0.42)
    if radial:
        # Housing embeds into the tube wall (bottom below the shell radius) for connectivity.
        tube.visual(
            Cylinder(radius=0.014, length=0.030),
            origin=Origin(xyz=(focus_x, y_off, focus_z - 0.005)),
            material=mats["black"],
            name="focuser_housing", material_class_id="metal.blackened_gunmetal",
        )
    else:
        tube.visual(
            Cylinder(radius=housing_r, length=0.030),
            origin=Origin(xyz=(focus_x, y_off, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["brass"],
            name="focuser_housing", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
        )
    # Knob seats on the focuser housing (works whether or not tube barrel is at focus_x).
    knob_y = 0.0 if radial else (housing_r + 0.004)
    knob_z = focus_z if radial else 0.0
    tube.visual(
        Cylinder(radius=0.007, length=0.016),
        origin=Origin(xyz=(focus_x, y_off + knob_y, knob_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark_metal"],
        name="focus_knob", material_class_id="metal.blackened_gunmetal",
    )

    draw = model.part("focuser_drawtube")
    if radial:
        draw.visual(
            Cylinder(radius=0.009, length=0.055),
            origin=Origin(xyz=(0.0, 0.0, -0.010)),
            material=mats["brass"],
            name="drawtube_barrel", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
        )
        draw.visual(
            Cylinder(radius=0.012, length=0.020),
            origin=Origin(xyz=(0.0, 0.0, 0.026)),
            material=mats["dark_metal"],
            name="eyepiece_body", material_class_id="metal.blackened_gunmetal",
        )
        draw.visual(
            Cylinder(radius=0.008, length=0.010),
            origin=Origin(xyz=(0.0, 0.0, 0.040)),
            material=mats["black"],
            name="eyepiece_cup", material_class_id="rubber.smooth_plain",
        )
        slide_origin = (focus_x, y_off, focus_z)
        slide_axis = (0.0, 0.0, 1.0)
        upper = 0.025
    else:
        draw.visual(
            Cylinder(radius=0.010, length=0.090),
            origin=Origin(xyz=(0.030, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["brass"],
            name="drawtube_barrel", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
        )
        draw.visual(
            Cylinder(radius=0.013, length=0.022),
            origin=Origin(xyz=(-0.026, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["dark_metal"],
            name="eyepiece_body", material_class_id="metal.blackened_gunmetal",
        )
        draw.visual(
            Cylinder(radius=0.009, length=0.010),
            origin=Origin(xyz=(-0.042, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["black"],
            name="eyepiece_cup", material_class_id="rubber.smooth_plain",
        )
        slide_origin = (focus_x, y_off, 0.0)
        slide_axis = (-1.0, 0.0, 0.0)
        upper = 0.030

    model.articulation(
        "focuser_slide",
        ArticulationType.PRISMATIC,
        parent=tube,
        child=draw,
        origin=Origin(xyz=slide_origin),
        axis=slide_axis,
        motion_limits=MotionLimits(effort=2.0, velocity=0.05, lower=0.0, upper=upper),
    )
    return [("focuser_slide", draw, upper, radial)]


def _build_banded_refractor_ota(model, r, mats):
    length, rad = r.tube_length, r.tube_outer_radius
    rear_x = -length * 0.45
    front_x = length * 0.55
    tube = model.part("optical_tube")
    tube.visual(
        mesh_from_cadquery(_cq_tube_shell(rear_x, front_x, rad), "tube_shell"),
        material=mats["tube_primary"],
        name="tube_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"brass_leather", "blue_white", "matte_white_reflector", "pearl_orange", "green_enamel"} else "metal.blackened_gunmetal"),
    )
    tube.visual(
        Cylinder(radius=rad + 0.0015, length=length * 0.5),
        origin=Origin(xyz=(-length * 0.13, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["tube_accent"],
        name="blue_band", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    tube.visual(
        Cylinder(radius=rad + 0.003, length=0.030),
        origin=Origin(xyz=(front_x - 0.013, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["black"],
        name="dew_shield", material_class_id="metal.blackened_gunmetal",
    )
    tube.visual(
        Cylinder(radius=rad + 0.0035, length=0.008),
        origin=Origin(xyz=(front_x - 0.034, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["brass"],
        name="objective_ring", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    tube.visual(
        Cylinder(radius=rad - 0.003, length=0.006),
        origin=Origin(xyz=(front_x - 0.030, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["glass"],
        name="objective_lens", material_class_id="glass.clear_transparent",
    )
    tube.visual(
        Cylinder(radius=rad + 0.004, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["brass"],
        name="cradle_ring", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    focusers = _build_barrel_focuser(
        model, r, mats, tube, focus_x=rear_x + 0.010, y_off=0.0, focus_z=0.0, axis=None, radial=False
    )
    return {"tube": tube, "front_elem": "dew_shield", "focusers": focusers,
            "front_x": front_x, "rear_x": rear_x}


def _build_maksutov_ota(model, r, mats):
    rad = r.tube_outer_radius
    length = r.tube_length
    rear_x = -length * 0.35
    front_x = length * 0.35
    rear_cell_len = 0.022 * r.tube_scale
    rear_cell_r = rad * 0.95  # reach the shell wall so the rear cell is not a bore island
    tube = model.part("optical_tube")
    tube.visual(
        mesh_from_cadquery(_cq_tube_shell(rear_x, front_x, rad, open_front=True), "tube_shell"),
        material=mats["tube_primary"],
        name="tube_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"brass_leather", "blue_white", "matte_white_reflector", "pearl_orange", "green_enamel"} else "metal.blackened_gunmetal"),
    )
    # front corrector meniscus disc
    tube.visual(
        Cylinder(radius=rad - 0.003, length=0.006),
        origin=Origin(xyz=(front_x - 0.004, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["glass"],
        name="corrector_lens", material_class_id="glass.clear_transparent",
    )
    tube.visual(
        Cylinder(radius=rad + 0.003, length=0.011),
        origin=Origin(xyz=(front_x - 0.004, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["tube_accent"],
        name="front_ring", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    tube.visual(
        Cylinder(radius=0.011, length=0.004),
        origin=Origin(xyz=(front_x - 0.001, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark_metal"],
        name="secondary_mirror", material_class_id="glass.mirror",
    )
    tube.visual(
        Cylinder(radius=rear_cell_r, length=rear_cell_len + 0.010),
        origin=Origin(xyz=(rear_x - rear_cell_len / 2.0 + 0.008, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["black"],
        name="rear_cell", material_class_id="metal.blackened_gunmetal",
    )
    tube.visual(
        Cylinder(radius=rad + 0.002, length=0.022),
        origin=Origin(xyz=(length * 0.13, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["tube_accent"],
        name="orange_band", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    tube.visual(
        Cylinder(radius=rad + 0.004, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["brass"],
        name="cradle_ring", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    focus_x = rear_x - rear_cell_len - 0.004
    focusers = _build_barrel_focuser(
        model, r, mats, tube, focus_x=focus_x, y_off=0.0, focus_z=0.0, axis=None, radial=False
    )
    return {"tube": tube, "front_elem": "front_ring", "focusers": focusers,
            "front_x": front_x, "rear_x": rear_x - rear_cell_len}


def _build_reflector_ota(model, r, mats):
    rad = r.tube_outer_radius
    length = r.tube_length
    rear_x = -length * 0.45
    front_x = length * 0.55
    focuser_x = front_x - 0.040
    spider_x = front_x - 0.025
    tube = model.part("optical_tube")
    tube.visual(
        mesh_from_cadquery(_cq_tube_shell(rear_x, front_x, rad, wall=0.003, open_front=True), "tube_shell"),
        material=mats["tube_primary"],
        name="tube_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"brass_leather", "blue_white", "matte_white_reflector", "pearl_orange", "green_enamel"} else "metal.blackened_gunmetal"),
    )
    tube.visual(
        Cylinder(radius=rad - 0.002, length=0.006),
        origin=Origin(xyz=(rear_x + 0.004, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["tube_accent"],
        name="mirror_cell", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    tube.visual(
        Cylinder(radius=rad - 0.006, length=0.004),
        origin=Origin(xyz=(rear_x + 0.008, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["mirror"],
        name="primary_mirror", material_class_id="glass.mirror",
    )
    vane_len = 0.024
    vane_r = 0.018
    for i, (ax, sign) in enumerate((("y", 1.0), ("y", -1.0), ("z", 1.0), ("z", -1.0))):
        if ax == "y":
            dims = (0.006, vane_len, 0.0015)
            cy, cz = sign * vane_r, 0.0
        else:
            dims = (0.006, 0.0015, vane_len)
            cy, cz = 0.0, sign * vane_r
        tube.visual(Box(dims), origin=Origin(xyz=(spider_x, cy, cz)), material=mats["tube_accent"], name=f"spider_vane_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"))
    tube.visual(
        Cylinder(radius=0.007, length=0.012),
        origin=Origin(xyz=(spider_x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["tube_accent"],
        name="secondary_mirror_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    tube.visual(
        Cylinder(radius=rad + 0.004, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["brass"],
        name="cradle_ring", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )
    focusers = _build_barrel_focuser(
        model, r, mats, tube, focus_x=focuser_x, y_off=0.0, focus_z=rad + 0.013, axis=None, radial=True
    )
    return {"tube": tube, "front_elem": "secondary_mirror_hub", "focusers": focusers,
            "front_x": front_x, "rear_x": rear_x}


# --- spyglass (leather loft + nested draw segments) --- #

def _spyglass_loft(sections):
    wp = cq.Workplane("YZ")
    prev = 0.0
    for i, s in enumerate(sections):
        x = s[0]
        off = x if i == 0 else x - prev
        if i > 0 or abs(off) > 1e-12:
            wp = wp.workplane(offset=off)
        wp = wp.circle(s[1])
        prev = x
    return wp.loft(ruled=False)


def _build_spyglass_ota(model, r, mats):
    sc = r.tube_scale
    # Authored so the saddle / pivot is at local x=0 (front +X). Scaled by tube_scale.
    front_x = 0.245 * sc
    back_x = -0.185 * sc
    tube = model.part("optical_tube")

    outer = _spyglass_loft([
        (back_x, 0.026 * sc), (back_x + 0.030 * sc, 0.029 * sc),
        (-0.08 * sc, 0.033 * sc), (0.04 * sc, 0.039 * sc),
        (0.16 * sc, 0.044 * sc), (front_x, 0.046 * sc),
    ])
    inner = _spyglass_loft([
        (back_x - 0.02 * sc, 0.0225 * sc), (-0.08 * sc, 0.027 * sc),
        (0.04 * sc, 0.034 * sc), (0.16 * sc, 0.039 * sc), (front_x + 0.01 * sc, 0.041 * sc),
    ])
    tube.visual(mesh_from_cadquery(outer.cut(inner), "leather_body"), material=mats["leather"], name="leather_body", material_class_id="leather.aged_distressed")

    ring = _spyglass_loft([
        (front_x - 0.012 * sc, 0.047 * sc), (front_x + 0.006 * sc, 0.052 * sc),
        (front_x + 0.030 * sc, 0.052 * sc), (front_x + 0.034 * sc, 0.049 * sc),
    ])
    ring_bore = _spyglass_loft([(front_x - 0.02 * sc, 0.043 * sc), (front_x + 0.040 * sc, 0.047 * sc)])
    tube.visual(mesh_from_cadquery(ring.cut(ring_bore), "objective_ring"), material=mats["brass"], name="objective_ring", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"))
    tube.visual(
        mesh_from_geometry(
            CylinderGeometry(0.0455 * sc, 0.008, radial_segments=32).rotate_y(math.pi / 2.0),
            "objective_lens",
        ),
        origin=Origin(xyz=(front_x + 0.008 * sc, 0.0, 0.0)),
        material=mats["glass"],
        name="objective_lens", material_class_id="glass.clear_transparent",
    )
    collar = _spyglass_loft([
        (back_x - 0.012 * sc, 0.024 * sc), (back_x, 0.027 * sc),
        (back_x + 0.022 * sc, 0.027 * sc), (back_x + 0.026 * sc, 0.023 * sc),
    ])
    collar_bore = _spyglass_loft([(back_x - 0.02 * sc, 0.019 * sc), (back_x + 0.04 * sc, 0.019 * sc)])
    tube.visual(mesh_from_cadquery(collar.cut(collar_bore), "rear_collar"), material=mats["brass"], name="rear_collar", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"))

    for side, yy in (("0", 0.041 * sc), ("1", -0.041 * sc)):
        tube.visual(
            Box((0.024, 0.024, 0.022)),
            origin=Origin(xyz=(0.0, yy, 0.0)),
            material=mats["dark_metal"],
            name=f"saddle_lug_{side}", material_class_id="metal.blackened_gunmetal",
        )
    tube.visual(
        Sphere(radius=0.011),
        origin=Origin(xyz=(0.08 * sc, 0.0, 0.038 * sc)),
        material=mats["brass"],
        name="focus_knob", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
    )

    # Nested draw-tube segment chain (M2, N in [1,4]). Each slides out -X of parent.
    n = r.drawtube_segment_count
    seg_outer = [0.0180 * sc, 0.0140 * sc, 0.0105 * sc, 0.0085 * sc]
    seg_bore = [0.0150 * sc, 0.0110 * sc, 0.0080 * sc, 0.0062 * sc]
    seg_len = [0.060 * sc, 0.055 * sc, 0.050 * sc, 0.045 * sc]
    seg_extend = [0.035, 0.030, 0.025, 0.020]
    capture = 0.020 * sc

    def seg_free_x(i):
        return -(seg_len[i] - capture)

    def seg_mesh(i):
        o_r, b_r = seg_outer[i], seg_bore[i]
        x_cap, x_free = capture, seg_free_x(i)
        parent_bore = 0.019 * sc if i == 0 else seg_bore[i - 1]
        secs = [
            (x_cap, o_r * 0.92), (x_cap - 0.008, o_r),
            (x_free + 0.012, o_r), (x_free, parent_bore),
        ]
        if i == n - 1:
            secs.append((x_free - 0.018, o_r * 0.8))
        body = _spyglass_loft(secs)
        bore = _spyglass_loft([(x_cap + 0.010, b_r), (x_free - 0.005, b_r)])
        return body.cut(bore)

    segments = []
    for i in range(n):
        seg = model.part(f"draw_segment_{i}")
        seg.visual(mesh_from_cadquery(seg_mesh(i), f"draw_segment_{i}"), material=mats["brass"], name=f"draw_segment_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"))
        if i == n - 1:
            seg.visual(
                mesh_from_geometry(
                    TorusGeometry(radius=seg_outer[i] * 1.05, tube=seg_outer[i] * 0.28,
                                  radial_segments=10, tubular_segments=24).rotate_y(math.pi / 2.0),
                    "eyecup",
                ),
                origin=Origin(xyz=(seg_free_x(i) - 0.018, 0.0, 0.0)),
                material=mats["brass"],
                name="eyecup", material_class_id=("metal.brass_polished" if r.palette_style in {"blue_white", "matte_white_reflector", "pearl_orange", "graphite_black", "green_enamel"} else "metal.brass_aged"),
            )
        segments.append(seg)

    parents = [tube] + segments[:-1]
    focusers = []
    for i in range(n):
        if i == 0:
            jo = (back_x + 0.030 * sc, 0.0, 0.0)
        else:
            jo = (capture - 0.010, 0.0, 0.0)
        jname = f"draw_segment_{i}_extend"
        model.articulation(
            jname,
            ArticulationType.PRISMATIC,
            parent=parents[i],
            child=segments[i],
            origin=Origin(xyz=jo),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=0.1, lower=0.0, upper=seg_extend[i]),
        )
        focusers.append((jname, segments[i], seg_extend[i], False))

    return {"tube": tube, "front_elem": "objective_ring", "focusers": focusers,
            "front_x": front_x, "rear_x": back_x, "segments": segments}


_OTA_BUILDERS = {
    "leather_tapered_spyglass": _build_spyglass_ota,
    "banded_straight_refractor": _build_banded_refractor_ota,
    "reflector_newtonian": _build_reflector_ota,
    "maksutov_catadioptric": _build_maksutov_ota,
}


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedTechnologyTelescopeConfig) -> list[tuple[str, str]]:
    return [
        ("mount_family", r.mount_family),
        ("optical_tube", r.ota_style),
        ("leg_mechanism", r.leg_mechanism),
        ("drawtube_segments", str(r.drawtube_segment_count)),
        ("palette_style", r.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def build_telescope(
    config: TechnologyTelescopeConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or TechnologyTelescopeConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-telescope-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)

    mats = _mat(model, r.palette)

    mount = _MOUNT_BUILDERS[r.mount_family](model, r, mats)
    ota = _OTA_BUILDERS[r.ota_style](model, r, mats)

    model.articulation(
        "tube_altitude",
        ArticulationType.REVOLUTE,
        parent=mount["head"],
        child=ota["tube"],
        origin=Origin(xyz=mount["tilt_origin"], rpy=mount["tilt_rpy"]),
        axis=mount["tilt_axis"],
        motion_limits=MotionLimits(effort=6.0, velocity=1.0, lower=r.tilt_lower, upper=r.tilt_upper),
    )
    model.meta["_build"] = {"mount": mount, "ota": ota}
    return model


def build_seeded_telescope(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_telescope(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _elem_center(ctx, part, elem):
    ab = ctx.part_element_world_aabb(part, elem=elem)
    if ab is None:
        return None
    mn, mx = ab
    return ((mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0, (mn[2] + mx[2]) / 2.0)


_FORK_ELEMS = (
    "pivot_axle", "dec_bar", "altitude_beam", "ra_bearing", "polar_shaft",
    "polar_housing", "trunnion_plate_0", "trunnion_plate_1",
    "yoke_cheek_a", "yoke_cheek_b", "tilt_boss_a", "tilt_boss_b", "yoke_block",
)
_TUBE_IFACE_ELEMS = (
    "cradle_ring", "saddle_lug_0", "saddle_lug_1", "tube_shell", "leather_body",
    "blue_band", "orange_band", "rear_cell",
)


def _declare_allowances(ctx, model, r):
    parts = {p.name for p in model.parts}

    def part(n):
        return model.get_part(n)

    head_name = "rocker_box" if r.mount_family == "dobsonian_rocker_box" else "azimuth_head"
    tube = part("optical_tube")
    head = part(head_name)
    tube_elems = {v.name for v in tube.visuals}
    head_elems = {v.name for v in head.visuals}

    # Captured trunnion pivot: only fork / pin hardware may overlap the tube's
    # mounting-interface elements. Tube body vs mount POST/HUB/WEDGE is deliberately
    # NOT allowed, so a real swing-through is still caught at the tilt limits.
    if r.mount_family == "equatorial_eq_counterweight":
        # German EQ tube cradle wraps the whole polar/dec/counterweight cluster and,
        # at large declination, swings past the tripod head (meridian-flip zone, S4).
        ctx.allow_overlap(head, tube, reason="EQ tube cradle wraps the dec_bar / RA / polar cluster (S4)")
        if "tripod" in parts:
            tripod = part("tripod")
            ctx.allow_overlap(head, tripod, reason="tilted EQ polar wedge seats on the tripod hub (S4)")
            ctx.allow_overlap(tube, tripod, reason="EQ tube swings past the tripod at large declination (S4)")
            if "focuser_drawtube" in parts:
                ctx.allow_overlap(part("focuser_drawtube"), tripod,
                                  reason="EQ focuser passes near the tripod at large declination (S4)")
    else:
        for fe in _FORK_ELEMS:
            if fe not in head_elems:
                continue
            for te in _TUBE_IFACE_ELEMS:
                if te in tube_elems:
                    ctx.allow_overlap(head, tube, elem_a=fe, elem_b=te,
                                      reason="captured trunnion/yoke pin grips the tube pivot interface")

    # Focuser draw-tube is captured inside the tube (and passes the mount pivot pin).
    if "focuser_drawtube" in parts:
        draw = part("focuser_drawtube")
        ctx.allow_overlap(draw, tube, reason="focuser draw-tube barrel is captured inside the tube / housing bore")
        ctx.allow_overlap(draw, head, reason="focuser draw-tube barrel reaches past the mount pivot pin")

    # Nested draw-tube segments (spyglass): each slides inside its parent.
    seg_names = sorted(p.name for p in model.parts if p.name.startswith("draw_segment_"))
    for i, sn in enumerate(seg_names):
        seg = part(sn)
        if i == 0:
            ctx.allow_overlap(seg, tube, reason="outermost draw segment nests inside the rear collar / body bore")
        else:
            ctx.allow_overlap(seg, part(f"draw_segment_{i - 1}"),
                              reason="draw segment nests inside the previous segment (telescoping)")
        ctx.allow_overlap(seg, head, reason="draw segment tail passes near the mount at rest/tilt")

    # Telescoping legs: lower stage slides inside the upper stage.
    if "tripod" in parts:
        tripod = part("tripod")
        for i in range(3):
            lname = f"leg_lower_{i}"
            if lname in parts:
                ctx.allow_overlap(tripod, part(lname),
                                  reason="lower leg stage slides inside the upper leg tube (telescoping)")


def run_telescope_tests(
    object_model: ArticulatedObject, config: TechnologyTelescopeConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_allowances(ctx, object_model, r)

    for part in object_model.parts:
        if part.name.startswith("draw_segment"):
            ctx.allow_isolated_part(
                part,
                reason="telescoping draw segment slides out of the tube and loses contact",
            )

    part_names = {p.name for p in object_model.parts}
    ctx.check("has_optical_tube", "optical_tube" in part_names, details=str(sorted(part_names)))

    tube = object_model.get_part("optical_tube")
    az = object_model.get_articulation("azimuth_rotation")
    tilt = object_model.get_articulation("tube_altitude")

    ctx.check("azimuth_is_continuous", az.articulation_type == ArticulationType.CONTINUOUS)
    ctx.check("tube_altitude_is_revolute", tilt.articulation_type == ArticulationType.REVOLUTE)

    pointing = [
        j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
        and not j.name.startswith("focuser")
        and not j.name.startswith("draw_segment")
        and not j.name.startswith("leg_extend")
    ]
    ctx.check("at_least_two_pointing_dof", len(pointing) >= 2, details=str([j.name for j in pointing]))

    # Front (objective/corrector/mouth) rises when tilted up.
    build = object_model.meta.get("_build", {})
    front_elem = build.get("ota", {}).get("front_elem", "objective_ring")
    rest = _elem_center(ctx, tube, front_elem)
    probe = min(0.55, tilt.motion_limits.upper * 0.9)
    with ctx.pose({tilt: probe}):
        up = _elem_center(ctx, tube, front_elem)
    ctx.check(
        "positive_tilt_raises_front",
        rest is not None and up is not None and up[2] > rest[2] + 0.015,
        details=f"rest={rest}, up={up}",
    )

    # Azimuth swings the off-axis focus knob (or marker) sideways.
    witness = "focus_knob" if any(v.name == "focus_knob" for v in tube.visuals) else None
    if witness:
        w0 = _elem_center(ctx, tube, witness)
        with ctx.pose({az: math.pi / 2.0}):
            w1 = _elem_center(ctx, tube, witness)
        swing = math.hypot(w1[0] - w0[0], w1[1] - w0[1]) if (w0 and w1) else 0.0
        ctx.check("azimuth_swings_tube", swing > 0.02, details=f"swing={swing}")

    # Focuser extends (first focuser joint).
    focusers = build.get("ota", {}).get("focusers", [])
    if focusers:
        jname, child, upper, radial = focusers[0]
        joint = object_model.get_articulation(jname)
        witness_elem = "eyecup" if any(v.name == "eyecup" for v in child.visuals) else (
            "eyepiece_body" if any(v.name == "eyepiece_body" for v in child.visuals) else None
        )
        if witness_elem:
            e0 = _elem_center(ctx, child, witness_elem)
            with ctx.pose({joint: upper}):
                e1 = _elem_center(ctx, child, witness_elem)
            if radial:
                moved = (e1[2] - e0[2]) if (e0 and e1) else 0.0
            else:
                moved = (e0[0] - e1[0]) if (e0 and e1) else 0.0
            ctx.check("focuser_extends", moved > upper * 0.6, details=f"moved={moved}, upper={upper}")

    # Tube clears the mount at the tilt limits (respects declared allow_overlap).
    for label, value in (("upper", tilt.motion_limits.upper), ("lower", tilt.motion_limits.lower)):
        with ctx.pose({tilt: value}):
            ctx.fail_if_parts_overlap_in_current_pose(name=f"tube_clears_mount_at_tilt_{label}")

    return ctx.report()


__all__ = [
    "TechnologyTelescopeConfig",
    "ResolvedTechnologyTelescopeConfig",
    "build_telescope",
    "build_seeded_telescope",
    "config_from_seed",
    "resolve_config",
    "run_telescope_tests",
    "slot_choices_for_seed",
    "__modular__",
]
