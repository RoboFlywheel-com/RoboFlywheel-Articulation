# SPDX-License-Identifier: Apache-2.0

"""Bell tower with swinging bell procedural template.

This module is the TEMPLATE_AFTER_REVIEW implementation pass for
``articraft_template_authoring/specs_modular_v1/bell_tower_with_swinging_bell.md``.

The template keeps the spec's modular vocabulary, but it builds with a
hand-written mixed graph instead of the linear ``_modular.assemble`` helper:

* Slot A ``support_structure`` emits one grounded static support part.
* Slot B ``bell_and_yoke`` emits one or more swinging bell parts.
* Slot C ``secondary_motion`` optionally emits clapper, striker, or pulley
  parts with their own joints.

Identity invariant: every seed builds at least one bell part connected to the
support by a horizontal REVOLUTE joint.  Static louvers, braces, roof trim,
courses, arches, and decorative bolt heads are visuals on the support part.
Only genuinely moving members become independent parts.

seed=0 anchor: steel_x_braced_frame + bronze_bell_with_steel_yoke + none.

Adopted sources:
S1 rec_bell_tower_with_swinging_bell_0003:
   steel frame, X bracing, yoke arms, bell_swing.
S2 rec_bell_tower_with_swinging_bell_0004:
   octagonal cupola, louver panels, cupola cast bell, fixed clapper.
S3 rec_bell_tower_with_swinging_bell_2f0ad6cf7c17417ab1291268aa663643:
   timber bell cote, arched hanger, independent clapper.
S4 rec_bell_tower_with_swinging_bell_80aac230bfe74f47bf1eecb678386cdc:
   Gothic masonry belfry, pointed arch language, multi-bell helper.
S5 rec_bell_tower_with_swinging_bell_65f83abb46784f14a516d52ad4095a57:
   masonry tower with guide wheel.
S6 rec_bell_tower_with_swinging_bell_d362039f24d341dd934698320851a0c0:
   Japanese post-and-beam pavilion, bonsho bell, external striker.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    ConeGeometry,
    Cylinder,
    Inertial,
    LatheGeometry,
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
    "steel_x_braced_frame",
    "octagonal_rooftop_cupola",
    "raked_timber_cote",
    "gothic_masonry_belfry",
    "japanese_post_beam_pavilion",
]
BellStyle = Literal[
    "bronze_yoke",
    "arched_hanger",
    "cupola_cast",
    "bonsho",
]
SecondaryMotion = Literal[
    "none",
    "internal_clapper_revolute",
    "fixed_clapper",
    "external_striker",
    "guide_wheel",
]
RoofStyle = Literal["none", "saddle", "pyramid", "spire", "cupola_roof"]
ArchOpeningStyle = Literal["none", "rectangular", "round_arch", "pointed_arch"]
MaterialStyle = Literal["steel", "timber", "stone", "bronze_dark", "mixed_church"]
AxisName = Literal["x", "y"]


SUPPORT_STYLES: tuple[SupportStyle, ...] = (
    "steel_x_braced_frame",
    "octagonal_rooftop_cupola",
    "raked_timber_cote",
    "gothic_masonry_belfry",
    "japanese_post_beam_pavilion",
)
BELL_STYLES: tuple[BellStyle, ...] = (
    "bronze_yoke",
    "arched_hanger",
    "cupola_cast",
    "bonsho",
)
SECONDARY_MOTIONS: tuple[SecondaryMotion, ...] = (
    "none",
    "internal_clapper_revolute",
    "fixed_clapper",
    "external_striker",
    "guide_wheel",
)
ROOF_STYLES: tuple[RoofStyle, ...] = ("none", "saddle", "pyramid", "spire", "cupola_roof")
ARCH_OPENING_STYLES: tuple[ArchOpeningStyle, ...] = (
    "none",
    "rectangular",
    "round_arch",
    "pointed_arch",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "steel",
    "timber",
    "stone",
    "bronze_dark",
    "mixed_church",
)


PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "steel": {
        "support": (0.24, 0.27, 0.29, 1.0),
        "support_dark": (0.16, 0.17, 0.18, 1.0),
        "trim": (0.50, 0.52, 0.54, 1.0),
        "roof": (0.20, 0.22, 0.24, 1.0),
        "bell": (0.60, 0.45, 0.20, 1.0),
        "bell_dark": (0.18, 0.18, 0.20, 1.0),
        "wood": (0.36, 0.22, 0.12, 1.0),
    },
    "timber": {
        "support": (0.42, 0.30, 0.18, 1.0),
        "support_dark": (0.28, 0.18, 0.10, 1.0),
        "trim": (0.55, 0.40, 0.24, 1.0),
        "roof": (0.24, 0.18, 0.14, 1.0),
        "bell": (0.64, 0.45, 0.18, 1.0),
        "bell_dark": (0.16, 0.16, 0.17, 1.0),
        "wood": (0.42, 0.30, 0.18, 1.0),
    },
    "stone": {
        "support": (0.58, 0.58, 0.56, 1.0),
        "support_dark": (0.38, 0.38, 0.36, 1.0),
        "trim": (0.68, 0.68, 0.66, 1.0),
        "roof": (0.18, 0.20, 0.23, 1.0),
        "bell": (0.68, 0.48, 0.20, 1.0),
        "bell_dark": (0.13, 0.13, 0.14, 1.0),
        "wood": (0.38, 0.24, 0.12, 1.0),
    },
    "bronze_dark": {
        "support": (0.28, 0.24, 0.18, 1.0),
        "support_dark": (0.16, 0.13, 0.10, 1.0),
        "trim": (0.55, 0.42, 0.24, 1.0),
        "roof": (0.18, 0.17, 0.15, 1.0),
        "bell": (0.50, 0.35, 0.14, 1.0),
        "bell_dark": (0.12, 0.11, 0.10, 1.0),
        "wood": (0.32, 0.20, 0.10, 1.0),
    },
    "mixed_church": {
        "support": (0.64, 0.63, 0.61, 1.0),
        "support_dark": (0.42, 0.42, 0.40, 1.0),
        "trim": (0.50, 0.30, 0.18, 1.0),
        "roof": (0.20, 0.22, 0.25, 1.0),
        "bell": (0.70, 0.50, 0.22, 1.0),
        "bell_dark": (0.16, 0.16, 0.17, 1.0),
        "wood": (0.38, 0.24, 0.12, 1.0),
    },
}


@dataclass(frozen=True)
class BellTowerWithSwingingBellConfig:
    support_style: SupportStyle | None = None
    bell_style: BellStyle | None = None
    secondary_motion: SecondaryMotion | None = None
    bell_count: int = 1
    tower_height: float = 2.2
    frame_width: float = 1.1
    bell_radius: float = 0.32
    swing_axis: AxisName | None = None
    roof_style: RoofStyle | None = None
    arch_opening_style: ArchOpeningStyle | None = None
    material_style: MaterialStyle | None = None
    swing_upper: float = 0.65
    clapper_upper: float = 0.45
    striker_upper: float = 0.55
    name: str = "seeded_bell_tower_with_swinging_bell"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["steel"])
    )


@dataclass(frozen=True)
class ResolvedBellTowerWithSwingingBellConfig:
    support_style: SupportStyle
    bell_style: BellStyle
    secondary_motion: SecondaryMotion
    bell_count: int
    tower_height: float
    frame_width: float
    bell_radius: float
    swing_axis: AxisName
    roof_style: RoofStyle
    arch_opening_style: ArchOpeningStyle
    material_style: MaterialStyle
    swing_upper: float
    clapper_upper: float
    striker_upper: float
    name: str
    support_part_name: str
    pivot_z: float
    pivot_span: float
    opening_half_span: float
    bell_spacing: float
    bell_scale: float
    axis_vector: tuple[float, float, float]
    transverse_axis_vector: tuple[float, float, float]
    palette: dict[str, tuple[float, float, float, float]]


@dataclass(frozen=True)
class SupportBuild:
    part: Part
    pivot_z: float
    pivot_span: float
    opening_half_span: float
    axis_vector: tuple[float, float, float]
    transverse_axis_vector: tuple[float, float, float]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


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


def _axis_vector(axis: AxisName) -> tuple[float, float, float]:
    return (1.0, 0.0, 0.0) if axis == "x" else (0.0, 1.0, 0.0)


def _transverse_vector(axis: AxisName) -> tuple[float, float, float]:
    return (0.0, 1.0, 0.0) if axis == "x" else (1.0, 0.0, 0.0)


def _axis_rpy(axis: AxisName) -> tuple[float, float, float]:
    return _cyl_x() if axis == "x" else _cyl_y()


def _vec_scale(vec: tuple[float, float, float], scale: float) -> tuple[float, float, float]:
    return (vec[0] * scale, vec[1] * scale, vec[2] * scale)


def _vec_add(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _offset_along(
    base: tuple[float, float, float],
    vec: tuple[float, float, float],
    distance: float,
) -> tuple[float, float, float]:
    return _vec_add(base, _vec_scale(vec, distance))


def _point_between(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
) -> tuple[float, float, float]:
    return ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5, (a[2] + b[2]) * 0.5)


def _distance(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
) -> float:
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2 + (b[2] - a[2]) ** 2)


def _member_rpy(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
) -> tuple[float, float, float]:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length_xy = math.hypot(dx, dy)
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(length_xy, dz)
    return (0.0, pitch, yaw)


def _add_round_member(
    part: Part,
    *,
    name: str,
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    radius: float,
    material: object,
) -> None:
    part.visual(
        Cylinder(radius=radius, length=_distance(a, b)),
        origin=Origin(xyz=_point_between(a, b), rpy=_member_rpy(a, b)),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


def _mesh(model: ArticulatedObject, geometry: MeshGeometry, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


def _bell_shell_geometry(radius: float, *, style: BellStyle) -> MeshGeometry:
    if style == "bonsho":
        outer = [
            (radius * 0.05, -radius * 0.08),
            (radius * 0.32, -radius * 0.09),
            (radius * 0.58, -radius * 0.18),
            (radius * 0.82, -radius * 0.42),
            (radius * 0.95, -radius * 0.82),
            (radius * 0.98, -radius * 1.45),
            (radius * 1.03, -radius * 1.82),
            (radius * 0.90, -radius * 1.92),
            (radius * 0.80, -radius * 1.46),
            (radius * 0.74, -radius * 0.86),
            (radius * 0.62, -radius * 0.38),
            (radius * 0.34, -radius * 0.18),
            (radius * 0.08, -radius * 0.16),
        ]
        return LatheGeometry(outer, segments=88)

    if style == "cupola_cast":
        outer = [
            (radius * 0.38, -radius * 0.10),
            (radius * 0.52, -radius * 0.18),
            (radius * 0.70, -radius * 0.42),
            (radius * 0.86, -radius * 0.82),
            (radius * 1.02, -radius * 1.18),
            (radius * 1.07, -radius * 1.30),
        ]
        inner = [
            (radius * 0.26, -radius * 0.14),
            (radius * 0.40, -radius * 0.24),
            (radius * 0.58, -radius * 0.48),
            (radius * 0.74, -radius * 0.86),
            (radius * 0.88, -radius * 1.22),
        ]
        return LatheGeometry.from_shell_profiles(
            outer,
            inner,
            segments=64,
            start_cap="flat",
            end_cap="flat",
            lip_samples=6,
        )

    outer = [
        (radius * 0.12, radius * 0.08),
        (radius * 0.30, radius * 0.06),
        (radius * 0.55, -radius * 0.08),
        (radius * 0.78, -radius * 0.42),
        (radius * 0.92, -radius * 0.86),
        (radius * 1.02, -radius * 1.22),
        (radius * 1.06, -radius * 1.34),
    ]
    inner = [
        (radius * 0.08, radius * 0.03),
        (radius * 0.22, 0.0),
        (radius * 0.42, -radius * 0.12),
        (radius * 0.64, -radius * 0.45),
        (radius * 0.82, -radius * 0.88),
        (radius * 0.92, -radius * 1.28),
    ]
    geom = LatheGeometry.from_shell_profiles(
        outer,
        inner,
        segments=72,
        start_cap="flat",
        end_cap="flat",
        lip_samples=8,
    )
    return geom


def _pulley_geometry(radius: float) -> MeshGeometry:
    geom = TorusGeometry(radius=radius, tube=radius * 0.14, radial_segments=18, tubular_segments=64)
    return geom


def _pyramid_roof_geometry(half_width: float, height: float, z_base: float) -> MeshGeometry:
    geom = MeshGeometry()
    v0 = geom.add_vertex(-half_width, -half_width, z_base)
    v1 = geom.add_vertex(half_width, -half_width, z_base)
    v2 = geom.add_vertex(half_width, half_width, z_base)
    v3 = geom.add_vertex(-half_width, half_width, z_base)
    apex = geom.add_vertex(0.0, 0.0, z_base + height)
    geom.add_face(v0, v1, apex)
    geom.add_face(v1, v2, apex)
    geom.add_face(v2, v3, apex)
    geom.add_face(v3, v0, apex)
    geom.add_face(v0, v2, v1)
    geom.add_face(v0, v3, v2)
    return geom


def _register_materials(
    model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]]
):
    return {name: model.material(name, rgba=rgba) for name, rgba in palette.items()}


def config_from_seed(seed: int) -> BellTowerWithSwingingBellConfig:
    if seed == 0:
        return BellTowerWithSwingingBellConfig(
            support_style="steel_x_braced_frame",
            bell_style="bronze_yoke",
            secondary_motion="none",
            bell_count=1,
            tower_height=2.2,
            frame_width=1.1,
            bell_radius=0.32,
            swing_axis="y",
            roof_style="none",
            arch_opening_style="rectangular",
            material_style="steel",
            name="seeded_bell_tower_with_swinging_bell_0",
        )

    curated: dict[int, BellTowerWithSwingingBellConfig] = {
        1: BellTowerWithSwingingBellConfig(
            support_style="octagonal_rooftop_cupola",
            bell_style="cupola_cast",
            secondary_motion="fixed_clapper",
            tower_height=1.5,
            frame_width=0.8,
            bell_radius=0.22,
            swing_axis="x",
            roof_style="cupola_roof",
            arch_opening_style="none",
            material_style="mixed_church",
            name="seeded_bell_tower_with_swinging_bell_1",
        ),
        2: BellTowerWithSwingingBellConfig(
            support_style="raked_timber_cote",
            bell_style="arched_hanger",
            secondary_motion="internal_clapper_revolute",
            tower_height=1.8,
            frame_width=0.85,
            bell_radius=0.25,
            swing_axis="y",
            roof_style="saddle",
            arch_opening_style="round_arch",
            material_style="timber",
            name="seeded_bell_tower_with_swinging_bell_2",
        ),
        3: BellTowerWithSwingingBellConfig(
            support_style="gothic_masonry_belfry",
            bell_style="bronze_yoke",
            secondary_motion="internal_clapper_revolute",
            bell_count=2,
            tower_height=3.0,
            frame_width=1.55,
            bell_radius=0.28,
            swing_axis="x",
            roof_style="spire",
            arch_opening_style="pointed_arch",
            material_style="stone",
            name="seeded_bell_tower_with_swinging_bell_3",
        ),
        4: BellTowerWithSwingingBellConfig(
            support_style="japanese_post_beam_pavilion",
            bell_style="bonsho",
            secondary_motion="external_striker",
            tower_height=2.4,
            frame_width=1.35,
            bell_radius=0.38,
            swing_axis="y",
            roof_style="saddle",
            arch_opening_style="none",
            material_style="timber",
            swing_upper=0.22,
            name="seeded_bell_tower_with_swinging_bell_4",
        ),
        5: BellTowerWithSwingingBellConfig(
            support_style="gothic_masonry_belfry",
            bell_style="arched_hanger",
            secondary_motion="guide_wheel",
            tower_height=2.8,
            frame_width=1.25,
            bell_radius=0.30,
            swing_axis="x",
            roof_style="pyramid",
            arch_opening_style="pointed_arch",
            material_style="stone",
            name="seeded_bell_tower_with_swinging_bell_5",
        ),
        6: BellTowerWithSwingingBellConfig(
            support_style="steel_x_braced_frame",
            bell_style="bronze_yoke",
            secondary_motion="internal_clapper_revolute",
            bell_count=3,
            tower_height=2.6,
            frame_width=1.75,
            bell_radius=0.24,
            swing_axis="y",
            roof_style="none",
            arch_opening_style="rectangular",
            material_style="steel",
            name="seeded_bell_tower_with_swinging_bell_6",
        ),
        7: BellTowerWithSwingingBellConfig(
            support_style="raked_timber_cote",
            bell_style="bronze_yoke",
            secondary_motion="none",
            tower_height=1.65,
            frame_width=0.75,
            bell_radius=0.22,
            swing_axis="y",
            roof_style="saddle",
            arch_opening_style="round_arch",
            material_style="timber",
            name="seeded_bell_tower_with_swinging_bell_7",
        ),
        8: BellTowerWithSwingingBellConfig(
            support_style="octagonal_rooftop_cupola",
            bell_style="cupola_cast",
            secondary_motion="none",
            tower_height=1.7,
            frame_width=0.9,
            bell_radius=0.24,
            swing_axis="x",
            roof_style="cupola_roof",
            arch_opening_style="none",
            material_style="mixed_church",
            name="seeded_bell_tower_with_swinging_bell_8",
        ),
        9: BellTowerWithSwingingBellConfig(
            support_style="japanese_post_beam_pavilion",
            bell_style="bonsho",
            secondary_motion="none",
            tower_height=2.7,
            frame_width=1.5,
            bell_radius=0.44,
            swing_axis="y",
            roof_style="saddle",
            arch_opening_style="none",
            material_style="bronze_dark",
            swing_upper=0.20,
            name="seeded_bell_tower_with_swinging_bell_9",
        ),
    }
    if seed in curated:
        return curated[seed]

    rng = random.Random(seed)
    support: SupportStyle = rng.choice(SUPPORT_STYLES)  # type: ignore[assignment]
    if support == "octagonal_rooftop_cupola":
        bell: BellStyle = "cupola_cast"
        secondary: SecondaryMotion = rng.choice(("none", "fixed_clapper"))  # type: ignore[assignment]
        roof: RoofStyle = "cupola_roof"
        arch: ArchOpeningStyle = "none"
        axis: AxisName = "x"
        material: MaterialStyle = "mixed_church"
        bell_count = 1
    elif support == "japanese_post_beam_pavilion":
        bell = "bonsho"
        secondary = rng.choice(("none", "external_striker"))  # type: ignore[assignment]
        roof = "saddle"
        arch = "none"
        axis = "y"
        material = rng.choice(("timber", "bronze_dark"))  # type: ignore[assignment]
        bell_count = 1
    elif support == "gothic_masonry_belfry":
        bell = rng.choice(("bronze_yoke", "arched_hanger"))  # type: ignore[assignment]
        secondary = rng.choice(("none", "internal_clapper_revolute", "guide_wheel"))  # type: ignore[assignment]
        roof = rng.choice(("pyramid", "spire"))  # type: ignore[assignment]
        arch = "pointed_arch"
        axis = "x"
        material = "stone"
        bell_count = rng.choice((1, 2, 3))
    elif support == "raked_timber_cote":
        bell = rng.choice(("bronze_yoke", "arched_hanger"))  # type: ignore[assignment]
        secondary = rng.choice(("none", "internal_clapper_revolute"))  # type: ignore[assignment]
        roof = "saddle"
        arch = "round_arch"
        axis = "y"
        material = "timber"
        bell_count = 1
    else:
        bell = "bronze_yoke"
        secondary = rng.choice(("none", "internal_clapper_revolute", "guide_wheel"))  # type: ignore[assignment]
        roof = "none"
        arch = "rectangular"
        axis = "y"
        material = "steel"
        bell_count = rng.choice((1, 2, 3))

    width = rng.uniform(0.75, 1.75)
    return BellTowerWithSwingingBellConfig(
        support_style=support,
        bell_style=bell,
        secondary_motion=secondary,
        bell_count=bell_count,
        tower_height=rng.uniform(1.45, 3.15),
        frame_width=width,
        bell_radius=rng.uniform(0.18, min(0.46, width * 0.23)),
        swing_axis=axis,
        roof_style=roof,
        arch_opening_style=arch,
        material_style=material,
        swing_upper=rng.uniform(0.32, 0.65),
        name=f"seeded_bell_tower_with_swinging_bell_{seed}",
    )


def resolve_config(
    config: BellTowerWithSwingingBellConfig,
) -> ResolvedBellTowerWithSwingingBellConfig:
    support = _require(
        config.support_style or "steel_x_braced_frame",
        SUPPORT_STYLES,
        field_name="support_style",
    )
    bell = _require(config.bell_style or "bronze_yoke", BELL_STYLES, field_name="bell_style")
    secondary = _require(
        config.secondary_motion or "none",
        SECONDARY_MOTIONS,
        field_name="secondary_motion",
    )
    if secondary == "guide_wheel":
        secondary = "internal_clapper_revolute"
    roof = _require(config.roof_style or "none", ROOF_STYLES, field_name="roof_style")
    arch = _require(
        config.arch_opening_style or "rectangular",
        ARCH_OPENING_STYLES,
        field_name="arch_opening_style",
    )
    material = _require(
        config.material_style or "steel",
        MATERIAL_STYLES,
        field_name="material_style",
    )
    axis = _require(config.swing_axis or "y", ("x", "y"), field_name="swing_axis")

    if support == "octagonal_rooftop_cupola":
        bell = "cupola_cast"
        roof = "cupola_roof"
        arch = "none"
        axis = "x"
        if secondary not in ("none", "fixed_clapper"):
            secondary = "fixed_clapper"
    elif support == "japanese_post_beam_pavilion":
        bell = "bonsho"
        roof = "saddle"
        arch = "none"
        axis = "y"
        if secondary not in ("none", "external_striker"):
            secondary = "external_striker"
    elif support == "raked_timber_cote":
        roof = "saddle"
        # The cote's raked posts converge to +-0.12w at pivot height and its
        # bearing blocks sit on the y faces; only a y-axis journal clears them.
        axis = "y"
        if arch not in ("round_arch", "rectangular"):
            arch = "round_arch"
        if secondary in ("external_striker", "guide_wheel"):
            secondary = "internal_clapper_revolute"
        if bell == "bonsho" and secondary == "internal_clapper_revolute":
            # A bonsho is struck from outside: its side strike lug sits exactly
            # in the plane an internal clapper would sweep through.
            secondary = "fixed_clapper"
    elif support == "gothic_masonry_belfry":
        if roof not in ("pyramid", "spire"):
            roof = "pyramid"
        if arch not in ("round_arch", "pointed_arch"):
            arch = "pointed_arch"
        if bell == "bonsho":
            bell = "bronze_yoke"
    else:
        roof = "none"
        arch = "rectangular"
        # The braced frame's pivot plates, pivot bolts, and top beam are
        # authored on the front/back faces for a y-axis journal.
        axis = "y"
        if bell == "bonsho":
            bell = "bronze_yoke"
        if secondary == "external_striker":
            secondary = "internal_clapper_revolute"

    tower_height = _clamp(config.tower_height, 1.4, 3.2)
    frame_width = _clamp(config.frame_width, 0.7, 1.8)
    bell_count = max(1, min(3, int(config.bell_count)))
    if support not in ("gothic_masonry_belfry", "steel_x_braced_frame"):
        bell_count = 1
    opening_half_span = frame_width * 0.42
    max_radius = max(0.18, min(0.48, opening_half_span * 0.74))
    if support == "raked_timber_cote":
        max_radius = min(max_radius, frame_width * 0.18)
    if support == "octagonal_rooftop_cupola":
        # Bell lip reach while swinging = ~1.07r + 1.62r*sin(swing); keep it
        # inside the corner-post ring (apothem = 0.34w) with clearance.
        max_radius = min(max_radius, frame_width * 0.20)
    if support == "japanese_post_beam_pavilion":
        max_radius = min(max_radius, frame_width * 0.22)
    # Floor scales with the frame so small towers are not forced to carry an
    # oversized bell that cannot swing clear of the surrounding posts.
    bell_floor = min(0.18, max_radius)
    bell_radius = min(max(config.bell_radius, bell_floor), max_radius)
    if bell_count > 1:
        bell_radius = min(bell_radius, (frame_width / bell_count) * 0.32)
    bell_scale = bell_radius / 0.32
    bell_spacing = max(bell_radius * 2.42, frame_width / max(bell_count, 1))

    if support == "octagonal_rooftop_cupola":
        pivot_z = tower_height * 0.48
        support_name = "support_cupola"
    elif support == "gothic_masonry_belfry":
        pivot_z = tower_height * 0.72
        support_name = "support_tower"
    elif support == "japanese_post_beam_pavilion":
        pivot_z = tower_height * 0.88
        support_name = "support_pavilion"
    elif support == "raked_timber_cote":
        pivot_z = tower_height * 0.86
        support_name = "support_frame"
    else:
        pivot_z = tower_height * 0.82
        support_name = "support_frame"

    palette = dict(PALETTES[material])
    if config.palette:
        palette.update(config.palette)

    swing_cap = config.swing_upper
    if support == "octagonal_rooftop_cupola":
        swing_cap = min(swing_cap, 0.12)
    elif support == "japanese_post_beam_pavilion":
        swing_cap = min(swing_cap, 0.12)
    elif support == "raked_timber_cote":
        swing_cap = min(swing_cap, 0.13)
    elif support == "gothic_masonry_belfry":
        swing_cap = min(swing_cap, 0.32 if roof == "spire" else 0.36)
    elif bell_count > 1:
        # Adjacent bells swing toward each other along the bell line; keep the
        # combined lip sweep (2*1.66r*sin(swing)) below the rest-pose gap.
        swing_cap = min(swing_cap, 0.16)

    striker_cap = config.striker_upper
    if support == "japanese_post_beam_pavilion":
        striker_cap = min(striker_cap, 0.18)
    elif support == "gothic_masonry_belfry":
        # A striker mounted on the belfry frame fouls the bell-frame
        # crossbeams on wide arcs; keep its swing modest.
        striker_cap = min(striker_cap, 0.30)

    swing_upper = _clamp(swing_cap, 0.10, 0.46)
    if support == "octagonal_rooftop_cupola":
        # A tilted bell's lip dips below its rest height on the side it swings
        # toward: lowest point = pivot - drop*cos(swing) - lip_r*sin(swing).
        # Keep that point clear of the sill deck (top at 0.10 + 0.01w).
        lip_dip = 1.62 * math.cos(swing_upper) + 1.07 * math.sin(swing_upper)
        bell_radius = min(
            bell_radius, (pivot_z - 0.10 - frame_width * 0.01 - 0.02) / lip_dip
        )
        bell_scale = bell_radius / 0.32
    elif support == "gothic_masonry_belfry":
        # Same dip must clear the masonry shaft top (0.35h where the shaft
        # height floors at 0.25h) and the stringcourse below the belfry.
        lip_dip = 1.66 * math.cos(swing_upper) + 1.06 * math.sin(swing_upper)
        bell_radius = min(
            bell_radius, (pivot_z - tower_height * 0.35 - 0.025) / lip_dip
        )
        bell_scale = bell_radius / 0.32
    if bell_count > 1:
        # Adjacent bells swing toward each other along the bell line; the bay
        # spacing must absorb the combined lip sweep (2*1.66r*sin(swing)) at
        # the authored swing limit, not just the rest-pose shells.
        spacing_cap = max(0.1, frame_width - bell_radius * 1.2) / (bell_count - 1)
        lip_reach = 2.0 * bell_radius * 1.07
        lip_sweep = 2.0 * bell_radius * 1.66 * math.sin(swing_upper)
        needed = lip_reach + lip_sweep + 0.02
        bell_spacing = min(max(bell_spacing, needed), spacing_cap)
        if bell_spacing + 1e-9 < needed:
            # Frame too narrow for the authored swing; a real tower would
            # foul here, so trim the swing limit until the lips clear.
            avail = bell_spacing - lip_reach - 0.02
            ratio = _clamp(avail / max(1e-6, 2.0 * bell_radius * 1.66), 0.0, 1.0)
            swing_upper = min(swing_upper, math.asin(ratio))

    return ResolvedBellTowerWithSwingingBellConfig(
        support_style=support,  # type: ignore[arg-type]
        bell_style=bell,  # type: ignore[arg-type]
        secondary_motion=secondary,  # type: ignore[arg-type]
        bell_count=bell_count,
        tower_height=tower_height,
        frame_width=frame_width,
        bell_radius=bell_radius,
        swing_axis=axis,  # type: ignore[arg-type]
        roof_style=roof,  # type: ignore[arg-type]
        arch_opening_style=arch,  # type: ignore[arg-type]
        material_style=material,  # type: ignore[arg-type]
        swing_upper=swing_upper,
        clapper_upper=_clamp(config.clapper_upper, 0.18, 0.55),
        striker_upper=_clamp(striker_cap, 0.14, 0.65),
        name=config.name,
        support_part_name=support_name,
        pivot_z=pivot_z,
        pivot_span=frame_width * 0.70,
        opening_half_span=opening_half_span,
        bell_spacing=bell_spacing,
        bell_scale=bell_scale,
        axis_vector=_axis_vector(axis),  # type: ignore[arg-type]
        transverse_axis_vector=_transverse_vector(axis),  # type: ignore[arg-type]
        palette=palette,
    )


def _build_support(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
) -> SupportBuild:
    if r.support_style == "octagonal_rooftop_cupola":
        return _build_octagonal_rooftop_cupola(model, r, materials)
    if r.support_style == "raked_timber_cote":
        return _build_raked_timber_cote(model, r, materials)
    if r.support_style == "gothic_masonry_belfry":
        return _build_gothic_masonry_belfry(model, r, materials)
    if r.support_style == "japanese_post_beam_pavilion":
        return _build_japanese_post_beam_pavilion(model, r, materials)
    return _build_steel_x_braced_frame(model, r, materials)


# adopted: S1
def _build_steel_x_braced_frame(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
) -> SupportBuild:
    frame = model.part(r.support_part_name)
    w = r.frame_width
    half = w * 0.36
    base_size = w * 0.86
    top_z = r.pivot_z
    post_radius = max(0.020, w * 0.024)
    frame.visual(
        Box((base_size, base_size, 0.045)),
        origin=Origin(xyz=(0.0, 0.0, 0.0225)),
        material=materials["support"],
        name="baseplate", material_class_id="metal.steel_bare",
    )
    for name, x, y in (
        ("post_front_right", half, half),
        ("post_front_left", -half, half),
        ("post_back_left", -half, -half),
        ("post_back_right", half, -half),
    ):
        frame.visual(
            Cylinder(radius=post_radius, length=top_z - 0.045),
            origin=Origin(xyz=(x, y, 0.045 + 0.5 * (top_z - 0.045))),
            material=materials["support"],
            name=name, material_class_id="metal.steel_bare",
        )
    rail_len = half * 2.0
    frame.visual(
        Cylinder(radius=post_radius * 0.85, length=rail_len),
        origin=Origin(xyz=(0.0, half, top_z), rpy=_cyl_x()),
        material=materials["support"],
        name="front_top_rail", material_class_id="metal.steel_bare",
    )
    frame.visual(
        Cylinder(radius=post_radius * 0.85, length=rail_len),
        origin=Origin(xyz=(0.0, -half, top_z), rpy=_cyl_x()),
        material=materials["support"],
        name="back_top_rail", material_class_id="metal.steel_bare",
    )
    frame.visual(
        Cylinder(radius=post_radius * 0.85, length=rail_len),
        origin=Origin(xyz=(half, 0.0, top_z), rpy=_cyl_y()),
        material=materials["support"],
        name="right_top_rail", material_class_id="metal.steel_bare",
    )
    frame.visual(
        Cylinder(radius=post_radius * 0.85, length=rail_len),
        origin=Origin(xyz=(-half, 0.0, top_z), rpy=_cyl_y()),
        material=materials["support"],
        name="left_top_rail", material_class_id="metal.steel_bare",
    )
    frame.visual(
        Box((w * 0.12, w * 0.70, w * 0.065)),
        origin=Origin(xyz=(0.0, 0.0, top_z + w * 0.050)),
        material=materials["support"],
        name="top_beam", material_class_id="metal.steel_bare",
    )
    plate_depth = w * 0.024
    for label, y in (("front", half), ("back", -half)):
        frame.visual(
            Box((w * 0.09, plate_depth, w * 0.16)),
            origin=Origin(xyz=(0.0, y, top_z)),
            material=materials["bell_dark"],
            name=f"{label}_pivot_plate", material_class_id="metal.blackened_gunmetal",
        )
        frame.visual(
            Cylinder(radius=post_radius * 0.85, length=plate_depth * 1.5),
            origin=Origin(xyz=(0.0, y, top_z), rpy=_cyl_y()),
            material=materials["trim"],
            name=f"{label}_pivot_bolt", material_class_id="metal.brushed_silver",
        )
    brace_low = max(0.10, r.tower_height * 0.08)
    brace_high = top_z - r.tower_height * 0.10
    for face, a, b in (
        ("front_rising", (-half, half, brace_low), (half, half, brace_high)),
        ("front_falling", (half, half, brace_low), (-half, half, brace_high)),
        ("back_rising", (-half, -half, brace_low), (half, -half, brace_high)),
        ("back_falling", (half, -half, brace_low), (-half, -half, brace_high)),
        ("right_rising", (half, -half, brace_low), (half, half, brace_high)),
        ("right_falling", (half, half, brace_low), (half, -half, brace_high)),
        ("left_rising", (-half, -half, brace_low), (-half, half, brace_high)),
        ("left_falling", (-half, half, brace_low), (-half, -half, brace_high)),
    ):
        _add_round_member(
            frame,
            name=f"x_brace_{face}",
            a=a,
            b=b,
            radius=max(0.008, post_radius * 0.45),
            material=materials["support"],
        )
    for label, x, y in (
        ("front_right", half, half),
        ("front_left", -half, half),
        ("back_left", -half, -half),
        ("back_right", half, -half),
    ):
        frame.visual(
            Box((w * 0.085, w * 0.030, w * 0.075)),
            origin=Origin(xyz=(x, y, 0.09)),
            material=materials["support_dark"],
            name=f"{label}_base_gusset_x", material_class_id="metal.blackened_gunmetal",
        )
        frame.visual(
            Box((w * 0.030, w * 0.085, w * 0.075)),
            origin=Origin(xyz=(x, y, 0.09)),
            material=materials["support_dark"],
            name=f"{label}_base_gusset_y", material_class_id="metal.blackened_gunmetal",
        )
    frame.inertial = Inertial.from_geometry(
        Box((base_size, base_size, top_z + 0.12)),
        mass=95.0,
        origin=Origin(xyz=(0.0, 0.0, (top_z + 0.12) * 0.5)),
    )
    return SupportBuild(
        part=frame,
        pivot_z=top_z,
        pivot_span=w * 0.70,
        opening_half_span=half,
        axis_vector=r.axis_vector,
        transverse_axis_vector=r.transverse_axis_vector,
    )


# adopted: S2
def _build_octagonal_rooftop_cupola(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
) -> SupportBuild:
    support = model.part(r.support_part_name)
    w = r.frame_width
    pivot_z = r.pivot_z
    support.visual(
        Box((w * 0.62, w * 0.62, 0.050)),
        origin=Origin(xyz=(0.0, 0.0, 0.025)),
        material=materials["roof"],
        name="roof_plate", material_class_id="metal.paint_coated",
    )
    support.visual(
        Box((w * 0.24, w * 0.24, 0.050)),
        origin=Origin(xyz=(0.0, 0.0, 0.075)),
        material=materials["support"],
        name="cupola_curb", material_class_id="wood.painted_clean",
    )
    post_z0 = 0.10
    post_h = pivot_z * 0.72
    apothem = w * 0.34
    for index in range(8):
        theta = index * math.tau / 8.0
        px = apothem * math.cos(theta)
        py = apothem * math.sin(theta)
        support.visual(
            Box((w * 0.028, w * 0.028, post_h)),
            origin=Origin(xyz=(px, py, post_z0 + post_h * 0.5), rpy=(0.0, 0.0, theta)),
            material=materials["support"],
            name=f"corner_post_{index}", material_class_id="wood.painted_clean",
        )
    for ring_name, z in (("sill_ring", post_z0), ("upper_ring", post_z0 + post_h)):
        if ring_name == "sill_ring":
            support.visual(
                Box((apothem * 2.18, apothem * 2.18, w * 0.020)),
                origin=Origin(xyz=(0.0, 0.0, z)),
                material=materials["support"],
                name=f"{ring_name}_deck", material_class_id="wood.plank_floor",
            )
        for index in range(8):
            theta = index * math.tau / 8.0
            support.visual(
                Box((w * 0.12, w * 0.018, w * 0.030)),
                origin=Origin(
                    xyz=(apothem * math.cos(theta), apothem * math.sin(theta), z),
                    rpy=(0.0, 0.0, theta + math.pi / 2.0),
                ),
                material=materials["support"],
                name=f"{ring_name}_{index}", material_class_id="wood.painted_clean",
            )
    for index in (0, 2, 4, 6):
        theta = index * math.tau / 8.0
        support.visual(
            Box((w * 0.11, w * 0.010, w * 0.14)),
            origin=Origin(
                xyz=(apothem * math.cos(theta), apothem * math.sin(theta), pivot_z * 0.54),
                rpy=(0.0, 0.0, theta + math.pi / 2.0),
            ),
            material=materials["support_dark"],
            name=f"louver_panel_{index}", material_class_id="wood.walnut_dark",
        )
        support.visual(
            Box((w * 0.12, w * 0.020, pivot_z * 0.36)),
            origin=Origin(
                xyz=(apothem * math.cos(theta), apothem * math.sin(theta), pivot_z * 0.53),
                rpy=(0.0, 0.0, theta + math.pi / 2.0),
            ),
            material=materials["support"],
            name=f"louver_backing_stile_{index}", material_class_id="wood.painted_clean",
        )
        for slat in range(3):
            support.visual(
                Box((w * 0.10, w * 0.012, w * 0.010)),
                origin=Origin(
                    xyz=(
                        apothem * math.cos(theta),
                        apothem * math.sin(theta),
                        pivot_z * (0.45 + slat * 0.055),
                    ),
                    rpy=(0.0, 0.0, theta + math.pi / 2.0),
                ),
                material=materials["trim"],
                name=f"louver_slat_{index}_{slat}", material_class_id="wood.polished_varnished",
            )
    support.visual(
        Box((w * 0.035, w * 0.12, w * 0.16)),
        origin=Origin(xyz=(-w * 0.255, 0.0, pivot_z)),
        material=materials["bell_dark"],
        name="left_pivot_ear", material_class_id="metal.blackened_gunmetal",
    )
    support.visual(
        Box((w * 0.035, w * 0.12, w * 0.16)),
        origin=Origin(xyz=(w * 0.255, 0.0, pivot_z)),
        material=materials["bell_dark"],
        name="right_pivot_ear", material_class_id="metal.blackened_gunmetal",
    )
    support.visual(
        Cylinder(radius=w * 0.018, length=w * 0.52),
        origin=Origin(xyz=(0.0, 0.0, pivot_z), rpy=_cyl_x()),
        material=materials["trim"],
        name="pivot_shaft", material_class_id="metal.brushed_silver",
    )
    roof = ConeGeometry(radius=w * 0.22, height=w * 0.17, radial_segments=8)
    roof.rotate_z(math.pi / 8.0)
    roof.translate(0.0, 0.0, post_z0 + post_h + w * 0.70)
    support.visual(
        _mesh(model, roof, "bell_tower_cupola_roof"),
        material=materials["roof"],
        name="octagonal_roof_shell", material_class_id="metal.copper_patinated",
    )
    roof_base_z = post_z0 + post_h + w * 0.64
    ring_top_z = post_z0 + post_h
    riser_h = max(w * 0.055, roof_base_z - ring_top_z)
    support.visual(
        Box((w * 0.72, w * 0.045, w * 0.040)),
        origin=Origin(xyz=(0.0, 0.0, roof_base_z + w * 0.075)),
        material=materials["support_dark"],
        name="cupola_roof_cross_tie_x", material_class_id="wood.walnut_dark",
    )
    support.visual(
        Box((w * 0.045, w * 0.72, w * 0.040)),
        origin=Origin(xyz=(0.0, 0.0, roof_base_z + w * 0.075)),
        material=materials["support_dark"],
        name="cupola_roof_cross_tie_y", material_class_id="wood.walnut_dark",
    )
    support.visual(
        Cylinder(radius=w * 0.018, length=w * 0.33),
        origin=Origin(xyz=(0.0, 0.0, roof_base_z + w * 0.165)),
        material=materials["support_dark"],
        name="cupola_roof_kingpost", material_class_id="wood.walnut_dark",
    )
    for index in range(8):
        theta = index * math.tau / 8.0
        px = apothem * math.cos(theta)
        py = apothem * math.sin(theta)
        support.visual(
            Box((w * 0.030, w * 0.030, riser_h)),
            origin=Origin(
                xyz=(px, py, ring_top_z + riser_h * 0.5),
                rpy=(0.0, 0.0, theta),
            ),
            material=materials["support"],
            name=f"roof_riser_{index}", material_class_id="wood.painted_clean",
        )
        support.visual(
            Box((w * 0.12, w * 0.018, w * 0.030)),
            origin=Origin(
                xyz=(
                    apothem * 0.88 * math.cos(theta),
                    apothem * 0.88 * math.sin(theta),
                    roof_base_z,
                ),
                rpy=(0.0, 0.0, theta + math.pi / 2.0),
            ),
            material=materials["trim"],
            name=f"roof_eave_tie_{index}", material_class_id="wood.polished_varnished",
        )
        _add_round_member(
            support,
            name=f"roof_radial_rafter_{index}",
            a=(0.0, 0.0, roof_base_z),
            b=(px, py, roof_base_z),
            radius=max(w * 0.008, 0.006),
            material=materials["trim"],
        )
    for label, x in (("left", -w * 0.255), ("right", w * 0.255)):
        support.visual(
            Box((w * 0.030, w * 0.040, max(w * 0.10, roof_base_z - pivot_z))),
            origin=Origin(xyz=(x, 0.0, pivot_z + max(w * 0.10, roof_base_z - pivot_z) * 0.5)),
            material=materials["bell_dark"],
            name=f"{label}_pivot_ear_roof_strap", material_class_id="metal.blackened_gunmetal",
        )
    support.visual(
        Cylinder(radius=w * 0.014, length=w * 0.10),
        origin=Origin(xyz=(0.0, 0.0, post_z0 + post_h + w * 0.86)),
        material=materials["bell_dark"],
        name="finial_spire", material_class_id="metal.blackened_gunmetal",
    )
    support.visual(
        Sphere(radius=w * 0.022),
        origin=Origin(xyz=(0.0, 0.0, post_z0 + post_h + w * 0.925)),
        material=materials["bell_dark"],
        name="finial_ball", material_class_id="metal.blackened_gunmetal",
    )
    support.inertial = Inertial.from_geometry(
        Box((w * 0.65, w * 0.65, r.tower_height)),
        mass=14.0,
        origin=Origin(xyz=(0.0, 0.0, r.tower_height * 0.5)),
    )
    return SupportBuild(
        part=support,
        pivot_z=pivot_z,
        pivot_span=w * 0.22,
        opening_half_span=w * 0.17,
        axis_vector=(1.0, 0.0, 0.0),
        transverse_axis_vector=(0.0, 1.0, 0.0),
    )


# adopted: S3
def _build_raked_timber_cote(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
) -> SupportBuild:
    frame = model.part(r.support_part_name)
    w = r.frame_width
    h = r.tower_height
    pivot_z = r.pivot_z
    frame.visual(
        Box((w * 1.32, w * 0.50, h * 0.10)),
        origin=Origin(xyz=(0.0, 0.0, h * 0.05)),
        material=materials["support_dark"],
        name="stone_plinth", material_class_id="stone.cut_sedimentary",
    )
    frame.visual(
        Box((w * 1.02, w * 0.12, h * 0.07)),
        origin=Origin(xyz=(0.0, 0.0, h * 0.23)),
        material=materials["support"],
        name="lower_tie_beam", material_class_id="wood.natural_generic",
    )
    for x, label in ((-w * 0.36, "left"), (w * 0.36, "right")):
        frame.visual(
            Box((w * 0.090, w * 0.105, pivot_z + h * 0.28)),
            origin=Origin(xyz=(x, 0.0, (pivot_z + h * 0.28) * 0.5)),
            material=materials["support_dark"],
            name=f"{label}_continuous_side_post", material_class_id="wood.walnut_dark",
        )
    frame.visual(
        Box((w * 0.84, w * 0.105, h * 0.070)),
        origin=Origin(xyz=(0.0, 0.0, pivot_z + h * 0.080)),
        material=materials["support_dark"],
        name="continuous_pivot_tie", material_class_id="wood.walnut_dark",
    )
    frame.visual(
        Box((w * 0.84, w * 0.105, h * 0.070)),
        origin=Origin(xyz=(0.0, 0.0, pivot_z + h * 0.25)),
        material=materials["support_dark"],
        name="continuous_roof_tie", material_class_id="wood.walnut_dark",
    )
    run = w * 0.32
    post_len = math.sqrt((pivot_z - h * 0.18) ** 2 + run**2)
    angle = math.atan2(run, pivot_z - h * 0.18)
    frame.visual(
        Box((w * 0.09, w * 0.10, post_len)),
        origin=Origin(xyz=(-w * 0.44, 0.0, (pivot_z + h * 0.18) * 0.5), rpy=(0.0, angle, 0.0)),
        material=materials["support"],
        name="left_raked_post", material_class_id="wood.natural_generic",
    )
    frame.visual(
        Box((w * 0.09, w * 0.10, post_len)),
        origin=Origin(xyz=(w * 0.44, 0.0, (pivot_z + h * 0.18) * 0.5), rpy=(0.0, -angle, 0.0)),
        material=materials["support"],
        name="right_raked_post", material_class_id="wood.natural_generic",
    )
    frame.visual(
        Box((w * 0.14, w * 0.50, h * 0.08)),
        origin=Origin(xyz=(0.0, 0.0, pivot_z + h * 0.13)),
        material=materials["support"],
        name="ridge_beam", material_class_id="wood.natural_generic",
    )
    frame.visual(
        Box((w * 0.18, w * 0.12, h * 0.16)),
        origin=Origin(xyz=(0.0, w * 0.34, pivot_z)),
        material=materials["bell_dark"],
        name="front_bearing_block", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        Box((w * 0.18, w * 0.12, h * 0.16)),
        origin=Origin(xyz=(0.0, -w * 0.34, pivot_z)),
        material=materials["bell_dark"],
        name="rear_bearing_block", material_class_id="metal.blackened_gunmetal",
    )
    hanger_h = h * 0.13
    for y, label in ((w * 0.34, "front"), (-w * 0.34, "rear")):
        frame.visual(
            Box((w * 0.070, w * 0.060, hanger_h)),
            origin=Origin(xyz=(0.0, y, pivot_z + hanger_h * 0.5)),
            material=materials["support"],
            name=f"{label}_bearing_roof_hanger", material_class_id="wood.natural_generic",
        )
        frame.visual(
            Box((w * 0.28, w * 0.055, h * 0.050)),
            origin=Origin(xyz=(0.0, y, pivot_z + h * 0.13)),
            material=materials["support"],
            name=f"{label}_bearing_to_ridge_tie", material_class_id="wood.natural_generic",
        )
    frame.visual(
        Cylinder(radius=w * 0.030, length=w * 0.42),
        origin=Origin(xyz=(0.0, 0.0, pivot_z), rpy=_cyl_y()),
        material=materials["bell_dark"],
        name="pivot_bearing_pin", material_class_id="metal.blackened_gunmetal",
    )
    if r.arch_opening_style == "round_arch":
        for index, x in enumerate((-w * 0.12, 0.0, w * 0.12)):
            frame.visual(
                Cylinder(radius=w * 0.030, length=w * 0.40),
                origin=Origin(xyz=(x, 0.0, pivot_z + h * 0.05), rpy=_cyl_y()),
                material=materials["trim"],
                name=f"arched_yoke_support_{index}", material_class_id="wood.polished_varnished",
            )
    if r.roof_style == "saddle":
        for x, label, tilt in ((-w * 0.32, "left", 0.34), (w * 0.32, "right", -0.34)):
            frame.visual(
                Box((w * 0.10, w * 0.48, h * 0.045)),
                origin=Origin(xyz=(x, 0.0, pivot_z + h * 0.17), rpy=(0.0, tilt, 0.0)),
                material=materials["support_dark"],
                name=f"{label}_roof_post_tie", material_class_id="wood.walnut_dark",
            )
        frame.visual(
            Box((w * 0.74, w * 0.54, h * 0.06)),
            origin=Origin(xyz=(-w * 0.11, 0.0, pivot_z + h * 0.25), rpy=(0.0, 0.36, 0.0)),
            material=materials["roof"],
            name="left_roof_plane", material_class_id="wood.rustic_weathered",
        )
        frame.visual(
            Box((w * 0.74, w * 0.54, h * 0.06)),
            origin=Origin(xyz=(w * 0.11, 0.0, pivot_z + h * 0.25), rpy=(0.0, -0.36, 0.0)),
            material=materials["roof"],
            name="right_roof_plane", material_class_id="wood.rustic_weathered",
        )
    frame.inertial = Inertial.from_geometry(
        Box((w * 1.35, w * 0.56, h)),
        mass=260.0,
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
    )
    return SupportBuild(
        part=frame,
        pivot_z=pivot_z,
        pivot_span=w * 0.40,
        opening_half_span=w * 0.32,
        axis_vector=(0.0, 1.0, 0.0),
        transverse_axis_vector=(1.0, 0.0, 0.0),
    )


# adopted: S4, S5
def _build_gothic_masonry_belfry(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
) -> SupportBuild:
    tower = model.part(r.support_part_name)
    w = r.frame_width
    h = r.tower_height
    pivot_z = r.pivot_z
    shaft_h = max(h * 0.25, pivot_z - r.bell_radius * 4.60 - h * 0.10)
    tower.visual(
        Box((w * 1.58, w * 1.58, h * 0.10)),
        origin=Origin(xyz=(0.0, 0.0, h * 0.05)),
        material=materials["support_dark"],
        name="foundation_plinth", material_class_id="stone.cut_sedimentary",
    )
    tower.visual(
        Box((w * 1.24, w * 1.24, shaft_h)),
        origin=Origin(xyz=(0.0, 0.0, h * 0.10 + shaft_h * 0.5)),
        material=materials["support"],
        name="main_masonry_shaft", material_class_id="stone.masonry_wall",
    )
    for x in (-w * 0.67, w * 0.67):
        for y in (-w * 0.67, w * 0.67):
            tower.visual(
                Box((w * 0.14, w * 0.14, shaft_h + h * 0.08)),
                origin=Origin(xyz=(x, y, h * 0.10 + (shaft_h + h * 0.08) * 0.5)),
                material=materials["support_dark"],
                name=f"corner_buttress_{x:.2f}_{y:.2f}", material_class_id="stone.masonry_wall",
            )
    belfry_floor_z = shaft_h + h * 0.05
    tower.visual(
        Box((w * 1.42, w * 1.42, h * 0.055)),
        origin=Origin(xyz=(0.0, 0.0, belfry_floor_z)),
        material=materials["support_dark"],
        name="belfry_stringcourse", material_class_id="stone.cut_sedimentary",
    )
    cornice_z = pivot_z + h * 0.32
    for x in (-w * 0.54, w * 0.54):
        for y in (-w * 0.54, w * 0.54):
            tower.visual(
                Box((w * 0.20, w * 0.20, cornice_z)),
                origin=Origin(xyz=(x, y, cornice_z * 0.5)),
                material=materials["support"],
                name=f"continuous_belfry_pylon_{x:.2f}_{y:.2f}", material_class_id="stone.masonry_wall",
            )
    pier_z = belfry_floor_z + h * 0.20
    pier_h = h * 0.34
    for x in (-w * 0.54, w * 0.54):
        for y in (-w * 0.54, w * 0.54):
            tower.visual(
                Box((w * 0.18, w * 0.18, pier_h)),
                origin=Origin(xyz=(x, y, pier_z + pier_h * 0.5)),
                material=materials["support"],
                name=f"belfry_pier_{x:.2f}_{y:.2f}", material_class_id="stone.masonry_wall",
            )
    for side, xyz, dims, rpy in (
        ("front", (0.0, -w * 0.61, pivot_z), (w * 1.15, w * 0.10, h * 0.10), (0.0, 0.0, 0.0)),
        ("rear", (0.0, w * 0.61, pivot_z), (w * 1.15, w * 0.10, h * 0.10), (0.0, 0.0, 0.0)),
        ("left", (-w * 0.61, 0.0, pivot_z), (w * 0.10, w * 1.15, h * 0.10), (0.0, 0.0, 0.0)),
        ("right", (w * 0.61, 0.0, pivot_z), (w * 0.10, w * 1.15, h * 0.10), (0.0, 0.0, 0.0)),
    ):
        tower.visual(
            Box(dims),
            origin=Origin(xyz=xyz, rpy=rpy),
            material=materials["wood"],
            name=f"{side}_bell_frame_crossbeam", material_class_id="wood.natural_generic",
        )
    if r.swing_axis == "x":
        # Pillow blocks and axle for the native x-axis journal. For a y-axis
        # journal the bell line runs along x instead, and bells would land on
        # these fixed +-0.28w blocks; the generic per-bell bearing hardware
        # from _build_bell_joints carries that case.
        for index, x in enumerate((-w * 0.28, w * 0.28)):
            tower.visual(
                Box((w * 0.11, w * 0.22, h * 0.10)),
                origin=Origin(xyz=(x, 0.0, pivot_z)),
                material=materials["bell_dark"],
                name=f"bell_bearing_{index}", material_class_id="metal.blackened_gunmetal",
            )
            tower.visual(
                Box((w * 0.075, w * 0.115, h * 0.18)),
                origin=Origin(xyz=(x, 0.0, pivot_z + h * 0.09)),
                material=materials["wood"],
                name=f"bell_bearing_drop_strap_{index}", material_class_id="wood.natural_generic",
            )
        tower.visual(
            Cylinder(radius=w * 0.030, length=w * 0.68),
            origin=Origin(xyz=(0.0, 0.0, pivot_z), rpy=_cyl_x()),
            material=materials["bell_dark"],
            name="bell_axle_crossbar", material_class_id="metal.blackened_gunmetal",
        )
    tower.visual(
        Box((w * 1.20, w * 0.18, h * 0.080)),
        origin=Origin(xyz=(0.0, 0.0, pivot_z + h * 0.090)),
        material=materials["wood"],
        name="central_bell_frame_tie_x", material_class_id="wood.natural_generic",
    )
    tower.visual(
        Box((w * 0.18, w * 1.20, h * 0.080)),
        origin=Origin(xyz=(0.0, 0.0, pivot_z + h * 0.090)),
        material=materials["wood"],
        name="central_bell_frame_tie_y", material_class_id="wood.natural_generic",
    )
    if r.arch_opening_style in ("round_arch", "pointed_arch"):
        for side, y in (("front", -w * 0.62), ("rear", w * 0.62)):
            tower.visual(
                Box((w * 0.98, w * 0.095, h * 0.050)),
                origin=Origin(xyz=(0.0, y, pivot_z + h * 0.18)),
                material=materials["trim"],
                name=f"{side}_arch_spring", material_class_id="stone.cut_sedimentary",
            )
            tower.visual(
                Cylinder(radius=w * 0.24, length=w * 0.052),
                origin=Origin(xyz=(0.0, y, pivot_z + h * 0.28), rpy=_cyl_y()),
                material=materials["trim"],
                name=f"{side}_arch_crown", material_class_id="stone.cut_sedimentary",
            )
    course_count = 6
    for i in range(course_count):
        z = h * 0.20 + i * shaft_h / (course_count + 1)
        tower.visual(
            Box((w * 1.28, w * 0.035, h * 0.014)),
            origin=Origin(xyz=(0.0, -w * 0.615, z)),
            material=materials["support_dark"],
            name=f"front_masonry_course_{i}", material_class_id="stone.masonry_wall",
        )
        tower.visual(
            Box((w * 1.28, w * 0.035, h * 0.014)),
            origin=Origin(xyz=(0.0, w * 0.615, z)),
            material=materials["support_dark"],
            name=f"rear_masonry_course_{i}", material_class_id="stone.masonry_wall",
        )
    tower.visual(
        Box((w * 1.42, w * 1.42, h * 0.055)),
        origin=Origin(xyz=(0.0, 0.0, cornice_z)),
        material=materials["support_dark"],
        name="belfry_cornice", material_class_id="stone.cut_sedimentary",
    )
    for x in (-w * 0.54, w * 0.54):
        for y in (-w * 0.54, w * 0.54):
            tower.visual(
                Box((w * 0.10, w * 0.10, max(h * 0.050, cornice_z - (pier_z + pier_h)))),
                origin=Origin(
                    xyz=(
                        x,
                        y,
                        pier_z + pier_h + max(h * 0.050, cornice_z - (pier_z + pier_h)) * 0.5,
                    )
                ),
                material=materials["support"],
                name=f"cornice_riser_{x:.2f}_{y:.2f}", material_class_id="stone.masonry_wall",
            )
    if r.roof_style == "spire":
        tower.visual(
            Box((w * 1.00, w * 1.00, h * 0.020)),
            origin=Origin(xyz=(0.0, 0.0, cornice_z + h * 0.028)),
            material=materials["support_dark"],
            name="roof_mortar_bed", material_class_id="plaster.smooth",
        )
        roof = _pyramid_roof_geometry(w * 0.66, h * 0.52, cornice_z + h * 0.03)
        tower.visual(
            _mesh(model, roof, "bell_tower_gothic_spire"),
            material=materials["roof"],
            name="spire_roof", material_class_id="stone.slate",
        )
        tower.visual(
            Cylinder(radius=w * 0.035, length=h * 0.18),
            origin=Origin(xyz=(0.0, 0.0, cornice_z + h * 0.60)),
            material=materials["bell_dark"],
            name="spire_finial", material_class_id="metal.blackened_gunmetal",
        )
    else:
        tower.visual(
            Box((w * 1.05, w * 1.05, h * 0.020)),
            origin=Origin(xyz=(0.0, 0.0, cornice_z + h * 0.028)),
            material=materials["support_dark"],
            name="roof_mortar_bed", material_class_id="plaster.smooth",
        )
        roof = _pyramid_roof_geometry(w * 0.70, h * 0.28, cornice_z + h * 0.03)
        tower.visual(
            _mesh(model, roof, "bell_tower_masonry_pyramid_roof"),
            material=materials["roof"],
            name="pyramid_roof", material_class_id="stone.slate",
        )
    tower.inertial = Inertial.from_geometry(
        Box((w * 1.6, w * 1.6, h)),
        mass=1400.0,
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
    )
    return SupportBuild(
        part=tower,
        pivot_z=pivot_z,
        pivot_span=w * 0.98,
        opening_half_span=w * 0.55,
        axis_vector=(1.0, 0.0, 0.0),
        transverse_axis_vector=(0.0, 1.0, 0.0),
    )


# adopted: S6
def _build_japanese_post_beam_pavilion(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
) -> SupportBuild:
    frame = model.part(r.support_part_name)
    w = r.frame_width
    h = r.tower_height
    pivot_z = r.pivot_z
    frame.visual(
        Box((w * 1.36, w * 0.36, h * 0.045)),
        origin=Origin(xyz=(-w * 0.32, 0.0, h * 0.022)),
        material=materials["support_dark"],
        name="left_foot", material_class_id="wood.walnut_dark",
    )
    frame.visual(
        Box((w * 1.36, w * 0.36, h * 0.045)),
        origin=Origin(xyz=(w * 0.32, 0.0, h * 0.022)),
        material=materials["support_dark"],
        name="right_foot", material_class_id="wood.walnut_dark",
    )
    for x in (-w * 0.44, w * 0.44):
        frame.visual(
            Box((w * 0.18, w * 0.18, h * 0.105)),
            origin=Origin(xyz=(x, 0.0, h * 0.052)),
            material=materials["support_dark"],
            name=f"foot_to_post_socket_{x:.2f}", material_class_id="wood.walnut_dark",
        )
        frame.visual(
            Box((w * 0.12, w * 0.14, pivot_z - h * 0.05)),
            origin=Origin(xyz=(x, 0.0, h * 0.05 + (pivot_z - h * 0.05) * 0.5)),
            material=materials["support"],
            name=f"post_{x:.2f}", material_class_id="wood.natural_generic",
        )
    frame.visual(
        Box((w * 1.16, w * 0.18, h * 0.09)),
        origin=Origin(xyz=(0.0, 0.0, pivot_z + h * 0.07)),
        material=materials["support"],
        name="crossbeam", material_class_id="wood.natural_generic",
    )
    frame.visual(
        Box((w * 1.06, w * 0.12, h * 0.06)),
        origin=Origin(xyz=(0.0, 0.0, h * 0.20)),
        material=materials["support"],
        name="lower_tie", material_class_id="wood.natural_generic",
    )
    frame.visual(
        Box((w * 0.08, w * 0.12, h * 0.18)),
        origin=Origin(xyz=(-w * 0.39, w * 0.11, pivot_z - h * 0.05), rpy=(0.0, 0.55, 0.0)),
        material=materials["support_dark"],
        name="left_brace", material_class_id="wood.walnut_dark",
    )
    frame.visual(
        Box((w * 0.08, w * 0.12, h * 0.18)),
        origin=Origin(xyz=(w * 0.39, -w * 0.11, pivot_z - h * 0.05), rpy=(0.0, -0.55, 0.0)),
        material=materials["support_dark"],
        name="right_brace", material_class_id="wood.walnut_dark",
    )
    for y, label in ((w * 0.08, "front"), (-w * 0.08, "back")):
        frame.visual(
            Box((w * 0.07, w * 0.05, h * 0.07)),
            origin=Origin(xyz=(0.0, y, pivot_z)),
            material=materials["bell_dark"],
            name=f"bell_hanger_{label}", material_class_id="metal.blackened_gunmetal",
        )
        frame.visual(
            Box((w * 0.060, w * 0.040, h * 0.11)),
            origin=Origin(xyz=(0.0, y, pivot_z + h * 0.055)),
            material=materials["support_dark"],
            name=f"bell_hanger_drop_{label}", material_class_id="wood.walnut_dark",
        )
    frame.visual(
        Cylinder(radius=w * 0.018, length=w * 0.20),
        origin=Origin(xyz=(0.0, 0.0, pivot_z), rpy=_cyl_y()),
        material=materials["bell_dark"],
        name="bell_crown_pin", material_class_id="metal.blackened_gunmetal",
    )
    if r.roof_style == "saddle":
        for x, label, tilt in ((-w * 0.43, "left", 0.24), (w * 0.43, "right", -0.24)):
            frame.visual(
                Box((w * 0.10, w * 0.16, h * 0.16)),
                origin=Origin(xyz=(x, 0.0, pivot_z + h * 0.16), rpy=(0.0, tilt, 0.0)),
                material=materials["support_dark"],
                name=f"{label}_roof_to_post_strut", material_class_id="wood.walnut_dark",
            )
        frame.visual(
            Box((w * 1.06, w * 0.14, h * 0.052)),
            origin=Origin(xyz=(0.0, 0.0, pivot_z + h * 0.205)),
            material=materials["support"],
            name="roof_tie_under_saddle", material_class_id="wood.natural_generic",
        )
        frame.visual(
            Box((w * 1.24, w * 0.44, h * 0.055)),
            origin=Origin(xyz=(-w * 0.09, 0.0, pivot_z + h * 0.25), rpy=(0.0, 0.28, 0.0)),
            material=materials["roof"],
            name="left_saddle_roof", material_class_id="ceramic.architectural_tile",
        )
        frame.visual(
            Box((w * 1.24, w * 0.44, h * 0.055)),
            origin=Origin(xyz=(w * 0.09, 0.0, pivot_z + h * 0.25), rpy=(0.0, -0.28, 0.0)),
            material=materials["roof"],
            name="right_saddle_roof", material_class_id="ceramic.architectural_tile",
        )
    frame.inertial = Inertial.from_geometry(
        Box((w * 1.4, w * 0.55, h)),
        mass=620.0,
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
    )
    return SupportBuild(
        part=frame,
        pivot_z=pivot_z,
        pivot_span=w * 0.20,
        opening_half_span=w * 0.44,
        axis_vector=(0.0, 1.0, 0.0),
        transverse_axis_vector=(1.0, 0.0, 0.0),
    )


def _bell_offsets(r: ResolvedBellTowerWithSwingingBellConfig) -> list[float]:
    if r.bell_count == 1:
        return [0.0]
    start = -0.5 * (r.bell_count - 1) * r.bell_spacing
    return [start + i * r.bell_spacing for i in range(r.bell_count)]


def _clapper_pivot_drop(r: ResolvedBellTowerWithSwingingBellConfig) -> float:
    # The cupola_cast shell-mount collar fills -0.40r..-0.58r around the crown,
    # so hang its clapper pivot below the collar instead of inside it.
    return r.bell_radius * (0.68 if r.bell_style == "cupola_cast" else 0.55)


# adopted: S1, S2, S3, S4, S5, S6
def _build_bell_part(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
    *,
    index: int,
    offset: float,
) -> Part:
    name = "bell" if r.bell_count == 1 else f"bell_{index}"
    bell = model.part(name)
    scale = r.bell_scale
    axis = r.swing_axis
    journal_len = max(r.bell_radius * 1.85, r.pivot_span / max(r.bell_count, 1) * 0.78)
    bell.visual(
        Cylinder(radius=r.bell_radius * 0.055, length=journal_len),
        origin=Origin(rpy=_axis_rpy(axis)),
        material=materials["bell_dark"],
        name="pivot_journal", material_class_id="metal.blackened_gunmetal",
    )
    if r.bell_style == "bronze_yoke":
        bell.visual(
            Cylinder(radius=r.bell_radius * 0.10, length=r.bell_radius * 0.16),
            origin=Origin(
                xyz=_offset_along((0.0, 0.0, 0.0), r.axis_vector, journal_len * 0.48),
                rpy=_axis_rpy(axis),
            ),
            material=materials["bell_dark"],
            name="outer_yoke_boss", material_class_id="metal.blackened_gunmetal",
        )
        bell.visual(
            Cylinder(radius=r.bell_radius * 0.10, length=r.bell_radius * 0.16),
            origin=Origin(
                xyz=_offset_along((0.0, 0.0, 0.0), r.axis_vector, -journal_len * 0.48),
                rpy=_axis_rpy(axis),
            ),
            material=materials["bell_dark"],
            name="inner_yoke_boss", material_class_id="metal.blackened_gunmetal",
        )
        bell.visual(
            Box((r.bell_radius * 0.22, journal_len * 0.88, r.bell_radius * 0.18)),
            origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.34)),
            material=materials["bell_dark"],
            name="yoke_crossbar", material_class_id="metal.blackened_gunmetal",
        )
    elif r.bell_style == "arched_hanger":
        bell.visual(
            Box((r.bell_radius * 0.34, journal_len * 0.75, r.bell_radius * 0.14)),
            origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.05)),
            material=materials["wood"],
            name="headstock", material_class_id="wood.natural_generic",
        )
    elif r.bell_style == "bonsho":
        bell.visual(
            Box((r.bell_radius * 0.38, r.bell_radius * 0.30, r.bell_radius * 0.12)),
            origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.05)),
            material=materials["bell"],
            name="bell_crown_cap", material_class_id="metal.bronze_cast",
        )
        bell.visual(
            Cylinder(radius=r.bell_radius * 0.22, length=r.bell_radius * 0.18),
            origin=Origin(xyz=(-r.bell_radius * 0.72, 0.0, -r.bell_radius * 1.22), rpy=_cyl_x()),
            material=materials["bell"],
            name="strike_boss", material_class_id="metal.bronze_cast",
        )
    else:
        crown_z = -r.bell_radius * (0.25 if r.bell_style == "cupola_cast" else 0.05)
        crown_h = r.bell_radius * (0.11 if r.bell_style == "cupola_cast" else 0.18)
        bell.visual(
            Box((r.bell_radius * 0.34, r.bell_radius * 0.22, crown_h)),
            origin=Origin(xyz=(0.0, 0.0, crown_z)),
            material=materials["bell_dark"],
            name="crown_block", material_class_id="metal.blackened_gunmetal",
        )
        for sign, label in ((-1.0, "left"), (1.0, "right")):
            bell.visual(
                Cylinder(radius=r.bell_radius * 0.060, length=r.bell_radius * 0.22),
                origin=Origin(xyz=(sign * r.bell_radius * 0.30, 0.0, 0.0), rpy=_cyl_x()),
                material=materials["bell_dark"],
                name=f"{label}_trunnion", material_class_id="metal.blackened_gunmetal",
            )
        if r.bell_style == "cupola_cast":
            # Wide enough to tie both trunnion shafts (inner ends at +-0.19r)
            # back to the crown, so the trunnions stay connected even when the
            # pivot journal runs along y instead of through them.
            bell.visual(
                Box((r.bell_radius * 0.44, r.bell_radius * 0.11, r.bell_radius * 0.30)),
                origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.13)),
                material=materials["bell_dark"],
                name="cupola_trunnion_crown_bridge", material_class_id="metal.blackened_gunmetal",
            )
    bell.visual(
        Cylinder(
            radius=r.bell_radius * 0.12,
            length=r.bell_radius * (0.46 if r.bell_style == "cupola_cast" else 0.78),
        ),
        origin=Origin(
            xyz=(0.0, 0.0, -r.bell_radius * (0.48 if r.bell_style == "cupola_cast" else 0.36))
        ),
        material=materials["bell_dark"],
        name="crown_to_shell_neck", material_class_id="metal.blackened_gunmetal",
    )
    if r.bell_style == "cupola_cast":
        bell.visual(
            Cylinder(radius=r.bell_radius * 0.34, length=r.bell_radius * 0.18),
            origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.49)),
            material=materials["bell_dark"],
            name="shell_mount_collar", material_class_id="metal.blackened_gunmetal",
        )
    bell.visual(
        _mesh(
            model,
            _bell_shell_geometry(r.bell_radius, style=r.bell_style),
            f"bell_tower_{name}_{r.bell_style}_shell",
        ),
        origin=Origin(
            xyz=(0.0, 0.0, -r.bell_radius * (0.32 if r.bell_style != "bonsho" else 0.08))
        ),
        material=materials["bell"],
        name="bell_shell", material_class_id="metal.bronze_cast",
    )
    if r.bell_style == "bonsho":
        bell.visual(
            Box((r.bell_radius * 0.42, r.bell_radius * 0.13, r.bell_radius * 0.18)),
            origin=Origin(xyz=(-r.bell_radius * 0.48, 0.0, -r.bell_radius * 1.22)),
            material=materials["bell"],
            name="strike_boss_neck", material_class_id="metal.bronze_cast",
        )
    if r.secondary_motion == "internal_clapper_revolute":
        bell.visual(
            Cylinder(radius=r.bell_radius * 0.050, length=r.bell_radius * 0.26),
            origin=Origin(xyz=(0.0, 0.0, -_clapper_pivot_drop(r)), rpy=_axis_rpy(r.swing_axis)),
            material=materials["bell_dark"],
            name="clapper_pivot_socket", material_class_id="metal.blackened_gunmetal",
        )
    if r.secondary_motion == "fixed_clapper" or (
        r.secondary_motion == "none" and r.bell_style == "cupola_cast"
    ):
        bell.visual(
            Cylinder(radius=r.bell_radius * 0.020, length=r.bell_radius * 0.62),
            origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.70)),
            material=materials["bell_dark"],
            name="fixed_clapper_rod", material_class_id="metal.blackened_gunmetal",
        )
        # The hanger rod starts below the support pivot pin/crossbar that
        # crosses the crown at pivot height (up to 0.03w radius on the timber
        # and masonry supports) instead of passing through it.
        hanger_top = -max(r.bell_radius * 0.10, r.frame_width * 0.038)
        hanger_bottom = -r.bell_radius * 0.46
        bell.visual(
            Cylinder(radius=r.bell_radius * 0.022, length=hanger_top - hanger_bottom),
            origin=Origin(xyz=(0.0, 0.0, (hanger_top + hanger_bottom) * 0.5)),
            material=materials["bell_dark"],
            name="fixed_clapper_hanger", material_class_id="metal.blackened_gunmetal",
        )
        bell.visual(
            Sphere(radius=r.bell_radius * 0.085),
            origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 1.08)),
            material=materials["bell_dark"],
            name="fixed_clapper_ball", material_class_id="metal.blackened_gunmetal",
        )
    bell.inertial = Inertial.from_geometry(
        Box((r.bell_radius * 2.25, journal_len, r.bell_radius * 2.15)),
        mass=70.0 * max(0.35, scale**3),
        origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.78)),
    )
    return bell


def _bell_joint_origin(
    r: ResolvedBellTowerWithSwingingBellConfig,
    offset: float,
) -> tuple[float, float, float]:
    base = (0.0, 0.0, r.pivot_z)
    return _offset_along(base, r.transverse_axis_vector, offset)


def _bearing_pin_length(r: ResolvedBellTowerWithSwingingBellConfig) -> float:
    if r.swing_axis == "x":
        if r.support_style == "octagonal_rooftop_cupola":
            return max(r.frame_width * 0.52, r.bell_radius * 1.12)
        if r.support_style == "gothic_masonry_belfry":
            return max(r.frame_width * 0.56, r.bell_radius * 1.18)
        return max(r.frame_width * 0.44, r.bell_radius * 1.10)
    if r.support_style == "raked_timber_cote":
        return max(r.frame_width * 0.68, r.bell_radius * 1.24)
    if r.support_style == "japanese_post_beam_pavilion":
        return max(r.frame_width * 0.24, r.bell_radius * 0.74)
    return max(r.frame_width * 0.78, r.bell_radius * 1.18)


def _bearing_min_strap_height(r: ResolvedBellTowerWithSwingingBellConfig) -> float:
    if r.support_style == "octagonal_rooftop_cupola":
        return max(r.frame_width * 0.14, r.tower_height * 0.055)
    if r.support_style == "raked_timber_cote":
        return r.tower_height * 0.13
    if r.support_style == "gothic_masonry_belfry":
        return r.tower_height * 0.11
    if r.support_style == "japanese_post_beam_pavilion":
        return r.tower_height * 0.11
    return max(r.frame_width * 0.11, r.tower_height * 0.050)


def _bearing_roof_anchor_z(r: ResolvedBellTowerWithSwingingBellConfig) -> float:
    if r.support_style == "octagonal_rooftop_cupola":
        ring_top_z = 0.10 + r.pivot_z * 0.72
        return ring_top_z + r.frame_width * 0.235
    if r.support_style == "raked_timber_cote":
        return r.pivot_z + r.tower_height * 0.13
    if r.support_style == "gothic_masonry_belfry":
        return r.pivot_z + r.tower_height * 0.32
    if r.support_style == "japanese_post_beam_pavilion":
        return r.pivot_z + r.tower_height * 0.205
    return r.pivot_z + r.frame_width * 0.050


def _add_bell_bearing_hardware(
    support: Part,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
    *,
    origin: tuple[float, float, float],
    index: int,
) -> None:
    label = "bell" if r.bell_count == 1 else f"bell_{index}"
    pin_len = _bearing_pin_length(r)
    pin_radius = max(0.012, r.bell_radius * 0.050)
    support.visual(
        Cylinder(radius=pin_radius, length=pin_len),
        origin=Origin(xyz=origin, rpy=_axis_rpy(r.swing_axis)),
        material=materials["bell_dark"],
        name="bell_bearing_pin" if r.bell_count == 1 else f"bell_{index}_bearing_pin", material_class_id="metal.blackened_gunmetal",
    )

    cheek_depth = max(0.020, r.bell_radius * 0.095)
    cheek_span = max(0.070, r.bell_radius * 0.36)
    cheek_height = max(0.060, r.bell_radius * 0.26)
    anchor_z = max(origin[2] + _bearing_min_strap_height(r), _bearing_roof_anchor_z(r))
    strap_h = max(0.020, anchor_z - origin[2])
    strap_span = max(0.045, r.bell_radius * 0.20)
    strap_depth = max(0.018, r.bell_radius * 0.070)
    top_tie_depth = max(0.026, r.bell_radius * 0.085)
    axis = r.axis_vector
    cheek_dims = (
        (cheek_depth, cheek_span, cheek_height)
        if r.swing_axis == "x"
        else (cheek_span, cheek_depth, cheek_height)
    )
    strap_dims = (
        (strap_depth, strap_span, strap_h)
        if r.swing_axis == "x"
        else (strap_span, strap_depth, strap_h)
    )
    roof_tie_dims = (
        (pin_len + cheek_depth * 2.0, strap_span * 1.35, top_tie_depth)
        if r.swing_axis == "x"
        else (strap_span * 1.35, pin_len + cheek_depth * 2.0, top_tie_depth)
    )
    for side_name, sign in (("a", -1.0), ("b", 1.0)):
        side_origin = _offset_along(origin, axis, sign * pin_len * 0.5)
        support.visual(
            Box(cheek_dims),
            origin=Origin(xyz=side_origin),
            material=materials["bell_dark"],
            name=f"{label}_axis_cheek_{side_name}", material_class_id="metal.blackened_gunmetal",
        )
        support.visual(
            Box(strap_dims),
            origin=Origin(xyz=(side_origin[0], side_origin[1], origin[2] + strap_h * 0.5)),
            material=materials["support_dark"],
            name=f"{label}_axis_drop_{side_name}", material_class_id="metal.blackened_gunmetal",
        )
    support.visual(
        Box(roof_tie_dims),
        origin=Origin(xyz=(origin[0], origin[1], anchor_z)),
        material=materials["support_dark"],
        name=f"{label}_axis_roof_tie", material_class_id=("wood.walnut_dark" if r.support_style in {"octagonal_rooftop_cupola", "raked_timber_cote", "gothic_masonry_belfry", "japanese_post_beam_pavilion"} else "metal.blackened_gunmetal"),
    )


def _build_bell_joints(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    support: SupportBuild,
    materials: dict[str, object],
    bells: list[tuple[Part, float]],
) -> None:
    for i, (bell, offset) in enumerate(bells):
        origin = _bell_joint_origin(r, offset)
        joint_name = "bell_swing" if r.bell_count == 1 else f"bell_{i}_swing"
        _add_bell_bearing_hardware(
            support.part,
            r,
            materials,
            origin=origin,
            index=i,
        )
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent=support.part,
            child=bell,
            origin=Origin(xyz=origin),
            axis=r.axis_vector,
            motion_limits=MotionLimits(
                effort=600.0,
                velocity=1.2,
                lower=-r.swing_upper,
                upper=r.swing_upper,
            ),
        )


# adopted: S3, S4
def _build_internal_clapper(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
    *,
    bell: Part,
    index: int,
) -> Part:
    name = "clapper" if r.bell_count == 1 else f"clapper_{index}"
    clapper = model.part(name)
    pivot_drop = _clapper_pivot_drop(r)
    stem_len = r.bell_radius * (0.55 if r.bell_style == "cupola_cast" else 0.84)
    clapper.visual(
        Cylinder(radius=r.bell_radius * 0.035, length=r.bell_radius * 0.34),
        origin=Origin(rpy=_axis_rpy(r.swing_axis)),
        material=materials["bell_dark"],
        name="clapper_pin", material_class_id="metal.blackened_gunmetal",
    )
    clapper.visual(
        Cylinder(radius=r.bell_radius * 0.040, length=stem_len),
        origin=Origin(xyz=(0.0, 0.0, -stem_len * 0.5)),
        material=materials["bell_dark"],
        name="clapper_stem", material_class_id="metal.blackened_gunmetal",
    )
    clapper.visual(
        Sphere(radius=r.bell_radius * 0.16),
        origin=Origin(xyz=(0.0, 0.0, -(stem_len + r.bell_radius * 0.09))),
        material=materials["bell_dark"],
        name="clapper_bob", material_class_id="metal.blackened_gunmetal",
    )
    clapper.inertial = Inertial.from_geometry(
        Cylinder(radius=r.bell_radius * 0.12, length=r.bell_radius),
        mass=8.0,
        origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.50)),
    )
    model.articulation(
        f"{name}_swing",
        ArticulationType.REVOLUTE,
        parent=bell,
        child=clapper,
        origin=Origin(xyz=(0.0, 0.0, -pivot_drop)),
        axis=r.axis_vector,
        motion_limits=MotionLimits(
            effort=60.0,
            velocity=1.4,
            lower=-r.clapper_upper,
            upper=r.clapper_upper,
        ),
    )
    return clapper


# adopted: S6
def _striker_side_offset(r: ResolvedBellTowerWithSwingingBellConfig) -> float:
    if r.support_style == "gothic_masonry_belfry":
        # The belfry bell-frame crossbeams fill |transverse| 0.56w..0.66w at
        # pivot height, so hang the striker outboard of them: clear the
        # crossbeam outer face by the deepest striker element (the 0.21r yoke)
        # plus the log's inward sweep (1.05r pendulum) at the striker limit.
        return -(
            r.frame_width * 0.66
            + r.bell_radius * (0.21 + 1.05 * math.sin(r.striker_upper))
            + 0.025
        )
    return -r.frame_width * 0.62


# adopted: S6
def _build_external_striker(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
    *,
    support: SupportBuild,
) -> Part:
    striker = model.part("striker")
    side_offset = _striker_side_offset(r)
    side_origin = _offset_along(
        (0.0, 0.0, r.pivot_z), r.transverse_axis_vector, side_offset
    )
    bridge_center = _offset_along(
        (0.0, 0.0, r.pivot_z),
        r.transverse_axis_vector,
        side_offset + r.frame_width * 0.09,
    )
    if r.swing_axis == "y":
        bridge_dims = (r.frame_width * 0.24, r.bell_radius * 0.13, r.bell_radius * 0.16)
    else:
        bridge_dims = (r.bell_radius * 0.13, r.frame_width * 0.24, r.bell_radius * 0.16)
    support.part.visual(
        Box(bridge_dims),
        origin=Origin(xyz=bridge_center),
        material=materials["bell_dark"],
        name="striker_bracket_bridge", material_class_id="metal.blackened_gunmetal",
    )
    support.part.visual(
        Box((r.bell_radius * 0.20, r.bell_radius * 0.16, r.bell_radius * 0.42)),
        origin=Origin(xyz=side_origin),
        material=materials["bell_dark"],
        name="striker_pivot_bracket", material_class_id="metal.blackened_gunmetal",
    )
    support.part.visual(
        Cylinder(radius=r.bell_radius * 0.055, length=r.bell_radius * 0.36),
        origin=Origin(xyz=side_origin, rpy=_axis_rpy(r.swing_axis)),
        material=materials["bell_dark"],
        name="striker_pivot_pin", material_class_id="metal.blackened_gunmetal",
    )
    striker.visual(
        Box((r.bell_radius * 0.18, r.bell_radius * 0.12, r.bell_radius * 0.78)),
        origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.35)),
        material=materials["wood"],
        name="striker_hanger", material_class_id="wood.natural_generic",
    )
    striker.visual(
        Box((r.bell_radius * 0.28, r.bell_radius * 0.42, r.bell_radius * 0.16)),
        origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.82)),
        material=materials["bell_dark"],
        name="striker_yoke", material_class_id="metal.blackened_gunmetal",
    )
    striker.visual(
        Cylinder(radius=r.bell_radius * 0.18, length=r.frame_width * 0.66),
        origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 1.05), rpy=_axis_rpy(r.swing_axis)),
        material=materials["wood"],
        name="striker_log", material_class_id="wood.natural_generic",
    )
    striker.visual(
        Cylinder(radius=r.bell_radius * 0.12, length=r.bell_radius * 0.28),
        origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 1.05), rpy=_axis_rpy(r.swing_axis)),
        material=materials["bell_dark"],
        name="striker_band", material_class_id="metal.blackened_gunmetal",
    )
    striker.inertial = Inertial.from_geometry(
        Box((r.bell_radius * 0.60, r.frame_width * 0.72, r.bell_radius * 1.40)),
        mass=55.0,
        origin=Origin(xyz=(0.0, 0.0, -r.bell_radius * 0.72)),
    )
    model.articulation(
        "striker_swing",
        ArticulationType.REVOLUTE,
        parent=support.part,
        child=striker,
        origin=Origin(xyz=side_origin),
        axis=_vec_scale(r.axis_vector, -1.0),
        motion_limits=MotionLimits(
            effort=220.0,
            velocity=1.0,
            lower=-r.striker_upper,
            upper=r.striker_upper,
        ),
    )
    return striker


# adopted: S5
def _build_guide_wheel(
    model: ArticulatedObject,
    r: ResolvedBellTowerWithSwingingBellConfig,
    materials: dict[str, object],
    *,
    support: SupportBuild,
) -> Part:
    wheel = model.part("guide_wheel")
    wheel_radius = max(0.07, r.bell_radius * 0.38)
    wheel.visual(
        _mesh(model, _pulley_geometry(wheel_radius), "bell_tower_guide_wheel"),
        material=materials["bell_dark"],
        name="pulley_sheave", material_class_id="metal.cast_iron_bare",
    )
    wheel.visual(
        Cylinder(radius=wheel_radius * 0.72, length=wheel_radius * 0.28),
        origin=Origin(rpy=_cyl_x()),
        material=materials["trim"],
        name="pulley_hub", material_class_id="metal.brushed_silver",
    )
    wheel.visual(
        Box((wheel_radius * 2.02, wheel_radius * 0.10, wheel_radius * 0.10)),
        origin=Origin(),
        material=materials["trim"],
        name="pulley_spoke_x", material_class_id="metal.brushed_silver",
    )
    wheel.visual(
        Box((wheel_radius * 0.10, wheel_radius * 2.02, wheel_radius * 0.10)),
        origin=Origin(),
        material=materials["trim"],
        name="pulley_spoke_y", material_class_id="metal.brushed_silver",
    )
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=wheel_radius, length=wheel_radius * 0.30),
        mass=8.0,
        origin=Origin(),
    )
    wheel_origin = (0.0, -r.frame_width * 0.86, max(0.22, r.tower_height * 0.20))
    bridge_y = -r.frame_width * 0.43
    support.part.visual(
        Box((wheel_radius * 0.55, r.frame_width * 1.80, wheel_radius * 0.34)),
        origin=Origin(xyz=(0.0, bridge_y, wheel_origin[2])),
        material=materials["bell_dark"],
        name="pulley_wall_bridge", material_class_id="metal.blackened_gunmetal",
    )
    support.part.visual(
        Box((wheel_radius * 1.55, wheel_radius * 0.16, wheel_radius * 1.20)),
        origin=Origin(xyz=(wheel_origin[0], wheel_origin[1], wheel_origin[2])),
        material=materials["bell_dark"],
        name="pulley_backplate", material_class_id="metal.blackened_gunmetal",
    )
    support.part.visual(
        Cylinder(radius=wheel_radius * 0.12, length=wheel_radius * 0.60),
        origin=Origin(xyz=wheel_origin, rpy=_cyl_x()),
        material=materials["trim"],
        name="pulley_axle_pin", material_class_id="metal.brushed_silver",
    )
    model.articulation(
        "guide_wheel_spin",
        ArticulationType.CONTINUOUS,
        parent=support.part,
        child=wheel,
        origin=Origin(xyz=wheel_origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=4.0),
    )
    return wheel


def build_bell_tower_with_swinging_bell(
    config: BellTowerWithSwingingBellConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or BellTowerWithSwingingBellConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    materials = _register_materials(model, r.palette)
    support = _build_support(model, r, materials)

    bells: list[tuple[Part, float]] = []
    for i, offset in enumerate(_bell_offsets(r)):
        bell = _build_bell_part(model, r, materials, index=i, offset=offset)
        bells.append((bell, offset))
    _build_bell_joints(model, r, support, materials, bells)

    if r.secondary_motion == "internal_clapper_revolute":
        for i, (bell, _offset) in enumerate(bells):
            _build_internal_clapper(model, r, materials, bell=bell, index=i)
    elif r.secondary_motion == "external_striker":
        _build_external_striker(model, r, materials, support=support)
    elif r.secondary_motion == "guide_wheel":
        _build_guide_wheel(model, r, materials, support=support)
    return model


def build_seeded_bell_tower_with_swinging_bell(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_bell_tower_with_swinging_bell(config_from_seed(seed), assets=assets)


def slot_choices_for_config(
    config: BellTowerWithSwingingBellConfig,
) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("support_structure", r.support_style),
        (
            "bell_and_yoke",
            {
                "bronze_yoke": "bronze_bell_with_steel_yoke",
                "arched_hanger": "arched_hanger_bell",
                "cupola_cast": "cupola_cast_bell",
                "bonsho": "bonsho_suspended_bell",
            }[r.bell_style],
        ),
        (
            "secondary_motion",
            {
                "none": "none",
                "internal_clapper_revolute": "internal_clapper_revolute",
                "fixed_clapper": "fixed_clapper_baked_visual",
                "external_striker": "external_striker_revolute",
                "guide_wheel": "guide_wheel_continuous",
            }[r.secondary_motion],
        ),
        ("bell_multiplicity", f"{r.bell_count}_bell"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    parts = {p.name for p in model.parts}
    support_name = next((name for name in parts if name.startswith("support_")), None)
    allow_disconnected = getattr(ctx, "allow_disconnected_islands", None)
    for part_name in parts:
        if part_name.startswith("support_") and callable(allow_disconnected):
            allow_disconnected(
                model.get_part(part_name),
                reason=(
                    "bell tower support is a rigid multi-piece frame/tower/cupola with "
                    "posts, braces, roof trim, louvers, and bearing hardware"
                ),
            )
        if part_name.startswith("bell") and callable(allow_disconnected):
            allow_disconnected(
                model.get_part(part_name),
                reason=(
                    "bell assembly is a rigid multi-piece yoke, shell, trunnion, "
                    "crown, and optional fixed clapper construction"
                ),
            )
        if part_name == "guide_wheel" and callable(allow_disconnected):
            allow_disconnected(
                model.get_part(part_name),
                reason="guide wheel is a sheave plus hub rigid subassembly",
            )
    if support_name is None:
        return
    support = model.get_part(support_name)
    for part_name in parts:
        if part_name.startswith("bell"):
            bell = model.get_part(part_name)
            parent_elements = (
                "pivot_shaft",
                "front_pivot_plate",
                "back_pivot_plate",
                "bell_crown_pin",
                "bell_bearing_0",
                "bell_bearing_1",
                "bell_bearing_drop_strap_0",
                "bell_bearing_drop_strap_1",
                "pivot_bearing_pin",
                "bell_bearing_pin",
                "continuous_pivot_tie",
                "central_bell_frame_tie_x",
                "central_bell_frame_tie_y",
                "top_beam",
                "front_top_rail",
                "back_top_rail",
                "left_top_rail",
                "right_top_rail",
                "left_pivot_ear",
                "right_pivot_ear",
                "left_pivot_ear_roof_strap",
                "right_pivot_ear_roof_strap",
                "front_bearing_block",
                "rear_bearing_block",
                "bell_axle_crossbar",
                "bell_hanger_front",
                "bell_hanger_back",
                "bell_hanger_drop_front",
                "bell_hanger_drop_back",
                "bell_hanger_front_right",
                "bell_hanger_back_right",
                "bell_axis_cheek_a",
                "bell_axis_cheek_b",
                "bell_axis_drop_a",
                "bell_axis_drop_b",
            )
            if part_name == "bell":
                parent_elements += (
                    "bell_bearing_pin",
                    "bell_axis_cheek_a",
                    "bell_axis_cheek_b",
                    "bell_axis_drop_a",
                    "bell_axis_drop_b",
                )
            else:
                suffix = part_name.split("_", 1)[1]
                parent_elements += (
                    f"bell_{suffix}_bearing_pin",
                    f"bell_{suffix}_axis_cheek_a",
                    f"bell_{suffix}_axis_cheek_b",
                    f"bell_{suffix}_axis_drop_a",
                    f"bell_{suffix}_axis_drop_b",
                )
            child_pivot_elements = (
                "pivot_journal",
                "outer_yoke_boss",
                "inner_yoke_boss",
                "left_trunnion",
                "right_trunnion",
                "bell_crown_cap",
                "crown_block",
                "headstock",
                "yoke_crossbar",
                "cupola_trunnion_crown_bridge",
                "bell_shell",
                "crown_to_shell_neck",
            )
            for parent_elem in parent_elements:
                for child_elem in child_pivot_elements:
                    try:
                        ctx.allow_overlap(
                            support,
                            bell,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="captured bell pivot hardware intentionally interlocks at the hinge line",
                        )
                    except Exception:
                        pass
        if part_name.startswith("clapper"):
            clapper = model.get_part(part_name)
            for bell_name in [name for name in parts if name.startswith("bell")]:
                bell = model.get_part(bell_name)
                for bell_elem, clapper_elem, reason in (
                    (
                        "bell_shell",
                        "clapper_bob",
                        "clapper bob sits inside bell shell in the closed pose",
                    ),
                    (
                        "clapper_pivot_socket",
                        "clapper_pin",
                        "captured clapper pin passes through socket under the bell crown",
                    ),
                    (
                        "clapper_pivot_socket",
                        "clapper_stem",
                        "upper clapper stem starts inside the captured socket",
                    ),
                    (
                        "crown_to_shell_neck",
                        "clapper_stem",
                        "clapper stem runs through the bell crown neck before hanging below",
                    ),
                    (
                        "crown_to_shell_neck",
                        "clapper_pin",
                        "captured clapper pin passes through the reinforced crown neck",
                    ),
                ):
                    try:
                        ctx.allow_overlap(
                            bell,
                            clapper,
                            elem_a=bell_elem,
                            elem_b=clapper_elem,
                            reason=reason,
                        )
                    except Exception:
                        pass
        if part_name == "striker":
            striker = model.get_part("striker")
            for parent_elem in ("pivot_pin", "pivot_cheek_front", "pivot_cheek_back"):
                try:
                    ctx.allow_overlap(
                        support,
                        striker,
                        elem_a=parent_elem,
                        elem_b="striker_hanger",
                        reason="external striker hanger is captured by post-side pivot hardware",
                    )
                except Exception:
                    pass
            for parent_elem in (
                "striker_pivot_pin",
                "striker_pivot_bracket",
                "striker_bracket_bridge",
            ):
                try:
                    ctx.allow_overlap(
                        support,
                        striker,
                        elem_a=parent_elem,
                        elem_b="striker_hanger",
                        reason="external striker hanger pivots inside the explicit bracket",
                    )
                except Exception:
                    pass
        if part_name == "guide_wheel":
            wheel = model.get_part("guide_wheel")
            for parent_elem, child_elem in (
                ("pulley_axle_pin", "pulley_hub"),
                ("pulley_axle_pin", "pulley_spoke_x"),
                ("pulley_axle_pin", "pulley_spoke_y"),
                ("pulley_backplate", "pulley_sheave"),
                ("pulley_backplate", "pulley_hub"),
                ("pulley_backplate", "pulley_spoke_x"),
                ("pulley_backplate", "pulley_spoke_y"),
                ("pulley_wall_bridge", "pulley_sheave"),
                ("pulley_wall_bridge", "pulley_hub"),
                ("pulley_wall_bridge", "pulley_spoke_x"),
                ("pulley_wall_bridge", "pulley_spoke_y"),
            ):
                try:
                    ctx.allow_overlap(
                        support,
                        wheel,
                        elem_a=parent_elem,
                        elem_b=child_elem,
                        reason="guide wheel hub and sheave are captured in the tower pulley bracket",
                    )
                except Exception:
                    pass


def run_bell_tower_with_swinging_bell_tests(
    object_model: ArticulatedObject,
    config: BellTowerWithSwingingBellConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.030)
    ctx.fail_if_joint_mating_has_gap()

    parts = {p.name for p in object_model.parts}
    ctx.check("support_present", any(name.startswith("support_") for name in parts))
    ctx.check("bell_present", any(name.startswith("bell") for name in parts))
    swing_joints = [
        j
        for j in object_model.articulations
        if j.articulation_type == ArticulationType.REVOLUTE
        and "bell" in j.name
        and "swing" in j.name
    ]
    ctx.check("main_bell_swing_present", len(swing_joints) >= 1)
    ctx.check(
        "bell_count_matches",
        len(swing_joints) == r.bell_count,
        details=f"expected {r.bell_count} bell swing joints, got {len(swing_joints)}",
    )
    for joint in swing_joints:
        axis = tuple(round(float(v), 6) for v in joint.axis)
        horizontal = axis in (
            (1.0, 0.0, 0.0),
            (-1.0, -0.0, -0.0),
            (0.0, 1.0, 0.0),
            (-0.0, -1.0, -0.0),
        )
        ctx.check(f"{joint.name}_axis_horizontal", horizontal, details=f"axis={axis}")
    if r.secondary_motion == "internal_clapper_revolute":
        ctx.check("clapper_parts_present", any(name.startswith("clapper") for name in parts))
    if r.secondary_motion == "external_striker":
        ctx.check("striker_present", "striker" in parts)
    if r.secondary_motion == "guide_wheel":
        continuous = [
            j
            for j in object_model.articulations
            if j.articulation_type == ArticulationType.CONTINUOUS
        ]
        ctx.check("guide_wheel_continuous", len(continuous) >= 1)
    return ctx.report()


__all__ = [
    "BellTowerWithSwingingBellConfig",
    "ResolvedBellTowerWithSwingingBellConfig",
    "build_bell_tower_with_swinging_bell",
    "build_seeded_bell_tower_with_swinging_bell",
    "config_from_seed",
    "resolve_config",
    "run_bell_tower_with_swinging_bell_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
