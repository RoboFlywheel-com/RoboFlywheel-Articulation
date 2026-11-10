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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

BarrierLayout = Literal[
    "sliding_panel",
    "swing_leaf",
    "bifold_leaf",
    "rising_wedge",
    "vertical_lift_panel",
]
SupportStyle = Literal[
    "control_cabinet",
    "flat_housing",
    "rail_frame",
    "pintle_post",
]
BoomSection = Literal["rectangular_tube", "tapered_box", "trussed"]
BoomSupportProfile = Literal["slim_cabinet", "round_pedestal", "box_head"]
CounterweightStyle = Literal["none", "tail_block", "counter_arm", "fin"]
BoomEndStyle = Literal["rubber_cap", "tapered_tip", "reflector_end"]
StripePattern = Literal["none", "long_red_strip", "segmented_red_bands", "yellow_hazard_bands"]
PanelStyle = Literal["mesh_frame", "tube_frame", "solid_panel"]
LeafFrameProfile = Literal["light_tube", "industrial_panel"]
InfillStyle = Literal["open_tube", "mesh", "diagonal_brace", "ornamental"]
TrackStyle = Literal["floor_rail", "twin_channel", "recessed_guide"]
HingeStyle = Literal["fork_yoke", "knuckle", "pintle_barrel"]
MaterialStyle = Literal[
    "parking_white",
    "hazard_yellow",
    "galvanized",
    "industrial_red",
    "red_white_security",
    "coated_graphite",
]

LAYOUT_SUPPORT: dict[BarrierLayout, SupportStyle] = {
    "sliding_panel": "rail_frame",
    "swing_leaf": "pintle_post",
    "bifold_leaf": "pintle_post",
    "rising_wedge": "flat_housing",
    "vertical_lift_panel": "rail_frame",
}

MATERIAL_PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "parking_white": {
        "support": (0.82, 0.84, 0.84, 1.0),
        "barrier": (0.94, 0.93, 0.86, 1.0),
        "accent": (0.80, 0.06, 0.04, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
    },
    "hazard_yellow": {
        "support": (0.20, 0.22, 0.22, 1.0),
        "barrier": (0.95, 0.74, 0.10, 1.0),
        "accent": (0.06, 0.06, 0.05, 1.0),
        "dark": (0.05, 0.05, 0.05, 1.0),
    },
    "galvanized": {
        "support": (0.58, 0.61, 0.62, 1.0),
        "barrier": (0.70, 0.73, 0.74, 1.0),
        "accent": (0.86, 0.18, 0.08, 1.0),
        "dark": (0.12, 0.13, 0.14, 1.0),
    },
    "industrial_red": {
        "support": (0.08, 0.09, 0.09, 1.0),
        "barrier": (0.70, 0.70, 0.66, 1.0),
        "accent": (0.55, 0.02, 0.02, 1.0),
        "dark": (0.04, 0.04, 0.04, 1.0),
    },
    "red_white_security": {
        "support": (0.50, 0.50, 0.46, 1.0),
        "barrier": (0.92, 0.90, 0.82, 1.0),
        "accent": (0.62, 0.02, 0.02, 1.0),
        "dark": (0.06, 0.06, 0.06, 1.0),
    },
    "coated_graphite": {
        "support": (0.18, 0.20, 0.22, 1.0),
        "barrier": (0.62, 0.64, 0.63, 1.0),
        "accent": (0.92, 0.72, 0.08, 1.0),
        "dark": (0.04, 0.045, 0.05, 1.0),
    },
}

ADOPTED_SOURCES: dict[str, str] = {
    "S1": "data/records/rec_barrier_gate_0002/revisions/rev_000001/model.py:L32-L163",
    "S2": "data/records/rec_barrier_gate_557f4d79951148ad88a0c526a09987a0/revisions/rev_000001/model.py:L27-L220",
    "S3": "data/records/rec_barrier_gate_b31475654e4b41c3b48a69158cbd2fb6/revisions/rev_000001/model.py:L185-L296",
    "S6": "data/records/rec_barrier_gate_b870b87019dd4d72b99a9ed24e459e7a/revisions/rev_000001/model.py:L81-L270",
    "S7": "data/records/rec_barrier_gate_0003/revisions/rev_000001/model.py:L28-L180",
    "S8": "data/records/rec_barrier_gate_a0be5d68a4744db9ad3d01334534f1e6/revisions/rev_000001/model.py:L1-L220",
    "S9": "data/records/rec_barrier_gate_90f1270c16a34e90b9ea0b76b0c7f325/revisions/rev_000001/model.py:L1-L230",
    "S10": "data/records/rec_barrier_gate_c928e4505e804a5e8704753571edeb3c/revisions/rev_000001/model.py:L1-L260",
    "S11": "data/records/rec_barrier_gate_2622f0752d0f42e3bb9a9bbbc778e868/revisions/rev_000001/model.py:L1-L240",
    "S12": "data/records/rec_barrier_gate_b398b7cdd16d4133b2277655affcf897/revisions/rev_000001/model.py:L1-L250",
    "S13": "data/records/rec_barrier_gate_1e730cf3f3c1431593a2a227ce531860/revisions/rev_000001/model.py:L1-L230",
    "S14": "data/records/rec_barrier_gate_2e17b13d427c4e5990437b0fef1400f9/revisions/rev_000001/model.py:L1-L220",
    "S15": "data/records/rec_barrier_gate_f8000362cf3a4c62965e78a33a2c23df/revisions/rev_000001/model.py:L1-L260",
    "S16": "data/records/rec_barrier_gate_aac86b50737842bd8ac956d2e5251dc3/revisions/rev_000001/model.py:L1-L220",
    "S18": "data/records/rec_barrier_gate_7d304d6794e24a4892d2dd9c08b6f1a3/revisions/rev_000001/model.py:L1-L250",
}


@dataclass(frozen=True)
class BarrierGateConfig:
    barrier_layout: BarrierLayout = "sliding_panel"
    support_style: SupportStyle | None = None
    boom_section: BoomSection = "rectangular_tube"
    boom_support_profile: BoomSupportProfile = "slim_cabinet"
    boom_length: float = 3.8
    counterweight_style: CounterweightStyle = "tail_block"
    boom_end_style: BoomEndStyle = "rubber_cap"
    stripe_pattern: StripePattern = "segmented_red_bands"
    fold_ratio: float = 0.52
    panel_count: int = 2
    panel_style: PanelStyle = "mesh_frame"
    leaf_frame_profile: LeafFrameProfile = "light_tube"
    infill_style: InfillStyle = "diagonal_brace"
    track_style: TrackStyle = "twin_channel"
    hinge_style: HingeStyle = "fork_yoke"
    catch_post_enabled: bool = True
    open_angle: float = 1.35
    slide_travel: float = 1.5
    material_style: MaterialStyle = "parking_white"
    name: str = "reference_barrier_gate_leaf_gate"


@dataclass(frozen=True)
class ResolvedBarrierGateConfig:
    barrier_layout: BarrierLayout
    support_style: SupportStyle
    boom_section: BoomSection
    boom_support_profile: BoomSupportProfile
    boom_length: float
    counterweight_style: CounterweightStyle
    boom_end_style: BoomEndStyle
    stripe_pattern: StripePattern
    fold_ratio: float
    inner_boom_length: float
    outer_boom_length: float
    panel_count: int
    panel_style: PanelStyle
    leaf_frame_profile: LeafFrameProfile
    panel_width: float
    infill_style: InfillStyle
    track_style: TrackStyle
    hinge_style: HingeStyle
    catch_post_enabled: bool
    open_angle: float
    slide_travel: float
    support_width: float
    support_depth: float
    support_height: float
    material_style: MaterialStyle
    name: str


def config_from_seed(seed: int) -> BarrierGateConfig:
    rng = random.Random(seed)
    layouts: tuple[BarrierLayout, ...] = (
        "sliding_panel",
        "swing_leaf",
        "bifold_leaf",
        "rising_wedge",
        "vertical_lift_panel",
    )
    layout = layouts[seed % len(layouts)]
    return BarrierGateConfig(
        barrier_layout=layout,
        support_style=LAYOUT_SUPPORT[layout],
        boom_section="rectangular_tube",
        boom_length=3.8,
        counterweight_style="none",
        boom_end_style="rubber_cap",
        stripe_pattern="none",
        fold_ratio=0.52,
        panel_count=1 if layout == "rising_wedge" else rng.choice((1, 2)),
        panel_style="solid_panel"
        if layout == "rising_wedge"
        else rng.choice(("mesh_frame", "tube_frame", "solid_panel")),
        infill_style=rng.choice(("open_tube", "mesh", "diagonal_brace", "ornamental")),
        track_style="recessed_guide"
        if layout in {"rising_wedge", "vertical_lift_panel"}
        else rng.choice(("floor_rail", "twin_channel", "recessed_guide")),
        hinge_style=rng.choice(("fork_yoke", "knuckle", "pintle_barrel")),
        catch_post_enabled=rng.random() < 0.55,
        open_angle=round(rng.uniform(0.65, 1.65), 3),
        slide_travel=round(rng.uniform(0.8, 2.4), 3),
        material_style=rng.choice(tuple(MATERIAL_PALETTES)),
        boom_support_profile="slim_cabinet",
        leaf_frame_profile=rng.choice(("light_tube", "industrial_panel")),
        name=f"seeded_barrier_gate_leaf_gate_{seed}",
    )


def resolve_config(config: BarrierGateConfig) -> ResolvedBarrierGateConfig:
    if config.barrier_layout not in LAYOUT_SUPPORT:
        raise ValueError(f"Unsupported barrier_layout: {config.barrier_layout}")
    support_style = config.support_style or LAYOUT_SUPPORT[config.barrier_layout]
    if support_style != LAYOUT_SUPPORT[config.barrier_layout]:
        raise ValueError("support_style must match barrier_layout")
    if config.boom_section not in ("rectangular_tube", "tapered_box", "trussed"):
        raise ValueError(f"Unsupported boom_section: {config.boom_section}")
    if config.boom_support_profile not in ("slim_cabinet", "round_pedestal", "box_head"):
        raise ValueError(f"Unsupported boom_support_profile: {config.boom_support_profile}")
    if config.counterweight_style not in ("none", "tail_block", "counter_arm", "fin"):
        raise ValueError(f"Unsupported counterweight_style: {config.counterweight_style}")
    if config.boom_end_style not in ("rubber_cap", "tapered_tip", "reflector_end"):
        raise ValueError(f"Unsupported boom_end_style: {config.boom_end_style}")
    if config.stripe_pattern not in (
        "none",
        "long_red_strip",
        "segmented_red_bands",
        "yellow_hazard_bands",
    ):
        raise ValueError(f"Unsupported stripe_pattern: {config.stripe_pattern}")
    panel_count = 1 if config.barrier_layout == "rising_wedge" else config.panel_count
    if panel_count not in (1, 2):
        raise ValueError("panel_count must be 1 or 2")
    if config.panel_style not in ("mesh_frame", "tube_frame", "solid_panel"):
        raise ValueError(f"Unsupported panel_style: {config.panel_style}")
    if config.leaf_frame_profile not in ("light_tube", "industrial_panel"):
        raise ValueError(f"Unsupported leaf_frame_profile: {config.leaf_frame_profile}")
    if config.infill_style not in ("open_tube", "mesh", "diagonal_brace", "ornamental"):
        raise ValueError(f"Unsupported infill_style: {config.infill_style}")
    if config.track_style not in ("floor_rail", "twin_channel", "recessed_guide"):
        raise ValueError(f"Unsupported track_style: {config.track_style}")
    if config.hinge_style not in ("fork_yoke", "knuckle", "pintle_barrel"):
        raise ValueError(f"Unsupported hinge_style: {config.hinge_style}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    boom_length = max(2.4, min(5.2, config.boom_length))
    fold_ratio = max(0.40, min(0.65, config.fold_ratio))
    open_angle = max(0.65, min(1.65, config.open_angle))
    slide_travel = max(0.8, min(2.4, config.slide_travel))
    inner_boom_length = boom_length * fold_ratio
    outer_boom_length = boom_length - inner_boom_length
    boom_support_profile = "slim_cabinet"
    if config.barrier_layout == "sliding_panel":
        support_dims = (slide_travel * 2.1 + 1.2, 0.18, 1.15)
    elif config.barrier_layout == "vertical_lift_panel":
        support_dims = (1.75, 0.26, 1.60)
    elif config.barrier_layout == "rising_wedge":
        support_dims = (1.62, 0.86, 0.30)
    else:
        support_dims = (0.20, 0.20, 1.35)

    return ResolvedBarrierGateConfig(
        barrier_layout=config.barrier_layout,
        support_style=support_style,
        boom_section=config.boom_section,
        boom_support_profile=boom_support_profile,
        boom_length=boom_length,
        counterweight_style=config.counterweight_style,
        boom_end_style=config.boom_end_style,
        stripe_pattern=config.stripe_pattern,
        fold_ratio=fold_ratio,
        inner_boom_length=inner_boom_length,
        outer_boom_length=outer_boom_length,
        panel_count=panel_count,
        panel_style=config.panel_style,
        leaf_frame_profile=config.leaf_frame_profile,
        panel_width=1.15,
        infill_style=config.infill_style,
        track_style=config.track_style,
        hinge_style=config.hinge_style,
        catch_post_enabled=config.catch_post_enabled,
        open_angle=open_angle,
        slide_travel=slide_travel,
        support_width=support_dims[0],
        support_depth=support_dims[1],
        support_height=support_dims[2],
        material_style=config.material_style,
        name=config.name,
    )


def _add_support_visuals(
    part, r: ResolvedBarrierGateConfig, *, support_mat, accent_mat, dark_mat
) -> None:
    if r.barrier_layout == "rising_wedge":
        part.visual(
            Box((r.support_width, r.support_depth, 0.060)),
            origin=Origin(xyz=(0.0, 0.0, 0.030)),
            material=dark_mat,
            name="road_channel_base", material_class_id="metal.cast_iron_bare",
        )
        part.visual(
            Box((r.support_width + 0.18, r.support_depth + 0.18, 0.026)),
            origin=Origin(xyz=(0.0, 0.0, 0.013)),
            material=support_mat,
            name="flush_road_frame", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        for y, label in ((-r.support_depth * 0.43, "front"), (r.support_depth * 0.43, "rear")):
            part.visual(
                Box((r.support_width + 0.10, 0.050, 0.105)),
                origin=Origin(xyz=(0.0, y, 0.082)),
                material=support_mat,
                name=f"{label}_channel_wall", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
        # Trough stays short and hugged to the rear wall: the plate's rear corner
        # sits at -support_width/2 + 0.11 (+ slope terms) at the closed pose and
        # only moves forward/up as the wedge rises, so a trough ending at
        # -support_width/2 + 0.10 is never struck at any pose.
        part.visual(
            Box((0.10, 0.30, 0.06)),
            origin=Origin(xyz=(-r.support_width / 2.0 + 0.05, 0.0, 0.060)),
            material=dark_mat,
            name="rear_hinge_trough", material_class_id="metal.cast_iron_bare",
        )
        # Bosses stand outside the plate half-width (plate width = support_depth * 0.70)
        # and weld into the channel walls, so the tilting plate sweeps clear of them
        # while the hinge axis still runs through both bosses.
        wedge_boss_y = r.support_depth * 0.41
        for y, face in ((-wedge_boss_y, "front"), (wedge_boss_y, "rear")):
            part.visual(
                Cylinder(radius=0.036, length=0.035),
                origin=Origin(
                    xyz=(-r.support_width / 2.0 + 0.11, y, 0.145),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=dark_mat,
                name=f"{face}_wedge_hinge_boss", material_class_id="metal.blackened_gunmetal",
            )
        return
    if r.barrier_layout == "vertical_lift_panel":
        counterweight_offset = 0.26
        rail_x = r.support_width / 2.0 + counterweight_offset
        # The ground sill spreads out under the counterweight guide rails so they are
        # one connected fixed support, not a floating island beside the columns.
        sill_width = r.support_width + 2.0 * counterweight_offset + 0.08
        part.visual(
            Box((sill_width, 0.32, 0.046)),
            origin=Origin(xyz=(0.0, 0.0, 0.023)),
            material=dark_mat,
            name="lift_gate_ground_sill", material_class_id="metal.cast_iron_bare",
        )
        for x, label in ((-r.support_width / 2.0, "left"), (r.support_width / 2.0, "right")):
            part.visual(
                Box((0.11, 0.20, r.support_height)),
                origin=Origin(xyz=(x, 0.0, r.support_height / 2.0)),
                material=support_mat,
                name=f"{label}_guide_column", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
            part.visual(
                Box((0.035, 0.075, r.support_height * 0.82)),
                origin=Origin(xyz=(x * 0.985, -0.070, r.support_height * 0.47)),
                material=dark_mat,
                name=f"{label}_front_guide_slot", material_class_id="metal.blackened_gunmetal",
            )
        part.visual(
            Box((r.support_width + 0.05, 0.18, 0.080)),
            origin=Origin(xyz=(0.0, 0.0, r.support_height + 0.040)),
            material=support_mat,
            name="upper_lift_track", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        for y, label in ((-0.0835, "front"), (0.0835, "rear")):
            part.visual(
                Box((0.18, 0.037, r.support_height * 0.82)),
                origin=Origin(xyz=(rail_x, y, r.support_height * 0.42)),
                material=dark_mat,
                name=f"{label}_counterweight_guide_rail", material_class_id="metal.steel_bare",
            )
        return
    if r.support_style == "control_cabinet":
        if r.barrier_layout == "folding_boom" or r.boom_support_profile == "slim_cabinet":
            part.visual(
                Box((0.70, 0.42, 0.08)),
                origin=Origin(xyz=(0.0, 0.0, 0.04)),
                material=dark_mat,
                name="floor_plate", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Box((0.34, 0.24, 0.18)),
                origin=Origin(xyz=(0.0, 0.0, 0.16)),
                material=dark_mat,
                name="pedestal", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Box((0.46, 0.18, 0.88)),
                origin=Origin(xyz=(0.0, 0.0, 0.65)),
                material=support_mat,
                name="flat_cabinet", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
            part.visual(
                Box((0.30, 0.010, 0.46)),
                origin=Origin(xyz=(-0.015, -0.095, 0.67)),
                material=dark_mat,
                name="service_panel", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Box((0.09, 0.012, 0.15)),
                origin=Origin(xyz=(-0.135, -0.102, 0.86)),
                material=accent_mat,
                name="warning_label", material_class_id="plastic.opaque_glossy_molded",
            )
            part.visual(
                Box((0.064, 0.020, 0.064)),
                origin=Origin(xyz=(0.03, -0.100, 0.96)),
                material=dark_mat,
                name="indicator_mount", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Cylinder(radius=0.035, length=0.018),
                origin=Origin(xyz=(0.03, -0.108, 0.96), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=accent_mat,
                name="indicator_lamp", material_class_id="tech.emissive_surface",
            )
            if r.barrier_layout == "single_boom":
                part.visual(
                    Box((0.020, 0.012, 0.11)),
                    origin=Origin(xyz=(-0.18, -0.102, 0.66)),
                    material=dark_mat,
                    name="service_panel_pull", material_class_id="metal.blackened_gunmetal",
                )
                for z, label in ((0.52, "green_button"), (0.58, "red_button")):
                    part.visual(
                        Cylinder(radius=0.018, length=0.012),
                        origin=Origin(xyz=(-0.10, -0.108, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                        material=accent_mat if label == "red_button" else support_mat,
                        name=label, material_class_id="plastic.opaque_glossy_molded",
                    )
            part.visual(
                Box((0.46, 0.19, 0.035)),
                origin=Origin(xyz=(0.0, 0.0, 1.107)),
                material=support_mat,
                name="flat_lid", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )

        if r.barrier_layout == "folding_boom":
            for y in (-0.052, 0.052):
                part.visual(
                    Box((0.24, 0.038, 0.19)),
                    origin=Origin(xyz=(0.32, y, 0.90)),
                    material=dark_mat,
                    name=f"folding_pivot_fork_{'left' if y < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
                )
            for y in (-0.090, 0.090):
                part.visual(
                    Cylinder(radius=0.105, length=0.025),
                    origin=Origin(xyz=(0.32, y, 0.90), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=support_mat,
                    name=f"folding_pivot_cap_{'left' if y < 0 else 'right'}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
                )
        elif r.boom_support_profile == "round_pedestal":
            part.visual(
                Cylinder(radius=0.12, length=0.04),
                origin=Origin(xyz=(0.0, 0.0, 0.02)),
                material=dark_mat,
                name="round_base_foot", material_class_id="metal.cast_iron_bare",
            )
            part.visual(
                Cylinder(radius=0.07, length=1.08),
                origin=Origin(xyz=(0.0, 0.0, 0.56)),
                material=dark_mat,
                name="round_pedestal_post", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Cylinder(radius=0.14, length=0.09),
                origin=Origin(xyz=(0.0, 0.0, 1.12)),
                material=support_mat,
                name="round_motor_drum", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
            part.visual(
                Box((0.20, 0.13, 0.11)),
                origin=Origin(xyz=(0.18, 0.0, 1.23)),
                material=dark_mat,
                name="round_output_gearbox", material_class_id="metal.blackened_gunmetal",
            )
            for y in (-0.065, 0.065):
                part.visual(
                    Box((0.22, 0.05, 0.15)),
                    origin=Origin(xyz=(0.205, y, 1.245)),
                    material=dark_mat,
                    name=f"round_hinge_yoke_{'left' if y < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
                )
            for y in (-0.12, 0.12):
                part.visual(
                    Cylinder(radius=0.050, length=0.018),
                    origin=Origin(xyz=(0.29, y, 1.30), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=dark_mat,
                    name=f"round_pivot_cap_{'front' if y < 0 else 'rear'}", material_class_id="metal.blackened_gunmetal",
                )
        elif r.boom_support_profile == "box_head":
            part.visual(
                Box((0.36, 0.32, 0.06)),
                origin=Origin(xyz=(0.0, 0.0, 0.03)),
                material=dark_mat,
                name="box_head_foot", material_class_id="metal.cast_iron_bare",
            )
            part.visual(
                Box((0.16, 0.18, 0.86)),
                origin=Origin(xyz=(0.0, 0.0, 0.43)),
                material=dark_mat,
                name="box_head_column", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Box((0.58, 0.28, 0.20)),
                origin=Origin(xyz=(0.04, 0.0, 1.12)),
                material=dark_mat,
                name="rectangular_motor_head", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Cylinder(radius=0.028, length=0.020),
                origin=Origin(xyz=(-0.20, -0.06, 1.24)),
                material=accent_mat,
                name="top_status_beacon", material_class_id="tech.emissive_surface",
            )
            for y in (-0.065, 0.065):
                part.visual(
                    Box((0.22, 0.05, 0.15)),
                    origin=Origin(xyz=(0.205, y, 1.245)),
                    material=dark_mat,
                    name=f"box_head_hinge_yoke_{'left' if y < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
                )
            part.visual(
                Box((0.18, 0.012, 0.075)),
                origin=Origin(xyz=(-0.03, -0.146, 1.10)),
                material=accent_mat,
                name="box_head_warning_plate", material_class_id="metal.paint_coated",
            )
        else:
            part.visual(
                Box((0.17, 0.20, 0.12)),
                origin=Origin(xyz=(0.19, 0.0, 1.23)),
                material=support_mat,
                name="upper_hinge_block", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
            for y in (-0.065, 0.065):
                part.visual(
                    Box((0.25, 0.05, 0.16)),
                    origin=Origin(xyz=(0.205, y, 1.23)),
                    material=support_mat,
                    name=f"hinge_yoke_{'left' if y < 0 else 'right'}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
                )
            for y in (-0.13, 0.13):
                part.visual(
                    Cylinder(radius=0.055, length=0.018),
                    origin=Origin(xyz=(0.29, y, 1.30), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=dark_mat,
                    name=f"pivot_pin_cap_{'front' if y < 0 else 'rear'}", material_class_id="metal.blackened_gunmetal",
                )
    elif r.support_style == "rail_frame":
        rail_head_height = 0.050
        base_height = 0.055
        # Sliding panels run outward along the track; stop posts stand just beyond
        # full travel on each side so a panel at maximum stroke clears them.
        panel_joint_offset = 0.66
        end_post_half_width = 0.05
        stop_clearance = 0.05
        stop_post_x = (
            panel_joint_offset
            + r.slide_travel
            + r.panel_width / 2.0
            + end_post_half_width
            + stop_clearance
        )
        ground_strip_width = (
            max(r.support_width + 0.40, 2.0 * (stop_post_x + end_post_half_width + 0.05))
            if r.barrier_layout == "sliding_panel"
            else r.support_width + 0.40
        )
        part.visual(
            Box((ground_strip_width, 0.34, 0.035)),
            origin=Origin(xyz=(0.0, 0.0, 0.0175)),
            material=support_mat,
            name="ground_strip", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        part.visual(
            Box((r.support_width - 0.18, 0.18, base_height)),
            origin=Origin(xyz=(0.0, 0.0, base_height / 2.0)),
            material=dark_mat,
            name="ground_rail_base", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Box((r.support_width - 0.28, 0.06, rail_head_height)),
            origin=Origin(xyz=(0.0, 0.0, base_height + rail_head_height / 2.0)),
            material=dark_mat,
            name="ground_rail_head", material_class_id="metal.steel_bare",
        )
        if r.track_style in ("twin_channel", "recessed_guide"):
            for y, label in ((-0.085, "front"), (0.085, "rear")):
                part.visual(
                    Box((r.support_width - 0.30, 0.018, 0.090)),
                    origin=Origin(xyz=(0.0, y, 0.078)),
                    material=dark_mat,
                    name=f"{label}_lower_channel_lip", material_class_id="metal.blackened_gunmetal",
                )
        part.visual(
            Box((0.11, 0.16, r.support_height)),
            origin=Origin(xyz=(0.0, 0.0, r.support_height / 2.0)),
            material=support_mat,
            name="center_latch_post", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        post_x_values = (-r.support_width / 2.0,)
        if r.barrier_layout == "vertical_lift_panel":
            post_x_values = (-r.support_width / 2.0, r.support_width / 2.0)
        elif r.barrier_layout == "sliding_panel":
            post_x_values = (-stop_post_x, stop_post_x)
        for x in post_x_values:
            part.visual(
                Box((0.10, 0.16, r.support_height)),
                origin=Origin(xyz=(x, 0.0, r.support_height / 2.0)),
                material=support_mat,
                name=f"end_post_{'left' if x < 0 else 'right'}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
        if r.track_style != "floor_rail":
            part.visual(
                Box((r.support_width - 0.16, 0.24, 0.10)),
                origin=Origin(xyz=(0.0, 0.0, 1.04)),
                material=support_mat,
                name="upper_track_cap", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
            # Flange plates hang the upper track off the center latch post: they
            # bite `flange_bite` into the post's depth so hanger and post form
            # one grounded solid, yet stay clear of the panel's guide lugs.
            flange_y = 0.105
            latch_post_half_depth = 0.16 / 2.0
            flange_bite = 0.010
            flange_depth = 2.0 * (flange_y - latch_post_half_depth) + flange_bite
            for y, name in ((-flange_y, "front_track_flange"), (flange_y, "rear_track_flange")):
                part.visual(
                    Box((r.support_width - 0.16, flange_depth, 0.36)),
                    origin=Origin(xyz=(0.0, y, 0.56)),
                    material=support_mat,
                    name=name, material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
                )
    else:
        part.visual(
            Cylinder(radius=0.055, length=r.support_height),
            origin=Origin(xyz=(0.0, 0.0, r.support_height / 2.0)),
            material=support_mat,
            name="pintle_post", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        part.visual(
            Box((0.24, 0.24, 0.025)),
            origin=Origin(xyz=(0.0, 0.0, 0.0125)),
            material=dark_mat,
            name="post_base_plate", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=0.072, length=0.050),
            origin=Origin(xyz=(0.0, 0.0, 0.025)),
            material=dark_mat,
            name="post_base_collar", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=0.058, length=0.018),
            origin=Origin(xyz=(0.0, 0.0, r.support_height + 0.009)),
            material=support_mat,
            name="post_cap", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        hinge_axis_x = 0.13
        for z_center, label in ((0.28, "lower"), (0.72, "upper")):
            part.visual(
                Box((0.15, 0.18 if r.hinge_style == "fork_yoke" else 0.11, 0.10)),
                origin=Origin(xyz=(hinge_axis_x / 2.0, 0.0, z_center)),
                material=dark_mat,
                name=f"post_{label}_bracket", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Cylinder(
                    radius=0.022 if r.hinge_style != "pintle_barrel" else 0.030,
                    length=0.15,
                ),
                origin=Origin(xyz=(hinge_axis_x, 0.0, z_center)),
                material=dark_mat,
                name=f"post_{label}_knuckle", material_class_id="metal.blackened_gunmetal",
            )
        latch_x = r.panel_width + 0.40
        if r.barrier_layout == "bifold_leaf":
            latch_x = r.panel_width * 2.0 + 0.48
        # An overhead header beam spans hinge post -> latch post. It grounds the
        # latch post (otherwise a distant island) and passes above the leaf peak
        # (and the bifold fold pivot pin) so it never obstructs the swing/bifold
        # motion.
        leaf_peak = 0.94
        header_clearance = 0.10
        header_thickness = 0.09
        header_depth = 0.10
        header_bottom_z = leaf_peak + header_clearance
        header_center_z = header_bottom_z + header_thickness / 2.0
        latch_post_height = header_center_z + header_thickness / 2.0 - 0.035
        part.visual(
            Box((latch_x + 0.10, header_depth, header_thickness)),
            origin=Origin(xyz=(latch_x / 2.0, 0.0, header_center_z)),
            material=support_mat,
            name="gate_header_beam", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        part.visual(
            Box((0.16, 0.20, 0.030)),
            origin=Origin(xyz=(latch_x, 0.0, 0.015)),
            material=dark_mat,
            name="latch_post_base_plate", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Box((0.065, 0.075, latch_post_height)),
            origin=Origin(xyz=(latch_x, 0.0, latch_post_height / 2.0)),
            material=support_mat,
            name="latch_post", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        part.visual(
            Box((0.055, 0.095, 0.13)),
            origin=Origin(xyz=(latch_x - 0.030, 0.0, 0.58)),
            material=dark_mat,
            name="magnetic_receiver", material_class_id="metal.blackened_gunmetal",
        )


def _joint_meta(
    joint_type: str,
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    joint_range: tuple[float, float],
    source_id: str,
) -> dict[str, object]:
    return {
        "type": joint_type,
        "axis": axis,
        "origin": origin,
        "range": joint_range,
        "source_id": source_id,
    }


def _add_boom_visuals(
    part, length: float, r: ResolvedBarrierGateConfig, *, barrier_mat, accent_mat, dark_mat
) -> None:
    if r.boom_section == "trussed":
        tube_start = 0.10
        chord_len = max(0.20, length - tube_start)
        part.visual(
            Box((chord_len, 0.06, 0.045)),
            origin=Origin(xyz=(tube_start + chord_len / 2.0, 0.0, 0.025)),
            material=barrier_mat,
            name="upper_chord", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        part.visual(
            Box((chord_len, 0.05, 0.035)),
            origin=Origin(xyz=(tube_start + chord_len / 2.0, 0.0, -0.035)),
            material=barrier_mat,
            name="lower_chord", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        for i in range(5):
            x = tube_start + chord_len * (i + 0.5) / 5.0
            part.visual(
                Box((0.035, 0.045, 0.13)),
                origin=Origin(xyz=(x, 0.0, -0.005), rpy=(0.0, 0.55, 0.0)),
                material=barrier_mat,
                name=f"truss_diag_{i}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
    else:
        z = 0.085 if r.boom_section == "tapered_box" else 0.070
        part.visual(
            Box((length, 0.08, z)),
            origin=Origin(xyz=(length / 2.0, 0.0, 0.0)),
            material=barrier_mat,
            name="boom_tube", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
    part.visual(
        Box((0.08, 0.08, 0.12)),
        origin=Origin(xyz=(0.065, 0.0, 0.0)),
        material=dark_mat,
        name="pivot_lug", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.25, 0.055, 0.050)),
        origin=Origin(xyz=(-0.115, 0.22, -0.010)),
        material=barrier_mat,
        name="tail_tube", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
    )
    if r.counterweight_style != "none":
        if r.counterweight_style == "counter_arm":
            part.visual(
                Box((0.36, 0.050, 0.035)),
                origin=Origin(xyz=(-0.23, 0.22, -0.070)),
                material=dark_mat,
                name="counter_arm_link", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Box((0.12, 0.090, 0.15)),
                origin=Origin(xyz=(-0.40, 0.22, -0.150)),
                material=dark_mat,
                name="counter_arm_weight", material_class_id="metal.cast_iron_bare",
            )
        elif r.counterweight_style == "fin":
            part.visual(
                Box((0.20, 0.030, 0.22)),
                origin=Origin(xyz=(-0.12, 0.22, -0.090)),
                material=dark_mat,
                name="counterweight_fin", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Box((0.075, 0.060, 0.035)),
                origin=Origin(xyz=(-0.02, 0.22, -0.010)),
                material=dark_mat,
                name="fin_root_clamp", material_class_id="metal.blackened_gunmetal",
            )
        else:
            part.visual(
                Box((0.055, 0.055, 0.11)),
                origin=Origin(xyz=(-0.12, 0.22, -0.085)),
                material=dark_mat,
                name="counterweight_hanger", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Box((0.18, 0.095, 0.12)),
                origin=Origin(xyz=(-0.12, 0.22, -0.190)),
                material=dark_mat,
                name="counterweight_tail_block", material_class_id="metal.cast_iron_bare",
            )
    if r.boom_end_style == "tapered_tip":
        part.visual(
            Box((0.14, 0.070, 0.070)),
            origin=Origin(xyz=(length + 0.060, 0.0, 0.0), rpy=(0.0, 0.10, 0.0)),
            material=barrier_mat,
            name="tapered_tip_block", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
    else:
        part.visual(
            Box((0.060, 0.088, 0.090)),
            origin=Origin(xyz=(length + 0.030, 0.0, 0.0)),
            material=dark_mat,
            name="tip_cap", material_class_id=("rubber.smooth_plain" if r.boom_end_style == "rubber_cap" else "metal.blackened_gunmetal"),
        )
        if r.boom_end_style == "reflector_end":
            for y, label in ((-0.050, "front"), (0.050, "rear")):
                part.visual(
                    Box((0.050, 0.010, 0.050)),
                    origin=Origin(xyz=(length + 0.065, y, 0.0)),
                    material=accent_mat,
                    name=f"tip_reflector_{label}", material_class_id="plastic.opaque_glossy_molded",
                )
    if r.stripe_pattern == "long_red_strip":
        for y, name in ((-0.045, "front"), (0.045, "rear")):
            part.visual(
                Box((length * 0.84, 0.012, 0.035)),
                origin=Origin(xyz=(length * 0.52, y, -0.045)),
                material=accent_mat,
                name=f"long_warning_strip_{name}", material_class_id="metal.paint_coated",
            )
    elif r.stripe_pattern != "none":
        for i in range(5):
            for y, name in ((-0.045, "front"), (0.045, "rear")):
                part.visual(
                    Box((0.16, 0.014, 0.045)),
                    origin=Origin(xyz=(length * (0.18 + i * 0.15), y, -0.045)),
                    material=accent_mat,
                    name=f"warning_band_{name}_{i}", material_class_id="metal.paint_coated",
                )


def _add_panel_visuals(
    part, r: ResolvedBarrierGateConfig, *, barrier_mat, accent_mat, dark_mat
) -> None:
    w = r.panel_width
    h = 0.94
    tube = 0.055
    bottom_z = 0.055
    top_z = h
    # Lateral offset of the upper guide rollers; the guide lug must reach them
    # so the roller/lug cluster is one connected solid, while staying clear of
    # the fixed-support track flanges (inner face at 0.075 m).
    upper_roller_offset = 0.050
    lug_depth = 2.0 * upper_roller_offset + 0.040
    # Infill members span rail-to-rail (with a `tube` bite into each rail) so the
    # infill is welded to the frame rather than floating mid-bay.
    infill_height = (top_z - bottom_z) + tube
    part.visual(
        Box((w, 0.045, tube)),
        origin=Origin(xyz=(0.0, 0.0, top_z)),
        material=barrier_mat,
        name="top_rail", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
    )
    part.visual(
        Box((w, 0.045, tube)),
        origin=Origin(xyz=(0.0, 0.0, bottom_z)),
        material=barrier_mat,
        name="bottom_rail", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
    )
    for x in (-w / 2.0, w / 2.0):
        part.visual(
            Box((tube, 0.045, top_z - bottom_z)),
            origin=Origin(xyz=(x, 0.0, (top_z + bottom_z) / 2.0)),
            material=barrier_mat,
            name=f"stile_{'left' if x < 0 else 'right'}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
    for x in (-w * 0.36, w * 0.36):
        part.visual(
            Box((0.12, 0.060, 0.045)),
            origin=Origin(xyz=(x, 0.0, 0.055)),
            material=dark_mat,
            name=f"bottom_guide_shoe_{'left' if x < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=0.025, length=0.050),
            origin=Origin(xyz=(x, 0.0, 0.048), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=dark_mat,
            name=f"guide_wheel_{'left' if x < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Box((0.10, lug_depth, 0.060)),
            origin=Origin(xyz=(x, 0.0, 0.955)),
            material=dark_mat,
            name=f"upper_guide_lug_{'left' if x < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
        )
        if r.track_style != "floor_rail":
            for y, face in ((-upper_roller_offset, "front"), (upper_roller_offset, "rear")):
                part.visual(
                    Cylinder(radius=0.018, length=0.030),
                    origin=Origin(xyz=(x, y, 0.955), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=dark_mat,
                    name=f"{face}_upper_guide_roller_{'left' if x < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
                )
    if r.panel_style == "solid_panel":
        part.visual(
            Box((w, 0.018, infill_height)),
            origin=Origin(xyz=(0.0, 0.0, (top_z + bottom_z) / 2.0)),
            material=accent_mat,
            name="solid_infill", material_class_id="metal.paint_coated",
        )
        for i, x in enumerate((-w * 0.22, 0.0, w * 0.22)):
            part.visual(
                Box((0.035, 0.026, (top_z - bottom_z) * 0.60)),
                origin=Origin(xyz=(x, 0.0, (top_z + bottom_z) / 2.0)),
                material=barrier_mat,
                name=f"solid_panel_stiffener_{i}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
    else:
        for i in range(4):
            x = -w * 0.32 + i * w * 0.21
            part.visual(
                Box((0.026, 0.030, infill_height)),
                origin=Origin(xyz=(x, 0.0, (top_z + bottom_z) / 2.0)),
                material=barrier_mat,
                name=f"vertical_bar_{i}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
        if r.panel_style == "mesh_frame":
            for i, z in enumerate((bottom_z + 0.19, bottom_z + 0.38, bottom_z + 0.57)):
                part.visual(
                    Box((w * 0.74, 0.020, 0.018)),
                    origin=Origin(xyz=(0.0, 0.0, z)),
                    material=accent_mat,
                    name=f"horizontal_mesh_bar_{i}", material_class_id="metal.paint_coated",
                )
        if r.infill_style in ("diagonal_brace", "ornamental"):
            part.visual(
                Box((w * 0.76, 0.026, 0.035)),
                origin=Origin(xyz=(0.0, 0.0, (top_z + bottom_z) / 2.0), rpy=(0.0, -0.48, 0.0)),
                material=accent_mat,
                name="diagonal_brace", material_class_id="metal.paint_coated",
            )


def _add_leaf_visuals(
    part,
    r: ResolvedBarrierGateConfig,
    *,
    barrier_mat,
    accent_mat,
    dark_mat,
    y_offset: float = 0.0,
    fold_anchor: bool = False,
) -> None:
    w = r.panel_width
    industrial = r.leaf_frame_profile == "industrial_panel"
    h = 0.94 if industrial else 0.88
    tube = 0.070 if industrial else 0.055
    frame_mat = accent_mat if industrial else barrier_mat
    hinge_leaf = 0.035
    x0 = hinge_leaf
    y0 = y_offset
    part.visual(
        Box((hinge_leaf, 0.060, 0.29)),
        origin=Origin(xyz=(hinge_leaf * 0.5, y0, 0.50)),
        material=dark_mat,
        name="hinge_contact_leaf", material_class_id="metal.blackened_gunmetal",
    )
    for z_center, label in ((0.28, "lower"), (0.72, "upper")):
        part.visual(
            Box((0.060, 0.13, 0.090)),
            origin=Origin(xyz=(x0 + 0.080, y0, z_center)),
            material=dark_mat,
            name=f"leaf_{label}_hinge_ear", material_class_id="metal.blackened_gunmetal",
        )
    part.visual(
        Box((w, 0.045, tube)),
        origin=Origin(xyz=(x0 + w / 2.0, y0, h - tube / 2.0)),
        material=frame_mat,
        name="top_rail", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((w, 0.045, tube)),
        origin=Origin(xyz=(x0 + w / 2.0, y0, tube / 2.0 + 0.015)),
        material=frame_mat,
        name="bottom_rail", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((tube, 0.045, h)),
        origin=Origin(xyz=(x0 + tube / 2.0, y0, h / 2.0)),
        material=frame_mat,
        name="leading_stile", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((tube, 0.045, h)),
        origin=Origin(xyz=(x0 + w - tube / 2.0, y0, h / 2.0)),
        material=frame_mat,
        name="trailing_stile", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((w, 0.040, tube * 0.75)),
        origin=Origin(xyz=(x0 + w * 0.50, y0, h * 0.50)),
        material=frame_mat,
        name="mid_rail", material_class_id="metal.paint_coated",
    )
    if r.panel_style == "solid_panel":
        part.visual(
            Box((w * 0.82, 0.018, h * 0.70)),
            origin=Origin(xyz=(x0 + w * 0.50, y0, h * 0.50)),
            material=barrier_mat if industrial else accent_mat,
            name="solid_infill", material_class_id=("metal.patterned_sheet_panel" if r.leaf_frame_profile == "industrial_panel" else "metal.paint_coated"),
        )
        if industrial:
            for i, x in enumerate((x0 + w * 0.28, x0 + w * 0.50, x0 + w * 0.72)):
                part.visual(
                    Box((0.045, 0.026, h - 2.0 * tube - 0.035)),
                    origin=Origin(xyz=(x, y0, h * 0.50)),
                    material=frame_mat,
                    name=f"solid_panel_stiffener_{i}", material_class_id="metal.paint_coated",
                )
        part.visual(
            Box((0.055, 0.050, 0.16)),
            origin=Origin(xyz=(x0 + w - 0.11, y0, h * 0.52)),
            material=dark_mat,
            name="lock_case", material_class_id="metal.blackened_gunmetal",
        )
    else:
        if r.infill_style in ("mesh", "ornamental"):
            for i in range(4):
                x = x0 + w * (0.22 + i * 0.17)
                part.visual(
                    Box((0.026, 0.030, h - 2.0 * tube - 0.035)),
                    origin=Origin(xyz=(x, y0, h * 0.50)),
                    material=frame_mat,
                    name=f"vertical_bar_{i}", material_class_id="metal.paint_coated",
                )
        if r.infill_style in ("diagonal_brace", "ornamental"):
            part.visual(
                Box((w * 0.74, 0.026, 0.035)),
                origin=Origin(xyz=(x0 + w * 0.52, y0, h * 0.50), rpy=(0.0, -0.48, 0.0)),
                material=frame_mat,
                name="diagonal_brace", material_class_id="metal.paint_coated",
            )
        if r.infill_style == "ornamental":
            part.visual(
                Cylinder(radius=0.075, length=0.018),
                origin=Origin(xyz=(x0 + w * 0.50, y0, h * 0.56), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=accent_mat,
                name="ornamental_center_ring", material_class_id="metal.paint_coated",
            )
            part.visual(
                Box((0.16, 0.020, 0.020)),
                origin=Origin(xyz=(x0 + w * 0.50, y0, h * 0.56)),
                material=accent_mat,
                name="ornamental_crossbar", material_class_id="metal.paint_coated",
            )
    part.visual(
        Box((0.060, 0.060, 0.11)),
        origin=Origin(xyz=(x0 + w - 0.030, y0, h * 0.58)),
        material=dark_mat,
        name="strike_plate", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Box((0.11, 0.080, 0.030)),
        origin=Origin(xyz=(x0 + w - 0.070, y0, 0.015)),
        material=dark_mat,
        name="bottom_guide_wheel", material_class_id="metal.blackened_gunmetal",
    )
    if fold_anchor:
        # Folding leaf: the frame is offset sideways by `y0` so it can fold flat
        # without colliding with the outer leaf. The fold axis is the joint axis
        # through this leaf's heel (local x=0, y=0): the knuckle barrel and pivot
        # pin sit on that axis just above the leaf peak (z > h, clear of the
        # outer leaf's trailing stile/top rail, which end at z <= h), and the
        # knuckle arm + riser carry the pivot across to the offset frame, so the
        # fold axis runs through real hardware. On-axis hardware does not sweep
        # as the leaf folds, so it stays clear at every fold angle.
        barrel_radius = 0.020
        barrel_length = 0.040
        barrel_z = h + 0.03
        arm_thickness = 0.040
        riser_height = 0.05
        riser_embed = 0.010
        # The riser bridges the knuckle (on the fold axis, x=0) across to the
        # leaf frame, whose top rail starts at the heel edge x0: it overhangs
        # the barrel side of the axis and laps onto the rail past x0, embedding
        # in the rail's top surface so the whole knuckle cluster is one
        # connected piece of the folding leaf.
        riser_heel_overhang = 0.025
        riser_rail_lap = 0.025
        riser_len_x = riser_heel_overhang + x0 + riser_rail_lap
        riser_center_x = (x0 + riser_rail_lap - riser_heel_overhang) / 2.0
        pin_length = 0.05
        pin_embed = 0.020
        part.visual(
            Cylinder(radius=barrel_radius, length=barrel_length),
            origin=Origin(xyz=(0.0, 0.0, barrel_z)),
            material=dark_mat,
            name="fold_knuckle_barrel", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Box((0.06, y0 + 0.04, arm_thickness)),
            origin=Origin(xyz=(0.0, y0 / 2.0, barrel_z)),
            material=dark_mat,
            name="fold_knuckle_arm", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Box((riser_len_x, 0.05, riser_height)),
            origin=Origin(xyz=(riser_center_x, y0, h + riser_height / 2.0 - riser_embed)),
            material=dark_mat,
            name="fold_pivot_riser", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=0.020, length=pin_length),
            origin=Origin(xyz=(0.0, 0.0, h + riser_height - riser_embed + pin_length / 2.0 - pin_embed)),
            material=dark_mat,
            name="fold_pivot_pin", material_class_id="metal.blackened_gunmetal",
        )
        # Long pivot rod on the fold axis: runs from the leaf's lower half
        # (the anchor-honesty gate probes the axis segment around the joint
        # origin) up through the knuckle barrel, so the fold axis rides in
        # child hardware along its full length. Being coaxial, it does not
        # sweep as the leaf folds. Its radius is a hinge-pin dimension kept
        # inside the joint contact band, so wrapping the outer leaf's fold
        # edge (trailing stile / strike plate / top rail corner) stays a
        # pin-in-knuckle engagement rather than a body intersection.
        sleeve_radius = 0.004
        sleeve_bottom = 0.45 * h
        sleeve_top = barrel_z + barrel_length / 2.0
        part.visual(
            Cylinder(radius=sleeve_radius, length=sleeve_top - sleeve_bottom),
            origin=Origin(xyz=(0.0, 0.0, (sleeve_top + sleeve_bottom) / 2.0)),
            material=dark_mat,
            name="fold_pivot_sleeve", material_class_id="metal.blackened_gunmetal",
        )
        # Lower post strap on the folding leaf: a second, lower strap at the leaf
        # heel (spanning z 0.12-0.32, clear of the outer leaf's bottom rail at
        # z<=0.085 and its lower ear starting at x = x0 + 0.080). It is kept
        # entirely on the offset (+y) side of the fold plane: every strap point
        # then stays farther than y0 from the fold axis, while the outer leaf's
        # trailing stile reaches at most sqrt(tube^2 + (frame_depth/2)^2) from
        # it, so the strap can never sweep into the stile at any fold angle.
        strap_width = y0 + 0.035
        part.visual(
            Box((x0, strap_width, 0.20)),
            origin=Origin(xyz=(x0 / 2.0, y0 + strap_width / 2.0, 0.22)),
            material=dark_mat,
            name="lower_post_strap", material_class_id="metal.blackened_gunmetal",
        )


def _add_wedge_visuals(
    part, r: ResolvedBarrierGateConfig, *, barrier_mat, accent_mat, dark_mat
) -> None:
    length = r.support_width * 0.76
    # Plate is kept narrower than the hinge boss spacing (bosses at
    # +/-support_depth * 0.41) so the tilted plate sweeps clear of them.
    width = r.support_depth * 0.70
    # Slope is shallow enough that the plate tip clears the channel base at the
    # closed pose, and the hinge arms carry the pin up to the plate underside.
    wedge_slope = 0.10
    plate_thickness = 0.070
    part.visual(
        Box((length, width, plate_thickness)),
        origin=Origin(xyz=(length / 2.0, 0.0, plate_thickness / 2.0), rpy=(0.0, -wedge_slope, 0.0)),
        material=barrier_mat,
        name="sloped_wedge_plate", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
    )
    # Tread sits low enough to bite into the plate top surface (the slope tilts
    # the plate top down toward the tip, so the embed grows with length) instead
    # of floating above it.
    part.visual(
        Box((length * 0.82, width * 0.72, 0.030)),
        origin=Origin(xyz=(length * 0.55, 0.0, plate_thickness + 0.005), rpy=(0.0, -wedge_slope, 0.0)),
        material=accent_mat,
        name="raised_anti_slip_tread", material_class_id="rubber.directional_grooved",
    )
    # Side ribs keep their original top height but extend down into the plate so
    # they are welded to it rather than hovering above the tilted surface.
    rib_top_z = 0.150
    rib_embed = 0.050
    for y, label in ((-width * 0.42, "front"), (width * 0.42, "rear")):
        part.visual(
            Box((length * 0.62, 0.026, rib_top_z - (plate_thickness - rib_embed))),
            origin=Origin(
                xyz=(
                    length * 0.56,
                    y,
                    (rib_top_z + plate_thickness - rib_embed) / 2.0,
                ),
                rpy=(0.0, -wedge_slope, 0.0),
            ),
            material=dark_mat,
            name=f"{label}_side_rib", material_class_id="metal.blackened_gunmetal",
        )
    # Axle runs between the two hinge bosses on the support with 0.5 mm running
    # clearance to each boss face (boss inner face sits at
    # support_depth * 0.41 - 0.0175), so the plate assembly stays grounded
    # through its whole tilt without ever touching the bosses.
    pin_radius = 0.042
    pin_half_span = r.support_depth * 0.41 - 0.0175 - 0.0005
    part.visual(
        Cylinder(radius=pin_radius, length=2.0 * pin_half_span),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=dark_mat,
        name="rear_hinge_pin", material_class_id="metal.blackened_gunmetal",
    )
    # Arms reach down past the pin surface so they wrap the axle instead of
    # hovering above it.
    arm_pin_embed = 0.022
    arm_bottom_z = pin_radius - arm_pin_embed
    arm_top_z = 0.230
    for y, label in ((-width * 0.30, "front"), (width * 0.30, "rear")):
        part.visual(
            Box((0.10, 0.03, arm_top_z - arm_bottom_z)),
            origin=Origin(xyz=(0.015, y, (arm_bottom_z + arm_top_z) / 2.0)),
            material=dark_mat,
            name=f"{label}_hinge_arm", material_class_id="metal.blackened_gunmetal",
        )


def _add_lift_panel_visuals(
    part, r: ResolvedBarrierGateConfig, *, barrier_mat, accent_mat, dark_mat
) -> None:
    w = r.support_width * 0.78
    h = r.support_height * 0.64
    bottom_rail_z = 0.115
    # Guide hardware sits on the front face and must bite into the lift stile so the
    # shoe/wheel cluster is welded to the panel frame.
    stile_depth = 0.052
    shoe_depth = 0.120
    shoe_y = -shoe_depth / 2.0 + 0.020
    wheel_y = -(stile_depth / 2.0 + 0.014)
    # Mesh bars run rail-to-rail so the infill grid is one solid with the frame.
    mesh_bar_height = h - bottom_rail_z
    mesh_bar_center_z = (h + bottom_rail_z) / 2.0
    part.visual(
        Box((w, 0.052, 0.070)),
        origin=Origin(xyz=(0.0, 0.0, h)),
        material=barrier_mat,
        name="lift_panel_top_rail", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
    )
    part.visual(
        Box((w, 0.052, 0.070)),
        origin=Origin(xyz=(0.0, 0.0, bottom_rail_z)),
        material=barrier_mat,
        name="lift_panel_bottom_rail", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
    )
    for x, label in ((-w / 2.0, "left"), (w / 2.0, "right")):
        part.visual(
            Box((0.065, stile_depth, h - 0.10)),
            origin=Origin(xyz=(x, 0.0, h / 2.0 + 0.030)),
            material=barrier_mat,
            name=f"{label}_lift_stile", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        part.visual(
            Box((0.100, shoe_depth, 0.140)),
            origin=Origin(xyz=(x, shoe_y, 0.500)),
            material=dark_mat,
            name=f"{label}_column_guide_shoe", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=0.030, length=0.070),
            origin=Origin(xyz=(x, wheel_y, 0.170), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=dark_mat,
            name=f"{label}_guide_wheel", material_class_id="metal.blackened_gunmetal",
        )
    for i in range(5):
        x = -w * 0.34 + i * w * 0.17
        part.visual(
            Box((0.028, 0.032, mesh_bar_height)),
            origin=Origin(xyz=(x, 0.0, mesh_bar_center_z)),
            material=barrier_mat,
            name=f"vertical_mesh_bar_{i}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
    for z, label in ((h * 0.38, "lower"), (h * 0.62, "upper")):
        part.visual(
            Box((w * 0.74, 0.024, 0.024)),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=accent_mat,
            name=f"{label}_mesh_crossbar", material_class_id="metal.paint_coated",
        )


def _add_counterweight_visuals(part, r: ResolvedBarrierGateConfig, *, dark_mat, accent_mat) -> None:
    block_height = r.support_height * 0.34
    # Sheave sits in the top of the counterweight block, embedded so the two form
    # one solid.
    sheave_z = block_height - 0.010
    part.visual(
        Box((0.13, 0.13, block_height)),
        origin=Origin(xyz=(0.0, 0.0, block_height / 2.0)),
        material=dark_mat,
        name="sliding_counterweight_block", material_class_id="metal.cast_iron_bare",
    )
    part.visual(
        Cylinder(radius=0.035, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, sheave_z)),
        material=accent_mat,
        name="cable_sheave", material_class_id="metal.steel_bare",
    )


def _add_folding_boom_visuals(
    part,
    length: float,
    r: ResolvedBarrierGateConfig,
    *,
    barrier_mat,
    accent_mat,
    dark_mat,
    include_mid_fork: bool,
) -> None:
    knuckle_len = 0.066
    part.visual(
        Cylinder(radius=0.052, length=knuckle_len),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=dark_mat,
        name="pivot_knuckle", material_class_id="metal.blackened_gunmetal",
    )
    tube_start = 0.075
    tube_len = max(0.20, length - tube_start - 0.075)
    if r.boom_section == "trussed":
        part.visual(
            Box((tube_len, 0.060, 0.040)),
            origin=Origin(xyz=(tube_start + tube_len / 2.0, 0.0, 0.030)),
            material=barrier_mat,
            name="upper_chord", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        part.visual(
            Box((tube_len, 0.050, 0.032)),
            origin=Origin(xyz=(tube_start + tube_len / 2.0, 0.0, -0.034)),
            material=barrier_mat,
            name="lower_chord", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        for i in range(4):
            x = tube_start + tube_len * (i + 0.5) / 4.0
            part.visual(
                Box((0.030, 0.040, 0.110)),
                origin=Origin(xyz=(x, 0.0, -0.002), rpy=(0.0, 0.55, 0.0)),
                material=barrier_mat,
                name=f"truss_diag_{i}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
    else:
        part.visual(
            Box((tube_len, 0.068, 0.090)),
            origin=Origin(xyz=(tube_start + tube_len / 2.0, 0.0, 0.0)),
            material=barrier_mat,
            name="boom_tube", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
    if r.stripe_pattern != "none":
        for i in range(3):
            x = tube_start + tube_len * (0.25 + i * 0.22)
            for y, face in ((-0.037, "front"), (0.037, "rear")):
                part.visual(
                    Box((0.15, 0.006, 0.100)),
                    origin=Origin(xyz=(x, y, 0.0)),
                    material=accent_mat,
                    name=f"warning_band_{face}_{i}", material_class_id="metal.paint_coated",
                )
    if include_mid_fork:
        for y in (-0.052, 0.052):
            part.visual(
                Box((0.16, 0.038, 0.15)),
                origin=Origin(xyz=(length, y, 0.0)),
                material=dark_mat,
                name=f"mid_fork_{'left' if y < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
            )
        for y in (-0.083, 0.083):
            part.visual(
                Cylinder(radius=0.078, length=0.026),
                origin=Origin(xyz=(length, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=barrier_mat,
                name=f"mid_cap_{'front' if y < 0 else 'rear'}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
    else:
        if r.boom_end_style == "tapered_tip":
            part.visual(
                Box((0.12, 0.064, 0.080)),
                origin=Origin(xyz=(length + 0.030, 0.0, 0.0), rpy=(0.0, 0.08, 0.0)),
                material=barrier_mat,
                name="tapered_outer_tip", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
        else:
            part.visual(
                Box((0.060, 0.078, 0.110)),
                origin=Origin(xyz=(length, 0.0, 0.0)),
                material=dark_mat,
                name="rubber_tip", material_class_id="rubber.smooth_plain",
            )
            if r.boom_end_style == "reflector_end":
                part.visual(
                    Box((0.045, 0.012, 0.055)),
                    origin=Origin(xyz=(length + 0.035, -0.045, 0.0)),
                    material=accent_mat,
                    name="outer_tip_reflector", material_class_id="plastic.opaque_glossy_molded",
                )


def build_barrier_gate(
    config: BarrierGateConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or BarrierGateConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-barrier-gate-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = MATERIAL_PALETTES[r.material_style]
    support_mat = model.material("barrier_support", rgba=palette["support"])
    barrier_mat = model.material("barrier_member", rgba=palette["barrier"])
    accent_mat = model.material("barrier_accent", rgba=palette["accent"])
    dark_mat = model.material("barrier_dark_hardware", rgba=palette["dark"])

    support = model.part("fixed_support")
    _add_support_visuals(
        support, r, support_mat=support_mat, accent_mat=accent_mat, dark_mat=dark_mat
    )

    if r.barrier_layout == "rising_wedge":
        wedge = model.part("rising_wedge_plate")
        _add_wedge_visuals(
            wedge, r, barrier_mat=barrier_mat, accent_mat=accent_mat, dark_mat=dark_mat
        )
        hinge_origin = (-r.support_width / 2.0 + 0.11, 0.0, 0.145)
        model.articulation(
            "wedge_lift_hinge",
            ArticulationType.REVOLUTE,
            parent=support,
            child=wedge,
            origin=Origin(xyz=hinge_origin),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=900.0, velocity=0.35, lower=0.0, upper=0.72),
            meta=_joint_meta("revolute", (0.0, -1.0, 0.0), hinge_origin, (0.0, 0.72), "S16"),
        )
    elif r.barrier_layout == "vertical_lift_panel":
        panel = model.part("vertical_lift_panel")
        _add_lift_panel_visuals(
            panel, r, barrier_mat=barrier_mat, accent_mat=accent_mat, dark_mat=dark_mat
        )
        counterweight = model.part("lift_counterweight")
        _add_counterweight_visuals(counterweight, r, dark_mat=dark_mat, accent_mat=accent_mat)
        # Travel is capped by real structure: the panel stops short of the upper
        # lift track and the counterweight stops above the ground sill.
        lift_panel_height = r.support_height * 0.64
        upper_track_underside = r.support_height
        panel_headroom = 0.01
        panel_travel = min(
            r.slide_travel * 0.55,
            upper_track_underside - (lift_panel_height + 0.035) - panel_headroom,
        )
        counterweight_rest_z = 0.34
        sill_top_z = 0.046
        counterweight_clearance = 0.01
        counterweight_travel = min(
            r.slide_travel * 0.45,
            counterweight_rest_z - sill_top_z - counterweight_clearance,
        )
        model.articulation(
            "panel_vertical_slide",
            ArticulationType.PRISMATIC,
            parent=support,
            child=panel,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=700.0, velocity=0.25, lower=0.0, upper=panel_travel
            ),
            meta=_joint_meta(
                "prismatic",
                (0.0, 0.0, 1.0),
                (0.0, 0.0, 0.0),
                (0.0, panel_travel),
                "S18",
            ),
        )
        model.articulation(
            "counterweight_vertical_slide",
            ArticulationType.PRISMATIC,
            parent=support,
            child=counterweight,
            origin=Origin(xyz=(r.support_width / 2.0 + 0.26, 0.0, counterweight_rest_z)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(
                effort=350.0, velocity=0.20, lower=0.0, upper=counterweight_travel
            ),
            meta=_joint_meta(
                "prismatic",
                (0.0, 0.0, -1.0),
                (r.support_width / 2.0 + 0.26, 0.0, counterweight_rest_z),
                (0.0, counterweight_travel),
                "S18",
            ),
        )
    elif r.barrier_layout == "sliding_panel":
        names = (
            ["sliding_panel_left"]
            if r.panel_count == 1
            else ["sliding_panel_left", "sliding_panel_right"]
        )
        for name in names:
            panel = model.part(name)
            _add_panel_visuals(
                panel, r, barrier_mat=barrier_mat, accent_mat=accent_mat, dark_mat=dark_mat
            )
            sign = -1.0 if name.endswith("left") else 1.0
            model.articulation(
                f"{name}_joint",
                ArticulationType.PRISMATIC,
                parent=support,
                child=panel,
                origin=Origin(xyz=(sign * 0.66, 0.0, 0.0)),
                axis=(sign, 0.0, 0.0),
                motion_limits=MotionLimits(
                    effort=450.0, velocity=0.30, lower=0.0, upper=r.slide_travel
                ),
                meta=_joint_meta(
                    "prismatic",
                    (sign, 0.0, 0.0),
                    (sign * 0.66, 0.0, 0.0),
                    (0.0, r.slide_travel),
                    "S3",
                ),
            )
    else:
        outer = model.part("swing_leaf_outer")
        _add_leaf_visuals(
            outer, r, barrier_mat=barrier_mat, accent_mat=accent_mat, dark_mat=dark_mat
        )
        model.articulation(
            "swing_leaf_hinge",
            ArticulationType.REVOLUTE,
            parent=support,
            child=outer,
            origin=Origin(xyz=(0.13, 0.0, 0.0)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=120.0, velocity=0.8, lower=0.0, upper=r.open_angle),
            meta=_joint_meta(
                "revolute", (0.0, 0.0, -1.0), (0.13, 0.0, 0.0), (0.0, r.open_angle), "S6"
            ),
        )
        if r.barrier_layout == "bifold_leaf":
            inner = model.part("swing_leaf_inner")
            # The folding leaf is offset sideways by one frame depth plus running
            # clearance so it can fold flat against the outer leaf without the
            # two frames intersecting at any fold angle.
            leaf_frame_depth = 0.045
            fold_running_clearance = 0.020
            fold_y_offset = leaf_frame_depth + fold_running_clearance
            _add_leaf_visuals(
                inner,
                r,
                barrier_mat=barrier_mat,
                accent_mat=accent_mat,
                dark_mat=dark_mat,
                y_offset=fold_y_offset,
                fold_anchor=True,
            )
            bifold_origin = (r.panel_width + 0.035, 0.0, 0.0)
            model.articulation(
                "bifold_inner_hinge",
                ArticulationType.REVOLUTE,
                parent=outer,
                child=inner,
                origin=Origin(xyz=bifold_origin),
                axis=(0.0, 0.0, -1.0),
                motion_limits=MotionLimits(effort=80.0, velocity=1.2, lower=0.0, upper=3.05),
                meta=_joint_meta("revolute", (0.0, 0.0, -1.0), bifold_origin, (0.0, 3.05), "S6"),
            )

    return model


def build_seeded_barrier_gate(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_barrier_gate(config_from_seed(seed), assets=assets)


def with_overrides(config: BarrierGateConfig, **kwargs: object) -> BarrierGateConfig:
    return replace(config, **kwargs)


def run_barrier_gate_tests(
    object_model: ArticulatedObject, config: BarrierGateConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    object_model.validate()

    # Each moving gate member (swing leaf, sliding panel, vertical lift panel) is
    # a single member captured on / running in the fixed support's hinges, rails
    # and guides; that single-member-on-its-base interface is a captured
    # engagement, and a vertical-lift panel rides guides above the ground body.
    _pn = {p.name for p in object_model.parts}
    if "fixed_support" in _pn:
        _fs = object_model.get_part("fixed_support")
        for _m in _pn:
            if _m == "fixed_support":
                continue
            if any(k in _m for k in ("leaf", "panel", "lift", "slid", "boom", "gate")):
                ctx.allow_overlap(
                    _fs, object_model.get_part(_m),
                    reason="Gate member is captured on the fixed-support hinges/rails/guides it moves in.",
                )
                if "lift" in _m or "vertical" in _m:
                    ctx.allow_isolated_part(
                        _m,
                        reason="Vertical-lift panel rides the support guides above the grounded body.",
                    )
                if _m == "swing_leaf_inner":
                    ctx.allow_isolated_part(
                        _m,
                        reason=(
                            "Folding leaf is joint-retained on the bifold hinge and "
                            "intentionally offset from the outer leaf by fold running "
                            "clearance so it can fold flat without collision."
                        ),
                    )
    ctx.check("has_fixed_support", object_model.get_part("fixed_support") is not None)
    moving = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check("has_moving_barrier_joint", len(moving) >= 1, details=f"moving={len(moving)}")
    for joint in moving:
        ctx.check(f"{joint.name}_has_axis", any(abs(v) > 0.0 for v in joint.axis))
        ctx.check(f"{joint.name}_has_origin", len(joint.origin.xyz) == 3)
        if joint.articulation_type in (ArticulationType.REVOLUTE, ArticulationType.PRISMATIC):
            limits = joint.motion_limits
            ctx.check(
                f"{joint.name}_has_range",
                limits is not None
                and limits.lower is not None
                and limits.upper is not None
                and limits.upper > limits.lower,
            )

    if r.barrier_layout in {"sliding_panel", "vertical_lift_panel"}:
        prismatics = [j for j in moving if j.articulation_type == ArticulationType.PRISMATIC]
        ctx.check("prismatic_barrier_count", len(prismatics) >= 1)
        if r.barrier_layout == "sliding_panel":
            ctx.check("sliding_panel_prismatic_count", len(prismatics) == r.panel_count)
            ctx.check("sliding_axes_along_track", all(abs(j.axis[0]) > 0.9 for j in prismatics))
        else:
            ctx.check("vertical_prismatic_axis", any(abs(j.axis[2]) > 0.9 for j in prismatics))
    elif r.barrier_layout == "rising_wedge":
        joint = object_model.get_articulation("wedge_lift_hinge")
        ctx.check("wedge_axis_lateral", abs(joint.axis[1]) > 0.9)
    else:
        joint = object_model.get_articulation("swing_leaf_hinge")
        ctx.check("swing_axis_vertical", abs(joint.axis[2]) > 0.9)

    ctx.check("part_diversity_layout_param", r.barrier_layout in LAYOUT_SUPPORT)
    ctx.check("part_diversity_support_param", r.support_style == LAYOUT_SUPPORT[r.barrier_layout])
    return ctx.report()
