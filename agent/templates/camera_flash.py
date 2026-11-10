# SPDX-License-Identifier: Apache-2.0

"""Procedural template for category `camera_flash`."""

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

BodyProfile = Literal["compact_stepped", "tall_control_body", "narrow_speedlight"]
NeckStyle = Literal["short_neck", "trunnion_yoke", "side_yoke_arms"]
HeadShape = Literal["boxy_speedlight", "wide_professional", "rounded_rect_bezel"]
DiffuserStyle = Literal["flat_panel", "bezel_plus_lens", "fresnel_face"]
ControlLayout = Literal["screen_only", "dial", "button_bank", "screen_dial_buttons"]
MountStyle = Literal["plate_only", "rails_shoe_block", "contact_lock_ring"]
MaterialStyle = Literal["black", "graphite", "pro_grey"]

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "black": {
        "body": (0.04, 0.04, 0.045, 1.0),
        "trim": (0.12, 0.12, 0.13, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "diffuser": (0.88, 0.86, 0.78, 0.62),
        "metal": (0.62, 0.63, 0.62, 1.0),
    },
    "graphite": {
        "body": (0.18, 0.19, 0.20, 1.0),
        "trim": (0.08, 0.09, 0.10, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
        "diffuser": (0.82, 0.88, 0.92, 0.58),
        "metal": (0.52, 0.54, 0.55, 1.0),
    },
    "pro_grey": {
        "body": (0.34, 0.35, 0.34, 1.0),
        "trim": (0.16, 0.16, 0.16, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
        "diffuser": (0.93, 0.90, 0.78, 0.62),
        "metal": (0.70, 0.70, 0.68, 1.0),
    },
}


@dataclass(frozen=True)
class CameraFlashConfig:
    body_height: float = 0.125
    body_width: float = 0.060
    body_depth: float = 0.048
    body_profile: BodyProfile = "compact_stepped"
    neck_style: NeckStyle = "short_neck"
    head_width: float = 0.078
    head_depth: float = 0.060
    head_height: float = 0.048
    head_shape: HeadShape = "boxy_speedlight"
    diffuser_style: DiffuserStyle = "fresnel_face"
    bounce_card_enabled: bool = True
    bounce_card_travel: float = 0.024
    battery_door_enabled: bool = False
    battery_door_range_deg: float = 100.0
    control_layout: ControlLayout = "screen_dial_buttons"
    mount_style: MountStyle = "contact_lock_ring"
    head_tilt_range_deg: float = 90.0
    yaw_range_deg: float = 155.0
    material_style: MaterialStyle = "black"
    name: str = "reference_camera_flash"


@dataclass(frozen=True)
class ResolvedCameraFlashConfig:
    body_height: float
    body_width: float
    body_depth: float
    body_profile: BodyProfile
    neck_style: NeckStyle
    head_width: float
    head_depth: float
    head_height: float
    head_shape: HeadShape
    diffuser_style: DiffuserStyle
    bounce_card_enabled: bool
    bounce_card_travel: float
    battery_door_enabled: bool
    battery_door_range_rad: float
    control_layout: ControlLayout
    mount_style: MountStyle
    head_tilt_range_rad: float
    yaw_range_rad: float
    neck_origin: tuple[float, float, float]
    head_origin: tuple[float, float, float]
    material_style: MaterialStyle
    name: str


def config_from_seed(seed: int) -> CameraFlashConfig:
    rng = random.Random(seed)
    profile: BodyProfile = rng.choice(("compact_stepped", "tall_control_body", "narrow_speedlight"))
    neck: NeckStyle = rng.choice(("short_neck", "trunnion_yoke", "side_yoke_arms"))
    head_shape: HeadShape = rng.choice(
        ("boxy_speedlight", "wide_professional", "rounded_rect_bezel")
    )
    return CameraFlashConfig(
        body_height=round(rng.uniform(0.105, 0.165), 3),
        body_width=round(rng.uniform(0.050, 0.074), 3),
        body_depth=round(rng.uniform(0.040, 0.060), 3),
        body_profile=profile,
        neck_style=neck,
        head_width=round(rng.uniform(0.068, 0.112), 3),
        head_depth=round(rng.uniform(0.052, 0.085), 3),
        head_height=round(rng.uniform(0.040, 0.065), 3),
        head_shape=head_shape,
        diffuser_style=rng.choice(("flat_panel", "bezel_plus_lens", "fresnel_face")),
        bounce_card_enabled=rng.random() < 0.65,
        bounce_card_travel=round(rng.uniform(0.020, 0.045), 3),
        battery_door_enabled=rng.random() < 0.35,
        battery_door_range_deg=round(rng.uniform(80.0, 110.0), 1),
        control_layout=rng.choice(("screen_only", "dial", "button_bank", "screen_dial_buttons")),
        mount_style=rng.choice(("plate_only", "rails_shoe_block", "contact_lock_ring")),
        head_tilt_range_deg=round(rng.uniform(75.0, 105.0), 1),
        yaw_range_deg=round(rng.uniform(120.0, 180.0), 1),
        material_style=rng.choice(("black", "graphite", "pro_grey")),
        name=f"seeded_camera_flash_{seed}",
    )


def resolve_config(config: CameraFlashConfig) -> ResolvedCameraFlashConfig:
    if config.body_profile not in {"compact_stepped", "tall_control_body", "narrow_speedlight"}:
        raise ValueError(f"Unsupported body_profile: {config.body_profile}")
    if config.neck_style not in {"short_neck", "trunnion_yoke", "side_yoke_arms"}:
        raise ValueError(f"Unsupported neck_style: {config.neck_style}")
    if config.head_shape not in {"boxy_speedlight", "wide_professional", "rounded_rect_bezel"}:
        raise ValueError(f"Unsupported head_shape: {config.head_shape}")
    if config.diffuser_style not in {"flat_panel", "bezel_plus_lens", "fresnel_face"}:
        raise ValueError(f"Unsupported diffuser_style: {config.diffuser_style}")
    if config.control_layout not in {"screen_only", "dial", "button_bank", "screen_dial_buttons"}:
        raise ValueError(f"Unsupported control_layout: {config.control_layout}")
    if config.mount_style not in {"plate_only", "rails_shoe_block", "contact_lock_ring"}:
        raise ValueError(f"Unsupported mount_style: {config.mount_style}")
    if not isinstance(config.bounce_card_enabled, bool):
        raise ValueError("bounce_card_enabled must be bool")
    if not isinstance(config.battery_door_enabled, bool):
        raise ValueError("battery_door_enabled must be bool")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    body_h = max(0.090, min(0.180, config.body_height))
    body_w = max(0.045, min(0.085, config.body_width))
    body_d = max(0.035, min(0.070, config.body_depth))
    head_w = max(0.060, min(0.125, config.head_width))
    if config.head_shape == "wide_professional":
        head_w = max(head_w, body_w * 1.55)
    return ResolvedCameraFlashConfig(
        body_height=body_h,
        body_width=body_w,
        body_depth=body_d,
        body_profile=config.body_profile,
        neck_style=config.neck_style,
        head_width=head_w,
        head_depth=max(0.046, min(0.095, config.head_depth)),
        head_height=max(0.036, min(0.075, config.head_height)),
        head_shape=config.head_shape,
        diffuser_style=config.diffuser_style,
        bounce_card_enabled=config.bounce_card_enabled,
        bounce_card_travel=max(0.012, min(0.055, config.bounce_card_travel)),
        battery_door_enabled=config.battery_door_enabled,
        battery_door_range_rad=math.radians(max(45.0, min(125.0, config.battery_door_range_deg))),
        control_layout=config.control_layout,
        mount_style=config.mount_style,
        head_tilt_range_rad=math.radians(max(55.0, min(120.0, config.head_tilt_range_deg))),
        yaw_range_rad=math.radians(max(60.0, min(180.0, config.yaw_range_deg))),
        neck_origin=(0.0, 0.0, body_h + 0.010),
        head_origin=(
            0.0,
            0.0,
            {
                "short_neck": 0.039,
                "trunnion_yoke": 0.037,
                "side_yoke_arms": 0.050,
            }[config.neck_style],
        ),
        material_style=config.material_style,
        name=config.name,
    )


def _joint_meta(joint_type: ArticulationType, axis, origin, joint_range) -> dict[str, object]:
    return {"type": joint_type.value, "axis": axis, "origin": origin, "range": joint_range}


def _build_body(
    body, r: ResolvedCameraFlashConfig, *, body_mat, trim_mat, metal_mat, rubber_mat, glass_mat
) -> None:
    body.visual(
        Box((r.body_width, r.body_depth, r.body_height)),
        origin=Origin(xyz=(0.0, 0.0, r.body_height / 2)),
        material=body_mat,
        name="body_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((r.body_width * 0.82, r.body_depth * 0.92, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, r.body_height)),
        material=trim_mat,
        name="swivel_socket", material_class_id="plastic.opaque_generic",
    )
    if r.body_profile == "tall_control_body":
        body.visual(
            Box((0.003, r.body_depth * 0.82, r.body_height * 0.66)),
            origin=Origin(xyz=(-r.body_width * 0.5 - 0.0015, 0.0, r.body_height * 0.47)),
            material=trim_mat,
            name="rear_control_panel", material_class_id="plastic.opaque_generic",
        )
    # Hotshoe mount variants from the adopted source snippets.
    body.visual(
        Box((r.body_width * 0.95, r.body_depth * 1.10, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, -0.003)),
        material=metal_mat,
        name="hotshoe_plate", material_class_id="metal.stainless_matte",
    )
    if r.mount_style in {"rails_shoe_block", "contact_lock_ring"}:
        for i, y in enumerate((-r.body_depth * 0.44, r.body_depth * 0.44)):
            body.visual(
                Box((r.body_width * 0.86, 0.004, 0.008)),
                origin=Origin(xyz=(0.0, y, 0.006)),
                material=metal_mat,
                name=f"hotshoe_rail_{i}", material_class_id="metal.stainless_matte",
            )
        body.visual(
            Box((r.body_width * 0.65, r.body_depth * 0.70, 0.010)),
            origin=Origin(xyz=(0.0, 0.0, 0.012)),
            material=trim_mat,
            name="shoe_block", material_class_id="plastic.opaque_generic",
        )
    if r.mount_style == "contact_lock_ring":
        body.visual(
            Cylinder(radius=r.body_width * 0.26, length=0.006),
            origin=Origin(xyz=(0.0, 0.0, 0.024)),
            material=metal_mat,
            name="lock_ring", material_class_id="metal.stainless_matte",
        )
    body.visual(
        Box((0.002, r.body_depth * 0.56, r.body_height * 0.16)),
        origin=Origin(xyz=(-r.body_width * 0.5 - 0.001, 0.0, r.body_height * 0.74)),
        material=glass_mat,
        name="rear_lcd", material_class_id="glass.smoked_tinted",
    )


def _build_neck(neck, r: ResolvedCameraFlashConfig, *, trim_mat) -> None:
    neck.visual(
        Cylinder(radius=r.body_width * 0.28, length=0.010), material=trim_mat, name="swivel_disk", material_class_id="plastic.opaque_generic"
    )
    if r.neck_style == "short_neck":
        neck.visual(
            Box((r.body_width * 0.42, r.body_depth * 0.36, 0.0277)),
            origin=Origin(xyz=(0.0, 0.0, 0.01785)),
            material=trim_mat,
            name="short_upright", material_class_id="plastic.opaque_generic",
        )
    elif r.neck_style == "trunnion_yoke":
        neck.visual(
            Box((r.head_width * 0.96, r.body_depth * 0.46, 0.0253)),
            origin=Origin(xyz=(0.0, 0.0, 0.01665)),
            material=trim_mat,
            name="trunnion_block", material_class_id="plastic.opaque_generic",
        )
        for i, x in enumerate((-r.head_width * 0.48, r.head_width * 0.48)):
            neck.visual(
                Cylinder(radius=0.009, length=0.012),
                origin=Origin(xyz=(x, 0.0, 0.035), rpy=(0.0, math.pi / 2, 0.0)),
                material=trim_mat,
                name=f"trunnion_boss_{i}", material_class_id="plastic.opaque_generic",
            )
    else:
        neck.visual(
            Box((r.body_width * 0.36, r.body_depth * 0.30, 0.025)),
            origin=Origin(xyz=(0.0, 0.0, 0.0165)),
            material=trim_mat,
            name="yoke_pedestal", material_class_id="plastic.opaque_generic",
        )
        neck.visual(
            Box((r.head_width * 1.08, r.body_depth * 0.26, 0.020)),
            origin=Origin(xyz=(0.0, 0.0, 0.022)),
            material=trim_mat,
            name="rear_bridge", material_class_id="plastic.opaque_generic",
        )
        for i, x in enumerate((-r.head_width * 0.54, r.head_width * 0.54)):
            neck.visual(
                Box((0.014, r.body_depth * 0.32, 0.070)),
                origin=Origin(xyz=(x, 0.0, 0.050)),
                material=trim_mat,
                name=f"yoke_arm_{i}", material_class_id="plastic.opaque_generic",
            )


def _build_head(head, r: ResolvedCameraFlashConfig, *, body_mat, trim_mat, diffuser_mat) -> None:
    # Five-star camera-flash samples seat the head around the tilt axis: the
    # rear of the flash body overlaps the yoke cheeks instead of floating in
    # front of a purely mathematical revolute origin.
    neck_front_y = r.body_depth * 0.23
    head_center_y = neck_front_y + r.head_depth * 0.5 + 0.003
    head_rear_y = head_center_y - r.head_depth * 0.5
    head_front_y = head_center_y + r.head_depth * 0.5
    diffuser_y = head_front_y + 0.001
    head.visual(
        Box((r.head_width, r.head_depth, r.head_height)),
        origin=Origin(xyz=(0.0, head_center_y, 0.0)),
        material=body_mat,
        name="head_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    tilt_barrel_length = r.head_width * (0.78 if r.neck_style == "trunnion_yoke" else 0.92)
    tilt_barrel_radius = max(0.006, r.head_height * 0.17)
    head.visual(
        Cylinder(
            radius=tilt_barrel_radius,
            length=tilt_barrel_length,
        ),
        origin=Origin(rpy=(0.0, math.pi / 2, 0.0)),
        material=trim_mat,
        name="tilt_barrel", material_class_id="plastic.opaque_generic",
    )
    bridge_depth = head_rear_y + 0.010
    head.visual(
        Box((r.head_width * 0.34, bridge_depth, r.head_height * 0.28)),
        origin=Origin(xyz=(0.0, bridge_depth * 0.5, 0.0)),
        material=trim_mat,
        name="tilt_barrel_to_head_bridge", material_class_id="plastic.opaque_generic",
    )
    if r.head_shape == "wide_professional":
        head.visual(
            Box((r.head_width * 1.04, r.head_depth * 0.18, r.head_height * 0.26)),
            origin=Origin(xyz=(0.0, head_front_y - r.head_depth * 0.12, r.head_height * 0.20)),
            material=trim_mat,
            name="card_slot_rail", material_class_id="plastic.opaque_generic",
        )
    if r.bounce_card_enabled:
        guide_height = r.bounce_card_travel + 0.004
        head.visual(
            Box((r.head_width * 0.50, 0.003, guide_height)),
            origin=Origin(
                xyz=(
                    0.0,
                    r.head_depth * 0.90 - 0.003,
                    r.head_height * 0.50 + r.bounce_card_travel * 0.50,
                )
            ),
            material=trim_mat,
            name="bounce_card_guide",
            material_class_id="plastic.opaque_generic",
        )
    if r.head_shape == "rounded_rect_bezel":
        head.visual(
            Box((r.head_width * 0.90, 0.006, r.head_height * 0.84)),
            origin=Origin(xyz=(0.0, head_front_y + 0.003, 0.0)),
            material=trim_mat,
            name="rounded_front_bezel", material_class_id="plastic.opaque_generic",
        )
    head.visual(
        Box((r.head_width * 0.82, 0.004, r.head_height * 0.70)),
        origin=Origin(xyz=(0.0, diffuser_y, 0.0)),
        material=diffuser_mat,
        name="front_diffuser", material_class_id="plastic.frosted_translucent",
    )
    if r.diffuser_style == "fresnel_face":
        for i in range(5):
            z = -r.head_height * 0.26 + i * r.head_height * 0.13
            head.visual(
                Box((r.head_width * 0.70, 0.002, 0.002)),
                origin=Origin(xyz=(0.0, head_front_y + 0.004, z)),
                material=trim_mat,
                name=f"fresnel_line_{i}", material_class_id="plastic.opaque_generic",
            )
    elif r.diffuser_style == "bezel_plus_lens":
        head.visual(
            Box((r.head_width * 0.55, 0.003, r.head_height * 0.38)),
            origin=Origin(xyz=(0.0, head_front_y + 0.003, 0.0)),
            material=diffuser_mat,
            name="inner_lens_panel", material_class_id="plastic.frosted_translucent",
        )
    saddle_center_z = (
        {
            "short_neck": 0.0317,
            "trunnion_yoke": 0.0293,
            "side_yoke_arms": 0.032,
        }[r.neck_style]
        + 0.001
        - r.head_origin[2]
    )
    saddle_bottom_z = saddle_center_z - 0.003
    saddle_top_z = max(saddle_center_z + 0.003, -tilt_barrel_radius + 0.001)
    head.visual(
        Box((r.head_width * 0.36, 0.010, saddle_top_z - saddle_bottom_z)),
        origin=Origin(xyz=(0.0, 0.0, (saddle_bottom_z + saddle_top_z) * 0.5)),
        material=trim_mat,
        name="tilt_saddle_contact", material_class_id="plastic.opaque_generic",
    )
    if r.neck_style == "short_neck":
        cap_length = 0.014
        cap_center_x = tilt_barrel_length * 0.5 + cap_length * 0.5 - 0.001
        for i, side in enumerate((-1.0, 1.0)):
            head.visual(
                Cylinder(radius=max(0.006, r.head_height * 0.15), length=cap_length),
                origin=Origin(xyz=(side * cap_center_x, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
                material=trim_mat,
                name=f"tilt_axis_cap_{i}", material_class_id="plastic.opaque_generic",
            )


def build_camera_flash(
    config: CameraFlashConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or CameraFlashConfig()
    r = resolve_config(config)
    assets = assets or AssetContext(Path(tempfile.mkdtemp(prefix="articraft-camera-flash-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["adopted_source_ids"] = ("S1", "S2", "S3", "S4")
    pal = PALETTES[r.material_style]
    body_mat = model.material("flash_body", rgba=pal["body"])
    trim_mat = model.material("flash_trim", rgba=pal["trim"])
    rubber_mat = model.material("flash_rubber", rgba=pal["rubber"])
    diffuser_mat = model.material("flash_diffuser", rgba=pal["diffuser"])
    metal_mat = model.material("flash_metal", rgba=pal["metal"])

    body = model.part("body")
    _build_body(
        body,
        r,
        body_mat=body_mat,
        trim_mat=trim_mat,
        metal_mat=metal_mat,
        rubber_mat=rubber_mat,
        glass_mat=diffuser_mat,
    )
    neck = model.part("neck")
    _build_neck(neck, r, trim_mat=trim_mat)
    head = model.part("head")
    _build_head(head, r, body_mat=body_mat, trim_mat=trim_mat, diffuser_mat=diffuser_mat)

    yaw_axis = (0.0, 0.0, 1.0)
    model.articulation(
        "body_to_neck_yaw",
        ArticulationType.REVOLUTE,
        parent=body,
        child=neck,
        origin=Origin(xyz=r.neck_origin),
        axis=yaw_axis,
        motion_limits=MotionLimits(
            effort=4.0, velocity=2.0, lower=-r.yaw_range_rad, upper=r.yaw_range_rad
        ),
        meta=_joint_meta(
            ArticulationType.REVOLUTE, yaw_axis, r.neck_origin, (-r.yaw_range_rad, r.yaw_range_rad)
        ),
    )
    tilt_axis = (1.0, 0.0, 0.0)
    model.articulation(
        "neck_to_head_tilt",
        ArticulationType.REVOLUTE,
        parent=neck,
        child=head,
        origin=Origin(xyz=r.head_origin),
        axis=tilt_axis,
        motion_limits=MotionLimits(
            effort=4.0, velocity=2.0, lower=-0.20, upper=r.head_tilt_range_rad
        ),
        meta=_joint_meta(
            ArticulationType.REVOLUTE, tilt_axis, r.head_origin, (-0.20, r.head_tilt_range_rad)
        ),
    )

    if r.bounce_card_enabled:
        card = model.part("bounce_card")
        card.visual(
            Box((r.head_width * 0.46, 0.003, r.head_height * 0.72)),
            origin=Origin(xyz=(0.0, 0.0, r.head_height * 0.36)),
            material=diffuser_mat,
            name="card_panel", material_class_id="plastic.frosted_translucent",
        )
        origin = (0.0, r.head_depth * 0.90, r.head_height * 0.50)
        axis = (0.0, 0.0, 1.0)
        model.articulation(
            "bounce_card_slide",
            ArticulationType.PRISMATIC,
            parent=head,
            child=card,
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(
                effort=1.0, velocity=0.08, lower=0.0, upper=r.bounce_card_travel
            ),
            meta=_joint_meta(ArticulationType.PRISMATIC, axis, origin, (0.0, r.bounce_card_travel)),
        )

    if r.battery_door_enabled:
        door = model.part("battery_door")
        door.visual(
            Box((0.004, r.body_depth * 0.78, r.body_height * 0.46)),
            origin=Origin(xyz=(0.002, r.body_depth * 0.39, 0.0)),
            material=body_mat,
            name="door_panel", material_class_id="plastic.opaque_glossy_molded",
        )
        door.visual(
            Cylinder(radius=0.003, length=r.body_height * 0.50),
            material=trim_mat,
            name="door_hinge_barrel", material_class_id="plastic.opaque_generic",
        )
        for i, z in enumerate((-0.12, 0.0, 0.12)):
            door.visual(
                Box((0.001, r.body_depth * 0.28, 0.002)),
                origin=Origin(xyz=(0.004, r.body_depth * 0.36, z * r.body_height)),
                material=rubber_mat,
                name=f"door_grip_rib_{i}", material_class_id="rubber.directional_grooved",
            )
        hinge_y = -r.body_depth * 0.42
        origin = (r.body_width * 0.52, 0.0, r.body_height * 0.48)
        origin = (origin[0], hinge_y, origin[2])
        axis = (0.0, 0.0, -1.0)
        model.articulation(
            "battery_door_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=door,
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(
                effort=1.0, velocity=1.3, lower=0.0, upper=r.battery_door_range_rad
            ),
            meta=_joint_meta(
                ArticulationType.REVOLUTE, axis, origin, (0.0, r.battery_door_range_rad)
            ),
        )

    if r.control_layout in {"dial", "screen_dial_buttons"}:
        dial = model.part("rear_dial")
        dial.visual(
            Cylinder(radius=0.014, length=0.006),
            origin=Origin(rpy=(0.0, math.pi / 2, 0.0)),
            material=rubber_mat,
            name="dial_wheel", material_class_id="rubber.directional_grooved",
        )
        rear_panel_thickness = 0.003 if r.body_profile == "tall_control_body" else 0.0
        origin = (-r.body_width * 0.5 - rear_panel_thickness - 0.003, 0.0, r.body_height * 0.38)
        axis = (-1.0, 0.0, 0.0)
        model.articulation(
            "rear_dial_turn",
            ArticulationType.REVOLUTE,
            parent=body,
            child=dial,
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(effort=0.5, velocity=3.0, lower=-math.pi, upper=math.pi),
            meta=_joint_meta(ArticulationType.REVOLUTE, axis, origin, (-math.pi, math.pi)),
        )
    if r.control_layout in {"button_bank", "screen_dial_buttons"}:
        button_zs = (
            (r.body_height * 0.22, r.body_height * 0.54, r.body_height * 0.70)
            if r.control_layout == "screen_dial_buttons"
            else (r.body_height * 0.24, r.body_height * 0.38, r.body_height * 0.52)
        )
        for i, z in enumerate(button_zs):
            button = model.part(f"button_{i}")
            button.visual(Box((0.004, 0.014, 0.008)), material=rubber_mat, name="button_cap", material_class_id="rubber.smooth_plain")
            rear_panel_thickness = 0.003 if r.body_profile == "tall_control_body" else 0.0
            origin = (
                -r.body_width * 0.5 - rear_panel_thickness - 0.002,
                r.body_depth * (-0.22 + i * 0.22),
                z,
            )
            axis = (1.0, 0.0, 0.0)
            model.articulation(
                f"button_press_{i}",
                ArticulationType.PRISMATIC,
                parent=body,
                child=button,
                origin=Origin(xyz=origin),
                axis=axis,
                motion_limits=MotionLimits(effort=0.8, velocity=0.03, lower=0.0, upper=0.003),
                meta=_joint_meta(ArticulationType.PRISMATIC, axis, origin, (0.0, 0.003)),
            )

    return model


def build_seeded_camera_flash(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_camera_flash(config_from_seed(seed), assets=assets)


def with_overrides(config: CameraFlashConfig, **kwargs: object) -> CameraFlashConfig:
    return replace(config, **kwargs)


def run_camera_flash_tests(
    object_model: ArticulatedObject, config: CameraFlashConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}
    ctx.check(
        "identity parts present",
        {"body", "neck", "head"}.issubset(names),
        details=str(sorted(names)),
    )
    yaw = object_model.get_articulation("body_to_neck_yaw")
    tilt = object_model.get_articulation("neck_to_head_tilt")
    ctx.check(
        "yaw joint revolute",
        yaw.articulation_type == ArticulationType.REVOLUTE,
        details=f"{yaw.articulation_type}",
    )
    ctx.check("yaw axis is vertical", yaw.axis == (0.0, 0.0, 1.0), details=f"{yaw.axis}")
    ctx.check(
        "tilt joint revolute",
        tilt.articulation_type == ArticulationType.REVOLUTE,
        details=f"{tilt.articulation_type}",
    )
    ctx.check(
        "tilt axis is side pivot",
        tuple(abs(v) for v in tilt.axis) in {(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)},
        details=f"{tilt.axis}",
    )
    for joint in object_model.articulations:
        if joint.articulation_type != ArticulationType.FIXED:
            ctx.check(
                f"{joint.name} has metadata",
                {"type", "axis", "origin", "range"}.issubset(joint.meta),
                details=str(joint.meta),
            )
    body_visuals = {v.name for v in object_model.get_part("body").visuals if v.name}
    ctx.check(
        "hotshoe mount present",
        any(name.startswith("hotshoe") or name == "shoe_block" for name in body_visuals),
        details=str(sorted(body_visuals)),
    )
    head_visuals = {v.name for v in object_model.get_part("head").visuals if v.name}
    ctx.check(
        "diffuser present", "front_diffuser" in head_visuals, details=str(sorted(head_visuals))
    )
    neck_visuals = {v.name for v in object_model.get_part("neck").visuals if v.name}
    if r.neck_style == "side_yoke_arms":
        ctx.check(
            "side yoke has embedded pedestal",
            "yoke_pedestal" in neck_visuals,
            details=str(sorted(neck_visuals)),
        )
    if r.neck_style == "short_neck":
        ctx.check(
            "axis caps present",
            {"tilt_axis_cap_0", "tilt_axis_cap_1"}.issubset(head_visuals),
            details=str(sorted(head_visuals)),
        )
    if r.bounce_card_enabled:
        card = object_model.get_articulation("bounce_card_slide")
        ctx.check(
            "bounce card prismatic",
            card.articulation_type == ArticulationType.PRISMATIC,
            details=f"{card.articulation_type}",
        )
        ctx.check("bounce card axis up", card.axis == (0.0, 0.0, 1.0), details=f"{card.axis}")
    if r.battery_door_enabled:
        ctx.check(
            "battery door hinge present",
            object_model.get_articulation("battery_door_hinge").articulation_type
            == ArticulationType.REVOLUTE,
        )
    return ctx.report()
