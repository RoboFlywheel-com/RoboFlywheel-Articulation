# SPDX-License-Identifier: Apache-2.0

"""Source-backed articulated makeup train cases and travel vanities.

Category identity: one rooted case-body chassis, one rear-hinged mirrored lid and
``palette_count`` independently articulated palette/tray parts that visibly leave the
case body.  Five case forms, five palette topologies, three applicator-storage
interfaces, two pan-module interfaces and two closures combine freely; the host
derives its deck recess, per-station cavities, wall pockets, runners, bearing posts
and hinge knuckles from the selected combination and from N.
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
    MotionLimits,
    Origin,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

CaseForm = Literal[
    "rounded_train_case",
    "round_compact",
    "train_case_tower",
    "book_style_folio",
    "cylindrical_vanity_case",
]
PaletteTopology = Literal[
    "pull_out_drawer",
    "telescoping_side_tray",
    "fan_out_wing",
    "flip_over_leaf",
    "accordion_tier",
]
ApplicatorStorage = Literal[
    "front_organizer_channels",
    "lid_brush_roll",
    "upright_tool_well",
]
PanModuleInterface = Literal["fixed_round_wells", "keyed_snap_tile_grid"]
Closure = Literal["front_latch_strike", "over_center_clasp"]

CASE_FORMS: tuple[CaseForm, ...] = (
    "rounded_train_case",
    "round_compact",
    "train_case_tower",
    "book_style_folio",
    "cylindrical_vanity_case",
)
PALETTE_TOPOLOGIES: tuple[PaletteTopology, ...] = (
    "pull_out_drawer",
    "telescoping_side_tray",
    "fan_out_wing",
    "flip_over_leaf",
    "accordion_tier",
)
APPLICATOR_STORAGES: tuple[ApplicatorStorage, ...] = (
    "front_organizer_channels",
    "lid_brush_roll",
    "upright_tool_well",
)
PAN_MODULE_INTERFACES: tuple[PanModuleInterface, ...] = (
    "fixed_round_wells",
    "keyed_snap_tile_grid",
)
CLOSURES: tuple[Closure, ...] = ("front_latch_strike", "over_center_clasp")
PALETTE_COUNTS: tuple[int, ...] = (2, 3, 4, 5, 6, 7)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("case_form", CASE_FORMS),
        component_slot("palette_topology", PALETTE_TOPOLOGIES),
        component_slot("applicator_storage", APPLICATOR_STORAGES),
        component_slot("pan_module_interface", PAN_MODULE_INTERFACES),
        component_slot("closure", CLOSURES),
        multiplicity_slot(
            "palette_count",
            PALETTE_COUNTS,
            item_slot="palette_topology",
        ),
    )
)

# Shared chassis constants: source-invariant wall / floor / rim thicknesses.
# Everything that changes silhouette is parameterised instead.
WALL_M = 0.010
FLOOR_M = 0.008
RIM_EXTRA_M = 0.007
DECK_SLAB_M = 0.007
LEVEL_WALL_M = 0.005
HINGE_INSET_M = 0.019
PIN_R_M = 0.0032
LID_PLATE_M = 0.008
FIT_M = 0.0004
POST_GAP_M = 0.011
POST_R_M = 0.0075
SIDES: tuple[str, ...] = ("left", "right", "front")
# How far each case form's bands, lips, cover boards or foot rings stand proud
# of the nominal plan face.  Outboard palette hardware clears this by design.
# Fraction of the nominal plan span a straight-edged station may occupy inside
# each case form; curved hosts give a station less usable tangential width.
_FORM_TANGENTIAL_FILL: dict[str, float] = {
    "rounded_train_case": 1.0,
    "round_compact": 0.72,
    "train_case_tower": 1.0,
    "book_style_folio": 1.0,
    "cylindrical_vanity_case": 0.86,
}
_FORM_STANDOFF_M: dict[str, float] = {
    "rounded_train_case": 0.003,
    "round_compact": 0.004,
    "train_case_tower": 0.0065,
    "book_style_folio": 0.007,
    "cylindrical_vanity_case": 0.0035,
}
_ROTARY = ("fan_out_wing", "accordion_tier")
_PRISMATIC = ("pull_out_drawer", "telescoping_side_tray")
# Hinge hardware chain along X: a central pair of lid knuckle tubes flanked by
# the case barrels, meeting with FIT_M of axial interference.
KNUCKLE_R_M = 0.0060
KNUCKLE_GAP_M = 0.020
KNUCKLE_LEN_M = 0.030
BARREL_LEN_M = 0.028
POST_RISE_M = 0.008


@dataclass(frozen=True)
class Station:
    """One articulated palette station and the host geometry it requires."""

    index: int
    side: str
    level: int
    band: int
    band_count: int
    tan_center_m: float
    tan_span_m: float
    tray_width_m: float
    bay_z0_m: float
    bay_height_m: float
    body_len_m: float
    tail_len_m: float
    travel_m: float
    cavity_depth_m: float
    arm_len_m: float
    inner_edge_m: float
    tier_rise_m: float
    leaf_len_m: float
    leaf_thickness_m: float


@dataclass(frozen=True)
class Config:
    case_form: CaseForm = "rounded_train_case"
    palette_topology: PaletteTopology = "pull_out_drawer"
    applicator_storage: ApplicatorStorage = "front_organizer_channels"
    pan_module_interface: PanModuleInterface = "fixed_round_wells"
    closure: Closure = "front_latch_strike"
    palette_count: int = 3
    case_width_m: float | None = None
    case_depth_m: float | None = None
    case_height_m: float | None = None
    lid_depth_m: float | None = None
    tray_height_m: float | None = None
    tray_extension_ratio: float | None = None
    corner_radius_m: float | None = None
    pan_pitch_m: float | None = None
    name: str = "makeup"


@dataclass(frozen=True)
class ResolvedConfig:
    case_form: CaseForm
    palette_topology: PaletteTopology
    applicator_storage: ApplicatorStorage
    pan_module_interface: PanModuleInterface
    closure: Closure
    palette_count: int
    case_width_m: float
    case_depth_m: float
    case_height_m: float
    lid_depth_m: float
    tray_height_m: float
    tray_extension_ratio: float
    corner_radius_m: float
    pan_pitch_m: float
    inner_width_m: float
    inner_depth_m: float
    rim_width_m: float
    recess_width_m: float
    recess_depth_m: float
    recess_drop_m: float
    plan_fill: float
    shell_radius_m: float
    bay_height_m: float
    level_pitch_m: float
    required_height_m: float
    body_height_m: float
    plinth_height_m: float
    deck_z_m: float
    hinge_y_m: float
    hinge_z_m: float
    lid_plan_width_m: float
    lid_plan_depth_m: float
    lid_box_depth_m: float
    lid_open_rad: float
    applicator_zone_depth_m: float
    applicator_zone_y_m: float
    pan_zone_width_m: float
    pan_zone_depth_m: float
    pan_zone_y_m: float
    pan_cols: int
    pan_rows: int
    pan_radius_m: float
    stations: tuple[Station, ...]
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x4D4B5001)
    return Config(
        case_form=choices["case_form"],
        palette_topology=choices["palette_topology"],
        applicator_storage=choices["applicator_storage"],
        pan_module_interface=choices["pan_module_interface"],
        closure=choices["closure"],
        palette_count=choices["palette_count"],
        case_width_m=round(rng.uniform(0.265, 0.405), 4),
        case_depth_m=round(rng.uniform(0.155, 0.235), 4),
        case_height_m=round(rng.uniform(0.055, 0.150), 4),
        lid_depth_m=round(rng.uniform(0.010, 0.055), 4),
        tray_height_m=round(rng.uniform(0.011, 0.026), 4),
        tray_extension_ratio=round(rng.uniform(0.45, 0.82), 4),
        corner_radius_m=round(rng.uniform(0.005, 0.028), 4),
        pan_pitch_m=round(rng.uniform(0.030, 0.052), 4),
    )


def _default(value: float | None, fallback: float) -> float:
    return fallback if value is None else float(value)


def _clamp(value: float, low: float, high: float) -> float:
    return low if value < low else (high if value > high else value)


def _station_layout(
    *,
    topology: PaletteTopology,
    count: int,
    inner_w: float,
    inner_d: float,
    tray_h: float,
    bay_h: float,
    pitch: float,
    plinth: float,
    ratio: float,
    tangential_fill: float,
) -> tuple[Station, ...]:
    """Allocate one station per level around the left / right / front walls.

    Origin 2's three-station left/right/front layout is reproduced exactly at
    N=3; the 5- and 7-tray forks stack same-side stations, so every station
    also owns its own vertical level.  The flip topology additionally splits
    each wall into tangential bands so a leaf never sweeps into its neighbour.
    """
    side_span_total = (inner_d - min(0.034, 0.16 * inner_d)) * tangential_fill
    front_span_total = (inner_w - min(0.034, 0.16 * inner_w)) * tangential_fill
    band_count = math.ceil(count / len(SIDES)) if topology == "flip_over_leaf" else 1
    stations: list[Station] = []
    for index in range(count):
        side = SIDES[index % len(SIDES)]
        band = index // len(SIDES) if topology == "flip_over_leaf" else 0
        span_total = side_span_total if side in ("left", "right") else front_span_total
        span = span_total / band_count
        tan_center = -span_total / 2.0 + (band + 0.5) * span
        radial_inner = inner_w if side in ("left", "right") else inner_d
        body_len = 0.32 * radial_inner
        gain = 1.28 if topology == "telescoping_side_tray" else 1.0
        travel = ratio * body_len * gain
        tail_len = travel + 0.012
        cavity_depth = body_len + tail_len + 0.010
        leaf_len = 0.30 * radial_inner
        tier_rise = 0.0
        if topology == "flip_over_leaf":
            cavity_depth = leaf_len + 0.010
        elif topology == "accordion_tier":
            tier_rise = 0.003 + 0.004 * (index % 3)
        else:
            tier_rise = 0.0
        stations.append(
            Station(
                index=index,
                side=side,
                level=index,
                band=band,
                band_count=band_count,
                tan_center_m=round(tan_center, 6),
                tan_span_m=round(span, 6),
                tray_width_m=round(span - 0.012, 6),
                bay_z0_m=round(FLOOR_M + plinth + index * pitch, 6),
                bay_height_m=round(bay_h, 6),
                body_len_m=round(body_len, 6),
                tail_len_m=round(tail_len, 6),
                travel_m=round(travel, 6),
                cavity_depth_m=round(cavity_depth, 6),
                arm_len_m=round(0.34 * radial_inner, 6),
                inner_edge_m=0.028 if topology == "accordion_tier" else 0.014,
                tier_rise_m=round(tier_rise, 6),
                leaf_len_m=round(leaf_len, 6),
                leaf_thickness_m=round(min(0.010, tray_h * 0.62), 6),
            )
        )
    return tuple(stations)


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "case_form": config.case_form,
            "palette_topology": config.palette_topology,
            "applicator_storage": config.applicator_storage,
            "pan_module_interface": config.pan_module_interface,
            "closure": config.closure,
            "palette_count": config.palette_count,
        }
    )
    width = _default(config.case_width_m, 0.335)
    depth = _default(config.case_depth_m, 0.195)
    height = _default(config.case_height_m, 0.100)
    lid_depth = _default(config.lid_depth_m, 0.028)
    tray_h = _default(config.tray_height_m, 0.018)
    ratio = _default(config.tray_extension_ratio, 0.62)
    corner = _default(config.corner_radius_m, 0.016)
    pan_pitch = _default(config.pan_pitch_m, 0.040)
    count = int(config.palette_count)

    if not 0.265 <= width <= 0.405:
        raise ValueError("case_width_m must be in [0.265, 0.405]")
    if not 0.155 <= depth <= 0.235:
        raise ValueError("case_depth_m must be in [0.155, 0.235]")
    if not 0.055 <= height <= 0.150:
        raise ValueError("case_height_m must be in [0.055, 0.150]")
    if not 0.010 <= lid_depth <= 0.055:
        raise ValueError("lid_depth_m must be in [0.010, 0.055]")
    if not 0.011 <= tray_h <= 0.026:
        raise ValueError("tray_height_m must be in [0.011, 0.026]")
    if not 0.45 <= ratio <= 0.82:
        raise ValueError("tray_extension_ratio must be in [0.45, 0.82]")
    if not 0.005 <= corner <= 0.028:
        raise ValueError("corner_radius_m must be in [0.005, 0.028]")
    if not 0.030 <= pan_pitch <= 0.052:
        raise ValueError("pan_pitch_m must be in [0.030, 0.052]")
    if count not in PALETTE_COUNTS:
        raise ValueError(f"palette_count must be one of {PALETTE_COUNTS}")

    inner_w = width - 2.0 * WALL_M
    inner_d = depth - 2.0 * WALL_M
    rim_w = WALL_M + RIM_EXTRA_M
    recess_w = width - 2.0 * rim_w
    recess_d = depth - 2.0 * rim_w

    # Plan silhouette: three rectangular families with different corner
    # softness, one elliptical compact and one capsule drum.
    if config.case_form == "train_case_tower":
        shell_radius = corner * 0.55
    elif config.case_form == "book_style_folio":
        shell_radius = corner * 1.7
    else:
        shell_radius = corner
    shell_radius = min(shell_radius, 0.40 * recess_d)
    if config.case_form == "round_compact":
        plan_fill = 0.70
    elif config.case_form == "cylindrical_vanity_case":
        plan_fill = 0.88
    else:
        plan_fill = 1.0

    # Bay band: prismatic trays run on side runners inside a through cavity;
    # the rotary and flip topologies need extra height for their bearings.
    if config.palette_topology in _PRISMATIC:
        bay_h = tray_h + 0.009
    elif config.palette_topology == "accordion_tier":
        bay_h = tray_h + 0.025
    elif config.palette_topology == "flip_over_leaf":
        bay_h = tray_h + 0.026
    else:
        bay_h = tray_h + 0.014
    pitch = bay_h + LEVEL_WALL_M

    # The recess is deep enough that the pan module and the applicator zone stay
    # clear of the lid knuckle envelope and of the closed lid box.
    recess_drop = 0.025
    if config.applicator_storage == "upright_tool_well":
        recess_drop += 0.013
    lid_box = lid_depth
    if config.applicator_storage == "lid_brush_roll":
        lid_box = max(lid_box, 0.024)

    required_h = FLOOR_M + count * pitch + DECK_SLAB_M + recess_drop
    body_h = max(height, required_h)
    plinth = body_h - required_h
    deck_z = body_h - recess_drop
    hinge_y = -depth / 2.0 + HINGE_INSET_M
    hinge_z = body_h - FIT_M

    applicator_d = max(0.030, 0.30 * recess_d * plan_fill)
    recess_half_d = (recess_d * plan_fill) / 2.0
    applicator_y = recess_half_d - applicator_d / 2.0 - 0.004
    pan_zone_d = 2.0 * recess_half_d - applicator_d - 0.019
    pan_zone_w = recess_w * plan_fill - 0.008
    pan_zone_y = -recess_half_d + 0.009 + pan_zone_d / 2.0
    if pan_zone_d < 0.028 or pan_zone_w < 0.060:
        raise ValueError("deck recess is too small for the pan module zone")

    pan_cols = int(_clamp(round(pan_zone_w / pan_pitch), 3, 6))
    pan_rows = int(_clamp(round(pan_zone_d / pan_pitch), 1, 3))
    pan_radius = min(
        0.40 * pan_pitch,
        0.42 * pan_zone_w / pan_cols,
        0.42 * pan_zone_d / pan_rows,
    )

    stations = _station_layout(
        topology=config.palette_topology,
        count=count,
        inner_w=inner_w,
        inner_d=inner_d,
        tray_h=tray_h,
        bay_h=bay_h,
        pitch=pitch,
        plinth=plinth,
        ratio=ratio,
        tangential_fill=_FORM_TANGENTIAL_FILL[config.case_form],
    )
    for station in stations:
        opposite = width if station.side in ("left", "right") else depth
        if station.cavity_depth_m + 0.008 >= opposite - WALL_M:
            raise ValueError("palette station cavity would break through the far wall")
        if station.tray_width_m <= 0.022:
            raise ValueError("palette station is too narrow for a real tray")

    return ResolvedConfig(
        case_form=config.case_form,
        palette_topology=config.palette_topology,
        applicator_storage=config.applicator_storage,
        pan_module_interface=config.pan_module_interface,
        closure=config.closure,
        palette_count=count,
        case_width_m=width,
        case_depth_m=depth,
        case_height_m=height,
        lid_depth_m=lid_depth,
        tray_height_m=tray_h,
        tray_extension_ratio=ratio,
        corner_radius_m=corner,
        pan_pitch_m=pan_pitch,
        inner_width_m=inner_w,
        inner_depth_m=inner_d,
        rim_width_m=rim_w,
        recess_width_m=recess_w,
        recess_depth_m=recess_d,
        recess_drop_m=recess_drop,
        plan_fill=plan_fill,
        shell_radius_m=shell_radius,
        bay_height_m=bay_h,
        level_pitch_m=pitch,
        required_height_m=required_h,
        body_height_m=body_h,
        plinth_height_m=plinth,
        deck_z_m=deck_z,
        hinge_y_m=hinge_y,
        hinge_z_m=hinge_z,
        lid_plan_width_m=width - 0.002,
        lid_plan_depth_m=depth - 0.002,
        lid_box_depth_m=lid_box,
        lid_open_rad=1.62,
        applicator_zone_depth_m=applicator_d,
        applicator_zone_y_m=applicator_y,
        pan_zone_width_m=pan_zone_w,
        pan_zone_depth_m=pan_zone_d,
        pan_zone_y_m=pan_zone_y,
        pan_cols=pan_cols,
        pan_rows=pan_rows,
        pan_radius_m=pan_radius,
        stations=stations,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# CadQuery helpers
# ---------------------------------------------------------------------------


def _rounded_box(
    width: float,
    depth: float,
    height: float,
    *,
    center: tuple[float, float, float],
    radius: float,
) -> cq.Workplane:
    """Box with molded-plan corner radii, authored in metres."""
    shape = cq.Workplane("XY").box(width, depth, height)
    safe = min(radius, 0.45 * width, 0.45 * depth)
    if safe > 5.0e-4:
        try:
            shape = shape.edges("|Z").fillet(safe)
        except Exception:  # pragma: no cover - degenerate fillet
            pass
    return shape.translate(center)


def _plan_solid(
    form: CaseForm,
    width: float,
    depth: float,
    height: float,
    *,
    z0: float,
    radius: float,
    center_y: float = 0.0,
) -> cq.Workplane:
    """The case-form plan profile extruded upward from ``z0``."""
    if form == "round_compact":
        return (
            cq.Workplane("XY")
            .ellipse(width / 2.0, depth / 2.0)
            .extrude(height)
            .translate((0.0, center_y, z0))
        )
    if form == "cylindrical_vanity_case":
        return (
            cq.Workplane("XY")
            .slot2D(width, min(depth, width * 0.96), angle=0.0)
            .extrude(height)
            .translate((0.0, center_y, z0))
        )
    return _rounded_box(
        width,
        depth,
        height,
        center=(0.0, center_y, z0 + height / 2.0),
        radius=radius,
    )


def _hollow_tray(
    width: float,
    depth: float,
    height: float,
    *,
    center_xy: tuple[float, float],
    z0: float,
    wall: float,
    floor: float,
    radius: float,
) -> cq.Workplane:
    """Open-topped tray with a true floor, two sides, a front and a back."""
    cx, cy = center_xy
    outer = _rounded_box(
        width,
        depth,
        height,
        center=(cx, cy, z0 + height / 2.0),
        radius=radius,
    )
    inner = _rounded_box(
        width - 2.0 * wall,
        depth - 2.0 * wall,
        height,
        center=(cx, cy, z0 + floor + height / 2.0),
        radius=max(0.001, radius - wall),
    )
    return outer.cut(inner)


def _compound(shapes: list[cq.Workplane]) -> cq.Workplane | None:
    """Fuse many cutters/adders into one shape so OCC runs a single boolean."""
    solids = [solid for shape in shapes for solid in shape.vals()]
    if not solids:
        return None
    return cq.Workplane("XY").newObject([cq.Compound.makeCompound(solids)])


def _cut_all(base: cq.Workplane, cutters: list[cq.Workplane]) -> cq.Workplane:
    """Batch cut with mutually disjoint tools.

    OCC's boolean cut is undefined for a self-intersecting tool, so this must
    only be used where the cutters cannot overlap each other (grid pockets,
    slot recesses).  Overlapping cutters are applied sequentially instead.
    """
    tool = _compound(cutters)
    return base if tool is None else base.cut(tool)


def _cut_each(base: cq.Workplane, cutters: list[cq.Workplane]) -> cq.Workplane:
    """Sequential cut for tools that may overlap one another."""
    for cutter in cutters:
        base = base.cut(cutter)
    return base


def _union_all(base: cq.Workplane, adders: list[cq.Workplane]) -> cq.Workplane:
    tool = _compound(adders)
    return base if tool is None else base.union(tool)


def _pocketed_plate(
    width: float,
    depth: float,
    height: float,
    *,
    center_xy: tuple[float, float],
    z0: float,
    radius: float,
    circle_pockets: tuple[tuple[float, float, float], ...] = (),
    slot_pockets: tuple[tuple[float, float, float, float], ...] = (),
) -> cq.Workplane:
    """Insert plate carrying real shallow circular and slot recesses."""
    cx, cy = center_xy
    plate = _rounded_box(
        width,
        depth,
        height,
        center=(cx, cy, z0 + height / 2.0),
        radius=radius,
    )
    cutters: list[cq.Workplane] = []
    for x, y, pocket_radius in circle_pockets:
        cutters.append(
            cq.Workplane("XY")
            .circle(pocket_radius)
            .extrude(height * 0.70)
            .translate((x, y, z0 + height * 0.52))
        )
    for x, y, length, diameter in slot_pockets:
        cutters.append(
            cq.Workplane("XY")
            .center(x, y)
            .slot2D(length, diameter, angle=0.0)
            .extrude(height * 0.70)
            .translate((0.0, 0.0, z0 + height * 0.52))
        )
    return _cut_all(plate, cutters)


def _axis_tube(
    length: float,
    outer_radius: float,
    inner_radius: float,
    *,
    axis: str,
    center: tuple[float, float, float],
) -> cq.Workplane:
    """Open-ended sleeve along a world axis."""
    plane = {"x": "YZ", "y": "XZ", "z": "XY"}[axis]
    shape = cq.Workplane(plane).circle(outer_radius)
    if inner_radius > 0.0:
        shape = shape.circle(inner_radius)
    return shape.extrude(length / 2.0, both=True).translate(center)


# One source-backed colourway per case form: origin 1 is a matte black case,
# origin 2 a pink moulded travel vanity.  Palette is not a structural axis, so
# these never stand in for a candidate; they only keep the forms legible.
_CASE_COLORWAYS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "rounded_train_case": {
        "shell": (0.19, 0.19, 0.22, 1.0),
        "shell_alt": (0.33, 0.32, 0.37, 1.0),
        "liner": (0.72, 0.68, 0.70, 1.0),
        "tray": (0.42, 0.40, 0.46, 1.0),
    },
    "round_compact": {
        "shell": (0.85, 0.44, 0.56, 1.0),
        "shell_alt": (0.66, 0.27, 0.40, 1.0),
        "liner": (0.96, 0.84, 0.86, 1.0),
        "tray": (0.92, 0.60, 0.70, 1.0),
    },
    "train_case_tower": {
        "shell": (0.30, 0.34, 0.40, 1.0),
        "shell_alt": (0.46, 0.50, 0.56, 1.0),
        "liner": (0.78, 0.79, 0.80, 1.0),
        "tray": (0.54, 0.57, 0.62, 1.0),
    },
    "book_style_folio": {
        "shell": (0.42, 0.28, 0.22, 1.0),
        "shell_alt": (0.58, 0.40, 0.30, 1.0),
        "liner": (0.90, 0.84, 0.74, 1.0),
        "tray": (0.64, 0.47, 0.36, 1.0),
    },
    "cylindrical_vanity_case": {
        "shell": (0.36, 0.56, 0.62, 1.0),
        "shell_alt": (0.24, 0.42, 0.50, 1.0),
        "liner": (0.86, 0.92, 0.93, 1.0),
        "tray": (0.52, 0.72, 0.76, 1.0),
    },
}


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, object]:
    way = _CASE_COLORWAYS[r.case_form]
    return {
        "shell": model.material("case_shell_finish", rgba=way["shell"]),
        "shell_alt": model.material("case_band_finish", rgba=way["shell_alt"]),
        "liner": model.material("case_liner", rgba=way["liner"]),
        "tray": model.material("tray_body_finish", rgba=way["tray"]),
        "hardware": model.material("warm_gold_hardware", rgba=(0.85, 0.66, 0.28, 1.0)),
        "steel": model.material("brushed_steel", rgba=(0.66, 0.68, 0.70, 1.0)),
        "mirror": model.material("mirror_silver", rgba=(0.86, 0.91, 0.94, 1.0)),
        "bristle": model.material("brush_bristle", rgba=(0.32, 0.24, 0.20, 1.0)),
    }


_PAN_COLORS: tuple[tuple[str, tuple[float, float, float, float]], ...] = (
    ("pan_cream", (0.97, 0.88, 0.74, 1.0)),
    ("pan_peach", (0.94, 0.55, 0.42, 1.0)),
    ("pan_coral", (0.87, 0.33, 0.31, 1.0)),
    ("pan_rose", (0.70, 0.26, 0.36, 1.0)),
    ("pan_mauve", (0.62, 0.38, 0.52, 1.0)),
    ("pan_tan", (0.72, 0.48, 0.33, 1.0)),
    ("pan_bronze", (0.66, 0.44, 0.24, 1.0)),
    ("pan_pink", (0.85, 0.41, 0.58, 1.0)),
    ("pan_violet", (0.54, 0.34, 0.70, 1.0)),
    ("pan_blue", (0.30, 0.48, 0.76, 1.0)),
    ("pan_teal", (0.22, 0.62, 0.64, 1.0)),
    ("pan_gold", (0.85, 0.70, 0.30, 1.0)),
)


def _pan_materials(model: ArticulatedObject) -> tuple[object, ...]:
    return tuple(model.material(name, rgba=rgba) for name, rgba in _PAN_COLORS)


# ---------------------------------------------------------------------------
# Case-form shells
# ---------------------------------------------------------------------------


def _shell_cut_solids(r: ResolvedConfig) -> list[cq.Workplane]:
    """Real hinge relief plus one bay cavity / wall pocket per station."""
    # The lid knuckles rotate inside a real relief channel cut through the rear
    # rim; without it the knuckle bodies would occupy chassis material.
    knuckle_span = KNUCKLE_GAP_M + KNUCKLE_LEN_M + 0.0025
    relief_front = r.hinge_y_m + KNUCKLE_R_M + 0.0025
    relief_rear = -r.case_depth_m / 2.0 - 0.006
    relief_bottom = r.hinge_z_m - (KNUCKLE_R_M + 0.0025)
    relief_top = r.body_height_m + 0.008
    cuts: list[cq.Workplane] = [
        _rounded_box(
            2.0 * knuckle_span,
            relief_front - relief_rear,
            relief_top - relief_bottom,
            center=(
                0.0,
                (relief_front + relief_rear) / 2.0,
                (relief_top + relief_bottom) / 2.0,
            ),
            radius=0.0,
        )
    ]
    for station in r.stations:
        half = r.case_width_m / 2.0 if station.side in ("left", "right") else r.case_depth_m / 2.0
        sign = -1.0 if station.side == "left" else 1.0
        z0 = station.bay_z0_m
        height = station.bay_height_m
        if r.palette_topology in _ROTARY:
            # Rotary stations seat their bearing bridge in a real wall pocket.
            radial = WALL_M * 0.7 + 0.004
            tangential = min(station.tan_span_m, 0.052)
        else:
            radial = station.cavity_depth_m
            tangential = station.tan_span_m
        outer = sign * (half + 0.006)
        center = outer - sign * radial / 2.0
        if station.side in ("left", "right"):
            cuts.append(
                _rounded_box(
                    radial,
                    tangential,
                    height,
                    center=(center, station.tan_center_m, z0 + height / 2.0),
                    radius=0.0,
                )
            )
        else:
            cuts.append(
                _rounded_box(
                    tangential,
                    radial,
                    height,
                    center=(station.tan_center_m, center, z0 + height / 2.0),
                    radius=0.0,
                )
            )
    return cuts


def _base_shell(r: ResolvedConfig) -> cq.Workplane:
    """The undrilled outer chassis body for the selected case form."""
    return _plan_solid(
        r.case_form,
        r.case_width_m,
        r.case_depth_m,
        r.body_height_m,
        z0=0.0,
        radius=r.shell_radius_m,
    )


def _deck_recess_solid(r: ResolvedConfig) -> cq.Workplane:
    return _plan_solid(
        r.case_form,
        r.case_width_m - 2.0 * r.rim_width_m,
        r.case_depth_m - 2.0 * r.rim_width_m,
        r.recess_drop_m + 0.020,
        z0=r.deck_z_m,
        radius=max(0.001, r.shell_radius_m - r.rim_width_m),
    )


def _case_form_rounded_train_case_build(r: ResolvedConfig) -> cq.Workplane:
    shell = _base_shell(r)
    lip_outer = _plan_solid(
        r.case_form,
        r.case_width_m + 0.006,
        r.case_depth_m + 0.006,
        0.011,
        z0=r.body_height_m - 0.011,
        radius=r.shell_radius_m + 0.003,
    )
    lip_inner = _plan_solid(
        r.case_form,
        r.case_width_m - 0.004,
        r.case_depth_m - 0.004,
        0.015,
        z0=r.body_height_m - 0.013,
        radius=max(0.001, r.shell_radius_m - 0.002),
    )
    return shell.union(lip_outer.cut(lip_inner))


def _case_form_round_compact_build(r: ResolvedConfig) -> cq.Workplane:
    shell = _base_shell(r)
    rim_outer = _plan_solid(
        r.case_form,
        r.case_width_m + 0.008,
        r.case_depth_m + 0.008,
        0.009,
        z0=r.body_height_m - 0.009,
        radius=0.0,
    )
    rim_inner = _plan_solid(
        r.case_form,
        r.case_width_m - 0.006,
        r.case_depth_m - 0.006,
        0.013,
        z0=r.body_height_m - 0.011,
        radius=0.0,
    )
    base_outer = _plan_solid(
        r.case_form,
        r.case_width_m * 0.86,
        r.case_depth_m * 0.86,
        0.006,
        z0=0.0,
        radius=0.0,
    )
    base_inner = _plan_solid(
        r.case_form,
        r.case_width_m * 0.74,
        r.case_depth_m * 0.74,
        0.010,
        z0=-0.002,
        radius=0.0,
    )
    return shell.union(rim_outer.cut(rim_inner)).union(base_outer.cut(base_inner))


def _case_form_train_case_tower_build(r: ResolvedConfig) -> cq.Workplane:
    shell = _base_shell(r)
    for fraction in (0.30, 0.66):
        z = r.body_height_m * fraction
        rail_outer = _plan_solid(
            r.case_form,
            r.case_width_m + 0.009,
            r.case_depth_m + 0.009,
            0.009,
            z0=z,
            radius=r.shell_radius_m + 0.004,
        )
        rail_inner = _plan_solid(
            r.case_form,
            r.case_width_m - 0.006,
            r.case_depth_m - 0.006,
            0.013,
            z0=z - 0.002,
            radius=max(0.001, r.shell_radius_m),
        )
        shell = shell.union(rail_outer.cut(rail_inner))
    foot_outer = _plan_solid(
        r.case_form,
        r.case_width_m + 0.013,
        r.case_depth_m + 0.013,
        0.010,
        z0=0.0,
        radius=r.shell_radius_m + 0.006,
    )
    foot_inner = _plan_solid(
        r.case_form,
        r.case_width_m - 0.010,
        r.case_depth_m - 0.010,
        0.014,
        z0=-0.002,
        radius=max(0.001, r.shell_radius_m),
    )
    return shell.union(foot_outer.cut(foot_inner))


def _case_form_book_style_folio_build(r: ResolvedConfig) -> cq.Workplane:
    shell = _base_shell(r)
    cover = _plan_solid(
        r.case_form,
        r.case_width_m + 0.014,
        r.case_depth_m + 0.014,
        0.007,
        z0=0.0,
        radius=r.shell_radius_m + 0.006,
    )
    spine = _rounded_box(
        r.case_width_m - 0.030,
        0.018,
        r.body_height_m * 0.80,
        center=(0.0, -r.case_depth_m / 2.0 - 0.006, r.body_height_m * 0.40),
        radius=0.007,
    )
    return shell.union(cover).union(spine)


def _case_form_cylindrical_vanity_case_build(r: ResolvedConfig) -> cq.Workplane:
    shell = _base_shell(r)
    band_z = r.body_height_m * 0.58
    band_outer = _plan_solid(
        r.case_form,
        r.case_width_m + 0.007,
        r.case_depth_m + 0.007,
        0.014,
        z0=band_z,
        radius=0.0,
    )
    band_inner = _plan_solid(
        r.case_form,
        r.case_width_m - 0.006,
        r.case_depth_m - 0.006,
        0.018,
        z0=band_z - 0.002,
        radius=0.0,
    )
    band = band_outer.cut(band_inner)
    front_half = _rounded_box(
        r.case_width_m + 0.020,
        r.case_depth_m,
        0.030,
        center=(0.0, r.case_depth_m / 2.0, band_z + 0.007),
        radius=0.0,
    )
    band = band.intersect(front_half)
    plinth_outer = _plan_solid(
        r.case_form,
        r.case_width_m * 0.94,
        r.case_depth_m * 0.94,
        0.008,
        z0=0.0,
        radius=0.0,
    )
    plinth_inner = _plan_solid(
        r.case_form,
        r.case_width_m * 0.80,
        r.case_depth_m * 0.80,
        0.012,
        z0=-0.002,
        radius=0.0,
    )
    return shell.union(band).union(plinth_outer.cut(plinth_inner))


_CASE_FORM_SHELLS = {
    "rounded_train_case": _case_form_rounded_train_case_build,
    "round_compact": _case_form_round_compact_build,
    "train_case_tower": _case_form_train_case_tower_build,
    "book_style_folio": _case_form_book_style_folio_build,
    "cylindrical_vanity_case": _case_form_cylindrical_vanity_case_build,
}


def _add_case_shell(
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    shape = _cut_each(
        _CASE_FORM_SHELLS[r.case_form](r),
        [_deck_recess_solid(r), *_shell_cut_solids(r)],
    )
    body.visual(
        mesh_from_cadquery(shape, f"makeup_{r.case_form}_shell", tolerance=0.0009),
        material=mats["shell"],
        name=f"case_form__{r.case_form}__chassis_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    liner = _plan_solid(
        r.case_form,
        (r.case_width_m - 2.0 * r.rim_width_m) - 0.004,
        (r.case_depth_m - 2.0 * r.rim_width_m) - 0.004,
        0.004,
        z0=r.deck_z_m - FIT_M,
        radius=max(0.001, r.shell_radius_m - r.rim_width_m),
    )
    body.visual(
        mesh_from_cadquery(liner, f"makeup_{r.case_form}_deck_liner", tolerance=0.0006),
        material=mats["liner"],
        name=f"case_form__{r.case_form}__deck_liner", material_class_id="fabric.velvet",
    )


def _barrel_center_x(r: ResolvedConfig) -> float:
    """Case barrel centre: it abuts the lid knuckle with FIT_M interference."""
    inner = KNUCKLE_GAP_M + KNUCKLE_LEN_M - FIT_M
    return min(inner + BARREL_LEN_M / 2.0, r.case_width_m / 2.0 - 0.012)


def _add_hinge_hardware(
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    # A full-width pin runs through the lid knuckle bores with real radial
    # clearance; the case barrels take the axial thrust.
    body.visual(
        Cylinder(radius=PIN_R_M, length=r.case_width_m - 0.034),
        origin=Origin(
            xyz=(0.0, r.hinge_y_m, r.hinge_z_m),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["hardware"],
        name="case_form__hinge_pin", material_class_id="metal.brass_polished",
    )
    barrel_x = _barrel_center_x(r)
    for index, sign in enumerate((-1.0, 1.0)):
        body.visual(
            Cylinder(radius=KNUCKLE_R_M, length=BARREL_LEN_M),
            origin=Origin(
                xyz=(sign * barrel_x, r.hinge_y_m, r.hinge_z_m),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["hardware"],
            name=f"case_form__hinge_barrel_{index}", material_class_id="metal.brass_polished",
        )
        body.visual(
            Box((0.026, 0.014, 0.013)),
            origin=Origin(
                xyz=(
                    sign * barrel_x,
                    r.hinge_y_m - 0.008,
                    r.hinge_z_m - 0.0075,
                )
            ),
            material=mats["hardware"],
            name=f"case_form__hinge_leaf_{index}", material_class_id="metal.brass_polished",
        )


# ---------------------------------------------------------------------------
# Pan-module interface
# ---------------------------------------------------------------------------


def _pan_grid_positions(r: ResolvedConfig) -> tuple[tuple[float, float], ...]:
    cell_x = r.pan_zone_width_m / r.pan_cols
    cell_y = r.pan_zone_depth_m / r.pan_rows
    positions: list[tuple[float, float]] = []
    for row in range(r.pan_rows):
        for col in range(r.pan_cols):
            x = -r.pan_zone_width_m / 2.0 + (col + 0.5) * cell_x
            y = r.pan_zone_y_m - r.pan_zone_depth_m / 2.0 + (row + 0.5) * cell_y
            positions.append((x, y))
    return tuple(positions)


def _pan_module_interface_fixed_round_wells_build(
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    pans: tuple[object, ...],
) -> None:
    positions = _pan_grid_positions(r)
    insert_t = 0.008
    z0 = r.deck_z_m + 0.0032
    plate = _pocketed_plate(
        r.pan_zone_width_m,
        r.pan_zone_depth_m,
        insert_t,
        center_xy=(0.0, r.pan_zone_y_m),
        z0=z0,
        radius=min(0.012, 0.30 * min(r.pan_zone_width_m, r.pan_zone_depth_m)),
        circle_pockets=tuple((x, y, r.pan_radius_m + 0.0012) for x, y in positions),
    )
    body.visual(
        mesh_from_cadquery(plate, "makeup_round_well_insert", tolerance=0.0005),
        material=mats["liner"],
        name="pan_module_interface__fixed_round_wells__well_insert", material_class_id="fabric.velvet",
    )
    pocket_floor = z0 + insert_t * 0.30
    for index, (x, y) in enumerate(positions):
        body.visual(
            Cylinder(radius=r.pan_radius_m, length=0.0055),
            origin=Origin(xyz=(x, y, pocket_floor + 0.0023)),
            material=pans[index % len(pans)],
            name=f"pan_module_interface__fixed_round_wells__pan_{index}", material_class_id="organic.wax",
        )


def _pan_module_interface_keyed_snap_tile_grid_build(
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    pans: tuple[object, ...],
) -> None:
    positions = _pan_grid_positions(r)
    base_t = 0.006
    rim_h = 0.007
    z0 = r.deck_z_m + 0.0032
    plan_radius = min(0.012, 0.30 * min(r.pan_zone_width_m, r.pan_zone_depth_m))
    base = _rounded_box(
        r.pan_zone_width_m,
        r.pan_zone_depth_m,
        base_t,
        center=(0.0, r.pan_zone_y_m, z0 + base_t / 2.0),
        radius=plan_radius,
    )
    rim_outer = _rounded_box(
        r.pan_zone_width_m,
        r.pan_zone_depth_m,
        rim_h,
        center=(0.0, r.pan_zone_y_m, z0 + base_t + rim_h / 2.0),
        radius=plan_radius,
    )
    rim_inner = _rounded_box(
        r.pan_zone_width_m - 0.011,
        r.pan_zone_depth_m - 0.011,
        rim_h + 0.003,
        center=(0.0, r.pan_zone_y_m, z0 + base_t + rim_h / 2.0),
        radius=max(0.001, plan_radius - 0.005),
    )
    grid = base.union(rim_outer.cut(rim_inner))
    cell_x = r.pan_zone_width_m / r.pan_cols
    cell_y = r.pan_zone_depth_m / r.pan_rows
    for col in range(1, r.pan_cols):
        grid = grid.union(
            _rounded_box(
                0.0034,
                r.pan_zone_depth_m - 0.011,
                rim_h,
                center=(
                    -r.pan_zone_width_m / 2.0 + col * cell_x,
                    r.pan_zone_y_m,
                    z0 + base_t + rim_h / 2.0,
                ),
                radius=0.0,
            )
        )
    for row in range(1, r.pan_rows):
        grid = grid.union(
            _rounded_box(
                r.pan_zone_width_m - 0.011,
                0.0034,
                rim_h,
                center=(
                    0.0,
                    r.pan_zone_y_m - r.pan_zone_depth_m / 2.0 + row * cell_y,
                    z0 + base_t + rim_h / 2.0,
                ),
                radius=0.0,
            )
        )
    # Each cell keeps an asymmetric locating key so a refill tile only snaps in
    # one way round; this is the keyed interface, not decoration.
    key_r = max(0.0018, 0.055 * r.pan_pitch_m)
    for x, y in positions:
        grid = grid.union(
            cq.Workplane("XY")
            .circle(key_r)
            .extrude(0.0026)
            .translate(
                (
                    x - cell_x / 2.0 + key_r + 0.0024,
                    y - cell_y / 2.0 + key_r + 0.0024,
                    z0 + base_t,
                )
            )
        )
    body.visual(
        mesh_from_cadquery(grid, "makeup_snap_tile_grid_insert", tolerance=0.0004),
        material=mats["liner"],
        name="pan_module_interface__keyed_snap_tile_grid__grid_insert", material_class_id="fabric.velvet",
    )
    tile_w = max(0.008, cell_x - 0.009)
    tile_d = max(0.008, cell_y - 0.009)
    for index, (x, y) in enumerate(positions):
        body.visual(
            Box((tile_w, tile_d, 0.0046)),
            origin=Origin(xyz=(x + 0.0018, y + 0.0018, z0 + base_t + 0.0019)),
            material=pans[index % len(pans)],
            name=f"pan_module_interface__keyed_snap_tile_grid__tile_{index}", material_class_id="organic.wax",
        )


_PAN_MODULE_BUILDERS = {
    "fixed_round_wells": _pan_module_interface_fixed_round_wells_build,
    "keyed_snap_tile_grid": _pan_module_interface_keyed_snap_tile_grid_build,
}


# ---------------------------------------------------------------------------
# Applicator storage
# ---------------------------------------------------------------------------


def _applicator_zone_span(r: ResolvedConfig) -> float:
    return r.recess_width_m * r.plan_fill - 0.012


def _applicator_storage_front_organizer_channels_build(
    body: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    span = _applicator_zone_span(r)
    channels = max(3, min(6, int(r.applicator_zone_depth_m / 0.011)))
    plate_t = 0.008
    z0 = r.deck_z_m + 0.0032
    slot_d = min(0.010, (r.applicator_zone_depth_m - 0.009) / channels)
    slots = tuple(
        (
            0.0,
            r.applicator_zone_y_m
            - r.applicator_zone_depth_m / 2.0
            + (i + 0.5) * (r.applicator_zone_depth_m / channels),
            span * 0.86,
            slot_d,
        )
        for i in range(channels)
    )
    plate = _pocketed_plate(
        span,
        r.applicator_zone_depth_m,
        plate_t,
        center_xy=(0.0, r.applicator_zone_y_m),
        z0=z0,
        radius=0.008,
        slot_pockets=slots,
    )
    body.visual(
        mesh_from_cadquery(plate, "makeup_brush_channel_insert", tolerance=0.0005),
        material=mats["liner"],
        name="applicator_storage__front_organizer_channels__channel_insert", material_class_id="fabric.velvet",
    )
    for index, (_, y, length, diameter) in enumerate(slots):
        body.visual(
            Cylinder(radius=diameter * 0.30, length=length * 0.92),
            origin=Origin(
                xyz=(0.0, y, z0 + plate_t * 0.30 + diameter * 0.28),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["bristle"] if index % 2 == 0 else mats["hardware"],
            name=(f"applicator_storage__front_organizer_channels__brush_handle_{index}"), material_class_id="organic.fur_fleece",
        )


def _applicator_storage_lid_brush_roll_build(
    body: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    span = _applicator_zone_span(r)
    # The case keeps a plain open accessory pocket; the applicators move to a
    # fitted roll panel inside the lid box.
    pocket = _hollow_tray(
        span,
        r.applicator_zone_depth_m,
        0.009,
        center_xy=(0.0, r.applicator_zone_y_m),
        z0=r.deck_z_m + 0.0032,
        wall=0.004,
        floor=0.0025,
        radius=0.007,
    )
    body.visual(
        mesh_from_cadquery(pocket, "makeup_accessory_pocket", tolerance=0.0005),
        material=mats["liner"],
        name="applicator_storage__lid_brush_roll__accessory_pocket", material_class_id="fabric.velvet",
    )
    panel_y = r.lid_plan_depth_m * 0.32
    panel_z = r.lid_box_depth_m - 0.0030
    panel = _rounded_box(
        r.lid_plan_width_m * 0.78,
        r.lid_plan_depth_m * 0.24,
        0.0036,
        center=(0.0, panel_y, panel_z + 0.0018),
        radius=0.008,
    )
    lid.visual(
        mesh_from_cadquery(panel, "makeup_lid_brush_panel", tolerance=0.0004),
        material=mats["liner"],
        name="applicator_storage__lid_brush_roll__roll_panel", material_class_id="fabric.velvet",
    )
    sleeves = 6
    pitch = (r.lid_plan_width_m * 0.72) / sleeves
    for index in range(sleeves):
        x = -r.lid_plan_width_m * 0.36 + (index + 0.5) * pitch
        sleeve = _axis_tube(
            0.015,
            0.0036,
            0.0021,
            axis="y",
            center=(x, panel_y - r.lid_plan_depth_m * 0.05, panel_z - 0.0033),
        )
        lid.visual(
            mesh_from_cadquery(
                sleeve,
                f"makeup_lid_brush_sleeve_{index}",
                tolerance=0.00025,
            ),
            material=mats["steel"],
            name=f"applicator_storage__lid_brush_roll__sleeve_{index}", material_class_id="metal.brushed_silver",
        )
        lid.visual(
            Cylinder(radius=0.0021, length=r.lid_plan_depth_m * 0.30),
            origin=Origin(
                xyz=(x, panel_y, panel_z - 0.0033),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["bristle"] if index % 2 == 0 else mats["hardware"],
            name=f"applicator_storage__lid_brush_roll__brush_{index}", material_class_id="organic.fur_fleece",
        )


def _applicator_storage_upright_tool_well_build(
    body: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    span = _applicator_zone_span(r)
    well_h = r.recess_drop_m - 0.007
    well = _hollow_tray(
        span,
        r.applicator_zone_depth_m,
        well_h,
        center_xy=(0.0, r.applicator_zone_y_m),
        z0=r.deck_z_m + 0.0032,
        wall=0.005,
        floor=0.003,
        radius=0.008,
    )
    divider = _rounded_box(
        0.004,
        r.applicator_zone_depth_m - 0.012,
        well_h - 0.004,
        center=(
            0.0,
            r.applicator_zone_y_m,
            r.deck_z_m + 0.0032 + (well_h - 0.004) / 2.0,
        ),
        radius=0.0,
    )
    body.visual(
        mesh_from_cadquery(
            well.union(divider),
            "makeup_upright_tool_well",
            tolerance=0.0005,
        ),
        material=mats["liner"],
        name="applicator_storage__upright_tool_well__tool_well", material_class_id="fabric.velvet",
    )
    tools = 5
    pitch = (span - 0.024) / tools
    tool_len = well_h + 0.004
    for index in range(tools):
        x = -(span - 0.024) / 2.0 + (index + 0.5) * pitch
        body.visual(
            Cylinder(radius=0.0034, length=tool_len),
            origin=Origin(
                xyz=(
                    x,
                    r.applicator_zone_y_m - r.applicator_zone_depth_m * 0.20,
                    r.deck_z_m + 0.0055 + tool_len / 2.0,
                )
            ),
            material=mats["hardware"] if index % 2 == 0 else mats["bristle"],
            name=f"applicator_storage__upright_tool_well__pencil_{index}", material_class_id="metal.brass_polished",
        )
    tube_y = r.applicator_zone_y_m + r.applicator_zone_depth_m * 0.24
    body.visual(
        Box((0.020, 0.018, tool_len)),
        origin=Origin(xyz=(0.0, tube_y, r.deck_z_m + 0.0055 + tool_len / 2.0)),
        material=mats["shell_alt"],
        name="applicator_storage__upright_tool_well__tube", material_class_id="metal.paint_coated",
    )
    body.visual(
        Cylinder(radius=0.0090, length=0.007),
        origin=Origin(xyz=(0.0, tube_y, r.deck_z_m + 0.0055 + tool_len - 0.002)),
        material=mats["hardware"],
        name="applicator_storage__upright_tool_well__tube_cap", material_class_id="metal.brass_polished",
    )


_APPLICATOR_BUILDERS = {
    "front_organizer_channels": _applicator_storage_front_organizer_channels_build,
    "lid_brush_roll": _applicator_storage_lid_brush_roll_build,
    "upright_tool_well": _applicator_storage_upright_tool_well_build,
}


# ---------------------------------------------------------------------------
# Mirrored lid
# ---------------------------------------------------------------------------


def _lid_rear_clearance(r: ResolvedConfig) -> cq.Workplane:
    """The lid stays open toward its own hinge so knuckles never bind."""
    return _rounded_box(
        r.lid_plan_width_m + 0.040,
        0.040,
        r.lid_box_depth_m + LID_PLATE_M + 0.060,
        center=(0.0, -0.010, (r.lid_box_depth_m + LID_PLATE_M) / 2.0 - 0.010),
        radius=0.0,
    )


def _lid_box_shape(r: ResolvedConfig) -> cq.Workplane:
    """Lid box authored about the hinge axis; the plan matches the chassis."""
    center_y = r.case_depth_m / 2.0 - HINGE_INSET_M
    plate = _plan_solid(
        r.case_form,
        r.lid_plan_width_m,
        r.lid_plan_depth_m,
        LID_PLATE_M,
        z0=r.lid_box_depth_m,
        radius=r.shell_radius_m,
        center_y=center_y,
    )
    wall_outer = _plan_solid(
        r.case_form,
        r.lid_plan_width_m,
        r.lid_plan_depth_m,
        r.lid_box_depth_m,
        z0=0.0,
        radius=r.shell_radius_m,
        center_y=center_y,
    )
    wall_inner = _plan_solid(
        r.case_form,
        r.lid_plan_width_m - 2.0 * WALL_M,
        r.lid_plan_depth_m - 2.0 * WALL_M,
        r.lid_box_depth_m + 0.004,
        z0=-0.002,
        radius=max(0.001, r.shell_radius_m - WALL_M),
        center_y=center_y,
    )
    box = plate.union(wall_outer.cut(wall_inner))
    return box.cut(_lid_rear_clearance(r))


def _add_lid(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object:
    lid = model.part(
        "mirror_lid",
        meta={
            "role": "mirror_lid",
            "rear_hinged": True,
            "lid_box_depth_m": r.lid_box_depth_m,
        },
    )
    lid.visual(
        mesh_from_cadquery(
            _lid_box_shape(r),
            f"makeup_{r.case_form}_lid_box",
            tolerance=0.0008,
        ),
        material=mats["shell"],
        name="mirror_lid__lid_box", material_class_id="plastic.opaque_glossy_molded",
    )
    center_y = r.case_depth_m / 2.0 - HINGE_INSET_M + 0.004
    inner_w = r.lid_plan_width_m - 2.0 * WALL_M
    inner_d = r.lid_plan_depth_m - 2.0 * WALL_M
    clearance = _lid_rear_clearance(r)
    mirror = _plan_solid(
        r.case_form,
        inner_w * 0.88,
        inner_d * 0.78,
        0.0024,
        z0=r.lid_box_depth_m - 0.0028,
        radius=max(0.001, r.shell_radius_m - WALL_M),
        center_y=center_y,
    )
    frame_outer = _plan_solid(
        r.case_form,
        inner_w * 0.95,
        inner_d * 0.86,
        0.0046,
        z0=r.lid_box_depth_m - 0.0046,
        radius=max(0.001, r.shell_radius_m - WALL_M),
        center_y=center_y,
    )
    frame_inner = _plan_solid(
        r.case_form,
        inner_w * 0.87,
        inner_d * 0.77,
        0.010,
        z0=r.lid_box_depth_m - 0.007,
        radius=max(0.001, r.shell_radius_m - WALL_M),
        center_y=center_y,
    )
    lid.visual(
        mesh_from_cadquery(
            mirror.cut(clearance),
            "makeup_lid_mirror",
            tolerance=0.0005,
        ),
        material=mats["mirror"],
        name="mirror_lid__inset_mirror", material_class_id="glass.mirror",
    )
    lid.visual(
        mesh_from_cadquery(
            frame_outer.cut(frame_inner).cut(clearance),
            "makeup_lid_mirror_frame",
            tolerance=0.0005,
        ),
        material=mats["liner"],
        name="mirror_lid__mirror_opening_frame", material_class_id="fabric.velvet",
    )
    # Two knuckle sleeves ride the case pin with real radial clearance and abut
    # the case barrels with FIT_M of axial interference: real bearing contact,
    # not an overlap allowance.  A hinge ear strap carries each sleeve back into
    # the lid box plate, exactly as in the source vanity.
    knuckle_x = KNUCKLE_GAP_M + KNUCKLE_LEN_M / 2.0
    # The strap starts inside the sleeve's upper wall and finishes inside the
    # lid plate, so it never encloses the case pin.
    ear_z0 = KNUCKLE_R_M - 0.0008
    ear_z1 = r.lid_box_depth_m + LID_PLATE_M * 0.6
    ear_height = max(0.006, ear_z1 - ear_z0)
    for index, sign in enumerate((-1.0, 1.0)):
        lid.visual(
            Box((KNUCKLE_LEN_M * 0.62, 0.014, ear_height)),
            origin=Origin(xyz=(sign * knuckle_x, 0.005, ear_z0 + ear_height / 2.0)),
            material=mats["hardware"],
            name=f"mirror_lid__hinge_ear_{index}", material_class_id="metal.brass_polished",
        )
        sleeve = _axis_tube(
            KNUCKLE_LEN_M,
            KNUCKLE_R_M,
            PIN_R_M + 0.0008,
            axis="x",
            center=(sign * knuckle_x, 0.0, 0.0),
        )
        lid.visual(
            mesh_from_cadquery(
                sleeve,
                f"makeup_lid_hinge_knuckle_{index}",
                tolerance=0.00022,
            ),
            material=mats["hardware"],
            name=f"mirror_lid__hinge_knuckle_{index}", material_class_id="metal.brass_polished",
        )
    return lid


# ---------------------------------------------------------------------------
# Closure
# ---------------------------------------------------------------------------


def _lid_front_local_y(r: ResolvedConfig) -> float:
    """Local y of the lid box's front outer face, measured from the hinge."""
    return (r.case_depth_m / 2.0 - HINGE_INSET_M) + r.lid_plan_depth_m / 2.0


def _keeper_frame(r: ResolvedConfig) -> tuple[float, float]:
    """Clasp keeper axis (local y, local z) just outboard of the lid wall."""
    return _lid_front_local_y(r) + 0.0047, max(r.lid_box_depth_m * 0.55, 0.0155)


def _closure_front_latch_strike_build(
    model: ArticulatedObject,
    body: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object | None:
    body.visual(
        Box((0.048, 0.011, 0.014)),
        origin=Origin(xyz=(0.0, r.case_depth_m / 2.0 - 0.0035, r.body_height_m - 0.019)),
        material=mats["hardware"],
        name="closure__front_latch_strike__case_strike", material_class_id="metal.brass_polished",
    )
    lid.visual(
        Box((0.040, 0.009, 0.011)),
        origin=Origin(
            xyz=(
                0.0,
                _lid_front_local_y(r) - 0.0035,
                max(r.lid_box_depth_m * 0.45, 0.0064),
            )
        ),
        material=mats["hardware"],
        name="closure__front_latch_strike__lid_catch", material_class_id="metal.brass_polished",
    )
    return None


def _closure_over_center_clasp_build(
    model: ArticulatedObject,
    body: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object:
    # The case strike sits proud of the front wall and just above the latched
    # hook, so the closed clasp reads as engaged with real clearance.
    body.visual(
        Box((0.044, 0.011, 0.014)),
        origin=Origin(xyz=(0.0, r.case_depth_m / 2.0 - 0.0035, r.body_height_m - 0.0195)),
        material=mats["hardware"],
        name="closure__over_center_clasp__case_strike", material_class_id="metal.brass_polished",
    )
    keeper_y, keeper_z = _keeper_frame(r)
    ear_span = 0.030

    for index, sign in enumerate((-1.0, 1.0)):
        lid.visual(
            Box((0.014, 0.009, 0.013)),
            origin=Origin(
                xyz=(
                    sign * (ear_span / 2.0 + 0.0086),
                    keeper_y - 0.0055,
                    keeper_z - 0.0075,
                )
            ),
            material=mats["hardware"],
            name=f"closure__over_center_clasp__keeper_bar_{index}", material_class_id="metal.brass_polished",
        )
    for index, sign in enumerate((-1.0, 1.0)):
        lid.visual(
            Cylinder(radius=0.0035, length=0.010),
            origin=Origin(
                xyz=(sign * (ear_span / 2.0 + 0.005), keeper_y, keeper_z),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["hardware"],
            name=f"closure__over_center_clasp__keeper_ear_{index}", material_class_id="metal.brass_polished",
        )
    clasp = model.part(
        "closure__over_center_clasp__lever",
        meta={
            "role": "closure_clasp",
            "slot": "closure",
            "candidate": "over_center_clasp",
        },
    )
    clasp.visual(
        Cylinder(radius=0.0035, length=ear_span + 0.0008),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["hardware"],
        name="closure__over_center_clasp__lever_pin", material_class_id="metal.brass_polished",
    )
    clasp.visual(
        Box((0.020, 0.009, 0.022)),
        origin=Origin(xyz=(0.0, 0.0055, -0.010)),
        material=mats["hardware"],
        name="closure__over_center_clasp__lever_arm", material_class_id="metal.brass_polished",
    )
    clasp.visual(
        Box((0.040, 0.012, 0.010)),
        origin=Origin(xyz=(0.0, 0.013, -0.024)),
        material=mats["hardware"],
        name="closure__over_center_clasp__lever_grip", material_class_id="metal.brass_polished",
    )
    clasp.visual(
        Box((0.038, 0.011, 0.008)),
        origin=Origin(xyz=(0.0, 0.0060, -0.0308)),
        material=mats["hardware"],
        name="closure__over_center_clasp__lever_hook", material_class_id="metal.brass_polished",
    )
    return clasp


_CLOSURE_BUILDERS = {
    "front_latch_strike": _closure_front_latch_strike_build,
    "over_center_clasp": _closure_over_center_clasp_build,
}


# ---------------------------------------------------------------------------
# Palette trays
# ---------------------------------------------------------------------------


def _add_tray_pans(
    part: object,
    *,
    prefix: str,
    center_x: float,
    center_y: float,
    span_x: float,
    span_y: float,
    z_seat: float,
    pan_pitch: float,
    pans: tuple[object, ...],
    color_shift: int,
    pan_height: float = 0.0045,
) -> int:
    if span_x <= 0.010 or span_y <= 0.010:
        return 0
    cols = int(_clamp(int(span_x / pan_pitch), 1, 3))
    rows = int(_clamp(int(span_y / pan_pitch), 1, 2))
    cell_x = span_x / cols
    cell_y = span_y / rows
    radius = min(0.40 * pan_pitch, 0.42 * cell_x, 0.42 * cell_y)
    if radius <= 0.0035:
        return 0
    index = 0
    for row in range(rows):
        for col in range(cols):
            x = center_x - span_x / 2.0 + (col + 0.5) * cell_x
            y = center_y - span_y / 2.0 + (row + 0.5) * cell_y
            part.visual(
                Cylinder(radius=radius, length=abs(pan_height)),
                origin=Origin(xyz=(x, y, z_seat)),
                material=pans[(index + color_shift) % len(pans)],
                name=f"{prefix}_pan_{index}", material_class_id="organic.wax",
            )
            index += 1
    return index


def _prismatic_frame(
    r: ResolvedConfig,
    station: Station,
) -> tuple[float, float, float, float, tuple[float, float, float], str]:
    """Return (half, sign, outer_u, tray_len, joint axis, long axis)."""
    if station.side in ("left", "right"):
        half = r.case_width_m / 2.0
        long_axis = "x"
    else:
        half = r.case_depth_m / 2.0
        long_axis = "y"
    sign = -1.0 if station.side == "left" else 1.0
    tray_len = station.body_len_m + station.tail_len_m
    outer_u = sign * (half + 0.002)
    axis = (sign, 0.0, 0.0) if long_axis == "x" else (0.0, sign, 0.0)
    return half, sign, outer_u, tray_len, axis, long_axis


def _drawer_shell(
    r: ResolvedConfig,
    station: Station,
    *,
    telescoping: bool,
) -> cq.Workplane:
    """Hollow tray plus its captured slide tail, in tray-local coordinates."""
    _half, sign, _outer_u, tray_len, _axis, long_axis = _prismatic_frame(r, station)
    width = station.tray_width_m
    tray_h = r.tray_height_m
    body_center_u = sign * (tray_len / 2.0 - station.body_len_m / 2.0)

    def place(u: float, v: float) -> tuple[float, float]:
        return (u, v) if long_axis == "x" else (v, u)

    def plan(long: float, cross: float) -> tuple[float, float]:
        return (long, cross) if long_axis == "x" else (cross, long)

    if telescoping:
        carriage_len = station.body_len_m * 0.44
        inner_len = station.body_len_m - carriage_len * 0.30
        carriage_center = sign * (tray_len / 2.0 - station.body_len_m + carriage_len / 2.0)
        inner_center = sign * (tray_len / 2.0 - inner_len / 2.0)
        cx, cy = place(carriage_center, 0.0)
        cw, cd = plan(carriage_len, width * 0.80)
        carriage = _hollow_tray(
            cw,
            cd,
            tray_h * 0.62,
            center_xy=(cx, cy),
            z0=0.003,
            wall=0.004,
            floor=0.0026,
            radius=0.005,
        )
        ix, iy = place(inner_center, 0.0)
        iw, idp = plan(inner_len, width)
        inner = _hollow_tray(
            iw,
            idp,
            tray_h,
            center_xy=(ix, iy),
            z0=0.003,
            wall=0.0045,
            floor=0.003,
            radius=0.006,
        )
        shell = carriage.union(inner)
        gx, gy = place(sign * (tray_len / 2.0 - inner_len), 0.0)
        gw, gd = plan(0.007, width * 0.92)
        shell = shell.union(
            _rounded_box(
                gw,
                gd,
                tray_h * 0.88,
                center=(gx, gy, 0.003 + tray_h * 0.44),
                radius=0.0,
            )
        )
    else:
        bx, by = place(body_center_u, 0.0)
        bw, bd = plan(station.body_len_m, width)
        shell = _hollow_tray(
            bw,
            bd,
            tray_h,
            center_xy=(bx, by),
            z0=0.003,
            wall=0.0045,
            floor=0.003,
            radius=0.006,
        )
        row, rod = plan(station.body_len_m + 0.005, width + 0.005)
        riw, rid = plan(station.body_len_m - 0.010, width - 0.010)
        rim_outer = _rounded_box(
            row,
            rod,
            0.0035,
            center=(bx, by, 0.003 + tray_h - 0.0017),
            radius=0.006,
        )
        rim_inner = _rounded_box(
            riw,
            rid,
            0.007,
            center=(bx, by, 0.003 + tray_h - 0.0017),
            radius=0.003,
        )
        shell = shell.union(rim_outer.cut(rim_inner))

    return shell


def _drawer_hardware(
    r: ResolvedConfig,
    station: Station,
) -> list[tuple[str, tuple[float, float, float], tuple[float, float, float]]]:
    """Twin carrier rails, inner crossbar, slide rails and the front pull.

    These are emitted as separate primitives on the tray part so the exact
    collision solver sees the real running surfaces instead of one fused mesh.
    """
    _half, sign, _outer_u, tray_len, _axis, long_axis = _prismatic_frame(r, station)
    width = station.tray_width_m
    tray_h = r.tray_height_m
    tail_center_u = -sign * (tray_len / 2.0 - station.tail_len_m / 2.0)

    def place(u: float, v: float) -> tuple[float, float]:
        return (u, v) if long_axis == "x" else (v, u)

    def plan(long: float, cross: float) -> tuple[float, float]:
        return (long, cross) if long_axis == "x" else (cross, long)

    items: list[tuple[str, tuple[float, float, float], tuple[float, float, float]]] = []
    rail_w = 0.018
    for index, rail_sign in enumerate((-1.0, 1.0)):
        rx, ry = place(tail_center_u, rail_sign * (width / 2.0 - rail_w / 2.0))
        rw, rd = plan(station.tail_len_m, rail_w)
        items.append((f"carrier_rail_{index}", (rw, rd, 0.0045), (rx, ry, 0.00225)))
    cx, cy = place(-sign * (tray_len / 2.0 - 0.010), 0.0)
    cw, cd = plan(0.016, width * 0.92)
    items.append(("carrier_crossbar", (cw, cd, 0.0045), (cx, cy, 0.00225)))
    for index, rail_sign in enumerate((-1.0, 1.0)):
        sx, sy = place(0.0, rail_sign * (width / 2.0 - 0.004))
        sw, sd = plan(tray_len, 0.008)
        items.append((f"slide_rail_{index}", (sw, sd, 0.0035), (sx, sy, 0.00175)))
    fx, fy = place(sign * (tray_len / 2.0 + 0.0035), 0.0)
    fw, fd = plan(0.008, width * 0.94)
    items.append(("front_pull", (fw, fd, tray_h * 0.88), (fx, fy, 0.003 + tray_h * 0.44)))
    return items


def _build_prismatic_station(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    pans: tuple[object, ...],
    station: Station,
    *,
    telescoping: bool,
) -> object:
    _half, sign, outer_u, tray_len, axis, long_axis = _prismatic_frame(r, station)
    footprint_center_u = outer_u - sign * tray_len / 2.0
    runner_top = station.bay_z0_m + 0.0035
    width = station.tray_width_m
    prefix = f"palette_topology__{r.palette_topology}__station_{station.index}"

    def place(u: float, v: float) -> tuple[float, float]:
        return (u, v) if long_axis == "x" else (v, u)

    def plan(long: float, cross: float) -> tuple[float, float]:
        return (long, cross) if long_axis == "x" else (cross, long)

    runner_len = station.cavity_depth_m - 0.010
    runner_center_u = outer_u + sign * 0.004 - sign * (station.cavity_depth_m / 2.0)
    for rail_index, rail_sign in enumerate((-1.0, 1.0)):
        rx, ry = place(runner_center_u, rail_sign * (width / 2.0 - 0.004))
        rw, rd = plan(runner_len, 0.010)
        body.visual(
            Box((rw, rd, 0.0043)),
            origin=Origin(xyz=(rx, ry, station.bay_z0_m + 0.00135)),
            material=mats["steel"],
            name=f"{prefix}_runner_{rail_index}", material_class_id="metal.brushed_silver",
        )
    # A real back stop closes the cavity and carries the retracted tray.
    sx, sy = place(outer_u - sign * (station.cavity_depth_m - 0.004), 0.0)
    sw, sd = plan(0.006, width + 0.008)
    body.visual(
        Box((sw, sd, station.bay_height_m * 0.78)),
        origin=Origin(xyz=(sx, sy, station.bay_z0_m + station.bay_height_m * 0.39)),
        material=mats["shell_alt"],
        name=f"{prefix}_cavity_backstop", material_class_id="metal.paint_coated",
    )

    part = model.part(
        f"palette_topology__{r.palette_topology}__tray_{station.index}",
        meta={
            "role": "palette_tray",
            "slot": "palette_topology",
            "candidate": r.palette_topology,
            "station_index": station.index,
            "station_side": station.side,
            "hollow_tray": True,
            "travel_m": station.travel_m,
        },
    )
    part.visual(
        mesh_from_cadquery(
            _drawer_shell(r, station, telescoping=telescoping),
            f"makeup_{r.palette_topology}_tray_{station.index}",
            tolerance=0.0006,
        ),
        material=mats["tray"],
        name=f"{prefix}_tray_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    for local_name, size, center in _drawer_hardware(r, station):
        part.visual(
            Box(size),
            origin=Origin(xyz=center),
            material=mats["steel"] if "slide" in local_name else mats["tray"],
            name=f"{prefix}_{local_name}", material_class_id="plastic.opaque_glossy_molded",
        )
    body_center_u = sign * (tray_len / 2.0 - station.body_len_m / 2.0)
    px, py = place(body_center_u, 0.0)
    span_long = station.body_len_m - 0.016
    span_cross = width - 0.016
    span_x, span_y = plan(span_long, span_cross)
    _add_tray_pans(
        part,
        prefix=prefix,
        center_x=px,
        center_y=py,
        span_x=span_x,
        span_y=span_y,
        z_seat=0.003 + 0.003 + 0.0022,
        pan_pitch=r.pan_pitch_m,
        pans=pans,
        color_shift=station.index * 3,
    )

    fx, fy = place(footprint_center_u, station.tan_center_m)
    extent = plan(station.cavity_depth_m, station.tan_span_m)
    consumer_extent = plan(tray_len, width)
    provider = PlaneInterface(
        name=f"case_form.palette_bay_{station.index}",
        point=(fx, fy, runner_top - FIT_M),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=extent,
    )
    consumer = PlaneInterface(
        name=f"palette_topology.tray_footprint_{station.index}",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=consumer_extent,
    )
    placement = mate_planes(provider, consumer, margin=0.0015)
    model.articulation(
        f"palette_topology__{r.palette_topology}__tray_{station.index}_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=part,
        origin=placement.origin,
        axis=axis,
        motion_limits=MotionLimits(
            effort=16.0,
            velocity=0.20,
            lower=0.0,
            upper=station.travel_m,
        ),
        meta={
            "motion": "positive extends the palette tray out of its host cavity",
            "station_side": station.side,
        },
    )
    return part


def _plan_face_offset(
    form: CaseForm,
    width: float,
    depth: float,
    *,
    side: str,
    tangential: float,
) -> float:
    """Radial distance from the plan centre to the real surface at ``tangential``.

    Outboard bearing bridges and cantilever shelves have to reach the actual
    curved wall of an elliptical or capsule host, not the bounding-box face.
    """
    if side in ("left", "right"):
        span, cross = width / 2.0, depth / 2.0
    else:
        span, cross = depth / 2.0, width / 2.0
    t = min(abs(tangential), cross * 0.999)
    if form == "round_compact":
        return span * math.sqrt(max(0.0, 1.0 - (t / cross) ** 2))
    if form == "cylindrical_vanity_case":
        radius = min(depth, width * 0.96) / 2.0
        straight = max(0.0, width / 2.0 - radius)
        if side in ("left", "right"):
            return straight + math.sqrt(max(0.0, radius**2 - min(t, radius) ** 2))
        if t <= straight:
            return radius
        return math.sqrt(max(0.0, radius**2 - (t - straight) ** 2))
    return span


def _min_plan_face(
    r: ResolvedConfig,
    *,
    side: str,
    tangentials: tuple[float, ...],
) -> float:
    return min(
        _plan_face_offset(
            r.case_form,
            r.case_width_m,
            r.case_depth_m,
            side=side,
            tangential=t,
        )
        for t in tangentials
    )


def _post_gap(r: ResolvedConfig) -> float:
    """Radial standoff of an outboard bearing post from the plan face."""
    return max(
        POST_GAP_M,
        _FORM_STANDOFF_M[r.case_form] + POST_R_M + 0.0018,
    )


def _leaf_standoff(r: ResolvedConfig) -> float:
    """Radial standoff of a flip leaf's inner edge from the plan face."""
    return _FORM_STANDOFF_M[r.case_form] + 0.0022


def _rotary_post_frame(
    r: ResolvedConfig,
    station: Station,
) -> tuple[float, float, float, tuple[float, float, float, float]]:
    """Post centre (x, y), joint z and the tray's local plan rectangle."""
    half = r.case_width_m / 2.0 if station.side in ("left", "right") else r.case_depth_m / 2.0
    length = station.arm_len_m
    width = station.tray_width_m
    gap = _post_gap(r)
    if station.side == "left":
        px = -(half + gap)
        py = station.tan_center_m + station.tan_span_m / 2.0 - 0.012
        rect = (-length, 0.0, -width, 0.0)
    elif station.side == "right":
        px = half + gap
        py = station.tan_center_m - station.tan_span_m / 2.0 + 0.012
        rect = (0.0, length, 0.0, width)
    else:
        px = station.tan_center_m - station.tan_span_m / 2.0 + 0.012
        py = half + gap
        rect = (-width, 0.0, 0.0, length)
    post_top = station.bay_z0_m + POST_RISE_M
    return px, py, post_top - FIT_M, rect


def _rotary_tray_rect(station: Station) -> tuple[float, float, float, float]:
    x0, x1, y0, y1 = (
        (-station.arm_len_m, 0.0, -station.tray_width_m, 0.0)
        if station.side == "left"
        else (
            (0.0, station.arm_len_m, 0.0, station.tray_width_m)
            if station.side == "right"
            else (-station.tray_width_m, 0.0, 0.0, station.arm_len_m)
        )
    )
    inner = station.inner_edge_m
    if x1 == 0.0 and x0 < 0.0:
        x1 = -inner
    elif x0 == 0.0 and x1 > 0.0:
        x0 = inner
    if y1 == 0.0 and y0 < 0.0:
        y1 = -inner
    elif y0 == 0.0 and y1 > 0.0:
        y0 = inner
    return x0, x1, y0, y1


def _rotary_tray_shape(
    r: ResolvedConfig,
    station: Station,
    *,
    accordion: bool,
) -> cq.Workplane:
    x0, x1, y0, y1 = _rotary_tray_rect(station)
    length_x = abs(x1 - x0)
    length_y = abs(y1 - y0)
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    rise = station.tier_rise_m if accordion else 0.0
    tray = _hollow_tray(
        length_x,
        length_y,
        r.tray_height_m,
        center_xy=(cx, cy),
        z0=rise,
        wall=0.0045,
        floor=0.003,
        radius=0.006,
    )
    # The pivot is carried by an outboard post and a low-profile hub.  The
    # former full-height boss read as a rod inserted through the makeup pan;
    # keep only a shallow bearing seat below the tray floor and bridge it to
    # the tray's inner edge with a short gusset.
    hub_depth = max(0.004, min(0.006, r.tray_height_m * 0.30))
    hub = (
        cq.Workplane("XY")
        .circle(POST_R_M * 1.08)
        # Start at the joint plane so the hidden shank captures the outboard
        # post even when an accordion tier is raised; only ``hub_depth`` is
        # visible above the tray floor.
        .extrude(rise + hub_depth)
        .translate((0.0, 0.0, 0.0))
    )
    bridge_depth = max(0.0035, min(0.0055, r.tray_height_m * 0.26))
    # Extend beneath the rounded tray corner so the low bridge is genuinely
    # fused to the tray floor rather than merely touching its tangent edge.
    inner = station.inner_edge_m
    bridge_run = inner + 0.012
    bridge_span = max(2.0 * POST_R_M, min(0.022, station.tray_width_m * 0.48))
    neck_span = bridge_span
    neck_depth = station.tray_width_m / 2.0 + POST_R_M
    if station.side == "right":
        bridge = _rounded_box(
            bridge_run,
            bridge_span,
            bridge_depth,
            center=(bridge_run / 2.0, station.tray_width_m / 2.0, rise + 0.001),
            radius=0.0015,
        )
        neck = _rounded_box(
            neck_span,
            neck_depth,
            bridge_depth,
            center=(0.0, neck_depth / 2.0, rise + 0.001),
            radius=0.0015,
        )
    elif station.side == "left":
        bridge = _rounded_box(
            bridge_run,
            bridge_span,
            bridge_depth,
            center=(-bridge_run / 2.0, -station.tray_width_m / 2.0, rise + 0.001),
            radius=0.0015,
        )
        neck = _rounded_box(
            neck_span,
            neck_depth,
            bridge_depth,
            center=(0.0, -neck_depth / 2.0, rise + 0.001),
            radius=0.0015,
        )
    else:
        bridge = _rounded_box(
            bridge_span,
            bridge_run,
            bridge_depth,
            center=(-station.tray_width_m / 2.0, bridge_run / 2.0, rise + 0.001),
            radius=0.0015,
        )
        neck = _rounded_box(
            neck_depth,
            neck_span,
            bridge_depth,
            center=(-neck_depth / 2.0, 0.0, rise + 0.001),
            radius=0.0015,
        )
    return tray.union(hub).union(bridge).union(neck)


def _rotary_hardware(
    r: ResolvedConfig,
    station: Station,
    *,
    accordion: bool,
) -> list[tuple[str, tuple[float, float, float], tuple[float, float, float], float]]:
    """Low underside hinge spine plus small accordion tier hardware.

    The former full-length carrier arm ran from the post to the pan centre and
    read as a rod inserted into the makeup tray.  The tray's underside bridge
    and hub now provide that load path.  A very thin spine remains underneath
    the floor only to keep the load path continuous; it is hidden from the top
    view by the tray rather than crossing its pan surface.
    """
    x0, x1, y0, y1 = _rotary_tray_rect(station)
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    rise = station.tier_rise_m if accordion else 0.0
    run = math.hypot(cx, cy)
    yaw = math.atan2(cy, cx) if run > 1.0e-4 else 0.0
    items: list[tuple[str, tuple[float, float, float], tuple[float, float, float], float]] = [
        (
            "underside_hinge_spine",
            (run, 0.009, 0.0032),
            (cx / 2.0, cy / 2.0, rise + 0.0006),
            yaw,
        )
    ]
    if not accordion:
        return items
    x0, x1, y0, y1 = _rotary_tray_rect(station)
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    yaw = math.atan2(cy, cx)
    # A compact square riser sits immediately above the hub/bridge.  It keeps
    # the accordion tiers vertically indexed without recreating a radial arm.
    column_r = station.inner_edge_m * 0.55
    items.append(
        (
            "tier_riser",
            (0.016, 0.016, rise + 0.0062),
            (
                column_r * math.cos(yaw),
                column_r * math.sin(yaw),
                (rise + 0.0062) / 2.0 + 0.0008,
            ),
            yaw,
        )
    )
    return items


def _build_rotary_station(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    pans: tuple[object, ...],
    station: Station,
    *,
    accordion: bool,
) -> object:
    px, py, joint_z, _rect = _rotary_post_frame(r, station)
    prefix = f"palette_topology__{r.palette_topology}__station_{station.index}"
    # Bearing bridge rooted through the real wall pocket into solid shell.
    tangential = py if station.side in ("left", "right") else px
    face = _min_plan_face(
        r,
        side=station.side,
        tangentials=(tangential - 0.014, tangential, tangential + 0.014),
    )
    root = max(0.010, face - WALL_M - 0.006)
    if station.side in ("left", "right"):
        wall_face = math.copysign(root, px)
        bridge_size = (abs(px - wall_face), 0.028, 0.0060)
        bridge_center = ((px + wall_face) / 2.0, py, station.bay_z0_m + 0.0030)
    else:
        wall_face = root
        bridge_size = (0.028, abs(py - wall_face), 0.0060)
        bridge_center = (px, (py + wall_face) / 2.0, station.bay_z0_m + 0.0030)
    body.visual(
        Box(bridge_size),
        origin=Origin(xyz=bridge_center),
        material=mats["shell_alt"],
        name=f"{prefix}_bearing_bridge", material_class_id="metal.paint_coated",
    )
    post_height = POST_RISE_M
    body.visual(
        Cylinder(radius=POST_R_M, length=post_height),
        origin=Origin(xyz=(px, py, station.bay_z0_m + post_height / 2.0)),
        material=mats["steel"],
        name=f"{prefix}_pivot_post", material_class_id="metal.brushed_silver",
    )
    body.visual(
        Cylinder(radius=POST_R_M + 0.0035, length=0.0035),
        origin=Origin(xyz=(px, py, station.bay_z0_m + 0.00175)),
        material=mats["steel"],
        name=f"{prefix}_thrust_collar", material_class_id="metal.brushed_silver",
    )

    part = model.part(
        f"palette_topology__{r.palette_topology}__tray_{station.index}",
        meta={
            "role": "palette_tray",
            "slot": "palette_topology",
            "candidate": r.palette_topology,
            "station_index": station.index,
            "station_side": station.side,
            "pivot_axis": (0.0, 0.0, 1.0),
            "tier_rise_m": station.tier_rise_m,
        },
    )
    part.visual(
        mesh_from_cadquery(
            _rotary_tray_shape(r, station, accordion=accordion),
            f"makeup_{r.palette_topology}_wing_{station.index}",
            tolerance=0.0006,
        ),
        material=mats["tray"],
        name=f"{prefix}_wing_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    for local_name, size, center, yaw in _rotary_hardware(r, station, accordion=accordion):
        part.visual(
            Box(size),
            origin=Origin(xyz=center, rpy=(0.0, 0.0, yaw)),
            material=mats["shell_alt"],
            name=f"{prefix}_{local_name}", material_class_id="metal.paint_coated",
        )
    x0, x1, y0, y1 = _rotary_tray_rect(station)
    rise = station.tier_rise_m if accordion else 0.0
    _add_tray_pans(
        part,
        prefix=prefix,
        center_x=(x0 + x1) / 2.0,
        center_y=(y0 + y1) / 2.0,
        span_x=abs(x1 - x0) - 0.016,
        span_y=abs(y1 - y0) - 0.016,
        z_seat=rise + 0.003 + 0.0022,
        pan_pitch=r.pan_pitch_m,
        pans=pans,
        color_shift=station.index * 3 + 4,
    )

    provider = AxisInterface(
        name=f"case_form.palette_post_{station.index}",
        point=(px, py, joint_z),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=POST_R_M,
    )
    consumer = AxisInterface(
        name=f"palette_topology.wing_boss_{station.index}",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=POST_R_M,
    )
    mate = mate_axes(provider, consumer)
    joint_name = f"palette_topology__{r.palette_topology}__tray_{station.index}_swing"
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=body,
        child=part,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=4.0,
            velocity=1.6,
            lower=-1.35,
            upper=0.0,
        ),
        meta={
            "motion": "the upper limit is the fully deployed fan position",
            "station_side": station.side,
        },
    )
    register_interface_mate(model, joint_name, mate)
    return part


def _flip_frame(
    r: ResolvedConfig,
    station: Station,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Return the axle point and joint axis of a flip station."""
    half = r.case_width_m / 2.0 if station.side in ("left", "right") else r.case_depth_m / 2.0
    z_axle = station.bay_z0_m + station.bay_height_m * 0.62
    reach = half + _leaf_standoff(r) + station.leaf_len_m
    if station.side == "left":
        return ((-reach, station.tan_center_m, z_axle), (0.0, -1.0, 0.0))
    if station.side == "right":
        return ((reach, station.tan_center_m, z_axle), (0.0, 1.0, 0.0))
    return ((station.tan_center_m, reach, z_axle), (-1.0, 0.0, 0.0))


def _flip_leaf_plan(station: Station) -> tuple[float, float, float, float]:
    """Local plan centre and size of the double-sided leaf."""
    length = station.leaf_len_m
    width = station.tray_width_m
    if station.side == "left":
        return length / 2.0, 0.0, length - 0.005, width
    if station.side == "right":
        return -length / 2.0, 0.0, length - 0.005, width
    return 0.0, -length / 2.0, width, length - 0.005


LEAF_RIM_M = 0.0045
LEAF_LUG_INSET_M = 0.0095
LEAF_LUG_LEN_M = 0.011


def _flip_leaf_shape(station: Station) -> cq.Workplane:
    cx, cy, size_x, size_y = _flip_leaf_plan(station)
    thickness = station.leaf_thickness_m
    slab = _rounded_box(
        size_x,
        size_y,
        thickness,
        center=(cx, cy, 0.0),
        radius=0.005,
    )
    rim_outer = _rounded_box(
        size_x,
        size_y,
        thickness + 2.0 * LEAF_RIM_M,
        center=(cx, cy, 0.0),
        radius=0.005,
    )
    rim_inner = _rounded_box(
        max(0.004, size_x - 0.010),
        max(0.004, size_y - 0.010),
        thickness + 2.0 * LEAF_RIM_M + 0.004,
        center=(cx, cy, 0.0),
        radius=0.002,
    )
    return slab.union(rim_outer.cut(rim_inner))


def _flip_leaf_axle_length(station: Station) -> float:
    return station.tray_width_m + 2.0 * (LEAF_LUG_INSET_M + FIT_M)


def _build_flip_station(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    pans: tuple[object, ...],
    station: Station,
) -> object:
    point, axis = _flip_frame(r, station)
    prefix = f"palette_topology__{r.palette_topology}__station_{station.index}"
    half = r.case_width_m / 2.0 if station.side in ("left", "right") else r.case_depth_m / 2.0
    length = station.leaf_len_m
    width = station.tray_width_m
    thickness = station.leaf_thickness_m
    # The leaf's lower rim, not its slab, is the surface that lands on the rest
    # rail, so the whole cantilever shelf sits below rim bottom - FIT.
    leaf_bottom = point[2] - thickness / 2.0 - LEAF_RIM_M
    rail_top = leaf_bottom + FIT_M
    rail_center_z = rail_top - 0.0025
    shelf_center_z = rail_top - 0.005 - 0.0025 + 0.0008
    lug_offset = width / 2.0 + LEAF_LUG_INSET_M + LEAF_LUG_LEN_M / 2.0
    standoff = _leaf_standoff(r)
    prop_offsets = (-(width / 2.0 - 0.007), width / 2.0 - 0.007)
    # The bay opening removes the wall over the whole shelf band, so the
    # cantilever is carried by two real props standing on the bay floor.  Their
    # radius follows the true plan face so the floor beneath them is solid.
    face = _min_plan_face(
        r,
        side=station.side,
        tangentials=tuple(station.tan_center_m + offset for offset in (*prop_offsets, 0.0)),
    )
    prop_radius = max(0.014, face - 0.008)
    root = max(0.010, prop_radius - 0.006)
    reach = half + standoff + length
    shelf_span = reach + 0.001 - root
    shelf_mid = (reach + 0.001 + root) / 2.0
    prop_h = shelf_center_z + 0.0025 - station.bay_z0_m + 0.0014
    prop_z = shelf_center_z + 0.0025 - prop_h / 2.0
    if station.side in ("left", "right"):
        sign = -1.0 if station.side == "left" else 1.0
        body.visual(
            Box((shelf_span, width + 0.026, 0.0050)),
            origin=Origin(xyz=(sign * shelf_mid, station.tan_center_m, shelf_center_z)),
            material=mats["shell_alt"],
            name=f"{prefix}_flip_shelf", material_class_id="metal.paint_coated",
        )
        for prop_index, prop_offset in enumerate(prop_offsets):
            body.visual(
                Box((0.012, 0.012, prop_h)),
                origin=Origin(
                    xyz=(
                        sign * prop_radius,
                        station.tan_center_m + prop_offset,
                        prop_z,
                    )
                ),
                material=mats["shell_alt"],
                name=f"{prefix}_flip_shelf_prop_{prop_index}", material_class_id="metal.paint_coated",
            )
        body.visual(
            Box((0.010, width * 0.9, 0.0050)),
            origin=Origin(
                xyz=(
                    sign * (half + standoff + length - 0.008),
                    station.tan_center_m,
                    rail_center_z,
                )
            ),
            material=mats["steel"],
            name=f"{prefix}_flip_rest_rail", material_class_id="metal.brushed_silver",
        )
        for lug_index, lug_sign in enumerate((-1.0, 1.0)):
            lug_y = station.tan_center_m + lug_sign * lug_offset
            post_h = point[2] - shelf_center_z + 0.0025
            body.visual(
                Box((0.011, LEAF_LUG_LEN_M, post_h)),
                origin=Origin(xyz=(point[0], lug_y, point[2] - post_h / 2.0 + 0.0008)),
                material=mats["shell_alt"],
                name=f"{prefix}_flip_knuckle_post_{lug_index}", material_class_id="metal.paint_coated",
            )
            body.visual(
                Cylinder(radius=KNUCKLE_R_M + 0.0004, length=LEAF_LUG_LEN_M),
                origin=Origin(
                    xyz=(point[0], lug_y, point[2]),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=mats["hardware"],
                name=f"{prefix}_flip_knuckle_{lug_index}", material_class_id="metal.brass_polished",
            )
    else:
        body.visual(
            Box((width + 0.026, shelf_span, 0.0050)),
            origin=Origin(xyz=(station.tan_center_m, shelf_mid, shelf_center_z)),
            material=mats["shell_alt"],
            name=f"{prefix}_flip_shelf", material_class_id="metal.paint_coated",
        )
        for prop_index, prop_offset in enumerate(prop_offsets):
            body.visual(
                Box((0.012, 0.012, prop_h)),
                origin=Origin(
                    xyz=(
                        station.tan_center_m + prop_offset,
                        prop_radius,
                        prop_z,
                    )
                ),
                material=mats["shell_alt"],
                name=f"{prefix}_flip_shelf_prop_{prop_index}", material_class_id="metal.paint_coated",
            )
        body.visual(
            Box((width * 0.9, 0.010, 0.0050)),
            origin=Origin(
                xyz=(station.tan_center_m, half + standoff + length - 0.008, rail_center_z)
            ),
            material=mats["steel"],
            name=f"{prefix}_flip_rest_rail", material_class_id="metal.brushed_silver",
        )
        for lug_index, lug_sign in enumerate((-1.0, 1.0)):
            lug_x = station.tan_center_m + lug_sign * lug_offset
            post_h = point[2] - shelf_center_z + 0.0025
            body.visual(
                Box((LEAF_LUG_LEN_M, 0.011, post_h)),
                origin=Origin(xyz=(lug_x, point[1], point[2] - post_h / 2.0 + 0.0008)),
                material=mats["shell_alt"],
                name=f"{prefix}_flip_knuckle_post_{lug_index}", material_class_id="metal.paint_coated",
            )
            body.visual(
                Cylinder(radius=KNUCKLE_R_M + 0.0004, length=LEAF_LUG_LEN_M),
                origin=Origin(
                    xyz=(lug_x, point[1], point[2]),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                material=mats["hardware"],
                name=f"{prefix}_flip_knuckle_{lug_index}", material_class_id="metal.brass_polished",
            )

    part = model.part(
        f"palette_topology__{r.palette_topology}__tray_{station.index}",
        meta={
            "role": "palette_tray",
            "slot": "palette_topology",
            "candidate": r.palette_topology,
            "station_index": station.index,
            "station_side": station.side,
            "double_sided": True,
        },
    )
    part.visual(
        mesh_from_cadquery(
            _flip_leaf_shape(station),
            f"makeup_flip_leaf_{station.index}",
            tolerance=0.0005,
        ),
        material=mats["tray"],
        name=f"{prefix}_leaf_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    # The axle is a primitive so the lug/axle interference stays exact.
    part.visual(
        Cylinder(radius=0.0034, length=_flip_leaf_axle_length(station)),
        origin=Origin(
            xyz=(0.0, 0.0, 0.0),
            rpy=(
                (math.pi / 2.0, 0.0, 0.0)
                if station.side in ("left", "right")
                else (0.0, math.pi / 2.0, 0.0)
            ),
        ),
        material=mats["hardware"],
        name=f"{prefix}_leaf_axle", material_class_id="metal.brass_polished",
    )
    cx, cy, size_x, size_y = _flip_leaf_plan(station)
    for face_index, face_sign in enumerate((1.0, -1.0)):
        _add_tray_pans(
            part,
            prefix=f"{prefix}_face{face_index}",
            center_x=cx,
            center_y=cy,
            span_x=size_x - 0.030,
            span_y=size_y - 0.024,
            z_seat=face_sign * (thickness / 2.0 + 0.0020),
            pan_pitch=r.pan_pitch_m,
            pans=pans,
            color_shift=station.index * 3 + face_index * 5,
            pan_height=0.0040,
        )

    provider = AxisInterface(
        name=f"case_form.flip_knuckle_{station.index}",
        point=point,
        axis=axis,
        radial=(0.0, 0.0, 1.0),
        radius=0.0064,
    )
    consumer = AxisInterface(
        name=f"palette_topology.leaf_axle_{station.index}",
        point=(0.0, 0.0, 0.0),
        axis=axis,
        radial=(0.0, 0.0, 1.0),
        radius=0.0034,
    )
    mate = mate_axes(provider, consumer)
    joint_name = f"palette_topology__{r.palette_topology}__tray_{station.index}_flip"
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=body,
        child=part,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=2.5,
            velocity=2.0,
            lower=0.0,
            upper=math.pi,
        ),
        meta={
            "motion": "the double sided leaf flips over its captured axle",
            "station_side": station.side,
        },
    )
    register_interface_mate(model, joint_name, mate)
    return part


def _palette_topology_pull_out_drawer_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    pans: tuple[object, ...],
) -> tuple[object, ...]:
    return tuple(
        _build_prismatic_station(model, body, r, mats, pans, station, telescoping=False)
        for station in r.stations
    )


def _palette_topology_telescoping_side_tray_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    pans: tuple[object, ...],
) -> tuple[object, ...]:
    return tuple(
        _build_prismatic_station(model, body, r, mats, pans, station, telescoping=True)
        for station in r.stations
    )


def _palette_topology_fan_out_wing_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    pans: tuple[object, ...],
) -> tuple[object, ...]:
    return tuple(
        _build_rotary_station(model, body, r, mats, pans, station, accordion=False)
        for station in r.stations
    )


def _palette_topology_accordion_tier_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    pans: tuple[object, ...],
) -> tuple[object, ...]:
    return tuple(
        _build_rotary_station(model, body, r, mats, pans, station, accordion=True)
        for station in r.stations
    )


def _palette_topology_flip_over_leaf_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    pans: tuple[object, ...],
) -> tuple[object, ...]:
    return tuple(_build_flip_station(model, body, r, mats, pans, station) for station in r.stations)


_PALETTE_BUILDERS = {
    "pull_out_drawer": _palette_topology_pull_out_drawer_build,
    "telescoping_side_tray": _palette_topology_telescoping_side_tray_build,
    "fan_out_wing": _palette_topology_fan_out_wing_build,
    "accordion_tier": _palette_topology_accordion_tier_build,
    "flip_over_leaf": _palette_topology_flip_over_leaf_build,
}


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def build_makeup(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "makeup",
            "slot_choices": (
                ("case_form", r.case_form),
                ("palette_topology", r.palette_topology),
                ("applicator_storage", r.applicator_storage),
                ("pan_module_interface", r.pan_module_interface),
                ("closure", r.closure),
                ("palette_count", r.palette_count),
            ),
            "source_identity": (
                "case body chassis, rear hinged mirrored lid and N independently "
                "articulated palette trays that leave the case body"
            ),
            "derived_host_adaptation": {
                "level_pitch_m": r.level_pitch_m,
                "required_height_m": r.required_height_m,
                "body_height_m": r.body_height_m,
                "plinth_height_m": r.plinth_height_m,
                "recess_drop_m": r.recess_drop_m,
            },
        },
    )
    mats = _materials(model, r)
    pans = _pan_materials(model)
    body = model.part(
        "case_body",
        meta={
            "role": "case_body",
            "slot": "case_form",
            "candidate": r.case_form,
            "real_deck_recess": True,
            "palette_station_count": r.palette_count,
        },
    )
    _add_case_shell(body, r, mats)
    _add_hinge_hardware(body, r, mats)
    _PAN_MODULE_BUILDERS[r.pan_module_interface](body, r, mats, pans)
    lid = _add_lid(model, r, mats)
    _APPLICATOR_BUILDERS[r.applicator_storage](body, lid, r, mats)
    clasp = _CLOSURE_BUILDERS[r.closure](model, body, lid, r, mats)

    hinge_provider = AxisInterface(
        name="case_form.lid_hinge_axis",
        point=(0.0, r.hinge_y_m, r.hinge_z_m),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=PIN_R_M,
    )
    hinge_consumer = AxisInterface(
        name="mirror_lid.hinge_axis",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=PIN_R_M + 0.0028,
    )
    hinge_mate = mate_axes(hinge_provider, hinge_consumer)
    model.articulation(
        "case_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=hinge_mate.origin,
        axis=hinge_mate.axis,
        motion_limits=MotionLimits(
            effort=8.0,
            velocity=1.8,
            lower=0.0,
            upper=r.lid_open_rad,
        ),
        meta={"motion": "the lower limit closes the lid box onto the case rim"},
    )
    register_interface_mate(model, "case_to_lid", hinge_mate)

    _PALETTE_BUILDERS[r.palette_topology](model, body, r, mats, pans)

    if clasp is not None:
        keeper_y, keeper_z = _keeper_frame(r)
        clasp_provider = AxisInterface(
            name="closure.keeper_axis",
            point=(0.0, keeper_y, keeper_z),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=0.0035,
        )
        clasp_consumer = AxisInterface(
            name="closure.lever_pin_axis",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=0.0035,
        )
        clasp_mate = mate_axes(clasp_provider, clasp_consumer)
        model.articulation(
            "closure__over_center_clasp__lever_pivot",
            ArticulationType.REVOLUTE,
            parent=lid,
            child=clasp,
            origin=clasp_mate.origin,
            axis=clasp_mate.axis,
            motion_limits=MotionLimits(
                effort=1.0,
                velocity=3.0,
                lower=0.0,
                upper=0.62,
            ),
            meta={"motion": "positive lifts the over centre clasp lever"},
        )
        register_interface_mate(
            model,
            "closure__over_center_clasp__lever_pivot",
            clasp_mate,
        )
    return model


def build_seeded_makeup(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_makeup(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Author tests
# ---------------------------------------------------------------------------


def _parts_by_role(model: ArticulatedObject, role: str) -> list[object]:
    return [part for part in model.parts if part.meta.get("role") == role]


def run_makeup_tests(
    model: ArticulatedObject,
    config: Config | None = None,
) -> TestReport:
    r = resolve_config(config or Config())
    ctx = TestContext(model)
    bodies = _parts_by_role(model, "case_body")
    lids = _parts_by_role(model, "mirror_lid")
    trays = _parts_by_role(model, "palette_tray")
    clasps = _parts_by_role(model, "closure_clasp")
    body = bodies[0] if bodies else None
    lid = lids[0] if lids else None
    lid_joint = model.get_articulation("case_to_lid")
    tray_prefix = f"palette_topology__{r.palette_topology}__tray_"
    tray_joints = [joint for joint in model.articulations if joint.child.startswith(tray_prefix)]

    ctx.check(
        "category_anchor: makeup train case identity",
        len(bodies) == 1
        and len(lids) == 1
        and len(trays) == r.palette_count
        and body is not None
        and lid is not None
        and body.meta.get("real_deck_recess") is True
        and len(clasps) == (1 if r.closure == "over_center_clasp" else 0),
        details=(
            f"case_body={len(bodies)}, mirror_lid={len(lids)}, "
            f"palette_tray={len(trays)}/{r.palette_count}, clasp={len(clasps)}"
        ),
    )
    ctx.check(
        "category_anchor: rear hinged mirrored lid over a real case rim",
        lid is not None
        and lid_joint is not None
        and lid_joint.parent == "case_body"
        and lid_joint.child == "mirror_lid"
        and lid_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(lid_joint.axis) == (1.0, 0.0, 0.0)
        and lid_joint.motion_limits is not None
        and math.isclose(lid_joint.motion_limits.lower, 0.0)
        and math.isclose(lid_joint.motion_limits.upper, r.lid_open_rad)
        and lid.get_visual("mirror_lid__inset_mirror") is not None
        and lid.get_visual("mirror_lid__mirror_opening_frame") is not None
        and lid.get_visual("mirror_lid__hinge_knuckle_0") is not None
        and body is not None
        and body.get_visual("case_form__hinge_pin") is not None
        and r.hinge_y_m < -r.case_depth_m / 2.0 + 0.030,
        details=f"lid_joint={lid_joint}, hinge=({r.hinge_y_m}, {r.hinge_z_m})",
    )
    expected_type = (
        ArticulationType.PRISMATIC
        if r.palette_topology in _PRISMATIC
        else ArticulationType.REVOLUTE
    )
    ctx.check(
        "category_anchor: independently articulated palette trays",
        len(tray_joints) == r.palette_count
        and all(joint.parent == "case_body" for joint in tray_joints)
        and all(joint.articulation_type == expected_type for joint in tray_joints)
        and all(joint.motion_limits is not None for joint in tray_joints)
        and all(joint.motion_limits.lower < joint.motion_limits.upper for joint in tray_joints)
        and len({joint.child for joint in tray_joints}) == r.palette_count
        and all(
            tray.get_visual(
                f"palette_topology__{r.palette_topology}__station_"
                f"{tray.meta.get('station_index')}_"
                + (
                    "tray_shell"
                    if r.palette_topology in _PRISMATIC
                    else ("leaf_shell" if r.palette_topology == "flip_over_leaf" else "wing_shell")
                )
            )
            is not None
            for tray in trays
        ),
        details=(
            f"topology={r.palette_topology}, joints={len(tray_joints)}, expected={expected_type}"
        ),
    )
    ctx.check(
        "derived host capacity grows with the palette station count",
        r.body_height_m >= r.required_height_m - 1e-9
        and math.isclose(
            r.required_height_m,
            FLOOR_M + r.palette_count * r.level_pitch_m + DECK_SLAB_M + r.recess_drop_m,
            rel_tol=1e-6,
            abs_tol=1e-9,
        )
        and r.plinth_height_m >= -1e-9
        and r.level_pitch_m > r.bay_height_m
        and all(
            station.bay_z0_m + station.bay_height_m <= r.deck_z_m - DECK_SLAB_M + 1e-6
            for station in r.stations
        ),
        details=(
            f"N={r.palette_count}, pitch={r.level_pitch_m}, "
            f"required={r.required_height_m}, body={r.body_height_m}, "
            f"plinth={r.plinth_height_m}"
        ),
    )
    ctx.check(
        "palette stations keep real running clearance in their host geometry",
        all(station.tray_width_m + 0.008 <= station.tan_span_m + 1e-9 for station in r.stations)
        and all(
            station.cavity_depth_m + 0.008
            < (r.case_width_m if station.side in ("left", "right") else r.case_depth_m) - WALL_M
            for station in r.stations
        )
        and len({station.level for station in r.stations}) == r.palette_count,
        details=f"stations={[(s.side, s.level, s.tray_width_m) for s in r.stations]}",
    )
    ctx.check(
        "pan module and applicator zones stay inside the deck recess",
        r.pan_zone_width_m <= r.recess_width_m * r.plan_fill + 1e-9
        and r.pan_zone_depth_m + r.applicator_zone_depth_m <= r.recess_depth_m * r.plan_fill + 1e-9
        and r.pan_cols >= 3
        and r.pan_rows >= 1
        and r.pan_radius_m > 0.004
        and body is not None
        and body.get_visual(f"case_form__{r.case_form}__chassis_shell") is not None
        and body.get_visual(f"case_form__{r.case_form}__deck_liner") is not None,
        details=(
            f"pan_zone=({r.pan_zone_width_m}, {r.pan_zone_depth_m}), "
            f"applicator={r.applicator_zone_depth_m}, "
            f"grid={r.pan_cols}x{r.pan_rows}"
        ),
    )
    if r.palette_topology in _PRISMATIC:
        ctx.check(
            "pull out palette trays stay captured on their side runners",
            all(station.tail_len_m > station.travel_m for station in r.stations)
            and all(
                station.body_len_m + station.tail_len_m + 0.010 <= station.cavity_depth_m + 1e-9
                for station in r.stations
            )
            and all(
                body is not None
                and body.get_visual(
                    f"palette_topology__{r.palette_topology}__station_{station.index}_runner_0"
                )
                is not None
                and body.get_visual(
                    f"palette_topology__{r.palette_topology}__station_{station.index}_runner_1"
                )
                is not None
                and body.get_visual(
                    f"palette_topology__{r.palette_topology}__station_"
                    f"{station.index}_cavity_backstop"
                )
                is not None
                for station in r.stations
            ),
            details=(
                f"travel={[s.travel_m for s in r.stations]}, "
                f"tail={[s.tail_len_m for s in r.stations]}"
            ),
        )
    if r.palette_topology in _ROTARY:
        ctx.check(
            "fan palette wings pivot on a real supported post",
            all(
                body is not None
                and body.get_visual(
                    f"palette_topology__{r.palette_topology}__station_{station.index}_pivot_post"
                )
                is not None
                and body.get_visual(
                    f"palette_topology__{r.palette_topology}__station_"
                    f"{station.index}_bearing_bridge"
                )
                is not None
                and body.get_visual(
                    f"palette_topology__{r.palette_topology}__station_{station.index}_thrust_collar"
                )
                is not None
                for station in r.stations
            )
            and all(tuple(joint.axis) == (0.0, 0.0, 1.0) for joint in tray_joints),
            details=f"stations={[s.index for s in r.stations]}",
        )
    if r.palette_topology == "flip_over_leaf":
        ctx.check(
            "double sided leaves hinge on real captured knuckles",
            all(
                body is not None
                and body.get_visual(
                    f"palette_topology__flip_over_leaf__station_{station.index}_flip_knuckle_0"
                )
                is not None
                and body.get_visual(
                    f"palette_topology__flip_over_leaf__station_{station.index}_flip_shelf"
                )
                is not None
                for station in r.stations
            )
            and all(
                joint.motion_limits is not None and math.isclose(joint.motion_limits.upper, math.pi)
                for joint in tray_joints
            )
            and all(
                station.band_count == math.ceil(r.palette_count / len(SIDES))
                for station in r.stations
            ),
            details=(
                f"bands={[(s.side, s.band) for s in r.stations]}, "
                f"band_count={r.stations[0].band_count}"
            ),
        )
    if r.closure == "over_center_clasp":
        clasp_joint = model.get_articulation("closure__over_center_clasp__lever_pivot")
        ctx.check(
            "over centre clasp is a real lever on the lid keeper",
            len(clasps) == 1
            and clasp_joint is not None
            and clasp_joint.parent == "mirror_lid"
            and clasp_joint.articulation_type == ArticulationType.REVOLUTE
            and lid is not None
            and lid.get_visual("closure__over_center_clasp__keeper_ear_0") is not None
            and body is not None
            and body.get_visual("closure__over_center_clasp__case_strike") is not None,
            details=f"clasp_joint={clasp_joint}",
        )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "cylindrical_drum_with_seven_flip_leaves",
        {
            "case_form": "cylindrical_vanity_case",
            "palette_topology": "flip_over_leaf",
            "applicator_storage": "upright_tool_well",
            "pan_module_interface": "keyed_snap_tile_grid",
            "closure": "over_center_clasp",
            "palette_count": 7,
            "case_width_m": 0.405,
            "case_depth_m": 0.235,
            "case_height_m": 0.055,
            "lid_depth_m": 0.055,
            "tray_height_m": 0.026,
            "tray_extension_ratio": 0.82,
            "corner_radius_m": 0.028,
            "pan_pitch_m": 0.052,
        },
        reason=(
            "largest curved host with the deepest recess, the tallest N-derived "
            "station stack and the longest double sided leaves"
        ),
    ),
    corner_case(
        "round_compact_min_with_two_telescoping_trays",
        {
            "case_form": "round_compact",
            "palette_topology": "telescoping_side_tray",
            "applicator_storage": "lid_brush_roll",
            "pan_module_interface": "fixed_round_wells",
            "closure": "front_latch_strike",
            "palette_count": 2,
            "case_width_m": 0.265,
            "case_depth_m": 0.155,
            "case_height_m": 0.055,
            "lid_depth_m": 0.010,
            "tray_height_m": 0.011,
            "tray_extension_ratio": 0.82,
            "corner_radius_m": 0.005,
            "pan_pitch_m": 0.030,
        },
        reason=(
            "smallest elliptical host with the longest telescoping travel and the "
            "shallowest lid box that still has to hold the brush roll"
        ),
    ),
    corner_case(
        "book_folio_with_seven_pull_out_drawers",
        {
            "case_form": "book_style_folio",
            "palette_topology": "pull_out_drawer",
            "applicator_storage": "front_organizer_channels",
            "pan_module_interface": "keyed_snap_tile_grid",
            "closure": "over_center_clasp",
            "palette_count": 7,
            "case_width_m": 0.280,
            "case_depth_m": 0.235,
            "case_height_m": 0.150,
            "lid_depth_m": 0.020,
            "tray_height_m": 0.026,
            "tray_extension_ratio": 0.82,
            "corner_radius_m": 0.028,
            "pan_pitch_m": 0.030,
        },
        reason=(
            "narrow soft folio host whose seven stacked cavities must not break "
            "through the far wall at maximum travel"
        ),
    ),
    corner_case(
        "train_tower_with_seven_accordion_tiers",
        {
            "case_form": "train_case_tower",
            "palette_topology": "accordion_tier",
            "applicator_storage": "upright_tool_well",
            "pan_module_interface": "fixed_round_wells",
            "closure": "over_center_clasp",
            "palette_count": 7,
            "case_width_m": 0.405,
            "case_depth_m": 0.235,
            "case_height_m": 0.150,
            "lid_depth_m": 0.055,
            "tray_height_m": 0.026,
            "tray_extension_ratio": 0.45,
            "corner_radius_m": 0.005,
            "pan_pitch_m": 0.045,
        },
        reason=(
            "tallest derived tower with staggered cantilever tiers on every wall "
            "and a deep lid box closing over standing tools"
        ),
    ),
    corner_case(
        "rounded_case_with_six_fan_wings",
        {
            "case_form": "rounded_train_case",
            "palette_topology": "fan_out_wing",
            "applicator_storage": "lid_brush_roll",
            "pan_module_interface": "keyed_snap_tile_grid",
            "closure": "front_latch_strike",
            "palette_count": 6,
            "case_width_m": 0.340,
            "case_depth_m": 0.155,
            "case_height_m": 0.150,
            "lid_depth_m": 0.040,
            "tray_height_m": 0.011,
            "tray_extension_ratio": 0.45,
            "corner_radius_m": 0.020,
            "pan_pitch_m": 0.052,
        },
        reason=(
            "shallow-depth host with six outboard wings whose folded and deployed "
            "sweeps must clear the walls and each other"
        ),
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "Station",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_makeup",
    "build_seeded_makeup",
    "config_from_seed",
    "resolve_config",
    "run_makeup_tests",
]
