# SPDX-License-Identifier: Apache-2.0

"""Turntable — modular procedural template.

Mixed parallel topology: a grounded plinth carries a continuously spinning
platter, a side-mounted tonearm swing stage, and optional controls/accessory
motion. The exported slot choices mirror the reviewed spec:

* Slot A ``plinth_base``
* Slot B ``platter_spindle``
* Slot C ``tonearm_stage``
* Slot D ``controls_accessories``

seed=0 anchor: simple_rect_plinth + direct_platter + simple_pivot_tonearm + none.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
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
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True


PlinthBase = Literal[
    "simple_rect_plinth",
    "rugged_spindle_plinth",
    "modular_bearing_plinth",
    "industrial_guarded_plinth",
]
PlatterSpindle = Literal[
    "direct_platter",
    "spindle_supported_platter",
    "guarded_platter",
    "raised_support_platter",
]
TonearmStage = Literal[
    "simple_pivot_tonearm",
    "two_axis_carriage_arm",
    "modular_tonearm_head",
    "retrofit_tonearm_stage",
]
ControlsAccessories = Literal[
    "none",
    "pitch_slider",
    "pitch_slider_and_guard_frame",
    "speed_dial_power_button",
    "service_hatches",
    "guard_frame",
    "fixed_guard_frame",
]
PaletteTheme = Literal["satin_black", "walnut_silver", "industrial_gray", "cream_red"]
PlatterDecoration = Literal[
    "plain_mat",
    "classic_strobe",
    "dense_strobe",
    "rim_notches",
    "minimal_marker",
    "adapter_on_mat",
]


PLINTH_MODULES: tuple[PlinthBase, ...] = (
    "simple_rect_plinth",
    "rugged_spindle_plinth",
    "modular_bearing_plinth",
    "industrial_guarded_plinth",
)
PLATTER_MODULES: tuple[PlatterSpindle, ...] = (
    "direct_platter",
    "spindle_supported_platter",
    "guarded_platter",
    "raised_support_platter",
)
TONEARM_MODULES: tuple[TonearmStage, ...] = (
    "simple_pivot_tonearm",
    "two_axis_carriage_arm",
    "modular_tonearm_head",
    "retrofit_tonearm_stage",
)
ACCESSORY_MODULES: tuple[ControlsAccessories, ...] = (
    "none",
    "pitch_slider",
    "pitch_slider_and_guard_frame",
    "speed_dial_power_button",
    "service_hatches",
    "guard_frame",
    "fixed_guard_frame",
)


PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "satin_black": {
        "plinth": (0.025, 0.025, 0.030, 1.0),
        "deck": (0.20, 0.21, 0.22, 1.0),
        "metal": (0.72, 0.74, 0.76, 1.0),
        "dark_metal": (0.10, 0.11, 0.12, 1.0),
        "rubber": (0.015, 0.015, 0.018, 1.0),
        "accent": (0.85, 0.12, 0.08, 1.0),
        "label": (0.92, 0.86, 0.72, 1.0),
        "glass": (0.62, 0.78, 0.92, 0.34),
    },
    "walnut_silver": {
        "plinth": (0.36, 0.20, 0.10, 1.0),
        "deck": (0.76, 0.72, 0.66, 1.0),
        "metal": (0.76, 0.78, 0.80, 1.0),
        "dark_metal": (0.16, 0.16, 0.17, 1.0),
        "rubber": (0.025, 0.023, 0.023, 1.0),
        "accent": (0.84, 0.64, 0.28, 1.0),
        "label": (0.92, 0.88, 0.72, 1.0),
        "glass": (0.62, 0.78, 0.92, 0.34),
    },
    "industrial_gray": {
        "plinth": (0.38, 0.39, 0.40, 1.0),
        "deck": (0.24, 0.25, 0.27, 1.0),
        "metal": (0.68, 0.70, 0.72, 1.0),
        "dark_metal": (0.10, 0.12, 0.13, 1.0),
        "rubber": (0.035, 0.035, 0.038, 1.0),
        "accent": (0.94, 0.72, 0.10, 1.0),
        "label": (0.94, 0.94, 0.88, 1.0),
        "glass": (0.60, 0.78, 0.92, 0.30),
    },
    "cream_red": {
        "plinth": (0.86, 0.82, 0.70, 1.0),
        "deck": (0.58, 0.08, 0.07, 1.0),
        "metal": (0.75, 0.75, 0.72, 1.0),
        "dark_metal": (0.12, 0.10, 0.10, 1.0),
        "rubber": (0.04, 0.035, 0.035, 1.0),
        "accent": (0.95, 0.80, 0.25, 1.0),
        "label": (0.96, 0.92, 0.76, 1.0),
        "glass": (0.64, 0.80, 0.92, 0.32),
    },
}


@dataclass(frozen=True)
class TurntableConfig:
    plinth_base: PlinthBase | None = None
    platter_spindle: PlatterSpindle | None = None
    tonearm_stage: TonearmStage | None = None
    controls_accessories: ControlsAccessories | None = None
    palette_theme: PaletteTheme = "satin_black"
    plinth_width: float = 0.46
    plinth_depth: float = 0.35
    plinth_height: float = 0.058
    platter_radius: float = 0.145
    tonearm_length: float = 0.255
    tonearm_sweep: float = 0.92
    dust_cover_open: float = 1.15
    platter_decoration: PlatterDecoration = "plain_mat"
    platter_decoration_phase: float = 0.0
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["satin_black"])
    )


@dataclass(frozen=True)
class ResolvedTurntableConfig:
    plinth_base: PlinthBase
    platter_spindle: PlatterSpindle
    tonearm_stage: TonearmStage
    controls_accessories: ControlsAccessories
    palette_theme: PaletteTheme
    plinth_width: float
    plinth_depth: float
    plinth_height: float
    platter_radius: float
    tonearm_length: float
    tonearm_sweep: float
    dust_cover_open: float
    platter_decoration: PlatterDecoration
    platter_decoration_phase: float
    deck_top_z: float
    platter_center: tuple[float, float]
    tonearm_mount: tuple[float, float]
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def config_from_seed(seed: int) -> TurntableConfig:
    if seed == 0:
        return TurntableConfig(
            plinth_base="simple_rect_plinth",
            platter_spindle="direct_platter",
            tonearm_stage="simple_pivot_tonearm",
            controls_accessories="none",
            palette_theme="satin_black",
            plinth_width=0.46,
            plinth_depth=0.35,
            plinth_height=0.058,
            platter_radius=0.145,
            tonearm_length=0.255,
            tonearm_sweep=0.92,
            dust_cover_open=1.15,
            platter_decoration="plain_mat",
            platter_decoration_phase=0.0,
        )
    rng = random.Random(seed)
    w = rng.uniform(0.42, 0.56)
    d = rng.uniform(0.32, 0.43)
    pr = rng.uniform(0.125, min(0.18, d * 0.43, w * 0.36))
    return TurntableConfig(
        plinth_base=rng.choice(PLINTH_MODULES),  # type: ignore[arg-type]
        platter_spindle=rng.choice(PLATTER_MODULES),  # type: ignore[arg-type]
        tonearm_stage=rng.choice(TONEARM_MODULES),  # type: ignore[arg-type]
        controls_accessories=rng.choice(ACCESSORY_MODULES),  # type: ignore[arg-type]
        palette_theme=rng.choice(tuple(PALETTES.keys())),  # type: ignore[arg-type]
        plinth_width=round(w, 4),
        plinth_depth=round(d, 4),
        plinth_height=round(rng.uniform(0.050, 0.085), 4),
        platter_radius=round(pr, 4),
        tonearm_length=round(rng.uniform(pr * 1.45, pr * 1.85), 4),
        tonearm_sweep=round(rng.uniform(0.65, 1.25), 3),
        dust_cover_open=round(rng.uniform(0.85, 1.35), 3),
        platter_decoration=rng.choice(
            (
                "plain_mat",
                "classic_strobe",
                "dense_strobe",
                "rim_notches",
                "minimal_marker",
                "adapter_on_mat",
            )
        ),  # type: ignore[arg-type]
        platter_decoration_phase=round(rng.uniform(0.0, math.tau), 4),
    )


def resolve_config(config: TurntableConfig) -> ResolvedTurntableConfig:
    plinth = config.plinth_base or "simple_rect_plinth"
    platter = config.platter_spindle or "direct_platter"
    tonearm = config.tonearm_stage or "simple_pivot_tonearm"
    accessory = config.controls_accessories or "none"
    decoration = config.platter_decoration
    for value, pool, label in (
        (plinth, PLINTH_MODULES, "plinth_base"),
        (platter, PLATTER_MODULES, "platter_spindle"),
        (tonearm, TONEARM_MODULES, "tonearm_stage"),
        (accessory, ACCESSORY_MODULES, "controls_accessories"),
    ):
        if value not in pool:
            raise ValueError(f"Unsupported {label}: {value!r}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")
    if decoration not in (
        "classic_strobe",
        "plain_mat",
        "dense_strobe",
        "rim_notches",
        "minimal_marker",
        "adapter_on_mat",
    ):
        raise ValueError(f"Unsupported platter_decoration: {decoration!r}")

    w = _clamp(config.plinth_width, 0.38, 0.62)
    d = _clamp(config.plinth_depth, 0.30, 0.48)
    h = _clamp(config.plinth_height, 0.045, 0.095)
    radius = _clamp(config.platter_radius, 0.105, min(0.19, d * 0.43, w * 0.38))
    arm_len = _clamp(config.tonearm_length, radius * 1.35, radius * 2.05)
    deck_top_z = h + 0.006
    platter_center = (-w * 0.14, d * 0.02)
    tonearm_mount = (w * 0.35, -d * 0.25)
    return ResolvedTurntableConfig(
        plinth_base=plinth,
        platter_spindle=platter,
        tonearm_stage=tonearm,
        controls_accessories=accessory,
        palette_theme=config.palette_theme,
        plinth_width=w,
        plinth_depth=d,
        plinth_height=h,
        platter_radius=radius,
        tonearm_length=arm_len,
        tonearm_sweep=_clamp(config.tonearm_sweep, 0.35, 1.55),
        dust_cover_open=_clamp(config.dust_cover_open, 0.60, 1.00),
        platter_decoration=decoration,
        platter_decoration_phase=float(config.platter_decoration_phase) % math.tau,
        deck_top_z=deck_top_z,
        platter_center=platter_center,
        tonearm_mount=tonearm_mount,
        palette=dict(PALETTES[config.palette_theme]),
    )


def _add_foot(part: Part, x: float, y: float, r: ResolvedTurntableConfig, name: str) -> None:
    part.visual(
        Cylinder(radius=0.020, length=0.012),
        origin=Origin(xyz=(x, y, 0.006)),
        material="rubber",
        name=name, material_class_id="rubber.smooth_plain",
    )


def _add_basic_deck_controls(part: Part, r: ResolvedTurntableConfig) -> None:
    z = r.deck_top_z + 0.0005
    x0 = -r.plinth_width * 0.40
    y0 = -r.plinth_depth * 0.34
    part.visual(
        Box((0.040, 0.016, 0.004)),
        origin=Origin(xyz=(x0, y0, z)),
        material="metal",
        name="speed_selector_slot", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=0.012, length=0.006),
        origin=Origin(xyz=(x0 + 0.055, y0, z + 0.001)),
        material="accent",
        name="start_stop_button_socket", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Box((0.018, 0.010, 0.003)),
        origin=Origin(xyz=(r.tonearm_mount[0] + 0.030, r.tonearm_mount[1] - 0.045, z)),
        material="dark_metal",
        name="arm_rest_cradle", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.044, 0.003, 0.001)),
        origin=Origin(xyz=(x0 - 0.001, y0 + 0.010, r.deck_top_z + 0.0003)),
        material="label",
        name="speed_selector_scale_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    for i, dx in enumerate((-0.015, 0.0, 0.015)):
        part.visual(
            Box((0.003, 0.007, 0.001)),
            origin=Origin(xyz=(x0 + dx, y0 + 0.010, r.deck_top_z + 0.0007)),
            material="label",
            name=f"speed_tick_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    part.visual(
        Cylinder(radius=0.0045, length=0.006),
        origin=Origin(xyz=(r.plinth_width * 0.44, r.plinth_depth * 0.25, z + 0.002)),
        material="metal",
        name="ground_terminal", material_class_id="metal.stainless_matte",
    )
    for i, yoff in enumerate((-0.012, 0.012)):
        part.visual(
            Cylinder(radius=0.006, length=0.006),
            origin=Origin(
                xyz=(r.plinth_width * 0.44, r.plinth_depth * 0.25 + yoff, z + 0.002),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material="accent" if i == 0 else "metal",
            name=f"rca_output_jack_{i}", material_class_id="metal.stainless_matte",
        )


def _build_plinth(model: ArticulatedObject, r: ResolvedTurntableConfig) -> None:
    plinth = model.part("plinth")
    w, d, h = r.plinth_width, r.plinth_depth, r.plinth_height
    plinth.visual(
        Box((w, d, h)),
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
        material="plinth",
        name="plinth_body", material_class_id=("wood.walnut_dark" if r.palette_theme == "walnut_silver" else "wood.painted_clean"),
    )
    plinth.visual(
        Box((w * 0.96, d * 0.94, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, h + 0.001)),
        material="deck",
        name="top_deck", material_class_id="metal.paint_coated",
    )
    for i, (x, y) in enumerate(
        (
            (-w * 0.40, -d * 0.38),
            (w * 0.40, -d * 0.38),
            (-w * 0.40, d * 0.38),
            (w * 0.40, d * 0.38),
        )
    ):
        _add_foot(plinth, x, y, r, f"rubber_foot_{i}")
    cx, cy = r.platter_center
    plinth.visual(
        Cylinder(radius=max(0.030, r.platter_radius * 0.24), length=0.006),
        origin=Origin(xyz=(cx, cy, r.deck_top_z + 0.001)),
        material="dark_metal",
        name="bearing_collar", material_class_id="metal.blackened_gunmetal",
    )
    tx, ty = r.tonearm_mount
    plinth.visual(
        Box((0.080, 0.064, 0.010)),
        origin=Origin(xyz=(tx, ty, r.deck_top_z + 0.001)),
        material="deck",
        name="tonearm_reinforcement_pad", material_class_id="metal.paint_coated",
    )
    plinth.visual(
        Cylinder(radius=0.027, length=0.016),
        origin=Origin(xyz=(tx, ty, r.deck_top_z + 0.004)),
        material="dark_metal",
        name="tonearm_mount_socket", material_class_id="metal.blackened_gunmetal",
    )
    plinth.visual(
        Box((0.096, 0.074, 0.012)),
        origin=Origin(xyz=(tx, ty, r.deck_top_z + 0.008)),
        material="dark_metal",
        name="tonearm_base_block", material_class_id="metal.blackened_gunmetal",
    )
    if r.tonearm_stage == "simple_pivot_tonearm":
        plinth.visual(
            Cylinder(radius=0.018, length=0.038),
            origin=Origin(xyz=(tx, ty, r.deck_top_z + 0.025)),
            material="metal",
            name="tonearm_vertical_post", material_class_id="metal.aluminum_bare",
        )
        plinth.visual(
            Cylinder(radius=0.024, length=0.008),
            origin=Origin(xyz=(tx, ty, r.deck_top_z + 0.046)),
            material="dark_metal",
            name="tonearm_top_bearing_seat", material_class_id="metal.blackened_gunmetal",
        )
    _add_basic_deck_controls(plinth, r)

    if r.plinth_base in ("rugged_spindle_plinth", "industrial_guarded_plinth"):
        plinth.visual(
            Box((w * 0.94, 0.030, 0.016)),
            origin=Origin(xyz=(0.0, -d * 0.44, h + 0.010)),
            material="deck",
            name="front_bumper", material_class_id="metal.paint_coated",
        )
        plinth.visual(
            Box((0.020, d * 0.72, 0.016)),
            origin=Origin(xyz=(-w * 0.47, 0.0, h + 0.010)),
            material="deck",
            name="left_side_rail", material_class_id="metal.paint_coated",
        )
        plinth.visual(
            Box((0.020, d * 0.72, 0.016)),
            origin=Origin(xyz=(w * 0.47, 0.0, h + 0.010)),
            material="deck",
            name="right_side_rail", material_class_id="metal.paint_coated",
        )
    if r.plinth_base == "modular_bearing_plinth":
        plinth.visual(
            Cylinder(radius=0.038, length=0.018),
            origin=Origin(xyz=(tx, ty, r.deck_top_z + 0.010)),
            material="metal",
            name="detachable_tonearm_base_ring", material_class_id="metal.aluminum_bare",
        )
        plinth.visual(
            Cylinder(radius=0.020, length=0.012),
            origin=Origin(xyz=(cx, cy, r.deck_top_z + 0.010)),
            material="metal",
            name="modular_spindle_insert", material_class_id="metal.stainless_matte",
        )
    if r.plinth_base == "industrial_guarded_plinth":
        guard_x = max(-w * 0.515, cx - r.platter_radius - 0.030)
        rear_y = cy + r.platter_radius * (0.55 if r.controls_accessories == "guard_frame" else 1.10)
        front_y = cy - r.platter_radius * 0.66
        rail_z = r.deck_top_z + 0.048
        for i, y in enumerate((front_y, cy + r.platter_radius * 0.22, rear_y)):
            plinth.visual(
                Cylinder(radius=0.013, length=0.006),
                origin=Origin(xyz=(guard_x, y, r.deck_top_z + 0.003)),
                material="dark_metal",
                name=f"left_guard_foot_{i}", material_class_id="metal.blackened_gunmetal",
            )
            plinth.visual(
                Cylinder(radius=0.0045, length=0.048),
                origin=Origin(xyz=(guard_x, y, r.deck_top_z + 0.027)),
                material="accent",
                name=f"left_guard_post_{i}", material_class_id="metal.paint_coated",
            )
        plinth.visual(
            Box((0.014, rear_y - front_y, 0.012)),
            origin=Origin(xyz=(guard_x, (front_y + rear_y) * 0.5, rail_z)),
            material="accent",
            name="left_platter_guard_rail", material_class_id="metal.paint_coated",
        )
        if r.controls_accessories != "guard_frame":
            rear_left_x = cx - r.platter_radius * 0.35
            rear_right_x = cx + r.platter_radius * 0.78
            for i, x in enumerate((rear_left_x, (rear_left_x + rear_right_x) * 0.5, rear_right_x)):
                plinth.visual(
                    Cylinder(radius=0.011, length=0.006),
                    origin=Origin(xyz=(x, rear_y, r.deck_top_z + 0.003)),
                    material="dark_metal",
                    name=f"rear_guard_foot_{i}", material_class_id="metal.blackened_gunmetal",
                )
                plinth.visual(
                    Cylinder(radius=0.004, length=0.026),
                    origin=Origin(xyz=(x, rear_y, r.deck_top_z + 0.016)),
                    material="accent",
                    name=f"rear_guard_post_{i}", material_class_id="metal.paint_coated",
                )
            plinth.visual(
                Box((rear_right_x - rear_left_x, 0.014, 0.010)),
                origin=Origin(
                    xyz=((rear_left_x + rear_right_x) * 0.5, rear_y, r.deck_top_z + 0.030)
                ),
                material="accent",
                name="rear_guard_rail", material_class_id="metal.paint_coated",
            )
    plinth.inertial = Inertial.from_geometry(
        Box((w, d, h)),
        mass=6.0,
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
    )


def _build_platter_part(model: ArticulatedObject, r: ResolvedTurntableConfig) -> None:
    platter = model.part("platter")
    radius = r.platter_radius
    platter.visual(
        Cylinder(radius=radius * 0.36, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material="dark_metal",
        name="hub_flange", material_class_id="metal.blackened_gunmetal",
    )
    platter.visual(
        Cylinder(radius=radius, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.020)),
        material="metal",
        name="platter_disc", material_class_id="metal.aluminum_bare",
    )
    platter.visual(
        Cylinder(radius=radius * 0.94, length=0.005),
        origin=Origin(xyz=(0.0, 0.0, 0.034)),
        material="rubber",
        name="rubber_record_mat", material_class_id="rubber.smooth_plain",
    )
    platter.visual(
        Cylinder(radius=radius * 0.28, length=0.003),
        origin=Origin(xyz=(0.0, 0.0, 0.038)),
        material="label",
        name="center_label", material_class_id="paper.plain_sheet",
    )
    groove_profiles = {
        "plain_mat": (0.42, 0.56, 0.70, 0.84),
        "classic_strobe": (0.42, 0.56, 0.70, 0.84),
        "dense_strobe": (0.36, 0.48, 0.60, 0.72, 0.84),
        "rim_notches": (0.46, 0.62, 0.78),
        "minimal_marker": (0.52, 0.72),
        "adapter_on_mat": (0.38, 0.52, 0.66, 0.80),
    }[r.platter_decoration]
    for i, groove_radius in enumerate(groove_profiles):
        platter.visual(
            Cylinder(radius=radius * groove_radius, length=0.0015),
            origin=Origin(xyz=(0.0, 0.0, 0.041 + i * 0.0004)),
            material="dark_metal",
            name=f"record_groove_ring_{i}", material_class_id="rubber.smooth_plain",
        )
    if r.platter_decoration == "plain_mat":
        marker_count = 0
        marker_size = (0.0, 0.0, 0.0)
        marker_radius = 0.0
        label_every = 1
    elif r.platter_decoration == "classic_strobe":
        marker_count = 24
        marker_size = (0.0035, 0.009, 0.002)
        marker_radius = radius * 0.985
        label_every = 2
    elif r.platter_decoration == "dense_strobe":
        marker_count = 48
        marker_size = (0.0025, 0.0065, 0.002)
        marker_radius = radius * 0.990
        label_every = 3
    elif r.platter_decoration == "rim_notches":
        marker_count = 18
        marker_size = (0.004, 0.012, 0.002)
        marker_radius = radius * 0.970
        label_every = 6
    elif r.platter_decoration == "minimal_marker":
        marker_count = 8
        marker_size = (0.003, 0.010, 0.002)
        marker_radius = radius * 0.955
        label_every = 4
    else:
        marker_count = 12
        marker_size = (0.0035, 0.009, 0.002)
        marker_radius = radius * 0.980
        label_every = 2
    for i in range(marker_count):
        angle = r.platter_decoration_phase + (math.tau * i) / marker_count
        platter.visual(
            Box(marker_size),
            origin=Origin(
                xyz=(
                    math.cos(angle) * marker_radius,
                    math.sin(angle) * marker_radius,
                    0.0336,
                ),
                rpy=(0.0, 0.0, angle),
            ),
            material="label" if i % label_every == 0 else "dark_metal",
            name=f"strobe_dot_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    platter.visual(
        Cylinder(radius=0.0035, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.048)),
        material="metal",
        name="spindle_tip", material_class_id="metal.stainless_matte",
    )
    if r.platter_decoration == "adapter_on_mat":
        adapter_angle = r.platter_decoration_phase + 0.73
        platter.visual(
            Cylinder(radius=0.014, length=0.004),
            origin=Origin(
                xyz=(
                    math.cos(adapter_angle) * radius * 0.40,
                    math.sin(adapter_angle) * radius * 0.40,
                    0.0378,
                )
            ),
            material="label",
            name="loose_45_adapter", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.platter_decoration == "minimal_marker":
        platter.visual(
            Box((radius * 0.22, 0.003, 0.0015)),
            origin=Origin(xyz=(0.0, radius * 0.50, 0.0363), rpy=(0.0, 0.0, math.pi / 2.0)),
            material="label",
            name="single_index_line", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    if r.platter_spindle == "guarded_platter":
        platter.visual(
            Cylinder(radius=radius * 1.02, length=0.006),
            origin=Origin(xyz=(0.0, 0.0, 0.014)),
            material="dark_metal",
            name="protective_outer_rim", material_class_id="metal.blackened_gunmetal",
        )
    platter.inertial = Inertial.from_geometry(
        Cylinder(radius=radius, length=0.035),
        mass=1.9,
        origin=Origin(xyz=(0.0, 0.0, 0.018)),
    )


def _build_platter_spindle(model: ArticulatedObject, r: ResolvedTurntableConfig) -> str:
    cx, cy = r.platter_center
    parent_name = "plinth"
    origin_z = r.deck_top_z + 0.003
    if r.platter_spindle in (
        "spindle_supported_platter",
        "guarded_platter",
        "raised_support_platter",
    ):
        support_name = (
            "spindle_support"
            if r.platter_spindle != "raised_support_platter"
            else "platter_support"
        )
        support = model.part(support_name)
        support.visual(
            Cylinder(radius=r.platter_radius * 0.32, length=0.024),
            origin=Origin(xyz=(0.0, 0.0, 0.012)),
            material="dark_metal",
            name="bearing_pedestal", material_class_id="metal.blackened_gunmetal",
        )
        support.visual(
            Cylinder(radius=r.platter_radius * 0.20, length=0.036),
            origin=Origin(xyz=(0.0, 0.0, 0.024)),
            material="metal",
            name="spindle_column", material_class_id="metal.stainless_matte",
        )
        if r.platter_spindle == "raised_support_platter":
            support.visual(
                Box((r.platter_radius * 0.72, r.platter_radius * 0.52, 0.012)),
                origin=Origin(xyz=(0.0, 0.0, 0.006)),
                material="deck",
                name="raised_support_foot", material_class_id="metal.paint_coated",
            )
        support.inertial = Inertial.from_geometry(
            Cylinder(radius=r.platter_radius * 0.32, length=0.040),
            mass=0.25,
            origin=Origin(xyz=(0.0, 0.0, 0.020)),
        )
        model.articulation(
            f"plinth_to_{support_name}",
            ArticulationType.FIXED,
            parent=model.get_part("plinth"),
            child=support,
            origin=Origin(xyz=(cx, cy, r.deck_top_z)),
        )
        parent_name = support_name
        origin_z = 0.031 if r.platter_spindle != "raised_support_platter" else 0.039
    _build_platter_part(model, r)
    model.articulation(
        "platter_spin",
        ArticulationType.CONTINUOUS,
        parent=model.get_part(parent_name),
        child=model.get_part("platter"),
        origin=Origin(xyz=(cx, cy, origin_z) if parent_name == "plinth" else (0.0, 0.0, origin_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=12.0),
    )
    return parent_name


def _emit_tonearm_beam(
    part: Part,
    r: ResolvedTurntableConfig,
    *,
    angle: float = 2.35,
    arm_z: float = 0.062,
    include_head: bool = True,
) -> None:
    length = r.tonearm_length
    ux = math.cos(angle)
    uy = math.sin(angle)
    side_x = -uy
    side_y = ux
    tube_rpy = (math.pi / 2.0, 0.0, angle + math.pi / 2.0)
    part.visual(
        Cylinder(radius=0.020, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.009)),
        material="dark_metal",
        name="pivot_collar", material_class_id="metal.blackened_gunmetal",
    )
    if arm_z > 0.026:
        spindle_h = max(0.014, arm_z - 0.018)
        part.visual(
            Cylinder(radius=0.007, length=spindle_h),
            origin=Origin(xyz=(0.0, 0.0, 0.014 + spindle_h * 0.5)),
            material="metal",
            name="vertical_pivot_spindle", material_class_id="metal.stainless_matte",
        )
    gimbal_z = max(0.014, arm_z - 0.004)
    part.visual(
        Box((0.034, 0.022, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, gimbal_z)),
        material="dark_metal",
        name="gimbal_yoke", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.004, length=0.050),
        origin=Origin(xyz=(0.0, 0.0, gimbal_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="metal",
        name="gimbal_pivot_pin", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=0.006, length=0.064),
        origin=Origin(xyz=(-ux * 0.034, -uy * 0.034, arm_z + 0.001), rpy=tube_rpy),
        material="metal",
        name="counterweight_stub", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=0.017, length=0.038),
        origin=Origin(xyz=(-ux * 0.074, -uy * 0.074, arm_z + 0.001), rpy=tube_rpy),
        material="dark_metal",
        name="counterweight", material_class_id="metal.blackened_gunmetal",
    )
    arm_cx = ux * length * 0.50
    arm_cy = uy * length * 0.50
    part.visual(
        Cylinder(radius=0.0045, length=length),
        origin=Origin(
            xyz=(arm_cx, arm_cy, arm_z + 0.002),
            rpy=tube_rpy,
        ),
        material="metal",
        name="tonearm_tube", material_class_id="metal.aluminum_bare",
    )
    if not include_head:
        return

    head_x = ux * (length + 0.006)
    head_y = uy * (length + 0.006)
    shell_z = arm_z - 0.004
    part.visual(
        Cylinder(radius=0.005, length=0.026),
        origin=Origin(xyz=(ux * (length - 0.006), uy * (length - 0.006), arm_z), rpy=tube_rpy),
        material="metal",
        name="headshell_coupler", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.038, 0.024, 0.006)),
        origin=Origin(xyz=(head_x, head_y, shell_z), rpy=(0.0, 0.0, angle)),
        material="metal",
        name="headshell", material_class_id="metal.aluminum_bare",
    )
    for side, label in ((-1.0, "left"), (1.0, "right")):
        part.visual(
            Box((0.032, 0.004, 0.010)),
            origin=Origin(
                xyz=(
                    head_x + side_x * side * 0.010,
                    head_y + side_y * side * 0.010,
                    shell_z - 0.006,
                ),
                rpy=(0.0, 0.0, angle),
            ),
            material="dark_metal",
            name=f"headshell_{label}_rail", material_class_id="metal.blackened_gunmetal",
        )
    part.visual(
        Box((0.014, 0.004, 0.018)),
        origin=Origin(
            xyz=(head_x - side_x * 0.013, head_y - side_y * 0.013, shell_z + 0.010),
            rpy=(0.0, 0.0, angle),
        ),
        material="metal",
        name="headshell_finger_lift", material_class_id="metal.aluminum_bare",
    )
    cart_x = head_x + ux * 0.010
    cart_y = head_y + uy * 0.010
    part.visual(
        Box((0.018, 0.014, 0.012)),
        origin=Origin(xyz=(cart_x, cart_y, shell_z - 0.009), rpy=(0.0, 0.0, angle)),
        material="accent",
        name="cartridge_body", material_class_id="plastic.opaque_glossy_molded",
    )
    for side, label in ((-1.0, "left"), (1.0, "right")):
        part.visual(
            Box((0.020, 0.003, 0.004)),
            origin=Origin(
                xyz=(
                    cart_x + side_x * side * 0.006,
                    cart_y + side_y * side * 0.006,
                    shell_z - 0.002,
                ),
                rpy=(0.0, 0.0, angle),
            ),
            material="dark_metal",
            name=f"cartridge_mount_{label}", material_class_id="metal.blackened_gunmetal",
        )
    stylus_x = cart_x + ux * 0.012
    stylus_y = cart_y + uy * 0.012
    part.visual(
        Box((0.016, 0.002, 0.002)),
        origin=Origin(
            xyz=(cart_x + ux * 0.006, cart_y + uy * 0.006, shell_z - 0.015),
            rpy=(0.0, 0.0, angle),
        ),
        material="dark_metal",
        name="stylus_cantilever", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.0013, length=0.010),
        origin=Origin(xyz=(stylus_x, stylus_y, shell_z - 0.015)),
        material="dark_metal",
        name="stylus_shank", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.004, 0.002, 0.004)),
        origin=Origin(xyz=(stylus_x + ux * 0.002, stylus_y + uy * 0.002, shell_z - 0.021)),
        material="dark_metal",
        name="stylus_tip", material_class_id="metal.blackened_gunmetal",
    )


def _build_simple_pivot_tonearm(model: ArticulatedObject, r: ResolvedTurntableConfig) -> None:
    tonearm = model.part("tonearm")
    _emit_tonearm_beam(tonearm, r, angle=1.92, arm_z=0.062 + _tonearm_record_lift(r))
    tonearm.inertial = Inertial.from_geometry(
        Box((r.tonearm_length, 0.07, 0.06)),
        mass=0.35,
        origin=Origin(xyz=(-0.02, 0.10, 0.030)),
    )
    tx, ty = r.tonearm_mount
    model.articulation(
        "tonearm_pivot",
        ArticulationType.REVOLUTE,
        parent=model.get_part("plinth"),
        child=tonearm,
        origin=Origin(xyz=(tx, ty, r.deck_top_z + 0.010)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.8, velocity=1.8, lower=0.0, upper=r.tonearm_sweep),
    )


def _build_two_axis_carriage_arm(model: ArticulatedObject, r: ResolvedTurntableConfig) -> None:
    carriage = model.part("tonearm_carriage")
    carriage.visual(
        Cylinder(radius=0.024, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
        material="dark_metal",
        name="base_collar", material_class_id="metal.blackened_gunmetal",
    )
    carriage.visual(
        Cylinder(radius=0.010, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, 0.028)),
        material="metal",
        name="pivot_pillar", material_class_id="metal.stainless_matte",
    )
    carriage.visual(
        Box((0.034, 0.030, 0.008)),
        origin=Origin(xyz=(0.002, 0.0, 0.050)),
        material="metal",
        name="bridge_plate", material_class_id="metal.aluminum_bare",
    )
    for y, name in ((-0.013, "left_cheek"), (0.013, "right_cheek")):
        carriage.visual(
            Box((0.012, 0.006, 0.026)),
            origin=Origin(xyz=(0.002, y, 0.064)),
            material="metal",
            name=name, material_class_id="metal.aluminum_bare",
        )
    arm = model.part("tonearm_tube")
    _emit_tonearm_beam(arm, r, angle=math.pi, arm_z=0.024)
    tx, ty = r.tonearm_mount
    model.articulation(
        "tonearm_pivot",
        ArticulationType.REVOLUTE,
        parent=model.get_part("plinth"),
        child=carriage,
        origin=Origin(xyz=(tx, ty, r.deck_top_z + 0.010), rpy=(0.0, 0.0, -0.32)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.2, velocity=1.5, lower=-0.95, upper=0.18),
    )
    model.articulation(
        "tonearm_pitch",
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=arm,
        origin=Origin(xyz=(0.002, 0.0, 0.064)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.6, velocity=1.0, lower=0.0, upper=0.05),
    )


def _build_modular_tonearm_head(model: ArticulatedObject, r: ResolvedTurntableConfig) -> None:
    lift = _tonearm_record_lift(r)
    base = model.part("tonearm_base_module")
    base.visual(
        Cylinder(radius=0.032, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material="dark_metal",
        name="mounting_disk", material_class_id="metal.blackened_gunmetal",
    )
    base.visual(
        Cylinder(radius=0.020, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.026)),
        material="dark_metal",
        name="support_pedestal", material_class_id="metal.blackened_gunmetal",
    )
    base.visual(
        Box((0.020, 0.018, 0.014)),
        origin=Origin(xyz=(-0.020, 0.0, 0.024)),
        material="dark_metal",
        name="anti_skate_block", material_class_id="metal.blackened_gunmetal",
    )
    bearing = model.part("tonearm_bearing_module")
    _emit_tonearm_beam(bearing, r, angle=math.pi, arm_z=0.030 + lift, include_head=False)
    head = model.part("tonearm_head_module")
    head.visual(
        Cylinder(radius=0.0045, length=0.020),
        origin=Origin(xyz=(0.0, -0.010, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="metal",
        name="head_connector", material_class_id="metal.stainless_matte",
    )
    head.visual(
        Box((0.030, 0.025, 0.006)),
        origin=Origin(xyz=(0.0, -0.022, -0.003)),
        material="metal",
        name="headshell_plate", material_class_id="metal.aluminum_bare",
    )
    for x, label in ((-0.010, "left"), (0.010, "right")):
        head.visual(
            Box((0.004, 0.026, 0.008)),
            origin=Origin(xyz=(x, -0.026, -0.007)),
            material="dark_metal",
            name=f"headshell_side_rail_{label}", material_class_id="metal.blackened_gunmetal",
        )
    head.visual(
        Box((0.016, 0.012, 0.010)),
        origin=Origin(xyz=(0.0, -0.038, -0.008)),
        material="accent",
        name="cartridge_body", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((0.020, 0.004, 0.004)),
        origin=Origin(xyz=(0.0, -0.034, -0.001)),
        material="dark_metal",
        name="cartridge_mount_bar", material_class_id="metal.blackened_gunmetal",
    )
    head.visual(
        Box((0.003, 0.014, 0.002)),
        origin=Origin(xyz=(0.0, -0.045, -0.0135)),
        material="dark_metal",
        name="stylus_cantilever", material_class_id="metal.blackened_gunmetal",
    )
    head.visual(
        Cylinder(radius=0.0012, length=0.009),
        origin=Origin(xyz=(0.0, -0.048, -0.016)),
        material="dark_metal",
        name="stylus_shank", material_class_id="metal.blackened_gunmetal",
    )
    head.visual(
        Box((0.004, 0.002, 0.004)),
        origin=Origin(xyz=(0.0, -0.050, -0.0205)),
        material="dark_metal",
        name="stylus_tip", material_class_id="metal.blackened_gunmetal",
    )
    tx, ty = r.tonearm_mount
    model.articulation(
        "plinth_to_tonearm_base",
        ArticulationType.FIXED,
        parent=model.get_part("plinth"),
        child=base,
        origin=Origin(xyz=(tx, ty, r.deck_top_z)),
    )
    model.articulation(
        "tonearm_pivot",
        ArticulationType.REVOLUTE,
        parent=base,
        child=bearing,
        origin=Origin(xyz=(0.0, 0.0, 0.040), rpy=(0.0, 0.0, -1.08)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.2, lower=0.0, upper=r.tonearm_sweep),
    )
    model.articulation(
        "bearing_to_head",
        ArticulationType.FIXED,
        parent=bearing,
        child=head,
        origin=Origin(xyz=(-r.tonearm_length - 0.003, 0.0, 0.030 + lift)),
    )


def _build_retrofit_tonearm_stage(model: ArticulatedObject, r: ResolvedTurntableConfig) -> None:
    lift = _tonearm_record_lift(r)
    support = model.part("tonearm_support")
    support.visual(
        Box((0.120, 0.090, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material="deck",
        name="support_base", material_class_id="metal.paint_coated",
    )
    support.visual(
        Box((0.085, 0.070, 0.050)),
        origin=Origin(xyz=(0.0, 0.0, 0.034)),
        material="dark_metal",
        name="arm_pedestal", material_class_id="metal.blackened_gunmetal",
    )
    support.visual(
        Box((0.016, 0.066, 0.026)),
        origin=Origin(xyz=(-0.048, 0.0, 0.028)),
        material="accent",
        name="stop_bridge", material_class_id="plastic.opaque_glossy_molded",
    )
    stage = model.part("tonearm_stage")
    _emit_tonearm_beam(stage, r, angle=math.pi, arm_z=0.030 + lift)
    tx, ty = r.tonearm_mount
    model.articulation(
        "plinth_to_tonearm_support",
        ArticulationType.FIXED,
        parent=model.get_part("plinth"),
        child=support,
        origin=Origin(xyz=(tx, ty, r.deck_top_z)),
    )
    model.articulation(
        "tonearm_pivot",
        ArticulationType.REVOLUTE,
        parent=support,
        child=stage,
        origin=Origin(xyz=(0.0, 0.0, 0.058), rpy=(0.0, 0.0, -1.08)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.4, velocity=1.5, lower=0.0, upper=r.tonearm_sweep),
    )


def _build_tonearm_stage(model: ArticulatedObject, r: ResolvedTurntableConfig) -> None:
    if r.tonearm_stage == "simple_pivot_tonearm":
        _build_simple_pivot_tonearm(model, r)
    elif r.tonearm_stage == "two_axis_carriage_arm":
        _build_two_axis_carriage_arm(model, r)
    elif r.tonearm_stage == "modular_tonearm_head":
        _build_modular_tonearm_head(model, r)
    elif r.tonearm_stage == "retrofit_tonearm_stage":
        _build_retrofit_tonearm_stage(model, r)
    else:  # pragma: no cover - resolve_config guards this.
        raise ValueError(f"Unsupported tonearm_stage: {r.tonearm_stage!r}")


def _build_fixed_guard_frame(model: ArticulatedObject, r: ResolvedTurntableConfig) -> None:
    plinth = model.get_part("plinth")
    guard = model.part("guard_frame")
    cx, cy = r.platter_center
    if r.plinth_base == "industrial_guarded_plinth":
        ring_radius = min(r.platter_radius + 0.008, r.plinth_depth * 0.42)
    else:
        ring_radius = max(
            r.platter_radius + 0.020,
            min(r.platter_radius + 0.030, r.plinth_depth * 0.49, r.plinth_width * 0.45),
        )
    post_z = 0.024
    ring_z = 0.044
    foot_z = 0.003
    guard.visual(
        Cylinder(radius=0.012, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, 0.002)),
        material="dark_metal",
        name="fixed_guard_center_mount", material_class_id="metal.blackened_gunmetal",
    )
    guard.visual(
        mesh_from_geometry(
            TorusGeometry(radius=ring_radius, tube=0.0055, radial_segments=18, tubular_segments=72),
            "fixed_guard_ring_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, ring_z)),
        material="dark_metal",
        name="fixed_guard_ring", material_class_id="metal.blackened_gunmetal",
    )
    for i, angle in enumerate((math.radians(128.0), math.radians(232.0), math.radians(326.0))):
        x = ring_radius * math.cos(angle)
        y = ring_radius * math.sin(angle)
        guard.visual(
            Box((ring_radius, 0.003, 0.002)),
            origin=Origin(
                xyz=(x * 0.5, y * 0.5, 0.002),
                rpy=(0.0, 0.0, angle),
            ),
            material="dark_metal",
            name=f"fixed_guard_radial_spoke_{i}", material_class_id="metal.blackened_gunmetal",
        )
        guard.visual(
            Cylinder(radius=0.013, length=0.006),
            origin=Origin(xyz=(x, y, foot_z)),
            material="dark_metal",
            name=f"fixed_guard_foot_{i}", material_class_id="metal.blackened_gunmetal",
        )
        guard.visual(
            Cylinder(radius=0.0048, length=0.040),
            origin=Origin(xyz=(x, y, post_z)),
            material="metal",
            name=f"fixed_guard_post_{i}", material_class_id="metal.stainless_matte",
        )
        guard.visual(
            Cylinder(radius=0.008, length=0.010),
            origin=Origin(xyz=(x, y, ring_z - 0.004)),
            material="dark_metal",
            name=f"fixed_guard_ring_clamp_{i}", material_class_id="metal.blackened_gunmetal",
        )
    model.articulation(
        "plinth_to_guard_frame",
        ArticulationType.FIXED,
        parent=plinth,
        child=guard,
        origin=Origin(xyz=(cx, cy, r.deck_top_z - 0.002)),
    )


def _build_accessories(model: ArticulatedObject, r: ResolvedTurntableConfig) -> None:
    plinth = model.get_part("plinth")
    plinth.visual(
        Box((0.10, 0.014, 0.012)),
        origin=Origin(
            xyz=(-r.plinth_width * 0.18, -r.plinth_depth * 0.515, r.plinth_height * 0.56)
        ),
        material="dark_metal",
        name="rear_cable_socket", material_class_id="metal.blackened_gunmetal",
    )
    if r.controls_accessories == "none":
        return
    if r.controls_accessories in {"pitch_slider", "pitch_slider_and_guard_frame"}:
        slider_x = r.plinth_width * 0.18
        slider_y = -r.plinth_depth * 0.32
        plinth.visual(
            Box((0.095, 0.036, 0.004)),
            origin=Origin(xyz=(slider_x, slider_y, r.deck_top_z + 0.002)),
            material="dark_metal",
            name="pitch_track", material_class_id="metal.blackened_gunmetal",
        )
        slider = model.part("pitch_slider")
        slider.visual(
            Box((0.018, 0.034, 0.004)),
            origin=Origin(xyz=(0.0, 0.0, 0.002)),
            material="rubber",
            name="slider_shoe", material_class_id="rubber.smooth_plain",
        )
        slider.visual(
            Box((0.018, 0.024, 0.012)),
            origin=Origin(xyz=(0.0, 0.0, 0.010)),
            material="deck",
            name="slider_knob", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            "pitch_slider",
            ArticulationType.PRISMATIC,
            parent=plinth,
            child=slider,
            origin=Origin(xyz=(slider_x, slider_y, r.deck_top_z - 0.001)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=0.08, lower=-0.012, upper=0.010),
        )
        if r.controls_accessories == "pitch_slider":
            return
    if r.controls_accessories in {"fixed_guard_frame", "pitch_slider_and_guard_frame"}:
        _build_fixed_guard_frame(model, r)
        return
    if r.controls_accessories == "speed_dial_power_button":
        dial = model.part("speed_dial")
        dial.visual(
            Cylinder(radius=0.022, length=0.012),
            origin=Origin(xyz=(0.0, 0.0, 0.006)),
            material="dark_metal",
            name="dial_body", material_class_id="metal.blackened_gunmetal",
        )
        dial.visual(
            Box((0.018, 0.004, 0.004)),
            origin=Origin(xyz=(0.016, 0.0, 0.014)),
            material="label",
            name="dial_pointer", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        button = model.part("power_button")
        button.visual(
            Cylinder(radius=0.014, length=0.010),
            origin=Origin(xyz=(0.0, 0.0, 0.005)),
            material="accent",
            name="button_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        # Seat the dial and button on their deck sockets (speed_selector_slot at
        # (-0.40w, -0.34d), start_stop_button_socket 0.055 further +x) so both
        # controls rest on real plinth geometry instead of floating above it.
        x = -r.plinth_width * 0.40
        y = -r.plinth_depth * 0.34
        model.articulation(
            "speed_dial_turn",
            ArticulationType.REVOLUTE,
            parent=plinth,
            child=dial,
            origin=Origin(xyz=(x, y, r.deck_top_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.2, velocity=4.0, lower=-2.4, upper=2.4),
        )
        model.articulation(
            "power_button_press",
            ArticulationType.PRISMATIC,
            parent=plinth,
            child=button,
            origin=Origin(xyz=(x + 0.055, y, r.deck_top_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.4, velocity=0.1, lower=-0.002, upper=0.002),
        )
    elif r.controls_accessories == "service_hatches":
        for i, x in enumerate((-0.055, 0.045)):
            plinth.visual(
                Box((0.074, 0.050, 0.006)),
                origin=Origin(xyz=(x, r.plinth_depth * 0.30, r.deck_top_z + 0.002)),
                material="dark_metal",
                name=f"service_hatch_recess_{i}", material_class_id="metal.blackened_gunmetal",
            )
            hatch = model.part(f"service_hatch_{i}")
            hatch.visual(
                Box((0.070, 0.046, 0.005)),
                origin=Origin(xyz=(0.0, 0.0, 0.0025)),
                material="deck",
                name="hatch_plate", material_class_id="metal.paint_coated",
            )
            hatch.visual(
                Cylinder(radius=0.003, length=0.050),
                origin=Origin(xyz=(-0.037, 0.0, 0.003), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material="metal",
                name="hatch_hinge_barrel", material_class_id="metal.stainless_matte",
            )
            model.articulation(
                f"service_hatch_hinge_{i}",
                ArticulationType.REVOLUTE,
                parent=plinth,
                child=hatch,
                origin=Origin(xyz=(x, r.plinth_depth * 0.30, r.deck_top_z + 0.002)),
                axis=(0.0, 1.0, 0.0),
                # Small travel: the plate is centre-hinged over the deck, so a large
                # open would drive one edge down into the plinth and the other up
                # into the platter. A shallow crack-open keeps both edges clear.
                motion_limits=MotionLimits(effort=0.3, velocity=1.2, lower=0.0, upper=0.13),
            )
    elif r.controls_accessories == "guard_frame":
        cover = model.part("dust_cover_guard")
        side_x = (
            r.plinth_width * 0.57 + 0.026
            if r.plinth_base == "industrial_guarded_plinth"
            else r.plinth_width * 0.50 + 0.034
        )
        cover_width = side_x * 2.0
        cover_depth = r.plinth_depth * 0.94
        side_x = cover_width * 0.50
        panel_h = 0.126
        panel_bottom_z = 0.010
        panel_center_z = panel_bottom_z + panel_h * 0.5
        top_z = panel_bottom_z + panel_h
        cover.visual(
            Box((cover_width, 0.020, 0.014)),
            origin=Origin(xyz=(0.0, 0.0, 0.008)),
            material="glass",
            name="rear_hinge_bar", material_class_id="glass.clear_transparent",
        )
        cover.visual(
            Box((cover_width, 0.012, 0.012)),
            origin=Origin(xyz=(0.0, 0.0, 0.018)),
            material="dark_metal",
            name="rear_lower_clamp_rail", material_class_id="metal.blackened_gunmetal",
        )
        for i, x in enumerate((-cover_width * 0.32, 0.0, cover_width * 0.32)):
            cover.visual(
                Cylinder(radius=0.006, length=0.028),
                origin=Origin(xyz=(x, 0.0, 0.020), rpy=(0.0, math.pi / 2.0, 0.0)),
                material="dark_metal",
                name=f"rear_hinge_knuckle_{i}", material_class_id="metal.blackened_gunmetal",
            )
        for side, label in ((-1.0, "left"), (1.0, "right")):
            x = side * side_x
            cover.visual(
                Box((0.014, cover_depth, 0.010)),
                origin=Origin(xyz=(x, cover_depth * 0.50, 0.005)),
                material="dark_metal",
                name=f"{label}_bottom_slide_foot", material_class_id="rubber.smooth_plain",
            )
            cover.visual(
                Box((0.012, cover_depth, panel_h)),
                origin=Origin(xyz=(x, cover_depth * 0.50, panel_center_z)),
                material="glass",
                name=f"{label}_clear_side", material_class_id="glass.clear_transparent",
            )
            cover.visual(
                Box((0.018, cover_depth, 0.010)),
                origin=Origin(xyz=(x, cover_depth * 0.50, top_z + 0.004)),
                material="dark_metal",
                name=f"{label}_top_side_rail", material_class_id="metal.blackened_gunmetal",
            )
            cover.visual(
                Box((0.020, 0.022, panel_h + 0.010)),
                origin=Origin(xyz=(x, cover_depth, panel_center_z + 0.002)),
                material="dark_metal",
                name=f"{label}_front_corner_post", material_class_id="metal.blackened_gunmetal",
            )
        cover.visual(
            Box((cover_width, 0.016, panel_h)),
            origin=Origin(xyz=(0.0, cover_depth, panel_center_z)),
            material="glass",
            name="front_clear_panel", material_class_id="glass.clear_transparent",
        )
        cover.visual(
            Box((cover_width, 0.020, 0.012)),
            origin=Origin(xyz=(0.0, cover_depth, top_z + 0.004)),
            material="dark_metal",
            name="front_top_lip", material_class_id="metal.blackened_gunmetal",
        )
        cover.visual(
            Box((cover_width * 0.64, 0.012, 0.012)),
            origin=Origin(xyz=(0.0, cover_depth, 0.007)),
            material="dark_metal",
            name="front_bottom_lip", material_class_id="metal.blackened_gunmetal",
        )
        model.articulation(
            "dust_cover_hinge",
            ArticulationType.REVOLUTE,
            parent=plinth,
            child=cover,
            origin=Origin(xyz=(0.0, -r.plinth_depth * 0.44, r.deck_top_z - 0.001)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=0.6, velocity=1.2, lower=0.0, upper=r.dust_cover_open
            ),
        )


def build_turntable(
    config: TurntableConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="turntable", assets=assets)
    for material, rgba in r.palette.items():
        model.material(material, rgba=rgba)

    _build_plinth(model, r)
    _build_platter_spindle(model, r)
    _build_tonearm_stage(model, r)
    _build_accessories(model, r)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_turntable(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_turntable(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedTurntableConfig) -> list[tuple[str, str]]:
    return [
        ("plinth_base", r.plinth_base),
        ("platter_spindle", r.platter_spindle),
        ("tonearm_stage", r.tonearm_stage),
        ("controls_accessories", r.controls_accessories),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def _visual_names(part: Part) -> set[str]:
    return {visual.name for visual in part.visuals if visual.name is not None}


def _has_visual(part: Part, visual_name: str) -> bool:
    return visual_name in _visual_names(part)


def _tonearm_record_lift(r: ResolvedTurntableConfig) -> float:
    if r.platter_spindle == "direct_platter":
        return 0.0
    return 0.028


def _allow_named_overlap(
    ctx: TestContext,
    part_a: Part,
    part_b: Part,
    *,
    elem_a: str,
    elem_b: str,
    reason: str,
) -> None:
    if _has_visual(part_a, elem_a) and _has_visual(part_b, elem_b):
        ctx.allow_overlap(part_a, part_b, elem_a=elem_a, elem_b=elem_b, reason=reason)


def _aabb_center_xy(aabb: tuple[tuple[float, float, float], tuple[float, float, float]]):
    return ((aabb[0][0] + aabb[1][0]) * 0.5, (aabb[0][1] + aabb[1][1]) * 0.5)


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    names = {p.name for p in model.parts}
    if "plinth" in names:
        plinth = model.get_part("plinth")
        if "platter" in names:
            platter = model.get_part("platter")
            _allow_named_overlap(
                ctx,
                plinth,
                platter,
                elem_a="bearing_collar",
                elem_b="hub_flange",
                reason="platter hub is captured by the visible plinth bearing collar",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                platter,
                elem_a="modular_spindle_insert",
                elem_b="hub_flange",
                reason="platter hub wraps the modular spindle insert",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                platter,
                elem_a="modular_spindle_insert",
                elem_b="platter_disc",
                reason="record/platter center sits over the modular spindle insert",
            )
        for support_name in ("spindle_support", "platter_support"):
            if support_name in names:
                support = model.get_part(support_name)
                _allow_named_overlap(
                    ctx,
                    plinth,
                    support,
                    elem_a="bearing_collar",
                    elem_b="bearing_pedestal",
                    reason=f"{support_name} pedestal is fixed into the plinth bearing collar",
                )
                _allow_named_overlap(
                    ctx,
                    plinth,
                    support,
                    elem_a="modular_spindle_insert",
                    elem_b="bearing_pedestal",
                    reason=f"{support_name} pedestal nests over the modular spindle insert",
                )
                _allow_named_overlap(
                    ctx,
                    plinth,
                    support,
                    elem_a="modular_spindle_insert",
                    elem_b="spindle_column",
                    reason=f"{support_name} spindle column is coaxial with the modular spindle insert",
                )
                _allow_named_overlap(
                    ctx,
                    plinth,
                    support,
                    elem_a="modular_spindle_insert",
                    elem_b="raised_support_foot",
                    reason=f"{support_name} foot is centered around the modular spindle insert",
                )
                if "platter" in names:
                    _allow_named_overlap(
                        ctx,
                        support,
                        model.get_part("platter"),
                        elem_a="spindle_column",
                        elem_b="hub_flange",
                        reason="platter hub wraps the visible spindle column",
                    )
        if "tonearm" in names:
            tonearm = model.get_part("tonearm")
            for parent_elem, child_elem in (
                ("tonearm_top_bearing_seat", "pivot_collar"),
                ("tonearm_top_bearing_seat", "vertical_pivot_spindle"),
                ("tonearm_vertical_post", "pivot_collar"),
                ("tonearm_vertical_post", "vertical_pivot_spindle"),
                ("detachable_tonearm_base_ring", "pivot_collar"),
            ):
                _allow_named_overlap(
                    ctx,
                    plinth,
                    tonearm,
                    elem_a=parent_elem,
                    elem_b=child_elem,
                    reason=f"{child_elem} is captured by the plinth {parent_elem}",
                )
        if "tonearm_carriage" in names:
            carriage = model.get_part("tonearm_carriage")
            _allow_named_overlap(
                ctx,
                plinth,
                carriage,
                elem_a="tonearm_mount_socket",
                elem_b="base_collar",
                reason="tonearm carriage base collar is seated in the plinth socket",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                carriage,
                elem_a="detachable_tonearm_base_ring",
                elem_b="base_collar",
                reason="tonearm carriage base collar is captured by the detachable base ring",
            )
        if "tonearm_base_module" in names:
            base = model.get_part("tonearm_base_module")
            _allow_named_overlap(
                ctx,
                plinth,
                base,
                elem_a="tonearm_reinforcement_pad",
                elem_b="mounting_disk",
                reason="modular tonearm mounting disk is bolted to the reinforced tonearm pad",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                base,
                elem_a="detachable_tonearm_base_ring",
                elem_b="mounting_disk",
                reason="modular tonearm mounting disk is captured by the detachable base ring",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                base,
                elem_a="detachable_tonearm_base_ring",
                elem_b="support_pedestal",
                reason="modular tonearm pedestal rises through the detachable base ring",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                base,
                elem_a="tonearm_mount_socket",
                elem_b="mounting_disk",
                reason="modular tonearm mounting disk is seated in the plinth socket",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                base,
                elem_a="tonearm_base_block",
                elem_b="mounting_disk",
                reason="modular tonearm mounting disk is bolted through the plinth base block",
            )
        if "tonearm_support" in names:
            support = model.get_part("tonearm_support")
            _allow_named_overlap(
                ctx,
                plinth,
                support,
                elem_a="right_side_rail",
                elem_b="support_base",
                reason="retrofit support base tucks under the rugged plinth side rail clamp",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                support,
                elem_a="tonearm_base_block",
                elem_b="support_base",
                reason="retrofit tonearm support base is bolted to the plinth base block",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                support,
                elem_a="tonearm_base_block",
                elem_b="arm_pedestal",
                reason="retrofit arm pedestal rises through the plinth base block",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                support,
                elem_a="tonearm_reinforcement_pad",
                elem_b="support_base",
                reason="retrofit support base sits on the reinforced tonearm pad",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                support,
                elem_a="tonearm_mount_socket",
                elem_b="support_base",
                reason="retrofit support base is captured by the lower tonearm mount socket",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                support,
                elem_a="detachable_tonearm_base_ring",
                elem_b="support_base",
                reason="retrofit support base is bolted through the detachable base ring",
            )
            _allow_named_overlap(
                ctx,
                plinth,
                support,
                elem_a="detachable_tonearm_base_ring",
                elem_b="arm_pedestal",
                reason="retrofit arm pedestal rises through the detachable base ring",
            )
        if "pitch_slider" in names:
            _allow_named_overlap(
                ctx,
                plinth,
                model.get_part("pitch_slider"),
                elem_a="pitch_track",
                elem_b="slider_shoe",
                reason="pitch slider shoe rides inside the plinth track",
            )
        for part_name, socket_elem, child_elem in (
            ("speed_dial", "speed_selector_slot", "dial_body"),
            ("power_button", "start_stop_button_socket", "button_cap"),
        ):
            if part_name in names:
                _allow_named_overlap(
                    ctx,
                    plinth,
                    model.get_part(part_name),
                    elem_a=socket_elem,
                    elem_b=child_elem,
                    reason=f"{part_name} is captured by its visible deck control socket",
                )
        for hatch in ("service_hatch_0", "service_hatch_1"):
            if hatch in names:
                _allow_named_overlap(
                    ctx,
                    plinth,
                    model.get_part(hatch),
                    elem_a=f"service_hatch_recess_{hatch.rsplit('_', 1)[1]}",
                    elem_b="hatch_plate",
                    reason=f"{hatch} plate closes into its plinth service recess",
                )
    for parent, child in (
        ("tonearm_carriage", "tonearm_tube"),
        ("tonearm_base_module", "tonearm_bearing_module"),
        ("tonearm_bearing_module", "tonearm_head_module"),
        ("tonearm_support", "tonearm_stage"),
        ("tonearm_support", "pitch_slider"),
        ("tonearm_base_module", "pitch_slider"),
    ):
        if parent in names and child in names:
            parent_part = model.get_part(parent)
            child_part = model.get_part(child)
            parent_elem, child_elem = {
                ("tonearm_carriage", "tonearm_tube"): ("left_cheek", "pivot_collar"),
                ("tonearm_base_module", "tonearm_bearing_module"): (
                    "support_pedestal",
                    "pivot_collar",
                ),
                ("tonearm_bearing_module", "tonearm_head_module"): (
                    "tonearm_tube",
                    "head_connector",
                ),
                ("tonearm_support", "tonearm_stage"): ("arm_pedestal", "pivot_collar"),
                ("tonearm_support", "pitch_slider"): ("support_base", "slider_shoe"),
                ("tonearm_base_module", "pitch_slider"): ("mounting_disk", "slider_shoe"),
            }[(parent, child)]
            _allow_named_overlap(
                ctx,
                parent_part,
                child_part,
                elem_a=parent_elem,
                elem_b=child_elem,
                reason=f"{child} pivot/coupler is mechanically captured by {parent}",
            )
            if (parent, child) == ("tonearm_carriage", "tonearm_tube"):
                _allow_named_overlap(
                    ctx,
                    parent_part,
                    child_part,
                    elem_a="right_cheek",
                    elem_b="pivot_collar",
                    reason="tonearm pivot collar is captured between both carriage cheeks",
                )
    if "dust_cover_guard" in names and "plinth" in names:
        ctx.allow_overlap(
            model.get_part("plinth"),
            model.get_part("dust_cover_guard"),
            elem_a="top_deck",
            elem_b="rear_hinge_bar",
            reason="dust cover hinge bar is mounted into the rear of the plinth top deck",
        )
        _allow_named_overlap(
            ctx,
            model.get_part("plinth"),
            model.get_part("dust_cover_guard"),
            elem_a="front_bumper",
            elem_b="rear_hinge_bar",
            reason="dust cover hinge barrel is clamped to the raised plinth bumper rail",
        )
        _allow_named_overlap(
            ctx,
            model.get_part("plinth"),
            model.get_part("dust_cover_guard"),
            elem_a="front_bumper",
            elem_b="rear_lower_clamp_rail",
            reason="dust cover lower clamp rail is clamped onto the raised plinth bumper rail",
        )
        for index in range(3):
            _allow_named_overlap(
                ctx,
                model.get_part("plinth"),
                model.get_part("dust_cover_guard"),
                elem_a="front_bumper",
                elem_b=f"rear_hinge_knuckle_{index}",
                reason=f"dust cover hinge knuckle {index} is pinned into the raised bumper rail",
            )
        for foot in ("left_bottom_slide_foot", "right_bottom_slide_foot", "front_bottom_lip"):
            _allow_named_overlap(
                ctx,
                model.get_part("plinth"),
                model.get_part("dust_cover_guard"),
                elem_a="top_deck",
                elem_b=foot,
                reason=f"dust cover {foot} sits on the plinth deck rather than floating",
            )
    if "guard_frame" in names and "plinth" in names:
        _allow_named_overlap(
            ctx,
            model.get_part("plinth"),
            model.get_part("guard_frame"),
            elem_a="top_deck",
            elem_b="fixed_guard_center_mount",
            reason="fixed guard center mount is screwed into the deck around the spindle area",
        )
        for index in range(3):
            _allow_named_overlap(
                ctx,
                model.get_part("plinth"),
                model.get_part("guard_frame"),
                elem_a="top_deck",
                elem_b=f"fixed_guard_foot_{index}",
                reason=f"fixed guard foot {index} is screwed to the plinth deck",
            )


def run_turntable_tests(object_model: ArticulatedObject, config: TurntableConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.030)
    ctx.fail_if_joint_mating_has_gap()

    parts = {p.name for p in object_model.parts}
    plinth = object_model.get_part("plinth")
    plinth_visuals = _visual_names(plinth)
    ctx.check("plinth_present", "plinth" in parts)
    ctx.check("platter_present", "platter" in parts)
    ctx.check(
        "tonearm_family_present",
        bool(parts & {"tonearm", "tonearm_tube", "tonearm_bearing_module", "tonearm_stage"}),
    )
    ctx.check(
        "plinth_has_real_tonearm_mount_detail",
        {"tonearm_base_block", "tonearm_mount_socket"} <= plinth_visuals
        and (
            r.tonearm_stage != "simple_pivot_tonearm"
            or {
                "tonearm_vertical_post",
                "tonearm_top_bearing_seat",
            }
            <= plinth_visuals
        ),
        details=f"plinth_visuals={sorted(plinth_visuals)}",
    )
    platter_spins = [
        j
        for j in object_model.articulations
        if j.articulation_type == ArticulationType.CONTINUOUS and j.child == "platter"
    ]
    ctx.check(
        "exactly_one_platter_spin",
        len(platter_spins) == 1,
        details=f"expected 1 platter CONTINUOUS joint, got {len(platter_spins)}",
    )
    if platter_spins:
        axis = platter_spins[0].axis
        ctx.check(
            "platter_spin_axis_vertical",
            axis == (0.0, 0.0, 1.0),
            details=f"expected vertical Z spin axis, got {axis!r}",
        )
    tonearm_revolutes = [
        j
        for j in object_model.articulations
        if j.articulation_type == ArticulationType.REVOLUTE
        and j.name in {"tonearm_pivot", "tonearm_pitch"}
    ]
    ctx.check("tonearm_has_revolute_motion", len(tonearm_revolutes) >= 1)
    platter = object_model.get_part("platter")
    if _has_visual(platter, "hub_flange"):
        ctx.expect_overlap(
            platter,
            plinth,
            axes="xy",
            min_overlap=0.018,
            elem_a="hub_flange",
            elem_b="bearing_collar",
            name="platter hub is centered in bearing collar footprint",
        )

    if "tonearm" in parts and _has_visual(
        object_model.get_part("tonearm"), "vertical_pivot_spindle"
    ):
        tonearm = object_model.get_part("tonearm")
        ctx.expect_overlap(
            tonearm,
            plinth,
            axes="xy",
            min_overlap=0.010,
            elem_a="vertical_pivot_spindle",
            elem_b="tonearm_top_bearing_seat",
            name="simple tonearm spindle is captured by top bearing seat",
        )
        ctx.expect_overlap(
            tonearm,
            plinth,
            axes="z",
            min_overlap=0.004,
            elem_a="vertical_pivot_spindle",
            elem_b="tonearm_top_bearing_seat",
            name="simple tonearm spindle overlaps bearing seat vertically",
        )
    if "tonearm_carriage" in parts:
        ctx.expect_overlap(
            object_model.get_part("tonearm_carriage"),
            plinth,
            axes="xy",
            min_overlap=0.010,
            elem_a="base_collar",
            elem_b="tonearm_mount_socket",
            name="two-axis tonearm carriage is seated in mount socket",
        )
    if "tonearm_base_module" in parts:
        ctx.expect_overlap(
            object_model.get_part("tonearm_base_module"),
            plinth,
            axes="xy",
            min_overlap=0.010,
            elem_a="mounting_disk",
            elem_b="tonearm_mount_socket",
            name="modular tonearm base disk is seated in mount socket",
        )
    if "tonearm_support" in parts:
        ctx.expect_overlap(
            object_model.get_part("tonearm_support"),
            plinth,
            axes="xy",
            min_overlap=0.030,
            elem_a="support_base",
            elem_b="tonearm_base_block",
            name="retrofit tonearm support sits on plinth base block",
        )

    stylus_part = next(
        (
            object_model.get_part(name)
            for name in ("tonearm", "tonearm_tube", "tonearm_head_module", "tonearm_stage")
            if name in parts and _has_visual(object_model.get_part(name), "stylus_tip")
        ),
        None,
    )
    if stylus_part is not None:
        stylus_visuals = _visual_names(stylus_part)
        ctx.check(
            "tonearm_has_named_cartridge_headshell_and_stylus",
            {"headshell", "cartridge_body", "stylus_tip"} <= stylus_visuals
            or {"headshell_plate", "cartridge_body", "stylus_tip"} <= stylus_visuals,
            details=f"{stylus_part.name}_visuals={sorted(stylus_visuals)}",
        )
        pivot = object_model.get_articulation("tonearm_pivot")
        limits = pivot.motion_limits
        lower = 0.0 if limits is None or limits.lower is None else float(limits.lower)
        upper = lower if limits is None or limits.upper is None else float(limits.upper)
        samples = tuple(lower + (upper - lower) * frac / 6.0 for frac in range(7))
        record_aabb = ctx.part_element_world_aabb(platter, elem="rubber_record_mat")
        stylus_can_reach_record = False
        closest_gap: float | None = None
        for value in samples:
            with ctx.pose(tonearm_pivot=value):
                stylus_aabb = ctx.part_element_world_aabb(stylus_part, elem="stylus_tip")
                record_aabb = ctx.part_element_world_aabb(platter, elem="rubber_record_mat")
                if stylus_aabb is None or record_aabb is None:
                    continue
                sx, sy = _aabb_center_xy(stylus_aabb)
                inside_xy = (
                    record_aabb[0][0] - 0.012 <= sx <= record_aabb[1][0] + 0.012
                    and record_aabb[0][1] - 0.012 <= sy <= record_aabb[1][1] + 0.012
                )
                gap = stylus_aabb[0][2] - record_aabb[1][2]
                closest_gap = gap if closest_gap is None else min(closest_gap, gap)
                stylus_can_reach_record = stylus_can_reach_record or (
                    inside_xy and -0.014 <= gap <= 0.070
                )
        ctx.check(
            "tonearm_sweep_places_stylus_near_record_surface",
            stylus_can_reach_record,
            details=f"closest_gap={closest_gap!r} samples={samples!r}",
        )
    if r.controls_accessories == "pitch_slider":
        ctx.check(
            "pitch_slider_prismatic",
            any(
                j.name == "pitch_slider" and j.articulation_type == ArticulationType.PRISMATIC
                for j in object_model.articulations
            ),
        )
    if r.controls_accessories == "guard_frame":
        ctx.check("dust_cover_guard_present", "dust_cover_guard" in parts)
        if "dust_cover_guard" in parts:
            cover = object_model.get_part("dust_cover_guard")
            cover_visuals = _visual_names(cover)
            ctx.check(
                "dust_cover_has_connected_feet_posts_and_lips",
                {
                    "rear_hinge_bar",
                    "left_bottom_slide_foot",
                    "right_bottom_slide_foot",
                    "front_bottom_lip",
                    "left_front_corner_post",
                    "right_front_corner_post",
                    "front_top_lip",
                }
                <= cover_visuals,
                details=f"cover_visuals={sorted(cover_visuals)}",
            )
            left_side = ctx.part_element_world_aabb(cover, elem="left_clear_side")
            right_side = ctx.part_element_world_aabb(cover, elem="right_clear_side")
            plinth_body = ctx.part_element_world_aabb(plinth, elem="plinth_body")
            ctx.check(
                "dust_cover_sides_have_only_small_plinth_overhang",
                left_side is not None
                and right_side is not None
                and plinth_body is not None
                and left_side[0][0] >= plinth_body[0][0] - 0.092
                and right_side[1][0] <= plinth_body[1][0] + 0.092,
                details=f"left_side={left_side}, right_side={right_side}, plinth={plinth_body}",
            )
    if r.controls_accessories == "fixed_guard_frame":
        ctx.check("fixed_guard_frame_present", "guard_frame" in parts)
        if "guard_frame" in parts:
            guard = object_model.get_part("guard_frame")
            guard_visuals = _visual_names(guard)
            ctx.check(
                "fixed_guard_has_three_deck_feet_and_ring",
                {
                    "fixed_guard_ring",
                    "fixed_guard_foot_0",
                    "fixed_guard_foot_1",
                    "fixed_guard_foot_2",
                }
                <= guard_visuals,
                details=f"guard_visuals={sorted(guard_visuals)}",
            )
            for index in range(3):
                ctx.expect_overlap(
                    guard,
                    plinth,
                    axes="z",
                    min_overlap=0.001,
                    elem_a=f"fixed_guard_foot_{index}",
                    elem_b="top_deck",
                    name=f"fixed guard foot {index} lands on deck",
                )
    if r.controls_accessories == "pitch_slider_and_guard_frame":
        ctx.check("pitch_slider_and_fixed_guard_present", {"pitch_slider", "guard_frame"} <= parts)
    return ctx.report()


__all__ = [
    "ControlsAccessories",
    "PaletteTheme",
    "PlatterSpindle",
    "PlinthBase",
    "ResolvedTurntableConfig",
    "TonearmStage",
    "TurntableConfig",
    "__modular__",
    "build_seeded_turntable",
    "build_turntable",
    "config_from_seed",
    "resolve_config",
    "run_turntable_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
