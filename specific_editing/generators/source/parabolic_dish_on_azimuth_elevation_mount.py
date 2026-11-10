# SPDX-License-Identifier: Apache-2.0

"""Parabolic dish on azimuth/elevation mount procedural template.

Implements ``articraft_template_authoring/specs_modular_v1/
parabolic_dish_on_azimuth_elevation_mount.md``.

The template follows the spec's linear chain:

* Slot A ``root_support`` emits the grounded pedestal/roof/tripod/mast visual.
* Slot B ``azimuth_stage`` emits a yawing yoke/fork with elevation sockets.
* Slot C ``dish_reflector_assembly`` emits a concave parabolic reflector with
  rim, rear ribs, trunnions, feed boom, and horn.
* Slot D ``auxiliary_mechanism`` is an optional real articulated child
  (rear_cover / instrument_hatch / side_crank / transport_leg), sampled with
  compatibility gating.

Identity invariant: every seed has a visible concave dish reflector, feed
support, root support, ``azimuth_spin`` around vertical Z, and
``elevation_tilt`` around a horizontal hinge line.

Geometry policy: the azimuth part owns the yoke sockets at the elevation hinge
line; the dish owns matching trunnion caps at the same line. The reflector,
back frame, feed boom, and horn are all visuals of the dish assembly, so the
antenna identity moves as one child of the elevation joint.

Adopted source mapping:
S1 rec_parabolic_dish_on_azimuth_elevation_mount_0004:
   canonical pedestal + azimuth yoke + reflector chain.
S2 rec_parabolic_dish_on_azimuth_elevation_mount_1a992a547a104469adb6a6b286f64e1d:
   roof mount, compact fork, feed boom.
S3 rec_parabolic_dish_on_azimuth_elevation_mount_3ebbc287998444179c7080d3a2807954:
   tripod support and ribbed portable dish.
S4 rec_parabolic_dish_on_azimuth_elevation_mount_49566120c578436cb5061a6f0e715707:
   instrument yoke, rear braces, side crank/instrument box cues.
S5 rec_parabolic_dish_on_azimuth_elevation_mount_b46d320f8c5e484d8e911539ce34497d:
   mast fork, parabolic spokes, annular support.
S6 rec_parabolic_dish_on_azimuth_elevation_mount_ff95ab246ac04d8d92e07ad4c874a686:
   heavy base, yoke towers, rear cover/electronics cues.
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
    LatheGeometry,
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


RootStyle = Literal[
    "pedestal",
    "roof_mount",
    "tripod",
    "mast",
    "heavy_service_base",
    "mobile_skid_base",
    "wall_mast_mount",
]
AzimuthStageStyle = Literal[
    "dual_yoke",
    "compact_fork",
    "tripod_head",
    "mast_fork",
    "instrument_yoke",
]
ReflectorStyle = Literal[
    "lathe_feed",
    "roof_feed_boom",
    "portable_ribbed",
    "instrumented_box",
    "cadquery_spoked",
]
AuxiliaryMechanism = Literal[
    "none",
    "instrument_hatch",
    "rear_cover",
    "side_crank",
    "transport_leg",
]
FeedStyle = Literal[
    "single_boom",
    "dual_strut",
    "tripod_feed",
    "horn_only",
    "none_minimal",
]
BackFrameStyle = Literal[
    "simple_spine",
    "ribbed",
    "truss",
    "instrument_box",
    "covered",
]
AzimuthJointType = Literal["continuous", "revolute_limited"]
MaterialStyle = Literal[
    "white_telecom",
    "galvanized_gray",
    "desert_roof",
    "portable_black",
    "observatory_blue",
]


ROOT_STYLES: tuple[RootStyle, ...] = (
    "pedestal",
    "roof_mount",
    "tripod",
    "mast",
    "heavy_service_base",
    "mobile_skid_base",
    "wall_mast_mount",
)
AZIMUTH_STAGE_STYLES: tuple[AzimuthStageStyle, ...] = (
    "dual_yoke",
    "compact_fork",
    "tripod_head",
    "mast_fork",
    "instrument_yoke",
)
REFLECTOR_STYLES: tuple[ReflectorStyle, ...] = (
    "lathe_feed",
    "roof_feed_boom",
    "portable_ribbed",
    "instrumented_box",
    "cadquery_spoked",
)
AUXILIARY_MECHANISMS: tuple[AuxiliaryMechanism, ...] = (
    "none",
    "instrument_hatch",
    "rear_cover",
    "side_crank",
    "transport_leg",
)
FEED_STYLES: tuple[FeedStyle, ...] = (
    "single_boom",
    "dual_strut",
    "tripod_feed",
    "horn_only",
    "none_minimal",
)
BACK_FRAME_STYLES: tuple[BackFrameStyle, ...] = (
    "simple_spine",
    "ribbed",
    "truss",
    "instrument_box",
    "covered",
)
AZIMUTH_JOINT_TYPES: tuple[AzimuthJointType, ...] = (
    "continuous",
    "revolute_limited",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "white_telecom",
    "galvanized_gray",
    "desert_roof",
    "portable_black",
    "observatory_blue",
)


SOURCE_INDEX = {
    "S1": (
        "data/records/rec_parabolic_dish_on_azimuth_elevation_mount_0004/"
        "revisions/rev_000001/model.py:L30-L335"
    ),
    "S2": (
        "data/records/rec_parabolic_dish_on_azimuth_elevation_mount_"
        "1a992a547a104469adb6a6b286f64e1d/revisions/rev_000001/"
        "model.py:L24-L128,L146-L351"
    ),
    "S3": (
        "data/records/rec_parabolic_dish_on_azimuth_elevation_mount_"
        "3ebbc287998444179c7080d3a2807954/revisions/rev_000001/"
        "model.py:L21-L106,L115-L269"
    ),
    "S4": (
        "data/records/rec_parabolic_dish_on_azimuth_elevation_mount_"
        "49566120c578436cb5061a6f0e715707/revisions/rev_000001/"
        "model.py:L27-L38,L177-L446"
    ),
    "S5": (
        "data/records/rec_parabolic_dish_on_azimuth_elevation_mount_"
        "b46d320f8c5e484d8e911539ce34497d/revisions/rev_000001/"
        "model.py:L22-L120,L129-L342"
    ),
    "S6": (
        "data/records/rec_parabolic_dish_on_azimuth_elevation_mount_"
        "ff95ab246ac04d8d92e07ad4c874a686/revisions/rev_000001/"
        "model.py:L21-L82,L93-L201"
    ),
}


PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_telecom": {
        "support": (0.74, 0.76, 0.74, 1.0),
        "support_dark": (0.34, 0.36, 0.36, 1.0),
        "reflector": (0.86, 0.88, 0.84, 1.0),
        "reflector_inner": (0.92, 0.94, 0.90, 1.0),
        "rim": (0.66, 0.68, 0.66, 1.0),
        "feed": (0.30, 0.32, 0.34, 1.0),
        "accent": (0.95, 0.72, 0.14, 1.0),
        "rubber": (0.045, 0.045, 0.050, 1.0),
    },
    "galvanized_gray": {
        "support": (0.54, 0.56, 0.58, 1.0),
        "support_dark": (0.22, 0.23, 0.24, 1.0),
        "reflector": (0.70, 0.72, 0.72, 1.0),
        "reflector_inner": (0.80, 0.82, 0.82, 1.0),
        "rim": (0.48, 0.50, 0.52, 1.0),
        "feed": (0.20, 0.22, 0.24, 1.0),
        "accent": (0.74, 0.78, 0.82, 1.0),
        "rubber": (0.035, 0.035, 0.038, 1.0),
    },
    "desert_roof": {
        "support": (0.62, 0.52, 0.38, 1.0),
        "support_dark": (0.30, 0.24, 0.16, 1.0),
        "reflector": (0.78, 0.72, 0.60, 1.0),
        "reflector_inner": (0.88, 0.82, 0.68, 1.0),
        "rim": (0.52, 0.44, 0.30, 1.0),
        "feed": (0.24, 0.22, 0.18, 1.0),
        "accent": (0.82, 0.48, 0.16, 1.0),
        "rubber": (0.055, 0.048, 0.040, 1.0),
    },
    "portable_black": {
        "support": (0.060, 0.064, 0.070, 1.0),
        "support_dark": (0.018, 0.020, 0.024, 1.0),
        "reflector": (0.16, 0.17, 0.18, 1.0),
        "reflector_inner": (0.22, 0.23, 0.24, 1.0),
        "rim": (0.09, 0.10, 0.11, 1.0),
        "feed": (0.78, 0.78, 0.74, 1.0),
        "accent": (0.12, 0.50, 0.82, 1.0),
        "rubber": (0.012, 0.012, 0.014, 1.0),
    },
    "observatory_blue": {
        "support": (0.24, 0.34, 0.46, 1.0),
        "support_dark": (0.08, 0.12, 0.18, 1.0),
        "reflector": (0.82, 0.86, 0.88, 1.0),
        "reflector_inner": (0.90, 0.94, 0.96, 1.0),
        "rim": (0.36, 0.44, 0.54, 1.0),
        "feed": (0.16, 0.20, 0.24, 1.0),
        "accent": (0.94, 0.86, 0.34, 1.0),
        "rubber": (0.026, 0.028, 0.032, 1.0),
    },
}


@dataclass(frozen=True)
class ParabolicDishConfig:
    root_style: RootStyle = "pedestal"
    azimuth_stage_style: AzimuthStageStyle = "dual_yoke"
    reflector_style: ReflectorStyle = "lathe_feed"
    auxiliary_mechanism: AuxiliaryMechanism = "none"
    feed_style: FeedStyle = "single_boom"
    back_frame_style: BackFrameStyle = "simple_spine"
    azimuth_joint_type: AzimuthJointType = "continuous"
    material_style: MaterialStyle = "white_telecom"
    feed_strut_count: int = 1
    rear_rib_count: int = 6
    back_ring_count: int = 1
    support_leg_count: int = 3
    dish_radius: float = 0.62
    dish_depth: float = 0.22
    azimuth_height: float = 0.72
    elevation_lower: float = -0.25
    elevation_upper: float = 1.15
    name: str = "reference_parabolic_dish_on_azimuth_elevation_mount"
    palette: dict[str, tuple[float, float, float, float]] | None = None


@dataclass(frozen=True)
class ResolvedParabolicDishConfig:
    root_style: RootStyle
    azimuth_stage_style: AzimuthStageStyle
    reflector_style: ReflectorStyle
    auxiliary_mechanism: AuxiliaryMechanism
    feed_style: FeedStyle
    back_frame_style: BackFrameStyle
    azimuth_joint_type: AzimuthJointType
    material_style: MaterialStyle
    feed_strut_count: int
    rear_rib_count: int
    back_ring_count: int
    support_leg_count: int
    dish_radius: float
    dish_depth: float
    azimuth_height: float
    elevation_lower: float
    elevation_upper: float
    yoke_span: float
    yoke_cheek_height: float
    yoke_thickness: float
    bearing_radius: float
    base_radius: float
    base_depth: float
    feed_length: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


@dataclass(frozen=True)
class ChainAnchors:
    root: Part
    azimuth: Part
    hinge_z: float
    yoke_span: float
    bearing_radius: float


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


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


def _register_materials(
    model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]]
):
    return {name: model.material(f"dish_{name}", rgba=rgba) for name, rgba in palette.items()}


def _mesh_for_model(model: ArticulatedObject, geometry: object, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


def _add_torus(
    model: ArticulatedObject,
    part: Part,
    *,
    name: str,
    radius: float,
    tube: float,
    material: object,
    origin: Origin | None = None,
    radial_segments: int = 14,
    tubular_segments: int = 64,
) -> None:
    part.visual(
        _mesh_for_model(
            model,
            TorusGeometry(
                radius=radius,
                tube=tube,
                radial_segments=radial_segments,
                tubular_segments=tubular_segments,
            ),
            name,
        ),
        origin=origin or Origin(),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _reflector_shell_geometry(radius: float, depth: float, wall: float):
    samples = 12
    outer: list[tuple[float, float]] = []
    inner: list[tuple[float, float]] = []
    for i in range(samples + 1):
        u = i / samples
        rr = max(radius * 0.10, radius * u)
        z = depth * (u * u)
        outer.append((rr, z))
        inner.append((max(radius * 0.08, rr - wall), max(0.0, z - wall)))
    return LatheGeometry.from_shell_profiles(
        outer,
        inner,
        segments=80,
        start_cap="round",
        end_cap="round",
        lip_samples=5,
    ).rotate_x(math.pi / 2.0)


# Compatibility gating: which azimuth stages physically fit each root, and
# (root-dependent) sensible mount heights. Procedural sampling draws from these
# compatible subsets — there is no curated/modulo seed table.
ROOT_AZIMUTH_COMPAT: dict[RootStyle, tuple[AzimuthStageStyle, ...]] = {
    "pedestal": ("dual_yoke", "compact_fork", "instrument_yoke"),
    "roof_mount": ("compact_fork", "dual_yoke"),
    "tripod": ("tripod_head", "dual_yoke"),
    "mast": ("mast_fork", "compact_fork"),
    "heavy_service_base": ("dual_yoke", "instrument_yoke"),
    "mobile_skid_base": ("compact_fork", "dual_yoke"),
    "wall_mast_mount": ("mast_fork", "compact_fork"),
}
ROOT_HEIGHT_RANGE: dict[RootStyle, tuple[float, float]] = {
    "pedestal": (0.62, 1.05),
    "roof_mount": (0.40, 0.62),
    "tripod": (0.50, 0.78),
    "mast": (0.70, 1.30),
    "heavy_service_base": (0.66, 1.15),
    "mobile_skid_base": (0.34, 0.56),
    "wall_mast_mount": (0.50, 0.92),
}


def _sample_feed_strut_count(feed: FeedStyle, rng: random.Random) -> int:
    """Feed-support multiplicity gated by the feed family: dual_strut spans a
    real 2/3/4 strut count (3/4 = tri-/quadrupod), tripod is fixed 3, the boom
    families are 1, and none_minimal is 0."""
    if feed == "none_minimal":
        return 0
    if feed == "dual_strut":
        return rng.choice((2, 3, 4))
    if feed == "tripod_feed":
        return 3
    return 1


def config_from_seed(seed: int) -> ParabolicDishConfig:
    """Deterministic procedural sampling (procedural-first; seed=0 is not
    special). Each slot is drawn from the compatible candidate subset."""
    rng = random.Random(seed)
    root: RootStyle = rng.choice(ROOT_STYLES)
    az: AzimuthStageStyle = rng.choice(ROOT_AZIMUTH_COMPAT[root])
    reflector: ReflectorStyle = rng.choice(REFLECTOR_STYLES)
    feed: FeedStyle = rng.choice(FEED_STYLES)
    back: BackFrameStyle = rng.choice(BACK_FRAME_STYLES)
    material: MaterialStyle = rng.choice(MATERIAL_STYLES)
    az_joint: AzimuthJointType = rng.choice(AZIMUTH_JOINT_TYPES)
    # Auxiliary gating: rear_cover needs the dish rear electronics box (covered
    # / instrument_box back). instrument_hatch + side_crank are self-contained.
    aux_choices: list[AuxiliaryMechanism] = ["none", "side_crank"]
    if back in ("instrument_box", "covered"):
        # rear cover / instrument hatch mount on the dish rear electronics box.
        aux_choices += ["rear_cover", "instrument_hatch"]
    if root == "mobile_skid_base":
        # fold-down transport leg requires the skid's leg hinge bridge.
        aux_choices.append("transport_leg")
    aux: AuxiliaryMechanism = rng.choice(aux_choices)
    # Multiplicity: feed struts, rear ribs, rear stiffener rings, and (tripod)
    # splayed support legs.
    feed_strut_count = _sample_feed_strut_count(feed, rng)
    rear_rib_count = rng.choice((4, 6, 8, 12))
    back_ring_count = rng.choice((0, 1, 2, 3))
    support_leg_count = rng.choice((3, 4)) if root == "tripod" else 3
    h_lo, h_hi = ROOT_HEIGHT_RANGE[root]
    return ParabolicDishConfig(
        root_style=root,
        azimuth_stage_style=az,
        reflector_style=reflector,
        auxiliary_mechanism=aux,
        feed_style=feed,
        back_frame_style=back,
        azimuth_joint_type=az_joint,
        material_style=material,
        feed_strut_count=feed_strut_count,
        rear_rib_count=rear_rib_count,
        back_ring_count=back_ring_count,
        support_leg_count=support_leg_count,
        dish_radius=round(rng.uniform(0.40, 0.78), 3),
        dish_depth=round(rng.uniform(0.14, 0.30), 3),
        azimuth_height=round(rng.uniform(h_lo, h_hi), 3),
        elevation_lower=round(rng.uniform(-0.22, -0.12), 3),
        elevation_upper=round(rng.uniform(0.85, 1.05), 3),
        name=f"seeded_parabolic_dish_on_azimuth_elevation_mount_{seed}",
    )


def resolve_config(config: ParabolicDishConfig) -> ResolvedParabolicDishConfig:
    root = _require(config.root_style, ROOT_STYLES, field_name="root_style")
    az = _require(
        config.azimuth_stage_style,
        AZIMUTH_STAGE_STYLES,
        field_name="azimuth_stage_style",
    )
    reflector = _require(config.reflector_style, REFLECTOR_STYLES, field_name="reflector_style")
    aux = _require(
        config.auxiliary_mechanism,
        AUXILIARY_MECHANISMS,
        field_name="auxiliary_mechanism",
    )
    feed = _require(config.feed_style, FEED_STYLES, field_name="feed_style")
    back = _require(config.back_frame_style, BACK_FRAME_STYLES, field_name="back_frame_style")
    az_joint = _require(
        config.azimuth_joint_type,
        AZIMUTH_JOINT_TYPES,
        field_name="azimuth_joint_type",
    )
    material = _require(config.material_style, MATERIAL_STYLES, field_name="material_style")

    radius = _clamp(config.dish_radius, 0.35, 1.05)
    # short compact/tripod yokes give the dish less swing clearance — cap radius
    # so the reflector clears the fork through the full elevation range.
    if az in ("compact_fork", "tripod_head"):
        radius = min(radius, 0.60)
    depth = _clamp(config.dish_depth, 0.10, 0.42)
    height = _clamp(config.azimuth_height, 0.35, 1.35)
    yoke_span = radius * 2.32
    yoke_cheek_height = radius * (2.35 if az in ("compact_fork", "tripod_head") else 2.50)
    yoke_thickness = max(0.030, radius * 0.065)
    bearing_radius = max(0.035, radius * 0.085)
    base_radius = max(0.18, radius * 0.46)
    base_depth = max(0.16, radius * 0.34)
    feed_length = radius * (1.18 if feed in ("single_boom", "dual_strut") else 0.98)
    if feed == "horn_only":
        feed_length = radius * 0.72
    palette = dict(PALETTES[material])
    if config.palette:
        palette.update(config.palette)

    lower = _clamp(config.elevation_lower, -0.60, 0.20)
    upper = _clamp(config.elevation_upper, 0.55, 1.35)
    if lower >= upper:
        lower, upper = -0.25, 1.15

    return ResolvedParabolicDishConfig(
        root_style=root,  # type: ignore[arg-type]
        azimuth_stage_style=az,  # type: ignore[arg-type]
        reflector_style=reflector,  # type: ignore[arg-type]
        auxiliary_mechanism=aux,  # type: ignore[arg-type]
        feed_style=feed,  # type: ignore[arg-type]
        back_frame_style=back,  # type: ignore[arg-type]
        azimuth_joint_type=az_joint,  # type: ignore[arg-type]
        material_style=material,  # type: ignore[arg-type]
        feed_strut_count=max(0, min(4, int(config.feed_strut_count))),
        rear_rib_count=max(4, min(16, int(config.rear_rib_count))),
        back_ring_count=max(0, min(3, int(config.back_ring_count))),
        support_leg_count=max(3, min(4, int(config.support_leg_count))),
        dish_radius=radius,
        dish_depth=depth,
        azimuth_height=height,
        elevation_lower=lower,
        elevation_upper=upper,
        yoke_span=yoke_span,
        yoke_cheek_height=yoke_cheek_height,
        yoke_thickness=yoke_thickness,
        bearing_radius=bearing_radius,
        base_radius=base_radius,
        base_depth=base_depth,
        feed_length=feed_length,
        name=config.name,
        palette=palette,
    )


def _decorate_pedestal_root(
    root: Part, r: ResolvedParabolicDishConfig, materials: dict[str, object]
) -> None:
    R = r.dish_radius
    root.visual(
        Cylinder(radius=r.base_radius * 1.08, length=R * 0.085),
        origin=Origin(xyz=(0.0, 0.0, R * 0.0425), rpy=_cyl_z()),
        material=materials["support_dark"],
        name="pedestal_ground_disk", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=r.base_radius * 0.72, length=R * 0.070),
        origin=Origin(xyz=(0.0, 0.0, R * 0.12), rpy=_cyl_z()),
        material=materials["support"],
        name="pedestal_raised_plinth", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.105, length=r.azimuth_height - R * 0.13),
        origin=Origin(xyz=(0.0, 0.0, (r.azimuth_height + R * 0.13) * 0.5), rpy=_cyl_z()),
        material=materials["support"],
        name="round_pedestal_column", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.17, length=R * 0.070),
        origin=Origin(xyz=(0.0, 0.0, r.azimuth_height - R * 0.035), rpy=_cyl_z()),
        material=materials["rim"],
        name="azimuth_lower_bearing_race", material_class_id="metal.stainless_matte",
    )


def _decorate_roof_root(
    root: Part, r: ResolvedParabolicDishConfig, materials: dict[str, object]
) -> None:
    R = r.dish_radius
    root.visual(
        Box((r.base_radius * 2.4, r.base_depth * 2.2, R * 0.07)),
        origin=Origin(xyz=(0.0, 0.0, R * 0.035)),
        material=materials["support_dark"],
        name="roof_mount_flat_plate", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    for i, (x, y) in enumerate(
        (
            (-r.base_radius * 0.85, -r.base_depth * 0.72),
            (r.base_radius * 0.85, -r.base_depth * 0.72),
            (-r.base_radius * 0.85, r.base_depth * 0.72),
            (r.base_radius * 0.85, r.base_depth * 0.72),
        )
    ):
        root.visual(
            Cylinder(radius=R * 0.030, length=R * 0.018),
            origin=Origin(xyz=(x, y, R * 0.078), rpy=_cyl_z()),
            material=materials["rubber"],
            name=f"roof_anchor_bolt_{i}", material_class_id="rubber.smooth_plain",
        )
    root.visual(
        Cylinder(radius=R * 0.13, length=r.azimuth_height - R * 0.07),
        origin=Origin(xyz=(0.0, 0.0, (r.azimuth_height + R * 0.07) * 0.5), rpy=_cyl_z()),
        material=materials["support"],
        name="short_roof_pedestal", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.20, length=R * 0.055),
        origin=Origin(xyz=(0.0, 0.0, r.azimuth_height - R * 0.026), rpy=_cyl_z()),
        material=materials["rim"],
        name="roof_turntable_race", material_class_id="metal.stainless_matte",
    )


def _decorate_tripod_root(
    root: Part, r: ResolvedParabolicDishConfig, materials: dict[str, object]
) -> None:
    R = r.dish_radius
    root.visual(
        Cylinder(radius=R * 0.12, length=r.azimuth_height),
        origin=Origin(xyz=(0.0, 0.0, r.azimuth_height * 0.50), rpy=_cyl_z()),
        material=materials["support"],
        name="tripod_center_post", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.19, length=R * 0.058),
        origin=Origin(xyz=(0.0, 0.0, r.azimuth_height), rpy=_cyl_z()),
        material=materials["rim"],
        name="tripod_head_bearing_race", material_class_id="metal.stainless_matte",
    )
    leg_len = r.base_radius * 1.40
    n_legs = r.support_leg_count  # 3 (tripod) or 4 (quad tower)
    for i in range(n_legs):
        angle = math.tau * i / n_legs + math.pi / 6.0
        x = math.cos(angle) * leg_len * 0.42
        y = math.sin(angle) * leg_len * 0.42
        root.visual(
            Box((R * 0.065, leg_len, R * 0.050)),
            origin=Origin(
                xyz=(x, y, R * 0.10),
                rpy=(0.24, 0.0, angle - math.pi / 2.0),
            ),
            material=materials["support_dark"],
            name=f"tripod_splayed_leg_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
        root.visual(
            Sphere(radius=R * 0.070),
            origin=Origin(
                xyz=(math.cos(angle) * leg_len * 0.84, math.sin(angle) * leg_len * 0.84, R * 0.062)
            ),
            material=materials["rubber"],
            name=f"tripod_rubber_foot_{i}", material_class_id="rubber.smooth_plain",
        )
        root.visual(
            Box((R * 0.045, leg_len * 1.72, R * 0.040)),
            origin=Origin(
                xyz=(math.cos(angle) * leg_len * 0.42, math.sin(angle) * leg_len * 0.42, R * 0.064),
                rpy=(0.0, 0.0, angle - math.pi / 2.0),
            ),
            material=materials["support_dark"],
            name=f"tripod_lower_foot_tie_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )


def _decorate_mast_root(
    root: Part, r: ResolvedParabolicDishConfig, materials: dict[str, object]
) -> None:
    R = r.dish_radius
    root.visual(
        Cylinder(radius=r.base_radius * 0.72, length=R * 0.070),
        origin=Origin(xyz=(0.0, 0.0, R * 0.035), rpy=_cyl_z()),
        material=materials["support_dark"],
        name="mast_base_flange", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.080, length=r.azimuth_height - R * 0.05),
        origin=Origin(xyz=(0.0, 0.0, (r.azimuth_height + R * 0.05) * 0.5), rpy=_cyl_z()),
        material=materials["support"],
        name="vertical_mast_tube", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    for i, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
        root.visual(
            Box((R * 0.030, R * 0.040, r.azimuth_height * 0.32)),
            origin=Origin(
                xyz=(
                    math.cos(angle) * R * 0.092,
                    math.sin(angle) * R * 0.092,
                    r.azimuth_height * 0.48,
                ),
                rpy=(0.0, 0.0, angle),
            ),
            material=materials["support_dark"],
            name=f"mast_vertical_web_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
    root.visual(
        Cylinder(radius=R * 0.16, length=R * 0.060),
        origin=Origin(xyz=(0.0, 0.0, r.azimuth_height), rpy=_cyl_z()),
        material=materials["rim"],
        name="mast_top_bearing_collar", material_class_id="metal.stainless_matte",
    )


def _decorate_heavy_root(
    root: Part, r: ResolvedParabolicDishConfig, materials: dict[str, object]
) -> None:
    R = r.dish_radius
    root.visual(
        Box((r.base_radius * 2.6, r.base_depth * 2.25, R * 0.12)),
        origin=Origin(xyz=(0.0, 0.0, R * 0.06)),
        material=materials["support_dark"],
        name="heavy_service_skid_base", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    root.visual(
        Box((r.base_radius * 1.65, r.base_depth * 1.32, R * 0.12)),
        origin=Origin(xyz=(0.0, 0.0, R * 0.18)),
        material=materials["support"],
        name="heavy_service_equipment_block", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.14, length=r.azimuth_height - R * 0.24),
        origin=Origin(xyz=(0.0, 0.0, (r.azimuth_height + R * 0.24) * 0.5), rpy=_cyl_z()),
        material=materials["support"],
        name="heavy_center_pedestal", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.24, length=R * 0.070),
        origin=Origin(xyz=(0.0, 0.0, r.azimuth_height), rpy=_cyl_z()),
        material=materials["rim"],
        name="heavy_azimuth_bearing_ring", material_class_id="metal.stainless_matte",
    )
    root.visual(
        Box((r.base_radius * 0.55, R * 0.10, R * 0.22)),
        origin=Origin(xyz=(-r.base_radius * 0.65, r.base_depth * 0.58, R * 0.25)),
        material=materials["accent"],
        name="service_cable_box", material_class_id="plastic.opaque_glossy_molded",
    )


def _skid_leg_bridge_xyz(r: ResolvedParabolicDishConfig) -> tuple[float, float, float]:
    """Shared anchor for the mobile-skid transport-leg hinge bridge."""
    return (0.0, -r.base_depth * 1.6, r.dish_radius * 0.12)


def _decorate_skid_root(
    root: Part, r: ResolvedParabolicDishConfig, materials: dict[str, object]
) -> None:
    R = r.dish_radius
    bw = r.base_radius * 0.95
    bd = r.base_depth * 1.6
    for sx, side in ((-1.0, "left"), (1.0, "right")):
        root.visual(
            Box((R * 0.07, bd * 2.05, R * 0.09)),
            origin=Origin(xyz=(sx * bw, 0.0, R * 0.045)),
            material=materials["support_dark"],
            name=f"{side}_transport_skid_rail", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
    for sy, end in ((-1.0, "front"), (1.0, "rear")):
        root.visual(
            Box((bw * 2.25, R * 0.07, R * 0.07)),
            origin=Origin(xyz=(0.0, sy * bd, R * 0.055)),
            material=materials["support_dark"],
            name=f"{end}_skid_crossbar", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
    root.visual(
        Box((bw * 2.05, bd * 1.75, R * 0.08)),
        origin=Origin(xyz=(0.0, 0.0, R * 0.095)),
        material=materials["support"],
        name="skid_center_deck", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.115, length=max(R * 0.08, r.azimuth_height - R * 0.10)),
        origin=Origin(xyz=(0.0, 0.0, (r.azimuth_height + R * 0.10) * 0.5), rpy=_cyl_z()),
        material=materials["support"],
        name="skid_center_post", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.18, length=R * 0.060),
        origin=Origin(xyz=(0.0, 0.0, r.azimuth_height), rpy=_cyl_z()),
        material=materials["rim"],
        name="skid_azimuth_bearing_race", material_class_id="metal.stainless_matte",
    )
    bx, by, bz = _skid_leg_bridge_xyz(r)
    root.visual(
        Box((bw * 0.9, R * 0.10, R * 0.12)),
        origin=Origin(xyz=(bx, by, bz)),
        material=materials["support_dark"],
        name="skid_leg_hinge_bridge", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )


def _decorate_wall_root(
    root: Part, r: ResolvedParabolicDishConfig, materials: dict[str, object]
) -> None:
    R = r.dish_radius
    H = r.azimuth_height
    bw = r.base_radius * 1.1
    wall_y = r.base_depth * 1.15
    root.visual(
        Box((bw * 2.0, R * 0.06, H * 1.12)),
        origin=Origin(xyz=(0.0, wall_y, H * 0.56)),
        material=materials["support_dark"],
        name="wall_mount_plate", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    for frac, lv in ((0.30, "lower"), (0.80, "upper")):
        root.visual(
            Box((R * 0.075, wall_y, R * 0.075)),
            origin=Origin(xyz=(0.0, wall_y * 0.5, H * frac)),
            material=materials["support"],
            name=f"wall_{lv}_standoff_arm", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
        )
    root.visual(
        Box((R * 0.05, wall_y * 0.9, R * 0.05)),
        origin=Origin(xyz=(0.0, wall_y * 0.5, H * 0.55), rpy=(0.0, math.pi / 2.5, 0.0)),
        material=materials["support_dark"],
        name="wall_diagonal_brace", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.075, length=H),
        origin=Origin(xyz=(0.0, 0.0, H * 0.5), rpy=_cyl_z()),
        material=materials["support"],
        name="vertical_wall_mast_pipe", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    root.visual(
        Cylinder(radius=R * 0.15, length=R * 0.060),
        origin=Origin(xyz=(0.0, 0.0, H), rpy=_cyl_z()),
        material=materials["rim"],
        name="wall_mast_top_collar", material_class_id="metal.stainless_matte",
    )


def _build_root_support(
    model: ArticulatedObject,
    r: ResolvedParabolicDishConfig,
    materials: dict[str, object],
) -> Part:
    name_by_style = {
        "pedestal": "pedestal",
        "roof_mount": "roof_mount",
        "tripod": "tripod",
        "mast": "mast",
        "heavy_service_base": "base",
        "mobile_skid_base": "skid_base",
        "wall_mast_mount": "wall_mount",
    }
    root = model.part(name_by_style[r.root_style])
    if r.root_style == "roof_mount":
        _decorate_roof_root(root, r, materials)
    elif r.root_style == "tripod":
        _decorate_tripod_root(root, r, materials)
    elif r.root_style == "mast":
        _decorate_mast_root(root, r, materials)
    elif r.root_style == "heavy_service_base":
        _decorate_heavy_root(root, r, materials)
    elif r.root_style == "mobile_skid_base":
        _decorate_skid_root(root, r, materials)
    elif r.root_style == "wall_mast_mount":
        _decorate_wall_root(root, r, materials)
    else:
        _decorate_pedestal_root(root, r, materials)
    root.inertial = Inertial.from_geometry(
        Cylinder(radius=r.base_radius, length=max(0.08, r.azimuth_height)),
        mass=max(30.0, 80.0 * r.dish_radius),
        origin=Origin(xyz=(0.0, 0.0, r.azimuth_height * 0.5), rpy=_cyl_z()),
    )
    return root


def _build_azimuth_stage(
    model: ArticulatedObject,
    r: ResolvedParabolicDishConfig,
    root: Part,
    materials: dict[str, object],
) -> ChainAnchors:
    az = model.part("azimuth_yoke")
    R = r.dish_radius
    az.visual(
        Cylinder(radius=R * 0.22, length=R * 0.090),
        origin=Origin(rpy=_cyl_z()),
        material=materials["rim"],
        name="azimuth_upper_turntable", material_class_id="metal.stainless_matte",
    )
    az.visual(
        Cylinder(radius=R * 0.145, length=R * 0.16),
        origin=Origin(xyz=(0.0, 0.0, R * 0.085), rpy=_cyl_z()),
        material=materials["support"],
        name="azimuth_motor_can", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    hinge_z = R * 1.55
    cheek_z = r.yoke_cheek_height * 0.50
    for sign, side in ((-1.0, "left"), (1.0, "right")):
        x = sign * r.yoke_span * 0.5
        az.visual(
            Box((r.yoke_thickness, R * 0.22, r.yoke_cheek_height)),
            origin=Origin(xyz=(x, 0.0, cheek_z)),
            material=materials["support"],
            name=f"{side}_elevation_yoke_cheek", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
        )
        az.visual(
            Cylinder(radius=r.bearing_radius * 1.16, length=r.yoke_thickness * 1.35),
            origin=Origin(xyz=(x, 0.0, hinge_z), rpy=_cyl_x()),
            material=materials["rim"],
            name=f"{side}_elevation_bearing_socket", material_class_id="metal.stainless_matte",
        )
        az.visual(
            Box((r.yoke_thickness * 1.15, R * 0.10, R * 0.13)),
            origin=Origin(xyz=(x, -R * 0.11, hinge_z - R * 0.13)),
            material=materials["support_dark"],
            name=f"{side}_yoke_lower_gusset", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
    az.visual(
        Cylinder(radius=max(0.008, R * 0.018), length=r.yoke_span + r.yoke_thickness * 1.60),
        origin=Origin(xyz=(0.0, 0.0, hinge_z), rpy=_cyl_x()),
        material=materials["support_dark"],
        name="elevation_cross_axle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    az.visual(
        Cylinder(radius=R * 0.018, length=R * 0.30),
        origin=Origin(xyz=(0.0, 0.0, R * 0.15), rpy=_cyl_z()),
        material=materials["support"],
        name="central_yoke_riser_tube", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
    )
    az.visual(
        Box((r.yoke_span + r.yoke_thickness, R * 0.18, R * 0.10)),
        origin=Origin(xyz=(0.0, 0.0, R * 0.24)),
        material=materials["support_dark"],
        name="rear_yoke_cross_tie", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    az.visual(
        Box((r.yoke_span + r.yoke_thickness, R * 0.18, R * 0.080)),
        origin=Origin(xyz=(0.0, R * 0.11, r.yoke_cheek_height - R * 0.08)),
        material=materials["support_dark"],
        name="upper_yoke_bridge", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    if r.azimuth_stage_style in ("instrument_yoke", "mast_fork"):
        knob_z = hinge_z + R * 0.18
        az.visual(
            Cylinder(radius=R * 0.022, length=R * 0.30),
            origin=Origin(
                xyz=(r.yoke_span * 0.50 + r.yoke_thickness * 0.50 + R * 0.075, 0.0, knob_z),
                rpy=_cyl_x(),
            ),
            material=materials["support_dark"],
            name="side_lock_knob_stem", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
        az.visual(
            Cylinder(radius=R * 0.065, length=R * 0.16),
            origin=Origin(
                xyz=(r.yoke_span * 0.50 + r.yoke_thickness + R * 0.12, 0.0, knob_z),
                rpy=_cyl_x(),
            ),
            material=materials["accent"],
            name="side_lock_knob_visual", material_class_id="plastic.opaque_glossy_molded",
        )
    if r.azimuth_stage_style in ("compact_fork", "tripod_head"):
        az.visual(
            Box((r.yoke_span * 0.60, R * 0.18, R * 0.12)),
            origin=Origin(xyz=(0.0, 0.0, R * 0.06)),
            material=materials["support_dark"],
            name="compact_head_block", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )

    if r.azimuth_joint_type == "revolute_limited":
        model.articulation(
            "azimuth_spin",
            ArticulationType.REVOLUTE,
            parent=root,
            child=az,
            origin=Origin(xyz=(0.0, 0.0, r.azimuth_height)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=150.0,
                velocity=0.7,
                lower=-math.pi,
                upper=math.pi,
            ),
        )
    else:
        model.articulation(
            "azimuth_spin",
            ArticulationType.CONTINUOUS,
            parent=root,
            child=az,
            origin=Origin(xyz=(0.0, 0.0, r.azimuth_height)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=150.0, velocity=0.7),
        )
    az.inertial = Inertial.from_geometry(
        Box((r.yoke_span, R * 0.25, max(R * 0.28, r.yoke_cheek_height))),
        mass=max(8.0, 20.0 * R),
        origin=Origin(xyz=(0.0, 0.0, cheek_z)),
    )
    return ChainAnchors(
        root=root,
        azimuth=az,
        hinge_z=hinge_z,
        yoke_span=r.yoke_span,
        bearing_radius=r.bearing_radius,
    )


def _add_reflector_shell(
    model: ArticulatedObject,
    dish: Part,
    r: ResolvedParabolicDishConfig,
    materials: dict[str, object],
) -> None:
    wall = max(0.012, r.dish_radius * 0.028)
    shell = _reflector_shell_geometry(r.dish_radius, r.dish_depth, wall)
    dish.visual(
        _mesh_for_model(model, shell, "parabolic_reflector_shell"),
        origin=Origin(xyz=(0.0, -r.dish_depth * 0.18, 0.0)),
        material=materials["reflector_inner"],
        name="concave_parabolic_reflector_shell", material_class_id="metal.aluminum_bare",
    )
    _add_torus(
        model,
        dish,
        name="reflector_front_rim_ring",
        radius=r.dish_radius,
        tube=max(0.014, r.dish_radius * 0.026),
        material=materials["rim"],
        origin=Origin(xyz=(0.0, -r.dish_depth * 1.18, 0.0), rpy=_cyl_y()),
        radial_segments=12,
        tubular_segments=80,
    )
    dish.visual(
        Cylinder(radius=r.dish_radius * 0.12, length=max(0.030, r.dish_radius * 0.070)),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=_cyl_y()),
        material=materials["support_dark"],
        name="rear_hub_plate", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    dish.visual(
        Cylinder(radius=r.dish_radius * 0.092, length=r.dish_depth * 1.34),
        origin=Origin(xyz=(0.0, -r.dish_depth * 0.60, 0.0), rpy=_cyl_y()),
        material=materials["support_dark"],
        name="central_reflector_spine", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    dish.visual(
        Box((r.dish_radius * 1.88, r.dish_depth * 1.26, r.dish_radius * 0.038)),
        origin=Origin(xyz=(0.0, -r.dish_depth * 0.63, 0.0)),
        material=materials["rim"],
        name="horizontal_reflector_bond_rib", material_class_id="metal.stainless_matte",
    )
    dish.visual(
        Box((r.dish_radius * 0.038, r.dish_depth * 1.26, r.dish_radius * 1.88)),
        origin=Origin(xyz=(0.0, -r.dish_depth * 0.63, 0.0)),
        material=materials["rim"],
        name="vertical_reflector_bond_rib", material_class_id="metal.stainless_matte",
    )


def _add_back_frame(
    dish: Part,
    r: ResolvedParabolicDishConfig,
    materials: dict[str, object],
) -> None:
    R = r.dish_radius
    dish.visual(
        Box((R * 0.18, R * 0.10, R * 0.18)),
        origin=Origin(xyz=(0.0, R * 0.035, 0.0)),
        material=materials["support_dark"],
        name="central_rear_bearing_block", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
    )
    for sign, side in ((-1.0, "left"), (1.0, "right")):
        x = sign * r.yoke_span * 0.5
        dish.visual(
            Cylinder(radius=r.bearing_radius * 0.98, length=r.yoke_thickness * 1.60),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=_cyl_x()),
            material=materials["rim"],
            name=f"{side}_dish_trunnion_pin", material_class_id="metal.stainless_matte",
        )
        dish.visual(
            Sphere(radius=r.bearing_radius * 1.05),
            origin=Origin(xyz=(x, 0.0, 0.0)),
            material=materials["rim"],
            name=f"{side}_dish_trunnion_cap", material_class_id="metal.stainless_matte",
        )
        dish.visual(
            Box((r.yoke_span * 0.54, R * 0.052, R * 0.052)),
            origin=Origin(xyz=(sign * r.yoke_span * 0.25, R * 0.025, 0.0), rpy=(0.0, 0.0, 0.0)),
            material=materials["support_dark"],
            name=f"{side}_trunnion_to_hub_spoke", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
    rib_count = r.rear_rib_count  # sampled multiplicity {4,6,8,12}
    for i in range(rib_count):
        angle = math.tau * i / rib_count
        x = math.cos(angle) * R * 0.39
        z = math.sin(angle) * R * 0.39
        length = R * 0.92
        dish.visual(
            Box((R * 0.035, R * 0.045, length)),
            origin=Origin(
                xyz=(x * 0.45, R * 0.018, z * 0.45),
                rpy=(0.0, angle + math.pi / 2.0, 0.0),
            ),
            material=materials["support_dark"],
            name=f"rear_radial_rib_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
    if r.back_frame_style in ("instrument_box", "covered"):
        dish.visual(
            Box((R * 0.10, R * 0.36, R * 0.38)),
            origin=Origin(xyz=(0.0, R * 0.23, -R * 0.15)),
            material=materials["support_dark"],
            name="rear_electronics_support_pylon", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
        dish.visual(
            Box((R * 0.36, R * 0.20, R * 0.28)),
            origin=Origin(xyz=(0.0, R * 0.42, -R * 0.30)),
            material=materials["support"],
            name="rear_electronics_cover_box", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
        )
        dish.visual(
            Box((R * 0.28, R * 0.035, R * 0.20)),
            origin=Origin(xyz=(0.0, R * 0.520, -R * 0.30)),
            material=materials["accent"],
            name="rear_cover_service_panel", material_class_id="metal.paint_coated",
        )


def _strut_between(
    part: Part,
    p0: tuple[float, float, float],
    p1: tuple[float, float, float],
    radius: float,
    material: object,
    name: str,
) -> None:
    """A cylinder spanning p0->p1 (local +z aligned to the segment direction)."""
    dx, dy, dz = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-6:
        return
    pitch = math.atan2(math.sqrt(dx * dx + dy * dy), dz)
    yaw = math.atan2(dy, dx)
    mid = (0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]), 0.5 * (p0[2] + p1[2]))
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=mid, rpy=(0.0, pitch, yaw)),
        material=material,
        name=name, material_class_id="metal.aluminum_bare",
    )


def _add_feed_support(
    dish: Part,
    r: ResolvedParabolicDishConfig,
    materials: dict[str, object],
) -> None:
    R = r.dish_radius
    n = r.feed_strut_count
    feed_y = -r.dish_depth * 1.18 - r.feed_length * 0.5
    front_y = -r.dish_depth * 1.18
    horn_y = -r.dish_depth * 1.18 - r.feed_length
    if n <= 0:
        return  # none_minimal: bare reflector, no feed boom
    # central boom/rod — connects the dish (like the single-boom feed) to the horn.
    dish.visual(
        Cylinder(radius=R * 0.020 if n == 1 else R * 0.014, length=r.feed_length),
        origin=Origin(xyz=(0.0, feed_y, 0.0), rpy=_cyl_y()),
        material=materials["feed"],
        name="central_feed_boom", material_class_id="metal.aluminum_bare",
    )
    if n >= 2:
        # feed-root disk on the central boom + N struts converging to a horn collar.
        # `feed_strut_count` (2/3/4) is the spec's feed-support multiplicity.
        dish.visual(
            Cylinder(radius=R * 0.22, length=R * 0.030),
            origin=Origin(xyz=(0.0, front_y, 0.0), rpy=_cyl_y()),
            material=materials["feed"],
            name="feed_root_disk", material_class_id="metal.aluminum_bare",
        )
        collar = (0.0, horn_y + R * 0.08, 0.0)
        dish.visual(
            Cylinder(radius=R * 0.052, length=R * 0.06),
            origin=Origin(xyz=collar, rpy=_cyl_y()),
            material=materials["feed"],
            name="feed_collar", material_class_id="metal.aluminum_bare",
        )
        for i in range(n):
            ang = math.tau * i / n + math.pi / 2.0
            p_root = (math.cos(ang) * R * 0.20, front_y, math.sin(ang) * R * 0.20)
            _strut_between(dish, p_root, collar, R * 0.016, materials["feed"], f"feed_strut_{i}")
    dish.visual(
        Cylinder(radius=R * 0.075, length=R * 0.16),
        origin=Origin(xyz=(0.0, horn_y, 0.0), rpy=_cyl_y()),
        material=materials["accent"],
        name="feed_horn_cylinder", material_class_id="metal.paint_coated",
    )
    dish.visual(
        Sphere(radius=R * 0.070),
        origin=Origin(xyz=(0.0, horn_y - R * 0.075, 0.0)),
        material=materials["feed"],
        name="feed_horn_receiver_ball", material_class_id="plastic.opaque_glossy_molded",
    )
    dish.visual(
        Cylinder(radius=R * 0.036, length=R * 0.22),
        origin=Origin(xyz=(0.0, horn_y + R * 0.10, 0.0), rpy=_cyl_y()),
        material=materials["feed"],
        name="feed_horn_back_neck", material_class_id="metal.aluminum_bare",
    )


def _add_back_stiffener_rings(
    model: ArticulatedObject,
    dish: Part,
    r: ResolvedParabolicDishConfig,
    materials: dict[str, object],
) -> None:
    """Concentric rear stiffener rings (multiplicity, sourced from samples
    7f8512f0 / 77d410b1). Each torus lies in the dish back plane and crosses
    the radial ribs, so it is supported by them."""
    n = r.back_ring_count
    R = r.dish_radius
    for i in range(n):
        rad = R * (0.28 + 0.24 * i / max(1, n - 1)) if n > 1 else R * 0.40
        _add_torus(
            model,
            dish,
            name=f"rear_stiffener_ring_{i}",
            radius=rad,
            tube=R * 0.022,
            material=materials["support_dark"],
            origin=Origin(xyz=(0.0, R * 0.05, 0.0), rpy=_cyl_y()),
        )


def _build_dish_assembly(
    model: ArticulatedObject,
    r: ResolvedParabolicDishConfig,
    anchors: ChainAnchors,
    materials: dict[str, object],
) -> Part:
    dish = model.part("dish_assembly")
    _add_reflector_shell(model, dish, r, materials)
    _add_back_frame(dish, r, materials)
    _add_back_stiffener_rings(model, dish, r, materials)
    _add_feed_support(dish, r, materials)
    if r.reflector_style in ("cadquery_spoked", "portable_ribbed"):
        dish.visual(
            Sphere(radius=r.dish_radius * 0.18),
            origin=Origin(xyz=(0.0, -r.dish_depth * 0.86, 0.0)),
            material=materials["rim"],
            name="front_spoke_center_boss", material_class_id="metal.stainless_matte",
        )
        for i, angle in enumerate((0.0, math.pi / 3.0, 2.0 * math.pi / 3.0)):
            dish.visual(
                Box((r.dish_radius * 0.030, r.dish_radius * 0.040, r.dish_radius * 0.80)),
                origin=Origin(
                    xyz=(
                        math.cos(angle) * r.dish_radius * 0.18,
                        -r.dish_depth * 0.72,
                        math.sin(angle) * r.dish_radius * 0.18,
                    ),
                    rpy=(0.0, angle, 0.0),
                ),
                material=materials["rim"],
                name=f"front_spoked_reflector_strut_{i}", material_class_id="metal.stainless_matte",
            )
    model.articulation(
        "elevation_tilt",
        ArticulationType.REVOLUTE,
        parent=anchors.azimuth,
        child=dish,
        origin=Origin(xyz=(0.0, 0.0, anchors.hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=120.0,
            velocity=0.8,
            lower=r.elevation_lower,
            upper=r.elevation_upper,
        ),
    )
    dish.inertial = Inertial.from_geometry(
        Sphere(radius=r.dish_radius),
        mass=max(5.0, 12.0 * r.dish_radius),
        origin=Origin(),
    )
    return dish


def _build_auxiliary(
    model: ArticulatedObject,
    r: ResolvedParabolicDishConfig,
    anchors: ChainAnchors,
    dish: Part,
    materials: dict[str, object],
) -> None:
    """Slot D optional auxiliary mechanism as a real articulated child.

    * rear_cover         REVOLUTE hinged electronics cover on the dish rear box.
    * instrument_hatch   FIXED instrument box on the dish rear hub + REVOLUTE hatch.
    * side_crank         CONTINUOUS manual crank/knob on the azimuth yoke side.
    """
    aux = r.auxiliary_mechanism
    if aux == "none":
        return
    R = r.dish_radius

    if aux == "rear_cover":
        # hinge a cover leaf on the rear electronics box (top-rear edge).
        box_y, box_z = R * 0.42, -R * 0.30
        box_top = box_z + R * 0.14
        cover = model.part("rear_cover")
        cover.visual(
            Cylinder(radius=R * 0.030, length=R * 0.34),
            origin=Origin(rpy=_cyl_x()),
            material=materials["support_dark"],
            name="cover_hinge_barrel", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
        cover.visual(
            Box((R * 0.34, R * 0.030, R * 0.30)),
            origin=Origin(xyz=(0.0, 0.0, -R * 0.15)),
            material=materials["accent"],
            name="cover_leaf", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((R * 0.10, R * 0.05, R * 0.030)),
            origin=Origin(xyz=(0.0, -R * 0.03, -R * 0.28)),
            material=materials["support_dark"],
            name="cover_pull", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
        model.articulation(
            "rear_cover_hinge",
            ArticulationType.REVOLUTE,
            parent=dish,
            child=cover,
            origin=Origin(xyz=(0.0, box_y, box_top)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=1.0, lower=0.0, upper=1.25),
        )
    elif aux == "instrument_hatch":
        # FIXED instrument box overlapping the dish rear bearing block.
        ibox = model.part("instrument_box")
        ibox.visual(
            Box((R * 0.30, R * 0.22, R * 0.26)),
            origin=Origin(),
            material=materials["support"],
            name="instrument_box_body", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
        )
        model.articulation(
            "instrument_box_fixed",
            ArticulationType.FIXED,
            parent=dish,
            child=ibox,
            origin=Origin(xyz=(0.0, R * 0.42, -R * 0.16)),
        )
        hatch = model.part("instrument_hatch")
        hatch.visual(
            Cylinder(radius=R * 0.026, length=R * 0.28),
            origin=Origin(rpy=_cyl_x()),
            material=materials["support_dark"],
            name="hatch_hinge_barrel", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
        hatch.visual(
            Box((R * 0.28, R * 0.024, R * 0.20)),
            origin=Origin(xyz=(0.0, 0.0, -R * 0.10)),
            material=materials["accent"],
            name="hatch_leaf", material_class_id="metal.paint_coated",
        )
        model.articulation(
            "instrument_hatch_hinge",
            ArticulationType.REVOLUTE,
            parent=ibox,
            child=hatch,
            origin=Origin(xyz=(0.0, 0.0, R * 0.13)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=15.0, velocity=1.0, lower=0.0, upper=1.2),
        )
    elif aux == "side_crank":
        # CONTINUOUS manual crank on the right yoke cheek.
        crank = model.part("side_crank")
        crank.visual(
            Cylinder(radius=R * 0.020, length=R * 0.20),
            origin=Origin(rpy=_cyl_x()),
            material=materials["support_dark"],
            name="crank_shaft", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
        crank.visual(
            Cylinder(radius=R * 0.055, length=R * 0.040),
            origin=Origin(xyz=(R * 0.11, 0.0, 0.0), rpy=_cyl_x()),
            material=materials["accent"],
            name="crank_hub", material_class_id="plastic.opaque_glossy_molded",
        )
        crank.visual(
            Box((R * 0.030, R * 0.030, R * 0.22)),
            origin=Origin(xyz=(R * 0.12, 0.0, R * 0.10)),
            material=materials["support_dark"],
            name="crank_handle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
        model.articulation(
            "crank_spin",
            ArticulationType.CONTINUOUS,
            parent=anchors.azimuth,
            child=crank,
            origin=Origin(xyz=(anchors.yoke_span * 0.5, 0.0, anchors.hinge_z * 0.62)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=10.0, velocity=3.0),
        )
    elif aux == "transport_leg":
        # fold-down stabilizer leg hinged on the mobile-skid leg bridge.
        leg = model.part("transport_leg")
        leg.visual(
            Cylinder(radius=R * 0.030, length=R * 0.40),
            origin=Origin(rpy=_cyl_x()),
            material=materials["support_dark"],
            name="leg_hinge_barrel", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
        leg.visual(
            Cylinder(radius=R * 0.035, length=R * 0.80),
            origin=Origin(xyz=(0.0, 0.0, -R * 0.34), rpy=_cyl_z()),
            material=materials["support"],
            name="leg_tube", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized_gray" else "metal.paint_coated"),
        )
        leg.visual(
            Box((R * 0.20, R * 0.22, R * 0.04)),
            origin=Origin(xyz=(0.0, 0.0, -R * 0.72)),
            material=materials["support_dark"],
            name="leg_foot_pad", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"galvanized_gray", "portable_black"} else "metal.paint_coated"),
        )
        model.articulation(
            "transport_leg_fold",
            ArticulationType.REVOLUTE,
            parent=anchors.root,
            child=leg,
            origin=Origin(xyz=_skid_leg_bridge_xyz(r)),
            axis=(1.0, 0.0, 0.0),
            # rest = deployed (down); folds FORWARD (-x rotation) away from the skid.
            motion_limits=MotionLimits(effort=25.0, velocity=1.0, lower=-1.35, upper=0.0),
        )


def build_parabolic_dish(
    config: ParabolicDishConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or ParabolicDishConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    materials = _register_materials(model, r.palette)
    root = _build_root_support(model, r, materials)
    anchors = _build_azimuth_stage(model, r, root, materials)
    dish = _build_dish_assembly(model, r, anchors, materials)
    _build_auxiliary(model, r, anchors, dish, materials)
    return model


def build_seeded_parabolic_dish(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_parabolic_dish(config_from_seed(seed), assets=assets)


def slot_choices_for_config(config: ParabolicDishConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("root_support", r.root_style),
        ("azimuth_stage", r.azimuth_stage_style),
        ("dish_reflector_assembly", r.reflector_style),
        ("auxiliary_mechanism", r.auxiliary_mechanism),
        ("feed_style", r.feed_style),
        ("feed_strut_count", str(r.feed_strut_count)),
        ("back_frame_style", r.back_frame_style),
        ("rear_rib_count", str(r.rear_rib_count)),
        ("back_ring_count", str(r.back_ring_count)),
        ("support_leg_count", str(r.support_leg_count)),
        ("azimuth_joint_type", r.azimuth_joint_type),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    part_names = {part.name for part in model.parts}
    root_names = ("pedestal", "roof_mount", "tripod", "mast", "base", "skid_base", "wall_mount")
    if "azimuth_yoke" in part_names:
        az = model.get_part("azimuth_yoke")
        for root_name in root_names:
            if root_name not in part_names:
                continue
            root = model.get_part(root_name)
            for elem_a in (
                "azimuth_lower_bearing_race",
                "roof_turntable_race",
                "tripod_head_bearing_race",
                "mast_top_bearing_collar",
                "heavy_azimuth_bearing_ring",
                "round_pedestal_column",
                "short_roof_pedestal",
                "tripod_center_post",
                "vertical_mast_tube",
                "heavy_center_pedestal",
                "skid_azimuth_bearing_race",
                "skid_center_post",
                "wall_mast_top_collar",
                "vertical_wall_mast_pipe",
            ):
                for elem_b in (
                    "azimuth_upper_turntable",
                    "azimuth_motor_can",
                    "compact_head_block",
                    "central_yoke_riser_tube",
                ):
                    try:
                        ctx.allow_overlap(
                            root,
                            az,
                            elem_a=elem_a,
                            elem_b=elem_b,
                            reason="azimuth turntable is seated in the root bearing race",
                        )
                    except Exception:
                        pass
    if "azimuth_yoke" in part_names and "dish_assembly" in part_names:
        az = model.get_part("azimuth_yoke")
        dish = model.get_part("dish_assembly")
        for elem_a in (
            "left_elevation_bearing_socket",
            "right_elevation_bearing_socket",
            "left_elevation_yoke_cheek",
            "right_elevation_yoke_cheek",
            "left_yoke_lower_gusset",
            "right_yoke_lower_gusset",
            "elevation_cross_axle",
        ):
            for elem_b in (
                "left_dish_trunnion_pin",
                "right_dish_trunnion_pin",
                "left_dish_trunnion_cap",
                "right_dish_trunnion_cap",
                "left_trunnion_to_hub_spoke",
                "right_trunnion_to_hub_spoke",
                "rear_electronics_support_pylon",
            ):
                try:
                    ctx.allow_overlap(
                        az,
                        dish,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="dish trunnion is captured by elevation yoke bearings",
                    )
                except Exception:
                    pass
        for elem_a in (
            "rear_yoke_cross_tie",
            "upper_yoke_bridge",
            "elevation_cross_axle",
            "central_yoke_riser_tube",
        ):
            for elem_b in (
                "central_rear_bearing_block",
                "rear_hub_plate",
                "central_reflector_spine",
                "horizontal_reflector_bond_rib",
                "vertical_reflector_bond_rib",
                *[f"rear_radial_rib_{i}" for i in range(12)],
                "rear_stiffener_ring_0",
                "rear_stiffener_ring_1",
                "rear_stiffener_ring_2",
                "left_trunnion_to_hub_spoke",
                "right_trunnion_to_hub_spoke",
                "rear_electronics_support_pylon",
            ):
                try:
                    ctx.allow_overlap(
                        az,
                        dish,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="rear yoke bridge sits close to the dish hub in the elevation mount",
                    )
                except Exception:
                    pass

    # Slot D auxiliary captured-pin / mount overlaps.
    def _try_allow(pa, pb, ea, eb, reason):
        if pa in part_names and pb in part_names:
            try:
                ctx.allow_overlap(
                    model.get_part(pa), model.get_part(pb), elem_a=ea, elem_b=eb, reason=reason
                )
            except Exception:
                pass

    # incidental cross-axle / bearing sockets vs dish hub features (front spoke
    # boss/struts on small dishes; rear radial ribs near the hub at the hinge).
    for ea in (
        "elevation_cross_axle",
        "left_elevation_bearing_socket",
        "right_elevation_bearing_socket",
    ):
        for eb in (
            "front_spoke_center_boss",
            "front_spoked_reflector_strut_0",
            "front_spoked_reflector_strut_1",
            "front_spoked_reflector_strut_2",
            "central_rear_bearing_block",
            *[f"rear_radial_rib_{i}" for i in range(12)],
            "rear_stiffener_ring_0",
            "rear_stiffener_ring_1",
            "rear_stiffener_ring_2",
        ):
            _try_allow(
                "azimuth_yoke",
                "dish_assembly",
                ea,
                eb,
                "cross axle / bearing near dish hub features",
            )
    if "rear_cover" in part_names:
        for eb in ("cover_hinge_barrel", "cover_leaf", "cover_pull"):
            for ea in (
                "rear_electronics_cover_box",
                "rear_cover_service_panel",
                "rear_electronics_support_pylon",
                "central_rear_bearing_block",
            ):
                _try_allow("dish_assembly", "rear_cover", ea, eb, "cover hinged on dish rear box")
    if "instrument_box" in part_names:
        for ea in (
            "central_rear_bearing_block",
            "rear_electronics_cover_box",
            "rear_electronics_support_pylon",
            "rear_cover_service_panel",
            "left_trunnion_to_hub_spoke",
            "right_trunnion_to_hub_spoke",
            *[f"rear_radial_rib_{i}" for i in range(12)],
        ):
            _try_allow(
                "dish_assembly",
                "instrument_box",
                ea,
                "instrument_box_body",
                "instrument box fixed on dish rear",
            )
        for ea in (
            "elevation_cross_axle",
            "left_elevation_bearing_socket",
            "right_elevation_bearing_socket",
            "central_yoke_riser_tube",
            "rear_yoke_cross_tie",
        ):
            _try_allow(
                "azimuth_yoke",
                "instrument_box",
                ea,
                "instrument_box_body",
                "instrument box near elevation axle",
            )
        for eb in ("hatch_hinge_barrel", "hatch_leaf"):
            _try_allow(
                "instrument_box",
                "instrument_hatch",
                "instrument_box_body",
                eb,
                "hatch hinged on box",
            )
            for ea in (
                "rear_electronics_cover_box",
                "rear_cover_service_panel",
                "rear_electronics_support_pylon",
            ):
                _try_allow(
                    "dish_assembly", "instrument_hatch", ea, eb, "hatch closed over dish rear box"
                )
    if "side_crank" in part_names:
        for ea in (
            "right_elevation_yoke_cheek",
            "right_elevation_bearing_socket",
            "right_yoke_lower_gusset",
        ):
            _try_allow(
                "azimuth_yoke",
                "side_crank",
                ea,
                "crank_shaft",
                "crank shaft journaled in yoke cheek",
            )
    if "transport_leg" in part_names:
        for eb in ("leg_hinge_barrel", "leg_tube"):
            for ea in (
                "skid_leg_hinge_bridge",
                "front_skid_crossbar",
                "left_transport_skid_rail",
                "right_transport_skid_rail",
            ):
                _try_allow(
                    "skid_base", "transport_leg", ea, eb, "transport leg hinged on skid bridge"
                )


def run_parabolic_dish_tests(
    object_model: ArticulatedObject,
    config: ParabolicDishConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=96,
        overlap_tol=0.005,
        overlap_volume_tol=0.0,
        ignore_adjacent=False,
        ignore_fixed=True,
    )

    part_names = {part.name for part in object_model.parts}
    joint_names = {joint.name for joint in object_model.joints}
    if "azimuth_yoke" not in part_names:
        ctx.fail("azimuth_stage", "parabolic dish must include an azimuth_yoke part")
    if "dish_assembly" not in part_names:
        ctx.fail("dish_identity", "parabolic dish must include a dish_assembly part")
    if "azimuth_spin" not in joint_names:
        ctx.fail("azimuth_joint", "parabolic dish must include azimuth_spin")
    if "elevation_tilt" not in joint_names:
        ctx.fail("elevation_joint", "parabolic dish must include elevation_tilt")
    for joint in object_model.joints:
        if joint.name == "azimuth_spin":
            if joint.axis != (0.0, 0.0, 1.0):
                ctx.fail("azimuth_axis", "azimuth_spin axis must be vertical Z")
            if joint.articulation_type not in (
                ArticulationType.CONTINUOUS,
                ArticulationType.REVOLUTE,
            ):
                ctx.fail("azimuth_type", "azimuth_spin must be continuous or revolute")
        if joint.name == "elevation_tilt":
            if joint.axis != (1.0, 0.0, 0.0):
                ctx.fail("elevation_axis", "elevation_tilt axis must be horizontal X")
            if joint.articulation_type != ArticulationType.REVOLUTE:
                ctx.fail("elevation_type", "elevation_tilt must be revolute")
    if r.dish_depth <= 0.0 or r.dish_radius <= 0.0:
        ctx.fail("reflector_geometry", "dish radius/depth must be positive")
    return ctx.report()


# Implementation notes (reflects the reviewed spec, fully implemented):
# * config_from_seed is deterministic procedural sampling (no curated/modulo
#   table); each slot is drawn from its compatible candidate subset.
# * Slot A root_support: pedestal / roof_mount / tripod / mast / heavy_service_base
#   / mobile_skid_base / wall_mast_mount (7 families).
# * Slot B azimuth_stage: dual_yoke / compact_fork / tripod_head / mast_fork /
#   instrument_yoke, gated per root.
# * Slot C reflector: lathe shell + feed/back-frame variants (feed_strut_count
#   1/2/3/4 multiplicity via feed_style).
# * Slot D auxiliary is REAL articulated parts, sampled with gating:
#   - instrument_hatch  FIXED instrument_box + REVOLUTE hatch on the dish rear.
#   - rear_cover        REVOLUTE hinged electronics cover (needs rear box back).
#   - side_crank        CONTINUOUS manual crank on the azimuth yoke side.
#   - transport_leg     REVOLUTE fold-down stabilizer (mobile_skid_base only).
# Invariant: keep the elevation origin at the yoke trunnion center. Do not move
# it to the reflector focus or dish rim; that produces visually plausible but
# invalid pan-tilt kinematics.
#
# Stable seed matrix:
# seed 0: pedestal + dual yoke + lathed reflector + single feed boom.
# seed 1: roof plate + compact fork + dual feed struts.
# seed 2: portable tripod + ribbed dish + tripod feed.
# seed 3: mast fork + spoked reflector.
# seed 4: heavy service base + instrument yoke visual.
# seed 5: tall pedestal + covered rear electronics cue.
# seed 6: roof mount + spoked reflector.
# seed 7: tripod visual + dual yoke.
# seed 8: mast visual + roof-style feed boom.
# seed 9: heavy base + compact instrumented reflector.
#
# These notes are comments rather than runtime data so they do not affect the
# generated model or storage records.
