# SPDX-License-Identifier: Apache-2.0

"""Music stand modular template.

Category: adjustable music stand that supports sheet music. A grounded ``base``
carries a vertical ``shaft`` (telescoping) which supports a tilting ``desk``
for sheet music. Optional page retention arms/clips pivot on the desk lip.

Slots (see specs_modular_v1/music_stand.md):

* ``base`` (③ Primary Form Family): folding_tripod / four_leg_base / weighted_round_base
* ``desk_form`` (③ Primary Form Family): perforated_panel / wire_frame / solid_tray
* ``height_stages`` (multiplicity): single_stage / three_stage
* ``page_retention``: none / paired_clips / paired_swing_arms

Derived from 5-star sources under ``data/records/rec_picturex_0611__music_stand_00{1,2,3}``
and the fork variants declared in ``articraft_data`` template_source_map.
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
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
)

__modular__ = True


BaseKind = Literal["folding_tripod", "four_leg_base", "weighted_round_base"]
DeskForm = Literal["perforated_panel", "wire_frame", "solid_tray"]
HeightStages = Literal["single_stage", "three_stage"]
PageRetention = Literal["none", "paired_clips", "paired_swing_arms"]
PaletteStyle = Literal["graphite_black", "satin_silver", "polished_brass", "matte_ivory"]

BASE_KINDS: tuple[BaseKind, ...] = ("folding_tripod", "four_leg_base", "weighted_round_base")
DESK_FORMS: tuple[DeskForm, ...] = ("perforated_panel", "wire_frame", "solid_tray")
HEIGHT_STAGES: tuple[HeightStages, ...] = ("single_stage", "three_stage")
PAGE_RETENTIONS: tuple[PageRetention, ...] = ("none", "paired_clips", "paired_swing_arms")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "graphite_black",
    "satin_silver",
    "polished_brass",
    "matte_ivory",
)

# height_stages sampling weights (spec §8).
HEIGHT_STAGE_WEIGHTS = (0.6, 0.4)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "graphite_black": {
        "shell": (0.10, 0.11, 0.13, 1.0),
        "metal": (0.16, 0.17, 0.18, 1.0),
        "accent": (0.02, 0.02, 0.02, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
        "paint": (0.14, 0.14, 0.15, 1.0),
    },
    "satin_silver": {
        "shell": (0.72, 0.74, 0.76, 1.0),
        "metal": (0.80, 0.81, 0.82, 1.0),
        "accent": (0.50, 0.51, 0.52, 1.0),
        "rubber": (0.06, 0.06, 0.06, 1.0),
        "paint": (0.66, 0.67, 0.68, 1.0),
    },
    "polished_brass": {
        "shell": (0.62, 0.48, 0.20, 1.0),
        "metal": (0.72, 0.56, 0.24, 1.0),
        "accent": (0.42, 0.32, 0.12, 1.0),
        "rubber": (0.05, 0.04, 0.03, 1.0),
        "paint": (0.56, 0.44, 0.20, 1.0),
    },
    "matte_ivory": {
        "shell": (0.92, 0.90, 0.84, 1.0),
        "metal": (0.68, 0.66, 0.62, 1.0),
        "accent": (0.55, 0.52, 0.48, 1.0),
        "rubber": (0.06, 0.05, 0.04, 1.0),
        "paint": (0.88, 0.86, 0.80, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Nominal dimensions (meters). Anchored to music_stand__003 origin model.py.
# ---------------------------------------------------------------------------
_BASE_HUB_R = 0.032  # 003 L120: base_hub radius
_BASE_HUB_H = 0.060
_BASE_HUB_Z = 0.105
_BRACE_COLLAR_R = 0.026
_BRACE_COLLAR_H = 0.030
_BRACE_COLLAR_Z = 0.160
_SLEEVE_OUTER_R = 0.0145
_SLEEVE_LEN = 0.580
_SLEEVE_Z0 = 0.110  # sleeve bottom in base frame
_COLLAR_TOP_Z = 0.690  # height_collar top (nominal)
_LEG_TUBE_R = 0.0085
_LEG_LEN = 0.400
_LEG_SPREAD_ANGLE = 0.90  # rest angle (rad) from vertical
_FOOT_R = 0.014

_SHAFT_LEN = 0.740
_SHAFT_R = 0.0085
_TILT_SOCKET_R = 0.0125
_TILT_SOCKET_H = 0.026
_TILT_BARREL_R = 0.014
_TILT_BARREL_H = 0.050
_SHAFT_Z0 = 0.090  # inner shaft's bottom in base frame (bottom-of-slot)
_SLIDE_TRAVEL = 0.220

_DESK_W = 0.560  # 003 L42
_DESK_D = 0.360
_DESK_T = 0.012
_DESK_LIP_H = 0.052
_YOKE_H = 0.052  # yoke side height
_YOKE_Y = 0.015
_HINGE_R = 0.015  # 003 L347
_HINGE_HALF_LEN = 0.0105
_DESK_UNDER_BRIDGE_W = 0.110
_DESK_UNDER_BRIDGE_D = 0.060
_DESK_UNDER_BRIDGE_H = 0.014

_ROUND_BASE_R = 0.145  # weighted round base radius (planar boundary)
_ROUND_BASE_H = 0.028

_CLIP_ARM_LEN = 0.070
_CLIP_ARM_W = 0.010
_CLIP_ARM_H = 0.006
_CLIP_PIVOT_R = 0.006


@dataclass(frozen=True)
class MusicStandConfig:
    base: BaseKind | None = None
    desk_form: DeskForm | None = None
    height_stages: HeightStages | None = None
    page_retention: PageRetention | None = None
    palette_style: PaletteStyle = "graphite_black"
    base_scale: float = 1.0
    column_height_scale: float = 1.0
    desk_width_scale: float = 1.0
    desk_depth_scale: float = 1.0
    tilt_range_scale: float = 1.0
    slide_travel_scale: float = 1.0
    name: str = "music_stand"


@dataclass(frozen=True)
class ResolvedMusicStandConfig:
    base: BaseKind
    desk_form: DeskForm
    height_stages: HeightStages
    page_retention: PageRetention
    palette_style: PaletteStyle
    base_scale: float
    column_height_scale: float
    desk_width_scale: float
    desk_depth_scale: float
    tilt_range_scale: float
    slide_travel_scale: float
    # Concrete geometry.
    sleeve_len: float
    sleeve_top_z: float
    shaft_len: float
    shaft_rest_z: float  # top of shaft (in base frame) at q=0
    collar_top_z: float
    slide_travel: float
    tilt_lower: float
    tilt_upper: float
    desk_w: float
    desk_d: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> MusicStandConfig:
    rng = random.Random(seed)
    return MusicStandConfig(
        base=rng.choice(BASE_KINDS),
        desk_form=rng.choice(DESK_FORMS),
        height_stages=rng.choices(HEIGHT_STAGES, weights=HEIGHT_STAGE_WEIGHTS, k=1)[0],
        page_retention=rng.choice(PAGE_RETENTIONS),
        palette_style=rng.choice(PALETTE_STYLES),
        base_scale=round(rng.uniform(0.92, 1.12), 4),
        column_height_scale=round(rng.uniform(0.88, 1.12), 4),
        desk_width_scale=round(rng.uniform(0.88, 1.12), 4),
        desk_depth_scale=round(rng.uniform(0.88, 1.12), 4),
        tilt_range_scale=round(rng.uniform(0.88, 1.08), 4),
        slide_travel_scale=round(rng.uniform(0.88, 1.08), 4),
        name=f"seeded_music_stand_{seed}",
    )


def resolve_config(config: MusicStandConfig | None = None) -> ResolvedMusicStandConfig:
    cfg = config or MusicStandConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    base = _pick(cfg.base, BASE_KINDS)
    desk_form = _pick(cfg.desk_form, DESK_FORMS)
    height_stages = _pick(cfg.height_stages, HEIGHT_STAGES)
    page_retention = _pick(cfg.page_retention, PAGE_RETENTIONS)

    base_scale = _clamp(cfg.base_scale, 0.90, 1.15)
    col_scale = _clamp(cfg.column_height_scale, 0.85, 1.15)
    w_scale = _clamp(cfg.desk_width_scale, 0.85, 1.15)
    d_scale = _clamp(cfg.desk_depth_scale, 0.85, 1.15)
    tilt_scale = _clamp(cfg.tilt_range_scale, 0.85, 1.10)
    travel_scale = _clamp(cfg.slide_travel_scale, 0.85, 1.10)

    sleeve_len = _SLEEVE_LEN * col_scale
    sleeve_top_z = _SLEEVE_Z0 + sleeve_len  # top of outer sleeve (base frame)
    shaft_len = _SHAFT_LEN * col_scale
    # shaft's top (in base frame at q=0) — chosen so tilt joint sits at desk pivot.
    # Nominal: 003 tilt origin at z=0.490 within shaft frame; shaft origin at 0.090 (base frame).
    # We'll pose shaft so its tilt_socket top sits at ~ sleeve_top + slack.
    shaft_rest_z = sleeve_top_z + 0.020  # tilt seat rests slightly above sleeve top
    collar_top_z = _COLLAR_TOP_Z * col_scale

    slide_travel = _clamp(_SLIDE_TRAVEL * travel_scale, 0.150, 0.260)
    tilt_lower = -0.55 * tilt_scale
    tilt_upper = 0.40 * tilt_scale

    desk_w = _DESK_W * w_scale
    desk_d = _DESK_D * d_scale

    return ResolvedMusicStandConfig(
        base=base,
        desk_form=desk_form,
        height_stages=height_stages,
        page_retention=page_retention,
        palette_style=palette_style,
        base_scale=base_scale,
        column_height_scale=col_scale,
        desk_width_scale=w_scale,
        desk_depth_scale=d_scale,
        tilt_range_scale=tilt_scale,
        slide_travel_scale=travel_scale,
        sleeve_len=sleeve_len,
        sleeve_top_z=sleeve_top_z,
        shaft_len=shaft_len,
        shaft_rest_z=shaft_rest_z,
        collar_top_z=collar_top_z,
        slide_travel=slide_travel,
        tilt_lower=tilt_lower,
        tilt_upper=tilt_upper,
        desk_w=desk_w,
        desk_d=desk_d,
        name=cfg.name or "music_stand",
    )


def with_overrides(config: MusicStandConfig, **kwargs: object) -> MusicStandConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: MusicStandConfig | ResolvedMusicStandConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedMusicStandConfig) else resolve_config(config)
    return (
        ("base", r.base),
        ("desk_form", r.desk_form),
        ("height_stages", r.height_stages),
        ("page_retention", r.page_retention),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Slot A: base
# ---------------------------------------------------------------------------
_TRIPOD_LEG_ANGLES = (-math.pi / 2.0, math.pi / 6.0, 5.0 * math.pi / 6.0)
_FOURLEG_ANGLES = (math.pi / 4.0, 3.0 * math.pi / 4.0, 5.0 * math.pi / 4.0, 7.0 * math.pi / 4.0)


def _build_base_common_column(base, r: ResolvedMusicStandConfig, mats):
    """Adds the outer telescoping sleeve + height collar visuals (shared)."""
    # Outer sleeve (hollow-modeled via a Cylinder + inner-air cavity is optional;
    # we render a solid outer Cylinder; the inner shaft is smaller radius so
    # inclusion is a captured pin case allowed at the joint).
    base.visual(
        Cylinder(radius=_SLEEVE_OUTER_R, length=r.sleeve_len),
        origin=Origin(xyz=(0.0, 0.0, _SLEEVE_Z0 + r.sleeve_len / 2.0)),
        material=mats["shell"],
        name="outer_sleeve", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
    )
    # Height collar sits at top of sleeve; explicitly named for MatingContract.
    collar_h = 0.030
    collar_z = _SLEEVE_Z0 + r.sleeve_len + collar_h / 2.0
    base.visual(
        Cylinder(radius=_SLEEVE_OUTER_R * 1.6, length=collar_h),
        origin=Origin(xyz=(0.0, 0.0, collar_z)),
        material=mats["metal"],
        name="height_collar", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
    )
    # Clamp pad — the sleeve/shaft contact patch.
    base.visual(
        Box((0.006, 0.008, 0.024)),
        origin=Origin(xyz=(0.010, 0.0, collar_z)),
        material=mats["accent"],
        name="clamp_pad", material_class_id="rubber.smooth_plain",
    )


def _build_folding_tripod_base(model: ArticulatedObject, r, mats) -> tuple:
    """Returns (base_part, leg_parts, brace_parts)."""
    base = model.part("base")
    base.visual(
        Cylinder(radius=_BASE_HUB_R * r.base_scale, length=_BASE_HUB_H),
        origin=Origin(xyz=(0.0, 0.0, _BASE_HUB_Z)),
        material=mats["shell"],
        name="base_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
    )
    base.visual(
        Cylinder(radius=_BRACE_COLLAR_R * r.base_scale, length=_BRACE_COLLAR_H),
        origin=Origin(xyz=(0.0, 0.0, _BRACE_COLLAR_Z)),
        material=mats["shell"],
        name="brace_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
    )
    _build_base_common_column(base, r, mats)
    base.inertial = Inertial.from_geometry(
        Box((0.15, 0.15, 0.10)),
        mass=1.2,
        origin=Origin(xyz=(0.0, 0.0, _BASE_HUB_Z)),
    )
    # Leg mounts (visible clevis lugs).
    for i, angle in enumerate(_TRIPOD_LEG_ANGLES):
        base.visual(
            Box((0.024, 0.020, 0.024)),
            origin=Origin(
                xyz=(0.038 * math.cos(angle), 0.038 * math.sin(angle), _BASE_HUB_Z),
                rpy=(0.0, 0.0, angle),
            ),
            material=mats["metal"],
            name=f"leg_mount_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
        )

    legs = []
    braces = []
    for i, angle in enumerate(_TRIPOD_LEG_ANGLES):
        leg = model.part(f"leg_{i}")
        # Leg cylinder extended along +X in local frame; rotated by hinge axis at joint.
        leg_len = _LEG_LEN * r.base_scale
        leg.visual(
            Cylinder(radius=_LEG_TUBE_R, length=leg_len),
            origin=Origin(xyz=(leg_len / 2.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["shell"],
            name="leg_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
        )
        leg.visual(
            Sphere(radius=_FOOT_R),
            origin=Origin(xyz=(leg_len, 0.0, 0.0)),
            material=mats["rubber"],
            name="foot", material_class_id="rubber.smooth_plain",
        )
        leg.inertial = Inertial.from_geometry(
            Box((leg_len, 0.020, 0.020)),
            mass=0.15,
            origin=Origin(xyz=(leg_len / 2.0, 0.0, 0.0)),
        )
        # Rest angle: pre-rpy rotates leg outward and slightly down.
        model.articulation(
            f"leg_hinge_{i}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=leg,
            origin=Origin(
                xyz=(0.042 * math.cos(angle), 0.042 * math.sin(angle), _BASE_HUB_Z),
                rpy=(0.0, _LEG_SPREAD_ANGLE, angle),
            ),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=35.0, velocity=2.0, lower=0.0, upper=1.20),
        )
        legs.append(leg)

        brace = model.part(f"brace_{i}")
        brace_len = 0.170 * r.base_scale
        brace.visual(
            Cylinder(radius=0.0045, length=brace_len),
            origin=Origin(xyz=(brace_len / 2.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name="brace_tube", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
        )
        brace.inertial = Inertial.from_geometry(
            Box((brace_len, 0.010, 0.010)),
            mass=0.05,
            origin=Origin(xyz=(brace_len / 2.0, 0.0, 0.0)),
        )
        model.articulation(
            f"brace_hinge_{i}",
            ArticulationType.REVOLUTE,
            parent=leg,
            child=brace,
            origin=Origin(xyz=(0.150 * r.base_scale, 0.0, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=2.5, lower=-0.85, upper=0.85),
        )
        braces.append(brace)

    return base, legs, braces


def _build_four_leg_base(model: ArticulatedObject, r, mats):
    base = model.part("base")
    # Base hub sits at the ground AND rises to embed the sleeve start.
    # Extending to z=0.130 keeps a solid path from feet up into the sleeve.
    hub_h = _SLEEVE_Z0 + 0.020
    base.visual(
        Cylinder(radius=_BASE_HUB_R * r.base_scale * 1.4, length=hub_h),
        origin=Origin(xyz=(0.0, 0.0, hub_h / 2.0)),
        material=mats["shell"],
        name="base_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
    )
    _build_base_common_column(base, r, mats)
    # 4 splayed legs as base visuals (Rule 1: fixed structure = parent visual).
    # Legs radiate outward from the hub at hub_h/2 so they connect to the hub.
    for i, angle in enumerate(_FOURLEG_ANGLES):
        leg_len = 0.240 * r.base_scale
        cx = math.cos(angle) * (leg_len / 2.0 + 0.020)
        cy = math.sin(angle) * (leg_len / 2.0 + 0.020)
        base.visual(
            Box((leg_len, 0.024, 0.030)),
            origin=Origin(xyz=(cx, cy, 0.015), rpy=(0.0, 0.0, angle)),
            material=mats["shell"],
            name=f"leg_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
        )
        fx = math.cos(angle) * (leg_len + 0.020)
        fy = math.sin(angle) * (leg_len + 0.020)
        base.visual(
            Sphere(radius=_FOOT_R),
            origin=Origin(xyz=(fx, fy, 0.010)),
            material=mats["rubber"],
            name=f"foot_{i}", material_class_id="rubber.smooth_plain",
        )
    base.inertial = Inertial.from_geometry(
        Box((0.40, 0.40, 0.10)),
        mass=1.8,
        origin=Origin(xyz=(0.0, 0.0, _BASE_HUB_Z)),
    )
    return base, [], []


def _build_weighted_round_base(model: ArticulatedObject, r, mats):
    base = model.part("base")
    disc_r = _ROUND_BASE_R * r.base_scale
    base.visual(
        Cylinder(radius=disc_r, length=_ROUND_BASE_H),
        origin=Origin(xyz=(0.0, 0.0, _ROUND_BASE_H / 2.0)),
        material=mats["paint"],
        name="weighted_disc", material_class_id="metal.paint_coated",
    )
    # Rubber foot ring (host-conformal decoration on the disc's -Z face).
    base.visual(
        Cylinder(radius=disc_r * 0.95, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        material=mats["rubber"],
        name="foot_ring", material_class_id="rubber.smooth_plain",
    )
    # Hub fairs from disc top up into the sleeve (avoiding a floating gap).
    hub_h = _SLEEVE_Z0 - 0.020 + 0.030  # from z≈0.010 to z≈0.130
    base.visual(
        Cylinder(radius=_BASE_HUB_R * r.base_scale, length=hub_h),
        origin=Origin(xyz=(0.0, 0.0, 0.010 + hub_h / 2.0)),
        material=mats["shell"],
        name="base_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
    )
    _build_base_common_column(base, r, mats)
    base.inertial = Inertial.from_geometry(
        Box((disc_r * 2.0, disc_r * 2.0, 0.10)),
        mass=3.5,
        origin=Origin(xyz=(0.0, 0.0, _BASE_HUB_Z)),
    )
    return base, [], []


_BASE_BUILDERS = {
    "folding_tripod": _build_folding_tripod_base,
    "four_leg_base": _build_four_leg_base,
    "weighted_round_base": _build_weighted_round_base,
}


# ---------------------------------------------------------------------------
# Slot C: shaft (telescoping column)
# ---------------------------------------------------------------------------
def _build_shaft(model: ArticulatedObject, r: ResolvedMusicStandConfig, base, mats) -> object:
    """Returns the topmost shaft part (holds the tilt seat)."""
    if r.height_stages == "single_stage":
        shaft = model.part("shaft")
        # Shaft body — a solid cylinder covering the guided length.
        shaft.visual(
            Cylinder(radius=_SHAFT_R, length=r.shaft_len),
            origin=Origin(xyz=(0.0, 0.0, r.shaft_len / 2.0)),
            material=mats["accent"],
            name="inner_shaft", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
        )
        # Tilt seat at top of shaft (part-local z = shaft_len).
        _emit_shaft_top_hardware(shaft, r, mats, top_z=r.shaft_len)
        shaft.inertial = Inertial.from_geometry(
            Box((0.030, 0.030, r.shaft_len)),
            mass=0.35,
            origin=Origin(xyz=(0.0, 0.0, r.shaft_len / 2.0)),
        )
        # Prismatic +Z from base to shaft. Shaft rest pose puts its bottom at _SHAFT_Z0.
        model.articulation(
            "shaft_slide",
            ArticulationType.PRISMATIC,
            parent=base,
            child=shaft,
            origin=Origin(xyz=(0.0, 0.0, _SHAFT_Z0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=80.0, velocity=0.18, lower=0.0, upper=r.slide_travel),
        )
        return shaft, [("shaft_slide", "shaft")]
    else:
        # three_stage: base -> mid_shaft -> shaft. Two PRISMATIC joints.
        mid_len = r.shaft_len * 0.85
        mid = model.part("mid_shaft")
        mid.visual(
            Cylinder(radius=_SHAFT_R * 1.15, length=mid_len),
            origin=Origin(xyz=(0.0, 0.0, mid_len / 2.0)),
            material=mats["accent"],
            name="mid_shaft_tube", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
        )
        mid.inertial = Inertial.from_geometry(
            Box((0.030, 0.030, mid_len)),
            mass=0.30,
            origin=Origin(xyz=(0.0, 0.0, mid_len / 2.0)),
        )
        model.articulation(
            "mid_slide",
            ArticulationType.PRISMATIC,
            parent=base,
            child=mid,
            origin=Origin(xyz=(0.0, 0.0, _SHAFT_Z0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=80.0, velocity=0.18, lower=0.0, upper=r.slide_travel * 0.5
            ),
        )

        top_len = r.shaft_len * 0.70
        shaft = model.part("shaft")
        shaft.visual(
            Cylinder(radius=_SHAFT_R, length=top_len),
            origin=Origin(xyz=(0.0, 0.0, top_len / 2.0)),
            material=mats["accent"],
            name="inner_shaft", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
        )
        _emit_shaft_top_hardware(shaft, r, mats, top_z=top_len)
        shaft.inertial = Inertial.from_geometry(
            Box((0.030, 0.030, top_len)),
            mass=0.30,
            origin=Origin(xyz=(0.0, 0.0, top_len / 2.0)),
        )
        model.articulation(
            "shaft_slide",
            ArticulationType.PRISMATIC,
            parent=mid,
            child=shaft,
            origin=Origin(xyz=(0.0, 0.0, mid_len * 0.4)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=80.0, velocity=0.18, lower=0.0, upper=r.slide_travel * 0.5
            ),
        )
        return shaft, [("mid_slide", "mid_shaft"), ("shaft_slide", "shaft")]


def _emit_shaft_top_hardware(shaft, r, mats, *, top_z: float):
    """Tilt socket + tilt barrel visuals at the top of the shaft (part-local)."""
    shaft.visual(
        Cylinder(radius=_TILT_SOCKET_R, length=_TILT_SOCKET_H),
        origin=Origin(xyz=(0.0, 0.0, top_z - _TILT_SOCKET_H / 2.0)),
        material=mats["shell"],
        name="tilt_socket", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
    )
    # Tilt barrel: horizontal cylinder passing through socket (the mating axis).
    shaft.visual(
        Cylinder(radius=_TILT_BARREL_R, length=_TILT_BARREL_H),
        origin=Origin(
            xyz=(0.0, 0.0, top_z),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["metal"],
        name="tilt_barrel", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
    )


# ---------------------------------------------------------------------------
# Slot B: desk_form
# ---------------------------------------------------------------------------
def _build_desk(
    model: ArticulatedObject,
    r: ResolvedMusicStandConfig,
    shaft,
    mats,
    *,
    tilt_origin_z_in_shaft: float,
):
    """Builds the desk part and joins it to the shaft with REVOLUTE tilt."""
    desk = model.part("desk")

    # ---- desk shell (varies by desk_form) ----
    if r.desk_form == "perforated_panel":
        # Base plate + retaining lip along -Y edge.
        desk.visual(
            Box((r.desk_w, r.desk_d, _DESK_T)),
            origin=Origin(xyz=(0.0, 0.0, _DESK_T / 2.0 + 0.050)),
            material=mats["shell"],
            name="tray_shell", material_class_id="metal.patterned_sheet_panel",
        )
        # Raised lip (lower edge = front, -Y).
        lip_t = 0.014
        lip_h = _DESK_LIP_H
        desk.visual(
            Box((r.desk_w, lip_t, lip_h)),
            origin=Origin(xyz=(0.0, -r.desk_d / 2.0 + lip_t / 2.0, _DESK_T + 0.050 + lip_h / 2.0)),
            material=mats["shell"],
            name="tray_front_lip", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
        )
    elif r.desk_form == "wire_frame":
        # Outer rectangular frame (4 rails) + 2 horizontal cross-rails.
        rail_t = 0.014
        outer_z = _DESK_T / 2.0 + 0.050
        # Top rail
        desk.visual(
            Box((r.desk_w, rail_t, rail_t)),
            origin=Origin(xyz=(0.0, r.desk_d / 2.0 - rail_t / 2.0, outer_z)),
            material=mats["shell"],
            name="frame_top", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
        )
        # Bottom rail (also serves as front lip)
        desk.visual(
            Box((r.desk_w, rail_t, rail_t * 3.0)),
            origin=Origin(xyz=(0.0, -r.desk_d / 2.0 + rail_t / 2.0, outer_z + rail_t)),
            material=mats["shell"],
            name="tray_front_lip", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),  # doubles as retention lip
        )
        # Left/right rails
        desk.visual(
            Box((rail_t, r.desk_d, rail_t)),
            origin=Origin(xyz=(-r.desk_w / 2.0 + rail_t / 2.0, 0.0, outer_z)),
            material=mats["shell"],
            name="frame_left", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
        )
        desk.visual(
            Box((rail_t, r.desk_d, rail_t)),
            origin=Origin(xyz=(r.desk_w / 2.0 - rail_t / 2.0, 0.0, outer_z)),
            material=mats["shell"],
            name="frame_right", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
        )
        # 2 horizontal cross-rails
        for i, frac in enumerate((-0.25, 0.25)):
            desk.visual(
                Box((r.desk_w - 2.0 * rail_t, rail_t * 0.6, rail_t * 0.6)),
                origin=Origin(xyz=(0.0, r.desk_d * frac, outer_z)),
                material=mats["shell"],
                name=f"cross_rail_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
            )
        # A thin surface plate to seat retention decoration and provide support.
        # Extend to touch all outer frame rails so the plate + frame form one
        # connected island.
        desk.visual(
            Box((r.desk_w - rail_t, r.desk_d - rail_t, 0.006)),
            origin=Origin(xyz=(0.0, 0.0, outer_z)),
            material=mats["paint"],
            name="tray_shell", material_class_id="metal.paint_coated",
        )
    else:  # solid_tray
        thick = _DESK_T * 1.8
        desk.visual(
            Box((r.desk_w, r.desk_d, thick)),
            origin=Origin(xyz=(0.0, 0.0, thick / 2.0 + 0.050)),
            material=mats["paint"],
            name="tray_shell", material_class_id="metal.paint_coated",
        )
        # Tall lip along -Y edge.
        lip_h = _DESK_LIP_H * 1.3
        lip_t = 0.018
        desk.visual(
            Box((r.desk_w, lip_t, lip_h)),
            origin=Origin(xyz=(0.0, -r.desk_d / 2.0 + lip_t / 2.0, thick + 0.050 + lip_h / 2.0)),
            material=mats["shell"],
            name="tray_front_lip", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
        )

    # ---- Underside bridge + yoke sides + hinge cylinders (shared across desk_forms) ----
    # Yoke sides straddle the tilt barrel; hinge cylinders form the tilt bore.
    # Bridge spans full desk width and full height so it embeds both into the
    # tray shell above (z reaches into shell) and the yoke sides below (z=0 up).
    bridge_h = _DESK_UNDER_BRIDGE_H
    bridge_z_center = 0.036
    desk.visual(
        Box((_DESK_UNDER_BRIDGE_W, _DESK_UNDER_BRIDGE_D, bridge_h + 0.020)),
        origin=Origin(xyz=(0.0, _YOKE_Y, bridge_z_center + bridge_h / 2.0)),
        material=mats["shell"],
        name="underside_bridge", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
    )
    yoke_x = 0.0345
    for side, x in (("side_0", -yoke_x), ("side_1", yoke_x)):
        # Yoke extends from z=0 up to bridge (z=0.056) so it definitely touches
        # both the hinge cylinder at z=0 and the bridge at z=0.036.
        desk.visual(
            Box((0.016, 0.050, _YOKE_H + 0.010)),
            origin=Origin(xyz=(x, _YOKE_Y, (_YOKE_H + 0.010) / 2.0)),
            material=mats["shell"],
            name=f"yoke_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "satin_silver", "matte_ivory"} else "metal.brass_polished"),
        )
        desk.visual(
            Cylinder(radius=_HINGE_R, length=2.0 * _HINGE_HALF_LEN),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"hinge_{side}", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
        )
    desk.inertial = Inertial.from_geometry(
        Box((r.desk_w, r.desk_d, 0.08)),
        mass=0.5,
        origin=Origin(xyz=(0.0, 0.0, 0.05)),
    )

    # Tilt joint: REVOLUTE about +X, parent=shaft, child=desk.
    # Small forward tilt at rest (matches source 003 rpy=(0.105,0,0)).
    model.articulation(
        "desk_tilt",
        ArticulationType.REVOLUTE,
        parent=shaft,
        child=desk,
        origin=Origin(
            xyz=(0.0, 0.0, tilt_origin_z_in_shaft),
            rpy=(0.10, 0.0, 0.0),
        ),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=35.0, velocity=1.5, lower=r.tilt_lower, upper=r.tilt_upper
        ),
    )
    return desk


# ---------------------------------------------------------------------------
# Slot D: page retention (parallel children of desk)
# ---------------------------------------------------------------------------
def _build_page_retention(model, r: ResolvedMusicStandConfig, desk, mats):
    if r.page_retention == "none":
        return []
    arms = []
    # Pivot near the front lip (bottom edge of desk in desk-local frame). Y is
    # placed to embed into the lip; Z is centered on the lip top so the pivot
    # cylinder is welded into the lip (no gap).
    # Place pivot BEHIND the front lip (larger y) so the clip hub cylinder does
    # not intersect the lip solid. Height sits on the tray shell top surface.
    if r.desk_form == "perforated_panel":
        pivot_y = -r.desk_d / 2.0 + 0.035  # 0.021m behind the lip (lip_t=0.014)
        pivot_z = _DESK_T + 0.050 + 0.020  # a small stud rising above the tray
    elif r.desk_form == "wire_frame":
        pivot_y = -r.desk_d / 2.0 + 0.045
        pivot_z = 0.056 + 0.020
    else:  # solid_tray
        thick = _DESK_T * 1.8
        pivot_y = -r.desk_d / 2.0 + 0.045
        pivot_z = thick + 0.050 + 0.020

    if r.page_retention == "paired_clips":
        arm_len = _CLIP_ARM_LEN
        arm_w = _CLIP_ARM_W
    else:  # paired_swing_arms
        arm_len = _CLIP_ARM_LEN * 1.6
        arm_w = _CLIP_ARM_W * 0.8

    for side, sign in (("left", -1.0), ("right", 1.0)):
        pivot_x = sign * (r.desk_w / 2.0 - 0.050)
        clip = model.part(f"clip_{side}")
        # Arm extends along +Y in local frame (up toward desk top).
        clip.visual(
            Box((arm_w, arm_len, _CLIP_ARM_H)),
            origin=Origin(xyz=(0.0, arm_len / 2.0, 0.0)),
            material=mats["accent"],
            name="clip_arm", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
        )
        # Pivot socket cylinder at part origin (for MatingContract to desk face).
        clip.visual(
            Cylinder(radius=_CLIP_PIVOT_R, length=0.010),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name="clip_hub", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
        )
        clip.inertial = Inertial.from_geometry(
            Box((0.010, arm_len, _CLIP_ARM_H)),
            mass=0.02,
            origin=Origin(xyz=(0.0, arm_len / 2.0, 0.0)),
        )
        # Pivot stud rising from the tray surface up to pivot_z, then the
        # horizontal pivot cylinder that the clip hub straddles. Stud roots the
        # pivot into the tray, avoiding a floating pivot island.
        stud_z0 = pivot_z - 0.020
        stud_h = pivot_z - stud_z0 + 0.006
        desk.visual(
            Box((0.012, 0.012, stud_h)),
            origin=Origin(xyz=(pivot_x, pivot_y, stud_z0 + stud_h / 2.0)),
            material=mats["metal"],
            name=f"clip_stud_{side}", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
        )
        desk.visual(
            Cylinder(radius=_CLIP_PIVOT_R * 1.4, length=0.014),
            origin=Origin(xyz=(pivot_x, pivot_y, pivot_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"clip_pivot_{side}", material_class_id=("metal.stainless_matte" if r.palette_style in {"satin_silver", "polished_brass", "matte_ivory"} else "metal.blackened_gunmetal"),
        )
        # REVOLUTE about X-axis (arm swings up-down over the page).
        # Joint origin offset +Z above the pivot lug so the arm sits ABOVE the
        # pivot cylinder (avoiding solid overlap in the closed pose).
        model.articulation(
            f"desk_to_clip_{side}",
            ArticulationType.REVOLUTE,
            parent=desk,
            child=clip,
            origin=Origin(xyz=(pivot_x, pivot_y, pivot_z + _CLIP_PIVOT_R + _CLIP_ARM_H)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=3.0, lower=0.0, upper=1.20),
        )
        arms.append((f"clip_{side}", f"desk_to_clip_{side}"))
    return arms


# ---------------------------------------------------------------------------
# Top-level builder
# ---------------------------------------------------------------------------
def build_music_stand(
    config: MusicStandConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"music_stand_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    base, legs, braces = _BASE_BUILDERS[r.base](model, r, mats)
    shaft, shaft_joints = _build_shaft(model, r, base, mats)
    # tilt origin in shaft-local frame — top of shaft
    if r.height_stages == "single_stage":
        tilt_origin_z = r.shaft_len
    else:
        tilt_origin_z = r.shaft_len * 0.70  # top of the topmost stage
    desk = _build_desk(model, r, shaft, mats, tilt_origin_z_in_shaft=tilt_origin_z)
    clips = _build_page_retention(model, r, desk, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["shaft_joints"] = shaft_joints
    model.meta["clip_parts"] = clips
    model.meta["leg_parts"] = [p.name for p in legs]
    model.meta["brace_parts"] = [p.name for p in braces]
    return model


def build_seeded_music_stand(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_music_stand(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_music_stand_tests(
    object_model: ArticulatedObject,
    config: MusicStandConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    base = object_model.get_part("base")

    # ---- Captured-pin / sleeve allowances (element-scoped). ----
    # Inner shaft is captured inside the outer sleeve at every slide pose.
    def _allow_shaft_through_base(child_part, elem_b_name):
        """Shaft/mid_shaft passes through the base hub / brace collar bore."""
        for elem_a in (
            "outer_sleeve",
            "height_collar",
            "clamp_pad",
            "base_hub",
            "brace_collar",
            "weighted_disc",
            "foot_ring",
        ):
            ctx.allow_overlap(
                base,
                child_part,
                elem_a=elem_a,
                elem_b=elem_b_name,
                reason=f"{elem_a} straddles the telescoping column (captured bore).",
            )

    if r.height_stages == "single_stage":
        shaft = object_model.get_part("shaft")
        _allow_shaft_through_base(shaft, "inner_shaft")
    else:
        mid = object_model.get_part("mid_shaft")
        shaft = object_model.get_part("shaft")
        _allow_shaft_through_base(mid, "mid_shaft_tube")
        # inner shaft passes through mid; and also through base bore.
        _allow_shaft_through_base(shaft, "inner_shaft")
        ctx.allow_overlap(
            mid,
            shaft,
            elem_a="mid_shaft_tube",
            elem_b="inner_shaft",
            reason="Inner shaft captured in mid shaft (telescoping stage 2).",
        )

    # Desk yoke straddles the shaft's tilt barrel (captured pivot).
    for side in ("side_0", "side_1"):
        ctx.allow_overlap(
            shaft,
            object_model.get_part("desk"),
            elem_a="tilt_barrel",
            elem_b=f"hinge_{side}",
            reason="Desk hinge knuckle is captured on the shaft tilt barrel.",
        )
        ctx.allow_overlap(
            shaft,
            object_model.get_part("desk"),
            elem_a="tilt_socket",
            elem_b=f"yoke_{side}",
            reason="Yoke side straddles the tilt socket at the pivot.",
        )

    # Folding tripod: leg tubes captured in leg_mount lugs, braces pinned to legs / seated in brace_collar.
    if r.base == "folding_tripod":
        for i in range(3):
            leg = object_model.get_part(f"leg_{i}")
            brace = object_model.get_part(f"brace_{i}")
            ctx.allow_overlap(
                base,
                leg,
                elem_a=f"leg_mount_{i}",
                elem_b="leg_tube",
                reason="Leg tube is captured at its welded hinge lug.",
            )
            ctx.allow_overlap(
                leg,
                brace,
                elem_a="leg_tube",
                elem_b="brace_tube",
                reason="Brace pivot is a captured pin through the leg.",
            )
            ctx.allow_overlap(
                base,
                brace,
                elem_a="brace_collar",
                elem_b="brace_tube",
                reason="Deployed brace end seats in the central collar clevis.",
            )
            # Leg mount might also touch the base hub cylinder.
            ctx.allow_overlap(
                base,
                leg,
                elem_a="base_hub",
                elem_b="leg_tube",
                reason="Leg tube grazes the base hub at the hinge.",
            )
            ctx.allow_overlap(
                base,
                leg,
                elem_a="brace_collar",
                elem_b="leg_tube",
                reason="Leg tube passes near the brace collar band at the hinge.",
            )

    # Page retention: clip hubs captured on desk pivot studs.
    for side in ("left", "right"):
        if any(part.name == f"clip_{side}" for part in object_model.parts):
            ctx.allow_overlap(
                object_model.get_part("desk"),
                object_model.get_part(f"clip_{side}"),
                elem_a=f"clip_pivot_{side}",
                elem_b="clip_hub",
                reason="Clip hub is captured on the desk pivot stud (captured pin).",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("base part present", "base" in part_names, details=str(sorted(part_names)))
    ctx.check("desk part present", "desk" in part_names, details=str(sorted(part_names)))
    ctx.check("shaft part present", "shaft" in part_names, details=str(sorted(part_names)))

    # Shaft slide is PRISMATIC +Z.
    j_slide = object_model.get_articulation("shaft_slide")
    ctx.check(
        "shaft_slide is PRISMATIC +Z",
        j_slide.articulation_type == ArticulationType.PRISMATIC and abs(j_slide.axis[2]) > 0.99,
        details=f"type={j_slide.articulation_type} axis={tuple(j_slide.axis)}",
    )

    # Desk tilt is REVOLUTE about X.
    j_tilt = object_model.get_articulation("desk_tilt")
    ctx.check(
        "desk_tilt is REVOLUTE about X",
        j_tilt.articulation_type == ArticulationType.REVOLUTE and abs(j_tilt.axis[0]) > 0.99,
        details=f"type={j_tilt.articulation_type} axis={tuple(j_tilt.axis)}",
    )

    # height_stages topology.
    if r.height_stages == "three_stage":
        j_mid = object_model.get_articulation("mid_slide")
        ctx.check(
            "three_stage exposes 2 PRISMATIC joints",
            j_mid.articulation_type == ArticulationType.PRISMATIC and abs(j_mid.axis[2]) > 0.99,
            details=f"mid_slide axis={tuple(j_mid.axis)}",
        )

    # base topology
    if r.base == "folding_tripod":
        for i in range(3):
            j = object_model.get_articulation(f"leg_hinge_{i}")
            ctx.check(
                f"leg_hinge_{i} is REVOLUTE",
                j.articulation_type == ArticulationType.REVOLUTE,
                details=f"type={j.articulation_type}",
            )

    # Page retention topology
    if r.page_retention != "none":
        for side in ("left", "right"):
            j = object_model.get_articulation(f"desk_to_clip_{side}")
            ctx.check(
                f"clip {side} is REVOLUTE about X",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
                details=f"axis={tuple(j.axis)}",
            )

    # ---- Motion semantics: shaft rises, desk tilts, clip pivots. ----
    shaft_part = object_model.get_part("shaft")
    shaft_rest = ctx.part_world_position(shaft_part)
    with ctx.pose({j_slide: j_slide.motion_limits.upper * 0.9}):
        shaft_up = ctx.part_world_position(shaft_part)
    if shaft_rest is not None and shaft_up is not None:
        ctx.check(
            "shaft rises with slide",
            shaft_up[2] > shaft_rest[2] + 0.05,
            details=f"rest_z={shaft_rest[2]:.3f} up_z={shaft_up[2]:.3f}",
        )

    desk_part = object_model.get_part("desk")
    tray_rest = ctx.part_world_aabb(desk_part)
    with ctx.pose({j_tilt: j_tilt.motion_limits.lower * 0.7}):
        tray_tilt = ctx.part_world_aabb(desk_part)
    if tray_rest is not None and tray_tilt is not None:
        ctx.check(
            "desk tilt changes tray envelope",
            abs(tray_tilt[1][2] - tray_rest[1][2]) > 0.010
            or abs(tray_tilt[0][2] - tray_rest[0][2]) > 0.010,
            details=f"rest_top_z={tray_rest[1][2]:.3f} tilt_top_z={tray_tilt[1][2]:.3f}",
        )

    if r.page_retention != "none":
        j_clip = object_model.get_articulation("desk_to_clip_left")
        clip_part = object_model.get_part("clip_left")
        c_rest = ctx.part_world_aabb(clip_part)
        with ctx.pose({j_clip: 1.0}):
            c_open = ctx.part_world_aabb(clip_part)
        if c_rest is not None and c_open is not None:
            ctx.check(
                "clip rotates",
                abs(c_open[1][2] - c_rest[1][2]) > 0.005
                or abs(c_open[1][1] - c_rest[1][1]) > 0.005,
                details=f"rest={c_rest} open={c_open}",
            )

    # ---- Ground / footprint (some element must reach ground) ----
    # For folding_tripod the feet are on the leg parts; for four_leg / weighted
    # the base has the ground contact directly. Check any root-subtree element.
    grounded_parts = [base]
    if r.base == "folding_tripod":
        for i in range(3):
            grounded_parts.append(object_model.get_part(f"leg_{i}"))
    z_mins = []
    for p in grounded_parts:
        aabb = ctx.part_world_aabb(p)
        if aabb is not None:
            z_mins.append(aabb[0][2])
    ctx.check(
        "stand rests near the ground",
        len(z_mins) > 0 and min(z_mins) < 0.06,
        details=f"z_mins={[round(z, 4) for z in z_mins]}",
    )

    # ---- slot_choices recorded ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "MusicStandConfig",
    "ResolvedMusicStandConfig",
    "build_music_stand",
    "build_seeded_music_stand",
    "config_from_seed",
    "resolve_config",
    "run_music_stand_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
