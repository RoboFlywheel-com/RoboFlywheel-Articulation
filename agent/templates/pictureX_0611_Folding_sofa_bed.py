# SPDX-License-Identifier: Apache-2.0

"""Self-contained folding sofa bed template.

A sofa whose seat/back mechanism folds out into a bed: a rigid upholstered
``sofa_frame`` root, a fixed ``seat_deck`` middle bed panel, a ``backrest`` that
reclines flat rearward onto fixed rear support legs, a ``foot_panel`` that folds
out forward to bed height, and ``deck_leg_count`` fold-down ``deck_leg`` supports
under the foot panel (each with a real captured pivot receiver).  Three
peripheral structural slots (base_leg, arm_style, deck_support) vary by controlled
world-knowledge extrapolation from the single source without touching the shared
conversion mechanism.  No source-replay import, no motion clamping, no whole-part
overlap allowance.

The three identifying articulations are REVOLUTE about the world x cross-axis
(the foot panel uses -x so it folds up over the seat rather than down through it),
built from
``mate_axes`` + ``register_interface_mate``.  Neutral (every revolute at its lower
limit) is the fully-folded sofa; upper limits give the fully-deployed bed.
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
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    multiplicity_slot,
    register_interface_mate,
)

BaseLeg = Literal["splayed_chrome", "tapered_walnut", "hairpin_steel"]
ArmStyle = Literal["bolster_arm", "roll_arm", "track_arm"]
DeckSupport = Literal["single_post", "splayed_strut"]
PaletteStyle = Literal["gray_tuft", "navy_linen", "camel_leather", "sage_weave"]

BASE_LEGS: tuple[BaseLeg, ...] = ("splayed_chrome", "tapered_walnut", "hairpin_steel")
ARM_STYLES: tuple[ArmStyle, ...] = ("bolster_arm", "roll_arm", "track_arm")
DECK_SUPPORTS: tuple[DeckSupport, ...] = ("single_post", "splayed_strut")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "gray_tuft",
    "navy_linen",
    "camel_leather",
    "sage_weave",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("base_leg", BASE_LEGS),
        component_slot("arm_style", ARM_STYLES),
        component_slot("deck_support", DECK_SUPPORTS),
        multiplicity_slot("deck_leg_count", (2, 3, 4), item_slot="deck_support"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "gray_tuft": {
        "upholstery": (0.48, 0.49, 0.50, 1.0),
        "seam": (0.36, 0.37, 0.38, 1.0),
        "button": (0.30, 0.31, 0.32, 1.0),
        "wood": (0.20, 0.14, 0.10, 1.0),
        "metal": (0.48, 0.51, 0.54, 1.0),
        "chrome": (0.78, 0.80, 0.82, 1.0),
        "foot": (0.05, 0.05, 0.06, 1.0),
    },
    "navy_linen": {
        "upholstery": (0.16, 0.21, 0.33, 1.0),
        "seam": (0.11, 0.15, 0.24, 1.0),
        "button": (0.09, 0.12, 0.20, 1.0),
        "wood": (0.30, 0.22, 0.14, 1.0),
        "metal": (0.40, 0.42, 0.45, 1.0),
        "chrome": (0.74, 0.76, 0.78, 1.0),
        "foot": (0.05, 0.05, 0.06, 1.0),
    },
    "camel_leather": {
        "upholstery": (0.63, 0.44, 0.26, 1.0),
        "seam": (0.47, 0.31, 0.17, 1.0),
        "button": (0.38, 0.25, 0.13, 1.0),
        "wood": (0.24, 0.16, 0.10, 1.0),
        "metal": (0.30, 0.31, 0.33, 1.0),
        "chrome": (0.72, 0.62, 0.40, 1.0),
        "foot": (0.06, 0.05, 0.04, 1.0),
    },
    "sage_weave": {
        "upholstery": (0.56, 0.61, 0.50, 1.0),
        "seam": (0.41, 0.46, 0.36, 1.0),
        "button": (0.34, 0.39, 0.30, 1.0),
        "wood": (0.28, 0.24, 0.16, 1.0),
        "metal": (0.46, 0.48, 0.47, 1.0),
        "chrome": (0.70, 0.74, 0.70, 1.0),
        "foot": (0.05, 0.05, 0.05, 1.0),
    },
}


# Fixed cross-section constants (continuous surface detail, not core/raw).
CUSHION_T = 0.11
DECK_T = 0.03
# Foot-panel clearance above the seat when folded.
#
# NOTE (open issue): this single value sets BOTH the folded clearance and, via
# `foot_hinge_z = bed_height + HINGE_GAP`, the deployed panel height.  The stowed
# deck legs (~0.04 tall) ride round with the panel and sweep into `seat_deck`
# mid-fold, which wants a larger gap -- but enlarging it lifts the deployed panel
# off bed level and fails the "deploys forward to bed height" invariant.  Fixing
# this properly means decoupling the two (e.g. a recess in the seat deck for the
# stowed legs, or stowing them on the panel's outer face), not retuning this.
HINGE_GAP = 0.016
FOOT_HINGE_Y = 0.035  # front hinge forward of the seat front edge
ARM_W = 0.16
# Sub-millimetre mount contact: parts overlap their host by less than the 1 mm
# collision tolerance so QC reads them as connected (contact) without an overlap.
MOUNT = 0.0006
# The deck-leg brackets must straddle OUTSIDE the leg's widest x-extent, or the
# leg sweeps through them when it folds.  The splayed strut fans to ~+-0.054 in x
# near its pivot, so the plates sit at +-0.062 and the pivot rod is long enough to
# journal into both of them.
DECK_RECEIVER_HALF = 0.062
# Plates are 0.012 thick and centred on DECK_RECEIVER_HALF, so their inner faces
# are at DECK_RECEIVER_HALF - 0.006.  The rod journals MOUNT past each inner face:
# real captured contact, but under the collision tolerance rather than spearing
# the full plate thickness.
DECK_PIVOT_ROD_LEN = 2.0 * (DECK_RECEIVER_HALF - 0.006 + MOUNT)


def _reanchor(part, delta: tuple[float, float, float]) -> None:
    """Re-express a child's local geometry against a moved joint origin.

    A FIXED joint's origin also *places* its child, so moving that origin onto
    the real mounting contact would drag the whole part with it.  Shifting every
    local element by the same delta cancels that motion exactly, leaving the part
    where it was in the world while the joint frame lands on real contact
    geometry (what `fail_if_articulation_origin_far_from_geometry` checks).
    """
    dx, dy, dz = delta
    for group in (part.visuals, getattr(part, "collisions", ()) or ()):
        for element in group:
            origin = element.origin
            x, y, z = origin.xyz
            element.origin = Origin(xyz=(x + dx, y + dy, z + dz), rpy=origin.rpy)


@dataclass(frozen=True)
class Config:
    base_leg: BaseLeg = "splayed_chrome"
    arm_style: ArmStyle = "bolster_arm"
    deck_support: DeckSupport = "single_post"
    deck_leg_count: int = 2
    width_m: float | None = None
    seat_depth_m: float | None = None
    bed_height_m: float | None = None
    palette_style: PaletteStyle = "gray_tuft"
    name: str = "pictureX_0611_Folding_sofa_bed"


@dataclass(frozen=True)
class ResolvedConfig:
    base_leg: BaseLeg
    arm_style: ArmStyle
    deck_support: DeckSupport
    deck_leg_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    width_m: float
    seat_depth_m: float
    bed_height_m: float
    seat_width_m: float
    z_under: float  # underside of seat deck / top of legs region
    leg_len_m: float
    backrest_len_m: float
    foot_len_m: float
    foot_hinge_z: float
    rear_support_y: float
    deck_pivot_local_z: float
    deck_leg_len_m: float
    deck_leg_local_y: float
    deck_leg_x: tuple[float, ...]
    front_post_x: float
    corner_x: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x50F5_0FA5_0BED)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        base_leg=choices["base_leg"],
        arm_style=choices["arm_style"],
        deck_support=choices["deck_support"],
        deck_leg_count=choices["deck_leg_count"],
        width_m=round(rng.uniform(1.70, 2.10), 4),
        seat_depth_m=round(rng.uniform(0.55, 0.68), 4),
        bed_height_m=round(rng.uniform(0.38, 0.44), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"folding_sofa_bed_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "base_leg": config.base_leg,
            "arm_style": config.arm_style,
            "deck_support": config.deck_support,
            "deck_leg_count": config.deck_leg_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")

    width = _clamp(0.0 if config.width_m is None else config.width_m, 1.70, 2.10) if config.width_m is not None else 1.90
    depth = _clamp(config.seat_depth_m, 0.55, 0.68) if config.seat_depth_m is not None else 0.60
    height = _clamp(config.bed_height_m, 0.38, 0.44) if config.bed_height_m is not None else 0.40
    if config.width_m is not None and not 1.70 <= float(config.width_m) <= 2.10:
        raise ValueError("width_m must be in [1.70, 2.10]")
    if config.seat_depth_m is not None and not 0.55 <= float(config.seat_depth_m) <= 0.68:
        raise ValueError("seat_depth_m must be in [0.55, 0.68]")
    if config.bed_height_m is not None and not 0.38 <= float(config.bed_height_m) <= 0.44:
        raise ValueError("bed_height_m must be in [0.38, 0.44]")

    seat_width = width - 2.0 * ARM_W
    z_under = height - CUSHION_T - DECK_T
    leg_len = z_under - 0.06  # legs stop at the apron bottom
    backrest_len = min(0.55, depth * 0.86)
    foot_len = max(0.34, depth - 0.16)  # clears the upright backrest cushion
    foot_hinge_z = height + HINGE_GAP
    rear_support_y = -depth - backrest_len
    deck_pivot_local_z = CUSHION_T + DECK_T + 0.024  # pivot sits on the deck face, not in it
    deck_leg_len = z_under + HINGE_GAP - 0.05  # deployed foot rests just off the floor
    deck_leg_local_y = -0.62 * foot_len
    n = int(config.deck_leg_count)
    span = seat_width * 0.72
    if n == 1:
        xs = (0.0,)
    else:
        xs = tuple(-span * 0.5 + span * i / (n - 1) for i in range(n))
    front_post_x = seat_width * 0.5 - 0.06
    corner_x = seat_width * 0.5 - 0.08
    return ResolvedConfig(
        base_leg=config.base_leg,
        arm_style=config.arm_style,
        deck_support=config.deck_support,
        deck_leg_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        width_m=width,
        seat_depth_m=depth,
        bed_height_m=height,
        seat_width_m=seat_width,
        z_under=z_under,
        leg_len_m=leg_len,
        backrest_len_m=backrest_len,
        foot_len_m=foot_len,
        foot_hinge_z=foot_hinge_z,
        rear_support_y=rear_support_y,
        deck_pivot_local_z=deck_pivot_local_z,
        deck_leg_len_m=deck_leg_len,
        deck_leg_local_y=deck_leg_local_y,
        deck_leg_x=xs,
        front_post_x=front_post_x,
        corner_x=corner_x,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("base_leg", config.base_leg),
        ("arm_style", config.arm_style),
        ("deck_support", config.deck_support),
        ("deck_leg_count", config.deck_leg_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"sofa_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"sofa_{r.palette_style}_{key}"
    return mats


def _x_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.stainless_matte",
    )


def _tufted_panel(
    part,
    prefix: str,
    mats: dict[str, str],
    *,
    width: float,
    depth: float,
    center_y: float,
    cushion_bottom_z: float,
    deck_bottom_z: float,
) -> None:
    """Upholstered cushion over a plywood deck, in world-aligned local coords."""
    part.visual(
        Box((width, depth, DECK_T)),
        origin=Origin(xyz=(0.0, center_y, deck_bottom_z + DECK_T * 0.5)),
        material=mats["wood"],
        name=f"{prefix}_deck", material_class_id="wood.plywood",
    )
    part.visual(
        Box((width, depth, CUSHION_T)),
        origin=Origin(xyz=(0.0, center_y, cushion_bottom_z + CUSHION_T * 0.5)),
        material=mats["upholstery"],
        name=f"{prefix}_cushion", material_class_id="fabric.upholstery_plain",
    )
    for i, fx in enumerate((-width / 6.0, width / 6.0)):
        part.visual(
            Box((0.012, depth * 0.86, 0.010)),
            origin=Origin(xyz=(fx, center_y, cushion_bottom_z + CUSHION_T)),
            material=mats["seam"],
            name=f"{prefix}_seam_{i}", material_class_id="fabric.thread_yarn",
        )
    for row, dy in enumerate((-depth * 0.24, depth * 0.24)):
        for col, bx in enumerate((-width * 0.28, 0.0, width * 0.28)):
            part.visual(
                Cylinder(radius=0.013, length=0.010),
                origin=Origin(xyz=(bx, center_y + dy, cushion_bottom_z + CUSHION_T - 0.003)),
                material=mats["button"],
                name=f"{prefix}_button_{row}_{col}", material_class_id="fabric.upholstery_plain",
            )


def _rev_axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    provider_radial: tuple[float, float, float],
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
    axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> None:
    provider = AxisInterface(
        name=f"{name}__provider",
        point=point,
        axis=axis,
        radial=provider_radial,
    )
    consumer = AxisInterface(
        name=f"{name}__consumer",
        axis=axis,
        radial=(0.0, 0.0, 1.0),
    )
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


# --- frame ------------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("sofa_frame", meta={"role": "sofa_frame"})
    sw = r.seat_width_m
    depth = r.seat_depth_m
    zt = r.z_under  # apron top
    zb = zt - 0.06  # apron bottom / leg top
    rail = 0.06
    # Apron rails (a rectangle under the seat deck).
    frame.visual(
        Box((sw, rail, 0.06)),
        origin=Origin(xyz=(0.0, -0.03, zt - 0.03)),
        material=mats["wood"],
        name="apron_front_rail", material_class_id="wood.engineered_board",
    )
    frame.visual(
        Box((sw, rail, 0.06)),
        origin=Origin(xyz=(0.0, -depth + 0.06, zt - 0.03)),
        material=mats["wood"],
        name="apron_rear_rail", material_class_id="wood.engineered_board",
    )
    for i, x in enumerate((-sw * 0.5 + 0.03, sw * 0.5 - 0.03)):
        frame.visual(
            Box((rail, depth, 0.06)),
            origin=Origin(xyz=(x, -depth * 0.5, zt - 0.03)),
            material=mats["wood"],
            name=f"apron_side_rail_{i}", material_class_id="wood.engineered_board",
        )
    # Front hinge posts + boss carrying the foot panel at the front-top edge.
    # Front hinge posts carry the foot-panel hinge via coaxial end lugs (a clevis
    # the child barrel sits between with real clearance — no overlap allowance).
    for i, x in enumerate((-r.front_post_x, r.front_post_x)):
        # The post is bolted onto the apron front rail (its front face is y=0),
        # so extend it 6 mm back over that rail.  Sitting wholly in front of the
        # rail left the post -- and the hinge lug riding on it -- as islands.
        post_hi = FOOT_HINGE_Y + 0.0275
        post_lo = -0.006
        frame.visual(
            Box((0.055, post_hi - post_lo, r.foot_hinge_z - zt)),
            origin=Origin(xyz=(x, 0.5 * (post_hi + post_lo), (zt + r.foot_hinge_z) * 0.5)),
            material=mats["metal"],
            name=f"front_hinge_post_{i}", material_class_id="metal.stainless_matte",
        )
        frame.visual(
            Cylinder(radius=0.024, length=0.07),
            origin=Origin(xyz=(x, FOOT_HINGE_Y, r.foot_hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"foot_hinge_lug_{i}", material_class_id="metal.stainless_matte",
        )
    # Rear backrest hinge: posts rise to bed height carrying coaxial end knuckles
    # just outside the (narrower) backrest panel width, so the barrel abuts them
    # without the reclining panel ever sweeping through a support.
    hb = r.bed_height_m
    back_half = r.seat_width_m * 0.40
    for i, x in enumerate((-(back_half + 0.045), back_half + 0.045)):
        # Same for the backrest post: the apron rear rail's outer face is at
        # -depth + 0.03, so lap 6 mm over it instead of standing clear behind it.
        bpost_lo = -depth - 0.025
        bpost_hi = -depth + 0.036
        frame.visual(
            Box((0.05, bpost_hi - bpost_lo, hb - zt)),
            origin=Origin(xyz=(x, 0.5 * (bpost_hi + bpost_lo), (zt + hb - 0.024) * 0.5)),
            material=mats["metal"],
            name=f"backrest_hinge_post_{i}", material_class_id="metal.stainless_matte",
        )
        frame.visual(
            Cylinder(radius=0.024, length=0.05),
            origin=Origin(xyz=(x, -depth, hb), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"backrest_hinge_knuckle_{i}", material_class_id="metal.stainless_matte",
        )
    # Rear support legs + rail that catch the reclined backrest far edge.
    for i, x in enumerate((-r.corner_x, r.corner_x)):
        frame.visual(
            Box((0.05, 0.05, zt)),
            origin=Origin(xyz=(x, r.rear_support_y, zt * 0.5)),
            material=mats["wood"],
            name=f"rear_support_leg_{i}", material_class_id="wood.engineered_board",
        )
    frame.visual(
        Box((sw, 0.06, 0.04)),
        origin=Origin(xyz=(0.0, r.rear_support_y, zt - 0.022)),
        material=mats["wood"],
        name="rear_support_rail", material_class_id="wood.engineered_board",
    )
    # Longitudinal stringers tying the rear support back to the apron.  Without
    # them the rear rail and its two legs float ~0.5 m behind the frame as a
    # detached island -- and a sofa bed's rear outrigger genuinely is carried on
    # side members running back from the seat box.
    stringer_front = -depth + 0.06
    stringer_rear = r.rear_support_y - 0.03
    for i, x in enumerate((-sw * 0.5 + 0.03, sw * 0.5 - 0.03)):
        frame.visual(
            Box((0.06, stringer_front - stringer_rear, 0.04)),
            origin=Origin(
                xyz=(x, 0.5 * (stringer_front + stringer_rear), zt - 0.022)
            ),
            material=mats["wood"],
            name=f"rear_support_stringer_{i}", material_class_id="wood.engineered_board",
        )
    frame.inertial = None
    return frame, zb


def _build_seat_deck(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    seat = model.part("seat_deck", meta={"role": "seat_deck"})
    # Seat cushion/deck stop 0.05 m short of the rear hinge line so nothing
    # intrudes into the backrest hinge zone.
    seat_depth = r.seat_depth_m - 0.06
    _tufted_panel(
        seat,
        "seat",
        mats,
        width=r.seat_width_m * 0.98,
        depth=seat_depth,
        center_y=-0.01 - seat_depth * 0.5,
        cushion_bottom_z=r.bed_height_m - CUSHION_T - MOUNT,
        deck_bottom_z=r.z_under - MOUNT,
    )
    # Seat the joint on the real bearing contact: the deck lands on the top face
    # of the apron front rail (rail top == r.z_under), not at the world origin.
    deck_mount = (0.0, -0.03, r.z_under)
    _reanchor(seat, (-deck_mount[0], -deck_mount[1], -deck_mount[2]))
    model.articulation(
        "frame_to_seat_deck",
        ArticulationType.FIXED,
        parent=frame,
        child=seat,
        origin=Origin(xyz=deck_mount),
    )


# --- backrest ---------------------------------------------------------------
def _build_backrest(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    back = model.part("backrest", meta={"role": "backrest"})
    width = r.seat_width_m * 0.80
    length = r.backrest_len_m
    # Hinge at bed height (Hb) at the seat rear edge.  The panel body sits BEHIND
    # the hinge when upright (cushion front face at local y=0 = the hinge plane),
    # so it never intrudes into the seat; reclining about +x lays it flat rearward
    # with the cushion top landing back at Hb.
    back.visual(
        Box((width, DECK_T, length)),
        origin=Origin(xyz=(0.0, -CUSHION_T - DECK_T * 0.5, length * 0.5)),
        material=mats["wood"],
        name="backrest_deck", material_class_id="wood.plywood",
    )
    back.visual(
        Box((width, CUSHION_T, length)),
        origin=Origin(xyz=(0.0, -CUSHION_T * 0.5, length * 0.5)),
        material=mats["upholstery"],
        name="backrest_cushion", material_class_id=("fabric.plain_flat_weave" if r.palette_style in {"gray_tuft", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    for i, fx in enumerate((-width * 0.28, width * 0.28)):
        back.visual(
            Box((0.012, 0.010, length * 0.86)),
            origin=Origin(xyz=(fx, -0.004, length * 0.5)),
            material=mats["seam"],
            name=f"backrest_seam_{i}", material_class_id="fabric.thread_yarn",
        )
    for row, fz in enumerate((length * 0.32, length * 0.68)):
        for col, bx in enumerate((-width * 0.3, 0.0, width * 0.3)):
            back.visual(
                Cylinder(radius=0.014, length=0.012),
                origin=Origin(xyz=(bx, -0.003, fz), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["button"],
                name=f"backrest_button_{row}_{col}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"gray_tuft", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
            )
    _x_cyl(back, "backrest_hinge_barrel", 0.024, 2.0 * (width * 0.5 + 0.02 + MOUNT), (0.0, 0.0, 0.0), mats["metal"])
    _rev_axis_joint(
        model,
        name="frame_to_backrest",
        parent=frame,
        child=back,
        point=(0.0, -r.seat_depth_m, r.bed_height_m),
        provider_radial=(0.0, 0.0, 1.0),
        lower=0.0,
        upper=math.pi / 2.0,
        effort=110.0,
        velocity=0.7,
    )


# --- foot panel + deck legs -------------------------------------------------
def _deck_support_single_post_build(leg, r: ResolvedConfig, mats: dict[str, str]) -> None:
    length = r.deck_leg_len_m
    leg.visual(
        Cylinder(radius=0.017, length=length),
        origin=Origin(xyz=(0.0, 0.0, length * 0.5)),
        material=mats["metal"],
        name="deck_leg_tube", material_class_id="metal.stainless_matte",
    )
    leg.visual(
        Sphere(radius=0.026),
        origin=Origin(xyz=(0.0, 0.0, length - 0.004)),
        material=mats["foot"],
        name="deck_leg_foot", material_class_id="rubber.smooth_plain",
    )
    _x_cyl(leg, "deck_leg_pivot_boss", 0.020, DECK_PIVOT_ROD_LEN, (0.0, 0.0, 0.0), mats["metal"])


def _deck_support_splayed_strut_build(leg, r: ResolvedConfig, mats: dict[str, str]) -> None:
    length = r.deck_leg_len_m
    splay = 0.09
    for i, sx in enumerate((-splay, splay)):
        cx = sx * 0.5
        strut_len = math.hypot(splay, length)
        pitch = math.atan2(splay, length) * (1.0 if i == 1 else -1.0)
        leg.visual(
            Box((0.020, 0.020, strut_len)),
            origin=Origin(xyz=(cx, 0.0, length * 0.5), rpy=(0.0, pitch, 0.0)),
            material=mats["metal"],
            name=f"deck_leg_strut_{i}", material_class_id="metal.stainless_matte",
        )
    leg.visual(
        Box((2.0 * splay + 0.04, 0.028, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, length + 0.010)),
        material=mats["foot"],
        name="deck_leg_crossfoot", material_class_id="rubber.smooth_plain",
    )
    _x_cyl(leg, "deck_leg_pivot_boss", 0.020, DECK_PIVOT_ROD_LEN, (0.0, 0.0, 0.0), mats["metal"])


_DECK_SUPPORT_BUILDERS = {
    "single_post": _deck_support_single_post_build,
    "splayed_strut": _deck_support_splayed_strut_build,
}


def _build_foot_panel(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    foot = model.part("foot_panel", meta={"role": "foot_panel"})
    width = r.seat_width_m * 0.98
    length = r.foot_len_m
    # Authored folded (theta=0): panel over the seat, cushion facing down toward
    # the seat (local z in [0, CUSHION_T]), deck on top (local z in
    # [CUSHION_T, CUSHION_T+DECK_T]), extending local -y from the front hinge.
    # The panel front edge is recessed 0.03 m behind the hinge so the mattress
    # never intrudes into the hinge lug zone.
    cy = -0.03 - length * 0.5
    foot.visual(
        Box((width, length, CUSHION_T)),
        origin=Origin(xyz=(0.0, cy, CUSHION_T * 0.5)),
        material=mats["upholstery"],
        name="foot_cushion", material_class_id=("fabric.plain_flat_weave" if r.palette_style in {"gray_tuft", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    foot.visual(
        Box((width, length, DECK_T)),
        origin=Origin(xyz=(0.0, cy, CUSHION_T + DECK_T * 0.5)),
        material=mats["wood"],
        name="foot_deck", material_class_id="wood.plywood",
    )
    for i, fx in enumerate((-width / 6.0, width / 6.0)):
        foot.visual(
            Box((0.012, length * 0.86, 0.010)),
            origin=Origin(xyz=(fx, cy, CUSHION_T + DECK_T + 0.004)),
            material=mats["seam"],
            name=f"foot_seam_{i}", material_class_id="fabric.thread_yarn",
        )
    _x_cyl(foot, "foot_hinge_barrel", 0.020, 2.0 * (r.front_post_x - 0.0344), (0.0, 0.0, 0.0), mats["metal"])
    # Hinge leaf strapping the barrel to the panel deck.  The barrel sits on the
    # pivot axis at local zero while the deck starts ~10 mm away, so without the
    # leaf the barrel is a disconnected island -- and a real piano-style hinge
    # does carry a leaf from the knuckle onto the panel.
    leaf_near = cy + length * 0.5
    foot.visual(
        Box((2.0 * (r.front_post_x - 0.0344), abs(leaf_near) + 0.006, 0.012)),
        origin=Origin(xyz=(0.0, 0.5 * (leaf_near - 0.006), 0.0)),
        material=mats["metal"],
        name="foot_hinge_leaf", material_class_id="metal.stainless_matte",
    )
    _rev_axis_joint(
        model,
        name="frame_to_foot_panel",
        parent=frame,
        child=foot,
        point=(0.0, FOOT_HINGE_Y, r.foot_hinge_z),
        provider_radial=(0.0, 0.0, 1.0),
        # Hinge about -X so the panel folds UP and over the seat on its way out.
        # About +X the identical end poses are reached by sweeping DOWN through
        # the seat deck, dragging the stowed deck legs through it mid-fold.
        axis=(-1.0, 0.0, 0.0),
        lower=0.0,
        upper=math.pi,
        effort=70.0,
        velocity=0.8,
    )

    builder = _DECK_SUPPORT_BUILDERS[r.deck_support]
    receiver_z = r.deck_pivot_local_z
    for index, x in enumerate(r.deck_leg_x):
        # Clevis receiver: two side plates the pivot boss sits between with real
        # clearance (no overlap allowance).
        for side, sx in enumerate((-DECK_RECEIVER_HALF, DECK_RECEIVER_HALF)):
            foot.visual(
                # 0.062 tall (was 0.055) so the receiver's top laps into the deck
                # it hangs from; at 0.055 it stopped 2.5 mm short and the whole
                # receiver/leg-pivot group read as a disconnected island.
                Box((0.012, 0.052, 0.062)),
                origin=Origin(xyz=(x + sx, r.deck_leg_local_y, receiver_z + 0.006)),
                material=mats["metal"],
                name=f"deck_receiver_{index}" if side == 0 else f"deck_receiver_{index}_b", material_class_id="metal.stainless_matte",
            )
        leg = model.part(
            f"deck_support__{r.deck_support}__deck_leg_{index}",
            meta={"role": "deck_leg", "index": index},
        )
        builder(leg, r, mats)
        _rev_axis_joint(
            model,
            name=f"foot_panel_to_deck_leg_{index}",
            parent=foot,
            child=leg,
            point=(x, r.deck_leg_local_y, receiver_z),
            provider_radial=(0.0, 1.0, 0.0),
            # The leg stows flat against the panel's deck face and swings out
            # away from it.  Negative rotation would sweep the strut straight
            # through the cushion, so the travel runs 0 -> +90 deg.
            lower=0.0,
            upper=math.pi / 2.0,
            effort=35.0,
            velocity=1.0,
        )


# --- base support legs ------------------------------------------------------
def _base_leg_positions(r: ResolvedConfig) -> tuple[tuple[float, float], ...]:
    # The foot panel sweeps through a vertical position on its way out, where its
    # own thickness reaches back to `FOOT_HINGE_Y - panel_thickness`.  The front
    # legs must stand behind that swept envelope, otherwise the deploying panel
    # passes straight through them.  Set them back from the envelope rather than
    # at a fixed -0.09, and never further back than the rear leg line.
    panel_thickness = CUSHION_T + DECK_T + 0.08
    swept_back_y = FOOT_HINGE_Y - panel_thickness
    front_y = min(-0.09, swept_back_y - 0.035)
    front_y = max(front_y, -r.seat_depth_m + 0.20)
    return (
        (-r.corner_x, front_y),
        (r.corner_x, front_y),
        (-r.corner_x, -r.seat_depth_m + 0.09),
        (r.corner_x, -r.seat_depth_m + 0.09),
    )


def _base_leg_splayed_chrome_build(leg, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    length = r.leg_len_m
    leg.visual(
        Cylinder(radius=0.017, length=length),
        origin=Origin(xyz=(0.0, 0.0, -length * 0.5)),
        material=mats["chrome"],
        name=f"base_leg__splayed_chrome__tube_{index}", material_class_id="metal.chrome_polished",
    )
    leg.visual(
        Sphere(radius=0.026),
        origin=Origin(xyz=(0.0, 0.0, -length + 0.004)),
        material=mats["foot"],
        name=f"base_leg__splayed_chrome__foot_{index}", material_class_id="rubber.smooth_plain",
    )


def _base_leg_tapered_walnut_build(leg, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    length = r.leg_len_m
    leg.visual(
        Box((0.050, 0.050, length * 0.5)),
        origin=Origin(xyz=(0.0, 0.0, -length * 0.25)),
        material=mats["wood"],
        name=f"base_leg__tapered_walnut__upper_{index}", material_class_id="wood.walnut_dark",
    )
    leg.visual(
        Box((0.034, 0.034, length * 0.5)),
        origin=Origin(xyz=(0.0, 0.0, -length * 0.75)),
        material=mats["wood"],
        name=f"base_leg__tapered_walnut__lower_{index}", material_class_id="wood.walnut_dark",
    )


def _base_leg_hairpin_steel_build(leg, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    length = r.leg_len_m
    for j, dy in enumerate((-0.05, 0.05)):
        leg.visual(
            Cylinder(radius=0.007, length=length),
            origin=Origin(xyz=(0.0, dy * 0.5, -length * 0.5), rpy=(math.atan2(dy, length), 0.0, 0.0)),
            material=mats["metal"],
            name=f"base_leg__hairpin_steel__rod_{index}_{j}", material_class_id="metal.steel_bare",
        )
    leg.visual(
        Box((0.03, 0.12, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, -length + 0.006)),
        material=mats["foot"],
        name=f"base_leg__hairpin_steel__shoe_{index}", material_class_id="rubber.smooth_plain",
    )


_BASE_LEG_BUILDERS = {
    "splayed_chrome": _base_leg_splayed_chrome_build,
    "tapered_walnut": _base_leg_tapered_walnut_build,
    "hairpin_steel": _base_leg_hairpin_steel_build,
}


def _build_base_legs(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str], leg_top_z: float) -> None:
    builder = _BASE_LEG_BUILDERS[r.base_leg]
    for index, (x, y) in enumerate(_base_leg_positions(r)):
        leg = model.part(
            f"base_leg__{r.base_leg}__leg_{index}",
            meta={"role": "support_leg", "index": index},
        )
        builder(leg, r, mats, index)
        # Mount plate whose top face laps the apron bottom by MOUNT (< overlap tol)
        # so the leg is connected to the frame without an overlap allowance.
        leg.visual(
            Box((0.055, 0.055, 0.02)),
            origin=Origin(xyz=(0.0, 0.0, MOUNT - 0.01)),
            material=mats["metal"],
            name=f"base_leg__{r.base_leg}__mount_{index}", material_class_id="metal.stainless_matte",
        )
        # Put the joint on the leg-to-rail interface.  The leg centreline sits
        # inboard of the apron side rail (rail inner edge = seat_width/2 - 0.06),
        # so an origin on the centreline is ~20 mm clear of any frame geometry.
        # The midpoint between the rail's inner edge and the mount plate's outer
        # edge lies inside both wherever they lap, and stays within tolerance of
        # each if a narrow gap remains.
        rail_inner = r.seat_width_m * 0.5 - 0.06
        mount_outer = abs(x) + 0.0275
        contact_x = math.copysign(0.5 * (rail_inner + mount_outer), x)
        _reanchor(leg, (x - contact_x, 0.0, 0.0))
        model.articulation(
            f"frame_to_support_leg_{index}",
            ArticulationType.FIXED,
            parent=frame,
            child=leg,
            origin=Origin(xyz=(contact_x, y, leg_top_z)),
        )


# --- arms -------------------------------------------------------------------
def _arm_style_bolster_arm_build(arm, r: ResolvedConfig, mats: dict[str, str], index: int, sign: float) -> None:
    depth = r.seat_depth_m
    base_h = r.z_under
    radius = (ARM_W - 0.02) * 0.5
    arm.visual(
        Box((ARM_W - 0.02, depth, base_h)),
        origin=Origin(xyz=(0.0, -depth * 0.5, base_h * 0.5)),
        material=mats["upholstery"],
        name=f"arm_style__bolster_arm__base_{index}", material_class_id=("fabric.plain_flat_weave" if r.palette_style in {"gray_tuft", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    arm.visual(
        Cylinder(radius=radius, length=depth),
        origin=Origin(xyz=(0.0, -depth * 0.5, base_h + radius), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["upholstery"],
        name=f"arm_style__bolster_arm__bolster_{index}", material_class_id=("fabric.plain_flat_weave" if r.palette_style in {"gray_tuft", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )


def _arm_style_roll_arm_build(arm, r: ResolvedConfig, mats: dict[str, str], index: int, sign: float) -> None:
    depth = r.seat_depth_m
    height = r.bed_height_m + 0.16
    arm.visual(
        Box((ARM_W - 0.02, depth, height - 0.05)),
        origin=Origin(xyz=(0.0, -depth * 0.5, (height - 0.05) * 0.5)),
        material=mats["upholstery"],
        name=f"arm_style__roll_arm__panel_{index}", material_class_id=("fabric.plain_flat_weave" if r.palette_style in {"gray_tuft", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    for j, ay in enumerate((-depth + 0.05, -0.05)):
        arm.visual(
            Cylinder(radius=0.05, length=ARM_W - 0.02),
            origin=Origin(xyz=(0.0, ay, height - 0.05), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["upholstery"],
            name=f"arm_style__roll_arm__roll_{index}_{j}", material_class_id=("fabric.plain_flat_weave" if r.palette_style in {"gray_tuft", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
        )


def _arm_style_track_arm_build(arm, r: ResolvedConfig, mats: dict[str, str], index: int, sign: float) -> None:
    depth = r.seat_depth_m
    height = r.bed_height_m + 0.06
    arm.visual(
        Box((ARM_W - 0.02, depth, height)),
        origin=Origin(xyz=(0.0, -depth * 0.5, height * 0.5)),
        material=mats["upholstery"],
        name=f"arm_style__track_arm__panel_{index}", material_class_id=("fabric.plain_flat_weave" if r.palette_style in {"gray_tuft", "navy_linen", "sage_weave"} else "leather.smooth_plain"),
    )
    arm.visual(
        Box((ARM_W - 0.02, depth, 0.03)),
        origin=Origin(xyz=(0.0, -depth * 0.5, height + 0.015)),
        material=mats["seam"],
        name=f"arm_style__track_arm__cap_{index}", material_class_id="fabric.thread_yarn",
    )


_ARM_BUILDERS = {
    "bolster_arm": _arm_style_bolster_arm_build,
    "roll_arm": _arm_style_roll_arm_build,
    "track_arm": _arm_style_track_arm_build,
}


def _build_arms(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    builder = _ARM_BUILDERS[r.arm_style]
    inner = r.seat_width_m * 0.5
    for index, sign in enumerate((-1.0, 1.0)):
        arm = model.part(
            f"arm_style__{r.arm_style}__armrest_{index}",
            meta={"role": "armrest", "index": index},
        )
        builder(arm, r, mats, index, sign)
        # Inner face laps the apron side by MOUNT so the arm is connected.
        # Anchor the joint on that lap: a point half a MOUNT inside the arm's
        # inner face, at apron-rail height, lies within BOTH bodies.  The old
        # origin sat at the arm's local zero on the floor plane, 0.21 m clear of
        # any frame geometry.  `_reanchor` keeps the arm itself where it was.
        arm_origin = (sign * (inner + (ARM_W - 0.02) * 0.5 - MOUNT), 0.0, 0.0)
        arm_mount = (sign * (inner - MOUNT * 0.5), -0.29, r.z_under - 0.03)
        _reanchor(arm, tuple(arm_origin[i] - arm_mount[i] for i in range(3)))
        model.articulation(
            f"frame_to_armrest_{index}",
            ArticulationType.FIXED,
            parent=frame,
            child=arm,
            origin=Origin(xyz=arm_mount),
        )


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_folding_sofa_bed(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Folding_sofa_bed",
            "slot_choices": slot_choices_for_config(r),
            "conversion": "reclining back + fold-out foot panel + fold-down deck legs",
        },
    )
    mats = _materials(model, r)
    frame, leg_top_z = _build_frame(model, r, mats)
    _build_seat_deck(model, frame, r, mats)
    _build_backrest(model, frame, r, mats)
    _build_foot_panel(model, frame, r, mats)
    _build_base_legs(model, frame, r, mats, leg_top_z)
    _build_arms(model, frame, r, mats)

    deck_leg_joints = [f"foot_panel_to_deck_leg_{i}" for i in range(r.deck_leg_count)]
    model.meta["risk_poses"] = (
        {
            "frame_to_backrest": 0.0,
            "frame_to_foot_panel": 0.0,
            **{name: 0.0 for name in deck_leg_joints},
        },
        {
            "frame_to_backrest": math.pi / 2.0,
            "frame_to_foot_panel": math.pi,
            **{name: math.pi / 2.0 for name in deck_leg_joints},
        },
    )
    model.meta["coupled_joint_pairs"] = (
        ("frame_to_backrest", "frame_to_foot_panel"),
        *[("frame_to_foot_panel", name) for name in deck_leg_joints],
    )
    return model


def build_seeded_picturex_0611_folding_sofa_bed(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_folding_sofa_bed(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_folding_sofa_bed_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    foot = model.get_part("foot_panel")
    back = model.get_part("backrest")

    frames = _parts_by_role(model, "sofa_frame")
    seats = _parts_by_role(model, "seat_deck")
    backs = _parts_by_role(model, "backrest")
    feet = _parts_by_role(model, "foot_panel")
    deck_legs = _parts_by_role(model, "deck_leg")
    support_legs = _parts_by_role(model, "support_leg")
    arms = _parts_by_role(model, "armrest")

    joints = {j.name: j for j in model.articulations}
    back_joint = joints.get("frame_to_backrest")
    foot_joint = joints.get("frame_to_foot_panel")
    deck_joints = [joints.get(f"foot_panel_to_deck_leg_{i}") for i in range(r.deck_leg_count)]

    def _is_rev_x(j) -> bool:
        # The category invariant is that the conversion hinges all lie on the
        # world X cross-axis.  The SIGN is only a rotation-direction convention:
        # the foot panel hinges about -X so it folds up and over the seat rather
        # than sweeping down through it, which is the same physical hinge line.
        return (
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(abs(v), 6) for v in j.axis) == (1.0, 0.0, 0.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    ctx.check(
        "category_anchor: folding sofa-bed conversion mechanism",
        len(frames) == 1
        and len(seats) == 1
        and len(backs) == 1
        and len(feet) == 1
        and model.root_parts() and model.root_parts()[0].name == "sofa_frame"
        and _is_rev_x(back_joint)
        and back_joint.parent == "sofa_frame"
        and _is_rev_x(foot_joint)
        and foot_joint.parent == "sofa_frame",
        details=(
            f"frames={len(frames)} seats={len(seats)} backs={len(backs)} feet={len(feet)} "
            f"back_joint={back_joint} foot_joint={foot_joint}"
        ),
    )

    ctx.check(
        "category_anchor: supported fold-down deck legs",
        len(deck_legs) == r.deck_leg_count
        and all(_is_rev_x(j) and j.parent == "foot_panel" for j in deck_joints)
        and all(
            any(v.name == f"deck_receiver_{i}" for v in foot.visuals)
            for i in range(r.deck_leg_count)
        ),
        details=f"deck_legs={len(deck_legs)} expected={r.deck_leg_count}",
    )

    ctx.check(
        "four fixed support legs and two fixed arms",
        len(support_legs) == 4
        and len(arms) == 2
        and all(
            joints.get(f"frame_to_support_leg_{i}") is not None
            and joints[f"frame_to_support_leg_{i}"].articulation_type == ArticulationType.FIXED
            for i in range(4)
        )
        and all(
            joints.get(f"frame_to_armrest_{i}") is not None
            and joints[f"frame_to_armrest_{i}"].articulation_type == ArticulationType.FIXED
            for i in range(2)
        ),
        details=f"support_legs={len(support_legs)} arms={len(arms)}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    base_ok = {
        "splayed_chrome": any(n.startswith("base_leg__splayed_chrome__tube") for n in visual_names),
        "tapered_walnut": any(n.startswith("base_leg__tapered_walnut__upper") for n in visual_names),
        "hairpin_steel": any(n.startswith("base_leg__hairpin_steel__rod") for n in visual_names),
    }[r.base_leg]
    ctx.check("category_anchor: base_leg identity", base_ok, details=f"base_leg={r.base_leg}")

    arm_ok = {
        "bolster_arm": any("bolster_arm__bolster" in n for n in visual_names),
        "roll_arm": any("roll_arm__roll" in n for n in visual_names),
        "track_arm": any("track_arm__cap" in n for n in visual_names),
    }[r.arm_style]
    ctx.check("category_anchor: arm_style identity", arm_ok, details=f"arm_style={r.arm_style}")

    deck_ok = {
        "single_post": any("deck_leg_tube" == n for n in visual_names),
        "splayed_strut": any("deck_leg_crossfoot" == n for n in visual_names),
    }[r.deck_support]
    ctx.check("category_anchor: deck_support identity", deck_ok, details=f"deck_support={r.deck_support}")

    # Motion evidence: the foot panel deploys forward and the deck legs reach the
    # floor in the deployed bed pose while staying clear when folded.
    rest_foot = ctx.part_element_world_aabb(foot, elem="foot_cushion")
    with ctx.pose({foot_joint: foot_joint.motion_limits.upper}):
        deployed_foot = ctx.part_element_world_aabb(foot, elem="foot_cushion")
        with ctx.pose({**{foot_joint: foot_joint.motion_limits.upper},
                       **{j: j.motion_limits.upper for j in deck_joints}}):
            deployed_deck = [ctx.part_world_aabb(leg) for leg in deck_legs]
    ctx.check(
        "foot panel deploys forward to bed height",
        rest_foot is not None
        and deployed_foot is not None
        and deployed_foot[1][1] > rest_foot[1][1] + 0.30
        and abs(deployed_foot[1][2] - r.bed_height_m) < 0.05,
        details=f"rest={rest_foot}, deployed={deployed_foot}, Hb={r.bed_height_m}",
    )
    ctx.check(
        "deployed deck legs reach the floor without hanging below it",
        all(b is not None and -0.010 <= b[0][2] <= 0.05 for b in deployed_deck),
        details=f"deployed_deck={deployed_deck}",
    )

    # Motion evidence: backrest reclines rearward and drops flat toward bed height.
    rest_back = ctx.part_element_world_aabb(back, elem="backrest_cushion")
    with ctx.pose({back_joint: back_joint.motion_limits.upper}):
        reclined_back = ctx.part_element_world_aabb(back, elem="backrest_cushion")
    ctx.check(
        "backrest reclines from upright to a flat bed panel",
        rest_back is not None
        and reclined_back is not None
        and reclined_back[1][2] < rest_back[1][2] - 0.20
        and reclined_back[0][1] < rest_back[0][1] - 0.20,
        details=f"rest={rest_back}, reclined={reclined_back}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "folded_sofa_narrow_min_height",
        {
            "base_leg": "tapered_walnut",
            "arm_style": "track_arm",
            "deck_support": "single_post",
            "deck_leg_count": 2,
            "width_m": 1.70,
            "seat_depth_m": 0.55,
            "bed_height_m": 0.38,
        },
        reason="minimum width/depth/height, minimum deck legs — tightest folded sofa",
    ),
    corner_case(
        "deployed_bed_wide_max_height",
        {
            "base_leg": "hairpin_steel",
            "arm_style": "roll_arm",
            "deck_support": "splayed_strut",
            "deck_leg_count": 4,
            "width_m": 2.10,
            "seat_depth_m": 0.68,
            "bed_height_m": 0.44,
        },
        reason="maximum envelope with four splayed deck legs — fully deployed bed",
    ),
    corner_case(
        "wide_bolster_triple_deck",
        {
            "base_leg": "splayed_chrome",
            "arm_style": "bolster_arm",
            "deck_support": "single_post",
            "deck_leg_count": 3,
            "width_m": 2.00,
            "seat_depth_m": 0.62,
            "bed_height_m": 0.41,
        },
        reason="mid envelope, three deck legs, source-like chrome/bolster identity",
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
    "build_picturex_0611_folding_sofa_bed",
    "build_seeded_picturex_0611_folding_sofa_bed",
    "run_picturex_0611_folding_sofa_bed_tests",
]
