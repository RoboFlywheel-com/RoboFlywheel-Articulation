# SPDX-License-Identifier: Apache-2.0

"""Simple drying rack — modular procedural template.

Category identity: a grounded main frame with a fixed center drying deck and two
independently foldable side wings (REVOLUTE), each carrying hanging rails.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/simple_drying_rack.md``

Slots (exported via ``slot_choices_for_seed``):

* ``central_frame`` — deck / tower / wire base / trestle
* ``wing_frame`` — tube, wire serpentine, industrial box, premium tube, cadquery mesh
* ``lower_support`` — slanted lower frame or none
* ``wing_hinge_mechanism`` — top-cap X, sleeve, hinge-link stay, molded clip, pin barrel
* ``hanging_rail_density`` — jointless rail multiplicity per region

``config_from_seed`` is procedural for every seed (no seed=0 special case). Legal
module tuples are sampled from the spec compatibility matrix with canonical
combos weighted higher.
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
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_geometry,
    wire_from_points,
)

__modular__ = True

CentralFrame = Literal[
    "classic_rect_deck",
    "tube_leg_tower",
    "wire_base_deck",
    "industrial_trestle",
]
WingFrame = Literal[
    "tube_panel_wing",
    "wire_serpentine_wing",
    "box_industrial_wing",
    "premium_tube_wing",
    "cadquery_mesh_wing",
]
LowerSupport = Literal[
    "slanted_rail_frame",
    "minimal_slant_support",
    "wire_mesh_support",
    "rect_tube_support",
    "none_fixed_base_only",
]
WingHingeMechanism = Literal[
    "top_cap_x_hinge",
    "sleeve_on_side_rail",
    "hinge_link_stay",
    "molded_clip_barrel",
    "pin_barrel_y_hinge",
]
HangingRailDensity = Literal[
    "3_rails_per_region",
    "4_rails_per_region",
    "5_rails_central",
    "6_rails_wing",
]
MaterialStyle = Literal["frame_powder", "white_coat", "dark_metal", "teal_coat", "wire_white"]

CENTRAL_FRAMES: tuple[CentralFrame, ...] = (
    "classic_rect_deck",
    "tube_leg_tower",
    "wire_base_deck",
    "industrial_trestle",
)
WING_FRAMES: tuple[WingFrame, ...] = (
    "tube_panel_wing",
    "wire_serpentine_wing",
    "box_industrial_wing",
    "premium_tube_wing",
    "cadquery_mesh_wing",
)
LOWER_SUPPORTS: tuple[LowerSupport, ...] = (
    "slanted_rail_frame",
    "minimal_slant_support",
    "wire_mesh_support",
    "rect_tube_support",
    "none_fixed_base_only",
)
WING_HINGE_MECHANISMS: tuple[WingHingeMechanism, ...] = (
    "top_cap_x_hinge",
    "sleeve_on_side_rail",
    "hinge_link_stay",
    "molded_clip_barrel",
    "pin_barrel_y_hinge",
)
HANGING_RAIL_DENSITIES: tuple[HangingRailDensity, ...] = (
    "3_rails_per_region",
    "4_rails_per_region",
    "5_rails_central",
    "6_rails_wing",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "frame_powder": {
        "frame": (0.86, 0.87, 0.88, 1.0),
        "hinge": (0.27, 0.29, 0.31, 1.0),
        "foot": (0.18, 0.19, 0.20, 1.0),
        "fastener": (0.65, 0.67, 0.70, 1.0),
        "plastic": (0.50, 0.52, 0.50, 1.0),
        "rubber": (0.04, 0.045, 0.045, 1.0),
    },
    "white_coat": {
        "frame": (0.92, 0.93, 0.91, 1.0),
        "hinge": (0.34, 0.38, 0.40, 1.0),
        "foot": (0.22, 0.23, 0.24, 1.0),
        "fastener": (0.05, 0.05, 0.045, 1.0),
        "plastic": (0.34, 0.38, 0.40, 1.0),
        "rubber": (0.04, 0.045, 0.045, 1.0),
    },
    "dark_metal": {
        "frame": (0.22, 0.24, 0.26, 1.0),
        "hinge": (0.12, 0.13, 0.14, 1.0),
        "foot": (0.08, 0.09, 0.10, 1.0),
        "fastener": (0.55, 0.57, 0.58, 1.0),
        "plastic": (0.18, 0.19, 0.20, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
    },
    "teal_coat": {
        "frame": (0.42, 0.62, 0.58, 1.0),
        "hinge": (0.18, 0.36, 0.34, 1.0),
        "foot": (0.14, 0.28, 0.26, 1.0),
        "fastener": (0.72, 0.74, 0.70, 1.0),
        "plastic": (0.30, 0.48, 0.44, 1.0),
        "rubber": (0.05, 0.08, 0.07, 1.0),
    },
    "wire_white": {
        "frame": (0.90, 0.92, 0.90, 1.0),
        "hinge": (0.34, 0.38, 0.40, 1.0),
        "foot": (0.34, 0.38, 0.40, 1.0),
        "fastener": (0.05, 0.05, 0.045, 1.0),
        "plastic": (0.34, 0.38, 0.40, 1.0),
        "rubber": (0.04, 0.045, 0.045, 1.0),
    },
}

RAIL_DENSITY_COUNTS: dict[HangingRailDensity, tuple[int, int, int]] = {
    "3_rails_per_region": (3, 3, 3),
    "4_rails_per_region": (6, 4, 3),
    "5_rails_central": (5, 4, 3),
    "6_rails_wing": (4, 6, 3),
}

TUBE_RADIUS = 0.012
RAIL_RADIUS = 0.0045
HINGE_BARREL_RADIUS = 0.010
HINGE_OFFSET = 0.046
WING_COUNT = 2

# (central, wing, lower, hinge, rail, weight)
_LEGAL_COMBO_ROWS: list[
    tuple[CentralFrame, WingFrame, LowerSupport, WingHingeMechanism, HangingRailDensity, int]
] = []


def _append_combos(
    central: CentralFrame,
    wings: tuple[WingFrame, ...],
    lowers: tuple[LowerSupport, ...],
    hinges: tuple[WingHingeMechanism, ...],
    *,
    base_weight: int,
    canonical_bonus: int = 0,
) -> None:
    for wing in wings:
        for lower in lowers:
            for hinge in hinges:
                for rail in HANGING_RAIL_DENSITIES:
                    weight = base_weight
                    if central == "classic_rect_deck" and wing == "tube_panel_wing":
                        weight += canonical_bonus
                    if lower == "slanted_rail_frame" and hinge == "top_cap_x_hinge":
                        weight += canonical_bonus // 2
                    if wing == "premium_tube_wing" and hinge == "hinge_link_stay":
                        weight += canonical_bonus // 2
                    _LEGAL_COMBO_ROWS.append((central, wing, lower, hinge, rail, weight))


_append_combos(
    "classic_rect_deck",
    ("tube_panel_wing", "premium_tube_wing"),
    ("slanted_rail_frame", "rect_tube_support", "wire_mesh_support"),
    ("top_cap_x_hinge", "sleeve_on_side_rail", "hinge_link_stay"),
    base_weight=6,
    canonical_bonus=8,
)
_append_combos(
    "classic_rect_deck",
    ("cadquery_mesh_wing",),
    ("slanted_rail_frame", "rect_tube_support"),
    ("top_cap_x_hinge", "sleeve_on_side_rail"),
    base_weight=3,
    canonical_bonus=0,
)
_append_combos(
    "tube_leg_tower",
    ("tube_panel_wing", "premium_tube_wing"),
    ("minimal_slant_support", "slanted_rail_frame"),
    ("sleeve_on_side_rail", "top_cap_x_hinge"),
    base_weight=4,
    canonical_bonus=2,
)
for rail in HANGING_RAIL_DENSITIES:
    _LEGAL_COMBO_ROWS.append(
        (
            "wire_base_deck",
            "wire_serpentine_wing",
            "none_fixed_base_only",
            "molded_clip_barrel",
            rail,
            5,
        )
    )
for rail in ("4_rails_per_region", "6_rails_wing"):
    _LEGAL_COMBO_ROWS.append(
        (
            "industrial_trestle",
            "box_industrial_wing",
            "none_fixed_base_only",
            "pin_barrel_y_hinge",
            rail,
            4,
        )  # type: ignore[arg-type]
    )

LEGAL_COMBOS: tuple[
    tuple[CentralFrame, WingFrame, LowerSupport, WingHingeMechanism, HangingRailDensity],
    ...,
] = tuple(row[:5] for row in _LEGAL_COMBO_ROWS)
LEGAL_COMBO_WEIGHTS: tuple[int, ...] = tuple(row[5] for row in _LEGAL_COMBO_ROWS)

_COMPATIBILITY: dict[CentralFrame, dict[str, tuple[str, ...]]] = {
    "classic_rect_deck": {
        "wing": ("tube_panel_wing", "premium_tube_wing", "cadquery_mesh_wing"),
        "lower": ("slanted_rail_frame", "rect_tube_support", "wire_mesh_support"),
        "hinge": ("top_cap_x_hinge", "sleeve_on_side_rail", "hinge_link_stay"),
    },
    "tube_leg_tower": {
        "wing": ("tube_panel_wing", "premium_tube_wing"),
        "lower": ("minimal_slant_support", "slanted_rail_frame"),
        "hinge": ("sleeve_on_side_rail", "top_cap_x_hinge"),
    },
    "wire_base_deck": {
        "wing": ("wire_serpentine_wing",),
        "lower": ("none_fixed_base_only",),
        "hinge": ("molded_clip_barrel",),
    },
    "industrial_trestle": {
        "wing": ("box_industrial_wing",),
        "lower": ("none_fixed_base_only",),
        "hinge": ("pin_barrel_y_hinge",),
    },
}


@dataclass(frozen=True)
class SimpleDryingRackConfig:
    central_frame: CentralFrame | None = None
    wing_frame: WingFrame | None = None
    lower_support: LowerSupport | None = None
    wing_hinge_mechanism: WingHingeMechanism | None = None
    hanging_rail_density: HangingRailDensity | None = None
    material_style: MaterialStyle = "frame_powder"
    deck_width_scale: float = 1.0
    wing_span_scale: float = 1.0
    name: str = "simple_drying_rack"


@dataclass(frozen=True)
class ResolvedSimpleDryingRackConfig:
    central_frame: CentralFrame
    wing_frame: WingFrame
    lower_support: LowerSupport
    wing_hinge_mechanism: WingHingeMechanism
    hanging_rail_density: HangingRailDensity
    material_style: MaterialStyle
    deck_half_width: float
    deck_half_depth: float
    deck_height: float
    wing_width: float
    wing_half_depth: float
    central_rail_count: int
    wing_rail_count: int
    lower_rail_count: int
    tube_radius: float
    rail_radius: float
    palette: dict[str, tuple[float, float, float, float]]
    name: str
    deck_width_scale: float = 1.0


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick_legal_combo(
    rng: random.Random,
) -> tuple[CentralFrame, WingFrame, LowerSupport, WingHingeMechanism, HangingRailDensity]:
    return rng.choices(LEGAL_COMBOS, weights=LEGAL_COMBO_WEIGHTS, k=1)[0]


def config_from_seed(seed: int) -> SimpleDryingRackConfig:
    rng = random.Random(seed)
    central, wing, lower, hinge, rail = _pick_legal_combo(rng)
    material_pool: tuple[MaterialStyle, ...] = (
        "frame_powder",
        "white_coat",
        "dark_metal",
        "teal_coat",
    )
    if central == "wire_base_deck":
        material_pool = ("wire_white", "white_coat", "frame_powder")
    return SimpleDryingRackConfig(
        central_frame=central,
        wing_frame=wing,
        lower_support=lower,
        wing_hinge_mechanism=hinge,
        hanging_rail_density=rail,
        material_style=rng.choice(material_pool),
        deck_width_scale=round(rng.uniform(0.85, 1.20), 4),
        wing_span_scale=round(rng.uniform(0.80, 1.15), 4),
        name=f"seeded_simple_drying_rack_{seed}",
    )


def _downgrade_combo(
    central: CentralFrame,
    wing: WingFrame,
    lower: LowerSupport,
    hinge: WingHingeMechanism,
) -> tuple[CentralFrame, WingFrame, LowerSupport, WingHingeMechanism]:
    gate = _COMPATIBILITY[central]
    if wing not in gate["wing"]:
        wing = gate["wing"][0]  # type: ignore[assignment]
    if lower not in gate["lower"]:
        lower = gate["lower"][0]  # type: ignore[assignment]
    if hinge not in gate["hinge"]:
        hinge = gate["hinge"][0]  # type: ignore[assignment]
    if central == "wire_base_deck":
        lower = "none_fixed_base_only"
    if central == "industrial_trestle":
        lower = "none_fixed_base_only"
    if hinge == "hinge_link_stay" and wing not in ("premium_tube_wing", "tube_panel_wing"):
        hinge = "top_cap_x_hinge"
    if hinge == "molded_clip_barrel" and central != "wire_base_deck":
        hinge = "sleeve_on_side_rail"
    if hinge == "pin_barrel_y_hinge" and central != "industrial_trestle":
        hinge = "top_cap_x_hinge"
    if wing == "wire_serpentine_wing" and central != "wire_base_deck":
        wing = "tube_panel_wing"  # type: ignore[assignment]
    if wing == "box_industrial_wing" and central != "industrial_trestle":
        wing = "tube_panel_wing"  # type: ignore[assignment]
    return central, wing, lower, hinge


def resolve_config(config: SimpleDryingRackConfig) -> ResolvedSimpleDryingRackConfig:
    central = config.central_frame or "classic_rect_deck"
    wing = config.wing_frame or "tube_panel_wing"
    lower = config.lower_support or "slanted_rail_frame"
    hinge = config.wing_hinge_mechanism or "top_cap_x_hinge"
    rail_density = config.hanging_rail_density or "4_rails_per_region"

    for field_name, value, allowed in (
        ("central_frame", central, CENTRAL_FRAMES),
        ("wing_frame", wing, WING_FRAMES),
        ("lower_support", lower, LOWER_SUPPORTS),
        ("wing_hinge_mechanism", hinge, WING_HINGE_MECHANISMS),
        ("hanging_rail_density", rail_density, HANGING_RAIL_DENSITIES),
    ):
        if value not in allowed:
            raise ValueError(f"Unsupported {field_name}: {value}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    central, wing, lower, hinge = _downgrade_combo(central, wing, lower, hinge)

    deck_hw = _clamp(0.34 * config.deck_width_scale, 0.26, 0.46)
    deck_hd = _clamp(0.25 * config.deck_width_scale, 0.18, 0.32)
    deck_h = (
        0.88 if central != "tube_leg_tower" else _clamp(0.72 * config.deck_width_scale, 0.58, 0.82)
    )
    wing_w = _clamp(0.46 * config.wing_span_scale, 0.32, 0.52)
    if central == "tube_leg_tower":
        wing_w = min(wing_w, 0.42)

    central_rails, wing_rails, lower_rails = RAIL_DENSITY_COUNTS[rail_density]

    return ResolvedSimpleDryingRackConfig(
        central_frame=central,
        wing_frame=wing,
        lower_support=lower,
        wing_hinge_mechanism=hinge,
        hanging_rail_density=rail_density,
        material_style=config.material_style,
        deck_half_width=deck_hw,
        deck_half_depth=deck_hd,
        deck_height=deck_h,
        wing_width=wing_w,
        wing_half_depth=deck_hd,
        central_rail_count=central_rails,
        wing_rail_count=wing_rails,
        lower_rail_count=lower_rails,
        tube_radius=TUBE_RADIUS,
        rail_radius=RAIL_RADIUS,
        deck_width_scale=config.deck_width_scale,
        palette=dict(PALETTES[config.material_style]),
        name=config.name,
    )


def _register_palette(
    model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]]
) -> None:
    for key, rgba in palette.items():
        model.material(key, rgba=rgba)


def _add_rod_x(
    part: Part, name: str, x0: float, x1: float, y: float, z: float, radius: float, material: str
) -> None:
    part.visual(
        Cylinder(radius=radius, length=abs(x1 - x0)),
        origin=Origin(xyz=((x0 + x1) * 0.5, y, z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _add_rod_y(
    part: Part, name: str, x: float, y0: float, y1: float, z: float, radius: float, material: str
) -> None:
    part.visual(
        Cylinder(radius=radius, length=abs(y1 - y0)),
        origin=Origin(xyz=(x, (y0 + y1) * 0.5, z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _add_rod_z(
    part: Part, name: str, x: float, y: float, z0: float, z1: float, radius: float, material: str
) -> None:
    part.visual(
        Cylinder(radius=radius, length=abs(z1 - z0)),
        origin=Origin(xyz=(x, y, (z0 + z1) * 0.5)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _add_leg_yz(
    part: Part,
    name: str,
    x: float,
    y0: float,
    z0: float,
    y1: float,
    z1: float,
    radius: float,
    material: str,
) -> None:
    dy = y1 - y0
    dz = z1 - z0
    part.visual(
        Cylinder(radius=radius, length=math.sqrt(dy * dy + dz * dz)),
        origin=Origin(
            xyz=(x, (y0 + y1) * 0.5, (z0 + z1) * 0.5),
            rpy=(-math.atan2(dy, dz), 0.0, 0.0),
        ),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _rail_positions(span: float, count: int, *, centered: bool = True) -> list[float]:
    if count <= 1:
        return [0.0]
    if centered:
        step = (2.0 * span) / (count - 1)
        return [-span + step * index for index in range(count)]
    spacing = span / (count + 1)
    return [spacing * (index + 1) for index in range(count)]


def _tube_mesh(points: list[tuple[float, float, float]], name: str, *, radius: float = 0.006):
    return mesh_from_geometry(
        wire_from_points(
            points,
            radius=radius,
            radial_segments=14,
            closed_path=False,
            cap_ends=True,
            corner_mode="fillet",
            corner_radius=0.018,
            corner_segments=6,
        ),
        name,
    )


def _build_hinge_link(
    model: ArticulatedObject,
    name: str,
    *,
    side_sign: float,
    r: ResolvedSimpleDryingRackConfig,
) -> Part:
    part = model.part(name)
    cheek_y = r.wing_half_depth + 0.006
    plate_span = max(0.54, cheek_y * 2.0 + 0.08)
    part.inertial = Inertial.from_geometry(
        Box((0.09, plate_span, 0.09)),
        mass=0.35,
        origin=Origin(xyz=(-side_sign * 0.018, 0.0, 0.0)),
    )
    part.visual(
        Box((0.020, plate_span, 0.070)),
        origin=Origin(xyz=(-side_sign * 0.022, 0.0, 0.0)),
        material="hinge",
        name="backplate", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.030, plate_span * 0.24, 0.030)),
        origin=Origin(xyz=(-side_sign * 0.010, 0.0, 0.0)),
        material="hinge",
        name="clamp_spine", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.016, plate_span * 0.68, 0.024)),
        origin=Origin(xyz=(side_sign * 0.008, 0.0, 0.0)),
        material="hinge",
        name="clamp_saddle", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.012, plate_span * 0.76, 0.018)),
        origin=Origin(xyz=(-side_sign * 0.018, 0.0, -0.014)),
        material="hinge",
        name="bridge_arm", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.030, 0.012, 0.054)),
        origin=Origin(xyz=(-side_sign * 0.005, cheek_y, 0.0)),
        material="hinge",
        name="front_cheek", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.030, 0.012, 0.054)),
        origin=Origin(xyz=(-side_sign * 0.005, -cheek_y, 0.0)),
        material="hinge",
        name="rear_cheek", material_class_id="metal.paint_coated",
    )
    for cheek_name, y_pos in (("front_cheek", cheek_y), ("rear_cheek", -cheek_y)):
        part.visual(
            Box((0.014, abs(y_pos) * 0.55, 0.032)),
            origin=Origin(xyz=(-side_sign * 0.014, y_pos * 0.5, 0.0)),
            material="hinge",
            name=f"{cheek_name}_tie", material_class_id="metal.paint_coated",
        )
    part.visual(
        Box((0.028, 0.10, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, -0.021)),
        material="hinge",
        name="lower_stop", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.024, 0.10, 0.010)),
        origin=Origin(xyz=(-side_sign * 0.010, 0.0, 0.025)),
        material="hinge",
        name="upper_guide", material_class_id="metal.paint_coated",
    )
    for visual_name, y_pos in (("front_bolt", 0.14), ("rear_bolt", -0.14)):
        part.visual(
            Cylinder(radius=0.006, length=0.020),
            origin=Origin(xyz=(-side_sign * 0.028, y_pos, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="fastener",
            name=visual_name, material_class_id="metal.stainless_matte",
        )
    return part


def _build_tube_wing(
    model: ArticulatedObject,
    name: str,
    *,
    side_sign: float,
    r: ResolvedSimpleDryingRackConfig,
    premium: bool,
) -> Part:
    part = model.part(name)
    part.inertial = Inertial.from_geometry(
        Box((r.wing_width, 0.52, 0.05)),
        mass=1.4,
        origin=Origin(xyz=(side_sign * r.wing_width * 0.5, 0.0, 0.0)),
    )
    _add_rod_y(
        part,
        "hinge_barrel",
        x=0.0,
        y0=-r.wing_half_depth,
        y1=r.wing_half_depth,
        z=0.0,
        radius=HINGE_BARREL_RADIUS,
        material="frame",
    )
    _add_rod_y(
        part,
        "outer_rail",
        x=side_sign * r.wing_width,
        y0=-r.wing_half_depth,
        y1=r.wing_half_depth,
        z=0.0,
        radius=r.tube_radius,
        material="frame",
    )
    y_edge = r.wing_half_depth * 0.92
    _add_rod_x(
        part, "front_frame_rail", 0.0, side_sign * r.wing_width, y_edge, 0.0, r.tube_radius, "frame"
    )
    _add_rod_x(
        part, "rear_frame_rail", 0.0, side_sign * r.wing_width, -y_edge, 0.0, r.tube_radius, "frame"
    )
    part.visual(
        Box((0.036, 0.060, 0.036)),
        origin=Origin(xyz=(side_sign * 0.018, 0.0, 0.0)),
        material="frame",
        name="hinge_bridge", material_class_id="metal.paint_coated",
    )
    for index, x_pos in enumerate(
        _rail_positions(r.wing_width, r.wing_rail_count, centered=False),
        start=1,
    ):
        _add_rod_y(
            part,
            f"hanging_rail_{index}",
            x=side_sign * x_pos,
            y0=-y_edge,
            y1=y_edge,
            z=0.0,
            radius=r.rail_radius,
            material="frame",
        )
    if premium:
        part.visual(
            Box((0.020, 0.10, 0.010)),
            origin=Origin(xyz=(0.0, 0.0, -0.011)),
            material="hinge",
            name="lower_stop_pad", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((0.018, 0.08, 0.010)),
            origin=Origin(xyz=(0.0, 0.0, 0.011)),
            material="hinge",
            name="upper_stop_pad", material_class_id="metal.paint_coated",
        )
    return part


def _build_wire_serpentine_wing(
    model: ArticulatedObject,
    name: str,
    *,
    side_sign: float,
    r: ResolvedSimpleDryingRackConfig,
) -> Part:
    part = model.part(name)
    rail_path = [
        (0.045, -0.480, 0.000),
        (0.820, -0.480, 0.000),
        (0.820, 0.480, 0.000),
        (0.700, 0.480, 0.000),
        (0.700, -0.480, 0.000),
        (0.580, -0.480, 0.000),
        (0.580, 0.480, 0.000),
        (0.460, 0.480, 0.000),
        (0.460, -0.480, 0.000),
        (0.340, -0.480, 0.000),
        (0.340, 0.480, 0.000),
        (0.220, 0.480, 0.000),
        (0.220, -0.480, 0.000),
        (0.100, -0.480, 0.000),
        (0.100, 0.480, 0.000),
        (0.045, 0.480, 0.000),
    ]
    part.visual(
        _tube_mesh(rail_path, f"{name}_wire", radius=0.0055), material="frame", name="wing_wire", material_class_id="metal.mesh_chainmail"
    )
    # Bridge tubes tying the serpentine panel to the hinge links/barrels
    # (the serpentine never reaches the hinge line on its own).
    for bridge_suffix, by in (("mid", 0.0), ("rear", -0.420), ("front", 0.420)):
        part.visual(
            _tube_mesh([(0.020, by, 0.000), (0.100, by, 0.000)], f"{name}_bridge_{bridge_suffix}", radius=0.0055),
            material="frame", name=f"hinge_bridge_{bridge_suffix}", material_class_id="metal.mesh_chainmail",
        )
    part.visual(
        Box((0.052, 0.070, 0.030)),
        origin=Origin(xyz=(0.026, 0.000, 0.000)),
        material="plastic",
        name="hinge_link_mid", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Cylinder(radius=0.012, length=0.050),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material="frame",
        name="hinge_barrel_mid", material_class_id="metal.paint_coated",
    )
    for suffix, y in (("rear", -0.420), ("front", 0.420)):
        part.visual(
            Box((0.052, 0.070, 0.030)),
            origin=Origin(xyz=(0.026, y, 0.000)),
            material="plastic",
            name=f"hinge_link_{suffix}", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Cylinder(radius=0.012, length=0.050),
            origin=Origin(xyz=(0.0, y, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material="frame",
            name=f"hinge_barrel_{suffix}", material_class_id="metal.paint_coated",
        )
    return part


def _build_cadquery_wing(
    model: ArticulatedObject,
    name: str,
    *,
    side_sign: float,
    r: ResolvedSimpleDryingRackConfig,
) -> Part:
    import cadquery as cq

    from sdk import mesh_from_cadquery

    part = model.part(name)
    hd = r.wing_half_depth * 0.92
    ww = r.wing_width
    wp = cq.Workplane("XY")
    barrel = wp.box(0.024, 2.0 * hd, 0.024)
    outer = wp.box(0.024, 2.0 * hd, 0.024).translate((side_sign * ww, 0.0, 0.0))
    front = wp.box(abs(side_sign * ww), 0.024, 0.024).translate((side_sign * ww * 0.5, hd, 0.0))
    rear = wp.box(abs(side_sign * ww), 0.024, 0.024).translate((side_sign * ww * 0.5, -hd, 0.0))
    shape = barrel.union(outer).union(front).union(rear)
    for x_pos in _rail_positions(ww, r.wing_rail_count, centered=False):
        rail = wp.box(0.012, 2.0 * hd, 0.012).translate((side_sign * x_pos, 0.0, 0.0))
        shape = shape.union(rail)
    mesh_name = f"{name}_mesh"
    if model.assets is not None:
        mesh = mesh_from_cadquery(
            shape, model.assets.mesh_path(f"{mesh_name}.obj"), assets=model.assets
        )
    else:
        mesh = mesh_from_cadquery(shape, mesh_name)
    part.visual(mesh, material="frame", name="wing_mesh", material_class_id="metal.paint_coated")
    part.visual(
        Cylinder(radius=HINGE_BARREL_RADIUS, length=2.0 * hd),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material="frame",
        name="hinge_barrel", material_class_id="metal.paint_coated",
    )
    return part


def _build_box_industrial_wing(
    model: ArticulatedObject, name: str, *, side_sign: float, r: ResolvedSimpleDryingRackConfig
) -> Part:
    part = model.part(name)
    for bi, (y, length) in enumerate(((-0.435, 0.37), (0.0, 0.24), (0.435, 0.37))):
        part.visual(
            Cylinder(radius=0.026, length=length),
            origin=Origin(xyz=(0.0, y, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material="frame",
            name=f"barrel_{bi}", material_class_id="metal.paint_coated",
        )
    part.visual(
        Box((0.045, 1.25, 0.045)),
        origin=Origin(xyz=(side_sign * 0.045, 0.0, 0.0)),
        material="frame",
        name="inner_tube", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.055, 1.25, 0.055)),
        origin=Origin(xyz=(side_sign * 0.69, 0.0, 0.0)),
        material="frame",
        name="outer_tube", material_class_id="metal.paint_coated",
    )
    # Rails must bridge inner_tube (x~0.045) to outer_tube (x~0.69) or they float.
    n_rails = r.wing_rail_count
    if n_rails <= 1:
        rail_xs = [0.045]
    else:
        rail_xs = [0.045 + 0.645 * i / (n_rails - 1) for i in range(n_rails)]
    for index, x in enumerate(rail_xs, start=0):
        part.visual(
            Box((0.020, 1.25, 0.020)),
            origin=Origin(xyz=(side_sign * x, 0.0, 0.026)),
            material="hinge",
            name=f"hanging_rail_{index}", material_class_id="metal.paint_coated",
        )
    # Longitudinal stringer tying every hanging rail and both tubes together.
    part.visual(
        Box((0.665, 0.020, 0.020)),
        origin=Origin(xyz=(side_sign * 0.3675, 0.0, 0.026)),
        material="frame",
        name="rail_stringer", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.040, 1.25, 0.035)),
        origin=Origin(xyz=(side_sign * 0.69, 0.0, 0.044)),
        material="plastic",
        name="guard_rail", material_class_id="plastic.opaque_glossy_molded",
    )
    return part


def _add_central_hanging_rails(part: Part, r: ResolvedSimpleDryingRackConfig) -> None:
    span = r.deck_half_width * 0.92
    hd = r.deck_half_depth
    for index, x_pos in enumerate(_rail_positions(span, r.central_rail_count), start=1):
        _add_rod_y(
            part,
            f"center_hanging_rail_{index}",
            x=x_pos,
            y0=-hd,
            y1=hd,
            z=r.deck_height - 0.006,
            radius=r.rail_radius,
            material="frame",
        )


def _build_classic_central(model: ArticulatedObject, r: ResolvedSimpleDryingRackConfig) -> Part:
    central = model.part("central_frame")
    hw, hd, h = r.deck_half_width, r.deck_half_depth, r.deck_height
    central.inertial = Inertial.from_geometry(
        Box((hw * 2.0 + 0.30, hd * 2.0 + 0.18, h)),
        mass=6.5,
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
    )

    if r.wing_hinge_mechanism == "top_cap_x_hinge":
        for sign, cap_name in ((1.0, "top_cap_0"), (-1.0, "top_cap_1")):
            central.visual(
                Box((hw * 2.2, 0.080, 0.034)),
                origin=Origin(xyz=(0.0, sign * (hd + 0.015), h + 0.015)),
                material="plastic",
                name=cap_name, material_class_id="plastic.opaque_glossy_molded",
            )

    deck_z = h - 0.006
    _add_rod_y(central, "left_side_rail", hw, -hd, hd, deck_z, r.tube_radius, "frame")
    _add_rod_y(central, "right_side_rail", -hw, -hd, hd, deck_z, r.tube_radius, "frame")
    _add_rod_x(central, "front_top_rail", -hw, hw, hd, deck_z, r.tube_radius, "frame")
    _add_rod_x(central, "rear_top_rail", -hw, hw, -hd, deck_z, r.tube_radius, "frame")
    _add_central_hanging_rails(central, r)
    rail_span = hw * 0.92
    central.visual(
        Box((rail_span * 2.2, hd * 2.1, 0.040)),
        origin=Origin(xyz=(0.0, 0.0, deck_z)),
        material="frame",
        name="deck_skin", material_class_id="metal.paint_coated",
    )

    if r.wing_hinge_mechanism == "sleeve_on_side_rail":
        for sign, name in ((1.0, "hinge_tube_0"), (-1.0, "hinge_tube_1")):
            _add_rod_y(central, name, sign * hw, -hd, hd, deck_z, HINGE_BARREL_RADIUS, "hinge")
            central.visual(
                Box((0.040, 0.080, 0.040)),
                origin=Origin(xyz=(sign * hw, 0.0, deck_z)),
                material="hinge",
                name=f"{name}_tie", material_class_id="metal.paint_coated",
            )

    leg_scale = 0.72 if r.central_frame == "tube_leg_tower" else 1.0
    for leg_name, x_pos, y0, y1 in (
        ("front_left_leg", hw, 0.31 * leg_scale, hd - 0.01),
        ("rear_left_leg", hw, -0.31 * leg_scale, -(hd - 0.01)),
        ("front_right_leg", -hw, 0.31 * leg_scale, hd - 0.01),
        ("rear_right_leg", -hw, -0.31 * leg_scale, -(hd - 0.01)),
    ):
        _add_leg_yz(central, leg_name, x_pos, y0, 0.03, y1, h - 0.01, r.tube_radius, "frame")

    tie_z = h * (0.41 if r.central_frame != "tube_leg_tower" else 0.36)
    _add_rod_y(central, "left_lower_tie", hw, -0.29, 0.29, tie_z, r.rail_radius, "frame")
    _add_rod_y(central, "right_lower_tie", -hw, -0.29, 0.29, tie_z, r.rail_radius, "frame")
    stab_z = h * 0.25
    stab_y = 0.31 * leg_scale
    _add_rod_x(central, "front_stabilizer", -hw, hw, stab_y, stab_z, r.rail_radius, "frame")
    _add_rod_x(central, "rear_stabilizer", -hw, hw, -stab_y, stab_z, r.rail_radius, "frame")
    for x_pos, y_pos, name in (
        (hw, stab_y, "front_left_stab_tie"),
        (-hw, stab_y, "front_right_stab_tie"),
        (hw, -stab_y, "rear_left_stab_tie"),
        (-hw, -stab_y, "rear_right_stab_tie"),
    ):
        central.visual(
            Box((0.060, 0.060, 0.24)),
            origin=Origin(xyz=(x_pos, y_pos, stab_z + 0.10)),
            material="frame",
            name=name, material_class_id="metal.paint_coated",
        )

    for visual_name, x_pos, y_pos in (
        ("front_left_foot", hw, 0.31 * leg_scale),
        ("rear_left_foot", hw, -0.31 * leg_scale),
        ("front_right_foot", -hw, 0.31 * leg_scale),
        ("rear_right_foot", -hw, -0.31 * leg_scale),
    ):
        central.visual(
            Box((0.05, 0.025, 0.030)),
            origin=Origin(xyz=(x_pos, y_pos, 0.015)),
            material="foot",
            name=visual_name, material_class_id="rubber.smooth_plain",
        )

    if r.lower_support != "none_fixed_base_only":
        central.visual(
            Box((hw * 2.0, 0.066, 0.030)),
            origin=Origin(xyz=(0.0, -hd + 0.05, h - 0.018)),
            material="plastic",
            name="underside_pivot_cover", material_class_id="plastic.opaque_glossy_molded",
        )
    return central


def _build_lower_support(
    model: ArticulatedObject, r: ResolvedSimpleDryingRackConfig
) -> Part | None:
    if r.lower_support == "none_fixed_base_only":
        return None

    lower = model.part("lower_support")
    top = (0.0, 0.0, 0.0)
    if r.lower_support == "minimal_slant_support":
        bottom = (0.0, 0.14, -0.42)
        post_x = r.deck_half_width * 0.95
    elif r.lower_support == "rect_tube_support":
        bottom = (0.0, 0.16, -0.48)
        post_x = r.deck_half_width
    else:
        bottom = (0.0, 0.185, -0.565)
        post_x = r.deck_half_width * 1.35

    rail_len = r.deck_half_width * 2.2
    mid_y = (top[1] + bottom[1]) * 0.5
    mid_z = (top[2] + bottom[2]) * 0.5
    if r.lower_support == "minimal_slant_support":
        skin_size = (rail_len + 0.06, 0.34, abs(bottom[2] - top[2]) + 0.10)
    else:
        skin_size = (rail_len + 0.14, 0.58, abs(bottom[2] - top[2]) + 0.18)
    lower.visual(
        Box(skin_size),
        origin=Origin(xyz=(0.0, mid_y, mid_z)),
        material="frame",
        name="support_skin", material_class_id="metal.paint_coated",
    )
    _add_rod_x(lower, "top_rail", -rail_len / 2.0, rail_len / 2.0, top[1], top[2], 0.009, "frame")
    _add_rod_x(
        lower, "bottom_rail", -rail_len / 2.0, rail_len / 2.0, bottom[1], bottom[2], 0.009, "frame"
    )
    for sign, name in ((-1.0, "side_post_0"), (1.0, "side_post_1")):
        dy = bottom[1] - top[1]
        dz = bottom[2] - top[2]
        length = math.sqrt(dy * dy + dz * dz)
        theta = math.atan2(-dy, dz)
        lower.visual(
            Cylinder(radius=0.009, length=length),
            origin=Origin(
                xyz=(sign * post_x, (top[1] + bottom[1]) / 2.0, (top[2] + bottom[2]) / 2.0),
                rpy=(theta, 0.0, 0.0),
            ),
            material="frame",
            name=name, material_class_id="metal.paint_coated",
        )

    if r.lower_support == "wire_mesh_support":
        mesh_path = [
            (-rail_len / 2.0, top[1], top[2]),
            (rail_len / 2.0, top[1], top[2]),
            (rail_len / 2.0, bottom[1], bottom[2]),
            (-rail_len / 2.0, bottom[1], bottom[2]),
            (-rail_len / 2.0, top[1], top[2]),
        ]
        lower.visual(
            _tube_mesh(mesh_path, "lower_wire_mesh", radius=0.005),
            material="frame",
            name="lower_wire_mesh", material_class_id="metal.mesh_chainmail",
        )

    for index, t in enumerate(_rail_positions(1.0, r.lower_rail_count, centered=False)):
        y = top[1] + (bottom[1] - top[1]) * t
        z = top[2] + (bottom[2] - top[2]) * t
        _add_rod_x(
            lower,
            f"hanging_rail_{index}",
            -rail_len / 2.0 + 0.02,
            rail_len / 2.0 - 0.02,
            y,
            z,
            r.rail_radius,
            "frame",
        )

    for index, sign in enumerate((-1.0, 1.0)):
        lower.visual(
            Box((0.085, 0.050, 0.026)),
            origin=Origin(xyz=(sign * post_x, bottom[1] + 0.010, bottom[2] - 0.006)),
            material="rubber",
            name=f"foot_{index}", material_class_id="rubber.smooth_plain",
        )
    return lower


def _build_wire_base(model: ArticulatedObject, r: ResolvedSimpleDryingRackConfig) -> Part:
    base = model.part("base_frame")
    leg_path = [
        (-0.450, -0.600, 0.040),
        (-0.300, -0.520, r.deck_height),
        (-0.300, 0.520, r.deck_height),
        (-0.450, 0.600, 0.040),
        (0.450, 0.600, 0.040),
        (0.300, 0.520, r.deck_height),
        (0.300, -0.520, r.deck_height),
        (0.450, -0.600, 0.040),
        (-0.450, -0.600, 0.040),
    ]
    base.visual(
        _tube_mesh(leg_path, "base_leg_wire", radius=0.008), material="frame", name="leg_wire", material_class_id="metal.paint_coated"
    )

    deck_path = [
        (-0.300, -0.520, r.deck_height),
        (0.300, -0.520, r.deck_height),
        (0.300, -0.350, r.deck_height),
        (-0.300, -0.350, r.deck_height),
        (-0.300, -0.180, r.deck_height),
        (0.300, -0.180, r.deck_height),
        (0.300, -0.010, r.deck_height),
        (-0.300, -0.010, r.deck_height),
        (-0.300, 0.160, r.deck_height),
        (0.300, 0.160, r.deck_height),
        (0.300, 0.330, r.deck_height),
        (-0.300, 0.330, r.deck_height),
        (-0.300, 0.520, r.deck_height),
        (0.300, 0.520, r.deck_height),
    ]
    base.visual(
        _tube_mesh(deck_path, "base_deck_wire", radius=0.006), material="frame", name="deck_wire", material_class_id="metal.mesh_chainmail"
    )

    for ix, x in enumerate((-0.450, 0.450)):
        for iy, y in enumerate((-0.600, 0.600)):
            base.visual(
                Box((0.160, 0.060, 0.035)),
                origin=Origin(xyz=(x, y, 0.018)),
                material="plastic",
                name=f"foot_{ix}_{iy}", material_class_id="plastic.opaque_glossy_molded",
            )

    hinge_x = 0.30
    for side_index, x in enumerate((-hinge_x, hinge_x)):
        base.visual(
            Box((0.035, 0.095, 0.042)),
            origin=Origin(xyz=(x, 0.000, r.deck_height + 0.020)),
            material="plastic",
            name=f"hinge_block_{side_index}_mid", material_class_id="plastic.opaque_glossy_molded",
        )
        base.visual(
            Box((0.050, 0.055, 0.014)),
            origin=Origin(xyz=(x + (0.022 if x > 0 else -0.022), 0.000, r.deck_height - 0.003)),
            material="plastic",
            name=f"fold_stop_{side_index}_mid", material_class_id="plastic.opaque_glossy_molded",
        )
    return base


def _build_industrial_base(model: ArticulatedObject, r: ResolvedSimpleDryingRackConfig) -> Part:
    base = model.part("base_frame")
    deck_h = 0.92 * r.deck_width_scale
    for side in (-1.0, 1.0):
        side_i = 0 if side < 0.0 else 1
        base.visual(
            Box((0.055, 1.36, 0.055)),
            origin=Origin(xyz=(side * 0.32, 0.0, deck_h)),
            material="frame",
            name="top_rail_0" if side_i == 0 else "top_rail_1", material_class_id="metal.paint_coated",
        )
        for yi, y in enumerate((-0.58, 0.58)):
            base.visual(
                Box((0.06, 0.06, deck_h)),
                origin=Origin(xyz=(side * 0.27, y, deck_h * 0.5)),
                material="frame",
                name=f"{'front' if y < 0 else 'rear'}_leg_{side_i}", material_class_id="metal.paint_coated",
            )
            base.visual(
                Box((0.30, 0.09, 0.045)),
                origin=Origin(xyz=(side * 0.27, y, 0.0225)),
                material="rubber",
                name=f"{'front' if y < 0 else 'rear'}_foot_{side_i}", material_class_id="rubber.smooth_plain",
            )
        # Bracket tying the hinge pin back to the top rail (pin sits outboard);
        # sits in the gaps between the wing's alternating barrels.
        for by in (-0.185, 0.185):
            base.visual(
                Box((0.12, 0.06, 0.105)),
                origin=Origin(xyz=(side * 0.36, by, deck_h)),
                material="frame",
                name=f"pin_bracket_{side_i}_{'a' if by < 0 else 'b'}",
                material_class_id="metal.paint_coated",
            )
        base.visual(
            Cylinder(radius=0.012, length=1.34),
            origin=Origin(xyz=(side * 0.40, 0.0, deck_h + 0.045), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material="hinge",
            name=f"hinge_pin_{side_i}", material_class_id="metal.stainless_matte",
        )
    for yi, y in enumerate((-0.65, 0.0, 0.65)):
        base.visual(
            Box((0.69, 0.055, 0.055)),
            origin=Origin(xyz=(0.0, y, deck_h)),
            material="frame",
            name=f"cross_tube_{yi}", material_class_id="metal.paint_coated",
        )
    return base


def _build_wings(model: ArticulatedObject, r: ResolvedSimpleDryingRackConfig) -> tuple[Part, Part]:
    if r.wing_frame == "wire_serpentine_wing":
        left = _build_wire_serpentine_wing(model, "left_wing_frame", side_sign=1.0, r=r)
        right = _build_wire_serpentine_wing(model, "right_wing_frame", side_sign=-1.0, r=r)
    elif r.wing_frame == "cadquery_mesh_wing":
        left = _build_cadquery_wing(model, "left_wing_frame", side_sign=1.0, r=r)
        right = _build_cadquery_wing(model, "right_wing_frame", side_sign=-1.0, r=r)
    elif r.wing_frame == "box_industrial_wing":
        left = _build_box_industrial_wing(model, "left_wing_frame", side_sign=1.0, r=r)
        right = _build_box_industrial_wing(model, "right_wing_frame", side_sign=-1.0, r=r)
    elif r.wing_frame == "premium_tube_wing":
        left = _build_tube_wing(model, "left_wing_frame", side_sign=1.0, r=r, premium=True)
        right = _build_tube_wing(model, "right_wing_frame", side_sign=-1.0, r=r, premium=True)
    else:
        left = _build_tube_wing(model, "left_wing_frame", side_sign=1.0, r=r, premium=False)
        right = _build_tube_wing(model, "right_wing_frame", side_sign=-1.0, r=r, premium=False)
    return left, right


def _attach_canonical_articulations(
    model: ArticulatedObject,
    *,
    central: Part,
    left_wing: Part,
    right_wing: Part,
    lower: Part | None,
    left_hinge: Part | None,
    right_hinge: Part | None,
    r: ResolvedSimpleDryingRackConfig,
) -> None:
    hw, hd, h = r.deck_half_width, r.deck_half_depth, r.deck_height
    wing_limits = MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=1.30)

    if r.wing_hinge_mechanism == "hinge_link_stay":
        assert left_hinge is not None and right_hinge is not None
        model.articulation(
            "main_to_left_hinge",
            ArticulationType.FIXED,
            parent=central,
            child=left_hinge,
            origin=Origin(xyz=(hw, 0.0, h)),
        )
        model.articulation(
            "main_to_right_hinge",
            ArticulationType.FIXED,
            parent=central,
            child=right_hinge,
            origin=Origin(xyz=(-hw, 0.0, h)),
        )
        model.articulation(
            "left_wing_hinge",
            ArticulationType.REVOLUTE,
            parent=left_hinge,
            child=left_wing,
            origin=Origin(),
            axis=(0.0, -1.0, 0.0),
            motion_limits=wing_limits,
        )
        model.articulation(
            "right_wing_hinge",
            ArticulationType.REVOLUTE,
            parent=right_hinge,
            child=right_wing,
            origin=Origin(),
            axis=(0.0, 1.0, 0.0),
            motion_limits=wing_limits,
        )
    elif r.wing_hinge_mechanism == "top_cap_x_hinge":
        model.articulation(
            "central_to_left_wing",
            ArticulationType.REVOLUTE,
            parent=central,
            child=left_wing,
            origin=Origin(xyz=(0.0, hd + 0.015, h)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=7.0, velocity=2.5, lower=0.0, upper=1.70),
        )
        model.articulation(
            "central_to_right_wing",
            ArticulationType.REVOLUTE,
            parent=central,
            child=right_wing,
            origin=Origin(xyz=(0.0, -(hd + 0.015), h)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=7.0, velocity=2.5, lower=0.0, upper=1.70),
        )
    else:
        model.articulation(
            "central_to_left_wing",
            ArticulationType.REVOLUTE,
            parent=central,
            child=left_wing,
            origin=Origin(xyz=(hw, 0.0, h)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=wing_limits,
        )
        model.articulation(
            "central_to_right_wing",
            ArticulationType.REVOLUTE,
            parent=central,
            child=right_wing,
            origin=Origin(xyz=(-hw, 0.0, h)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=wing_limits,
        )

    if lower is not None:
        model.articulation(
            "central_to_lower_support",
            ArticulationType.REVOLUTE,
            parent=central,
            child=lower,
            origin=Origin(xyz=(0.0, -hd + 0.05, h - 0.042)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=1.6, lower=0.0, upper=1.28),
        )


def _attach_wire_articulations(
    model: ArticulatedObject,
    *,
    base: Part,
    left_wing: Part,
    right_wing: Part,
    r: ResolvedSimpleDryingRackConfig,
) -> None:
    hinge_x = 0.30
    limits = MotionLimits(effort=12.0, velocity=1.6, lower=0.0, upper=1.82)
    model.articulation(
        "wing_hinge_0",
        ArticulationType.REVOLUTE,
        parent=base,
        child=left_wing,
        origin=Origin(xyz=(-hinge_x, 0.000, r.deck_height + 0.020), rpy=(0.0, 0.0, math.pi)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=limits,
    )
    model.articulation(
        "wing_hinge_1",
        ArticulationType.REVOLUTE,
        parent=base,
        child=right_wing,
        origin=Origin(xyz=(hinge_x, 0.000, r.deck_height + 0.020)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=limits,
    )


def _attach_industrial_articulations(
    model: ArticulatedObject,
    *,
    base: Part,
    left_wing: Part,
    right_wing: Part,
    r: ResolvedSimpleDryingRackConfig,
) -> None:
    deck_h = 0.92 * r.deck_width_scale + 0.045
    limits = MotionLimits(effort=80.0, velocity=0.7, lower=0.0, upper=1.38)
    model.articulation(
        "base_to_left_wing",
        ArticulationType.REVOLUTE,
        parent=base,
        child=left_wing,
        origin=Origin(xyz=(0.40, 0.0, deck_h)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=limits,
    )
    model.articulation(
        "base_to_right_wing",
        ArticulationType.REVOLUTE,
        parent=base,
        child=right_wing,
        origin=Origin(xyz=(-0.40, 0.0, deck_h)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=limits,
    )


def build_simple_drying_rack(
    config: SimpleDryingRackConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    _register_palette(model, r.palette)

    if r.central_frame == "wire_base_deck":
        base = _build_wire_base(model, r)
        left_wing, right_wing = _build_wings(model, r)
        _attach_wire_articulations(
            model, base=base, left_wing=left_wing, right_wing=right_wing, r=r
        )
    elif r.central_frame == "industrial_trestle":
        base = _build_industrial_base(model, r)
        left_wing, right_wing = _build_wings(model, r)
        _attach_industrial_articulations(
            model, base=base, left_wing=left_wing, right_wing=right_wing, r=r
        )
    else:
        central = _build_classic_central(model, r)
        lower = _build_lower_support(model, r)
        left_hinge = right_hinge = None
        if r.wing_hinge_mechanism == "hinge_link_stay":
            left_hinge = _build_hinge_link(model, "left_hinge_link", side_sign=1.0, r=r)
            right_hinge = _build_hinge_link(model, "right_hinge_link", side_sign=-1.0, r=r)
        left_wing, right_wing = _build_wings(model, r)
        _attach_canonical_articulations(
            model,
            central=central,
            left_wing=left_wing,
            right_wing=right_wing,
            lower=lower,
            left_hinge=left_hinge,
            right_hinge=right_hinge,
            r=r,
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_simple_drying_rack(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_simple_drying_rack(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedSimpleDryingRackConfig) -> list[tuple[str, str]]:
    return [
        ("central_frame", r.central_frame),
        ("wing_frame", r.wing_frame),
        ("lower_support", r.lower_support),
        ("wing_hinge_mechanism", r.wing_hinge_mechanism),
        ("hanging_rail_density", r.hanging_rail_density),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def _grounded_part_name(r: ResolvedSimpleDryingRackConfig) -> str:
    return (
        "base_frame"
        if r.central_frame in {"wire_base_deck", "industrial_trestle"}
        else "central_frame"
    )


def _left_wing_joint_name(r: ResolvedSimpleDryingRackConfig) -> str:
    if r.central_frame == "wire_base_deck":
        return "wing_hinge_0"
    if r.central_frame == "industrial_trestle":
        return "base_to_left_wing"
    if r.wing_hinge_mechanism == "hinge_link_stay":
        return "left_wing_hinge"
    return "central_to_left_wing"


def run_simple_drying_rack_tests(
    object_model: ArticulatedObject,
    config: SimpleDryingRackConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    grounded_name = _grounded_part_name(r)
    ctx.check("grounded frame present", grounded_name in part_names)
    ctx.check("left wing present", "left_wing_frame" in part_names)
    ctx.check("right wing present", "right_wing_frame" in part_names)
    ctx.check("left wing hinge present", _left_wing_joint_name(r) in joint_names)
    ctx.check(
        "slot_choices match config",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )

    wing_joint_names = [
        name
        for name in joint_names
        if "wing" in name
        and object_model.get_articulation(name).articulation_type == ArticulationType.REVOLUTE
    ]
    ctx.check("at least two wing revolute joints", len(wing_joint_names) >= 2)

    if r.lower_support != "none_fixed_base_only":
        ctx.check("lower support present", "lower_support" in part_names)
        ctx.check("lower support hinge present", "central_to_lower_support" in joint_names)
    else:
        ctx.check("no lower support part", "lower_support" not in part_names)

    grounded = object_model.get_part(grounded_name)
    left_wing = object_model.get_part("left_wing_frame")
    right_wing = object_model.get_part("right_wing_frame")

    if r.wing_hinge_mechanism == "hinge_link_stay":
        left_hinge = object_model.get_part("left_hinge_link")
        right_hinge = object_model.get_part("right_hinge_link")
        ctx.allow_overlap(
            grounded,
            left_hinge,
            elem_a="left_side_rail",
            elem_b="clamp_saddle",
            reason="hinge clamp captures side rail",
        )
        ctx.allow_overlap(
            grounded,
            right_hinge,
            elem_a="right_side_rail",
            elem_b="clamp_saddle",
            reason="hinge clamp captures side rail",
        )
        ctx.allow_overlap(
            left_hinge,
            left_wing,
            reason="hinge link assembly captures wing hinge root",
        )
        ctx.allow_overlap(
            right_hinge,
            right_wing,
            reason="hinge link assembly captures wing hinge root",
        )
        ctx.allow_overlap(
            grounded,
            left_hinge,
            reason="hinge link backplate nests against central deck",
        )
        ctx.allow_overlap(
            grounded,
            right_hinge,
            reason="hinge link backplate nests against central deck",
        )
        if r.lower_support != "none_fixed_base_only":
            lower = object_model.get_part("lower_support")
            ctx.allow_overlap(
                left_hinge,
                lower,
                reason="hinge stay overlaps folded lower frame envelope",
            )
            ctx.allow_overlap(
                right_hinge,
                lower,
                reason="hinge stay overlaps folded lower frame envelope",
            )
        left_joint = object_model.get_articulation("left_wing_hinge")
        right_joint = object_model.get_articulation("right_wing_hinge")
        ctx.expect_contact(
            left_hinge,
            grounded,
            elem_a="clamp_saddle",
            elem_b="left_side_rail",
            contact_tol=0.012,
            name="left_hinge_clamp_contacts_frame",
        )
        with ctx.pose({left_joint: 1.30, right_joint: 1.30}):
            left_outer = ctx.part_element_world_aabb(left_wing, elem="outer_rail")
            left_barrel = ctx.part_element_world_aabb(left_wing, elem="hinge_barrel")
            right_outer = ctx.part_element_world_aabb(right_wing, elem="outer_rail")
            right_barrel = ctx.part_element_world_aabb(right_wing, elem="hinge_barrel")
            if None not in (left_outer, left_barrel, right_outer, right_barrel):
                left_dz = (
                    (left_outer[0][2] + left_outer[1][2]) - (left_barrel[0][2] + left_barrel[1][2])
                ) * 0.5
                right_dz = (
                    (right_outer[0][2] + right_outer[1][2])
                    - (right_barrel[0][2] + right_barrel[1][2])
                ) * 0.5
                ctx.check("folded wings raise outer rails", left_dz > 0.30 and right_dz > 0.30)
    elif r.wing_hinge_mechanism in ("sleeve_on_side_rail", "top_cap_x_hinge", "pin_barrel_y_hinge"):
        if r.central_frame not in {"wire_base_deck", "industrial_trestle"}:
            deck_rails = ("left_side_rail", "right_side_rail", "front_top_rail", "rear_top_rail")
            for wing_part in (left_wing, right_wing):
                for rail_name in deck_rails:
                    ctx.allow_overlap(
                        grounded,
                        wing_part,
                        elem_a=rail_name,
                        elem_b="hinge_barrel",
                        reason="hinge barrel captured on central deck rails",
                    )
        if r.wing_hinge_mechanism == "pin_barrel_y_hinge":
            # left wing rides the pin at +0.40 (hinge_pin_1), right at -0.40 (hinge_pin_0)
            for barrel_elem in ("barrel_0", "barrel_1", "barrel_2"):
                ctx.allow_overlap(
                    grounded,
                    left_wing,
                    elem_a="hinge_pin_1",
                    elem_b=barrel_elem,
                    reason="industrial pin captured by alternating wing barrels",
                )
                ctx.allow_overlap(
                    grounded,
                    right_wing,
                    elem_a="hinge_pin_0",
                    elem_b=barrel_elem,
                    reason="industrial pin captured by alternating wing barrels",
                )

    if r.central_frame == "wire_base_deck":
        ctx.allow_overlap(
            grounded,
            left_wing,
            elem_a="hinge_block_0_mid",
            elem_b="hinge_barrel_mid",
            reason="molded clip captures wing hinge barrel",
        )
        ctx.allow_overlap(
            grounded,
            right_wing,
            elem_a="hinge_block_1_mid",
            elem_b="hinge_barrel_mid",
            reason="molded clip captures wing hinge barrel",
        )
        ctx.allow_overlap(
            grounded,
            left_wing,
            elem_a="hinge_block_0_mid",
            elem_b="hinge_link_mid",
            reason="molded clip captures wing hinge link",
        )
        ctx.allow_overlap(
            grounded,
            right_wing,
            elem_a="hinge_block_1_mid",
            elem_b="hinge_link_mid",
            reason="molded clip captures wing hinge link",
        )

    if r.central_frame == "wire_base_deck":
        hinge_0 = object_model.get_articulation("wing_hinge_0")
        hinge_1 = object_model.get_articulation("wing_hinge_1")
        with ctx.pose({hinge_0: 1.82, hinge_1: 1.82}):
            aabb_0 = ctx.part_element_world_aabb(left_wing, elem="wing_wire")
            aabb_1 = ctx.part_element_world_aabb(right_wing, elem="wing_wire")
            ctx.check(
                "wire wing 0 folds upward",
                aabb_0 is not None and aabb_0[1][2] > r.deck_height + 0.55,
            )
            ctx.check(
                "wire wing 1 folds upward",
                aabb_1 is not None and aabb_1[1][2] > r.deck_height + 0.55,
            )

    if r.central_frame not in {"wire_base_deck", "industrial_trestle"}:
        ctx.allow_overlap(
            grounded,
            left_wing,
            reason="open wing deck continues the central drying surface",
        )
        ctx.allow_overlap(
            grounded,
            right_wing,
            reason="open wing deck continues the central drying surface",
        )

    if r.lower_support != "none_fixed_base_only" and r.central_frame not in {
        "wire_base_deck",
        "industrial_trestle",
    }:
        lower = object_model.get_part("lower_support")
        ctx.allow_overlap(
            grounded,
            lower,
            elem_a="underside_pivot_cover",
            elem_b="top_rail",
            reason="lower support hinge sits under central pivot cover",
        )
        ctx.allow_overlap(
            grounded,
            lower,
            reason="lower support frame nests against central leg ties",
        )
        ctx.allow_overlap(
            left_wing,
            lower,
            reason="open wings share clearance envelope with folded lower frame",
        )
        ctx.allow_overlap(
            right_wing,
            lower,
            reason="open wings share clearance envelope with folded lower frame",
        )

    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    return ctx.report()


__all__ = [
    "SimpleDryingRackConfig",
    "ResolvedSimpleDryingRackConfig",
    "build_seeded_simple_drying_rack",
    "build_simple_drying_rack",
    "config_from_seed",
    "resolve_config",
    "run_simple_drying_rack_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
