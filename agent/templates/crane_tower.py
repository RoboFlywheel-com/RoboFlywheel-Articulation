# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Material,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

CraneVariant = Literal[
    "hammerhead",
    "luffing_jib",
    "self_erecting",
    "derrick_pedestal",
    "knuckle_boom",
    "gantry_bridge",
]
MastProfile = Literal["square_lattice", "square_telescoping", "round_pedestal", "portal_frame"]
BaseStyle = Literal["fixed_foundation", "wheeled_outrigger", "pedestal_flange", "portal_runway"]
JibLayout = Literal[
    "horizontal_jib_counterjib",
    "luffing_single_boom",
    "knuckle_two_arm",
    "gantry_bridge",
]
TrolleyMode = Literal["jib_trolley", "fixed_tip_hook", "bridge_crab_trolley"]
HookBlockStyle = Literal["simple_block", "sheaved_block", "curved_hook"]
CabStyle = Literal["center_cab", "side_cab", "machinery_house_only", "none"]
MaterialStyle = Literal["construction_yellow", "industrial_blue", "white_red"]

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "construction_yellow": {
        "structure": (1.0, 0.72, 0.06, 1.0),
        "steel": (0.06, 0.065, 0.07, 1.0),
        "base": (0.36, 0.38, 0.40, 1.0),
        "cab": (0.18, 0.22, 0.25, 1.0),
        "glass": (0.20, 0.43, 0.75, 0.70),
        "hook": (0.85, 0.08, 0.04, 1.0),
        "counterweight": (0.42, 0.41, 0.38, 1.0),
    },
    "industrial_blue": {
        "structure": (0.10, 0.34, 0.66, 1.0),
        "steel": (0.24, 0.26, 0.30, 1.0),
        "base": (0.48, 0.50, 0.53, 1.0),
        "cab": (0.16, 0.18, 0.22, 1.0),
        "glass": (0.62, 0.76, 0.90, 0.36),
        "hook": (0.88, 0.10, 0.06, 1.0),
        "counterweight": (0.38, 0.38, 0.36, 1.0),
    },
    "white_red": {
        "structure": (0.90, 0.88, 0.82, 1.0),
        "steel": (0.28, 0.30, 0.33, 1.0),
        "base": (0.58, 0.58, 0.56, 1.0),
        "cab": (0.78, 0.08, 0.06, 1.0),
        "glass": (0.58, 0.76, 0.92, 0.36),
        "hook": (0.80, 0.05, 0.03, 1.0),
        "counterweight": (0.45, 0.44, 0.42, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Shared interface constants (single source of truth).
# Rail bars, rail-carrying verticals, trolley joint origin, and the slewing
# seat plate are all derived from these values so mating geometry stays
# consistent for every sampled config.
# ---------------------------------------------------------------------------
# Slewing bearing ring (upperworks torus); the base seat plate spans its
# full footprint so the plan overlap with the lower bearing plate >= 2.0.
SLEW_RING_RADIUS = 1.18
SLEW_RING_TUBE = 0.10
# Under-hung trolley rails on the hammerhead jib.
RAIL_THICKNESS = 0.11
RAIL_Z = 0.80  # rail bar center height in the upperworks frame
RAIL_X_START = 0.95  # rail start inset from the mast centerline
RAIL_X_END_INSET = 0.8  # rail end inset from the jib tip
# Rail bogies (trolley frame); the bogie top faces key onto the rail bottoms.
BOGIE_Z_SIZE = 0.08
BOGIE_CENTER_Z = -0.015
# Trolley joint origin height, solved from the rail/bogie keying constraint:
# origin_z + bogie top offset == rail bottom face.
TROLLEY_ORIGIN_Z = RAIL_Z - RAIL_THICKNESS / 2.0 - (BOGIE_CENTER_Z + BOGIE_Z_SIZE / 2.0)
# Trolley home position along the jib: crossbeam rear edge stays clear of the
# rail start inset.
TROLLEY_HOME_X = 2.0


@dataclass(frozen=True)
class CraneTowerConfig:
    crane_variant: CraneVariant = "hammerhead"
    mast_profile: MastProfile = "square_lattice"
    base_style: BaseStyle = "fixed_foundation"
    jib_layout: JibLayout = "horizontal_jib_counterjib"
    trolley_mode: TrolleyMode = "jib_trolley"
    hook_block_style: HookBlockStyle = "sheaved_block"
    cab_style: CabStyle = "side_cab"
    material_style: MaterialStyle = "construction_yellow"
    mast_height: float = 20.0
    mast_panel_count: int = 8
    jib_length: float = 24.0
    truss_panel_count: int = 8
    counter_jib_length_ratio: float = 0.36
    ballast_block_count: int = 3
    hook_drop: float = 4.0
    slew_range: float | Literal["continuous"] = math.pi
    name: str = "reference_crane_tower"


@dataclass(frozen=True)
class ResolvedCraneTowerConfig:
    crane_variant: CraneVariant
    mast_profile: MastProfile
    base_style: BaseStyle
    jib_layout: JibLayout
    trolley_mode: TrolleyMode
    hook_block_style: HookBlockStyle
    cab_style: CabStyle
    material_style: MaterialStyle
    mast_height: float
    mast_width: float
    mast_panel_count: int
    jib_length: float
    jib_width: float
    truss_panel_count: int
    counter_jib_length: float
    ballast_block_count: int
    hook_drop: float
    trolley_travel: float
    extension_travel: float
    slew_range: float | Literal["continuous"]
    name: str


def config_from_seed(seed: int) -> CraneTowerConfig:
    rng = random.Random(seed)
    # Keep only hammerhead/derrick families for seeded output.
    # Luffing/self-erecting/knuckle/gantry forms are excluded.
    variant: CraneVariant = rng.choice(("hammerhead", "derrick_pedestal"))
    return CraneTowerConfig(
        crane_variant=variant,
        material_style=rng.choice(("construction_yellow", "industrial_blue", "white_red")),
        hook_block_style=rng.choice(("simple_block", "sheaved_block", "curved_hook")),
        cab_style=rng.choice(("center_cab", "side_cab", "machinery_house_only", "none")),
        mast_height=round(rng.uniform(8.0, 24.0), 2),
        mast_panel_count=rng.randint(4, 14),
        jib_length=round(rng.uniform(10.0, 26.0), 2),
        truss_panel_count=rng.randint(4, 12),
        counter_jib_length_ratio=round(rng.uniform(0.28, 0.50), 2),
        ballast_block_count=rng.randint(1, 4),
        hook_drop=round(rng.uniform(2.2, 6.0), 2),
        slew_range="continuous" if rng.random() < 0.65 else round(rng.uniform(1.57, 6.28), 2),
        name=f"seeded_crane_tower_{seed}",
    )


def resolve_config(config: CraneTowerConfig) -> ResolvedCraneTowerConfig:
    variants = {
        "hammerhead",
        "luffing_jib",
        "self_erecting",
        "derrick_pedestal",
        "knuckle_boom",
        "gantry_bridge",
    }
    if config.crane_variant not in variants:
        raise ValueError(f"Unsupported crane_variant: {config.crane_variant}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if config.hook_block_style not in {"simple_block", "sheaved_block", "curved_hook"}:
        raise ValueError(f"Unsupported hook_block_style: {config.hook_block_style}")
    if not 6.0 <= config.mast_height <= 26.0:
        raise ValueError("mast_height must be in [6.0, 26.0]")
    if not 4 <= config.mast_panel_count <= 16:
        raise ValueError("mast_panel_count must be in [4, 16]")
    if not 6.0 <= config.jib_length <= 28.0:
        raise ValueError("jib_length must be in [6.0, 28.0]")
    if not 0.25 <= config.counter_jib_length_ratio <= 0.55:
        raise ValueError("counter_jib_length_ratio must be in [0.25, 0.55]")

    if config.crane_variant in {"luffing_jib", "self_erecting", "knuckle_boom", "gantry_bridge"}:
        config = replace(
            config,
            crane_variant="hammerhead",
            mast_profile="square_lattice",
            base_style="fixed_foundation",
            jib_layout="horizontal_jib_counterjib",
            trolley_mode="jib_trolley",
        )

    mast_profile = config.mast_profile
    base_style = config.base_style
    jib_layout = config.jib_layout
    trolley_mode = config.trolley_mode
    extension_travel = 0.0

    if config.crane_variant == "luffing_jib":
        jib_layout = "luffing_single_boom"
        trolley_mode = "fixed_tip_hook"
    elif config.crane_variant == "self_erecting":
        mast_profile = "square_telescoping"
        base_style = "wheeled_outrigger"
        extension_travel = min(4.0, config.mast_height * 0.18)
    elif config.crane_variant == "derrick_pedestal":
        mast_profile = "round_pedestal"
        base_style = "pedestal_flange"
    elif config.crane_variant == "knuckle_boom":
        jib_layout = "knuckle_two_arm"
        trolley_mode = "fixed_tip_hook"
    elif config.crane_variant == "gantry_bridge":
        mast_profile = "portal_frame"
        base_style = "portal_runway"
        jib_layout = "gantry_bridge"
        trolley_mode = "bridge_crab_trolley"
    elif trolley_mode == "jib_trolley":
        pass  # keep jib_trolley for hammerhead

    mast_width = 2.2 if mast_profile == "square_lattice" else 1.4
    if mast_profile == "round_pedestal":
        mast_width = 0.75
    elif mast_profile == "portal_frame":
        mast_width = max(6.0, min(18.0, config.jib_length))
    jib_width = 1.55
    counter_len = config.jib_length * config.counter_jib_length_ratio
    trolley_clearance = 2.0 if jib_layout == "gantry_bridge" else 3.6
    trolley_travel = max(1.0, config.jib_length - trolley_clearance)
    if config.slew_range != "continuous" and not 1.57 <= float(config.slew_range) <= 6.28:
        raise ValueError("slew_range must be 'continuous' or a float in [1.57, 6.28]")

    return ResolvedCraneTowerConfig(
        crane_variant=config.crane_variant,
        mast_profile=mast_profile,
        base_style=base_style,
        jib_layout=jib_layout,
        trolley_mode=trolley_mode,
        hook_block_style=config.hook_block_style,
        cab_style=config.cab_style,
        material_style=config.material_style,
        mast_height=config.mast_height,
        mast_width=mast_width,
        mast_panel_count=config.mast_panel_count,
        jib_length=config.jib_length,
        jib_width=jib_width,
        truss_panel_count=max(4, min(12, config.truss_panel_count)),
        counter_jib_length=counter_len,
        ballast_block_count=max(0, min(6, config.ballast_block_count)),
        hook_drop=max(1.5, min(config.hook_drop, config.mast_height * 0.45)),
        trolley_travel=trolley_travel,
        extension_travel=extension_travel,
        slew_range=config.slew_range,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Geometry helpers — all 3-D diagonal bars use proper pitch+yaw transforms
# ---------------------------------------------------------------------------


def _bar_origin_between(
    p0: tuple[float, float, float], p1: tuple[float, float, float]
) -> tuple[float, Origin]:
    """Return (length, Origin) so that a Box of that length along local +X spans p0→p1."""
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    horizontal = math.sqrt(dx * dx + dy * dy)
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(-dz, horizontal)
    return length, Origin(
        xyz=((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), rpy=(0.0, pitch, yaw)
    )


def _add_bar(
    part,
    name: str,
    p0: tuple[float, float, float],
    p1: tuple[float, float, float],
    thickness: float,
    material: Material,
) -> None:
    """Add a box-section bar whose axis aligns with the vector p0→p1."""
    length, origin = _bar_origin_between(p0, p1)
    part.visual(Box((length, thickness, thickness)), origin=origin, material=material, name=name, material_class_id="metal.paint_coated")


def _add_box(
    part,
    name: str,
    size: tuple[float, float, float],
    center: tuple[float, float, float],
    material: Material,
) -> None:
    part.visual(Box(size), origin=Origin(xyz=center), material=material, name=name, material_class_id="metal.paint_coated")


def _joint_meta(
    joint_type: ArticulationType,
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    limits: MotionLimits | None,
) -> dict[str, object]:
    if joint_type == ArticulationType.CONTINUOUS:
        joint_range: object = "continuous"
    else:
        joint_range = None if limits is None else (limits.lower, limits.upper)
    return {
        "type": joint_type.value,
        "axis": axis,
        "origin": origin,
        "range": joint_range,
    }


# ---------------------------------------------------------------------------
# Mast builders
# ---------------------------------------------------------------------------


def _add_lattice_mast(
    part, resolved: ResolvedCraneTowerConfig, structure: Material, steel: Material
) -> None:
    """Square lattice mast: four corner chords, horizontal ring ties at each panel level,
    and alternating face diagonals on all four faces."""
    w = resolved.mast_width
    h = resolved.mast_height
    half = w / 2.0
    post_size = 0.14

    for ix, x in enumerate((-half, half)):
        for iy, y in enumerate((-half, half)):
            _add_box(
                part,
                f"corner_post_{ix}_{iy}",
                (post_size, post_size, h),
                (x, y, h / 2.0),
                structure,
            )

    _add_box(part, "base_footing", (w + 1.2, w + 1.2, 0.28), (0.0, 0.0, 0.14), steel)
    _add_box(part, "top_bearing_plate", (w + 0.35, w + 0.35, 0.08), (0.0, 0.0, h - 0.04), steel)

    # Ring ties including one close to the top so the bearing plates touch cleanly.
    levels = [i * 2.5 for i in range(int(h / 2.5) + 1)]
    if h - 0.14 not in levels:
        levels.append(h - 0.14)
    levels = sorted(set(levels))

    for li, z in enumerate(levels):
        _add_bar(part, f"front_tie_{li}", (-half, -half, z), (half, -half, z), 0.10, structure)
        _add_bar(part, f"rear_tie_{li}", (-half, half, z), (half, half, z), 0.10, structure)
        _add_bar(part, f"side_tie_0_{li}", (-half, -half, z), (-half, half, z), 0.10, structure)
        _add_bar(part, f"side_tie_1_{li}", (half, -half, z), (half, half, z), 0.10, structure)

    for si, z0 in enumerate(levels[:-1]):
        z1 = levels[si + 1]
        if si % 2 == 0:
            fa, fb = (-half, -half, z0), (half, -half, z1)
            ra, rb = (-half, half, z0), (half, half, z1)
            la, lb = (-half, -half, z0), (-half, half, z1)
            rta, rtb = (half, -half, z0), (half, half, z1)
        else:
            fa, fb = (half, -half, z0), (-half, -half, z1)
            ra, rb = (half, half, z0), (-half, half, z1)
            la, lb = (-half, half, z0), (-half, -half, z1)
            rta, rtb = (half, half, z0), (half, -half, z1)
        _add_bar(part, f"mast_diag_front_{si}", fa, fb, 0.08, steel)
        _add_bar(part, f"mast_diag_rear_{si}", ra, rb, 0.08, steel)
        _add_bar(part, f"mast_diag_side_0_{si}", la, lb, 0.08, steel)
        _add_bar(part, f"mast_diag_side_1_{si}", rta, rtb, 0.08, steel)


def _add_telescoping_mast(
    part, resolved: ResolvedCraneTowerConfig, structure: Material, steel: Material
) -> None:
    w = resolved.mast_width
    h = resolved.mast_height
    sleeve_h = h * 0.62
    wall = 0.11
    _add_box(
        part,
        "mast_sleeve_left_wall",
        (wall, w + wall, sleeve_h),
        (-w / 2.0, 0.0, sleeve_h / 2.0),
        structure,
    )
    _add_box(
        part,
        "mast_sleeve_right_wall",
        (wall, w + wall, sleeve_h),
        (w / 2.0, 0.0, sleeve_h / 2.0),
        structure,
    )
    _add_box(
        part,
        "mast_sleeve_front_wall",
        (w + wall, wall, sleeve_h),
        (0.0, -w / 2.0, sleeve_h / 2.0),
        structure,
    )
    _add_box(
        part,
        "mast_sleeve_rear_wall",
        (w + wall, wall, sleeve_h),
        (0.0, w / 2.0, sleeve_h / 2.0),
        structure,
    )
    _add_box(part, "mast_bottom_collar", (w + 0.34, w + 0.34, 0.18), (0.0, 0.0, 0.09), steel)
    _add_box(
        part, "mast_top_collar", (w + 0.34, w + 0.34, 0.14), (0.0, 0.0, sleeve_h - 0.07), steel
    )


# ---------------------------------------------------------------------------
# Jib/boom builders
# ---------------------------------------------------------------------------


def _add_main_jib(
    part, resolved: ResolvedCraneTowerConfig, structure: Material, steel: Material
) -> None:
    """Hammerhead main jib: double bottom chords, single top chord, cross ties,
    vertical web posts, alternating diagonals, trolley rails, cathead, and pendant stays."""
    length = resolved.jib_length
    y_left = -resolved.jib_width / 2.0
    y_right = resolved.jib_width / 2.0
    jib_start = 0.15
    bottom_z = 1.02
    top_z = 2.34

    # Main jib chords.
    for y, side in ((y_left, "near"), (y_right, "far")):
        _add_bar(
            part,
            f"main_bottom_chord_{side}",
            (jib_start, y, bottom_z),
            (length, y, bottom_z),
            0.16,
            structure,
        )
        _add_bar(
            part,
            f"main_top_chord_{side}",
            (jib_start, y, top_z),
            (length, y, top_z),
            0.13,
            structure,
        )
        # Trolley rail bars below the bottom chords (see RAIL_* constants).
        _add_bar(
            part,
            f"trolley_rail_{side}",
            (RAIL_X_START, y, RAIL_Z),
            (length - RAIL_X_END_INSET, y, RAIL_Z),
            RAIL_THICKNESS,
            steel,
        )

    # Cross ties, vertical posts, and zigzag web diagonals.
    nodes = [
        jib_start + length * i / resolved.truss_panel_count
        for i in range(resolved.truss_panel_count + 1)
    ]
    # The under-hung trolley rails span x in [RAIL_X_START, length - RAIL_X_END_INSET]
    # at RAIL_Z. Vertical posts under the rail span extend down to the rail top
    # face so the rails are carried by the truss instead of floating below the
    # bottom chord.
    rail_top_z = RAIL_Z + RAIL_THICKNESS / 2.0
    rail_x_min = RAIL_X_START
    rail_x_max = length - RAIL_X_END_INSET
    for ni, x in enumerate(nodes):
        _add_bar(
            part,
            f"main_cross_bottom_{ni}",
            (x, y_left, bottom_z),
            (x, y_right, bottom_z),
            0.105,
            structure,
        )
        _add_bar(
            part, f"main_cross_top_{ni}", (x, y_left, top_z), (x, y_right, top_z), 0.095, structure
        )
        vert_bottom_z = rail_top_z if rail_x_min <= x <= rail_x_max else bottom_z
        _add_bar(
            part,
            f"main_vert_near_{ni}",
            (x, y_left, vert_bottom_z),
            (x, y_left, top_z),
            0.095,
            structure,
        )
        _add_bar(
            part,
            f"main_vert_far_{ni}",
            (x, y_right, vert_bottom_z),
            (x, y_right, top_z),
            0.095,
            structure,
        )

    for si in range(len(nodes) - 1):
        x0, x1 = nodes[si], nodes[si + 1]
        for y, side in ((y_left, "left"), (y_right, "right")):
            if si % 2 == 0:
                _add_bar(
                    part, f"jib_{side}_diag_{si}", (x0, y, bottom_z), (x1, y, top_z), 0.085, steel
                )
            else:
                _add_bar(
                    part, f"jib_{side}_diag_{si}", (x0, y, top_z), (x1, y, bottom_z), 0.085, steel
                )

    # Cathead post and cross-arm above the turntable deck.
    _add_bar(part, "cathead_post", (0.0, 0.0, 0.58), (0.0, 0.0, 3.65), 0.18, structure)
    _add_bar(part, "cathead_cross", (0.0, -0.82, 3.55), (0.0, 0.82, 3.55), 0.12, structure)

    # Pendant stays from cathead apex to mid-jib and tip.
    _add_bar(
        part, "main_pendant_near", (0.0, -0.52, 3.55), (length * 0.65, y_left, top_z), 0.055, steel
    )
    _add_bar(
        part, "main_pendant_far", (0.0, 0.52, 3.55), (length * 0.65, y_right, top_z), 0.055, steel
    )
    _add_bar(
        part,
        "main_pendant_near_tip",
        (0.0, -0.52, 3.55),
        (length - 0.5, y_left, top_z),
        0.040,
        steel,
    )
    _add_bar(
        part,
        "main_pendant_far_tip",
        (0.0, 0.52, 3.55),
        (length - 0.5, y_right, top_z),
        0.040,
        steel,
    )

    # Jib tip marker.
    _add_box(part, "jib_tip_marker", (0.38, 0.38, 0.46), (length + 0.10, 0.0, 2.08), structure)


def _add_counter_jib(
    part,
    resolved: ResolvedCraneTowerConfig,
    structure: Material,
    steel: Material,
    counterweight: Material,
) -> None:
    """Counter-jib: shorter truss in the -X direction with concrete ballast blocks."""
    counter_end = -resolved.counter_jib_length
    y_left = -resolved.jib_width / 2.0
    y_right = resolved.jib_width / 2.0
    bottom_z = 1.02
    top_z = 2.34
    nodes = [0.0, counter_end * 0.35, counter_end * 0.70, counter_end]

    for y, side in ((y_left, "near"), (y_right, "far")):
        _add_bar(
            part,
            f"counter_bottom_chord_{side}",
            (0.0, y, bottom_z),
            (counter_end, y, bottom_z),
            0.17,
            structure,
        )
        _add_bar(
            part,
            f"counter_top_chord_{side}",
            (0.0, y, top_z),
            (counter_end, y, top_z),
            0.13,
            structure,
        )

    for ni, x in enumerate(nodes):
        _add_bar(
            part,
            f"counter_cross_bottom_{ni}",
            (x, y_left, bottom_z),
            (x, y_right, bottom_z),
            0.105,
            structure,
        )
        _add_bar(
            part,
            f"counter_cross_top_{ni}",
            (x, y_left, top_z),
            (x, y_right, top_z),
            0.095,
            structure,
        )
        _add_bar(
            part,
            f"counter_vert_near_{ni}",
            (x, y_left, bottom_z),
            (x, y_left, top_z),
            0.095,
            structure,
        )
        _add_bar(
            part,
            f"counter_vert_far_{ni}",
            (x, y_right, bottom_z),
            (x, y_right, top_z),
            0.095,
            structure,
        )

    for si in range(len(nodes) - 1):
        x0, x1 = nodes[si], nodes[si + 1]
        for y, side in ((y_left, "near"), (y_right, "far")):
            _add_bar(
                part, f"counter_web_{side}_{si}", (x0, y, top_z), (x1, y, bottom_z), 0.085, steel
            )

    _add_bar(
        part,
        "counter_pendant_near",
        (0.0, -0.52, 3.55),
        (counter_end * 0.80, y_left, top_z),
        0.055,
        steel,
    )
    _add_bar(
        part,
        "counter_pendant_far",
        (0.0, 0.52, 3.55),
        (counter_end * 0.80, y_right, top_z),
        0.055,
        steel,
    )

    # Ballast blocks stacked at counter-jib end.
    for idx in range(resolved.ballast_block_count):
        x = counter_end + idx * 0.50 + 0.25
        _add_box(part, f"counterweight_{idx}", (0.48, 1.55, 0.92), (x, 0.0, 0.58), counterweight)


# ---------------------------------------------------------------------------
# Turntable / slewing deck
# ---------------------------------------------------------------------------


def _build_turntable(
    turntable,
    resolved: ResolvedCraneTowerConfig,
    structure: Material,
    steel: Material,
    cab_mat: Material,
    glass: Material,
    counterweight: Material,
    *,
    assets: AssetContext,
) -> None:
    """Turntable part: bearing plates, slewing ring torus, machinery deck, cab,
    main jib, and counter-jib."""
    # Lower slewing interface.
    _add_box(turntable, "lower_bearing_plate", (2.65, 2.65, 0.08), (0.0, 0.0, 0.04), steel)
    _add_box(turntable, "bearing_pedestal", (1.15, 1.15, 0.24), (0.0, 0.0, 0.18), steel)
    turntable.visual(
        mesh_from_geometry(
            TorusGeometry(
                radius=SLEW_RING_RADIUS,
                tube=SLEW_RING_TUBE,
                radial_segments=18,
                tubular_segments=64,
            ),
            assets.mesh_path("slewing_ring.obj"),
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.18)),
        material=steel,
        name="slewing_ring", material_class_id="metal.steel_bare",
    )

    # Machinery deck and house.
    _add_box(turntable, "machinery_deck", (2.7, 2.0, 0.42), (-0.18, 0.0, 0.48), structure)
    _add_box(turntable, "machinery_house", (1.4, 1.15, 0.72), (-0.75, 0.0, 0.96), structure)

    # Operator cab.
    if resolved.cab_style != "none":
        cab_x = 0.70 if resolved.cab_style in ("side_cab", "center_cab") else 0.0
        cab_y = -1.18 if resolved.cab_style == "side_cab" else 0.0
        _add_box(turntable, "operator_cab", (0.82, 0.78, 0.68), (cab_x, cab_y, 0.92), cab_mat)
        _add_box(
            turntable, "cab_window", (0.56, 0.035, 0.36), (cab_x + 0.10, cab_y - 0.40, 0.98), glass
        )

    # Jibs (attached to the turntable, rotating with it).
    if resolved.jib_layout == "horizontal_jib_counterjib":
        _add_main_jib(turntable, resolved, structure, steel)
        _add_counter_jib(turntable, resolved, structure, steel, counterweight)
    elif resolved.jib_layout == "knuckle_two_arm":
        # Primary knuckle arm spanning from mast to mid-reach.
        primary_length = resolved.jib_length * 0.55
        secondary_length = resolved.jib_length * 0.45
        knuckle_x = primary_length
        tip_x = knuckle_x + secondary_length
        # hook_origin is at (jib_length * 0.72 + 1.0, 0, 0.82) in upperworks space.
        # We place the hook attachment post so it overlaps both the arm and the hoist cable.
        hook_x = resolved.jib_length * 0.72 + 1.0
        _add_bar(
            turntable,
            "knuckle_primary_arm",
            (0.0, 0.0, 1.2),
            (knuckle_x, 0.0, 1.2),
            0.22,
            structure,
        )
        _add_bar(
            turntable,
            "knuckle_secondary_arm",
            (knuckle_x, 0.0, 1.2),
            (tip_x, 0.0, 1.1),
            0.18,
            structure,
        )
        # Knuckle joint pivot box.
        _add_box(turntable, "knuckle_pivot", (0.28, 0.28, 0.28), (knuckle_x, 0.0, 1.2), steel)
        # Vertical hook attachment post connecting arm to hook cable.
        # Bottom face at z=0.82 (hook origin z) — touching but not overlapping the hoist cable.
        # Post center=(hook_x, 0, 1.01), half-height=0.19 → bottom at 0.82, top at 1.20.
        _add_box(turntable, "hook_attachment_post", (0.14, 0.14, 0.38), (hook_x, 0.0, 1.01), steel)
        # Counter ballast at base.
        _add_box(turntable, "knuckle_ballast", (0.85, 0.62, 0.64), (-0.55, 0.0, 0.80), structure)


# ---------------------------------------------------------------------------
# Trolley and hook builders
# ---------------------------------------------------------------------------


def _build_trolley(
    trolley, resolved: ResolvedCraneTowerConfig, structure: Material, steel: Material
) -> None:
    """Under-hung jib trolley: crossbeam keyed between the rails, four rail bogies,
    and a compact hoist unit hung below the crossbeam.

    The trolley origin sits at TROLLEY_ORIGIN_Z in the upperworks frame, derived
    from the RAIL_*/BOGIE_* constants so that the bogie top faces meet the rail
    bottom faces with zero penetration. The whole carriage stays below the jib
    bottom-chord cross ties (z≈1.02) so it can travel the full rail length without
    colliding with the truss.
    """
    y_left = -resolved.jib_width / 2.0
    y_right = resolved.jib_width / 2.0

    # Central cross-beam above trolley origin. Set Y-span to the rail inner-face
    # distance so the trolley body is laterally keyed into the two rails. Bottom
    # face at z_local=0.0 (the hoist cable top plane).
    crossbeam_y_span = resolved.jib_width - RAIL_THICKNESS
    crossbeam_x_size = 0.82
    crossbeam_z_size = 0.16
    crossbeam_center_z = crossbeam_z_size / 2.0
    _add_box(
        trolley,
        "trolley_crossbeam",
        (crossbeam_x_size, crossbeam_y_span, crossbeam_z_size),
        (0.0, 0.0, crossbeam_center_z),
        steel,
    )

    # Rail bogie pads at y=±jib_width/2, one per corner. Each bogie is centered on
    # its rail and widened inward so it spans the rail-to-crossbeam gap
    # (RAIL_THICKNESS / 2) and overlaps the crossbeam edge by bogie_overlap — the
    # carriage is one connected piece. Bogie top faces meet the rail bottom faces.
    bogie_x_size = 0.18
    bogie_overlap = 0.015
    bogie_y_size = RAIL_THICKNESS + 2.0 * bogie_overlap
    bogie_x_offset = crossbeam_x_size / 2.0 - bogie_x_size / 2.0 - 0.04  # inboard of ends
    for x in (-bogie_x_offset, bogie_x_offset):
        for y, side in ((y_left, "left"), (y_right, "right")):
            _add_box(
                trolley,
                f"rail_bogie_{side}_{'front' if x > 0 else 'rear'}",
                (bogie_x_size, bogie_y_size, BOGIE_Z_SIZE),
                (x, y, BOGIE_CENTER_Z),
                steel,
            )

    # Hoist machinery hung below the crossbeam, offset in +x so the hook cable at
    # local x=0 passes clear. Top face contacts the crossbeam bottom face.
    hoist_x_size = 0.55
    hoist_y_size = 0.45
    hoist_z_size = 0.30
    cable_lane_clearance = 0.125  # gap between hoist house and the cable lane at x=0
    hoist_x_offset = hoist_x_size / 2.0 + cable_lane_clearance
    crossbeam_bottom_z = crossbeam_center_z - crossbeam_z_size / 2.0
    hoist_center_z = crossbeam_bottom_z - hoist_z_size / 2.0
    _add_box(
        trolley,
        "hoist_house",
        (hoist_x_size, hoist_y_size, hoist_z_size),
        (hoist_x_offset, 0.0, hoist_center_z),
        structure,
    )
    drum_radius = 0.10  # fits inside the hoist house (<= hoist_z_size / 2)
    drum_length = hoist_y_size + 0.05  # protrudes slightly past the house sides
    trolley.visual(
        Cylinder(radius=drum_radius, length=drum_length),
        origin=Origin(xyz=(hoist_x_offset, 0.0, hoist_center_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=steel,
        name="hoist_drum", material_class_id="metal.steel_bare",
    )


def _build_hook(
    part,
    resolved: ResolvedCraneTowerConfig,
    steel: Material,
    hook_mat: Material,
    *,
    assets: AssetContext,
) -> None:
    """Hoist cable, upper/lower sheave block, and hook."""
    drop = resolved.hook_drop

    # Main hoist cable cylinder.
    part.visual(
        Cylinder(radius=0.025, length=drop),
        origin=Origin(xyz=(0.0, 0.0, -drop / 2.0)),
        material=steel,
        name="hoist_cable", material_class_id="tech.cable_pipe_bundle",
    )
    # Twin load cables flanking the main cable.
    for y, name in ((-0.07, "hoist_cable_left"), (0.07, "hoist_cable_right")):
        part.visual(
            Cylinder(radius=0.010, length=drop),
            origin=Origin(xyz=(0.0, y, -drop / 2.0)),
            material=steel,
            name=name, material_class_id="tech.cable_pipe_bundle",
        )

    # Vertical stack below the cable end: each element's top face mates with the
    # bottom face of the element above. Centers are derived from the half-heights
    # so the contact chain closes for any hook_drop.
    yoke_z_size = 0.12
    yoke_center_z = -drop - yoke_z_size / 2.0
    _add_box(part, "hanger_yoke", (0.42, 0.30, yoke_z_size), (0.0, 0.0, yoke_center_z), steel)
    block_z_size = 0.48
    block_top_z = yoke_center_z - yoke_z_size / 2.0
    block_center_z = block_top_z - block_z_size / 2.0
    _add_box(part, "hook_block", (0.55, 0.38, block_z_size), (0.0, 0.0, block_center_z), steel)

    if resolved.hook_block_style == "sheaved_block":
        # Sheave axles ride inside the block, a fixed inset below its top face.
        sheave_axle_inset = 0.08
        sheave_center_z = block_top_z - sheave_axle_inset
        for y, name in ((-0.10, "left_sheave"), (0.10, "right_sheave")):
            part.visual(
                Cylinder(radius=0.09, length=0.08),
                origin=Origin(
                    xyz=(0.0, y, sheave_center_z),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=steel,
                name=name, material_class_id="metal.steel_bare",
            )

    if resolved.hook_block_style == "curved_hook":
        # Spline-based curved hook for realistic shape. Root starts inside the
        # hook block (hook_root_inset below its top face), then curves down.
        hook_root_inset = 0.14
        hook_base_z = block_top_z - hook_root_inset
        hook_tube = tube_from_spline_points(
            [
                (0.0, 0.0, hook_base_z),
                (0.0, 0.0, hook_base_z - 0.32),
                (0.18, 0.0, hook_base_z - 0.52),
                (0.10, 0.0, hook_base_z - 0.76),
                (-0.14, 0.0, hook_base_z - 0.68),
                (-0.04, 0.0, hook_base_z - 0.50),
            ],
            radius=0.045,
            samples_per_segment=12,
            radial_segments=18,
            cap_ends=True,
        )
        part.visual(
            mesh_from_geometry(hook_tube, assets.mesh_path("curved_hook_tube.obj")),
            material=hook_mat,
            name="curved_hook_tip", material_class_id="metal.paint_coated",
        )
    elif resolved.hook_block_style == "sheaved_block":
        # Hook stem hangs from the hook-block bottom face; hook tip from the stem.
        stem_length = 0.38
        stem_top_z = block_center_z - block_z_size / 2.0
        stem_center_z = stem_top_z - stem_length / 2.0
        part.visual(
            Cylinder(radius=0.035, length=stem_length),
            origin=Origin(xyz=(0.0, 0.0, stem_center_z)),
            material=hook_mat,
            name="hook_stem", material_class_id="metal.paint_coated",
        )
        tip_z_size = 0.08
        tip_center_z = stem_top_z - stem_length - tip_z_size / 2.0
        _add_box(part, "hook_tip", (0.22, 0.08, tip_z_size), (0.10, 0.0, tip_center_z), hook_mat)


# ---------------------------------------------------------------------------
# Gantry bridge crane (separate variant)
# ---------------------------------------------------------------------------


def _build_gantry_bridge_crane(
    model: ArticulatedObject,
    resolved: ResolvedCraneTowerConfig,
    base_mat: Material,
    structure: Material,
    steel: Material,
    cab_mat: Material,
    glass: Material,
    hook_mat: Material,
    *,
    assets: AssetContext,
) -> None:
    span = resolved.mast_width
    height = max(5.2, min(14.0, resolved.mast_height * 0.62))
    runway_length = max(12.0, resolved.jib_length * 1.45)
    bridge_depth = 1.40

    base = model.part("base")
    for sx, rail_name in ((-1.0, "left"), (1.0, "right")):
        x = sx * span / 2.0
        _add_box(
            base, f"runway_rail_{rail_name}", (0.20, runway_length, 0.16), (x, 0.0, 0.08), steel
        )
        _add_box(
            base,
            f"runway_sleeper_strip_{rail_name}",
            (0.45, runway_length, 0.10),
            (x, 0.0, 0.03),
            base_mat,
        )
    for i in range(7):
        y = -runway_length / 2.0 + runway_length * i / 6.0
        _add_box(base, f"runway_tie_{i}", (span + 0.55, 0.12, 0.08), (0.0, y, 0.04), base_mat)

    bridge = model.part("portal_frame")
    top_z = 0.16 + height
    for sx_i, sx in enumerate((-1.0, 1.0)):
        for sy_i, sy in enumerate((-1.0, 1.0)):
            x = sx * span / 2.0
            y = sy * bridge_depth / 2.0
            _add_box(
                bridge,
                f"portal_leg_{sx_i}_{sy_i}",
                (0.18, 0.18, height),
                (x, y, 0.16 + height / 2.0),
                structure,
            )
            _add_box(
                bridge, f"rail_wheel_bogie_{sx_i}_{sy_i}", (0.52, 0.34, 0.18), (x, y, 0.25), steel
            )
        _add_bar(
            bridge,
            f"portal_side_diag_{'right' if sx > 0 else 'left'}",
            (sx * span / 2.0, -bridge_depth / 2.0, 0.50),
            (sx * span / 2.0, bridge_depth / 2.0, top_z - 0.30),
            0.050,
            steel,
        )
    _add_box(bridge, "bridge_main_girder", (span + 0.90, 0.36, 0.28), (0.0, 0.0, top_z), structure)
    _add_box(
        bridge, "crab_rail_front", (span + 0.50, 0.16, 0.14), (0.0, -0.34, top_z - 0.32), steel
    )
    _add_box(bridge, "crab_rail_rear", (span + 0.50, 0.16, 0.14), (0.0, 0.34, top_z - 0.32), steel)
    for i in range(resolved.truss_panel_count + 1):
        x = -span / 2.0 + span * i / resolved.truss_panel_count
        _add_box(bridge, f"bridge_cross_tie_{i}", (0.06, 0.92, 0.06), (x, 0.0, top_z - 0.15), steel)
    for i in range(resolved.truss_panel_count):
        x0 = -span / 2.0 + span * i / resolved.truss_panel_count
        x1 = -span / 2.0 + span * (i + 1) / resolved.truss_panel_count
        _add_bar(
            bridge,
            f"bridge_left_diag_{i}",
            (x0, -0.18, top_z + 0.12),
            (x1, -0.18, top_z - 0.42),
            0.040,
            steel,
        )
        _add_bar(
            bridge,
            f"bridge_right_diag_{i}",
            (x0, 0.18, top_z - 0.42),
            (x1, 0.18, top_z + 0.12),
            0.040,
            steel,
        )
    if resolved.cab_style != "none":
        cab_x = -span / 2.0 - 0.55
        _add_box(bridge, "gantry_cab", (0.72, 0.54, 0.62), (cab_x, -0.62, top_z - 0.78), cab_mat)
        _add_box(
            bridge, "gantry_cab_glazing", (0.34, 0.02, 0.32), (cab_x, -0.90, top_z - 0.76), glass
        )

    bridge_limits = MotionLimits(
        effort=90000.0, velocity=0.45, lower=0.0, upper=runway_length - bridge_depth
    )
    bridge_origin = (0.0, -runway_length / 2.0 + bridge_depth / 2.0, 0.0)
    model.articulation(
        "bridge_travel_joint",
        ArticulationType.PRISMATIC,
        parent=base,
        child=bridge,
        origin=Origin(xyz=bridge_origin),
        axis=(0.0, 1.0, 0.0),
        motion_limits=bridge_limits,
        meta=_joint_meta(ArticulationType.PRISMATIC, (0.0, 1.0, 0.0), bridge_origin, bridge_limits),
    )

    trolley = model.part("trolley")
    _add_box(trolley, "crab_trolley_frame", (0.94, 0.78, 0.30), (0.0, 0.0, 0.0), steel)
    _add_box(trolley, "crab_hoist_house", (0.58, 0.48, 0.34), (0.0, 0.0, -0.32), structure)
    trolley_limits = MotionLimits(
        effort=17000.0, velocity=0.65, lower=0.0, upper=resolved.trolley_travel
    )
    trolley_origin = (-span / 2.0 + 1.0, 0.0, top_z - 0.54)
    model.articulation(
        "trolley_travel_joint",
        ArticulationType.PRISMATIC,
        parent=bridge,
        child=trolley,
        origin=Origin(xyz=trolley_origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=trolley_limits,
        meta=_joint_meta(
            ArticulationType.PRISMATIC, (1.0, 0.0, 0.0), trolley_origin, trolley_limits
        ),
    )

    hook = model.part("hook_block")
    _build_hook(hook, resolved, steel, hook_mat, assets=assets)
    hook_origin = (0.0, 0.0, -0.49)
    model.articulation(
        "hook_suspension_joint",
        ArticulationType.FIXED,
        parent=trolley,
        child=hook,
        origin=Origin(xyz=hook_origin),
        meta=_joint_meta(ArticulationType.FIXED, (0.0, 0.0, 1.0), hook_origin, None),
    )


# ---------------------------------------------------------------------------
# Main build function
# ---------------------------------------------------------------------------


def build_crane_tower(
    config: CraneTowerConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or CraneTowerConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-crane-tower-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)
    palette = PALETTES[resolved.material_style]
    base_mat = model.material("crane_base", rgba=palette["base"])
    structure = model.material("crane_structure", rgba=palette["structure"])
    steel = model.material("crane_steel", rgba=palette["steel"])
    cab_mat = model.material("crane_cab", rgba=palette["cab"])
    glass = model.material("crane_glass", rgba=palette["glass"])
    hook_mat = model.material("crane_hook", rgba=palette["hook"])
    counterweight_mat = model.material("crane_counterweight", rgba=palette["counterweight"])

    if resolved.crane_variant == "gantry_bridge":
        _build_gantry_bridge_crane(
            model, resolved, base_mat, structure, steel, cab_mat, glass, hook_mat, assets=assets
        )
        return model

    # ------------------------------------------------------------------
    # Base / mast
    # ------------------------------------------------------------------
    base = model.part("base")

    # Derrick pedestal stack (column + flange). The round mast seats directly on
    # the flange top face, and the slewing plane sits one mast_height above it.
    ped_col_len = 0.35
    ped_flange_len = 0.12
    pedestal_top_z = ped_col_len + ped_flange_len

    if resolved.base_style == "wheeled_outrigger":
        _add_box(base, "wheeled_chassis", (3.8, 1.6, 0.32), (0.0, 0.0, 0.16), base_mat)
        for sx_i, sx in enumerate((-1.0, 1.0)):
            for sy_i, sy in enumerate((-1.0, 1.0)):
                _add_box(
                    base,
                    f"outrigger_beam_{sx_i}_{sy_i}",
                    (0.85, 0.12, 0.10),
                    (sx * 1.35, sy * 0.92, 0.34),
                    steel,
                )
                base.visual(
                    Cylinder(radius=0.18, length=0.12),
                    origin=Origin(
                        xyz=(sx * 1.1, sy * 0.92, 0.12),
                        rpy=(math.pi / 2.0, 0.0, 0.0),
                    ),
                    material=steel,
                    name=f"road_wheel_{sx_i}_{sy_i}", material_class_id="rubber.smooth_plain",
                )
    elif resolved.base_style == "pedestal_flange":
        base.visual(
            Cylinder(radius=0.85, length=ped_col_len),
            origin=Origin(xyz=(0.0, 0.0, ped_col_len / 2.0)),
            material=base_mat,
            name="round_pedestal", material_class_id="concrete.smooth_cast",
        )
        base.visual(
            Cylinder(radius=1.15, length=ped_flange_len),
            origin=Origin(xyz=(0.0, 0.0, ped_col_len + ped_flange_len / 2.0)),
            material=steel,
            name="pedestal_flange", material_class_id="metal.steel_bare",
        )
    else:
        _add_box(base, "fixed_foundation", (3.4, 3.4, 0.55), (0.0, 0.0, 0.275), base_mat)
        _add_box(base, "pedestal_cap", (1.6, 1.6, 0.35), (0.0, 0.0, 0.725), base_mat)

    if resolved.mast_profile == "round_pedestal":
        # Round mast column rises from the pedestal flange top to the slewing
        # plane; its free length equals mast_height, so the mast is fully
        # supported by the base.
        round_mast_bottom = pedestal_top_z
        round_mast_top = pedestal_top_z + resolved.mast_height
        base.visual(
            Cylinder(
                radius=resolved.mast_width / 2.0,
                length=round_mast_top - round_mast_bottom,
            ),
            origin=Origin(xyz=(0.0, 0.0, (round_mast_bottom + round_mast_top) / 2.0)),
            material=structure,
            name="round_mast", material_class_id="metal.paint_coated",
        )
        # Slewing-bearing seat: a platform plate spanning the full slewing-ring
        # footprint (2 * (SLEW_RING_RADIUS + SLEW_RING_TUBE)), which also keeps
        # the plan overlap with the upperworks lower bearing plate >= 2.0. Its
        # top face is the slewing plane.
        seat_plate_size = 2.0 * (SLEW_RING_RADIUS + SLEW_RING_TUBE)
        seat_plate_thk = 0.10
        _add_box(
            base,
            "top_bearing_plate",
            (seat_plate_size, seat_plate_size, seat_plate_thk),
            (0.0, 0.0, round_mast_top - seat_plate_thk / 2.0),
            steel,
        )
    elif resolved.mast_profile == "square_telescoping":
        _add_telescoping_mast(base, resolved, structure, steel)
    else:
        _add_lattice_mast(base, resolved, structure, steel)

    # Slew transition stub just below mast top (sits flush under the slewing bearing).
    if resolved.mast_profile != "round_pedestal":
        base.visual(
            Cylinder(radius=0.22, length=0.030),
            origin=Origin(xyz=(0.0, 0.0, resolved.mast_height - 0.020)),
            material=steel,
            name="slew_transition_stub", material_class_id="metal.steel_bare",
        )

    # ------------------------------------------------------------------
    # Optional telescoping inner mast (self_erecting variant)
    # ------------------------------------------------------------------
    mast_parent = base
    if resolved.mast_profile == "round_pedestal":
        slew_z = pedestal_top_z + resolved.mast_height
    else:
        slew_z = resolved.mast_height

    if resolved.extension_travel > 0:
        inner = model.part("inner_mast")
        _add_box(
            inner,
            "telescoping_inner_mast",
            (0.74, 0.74, resolved.mast_height * 0.45),
            (0.0, 0.0, resolved.mast_height * 0.225),
            structure,
        )
        ext_limits = MotionLimits(
            effort=120000.0, velocity=0.18, lower=0.0, upper=resolved.extension_travel
        )
        ext_origin = (0.0, 0.0, resolved.mast_height * 0.58)
        model.articulation(
            "mast_extension_joint",
            ArticulationType.PRISMATIC,
            parent=base,
            child=inner,
            origin=Origin(xyz=ext_origin),
            axis=(0.0, 0.0, 1.0),
            motion_limits=ext_limits,
            meta=_joint_meta(ArticulationType.PRISMATIC, (0.0, 0.0, 1.0), ext_origin, ext_limits),
        )
        mast_parent = inner
        slew_z = resolved.mast_height * 0.45

    # ------------------------------------------------------------------
    # Slewing upperworks
    # ------------------------------------------------------------------
    upperworks = model.part("upperworks")
    _build_turntable(
        upperworks, resolved, structure, steel, cab_mat, glass, counterweight_mat, assets=assets
    )

    slew_type = (
        ArticulationType.CONTINUOUS
        if resolved.slew_range == "continuous"
        else ArticulationType.REVOLUTE
    )
    slew_limits = (
        MotionLimits(effort=250000.0, velocity=0.18)
        if slew_type == ArticulationType.CONTINUOUS
        else MotionLimits(
            effort=250000.0,
            velocity=0.18,
            lower=-float(resolved.slew_range) / 2.0,
            upper=float(resolved.slew_range) / 2.0,
        )
    )
    slew_origin = (0.0, 0.0, slew_z)
    model.articulation(
        "slew_joint",
        slew_type,
        parent=mast_parent,
        child=upperworks,
        origin=Origin(xyz=slew_origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=slew_limits,
        meta=_joint_meta(slew_type, (0.0, 0.0, 1.0), slew_origin, slew_limits),
    )

    # ------------------------------------------------------------------
    # Luffing jib (luffing_jib variant)
    # ------------------------------------------------------------------
    hook_parent = upperworks
    hook_origin: tuple[float, float, float] = (resolved.jib_length * 0.72 + 1.0, 0.0, 0.82)

    if resolved.jib_layout == "luffing_single_boom":
        jib = model.part("jib")
        _add_box(upperworks, "luff_heel_saddle", (0.30, 0.58, 0.22), (1.05, 0.0, 0.69), steel)
        _add_box(upperworks, "luff_cheek_left", (0.18, 0.08, 0.38), (1.05, -0.39, 0.95), steel)
        _add_box(upperworks, "luff_cheek_right", (0.18, 0.08, 0.38), (1.05, 0.39, 0.95), steel)
        jib.visual(
            Cylinder(radius=0.14, length=0.70),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=steel,
            name="hinge_barrel", material_class_id="metal.steel_bare",
        )
        _add_box(
            jib,
            "luffing_boom_truss",
            (resolved.jib_length, 0.42, 0.22),
            (resolved.jib_length / 2.0, 0.0, 0.44),
            structure,
        )
        _add_box(
            jib,
            "luffing_top_chord_left",
            (resolved.jib_length * 0.88, 0.12, 0.10),
            (resolved.jib_length * 0.48, -0.24, 1.10),
            structure,
        )
        _add_box(
            jib,
            "luffing_top_chord_right",
            (resolved.jib_length * 0.88, 0.12, 0.10),
            (resolved.jib_length * 0.48, 0.24, 1.10),
            structure,
        )
        panel_count = max(4, min(10, resolved.truss_panel_count))
        for i in range(panel_count + 1):
            x = resolved.jib_length * i / panel_count
            top_chord_z = 1.34 - 0.48 * i / panel_count
            _add_box(jib, f"luff_cross_tie_{i}", (0.055, 0.56, 0.055), (x, 0.0, 0.58), steel)
            x_next = min(resolved.jib_length, x + resolved.jib_length / panel_count)
            _add_bar(
                jib,
                f"luff_left_web_{i}",
                (x, -0.22, 0.55),
                (x_next, -0.22, top_chord_z),
                0.040,
                steel,
            )
            _add_bar(
                jib,
                f"luff_right_web_{i}",
                (x, 0.22, 0.55),
                (x_next, 0.22, top_chord_z),
                0.040,
                steel,
            )
        jib.visual(
            Cylinder(radius=0.13, length=0.74),
            origin=Origin(
                xyz=(resolved.jib_length - 0.45, 0.0, 0.78),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=steel,
            name="tip_sheave", material_class_id="metal.steel_bare",
        )
        luff_limits = MotionLimits(effort=180000.0, velocity=0.22, lower=0.0, upper=0.95)
        luff_origin = (1.05, 0.0, 0.95)
        model.articulation(
            "luff_joint",
            ArticulationType.REVOLUTE,
            parent=upperworks,
            child=jib,
            origin=Origin(xyz=luff_origin),
            axis=(0.0, -1.0, 0.0),
            motion_limits=luff_limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (0.0, -1.0, 0.0), luff_origin, luff_limits),
        )
        hook_parent = jib
        hook_origin = (resolved.jib_length - 0.6, 0.0, 0.33)

    # ------------------------------------------------------------------
    # Jib trolley (hammerhead variant)
    # ------------------------------------------------------------------
    elif resolved.trolley_mode == "jib_trolley":
        trolley = model.part("trolley")
        _build_trolley(trolley, resolved, structure, steel)

        trolley_limits = MotionLimits(
            effort=25000.0, velocity=0.65, lower=0.0, upper=resolved.trolley_travel
        )
        trolley_origin = (TROLLEY_HOME_X, 0.0, TROLLEY_ORIGIN_Z)
        model.articulation(
            "turntable_to_trolley",
            ArticulationType.PRISMATIC,
            parent=upperworks,
            child=trolley,
            origin=Origin(xyz=trolley_origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=trolley_limits,
            meta=_joint_meta(
                ArticulationType.PRISMATIC, (1.0, 0.0, 0.0), trolley_origin, trolley_limits
            ),
        )
        hook_parent = trolley
        hook_origin = (0.0, 0.0, 0.0)

    # ------------------------------------------------------------------
    # Hook block
    # ------------------------------------------------------------------
    hook = model.part("hook_block")
    _build_hook(hook, resolved, steel, hook_mat, assets=assets)
    model.articulation(
        "hook_suspension_joint",
        ArticulationType.FIXED,
        parent=hook_parent,
        child=hook,
        origin=Origin(xyz=hook_origin),
        meta=_joint_meta(ArticulationType.FIXED, (0.0, 0.0, 1.0), hook_origin, None),
    )

    return model


def build_seeded_crane_tower(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_crane_tower(config_from_seed(seed), assets=assets)


def with_overrides(config: CraneTowerConfig, **kwargs: object) -> CraneTowerConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def run_crane_tower_tests(object_model: ArticulatedObject, config: CraneTowerConfig) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {part.name for part in object_model.parts}
    joint_names = {joint.name for joint in object_model.articulations}

    ctx.check("has hook block", "hook_block" in part_names)

    if resolved.jib_layout == "gantry_bridge":
        ctx.check("gantry has base and portal frame", {"base", "portal_frame"} <= part_names)
        ctx.check(
            "gantry has bridge and trolley joints",
            {"bridge_travel_joint", "trolley_travel_joint"} <= joint_names,
            details=str(joint_names),
        )
        bridge = object_model.get_articulation("bridge_travel_joint")
        trolley_joint = object_model.get_articulation("trolley_travel_joint")
        ctx.check("bridge travels along runway (y-axis)", bridge.axis == (0.0, 1.0, 0.0))
        ctx.check(
            "crab trolley travels across bridge (x-axis)", trolley_joint.axis == (1.0, 0.0, 0.0)
        )
    else:
        ctx.check("tower has base and upperworks", {"base", "upperworks"} <= part_names)
        slew = object_model.get_articulation("slew_joint")
        ctx.check(
            "slew axis is vertical (0,0,1)", slew.axis == (0.0, 0.0, 1.0), details=str(slew.axis)
        )
        ctx.check(
            "slew origin is at mast top (xy≈0)",
            abs(slew.origin.xyz[0]) <= 0.001 and abs(slew.origin.xyz[1]) <= 0.001,
            details=str(slew.origin.xyz),
        )

        # Slewing bearing: upperworks lower plate should sit on mast top bearing plate.
        upperworks_part = object_model.get_part("upperworks")
        base_part = object_model.get_part("base")
        ctx.expect_gap(
            upperworks_part,
            base_part,
            axis="z",
            positive_elem="lower_bearing_plate",
            negative_elem="top_bearing_plate",
            min_gap=0.0,
            max_gap=0.001,
            name="slewing bearing seated on mast",
        )
        ctx.expect_overlap(
            upperworks_part,
            base_part,
            axes="xy",
            elem_a="lower_bearing_plate",
            elem_b="top_bearing_plate",
            min_overlap=2.0,
            name="bearing plates overlap in plan",
        )

    if resolved.jib_layout == "luffing_single_boom":
        luff = object_model.get_articulation("luff_joint")
        ctx.check("luff joint is revolute", luff.articulation_type == ArticulationType.REVOLUTE)
        ctx.check(
            "luff axis is horizontal (y)", tuple(abs(v) for v in luff.axis) == (0.0, 1.0, 0.0)
        )

    if resolved.trolley_mode == "jib_trolley":
        trolley_joint = object_model.get_articulation("turntable_to_trolley")
        ctx.check(
            "trolley travels along jib x-axis",
            trolley_joint.axis == (1.0, 0.0, 0.0),
            details=str(trolley_joint.axis),
        )

        # Trolley travel test: extend to max travel and verify x displacement.
        upperworks_part = object_model.get_part("upperworks")
        trolley_part = object_model.get_part("trolley")
        rest_pos = ctx.part_world_position(trolley_part)
        with ctx.pose({trolley_joint: resolved.trolley_travel}):
            ctx.expect_within(
                trolley_part,
                upperworks_part,
                axes="x",
                inner_elem="trolley_crossbeam",
                outer_elem="trolley_rail_near",
                margin=0.0,
                name="extended trolley stays within rail length",
            )
            # Lateral rail fit: trolley crossbeam is constrained to touch both rail inner faces.
            ctx.expect_gap(
                upperworks_part,
                trolley_part,
                axis="y",
                positive_elem="trolley_rail_far",
                negative_elem="trolley_crossbeam",
                min_gap=0.0,
                max_gap=0.002,
                name="trolley crossbeam touches right rail inner face",
            )
            ctx.expect_gap(
                trolley_part,
                upperworks_part,
                axis="y",
                positive_elem="trolley_crossbeam",
                negative_elem="trolley_rail_near",
                min_gap=0.0,
                max_gap=0.002,
                name="trolley crossbeam touches left rail inner face",
            )
            extended_pos = ctx.part_world_position(trolley_part)
        ctx.check(
            "trolley translates outward along main jib",
            rest_pos is not None
            and extended_pos is not None
            and extended_pos[0] > rest_pos[0] + resolved.trolley_travel * 0.9,
            details=f"rest={rest_pos}, extended={extended_pos}",
        )

    if resolved.jib_layout == "horizontal_jib_counterjib":
        upperworks_part = object_model.get_part("upperworks")
        slew = object_model.get_articulation("slew_joint")
        main_aabb = ctx.part_element_world_aabb(upperworks_part, elem="main_bottom_chord_near")
        counter_aabb = ctx.part_element_world_aabb(
            upperworks_part, elem="counter_bottom_chord_near"
        )
        ctx.check(
            "main jib is longer than counter jib",
            main_aabb is not None
            and counter_aabb is not None
            and main_aabb[1][0] > resolved.jib_length * 0.9
            and counter_aabb[0][0] < -resolved.counter_jib_length * 0.9,
            details=f"main={main_aabb}, counter={counter_aabb}",
        )

        # Slewing rotation test.
        with ctx.pose({slew: math.pi / 2}):
            rotated_main = ctx.part_element_world_aabb(
                upperworks_part, elem="main_bottom_chord_near"
            )
        ctx.check(
            "slewing joint rotates the horizontal jib about the mast",
            rotated_main is not None and rotated_main[1][1] > resolved.jib_length * 0.85,
            details=f"rotated main jib aabb={rotated_main}",
        )

    if resolved.extension_travel > 0:
        ext = object_model.get_articulation("mast_extension_joint")
        ctx.check(
            "mast extension axis is vertical (z)",
            ext.axis == (0.0, 0.0, 1.0),
            details=str(ext.axis),
        )

    for joint in object_model.articulations:
        if joint.articulation_type != ArticulationType.FIXED:
            ctx.check(
                f"{joint.name} has required metadata keys",
                {"type", "axis", "origin", "range"} <= set(joint.meta),
                details=str(joint.meta),
            )

    return ctx.report()
