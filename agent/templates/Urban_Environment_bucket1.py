# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Parametric open sheet-metal fire bucket / utility pail.

This is a self-contained Design-backed rebuild.  The complete reviewed source
pool is recorded in
``articraft_template_authoring/source_maps/Urban_Environment_bucket1.md``.

Only the source-recognizable bucket remains:

* one hollow revolved thin-sheet shell;
* one rolled mouth rim;
* two opposed riveted pivot ears; and
* one steel-wire swing bail on a real horizontal REVOLUTE axis.

The structural domain independently varies four body profiles, three real
sheet-metal mouth-edge constructions, two swing-bail silhouettes and two
riveted-ear forms.  Continuous parameters vary mouth size, depth/aspect, taper,
curvature, standing pad, tip closure, wire gauge and bail rise.  Coherent
material styles add enamel, weathered, galvanized or dark-metal colorways
without adding separate geometry to imitate texture.

The old wall plate, cradle ring, support frame, hook mount, body hoops, lid and
side-grip substitutions are intentionally absent.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    Inertial,
    LatheGeometry,
    MotionLimits,
    MotionProperties,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    TorusGeometry,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    register_interface_mate,
    tube_from_spline_points,
)

__modular__ = True

BodyProfile = Literal[
    "tapered_pail",
    "straight_pail",
    "rounded_bowl",
    "pointed_fire_bucket",
]
RimProfile = Literal["rolled_wire", "flared_fold", "double_bead"]
BailProfile = Literal["round_arch", "shouldered_arch"]
EarStyle = Literal["riveted_strap", "round_stamped_lug"]
MaterialStyle = Literal[
    "fire_red_enamel",
    "safety_yellow_enamel",
    "utility_blue_enamel",
    "forest_green_enamel",
    "galvanized_zinc",
    "weathered_red",
    "hammered_black",
]

BODY_PROFILES: tuple[BodyProfile, ...] = (
    "tapered_pail",
    "straight_pail",
    "rounded_bowl",
    "pointed_fire_bucket",
)
RIM_PROFILES: tuple[RimProfile, ...] = ("rolled_wire", "flared_fold", "double_bead")
BAIL_PROFILES: tuple[BailProfile, ...] = ("round_arch", "shouldered_arch")
EAR_STYLES: tuple[EarStyle, ...] = ("riveted_strap", "round_stamped_lug")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "fire_red_enamel",
    "safety_yellow_enamel",
    "utility_blue_enamel",
    "forest_green_enamel",
    "galvanized_zinc",
    "weathered_red",
    "hammered_black",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "body_profile",
            BODY_PROFILES,
            role="open sheet-metal bucket wall profile and lower closure",
        ),
        component_slot(
            "rim_profile",
            RIM_PROFILES,
            role="structural sheet-metal mouth-edge construction",
        ),
        component_slot(
            "bail_profile",
            BAIL_PROFILES,
            role="single spanning swing-bail silhouette",
        ),
        component_slot(
            "ear_style",
            EAR_STYLES,
            role="paired riveted pivot-ear construction",
        ),
    )
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "fire_red_enamel": {
        "body": (0.72, 0.045, 0.035, 1.0),
        "rim": (0.84, 0.070, 0.055, 1.0),
        "ear": (0.61, 0.030, 0.025, 1.0),
        "wire": (0.72, 0.75, 0.78, 1.0),
    },
    "safety_yellow_enamel": {
        "body": (0.96, 0.66, 0.035, 1.0),
        "rim": (1.00, 0.77, 0.08, 1.0),
        "ear": (0.83, 0.52, 0.02, 1.0),
        "wire": (0.31, 0.33, 0.35, 1.0),
    },
    "utility_blue_enamel": {
        "body": (0.06, 0.30, 0.68, 1.0),
        "rim": (0.10, 0.40, 0.82, 1.0),
        "ear": (0.045, 0.24, 0.56, 1.0),
        "wire": (0.70, 0.73, 0.76, 1.0),
    },
    "forest_green_enamel": {
        "body": (0.06, 0.30, 0.16, 1.0),
        "rim": (0.09, 0.40, 0.22, 1.0),
        "ear": (0.04, 0.24, 0.12, 1.0),
        "wire": (0.67, 0.69, 0.67, 1.0),
    },
    "galvanized_zinc": {
        "body": (0.67, 0.70, 0.72, 1.0),
        "rim": (0.79, 0.81, 0.82, 1.0),
        "ear": (0.58, 0.61, 0.63, 1.0),
        "wire": (0.43, 0.46, 0.48, 1.0),
    },
    "weathered_red": {
        "body": (0.48, 0.075, 0.055, 1.0),
        "rim": (0.62, 0.10, 0.07, 1.0),
        "ear": (0.37, 0.055, 0.04, 1.0),
        "wire": (0.36, 0.34, 0.31, 1.0),
    },
    "hammered_black": {
        "body": (0.075, 0.082, 0.090, 1.0),
        "rim": (0.14, 0.15, 0.16, 1.0),
        "ear": (0.055, 0.060, 0.066, 1.0),
        "wire": (0.43, 0.45, 0.47, 1.0),
    },
}

SHELL_SEGMENTS = 64
PROFILE_STATIONS = 24
RUN_CLEARANCE = 0.00045
EAR_EMBED = 0.004
@dataclass(frozen=True)
class Config:
    body_profile: BodyProfile = "tapered_pail"
    rim_profile: RimProfile = "rolled_wire"
    bail_profile: BailProfile = "round_arch"
    ear_style: EarStyle = "riveted_strap"
    mouth_radius_m: float = 0.140
    body_height_m: float = 0.280
    taper_ratio: float = 0.74
    bowl_depth_ratio: float = 0.96
    standing_pad_ratio: float = 0.15
    pointed_aspect_ratio: float = 1.88
    point_radius_ratio: float = 0.032
    bail_rise_ratio: float = 1.28
    bail_wire_radius_m: float = 0.0030
    material_style: MaterialStyle = "fire_red_enamel"
    name: str = "urban_environment_bucket1"


@dataclass(frozen=True)
class ResolvedConfig:
    body_profile: BodyProfile
    rim_profile: RimProfile
    bail_profile: BailProfile
    ear_style: EarStyle
    mouth_radius_m: float
    body_height_m: float
    taper_ratio: float
    bowl_depth_ratio: float
    standing_pad_ratio: float
    pointed_aspect_ratio: float
    point_radius_ratio: float
    bail_rise_ratio: float
    bail_wire_radius_m: float
    material_style: MaterialStyle
    name: str
    # derived
    wall_m: float
    floor_m: float
    rim_tube_m: float
    base_radius_m: float
    point_radius_m: float
    pivot_z_m: float
    pivot_radius_m: float
    pin_radius_m: float
    eye_major_radius_m: float
    bail_rise_m: float
    ear_height_m: float
    ear_tangent_width_m: float

    @property
    def is_pointed(self) -> bool:
        return self.body_profile == "pointed_fire_bucket"


# Backward-compatible public names used by existing callers.
Bucket1Config = Config
ResolvedBucket1Config = ResolvedConfig


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0xB0C1_2026)
    material_style = rng.choice(MATERIAL_STYLES)
    # Consume the retired decoration draw so existing seeds keep their
    # previously approved structural dimensions after texture geometry removal.
    if material_style.endswith("_enamel"):
        rng.randint(0, 4)
    elif material_style == "galvanized_zinc":
        rng.randint(7, 12)
    else:
        rng.randint(5, 12)
    return Config(
        body_profile=choices["body_profile"],
        rim_profile=choices["rim_profile"],
        bail_profile=choices["bail_profile"],
        ear_style=choices["ear_style"],
        mouth_radius_m=round(rng.uniform(0.105, 0.180), 4),
        body_height_m=round(rng.uniform(0.220, 0.420), 4),
        taper_ratio=round(rng.uniform(0.58, 0.88), 4),
        bowl_depth_ratio=round(rng.uniform(0.78, 1.18), 4),
        standing_pad_ratio=round(rng.uniform(0.10, 0.24), 4),
        pointed_aspect_ratio=round(rng.uniform(1.55, 2.65), 4),
        point_radius_ratio=round(rng.uniform(0.018, 0.060), 4),
        bail_rise_ratio=round(rng.uniform(1.15, 1.55), 4),
        bail_wire_radius_m=round(rng.uniform(0.0022, 0.0042), 5),
        material_style=material_style,
        name=f"urban_environment_bucket1_seed_{seed}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    profile = _pick(cfg.body_profile, BODY_PROFILES)
    rim_profile = _pick(cfg.rim_profile, RIM_PROFILES)
    bail_profile = _pick(cfg.bail_profile, BAIL_PROFILES)
    ear_style = _pick(cfg.ear_style, EAR_STYLES)
    style = _pick(cfg.material_style, MATERIAL_STYLES)
    mouth = _clamp(cfg.mouth_radius_m, 0.105, 0.180)
    nominal_h = _clamp(cfg.body_height_m, 0.220, 0.420)
    taper = _clamp(cfg.taper_ratio, 0.58, 0.88)
    bowl_depth_ratio = _clamp(cfg.bowl_depth_ratio, 0.78, 1.18)
    pad_ratio = _clamp(cfg.standing_pad_ratio, 0.10, 0.24)
    pointed_aspect = _clamp(cfg.pointed_aspect_ratio, 1.55, 2.65)
    point_ratio = _clamp(cfg.point_radius_ratio, 0.018, 0.060)
    wire = _clamp(cfg.bail_wire_radius_m, 0.0022, 0.0042)
    bail_rise_ratio = _clamp(cfg.bail_rise_ratio, 1.15, 1.55)

    wall = _clamp(0.012 * mouth, 0.0012, 0.0022)
    floor = _clamp(2.5 * wall, 0.0030, 0.0060)
    rim_tube = _clamp(0.040 * mouth, 0.0040, 0.0070)

    if profile == "tapered_pail":
        body_h = nominal_h
        base_r = taper * mouth
        point_r = 0.0
    elif profile == "straight_pail":
        body_h = nominal_h
        base_r = mouth
        point_r = 0.0
    elif profile == "rounded_bowl":
        body_h = mouth * bowl_depth_ratio
        base_r = mouth * pad_ratio
        point_r = 0.0
    else:
        body_h = mouth * pointed_aspect
        point_r = mouth * point_ratio
        base_r = point_r

    pivot_z = body_h - max(2.2 * rim_tube, 0.014)
    pin_r = max(0.0018, 0.72 * wire)
    eye_major = pin_r + RUN_CLEARANCE + wire
    pivot_radius = mouth + rim_tube + 2.2 * wire
    bail_rise = max(
        mouth * bail_rise_ratio,
        pivot_radius + eye_major + 1.5 * wire,
    )
    ear_h = max(0.018, 5.0 * wire)
    ear_w = max(0.018, 5.5 * wire)

    return ResolvedConfig(
        body_profile=profile,
        rim_profile=rim_profile,
        bail_profile=bail_profile,
        ear_style=ear_style,
        mouth_radius_m=mouth,
        body_height_m=body_h,
        taper_ratio=taper,
        bowl_depth_ratio=bowl_depth_ratio,
        standing_pad_ratio=pad_ratio,
        pointed_aspect_ratio=pointed_aspect,
        point_radius_ratio=point_ratio,
        bail_rise_ratio=bail_rise_ratio,
        bail_wire_radius_m=wire,
        material_style=style,
        name=cfg.name or "urban_environment_bucket1",
        wall_m=wall,
        floor_m=floor,
        rim_tube_m=rim_tube,
        base_radius_m=base_r,
        point_radius_m=point_r,
        pivot_z_m=pivot_z,
        pivot_radius_m=pivot_radius,
        pin_radius_m=pin_r,
        eye_major_radius_m=eye_major,
        bail_rise_m=bail_rise,
        ear_height_m=ear_h,
        ear_tangent_width_m=ear_w,
    )


def with_overrides(config: Config, **kwargs: object) -> Config:
    return replace(config, **kwargs)


def _body_profile_tapered_pail_build(
    r: ResolvedConfig,
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    base = r.base_radius_m
    mouth = r.mouth_radius_m
    h = r.body_height_m
    outer = [(base, 0.0), ((base + mouth) * 0.5, h * 0.5), (mouth, h)]
    inner_base = base - r.wall_m
    inner_mouth = mouth - r.wall_m
    inner = [
        (0.0, r.floor_m),
        (inner_base, r.floor_m),
        ((inner_base + inner_mouth) * 0.5, h * 0.5),
        (inner_mouth, h),
    ]
    return outer, inner


def _body_profile_straight_pail_build(
    r: ResolvedConfig,
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    radius = r.mouth_radius_m
    h = r.body_height_m
    outer = [(radius, 0.0), (radius, h)]
    inner = [
        (0.0, r.floor_m),
        (radius - r.wall_m, r.floor_m),
        (radius - r.wall_m, h),
    ]
    return outer, inner


def _body_profile_rounded_bowl_build(
    r: ResolvedConfig,
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    mouth = r.mouth_radius_m
    depth = r.body_height_m
    pad = r.base_radius_m
    theta_start = -math.acos(_clamp(pad / mouth, 0.0, 0.999))
    outer: list[tuple[float, float]] = [(pad, 0.0)]
    for i in range(PROFILE_STATIONS + 1):
        theta = theta_start * (1.0 - i / PROFILE_STATIONS)
        outer.append((mouth * math.cos(theta), depth * (1.0 + math.sin(theta))))

    inner_mouth = mouth - r.wall_m
    inner_depth = max(depth - r.wall_m, 0.75 * depth)
    sine = _clamp((r.floor_m - depth) / inner_depth, -0.999, 0.0)
    inner_start = math.asin(sine)
    inner: list[tuple[float, float]] = [
        (0.0, r.floor_m),
        (inner_mouth * math.cos(inner_start), r.floor_m),
    ]
    for i in range(PROFILE_STATIONS + 1):
        theta = inner_start * (1.0 - i / PROFILE_STATIONS)
        inner.append(
            (
                inner_mouth * math.cos(theta),
                depth + inner_depth * math.sin(theta),
            )
        )
    return outer, inner


def _body_profile_pointed_fire_bucket_build(
    r: ResolvedConfig,
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    tip = r.point_radius_m
    mouth = r.mouth_radius_m
    h = r.body_height_m
    outer = [
        (tip, 0.0),
        (0.33 * mouth, 0.32 * h),
        (0.67 * mouth, 0.67 * h),
        (mouth, h),
    ]
    inner = [
        (0.0, 2.0 * r.wall_m),
        (max(0.0006, tip - r.wall_m), 2.7 * r.wall_m),
        (0.33 * mouth - r.wall_m, 0.32 * h),
        (0.67 * mouth - r.wall_m, 0.67 * h),
        (mouth - r.wall_m, h),
    ]
    return outer, inner


_BODY_PROFILE_BUILDERS = {
    "tapered_pail": _body_profile_tapered_pail_build,
    "straight_pail": _body_profile_straight_pail_build,
    "rounded_bowl": _body_profile_rounded_bowl_build,
    "pointed_fire_bucket": _body_profile_pointed_fire_bucket_build,
}


def _radius_at(r: ResolvedConfig, z: float) -> float:
    zc = _clamp(z, 0.0, r.body_height_m)
    t = zc / max(r.body_height_m, 1e-9)
    if r.body_profile == "straight_pail":
        return r.mouth_radius_m
    if r.body_profile == "tapered_pail":
        return r.base_radius_m + (r.mouth_radius_m - r.base_radius_m) * t
    if r.body_profile == "pointed_fire_bucket":
        # Follow the exact authored piecewise cone stations.  A single end-to-
        # end interpolation can sit almost a millimetre outside the deep cone
        # between stations, which is enough to detach a sub-millimetre finish
        # mark from the real faceted shell.
        stations = (
            (0.0, r.point_radius_m),
            (0.32, 0.33 * r.mouth_radius_m),
            (0.67, 0.67 * r.mouth_radius_m),
            (1.0, r.mouth_radius_m),
        )
        for (t0, r0), (t1, r1) in zip(stations, stations[1:]):
            if t <= t1:
                local = (t - t0) / (t1 - t0)
                return r0 + (r1 - r0) * local
        return r.mouth_radius_m
    # Elliptical bowl inverse: z = depth * (1 + sin(theta)).
    sine = _clamp(t - 1.0, -1.0, 0.0)
    return max(
        r.base_radius_m,
        r.mouth_radius_m * math.sqrt(max(0.0, 1.0 - sine * sine)),
    )


def _rim_profile_rolled_wire_build(body, r: ResolvedConfig, mats) -> None:
    rim = TorusGeometry(
        radius=r.mouth_radius_m - 0.35 * r.rim_tube_m,
        tube=r.rim_tube_m,
        radial_segments=20,
        tubular_segments=SHELL_SEGMENTS,
    )
    body.visual(
        mesh_from_geometry(rim, "bucket1_rim_rolled_wire"),
        origin=Origin(xyz=(0.0, 0.0, r.body_height_m)),
        material=mats["rim"],
        name="rim_profile__rolled_wire__mouth_roll", material_class_id=("metal.paint_coated" if r.material_style in {"fire_red_enamel", "safety_yellow_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "hammered_black"} else "rust.painted_weathered"),
    )


def _rim_profile_flared_fold_build(body, r: ResolvedConfig, mats) -> None:
    # A closed revolved sheet-metal fold: the inner edge embeds into the shell
    # termination and the outer edge projects visibly beyond the mouth.
    fold_t = max(1.8 * r.wall_m, 0.0024)
    inner_r = r.mouth_radius_m - 1.2 * r.wall_m
    outer_r = r.mouth_radius_m + 1.65 * r.rim_tube_m
    z = r.body_height_m
    profile = [
        (inner_r, z - 0.75 * fold_t),
        (outer_r, z - 0.20 * fold_t),
        (outer_r, z + 0.80 * fold_t),
        (inner_r, z + 0.35 * fold_t),
    ]
    body.visual(
        mesh_from_geometry(
            LatheGeometry(profile, segments=SHELL_SEGMENTS),
            "bucket1_rim_flared_fold",
        ),
        material=mats["rim"],
        name="rim_profile__flared_fold__outward_lip", material_class_id=("metal.paint_coated" if r.material_style in {"fire_red_enamel", "safety_yellow_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "hammered_black"} else "rust.painted_weathered"),
    )


def _rim_profile_double_bead_build(body, r: ResolvedConfig, mats) -> None:
    bead = max(0.72 * r.rim_tube_m, 0.0034)
    center_r = r.mouth_radius_m - 0.25 * bead
    for i, z_offset in enumerate((0.10 * bead, -1.45 * bead)):
        ring = TorusGeometry(
            radius=center_r,
            tube=bead,
            radial_segments=18,
            tubular_segments=SHELL_SEGMENTS,
        )
        body.visual(
            mesh_from_geometry(ring, f"bucket1_rim_double_bead_{i}"),
            origin=Origin(xyz=(0.0, 0.0, r.body_height_m + z_offset)),
            material=mats["rim"],
            name=f"rim_profile__double_bead__bead_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"fire_red_enamel", "safety_yellow_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "hammered_black"} else "rust.painted_weathered"),
        )


_RIM_PROFILE_BUILDERS = {
    "rolled_wire": _rim_profile_rolled_wire_build,
    "flared_fold": _rim_profile_flared_fold_build,
    "double_bead": _rim_profile_double_bead_build,
}


def _emit_body(body, r: ResolvedConfig, mats) -> None:
    outer, inner = _BODY_PROFILE_BUILDERS[r.body_profile](r)
    shell = LatheGeometry.from_shell_profiles(outer, inner, segments=SHELL_SEGMENTS)
    body.visual(
        mesh_from_geometry(shell, f"bucket1_{r.body_profile}_shell"),
        material=mats["body"],
        name=f"body_profile__{r.body_profile}__hollow_shell", material_class_id=("metal.paint_coated" if r.material_style in {"fire_red_enamel", "safety_yellow_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "hammered_black"} else "rust.painted_weathered"),
    )
    _RIM_PROFILE_BUILDERS[r.rim_profile](body, r, mats)


def _emit_pivot_pin_and_head(
    body,
    r: ResolvedConfig,
    mats,
    *,
    sign: float,
    tag: str,
    head_scale: float,
) -> None:
    wall_r = _radius_at(r, r.pivot_z_m)
    wire = r.bail_wire_radius_m
    pin_outer = r.pivot_radius_m + wire + RUN_CLEARANCE
    pin_inner = wall_r - 0.5 * EAR_EMBED
    pin_len = pin_outer - pin_inner
    pin_center = 0.5 * (pin_outer + pin_inner)
    head_t = max(0.0024, 0.8 * wire)
    head_center = pin_outer + 0.5 * head_t
    head_r = r.eye_major_radius_m + head_scale * wire
    body.visual(
        Cylinder(radius=r.pin_radius_m, length=pin_len),
        origin=Origin(
            xyz=(0.0, sign * pin_center, r.pivot_z_m),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["wire"],
        name=f"ear_style__{r.ear_style}__pivot_pin_{tag}", material_class_id=("metal.steel_bare" if r.material_style in {"fire_red_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "weathered_red"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        Cylinder(radius=head_r, length=head_t),
        origin=Origin(
            xyz=(0.0, sign * head_center, r.pivot_z_m),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["wire"],
        name=f"ear_style__{r.ear_style}__rivet_head_{tag}", material_class_id=("metal.steel_bare" if r.material_style in {"fire_red_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "weathered_red"} else "metal.blackened_gunmetal"),
    )


def _ear_style_riveted_strap_build(body, r: ResolvedConfig, mats) -> None:
    wall_r = _radius_at(r, r.pivot_z_m)
    plate_outer = r.pivot_radius_m - r.bail_wire_radius_m - RUN_CLEARANCE
    plate_inner = wall_r - EAR_EMBED
    plate_span = plate_outer - plate_inner
    plate_center = 0.5 * (plate_outer + plate_inner)
    for sign, tag in ((1.0, "positive"), (-1.0, "negative")):
        body.visual(
            Box((r.ear_tangent_width_m, plate_span, r.ear_height_m)),
            origin=Origin(xyz=(0.0, sign * plate_center, r.pivot_z_m)),
            material=mats["ear"],
            name=f"ear_style__riveted_strap__strap_{tag}", material_class_id=("metal.paint_coated" if r.material_style in {"fire_red_enamel", "safety_yellow_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "hammered_black"} else "rust.painted_weathered"),
        )
        _emit_pivot_pin_and_head(
            body,
            r,
            mats,
            sign=sign,
            tag=tag,
            head_scale=0.55,
        )


def _ear_style_round_stamped_lug_build(body, r: ResolvedConfig, mats) -> None:
    wall_r = _radius_at(r, r.pivot_z_m)
    lug_radius = max(0.010, 0.62 * r.ear_height_m)
    lug_t = max(0.0038, 1.25 * r.bail_wire_radius_m)
    lug_center_radius = (
        r.pivot_radius_m
        - r.bail_wire_radius_m
        - RUN_CLEARANCE
        - 0.5 * lug_t
    )
    neck_inner = wall_r - EAR_EMBED
    neck_outer = lug_center_radius - 0.20 * lug_radius
    neck_span = neck_outer - neck_inner
    neck_center = 0.5 * (neck_outer + neck_inner)
    neck_h = 0.90 * lug_radius
    for sign, tag in ((1.0, "positive"), (-1.0, "negative")):
        body.visual(
            Box((1.15 * lug_radius, neck_span, neck_h)),
            origin=Origin(xyz=(0.0, sign * neck_center, r.pivot_z_m)),
            material=mats["ear"],
            name=f"ear_style__round_stamped_lug__neck_{tag}", material_class_id=("metal.paint_coated" if r.material_style in {"fire_red_enamel", "safety_yellow_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "hammered_black"} else "rust.painted_weathered"),
        )
        body.visual(
            Cylinder(radius=lug_radius, length=lug_t),
            origin=Origin(
                xyz=(0.0, sign * lug_center_radius, r.pivot_z_m),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["ear"],
            name=f"ear_style__round_stamped_lug__disc_{tag}", material_class_id=("metal.paint_coated" if r.material_style in {"fire_red_enamel", "safety_yellow_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "hammered_black"} else "rust.painted_weathered"),
        )
        _emit_pivot_pin_and_head(
            body,
            r,
            mats,
            sign=sign,
            tag=tag,
            head_scale=0.35,
        )


_EAR_STYLE_BUILDERS = {
    "riveted_strap": _ear_style_riveted_strap_build,
    "round_stamped_lug": _ear_style_round_stamped_lug_build,
}


def _emit_pivot_ears(body, r: ResolvedConfig, mats) -> None:
    _EAR_STYLE_BUILDERS[r.ear_style](body, r, mats)


def _bail_profile_round_arch_build(r: ResolvedConfig) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    for i in range(13):
        theta = math.pi * i / 12.0
        y = r.pivot_radius_m * math.cos(theta)
        z = (
            r.eye_major_radius_m * (1.0 - math.sin(theta) ** 2)
            + r.bail_rise_m * math.sin(theta)
        )
        points.append((0.0, y, z))
    return points


def _bail_profile_shouldered_arch_build(
    r: ResolvedConfig,
) -> list[tuple[float, float, float]]:
    side_clear = max(3.0 * r.eye_major_radius_m, 0.20 * r.bail_rise_m)
    return [
        (0.0, r.pivot_radius_m, r.eye_major_radius_m),
        (0.0, r.pivot_radius_m, side_clear),
        (0.0, 0.84 * r.pivot_radius_m, 0.72 * r.bail_rise_m),
        (0.0, 0.56 * r.pivot_radius_m, 0.95 * r.bail_rise_m),
        (0.0, 0.26 * r.pivot_radius_m, r.bail_rise_m),
        (0.0, -0.26 * r.pivot_radius_m, r.bail_rise_m),
        (0.0, -0.56 * r.pivot_radius_m, 0.95 * r.bail_rise_m),
        (0.0, -0.84 * r.pivot_radius_m, 0.72 * r.bail_rise_m),
        (0.0, -r.pivot_radius_m, side_clear),
        (0.0, -r.pivot_radius_m, r.eye_major_radius_m),
    ]


_BAIL_PROFILE_BUILDERS = {
    "round_arch": _bail_profile_round_arch_build,
    "shouldered_arch": _bail_profile_shouldered_arch_build,
}


def _emit_swing_bail(model, body, r: ResolvedConfig, mats):
    bail = model.part(
        "swing_bail",
        meta={
            "role": "swing_bail",
            "candidate": r.bail_profile,
            "wire_radius_m": r.bail_wire_radius_m,
        },
    )
    eye = TorusGeometry(
        radius=r.eye_major_radius_m,
        tube=r.bail_wire_radius_m,
        radial_segments=16,
        tubular_segments=32,
    )
    for sign, tag in ((1.0, "positive"), (-1.0, "negative")):
        bail.visual(
            mesh_from_geometry(eye, f"bucket1_bail_eye_{tag}"),
            origin=Origin(
                xyz=(0.0, sign * r.pivot_radius_m, 0.0),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["wire"],
            name=f"bail_profile__{r.bail_profile}__eye_{tag}", material_class_id=("metal.steel_bare" if r.material_style in {"fire_red_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "weathered_red"} else "metal.blackened_gunmetal"),
        )

    points = _BAIL_PROFILE_BUILDERS[r.bail_profile](r)
    bail.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                points,
                radius=r.bail_wire_radius_m,
                samples_per_segment=8,
                radial_segments=10,
                cap_ends=True,
            ),
            f"bucket1_swing_bail_{r.bail_profile}",
        ),
        material=mats["wire"],
        name=f"bail_profile__{r.bail_profile}__wire", material_class_id=("metal.steel_bare" if r.material_style in {"fire_red_enamel", "utility_blue_enamel", "forest_green_enamel", "galvanized_zinc", "weathered_red"} else "metal.blackened_gunmetal"),
    )
    bail.inertial = Inertial.from_geometry(
        Cylinder(
            radius=r.bail_wire_radius_m,
            length=2.0 * r.pivot_radius_m,
        ),
        mass=0.10,
    )

    provider = AxisInterface(
        name="bucket_body.bail_pivot_axis",
        point=(0.0, 0.0, r.pivot_z_m),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=r.pin_radius_m + RUN_CLEARANCE,
    )
    consumer = AxisInterface(
        name="swing_bail.pivot_axis",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=r.pin_radius_m,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    joint_name = "bucket_to_swing_bail"
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=body,
        child=bail,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=4.0,
            velocity=2.5,
            lower=math.radians(-100.0),
            upper=math.radians(100.0),
        ),
        motion_properties=MotionProperties(damping=0.08, friction=0.025),
    )
    register_interface_mate(model, joint_name, mate)
    return bail


def slot_choices_for_config(
    config: Config | ResolvedConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("body_profile", r.body_profile),
        ("rim_profile", r.rim_profile),
        ("bail_profile", r.bail_profile),
        ("ear_style", r.ear_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def build_bucket1(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "urban_environment_bucket1",
            "body_profile": r.body_profile,
            "rim_profile": r.rim_profile,
            "bail_profile": r.bail_profile,
            "ear_style": r.ear_style,
            "material_style": r.material_style,
            "excluded_structures": (
                "wall_bracket",
                "cradle_ring",
                "support_frame",
                "hook_mount",
                "body_hoops",
                "lid",
                "side_grips",
            ),
        },
    )
    mats = {
        key: model.material(f"bucket1_{r.material_style}_{key}", rgba=rgba)
        for key, rgba in PALETTES[r.material_style].items()
    }
    body = model.part(
        "bucket_body",
        meta={
            "role": "bucket_body",
            "candidate": r.body_profile,
            "open_top": True,
            "thin_sheet": True,
        },
    )
    _emit_body(body, r, mats)
    _emit_pivot_ears(body, r, mats)
    body.inertial = Inertial.from_geometry(
        Cylinder(radius=r.mouth_radius_m, length=r.body_height_m),
        mass=1.15,
        origin=Origin(xyz=(0.0, 0.0, 0.52 * r.body_height_m)),
    )
    _emit_swing_bail(model, body, r, mats)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_bucket1(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_bucket1(config_from_seed(seed), assets=assets)


def run_bucket1_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("bucket_body")
    bail = object_model.get_part("swing_bail")
    joint = object_model.get_articulation("bucket_to_swing_bail")
    body_visuals = {visual.name for visual in body.visuals}
    bail_visuals = {visual.name for visual in bail.visuals}
    all_entity_names = {
        *(part.name for part in object_model.parts),
        *(visual.name for part in object_model.parts for visual in part.visuals),
    }

    # Category anchors declared in TemplateDesign.
    shell_name = f"body_profile__{r.body_profile}__hollow_shell"
    ctx.check(
        "bucket is an open hollow revolved shell",
        shell_name in body_visuals
        and bool(body.meta.get("open_top"))
        and bool(body.meta.get("thin_sheet"))
        and r.wall_m < 0.025 * r.mouth_radius_m,
        details=f"shell={shell_name!r} visuals={sorted(body_visuals)} wall={r.wall_m:.5f}",
    )
    ctx.check(
        "selected rim profile finishes the open mouth",
        sum(name.startswith(f"rim_profile__{r.rim_profile}__") for name in body_visuals)
        == (2 if r.rim_profile == "double_bead" else 1)
        and r.rim_tube_m >= 0.004
        and r.mouth_radius_m > 20.0 * r.wall_m,
        details=f"rim={r.rim_profile} visuals={sorted(body_visuals)}",
    )
    expected_ear_tokens = (
        ("strap",)
        if r.ear_style == "riveted_strap"
        else ("neck", "disc")
    )
    ctx.check(
        "selected paired ear style supports the bail pivot",
        all(
            any(
                name.startswith(f"ear_style__{r.ear_style}__{token}_{side}")
                for name in body_visuals
            )
            for token in expected_ear_tokens
            for side in ("positive", "negative")
        )
        and all(
            f"ear_style__{r.ear_style}__pivot_pin_{side}" in body_visuals
            and f"ear_style__{r.ear_style}__rivet_head_{side}" in body_visuals
            for side in ("positive", "negative")
        )
        and r.pivot_radius_m > r.mouth_radius_m + r.rim_tube_m
        and 0.0 < r.body_height_m - r.pivot_z_m < 0.025,
        details=(
            f"ear={r.ear_style} mouth={r.mouth_radius_m:.4f} rim_tube={r.rim_tube_m:.4f} "
            f"pivot_r={r.pivot_radius_m:.4f} pivot_z={r.pivot_z_m:.4f}"
        ),
    )
    ctx.check(
        "selected bail profile changes the carry silhouette",
        {
            f"bail_profile__{r.bail_profile}__wire",
            f"bail_profile__{r.bail_profile}__eye_positive",
            f"bail_profile__{r.bail_profile}__eye_negative",
        }.issubset(bail_visuals)
        and bail.meta.get("candidate") == r.bail_profile,
        details=f"bail={r.bail_profile} visuals={sorted(bail_visuals)}",
    )
    limits = joint.motion_limits
    ctx.check(
        "swing bail pivots on the opposed ear diameter",
        joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(joint.axis) == (0.0, 1.0, 0.0)
        and abs(joint.origin.xyz[0]) < 1e-9
        and abs(joint.origin.xyz[1]) < 1e-9
        and abs(joint.origin.xyz[2] - r.pivot_z_m) < 1e-8
        and limits is not None
        and limits.lower < -1.5
        and limits.upper > 1.5
        and bail.meta.get("role") == "swing_bail",
        details=f"axis={tuple(joint.axis)} origin={joint.origin.xyz} limits={limits}",
    )
    forbidden = ("bracket", "cradle", "rack", "support_frame", "hook_mount", "body_hoop")
    ctx.check(
        "no external rack or cradle structure is emitted",
        not any(token in name for name in all_entity_names for token in forbidden),
        details=f"entities={sorted(all_entity_names)}",
    )

    body_aabb = ctx.part_world_aabb(body)
    if not r.is_pointed:
        ctx.check(
            "standing profile has a real floor or standing pad",
            body_aabb is not None
            # The 64-facet rounded shell can extend about 2.3 mm below its
            # authored z=0 pad at the widest/shallowest ellipse.  Three
            # millimetres is still well inside the real 5.4 mm floor thickness.
            and abs(body_aabb[0][2]) < 0.003
            and r.base_radius_m >= 0.10 * r.mouth_radius_m
            and r.floor_m >= 0.003,
            details=f"aabb={body_aabb} base_r={r.base_radius_m:.4f} floor={r.floor_m:.4f}",
        )
    else:
        ctx.check(
            "pointed profile closes at its apex without a support frame",
            body_aabb is not None
            and abs(body_aabb[0][2]) < 0.002
            and r.point_radius_m <= 0.06 * r.mouth_radius_m
            and not any("support" in name or "cradle" in name for name in all_entity_names),
            details=f"aabb={body_aabb} tip_r={r.point_radius_m:.5f}",
        )

    # The eye bores remain coaxial on both ends and the entire elliptical arch
    # stays outside the active mouth radius at the two side poses.
    eye_gap = (r.eye_major_radius_m - r.bail_wire_radius_m) - r.pin_radius_m
    ctx.check(
        "bail eyes retain a sub-millimetre running fit on both pivot pins",
        0.0 < eye_gap <= 0.001,
        details=f"eye_gap={eye_gap:.6f}",
    )
    rest_aabb = ctx.part_world_aabb(bail)
    with ctx.pose({joint: math.radians(90.0)}):
        side_aabb = ctx.part_world_aabb(bail)
    ctx.check(
        "bail arch swings from overhead to the bucket side",
        rest_aabb is not None
        and side_aabb is not None
        and rest_aabb[1][2] > side_aabb[1][2] + 0.35 * r.mouth_radius_m
        and side_aabb[1][0] > r.mouth_radius_m + r.rim_tube_m,
        details=f"upright={rest_aabb} side={side_aabb}",
    )
    ctx.check(
        "surface style emits no separate texture geometry",
        not any(name.startswith("surface_finish_mark_") for name in all_entity_names),
        details=f"style={r.material_style}",
    )
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    ctx.check_mesh_assets_ready()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=20)
    ctx.fail_if_isolated_parts()
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "tall_narrow_tapered_pail",
        {
            "body_profile": "tapered_pail",
            "rim_profile": "double_bead",
            "bail_profile": "shouldered_arch",
            "ear_style": "riveted_strap",
            "mouth_radius_m": 0.105,
            "body_height_m": 0.420,
            "taper_ratio": 0.58,
            "bail_rise_ratio": 1.55,
            "bail_wire_radius_m": 0.0042,
        },
        reason="Tallest narrow standing shell with double mouth beads, angular bail and heaviest wire.",
    ),
    corner_case(
        "wide_shallow_rounded_bowl",
        {
            "body_profile": "rounded_bowl",
            "rim_profile": "flared_fold",
            "bail_profile": "round_arch",
            "ear_style": "round_stamped_lug",
            "mouth_radius_m": 0.180,
            "bowl_depth_ratio": 0.78,
            "standing_pad_ratio": 0.24,
            "bail_rise_ratio": 1.15,
            "bail_wire_radius_m": 0.0042,
            "material_style": "galvanized_zinc",
        },
        reason="Widest shallow bowl with flared mouth, round lugs, largest pad and minimum bail rise.",
    ),
    corner_case(
        "deep_pointed_fire_bucket",
        {
            "body_profile": "pointed_fire_bucket",
            "rim_profile": "double_bead",
            "bail_profile": "shouldered_arch",
            "ear_style": "round_stamped_lug",
            "mouth_radius_m": 0.105,
            "pointed_aspect_ratio": 2.65,
            "point_radius_ratio": 0.018,
            "bail_rise_ratio": 1.15,
            "bail_wire_radius_m": 0.0022,
            "material_style": "weathered_red",
        },
        reason="Deepest pointed profile with the reinforced mouth, angular bail and finest closed tip.",
    ),
    corner_case(
        "wide_straight_heavy_bail",
        {
            "body_profile": "straight_pail",
            "rim_profile": "flared_fold",
            "bail_profile": "shouldered_arch",
            "ear_style": "riveted_strap",
            "mouth_radius_m": 0.180,
            "body_height_m": 0.220,
            "bail_rise_ratio": 1.55,
            "bail_wire_radius_m": 0.0042,
            "material_style": "hammered_black",
        },
        reason="Widest shortest straight shell with flared mouth, angular heavy bail and dark finish.",
    ),
)


__all__ = (
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "Bucket1Config",
    "ResolvedBucket1Config",
    "build_bucket1",
    "build_seeded_bucket1",
    "config_from_seed",
    "resolve_config",
    "run_bucket1_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
