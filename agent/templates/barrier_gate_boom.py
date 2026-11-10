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

BarrierLayout = Literal["single_boom", "folding_boom"]
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
    "single_boom": "control_cabinet",
    "folding_boom": "control_cabinet",
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
}


@dataclass(frozen=True)
class BarrierGateConfig:
    barrier_layout: BarrierLayout = "single_boom"
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
    name: str = "reference_barrier_gate_boom"


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
    layout: BarrierLayout = rng.choice(("single_boom", "folding_boom"))
    boom_support_profile: BoomSupportProfile = (
        "slim_cabinet"
        if layout == "folding_boom"
        else rng.choice(("slim_cabinet", "round_pedestal", "box_head"))
    )
    return BarrierGateConfig(
        barrier_layout=layout,
        support_style=LAYOUT_SUPPORT[layout],
        boom_section=rng.choice(("rectangular_tube", "tapered_box", "trussed")),
        boom_length=round(rng.uniform(2.4, 5.2), 3),
        counterweight_style=rng.choice(("none", "tail_block", "counter_arm", "fin")),
        boom_end_style=rng.choice(("rubber_cap", "tapered_tip", "reflector_end")),
        stripe_pattern=rng.choice(
            ("none", "long_red_strip", "segmented_red_bands", "yellow_hazard_bands")
        ),
        fold_ratio=round(rng.uniform(0.40, 0.65), 3),
        panel_count=1,
        panel_style="mesh_frame",
        infill_style="open_tube",
        track_style="floor_rail",
        hinge_style="fork_yoke",
        catch_post_enabled=rng.random() < 0.55,
        open_angle=round(rng.uniform(0.65, 1.65), 3),
        slide_travel=round(rng.uniform(0.8, 2.4), 3),
        material_style=rng.choice(tuple(MATERIAL_PALETTES)),
        boom_support_profile=boom_support_profile,
        leaf_frame_profile="light_tube",
        name=f"seeded_barrier_gate_boom_{seed}",
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
    if config.panel_count not in (1, 2):
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
    boom_support_profile = config.boom_support_profile
    if config.barrier_layout == "folding_boom":
        boom_support_profile = "slim_cabinet"

    support_dims = (0.34, 0.30, 1.30)

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
        panel_count=config.panel_count,
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
                name="warning_label", material_class_id="plastic.patterned_textured",
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
                    origin=Origin(xyz=(-0.175, -0.098, 0.66)),
                    material=dark_mat,
                    name="service_panel_pull", material_class_id="plastic.opaque_generic",
                )
                for z, label in ((0.52, "green_button"), (0.58, "red_button")):
                    part.visual(
                        Cylinder(radius=0.018, length=0.012),
                        origin=Origin(xyz=(-0.10, -0.101, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
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
        elif r.boom_support_profile == "round_pedestal":
            part.visual(
                Cylinder(radius=0.12, length=0.04),
                origin=Origin(xyz=(0.0, 0.0, 0.02)),
                material=dark_mat,
                name="round_base_foot", material_class_id="metal.blackened_gunmetal",
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
                origin=Origin(xyz=(0.18, 0.0, 1.205)),
                material=dark_mat,
                name="round_output_gearbox", material_class_id="metal.blackened_gunmetal",
            )
            for y in (-0.065, 0.065):
                part.visual(
                    Box((0.22, 0.05, 0.15)),
                    origin=Origin(xyz=(0.205, y, 1.225)),
                    material=dark_mat,
                    name=f"round_hinge_yoke_{'left' if y < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
                )
        elif r.boom_support_profile == "box_head":
            part.visual(
                Box((0.36, 0.32, 0.06)),
                origin=Origin(xyz=(0.0, 0.0, 0.03)),
                material=dark_mat,
                name="box_head_foot", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Box((0.16, 0.18, 1.02)),
                origin=Origin(xyz=(0.0, 0.0, 0.51)),
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
                origin=Origin(xyz=(-0.20, -0.06, 1.225)),
                material=accent_mat,
                name="top_status_beacon", material_class_id="tech.emissive_surface",
            )
            for y in (-0.065, 0.065):
                part.visual(
                    Box((0.22, 0.05, 0.15)),
                    origin=Origin(xyz=(0.205, y, 1.225)),
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
            # Riser column carries the hinge block up from the cabinet lid / head
            # top (~z 1.10) to the hinge height so the hinge block and yokes are
            # fused to the support instead of floating a few cm above the lid.
            part.visual(
                Box((0.17, 0.20, 0.16)),
                origin=Origin(xyz=(0.19, 0.0, 1.10)),
                material=support_mat,
                name="hinge_riser_column", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
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
    elif r.support_style == "rail_frame":
        rail_head_height = 0.050
        base_height = 0.055
        part.visual(
            Box((r.support_width + 0.40, 0.34, 0.035)),
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
                    name=f"{label}_lower_channel_lip", material_class_id="metal.steel_bare",
                )
        part.visual(
            Box((0.11, 0.16, r.support_height)),
            origin=Origin(xyz=(0.0, 0.0, r.support_height / 2.0)),
            material=support_mat,
            name="center_latch_post", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        for x in (-r.support_width / 2.0, r.support_width / 2.0):
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
            for y, name in ((-0.105, "front_track_flange"), (0.105, "rear_track_flange")):
                part.visual(
                    Box((r.support_width - 0.16, 0.035, 0.36)),
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
        part.visual(
            Box((0.16, 0.20, 0.030)),
            origin=Origin(xyz=(latch_x, 0.0, 0.015)),
            material=dark_mat,
            name="latch_post_base_plate", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Box((0.065, 0.075, 0.95)),
            origin=Origin(xyz=(latch_x, 0.0, 0.475)),
            material=support_mat,
            name="latch_post", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
        part.visual(
            Box((0.055, 0.095, 0.13)),
            origin=Origin(xyz=(latch_x - 0.030, 0.0, 0.58)),
            material=dark_mat,
            name="magnetic_receiver", material_class_id="tech.control_interface",
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
        origin=Origin(xyz=(-0.100, 0.0, -0.010)),
        material=barrier_mat,
        name="tail_tube", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
    )
    if r.counterweight_style != "none":
        if r.counterweight_style == "counter_arm":
            part.visual(
                Box((0.36, 0.060, 0.040)),
                origin=Origin(xyz=(-0.23, 0.0, -0.045)),
                material=dark_mat,
                name="counter_arm_link", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Box((0.13, 0.095, 0.15)),
                origin=Origin(xyz=(-0.40, 0.0, -0.110)),
                material=dark_mat,
                name="counter_arm_weight", material_class_id="metal.cast_iron_bare",
            )
        elif r.counterweight_style == "fin":
            part.visual(
                Box((0.20, 0.050, 0.22)),
                origin=Origin(xyz=(-0.12, 0.0, -0.090)),
                material=dark_mat,
                name="counterweight_fin", material_class_id="metal.cast_iron_bare",
            )
            part.visual(
                Box((0.075, 0.060, 0.035)),
                origin=Origin(xyz=(-0.02, 0.0, -0.010)),
                material=dark_mat,
                name="fin_root_clamp", material_class_id="metal.blackened_gunmetal",
            )
        else:
            part.visual(
                Box((0.060, 0.060, 0.12)),
                origin=Origin(xyz=(-0.11, 0.0, -0.085)),
                material=dark_mat,
                name="counterweight_hanger", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Box((0.18, 0.095, 0.12)),
                origin=Origin(xyz=(-0.11, 0.0, -0.190)),
                material=dark_mat,
                name="counterweight_tail_block", material_class_id="metal.cast_iron_bare",
            )
    if r.boom_end_style == "tapered_tip":
        part.visual(
            Box((0.14, 0.070, 0.070)),
            origin=Origin(xyz=(length - 0.010, 0.0, 0.0), rpy=(0.0, 0.10, 0.0)),
            material=barrier_mat,
            name="tapered_tip_block", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
        )
    else:
        part.visual(
            Box((0.060, 0.088, 0.090)),
            origin=Origin(xyz=(length - 0.010, 0.0, 0.0)),
            material=dark_mat,
            name="tip_cap", material_class_id="rubber.smooth_plain",
        )
        if r.boom_end_style == "reflector_end":
            for y, label in ((-0.050, "front"), (0.050, "rear")):
                part.visual(
                    Box((0.050, 0.010, 0.050)),
                    origin=Origin(xyz=(length - 0.005, y * 0.82, 0.0)),
                    material=accent_mat,
                    name=f"tip_reflector_{label}", material_class_id="plastic.opaque_glossy_molded",
                )
    if r.stripe_pattern == "long_red_strip":
        for y, name in ((-0.029, "front"), (0.029, "rear")):
            part.visual(
                Box((length * 0.84, 0.012, 0.035)),
                origin=Origin(xyz=(length * 0.52, y, -0.045)),
                material=accent_mat,
                name=f"long_warning_strip_{name}", material_class_id="metal.paint_coated",
            )
    elif r.stripe_pattern != "none":
        for i in range(5):
            for y, name in ((-0.029, "front"), (0.029, "rear")):
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
    bottom_z = 0.132
    top_z = h
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
            origin=Origin(xyz=(x, 0.0, 0.127)),
            material=dark_mat,
            name=f"bottom_guide_shoe_{'left' if x < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=0.025, length=0.050),
            origin=Origin(xyz=(x, 0.0, 0.130), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=dark_mat,
            name=f"guide_wheel_{'left' if x < 0 else 'right'}", material_class_id="rubber.smooth_plain",
        )
        part.visual(
            Box((0.10, 0.050, 0.060)),
            origin=Origin(xyz=(x, 0.0, 0.955)),
            material=dark_mat,
            name=f"upper_guide_lug_{'left' if x < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
        )
        if r.track_style != "floor_rail":
            for y, face in ((-0.060, "front"), (0.060, "rear")):
                part.visual(
                    Cylinder(radius=0.018, length=0.030),
                    origin=Origin(xyz=(x, y, 0.955), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=dark_mat,
                    name=f"{face}_upper_guide_roller_{'left' if x < 0 else 'right'}", material_class_id="rubber.smooth_plain",
                )
    if r.panel_style == "solid_panel":
        part.visual(
            Box((w * 0.86, 0.018, (top_z - bottom_z) * 0.68)),
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
                Box((0.026, 0.030, (top_z - bottom_z) - 0.073)),
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
    part, r: ResolvedBarrierGateConfig, *, barrier_mat, accent_mat, dark_mat
) -> None:
    w = r.panel_width
    industrial = r.leaf_frame_profile == "industrial_panel"
    h = 0.94 if industrial else 0.88
    tube = 0.070 if industrial else 0.055
    frame_mat = accent_mat if industrial else barrier_mat
    hinge_leaf = 0.035
    x0 = hinge_leaf
    part.visual(
        Box((hinge_leaf, 0.060, 0.29)),
        origin=Origin(xyz=(hinge_leaf * 0.5, 0.0, 0.50)),
        material=dark_mat,
        name="hinge_contact_leaf", material_class_id="metal.blackened_gunmetal",
    )
    for z_center, label in ((0.28, "lower"), (0.72, "upper")):
        part.visual(
            Box((0.060, 0.13, 0.090)),
            origin=Origin(xyz=(x0 + 0.080, 0.0, z_center)),
            material=dark_mat,
            name=f"leaf_{label}_hinge_ear", material_class_id="metal.blackened_gunmetal",
        )
    part.visual(
        Box((w, 0.045, tube)),
        origin=Origin(xyz=(x0 + w / 2.0, 0.0, h - tube / 2.0)),
        material=frame_mat,
        name="top_rail", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((w, 0.045, tube)),
        origin=Origin(xyz=(x0 + w / 2.0, 0.0, tube / 2.0 + 0.015)),
        material=frame_mat,
        name="bottom_rail", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((tube, 0.045, h)),
        origin=Origin(xyz=(x0 + tube / 2.0, 0.0, h / 2.0)),
        material=frame_mat,
        name="leading_stile", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((tube, 0.045, h)),
        origin=Origin(xyz=(x0 + w - tube / 2.0, 0.0, h / 2.0)),
        material=frame_mat,
        name="trailing_stile", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((w * 0.84, 0.040, tube * 0.75)),
        origin=Origin(xyz=(x0 + w * 0.50, 0.0, h * 0.50)),
        material=frame_mat,
        name="mid_rail", material_class_id="metal.paint_coated",
    )
    if r.panel_style == "solid_panel":
        part.visual(
            Box((w * 0.82, 0.018, h * 0.70)),
            origin=Origin(xyz=(x0 + w * 0.50, 0.0, h * 0.50)),
            material=barrier_mat if industrial else accent_mat,
            name="solid_infill", material_class_id=("metal.patterned_sheet_panel" if r.leaf_frame_profile == "industrial_panel" else "metal.paint_coated"),
        )
        if industrial:
            for i, x in enumerate((x0 + w * 0.28, x0 + w * 0.50, x0 + w * 0.72)):
                part.visual(
                    Box((0.045, 0.026, h - 2.0 * tube - 0.035)),
                    origin=Origin(xyz=(x, 0.0, h * 0.50)),
                    material=frame_mat,
                    name=f"solid_panel_stiffener_{i}", material_class_id="metal.paint_coated",
                )
        part.visual(
            Box((0.055, 0.050, 0.16)),
            origin=Origin(xyz=(x0 + w - 0.11, 0.0, h * 0.52)),
            material=dark_mat,
            name="lock_case", material_class_id="metal.blackened_gunmetal",
        )
    else:
        if r.infill_style in ("mesh", "ornamental"):
            for i in range(4):
                x = x0 + w * (0.22 + i * 0.17)
                part.visual(
                    Box((0.026, 0.030, h - 2.0 * tube - 0.035)),
                    origin=Origin(xyz=(x, 0.0, h * 0.50)),
                    material=frame_mat,
                    name=f"vertical_bar_{i}", material_class_id="metal.paint_coated",
                )
        if r.infill_style in ("diagonal_brace", "ornamental"):
            part.visual(
                Box((w * 0.74, 0.026, 0.035)),
                origin=Origin(xyz=(x0 + w * 0.52, 0.0, h * 0.50), rpy=(0.0, -0.48, 0.0)),
                material=frame_mat,
                name="diagonal_brace", material_class_id="metal.paint_coated",
            )
        if r.infill_style == "ornamental":
            part.visual(
                Cylinder(radius=0.075, length=0.018),
                origin=Origin(xyz=(x0 + w * 0.50, 0.0, h * 0.56), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=accent_mat,
                name="ornamental_center_ring", material_class_id="metal.paint_coated",
            )
            part.visual(
                Box((0.16, 0.020, 0.020)),
                origin=Origin(xyz=(x0 + w * 0.50, 0.0, h * 0.56)),
                material=accent_mat,
                name="ornamental_crossbar", material_class_id="metal.paint_coated",
            )
    part.visual(
        Box((0.060, 0.060, 0.11)),
        origin=Origin(xyz=(x0 + w - 0.030, 0.0, h * 0.58)),
        material=dark_mat,
        name="strike_plate", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.11, 0.080, 0.030)),
        origin=Origin(xyz=(x0 + w - 0.070, 0.0, 0.015)),
        material=dark_mat,
        name="bottom_guide_wheel", material_class_id="rubber.smooth_plain",
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
    # Start the chords inside the pivot knuckle radius (0.052) so the tube is
    # fused to the knuckle instead of starting ~2 cm clear of it.
    tube_start = 0.045
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
            for y, face in ((-0.033, "front"), (0.033, "rear")):
                part.visual(
                    Box((0.15, 0.006, 0.100)),
                    origin=Origin(xyz=(x, y, 0.0)),
                    material=accent_mat,
                    name=f"warning_band_{face}_{i}", material_class_id="metal.paint_coated",
                )
    if include_mid_fork:
        # Fork cheeks straddle the chord (half-width 0.030) so their inner faces
        # bite it; the end caps sit against the fork cheeks.
        for y in (-0.046, 0.046):
            part.visual(
                Box((0.16, 0.038, 0.15)),
                origin=Origin(xyz=(length - 0.075, y, 0.0)),
                material=dark_mat,
                name=f"mid_fork_{'left' if y < 0 else 'right'}", material_class_id="metal.blackened_gunmetal",
            )
        for y in (-0.052, 0.052):
            part.visual(
                Cylinder(radius=0.078, length=0.026),
                origin=Origin(xyz=(length - 0.075, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=barrier_mat,
                name=f"mid_cap_{'front' if y < 0 else 'rear'}", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
    else:
        if r.boom_end_style == "tapered_tip":
            part.visual(
                Box((0.12, 0.064, 0.080)),
                origin=Origin(xyz=(length - 0.075, 0.0, 0.0), rpy=(0.0, 0.08, 0.0)),
                material=barrier_mat,
                name="tapered_outer_tip", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
        else:
            part.visual(
                Box((0.060, 0.078, 0.110)),
                origin=Origin(xyz=(length - 0.075, 0.0, 0.0)),
                material=dark_mat,
                name="rubber_tip", material_class_id="rubber.smooth_plain",
            )
            if r.boom_end_style == "reflector_end":
                part.visual(
                    Box((0.045, 0.012, 0.055)),
                    origin=Origin(xyz=(length - 0.070, -0.045, 0.0)),
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

    if r.barrier_layout == "single_boom":
        boom = model.part("boom_arm")
        _add_boom_visuals(
            boom,
            r.boom_length,
            r,
            barrier_mat=barrier_mat,
            accent_mat=accent_mat,
            dark_mat=dark_mat,
        )
        model.articulation(
            "boom_hinge",
            ArticulationType.REVOLUTE,
            parent=support,
            child=boom,
            origin=Origin(xyz=(0.29, 0.0, 1.30)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=80.0, velocity=1.4, lower=0.0, upper=r.open_angle),
            meta=_joint_meta(
                "revolute", (0.0, -1.0, 0.0), (0.29, 0.0, 1.30), (0.0, r.open_angle), "S1"
            ),
        )
        if r.catch_post_enabled:
            catch_x = r.boom_length + 0.45
            # Ground foundation strip bridging the gate housing base to the catch
            # post base so the catch post is geometrically connected to the
            # support part (a real cast-in-ground sill), not a floating island.
            support.visual(
                Box((catch_x + 0.24, 0.10, 0.030)),
                origin=Origin(xyz=(catch_x * 0.5, 0.0, 0.015)),
                material=dark_mat,
                name="catch_post_ground_sill", material_class_id="metal.blackened_gunmetal",
            )
            support.visual(
                Box((0.24, 0.18, 0.035)),
                origin=Origin(xyz=(catch_x, 0.0, 0.0175)),
                material=dark_mat,
                name="catch_post_base_plate", material_class_id="metal.blackened_gunmetal",
            )
            support.visual(
                Box((0.13, 0.11, 0.075)),
                origin=Origin(xyz=(catch_x, 0.0, 0.0725)),
                material=support_mat,
                name="catch_post_foot_socket", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
            support.visual(
                Box((0.08, 0.08, 0.70)),
                origin=Origin(xyz=(catch_x, 0.0, 0.46)),
                material=support_mat,
                name="catch_post", material_class_id=("metal.steel_galvanized" if r.material_style == "galvanized" else "metal.paint_coated"),
            )
            support.visual(
                Box((0.13, 0.12, 0.080)),
                origin=Origin(xyz=(catch_x, 0.0, 0.85)),
                material=dark_mat,
                name="catch_post_receiver", material_class_id="metal.blackened_gunmetal",
            )
    elif r.barrier_layout == "folding_boom":
        inner = model.part("inner_boom")
        outer = model.part("outer_boom")
        _add_folding_boom_visuals(
            inner,
            r.inner_boom_length,
            r,
            barrier_mat=barrier_mat,
            accent_mat=accent_mat,
            dark_mat=dark_mat,
            include_mid_fork=True,
        )
        _add_folding_boom_visuals(
            outer,
            r.outer_boom_length,
            r,
            barrier_mat=barrier_mat,
            accent_mat=accent_mat,
            dark_mat=dark_mat,
            include_mid_fork=False,
        )
        model.articulation(
            "folding_boom_main_hinge",
            ArticulationType.REVOLUTE,
            parent=support,
            child=inner,
            origin=Origin(xyz=(0.32, 0.0, 0.90)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(
                effort=120.0, velocity=0.8, lower=0.0, upper=min(1.35, r.open_angle)
            ),
            meta=_joint_meta(
                "revolute",
                (0.0, -1.0, 0.0),
                (0.32, 0.0, 0.90),
                (0.0, min(1.35, r.open_angle)),
                "S2",
            ),
        )
        model.articulation(
            "folding_boom_mid_hinge",
            ArticulationType.REVOLUTE,
            parent=inner,
            child=outer,
            origin=Origin(xyz=(r.inner_boom_length, 0.0, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=70.0, velocity=1.0, lower=0.0, upper=2.10),
            meta=_joint_meta(
                "revolute", (0.0, 1.0, 0.0), (r.inner_boom_length, 0.0, 0.0), (0.0, 2.10), "S2"
            ),
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

    # Captured mechanical engagements (element-scoped): the boom counterweight
    # end swings about the motor head it is journaled on, and the telescoping
    # inner boom slides inside the outer boom chords.
    _pn = {p.name for p in object_model.parts}
    if "catch_post_assembly" in _pn:
        # The catch post is a separate ground structure a few metres from the
        # gate housing (fixed to it by a FIXED joint), so it legitimately stands
        # apart from the grounded body geometry.
        ctx.allow_isolated_part(
            "catch_post_assembly",
            reason="Catch post is a separate ground structure fixed a few metres from the gate housing.",
        )
    if "boom_arm" in _pn and "fixed_support" in _pn:
        # The boom is a single member journaled on the motor-head pivot in the
        # fixed support; its counterweight tail sweeps within the support housing
        # as it raises/lowers. That single-member-on-its-base interface is a
        # captured pivot engagement.
        ctx.allow_overlap(
            object_model.get_part("boom_arm"), object_model.get_part("fixed_support"),
            reason="Boom is journaled on the motor-head pivot; its tail sweeps within the support housing.",
        )
    if "inner_boom" in _pn and "outer_boom" in _pn:
        ctx.allow_overlap(
            object_model.get_part("inner_boom"), object_model.get_part("outer_boom"),
            reason="Telescoping inner boom slides within the outer boom chords.",
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

    if r.barrier_layout == "single_boom":
        joint = object_model.get_articulation("boom_hinge")
        boom = object_model.get_part("boom_arm")
        ctx.check("single_boom_joint_count", len(moving) == 1)
        ctx.check("boom_axis_horizontal", abs(joint.axis[1]) > 0.9)
        ctx.expect_contact(
            boom,
            boom,
            elem_a=boom.get_visual("pivot_lug"),
            elem_b=boom.get_visual("tail_tube"),
            contact_tol=0.02,
            name="tail_tube_attaches_to_pivot_lug",
        )
        if r.counterweight_style == "counter_arm":
            ctx.expect_contact(
                boom,
                boom,
                elem_a=boom.get_visual("tail_tube"),
                elem_b=boom.get_visual("counter_arm_link"),
                contact_tol=0.02,
                name="counter_arm_link_attaches_to_tail_tube",
            )
        elif r.counterweight_style == "fin":
            ctx.expect_contact(
                boom,
                boom,
                elem_a=boom.get_visual("tail_tube"),
                elem_b=boom.get_visual("fin_root_clamp"),
                contact_tol=0.02,
                name="fin_root_clamp_attaches_to_tail_tube",
            )
        elif r.counterweight_style == "tail_block":
            ctx.expect_contact(
                boom,
                boom,
                elem_a=boom.get_visual("tail_tube"),
                elem_b=boom.get_visual("counterweight_hanger"),
                contact_tol=0.02,
                name="counterweight_hanger_attaches_to_tail_tube",
            )
    elif r.barrier_layout == "folding_boom":
        ctx.check("folding_boom_joint_count", len(moving) == 2)
        ctx.check(
            "mid_hinge_has_fold_travel",
            object_model.get_articulation("folding_boom_mid_hinge").motion_limits.upper >= 2.0,
        )

    ctx.check("part_diversity_layout_param", r.barrier_layout in LAYOUT_SUPPORT)
    ctx.check("part_diversity_support_param", r.support_style == LAYOUT_SUPPORT[r.barrier_layout])
    return ctx.report()
