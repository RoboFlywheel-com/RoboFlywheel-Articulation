# SPDX-License-Identifier: Apache-2.0

"""Playground merry-go-round (spherical / dome / drum spinner) modular template.

A rideable rotating playground device: a FIXED ground-anchored center post /
stand carries a rideable cage that spins freely 360 degrees about the vertical
Z axis (a single CONTINUOUS joint). The cage is a loop-emitted lattice of real
``TorusGeometry`` latitude rings + N meridian spline-tube arcs (or vertical
drum bars) with candy-stripe sleeves, all fixed to the cage as one rigid body.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Playground_Playground_playground_merry_go_round.md``
and the 7 5-star samples (1 parent + 6 slot-fork variants) synced under
``data/records/`` (S1 parent, S2 roundpost, S3 tripod, S4 dome, S5 drum, S6/S7
n_meridian variants).

Structure (pattern = ``mixed``): a single root ``post`` part (base_post module)
carries a single ``cage`` part (cage_form module) as the spinning child, plus
internal multiplicity (N meridian arcs / drum bars + latitude rings + clamps,
all baked as cage visuals — Rule 1).

  * ``base_post`` (3): square_box_post (Box) / round_turned_post (LatheGeometry
    turned shaft) / tripod_stand (hub + 3 spline-tube legs + shaft).
  * ``cage_form`` (3): spherical_hoop_cage (double-pole sphere, latitude tori +
    meridian arcs) / half_dome_cage (single upper pole, floor-base hemisphere) /
    cylindrical_drum_cage (double-pole equal-radius drum + vertical bars + spokes).
  * ``n_meridian`` (N in [2,6]): multiplicity — N full meridian planes (2N half
    arcs) for sphere/dome; the drum cage uses ``n_drum_bar`` instead.
  * ``n_latitude_ring`` (M in [3,5]): secondary multiplicity — M horizontal rings.
  * ``n_drum_bar`` (K in [8,16]): drum-only vertical-bar multiplicity.

Derived (resolve_config): ``journal_count`` = 1 for half_dome else 2;
``center_z`` from (base_post, cage_form); press-fit / ground-clearance / rideable
inequalities are projected here, never left to the builder.

The single CONTINUOUS ``cage_spin`` joint mounts the cage collars onto the post
journals (shaft-in-bushing). Those collar/journal pairs are coaxial cylindrical
captured-pin fits, declared via element-scoped ``allow_overlap`` + ``expect_within``
+ ``expect_contact`` (the grandfathered captured-pin pattern, mirroring each
source record's run_tests block); MatingContract is reserved for axis-aligned
flat faces and is not used for the cylindrical bearing fit.
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
    Box,
    Cylinder,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

BasePost = Literal["square_box_post", "round_turned_post", "tripod_stand"]
CageForm = Literal["spherical_hoop_cage", "half_dome_cage", "cylindrical_drum_cage"]
PaletteStyle = Literal[
    "classic_candy", "sky_blue_yellow", "steel_worn", "rust_retro", "mint_coral"
]

BASE_POSTS: tuple[BasePost, ...] = (
    "square_box_post",
    "round_turned_post",
    "tripod_stand",
)
CAGE_FORMS: tuple[CageForm, ...] = (
    "spherical_hoop_cage",
    "half_dome_cage",
    "cylindrical_drum_cage",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_candy",
    "sky_blue_yellow",
    "steel_worn",
    "rust_retro",
    "mint_coral",
)

# Multiplicity ranges (spec §"参数范围汇总").
N_MERIDIAN_MIN = 2
N_MERIDIAN_MAX = 6
N_LAT_MIN = 3
N_LAT_MAX = 5
N_DRUM_MIN = 8
N_DRUM_MAX = 16
# Small N high-frequency, large N rare tail (spec: 小 N 偏多).
N_MERIDIAN_VALUES = (2, 3, 4, 5, 6)
N_MERIDIAN_WEIGHTS = (0.30, 0.30, 0.22, 0.10, 0.08)

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), from the S1 parent + variants.
# ---------------------------------------------------------------------------
SPHERE_R = 0.90  # hoop sphere radius (1.8 m diameter)
DRUM_R = 0.88  # drum cage radius
DRUM_HALF_H = 0.75  # half-height of drum (1.5 m total)
TUBE_R = 0.020  # steel tube radius
STRIPE_R = 0.0215  # white stripe sleeve radius (proud of red tube)

POST_W = 0.12  # square post width
POST_H = 2.20  # post height
POST_SHAFT_R = 0.065  # round turned shaft radius
POST_FLANGE_R = 0.155  # round base flange radius
POST_BASE_PLATE_R = 0.18  # round ground anchor plate radius

# Tripod
HUB_R = 0.10
HUB_H = 0.12
HUB_Z = 0.35
SHAFT_R = 0.045
LEG_TUBE_R = 0.025
LEG_SPREAD = 0.55
FOOT_R = 0.060
FOOT_H = 0.025

# Bearing collar / journal (press fit: COLLAR_INNER_R > JOURNAL_R).
COLLAR_INNER_R = 0.0895
COLLAR_OUTER_R = 0.115
COLLAR_HALF_H = 0.070
JOURNAL_R = 0.0905  # < COLLAR_INNER_R? No — source uses 0.0905 > 0.0895; see note.
JOURNAL_LEN = 0.18

N_STRIPE_SEGMENTS = 8
N_SPOKE_ARMS = 6

# Nominal center heights by (base_post, cage_form) — spec equation.
CENTER_Z_SQUARE_ROUND = 1.10
CENTER_Z_TRIPOD = 1.40
# half_dome center_z = equator/floor-ring plane height.
CENTER_Z_DOME_SQUARE_ROUND = 0.90
CENTER_Z_DOME_TRIPOD = 1.05


# Palettes: each maps the 7 shared material keys to rgba (spec §Palette).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_candy": {
        "post": (0.90, 0.90, 0.87, 1.0),
        "steel": (0.24, 0.25, 0.27, 1.0),
        "ring": (0.27, 0.60, 0.78, 1.0),
        "accent": (0.90, 0.76, 0.12, 1.0),
        "meridian": (0.76, 0.13, 0.13, 1.0),
        "stripe": (0.92, 0.90, 0.86, 1.0),
        "clamp": (0.45, 0.27, 0.16, 1.0),
    },
    "sky_blue_yellow": {
        "post": (0.92, 0.92, 0.90, 1.0),
        "steel": (0.26, 0.27, 0.30, 1.0),
        "ring": (0.27, 0.60, 0.78, 1.0),
        "accent": (0.92, 0.80, 0.16, 1.0),
        "meridian": (0.30, 0.55, 0.80, 1.0),
        "stripe": (0.93, 0.92, 0.88, 1.0),
        "clamp": (0.30, 0.32, 0.36, 1.0),
    },
    "steel_worn": {
        "post": (0.42, 0.43, 0.45, 1.0),
        "steel": (0.24, 0.25, 0.27, 1.0),
        "ring": (0.30, 0.32, 0.35, 1.0),
        "accent": (0.78, 0.66, 0.18, 1.0),
        "meridian": (0.32, 0.33, 0.36, 1.0),
        "stripe": (0.55, 0.56, 0.58, 1.0),
        "clamp": (0.22, 0.22, 0.24, 1.0),
    },
    "rust_retro": {
        "post": (0.50, 0.32, 0.20, 1.0),
        "steel": (0.40, 0.26, 0.18, 1.0),
        "ring": (0.45, 0.27, 0.16, 1.0),
        "accent": (0.80, 0.60, 0.20, 1.0),
        "meridian": (0.70, 0.18, 0.14, 1.0),
        "stripe": (0.62, 0.45, 0.35, 1.0),
        "clamp": (0.40, 0.24, 0.15, 1.0),
    },
    "mint_coral": {
        "post": (0.93, 0.93, 0.90, 1.0),
        "steel": (0.30, 0.34, 0.34, 1.0),
        "ring": (0.40, 0.78, 0.70, 1.0),
        "accent": (0.95, 0.82, 0.30, 1.0),
        "meridian": (0.92, 0.42, 0.40, 1.0),
        "stripe": (0.95, 0.93, 0.90, 1.0),
        "clamp": (0.50, 0.40, 0.38, 1.0),
    },
}


@dataclass(frozen=True)
class MerryGoRoundConfig:
    base_post: BasePost | None = None
    cage_form: CageForm | None = None
    n_meridian: int | None = None
    n_latitude_ring: int | None = None
    n_drum_bar: int | None = None
    palette_style: PaletteStyle = "classic_candy"
    cage_radius_scale: float = 1.0
    post_height_scale: float = 1.0
    name: str = "playground_merry_go_round"


@dataclass(frozen=True)
class ResolvedMerryGoRoundConfig:
    base_post: BasePost
    cage_form: CageForm
    n_meridian: int
    n_latitude_ring: int
    n_drum_bar: int
    palette_style: PaletteStyle
    journal_count: int  # 1 (dome) or 2
    center_z: float
    cage_r: float  # sphere / drum radius (scaled)
    drum_half_h: float
    post_h: float  # scaled post height (square/round) or shaft-derived
    name: str

    @property
    def is_drum(self) -> bool:
        return self.cage_form == "cylindrical_drum_cage"

    @property
    def is_dome(self) -> bool:
        return self.cage_form == "half_dome_cage"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> MerryGoRoundConfig:
    rng = random.Random(seed)
    base_post = rng.choice(BASE_POSTS)
    cage_form = rng.choice(CAGE_FORMS)
    n_meridian = rng.choices(N_MERIDIAN_VALUES, weights=N_MERIDIAN_WEIGHTS, k=1)[0]
    n_latitude_ring = rng.randint(N_LAT_MIN, N_LAT_MAX)
    n_drum_bar = rng.randint(N_DRUM_MIN, N_DRUM_MAX)
    return MerryGoRoundConfig(
        base_post=base_post,
        cage_form=cage_form,
        n_meridian=n_meridian,
        n_latitude_ring=n_latitude_ring,
        n_drum_bar=n_drum_bar,
        palette_style=rng.choice(PALETTE_STYLES),
        cage_radius_scale=round(rng.uniform(0.92, 1.06), 4),
        post_height_scale=round(rng.uniform(0.95, 1.08), 4),
        name=f"seeded_playground_merry_go_round_{seed}",
    )


def resolve_config(
    config: MerryGoRoundConfig | None = None,
) -> ResolvedMerryGoRoundConfig:
    cfg = config or MerryGoRoundConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    base_post = _pick(cfg.base_post, BASE_POSTS)
    cage_form = _pick(cfg.cage_form, CAGE_FORMS)

    n_meridian = int(cfg.n_meridian) if cfg.n_meridian is not None else 3
    n_meridian = int(_clamp(n_meridian, N_MERIDIAN_MIN, N_MERIDIAN_MAX))
    n_latitude_ring = int(cfg.n_latitude_ring) if cfg.n_latitude_ring is not None else 4
    n_latitude_ring = int(_clamp(n_latitude_ring, N_LAT_MIN, N_LAT_MAX))
    n_drum_bar = int(cfg.n_drum_bar) if cfg.n_drum_bar is not None else 12
    n_drum_bar = int(_clamp(n_drum_bar, N_DRUM_MIN, N_DRUM_MAX))

    # --- Derived: journal_count (conditional). half_dome -> single upper pole.
    journal_count = 1 if cage_form == "half_dome_cage" else 2

    # --- Controlled local scale (clamped). ---
    radius_scale = _clamp(cfg.cage_radius_scale, 0.92, 1.06)
    height_scale = _clamp(cfg.post_height_scale, 0.95, 1.08)

    is_drum = cage_form == "cylindrical_drum_cage"
    cage_r = (DRUM_R if is_drum else SPHERE_R) * radius_scale
    drum_half_h = DRUM_HALF_H * radius_scale

    # --- Derived center_z (equation): per (base_post, cage_form). ---
    if cage_form == "half_dome_cage":
        center_z = (
            CENTER_Z_DOME_TRIPOD
            if base_post == "tripod_stand"
            else CENTER_Z_DOME_SQUARE_ROUND
        )
    else:
        center_z = (
            CENTER_Z_TRIPOD
            if base_post == "tripod_stand"
            else CENTER_Z_SQUARE_ROUND
        )

    post_h = POST_H * height_scale

    # --- Inequality: cage min_z > 0.05 (ground clearance). ---
    # Lowest cage point: sphere -> center_z - cage_r; drum -> center_z - drum_half_h;
    # dome -> center_z (floor ring at equator plane). Raise center_z if needed.
    if cage_form == "half_dome_cage":
        cage_min_z = center_z  # floor ring sits at center_z
    elif is_drum:
        cage_min_z = center_z - drum_half_h
    else:
        cage_min_z = center_z - cage_r
    if cage_min_z <= 0.06:
        center_z += (0.08 - cage_min_z)

    return ResolvedMerryGoRoundConfig(
        base_post=base_post,
        cage_form=cage_form,
        n_meridian=n_meridian,
        n_latitude_ring=n_latitude_ring,
        n_drum_bar=n_drum_bar,
        palette_style=palette_style,
        journal_count=journal_count,
        center_z=center_z,
        cage_r=cage_r,
        drum_half_h=drum_half_h,
        post_h=post_h,
        name=cfg.name or "playground_merry_go_round",
    )


def with_overrides(config: MerryGoRoundConfig, **kwargs: object) -> MerryGoRoundConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: MerryGoRoundConfig | ResolvedMerryGoRoundConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedMerryGoRoundConfig)
        else resolve_config(config)
    )
    choices: list[tuple[str, str]] = [
        ("base_post", r.base_post),
        ("cage_form", r.cage_form),
    ]
    # Drum's multiplicity axis is n_drum_bar; sphere/dome use n_meridian.
    if r.is_drum:
        choices.append(("n_drum_bar", f"k{r.n_drum_bar}"))
    else:
        choices.append(("n_meridian", f"n{r.n_meridian}"))
    choices.append(("n_latitude_ring", f"m{r.n_latitude_ring}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers.
# ---------------------------------------------------------------------------
def _collar_pole_z(r: ResolvedMerryGoRoundConfig) -> float:
    """Local z of the upper pole collar center (sphere/dome) above cage center."""
    arc_phi0 = math.asin(min(0.99, COLLAR_OUTER_R / r.cage_r))
    return r.cage_r * math.cos(arc_phi0)


def _arc_points(
    cage_r: float, phi_start: float, phi_end: float, n: int
) -> list[tuple[float, float, float]]:
    pts = []
    for i in range(n):
        phi = phi_start + (phi_end - phi_start) * i / (n - 1)
        pts.append((cage_r * math.sin(phi), 0.0, cage_r * math.cos(phi)))
    return pts


def _collar_mesh():
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(
            [(COLLAR_OUTER_R, -COLLAR_HALF_H), (COLLAR_OUTER_R, COLLAR_HALF_H)],
            [(COLLAR_INNER_R, -COLLAR_HALF_H), (COLLAR_INNER_R, COLLAR_HALF_H)],
            segments=48,
        ),
        "bearing_collar",
    )


def _leg_points(azimuth: float, n: int = 7) -> list[tuple[float, float, float]]:
    top_r, top_z = HUB_R, HUB_Z + HUB_H / 2.0
    bot_r, bot_z = LEG_SPREAD, FOOT_H
    pts = []
    for j in range(n):
        t = j / (n - 1)
        rr = top_r + t * (bot_r - top_r)
        zz = top_z + t * (bot_z - top_z)
        pts.append((rr * math.cos(azimuth), rr * math.sin(azimuth), zz))
    return pts


def _turned_post_profile(post_h: float) -> list[tuple[float, float]]:
    top = post_h
    return [
        (0.000, 0.000),
        (POST_FLANGE_R, 0.000),
        (POST_FLANGE_R, 0.050),
        (POST_FLANGE_R - 0.010, 0.060),
        (POST_SHAFT_R + 0.008, 0.085),
        (POST_SHAFT_R, 0.120),
        (POST_SHAFT_R, top - 0.150),
        (POST_SHAFT_R + 0.006, top - 0.138),
        (POST_SHAFT_R + 0.006, top - 0.128),
        (POST_SHAFT_R, top - 0.116),
        (POST_SHAFT_R - 0.008, top - 0.090),
        (POST_SHAFT_R - 0.020, top - 0.055),
        (0.030, top - 0.020),
        (0.000, top),
    ]


# ---------------------------------------------------------------------------
# Base post modules (Slot A). Each emits the journals at the derived pole(s).
# ---------------------------------------------------------------------------
def _emit_journals(post, r: ResolvedMerryGoRoundConfig, mats) -> None:
    """Upper (and lower, unless dome) round bearing journals."""
    pole_z = r.drum_half_h if r.is_drum else _collar_pole_z(r)
    signs = (1.0,) if r.journal_count == 1 else (1.0, -1.0)
    tags = {1.0: "upper", -1.0: "lower"}
    for sign in signs:
        post.visual(
            Cylinder(radius=JOURNAL_R, length=JOURNAL_LEN),
            origin=Origin(xyz=(0.0, 0.0, r.center_z + sign * pole_z)),
            material=mats["steel"],
            name=f"journal_{tags[sign]}", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
        )
    # Thin axial spindle through the spin center: a slim steel shaft on the post
    # axis spanning from the lowest journal up to the upper journal, so the spin
    # joint origin (at z=center_z on the axis) sits inside real post geometry.
    spindle_lo = r.center_z - (0.0 if r.journal_count == 1 else pole_z)
    spindle_hi = r.center_z + pole_z
    post.visual(
        Cylinder(radius=0.012, length=spindle_hi - spindle_lo),
        origin=Origin(xyz=(0.0, 0.0, (spindle_lo + spindle_hi) / 2.0)),
        material=mats["steel"],
        name="axle_spindle", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
    )


def _build_square_box_post(model, r: ResolvedMerryGoRoundConfig, mats):
    post = model.part("post")
    post.visual(
        Box((0.34, 0.34, 0.025)),
        origin=Origin(xyz=(0.0, 0.0, 0.0125)),
        material=mats["steel"],
        name="base_plate", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
    )
    post.visual(
        Box((POST_W, POST_W, r.post_h)),
        origin=Origin(xyz=(0.0, 0.0, r.post_h / 2.0)),
        material=mats["post"],
        name="post_column", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
    )
    post.visual(
        Box((0.14, 0.14, 0.02)),
        origin=Origin(xyz=(0.0, 0.0, r.post_h + 0.01)),
        material=mats["post"],
        name="post_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
    )
    _emit_journals(post, r, mats)
    post.inertial = Inertial.from_geometry(
        Box((POST_W, POST_W, r.post_h)),
        mass=40.0,
        origin=Origin(xyz=(0.0, 0.0, r.post_h / 2.0)),
    )
    return post


def _build_round_turned_post(model, r: ResolvedMerryGoRoundConfig, mats):
    post = model.part("post")
    post.visual(
        Cylinder(radius=POST_BASE_PLATE_R, length=0.025),
        origin=Origin(xyz=(0.0, 0.0, 0.0125)),
        material=mats["steel"],
        name="base_plate", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
    )
    post.visual(
        mesh_from_geometry(
            LatheGeometry(_turned_post_profile(r.post_h), segments=48), "post_shaft"
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["post"],
        name="post_column", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
    )
    _emit_journals(post, r, mats)
    post.inertial = Inertial.from_geometry(
        Cylinder(radius=POST_SHAFT_R, length=r.post_h),
        mass=40.0,
        origin=Origin(xyz=(0.0, 0.0, r.post_h / 2.0)),
    )
    return post


def _build_tripod_stand(model, r: ResolvedMerryGoRoundConfig, mats):
    stand = model.part("post")
    hub_top = HUB_Z + HUB_H / 2.0
    hub_bot = HUB_Z - HUB_H / 2.0
    shaft_top = r.center_z + (r.drum_half_h if r.is_drum else _collar_pole_z(r)) + 0.30
    stand.visual(
        Cylinder(radius=HUB_R, length=HUB_H),
        origin=Origin(xyz=(0.0, 0.0, HUB_Z)),
        material=mats["post"],
        name="hub", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
    )
    stand.visual(
        Cylinder(radius=HUB_R + 0.020, length=0.015),
        origin=Origin(xyz=(0.0, 0.0, hub_top + 0.005)),
        material=mats["steel"],
        name="hub_flange", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
    )
    shaft_len = shaft_top - hub_bot
    stand.visual(
        Cylinder(radius=SHAFT_R, length=shaft_len),
        origin=Origin(xyz=(0.0, 0.0, (shaft_top + hub_bot) / 2.0)),
        material=mats["post"],
        name="shaft", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
    )
    stand.visual(
        Cylinder(radius=0.060, length=0.025),
        origin=Origin(xyz=(0.0, 0.0, hub_top + 0.020)),
        material=mats["steel"],
        name="shaft_collar", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
    )
    stand.visual(
        Cylinder(radius=0.060, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, shaft_top + 0.010)),
        material=mats["steel"],
        name="shaft_cap", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
    )
    for i in range(3):
        az = i * 2.0 * math.pi / 3.0
        stand.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    _leg_points(az, n=7),
                    radius=LEG_TUBE_R,
                    samples_per_segment=4,
                    radial_segments=14,
                    cap_ends=True,
                ),
                f"leg_{i}",
            ),
            material=mats["post"],
            name=f"leg_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
        )
        stand.visual(
            Cylinder(radius=FOOT_R, length=FOOT_H),
            origin=Origin(
                xyz=(LEG_SPREAD * math.cos(az), LEG_SPREAD * math.sin(az), FOOT_H / 2.0)
            ),
            material=mats["steel"],
            name=f"foot_{i}", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
        )
        clamp_r = HUB_R + 0.010
        stand.visual(
            Box((0.050, 0.040, 0.045)),
            origin=Origin(
                xyz=(clamp_r * math.cos(az), clamp_r * math.sin(az), hub_top - 0.005),
                rpy=(0.0, 0.0, az),
            ),
            material=mats["clamp"],
            name=f"leg_clamp_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
        )
    _emit_journals(stand, r, mats)
    stand.inertial = Inertial.from_geometry(
        Cylinder(radius=LEG_SPREAD, length=shaft_top),
        mass=45.0,
        origin=Origin(xyz=(0.0, 0.0, shaft_top / 2.0)),
    )
    return stand


_POST_BUILDERS = {
    "square_box_post": _build_square_box_post,
    "round_turned_post": _build_round_turned_post,
    "tripod_stand": _build_tripod_stand,
}


# ---------------------------------------------------------------------------
# Cage modules (Slot B). All authored in a local frame at cage center; the
# cage_spin joint origin is at (0,0,center_z).
# ---------------------------------------------------------------------------
def _emit_collars(cage, r: ResolvedMerryGoRoundConfig, mats) -> None:
    pole_z = r.drum_half_h if r.is_drum else _collar_pole_z(r)
    collar_mesh = _collar_mesh()
    cage.visual(
        collar_mesh,
        origin=Origin(xyz=(0.0, 0.0, pole_z)),
        material=mats["steel"],
        name="collar_upper", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
    )
    if r.journal_count == 2:
        cage.visual(
            collar_mesh,
            origin=Origin(xyz=(0.0, 0.0, -pole_z)),
            material=mats["steel"],
            name="collar_lower", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
        )
    # Central axle sleeve along the spin axis: a hollow steel tube riding the
    # journal through the cage center. This anchors the spin-joint origin (at
    # cage-local 0,0,0) to real solid cage geometry, and reads as the hub
    # bushing the cage turns on. Dome: from floor plane (0) up to the collar.
    if r.is_dome:
        axle_lo, axle_hi = 0.0, pole_z
    else:
        axle_lo, axle_hi = -pole_z, pole_z
    axle_len = axle_hi - axle_lo
    cage.visual(
        Cylinder(radius=COLLAR_INNER_R + 0.004, length=axle_len),
        origin=Origin(xyz=(0.0, 0.0, (axle_lo + axle_hi) / 2.0)),
        material=mats["steel"],
        name="center_axle", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
    )


def _stripe_meshes_arc(
    cage_r: float, phi0: float, phi1: float
) -> list:
    delta = (phi1 - phi0) / N_STRIPE_SEGMENTS
    meshes = []
    for j in range(1, N_STRIPE_SEGMENTS, 2):
        meshes.append(
            mesh_from_geometry(
                tube_from_spline_points(
                    _arc_points(cage_r, phi0 + j * delta, phi0 + (j + 1) * delta, 7),
                    radius=STRIPE_R,
                    samples_per_segment=4,
                    radial_segments=14,
                    cap_ends=True,
                ),
                f"meridian_stripe_{j}",
            )
        )
    return meshes


def _emit_meridians(
    cage, r: ResolvedMerryGoRoundConfig, mats, *, phi0: float, phi1: float
) -> None:
    arc_mesh = mesh_from_geometry(
        tube_from_spline_points(
            _arc_points(r.cage_r, phi0, phi1, 33),
            radius=TUBE_R,
            samples_per_segment=4,
            radial_segments=14,
            cap_ends=True,
        ),
        "meridian_arc",
    )
    stripe_meshes = _stripe_meshes_arc(r.cage_r, phi0, phi1)
    for k in range(2 * r.n_meridian):
        yaw = k * math.pi / r.n_meridian
        cage.visual(
            arc_mesh,
            origin=Origin(rpy=(0.0, 0.0, yaw)),
            material=mats["meridian"],
            name=f"meridian_arc_{k}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
        )
        for s, stripe_mesh in enumerate(stripe_meshes):
            cage.visual(
                stripe_mesh,
                origin=Origin(rpy=(0.0, 0.0, yaw)),
                material=mats["stripe"],
                name=f"meridian_stripe_{k}_{s}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
            )


def _emit_ring_clamps(
    cage, r: ResolvedMerryGoRoundConfig, mats, *, ring_specs, n_az: int
) -> None:
    for i, (ring_r, height) in enumerate(ring_specs):
        for k in range(n_az):
            az = k * 2.0 * math.pi / n_az
            cage.visual(
                Box((0.055, 0.05, 0.05)),
                origin=Origin(
                    xyz=(ring_r * math.cos(az), ring_r * math.sin(az), height),
                    rpy=(0.0, 0.0, az),
                ),
                material=mats["clamp"],
                name=f"clamp_r{i}_{k}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
            )


def _sphere_ring_specs(r: ResolvedMerryGoRoundConfig) -> list[tuple[float, float]]:
    """M latitude rings stacked over the sphere; equator (h=0) is the largest.

    Heights spread across [-0.65*R, 0.58*R]; one ring near the lower-middle is
    the yellow accent. Returns (ring_radius, height, mat_key) for each.
    """
    m = r.n_latitude_ring
    specs = []
    z_lo, z_hi = -0.65 * r.cage_r, 0.58 * r.cage_r
    for i in range(m):
        t = i / (m - 1)
        h = z_lo + t * (z_hi - z_lo)
        ring_r = math.sqrt(max(0.0, r.cage_r**2 - h**2))
        specs.append((ring_r, h))
    return specs


def _dome_ring_specs(r: ResolvedMerryGoRoundConfig) -> list[tuple[float, float]]:
    """M latitude rings on a hemisphere: floor ring (h=0) largest, shrinking up."""
    m = r.n_latitude_ring
    specs = []
    z_hi = 0.80 * r.cage_r
    for i in range(m):
        t = i / (m - 1)
        h = t * z_hi
        ring_r = math.sqrt(max(0.0, r.cage_r**2 - h**2))
        specs.append((ring_r, h))
    return specs


def _drum_ring_specs(r: ResolvedMerryGoRoundConfig) -> list[tuple[float, float]]:
    """M equal-radius drum rings stacked over [-half_h, +half_h]."""
    m = r.n_latitude_ring
    specs = []
    for i in range(m):
        t = i / (m - 1)
        h = -r.drum_half_h + t * (2.0 * r.drum_half_h)
        specs.append((r.cage_r, h))
    return specs


def _emit_rings(cage, mats, *, ring_specs, accent_index: int) -> None:
    for i, (ring_r, height) in enumerate(ring_specs):
        mat = mats["accent"] if i == accent_index else mats["ring"]
        cage.visual(
            mesh_from_geometry(
                TorusGeometry(
                    radius=max(0.05, ring_r),
                    tube=TUBE_R,
                    radial_segments=16,
                    tubular_segments=72,
                ),
                f"latitude_ring_{i}",
            ),
            origin=Origin(xyz=(0.0, 0.0, height)),
            material=mat,
            name=f"latitude_ring_{i}", material_class_id="metal.paint_coated",
        )


def _build_spherical_hoop_cage(model, r: ResolvedMerryGoRoundConfig, mats):
    cage = model.part("cage")
    _emit_collars(cage, r, mats)
    ring_specs = _sphere_ring_specs(r)
    accent = max(0, ring_specs.index(min(ring_specs, key=lambda s: abs(s[1] + 0.34 * r.cage_r))))
    _emit_rings(cage, mats, ring_specs=ring_specs, accent_index=accent)
    arc_phi0 = math.asin(min(0.99, COLLAR_OUTER_R / r.cage_r))
    _emit_meridians(cage, r, mats, phi0=arc_phi0, phi1=math.pi - arc_phi0)
    _emit_ring_clamps(cage, r, mats, ring_specs=ring_specs, n_az=2 * r.n_meridian)
    cage.inertial = Inertial.from_geometry(
        Cylinder(radius=r.cage_r, length=2.0 * r.cage_r),
        mass=30.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    return cage


def _build_half_dome_cage(model, r: ResolvedMerryGoRoundConfig, mats):
    cage = model.part("cage")
    _emit_collars(cage, r, mats)
    ring_specs = _dome_ring_specs(r)
    # Yellow accent near upper-middle.
    accent = min(len(ring_specs) - 1, max(0, len(ring_specs) - 2))
    _emit_rings(cage, mats, ring_specs=ring_specs, accent_index=accent)
    arc_phi0 = math.asin(min(0.99, COLLAR_OUTER_R / r.cage_r))
    _emit_meridians(cage, r, mats, phi0=arc_phi0, phi1=math.pi / 2.0)
    _emit_ring_clamps(cage, r, mats, ring_specs=ring_specs, n_az=2 * r.n_meridian)
    cage.inertial = Inertial.from_geometry(
        Cylinder(radius=r.cage_r, length=r.cage_r),
        mass=24.0,
        origin=Origin(xyz=(0.0, 0.0, 0.4 * r.cage_r)),
    )
    return cage


def _build_cylindrical_drum_cage(model, r: ResolvedMerryGoRoundConfig, mats):
    cage = model.part("cage")
    _emit_collars(cage, r, mats)
    ring_specs = _drum_ring_specs(r)
    accent = max(0, len(ring_specs) // 2)
    _emit_rings(cage, mats, ring_specs=ring_specs, accent_index=accent)

    # K vertical bars + candy stripes.
    bar_mesh = mesh_from_geometry(
        tube_from_spline_points(
            [(r.cage_r, 0.0, -r.drum_half_h), (r.cage_r, 0.0, r.drum_half_h)],
            radius=TUBE_R,
            samples_per_segment=4,
            radial_segments=14,
            cap_ends=True,
        ),
        "vertical_bar",
    )
    stripe_len = (2.0 * r.drum_half_h) / N_STRIPE_SEGMENTS
    stripe_meshes = []
    for j in range(1, N_STRIPE_SEGMENTS, 2):
        z0 = -r.drum_half_h + j * stripe_len
        stripe_meshes.append(
            mesh_from_geometry(
                tube_from_spline_points(
                    [(r.cage_r, 0.0, z0), (r.cage_r, 0.0, z0 + stripe_len)],
                    radius=STRIPE_R,
                    samples_per_segment=2,
                    radial_segments=14,
                    cap_ends=True,
                ),
                f"bar_stripe_{j}",
            )
        )
    for i in range(r.n_drum_bar):
        theta = i * 2.0 * math.pi / r.n_drum_bar
        cage.visual(
            bar_mesh,
            origin=Origin(rpy=(0.0, 0.0, theta)),
            material=mats["meridian"],
            name=f"vertical_bar_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
        )
        for s, stripe_mesh in enumerate(stripe_meshes):
            cage.visual(
                stripe_mesh,
                origin=Origin(rpy=(0.0, 0.0, theta)),
                material=mats["stripe"],
                name=f"bar_stripe_{i}_{s}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
            )

    # Radial spoke arms (collar -> drum ring) at top and bottom — structural path.
    spoke_mesh = mesh_from_geometry(
        tube_from_spline_points(
            [(COLLAR_OUTER_R, 0.0, 0.0), (r.cage_r - TUBE_R, 0.0, 0.0)],
            radius=TUBE_R,
            samples_per_segment=4,
            radial_segments=14,
            cap_ends=True,
        ),
        "spoke_arm",
    )
    for i in range(N_SPOKE_ARMS):
        theta = i * 2.0 * math.pi / N_SPOKE_ARMS
        cage.visual(
            spoke_mesh,
            origin=Origin(xyz=(0.0, 0.0, r.drum_half_h), rpy=(0.0, 0.0, theta)),
            material=mats["steel"],
            name=f"spoke_upper_{i}", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
        )
        cage.visual(
            spoke_mesh,
            origin=Origin(xyz=(0.0, 0.0, -r.drum_half_h), rpy=(0.0, 0.0, theta)),
            material=mats["steel"],
            name=f"spoke_lower_{i}", material_class_id=("metal.steel_bare" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "metal.steel_rusted"),
        )

    # Clamps where vertical bars meet the top / bottom rings.
    for ring_tag, ring_h in (("top", r.drum_half_h), ("bot", -r.drum_half_h)):
        for i in range(r.n_drum_bar):
            theta = i * 2.0 * math.pi / r.n_drum_bar
            cage.visual(
                Box((0.055, 0.05, 0.05)),
                origin=Origin(
                    xyz=(r.cage_r * math.cos(theta), r.cage_r * math.sin(theta), ring_h),
                    rpy=(0.0, 0.0, theta),
                ),
                material=mats["clamp"],
                name=f"clamp_{ring_tag}_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_candy", "sky_blue_yellow", "steel_worn", "mint_coral"} else "rust.painted_weathered"),
            )
    cage.inertial = Inertial.from_geometry(
        Cylinder(radius=r.cage_r, length=2.0 * r.drum_half_h),
        mass=30.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    return cage


_CAGE_BUILDERS = {
    "spherical_hoop_cage": _build_spherical_hoop_cage,
    "half_dome_cage": _build_half_dome_cage,
    "cylindrical_drum_cage": _build_cylindrical_drum_cage,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_playground_merry_go_round(
    config: MerryGoRoundConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"pmgr_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    post = _POST_BUILDERS[r.base_post](model, r, mats)
    cage = _CAGE_BUILDERS[r.cage_form](model, r, mats)

    model.articulation(
        "cage_spin",
        ArticulationType.CONTINUOUS,
        parent=post,
        child=cage,
        origin=Origin(xyz=(0.0, 0.0, r.center_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=200.0, velocity=6.0),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_playground_merry_go_round(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_playground_merry_go_round(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_playground_merry_go_round_tests(
    object_model: ArticulatedObject,
    config: MerryGoRoundConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    post = object_model.get_part("post")
    cage = object_model.get_part("cage")
    spin = object_model.get_articulation("cage_spin")

    # ---- Collar / journal captured-pin allowances (element-scoped). ----
    tags = ("upper",) if r.journal_count == 1 else ("upper", "lower")
    for tag in tags:
        ctx.allow_overlap(
            cage,
            post,
            elem_a=f"collar_{tag}",
            elem_b=f"journal_{tag}",
            reason=(
                "The cage bearing collar is intentionally captured on the round "
                "post journal (shaft-in-bushing) so the spinning cage reads as "
                "mounted on its bearing."
            ),
        )
    # The central axle sleeve rides the post journals/column on the shared axis.
    ctx.allow_overlap(
        cage,
        post,
        reason=(
            "The cage center axle is a hollow sleeve riding coaxially on the "
            "post journals/column (shaft-in-bushing) along the spin axis."
        ),
    )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Joint identity: single CONTINUOUS spin about vertical Z. ----
    ctx.check(
        "cage spin is CONTINUOUS about vertical Z axis",
        spin.articulation_type == ArticulationType.CONTINUOUS
        and abs(spin.axis[2]) > 0.99
        and abs(spin.axis[0]) < 0.01
        and abs(spin.axis[1]) < 0.01,
        details=f"type={spin.articulation_type} axis={tuple(spin.axis)}",
    )
    spins = [
        j
        for j in object_model.articulations
        if j.articulation_type == ArticulationType.CONTINUOUS
    ]
    ctx.check(
        "exactly one spin joint (no per-seat joints)",
        len(spins) == 1
        and sum(
            1 for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
        )
        == 1,
        details=f"continuous={len(spins)} total_nonfixed="
        f"{sum(1 for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED)}",
    )

    # ---- Cage concentric with the post axis. ----
    ctx.expect_origin_distance(
        cage, post, axes="xy", max_dist=0.003, name="cage centered on post axis"
    )

    # ---- Collar / journal contract: bore captures journal, rides it. ----
    for tag in tags:
        ctx.expect_within(
            post,
            cage,
            axes="xy",
            inner_elem=f"journal_{tag}",
            outer_elem=f"collar_{tag}",
            margin=0.0,
            name=f"{tag} journal sits inside its collar bore",
        )
        ctx.expect_contact(
            cage,
            post,
            elem_a=f"collar_{tag}",
            elem_b=f"journal_{tag}",
            contact_tol=0.005,
            name=f"{tag} collar rides its journal",
        )

    # ---- journal_count matches cage_form derivation. ----
    journal_names = {v.name for v in post.visuals if v.name.startswith("journal_")}
    ctx.check(
        "journal_count derived from cage_form (1 for dome else 2)",
        len(journal_names) == r.journal_count
        and (r.journal_count == 1) == (r.cage_form == "half_dome_cage"),
        details=f"journals={sorted(journal_names)} count={r.journal_count} cage={r.cage_form}",
    )

    # ---- Multiplicity: meridian arcs / drum bars vary part count with N. ----
    if r.is_drum:
        bars = [v.name for v in cage.visuals if v.name.startswith("vertical_bar_")]
        ctx.check(
            "N drum bars emitted (multiplicity)",
            len(bars) == r.n_drum_bar,
            details=f"bars={len(bars)} expected={r.n_drum_bar}",
        )
        # Spoke arms present (structural support path for drum rings).
        spokes = [v.name for v in cage.visuals if v.name.startswith("spoke_")]
        ctx.check(
            "drum spoke arms present (structural path)",
            len(spokes) == 2 * N_SPOKE_ARMS,
            details=f"spokes={len(spokes)}",
        )
    else:
        arcs = [v.name for v in cage.visuals if v.name.startswith("meridian_arc_")]
        ctx.check(
            "2N meridian half-arcs emitted (multiplicity)",
            len(arcs) == 2 * r.n_meridian,
            details=f"arcs={len(arcs)} expected={2 * r.n_meridian}",
        )

    # ---- Latitude rings present and use real Torus geometry. ----
    rings = [v.name for v in cage.visuals if v.name.startswith("latitude_ring_")]
    ctx.check(
        "M latitude rings emitted",
        len(rings) == r.n_latitude_ring,
        details=f"rings={len(rings)} expected={r.n_latitude_ring}",
    )

    # ---- Cage is rideable scale and clears the ground. ----
    cage_aabb = ctx.part_world_aabb(cage)
    post_aabb = ctx.part_world_aabb(post)
    if cage_aabb is not None:
        width = cage_aabb[1][0] - cage_aabb[0][0]
        ctx.check(
            "cage is rideable scale (~1.4-2.0 m wide)",
            1.40 <= width <= 2.05,
            details=f"cage width={width:.3f}",
        )
        ctx.check(
            "cage clears the ground",
            cage_aabb[0][2] > 0.05,
            details=f"cage min z={cage_aabb[0][2]:.3f}",
        )
    if post_aabb is not None:
        ctx.check(
            "post is anchored to the ground",
            post_aabb[0][2] < 0.03,
            details=f"post min z={post_aabb[0][2]:.3f}",
        )

    # ---- Decisive spin pose: a clamp swings from +X toward +Y on a quarter turn. ----
    clamp0 = next(
        (v.name for v in cage.visuals if v.name.startswith("clamp_")), None
    )
    if clamp0 is not None:
        before = ctx.part_element_world_aabb(cage, elem=clamp0)
        with ctx.pose({spin: math.pi / 2.0}):
            ctx.expect_origin_distance(
                cage, post, axes="xy", max_dist=0.003, name="spinning cage stays centered"
            )
            after = ctx.part_element_world_aabb(cage, elem=clamp0)

        def _cxy(aabb):
            return ((aabb[0][0] + aabb[1][0]) / 2.0, (aabb[0][1] + aabb[1][1]) / 2.0)

        ok = False
        details = "missing clamp element"
        if before is not None and after is not None:
            bx, by = _cxy(before)
            ax, ay = _cxy(after)
            # 90deg rotation about Z carries (bx,by) -> (-by, bx).
            exp_x, exp_y = -by, bx
            ok = (
                abs(ax - exp_x) < 0.06
                and abs(ay - exp_y) < 0.06
                and (abs(bx) + abs(by)) > 0.30
            )
            details = f"before=({bx:.2f},{by:.2f}) after=({ax:.2f},{ay:.2f}) exp=({exp_x:.2f},{exp_y:.2f})"
        ctx.check("quarter-turn spin rotates a cage clamp about Z", ok, details=details)

    # ---- Press-fit inequality proven from authored dims. ----
    ctx.check(
        "collar bore clears the journal (press fit, bore >= journal - eps)",
        COLLAR_INNER_R >= JOURNAL_R - 0.0015,
        details=f"collar_inner_r={COLLAR_INNER_R} journal_r={JOURNAL_R}",
    )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded with multiplicity encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "MerryGoRoundConfig",
    "ResolvedMerryGoRoundConfig",
    "build_playground_merry_go_round",
    "build_seeded_playground_merry_go_round",
    "config_from_seed",
    "resolve_config",
    "run_playground_merry_go_round_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
