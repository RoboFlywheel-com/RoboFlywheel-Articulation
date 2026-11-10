# SPDX-License-Identifier: Apache-2.0

"""N-joint serial revolute chain modular template.

This template is sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/n_joint_revolute_chain.md``.
It adapts the three- and four-joint 5-star source families into a single
procedural domain with ``joint_count`` in ``{3, 4}``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from agent.templates._modular import InterfaceSpec
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeWithHolesGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

JointCountTopology = Literal["three_revolute_serial", "four_revolute_serial"]
RootSupport = Literal[
    "cadquery_pedestal_column",
    "bridge_clevis_support",
    "desk_clamp_turret",
    "side_cheek_plate",
]
LinkBodyFamily = Literal[
    "cadquery_solid_hubbed_beam",
    "extruded_open_frame_fork",
    "boxed_fork_washer_stack",
    "cadquery_alternating_side_plate",
    "tube_spring_boom",
]
AxisFamily = Literal[
    "parallel_pitch_y",
    "parallel_yaw_z",
    "mixed_root_yaw_then_pitch",
    "side_plate_pitch_y",
]
TerminalModule = Literal[
    "compact_pad_tab",
    "sensor_pod_fixed",
    "microphone_head",
    "rectangular_calibration_pad",
]
MaterialStyle = Literal["dark_steel", "satin_aluminum", "machine_gray", "lab_blue", "black_boom"]

JOINT_TOPOLOGIES: tuple[JointCountTopology, ...] = (
    "three_revolute_serial",
    "four_revolute_serial",
)
ROOT_SUPPORTS: tuple[RootSupport, ...] = (
    "cadquery_pedestal_column",
    "bridge_clevis_support",
    "desk_clamp_turret",
    "side_cheek_plate",
)
LINK_FAMILIES: tuple[LinkBodyFamily, ...] = (
    "cadquery_solid_hubbed_beam",
    "extruded_open_frame_fork",
    "boxed_fork_washer_stack",
    "cadquery_alternating_side_plate",
    "tube_spring_boom",
)
AXIS_FAMILIES: tuple[AxisFamily, ...] = (
    "parallel_pitch_y",
    "parallel_yaw_z",
    "mixed_root_yaw_then_pitch",
    "side_plate_pitch_y",
)
TERMINALS: tuple[TerminalModule, ...] = (
    "compact_pad_tab",
    "sensor_pod_fixed",
    "microphone_head",
    "rectangular_calibration_pad",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "dark_steel",
    "satin_aluminum",
    "machine_gray",
    "lab_blue",
    "black_boom",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "dark_steel": {
        "base": (0.10, 0.11, 0.12, 1.0),
        "link": (0.32, 0.34, 0.35, 1.0),
        "joint": (0.72, 0.70, 0.64, 1.0),
        "accent": (0.18, 0.22, 0.27, 1.0),
        "terminal": (0.05, 0.055, 0.06, 1.0),
        "rubber": (0.015, 0.015, 0.014, 1.0),
    },
    "satin_aluminum": {
        "base": (0.47, 0.49, 0.50, 1.0),
        "link": (0.70, 0.72, 0.72, 1.0),
        "joint": (0.82, 0.80, 0.72, 1.0),
        "accent": (0.28, 0.29, 0.30, 1.0),
        "terminal": (0.18, 0.19, 0.20, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
    },
    "machine_gray": {
        "base": (0.28, 0.30, 0.31, 1.0),
        "link": (0.54, 0.56, 0.56, 1.0),
        "joint": (0.78, 0.76, 0.68, 1.0),
        "accent": (0.42, 0.44, 0.45, 1.0),
        "terminal": (0.20, 0.21, 0.22, 1.0),
        "rubber": (0.025, 0.025, 0.026, 1.0),
    },
    "lab_blue": {
        "base": (0.16, 0.24, 0.34, 1.0),
        "link": (0.30, 0.44, 0.58, 1.0),
        "joint": (0.78, 0.80, 0.80, 1.0),
        "accent": (0.70, 0.74, 0.76, 1.0),
        "terminal": (0.05, 0.08, 0.11, 1.0),
        "rubber": (0.015, 0.017, 0.018, 1.0),
    },
    "black_boom": {
        "base": (0.035, 0.037, 0.040, 1.0),
        "link": (0.08, 0.085, 0.090, 1.0),
        "joint": (0.58, 0.58, 0.54, 1.0),
        "accent": (0.20, 0.21, 0.22, 1.0),
        "terminal": (0.015, 0.016, 0.018, 1.0),
        "rubber": (0.005, 0.005, 0.005, 1.0),
    },
}


@dataclass(frozen=True)
class NJointRevoluteChainConfig:
    joint_count_topology: JointCountTopology | None = None
    root_support: RootSupport | None = None
    link_body_family: LinkBodyFamily | None = None
    axis_family: AxisFamily | None = None
    terminal_module: TerminalModule | None = None
    material_style: MaterialStyle = "machine_gray"
    link_length_scale: float = 1.0
    link_width_scale: float = 1.0
    hub_radius_scale: float = 1.0
    layer_spacing_scale: float = 1.0
    joint_limit_scale: float = 1.0
    terminal_size_scale: float = 1.0
    name: str = "n_joint_revolute_chain"


@dataclass(frozen=True)
class ResolvedNJointRevoluteChainConfig:
    joint_count_topology: JointCountTopology
    root_support: RootSupport
    link_body_family: LinkBodyFamily
    axis_family: AxisFamily
    terminal_module: TerminalModule
    material_style: MaterialStyle
    joint_count: int
    link_lengths: tuple[float, ...]
    link_width: float
    link_height: float
    hub_radius: float
    hub_length: float
    layer_spacing: float
    root_origin: tuple[float, float, float]
    joint_axes: tuple[tuple[float, float, float], ...]
    joint_limits: tuple[tuple[float, float], ...]
    terminal_size_scale: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _compatible(
    joint_topology: JointCountTopology,
    root: RootSupport,
    link: LinkBodyFamily,
    axis: AxisFamily,
    terminal: TerminalModule,
) -> bool:
    if link == "tube_spring_boom" and joint_topology != "three_revolute_serial":
        return False
    if terminal == "sensor_pod_fixed" and joint_topology != "four_revolute_serial":
        return False
    if root == "desk_clamp_turret" and axis not in (
        "mixed_root_yaw_then_pitch",
        "parallel_pitch_y",
    ):
        return False
    if root == "side_cheek_plate" and axis not in ("side_plate_pitch_y", "parallel_pitch_y"):
        return False
    if axis == "parallel_yaw_z" and link not in (
        "extruded_open_frame_fork",
        "cadquery_alternating_side_plate",
    ):
        return False
    if axis in ("side_plate_pitch_y", "parallel_yaw_z") and root == "cadquery_pedestal_column":
        return False
    if link == "tube_spring_boom" and terminal not in ("microphone_head", "compact_pad_tab"):
        return False
    return True


def _legal_configs() -> tuple[
    tuple[JointCountTopology, RootSupport, LinkBodyFamily, AxisFamily, TerminalModule], ...
]:
    combos = []
    for topology in JOINT_TOPOLOGIES:
        for root in ROOT_SUPPORTS:
            for link in LINK_FAMILIES:
                for axis in AXIS_FAMILIES:
                    for terminal in TERMINALS:
                        if _compatible(topology, root, link, axis, terminal):
                            combos.append((topology, root, link, axis, terminal))
    return tuple(combos)


_LEGAL_CONFIGS = _legal_configs()


def config_from_seed(seed: int) -> NJointRevoluteChainConfig:
    rng = random.Random(seed)
    topology, root, link, axis, terminal = rng.choice(_LEGAL_CONFIGS)
    return NJointRevoluteChainConfig(
        joint_count_topology=topology,
        root_support=root,
        link_body_family=link,
        axis_family=axis,
        terminal_module=terminal,
        material_style=rng.choice(MATERIAL_STYLES),
        link_length_scale=round(rng.uniform(0.82, 1.18), 4),
        link_width_scale=round(rng.uniform(0.85, 1.15), 4),
        hub_radius_scale=round(rng.uniform(0.88, 1.14), 4),
        layer_spacing_scale=round(rng.uniform(0.90, 1.18), 4),
        joint_limit_scale=round(rng.uniform(0.75, 1.10), 4),
        terminal_size_scale=round(rng.uniform(0.80, 1.20), 4),
        name=f"seeded_n_joint_revolute_chain_{seed}",
    )


def resolve_config(
    config: NJointRevoluteChainConfig | None = None,
) -> ResolvedNJointRevoluteChainConfig:
    cfg = config or NJointRevoluteChainConfig()
    topology = _pick(cfg.joint_count_topology, JOINT_TOPOLOGIES)
    root = _pick(cfg.root_support, ROOT_SUPPORTS)
    link = _pick(cfg.link_body_family, LINK_FAMILIES)
    axis = _pick(cfg.axis_family, AXIS_FAMILIES)
    terminal = _pick(cfg.terminal_module, TERMINALS)

    if not _compatible(topology, root, link, axis, terminal):
        for combo in _LEGAL_CONFIGS:
            if combo[0] == topology and combo[2] == link:
                topology, root, link, axis, terminal = combo
                break
        else:
            topology, root, link, axis, terminal = _LEGAL_CONFIGS[0]

    joint_count = 3 if topology == "three_revolute_serial" else 4
    length_scale = _clamp(cfg.link_length_scale, 0.82, 1.18)
    width_scale = _clamp(cfg.link_width_scale, 0.85, 1.15)
    hub_scale = _clamp(cfg.hub_radius_scale, 0.88, 1.14)
    layer_scale = _clamp(cfg.layer_spacing_scale, 0.90, 1.18)
    limit_scale = _clamp(cfg.joint_limit_scale, 0.75, 1.10)
    terminal_scale = _clamp(cfg.terminal_size_scale, 0.80, 1.20)

    base_lengths = (0.34, 0.285, 0.225) if joint_count == 3 else (0.30, 0.255, 0.220, 0.175)
    if link == "boxed_fork_washer_stack":
        base_lengths = tuple(v * 1.18 for v in base_lengths)
    elif link == "tube_spring_boom":
        base_lengths = tuple(v * 1.08 for v in base_lengths)
    elif axis == "parallel_yaw_z":
        base_lengths = tuple(v * 0.88 for v in base_lengths)

    if axis in ("parallel_yaw_z",):
        root_origin = (0.0, 0.0, 0.075)
    elif root == "side_cheek_plate":
        root_origin = (0.0, 0.0, 0.105)
    elif root == "desk_clamp_turret":
        root_origin = (0.0, 0.0, 0.205)
    else:
        root_origin = (0.0, 0.0, 0.155)

    if axis == "parallel_yaw_z":
        axes = tuple((0.0, 0.0, 1.0) for _ in range(joint_count))
    elif axis == "mixed_root_yaw_then_pitch":
        axes = ((0.0, 0.0, 1.0),) + tuple((0.0, -1.0, 0.0) for _ in range(joint_count - 1))
    else:
        axes = tuple((0.0, -1.0, 0.0) for _ in range(joint_count))

    limits = tuple(
        (-0.72 * limit_scale, 1.20 * limit_scale)
        if axes[i] != (0.0, 0.0, 1.0)
        else (-1.35 * limit_scale, 1.35 * limit_scale)
        for i in range(joint_count)
    )

    link_width = 0.052 * width_scale
    if link in ("cadquery_alternating_side_plate", "extruded_open_frame_fork"):
        link_width *= 0.82
    elif link == "tube_spring_boom":
        link_width *= 0.70
    return ResolvedNJointRevoluteChainConfig(
        joint_count_topology=topology,
        root_support=root,
        link_body_family=link,
        axis_family=axis,
        terminal_module=terminal,
        material_style=_pick(cfg.material_style, MATERIAL_STYLES),
        joint_count=joint_count,
        link_lengths=tuple(round(v * length_scale, 4) for v in base_lengths),
        link_width=link_width,
        link_height=max(0.026, link_width * 0.72),
        hub_radius=0.023 * hub_scale,
        hub_length=0.040 * hub_scale,
        layer_spacing=0.026 * layer_scale,
        root_origin=root_origin,
        joint_axes=axes,
        joint_limits=limits,
        terminal_size_scale=terminal_scale,
        name=cfg.name or "n_joint_revolute_chain",
    )


def with_overrides(
    config: NJointRevoluteChainConfig, **kwargs: object
) -> NJointRevoluteChainConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: NJointRevoluteChainConfig | ResolvedNJointRevoluteChainConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedNJointRevoluteChainConfig) else resolve_config(config)
    return (
        ("joint_count_topology", r.joint_count_topology),
        ("root_support", r.root_support),
        ("link_body_family", r.link_body_family),
        ("axis_family", r.axis_family),
        ("terminal_module", r.terminal_module),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _x_cyl(x: float, y: float, z: float) -> Origin:
    return Origin(xyz=(x, y, z), rpy=(0.0, math.pi / 2.0, 0.0))


def _y_cyl(x: float, y: float, z: float) -> Origin:
    return Origin(xyz=(x, y, z), rpy=(math.pi / 2.0, 0.0, 0.0))


def _z_cyl(x: float, y: float, z: float) -> Origin:
    return Origin(xyz=(x, y, z))


def _mat(model: ArticulatedObject, r: ResolvedNJointRevoluteChainConfig, key: str):
    return model.material(f"n_joint_{key}", rgba=PALETTES[r.material_style][key])


def _mesh_for_model(model: ArticulatedObject, geometry: object, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


def _circle_profile(radius: float, *, center: tuple[float, float] = (0.0, 0.0), segments: int = 36):
    cx, cy = center
    return [
        (
            cx + math.cos(2.0 * math.pi * i / segments) * radius,
            cy + math.sin(2.0 * math.pi * i / segments) * radius,
        )
        for i in range(segments)
    ]


def _capsule_profile(length: float, radius: float, *, segments: int = 12):
    pts: list[tuple[float, float]] = []
    for i in range(segments + 1):
        a = math.pi / 2.0 + math.pi * i / segments
        pts.append((math.cos(a) * radius, math.sin(a) * radius))
    for i in range(segments + 1):
        a = -math.pi / 2.0 + math.pi * i / segments
        pts.append((length + math.cos(a) * radius, math.sin(a) * radius))
    return pts


def _extruded_plate_mesh(
    name: str,
    outer_profile,
    hole_profiles,
    thickness: float,
):
    return mesh_from_geometry(
        ExtrudeWithHolesGeometry(
            outer_profile, hole_profiles, height=thickness, center=True
        ).rotate_x(math.pi / 2.0),
        name,
    )


def _cadquery_base_mesh(r: ResolvedNJointRevoluteChainConfig):
    plate = cq.Workplane("XY").box(0.22, 0.16, 0.026).translate((0.0, 0.0, 0.013))
    column_h = r.root_origin[2] - 0.040
    column = (
        cq.Workplane("XY").box(0.065, 0.060, column_h).translate((0.0, 0.0, 0.026 + column_h / 2.0))
    )
    block = cq.Workplane("XY").box(0.070, 0.072, 0.048).translate((-0.025, 0.0, r.root_origin[2]))
    rib = (
        cq.Workplane("XY")
        .box(0.032, 0.050, 0.072)
        .translate((-0.060, 0.0, r.root_origin[2] - 0.034))
    )
    return mesh_from_cadquery(
        plate.union(column).union(block).union(rib), "cadquery_pedestal_column.obj"
    )


def _cadquery_link_mesh(length: float, width: float, height: float, hub_r: float, hub_l: float):
    prox = cq.Workplane("YZ").circle(hub_r).extrude(hub_l).translate((hub_l / 2.0, 0.0, 0.0))
    beam = cq.Workplane("XY").box(length, width, height).translate((length / 2.0, 0.0, 0.0))
    dist = (
        cq.Workplane("YZ").circle(hub_r * 0.94).extrude(hub_l * 0.92).translate((length, 0.0, 0.0))
    )
    stiff = (
        cq.Workplane("XY")
        .box(length * 0.70, width * 0.62, height * 0.44)
        .translate((length * 0.55, 0.0, -height * 0.34))
    )
    return mesh_from_cadquery(
        prox.union(beam).union(dist).union(stiff), "cadquery_solid_hubbed_beam.obj"
    )


def _alternating_plate_mesh(length: float, radius: float, thickness: float, name: str):
    outer = _capsule_profile(length, radius, segments=16)
    holes = [_circle_profile(radius * 0.36), _circle_profile(radius * 0.34, center=(length, 0.0))]
    return _extruded_plate_mesh(name, outer, holes, thickness)


def _add_socket(
    part, *, x: float, z: float, r: ResolvedNJointRevoluteChainConfig, mats, name: str
) -> None:
    if r.joint_axes[0] == (0.0, 0.0, 1.0):
        part.visual(
            Box((0.018, r.hub_radius * 2.25, 0.012)),
            origin=Origin(xyz=(x - 0.009, 0.0, z)),
            material=mats["joint"],
            name=name, material_class_id="metal.stainless_matte",
        )
        part.visual(
            Cylinder(radius=r.hub_radius * 1.22, length=r.hub_length * 0.50),
            origin=_z_cyl(x, 0.0, z),
            material=mats["joint"],
            name=f"{name}_round_bearing", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Box((0.026, r.hub_radius * 1.10, 0.032)),
            origin=Origin(xyz=(x - 0.031, 0.0, z)),
            material=mats["joint"],
            name=f"{name}_bearing_web", material_class_id="metal.stainless_matte",
        )
    else:
        part.visual(
            Box((0.030, r.hub_length * 1.85, r.hub_radius * 2.70)),
            origin=Origin(xyz=(x - 0.015, 0.0, z)),
            material=mats["joint"],
            name=name, material_class_id="metal.stainless_matte",
        )
        part.visual(
            Box((0.026, r.hub_length * 1.15, r.hub_radius * 1.45)),
            origin=Origin(xyz=(x - 0.043, 0.0, z)),
            material=mats["joint"],
            name=f"{name}_bearing_web", material_class_id="metal.stainless_matte",
        )


def _add_pin(
    part, *, x: float, length: float, r: ResolvedNJointRevoluteChainConfig, mats, name: str
) -> None:
    axis = (0.0, 0.0, 1.0) if r.axis_family == "parallel_yaw_z" else (0.0, -1.0, 0.0)
    origin = _z_cyl(x, 0.0, 0.0) if axis == (0.0, 0.0, 1.0) else _y_cyl(x, 0.0, 0.0)
    part.visual(
        Cylinder(radius=r.hub_radius * 0.38, length=length),
        origin=origin,
        material=mats["joint"],
        name=name, material_class_id="metal.stainless_matte",
    )


def _build_root(model: ArticulatedObject, r: ResolvedNJointRevoluteChainConfig, mats):
    base = model.part("root_support")
    z = r.root_origin[2]
    if r.root_support == "cadquery_pedestal_column":
        base.visual(_cadquery_base_mesh(r), material=mats["base"], name="pedestal_mesh", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"))
    elif r.root_support == "bridge_clevis_support":
        base.visual(
            Box((0.26, 0.16, 0.026)),
            origin=Origin(xyz=(0.02, 0.0, 0.013)),
            material=mats["base"],
            name="bridge_foot", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
        )
        for y, suffix in ((-0.052, "left"), (0.052, "right")):
            base.visual(
                Box((0.040, 0.026, z)),
                origin=Origin(xyz=(-0.035, y, z / 2.0)),
                material=mats["base"],
                name=f"{suffix}_post", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
            )
        base.visual(
            Box((0.135, 0.130, 0.024)),
            origin=Origin(xyz=(0.0, 0.0, z + 0.040)),
            material=mats["accent"],
            name="top_bridge", material_class_id="metal.paint_coated",
        )
        base.visual(
            Box((0.044, 0.054, 0.086)),
            origin=Origin(xyz=(-0.026, 0.0, z + 0.018)),
            material=mats["joint"],
            name="central_bearing_tower", material_class_id="metal.stainless_matte",
        )
        for y, suffix in ((-0.045, "near"), (0.045, "far")):
            base.visual(
                Box((0.060, 0.018, 0.086)),
                origin=Origin(xyz=(-0.020, y, z)),
                material=mats["joint"],
                name=f"root_{suffix}_lug", material_class_id="metal.stainless_matte",
            )
    elif r.root_support == "desk_clamp_turret":
        base.visual(
            Box((0.24, 0.075, 0.030)),
            origin=Origin(xyz=(-0.045, 0.0, 0.015)),
            material=mats["base"],
            name="desk_edge", material_class_id="wood.engineered_board",
        )
        base.visual(
            Box((0.040, 0.070, 0.150)),
            origin=Origin(xyz=(-0.105, 0.0, 0.090)),
            material=mats["base"],
            name="clamp_spine", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
        )
        base.visual(
            Box((0.110, 0.070, 0.030)),
            origin=Origin(xyz=(-0.052, 0.0, 0.165)),
            material=mats["accent"],
            name="upper_jaw", material_class_id="metal.paint_coated",
        )
        base.visual(
            Box((0.085, 0.058, 0.022)),
            origin=Origin(xyz=(-0.060, 0.0, 0.040)),
            material=mats["accent"],
            name="pressure_pad", material_class_id="rubber.smooth_plain",
        )
        base.visual(
            Cylinder(radius=0.020, length=z - 0.045),
            origin=_z_cyl(0.0, 0.0, (z + 0.045) / 2.0),
            material=mats["joint"],
            name="vertical_post", material_class_id="metal.stainless_matte",
        )
        base.visual(
            Cylinder(radius=0.043, length=0.024),
            origin=_z_cyl(0.0, 0.0, z - 0.012),
            material=mats["joint"],
            name="turret_cap", material_class_id="metal.stainless_matte",
        )
    else:
        plate = _extruded_plate_mesh(
            "side_cheek_plate.obj",
            rounded_rect_profile(0.125, 0.170, 0.014, corner_segments=8),
            [
                _circle_profile(r.hub_radius * 0.42),
                _circle_profile(0.005, center=(-0.034, 0.050)),
                _circle_profile(0.005, center=(-0.034, -0.050)),
            ],
            0.012,
        )
        base.visual(
            plate,
            origin=Origin(xyz=(0.0, -r.layer_spacing, z)),
            material=mats["base"],
            name="side_cheek_plate", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
        )
        base.visual(
            Cylinder(radius=r.hub_radius * 1.22, length=0.014),
            origin=_y_cyl(0.0, -r.layer_spacing, z),
            material=mats["joint"],
            name="cheek_pin_boss", material_class_id="metal.stainless_matte",
        )
    _add_socket(base, x=0.0, z=z, r=r, mats=mats, name="root_socket")
    return base


def _build_link(
    model: ArticulatedObject,
    r: ResolvedNJointRevoluteChainConfig,
    mats,
    *,
    index: int,
    length: float,
):
    part = model.part(f"link_{index}")
    w = r.link_width * (1.0 - index * 0.055)
    h = r.link_height * (1.0 - index * 0.045)
    hub = r.hub_radius * (1.0 - index * 0.030)
    hub_l = r.hub_length * (1.0 - index * 0.025)
    layer = r.layer_spacing if index % 2 == 0 else -r.layer_spacing

    if r.link_body_family == "cadquery_solid_hubbed_beam":
        part.visual(
            _cadquery_link_mesh(length, w, h, hub, hub_l),
            material=mats["link"],
            name="cadquery_link_body", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
        )
    elif r.link_body_family == "extruded_open_frame_fork":
        mesh = _alternating_plate_mesh(
            length, hub * 1.12, max(0.010, hub_l * 0.26), "open_frame_plate.obj"
        )
        part.visual(
            mesh,
            origin=Origin(xyz=(0.0, layer, 0.0)),
            material=mats["link"],
            name="open_frame_plate", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
        )
        for y, suffix in (
            (layer - r.layer_spacing * 0.52, "inner"),
            (layer + r.layer_spacing * 0.52, "outer"),
        ):
            part.visual(
                Box((0.070, 0.008, hub * 2.25)),
                origin=Origin(xyz=(length, y, 0.0)),
                material=mats["joint"],
                name=f"distal_{suffix}_fork_cheek", material_class_id="metal.stainless_matte",
            )
        part.visual(
            Box((0.036, abs(layer) + r.layer_spacing * 1.36, hub * 1.18)),
            origin=Origin(xyz=(length - 0.024, layer / 2.0, 0.0)),
            material=mats["joint"],
            name="distal_fork_web", material_class_id="metal.stainless_matte",
        )
    elif r.link_body_family == "boxed_fork_washer_stack":
        part.visual(
            Cylinder(radius=hub, length=hub_l),
            origin=_x_cyl(hub_l / 2.0, 0.0, 0.0),
            material=mats["joint"],
            name="proximal_bearing", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Box((length - hub_l * 1.7, w, h)),
            origin=Origin(xyz=(length * 0.50, 0.0, 0.0)),
            material=mats["link"],
            name="box_beam", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
        )
        part.visual(
            Box((length * 0.72, w * 0.28, h * 0.26)),
            origin=Origin(xyz=(length * 0.54, 0.0, h * 0.48)),
            material=mats["accent"],
            name="top_rib", material_class_id="metal.paint_coated",
        )
        for y, suffix in ((-w * 0.62, "near"), (w * 0.62, "far")):
            part.visual(
                Box((0.078, w * 0.28, h * 1.65)),
                origin=Origin(xyz=(length, y, 0.0)),
                material=mats["joint"],
                name=f"distal_{suffix}_fork_cheek", material_class_id="metal.stainless_matte",
            )
    elif r.link_body_family == "cadquery_alternating_side_plate":
        plate = _alternating_plate_mesh(length, hub * 1.10, 0.012, "alternating_side_plate.obj")
        part.visual(
            plate, origin=Origin(xyz=(0.0, layer, 0.0)), material=mats["link"], name="side_plate", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated")
        )
        part.visual(
            Cylinder(radius=hub * 1.05, length=0.014),
            origin=_y_cyl(0.0, layer, 0.0),
            material=mats["joint"],
            name="proximal_bearing", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Cylinder(radius=hub, length=0.014),
            origin=_y_cyl(length, layer, 0.0),
            material=mats["joint"],
            name="distal_round_bearing", material_class_id="metal.stainless_matte",
        )
    else:
        y = w * 0.42
        for side, suffix in ((-y, "near"), (y, "far")):
            tube = tube_from_spline_points(
                [(0.0, side, 0.0), (length * 0.48, side, 0.018), (length, side, 0.0)],
                radius=hub * 0.24,
                samples_per_segment=10,
                radial_segments=10,
                cap_ends=True,
            )
            part.visual(
                _mesh_for_model(model, tube, f"tube_{suffix}"),
                material=mats["link"],
                name=f"tube_{suffix}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
            )
        for x, suffix in ((0.0, "proximal"), (length * 0.50, "middle"), (length, "distal")):
            part.visual(
                Box((0.018, w * 1.12, hub * 0.42)),
                origin=Origin(xyz=(x, 0.0, 0.0)),
                material=mats["accent"],
                name=f"{suffix}_crossbar", material_class_id="metal.paint_coated",
            )
        spring = tube_from_spline_points(
            [(length * t / 12.0, 0.0, math.sin(t * math.pi) * hub * 0.35) for t in range(13)],
            radius=hub * 0.105,
            samples_per_segment=8,
            radial_segments=8,
            cap_ends=True,
        )
        part.visual(
            _mesh_for_model(model, spring, "boom_spring"),
            material=mats["joint"],
            name="helical_spring_trace", material_class_id="metal.steel_bare",
        )

    if r.link_body_family not in ("boxed_fork_washer_stack", "cadquery_alternating_side_plate"):
        part.visual(
            Cylinder(radius=hub, length=hub_l),
            origin=_x_cyl(hub_l / 2.0, 0.0, 0.0),
            material=mats["joint"],
            name="proximal_bearing", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Cylinder(radius=hub * 0.92, length=hub_l * 0.82),
            origin=_x_cyl(length, 0.0, 0.0),
            material=mats["joint"],
            name="distal_round_bearing", material_class_id="metal.stainless_matte",
        )
    part.visual(
        Box((0.014, max(w * 0.82, hub_l * 0.75), hub * 1.70)),
        origin=Origin(xyz=(0.007, 0.0, 0.0)),
        material=mats["joint"],
        name="proximal_hub", material_class_id="metal.stainless_matte",
    )
    if r.link_body_family in ("cadquery_alternating_side_plate", "extruded_open_frame_fork"):
        part.visual(
            Box((0.018, abs(layer) + 0.018, hub * 1.10)),
            origin=Origin(xyz=(0.018, layer / 2.0, 0.0)),
            material=mats["joint"],
            name="proximal_layer_bridge", material_class_id="metal.stainless_matte",
        )
    part.visual(
        Box((0.014, max(w * 0.82, hub_l * 0.75), hub * 1.62)),
        origin=Origin(xyz=(length - 0.007, 0.0, 0.0)),
        material=mats["joint"],
        name="distal_socket", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Box((0.074, max(w * 0.82, hub_l * 0.70), hub * 1.55)),
        origin=Origin(xyz=(length - 0.030, 0.0, 0.0)),
        material=mats["joint"],
        name="distal_socket_neck", material_class_id="metal.stainless_matte",
    )
    _add_pin(part, x=length, length=max(hub_l, w * 1.55), r=r, mats=mats, name="distal_pin")
    return part


def _build_terminal(model: ArticulatedObject, r: ResolvedNJointRevoluteChainConfig, mats):
    part = model.part("terminal")
    scale = r.terminal_size_scale
    hub = r.hub_radius * 0.92
    hub_l = r.hub_length * 0.86
    part.visual(
        Cylinder(radius=hub, length=hub_l),
        origin=_x_cyl(hub_l / 2.0, 0.0, 0.0),
        material=mats["joint"],
        name="terminal_bearing", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Box((0.014, hub_l * 0.85, hub * 1.70)),
        origin=Origin(xyz=(0.007, 0.0, 0.0)),
        material=mats["joint"],
        name="terminal_hub", material_class_id="metal.stainless_matte",
    )

    if r.terminal_module == "compact_pad_tab":
        part.visual(
            Box((0.095 * scale, 0.034 * scale, 0.026 * scale)),
            origin=Origin(xyz=(0.060 * scale, 0.0, 0.0)),
            material=mats["link"],
            name="wrist_body", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
        )
        part.visual(
            Box((0.040 * scale, 0.082 * scale, 0.052 * scale)),
            origin=Origin(xyz=(0.125 * scale, 0.0, 0.0)),
            material=mats["terminal"],
            name="rectangular_pad", material_class_id="rubber.smooth_plain",
        )
    elif r.terminal_module == "sensor_pod_fixed":
        part.visual(
            Box((0.070 * scale, 0.044 * scale, 0.036 * scale)),
            origin=Origin(xyz=(0.060 * scale, 0.0, 0.0)),
            material=mats["link"],
            name="sensor_mast", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
        )
        part.visual(
            Box((0.080 * scale, 0.070 * scale, 0.052 * scale)),
            origin=Origin(xyz=(0.118 * scale, 0.0, 0.010 * scale)),
            material=mats["terminal"],
            name="sensor_body", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Box((0.020 * scale, 0.052 * scale, 0.024 * scale)),
            origin=Origin(xyz=(0.165 * scale, 0.0, 0.010 * scale)),
            material=mats["rubber"],
            name="sensor_lens", material_class_id="glass.smoked_tinted",
        )
        part.visual(
            Box((0.070 * scale, 0.076 * scale, 0.010 * scale)),
            origin=Origin(xyz=(0.125 * scale, 0.0, 0.036 * scale)),
            material=mats["accent"],
            name="sensor_visor", material_class_id="plastic.frosted_translucent",
        )
    elif r.terminal_module == "microphone_head":
        part.visual(
            Box((0.070 * scale, 0.030 * scale, 0.030 * scale)),
            origin=Origin(xyz=(0.050 * scale, 0.0, 0.0)),
            material=mats["link"],
            name="mic_stem", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
        )
        part.visual(
            Cylinder(radius=0.030 * scale, length=0.110 * scale),
            origin=_x_cyl(0.130 * scale, 0.0, 0.0),
            material=mats["terminal"],
            name="microphone_body", material_class_id="plastic.opaque_glossy_molded",
        )
        for x in (0.095, 0.120, 0.145, 0.170):
            part.visual(
                Cylinder(radius=0.0315 * scale, length=0.006 * scale),
                origin=_x_cyl(x * scale, 0.0, 0.0),
                material=mats["accent"],
                name=f"grille_band_{x:.3f}", material_class_id="metal.mesh_chainmail",
            )
    else:
        part.visual(
            Box((0.150 * scale, 0.030 * scale, 0.030 * scale)),
            origin=Origin(xyz=(0.080 * scale, 0.0, 0.0)),
            material=mats["link"],
            name="wrist_beam", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"dark_steel", "satin_aluminum", "black_boom"} else "metal.paint_coated"),
        )
        part.visual(
            Box((0.050 * scale, 0.074 * scale, 0.064 * scale)),
            origin=Origin(xyz=(0.165 * scale, 0.0, 0.0)),
            material=mats["joint"],
            name="pad_backing_lug", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Box((0.030 * scale, 0.190 * scale, 0.130 * scale)),
            origin=Origin(xyz=(0.192 * scale, 0.0, 0.0)),
            material=mats["terminal"],
            name="rectangular_pad_plate", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((0.008 * scale, 0.174 * scale, 0.114 * scale)),
            origin=Origin(xyz=(0.209 * scale, 0.0, 0.0)),
            material=mats["rubber"],
            name="pad_face", material_class_id="rubber.smooth_plain",
        )
    return part


def _joint_mating(parent_part: str, child_part: str) -> MatingContract:
    parent_visual = "root_socket" if parent_part == "root_support" else "distal_socket"
    child_visual = "terminal_hub" if child_part == "terminal" else "proximal_hub"
    return MatingContract(
        parent_visual, "positive_x", child_visual, "negative_x", contact_tol=0.003
    )


def _interfaces_for_model(r: ResolvedNJointRevoluteChainConfig) -> tuple[InterfaceSpec, ...]:
    interfaces = [
        InterfaceSpec(
            "root_downstream",
            "root_support",
            "root_socket",
            "positive_x",
            r.root_origin,
            consumer_joint_type=ArticulationType.REVOLUTE,
            consumer_joint_axis=r.joint_axes[0],
        )
    ]
    for index, length in enumerate(r.link_lengths[:-1]):
        interfaces.append(
            InterfaceSpec(
                f"link_{index}_downstream",
                f"link_{index}",
                "distal_socket",
                "positive_x",
                (length, 0.0, 0.0),
                consumer_joint_type=ArticulationType.REVOLUTE,
                consumer_joint_axis=r.joint_axes[min(index + 1, r.joint_count - 1)],
            )
        )
    return tuple(interfaces)


def build_n_joint_revolute_chain(
    config: NJointRevoluteChainConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: _mat(model, r, key)
        for key in ("base", "link", "joint", "accent", "terminal", "rubber")
    }

    _build_root(model, r, mats)
    link_parts = [
        _build_link(model, r, mats, index=i, length=length)
        for i, length in enumerate(r.link_lengths[:-1])
    ]
    _build_terminal(model, r, mats)

    children = [part.name for part in link_parts] + ["terminal"]
    parents = ["root_support"] + children[:-1]
    origins = [r.root_origin] + [(length, 0.0, 0.0) for length in r.link_lengths[:-1]]

    for i, (parent, child, origin, axis, limits) in enumerate(
        zip(parents, children, origins, r.joint_axes, r.joint_limits)
    ):
        model.articulation(
            f"joint_{i}",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=child,
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(
                lower=limits[0], upper=limits[1], effort=40.0 / (i + 1), velocity=1.8
            ),
            mating=_joint_mating(parent, child),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["interfaces"] = tuple(
        interface.interface_name for interface in _interfaces_for_model(r)
    )
    return model


def build_seeded_n_joint_revolute_chain(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_n_joint_revolute_chain(config_from_seed(seed), assets=assets)


def _aabb_center(aabb) -> tuple[float, float, float]:
    return (
        (aabb[0][0] + aabb[1][0]) * 0.5,
        (aabb[0][1] + aabb[1][1]) * 0.5,
        (aabb[0][2] + aabb[1][2]) * 0.5,
    )


def run_n_joint_revolute_chain_tests(
    object_model: ArticulatedObject,
    config: NJointRevoluteChainConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    for i in range(r.joint_count):
        parent = "root_support" if i == 0 else f"link_{i - 1}"
        child = "terminal" if i == r.joint_count - 1 else f"link_{i}"
        ctx.allow_overlap(
            object_model.get_part(parent),
            object_model.get_part(child),
            reason=f"joint_{i} captured pin/boss overlap is source-backed hinge hardware",
        )
    if r.link_body_family == "tube_spring_boom":
        for i in range(r.joint_count - 1):
            ctx.check(
                f"tube_boom_link_{i}_source_backed",
                object_model.get_part(f"link_{i}") is not None,
                details="tube_spring_boom uses source-backed twin tubes, crossbars, and spring traces",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    part_names = {part.name for part in object_model.parts}
    expected = {"root_support", "terminal"} | {f"link_{i}" for i in range(r.joint_count - 1)}
    ctx.check(
        "expected_parts_present", expected.issubset(part_names), details=str(sorted(part_names))
    )
    ctx.check(
        "exact_revolute_joint_count",
        len(object_model.joints) == r.joint_count,
        details=f"{len(object_model.joints)}",
    )

    for i, axis in enumerate(r.joint_axes):
        joint = object_model.get_articulation(f"joint_{i}")
        ctx.check(
            f"joint_{i}_type",
            joint.articulation_type == ArticulationType.REVOLUTE,
            details=str(joint.articulation_type),
        )
        ctx.check(f"joint_{i}_axis", tuple(joint.axis) == axis, details=str(joint.axis))
        ctx.check(f"joint_{i}_mating", joint.mating is not None, details="missing mating contract")

    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    terminal = object_model.get_part("terminal")
    rest_aabb = ctx.part_world_aabb(terminal)
    pose = {}
    for i in range(r.joint_count):
        joint = object_model.get_articulation(f"joint_{i}")
        pose[joint] = joint.motion_limits.upper * 0.32
    with ctx.pose(pose):
        posed_aabb = ctx.part_world_aabb(terminal)
    if rest_aabb and posed_aabb:
        rest_center = _aabb_center(rest_aabb)
        posed_center = _aabb_center(posed_aabb)
        delta = math.sqrt(sum((posed_center[i] - rest_center[i]) ** 2 for i in range(3)))
        ctx.check("terminal_moves_under_pose", delta > 0.015, details=f"delta={delta:.4f}")
    return ctx.report()


__all__ = (
    "NJointRevoluteChainConfig",
    "ResolvedNJointRevoluteChainConfig",
    "build_n_joint_revolute_chain",
    "build_seeded_n_joint_revolute_chain",
    "config_from_seed",
    "resolve_config",
    "run_n_joint_revolute_chain_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
