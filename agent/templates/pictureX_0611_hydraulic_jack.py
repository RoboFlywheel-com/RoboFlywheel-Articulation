# SPDX-License-Identifier: Apache-2.0

"""Self-contained crossed scissor lift jack template.

One rigid ``lift_base`` root carries the frame rails, the scissor pivot lugs and
the actuator.  Each of ``scissor_stage_count`` stages is a real X:

* ``arm_a`` is a REVOLUTE (+x) child of that stage's host -- the base for stage
  0, the previous ``lift_deck`` otherwise -- and is the stage's only independent
  joint;
* ``arm_b`` is a REVOLUTE (+x) child of ``arm_a`` at the cross pivot, mimicking
  the stage driver with multiplier ``-2``;
* the stage's ``lift_deck`` is a REVOLUTE (+x) child of ``arm_b`` at arm_b's
  upper pin, mimicking the stage driver with multiplier ``+1``.

Those two mimics are what makes the closed scissor loop exact inside a URDF
tree.  With the links authored at ``THETA0`` and the driver adding ``q``:

* arm_a's global angle is ``+(THETA0 + q)`` and arm_b's is ``-(THETA0 + q)``;
* arm_b's upper pin stays at a FIXED y and rises to ``2*a*sin(THETA0 + q)``, so
  the deck is pinned there and stays exactly level;
* arm_a's upper roller slides under the deck and arm_b's lower roller slides
  along the host rail, which is precisely how a scissor lift works.

Four component slots vary without touching the mechanism: ``arm_style``,
``frame_style``, ``deck_fitting`` and ``drive_unit``.  No source-replay import,
no motion clamping, no whole-part overlap allowance.
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
    AxisInterface,
    Box,
    Cylinder,
    LatheGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

ArmStyle = Literal["slotted_plate_arm", "boxed_bar_arm"]
FrameStyle = Literal["slotted_side_plate", "boxed_channel", "toe_channel"]
DeckFitting = Literal["flat_deck", "screw_riser", "vee_cradle"]
DriveUnit = Literal["hydraulic_pump", "air_over_hydraulic"]
PaletteStyle = Literal["lab_blue", "works_orange", "graphite", "signal_red"]

ARM_STYLES: tuple[ArmStyle, ...] = ("slotted_plate_arm", "boxed_bar_arm")
FRAME_STYLES: tuple[FrameStyle, ...] = ("slotted_side_plate", "boxed_channel", "toe_channel")
DECK_FITTINGS: tuple[DeckFitting, ...] = ("flat_deck", "screw_riser", "vee_cradle")
DRIVE_UNITS: tuple[DriveUnit, ...] = ("hydraulic_pump", "air_over_hydraulic")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("lab_blue", "works_orange", "graphite", "signal_red")


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("arm_style", ARM_STYLES),
        component_slot("frame_style", FRAME_STYLES),
        component_slot("deck_fitting", DECK_FITTINGS),
        component_slot("drive_unit", DRIVE_UNITS),
        multiplicity_slot("scissor_stage_count", (1, 2, 3), item_slot="arm_style"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "lab_blue": {
        "paint": (0.10, 0.24, 0.52, 1.0),
        "edge": (0.04, 0.13, 0.30, 1.0),
        "steel": (0.42, 0.45, 0.48, 1.0),
        "chrome": (0.72, 0.76, 0.79, 1.0),
        "dark": (0.09, 0.10, 0.11, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
    },
    "works_orange": {
        "paint": (0.88, 0.36, 0.09, 1.0),
        "edge": (0.62, 0.24, 0.05, 1.0),
        "steel": (0.30, 0.31, 0.33, 1.0),
        "chrome": (0.76, 0.78, 0.80, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
    },
    "graphite": {
        "paint": (0.24, 0.25, 0.27, 1.0),
        "edge": (0.13, 0.14, 0.15, 1.0),
        "steel": (0.48, 0.50, 0.52, 1.0),
        "chrome": (0.80, 0.82, 0.84, 1.0),
        "dark": (0.07, 0.07, 0.08, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
    },
    "signal_red": {
        "paint": (0.70, 0.13, 0.12, 1.0),
        "edge": (0.44, 0.07, 0.07, 1.0),
        "steel": (0.38, 0.39, 0.41, 1.0),
        "chrome": (0.75, 0.77, 0.79, 1.0),
        "dark": (0.09, 0.08, 0.08, 1.0),
        "rubber": (0.06, 0.05, 0.05, 1.0),
    },
}


# Scissor angle band.  The links are AUTHORED at THETA0, so the driver joint
# runs 0 .. THETA1-THETA0 and its neutral pose is the fully-lowered lift.
THETA0 = 0.26
THETA1 = 1.02
PLATE_T = 0.010          # link plate thickness in x
PLATE_H = 0.026          # link plate depth
ROLLER_R = 0.013         # slider roller radius; also the pivot rise above a rail
DECK_T = 0.012
BASE_PLATE_T = 0.010
RAIL_H = 0.026
# Rails/ties are authored from RAIL_Z0 so they overlap the floor plate they
# stand on.  Butting them at exactly z=BASE_PLATE_T is a coincident face,
# which the 1e-6 m same-part island check reads as disconnected.
RAIL_Z0 = BASE_PLATE_T - 0.002
RAIL_FULL_H = RAIL_H + 0.002
# Sub-millimetre lap: a fitting laps its host by less than the collision
# tolerance so QC reads real contact without an overlap allowance.
MOUNT = 0.0006
CLEVIS_HALF = 0.016    # clevis ear centre offset in x
CLEVIS_EAR_T = 0.011   # clevis ear thickness in x
# The lever boss journals MOUNT past each ear's inner face: real captured
# contact, but under the collision tolerance rather than spearing the ear.
CLEVIS_PIN_LEN = 2.0 * (CLEVIS_HALF - CLEVIS_EAR_T * 0.5 + MOUNT)
# Running gap under a slider roller: inside the 1 mm assembly tolerance, so the
# roller counts as supported by the rail it rides without penetrating it.
RUN_GAP = 0.0004


@dataclass(frozen=True)
class Config:
    arm_style: ArmStyle = "slotted_plate_arm"
    frame_style: FrameStyle = "slotted_side_plate"
    deck_fitting: DeckFitting = "flat_deck"
    drive_unit: DriveUnit = "hydraulic_pump"
    scissor_stage_count: int = 1
    deck_len_m: float | None = None
    deck_width_m: float | None = None
    arm_span_ratio: float | None = None
    palette_style: PaletteStyle = "lab_blue"
    name: str = "pictureX_0611_hydraulic_jack"


@dataclass(frozen=True)
class ResolvedConfig:
    arm_style: ArmStyle
    frame_style: FrameStyle
    deck_fitting: DeckFitting
    drive_unit: DriveUnit
    scissor_stage_count: int
    scissor_arm_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    deck_len_m: float
    deck_width_m: float
    arm_span_ratio: float
    arm_half_m: float        # a: half the link length
    stage_travel_rad: float  # driver range
    stage_lift_m: float      # lift of one stage at full travel
    rail_x: float            # base/deck rail plate x station
    arm_a_x: float           # arm_a plate x station
    arm_b_x: float           # arm_b plate x station
    pivot_rise: float        # pivot centreline above the rail top it sits on
    deck_centre_y: float     # deck centre in deck-local y
    deck_top_local_z: float  # deck top face in deck-local z
    base_rail_top_z: float
    drive_x: float
    drive_pivot_z: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x5C1_5504)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        arm_style=choices["arm_style"],
        frame_style=choices["frame_style"],
        deck_fitting=choices["deck_fitting"],
        drive_unit=choices["drive_unit"],
        scissor_stage_count=choices["scissor_stage_count"],
        deck_len_m=round(rng.uniform(0.30, 0.60), 4),
        deck_width_m=round(rng.uniform(0.22, 0.42), 4),
        arm_span_ratio=round(rng.uniform(0.72, 0.90), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"hydraulic_jack_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "arm_style": config.arm_style,
            "frame_style": config.frame_style,
            "deck_fitting": config.deck_fitting,
            "drive_unit": config.drive_unit,
            "scissor_stage_count": config.scissor_stage_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.deck_len_m is not None and not 0.30 <= float(config.deck_len_m) <= 0.60:
        raise ValueError("deck_len_m must be in [0.30, 0.60]")
    if config.deck_width_m is not None and not 0.22 <= float(config.deck_width_m) <= 0.42:
        raise ValueError("deck_width_m must be in [0.22, 0.42]")
    if config.arm_span_ratio is not None and not 0.72 <= float(config.arm_span_ratio) <= 0.90:
        raise ValueError("arm_span_ratio must be in [0.72, 0.90]")

    length = _clamp(config.deck_len_m, 0.30, 0.60) if config.deck_len_m is not None else 0.44
    width = _clamp(config.deck_width_m, 0.22, 0.42) if config.deck_width_m is not None else 0.30
    ratio = _clamp(config.arm_span_ratio, 0.72, 0.90) if config.arm_span_ratio is not None else 0.82

    a = length * ratio * 0.5
    travel = THETA1 - THETA0
    lift = 2.0 * a * (math.sin(THETA1) - math.sin(THETA0))

    rail_x = width * 0.5 - 0.018
    arm_a_x = rail_x - 0.016
    arm_b_x = arm_a_x - 0.014
    pivot_rise = ROLLER_R + RUN_GAP

    # The deck spans the whole slider run of arm_a's upper roller, which in
    # deck-local y runs from 2a*cos(THETA1) to 2a*cos(THETA0).
    deck_centre_y = a * math.cos(THETA0)
    deck_top_local_z = ROLLER_R - RUN_GAP + DECK_T

    base_rail_top_z = BASE_PLATE_T + RAIL_H
    drive_x = width * 0.5 + 0.010
    drive_pivot_z = base_rail_top_z + 0.052

    return ResolvedConfig(
        arm_style=config.arm_style,
        frame_style=config.frame_style,
        deck_fitting=config.deck_fitting,
        drive_unit=config.drive_unit,
        scissor_stage_count=int(config.scissor_stage_count),
        scissor_arm_count=2 * int(config.scissor_stage_count),
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        deck_len_m=length,
        deck_width_m=width,
        arm_span_ratio=ratio,
        arm_half_m=a,
        stage_travel_rad=travel,
        stage_lift_m=lift,
        rail_x=rail_x,
        arm_a_x=arm_a_x,
        arm_b_x=arm_b_x,
        pivot_rise=pivot_rise,
        deck_centre_y=deck_centre_y,
        deck_top_local_z=deck_top_local_z,
        base_rail_top_z=base_rail_top_z,
        drive_x=drive_x,
        drive_pivot_z=drive_pivot_z,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("arm_style", config.arm_style),
        ("frame_style", config.frame_style),
        ("deck_fitting", config.deck_fitting),
        ("drive_unit", config.drive_unit),
        ("scissor_stage_count", config.scissor_stage_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"jack_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"jack_{r.palette_style}_{key}"
    return mats


def _tube(name: str, outer_r: float, inner_r: float, z0: float, z1: float, segments: int = 24):
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(
            [(outer_r, z0), (outer_r, z1)],
            [(inner_r, z0), (inner_r, z1)],
            segments=segments,
        ),
        name,
    )


def _x_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _rev_axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    provider_radial: tuple[float, float, float],
    consumer_radial: tuple[float, float, float],
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
    mimic: Mimic | None = None,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=provider_radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=consumer_radial)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(lower=lower, upper=upper, effort=effort, velocity=velocity),
        mimic=mimic,
    )
    register_interface_mate(model, name, mate)


# --- scissor link candidates ------------------------------------------------
#
# Every link is authored along its own axis at a fixed authoring angle, and is
# addressed by the signed distance ``s`` along that axis from the PART ORIGIN
# (which is the joint the link hangs from).  arm_a's origin is its fixed pivot,
# so its body runs s in [0, 2a] and ``centre_s = a``.  arm_b's origin is the
# cross pivot in the MIDDLE of the link, so its body runs s in [-a, +a] and
# ``centre_s = 0``.  Getting that offset wrong is what makes arm_b's upper pin
# land on empty space and the link swing below the floor.
def _s_point(s: float, angle: float) -> tuple[float, float, float]:
    return (0.0, s * math.cos(angle), s * math.sin(angle))


def _arm_style_slotted_plate_arm_build(
    part, r: ResolvedConfig, mats: dict[str, str], *, half: float, angle: float, tag: str,
    centre_s: float,
) -> None:
    """Twin pressed link plates carrying a long lightening slot.

    The slot is real material removal, so each plate is authored as its two
    flanges plus end webs rather than a solid bar with a painted-on slot.
    """
    length = 2.0 * half
    _, cy, cz = _s_point(centre_s, angle)
    web = 0.007
    flange = (PLATE_H - 2.0 * web) * 0.5 + web
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * (r.arm_a_x if tag == "a" else r.arm_b_x)
        for i, dz in enumerate((-(PLATE_H - flange) * 0.5, (PLATE_H - flange) * 0.5)):
            part.visual(
                Box((PLATE_T, length, flange)),
                origin=Origin(
                    xyz=(x, cy - dz * math.sin(angle), cz + dz * math.cos(angle)),
                    rpy=(angle, 0.0, 0.0),
                ),
                material=mats["paint"],
                name=f"arm_style__slotted_plate_arm__flange_{tag}_{side}_{i}", material_class_id="metal.paint_coated",
            )
        for i, ds in enumerate((-half + 0.016, half - 0.016)):
            _, wy, wz = _s_point(centre_s + ds, angle)
            part.visual(
                Box((PLATE_T, 0.030, PLATE_H)),
                origin=Origin(xyz=(x, wy, wz), rpy=(angle, 0.0, 0.0)),
                material=mats["paint"],
                name=f"arm_style__slotted_plate_arm__web_{tag}_{side}_{i}", material_class_id="metal.paint_coated",
            )
        # Exposed zinc pivot head on the outer face of each plate.
        part.visual(
            Cylinder(radius=0.010, length=0.006),
            origin=Origin(
                xyz=(x + sx * (PLATE_T * 0.5 + 0.002), 0.0, 0.0),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["chrome"],
            name=f"arm_style__slotted_plate_arm__pivot_head_{tag}_{side}", material_class_id="metal.chrome_polished",
        )


def _arm_style_boxed_bar_arm_build(
    part, r: ResolvedConfig, mats: dict[str, str], *, half: float, angle: float, tag: str,
    centre_s: float,
) -> None:
    """Plain solid boxed bar links with welded end bosses."""
    length = 2.0 * half
    _, cy, cz = _s_point(centre_s, angle)
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * (r.arm_a_x if tag == "a" else r.arm_b_x)
        part.visual(
            Box((PLATE_T, length, PLATE_H)),
            origin=Origin(xyz=(x, cy, cz), rpy=(angle, 0.0, 0.0)),
            material=mats["paint"],
            name=f"arm_style__boxed_bar_arm__bar_{tag}_{side}", material_class_id="metal.paint_coated",
        )
        for i, ds in enumerate((-half, half)):
            _, by, bz = _s_point(centre_s + ds, angle)
            _x_cyl(
                part,
                f"arm_style__boxed_bar_arm__end_boss_{tag}_{side}_{i}",
                PLATE_H * 0.5,
                PLATE_T + 0.004,
                (x, by, bz),
                mats["edge"],
            )


_ARM_BUILDERS = {
    "slotted_plate_arm": _arm_style_slotted_plate_arm_build,
    "boxed_bar_arm": _arm_style_boxed_bar_arm_build,
}


def _add_arm_common(part, r: ResolvedConfig, mats: dict[str, str], *, half: float,
                    angle: float, tag: str, tie_s: float, roller_s: float) -> None:
    """Tie spacer tube across the link, plus the slider roller at its free end.

    The tie tube is what makes the two side plates one connected solid.  It is
    deliberately NOT at the cross pivot: the other link of the X carries its
    cross pin there, and two full-width cylinders on the same axis would be a
    head-on interpenetration.  The two links only ever meet at s = a, so any
    other station is clear by 1.6*a*sin(theta) or more.
    """
    x_station = r.arm_a_x if tag == "a" else r.arm_b_x
    _x_cyl(
        part,
        f"arm_tie_tube_{tag}",
        0.008,
        2.0 * (x_station + PLATE_T * 0.5),
        _s_point(tie_s, angle),
        mats["steel"],
    )
    # Slider roller at the free end, riding the host rail / deck underside.
    _x_cyl(
        part,
        f"arm_roller_{tag}",
        ROLLER_R,
        2.0 * (x_station + PLATE_T * 0.5 + 0.004),
        _s_point(roller_s, angle),
        mats["chrome"],
    )


# --- frame style candidates -------------------------------------------------
def _frame_style_slotted_side_plate_build(frame, r: ResolvedConfig, mats: dict[str, str],
                                          y0: float, y1: float) -> None:
    length = y1 - y0
    cy = 0.5 * (y0 + y1)
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * r.rail_x
        # Slotted rail: two flanges plus end webs, so the slot is real.
        for i, dz in enumerate((-0.009, 0.008)):
            frame.visual(
                Box((0.012, length, 0.012 if i == 0 else 0.010)),
                origin=Origin(xyz=(x, cy, RAIL_Z0 + RAIL_FULL_H * 0.5 + dz)),
                material=mats["paint"],
                name=f"frame_style__slotted_side_plate__flange_{side}_{i}", material_class_id="metal.paint_coated",
            )
        for i, dy in enumerate((-length * 0.5 + 0.020, 0.0, length * 0.5 - 0.020)):
            frame.visual(
                Box((0.012, 0.030, RAIL_FULL_H)),
                origin=Origin(xyz=(x, cy + dy, RAIL_Z0 + RAIL_FULL_H * 0.5)),
                material=mats["paint"],
                name=f"frame_style__slotted_side_plate__web_{side}_{i}", material_class_id="metal.paint_coated",
            )


def _frame_style_boxed_channel_build(frame, r: ResolvedConfig, mats: dict[str, str],
                                     y0: float, y1: float) -> None:
    length = y1 - y0
    cy = 0.5 * (y0 + y1)
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * r.rail_x
        frame.visual(
            Box((0.012, length, RAIL_FULL_H)),
            origin=Origin(xyz=(x, cy, RAIL_Z0 + RAIL_FULL_H * 0.5)),
            material=mats["paint"],
            name=f"frame_style__boxed_channel__wall_{side}", material_class_id="metal.paint_coated",
        )
        # Rolled top edge of the pressed box section.
        frame.visual(
            Box((0.022, length, 0.008)),
            origin=Origin(xyz=(x - sx * 0.005, cy, BASE_PLATE_T + RAIL_H - 0.004)),
            material=mats["edge"],
            name=f"frame_style__boxed_channel__rolled_edge_{side}", material_class_id="metal.paint_coated",
        )


def _frame_style_toe_channel_build(frame, r: ResolvedConfig, mats: dict[str, str],
                                   y0: float, y1: float) -> None:
    length = y1 - y0
    cy = 0.5 * (y0 + y1)
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * r.rail_x
        frame.visual(
            Box((0.012, length, RAIL_FULL_H)),
            origin=Origin(xyz=(x, cy, RAIL_Z0 + RAIL_FULL_H * 0.5)),
            material=mats["paint"],
            name=f"frame_style__toe_channel__wall_{side}", material_class_id="metal.paint_coated",
        )
        # Inturned channel lip.
        frame.visual(
            Box((0.020, length, 0.007)),
            origin=Origin(xyz=(x - sx * 0.004, cy, BASE_PLATE_T + 0.0035)),
            material=mats["edge"],
            name=f"frame_style__toe_channel__lip_{side}", material_class_id="metal.paint_coated",
        )
    # Low toe rail reaching out under the load edge.
    frame.visual(
        Box((r.deck_width_m * 0.86, 0.030, 0.009)),
        origin=Origin(xyz=(0.0, y0 - 0.010, 0.0045)),
        material=mats["edge"],
        name="frame_style__toe_channel__toe_rail", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Box((r.deck_width_m * 0.86, 0.030, BASE_PLATE_T)),
        origin=Origin(xyz=(0.0, y0 + 0.008, BASE_PLATE_T * 0.5)),
        material=mats["edge"],
        name="frame_style__toe_channel__toe_web", material_class_id="metal.paint_coated",
    )


_FRAME_BUILDERS = {
    "slotted_side_plate": _frame_style_slotted_side_plate_build,
    "boxed_channel": _frame_style_boxed_channel_build,
    "toe_channel": _frame_style_toe_channel_build,
}


def _pivot_lugs(part, r: ResolvedConfig, mats: dict[str, str], y: float, top_z: float,
                prefix: str) -> None:
    """Two lugs straddling the arm plates, carrying the fixed stage pivot."""
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * (r.arm_a_x + PLATE_T * 0.5 + 0.006)
        part.visual(
            Box((0.010, 0.030, r.pivot_rise + 0.014)),
            origin=Origin(xyz=(x, y, top_z + (r.pivot_rise + 0.014) * 0.5 - 0.014)),
            material=mats["steel"],
            name=f"{prefix}_lug_{side}", material_class_id="metal.steel_bare",
        )


# --- base -------------------------------------------------------------------
def _build_base(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    base = model.part("lift_base", meta={"role": "lift_base"})
    a = r.arm_half_m
    # The base plate is expressed in world coords; the stage-0 fixed pivot is at
    # y = -a, so the deck-local frame convention (0 .. 2a) maps to y - a.
    y0 = -a - 0.02
    y1 = -a + r.deck_len_m - 0.02
    base.visual(
        Box((r.deck_width_m, y1 - y0, BASE_PLATE_T)),
        origin=Origin(xyz=(0.0, 0.5 * (y0 + y1), BASE_PLATE_T * 0.5)),
        material=mats["paint"],
        name="base_floor", material_class_id="metal.paint_coated",
    )
    _FRAME_BUILDERS[r.frame_style](base, r, mats, y0, y1)
    # Cross ties between the rails.  They sit LOW, just above the floor plate,
    # so they stay clear of the band the scissor links sweep (whose lowest
    # point is the roller riding the rail top).
    for i, y in enumerate((y0 + 0.016, y1 - 0.016)):
        _x_cyl(base, f"base_cross_tie_{i}", 0.006, 2.0 * r.rail_x,
               (0.0, y, BASE_PLATE_T + 0.002), mats["steel"])
    _pivot_lugs(base, r, mats, -a, r.base_rail_top_z, "base_pivot")
    return base


# --- deck fitting candidates ------------------------------------------------
def _fitting_radius(r: ResolvedConfig) -> float:
    return min(r.deck_width_m, r.deck_len_m) * 0.22


def _deck_fitting_flat_deck_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    w = r.deck_width_m * 0.96
    d = r.deck_len_m * 0.94
    part.visual(
        Box((w, d, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, 0.005 - MOUNT)),
        material=mats["paint"],
        name="deck_fitting__flat_deck__top_plate", material_class_id="metal.paint_coated",
    )
    for i, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((w, 0.012, 0.010)),
            origin=Origin(xyz=(0.0, sy * (d * 0.5 - 0.006), 0.012 - MOUNT)),
            material=mats["edge"],
            name=f"deck_fitting__flat_deck__lip_{i}", material_class_id="metal.paint_coated",
        )


def _deck_fitting_screw_riser_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    rad = _fitting_radius(r)
    col = 0.050 + r.deck_len_m * 0.10
    stem_r = rad * 0.42
    part.visual(
        Cylinder(radius=stem_r, length=col + MOUNT),
        origin=Origin(xyz=(0.0, 0.0, (col - MOUNT) * 0.5)),
        material=mats["chrome"],
        name="deck_fitting__screw_riser__column", material_class_id="metal.chrome_polished",
    )
    for i in range(6):
        z = col * (0.14 + 0.68 * i / 5.0)
        part.visual(
            _tube(f"riser_thread_{i}", stem_r + 0.0015, stem_r - 0.0015, 0.0, 0.0025, 20),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["chrome"],
            name=f"deck_fitting__screw_riser__thread_{i}", material_class_id="metal.chrome_polished",
        )
    part.visual(
        Box((rad * 1.7, rad * 1.7, 0.014)),
        origin=Origin(xyz=(0.0, 0.0, col * 0.28)),
        material=mats["steel"],
        name="deck_fitting__screw_riser__collar", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=rad, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, col - 0.005)),
        material=mats["dark"],
        name="deck_fitting__screw_riser__saddle_pad", material_class_id="metal.blackened_gunmetal",
    )


def _deck_fitting_vee_cradle_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    width = _fitting_radius(r) * 2.6
    part.visual(
        Box((width, width * 0.72, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.006 - MOUNT)),
        material=mats["steel"],
        name="deck_fitting__vee_cradle__base", material_class_id="metal.steel_bare",
    )
    tilt = 0.55
    cheek = width * 0.40
    half = cheek * 0.5
    dy = half * math.sin(tilt)
    z_c = 0.006 + half * math.cos(tilt)
    top_y = cheek * math.sin(tilt)
    top_z = 0.006 + cheek * math.cos(tilt)
    for i, sy in enumerate((-1.0, 1.0)):
        # Rotating about +x sends the cheek's far end toward -y, so the tilt
        # sign is the opposite of the side: each cheek's lower end lands at the
        # groove root (y=0, inside the base plate) and its top out at sy*top_y.
        part.visual(
            Box((width, 0.010, cheek)),
            origin=Origin(xyz=(0.0, sy * dy, z_c), rpy=(-sy * tilt, 0.0, 0.0)),
            material=mats["steel"],
            name=f"deck_fitting__vee_cradle__cheek_{i}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((width, 0.012, 0.012)),
            origin=Origin(xyz=(0.0, sy * top_y, top_z)),
            material=mats["dark"],
            name=f"deck_fitting__vee_cradle__lip_{i}", material_class_id="metal.blackened_gunmetal",
        )


_FITTING_BUILDERS = {
    "flat_deck": _deck_fitting_flat_deck_build,
    "screw_riser": _deck_fitting_screw_riser_build,
    "vee_cradle": _deck_fitting_vee_cradle_build,
}


# --- drive unit candidates --------------------------------------------------
def _drive_unit_hydraulic_pump_build(part, base, r: ResolvedConfig, mats: dict[str, str]) -> None:
    # Host adaptation: the cylinder and its cradle live on the base, outboard of
    # the rails, so nothing intrudes into the volume the scissor sweeps.
    a = r.arm_half_m
    body_len = r.deck_len_m * 0.34
    # The cradle must REACH BACK onto the frame rail.  Sitting wholly outboard
    # of the floor plate left the whole actuator group as an island on the base.
    cradle_x0 = r.rail_x - 0.006
    cradle_x1 = r.drive_x + 0.013
    base.visual(
        Box((cradle_x1 - cradle_x0, body_len + 0.020, 0.030)),
        origin=Origin(
            xyz=(0.5 * (cradle_x0 + cradle_x1), -a + body_len * 0.5, r.base_rail_top_z - 0.008)
        ),
        material=mats["edge"],
        name="drive_unit__hydraulic_pump__cradle", material_class_id="metal.paint_coated",
    )
    part_free = None  # explicit: the actuator body is host geometry, not a link
    del part_free
    base.visual(
        Cylinder(radius=0.022, length=body_len),
        origin=Origin(
            xyz=(r.drive_x, -a + body_len * 0.5, r.base_rail_top_z + 0.020),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["dark"],
        name="drive_unit__hydraulic_pump__cylinder_body", material_class_id="metal.blackened_gunmetal",
    )
    base.visual(
        Cylinder(radius=0.013, length=body_len * 0.5),
        origin=Origin(
            xyz=(r.drive_x, -a + body_len + body_len * 0.24, r.base_rail_top_z + 0.020),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["chrome"],
        name="drive_unit__hydraulic_pump__cylinder_rod", material_class_id="metal.chrome_polished",
    )
    for side, sy in enumerate((-1.0, 1.0)):
        base.visual(
            Box((CLEVIS_EAR_T, 0.026, 0.038)),
            origin=Origin(
                xyz=(r.drive_x + sy * CLEVIS_HALF, -a + 0.010, r.drive_pivot_z - 0.014)
            ),
            material=mats["dark"],
            name=f"drive_unit__hydraulic_pump__clevis_ear_{side}", material_class_id="metal.blackened_gunmetal",
        )
    # The lever itself: the articulated drive input.
    _x_cyl(part, "drive_unit__hydraulic_pump__pivot_boss", 0.008, CLEVIS_PIN_LEN,
           (0.0, 0.0, 0.0), mats["chrome"])
    bar = r.deck_len_m * 0.52
    ang = math.radians(34.0)
    part.visual(
        Box((0.014, bar, 0.012)),
        origin=Origin(
            xyz=(0.0, -bar * 0.5 * math.cos(ang), bar * 0.5 * math.sin(ang)),
            rpy=(-ang, 0.0, 0.0),
        ),
        material=mats["paint"],
        name="drive_unit__hydraulic_pump__lever_bar", material_class_id="metal.paint_coated",
    )
    grip = bar * 0.32
    part.visual(
        Box((0.024, grip, 0.022)),
        origin=Origin(
            xyz=(
                0.0,
                -(bar - grip * 0.5) * math.cos(ang),
                (bar - grip * 0.5) * math.sin(ang),
            ),
            rpy=(-ang, 0.0, 0.0),
        ),
        material=mats["rubber"],
        name="drive_unit__hydraulic_pump__grip", material_class_id="rubber.smooth_plain",
    )


def _drive_unit_air_over_hydraulic_build(part, base, r: ResolvedConfig, mats: dict[str, str]) -> None:
    a = r.arm_half_m
    body_len = r.deck_len_m * 0.30
    # The cradle must REACH BACK onto the frame rail.  Sitting wholly outboard
    # of the floor plate left the whole actuator group as an island on the base.
    cradle_x0 = r.rail_x - 0.006
    cradle_x1 = r.drive_x + 0.013
    base.visual(
        Box((cradle_x1 - cradle_x0, body_len + 0.020, 0.030)),
        origin=Origin(
            xyz=(0.5 * (cradle_x0 + cradle_x1), -a + body_len * 0.5, r.base_rail_top_z - 0.008)
        ),
        material=mats["edge"],
        name="drive_unit__air_over_hydraulic__cradle", material_class_id="metal.paint_coated",
    )
    base.visual(
        Cylinder(radius=0.022, length=body_len),
        origin=Origin(
            xyz=(r.drive_x, -a + body_len * 0.5, r.base_rail_top_z + 0.020),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["dark"],
        name="drive_unit__air_over_hydraulic__cylinder_body", material_class_id="metal.blackened_gunmetal",
    )
    # Air-assist can with a banded shell and an inlet fitting.
    can_r = 0.026
    can_y = -a + body_len + can_r + 0.010
    base.visual(
        Cylinder(radius=can_r, length=body_len * 0.62),
        origin=Origin(
            xyz=(r.drive_x, can_y, r.base_rail_top_z + 0.020),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["steel"],
        name="drive_unit__air_over_hydraulic__air_can", material_class_id="metal.steel_bare",
    )
    base.visual(
        _tube("air_can_band", can_r + 0.0018, can_r - 0.002, 0.0, 0.010, 24),
        origin=Origin(
            xyz=(r.drive_x, can_y, r.base_rail_top_z + 0.020),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["chrome"],
        name="drive_unit__air_over_hydraulic__air_can_band", material_class_id="metal.chrome_polished",
    )
    base.visual(
        Cylinder(radius=0.008, length=0.024),
        origin=Origin(
            xyz=(r.drive_x, can_y + body_len * 0.30, r.base_rail_top_z + 0.020),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["chrome"],
        name="drive_unit__air_over_hydraulic__air_inlet", material_class_id="metal.chrome_polished",
    )
    for side, sy in enumerate((-1.0, 1.0)):
        base.visual(
            Box((CLEVIS_EAR_T, 0.026, 0.038)),
            origin=Origin(
                xyz=(r.drive_x + sy * CLEVIS_HALF, -a + 0.010, r.drive_pivot_z - 0.014)
            ),
            material=mats["dark"],
            name=f"drive_unit__air_over_hydraulic__clevis_ear_{side}", material_class_id="metal.blackened_gunmetal",
        )
    # Short trigger lever instead of a long hand bar.
    _x_cyl(part, "drive_unit__air_over_hydraulic__pivot_boss", 0.008, CLEVIS_PIN_LEN,
           (0.0, 0.0, 0.0), mats["chrome"])
    bar = r.deck_len_m * 0.24
    ang = math.radians(26.0)
    part.visual(
        Box((0.018, bar, 0.014)),
        origin=Origin(
            xyz=(0.0, -bar * 0.5 * math.cos(ang), bar * 0.5 * math.sin(ang)),
            rpy=(-ang, 0.0, 0.0),
        ),
        material=mats["dark"],
        name="drive_unit__air_over_hydraulic__trigger", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.026, bar * 0.34, 0.022)),
        origin=Origin(
            xyz=(
                0.0,
                -(bar - bar * 0.17) * math.cos(ang),
                (bar - bar * 0.17) * math.sin(ang),
            ),
            rpy=(-ang, 0.0, 0.0),
        ),
        material=mats["rubber"],
        name="drive_unit__air_over_hydraulic__trigger_boot", material_class_id="rubber.smooth_plain",
    )


_DRIVE_BUILDERS = {
    "hydraulic_pump": _drive_unit_hydraulic_pump_build,
    "air_over_hydraulic": _drive_unit_air_over_hydraulic_build,
}


# --- scissor stages ---------------------------------------------------------
def _build_stages(model: ArticulatedObject, base, r: ResolvedConfig, mats: dict[str, str]):
    a = r.arm_half_m
    builder = _ARM_BUILDERS[r.arm_style]
    host = base
    host_rail_top = r.base_rail_top_z
    host_pivot_y = -a  # world y of stage 0's fixed pivot
    top_deck = None
    for stage in range(r.scissor_stage_count):
        driver = f"stage_{stage}_scissor_drive"

        arm_a = model.part(
            f"arm_style__{r.arm_style}__stage_{stage}_arm_a",
            meta={"role": "scissor_arm", "stage": stage, "link": "a"},
        )
        builder(arm_a, r, mats, half=a, angle=THETA0, tag="a", centre_s=a)
        _add_arm_common(arm_a, r, mats, half=a, angle=THETA0, tag="a",
                        tie_s=1.8 * a, roller_s=2.0 * a)
        # Pivot pin on the joint axis, journalled into the host's lugs.
        _x_cyl(arm_a, "arm_a_pivot_pin", 0.009, 2.0 * (r.arm_a_x + 0.0066), (0.0, 0.0, 0.0),
               mats["chrome"])
        _rev_axis_joint(
            model,
            name=driver,
            parent=host,
            child=arm_a,
            point=(0.0, host_pivot_y, host_rail_top + r.pivot_rise),
            axis=(1.0, 0.0, 0.0),
            provider_radial=(0.0, 1.0, 0.0),
            consumer_radial=(0.0, 1.0, 0.0),
            lower=0.0,
            upper=r.stage_travel_rad,
            effort=16000.0,
            velocity=0.30,
        )

        arm_b = model.part(
            f"arm_style__{r.arm_style}__stage_{stage}_arm_b",
            meta={"role": "scissor_arm", "stage": stage, "link": "b"},
        )
        # arm_b is authored at -THETA0 and centred on the cross pivot, so with a
        # mimic of -2q its global angle is exactly -(THETA0 + q).
        # arm_b's origin IS the cross pivot, in the middle of the link, so the
        # body runs s in [-a, +a]: the -a end is the upper deck pin and the +a
        # end is the lower roller sliding on the host rail.
        builder(arm_b, r, mats, half=a, angle=-THETA0, tag="b", centre_s=0.0)
        _add_arm_common(arm_b, r, mats, half=a, angle=-THETA0, tag="b",
                        tie_s=-0.6 * a, roller_s=a)
        # The cross pin journals MOUNT past arm_a's INNER plate face.  Running it
        # to the outer face instead drove a 0.009 m pin straight through a
        # 0.010 m plate -- a real 10 mm interpenetration, not a bearing fit.
        _x_cyl(
            arm_b,
            "arm_b_cross_pin",
            0.009,
            2.0 * (r.arm_a_x - PLATE_T * 0.5 + MOUNT),
            (0.0, 0.0, 0.0),
            mats["chrome"],
        )
        # Upper pin on the deck-levelling axis, journalled into the deck lugs.
        _x_cyl(
            arm_b,
            "arm_b_deck_pin",
            0.009,
            2.0 * (r.arm_b_x + 0.0066),
            _s_point(-a, -THETA0),
            mats["chrome"],
        )
        _rev_axis_joint(
            model,
            name=f"stage_{stage}_cross_pivot",
            parent=arm_a,
            child=arm_b,
            point=(0.0, a * math.cos(THETA0), a * math.sin(THETA0)),
            axis=(1.0, 0.0, 0.0),
            provider_radial=(0.0, 1.0, 0.0),
            consumer_radial=(0.0, 1.0, 0.0),
            lower=-2.0 * r.stage_travel_rad,
            upper=0.0,
            effort=16000.0,
            velocity=0.60,
            mimic=Mimic(joint=driver, multiplier=-2.0),
        )

        deck = model.part(
            f"lift_deck_{stage}",
            meta={"role": "lift_deck", "stage": stage},
        )
        _build_deck(deck, r, mats, stage=stage,
                    hosts_next_stage=stage < r.scissor_stage_count - 1)
        _rev_axis_joint(
            model,
            name=f"stage_{stage}_deck_level",
            parent=arm_b,
            child=deck,
            # arm_b's upper pin: the -a end of a link authored at -THETA0.
            point=(0.0, -a * math.cos(THETA0), a * math.sin(THETA0)),
            axis=(1.0, 0.0, 0.0),
            provider_radial=(0.0, 1.0, 0.0),
            consumer_radial=(0.0, 1.0, 0.0),
            lower=0.0,
            upper=r.stage_travel_rad,
            effort=16000.0,
            velocity=0.30,
            mimic=Mimic(joint=driver, multiplier=1.0),
        )

        host = deck
        host_rail_top = r.deck_top_local_z
        host_pivot_y = 0.0  # deck-local y of the next stage's fixed pivot
        top_deck = deck
    return top_deck


def _build_deck(deck, r: ResolvedConfig, mats: dict[str, str], *, stage: int,
                hosts_next_stage: bool) -> None:
    """A level deck plate spanning the whole slider run, on its own rails."""
    a = r.arm_half_m
    z_bottom = ROLLER_R - RUN_GAP
    cy = r.deck_centre_y
    deck.visual(
        Box((r.deck_width_m, r.deck_len_m, DECK_T)),
        origin=Origin(xyz=(0.0, cy, z_bottom + DECK_T * 0.5)),
        material=mats["paint"],
        name=f"deck_plate_{stage}", material_class_id="metal.paint_coated",
    )
    # Pin bracket down onto arm_b's upper pin at deck-local origin, so the deck
    # is genuinely carried there instead of floating above the link.
    for side, sx in enumerate((-1.0, 1.0)):
        deck.visual(
            Box((0.010, 0.030, z_bottom + 0.004)),
            origin=Origin(
                xyz=(sx * (r.arm_b_x + PLATE_T * 0.5 + 0.006), 0.0, (z_bottom + 0.004) * 0.5 - 0.004)
            ),
            material=mats["steel"],
            name=f"deck_pin_lug_{stage}_{side}", material_class_id="metal.steel_bare",
        )
    # Guide rails on the underside for the sliding roller of arm_a.
    for side, sx in enumerate((-1.0, 1.0)):
        deck.visual(
            Box((0.010, r.deck_len_m * 0.92, 0.008)),
            origin=Origin(xyz=(sx * (r.arm_a_x + PLATE_T * 0.5 + 0.007), cy, z_bottom - 0.004 + MOUNT)),
            material=mats["edge"],
            name=f"deck_guide_rail_{stage}_{side}", material_class_id="metal.paint_coated",
        )
    # Rails and pivot lugs on the TOP face -- but ONLY on a deck that actually
    # carries another stage.  The topmost deck carries the deck_fitting instead,
    # and leaving hardware up there would have the fitting sitting inside it.
    if hosts_next_stage:
        for side, sx in enumerate((-1.0, 1.0)):
            deck.visual(
                Box((0.012, r.deck_len_m * 0.92, RAIL_H * 0.5)),
                origin=Origin(
                    xyz=(sx * r.rail_x, cy, z_bottom + DECK_T + RAIL_H * 0.25 - MOUNT)
                ),
                material=mats["edge"],
                name=f"deck_top_rail_{stage}_{side}", material_class_id="metal.paint_coated",
            )
        _pivot_lugs(deck, r, mats, 0.0, r.deck_top_local_z, f"deck_pivot_{stage}")


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_hydraulic_jack(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_hydraulic_jack",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "crossed scissor lift, one independent driver per stage",
        },
    )
    mats = _materials(model, r)
    base = _build_base(model, r, mats)
    top_deck = _build_stages(model, base, r, mats)

    fitting = model.part(
        f"deck_fitting__{r.deck_fitting}__fitting",
        meta={"role": "deck_fitting"},
    )
    _FITTING_BUILDERS[r.deck_fitting](fitting, r, mats)
    fitting_z = r.deck_top_local_z
    if r.deck_fitting == "screw_riser":
        _rev_axis_joint(
            model,
            name="deck_to_fitting",
            parent=top_deck,
            child=fitting,
            point=(0.0, r.deck_centre_y, fitting_z),
            axis=(0.0, 0.0, 1.0),
            provider_radial=(1.0, 0.0, 0.0),
            consumer_radial=(1.0, 0.0, 0.0),
            lower=-math.pi,
            upper=math.pi,
            effort=60.0,
            velocity=2.0,
        )
    else:
        model.articulation(
            "deck_to_fitting",
            ArticulationType.FIXED,
            parent=top_deck,
            child=fitting,
            origin=Origin(xyz=(0.0, r.deck_centre_y, fitting_z)),
        )

    drive = model.part(
        f"drive_unit__{r.drive_unit}__lever",
        meta={"role": "drive_input"},
    )
    _DRIVE_BUILDERS[r.drive_unit](drive, base, r, mats)
    _rev_axis_joint(
        model,
        name="base_to_drive_input",
        parent=base,
        child=drive,
        point=(r.drive_x, -r.arm_half_m + 0.010, r.drive_pivot_z),
        # The lever pin runs ALONG x (that is the pin the clevis ears straddle),
        # so the lever swings fore-and-aft in the y-z plane and never moves in x
        # -- it stays outboard of the rails at every pose.
        axis=(1.0, 0.0, 0.0),
        provider_radial=(0.0, 1.0, 0.0),
        consumer_radial=(0.0, 1.0, 0.0),
        lower=-0.30,
        upper=0.30,
        effort=300.0,
        velocity=2.0,
    )

    drivers = [f"stage_{i}_scissor_drive" for i in range(r.scissor_stage_count)]
    model.meta["risk_poses"] = (
        {name: 0.0 for name in drivers} | {"base_to_drive_input": 0.0},
        {name: r.stage_travel_rad for name in drivers} | {"base_to_drive_input": 0.30},
        {name: r.stage_travel_rad for name in drivers} | {"base_to_drive_input": -0.30},
        # Mixed stages: the tallest stage fully up while the one under it is
        # fully down is the real stacking risk.
        {name: (r.stage_travel_rad if i % 2 else 0.0) for i, name in enumerate(drivers)},
    )
    model.meta["coupled_joint_pairs"] = tuple(
        (drivers[i], drivers[i + 1]) for i in range(len(drivers) - 1)
    ) + ((drivers[0], "base_to_drive_input"),)
    return model


def build_seeded_picturex_0611_hydraulic_jack(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_hydraulic_jack(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_hydraulic_jack_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    bases = _parts_by_role(model, "lift_base")
    arms = _parts_by_role(model, "scissor_arm")
    decks = _parts_by_role(model, "lift_deck")
    fittings = _parts_by_role(model, "deck_fitting")
    drives = _parts_by_role(model, "drive_input")

    joints = {j.name: j for j in model.articulations}
    drivers = [joints.get(f"stage_{i}_scissor_drive") for i in range(r.scissor_stage_count)]
    crosses = [joints.get(f"stage_{i}_cross_pivot") for i in range(r.scissor_stage_count)]
    levels = [joints.get(f"stage_{i}_deck_level") for i in range(r.scissor_stage_count)]
    drive_joint = joints.get("base_to_drive_input")

    def _is_rev_x(j) -> bool:
        return (
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(abs(v), 6) for v in j.axis) == (1.0, 0.0, 0.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    # Every stage is a real X: an independent driver, a cross pivot mimicking it
    # at -2, and a deck-levelling joint mimicking it at +1.
    mimics_ok = all(
        crosses[i] is not None
        and levels[i] is not None
        and getattr(crosses[i].mimic, "joint", None) == f"stage_{i}_scissor_drive"
        and abs(float(crosses[i].mimic.multiplier) + 2.0) < 1e-9
        and getattr(levels[i].mimic, "joint", None) == f"stage_{i}_scissor_drive"
        and abs(float(levels[i].mimic.multiplier) - 1.0) < 1e-9
        and getattr(drivers[i], "mimic", None) is None
        for i in range(r.scissor_stage_count)
    )
    ctx.check(
        "category_anchor: crossed scissor lift mechanism",
        len(bases) == 1
        and len(arms) == 2 * r.scissor_stage_count
        and len(decks) == r.scissor_stage_count
        and len(fittings) == 1
        and len(drives) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "lift_base"
        and all(_is_rev_x(j) for j in drivers)
        and all(_is_rev_x(j) for j in crosses)
        and all(_is_rev_x(j) for j in levels)
        and drivers[0].parent == "lift_base"
        and mimics_ok,
        details=(
            f"bases={len(bases)} arms={len(arms)} decks={len(decks)} "
            f"fittings={len(fittings)} drives={len(drives)} mimics_ok={mimics_ok}"
        ),
    )

    # The scissor must actually lift, and the deck must stay level and at a
    # fixed y while it does -- that is the whole point of the -2/+1 mimics.
    top_deck = decks[-1]
    rest = ctx.part_element_world_aabb(top_deck, elem=f"deck_plate_{r.scissor_stage_count - 1}")
    top_pose = {j: j.motion_limits.upper for j in drivers}
    with ctx.pose(top_pose):
        raised = ctx.part_element_world_aabb(top_deck, elem=f"deck_plate_{r.scissor_stage_count - 1}")
    expected = r.stage_lift_m * r.scissor_stage_count
    level_ok = (
        rest is not None
        and raised is not None
        and abs((raised[1][2] - raised[0][2]) - (rest[1][2] - rest[0][2])) < 1e-4
        and abs(raised[0][1] - rest[0][1]) < 1e-4
        and abs(raised[1][1] - rest[1][1]) < 1e-4
    )
    ctx.check(
        "category_anchor: platform rises level and parallel to the base",
        level_ok and abs((raised[0][2] - rest[0][2]) - expected) < 2e-3,
        details=f"rest={rest} raised={raised} expected_lift={expected} level_ok={level_ok}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    arm_ok = {
        "slotted_plate_arm": any("slotted_plate_arm__web" in n for n in visual_names),
        "boxed_bar_arm": any("boxed_bar_arm__end_boss" in n for n in visual_names),
    }[r.arm_style]
    ctx.check("category_anchor: arm_style identity", arm_ok, details=f"arm_style={r.arm_style}")

    frame_ok = {
        "slotted_side_plate": any("slotted_side_plate__web" in n for n in visual_names),
        "boxed_channel": any("boxed_channel__rolled_edge" in n for n in visual_names),
        "toe_channel": any("toe_channel__toe_rail" in n for n in visual_names),
    }[r.frame_style]
    ctx.check("category_anchor: frame_style identity", frame_ok, details=f"frame_style={r.frame_style}")

    fit_ok = {
        "flat_deck": any("flat_deck__lip" in n for n in visual_names),
        "screw_riser": any("screw_riser__thread" in n for n in visual_names),
        "vee_cradle": any("vee_cradle__cheek" in n for n in visual_names),
    }[r.deck_fitting]
    ctx.check("category_anchor: deck_fitting identity", fit_ok, details=f"deck_fitting={r.deck_fitting}")

    drive_ok = {
        "hydraulic_pump": any("hydraulic_pump__grip" in n for n in visual_names),
        "air_over_hydraulic": any("air_over_hydraulic__air_can" in n for n in visual_names),
    }[r.drive_unit]
    ctx.check("category_anchor: drive_unit identity", drive_ok, details=f"drive_unit={r.drive_unit}")

    rest_d = ctx.part_world_aabb(drives[0])
    with ctx.pose({drive_joint: drive_joint.motion_limits.upper}):
        up_d = ctx.part_world_aabb(drives[0])
    with ctx.pose({drive_joint: drive_joint.motion_limits.lower}):
        down_d = ctx.part_world_aabb(drives[0])
    ctx.check(
        "drive lever swings through a real arc outboard of the rails",
        all(b is not None for b in (rest_d, up_d, down_d))
        and abs(up_d[1][2] - down_d[1][2]) > 0.005
        and min(up_d[0][0], down_d[0][0], rest_d[0][0]) > r.rail_x,
        details=f"rest={rest_d} up={up_d} down={down_d}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_deck_single_stage_flat",
        {
            "arm_style": "boxed_bar_arm",
            "frame_style": "boxed_channel",
            "deck_fitting": "flat_deck",
            "drive_unit": "hydraulic_pump",
            "scissor_stage_count": 1,
            "deck_len_m": 0.30,
            "deck_width_m": 0.22,
            "arm_span_ratio": 0.72,
        },
        reason="smallest deck and narrowest width with the shortest arms — tightest link nesting",
    ),
    corner_case(
        "max_deck_triple_stage_riser",
        {
            "arm_style": "slotted_plate_arm",
            "frame_style": "toe_channel",
            "deck_fitting": "screw_riser",
            "drive_unit": "air_over_hydraulic",
            "scissor_stage_count": 3,
            "deck_len_m": 0.60,
            "deck_width_m": 0.42,
            "arm_span_ratio": 0.90,
            },
        reason="maximum envelope, three stacked stages plus the screw riser — tallest reach",
    ),
    corner_case(
        "long_arm_short_deck_cradle",
        {
            "arm_style": "slotted_plate_arm",
            "frame_style": "slotted_side_plate",
            "deck_fitting": "vee_cradle",
            "drive_unit": "hydraulic_pump",
            "scissor_stage_count": 2,
            "deck_len_m": 0.30,
            "deck_width_m": 0.42,
            "arm_span_ratio": 0.90,
        },
        reason="longest arms relative to the deck — the slider run only just fits the deck",
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
    "build_picturex_0611_hydraulic_jack",
    "build_seeded_picturex_0611_hydraulic_jack",
    "run_picturex_0611_hydraulic_jack_tests",
]
