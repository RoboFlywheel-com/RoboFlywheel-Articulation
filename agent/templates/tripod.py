# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``tripod`` (0611).

Follows ``articraft_template_authoring/specs_modular_v1/tripod.md``.

A three-legged equipment support: a central hub/chassis grounding three
deployable (hinged, optionally telescoping) legs, topped by a mounting
interface (fixed threaded stud, or a pan/tilt/ball/gimbal camera head),
optionally raised by a center column.

Mixed pattern:
    hub (root)
      ├─[REVOLUTE leg_hinge ×3 (+PRISMATIC telescoping, +REVOLUTE brace)]→ legs
      └─[optional PRISMATIC center_column_slide + REVOLUTE crank]→ center_column
           └─[REVOLUTE head_pan]→ pan_base
                └─[REVOLUTE head_tilt]→ tilt_head
                     └─[PRISMATIC plate_slide]→ mounting_plate

Slots:
    legs  : single_section (S3) / two_stage (S2) / three_stage (S1) / braced_three_stage (S1)
    column: none / crank_column / boom_column / leveling_column  (tall-hub families only)
    head  : fixed_mount (S3) / three_way_pan_tilt (S1) / ball_head (S2)
            / fluid_video_head / gimbal_head   ← ③ Primary Form Family slot

Adopted sources:
    S1 rec_picturex_0611__tripod__001 — tall black camera tripod, telescoping legs,
       center column crank, 3-way pan/tilt head, braces.
    S2 rec_picturex_0611__tripod__002 — compact ball-head tripod, 2-stage legs.
    S3 rec_picturex_0611__tripod__003 — compact silver tabletop tripod, single-section
       legs, fixed threaded mount.
    + forked variants: fluid_video / gimbal heads, leveling-bowl / reversible-boom
       columns, retractable-spike / suction feet.
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
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    LatheGeometry,
    LoftGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

LegsStyle = Literal["single_section", "two_stage", "three_stage", "braced_three_stage"]
ColumnStyle = Literal["none", "crank_column", "boom_column", "leveling_column"]
HeadStyle = Literal[
    "fixed_mount", "three_way_pan_tilt", "ball_head", "fluid_video_head", "gimbal_head"
]
PaletteStyle = Literal[
    "matte_black", "satin_silver", "brushed_aluminum", "graphite_pro", "carbon_red", "titanium_gray"
]

# Every palette defines the same six keys used by all modules:
#   shell  — main cast body / hub
#   tube   — leg tube stock
#   clamp  — clamp collars / housings
#   metal  — bright machined steel / silver hardware
#   rubber — feet / grips
#   accent — trim ring / identification mark
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "matte_black": {
        "shell": (0.045, 0.050, 0.052, 1.0),
        "tube": (0.115, 0.125, 0.128, 1.0),
        "clamp": (0.020, 0.022, 0.024, 1.0),
        "metal": (0.22, 0.23, 0.24, 1.0),
        "rubber": (0.030, 0.032, 0.034, 1.0),
        "accent": (0.70, 0.055, 0.035, 1.0),
    },
    "satin_silver": {
        "shell": (0.055, 0.060, 0.065, 1.0),
        "tube": (0.105, 0.115, 0.125, 1.0),
        "clamp": (0.225, 0.240, 0.250, 1.0),
        "metal": (0.660, 0.690, 0.700, 1.0),
        "rubber": (0.022, 0.024, 0.026, 1.0),
        "accent": (0.660, 0.690, 0.700, 1.0),
    },
    "brushed_aluminum": {
        "shell": (0.72, 0.74, 0.75, 1.0),
        "tube": (0.70, 0.72, 0.73, 1.0),
        "clamp": (0.79, 0.80, 0.80, 1.0),
        "metal": (0.26, 0.27, 0.27, 1.0),
        "rubber": (0.045, 0.047, 0.050, 1.0),
        "accent": (0.79, 0.80, 0.80, 1.0),
    },
    "graphite_pro": {
        "shell": (0.10, 0.10, 0.11, 1.0),
        "tube": (0.16, 0.17, 0.18, 1.0),
        "clamp": (0.07, 0.07, 0.08, 1.0),
        "metal": (0.55, 0.57, 0.60, 1.0),
        "rubber": (0.020, 0.020, 0.020, 1.0),
        "accent": (0.35, 0.37, 0.40, 1.0),
    },
    "carbon_red": {
        "shell": (0.060, 0.060, 0.070, 1.0),
        "tube": (0.100, 0.100, 0.110, 1.0),
        "clamp": (0.030, 0.030, 0.035, 1.0),
        "metal": (0.50, 0.50, 0.52, 1.0),
        "rubber": (0.020, 0.020, 0.020, 1.0),
        "accent": (0.75, 0.060, 0.050, 1.0),
    },
    "titanium_gray": {
        "shell": (0.55, 0.56, 0.58, 1.0),
        "tube": (0.62, 0.63, 0.64, 1.0),
        "clamp": (0.48, 0.49, 0.50, 1.0),
        "metal": (0.72, 0.73, 0.74, 1.0),
        "rubber": (0.050, 0.050, 0.050, 1.0),
        "accent": (0.80, 0.55, 0.20, 1.0),
    },
}

LEG_AZIMUTHS = (math.radians(-90.0), math.radians(150.0), math.radians(30.0))


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TripodConfig:
    legs_style: LegsStyle = "three_stage"
    column_style: ColumnStyle = "none"
    head_style: HeadStyle = "ball_head"
    palette_style: PaletteStyle = "matte_black"
    height_scale: float = 1.0
    spread_scale: float = 1.0
    name: str = "reference_tripod"


@dataclass(frozen=True)
class ResolvedTripodConfig:
    legs_style: LegsStyle
    column_style: ColumnStyle
    head_style: HeadStyle
    palette_style: PaletteStyle
    height_scale: float
    spread_scale: float
    leg_fold_upper: float
    palette: dict[str, tuple[float, float, float, float]]
    leg_stage_count: int
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


_TALL_LEGS = {"three_stage", "braced_three_stage"}
_STAGE_COUNT = {
    "single_section": 1,
    "two_stage": 2,
    "three_stage": 3,
    "braced_three_stage": 3,
}


def config_from_seed(seed: int) -> TripodConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    palette_style: PaletteStyle = rng.choice(tuple(PALETTES))

    legs_style: LegsStyle = rng.choices(
        ("three_stage", "two_stage", "single_section", "braced_three_stage"),
        weights=(0.35, 0.30, 0.20, 0.15),
    )[0]

    if legs_style in _TALL_LEGS:
        column_style: ColumnStyle = rng.choices(
            ("none", "crank_column", "boom_column", "leveling_column"),
            weights=(0.40, 0.28, 0.16, 0.16),
        )[0]
    else:
        column_style = "none"

    if column_style == "none":
        # fixed_mount reads as the compact tabletop tripod; commoner on short legs.
        if legs_style in ("single_section", "two_stage"):
            head_style: HeadStyle = rng.choices(
                (
                    "ball_head",
                    "fixed_mount",
                    "three_way_pan_tilt",
                    "fluid_video_head",
                    "gimbal_head",
                ),
                weights=(0.30, 0.24, 0.18, 0.14, 0.14),
            )[0]
        else:
            head_style = rng.choices(
                (
                    "three_way_pan_tilt",
                    "ball_head",
                    "fluid_video_head",
                    "gimbal_head",
                    "fixed_mount",
                ),
                weights=(0.28, 0.24, 0.20, 0.18, 0.10),
            )[0]
    else:
        # A raised center column carries an articulated head (never a fixed stud).
        head_style = rng.choices(
            ("three_way_pan_tilt", "ball_head", "fluid_video_head", "gimbal_head"),
            weights=(0.30, 0.26, 0.24, 0.20),
        )[0]

    height_scale = round(rng.uniform(0.85, 1.20), 4)
    spread_scale = round(rng.uniform(0.85, 1.20), 4)

    return TripodConfig(
        legs_style=legs_style,
        column_style=column_style,
        head_style=head_style,
        palette_style=palette_style,
        height_scale=height_scale,
        spread_scale=spread_scale,
        name=f"seeded_tripod_{seed}",
    )


def resolve_config(config: TripodConfig) -> ResolvedTripodConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    legs_style = config.legs_style
    column_style = config.column_style
    head_style = config.head_style

    # Compatibility: a center column needs the tall S1 hub (center sleeve bore).
    if column_style != "none" and legs_style not in _TALL_LEGS:
        column_style = "none"
    # A fixed threaded stud only sits on the bare hub (no raised column).
    if head_style == "fixed_mount" and column_style != "none":
        head_style = "ball_head"

    height_scale = _clamp(config.height_scale, 0.80, 1.25)
    spread_scale = _clamp(config.spread_scale, 0.80, 1.25)
    leg_fold_upper = 0.34

    return ResolvedTripodConfig(
        legs_style=legs_style,
        column_style=column_style,
        head_style=head_style,
        palette_style=config.palette_style,
        height_scale=height_scale,
        spread_scale=spread_scale,
        leg_fold_upper=leg_fold_upper,
        palette=dict(PALETTES[config.palette_style]),
        leg_stage_count=_STAGE_COUNT[legs_style],
        name=config.name,
    )


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _mat(model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]]) -> dict:
    return {key: model.material(key, rgba=rgba) for key, rgba in palette.items()}


def _hollow_tube(outer_radius, inner_radius, z0, z1, name, *, assets):
    shape = (
        cq.Workplane("XY")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(z1 - z0)
        .translate((0.0, 0.0, z0))
    )
    return mesh_from_cadquery(shape, name, assets=assets, tolerance=0.001, angular_tolerance=0.08)


def _rounded_box(size, radius, name, *, assets):
    shape = cq.Workplane("XY").box(*size)
    if radius > 0.0:
        shape = shape.edges().fillet(radius)
    return mesh_from_cadquery(shape, name, assets=assets, tolerance=0.001, angular_tolerance=0.08)


def _distance(a, b):
    return math.sqrt(sum((b[i] - a[i]) ** 2 for i in range(3)))


def _midpoint(a, b):
    return tuple((a[i] + b[i]) * 0.5 for i in range(3))


def _rpy_for_z_axis(a, b):
    dx, dy, dz = (b[i] - a[i] for i in range(3))
    return (0.0, math.atan2(math.hypot(dx, dy), dz), math.atan2(dy, dx))


def _add_member(part, a, b, radius, material, name):
    part.visual(
        Cylinder(radius=radius, length=_distance(a, b)),
        origin=Origin(xyz=_midpoint(a, b), rpy=_rpy_for_z_axis(a, b)),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _leg_direction(azimuth, outward_tilt):
    return (
        math.sin(outward_tilt) * math.cos(azimuth),
        math.sin(outward_tilt) * math.sin(azimuth),
        -math.cos(outward_tilt),
    )


def _point_along(start, direction, distance):
    return tuple(start[i] + direction[i] * distance for i in range(3))


# --------------------------------------------------------------------------- #
# Slot A — legs (each builds the hub and returns (hub_part, seat_z))
# --------------------------------------------------------------------------- #


def _build_single_section_legs(model, r, mats, *, assets):
    """Compact clevis-ear aluminum hub + 3 single-section hinged legs (S3)."""
    h = r.height_scale
    sp = r.spread_scale
    shell, tube, metal, rubber = mats["shell"], mats["tube"], mats["metal"], mats["rubber"]
    pivot_z = 0.210 * h

    hub = model.part("hub")
    hub.visual(
        Cylinder(radius=0.018, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, pivot_z)),
        material=shell,
        name="lower_hub", material_class_id="metal.paint_coated",
    )
    hub.visual(
        Cylinder(radius=0.0145, length=0.015),
        origin=Origin(xyz=(0.0, 0.0, pivot_z + 0.0165)),
        material=shell,
        name="mount_shoulder", material_class_id="metal.paint_coated",
    )
    seat_z = pivot_z + 0.024

    for index, azimuth in enumerate(LEG_AZIMUTHS):
        radial = (math.cos(azimuth), math.sin(azimuth), 0.0)
        tangent = (-math.sin(azimuth), math.cos(azimuth), 0.0)
        center = (0.023 * radial[0], 0.023 * radial[1], pivot_z)
        for ear_name, y0, y1 in (("a", -0.011, -0.005), ("b", 0.005, 0.011)):
            start = tuple(center[k] + y0 * tangent[k] for k in range(3))
            end = tuple(center[k] + y1 * tangent[k] for k in range(3))
            _add_member(hub, start, end, 0.0062, metal, f"hinge_ear_{index}_{ear_name}")

    reach = 0.182 * sp
    drop = 0.188 * h
    for index, azimuth in enumerate(LEG_AZIMUTHS):
        leg = model.part(f"leg_{index}")
        _add_member(leg, (0.0, -0.006, 0.0), (0.0, 0.006, 0.0), 0.0048, metal, "hinge_lug")
        tube_start = (0.003, 0.0, -0.002)
        tube_end = (reach, 0.0, -drop)
        _add_member(leg, tube_start, tube_end, 0.00465, tube, "aluminum_tube")
        ferrule_dir = tuple((tube_end[k] - tube_start[k]) for k in range(3))
        flen = _distance((0, 0, 0), ferrule_dir)
        unit = tuple(ferrule_dir[k] / flen for k in range(3))
        ferrule_a = _point_along(tube_end, unit, -0.006)
        ferrule_b = _point_along(tube_end, unit, 0.004)
        _add_member(leg, ferrule_a, ferrule_b, 0.00505, metal, "foot_ferrule")
        foot_a = _point_along(tube_end, unit, 0.0)
        foot_b = _point_along(tube_end, unit, 0.016)
        _add_member(leg, foot_a, foot_b, 0.0058, rubber, "rubber_foot")
        model.articulation(
            f"leg_hinge_{index}",
            ArticulationType.REVOLUTE,
            parent=hub,
            child=leg,
            origin=Origin(xyz=(0.023 * radial_of(azimuth)[0], 0.023 * radial_of(azimuth)[1], pivot_z),
                          rpy=(0.0, 0.0, azimuth)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=1.2, lower=-0.15, upper=r.leg_fold_upper),
            meta={"positive_motion": "folds leg inward"},
        )
    return hub, seat_z


def radial_of(azimuth):
    return (math.cos(azimuth), math.sin(azimuth), 0.0)


def _build_two_stage_legs(model, r, mats, *, assets):
    """Lathe hub + 3 two-stage telescoping legs with clamp tabs (S2)."""
    h = r.height_scale
    shell, tube, clamp, metal, rubber = (
        mats["shell"], mats["tube"], mats["clamp"], mats["metal"], mats["rubber"]
    )

    # Shared per-leg meshes (built once, reused across the 3 identical legs).
    outer_leg = _rounded_sleeve(0.0220, 0.0160, 0.0200, 0.0140, 0.1760, "outer_leg_sleeve")
    lower_leg = _rounded_prism(0.0158, 0.0098, 0.1420, 0.0022, "lower_leg_tube")
    clamp_collar = _rounded_sleeve(0.0270, 0.0210, 0.0210, 0.0150, 0.0240, "leg_clamp_collar")
    foot = _foot_loft("angled_rubber_foot")

    hub_top_z = 0.270 * h
    hinge_z = 0.246 * h
    hub = model.part("hub")
    hub_profile = [
        (0.000, hub_top_z - 0.038),
        (0.026, hub_top_z - 0.038),
        (0.031, hub_top_z - 0.031),
        (0.031, hub_top_z - 0.018),
        (0.027, hub_top_z - 0.007),
        (0.024, hub_top_z),
        (0.000, hub_top_z),
    ]
    hub.visual(
        mesh_from_geometry(LatheGeometry(hub_profile, segments=48), "tripod_hub_shell"),
        material=shell,
        name="hub_shell", material_class_id="metal.paint_coated",
    )
    hub.visual(
        Cylinder(radius=0.026, length=0.005),
        origin=Origin(xyz=(0.0, 0.0, hub_top_z - 0.002)),
        material=clamp,
        name="head_seat", material_class_id="metal.paint_coated",
    )
    seat_z = hub_top_z

    leg_spread = math.radians(34.0)
    for index, azimuth in enumerate(LEG_AZIMUTHS):
        c, s = math.cos(azimuth), math.sin(azimuth)
        hinge_r = 0.0355
        hinge_xyz = (hinge_r * c, hinge_r * s, hinge_z)
        hub.visual(
            Box((0.0125, 0.0150, 0.0120)),
            origin=Origin(xyz=(0.0280 * c, 0.0280 * s, hinge_z), rpy=(0.0, 0.0, azimuth)),
            material=shell,
            name=f"pivot_bridge_{index}", material_class_id="metal.paint_coated",
        )
        hub.visual(
            Cylinder(radius=0.0054, length=0.0220),
            origin=Origin(xyz=hinge_xyz, rpy=(math.pi / 2.0, 0.0, azimuth)),
            material=metal,
            name=f"pivot_pin_{index}", material_class_id="metal.chrome_polished",
        )

        upper = model.part(f"upper_leg_{index}")
        upper.visual(
            Cylinder(radius=0.0070, length=0.0180),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=tube,
            name="hinge_barrel", material_class_id="metal.aluminum_bare",
        )
        upper.visual(
            Box((0.0220, 0.0160, 0.0250)),
            origin=Origin(xyz=(0.0, 0.0, -0.0160)),
            material=shell,
            name="upper_shoulder", material_class_id="metal.paint_coated",
        )
        upper.visual(outer_leg, origin=Origin(xyz=(0.0, 0.0, -0.0910)), material=shell,
                     name="outer_sleeve", material_class_id="metal.paint_coated")
        upper.visual(
            Box((0.0170, 0.0012, 0.1260)),
            origin=Origin(xyz=(0.0, -0.00805, -0.0930)),
            material=tube,
            name="recessed_face", material_class_id="metal.aluminum_bare",
        )
        upper.visual(clamp_collar, origin=Origin(xyz=(0.0, 0.0, -0.1630)), material=clamp,
                     name="clamp_collar", material_class_id="plastic.opaque_glossy_molded")
        # Clamp flip tab folded as a non-articulating host visual (Rule 1).
        upper.visual(
            Box((0.0090, 0.0110, 0.0260)),
            origin=Origin(xyz=(0.0170, 0.0, -0.1560)),
            material=clamp,
            name="clamp_lever_tab", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"leg_hinge_{index}",
            ArticulationType.REVOLUTE,
            parent=hub,
            child=upper,
            origin=Origin(xyz=hinge_xyz, rpy=(0.0, -leg_spread, azimuth)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=1.8, lower=-0.20, upper=r.leg_fold_upper),
            meta={"positive_motion": "folds the leg inward"},
        )

        lower = model.part(f"lower_leg_{index}")
        lower.visual(lower_leg, origin=Origin(xyz=(0.0, 0.0, -0.0500)), material=tube,
                     name="inner_tube", material_class_id="metal.aluminum_bare")
        lower.visual(
            Box((0.0170, 0.0110, 0.0080)),
            origin=Origin(xyz=(0.0, 0.0, -0.1160)),
            material=clamp,
            name="foot_socket", material_class_id="plastic.opaque_glossy_molded",
        )
        lower.visual(foot, material=rubber, name="rubber_foot", material_class_id="rubber.smooth_plain")
        model.articulation(
            f"leg_extension_{index}",
            ArticulationType.PRISMATIC,
            parent=upper,
            child=lower,
            origin=Origin(xyz=(0.0, 0.0, -0.1420)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=45.0, velocity=0.16, lower=0.0, upper=0.035),
        )
    return hub, seat_z


def _rounded_prism(width, depth, height, radius, name):
    geometry = ExtrudeGeometry(
        rounded_rect_profile(width, depth, radius, corner_segments=6), height, center=True
    )
    return mesh_from_geometry(geometry, name)


def _rounded_sleeve(ow, od, iw, idp, height, name):
    geometry = ExtrudeWithHolesGeometry(
        rounded_rect_profile(ow, od, min(ow, od) * 0.18),
        [rounded_rect_profile(iw, idp, min(iw, idp) * 0.17)],
        height,
        center=True,
    )
    return mesh_from_geometry(geometry, name)


def _foot_loft(name):
    top = rounded_rect_profile(0.0170, 0.0120, 0.0024, corner_segments=6)
    middle = rounded_rect_profile(0.0200, 0.0155, 0.0032, corner_segments=6)
    bottom = rounded_rect_profile(0.0230, 0.0185, 0.0040, corner_segments=6)
    geometry = LoftGeometry(
        [
            [(x, y, -0.116) for x, y in top],
            [(x + 0.0010, y, -0.130) for x, y in middle],
            [(x + 0.0022, y, -0.145) for x, y in bottom],
        ],
        cap=True,
        closed=True,
    )
    return mesh_from_geometry(geometry, name)


def _build_tall_legs(model, r, mats, *, braced, assets):
    """Tall spider chassis + 3 three-stage telescoping legs (+braces) (S1)."""
    h = r.height_scale
    sp = r.spread_scale
    shell, tube, metal, rubber, accent = (
        mats["shell"], mats["tube"], mats["metal"], mats["rubber"], mats["accent"]
    )

    chassis = model.part("chassis")
    chassis.visual(
        _hollow_tube(0.026, 0.0182, 0.34 * h, 0.965 * h, "tripod_center_sleeve", assets=assets),
        material=tube,
        name="center_sleeve", material_class_id="metal.aluminum_bare",
    )
    chassis.visual(
        _hollow_tube(0.056, 0.027, 0.805 * h, 0.925 * h, "tripod_spider", assets=assets),
        material=shell,
        name="spider", material_class_id="metal.paint_coated",
    )
    chassis.visual(
        _hollow_tube(0.035, 0.0255, 0.505 * h, 0.565 * h, "tripod_brace_collar", assets=assets),
        material=shell,
        name="brace_collar", material_class_id="metal.paint_coated",
    )
    chassis.visual(
        _hollow_tube(0.033, 0.0152, 0.925 * h, 0.965 * h, "tripod_column_clamp", assets=assets),
        material=shell,
        name="column_clamp", material_class_id="metal.paint_coated",
    )
    chassis.visual(
        Box((0.030, 0.020, 0.050)),
        origin=Origin(xyz=(-0.046, -0.018, 0.845 * h)),
        material=shell,
        name="crank_mount", material_class_id="metal.paint_coated",
    )

    hinge_z = 0.865 * h
    seat_z = 0.965 * h

    # spread_scale widens the leg splay via the outward tilt (feet spread wider);
    # the hip radius stays fixed so the hinge always sits on the cast leg lug (S1).
    tilt_gain = _clamp(sp, 0.80, 1.25)
    leg_specs = (
        (0, LEG_AZIMUTHS[0], math.radians(17.0) * tilt_gain, 0.870),
        (1, LEG_AZIMUTHS[1], math.radians(20.5) * tilt_gain, 0.885),
        (2, LEG_AZIMUTHS[2], math.radians(19.5) * tilt_gain, 0.885),
    )
    leg_data = []
    for index, azimuth, tilt, total_length in leg_specs:
        radial = radial_of(azimuth)
        hip = (0.071 * radial[0], 0.071 * radial[1], hinge_z)
        direction = _leg_direction(azimuth, tilt)
        lug_start = (0.040 * radial[0], 0.040 * radial[1], hinge_z)
        lug_end = (0.062 * radial[0], 0.062 * radial[1], hinge_z)
        _add_member(chassis, lug_start, lug_end, 0.007, shell, f"leg_lug_{index}")
        leg_data.append((index, azimuth, tilt, total_length, hip, direction))

    for index, azimuth, tilt, total_length, hip, direction in leg_data:
        upper = model.part(f"upper_leg_{index}")
        upper.visual(
            Cylinder(radius=0.009, length=0.028),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=metal,
            name="hip_barrel", material_class_id="metal.chrome_polished",
        )
        upper.visual(
            _hollow_tube(0.0142, 0.0110, 0.006, 0.430 * h, f"tripod_upper_leg_{index}", assets=assets),
            material=tube,
            name="upper_tube", material_class_id="metal.aluminum_bare",
        )
        upper.visual(
            _hollow_tube(0.0190, 0.0100, 0.414 * h, 0.442 * h, f"tripod_upper_clamp_{index}",
                         assets=assets),
            material=shell,
            name="upper_clamp", material_class_id="metal.paint_coated",
        )
        upper.visual(
            Box((0.013, 0.020, 0.022)),
            origin=Origin(xyz=(0.0205, 0.0, 0.428 * h)),
            material=shell,
            name="upper_clamp_housing", material_class_id="metal.paint_coated",
        )
        if index == 0:
            upper.visual(
                Box((0.0025, 0.012, 0.100)),
                origin=Origin(xyz=(0.0140, -0.001, 0.310 * h)),
                material=accent,
                name="red_identification_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
        model.articulation(
            f"leg_hinge_{index}",
            ArticulationType.REVOLUTE,
            parent=chassis,
            child=upper,
            origin=Origin(xyz=hip, rpy=(0.0, math.pi - tilt, azimuth)),
            axis=(0.0, 1.0, 0.0),
            # Tall telescoping legs fold toward the fat center column; keep the
            # deploy/fold swing small so the mid section clears the sleeve/collar.
            motion_limits=MotionLimits(effort=35.0, velocity=1.2, lower=-0.14, upper=0.16),
        )

        middle = model.part(f"middle_leg_{index}")
        middle.visual(
            _hollow_tube(0.0100, 0.0072, -0.090, 0.250 * h, f"tripod_middle_leg_{index}",
                         assets=assets),
            material=metal,
            name="middle_tube", material_class_id="metal.chrome_polished",
        )
        middle.visual(
            _hollow_tube(0.0152, 0.0062, 0.234 * h, 0.263 * h, f"tripod_middle_clamp_{index}",
                         assets=assets),
            material=shell,
            name="middle_clamp", material_class_id="metal.paint_coated",
        )
        middle.visual(
            Box((0.012, 0.018, 0.022)),
            origin=Origin(xyz=(0.0175, 0.0, 0.248 * h)),
            material=shell,
            name="middle_clamp_housing", material_class_id="metal.paint_coated",
        )
        model.articulation(
            f"upper_to_middle_{index}",
            ArticulationType.PRISMATIC,
            parent=upper,
            child=middle,
            origin=Origin(xyz=(0.0, 0.0, 0.430 * h)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=90.0, velocity=0.20, lower=-0.055, upper=0.090),
        )

        lower_visible = total_length * h - 0.680 * h
        lower = model.part(f"lower_leg_{index}")
        lower.visual(
            Cylinder(radius=0.0062, length=lower_visible + 0.075),
            origin=Origin(xyz=(0.0, 0.0, (lower_visible - 0.075) * 0.5)),
            material=metal,
            name="lower_tube", material_class_id="metal.chrome_polished",
        )
        lower.visual(
            Cylinder(radius=0.0090, length=0.020),
            origin=Origin(xyz=(0.0, 0.0, lower_visible + 0.004)),
            material=rubber,
            name="foot_socket", material_class_id="rubber.smooth_plain",
        )
        lower.visual(
            Sphere(radius=0.0165),
            origin=Origin(xyz=(0.0, 0.0, lower_visible + 0.018)),
            material=rubber,
            name="rubber_foot", material_class_id="rubber.smooth_plain",
        )
        model.articulation(
            f"middle_to_lower_{index}",
            ArticulationType.PRISMATIC,
            parent=middle,
            child=lower,
            origin=Origin(xyz=(0.0, 0.0, 0.250 * h)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=75.0, velocity=0.22, lower=-0.045, upper=0.075),
        )

        if braced:
            radial = radial_of(azimuth)
            brace_start = (0.040 * radial[0], 0.040 * radial[1], 0.535 * h)
            brace_target = _point_along(hip, direction, 0.500)
            brace_length = max(0.05, _distance(brace_start, brace_target) - 0.060)
            unit = tuple(
                (brace_target[k] - brace_start[k]) / _distance(brace_start, brace_target)
                for k in range(3)
            )
            brace_end = _point_along(brace_start, unit, brace_length)
            brace = model.part(f"brace_{index}")
            brace.visual(Sphere(radius=0.0053), origin=Origin(), material=metal, name="brace_eye", material_class_id="metal.chrome_polished")
            brace.visual(
                Cylinder(radius=0.0042, length=brace_length - 0.004),
                origin=Origin(xyz=(0.0, 0.0, (brace_length + 0.004) * 0.5)),
                material=metal,
                name="brace_rod", material_class_id="metal.chrome_polished",
            )
            brace.visual(
                Sphere(radius=0.005),
                origin=Origin(xyz=(0.0, 0.0, brace_length)),
                material=metal,
                name="outer_eye", material_class_id="metal.chrome_polished",
            )
            model.articulation(
                f"brace_hinge_{index}",
                ArticulationType.REVOLUTE,
                parent=chassis,
                child=brace,
                origin=Origin(xyz=brace_start, rpy=_rpy_for_z_axis(brace_start, brace_end)),
                axis=(0.0, 1.0, 0.0),
                # Deployed center brace is a near-locked strut coupled to the leg;
                # only a small take-up swing so it never sweeps across the leg tube.
                motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=-0.05, upper=0.05),
            )
    return chassis, seat_z


# --------------------------------------------------------------------------- #
# Slot B — center column (returns mount_part + head_pan origin z in that frame)
# --------------------------------------------------------------------------- #


def _build_column(model, r, mats, *, hub, seat_z, assets):
    """Build the optional center column; return (mount_part, pan_origin_z)."""
    if r.column_style == "none":
        return hub, seat_z

    shell, metal, rubber = mats["shell"], mats["metal"], mats["rubber"]
    column = model.part("center_column")
    column.visual(
        Cylinder(radius=0.0152, length=0.360),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=metal,
        name="column_tube", material_class_id="metal.chrome_polished",
    )
    if r.column_style == "leveling_column":
        column.visual(
            _leveling_bowl_cap("tripod_leveling_bowl_cap", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, 0.171)),
            material=shell,
            name="column_top_cap", material_class_id="metal.paint_coated",
        )
    else:
        column.visual(
            Cylinder(radius=0.021, length=0.018),
            origin=Origin(xyz=(0.0, 0.0, 0.171)),
            material=shell,
            name="column_top_cap", material_class_id="metal.paint_coated",
        )
    if r.column_style == "boom_column":
        column.visual(
            _rounded_box((0.064, 0.070, 0.066), 0.009, "tripod_boom_pivot_housing", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, 0.150)),
            material=shell,
            name="boom_pivot_housing", material_class_id="metal.paint_coated",
        )
    model.articulation(
        "center_column_slide",
        ArticulationType.PRISMATIC,
        parent=hub,
        child=column,
        origin=Origin(xyz=(0.0, 0.0, seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.12, lower=-0.08, upper=0.20),
    )

    # The crank rotates about a radial (X) shaft mounted outboard of the fat
    # spider, so its handle sweeps a vertical circle in the Y-Z plane and never
    # crosses the center column.
    crank = model.part("column_crank")
    crank.visual(
        Cylinder(radius=0.006, length=0.026, ),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal,
        name="crank_pivot", material_class_id="metal.chrome_polished",
    )
    crank_curve = tube_from_spline_points(
        [(-0.004, 0.0, 0.0), (-0.010, 0.0, -0.022), (-0.012, 0.0, -0.044), (-0.012, 0.010, -0.052)],
        radius=0.0042,
        samples_per_segment=12,
        radial_segments=14,
        cap_ends=True,
    )
    crank.visual(mesh_from_geometry(crank_curve, "tripod_column_crank_arm"), material=shell,
                 name="crank_arm", material_class_id="metal.paint_coated")
    crank.visual(
        Cylinder(radius=0.008, length=0.040),
        origin=Origin(xyz=(-0.020, 0.010, -0.052), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="crank_grip", material_class_id="rubber.smooth_plain",
    )
    model.articulation(
        "column_crank_turn",
        ArticulationType.REVOLUTE,
        parent=hub,
        child=crank,
        origin=Origin(xyz=(-0.070, -0.018, seat_z - 0.120)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=5.0, lower=-math.pi, upper=math.pi),
    )
    return column, 0.180


def _leveling_bowl_cap(name, *, assets):
    outer = cq.Workplane("XY").sphere(0.030)
    lower_half = cq.Workplane("XY").box(0.08, 0.08, 0.030).translate((0.0, 0.0, -0.015))
    inner = cq.Workplane("XY").sphere(0.024)
    bowl = outer.intersect(lower_half).cut(inner)
    neck = cq.Workplane("XY").circle(0.016).extrude(-0.020)
    lip = cq.Workplane("XY").circle(0.030).circle(0.026).extrude(0.006)
    shape = bowl.union(neck).union(lip)
    return mesh_from_cadquery(shape, name, assets=assets, tolerance=0.001, angular_tolerance=0.08)


# --------------------------------------------------------------------------- #
# Slot C — head (③ Primary Form Family)
# --------------------------------------------------------------------------- #


def _build_fork_pan_base(model, r, mats, *, mount_part, pan_origin_z):
    """S1 pan base: drum + rounded body + two fork cheeks. Returns pan_base part."""
    shell = mats["shell"]
    pan_base = model.part("pan_base")
    pan_base.visual(
        Cylinder(radius=0.036, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.015)),
        material=shell,
        name="pan_drum", material_class_id="metal.paint_coated",
    )
    pan_base.visual(
        _rounded_box((0.078, 0.064, 0.052), 0.006, "tripod_pan_body", assets=r_assets(model)),
        origin=Origin(xyz=(0.0, 0.0, 0.050)),
        material=shell,
        name="pan_body", material_class_id="metal.paint_coated",
    )
    for side in (-1.0, 1.0):
        pan_base.visual(
            _rounded_box((0.030, 0.013, 0.074), 0.004, f"tripod_head_cheek_{int(side)}",
                         assets=r_assets(model)),
            origin=Origin(xyz=(0.0, side * 0.027, 0.079)),
            material=shell,
            name=f"fork_cheek_{int(side)}", material_class_id="metal.paint_coated",
        )
    model.articulation(
        "head_pan",
        ArticulationType.REVOLUTE,
        parent=mount_part,
        child=pan_base,
        origin=Origin(xyz=(0.0, 0.0, pan_origin_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=10.0, velocity=2.0, lower=-math.pi, upper=math.pi),
    )
    return pan_base


def r_assets(model):
    return model.assets


def _add_quick_plate(model, r, mats, *, tilt_head):
    shell, metal, rubber = mats["shell"], mats["metal"], mats["rubber"]
    plate = model.part("mounting_plate")
    plate.visual(
        _rounded_box((0.118, 0.076, 0.012), 0.005, "tripod_quick_plate", assets=r_assets(model)),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material=shell,
        name="plate_shell", material_class_id="metal.paint_coated",
    )
    plate.visual(
        Box((0.082, 0.048, 0.004)),
        origin=Origin(xyz=(0.0, 0.0, 0.014)),
        material=rubber,
        name="camera_pad", material_class_id="rubber.smooth_plain",
    )
    plate.visual(
        Cylinder(radius=0.006, length=0.010),
        origin=Origin(xyz=(-0.020, 0.0, 0.019)),
        material=metal,
        name="mount_screw", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "plate_slide",
        ArticulationType.PRISMATIC,
        parent=tilt_head,
        child=plate,
        origin=Origin(xyz=(0.0, 0.0, 0.079)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.08, lower=-0.018, upper=0.018),
    )


def _build_three_way_head(model, r, mats, *, mount_part, pan_origin_z):
    pan_base = _build_fork_pan_base(model, r, mats, mount_part=mount_part, pan_origin_z=pan_origin_z)
    shell, metal, rubber = mats["shell"], mats["metal"], mats["rubber"]
    tilt = model.part("tilt_head")
    tilt.visual(
        Cylinder(radius=0.020, length=0.043),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="tilt_barrel", material_class_id="metal.chrome_polished",
    )
    tilt.visual(
        _rounded_box((0.074, 0.042, 0.060), 0.007, "tripod_tilt_body", assets=r_assets(model)),
        origin=Origin(xyz=(0.012, 0.0, 0.031)),
        material=shell,
        name="tilt_body", material_class_id="metal.paint_coated",
    )
    tilt.visual(
        Box((0.066, 0.052, 0.026)),
        origin=Origin(xyz=(0.006, 0.0, 0.066)),
        material=shell,
        name="plate_support", material_class_id="metal.paint_coated",
    )
    handle = tube_from_spline_points(
        [(0.025, -0.018, 0.020), (0.085, -0.027, 0.008), (0.160, -0.037, -0.006),
         (0.218, -0.043, -0.012)],
        radius=0.006,
        samples_per_segment=14,
        radial_segments=16,
        cap_ends=True,
    )
    tilt.visual(mesh_from_geometry(handle, "tripod_pan_handle"), material=shell,
                name="pan_handle_shaft", material_class_id="metal.paint_coated")
    _add_member(tilt, (0.205, -0.043, -0.012), (0.277, -0.049, -0.020), 0.013, rubber,
                "pan_handle_grip")
    model.articulation(
        "head_tilt",
        ArticulationType.REVOLUTE,
        parent=pan_base,
        child=tilt,
        origin=Origin(xyz=(0.0, 0.0, 0.098)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.5, lower=-0.85, upper=0.90),
    )
    _add_quick_plate(model, r, mats, tilt_head=tilt)


def _build_fluid_video_head(model, r, mats, *, mount_part, pan_origin_z):
    pan_base = _build_fork_pan_base(model, r, mats, mount_part=mount_part, pan_origin_z=pan_origin_z)
    shell, metal, rubber = mats["shell"], mats["metal"], mats["rubber"]
    tilt = model.part("tilt_head")
    tilt.visual(
        Cylinder(radius=0.011, length=0.048),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="tilt_spindle", material_class_id="metal.chrome_polished",
    )
    tilt.visual(
        Cylinder(radius=0.026, length=0.050),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=shell,
        name="fluid_cartridge", material_class_id="metal.paint_coated",
    )
    tilt.visual(
        _fluid_head_shell("tripod_fluid_head_shell", assets=r_assets(model)),
        origin=Origin(),
        material=shell,
        name="fluid_head_shell", material_class_id="metal.paint_coated",
    )
    tilt.visual(
        Box((0.066, 0.052, 0.026)),
        origin=Origin(xyz=(0.006, 0.0, 0.066)),
        material=shell,
        name="plate_support", material_class_id="metal.paint_coated",
    )
    handle = tube_from_spline_points(
        [(0.025, -0.018, 0.020), (0.085, -0.027, 0.008), (0.160, -0.037, -0.006),
         (0.218, -0.043, -0.012)],
        radius=0.006,
        samples_per_segment=14,
        radial_segments=16,
        cap_ends=True,
    )
    tilt.visual(mesh_from_geometry(handle, "tripod_fluid_pan_handle"), material=shell,
                name="pan_handle_shaft", material_class_id="metal.paint_coated")
    _add_member(tilt, (0.205, -0.043, -0.012), (0.277, -0.049, -0.020), 0.013, rubber,
                "pan_handle_grip")
    model.articulation(
        "head_tilt",
        ArticulationType.REVOLUTE,
        parent=pan_base,
        child=tilt,
        origin=Origin(xyz=(0.0, 0.0, 0.098)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=18.0, velocity=1.0, lower=-0.85, upper=0.90),
    )
    _add_quick_plate(model, r, mats, tilt_head=tilt)


def _fluid_head_shell(name, *, assets):
    shape = (
        cq.Workplane("XZ")
        .moveTo(-0.035, -0.006)
        .lineTo(0.024, -0.006)
        .lineTo(0.047, 0.022)
        .lineTo(0.038, 0.055)
        .lineTo(0.018, 0.065)
        .lineTo(-0.030, 0.061)
        .lineTo(-0.043, 0.030)
        .close()
        .extrude(0.022, both=True)
    )
    return mesh_from_cadquery(shape, name, assets=assets, tolerance=0.001, angular_tolerance=0.08)


def _build_gimbal_head(model, r, mats, *, mount_part, pan_origin_z):
    pan_base = _build_fork_pan_base(model, r, mats, mount_part=mount_part, pan_origin_z=pan_origin_z)
    shell, metal, clamp = mats["shell"], mats["metal"], mats["clamp"]
    tilt = model.part("tilt_head")
    tilt.visual(
        Cylinder(radius=0.0175, length=0.038),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="gimbal_axle", material_class_id="metal.chrome_polished",
    )
    for side in (-1.0, 1.0):
        tilt.visual(
            Cylinder(radius=0.0235, length=0.007),
            origin=Origin(xyz=(0.0, side * 0.0225, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=clamp,
            name=f"gimbal_hub_{int(side)}", material_class_id="metal.paint_coated",
        )
    arm = tube_from_spline_points(
        [(0.000, -0.014, 0.000), (-0.018, -0.014, 0.018), (-0.024, -0.014, 0.044),
         (-0.010, -0.014, 0.066)],
        radius=0.009,
        samples_per_segment=14,
        radial_segments=16,
        cap_ends=True,
    )
    tilt.visual(mesh_from_geometry(arm, "tripod_gimbal_swing_arm"), material=shell,
                name="gimbal_swing_arm", material_class_id="metal.paint_coated")
    tilt.visual(
        _rounded_box((0.088, 0.052, 0.018), 0.004, "tripod_gimbal_carriage", assets=r_assets(model)),
        origin=Origin(xyz=(0.010, 0.0, 0.070)),
        material=shell,
        name="plate_support", material_class_id="metal.paint_coated",
    )
    tilt.visual(
        Box((0.070, 0.032, 0.010)),
        origin=Origin(xyz=(0.010, 0.0, 0.057)),
        material=clamp,
        name="gimbal_rail", material_class_id="metal.paint_coated",
    )
    model.articulation(
        "head_tilt",
        ArticulationType.REVOLUTE,
        parent=pan_base,
        child=tilt,
        origin=Origin(xyz=(0.0, 0.0, 0.098)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.5, lower=-0.80, upper=0.85),
    )


def _build_ball_head(model, r, mats, *, mount_part, pan_origin_z):
    shell, clamp, metal, rubber, accent = (
        mats["shell"], mats["clamp"], mats["metal"], mats["rubber"], mats["accent"]
    )
    pan_body = model.part("pan_base")
    pan_profile = [
        (0.000, 0.000), (0.024, 0.000), (0.025, 0.005), (0.0225, 0.009), (0.0225, 0.031),
        (0.0195, 0.037), (0.0175, 0.041), (0.000, 0.041),
    ]
    pan_body.visual(
        mesh_from_geometry(LatheGeometry(pan_profile, segments=48), "pan_body_shell"),
        material=clamp,
        name="head_shell", material_class_id="metal.paint_coated",
    )
    pan_body.visual(
        Cylinder(radius=0.0255, length=0.0030),
        origin=Origin(xyz=(0.0, 0.0, 0.0040)),
        material=accent,
        name="lower_trim_ring", material_class_id="metal.paint_coated",
    )
    pan_body.visual(
        Cylinder(radius=0.0200, length=0.0040),
        origin=Origin(xyz=(0.0, 0.0, 0.0385)),
        material=accent,
        name="upper_trim_ring", material_class_id="metal.paint_coated",
    )
    pan_body.visual(
        Cylinder(radius=0.0190, length=0.0140),
        origin=Origin(xyz=(0.0, 0.0, 0.0470)),
        material=shell,
        name="tilt_socket", material_class_id="metal.paint_coated",
    )
    model.articulation(
        "head_pan",
        ArticulationType.REVOLUTE,
        parent=mount_part,
        child=pan_body,
        origin=Origin(xyz=(0.0, 0.0, pan_origin_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=6.0, velocity=2.2, lower=-math.pi, upper=math.pi),
    )

    tilt = model.part("tilt_head")
    tilt.visual(Sphere(radius=0.0145), material=clamp, name="tilt_ball", material_class_id="metal.chrome_polished")
    tilt.visual(
        Cylinder(radius=0.0085, length=0.0240),
        origin=Origin(xyz=(0.0, 0.0, 0.0220)),
        material=clamp,
        name="plate_stem", material_class_id="metal.chrome_polished",
    )
    tilt.visual(
        Cylinder(radius=0.0245, length=0.0040),
        origin=Origin(xyz=(0.0, 0.0, 0.0330)),
        material=accent,
        name="toothed_ring", material_class_id="metal.paint_coated",
    )
    tilt.visual(
        _rounded_prism(0.0580, 0.0440, 0.0060, 0.0060, "ball_mounting_plate"),
        origin=Origin(xyz=(0.0, 0.0, 0.0375)),
        material=shell,
        name="mounting_plate", material_class_id="metal.paint_coated",
    )
    tilt.visual(
        _rounded_prism(0.0500, 0.0340, 0.0016, 0.0045, "ball_mounting_pad"),
        origin=Origin(xyz=(0.0, 0.0, 0.0413)),
        material=rubber,
        name="camera_pad", material_class_id="rubber.smooth_plain",
    )
    tilt.visual(
        Cylinder(radius=0.0037, length=0.0018),
        origin=Origin(xyz=(0.0, 0.0, 0.0421)),
        material=metal,
        name="mount_screw", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "head_tilt",
        ArticulationType.REVOLUTE,
        parent=pan_body,
        child=tilt,
        origin=Origin(xyz=(0.0, 0.0, 0.0510)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.8, lower=-0.65, upper=0.65),
    )


def _build_fixed_mount_head(model, r, mats, *, mount_part, pan_origin_z):
    """Threaded stud stack fused into the hub visual (no articulation) (S3)."""
    metal = mats["metal"]
    clamp = mats["clamp"]
    z = pan_origin_z
    mount_part.visual(
        Cylinder(radius=0.0115, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, z + 0.005)),
        material=clamp,
        name="mount_platform", material_class_id="metal.paint_coated",
    )
    mount_part.visual(
        Cylinder(radius=0.00315, length=0.013),
        origin=Origin(xyz=(0.0, 0.0, z + 0.016)),
        material=metal,
        name="mounting_stud", material_class_id="metal.chrome_polished",
    )
    for idx, dz in enumerate((0.007, 0.010, 0.013, 0.016)):
        mount_part.visual(
            Cylinder(radius=0.00365, length=0.00135),
            origin=Origin(xyz=(0.0, 0.0, z + dz)),
            material=metal,
            name=f"thread_crest_{idx}", material_class_id="metal.chrome_polished",
        )


_HEAD_BUILDERS = {
    "three_way_pan_tilt": _build_three_way_head,
    "ball_head": _build_ball_head,
    "fluid_video_head": _build_fluid_video_head,
    "gimbal_head": _build_gimbal_head,
    "fixed_mount": _build_fixed_mount_head,
}


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #


def build_tripod(config: TripodConfig | None = None, *, assets: AssetContext | None = None):
    config = config or TripodConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-tripod-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)

    mats = _mat(model, r.palette)

    if r.legs_style == "single_section":
        hub, seat_z = _build_single_section_legs(model, r, mats, assets=assets)
    elif r.legs_style == "two_stage":
        hub, seat_z = _build_two_stage_legs(model, r, mats, assets=assets)
    elif r.legs_style == "three_stage":
        hub, seat_z = _build_tall_legs(model, r, mats, braced=False, assets=assets)
    elif r.legs_style == "braced_three_stage":
        hub, seat_z = _build_tall_legs(model, r, mats, braced=True, assets=assets)
    else:
        raise ValueError(f"Unhandled legs_style: {r.legs_style}")

    mount_part, pan_origin_z = _build_column(model, r, mats, hub=hub, seat_z=seat_z, assets=assets)

    _HEAD_BUILDERS[r.head_style](
        model, r, mats, mount_part=mount_part, pan_origin_z=pan_origin_z
    )
    return model


def build_seeded_tripod(seed: int, *, assets: AssetContext | None = None):
    return build_tripod(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedTripodConfig) -> list[tuple[str, str]]:
    return [
        ("legs", r.legs_style),
        ("leg_stages", str(r.leg_stage_count)),
        ("center_column", r.column_style),
        ("head", r.head_style),
        ("palette_style", r.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _declare_allowances(ctx, model, r):
    parts = {p.name for p in model.parts}

    def allow(a, b, *, reason, elem_a=None, elem_b=None):
        if a in parts and b in parts:
            ctx.allow_overlap(model.get_part(a), model.get_part(b), reason=reason,
                              elem_a=elem_a, elem_b=elem_b)

    hub_name = "chassis" if r.legs_style in _TALL_LEGS else "hub"

    if r.legs_style == "single_section":
        for i in range(3):
            for ear in ("a", "b"):
                allow(hub_name, f"leg_{i}", elem_a=f"hinge_ear_{i}_{ear}", elem_b="hinge_lug",
                      reason="leg lug captured between the hub clevis ears")
    elif r.legs_style == "two_stage":
        for i in range(3):
            # S2: compact captured pivot pin + closely fitted shoulder at each hinge.
            allow(hub_name, f"upper_leg_{i}",
                  reason="captured pivot pin and closely fitted shoulder at the folding-leg hinge")
            allow(f"upper_leg_{i}", f"lower_leg_{i}", elem_a="outer_sleeve", elem_b="inner_tube",
                  reason="inner stage retained inside the outer sleeve")
            allow(f"upper_leg_{i}", f"lower_leg_{i}", elem_a="clamp_collar", elem_b="inner_tube",
                  reason="inner stage passes through the clamp collar bore")
    else:  # tall
        allow("chassis", "center_column", elem_a="column_clamp", elem_b="column_tube",
              reason="center column tube captured by the top guide bushing")
        allow("chassis", "column_crank", elem_a="crank_mount", elem_b="crank_pivot",
              reason="crank shaft is journalled into the crank mount boss")
        allow("chassis", "column_crank", elem_a="crank_mount", elem_b="crank_arm",
              reason="crank arm root sweeps against the crank mount boss")
        for i in range(3):
            # S1: leg hip barrel/tube seated against the cast spider and leg lug.
            allow("chassis", f"upper_leg_{i}",
                  reason="leg hip barrel is seated against the spider and captured leg lug")
            allow(f"upper_leg_{i}", f"middle_leg_{i}", elem_a="upper_clamp", elem_b="middle_tube",
                  reason="middle telescoping tube seated in the upper clamp bushing")
            allow(f"middle_leg_{i}", f"lower_leg_{i}", elem_a="middle_clamp", elem_b="lower_tube",
                  reason="lower telescoping tube seated in the middle clamp bushing")
            if r.legs_style == "braced_three_stage":
                allow("chassis", f"brace_{i}", elem_a="brace_collar", elem_b="brace_eye",
                      reason="brace eye captured at its collar pivot")
                allow(f"brace_{i}", f"upper_leg_{i}",
                      reason="brace strut lands against the upper leg tube it stabilizes")
                allow(f"brace_{i}", f"middle_leg_{i}",
                      reason="brace outer eye rests against the middle leg section it braces")

    # Head bearing + quick-plate rail seats (present for every pan/tilt head).
    allow("pan_base", "tilt_head",
          reason="tilt bearing / ball is captured in the pan-head socket or fork")
    allow("tilt_head", "mounting_plate",
          reason="quick-release plate rides on the tilt-head plate-support rail")
    allow("pan_base", "mounting_plate",
          reason="quick plate passes over the pan-head body at tilt extremes")

    # The raised column carries the whole head stack clear of the chassis.
    for head_part in ("center_column", "mounting_plate", "pan_base", "tilt_head"):
        if head_part in parts:
            ctx.allow_isolated_part(
                model.get_part(head_part),
                reason=f"{head_part} rides the raised column above the chassis legs and loses contact",
            )


def run_tripod_tests(object_model, config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_allowances(ctx, object_model, r)

    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    # Identity: exactly three legs.
    if r.legs_style == "single_section":
        leg_parts = [f"leg_{i}" for i in range(3)]
    else:
        leg_parts = [f"upper_leg_{i}" for i in range(3)]
    ctx.check("three_legs_present", all(n in part_names for n in leg_parts),
              details=str(sorted(part_names)))

    # At least one non-fixed joint (leg hinges always articulate).
    nonfixed = [j for j in object_model.articulations
                if j.articulation_type != ArticulationType.FIXED]
    ctx.check("has_nonfixed_joint", len(nonfixed) >= 3, details=str([j.name for j in nonfixed]))

    # Leg hinge axis/type.
    for i in range(3):
        hj = f"leg_hinge_{i}" if r.legs_style != "single_section" else f"leg_hinge_{i}"
        if hj in joint_names:
            j = object_model.get_articulation(hj)
            ctx.check(f"leg_hinge_{i}_revolute", j.articulation_type == ArticulationType.REVOLUTE)

    # Head pan/tilt joint types where present.
    if "head_pan" in joint_names:
        ctx.check("head_pan_revolute",
                  object_model.get_articulation("head_pan").articulation_type
                  == ArticulationType.REVOLUTE)
    if "head_tilt" in joint_names:
        ctx.check("head_tilt_revolute",
                  object_model.get_articulation("head_tilt").articulation_type
                  == ArticulationType.REVOLUTE)

    # Feet rest near a common support plane.
    foot_parts = leg_parts if r.legs_style == "single_section" else [
        (f"lower_leg_{i}" if r.legs_style != "single_section" else f"leg_{i}") for i in range(3)
    ]
    foot_aabbs = [ctx.part_world_aabb(object_model.get_part(n)) for n in foot_parts
                  if n in part_names]
    if all(a is not None for a in foot_aabbs) and foot_aabbs:
        lowest = min(a[0][2] for a in foot_aabbs)
        ctx.check("feet_near_ground", -0.06 <= lowest <= 0.12, details=f"lowest={lowest:.4f}")

    # Motion QC: no self-intersection across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    # Targeted mechanism poses.
    _targeted_motion_checks(ctx, object_model, r, joint_names)

    return ctx.report()


def _targeted_motion_checks(ctx, model, r, joint_names):
    # Leg telescoping extends the foot outward.
    if r.legs_style == "two_stage" and "leg_extension_0" in joint_names:
        ext = model.get_articulation("leg_extension_0")
        lower = model.get_part("lower_leg_0")
        rest = ctx.part_world_position(lower)
        with ctx.pose({ext: ext.motion_limits.upper}):
            moved = ctx.part_world_position(lower)
        if rest is not None and moved is not None:
            ctx.check("two_stage_leg_extends", _distance(rest, moved) > 0.02,
                      details=f"travel={_distance(rest, moved):.4f}")
    if r.legs_style in _TALL_LEGS and "middle_to_lower_0" in joint_names:
        slide = model.get_articulation("middle_to_lower_0")
        lower = model.get_part("lower_leg_0")
        rest = ctx.part_world_position(lower)
        with ctx.pose({slide: slide.motion_limits.upper}):
            moved = ctx.part_world_position(lower)
        if rest is not None and moved is not None:
            ctx.check("tall_leg_stage_moves", _distance(rest, moved) > 0.03,
                      details=f"travel={_distance(rest, moved):.4f}")

    # Head tilt visibly moves the payload interface.
    if "head_tilt" in joint_names:
        tilt = model.get_articulation("head_tilt")
        plate = model.get_part("mounting_plate") if any(
            p.name == "mounting_plate" for p in model.parts) else model.get_part("tilt_head")
        rest = ctx.part_world_aabb(plate)
        with ctx.pose({tilt: tilt.motion_limits.upper}):
            tilted = ctx.part_world_aabb(plate)
        if rest is not None and tilted is not None:
            moved = (abs(tilted[0][0] - rest[0][0]) > 0.008
                     or abs(tilted[1][2] - rest[1][2]) > 0.004)
            ctx.check("head_tilt_moves_payload", moved, details=f"rest={rest}, tilted={tilted}")

    # Head pan rotates the head.
    if "head_pan" in joint_names:
        pan = model.get_articulation("head_pan")
        head = model.get_part("tilt_head") if any(
            p.name == "tilt_head" for p in model.parts) else model.get_part("pan_base")
        rest = ctx.part_world_position(head)
        with ctx.pose({pan: math.pi / 2.0}):
            panned = ctx.part_world_position(head)
        if rest is not None and panned is not None and (abs(rest[0]) > 0.005 or abs(rest[1]) > 0.005):
            ctx.check("head_pan_rotates", _distance(rest, panned) > 0.004)


__all__ = [
    "TripodConfig",
    "ResolvedTripodConfig",
    "build_tripod",
    "build_seeded_tripod",
    "config_from_seed",
    "resolve_config",
    "run_tripod_tests",
    "slot_choices_for_seed",
    "__modular__",
]
