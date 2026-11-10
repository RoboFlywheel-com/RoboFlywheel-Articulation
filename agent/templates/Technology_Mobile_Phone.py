# SPDX-License-Identifier: Apache-2.0

"""Source-backed modular mobile-phone template.

The template composes one topology-defining host, one front module, and one
antenna treatment. Variant sources contribute only their changed component:
unchanged candybar or clamshell geometry is de-duplicated to its parent.

Coordinates: X = handset width, Y = handset length/top, Z = front/outward.
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
    Inertial,
    MotionLimits,
    Origin,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_geometry,
    register_interface_mate,
    rounded_rect_profile,
)

__preview_front_axis__ = "+z"

HostMechanism = Literal[
    "curved_monoblock",
    "vertical_slider",
    "corner_swivel",
    "senior_clamshell",
]
FrontModule = Literal[
    "classic_function_numeric",
    "numeric_only_12",
    "qwerty_40",
    "full_touch",
    "senior_large_keypad",
]
AntennaModule = Literal["integrated_internal", "telescoping_mast"]

_HOSTS = ("curved_monoblock", "vertical_slider", "corner_swivel", "senior_clamshell")
_FRONTS = (
    "classic_function_numeric",
    "numeric_only_12",
    "qwerty_40",
    "full_touch",
    "senior_large_keypad",
)
_ANTENNAS = ("integrated_internal", "telescoping_mast")

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("host_mechanism", _HOSTS),
        component_slot("front_module", _FRONTS),
        component_slot("antenna_module", _ANTENNAS),
    )
)

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {
        "shell": (0.035, 0.050, 0.130, 1.0),
        "shell_2": (0.18, 0.21, 0.27, 1.0),
        "deck": (0.055, 0.065, 0.105, 1.0),
        "key": (0.70, 0.71, 0.69, 1.0),
        "screen": (0.45, 0.67, 0.42, 1.0),
        "bezel": (0.012, 0.015, 0.022, 1.0),
        "metal": (0.56, 0.59, 0.62, 1.0),
        "accent": (0.00, 0.56, 0.72, 1.0),
    },
    {
        "shell": (0.030, 0.032, 0.036, 1.0),
        "shell_2": (0.40, 0.43, 0.47, 1.0),
        "deck": (0.075, 0.078, 0.085, 1.0),
        "key": (0.16, 0.17, 0.19, 1.0),
        "screen": (0.38, 0.72, 0.86, 1.0),
        "bezel": (0.010, 0.011, 0.014, 1.0),
        "metal": (0.64, 0.65, 0.67, 1.0),
        "accent": (0.92, 0.20, 0.08, 1.0),
    },
    {
        "shell": (0.74, 0.76, 0.78, 1.0),
        "shell_2": (0.88, 0.89, 0.90, 1.0),
        "deck": (0.26, 0.28, 0.31, 1.0),
        "key": (0.10, 0.11, 0.13, 1.0),
        "screen": (0.08, 0.19, 0.34, 1.0),
        "bezel": (0.025, 0.027, 0.032, 1.0),
        "metal": (0.48, 0.50, 0.53, 1.0),
        "accent": (0.18, 0.55, 0.88, 1.0),
    },
)

_KEY_TRAVEL = 0.0010
_FRONT_RECESS = 0.00065
_KEY_HEIGHT = 0.0026
_MIN_PRESSED_KEY_PROTRUSION = 0.00085
_SLIDER_TRAVEL = 0.030
_SWIVEL_RANGE = math.pi
_CLAMSHELL_CLOSE = math.radians(92.0)
_ANTENNA_TRAVEL = 0.018

_FRONT_WIDTH = {
    "classic_function_numeric": 0.044,
    "numeric_only_12": 0.042,
    "qwerty_40": 0.058,
    "full_touch": 0.048,
    "senior_large_keypad": 0.054,
}
_FRONT_HEIGHT = {
    "classic_function_numeric": 0.058,
    "numeric_only_12": 0.050,
    "qwerty_40": 0.031,
    "full_touch": 0.016,
    "senior_large_keypad": 0.076,
}
_KEY_COUNTS = {
    "classic_function_numeric": 15,
    "numeric_only_12": 12,
    "qwerty_40": 40,
    "full_touch": 4,
    "senior_large_keypad": 21,
}


@dataclass(frozen=True)
class Config:
    host_mechanism: HostMechanism = "curved_monoblock"
    front_module: FrontModule = "classic_function_numeric"
    antenna_module: AntennaModule = "integrated_internal"
    palette: int = 0
    body_scale: float = 1.0
    thickness_scale: float = 1.0
    name: str = "Technology_Mobile_Phone"


@dataclass(frozen=True)
class ResolvedConfig:
    host_mechanism: HostMechanism
    front_module: FrontModule
    antenna_module: AntennaModule
    palette: int
    name: str
    body_width_m: float
    body_height_m: float
    body_thickness_m: float
    front_width_m: float
    front_height_m: float
    front_center_y_m: float
    screen_width_m: float
    screen_height_m: float
    key_count: int
    slider_travel_m: float
    swivel_range_rad: float
    clamshell_close_rad: float
    antenna_travel_m: float


@dataclass(frozen=True)
class _Host:
    body: object
    display: object
    front_point: tuple[float, float, float]
    front_extent: tuple[float, float]
    antenna_point: tuple[float, float, float]
    display_vertical: bool
    display_face: float
    display_center: tuple[float, float]


def _clamp_scale(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    index = int(seed)
    antenna = _ANTENNAS[index % len(_ANTENNAS)]
    index //= len(_ANTENNAS)
    front = _FRONTS[index % len(_FRONTS)]
    index //= len(_FRONTS)
    host = _HOSTS[index % len(_HOSTS)]
    return Config(
        host_mechanism=host,
        front_module=front,
        antenna_module=antenna,
        palette=rng.randrange(len(_PALETTES)),
        body_scale=round(rng.uniform(0.90, 1.12), 4),
        thickness_scale=round(rng.uniform(0.85, 1.20), 4),
        name=f"Technology_Mobile_Phone_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    if config.host_mechanism not in _HOSTS:
        raise ValueError(f"unsupported host_mechanism: {config.host_mechanism}")
    if config.front_module not in _FRONTS:
        raise ValueError(f"unsupported front_module: {config.front_module}")
    if config.antenna_module not in _ANTENNAS:
        raise ValueError(f"unsupported antenna_module: {config.antenna_module}")
    body_scale = _clamp_scale(config.body_scale, 0.90, 1.12)
    thickness_scale = _clamp_scale(config.thickness_scale, 0.85, 1.20)
    host_width = {
        "curved_monoblock": 0.050,
        "vertical_slider": 0.052,
        "corner_swivel": 0.052,
        "senior_clamshell": 0.058,
    }[config.host_mechanism]
    front_width = _FRONT_WIDTH[config.front_module] * body_scale
    front_height = _FRONT_HEIGHT[config.front_module] * body_scale
    body_width = max(host_width * body_scale, front_width + 0.006)
    body_height = max(0.116, front_height + 0.044) * body_scale
    body_thickness = {
        "curved_monoblock": 0.021,
        "vertical_slider": 0.018,
        "corner_swivel": 0.020,
        "senior_clamshell": 0.018,
    }[config.host_mechanism] * thickness_scale
    touch = config.front_module == "full_touch"
    senior = config.front_module == "senior_large_keypad"
    screen_width = body_width - (0.008 if touch else 0.014)
    screen_height = body_height * (0.58 if touch else (0.46 if senior else 0.27))
    return ResolvedConfig(
        host_mechanism=config.host_mechanism,
        front_module=config.front_module,
        antenna_module=config.antenna_module,
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        body_width_m=body_width,
        body_height_m=body_height,
        body_thickness_m=body_thickness,
        front_width_m=front_width,
        front_height_m=front_height,
        front_center_y_m=-body_height * 0.22,
        screen_width_m=screen_width,
        screen_height_m=screen_height,
        key_count=_KEY_COUNTS[config.front_module],
        slider_travel_m=_SLIDER_TRAVEL * body_scale,
        swivel_range_rad=_SWIVEL_RANGE,
        clamshell_close_rad=_CLAMSHELL_CLOSE,
        antenna_travel_m=_ANTENNA_TRAVEL * body_scale,
    )


def _materials(model: ArticulatedObject, palette: int):
    colors = _PALETTES[palette]
    return {
        name: model.material(f"phone_{name}_{palette}", rgba=rgba) for name, rgba in colors.items()
    }


def _rounded_mesh(width: float, height: float, thickness: float, radius: float, name: str):
    profile = rounded_rect_profile(
        width,
        height,
        min(radius, width * 0.45, height * 0.45),
        corner_segments=10,
    )
    geom = ExtrudeGeometry.from_z0(profile, thickness, cap=True)
    geom.translate(0.0, 0.0, -thickness / 2.0)
    return mesh_from_geometry(geom, name)


def _body_part(model: ArticulatedObject, r: ResolvedConfig):
    return model.part(
        "handset_body",
        meta={"role": "handset_body", "slot": "host_mechanism", "candidate": r.host_mechanism},
    )


def _display_part(model: ArticulatedObject, r: ResolvedConfig):
    return model.part(
        "display_panel",
        meta={"role": "display_panel", "slot": "host_mechanism", "candidate": r.host_mechanism},
    )


def _host_mechanism_curved_monoblock_build(
    model: ArticulatedObject, r: ResolvedConfig, mats
) -> _Host:
    tag = "host_mechanism__curved_monoblock"
    body = _body_part(model, r)
    body.visual(
        _rounded_mesh(
            r.body_width_m,
            r.body_height_m,
            r.body_thickness_m,
            0.014,
            f"{tag}__shell_mesh",
        ),
        material=mats["shell"],
        name=f"{tag}__shell", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        _rounded_mesh(
            r.body_width_m - 0.003,
            r.body_height_m - 0.003,
            0.0012,
            0.012,
            f"{tag}__front_rim_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.body_thickness_m / 2.0 + 0.0006)),
        material=mats["shell_2"],
        name=f"{tag}__front_rim", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((r.body_width_m * 0.26, 0.0012, 0.0010)),
        origin=Origin(xyz=(0.0, r.body_height_m * 0.43, r.body_thickness_m / 2.0 + 0.0016)),
        material=mats["bezel"],
        name=f"{tag}__earpiece_slot", material_class_id="plastic.opaque_glossy_molded",
    )
    body.inertial = Inertial.from_geometry(
        Box((r.body_width_m, r.body_height_m, r.body_thickness_m)), mass=0.135
    )
    display = _display_part(model, r)
    display.visual(
        _rounded_mesh(
            r.screen_width_m + 0.005,
            r.screen_height_m + 0.006,
            0.0014,
            0.004,
            f"{tag}__display_frame_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0007)),
        material=mats["bezel"],
        name=f"{tag}__display_frame", material_class_id="plastic.opaque_glossy_molded",
    )
    display.inertial = Inertial.from_geometry(
        Box((r.screen_width_m, r.screen_height_m, 0.0014)), mass=0.012
    )
    display_y = r.body_height_m * 0.25
    model.articulation(
        f"{tag}__display_fixed",
        ArticulationType.FIXED,
        parent=body,
        child=display,
        origin=Origin(xyz=(0.0, display_y, r.body_thickness_m / 2.0 + 0.0006)),
    )
    return _Host(
        body=body,
        display=display,
        front_point=(0.0, r.front_center_y_m, r.body_thickness_m / 2.0 + 0.0012),
        front_extent=(r.body_width_m - 0.006, r.front_height_m + 0.006),
        antenna_point=(
            r.body_width_m / 2.0 - 0.004,
            r.body_height_m / 2.0 - 0.002,
            0.0,
        ),
        display_vertical=False,
        display_face=0.0014,
        display_center=(0.0, 0.0),
    )


def _host_mechanism_vertical_slider_build(
    model: ArticulatedObject, r: ResolvedConfig, mats
) -> _Host:
    tag = "host_mechanism__vertical_slider"
    body = _body_part(model, r)
    body.visual(
        _rounded_mesh(
            r.body_width_m,
            r.body_height_m * 0.78,
            r.body_thickness_m,
            0.012,
            f"{tag}__lower_shell_mesh",
        ),
        origin=Origin(xyz=(0.0, -r.body_height_m * 0.11, 0.0)),
        material=mats["shell"],
        name=f"{tag}__lower_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((r.body_width_m - 0.010, r.body_height_m * 0.52, 0.0012)),
        origin=Origin(xyz=(0.0, -r.body_height_m * 0.17, r.body_thickness_m / 2.0 - 0.0005)),
        material=mats["deck"],
        name=f"{tag}__recessed_slide_bay", material_class_id="plastic.opaque_glossy_molded",
    )
    body.inertial = Inertial.from_geometry(
        Box((r.body_width_m, r.body_height_m * 0.78, r.body_thickness_m)), mass=0.095
    )
    display = _display_part(model, r)
    carrier_h = r.body_height_m * 0.62
    display.visual(
        _rounded_mesh(
            r.body_width_m,
            carrier_h,
            0.006,
            0.011,
            f"{tag}__screen_carrier_mesh",
        ),
        origin=Origin(xyz=(0.0, r.body_height_m * 0.16, 0.003)),
        material=mats["shell_2"],
        name=f"{tag}__screen_carrier", material_class_id="plastic.opaque_glossy_molded",
    )
    display.inertial = Inertial.from_geometry(Box((r.body_width_m, carrier_h, 0.006)), mass=0.055)
    provider = AxisInterface(
        name="host_mechanism.slider_axis",
        point=(0.0, 0.0, r.body_thickness_m / 2.0 + 0.0005),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name="host_mechanism.screen_carriage_axis",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
    )
    mate = mate_axes(provider, consumer)
    joint = f"{tag}__screen_slide"
    model.articulation(
        joint,
        ArticulationType.PRISMATIC,
        parent=body,
        child=display,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=3.0, velocity=0.15, lower=0.0, upper=r.slider_travel_m),
    )
    register_interface_mate(model, joint, mate)
    return _Host(
        body=body,
        display=display,
        front_point=(0.0, r.front_center_y_m, r.body_thickness_m / 2.0 + 0.0001),
        front_extent=(r.body_width_m - 0.006, r.front_height_m + 0.006),
        antenna_point=(
            r.body_width_m / 2.0 - 0.004,
            r.body_height_m * 0.28,
            0.0,
        ),
        display_vertical=False,
        display_face=0.006,
        display_center=(0.0, r.body_height_m * 0.18),
    )


def _host_mechanism_corner_swivel_build(model: ArticulatedObject, r: ResolvedConfig, mats) -> _Host:
    tag = "host_mechanism__corner_swivel"
    body = _body_part(model, r)
    body.visual(
        _rounded_mesh(
            r.body_width_m,
            r.body_height_m * 0.72,
            r.body_thickness_m,
            0.012,
            f"{tag}__lower_shell_mesh",
        ),
        origin=Origin(xyz=(0.0, -r.body_height_m * 0.14, 0.0)),
        material=mats["shell"],
        name=f"{tag}__lower_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    pivot_x = -r.body_width_m / 2.0 + 0.007
    pivot_y = r.body_height_m * 0.08
    body.visual(
        Cylinder(radius=0.0042, length=r.body_thickness_m + 0.004),
        origin=Origin(xyz=(pivot_x, pivot_y, 0.0)),
        material=mats["metal"],
        name=f"{tag}__pivot_post", material_class_id="metal.stainless_matte",
    )
    body.inertial = Inertial.from_geometry(
        Box((r.body_width_m, r.body_height_m * 0.72, r.body_thickness_m)), mass=0.095
    )
    display = _display_part(model, r)
    carrier_h = r.body_height_m * 0.48
    local_center = (-pivot_x, r.body_height_m * 0.23 - pivot_y)
    display.visual(
        _rounded_mesh(
            r.body_width_m,
            carrier_h,
            0.006,
            0.010,
            f"{tag}__screen_carrier_mesh",
        ),
        origin=Origin(xyz=(local_center[0], local_center[1], 0.003)),
        material=mats["shell_2"],
        name=f"{tag}__screen_carrier", material_class_id="plastic.opaque_glossy_molded",
    )
    display.visual(
        Cylinder(radius=0.0052, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        material=mats["metal"],
        name=f"{tag}__pivot_hub", material_class_id="metal.stainless_matte",
    )
    display.inertial = Inertial.from_geometry(
        Box((r.body_width_m, carrier_h, 0.006)),
        mass=0.050,
        origin=Origin(xyz=(local_center[0], local_center[1], 0.003)),
    )
    provider = AxisInterface(
        name="host_mechanism.swivel_axis",
        point=(pivot_x, pivot_y, r.body_thickness_m / 2.0 + 0.0005),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0042,
    )
    consumer = AxisInterface(
        name="host_mechanism.screen_hub_axis",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0038,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    joint = f"{tag}__screen_swivel"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=body,
        child=display,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=3.0, velocity=1.8, lower=0.0, upper=r.swivel_range_rad),
    )
    register_interface_mate(model, joint, mate)
    return _Host(
        body=body,
        display=display,
        front_point=(0.0, r.front_center_y_m, r.body_thickness_m / 2.0),
        front_extent=(r.body_width_m - 0.006, r.front_height_m + 0.006),
        antenna_point=(
            r.body_width_m / 2.0 - 0.004,
            r.body_height_m * 0.22,
            0.0,
        ),
        display_vertical=False,
        display_face=0.006,
        display_center=local_center,
    )


def _host_mechanism_senior_clamshell_build(
    model: ArticulatedObject, r: ResolvedConfig, mats
) -> _Host:
    tag = "host_mechanism__senior_clamshell"
    body = _body_part(model, r)
    body.visual(
        _rounded_mesh(
            r.body_width_m,
            r.body_height_m,
            r.body_thickness_m,
            0.010,
            f"{tag}__lower_shell_mesh",
        ),
        material=mats["shell"],
        name=f"{tag}__lower_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    hinge_y = r.body_height_m / 2.0 - 0.004
    hinge_z = r.body_thickness_m / 2.0 + 0.0048
    for index, x in enumerate((-r.body_width_m * 0.34, r.body_width_m * 0.34)):
        body.visual(
            Cylinder(radius=0.0048, length=r.body_width_m * 0.25),
            origin=Origin(xyz=(x, hinge_y, hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["shell_2"],
            name=f"{tag}__body_knuckle_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    body.inertial = Inertial.from_geometry(
        Box((r.body_width_m, r.body_height_m, r.body_thickness_m)), mass=0.095
    )
    display = _display_part(model, r)
    lid_h = r.body_height_m * 0.92
    display.visual(
        _rounded_mesh(
            r.body_width_m,
            lid_h,
            0.008,
            0.010,
            f"{tag}__lid_shell_mesh",
        ),
        origin=Origin(
            xyz=(0.0, 0.004, lid_h / 2.0),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["shell"],
        name=f"{tag}__lid_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    display.visual(
        Cylinder(radius=0.0045, length=r.body_width_m * 0.46),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["shell_2"],
        name=f"{tag}__lid_knuckle", material_class_id="plastic.opaque_glossy_molded",
    )
    display.inertial = Inertial.from_geometry(
        Box((r.body_width_m, 0.008, lid_h)),
        mass=0.060,
        origin=Origin(xyz=(0.0, 0.004, lid_h / 2.0)),
    )
    provider = AxisInterface(
        name="host_mechanism.clamshell_axis",
        point=(0.0, hinge_y, hinge_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0048,
    )
    consumer = AxisInterface(
        name="host_mechanism.lid_axis",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0045,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    joint = f"{tag}__lid_hinge"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=body,
        child=display,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=4.0, velocity=1.5, lower=0.0, upper=r.clamshell_close_rad
        ),
    )
    register_interface_mate(model, joint, mate)
    return _Host(
        body=body,
        display=display,
        front_point=(0.0, r.front_center_y_m, r.body_thickness_m / 2.0),
        front_extent=(r.body_width_m - 0.006, r.front_height_m + 0.006),
        antenna_point=(
            r.body_width_m / 2.0 - 0.004,
            r.body_height_m / 2.0 - 0.010,
            0.0,
        ),
        display_vertical=True,
        display_face=-0.0005,
        display_center=(0.0, lid_h * 0.52),
    )


_HOST_BUILDERS = {
    "curved_monoblock": _host_mechanism_curved_monoblock_build,
    "vertical_slider": _host_mechanism_vertical_slider_build,
    "corner_swivel": _host_mechanism_corner_swivel_build,
    "senior_clamshell": _host_mechanism_senior_clamshell_build,
}


def _decorate_display(host: _Host, r: ResolvedConfig, mats, tag: str) -> None:
    if host.display_vertical:
        host.display.visual(
            Box((r.screen_width_m + 0.004, 0.0010, r.screen_height_m + 0.006)),
            origin=Origin(xyz=(host.display_center[0], host.display_face, host.display_center[1])),
            material=mats["bezel"],
            name=f"{tag}__screen_bezel", material_class_id="plastic.opaque_glossy_molded",
        )
        host.display.visual(
            Box((r.screen_width_m, 0.0008, r.screen_height_m)),
            origin=Origin(
                xyz=(host.display_center[0], host.display_face - 0.0008, host.display_center[1])
            ),
            material=mats["screen"],
            name=f"{tag}__screen_glass", material_class_id="tech.emissive_surface",
        )
        host.display.visual(
            Box((r.screen_width_m * 0.34, 0.0008, 0.0012)),
            origin=Origin(
                xyz=(
                    host.display_center[0],
                    host.display_face - 0.0004,
                    host.display_center[1] + r.screen_height_m * 0.46,
                )
            ),
            material=mats["bezel"],
            name=f"{tag}__earpiece", material_class_id="metal.mesh_chainmail",
        )
    else:
        x, y = host.display_center
        host.display.visual(
            Box((r.screen_width_m + 0.004, r.screen_height_m + 0.005, 0.0010)),
            origin=Origin(xyz=(x, y, host.display_face + 0.0005)),
            material=mats["bezel"],
            name=f"{tag}__screen_bezel", material_class_id="plastic.opaque_glossy_molded",
        )
        host.display.visual(
            Box((r.screen_width_m, r.screen_height_m, 0.0007)),
            origin=Origin(xyz=(x, y, host.display_face + 0.00125)),
            material=mats["screen"],
            name=f"{tag}__screen_glass", material_class_id="tech.emissive_surface",
        )
        host.display.visual(
            Box((r.screen_width_m * 0.34, 0.0011, 0.0007)),
            origin=Origin(xyz=(x, y + r.screen_height_m * 0.46, host.display_face + 0.00075)),
            material=mats["bezel"],
            name=f"{tag}__earpiece", material_class_id="metal.mesh_chainmail",
        )


def _mount_front_deck(model: ArticulatedObject, host: _Host, r: ResolvedConfig, mats, tag: str):
    deck = model.part(
        "front_deck",
        meta={"role": "input_surface", "slot": "front_module", "candidate": r.front_module},
    )
    provider = PlaneInterface(
        name="host_mechanism.front_bay",
        point=host.front_point,
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=host.front_extent,
    )
    consumer = PlaneInterface(
        name="front_module.host_mount",
        point=(0.0, 0.0, _FRONT_RECESS),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.front_width_m, r.front_height_m),
    )
    mate = mate_planes(provider, consumer)
    model.articulation(
        f"{tag}__deck_mount",
        ArticulationType.FIXED,
        parent=host.body,
        child=deck,
        origin=mate.origin,
    )
    deck.visual(
        _rounded_mesh(
            r.front_width_m,
            r.front_height_m,
            0.00025,
            min(0.005, r.front_height_m * 0.18),
            f"{tag}__deck_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, _FRONT_RECESS + 0.000125)),
        material=mats["deck"],
        name=f"{tag}__deck", material_class_id="plastic.opaque_glossy_molded",
    )
    deck.inertial = Inertial.from_geometry(
        Box((r.front_width_m, r.front_height_m, 0.00025)), mass=0.012
    )
    return deck


def _key_box(width: float, height: float):
    return Box((width, height, _KEY_HEIGHT))


def _add_grid_keys(
    model: ArticulatedObject,
    deck,
    r: ResolvedConfig,
    mats,
    tag: str,
    *,
    rows: int,
    cols: int,
    count: int,
    accent_indices: tuple[int, ...] = (),
) -> None:
    pitch_x = r.front_width_m / (cols + 0.45)
    pitch_y = r.front_height_m / (rows + 0.45)
    key_w = pitch_x * 0.74
    key_h = pitch_y * 0.66
    x0 = -(cols - 1) * pitch_x / 2.0
    y0 = (rows - 1) * pitch_y / 2.0
    geometry = _key_box(key_w, key_h)
    for index in range(count):
        row, col = divmod(index, cols)
        key = model.part(
            f"{tag}__press_key_{index}",
            meta={
                "role": "key_press",
                "slot": "front_module",
                "candidate": r.front_module,
                "opening_extent": (pitch_x * 0.84, pitch_y * 0.76),
            },
        )
        key.visual(
            geometry,
            origin=Origin(xyz=(0.0, 0.0, _KEY_HEIGHT / 2.0)),
            material=mats["accent"] if index in accent_indices else mats["key"],
            name=f"{tag}__cap_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        key.visual(
            Box((key_w * 0.34, key_h * 0.12, 0.00025)),
            origin=Origin(xyz=(0.0, 0.0, _KEY_HEIGHT + 0.00012)),
            material=mats["bezel"],
            name=f"{tag}__legend_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        key.inertial = Inertial.from_geometry(geometry, mass=0.0008)
        model.articulation(
            f"{tag}__press_joint_{index}",
            ArticulationType.PRISMATIC,
            parent=deck,
            child=key,
            origin=Origin(xyz=(x0 + col * pitch_x, y0 - row * pitch_y, 0.0)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=1.0, velocity=0.06, lower=0.0, upper=_KEY_TRAVEL),
            meta={"motion_qc_repeat_group": f"{tag}__key_press"},
        )


def _front_module_classic_function_numeric_build(
    model: ArticulatedObject, host: _Host, r: ResolvedConfig, mats
) -> None:
    tag = "front_module__classic_function_numeric"
    _decorate_display(host, r, mats, tag)
    deck = _mount_front_deck(model, host, r, mats, tag)
    _add_grid_keys(model, deck, r, mats, tag, rows=5, cols=3, count=15, accent_indices=(1,))
    deck.visual(
        Box((r.front_width_m * 0.52, 0.0012, 0.0005)),
        origin=Origin(xyz=(0.0, r.front_height_m * 0.39, 0.00105)),
        material=mats["accent"],
        name=f"{tag}__smile_navigation_bar", material_class_id="plastic.opaque_glossy_molded",
    )


def _front_module_numeric_only_12_build(
    model: ArticulatedObject, host: _Host, r: ResolvedConfig, mats
) -> None:
    tag = "front_module__numeric_only_12"
    _decorate_display(host, r, mats, tag)
    deck = _mount_front_deck(model, host, r, mats, tag)
    _add_grid_keys(model, deck, r, mats, tag, rows=4, cols=3, count=12)


def _front_module_qwerty_40_build(
    model: ArticulatedObject, host: _Host, r: ResolvedConfig, mats
) -> None:
    tag = "front_module__qwerty_40"
    _decorate_display(host, r, mats, tag)
    deck = _mount_front_deck(model, host, r, mats, tag)
    _add_grid_keys(model, deck, r, mats, tag, rows=4, cols=10, count=40)


def _front_module_full_touch_build(
    model: ArticulatedObject, host: _Host, r: ResolvedConfig, mats
) -> None:
    tag = "front_module__full_touch"
    _decorate_display(host, r, mats, tag)
    deck = _mount_front_deck(model, host, r, mats, tag)
    specs = (
        (0.0, 0.0, (0.0, 0.0, -1.0)),
        (r.front_width_m * 0.34, 0.003, (-1.0, 0.0, 0.0)),
        (-r.front_width_m * 0.34, 0.004, (1.0, 0.0, 0.0)),
        (-r.front_width_m * 0.34, -0.004, (1.0, 0.0, 0.0)),
    )
    for index, (x, y, axis) in enumerate(specs):
        key = model.part(
            f"{tag}__press_key_{index}",
            meta={"role": "key_press", "slot": "front_module", "candidate": r.front_module},
        )
        key.visual(
            Cylinder(radius=0.0030 if index == 0 else 0.0020, length=0.0015),
            origin=Origin(xyz=(0.0, 0.0, 0.00075)),
            material=mats["metal"],
            name=f"{tag}__control_{index}", material_class_id="metal.stainless_matte",
        )
        key.inertial = Inertial.from_geometry(Box((0.006, 0.006, 0.0015)), mass=0.0006)
        model.articulation(
            f"{tag}__press_joint_{index}",
            ArticulationType.PRISMATIC,
            parent=deck,
            child=key,
            origin=Origin(xyz=(x, y, 0.0)),
            axis=axis,
            motion_limits=MotionLimits(effort=1.0, velocity=0.05, lower=0.0, upper=0.0008),
        )


def _front_module_senior_large_keypad_build(
    model: ArticulatedObject, host: _Host, r: ResolvedConfig, mats
) -> None:
    tag = "front_module__senior_large_keypad"
    _decorate_display(host, r, mats, tag)
    deck = _mount_front_deck(model, host, r, mats, tag)
    _add_grid_keys(
        model,
        deck,
        r,
        mats,
        tag,
        rows=7,
        cols=3,
        count=21,
        accent_indices=(4, 6),
    )


_FRONT_BUILDERS = {
    "classic_function_numeric": _front_module_classic_function_numeric_build,
    "numeric_only_12": _front_module_numeric_only_12_build,
    "qwerty_40": _front_module_qwerty_40_build,
    "full_touch": _front_module_full_touch_build,
    "senior_large_keypad": _front_module_senior_large_keypad_build,
}


def _antenna_module_integrated_internal_build(
    model: ArticulatedObject, host: _Host, r: ResolvedConfig, mats
) -> None:
    tag = "antenna_module__integrated_internal"
    mount = host.antenna_point
    host.body.visual(
        Box((0.008, 0.0040, 0.0012)),
        origin=Origin(
            xyz=(
                mount[0],
                mount[1] - 0.002,
                r.body_thickness_m / 2.0,
            )
        ),
        material=mats["shell_2"],
        name=f"{tag}__molded_radio_window", material_class_id="plastic.opaque_glossy_molded",
    )


def _antenna_module_telescoping_mast_build(
    model: ArticulatedObject, host: _Host, r: ResolvedConfig, mats
) -> None:
    tag = "antenna_module__telescoping_mast"
    mount = host.antenna_point
    sleeve_length = 0.020
    host.body.visual(
        Cylinder(radius=0.0036, length=0.005),
        origin=Origin(xyz=mount, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name=f"{tag}__boss", material_class_id="metal.stainless_matte",
    )
    host.body.visual(
        Cylinder(radius=0.0031, length=sleeve_length),
        origin=Origin(
            xyz=(mount[0], mount[1] + sleeve_length / 2.0, mount[2]),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["metal"],
        name=f"{tag}__guide_sleeve", material_class_id="metal.stainless_matte",
    )
    mast = model.part(
        f"{tag}__mast",
        meta={"role": "antenna_mast", "slot": "antenna_module", "candidate": r.antenna_module},
    )
    mast_length = 0.028
    mast.visual(
        Cylinder(radius=0.0017, length=mast_length),
        origin=Origin(xyz=(0.0, mast_length / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name=f"{tag}__mast_rod", material_class_id="metal.stainless_matte",
    )
    mast.visual(
        Cylinder(radius=0.0025, length=0.004),
        origin=Origin(xyz=(0.0, mast_length + 0.002, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["shell_2"],
        name=f"{tag}__tip_bulb", material_class_id="plastic.opaque_glossy_molded",
    )
    mast.inertial = Inertial.from_geometry(Box((0.0034, mast_length + 0.004, 0.0034)), mass=0.003)
    provider = AxisInterface(
        name="host_mechanism.antenna_socket",
        point=mount,
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0031,
    )
    consumer = AxisInterface(
        name="antenna_module.host_socket",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0017,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    joint = f"{tag}__extend_joint"
    model.articulation(
        joint,
        ArticulationType.PRISMATIC,
        parent=host.body,
        child=mast,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=1.0, velocity=0.10, lower=0.0, upper=r.antenna_travel_m),
    )
    register_interface_mate(model, joint, mate)


_ANTENNA_BUILDERS = {
    "integrated_internal": _antenna_module_integrated_internal_build,
    "telescoping_mast": _antenna_module_telescoping_mast_build,
}


def build_mobile_phone(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette)
    host = _HOST_BUILDERS[r.host_mechanism](model, r, mats)
    _FRONT_BUILDERS[r.front_module](model, host, r, mats)
    _ANTENNA_BUILDERS[r.antenna_module](model, host, r, mats)
    model.meta["slot_choices"] = (
        ("host_mechanism", r.host_mechanism),
        ("front_module", r.front_module),
        ("antenna_module", r.antenna_module),
    )
    model.meta["key_count_actual"] = r.key_count
    return model


def build_seeded_mobile_phone(seed: int) -> ArticulatedObject:
    return build_mobile_phone(config_from_seed(seed))


def run_mobile_phone_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    roles: dict[str, list[object]] = {}
    for part in object_model.parts:
        role = str(getattr(part, "meta", {}).get("role") or "")
        if role:
            roles.setdefault(role, []).append(part)
    ctx.check(
        "category_anchor: handheld body carries one display and one input surface",
        len(roles.get("handset_body", [])) == 1
        and len(roles.get("display_panel", [])) == 1
        and len(roles.get("input_surface", [])) == 1,
        details={name: len(parts) for name, parts in roles.items()},
    )
    key_parts = roles.get("key_press", [])
    key_joints = [
        joint
        for joint in object_model.articulations
        if joint.name.startswith(f"front_module__{r.front_module}__press_joint_")
    ]
    if r.front_module != "full_touch":
        moved = True
        surface_relation_ok = True
        for joint in key_joints:
            part = object_model.get_part(joint.child)
            rest = ctx.part_world_position(part)
            cap_name = joint.name.replace("__press_joint_", "__cap_")
            opening_extent = tuple(float(value) for value in part.meta["opening_extent"])
            opening_frame = PlaneInterface(
                name=f"{joint.name}.front_opening",
                point=(
                    0.0 if rest is None else rest[0],
                    0.0 if rest is None else rest[1],
                    0.0 if rest is None else rest[2] + _FRONT_RECESS,
                ),
                normal=(0.0, 0.0, 1.0),
                tangent_u=(1.0, 0.0, 0.0),
                extent=opening_extent,
            )
            normal_ok = (
                rest is not None
                and ctx.expect_normal_band(
                    part,
                    frame=opening_frame,
                    minimum=-_FRONT_RECESS - 0.00005,
                    maximum=_KEY_HEIGHT - _FRONT_RECESS + 0.00005,
                    elem=cap_name,
                    name=f"surface_relation: {joint.name} cap occupies its exposure band",
                )
            )
            footprint_ok = (
                rest is not None
                and ctx.expect_footprint_within(
                    part,
                    frame=opening_frame,
                    margin=0.0001,
                    name=f"surface_relation: {joint.name} footprint fits its opening",
                )
            )
            with ctx.pose({joint: _KEY_TRAVEL}):
                pressed = ctx.part_world_position(part)
                pressed_normal_ok = (
                    rest is not None
                    and ctx.expect_normal_band(
                        part,
                        frame=opening_frame,
                        minimum=-_FRONT_RECESS - _KEY_TRAVEL - 0.00005,
                        maximum=(
                            _KEY_HEIGHT
                            - _FRONT_RECESS
                            - _KEY_TRAVEL
                            + 0.00005
                        ),
                        minimum_protrusion=_MIN_PRESSED_KEY_PROTRUSION,
                        elem=cap_name,
                        name=(
                            f"surface_relation: {joint.name} retains visible cap "
                            "thickness when fully pressed"
                        ),
                    )
                )
                pressed_footprint_ok = (
                    rest is not None
                    and ctx.expect_footprint_within(
                        part,
                        frame=opening_frame,
                        margin=0.0001,
                        name=(
                            f"surface_relation: {joint.name} remains in its opening "
                            "when pressed"
                        ),
                    )
                )
            moved = (
                moved
                and rest is not None
                and pressed is not None
                and pressed[2] < rest[2] - _KEY_TRAVEL * 0.70
            )
            surface_relation_ok = (
                surface_relation_ok
                and bool(normal_ok)
                and bool(footprint_ok)
                and bool(pressed_normal_ok)
                and bool(pressed_footprint_ok)
            )
        ctx.check(
            "category_anchor: every hardware key is repeated and presses inward",
            len(key_parts) == r.key_count
            and len(key_joints) == r.key_count
            and int(object_model.meta.get("key_count_actual", 0)) == r.key_count
            and moved,
            details=f"parts={len(key_parts)} joints={len(key_joints)} expected={r.key_count}",
        )
        ctx.check(
            "category_anchor: every hardware key remains exposed inside its front opening",
            len(key_parts) == r.key_count and surface_relation_ok,
            details=f"keys={len(key_parts)} expected={r.key_count}",
        )
    else:
        display = roles["display_panel"][0]
        names = {str(visual.name) for visual in display.visuals}
        ctx.check(
            "category_anchor: touch front preserves broad glass and four physical controls",
            len(key_parts) == 4
            and len(key_joints) == 4
            and any(name.endswith("__screen_glass") for name in names)
            and r.screen_width_m >= r.body_width_m * 0.80,
            details=f"keys={len(key_parts)} screen_width={r.screen_width_m}",
        )
    if r.host_mechanism == "vertical_slider":
        joint = object_model.get_articulation("host_mechanism__vertical_slider__screen_slide")
        display = roles["display_panel"][0]
        rest = ctx.part_world_position(display)
        with ctx.pose({joint: r.slider_travel_m}):
            opened = ctx.part_world_position(display)
        ctx.check(
            "category_anchor: slider display exposes the supported front bay",
            rest is not None
            and opened is not None
            and opened[1] > rest[1] + r.slider_travel_m * 0.80,
            details=f"rest={rest} opened={opened}",
        )
    elif r.host_mechanism == "corner_swivel":
        joint = object_model.get_articulation("host_mechanism__corner_swivel__screen_swivel")
        display = roles["display_panel"][0]
        rest_box = ctx.part_world_aabb(display)
        with ctx.pose({joint: r.swivel_range_rad}):
            opened_box = ctx.part_world_aabb(display)
        rest = (
            None
            if rest_box is None
            else tuple((rest_box[0][i] + rest_box[1][i]) / 2.0 for i in range(3))
        )
        opened = (
            None
            if opened_box is None
            else tuple((opened_box[0][i] + opened_box[1][i]) / 2.0 for i in range(3))
        )
        ctx.check(
            "category_anchor: swivel display rotates about the visible corner post",
            rest is not None
            and opened is not None
            and math.dist(rest, opened) > r.body_width_m * 0.45,
            details=f"rest={rest} opened={opened}",
        )
    elif r.host_mechanism == "senior_clamshell":
        joint = object_model.get_articulation("host_mechanism__senior_clamshell__lid_hinge")
        display = roles["display_panel"][0]
        opened = ctx.part_world_aabb(display)
        with ctx.pose({joint: r.clamshell_close_rad}):
            closed = ctx.part_world_aabb(display)
        ctx.check(
            "category_anchor: clamshell lid closes over the front module",
            opened is not None
            and closed is not None
            and closed[1][2] < opened[1][2] - r.body_height_m * 0.35,
            details=f"opened={opened} closed={closed}",
        )
    if r.antenna_module == "telescoping_mast":
        joint = object_model.get_articulation("antenna_module__telescoping_mast__extend_joint")
        mast = roles["antenna_mast"][0]
        rest = ctx.part_world_position(mast)
        with ctx.pose({joint: r.antenna_travel_m}):
            extended = ctx.part_world_position(mast)
        ctx.check(
            "category_anchor: telescoping mast remains guided while extending",
            rest is not None
            and extended is not None
            and extended[1] > rest[1] + r.antenna_travel_m * 0.80,
            details=f"rest={rest} extended={extended}",
        )
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=40,
        ignore_adjacent=True,
        ignore_fixed=True,
    )
    return ctx.report()


run_mobile_phone_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case(
        "slider_senior_front_telescoping",
        {
            "host_mechanism": "vertical_slider",
            "front_module": "senior_large_keypad",
            "antenna_module": "telescoping_mast",
        },
        reason="largest hardware front on the moving stacked host with the external mast",
    ),
    corner_case(
        "swivel_qwerty_telescoping",
        {
            "host_mechanism": "corner_swivel",
            "front_module": "qwerty_40",
            "antenna_module": "telescoping_mast",
        },
        reason="widest dense front under the full corner-pivot sweep",
    ),
    corner_case(
        "clamshell_touch_telescoping",
        {
            "host_mechanism": "senior_clamshell",
            "front_module": "full_touch",
            "antenna_module": "telescoping_mast",
        },
        reason="broad glass front, closing lid, and mast occupy the upper host perimeter",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_mobile_phone",
    "build_seeded_mobile_phone",
    "config_from_seed",
    "resolve_config",
    "run_mobile_phone_tests",
]
