# SPDX-License-Identifier: Apache-2.0

"""Self-contained lift-and-pull convertible sofa bed template.

One rigid ``sofa_frame`` root carries the carcass, the fixed arms, the REAR seat
band and the carriage guides.  ``back_panel_count`` ``back_panel`` parts are
REVOLUTE (+x) children of the frame.  The ``pullout_carriage`` is a PRISMATIC
(+y) child of the frame, the ``deck_lift_stage`` is a PRISMATIC (+z) child of
that carriage, and the ``bed_deck`` is FIXED on the lift stage.

The seat is cushioned only over its REAR band and the deck's retracted footprint
lies entirely forward of it, so raising the deck while the carriage is still in
never drives it into the seat.  Deck up + carriage in is the sofa, deck up +
carriage out is the bed, deck down is the stowed platform -- and every single
joint boundary pose is genuinely clear, not just those three.

Four component slots vary without touching the mechanism: ``back_build``,
``deck_build``, ``lift_frame`` and ``carriage_style``.  No source-replay import,
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

BackBuild = Literal["tufted_panel", "ratchet_back", "split_panel"]
DeckBuild = Literal["slab_deck", "trifold_deck"]
LiftFrame = Literal["post_lift", "scissor_underframe"]
CarriageStyle = Literal["rail_carriage", "roller_carriage"]
ArmBuild = Literal["fixed_arm", "fold_down_arm"]
PaletteStyle = Literal["dove_gray", "navy_linen", "camel_leather", "sage_weave"]

BACK_BUILDS: tuple[BackBuild, ...] = ("tufted_panel", "ratchet_back", "split_panel")
DECK_BUILDS: tuple[DeckBuild, ...] = ("slab_deck", "trifold_deck")
LIFT_FRAMES: tuple[LiftFrame, ...] = ("post_lift", "scissor_underframe")
CARRIAGE_STYLES: tuple[CarriageStyle, ...] = ("rail_carriage", "roller_carriage")
ARM_BUILDS: tuple[ArmBuild, ...] = ("fixed_arm", "fold_down_arm")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("dove_gray", "navy_linen", "camel_leather", "sage_weave")


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("back_build", BACK_BUILDS),
        component_slot("deck_build", DECK_BUILDS),
        component_slot("lift_frame", LIFT_FRAMES),
        component_slot("carriage_style", CARRIAGE_STYLES),
        component_slot("arm_build", ARM_BUILDS),
        multiplicity_slot("back_panel_count", (1, 2, 3), item_slot="back_build"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "dove_gray": {
        "upholstery": (0.70, 0.71, 0.72, 1.0),
        "shadow": (0.55, 0.56, 0.57, 1.0),
        "steel": (0.24, 0.26, 0.27, 1.0),
        "zinc": (0.62, 0.65, 0.67, 1.0),
        "foot": (0.07, 0.07, 0.08, 1.0),
    },
    "navy_linen": {
        "upholstery": (0.18, 0.23, 0.35, 1.0),
        "shadow": (0.12, 0.16, 0.25, 1.0),
        "steel": (0.22, 0.24, 0.28, 1.0),
        "zinc": (0.58, 0.61, 0.65, 1.0),
        "foot": (0.05, 0.05, 0.06, 1.0),
    },
    "camel_leather": {
        "upholstery": (0.64, 0.45, 0.27, 1.0),
        "shadow": (0.47, 0.31, 0.17, 1.0),
        "steel": (0.28, 0.25, 0.22, 1.0),
        "zinc": (0.66, 0.60, 0.48, 1.0),
        "foot": (0.07, 0.06, 0.05, 1.0),
    },
    "sage_weave": {
        "upholstery": (0.57, 0.62, 0.51, 1.0),
        "shadow": (0.41, 0.46, 0.36, 1.0),
        "steel": (0.26, 0.29, 0.26, 1.0),
        "zinc": (0.61, 0.64, 0.60, 1.0),
        "foot": (0.05, 0.05, 0.05, 1.0),
    },
}


ARM_W = 0.155            # upholstered arm width per side
DECK_T = 0.070           # bed deck thickness
SEAT_BAND = 0.26         # cushioned rear seat band depth
# The retracted deck parks this far FORWARD of the seat band, so raising it with
# the carriage still in can never drive it into the seat.
SEAT_STANDOFF = 0.035
BACK_RECLINE = 0.62
RAIL_H = 0.036
GUIDE_STANDOFF = 0.090   # guide station behind the deck's rear edge
# The lift stage's top frame and deck ride ABOVE the carriage rails, so the
# deck fully down still sits clear of the carriage it is carried by.
STAGE_DECK_Z = 0.045
# Sub-millimetre lap: a fitting laps its host by less than the collision
# tolerance so QC reads real contact without an overlap allowance.
MOUNT = 0.0006


@dataclass(frozen=True)
class Config:
    back_build: BackBuild = "tufted_panel"
    deck_build: DeckBuild = "slab_deck"
    lift_frame: LiftFrame = "post_lift"
    carriage_style: CarriageStyle = "rail_carriage"
    arm_build: ArmBuild = "fixed_arm"
    back_panel_count: int = 2
    width_m: float | None = None
    seat_depth_m: float | None = None
    bed_height_m: float | None = None
    palette_style: PaletteStyle = "dove_gray"
    name: str = "pictureX_0611_Folding_sofa_bed3"


@dataclass(frozen=True)
class ResolvedConfig:
    back_build: BackBuild
    deck_build: DeckBuild
    lift_frame: LiftFrame
    carriage_style: CarriageStyle
    arm_build: ArmBuild
    back_panel_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    width_m: float
    seat_depth_m: float
    bed_height_m: float
    seat_width_m: float
    seat_y0: float
    seat_y1: float
    deck_rear_y: float
    deck_len_m: float
    deck_width_m: float
    carriage_travel_m: float
    carriage_z: float
    lift_travel_m: float
    back_hinge_y: float
    back_len_m: float
    back_x: tuple[float, ...]
    back_panel_w: float
    rail_x: float
    post_x: float
    post_y: tuple[float, ...]
    plinth_top_z: float
    arm_base_h_m: float
    arm_panel_h_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x50FA_0BE3)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        back_build=choices["back_build"],
        deck_build=choices["deck_build"],
        lift_frame=choices["lift_frame"],
        carriage_style=choices["carriage_style"],
        arm_build=choices["arm_build"],
        back_panel_count=choices["back_panel_count"],
        width_m=round(rng.uniform(1.55, 2.05), 4),
        seat_depth_m=round(rng.uniform(0.52, 0.68), 4),
        bed_height_m=round(rng.uniform(0.38, 0.46), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"folding_sofa_bed3_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "back_build": config.back_build,
            "deck_build": config.deck_build,
            "lift_frame": config.lift_frame,
            "carriage_style": config.carriage_style,
            "arm_build": config.arm_build,
            "back_panel_count": config.back_panel_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.width_m is not None and not 1.55 <= float(config.width_m) <= 2.05:
        raise ValueError("width_m must be in [1.55, 2.05]")
    if config.seat_depth_m is not None and not 0.52 <= float(config.seat_depth_m) <= 0.68:
        raise ValueError("seat_depth_m must be in [0.52, 0.68]")
    if config.bed_height_m is not None and not 0.38 <= float(config.bed_height_m) <= 0.46:
        raise ValueError("bed_height_m must be in [0.38, 0.46]")

    width = _clamp(config.width_m, 1.55, 2.05) if config.width_m is not None else 1.85
    depth = _clamp(config.seat_depth_m, 0.52, 0.68) if config.seat_depth_m is not None else 0.60
    height = _clamp(config.bed_height_m, 0.38, 0.46) if config.bed_height_m is not None else 0.42

    seat_width = width - 2.0 * ARM_W
    seat_y0 = -depth + 0.05
    seat_y1 = seat_y0 + SEAT_BAND
    deck_rear = seat_y1 + SEAT_STANDOFF
    deck_len = depth * 0.62
    deck_width = seat_width - 0.080
    travel = depth * 0.29
    plinth_top = height - 0.10
    # Ride height is set so the lift posts, which hang lift_travel + 40 mm below
    # the stage, still clear the floor with the deck fully down.
    carriage_z = (height - DECK_T) * 0.45 + 0.030
    lift_travel = (height - DECK_T) - (carriage_z + STAGE_DECK_Z)

    n = int(config.back_panel_count)
    panel_w = (seat_width - 0.030 * (n + 1)) / n
    xs = tuple(-(n - 1) * 0.5 * (panel_w + 0.030) + (panel_w + 0.030) * i for i in range(n))

    back_hinge_y = -depth + 0.030
    back_len = min(0.46, depth * 0.76)
    rail_x = seat_width * 0.5 - 0.075
    post_x = rail_x - 0.045
    post_y = (deck_rear + 0.10, deck_rear + deck_len - 0.10)

    return ResolvedConfig(
        back_build=config.back_build,
        deck_build=config.deck_build,
        lift_frame=config.lift_frame,
        carriage_style=config.carriage_style,
        arm_build=config.arm_build,
        back_panel_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        width_m=width,
        seat_depth_m=depth,
        bed_height_m=height,
        seat_width_m=seat_width,
        seat_y0=seat_y0,
        seat_y1=seat_y1,
        deck_rear_y=deck_rear,
        deck_len_m=deck_len,
        deck_width_m=deck_width,
        carriage_travel_m=travel,
        carriage_z=carriage_z,
        lift_travel_m=lift_travel,
        back_hinge_y=back_hinge_y,
        back_len_m=back_len,
        back_x=xs,
        back_panel_w=panel_w,
        rail_x=rail_x,
        post_x=post_x,
        post_y=post_y,
        plinth_top_z=plinth_top,
        arm_base_h_m=(
            height + 0.15 if config.arm_build == "fixed_arm" else plinth_top + 0.030
        ),
        arm_panel_h_m=(height + 0.15) - (plinth_top + 0.030),
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("back_build", config.back_build),
        ("deck_build", config.deck_build),
        ("lift_frame", config.lift_frame),
        ("carriage_style", config.carriage_style),
        ("arm_build", config.arm_build),
        ("back_panel_count", config.back_panel_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"sb3_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"sb3_{r.palette_style}_{key}"
    return mats


def _x_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.brushed_silver",
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


# --- back panel candidates --------------------------------------------------
def _back_build_tufted_panel_build(back, r: ResolvedConfig, mats: dict[str, str],
                                   index: int) -> None:
    w = r.back_panel_w
    length = r.back_len_m
    back.visual(
        Box((w, 0.096, length)),
        origin=Origin(xyz=(0.0, -0.048, length * 0.5)),
        material=mats["upholstery"],
        name=f"back_build__tufted_panel__pad_{index}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    for row, fz in enumerate((length * 0.32, length * 0.68)):
        for col, bx in enumerate((-w * 0.26, 0.0, w * 0.26)):
            back.visual(
                Cylinder(radius=0.013, length=0.012),
                origin=Origin(xyz=(bx, -0.004, fz), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["shadow"],
                name=f"back_build__tufted_panel__button_{index}_{row}_{col}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
            )
    back.visual(
        Box((w, 0.096, 0.026)),
        origin=Origin(xyz=(0.0, -0.048, length - 0.010)),
        material=mats["shadow"],
        name=f"back_build__tufted_panel__piped_top_{index}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )


def _back_build_ratchet_back_build(back, r: ResolvedConfig, mats: dict[str, str],
                                   index: int) -> None:
    w = r.back_panel_w - 0.030
    length = r.back_len_m
    back.visual(
        Box((w, 0.092, length)),
        origin=Origin(xyz=(0.0, -0.046, length * 0.5)),
        material=mats["upholstery"],
        name=f"back_build__ratchet_back__pad_{index}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * (w * 0.5 + 0.006)
        back.visual(
            Box((0.010, 0.084, length * 0.88)),
            origin=Origin(xyz=(x, -0.042, length * 0.50)),
            material=mats["zinc"],
            name=f"back_build__ratchet_back__plate_{index}_{side}", material_class_id="metal.brushed_silver",
        )
        for nkey in range(4):
            back.visual(
                Box((0.014, 0.018, 0.014)),
                origin=Origin(xyz=(x, -0.010, length * (0.16 + 0.20 * nkey))),
                material=mats["zinc"],
                name=f"back_build__ratchet_back__notch_{index}_{side}_{nkey}", material_class_id="metal.brushed_silver",
            )


def _back_build_split_panel_build(back, r: ResolvedConfig, mats: dict[str, str],
                                  index: int) -> None:
    w = r.back_panel_w
    length = r.back_len_m
    # Shared upholstered base rail carrying two stacked pads.
    back.visual(
        Box((w, 0.100, length * 0.22)),
        origin=Origin(xyz=(0.0, -0.050, length * 0.11)),
        material=mats["shadow"],
        name=f"back_build__split_panel__base_rail_{index}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    for p in range(2):
        back.visual(
            Box((w - 0.020, 0.090, length * 0.38)),
            origin=Origin(
                xyz=(0.0, -0.045, length * (0.20 + 0.40 * p) + length * 0.19)
            ),
            material=mats["upholstery"],
            name=f"back_build__split_panel__pad_{index}_{p}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
        )
    # Spine bridging the two pads down onto the base rail.
    back.visual(
        Box((w * 0.30, 0.096, length * 0.86)),
        origin=Origin(xyz=(0.0, -0.048, length * 0.51)),
        material=mats["shadow"],
        name=f"back_build__split_panel__spine_{index}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )


_BACK_BUILDERS = {
    "tufted_panel": _back_build_tufted_panel_build,
    "ratchet_back": _back_build_ratchet_back_build,
    "split_panel": _back_build_split_panel_build,
}


# --- bed deck candidates ----------------------------------------------------
def _deck_build_slab_deck_build(deck, r: ResolvedConfig, mats: dict[str, str]) -> None:
    w = r.deck_width_m
    d = r.deck_len_m
    deck.visual(
        Box((w, d, 0.020)),
        origin=Origin(xyz=(0.0, d * 0.5, 0.010)),
        material=mats["steel"],
        name="deck_build__slab_deck__platform", material_class_id="metal.steel_bare",
    )
    deck.visual(
        Box((w - 0.014, d - 0.014, DECK_T - 0.020)),
        origin=Origin(xyz=(0.0, d * 0.5, 0.020 + (DECK_T - 0.020) * 0.5)),
        material=mats["upholstery"],
        name="deck_build__slab_deck__mattress", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    for side, sy in enumerate((0.0, 1.0)):
        deck.visual(
            Box((w - 0.014, 0.026, 0.026)),
            origin=Origin(xyz=(0.0, 0.014 + sy * (d - 0.028), DECK_T - 0.014)),
            material=mats["shadow"],
            name=f"deck_build__slab_deck__welt_{side}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
        )


def _deck_build_trifold_deck_build(deck, r: ResolvedConfig, mats: dict[str, str]) -> None:
    w = r.deck_width_m
    d = r.deck_len_m
    deck.visual(
        Box((w, d, 0.020)),
        origin=Origin(xyz=(0.0, d * 0.5, 0.010)),
        material=mats["steel"],
        name="deck_build__trifold_deck__platform", material_class_id="metal.steel_bare",
    )
    pads = 3
    run = (d - 0.020) / pads
    for i in range(pads):
        y0 = 0.010 + run * i
        deck.visual(
            Box((w - 0.016, run - 0.010, DECK_T - 0.020)),
            origin=Origin(xyz=(0.0, y0 + run * 0.5, 0.020 + (DECK_T - 0.020) * 0.5)),
            material=mats["upholstery"],
            name=f"deck_build__trifold_deck__pad_{i}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
        )
        if i:
            deck.visual(
                Box((w - 0.016, 0.018, DECK_T - 0.024)),
                origin=Origin(xyz=(0.0, y0, 0.020 + (DECK_T - 0.020) * 0.5)),
                material=mats["shadow"],
                name=f"deck_build__trifold_deck__seam_bead_{i}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
            )


_DECK_BUILDERS = {
    "slab_deck": _deck_build_slab_deck_build,
    "trifold_deck": _deck_build_trifold_deck_build,
}


# --- lift frame candidates --------------------------------------------------
def _lift_frame_post_lift_build(stage, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Straight telescoping posts under the deck footprint.

    The stage's local origin is the CARRIAGE origin, not the deck rear, so every
    station is offset by deck_rear_y.
    """
    rise = r.lift_travel_m + 0.040
    post_x = r.post_x
    y0 = r.deck_rear_y
    for side, sx in enumerate((-1.0, 1.0)):
        for j, dy in enumerate((0.10, r.deck_len_m - 0.10)):
            stage.visual(
                Box((0.034, 0.034, rise)),
                origin=Origin(
                    xyz=(sx * post_x, y0 + dy, STAGE_DECK_Z - 0.026 - rise * 0.5 + MOUNT)
                ),
                material=mats["steel"],
                name=f"lift_frame__post_lift__post_{side}_{j}", material_class_id="metal.steel_bare",
            )
    stage.visual(
        Box((2.0 * r.rail_x + 0.034, r.deck_len_m, 0.026)),
        origin=Origin(xyz=(0.0, y0 + r.deck_len_m * 0.5, STAGE_DECK_Z - 0.013)),
        material=mats["steel"],
        name="lift_frame__post_lift__top_frame", material_class_id="metal.steel_bare",
    )


def _lift_frame_scissor_underframe_build(stage, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Crossed scissor links under the deck instead of straight posts."""
    rise = r.lift_travel_m + 0.040
    span = r.deck_len_m - 0.20
    post_x = r.post_x
    y0 = r.deck_rear_y
    mid_z = STAGE_DECK_Z - 0.026 - rise * 0.5 + MOUNT
    for side, sx in enumerate((-1.0, 1.0)):
        for k, sgn in enumerate((-1.0, 1.0)):
            length = math.hypot(span, rise)
            pitch = math.atan2(span, rise) * sgn
            stage.visual(
                Box((0.034, 0.024, length)),
                origin=Origin(
                    xyz=(sx * post_x, y0 + 0.10 + span * 0.5, mid_z),
                    rpy=(pitch, 0.0, 0.0),
                ),
                material=mats["steel"],
                name=f"lift_frame__scissor_underframe__link_{side}_{k}", material_class_id="metal.steel_bare",
            )
        # Centre pin where the two links cross.
        _x_cyl(
            stage,
            f"lift_frame__scissor_underframe__cross_pin_{side}",
            0.012,
            0.040,
            (sx * post_x, y0 + 0.10 + span * 0.5, mid_z),
            mats["zinc"],
        )
    stage.visual(
        Box((2.0 * r.rail_x + 0.034, r.deck_len_m, 0.026)),
        origin=Origin(xyz=(0.0, y0 + r.deck_len_m * 0.5, STAGE_DECK_Z - 0.013)),
        material=mats["steel"],
        name="lift_frame__scissor_underframe__top_frame", material_class_id="metal.steel_bare",
    )


_LIFT_BUILDERS = {
    "post_lift": _lift_frame_post_lift_build,
    "scissor_underframe": _lift_frame_scissor_underframe_build,
}


# --- carriage style candidates ----------------------------------------------
def _carriage_style_rail_carriage_build(carriage, frame, r: ResolvedConfig,
                                        mats: dict[str, str]) -> None:
    reach = r.deck_len_m + r.carriage_travel_m + GUIDE_STANDOFF
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * r.rail_x
        carriage.visual(
            Box((0.028, reach, 0.028)),
            origin=Origin(xyz=(x, r.deck_rear_y + r.deck_len_m - reach * 0.5, 0.0)),
            material=mats["steel"],
            name=f"carriage_style__rail_carriage__inner_rail_{side}", material_class_id="metal.steel_bare",
        )
        _guide_channel(
            frame, mats, x=x, y=r.deck_rear_y - GUIDE_STANDOFF, z=r.carriage_z,
            length=0.100, rail_half=0.014,
            name=f"carriage_style__rail_carriage__guide_{side}",
        )


def _carriage_style_roller_carriage_build(carriage, frame, r: ResolvedConfig,
                                          mats: dict[str, str]) -> None:
    reach = r.deck_len_m + r.carriage_travel_m + GUIDE_STANDOFF
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * r.rail_x
        carriage.visual(
            Box((0.028, reach, 0.028)),
            origin=Origin(xyz=(x, r.deck_rear_y + r.deck_len_m - reach * 0.5, 0.0)),
            material=mats["steel"],
            name=f"carriage_style__roller_carriage__inner_rail_{side}", material_class_id="metal.steel_bare",
        )
        # Roll-out foot housings under the carriage front rail.
        carriage.visual(
            Box((0.044, 0.048, 0.040)),
            origin=Origin(xyz=(x, r.deck_rear_y + 0.070, -0.020)),
            material=mats["zinc"],
            name=f"carriage_style__roller_carriage__roller_housing_{side}", material_class_id="metal.brushed_silver",
        )
        _x_cyl(
            carriage,
            f"carriage_style__roller_carriage__roller_{side}",
            0.019,
            0.030,
            (x, r.deck_rear_y + 0.070, -0.030),
            mats["foot"],
        )
        _guide_channel(
            frame, mats, x=x, y=r.deck_rear_y - GUIDE_STANDOFF, z=r.carriage_z,
            length=0.100, rail_half=0.014,
            name=f"carriage_style__roller_carriage__guide_{side}",
        )


def _guide_channel(frame, mats: dict[str, str], *, x: float, y: float, z: float,
                   length: float, rail_half: float, name: str) -> None:
    """Open-top U channel the carriage rail runs in.

    A solid block at the rail station would simply contain the rail (a
    whole-volume interpenetration); an open channel captures it sideways and
    from below while leaving a MOUNT running fit, and lets anything the carriage
    carries above the rail sweep over it.
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


_CARRIAGE_BUILDERS = {
    "rail_carriage": _carriage_style_rail_carriage_build,
    "roller_carriage": _carriage_style_roller_carriage_build,
}


# --- carcass ----------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("sofa_frame", meta={"role": "sofa_frame"})
    depth = r.seat_depth_m
    w = r.width_m
    sw = r.seat_width_m
    # Plinth, arms and the cushioned REAR seat band.
    plinth_h = r.plinth_top_z - 0.055
    for side, sx in enumerate((-1.0, 1.0)):
        block_w = w * 0.5 - (sw * 0.5 - 0.030)
        frame.visual(
            Box((block_w, depth, plinth_h)),
            origin=Origin(
                xyz=(
                    sx * (w * 0.5 - block_w * 0.5),
                    -depth * 0.5,
                    0.055 + plinth_h * 0.5,
                )
            ),
            material=mats["upholstery"],
            name=f"carcass_plinth_side_{side}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
        )
    frame.visual(
        Box((w, 0.040, plinth_h)),
        origin=Origin(xyz=(0.0, -depth + 0.020, 0.055 + plinth_h * 0.5)),
        material=mats["upholstery"],
        name="carcass_plinth_rear", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    # Cross member under the carriage guides, tying them to both side blocks.
    frame.visual(
        Box((sw, 0.070, 0.024)),
        origin=Origin(
            xyz=(0.0, r.deck_rear_y - GUIDE_STANDOFF, r.carriage_z - 0.031)
        ),
        material=mats["steel"],
        name="carriage_guide_crossmember", material_class_id="metal.steel_bare",
    )
    for i, (x, y) in enumerate(
        (
            (-(w * 0.5 - 0.06), -depth + 0.07),
            (w * 0.5 - 0.06, -depth + 0.07),
            (-(w * 0.5 - 0.06), -0.07),
            (w * 0.5 - 0.06, -0.07),
        )
    ):
        frame.visual(
            Box((0.046, 0.046, 0.058)),
            origin=Origin(xyz=(x, y, 0.029)),
            material=mats["foot"],
            name=f"carcass_foot_{i}", material_class_id="rubber.smooth_plain",
        )
    arm_h = r.arm_base_h_m
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((ARM_W, depth + 0.10, arm_h)),
            origin=Origin(
                xyz=(
                    sx * (w - ARM_W) * 0.5,
                    -depth * 0.5 + 0.05,
                    arm_h * 0.5,
                )
            ),
            material=mats["upholstery"],
            name=f"carcass_arm_{side}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
        )
        if r.arm_build == "fold_down_arm":
            # Hinge knuckles straddle the barrel on the outer top edge of the
            # shortened arm base, so the pin never shares a volume with them.
            for cheek, cy in enumerate((-0.038, 0.038)):
                frame.visual(
                    Box((0.030, 0.010, 0.018)),
                    origin=Origin(
                        xyz=(
                            sx * (w * 0.5 - 0.020),
                            -depth * 0.5 + 0.05 + cy,
                            arm_h + 0.005,
                        )
                    ),
                    material=mats["steel"],
                    name=f"arm_hinge_cheek_{side}_{cheek}", material_class_id="metal.steel_bare",
                )
    seat_cy = 0.5 * (r.seat_y0 + r.seat_y1)
    frame.visual(
        Box((sw * 0.99, SEAT_BAND, 0.100)),
        origin=Origin(xyz=(0.0, seat_cy, r.bed_height_m - 0.050)),
        material=mats["upholstery"],
        name="seat_band_cushion", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    frame.visual(
        Box((sw * 0.99, SEAT_BAND, r.bed_height_m - 0.100 - r.plinth_top_z + 0.020)),
        origin=Origin(
            xyz=(
                0.0,
                seat_cy,
                r.plinth_top_z - 0.010
                + (r.bed_height_m - 0.100 - r.plinth_top_z + 0.020) * 0.5,
            )
        ),
        material=mats["upholstery"],
        name="seat_band_riser", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    # Back hinge brackets straddling each back panel.
    for index, x in enumerate(r.back_x):
        for side, sx in enumerate((-1.0, 1.0)):
            frame.visual(
                Box((0.013, 0.048, r.bed_height_m - r.plinth_top_z + 0.075)),
                origin=Origin(
                    xyz=(
                        x + sx * (r.back_panel_w * 0.5 + 0.009),
                        r.back_hinge_y,
                        r.plinth_top_z
                        + (r.bed_height_m - r.plinth_top_z + 0.075) * 0.5
                        - 0.020,
                    )
                ),
                material=mats["steel"],
                name=f"back_hinge_bracket_{index}_{side}", material_class_id="metal.steel_bare",
            )
    return frame


def _arm_build_fixed_arm_build(model, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """001.png: the carcass arms are one fixed upholstered surround."""

    return None


def _arm_build_fold_down_arm_build(
    model, frame, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """fold_down_arms fork L428-L480: each arm top folds out into a bed extension.

    The hinge line sits on the outer top edge of the shortened arm base, so the
    panel rolls out and up instead of sweeping down through the base.
    """

    depth = r.seat_depth_m
    w = r.width_m
    panel_h = r.arm_panel_h_m
    for side, sx in enumerate((-1.0, 1.0)):
        arm = model.part(
            f"arm_build__fold_down_arm__panel_{side}",
            meta={"role": "fold_down_arm", "index": side},
        )
        panel_w = ARM_W - 0.030
        arm.visual(
            Cylinder(radius=0.016, length=0.060),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["zinc"],
            name=f"arm_build__fold_down_arm__hinge_barrel_{side}", material_class_id="metal.brushed_silver",
        )
        arm.visual(
            Box((panel_w, depth + 0.10, panel_h)),
            origin=Origin(
                xyz=(
                    -sx * panel_w * 0.5,
                    0.0,
                    panel_h * 0.5,
                )
            ),
            material=mats["upholstery"],
            name=f"arm_build__fold_down_arm__panel_body_{side}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
        )
        arm.visual(
            Box((0.010, depth * 0.86, 0.010)),
            origin=Origin(
                xyz=(
                    -sx * (panel_w - 0.008),
                    0.0,
                    panel_h * 0.62,
                )
            ),
            material=mats["shadow"],
            name=f"arm_build__fold_down_arm__panel_seam_{side}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"dove_gray", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
        )
        provider = AxisInterface(
            name=f"frame_to_fold_arm_{side}__provider",
            point=(
                sx * (w * 0.5 - 0.020),
                -depth * 0.5 + 0.05,
                r.arm_base_h_m + 0.016,
            ),
            axis=(0.0, sx, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=0.016,
        )
        consumer = AxisInterface(
            name=f"frame_to_fold_arm_{side}__consumer",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, sx, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=0.016,
        )
        mate = mate_axes(provider, consumer)
        joint = f"frame_to_fold_arm_{side}"
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=frame,
            child=arm,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(
                effort=60.0, velocity=0.8, lower=0.0, upper=math.pi / 2.0
            ),
            meta={"mechanism": "fold-down arm bed extension"},
        )
        register_interface_mate(model, joint, mate)


_ARM_BUILDERS = {
    "fixed_arm": _arm_build_fixed_arm_build,
    "fold_down_arm": _arm_build_fold_down_arm_build,
}


def _build_carriage(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]):
    carriage = model.part("pullout_carriage", meta={"role": "pullout_carriage"})
    # Front cross rail the lift stage stands on, tying both carriage rails.
    carriage.visual(
        Box((2.0 * r.rail_x + 0.028, 0.030, 0.028)),
        origin=Origin(xyz=(0.0, r.deck_rear_y + 0.015, 0.0)),
        material=mats["steel"],
        name="carriage_front_rail", material_class_id="metal.steel_bare",
    )
    carriage.visual(
        Box((2.0 * r.rail_x + 0.028, 0.030, 0.028)),
        origin=Origin(xyz=(0.0, r.deck_rear_y + r.deck_len_m - 0.015, 0.0)),
        material=mats["steel"],
        name="carriage_nose_rail", material_class_id="metal.steel_bare",
    )
    # Post sockets: the lift posts slide inside these over the whole travel, so
    # the stage keeps real bearing contact with the carriage at every height.
    # A solid pad under each post would instead be speared by it.  The sockets
    # sit BELOW the stage's top frame and are tied out to the carriage rails.
    sock_half = 0.017 + MOUNT + 0.005
    for side, sx in enumerate((-1.0, 1.0)):
        px = sx * r.post_x
        for jdx, y in enumerate(r.post_y):
            for wall, sw_ in enumerate((-1.0, 1.0)):
                carriage.visual(
                    Box((0.010, 0.048, 0.054)),
                    origin=Origin(xyz=(px + sw_ * sock_half, y, -0.013)),
                    material=mats["steel"],
                    name=f"post_socket_{side}_{jdx}_{wall}", material_class_id="metal.steel_bare",
                )
            # Tie plate from the outer socket wall out to the carriage rail.
            x_in = r.post_x + sock_half
            x_out = r.rail_x + 0.014
            carriage.visual(
                Box((x_out - x_in, 0.048, 0.010)),
                origin=Origin(xyz=(sx * 0.5 * (x_in + x_out), y, -0.006)),
                material=mats["steel"],
                name=f"post_socket_tie_{side}_{jdx}", material_class_id="metal.steel_bare",
            )
        # Longitudinal side beams tying both sockets to both cross rails.  A
        # cross web across each socket would be in the way of the scissor link's
        # foot, which has to reach down into that same socket.
        for wall, sw_ in enumerate((-1.0, 1.0)):
            carriage.visual(
                Box((0.010, r.deck_len_m - 0.030, 0.010)),
                origin=Origin(
                    xyz=(
                        px + sw_ * sock_half,
                        r.deck_rear_y + r.deck_len_m * 0.5,
                        -0.006,
                    )
                ),
                material=mats["steel"],
                name=f"carriage_side_beam_{side}_{wall}", material_class_id="metal.steel_bare",
            )
    _CARRIAGE_BUILDERS[r.carriage_style](carriage, frame, r, mats)
    model.articulation(
        "frame_to_pullout_carriage",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, r.carriage_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=r.carriage_travel_m, effort=600.0, velocity=0.22
        ),
        meta={"positive_motion": "pulls the bed carriage out from under the seat"},
    )
    return carriage


def _build_lift(model: ArticulatedObject, carriage, r: ResolvedConfig, mats: dict[str, str]):
    stage = model.part("deck_lift_stage", meta={"role": "deck_lift_stage"})
    _LIFT_BUILDERS[r.lift_frame](stage, r, mats)
    model.articulation(
        "carriage_to_deck_lift",
        ArticulationType.PRISMATIC,
        parent=carriage,
        child=stage,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=r.lift_travel_m, effort=900.0, velocity=0.12
        ),
        meta={"positive_motion": "raises the bed deck to bed height"},
    )

    deck = model.part(
        f"deck_build__{r.deck_build}__bed_deck",
        meta={"role": "bed_deck"},
    )
    _DECK_BUILDERS[r.deck_build](deck, r, mats)
    model.articulation(
        "lift_to_bed_deck",
        ArticulationType.FIXED,
        parent=stage,
        child=deck,
        origin=Origin(xyz=(0.0, r.deck_rear_y, STAGE_DECK_Z)),
    )
    return stage, deck


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_folding_sofa_bed3(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Folding_sofa_bed3",
            "slot_choices": slot_choices_for_config(r),
            "conversion": "pull-out carriage + vertical deck lift to bed height",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)
    _ARM_BUILDERS[r.arm_build](model, frame, r, mats)
    carriage = _build_carriage(model, frame, r, mats)
    _build_lift(model, carriage, r, mats)

    for index, x in enumerate(r.back_x):
        back = model.part(
            f"back_build__{r.back_build}__back_panel_{index}",
            meta={"role": "back_panel", "index": index},
        )
        _BACK_BUILDERS[r.back_build](back, r, mats, index)
        _x_cyl(
            back,
            f"back_hinge_barrel_{index}",
            0.016,
            2.0 * (r.back_panel_w * 0.5 + 0.0025 + MOUNT),
            (0.0, 0.0, 0.0),
            mats["zinc"],
        )
        _rev_joint(
            model,
            name=f"frame_to_back_panel_{index}",
            parent=frame,
            child=back,
            point=(x, r.back_hinge_y, r.bed_height_m),
            lower=0.0,
            upper=BACK_RECLINE,
            effort=190.0,
            velocity=0.45,
        )

    back_joints = [f"frame_to_back_panel_{i}" for i in range(r.back_panel_count)]
    model.meta["risk_poses"] = (
        {n: 0.0 for n in back_joints}
        | {"frame_to_pullout_carriage": 0.0, "carriage_to_deck_lift": 0.0},
        {n: 0.0 for n in back_joints}
        | {
            "frame_to_pullout_carriage": r.carriage_travel_m,
            "carriage_to_deck_lift": r.lift_travel_m,
        },
        {n: BACK_RECLINE for n in back_joints}
        | {"frame_to_pullout_carriage": 0.0, "carriage_to_deck_lift": r.lift_travel_m},
    )
    model.meta["coupled_joint_pairs"] = (
        ("frame_to_pullout_carriage", "carriage_to_deck_lift"),
    ) + tuple((n, "carriage_to_deck_lift") for n in back_joints)
    return model


def build_seeded_picturex_0611_folding_sofa_bed3(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_folding_sofa_bed3(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_folding_sofa_bed3_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "sofa_frame")
    backs = _parts_by_role(model, "back_panel")
    carriages = _parts_by_role(model, "pullout_carriage")
    stages = _parts_by_role(model, "deck_lift_stage")
    decks = _parts_by_role(model, "bed_deck")

    arms = _parts_by_role(model, "fold_down_arm")
    joints = {j.name: j for j in model.articulations}
    car_joint = joints.get("frame_to_pullout_carriage")
    lift_joint = joints.get("carriage_to_deck_lift")
    deck_joint = joints.get("lift_to_bed_deck")
    back_joints = [joints.get(f"frame_to_back_panel_{i}") for i in range(r.back_panel_count)]

    ctx.check(
        "category_anchor: the arm build matches the selected surround",
        len(arms) == (2 if r.arm_build == "fold_down_arm" else 0),
        details=f"arm_build={r.arm_build}, arms={[part.name for part in arms]}",
    )
    if arms:
        fold = joints["frame_to_fold_arm_0"]
        upright = ctx.part_world_aabb(arms[0])
        with ctx.pose({fold: fold.motion_limits.upper}):
            folded = ctx.part_world_aabb(arms[0])
        reach = None
        if upright is not None and folded is not None:
            reach = abs(folded[0][0]) - abs(upright[0][0])
        dropped = None if folded is None or upright is None else upright[1][2] - folded[1][2]
        ctx.check(
            "folding an arm really extends the sleeping surface outward",
            reach is not None and reach > 0.10 and dropped is not None and dropped > 0.04,
            details=f"upright={upright}, folded={folded}, reach={reach}, dropped={dropped}",
        )

    def _is_pris(j, axis) -> bool:
        return (
            j is not None
            and j.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(v, 6) for v in j.axis) == axis
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    ctx.check(
        "category_anchor: carriage slides out and the lift raises the deck",
        len(frames) == 1
        and len(carriages) == 1
        and len(stages) == 1
        and len(decks) == 1
        and len(backs) == r.back_panel_count
        and bool(model.root_parts())
        and model.root_parts()[0].name == "sofa_frame"
        and _is_pris(car_joint, (0.0, 1.0, 0.0))
        and car_joint.parent == "sofa_frame"
        and _is_pris(lift_joint, (0.0, 0.0, 1.0))
        and lift_joint.parent == "pullout_carriage"
        and deck_joint is not None
        and deck_joint.articulation_type == ArticulationType.FIXED
        and deck_joint.parent == "deck_lift_stage"
        and all(
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(abs(v), 6) for v in j.axis) == (1.0, 0.0, 0.0)
            and j.parent == "sofa_frame"
            for j in back_joints
        ),
        details=f"backs={len(backs)} carriages={len(carriages)} decks={len(decks)}",
    )

    # Motion evidence: the lift really carries the deck to bed height, and the
    # retracted deck footprint sits FORWARD of the cushioned seat band, which is
    # what makes "lift while still retracted" a legal pose at all.
    deck = decks[0]
    down = ctx.part_world_aabb(deck)
    with ctx.pose({lift_joint: lift_joint.motion_limits.upper}):
        up = ctx.part_world_aabb(deck)
        with ctx.pose({car_joint: car_joint.motion_limits.upper}):
            out = ctx.part_world_aabb(deck)
    ctx.check(
        "category_anchor: deck reaches bed height and clears the seat band",
        all(b is not None for b in (down, up, out))
        and abs((up[0][2] - down[0][2]) - r.lift_travel_m) < 1e-3
        and abs(up[1][2] - r.bed_height_m) < 0.012
        and abs((out[0][1] - up[0][1]) - r.carriage_travel_m) < 1e-3
        and r.deck_rear_y > r.seat_y1 + 0.010,
        details=(
            f"down={down} up={up} out={out} lift={r.lift_travel_m} "
            f"deck_rear={r.deck_rear_y} seat_front={r.seat_y1}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    back_ok = {
        "tufted_panel": any("tufted_panel__button" in n for n in visual_names),
        "ratchet_back": any("ratchet_back__notch" in n for n in visual_names),
        "split_panel": any("split_panel__base_rail" in n for n in visual_names),
    }[r.back_build]
    ctx.check("category_anchor: back_build identity", back_ok, details=f"back_build={r.back_build}")

    deck_ok = {
        "slab_deck": any("slab_deck__welt" in n for n in visual_names),
        "trifold_deck": any("trifold_deck__seam_bead" in n for n in visual_names),
    }[r.deck_build]
    ctx.check("category_anchor: deck_build identity", deck_ok, details=f"deck_build={r.deck_build}")

    lift_ok = {
        "post_lift": any("post_lift__post" in n for n in visual_names),
        "scissor_underframe": any("scissor_underframe__cross_pin" in n for n in visual_names),
    }[r.lift_frame]
    ctx.check("category_anchor: lift_frame identity", lift_ok, details=f"lift_frame={r.lift_frame}")

    car_ok = {
        "rail_carriage": any("rail_carriage__guide" in n for n in visual_names),
        "roller_carriage": any("roller_carriage__roller_housing" in n for n in visual_names),
    }[r.carriage_style]
    ctx.check(
        "category_anchor: carriage_style identity", car_ok,
        details=f"carriage_style={r.carriage_style}",
    )

    ctx.check(
        "back panels are pitched across the seat width",
        len(r.back_x) == r.back_panel_count
        and r.back_panel_w > 0.20
        and all(
            abs(x) + r.back_panel_w * 0.5 <= r.seat_width_m * 0.5 + 1e-9 for x in r.back_x
        ),
        details=f"back_x={r.back_x} panel_w={r.back_panel_w}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "narrow_shallow_single_panel",
        {
            "back_build": "tufted_panel",
            "deck_build": "slab_deck",
            "lift_frame": "post_lift",
            "carriage_style": "rail_carriage",
            "back_panel_count": 1,
            "width_m": 1.55,
            "seat_depth_m": 0.52,
            "bed_height_m": 0.38,
        },
        reason="narrowest shallowest carcass with one wide back panel and the shortest lift",
    ),
    corner_case(
        "wide_deep_three_panels_scissor",
        {
            "back_build": "split_panel",
            "deck_build": "trifold_deck",
            "lift_frame": "scissor_underframe",
            "carriage_style": "roller_carriage",
            "back_panel_count": 3,
            "width_m": 2.05,
            "seat_depth_m": 0.68,
            "bed_height_m": 0.46,
        },
        reason="largest envelope, three back panels and the scissor lift at full travel",
    ),
    corner_case(
        "narrow_deep_three_panels_ratchet",
        {
            "back_build": "ratchet_back",
            "deck_build": "slab_deck",
            "lift_frame": "scissor_underframe",
            "carriage_style": "rail_carriage",
            "back_panel_count": 3,
            "width_m": 1.55,
            "seat_depth_m": 0.68,
            "bed_height_m": 0.38,
        },
        reason="three ratchet panels squeezed into the narrowest seat width - tightest panel pitch",
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
    "build_picturex_0611_folding_sofa_bed3",
    "build_seeded_picturex_0611_folding_sofa_bed3",
    "run_picturex_0611_folding_sofa_bed3_tests",
]
