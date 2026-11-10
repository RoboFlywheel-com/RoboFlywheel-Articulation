# SPDX-License-Identifier: Apache-2.0

"""Self-contained reclining convertible sofa template.

One rigid ``sofa_frame`` root carries the carcass, the fixed arms, the seat
decks and every hinge bracket.  Each of ``seat_count`` seat units contributes:

* a ``seat_back`` -- a REVOLUTE (+x) child of the frame that reclines rearward
  into free space behind the sofa;
* a ``legrest`` -- a REVOLUTE (+x) child of the frame that hangs stowed in front
  of the plinth and swings UP and forward to seat level.

Both are independent joints and both sweep only into free space, so every
single-joint boundary pose is genuinely clear rather than only the two showroom
configurations.  A ``recline_control`` knob turns on the outer arm.

Four component slots vary without touching the mechanism: ``back_build``,
``base_style``, ``deck_build`` and ``legrest_style``.  No source-replay import,
no motion clamping, no whole-part overlap allowance.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

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
    component_slot,
    corner_case,
    mate_axes,
    multiplicity_slot,
    register_interface_mate,
)

BackBuild = Literal["single_back", "split_ratchet", "bifold_panels"]
BaseStyle = Literal["plinth_base", "metal_futon", "storage_base"]
DeckBuild = Literal["upholstered_deck", "slatted_deck"]
LegrestStyle = Literal["pad_legrest", "chaise_legrest"]
PaletteStyle = Literal["warm_gray", "navy_linen", "camel_leather", "sage_weave"]

BACK_BUILDS: tuple[BackBuild, ...] = ("single_back", "split_ratchet", "bifold_panels")
BASE_STYLES: tuple[BaseStyle, ...] = ("plinth_base", "metal_futon", "storage_base")
DECK_BUILDS: tuple[DeckBuild, ...] = ("upholstered_deck", "slatted_deck")
LEGREST_STYLES: tuple[LegrestStyle, ...] = ("pad_legrest", "chaise_legrest")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("warm_gray", "navy_linen", "camel_leather", "sage_weave")


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("back_build", BACK_BUILDS),
        component_slot("base_style", BASE_STYLES),
        component_slot("deck_build", DECK_BUILDS),
        component_slot("legrest_style", LEGREST_STYLES),
        multiplicity_slot("seat_count", (1, 2, 3), item_slot="back_build"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_gray": {
        "upholstery": (0.68, 0.67, 0.65, 1.0),
        "shadow": (0.52, 0.51, 0.50, 1.0),
        "steel": (0.30, 0.31, 0.32, 1.0),
        "zinc": (0.62, 0.65, 0.67, 1.0),
        "foot": (0.08, 0.08, 0.08, 1.0),
    },
    "navy_linen": {
        "upholstery": (0.18, 0.23, 0.35, 1.0),
        "shadow": (0.12, 0.16, 0.25, 1.0),
        "steel": (0.24, 0.26, 0.30, 1.0),
        "zinc": (0.58, 0.61, 0.65, 1.0),
        "foot": (0.06, 0.06, 0.07, 1.0),
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
CUSHION_T = 0.10         # seat cushion thickness
BACK_RECLINE = 0.55      # backrest travel, rad
LEG_TRAVEL = math.pi / 2.0
# Sub-millimetre lap: a fitting laps its host by less than the collision
# tolerance so QC reads real contact without an overlap allowance.
MOUNT = 0.0006


@dataclass(frozen=True)
class Config:
    back_build: BackBuild = "single_back"
    base_style: BaseStyle = "plinth_base"
    deck_build: DeckBuild = "upholstered_deck"
    legrest_style: LegrestStyle = "pad_legrest"
    seat_count: int = 2
    seat_width_m: float | None = None
    seat_depth_m: float | None = None
    seat_height_m: float | None = None
    palette_style: PaletteStyle = "warm_gray"
    name: str = "pictureX_0611_Folding_sofa_bed2"


@dataclass(frozen=True)
class ResolvedConfig:
    back_build: BackBuild
    base_style: BaseStyle
    deck_build: DeckBuild
    legrest_style: LegrestStyle
    seat_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    seat_width_m: float
    seat_depth_m: float
    seat_height_m: float
    total_width_m: float
    seat_x: tuple[float, ...]
    plinth_top_z: float
    back_hinge_y: float
    back_len_m: float
    leg_hinge_y: float
    leg_hinge_z: float
    leg_len_m: float
    control_x: float
    control_z: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x50FA_0BE2)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        back_build=choices["back_build"],
        base_style=choices["base_style"],
        deck_build=choices["deck_build"],
        legrest_style=choices["legrest_style"],
        seat_count=choices["seat_count"],
        seat_width_m=round(rng.uniform(0.52, 0.74), 4),
        seat_depth_m=round(rng.uniform(0.52, 0.68), 4),
        seat_height_m=round(rng.uniform(0.38, 0.46), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"folding_sofa_bed2_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "back_build": config.back_build,
            "base_style": config.base_style,
            "deck_build": config.deck_build,
            "legrest_style": config.legrest_style,
            "seat_count": config.seat_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.seat_width_m is not None and not 0.52 <= float(config.seat_width_m) <= 0.74:
        raise ValueError("seat_width_m must be in [0.52, 0.74]")
    if config.seat_depth_m is not None and not 0.52 <= float(config.seat_depth_m) <= 0.68:
        raise ValueError("seat_depth_m must be in [0.52, 0.68]")
    if config.seat_height_m is not None and not 0.38 <= float(config.seat_height_m) <= 0.46:
        raise ValueError("seat_height_m must be in [0.38, 0.46]")

    sw = _clamp(config.seat_width_m, 0.52, 0.74) if config.seat_width_m is not None else 0.62
    depth = _clamp(config.seat_depth_m, 0.52, 0.68) if config.seat_depth_m is not None else 0.60
    height = _clamp(config.seat_height_m, 0.38, 0.46) if config.seat_height_m is not None else 0.42

    n = int(config.seat_count)
    total = n * sw + 2.0 * ARM_W
    xs = tuple(-(n - 1) * 0.5 * sw + sw * i for i in range(n))

    plinth_top = height - CUSHION_T
    back_hinge_y = -depth + 0.026
    back_len = min(0.50, depth * 0.80)
    leg_hinge_y = 0.055
    leg_hinge_z = plinth_top - 0.030
    leg_len = leg_hinge_z - 0.050
    control_x = total * 0.5 + 0.002
    control_z = height + 0.055

    return ResolvedConfig(
        back_build=config.back_build,
        base_style=config.base_style,
        deck_build=config.deck_build,
        legrest_style=config.legrest_style,
        seat_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        seat_width_m=sw,
        seat_depth_m=depth,
        seat_height_m=height,
        total_width_m=total,
        seat_x=xs,
        plinth_top_z=plinth_top,
        back_hinge_y=back_hinge_y,
        back_len_m=back_len,
        leg_hinge_y=leg_hinge_y,
        leg_hinge_z=leg_hinge_z,
        leg_len_m=leg_len,
        control_x=control_x,
        control_z=control_z,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("back_build", config.back_build),
        ("base_style", config.base_style),
        ("deck_build", config.deck_build),
        ("legrest_style", config.legrest_style),
        ("seat_count", config.seat_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"sb2_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"sb2_{r.palette_style}_{key}"
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
    axis: tuple[float, float, float],
    provider_radial: tuple[float, float, float],
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=provider_radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=provider_radial)
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


# --- base style candidates --------------------------------------------------
def _base_style_plinth_base_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    depth = r.seat_depth_m
    w = r.total_width_m
    frame.visual(
        Box((w, depth, r.plinth_top_z - 0.060)),
        origin=Origin(xyz=(0.0, -depth * 0.5, 0.060 + (r.plinth_top_z - 0.060) * 0.5)),
        material=mats["upholstery"],
        name="base_style__plinth_base__plinth", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    # Recessed toe kick under the plinth front.
    frame.visual(
        Box((w - 0.040, depth - 0.040, 0.056)),
        origin=Origin(xyz=(0.0, -depth * 0.5, 0.032)),
        material=mats["shadow"],
        name="base_style__plinth_base__toe_kick", material_class_id="wood.painted_clean",
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
            Box((0.048, 0.048, 0.062)),
            origin=Origin(xyz=(x, y, 0.031)),
            material=mats["foot"],
            name=f"base_style__plinth_base__block_foot_{i}", material_class_id="rubber.smooth_plain",
        )


def _base_style_metal_futon_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    depth = r.seat_depth_m
    w = r.total_width_m
    rail_z = r.plinth_top_z - 0.030
    for side, sy in enumerate((-1.0, 1.0)):
        y = -depth * 0.5 + sy * (depth * 0.5 - 0.030)
        frame.visual(
            Box((w, 0.036, 0.036)),
            origin=Origin(xyz=(0.0, y, rail_z)),
            material=mats["steel"],
            name=f"base_style__metal_futon__side_rail_{side}", material_class_id="metal.steel_bare",
        )
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.036, depth - 0.060, 0.036)),
            origin=Origin(xyz=(sx * (w * 0.5 - 0.018), -depth * 0.5, rail_z)),
            material=mats["steel"],
            name=f"base_style__metal_futon__end_rail_{side}", material_class_id="metal.steel_bare",
        )
    # Splayed tube legs, the exposed-frame tell.
    for i, (x, y) in enumerate(
        (
            (-(w * 0.5 - 0.05), -depth + 0.06),
            (w * 0.5 - 0.05, -depth + 0.06),
            (-(w * 0.5 - 0.05), -0.06),
            (w * 0.5 - 0.05, -0.06),
        )
    ):
        frame.visual(
            Cylinder(radius=0.017, length=rail_z + 0.018),
            origin=Origin(xyz=(x, y, (rail_z + 0.018) * 0.5)),
            material=mats["steel"],
            name=f"base_style__metal_futon__tube_leg_{i}", material_class_id="metal.steel_bare",
        )
    # Deck panel spanning the rails: on an open frame the seat has nothing to
    # bed onto otherwise, and the whole seat build reads as an island.
    frame.visual(
        Box((w - 0.040, depth - 0.070, 0.022)),
        origin=Origin(xyz=(0.0, -depth * 0.5, r.plinth_top_z - 0.009)),
        material=mats["steel"],
        name="base_style__metal_futon__deck_panel", material_class_id="metal.steel_bare",
    )
    # Cross tie so the two side rails read as one welded frame.
    frame.visual(
        Box((w - 0.060, 0.030, 0.026)),
        origin=Origin(xyz=(0.0, -depth * 0.5, rail_z)),
        material=mats["steel"],
        name="base_style__metal_futon__cross_tie", material_class_id="metal.steel_bare",
    )


def _base_style_storage_base_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    depth = r.seat_depth_m
    w = r.total_width_m
    frame.visual(
        Box((w, depth, r.plinth_top_z)),
        origin=Origin(xyz=(0.0, -depth * 0.5, r.plinth_top_z * 0.5)),
        material=mats["upholstery"],
        name="base_style__storage_base__box", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    # Recessed front door panel with a pull.
    frame.visual(
        Box((w - 0.100, 0.014, r.plinth_top_z - 0.070)),
        origin=Origin(xyz=(0.0, 0.004, r.plinth_top_z * 0.5)),
        material=mats["shadow"],
        name="base_style__storage_base__door_panel", material_class_id="wood.painted_clean",
    )
    frame.visual(
        Box((0.120, 0.018, 0.020)),
        origin=Origin(xyz=(0.0, 0.010, r.plinth_top_z * 0.5 + 0.030)),
        material=mats["zinc"],
        name="base_style__storage_base__door_pull", material_class_id="metal.brushed_silver",
    )


_BASE_BUILDERS = {
    "plinth_base": _base_style_plinth_base_build,
    "metal_futon": _base_style_metal_futon_build,
    "storage_base": _base_style_storage_base_build,
}


# --- seat deck candidates ---------------------------------------------------
def _deck_build_upholstered_deck_build(frame, r: ResolvedConfig, mats: dict[str, str],
                                       index: int, x: float) -> None:
    depth = r.seat_depth_m
    sw = r.seat_width_m
    frame.visual(
        Box((sw - 0.020, depth - 0.092, CUSHION_T)),
        origin=Origin(
            xyz=(x, -depth * 0.5 + 0.016, r.plinth_top_z + CUSHION_T * 0.5 - MOUNT)
        ),
        material=mats["upholstery"],
        name=f"deck_build__upholstered_deck__cushion_{index}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    frame.visual(
        Box((sw - 0.020, 0.026, 0.026)),
        origin=Origin(xyz=(x, -0.040, r.seat_height_m - 0.014)),
        material=mats["shadow"],
        name=f"deck_build__upholstered_deck__welt_{index}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )


def _deck_build_slatted_deck_build(frame, r: ResolvedConfig, mats: dict[str, str],
                                   index: int, x: float) -> None:
    depth = r.seat_depth_m
    sw = r.seat_width_m
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.030, depth - 0.092, 0.030)),
            origin=Origin(
                xyz=(
                    x + sx * (sw * 0.5 - 0.020),
                    -depth * 0.5 + 0.016,
                    r.plinth_top_z + 0.002,
                )
            ),
            material=mats["steel"],
            name=f"deck_build__slatted_deck__bearer_{index}_{side}", material_class_id="metal.steel_bare",
        )
    slats = 5
    for i in range(slats):
        y = -depth + 0.086 + (depth - 0.156) * i / (slats - 1)
        frame.visual(
            Box((sw - 0.020, 0.034, 0.018)),
            origin=Origin(xyz=(x, y, r.plinth_top_z + 0.020)),
            material=mats["steel"],
            name=f"deck_build__slatted_deck__slat_{index}_{i}", material_class_id="metal.steel_bare",
        )
    frame.visual(
        Box((sw - 0.024, depth - 0.100, CUSHION_T - 0.036)),
        origin=Origin(
            xyz=(x, -depth * 0.5 + 0.020, r.plinth_top_z + 0.026 + (CUSHION_T - 0.036) * 0.5)
        ),
        material=mats["upholstery"],
        name=f"deck_build__slatted_deck__thin_pad_{index}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )


_DECK_BUILDERS = {
    "upholstered_deck": _deck_build_upholstered_deck_build,
    "slatted_deck": _deck_build_slatted_deck_build,
}


# --- backrest candidates ----------------------------------------------------
def _back_build_single_back_build(back, r: ResolvedConfig, mats: dict[str, str],
                                  index: int) -> None:
    w = r.seat_width_m - 0.030
    length = r.back_len_m
    back.visual(
        Box((w, 0.100, length)),
        origin=Origin(xyz=(0.0, -0.050, length * 0.5)),
        material=mats["upholstery"],
        name=f"back_build__single_back__pad_{index}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    back.visual(
        Box((w, 0.028, 0.028)),
        origin=Origin(xyz=(0.0, -0.050, length - 0.010)),
        material=mats["shadow"],
        name=f"back_build__single_back__piped_top_{index}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )


def _back_build_split_ratchet_build(back, r: ResolvedConfig, mats: dict[str, str],
                                    index: int) -> None:
    w = r.seat_width_m - 0.045
    length = r.back_len_m
    for p in range(2):
        z0 = length * 0.50 * p
        back.visual(
            Box((w, 0.094, length * 0.44)),
            origin=Origin(xyz=(0.0, -0.047, z0 + length * 0.22)),
            material=mats["upholstery"],
            name=f"back_build__split_ratchet__panel_{index}_{p}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
        )
    # Exposed side ratchet plates with stepped notches.
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * (w * 0.5 + 0.003)
        back.visual(
            Box((0.010, 0.086, length * 0.86)),
            origin=Origin(xyz=(x, -0.043, length * 0.50)),
            material=mats["zinc"],
            name=f"back_build__split_ratchet__plate_{index}_{side}", material_class_id="metal.brushed_silver",
        )
        for nkey in range(3):
            back.visual(
                Box((0.014, 0.018, 0.014)),
                origin=Origin(xyz=(x, -0.012, length * (0.16 + 0.24 * nkey))),
                material=mats["zinc"],
                name=f"back_build__split_ratchet__notch_{index}_{side}_{nkey}", material_class_id="metal.brushed_silver",
            )


def _back_build_bifold_panels_build(back, r: ResolvedConfig, mats: dict[str, str],
                                    index: int) -> None:
    w = r.seat_width_m - 0.030
    length = r.back_len_m
    for p in range(2):
        back.visual(
            Box((w, 0.092, length * 0.47)),
            origin=Origin(
                xyz=(0.0, -0.046, length * (0.03 + 0.49 * p) + length * 0.235)
            ),
            material=mats["upholstery"],
            name=f"back_build__bifold_panels__panel_{index}_{p}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
        )
    # Seam bead on the fold line between the two panels.
    back.visual(
        Box((w, 0.100, length * 0.08)),
        origin=Origin(xyz=(0.0, -0.046, length * 0.51)),
        material=mats["shadow"],
        name=f"back_build__bifold_panels__seam_bead_{index}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )


_BACK_BUILDERS = {
    "single_back": _back_build_single_back_build,
    "split_ratchet": _back_build_split_ratchet_build,
    "bifold_panels": _back_build_bifold_panels_build,
}


# --- legrest candidates -----------------------------------------------------
def _legrest_style_pad_legrest_build(leg, r: ResolvedConfig, mats: dict[str, str],
                                     index: int) -> None:
    w = r.seat_width_m - 0.040
    length = r.leg_len_m
    leg.visual(
        Box((w, 0.070, length)),
        origin=Origin(xyz=(0.0, 0.010, -length * 0.5)),
        material=mats["upholstery"],
        name=f"legrest_style__pad_legrest__pad_{index}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    leg.visual(
        Box((w, 0.026, 0.026)),
        origin=Origin(xyz=(0.0, 0.010, -length + 0.012)),
        material=mats["shadow"],
        name=f"legrest_style__pad_legrest__welt_{index}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )


def _legrest_style_chaise_legrest_build(leg, r: ResolvedConfig, mats: dict[str, str],
                                        index: int) -> None:
    w = r.seat_width_m - 0.040
    length = r.leg_len_m
    leg.visual(
        Box((w, 0.096, length)),
        origin=Origin(xyz=(0.0, 0.020, -length * 0.5)),
        material=mats["upholstery"],
        name=f"legrest_style__chaise_legrest__pad_{index}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
    )
    # Raised side bolsters, the chaise tell.
    for side, sx in enumerate((-1.0, 1.0)):
        leg.visual(
            Box((0.044, 0.056, length * 0.84)),
            origin=Origin(
                xyz=(sx * (w * 0.5 - 0.026), 0.020, -length * 0.5)
            ),
            material=mats["upholstery"],
            name=f"legrest_style__chaise_legrest__bolster_{index}_{side}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
        )


_LEGREST_BUILDERS = {
    "pad_legrest": _legrest_style_pad_legrest_build,
    "chaise_legrest": _legrest_style_chaise_legrest_build,
}


# --- carcass ----------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("sofa_frame", meta={"role": "sofa_frame"})
    depth = r.seat_depth_m
    w = r.total_width_m
    _BASE_BUILDERS[r.base_style](frame, r, mats)
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((ARM_W, depth, r.seat_height_m + 0.145)),
            origin=Origin(
                xyz=(sx * (w - ARM_W) * 0.5, -depth * 0.5, (r.seat_height_m + 0.145) * 0.5)
            ),
            material=mats["upholstery"],
            name=f"carcass_arm_{side}", material_class_id=("leather.smooth_plain" if r.palette_style == "camel_leather" else "fabric.upholstery_plain"),
        )
    for index, x in enumerate(r.seat_x):
        _DECK_BUILDERS[r.deck_build](frame, r, mats, index, x)
        # Backrest hinge brackets straddling each seat's back panel.
        for side, sx in enumerate((-1.0, 1.0)):
            frame.visual(
                Box((0.014, 0.052, r.seat_height_m - r.plinth_top_z + 0.070)),
                origin=Origin(
                    xyz=(
                        x + sx * (r.seat_width_m * 0.5 - 0.006),
                        r.back_hinge_y,
                        r.plinth_top_z + (r.seat_height_m - r.plinth_top_z + 0.070) * 0.5 - 0.020,
                    )
                ),
                material=mats["steel"],
                name=f"back_hinge_bracket_{index}_{side}", material_class_id="metal.steel_bare",
            )
            # Legrest hinge brackets on the plinth front.
            frame.visual(
                Box((0.014, 0.086, 0.052)),
                origin=Origin(
                    xyz=(
                        x + sx * (r.seat_width_m * 0.5 - 0.012),
                        r.leg_hinge_y - 0.036,
                        r.leg_hinge_z,
                    )
                ),
                material=mats["steel"],
                name=f"legrest_hinge_bracket_{index}_{side}", material_class_id="metal.steel_bare",
            )
    return frame


def _build_seat_units(model: ArticulatedObject, frame, r: ResolvedConfig,
                      mats: dict[str, str]):
    backs, legs = [], []
    for index, x in enumerate(r.seat_x):
        back = model.part(
            f"back_build__{r.back_build}__seat_back_{index}",
            meta={"role": "seat_back", "index": index},
        )
        _BACK_BUILDERS[r.back_build](back, r, mats, index)
        _x_cyl(
            back,
            f"back_hinge_barrel_{index}",
            0.017,
            2.0 * (r.seat_width_m * 0.5 - 0.013 + MOUNT),
            (0.0, 0.0, 0.0),
            mats["zinc"],
        )
        _rev_joint(
            model,
            name=f"frame_to_seat_back_{index}",
            parent=frame,
            child=back,
            point=(x, r.back_hinge_y, r.seat_height_m),
            axis=(1.0, 0.0, 0.0),
            provider_radial=(0.0, 0.0, 1.0),
            lower=0.0,
            upper=BACK_RECLINE,
            effort=200.0,
            velocity=0.45,
        )
        backs.append(back)

        leg = model.part(
            f"legrest_style__{r.legrest_style}__legrest_{index}",
            meta={"role": "legrest", "index": index},
        )
        _LEGREST_BUILDERS[r.legrest_style](leg, r, mats, index)
        _x_cyl(
            leg,
            f"legrest_hinge_barrel_{index}",
            0.016,
            2.0 * (r.seat_width_m * 0.5 - 0.019 + MOUNT),
            (0.0, 0.0, 0.0),
            mats["zinc"],
        )
        _rev_joint(
            model,
            name=f"frame_to_legrest_{index}",
            parent=frame,
            child=leg,
            point=(x, r.leg_hinge_y, r.leg_hinge_z),
            axis=(1.0, 0.0, 0.0),
            provider_radial=(0.0, 0.0, 1.0),
            # Stowed hanging down in front of the plinth; +pi/2 swings it up and
            # forward to seat level, into free air.
            lower=0.0,
            upper=LEG_TRAVEL,
            effort=150.0,
            velocity=0.60,
        )
        legs.append(leg)
    return backs, legs


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_folding_sofa_bed2(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Folding_sofa_bed2",
            "slot_choices": slot_choices_for_config(r),
            "conversion": "per-seat reclining back + pop-out legrest",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)
    _build_seat_units(model, frame, r, mats)

    control = model.part("recline_control", meta={"role": "recline_control"})
    control.visual(
        Cylinder(radius=0.021, length=0.018),
        origin=Origin(xyz=(0.008, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["zinc"],
        name="recline_control__knob", material_class_id="metal.brushed_silver",
    )
    control.visual(
        Box((0.012, 0.006, 0.026)),
        origin=Origin(xyz=(0.015, 0.0, 0.0)),
        material=mats["shadow"],
        name="recline_control__indicator", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    # Escutcheon on the arm's outer face that the knob turns in.
    frame.visual(
        Box((0.012, 0.056, 0.056)),
        origin=Origin(xyz=(r.control_x - 0.006, -r.seat_depth_m * 0.34, r.control_z)),
        material=mats["shadow"],
        name="recline_control_escutcheon", material_class_id="plastic.opaque_generic",
    )
    _rev_joint(
        model,
        name="frame_to_recline_control",
        parent=frame,
        child=control,
        point=(r.control_x, -r.seat_depth_m * 0.34, r.control_z),
        axis=(1.0, 0.0, 0.0),
        provider_radial=(0.0, 0.0, 1.0),
        lower=-0.80,
        upper=0.80,
        effort=6.0,
        velocity=4.0,
    )

    back_joints = [f"frame_to_seat_back_{i}" for i in range(r.seat_count)]
    leg_joints = [f"frame_to_legrest_{i}" for i in range(r.seat_count)]
    model.meta["risk_poses"] = (
        {n: 0.0 for n in back_joints + leg_joints} | {"frame_to_recline_control": 0.0},
        {n: BACK_RECLINE for n in back_joints}
        | {n: LEG_TRAVEL for n in leg_joints}
        | {"frame_to_recline_control": 0.80},
        {n: BACK_RECLINE for n in back_joints}
        | {n: 0.0 for n in leg_joints}
        | {"frame_to_recline_control": -0.80},
    )
    model.meta["coupled_joint_pairs"] = tuple(
        (back_joints[i], leg_joints[i]) for i in range(r.seat_count)
    )
    return model


def build_seeded_picturex_0611_folding_sofa_bed2(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_folding_sofa_bed2(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_folding_sofa_bed2_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "sofa_frame")
    backs = _parts_by_role(model, "seat_back")
    legs = _parts_by_role(model, "legrest")
    controls = _parts_by_role(model, "recline_control")

    joints = {j.name: j for j in model.articulations}
    back_joints = [joints.get(f"frame_to_seat_back_{i}") for i in range(r.seat_count)]
    leg_joints = [joints.get(f"frame_to_legrest_{i}") for i in range(r.seat_count)]
    control_joint = joints.get("frame_to_recline_control")

    def _is_rev_x(j) -> bool:
        return (
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(abs(v), 6) for v in j.axis) == (1.0, 0.0, 0.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    ctx.check(
        "category_anchor: per-seat reclining back and pop-out legrest",
        len(frames) == 1
        and len(backs) == r.seat_count
        and len(legs) == r.seat_count
        and len(controls) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "sofa_frame"
        and all(_is_rev_x(j) and j.parent == "sofa_frame" for j in back_joints)
        and all(_is_rev_x(j) and j.parent == "sofa_frame" for j in leg_joints)
        and _is_rev_x(control_joint),
        details=f"backs={len(backs)} legs={len(legs)} seats={r.seat_count}",
    )

    # Motion evidence: each back really reclines rearward, and each legrest
    # really swings up from below the seat to seat level without hitting the
    # floor at either limit.
    back0, leg0 = backs[0], legs[0]
    rest_b = ctx.part_world_aabb(back0)
    with ctx.pose({back_joints[0]: back_joints[0].motion_limits.upper}):
        recl_b = ctx.part_world_aabb(back0)
    stow_l = ctx.part_world_aabb(leg0)
    with ctx.pose({leg_joints[0]: leg_joints[0].motion_limits.upper}):
        out_l = ctx.part_world_aabb(leg0)
    ctx.check(
        "category_anchor: legrest swings up to seat level and clears the floor",
        all(b is not None for b in (rest_b, recl_b, stow_l, out_l))
        and recl_b[0][1] < rest_b[0][1] - 0.10
        and recl_b[1][2] < rest_b[1][2] - 0.02
        and stow_l[0][2] > 0.0
        and out_l[1][1] > stow_l[1][1] + 0.10
        and out_l[0][2] > stow_l[0][2] + 0.10,
        details=f"back rest={rest_b} reclined={recl_b} leg stow={stow_l} out={out_l}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    back_ok = {
        "single_back": any("single_back__piped_top" in n for n in visual_names),
        "split_ratchet": any("split_ratchet__notch" in n for n in visual_names),
        "bifold_panels": any("bifold_panels__seam_bead" in n for n in visual_names),
    }[r.back_build]
    ctx.check("category_anchor: back_build identity", back_ok, details=f"back_build={r.back_build}")

    base_ok = {
        "plinth_base": any("plinth_base__toe_kick" in n for n in visual_names),
        "metal_futon": any("metal_futon__tube_leg" in n for n in visual_names),
        "storage_base": any("storage_base__door_pull" in n for n in visual_names),
    }[r.base_style]
    ctx.check("category_anchor: base_style identity", base_ok, details=f"base_style={r.base_style}")

    deck_ok = {
        "upholstered_deck": any("upholstered_deck__welt" in n for n in visual_names),
        "slatted_deck": any("slatted_deck__slat" in n for n in visual_names),
    }[r.deck_build]
    ctx.check("category_anchor: deck_build identity", deck_ok, details=f"deck_build={r.deck_build}")

    leg_ok = {
        "pad_legrest": any("pad_legrest__welt" in n for n in visual_names),
        "chaise_legrest": any("chaise_legrest__bolster" in n for n in visual_names),
    }[r.legrest_style]
    ctx.check(
        "category_anchor: legrest_style identity", leg_ok,
        details=f"legrest_style={r.legrest_style}",
    )

    ctx.check(
        "seat units are pitched across the carcass",
        len(r.seat_x) == r.seat_count
        and abs(r.total_width_m - (r.seat_count * r.seat_width_m + 2.0 * ARM_W)) < 1e-9
        and all(
            abs((r.seat_x[i + 1] - r.seat_x[i]) - r.seat_width_m) < 1e-9
            for i in range(len(r.seat_x) - 1)
        ),
        details=f"seat_x={r.seat_x} width={r.total_width_m}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "single_seat_min_envelope",
        {
            "back_build": "single_back",
            "base_style": "plinth_base",
            "deck_build": "upholstered_deck",
            "legrest_style": "pad_legrest",
            "seat_count": 1,
            "seat_width_m": 0.52,
            "seat_depth_m": 0.52,
            "seat_height_m": 0.38,
        },
        reason="single narrow shallow seat with the lowest hinge line - shortest legrest",
    ),
    corner_case(
        "three_seat_max_envelope_chaise",
        {
            "back_build": "split_ratchet",
            "base_style": "metal_futon",
            "deck_build": "slatted_deck",
            "legrest_style": "chaise_legrest",
            "seat_count": 3,
            "seat_width_m": 0.74,
            "seat_depth_m": 0.68,
            "seat_height_m": 0.46,
        },
        reason="widest three-seat carcass with the longest chaise legrests on an open frame",
    ),
    corner_case(
        "three_seat_shallow_storage_bifold",
        {
            "back_build": "bifold_panels",
            "base_style": "storage_base",
            "deck_build": "upholstered_deck",
            "legrest_style": "chaise_legrest",
            "seat_count": 3,
            "seat_width_m": 0.52,
            "seat_depth_m": 0.52,
            "seat_height_m": 0.46,
        },
        reason="three narrow seats on the shallowest storage box - tightest back/legrest packing",
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
    "build_picturex_0611_folding_sofa_bed2",
    "build_seeded_picturex_0611_folding_sofa_bed2",
    "run_picturex_0611_folding_sofa_bed2_tests",
]
