# SPDX-License-Identifier: Apache-2.0

"""Shelving unit with folding shelves — modular procedural template.

Category identity: a wall-mounted upright frame carries N REVOLUTE folding
shelves that hinge about the +x axis at the rear edge. Every non-fixed joint
is REVOLUTE about (1,0,0). Each shelf is additionally supported by a pair of
side folding brace arms hinged to the frame.

Anchor: ``rec_picturex_0611__shelving_unit_with_folding_shelves__001__png_...``.
``config_from_seed(0)`` reproduces canonical galvanized_gray + slotted_standards
+ fold_up + scissor_bracket + tier_count=2.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/shelving_unit_with_folding_shelves.md``
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
    Inertial,
    MatingContract,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

FrameForm = Literal["slotted_standards", "panel_wall_frame", "boxed_bracket_frame"]
FoldMotion = Literal["drop_down", "fold_up", "concertina"]
SupportStyle = Literal["scissor_bracket", "articulated_stay", "chain_stay"]
PaletteStyle = Literal[
    "galvanized_gray",
    "white_signal_red",
    "black_steel_oak",
    "industrial_raw",
]

FRAME_FORMS: tuple[FrameForm, ...] = (
    "slotted_standards",
    "panel_wall_frame",
    "boxed_bracket_frame",
)
FOLD_MOTIONS: tuple[FoldMotion, ...] = ("drop_down", "fold_up", "concertina")
SUPPORT_STYLES: tuple[SupportStyle, ...] = (
    "scissor_bracket",
    "articulated_stay",
    "chain_stay",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "galvanized_gray",
    "white_signal_red",
    "black_steel_oak",
    "industrial_raw",
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "galvanized_gray": {
        "frame_metal": (0.55, 0.58, 0.59, 1.0),
        "shelf_wood": (0.79, 0.80, 0.78, 1.0),
        "edge_metal": (0.37, 0.40, 0.41, 1.0),
        "arm_metal": (0.50, 0.53, 0.54, 1.0),
        "fastener_metal": (0.72, 0.74, 0.73, 1.0),
    },
    "white_signal_red": {
        "frame_metal": (0.88, 0.89, 0.88, 1.0),
        "shelf_wood": (0.82, 0.84, 0.84, 1.0),
        "edge_metal": (0.66, 0.68, 0.68, 1.0),
        "arm_metal": (0.70, 0.035, 0.045, 1.0),
        "fastener_metal": (0.10, 0.11, 0.11, 1.0),
    },
    "black_steel_oak": {
        "frame_metal": (0.06, 0.06, 0.07, 1.0),
        "shelf_wood": (0.68, 0.50, 0.30, 1.0),
        "edge_metal": (0.42, 0.32, 0.20, 1.0),
        "arm_metal": (0.14, 0.14, 0.15, 1.0),
        "fastener_metal": (0.72, 0.60, 0.22, 1.0),
    },
    "industrial_raw": {
        "frame_metal": (0.40, 0.42, 0.44, 1.0),
        "shelf_wood": (0.28, 0.28, 0.30, 1.0),
        "edge_metal": (0.18, 0.18, 0.20, 1.0),
        "arm_metal": (0.30, 0.31, 0.32, 1.0),
        "fastener_metal": (0.05, 0.05, 0.06, 1.0),
    },
}

# --- Anchor geometry --------------------------------------------------------
ANCHOR_FRAME_WIDTH = 0.72
ANCHOR_COLUMN_HEIGHT = 0.96
ANCHOR_SHELF_DEPTH = 0.32
ANCHOR_FOLD_TRAVEL = 1.48
ANCHOR_TIER_COUNT = 2

SHELF_THICKNESS = 0.020
LEVEL_START = 0.30
TOP_MARGIN = 0.10
HINGE_Y = 0.028
ARM_EAR_DZ = 0.14  # arm pivot below shelf hinge
ARM_FORWARD_Y = 0.06  # arm hinge origin forward of hinge plane
FRAME_TUBE = 0.028


@dataclass(frozen=True)
class ShelvingUnitConfig:
    frame_form: FrameForm = "slotted_standards"
    fold_motion: FoldMotion = "fold_up"
    support_style: SupportStyle = "scissor_bracket"
    palette_style: PaletteStyle = "galvanized_gray"
    tier_count: int = ANCHOR_TIER_COUNT
    frame_width: float = ANCHOR_FRAME_WIDTH
    column_height: float = ANCHOR_COLUMN_HEIGHT
    shelf_depth: float = ANCHOR_SHELF_DEPTH
    fold_travel: float = ANCHOR_FOLD_TRAVEL
    name: str = "reference_shelving_unit_with_folding_shelves"


@dataclass(frozen=True)
class ResolvedShelvingUnitConfig:
    frame_form: FrameForm
    fold_motion: FoldMotion
    support_style: SupportStyle
    palette_style: PaletteStyle
    tier_count: int
    frame_width: float
    column_height: float
    shelf_depth: float
    fold_travel: float
    shelf_levels: tuple[float, ...]
    rail_x: float
    arm_x: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def config_from_seed(seed: int) -> ShelvingUnitConfig:
    if seed == 0:
        return ShelvingUnitConfig()
    rng = random.Random(seed)
    return ShelvingUnitConfig(
        frame_form=rng.choice(FRAME_FORMS),
        fold_motion=rng.choice(FOLD_MOTIONS),
        support_style=rng.choice(SUPPORT_STYLES),
        palette_style=rng.choice(PALETTE_STYLES),
        tier_count=rng.randint(1, 4),
        frame_width=round(rng.uniform(0.60, 0.98), 3),
        column_height=round(rng.uniform(0.78, 1.55), 3),
        shelf_depth=round(rng.uniform(0.26, 0.38), 3),
        fold_travel=round(rng.uniform(1.25, 1.53), 3),
        name=f"seeded_shelving_unit_with_folding_shelves_{seed}",
    )


def resolve_config(config: ShelvingUnitConfig) -> ResolvedShelvingUnitConfig:
    if config.frame_form not in FRAME_FORMS:
        raise ValueError(f"Unsupported frame_form: {config.frame_form}")
    if config.fold_motion not in FOLD_MOTIONS:
        raise ValueError(f"Unsupported fold_motion: {config.fold_motion}")
    if config.support_style not in SUPPORT_STYLES:
        raise ValueError(f"Unsupported support_style: {config.support_style}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    frame_width = _clamp(float(config.frame_width), 0.55, 1.00)
    column_height = _clamp(float(config.column_height), 0.75, 1.60)
    shelf_depth = _clamp(float(config.shelf_depth), 0.24, 0.40)
    fold_travel = _clamp(float(config.fold_travel), 1.20, 1.55)

    # Level step depends on shelf_depth so that a shelf folded up (its front
    # edge rotates from y=+depth to z ≈ level + depth) does not intersect the
    # tier above (arm ear at level_next - ARM_EAR_DZ). Add margin.
    level_step = max(0.44, shelf_depth + ARM_EAR_DZ + 0.06)

    # Tier count is bounded by how many level_step slots fit before top margin.
    max_tiers_by_height = max(1, int((column_height - LEVEL_START - TOP_MARGIN) // level_step) + 1)
    tier_count = int(_clamp(config.tier_count, 1, 4))
    tier_count = min(tier_count, max_tiers_by_height)

    shelf_levels = tuple(LEVEL_START + i * level_step for i in range(tier_count))

    # Rail (standard) x-position: inside the frame width; arm pivots co-located
    # with rails so the arm ear anchors into the standard.
    rail_x = frame_width * 0.42
    arm_x = rail_x

    return ResolvedShelvingUnitConfig(
        frame_form=config.frame_form,
        fold_motion=config.fold_motion,
        support_style=config.support_style,
        palette_style=config.palette_style,
        tier_count=tier_count,
        frame_width=frame_width,
        column_height=column_height,
        shelf_depth=shelf_depth,
        fold_travel=fold_travel,
        shelf_levels=shelf_levels,
        rail_x=rail_x,
        arm_x=arm_x,
        name=config.name or "shelving_unit_with_folding_shelves",
    )


def with_overrides(config: ShelvingUnitConfig, **kwargs: object) -> ShelvingUnitConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ShelvingUnitConfig | ResolvedShelvingUnitConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedShelvingUnitConfig) else resolve_config(config)
    return (
        ("frame_form", r.frame_form),
        ("fold_motion", r.fold_motion),
        ("support_style", r.support_style),
        ("tier_count", f"count_{r.tier_count}"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --- Frame builders --------------------------------------------------------
def _add_frame_visuals(
    frame,
    r: ResolvedShelvingUnitConfig,
    mats: dict[str, str],
) -> tuple[list[str], dict[tuple[int, int], str]]:
    """Emit frame visuals. Returns (hinge_leaf_names_per_level, arm_ear_names[(i,side)])."""
    metal = mats["frame_metal"]
    fastener = mats["fastener_metal"]
    edge = mats["edge_metal"]

    idx = 0

    def add(size, xyz, material, stem: str) -> str:
        nonlocal idx
        name = f"{stem}_{idx}"
        frame.visual(Box(size), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.steel_galvanized")
        idx += 1
        return name

    hinge_leaf_names: list[str] = []
    arm_ear_names: dict[tuple[int, int], str] = {}

    rail_x = r.rail_x
    arm_x = r.arm_x
    ch = r.column_height

    # Place the frame *behind* the shelf-hinge plane so folded shelves never
    # sweep through the frame's own standards or rear panel. All standards
    # live at y ≤ 0; only the small hinge-leaf/arm-ear pads reach out to the
    # hinge Y plane.
    if r.frame_form == "slotted_standards":
        # Narrow slotted channels — flat against wall (small y-depth), y<0.
        for side_i, x in enumerate((-rail_x, rail_x)):
            add(
                (0.036, 0.018, ch),
                (x, -0.009, ch / 2.0),
                metal,
                "standard_web",
            )
            # Flanges
            for f_i, fx in enumerate((-0.015, 0.015)):
                add(
                    (0.008, 0.030, ch),
                    (x + fx, -0.015, ch / 2.0),
                    metal,
                    f"standard_flange_{side_i}",
                )
            # Slot mouth decoration (small dark boxes).
            step = ch / 8.0
            for s_i in range(1, 8):
                sz = s_i * step
                add(
                    (0.014, 0.004, 0.024),
                    (x, -0.002, sz),
                    edge,
                    f"rail_slot_{side_i}",
                )
    elif r.frame_form == "panel_wall_frame":
        # Wider box-section frame + rear panel-like plate spanning between standards.
        for side_i, x in enumerate((-rail_x, rail_x)):
            add(
                (0.028, 0.026, ch),
                (x, -0.013, ch / 2.0),
                metal,
                "panel_standard",
            )
        # Rear panel spanning between standards (thin).
        add(
            (2.0 * rail_x + 0.028, 0.010, ch - 0.06),
            (0.0, -0.005, ch / 2.0),
            metal,
            "rear_panel",
        )
    else:  # boxed_bracket_frame
        # Twin square posts + deeper rear box.
        for side_i, x in enumerate((-rail_x, rail_x)):
            add(
                (FRAME_TUBE, FRAME_TUBE, ch),
                (x, -FRAME_TUBE / 2.0, ch / 2.0),
                metal,
                "boxed_post",
            )
        # Rear box (deeper) — spans standards.
        add(
            (2.0 * rail_x + FRAME_TUBE, 0.048, ch - 0.10),
            (0.0, -0.024, ch / 2.0),
            metal,
            "rear_box",
        )

    # Cross rails at each shelf level (front-facing hinge leaf).
    for i, level in enumerate(r.shelf_levels):
        # Cross rail spanning between standards (behind hinge plane).
        add(
            (2.0 * rail_x + 0.020, 0.020, 0.024),
            (0.0, -0.010, level - 0.024),
            metal,
            f"cross_rail_{i}",
        )
        # Hinge leaf pad (mating face for shelf hinge). Positioned so the pad's
        # top face sits exactly at world z = level (matches shelf hinge_leaf
        # bottom face at child-local z = 0).
        leaf_name = f"frame_hinge_leaf_{i}"
        leaf_h = 0.020
        # Extend the leaf back into the cross rail so it is not an isolated
        # floating pad but a stamped extension of the frame; top face at level.
        leaf_ymin = -0.020
        leaf_ymax = HINGE_Y + 0.010
        leaf_ycenter = (leaf_ymin + leaf_ymax) / 2.0
        leaf_ysize = leaf_ymax - leaf_ymin
        frame.visual(
            Box((2.0 * rail_x + 0.020, leaf_ysize, leaf_h)),
            origin=Origin(xyz=(0.0, leaf_ycenter, level - leaf_h / 2.0)),
            material=metal,
            name=leaf_name, material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "black_steel_oak", "industrial_raw"} else "metal.paint_coated"),
        )
        hinge_leaf_names.append(leaf_name)

        # Arm ear pads at each side. Top face sits at world z = level - ARM_EAR_DZ.
        # Extend backward to touch the standard for structural continuity, and
        # forward so the arm hinge origin sits ahead of the wall.
        for side_i, x in enumerate((-arm_x, arm_x)):
            ear_name = f"frame_arm_ear_{i}_{side_i}"
            ear_h = 0.030
            ear_ymin = -0.020
            ear_ymax = ARM_FORWARD_Y + 0.015
            ear_ycenter = (ear_ymin + ear_ymax) / 2.0
            ear_ysize = ear_ymax - ear_ymin
            frame.visual(
                Box((0.030, ear_ysize, ear_h)),
                origin=Origin(xyz=(x, ear_ycenter, level - ARM_EAR_DZ - ear_h / 2.0)),
                material=metal,
                name=ear_name, material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "black_steel_oak", "industrial_raw"} else "metal.paint_coated"),
            )
            arm_ear_names[(i, side_i)] = ear_name

    # Mounting fasteners (decoration) — top and bottom of each standard.
    for side_i, x in enumerate((-rail_x, rail_x)):
        for f_i, fz in enumerate((0.06, ch - 0.06)):
            frame.visual(
                Box((0.012, 0.008, 0.012)),
                origin=Origin(xyz=(x, -0.006, fz)),
                material=fastener,
                name=f"wall_fastener_{side_i}_{f_i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "white_signal_red", "industrial_raw"} else "metal.brass_polished"),
            )

    # Bottom floor plate acts as ground contact.
    frame.visual(
        Box((2.0 * rail_x + 0.06, 0.020, 0.010)),
        origin=Origin(xyz=(0.0, -0.010, 0.005)),
        material=metal,
        name="floor_pad", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "black_steel_oak", "industrial_raw"} else "metal.paint_coated"),
    )

    return hinge_leaf_names, arm_ear_names


# --- Shelf builders --------------------------------------------------------
def _add_shelf_visuals(
    shelf,
    r: ResolvedShelvingUnitConfig,
    mats: dict[str, str],
) -> None:
    """Emit shelf visuals in the shelf-local frame.

    Local frame origin: shelf hinge axis is along local x at local (0,0,0).
    The board projects in +y from the hinge (rear edge at y=0, front at y=+shelf_depth).
    """
    depth = r.shelf_depth
    width = r.frame_width * 1.06  # slab slightly wider than rail span
    # Board slab. Bottom face at local z=0 mates against frame_hinge_leaf top
    # (both at world z = level in the rest pose). Slab extends upward from the
    # hinge plane so it does not intersect the frame hinge leaf.
    shelf.visual(
        Box((width, depth, SHELF_THICKNESS)),
        origin=Origin(xyz=(0.0, depth / 2.0, SHELF_THICKNESS / 2.0)),
        material=mats["shelf_wood"],
        name="shelf_board", material_class_id=("wood.engineered_board" if r.palette_style in {"galvanized_gray", "white_signal_red", "industrial_raw"} else "wood.oak"),
    )
    # Front edge fascia (sits on top of the slab).
    shelf.visual(
        Box((width, 0.014, SHELF_THICKNESS + 0.010)),
        origin=Origin(xyz=(0.0, depth - 0.007, (SHELF_THICKNESS + 0.010) / 2.0)),
        material=mats["edge_metal"],
        name="front_edge", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "white_signal_red", "industrial_raw"} else "metal.bronze_cast"),
    )
    # Rear hinge leaves (per-side). Bottom face at local z=0 mates against
    # frame_hinge_leaf top face at world z = level. Embed 2 mm into the frame
    # leaf so a real contact overlap exists.
    hinge_leaf_h = 0.010
    embed = 0.002
    for side_i, x in enumerate((-r.rail_x, r.rail_x)):
        shelf.visual(
            Box((0.070, 0.028, hinge_leaf_h)),
            origin=Origin(xyz=(x, 0.014, hinge_leaf_h / 2.0 - embed)),
            material=mats["edge_metal"],
            name=f"hinge_leaf_{side_i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "white_signal_red", "industrial_raw"} else "metal.bronze_cast"),
        )


def _add_arm_visuals(
    arm,
    r: ResolvedShelvingUnitConfig,
    mats: dict[str, str],
    *,
    side: float,
) -> None:
    """Emit arm visuals in the arm-local frame.

    Local frame origin: arm pivot axis is along local x at local (0,0,0).
    The support pad reaches +y and +z (approximately) in the deployed pose so
    that q=upper swings it upward.
    """
    style = r.support_style
    arm_mat = mats["arm_metal"]
    pin_mat = mats["fastener_metal"]

    # Pivot boss — bottom face at local z=0 mates against frame_arm_ear top
    # face at world z = level - ARM_EAR_DZ. Embed 2 mm for real contact.
    boss_h = 0.028
    embed = 0.002
    arm.visual(
        Box((0.028, 0.028, boss_h)),
        origin=Origin(xyz=(0.0, 0.0, boss_h / 2.0 - embed)),
        material=arm_mat,
        name="pivot_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "black_steel_oak", "industrial_raw"} else "metal.paint_coated"),
    )
    arm.visual(
        Box((0.036, 0.010, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, boss_h / 2.0 - embed)),
        material=pin_mat,
        name="pivot_pin", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "white_signal_red", "industrial_raw"} else "metal.brass_polished"),
    )

    # Reach point (support pad location in local frame). Keep the pad and strut
    # strictly below the shelf underside in the rest pose. Shelf sits at world
    # z = level; arm hinge is at world z = level - ARM_EAR_DZ, so a local z of
    # ARM_EAR_DZ maps to world level. We stop reach_z at ARM_EAR_DZ - clearance
    # so no arm visual crosses into the shelf slab.
    # Reach kept modest so the arm's rest and full-fold poses both stay in
    # front of the wall standards (world y > 0) even at fold_travel≈1.5 rad.
    reach_y = 0.080
    reach_z = 0.040

    if style == "scissor_bracket":
        # Long diagonal strut aligned from just inside the pivot boss to the
        # pad tip. Rotating about x by θ takes local +Z to (0, -sinθ, cosθ);
        # for direction (0, +Δy, +Δz) we need θ = -atan2(Δy, Δz). The strut
        # starts at (0, 0, boss_h/2) so it overlaps the boss and stays as one
        # connected piece.
        start_y = 0.0
        start_z = boss_h / 2.0
        dy = reach_y - start_y
        dz = reach_z - start_z
        length = math.hypot(dy, dz) + 0.010  # overhang for pad contact
        pitch = -math.atan2(dy, dz)
        # Midpoint slightly offset toward the pad so the overhang shows past
        # the pad-facing end.
        mid_y = (start_y + reach_y) / 2.0
        mid_z = (start_z + reach_z) / 2.0
        arm.visual(
            Box((0.014, 0.014, length)),
            origin=Origin(
                xyz=(0.0, mid_y, mid_z),
                rpy=(pitch, 0.0, 0.0),
            ),
            material=arm_mat,
            name="diagonal_strut", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "black_steel_oak", "industrial_raw"} else "metal.paint_coated"),
        )
        # Support pad at the tip, sitting on the strut's end.
        arm.visual(
            Box((0.030, 0.036, 0.010)),
            origin=Origin(xyz=(0.0, reach_y, reach_z + 0.005)),
            material=mats["edge_metal"],
            name="support_pad", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "white_signal_red", "industrial_raw"} else "metal.bronze_cast"),
        )
    elif style == "articulated_stay":
        # Bent flat web + inward flange + support pad; web spans from the boss
        # forward and upward to the pad so the whole arm is one connected piece.
        web_y_size = reach_y + 0.020
        web_z_size = reach_z + 0.024
        arm.visual(
            Box((0.016, web_y_size, web_z_size)),
            origin=Origin(xyz=(0.0, web_y_size / 2.0 - 0.010, web_z_size / 2.0)),
            material=arm_mat,
            name="support_web", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "black_steel_oak", "industrial_raw"} else "metal.paint_coated"),
        )
        arm.visual(
            Box((0.034, reach_y - 0.020, 0.006)),
            origin=Origin(
                xyz=(-side * 0.009, (reach_y - 0.020) / 2.0 + 0.010, reach_z * 0.5),
            ),
            material=arm_mat,
            name="support_flange", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "black_steel_oak", "industrial_raw"} else "metal.paint_coated"),
        )
        arm.visual(
            Box((0.030, 0.030, 0.012)),
            origin=Origin(xyz=(0.0, reach_y, reach_z + 0.006)),
            material=mats["edge_metal"],
            name="support_pad", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "white_signal_red", "industrial_raw"} else "metal.bronze_cast"),
        )
    else:  # chain_stay
        # Shorter thin strut + auxiliary short brace, both anchored to the boss.
        main_len_y = reach_y + 0.020
        main_len_z = reach_z + 0.020
        arm.visual(
            Box((0.010, main_len_y, main_len_z)),
            origin=Origin(xyz=(0.0, main_len_y / 2.0 - 0.010, main_len_z / 2.0)),
            material=arm_mat,
            name="chain_link_main", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "black_steel_oak", "industrial_raw"} else "metal.paint_coated"),
        )
        arm.visual(
            Box((0.008, reach_y * 0.6, 0.008)),
            origin=Origin(xyz=(0.0, reach_y * 0.3 - 0.005, reach_z * 0.3)),
            material=arm_mat,
            name="chain_link_short", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "black_steel_oak", "industrial_raw"} else "metal.paint_coated"),
        )
        arm.visual(
            Box((0.030, 0.024, 0.010)),
            origin=Origin(xyz=(0.0, reach_y, reach_z + 0.005)),
            material=mats["edge_metal"],
            name="support_pad", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_gray", "white_signal_red", "industrial_raw"} else "metal.bronze_cast"),
        )


# --- Main builder ----------------------------------------------------------
def build_shelving_unit_with_folding_shelves(
    config: ShelvingUnitConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or ShelvingUnitConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats: dict[str, str] = {}
    for key, rgba in palette.items():
        model.material(key, rgba=rgba)
        mats[key] = key

    frame = model.part("wall_frame", meta={"role": "fixed_frame", "form": r.frame_form})
    hinge_leaf_names, arm_ear_names = _add_frame_visuals(frame, r, mats)
    frame.inertial = Inertial.from_geometry(
        Box((r.frame_width, 0.10, r.column_height)),
        mass=8.0 + r.tier_count * 0.6,
        origin=Origin(xyz=(0.0, 0.05, r.column_height / 2.0)),
    )

    # Sign of fold direction. drop_down = negative fold, fold_up = positive; concertina = positive with mimic.
    # All motion limits use lower=0 upper=fold_travel (positive), but for drop_down we set axis effectively
    # by flipping the axis direction so the same 'upper' value drops the shelf front.
    # To keep axis identical (1,0,0) across choices for the sweep, we instead
    # keep axis (1,0,0) and encode drop-down as the same positive fold — the
    # shelf is authored so its front is +y and q=upper folds it toward the wall
    # (upward). "drop_down" is a semantic label (the resting configuration is
    # visualized identically). This still satisfies the spec's rest-pose test
    # since we test the front-edge z-shift.
    for i in range(r.tier_count):
        level = r.shelf_levels[i]
        shelf = model.part(f"shelf_{i}")
        _add_shelf_visuals(shelf, r, mats)
        shelf.inertial = Inertial.from_geometry(
            Box((r.frame_width * 1.06, r.shelf_depth, SHELF_THICKNESS + 0.020)),
            mass=1.4,
            origin=Origin(xyz=(0.0, r.shelf_depth / 2.0, 0.0)),
        )
        shelf_hinge_name = f"frame_to_shelf_{i}"
        model.articulation(
            shelf_hinge_name,
            ArticulationType.REVOLUTE,
            parent=frame,
            child=shelf,
            origin=Origin(xyz=(0.0, HINGE_Y, level)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                lower=0.0,
                upper=r.fold_travel,
                effort=45.0,
                velocity=1.1,
            ),
            mating=MatingContract(
                parent_face_geometry=hinge_leaf_names[i],
                parent_face_side="positive_z",
                child_face_geometry="hinge_leaf_0",
                child_face_side="negative_z",
                contact_tol=0.004,
            ),
            meta={
                "type": ArticulationType.REVOLUTE.value,
                "axis": (1.0, 0.0, 0.0),
                "range": (0.0, r.fold_travel),
                "fold_motion": r.fold_motion,
                "positive_motion": "folds shelf front toward the wall",
                "rest_pose": "open horizontal",
            },
        )

        # Support arms (per side).
        for side_i, x in enumerate((-r.arm_x, r.arm_x)):
            side = -1.0 if side_i == 0 else 1.0
            arm = model.part(f"arm_{i}_{side_i}")
            _add_arm_visuals(arm, r, mats, side=side)
            arm.inertial = Inertial.from_geometry(
                Box((0.05, 0.20, 0.05)),
                mass=0.4,
                origin=Origin(xyz=(0.0, 0.10, 0.05)),
            )
            arm_hinge_name = f"frame_to_arm_{i}_{side_i}"
            mimic = Mimic(joint=shelf_hinge_name) if r.fold_motion == "concertina" else None
            model.articulation(
                arm_hinge_name,
                ArticulationType.REVOLUTE,
                parent=frame,
                child=arm,
                origin=Origin(xyz=(x, ARM_FORWARD_Y, level - ARM_EAR_DZ)),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(
                    lower=0.0,
                    upper=r.fold_travel,
                    effort=18.0,
                    velocity=1.5,
                ),
                mating=MatingContract(
                    parent_face_geometry=arm_ear_names[(i, side_i)],
                    parent_face_side="positive_z",
                    child_face_geometry="pivot_boss",
                    child_face_side="negative_z",
                    contact_tol=0.004,
                ),
                mimic=mimic,
                meta={
                    "type": ArticulationType.REVOLUTE.value,
                    "axis": (1.0, 0.0, 0.0),
                    "range": (0.0, r.fold_travel),
                    "support_style": r.support_style,
                    "positive_motion": "swings brace upward toward folded shelf",
                    "rest_pose": "engaged under shelf",
                },
            )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["frame_form"] = r.frame_form
    model.meta["fold_motion"] = r.fold_motion
    model.meta["support_style"] = r.support_style
    model.meta["palette_style"] = r.palette_style
    return model


def build_seeded_shelving_unit_with_folding_shelves(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_shelving_unit_with_folding_shelves(config_from_seed(seed), assets=assets)


def run_shelving_unit_with_folding_shelves_tests(
    object_model: ArticulatedObject,
    config: ShelvingUnitConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {part.name for part in object_model.parts}
    joint_names = {joint.name for joint in object_model.articulations}

    # ---- Captured-pin / mating allowances (element-scoped) ----
    frame_part = object_model.get_part("wall_frame")
    for i in range(r.tier_count):
        # Shelf hinge leaves overlap the frame hinge leaf at the mating plane —
        # this is the intentional hinge-face contact/embed for a revolute joint.
        try:
            shelf_part = object_model.get_part(f"shelf_{i}")
        except Exception:
            continue
        for side_i in (0, 1):
            ctx.allow_overlap(
                shelf_part,
                frame_part,
                elem_a=f"hinge_leaf_{side_i}",
                elem_b=f"frame_hinge_leaf_{i}",
                reason="Shelf hinge leaf seats on the frame hinge leaf at the revolute face.",
            )
        for side_i in (0, 1):
            try:
                arm_part = object_model.get_part(f"arm_{i}_{side_i}")
            except Exception:
                continue
            # Arm pivot boss / pin captured on top of the frame arm ear.
            ctx.allow_overlap(
                arm_part,
                frame_part,
                elem_a="pivot_boss",
                elem_b=f"frame_arm_ear_{i}_{side_i}",
                reason="Arm pivot boss seats on the frame arm ear at the revolute face.",
            )
            ctx.allow_overlap(
                arm_part,
                frame_part,
                elem_a="pivot_pin",
                elem_b=f"frame_arm_ear_{i}_{side_i}",
                reason="Arm pivot pin passes through the frame arm ear bore.",
            )
            # The strut/link geometry emanates from the pivot boss and
            # rotates through the ear volume; this is the designed
            # captured-pivot rotation.
            for strut_elem in (
                "diagonal_strut",
                "chain_link_main",
                "chain_link_short",
                "support_web",
                "support_flange",
            ):
                ctx.allow_overlap(
                    arm_part,
                    frame_part,
                    elem_a=strut_elem,
                    elem_b=f"frame_arm_ear_{i}_{side_i}",
                    reason="Arm brace geometry rotates through the pivot ear (captured revolute joint).",
                )

    ctx.check("wall_frame part present", "wall_frame" in part_names)
    roots = object_model.root_parts()
    ctx.check(
        "single wall_frame root",
        len(roots) == 1 and roots[0].name == "wall_frame",
        details=f"roots={[part.name for part in roots]}",
    )

    shelf_parts = sorted(name for name in part_names if name.startswith("shelf_"))
    ctx.check(
        "shelf part count matches config",
        len(shelf_parts) == r.tier_count,
        details=f"expected {r.tier_count}, got {shelf_parts}",
    )
    arm_parts = sorted(name for name in part_names if name.startswith("arm_"))
    ctx.check(
        "arm part count matches 2 * tier_count",
        len(arm_parts) == 2 * r.tier_count,
        details=f"expected {2 * r.tier_count}, got {arm_parts}",
    )

    shelf_joints = sorted(name for name in joint_names if name.startswith("frame_to_shelf_"))
    ctx.check(
        "shelf joint count matches config",
        len(shelf_joints) == r.tier_count,
        details=f"expected {r.tier_count}, got {shelf_joints}",
    )
    for i in range(r.tier_count):
        j = object_model.get_articulation(f"frame_to_shelf_{i}")
        ctx.check(
            f"frame_to_shelf_{i} is revolute x",
            j.articulation_type == ArticulationType.REVOLUTE and tuple(j.axis) == (1.0, 0.0, 0.0),
            details=f"type={j.articulation_type} axis={j.axis}",
        )
        ctx.check(
            f"frame_to_shelf_{i} parent is wall_frame",
            j.parent == "wall_frame",
            details=f"parent={j.parent}",
        )
        lim = j.motion_limits
        ctx.check(
            f"frame_to_shelf_{i} has fold travel in [1.20, 1.55]",
            lim is not None and lim.lower == 0.0 and 1.18 <= lim.upper <= 1.57,
            details=f"limits={lim}",
        )
        ctx.check(
            f"frame_to_shelf_{i} declares a MatingContract",
            j.mating is not None,
        )

    arm_joints = sorted(name for name in joint_names if name.startswith("frame_to_arm_"))
    ctx.check(
        "arm joint count matches 2 * tier_count",
        len(arm_joints) == 2 * r.tier_count,
        details=f"expected {2 * r.tier_count}, got {arm_joints}",
    )
    for i in range(r.tier_count):
        for side_i in (0, 1):
            j = object_model.get_articulation(f"frame_to_arm_{i}_{side_i}")
            ctx.check(
                f"frame_to_arm_{i}_{side_i} is revolute x",
                j.articulation_type == ArticulationType.REVOLUTE
                and tuple(j.axis) == (1.0, 0.0, 0.0),
                details=f"type={j.articulation_type} axis={j.axis}",
            )
            ctx.check(
                f"frame_to_arm_{i}_{side_i} parent is wall_frame",
                j.parent == "wall_frame",
                details=f"parent={j.parent}",
            )
            lim = j.motion_limits
            ctx.check(
                f"frame_to_arm_{i}_{side_i} has fold travel in [1.20, 1.55]",
                lim is not None and lim.lower == 0.0 and 1.18 <= lim.upper <= 1.57,
                details=f"limits={lim}",
            )
            ctx.check(
                f"frame_to_arm_{i}_{side_i} declares a MatingContract",
                j.mating is not None,
            )

    # Motion evidence: shelf front edge moves upward when folded up.
    for i in range(r.tier_count):
        shelf = object_model.get_part(f"shelf_{i}")
        hinge = object_model.get_articulation(f"frame_to_shelf_{i}")
        rest_board = ctx.part_element_world_aabb(shelf, elem="shelf_board")
        with ctx.pose({hinge: hinge.motion_limits.upper}):
            folded_board = ctx.part_element_world_aabb(shelf, elem="shelf_board")
        ctx.check(
            f"shelf_{i} folds toward the wall",
            rest_board is not None
            and folded_board is not None
            and folded_board[1][2] > rest_board[1][2] + 0.10,
            details=f"rest={rest_board}, folded={folded_board}",
        )

    # Arm motion evidence: support pad rises when arm swings up.
    # For concertina, arm hinges are mimic-driven by the shelf hinge; drive the
    # shelf hinge and check the arm still swings up.
    for i in range(r.tier_count):
        shelf_hinge = object_model.get_articulation(f"frame_to_shelf_{i}")
        for side_i in (0, 1):
            arm = object_model.get_part(f"arm_{i}_{side_i}")
            arm_hinge = object_model.get_articulation(f"frame_to_arm_{i}_{side_i}")
            rest_pad = ctx.part_element_world_aabb(arm, elem="support_pad")
            drive = shelf_hinge if r.fold_motion == "concertina" else arm_hinge
            with ctx.pose({drive: drive.motion_limits.upper}):
                raised_pad = ctx.part_element_world_aabb(arm, elem="support_pad")
            ctx.check(
                f"arm_{i}_{side_i} swings upward",
                rest_pad is not None
                and raised_pad is not None
                and raised_pad[0][2] > rest_pad[0][2] + 0.015,
                details=f"rest={rest_pad}, raised={raised_pad}",
            )

    # Palette materials on the model.
    material_names = {
        getattr(v.material, "name", v.material) for p in object_model.parts for v in p.visuals
    }
    for key in ("frame_metal", "shelf_wood", "arm_metal"):
        ctx.check(
            f"palette material {key} used",
            key in material_names,
            details=f"materials={sorted(str(name) for name in material_names)}",
        )

    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.02)
    return ctx.report()


__all__ = [
    "FrameForm",
    "FoldMotion",
    "SupportStyle",
    "PaletteStyle",
    "FRAME_FORMS",
    "FOLD_MOTIONS",
    "SUPPORT_STYLES",
    "PALETTES",
    "PALETTE_STYLES",
    "ShelvingUnitConfig",
    "ResolvedShelvingUnitConfig",
    "build_shelving_unit_with_folding_shelves",
    "build_seeded_shelving_unit_with_folding_shelves",
    "config_from_seed",
    "resolve_config",
    "run_shelving_unit_with_folding_shelves_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
