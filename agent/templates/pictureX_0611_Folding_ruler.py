# SPDX-License-Identifier: Apache-2.0

"""Source-backed carpenter's folding rule: a serial chain of graduated segments.

Rebuilt from the single source record (a two-blade folding angle ruler) into a
self-contained ``TEMPLATE_DOMAIN`` template. The source's characteristic building
block -- a flat, thin, two-colour graduated slat with a rounded pivot lug and a
through-rivet pivot -- is preserved and generalised into a chain of N segments
joined by N-1 out-of-plane (Z-axis) revolute hinges. Every hinge rotates about Z,
so each segment keeps a fixed stacked Z level regardless of fold angle; body/body
collisions are therefore pose-invariant and only the per-joint hub captures the
child near lug.

Four independent structural slots:

* ``hinge_style``   -- per-joint pivot hardware (graduated dial hub vs flush rivet)
* ``end_profile``   -- the pivot-end silhouette of every segment end
* ``blade_section`` -- the slat cross-section family (flat / T-spine / edge rail),
  a controlled form-family extrapolation driven by one shared section descriptor
  (``section_rise_m`` / ``section_drop_m`` / ``section_flat_x0_m``) that also
  re-derives the stacked level pitch, the hub seat height and the scale-band /
  graduation placement
* ``tip_treatment`` -- the two free chain ends (bare tip, brass end shoe, hook tang)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    TorusGeometry,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

HingeStyle = Literal["angle_dial", "flush_rivet"]
EndProfile = Literal["round_lug", "square_paddle"]
BladeSection = Literal["flat_slat", "ridged_spine", "edge_rail"]
TipTreatment = Literal["plain_tip", "brass_shoe", "hook_tang"]

HINGE_STYLES: tuple[HingeStyle, ...] = ("angle_dial", "flush_rivet")
END_PROFILES: tuple[EndProfile, ...] = ("round_lug", "square_paddle")
BLADE_SECTIONS: tuple[BladeSection, ...] = ("flat_slat", "ridged_spine", "edge_rail")
TIP_TREATMENTS: tuple[TipTreatment, ...] = ("plain_tip", "brass_shoe", "hook_tang")
SEGMENT_COUNTS: tuple[int, ...] = (2, 4, 6, 8, 10)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("hinge_style", HINGE_STYLES),
        component_slot("end_profile", END_PROFILES),
        component_slot("blade_section", BLADE_SECTIONS),
        component_slot("tip_treatment", TIP_TREATMENTS),
        multiplicity_slot(
            "segment_count",
            SEGMENT_COUNTS,
            item_slot="end_profile",
        ),
    )
)

# --- source-derived fixed hardware constants (rec ...4fff479c, rev_000001) -----
THICKNESS = 0.0018        # BLADE_THICKNESS
HOLE_R = 0.0033           # PIVOT_HOLE_RADIUS
AXLE_R = 0.0030           # axle
CAP_R = 0.0058            # rivet_cap
CAP_H = 0.0012
RECESS_R = 0.0016         # rivet_recess
WASHER_R = 0.0100         # rear_washer (scaled from 0.0115)
WASHER_H = 0.0010
DIAL_FACE_R = 0.0215      # dial_face
DIAL_FACE_H = 0.0018
DIAL_RIM_R = 0.0202       # dial_rim torus
DIAL_RIM_TUBE = 0.00125
DIAL_TICK_COUNT = 24
DIAL_TICK_RADIUS = 0.0166
LUG_R_MAX = 0.013         # PIVOT_LUG_RADIUS

# Hub-free zone at each pivot so neither the graduated scale nor any raised
# cross-section feature ever sits under a pivot hub.
_HUB_KEEPOUT = DIAL_FACE_R + 0.005

# Per-hinge-style vertical gap between neighbouring stacked segment levels.  The
# taller dial hub needs the larger gap so its reading boss clears the two
# non-adjacent segment levels (i-1 and i+2).
_STYLE_GAP = {"angle_dial": 0.0080, "flush_rivet": 0.0035}

# Shared cross-section descriptor: (rise above the slat top, drop below the slat
# bottom, half-width of the centre feature).  One descriptor per blade_section
# candidate; it drives the blade mesh, the stacked level pitch (hence the hub
# seat height and axle length) and the scale-band / graduation placement.
_SECTION_PROFILE = {
    "flat_slat": (0.0, 0.0, 0.0),
    "ridged_spine": (0.0013, 0.0, 0.0),
    "edge_rail": (0.0009, 0.0009, 0.0),
}

# Tip descriptor: (rise, drop, outward extent beyond the free pivot centre).
_TIP_PROFILE = {
    "plain_tip": (0.0, 0.0, 0.0),
    "brass_shoe": (0.0006, 0.0006, 0.0140),
    "hook_tang": (0.0, 0.0, 0.0220),
}


@dataclass(frozen=True)
class Config:
    hinge_style: HingeStyle = "angle_dial"
    end_profile: EndProfile = "round_lug"
    blade_section: BladeSection = "flat_slat"
    tip_treatment: TipTreatment = "plain_tip"
    segment_count: int = 6
    segment_length_m: float | None = None
    segment_width_m: float | None = None
    name: str = "pictureX_0611_folding_ruler"


@dataclass(frozen=True)
class ResolvedConfig:
    hinge_style: HingeStyle
    end_profile: EndProfile
    blade_section: BladeSection
    tip_treatment: TipTreatment
    segment_count: int
    hinge_count: int
    segment_length_m: float
    segment_width_m: float
    thickness_m: float
    lug_radius_m: float
    hole_radius_m: float
    section_rise_m: float
    section_drop_m: float
    section_flat_x0_m: float
    section_feature_width_m: float
    tip_rise_m: float
    tip_drop_m: float
    tip_extent_m: float
    band_center_x_m: float
    band_width_m: float
    level_pitch_m: float
    style_gap_m: float
    child_lug_top_z_m: float
    capture_gap_m: float
    tick_inset_m: float
    fold_upper_rad: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x0F01D_2026)
    return Config(
        hinge_style=choices["hinge_style"],
        end_profile=choices["end_profile"],
        blade_section=choices["blade_section"],
        tip_treatment=choices["tip_treatment"],
        segment_count=choices["segment_count"],
        segment_length_m=round(rng.uniform(0.14, 0.22), 4),
        segment_width_m=round(rng.uniform(0.026, 0.040), 4),
    )


def slot_choices_for_config(config: Config) -> tuple[tuple[str, object], ...]:
    return (
        ("hinge_style", config.hinge_style),
        ("end_profile", config.end_profile),
        ("blade_section", config.blade_section),
        ("tip_treatment", config.tip_treatment),
        ("segment_count", config.segment_count),
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "hinge_style": config.hinge_style,
            "end_profile": config.end_profile,
            "blade_section": config.blade_section,
            "tip_treatment": config.tip_treatment,
            "segment_count": config.segment_count,
        }
    )
    length = 0.18 if config.segment_length_m is None else float(config.segment_length_m)
    width = 0.034 if config.segment_width_m is None else float(config.segment_width_m)
    if not 0.14 <= length <= 0.22:
        raise ValueError("segment_length_m must be in [0.14, 0.22]")
    if not 0.026 <= width <= 0.040:
        raise ValueError("segment_width_m must be in [0.026, 0.040]")

    thickness = THICKNESS
    lug_radius = min(LUG_R_MAX, width * 0.42)

    # --- one shared section descriptor drives the blade and every dependent ----
    rise, drop, _ = _SECTION_PROFILE[config.blade_section]
    if config.blade_section == "ridged_spine":
        feature_width = max(0.0060, width * 0.30)
        flat_x0 = feature_width / 2.0
    elif config.blade_section == "edge_rail":
        feature_width = max(0.0045, width * 0.16)
        # the rail hugs the -X (back) edge, so the +X graduated edge stays flat
        flat_x0 = 0.0
    else:
        feature_width = 0.0
        flat_x0 = 0.0
    tip_rise, tip_drop, tip_extent = _TIP_PROFILE[config.tip_treatment]
    section_rise = max(rise, tip_rise)
    section_drop = max(drop, tip_drop)

    # Scale band sits on the flat land between the section feature and the
    # graduated +X edge; both bounds derive from the same section descriptor.
    x_edge = width / 2.0
    band_lo = flat_x0 + 0.0012
    band_hi = max(band_lo + 0.0030, x_edge - 0.0070)
    band_center = (band_lo + band_hi) / 2.0
    band_width = min(0.012, max(0.0030, (band_hi - band_lo) * 0.6))

    style_gap = _STYLE_GAP[config.hinge_style]
    level_pitch = thickness + section_rise + section_drop + style_gap
    return ResolvedConfig(
        hinge_style=config.hinge_style,
        end_profile=config.end_profile,
        blade_section=config.blade_section,
        tip_treatment=config.tip_treatment,
        segment_count=config.segment_count,
        hinge_count=config.segment_count - 1,
        segment_length_m=length,
        segment_width_m=width,
        thickness_m=thickness,
        lug_radius_m=lug_radius,
        hole_radius_m=HOLE_R,
        section_rise_m=section_rise,
        section_drop_m=section_drop,
        section_flat_x0_m=flat_x0,
        section_feature_width_m=feature_width,
        tip_rise_m=tip_rise,
        tip_drop_m=tip_drop,
        tip_extent_m=tip_extent,
        band_center_x_m=band_center,
        band_width_m=band_width,
        level_pitch_m=level_pitch,
        style_gap_m=style_gap,
        # top face of the child near-lug.  The capturing element seats onto it
        # with a shallow (sub-millimetre) retention overlap so the parts are in
        # real contact for connectivity, while staying well under the collision
        # overlap tolerance so no interpenetration is flagged (no allowance).
        child_lug_top_z_m=level_pitch + thickness * 0.5,
        capture_gap_m=-0.00030,
        tick_inset_m=_HUB_KEEPOUT,
        fold_upper_rad=math.pi,
        name=config.name,
    )


# --- materials ----------------------------------------------------------------
def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("satin_aluminium", rgba=(0.77, 0.79, 0.78, 1.0))
    model.material("ivory_scale_face", rgba=(0.92, 0.92, 0.88, 1.0))
    model.material("etched_black", rgba=(0.07, 0.075, 0.07, 1.0))
    model.material("scale_red", rgba=(0.70, 0.08, 0.055, 1.0))
    model.material("frosted_dial", rgba=(0.82, 0.84, 0.82, 0.92))
    model.material("dial_edge", rgba=(0.58, 0.61, 0.59, 1.0))
    model.material("rivet_steel", rgba=(0.50, 0.53, 0.52, 1.0))
    return {
        "metal": "satin_aluminium",
        "scale_face": "ivory_scale_face",
        "black": "etched_black",
        "red": "scale_red",
        "dial": "frosted_dial",
        "dial_edge": "dial_edge",
        "steel": "rivet_steel",
    }


# --- segment end-profile meshes (body + both pivot ends, local z in [0, t]) ----
def _end_profile_round_lug_shape(r: ResolvedConfig) -> cq.Workplane:
    """Flat slat with a round pivot lug at each end (source ``_blade_shape``)."""
    length = r.segment_length_m
    body = (
        cq.Workplane("XY")
        .center(0.0, length / 2.0)
        .rect(r.segment_width_m, length)
        .extrude(r.thickness_m)
    )
    lug_near = cq.Workplane("XY").center(0.0, 0.0).circle(r.lug_radius_m).extrude(r.thickness_m)
    lug_far = cq.Workplane("XY").center(0.0, length).circle(r.lug_radius_m).extrude(r.thickness_m)
    return body.union(lug_near).union(lug_far)


def _end_profile_square_paddle_shape(r: ResolvedConfig) -> cq.Workplane:
    """Flat slat with a squared, wider paddle end at each pivot."""
    length = r.segment_length_m
    body = (
        cq.Workplane("XY")
        .center(0.0, length / 2.0)
        .rect(r.segment_width_m, length)
        .extrude(r.thickness_m)
    )
    pad_w = r.segment_width_m + 0.006
    pad_len = 2.0 * r.lug_radius_m
    pad_near = cq.Workplane("XY").center(0.0, 0.0).rect(pad_w, pad_len).extrude(r.thickness_m)
    pad_far = cq.Workplane("XY").center(0.0, length).rect(pad_w, pad_len).extrude(r.thickness_m)
    return body.union(pad_near).union(pad_far)


_SHAPE_BUILDERS = {
    "round_lug": _end_profile_round_lug_shape,
    "square_paddle": _end_profile_square_paddle_shape,
}


# --- blade cross-section family ------------------------------------------------
def _section_span(r: ResolvedConfig) -> tuple[float, float]:
    """Mid-span window that stays clear of both pivot hubs."""
    return (r.tick_inset_m, r.segment_length_m - r.tick_inset_m)


def _blade_section_flat_slat_feature(shape: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    """Source cross-section: a plain flat slat, no added rib (rise = drop = 0)."""
    return shape


def _blade_section_ridged_spine_feature(shape: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    """T-section: a raised centre spine between the two pivot bosses."""
    y0, y1 = _section_span(r)
    spine = (
        cq.Workplane("XY")
        .center(0.0, (y0 + y1) / 2.0)
        .rect(r.section_feature_width_m, y1 - y0)
        .extrude(r.section_rise_m)
        .translate((0.0, 0.0, r.thickness_m - 0.0002))
    )
    return shape.union(spine)


def _blade_section_edge_rail_feature(shape: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    """Rail section: the ungraduated -X back edge is thickened above and below."""
    y0, y1 = _section_span(r)
    rail_w = r.section_feature_width_m
    rail_x = -r.segment_width_m / 2.0 + rail_w / 2.0
    height = r.thickness_m + r.section_rise_m + r.section_drop_m
    rail = (
        cq.Workplane("XY")
        .center(rail_x, (y0 + y1) / 2.0)
        .rect(rail_w, y1 - y0)
        .extrude(height)
        .translate((0.0, 0.0, -r.section_drop_m))
    )
    return shape.union(rail)


_SECTION_BUILDERS = {
    "flat_slat": _blade_section_flat_slat_feature,
    "ridged_spine": _blade_section_ridged_spine_feature,
    "edge_rail": _blade_section_edge_rail_feature,
}


# --- free chain-end tip treatments --------------------------------------------
def _tip_treatment_plain_tip(shape: cq.Workplane, r: ResolvedConfig, side: int) -> cq.Workplane:
    """Source treatment: the free end is the bare slat end, no added hardware."""
    return shape


def _tip_treatment_brass_shoe(shape: cq.Workplane, r: ResolvedConfig, side: int) -> cq.Workplane:
    """A wrapped metal end shoe: wider than the slat and proud on both faces."""
    y_end = r.segment_length_m if side > 0 else 0.0
    shoe_len = 0.020
    cy = y_end + side * (r.tip_extent_m - shoe_len / 2.0)
    shoe = (
        cq.Workplane("XY")
        .center(0.0, cy)
        .rect(r.segment_width_m + 0.010, shoe_len)
        .extrude(r.thickness_m + r.tip_rise_m + r.tip_drop_m)
        .translate((0.0, 0.0, -r.tip_drop_m))
    )
    return shape.union(shoe)


def _tip_treatment_hook_tang(shape: cq.Workplane, r: ResolvedConfig, side: int) -> cq.Workplane:
    """An in-plane L hook: a tang off the graduated edge closed by a cross lip."""
    y_end = r.segment_length_m if side > 0 else 0.0
    x_edge = r.segment_width_m / 2.0
    tang_w = max(0.0070, r.segment_width_m * 0.30)
    tang_len = 0.026
    tang = (
        cq.Workplane("XY")
        .center(x_edge - tang_w / 2.0, y_end + side * (r.tip_extent_m - tang_len / 2.0))
        .rect(tang_w, tang_len)
        .extrude(r.thickness_m)
    )
    lip_inner = -r.segment_width_m * 0.42
    lip_outer = x_edge - tang_w + 0.0008
    lip_len = 0.004
    lip = (
        cq.Workplane("XY")
        .center(
            (lip_inner + lip_outer) / 2.0,
            y_end + side * (r.tip_extent_m - lip_len / 2.0),
        )
        .rect(lip_outer - lip_inner, lip_len)
        .extrude(r.thickness_m)
    )
    return shape.union(tang).union(lip)


_TIP_BUILDERS = {
    "plain_tip": _tip_treatment_plain_tip,
    "brass_shoe": _tip_treatment_brass_shoe,
    "hook_tang": _tip_treatment_hook_tang,
}


def _cut_pivot_holes(shape: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    hole_near = (
        cq.Workplane("XY")
        .center(0.0, 0.0)
        .circle(r.hole_radius_m)
        .extrude(0.020)
        .translate((0.0, 0.0, -0.010))
    )
    hole_far = (
        cq.Workplane("XY")
        .center(0.0, r.segment_length_m)
        .circle(r.hole_radius_m)
        .extrude(0.020)
        .translate((0.0, 0.0, -0.010))
    )
    shape = shape.cut(hole_near).cut(hole_far)
    return shape.translate((0.0, 0.0, -r.thickness_m / 2.0))


def _segment_shape(r: ResolvedConfig, *, near_tip: bool, far_tip: bool) -> cq.Workplane:
    shape = _SHAPE_BUILDERS[r.end_profile](r)
    shape = _SECTION_BUILDERS[r.blade_section](shape, r)
    tip_builder = _TIP_BUILDERS[r.tip_treatment]
    if near_tip:
        shape = tip_builder(shape, r, -1)
    if far_tip:
        shape = tip_builder(shape, r, 1)
    return _cut_pivot_holes(shape, r)


# --- graduated scale print (decoration; kept clear of the hub keepout) --------
def _add_scale_print(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    face_z = r.thickness_m / 2.0
    y0, y1 = _section_span(r)
    if y1 - y0 <= 0.02:
        return
    x_edge = r.segment_width_m / 2.0
    part.visual(
        Box((r.band_width_m, y1 - y0, 0.00010)),
        origin=Origin(xyz=(r.band_center_x_m, (y0 + y1) / 2.0, face_z + 0.00003)),
        material=mats["scale_face"],
        name="scale_band", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    count = max(2, int((y1 - y0) / 0.010))
    for i in range(count + 1):
        y = y0 + (y1 - y0) * i / count
        is_major = i % 5 == 0
        tick_len = 0.0060 if is_major else 0.0034
        part.visual(
            Box((tick_len, 0.00042 if is_major else 0.00030, 0.00014)),
            origin=Origin(xyz=(x_edge - tick_len / 2.0, y, face_z + 0.00005)),
            material=mats["red"] if is_major else mats["black"],
            name=f"outer_tick_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )


# --- per-joint pivot hardware (hinge_style) -----------------------------------
def _hub_common(part, r: ResolvedConfig, mats: dict[str, str], prefix: str, axle_top: float) -> None:
    """Through axle + rear washer shared by both hinge styles, at the far pivot.

    The washer overlaps this part's own far lug from below (same-part contact) so
    the hub hardware stays intra-part connected without touching the child.
    """
    axle_bottom = -(r.thickness_m / 2.0 + 0.0005)
    part.visual(
        Cylinder(radius=AXLE_R, length=axle_top - axle_bottom),
        origin=Origin(xyz=(0.0, r.segment_length_m, (axle_top + axle_bottom) / 2.0)),
        material=mats["steel"],
        name=f"{prefix}__hub_axle", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=WASHER_R, length=WASHER_H),
        origin=Origin(
            xyz=(0.0, r.segment_length_m, -(r.thickness_m / 2.0) - WASHER_H / 2.0 + 0.0003)
        ),
        material=mats["steel"],
        name=f"{prefix}__hub_washer", material_class_id="metal.steel_bare",
    )


def _hinge_style_flush_rivet_hub(part, r: ResolvedConfig, mats: dict[str, str], index: int) -> str:
    prefix = "hinge_style__flush_rivet"
    y = r.segment_length_m
    # capture cap bottom seats a shallow retention overlap into the child lug top.
    cap_bottom = r.child_lug_top_z_m + r.capture_gap_m
    cap_z = cap_bottom + CAP_H / 2.0
    cap_top = cap_bottom + CAP_H
    # axle runs up into the cap so every hub element is intra-part connected.
    _hub_common(part, r, mats, prefix, axle_top=cap_z)
    part.visual(
        Cylinder(radius=CAP_R, length=CAP_H),
        origin=Origin(xyz=(0.0, y, cap_z)),
        material=mats["steel"],
        name=f"{prefix}__capture_cap", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=RECESS_R, length=0.00035),
        origin=Origin(xyz=(0.0, y, cap_top - 0.00005 + 0.00035 / 2.0)),
        material=mats["black"],
        name=f"{prefix}__hub_recess", material_class_id="metal.blackened_gunmetal",
    )
    return f"{prefix}__capture_cap"


def _hinge_style_angle_dial_hub(part, r: ResolvedConfig, mats: dict[str, str], index: int) -> str:
    prefix = "hinge_style__angle_dial"
    y = r.segment_length_m
    # dial face bottom seats a shallow retention overlap into the child lug top.
    face_bottom = r.child_lug_top_z_m + r.capture_gap_m
    face_z = face_bottom + DIAL_FACE_H / 2.0
    face_top = face_bottom + DIAL_FACE_H
    # A tall central axle threads washer -> parent lug -> dial face -> rivet cap,
    # so every dial element is intra-part connected to the slat.
    cap_z = face_top - 0.00005 + CAP_H / 2.0
    _hub_common(part, r, mats, prefix, axle_top=cap_z)
    part.visual(
        Cylinder(radius=DIAL_FACE_R, length=DIAL_FACE_H),
        origin=Origin(xyz=(0.0, y, face_z)),
        material=mats["dial"],
        name=f"{prefix}__dial_face", material_class_id="plastic.frosted_translucent",
    )
    rim = TorusGeometry(
        radius=DIAL_RIM_R, tube=DIAL_RIM_TUBE, radial_segments=20, tubular_segments=48
    )
    # torus tube seats slightly into the dial face top so it is not a floating ring.
    rim_z = face_top - 0.00005 + DIAL_RIM_TUBE
    part.visual(
        mesh_from_geometry(rim, f"{prefix}__dial_rim_{index}_mesh"),
        origin=Origin(xyz=(0.0, y, rim_z)),
        material=mats["dial_edge"],
        name=f"{prefix}__dial_rim", material_class_id="metal.aluminum_bare",
    )
    tick_h = 0.00016
    tick_z = face_top - 0.00005 + tick_h / 2.0  # graduation ticks embed into the face top
    for i in range(DIAL_TICK_COUNT):
        theta = math.tau * i / DIAL_TICK_COUNT
        major = i % 3 == 0
        tick_len = 0.0035 if major else 0.0021
        part.visual(
            Box((0.00038 if major else 0.00027, tick_len, tick_h)),
            origin=Origin(
                xyz=(
                    DIAL_TICK_RADIUS * math.cos(theta),
                    y + DIAL_TICK_RADIUS * math.sin(theta),
                    tick_z,
                ),
                rpy=(0.0, 0.0, theta - math.pi / 2.0),
            ),
            material=mats["black"],
            name=f"{prefix}__dial_tick_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    part.visual(
        Cylinder(radius=CAP_R, length=CAP_H),
        origin=Origin(xyz=(0.0, y, cap_z)),
        material=mats["steel"],
        name=f"{prefix}__hub_cap", material_class_id="metal.steel_bare",
    )
    return f"{prefix}__dial_face"


_HUB_BUILDERS = {
    "flush_rivet": _hinge_style_flush_rivet_hub,
    "angle_dial": _hinge_style_angle_dial_hub,
}


# --- assembly -----------------------------------------------------------------
def _shell_visual_name(r: ResolvedConfig, *, is_tip_segment: bool) -> str:
    base = f"blade_section__{r.blade_section}__segment_shell"
    if is_tip_segment:
        return f"blade_section__{r.blade_section}__tip_treatment__{r.tip_treatment}__segment_shell"
    return base


def _build_segment(model: ArticulatedObject, r: ResolvedConfig, mats, *, index: int, shape, is_tip_segment: bool):
    part = model.part(
        f"end_profile__{r.end_profile}__segment_{index}",
        meta={
            "role": "rule_segment",
            "index": index,
            "hinge_style": r.hinge_style,
            "end_profile": r.end_profile,
            "blade_section": r.blade_section,
            "tip_treatment": r.tip_treatment if is_tip_segment else "interior",
            "level_z": index * r.level_pitch_m,
        },
    )
    mesh = mesh_from_cadquery(
        shape,
        f"end_profile__{r.end_profile}__segment_{index}_shell",
        tolerance=0.0003,
    )
    part.visual(
        mesh,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["metal"],
        name=_shell_visual_name(r, is_tip_segment=is_tip_segment), material_class_id="metal.aluminum_bare",
    )
    _add_scale_print(part, r, mats)
    return part


def _add_hinge(
    model: ArticulatedObject, parent, child, r: ResolvedConfig, *, index: int
) -> None:
    """Out-of-plane (Z) revolute hinge; child rotates about its own near pivot."""
    name = f"hinge_style__{r.hinge_style}__hinge_{index}"
    provider = AxisInterface(
        name=f"{name}_provider",
        point=(0.0, r.segment_length_m, r.level_pitch_m),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name=f"{name}_consumer",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=2.0,
            velocity=2.5,
            lower=0.0,
            upper=r.fold_upper_rad,
        ),
        meta={"mechanism": "through-rivet folding pivot", "hinge_index": index},
    )
    register_interface_mate(model, name, mate)


def build_picturex_0611_folding_ruler(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    resolved_source = config or config_from_seed(0)
    r = resolve_config(resolved_source)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Folding_ruler",
            "slot_choices": slot_choices_for_config(resolved_source),
            "source_layout": "serial carpenter's folding rule (source: two-blade angle ruler)",
        },
    )
    mats = _materials(model)

    # The chain has exactly two free ends: segment 0's near pivot end and the last
    # segment's far end.  They carry the tip treatment; interior ends are pivots.
    interior_shape = None
    near_tip_shape = _segment_shape(r, near_tip=True, far_tip=False)
    far_tip_shape = _segment_shape(r, near_tip=False, far_tip=True)
    if r.segment_count > 2:
        interior_shape = _segment_shape(r, near_tip=False, far_tip=False)

    hub_builder = _HUB_BUILDERS[r.hinge_style]
    segments = []
    for index in range(r.segment_count):
        if index == 0:
            shape, is_tip = near_tip_shape, True
        elif index == r.segment_count - 1:
            shape, is_tip = far_tip_shape, True
        else:
            shape, is_tip = interior_shape, False
        seg = _build_segment(model, r, mats, index=index, shape=shape, is_tip_segment=is_tip)
        # Every segment except the free tail hosts the outgoing pivot hub.
        if index < r.segment_count - 1:
            hub_builder(seg, r, mats, index)
        segments.append(seg)

    for index in range(r.hinge_count):
        _add_hinge(model, segments[index], segments[index + 1], r, index=index)

    # Authored high-risk coupled poses: fully extended (all hinges 0) and fully
    # folded (all hinges at the upper limit).  Rotation is about Z so segment Z
    # levels stay fixed, but these prove the declared hub captures hold across the
    # whole chain simultaneously.
    hinge_names = [f"hinge_style__{r.hinge_style}__hinge_{i}" for i in range(r.hinge_count)]
    if hinge_names:
        model.meta["risk_poses"] = (
            {name: 0.0 for name in hinge_names},
            {name: r.fold_upper_rad for name in hinge_names},
        )
        model.meta["coupled_joint_pairs"] = tuple(
            (hinge_names[i], hinge_names[i + 1]) for i in range(len(hinge_names) - 1)
        )
    return model


# --- authored tests -----------------------------------------------------------
def _segments_in_order(model: ArticulatedObject):
    segs = [p for p in model.parts if p.meta.get("role") == "rule_segment"]
    return sorted(segs, key=lambda p: int(p.meta.get("index", 0)))


def run_picturex_0611_folding_ruler_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    segments = _segments_in_order(model)
    hinges = [
        j
        for j in model.articulations
        if j.name.startswith(f"hinge_style__{r.hinge_style}__hinge_")
    ]

    ctx.check(
        "category_anchor: serial folding-rule chain",
        len(segments) == r.segment_count
        and len(hinges) == r.hinge_count
        and len(model.root_parts()) == 1
        and model.root_parts()[0].name == segments[0].name
        and tuple(model.meta.get("slot_choices", ())) == slot_choices_for_config(config),
        details=(
            f"segments={len(segments)}, hinges={len(hinges)}, "
            f"roots={[p.name for p in model.root_parts()]}"
        ),
    )

    seg_names = {p.name for p in segments}
    chain_ok = True
    for i, joint in enumerate(sorted(hinges, key=lambda j: int(j.meta.get("hinge_index", 0)))):
        chain_ok = chain_ok and (
            joint.parent == segments[i].name and joint.child == segments[i + 1].name
        )
    ctx.check(
        "category_anchor: out-of-plane pivot hinges",
        len(hinges) == r.hinge_count
        and chain_ok
        and all(
            j.articulation_type == ArticulationType.REVOLUTE
            and tuple(j.axis) == (0.0, 0.0, 1.0)
            and j.motion_limits is not None
            and j.motion_limits.lower == 0.0
            and abs(j.motion_limits.upper - math.pi) < 1e-9
            and j.parent in seg_names
            and j.child in seg_names
            for j in hinges
        ),
        details=f"hinges={[j.name for j in hinges]}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    if r.hinge_style == "angle_dial":
        boss_ok = (
            any("angle_dial__dial_face" in n for n in visual_names)
            and any("angle_dial__dial_rim" in n for n in visual_names)
            and any("angle_dial__dial_tick_" in n for n in visual_names)
        )
        ctx.check(
            "category_anchor: angle_dial reading boss",
            boss_ok,
            details=f"dial visuals present={boss_ok}",
        )
        capture_name = "hinge_style__angle_dial__dial_face"
    else:
        rivet_ok = (
            any("flush_rivet__capture_cap" in n for n in visual_names)
            and any("flush_rivet__hub_axle" in n for n in visual_names)
            and any("flush_rivet__hub_washer" in n for n in visual_names)
            and not any("dial_face" in n for n in visual_names)
        )
        ctx.check(
            "category_anchor: flush_rivet pivot hardware",
            rivet_ok,
            details=f"rivet visuals present={rivet_ok}",
        )
        capture_name = "hinge_style__flush_rivet__capture_cap"

    def _seg_visual_names(seg) -> set[str]:
        return {v.name or "" for v in seg.visuals}

    # --- end_profile anchor: every segment end carries the chosen pivot end -----
    ctx.check(
        "category_anchor: pivot end profile",
        all(
            seg.name.startswith(f"end_profile__{r.end_profile}__segment_")
            and seg.meta.get("end_profile") == r.end_profile
            for seg in segments
        )
        and r.lug_radius_m == min(LUG_R_MAX, r.segment_width_m * 0.42)
        and r.hole_radius_m == HOLE_R,
        details=f"end_profile={r.end_profile}, lug_r={r.lug_radius_m}",
    )

    # --- blade_section anchor: one shared descriptor drives blade + dependents --
    declared_rise, declared_drop, _ = _SECTION_PROFILE[r.blade_section]
    tip_rise, tip_drop, tip_extent = _TIP_PROFILE[r.tip_treatment]
    section_shell_ok = all(
        any(f"blade_section__{r.blade_section}__" in n for n in _seg_visual_names(seg))
        for seg in segments
    )
    pitch_ok = (
        abs(
            r.level_pitch_m
            - (r.thickness_m + r.section_rise_m + r.section_drop_m + r.style_gap_m)
        )
        < 1e-12
        and abs(r.child_lug_top_z_m - (r.level_pitch_m + r.thickness_m / 2.0)) < 1e-12
        and r.section_rise_m == max(declared_rise, tip_rise)
        and r.section_drop_m == max(declared_drop, tip_drop)
        and r.style_gap_m == _STYLE_GAP[r.hinge_style]
    )
    # the raised/dropped rib never reaches under a pivot hub, and the scale band
    # sits on the flat land the same descriptor leaves free.
    y0, y1 = _section_span(r)
    keepout_ok = y0 >= DIAL_FACE_R + 0.004 and y1 <= r.segment_length_m - (DIAL_FACE_R + 0.004)
    band_ok = (
        r.band_center_x_m - r.band_width_m / 2.0 >= r.section_flat_x0_m - 0.0015
        and r.band_center_x_m + r.band_width_m / 2.0 <= r.segment_width_m / 2.0
    )
    feature_ok = (r.blade_section == "flat_slat") == (r.section_feature_width_m == 0.0)
    ctx.check(
        "category_anchor: blade cross-section family",
        section_shell_ok and pitch_ok and keepout_ok and band_ok and feature_ok,
        details=(
            f"section={r.blade_section}, rise={r.section_rise_m}, drop={r.section_drop_m}, "
            f"pitch={r.level_pitch_m}, flat_x0={r.section_flat_x0_m}, "
            f"band=({r.band_center_x_m}, {r.band_width_m}), span=({y0}, {y1})"
        ),
    )

    # --- tip_treatment anchor: exactly the two free chain ends are treated ------
    tip_token = f"tip_treatment__{r.tip_treatment}__"
    tip_segments = [
        seg for seg in segments if any(tip_token in n for n in _seg_visual_names(seg))
    ]
    interior_clean = all(
        not any("tip_treatment__" in n for n in _seg_visual_names(seg))
        for seg in segments[1:-1]
    )
    ctx.check(
        "category_anchor: free-end tip treatment",
        len(tip_segments) == 2
        and tip_segments[0].name == segments[0].name
        and tip_segments[1].name == segments[-1].name
        and interior_clean
        and r.tip_extent_m == tip_extent
        and (r.tip_extent_m > 0.0) == (r.tip_treatment != "plain_tip"),
        details=(
            f"tip={r.tip_treatment}, treated={[s.name for s in tip_segments]}, "
            f"extent={r.tip_extent_m}, interior_clean={interior_clean}"
        ),
    )

    def _band_is_ivory(seg) -> bool:
        band = seg.get_visual("scale_band")
        mat = getattr(band, "material", None)
        mat_name = getattr(mat, "name", mat)
        return mat_name == "ivory_scale_face"

    ctx.check(
        "graduated two-colour scale on segments",
        all(
            any((v.name or "").startswith("outer_tick_") for v in seg.visuals)
            and _band_is_ivory(seg)
            for seg in segments
        ),
        details="each segment keeps its dense graduated edge ticks and pale scale band",
    )

    # Every interior segment hosts the outgoing pivot hub (its capturing element);
    # the free tail segment has none.  Verified structurally (mesh-free) so that
    # the actual hub clearance and no-intersection are owned by sweep collision QC.
    interior_ok = all(
        any(capture_name in n for n in _seg_visual_names(segments[i]))
        for i in range(r.hinge_count)
    )
    tail_ok = not any(
        ("dial_face" in n or "capture_cap" in n)
        for n in _seg_visual_names(segments[-1])
    )
    ctx.check(
        "segment_count drives N-1 hub-bearing hinges (tail is a free end)",
        len(hinges) == r.segment_count - 1 and interior_ok and tail_ok,
        details=f"interior_hubs_ok={interior_ok}, tail_free={tail_ok}",
    )

    # Fully folded / fully extended coupled poses are declared as authored
    # risk_poses in model.meta, so sweep motion/collision QC exercises the whole
    # chain at both extremes; assert they are present and well-formed here.
    risk = model.meta.get("risk_poses", ())
    coupled = model.meta.get("coupled_joint_pairs", ())
    hinge_name_set = {j.name for j in hinges}
    folded_declared = any(
        len(p) == r.hinge_count
        and set(p) <= hinge_name_set
        and all(abs(v - r.fold_upper_rad) < 1e-9 for v in p.values())
        for p in risk
        if isinstance(p, dict)
    )
    extended_declared = any(
        len(p) == r.hinge_count
        and set(p) <= hinge_name_set
        and all(v == 0.0 for v in p.values())
        for p in risk
        if isinstance(p, dict)
    )
    ctx.check(
        "fully folded and fully extended chain poses are declared for motion QC",
        r.hinge_count == 0
        or (folded_declared and extended_declared and len(coupled) == r.hinge_count - 1),
        details=f"risk_poses={len(risk)}, coupled_pairs={len(coupled)}",
    )

    return ctx.report()


# High-risk cross-slot / N boundary configs.  Motion QC additionally executes the
# authored fully-folded and fully-extended risk poses on each of these builds.
TEMPLATE_CORNERS = (
    corner_case(
        "max_chain_angle_dial_round_spine_hook",
        {
            "hinge_style": "angle_dial",
            "end_profile": "round_lug",
            "blade_section": "ridged_spine",
            "tip_treatment": "hook_tang",
            "segment_count": 10,
            "segment_length_m": 0.14,
            "segment_width_m": 0.040,
        },
        reason=(
            "longest chain, tallest dial hubs, shortest segments, raised centre spine "
            "and the longest free-end tang (densest fold stack)"
        ),
    ),
    corner_case(
        "max_chain_flush_square_rail_shoe",
        {
            "hinge_style": "flush_rivet",
            "end_profile": "square_paddle",
            "blade_section": "edge_rail",
            "tip_treatment": "brass_shoe",
            "segment_count": 10,
            "segment_length_m": 0.22,
            "segment_width_m": 0.026,
        },
        reason=(
            "tightest stacked pitch (flush rivet) combined with the only section that "
            "thickens both faces plus the proud end shoe, on the narrowest slats"
        ),
    ),
    corner_case(
        "min_chain_angle_dial_square_flat",
        {
            "hinge_style": "angle_dial",
            "end_profile": "square_paddle",
            "blade_section": "flat_slat",
            "tip_treatment": "plain_tip",
            "segment_count": 2,
            "segment_length_m": 0.22,
            "segment_width_m": 0.040,
        },
        reason="minimum single-fold bevel rule (source-like) with the dial hub",
    ),
    corner_case(
        "short_narrow_spine_shoe_flush",
        {
            "hinge_style": "flush_rivet",
            "end_profile": "round_lug",
            "blade_section": "ridged_spine",
            "tip_treatment": "brass_shoe",
            "segment_count": 8,
            "segment_length_m": 0.14,
            "segment_width_m": 0.026,
        },
        reason=(
            "narrowest slat with the widest relative spine and the flush pitch: the "
            "tightest scale-band land the section descriptor can produce"
        ),
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_picturex_0611_folding_ruler",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_folding_ruler_tests",
    "slot_choices_for_config",
]
