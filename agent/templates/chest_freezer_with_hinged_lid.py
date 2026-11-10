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
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points,
)

BodyStyle = Literal[
    "residential_white", "commercial_display", "marine_cooler", "laboratory", "split_lid_cooler"
]
LidLayout = Literal["single_hinged", "split_hinged", "sliding_glass"]
LidMaterialStyle = Literal["solid_insulated", "framed_glass"]
HingeStyle = Literal["barrel_pair", "piano", "center_spine", "guide_rail"]
HandleStyle = Literal["front_bar", "recessed", "molded_end_grip", "carry_handle", "none"]
GasketStyle = Literal["thin_black_strip", "compressed_ring", "glass_runner"]
AccessorySet = Literal["none", "control_vent", "stay_and_drain", "display_products"]

HINGE_BARREL_RADIUS = 0.015
HINGE_EDGE_CLEARANCE = 0.030

BODY_PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "residential_white": {
        "shell": (0.92, 0.94, 0.95, 1.0),
        "lid": (0.96, 0.97, 0.98, 1.0),
        "liner": (0.78, 0.86, 0.92, 0.50),
        "trim": (0.42, 0.45, 0.48, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
        "dark": (0.16, 0.17, 0.18, 1.0),
        "steel": (0.62, 0.64, 0.67, 1.0),
    },
    "commercial_display": {
        "shell": (0.16, 0.17, 0.18, 1.0),
        "lid": (0.28, 0.30, 0.31, 1.0),
        "liner": (0.70, 0.86, 0.96, 0.36),
        "trim": (0.72, 0.74, 0.74, 1.0),
        "rubber": (0.035, 0.035, 0.038, 1.0),
        "dark": (0.05, 0.055, 0.06, 1.0),
        "steel": (0.58, 0.60, 0.63, 1.0),
    },
    "marine_cooler": {
        "shell": (0.78, 0.87, 0.90, 1.0),
        "lid": (0.93, 0.95, 0.92, 1.0),
        "liner": (0.66, 0.78, 0.84, 0.42),
        "trim": (0.08, 0.24, 0.36, 1.0),
        "rubber": (0.035, 0.04, 0.045, 1.0),
        "dark": (0.10, 0.14, 0.16, 1.0),
        "steel": (0.60, 0.62, 0.65, 1.0),
    },
    "laboratory": {
        "shell": (0.82, 0.84, 0.82, 1.0),
        "lid": (0.88, 0.89, 0.86, 1.0),
        "liner": (0.76, 0.88, 0.92, 0.44),
        "trim": (0.62, 0.64, 0.65, 1.0),
        "rubber": (0.08, 0.09, 0.10, 1.0),
        "dark": (0.22, 0.23, 0.24, 1.0),
        "steel": (0.60, 0.62, 0.65, 1.0),
    },
    "split_lid_cooler": {
        "shell": (0.24, 0.46, 0.62, 1.0),
        "lid": (0.86, 0.88, 0.84, 1.0),
        "liner": (0.78, 0.88, 0.92, 0.42),
        "trim": (0.18, 0.19, 0.20, 1.0),
        "rubber": (0.035, 0.035, 0.04, 1.0),
        "dark": (0.08, 0.08, 0.085, 1.0),
        "steel": (0.58, 0.60, 0.62, 1.0),
    },
}

SINGLE_HINGED_BODY_STYLES: set[BodyStyle] = {
    "residential_white",
    "marine_cooler",
    "laboratory",
}


def _max_interior_bin_count_for_length(config_length: float) -> int:
    if config_length < 1.15:
        return 1
    if config_length < 1.45:
        return 2
    if config_length < 1.85:
        return 3
    return 4


@dataclass(frozen=True)
class ChestFreezerWithHingedLidConfig:
    body_style: BodyStyle = "residential_white"
    lid_layout: LidLayout = "single_hinged"
    lid_material_style: LidMaterialStyle = "solid_insulated"
    body_length: float = 1.28
    body_width: float = 0.72
    body_height: float = 0.88
    wall_thickness: float = 0.055
    hinge_count: int = 2
    hinge_style: HingeStyle = "barrel_pair"
    handle_style: HandleStyle = "front_bar"
    gasket_style: GasketStyle = "thin_black_strip"
    accessory_set: AccessorySet = "control_vent"
    interior_bin_count: int = 2
    foot_count: int = 4
    foot_height: float = 0.045
    name: str = "reference_chest_freezer"


@dataclass(frozen=True)
class ResolvedChestFreezerWithHingedLidConfig:
    body_style: BodyStyle
    lid_layout: LidLayout
    lid_material_style: LidMaterialStyle
    body_length: float
    body_width: float
    body_height: float
    wall_thickness: float
    hinge_count: int
    hinge_style: HingeStyle
    handle_style: HandleStyle
    gasket_style: GasketStyle
    accessory_set: AccessorySet
    interior_bin_count: int
    foot_count: int
    foot_height: float
    lid_count: int
    lid_thickness: float
    rim_height: float
    opening_length: float
    opening_width: float
    sliding_travel: float
    base_height: float
    liner_floor_z: float
    hinge_y: float
    name: str


def config_from_seed(seed: int) -> ChestFreezerWithHingedLidConfig:
    rng = random.Random(seed)
    # Keep insulated hinged freezer families; sliding glass display cases are a
    # different mechanism and remain excluded from seeded output.
    lid_layout: LidLayout = rng.choice(("single_hinged", "split_hinged"))
    body_style: BodyStyle = rng.choice(
        (
            "residential_white",
            "commercial_display",
            "marine_cooler",
            "laboratory",
            "split_lid_cooler",
        )
    )
    if lid_layout == "split_hinged":
        body_style = "split_lid_cooler"
    elif body_style in {"commercial_display", "split_lid_cooler"}:
        body_style = "residential_white"
    accessory_choices: tuple[AccessorySet, ...] = (
        ("none", "control_vent")
        if lid_layout == "split_hinged"
        else ("none", "control_vent", "stay_and_drain")
    )
    body_length = round(rng.uniform(0.90, 2.40), 3)
    body_width = round(rng.uniform(0.34, 0.95), 3)
    body_height = round(rng.uniform(0.35, 1.0), 3)
    wall_thickness = round(rng.uniform(0.025, 0.075), 3)
    max_bins = _max_interior_bin_count_for_length(body_length)
    bin_candidates = list(range(max_bins + 1))
    # Use a separate deterministic RNG so we don't perturb existing seeded layout/style sampling.
    bin_rng = random.Random(seed ^ 0x5A17C0DE)
    interior_bin_count = bin_rng.choices(bin_candidates, weights=[1] + [3] * max_bins, k=1)[0]
    return ChestFreezerWithHingedLidConfig(
        body_style=body_style,
        lid_layout=lid_layout,
        lid_material_style="solid_insulated",
        body_length=body_length,
        body_width=body_width,
        body_height=body_height,
        wall_thickness=wall_thickness,
        hinge_count=2 if lid_layout == "split_hinged" else rng.choice((2, 3)),
        hinge_style="center_spine" if lid_layout == "split_hinged" else "barrel_pair",
        handle_style=rng.choice(
            ("front_bar", "recessed", "molded_end_grip", "carry_handle", "none")
        ),
        gasket_style=rng.choice(("thin_black_strip", "compressed_ring")),
        accessory_set=rng.choice(accessory_choices),
        interior_bin_count=interior_bin_count,
        foot_count=rng.choice((0, 4)),
        foot_height=round(rng.uniform(0.02, 0.07), 3),
        name=f"seeded_chest_freezer_{seed}",
    )


def resolve_config(
    config: ChestFreezerWithHingedLidConfig,
) -> ResolvedChestFreezerWithHingedLidConfig:
    if config.body_style not in {
        "residential_white",
        "commercial_display",
        "marine_cooler",
        "laboratory",
        "split_lid_cooler",
    }:
        raise ValueError(f"Unsupported body_style: {config.body_style}")
    if config.lid_layout not in {"single_hinged", "split_hinged", "sliding_glass"}:
        raise ValueError(f"Unsupported lid_layout: {config.lid_layout}")
    if config.lid_material_style not in {"solid_insulated", "framed_glass"}:
        raise ValueError(f"Unsupported lid_material_style: {config.lid_material_style}")
    if config.hinge_style not in {"barrel_pair", "piano", "center_spine", "guide_rail"}:
        raise ValueError(f"Unsupported hinge_style: {config.hinge_style}")
    if config.handle_style not in {
        "front_bar",
        "recessed",
        "molded_end_grip",
        "carry_handle",
        "none",
    }:
        raise ValueError(f"Unsupported handle_style: {config.handle_style}")
    if config.gasket_style not in {"thin_black_strip", "compressed_ring", "glass_runner"}:
        raise ValueError(f"Unsupported gasket_style: {config.gasket_style}")
    if config.accessory_set not in {"none", "control_vent", "stay_and_drain", "display_products"}:
        raise ValueError(f"Unsupported accessory_set: {config.accessory_set}")
    if not 0.9 <= config.body_length <= 2.4:
        raise ValueError("body_length must be in [0.9, 2.4]")
    if not 0.34 <= config.body_width <= 0.95:
        raise ValueError("body_width must be in [0.34, 0.95]")
    if not 0.35 <= config.body_height <= 1.0:
        raise ValueError("body_height must be in [0.35, 1.0]")
    if not 0.025 <= config.wall_thickness <= 0.075:
        raise ValueError("wall_thickness must be in [0.025, 0.075]")
    if not 0 <= config.interior_bin_count <= 4:
        raise ValueError("interior_bin_count must be in [0, 4]")
    if config.foot_count not in {0, 4}:
        raise ValueError("foot_count must be 0 or 4")

    if config.lid_layout == "sliding_glass":
        config = replace(config, lid_layout="single_hinged")
    config = replace(
        config,
        body_style="residential_white"
        if config.lid_layout == "single_hinged"
        and config.body_style in {"commercial_display", "split_lid_cooler"}
        else config.body_style,
        lid_material_style="solid_insulated",
        hinge_count=2 if config.hinge_count not in {2, 3} else config.hinge_count,
        hinge_style="barrel_pair"
        if config.lid_layout == "single_hinged"
        and config.hinge_style in {"center_spine", "guide_rail", "piano"}
        else config.hinge_style,
        gasket_style="thin_black_strip"
        if config.gasket_style == "glass_runner"
        else config.gasket_style,
        accessory_set="control_vent"
        if config.accessory_set == "display_products"
        or (config.lid_layout == "split_hinged" and config.accessory_set == "stay_and_drain")
        else config.accessory_set,
        interior_bin_count=max(
            0,
            min(
                config.interior_bin_count,
                _max_interior_bin_count_for_length(config.body_length),
            ),
        ),
    )

    body_style = config.body_style
    lid_material_style = config.lid_material_style
    hinge_count = config.hinge_count
    hinge_style = config.hinge_style
    gasket_style = config.gasket_style

    if config.lid_layout == "sliding_glass":
        body_style = "commercial_display"
        lid_material_style = "framed_glass"
        hinge_count = 0
        hinge_style = "guide_rail"
        gasket_style = "glass_runner"
    else:
        lid_material_style = "solid_insulated"
        if hinge_count not in {2, 3}:
            hinge_count = 2
        if gasket_style == "glass_runner":
            gasket_style = "thin_black_strip"
        if config.lid_layout == "split_hinged":
            body_style = "split_lid_cooler"
            hinge_style = "center_spine"
        elif body_style not in SINGLE_HINGED_BODY_STYLES:
            body_style = "residential_white"

    lid_count = 2 if config.lid_layout == "split_hinged" else 1
    rim_height = max(0.026, config.wall_thickness * 0.62)
    opening_length = config.body_length - 2.0 * config.wall_thickness
    opening_width = config.body_width - 2.0 * config.wall_thickness
    lid_thickness = max(0.045, config.body_height * 0.075)
    sliding_travel = max(0.18, min(config.body_length * 0.45, config.body_length - 0.25))
    base_height = max(0.10, config.body_height * 0.136)
    liner_floor_z = base_height + 0.005
    # Place the hinge axis behind the rear wall. The lid-side hinge leaf spans
    # the offset, so the rectangular insulated shell clears the barrel through
    # its full opening sweep while still closing exactly over the rear edge.
    hinge_y = -(config.body_width / 2.0) - HINGE_EDGE_CLEARANCE

    return ResolvedChestFreezerWithHingedLidConfig(
        body_style=body_style,
        lid_layout=config.lid_layout,
        lid_material_style=lid_material_style,
        body_length=config.body_length,
        body_width=config.body_width,
        body_height=config.body_height,
        wall_thickness=config.wall_thickness,
        hinge_count=hinge_count,
        hinge_style=hinge_style,
        handle_style=config.handle_style,
        gasket_style=gasket_style,
        accessory_set=config.accessory_set,
        interior_bin_count=config.interior_bin_count,
        foot_count=config.foot_count,
        foot_height=config.foot_height,
        lid_count=lid_count,
        lid_thickness=lid_thickness,
        rim_height=rim_height,
        opening_length=opening_length,
        opening_width=opening_width,
        sliding_travel=sliding_travel,
        base_height=base_height,
        liner_floor_z=liner_floor_z,
        hinge_y=hinge_y,
        name=config.name,
    )


def _joint_meta(
    joint_type: str,
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    joint_range: object,
) -> dict[str, object]:
    return {"type": joint_type, "axis": axis, "origin": origin, "range": joint_range}


def _split_hinge_separation(resolved: ResolvedChestFreezerWithHingedLidConfig) -> float:
    return max(resolved.wall_thickness * 0.40, resolved.lid_thickness * 1.05)


def _build_body(
    body,
    resolved: ResolvedChestFreezerWithHingedLidConfig,
    *,
    assets: AssetContext,
    shell,
    liner,
    trim,
    rubber,
    dark,
    steel,
) -> None:
    L = resolved.body_length
    W = resolved.body_width
    H = resolved.body_height
    wall = resolved.wall_thickness
    base_h = resolved.base_height
    liner_floor_z = resolved.liner_floor_z
    rim_h = resolved.rim_height
    opening_l = resolved.opening_length
    opening_w = resolved.opening_width

    # --- Outer shell ---
    body.visual(
        Box((L, W, base_h)),
        origin=Origin(xyz=(0.0, 0.0, base_h / 2.0)),
        material=shell,
        name="base_pan", material_class_id=("metal.paint_coated" if resolved.body_style in {"residential_white", "commercial_display", "split_lid_cooler"} else "metal.stainless_matte"),
    )
    wall_h = H - base_h
    wall_z = base_h + wall_h / 2.0
    body.visual(
        Box((wall, W, wall_h)),
        origin=Origin(xyz=(-(L / 2.0) + wall / 2.0, 0.0, wall_z)),
        material=shell,
        name="left_outer_wall", material_class_id=("metal.paint_coated" if resolved.body_style in {"residential_white", "commercial_display", "split_lid_cooler"} else "metal.stainless_matte"),
    )
    body.visual(
        Box((wall, W, wall_h)),
        origin=Origin(xyz=((L / 2.0) - wall / 2.0, 0.0, wall_z)),
        material=shell,
        name="right_outer_wall", material_class_id=("metal.paint_coated" if resolved.body_style in {"residential_white", "commercial_display", "split_lid_cooler"} else "metal.stainless_matte"),
    )
    body.visual(
        Box((L, wall, wall_h)),
        origin=Origin(xyz=(0.0, (W / 2.0) - wall / 2.0, wall_z)),
        material=shell,
        name="front_outer_wall", material_class_id=("metal.paint_coated" if resolved.body_style in {"residential_white", "commercial_display", "split_lid_cooler"} else "metal.stainless_matte"),
    )
    body.visual(
        Box((L, wall, wall_h)),
        origin=Origin(xyz=(0.0, -(W / 2.0) + wall / 2.0, wall_z)),
        material=shell,
        name="rear_outer_wall", material_class_id=("metal.paint_coated" if resolved.body_style in {"residential_white", "commercial_display", "split_lid_cooler"} else "metal.stainless_matte"),
    )

    # --- Inner liner ---
    liner_h = H - liner_floor_z - 0.015
    inner_wall_z = liner_floor_z + liner_h / 2.0
    liner_t = max(0.012, wall * 0.22)
    body.visual(
        Box((opening_l + 2.0 * liner_t, opening_w + 2.0 * liner_t, 0.030)),
        origin=Origin(xyz=(0.0, 0.0, liner_floor_z - 0.015)),
        material=liner,
        name="liner_floor", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((liner_t, opening_w, liner_h)),
        origin=Origin(xyz=(-(opening_l / 2.0) - liner_t / 2.0, 0.0, inner_wall_z)),
        material=liner,
        name="left_liner", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((liner_t, opening_w, liner_h)),
        origin=Origin(xyz=((opening_l / 2.0) + liner_t / 2.0, 0.0, inner_wall_z)),
        material=liner,
        name="right_liner", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((opening_l + 2.0 * liner_t, liner_t, liner_h)),
        origin=Origin(xyz=(0.0, (opening_w / 2.0) + liner_t / 2.0, inner_wall_z)),
        material=liner,
        name="front_liner", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((opening_l + 2.0 * liner_t, liner_t, liner_h)),
        origin=Origin(xyz=(0.0, -(opening_w / 2.0) - liner_t / 2.0, inner_wall_z)),
        material=liner,
        name="rear_liner", material_class_id="plastic.opaque_glossy_molded",
    )

    # Compressor hump in interior (hinged layouts only)
    if resolved.lid_layout != "sliding_glass":
        hump_w = max(0.14, opening_l * 0.19)
        hump_d = max(0.28, opening_w * 0.69)
        hump_h = max(0.10, H * 0.20)
        body.visual(
            Box((hump_w, hump_d, hump_h)),
            origin=Origin(xyz=(L * 0.28, 0.0, liner_floor_z + hump_h / 2.0)),
            material=liner,
            name="compressor_hump", material_class_id="plastic.opaque_glossy_molded",
        )

    # --- Top rim ---
    side_rim_w = (L - opening_l) / 2.0
    front_rim_d = (W - opening_w) / 2.0
    rim_z = H - rim_h / 2.0
    body.visual(
        Box((side_rim_w, W, rim_h)),
        origin=Origin(xyz=(-(opening_l / 2.0) - side_rim_w / 2.0, 0.0, rim_z)),
        material=trim,
        name="left_top_rim", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((side_rim_w, W, rim_h)),
        origin=Origin(xyz=((opening_l / 2.0) + side_rim_w / 2.0, 0.0, rim_z)),
        material=trim,
        name="right_top_rim", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((opening_l, front_rim_d, rim_h)),
        origin=Origin(xyz=(0.0, (opening_w / 2.0) + front_rim_d / 2.0, rim_z)),
        material=trim,
        name="front_top_rim", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((opening_l, front_rim_d, rim_h)),
        origin=Origin(xyz=(0.0, -(opening_w / 2.0) - front_rim_d / 2.0, rim_z)),
        material=trim,
        name="rear_top_rim", material_class_id="plastic.opaque_glossy_molded",
    )

    # Center spine divider for split-hinged layout
    if resolved.lid_layout == "split_hinged":
        split_hinge_sep = _split_hinge_separation(resolved)
        # Extend the structural spine to the inner faces of the two hinge
        # bosses so all fixed hinge hardware has a continuous load path.
        spine_half_width = max(0.0175, split_hinge_sep - 0.024)
        body.visual(
            Box((L - 0.04, spine_half_width * 2.0, rim_h * 1.2)),
            origin=Origin(xyz=(0.0, 0.0, H - rim_h * 0.4)),
            material=trim,
            name="center_spine", material_class_id="plastic.opaque_glossy_molded",
        )
        for sign in (-1.0, 1.0):
            body.visual(
                Cylinder(radius=0.009, length=L * 0.82),
                origin=Origin(
                    xyz=(0.0, sign * wall * 0.18, H + 0.010),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                material=dark,
                name=f"center_spine_hinge_barrel_{'front' if sign > 0 else 'rear'}", material_class_id="metal.blackened_gunmetal",
            )

    # Guide rails for sliding-glass layout
    if resolved.lid_layout == "sliding_glass":
        body.visual(
            Box((L - 0.10, 0.030, 0.026)),
            origin=Origin(xyz=(0.0, W * 0.5 - wall * 0.45, H + 0.010)),
            material=trim,
            name="front_guide_rail", material_class_id="metal.aluminum_bare",
        )
        body.visual(
            Box((L - 0.10, 0.030, 0.026)),
            origin=Origin(xyz=(0.0, -W * 0.5 + wall * 0.45, H + 0.010)),
            material=trim,
            name="rear_guide_rail", material_class_id="metal.aluminum_bare",
        )
        body.visual(
            Box((L * 0.44, W - 2.2 * wall, 0.012)),
            origin=Origin(xyz=(L * 0.28, 0.0, H + 0.030)),
            material=liner,
            name="fixed_glass", material_class_id="glass.clear_transparent",
        )
        body.visual(
            Box((L * 0.44, 0.038, 0.026)),
            origin=Origin(xyz=(L * 0.28, W * 0.5 - wall * 0.92, H + 0.032)),
            material=trim,
            name="fixed_front_frame", material_class_id="metal.aluminum_bare",
        )
        body.visual(
            Box((L * 0.44, 0.038, 0.026)),
            origin=Origin(xyz=(L * 0.28, -W * 0.5 + wall * 0.92, H + 0.032)),
            material=trim,
            name="fixed_rear_frame", material_class_id="metal.aluminum_bare",
        )
        body.visual(
            Box((0.022, W - 2.0 * wall, 0.026)),
            origin=Origin(xyz=(L * 0.08, 0.0, H + 0.010)),
            material=trim,
            name="fixed_center_frame", material_class_id="metal.aluminum_bare",
        )
        # Sliding stop bracket at the default sliding-lid travel start position;
        # this also serves as the body geometry anchor for the joint origin check.
        # Y width narrowed to leave clearance for the sliding lid front/rear frames.
        body.visual(
            Box((0.020, W - 2.0 * wall - 0.08, 0.022)),
            origin=Origin(xyz=(-L * 0.25, 0.0, H - 0.002)),
            material=trim,
            name="sliding_stop_bracket", material_class_id="metal.aluminum_bare",
        )
    elif resolved.hinge_style in {"barrel_pair", "piano"}:
        hinge_y = resolved.hinge_y
        if resolved.hinge_style == "piano":
            body.visual(
                Cylinder(radius=0.010, length=L * 0.82),
                origin=Origin(xyz=(0.0, hinge_y, H + 0.010), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=dark,
                name="rear_piano_hinge_barrel", material_class_id="metal.blackened_gunmetal",
            )
        else:
            count = max(2, resolved.hinge_count)
            usable = L * 0.68
            for idx in range(count):
                x = -usable * 0.5 + usable * idx / max(1, count - 1)
                body.visual(
                    Cylinder(radius=HINGE_BARREL_RADIUS, length=min(0.11, L * 0.12)),
                    origin=Origin(
                        xyz=(x, hinge_y, H), rpy=(0.0, math.pi / 2.0, 0.0)
                    ),
                    material=dark,
                    name=f"rear_hinge_barrel_{idx}", material_class_id="metal.blackened_gunmetal",
                )
                leaf_inner_y = hinge_y + HINGE_BARREL_RADIUS - 0.002
                leaf_outer_y = hinge_y + HINGE_EDGE_CLEARANCE + 0.002
                body.visual(
                    Box((0.060, leaf_outer_y - leaf_inner_y, 0.008)),
                    origin=Origin(xyz=(x, (leaf_inner_y + leaf_outer_y) * 0.5, H - 0.004)),
                    material=trim,
                    name=f"rear_hinge_leaf_{idx}", material_class_id="metal.stainless_matte",
                )

    # --- Control panel and vent (accessory_set) ---
    if resolved.accessory_set in {"control_vent", "display_products"}:
        body.visual(
            Box((0.18, 0.045, 0.12)),
            origin=Origin(xyz=(L * 0.30, W / 2.0 + 0.0225, H * 0.30)),
            material=dark,
            name="control_housing", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Box((0.11, 0.006, 0.05)),
            origin=Origin(xyz=(L * 0.30, W / 2.0 + 0.048, H * 0.30 + 0.025)),
            material=trim,
            name="control_face", material_class_id="tech.control_interface",
        )
        body.visual(
            Cylinder(
                radius=0.026,
                length=0.024,
            ),
            origin=Origin(
                xyz=(L * 0.255, W / 2.0 + 0.057, H * 0.30),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=dark,
            name="thermostat_knob", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Box((0.008, 0.010, 0.028)),
            origin=Origin(xyz=(L * 0.255, W / 2.0 + 0.073, H * 0.30 + 0.018)),
            material=steel,
            name="knob_indicator", material_class_id="metal.stainless_matte",
        )
        body.visual(
            Box((0.014, W * 0.38, H * 0.18)),
            origin=Origin(xyz=(L / 2.0 + 0.007, -W * 0.12, H * 0.28)),
            material=dark,
            name="condenser_vent_panel", material_class_id="metal.paint_coated",
        )
        slat_count = 6
        for i in range(slat_count):
            z = H * 0.165 + (H * 0.18 / slat_count) * i
            body.visual(
                Box((0.018, W * 0.24, 0.010)),
                origin=Origin(xyz=(L / 2.0 + 0.009, -W * 0.12, z)),
                material=trim,
                name=f"vent_slat_{i}", material_class_id="metal.paint_coated",
            )

    if resolved.interior_bin_count > 0:
        count = resolved.interior_bin_count
        margin_x = max(0.05, wall * 1.6)
        usable_l = max(0.25, opening_l - 2.0 * margin_x)
        gap_x = max(0.015, min(0.045, usable_l * 0.06))
        bin_l = (usable_l - gap_x * (count - 1)) / count
        if count > 1 and bin_l < 0.11:
            gap_x = max(0.010, (usable_l - count * 0.11) / (count - 1))
            bin_l = (usable_l - gap_x * (count - 1)) / count
        bin_l = min(0.30, max(0.09, bin_l))
        if count * bin_l + (count - 1) * gap_x > usable_l:
            bin_l = (usable_l - (count - 1) * gap_x) / count
        bin_d = min(0.12, max(0.085, opening_w * 0.16))
        bin_h = min(0.11, max(0.075, H * 0.11))
        wire_t = 0.007
        bin_y = opening_w * 0.5 - wall * 1.1 - bin_d * 0.5 - 0.006
        bin_floor_z = liner_floor_z + 0.060
        bin_mid_z = bin_floor_z + bin_h * 0.5
        supported_side_h = bin_h + (bin_floor_z - liner_floor_z)
        supported_side_mid_z = liner_floor_z + supported_side_h * 0.5
        start_x = -(opening_l * 0.5) + margin_x + bin_l * 0.5
        for idx in range(count):
            x = start_x + idx * (bin_l + gap_x)
            body.visual(
                Box((bin_l, bin_d, wire_t)),
                origin=Origin(xyz=(x, bin_y, bin_floor_z + wire_t * 0.5)),
                material=steel,
                name=f"interior_bin_{idx}_floor", material_class_id="metal.stainless_matte",
            )
            body.visual(
                Box((wire_t, bin_d, supported_side_h)),
                origin=Origin(
                    xyz=(
                        x - (bin_l * 0.5) + wire_t * 0.5,
                        bin_y,
                        supported_side_mid_z,
                    )
                ),
                material=steel,
                name=f"interior_bin_{idx}_left", material_class_id="metal.stainless_matte",
            )
            body.visual(
                Box((wire_t, bin_d, supported_side_h)),
                origin=Origin(
                    xyz=(
                        x + (bin_l * 0.5) - wire_t * 0.5,
                        bin_y,
                        supported_side_mid_z,
                    )
                ),
                material=steel,
                name=f"interior_bin_{idx}_right", material_class_id="metal.stainless_matte",
            )
            body.visual(
                Box((bin_l, wire_t, bin_h)),
                origin=Origin(xyz=(x, bin_y + (bin_d * 0.5) - wire_t * 0.5, bin_mid_z)),
                material=steel,
                name=f"interior_bin_{idx}_front", material_class_id="metal.stainless_matte",
            )
            body.visual(
                Box((bin_l, wire_t, bin_h)),
                origin=Origin(xyz=(x, bin_y - (bin_d * 0.5) + wire_t * 0.5, bin_mid_z)),
                material=steel,
                name=f"interior_bin_{idx}_rear", material_class_id="metal.stainless_matte",
            )

    if resolved.accessory_set == "stay_and_drain":
        body.visual(
            Cylinder(radius=0.030, length=0.055),
            origin=Origin(xyz=(L / 2.0 + 0.020, 0.0, H * 0.18), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=dark,
            name="drain_spigot_body", material_class_id="plastic.opaque_glossy_molded",
        )
        # stay_bracket_base moved to right-side body top to avoid flat_stay_bar sweep path
        # which runs near X=-0.32; placing at L/2-0.060 keeps it on the right end face.
        body.visual(
            Box((0.030, 0.055, 0.075)),
            origin=Origin(xyz=(L / 2.0 - 0.060, W / 2.0 + 0.015, H - 0.08)),
            material=trim,
            name="stay_bracket_base", material_class_id="metal.paint_coated",
        )
        # Rear service panel
        body.visual(
            Box((L * 0.48, 0.008, H * 0.27)),
            origin=Origin(xyz=(0.0, -(W / 2.0) - 0.004, H * 0.27)),
            material=trim,
            name="rear_service_panel", material_class_id="metal.paint_coated",
        )

    # --- Feet ---
    if resolved.foot_count:
        for idx, sx in enumerate((-1.0, 1.0)):
            for idy, sy in enumerate((-1.0, 1.0)):
                body.visual(
                    Cylinder(radius=0.030, length=resolved.foot_height),
                    origin=Origin(
                        xyz=(sx * (L * 0.42), sy * (W * 0.35), resolved.foot_height / 2.0)
                    ),
                    material=rubber,
                    name=f"foot_{idx}_{idy}", material_class_id="rubber.smooth_plain",
                )

    body.inertial = Inertial.from_geometry(
        Box((L, W, H)),
        mass=58.0,
        origin=Origin(xyz=(0.0, 0.0, H / 2.0)),
    )


def _add_lid_visuals(
    lid,
    resolved: ResolvedChestFreezerWithHingedLidConfig,
    *,
    assets: AssetContext,
    shell,
    trim,
    rubber,
    glass,
    steel,
    name: str,
    width_y: float,
    y_sign: float = 1.0,
    glass_half_x: float | None = None,
) -> None:
    L = resolved.body_length
    lid_t = resolved.lid_thickness
    W = resolved.body_width
    edge_offset = HINGE_EDGE_CLEARANCE if resolved.lid_layout == "single_hinged" else 0.0
    lid_z_offset = -lid_t if resolved.lid_layout == "split_hinged" else 0.0
    lid_center_y = y_sign * (width_y * 0.5 + edge_offset)

    if resolved.lid_material_style == "framed_glass":
        # glass_half_x constrains the X extent of glass and frame visuals so the sliding
        # lid (joint at X=-L*0.25) doesn't clip through the body outer walls.
        gx = glass_half_x if glass_half_x is not None else L * 0.23
        rail_y = W * 0.5 - resolved.wall_thickness * 0.45
        lid.visual(
            Box((gx * 2.0, width_y, 0.012)),
            origin=Origin(xyz=(0.0, 0.0, 0.006 + lid_z_offset)),
            material=glass,
            name="glass_pane", material_class_id="glass.clear_transparent",
        )
        lid.visual(
            Box((gx * 2.0 + 0.020, 0.030, 0.030)),
            origin=Origin(xyz=(0.0, width_y * 0.5, lid_z_offset)),
            material=trim,
            name="front_frame", material_class_id="metal.aluminum_bare",
        )
        lid.visual(
            Box((gx * 2.0 + 0.020, 0.030, 0.030)),
            origin=Origin(xyz=(0.0, -width_y * 0.5, lid_z_offset)),
            material=trim,
            name="rear_frame", material_class_id="metal.aluminum_bare",
        )
        # Side frames omitted: the sliding lid is offset in X so fixed-size side frames
        # would clip through the body's outer walls in many configurations.
        lid.visual(
            Box((0.20, 0.035, 0.035)),
            origin=Origin(xyz=(-L * 0.12, width_y * 0.45, 0.030 + lid_z_offset)),
            material=rubber,
            name="pull_handle", material_class_id="rubber.smooth_plain",
        )
        for y, runner_name in ((rail_y, "front_runner"), (-rail_y, "rear_runner")):
            lid.visual(
                Box((gx * 2.0, 0.020, 0.002)),
                origin=Origin(xyz=(0.0, y, -0.033 + lid_z_offset)),
                material=rubber,
                name=runner_name, material_class_id="rubber.smooth_plain",
            )
    else:
        gasket_y = 0.018
        if resolved.lid_layout == "single_hinged":
            front_gasket_y = W - 1.45 * resolved.wall_thickness - gasket_y * 0.5
        else:
            front_gasket_y = W * 0.5 - 1.4 * resolved.wall_thickness - gasket_y * 0.5

        # Main lid shell (slight overhang on all sides like five-star sample)
        lid.visual(
            Box((L + 0.020, width_y, lid_t)),
            origin=Origin(xyz=(0.0, lid_center_y, lid_t * 0.5 + lid_z_offset)),
            material=shell,
            name="lid_shell", material_class_id=("metal.paint_coated" if resolved.body_style in {"residential_white", "commercial_display", "split_lid_cooler"} else "metal.stainless_matte"),
        )
        # Raised insert panel on top and recessed inner panel; omitted for split_hinged
        # because at maximum open angle (1.75 rad) the panels from each lid swing past
        # center and collide with panels on the opposite lid.
        if resolved.lid_layout != "split_hinged":
            lid.visual(
                Box((L * 0.80, width_y * 0.67, 0.008)),
                origin=Origin(xyz=(0.0, lid_center_y, lid_t + 0.004 + lid_z_offset)),
                material=trim,
                name="top_reinforcement_panel", material_class_id="plastic.opaque_glossy_molded",
            )
            lid.visual(
                Box((L * 0.92, width_y * 0.83, 0.026)),
                origin=Origin(
                    xyz=(0.0, lid_center_y, lid_t * 0.5 + 0.005 + lid_z_offset)
                ),
                material=glass,
                name="inner_lid_panel", material_class_id="plastic.opaque_glossy_molded",
            )
        # Gasket strips (four sides)
        lid.visual(
            Box((L * 0.87, gasket_y, 0.014)),
            origin=Origin(
                xyz=(
                    0.0,
                    y_sign * (front_gasket_y + edge_offset),
                    0.006 + lid_z_offset,
                )
            ),
            material=rubber,
            name="front_gasket", material_class_id="rubber.smooth_plain",
        )
        # For split_hinged the center spine seals the inner edge; only add rear_gasket
        # for single_hinged to avoid the gasket intersecting the other lid's sweep path.
        if resolved.lid_layout != "split_hinged":
            lid.visual(
                Box((L * 0.87, gasket_y, 0.014)),
                origin=Origin(
                    xyz=(
                        0.0,
                        y_sign * (edge_offset + gasket_y * 0.5),
                        0.006 + lid_z_offset,
                    )
                ),
                material=rubber,
                name="rear_gasket", material_class_id="rubber.smooth_plain",
            )
        for side, x in (("left", -L * 0.44), ("right", L * 0.44)):
            lid.visual(
                Box((gasket_y, max(0.03, width_y - 0.08), 0.014)),
                origin=Origin(xyz=(x, lid_center_y, 0.006 + lid_z_offset)),
                material=rubber,
                name=f"{side}_gasket", material_class_id="rubber.smooth_plain",
            )

        # Hinge leaves on lid (only for single_hinged; split_hinged uses the body
        # center_spine_hinge_barrel, and placing leaves here would sweep into the
        # other lid's motion path when open at maximum angle).
        if resolved.lid_layout != "split_hinged":
            leaf_inner_y = HINGE_BARREL_RADIUS - 0.003
            leaf_outer_y = HINGE_EDGE_CLEARANCE + 0.002
            # Align the moving leaves with the outer fixed barrel positions.
            for side, x in (("left", -L * 0.34), ("right", L * 0.34)):
                lid.visual(
                    Box((0.100, leaf_outer_y - leaf_inner_y, 0.008)),
                    origin=Origin(
                        xyz=(
                            x,
                            y_sign * (leaf_inner_y + leaf_outer_y) * 0.5,
                            0.004 + lid_z_offset,
                        )
                    ),
                    material=trim,
                    name=f"{side}_hinge_leaf", material_class_id="metal.stainless_matte",
                )
        if resolved.lid_layout == "split_hinged":
            leaf_inner_y = HINGE_BARREL_RADIUS - 0.003
            leaf_outer_y = HINGE_EDGE_CLEARANCE + 0.002
            lid.visual(
                Box((L * 0.72, leaf_outer_y - leaf_inner_y, 0.004)),
                origin=Origin(
                    xyz=(
                        0.0,
                        y_sign * (leaf_inner_y + leaf_outer_y) * 0.5,
                        0.002 + lid_z_offset,
                    )
                ),
                material=trim,
                name="hinge_barrel", material_class_id="metal.blackened_gunmetal",
            )

        # Handle
        if resolved.handle_style == "front_bar":
            # Spline-based tube handle (matching five-star sample quality)
            handle_x_left = -L * 0.145
            handle_x_right = L * 0.145
            handle_y = y_sign * (width_y + edge_offset + 0.012)
            handle_z_mount = lid_t * 0.52 + lid_z_offset
            lid.visual(
                Box((0.050, 0.024, 0.030)),
                origin=Origin(xyz=(handle_x_left, handle_y, handle_z_mount)),
                material=trim,
                name="handle_mount_left", material_class_id="plastic.opaque_glossy_molded",
            )
            lid.visual(
                Box((0.050, 0.024, 0.030)),
                origin=Origin(xyz=(handle_x_right, handle_y, handle_z_mount)),
                material=trim,
                name="handle_mount_right", material_class_id="plastic.opaque_glossy_molded",
            )
            handle_mesh = mesh_from_geometry(
                tube_from_spline_points(
                    [
                        (
                            handle_x_left,
                            y_sign * (width_y + edge_offset + 0.011),
                            lid_t * 0.52 + lid_z_offset,
                        ),
                        (
                            handle_x_left * 0.6,
                            y_sign * (width_y + edge_offset + 0.025),
                            lid_t * 0.65 + lid_z_offset,
                        ),
                        (
                            handle_x_right * 0.6,
                            y_sign * (width_y + edge_offset + 0.025),
                            lid_t * 0.65 + lid_z_offset,
                        ),
                        (
                            handle_x_right,
                            y_sign * (width_y + edge_offset + 0.011),
                            lid_t * 0.52 + lid_z_offset,
                        ),
                    ],
                    radius=0.011,
                    samples_per_segment=18,
                    radial_segments=18,
                    cap_ends=True,
                ),
                assets.mesh_path(f"freezer_{name}_handle.obj"),
            )
            lid.visual(handle_mesh, material=steel, name="handle_bar", material_class_id="metal.stainless_matte")
        elif resolved.handle_style == "recessed":
            lid.visual(
                Box((0.28, 0.020, 0.012)),
                origin=Origin(
                    xyz=(
                        0.0,
                        y_sign * (width_y + edge_offset + 0.010),
                        lid_t * 0.4 + lid_z_offset,
                    )
                ),
                material=rubber,
                name="recessed_grip", material_class_id="rubber.smooth_plain",
            )
        elif resolved.handle_style == "molded_end_grip":
            for side, x in (
                ("left", -(L * 0.5 + 0.010)),
                ("right", L * 0.5 + 0.010),
            ):
                lid.visual(
                    Box((0.018, width_y * 0.42, 0.044)),
                    origin=Origin(xyz=(x, lid_center_y, lid_t * 0.48 + lid_z_offset)),
                    material=trim,
                    name=f"{side}_molded_end_grip", material_class_id="plastic.opaque_glossy_molded",
                )
        elif resolved.handle_style == "carry_handle":
            lid.visual(
                Box((0.46, 0.024, 0.004)),
                origin=Origin(xyz=(0.0, lid_center_y, lid_t + 0.002 + lid_z_offset)),
                material=trim,
                name="folding_carry_handle", material_class_id="plastic.opaque_glossy_molded",
            )

    lid.inertial = Inertial.from_geometry(
        Box((L, width_y, lid_t)),
        mass=12.0,
        origin=Origin(xyz=(0.0, lid_center_y, lid_t * 0.5 + lid_z_offset)),
    )
    _ = name


def build_chest_freezer(
    config: ChestFreezerWithHingedLidConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or ChestFreezerWithHingedLidConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-chest-freezer-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)
    palette = BODY_PALETTES[resolved.body_style]
    shell = model.material("freezer_shell", rgba=palette["shell"])
    lid_shell = model.material("freezer_lid", rgba=palette["lid"])
    liner = model.material("freezer_liner_or_glass", rgba=palette["liner"])
    trim = model.material("freezer_trim", rgba=palette["trim"])
    rubber = model.material("freezer_gasket", rgba=palette["rubber"])
    dark = model.material("freezer_dark_accessory", rgba=palette["dark"])
    steel = model.material("freezer_steel", rgba=palette["steel"])

    L = resolved.body_length
    W = resolved.body_width
    H = resolved.body_height

    body = model.part("body")
    _build_body(
        body,
        resolved,
        assets=assets,
        shell=shell,
        liner=liner,
        trim=trim,
        rubber=rubber,
        dark=dark,
        steel=steel,
    )

    if resolved.lid_layout == "single_hinged":
        lid = model.part("lid")
        _add_lid_visuals(
            lid,
            resolved,
            assets=assets,
            shell=lid_shell,
            trim=trim,
            rubber=rubber,
            glass=liner,
            steel=steel,
            name="lid",
            width_y=W,
            y_sign=1.0,
        )
        origin = (0.0, resolved.hinge_y, H)
        model.articulation(
            "lid_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=lid,
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=45.0, velocity=1.5, lower=0.0, upper=1.35),
            meta=_joint_meta("revolute", (1.0, 0.0, 0.0), origin, (0.0, 1.35)),
        )
    elif resolved.lid_layout == "split_hinged":
        # Hinge separation must exceed lid_thickness so neither lid sweeps into
        # the other lid's territory when fully open (max angle 1.75 rad ≈ 100°).
        # Minimum: hinge_sep > lid_thickness * sin(1.75) ≈ lid_thickness * 0.984.
        split_hinge_sep = _split_hinge_separation(resolved)
        # Fixed support plates meet the top-inner-edge pivot from the center spine's
        # outer faces. At maximum opening the lid thickness sweeps outward above
        # these plates instead of through the fixed hinge hardware.
        boss_depth = 0.024
        boss_height = resolved.lid_thickness + 0.010
        for sign in (1.0, -1.0):
            body.visual(
                Box((L * 0.82, boss_depth, boss_height)),
                origin=Origin(
                    xyz=(
                        0.0,
                        sign * (split_hinge_sep - boss_depth * 0.5),
                        H + resolved.lid_thickness - boss_height * 0.5,
                    )
                ),
                material=dark,
                name=f"split_hinge_boss_{'front' if sign > 0 else 'rear'}", material_class_id="metal.blackened_gunmetal",
            )
        for i, sign in enumerate((1.0, -1.0)):
            lid = model.part(f"lid_{i}")
            _add_lid_visuals(
                lid,
                resolved,
                assets=assets,
                shell=lid_shell,
                trim=trim,
                rubber=rubber,
                glass=liner,
                steel=steel,
                name=f"lid_{i}",
                width_y=W * 0.47,
                y_sign=sign,
            )
            origin = (0.0, sign * split_hinge_sep, H + resolved.lid_thickness)
            axis = (sign, 0.0, 0.0)
            model.articulation(
                f"lid_{i}_hinge",
                ArticulationType.REVOLUTE,
                parent=body,
                child=lid,
                origin=Origin(xyz=origin),
                axis=axis,
                motion_limits=MotionLimits(
                    effort=18.0, velocity=2.0, lower=0.0, upper=math.pi / 2.0
                ),
                meta=_joint_meta("revolute", axis, origin, (0.0, math.pi / 2.0)),
            )
    else:
        # Clamp width_y so the sliding lid's front/rear frames stay inside the guide rails.
        # Guide rail inner edge: W*0.5 - wall*0.45 - 0.015 (half-width of guide rail).
        # Clamp width_y so the sliding lid's front/rear frames stay inside the guide rails.
        # Frame outer Y = width_y/2 + 0.015; body outer wall inner face = W/2 - wall.
        # Need clearance ≥ 0.005: width_y/2 + 0.015 ≤ W/2 - wall - 0.005
        # => width_y ≤ W - 2*wall - 0.040.
        sliding_width_y = min(W * 0.82, W - 2 * resolved.wall_thickness - 0.040)
        # Clamp X extent of glass/frame so they stay within the body opening left wall.
        # Lid joint is at X = -L*0.25 in body frame; body left inner wall is at
        # X = -(L/2 - wall) in body frame = -L*0.25+wall in lid frame.
        # Max half-x in lid frame (leftward) = L*0.25 - wall - clearance.
        wall = resolved.wall_thickness
        sliding_glass_half_x = min(L * 0.23, L * 0.25 - wall - 0.010)
        sliding_lid = model.part("sliding_lid")
        _add_lid_visuals(
            sliding_lid,
            resolved,
            assets=assets,
            shell=lid_shell,
            trim=trim,
            rubber=rubber,
            glass=liner,
            steel=steel,
            name="sliding_lid",
            width_y=sliding_width_y,
            glass_half_x=sliding_glass_half_x,
        )
        origin = (-L * 0.25, 0.0, H + 0.010)
        model.articulation(
            "sliding_lid_slide",
            ArticulationType.PRISMATIC,
            parent=body,
            child=sliding_lid,
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=70.0, velocity=0.45, lower=0.0, upper=resolved.sliding_travel
            ),
            meta=_joint_meta("prismatic", (1.0, 0.0, 0.0), origin, (0.0, resolved.sliding_travel)),
        )

    if resolved.accessory_set == "stay_and_drain" and resolved.lid_layout != "sliding_glass":
        stay = model.part("stay_rod")
        # Joint placed at X = -L*0.30 on the lid front face (Y = W+0.010, dist_parent =
        # 0.010 < tol=0.012).  X = -L*0.30 is outside the front_bar handle arc (which
        # spans X = ±L*0.145), so upper_pin_eye at (0,0,0) in stay_rod frame does not
        # overlap the handle tube mesh regardless of handle_style.
        stay.visual(
            Box((0.040, 0.018, 0.040)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=trim,
            name="upper_pin_eye", material_class_id="metal.paint_coated",
        )
        lid_t = resolved.lid_thickness
        # Y = W + 0.009 in lid frame: just outside the lid front face (dist_parent = 0.009 <
        # tol=0.012); pin_eye inner Y face = W+0.009-0.009 = W, touching the lid face so
        # fail_if_isolated_parts sees gap = 0.  X = -L*0.30 is to the left of the handle arc
        # (|handle_x| = L*0.145) so no handle-bar overlap occurs.
        stay_origin = (
            -L * 0.30,
            W + HINGE_EDGE_CLEARANCE + 0.009,
            lid_t * 0.5,
        )
        model.articulation(
            "stay_rod_joint",
            ArticulationType.REVOLUTE,
            parent="lid" if resolved.lid_layout == "single_hinged" else "lid_0",
            child=stay,
            origin=Origin(xyz=stay_origin),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=-0.35, upper=1.15),
            meta=_joint_meta("revolute", (0.0, 1.0, 0.0), stay_origin, (-0.35, 1.15)),
        )
        lever = model.part("spigot_lever")
        # A compact spindle hub keeps the turn lever retained on the fixed
        # drain-spigot body throughout its full swing about the Y axis.
        lever.visual(
            Cylinder(radius=0.010, length=0.050),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=dark,
            name="spindle_hub",
            material_class_id="plastic.opaque_glossy_molded",
        )
        lever.visual(
            Box((0.070, 0.040, 0.018)),
            origin=Origin(xyz=(0.040, 0.0, 0.0)),
            material=dark,
            name="turn_lever", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            "spigot_lever_joint",
            ArticulationType.REVOLUTE,
            parent=body,
            child=lever,
            origin=Origin(xyz=(L * 0.5 + 0.056, 0.0, H * 0.18)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.5, velocity=2.5, lower=-0.85, upper=0.85),
            meta=_joint_meta(
                "revolute", (0.0, 1.0, 0.0), (L * 0.5 + 0.056, 0.0, H * 0.18), (-0.85, 0.85)
            ),
        )
    return model


def build_seeded_chest_freezer(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_chest_freezer(config_from_seed(seed), assets=assets)


def with_overrides(
    config: ChestFreezerWithHingedLidConfig, **kwargs: object
) -> ChestFreezerWithHingedLidConfig:
    return replace(config, **kwargs)


def run_chest_freezer_tests(
    object_model: ArticulatedObject, config: ChestFreezerWithHingedLidConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")
    body_visuals = {v.name for v in body.visuals}
    ctx.check(
        "identity_hollow_liner_and_rim",
        {"liner_floor", "front_top_rim", "rear_top_rim"}.issubset(body_visuals),
        details=str(body_visuals),
    )
    ctx.check_model_valid()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.012)
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=160,
        overlap_tol=0.005,
        overlap_volume_tol=0.0,
        ignore_adjacent=True,
        ignore_fixed=True,
    )

    for joint in object_model.articulations:
        if joint.articulation_type != ArticulationType.FIXED:
            ctx.check(
                f"{joint.name}_has_joint_metadata",
                {"type", "axis", "origin", "range"}.issubset(joint.meta),
                details=str(joint.meta),
            )

    if resolved.lid_layout == "single_hinged":
        joint = object_model.get_articulation("lid_hinge")
        ctx.check(
            "single_lid_revolute",
            joint.articulation_type == ArticulationType.REVOLUTE,
            details=str(joint.articulation_type),
        )
        ctx.check(
            "single_hinge_on_rear_edge",
            joint.origin.xyz[1] < -resolved.body_width * 0.35,
            details=str(joint.origin.xyz),
        )
        ctx.expect_aabb_contact("lid", "body")
        ctx.expect_aabb_overlap("lid", "body", axes="x", min_overlap=resolved.body_length * 0.92)
        ctx.expect_aabb_overlap("lid", "body", axes="y", min_overlap=resolved.body_width * 0.95)
        ctx.expect_aabb_gap("lid", "body", axis="z", max_gap=0.004, max_penetration=0.024)
        ctx.expect_origin_distance("lid", "body", axes="x", max_dist=0.025)
        ctx.expect_joint_motion_axis(
            "lid_hinge", "lid", world_axis="z", direction="positive", min_delta=0.08
        )
        with ctx.pose(lid_hinge=0.70):
            ctx.expect_aabb_overlap(
                "lid", "body", axes="x", min_overlap=resolved.body_length * 0.90
            )
        with ctx.pose(lid_hinge=1.35):
            ctx.expect_aabb_overlap(
                "lid", "body", axes="x", min_overlap=resolved.body_length * 0.90
            )

    elif resolved.lid_layout == "split_hinged":
        joints = [
            object_model.get_articulation("lid_0_hinge"),
            object_model.get_articulation("lid_1_hinge"),
        ]
        ctx.check(
            "split_lid_count",
            all(j.articulation_type == ArticulationType.REVOLUTE for j in joints),
            details=str(joints),
        )
        ctx.check(
            "split_hinge_axes_mirrored",
            tuple(joints[0].axis) == (1.0, 0.0, 0.0) and tuple(joints[1].axis) == (-1.0, 0.0, 0.0),
            details=str([j.axis for j in joints]),
        )
    else:
        joint = object_model.get_articulation("sliding_lid_slide")
        ctx.check(
            "sliding_lid_prismatic",
            joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(joint.axis) == (1.0, 0.0, 0.0),
            details=str((joint.articulation_type, joint.axis)),
        )
        ctx.check(
            "guide_rails_present",
            {"front_guide_rail", "rear_guide_rail"}.issubset(body_visuals),
            details=str(body_visuals),
        )
    return ctx.report()
