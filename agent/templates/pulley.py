# SPDX-License-Identifier: Apache-2.0

"""Source-backed procedural pulley family.

This ordinary single-file template keeps the authored component geometry and
assembly logic in one module.  SourceMap and TemplateDesign are authoring inputs
only; seeded builds depend on this file and the public SDK.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    LatheGeometry,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

FrameConstruction = Literal["open_cheeks", "enclosed_shell", "hinged_gate"]
MountInterface = Literal["fixed_plate", "clevis", "closed_eye", "swivel_hook"]
SheaveProfile = Literal["deep_u", "narrow_v"]
SecondaryModule = Literal["none", "becket_eye"]
PaletteStyle = Literal["galvanized", "marine_black", "bronze_rigging"]


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "frame_construction", ("open_cheeks", "enclosed_shell", "hinged_gate")
        ),
        component_slot(
            "mount_interface", ("fixed_plate", "clevis", "closed_eye", "swivel_hook")
        ),
        component_slot("sheave_profile", ("deep_u", "narrow_v")),
        component_slot("secondary_module", ("none", "becket_eye")),
        multiplicity_slot(
            "sheave_count",
            (1, 2, 3),
            item_slot="sheave_profile",
        ),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "galvanized": {
        "frame": (0.37, 0.40, 0.42, 1.0),
        "edge": (0.18, 0.20, 0.21, 1.0),
        "sheave": (0.12, 0.13, 0.14, 1.0),
        "hardware": (0.68, 0.70, 0.71, 1.0),
    },
    "marine_black": {
        "frame": (0.055, 0.060, 0.064, 1.0),
        "edge": (0.015, 0.017, 0.019, 1.0),
        "sheave": (0.22, 0.24, 0.25, 1.0),
        "hardware": (0.55, 0.57, 0.58, 1.0),
    },
    "bronze_rigging": {
        "frame": (0.42, 0.25, 0.10, 1.0),
        "edge": (0.17, 0.09, 0.035, 1.0),
        "sheave": (0.20, 0.12, 0.055, 1.0),
        "hardware": (0.68, 0.49, 0.23, 1.0),
    },
}


@dataclass(frozen=True)
class Config:
    frame_construction: FrameConstruction = "open_cheeks"
    mount_interface: MountInterface = "fixed_plate"
    sheave_profile: SheaveProfile = "deep_u"
    secondary_module: SecondaryModule = "none"
    sheave_count: int = 1
    pulley_scale: float = 1.0
    sheave_radius_ratio: float = 1.0
    palette_style: PaletteStyle = "galvanized"
    name: str = "pulley"


@dataclass(frozen=True)
class ResolvedConfig:
    frame_construction: FrameConstruction
    mount_interface: MountInterface
    sheave_profile: SheaveProfile
    secondary_module: SecondaryModule
    sheave_count: int
    pulley_scale: float
    sheave_radius_ratio: float
    palette_style: PaletteStyle
    name: str
    sheave_radius: float
    sheave_width: float
    bore_radius: float
    axle_radius: float
    sheave_pitch: float
    stack_width: float
    cheek_thickness: float
    cheek_center_x: float
    bridge_width: float
    axle_length: float
    axle_height: float
    frame_length: float
    frame_bottom_z: float
    frame_top_z: float
    gate_hinge_y: float
    gate_travel: float
    hook_axis_y: float
    becket_center_y: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed))
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        frame_construction=choices["frame_construction"],
        mount_interface=choices["mount_interface"],
        sheave_profile=choices["sheave_profile"],
        secondary_module=choices["secondary_module"],
        sheave_count=choices["sheave_count"],
        pulley_scale=rng.uniform(0.88, 1.12),
        sheave_radius_ratio=rng.uniform(0.92, 1.08),
        palette_style=rng.choice(tuple(PALETTES)),
        name=f"pulley_seed_{int(seed)}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    domain_values = {
        "frame_construction": cfg.frame_construction,
        "mount_interface": cfg.mount_interface,
        "sheave_profile": cfg.sheave_profile,
        "secondary_module": cfg.secondary_module,
        "sheave_count": cfg.sheave_count,
    }
    TEMPLATE_DOMAIN.validate(domain_values)
    scale = _clamp(cfg.pulley_scale, 0.88, 1.12)
    radius_ratio = _clamp(cfg.sheave_radius_ratio, 0.92, 1.08)
    sheave_radius = 0.0125 * scale * radius_ratio
    sheave_width = 0.0140 * scale
    bore_radius = 0.0034 * scale
    axle_radius = bore_radius - 0.00035 * scale
    sheave_pitch = sheave_width + 0.0012 * scale
    stack_width = sheave_width + (cfg.sheave_count - 1) * sheave_pitch
    cheek_thickness = (0.0032 if cfg.frame_construction != "open_cheeks" else 0.0030) * scale
    cheek_center_x = 0.5 * stack_width + cheek_thickness + 0.0010 * scale
    bridge_width = max(0.034 * scale, stack_width + 2.0 * cheek_thickness + 0.004 * scale)
    axle_length = 2.0 * (cheek_center_x + cheek_thickness + 0.0018 * scale)
    axle_height = 0.023 * scale
    frame_length = 0.064 * scale
    frame_bottom_z = 0.004 * scale
    frame_top_z = axle_height + sheave_radius + 0.007 * scale
    return ResolvedConfig(
        frame_construction=cfg.frame_construction,
        mount_interface=cfg.mount_interface,
        sheave_profile=cfg.sheave_profile,
        secondary_module=cfg.secondary_module,
        sheave_count=cfg.sheave_count,
        pulley_scale=scale,
        sheave_radius_ratio=radius_ratio,
        palette_style=cfg.palette_style,
        name=cfg.name,
        sheave_radius=sheave_radius,
        sheave_width=sheave_width,
        bore_radius=bore_radius,
        axle_radius=axle_radius,
        sheave_pitch=sheave_pitch,
        stack_width=stack_width,
        cheek_thickness=cheek_thickness,
        cheek_center_x=cheek_center_x,
        bridge_width=bridge_width,
        axle_length=axle_length,
        axle_height=axle_height,
        frame_length=frame_length,
        frame_bottom_z=frame_bottom_z,
        frame_top_z=frame_top_z,
        gate_hinge_y=-0.020 * scale,
        gate_travel=math.radians(95.0),
        hook_axis_y=-0.040 * scale,
        becket_center_y=0.040 * scale,
        palette=dict(PALETTES[cfg.palette_style]),
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, object]:
    return {
        "frame_construction": config.frame_construction,
        "mount_interface": config.mount_interface,
        "sheave_profile": config.sheave_profile,
        "secondary_module": config.secondary_module,
        "sheave_count": config.sheave_count,
    }


def slot_choices_for_seed(seed: int) -> dict[str, object]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig):
    return {
        key: model.material(f"pulley_{r.palette_style}_{key}", rgba=rgba)
        for key, rgba in r.palette.items()
    }


def _cylinder_x(radius: float, length: float) -> tuple[Cylinder, Origin]:
    return Cylinder(radius=radius, length=length), Origin(rpy=(0.0, math.pi / 2.0, 0.0))


def _annulus_yz(outer: float, inner: float, thickness: float, *, cy: float, cz: float):
    return (
        cq.Workplane("YZ")
        .center(cy, cz)
        .circle(outer)
        .circle(inner)
        .extrude(thickness / 2.0, both=True)
    )


def _rounded_cheek_shape(r: ResolvedConfig, *, slotted: bool = False):
    s = r.pulley_scale
    boss_r = r.sheave_radius + 0.0045 * s
    cheek = (
        cq.Workplane("YZ")
        .center(0.0, r.axle_height)
        .circle(boss_r)
        .extrude(r.cheek_thickness / 2.0, both=True)
    )
    web = (
        cq.Workplane("YZ")
        .center(0.0, 0.5 * (r.axle_height + r.frame_bottom_z))
        .rect(0.026 * s, r.axle_height - r.frame_bottom_z + 0.006 * s)
        .extrude(r.cheek_thickness / 2.0, both=True)
    )
    upper = (
        cq.Workplane("YZ")
        .center(0.0, 0.5 * (r.frame_top_z + r.axle_height))
        .rect(0.028 * s, r.frame_top_z - r.axle_height)
        .extrude(r.cheek_thickness / 2.0, both=True)
    )
    cheek = cheek.union(web).union(upper)
    bore = (
        cq.Workplane("YZ")
        .center(0.0, r.axle_height)
        .circle(r.bore_radius + 0.0004 * s)
        .extrude(r.cheek_thickness, both=True)
    )
    cheek = cheek.cut(bore)
    if slotted:
        release = (
            cq.Workplane("YZ")
            .center(0.0, r.axle_height + 0.5 * boss_r)
            .rect(2.15 * r.bore_radius, boss_r)
            .extrude(r.cheek_thickness, both=True)
        )
        cheek = cheek.cut(release)
    return cheek


def _add_captured_axle(frame, r: ResolvedConfig, mats) -> None:
    geom, local = _cylinder_x(r.axle_radius, r.axle_length)
    frame.visual(
        geom,
        origin=Origin(xyz=(0.0, 0.0, r.axle_height), rpy=local.rpy),
        material=mats["hardware"],
        name="captured_axle", material_class_id=("metal.brass_polished" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.stainless_matte"),
    )
    retainer_x = 0.5 * r.axle_length + 0.00045 * r.pulley_scale
    for side, tag in ((-1.0, "left"), (1.0, "right")):
        sleeve, sleeve_origin = _cylinder_x(
            r.bore_radius + 0.00045 * r.pulley_scale,
            r.cheek_thickness + 0.0005 * r.pulley_scale,
        )
        frame.visual(
            sleeve,
            origin=Origin(
                xyz=(side * r.cheek_center_x, 0.0, r.axle_height),
                rpy=sleeve_origin.rpy,
            ),
            material=mats["hardware"],
            name=f"pressed_bearing_sleeve_{tag}", material_class_id=("metal.brass_polished" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.stainless_matte"),
        )
        cap, cap_origin = _cylinder_x(r.bore_radius + 0.0015 * r.pulley_scale, 0.0012 * r.pulley_scale)
        frame.visual(
            cap,
            origin=Origin(
                xyz=(side * retainer_x, 0.0, r.axle_height), rpy=cap_origin.rpy
            ),
            material=mats["hardware"],
            name=f"axle_retainer_{tag}", material_class_id=("metal.brass_polished" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.stainless_matte"),
        )


def _add_bridge(frame, r: ResolvedConfig, mats) -> None:
    s = r.pulley_scale
    full_half_x = r.cheek_center_x + 0.5 * r.cheek_thickness
    if r.frame_construction == "hinged_gate":
        # The load spine belongs to the fixed cheek only.  Leaving the moving
        # cheek side open gives the service gate a real outward sweep volume.
        spine_x = -0.5 * full_half_x
        spine_width = full_half_x
        bridge_x = -0.25 * r.bridge_width
        bridge_width = 0.5 * r.bridge_width
    else:
        spine_x = 0.0
        spine_width = 2.0 * full_half_x
        bridge_x = 0.0
        bridge_width = r.bridge_width
    frame.visual(
        Box((spine_width, 0.090 * s, 0.006 * s)),
        origin=Origin(xyz=(spine_x, 0.0, r.frame_bottom_z)),
        material=mats["frame"],
        name="continuous_load_spine", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )
    for y, name in ((-0.022 * s, "mount_bridge"), (0.022 * s, "secondary_bridge")):
        frame.visual(
            Box((bridge_width, 0.030 * s, 0.007 * s)),
            origin=Origin(xyz=(bridge_x, y, r.frame_bottom_z + 0.0035 * s)),
            material=mats["frame"],
            name=name, material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
        )


def _add_thrust_washers(frame, r: ResolvedConfig, mats) -> None:
    s = r.pulley_scale
    wheel_centers = _sheave_centers(r)
    boundaries = [wheel_centers[0] - 0.5 * r.sheave_width - 0.00045 * s]
    boundaries += [0.5 * (a + b) for a, b in zip(wheel_centers, wheel_centers[1:])]
    boundaries += [wheel_centers[-1] + 0.5 * r.sheave_width + 0.00045 * s]
    for i, x in enumerate(boundaries):
        washer, washer_origin = _cylinder_x(r.bore_radius + 0.0016 * s, 0.00045 * s)
        frame.visual(
            washer,
            origin=Origin(xyz=(x, 0.0, r.axle_height), rpy=washer_origin.rpy),
            material=mats["hardware"],
            name=f"thrust_washer_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.stainless_matte"),
        )


def _frame_construction_open_cheeks_build(model, r, mats, assets):
    frame = model.part("frame_construction__open_cheeks__frame")
    cheek_mesh = mesh_from_cadquery(
        _rounded_cheek_shape(r), "pulley_open_cheek", assets=assets, tolerance=0.00025
    )
    for side, tag in ((-1.0, "left"), (1.0, "right")):
        frame.visual(
            cheek_mesh,
            origin=Origin(xyz=(side * r.cheek_center_x, 0.0, 0.0)),
            material=mats["frame"],
            name=f"rounded_bearing_cheek_{tag}", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
        )
    _add_bridge(frame, r, mats)
    _add_captured_axle(frame, r, mats)
    _add_thrust_washers(frame, r, mats)
    return frame


def _frame_construction_enclosed_shell_build(model, r, mats, assets):
    frame = model.part("frame_construction__enclosed_shell__frame")
    cheek_mesh = mesh_from_cadquery(
        _rounded_cheek_shape(r), "pulley_shell_bearing_wall", assets=assets, tolerance=0.00025
    )
    for side, tag in ((-1.0, "left"), (1.0, "right")):
        frame.visual(
            cheek_mesh,
            origin=Origin(xyz=(side * r.cheek_center_x, 0.0, 0.0)),
            material=mats["frame"],
            name=f"integral_bearing_wall_{tag}", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
        )
    s = r.pulley_scale
    outer_x = 2.0 * (r.cheek_center_x + 0.5 * r.cheek_thickness)
    # Four rails close the chamber while leaving opposed rope windows at the
    # sheave tangency regions.  The internal width is derived directly from N.
    for y, z, dy, dz, name in (
        (0.0, r.frame_top_z, 0.014 * s, 0.004 * s, "shell_crown"),
        (0.0, r.frame_bottom_z, 0.014 * s, 0.004 * s, "shell_keel"),
        (-0.5 * r.frame_length + 0.004 * s, 0.5 * (r.frame_top_z + r.frame_bottom_z), 0.006 * s, r.frame_top_z - r.frame_bottom_z, "rear_shell_web"),
        (0.5 * r.frame_length - 0.004 * s, 0.5 * (r.frame_top_z + r.frame_bottom_z), 0.006 * s, r.frame_top_z - r.frame_bottom_z, "front_shell_web"),
    ):
        frame.visual(
            Box((outer_x, dy, dz)),
            origin=Origin(xyz=(0.0, y, z)),
            material=mats["frame"],
            name=name, material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
        )
    _add_bridge(frame, r, mats)
    _add_captured_axle(frame, r, mats)
    _add_thrust_washers(frame, r, mats)
    return frame


def _add_axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    provider: AxisInterface,
    consumer: AxisInterface,
    articulation_type: ArticulationType,
    motion_limits: MotionLimits,
):
    mate = mate_axes(provider, consumer)
    joint = model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=motion_limits,
    )
    register_interface_mate(model, name, mate)
    return joint


def _frame_construction_hinged_gate_build(model, r, mats, assets):
    frame = model.part("frame_construction__hinged_gate__frame")
    fixed_mesh = mesh_from_cadquery(
        _rounded_cheek_shape(r), "pulley_hinged_fixed_cheek", assets=assets, tolerance=0.00025
    )
    frame.visual(
        fixed_mesh,
        origin=Origin(xyz=(-r.cheek_center_x, 0.0, 0.0)),
        material=mats["frame"],
        name="fixed_bearing_cheek", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )
    _add_bridge(frame, r, mats)
    _add_captured_axle(frame, r, mats)
    _add_thrust_washers(frame, r, mats)
    s = r.pulley_scale
    hinge_z = r.frame_bottom_z + 0.008 * s
    frame.visual(
        Cylinder(radius=0.0033 * s, length=0.012 * s),
        origin=Origin(xyz=(r.cheek_center_x, r.gate_hinge_y, hinge_z)),
        material=mats["hardware"],
        name="captured_gate_hinge_pin", material_class_id=("metal.brass_polished" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.stainless_matte"),
    )
    frame.visual(
        Box((2.0 * r.cheek_center_x, 0.006 * s, 0.006 * s)),
        origin=Origin(xyz=(0.0, r.gate_hinge_y, hinge_z)),
        material=mats["frame"],
        name="fixed_hinge_yoke", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )
    frame.visual(
        Box((0.007 * s, 0.006 * s, 0.008 * s)),
        origin=Origin(xyz=(r.cheek_center_x, 0.022 * s, r.frame_bottom_z + 0.006 * s)),
        material=mats["hardware"],
        name="gate_latch_post", material_class_id=("metal.brass_polished" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.stainless_matte"),
    )
    frame.visual(
        Box((2.0 * r.cheek_center_x, 0.006 * s, 0.007 * s)),
        origin=Origin(xyz=(0.0, 0.022 * s, r.frame_bottom_z + 0.006 * s)),
        material=mats["frame"],
        name="fixed_latch_crossbar", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )

    gate = model.part("frame_construction__hinged_gate__gate")
    local_gate = _rounded_cheek_shape(r, slotted=True).translate(
        (0.0, -r.gate_hinge_y, -hinge_z)
    )
    gate.visual(
        mesh_from_cadquery(local_gate, "pulley_hinged_release_gate", assets=assets, tolerance=0.00025),
        material=mats["frame"],
        name="slotted_release_gate", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )
    gate.visual(
        Cylinder(radius=0.0063 * s, length=0.006 * s),
        material=mats["edge"],
        name="moving_hinge_barrel", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "marine_black"} else "metal.brass_aged"),
    )
    gate.visual(
        Box((0.008 * s, 0.015 * s, 0.013 * s)),
        origin=Origin(
            xyz=(0.0, 0.022 * s - r.gate_hinge_y, r.frame_bottom_z + 0.006 * s - hinge_z)
        ),
        material=mats["edge"],
        name="gate_latch_lug", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "marine_black"} else "metal.brass_aged"),
    )
    _add_axis_joint(
        model,
        name="frame_construction__hinged_gate__hinge",
        parent=frame,
        child=gate,
        provider=AxisInterface(
            name="frame_gate_axis",
            point=(r.cheek_center_x, r.gate_hinge_y, hinge_z),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
        ),
        consumer=AxisInterface(
            name="gate_local_axis", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
        ),
        articulation_type=ArticulationType.REVOLUTE,
        motion_limits=MotionLimits(lower=-r.gate_travel, upper=0.0, effort=2.0, velocity=1.5),
    )
    return frame


def _mount_interface_fixed_plate_build(frame, r, mats, assets):
    s = r.pulley_scale
    plate_w = max(r.bridge_width, 0.038 * s)
    plate_l = 0.028 * s
    plate_t = 0.0035 * s
    plate = (
        cq.Workplane("XY")
        .box(plate_w, plate_l, plate_t)
        .faces(">Z")
        .workplane()
        .pushPoints([(-0.28 * plate_w, 0.0), (0.28 * plate_w, 0.0)])
        .cskHole(0.0048 * s, 0.0090 * s, 82.0)
    )
    frame.visual(
        mesh_from_cadquery(plate, "pulley_countersunk_mount_plate", assets=assets, tolerance=0.00025),
        origin=Origin(xyz=(0.0, -0.039 * s, r.frame_bottom_z - 0.001 * s)),
        material=mats["frame"],
        name="mount_interface__fixed_plate__mount", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )


def _mount_interface_clevis_build(frame, r, mats, assets):
    s = r.pulley_scale
    ear_x = 0.5 * min(r.bridge_width - 0.006 * s, 0.024 * s)
    pin_z = r.frame_bottom_z + 0.016 * s
    pin_y = -0.041 * s
    for side, tag in ((-1.0, "left"), (1.0, "right")):
        ear = (
            cq.Workplane("YZ")
            .center(pin_y, pin_z)
            .circle(0.007 * s)
            .extrude(0.003 * s, both=True)
            .union(
                cq.Workplane("YZ")
                .center(pin_y + 0.005 * s, pin_z - 0.007 * s)
                .rect(0.012 * s, 0.018 * s)
                .extrude(0.003 * s, both=True)
            )
            .cut(
                cq.Workplane("YZ")
                .center(pin_y, pin_z)
                .circle(0.0027 * s)
                .extrude(0.006 * s, both=True)
            )
        )
        frame.visual(
            mesh_from_cadquery(ear, f"pulley_clevis_ear_{tag}", assets=assets, tolerance=0.00025),
            origin=Origin(xyz=(side * ear_x, 0.0, 0.0)),
            material=mats["frame"],
            name=f"mount_interface__clevis__ear_{tag}", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
        )
    pin, pin_origin = _cylinder_x(0.00272 * s, 2.0 * ear_x + 0.009 * s)
    frame.visual(
        pin,
        origin=Origin(xyz=(0.0, pin_y, pin_z), rpy=pin_origin.rpy),
        material=mats["hardware"],
        name="mount_interface__clevis__attachment_pin", material_class_id=("metal.brass_polished" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.stainless_matte"),
    )


def _mount_interface_closed_eye_build(frame, r, mats, assets):
    s = r.pulley_scale
    center_y = -0.043 * s
    center_z = r.frame_bottom_z + 0.014 * s
    eye = _annulus_yz(0.010 * s, 0.0052 * s, min(r.bridge_width, 0.012 * s), cy=center_y, cz=center_z)
    frame.visual(
        mesh_from_cadquery(eye, "pulley_closed_mount_eye", assets=assets, tolerance=0.00022),
        material=mats["frame"],
        name="mount_interface__closed_eye__mount", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )
    frame.visual(
        Box((min(r.bridge_width, 0.016 * s), 0.014 * s, 0.010 * s)),
        origin=Origin(xyz=(0.0, -0.031 * s, r.frame_bottom_z + 0.009 * s)),
        material=mats["frame"],
        name="mount_interface__closed_eye__reinforced_neck", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )


def _hook_shape(r: ResolvedConfig):
    s = r.pulley_scale
    # A C-shaped plate in XY with a real open throat; the stem lies at local origin.
    ring = (
        cq.Workplane("XY")
        .center(0.0, -0.012 * s)
        .circle(0.013 * s)
        .circle(0.0075 * s)
        .extrude(0.0035 * s, both=True)
    )
    throat = (
        cq.Workplane("XY")
        .center(0.010 * s, -0.005 * s)
        .rect(0.014 * s, 0.020 * s)
        .extrude(0.006 * s, both=True)
    )
    neck = cq.Workplane("XY").center(0.0, -0.003 * s).rect(0.007 * s, 0.013 * s).extrude(0.0035 * s, both=True)
    return ring.cut(throat).union(neck)


def _mount_interface_swivel_hook_build(model, frame, r, mats, assets):
    s = r.pulley_scale
    axis_z = r.frame_bottom_z - 0.001 * s
    frame.visual(
        Box((min(r.bridge_width, 0.022 * s), 0.012 * s, 0.006 * s)),
        origin=Origin(xyz=(0.0, r.hook_axis_y + 0.009 * s, axis_z + 0.003 * s)),
        material=mats["frame"],
        name="mount_interface__swivel_hook__bearing_bridge", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )
    bearing_tube = (
        cq.Workplane("XY")
        .circle(0.0047 * s)
        .circle(0.0032 * s)
        .extrude(0.003 * s, both=True)
    )
    frame.visual(
        mesh_from_cadquery(bearing_tube, "pulley_swivel_bearing", assets=assets, tolerance=0.0002),
        origin=Origin(xyz=(0.0, r.hook_axis_y, axis_z)),
        material=mats["hardware"],
        name="mount_interface__swivel_hook__captured_bearing", material_class_id=("metal.brass_polished" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.stainless_matte"),
    )
    hook = model.part("mount_interface__swivel_hook__hook")
    hook.visual(
        mesh_from_cadquery(_hook_shape(r), "pulley_swivel_load_hook", assets=assets, tolerance=0.0002),
        origin=Origin(xyz=(0.0, 0.0, -0.012 * s)),
        material=mats["frame"],
        name="open_load_hook", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )
    hook.visual(
        Cylinder(radius=0.0028 * s, length=0.010 * s),
        origin=Origin(xyz=(0.0, 0.0, -0.004 * s)),
        material=mats["hardware"],
        name="swivel_stem", material_class_id=("metal.brass_polished" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.stainless_matte"),
    )
    _add_axis_joint(
        model,
        name="mount_interface__swivel_hook__rotation",
        parent=frame,
        child=hook,
        provider=AxisInterface(
            name="frame_swivel_axis",
            point=(0.0, r.hook_axis_y, axis_z),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
        ),
        consumer=AxisInterface(
            name="hook_local_axis", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
        ),
        articulation_type=ArticulationType.CONTINUOUS,
        motion_limits=MotionLimits(effort=1.5, velocity=3.0),
    )


def _secondary_module_becket_eye_build(frame, r, mats, assets):
    s = r.pulley_scale
    center_z = r.frame_bottom_z + 0.012 * s
    becket = _annulus_yz(
        0.0085 * s,
        0.0043 * s,
        min(r.bridge_width, 0.010 * s),
        cy=r.becket_center_y,
        cz=center_z,
    )
    frame.visual(
        mesh_from_cadquery(becket, "pulley_secondary_becket", assets=assets, tolerance=0.00022),
        material=mats["frame"],
        name="secondary_module__becket_eye__anchor", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )
    frame.visual(
        Box((min(r.bridge_width, 0.014 * s), 0.012 * s, 0.008 * s)),
        origin=Origin(xyz=(0.0, 0.031 * s, center_z)),
        material=mats["frame"],
        name="secondary_module__becket_eye__reinforced_neck", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.paint_coated"),
    )


def _sheave_centers(r: ResolvedConfig) -> list[float]:
    start = -0.5 * (r.sheave_count - 1) * r.sheave_pitch
    return [start + i * r.sheave_pitch for i in range(r.sheave_count)]


def _sheave_geometry(r: ResolvedConfig):
    half = 0.5 * r.sheave_width
    rr = r.sheave_radius
    if r.sheave_profile == "deep_u":
        outer = [
            (0.96 * rr, -half),
            (rr, -0.82 * half),
            (rr, -0.54 * half),
            (0.79 * rr, 0.0),
            (rr, 0.54 * half),
            (rr, 0.82 * half),
            (0.96 * rr, half),
        ]
    else:
        outer = [
            (0.95 * rr, -half),
            (rr, -0.76 * half),
            (rr, -0.45 * half),
            (0.70 * rr, 0.0),
            (rr, 0.45 * half),
            (rr, 0.76 * half),
            (0.95 * rr, half),
        ]
    inner = [(r.bore_radius, -half), (r.bore_radius, half)]
    return LatheGeometry.from_shell_profiles(outer, inner, segments=48).rotate_y(math.pi / 2.0)


def _build_sheaves(model, frame, r, mats):
    wheel_mesh = mesh_from_geometry(_sheave_geometry(r), f"pulley_{r.sheave_profile}_sheave")
    for i, x in enumerate(_sheave_centers(r)):
        sheave = model.part(f"sheave_profile__{r.sheave_profile}__sheave_{i}")
        sheave.visual(wheel_mesh, material=mats["sheave"], name=f"grooved_sheave_{i}", material_class_id=("metal.bronze_cast" if r.palette_style in {"marine_black", "bronze_rigging"} else "metal.cast_iron_bare"))
        hub, hub_origin = _cylinder_x(r.bore_radius + 0.0020 * r.pulley_scale, 0.28 * r.sheave_width)
        sheave.visual(
            hub,
            origin=hub_origin,
            material=mats["hardware"],
            name=f"sheave_hub_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"galvanized", "bronze_rigging"} else "metal.stainless_matte"),
        )
        _add_axis_joint(
            model,
            name=f"sheave_profile__{r.sheave_profile}__rotation_{i}",
            parent=frame,
            child=sheave,
            provider=AxisInterface(
                name=f"frame_sheave_axis_{i}",
                point=(x, 0.0, r.axle_height),
                axis=(1.0, 0.0, 0.0),
                radial=(0.0, 0.0, 1.0),
                radius=r.bore_radius,
            ),
            consumer=AxisInterface(
                name=f"sheave_local_axis_{i}",
                axis=(1.0, 0.0, 0.0),
                radial=(0.0, 0.0, 1.0),
                radius=r.axle_radius,
            ),
            articulation_type=ArticulationType.CONTINUOUS,
            motion_limits=MotionLimits(effort=0.8, velocity=20.0),
        )


_FRAME_BUILDERS = {
    "open_cheeks": _frame_construction_open_cheeks_build,
    "enclosed_shell": _frame_construction_enclosed_shell_build,
    "hinged_gate": _frame_construction_hinged_gate_build,
}


def build_pulley(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r)
    frame = _FRAME_BUILDERS[r.frame_construction](model, r, mats, assets)

    if r.mount_interface == "fixed_plate":
        _mount_interface_fixed_plate_build(frame, r, mats, assets)
    elif r.mount_interface == "clevis":
        _mount_interface_clevis_build(frame, r, mats, assets)
    elif r.mount_interface == "closed_eye":
        _mount_interface_closed_eye_build(frame, r, mats, assets)
    else:
        _mount_interface_swivel_hook_build(model, frame, r, mats, assets)

    if r.secondary_module == "becket_eye":
        _secondary_module_becket_eye_build(frame, r, mats, assets)
    _build_sheaves(model, frame, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/pulley"
    model.meta["assembly_dimensions"] = {
        "stack_width": r.stack_width,
        "cheek_center_x": r.cheek_center_x,
        "bridge_width": r.bridge_width,
        "axle_length": r.axle_length,
        "bore_radius": r.bore_radius,
        "axle_radius": r.axle_radius,
    }
    return model


def build_seeded_pulley(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_pulley(config_from_seed(seed), assets=assets)


def run_pulley_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    parts = {part.name for part in object_model.parts}
    joints = {joint.name: joint for joint in object_model.articulations}

    frame_name = f"frame_construction__{r.frame_construction}__frame"
    ctx.check("selected source-backed frame exists", frame_name in parts)
    expected_sheaves = {
        f"sheave_profile__{r.sheave_profile}__sheave_{i}" for i in range(r.sheave_count)
    }
    ctx.check(
        "N independently rotating sheaves exist",
        expected_sheaves.issubset(parts),
        details=f"expected={sorted(expected_sheaves)} parts={sorted(parts)}",
    )
    for i, expected_x in enumerate(_sheave_centers(r)):
        joint = joints.get(f"sheave_profile__{r.sheave_profile}__rotation_{i}")
        ctx.check(
            f"sheave {i} uses a continuous X-axis bore joint",
            joint is not None
            and joint.articulation_type == ArticulationType.CONTINUOUS
            and tuple(joint.axis) == (1.0, 0.0, 0.0)
            and math.isclose(joint.origin.xyz[0], expected_x, abs_tol=1.0e-9)
            and math.isclose(joint.origin.xyz[2], r.axle_height, abs_tol=1.0e-9),
        )

    ctx.check(
        "axle has positive running clearance inside every sheave bore",
        r.bore_radius - r.axle_radius >= 0.00030 * r.pulley_scale,
    )
    ctx.check(
        "N-wide stack remains inside both bearing cheeks",
        0.5 * r.stack_width + 0.5 * r.sheave_width * 0.0
        < r.cheek_center_x - 0.5 * r.cheek_thickness,
    )
    ctx.check(
        "captured axle spans both cheeks and outside retainers",
        0.5 * r.axle_length > r.cheek_center_x + 0.5 * r.cheek_thickness,
    )

    gate_joint = joints.get("frame_construction__hinged_gate__hinge")
    ctx.check(
        "hinged gate topology matches the selected frame",
        (
            gate_joint is not None
            and gate_joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(gate_joint.axis) == (0.0, 0.0, 1.0)
            and gate_joint.motion_limits is not None
            and math.isclose(gate_joint.motion_limits.lower, -r.gate_travel)
            and math.isclose(gate_joint.motion_limits.upper, 0.0)
        )
        if r.frame_construction == "hinged_gate"
        else gate_joint is None,
    )
    hook_joint = joints.get("mount_interface__swivel_hook__rotation")
    ctx.check(
        "swivel hook topology matches the selected mount",
        (
            hook_joint is not None
            and hook_joint.articulation_type == ArticulationType.CONTINUOUS
            and tuple(hook_joint.axis) == (0.0, 0.0, 1.0)
        )
        if r.mount_interface == "swivel_hook"
        else hook_joint is None,
    )
    ctx.check(
        "becket opening stays beyond the sheave rope envelope",
        r.becket_center_y - 0.0085 * r.pulley_scale > r.sheave_radius
        if r.secondary_module == "becket_eye"
        else True,
    )
    ctx.check(
        "domain choices are recorded on the model",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "wide_enclosed_three_sheave_rig",
        {
            "frame_construction": "enclosed_shell",
            "mount_interface": "swivel_hook",
            "sheave_profile": "narrow_v",
            "secondary_module": "becket_eye",
            "sheave_count": 3,
            "pulley_scale": 1.12,
            "sheave_radius_ratio": 1.08,
        },
        reason="maximum N shell capacity, swivel sweep and becket clearance",
    ),
    corner_case(
        "open_hinged_service_position",
        {
            "frame_construction": "hinged_gate",
            "mount_interface": "clevis",
            "sheave_profile": "deep_u",
            "secondary_module": "becket_eye",
            "sheave_count": 3,
            "pulley_scale": 0.88,
            "sheave_radius_ratio": 0.92,
        },
        reason="compact three-wheel gate, latch and release-slot geometry",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_pulley",
    "build_seeded_pulley",
    "run_pulley_tests",
]
