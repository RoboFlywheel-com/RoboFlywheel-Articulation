# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Source-backed studio-lamp family with adaptive head supports.

The runtime domain is the full Cartesian product documented by the SourceMap.
Head envelopes derive their yoke/fork geometry, and both multiplicities emit
real load-bearing geometry.  No source runtime is imported by this module.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    LatheGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
    tube_from_spline_points,
)

__modular__ = True

GroundSupport = Literal[
    "classic_hinged_tripod", "radial_tube_spider", "folding_braced_spider",
    "vintage_clevis_tripod", "rolling_caster_star", "weighted_disk",
]
MastProfile = Literal[
    "classic_black_nested_tubes", "boom_heavy_riser", "vintage_silver_drop_mast",
]
HeadSupportMechanism = Literal[
    "adaptive_direct_trunnion_yoke", "counterbalance_boom_fork",
    "compact_round_tube_u_yoke", "dual_axis_pan_u_yoke",
]
LampHeadAssembly = Literal[
    "portrait_softbox", "portrait_softbox_barn_doors", "landscape_softbox",
    "landscape_softbox_focus_ring", "round_beauty_dish", "led_panel",
    "fresnel_can", "vintage_spotlight_can",
]
Support = Literal["tripod", "rolling_base", "counterweighted_boom_base"]
HeadFamily = Literal[
    "softbox_rect",
    "round_reflector",
    "led_panel",
    "fresnel_can",
    "spotlight_can",
]
HeadModule = Literal["none", "focus_barrel", "barn_doors_4"]
PaletteStyle = Literal[
    "studio_black",
    "silver_industrial",
    "warm_brass",
    "cinema_grey",
    "arctic_white",
]

GROUND_SUPPORTS: tuple[GroundSupport, ...] = (
    "classic_hinged_tripod", "radial_tube_spider", "folding_braced_spider",
    "vintage_clevis_tripod", "rolling_caster_star", "weighted_disk",
)
MAST_PROFILES: tuple[MastProfile, ...] = (
    "classic_black_nested_tubes", "boom_heavy_riser", "vintage_silver_drop_mast",
)
HEAD_SUPPORT_MECHANISMS: tuple[HeadSupportMechanism, ...] = (
    "adaptive_direct_trunnion_yoke", "counterbalance_boom_fork",
    "compact_round_tube_u_yoke", "dual_axis_pan_u_yoke",
)
LAMP_HEAD_ASSEMBLIES: tuple[LampHeadAssembly, ...] = (
    "portrait_softbox", "portrait_softbox_barn_doors", "landscape_softbox",
    "landscape_softbox_focus_ring", "round_beauty_dish", "led_panel",
    "fresnel_can", "vintage_spotlight_can",
)
TEMPLATE_DOMAIN = TemplateDomain(slots=(
    component_slot("ground_support", GROUND_SUPPORTS),
    component_slot("mast_profile", MAST_PROFILES),
    component_slot("head_support_mechanism", HEAD_SUPPORT_MECHANISMS),
    component_slot("lamp_head_assembly", LAMP_HEAD_ASSEMBLIES),
    multiplicity_slot(
        "radial_support_count",
        (3, 4, 5, 6, 7),
        item_slot="ground_support",
    ),
    multiplicity_slot(
        "mast_stage_count",
        (1, 2, 3),
        item_slot="mast_profile",
    ),
))

SUPPORTS: tuple[Support, ...] = ("tripod", "rolling_base", "counterweighted_boom_base")
HEAD_FAMILIES: tuple[HeadFamily, ...] = (
    "softbox_rect",
    "round_reflector",
    "led_panel",
    "fresnel_can",
    "spotlight_can",
)
HEAD_MODULES: tuple[HeadModule, ...] = ("none", "focus_barrel", "barn_doors_4")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "studio_black",
    "silver_industrial",
    "warm_brass",
    "cinema_grey",
    "arctic_white",
)

# head families whose front face is broadly planar/rimmed — barn doors need that.
BARN_DOOR_HEADS: tuple[HeadFamily, ...] = ("softbox_rect", "led_panel", "round_reflector")

MAST_COUNT_MIN = 1
MAST_COUNT_MAX = 3
MAST_COUNT_WEIGHTS = (0.30, 0.45, 0.25)

# 5 realistic colorways covering metal / painted / fabric / plastic.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "studio_black": {
        "body": (0.045, 0.048, 0.052, 1.0),
        "metal": (0.13, 0.14, 0.15, 1.0),
        "fabric": (0.020, 0.022, 0.026, 1.0),
        "diffuser": (0.96, 0.94, 0.88, 1.0),
        "lens": (0.86, 0.90, 0.94, 0.70),
        "rubber": (0.020, 0.020, 0.024, 1.0),
        "accent": (0.65, 0.66, 0.68, 1.0),
        "counterweight": (0.13, 0.14, 0.15, 1.0),
    },
    "silver_industrial": {
        "body": (0.72, 0.74, 0.76, 1.0),
        "metal": (0.86, 0.87, 0.88, 1.0),
        "fabric": (0.28, 0.30, 0.33, 1.0),
        "diffuser": (0.96, 0.96, 0.92, 1.0),
        "lens": (0.90, 0.94, 0.98, 0.75),
        "rubber": (0.03, 0.03, 0.035, 1.0),
        "accent": (0.12, 0.13, 0.14, 1.0),
        "counterweight": (0.30, 0.31, 0.32, 1.0),
    },
    "warm_brass": {
        "body": (0.20, 0.16, 0.11, 1.0),
        "metal": (0.78, 0.58, 0.30, 1.0),
        "fabric": (0.18, 0.14, 0.10, 1.0),
        "diffuser": (0.98, 0.88, 0.66, 1.0),
        "lens": (0.96, 0.86, 0.60, 0.72),
        "rubber": (0.04, 0.03, 0.02, 1.0),
        "accent": (0.86, 0.68, 0.38, 1.0),
        "counterweight": (0.28, 0.20, 0.11, 1.0),
    },
    "cinema_grey": {
        "body": (0.28, 0.30, 0.32, 1.0),
        "metal": (0.48, 0.50, 0.52, 1.0),
        "fabric": (0.10, 0.11, 0.12, 1.0),
        "diffuser": (0.92, 0.94, 0.96, 1.0),
        "lens": (0.85, 0.90, 0.94, 0.70),
        "rubber": (0.02, 0.02, 0.024, 1.0),
        "accent": (0.72, 0.74, 0.76, 1.0),
        "counterweight": (0.18, 0.19, 0.20, 1.0),
    },
    "arctic_white": {
        "body": (0.92, 0.93, 0.94, 1.0),
        "metal": (0.72, 0.74, 0.76, 1.0),
        "fabric": (0.86, 0.87, 0.88, 1.0),
        "diffuser": (0.98, 0.98, 0.98, 1.0),
        "lens": (0.90, 0.94, 0.98, 0.70),
        "rubber": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.36, 0.38, 0.40, 1.0),
        "counterweight": (0.40, 0.41, 0.42, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Baseline geometry constants (meters). Derived from the source records.
# ---------------------------------------------------------------------------
_BASE_HUB_R = 0.040
_BASE_HUB_H = 0.080

# Column: each stage is a hollow tube extruded along +Z from base of the stage.
_STAGE_TUBE_LEN = 0.70
_STAGE_OUTER_R_BASE = 0.019  # base outer tube
_STAGE_TAPER = 0.0025  # each stage shrinks by this in radius
_STAGE_TRAVEL = 0.14  # +/- range of the PRISMATIC per stage
_STAGE_INSERT_OVERLAP = 0.16  # how much the child sits back inside the parent

_YOKE_HEIGHT = 0.32
_YOKE_ARM_HALF_SPAN = 0.28
_YOKE_BEARING_R = 0.012
_YOKE_TRUNNION_HALF_LEN = 0.03  # half the trunnion length
_YOKE_SLEEVE_H = 0.036
_YOKE_MIN_HEAD_CLEAR_Z = 0.28  # min Z gap between top of sleeve and trunnion axis
_TRUNNION_SHAFT_R = 0.010  # head trunnion shaft radius shared with the heads
_MOUNT_GAP = 0.0005  # running clearance used at captured interfaces

_TRIPOD_LEG_RADIAL = 0.068  # hinge center radial (outside the tripod_hub)
_TRIPOD_LEG_LEN = 0.42
_TRIPOD_LEG_TIP_DROP = 0.20  # tip Z drop from hinge

_CASTER_ARM_LEN = 0.34
_CASTER_R = 0.036
_CASTER_YOKE_LEN = 0.06  # vertical yoke fork height between arm top and axle

_COUNTERWEIGHT_R_MIN = 0.20
_COUNTERWEIGHT_R_MAX = 0.50
_COUNTERWEIGHT_H = 0.045


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class StudioLampConfig:
    ground_support: GroundSupport = "classic_hinged_tripod"
    mast_profile: MastProfile = "classic_black_nested_tubes"
    head_support_mechanism: HeadSupportMechanism = "adaptive_direct_trunnion_yoke"
    lamp_head_assembly: LampHeadAssembly = "portrait_softbox"
    radial_support_count: int = 3
    mast_stage_count: int = 2
    column_length_scale: float = 1.0
    mast_travel_scale: float = 1.0
    head_scale: float = 1.0
    # Candidate-local physical dimensions.  Inactive candidates leave their
    # value unset; resolve_config supplies the source-faithful nominal.
    classic_tripod_leg_reach_m: float | None = None
    radial_spider_leg_reach_m: float | None = None
    folding_spider_leg_reach_m: float | None = None
    vintage_clevis_leg_reach_m: float | None = None
    rolling_caster_arm_length_m: float | None = None
    weighted_disk_radius_m: float | None = None
    seed: int = 0


# Public alias consumed by the check/corner harnesses (`_template.Config`).
Config = StudioLampConfig


@dataclass(frozen=True)
class ResolvedStudioLampConfig:
    ground_support: GroundSupport
    mast_profile: MastProfile
    head_support_mechanism: HeadSupportMechanism
    lamp_head_assembly: LampHeadAssembly
    radial_support_count: int
    mast_stage_count: int
    # Internal source-family routing retained to reuse geometry builders.
    support: Support
    head_family: HeadFamily
    head_module: HeadModule
    mast_count: int
    palette_style: PaletteStyle
    column_length_scale: float
    mast_travel_scale: float
    head_scale: float
    classic_tripod_leg_reach_m: float
    radial_spider_leg_reach_m: float
    folding_spider_leg_reach_m: float
    vintage_clevis_leg_reach_m: float
    rolling_caster_arm_length_m: float
    weighted_disk_radius_m: float
    seed: int

    # Derived
    stage_tube_len: float  # per-stage tube length
    stage_travel: float  # per-stage PRISMATIC half-range
    head_size: float  # nominal head "scale" of head_family
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _pick(value, choices, default):
    if value is None:
        return default
    return value if value in choices else default


def config_from_seed(seed: int) -> StudioLampConfig:
    rng = random.Random(seed)
    choices = TEMPLATE_DOMAIN.sample(rng)
    ground_support = choices["ground_support"]
    local_dimensions = {
        "classic_tripod_leg_reach_m": None,
        "radial_spider_leg_reach_m": None,
        "folding_spider_leg_reach_m": None,
        "vintage_clevis_leg_reach_m": None,
        "rolling_caster_arm_length_m": None,
        "weighted_disk_radius_m": None,
    }
    ranges = {
        "classic_hinged_tripod": ("classic_tripod_leg_reach_m", 0.45, 0.54),
        "radial_tube_spider": ("radial_spider_leg_reach_m", 0.53, 0.64),
        "folding_braced_spider": ("folding_spider_leg_reach_m", 0.53, 0.64),
        "vintage_clevis_tripod": ("vintage_clevis_leg_reach_m", 0.40, 0.47),
        "rolling_caster_star": ("rolling_caster_arm_length_m", 0.31, 0.37),
        "weighted_disk": ("weighted_disk_radius_m", _COUNTERWEIGHT_R_MIN, _COUNTERWEIGHT_R_MAX),
    }
    field_name, minimum, maximum = ranges[ground_support]
    local_dimensions[field_name] = round(rng.uniform(minimum, maximum), 4)
    return StudioLampConfig(
        ground_support=ground_support,
        mast_profile=choices["mast_profile"],
        head_support_mechanism=choices["head_support_mechanism"],
        lamp_head_assembly=choices["lamp_head_assembly"],
        radial_support_count=choices["radial_support_count"],
        mast_stage_count=choices["mast_stage_count"],
        column_length_scale=round(rng.uniform(0.88, 1.14), 4),
        mast_travel_scale=round(rng.uniform(0.82, 1.14), 4),
        head_scale=round(rng.uniform(0.88, 1.18), 4),
        **local_dimensions,
        seed=seed,
    )


def resolve_config(config: StudioLampConfig | None = None) -> ResolvedStudioLampConfig:
    cfg = config or StudioLampConfig()
    domain_values = {
        "ground_support": cfg.ground_support,
        "mast_profile": cfg.mast_profile,
        "head_support_mechanism": cfg.head_support_mechanism,
        "lamp_head_assembly": cfg.lamp_head_assembly,
        "radial_support_count": cfg.radial_support_count,
        "mast_stage_count": cfg.mast_stage_count,
    }
    TEMPLATE_DOMAIN.validate(domain_values)
    support: Support = (
        "rolling_base" if cfg.ground_support == "rolling_caster_star"
        else "counterweighted_boom_base" if cfg.ground_support == "weighted_disk"
        else "tripod"
    )
    head_map = {
        "portrait_softbox": ("softbox_rect", "none"),
        "portrait_softbox_barn_doors": ("softbox_rect", "barn_doors_4"),
        "landscape_softbox": ("softbox_rect", "none"),
        "landscape_softbox_focus_ring": ("softbox_rect", "focus_barrel"),
        "round_beauty_dish": ("round_reflector", "none"),
        "led_panel": ("led_panel", "none"),
        "fresnel_can": ("fresnel_can", "none"),
        "vintage_spotlight_can": ("spotlight_can", "none"),
    }
    head_family, head_module = head_map[cfg.lamp_head_assembly]
    mast_count = cfg.mast_stage_count
    palette_style: PaletteStyle = (
        "silver_industrial" if cfg.lamp_head_assembly == "vintage_spotlight_can"
        or cfg.mast_profile == "vintage_silver_drop_mast"
        or cfg.ground_support == "vintage_clevis_tripod" else "studio_black"
    )

    col_scale = _clamp(cfg.column_length_scale, 0.85, 1.15)
    travel_scale = _clamp(cfg.mast_travel_scale, 0.80, 1.15)
    head_scale = _clamp(cfg.head_scale, 0.85, 1.20)
    classic_tripod_leg_reach_m = _clamp(
        cfg.classic_tripod_leg_reach_m if cfg.classic_tripod_leg_reach_m is not None else 0.490,
        0.45, 0.54,
    )
    radial_spider_leg_reach_m = _clamp(
        cfg.radial_spider_leg_reach_m if cfg.radial_spider_leg_reach_m is not None else 0.580,
        0.53, 0.64,
    )
    folding_spider_leg_reach_m = _clamp(
        cfg.folding_spider_leg_reach_m if cfg.folding_spider_leg_reach_m is not None else 0.580,
        0.53, 0.64,
    )
    vintage_clevis_leg_reach_m = _clamp(
        cfg.vintage_clevis_leg_reach_m if cfg.vintage_clevis_leg_reach_m is not None else 0.430,
        0.40, 0.47,
    )
    rolling_caster_arm_length_m = _clamp(
        cfg.rolling_caster_arm_length_m if cfg.rolling_caster_arm_length_m is not None else _CASTER_ARM_LEN,
        0.31, 0.37,
    )
    weighted_disk_radius_m = _clamp(
        cfg.weighted_disk_radius_m if cfg.weighted_disk_radius_m is not None else 0.35,
        _COUNTERWEIGHT_R_MIN, _COUNTERWEIGHT_R_MAX,
    )

    stage_tube_len = _STAGE_TUBE_LEN * col_scale
    # Keep travel <= 0.9 * (tube_len - insert_overlap) — assures deep insertion.
    max_travel = 0.9 * max(stage_tube_len - _STAGE_INSERT_OVERLAP, 0.10)
    stage_travel = min(_STAGE_TRAVEL * travel_scale, max_travel)

    palette = dict(PALETTES[palette_style])

    return ResolvedStudioLampConfig(
        ground_support=cfg.ground_support,
        mast_profile=cfg.mast_profile,
        head_support_mechanism=cfg.head_support_mechanism,
        lamp_head_assembly=cfg.lamp_head_assembly,
        radial_support_count=cfg.radial_support_count,
        mast_stage_count=cfg.mast_stage_count,
        support=support,
        head_family=head_family,
        head_module=head_module,
        mast_count=mast_count,
        palette_style=palette_style,
        column_length_scale=col_scale,
        mast_travel_scale=travel_scale,
        head_scale=head_scale,
        classic_tripod_leg_reach_m=classic_tripod_leg_reach_m,
        radial_spider_leg_reach_m=radial_spider_leg_reach_m,
        folding_spider_leg_reach_m=folding_spider_leg_reach_m,
        vintage_clevis_leg_reach_m=vintage_clevis_leg_reach_m,
        rolling_caster_arm_length_m=rolling_caster_arm_length_m,
        weighted_disk_radius_m=weighted_disk_radius_m,
        seed=int(cfg.seed),
        stage_tube_len=stage_tube_len,
        stage_travel=stage_travel,
        head_size=head_scale,
        palette=palette,
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def slot_choices_for_config(
    r: StudioLampConfig | ResolvedStudioLampConfig,
) -> tuple[tuple[str, str], ...]:
    # Structural candidate reporting intentionally excludes N multiplicities;
    # TemplateDomain reports those separately as radial/mast count coverage.
    return (
        ("ground_support", r.ground_support),
        ("mast_profile", r.mast_profile),
        ("head_support_mechanism", r.head_support_mechanism),
        ("lamp_head_assembly", r.lamp_head_assembly),
    )


# ---------------------------------------------------------------------------
# Material helpers
# ---------------------------------------------------------------------------
def _material_map(model: ArticulatedObject, r: ResolvedStudioLampConfig) -> dict[str, object]:
    mats: dict[str, object] = {}
    for key, rgba in r.palette.items():
        mats[key] = model.material(f"studio_lamp_{r.palette_style}_{key}", rgba=rgba)
    return mats


# ---------------------------------------------------------------------------
# Hollow tube helper (LatheGeometry — no cadquery boolean cost).
# ---------------------------------------------------------------------------
def _hollow_tube_geom(outer_r: float, inner_r: float, length: float, *, segments: int = 32):
    """Annular tube extruded along +Z from z=0 to z=length."""
    outer = [(outer_r, 0.0), (outer_r, length)]
    inner = [(inner_r, 0.0), (inner_r, length)]
    return LatheGeometry.from_shell_profiles(
        outer, inner, segments=segments, start_cap="flat", end_cap="flat"
    )


def _add_axis_joint(
    model, *, name, parent, child, point, axis, articulation_type, limits,
    consumer_axis=(1.0, 0.0, 0.0), radial=(0.0, 0.0, 1.0), consumer_radial=None,
):
    if abs(axis[2]) > 0.9 and radial == (0.0, 0.0, 1.0):
        radial = (0.0, 1.0, 0.0)
    provider = AxisInterface(
        name=f"{name}_provider", point=point, axis=axis, radial=radial
    )
    if consumer_radial is None:
        consumer_radial = (0.0, 1.0, 0.0) if abs(consumer_axis[2]) > 0.9 else (0.0, 0.0, 1.0)
    consumer = AxisInterface(
        name=f"{name}_consumer", axis=consumer_axis, radial=consumer_radial
    )
    mate = mate_axes(provider, consumer)
    joint = model.articulation(
        name, articulation_type, parent=parent, child=child,
        origin=mate.origin, axis=mate.axis, motion_limits=limits,
    )
    register_interface_mate(model, name, mate)
    return joint


# ---------------------------------------------------------------------------
# Support builders (Slot A)
# ---------------------------------------------------------------------------
def _add_support_column(
    base,
    r: ResolvedStudioLampConfig,
    mats,
    *,
    bottom_z: float,
    length_factor: float,
    tube_material: str = "metal",
    collar_material: str = "body",
    outer_r: float = _STAGE_OUTER_R_BASE,
) -> tuple[float, float]:
    """Add the source-family lower sleeve and return its top plane and radius."""
    col_len = r.stage_tube_len * length_factor
    base.visual(
        mesh_from_geometry(
            _hollow_tube_geom(outer_r, outer_r * 0.80, col_len, segments=28),
            "base_outer_tube",
        ),
        origin=Origin(xyz=(0.0, 0.0, bottom_z)),
        material=mats[tube_material],
        name="outer_tube", material_class_id="metal.paint_coated",
    )
    top_z = bottom_z + col_len
    base.visual(
        mesh_from_geometry(
            _hollow_tube_geom(outer_r * 1.45, outer_r * 0.96, 0.045, segments=24),
            "lower_clamp_collar_ring",
        ),
        origin=Origin(xyz=(0.0, 0.0, top_z - 0.045)),
        material=mats[collar_material],
        name="lower_clamp_collar", material_class_id="metal.paint_coated",
    )
    return top_z, outer_r


def _add_spline_tube(part, points, radius, material, name, mesh_name, *, samples=18, segments=18):
    part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                points,
                radius=radius,
                samples_per_segment=samples,
                radial_segments=segments,
                cap_ends=True,
            ),
            mesh_name,
        ),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _support_angle(index: int, count: int) -> float:
    return -math.pi / 2.0 + 2.0 * math.pi * index / count


def _build_support_classic_hinged_tripod(
    model: ArticulatedObject, r: ResolvedStudioLampConfig, mats
) -> tuple[float, float]:
    """Source 001: cast hub, short hinge links, curved legs, braces and ball feet."""
    base = model.part("base")
    hinge_z = 0.200
    hinge_radius = max(0.045, 0.0052 * r.radial_support_count + 0.018)
    # Captured hinge: the link tongue stops just outside the barrel with a
    # sub-millimetre running gap, so the pair stays in contact without
    # interpenetrating at any swing angle.
    link_half_w = 0.009
    link_half_h = 0.010
    link_len = 0.080
    link_clear = 0.0008
    barrel_outer_r = 0.014
    barrel_inner_r = 0.5 * barrel_outer_r
    barrel_half_len = 0.015
    base.visual(
        Cylinder(radius=0.030, length=0.100),
        origin=Origin(xyz=(0.0, 0.0, hinge_z)),
        material=mats["body"],
        name="tripod_hub", material_class_id="metal.paint_coated",
    )
    top_z, col_outer_r = _add_support_column(
        base, r, mats, bottom_z=hinge_z, length_factor=1.04,
        tube_material="body", collar_material="metal",
    )
    foot_r = 0.018
    leg_len = r.classic_tripod_leg_reach_m
    tip_drop = hinge_z - foot_r
    for idx in range(r.radial_support_count):
        ang = _support_angle(idx, r.radial_support_count)
        c, s = math.cos(ang), math.sin(ang)
        barrel_ring_inner = hinge_radius - barrel_outer_r
        if barrel_ring_inner > 0.030:
            # At N=7 the pitch-derived barrel circle moves 1.4 mm beyond the
            # cast hub.  A short shoulder closes only that gap and stops before
            # the moving hinge link.
            bridge_inner_r = 0.028
            bridge_outer_r = barrel_ring_inner + 0.002
            bridge_len = bridge_outer_r - bridge_inner_r
            bridge_mid = 0.5 * (bridge_inner_r + bridge_outer_r)
            base.visual(
                Box((bridge_len, 0.018, 0.018)),
                origin=Origin(
                    xyz=(bridge_mid * c, bridge_mid * s, hinge_z),
                    rpy=(0.0, 0.0, ang),
                ),
                material=mats["body"],
                name=f"hinge_bridge_{idx}", material_class_id="metal.paint_coated",
            )
        base.visual(
            mesh_from_geometry(
                _hollow_tube_geom(
                    barrel_outer_r, barrel_inner_r, 2.0 * barrel_half_len, segments=24,
                ),
                f"classic_hinge_barrel_{idx}",
            ),
            origin=Origin(
                xyz=(
                    hinge_radius * c + barrel_half_len * s,
                    hinge_radius * s - barrel_half_len * c,
                    hinge_z,
                ),
                rpy=(-math.pi / 2.0, 0.0, ang),
            ),
            material=mats["body"],
            name=f"hinge_barrel_{idx}", material_class_id="metal.paint_coated",
        )
        leg = model.part(f"leg_{idx}")
        # The link tongue starts just outside the barrel surface (running gap
        # ``link_clear``), keeping the leg in contact with the hinge without
        # penetrating the barrel at any swing angle.
        leg.visual(
            Box((link_len, 2.0 * link_half_w, 2.0 * link_half_h)),
            origin=Origin(xyz=(barrel_outer_r + link_clear + 0.5 * link_len, 0.0, 0.0)),
            material=mats["body"],
            name="hinge_link", material_class_id="metal.paint_coated",
        )
        _add_spline_tube(
            leg,
            [
                (0.075, 0.0, -0.004),
                (leg_len * 0.50, 0.0, -tip_drop * 0.35),
                (leg_len, 0.0, -tip_drop),
            ],
            0.011, mats["body"], "leg_tube", f"classic_tripod_leg_{idx}",
            samples=18, segments=20,
        )
        _add_spline_tube(
            leg,
            [
                (leg_len * 0.32, 0.0, -tip_drop * 0.20),
                (0.105, 0.0, 0.018),
                (0.055, 0.0, 0.083),
            ],
            0.006, mats["metal"], "support_brace", f"classic_tripod_brace_{idx}",
            samples=14, segments=16,
        )
        leg.visual(
            Sphere(radius=foot_r),
            origin=Origin(xyz=(leg_len, 0.0, -tip_drop)),
            material=mats["rubber"],
            name="rubber_foot", material_class_id="rubber.smooth_plain",
        )
        _add_axis_joint(
            model, name=f"base_to_leg_{idx}", parent=base, child=leg,
            point=(hinge_radius * c, hinge_radius * s, hinge_z),
            axis=(-s, c, 0.0), articulation_type=ArticulationType.REVOLUTE,
            consumer_axis=(0.0, 1.0, 0.0),
            limits=MotionLimits(effort=30.0, velocity=1.5, lower=-0.72, upper=0.05),
        )
    return top_z, col_outer_r


def _build_support_radial_tube_spider(
    model: ArticulatedObject, r: ResolvedStudioLampConfig, mats
) -> tuple[float, float]:
    """Source 002: low socket with long shallow-curved hinged radial tubes."""
    base = model.part("base")
    hinge_z = 0.205
    # The source 67 mm pin circle already has enough tangential capacity for N=7
    # (about 60 mm pitch), so increasing it would disconnect the pin bosses.
    hinge_radius = 0.067
    # Pin-and-sleeve hinge: the base lug rides on the joint axis and the leg's
    # hollow sleeve wraps it with a sub-millimetre running clearance.
    lug_r = 0.008
    sleeve_clear = 0.0008
    sleeve_inner_r = lug_r + sleeve_clear
    sleeve_outer_r = 0.0115
    sleeve_half_len = 0.009
    sleeve_len = 2.0 * sleeve_half_len
    # The lug pin protrudes past each sleeve end so a base arm can grip it
    # clear of the sleeve and embed into the hub (within-part connectivity).
    lug_half_len = sleeve_half_len + 0.009
    tube_r = 0.0105
    # Start the tube just outside the lug surface (cross-part running gap)
    # but embedded in the sleeve wall, so sleeve and leg tube stay one piece.
    tube_start_x = lug_r + 0.002
    base.visual(
        Cylinder(radius=0.055, length=0.100),
        origin=Origin(xyz=(0.0, 0.0, hinge_z)),
        material=mats["body"],
        name="tripod_hub", material_class_id="metal.paint_coated",
    )
    base.visual(
        Cylinder(radius=0.032, length=0.060),
        origin=Origin(xyz=(0.0, 0.0, 0.285)),
        material=mats["body"],
        name="hub_neck", material_class_id="metal.paint_coated",
    )
    top_z, col_outer_r = _add_support_column(
        base, r, mats, bottom_z=0.285, length_factor=1.12,
        tube_material="metal", collar_material="body", outer_r=0.0185,
    )
    foot_r = 0.014
    leg_len = r.radial_spider_leg_reach_m
    tip_drop = hinge_z - foot_r
    for idx in range(r.radial_support_count):
        ang = _support_angle(idx, r.radial_support_count)
        c, s = math.cos(ang), math.sin(ang)
        base.visual(
            Cylinder(radius=lug_r, length=2.0 * lug_half_len),
            origin=Origin(
                xyz=(hinge_radius * c, hinge_radius * s, hinge_z),
                rpy=(-math.pi / 2.0, 0.0, ang),
            ),
            material=mats["metal"],
            name=f"leg_hinge_lug_{idx}", material_class_id="metal.stainless_matte",
        )
        # A radial arm grips the protruding lug end clear of the sleeve and
        # embeds into the hub so the hinge pin is one connected base piece.
        arm_y = sleeve_half_len + 0.005
        arm_r_in = 0.048
        arm_r_out = hinge_radius + 0.004
        arm_mid = 0.5 * (arm_r_in + arm_r_out)
        base.visual(
            Box((arm_r_out - arm_r_in, 0.004, 2.0 * lug_r + 0.004)),
            origin=Origin(
                xyz=(arm_mid * c - arm_y * s, arm_mid * s + arm_y * c, hinge_z),
                rpy=(0.0, 0.0, ang),
            ),
            material=mats["metal"],
            name=f"hinge_arm_{idx}", material_class_id="metal.paint_coated",
        )
        leg = model.part(f"leg_{idx}")
        leg.visual(
            mesh_from_geometry(
                _hollow_tube_geom(
                    sleeve_outer_r, sleeve_inner_r, sleeve_len, segments=20,
                ),
                f"radial_spider_hinge_sleeve_{idx}",
            ),
            origin=Origin(xyz=(0.0, 0.5 * sleeve_len, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["body"],
            name="hinge_sleeve", material_class_id="metal.paint_coated",
        )
        _add_spline_tube(
            leg,
            [
                (tube_start_x, 0.0, 0.0),
                (leg_len * 0.388, 0.0, -tip_drop * 0.236),
                (leg_len, 0.0, -tip_drop),
            ],
            tube_r, mats["body"], "leg_tube", f"radial_spider_leg_{idx}",
        )
        leg.visual(
            Sphere(radius=foot_r),
            origin=Origin(xyz=(leg_len, 0.0, -tip_drop)),
            material=mats["rubber"],
            name="rubber_foot", material_class_id="rubber.smooth_plain",
        )
        _add_axis_joint(
            model, name=f"base_to_leg_{idx}", parent=base, child=leg,
            point=(hinge_radius * c, hinge_radius * s, hinge_z),
            axis=(-s, c, 0.0), articulation_type=ArticulationType.REVOLUTE,
            consumer_axis=(0.0, 1.0, 0.0),
            limits=MotionLimits(effort=22.0, velocity=1.2, lower=0.0, upper=1.18),
        )
    return top_z, col_outer_r


def _build_support_folding_braced_spider(
    model: ArticulatedObject, r: ResolvedStudioLampConfig, mats
) -> tuple[float, float]:
    """Folding source variant: low spider plus guide collar and one brace per leg."""
    base = model.part("base")
    hinge_z = 0.205
    hinge_radius = 0.067
    # Same captured pin-and-sleeve hinge as the radial spider, with clearances
    # derived from the lug radius.
    lug_r = 0.008
    sleeve_clear = 0.0008
    sleeve_inner_r = lug_r + sleeve_clear
    sleeve_outer_r = 0.0115
    sleeve_half_len = 0.009
    sleeve_len = 2.0 * sleeve_half_len
    # Same captured pin-and-sleeve hinge as the radial spider: the lug protrudes
    # past each sleeve end so a base arm can grip it clear of the sleeve.
    lug_half_len = sleeve_half_len + 0.009
    tube_r = 0.0105
    # Same start rule as the radial spider: cap tip clears the lug (cross-part
    # running gap) but embeds in the sleeve wall for within-part connectivity.
    tube_start_x = lug_r + 0.002
    hub_r = 0.055
    hub_len = 0.100
    base.visual(
        Cylinder(radius=hub_r, length=hub_len),
        origin=Origin(xyz=(0.0, 0.0, hinge_z)),
        material=mats["body"],
        name="tripod_hub", material_class_id="metal.paint_coated",
    )
    guide_r = 0.038
    guide_len = 0.050
    guide_z = 0.130
    base.visual(
        Cylinder(radius=guide_r, length=guide_len),
        origin=Origin(xyz=(0.0, 0.0, guide_z)),
        material=mats["body"],
        name="hub_lower_guide", material_class_id="metal.paint_coated",
    )
    base.visual(
        mesh_from_geometry(
            _hollow_tube_geom(0.044, 0.0375, 0.025, segments=24),
            "folding_spider_collar_ring",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.1055)),
        material=mats["metal"],
        name="spider_collar", material_class_id="metal.stainless_matte",
    )
    base.visual(
        Cylinder(radius=0.032, length=0.060),
        origin=Origin(xyz=(0.0, 0.0, 0.285)),
        material=mats["body"],
        name="hub_neck", material_class_id="metal.paint_coated",
    )
    top_z, col_outer_r = _add_support_column(
        base, r, mats, bottom_z=0.285, length_factor=1.12,
        tube_material="metal", collar_material="body", outer_r=0.0185,
    )
    foot_r = 0.014
    leg_len = r.folding_spider_leg_reach_m
    tip_drop = hinge_z - foot_r
    # More legs leave less angular room around the shared sliding collar.  The
    # derived stop models that real host-capacity constraint instead of letting
    # independently articulated braces cross through one another when folded.
    fold_upper = max(0.38, 0.68 - 0.10 * max(r.radial_support_count - 4, 0))
    # The brace strut folds rigidly with the leg, so its free end sweeps an arc
    # about the hinge pin. Anchor the strut outboard of the hub rim so the full
    # fold envelope clears the hub wall and the lower guide collar: the minimum
    # sweep radius (reached at full fold) must stay outside the hub radius by
    # the strut radius plus a running clearance, and the anchor height is
    # pinned just below the hub's bottom face.
    strut_radius = 0.004
    strut_clear = 0.006
    strut_anchor_min_r = hub_r + strut_radius + strut_clear
    strut_anchor_z = -0.5 * hub_len - 0.005  # relative to the hinge plane
    strut_anchor_x = (
        strut_anchor_min_r - hinge_radius - strut_anchor_z * math.sin(fold_upper)
    ) / math.cos(fold_upper)
    for idx in range(r.radial_support_count):
        ang = _support_angle(idx, r.radial_support_count)
        c, s = math.cos(ang), math.sin(ang)
        base.visual(
            Cylinder(radius=lug_r, length=2.0 * lug_half_len),
            origin=Origin(
                xyz=(hinge_radius * c, hinge_radius * s, hinge_z),
                rpy=(-math.pi / 2.0, 0.0, ang),
            ),
            material=mats["metal"],
            name=f"leg_hinge_lug_{idx}", material_class_id="metal.stainless_matte",
        )
        # A radial arm grips the protruding lug end clear of the sleeve and
        # embeds into the hub so the hinge pin is one connected base piece.
        arm_y = sleeve_half_len + 0.005
        arm_r_in = 0.048
        arm_r_out = hinge_radius + 0.004
        arm_mid = 0.5 * (arm_r_in + arm_r_out)
        base.visual(
            Box((arm_r_out - arm_r_in, 0.004, 2.0 * lug_r + 0.004)),
            origin=Origin(
                xyz=(arm_mid * c - arm_y * s, arm_mid * s + arm_y * c, hinge_z),
                rpy=(0.0, 0.0, ang),
            ),
            material=mats["metal"],
            name=f"hinge_arm_{idx}", material_class_id="metal.paint_coated",
        )
        leg = model.part(f"leg_{idx}")
        leg.visual(
            mesh_from_geometry(
                _hollow_tube_geom(
                    sleeve_outer_r, sleeve_inner_r, sleeve_len, segments=20,
                ),
                f"folding_spider_hinge_sleeve_{idx}",
            ),
            origin=Origin(xyz=(0.0, 0.5 * sleeve_len, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["body"],
            name="hinge_sleeve", material_class_id="metal.paint_coated",
        )
        _add_spline_tube(
            leg,
            [
                (tube_start_x, 0.0, 0.0),
                (leg_len * 0.388, 0.0, -tip_drop * 0.236),
                (leg_len, 0.0, -tip_drop),
            ],
            tube_r, mats["body"], "leg_tube", f"folding_spider_leg_{idx}",
        )
        _add_spline_tube(
            leg,
            [
                (leg_len * 0.328, 0.0, -tip_drop * 0.210),
                (strut_anchor_x, 0.0, strut_anchor_z),
            ],
            strut_radius, mats["metal"], "leg_strut", f"folding_spider_strut_{idx}",
            samples=6, segments=10,
        )
        leg.visual(
            Sphere(radius=foot_r),
            origin=Origin(xyz=(leg_len, 0.0, -tip_drop)),
            material=mats["rubber"],
            name="rubber_foot", material_class_id="rubber.smooth_plain",
        )
        _add_axis_joint(
            model, name=f"base_to_leg_{idx}", parent=base, child=leg,
            point=(hinge_radius * c, hinge_radius * s, hinge_z),
            axis=(-s, c, 0.0), articulation_type=ArticulationType.REVOLUTE,
            consumer_axis=(0.0, 1.0, 0.0),
            # The shared brace collar stops high-N legs earlier because their
            # tangential spacing is smaller.
            limits=MotionLimits(effort=22.0, velocity=1.2, lower=0.0, upper=fold_upper),
        )
    return top_z, col_outer_r


def _build_support_vintage_clevis_tripod(
    model: ArticulatedObject, r: ResolvedStudioLampConfig, mats
) -> tuple[float, float]:
    """Source 003: high cast spider, paired clevis plates and collared heavy legs."""
    base = model.part("base")
    hinge_z = 0.780
    # The source clevis pair is only 27 mm wide, so the 52 mm pin circle still
    # clears adjacent modules at N=7 while keeping each fork cast into the hub.
    hinge_radius = 0.052
    base.visual(
        Cylinder(radius=0.036, length=0.080),
        origin=Origin(xyz=(0.0, 0.0, hinge_z)),
        material=mats["accent"],
        name="tripod_hub", material_class_id="metal.blackened_gunmetal",
    )
    base.visual(
        Cylinder(radius=0.010, length=0.540),
        origin=Origin(xyz=(0.0, 0.0, 0.470)),
        material=mats["accent"],
        name="center_drop", material_class_id="metal.blackened_gunmetal",
    )
    top_z, col_outer_r = _add_support_column(
        base, r, mats, bottom_z=0.760, length_factor=0.74,
        tube_material="accent", collar_material="metal", outer_r=0.016,
    )
    foot_r = 0.018
    leg_len = r.vintage_clevis_leg_reach_m
    tip_drop = hinge_z - foot_r
    # Captured clevis hinge: the pin spans only the gap between the paired
    # plates, the leg eye is a hollow boss around it, and the neck weld starts
    # outside the pin — all clearances derived from the pin radius.
    pin_r = 0.0045
    plate_center_t = 0.011
    plate_thickness = 0.005
    pin_clear = 0.0005
    # Pin ends embed into the clevis plates so it stays one connected base piece;
    # the leg eye stays axially short of the plate inner faces by pin_clear.
    pin_half_len = plate_center_t
    eye_inner_r = pin_r + pin_clear
    eye_outer_r = 0.012
    eye_half_len = plate_center_t - 0.5 * plate_thickness - pin_clear
    neck_r = 0.006
    # Start the neck slightly inside the eye's outer surface so the two stay
    # one connected piece of the leg.
    neck_start = (eye_outer_r - 0.006, 0.0, -0.010)
    for idx in range(r.radial_support_count):
        ang = _support_angle(idx, r.radial_support_count)
        c, s = math.cos(ang), math.sin(ang)
        tangent = (-s, c)
        for side in (-1, 1):
            center_r = hinge_radius - 0.010
            center_t = side * 0.011
            base.visual(
                Box((0.022, 0.005, 0.030)),
                origin=Origin(
                    xyz=(
                        center_r * c + center_t * tangent[0],
                        center_r * s + center_t * tangent[1],
                        hinge_z,
                    ),
                    rpy=(0.0, 0.0, ang),
                ),
                material=mats["accent"],
                name=f"clevis_plate_{idx}_{side}", material_class_id="metal.blackened_gunmetal",
            )
        base.visual(
            Cylinder(radius=pin_r, length=2.0 * pin_half_len),
            origin=Origin(
                xyz=(hinge_radius * c, hinge_radius * s, hinge_z),
                rpy=(-math.pi / 2.0, 0.0, ang),
            ),
            material=mats["metal"],
            name=f"hinge_pin_{idx}", material_class_id="metal.stainless_matte",
        )
        leg = model.part(f"leg_{idx}")
        leg.visual(
            mesh_from_geometry(
                _hollow_tube_geom(
                    eye_outer_r, eye_inner_r, 2.0 * eye_half_len, segments=20,
                ),
                f"vintage_hinge_eye_{idx}",
            ),
            origin=Origin(xyz=(0.0, eye_half_len, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name="hinge_eye", material_class_id="metal.blackened_gunmetal",
        )
        _add_spline_tube(
            leg, [neck_start, (0.020, 0.0, -0.025)],
            neck_r, mats["accent"], "leg_neck", f"vintage_leg_neck_{idx}",
            samples=5, segments=14,
        )
        _add_spline_tube(
            leg, [(0.020, 0.0, -0.025), (leg_len, 0.0, -tip_drop)],
            0.013, mats["accent"], "leg_tube", f"vintage_leg_tube_{idx}",
            samples=10, segments=18,
        )
        collar_start = 0.44
        collar_end = 0.52
        _add_spline_tube(
            leg,
            [
                (leg_len * collar_start, 0.0, -tip_drop * collar_start),
                (leg_len * collar_end, 0.0, -tip_drop * collar_end),
            ],
            0.016, mats["metal"], "leg_collar", f"vintage_leg_collar_{idx}",
            samples=5, segments=18,
        )
        leg.visual(
            Sphere(radius=foot_r),
            origin=Origin(xyz=(leg_len, 0.0, -tip_drop)),
            material=mats["rubber"],
            name="rubber_foot", material_class_id="rubber.smooth_plain",
        )
        _add_axis_joint(
            model, name=f"base_to_leg_{idx}", parent=base, child=leg,
            point=(hinge_radius * c, hinge_radius * s, hinge_z),
            axis=(-s, c, 0.0), articulation_type=ArticulationType.REVOLUTE,
            consumer_axis=(0.0, 1.0, 0.0),
            limits=MotionLimits(effort=18.0, velocity=1.2, lower=-0.16, upper=0.34),
        )
    return top_z, col_outer_r


def _build_support_rolling_base(
    model: ArticulatedObject, r: ResolvedStudioLampConfig, mats
) -> tuple[float, float]:
    """Rolling base: 3 CONTINUOUS caster wheels + a low central hub."""
    base = model.part("base")
    # Elevate the spider arm above the wheel top so the arm cannot overlap the wheels.
    arm_z = 2.0 * _CASTER_R + 0.026 + 0.010  # wheel top + arm half-thickness + margin
    # The hub is an annulus whose bore continues the column bore, so the mast's
    # lowest tube can descend through it at full travel instead of plunging
    # into a solid hub.
    base.visual(
        mesh_from_geometry(
            _hollow_tube_geom(
                _BASE_HUB_R * 1.1, _STAGE_OUTER_R_BASE * 0.80,
                _BASE_HUB_H * 0.7, segments=28,
            ),
            "rolling_hub_ring",
        ),
        # The hollow tube extrudes upward from its origin, so shift the origin
        # down by half the hub height to keep the annulus vertically centred
        # on the spider-arm plane (as the old centred solid cylinder was).
        origin=Origin(xyz=(0.0, 0.0, arm_z + 0.020 - 0.5 * _BASE_HUB_H * 0.7)),
        material=mats["body"],
        name="rolling_hub", material_class_id="metal.paint_coated",
    )
    # N spider arms (visible, load bearing).
    for idx in range(r.radial_support_count):
        ang = -math.pi / 2.0 + 2.0 * math.pi * idx / r.radial_support_count
        c, s = math.cos(ang), math.sin(ang)
        arm_len = r.rolling_caster_arm_length_m
        mid_r = arm_len * 0.5
        base.visual(
            Box((arm_len, 0.026, 0.026)),
            origin=Origin(
                xyz=(mid_r * c, mid_r * s, arm_z),
                rpy=(0.0, 0.0, ang),
            ),
            material=mats["body"],
            name=f"spider_arm_{idx}", material_class_id="metal.paint_coated",
        )

    # Central column stub (base's outer_tube for mast stages), rooted at arm_z.
    col_outer_r = _STAGE_OUTER_R_BASE
    col_inner_r = col_outer_r * 0.80
    col_len = _BASE_HUB_H + r.stage_tube_len * 0.35
    base.visual(
        mesh_from_geometry(
            _hollow_tube_geom(col_outer_r, col_inner_r, col_len, segments=28),
            "base_outer_tube",
        ),
        origin=Origin(xyz=(0.0, 0.0, arm_z + 0.020)),
        material=mats["metal"],
        name="outer_tube", material_class_id="metal.steel_bare",
    )
    top_z = arm_z + 0.020 + col_len
    base.visual(
        mesh_from_geometry(
            _hollow_tube_geom(col_outer_r * 1.35, col_outer_r * 0.98, 0.030, segments=24),
            "lower_clamp_collar_ring",
        ),
        origin=Origin(xyz=(0.0, 0.0, top_z - 0.032)),
        material=mats["body"],
        name="lower_clamp_collar", material_class_id="metal.paint_coated",
    )

    # N CONTINUOUS caster wheels.
    for idx in range(r.radial_support_count):
        ang = -math.pi / 2.0 + 2.0 * math.pi * idx / r.radial_support_count
        c, s = math.cos(ang), math.sin(ang)
        arm_len = r.rolling_caster_arm_length_m
        # Source construction: two thin side plates straddle the tire. The old
        # single center block penetrated the wheel and was unsuitable for
        # downstream collision geometry.
        wheel_width = 0.026
        fork_thickness = 0.004
        fork_gap = 0.001
        fork_offset = 0.5 * wheel_width + 0.5 * fork_thickness + fork_gap
        arm_bottom_z = arm_z - 0.013
        fork_h = max(arm_bottom_z - _CASTER_R + 0.008, 0.024)
        fork_center_z = _CASTER_R + 0.5 * fork_h - 0.004
        # Inner faces of the side plates sit at fork_offset - fork_thickness/2;
        # hub caps must stop short of them with a sub-millimetre running gap.
        hub_cap_len = 0.002
        hub_cap_offset = fork_offset - 0.5 * fork_thickness - 0.001 - 0.5 * hub_cap_len
        for side in (-1, 1):
            tangent_x = -s * side * fork_offset
            tangent_y = c * side * fork_offset
            base.visual(
                Box((0.038, fork_thickness, fork_h)),
                origin=Origin(
                    xyz=(arm_len * c + tangent_x, arm_len * s + tangent_y, fork_center_z),
                    rpy=(0.0, 0.0, ang),
                ),
                material=mats["metal"],
                name=f"caster_fork_plate_{idx}_{side}", material_class_id="metal.steel_bare",
            )
        base.visual(
            Box((0.038, 2.0 * (fork_offset + 0.5 * fork_thickness), 0.008)),
            origin=Origin(
                xyz=(arm_len * c, arm_len * s, arm_bottom_z + 0.002),
                rpy=(0.0, 0.0, ang),
            ),
            material=mats["metal"],
            name=f"caster_fork_bridge_{idx}", material_class_id="metal.steel_bare",
        )
        wheel = model.part(f"caster_wheel_{idx}")
        wheel.visual(
            Cylinder(radius=_CASTER_R, length=wheel_width),
            origin=Origin(rpy=(0.0, 0.0, 0.0)),
            material=mats["rubber"],
            name="wheel", material_class_id="rubber.smooth_plain",
        )
        # Hub caps bridge the wheel faces toward the fork bearings while the
        # tire and caps keep a visible sub-millimetre running clearance from
        # each side plate (no interpenetration).
        for side in (-1, 1):
            wheel.visual(
                Cylinder(radius=0.009, length=hub_cap_len),
                origin=Origin(xyz=(0.0, 0.0, side * hub_cap_offset)),
                material=mats["metal"],
                name=f"wheel_hub_{side}", material_class_id="metal.aluminum_bare",
            )
        # Rotate the wheel's Z axis to lie along the tangent so it spins around a horizontal axle.
        _add_axis_joint(
            model, name=f"base_to_caster_{idx}", parent=base, child=wheel,
            point=(arm_len * c, arm_len * s, _CASTER_R), axis=(-s, c, 0.0),
            consumer_axis=(0.0, 0.0, 1.0),
            articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=2.0, velocity=8.0),
        )
    return top_z, col_outer_r


def _build_support_counterweighted_boom_base(
    model: ArticulatedObject, r: ResolvedStudioLampConfig, mats
) -> tuple[float, float]:
    """Source-faithful weighted disk with N integral ribs and ground pads."""
    base = model.part("base")
    disc_r = r.weighted_disk_radius_m
    radius_t = _clamp(
        (disc_r - _COUNTERWEIGHT_R_MIN)
        / (_COUNTERWEIGHT_R_MAX - _COUNTERWEIGHT_R_MIN),
        0.0,
        1.0,
    )
    rib_width = 0.012 + 0.010 * radius_t
    rib_height = 0.012 + 0.006 * radius_t
    pad_r = 0.014 + 0.010 * radius_t
    # A short but wide hub.
    base.visual(
        Cylinder(radius=_BASE_HUB_R * 1.25, length=_BASE_HUB_H * 1.10),
        origin=Origin(xyz=(0.0, 0.0, _BASE_HUB_H * 0.55)),
        material=mats["body"],
        name="wide_hub", material_class_id="metal.paint_coated",
    )
    # Central counterweight disc — a low-slung heavy plate.
    base.visual(
        Cylinder(radius=disc_r, length=_COUNTERWEIGHT_H),
        origin=Origin(xyz=(0.0, 0.0, _COUNTERWEIGHT_H / 2.0)),
        material=mats["counterweight"],
        name="counterweight_disc", material_class_id="metal.cast_iron_bare",
    )
    col_outer_r = _STAGE_OUTER_R_BASE * 1.05
    col_inner_r = col_outer_r * 0.80
    # Size the base column by the retract envelope: at full retract the bottom
    # of stage_0 sits at (col_len - _STAGE_INSERT_OVERLAP - stage_travel), and
    # that point must stay above the solid hub top by a running margin, or the
    # retracted tube plunges into the hub and the counterweight disc below.
    hub_top_z = _BASE_HUB_H * 1.10
    retract_clearance = 0.005
    col_len = hub_top_z + _STAGE_INSERT_OVERLAP + r.stage_travel + retract_clearance
    base.visual(
        mesh_from_geometry(
            _hollow_tube_geom(col_outer_r, col_inner_r, col_len, segments=28),
            "base_outer_tube",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["metal"],
        name="outer_tube", material_class_id="metal.steel_bare",
    )
    top_z = col_len
    base.visual(
        mesh_from_geometry(
            _hollow_tube_geom(col_outer_r * 1.35, col_outer_r * 0.98, 0.030, segments=24),
            "lower_clamp_collar_ring",
        ),
        origin=Origin(xyz=(0.0, 0.0, top_z - 0.032)),
        material=mats["body"],
        name="lower_clamp_collar", material_class_id="metal.paint_coated",
    )
    # N is still structural on a disk base: cast ribs transfer mast load to the rim,
    # with matching rubber contacts below. The source silhouette remains a disk.
    for idx in range(r.radial_support_count):
        ang = -math.pi / 2.0 + 2.0 * math.pi * idx / r.radial_support_count
        c, s = math.cos(ang), math.sin(ang)
        base.visual(
            Box((disc_r * 0.68, rib_width, rib_height)),
            origin=Origin(
                xyz=(disc_r * 0.46 * c, disc_r * 0.46 * s,
                     _COUNTERWEIGHT_H + 0.5 * rib_height - 0.002), rpy=(0.0, 0.0, ang),
            ),
            material=mats["metal"],
            name=f"cast_rib_{idx}", material_class_id="metal.cast_iron_bare",
        )
        base.visual(
            Cylinder(radius=pad_r, length=0.006),
            origin=Origin(xyz=(disc_r * 0.72 * c,
                               disc_r * 0.72 * s, 0.003)),
            material=mats["rubber"],
            name=f"ground_pad_{idx}", material_class_id="rubber.smooth_plain",
        )
    return top_z, col_outer_r


def _build_support(
    model: ArticulatedObject, r: ResolvedStudioLampConfig, mats
) -> tuple[float, float]:
    if r.ground_support == "classic_hinged_tripod":
        return _build_support_classic_hinged_tripod(model, r, mats)
    if r.ground_support == "radial_tube_spider":
        return _build_support_radial_tube_spider(model, r, mats)
    if r.ground_support == "folding_braced_spider":
        return _build_support_folding_braced_spider(model, r, mats)
    if r.ground_support == "vintage_clevis_tripod":
        return _build_support_vintage_clevis_tripod(model, r, mats)
    if r.support == "rolling_base":
        return _build_support_rolling_base(model, r, mats)
    return _build_support_counterweighted_boom_base(model, r, mats)


# ---------------------------------------------------------------------------
# Mast stages (multiplicity)
# ---------------------------------------------------------------------------
def _build_mast_stages(
    model: ArticulatedObject,
    r: ResolvedStudioLampConfig,
    mats,
    base_top_z: float,
    base_outer_r: float,
) -> tuple[str, float, float]:
    """Emit `mast_count` telescoping stages. Returns (topmost_part_name,
    joint_origin_z_on_top_part_for_yoke_fixed, top_outer_r)."""
    prev_part_name = "base"
    prev_top_z_local = base_top_z  # in prev part's local frame
    prev_outer_r = base_outer_r
    prev_inner_r = base_outer_r * 0.80  # every parent bore is 0.80x its outer
    for i in range(r.mast_count):
        stage_name = f"mast_stage_{i}"
        stage = model.part(stage_name)
        # Slide inside the parent bore with a sub-millimetre running gap
        # instead of intersecting the parent wall; wall thickness keeps the
        # 0.78 bore ratio shared by all stages.
        outer_r = prev_inner_r - 0.0008
        inner_r = outer_r * 0.78
        tube_len = r.stage_tube_len
        # Author the stage tube from local z=0 upward.
        stage.visual(
            mesh_from_geometry(
                _hollow_tube_geom(outer_r, inner_r, tube_len, segments=28),
                f"stage_{i}_tube",
            ),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=(mats["accent"] if r.mast_profile != "classic_black_nested_tubes" and i > 0 else mats["metal"]),
            name="inner_tube", material_class_id=("metal.blackened_gunmetal" if r.mast_profile in {"classic_black_nested_tubes", "vintage_silver_drop_mast"} else "metal.paint_coated"),
        )
        # A clamp collar at the top of the stage (a hollow ring around the tube).
        stage.visual(
            mesh_from_geometry(
                _hollow_tube_geom(outer_r * 1.35, outer_r * 0.98, 0.024, segments=24),
                f"stage_{i}_clamp_ring",
            ),
            origin=Origin(xyz=(0.0, 0.0, tube_len - 0.026)),
            material=mats["body"],
            name="stage_clamp_collar", material_class_id="metal.paint_coated",
        )
        # PRISMATIC joint from prev_part.top to this stage's origin (its z=0).
        # The joint origin is at prev_part_local (0,0, prev_top_z_local - insert_overlap);
        # i.e. this stage's bottom sits inside the prev outer tube by _STAGE_INSERT_OVERLAP.
        joint_origin_z = prev_top_z_local - _STAGE_INSERT_OVERLAP
        model.articulation(
            f"stage_{i}_prismatic",
            ArticulationType.PRISMATIC,
            parent=prev_part_name,
            child=stage_name,
            origin=Origin(xyz=(0.0, 0.0, joint_origin_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=100.0,
                velocity=0.20,
                lower=-r.stage_travel,
                upper=r.stage_travel,
            ),
        )
        prev_part_name = stage_name
        prev_top_z_local = tube_len
        prev_outer_r = outer_r
        prev_inner_r = inner_r
    return prev_part_name, prev_top_z_local, prev_outer_r


# ---------------------------------------------------------------------------
# Head envelope and support mechanism. No universal frame is imposed.
# ---------------------------------------------------------------------------
def _head_envelope(r: ResolvedStudioLampConfig) -> tuple[float, float, float]:
    s = r.head_scale
    if r.lamp_head_assembly.startswith("portrait_softbox"):
        return 0.24 * s, 0.30 * s, 0.30 * s
    if r.lamp_head_assembly.startswith("landscape_softbox"):
        return 0.30 * s, 0.21 * s, 0.30 * s
    if r.lamp_head_assembly == "led_panel":
        return 0.20 * s, 0.145 * s, 0.065 * s
    if r.lamp_head_assembly == "round_beauty_dish":
        return 0.22 * s, 0.22 * s, 0.24 * s
    return 0.145 * s, 0.145 * s, 0.28 * s


def _build_yoke(
    model: ArticulatedObject,
    r: ResolvedStudioLampConfig,
    mats,
    top_stage: str,
    yoke_join_z: float,
    top_outer_r: float,
) -> tuple[str, tuple[float, float, float]]:
    """Build one of four source mechanisms and return its head-axis frame."""
    half_w, half_h, head_depth = _head_envelope(r)
    inside_half = half_w + 0.035
    sleeve_h = _YOKE_SLEEVE_H
    trunnion_z = sleeve_h + half_h + 0.075
    shaft_r = _TRUNNION_SHAFT_R
    gap = _MOUNT_GAP
    mount = model.part("mechanism_mount")
    # Receiver sleeve is a hollow ring: the mast-top tube butts against its bore
    # bottom instead of penetrating a solid sleeve.
    mount.visual(
        mesh_from_geometry(
            _hollow_tube_geom(
                top_outer_r * 1.35, top_outer_r + gap, sleeve_h, segments=24,
            ),
            "receiver_sleeve_ring",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["body"],
        name="receiver_sleeve", material_class_id="metal.paint_coated",
    )
    # A seat ring closes the sleeve bore just below the mast-top rim; it gives
    # the FIXED mount joint a nearby child surface and stops the mast tube.
    seat_gap = 0.0002
    mount.visual(
        mesh_from_geometry(
            _hollow_tube_geom(
                top_outer_r * 1.35,
                max(top_outer_r - 0.001, 0.002),
                0.004,
                segments=24,
            ),
            "receiver_seat_ring",
        ),
        origin=Origin(xyz=(0.0, 0.0, seat_gap)),
        material=mats["metal"],
        name="receiver_seat", material_class_id="metal.steel_bare",
    )
    # A cap closes the sleeve top; the yoke boss (or pan bearing / riser)
    # pivots on it with a running gap.
    mount.visual(
        Cylinder(radius=top_outer_r * 1.35, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, sleeve_h - 0.002)),
        material=mats["body"],
        name="receiver_cap", material_class_id="metal.paint_coated",
    )
    model.articulation(
        f"{top_stage}_to_mechanism_mount", ArticulationType.FIXED,
        parent=top_stage, child=mount,
        origin=Origin(xyz=(0.0, 0.0, yoke_join_z)),
    )

    mechanism = r.head_support_mechanism
    yoke = model.part("yoke")
    if mechanism == "counterbalance_boom_fork":
        # The pivot hub is coaxial with the boom_tilt axis; the riser post on
        # the mount supports it with a sub-millimetre gap, and the pivot sits
        # high enough for the counterweight to clear the sleeve over the full
        # tilt range.
        hub_r = 0.015
        hub_half_len = 0.05
        boom_r = 0.014
        cw_r = 0.045
        cw_half_len = 0.05
        cw_center_y = -0.065
        tilt_upper = 0.55
        boom_joint_z = (
            sleeve_h + cw_r + abs(cw_center_y) * math.sin(tilt_upper) + 2.0 * gap
        )
        riser_r = 0.012
        # Stop the riser just inside the hub radius so the boom_tilt origin is
        # within the articulation-anchor tolerance of the mount geometry while
        # the hub still rests on it with a running gap.
        riser_top_z = boom_joint_z - hub_r + gap
        mount.visual(
            Cylinder(radius=riser_r, length=riser_top_z - sleeve_h + 0.002),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * (sleeve_h - 0.002 + riser_top_z))),
            material=mats["metal"], name="boom_riser", material_class_id="metal.paint_coated",
        )
        yoke.visual(
            Cylinder(radius=hub_r, length=2.0 * hub_half_len),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"], name="boom_pivot_hub", material_class_id="metal.stainless_matte",
        )
        yoke.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    [(0.0, 0.0, 0.0), (0.0, 0.24, 0.16), (0.0, 0.49, 0.32)],
                    radius=boom_r, samples_per_segment=12, radial_segments=16, cap_ends=True,
                ), "counterbalance_boom_tube"
            ), material=mats["body"], name="counterbalance_boom", material_class_id="metal.paint_coated",
        )
        # Counterweight rides beside the hub end; keep its bore-side face clear
        # of the mount riser by the running gap while still overlapping the
        # hub (same part) for connectivity.
        cw_x = cw_r + riser_r + gap
        yoke.visual(
            Cylinder(radius=cw_r, length=2.0 * cw_half_len),
            origin=Origin(xyz=(cw_x, cw_center_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["counterweight"], name="rear_counterweight", material_class_id="metal.cast_iron_bare",
        )
        # Local head axis is forward and above the boom pivot. It is raised
        # high enough (from the head envelope) that the head's full downward
        # tilt sweep clears the boom-tip bridge; the fork arms span the bridge
        # to just under the trunnion shaft with a running gap.
        boom_tip_y = 0.49
        boom_tip_z = 0.32
        sweep_r = math.hypot(head_depth, half_h)
        trunnion_z = boom_tip_z + sweep_r + 0.035 + gap
        bearing_top_z = trunnion_z - shaft_r - gap
        bearing_bot_z = boom_tip_z + 0.020
        bearing_box_h = bearing_top_z - bearing_bot_z
        bearing_center_z = 0.5 * (bearing_top_z + bearing_bot_z)
        for side, sign in ((0, -1.0), (1, 1.0)):
            yoke.visual(
                Box((0.020, 0.055, bearing_box_h)),
                origin=Origin(xyz=(sign * inside_half, boom_tip_y, bearing_center_z)),
                material=mats["body"], name=f"bearing_{side}", material_class_id="metal.paint_coated",
            )
        yoke.visual(
            Box((2.0 * inside_half + 0.020, 0.055, 0.040)),
            origin=Origin(xyz=(0.0, boom_tip_y, boom_tip_z)),
            material=mats["body"], name="boom_tip_fork_bridge", material_class_id="metal.paint_coated",
        )
        _add_axis_joint(
            model, name="boom_tilt", parent=mount, child=yoke,
            point=(0.0, 0.0, boom_joint_z), axis=(1.0, 0.0, 0.0),
            consumer_axis=(1.0, 0.0, 0.0), articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=80.0, velocity=0.8, lower=-0.35, upper=tilt_upper),
        )
        # The yoke part's origin coincides with the boom pivot (the mate solved
        # by _add_axis_joint), so the fork's head frame stays yoke-relative.
        return "yoke", (0.0, boom_tip_y, trunnion_z)

    # Common U-yoke family: the yoke rides just above the receiver sleeve (or
    # the pan bearing) with a running gap instead of penetrating the sleeve.
    pan_bearing_h = 0.028
    pan_embed = 0.001
    yoke_lift = sleeve_h + gap
    if mechanism == "dual_axis_pan_u_yoke":
        yoke_lift += pan_bearing_h - pan_embed
    yoke.visual(
        Cylinder(radius=top_outer_r * 1.20, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, 0.020)),
        material=mats["body"], name="mechanism_contact_boss", material_class_id="metal.paint_coated",
    )
    arm_thickness = 0.018 if mechanism == "compact_round_tube_u_yoke" else 0.024
    bearing_len = arm_thickness + 0.008
    bearing_inner_r = shaft_r + gap
    # Arms stop 1 mm short of the bearing axis bite so the hollow bearings stay
    # attached to the arms while the head shaft clears the arm tops.
    arm_top_z = trunnion_z - _YOKE_BEARING_R + 0.001
    arm_h = arm_top_z - sleeve_h
    yoke.visual(
        Box((2.0 * inside_half + 0.026, 0.028, 0.026)),
        origin=Origin(xyz=(0.0, 0.0, sleeve_h + 0.013)),
        material=mats["body"], name="yoke_bridge_plate", material_class_id="metal.paint_coated",
    )
    for side, sign in ((0, -1.0), (1, 1.0)):
        yoke.visual(
            Box((arm_thickness, arm_thickness, arm_h)),
            origin=Origin(xyz=(sign * inside_half, 0.0, sleeve_h + arm_h * 0.5)),
            material=mats["body"], name=f"yoke_arm_{side}", material_class_id="metal.paint_coated",
        )
        yoke.visual(
            mesh_from_geometry(
                _hollow_tube_geom(
                    _YOKE_BEARING_R, bearing_inner_r, bearing_len, segments=20,
                ),
                f"u_yoke_bearing_{side}",
            ),
            origin=Origin(
                xyz=(sign * inside_half - 0.5 * bearing_len, 0.0, trunnion_z),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["metal"], name=f"bearing_{side}", material_class_id="metal.stainless_matte",
        )
    if mechanism == "dual_axis_pan_u_yoke":
        mount.visual(
            Cylinder(radius=top_outer_r * 1.7, length=pan_bearing_h),
            origin=Origin(
                xyz=(0.0, 0.0, sleeve_h - pan_embed + 0.5 * pan_bearing_h)
            ),
            material=mats["metal"], name="pan_bearing", material_class_id="metal.stainless_matte",
        )
        _add_axis_joint(
            model, name="yoke_pan", parent=mount, child=yoke,
            point=(0.0, 0.0, yoke_lift), axis=(0.0, 0.0, 1.0),
            consumer_axis=(0.0, 0.0, 1.0), articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=20.0, velocity=1.4),
        )
    else:
        model.articulation(
            "mechanism_mount_to_yoke", ArticulationType.FIXED,
            parent=mount, child=yoke, origin=Origin(xyz=(0.0, 0.0, yoke_lift)),
        )
    return "yoke", (0.0, 0.0, trunnion_z)


# ---------------------------------------------------------------------------
# Head families (Slot B)
# ---------------------------------------------------------------------------
def _build_head_softbox_rect(head, r: ResolvedStudioLampConfig, mats) -> tuple[float, float]:
    """Rectangular softbox — a solid tapering box body approximation.
    Returns (head_front_y, head_rim_half_width)."""
    scale = r.head_scale
    depth = 0.30 * scale
    portrait = r.lamp_head_assembly.startswith("portrait_softbox")
    front_w = (0.48 if portrait else 0.60) * scale
    front_h = (0.60 if portrait else 0.42) * scale
    rear_w = 0.18 * scale
    rear_h = 0.24 * scale
    # The body starts just past the trunnion shaft so the shaft never
    # penetrates the loft; the rear housing bridges shaft to body.
    can_offset = _TRUNNION_SHAFT_R + _MOUNT_GAP
    softbox = (
        cq.Workplane("XY").rect(rear_w, rear_h)
        .workplane(offset=depth).rect(front_w, front_h).loft(combine=True)
    )
    head.visual(
        mesh_from_cadquery(softbox, f"{r.lamp_head_assembly}_loft", tolerance=0.0012),
        origin=Origin(xyz=(0.0, can_offset, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["fabric"],
        name="softbox_body", material_class_id="fabric.plain_flat_weave",
    )
    # Front diffuser panel (sits at the front face, embedded slightly).
    head.visual(
        Box((front_w, 0.010, front_h)),
        origin=Origin(xyz=(0.0, can_offset + depth - 0.002, 0.0)),
        material=mats["diffuser"],
        name="front_diffuser", material_class_id="fabric.sheer",
    )
    # Rear housing (mounted to the trunnion).
    head.visual(
        Cylinder(radius=0.08 * scale, length=0.08 * scale),
        origin=Origin(xyz=(0.0, -0.02, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["body"],
        name="rear_housing", material_class_id="metal.paint_coated",
    )
    # Trunnion shaft (along X, straddles the yoke bearings).
    head.visual(
        Cylinder(radius=_TRUNNION_SHAFT_R, length=2.0 * (_head_envelope(r)[0] + 0.045)),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="trunnion_shaft", material_class_id="metal.steel_bare",
    )
    return depth + can_offset, front_w * 0.5


def _build_head_round_reflector(head, r: ResolvedStudioLampConfig, mats):
    """Round parabolic beauty dish reflector — a solid tapered can + front rim + diffuser."""
    scale = r.head_scale
    depth = 0.24 * scale
    rear_r = 0.065 * scale
    front_r = 0.21 * scale
    # A tapered LatheGeometry shell approximates the parabola without disconnected rings.
    outer_profile = [
        (rear_r, 0.0),
        (rear_r + (front_r - rear_r) * math.sqrt(0.33), depth * 0.33),
        (rear_r + (front_r - rear_r) * math.sqrt(0.66), depth * 0.66),
        (front_r, depth),
    ]
    inner_profile = [
        (max(rear_r - 0.006, 0.001), 0.006),
        (max(rear_r + (front_r - rear_r) * math.sqrt(0.33) - 0.006, 0.001), depth * 0.33 + 0.001),
        (max(rear_r + (front_r - rear_r) * math.sqrt(0.66) - 0.006, 0.001), depth * 0.66),
        (max(front_r - 0.006, 0.001), depth - 0.001),
    ]
    dish = LatheGeometry.from_shell_profiles(
        outer_profile,
        inner_profile,
        segments=40,
        start_cap="flat",
        end_cap="flat",
    )
    head.visual(
        mesh_from_geometry(dish, "beauty_dish_shell"),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["body"],
        name="reflector_shell", material_class_id="metal.paint_coated",
    )
    # Front rim (a metal ring embedded slightly into the shell's front).
    head.visual(
        Cylinder(radius=front_r * 1.02, length=0.014),
        origin=Origin(xyz=(0.0, depth - 0.007, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="reflector_rim", material_class_id="metal.aluminum_bare",
    )
    # A translucent diffuser disc inside the front opening.
    head.visual(
        Cylinder(radius=front_r * 0.90, length=0.005),
        origin=Origin(xyz=(0.0, depth - 0.005, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["diffuser"],
        name="front_diffuser", material_class_id="fabric.sheer",
    )
    head.visual(
        Cylinder(radius=0.06 * scale, length=0.08 * scale),
        origin=Origin(xyz=(0.0, -0.02, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["body"],
        name="rear_housing", material_class_id="metal.paint_coated",
    )
    head.visual(
        Cylinder(radius=0.010, length=2.0 * (_head_envelope(r)[0] + 0.045)),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="trunnion_shaft", material_class_id="metal.steel_bare",
    )
    return depth, front_r


def _build_head_led_panel(head, r: ResolvedStudioLampConfig, mats):
    """LED panel — flat rectangular body + LED grid front."""
    scale = r.head_scale
    depth = 0.05 * scale
    front_w = 0.40 * scale
    front_h = 0.29 * scale
    # Body slab.
    head.visual(
        Box((front_w, depth, front_h)),
        origin=Origin(xyz=(0.0, depth * 0.5, 0.0)),
        material=mats["body"],
        name="panel_body", material_class_id="metal.paint_coated",
    )
    # Front LED grid — a single diffuser cover (grid pattern implicit via material).
    head.visual(
        Box((front_w * 0.94, 0.006, front_h * 0.94)),
        origin=Origin(xyz=(0.0, depth, 0.0)),
        material=mats["diffuser"],
        name="front_diffuser", material_class_id="plastic.frosted_translucent",
    )
    # Rear yoke bridge attachment (a small block).
    head.visual(
        Box((0.10 * scale, 0.04 * scale, 0.04 * scale)),
        origin=Origin(xyz=(0.0, -0.02, 0.0)),
        material=mats["body"],
        name="rear_housing", material_class_id="metal.paint_coated",
    )
    for i in range(6):
        x = (i - 2.5) * front_w * 0.12
        head.visual(
            Box((0.010, 0.020, front_h * 0.68)),
            origin=Origin(xyz=(x, -0.006, 0.0)),
            material=mats["metal"], name=f"rear_heat_fin_{i}", material_class_id="metal.aluminum_bare",
        )
    head.visual(
        Cylinder(radius=0.018 * scale, length=0.016),
        origin=Origin(xyz=(front_w * 0.30, -0.010, -front_h * 0.28),
                      rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["accent"], name="dimmer_knob", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Sphere(radius=0.006 * scale),
        origin=Origin(xyz=(front_w * 0.18, -0.012, -front_h * 0.28)),
        material=mats["lens"], name="power_indicator", material_class_id="plastic.clear_rigid",
    )
    head.visual(
        Cylinder(radius=0.010, length=2.0 * (_head_envelope(r)[0] + 0.045)),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="trunnion_shaft", material_class_id="metal.steel_bare",
    )
    return depth, front_w * 0.5


def _build_head_fresnel_can(head, r: ResolvedStudioLampConfig, mats):
    """Fresnel spotlight — cylindrical can + concentric fresnel rings on front lens."""
    scale = r.head_scale
    body_r = 0.13 * scale
    body_len = 0.22 * scale
    # Can body starts just past the trunnion shaft; the rear housing bridges
    # shaft to can.
    can_offset = _TRUNNION_SHAFT_R + _MOUNT_GAP
    housing_len = 0.05 * scale
    head.visual(
        Cylinder(radius=body_r, length=body_len),
        origin=Origin(xyz=(0.0, can_offset + body_len * 0.5, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["body"],
        name="can_body", material_class_id="metal.paint_coated",
    )
    # Fresnel front lens — a slightly convex disc (named `front_diffuser` so it
    # participates in the common front-face test contract).
    head.visual(
        Cylinder(radius=body_r * 0.94, length=0.014),
        origin=Origin(xyz=(0.0, can_offset + body_len + 0.007, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["lens"],
        name="front_diffuser", material_class_id="glass.clear_transparent",
    )
    # A single outer accent ring at the lens rim — host-conformal (radius derived
    # from lens radius). Additional concentric rings would create disconnected
    # islands inside the part, so they are represented via material tone rather
    # than separate visuals.
    head.visual(
        mesh_from_geometry(
            _hollow_tube_geom(body_r * 0.96, body_r * 0.86, 0.008, segments=32),
            "fresnel_rim_band",
        ),
        origin=Origin(xyz=(0.0, can_offset + body_len + 0.018, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["accent"],
        name="fresnel_ring_band", material_class_id="metal.paint_coated",
    )
    # Rear housing.
    head.visual(
        Cylinder(radius=body_r * 0.85, length=housing_len),
        origin=Origin(xyz=(0.0, can_offset - 0.5 * housing_len, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="rear_housing", material_class_id="metal.steel_bare",
    )
    head.visual(
        Cylinder(radius=_TRUNNION_SHAFT_R, length=2.0 * (_head_envelope(r)[0] + 0.045)),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="trunnion_shaft", material_class_id="metal.steel_bare",
    )
    return body_len + can_offset, body_r


def _build_head_spotlight_can(head, r: ResolvedStudioLampConfig, mats):
    """Spotlight can — LatheGeometry shell with vent bands and a carry handle."""
    scale = r.head_scale
    # LatheGeometry shell — profile approximates rec_003 `_lamp_shell`.
    shell_len = 0.25 * scale
    # Shell starts just past the trunnion shaft; the rear cap bridges both.
    can_offset = _TRUNNION_SHAFT_R + _MOUNT_GAP
    profile_outer = [
        (0.070 * scale, 0.0),
        (0.088 * scale, shell_len * 0.18),
        (0.102 * scale, shell_len * 0.44),
        (0.115 * scale, shell_len * 0.72),
        (0.130 * scale, shell_len * 1.00),
    ]
    profile_inner = [
        (0.058 * scale, 0.005),
        (0.078 * scale, shell_len * 0.18),
        (0.092 * scale, shell_len * 0.44),
        (0.104 * scale, shell_len * 0.72),
        (0.118 * scale, shell_len * 0.985),
    ]
    lathe = LatheGeometry.from_shell_profiles(
        profile_outer,
        profile_inner,
        segments=48,
        start_cap="round",
        end_cap="round",
        lip_samples=6,
    )
    head.visual(
        mesh_from_geometry(lathe, "spotlight_lamp_shell"),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["body"],
        name="head_shell", material_class_id="metal.paint_coated",
    )
    # Front diffuser lens.
    head.visual(
        Cylinder(radius=0.128 * scale, length=0.006),
        origin=Origin(xyz=(0.0, shell_len + 0.003, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["diffuser"],
        name="front_diffuser", material_class_id="glass.frosted_smooth",
    )
    # Rear can cap.
    head.visual(
        Cylinder(radius=0.070 * scale, length=0.030),
        origin=Origin(xyz=(0.0, -0.015, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="rear_housing", material_class_id="metal.steel_bare",
    )
    # A single vent band on the shell — host-conformal, derived from shell radius.
    head.visual(
        Cylinder(radius=0.116 * scale, length=0.006),
        origin=Origin(xyz=(0.0, shell_len * 0.55, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["accent"],
        name="vent_band", material_class_id="metal.paint_coated",
    )
    # Trunnion.
    head.visual(
        Cylinder(radius=0.010, length=2.0 * (_head_envelope(r)[0] + 0.045)),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="trunnion_shaft", material_class_id="metal.steel_bare",
    )
    return shell_len, 0.128 * scale


def _build_lamp_head(
    model: ArticulatedObject,
    r: ResolvedStudioLampConfig,
    mats,
    yoke_part: str,
    trunnion_point: tuple[float, float, float],
) -> tuple[float, float]:
    """Build ``lamp_head`` and REVOLUTE it around the yoke's trunnion axis.
    Returns (head_front_y_local, head_rim_half_size) for head_module mounting."""
    head = model.part("lamp_head")
    if r.head_family == "softbox_rect":
        front_y, rim = _build_head_softbox_rect(head, r, mats)
    elif r.head_family == "round_reflector":
        front_y, rim = _build_head_round_reflector(head, r, mats)
    elif r.head_family == "led_panel":
        front_y, rim = _build_head_led_panel(head, r, mats)
    elif r.head_family == "fresnel_can":
        front_y, rim = _build_head_fresnel_can(head, r, mats)
    else:
        front_y, rim = _build_head_spotlight_can(head, r, mats)

    # REVOLUTE head_tilt around x axis at the trunnion (grandfathered — captured trunnion
    # in yoke bearings; no MatingContract).
    _add_axis_joint(
        model, name="head_tilt", parent=yoke_part, child=head,
        point=trunnion_point, axis=(1.0, 0.0, 0.0),
        consumer_axis=(1.0, 0.0, 0.0), articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=30.0, velocity=1.2, lower=-0.55, upper=0.65),
    )
    return front_y, rim


# ---------------------------------------------------------------------------
# Head modules (Slot C)
# ---------------------------------------------------------------------------
def _build_head_module(
    model: ArticulatedObject,
    r: ResolvedStudioLampConfig,
    mats,
    front_y: float,
    rim: float,
) -> None:
    if r.head_module == "none":
        return
    if r.head_module == "focus_barrel":
        barrel = model.part("focus_barrel")
        barrel_len = 0.035
        # The ring wraps the softbox rear housing (radius 0.08*scale) with a
        # sub-millimetre running gap, and hangs just below the trunnion shaft
        # so neither interface interpenetrates. The outer radius is derived
        # from the housing radius and wall ratio so the inner wall stays
        # within the isolation contact tolerance of the head; an aesthetic
        # minimum radius would float the ring clear of the housing.
        rear_r = 0.08 * r.head_scale
        wall_ratio = 0.90
        focus_r = (rear_r + 0.0008) / wall_ratio
        barrel_center_y = -(_TRUNNION_SHAFT_R + _MOUNT_GAP + 0.5 * barrel_len)
        barrel.visual(
            mesh_from_geometry(
                _hollow_tube_geom(focus_r, focus_r * wall_ratio, barrel_len, segments=32),
                "focus_barrel_shell",
            ),
            origin=Origin(
                xyz=(0.0, barrel_center_y - 0.5 * barrel_len, 0.0),
                rpy=(-math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["metal"],
            name="focus_barrel_shell", material_class_id="metal.aluminum_bare",
        )
        for i in range(24):
            a = 2.0 * math.pi * i / 24.0
            barrel.visual(
                Box((0.006, barrel_len * 0.78, 0.010)),
                origin=Origin(xyz=((focus_r * 1.02) * math.cos(a), barrel_center_y,
                                   (focus_r * 1.02) * math.sin(a)), rpy=(0.0, a, 0.0)),
                material=mats["body"], name=f"focus_grip_{i}", material_class_id="rubber.directional_grooved",
            )
        _add_axis_joint(
            model, name="head_to_focus_barrel", parent="lamp_head", child=barrel,
            point=(0.0, -0.015, 0.0), axis=(0.0, 1.0, 0.0),
            consumer_axis=(0.0, 1.0, 0.0), articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=6.0, velocity=1.5),
        )
        return

    # Source barn doors close in the diffuser plane. Top/bottom are the outer
    # layer, while left/right sit 2 mm nearer the diffuser. Each leaf owns a
    # captured barrel and extends inward from its own rim edge at q=0.
    head = model.get_part("lamp_head")
    front_hx, front_hz, _ = _head_envelope(r)
    outer_y = front_y + 0.009
    inner_y = front_y + 0.006
    hinge_radius = 0.005 * r.head_scale
    # Each bracket sits just behind its captured barrel: the near face clears
    # the barrel's swept radius by the running gap, so the bracket never
    # interpenetrates the barrel while the barrel stays inside the isolation
    # contact band of the head. Thicknesses are the bracket depths in y.
    bracket_gap = _MOUNT_GAP
    outer_bracket_t = 0.016
    inner_bracket_t = 0.014
    outer_bracket_y = outer_y - hinge_radius - bracket_gap - 0.5 * outer_bracket_t
    inner_bracket_y = inner_y - hinge_radius - bracket_gap - 0.5 * inner_bracket_t
    bracket_specs = (
        ("top", (0.0, outer_bracket_y, front_hz), (0.080 * r.head_scale, outer_bracket_t, 0.018)),
        ("bottom", (0.0, outer_bracket_y, -front_hz), (0.080 * r.head_scale, outer_bracket_t, 0.018)),
        ("left", (-front_hx, inner_bracket_y, 0.0), (0.018, inner_bracket_t, 0.080 * r.head_scale)),
        ("right", (front_hx, inner_bracket_y, 0.0), (0.018, inner_bracket_t, 0.080 * r.head_scale)),
    )
    for name, xyz, size in bracket_specs:
        head.visual(
            Box(size), origin=Origin(xyz=xyz), material=mats["body"],
            name=f"barn_bracket_{name}", material_class_id="metal.paint_coated",
        )

    # The leaves tile the diffuser when closed: top/bottom are the outer
    # full-width leaves of depth leaf_depth, and left/right fill the middle
    # band, meeting at the centreline.  Top/bottom then own the outer z-strips
    # while left/right own the middle z-band, so every adjacent pair swings on
    # a disjoint envelope and the leaves can all open together without touch.
    leaf_depth = 0.5 * front_hz
    horizontal_w = 2.0 * front_hx
    horizontal_h = leaf_depth
    vertical_w = front_hx
    vertical_h = 2.0 * front_hz - 2.0 * leaf_depth
    door_specs = (
        # name, hinge point, axis, panel size, panel offset, barrel length/rpy
        ("top", (0.0, outer_y, front_hz), (1.0, 0.0, 0.0),
         (horizontal_w, 0.003, horizontal_h), (0.0, 0.0, -0.5 * horizontal_h),
         1.58 * front_hx, (0.0, math.pi / 2.0, 0.0)),
        ("bottom", (0.0, outer_y, -front_hz), (-1.0, 0.0, 0.0),
         (horizontal_w, 0.003, horizontal_h), (0.0, 0.0, 0.5 * horizontal_h),
         1.58 * front_hx, (0.0, math.pi / 2.0, 0.0)),
        ("left", (-front_hx, inner_y, 0.0), (0.0, 0.0, 1.0),
         (vertical_w, 0.003, vertical_h), (0.5 * vertical_w, 0.0, 0.0),
         vertical_h, (0.0, 0.0, 0.0)),
        ("right", (front_hx, inner_y, 0.0), (0.0, 0.0, -1.0),
         (vertical_w, 0.003, vertical_h), (-0.5 * vertical_w, 0.0, 0.0),
         vertical_h, (0.0, 0.0, 0.0)),
    )
    for name, hinge_xyz, axis, panel_size, panel_offset, barrel_len, barrel_rpy in door_specs:
        door = model.part(f"barn_door_{name}")
        door.visual(
            Box(panel_size), origin=Origin(xyz=panel_offset),
            material=mats["body"], name="door_panel", material_class_id="metal.paint_coated",
        )
        door.visual(
            Cylinder(radius=hinge_radius, length=barrel_len),
            origin=Origin(rpy=barrel_rpy), material=mats["metal"],
            name="hinge_barrel", material_class_id="metal.steel_bare",
        )
        _add_axis_joint(
            model, name=f"head_to_barn_door_{name}", parent="lamp_head", child=door,
            point=hinge_xyz, axis=axis, consumer_axis=axis,
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=3.0, velocity=3.0, lower=0.0, upper=1.65),
        )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_studio_lamp(
    config: StudioLampConfig | ResolvedStudioLampConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = config if isinstance(config, ResolvedStudioLampConfig) else resolve_config(config)
    model = ArticulatedObject(
        name=f"seeded_studio_lamp_{r.seed}",
        meta={"category": "studio_lamp", "slot_choices": slot_choices_for_config(r)},
    )
    if assets is not None:
        model.set_assets(assets)

    mats = _material_map(model, r)

    base_top_z, base_outer_r = _build_support(model, r, mats)
    top_stage, top_top_z, top_outer_r = _build_mast_stages(model, r, mats, base_top_z, base_outer_r)
    yoke_part, trunnion_point = _build_yoke(model, r, mats, top_stage, top_top_z, top_outer_r)
    front_y, rim = _build_lamp_head(model, r, mats, yoke_part, trunnion_point)
    _build_head_module(model, r, mats, front_y, rim)

    return model


def build_seeded_studio_lamp(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_studio_lamp(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
# The public contract owns the merged current-domain author tests, including
# category and motion assertions plus candidate-local allowances and real
# multiplicity counts.
def run_studio_lamp_tests(
    object_model: ArticulatedObject,
    config: StudioLampConfig | ResolvedStudioLampConfig | None = None,
) -> TestReport:
    r = config if isinstance(config, ResolvedStudioLampConfig) else resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    names = {part.name for part in object_model.parts}
    ctx.check(
        "category is studio lamp",
        object_model.meta.get("category") == "studio_lamp",
    )
    ctx.check("core assembly exists", {"base", "mechanism_mount", "yoke", "lamp_head"} <= names)
    ctx.check(
        "mast multiplicity is real",
        sum(name.startswith("mast_stage_") for name in names) == r.mast_stage_count,
    )
    if r.ground_support == "rolling_caster_star":
        base = object_model.get_part("base")
        ctx.check(
            "rolling support multiplicity is real",
            sum(name.startswith("caster_wheel_") for name in names) == r.radial_support_count,
        )
        for i in range(r.radial_support_count):
            wheel = object_model.get_part(f"caster_wheel_{i}")
            joint = object_model.get_articulation(f"base_to_caster_{i}")
            ctx.check(
                f"caster {i} uses two side plates, hub caps and a continuous wheel-center axis",
                all(base.get_visual(f"caster_fork_plate_{i}_{side}") is not None
                    and wheel.get_visual(f"wheel_hub_{side}") is not None
                    for side in (-1, 1))
                and joint.articulation_type == ArticulationType.CONTINUOUS,
            )
    elif r.ground_support == "weighted_disk":
        base = object_model.get_part("base")
        expected_r = _COUNTERWEIGHT_R_MIN + (
            _COUNTERWEIGHT_R_MAX - _COUNTERWEIGHT_R_MIN
        ) * _clamp(
            (r.weighted_disk_radius_m - _COUNTERWEIGHT_R_MIN)
            / (_COUNTERWEIGHT_R_MAX - _COUNTERWEIGHT_R_MIN),
            0.0,
            1.0,
        )
        disc = base.get_visual("counterweight_disc")
        ctx.check(
            "weighted disk radius spans the derived 0.20 to 0.50 meter range",
            disc is not None
            and _COUNTERWEIGHT_R_MIN <= disc.geometry.radius <= _COUNTERWEIGHT_R_MAX
            and math.isclose(disc.geometry.radius, expected_r, abs_tol=1e-9),
            details=f"actual={disc.geometry.radius if disc else None}, expected={expected_r}",
        )
        ctx.check(
            "disk multiplicity emits ribs and pads",
            all(base.get_visual(f"cast_rib_{i}") and base.get_visual(f"ground_pad_{i}")
                for i in range(r.radial_support_count)),
        )
    else:
        ctx.check(
            "radial leg multiplicity is real",
            sum(name.startswith("leg_") for name in names) == r.radial_support_count,
        )
        base = object_model.get_part("base")
        for i in range(r.radial_support_count):
            leg = object_model.get_part(f"leg_{i}")
            joint = object_model.get_articulation(f"base_to_leg_{i}")
            ctx.check(
                f"leg {i} uses a registered source hinge",
                joint.articulation_type == ArticulationType.REVOLUTE,
            )
            foot = ctx.part_element_world_aabb(leg, elem="rubber_foot")
            ctx.check(
                f"leg {i} foot is grounded in the deployed pose",
                foot is not None and abs(foot[0][2]) <= 0.004,
                details=f"foot_aabb={foot}",
            )
        if r.ground_support == "classic_hinged_tripod":
            ctx.check(
                "classic tripod preserves hinge links, curved tubes and braces",
                all(
                    base.get_visual(f"hinge_barrel_{i}") is not None
                    and object_model.get_part(f"leg_{i}").get_visual("hinge_link") is not None
                    and object_model.get_part(f"leg_{i}").get_visual("leg_tube") is not None
                    and object_model.get_part(f"leg_{i}").get_visual("support_brace") is not None
                    for i in range(r.radial_support_count)
                ),
            )
        elif r.ground_support == "radial_tube_spider":
            ctx.check(
                "radial spider preserves low hub and shallow curved tubes",
                base.get_visual("hub_neck") is not None
                and all(
                    base.get_visual(f"leg_hinge_lug_{i}") is not None
                    and object_model.get_part(f"leg_{i}").get_visual("hinge_sleeve") is not None
                    and object_model.get_part(f"leg_{i}").get_visual("leg_tube") is not None
                    for i in range(r.radial_support_count)
                ),
            )
        elif r.ground_support == "folding_braced_spider":
            ctx.check(
                "folding spider preserves guide collar and one strut per leg",
                base.get_visual("hub_lower_guide") is not None
                and base.get_visual("spider_collar") is not None
                and all(
                    object_model.get_part(f"leg_{i}").get_visual("leg_strut") is not None
                    for i in range(r.radial_support_count)
                ),
            )
        elif r.ground_support == "vintage_clevis_tripod":
            ctx.check(
                "vintage tripod preserves paired clevises, pins and bright leg collars",
                base.get_visual("center_drop") is not None
                and all(
                    base.get_visual(f"clevis_plate_{i}_{side}") is not None
                    for i in range(r.radial_support_count)
                    for side in (-1, 1)
                )
                and all(
                    base.get_visual(f"hinge_pin_{i}") is not None
                    and object_model.get_part(f"leg_{i}").get_visual("leg_neck") is not None
                    and object_model.get_part(f"leg_{i}").get_visual("leg_collar") is not None
                    for i in range(r.radial_support_count)
                ),
            )
    ctx.check(
        "slot choices recorded",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    ctx.check(
        "focus ring uses optical-axis rotation",
        object_model.get_articulation("head_to_focus_barrel").articulation_type
        == ArticulationType.CONTINUOUS
        if r.lamp_head_assembly == "landscape_softbox_focus_ring" else True,
    )
    if r.lamp_head_assembly == "portrait_softbox_barn_doors":
        head = object_model.get_part("lamp_head")
        ctx.check(
            "barn doors have four source rim brackets",
            all(head.get_visual(f"barn_bracket_{name}") is not None
                for name in ("top", "bottom", "left", "right")),
        )
        for name in ("top", "bottom", "left", "right"):
            door = object_model.get_part(f"barn_door_{name}")
            panel = door.get_visual("door_panel")
            joint = object_model.get_articulation(f"head_to_barn_door_{name}")
            ctx.check(
                f"barn door {name} is a thin front-plane leaf with captured barrel",
                panel.geometry.size[1] <= 0.004
                and door.get_visual("hinge_barrel") is not None
                and math.isclose(joint.motion_limits.upper, 1.65),
            )
    # All captured interfaces (hinges, sleeves, bearings, nested tubes) are
    # authored with real running clearances, so no overlap allowances remain.

    # Retained from the earlier source-backed contract: these exercise actual
    # motion rather than merely checking that the joints exist.
    head_tilt = object_model.get_articulation("head_tilt")
    front = ctx.part_element_world_aabb(
        object_model.get_part("lamp_head"),
        elem="front_diffuser",
    )
    with ctx.pose({head_tilt: 0.4}):
        tilted = ctx.part_element_world_aabb(
            object_model.get_part("lamp_head"),
            elem="front_diffuser",
        )
    ctx.check(
        "positive head tilt raises front",
        front is not None
        and tilted is not None
        and 0.5 * (tilted[0][2] + tilted[1][2])
        > 0.5 * (front[0][2] + front[1][2]) + 0.005,
        details=f"front={front}, tilted={tilted}",
    )
    top_part = object_model.get_part(f"mast_stage_{r.mast_stage_count - 1}")
    rest_pos = ctx.part_world_position(top_part)
    mast_pose = {
        object_model.get_articulation(f"stage_{i}_prismatic"):
        object_model.get_articulation(f"stage_{i}_prismatic").motion_limits.upper
        for i in range(r.mast_stage_count)
    }
    with ctx.pose(mast_pose):
        raised_pos = ctx.part_world_position(top_part)
    ctx.check(
        "mast extension raises head support",
        rest_pos is not None
        and raised_pos is not None
        and raised_pos[2] > rest_pos[2] + 0.005,
        details=f"rest={rest_pos}, raised={raised_pos}",
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "seven_caster_three_stage_boom_softbox",
        {"ground_support": "rolling_caster_star", "mast_profile": "boom_heavy_riser",
         "head_support_mechanism": "counterbalance_boom_fork",
         "lamp_head_assembly": "landscape_softbox_focus_ring",
         "radial_support_count": 7, "mast_stage_count": 3,
         "head_scale": 1.16, "rolling_caster_arm_length_m": 0.37},
        reason="maximum radial and mast multiplicity with boom and rotating focus ring",
    ),
    corner_case(
        "compact_disk_pan_barn_doors",
        {"ground_support": "weighted_disk", "mast_profile": "vintage_silver_drop_mast",
         "head_support_mechanism": "dual_axis_pan_u_yoke",
         "lamp_head_assembly": "portrait_softbox_barn_doors",
         "radial_support_count": 3, "mast_stage_count": 1,
         "head_scale": 0.88, "weighted_disk_radius_m": 0.20},
        reason="minimum 0.20 m weighted-disk radius with compact pan/tilt and four door axes",
    ),
    corner_case(
        "wide_disk_three_stage_boom",
        {"ground_support": "weighted_disk", "mast_profile": "boom_heavy_riser",
         "head_support_mechanism": "counterbalance_boom_fork",
         "lamp_head_assembly": "landscape_softbox",
         "radial_support_count": 7, "mast_stage_count": 3,
         "head_scale": 1.10, "weighted_disk_radius_m": 0.50},
        reason="maximum 0.50 m weighted-disk radius with seven derived ribs and pads",
    ),
    corner_case(
        "seven_low_radial_spider",
        {"ground_support": "radial_tube_spider", "mast_profile": "classic_black_nested_tubes",
         "head_support_mechanism": "adaptive_direct_trunnion_yoke",
         "lamp_head_assembly": "round_beauty_dish",
         "radial_support_count": 7, "mast_stage_count": 2,
         "head_scale": 1.0, "radial_spider_leg_reach_m": 0.64},
        reason="maximum low-spider multiplicity exercises derived hinge spacing and curved legs",
    ),
    corner_case(
        "seven_vintage_clevis_legs",
        {"ground_support": "vintage_clevis_tripod", "mast_profile": "vintage_silver_drop_mast",
         "head_support_mechanism": "compact_round_tube_u_yoke",
         "lamp_head_assembly": "vintage_spotlight_can",
         "radial_support_count": 7, "mast_stage_count": 1,
         "head_scale": 0.94, "vintage_clevis_leg_reach_m": 0.40},
        reason="maximum clevis multiplicity checks paired fork spacing, pins and grounded feet",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "StudioLampConfig",
    "ResolvedStudioLampConfig",
    "SUPPORTS",
    "HEAD_FAMILIES",
    "HEAD_MODULES",
    "PALETTE_STYLES",
    "PALETTES",
    "build_studio_lamp",
    "build_seeded_studio_lamp",
    "config_from_seed",
    "resolve_config",
    "run_studio_lamp_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
