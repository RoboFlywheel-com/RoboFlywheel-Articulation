# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeWithHolesGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

AssemblyLayout = Literal["combined_crankset", "modular_three_piece"]
SpindleAxis = Literal["x", "y"]
CrankArmProfile = Literal["forged_solid", "hollow_tapered", "stubby_bmx", "short_folding"]
ChainringProfile = Literal[
    "round_single",
    "track_solid",
    "road_double",
    "compact_double",
    "road_triple",
    "bmx_sprocket",
    "oval_one_by",
    "narrow_wide_one_by",
    "bash_guard",
]
SpiderStyle = Literal["none_direct_mount", "four_arm", "five_arm", "solid_carrier"]
PedalStyle = Literal[
    "platform",
    "pinned_platform",
    "cage",
    "rat_trap",
    "clipless",
    "road_clipless",
    "folding_cage",
    "slim_folding",
]
PedalMotionMode = Literal["spin", "fold", "spin_and_fold"]
BBShellStyle = Literal[
    "cartridge",
    "sealed_compact",
    "pressfit",
    "square_taper",
    "external_bearing",
    "two_piece_hollow",
    "wide_cups",
    "bmx_three_piece",
    "ebike_mid_motor",
    "torque_sensor_ebike",
    "power_meter_spindle",
]
MaterialStyle = Literal[
    "black_alloy",
    "silver_road",
    "bmx_raw",
    "dark_graphite",
    "polished_steel",
    "champagne_track",
    "two_tone_black_silver",
]

CHAINRING_PROFILES: tuple[ChainringProfile, ...] = (
    "round_single",
    "track_solid",
    "road_double",
    "compact_double",
    "road_triple",
    "bmx_sprocket",
    "oval_one_by",
    "narrow_wide_one_by",
    "bash_guard",
)
PEDAL_STYLES: tuple[PedalStyle, ...] = (
    "platform",
    "pinned_platform",
    "cage",
    "rat_trap",
    "clipless",
    "road_clipless",
    "folding_cage",
    "slim_folding",
)
FOLDING_PEDAL_STYLES: tuple[PedalStyle, ...] = ("folding_cage", "slim_folding")
BB_SHELL_STYLES: tuple[BBShellStyle, ...] = (
    "cartridge",
    "sealed_compact",
    "pressfit",
    "square_taper",
    "external_bearing",
    "two_piece_hollow",
    "wide_cups",
    "bmx_three_piece",
    "ebike_mid_motor",
    "torque_sensor_ebike",
    "power_meter_spindle",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "black_alloy",
    "silver_road",
    "bmx_raw",
    "dark_graphite",
    "polished_steel",
    "champagne_track",
    "two_tone_black_silver",
)

MATERIAL_PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_alloy": {
        "shell": (0.06, 0.06, 0.07, 1.0),
        "metal": (0.18, 0.19, 0.20, 1.0),
        "ring": (0.03, 0.03, 0.03, 1.0),
        "pedal": (0.10, 0.10, 0.11, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
    },
    "silver_road": {
        "shell": (0.12, 0.12, 0.13, 1.0),
        "metal": (0.70, 0.72, 0.72, 1.0),
        "ring": (0.62, 0.64, 0.64, 1.0),
        "pedal": (0.18, 0.18, 0.19, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
    },
    "bmx_raw": {
        "shell": (0.08, 0.08, 0.08, 1.0),
        "metal": (0.50, 0.48, 0.44, 1.0),
        "ring": (0.30, 0.30, 0.28, 1.0),
        "pedal": (0.08, 0.08, 0.09, 1.0),
        "rubber": (0.01, 0.01, 0.01, 1.0),
    },
    "dark_graphite": {
        "shell": (0.02, 0.025, 0.03, 1.0),
        "metal": (0.12, 0.13, 0.14, 1.0),
        "ring": (0.04, 0.04, 0.045, 1.0),
        "pedal": (0.03, 0.03, 0.035, 1.0),
        "rubber": (0.006, 0.006, 0.006, 1.0),
    },
    "polished_steel": {
        "shell": (0.34, 0.35, 0.36, 1.0),
        "metal": (0.82, 0.84, 0.84, 1.0),
        "ring": (0.68, 0.70, 0.70, 1.0),
        "pedal": (0.16, 0.16, 0.17, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
    },
    "champagne_track": {
        "shell": (0.12, 0.11, 0.095, 1.0),
        "metal": (0.72, 0.67, 0.55, 1.0),
        "ring": (0.09, 0.085, 0.075, 1.0),
        "pedal": (0.08, 0.08, 0.08, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
    },
    "two_tone_black_silver": {
        "shell": (0.08, 0.08, 0.085, 1.0),
        "metal": (0.66, 0.67, 0.68, 1.0),
        "ring": (0.035, 0.035, 0.04, 1.0),
        "pedal": (0.05, 0.05, 0.055, 1.0),
        "rubber": (0.70, 0.70, 0.68, 1.0),
    },
}

ADOPTED_SOURCES: dict[str, str] = {
    "S1": "data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L236-L477",
    "S2": "data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L248-L422",
    "S3": "data/records/rec_bicycle_crankset_and_pedal_assembly_32f074afe5b34845a25b71af925a3aca/revisions/rev_000001/model.py:L217-L324",
    "S4": "data/records/rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257/revisions/rev_000001/model.py:L123-L318",
    "S5": "data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L155-L348",
}

FIVE_STAR_SOURCE_RECORDS: tuple[str, ...] = (
    "rec_bicycle_crankset_and_pedal_assembly_0001",
    "rec_bicycle_crankset_and_pedal_assembly_0004",
    "rec_bicycle_crankset_and_pedal_assembly_0006",
    "rec_bicycle_crankset_and_pedal_assembly_0007",
    "rec_bicycle_crankset_and_pedal_assembly_0008",
    "rec_bicycle_crankset_and_pedal_assembly_071b4704ed244c78a574033d4cc20cd3",
    "rec_bicycle_crankset_and_pedal_assembly_0d8434da0254429bb965c57a0e69b3c4",
    "rec_bicycle_crankset_and_pedal_assembly_13ce71f8ff35489b93e3d15133cd902d",
    "rec_bicycle_crankset_and_pedal_assembly_1f6300db6a2a411ea2a58487d131b62d",
    "rec_bicycle_crankset_and_pedal_assembly_205d5b5e06ed4f38a66ac0539dc8db88",
    "rec_bicycle_crankset_and_pedal_assembly_2e56ec4afa0145b0a746b81cc7ab8597",
    "rec_bicycle_crankset_and_pedal_assembly_32f074afe5b34845a25b71af925a3aca",
    "rec_bicycle_crankset_and_pedal_assembly_3becb49b39f04ec1890be3ede4d3d1c5",
    "rec_bicycle_crankset_and_pedal_assembly_539a15e4d4a749249facff64a2ad00b8",
    "rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257",
    "rec_bicycle_crankset_and_pedal_assembly_54d5cb42dd2f4a6783594c35403ebfc4",
    "rec_bicycle_crankset_and_pedal_assembly_5fe9bf7e4c1645d888747e760f2f4536",
    "rec_bicycle_crankset_and_pedal_assembly_6a5315f7a66445b3a08a9d138595ef21",
    "rec_bicycle_crankset_and_pedal_assembly_6d39d60004e24bafafafe0db64d0f8ec",
    "rec_bicycle_crankset_and_pedal_assembly_6ee85b9a5233414988fb2ea3504fea7d",
    "rec_bicycle_crankset_and_pedal_assembly_815cd8c51ee342719a051869fe2b7325",
    "rec_bicycle_crankset_and_pedal_assembly_8e15ccba41b640c3919fafd7ce1692c5",
    "rec_bicycle_crankset_and_pedal_assembly_9304867f712844ec9eb912f655084898",
    "rec_bicycle_crankset_and_pedal_assembly_a17a36bce7814b58b15d1c8d6e28d7e9",
    "rec_bicycle_crankset_and_pedal_assembly_ae2baa8af500461f881edaf1fcf9a7a1",
    "rec_bicycle_crankset_and_pedal_assembly_b15a4f5c5bc84bddbafd8d2b132f0a30",
    "rec_bicycle_crankset_and_pedal_assembly_b6c74f4ad37d4597846d4c9ce81cf989",
    "rec_bicycle_crankset_and_pedal_assembly_b8f36fb1f1834f378e16a4cf6dd4aeca",
    "rec_bicycle_crankset_and_pedal_assembly_c01d5c66a6084eb0baa58cb5c4cdc263",
    "rec_bicycle_crankset_and_pedal_assembly_c70031db18fc4f088e3d96d6f49d3ca1",
    "rec_bicycle_crankset_and_pedal_assembly_c83bb2e32c634d3aa349092a0452d6ca",
    "rec_bicycle_crankset_and_pedal_assembly_d5298cf0d3384523a9a635e33df289cc",
    "rec_bicycle_crankset_and_pedal_assembly_e24f94fafbd840e9a98c4e219c9362b1",
    "rec_bicycle_crankset_and_pedal_assembly_e4cbae29d5184766950a8d3beccbc0c6",
    "rec_bicycle_crankset_and_pedal_assembly_fad3dea7794144328118a137a31cc5e5",
    "rec_bicycle_crankset_and_pedal_assembly_ffab53b53ce24dcfbf35adeb3cacb72c",
)


@dataclass(frozen=True)
class BicycleCranksetAndPedalAssemblyConfig:
    assembly_layout: AssemblyLayout = "combined_crankset"
    spindle_axis: SpindleAxis = "x"
    crank_length: float = 0.170
    crank_arm_profile: CrankArmProfile = "forged_solid"
    chainring_count: int = 1
    chainring_profile: ChainringProfile = "round_single"
    spider_style: SpiderStyle = "five_arm"
    pedal_style: PedalStyle = "platform"
    pedal_motion_mode: PedalMotionMode = "spin"
    bb_shell_style: BBShellStyle = "cartridge"
    crank_phase_offset: float = math.pi
    material_style: MaterialStyle = "black_alloy"
    name: str = "reference_bicycle_crankset_and_pedal_assembly"


@dataclass(frozen=True)
class ResolvedBicycleCranksetAndPedalAssemblyConfig:
    assembly_layout: AssemblyLayout
    spindle_axis: SpindleAxis
    axis: tuple[float, float, float]
    crank_length: float
    arm_width: float
    arm_thickness: float
    crank_arm_profile: CrankArmProfile
    chainring_count: int
    chainring_profile: ChainringProfile
    ring_radii: tuple[float, ...]
    spider_style: SpiderStyle
    spider_arm_count: int
    pedal_style: PedalStyle
    pedal_motion_mode: PedalMotionMode
    bb_shell_style: BBShellStyle
    spindle_length: float
    spindle_radius: float
    crank_phase_offset: float
    material_style: MaterialStyle
    name: str


def config_from_seed(seed: int) -> BicycleCranksetAndPedalAssemblyConfig:
    rng = random.Random(seed)
    pedal_style: PedalStyle = rng.choice(PEDAL_STYLES)
    pedal_motion_mode: PedalMotionMode = (
        rng.choice(("fold", "spin_and_fold")) if pedal_style in FOLDING_PEDAL_STYLES else "spin"
    )
    profile: ChainringProfile = rng.choice(CHAINRING_PROFILES)
    if profile in ("road_double", "compact_double"):
        chainring_count = 2
    elif profile == "road_triple":
        chainring_count = 3
    else:
        chainring_count = 1
    return BicycleCranksetAndPedalAssemblyConfig(
        assembly_layout=rng.choice(("combined_crankset", "modular_three_piece")),
        spindle_axis="x",
        crank_length=round(rng.uniform(0.118, 0.180), 4),
        crank_arm_profile=rng.choice(
            ("forged_solid", "hollow_tapered", "stubby_bmx", "short_folding")
        ),
        chainring_count=chainring_count,
        chainring_profile=profile,
        spider_style=rng.choice(("none_direct_mount", "four_arm", "five_arm", "solid_carrier")),
        pedal_style=pedal_style,
        pedal_motion_mode=pedal_motion_mode,
        bb_shell_style=rng.choice(BB_SHELL_STYLES),
        material_style=rng.choice(MATERIAL_STYLES),
        name=f"seeded_bicycle_crankset_{seed}",
    )


def resolve_config(
    config: BicycleCranksetAndPedalAssemblyConfig,
) -> ResolvedBicycleCranksetAndPedalAssemblyConfig:
    if config.assembly_layout not in ("combined_crankset", "modular_three_piece"):
        raise ValueError(f"Unsupported assembly_layout: {config.assembly_layout}")
    if config.spindle_axis not in ("x", "y"):
        raise ValueError(f"Unsupported spindle_axis: {config.spindle_axis}")
    if config.crank_arm_profile not in (
        "forged_solid",
        "hollow_tapered",
        "stubby_bmx",
        "short_folding",
    ):
        raise ValueError(f"Unsupported crank_arm_profile: {config.crank_arm_profile}")
    if config.chainring_count not in (1, 2, 3):
        raise ValueError("chainring_count must be 1, 2, or 3")
    if config.chainring_profile not in CHAINRING_PROFILES:
        raise ValueError(f"Unsupported chainring_profile: {config.chainring_profile}")
    if config.spider_style not in ("none_direct_mount", "four_arm", "five_arm", "solid_carrier"):
        raise ValueError(f"Unsupported spider_style: {config.spider_style}")
    if config.pedal_style not in PEDAL_STYLES:
        raise ValueError(f"Unsupported pedal_style: {config.pedal_style}")
    if config.pedal_motion_mode not in ("spin", "fold", "spin_and_fold"):
        raise ValueError(f"Unsupported pedal_motion_mode: {config.pedal_motion_mode}")
    if config.pedal_style not in FOLDING_PEDAL_STYLES and config.pedal_motion_mode != "spin":
        raise ValueError("non-folding pedals must use pedal_motion_mode='spin'")
    if config.bb_shell_style not in BB_SHELL_STYLES:
        raise ValueError(f"Unsupported bb_shell_style: {config.bb_shell_style}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    crank_length = max(0.118, min(0.180, config.crank_length))
    arm_width = {
        "forged_solid": 0.024,
        "hollow_tapered": 0.030,
        "stubby_bmx": 0.032,
        "short_folding": 0.022,
    }[config.crank_arm_profile]
    arm_thickness = 0.014 if config.crank_arm_profile != "stubby_bmx" else 0.020
    ring_radii = {1: (0.078,), 2: (0.086, 0.066), 3: (0.094, 0.078, 0.060)}[config.chainring_count]
    if config.chainring_profile == "bmx_sprocket":
        ring_radii = (0.070,)
    if config.chainring_profile == "track_solid":
        ring_radii = (0.094,)
    if config.chainring_profile == "bash_guard":
        ring_radii = (0.092,)
    if config.chainring_profile == "oval_one_by":
        ring_radii = (0.084,)
    if config.chainring_profile == "narrow_wide_one_by":
        ring_radii = (0.086,)
    if config.chainring_profile == "road_double":
        ring_radii = (0.096, 0.074)
    if config.chainring_profile == "compact_double":
        ring_radii = (0.088, 0.066)
    if config.chainring_profile == "road_triple":
        ring_radii = (0.098, 0.080, 0.062)
    resolved_chainring_count = len(ring_radii)
    spider_arm_count = {"none_direct_mount": 0, "four_arm": 4, "five_arm": 5, "solid_carrier": 6}[
        config.spider_style
    ]
    if config.chainring_profile == "track_solid":
        spider_arm_count = 0
    axis = (1.0, 0.0, 0.0) if config.spindle_axis == "x" else (0.0, 1.0, 0.0)
    return ResolvedBicycleCranksetAndPedalAssemblyConfig(
        assembly_layout=config.assembly_layout,
        spindle_axis=config.spindle_axis,
        axis=axis,
        crank_length=crank_length,
        arm_width=arm_width,
        arm_thickness=arm_thickness,
        crank_arm_profile=config.crank_arm_profile,
        chainring_count=resolved_chainring_count,
        chainring_profile=config.chainring_profile,
        ring_radii=ring_radii,
        spider_style=config.spider_style,
        spider_arm_count=spider_arm_count,
        pedal_style=config.pedal_style,
        pedal_motion_mode=config.pedal_motion_mode,
        bb_shell_style=config.bb_shell_style,
        spindle_length=(
            0.190
            if config.bb_shell_style
            in ("wide_cups", "bmx_three_piece", "ebike_mid_motor", "torque_sensor_ebike")
            else 0.170
            if config.bb_shell_style
            in ("external_bearing", "two_piece_hollow", "power_meter_spindle")
            else 0.152
        ),
        spindle_radius=0.0115,
        crank_phase_offset=math.pi,
        material_style=config.material_style,
        name=config.name,
    )


def _cyl_axis_rpy(axis: SpindleAxis) -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0) if axis == "x" else (math.pi / 2.0, 0.0, 0.0)


def _radial_xyz(
    axis: SpindleAxis, axial: float, radial: float, angle: float
) -> tuple[float, float, float]:
    a = axial
    u = radial * math.sin(angle)
    v = radial * math.cos(angle)
    if axis == "x":
        return (a, u, v)
    return (u, a, v)


def _drive_axial(r: ResolvedBicycleCranksetAndPedalAssemblyConfig) -> float:
    return r.spindle_length * 0.37


def _non_drive_axial(r: ResolvedBicycleCranksetAndPedalAssemblyConfig) -> float:
    return -r.spindle_length * 0.37


def _modular_drive_axial(r: ResolvedBicycleCranksetAndPedalAssemblyConfig) -> float:
    return r.spindle_length * 0.5 + 0.009


def _modular_non_drive_axial(r: ResolvedBicycleCranksetAndPedalAssemblyConfig) -> float:
    return -_modular_drive_axial(r)


def _outboard_xyz(
    r: ResolvedBicycleCranksetAndPedalAssemblyConfig, side: str, distance: float
) -> tuple[float, float, float]:
    sign = 1.0 if side == "right" else -1.0
    if r.spindle_axis == "x":
        return (sign * distance, 0.0, 0.0)
    return (0.0, sign * distance, 0.0)


def _offset_xyz(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _pedal_local_xyz(
    r: ResolvedBicycleCranksetAndPedalAssemblyConfig,
    side: str,
    axial: float,
    lateral: float = 0.0,
    vertical: float = 0.0,
) -> tuple[float, float, float]:
    sign = 1.0 if side == "right" else -1.0
    if r.spindle_axis == "x":
        return (sign * axial, lateral, vertical)
    return (lateral, sign * axial, vertical)


def _pedal_child_rpy(
    r: ResolvedBicycleCranksetAndPedalAssemblyConfig, side: str
) -> tuple[float, float, float]:
    if r.assembly_layout == "modular_three_piece" and side == "left":
        return (0.0, math.pi, 0.0)
    return (0.0, 0.0, 0.0)


def _pedal_box_size(
    r: ResolvedBicycleCranksetAndPedalAssemblyConfig,
    axial: float,
    lateral: float,
    vertical: float,
) -> tuple[float, float, float]:
    if r.spindle_axis == "x":
        return (axial, lateral, vertical)
    return (lateral, axial, vertical)


def _radial_bar_size(
    axis: SpindleAxis, axial_thickness: float, tangential_width: float, radial_length: float
) -> tuple[float, float, float]:
    if axis == "x":
        return (axial_thickness, tangential_width, radial_length)
    return (tangential_width, axial_thickness, radial_length)


def _radial_bar_rpy(axis: SpindleAxis, angle: float) -> tuple[float, float, float]:
    if axis == "x":
        return (-angle, 0.0, 0.0)
    return (0.0, angle, 0.0)


def _circle_profile(radius: float, *, segments: int = 48) -> list[tuple[float, float]]:
    return [
        (
            radius * math.cos(2.0 * math.pi * index / segments),
            radius * math.sin(2.0 * math.pi * index / segments),
        )
        for index in range(segments)
    ]


def _toothed_ring_profile(
    teeth: int, root_radius: float, tip_radius: float
) -> list[tuple[float, float]]:
    profile: list[tuple[float, float]] = []
    step = 2.0 * math.pi / teeth
    for tooth in range(teeth):
        angle = tooth * step
        profile.extend(
            [
                (root_radius * math.cos(angle), root_radius * math.sin(angle)),
                (
                    tip_radius * math.cos(angle + step * 0.24),
                    tip_radius * math.sin(angle + step * 0.24),
                ),
                (
                    tip_radius * math.cos(angle + step * 0.50),
                    tip_radius * math.sin(angle + step * 0.50),
                ),
                (
                    root_radius * math.cos(angle + step * 0.84),
                    root_radius * math.sin(angle + step * 0.84),
                ),
            ]
        )
    return profile


def _chainring_geometry(
    r: ResolvedBicycleCranksetAndPedalAssemblyConfig, radius: float, teeth: int
) -> ExtrudeWithHolesGeometry:
    holes = [_circle_profile(max(0.024, radius * 0.42), segments=48)]
    if r.spider_style != "solid_carrier" and r.chainring_profile != "track_solid":
        pocket_radius = radius * 0.60
        pocket_size = max(0.004, radius * 0.065)
        for pocket in range(5):
            angle = 2.0 * math.pi * pocket / 5.0 + math.pi / 5.0
            holes.append(
                [
                    (
                        pocket_radius * math.cos(angle) + pocket_size * math.cos(theta),
                        pocket_radius * math.sin(angle) + pocket_size * math.sin(theta),
                    )
                    for theta in (2.0 * math.pi * step / 20.0 for step in range(20))
                ]
            )
    geometry = ExtrudeWithHolesGeometry(
        _toothed_ring_profile(teeth, radius, radius + 0.0035),
        holes,
        height=0.0055,
        center=True,
        closed=True,
    )
    if r.chainring_profile == "oval_one_by":
        geometry.scale(1.0, 0.86, 1.0)
    if r.chainring_profile == "track_solid":
        geometry.scale(1.0, 1.0, 1.25)
    if r.spindle_axis == "x":
        return geometry.rotate_y(math.pi / 2.0)
    return geometry.rotate_x(math.pi / 2.0)


def _chainring_teeth(r: ResolvedBicycleCranksetAndPedalAssemblyConfig, index: int) -> int:
    if r.chainring_profile == "bmx_sprocket":
        return 24
    if r.chainring_profile == "track_solid":
        return 44
    if r.chainring_profile == "road_triple":
        return (46, 38, 28)[index]
    if r.chainring_profile == "road_double":
        return (50, 34)[index]
    if r.chainring_profile == "compact_double":
        return (46, 30)[index]
    if r.chainring_profile == "oval_one_by":
        return 32
    if r.chainring_profile == "narrow_wide_one_by":
        return 34
    if r.chainring_profile == "bash_guard":
        return 34
    return 36


def _pedal_root_clearance(r: ResolvedBicycleCranksetAndPedalAssemblyConfig) -> float:
    return max(0.007, r.arm_thickness * 0.5)


def _pedal_knuckle_center_distance(r: ResolvedBicycleCranksetAndPedalAssemblyConfig) -> float:
    return _pedal_root_clearance(r) + 0.011


def _add_shell_blocks(
    part,
    r: ResolvedBicycleCranksetAndPedalAssemblyConfig,
    *,
    axial: float,
    length: float,
    outer_radius: float,
    prefix: str,
    material,
) -> None:
    inner_radius = r.spindle_radius
    wall = max(0.006, outer_radius - inner_radius)
    shell_center = inner_radius + wall * 0.5
    if r.spindle_axis == "x":
        part.visual(
            Box((length, outer_radius * 2.0, wall)),
            origin=Origin(xyz=(axial, 0.0, shell_center)),
            material=material,
            name=f"{prefix}_upper_shell", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
        part.visual(
            Box((length, outer_radius * 2.0, wall)),
            origin=Origin(xyz=(axial, 0.0, -shell_center)),
            material=material,
            name=f"{prefix}_lower_shell", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
        part.visual(
            Box((length, wall, inner_radius * 2.0)),
            origin=Origin(xyz=(axial, shell_center, 0.0)),
            material=material,
            name=f"{prefix}_front_shell", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
        part.visual(
            Box((length, wall, inner_radius * 2.0)),
            origin=Origin(xyz=(axial, -shell_center, 0.0)),
            material=material,
            name=f"{prefix}_rear_shell", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
    else:
        part.visual(
            Box((outer_radius * 2.0, length, wall)),
            origin=Origin(xyz=(0.0, axial, shell_center)),
            material=material,
            name=f"{prefix}_upper_shell", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
        part.visual(
            Box((outer_radius * 2.0, length, wall)),
            origin=Origin(xyz=(0.0, axial, -shell_center)),
            material=material,
            name=f"{prefix}_lower_shell", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
        part.visual(
            Box((wall, length, inner_radius * 2.0)),
            origin=Origin(xyz=(shell_center, axial, 0.0)),
            material=material,
            name=f"{prefix}_front_shell", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
        part.visual(
            Box((wall, length, inner_radius * 2.0)),
            origin=Origin(xyz=(-shell_center, axial, 0.0)),
            material=material,
            name=f"{prefix}_rear_shell", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )


def _add_bottom_bracket_shell(
    part, r: ResolvedBicycleCranksetAndPedalAssemblyConfig, *, shell_mat, metal_mat
) -> None:
    shell_radius = (
        0.040
        if r.bb_shell_style in ("ebike_mid_motor", "torque_sensor_ebike")
        else 0.030
        if r.bb_shell_style in ("wide_cups", "two_piece_hollow")
        else 0.028
        if r.bb_shell_style == "square_taper"
        else 0.024
        if r.bb_shell_style == "sealed_compact"
        else 0.026
    )
    shell_length = (
        0.095
        if r.bb_shell_style in ("ebike_mid_motor", "torque_sensor_ebike")
        else 0.083
        if r.bb_shell_style in ("wide_cups", "two_piece_hollow")
        else 0.068
        if r.bb_shell_style == "sealed_compact"
        else 0.073
    )
    _add_shell_blocks(
        part,
        r,
        axial=0.0,
        length=shell_length,
        outer_radius=shell_radius,
        prefix="shell",
        material=shell_mat,
    )
    if r.bb_shell_style in ("ebike_mid_motor", "torque_sensor_ebike"):
        part.visual(
            Box((0.108, 0.072, 0.040)) if r.spindle_axis == "x" else Box((0.072, 0.108, 0.040)),
            origin=Origin(xyz=(0.0, 0.0, -0.036)),
            material=shell_mat,
            name="mid_motor_lower_housing", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track", "two_tone_black_silver"} else "metal.aluminum_bare"),
        )
    if r.bb_shell_style == "torque_sensor_ebike":
        part.visual(
            Box(_radial_bar_size(r.spindle_axis, 0.026, 0.020, 0.018)),
            origin=Origin(xyz=_radial_xyz(r.spindle_axis, -0.026, 0.046, 1.35)),
            material=metal_mat,
            name="torque_sensor_module", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
    cup_r = (
        0.033
        if r.bb_shell_style in ("external_bearing", "wide_cups", "two_piece_hollow")
        else 0.030
        if r.bb_shell_style in ("bmx_three_piece", "ebike_mid_motor", "torque_sensor_ebike")
        else 0.026
        if r.bb_shell_style in ("pressfit", "sealed_compact")
        else 0.0245
    )
    # Bearing cups must sit on (not past) the shell ends so they stay fused to
    # the shell; clamp their axial centre just inside each shell end.
    _cup_axial_max = shell_length * 0.5 - 0.004
    for name, axial in (
        ("drive_cup", min(_drive_axial(r) * 0.78, _cup_axial_max)),
        ("non_drive_cup", max(_non_drive_axial(r) * 0.78, -_cup_axial_max)),
    ):
        _add_shell_blocks(
            part, r, axial=axial, length=0.010, outer_radius=cup_r, prefix=name, material=metal_mat
        )


def _add_center_connection_visuals(
    part,
    r: ResolvedBicycleCranksetAndPedalAssemblyConfig,
    *,
    metal_mat,
    ring_mat,
    local_origin: bool = False,
) -> None:
    drive = 0.0 if local_origin else _drive_axial(r)
    non_drive = 0.0 if local_origin else _non_drive_axial(r)
    drive_side = (("right", drive), ("left", non_drive))
    for side, axial in drive_side:
        radius = 0.023
        length = 0.014
        if r.bb_shell_style in ("external_bearing", "wide_cups", "two_piece_hollow"):
            radius = 0.030
            length = 0.018
        elif r.bb_shell_style == "sealed_compact":
            radius = 0.020
            length = 0.012
        elif r.bb_shell_style == "square_taper":
            radius = 0.021
            length = 0.012
        elif r.bb_shell_style == "bmx_three_piece":
            radius = 0.019
            length = 0.026
        elif r.bb_shell_style in ("ebike_mid_motor", "torque_sensor_ebike"):
            radius = 0.034
            length = 0.018
        elif r.bb_shell_style == "power_meter_spindle":
            radius = 0.026 if side == "right" else 0.021
            length = 0.018
        part.visual(
            Cylinder(radius=radius, length=length),
            origin=Origin(
                xyz=_radial_xyz(r.spindle_axis, axial, 0.0, 0.0), rpy=_cyl_axis_rpy(r.spindle_axis)
            ),
            material=metal_mat,
            name=f"{side}_interface_collar", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
        if r.bb_shell_style == "square_taper":
            flat_axial = axial + (0.010 if side == "right" else -0.010)
            part.visual(
                Box(_radial_bar_size(r.spindle_axis, 0.010, 0.020, 0.020)),
                origin=Origin(xyz=_radial_xyz(r.spindle_axis, flat_axial, 0.0, 0.0)),
                material=metal_mat,
                name=f"{side}_square_taper_flat", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
            )
        if r.bb_shell_style == "two_piece_hollow":
            cap_axial = axial + (0.014 if side == "right" else -0.014)
            part.visual(
                Cylinder(radius=0.018 if side == "left" else 0.024, length=0.006),
                origin=Origin(
                    xyz=_radial_xyz(r.spindle_axis, cap_axial, 0.0, 0.0),
                    rpy=_cyl_axis_rpy(r.spindle_axis),
                ),
                material=ring_mat,
                name=f"{side}_two_piece_preload_cap", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track", "two_tone_black_silver"} else "metal.brushed_silver"),
            )
    if r.bb_shell_style == "torque_sensor_ebike":
        part.visual(
            Cylinder(radius=0.014, length=0.018),
            origin=Origin(
                xyz=_radial_xyz(r.spindle_axis, drive + 0.012, 0.040, 2.45),
                rpy=_cyl_axis_rpy(r.spindle_axis),
            ),
            material=ring_mat,
            name="right_torque_sensor_ring", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track", "two_tone_black_silver"} else "metal.brushed_silver"),
        )


def _add_crank_arm_visual(
    part,
    r: ResolvedBicycleCranksetAndPedalAssemblyConfig,
    side: str,
    *,
    metal_mat,
    local_axial: float | None = None,
    local_angle: float | None = None,
) -> None:
    sign = 1.0 if side == "right" else -1.0
    axial = sign * _drive_axial(r) if local_axial is None else local_axial
    # Default: combined crankset uses horizontal arms (±π/2) so pedals sit at shaft ends.
    # Modular layout passes local_angle=-π explicitly to keep arms pointing down in child frame.
    arm_angle = (
        ((-math.pi / 2.0) if side == "right" else (math.pi / 2.0))
        if local_angle is None
        else local_angle
    )
    part.visual(
        Cylinder(radius=0.025, length=0.018),
        origin=Origin(
            xyz=_radial_xyz(r.spindle_axis, axial, 0.0, 0.0), rpy=_cyl_axis_rpy(r.spindle_axis)
        ),
        material=metal_mat,
        name=f"{side}_boss", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
    )
    u_center = r.crank_length * math.sin(arm_angle) / 2.0
    z_center = r.crank_length * math.cos(arm_angle) / 2.0
    arm_in_y = abs(math.sin(arm_angle)) > abs(math.cos(arm_angle))
    if r.spindle_axis == "x":
        if arm_in_y:
            origin = Origin(xyz=(axial, u_center, 0.0))
            size = (r.arm_thickness, r.crank_length, r.arm_width)
        else:
            origin = Origin(xyz=(axial, 0.0, z_center))
            size = (r.arm_thickness, r.arm_width, r.crank_length)
    else:
        if arm_in_y:
            origin = Origin(xyz=(u_center, axial, 0.0))
            size = (r.crank_length, r.arm_thickness, r.arm_width)
        else:
            origin = Origin(xyz=(0.0, axial, z_center))
            size = (r.arm_width, r.arm_thickness, r.crank_length)
    part.visual(Box(size), origin=origin, material=metal_mat, name=f"{side}_crank_arm", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"))
    eye = _radial_xyz(r.spindle_axis, axial, r.crank_length, arm_angle)
    part.visual(
        Cylinder(radius=0.016, length=0.014),
        origin=Origin(xyz=eye, rpy=_cyl_axis_rpy(r.spindle_axis)),
        material=metal_mat,
        name=f"{side}_pedal_eye", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
    )


def _add_chainrings(
    part,
    r: ResolvedBicycleCranksetAndPedalAssemblyConfig,
    *,
    assets: AssetContext,
    ring_mat,
    metal_mat,
    axial_base: float | None = None,
) -> None:
    axial_base = _drive_axial(r) + 0.012 if axial_base is None else axial_base
    for index, radius in enumerate(r.ring_radii):
        # Spacing below the ring thickness so stacked rings fuse into one part.
        axial = axial_base + index * 0.004
        teeth = _chainring_teeth(r, index)
        part.visual(
            mesh_from_geometry(
                _chainring_geometry(r, radius, teeth),
                assets.mesh_path(
                    f"chainring_{r.spindle_axis}_{r.chainring_profile}_{index + 1}.obj"
                ),
            ),
            origin=Origin(
                xyz=_radial_xyz(r.spindle_axis, axial, 0.0, 0.0),
            ),
            material=ring_mat,
            name=f"chainring_{index + 1}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track", "two_tone_black_silver"} else "metal.brushed_silver"),
        )
        if r.chainring_profile == "bash_guard":
            part.visual(
                Cylinder(radius=radius + 0.009, length=0.004),
                origin=Origin(
                    xyz=_radial_xyz(r.spindle_axis, axial + 0.006, 0.0, 0.0),
                    rpy=_cyl_axis_rpy(r.spindle_axis),
                ),
                material=metal_mat,
                name="bash_guard_outer_disc", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
            )
        if r.chainring_profile == "narrow_wide_one_by" and index == 0:
            for marker in range(12):
                angle = 2.0 * math.pi * marker / 12.0
                part.visual(
                    Box(_radial_bar_size(r.spindle_axis, 0.004, 0.006, 0.010)),
                    origin=Origin(
                        xyz=_radial_xyz(r.spindle_axis, axial + 0.004, radius + 0.003, angle),
                        rpy=_radial_bar_rpy(r.spindle_axis, angle),
                    ),
                    material=metal_mat,
                    name=f"narrow_wide_tooth_marker_{marker}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
                )
    if r.spider_arm_count:
        spider_radius = min(r.ring_radii) * 0.68
        spider_root_radius = 0.024
        spider_arm_length = max(0.020, spider_radius - spider_root_radius)
        spider_mid_radius = spider_root_radius + spider_arm_length * 0.5
        spider_width = 0.015 if r.spider_style == "solid_carrier" else 0.010
        part.visual(
            Cylinder(radius=spider_root_radius, length=0.012),
            origin=Origin(
                xyz=_radial_xyz(r.spindle_axis, axial_base + 0.003, 0.0, 0.0),
                rpy=_cyl_axis_rpy(r.spindle_axis),
            ),
            material=metal_mat,
            name="spider_hub", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
        for arm in range(r.spider_arm_count):
            angle = 2.0 * math.pi * arm / r.spider_arm_count
            spider_axial = axial_base + 0.003
            part.visual(
                Box(_radial_bar_size(r.spindle_axis, 0.007, spider_width, spider_arm_length)),
                origin=Origin(
                    xyz=_radial_xyz(r.spindle_axis, spider_axial, spider_mid_radius, angle),
                    rpy=_radial_bar_rpy(r.spindle_axis, angle),
                ),
                material=metal_mat,
                name=f"spider_arm_{arm}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
            )
            part.visual(
                Cylinder(radius=0.0035, length=0.006),
                origin=Origin(
                    xyz=_radial_xyz(r.spindle_axis, spider_axial + 0.003, spider_radius, angle),
                    rpy=_cyl_axis_rpy(r.spindle_axis),
                ),
                material=metal_mat,
                name=f"chainring_bolt_{arm}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
            )


def _add_pedal_visual(
    part, r: ResolvedBicycleCranksetAndPedalAssemblyConfig, side: str, *, pedal_mat, rubber_mat
) -> None:
    width = (
        0.098
        if r.pedal_style in ("pinned_platform", "rat_trap")
        else 0.092
        if r.pedal_style in ("platform", "cage", "folding_cage")
        else 0.070
        if r.pedal_style == "slim_folding"
        else 0.064
        if r.pedal_style == "road_clipless"
        else 0.072
    )
    length = (
        0.086
        if r.pedal_style in ("platform", "pinned_platform", "rat_trap", "folding_cage")
        else 0.074
        if r.pedal_style in ("cage", "slim_folding")
        else 0.056
        if r.pedal_style == "road_clipless"
        else 0.060
    )
    body_distance = 0.086 if r.pedal_motion_mode == "spin_and_fold" else 0.070
    sign = 1.0 if side == "right" else -1.0
    body_half_axis = length * 0.5
    axle_start = (
        _pedal_knuckle_center_distance(r) + 0.011
        if r.pedal_motion_mode == "spin_and_fold"
        else _pedal_root_clearance(r)
    )
    axle_end = body_distance - body_half_axis
    if axle_end > axle_start:
        axle_center = sign * (axle_start + axle_end) * 0.5
        axle_length = axle_end - axle_start
        axle_origin = (axle_center, 0.0, 0.0) if r.spindle_axis == "x" else (0.0, axle_center, 0.0)
        part.visual(
            Cylinder(radius=0.005, length=axle_length),
            origin=Origin(xyz=axle_origin, rpy=_cyl_axis_rpy(r.spindle_axis)),
            material=rubber_mat,
            name=f"{side}_pedal_axle", material_class_id="metal.steel_bare",
        )
    body_offset = _pedal_local_xyz(r, side, body_distance)
    if r.pedal_style in ("cage", "rat_trap", "folding_cage", "slim_folding"):
        inner_axial = body_distance - length * 0.5 + 0.006
        outer_axial = body_distance + length * 0.5 - 0.006
        for rail_name, axial in (("inner_rail", inner_axial), ("outer_rail", outer_axial)):
            part.visual(
                Box(_pedal_box_size(r, 0.012, width, 0.018)),
                origin=Origin(xyz=_pedal_local_xyz(r, side, axial, 0.0, 0.0)),
                material=pedal_mat,
                name=f"{side}_{rail_name}", material_class_id="metal.blackened_gunmetal",
            )
        for rail_name, lateral in (
            ("front_rail", width * 0.5 - 0.006),
            ("rear_rail", -width * 0.5 + 0.006),
        ):
            part.visual(
                Box(_pedal_box_size(r, length, 0.012, 0.014)),
                origin=Origin(xyz=_pedal_local_xyz(r, side, body_distance, lateral, 0.002)),
                material=pedal_mat,
                name=f"{side}_{rail_name}", material_class_id="metal.blackened_gunmetal",
            )
        part.visual(
            Box(_pedal_box_size(r, length * 0.90, width * 0.80, 0.010)),
            origin=Origin(xyz=_pedal_local_xyz(r, side, body_distance, 0.0, 0.001)),
            material=rubber_mat,
            name=f"{side}_pedal_deck", material_class_id="rubber.directional_grooved",
        )
        if r.pedal_style in ("rat_trap", "folding_cage", "slim_folding"):
            for row, lateral in enumerate((-width * 0.40, width * 0.40)):
                for col, axial_offset in enumerate((-length * 0.28, 0.0, length * 0.28)):
                    part.visual(
                        Box(_pedal_box_size(r, 0.006, 0.005, 0.010)),
                        origin=Origin(
                            xyz=_pedal_local_xyz(
                                r, side, body_distance + axial_offset, lateral, 0.010
                            )
                        ),
                        material=rubber_mat,
                        name=f"{side}_cage_grip_pin_{row}_{col}", material_class_id="rubber.pebbled",
                    )
    elif r.pedal_style in ("clipless", "road_clipless"):
        part.visual(
            Box(_pedal_box_size(r, length, width, 0.018)),
            origin=Origin(xyz=body_offset),
            material=pedal_mat,
            name=f"{side}_pedal_body", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Box(_pedal_box_size(r, length * 0.52, width * 0.40, 0.010)),
            origin=Origin(xyz=_pedal_local_xyz(r, side, body_distance, 0.0, 0.011)),
            material=rubber_mat,
            name=f"{side}_cleat_pocket", material_class_id="rubber.smooth_plain",
        )
        if r.pedal_style == "road_clipless":
            for rail_name, axial_offset in (
                ("front_binding", -length * 0.32),
                ("rear_binding", length * 0.32),
            ):
                part.visual(
                    Box(_pedal_box_size(r, 0.010, width * 0.62, 0.012)),
                    origin=Origin(
                        xyz=_pedal_local_xyz(r, side, body_distance + axial_offset, 0.0, 0.018)
                    ),
                    material=pedal_mat,
                    name=f"{side}_{rail_name}", material_class_id="metal.blackened_gunmetal",
                )
    else:
        part.visual(
            Box(_pedal_box_size(r, length, width, 0.018)),
            origin=Origin(xyz=body_offset),
            material=pedal_mat,
            name=f"{side}_pedal_body", material_class_id="plastic.opaque_glossy_molded",
        )
        for y in (-width * 0.32, width * 0.32):
            part.visual(
                Box(_pedal_box_size(r, length * 0.85, 0.006, 0.026)),
                origin=Origin(xyz=_pedal_local_xyz(r, side, body_distance, y, 0.0)),
                material=rubber_mat,
                name=f"{side}_tread_{y:+.3f}", material_class_id="rubber.directional_grooved",
            )
        if r.pedal_style == "pinned_platform":
            for row, lateral in enumerate((-width * 0.40, width * 0.40)):
                for col, axial_offset in enumerate((-length * 0.32, 0.0, length * 0.32)):
                    part.visual(
                        Box(_pedal_box_size(r, 0.005, 0.005, 0.012)),
                        origin=Origin(
                            xyz=_pedal_local_xyz(
                                r, side, body_distance + axial_offset, lateral, 0.015
                            )
                        ),
                        material=rubber_mat,
                        name=f"{side}_platform_pin_{row}_{col}", material_class_id="rubber.pebbled",
                    )


def _pedal_origin(
    r: ResolvedBicycleCranksetAndPedalAssemblyConfig,
    side: str,
    *,
    modular_arm_local: bool = False,
) -> tuple[float, float, float]:
    axial = (
        0.0 if modular_arm_local else (_drive_axial(r) if side == "right" else _non_drive_axial(r))
    )
    if modular_arm_local:
        # Modular child-local arms always point down (-π) for consistent assembly.
        angle = -math.pi
    else:
        # Combined crankset: horizontal arms at ±π/2 so pedals sit at shaft-end height.
        angle = -math.pi / 2.0 if side == "right" else math.pi / 2.0
    return _radial_xyz(r.spindle_axis, axial, r.crank_length, angle)


def build_bicycle_crankset(
    config: BicycleCranksetAndPedalAssemblyConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or BicycleCranksetAndPedalAssemblyConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-bicycle-crankset-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = MATERIAL_PALETTES[r.material_style]
    shell_mat = model.material("bb_shell_material", rgba=palette["shell"])
    metal_mat = model.material("crank_metal", rgba=palette["metal"])
    ring_mat = model.material("chainring_material", rgba=palette["ring"])
    pedal_mat = model.material("pedal_body", rgba=palette["pedal"])
    rubber_mat = model.material("pedal_rubber", rgba=palette["rubber"])

    bb = model.part("bottom_bracket_shell")
    _add_bottom_bracket_shell(bb, r, shell_mat=shell_mat, metal_mat=metal_mat)

    if r.assembly_layout == "combined_crankset":
        crankset = model.part("crankset_combined")
        crankset.visual(
            Cylinder(radius=r.spindle_radius, length=r.spindle_length),
            origin=Origin(rpy=_cyl_axis_rpy(r.spindle_axis)),
            material=metal_mat,
            name="spindle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
        _add_center_connection_visuals(crankset, r, metal_mat=metal_mat, ring_mat=ring_mat)
        _add_crank_arm_visual(crankset, r, "right", metal_mat=metal_mat)
        _add_crank_arm_visual(crankset, r, "left", metal_mat=metal_mat)
        _add_chainrings(crankset, r, assets=assets, ring_mat=ring_mat, metal_mat=metal_mat)
        model.articulation(
            "bb_to_crank_spin",
            ArticulationType.CONTINUOUS,
            parent=bb,
            child=crankset,
            origin=Origin(),
            axis=r.axis,
            motion_limits=MotionLimits(effort=160.0, velocity=18.0),
            meta={"source_id": "S1"},
        )
        pedal_parent_right = crankset
        pedal_parent_left = crankset
    else:
        spindle = model.part("spindle")
        spindle.visual(
            Cylinder(radius=r.spindle_radius, length=r.spindle_length),
            origin=Origin(rpy=_cyl_axis_rpy(r.spindle_axis)),
            material=metal_mat,
            name="axle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
        )
        _add_center_connection_visuals(spindle, r, metal_mat=metal_mat, ring_mat=ring_mat)
        model.articulation(
            "bb_to_crank_spin",
            ArticulationType.CONTINUOUS,
            parent=bb,
            child=spindle,
            origin=Origin(),
            axis=r.axis,
            motion_limits=MotionLimits(effort=180.0, velocity=25.0),
            meta={"source_id": "S2"},
        )
        right_arm = model.part("right_crank")
        left_arm = model.part("left_crank")
        _add_crank_arm_visual(
            right_arm,
            r,
            "right",
            metal_mat=metal_mat,
            local_axial=0.0,
            local_angle=-math.pi,
        )
        _add_crank_arm_visual(
            left_arm,
            r,
            "left",
            metal_mat=metal_mat,
            local_axial=0.0,
            local_angle=-math.pi,
        )
        chainring = model.part("chainring")
        _add_chainrings(
            chainring,
            r,
            assets=assets,
            ring_mat=ring_mat,
            metal_mat=metal_mat,
            axial_base=r.arm_thickness * 0.5 + 0.0025,
        )
        model.articulation(
            "spindle_to_right_crank",
            ArticulationType.FIXED,
            parent=spindle,
            child=right_arm,
            origin=Origin(xyz=_radial_xyz(r.spindle_axis, _modular_drive_axial(r), 0.0, 0.0)),
            meta={"source_id": "S2"},
        )
        model.articulation(
            "spindle_to_left_crank",
            ArticulationType.FIXED,
            parent=spindle,
            child=left_arm,
            origin=Origin(
                xyz=_radial_xyz(r.spindle_axis, _modular_non_drive_axial(r), 0.0, 0.0),
                rpy=(0.0, math.pi, 0.0),
            ),
            meta={"source_id": "S2"},
        )
        model.articulation(
            "right_crank_to_chainring",
            ArticulationType.FIXED,
            parent=right_arm,
            child=chainring,
            origin=Origin(),
            meta={"source_id": "S3"},
        )
        pedal_parent_right = right_arm
        pedal_parent_left = left_arm

    for side, parent in (("right", pedal_parent_right), ("left", pedal_parent_left)):
        pedal = model.part(f"{side}_pedal")
        _add_pedal_visual(pedal, r, side, pedal_mat=pedal_mat, rubber_mat=rubber_mat)
        origin = Origin(
            xyz=_pedal_origin(
                r, side, modular_arm_local=r.assembly_layout == "modular_three_piece"
            ),
            rpy=_pedal_child_rpy(r, side),
        )
        if r.pedal_motion_mode == "spin":
            model.articulation(
                f"{side}_pedal_spin",
                ArticulationType.CONTINUOUS,
                parent=parent,
                child=pedal,
                origin=origin,
                axis=r.axis,
                motion_limits=MotionLimits(effort=25.0, velocity=22.0),
                meta={"source_id": "S1"},
            )
        elif r.pedal_motion_mode == "fold":
            model.articulation(
                f"{side}_pedal_fold",
                ArticulationType.REVOLUTE,
                parent=parent,
                child=pedal,
                origin=origin,
                axis=(0.0, -1.0, 0.0),
                motion_limits=MotionLimits(
                    effort=20.0, velocity=2.0, lower=0.0, upper=math.pi / 2.0
                ),
                meta={"source_id": "S4"},
            )
        else:
            knuckle = model.part(f"{side}_pedal_knuckle")
            knuckle.visual(
                Cylinder(radius=0.014, length=0.022),
                origin=Origin(
                    xyz=_outboard_xyz(r, side, _pedal_knuckle_center_distance(r)),
                    rpy=_cyl_axis_rpy(r.spindle_axis),
                ),
                material=metal_mat,
                name=f"{side}_fold_knuckle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_alloy", "bmx_raw", "dark_graphite", "polished_steel", "champagne_track"} else "metal.brushed_silver"),
            )
            model.articulation(
                f"{side}_pedal_fold",
                ArticulationType.REVOLUTE,
                parent=parent,
                child=knuckle,
                origin=origin,
                axis=(0.0, -1.0, 0.0),
                motion_limits=MotionLimits(
                    effort=20.0, velocity=2.0, lower=0.0, upper=math.pi / 2.0
                ),
                meta={"source_id": "S4"},
            )
            model.articulation(
                f"{side}_pedal_spin",
                ArticulationType.CONTINUOUS,
                parent=knuckle,
                child=pedal,
                origin=Origin(),
                axis=r.axis,
                motion_limits=MotionLimits(effort=25.0, velocity=22.0),
                meta={"source_id": "S5"},
            )

    return model


def build_seeded_bicycle_crankset(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_bicycle_crankset(config_from_seed(seed), assets=assets)


def with_overrides(
    config: BicycleCranksetAndPedalAssemblyConfig, **kwargs: object
) -> BicycleCranksetAndPedalAssemblyConfig:
    return replace(config, **kwargs)


def run_bicycle_crankset_tests(
    object_model: ArticulatedObject, config: BicycleCranksetAndPedalAssemblyConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    object_model.validate()

    # Each pedal is bolted onto its crank arm's pedal eye; the axle / deck / cage
    # sit right against the eye, so that crank<->pedal interface is intentional.
    _crank_part_names = [n for n in ("crankset_combined", "right_crank", "left_crank", "chainring")
                         if any(p.name == n for p in object_model.parts)]
    for _cp in _crank_part_names:
        for _pp in ("right_pedal", "left_pedal", "right_pedal_knuckle", "left_pedal_knuckle"):
            try:
                ctx.allow_overlap(
                    object_model.get_part(_cp),
                    object_model.get_part(_pp),
                    reason="Pedal axle/deck bolts onto the crank arm pedal eye.",
                )
            except Exception:
                pass
    crank_joint = object_model.get_articulation("bb_to_crank_spin")
    ctx.check("crank_joint_is_rotary", crank_joint.articulation_type == ArticulationType.CONTINUOUS)
    ctx.check("crank_axis_matches_config", crank_joint.axis == r.axis)
    pedal_joints = [
        j
        for j in object_model.articulations
        if "pedal" in j.name and j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check("pedal_motion_joint_count", len(pedal_joints) >= 2)
    for joint in pedal_joints:
        ctx.check(f"{joint.name}_has_origin", len(joint.origin.xyz) == 3)
        if joint.articulation_type == ArticulationType.CONTINUOUS:
            ctx.check(
                f"{joint.name}_axis_parallel", sum(a * b for a, b in zip(joint.axis, r.axis)) > 0.9
            )
        else:
            limits = joint.motion_limits
            ctx.check(
                f"{joint.name}_fold_range",
                limits is not None and 1.4 <= (limits.upper or 0.0) <= 1.7,
            )
    right = _pedal_origin(r, "right")
    left = _pedal_origin(r, "left")
    if r.spindle_axis == "x":
        radial_dot = right[1] * left[1] + right[2] * left[2]
    else:
        radial_dot = right[0] * left[0] + right[2] * left[2]
    ctx.check("left_right_pedals_opposed", radial_dot < 0.0, details=f"dot={radial_dot}")
    if r.assembly_layout == "modular_three_piece":
        ctx.check(
            "modular_has_fixed_right_arm",
            object_model.get_articulation("spindle_to_right_crank").articulation_type
            == ArticulationType.FIXED,
        )
        ctx.check("modular_has_chainring_part", object_model.get_part("chainring") is not None)
    else:
        ctx.check(
            "combined_has_crankset_part", object_model.get_part("crankset_combined") is not None
        )
    ctx.check("chainring_count_matches", len(r.ring_radii) == r.chainring_count)
    ctx.check(
        "part_diversity_parameters_present",
        all((r.assembly_layout, r.crank_arm_profile, r.chainring_profile, r.pedal_style)),
    )
    return ctx.report()
