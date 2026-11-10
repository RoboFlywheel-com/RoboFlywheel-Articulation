# SPDX-License-Identifier: Apache-2.0

"""Gear assemblies — modular procedural template.

Category identity: a grounded gear bed/support carries N closely spaced gear stages,
each with a CONTINUOUS spin joint about world +Z.  Parallel stages are placed with a
small running clearance between their tooth envelopes.  Tooth counts are jointless
visual multiplicity inside each spinning stage part.

Slots (exported via ``slot_choices_for_seed``):

* ``support_bed`` — bed plate / frame style
* ``gear_stage_multiplicity`` — ``"{N}_spin_stages"`` (joint-bearing count)
* ``gear_profile`` — parallel bench shafts vs coaxial stack
* ``material_palette`` — finish theme

seed=0 anchor mirrors ``rec_gear_assemblies_0001``: open side-frame bench,
3 parallel spin stages, machined-steel palette.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/gear_assemblies.md``
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

SupportBed = Literal["open_side_frame", "channel_plate", "heavy_bench", "compact_skid"]
GearProfile = Literal["parallel_bench", "coaxial_stack"]
MaterialStyle = Literal["machined_steel", "painted_industrial", "dark_oxide", "bronze_accent"]

SUPPORT_BEDS: tuple[SupportBed, ...] = (
    "open_side_frame",
    "channel_plate",
    "heavy_bench",
    "compact_skid",
)
GEAR_PROFILES: tuple[GearProfile, ...] = ("parallel_bench", "coaxial_stack")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "machined_steel",
    "painted_industrial",
    "dark_oxide",
    "bronze_accent",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "machined_steel": {
        "bed": (0.24, 0.28, 0.32, 1.0),
        "support": (0.24, 0.28, 0.32, 1.0),
        "gear": (0.66, 0.68, 0.71, 1.0),
        "hub": (0.58, 0.60, 0.62, 1.0),
        "bearing": (0.73, 0.55, 0.24, 1.0),
        "accent": (0.68, 0.15, 0.13, 1.0),
        "dark": (0.14, 0.15, 0.17, 1.0),
    },
    "painted_industrial": {
        "bed": (0.34, 0.38, 0.42, 1.0),
        "support": (0.30, 0.34, 0.38, 1.0),
        "gear": (0.72, 0.74, 0.76, 1.0),
        "hub": (0.62, 0.64, 0.66, 1.0),
        "bearing": (0.80, 0.62, 0.22, 1.0),
        "accent": (0.92, 0.72, 0.10, 1.0),
        "dark": (0.12, 0.13, 0.14, 1.0),
    },
    "dark_oxide": {
        "bed": (0.10, 0.11, 0.12, 1.0),
        "support": (0.14, 0.15, 0.16, 1.0),
        "gear": (0.42, 0.44, 0.46, 1.0),
        "hub": (0.28, 0.30, 0.31, 1.0),
        "bearing": (0.56, 0.42, 0.18, 1.0),
        "accent": (0.78, 0.58, 0.16, 1.0),
        "dark": (0.04, 0.04, 0.05, 1.0),
    },
    "bronze_accent": {
        "bed": (0.22, 0.24, 0.26, 1.0),
        "support": (0.26, 0.28, 0.30, 1.0),
        "gear": (0.64, 0.66, 0.68, 1.0),
        "hub": (0.74, 0.56, 0.26, 1.0),
        "bearing": (0.82, 0.64, 0.28, 1.0),
        "accent": (0.86, 0.22, 0.14, 1.0),
        "dark": (0.16, 0.14, 0.12, 1.0),
    },
}

BED_THICKNESS = 0.014
PAD_HEIGHT = 0.006
SUPPORT_HEIGHT = 0.040
SUPPORT_MOUNT_Z = BED_THICKNESS + PAD_HEIGHT
PARALLEL_GEAR_CLEARANCE = 0.001
SPIN_LIMITS = MotionLimits(effort=18.0, velocity=25.0)

# rec_gear_assemblies_0001 tooth counts for the seed-0 anchor.
ANCHOR_TOOTH_COUNTS: tuple[int, ...] = (20, 32, 36)


@dataclass(frozen=True)
class GearAssembliesConfig:
    support_bed: SupportBed | None = None
    gear_profile: GearProfile | None = None
    gear_stage_count: int | None = None
    tooth_counts: tuple[int, ...] | None = None
    bed_length_scale: float = 1.0
    gear_module_scale: float = 1.0
    material_style: MaterialStyle = "machined_steel"
    name: str = "gear_assemblies"


@dataclass(frozen=True)
class StageSpec:
    index: int
    joint_origin: tuple[float, float, float]
    pitch_radius: float
    gear_height: float
    tooth_count: int
    parent_name: str
    joint_name: str


@dataclass(frozen=True)
class ResolvedGearAssembliesConfig:
    support_bed: SupportBed
    gear_profile: GearProfile
    gear_stage_count: int
    tooth_counts: tuple[int, ...]
    bed_length: float
    bed_width: float
    gear_module: float
    material_style: MaterialStyle
    palette: dict[str, tuple[float, float, float, float]]
    stages: tuple[StageSpec, ...]
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _clampi(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(value)))


def _pitch_radius(tooth_count: int, module: float) -> float:
    return max(0.012, module * tooth_count * 0.5)


def _gear_outer_radius(tooth_count: int, pitch_radius: float) -> float:
    """Radius of the circle enclosing every simplified tooth box."""
    root_r = pitch_radius * 0.86
    tip_r = pitch_radius * 1.08
    tooth_w = max(0.004, math.tau * pitch_radius / tooth_count * 0.42)
    tooth_radial = (tip_r - root_r) * 0.85 + 0.004
    mid_r = (root_r + tip_r) * 0.5
    return mid_r + math.hypot(tooth_radial * 0.5, tooth_w * 0.5)


def _parallel_stage_x_positions(
    tooth_counts: tuple[int, ...], pitch_radii: tuple[float, ...]
) -> tuple[float, ...]:
    outer_radii = tuple(
        _gear_outer_radius(tooth_count, pitch_radius)
        for tooth_count, pitch_radius in zip(tooth_counts, pitch_radii, strict=True)
    )
    positions = [0.0]
    for left_r, right_r in zip(outer_radii, outer_radii[1:]):
        positions.append(positions[-1] + left_r + right_r + PARALLEL_GEAR_CLEARANCE)

    left_edge = positions[0] - outer_radii[0]
    right_edge = positions[-1] + outer_radii[-1]
    center_offset = 0.5 * (left_edge + right_edge)
    return tuple(x - center_offset for x in positions)


def config_from_seed(seed: int) -> GearAssembliesConfig:
    if seed == 0:
        return GearAssembliesConfig(
            support_bed="open_side_frame",
            gear_profile="parallel_bench",
            gear_stage_count=3,
            tooth_counts=ANCHOR_TOOTH_COUNTS,
            bed_length_scale=1.0,
            gear_module_scale=1.0,
            material_style="machined_steel",
            name="seeded_gear_assemblies_0",
        )

    rng = random.Random(seed)
    stage_count = rng.randint(2, 4)
    tooth_pool = (12, 16, 18, 20, 24, 28, 32, 36, 40, 48)
    tooth_counts = tuple(rng.choice(tooth_pool) for _ in range(stage_count))
    return GearAssembliesConfig(
        support_bed=rng.choice(SUPPORT_BEDS),
        gear_profile=rng.choice(GEAR_PROFILES),
        gear_stage_count=stage_count,
        tooth_counts=tooth_counts,
        bed_length_scale=round(rng.uniform(0.85, 1.20), 3),
        gear_module_scale=round(rng.uniform(0.85, 1.18), 3),
        material_style=rng.choice(MATERIAL_STYLES),
        name=f"seeded_gear_assemblies_{seed}",
    )


def resolve_config(config: GearAssembliesConfig | None = None) -> ResolvedGearAssembliesConfig:
    cfg = config or GearAssembliesConfig()
    support_bed = cfg.support_bed or "open_side_frame"
    gear_profile = cfg.gear_profile or "parallel_bench"
    stage_count = _clampi(cfg.gear_stage_count or 3, 2, 4)

    if support_bed not in SUPPORT_BEDS:
        raise ValueError(f"Unsupported support_bed: {support_bed}")
    if gear_profile not in GEAR_PROFILES:
        raise ValueError(f"Unsupported gear_profile: {gear_profile}")
    if cfg.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {cfg.material_style}")

    tooth_counts = cfg.tooth_counts
    if tooth_counts is None or len(tooth_counts) != stage_count:
        if stage_count == 3:
            tooth_counts = ANCHOR_TOOTH_COUNTS
        else:
            tooth_counts = tuple(16 + 8 * i for i in range(stage_count))
    tooth_counts = tuple(_clampi(t, 8, 64) for t in tooth_counts)

    module = 0.0027 * _clamp(cfg.gear_module_scale, 0.75, 1.35)
    pitch_radii = tuple(_pitch_radius(t, module) for t in tooth_counts)

    stages: list[StageSpec] = []
    spin_z = SUPPORT_MOUNT_Z + SUPPORT_HEIGHT

    if gear_profile == "parallel_bench":
        xs = _parallel_stage_x_positions(tooth_counts, pitch_radii)
        for i in range(stage_count):
            radius = pitch_radii[i]
            stages.append(
                StageSpec(
                    index=i,
                    joint_origin=(xs[i], 0.0, spin_z),
                    pitch_radius=radius,
                    gear_height=0.010 + 0.002 * (stage_count - i),
                    tooth_count=tooth_counts[i],
                    parent_name="gear_bed",
                    joint_name=f"bed_to_stage_{i}",
                )
            )
    else:
        world_z = spin_z
        prev_world_z = 0.0
        for i in range(stage_count):
            radius = _pitch_radius(tooth_counts[i], module) * (1.0 - 0.08 * i)
            height = 0.012 + 0.004 * (stage_count - i)
            parent = "gear_bed" if i == 0 else f"gear_stage_{i - 1}"
            joint = "bed_to_stage_0" if i == 0 else f"stage_{i - 1}_to_stage_{i}"
            if i == 0:
                joint_origin = (0.0, 0.0, world_z)
            else:
                joint_origin = (0.0, 0.0, world_z - prev_world_z)
            stages.append(
                StageSpec(
                    index=i,
                    joint_origin=joint_origin,
                    pitch_radius=radius,
                    gear_height=height,
                    tooth_count=tooth_counts[i],
                    parent_name=parent,
                    joint_name=joint,
                )
            )
            prev_world_z = world_z
            world_z += max(0.004, height * 0.42)

    stage_outer_radii = tuple(
        _gear_outer_radius(spec.tooth_count, spec.pitch_radius) for spec in stages
    )
    bed_margin = 0.05 * _clamp(cfg.bed_length_scale, 0.75, 1.35)
    if gear_profile == "parallel_bench":
        row_width = (
            stages[-1].joint_origin[0]
            - stages[0].joint_origin[0]
            + stage_outer_radii[0]
            + stage_outer_radii[-1]
        )
    else:
        row_width = 2.0 * max(stage_outer_radii)
    bed_length = max(0.22, row_width + 2.0 * bed_margin)
    bed_width = max(0.12, 2.0 * max(stage_outer_radii) + 0.04)

    return ResolvedGearAssembliesConfig(
        support_bed=support_bed,
        gear_profile=gear_profile,
        gear_stage_count=stage_count,
        tooth_counts=tooth_counts,
        bed_length=bed_length,
        bed_width=bed_width,
        gear_module=module,
        material_style=cfg.material_style,
        palette=dict(PALETTES[cfg.material_style]),
        stages=tuple(stages),
        name=cfg.name,
    )


def _mat(model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]], key: str):
    return model.material(key, rgba=palette[key])


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.steel_bare")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


def _build_support_pedestal(
    bed,
    *,
    x_pos: float,
    width: float,
    depth: float,
    mats: dict[str, object],
) -> None:
    _box(
        bed,
        (width, depth, PAD_HEIGHT),
        (x_pos, 0.0, BED_THICKNESS + PAD_HEIGHT * 0.5),
        mats["support"],
        f"support_pad_{x_pos:.3f}",
    )
    pillar_h = SUPPORT_HEIGHT - 0.006
    _box(
        bed,
        (width * 0.36, depth * 0.46, pillar_h),
        (x_pos, 0.0, BED_THICKNESS + PAD_HEIGHT + pillar_h * 0.5),
        mats["dark"],
        f"support_pillar_{x_pos:.3f}",
    )
    _box(
        bed,
        (width * 0.44, depth * 0.52, 0.006),
        (x_pos, 0.0, BED_THICKNESS + PAD_HEIGHT + SUPPORT_HEIGHT - 0.003),
        mats["support"],
        f"support_cap_{x_pos:.3f}",
    )
    _cyl(
        bed,
        min(width, depth) * 0.16,
        0.004,
        (x_pos, 0.0, BED_THICKNESS + PAD_HEIGHT + SUPPORT_HEIGHT + 0.001),
        mats["bearing"],
        f"bearing_collar_{x_pos:.3f}",
    )


def _build_gear_bed(
    model: ArticulatedObject, r: ResolvedGearAssembliesConfig, mats: dict[str, object]
):
    bed = model.part("gear_bed")
    L, W = r.bed_length, r.bed_width

    _box(bed, (L, W, BED_THICKNESS), (0.0, 0.0, BED_THICKNESS * 0.5), mats["bed"], "bed_plate")
    _box(
        bed,
        (L * 0.72, W * 0.20, PAD_HEIGHT),
        (0.0, 0.0, BED_THICKNESS + PAD_HEIGHT * 0.5),
        mats["support"],
        "center_pad",
    )

    if r.support_bed == "open_side_frame":
        for y_sign, suffix in ((-1.0, "neg"), (1.0, "pos")):
            _box(
                bed,
                (L * 0.78, 0.012, SUPPORT_HEIGHT + PAD_HEIGHT),
                (
                    0.0,
                    y_sign * (W * 0.46),
                    SUPPORT_MOUNT_Z + SUPPORT_HEIGHT * 0.5 - PAD_HEIGHT * 0.5,
                ),
                mats["support"],
                f"side_rail_{suffix}",
            )
    elif r.support_bed == "channel_plate":
        _box(
            bed,
            (L * 0.86, W * 0.86, 0.008),
            (0.0, 0.0, BED_THICKNESS + 0.004),
            mats["dark"],
            "channel_lip",
        )
    elif r.support_bed == "heavy_bench":
        for x_off, suffix in ((-L * 0.34, "left"), (L * 0.34, "right")):
            _box(
                bed,
                (L * 0.12, W * 0.72, 0.028),
                (x_off, 0.0, BED_THICKNESS + 0.014),
                mats["dark"],
                f"bench_mass_{suffix}",
            )
    else:
        for x_off, suffix in ((-L * 0.38, "left"), (L * 0.38, "right")):
            _cyl(
                bed,
                0.012,
                0.006,
                (x_off, W * 0.38, BED_THICKNESS + 0.003),
                mats["dark"],
                f"skid_foot_{suffix}",
            )

    if r.gear_profile == "parallel_bench":
        for spec in r.stages:
            width = max(0.040, spec.pitch_radius * 1.15)
            depth = max(0.040, spec.pitch_radius * 1.05)
            _build_support_pedestal(
                bed,
                x_pos=spec.joint_origin[0],
                width=width,
                depth=depth,
                mats=mats,
            )
    else:
        spin_z = r.stages[0].joint_origin[2]
        top_z = spin_z + r.stages[0].gear_height
        for spec in r.stages[1:]:
            top_z += spec.joint_origin[2] + spec.gear_height
        shaft_h = max(0.050, top_z - spin_z + 0.006)
        shaft_r = max(0.012, r.stages[0].pitch_radius * 0.18)
        pedestal_h = max(0.020, spin_z - BED_THICKNESS)
        _box(
            bed,
            (shaft_r * 2.8, shaft_r * 2.8, pedestal_h),
            (0.0, 0.0, BED_THICKNESS + pedestal_h * 0.5),
            mats["support"],
            "coaxial_pedestal",
        )
        _cyl(
            bed,
            shaft_r,
            shaft_h,
            (0.0, 0.0, spin_z + shaft_h * 0.5),
            mats["hub"],
            "coaxial_spindle",
        )
        _cyl(
            bed,
            r.stages[0].pitch_radius * 0.34,
            0.006,
            (0.0, 0.0, spin_z - 0.002),
            mats["bearing"],
            "coaxial_bearing",
        )

    bed.inertial = Inertial.from_geometry(
        Box((L, W, BED_THICKNESS + PAD_HEIGHT)),
        mass=6.0 + 0.8 * r.gear_stage_count,
        origin=Origin(xyz=(0.0, 0.0, (BED_THICKNESS + PAD_HEIGHT) * 0.5)),
    )
    return bed


def _add_spur_gear_visuals(
    stage,
    *,
    tooth_count: int,
    pitch_radius: float,
    gear_height: float,
    mats: dict[str, object],
    index: int,
) -> None:
    hub_r = max(0.008, pitch_radius * 0.28)
    bore_r = hub_r * 0.42
    root_r = pitch_radius * 0.86
    tip_r = pitch_radius * 1.08

    _cyl(
        stage,
        hub_r,
        gear_height + 0.006,
        (0.0, 0.0, gear_height * 0.5),
        mats["hub"],
        "gear_hub",
    )
    _cyl(
        stage,
        root_r,
        gear_height * 0.72,
        (0.0, 0.0, gear_height * 0.36),
        mats["gear"],
        "gear_web",
    )
    _cyl(
        stage,
        root_r * 0.55,
        gear_height * 0.55,
        (0.0, 0.0, gear_height * 0.50),
        mats["dark"],
        "lightening_ring",
    )

    tooth_w = max(0.004, math.tau * pitch_radius / tooth_count * 0.42)
    tooth_h = max(0.003, gear_height * 0.62)
    tooth_radial = (tip_r - root_r) * 0.85 + 0.004
    mid_r = (root_r + tip_r) * 0.5
    for k in range(tooth_count):
        ang = math.tau * k / tooth_count
        cx = mid_r * math.cos(ang)
        cy = mid_r * math.sin(ang)
        _box(
            stage,
            (tooth_radial, tooth_w, tooth_h),
            (cx, cy, gear_height * 0.50),
            mats["gear"],
            f"gear_tooth_{k}",
            rpy=(0.0, 0.0, ang),
        )

    _cyl(
        stage,
        bore_r,
        gear_height * 0.42,
        (0.0, 0.0, gear_height * 0.72),
        mats["dark"],
        "center_bore",
    )

    if index == 0:
        _box(
            stage,
            (pitch_radius * 0.30, 0.010, 0.012),
            (pitch_radius * 0.36, 0.0, gear_height * 0.52),
            mats["accent"],
            "drive_spoke",
        )
        _cyl(
            stage,
            pitch_radius * 0.16,
            0.010,
            (pitch_radius * 0.72, 0.0, gear_height * 0.52),
            mats["accent"],
            "drive_handwheel",
        )


def _build_gear_stage(
    model: ArticulatedObject,
    spec: StageSpec,
    mats: dict[str, object],
    *,
    gear_profile: GearProfile,
) -> None:
    stage = model.part(f"gear_stage_{spec.index}")
    _cyl(
        stage,
        max(0.006, spec.pitch_radius * 0.12),
        0.006,
        (0.0, 0.0, 0.005),
        mats["bearing"],
        "journal_stub",
    )
    if gear_profile == "coaxial_stack":
        clip_h = 0.030 if spec.index > 0 else 0.012
        _cyl(
            stage,
            0.011,
            clip_h,
            (0.0, 0.0, -(clip_h * 0.5) + 0.004),
            mats["hub"],
            "coaxial_clip",
        )
        _cyl(
            stage,
            max(0.008, spec.pitch_radius * 0.16),
            spec.gear_height * 0.62,
            (0.0, 0.0, spec.gear_height * 0.22),
            mats["hub"],
            "coaxial_sleeve",
        )
    _add_spur_gear_visuals(
        stage,
        tooth_count=spec.tooth_count,
        pitch_radius=spec.pitch_radius,
        gear_height=spec.gear_height,
        mats=mats,
        index=spec.index,
    )
    stage.inertial = Inertial.from_geometry(
        Cylinder(radius=spec.pitch_radius, length=spec.gear_height + 0.010),
        mass=max(0.35, spec.pitch_radius * spec.pitch_radius * spec.gear_height * 2200.0),
        origin=Origin(xyz=(0.0, 0.0, spec.gear_height * 0.5)),
    )


def build_gear_assemblies(
    config: GearAssembliesConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {key: _mat(model, r.palette, key) for key in r.palette}
    _build_gear_bed(model, r, mats)

    for spec in r.stages:
        _build_gear_stage(model, spec, mats, gear_profile=r.gear_profile)
        model.articulation(
            spec.joint_name,
            ArticulationType.CONTINUOUS,
            parent=spec.parent_name,
            child=f"gear_stage_{spec.index}",
            origin=Origin(xyz=spec.joint_origin),
            axis=(0.0, 0.0, 1.0),
            motion_limits=SPIN_LIMITS,
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["tooth_multiplicity"] = "_".join(str(t) for t in r.tooth_counts)
    return model


def build_seeded_gear_assemblies(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_gear_assemblies(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedGearAssembliesConfig) -> list[tuple[str, str]]:
    return [
        ("support_bed", r.support_bed),
        ("gear_stage_multiplicity", f"{r.gear_stage_count}_spin_stages"),
        ("gear_profile", r.gear_profile),
        ("material_palette", r.material_style),
        ("tooth_multiplicity", "_".join(str(t) for t in r.tooth_counts)),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def run_gear_assemblies_tests(
    object_model: ArticulatedObject,
    config: GearAssembliesConfig | None = None,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_map = {j.name: j for j in object_model.articulations}

    ctx.check("gear_bed_present", "gear_bed" in part_names)
    stage_parts = sorted(n for n in part_names if n.startswith("gear_stage_"))
    ctx.check(
        "gear_stage_count",
        len(stage_parts) == r.gear_stage_count,
        details=f"expected {r.gear_stage_count}, got {len(stage_parts)}",
    )

    for spec in r.stages:
        part_name = f"gear_stage_{spec.index}"
        ctx.check(f"{part_name}_present", part_name in part_names)
        ctx.check(f"{spec.joint_name}_present", spec.joint_name in joint_map)
        joint = joint_map.get(spec.joint_name)
        if joint is not None:
            ctx.check(
                f"{spec.joint_name}_continuous",
                joint.articulation_type == ArticulationType.CONTINUOUS,
                details=str(joint.articulation_type),
            )
            ctx.check(
                f"{spec.joint_name}_axis_z",
                tuple(joint.axis) == (0.0, 0.0, 1.0),
                details=str(joint.axis),
            )
            ctx.check(
                f"{spec.joint_name}_parent",
                joint.parent == spec.parent_name,
                details=f"{joint.parent} != {spec.parent_name}",
            )
            ctx.check(
                f"{spec.joint_name}_child",
                joint.child == part_name,
                details=f"{joint.child} != {part_name}",
            )

    tooth_visuals = sum(
        1
        for p in object_model.parts
        if p.name.startswith("gear_stage_")
        for v in p.visuals
        if v.name.startswith("gear_tooth_")
    )
    expected_teeth = sum(r.tooth_counts)
    ctx.check(
        "tooth_multiplicity_visuals",
        tooth_visuals == expected_teeth,
        details=f"visual teeth={tooth_visuals} expected={expected_teeth}",
    )

    if r.gear_profile == "parallel_bench":
        for spec in r.stages:
            ctx.check(
                f"bed_to_stage_{spec.index}_naming",
                spec.joint_name == f"bed_to_stage_{spec.index}",
            )
        for left, right in zip(r.stages, r.stages[1:]):
            center_distance = right.joint_origin[0] - left.joint_origin[0]
            outer_gap = center_distance - (
                _gear_outer_radius(left.tooth_count, left.pitch_radius)
                + _gear_outer_radius(right.tooth_count, right.pitch_radius)
            )
            ctx.check(
                f"parallel_adjacent_gear_{left.index}_{right.index}_clearance",
                abs(outer_gap - PARALLEL_GEAR_CLEARANCE) <= 1e-9,
                details=(
                    f"outer_gap={outer_gap:.6f} m; "
                    f"expected={PARALLEL_GEAR_CLEARANCE:.6f} m"
                ),
            )
    else:
        ctx.check("coaxial_first_joint", r.stages[0].joint_name == "bed_to_stage_0")
        for i in range(1, r.gear_stage_count):
            ctx.check(
                f"coaxial_chain_joint_{i}",
                r.stages[i].joint_name == f"stage_{i - 1}_to_stage_{i}",
            )
        bed = object_model.get_part("gear_bed")
        for spec in r.stages:
            stage = object_model.get_part(f"gear_stage_{spec.index}")
            ctx.allow_overlap(
                bed,
                stage,
                reason="coaxial spindle and clips engage stacked gear hubs on the bed shaft",
            )
        for i in range(r.gear_stage_count):
            for j in range(i + 1, r.gear_stage_count):
                ctx.allow_overlap(
                    object_model.get_part(f"gear_stage_{i}"),
                    object_model.get_part(f"gear_stage_{j}"),
                    reason="coaxial stack stages share the same shaft axis at rest",
                )

    return ctx.report()


__all__ = [
    "GearAssembliesConfig",
    "ResolvedGearAssembliesConfig",
    "config_from_seed",
    "resolve_config",
    "build_gear_assemblies",
    "build_seeded_gear_assemblies",
    "slot_choices_for_seed",
    "slot_choices_for_config",
    "run_gear_assemblies_tests",
]
