# SPDX-License-Identifier: Apache-2.0

"""Source-backed procedural microphone boom-arm families.

This ordinary single-file template couples each arm topology with its mechanically matched
compensation system. SourceMap and TemplateDesign are authoring inputs only.
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
    AxisInterface,
    Box,
    Cylinder,
    ExtrudeGeometry,
    KnobGeometry,
    KnobGrip,
    MotionLimits,
    Origin,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    TorusGeometry,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    register_interface_mate,
    rounded_rect_profile,
    tube_from_spline_points,
)

MechanismFamily = Literal[
    "folded_extension",
    "low_profile_extension",
    "wall_swing_torsion",
    "tubular_gas",
    "three_link_counterweight",
    "parallelogram_constant_force",
]
BaseMount = Literal["desk_clamp", "weighted_desktop", "grommet", "wall_plate", "floor_stand"]
TerminalMount = Literal["threaded_adapter", "studio_cradle", "shock_mount"]
PaletteStyle = Literal["studio_black", "graphite", "warm_gray"]


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "mechanism_family",
            (
                "folded_extension",
                "low_profile_extension",
                "wall_swing_torsion",
                "tubular_gas",
                "three_link_counterweight",
                "parallelogram_constant_force",
            ),
        ),
        component_slot(
            "base_mount",
            ("desk_clamp", "weighted_desktop", "grommet", "wall_plate", "floor_stand"),
        ),
        component_slot("terminal_mount", ("threaded_adapter", "studio_cradle", "shock_mount")),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "studio_black": {
        "coat": (0.025, 0.028, 0.032, 1.0),
        "edge": (0.085, 0.090, 0.095, 1.0),
        "metal": (0.38, 0.40, 0.42, 1.0),
        "rubber": (0.012, 0.014, 0.016, 1.0),
        "spring": (0.24, 0.26, 0.27, 1.0),
        "accent": (0.40, 0.045, 0.035, 1.0),
    },
    "graphite": {
        "coat": (0.10, 0.11, 0.12, 1.0),
        "edge": (0.19, 0.20, 0.21, 1.0),
        "metal": (0.56, 0.57, 0.58, 1.0),
        "rubber": (0.025, 0.027, 0.029, 1.0),
        "spring": (0.34, 0.35, 0.36, 1.0),
        "accent": (0.62, 0.08, 0.05, 1.0),
    },
    "warm_gray": {
        "coat": (0.19, 0.18, 0.16, 1.0),
        "edge": (0.28, 0.27, 0.24, 1.0),
        "metal": (0.61, 0.58, 0.51, 1.0),
        "rubber": (0.035, 0.032, 0.028, 1.0),
        "spring": (0.39, 0.37, 0.33, 1.0),
        "accent": (0.52, 0.10, 0.055, 1.0),
    },
}


@dataclass(frozen=True)
class Config:
    mechanism_family: MechanismFamily
    base_mount: BaseMount
    terminal_mount: TerminalMount
    palette_style: PaletteStyle = "studio_black"
    overall_scale: float = 1.0
    reach_scale: float = 1.0
    section_scale: float = 1.0
    name: str = "microphone_boom_arm"


@dataclass(frozen=True)
class ResolvedConfig:
    mechanism_family: MechanismFamily
    base_mount: BaseMount
    terminal_mount: TerminalMount
    palette_style: PaletteStyle
    scale: float
    reach_scale: float
    section_scale: float
    root_height: float
    shoulder_height: float
    link_lengths: tuple[float, ...]
    link_width: float
    link_depth: float
    neutral_angles: tuple[float, ...]
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x4D49_435F_424F_4F4D)
    return Config(
        mechanism_family=choices["mechanism_family"],
        base_mount=choices["base_mount"],
        terminal_mount=choices["terminal_mount"],
        palette_style=rng.choice(tuple(PALETTES)),
        overall_scale=round(rng.uniform(0.90, 1.10), 4),
        reach_scale=round(rng.uniform(0.90, 1.10), 4),
        section_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"microphone_boom_arm_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "mechanism_family": config.mechanism_family,
            "base_mount": config.base_mount,
            "terminal_mount": config.terminal_mount,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    scale = _clamp(config.overall_scale, 0.88, 1.12)
    reach = _clamp(config.reach_scale, 0.88, 1.12)
    section = _clamp(config.section_scale, 0.88, 1.12)
    root_height = {
        "desk_clamp": 0.155,
        "weighted_desktop": 0.082,
        "grommet": 0.070,
        "wall_plate": 0.145,
        "floor_stand": 0.620,
    }[config.base_mount]
    lengths, angles, width, depth = {
        "folded_extension": ((0.285, 0.365), (0.52, 1.12), 0.034, 0.027),
        "low_profile_extension": ((0.340, 0.400), (0.12, 0.10), 0.027, 0.029),
        "wall_swing_torsion": ((0.320, 0.455), (1.02, -0.90), 0.030, 0.029),
        "tubular_gas": ((0.355, 0.430), (0.82, -0.68), 0.042, 0.050),
        "three_link_counterweight": ((0.260, 0.250, 0.285), (0.78, -0.42, -0.24), 0.035, 0.030),
        "parallelogram_constant_force": ((0.340, 0.490), (1.02, -0.90), 0.052, 0.052),
    }[config.mechanism_family]
    return ResolvedConfig(
        mechanism_family=config.mechanism_family,
        base_mount=config.base_mount,
        terminal_mount=config.terminal_mount,
        palette_style=config.palette_style,
        scale=scale,
        reach_scale=reach,
        section_scale=section,
        root_height=root_height * scale,
        shoulder_height=0.082 * scale,
        link_lengths=tuple(value * scale * reach for value in lengths),
        link_width=width * scale * section,
        link_depth=depth * scale * section,
        neutral_angles=angles,
        palette=PALETTES[config.palette_style],
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, str]:
    return {
        "mechanism_family": config.mechanism_family,
        "base_mount": config.base_mount,
        "terminal_mount": config.terminal_mount,
    }


def slot_choices_for_seed(seed: int) -> dict[str, str]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig):
    return {name: model.material(name, rgba=rgba) for name, rgba in r.palette.items()}


def _cylinder_x(radius: float, length: float) -> tuple[Cylinder, Origin]:
    return Cylinder(radius=radius, length=length), Origin(rpy=(0.0, math.pi / 2.0, 0.0))


def _cylinder_y(radius: float, length: float) -> tuple[Cylinder, Origin]:
    return Cylinder(radius=radius, length=length), Origin(rpy=(math.pi / 2.0, 0.0, 0.0))


def _rounded_bar_mesh(length: float, width: float, depth: float, name: str):
    profile = rounded_rect_profile(length, width, min(length, width) * 0.44, corner_segments=10)
    return mesh_from_geometry(
        ExtrudeGeometry(profile, depth, center=True).rotate_x(math.pi / 2.0), name
    )


def _spring_mesh(length: float, y: float, z: float, name: str, turns: int = 18):
    start = 0.045
    stop = max(start + 0.030, length - 0.050)
    coil = 0.0038
    points = [(0.030, y, z), (start, y, z)]
    for index in range(turns * 5 + 1):
        t = index / (turns * 5)
        phase = 2.0 * math.pi * turns * t
        points.append(
            (
                start + (stop - start) * t,
                y + coil * math.cos(phase),
                z + coil * math.sin(phase),
            )
        )
    points.extend(((stop, y, z), (length - 0.030, y, z)))
    geometry = tube_from_spline_points(
        points,
        radius=0.0011,
        samples_per_segment=2,
        radial_segments=8,
        cap_ends=True,
    )
    return mesh_from_geometry(geometry, name)


def _add_axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    provider: AxisInterface,
    consumer: AxisInterface,
    lower: float,
    upper: float,
):
    mate = mate_axes(provider, consumer)
    joint = model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(lower=lower, upper=upper, effort=24.0, velocity=1.4),
    )
    register_interface_mate(model, name, mate)
    return joint


def _root_axis(r: ResolvedConfig, name: str) -> AxisInterface:
    return AxisInterface(
        name=name,
        point=(0.0, 0.0, r.root_height),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )


# ---------------------------------------------------------------------------
# Base candidates
# ---------------------------------------------------------------------------


def _add_socket(base, r, mats, prefix: str):
    s = r.scale
    base.visual(
        Cylinder(radius=0.028 * s, length=0.024 * s),
        origin=Origin(xyz=(0.0, 0.0, r.root_height - 0.012 * s)),
        material=mats["edge"],
        name=f"{prefix}__socket", material_class_id="metal.blackened_gunmetal",
    )


def _base_mount_desk_clamp_build(model, r, mats, assets):
    base = model.part("base_mount__desk_clamp__base")
    s = r.scale
    base.visual(
        Box((0.040 * s, 0.070 * s, 0.140 * s)),
        origin=Origin(xyz=(-0.045 * s, 0.0, 0.070 * s)),
        material=mats["coat"],
        name="base_mount__desk_clamp__spine", material_class_id="metal.paint_coated",
    )
    base.visual(
        Box((0.125 * s, 0.070 * s, 0.020 * s)),
        origin=Origin(xyz=(0.0, 0.0, 0.140 * s)),
        material=mats["coat"],
        name="base_mount__desk_clamp__top_jaw", material_class_id="metal.paint_coated",
    )
    base.visual(
        Box((0.095 * s, 0.070 * s, 0.018 * s)),
        origin=Origin(xyz=(-0.015 * s, 0.0, 0.010 * s)),
        material=mats["coat"],
        name="base_mount__desk_clamp__lower_jaw", material_class_id="metal.paint_coated",
    )
    base.visual(
        Box((0.085 * s, 0.056 * s, 0.005 * s)),
        origin=Origin(xyz=(0.012 * s, 0.0, 0.1275 * s)),
        material=mats["rubber"],
        name="base_mount__desk_clamp__desk_pad", material_class_id="rubber.smooth_plain",
    )
    base.visual(
        Cylinder(radius=0.005 * s, length=0.105 * s),
        origin=Origin(xyz=(0.018 * s, 0.0, 0.055 * s)),
        material=mats["metal"],
        name="base_mount__desk_clamp__screw", material_class_id="metal.stainless_matte",
    )
    base.visual(
        Cylinder(radius=0.019 * s, length=0.006 * s),
        origin=Origin(xyz=(0.018 * s, 0.0, 0.1095 * s)),
        material=mats["rubber"],
        name="base_mount__desk_clamp__pressure_pad", material_class_id="rubber.smooth_plain",
    )
    handle, rot = _cylinder_x(0.004 * s, 0.082 * s)
    base.visual(
        handle,
        origin=Origin(xyz=(0.018 * s, 0.0, 0.001 * s), rpy=rot.rpy),
        material=mats["metal"],
        name="base_mount__desk_clamp__handle", material_class_id="metal.stainless_matte",
    )
    _add_socket(base, r, mats, "base_mount__desk_clamp")
    return base, _root_axis(r, "base_mount.desk_clamp.swivel_axis")


def _base_mount_weighted_desktop_build(model, r, mats, assets):
    base = model.part("base_mount__weighted_desktop__base")
    s = r.scale
    base.visual(
        _rounded_bar_mesh(0.190 * s, 0.130 * s, 0.020 * s, "desktop_foot"),
        origin=Origin(xyz=(0.0, 0.0, 0.012 * s)),
        material=mats["coat"],
        name="base_mount__weighted_desktop__foot", material_class_id="metal.paint_coated",
    )
    base.visual(
        _rounded_bar_mesh(0.122 * s, 0.090 * s, 0.040 * s, "desktop_shell"),
        origin=Origin(xyz=(0.0, 0.0, 0.041 * s)),
        material=mats["edge"],
        name="base_mount__weighted_desktop__shell", material_class_id="metal.blackened_gunmetal",
    )
    base.visual(
        Box((0.170 * s, 0.110 * s, 0.005 * s)),
        origin=Origin(xyz=(0.0, 0.0, 0.0025 * s)),
        material=mats["rubber"],
        name="base_mount__weighted_desktop__pad", material_class_id="rubber.smooth_plain",
    )
    _add_socket(base, r, mats, "base_mount__weighted_desktop")
    return base, _root_axis(r, "base_mount.weighted_desktop.swivel_axis")


def _base_mount_grommet_build(model, r, mats, assets):
    base = model.part("base_mount__grommet__base")
    s = r.scale
    base.visual(
        Cylinder(radius=0.046 * s, length=0.009 * s),
        origin=Origin(xyz=(0.0, 0.0, 0.0045 * s)),
        material=mats["coat"],
        name="base_mount__grommet__top_flange", material_class_id="metal.paint_coated",
    )
    base.visual(
        Cylinder(radius=0.012 * s, length=0.085 * s),
        origin=Origin(xyz=(0.0, 0.0, -0.034 * s)),
        material=mats["metal"],
        name="base_mount__grommet__through_post", material_class_id="metal.stainless_matte",
    )
    base.visual(
        Cylinder(radius=0.030 * s, length=0.012 * s),
        origin=Origin(xyz=(0.0, 0.0, -0.080 * s)),
        material=mats["edge"],
        name="base_mount__grommet__lower_nut", material_class_id="metal.blackened_gunmetal",
    )
    base.visual(
        Cylinder(radius=0.025 * s, length=0.061 * s),
        origin=Origin(xyz=(0.0, 0.0, 0.0395 * s)),
        material=mats["coat"],
        name="base_mount__grommet__tower", material_class_id="metal.paint_coated",
    )
    _add_socket(base, r, mats, "base_mount__grommet")
    return base, _root_axis(r, "base_mount.grommet.swivel_axis")


def _base_mount_wall_plate_build(model, r, mats, assets):
    base = model.part("base_mount__wall_plate__base")
    s = r.scale
    base.visual(
        Box((0.016 * s, 0.110 * s, 0.245 * s)),
        origin=Origin(xyz=(-0.070 * s, 0.0, 0.030 * s)),
        material=mats["coat"],
        name="base_mount__wall_plate__plate", material_class_id="metal.paint_coated",
    )
    for index, (y, z) in enumerate(
        ((-0.036, -0.045), (0.036, -0.045), (-0.036, 0.105), (0.036, 0.105))
    ):
        fastener, rot = _cylinder_x(0.0065 * s, 0.022 * s)
        base.visual(
            fastener,
            origin=Origin(xyz=(-0.080 * s, y * s, z * s), rpy=rot.rpy),
            material=mats["metal"],
            name=f"base_mount__wall_plate__fastener_{index}", material_class_id="metal.stainless_matte",
        )
    base.visual(
        Box((0.130 * s, 0.075 * s, 0.052 * s)),
        origin=Origin(xyz=(-0.010 * s, 0.0, 0.106 * s)),
        material=mats["coat"],
        name="base_mount__wall_plate__cantilever", material_class_id="metal.paint_coated",
    )
    _add_socket(base, r, mats, "base_mount__wall_plate")
    return base, _root_axis(r, "base_mount.wall_plate.swivel_axis")


def _base_mount_floor_stand_build(model, r, mats, assets):
    base = model.part("base_mount__floor_stand__base")
    s = r.scale
    base.visual(
        _rounded_bar_mesh(0.360 * s, 0.300 * s, 0.028 * s, "floor_foot"),
        origin=Origin(xyz=(0.0, 0.0, 0.014 * s)),
        material=mats["coat"],
        name="base_mount__floor_stand__foot", material_class_id="metal.paint_coated",
    )
    base.visual(
        Cylinder(radius=0.030 * s, length=0.575 * s),
        origin=Origin(xyz=(0.0, 0.0, 0.315 * s)),
        material=mats["coat"],
        name="base_mount__floor_stand__riser", material_class_id="metal.paint_coated",
    )
    base.visual(
        Cylinder(radius=0.045 * s, length=0.018 * s),
        origin=Origin(xyz=(0.0, 0.0, 0.042 * s)),
        material=mats["edge"],
        name="base_mount__floor_stand__collar", material_class_id="metal.blackened_gunmetal",
    )
    _add_socket(base, r, mats, "base_mount__floor_stand")
    return base, _root_axis(r, "base_mount.floor_stand.swivel_axis")


_BASE_BUILDERS = {
    "desk_clamp": _base_mount_desk_clamp_build,
    "weighted_desktop": _base_mount_weighted_desktop_build,
    "grommet": _base_mount_grommet_build,
    "wall_plate": _base_mount_wall_plate_build,
    "floor_stand": _base_mount_floor_stand_build,
}


# ---------------------------------------------------------------------------
# Mechanism-family geometry
# ---------------------------------------------------------------------------


def _add_knob(part, *, xyz, s: float, mats, name: str):
    geometry = KnobGeometry(
        0.032 * s,
        0.015 * s,
        body_style="lobed",
        base_diameter=0.025 * s,
        top_diameter=0.030 * s,
        grip=KnobGrip(style="ribbed", count=10, depth=0.0007 * s),
        center=True,
    )
    part.visual(
        mesh_from_geometry(geometry, name),
        origin=Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["edge"],
        name=name, material_class_id="plastic.patterned_textured",
    )


def _add_joint_hub(part, r, mats, prefix: str):
    hub_radius = r.link_width * 0.62
    hub_depth = r.link_depth * 0.48
    hub, rot = _cylinder_y(hub_radius, hub_depth)
    part.visual(hub, origin=Origin(rpy=rot.rpy), material=mats["coat"], name=f"{prefix}__hub", material_class_id="metal.paint_coated")
    bridge_length = hub_radius + 0.030 * r.scale
    part.visual(
        Box((bridge_length, hub_depth * 0.96, r.link_width * 0.48)),
        origin=Origin(xyz=(bridge_length * 0.5, 0.0, 0.0)),
        material=mats["coat"],
        name=f"{prefix}__hub_bridge", material_class_id="metal.paint_coated",
    )
    return hub_radius, hub_depth


def _add_end_fork(part, *, length: float, r, mats, prefix: str):
    child_hub_depth = r.link_depth * 0.48
    gap = 0.0012 * r.scale
    cheek_t = 0.007 * r.scale
    cheek_y = child_hub_depth * 0.5 + gap + cheek_t * 0.5
    cheek_radius = r.link_width * 0.70
    for index, y in enumerate((-cheek_y, cheek_y)):
        cheek, rot = _cylinder_y(cheek_radius, cheek_t)
        part.visual(
            cheek,
            origin=Origin(xyz=(length, y, 0.0), rpy=rot.rpy),
            material=mats["coat"],
            name=f"{prefix}__end_cheek_{index}", material_class_id="metal.paint_coated",
        )
        bridge_length = max(
            r.link_width * 1.15,
            r.link_width * 0.70 + 0.025 * r.scale,
        )
        part.visual(
            Box((bridge_length, cheek_t, r.link_width * 0.34)),
            origin=Origin(xyz=(length - bridge_length * 0.5, y, 0.0)),
            material=mats["coat"],
            name=f"{prefix}__end_bridge_{index}", material_class_id="metal.paint_coated",
        )
    crossbar_length = r.link_width * 0.36
    clearance_radius = max(0.024 * r.scale, r.link_width * 0.70)
    crossbar_near_x = length - clearance_radius - 0.002 * r.scale
    part.visual(
        Box((crossbar_length, 2.0 * cheek_y + cheek_t, r.link_width * 0.34)),
        origin=Origin(xyz=(crossbar_near_x - crossbar_length * 0.5, 0.0, 0.0)),
        material=mats["coat"],
        name=f"{prefix}__end_crossbar", material_class_id="metal.paint_coated",
    )
    knob_depth = 0.015 * r.scale
    axle_length = 2.0 * (cheek_y + cheek_t * 0.5 + knob_depth + 0.002 * r.scale)
    axle, axle_rot = _cylinder_y(0.0015 * r.scale, axle_length)
    part.visual(
        axle,
        origin=Origin(xyz=(length, 0.0, 0.0), rpy=axle_rot.rpy),
        material=mats["metal"],
        name=f"{prefix}__pivot_axle", material_class_id="metal.stainless_matte",
    )
    cap_length = 0.0035 * r.scale
    for index, sign in enumerate((-1.0, 1.0)):
        pin_cap, rot = _cylinder_y(0.006 * r.scale, cap_length)
        part.visual(
            pin_cap,
            origin=Origin(
                xyz=(
                    length,
                    sign * (cheek_y + cheek_t * 0.5 + cap_length * 0.5 - 0.001 * r.scale),
                    0.0,
                ),
                rpy=rot.rpy,
            ),
            material=mats["metal"],
            name=f"{prefix}__pivot_pin_cap_{index}", material_class_id="metal.stainless_matte",
        )
    _add_knob(
        part,
        xyz=(
            length,
            -(cheek_y + cheek_t * 0.5 + knob_depth * 0.5 - 0.0015 * r.scale),
            0.0,
        ),
        s=r.scale,
        mats=mats,
        name=f"{prefix}__friction_knob",
    )
    return cheek_radius


def _add_box_link(part, *, length: float, r, mats, prefix: str, spring: bool):
    hub_radius, _ = _add_joint_hub(part, r, mats, prefix)
    fork_radius = r.link_width * 0.70
    start = hub_radius + 0.010 * r.scale
    stop = length - fork_radius - 0.010 * r.scale
    body_length = stop - start
    part.visual(
        _rounded_bar_mesh(body_length, r.link_width, r.link_depth, f"{prefix}_shell_mesh"),
        origin=Origin(xyz=((start + stop) * 0.5, 0.0, 0.0)),
        material=mats["coat"],
        name=f"{prefix}__shell", material_class_id="metal.paint_coated",
    )
    part.visual(
        _rounded_bar_mesh(
            body_length * 0.94, r.link_width * 0.62, 0.0025 * r.scale, f"{prefix}_face_mesh"
        ),
        origin=Origin(xyz=((start + stop) * 0.5, -r.link_depth * 0.52, 0.0)),
        material=mats["edge"],
        name=f"{prefix}__face", material_class_id="metal.blackened_gunmetal",
    )
    _add_end_fork(part, length=length, r=r, mats=mats, prefix=prefix)
    for index, x in enumerate((start + body_length * 0.36, start + body_length * 0.70)):
        part.visual(
            Box((0.014 * r.scale, r.link_depth * 1.06, 0.009 * r.scale)),
            origin=Origin(xyz=(x, 0.0, -r.link_width * 0.60)),
            material=mats["rubber"],
            name=f"{prefix}__cable_guide_{index}", material_class_id="rubber.smooth_plain",
        )
    if spring:
        part.visual(
            _spring_mesh(
                stop - start, r.link_depth * 0.60, r.link_width * 0.30, f"{prefix}_spring_mesh"
            ),
            origin=Origin(xyz=(start, 0.0, 0.0)),
            material=mats["spring"],
            name=f"{prefix}__extension_spring", material_class_id="metal.steel_bare",
        )


def _add_tubular_link(part, *, length: float, r, mats, prefix: str, gas: bool):
    hub_radius, _ = _add_joint_hub(part, r, mats, prefix)
    fork_radius = r.link_width * 0.70
    start = hub_radius + 0.012 * r.scale
    stop = length - fork_radius - 0.012 * r.scale
    tube_length = stop - start
    tube, rot = _cylinder_x(r.link_width * 0.11, tube_length)
    for index, z in enumerate((-r.link_width * 0.27, r.link_width * 0.27)):
        part.visual(
            tube,
            origin=Origin(xyz=((start + stop) * 0.5, 0.0, z), rpy=rot.rpy),
            material=mats["coat"],
            name=f"{prefix}__tube_{index}", material_class_id="metal.paint_coated",
        )
    part.visual(
        Box((tube_length, r.link_depth * 0.42, r.link_width * 0.24)),
        origin=Origin(xyz=((start + stop) * 0.5, 0.0, 0.0)),
        material=mats["edge"],
        name=f"{prefix}__spine", material_class_id="metal.blackened_gunmetal",
    )
    for index, x in enumerate((start + tube_length * 0.18, start + tube_length * 0.82)):
        part.visual(
            Box((0.012 * r.scale, r.link_depth * 0.34, r.link_width * 0.68)),
            origin=Origin(xyz=(x, 0.0, 0.0)),
            material=mats["edge"],
            name=f"{prefix}__tube_bridge_{index}", material_class_id="metal.blackened_gunmetal",
        )
    _add_end_fork(part, length=length, r=r, mats=mats, prefix=prefix)
    if gas:
        body_len = tube_length * 0.46
        body, body_rot = _cylinder_x(0.0068 * r.scale, body_len)
        part.visual(
            body,
            origin=Origin(
                xyz=(start + body_len * 0.58, r.link_depth * 0.18, -r.link_width * 0.30),
                rpy=body_rot.rpy,
            ),
            material=mats["spring"],
            name=f"{prefix}__gas_strut_body", material_class_id="metal.paint_coated",
        )
        rod_len = tube_length * 0.24
        rod, rod_rot = _cylinder_x(0.0033 * r.scale, rod_len)
        part.visual(
            rod,
            origin=Origin(
                xyz=(
                    start + body_len + rod_len * 0.45,
                    r.link_depth * 0.18,
                    -r.link_width * 0.30,
                ),
                rpy=rod_rot.rpy,
            ),
            material=mats["metal"],
            name=f"{prefix}__gas_strut_rod", material_class_id="metal.chrome_polished",
        )


def _add_parallelogram_link(part, *, length: float, r, mats, prefix: str):
    hub_radius, _ = _add_joint_hub(part, r, mats, prefix)
    fork_radius = r.link_width * 0.70
    start = hub_radius + 0.012 * r.scale
    stop = length - fork_radius - 0.012 * r.scale
    rail_length = stop - start
    part.visual(
        Box((rail_length, r.link_depth * 0.50, r.link_width * 0.12)),
        origin=Origin(xyz=((start + stop) * 0.5, 0.0, 0.0)),
        material=mats["edge"],
        name=f"{prefix}__central_spine", material_class_id="metal.blackened_gunmetal",
    )
    for index, z in enumerate((-r.link_width * 0.30, r.link_width * 0.30)):
        part.visual(
            Box((rail_length, r.link_depth * 0.25, r.link_width * 0.16)),
            origin=Origin(
                xyz=((start + stop) * 0.5, (-0.010 if index == 0 else 0.010) * r.scale, z)
            ),
            material=mats["coat"],
            name=f"{prefix}__rail_{index}", material_class_id="metal.paint_coated",
        )
    for index, x in enumerate((start + rail_length * 0.16, start + rail_length * 0.84)):
        part.visual(
            Box((0.013 * r.scale, r.link_depth * 0.56, r.link_width * 0.74)),
            origin=Origin(xyz=(x, 0.0, 0.0)),
            material=mats["edge"],
            name=f"{prefix}__rail_bridge_{index}", material_class_id="metal.blackened_gunmetal",
        )
    _add_end_fork(part, length=length, r=r, mats=mats, prefix=prefix)
    for index, y in enumerate((-0.014 * r.scale, 0.014 * r.scale)):
        part.visual(
            _spring_mesh(rail_length, y, 0.0, f"{prefix}_constant_spring_{index}", turns=24),
            origin=Origin(xyz=(start, 0.0, 0.0)),
            material=mats["spring"],
            name=f"{prefix}__constant_force_spring_{index}", material_class_id="metal.steel_bare",
        )


def _add_swivel_fork(swivel, r, mats, family: str):
    child_hub_depth = r.link_depth * 0.48
    gap = 0.0012 * r.scale
    cheek_t = 0.007 * r.scale
    cheek_y = child_hub_depth * 0.5 + gap + cheek_t * 0.5
    post_length = r.shoulder_height - r.link_width * 0.76
    swivel.visual(
        Cylinder(radius=0.018 * r.scale, length=post_length),
        origin=Origin(xyz=(0.0, 0.0, post_length * 0.5)),
        material=mats["coat"],
        name=f"mechanism_family__{family}__swivel_post", material_class_id="metal.paint_coated",
    )
    swivel.visual(
        Cylinder(radius=0.031 * r.scale, length=0.010 * r.scale),
        origin=Origin(xyz=(0.0, 0.0, 0.006 * r.scale)),
        material=mats["edge"],
        name=f"mechanism_family__{family}__swivel_flange", material_class_id="metal.blackened_gunmetal",
    )
    for index, y in enumerate((-cheek_y, cheek_y)):
        cheek, rot = _cylinder_y(r.link_width * 0.70, cheek_t)
        swivel.visual(
            cheek,
            origin=Origin(xyz=(0.0, y, r.shoulder_height), rpy=rot.rpy),
            material=mats["coat"],
            name=f"mechanism_family__{family}__shoulder_cheek_{index}", material_class_id="metal.paint_coated",
        )
        swivel.visual(
            Box((r.link_width * 0.34, cheek_t, r.link_width * 1.05)),
            origin=Origin(xyz=(0.0, y, r.shoulder_height - r.link_width * 0.52)),
            material=mats["coat"],
            name=f"mechanism_family__{family}__shoulder_bridge_{index}", material_class_id="metal.paint_coated",
        )
    knob_depth = 0.015 * r.scale
    axle_length = 2.0 * (cheek_y + cheek_t * 0.5 + knob_depth + 0.002 * r.scale)
    axle, axle_rot = _cylinder_y(0.0015 * r.scale, axle_length)
    swivel.visual(
        axle,
        origin=Origin(xyz=(0.0, 0.0, r.shoulder_height), rpy=axle_rot.rpy),
        material=mats["metal"],
        name=f"mechanism_family__{family}__shoulder_axle", material_class_id="metal.stainless_matte",
    )
    cap_length = 0.0035 * r.scale
    for index, sign in enumerate((-1.0, 1.0)):
        pin_cap, rot = _cylinder_y(0.006 * r.scale, cap_length)
        swivel.visual(
            pin_cap,
            origin=Origin(
                xyz=(
                    0.0,
                    sign * (cheek_y + cheek_t * 0.5 + cap_length * 0.5 - 0.001 * r.scale),
                    r.shoulder_height,
                ),
                rpy=rot.rpy,
            ),
            material=mats["metal"],
            name=f"mechanism_family__{family}__shoulder_pin_cap_{index}", material_class_id="metal.stainless_matte",
        )
    _add_knob(
        swivel,
        xyz=(
            0.0,
            -(cheek_y + cheek_t * 0.5 + knob_depth * 0.5 - 0.0015 * r.scale),
            r.shoulder_height,
        ),
        s=r.scale,
        mats=mats,
        name=f"mechanism_family__{family}__shoulder_friction_knob",
    )


def _build_mechanism(model, base, root_axis, r, mats, *, style: str):
    family = r.mechanism_family
    swivel = model.part(f"mechanism_family__{family}__swivel")
    _add_swivel_fork(swivel, r, mats, family)
    _add_axis_joint(
        model,
        name=f"mechanism_family__{family}__base_yaw",
        parent=base,
        child=swivel,
        provider=root_axis,
        consumer=AxisInterface(
            name=f"mechanism_family.{family}.root_axis",
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
        ),
        lower=-1.55,
        upper=1.55,
    )

    links = []
    parent = swivel
    for index, (length, angle) in enumerate(zip(r.link_lengths, r.neutral_angles, strict=True)):
        local_name = "terminal_link" if index == len(r.link_lengths) - 1 else f"link_{index}"
        prefix = f"mechanism_family__{family}__{local_name}"
        link = model.part(prefix)
        if style == "box":
            _add_box_link(link, length=length, r=r, mats=mats, prefix=prefix, spring=True)
        elif style == "torsion":
            _add_box_link(link, length=length, r=r, mats=mats, prefix=prefix, spring=False)
            coil = TorusGeometry(
                r.link_width * 0.50, r.link_width * 0.075, radial_segments=16, tubular_segments=30
            ).rotate_x(math.pi / 2.0)
            link.visual(
                mesh_from_geometry(coil, f"{prefix}_torsion_mesh"),
                material=mats["spring"],
                name=f"{prefix}__torsion_coil", material_class_id="metal.steel_bare",
            )
        elif style == "tubular":
            _add_tubular_link(link, length=length, r=r, mats=mats, prefix=prefix, gas=index == 0)
        elif style == "three_link":
            _add_box_link(link, length=length, r=r, mats=mats, prefix=prefix, spring=index == 1)
        else:
            _add_parallelogram_link(link, length=length, r=r, mats=mats, prefix=prefix)

        provider_point = (
            (0.0, 0.0, r.shoulder_height) if index == 0 else (r.link_lengths[index - 1], 0.0, 0.0)
        )
        _add_axis_joint(
            model,
            name=f"mechanism_family__{family}__joint_{index}_pitch",
            parent=parent,
            child=link,
            provider=AxisInterface(
                name=f"mechanism_family.{family}.joint_{index}_axis",
                point=provider_point,
                axis=(0.0, 1.0, 0.0),
                radial=(math.cos(angle), 0.0, math.sin(angle)),
            ),
            consumer=AxisInterface(
                name=f"mechanism_family.{family}.link_{index}_axis",
                axis=(0.0, 1.0, 0.0),
                radial=(1.0, 0.0, 0.0),
            ),
            lower=-0.30 if index == 0 else -0.38,
            upper=0.34 if index == 0 else 0.42,
        )
        links.append(link)
        parent = link

    if style == "three_link":
        first = links[0]
        y = r.link_depth * 0.52
        points = (
            (0.040, y, 0.010),
            (r.link_lengths[0] * 0.62, y, 0.030),
            (r.link_lengths[0] * 0.78, y, -0.095 * r.scale),
        )
        first.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    points,
                    radius=0.0015 * r.scale,
                    samples_per_segment=12,
                    radial_segments=8,
                    cap_ends=True,
                ),
                f"mechanism_family__{family}_counterweight_cable",
            ),
            material=mats["metal"],
            name=f"mechanism_family__{family}__counterweight_cable", material_class_id="tech.cable_pipe_bundle",
        )
        first.visual(
            Box((0.014 * r.scale, y + 0.006 * r.scale, 0.010 * r.scale)),
            origin=Origin(xyz=(0.040 * r.scale, y * 0.5, 0.010 * r.scale)),
            material=mats["metal"],
            name=f"mechanism_family__{family}__counterweight_cable_anchor", material_class_id="metal.stainless_matte",
        )
        first.visual(
            Cylinder(radius=0.017 * r.scale, length=0.048 * r.scale),
            origin=Origin(xyz=(r.link_lengths[0] * 0.78, y, -0.117 * r.scale)),
            material=mats["accent"],
            name=f"mechanism_family__{family}__counterweight", material_class_id="metal.paint_coated",
        )

    terminal_link = links[-1]
    return terminal_link, AxisInterface(
        name=f"mechanism_family.{family}.terminal_axis",
        point=(r.link_lengths[-1], 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
    )


def _mechanism_family_folded_extension_build(model, base, root_axis, r, mats, assets):
    return _build_mechanism(model, base, root_axis, r, mats, style="box")


def _mechanism_family_low_profile_extension_build(model, base, root_axis, r, mats, assets):
    return _build_mechanism(model, base, root_axis, r, mats, style="box")


def _mechanism_family_wall_swing_torsion_build(model, base, root_axis, r, mats, assets):
    return _build_mechanism(model, base, root_axis, r, mats, style="torsion")


def _mechanism_family_tubular_gas_build(model, base, root_axis, r, mats, assets):
    return _build_mechanism(model, base, root_axis, r, mats, style="tubular")


def _mechanism_family_three_link_counterweight_build(model, base, root_axis, r, mats, assets):
    return _build_mechanism(model, base, root_axis, r, mats, style="three_link")


def _mechanism_family_parallelogram_constant_force_build(model, base, root_axis, r, mats, assets):
    return _build_mechanism(model, base, root_axis, r, mats, style="parallelogram")


_MECHANISM_BUILDERS = {
    "folded_extension": _mechanism_family_folded_extension_build,
    "low_profile_extension": _mechanism_family_low_profile_extension_build,
    "wall_swing_torsion": _mechanism_family_wall_swing_torsion_build,
    "tubular_gas": _mechanism_family_tubular_gas_build,
    "three_link_counterweight": _mechanism_family_three_link_counterweight_build,
    "parallelogram_constant_force": _mechanism_family_parallelogram_constant_force_build,
}


# ---------------------------------------------------------------------------
# Terminal candidates
# ---------------------------------------------------------------------------


def _terminal_hub(part, r, mats, prefix: str):
    depth = r.link_depth * 0.48
    hub, rot = _cylinder_y(0.024 * r.scale, depth)
    part.visual(hub, origin=Origin(rpy=rot.rpy), material=mats["coat"], name=f"{prefix}__wrist_hub", material_class_id="metal.paint_coated")


def _attach_terminal(model, parent, provider, part, r, name: str):
    _add_axis_joint(
        model,
        name=name,
        parent=parent,
        child=part,
        provider=provider,
        consumer=AxisInterface(
            name=f"terminal_mount.{r.terminal_mount}.wrist_axis",
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
        ),
        lower=-0.48,
        upper=0.48,
    )


def _terminal_mount_threaded_adapter_build(model, parent, provider, r, mats, assets):
    prefix = "terminal_mount__threaded_adapter"
    part = model.part(f"{prefix}__mount")
    s = r.scale
    _terminal_hub(part, r, mats, prefix)
    part.visual(
        Box((0.060 * s, 0.018 * s, 0.022 * s)),
        origin=Origin(xyz=(0.052 * s, 0.0, 0.0)),
        material=mats["coat"],
        name=f"{prefix}__drop", material_class_id="metal.paint_coated",
    )
    stud, rot = _cylinder_x(0.0055 * s, 0.046 * s)
    part.visual(
        stud,
        origin=Origin(xyz=(0.104 * s, 0.0, 0.0), rpy=rot.rpy),
        material=mats["metal"],
        name=f"{prefix}__threaded_stud", material_class_id="metal.stainless_matte",
    )
    collar, collar_rot = _cylinder_x(0.014 * s, 0.012 * s)
    part.visual(
        collar,
        origin=Origin(xyz=(0.078 * s, 0.0, 0.0), rpy=collar_rot.rpy),
        material=mats["edge"],
        name=f"{prefix}__collar", material_class_id="metal.blackened_gunmetal",
    )
    _attach_terminal(model, parent, provider, part, r, f"{prefix}__pitch")
    return part


def _terminal_mount_studio_cradle_build(model, parent, provider, r, mats, assets):
    prefix = "terminal_mount__studio_cradle"
    part = model.part(f"{prefix}__mount")
    s = r.scale
    _terminal_hub(part, r, mats, prefix)
    part.visual(
        Box((0.078 * s, 0.018 * s, 0.022 * s)),
        origin=Origin(xyz=(0.045 * s, 0.0, 0.0)),
        material=mats["coat"],
        name=f"{prefix}__drop", material_class_id="metal.paint_coated",
    )
    for index, y in enumerate((-0.042, 0.042)):
        part.visual(
            Box((0.075 * s, 0.012 * s, 0.016 * s)),
            origin=Origin(xyz=(0.112 * s, y * s, 0.0)),
            material=mats["coat"],
            name=f"{prefix}__yoke_arm_{index}", material_class_id="metal.paint_coated",
        )
    part.visual(
        Box((0.020 * s, 0.096 * s, 0.016 * s)),
        origin=Origin(xyz=(0.079 * s, 0.0, 0.0)),
        material=mats["coat"],
        name=f"{prefix}__yoke_root", material_class_id="metal.paint_coated",
    )
    crossbar, rot = _cylinder_y(0.0055 * s, 0.096 * s)
    part.visual(
        crossbar,
        origin=Origin(xyz=(0.148 * s, 0.0, 0.0), rpy=rot.rpy),
        material=mats["metal"],
        name=f"{prefix}__crossbar", material_class_id="metal.chrome_polished",
    )
    part.visual(
        Cylinder(radius=0.022 * s, length=0.140 * s),
        origin=Origin(xyz=(0.148 * s, 0.0, 0.066 * s)),
        material=mats["edge"],
        name=f"{prefix}__microphone_body", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Sphere(radius=0.028 * s),
        origin=Origin(xyz=(0.148 * s, 0.0, 0.146 * s)),
        material=mats["metal"],
        name=f"{prefix}__grille", material_class_id="metal.mesh_chainmail",
    )
    _attach_terminal(model, parent, provider, part, r, f"{prefix}__pitch")
    return part


def _terminal_mount_shock_mount_build(model, parent, provider, r, mats, assets):
    prefix = "terminal_mount__shock_mount"
    part = model.part(f"{prefix}__mount")
    s = r.scale
    _terminal_hub(part, r, mats, prefix)
    part.visual(
        Box((0.080 * s, 0.018 * s, 0.022 * s)),
        origin=Origin(xyz=(0.060 * s, 0.0, 0.0)),
        material=mats["coat"],
        name=f"{prefix}__drop", material_class_id="metal.paint_coated",
    )
    ring = TorusGeometry(0.045 * s, 0.004 * s, radial_segments=18, tubular_segments=36)
    part.visual(
        mesh_from_geometry(ring, "shock_ring"),
        origin=Origin(xyz=(0.125 * s, 0.0, 0.0)),
        material=mats["edge"],
        name=f"{prefix}__ring", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.019 * s, length=0.016 * s),
        origin=Origin(xyz=(0.125 * s, 0.0, 0.0)),
        material=mats["rubber"],
        name=f"{prefix}__collar", material_class_id="rubber.smooth_plain",
    )
    for index, (x, y) in enumerate(((0.032, 0.0), (-0.032, 0.0), (0.0, 0.032), (0.0, -0.032))):
        part.visual(
            Box((0.024 * s if x else 0.005 * s, 0.005 * s if x else 0.024 * s, 0.004 * s)),
            origin=Origin(xyz=((0.125 + x * 0.5) * s, y * 0.5 * s, 0.0)),
            material=mats["rubber"],
            name=f"{prefix}__elastomer_{index}", material_class_id="rubber.smooth_plain",
        )
    part.visual(
        Cylinder(radius=0.019 * s, length=0.122 * s),
        origin=Origin(xyz=(0.125 * s, 0.0, 0.067 * s)),
        material=mats["edge"],
        name=f"{prefix}__microphone_body", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.024 * s, length=0.052 * s),
        origin=Origin(xyz=(0.125 * s, 0.0, 0.149 * s)),
        material=mats["metal"],
        name=f"{prefix}__grille", material_class_id="metal.mesh_chainmail",
    )
    part.visual(
        Box((0.050 * s, 0.007 * s, 0.064 * s)),
        origin=Origin(xyz=(0.190 * s, 0.0, 0.122 * s)),
        material=mats["edge"],
        name=f"{prefix}__pop_filter", material_class_id="fabric.open_mesh",
    )
    neck = (
        (0.140 * s, 0.0, 0.018 * s),
        (0.178 * s, 0.0, 0.060 * s),
        (0.190 * s, 0.0, 0.093 * s),
    )
    part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                neck, radius=0.0025 * s, samples_per_segment=10, radial_segments=8, cap_ends=True
            ),
            "pop_filter_neck",
        ),
        material=mats["coat"],
        name=f"{prefix}__pop_filter_neck", material_class_id="metal.paint_coated",
    )
    _attach_terminal(model, parent, provider, part, r, f"{prefix}__pitch")
    return part


_TERMINAL_BUILDERS = {
    "threaded_adapter": _terminal_mount_threaded_adapter_build,
    "studio_cradle": _terminal_mount_studio_cradle_build,
    "shock_mount": _terminal_mount_shock_mount_build,
}


def build_microphone_boom_arm(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r)
    base, root_axis = _BASE_BUILDERS[r.base_mount](model, r, mats, assets)
    terminal_parent, terminal_axis = _MECHANISM_BUILDERS[r.mechanism_family](
        model, base, root_axis, r, mats, assets
    )
    _TERMINAL_BUILDERS[r.terminal_mount](model, terminal_parent, terminal_axis, r, mats, assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/microphone_boom_arm"
    return model


def build_seeded_microphone_boom_arm(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_microphone_boom_arm(config_from_seed(seed), assets=assets)


def run_microphone_boom_arm_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    parts = {part.name for part in object_model.parts}
    rotational = [
        joint
        for joint in object_model.articulations
        if joint.articulation_type in {ArticulationType.REVOLUTE, ArticulationType.CONTINUOUS}
    ]
    ctx.check("selected base exists", f"base_mount__{r.base_mount}__base" in parts)
    ctx.check(
        "selected swivel exists",
        f"mechanism_family__{r.mechanism_family}__swivel" in parts,
    )
    ctx.check(
        "selected terminal exists",
        f"terminal_mount__{r.terminal_mount}__mount" in parts,
    )
    link_prefix = f"mechanism_family__{r.mechanism_family}__"
    links = {
        name
        for name in parts
        if name.startswith(f"{link_prefix}link_") or name == f"{link_prefix}terminal_link"
    }
    ctx.check(
        "structural family emits its full link graph",
        len(links) == len(r.link_lengths),
        details=f"expected={len(r.link_lengths)}, actual={sorted(links)}",
    )
    ctx.check(
        "all boom motion is bounded and explicit",
        len(rotational) == len(r.link_lengths) + 2
        and all(joint.motion_limits is not None for joint in rotational),
    )
    ctx.check(
        "domain choices are recorded",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "compact_sections_and_reach",
        {"overall_scale": 0.88, "reach_scale": 0.88, "section_scale": 0.88},
        reason="lower continuous geometry boundaries",
    ),
    corner_case(
        "large_sections_and_reach",
        {"overall_scale": 1.12, "reach_scale": 1.12, "section_scale": 1.12},
        reason="upper continuous geometry boundaries",
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
    "build_microphone_boom_arm",
    "build_seeded_microphone_boom_arm",
    "run_microphone_boom_arm_tests",
]
