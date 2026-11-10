# SPDX-License-Identifier: Apache-2.0

"""Self-contained pull-out (sleeper) sofa bed template.

One rigid ``sofa_frame`` root carries the upholstered carcass, the fixed arms,
the apron and the carriage guides; a fixed ``seat_deck`` is the rear bed
section.  The ``backrest`` is a REVOLUTE (+x) child of the frame.  The
``pullout_deck`` is a PRISMATIC (+y) child of the frame running in those guides,
and two ``mattress_leaf`` panels ride it: leaf 0 hinges on the carriage and
leaf 1 hinges on leaf 0, both REVOLUTE about +x so they fold UP and back over
the carriage instead of down through the seat.  ``bed_leg_count`` fold-down
``bed_leg`` supports hinge under leaf 1 and reach the floor when the bed is made.

The geometry is laid out so that every INDEPENDENT single-joint pose is clear,
not just the two showroom configurations: the retracted carriage still parks its
leaf hinge well in front of the fixed seat, so a leaf laid flat while the
carriage is in never reaches the seat, and a leaf folded up passes between the
arms and finishes above the backrest.

Four component slots vary without touching the mechanism: ``back_style``,
``deck_frame``, ``mattress_build`` and ``bed_leg``.  No source-replay import, no
motion clamping, no whole-part overlap allowance.
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
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    multiplicity_slot,
    register_interface_mate,
)

BackStyle = Literal["plain_pad", "clickclack_ratchet", "slatted_fold_back"]
DeckFrame = Literal["sleeve_rail", "nested_rail", "slatted_frame"]
MattressBuild = Literal["slatted_panel", "tufted_panel"]
BedLeg = Literal["u_leg", "twin_post"]
PaletteStyle = Literal["pale_gray", "navy_linen", "camel_leather", "sage_weave"]

BACK_STYLES: tuple[BackStyle, ...] = ("plain_pad", "clickclack_ratchet", "slatted_fold_back")
DECK_FRAMES: tuple[DeckFrame, ...] = ("sleeve_rail", "nested_rail", "slatted_frame")
MATTRESS_BUILDS: tuple[MattressBuild, ...] = ("slatted_panel", "tufted_panel")
BED_LEGS: tuple[BedLeg, ...] = ("u_leg", "twin_post")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("pale_gray", "navy_linen", "camel_leather", "sage_weave")


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("back_style", BACK_STYLES),
        component_slot("deck_frame", DECK_FRAMES),
        component_slot("mattress_build", MATTRESS_BUILDS),
        component_slot("bed_leg", BED_LEGS),
        multiplicity_slot("bed_leg_count", (2, 3, 4), item_slot="bed_leg"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "pale_gray": {
        "upholstery": (0.73, 0.75, 0.77, 1.0),
        "shadow": (0.60, 0.62, 0.64, 1.0),
        "mattress": (0.94, 0.95, 0.95, 1.0),
        "steel": (0.19, 0.21, 0.22, 1.0),
        "zinc": (0.62, 0.65, 0.67, 1.0),
        "foot": (0.06, 0.06, 0.07, 1.0),
    },
    "navy_linen": {
        "upholstery": (0.17, 0.22, 0.34, 1.0),
        "shadow": (0.11, 0.15, 0.24, 1.0),
        "mattress": (0.92, 0.93, 0.94, 1.0),
        "steel": (0.22, 0.24, 0.28, 1.0),
        "zinc": (0.58, 0.61, 0.65, 1.0),
        "foot": (0.05, 0.05, 0.06, 1.0),
    },
    "camel_leather": {
        "upholstery": (0.63, 0.44, 0.26, 1.0),
        "shadow": (0.47, 0.31, 0.17, 1.0),
        "mattress": (0.95, 0.94, 0.90, 1.0),
        "steel": (0.26, 0.24, 0.22, 1.0),
        "zinc": (0.66, 0.60, 0.48, 1.0),
        "foot": (0.07, 0.06, 0.05, 1.0),
    },
    "sage_weave": {
        "upholstery": (0.56, 0.61, 0.50, 1.0),
        "shadow": (0.41, 0.46, 0.36, 1.0),
        "mattress": (0.93, 0.94, 0.92, 1.0),
        "steel": (0.24, 0.27, 0.24, 1.0),
        "zinc": (0.61, 0.64, 0.60, 1.0),
        "foot": (0.05, 0.05, 0.05, 1.0),
    },
}


ARM_W = 0.16             # upholstered arm width per side
LEAF_T = 0.055           # mattress leaf thickness
SEAT_RUN = 0.26          # fixed rear bed section depth
# The retracted carriage parks its leaf hinge this far in FRONT of the fixed
# seat, so a leaf laid flat with the carriage in cannot reach the seat at all.
SEAT_STANDOFF = 0.12
RAIL_H = 0.040
# The carriage joint origin sits on its rail, DECK_RAIL_DROP below the leaf
# hinge line.  Everything the carriage owns is therefore authored in
# carriage-local z (0 at that rail), not in world z.
DECK_RAIL_DROP = 0.060
RAIL_TAIL = 0.20         # rail length behind the travel, so the guide stays engaged
LEG_BRACKET_X = 0.070    # leg receiver bracket centre offset
LEG_BRACKET_T = 0.012
# Each leaf's body starts LEAF_GAP past its own hinge and the next leaf's
# hinge sits LEAF_GAP beyond this leaf's far edge, so neither hinge barrel is
# buried in a leaf body -- that is the real seam of a hinged mattress.
LEAF_GAP = 0.022
HINGE_R = 0.016
KNUCKLE_R = 0.018
KNUCKLE_LEN = 0.040
# A leaf folded to vertical sweeps its own half-thickness back past its
# hinge, so the next hinge has to stand off by more than that or the two
# leaves interpenetrate at the fold.
HINGE_OFFSET = LEAF_T * 0.5 + 0.005
# Sub-millimetre lap: a fitting laps its host by less than the collision
# tolerance so QC reads real contact without an overlap allowance.
MOUNT = 0.0006
# The leg pivot journals MOUNT past each receiver's inner face.
LEG_PIVOT_LEN = 2.0 * (LEG_BRACKET_X - LEG_BRACKET_T * 0.5 + MOUNT)


@dataclass(frozen=True)
class Config:
    back_style: BackStyle = "plain_pad"
    deck_frame: DeckFrame = "sleeve_rail"
    mattress_build: MattressBuild = "slatted_panel"
    bed_leg: BedLeg = "u_leg"
    bed_leg_count: int = 2
    width_m: float | None = None
    seat_depth_m: float | None = None
    bed_height_m: float | None = None
    palette_style: PaletteStyle = "pale_gray"
    name: str = "pictureX_0611_Folding_sofa_bed1"


@dataclass(frozen=True)
class ResolvedConfig:
    back_style: BackStyle
    deck_frame: DeckFrame
    mattress_build: MattressBuild
    bed_leg: BedLeg
    bed_leg_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    width_m: float
    seat_depth_m: float
    bed_height_m: float
    seat_width_m: float
    leaf_width_m: float
    leaf_len_m: float
    seat_y0: float
    seat_y1: float
    deck_front_y: float
    deck_travel_m: float
    hinge_z: float
    back_hinge_y: float
    back_len_m: float
    leg_len_m: float
    leg_x: tuple[float, ...]
    leg_local_y: float
    rail_x: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x50FA_0BE1)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        back_style=choices["back_style"],
        deck_frame=choices["deck_frame"],
        mattress_build=choices["mattress_build"],
        bed_leg=choices["bed_leg"],
        bed_leg_count=choices["bed_leg_count"],
        width_m=round(rng.uniform(1.60, 2.10), 4),
        seat_depth_m=round(rng.uniform(0.52, 0.68), 4),
        bed_height_m=round(rng.uniform(0.38, 0.46), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"folding_sofa_bed1_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "back_style": config.back_style,
            "deck_frame": config.deck_frame,
            "mattress_build": config.mattress_build,
            "bed_leg": config.bed_leg,
            "bed_leg_count": config.bed_leg_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.width_m is not None and not 1.60 <= float(config.width_m) <= 2.10:
        raise ValueError("width_m must be in [1.60, 2.10]")
    if config.seat_depth_m is not None and not 0.52 <= float(config.seat_depth_m) <= 0.68:
        raise ValueError("seat_depth_m must be in [0.52, 0.68]")
    if config.bed_height_m is not None and not 0.38 <= float(config.bed_height_m) <= 0.46:
        raise ValueError("bed_height_m must be in [0.38, 0.46]")

    width = _clamp(config.width_m, 1.60, 2.10) if config.width_m is not None else 1.90
    depth = _clamp(config.seat_depth_m, 0.52, 0.68) if config.seat_depth_m is not None else 0.60
    height = _clamp(config.bed_height_m, 0.38, 0.46) if config.bed_height_m is not None else 0.42

    seat_width = width - 2.0 * ARM_W
    leaf_width = seat_width * 0.96
    leaf_len = depth * 0.92
    seat_y0 = -depth + 0.060
    seat_y1 = seat_y0 + SEAT_RUN
    deck_front = seat_y1 + SEAT_STANDOFF
    travel = depth * 0.28
    hinge_z = height - LEAF_T * 0.5
    back_hinge_y = -depth + 0.020
    back_len = min(0.45, depth * 0.75)
    # Pivot sits LEAF_T/2 + 0.020 under the leaf mid-plane, which is itself
    # LEAF_T/2 under the bed surface, so this is what actually reaches the floor.
    leg_len = height - LEAF_T - 0.032

    n = int(config.bed_leg_count)
    span = leaf_width * 0.74
    if n == 1:
        legs = (0.0,)
    else:
        legs = tuple(-span * 0.5 + span * i / (n - 1) for i in range(n))
    leg_local_y = leaf_len * 0.80
    rail_x = seat_width * 0.5 - 0.09

    return ResolvedConfig(
        back_style=config.back_style,
        deck_frame=config.deck_frame,
        mattress_build=config.mattress_build,
        bed_leg=config.bed_leg,
        bed_leg_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        width_m=width,
        seat_depth_m=depth,
        bed_height_m=height,
        seat_width_m=seat_width,
        leaf_width_m=leaf_width,
        leaf_len_m=leaf_len,
        seat_y0=seat_y0,
        seat_y1=seat_y1,
        deck_front_y=deck_front,
        deck_travel_m=travel,
        hinge_z=hinge_z,
        back_hinge_y=back_hinge_y,
        back_len_m=back_len,
        leg_len_m=leg_len,
        leg_x=legs,
        leg_local_y=leg_local_y,
        rail_x=rail_x,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("back_style", config.back_style),
        ("deck_frame", config.deck_frame),
        ("mattress_build", config.mattress_build),
        ("bed_leg", config.bed_leg),
        ("bed_leg_count", config.bed_leg_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"sb1_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"sb1_{r.palette_style}_{key}"
    return mats


def _x_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.steel_galvanized",
    )


def _rev_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
) -> None:
    provider = AxisInterface(
        name=f"{name}__provider", point=point, axis=(1.0, 0.0, 0.0), radial=(0.0, 0.0, 1.0)
    )
    consumer = AxisInterface(name=f"{name}__consumer", axis=(1.0, 0.0, 0.0), radial=(0.0, 0.0, 1.0))
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(lower=lower, upper=upper, effort=effort, velocity=velocity),
    )
    register_interface_mate(model, name, mate)


# --- mattress leaf candidates ----------------------------------------------
def _mattress_build_slatted_panel_build(part, r: ResolvedConfig, mats: dict[str, str],
                                        index: int) -> None:
    """Steel frame with a regular rhythm of transverse slats under the pad."""
    w = r.leaf_width_m
    d = r.leaf_len_m
    cy = 0.5 * (LEAF_GAP + d)
    run = d - LEAF_GAP
    frame_t = 0.018
    for side, sx in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.030, run, frame_t)),
            origin=Origin(xyz=(sx * (w * 0.5 - 0.015), cy, -LEAF_T * 0.5 + frame_t * 0.5)),
            material=mats["steel"],
            name=f"mattress_build__slatted_panel__side_rail_{index}_{side}", material_class_id="metal.steel_bare",
        )
    for e, y in enumerate((LEAF_GAP + 0.016, d - 0.016)):
        part.visual(
            Box((w, 0.028, frame_t)),
            origin=Origin(xyz=(0.0, y, -LEAF_T * 0.5 + frame_t * 0.5)),
            material=mats["steel"],
            name=f"mattress_build__slatted_panel__end_rail_{index}_{e}", material_class_id="metal.steel_bare",
        )
    slats = 5
    for i in range(slats):
        y = LEAF_GAP + 0.04 + (run - 0.08) * i / (slats - 1)
        part.visual(
            Box((w * 0.97, 0.026, 0.014)),
            origin=Origin(xyz=(0.0, y, -LEAF_T * 0.5 + frame_t - 0.006)),
            material=mats["steel"],
            name=f"mattress_build__slatted_panel__slat_{index}_{i}", material_class_id="metal.steel_bare",
        )
    part.visual(
        Box((w * 0.98, run - 0.010, LEAF_T - frame_t + 0.004)),
        origin=Origin(xyz=(0.0, cy, LEAF_T * 0.5 - (LEAF_T - frame_t + 0.004) * 0.5)),
        material=mats["mattress"],
        name=f"mattress_build__slatted_panel__pad_{index}", material_class_id="fabric.plain_flat_weave",
    )


def _mattress_build_tufted_panel_build(part, r: ResolvedConfig, mats: dict[str, str],
                                       index: int) -> None:
    """Upholstered cushion panel with seams and buttons, no exposed slats."""
    w = r.leaf_width_m
    d = r.leaf_len_m
    cy = 0.5 * (LEAF_GAP + d)
    run = d - LEAF_GAP
    deck_t = 0.016
    part.visual(
        Box((w, run, deck_t)),
        origin=Origin(xyz=(0.0, cy, -LEAF_T * 0.5 + deck_t * 0.5)),
        material=mats["shadow"],
        name=f"mattress_build__tufted_panel__deck_{index}", material_class_id="fabric.plain_flat_weave",
    )
    part.visual(
        Box((w * 0.99, run - 0.008, LEAF_T - deck_t + 0.004)),
        origin=Origin(xyz=(0.0, cy, LEAF_T * 0.5 - (LEAF_T - deck_t + 0.004) * 0.5)),
        material=mats["upholstery"],
        name=f"mattress_build__tufted_panel__cushion_{index}", material_class_id=("leather.quilted_upholstery" if r.palette_style == "camel_leather" else "fabric.quilted_pleated"),
    )
    for i, fx in enumerate((-w / 6.0, w / 6.0)):
        part.visual(
            Box((0.012, run * 0.86, 0.010)),
            origin=Origin(xyz=(fx, cy, LEAF_T * 0.5 - 0.004)),
            material=mats["shadow"],
            name=f"mattress_build__tufted_panel__seam_{index}_{i}", material_class_id=("leather.quilted_upholstery" if r.palette_style == "camel_leather" else "fabric.quilted_pleated"),
        )
    for row, dy in enumerate((-run * 0.24, run * 0.24)):
        for col, bx in enumerate((-w * 0.28, 0.0, w * 0.28)):
            part.visual(
                Cylinder(radius=0.013, length=0.010),
                origin=Origin(xyz=(bx, cy + dy, LEAF_T * 0.5 - 0.003)),
                material=mats["shadow"],
                name=f"mattress_build__tufted_panel__button_{index}_{row}_{col}", material_class_id=("leather.quilted_upholstery" if r.palette_style == "camel_leather" else "fabric.quilted_pleated"),
            )


_LEAF_BUILDERS = {
    "slatted_panel": _mattress_build_slatted_panel_build,
    "tufted_panel": _mattress_build_tufted_panel_build,
}


# --- bed leg candidates -----------------------------------------------------
def _bed_leg_u_leg_build(leg, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    length = r.leg_len_m
    span = 0.11
    for side, sx in enumerate((-1.0, 1.0)):
        leg.visual(
            Box((0.026, length, 0.026)),
            origin=Origin(xyz=(sx * span * 0.5, -length * 0.5, 0.0)),
            material=mats["steel"],
            name=f"bed_leg__u_leg__post_{index}_{side}", material_class_id="metal.steel_bare",
        )
        leg.visual(
            Box((0.032, 0.016, 0.034)),
            origin=Origin(xyz=(sx * span * 0.5, -length + 0.006, 0.0)),
            material=mats["foot"],
            name=f"bed_leg__u_leg__foot_pad_{index}_{side}", material_class_id="rubber.smooth_plain",
        )
    # The U bend tying both posts, which is what makes it a U leg.
    leg.visual(
        Box((span + 0.026, 0.026, 0.026)),
        origin=Origin(xyz=(0.0, -length + 0.020, 0.0)),
        material=mats["steel"],
        name=f"bed_leg__u_leg__bend_{index}", material_class_id="metal.steel_bare",
    )
    _x_cyl(leg, f"bed_leg__u_leg__pivot_{index}", 0.011, LEG_PIVOT_LEN, (0.0, 0.0, 0.0),
           mats["zinc"])


def _bed_leg_twin_post_build(leg, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    length = r.leg_len_m
    span = 0.09
    for side, sx in enumerate((-1.0, 1.0)):
        leg.visual(
            Box((0.030, length, 0.030)),
            origin=Origin(xyz=(sx * span * 0.5, -length * 0.5, 0.0)),
            material=mats["steel"],
            name=f"bed_leg__twin_post__post_{index}_{side}", material_class_id="metal.steel_bare",
        )
        leg.visual(
            Cylinder(radius=0.020, length=0.014),
            origin=Origin(
                xyz=(sx * span * 0.5, -length + 0.005, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=mats["foot"],
            name=f"bed_leg__twin_post__glide_{index}_{side}", material_class_id="rubber.smooth_plain",
        )
    # Tie bar partway down, the twin-post leg's identifying brace.
    leg.visual(
        Box((span + 0.030, 0.020, 0.020)),
        origin=Origin(xyz=(0.0, -length * 0.62, 0.0)),
        material=mats["zinc"],
        name=f"bed_leg__twin_post__tie_bar_{index}", material_class_id="metal.steel_galvanized",
    )
    _x_cyl(leg, f"bed_leg__twin_post__pivot_{index}", 0.011, LEG_PIVOT_LEN, (0.0, 0.0, 0.0),
           mats["zinc"])


_LEG_BUILDERS = {
    "u_leg": _bed_leg_u_leg_build,
    "twin_post": _bed_leg_twin_post_build,
}


# --- deck frame candidates --------------------------------------------------
def _deck_frame_sleeve_rail_build(deck, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Square guide sleeves in the apron, with the carriage rails inside them."""
    reach = r.deck_travel_m + RAIL_TAIL
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * r.rail_x
        deck.visual(
            Box((0.026, reach, 0.026)),
            origin=Origin(xyz=(x, r.deck_front_y - reach * 0.5, 0.0)),
            material=mats["steel"],
            name=f"deck_frame__sleeve_rail__inner_rail_{side}", material_class_id="metal.steel_bare",
        )
        _guide_channel(
            frame, mats, x=x, y=r.deck_front_y - 0.090, z=r.hinge_z - DECK_RAIL_DROP,
            length=0.120, rail_half=0.013,
            name=f"deck_frame__sleeve_rail__guide_sleeve_{side}",
        )


def _deck_frame_nested_rail_build(deck, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Nested telescoping rails: a visible outer section and an inner slide."""
    reach = r.deck_travel_m + RAIL_TAIL
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * r.rail_x
        deck.visual(
            Box((0.022, reach, 0.022)),
            origin=Origin(xyz=(x, r.deck_front_y - reach * 0.5, 0.0)),
            material=mats["zinc"],
            name=f"deck_frame__nested_rail__inner_slide_{side}", material_class_id="metal.steel_galvanized",
        )
        _guide_channel(
            frame, mats, x=x, y=r.deck_front_y - 0.090, z=r.hinge_z - DECK_RAIL_DROP,
            length=0.120, rail_half=0.011,
            name=f"deck_frame__nested_rail__outer_section_{side}",
        )
        # Stop collar: a ring around the outer section, not a plug in the bore.
        for f, dz in enumerate((-0.026, 0.026)):
            frame.visual(
                Box((0.050, 0.024, 0.008)),
                origin=Origin(xyz=(x, r.deck_front_y - 0.158, r.hinge_z - DECK_RAIL_DROP + dz)),
                material=mats["zinc"],
                name=f"deck_frame__nested_rail__stop_collar_{side}_{f}", material_class_id="metal.steel_galvanized",
            )


def _deck_frame_slatted_frame_build(deck, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Open slatted carriage platform: side rails crossed by transverse slats."""
    reach = r.deck_travel_m + RAIL_TAIL
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * r.rail_x
        deck.visual(
            Box((0.026, reach, 0.026)),
            origin=Origin(xyz=(x, r.deck_front_y - reach * 0.5, 0.0)),
            material=mats["steel"],
            name=f"deck_frame__slatted_frame__side_rail_{side}", material_class_id="metal.steel_bare",
        )
        _guide_channel(
            frame, mats, x=x, y=r.deck_front_y - 0.090, z=r.hinge_z - DECK_RAIL_DROP,
            length=0.120, rail_half=0.013,
            name=f"deck_frame__slatted_frame__guide_block_{side}",
        )
    slats = 4
    for i in range(slats):
        y = r.deck_front_y - 0.030 - (reach - 0.070) * i / (slats - 1)
        # Slats sit above the channel side walls, on risers off the rails, so
        # they sweep clear over the fixed guides at every travel position.
        deck.visual(
            Box((2.0 * r.rail_x + 0.026, 0.024, 0.008)),
            origin=Origin(xyz=(0.0, y, 0.019)),
            material=mats["zinc"],
            name=f"deck_frame__slatted_frame__platform_slat_{i}", material_class_id="metal.steel_galvanized",
        )
        for side, sx in enumerate((-1.0, 1.0)):
            deck.visual(
                Box((0.014, 0.022, 0.020)),
                origin=Origin(xyz=(sx * r.rail_x, y, 0.010)),
                material=mats["zinc"],
                name=f"deck_frame__slatted_frame__slat_riser_{i}_{side}", material_class_id="metal.steel_galvanized",
            )


def _guide_channel(frame, mats: dict[str, str], *, x: float, y: float, z: float,
                   length: float, rail_half: float, name: str) -> None:
    """Four plates forming an open channel the carriage rail slides through.

    A solid block at the rail station would simply contain the rail, which is a
    whole-volume interpenetration; a channel leaves a real running clearance.
    """
    gap = MOUNT
    frame.visual(
        Box((2.0 * (rail_half + gap + 0.010), length, 0.010)),
        origin=Origin(xyz=(x, y, z - (rail_half + gap + 0.005))),
        material=mats["steel"],
        name=f"{name}_floor", material_class_id="metal.steel_bare",
    )
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.010, length, 2.0 * (rail_half + gap))),
            origin=Origin(xyz=(x + sx * (rail_half + gap + 0.005), y, z)),
            material=mats["steel"],
            name=f"{name}_side_{side}", material_class_id="metal.steel_bare",
        )


_DECK_BUILDERS = {
    "sleeve_rail": _deck_frame_sleeve_rail_build,
    "nested_rail": _deck_frame_nested_rail_build,
    "slatted_frame": _deck_frame_slatted_frame_build,
}


# --- backrest candidates ----------------------------------------------------
def _back_style_plain_pad_build(back, r: ResolvedConfig, mats: dict[str, str]) -> None:
    w = r.seat_width_m * 0.94
    length = r.back_len_m
    back.visual(
        Box((w, 0.100, length)),
        origin=Origin(xyz=(0.0, -0.050, length * 0.5)),
        material=mats["upholstery"],
        name="back_style__plain_pad__pad", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    back.visual(
        Box((w * 0.98, 0.014, length * 0.92)),
        origin=Origin(xyz=(0.0, -0.004, length * 0.5)),
        material=mats["shadow"],
        name="back_style__plain_pad__face_panel", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )


def _back_style_clickclack_ratchet_build(back, r: ResolvedConfig, mats: dict[str, str]) -> None:
    w = r.seat_width_m * 0.90
    length = r.back_len_m
    back.visual(
        Box((w, 0.100, length)),
        origin=Origin(xyz=(0.0, -0.050, length * 0.5)),
        material=mats["upholstery"],
        name="back_style__clickclack_ratchet__pad", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    # Exposed side ratchet plates with stepped notches: the click-clack tell.
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * (w * 0.5 + 0.014)
        back.visual(
            Box((0.010, 0.086, length * 0.42)),
            origin=Origin(xyz=(x, -0.043, length * 0.20)),
            material=mats["zinc"],
            name=f"back_style__clickclack_ratchet__plate_{side}", material_class_id="metal.steel_galvanized",
        )
        for n in range(3):
            back.visual(
                Box((0.014, 0.020, 0.014)),
                origin=Origin(
                    xyz=(x, -0.012 - 0.026 * n, length * 0.06 + 0.030 * n)
                ),
                material=mats["zinc"],
                name=f"back_style__clickclack_ratchet__notch_{side}_{n}", material_class_id="metal.steel_galvanized",
            )


def _back_style_slatted_fold_back_build(back, r: ResolvedConfig, mats: dict[str, str]) -> None:
    w = r.seat_width_m * 0.94
    length = r.back_len_m
    for side, sx in enumerate((-1.0, 1.0)):
        back.visual(
            Box((0.030, 0.030, length)),
            origin=Origin(xyz=(sx * (w * 0.5 - 0.015), -0.015, length * 0.5)),
            material=mats["steel"],
            name=f"back_style__slatted_fold_back__stile_{side}", material_class_id="metal.steel_bare",
        )
    for i in range(4):
        z = length * (0.12 + 0.76 * i / 3.0)
        back.visual(
            Box((w, 0.022, 0.020)),
            origin=Origin(xyz=(0.0, -0.015, z)),
            material=mats["steel"],
            name=f"back_style__slatted_fold_back__slat_{i}", material_class_id="metal.steel_bare",
        )
    back.visual(
        Box((w * 0.92, 0.070, length * 0.88)),
        origin=Origin(xyz=(0.0, -0.052, length * 0.5)),
        material=mats["upholstery"],
        name="back_style__slatted_fold_back__face_pad", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )


_BACK_BUILDERS = {
    "plain_pad": _back_style_plain_pad_build,
    "clickclack_ratchet": _back_style_clickclack_ratchet_build,
    "slatted_fold_back": _back_style_slatted_fold_back_build,
}


# --- carcass ----------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("sofa_frame", meta={"role": "sofa_frame"})
    depth = r.seat_depth_m
    sw = r.seat_width_m
    base_z = r.hinge_z - 0.090
    # Plinth carrying everything, from the rear panel to the front apron.
    frame.visual(
        Box((r.width_m, depth + 0.04, 0.070)),
        origin=Origin(xyz=(0.0, -depth * 0.5 + 0.02, base_z - 0.035)),
        material=mats["upholstery"],
        name="carcass_plinth", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((ARM_W, depth + 0.04, r.bed_height_m + 0.16)),
            origin=Origin(
                xyz=(
                    sx * (r.width_m - ARM_W) * 0.5,
                    -depth * 0.5 + 0.02,
                    (r.bed_height_m + 0.16) * 0.5,
                )
            ),
            material=mats["upholstery"],
            name=f"carcass_arm_{side}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
        )
    frame.visual(
        Box((sw, 0.090, 0.070)),
        origin=Origin(xyz=(0.0, -depth + 0.045, base_z - 0.020)),
        material=mats["upholstery"],
        name="carcass_rear_apron", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    frame.visual(
        Box((sw, 0.080, 0.070)),
        origin=Origin(xyz=(0.0, 0.0, base_z - 0.020)),
        material=mats["upholstery"],
        name="carcass_front_apron", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    # Seat support: two side boards outboard of the carriage rails, plus cross
    # rails threaded through the gap ABOVE those rails.  Without them the fixed
    # seat has nothing under it and reads as an isolated part.
    seat_cy = 0.5 * (r.seat_y0 + r.seat_y1)
    board_x0 = sw * 0.5 - 0.070
    board_x1 = sw * 0.5 - 0.002
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((board_x1 - board_x0, r.seat_y1 - r.seat_y0 + 0.04,
                 r.bed_height_m - LEAF_T - base_z + MOUNT)),
            origin=Origin(
                xyz=(
                    sx * 0.5 * (board_x0 + board_x1),
                    seat_cy,
                    0.5 * (base_z + r.bed_height_m - LEAF_T + MOUNT),
                )
            ),
            material=mats["upholstery"],
            name=f"seat_support_board_{side}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
        )
    for i, y in enumerate((r.seat_y0 + 0.03, seat_cy, r.seat_y1 - 0.03)):
        frame.visual(
            Box((sw * 0.98, 0.048, 0.008)),
            origin=Origin(xyz=(0.0, y, r.bed_height_m - LEAF_T - 0.004)),
            material=mats["steel"],
            name=f"seat_support_rail_{i}", material_class_id="metal.steel_bare",
        )

    # Backrest hinge knuckles just outside the back pad.
    back_half = r.seat_width_m * 0.48
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.044, 0.070, r.bed_height_m - base_z + 0.070)),
            origin=Origin(
                xyz=(
                    sx * (back_half + 0.022),
                    r.back_hinge_y,
                    0.5 * (base_z - 0.060 + r.bed_height_m),
                )
            ),
            material=mats["steel"],
            name=f"backrest_hinge_post_{side}", material_class_id="metal.steel_bare",
        )
        _x_cyl(
            frame,
            f"backrest_hinge_knuckle_{side}",
            0.022,
            0.046,
            (sx * (back_half + 0.022), r.back_hinge_y, r.bed_height_m),
            mats["zinc"],
        )
    for index, (x, y) in enumerate(
        (
            (-(r.width_m * 0.5 - 0.07), -depth + 0.09),
            (r.width_m * 0.5 - 0.07, -depth + 0.09),
            (-(r.width_m * 0.5 - 0.07), -0.06),
            (r.width_m * 0.5 - 0.07, -0.06),
        )
    ):
        frame.visual(
            Box((0.042, 0.042, base_z - 0.070 + MOUNT)),
            origin=Origin(xyz=(x, y, (base_z - 0.070 + MOUNT) * 0.5)),
            material=mats["foot"],
            name=f"carcass_foot_{index}", material_class_id="rubber.smooth_plain",
        )
    return frame


def _build_seat(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    seat = model.part("seat_deck", meta={"role": "seat_deck"})
    cy = 0.5 * (r.seat_y0 + r.seat_y1)
    run = r.seat_y1 - r.seat_y0
    # Authored in SEAT-LOCAL coordinates: the FIXED joint origin already places
    # this part at (0, cy, bed_height - LEAF_T), so repeating those world values
    # in the visuals would double the offset and float the seat off the frame.
    seat.visual(
        Box((r.seat_width_m * 0.98, run, 0.020)),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        material=mats["shadow"],
        name="seat_deck_board", material_class_id="fabric.plain_flat_weave",
    )
    seat.visual(
        Box((r.seat_width_m * 0.96, run - 0.010, LEAF_T - 0.020)),
        origin=Origin(xyz=(0.0, 0.0, LEAF_T - (LEAF_T - 0.020) * 0.5)),
        material=mats["upholstery"],
        name="seat_deck_cushion", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    model.articulation(
        "frame_to_seat_deck",
        ArticulationType.FIXED,
        parent=frame,
        child=seat,
        origin=Origin(xyz=(0.0, cy, r.bed_height_m - LEAF_T)),
    )


# --- carriage, leaves and legs ---------------------------------------------
def _build_carriage(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]):
    deck = model.part("pullout_deck", meta={"role": "pullout_deck"})
    # Front cross rail the leaf hinge hangs on, tying both carriage rails.
    deck.visual(
        Box((2.0 * r.rail_x + 0.026, 0.024, 0.026)),
        origin=Origin(xyz=(0.0, r.deck_front_y - 0.012, 0.0)),
        material=mats["steel"],
        name="carriage_front_rail", material_class_id="metal.steel_bare",
    )
    _DECK_BUILDERS[r.deck_frame](deck, frame, r, mats)
    # Hinge stanchions rising from the carriage rail to the leaf hinge line.
    for side, sx in enumerate((-1.0, 1.0)):
        deck.visual(
            Box((0.030, 0.034, 0.050 + 0.012)),
            origin=Origin(
                xyz=(sx * r.rail_x, r.deck_front_y - 0.008, DECK_RAIL_DROP * 0.5 - 0.006)
            ),
            material=mats["steel"],
            name=f"carriage_hinge_stanchion_{side}", material_class_id="metal.steel_bare",
        )
        _x_cyl(
            deck,
            f"carriage_hinge_knuckle_{side}",
            0.018,
            0.040,
            (sx * r.rail_x, r.deck_front_y, DECK_RAIL_DROP),
            mats["zinc"],
        )
    model.articulation(
        "frame_to_pullout_deck",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=deck,
        origin=Origin(xyz=(0.0, 0.0, r.hinge_z - DECK_RAIL_DROP)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=r.deck_travel_m, effort=600.0, velocity=0.22
        ),
        meta={"positive_motion": "pulls the sleeper carriage out of the carcass"},
    )
    return deck


def _build_leaves(model: ArticulatedObject, deck, r: ResolvedConfig, mats: dict[str, str]):
    leaves = []
    parent = deck
    for index in range(2):
        leaf = model.part(
            f"mattress_build__{r.mattress_build}__leaf_{index}",
            meta={"role": "mattress_leaf", "index": index},
        )
        _LEAF_BUILDERS[r.mattress_build](leaf, r, mats, index)
        # Hinge barrel on the leaf's rear edge, journalled into the knuckles of
        # whatever it hangs from.
        knuckle_x = r.rail_x if index == 0 else r.leaf_width_m * 0.40
        barrel_len = 2.0 * (knuckle_x - KNUCKLE_LEN * 0.5 + MOUNT)
        _x_cyl(
            leaf,
            f"leaf_hinge_barrel_{index}",
            HINGE_R,
            barrel_len,
            (0.0, 0.0, 0.0),
            mats["zinc"],
        )
        # Hinge leaf strapping the barrel onto the panel.  The barrel sits on
        # the pivot axis while the panel body starts LEAF_GAP away, so without
        # the strap the barrel is an island under the 1e-6 m check -- and a real
        # piano-style hinge does carry a leaf from the knuckle onto the panel.
        leaf.visual(
            Box((barrel_len, LEAF_GAP + 0.012, 0.012)),
            origin=Origin(xyz=(0.0, (LEAF_GAP + 0.012) * 0.5 - 0.006, 0.0)),
            material=mats["zinc"],
            name=f"leaf_hinge_strap_{index}", material_class_id="metal.steel_galvanized",
        )
        if index == 0:
            point = (0.0, r.deck_front_y, DECK_RAIL_DROP)
        else:
            # Knuckles on leaf 0's far edge that leaf 1's barrel journals into.
            for side, sx in enumerate((-1.0, 1.0)):
                _x_cyl(
                    parent,
                    f"leaf_0_front_knuckle_{side}",
                    KNUCKLE_R,
                    KNUCKLE_LEN,
                    (sx * knuckle_x, r.leaf_len_m + HINGE_OFFSET, 0.0),
                    mats["zinc"],
                )
                # Arm carrying each knuckle off the leaf body it belongs to.
                parent.visual(
                    Box((KNUCKLE_LEN, HINGE_OFFSET + 0.012, 0.014)),
                    origin=Origin(
                        xyz=(
                            sx * knuckle_x,
                            r.leaf_len_m + (HINGE_OFFSET - 0.012) * 0.5,
                            0.0,
                        )
                    ),
                    material=mats["zinc"],
                    name=f"leaf_0_knuckle_arm_{side}", material_class_id="metal.steel_galvanized",
                )
            point = (0.0, r.leaf_len_m + HINGE_OFFSET, 0.0)
        _rev_joint(
            model,
            name=f"leaf_{index}_fold",
            parent=parent,
            child=leaf,
            point=point,
            lower=0.0,
            upper=math.pi / 2.0,
            effort=260.0,
            velocity=0.55,
        )
        leaves.append(leaf)
        parent = leaf
    return leaves


def _build_bed_legs(model: ArticulatedObject, leaf1, r: ResolvedConfig, mats: dict[str, str]):
    builder = _LEG_BUILDERS[r.bed_leg]
    legs = []
    # Hinge rail across the leaf underside carrying every receiver bracket.
    leaf1.visual(
        Box((r.leaf_width_m, 0.048, 0.014)),
        origin=Origin(xyz=(0.0, r.leg_local_y, -LEAF_T * 0.5 - 0.004)),
        material=mats["steel"],
        name="leg_hinge_rail", material_class_id="metal.steel_bare",
    )
    for index, x in enumerate(r.leg_x):
        # Receiver bracket pair on that rail that captures the leg pivot.
        for side, sx in enumerate((-1.0, 1.0)):
            leaf1.visual(
                Box((LEG_BRACKET_T, 0.046, 0.052)),
                origin=Origin(
                    xyz=(x + sx * LEG_BRACKET_X, r.leg_local_y, -LEAF_T * 0.5 - 0.018)
                ),
                material=mats["steel"],
                name=f"leg_receiver_{index}_{side}", material_class_id="metal.steel_bare",
            )
        leg = model.part(
            f"bed_leg__{r.bed_leg}__leg_{index}",
            meta={"role": "bed_leg", "index": index},
        )
        builder(leg, r, mats, index)
        _rev_joint(
            model,
            name=f"leaf_to_bed_leg_{index}",
            parent=leaf1,
            child=leg,
            point=(x, r.leg_local_y, -LEAF_T * 0.5 - 0.030),
            # The leg stows flat under the leaf and swings DOWN to the floor.
            lower=0.0,
            upper=math.pi / 2.0,
            effort=90.0,
            velocity=1.0,
        )
        legs.append(leg)
    return legs


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_folding_sofa_bed1(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Folding_sofa_bed1",
            "slot_choices": slot_choices_for_config(r),
            "conversion": "guided pull-out carriage + folding mattress leaves + fold-down legs",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)
    _build_seat(model, frame, r, mats)

    back = model.part(f"back_style__{r.back_style}__backrest", meta={"role": "backrest"})
    _BACK_BUILDERS[r.back_style](back, r, mats)
    _x_cyl(
        back,
        "backrest_hinge_barrel",
        0.016,
        2.0 * (r.seat_width_m * 0.48 - 0.001 + MOUNT),
        (0.0, 0.0, 0.0),
        mats["zinc"],
    )
    _rev_joint(
        model,
        name="frame_to_backrest",
        parent=frame,
        child=back,
        point=(0.0, r.back_hinge_y, r.bed_height_m),
        lower=0.0,
        upper=math.pi / 2.0,
        effort=180.0,
        velocity=0.45,
    )

    deck = _build_carriage(model, frame, r, mats)
    leaves = _build_leaves(model, deck, r, mats)
    _build_bed_legs(model, leaves[1], r, mats)

    leg_joints = [f"leaf_to_bed_leg_{i}" for i in range(r.bed_leg_count)]
    model.meta["risk_poses"] = (
        {
            "frame_to_pullout_deck": 0.0,
            "frame_to_backrest": 0.0,
            "leaf_0_fold": 0.0,
            "leaf_1_fold": 0.0,
            **{n: 0.0 for n in leg_joints},
        },
        {
            "frame_to_pullout_deck": r.deck_travel_m,
            "frame_to_backrest": math.pi / 2.0,
            "leaf_0_fold": 0.0,
            "leaf_1_fold": 0.0,
            **{n: math.pi / 2.0 for n in leg_joints},
        },
        {
            "frame_to_pullout_deck": 0.0,
            "frame_to_backrest": 0.0,
            "leaf_0_fold": math.pi / 2.0,
            "leaf_1_fold": math.pi / 2.0,
            **{n: 0.0 for n in leg_joints},
        },
    )
    model.meta["coupled_joint_pairs"] = (
        ("frame_to_pullout_deck", "leaf_0_fold"),
        ("leaf_0_fold", "leaf_1_fold"),
        ("frame_to_backrest", "leaf_1_fold"),
    ) + tuple(("leaf_1_fold", n) for n in leg_joints)
    return model


def build_seeded_picturex_0611_folding_sofa_bed1(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_folding_sofa_bed1(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_folding_sofa_bed1_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "sofa_frame")
    seats = _parts_by_role(model, "seat_deck")
    backs = _parts_by_role(model, "backrest")
    decks = _parts_by_role(model, "pullout_deck")
    leaves = _parts_by_role(model, "mattress_leaf")
    legs = _parts_by_role(model, "bed_leg")

    joints = {j.name: j for j in model.articulations}
    deck_joint = joints.get("frame_to_pullout_deck")
    back_joint = joints.get("frame_to_backrest")
    leaf_joints = [joints.get(f"leaf_{i}_fold") for i in range(2)]
    leg_joints = [joints.get(f"leaf_to_bed_leg_{i}") for i in range(r.bed_leg_count)]

    def _is_rev_x(j) -> bool:
        return (
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(abs(v), 6) for v in j.axis) == (1.0, 0.0, 0.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    ctx.check(
        "category_anchor: guided pull-out sleeper carriage",
        len(frames) == 1
        and len(seats) == 1
        and len(backs) == 1
        and len(decks) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "sofa_frame"
        and deck_joint is not None
        and deck_joint.articulation_type == ArticulationType.PRISMATIC
        and tuple(round(v, 6) for v in deck_joint.axis) == (0.0, 1.0, 0.0)
        and deck_joint.parent == "sofa_frame"
        and deck_joint.motion_limits.upper > deck_joint.motion_limits.lower
        and _is_rev_x(back_joint)
        and back_joint.parent == "sofa_frame",
        details=(
            f"frames={len(frames)} seats={len(seats)} backs={len(backs)} decks={len(decks)}"
        ),
    )

    ctx.check(
        "category_anchor: folding mattress leaves on the carriage",
        len(leaves) == 2
        and all(_is_rev_x(j) for j in leaf_joints)
        and leaf_joints[0].parent == "pullout_deck"
        and leaf_joints[1].parent == leaves[0].name
        # The retracted carriage must still park its hinge in front of the seat,
        # or a leaf laid flat with the carriage in would land on the seat.
        and r.deck_front_y > r.seat_y1 + 0.05,
        details=(
            f"leaves={len(leaves)} deck_front={r.deck_front_y} seat_front={r.seat_y1}"
        ),
    )

    # Motion evidence: the carriage really travels, and the legs really reach
    # the floor with the bed made.
    rest_deck = ctx.part_world_aabb(decks[0])
    with ctx.pose({deck_joint: deck_joint.motion_limits.upper}):
        out_deck = ctx.part_world_aabb(decks[0])
        with ctx.pose({j: j.motion_limits.upper for j in leg_joints}):
            leg_boxes = [ctx.part_world_aabb(leg) for leg in legs]
    ctx.check(
        "category_anchor: fold-down bed legs reach the floor",
        len(legs) == r.bed_leg_count
        and all(_is_rev_x(j) and j.parent == leaves[1].name for j in leg_joints)
        and all(b is not None and -0.012 <= b[0][2] <= 0.055 for b in leg_boxes),
        details=f"legs={len(legs)} leg_boxes={leg_boxes}",
    )
    ctx.check(
        "carriage pulls forward by its full travel",
        rest_deck is not None
        and out_deck is not None
        and abs((out_deck[0][1] - rest_deck[0][1]) - r.deck_travel_m) < 1e-3,
        details=f"rest={rest_deck} out={out_deck} travel={r.deck_travel_m}",
    )

    # Motion evidence: the leaves fold UP, clear of the seat, not down into it.
    leaf1 = leaves[1]
    flat = ctx.part_world_aabb(leaf1)
    with ctx.pose({leaf_joints[0]: leaf_joints[0].motion_limits.upper,
                   leaf_joints[1]: leaf_joints[1].motion_limits.upper}):
        folded = ctx.part_world_aabb(leaf1)
    ctx.check(
        "mattress leaves fold up and back above the backrest",
        flat is not None
        and folded is not None
        and folded[0][2] > flat[1][2] + 0.20
        and folded[0][1] < flat[0][1],
        details=f"flat={flat} folded={folded}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    back_ok = {
        "plain_pad": any("plain_pad__face_panel" in n for n in visual_names),
        "clickclack_ratchet": any("clickclack_ratchet__notch" in n for n in visual_names),
        "slatted_fold_back": any("slatted_fold_back__slat" in n for n in visual_names),
    }[r.back_style]
    ctx.check("category_anchor: back_style identity", back_ok, details=f"back_style={r.back_style}")

    deck_ok = {
        "sleeve_rail": any("sleeve_rail__guide_sleeve" in n for n in visual_names),
        "nested_rail": any("nested_rail__stop_collar" in n for n in visual_names),
        "slatted_frame": any("slatted_frame__platform_slat" in n for n in visual_names),
    }[r.deck_frame]
    ctx.check("category_anchor: deck_frame identity", deck_ok, details=f"deck_frame={r.deck_frame}")

    mat_ok = {
        "slatted_panel": any("slatted_panel__slat" in n for n in visual_names),
        "tufted_panel": any("tufted_panel__button" in n for n in visual_names),
    }[r.mattress_build]
    ctx.check(
        "category_anchor: mattress_build identity", mat_ok,
        details=f"mattress_build={r.mattress_build}",
    )

    leg_ok = {
        "u_leg": any("u_leg__bend" in n for n in visual_names),
        "twin_post": any("twin_post__tie_bar" in n for n in visual_names),
    }[r.bed_leg]
    ctx.check("category_anchor: bed_leg identity", leg_ok, details=f"bed_leg={r.bed_leg}")

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "narrow_shallow_two_legs",
        {
            "back_style": "plain_pad",
            "deck_frame": "sleeve_rail",
            "mattress_build": "tufted_panel",
            "bed_leg": "u_leg",
            "bed_leg_count": 2,
            "width_m": 1.60,
            "seat_depth_m": 0.52,
            "bed_height_m": 0.38,
        },
        reason="narrowest, shallowest sofa with the shortest carriage travel and two legs",
    ),
    corner_case(
        "wide_deep_four_legs_slatted",
        {
            "back_style": "slatted_fold_back",
            "deck_frame": "slatted_frame",
            "mattress_build": "slatted_panel",
            "bed_leg": "twin_post",
            "bed_leg_count": 4,
            "width_m": 2.10,
            "seat_depth_m": 0.68,
            "bed_height_m": 0.46,
        },
        reason="largest envelope, longest leaves and four twin-post legs",
    ),
    corner_case(
        "wide_shallow_ratchet_nested",
        {
            "back_style": "clickclack_ratchet",
            "deck_frame": "nested_rail",
            "mattress_build": "slatted_panel",
            "bed_leg": "u_leg",
            "bed_leg_count": 3,
            "width_m": 2.10,
            "seat_depth_m": 0.52,
            "bed_height_m": 0.46,
        },
        reason="widest body on the shallowest carcass - tightest folded-leaf to backrest clearance",
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
    "build_picturex_0611_folding_sofa_bed1",
    "build_seeded_picturex_0611_folding_sofa_bed1",
    "run_picturex_0611_folding_sofa_bed1_tests",
]
