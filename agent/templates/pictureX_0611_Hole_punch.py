# SPDX-License-Identifier: Apache-2.0

"""Self-contained heavy-duty desk hole punch template.

One grounded ``base`` part carries the sole, the rubber feet, the CadQuery deck
and one annular die per station; the deck's chip passages and its drawer cavity
are cut per station and per chip candidate.  A ``frame`` part is FIXED on the
rear of the deck and always exposes the same two interfaces: a head beam bored
once per station (plus a plunger bore when the plunger is active) and a pivot
line.  ``punch_station_count`` carriages ride PRISMATIC straight down out of
that beam; every guide stem runs in its bore with a 0.8 mm fit over the whole
stroke and every pin enters its own die ring at full stroke, so nothing is
retained by an overlap allowance.

Five slots vary without touching that chain: ``frame_form`` (cast hood, twin
side plates, one-piece C loop), ``actuation`` (long ball-grip lever, twin-strap
U-grip lever, drag-link lever, or a press plunger whose stem mimics carriage 0),
``punch_station`` (collared or long pin), ``paper_guide`` (side rail stops or
bed fences) and ``chip_handling`` (pull-out drawer or fixed bed).
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
    Mimic,
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
    multiplicity_slot,
    register_interface_mate,
)

FrameForm = Literal["nose_hood", "side_plate", "c_loop"]
Actuation = Literal["direct_lever", "compound_lever", "plunger", "lever_linkage"]
PunchStation = Literal["collared_pin", "long_pin"]
PaperGuide = Literal["rail_guides", "bed_guides"]
ChipHandling = Literal["pull_out_tray", "fixed_bed"]
PaletteStyle = Literal["warm_gray", "satin_aluminum", "industrial_green", "charcoal"]

FRAME_FORMS: tuple[FrameForm, ...] = ("nose_hood", "side_plate", "c_loop")
ACTUATIONS: tuple[Actuation, ...] = ("direct_lever", "compound_lever", "plunger", "lever_linkage")
PUNCH_STATIONS: tuple[PunchStation, ...] = ("collared_pin", "long_pin")
PAPER_GUIDES: tuple[PaperGuide, ...] = ("rail_guides", "bed_guides")
CHIP_HANDLINGS: tuple[ChipHandling, ...] = ("pull_out_tray", "fixed_bed")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "warm_gray",
    "satin_aluminum",
    "industrial_green",
    "charcoal",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("frame_form", FRAME_FORMS),
        component_slot("actuation", ACTUATIONS),
        component_slot("punch_station", PUNCH_STATIONS),
        component_slot("paper_guide", PAPER_GUIDES),
        component_slot("chip_handling", CHIP_HANDLINGS),
        multiplicity_slot("punch_station_count", (1, 2, 3, 4), item_slot="punch_station"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_gray": {
        "body": (0.55, 0.54, 0.51, 1.0),
        "paint": (0.18, 0.18, 0.19, 1.0),
        "steel": (0.74, 0.76, 0.78, 1.0),
        "dark_steel": (0.30, 0.31, 0.33, 1.0),
        "plastic": (0.11, 0.11, 0.12, 1.0),
        "accent": (0.24, 0.36, 0.55, 1.0),
    },
    "satin_aluminum": {
        "body": (0.78, 0.79, 0.80, 1.0),
        "paint": (0.14, 0.14, 0.15, 1.0),
        "steel": (0.82, 0.84, 0.86, 1.0),
        "dark_steel": (0.34, 0.35, 0.36, 1.0),
        "plastic": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.60, 0.62, 0.64, 1.0),
    },
    "industrial_green": {
        "body": (0.22, 0.36, 0.28, 1.0),
        "paint": (0.13, 0.21, 0.16, 1.0),
        "steel": (0.75, 0.77, 0.78, 1.0),
        "dark_steel": (0.29, 0.31, 0.30, 1.0),
        "plastic": (0.09, 0.11, 0.10, 1.0),
        "accent": (0.86, 0.78, 0.36, 1.0),
    },
    "charcoal": {
        "body": (0.22, 0.22, 0.23, 1.0),
        "paint": (0.11, 0.11, 0.12, 1.0),
        "steel": (0.72, 0.74, 0.76, 1.0),
        "dark_steel": (0.32, 0.33, 0.34, 1.0),
        "plastic": (0.07, 0.07, 0.08, 1.0),
        "accent": (0.70, 0.24, 0.18, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
STATION_PITCH = 0.054     # standard heavy-punch hole pitch
FOOT_H = 0.008
SOLE_T = 0.012
DECK_T = 0.027
DIE_T = 0.004             # die ring, lapped 1 mm into the deck
PIN_R = 0.0045
STEM_R = 0.005
BEAM_T = 0.030
PUNCH_TRAVEL = 0.016
# Radial running fit, under the 1 mm assembly-gap tolerance: a stem is
# journalled (supported) in its bore with no penetration.
FIT = 0.0008
SEAT = 0.0006             # sub-millimetre seating lap
DECK_TOP = FOOT_H + SOLE_T + DECK_T          # 0.047
DIE_TOP = DECK_TOP + DIE_T - 0.001           # 0.050
PIN_BOTTOM = DIE_TOP + PUNCH_TRAVEL - 0.002  # 0.064 at rest, 2 mm into the die at stroke
PIN_LEN = 0.030
BLOCK_H = 0.022
BLOCK_TOP = PIN_BOTTOM + PIN_LEN - 0.002 + BLOCK_H   # 0.114
BEAM_BOTTOM = BLOCK_TOP + 0.001                      # 0.115
BEAM_TOP = BEAM_BOTTOM + BEAM_T                      # 0.145
PIVOT_Z = BEAM_TOP + 0.026                           # 0.171
# The guide stem keeps 30 mm of engagement in its beam bore at full stroke and
# still ends below the press plunger's driver plate.
STEM_LEN = PUNCH_TRAVEL + BEAM_T + 0.003          # 0.049
STEM_TOP = BLOCK_TOP - 0.002 + STEM_LEN           # 0.161
# The press yoke clears every guide stem by 1 mm even when only the mimicked
# carriage has moved, so an independent station can never be driven into it.
DRIVER_Z0 = STEM_TOP + PUNCH_TRAVEL + 0.001
DRIVER_T = 0.006
BRIDGE_BOTTOM = DRIVER_Z0 + DRIVER_T + 0.013      # 0.181
BRIDGE_T = 0.012
CAP_Z0 = BRIDGE_BOTTOM + BRIDGE_T + PUNCH_TRAVEL + 0.002
CAP_T = 0.010
AXLE_R = 0.0065
LINK_Y = 0.020
LINK_PLATE_Y = 0.032
LEVER_SLOT_HALF_Y = 0.046
RAIL_LIFT = 0.010


@dataclass(frozen=True)
class Config:
    frame_form: FrameForm = "side_plate"
    actuation: Actuation = "direct_lever"
    punch_station: PunchStation = "collared_pin"
    paper_guide: PaperGuide = "bed_guides"
    chip_handling: ChipHandling = "fixed_bed"
    punch_station_count: int = 2
    base_length_m: float | None = None
    throat_depth_m: float | None = None
    lever_reach_m: float | None = None
    palette_style: PaletteStyle = "warm_gray"
    name: str = "pictureX_0611_Hole_punch"


@dataclass(frozen=True)
class ResolvedConfig:
    frame_form: FrameForm
    actuation: Actuation
    punch_station: PunchStation
    paper_guide: PaperGuide
    chip_handling: ChipHandling
    punch_station_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    base_length_m: float
    throat_depth_m: float
    lever_reach_m: float
    station_span_m: float
    station_y: tuple[float, ...]
    deck_half_y: float
    frame_face_x: float
    punch_line_x_m: float
    pivot_x: float
    beam_half_y: float
    beam_x0: float
    beam_x1: float
    frame_half_y: float
    strap_y: float
    link_y: float
    grip_x_m: float
    guide_travel_m: float
    depth_travel_m: float
    tray_travel_m: float
    guide_z: float
    rail_half_y: float
    bed_x0: float
    bed_x1: float
    cavity_x0: float
    cavity_x1: float
    cavity_half_y: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x40_5E_C1_07)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        frame_form=choices["frame_form"],
        actuation=choices["actuation"],
        punch_station=choices["punch_station"],
        paper_guide=choices["paper_guide"],
        chip_handling=choices["chip_handling"],
        punch_station_count=choices["punch_station_count"],
        base_length_m=round(rng.uniform(0.300, 0.460), 4),
        throat_depth_m=round(rng.uniform(0.045, 0.090), 4),
        lever_reach_m=round(rng.uniform(0.200, 0.360), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"hole_punch_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "frame_form": config.frame_form,
            "actuation": config.actuation,
            "punch_station": config.punch_station,
            "paper_guide": config.paper_guide,
            "chip_handling": config.chip_handling,
            "punch_station_count": config.punch_station_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.base_length_m is not None and not 0.300 <= float(config.base_length_m) <= 0.460:
        raise ValueError("base_length_m must be in [0.300, 0.460]")
    if config.throat_depth_m is not None and not 0.045 <= float(config.throat_depth_m) <= 0.090:
        raise ValueError("throat_depth_m must be in [0.045, 0.090]")
    if config.lever_reach_m is not None and not 0.200 <= float(config.lever_reach_m) <= 0.360:
        raise ValueError("lever_reach_m must be in [0.200, 0.360]")

    length = (
        _clamp(config.base_length_m, 0.300, 0.460) if config.base_length_m is not None else 0.380
    )
    throat = (
        _clamp(config.throat_depth_m, 0.045, 0.090)
        if config.throat_depth_m is not None
        else 0.062
    )
    reach = (
        _clamp(config.lever_reach_m, 0.200, 0.360) if config.lever_reach_m is not None else 0.280
    )

    n = int(config.punch_station_count)
    span = (n - 1) * STATION_PITCH
    ys = tuple((i - (n - 1) / 2.0) * STATION_PITCH for i in range(n))
    deck_half_y = max(0.086, 0.5 * span + 0.070)
    frame_face_x = 0.5 * length - 0.075
    punch_x = frame_face_x - throat
    pivot_x = frame_face_x + 0.030
    beam_half_y = 0.5 * span + 0.020
    frame_half_y = 0.5 * span + 0.058
    strap_y = 0.5 * span + 0.080
    link_y = 0.5 * span + 0.030
    guide_z = DECK_TOP + (0.005 if config.chip_handling == "fixed_bed" else 0.0)
    guide_travel = (
        0.32 * length
        if config.paper_guide == "rail_guides"
        else deck_half_y - 0.5 * span - 0.045
    )
    rail_half_y = deck_half_y + guide_travel + 0.020

    return ResolvedConfig(
        frame_form=config.frame_form,
        actuation=config.actuation,
        punch_station=config.punch_station,
        paper_guide=config.paper_guide,
        chip_handling=config.chip_handling,
        punch_station_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        base_length_m=length,
        throat_depth_m=throat,
        lever_reach_m=reach,
        station_span_m=span,
        station_y=ys,
        deck_half_y=deck_half_y,
        frame_face_x=frame_face_x,
        punch_line_x_m=punch_x,
        pivot_x=pivot_x,
        beam_half_y=beam_half_y,
        beam_x0=punch_x - 0.026,
        beam_x1=frame_face_x + 0.006,
        frame_half_y=frame_half_y,
        strap_y=strap_y,
        link_y=link_y,
        grip_x_m=punch_x - reach,
        guide_travel_m=guide_travel,
        depth_travel_m=0.25 * length,
        tray_travel_m=0.30 * length,
        guide_z=guide_z,
        rail_half_y=rail_half_y,
        bed_x0=-0.5 * length + 0.008,
        bed_x1=punch_x - 0.036,
        cavity_x0=-0.5 * length + 0.007,
        cavity_x1=frame_face_x - 0.010,
        cavity_half_y=deck_half_y - 0.014,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("frame_form", config.frame_form),
        ("actuation", config.actuation),
        ("punch_station", config.punch_station),
        ("paper_guide", config.paper_guide),
        ("chip_handling", config.chip_handling),
        ("punch_station_count", config.punch_station_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"punch_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _local_origin(
    origin: Origin | None, offset: tuple[float, float, float]
) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(a - b for a, b in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


def _y_cyl(
    part,
    offset: tuple[float, float, float],
    name: str,
    radius: float,
    length: float,
    xyz,
    material: str,
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=_local_origin(
            Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)), offset
        ),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _box_at(x0, x1, y0, y1, z0, z1):
    return (
        cq.Workplane("XY")
        .transformed(offset=(0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1)))
        .box(x1 - x0, y1 - y0, z1 - z0)
    )


def _z_bore(x, y, radius, z0, z1):
    return (
        cq.Workplane("XY")
        .transformed(offset=(x, y, 0.5 * (z0 + z1)))
        .cylinder(height=z1 - z0, radius=radius, direct=(0.0, 0.0, 1.0))
    )


# --- base --------------------------------------------------------------------
def _deck_mesh(r: ResolvedConfig):
    """The deck: a real solid with chip passages and, for the drawer, a cavity."""
    deck = _box_at(
        -0.5 * r.base_length_m + 0.007,
        0.5 * r.base_length_m - 0.007,
        -(r.deck_half_y - 0.005),
        r.deck_half_y - 0.005,
        FOOT_H + SOLE_T,
        DECK_TOP,
    )
    if r.chip_handling == "pull_out_tray":
        deck = deck.cut(
            _box_at(
                r.cavity_x0,
                r.cavity_x1,
                -r.cavity_half_y,
                r.cavity_half_y,
                FOOT_H + SOLE_T + 0.004,
                DECK_TOP - 0.009,
            )
        )
    for y in r.station_y:
        deck = deck.cut(
            _z_bore(r.punch_line_x_m, y, PIN_R + 0.002, FOOT_H, DECK_TOP + 0.002)
        )
    return mesh_from_cadquery(deck, "punch_deck")


def _die_ring_mesh(name: str):
    ring = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, 0.5 * DIE_T))
        .cylinder(height=DIE_T, radius=0.011, direct=(0.0, 0.0, 1.0))
    )
    ring = ring.cut(_z_bore(0.0, 0.0, PIN_R + FIT, -0.01, 0.02))
    return mesh_from_cadquery(ring, name)


def _build_base(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    base = model.part("base", meta={"role": "base"})
    base.visual(
        Box((r.base_length_m, 2.0 * r.deck_half_y, SOLE_T)),
        origin=Origin(xyz=(0.0, 0.0, FOOT_H + 0.5 * SOLE_T)),
        material=mats["body"],
        name="base_sole", material_class_id="metal.paint_coated",
    )
    base.visual(
        _deck_mesh(r),
        material=mats["paint"],
        name="base_deck", material_class_id="metal.paint_coated",
    )
    for index, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        base.visual(
            Cylinder(radius=0.011, length=FOOT_H + SEAT),
            origin=Origin(
                xyz=(
                    sx * (0.5 * r.base_length_m - 0.026),
                    sy * (r.deck_half_y - 0.024),
                    0.5 * (FOOT_H + SEAT),
                )
            ),
            material=mats["plastic"],
            name=f"rubber_foot_{index}", material_class_id="rubber.smooth_plain",
        )
    for index, y in enumerate(r.station_y):
        base.visual(
            _die_ring_mesh(f"punch_die_ring_{index}"),
            origin=Origin(xyz=(r.punch_line_x_m, y, DECK_TOP - 0.001)),
            material=mats["steel"],
            name=f"die_{index}", material_class_id="metal.steel_bare",
        )
    return base


# --- frame form candidates ---------------------------------------------------
def _head_beam_mesh(r: ResolvedConfig):
    beam = _box_at(
        r.beam_x0, r.beam_x1, -r.beam_half_y, r.beam_half_y, BEAM_BOTTOM, BEAM_TOP
    )
    for y in r.station_y:
        beam = beam.cut(
            _z_bore(r.punch_line_x_m, y, STEM_R + FIT, BEAM_BOTTOM - 0.01, BEAM_TOP + 0.01)
        )
    return mesh_from_cadquery(beam, "punch_head_beam")


def _frame_form_side_plate_build(
    part, offset: tuple[float, float, float], r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """Built-up frame: two rear side plates, crossbeam, head neck and supports."""
    for index, sy in enumerate((-1.0, 1.0)):
        y = sy * (r.frame_half_y - 0.005)
        part.visual(
            Box((0.070, 0.010, PIVOT_Z - DECK_TOP + 0.012)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        r.frame_face_x + 0.036,
                        y,
                        0.5 * (DECK_TOP - 0.002 + PIVOT_Z + 0.010),
                    )
                ),
                offset,
            ),
            material=mats["body"],
            name=f"frame_form__side_plate__side_plate_{index}", material_class_id="metal.paint_coated",
        )
        _y_cyl(
            part,
            offset,
            f"frame_form__side_plate__pivot_boss_{index}",
            0.024,
            0.011,
            (r.pivot_x, y, PIVOT_Z),
            mats["body"],
        )
        part.visual(
            Box((0.055, 0.012, 0.040)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        r.frame_face_x + 0.004,
                        sy * (r.beam_half_y + 0.004),
                        BEAM_BOTTOM - 0.014,
                    )
                ),
                offset,
            ),
            material=mats["body"],
            name=f"frame_form__side_plate__head_support_{index}", material_class_id="metal.paint_coated",
        )
    part.visual(
        Box((0.086, 2.0 * r.frame_half_y - 0.020, 0.032)),
        origin=_local_origin(
            Origin(xyz=(r.frame_face_x + 0.036, 0.0, DECK_TOP + 0.014)), offset
        ),
        material=mats["paint"],
        name="frame_form__side_plate__lower_crossbeam", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.060, 2.0 * r.beam_half_y - 0.010, BEAM_TOP - DECK_TOP - 0.026)),
        origin=_local_origin(
            Origin(
                xyz=(
                    r.frame_face_x + 0.026,
                    0.0,
                    0.5 * (DECK_TOP + 0.028 + BEAM_TOP),
                )
            ),
            offset,
        ),
        material=mats["paint"],
        name="frame_form__side_plate__head_neck", material_class_id="metal.paint_coated",
    )


def _station_corridor(r: ResolvedConfig):
    """Clearance above the head beam for the guide stems, driver plate, bridge
    and press cap, so a cast frame never guides or fouls the punch chain."""
    half_y = 0.5 * r.station_span_m + 0.040
    return _box_at(
        r.punch_line_x_m - 0.034,
        r.punch_line_x_m + 0.034,
        -half_y,
        half_y,
        BEAM_TOP - 0.002,
        PIVOT_Z + 0.090,
    )


def _lever_slot(r: ResolvedConfig, x0: float, x1: float):
    """The slot a hand lever swings in, cut through the cast frame top."""
    return _box_at(x0, x1, -LEVER_SLOT_HALF_Y, LEVER_SLOT_HALF_Y, BEAM_TOP + 0.002, PIVOT_Z + 0.060)


def _frame_form_nose_hood_build(
    part, offset: tuple[float, float, float], r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """One-piece cast hood over the head beam, with a real lever throat."""
    hood = (
        cq.Workplane("XZ")
        .polyline(
            [
                (r.beam_x0 - 0.006, BEAM_BOTTOM - 0.004),
                (r.beam_x0 + 0.010, BEAM_TOP + 0.030),
                (r.frame_face_x + 0.052, PIVOT_Z + 0.014),
                (r.frame_face_x + 0.062, DECK_TOP + 0.001),
                (r.frame_face_x - 0.006, DECK_TOP + 0.001),
            ]
        )
        .close()
        .extrude(r.frame_half_y, both=True)
    )
    hood = hood.cut(_lever_slot(r, r.beam_x0 - 0.020, r.frame_face_x + 0.070))
    hood = hood.cut(_station_corridor(r))
    # The head beam is its own bored member: the hood must not fill that volume
    # and re-block the stems, but keeps a 4 mm lap on each side to stay one solid.
    hood = hood.cut(
        _box_at(
            r.beam_x0 - 0.001,
            r.beam_x1 + 0.001,
            -(r.beam_half_y - 0.004),
            r.beam_half_y - 0.004,
            BEAM_BOTTOM - 0.001,
            BEAM_TOP + 0.001,
        )
    )
    # Real forward throat under the head beam: the paper opening of 001.
    hood = hood.cut(
        _box_at(
            r.beam_x0 - 0.020,
            r.frame_face_x - 0.004,
            -(r.frame_half_y + 0.01),
            r.frame_half_y + 0.01,
            DECK_TOP + 0.004,
            BEAM_BOTTOM - SEAT,
        )
    )
    part.visual(
        mesh_from_cadquery(hood, "punch_nose_hood"),
        origin=_local_origin(None, offset),
        material=mats["paint"],
        name="frame_form__nose_hood__hood", material_class_id="metal.paint_coated",
    )
    for index, sy in enumerate((-1.0, 1.0)):
        _y_cyl(
            part,
            offset,
            f"frame_form__nose_hood__pivot_boss_{index}",
            0.024,
            0.010,
            (r.pivot_x, sy * (r.frame_half_y + 0.004), PIVOT_Z),
            mats["body"],
        )


def _frame_form_c_loop_build(
    part, offset: tuple[float, float, float], r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """One-piece deep-throat C profile: spine, head and a die-bearing lower jaw."""
    x_front = r.beam_x0 - 0.004
    x_rear = r.frame_face_x + 0.062
    jaw_top = DIE_TOP + 0.001
    body = (
        cq.Workplane("XZ")
        .polyline(
            [
                (x_front, DECK_TOP + 0.001),
                (x_rear, DECK_TOP + 0.001),
                (x_rear, PIVOT_Z + 0.014),
                (x_front, PIVOT_Z + 0.014),
                (x_front, BEAM_TOP - 0.002),
                (r.frame_face_x + 0.004, BEAM_TOP - 0.002),
                (r.frame_face_x + 0.004, jaw_top),
                (x_front, jaw_top),
            ]
        )
        .close()
        .extrude(r.frame_half_y, both=True)
    )
    body = body.cut(_lever_slot(r, x_front - 0.020, x_rear + 0.010))
    body = body.cut(_station_corridor(r))
    # The lower jaw is the die carrier: every station passes through it.
    for y in r.station_y:
        body = body.cut(
            _z_bore(r.punch_line_x_m, y, 0.0125, DECK_TOP - 0.01, jaw_top + 0.01)
        )

    part.visual(
        mesh_from_cadquery(body, "punch_c_loop_frame"),
        origin=_local_origin(None, offset),
        material=mats["body"],
        name="frame_form__c_loop__c_frame_body", material_class_id="metal.paint_coated",
    )
    for index, sy in enumerate((-1.0, 1.0)):
        _y_cyl(
            part,
            offset,
            f"frame_form__c_loop__pivot_cheek_{index}",
            0.022,
            0.010,
            (r.pivot_x, sy * (r.frame_half_y + 0.004), PIVOT_Z),
            mats["dark_steel"],
        )


_FRAME_BUILDERS = {
    "nose_hood": _frame_form_nose_hood_build,
    "side_plate": _frame_form_side_plate_build,
    "c_loop": _frame_form_c_loop_build,
}


def _frame_offset(r: ResolvedConfig) -> tuple[float, float, float]:
    """The frame's local origin, chosen inside the head beam."""
    return (r.frame_face_x + 0.030, 0.0, DECK_TOP + 0.010)


def _build_frame(model: ArticulatedObject, base, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("frame", meta={"role": "frame"})
    off = _frame_offset(r)
    frame.visual(
        _head_beam_mesh(r),
        origin=_local_origin(None, off),
        material=mats["paint"],
        name="head_beam",
        material_class_id="metal.paint_coated",
    )
    _FRAME_BUILDERS[r.frame_form](frame, off, r, mats)
    if r.actuation in ("direct_lever", "compound_lever", "lever_linkage"):
        # Host adaptation: a lever needs a real pivot axle through the cheeks.
        _y_cyl(
            frame,
            off,
            "pivot_axle",
            AXLE_R,
            2.0 * (r.strap_y + 0.008)
            if r.actuation == "compound_lever"
            else 2.0 * (r.frame_half_y + 0.012),
            (r.pivot_x, 0.0, PIVOT_Z),
            mats["steel"],
        )
    if r.actuation == "plunger":
        # Host adaptation: the press plunger needs a bored top bridge on posts.
        bridge = _box_at(
            r.punch_line_x_m - 0.030,
            r.punch_line_x_m + 0.030,
            -(0.5 * r.station_span_m + 0.034),
            0.5 * r.station_span_m + 0.034,
            BRIDGE_BOTTOM,
            BRIDGE_BOTTOM + BRIDGE_T,
        )
        bridge = bridge.cut(
            _z_bore(
                r.punch_line_x_m, 0.0, 0.009 + FIT, BRIDGE_BOTTOM - 0.01, BRIDGE_BOTTOM + 0.03
            )
        )
        for sy in (-1.0, 1.0):
            y = sy * (0.5 * r.station_span_m + 0.019)
            bridge = bridge.union(
                _box_at(
                    r.punch_line_x_m - 0.012,
                    r.punch_line_x_m + 0.012,
                    y - 0.007,
                    y + 0.007,
                    BEAM_TOP - 0.002,
                    BRIDGE_BOTTOM + 0.001,
                )
            )
        frame.visual(
            mesh_from_cadquery(bridge, "punch_plunger_bridge"),
            origin=_local_origin(None, off),
            material=mats["body"],
            name="actuation__plunger__bridge", material_class_id="metal.paint_coated",
        )
    model.articulation(
        "base_to_frame",
        ArticulationType.FIXED,
        parent=base,
        child=frame,
        origin=Origin(xyz=off),
    )
    return frame


# --- punch station candidates ------------------------------------------------
def _punch_station_collared_pin_build(part, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    part.visual(
        Box((0.026, 0.026, BLOCK_H)),
        origin=Origin(xyz=(0.0, 0.0, BLOCK_TOP - 0.5 * BLOCK_H - BEAM_BOTTOM)),
        material=mats["paint"],
        name=f"punch_station__collared_pin__carriage_block_{index}", material_class_id="metal.paint_coated",
    )
    part.visual(
        Cylinder(radius=STEM_R, length=STEM_LEN),
        origin=Origin(
            xyz=(0.0, 0.0, BLOCK_TOP - 0.002 + 0.5 * STEM_LEN - BEAM_BOTTOM)
        ),
        material=mats["steel"],
        name=f"punch_station__collared_pin__guide_stem_{index}", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=0.010, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, BLOCK_TOP - BLOCK_H - 0.002 - BEAM_BOTTOM)),
        material=mats["plastic"],
        name=f"punch_station__collared_pin__spring_cap_{index}", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Cylinder(radius=PIN_R, length=PIN_LEN),
        origin=Origin(xyz=(0.0, 0.0, PIN_BOTTOM + 0.5 * PIN_LEN - BEAM_BOTTOM)),
        material=mats["steel"],
        name=f"punch_station__collared_pin__punch_pin_{index}", material_class_id="metal.steel_bare",
    )


def _punch_station_long_pin_build(part, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    part.visual(
        Box((0.036, 0.042, BLOCK_H)),
        origin=Origin(xyz=(0.0, 0.0, BLOCK_TOP - 0.5 * BLOCK_H - BEAM_BOTTOM)),
        material=mats["dark_steel"],
        name=f"punch_station__long_pin__carriage_block_{index}", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=STEM_R, length=STEM_LEN),
        origin=Origin(
            xyz=(0.0, 0.0, BLOCK_TOP - 0.002 + 0.5 * STEM_LEN - BEAM_BOTTOM)
        ),
        material=mats["steel"],
        name=f"punch_station__long_pin__guide_stem_{index}", material_class_id="metal.steel_bare",
    )
    pin_len = PIN_LEN + 0.010
    part.visual(
        Cylinder(radius=PIN_R + 0.0005, length=pin_len),
        origin=Origin(xyz=(0.0, 0.0, PIN_BOTTOM + 0.5 * pin_len - BEAM_BOTTOM)),
        material=mats["steel"],
        name=f"punch_station__long_pin__punch_pin_{index}", material_class_id="metal.steel_bare",
    )


_STATION_BUILDERS = {
    "collared_pin": _punch_station_collared_pin_build,
    "long_pin": _punch_station_long_pin_build,
}


def _build_stations(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> list:
    carriages = []
    for index, y in enumerate(r.station_y):
        part = model.part(
            f"punch_station__{r.punch_station}__carriage_{index}",
            meta={
                "role": "punch_carriage",
                "index": index,
                "motion_qc_repeat_group": "punch_stations",
            },
        )
        _STATION_BUILDERS[r.punch_station](part, r, mats, index)
        off = _frame_offset(r)
        model.articulation(
            f"frame_to_punch_carriage_{index}",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=part,
            origin=Origin(
                xyz=(r.punch_line_x_m - off[0], y - off[1], BEAM_BOTTOM - off[2])
            ),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=1400.0, velocity=0.12, lower=-PUNCH_TRAVEL, upper=0.0
            ),
            meta={
                "positive_motion": "returns the carriage to the top of its stroke",
                "motion_qc_repeat_group": "punch_stations",
            },
        )
        carriages.append(part)
    return carriages


# --- actuation candidates ----------------------------------------------------
def _pivot_eye_mesh(name: str, radius: float = 0.016, width: float = 0.024):
    """A pivot eye bored for the frame axle: a real running fit, not a boss."""
    eye = cq.Workplane("XY").cylinder(height=width, radius=radius, direct=(0.0, 1.0, 0.0))
    eye = eye.cut(
        cq.Workplane("XY").cylinder(height=width * 3.0, radius=AXLE_R + FIT, direct=(0.0, 1.0, 0.0))
    )
    return mesh_from_cadquery(eye, name)


def _pivot_joint(model, frame, handle, r: ResolvedConfig, *, lower: float, upper: float) -> None:
    off = _frame_offset(r)
    provider = AxisInterface(
        name="frame_to_handle__provider",
        point=(r.pivot_x - off[0], -off[1], PIVOT_Z - off[2]),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name="frame_to_handle__consumer", axis=(0.0, 1.0, 0.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "frame_to_handle",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=handle,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=280.0, velocity=1.2, lower=lower, upper=upper),
        meta={"positive_motion": "lifts the lever away from the punch stroke"},
    )
    register_interface_mate(model, "frame_to_handle", mate)


def _actuation_direct_lever_build(model, frame, r, mats, carriages) -> list:
    handle = model.part(
        "actuation__direct_lever__handle", meta={"role": "actuator"}
    )
    handle.visual(
        _pivot_eye_mesh("punch_direct_lever_eye"),
        material=mats["steel"],
        name="actuation__direct_lever__pivot_eye", material_class_id="metal.steel_bare",
    )
    bar_len = r.lever_reach_m
    handle.visual(
        Box((bar_len, 0.018, 0.011)),
        origin=Origin(xyz=(-0.5 * bar_len - 0.010, 0.0, 0.0)),
        material=mats["steel"],
        name="actuation__direct_lever__lever_arm", material_class_id="metal.steel_bare",
    )
    _y_cyl(
        handle,
        (0.0, 0.0, 0.0),
        "actuation__direct_lever__grip_stem",
        0.009,
        0.020,
        (-bar_len - 0.012, 0.0, 0.0),
        mats["steel"],
    )
    handle.visual(
        Sphere(radius=0.023),
        origin=Origin(xyz=(-bar_len - 0.030, 0.0, 0.0)),
        material=mats["plastic"],
        name="actuation__direct_lever__ball_grip", material_class_id="plastic.opaque_glossy_molded",
    )
    _pivot_joint(model, frame, handle, r, lower=-0.12, upper=0.95)
    return [handle]


def _actuation_compound_lever_build(model, frame, r, mats, carriages) -> list:
    handle = model.part(
        "actuation__compound_lever__handle", meta={"role": "actuator"}
    )
    bar_len = r.lever_reach_m
    for index, sy in enumerate((-1.0, 1.0)):
        y = sy * r.strap_y
        handle.visual(
            Box((bar_len, 0.015, 0.012)),
            origin=Origin(xyz=(-0.5 * bar_len - 0.010, y, 0.0)),
            material=mats["body"],
            name=f"actuation__compound_lever__handle_arm_{index}", material_class_id="metal.paint_coated",
        )
        handle.visual(
            _pivot_eye_mesh(f"punch_compound_pivot_disc_{index}", radius=0.019, width=0.010),
            origin=Origin(xyz=(0.0, y, 0.0)),
            material=mats["plastic"],
            name=f"actuation__compound_lever__pivot_disc_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    # The two straps are tied together by the U grip at the front; nothing may
    # cross the pivot line, where the cast frame sits between them.
    handle.visual(
        Box((0.060, 2.0 * r.strap_y + 0.034, 0.038)),
        origin=Origin(xyz=(-bar_len - 0.004, 0.0, 0.0)),
        material=mats["plastic"],
        name="actuation__compound_lever__handle_grip", material_class_id="plastic.opaque_glossy_molded",
    )
    _pivot_joint(model, frame, handle, r, lower=-0.16, upper=0.90)
    return [handle]


def _actuation_lever_linkage_build(model, frame, r, mats, carriages) -> list:
    handle = model.part(
        "actuation__lever_linkage__handle", meta={"role": "actuator"}
    )
    bar_len = r.lever_reach_m
    handle.visual(
        _pivot_eye_mesh("punch_lever_linkage_eye"),
        material=mats["steel"],
        name="actuation__lever_linkage__pivot_eye", material_class_id="metal.steel_bare",
    )
    handle.visual(
        Box((bar_len, 0.018, 0.011)),
        origin=Origin(xyz=(-0.5 * bar_len - 0.010, 0.0, 0.0)),
        material=mats["steel"],
        name="actuation__lever_linkage__lever_arm", material_class_id="metal.steel_bare",
    )
    handle.visual(
        Box((0.020, 0.010, 0.030)),
        origin=Origin(xyz=(-0.035, LINK_Y, 0.011)),
        material=mats["steel"],
        name="actuation__lever_linkage__link_lug", material_class_id="metal.steel_bare",
    )
    handle.visual(
        Box((0.020, 2.0 * LINK_Y, 0.011)),
        origin=Origin(xyz=(-0.035, 0.0, 0.0)),
        material=mats["steel"],
        name="actuation__lever_linkage__lug_web", material_class_id="metal.steel_bare",
    )
    _y_cyl(
        handle,
        (0.0, 0.0, 0.0),
        "actuation__lever_linkage__grip_stem",
        0.009,
        0.020,
        (-bar_len - 0.012, 0.0, 0.0),
        mats["steel"],
    )
    handle.visual(
        Sphere(radius=0.023),
        origin=Origin(xyz=(-bar_len - 0.030, 0.0, 0.0)),
        material=mats["plastic"],
        name="actuation__lever_linkage__ball_grip", material_class_id="plastic.opaque_glossy_molded",
    )
    _pivot_joint(model, frame, handle, r, lower=-0.12, upper=0.90)

    link = model.part("actuation__lever_linkage__drag_link", meta={"role": "transmission"})
    link_len = 0.030 + 0.04 * r.lever_reach_m
    plate = _box_at(0.008, link_len - 0.008, -0.005, 0.005, -0.009, -0.001)
    for x in (0.0, link_len):
        plate = plate.union(
            cq.Workplane("XY")
            .transformed(offset=(x, 0.0, -0.004))
            .cylinder(height=0.010, radius=0.008, direct=(0.0, 0.0, 1.0))
        )
        plate = plate.cut(
            cq.Workplane("XY")
            .transformed(offset=(x, 0.0, 0.0))
            .cylinder(height=0.04, radius=0.0034 + FIT, direct=(0.0, 1.0, 0.0))
        )
    link.visual(
        mesh_from_cadquery(plate, "punch_drag_link_plate"),
        material=mats["dark_steel"],
        name="actuation__lever_linkage__link_plate", material_class_id="metal.blackened_gunmetal",
    )
    for index, x in enumerate((0.0, link_len)):
        _y_cyl(
            link,
            (0.0, 0.0, 0.0),
            f"actuation__lever_linkage__capture_pin_{index}",
            0.0034 + FIT + 0.0004,
            2.0 * (LINK_PLATE_Y - LINK_Y - 0.005 - SEAT),
            (x, 0.0, 0.0),
            mats["steel"],
        )
    # The link hangs from a bracket above the lever bar and stays clear of the
    # head beam over the whole lever arc: its lowest reach is pivot height minus
    # the bracket rise plus the link length.
    provider = AxisInterface(
        name="handle_to_drag_link__provider",
        point=(-0.035, LINK_PLATE_Y, 0.022),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name="handle_to_drag_link__consumer", axis=(0.0, 1.0, 0.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "handle_to_drag_link",
        ArticulationType.REVOLUTE,
        parent=handle,
        child=link,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=180.0, velocity=1.0, lower=-0.60, upper=0.10),
        mimic=Mimic(joint="frame_to_handle", multiplier=-0.60, offset=0.0),
    )
    register_interface_mate(model, "handle_to_drag_link", mate)
    return [handle, link]


def _actuation_plunger_build(model, frame, r, mats, carriages) -> list:
    plunger = model.part("actuation__plunger__plunger", meta={"role": "actuator"})
    stem_z0 = DRIVER_Z0 + 0.004
    stem_z1 = CAP_Z0 + CAP_T - 0.006
    plunger.visual(
        Cylinder(radius=0.009, length=stem_z1 - stem_z0),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (stem_z0 + stem_z1) - BEAM_TOP)),
        material=mats["steel"],
        name="actuation__plunger__plunger_stem", material_class_id="metal.steel_bare",
    )
    # The driver plate bears on the carriage stem tops; the plunger mimics
    # carriage 0, so that 1 mm bearing gap is preserved through the stroke.
    plunger.visual(
        Box((0.024, r.station_span_m + 0.020, DRIVER_T)),
        origin=Origin(xyz=(0.0, 0.0, DRIVER_Z0 + 0.5 * DRIVER_T - BEAM_TOP)),
        material=mats["paint"],
        name="actuation__plunger__driver_plate", material_class_id="metal.paint_coated",
    )
    collar = (
        cq.Workplane("XY")
        .cylinder(height=0.010, radius=0.014, direct=(0.0, 0.0, 1.0))
        .cut(cq.Workplane("XY").cylinder(height=0.05, radius=0.0088, direct=(0.0, 0.0, 1.0)))
    )
    plunger.visual(
        mesh_from_cadquery(collar, "punch_return_spring_collar"),
        origin=Origin(xyz=(0.0, 0.0, DRIVER_Z0 + DRIVER_T + 0.006 - BEAM_TOP)),
        material=mats["body"],
        name="actuation__plunger__return_spring_collar", material_class_id="metal.paint_coated",
    )
    plunger.visual(
        Cylinder(radius=0.032, length=CAP_T),
        origin=Origin(xyz=(0.0, 0.0, CAP_Z0 + 0.5 * CAP_T - BEAM_TOP)),
        material=mats["plastic"],
        name="actuation__plunger__press_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "frame_to_plunger",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=plunger,
        origin=Origin(
            xyz=(
                r.punch_line_x_m - _frame_offset(r)[0],
                -_frame_offset(r)[1],
                BEAM_TOP - _frame_offset(r)[2],
            )
        ),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=900.0, velocity=0.18, lower=-PUNCH_TRAVEL, upper=0.0
        ),
        mimic=Mimic(joint="frame_to_punch_carriage_0", multiplier=1.0, offset=0.0),
        meta={"positive_motion": "returns the press plunger to the top of its stroke"},
    )
    return [plunger]


_ACTUATION_BUILDERS = {
    "direct_lever": _actuation_direct_lever_build,
    "compound_lever": _actuation_compound_lever_build,
    "plunger": _actuation_plunger_build,
    "lever_linkage": _actuation_lever_linkage_build,
}


# --- chip handling candidates ------------------------------------------------
def _chip_handling_pull_out_tray_build(model, base, r, mats) -> None:
    tray = model.part("chip_tray", meta={"role": "chip_bed"})
    x0 = r.cavity_x0 + 0.001
    x1 = r.cavity_x1 - 0.001
    hy = r.cavity_half_y - 0.001
    z0 = FOOT_H + SOLE_T + 0.005
    z1 = DECK_TOP - 0.010
    cx = 0.5 * (x0 + x1)
    cz = 0.5 * (z0 + z1)
    off = (cx, 0.0, cz)
    shell = _box_at(x0, x1, -hy, hy, z0, z1)
    shell = shell.cut(
        _box_at(x0 + 0.005, x1 - 0.005, -hy + 0.005, hy - 0.005, z0 + 0.004, z1 + 0.01)
    )
    tray.visual(
        mesh_from_cadquery(shell, "punch_chip_tray"),
        origin=_local_origin(None, off),
        material=mats["plastic"],
        name="chip_handling__pull_out_tray__tray_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    tray.visual(
        Box((0.010, 2.0 * hy - 0.020, z1 - z0 + 0.008)),
        origin=_local_origin(Origin(xyz=(x0 - 0.005, 0.0, cz + 0.004)), off),
        material=mats["plastic"],
        name="chip_handling__pull_out_tray__tray_front", material_class_id="plastic.opaque_glossy_molded",
    )
    tray.visual(
        Box((0.012, 0.048, 0.006)),
        origin=_local_origin(Origin(xyz=(x0 - 0.014, 0.0, cz + 0.004)), off),
        material=mats["dark_steel"],
        name="chip_handling__pull_out_tray__pull_loop", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        "base_to_chip_tray",
        ArticulationType.PRISMATIC,
        parent=base,
        child=tray,
        origin=Origin(xyz=off),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=18.0, velocity=0.18, lower=0.0, upper=r.tray_travel_m
        ),
        meta={"positive_motion": "pulls the chip drawer out of the base"},
    )


def _chip_handling_fixed_bed_build(model, base, r, mats) -> None:
    bed = model.part("chip_tray", meta={"role": "chip_bed"})
    off = (0.5 * (r.bed_x0 + r.bed_x1), 0.0, DECK_TOP + 0.0025 - 0.5 * SEAT)
    bed.visual(
        Box((r.bed_x1 - r.bed_x0, 2.0 * (r.deck_half_y - 0.010), 0.005 + SEAT)),
        origin=_local_origin(Origin(xyz=off), off),
        material=mats["plastic"],
        name="chip_handling__fixed_bed__tray_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    bed.visual(
        Box((0.008, 2.0 * (r.deck_half_y - 0.024), 0.012)),
        origin=_local_origin(
            Origin(xyz=(r.bed_x0 + 0.004, 0.0, DECK_TOP + 0.008)), off
        ),
        material=mats["plastic"],
        name="chip_handling__fixed_bed__tray_pull_lip", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "base_to_chip_tray",
        ArticulationType.FIXED,
        parent=base,
        child=bed,
        origin=Origin(xyz=off),
    )


_CHIP_BUILDERS = {
    "pull_out_tray": _chip_handling_pull_out_tray_build,
    "fixed_bed": _chip_handling_fixed_bed_build,
}


# --- paper guide candidates --------------------------------------------------
def _paper_guide_rail_guides_build(model, base, r, mats) -> list:
    rail = model.part("guide_rail", meta={"role": "paper_rail"})
    rail_x = r.punch_line_x_m - 0.060
    rail_z = r.guide_z + RAIL_LIFT
    rail.visual(
        Box((0.026, 2.0 * r.rail_half_y, 0.005)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["steel"],
        name="paper_guide__rail_guides__guide_bar", material_class_id="metal.steel_bare",
    )
    for index, sy in enumerate((-1.0, 1.0)):
        # Standoffs carry the rail clear of the deck so the stop collars can
        # wrap it from below without cutting into the base.
        rail.visual(
            Box((0.024, 0.020, RAIL_LIFT + 0.0025 + SEAT)),
            origin=Origin(
                xyz=(
                    0.0,
                    sy * (r.deck_half_y - 0.030),
                    0.5 * (0.0025 - RAIL_LIFT - SEAT),
                )
            ),
            material=mats["steel"],
            name=f"paper_guide__rail_guides__rail_standoff_{index}", material_class_id="metal.steel_bare",
        )
    for index in range(6):
        y = (index - 2.5) * (r.rail_half_y / 3.2)
        rail.visual(
            Box((0.018, 0.0012, 0.0008)),
            origin=Origin(xyz=(0.0, y, 0.0028)),
            material=mats["dark_steel"],
            name=f"paper_guide__rail_guides__rail_tick_{index}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    model.articulation(
        "base_to_guide_rail",
        ArticulationType.FIXED,
        parent=base,
        child=rail,
        origin=Origin(xyz=(rail_x, 0.0, rail_z)),
    )

    stops = []
    for index, sy in enumerate((-1.0, 1.0)):
        stop = model.part(
            f"paper_guide__rail_guides__paper_stop_{index}", meta={"role": "paper_stop"}
        )
        collar = _box_at(-0.017, 0.017, -0.011, 0.011, -0.008, 0.011)
        collar = collar.cut(
            _box_at(-0.014, 0.014, -0.02, 0.02, -0.0025 - FIT, 0.0025 + FIT)
        )
        stop.visual(
            mesh_from_cadquery(collar, f"punch_guide_collar_{index}"),
            material=mats["paint"],
            name=f"paper_guide__rail_guides__collar_{index}", material_class_id="metal.paint_coated",
        )
        stop.visual(
            Box((0.038, 0.006, 0.026)),
            origin=Origin(xyz=(-0.012, -sy * 0.008, 0.022)),
            material=mats["paint"],
            name=f"paper_guide__rail_guides__stop_fence_{index}", material_class_id="metal.paint_coated",
        )
        stop.visual(
            Cylinder(radius=0.006, length=0.010),
            origin=Origin(xyz=(0.0, 0.0, 0.015)),
            material=mats["dark_steel"],
            name=f"paper_guide__rail_guides__thumb_screw_{index}", material_class_id="metal.blackened_gunmetal",
        )
        model.articulation(
            f"guide_rail_to_paper_stop_{index}",
            ArticulationType.PRISMATIC,
            parent=rail,
            child=stop,
            origin=Origin(xyz=(0.0, sy * (r.rail_half_y - 0.020), 0.0)),
            axis=(0.0, -sy, 0.0),
            motion_limits=MotionLimits(
                effort=35.0, velocity=0.18, lower=0.0, upper=r.guide_travel_m
            ),
            meta={"positive_motion": "slides the paper stop inward along the rail"},
        )
        stops.append(stop)
    return stops


def _paper_guide_bed_guides_build(model, base, r, mats) -> list:
    lateral = model.part("paper_guide__bed_guides__lateral_guide", meta={"role": "paper_stop"})
    lateral.visual(
        Box((0.045, 0.028, 0.004)),
        origin=Origin(xyz=(0.0, 0.0, 0.002 - SEAT)),
        material=mats["body"],
        name="paper_guide__bed_guides__lateral_foot", material_class_id="metal.paint_coated",
    )
    lateral.visual(
        Box((0.045, 0.005, 0.026)),
        origin=Origin(xyz=(0.0, 0.0, 0.015)),
        material=mats["body"],
        name="paper_guide__bed_guides__lateral_fence", material_class_id="metal.paint_coated",
    )
    lateral.visual(
        Cylinder(radius=0.008, length=0.007),
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
        material=mats["plastic"],
        name="paper_guide__bed_guides__lateral_knob", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "base_to_lateral_guide",
        ArticulationType.PRISMATIC,
        parent=base,
        child=lateral,
        origin=Origin(xyz=(r.punch_line_x_m - 0.055, r.deck_half_y - 0.016, r.guide_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=12.0, velocity=0.10, lower=0.0, upper=r.guide_travel_m
        ),
        meta={"positive_motion": "closes the lateral stop onto the paper"},
    )

    depth = model.part("paper_guide__bed_guides__depth_guide", meta={"role": "paper_stop"})
    depth.visual(
        Box((0.030, 0.028, 0.004)),
        origin=Origin(xyz=(0.0, 0.0, 0.002 - SEAT)),
        material=mats["body"],
        name="paper_guide__bed_guides__depth_foot", material_class_id="metal.paint_coated",
    )
    depth.visual(
        Box((0.005, 0.070, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, 0.014)),
        material=mats["body"],
        name="paper_guide__bed_guides__depth_fence", material_class_id="metal.paint_coated",
    )
    depth.visual(
        Cylinder(radius=0.008, length=0.007),
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
        material=mats["plastic"],
        name="paper_guide__bed_guides__depth_knob", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "base_to_depth_guide",
        ArticulationType.PRISMATIC,
        parent=base,
        child=depth,
        origin=Origin(
            xyz=(
                -0.5 * r.base_length_m + 0.030,
                -(r.deck_half_y - 0.048),
                r.guide_z,
            )
        ),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=12.0, velocity=0.10, lower=0.0, upper=r.depth_travel_m
        ),
        meta={"positive_motion": "slides the depth stop toward the punch line"},
    )
    return [lateral, depth]


_GUIDE_BUILDERS = {
    "rail_guides": _paper_guide_rail_guides_build,
    "bed_guides": _paper_guide_bed_guides_build,
}


# --- assembly ----------------------------------------------------------------
def build_picturex_0611_hole_punch(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Hole_punch",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "hand-driven vertical punch carriages over fixed dies",
        },
    )
    mats = _materials(model, r)
    base = _build_base(model, r, mats)
    frame = _build_frame(model, base, r, mats)
    carriages = _build_stations(model, frame, r, mats)
    _ACTUATION_BUILDERS[r.actuation](model, frame, r, mats, carriages)
    _CHIP_BUILDERS[r.chip_handling](model, base, r, mats)
    _GUIDE_BUILDERS[r.paper_guide](model, base, r, mats)

    pressed = {
        f"frame_to_punch_carriage_{i}": -PUNCH_TRAVEL for i in range(r.punch_station_count)
    }
    risk = [
        {f"frame_to_punch_carriage_{i}": 0.0 for i in range(r.punch_station_count)},
        dict(pressed),
    ]
    if r.actuation in ("direct_lever", "compound_lever", "lever_linkage"):
        risk[1] = dict(pressed) | {"frame_to_handle": -0.12}
        risk.append(dict(pressed) | {"frame_to_handle": 0.90})
    if r.chip_handling == "pull_out_tray":
        risk[0]["base_to_chip_tray"] = r.tray_travel_m
    model.meta["risk_poses"] = tuple(risk)
    if r.punch_station_count > 1:
        model.meta["coupled_joint_pairs"] = (
            ("frame_to_punch_carriage_0", "frame_to_punch_carriage_1"),
        )
    return model


def build_seeded_picturex_0611_hole_punch(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_hole_punch(config_from_seed(seed), assets=assets)


# --- authored tests -----------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_hole_punch_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    bases = _parts_by_role(model, "base")
    frames = _parts_by_role(model, "frame")
    carriages = _parts_by_role(model, "punch_carriage")
    actuators = _parts_by_role(model, "actuator")
    beds = _parts_by_role(model, "chip_bed")
    joints = {j.name: j for j in model.articulations}

    station_joints = [
        joints.get(f"frame_to_punch_carriage_{i}") for i in range(r.punch_station_count)
    ]

    def _is_pris_z(j) -> bool:
        return (
            j is not None
            and j.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(v, 6) for v in j.axis) == (0.0, 0.0, 1.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    ctx.check(
        "category_anchor: heavy-duty punch base, frame and station chain",
        len(bases) == 1
        and len(frames) == 1
        and len(actuators) == 1
        and len(beds) == 1
        and len(carriages) == r.punch_station_count
        and bool(model.root_parts())
        and model.root_parts()[0].name == "base"
        and joints["base_to_frame"].articulation_type == ArticulationType.FIXED
        and all(_is_pris_z(j) for j in station_joints)
        and all(j.parent == "frame" for j in station_joints),
        details=(
            f"bases={len(bases)} frames={len(frames)} carriages={len(carriages)} "
            f"actuators={len(actuators)} beds={len(beds)} joints={sorted(joints)}"
        ),
    )

    # The stems stay inside their beam bores over the whole stroke, and each pin
    # reaches into its own die ring without ever touching the deck.
    ctx.check(
        "category_anchor: punch pins stay guided over their dies",
        0.0 < FIT <= 0.001
        and STEM_LEN >= BEAM_T + PUNCH_TRAVEL + 0.002
        and PIN_BOTTOM - PUNCH_TRAVEL < DIE_TOP
        and PIN_BOTTOM > DIE_TOP + 0.010
        and len(set(r.station_y)) == r.punch_station_count
        and all(
            abs(r.station_y[i + 1] - r.station_y[i] - STATION_PITCH) < 1e-9
            for i in range(r.punch_station_count - 1)
        )
        and r.deck_half_y >= 0.5 * r.station_span_m + 0.070
        and r.punch_line_x_m < r.frame_face_x - 0.040,
        details=(
            f"stem_len={STEM_LEN} pin_bottom={PIN_BOTTOM} die_top={DIE_TOP} "
            f"station_y={r.station_y} deck_half_y={r.deck_half_y}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    frame_ok = {
        "nose_hood": any("nose_hood__hood" in n for n in visual_names)
        and sum(1 for n in visual_names if "nose_hood__pivot_boss" in n) == 2,
        "side_plate": sum(1 for n in visual_names if "side_plate__side_plate_" in n) == 2
        and any("side_plate__head_neck" in n for n in visual_names),
        "c_loop": any("c_loop__c_frame_body" in n for n in visual_names)
        and sum(1 for n in visual_names if "c_loop__pivot_cheek" in n) == 2,
    }[r.frame_form]
    ctx.check("category_anchor: frame_form identity", frame_ok, details=f"frame_form={r.frame_form}")

    actuation_ok = {
        "direct_lever": any("direct_lever__ball_grip" in n for n in visual_names)
        and joints["frame_to_handle"].articulation_type == ArticulationType.REVOLUTE,
        "compound_lever": sum(1 for n in visual_names if "compound_lever__handle_arm" in n) == 2
        and any("compound_lever__handle_grip" in n for n in visual_names),
        "plunger": any("plunger__press_cap" in n for n in visual_names)
        and joints["frame_to_plunger"].mimic is not None
        and joints["frame_to_plunger"].mimic.joint == "frame_to_punch_carriage_0",
        "lever_linkage": any("lever_linkage__link_plate" in n for n in visual_names)
        and joints["handle_to_drag_link"].mimic is not None
        and joints["handle_to_drag_link"].mimic.joint == "frame_to_handle",
    }[r.actuation]
    ctx.check("category_anchor: actuation identity", actuation_ok, details=f"actuation={r.actuation}")

    station_ok = {
        "collared_pin": sum(1 for n in visual_names if "collared_pin__spring_cap" in n)
        == r.punch_station_count,
        "long_pin": sum(1 for n in visual_names if "long_pin__punch_pin" in n)
        == r.punch_station_count,
    }[r.punch_station]
    ctx.check(
        "category_anchor: punch_station identity",
        station_ok,
        details=f"punch_station={r.punch_station} n={r.punch_station_count}",
    )

    guide_ok = {
        "rail_guides": sum(1 for n in visual_names if "rail_guides__stop_fence" in n) == 2
        and len(_parts_by_role(model, "paper_rail")) == 1,
        "bed_guides": any("bed_guides__lateral_fence" in n for n in visual_names)
        and any("bed_guides__depth_fence" in n for n in visual_names),
    }[r.paper_guide]
    ctx.check("category_anchor: paper_guide identity", guide_ok, details=f"paper_guide={r.paper_guide}")

    chip_ok = {
        "pull_out_tray": joints["base_to_chip_tray"].articulation_type
        == ArticulationType.PRISMATIC
        and any("pull_out_tray__pull_loop" in n for n in visual_names)
        and any("pull_out_tray__tray_front" in n for n in visual_names),
        "fixed_bed": joints["base_to_chip_tray"].articulation_type == ArticulationType.FIXED
        and any("fixed_bed__tray_pull_lip" in n for n in visual_names),
    }[r.chip_handling]
    ctx.check(
        "category_anchor: chip_handling identity", chip_ok, details=f"chip_handling={r.chip_handling}"
    )

    # Motion evidence: pressing a station drives its pin down the full stroke.
    first = carriages[0]
    rest = ctx.part_world_aabb(first)
    with ctx.pose({station_joints[0]: -PUNCH_TRAVEL}):
        pressed = ctx.part_world_aabb(first)
    ctx.check(
        "a punch station drives its pin down the full stroke",
        rest is not None
        and pressed is not None
        and abs((rest[0][2] - pressed[0][2]) - PUNCH_TRAVEL) < 1e-3
        and pressed[0][2] < DIE_TOP,
        details=f"rest={rest} pressed={pressed}",
    )

    if r.actuation in ("direct_lever", "compound_lever", "lever_linkage"):
        handle_joint = joints["frame_to_handle"]
        up = None
        down = None
        with ctx.pose({handle_joint: handle_joint.motion_limits.upper}):
            up = ctx.part_world_aabb(actuators[0])
        with ctx.pose({handle_joint: handle_joint.motion_limits.lower}):
            down = ctx.part_world_aabb(actuators[0])
        ctx.check(
            "the hand lever swings through a real arc in front of the frame",
            up is not None
            and down is not None
            and up[1][2] > down[1][2] + 0.05
            and down[0][0] < r.punch_line_x_m,
            details=f"up={up} down={down}",
        )
    else:
        plunger_joint = joints["frame_to_plunger"]
        ctx.check(
            "the press plunger is slaved to the punch carriages",
            plunger_joint.articulation_type == ArticulationType.PRISMATIC
            and plunger_joint.mimic is not None
            and abs(plunger_joint.mimic.multiplier - 1.0) < 1e-9
            and plunger_joint.motion_limits.lower == -PUNCH_TRAVEL,
            details=f"plunger={plunger_joint.name}",
        )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_base_single_station_hood_lever",
        {
            "frame_form": "nose_hood",
            "actuation": "direct_lever",
            "punch_station": "long_pin",
            "paper_guide": "rail_guides",
            "chip_handling": "pull_out_tray",
            "punch_station_count": 1,
            "base_length_m": 0.300,
            "throat_depth_m": 0.045,
            "lever_reach_m": 0.200,
        },
        reason="smallest base and shallowest throat with one deep station and a drawer",
    ),
    corner_case(
        "max_base_four_stations_cloop_plunger",
        {
            "frame_form": "c_loop",
            "actuation": "plunger",
            "punch_station": "collared_pin",
            "paper_guide": "bed_guides",
            "chip_handling": "fixed_bed",
            "punch_station_count": 4,
            "base_length_m": 0.460,
            "throat_depth_m": 0.090,
            "lever_reach_m": 0.360,
        },
        reason="widest four-station head with the deepest throat and the bridged plunger",
    ),
    corner_case(
        "deep_throat_four_stations_linkage",
        {
            "frame_form": "side_plate",
            "actuation": "lever_linkage",
            "punch_station": "long_pin",
            "paper_guide": "rail_guides",
            "chip_handling": "pull_out_tray",
            "punch_station_count": 4,
            "base_length_m": 0.300,
            "throat_depth_m": 0.090,
            "lever_reach_m": 0.360,
        },
        reason="deepest throat on the shortest base with four stations and the drag link",
    ),
    corner_case(
        "wide_bed_guides_three_stations_hood",
        {
            "frame_form": "nose_hood",
            "actuation": "compound_lever",
            "punch_station": "collared_pin",
            "paper_guide": "bed_guides",
            "chip_handling": "fixed_bed",
            "punch_station_count": 3,
            "base_length_m": 0.460,
            "throat_depth_m": 0.045,
            "lever_reach_m": 0.200,
        },
        reason="shortest lever over the widest bed — tightest guide travel against the stations",
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
    "build_picturex_0611_hole_punch",
    "build_seeded_picturex_0611_hole_punch",
    "run_picturex_0611_hole_punch_tests",
]
