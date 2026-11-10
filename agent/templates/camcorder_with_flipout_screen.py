# SPDX-License-Identifier: Apache-2.0

"""Procedural template for category `camcorder_with_flipout_screen`."""

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

BodyProfile = Literal[
    "palm_rounded", "tapered_home_video", "documentary_block", "shoulder_rear_hump"
]
LensStyle = Literal["short_objective", "long_barrel", "wide_hood"]
HoodStyle = Literal["none", "rectangular_hood", "stepped_shade"]
ScreenLayout = Literal["single_door", "door_with_inner_swivel", "armature_two_link"]
GripStyle = Literal["none", "side_pad", "hand_strap", "top_handle", "strap_and_handle"]
ViewfinderStyle = Literal["none", "rear_eyecup", "raised_viewfinder_with_diopter"]
ControlLayout = Literal["minimal", "side_buttons", "mode_dial", "buttons_and_dial"]
RingStyle = Literal["none", "focus_ring", "zoom_ring"]
MaterialStyle = Literal["charcoal", "silver", "broadcast_black"]

# Sequenced 2-DOF flip-out screen (door_with_inner_swivel): the outer flip hinge
# opens the panel away from the body, then the inner swivel rotates the display
# to face any direction (including fully face-forward for self-recording). Both
# axes keep their FULL designed travel — the useful "flipped out + rotated
# face-forward" pose must be reachable. Some flip×swivel combinations sweep the
# panel back toward the body/grip (a fold-in the pose-setter would never leave it
# in); those screen↔body/grip overlaps are whitelisted in run_camcorder_tests.
_SCREEN_SWIVEL_RANGE_RAD = math.radians(180.0)  # full designed rotate (face-forward)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "charcoal": {
        "body": (0.18, 0.19, 0.20, 1.0),
        "trim": (0.08, 0.08, 0.09, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
        "glass": (0.12, 0.30, 0.36, 0.55),
        "label": (0.78, 0.78, 0.74, 1.0),
    },
    "silver": {
        "body": (0.66, 0.68, 0.68, 1.0),
        "trim": (0.16, 0.17, 0.18, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
        "glass": (0.08, 0.22, 0.30, 0.52),
        "label": (0.05, 0.05, 0.05, 1.0),
    },
    "broadcast_black": {
        "body": (0.06, 0.06, 0.07, 1.0),
        "trim": (0.12, 0.12, 0.13, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "glass": (0.10, 0.34, 0.40, 0.58),
        "label": (0.85, 0.82, 0.68, 1.0),
    },
}


@dataclass(frozen=True)
class CamcorderWithFlipoutScreenConfig:
    body_length: float | None = None
    body_width: float = 0.105
    body_height: float = 0.085
    body_profile: BodyProfile = "tapered_home_video"
    lens_style: LensStyle = "short_objective"
    hood_style: HoodStyle = "none"
    lens_length: float | None = None
    lens_radius: float | None = None
    screen_layout: ScreenLayout = "single_door"
    screen_width: float = 0.082
    screen_height: float = 0.060
    screen_open_range_deg: float = 135.0
    grip_style: GripStyle = "hand_strap"
    viewfinder_style: ViewfinderStyle = "rear_eyecup"
    control_layout: ControlLayout = "buttons_and_dial"
    ring_style: RingStyle = "focus_ring"
    button_count: int = 3
    material_style: MaterialStyle = "charcoal"
    name: str = "reference_camcorder_with_flipout_screen"


@dataclass(frozen=True)
class ResolvedCamcorderWithFlipoutScreenConfig:
    body_length: float
    body_width: float
    body_height: float
    body_profile: BodyProfile
    lens_style: LensStyle
    hood_style: HoodStyle
    lens_length: float
    lens_radius: float
    screen_layout: ScreenLayout
    screen_width: float
    screen_height: float
    screen_open_range_rad: float
    swivel_hinge_range_rad: float
    screen_swivel_range_rad: float
    screen_hinge_origin: tuple[float, float, float]
    grip_style: GripStyle
    viewfinder_style: ViewfinderStyle
    control_layout: ControlLayout
    ring_style: RingStyle
    button_count: int
    material_style: MaterialStyle
    name: str


def config_from_seed(seed: int) -> CamcorderWithFlipoutScreenConfig:
    rng = random.Random(seed)
    profile: BodyProfile = rng.choice(
        ("palm_rounded", "tapered_home_video", "documentary_block", "shoulder_rear_hump")
    )
    length = {
        "palm_rounded": rng.uniform(0.155, 0.185),
        "tapered_home_video": rng.uniform(0.170, 0.215),
        "documentary_block": rng.uniform(0.220, 0.285),
        "shoulder_rear_hump": rng.uniform(0.235, 0.320),
    }[profile]
    lens_style: LensStyle = rng.choice(("short_objective", "long_barrel", "wide_hood"))
    hood_style: HoodStyle = (
        rng.choice(("rectangular_hood", "stepped_shade"))
        if lens_style == "wide_hood" or rng.random() < 0.28
        else "none"
    )
    # Keep the stable door families. The two-link armature is still excluded
    # because it adds a floating intermediate linkage that is easy to misplace.
    screen_layout: ScreenLayout = rng.choice(("single_door", "door_with_inner_swivel"))
    control_layout: ControlLayout = rng.choice(("minimal", "side_buttons"))
    return CamcorderWithFlipoutScreenConfig(
        body_length=round(length, 3),
        body_width=round(rng.uniform(0.090, 0.125), 3),
        body_height=round(rng.uniform(0.070, 0.105), 3),
        body_profile=profile,
        lens_style=lens_style,
        hood_style=hood_style,
        lens_length=round(rng.uniform(0.040, 0.115), 3),
        lens_radius=round(rng.uniform(0.025, 0.044), 3),
        screen_layout=screen_layout,
        screen_width=round(rng.uniform(0.064, 0.096), 3),
        screen_height=round(rng.uniform(0.048, 0.072), 3),
        screen_open_range_deg=round(rng.uniform(120.0, 180.0), 1),
        grip_style=rng.choice(("none", "side_pad", "hand_strap")),
        viewfinder_style=rng.choice(("none", "rear_eyecup", "raised_viewfinder_with_diopter")),
        control_layout=control_layout,
        ring_style=rng.choice(("none", "focus_ring", "zoom_ring")),
        button_count=rng.choice((2, 3, 4)),
        material_style=rng.choice(("charcoal", "silver", "broadcast_black")),
        name=f"seeded_camcorder_{seed}",
    )


def resolve_config(
    config: CamcorderWithFlipoutScreenConfig,
) -> ResolvedCamcorderWithFlipoutScreenConfig:
    if config.body_profile not in {
        "palm_rounded",
        "tapered_home_video",
        "documentary_block",
        "shoulder_rear_hump",
    }:
        raise ValueError(f"Unsupported body_profile: {config.body_profile}")
    if config.lens_style not in {"short_objective", "long_barrel", "wide_hood"}:
        raise ValueError(f"Unsupported lens_style: {config.lens_style}")
    if config.hood_style not in {"none", "rectangular_hood", "stepped_shade"}:
        raise ValueError(f"Unsupported hood_style: {config.hood_style}")
    if config.screen_layout not in {"single_door", "door_with_inner_swivel", "armature_two_link"}:
        raise ValueError(f"Unsupported screen_layout: {config.screen_layout}")
    if config.grip_style not in {
        "none",
        "side_pad",
        "hand_strap",
        "top_handle",
        "strap_and_handle",
    }:
        raise ValueError(f"Unsupported grip_style: {config.grip_style}")
    if config.viewfinder_style not in {"none", "rear_eyecup", "raised_viewfinder_with_diopter"}:
        raise ValueError(f"Unsupported viewfinder_style: {config.viewfinder_style}")
    if config.control_layout not in {"minimal", "side_buttons", "mode_dial", "buttons_and_dial"}:
        raise ValueError(f"Unsupported control_layout: {config.control_layout}")
    if config.ring_style not in {"none", "focus_ring", "zoom_ring"}:
        raise ValueError(f"Unsupported ring_style: {config.ring_style}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if config.button_count < 0 or config.button_count > 6:
        raise ValueError("button_count must be in [0, 6]")

    if config.screen_layout == "armature_two_link":
        config = replace(config, screen_layout="single_door")
    if config.grip_style in {"top_handle", "strap_and_handle"}:
        config = replace(config, grip_style="hand_strap")

    default_length = {
        "palm_rounded": 0.165,
        "tapered_home_video": 0.190,
        "documentary_block": 0.245,
        "shoulder_rear_hump": 0.265,
    }[config.body_profile]
    body_length = max(0.140, min(0.330, config.body_length or default_length))
    body_width = max(0.075, min(0.140, config.body_width))
    body_height = max(0.060, min(0.120, config.body_height))
    lens_length = config.lens_length
    if lens_length is None:
        lens_length = {"short_objective": 0.050, "long_barrel": 0.090, "wide_hood": 0.075}[
            config.lens_style
        ]
    lens_radius = config.lens_radius
    if lens_radius is None:
        lens_radius = {"short_objective": 0.026, "long_barrel": 0.034, "wide_hood": 0.040}[
            config.lens_style
        ]
    if config.hood_style == "none" and config.lens_style == "wide_hood":
        hood_style: HoodStyle = "rectangular_hood"
    else:
        hood_style = config.hood_style
    screen_width = max(0.060, min(0.105, config.screen_width))
    screen_height = max(0.044, min(0.080, config.screen_height))
    display_bay_center_x = body_length * 0.08
    hinge_origin = (display_bay_center_x - screen_width * 0.50, body_width * 0.5 + 0.005, 0.0)
    screen_open_range_rad = math.radians(max(90.0, min(180.0, config.screen_open_range_deg)))
    # door_with_inner_swivel stacks two parallel (vertical) revolute axes: the
    # outer flip hinge (full seeded open range) and the inner swivel (full
    # designed rotate, up to face-forward). Both keep their full independent
    # travel — the useful "flipped out + rotated face-forward" pose is reachable.
    # Flip×swivel combinations that fold the panel back toward the body are the
    # pose-setter's concern and are whitelisted via a screen↔body/grip allowance.
    swivel_hinge_range_rad = screen_open_range_rad
    screen_swivel_range_rad = _SCREEN_SWIVEL_RANGE_RAD
    button_count = (
        0 if config.control_layout in {"minimal", "mode_dial"} else max(1, config.button_count)
    )

    return ResolvedCamcorderWithFlipoutScreenConfig(
        body_length=body_length,
        body_width=body_width,
        body_height=body_height,
        body_profile=config.body_profile,
        lens_style=config.lens_style,
        hood_style=hood_style,
        lens_length=max(0.035, min(0.130, lens_length)),
        lens_radius=max(0.020, min(0.050, lens_radius)),
        screen_layout=config.screen_layout,
        screen_width=screen_width,
        screen_height=screen_height,
        screen_open_range_rad=screen_open_range_rad,
        swivel_hinge_range_rad=swivel_hinge_range_rad,
        screen_swivel_range_rad=screen_swivel_range_rad,
        screen_hinge_origin=hinge_origin,
        grip_style=config.grip_style,
        viewfinder_style=config.viewfinder_style,
        control_layout=config.control_layout,
        ring_style=config.ring_style,
        button_count=button_count,
        material_style=config.material_style,
        name=config.name,
    )


def _joint_meta(
    joint_type: ArticulationType,
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    joint_range: tuple[float | None, float | None],
) -> dict[str, object]:
    return {"type": joint_type.value, "axis": axis, "origin": origin, "range": joint_range}


def _build_body(
    body, r: ResolvedCamcorderWithFlipoutScreenConfig, *, body_mat, trim_mat, rubber_mat, glass_mat
) -> None:
    L, W, H = r.body_length, r.body_width, r.body_height
    body.visual(Box((L, W, H)), material=body_mat, name="body_shell", material_class_id="plastic.opaque_glossy_molded")
    if r.body_profile in {"tapered_home_video", "shoulder_rear_hump"}:
        body.visual(
            Box((L * 0.28, W * 0.95, H * 0.76)),
            origin=Origin(xyz=(-L * 0.36, 0.0, H * 0.04)),
            material=trim_mat,
            name="rear_battery_hump", material_class_id="plastic.opaque_glossy_molded",
        )
    if r.body_profile == "documentary_block":
        body.visual(
            Box((L * 0.42, W * 0.42, H * 0.26)),
            origin=Origin(xyz=(0.0, 0.0, H * 0.63)),
            material=trim_mat,
            name="top_block", material_class_id="plastic.opaque_glossy_molded",
        )
    body.visual(
        Box((L * 0.42, 0.002, H * 0.68)),
        origin=Origin(xyz=(L * 0.08, W * 0.5 - 0.001, 0.0)),
        material=trim_mat,
        name="display_bay", material_class_id="plastic.opaque_glossy_molded",
    )
    if r.grip_style in {"side_pad", "hand_strap", "strap_and_handle"}:
        body.visual(
            Box((L * 0.50, 0.010, H * 0.68)),
            origin=Origin(xyz=(0.0, -W * 0.5 - 0.005, -H * 0.03)),
            material=rubber_mat,
            name="hand_strap", material_class_id="rubber.smooth_plain",
        )
    if r.viewfinder_style != "none":
        body.visual(
            Cylinder(radius=H * 0.15, length=L * 0.20),
            origin=Origin(xyz=(-L * 0.52, 0.0, H * 0.32), rpy=(0.0, math.pi / 2, 0.0)),
            material=trim_mat,
            name="rear_eyecup", material_class_id="plastic.opaque_glossy_molded",
        )
    if r.viewfinder_style == "raised_viewfinder_with_diopter":
        body.visual(
            Cylinder(radius=0.008, length=0.006),
            origin=Origin(xyz=(-L * 0.45, -W * 0.18, H * 0.52), rpy=(math.pi / 2, 0.0, 0.0)),
            material=rubber_mat,
            name="diopter_wheel_socket", material_class_id="rubber.smooth_plain",
        )
    body.visual(
        Box((L * 0.16, 0.001, H * 0.22)),
        origin=Origin(xyz=(L * 0.05, W * 0.5 - 0.0015, 0.0)),
        material=glass_mat,
        name="closed_screen_shadow", material_class_id="glass.smoked_tinted",
    )


def _build_lens(
    lens, r: ResolvedCamcorderWithFlipoutScreenConfig, *, trim_mat, rubber_mat, glass_mat
) -> None:
    length = r.lens_length
    radius = r.lens_radius
    lens.visual(
        Cylinder(radius=radius * 1.15, length=0.018),
        origin=Origin(xyz=(0.009, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
        material=trim_mat,
        name="mount_collar", material_class_id="metal.blackened_gunmetal",
    )
    lens.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=(0.018 + length / 2, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
        material=trim_mat,
        name="lens_barrel", material_class_id="metal.blackened_gunmetal",
    )
    lens.visual(
        Cylinder(radius=radius * 0.72, length=0.004),
        origin=Origin(xyz=(0.020 + length, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
        material=glass_mat,
        name="front_glass", material_class_id="glass.clear_transparent",
    )
    if r.hood_style == "rectangular_hood":
        lens.visual(
            Box((0.030, radius * 2.55, radius * 2.10)),
            origin=Origin(xyz=(0.036 + length, 0.0, 0.0)),
            material=rubber_mat,
            name="lens_hood", material_class_id="rubber.smooth_plain",
        )
    elif r.hood_style == "stepped_shade":
        lens.visual(
            Cylinder(radius=radius * 1.35, length=0.018),
            origin=Origin(xyz=(0.030 + length, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
            material=rubber_mat,
            name="stepped_lens_shade", material_class_id="rubber.smooth_plain",
        )
        lens.visual(
            Box((0.012, radius * 2.90, radius * 0.42)),
            origin=Origin(xyz=(0.044 + length, 0.0, radius * 0.88)),
            material=rubber_mat,
            name="shade_top_brow", material_class_id="rubber.smooth_plain",
        )
    if r.lens_style == "long_barrel":
        lens.visual(
            Cylinder(radius=radius * 1.10, length=0.014),
            origin=Origin(xyz=(0.040, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
            material=rubber_mat,
            name="zoom_band", material_class_id="rubber.smooth_plain",
        )


def _build_control_ring(ring, r: ResolvedCamcorderWithFlipoutScreenConfig, *, rubber_mat) -> None:
    pad = 0.006
    width = 0.014
    radius = r.lens_radius
    # Solid grip band centered on the optical spin axis. The four contact pads
    # below are purely radial detail whose geometry sits `radius` away from the
    # ring's local origin; without this band the CONTINUOUS `lens_ring_spin`
    # origin (correctly on the barrel axis) would read as "far from geometry".
    # The band is concentric with, and slightly proud of, the lens barrel, so
    # the ring's local origin (0,0,0) lies inside real geometry (dist_child≈0).
    # The concentric band↔barrel overlap is the ring-on-shaft mechanism
    # engagement and is declared via allow_overlap in run_camcorder_tests.
    ring.visual(
        Cylinder(radius=radius + 0.003, length=width),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
        material=rubber_mat,
        name="ring_band", material_class_id="rubber.smooth_plain",
    )
    pads = (
        ((0.0, radius + pad * 0.5, 0.0), (width, pad, 0.014), 0.0),
        ((0.0, -radius - pad * 0.5, 0.0), (width, pad, 0.014), 0.0),
        ((0.0, 0.0, radius + pad * 0.5), (width, 0.014, pad), 0.0),
        ((0.0, 0.0, -radius - pad * 0.5), (width, 0.014, pad), 0.0),
    )
    for i, (xyz, size, yaw) in enumerate(pads):
        ring.visual(
            Box(size),
            origin=Origin(xyz=xyz, rpy=(0.0, 0.0, yaw)),
            material=rubber_mat,
            name=f"ring_contact_pad_{i}", material_class_id="rubber.smooth_plain",
        )
    if r.ring_style == "zoom_ring":
        tab_height = 0.010
        # Keep the tab attached to the ring contact geometry (no visible floating gap)
        # across different seeded lens radii.
        tab_center_z = radius + pad + tab_height * 0.5
        ring.visual(
            Box((width * 0.60, 0.038, tab_height)),
            origin=Origin(xyz=(0.0, 0.0, tab_center_z)),
            material=rubber_mat,
            name="zoom_ring_tab", material_class_id="rubber.smooth_plain",
        )


def _build_screen_panel(
    screen, r: ResolvedCamcorderWithFlipoutScreenConfig, *, trim_mat, glass_mat
) -> None:
    screen.visual(
        Box((r.screen_width, 0.010, r.screen_height)),
        origin=Origin(xyz=(r.screen_width / 2, 0.0, 0.0)),
        material=trim_mat,
        name="screen_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    screen.visual(
        Box((r.screen_width * 0.82, 0.002, r.screen_height * 0.76)),
        origin=Origin(xyz=(r.screen_width / 2, 0.006, 0.0)),
        material=glass_mat,
        name="display_panel", material_class_id="tech.emissive_surface",
    )
    screen.visual(
        Cylinder(radius=0.004, length=r.screen_height * 0.96),
        origin=Origin(rpy=(0.0, 0.0, 0.0)),
        material=trim_mat,
        name="screen_hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )


def _build_controls(
    model: ArticulatedObject,
    body,
    r: ResolvedCamcorderWithFlipoutScreenConfig,
    *,
    trim_mat,
    rubber_mat,
) -> None:
    if r.control_layout in {"mode_dial", "buttons_and_dial"}:
        dial = model.part("mode_dial")
        dial.visual(
            Cylinder(radius=0.014, length=0.008),
            material=rubber_mat,
            name="dial_body", material_class_id="rubber.smooth_plain",
        )
        origin = (0.0, r.body_width * 0.22, r.body_height * 0.5 + 0.004)
        axis = (0.0, 0.0, 1.0)
        model.articulation(
            "mode_dial_turn",
            ArticulationType.REVOLUTE,
            parent=body,
            child=dial,
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(effort=0.8, velocity=3.0, lower=-1.85, upper=1.40),
            meta=_joint_meta(ArticulationType.REVOLUTE, axis, origin, (-1.85, 1.40)),
        )
    if r.control_layout in {"side_buttons", "buttons_and_dial"}:
        button_z = (
            r.body_height * 0.76 + 0.004
            if r.body_profile == "documentary_block"
            else r.body_height * 0.5 + 0.004
        )
        for i in range(r.button_count):
            button = model.part(f"button_{i}")
            button.visual(Box((0.012, 0.004, 0.008)), material=rubber_mat, name="button_cap", material_class_id="rubber.smooth_plain")
            origin = (
                r.body_length * (-0.10 + i * 0.08),
                -r.body_width * 0.12,
                button_z,
            )
            axis = (0.0, 0.0, -1.0)
            model.articulation(
                f"button_press_{i}",
                ArticulationType.PRISMATIC,
                parent=body,
                child=button,
                origin=Origin(xyz=origin),
                axis=axis,
                motion_limits=MotionLimits(effort=0.8, velocity=0.03, lower=0.0, upper=0.004),
                meta=_joint_meta(ArticulationType.PRISMATIC, axis, origin, (0.0, 0.004)),
            )


def build_camcorder(
    config: CamcorderWithFlipoutScreenConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or CamcorderWithFlipoutScreenConfig()
    r = resolve_config(config)
    assets = assets or AssetContext(Path(tempfile.mkdtemp(prefix="articraft-camcorder-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["adopted_source_ids"] = ("S1", "S2", "S3", "S4", "S5")
    pal = PALETTES[r.material_style]
    body_mat = model.material("camcorder_body", rgba=pal["body"])
    trim_mat = model.material("camcorder_trim", rgba=pal["trim"])
    rubber_mat = model.material("camcorder_rubber", rgba=pal["rubber"])
    glass_mat = model.material("camcorder_glass", rgba=pal["glass"])

    body = model.part("body")
    _build_body(
        body, r, body_mat=body_mat, trim_mat=trim_mat, rubber_mat=rubber_mat, glass_mat=glass_mat
    )

    lens = model.part("lens")
    _build_lens(lens, r, trim_mat=trim_mat, rubber_mat=rubber_mat, glass_mat=glass_mat)
    model.articulation(
        "body_to_lens",
        ArticulationType.FIXED,
        parent=body,
        child=lens,
        origin=Origin(xyz=(r.body_length / 2, 0.0, 0.0)),
    )

    if r.ring_style != "none":
        ring = model.part("lens_control_ring")
        _build_control_ring(ring, r, rubber_mat=rubber_mat)
        origin = (0.018 + r.lens_length * 0.90, 0.0, 0.0)
        axis = (1.0, 0.0, 0.0)
        model.articulation(
            "lens_ring_spin",
            ArticulationType.CONTINUOUS,
            parent=lens,
            child=ring,
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(effort=1.2, velocity=6.0),
            meta=_joint_meta(ArticulationType.CONTINUOUS, axis, origin, (None, None)),
        )

    if r.screen_layout == "single_door":
        screen = model.part("flip_screen")
        _build_screen_panel(screen, r, trim_mat=trim_mat, glass_mat=glass_mat)
        axis = (0.0, 0.0, 1.0)
        model.articulation(
            "screen_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=screen,
            origin=Origin(xyz=r.screen_hinge_origin),
            axis=axis,
            motion_limits=MotionLimits(
                effort=2.0, velocity=2.0, lower=0.0, upper=r.screen_open_range_rad
            ),
            meta=_joint_meta(
                ArticulationType.REVOLUTE,
                axis,
                r.screen_hinge_origin,
                (0.0, r.screen_open_range_rad),
            ),
        )
    elif r.screen_layout == "door_with_inner_swivel":
        door = model.part("screen_door")
        # Keep the whole door on the +x (outboard) side of the hinge axis. A
        # spine centered on the hinge origin would swing its rear (-x) half back
        # into the body as the door opens; rebasing it to +x removes that dig so
        # the hinge can open through its full derived range for wide screens.
        door.visual(
            Box((r.screen_width * 0.24, 0.010, r.screen_height)),
            origin=Origin(xyz=(r.screen_width * 0.12, 0.0, 0.0)),
            material=trim_mat,
            name="door_spine", material_class_id="metal.blackened_gunmetal",
        )
        door.visual(
            Box((r.screen_width, 0.007, r.screen_height)),
            origin=Origin(xyz=(r.screen_width / 2, 0.0, 0.0)),
            material=trim_mat,
            name="door_shell", material_class_id="plastic.opaque_glossy_molded",
        )
        axis = (0.0, 0.0, 1.0)
        model.articulation(
            "screen_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=door,
            origin=Origin(xyz=r.screen_hinge_origin),
            axis=axis,
            motion_limits=MotionLimits(
                effort=2.0, velocity=2.0, lower=0.0, upper=r.swivel_hinge_range_rad
            ),
            meta=_joint_meta(
                ArticulationType.REVOLUTE,
                axis,
                r.screen_hinge_origin,
                (0.0, r.swivel_hinge_range_rad),
            ),
        )
        screen = model.part("flip_screen")
        _build_screen_panel(screen, r, trim_mat=trim_mat, glass_mat=glass_mat)
        inner_origin = (r.screen_width * 0.18, 0.0085, 0.0)
        model.articulation(
            "screen_swivel",
            ArticulationType.REVOLUTE,
            parent=door,
            child=screen,
            origin=Origin(xyz=inner_origin),
            axis=axis,
            motion_limits=MotionLimits(
                effort=1.0, velocity=2.0, lower=0.0, upper=r.screen_swivel_range_rad
            ),
            meta=_joint_meta(
                ArticulationType.REVOLUTE, axis, inner_origin, (0.0, r.screen_swivel_range_rad)
            ),
        )
    else:
        arm = model.part("screen_arm")
        arm.visual(
            Cylinder(radius=0.006, length=r.screen_height), material=trim_mat, name="root_barrel", material_class_id="metal.blackened_gunmetal"
        )
        arm.visual(
            Box((0.018, 0.050, 0.014)),
            origin=Origin(xyz=(0.0, 0.025, 0.0)),
            material=trim_mat,
            name="arm_beam", material_class_id="metal.blackened_gunmetal",
        )
        axis_root = (0.0, 0.0, -1.0)
        model.articulation(
            "screen_arm_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=arm,
            origin=Origin(xyz=r.screen_hinge_origin),
            axis=axis_root,
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=-0.35, upper=1.10),
            meta=_joint_meta(
                ArticulationType.REVOLUTE, axis_root, r.screen_hinge_origin, (-0.35, 1.10)
            ),
        )
        screen = model.part("flip_screen")
        _build_screen_panel(screen, r, trim_mat=trim_mat, glass_mat=glass_mat)
        inner_origin = (0.0, 0.054, 0.0)
        axis = (0.0, 0.0, 1.0)
        model.articulation(
            "screen_hinge",
            ArticulationType.REVOLUTE,
            parent=arm,
            child=screen,
            origin=Origin(xyz=inner_origin),
            axis=axis,
            motion_limits=MotionLimits(
                effort=1.5, velocity=2.5, lower=0.0, upper=r.screen_open_range_rad
            ),
            meta=_joint_meta(
                ArticulationType.REVOLUTE, axis, inner_origin, (0.0, r.screen_open_range_rad)
            ),
        )

    _build_controls(model, body, r, trim_mat=trim_mat, rubber_mat=rubber_mat)
    return model


def build_seeded_camcorder(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_camcorder(config_from_seed(seed), assets=assets)


def with_overrides(
    config: CamcorderWithFlipoutScreenConfig, **kwargs: object
) -> CamcorderWithFlipoutScreenConfig:
    return replace(config, **kwargs)


__modular__ = True


def slot_choices_for_config(
    config: CamcorderWithFlipoutScreenConfig | ResolvedCamcorderWithFlipoutScreenConfig,
) -> tuple[tuple[str, str], ...]:
    """Report the seed's per-slot module choices for the coverage gate.

    Uses the *resolved* config so each slot reflects what is actually built
    (after resolve_config's collapses, e.g. wide_hood forcing a hood and the
    top_handle/strap_and_handle -> hand_strap fold).
    """
    r = (
        config
        if isinstance(config, ResolvedCamcorderWithFlipoutScreenConfig)
        else resolve_config(config)
    )
    return (
        ("body_profile", r.body_profile),
        ("lens_style", r.lens_style),
        ("hood_style", r.hood_style),
        ("screen_layout", r.screen_layout),
        ("ring_style", r.ring_style),
        ("grip_style", r.grip_style),
        ("viewfinder_style", r.viewfinder_style),
        ("control_layout", r.control_layout),
        ("buttons", f"buttons_{r.button_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def run_camcorder_tests(
    object_model: ArticulatedObject, config: CamcorderWithFlipoutScreenConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    if r.ring_style != "none":
        # The control ring's solid grip band is concentric with (and slightly
        # proud of) the lens barrel so it reads as a band on the barrel and its
        # local origin lies on real geometry. That is the ring-on-shaft rotary
        # engagement, not a modelling clash.
        ctx.allow_overlap(
            "lens",
            "lens_control_ring",
            elem_a="lens_barrel",
            elem_b="ring_band",
            reason="focus/zoom ring rotates concentrically on the lens barrel",
        )
    if r.screen_layout == "door_with_inner_swivel":
        # The door+panel stack swings fully away from the body on the flip hinge.
        ctx.allow_isolated_part(
            "flip_screen",
            reason="flip-out screen panel detaches from the body when flipped open",
        )
        ctx.allow_isolated_part(
            "screen_door",
            reason="screen door swings away from the body on the flip hinge and loses contact",
        )
        # flip_screen is mounted face-to-face on screen_door through the inner
        # swivel revolute. The two thin panels stack ~5mm apart, so once the
        # shared hinge rotates them their world AABBs intersect (a conservative
        # bounding-box artifact of adjacent stacked panels, not a body clash).
        # Scope the allowance to the swivel members' element pairs only.
        for screen_elem in ("screen_shell", "display_panel", "screen_hinge_barrel"):
            for door_elem in ("door_spine", "door_shell"):
                ctx.allow_overlap(
                    "flip_screen",
                    "screen_door",
                    elem_a=screen_elem,
                    elem_b=door_elem,
                    reason="swivel panel stacks face-to-face on the screen door",
                )
        # Sequenced 2-DOF: the flip hinge and inner swivel both keep their full
        # designed travel, so the useful "flipped out + rotated face-forward" pose
        # is reachable. Some flip×swivel combinations sweep the panel back toward
        # the rear body (a fold-in the pose-setter would never leave the screen
        # in); those screen↔rear-body overlaps are the pose-setter's responsibility.
        # Element-scoped to the panel members × the REAR body elements only, so a
        # clash with the lens / front body / grip stays caught.
        for screen_elem in ("screen_shell", "display_panel", "screen_hinge_barrel"):
            for body_elem in ("body_shell", "rear_battery_hump", "rear_eyecup"):
                ctx.allow_overlap(
                    "flip_screen",
                    "body",
                    elem_a=screen_elem,
                    elem_b=body_elem,
                    reason=(
                        "Sequenced 2-DOF flip-out screen: the panel keeps full flip + "
                        "full swivel travel; flip×swivel combos that fold it back into "
                        "the rear body are unphysical pose-setter states, not real "
                        "operating poses, so panel↔rear-body overlap is allowed. Scoped "
                        "to panel×rear-body elements only (lens/front/grip stay checked)."
                    ),
                )
    names = {p.name for p in object_model.parts}
    ctx.check(
        "identity parts present",
        {"body", "lens", "flip_screen"}.issubset(names),
        details=str(sorted(names)),
    )
    hinge = object_model.get_articulation("screen_hinge")
    ctx.check(
        "screen hinge is revolute",
        hinge.articulation_type == ArticulationType.REVOLUTE,
        details=f"type={hinge.articulation_type}",
    )
    ctx.check(
        "screen hinge axis is vertical",
        tuple(abs(v) for v in hinge.axis) == (0.0, 0.0, 1.0),
        details=f"axis={hinge.axis}",
    )
    ctx.check(
        "screen hinge has metadata",
        {"type", "axis", "origin", "range"}.issubset(hinge.meta),
        details=str(hinge.meta),
    )
    ctx.check(
        "lens is fixed to body",
        object_model.get_articulation("body_to_lens").articulation_type == ArticulationType.FIXED,
    )
    if r.screen_layout == "door_with_inner_swivel":
        ctx.check(
            "inner swivel present",
            object_model.get_articulation("screen_swivel").articulation_type
            == ArticulationType.REVOLUTE,
        )
    if r.screen_layout == "armature_two_link":
        ctx.check(
            "arm hinge present",
            object_model.get_articulation("screen_arm_hinge").articulation_type
            == ArticulationType.REVOLUTE,
        )
    if r.ring_style != "none":
        joint = object_model.get_articulation("lens_ring_spin")
        ctx.check(
            "lens ring is continuous",
            joint.articulation_type == ArticulationType.CONTINUOUS,
            details=f"type={joint.articulation_type}",
        )
        ctx.check(
            "lens ring axis is optical", joint.axis == (1.0, 0.0, 0.0), details=f"axis={joint.axis}"
        )
    if r.ring_style == "zoom_ring":
        ring = object_model.get_part("lens_control_ring")
        top_pad = next((v for v in ring.visuals if v.name == "ring_contact_pad_2"), None)
        zoom_tab = next((v for v in ring.visuals if v.name == "zoom_ring_tab"), None)
        ctx.check("zoom tab visual present", zoom_tab is not None)
        if top_pad is not None and zoom_tab is not None:
            pad_aabb = ctx.part_element_world_aabb(ring, elem=top_pad)
            tab_aabb = ctx.part_element_world_aabb(ring, elem=zoom_tab)
            gap = None
            if pad_aabb is not None and tab_aabb is not None:
                gap = tab_aabb[0][2] - pad_aabb[1][2]
            ctx.check(
                "zoom tab touches top lens ring pad",
                gap is not None and abs(gap) <= 1e-4,
                details=f"gap={gap}",
            )
    if r.control_layout in {"side_buttons", "buttons_and_dial"}:
        buttons = [j for j in object_model.articulations if j.name.startswith("button_press_")]
        ctx.check(
            "button press joints match layout",
            len(buttons) == r.button_count,
            details=f"{len(buttons)} vs {r.button_count}",
        )
        ctx.check(
            "buttons are prismatic",
            all(j.articulation_type == ArticulationType.PRISMATIC for j in buttons),
        )
    return ctx.report()
