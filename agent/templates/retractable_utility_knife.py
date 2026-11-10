# SPDX-License-Identifier: Apache-2.0

"""Retractable utility knife procedural template.

PRIMARY_ANCHOR = rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7:rev_000001

Adapted from the anchor's structural skeleton with literal dimensions
parameterised. Part tree, joint topology, primitive choices and the use of
LatheGeometry / ExtrudeGeometry meshes for the blade and lofted button are
inherited verbatim from the anchor (per AUTHORING.md §A Rule 3);
only literal sizes, blade segment count and grip strip layout are made
configurable.

Anchor part tree:
  body_shell (14 visuals incl. 1 Mesh: rear_top_bridge)
  blade_carrier (3 Box visuals)
  blade (1 Mesh blade_plate + 5 Box score_lines)
  thumb_slider (Box slider_stem + Mesh slider_button + 3 Box ridges)
  lock_wheel (Cylinder wheel_disc + Cylinder wheel_hub + Box wheel_fin)

Anchor joint topology (must be preserved):
  body_shell -> blade_carrier : PRISMATIC axis x  (carrier slides along the body)
  blade_carrier -> blade       : FIXED            (blade follows carrier)
  blade_carrier -> thumb_slider: FIXED            (slider follows carrier)
  body_shell -> lock_wheel     : REVOLUTE axis y  (lock wheel pinned to right wall)

Rule 1 ("不动就不是 part") is upheld: only the four parts above exist; all
other visuals (grips, nose roofs, walls, score lines, slider ridges,
wheel fin) are attached as ``parent.visual(...)`` on whichever part already
moves with them. Rule 2 ("parent must really anchor the child") is enforced
by MatingContract declarations on every articulation that creates a separate
child part.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    LoftGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
)

BladeStyle = Literal["snap_off_trapezoid", "fixed_trapezoid", "compact_trapezoid"]
GripStyle = Literal["triple_strip", "single_strip", "diamond_pattern"]
LockStyle = Literal["thumb_wheel", "none"]
NoseTreatment = Literal["squared", "rounded", "pointed"]
PaletteTheme = Literal[
    "anchor_yellow",
    "industrial_black",
    "navy_blue",
    "safety_orange",
    "stealth_gray",
]


KNIFE_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "anchor_yellow": {
        "body": (0.92, 0.77, 0.16, 1.0),
        "grip": (0.12, 0.12, 0.12, 1.0),
        "track": (0.40, 0.42, 0.44, 1.0),
        "slider": (0.14, 0.14, 0.15, 1.0),
        "wheel": (0.10, 0.10, 0.11, 1.0),
        "steel": (0.82, 0.84, 0.86, 1.0),
        "dark_steel": (0.44, 0.47, 0.50, 1.0),
    },
    "industrial_black": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "grip": (0.65, 0.55, 0.18, 1.0),
        "track": (0.30, 0.32, 0.34, 1.0),
        "slider": (0.85, 0.20, 0.15, 1.0),
        "wheel": (0.05, 0.05, 0.06, 1.0),
        "steel": (0.82, 0.84, 0.86, 1.0),
        "dark_steel": (0.30, 0.32, 0.34, 1.0),
    },
    "navy_blue": {
        "body": (0.13, 0.22, 0.40, 1.0),
        "grip": (0.55, 0.58, 0.62, 1.0),
        "track": (0.30, 0.34, 0.42, 1.0),
        "slider": (0.92, 0.92, 0.92, 1.0),
        "wheel": (0.85, 0.55, 0.10, 1.0),
        "steel": (0.82, 0.84, 0.86, 1.0),
        "dark_steel": (0.42, 0.45, 0.50, 1.0),
    },
    "safety_orange": {
        "body": (0.95, 0.42, 0.10, 1.0),
        "grip": (0.10, 0.10, 0.11, 1.0),
        "track": (0.35, 0.36, 0.38, 1.0),
        "slider": (0.18, 0.18, 0.19, 1.0),
        "wheel": (0.06, 0.06, 0.07, 1.0),
        "steel": (0.85, 0.86, 0.88, 1.0),
        "dark_steel": (0.46, 0.48, 0.52, 1.0),
    },
    "stealth_gray": {
        "body": (0.22, 0.23, 0.25, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "track": (0.34, 0.36, 0.38, 1.0),
        "slider": (0.10, 0.10, 0.11, 1.0),
        "wheel": (0.03, 0.03, 0.04, 1.0),
        "steel": (0.65, 0.68, 0.72, 1.0),
        "dark_steel": (0.28, 0.30, 0.32, 1.0),
    },
}


@dataclass(frozen=True)
class RetractableUtilityKnifeConfig:
    blade_style: BladeStyle = "snap_off_trapezoid"
    grip_style: GripStyle = "triple_strip"
    lock_style: LockStyle = "thumb_wheel"
    nose_treatment: NoseTreatment = "squared"
    palette_theme: PaletteTheme = "anchor_yellow"

    handle_length: float = 0.168
    handle_width: float = 0.026
    handle_height: float = 0.021
    wall_thickness: float = 0.003

    blade_length: float = 0.121
    blade_height: float = 0.0088
    blade_thickness: float = 0.0008
    blade_segment_count: int = 5

    carrier_travel: float = 0.032
    carrier_length: float = 0.082
    carrier_width: float = 0.013
    carrier_block_length: float = 0.026

    slider_button_size: tuple[float, float, float] = (0.018, 0.010, 0.005)
    slider_ridge_count: int = 3

    lock_wheel_radius: float = 0.007
    lock_wheel_length: float = 0.005

    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: {
            "body": (0.92, 0.77, 0.16, 1.0),
            "grip": (0.12, 0.12, 0.12, 1.0),
            "track": (0.40, 0.42, 0.44, 1.0),
            "slider": (0.14, 0.14, 0.15, 1.0),
            "wheel": (0.10, 0.10, 0.11, 1.0),
            "steel": (0.82, 0.84, 0.86, 1.0),
            "dark_steel": (0.44, 0.47, 0.50, 1.0),
        }
    )


@dataclass(frozen=True)
class ResolvedRetractableUtilityKnifeConfig:
    blade_style: BladeStyle
    grip_style: GripStyle
    lock_style: LockStyle
    nose_treatment: NoseTreatment
    palette_theme: PaletteTheme
    handle_length: float
    handle_width: float
    handle_height: float
    wall_thickness: float
    blade_length: float
    blade_height: float
    blade_thickness: float
    blade_segment_count: int
    carrier_travel: float
    carrier_length: float
    carrier_width: float
    carrier_block_length: float
    slider_button_size: tuple[float, float, float]
    slider_ridge_count: int
    lock_wheel_radius: float
    lock_wheel_length: float
    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> RetractableUtilityKnifeConfig:
    """Sample a knife configuration for the given seed.

    Per AUTHORING.md §A Rule 3, `seed=0` must produce a config
    whose geometry fingerprint matches the PRIMARY_ANCHOR
    (`rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7`).
    That means: snap_off_trapezoid blade with 5 segments, triple grip
    strips, thumb wheel lock, anchor's nominal dimensions. Other seeds
    sample freely over the enum/continuous parameter domain.
    """
    if seed == 0:
        return RetractableUtilityKnifeConfig(
            blade_style="snap_off_trapezoid",
            grip_style="triple_strip",
            lock_style="thumb_wheel",
            nose_treatment="squared",
            palette_theme="anchor_yellow",
            handle_length=0.168,
            handle_width=0.026,
            handle_height=0.021,
            blade_length=0.121,
            blade_height=0.0088,
            blade_thickness=0.0008,
            blade_segment_count=5,
            carrier_travel=0.032,
            carrier_length=0.082,
            carrier_width=0.013,
            carrier_block_length=0.026,
            slider_button_size=(0.018, 0.010, 0.005),
            slider_ridge_count=3,
            lock_wheel_radius=0.007,
            lock_wheel_length=0.005,
        )

    rng = random.Random(seed)
    blade_style: BladeStyle = rng.choice(
        ("snap_off_trapezoid", "fixed_trapezoid", "compact_trapezoid")
    )
    grip_style: GripStyle = rng.choice(("triple_strip", "single_strip", "diamond_pattern"))
    lock_style: LockStyle = rng.choice(("thumb_wheel", "none"))
    nose_treatment: NoseTreatment = rng.choice(("squared", "rounded", "pointed"))
    palette_theme: PaletteTheme = rng.choice(tuple(KNIFE_PALETTE_PRESETS.keys()))

    # Tier 4 — wider continuous ranges (still safe under bbox_ratio ±30%).
    handle_length = rng.uniform(0.135, 0.205)
    handle_width = rng.uniform(0.022, 0.032)
    handle_height = rng.uniform(0.016, 0.028)

    blade_length = rng.uniform(0.085, 0.155)
    blade_height = rng.uniform(0.0070, 0.0110)

    carrier_travel = rng.uniform(0.022, 0.045)

    blade_segment_count = rng.randint(3, 8) if blade_style == "snap_off_trapezoid" else 0
    slider_ridge_count = rng.randint(1, 5)

    return RetractableUtilityKnifeConfig(
        blade_style=blade_style,
        grip_style=grip_style,
        lock_style=lock_style,
        nose_treatment=nose_treatment,
        palette_theme=palette_theme,
        handle_length=round(handle_length, 4),
        handle_width=round(handle_width, 4),
        handle_height=round(handle_height, 4),
        blade_length=round(blade_length, 4),
        blade_height=round(blade_height, 5),
        blade_segment_count=blade_segment_count,
        carrier_travel=round(carrier_travel, 4),
        slider_ridge_count=slider_ridge_count,
    )


def resolve_config(
    config: RetractableUtilityKnifeConfig,
) -> ResolvedRetractableUtilityKnifeConfig:
    valid_blade = {"snap_off_trapezoid", "fixed_trapezoid", "compact_trapezoid"}
    if str(config.blade_style) not in valid_blade:
        raise ValueError(f"Unsupported blade_style: {config.blade_style}")
    valid_grip = {"triple_strip", "single_strip", "diamond_pattern"}
    if str(config.grip_style) not in valid_grip:
        raise ValueError(f"Unsupported grip_style: {config.grip_style}")
    valid_lock = {"thumb_wheel", "none"}
    if str(config.lock_style) not in valid_lock:
        raise ValueError(f"Unsupported lock_style: {config.lock_style}")
    valid_nose = {"squared", "rounded", "pointed"}
    if str(config.nose_treatment) not in valid_nose:
        raise ValueError(f"Unsupported nose_treatment: {config.nose_treatment}")
    if str(config.palette_theme) not in KNIFE_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    handle_length = max(0.140, min(float(config.handle_length), 0.200))
    handle_width = max(0.020, min(float(config.handle_width), 0.034))
    handle_height = max(0.016, min(float(config.handle_height), 0.026))
    wall_thickness = max(0.0024, min(float(config.wall_thickness), 0.0040))
    blade_length = max(0.090, min(float(config.blade_length), 0.140))
    blade_height = max(0.0070, min(float(config.blade_height), 0.0110))
    blade_thickness = max(0.0006, min(float(config.blade_thickness), 0.0012))

    blade_seg = int(config.blade_segment_count)
    if config.blade_style != "snap_off_trapezoid":
        blade_seg = 0
    else:
        blade_seg = max(3, min(blade_seg, 8))

    carrier_travel = max(0.018, min(float(config.carrier_travel), 0.050))
    carrier_length = max(0.060, min(float(config.carrier_length), 0.110))
    carrier_width = max(0.010, min(handle_width - 2 * wall_thickness - 0.001, 0.020))
    carrier_block_length = max(0.018, min(float(config.carrier_block_length), 0.040))

    slider_button_size = tuple(float(v) for v in config.slider_button_size)
    if len(slider_button_size) != 3:
        slider_button_size = (0.018, 0.010, 0.005)
    slider_ridge_count = max(0, min(int(config.slider_ridge_count), 5))

    lock_wheel_radius = max(0.005, min(float(config.lock_wheel_radius), 0.011))
    lock_wheel_length = max(0.003, min(float(config.lock_wheel_length), 0.008))

    palette = dict(KNIFE_PALETTE_PRESETS[config.palette_theme])

    return ResolvedRetractableUtilityKnifeConfig(
        blade_style=config.blade_style,
        grip_style=config.grip_style,
        lock_style=config.lock_style,
        nose_treatment=config.nose_treatment,
        palette_theme=config.palette_theme,
        handle_length=handle_length,
        handle_width=handle_width,
        handle_height=handle_height,
        wall_thickness=wall_thickness,
        blade_length=blade_length,
        blade_height=blade_height,
        blade_thickness=blade_thickness,
        blade_segment_count=blade_seg,
        carrier_travel=carrier_travel,
        carrier_length=carrier_length,
        carrier_width=carrier_width,
        carrier_block_length=carrier_block_length,
        slider_button_size=slider_button_size,  # type: ignore[arg-type]
        slider_ridge_count=slider_ridge_count,
        lock_wheel_radius=lock_wheel_radius,
        lock_wheel_length=lock_wheel_length,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Mesh helpers — adapted from anchor's `_blade_mesh` /
# `_lofted_rounded_block_mesh` / `_slider_button_mesh` /
# `_rear_top_bridge_mesh` with literals parameterised. Primitive type
# (ExtrudeGeometry / LoftGeometry) is preserved per Rule 3.
# --------------------------------------------------------------------------- #


def _blade_mesh(
    *,
    blade_length: float,
    blade_height: float,
    blade_thickness: float,
    blade_style: BladeStyle = "snap_off_trapezoid",
) -> object:
    """Trapezoidal blade silhouette extruded along z, with profile chosen by
    blade_style:

    - snap_off_trapezoid (anchor): classic snap-off blade with rear tab,
      flat bottom edge, raked tip with rear_tip_lift kick at the tab end.
    - fixed_trapezoid: shorter rear tab, straight cutting edge across most
      of body_length, single sharp tip with no segmentation kick.
    - compact_trapezoid: shorter body_length, blunter chisel tip, taller
      rear tab — utility-blade variant that doesn't break into segments.

    All three branches stay Mesh-typed via mesh_from_geometry(ExtrudeGeometry)
    per primitive_complexity_lower_bound.
    """
    if blade_style == "fixed_trapezoid":
        rear_tab = blade_length * 0.055
        body_length = blade_length * 0.85
        tip_extension = blade_length * 0.095
        profile = [
            (-rear_tab, 0.0),
            (body_length, 0.0),
            (body_length + tip_extension, blade_height * 0.45),
            (body_length * 0.72, blade_height),
            (-rear_tab, blade_height),
        ]
        mesh_name = "utility_knife_blade_fixed"
    elif blade_style == "compact_trapezoid":
        rear_tab = blade_length * 0.105
        body_length = blade_length * 0.55
        tip_extension = blade_length * 0.255
        profile = [
            (-rear_tab, blade_height * 0.10),
            (-rear_tab + 0.003, 0.0),
            (body_length, 0.0),
            (body_length + tip_extension, blade_height * 0.55),
            (body_length * 0.62, blade_height),
            (-rear_tab, blade_height),
        ]
        mesh_name = "utility_knife_blade_compact"
    else:  # snap_off_trapezoid (anchor)
        rear_tab = blade_length * 0.085
        body_length = blade_length * 0.685
        tip_extension = blade_length * 0.300
        rear_tip_lift = blade_height * 0.0625
        tip_lift = blade_height * 0.75
        profile = [
            (-rear_tab, rear_tip_lift),
            (-rear_tab + 0.004, 0.0),
            (body_length, 0.0),
            (body_length + tip_extension, tip_lift),
            (body_length * 0.566, blade_height),
            (-rear_tab, blade_height),
        ]
        mesh_name = "utility_knife_blade"
    return mesh_from_geometry(
        ExtrudeGeometry.from_z0(profile, blade_thickness, cap=True, closed=True),
        mesh_name,
    )


def _lofted_rounded_block_mesh(
    name: str,
    *,
    width: float,
    depth: float,
    height: float,
    top_scale: float = 0.72,
    mid_scale: float = 0.88,
    top_x_shift: float = 0.0,
) -> object:
    """Three-section lofted rounded-rectangle mesh used for the slider button
    and rear bridge. Adapted verbatim from anchor with width/depth/height
    parameterised."""
    base_radius = min(width, depth) * 0.18

    def section(w: float, d: float, z: float, dx: float = 0.0):
        return [
            (x + dx, y, z)
            for x, y in rounded_rect_profile(w, d, radius=min(base_radius, w * 0.45, d * 0.45))
        ]

    geom = LoftGeometry(
        [
            section(width, depth, 0.0, 0.0),
            section(width * mid_scale, depth * mid_scale, height * 0.55, top_x_shift * 0.45),
            section(width * top_scale, depth * top_scale, height, top_x_shift),
        ],
        cap=True,
        closed=True,
    )
    return mesh_from_geometry(geom, name)


def _slider_button_mesh(size: tuple[float, float, float]) -> object:
    return _lofted_rounded_block_mesh(
        "utility_slider_button",
        width=float(size[0]),
        depth=float(size[1]),
        height=float(size[2]),
        top_scale=0.68,
        mid_scale=0.86,
        top_x_shift=0.0012,
    )


def _rear_top_bridge_mesh(width: float) -> object:
    return _lofted_rounded_block_mesh(
        "utility_rear_top_bridge",
        width=width,
        depth=0.018,
        height=0.003,
        top_scale=0.86,
        mid_scale=0.93,
        top_x_shift=0.0015,
    )


# --------------------------------------------------------------------------- #
# Builder
# --------------------------------------------------------------------------- #


def _build_body_shell(part, r: ResolvedRetractableUtilityKnifeConfig, palette) -> None:
    """Adapted from anchor's body_shell construction (model.py:L104-L193).

    Anchor produces 14 visuals; the template preserves all of them (bottom_pan,
    left/right walls, two top rails, rear cap, four nose visuals, grip strips,
    rear top bridge Mesh). Grip strip count varies by grip_style enum; other
    visuals always present.
    """
    body_mat = "body"
    grip_mat = "grip"
    L = r.handle_length
    W = r.handle_width
    H = r.handle_height
    wall = r.wall_thickness

    bottom_thickness = wall
    bottom_z = bottom_thickness * 0.5
    inner_height = H - bottom_thickness

    part.visual(
        Box((L, W, bottom_thickness)),
        origin=Origin(xyz=(0.0, 0.0, bottom_z)),
        material=body_mat,
        name="bottom_pan", material_class_id="metal.paint_coated",
    )

    wall_top_z = bottom_thickness + inner_height
    wall_center_z = bottom_thickness + 0.5 * inner_height
    wall_y_outer = 0.5 * W - 0.5 * wall
    wall_length = L - 2 * 0.006

    part.visual(
        Box((wall_length, wall, inner_height)),
        origin=Origin(xyz=(-0.002, -wall_y_outer, wall_center_z)),
        material=body_mat,
        name="left_wall", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((wall_length, wall, inner_height)),
        origin=Origin(xyz=(-0.002, +wall_y_outer, wall_center_z)),
        material=body_mat,
        name="right_wall", material_class_id="metal.paint_coated",
    )

    top_rail_length = L * 0.74
    top_rail_width = W * 0.39
    top_rail_thickness = 0.004
    top_rail_y = 0.5 * W - 0.5 * top_rail_width - wall * 0.0
    part.visual(
        Box((top_rail_length, top_rail_width, top_rail_thickness)),
        origin=Origin(xyz=(-0.006, -top_rail_y, wall_top_z - 0.5 * top_rail_thickness)),
        material=body_mat,
        name="left_top_rail", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((top_rail_length, top_rail_width, top_rail_thickness)),
        origin=Origin(xyz=(-0.006, +top_rail_y, wall_top_z - 0.5 * top_rail_thickness)),
        material=body_mat,
        name="right_top_rail", material_class_id="metal.paint_coated",
    )

    rear_cap_thickness = 0.010
    part.visual(
        Box((rear_cap_thickness, W, inner_height)),
        origin=Origin(xyz=(-0.5 * L + 0.5 * rear_cap_thickness, 0.0, wall_center_z)),
        material=body_mat,
        name="rear_cap", material_class_id="metal.paint_coated",
    )

    # Tier 1 — nose_treatment enum changes the proportions of the four nose
    # visuals (left/right cheek + left/right roof). seed=0 ("squared")
    # reproduces anchor's nose geometry exactly.
    if r.nose_treatment == "rounded":
        nose_cheek_length = 0.024
        nose_cheek_height_ratio = 0.62
        nose_roof_length = 0.030
    elif r.nose_treatment == "pointed":
        nose_cheek_length = 0.022
        nose_cheek_height_ratio = 0.55
        nose_roof_length = 0.034
    else:  # squared (anchor)
        nose_cheek_length = 0.016
        nose_cheek_height_ratio = 0.75
        nose_roof_length = 0.024

    nose_cheek_height = inner_height * nose_cheek_height_ratio
    nose_cheek_center_z = bottom_thickness + 0.5 * nose_cheek_height
    nose_cheek_x = 0.5 * L - 0.5 * nose_cheek_length
    part.visual(
        Box((nose_cheek_length, wall, nose_cheek_height)),
        origin=Origin(xyz=(nose_cheek_x, -wall_y_outer, nose_cheek_center_z)),
        material=body_mat,
        name="nose_left_cheek", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((nose_cheek_length, wall, nose_cheek_height)),
        origin=Origin(xyz=(nose_cheek_x, +wall_y_outer, nose_cheek_center_z)),
        material=body_mat,
        name="nose_right_cheek", material_class_id="metal.paint_coated",
    )

    nose_roof_thickness = 0.003
    nose_roof_width = top_rail_width
    nose_roof_x = 0.5 * L - 0.5 * nose_roof_length - 0.001
    part.visual(
        Box((nose_roof_length, nose_roof_width, nose_roof_thickness)),
        origin=Origin(xyz=(nose_roof_x, -top_rail_y, wall_top_z - 0.5 * nose_roof_thickness)),
        material=body_mat,
        name="nose_left_roof", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((nose_roof_length, nose_roof_width, nose_roof_thickness)),
        origin=Origin(xyz=(nose_roof_x, +top_rail_y, wall_top_z - 0.5 * nose_roof_thickness)),
        material=body_mat,
        name="nose_right_roof", material_class_id="metal.paint_coated",
    )

    grip_thickness = 0.0014
    grip_height = inner_height * 0.4
    grip_z = bottom_thickness + grip_height * 0.6
    grip_y = 0.5 * W - 0.5 * grip_thickness

    if r.grip_style == "triple_strip":
        # Anchor: three textured rubber strips (one long left, two right).
        part.visual(
            Box((L * 0.535, grip_thickness, grip_height)),
            origin=Origin(xyz=(-0.008, -grip_y, grip_z)),
            material=grip_mat,
            name="left_grip", material_class_id="rubber.pebbled",
        )
        part.visual(
            Box((L * 0.297, grip_thickness, grip_height)),
            origin=Origin(xyz=(-0.034, +grip_y, grip_z)),
            material=grip_mat,
            name="right_rear_grip", material_class_id="rubber.pebbled",
        )
        part.visual(
            Box((L * 0.178, grip_thickness, grip_height)),
            origin=Origin(xyz=(+0.056, +grip_y, grip_z)),
            material=grip_mat,
            name="right_front_grip", material_class_id="rubber.pebbled",
        )
    elif r.grip_style == "single_strip":
        # Single long strip down both sides.
        part.visual(
            Box((L * 0.78, grip_thickness, grip_height * 1.25)),
            origin=Origin(xyz=(-0.008, -grip_y, grip_z)),
            material=grip_mat,
            name="left_grip", material_class_id="rubber.smooth_plain",
        )
        part.visual(
            Box((L * 0.78, grip_thickness, grip_height * 1.25)),
            origin=Origin(xyz=(-0.008, +grip_y, grip_z)),
            material=grip_mat,
            name="right_grip", material_class_id="rubber.smooth_plain",
        )
    else:  # diamond_pattern
        # Grid of small grip dots, alternating sides. Preserves visual count
        # roughly comparable to anchor's 3 strips while producing a clearly
        # different surface texture.
        dot_w = L * 0.035
        dot_h = grip_height * 0.55
        dot_pitch = L * 0.07
        n_cols = max(3, int(L / dot_pitch * 0.55))
        for i in range(n_cols):
            x = -L * 0.30 + i * dot_pitch
            side_y = -grip_y if i % 2 == 0 else +grip_y
            part.visual(
                Box((dot_w, grip_thickness, dot_h)),
                origin=Origin(xyz=(x, side_y, grip_z + grip_height * 0.15)),
                material=grip_mat,
                name=f"grip_dot_{i}", material_class_id="rubber.pebbled",
            )

    bridge_width = L * 0.37
    part.visual(
        _rear_top_bridge_mesh(width=bridge_width),
        origin=Origin(xyz=(-L * 0.25, 0.0, wall_top_z - 0.0010)),
        material=body_mat,
        name="rear_top_bridge", material_class_id="metal.paint_coated",
    )

    part.inertial = Inertial.from_geometry(
        Box((L * 1.012, W * 1.19, H + 0.0)),
        mass=0.28,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * H)),
    )


def _build_blade_carrier(part, r: ResolvedRetractableUtilityKnifeConfig, palette) -> None:
    """Adapted from anchor's blade_carrier (model.py:L195-L218): 3 Box visuals
    carrier_rail / carrier_block / front_shoe."""
    track_mat = "track"
    cl = r.carrier_length
    cw = r.carrier_width
    block_l = r.carrier_block_length
    block_h = 0.010
    rail_thickness = 0.003

    part.visual(
        Box((cl, cw, rail_thickness)),
        origin=Origin(xyz=(cl * 0.5, 0.0, rail_thickness * 0.5)),
        material=track_mat,
        name="carrier_rail", material_class_id="metal.steel_galvanized",
    )
    part.visual(
        Box((block_l, cw, block_h)),
        origin=Origin(xyz=(block_l * 0.5 - 0.003, 0.0, block_h * 0.5)),
        material=track_mat,
        name="carrier_block", material_class_id="metal.steel_galvanized",
    )
    shoe_l = 0.018
    shoe_w = cw * 0.85
    shoe_h = 0.006
    part.visual(
        Box((shoe_l, shoe_w, shoe_h)),
        origin=Origin(xyz=(cl - shoe_l * 0.5 - 0.004, 0.0, shoe_h * 0.5 + 0.001)),
        material=track_mat,
        name="front_shoe", material_class_id="metal.steel_galvanized",
    )

    part.inertial = Inertial.from_geometry(
        Box((cl, cw, block_h)),
        mass=0.03,
        origin=Origin(xyz=(cl * 0.5, 0.0, block_h * 0.5)),
    )


def _build_blade(part, r: ResolvedRetractableUtilityKnifeConfig, palette) -> None:
    """Adapted from anchor's blade construction (model.py:L220-L241): blade_plate
    is always a Mesh (ExtrudeGeometry) — Rule 3 forbids downgrading to Box.
    Score lines are conditional on blade_style == 'snap_off_trapezoid'."""
    steel = "steel"
    dark_steel = "dark_steel"
    part.visual(
        _blade_mesh(
            blade_length=r.blade_length,
            blade_height=r.blade_height,
            blade_thickness=r.blade_thickness,
            blade_style=r.blade_style,
        ),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=steel,
        name="blade_plate", material_class_id="metal.steel_bare",
    )

    if r.blade_style == "snap_off_trapezoid" and r.blade_segment_count > 0:
        body_len = r.blade_length * 0.685
        span = body_len * 0.74
        start_x = -body_len * 0.20
        step = span / max(1, r.blade_segment_count)
        for i in range(r.blade_segment_count):
            x = start_x + (i + 0.5) * step
            part.visual(
                Box((0.0005, 0.00018, r.blade_height * 0.91)),
                origin=Origin(
                    xyz=(x, -0.00033, r.blade_height * 0.5),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=dark_steel,
                name=f"score_line_{i}", material_class_id="metal.blackened_gunmetal",
            )
    else:
        # Add one decorative cosmetic ridge so the blade isn't a bare mesh —
        # mirrors anchor's "at least one decoration" pattern. Non-snap_off
        # styles use a single longitudinal etch line.
        part.visual(
            Box((r.blade_length * 0.45, 0.00018, r.blade_height * 0.45)),
            origin=Origin(
                xyz=(0.0, -0.00033, r.blade_height * 0.5),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=dark_steel,
            name="score_line_0", material_class_id="metal.blackened_gunmetal",
        )

    part.inertial = Inertial.from_geometry(
        Box((r.blade_length, r.blade_thickness, r.blade_height)),
        mass=0.01,
        origin=Origin(xyz=(r.blade_length * 0.235, 0.0, r.blade_height * 0.5)),
    )


def _build_thumb_slider(part, r: ResolvedRetractableUtilityKnifeConfig, palette) -> None:
    """Adapted from anchor's thumb_slider (model.py:L243-L267): Box slider_stem,
    Mesh slider_button (lofted), and N Box ridges."""
    slider_mat = "slider"
    dark_steel = "dark_steel"
    stem_size = (0.005, 0.003, 0.008)
    part.visual(
        Box(stem_size),
        origin=Origin(xyz=(0.0, 0.0, stem_size[2] * 0.5)),
        material=slider_mat,
        name="slider_stem", material_class_id="plastic.opaque_glossy_molded",
    )
    btn_w, btn_d, btn_h = r.slider_button_size
    part.visual(
        _slider_button_mesh(r.slider_button_size),
        origin=Origin(xyz=(0.0, 0.0, stem_size[2])),
        material=slider_mat,
        name="slider_button", material_class_id="plastic.opaque_glossy_molded",
    )
    if r.slider_ridge_count > 0:
        span = btn_w * 0.55
        start_x = -span * 0.5
        step = span / max(1, r.slider_ridge_count - 1) if r.slider_ridge_count > 1 else 0.0
        for i in range(r.slider_ridge_count):
            x = start_x + i * step if r.slider_ridge_count > 1 else 0.0
            part.visual(
                Box((0.0014, btn_d * 0.9, 0.0012)),
                origin=Origin(xyz=(x, 0.0, stem_size[2] + btn_h * 1.12)),
                material=dark_steel,
                name=f"slider_ridge_{i}", material_class_id="metal.blackened_gunmetal",
            )

    part.inertial = Inertial.from_geometry(
        Box((btn_w, btn_d, stem_size[2] + btn_h)),
        mass=0.012,
        origin=Origin(xyz=(0.0, 0.0, (stem_size[2] + btn_h) * 0.5)),
    )


def _build_lock_wheel(part, r: ResolvedRetractableUtilityKnifeConfig, palette) -> None:
    """Adapted from anchor's lock_wheel (model.py:L269-L292): Cylinder
    wheel_disc (rotated so its axis is along y) + Cylinder wheel_hub + Box
    wheel_fin. Wheel sits OUTSIDE the body wall, so child link origin will be
    on the body's positive_y wall face."""
    wheel_mat = "wheel"
    dark_steel = "dark_steel"
    R = r.lock_wheel_radius
    L = r.lock_wheel_length
    disc_y_half = L * 0.5

    part.visual(
        Cylinder(radius=R, length=L),
        origin=Origin(xyz=(0.0, disc_y_half, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=wheel_mat,
        name="wheel_disc", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Cylinder(radius=R * 0.43, length=L * 0.4),
        origin=Origin(
            xyz=(0.0, L + L * 0.2, 0.0),
            rpy=(-math.pi / 2.0, 0.0, 0.0),
        ),
        material=dark_steel,
        name="wheel_hub", material_class_id="metal.blackened_gunmetal",
    )
    fin_l = R * 0.5
    fin_w = L * 0.84
    fin_h = R * 0.31
    part.visual(
        Box((fin_l, fin_w, fin_h)),
        origin=Origin(xyz=(R * 1.14, disc_y_half + L * 0.38, 0.0)),
        material=dark_steel,
        name="wheel_fin", material_class_id="metal.blackened_gunmetal",
    )

    part.inertial = Inertial.from_geometry(
        Cylinder(radius=R, length=L),
        mass=0.01,
        origin=Origin(xyz=(0.0, disc_y_half, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
    )


def build_retractable_utility_knife(
    config: RetractableUtilityKnifeConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    palette = r.palette
    model = ArticulatedObject(name="retractable_utility_knife", assets=assets)
    for material_name, rgba in palette.items():
        model.material(material_name, rgba=rgba)

    body_shell = model.part("body_shell")
    _build_body_shell(body_shell, r, palette)

    blade_carrier = model.part("blade_carrier")
    _build_blade_carrier(blade_carrier, r, palette)

    blade = model.part("blade")
    _build_blade(blade, r, palette)

    thumb_slider = model.part("thumb_slider")
    _build_thumb_slider(thumb_slider, r, palette)

    # Joint origins. The carrier rides ON the bottom_pan (anchor places it at
    # z=0.003 above floor); blade and slider attach FIXED on top of the
    # carrier_block; lock wheel pins to the body's right wall.
    bottom_thickness = r.wall_thickness
    inner_height = r.handle_height - bottom_thickness
    carrier_start_x = -r.handle_length * 0.5 + r.carrier_block_length * 0.5 + 0.008
    _ = bottom_thickness + 0.010  # carrier_top_z; not used as a variable but documents the value

    model.articulation(
        "body_to_carrier",
        ArticulationType.PRISMATIC,
        parent=body_shell,
        child=blade_carrier,
        origin=Origin(xyz=(carrier_start_x, 0.0, bottom_thickness)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=0.20, lower=0.0, upper=r.carrier_travel),
        mating=MatingContract(
            parent_face_geometry="bottom_pan",
            parent_face_side="positive_z",
            child_face_geometry="carrier_rail",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )

    # Blade sits on the carrier_block's top face. The blade Mesh's bottom
    # face (after the rpy=(π/2,0,0) rotation putting it flat) is at y=0 in
    # the blade's local frame, but its negative_z extent in world frame is
    # the blade Mesh's "low" side. We attach the blade so its plate rests at
    # carrier_block_top_z; the joint origin in carrier-local frame is at
    # (block_center_x, 0, carrier_block_top_z).
    block_top_z = 0.010
    block_center_x = r.carrier_block_length * 0.5 - 0.003
    model.articulation(
        "carrier_to_blade",
        ArticulationType.FIXED,
        parent=blade_carrier,
        child=blade,
        origin=Origin(xyz=(block_center_x + 0.002, 0.0, block_top_z + 0.0002)),
        mating=MatingContract(
            parent_face_geometry="carrier_block",
            parent_face_side="positive_z",
            child_face_geometry="blade_plate",
            child_face_side="negative_z",
            contact_tol=0.0020,
        ),
    )

    # Slider sits on the carrier_block too, at a slightly different x offset
    # (right above the slot in the body's top rails).
    slider_x_in_carrier = r.carrier_block_length * 0.5 + 0.004
    model.articulation(
        "carrier_to_slider",
        ArticulationType.FIXED,
        parent=blade_carrier,
        child=thumb_slider,
        origin=Origin(xyz=(slider_x_in_carrier, 0.0, block_top_z)),
        mating=MatingContract(
            parent_face_geometry="carrier_block",
            parent_face_side="positive_z",
            child_face_geometry="slider_stem",
            child_face_side="negative_z",
            contact_tol=0.0010,
        ),
    )

    if r.lock_style == "thumb_wheel":
        lock_wheel = model.part("lock_wheel")
        _build_lock_wheel(lock_wheel, r, palette)
        wheel_x = r.handle_length * 0.13
        wall_y = 0.5 * r.handle_width - r.wall_thickness * 0.5
        wheel_z = bottom_thickness + inner_height * 0.65
        model.articulation(
            "body_to_lock_wheel",
            ArticulationType.REVOLUTE,
            parent=body_shell,
            child=lock_wheel,
            origin=Origin(xyz=(wheel_x, wall_y, wheel_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=8.0, lower=-math.pi, upper=math.pi),
            mating=MatingContract(
                parent_face_geometry="right_wall",
                parent_face_side="positive_y",
                child_face_geometry="wheel_disc",
                child_face_side="negative_y",
                contact_tol=0.0020,
            ),
        )

    return model


def build_seeded_retractable_utility_knife(seed: int) -> ArticulatedObject:
    return build_retractable_utility_knife(config_from_seed(seed))


def _expect_anchor_size_range(ctx: TestContext, body_shell, r) -> None:
    """Anchor body AABB is roughly 0.168 x 0.026 x 0.021. We assert the
    template's body_shell stays inside a relaxed envelope so the rendered
    knife always reads as a hand-held utility knife rather than a knife
    block, ruler, or pen-shaped fragment."""
    body_aabb = ctx.part_world_aabb(body_shell)
    if body_aabb is None:
        return
    x_size = body_aabb[1][0] - body_aabb[0][0]
    y_size = body_aabb[1][1] - body_aabb[0][1]
    z_size = body_aabb[1][2] - body_aabb[0][2]
    ctx.check(
        "body_size_realistic",
        0.130 <= x_size <= 0.215 and 0.018 <= y_size <= 0.040 and 0.014 <= z_size <= 0.030,
        f"Unexpected body AABB extents: x={x_size:.4f} y={y_size:.4f} z={z_size:.4f}",
    )


def _expect_carrier_travel_changes_blade_position(
    ctx: TestContext, body_to_carrier, blade, body_shell
) -> None:
    """When the carrier slides from lower to upper, the blade tip should
    extend past the body's nose by roughly the carrier_travel distance.

    This mirrors the anchor's "blade_extended_exposure" / "blade_rest_exposure"
    checks but is loosened to a pure motion-delta assertion so the template
    doesn't have to pin specific exposure values across enum branches.
    """
    limits = body_to_carrier.motion_limits
    if limits is None or limits.lower is None or limits.upper is None:
        return
    with ctx.pose({body_to_carrier: limits.lower}):
        rest = ctx.part_world_aabb(blade)
        rest_body = ctx.part_world_aabb(body_shell)
        ctx.fail_if_parts_overlap_in_current_pose(name="carrier_lower_no_overlap")
        ctx.fail_if_isolated_parts(name="carrier_lower_no_floating")
    with ctx.pose({body_to_carrier: limits.upper}):
        extended = ctx.part_world_aabb(blade)
        ctx.fail_if_parts_overlap_in_current_pose(name="carrier_upper_no_overlap")
        ctx.fail_if_isolated_parts(name="carrier_upper_no_floating")
    if rest is None or extended is None or rest_body is None:
        return
    advance = extended[1][0] - rest[1][0]
    expected = limits.upper - limits.lower
    ctx.check(
        "carrier_travel_advances_blade",
        abs(advance - expected) < 0.005,
        (
            f"Blade tip world-x advance under carrier slide should be ~{expected:.4f}m, "
            f"got {advance:.4f}m"
        ),
    )


def _expect_lock_wheel_rotation_visible(ctx: TestContext, body_to_lock_wheel, lock_wheel) -> None:
    """The fin on the lock wheel must visibly move when the wheel rotates
    π/2 — protects against accidentally placing the fin on the rotation
    axis (where it'd appear stationary)."""
    if body_to_lock_wheel is None:
        return
    with ctx.pose({body_to_lock_wheel: 0.0}):
        rest_fin = ctx.part_element_world_aabb(lock_wheel, elem="wheel_fin")
    with ctx.pose({body_to_lock_wheel: math.pi / 2.0}):
        turned_fin = ctx.part_element_world_aabb(lock_wheel, elem="wheel_fin")
    if rest_fin is None or turned_fin is None:
        return
    moved = (
        abs(turned_fin[1][0] - rest_fin[1][0]) >= 0.0015
        or abs(turned_fin[1][2] - rest_fin[1][2]) >= 0.0015
        or abs(turned_fin[0][0] - rest_fin[0][0]) >= 0.0015
        or abs(turned_fin[0][2] - rest_fin[0][2]) >= 0.0015
    )
    ctx.check(
        "lock_wheel_fin_moves_under_rotation",
        moved,
        f"wheel_fin AABB did not move enough: rest={rest_fin!r} turned={turned_fin!r}",
    )


def run_retractable_utility_knife_tests(
    model: ArticulatedObject,
    config: RetractableUtilityKnifeConfig,
) -> TestReport:
    """Author-layer QC for the retractable utility knife template.

    The compiler-owned baseline (`check_model_valid` / `fail_if_isolated_parts`
    / `fail_if_parts_overlap_in_current_pose` /
    `fail_if_articulation_origin_far_from_geometry` /
    `fail_if_joint_mating_has_gap`) is run automatically by
    `_run_compiler_owned_baseline_tests` during `target=full` compile, so
    we don't need to re-invoke those here. This function adds knife-specific
    assertions that go beyond the generic baseline:

    - body size envelope (catches scaled-up or scaled-down geometry)
    - carrier travel actually advances blade tip in world coordinates
    - both extreme carrier poses are overlap- and isolation-free
    - lock_wheel fin visibly moves when the wheel rotates 90°
    - joint type/axis sanity for body_to_carrier and body_to_lock_wheel
    """
    r = resolve_config(config)
    ctx = TestContext(model)

    body_shell = model.get_part("body_shell")
    blade = model.get_part("blade")

    body_to_carrier = model.get_articulation("body_to_carrier")
    body_to_lock_wheel = None
    if r.lock_style == "thumb_wheel":
        body_to_lock_wheel = model.get_articulation("body_to_lock_wheel")

    # Baseline-equivalent checks (will be deduplicated against the compiler
    # baseline by `_filter_duplicate_automated_baseline_results` so the
    # author and the baseline don't both report the same failure twice).
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # Joint type/axis sanity. Adapted from anchor's run_tests "carrier_joint_type"
    # and "carrier_joint_axis" checks.
    ctx.check(
        "carrier_joint_type_is_prismatic",
        body_to_carrier.articulation_type == ArticulationType.PRISMATIC,
        f"Expected PRISMATIC carrier joint, got {body_to_carrier.articulation_type!r}",
    )
    ctx.check(
        "carrier_joint_axis_is_x",
        tuple(body_to_carrier.axis) == (1.0, 0.0, 0.0),
        f"Expected carrier axis (1, 0, 0), got {body_to_carrier.axis!r}",
    )
    if body_to_lock_wheel is not None:
        ctx.check(
            "wheel_joint_axis_is_y",
            tuple(body_to_lock_wheel.axis) == (0.0, 1.0, 0.0),
            f"Expected lock wheel axis (0, 1, 0), got {body_to_lock_wheel.axis!r}",
        )

    # Contact expectations are handled by the MatingContract gate in baseline
    # (`fail_if_joint_mating_has_gap`) — we don't repeat them here at the
    # 1µm contact tolerance because the carrier intentionally sits a few
    # tenths of a millimetre above its parent face to avoid bot-mesh
    # collision sliver overlaps during the sweep poses.

    # Knife-specific shape envelope + motion-limit sweep.
    _expect_anchor_size_range(ctx, body_shell, r)
    _expect_carrier_travel_changes_blade_position(ctx, body_to_carrier, blade, body_shell)
    if body_to_lock_wheel is not None:
        lock_wheel = model.get_part("lock_wheel")
        _expect_lock_wheel_rotation_visible(ctx, body_to_lock_wheel, lock_wheel)

    return ctx.report()


# --------------------------------------------------------------------------- #
# Authoring notes (AUTHORING.md §A compliance summary)
# --------------------------------------------------------------------------- #
# Rule 1 — "不动就不是 part" (if it doesn't articulate, it isn't a part):
#   The template defines exactly 5 parts (4 if lock_style == "none"). Every
#   decorative cylinder, box, rail strip, grip strip, score line and slider
#   ridge is attached as `part.visual(...)` on whichever part already moves
#   with it, never as a separate part joined by a FIXED articulation.
#
# Rule 2 — "parent must really anchor the child" (no phantom anchors):
#   Each non-trivial joint declares a MatingContract:
#     body_to_carrier:   parent=body_shell.bottom_pan (+z) -> child=blade_carrier.carrier_rail (-z)
#     carrier_to_blade:  parent=blade_carrier.carrier_block (+z) -> child=blade.blade_plate (-z)
#     carrier_to_slider: parent=blade_carrier.carrier_block (+z) -> child=thumb_slider.slider_stem (-z)
#     body_to_lock_wheel: parent=body_shell.right_wall (+y) -> child=lock_wheel.wheel_disc (-y)
#   The parent face geometries (bottom_pan, carrier_block, right_wall) are
#   large real visuals — not 3mm cosmetic disks — so the rendered model
#   visibly anchors the child even before the gate check runs.
#
# Rule 3 — "derive structure from a single PRIMARY_ANCHOR":
#   PRIMARY_ANCHOR = rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7:rev_000001
#   - Part tree (body_shell / blade_carrier / blade / thumb_slider / lock_wheel)
#     and joint topology (body->carrier PRISMATIC, carrier->blade FIXED,
#     carrier->slider FIXED, body->lock_wheel REVOLUTE) come from the anchor.
#   - Mesh primitives (ExtrudeGeometry blade, LoftGeometry slider button and
#     rear top bridge) are preserved verbatim per primitive_complexity_lower_bound.
#   - All literal dimensions in the anchor were lifted into the Config and
#     ResolvedConfig dataclasses; only `seed == 0` reproduces the exact
#     anchor configuration (see anchor_geometry_match gate semantics).
# --------------------------------------------------------------------------- #


# Future maintainers: when adding a new BladeStyle / GripStyle / LockStyle
# enum value, re-run `articraft template compile-sweep retractable_utility_knife`
# and confirm anchor_geometry_match still passes at seed=0 for the new
# branch's representative configuration.


__all__ = [
    "BladeStyle",
    "GripStyle",
    "LockStyle",
    "RetractableUtilityKnifeConfig",
    "ResolvedRetractableUtilityKnifeConfig",
    "build_retractable_utility_knife",
    "build_seeded_retractable_utility_knife",
    "config_from_seed",
    "resolve_config",
    "run_retractable_utility_knife_tests",
]
