# SPDX-License-Identifier: Apache-2.0

"""Harmonic drive (strain-wave reducer) — modular procedural template.

Coaxial concentric strain-wave gearbox: a fixed housing/flange root carries a
flexible externally-toothed flexspline, an elliptical wave-generator input cam,
a rigid internally-toothed circular spline and (in rotary mechanisms) a rotating
output flange — all on one central +Z axis with a mount bolt circle and a hollow
central bore.

Slots (exported into ``slot_choices``):

* Slot A ``form_family``  — ③ Primary Form Family of the housing + flexspline body
  (``pancake_flat`` / ``deep_cup`` / ``component_tube`` / ``top_hat``).
* Slot B ``mechanism``    — ② joint topology of the moving members
  (``rotary_revolute`` / ``rotary_continuous`` / ``exploded_prismatic``).
* Slot C ``skeleton``     — ① gear-element decomposition
  (``fused_housing`` / ``separated_elements``).
* multiplicity ``mount_bolts`` — N mount bolts on the fixed flange (N in [8, 30]).

Everything is authored in world coordinates at the assembled (closed) pose;
coaxial revolute/continuous/prismatic joints sit on the +Z symmetry centerline
(origin honesty passes via the centerline / prismatic exemptions), and the only
FIXED joints (output→flexspline, housing→circular_spline) are single-sourced via
``mount_fixed`` onto real ring geometry.
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
    MotionLimits,
    Origin,
    Part,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

from agent.templates._modular import mount_fixed

__modular__ = True

TAU = 2.0 * math.pi


FormFamily = Literal["pancake_flat", "deep_cup", "component_tube", "top_hat"]
Mechanism = Literal["rotary_revolute", "rotary_continuous", "exploded_prismatic"]
Skeleton = Literal["fused_housing", "separated_elements"]
PaletteTheme = Literal["satin_aluminum", "black_oxide", "gray_green", "bronze_gold"]

FORM_MODULES: tuple[FormFamily, ...] = (
    "pancake_flat",
    "deep_cup",
    "component_tube",
    "top_hat",
)
MECHANISM_MODULES: tuple[Mechanism, ...] = (
    "rotary_revolute",
    "rotary_continuous",
    "exploded_prismatic",
)
SKELETON_MODULES: tuple[Skeleton, ...] = ("fused_housing", "separated_elements")


PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "satin_aluminum": {
        "body": (0.72, 0.73, 0.72, 1.0),
        "flange": (0.66, 0.67, 0.68, 1.0),
        "flex": (0.78, 0.58, 0.30, 1.0),
        "teeth": (0.55, 0.56, 0.55, 1.0),
        "bolt": (0.10, 0.11, 0.12, 1.0),
        "cam": (0.08, 0.085, 0.09, 1.0),
        "bearing": (0.90, 0.91, 0.88, 1.0),
        "output": (0.62, 0.64, 0.66, 1.0),
        "spline": (0.20, 0.21, 0.21, 1.0),
    },
    "black_oxide": {
        "body": (0.10, 0.11, 0.12, 1.0),
        "flange": (0.16, 0.17, 0.18, 1.0),
        "flex": (0.55, 0.56, 0.56, 1.0),
        "teeth": (0.30, 0.31, 0.31, 1.0),
        "bolt": (0.02, 0.02, 0.025, 1.0),
        "cam": (0.015, 0.016, 0.018, 1.0),
        "bearing": (0.88, 0.89, 0.86, 1.0),
        "output": (0.30, 0.31, 0.33, 1.0),
        "spline": (0.04, 0.04, 0.05, 1.0),
    },
    "gray_green": {
        "body": (0.38, 0.48, 0.42, 1.0),
        "flange": (0.34, 0.44, 0.39, 1.0),
        "flex": (0.78, 0.58, 0.30, 1.0),
        "teeth": (0.55, 0.56, 0.55, 1.0),
        "bolt": (0.03, 0.035, 0.04, 1.0),
        "cam": (0.08, 0.085, 0.09, 1.0),
        "bearing": (0.90, 0.91, 0.88, 1.0),
        "output": (0.55, 0.60, 0.57, 1.0),
        "spline": (0.10, 0.13, 0.11, 1.0),
    },
    "bronze_gold": {
        "body": (0.55, 0.45, 0.28, 1.0),
        "flange": (0.62, 0.52, 0.32, 1.0),
        "flex": (0.80, 0.66, 0.36, 1.0),
        "teeth": (0.45, 0.40, 0.28, 1.0),
        "bolt": (0.12, 0.10, 0.07, 1.0),
        "cam": (0.10, 0.09, 0.07, 1.0),
        "bearing": (0.90, 0.88, 0.78, 1.0),
        "output": (0.68, 0.58, 0.34, 1.0),
        "spline": (0.22, 0.18, 0.11, 1.0),
    },
}


@dataclass(frozen=True)
class HarmonicDriveConfig:
    form_family: FormFamily | None = None
    mechanism: Mechanism | None = None
    skeleton: Skeleton | None = None
    palette_theme: PaletteTheme = "satin_aluminum"
    bolt_count: int = 12
    frame_scale: float = 1.0
    flex_height_scale: float = 1.0
    bore_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedHarmonicDriveConfig:
    form_family: FormFamily
    mechanism: Mechanism
    skeleton: Skeleton
    palette_theme: PaletteTheme
    bolt_count: int
    frame_scale: float
    flex_height_scale: float
    bore_scale: float
    # Derived radii (metres)
    flange_outer_r: float
    flange_h: float
    bore_r: float
    bolt_circle_r: float
    bolt_head_r: float
    flex_outer_r: float
    flex_inner_r: float
    tooth_count: int
    cam_major_r: float
    cam_minor_r: float
    output_bore_r: float
    output_disk_r: float
    cs_ring_outer_r: float
    # Derived z-planes (metres, world)
    housing_top_z: float
    flex_seat_z: float
    flex_body_h: float
    flex_mouth_z: float
    cam_seat_z: float
    output_disk_z: float
    circular_spline_seat_z: float
    bolt_z: float
    explode_travel: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _sample_bolt_count(rng: random.Random) -> int:
    # Weighted: small N frequent, large N rare (mirrors §8 mount-bolt band).
    band = rng.random()
    if band < 0.5:
        return rng.randint(8, 12)
    if band < 0.85:
        return rng.randint(13, 20)
    return rng.randint(21, 30)


def config_from_seed(seed: int) -> HarmonicDriveConfig:
    # Procedural-first: seed 0 is NOT special-cased; every seed samples the
    # same deterministic domain.
    rng = random.Random(seed)
    return HarmonicDriveConfig(
        form_family=rng.choice(FORM_MODULES),  # type: ignore[arg-type]
        mechanism=rng.choice(MECHANISM_MODULES),  # type: ignore[arg-type]
        skeleton=rng.choice(SKELETON_MODULES),  # type: ignore[arg-type]
        palette_theme=rng.choice(tuple(PALETTES.keys())),  # type: ignore[arg-type]
        bolt_count=_sample_bolt_count(rng),
        frame_scale=round(rng.uniform(0.85, 1.25), 4),
        flex_height_scale=round(rng.uniform(0.85, 1.20), 4),
        bore_scale=round(rng.uniform(0.80, 1.30), 4),
    )


def resolve_config(config: HarmonicDriveConfig) -> ResolvedHarmonicDriveConfig:
    form = config.form_family or "pancake_flat"
    mech = config.mechanism or "rotary_revolute"
    skel = config.skeleton or "fused_housing"
    for value, pool, label in (
        (form, FORM_MODULES, "form_family"),
        (mech, MECHANISM_MODULES, "mechanism"),
        (skel, SKELETON_MODULES, "skeleton"),
    ):
        if value not in pool:
            raise ValueError(f"Unsupported {label}: {value!r}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")

    fs = _clamp(config.frame_scale, 0.85, 1.25)
    fhs = _clamp(config.flex_height_scale, 0.85, 1.20)
    bs = _clamp(config.bore_scale, 0.80, 1.30)
    bolt_count = int(_clamp(config.bolt_count, 8, 30))

    # Independent primary radii, then derived (equation) quantities.
    flange_outer_r = 0.090 * fs
    flange_h = 0.016
    flex_outer_r = 0.052 * fs
    flex_inner_r = flex_outer_r - 0.010  # ~10mm flexspline wall
    # bore <= flex_inner - wall_min (inequality projection).
    bore_r = _clamp(0.020 * fs * bs, 0.010, flex_inner_r - 0.006)
    bolt_head_r = 0.006 * fs
    # bolt circle sits on the flange annulus (inequality: circle + head <= outer).
    bolt_circle_r = _clamp(flange_outer_r - 0.014, bore_r + bolt_head_r + 0.004,
                           flange_outer_r - bolt_head_r - 0.002)
    tooth_count = int(_clamp(round(1200.0 * flex_outer_r), 40, 80))
    # Wave cam: elliptical strain-wave cam — major axis lightly interferes with
    # the flexspline bore wall (real strain wave), minor axis clears.
    cam_major_r = flex_inner_r + 0.0015
    cam_minor_r = flex_inner_r * 0.60
    output_bore_r = _clamp(bore_r + 0.004, bore_r, flex_inner_r - 0.002)
    output_disk_r = flange_outer_r * 0.72
    # Separated circular-spline ring must nest inside the mount-bolt circle
    # (inequality: cs_outer <= bolt_circle_r - bolt_head_r - clearance).
    cs_ring_outer_r = _clamp(
        bolt_circle_r - bolt_head_r - 0.003,
        flex_outer_r + 0.008, flex_outer_r + 0.016,
    )

    # Form-specific z-layout.
    if form == "pancake_flat":
        housing_top_z = flange_h + 0.006
        flex_body_h = 0.014 * fhs
        flex_seat_z = housing_top_z - 0.002
    elif form == "deep_cup":
        housing_top_z = flange_h
        flex_body_h = 0.095 * fhs
        flex_seat_z = flange_h - 0.002
    elif form == "component_tube":
        housing_top_z = flange_h
        flex_body_h = 0.090 * fhs
        flex_seat_z = flange_h - 0.002
    else:  # top_hat
        housing_top_z = flange_h
        flex_body_h = 0.050 * fhs
        flex_seat_z = flange_h - 0.002

    flex_mouth_z = flex_seat_z + flex_body_h
    cam_seat_z = flex_seat_z + 0.30 * flex_body_h
    output_disk_z = flex_mouth_z
    # Seat the separated circular spline just above the mount-bolt heads so the
    # ring never shares a z-band with the bolt cylinders.
    circular_spline_seat_z = flange_h + 0.006
    bolt_z = flange_h
    explode_travel = _clamp(flex_body_h * 1.4 + 0.03, 0.06, 0.18)

    return ResolvedHarmonicDriveConfig(
        form_family=form,
        mechanism=mech,
        skeleton=skel,
        palette_theme=config.palette_theme,
        bolt_count=bolt_count,
        frame_scale=fs,
        flex_height_scale=fhs,
        bore_scale=bs,
        flange_outer_r=flange_outer_r,
        flange_h=flange_h,
        bore_r=bore_r,
        bolt_circle_r=bolt_circle_r,
        bolt_head_r=bolt_head_r,
        flex_outer_r=flex_outer_r,
        flex_inner_r=flex_inner_r,
        tooth_count=tooth_count,
        cam_major_r=cam_major_r,
        cam_minor_r=cam_minor_r,
        output_bore_r=output_bore_r,
        output_disk_r=output_disk_r,
        cs_ring_outer_r=cs_ring_outer_r,
        housing_top_z=housing_top_z,
        flex_seat_z=flex_seat_z,
        flex_body_h=flex_body_h,
        flex_mouth_z=flex_mouth_z,
        cam_seat_z=cam_seat_z,
        output_disk_z=output_disk_z,
        circular_spline_seat_z=circular_spline_seat_z,
        bolt_z=bolt_z,
        explode_travel=explode_travel,
        palette=dict(PALETTES[config.palette_theme]),
    )


# ---------------------------------------------------------------------------
# CadQuery geometry helpers (adapted from the 5-star source records; primitive
# families preserved per AUTHORING §A Rule 3).
# ---------------------------------------------------------------------------
_MESH_TOL = 0.0009
_MESH_ANG = 0.05


def _annular(outer_r: float, inner_r: float, height: float, z0: float = 0.0) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .circle(outer_r)
        .circle(inner_r)
        .extrude(height)
    )


def _solid_cyl(radius: float, height: float, z0: float = 0.0) -> cq.Workplane:
    return cq.Workplane("XY").workplane(offset=z0).circle(radius).extrude(height)


def _pancake_housing_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    body = _annular(r.flange_outer_r, r.bore_r, r.flange_h, 0.0)
    body = body.union(_annular(r.flange_outer_r * 0.66, r.bore_r, 0.006, r.flange_h))
    return body


def _flange_bore_housing_solid(
    r: ResolvedHarmonicDriveConfig, *, ledge_h: float, flange_outer: float | None = None
) -> cq.Workplane:
    fo = flange_outer if flange_outer is not None else r.flange_outer_r
    body = _annular(fo, r.bore_r, r.flange_h, 0.0)
    # Circular-spline bore ledge the flexspline nests through (clearance fit).
    body = body.union(
        _annular(r.flex_outer_r + 0.020, r.flex_outer_r + 0.008, ledge_h, r.flange_h)
    )
    return body


def _tube_housing_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    fo = r.flange_outer_r * 1.04
    # Cylindrical OUTER shroud rising from the flange rim (canister / cup unit).
    # Anchored at the outer edge (not between the flexspline teeth and the race,
    # where at small frame_scale there is no radial room), so the mount bolts and
    # bearing race seat on the exposed flange floor INSIDE the shroud — their
    # surfaces cross the flange-top face and stay connected on every scale — while
    # the flexspline/teeth sit far inside with wide clearance and nothing (output
    # disk, circular spline) can collide with the fixed shroud wall.
    shroud_outer = fo
    shroud_inner = fo - 0.008
    tube_h = r.flex_body_h + 0.010
    body = _annular(fo, r.bore_r, r.flange_h, 0.0)
    body = body.union(_annular(shroud_outer, shroud_inner, tube_h, r.flange_h))
    # Inward top lip for a finished canister mouth (kept well clear of the central
    # output disk / circular spline, which live at far smaller radii).
    body = body.union(_annular(shroud_outer, shroud_inner - 0.004, 0.006, r.flange_h + tube_h))
    return body


def _fused_spline_collar(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    # Rigid circular-spline collar unioned into the housing solid (fused
    # skeleton). Spans from inside the flange up past the spline height so it is
    # always one connected solid with the flange, and so the fused spline-tooth
    # cylinders embed into it (no intra-part island on any form).
    z0 = r.flange_h * 0.5
    top = r.housing_top_z + 0.006
    return _annular(r.flex_outer_r + 0.014, r.flex_outer_r + 0.005, top - z0, z0)


def _housing_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    if r.form_family == "pancake_flat":
        body = _pancake_housing_solid(r)
    elif r.form_family == "deep_cup":
        body = _flange_bore_housing_solid(r, ledge_h=0.030)
    elif r.form_family == "component_tube":
        body = _tube_housing_solid(r)
    else:  # top_hat
        body = _flange_bore_housing_solid(r, ledge_h=0.018)
    if r.skeleton == "fused_housing":
        body = body.union(_fused_spline_collar(r))
    return body


def _pancake_flex_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    return _annular(r.flex_outer_r, r.flex_inner_r, r.flex_body_h, r.flex_seat_z)


def _cup_flex_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    z0 = r.flex_seat_z
    bottom_h = 0.012
    outer = _solid_cyl(r.flex_outer_r, r.flex_body_h, z0)
    void = _solid_cyl(r.flex_inner_r, r.flex_body_h - bottom_h + 0.002, z0 + bottom_h)
    body = outer.cut(void)
    body = body.union(
        _annular(r.flex_outer_r + 0.004, r.flex_inner_r - 0.002, 0.006, z0 + r.flex_body_h - 0.006)
    )
    return body


def _sleeve_flex_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    return _annular(r.flex_outer_r, r.flex_inner_r, r.flex_body_h, r.flex_seat_z)


def _tophat_flex_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    z0 = r.flex_seat_z
    barrel = _annular(r.flex_outer_r, r.flex_inner_r, r.flex_body_h, z0)
    brim_outer = min(r.flange_outer_r * 0.80, r.flange_outer_r - 0.004)
    brim = _annular(brim_outer, r.flex_inner_r, 0.007, z0 + r.flex_body_h - 0.007)
    return barrel.union(brim)


def _flex_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    if r.form_family == "pancake_flat":
        return _pancake_flex_solid(r)
    if r.form_family == "deep_cup":
        return _cup_flex_solid(r)
    if r.form_family == "component_tube":
        return _sleeve_flex_solid(r)
    return _tophat_flex_solid(r)


def _cam_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=r.cam_seat_z)
        .ellipse(r.cam_major_r, r.cam_minor_r)
        .extrude(0.016)
    )


def _output_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    z = r.output_disk_z
    disk = _annular(r.output_disk_r, r.output_bore_r, 0.010, z)
    # Downward pilot / bearing land ring seats into the flexspline mouth and
    # bridges the rotating output to the (fixed-to-output) flexspline.
    pilot = _annular(r.flex_inner_r + 0.003, r.output_bore_r, 0.010, z - 0.010)
    return disk.union(pilot)


def _circular_spline_solid(r: ResolvedHarmonicDriveConfig) -> cq.Workplane:
    z0 = r.circular_spline_seat_z
    inner = r.flex_outer_r + 0.006
    outer = r.cs_ring_outer_r
    ring = _annular(outer, inner, 0.010, z0)
    # Downward seat lip to the flange top — bridges the ring to the housing for a
    # real support/contact path, and stays radially inside the mount-bolt circle.
    ring = ring.union(_annular(outer, inner, z0 - r.flange_h + 0.001, r.flange_h))
    return ring


# ---------------------------------------------------------------------------
# Loop emitters (repeated homogeneous decoration → host visuals, Rule 1).
# ---------------------------------------------------------------------------
def _emit_bolts(part: Part, r: ResolvedHarmonicDriveConfig) -> None:
    head_h = 0.006
    for i in range(r.bolt_count):
        a = TAU * i / r.bolt_count
        part.visual(
            Cylinder(radius=r.bolt_head_r, length=head_h),
            origin=Origin(
                xyz=(
                    r.bolt_circle_r * math.cos(a),
                    r.bolt_circle_r * math.sin(a),
                    r.bolt_z + head_h * 0.5 - 0.002,
                )
            ),
            material="bolt",
            name=f"bolt_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _emit_ext_teeth(part: Part, r: ResolvedHarmonicDriveConfig, z_center: float) -> None:
    tooth_h = min(0.7 * r.flex_body_h, 0.070)
    for i in range(r.tooth_count):
        a = TAU * i / r.tooth_count
        rr = r.flex_outer_r - 0.001
        part.visual(
            Box((0.0035, 0.0070, tooth_h)),
            origin=Origin(
                xyz=(rr * math.cos(a), rr * math.sin(a), z_center),
                rpy=(0.0, 0.0, a),
            ),
            material="teeth",
            name=f"tooth_{i}", material_class_id=("metal.steel_bare" if r.palette_theme in {"satin_aluminum", "gray_green", "bronze_gold"} else "metal.blackened_gunmetal"),
        )


def _emit_bearing_balls(part: Part, r: ResolvedHarmonicDriveConfig) -> None:
    count = 28
    ring_r = r.flange_outer_r * 0.78
    ball_r = 0.0026 * r.frame_scale
    # Seat each ball straddling the bearing-race top face (race spans z in
    # [flange_h-0.002, flange_h+0.004], radially 0.74..0.82*flange_outer_r; the
    # ball ring sits at 0.78*flange_outer_r, dead-centre of that annulus). The
    # centre is dropped 0.4*ball_r below the race top so the lower hemisphere is
    # always embedded in race material while the crown protrudes — the sphere
    # surface therefore crosses the race top face at every frame_scale, giving a
    # guaranteed surface-contact connection (no floating-island artefact).
    race_top_z = r.flange_h + 0.004
    z = race_top_z - 0.4 * ball_r
    for i in range(count):
        a = TAU * i / count
        part.visual(
            Sphere(radius=ball_r),
            origin=Origin(xyz=(ring_r * math.cos(a), ring_r * math.sin(a), z)),
            material="bearing",
            name=f"bearing_ball_{i}", material_class_id="metal.chrome_polished",
        )


# ---------------------------------------------------------------------------
# Slot builders
# ---------------------------------------------------------------------------
def _build_housing(model: ArticulatedObject, r: ResolvedHarmonicDriveConfig) -> Part:
    housing = model.part("housing")
    housing.visual(
        mesh_from_cadquery(_housing_solid(r), "housing_shell", tolerance=_MESH_TOL, angular_tolerance=_MESH_ANG),
        material="body",
        name="housing_shell", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"satin_aluminum", "gray_green", "bronze_gold"} else "metal.blackened_gunmetal"),
    )
    # Bearing-race backing ring + captured ball set (host visuals, Rule 1/4).
    # Embedded 2mm into the flange top so the race (and the balls resting on it)
    # stay connected on every form/scale (no coplanar-face tessellation gap).
    housing.visual(
        mesh_from_cadquery(
            _annular(r.flange_outer_r * 0.82, r.flange_outer_r * 0.74, 0.006, r.flange_h - 0.002),
            "bearing_race",
            tolerance=_MESH_TOL,
        ),
        material="spline",
        name="bearing_race", material_class_id="metal.blackened_gunmetal",
    )
    _emit_bearing_balls(housing, r)
    _emit_bolts(housing, r)
    # Fused skeleton: the rigid circular spline is the collar unioned into the
    # housing solid (see _fused_spline_collar) — no separate parts/visuals.
    return housing


def _build_flexspline(model: ArticulatedObject, r: ResolvedHarmonicDriveConfig) -> Part:
    flex = model.part("flexspline")
    flex.visual(
        mesh_from_cadquery(_flex_solid(r), "flexspline_body", tolerance=_MESH_TOL, angular_tolerance=_MESH_ANG),
        material="flex",
        name="flexspline_body", material_class_id=("metal.copper_bare" if r.palette_theme in {"satin_aluminum", "gray_green", "bronze_gold"} else "metal.stainless_matte"),
    )
    tooth_z = r.flex_seat_z + 0.55 * r.flex_body_h
    _emit_ext_teeth(flex, r, tooth_z)
    return flex


def _build_wave(model: ArticulatedObject, r: ResolvedHarmonicDriveConfig) -> Part:
    wave = model.part("wave_generator")
    wave.visual(
        mesh_from_cadquery(_cam_solid(r), "elliptical_cam", tolerance=_MESH_TOL, angular_tolerance=0.04),
        material="cam",
        name="elliptical_cam", material_class_id="metal.blackened_gunmetal",
    )
    # Center hub / input shaft rising through the bore (interference contact with
    # the flexspline / housing bore provides the wave's support path).
    hub_bottom = r.flange_h * 0.5
    hub_top = r.cam_seat_z + 0.020
    hub_h = max(0.010, hub_top - hub_bottom)
    wave.visual(
        Cylinder(radius=r.bore_r * 0.92, length=hub_h),
        origin=Origin(xyz=(0.0, 0.0, hub_bottom + hub_h * 0.5)),
        material="cam",
        name="center_hub", material_class_id="metal.blackened_gunmetal",
    )
    wave.visual(
        Cylinder(radius=r.bore_r * 0.55, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, hub_top + 0.007)),
        material="output",
        name="input_knob", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"satin_aluminum", "gray_green", "bronze_gold"} else "metal.blackened_gunmetal"),
    )
    return wave


def _build_output(model: ArticulatedObject, r: ResolvedHarmonicDriveConfig) -> Part:
    output = model.part("output_flange")
    output.visual(
        mesh_from_cadquery(_output_solid(r), "output_disk", tolerance=_MESH_TOL, angular_tolerance=_MESH_ANG),
        material="output",
        name="output_disk", material_class_id=("metal.aluminum_bare" if r.palette_theme in {"satin_aluminum", "gray_green", "bronze_gold"} else "metal.blackened_gunmetal"),
    )
    # Groove line + output bolt-hole shadows (host visuals, host-derived radii).
    for i in range(4):
        a = TAU * i / 4 + math.radians(45.0)
        rr = r.output_disk_r * 0.7
        output.visual(
            Cylinder(radius=0.0022, length=0.0016),
            origin=Origin(xyz=(rr * math.cos(a), rr * math.sin(a), r.output_disk_z + 0.010)),
            material="spline",
            name=f"output_hole_{i}", material_class_id="metal.blackened_gunmetal",
        )
    return output


def _build_circular_spline(model: ArticulatedObject, r: ResolvedHarmonicDriveConfig) -> Part:
    cs = model.part("circular_spline")
    cs.visual(
        mesh_from_cadquery(_circular_spline_solid(r), "circular_spline_ring", tolerance=_MESH_TOL, angular_tolerance=_MESH_ANG),
        material="spline",
        name="circular_spline_ring", material_class_id="metal.blackened_gunmetal",
    )
    return cs


def _wave_limits_bounded() -> MotionLimits:
    return MotionLimits(effort=8.0, velocity=20.0, lower=-math.pi, upper=math.pi)


def _build_mechanism(model: ArticulatedObject, r: ResolvedHarmonicDriveConfig) -> None:
    housing = model.get_part("housing")
    flex = model.get_part("flexspline")
    if r.mechanism in ("rotary_revolute", "rotary_continuous"):
        output = _build_output(model, r)
        wave = _build_wave(model, r)
        jtype = (
            ArticulationType.REVOLUTE
            if r.mechanism == "rotary_revolute"
            else ArticulationType.CONTINUOUS
        )
        out_limits = (
            MotionLimits(effort=60.0, velocity=1.5, lower=0.0, upper=math.pi)
            if r.mechanism == "rotary_revolute"
            else MotionLimits(effort=60.0, velocity=1.5)
        )
        wave_limits = (
            _wave_limits_bounded()
            if r.mechanism == "rotary_revolute"
            else MotionLimits(effort=8.0, velocity=60.0)
        )
        # housing -> output_flange (coaxial +Z reduction output).
        model.articulation(
            "housing_to_output",
            jtype,
            parent=housing,
            child=output,
            origin=Origin(),
            axis=(0.0, 0.0, 1.0),
            motion_limits=out_limits,
            meta={"role": "coaxial output flange rotation"},
        )
        # output_flange -> flexspline (bolted, FIXED) — single-sourced onto the
        # shared mount ring band (real ring geometry, not the hollow bore centre).
        mount_r = (r.flex_inner_r + r.flex_outer_r) * 0.5
        mount_z = r.flex_mouth_z - 0.006
        mount_fixed(
            model,
            joint_name="output_to_flexspline",
            parent="output_flange",
            child="flexspline",
            parent_anchor=(mount_r, 0.0, mount_z),
            child_anchor=(mount_r, 0.0, mount_z),
        )
        # housing -> wave_generator (coaxial +Z input).
        model.articulation(
            "housing_to_wave",
            jtype,
            parent=housing,
            child=wave,
            origin=Origin(),
            axis=(0.0, 0.0, 1.0),
            motion_limits=wave_limits,
            meta={"role": "input wave-generator rotation"},
        )
    else:  # exploded_prismatic
        wave = _build_wave(model, r)
        model.articulation(
            "housing_to_flexspline",
            ArticulationType.PRISMATIC,
            parent=housing,
            child=flex,
            origin=Origin(),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=40.0, velocity=0.15, lower=0.0, upper=r.explode_travel),
            meta={"role": "exploded assembly-step slide (flexspline)"},
        )
        model.articulation(
            "flexspline_to_wave",
            ArticulationType.PRISMATIC,
            parent=flex,
            child=wave,
            origin=Origin(),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=30.0, velocity=0.12, lower=0.0, upper=r.explode_travel * 1.1),
            meta={"role": "exploded assembly-step slide (wave generator)"},
        )


def _build_skeleton(model: ArticulatedObject, r: ResolvedHarmonicDriveConfig) -> None:
    if r.skeleton != "separated_elements":
        return
    cs = _build_circular_spline(model, r)
    # Fixed into the housing bore seat (single-sourced onto the seat-lip ring
    # band where both the housing flange and the cs lip carry material).
    seat_r = (r.flex_outer_r + 0.006 + r.cs_ring_outer_r) * 0.5
    mount_fixed(
        model,
        joint_name="housing_to_circular_spline",
        parent="housing",
        child="circular_spline",
        parent_anchor=(seat_r, 0.0, r.flange_h + 0.002),
        child_anchor=(seat_r, 0.0, r.flange_h + 0.002),
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_harmonic_drive(
    config: HarmonicDriveConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="harmonic_drive", assets=assets)
    for token, rgba in r.palette.items():
        model.material(token, rgba=rgba)

    _build_housing(model, r)
    _build_flexspline(model, r)
    _build_mechanism(model, r)
    _build_skeleton(model, r)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_harmonic_drive(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_harmonic_drive(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedHarmonicDriveConfig) -> list[tuple[str, str]]:
    return [
        ("form_family", r.form_family),
        ("mechanism", r.mechanism),
        ("skeleton", r.skeleton),
        ("mount_bolts", f"bolts_n{r.bolt_count}"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _visual_names(part: Part) -> set[str]:
    return {v.name for v in part.visuals if v.name is not None}


def _has(part: Part, name: str) -> bool:
    return name in _visual_names(part)


def _allow(ctx: TestContext, model: ArticulatedObject, a: str, b: str, ea: str, eb: str, reason: str) -> None:
    names = {p.name for p in model.parts}
    if a in names and b in names and _has(model.get_part(a), ea) and _has(model.get_part(b), eb):
        ctx.allow_overlap(model.get_part(a), model.get_part(b), elem_a=ea, elem_b=eb, reason=reason)


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    # The flexspline (with the wave generator riding inside it) is extracted
    # from the housing on its axial joint, losing all body contact.
    for name in ("flexspline", "wave_generator"):
        if name in {p.name for p in model.parts}:
            ctx.allow_isolated_part(
                model.get_part(name),
                reason=f"{name} rides inside the flexspline bore and detaches from the housing when extracted",
            )
    _allow(ctx, model, "flexspline", "housing", "flexspline_body", "housing_shell",
           "Flexspline base is seated into the fixed flange top and nests through the circular-spline bore.")
    _allow(ctx, model, "wave_generator", "flexspline", "elliptical_cam", "flexspline_body",
           "The elliptical wave-generator cam intentionally interferes with the flexspline bore wall (the strain wave).")
    _allow(ctx, model, "wave_generator", "flexspline", "center_hub", "flexspline_body",
           "Wave-generator hub rides inside the flexspline bore.")
    _allow(ctx, model, "wave_generator", "housing", "center_hub", "housing_shell",
           "Wave-generator input hub passes through the central housing bore.")
    _allow(ctx, model, "output_flange", "flexspline", "output_disk", "flexspline_body",
           "Output disk pilot / bearing land seats into the flexspline mouth as the supporting mating face.")
    _allow(ctx, model, "output_flange", "wave_generator", "output_disk", "elliptical_cam",
           "The wave-generator input cam is coaxially captured inside the output flange bore/pilot.")
    _allow(ctx, model, "output_flange", "wave_generator", "output_disk", "center_hub",
           "The wave-generator input hub runs coaxially through the output flange central bore.")
    _allow(ctx, model, "output_flange", "housing", "output_disk", "housing_shell",
           "Output disk overlaps the low housing rim on flat/pancake frames.")
    _allow(ctx, model, "circular_spline", "housing", "circular_spline_ring", "housing_shell",
           "Circular spline ring is bolted into the housing front bore as a seated insert.")
    _allow(ctx, model, "flexspline", "circular_spline", "flexspline_body", "circular_spline_ring",
           "Flexspline nests inside the circular spline and meshes against its internal teeth.")
    _allow(ctx, model, "output_flange", "circular_spline", "output_disk", "circular_spline_ring",
           "Output disk sits just above the circular spline ring on short frames.")


def run_harmonic_drive_tests(
    object_model: ArticulatedObject, config: HarmonicDriveConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model)

    # Compiler baseline (also run by the sweep; explicit here for authoring).
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    parts = {p.name for p in object_model.parts}
    housing = object_model.get_part("housing")
    flex = object_model.get_part("flexspline")

    # ── Category identity ──
    ctx.check("housing_present", "housing" in parts)
    ctx.check("flexspline_present", "flexspline" in parts)
    ctx.check("wave_generator_present", "wave_generator" in parts)
    ctx.check(
        "mount_bolts_present",
        len([v for v in _visual_names(housing) if v.startswith("bolt_")]) == r.bolt_count
        and r.bolt_count == config_bolt_count(config),
        details=f"bolt_count={r.bolt_count}",
    )
    ctx.check(
        "flexspline_has_external_teeth",
        len([v for v in _visual_names(flex) if v.startswith("tooth_")]) == r.tooth_count,
        details=f"tooth_count={r.tooth_count}",
    )
    ctx.check(
        "circular_spline_present_iff_separated",
        ("circular_spline" in parts) == (r.skeleton == "separated_elements"),
        details=f"skeleton={r.skeleton}, has_cs={'circular_spline' in parts}",
    )

    # ── Concentric coaxial stack ──
    # Flexspline / circular_spline part frames are mounted onto their ring
    # geometry via mount_fixed (off-axis frame origin by construction), so
    # concentricity is checked on the GEOMETRY center, not the part frame.
    flex_aabb = ctx.part_world_aabb(flex)
    if flex_aabb is not None:
        cx = 0.5 * (flex_aabb[0][0] + flex_aabb[1][0])
        cy = 0.5 * (flex_aabb[0][1] + flex_aabb[1][1])
        ctx.check(
            "flexspline geometry concentric with axis",
            abs(cx) < 0.0015 and abs(cy) < 0.0015,
            details=f"flex center=({cx:.5f},{cy:.5f})",
        )
    else:
        ctx.fail("flexspline geometry concentric with axis", "flexspline AABB unavailable")
    wave = object_model.get_part("wave_generator")
    ctx.expect_origin_distance(wave, housing, axes="xy", max_dist=0.0006,
                               name="wave generator concentric with housing")

    # ── Mechanism-specific joint semantics + targeted motion ──
    if r.mechanism in ("rotary_revolute", "rotary_continuous"):
        expected = (
            ArticulationType.REVOLUTE
            if r.mechanism == "rotary_revolute"
            else ArticulationType.CONTINUOUS
        )
        out_joint = object_model.get_articulation("housing_to_output")
        wave_joint = object_model.get_articulation("housing_to_wave")
        fix_joint = object_model.get_articulation("output_to_flexspline")
        ctx.check(
            "rotary joints have expected type and +Z axis",
            out_joint.articulation_type == expected
            and wave_joint.articulation_type == expected
            and tuple(out_joint.axis) == (0.0, 0.0, 1.0)
            and tuple(wave_joint.axis) == (0.0, 0.0, 1.0),
            details=f"out={out_joint.articulation_type}/{out_joint.axis}, wave={wave_joint.articulation_type}/{wave_joint.axis}",
        )
        ctx.check(
            "flexspline is FIXED to output flange",
            fix_joint.articulation_type == ArticulationType.FIXED
            and fix_joint.parent == "output_flange"
            and fix_joint.child == "flexspline",
            details=f"{fix_joint.parent}->{fix_joint.child}/{fix_joint.articulation_type}",
        )
        if r.mechanism == "rotary_continuous":
            ctx.check(
                "continuous joints are unbounded",
                out_joint.motion_limits.lower is None and wave_joint.motion_limits.lower is None,
                details="continuous joints must have no positional bounds",
            )
        # Targeted: rotating the input turns the elliptical cam (AABB x-extent changes).
        rest = ctx.part_element_world_aabb(wave, elem="elliptical_cam")
        with ctx.pose({wave_joint: math.pi / 2.0}):
            turned = ctx.part_element_world_aabb(wave, elem="elliptical_cam")
        if rest is not None and turned is not None:
            rest_dx = rest[1][0] - rest[0][0]
            turned_dx = turned[1][0] - turned[0][0]
            ctx.check(
                "input rotation turns elliptical wave generator",
                abs(rest_dx - turned_dx) > 0.002,
                details=f"rest_dx={rest_dx:.5f} turned_dx={turned_dx:.5f}",
            )
        else:
            ctx.fail("input rotation turns elliptical wave generator", "cam AABB unavailable")
        # Targeted: output flange actually rotates (off-axis hole moves).
        out = object_model.get_part("output_flange")
        rest_h = ctx.part_element_world_aabb(out, elem="output_hole_0")
        with ctx.pose({out_joint: 0.8}):
            moved_h = ctx.part_element_world_aabb(out, elem="output_hole_0")
        if rest_h is not None and moved_h is not None:
            rest_cx = 0.5 * (rest_h[0][0] + rest_h[1][0])
            moved_cx = 0.5 * (moved_h[0][0] + moved_h[1][0])
            ctx.check(
                "output flange rotates about the central axis",
                abs(rest_cx - moved_cx) > 0.004,
                details=f"rest_cx={rest_cx:.5f} moved_cx={moved_cx:.5f}",
            )
        else:
            ctx.fail("output flange rotates about the central axis", "output hole AABB unavailable")
    else:  # exploded_prismatic
        flex_joint = object_model.get_articulation("housing_to_flexspline")
        wave_joint = object_model.get_articulation("flexspline_to_wave")
        ctx.check(
            "exploded joints are PRISMATIC +Z",
            flex_joint.articulation_type == ArticulationType.PRISMATIC
            and wave_joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(flex_joint.axis) == (0.0, 0.0, 1.0)
            and tuple(wave_joint.axis) == (0.0, 0.0, 1.0),
            details=f"flex={flex_joint.articulation_type}/{flex_joint.axis}, wave={wave_joint.articulation_type}/{wave_joint.axis}",
        )
        rest_z = ctx.part_world_position(flex)
        with ctx.pose({flex_joint: r.explode_travel}):
            up_z = ctx.part_world_position(flex)
        ctx.check(
            "flexspline slides upward in the exploded view",
            rest_z is not None and up_z is not None and up_z[2] > rest_z[2] + r.explode_travel * 0.8,
            details=f"rest={rest_z}, up={up_z}",
        )
        with ctx.pose({flex_joint: r.explode_travel}):
            ctx.expect_gap(
                flex, housing, axis="z",
                positive_elem="flexspline_body", negative_elem="housing_shell",
                min_gap=0.004,
                name="exploded flexspline clears the housing",
            )

    # ── Rule 5: no through-model at any sampled joint pose ──
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    return ctx.report()


def config_bolt_count(config: HarmonicDriveConfig) -> int:
    return int(_clamp(config.bolt_count, 8, 30))


__all__ = [
    "FormFamily",
    "HarmonicDriveConfig",
    "Mechanism",
    "PaletteTheme",
    "ResolvedHarmonicDriveConfig",
    "Skeleton",
    "__modular__",
    "build_harmonic_drive",
    "build_seeded_harmonic_drive",
    "config_from_seed",
    "resolve_config",
    "run_harmonic_drive_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
