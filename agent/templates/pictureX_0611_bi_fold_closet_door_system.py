# SPDX-License-Identifier: Apache-2.0

"""Self-contained bi-fold closet door system template.

The grounded ``opening_frame`` part lines the opening: two side jambs, a sill, a
header and a CadQuery U-track whose web and two downward lips leave a real open
channel, plus one mullion post per extra pair.  Each of ``bifold_pair_count``
bays carries a ``pivot_leaf`` on a REVOLUTE (+z) jamb pivot followed by the rest
of the fold set on REVOLUTE (+z) centre hinges; each centre hinge MIMICS the
bay's own jamb joint at -2.0 then +2.0 down the chain, which is exactly the
fold constraint that keeps the free edge on the track, so a bay has one honest
degree of freedom however many leaves it has.

Three slots vary over that chain: ``fold_set`` (a two-leaf pair or a three-leaf
accordion), ``leaf_face`` (plain slab, framed mirror, pitched louvers, raised
panels, glazed lite) and ``hardware_set`` (floor pivot pin with a track roller,
jamb butt hinges, heavy full-height pivots, a dual track, or a top-hung
carrier).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    Mimic,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

FoldSet = Literal["pair_fold", "trifold_fold"]
LeafFace = Literal["plain_slab", "mirrored", "louvered", "raised_panel", "glass_lite"]
HardwareSet = Literal[
    "jamb_pivot",
    "butt_hinge",
    "top_hung",
    "dual_track",
    "heavy_pivot",
]
PaletteStyle = Literal["white_paint", "oak_veneer", "walnut", "graphite"]

FOLD_SETS: tuple[FoldSet, ...] = ("pair_fold", "trifold_fold")
LEAF_FACES: tuple[LeafFace, ...] = (
    "plain_slab",
    "mirrored",
    "louvered",
    "raised_panel",
    "glass_lite",
)
HARDWARE_SETS: tuple[HardwareSet, ...] = (
    "jamb_pivot",
    "butt_hinge",
    "top_hung",
    "dual_track",
    "heavy_pivot",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("white_paint", "oak_veneer", "walnut", "graphite")


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("fold_set", FOLD_SETS),
        component_slot("leaf_face", LEAF_FACES),
        component_slot("hardware_set", HARDWARE_SETS),
        multiplicity_slot("bifold_pair_count", (1, 2, 3), item_slot="leaf_face"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_paint": {
        "door": (0.93, 0.93, 0.91, 1.0),
        "frame": (0.88, 0.88, 0.86, 1.0),
        "field": (0.86, 0.88, 0.90, 1.0),
        "metal": (0.74, 0.76, 0.78, 1.0),
        "dark": (0.16, 0.16, 0.17, 1.0),
        "shadow": (0.62, 0.62, 0.60, 1.0),
    },
    "oak_veneer": {
        "door": (0.76, 0.60, 0.38, 1.0),
        "frame": (0.66, 0.51, 0.31, 1.0),
        "field": (0.82, 0.68, 0.46, 1.0),
        "metal": (0.72, 0.74, 0.76, 1.0),
        "dark": (0.22, 0.16, 0.10, 1.0),
        "shadow": (0.52, 0.40, 0.24, 1.0),
    },
    "walnut": {
        "door": (0.36, 0.24, 0.16, 1.0),
        "frame": (0.29, 0.19, 0.13, 1.0),
        "field": (0.44, 0.30, 0.20, 1.0),
        "metal": (0.70, 0.72, 0.74, 1.0),
        "dark": (0.12, 0.08, 0.06, 1.0),
        "shadow": (0.22, 0.15, 0.10, 1.0),
    },
    "graphite": {
        "door": (0.26, 0.27, 0.28, 1.0),
        "frame": (0.20, 0.21, 0.22, 1.0),
        "field": (0.34, 0.35, 0.36, 1.0),
        "metal": (0.76, 0.78, 0.80, 1.0),
        "dark": (0.10, 0.10, 0.11, 1.0),
        "shadow": (0.16, 0.16, 0.17, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
JAMB_W = 0.030  # jamb thickness in x
LEAF_T = 0.022  # leaf thickness in y
LEAF_GAP = 0.004  # gap between a leaf edge and its neighbour
PIVOT_INSET = 0.028  # pivot centre inside the jamb face
TRACK_H = 0.034  # header track height
TRACK_HALF_Y = 0.060  # header track half width (a folding pair needs a wide channel)
TRACK_LIP = 0.008
SILL_H = 0.018
HEADER_H = 0.060
FOLD_MAX = 1.25  # inner-leaf opening angle
# Radial running fit, under the 1 mm assembly-gap tolerance.
FIT = 0.0008
SEAT = 0.0006
ROLLER_R = 0.010
STILE_W = 0.022
# The centre hinge stands off the closet side of the leaf faces on its own
# knuckle straps.  The sign matters: with the knuckle behind the doors the two
# slabs swing apart as the pair folds, instead of closing onto each other.
KNUCKLE_R = 0.009
# Two knuckles 40 mm apart on the axis, leaving a 0.8 mm running clearance.
KNUCKLE_H = 0.0392
PIVOT_ROD_R = 0.006
# The jamb pivot rod stands in front of the leaf face and the centre hinge
# stands behind it; both keep their hardware clear of the door slab itself.
PIVOT_STANDOFF = 0.018
HINGE_BACK = 0.030
# The lining stands this far in front of the opening plane; the leaves and all
# their hardware swing entirely in front of it.
LINING_FRONT = 0.020


@dataclass(frozen=True)
class Config:
    fold_set: FoldSet = "pair_fold"
    leaf_face: LeafFace = "plain_slab"
    hardware_set: HardwareSet = "jamb_pivot"
    bifold_pair_count: int = 2
    opening_width_m: float | None = None
    opening_height_m: float | None = None
    closet_depth_m: float | None = None
    palette_style: PaletteStyle = "white_paint"
    name: str = "pictureX_0611_bi_fold_closet_door_system"


@dataclass(frozen=True)
class ResolvedConfig:
    fold_set: FoldSet
    leaf_face: LeafFace
    hardware_set: HardwareSet
    bifold_pair_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    opening_width_m: float
    opening_height_m: float
    closet_depth_m: float
    leaf_count: int
    bay_width_m: float
    leaf_span_m: float
    leaf_spans_m: tuple[float, ...]
    leaf_height_m: float
    pivot_inset_m: float
    leaf_y: float
    track_z: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x6D_04_B1_2F)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        fold_set=choices["fold_set"],
        leaf_face=choices["leaf_face"],
        hardware_set=choices["hardware_set"],
        bifold_pair_count=choices["bifold_pair_count"],
        opening_width_m=round(rng.uniform(0.900, 2.600), 4),
        opening_height_m=round(rng.uniform(1.900, 2.450), 4),
        closet_depth_m=round(rng.uniform(0.280, 0.700), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"bi_fold_closet_door_system_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "fold_set": config.fold_set,
            "leaf_face": config.leaf_face,
            "hardware_set": config.hardware_set,
            "bifold_pair_count": config.bifold_pair_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.opening_width_m is not None and not 0.900 <= float(config.opening_width_m) <= 2.600:
        raise ValueError("opening_width_m must be in [0.900, 2.600]")
    if config.opening_height_m is not None and not 1.900 <= float(config.opening_height_m) <= 2.450:
        raise ValueError("opening_height_m must be in [1.900, 2.450]")
    if config.closet_depth_m is not None and not 0.280 <= float(config.closet_depth_m) <= 0.700:
        raise ValueError("closet_depth_m must be in [0.280, 0.700]")

    width = (
        _clamp(config.opening_width_m, 0.900, 2.600)
        if config.opening_width_m is not None
        else 1.800
    )
    height = (
        _clamp(config.opening_height_m, 1.900, 2.450)
        if config.opening_height_m is not None
        else 2.100
    )
    depth = (
        _clamp(config.closet_depth_m, 0.280, 0.700) if config.closet_depth_m is not None else 0.600
    )
    n = int(config.bifold_pair_count)
    # Each pair halves its own bay, so a bay never gets narrower than a real leaf.
    bay = max(0.400, width / n)
    width = bay * n
    # The set starts at the pivot line and has to stop clear of the next
    # mullion, so both the inset and half a post come out of the bay before it
    # is divided between however many leaves the fold set has.
    leaf_count = 2 if config.fold_set == "pair_fold" else 3
    run = bay - PIVOT_INSET - 0.5 * JAMB_W - (leaf_count + 1) * LEAF_GAP
    # A folding door only keeps its free edge on the track if the leaves that
    # swing one way and the leaves that swing the other way cancel out.  A pair
    # does that with two equal halves; an accordion needs its middle leaf to be
    # as wide as the two outer ones together, which is exactly the narrow-wide-
    # narrow proportion real trifold units are built to.
    leaf_spans = (0.5 * run, 0.5 * run) if leaf_count == 2 else (0.25 * run, 0.5 * run, 0.25 * run)
    leaf_span = leaf_spans[0]
    leaf_height = height - SILL_H - TRACK_H - 0.010
    return ResolvedConfig(
        fold_set=config.fold_set,
        leaf_face=config.leaf_face,
        hardware_set=config.hardware_set,
        bifold_pair_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        opening_width_m=width,
        opening_height_m=height,
        closet_depth_m=depth,
        leaf_count=leaf_count,
        bay_width_m=bay,
        leaf_span_m=leaf_span,
        leaf_spans_m=leaf_spans,
        leaf_height_m=leaf_height,
        pivot_inset_m=PIVOT_INSET,
        leaf_y=-(LINING_FRONT + SEAT + 0.5 * LEAF_T),
        track_z=height - TRACK_H,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("fold_set", config.fold_set),
        ("leaf_face", config.leaf_face),
        ("hardware_set", config.hardware_set),
        ("bifold_pair_count", config.bifold_pair_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"bifold_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _box_at(x0, x1, y0, y1, z0, z1):
    return (
        cq.Workplane("XY")
        .transformed(offset=(0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1)))
        .box(x1 - x0, y1 - y0, z1 - z0)
    )


def _local_origin(
    origin: Origin | None, offset: tuple[float, float, float]
) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(value - shift for value, shift in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


def _bay_x0(r: ResolvedConfig, index: int) -> float:
    return -0.5 * r.opening_width_m + index * r.bay_width_m


# --- opening frame -------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("opening_frame", meta={"role": "opening_frame"})
    half_w = 0.5 * r.opening_width_m
    depth = r.closet_depth_m
    for index, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((JAMB_W, depth + LINING_FRONT, r.opening_height_m)),
            origin=Origin(
                xyz=(
                    sx * (half_w + 0.5 * JAMB_W),
                    0.5 * depth - 0.5 * LINING_FRONT,
                    0.5 * r.opening_height_m,
                )
            ),
            material=mats["frame"],
            name=f"side_jamb_{index}", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
        )
    for index in range(1, r.bifold_pair_count):
        frame.visual(
            Box((JAMB_W, 0.5 * depth + LINING_FRONT, r.opening_height_m)),
            origin=Origin(
                xyz=(
                    _bay_x0(r, index),
                    0.25 * depth - 0.5 * LINING_FRONT,
                    0.5 * r.opening_height_m,
                )
            ),
            material=mats["frame"],
            name=f"mullion_post_{index}", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
        )
    sill = _box_at(
        -0.5 * r.opening_width_m - JAMB_W,
        0.5 * r.opening_width_m + JAMB_W,
        -LINING_FRONT,
        depth,
        0.0,
        SILL_H,
    )
    # Each pivot family drops a pin into a real bored socket in the sill.
    pin_r = (0.006 if r.hardware_set == "jamb_pivot" else 0.004) + FIT
    if r.hardware_set != "butt_hinge":
        for index in range(r.bifold_pair_count):
            sill = sill.cut(
                cq.Workplane("XY")
                .transformed(
                    offset=(
                        _bay_x0(r, index) + r.pivot_inset_m,
                        r.leaf_y - PIVOT_STANDOFF,
                        SILL_H - 0.007,
                    )
                )
                .cylinder(height=0.016, radius=pin_r, direct=(0.0, 0.0, 1.0))
            )
    if r.hardware_set == "dual_track":
        # A real second guide channel let into the sill under the leaf line.
        for index in range(r.bifold_pair_count):
            x0 = _bay_x0(r, index) + r.pivot_inset_m
            sill = sill.cut(
                _box_at(
                    x0 - 0.010,
                    x0 + r.bay_width_m - 0.030,
                    r.leaf_y - 0.014,
                    r.leaf_y + 0.014,
                    SILL_H - 0.008,
                    SILL_H + 0.01,
                )
            )
    frame.visual(
        mesh_from_cadquery(sill, "bifold_sill"),
        material=mats["shadow"],
        name="sill", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
    )
    frame.visual(
        Box((r.opening_width_m + 2.0 * JAMB_W, depth + LINING_FRONT, HEADER_H)),
        origin=Origin(
            xyz=(
                0.0,
                0.5 * depth - 0.5 * LINING_FRONT,
                r.opening_height_m + 0.5 * HEADER_H,
            )
        ),
        material=mats["frame"],
        name="header", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
    )
    # A real U-track: a web and two downward lips leaving an open channel.
    track = _box_at(
        -r.opening_width_m * 0.5 - 0.004,
        r.opening_width_m * 0.5 + 0.004,
        r.leaf_y - TRACK_HALF_Y,
        r.leaf_y + TRACK_HALF_Y,
        r.track_z,
        r.track_z + TRACK_H,
    )
    track = track.cut(
        _box_at(
            -r.opening_width_m * 0.5 - 0.01,
            r.opening_width_m * 0.5 + 0.01,
            r.leaf_y - TRACK_HALF_Y + TRACK_LIP,
            r.leaf_y + TRACK_HALF_Y - TRACK_LIP,
            r.track_z - 0.01,
            r.track_z + TRACK_H - 0.010,
        )
    )
    frame.visual(
        mesh_from_cadquery(track, "bifold_header_track"),
        material=mats["metal"],
        name="header_track", material_class_id="metal.aluminum_bare",
    )
    # Every hardware family turns on a real pivot rod: the leaf barrels wrap it
    # with a running fit, so an opening pair never leaves the grounded body.
    for index in range(r.bifold_pair_count):
        frame.visual(
            Cylinder(radius=PIVOT_ROD_R, length=r.opening_height_m),
            origin=Origin(
                xyz=(
                    _bay_x0(r, index) + r.pivot_inset_m,
                    r.leaf_y - PIVOT_STANDOFF,
                    0.5 * r.opening_height_m,
                )
            ),
            material=mats["metal"],
            name=f"pivot_rod_{index}", material_class_id="metal.stainless_matte",
        )
    if r.hardware_set == "jamb_pivot":
        for index in range(r.bifold_pair_count):
            ring = _box_at(-0.014, 0.014, -0.014, 0.014, 0.0, 0.004).cut(
                cq.Workplane("XY")
                .transformed(offset=(0.0, 0.0, 0.002))
                .cylinder(height=0.020, radius=PIVOT_ROD_R - 0.001, direct=(0.0, 0.0, 1.0))
            )
            frame.visual(
                mesh_from_cadquery(ring, f"bifold_floor_socket_{index}"),
                origin=Origin(
                    xyz=(
                        _bay_x0(r, index) + r.pivot_inset_m,
                        r.leaf_y - PIVOT_STANDOFF,
                        SILL_H - 0.004,
                    )
                ),
                material=mats["metal"],
                name=f"hardware_set__jamb_pivot__floor_socket_{index}", material_class_id="metal.stainless_matte",
            )
    return frame


# --- leaf face candidates ------------------------------------------------------
def _leaf_core(part, offset, r: ResolvedConfig, mats: dict[str, str], tag: str) -> None:
    span = r.leaf_span_m
    part.visual(
        Box((span, LEAF_T, r.leaf_height_m)),
        origin=_local_origin(
            Origin(xyz=(0.5 * span, 0.0, 0.5 * r.leaf_height_m)), offset
        ),
        material=mats["door"],
        name=f"{tag}__door_core", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
    )
    for name, x in (("near_stile", 0.012), ("far_stile", span - 0.012)):
        part.visual(
            Box((STILE_W, 0.006, r.leaf_height_m - 0.040)),
            origin=_local_origin(
                Origin(xyz=(x, -0.5 * LEAF_T - 0.003, 0.5 * r.leaf_height_m)),
                offset,
            ),
            material=mats["frame"],
            name=f"{tag}__{name}", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
        )
    for name, z in (("bottom_rail", 0.016), ("top_rail", r.leaf_height_m - 0.016)):
        part.visual(
            Box((span, 0.006, 0.032)),
            origin=_local_origin(
                Origin(xyz=(0.5 * span, -0.5 * LEAF_T - 0.003, z)), offset
            ),
            material=mats["frame"],
            name=f"{tag}__{name}", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
        )


def _leaf_face_plain_slab_build(part, offset, r, mats, tag) -> None:
    _leaf_core(part, offset, r, mats, tag)
    part.visual(
        Box((r.leaf_span_m - 0.060, 0.004, r.leaf_height_m - 0.090)),
        origin=_local_origin(
            Origin(
                xyz=(
                    0.5 * r.leaf_span_m,
                    -0.5 * LEAF_T - 0.002,
                    0.5 * r.leaf_height_m,
                )
            ),
            offset,
        ),
        material=mats["door"],
        name=f"{tag}__leaf_face__plain_slab__flush_field", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
    )


def _leaf_face_mirrored_build(part, offset, r, mats, tag) -> None:
    _leaf_core(part, offset, r, mats, tag)
    part.visual(
        Box((r.leaf_span_m - 0.056, 0.004, r.leaf_height_m - 0.080)),
        origin=_local_origin(
            Origin(
                xyz=(
                    0.5 * r.leaf_span_m,
                    -0.5 * LEAF_T - 0.002,
                    0.5 * r.leaf_height_m,
                )
            ),
            offset,
        ),
        material=mats["field"],
        name=f"{tag}__leaf_face__mirrored__mirror_field", material_class_id="glass.mirror",
    )
    for index, sz in enumerate((-1.0, 1.0)):
        part.visual(
            Box((r.leaf_span_m - 0.048, 0.008, 0.012)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        0.5 * r.leaf_span_m,
                        -0.5 * LEAF_T - 0.004,
                        0.5 * r.leaf_height_m
                        + sz * (0.5 * r.leaf_height_m - 0.040),
                    )
                )
                , offset
            ),
            material=mats["frame"],
            name=f"{tag}__leaf_face__mirrored__glazing_bead_{index}", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
        )


def _leaf_face_louvered_build(part, offset, r, mats, tag) -> None:
    _leaf_core(part, offset, r, mats, tag)
    zone0 = 0.050
    zone1 = r.leaf_height_m - 0.050
    count = max(8, min(22, int((zone1 - zone0) / 0.075)))
    pitch = (zone1 - zone0) / count
    for k in range(count):
        z = zone0 + pitch * (k + 0.5)
        part.visual(
            Box((r.leaf_span_m - 0.048, 0.020, 0.008)),
            origin=_local_origin(
                Origin(
                    xyz=(0.5 * r.leaf_span_m, -0.5 * LEAF_T - 0.004, z),
                    rpy=(-0.52, 0.0, 0.0),
                ),
                offset,
            ),
            material=mats["field"],
            name=f"{tag}__leaf_face__louvered__slat_{k}", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
        )


def _leaf_face_raised_panel_build(part, offset, r, mats, tag) -> None:
    _leaf_core(part, offset, r, mats, tag)
    span = r.leaf_span_m
    fields = 2
    field_h = (r.leaf_height_m - 0.140) / fields
    for k in range(fields):
        z0 = 0.070 + k * field_h
        part.visual(
            Box((span - 0.080, 0.010, field_h - 0.030)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        0.5 * span,
                        -0.5 * LEAF_T - 0.005,
                        z0 + 0.5 * (field_h - 0.030),
                    )
                ),
                offset,
            ),
            material=mats["field"],
            name=f"{tag}__leaf_face__raised_panel__field_{k}", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
        )
        part.visual(
            Box((span - 0.060, 0.005, field_h - 0.014)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        0.5 * span,
                        -0.5 * LEAF_T - 0.0025,
                        z0 + 0.5 * (field_h - 0.030),
                    )
                ),
                offset,
            ),
            material=mats["frame"],
            name=f"{tag}__leaf_face__raised_panel__bevel_{k}", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
        )
    part.visual(
        Box((span, 0.006, 0.028)),
        origin=_local_origin(
            Origin(
                xyz=(
                    0.5 * span,
                    -0.5 * LEAF_T - 0.003,
                    0.070 + field_h - 0.012,
                )
            ),
            offset,
        ),
        material=mats["frame"],
        name=f"{tag}__leaf_face__raised_panel__lock_rail", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
    )


def _leaf_face_glass_lite_build(part, offset, r, mats, tag) -> None:
    """A perimeter frame capturing a rebated translucent field: the leaf really
    reads through instead of being a slab with something applied to it."""
    span = r.leaf_span_m
    frame_w = min(0.056, 0.30 * span)
    core = _box_at(0.0, span, -0.5 * LEAF_T, 0.5 * LEAF_T, 0.0, r.leaf_height_m)
    core = core.cut(
        _box_at(
            frame_w,
            span - frame_w,
            -LEAF_T,
            LEAF_T,
            frame_w,
            r.leaf_height_m - frame_w,
        )
    )
    part.visual(
        mesh_from_cadquery(core, f"bifold_glass_frame_{tag}"),
        origin=_local_origin(None, offset),
        material=mats["door"],
        name=f"{tag}__door_core", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
    )
    part.visual(
        Box(
            (
                span - 2.0 * frame_w + 0.016,
                0.006,
                r.leaf_height_m - 2.0 * frame_w + 0.016,
            )
        ),
        origin=_local_origin(
            Origin(xyz=(0.5 * span, 0.004, 0.5 * r.leaf_height_m)), offset
        ),
        material=mats["field"],
        name=f"{tag}__leaf_face__glass_lite__glass_field", material_class_id="glass.frosted_smooth",
    )
    for index, sz in enumerate((-1.0, 1.0)):
        part.visual(
            Box((span - 2.0 * frame_w + 0.020, 0.008, 0.012)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        0.5 * span,
                        -0.5 * LEAF_T - 0.003,
                        0.5 * r.leaf_height_m
                        + sz * (0.5 * r.leaf_height_m - frame_w + 0.004),
                    )
                )
                , offset
            ),
            material=mats["frame"],
            name=f"{tag}__leaf_face__glass_lite__glazing_bead_{index}", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
        )


_LEAF_BUILDERS = {
    "plain_slab": _leaf_face_plain_slab_build,
    "mirrored": _leaf_face_mirrored_build,
    "louvered": _leaf_face_louvered_build,
    "raised_panel": _leaf_face_raised_panel_build,
    "glass_lite": _leaf_face_glass_lite_build,
}


# --- hardware candidates -------------------------------------------------------
def _hardware_on_pivot_leaf(host, r, mats, index: int) -> None:
    """Whatever carries the inner leaf, always on the same pivot line."""
    barrel = (
        cq.Workplane("XY")
        .cylinder(height=0.070, radius=0.012, direct=(0.0, 0.0, 1.0))
        .cut(
            cq.Workplane("XY").cylinder(
                height=0.20, radius=PIVOT_ROD_R + FIT, direct=(0.0, 0.0, 1.0)
            )
        )
    )
    for k in range(3):
        z = 0.100 + k * (r.leaf_height_m - 0.200) / 2.0
        host.visual(
            mesh_from_cadquery(barrel, f"bifold_pivot_barrel_{index}_{k}"),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["metal"],
            name=f"pivot_barrel_{index}_{k}", material_class_id="metal.stainless_matte",
        )
    if r.hardware_set == "jamb_pivot":
        for k, z in ((0, 0.014), (1, r.leaf_height_m - 0.014)):
            host.visual(
                Box((0.042, LEAF_T - 0.004, 0.026)),
                origin=Origin(xyz=(0.030, PIVOT_STANDOFF - 0.5 * LEAF_T + 0.002, z)),
                material=mats["frame"],
                name=f"hardware_set__jamb_pivot__corner_block_{index}_{k}", material_class_id=("wood.painted_clean" if r.palette_style in {"white_paint", "walnut", "graphite"} else "wood.veneer_panel"),
            )
        # The pivot rod is the pin; the corner blocks are what tie it into the
        # slab, and the sill ring is its socket.
        host.visual(
            Box((0.030, 0.014, 0.020)),
            origin=Origin(xyz=(0.022, PIVOT_STANDOFF - 0.5 * LEAF_T - 0.006, 0.030)),
            material=mats["metal"],
            name=f"hardware_set__jamb_pivot__pivot_strap_{index}", material_class_id="metal.stainless_matte",
        )
    elif r.hardware_set == "butt_hinge":
        for k in range(3):
            z = 0.120 + k * (r.leaf_height_m - 0.240) / 2.0
            host.visual(
                Box((0.030, 0.005, 0.090)),
                origin=Origin(xyz=(0.021, PIVOT_STANDOFF - 0.5 * LEAF_T - 0.0025, z)),
                material=mats["metal"],
                name=f"hardware_set__butt_hinge__hinge_leaf_{index}_{k}", material_class_id="metal.stainless_matte",
            )
            host.visual(
                Box((0.008, 0.010, 0.096)),
                origin=Origin(xyz=(0.014, PIVOT_STANDOFF - 0.5 * LEAF_T - 0.004, z)),
                material=mats["metal"],
                name=f"hardware_set__butt_hinge__knuckle_{index}_{k}", material_class_id="metal.stainless_matte",
            )
    elif r.hardware_set == "heavy_pivot":
        # Full-height pivots: stout corner plates and thicker pins carry the
        # whole leaf, so there is no track roller at all.
        for k, z in ((0, 0.020), (1, r.leaf_height_m - 0.014)):
            host.visual(
                Box((0.052, LEAF_T + 0.006, 0.040 if k == 0 else 0.026)),
                origin=Origin(xyz=(0.034, PIVOT_STANDOFF - 0.5 * LEAF_T + 0.002, z)),
                material=mats["metal"],
                name=f"hardware_set__heavy_pivot__corner_plate_{index}_{k}", material_class_id="metal.stainless_matte",
            )
        host.visual(
            Box((0.026, 0.020, r.leaf_height_m - 0.070)),
            origin=Origin(
                xyz=(0.021, PIVOT_STANDOFF - 0.5 * LEAF_T + 0.002, 0.5 * r.leaf_height_m)
            ),
            material=mats["metal"],
            name=f"hardware_set__heavy_pivot__load_strap_{index}", material_class_id="metal.stainless_matte",
        )
    elif r.hardware_set == "dual_track":
        host.visual(
            Box((0.042, LEAF_T - 0.004, 0.022)),
            origin=Origin(xyz=(0.030, PIVOT_STANDOFF - 0.5 * LEAF_T + 0.002, 0.030)),
            material=mats["metal"],
            name=f"hardware_set__dual_track__roller_bracket_{index}", material_class_id="metal.stainless_matte",
        )
        host.visual(
            Cylinder(radius=0.010, length=0.012),
            origin=Origin(
                xyz=(0.040, PIVOT_STANDOFF - 0.5 * LEAF_T + 0.002, 0.014),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["metal"],
            name=f"hardware_set__dual_track__floor_roller_{index}", material_class_id="metal.stainless_matte",
        )
        host.visual(
            Box((0.030, 0.014, 0.024)),
            origin=Origin(
                xyz=(0.022, PIVOT_STANDOFF - 0.5 * LEAF_T + 0.002, r.leaf_height_m - 0.012)
            ),
            material=mats["metal"],
            name=f"hardware_set__dual_track__top_strap_{index}", material_class_id="metal.stainless_matte",
        )
    else:
        host.visual(
            Box((0.016, 0.036, 0.030)),
            origin=Origin(xyz=(0.018, 0.0, r.leaf_height_m + 0.015)),
            material=mats["metal"],
            name=f"hardware_set__top_hung__carrier_bracket_{index}", material_class_id="metal.stainless_matte",
        )
        host.visual(
            Cylinder(radius=ROLLER_R - 0.002, length=0.014),
            origin=Origin(xyz=(0.018, 0.0, r.leaf_height_m + 0.024), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name=f"hardware_set__top_hung__carrier_roller_{index}", material_class_id="metal.stainless_matte",
        )
        host.visual(
            Box((0.026, 0.012, 0.018)),
            origin=Origin(xyz=(0.020, PIVOT_STANDOFF - 0.5 * LEAF_T - 0.005, 0.020)),
            material=mats["metal"],
            name=f"hardware_set__top_hung__locating_shoe_{index}", material_class_id="metal.stainless_matte",
        )


# --- assembly ------------------------------------------------------------------
def _revolute_z(model, *, name, parent, child, point, lower, upper, mimic=None, meta=None) -> None:
    provider = AxisInterface(
        name=f"{name}__provider", point=point, axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    consumer = AxisInterface(name=f"{name}__consumer", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0))
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=90.0, velocity=2.0, lower=lower, upper=upper),
        mimic=mimic,
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


def _leaf_roles(leaf_count: int) -> tuple[str, ...]:
    """pivot leaf, then any mid leaves, then the leaf that carries the handle."""
    return ("pivot_leaf",) + ("mid_leaf",) * (leaf_count - 2) + ("handle_leaf",)


def _hinge_offset_y(k: int) -> float:
    """Stand-off of hinge ``k`` from the closed leaf plane.

    Hinge 0 is the jamb pivot rod, which sits behind the leaf.  Every centre
    hinge alternates side, because that is exactly what lets an accordion open:
    successive leaves close onto opposite faces, so the knuckle has to stand
    proud on whichever side they are closing.
    """
    if k == 0:
        return -PIVOT_STANDOFF
    return HINGE_BACK if k % 2 else -HINGE_BACK


def _centre_hinge_hardware(parent, child, r, mats, tag: str, b_prev: float, b_k: float) -> None:
    """Straps from each leaf plane out to the shared knuckle line."""
    for k in range(3):
        z = 0.150 + k * (r.leaf_height_m - 0.300) / 2.0
        parent.visual(
            Box((0.030, abs(b_k), 0.010)),
            origin=Origin(xyz=(r.leaf_span_m + LEAF_GAP - 0.018, -b_prev + 0.5 * b_k, z + 0.020)),
            material=mats["metal"],
            name=f"hinge_strap_a_{tag}_{k}", material_class_id="metal.stainless_matte",
        )
        # The two knuckles interleave on the axis with a running fit, so the
        # leaves stay supported through the whole fold instead of parting.
        parent.visual(
            Cylinder(radius=KNUCKLE_R, length=KNUCKLE_H),
            origin=Origin(xyz=(r.leaf_span_m + LEAF_GAP, b_k - b_prev, z + 0.020)),
            material=mats["metal"],
            name=f"hinge_knuckle_a_{tag}_{k}", material_class_id="metal.stainless_matte",
        )
        child.visual(
            Box((0.030, abs(b_k), 0.010)),
            origin=Origin(xyz=(0.012, -0.5 * b_k, z - 0.020)),
            material=mats["metal"],
            name=f"hinge_strap_b_{tag}_{k}", material_class_id="metal.stainless_matte",
        )
        child.visual(
            Cylinder(radius=KNUCKLE_R, length=KNUCKLE_H),
            origin=Origin(xyz=(0.0, 0.0, z - 0.020)),
            material=mats["metal"],
            name=f"hinge_knuckle_b_{tag}_{k}", material_class_id="metal.stainless_matte",
        )


def _build_fold_chain(model: ArticulatedObject, r: ResolvedConfig, mats, frame, index: int) -> None:
    """One bay: a jamb-pivoted leaf followed by the rest of the fold set.

    Every centre hinge mimics the bay's own jamb joint, alternating -2.0 and
    +2.0, so leaf ``k`` ends up at absolute angle ``(-1)**k * a`` while the bay
    keeps a single honest degree of freedom.
    """
    builder = _LEAF_BUILDERS[r.leaf_face]
    roles = _leaf_roles(r.leaf_count)
    # Each leaf is authored against its own span, so the same face builders draw
    # the narrow outer leaves and the wide middle one of an accordion.
    per_leaf = [replace(r, leaf_span_m=span) for span in r.leaf_spans_m]
    pivot_x = _bay_x0(r, index) + r.pivot_inset_m
    leaves = []
    for k, role in enumerate(roles):
        b_k = _hinge_offset_y(k)
        rk = per_leaf[k]
        leaf = model.part(
            f"leaf_face__{r.leaf_face}__{role}_{index}",
            meta={"role": role, "index": index, "leaf_index": k},
        )
        builder(leaf, (0.0, b_k, 0.0), rk, mats, f"{role}_{index}")
        leaves.append(leaf)
        if k == 0:
            _hardware_on_pivot_leaf(leaf, rk, mats, index)
            _revolute_z(
                model,
                name=f"frame_to_pivot_leaf_{index}",
                parent=frame,
                child=leaf,
                point=(pivot_x, r.leaf_y + b_k, SILL_H),
                lower=-FOLD_MAX,
                upper=0.0,
                meta={"positive_motion": "closes the fold set back across the opening"},
            )
            continue
        b_prev = _hinge_offset_y(k - 1)
        _centre_hinge_hardware(
            leaves[k - 1], leaf, per_leaf[k - 1], mats, f"{index}_{k}", b_prev, b_k
        )
        # Odd hinges swing the next leaf back past the previous one (-2.0);
        # even hinges bring it forward again (+2.0).  That alternation is the
        # accordion, and a two-leaf set simply stops after the first term.
        multiplier = -2.0 if k % 2 else 2.0
        _revolute_z(
            model,
            name=f"{roles[k - 1]}_to_{role}_{index}",
            parent=leaves[k - 1],
            child=leaf,
            point=(per_leaf[k - 1].leaf_span_m + LEAF_GAP, b_k - b_prev, 0.0),
            lower=0.0 if multiplier < 0 else -2.0 * FOLD_MAX,
            upper=2.0 * FOLD_MAX if multiplier < 0 else 0.0,
            mimic=Mimic(joint=f"frame_to_pivot_leaf_{index}", multiplier=multiplier, offset=0.0),
        )
    # The free edge of the last leaf is what rides the header channel and
    # carries the pull, whether the set folds in two or in three.
    last = leaves[-1]
    last_span = r.leaf_spans_m[-1]
    face_y = -_hinge_offset_y(len(roles) - 1)
    last.visual(
        Cylinder(radius=ROLLER_R - 0.002, length=0.012),
        origin=Origin(
            xyz=(last_span - 0.018, face_y, r.leaf_height_m + 0.014),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["metal"],
        name=f"track_roller_{index}", material_class_id="metal.stainless_matte",
    )
    last.visual(
        Box((0.030, LEAF_T - 0.006, 0.020)),
        origin=Origin(xyz=(last_span - 0.018, face_y, r.leaf_height_m + 0.002)),
        material=mats["metal"],
        name=f"roller_stem_{index}", material_class_id="metal.stainless_matte",
    )
    last.visual(
        Box((0.020, LEAF_T + 0.024, 0.110)),
        origin=Origin(xyz=(last_span - 0.030, face_y, 0.42 * r.leaf_height_m)),
        material=mats["dark"],
        name=f"pull_handle_{index}", material_class_id="metal.blackened_gunmetal",
    )


def _chain_joint_names(r: ResolvedConfig, index: int) -> tuple[str, ...]:
    roles = _leaf_roles(r.leaf_count)
    return tuple(f"{roles[k - 1]}_to_{roles[k]}_{index}" for k in range(1, len(roles)))


def build_picturex_0611_bi_fold_closet_door_system(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_bi_fold_closet_door_system",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "jamb-pivoted fold pairs running in a header track",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)
    for index in range(r.bifold_pair_count):
        _build_fold_chain(model, r, mats, frame, index)

    fold = {f"frame_to_pivot_leaf_{i}": -FOLD_MAX for i in range(r.bifold_pair_count)}
    model.meta["risk_poses"] = (
        {f"frame_to_pivot_leaf_{i}": 0.0 for i in range(r.bifold_pair_count)},
        dict(fold),
        {f"frame_to_pivot_leaf_{i}": -0.5 * FOLD_MAX for i in range(r.bifold_pair_count)},
    )
    if r.bifold_pair_count > 1:
        model.meta["coupled_joint_pairs"] = (("frame_to_pivot_leaf_0", "frame_to_pivot_leaf_1"),)
    return model


def build_seeded_picturex_0611_bi_fold_closet_door_system(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_bi_fold_closet_door_system(config_from_seed(seed), assets=assets)


# --- authored tests ------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_bi_fold_closet_door_system_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "opening_frame")
    pivots = _parts_by_role(model, "pivot_leaf")
    mids = _parts_by_role(model, "mid_leaf")
    handles = _parts_by_role(model, "handle_leaf")
    joints = {j.name: j for j in model.articulations}
    chains = [_chain_joint_names(r, i) for i in range(r.bifold_pair_count)]
    leaves_per_bay = [
        [pivots[i]] + [m for m in mids if m.meta.get("index") == i] + [handles[i]]
        for i in range(r.bifold_pair_count)
    ]

    def _rev_z(name: str) -> bool:
        j = joints.get(name)
        return (
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 0.0, 1.0)
        )

    ctx.check(
        "category_anchor: lined opening with a jamb-pivoted fold pair per bay",
        len(frames) == 1
        and len(pivots) == r.bifold_pair_count
        and len(handles) == r.bifold_pair_count
        and len(mids) == (r.leaf_count - 2) * r.bifold_pair_count
        and bool(model.root_parts())
        and model.root_parts()[0].name == "opening_frame"
        and all(
            _rev_z(f"frame_to_pivot_leaf_{i}")
            and joints[f"frame_to_pivot_leaf_{i}"].parent == "opening_frame"
            and len(chains[i]) == r.leaf_count - 1
            and all(
                _rev_z(name)
                and joints[name].parent == leaves_per_bay[i][k].name
                and joints[name].child == leaves_per_bay[i][k + 1].name
                for k, name in enumerate(chains[i])
            )
            for i in range(r.bifold_pair_count)
        ),
        details=(
            f"frames={len(frames)} pivots={len(pivots)} mids={len(mids)} "
            f"handles={len(handles)} joints={sorted(joints)}"
        ),
    )

    ctx.check(
        "category_anchor: the outer leaf folds back at twice the inner leaf angle",
        all(
            joints[name].mimic is not None
            and joints[name].mimic.joint == f"frame_to_pivot_leaf_{i}"
            and abs(joints[name].mimic.multiplier - (-2.0 if k % 2 == 0 else 2.0)) < 1e-9
            for i in range(r.bifold_pair_count)
            for k, name in enumerate(chains[i])
        )
        # The leaves that swing each way must cancel, or the free edge would
        # walk out of the header channel as the set folds.
        and abs(
            sum(r.leaf_spans_m)
            - (r.bay_width_m - PIVOT_INSET - 0.5 * JAMB_W - (r.leaf_count + 1) * LEAF_GAP)
        )
        < 1e-9
        and len(r.leaf_spans_m) == r.leaf_count
        and abs(sum(span * (-1.0) ** k for k, span in enumerate(r.leaf_spans_m))) < 1e-9
        and min(r.leaf_spans_m) > 0.080
        and abs(r.bay_width_m * r.bifold_pair_count - r.opening_width_m) < 1e-9
        and r.leaf_height_m < r.opening_height_m - SILL_H,
        details=(
            f"span={r.leaf_span_m} bay={r.bay_width_m} width={r.opening_width_m} "
            f"height={r.leaf_height_m}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    face_ok = {
        "plain_slab": sum(1 for n in visual_names if "plain_slab__flush_field" in n)
        == r.leaf_count * r.bifold_pair_count,
        "mirrored": sum(1 for n in visual_names if "mirrored__mirror_field" in n)
        == r.leaf_count * r.bifold_pair_count,
        "louvered": sum(1 for n in visual_names if "louvered__slat_" in n)
        >= 8 * r.leaf_count * r.bifold_pair_count,
        "raised_panel": sum(1 for n in visual_names if "raised_panel__field_" in n)
        == 2 * r.leaf_count * r.bifold_pair_count,
        "glass_lite": sum(1 for n in visual_names if "glass_lite__glass_field" in n)
        == r.leaf_count * r.bifold_pair_count
        and sum(1 for n in visual_names if "glass_lite__glazing_bead" in n)
        == 2 * r.leaf_count * r.bifold_pair_count,
    }[r.leaf_face]
    ctx.check("category_anchor: leaf_face identity", face_ok, details=f"face={r.leaf_face}")

    knuckles = sum(1 for n in visual_names if n.startswith("hinge_knuckle_a_"))
    ctx.check(
        "category_anchor: fold_set identity",
        {"pair_fold": r.leaf_count == 2, "trifold_fold": r.leaf_count == 3}[r.fold_set]
        and knuckles == 3 * (r.leaf_count - 1) * r.bifold_pair_count
        and all(len(bay) == r.leaf_count for bay in leaves_per_bay)
        # Alternating stand-off: the knuckle line of each centre hinge sits on
        # the opposite face from the one before it, which is what keeps an
        # accordion from folding its leaves into each other.
        and all(
            _hinge_offset_y(k) * _hinge_offset_y(k + 1) < 0.0 for k in range(1, r.leaf_count - 1)
        ),
        details=f"fold_set={r.fold_set} leaves={r.leaf_count} knuckles={knuckles}",
    )

    hardware_ok = {
        "jamb_pivot": sum(1 for n in visual_names if "jamb_pivot__pivot_strap" in n)
        == r.bifold_pair_count
        and sum(1 for n in visual_names if "jamb_pivot__corner_block" in n)
        == 2 * r.bifold_pair_count
        and sum(1 for n in visual_names if "jamb_pivot__floor_socket" in n) == r.bifold_pair_count,
        "butt_hinge": sum(1 for n in visual_names if "butt_hinge__knuckle" in n)
        == 3 * r.bifold_pair_count,
        "heavy_pivot": sum(1 for n in visual_names if "heavy_pivot__corner_plate" in n)
        == 2 * r.bifold_pair_count
        and sum(1 for n in visual_names if "heavy_pivot__load_strap" in n) == r.bifold_pair_count,
        "dual_track": sum(1 for n in visual_names if "dual_track__floor_roller" in n)
        == r.bifold_pair_count
        and sum(1 for n in visual_names if "dual_track__roller_bracket" in n)
        == r.bifold_pair_count,
        "top_hung": sum(1 for n in visual_names if "top_hung__carrier_roller" in n)
        == r.bifold_pair_count
        and sum(1 for n in visual_names if "top_hung__locating_shoe" in n) == r.bifold_pair_count,
    }[r.hardware_set]
    ctx.check("category_anchor: hardware_set identity", hardware_ok, details=f"hw={r.hardware_set}")

    # Motion evidence: folding a pair clears the bay and keeps the free edge on
    # the track line, which is what the -2.0 mimic encodes.
    pivot_joint = joints["frame_to_pivot_leaf_0"]
    closed = ctx.part_world_aabb(handles[0])
    with ctx.pose({pivot_joint: -FOLD_MAX}):
        folded = ctx.part_world_aabb(handles[0])
    bay_x0 = _bay_x0(r, 0)
    # An accordion parks wider than a pair: it stacks the same total leaf run,
    # but every alternating knuckle stand-off adds its own step in x.  The two
    # fractions are the measured worst case over the domain plus headroom.
    parked_frac = 0.62 if r.leaf_count == 2 else 0.76
    ctx.check(
        "folding a bay clears it and stacks back beside the pivot jamb",
        closed is not None
        and folded is not None
        # Closed, the last leaf reaches the far side of its bay; folded, it is
        # stacked back beside the pivot jamb.
        and closed[1][0] > bay_x0 + 0.70 * r.bay_width_m
        and folded[1][0] < bay_x0 + parked_frac * r.bay_width_m,
        details=(
            f"closed={closed} folded={folded} bay_x0={bay_x0} "
            f"leaves={r.leaf_count} frac={parked_frac}"
        ),
    )

    # The whole point of the alternating spans is that the free edge never
    # leaves the header channel, at any fold angle.
    channel = (r.leaf_y - TRACK_HALF_Y + TRACK_LIP, r.leaf_y + TRACK_HALF_Y - TRACK_LIP)
    roller_boxes = []
    for angle in (0.0, -0.25 * FOLD_MAX, -0.5 * FOLD_MAX, -FOLD_MAX):
        with ctx.pose({pivot_joint: angle}):
            roller_boxes.append(ctx.part_element_world_aabb(handles[0], elem=f"track_roller_{0}"))
    ctx.check(
        "the free edge stays in the header channel through the whole fold",
        all(box is not None for box in roller_boxes)
        and all(channel[0] < box[0][1] and box[1][1] < channel[1] for box in roller_boxes),
        details=f"channel={channel} roller={[None if b is None else (b[0][1], b[1][1]) for b in roller_boxes]}",
    )

    # A fold set has to park as a stack of successive steps along the jamb, not
    # collapse onto itself, and some leaf has to swing well clear of the opening
    # plane on the way — the handle leaf for a pair, the mid leaf for a trifold.
    bay_leaves = leaves_per_bay[0]
    closed_boxes = [ctx.part_world_aabb(leaf) for leaf in bay_leaves]
    with ctx.pose({pivot_joint: -FOLD_MAX}):
        stack = [ctx.part_world_aabb(leaf) for leaf in bay_leaves]
    widest = max(r.leaf_spans_m)
    ctx.check(
        "the fold set parks as one step per leaf and swings clear of the plane",
        all(box is not None for box in stack)
        and all(box is not None for box in closed_boxes)
        and all(
            stack[k + 1][0][0] > stack[k][0][0] + 0.25 * r.leaf_span_m
            for k in range(len(stack) - 1)
        )
        and min(box[0][1] for box in stack)
        < min(box[0][1] for box in closed_boxes) - 0.30 * widest,
        details=(
            f"stack_min_x={[b[0][0] for b in stack]} "
            f"swing={min(b[0][1] for b in stack)} closed={min(b[0][1] for b in closed_boxes)}"
        ),
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "narrow_single_pair_plain_pivot",
        {
            "fold_set": "pair_fold",
            "leaf_face": "plain_slab",
            "hardware_set": "jamb_pivot",
            "bifold_pair_count": 1,
            "opening_width_m": 0.900,
            "opening_height_m": 1.900,
            "closet_depth_m": 0.280,
        },
        reason="narrowest single pair in the shallowest closet — tightest fold envelope",
    ),
    corner_case(
        "wide_three_pairs_louvered_top_hung",
        {
            "fold_set": "trifold_fold",
            "leaf_face": "louvered",
            "hardware_set": "heavy_pivot",
            "bifold_pair_count": 3,
            "opening_width_m": 2.600,
            "opening_height_m": 2.450,
            "closet_depth_m": 0.700,
        },
        reason="widest three-bay opening with the tallest louvered accordions on carriers",
    ),
    corner_case(
        "narrow_three_pairs_raised_butt",
        {
            "fold_set": "trifold_fold",
            "leaf_face": "glass_lite",
            "hardware_set": "dual_track",
            "bifold_pair_count": 3,
            "opening_width_m": 0.900,
            "opening_height_m": 2.450,
            "closet_depth_m": 0.280,
        },
        reason="three trifold bays in the narrowest opening — the shortest admissible leaf",
    ),
    corner_case(
        "wide_single_pair_mirrored_pivot",
        {
            "fold_set": "pair_fold",
            "leaf_face": "mirrored",
            "hardware_set": "jamb_pivot",
            "bifold_pair_count": 1,
            "opening_width_m": 2.600,
            "opening_height_m": 1.900,
            "closet_depth_m": 0.700,
        },
        reason="one pair across the widest opening — the longest leaf span and fold sweep",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_picturex_0611_bi_fold_closet_door_system",
    "build_seeded_picturex_0611_bi_fold_closet_door_system",
    "run_picturex_0611_bi_fold_closet_door_system_tests",
]
