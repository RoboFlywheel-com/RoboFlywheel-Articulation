# SPDX-License-Identifier: Apache-2.0

"""Procedural mechanical timer assembled from source-backed component families.

This is an ordinary single-file template.  SourceMap and TemplateDesign are authoring
inputs only; seeded builds depend on this module and the public SDK.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    mesh_from_geometry,
    register_interface_mate,
    rounded_rect_profile,
    superellipse_profile,
)

BodyForm = Literal[
    "arched_rect",
    "soft_square",
    "round_puck",
    "sloped_wedge",
    "tall_program_case",
    "pedestal_round",
]
ScaleStyle = Literal["numbered_radial", "direction_ring", "concentric_dual"]
WindingControl = Literal["center_paddle", "outer_bezel"]
SupportStyle = Literal["tabletop_feet", "rear_plug", "folding_magnetic_stand", "wall_bracket"]
AlertControl = Literal["none", "bell_silence_lever"]
PaletteStyle = Literal["warm_ivory", "cream_graphite", "mint_chrome", "black_silver"]
NumeralStyle = Literal[
    "block_seven_segment",
    "printed_font",
    "slim_instrument",
]


NUMERAL_STYLES: tuple[NumeralStyle, ...] = (
    "block_seven_segment",
    "printed_font",
    "slim_instrument",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "body_form",
            (
                "arched_rect",
                "soft_square",
                "round_puck",
                "sloped_wedge",
                "tall_program_case",
                "pedestal_round",
            ),
        ),
        component_slot("scale", ("numbered_radial", "direction_ring", "concentric_dual")),
        component_slot("winding_control", ("center_paddle", "outer_bezel")),
        component_slot(
            "support",
            ("tabletop_feet", "rear_plug", "folding_magnetic_stand", "wall_bracket"),
        ),
        component_slot("alert_control", ("none", "bell_silence_lever")),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_ivory": {
        "shell": (0.82, 0.79, 0.68, 1.0),
        "face": (0.94, 0.91, 0.79, 1.0),
        "ink": (0.055, 0.050, 0.042, 1.0),
        "metal": (0.56, 0.55, 0.50, 1.0),
        "pointer": (0.86, 0.055, 0.040, 1.0),
        "rubber": (0.08, 0.075, 0.065, 1.0),
    },
    "cream_graphite": {
        "shell": (0.74, 0.72, 0.66, 1.0),
        "face": (0.91, 0.89, 0.82, 1.0),
        "ink": (0.045, 0.048, 0.050, 1.0),
        "metal": (0.30, 0.31, 0.32, 1.0),
        "pointer": (0.78, 0.070, 0.045, 1.0),
        "rubber": (0.04, 0.045, 0.047, 1.0),
    },
    "mint_chrome": {
        "shell": (0.48, 0.68, 0.62, 1.0),
        "face": (0.91, 0.94, 0.88, 1.0),
        "ink": (0.035, 0.055, 0.052, 1.0),
        "metal": (0.70, 0.72, 0.72, 1.0),
        "pointer": (0.92, 0.13, 0.065, 1.0),
        "rubber": (0.055, 0.065, 0.062, 1.0),
    },
    "black_silver": {
        "shell": (0.075, 0.080, 0.082, 1.0),
        "face": (0.78, 0.79, 0.77, 1.0),
        "ink": (0.025, 0.027, 0.028, 1.0),
        "metal": (0.63, 0.65, 0.66, 1.0),
        "pointer": (0.94, 0.11, 0.055, 1.0),
        "rubber": (0.025, 0.027, 0.028, 1.0),
    },
}


@dataclass(frozen=True)
class Config:
    body_form: BodyForm
    scale: ScaleStyle
    winding_control: WindingControl
    support: SupportStyle
    alert_control: AlertControl
    palette_style: PaletteStyle = "warm_ivory"
    body_scale: float = 1.0
    dial_ratio: float = 0.72
    detail_scale: float = 1.0
    numeral_style: NumeralStyle = "block_seven_segment"
    name: str = "mechanical_timer"


@dataclass(frozen=True)
class ResolvedConfig:
    body_form: BodyForm
    scale: ScaleStyle
    winding_control: WindingControl
    support: SupportStyle
    alert_control: AlertControl
    palette_style: PaletteStyle
    body_width: float
    body_height: float
    body_depth: float
    dial_radius: float
    dial_center_z: float
    front_y: float
    front_mount_y: float
    front_tilt: float
    dial_rear_y: float
    rear_y: float
    detail_scale: float
    numeral_style: NumeralStyle
    lever_travel: float
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x6D54_494D_4552)
    return Config(
        body_form=choices["body_form"],
        scale=choices["scale"],
        winding_control=choices["winding_control"],
        support=choices["support"],
        alert_control=choices["alert_control"],
        palette_style=rng.choice(tuple(PALETTES)),
        body_scale=round(rng.uniform(0.88, 1.12), 4),
        dial_ratio=round(rng.uniform(0.67, 0.77), 4),
        detail_scale=round(rng.uniform(0.88, 1.12), 4),
        numeral_style=rng.choice(NUMERAL_STYLES),
        name=f"mechanical_timer_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "body_form": config.body_form,
            "scale": config.scale,
            "winding_control": config.winding_control,
            "support": config.support,
            "alert_control": config.alert_control,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.numeral_style not in NUMERAL_STYLES:
        raise ValueError(f"unsupported numeral_style: {config.numeral_style}")

    scale = _clamp(config.body_scale, 0.85, 1.15)
    nominal = {
        "arched_rect": (0.150, 0.158, 0.044),
        "soft_square": (0.118, 0.122, 0.042),
        "round_puck": (0.116, 0.116, 0.040),
        "sloped_wedge": (0.136, 0.126, 0.056),
        "tall_program_case": (0.068, 0.125, 0.034),
        "pedestal_round": (0.102, 0.147, 0.056),
    }[config.body_form]
    width, height, depth = (value * scale for value in nominal)
    dial_ratio = _clamp(config.dial_ratio, 0.65, 0.79)
    effective_dial_ratio = (
        min(dial_ratio * 1.15, 0.875) if config.body_form == "pedestal_round" else dial_ratio
    )
    dial_radius = min(width, height) * 0.5 * effective_dial_ratio
    dial_center_z = {
        "arched_rect": 0.008 * scale,
        "tall_program_case": 0.030 * scale,
        "pedestal_round": 0.0225 * scale,
    }.get(config.body_form, 0.0)
    front_y = -depth * 0.5
    if config.body_form == "sloped_wedge":
        # The wedge's source profile moves from front_y + 0.12 * depth at the
        # bottom to front_y - 0.10 * depth at the top.  Expose that inclined
        # plane as the common host interface for every front-mounted component.
        front_slope = -0.22 * depth / height
        front_tilt = math.atan2(0.22 * depth, height)
        front_mount_y = front_y + 0.01 * depth + front_slope * dial_center_z
        dial_rear_y = depth * 0.5
        rear_y = depth * 0.5
    elif config.body_form == "pedestal_round":
        # The source pedestal's foot is deeper than its circular timer head.
        # Front/rear dial interfaces therefore use the 28 mm head depth while
        # rear support accessories continue to use the full 56 mm envelope.
        front_tilt = 0.0
        front_mount_y = -0.014 * scale
        dial_rear_y = 0.014 * scale
        rear_y = depth * 0.5
    else:
        front_tilt = 0.0
        front_mount_y = front_y
        dial_rear_y = depth * 0.5
        rear_y = depth * 0.5
    return ResolvedConfig(
        body_form=config.body_form,
        scale=config.scale,
        winding_control=config.winding_control,
        support=config.support,
        alert_control=config.alert_control,
        palette_style=config.palette_style,
        body_width=width,
        body_height=height,
        body_depth=depth,
        dial_radius=dial_radius,
        dial_center_z=dial_center_z,
        front_y=front_y,
        front_mount_y=front_mount_y,
        front_tilt=front_tilt,
        dial_rear_y=dial_rear_y,
        rear_y=rear_y,
        detail_scale=_clamp(config.detail_scale, 0.82, 1.18),
        numeral_style=config.numeral_style,
        lever_travel=0.012 * scale,
        palette=dict(PALETTES[config.palette_style]),
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> list[tuple[str, str]]:
    return [
        ("body_form", config.body_form),
        ("scale", config.scale),
        ("winding_control", config.winding_control),
        ("support", config.support),
        ("alert_control", config.alert_control),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def _circle_profile(diameter: float, segments: int = 72) -> list[tuple[float, float]]:
    return superellipse_profile(diameter, diameter, exponent=2.0, segments=segments)


def _front_mount_origin(r: ResolvedConfig, outward_offset: float) -> Origin:
    """Place a front component parallel to the selected body's front plane."""

    cos_tilt = math.cos(r.front_tilt)
    sin_tilt = math.sin(r.front_tilt)
    return Origin(
        xyz=(
            0.0,
            r.front_mount_y - outward_offset * cos_tilt,
            r.dial_center_z - outward_offset * sin_tilt,
        ),
        rpy=(r.front_tilt, 0.0, 0.0),
    )


def _front_axis_interfaces(
    r: ResolvedConfig,
    outward_offset: float,
    *,
    consumer_name: str,
) -> tuple[AxisInterface, AxisInterface]:
    """Expose the body front normal and the component's local spin axis."""

    mount = _front_mount_origin(r, outward_offset)
    cos_tilt = math.cos(r.front_tilt)
    sin_tilt = math.sin(r.front_tilt)
    return (
        AxisInterface(
            name=f"body_form.{r.body_form}.front_axis",
            point=mount.xyz,
            axis=(0.0, -cos_tilt, -sin_tilt),
            radial=(1.0, 0.0, 0.0),
        ),
        AxisInterface(
            name=consumer_name,
            axis=(0.0, -1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
        ),
    )


def _add_axis_mated_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    provider: AxisInterface,
    consumer: AxisInterface,
    motion_limits: MotionLimits,
):
    """Create one rotating joint from independently declared local axes."""

    mate = mate_axes(provider, consumer)
    joint = model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=motion_limits,
    )
    register_interface_mate(model, name, mate)
    return joint


def _front_profile_mesh(profile, depth: float, name: str, assets: AssetContext | None):
    geometry = ExtrudeGeometry(profile, depth, center=True).rotate_x(math.pi / 2.0)
    return mesh_from_geometry(geometry, name)


def _front_annulus_mesh(
    outer_radius: float,
    inner_radius: float,
    depth: float,
    name: str,
    assets: AssetContext | None,
    *,
    outer_profile: list[tuple[float, float]] | None = None,
):
    geometry = ExtrudeWithHolesGeometry(
        outer_profile or _circle_profile(2.0 * outer_radius),
        [_circle_profile(2.0 * inner_radius)],
        depth,
        center=True,
    ).rotate_x(math.pi / 2.0)
    return mesh_from_geometry(geometry, name)


def _materials(model: ArticulatedObject, r: ResolvedConfig):
    return {
        key: model.material(f"timer_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in r.palette.items()
    }


# ---------------------------------------------------------------------------
# Body component candidates
# ---------------------------------------------------------------------------


def _body_form_arched_rect_build(model, r, mats, assets):
    body = model.part("body_form__arched_rect__housing")
    solid = (
        cq.Workplane("XY")
        .box(r.body_width, r.body_depth, r.body_height)
        .edges()
        .fillet(min(r.body_width, r.body_height) * 0.065)
    )
    body.visual(
        mesh_from_cadquery(solid, "timer_arched_rect_housing", assets=assets, tolerance=0.0005),
        material=mats["shell"],
        name="body_form__arched_rect__housing_shell", material_class_id="metal.paint_coated",
    )
    face = rounded_rect_profile(
        r.body_width * 0.93,
        r.body_height * 0.91,
        min(r.body_width, r.body_height) * 0.08,
        corner_segments=12,
    )
    body.visual(
        _front_profile_mesh(face, 0.0012, "timer_arched_front_face", assets),
        origin=Origin(xyz=(0.0, r.front_y - 0.0008, 0.0)),
        material=mats["face"],
        name="body_form__arched_rect__front_face", material_class_id="metal.paint_coated",
    )
    return body


def _body_form_soft_square_build(model, r, mats, assets):
    body = model.part("body_form__soft_square__housing")
    solid = (
        cq.Workplane("XY")
        .box(r.body_width, r.body_depth, r.body_height)
        .edges()
        .fillet(min(r.body_width, r.body_height) * 0.13)
    )
    body.visual(
        mesh_from_cadquery(solid, "timer_soft_square_housing", assets=assets, tolerance=0.00045),
        material=mats["shell"],
        name="body_form__soft_square__housing_shell", material_class_id="metal.paint_coated",
    )
    return body


def _body_form_round_puck_build(model, r, mats, assets):
    body = model.part("body_form__round_puck__housing")
    radius = min(r.body_width, r.body_height) * 0.5
    puck = (
        cq.Workplane("XZ")
        .circle(radius)
        .extrude(r.body_depth * 0.5, both=True)
        .edges()
        .chamfer(0.0015)
    )
    body.visual(
        mesh_from_cadquery(puck, "timer_round_puck_housing", assets=assets, tolerance=0.0004),
        material=mats["shell"],
        name="body_form__round_puck__housing_shell", material_class_id="metal.paint_coated",
    )
    return body


def _body_form_sloped_wedge_build(model, r, mats, assets):
    body = model.part("body_form__sloped_wedge__housing")
    front_bottom = r.front_y + r.body_depth * 0.12
    front_top = r.front_y - r.body_depth * 0.10
    profile = [
        (front_bottom, -r.body_height * 0.5),
        (r.rear_y, -r.body_height * 0.5),
        (r.rear_y, r.body_height * 0.5),
        (front_top, r.body_height * 0.5),
    ]
    wedge = (
        cq.Workplane("YZ")
        .polyline(profile)
        .close()
        .extrude(r.body_width * 0.5, both=True)
        .edges("|X")
        .fillet(0.004)
    )
    body.visual(
        mesh_from_cadquery(wedge, "timer_sloped_wedge_housing", assets=assets, tolerance=0.0005),
        material=mats["shell"],
        name="body_form__sloped_wedge__housing_shell", material_class_id="metal.paint_coated",
    )
    return body


def _tall_program_case_shape(scale: float):
    """Source-backed 003 silhouette: round head fused to a long lower case."""

    lower = (
        cq.Workplane("XY")
        .center(0.0, -0.025 * scale)
        .rect(0.064 * scale, 0.074 * scale)
        .extrude(0.017 * scale, both=True)
        .edges("|Z")
        .fillet(0.016 * scale)
    )
    upper = (
        cq.Workplane("XY")
        .center(0.0, 0.030 * scale)
        .circle(0.033 * scale)
        .extrude(0.017 * scale, both=True)
    )
    body = lower.union(upper)
    recess = (
        cq.Workplane("XY")
        .center(0.0, -0.031 * scale)
        .circle(0.024 * scale)
        .extrude(0.0045 * scale)
        .translate((0.0, 0.0, 0.0135 * scale))
    )
    body = body.cut(recess)
    for x, z, width, height, angle in (
        (-0.0095, -0.0265, 0.0040, 0.0120, -27.0),
        (0.0095, -0.0265, 0.0040, 0.0120, 27.0),
        (0.0, -0.0460, 0.0042, 0.0100, 0.0),
    ):
        cutter = (
            cq.Workplane("XY")
            .rect(width * scale, height * scale)
            .extrude(0.010 * scale)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
            .translate((x * scale, z * scale, 0.009 * scale))
        )
        body = body.cut(cutter)
    indicator_hole = (
        cq.Workplane("XY")
        .center(0.016 * scale, -0.004 * scale)
        .circle(0.0014 * scale)
        .extrude(0.006 * scale)
        .translate((0.0, 0.0, 0.012 * scale))
    )
    return body.cut(indicator_hole).rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)


def _body_form_tall_program_case_build(model, r, mats, assets):
    body = model.part("body_form__tall_program_case__housing")
    scale = r.body_width / 0.068
    body.visual(
        mesh_from_cadquery(
            _tall_program_case_shape(scale),
            "timer_tall_program_case",
            assets=assets,
            tolerance=0.0004,
        ),
        material=mats["shell"],
        name="body_form__tall_program_case__housing_shell", material_class_id="metal.paint_coated",
    )
    body.visual(
        Sphere(radius=0.00155 * scale),
        origin=Origin(xyz=(0.016 * scale, r.front_mount_y - 0.00045, -0.004 * scale)),
        material=mats["pointer"],
        name="body_form__tall_program_case__indicator_lens", material_class_id="plastic.frosted_translucent",
    )
    return body


def _pedestal_round_shape(scale: float, dial_center_z: float):
    """Source-backed 002 case, pedestal, rounded foot and rear gusset."""

    case = (
        cq.Workplane("XY")
        .cylinder(0.028 * scale, 0.051 * scale, centered=True)
        .edges()
        .chamfer(0.0014 * scale)
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
        .translate((0.0, 0.0, dial_center_z))
    )
    z_shift = -0.0735 * scale
    pedestal = (
        cq.Workplane("XY")
        .box(0.052 * scale, 0.034 * scale, 0.041 * scale, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.005 * scale)
        .translate((0.0, 0.003 * scale, z_shift + 0.009 * scale))
    )
    foot = (
        cq.Workplane("XY")
        .box(0.084 * scale, 0.056 * scale, 0.012 * scale, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.010 * scale)
        .translate((0.0, 0.0, z_shift))
    )
    rear_gusset = (
        cq.Workplane("XY")
        .box(0.038 * scale, 0.024 * scale, 0.030 * scale, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.004 * scale)
        .translate((0.0, 0.010 * scale, z_shift + 0.036 * scale))
    )
    return case.union(pedestal).union(foot).union(rear_gusset)


def _body_form_pedestal_round_build(model, r, mats, assets):
    body = model.part("body_form__pedestal_round__housing")
    scale = r.body_width / 0.102
    body.visual(
        mesh_from_cadquery(
            _pedestal_round_shape(scale, r.dial_center_z),
            "timer_pedestal_round_case",
            assets=assets,
            tolerance=0.0004,
        ),
        material=mats["shell"],
        name="body_form__pedestal_round__housing_shell", material_class_id="metal.paint_coated",
    )
    foot_inset = rounded_rect_profile(
        0.072 * scale,
        0.006 * scale,
        0.002 * scale,
        corner_segments=10,
    )
    body.visual(
        _front_profile_mesh(
            foot_inset,
            0.0012 * scale,
            "timer_pedestal_foot_inset",
            assets,
        ),
        origin=Origin(xyz=(0.0, -0.0284 * scale, -0.0675 * scale)),
        material=mats["face"],
        name="body_form__pedestal_round__foot_inset", material_class_id="metal.paint_coated",
    )
    return body


_BODY_BUILDERS = {
    "arched_rect": _body_form_arched_rect_build,
    "soft_square": _body_form_soft_square_build,
    "round_puck": _body_form_round_puck_build,
    "sloped_wedge": _body_form_sloped_wedge_build,
    "tall_program_case": _body_form_tall_program_case_build,
    "pedestal_round": _body_form_pedestal_round_build,
}


def _add_rear_spring_case(body, r, mats):
    body.visual(
        Cylinder(radius=r.dial_radius * 0.83, length=0.008),
        origin=Origin(
            xyz=(0.0, r.dial_rear_y + 0.0030, r.dial_center_z),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["metal"],
        name="assembly__rear_spring_case", material_class_id="metal.steel_bare",
    )
    body.visual(
        Cylinder(radius=r.dial_radius * 0.68, length=0.0015),
        origin=Origin(
            xyz=(0.0, r.dial_rear_y + 0.0074, r.dial_center_z),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["shell"],
        name="assembly__rear_case_cover", material_class_id="metal.paint_coated",
    )
    body.visual(
        _front_annulus_mesh(
            r.dial_radius * 1.09,
            r.dial_radius * 0.995,
            0.0024,
            "timer_front_bezel_capture",
            None,
        ),
        origin=_front_mount_origin(r, 0.0012),
        material=mats["metal"],
        name="assembly__front_bezel_capture", material_class_id="metal.chrome_polished",
    )


# ---------------------------------------------------------------------------
# Dial scale candidates and invariant pointer
# ---------------------------------------------------------------------------


_DIGIT_SEGMENTS = {
    "0": "abcedf",
    "1": "bc",
    "2": "abged",
    "3": "abgcd",
    "4": "fgbc",
    "5": "afgcd",
    "6": "afgecd",
    "7": "abc",
    "8": "abcdefg",
    "9": "abfgcd",
}


def _add_block_digit(part, digit, x, z, size, y, material, prefix):
    """Original robust rectangular seven-segment numeral."""

    width, height, bar = size, size * 1.55, size * 0.17
    vertical = height * 0.48
    placements = {
        "a": ((x, z + height * 0.50), (width, 0.00045, bar)),
        "g": ((x, z), (width, 0.00045, bar)),
        "d": ((x, z - height * 0.50), (width, 0.00045, bar)),
        "b": ((x + width * 0.50, z + height * 0.25), (bar, 0.00045, vertical)),
        "c": ((x + width * 0.50, z - height * 0.25), (bar, 0.00045, vertical)),
        "e": ((x - width * 0.50, z - height * 0.25), (bar, 0.00045, vertical)),
        "f": ((x - width * 0.50, z + height * 0.25), (bar, 0.00045, vertical)),
    }
    for segment in _DIGIT_SEGMENTS[digit]:
        (px, pz), dims = placements[segment]
        part.visual(
            Box(dims),
            origin=Origin(xyz=(px, y, pz)),
            material=material,
            name=f"{prefix}_{segment}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )


_LABEL_FONT_PATH = Path(__file__).resolve().parent / "fonts" / "DroidSans.ttf"


def _occ_label_solid(text, height, depth, font_path):
    """Extruded OCC glyph solid; None when OCC yields a zero-face shape.

    When the font cannot be resolved (headless worker with no fontconfig
    fonts), Font_BRepTextBuilder returns an EMPTY compound and cadquery dies
    with ``IndexError: list index out of range`` at ``text_flat.Faces()[0]``
    in occ_impl/shapes.py -- the crash class that killed pictureX_0611_compass
    on MDL workers.  Contain that here.
    """
    try:
        glyphs = cq.Workplane("XZ").text(
            text,
            height,
            depth,
            combine=False,
            halign="center",
            valign="center",
            fontPath=font_path,
        )
    except Exception:
        return None
    return glyphs if glyphs.solids().vals() else None


def _stroked_label_solid(text, height, depth):
    """Seven-segment box-stroke digits for environments where OCC font
    rendering is unavailable; the string is centered at the origin like
    halign/valign=center.  None for unsupported characters (only digits and
    spaces can be drawn)."""
    width = height * 0.62
    bar = height * 0.13
    half_h = height * 0.45
    pitch = width * 1.30

    def _bar(cx, cz, dx, dz):
        return cq.Workplane("XZ").box(dx, dz, depth).translate((cx, cz, depth * 0.5))

    segments = {
        "a": (0.0, half_h - bar * 0.5, width, bar),
        "g": (0.0, 0.0, width, bar),
        "d": (0.0, -(half_h - bar * 0.5), width, bar),
        "b": (width * 0.5 - bar * 0.5, half_h * 0.5, bar, half_h),
        "c": (width * 0.5 - bar * 0.5, -half_h * 0.5, bar, half_h),
        "e": (-(width * 0.5 - bar * 0.5), -half_h * 0.5, bar, half_h),
        "f": (-(width * 0.5 - bar * 0.5), half_h * 0.5, bar, half_h),
    }
    solid = None
    for index, char in enumerate(text):
        if char == " ":
            continue
        digit = _DIGIT_SEGMENTS.get(char)
        if digit is None:
            return None
        char_x = (index - (len(text) - 1) * 0.5) * pitch
        for segment in digit:
            sx, sz, dx, dz = segments[segment]
            piece = _bar(char_x + sx, sz, dx, dz)
            solid = piece if solid is None else solid.union(piece)
    return solid


def _printed_label_mesh(text, height, depth, name, assets):
    """Source-style upright dial text, centered by its actual glyph bounds.

    Font resolution chains bundled DroidSans -> OCC system font -> stroked
    seven-segment digits, so no environment can produce a zero-face text
    solid.  None for empty/unsupported text; the caller skips the visual.
    """

    text = (text or "").strip()
    if not text:
        return None
    font_path = str(_LABEL_FONT_PATH) if _LABEL_FONT_PATH.is_file() else None
    glyphs = _occ_label_solid(text, height, depth, font_path) if font_path else None
    if glyphs is None:
        glyphs = _occ_label_solid(text, height, depth, None)
    if glyphs is None:
        glyphs = _stroked_label_solid(text, height, depth)
    if glyphs is None:
        return None
    bounds = glyphs.val().BoundingBox()
    glyphs = glyphs.translate(
        (
            -(bounds.xmin + bounds.xmax) * 0.5,
            0.0,
            -(bounds.zmin + bounds.zmax) * 0.5,
        )
    )
    return mesh_from_cadquery(glyphs, name, assets=assets, tolerance=0.00012)


def _add_printed_label(part, text, x, z, height, material, prefix, assets):
    label = _printed_label_mesh(
        text,
        height,
        0.00034,
        f"timer_printed_minute_{text}",
        assets,
    )
    if label is None:
        return
    part.visual(
        label,
        origin=Origin(xyz=(x, -0.00060, z)),
        material=material,
        name=prefix, appearance_only=AppearanceOnlySpec(kind="text", text=str(text)),
    )


def _instrument_bar_mesh(length, stroke, name, assets):
    tip = min(stroke * 0.48, length * 0.14)
    profile = [
        (-length * 0.5 + tip, -stroke * 0.5),
        (length * 0.5 - tip, -stroke * 0.5),
        (length * 0.5, 0.0),
        (length * 0.5 - tip, stroke * 0.5),
        (-length * 0.5 + tip, stroke * 0.5),
        (-length * 0.5, 0.0),
    ]
    return _front_profile_mesh(profile, 0.00034, name, assets)


def _add_instrument_digit(part, digit, x, z, size, y, material, prefix, assets):
    """Slim source-style seven-segment digit with chamfered stroke ends."""

    width = size * 0.78
    height = size * 1.42
    stroke = size * 0.11
    vertical = height * 0.46
    placements = {
        "a": ((x, z + height * 0.50), width, False),
        "g": ((x, z), width, False),
        "d": ((x, z - height * 0.50), width, False),
        "b": ((x + width * 0.50, z + height * 0.25), vertical, True),
        "c": ((x + width * 0.50, z - height * 0.25), vertical, True),
        "e": ((x - width * 0.50, z - height * 0.25), vertical, True),
        "f": ((x - width * 0.50, z + height * 0.25), vertical, True),
    }
    for segment in _DIGIT_SEGMENTS[digit]:
        (px, pz), length, vertical_segment = placements[segment]
        part.visual(
            _instrument_bar_mesh(
                length,
                stroke,
                "timer_instrument_digit_segment",
                assets,
            ),
            origin=Origin(
                # Sink the 0.34 mm stroke 0.05 mm into the dial skin so the
                # refined numeral remains one supported visual island.
                xyz=(px, y + 0.00005, pz),
                rpy=(0.0, math.pi / 2.0, 0.0) if vertical_segment else (0.0, 0.0, 0.0),
            ),
            material=material,
            name=f"{prefix}_{segment}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )


def _add_tick_ring(part, radius, count, major_step, y, material, prefix, scale=1.0):
    for index in range(count):
        angle = 2.0 * math.pi * index / count
        major = index % major_step == 0
        length = radius * (0.11 if major else 0.065) * scale
        width = radius * (0.018 if major else 0.010) * scale
        center = radius - length * 0.5
        part.visual(
            Box((width, 0.00042, length)),
            origin=Origin(
                xyz=(center * math.sin(angle), y, center * math.cos(angle)),
                rpy=(0.0, angle, 0.0),
            ),
            material=material,
            name=f"{prefix}_{index:02d}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )


def _new_dial(model, body, r, mats, candidate):
    dial = model.part(f"scale__{candidate}__dial")
    dial.visual(
        Cylinder(radius=r.dial_radius, length=0.0012),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["face"],
        name=f"scale__{candidate}__dial_plate", material_class_id="metal.paint_coated",
    )
    joint_name = f"scale__{candidate}__dial_rotation"
    provider, consumer = _front_axis_interfaces(
        r,
        0.0030005,
        consumer_name=f"scale.{candidate}.dial_axis",
    )
    _add_axis_mated_joint(
        model,
        name=joint_name,
        parent=body,
        child=dial,
        provider=provider,
        consumer=consumer,
        motion_limits=MotionLimits(effort=0.35, velocity=2.5, lower=-math.pi, upper=math.pi),
    )
    return dial


def _scale_numbered_radial_build(model, body, r, mats, assets):
    dial = _new_dial(model, body, r, mats, "numbered_radial")
    _add_tick_ring(
        dial, r.dial_radius * 0.93, 60, 5, -0.00078, mats["ink"], "scale__numbered_radial__tick"
    )
    labels = (
        ("60", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55")
        if r.numeral_style != "block_seven_segment"
        else tuple(str(value) for value in range(0, 60, 5))
    )
    radius = r.dial_radius * 0.73
    for index, label in enumerate(labels):
        angle = math.radians(index * 30.0)
        x, z = radius * math.sin(angle), radius * math.cos(angle)
        if r.numeral_style == "printed_font":
            _add_printed_label(
                dial,
                label,
                x,
                z,
                r.dial_radius * 0.14 * r.detail_scale,
                mats["ink"],
                f"scale__numbered_radial__number_{label}",
                assets,
            )
            continue

        size = (
            r.dial_radius
            * (0.075 if r.numeral_style == "block_seven_segment" else 0.085)
            * r.detail_scale
        )
        pitch = size * (1.18 if r.numeral_style == "block_seven_segment" else 1.02)
        for digit_index, digit in enumerate(label):
            args = (
                dial,
                digit,
                x + (digit_index - (len(label) - 1) * 0.5) * pitch,
                z,
                size,
                -0.00079,
                mats["ink"],
                f"scale__numbered_radial__number_{label}_{digit_index}",
            )
            if r.numeral_style == "block_seven_segment":
                _add_block_digit(*args)
            else:
                _add_instrument_digit(*args, assets)
    return dial


def _scale_direction_ring_build(model, body, r, mats, assets):
    dial = _new_dial(model, body, r, mats, "direction_ring")
    _add_tick_ring(
        dial, r.dial_radius * 0.91, 48, 4, -0.00078, mats["ink"], "scale__direction_ring__tick"
    )
    size = r.dial_radius * 0.10 * r.detail_scale
    for label, angle in (("3", math.pi / 2), ("6", math.pi), ("9", -math.pi / 2), ("12", 0.0)):
        radius = r.dial_radius * 0.62
        x, z = radius * math.sin(angle), radius * math.cos(angle)
        if r.numeral_style == "printed_font":
            _add_printed_label(
                dial,
                label,
                x,
                z,
                r.dial_radius * 0.15 * r.detail_scale,
                mats["ink"],
                f"scale__direction_ring__number_{label}",
                assets,
            )
            continue
        for index, digit in enumerate(label):
            block_style = r.numeral_style == "block_seven_segment"
            args = (
                dial,
                digit,
                x + (index - (len(label) - 1) * 0.5) * size * (1.2 if block_style else 1.02),
                z,
                size,
                -0.00080,
                mats["ink"],
                f"scale__direction_ring__number_{label}_{index}",
            )
            if block_style:
                _add_block_digit(*args)
            else:
                _add_instrument_digit(*args, assets)
    arc_radius = r.dial_radius * 0.48
    for index, angle in enumerate(tuple(math.radians(value) for value in range(-58, 59, 12))):
        dial.visual(
            Box((r.dial_radius * 0.045, 0.00044, r.dial_radius * 0.018)),
            origin=Origin(
                xyz=(arc_radius * math.sin(angle), -0.00081, arc_radius * math.cos(angle)),
                rpy=(0.0, angle, 0.0),
            ),
            material=mats["ink"],
            name=f"scale__direction_ring__direction_arc_{index}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    arrow = [
        (0.0, 0.0),
        (-r.dial_radius * 0.08, -r.dial_radius * 0.05),
        (r.dial_radius * 0.08, -r.dial_radius * 0.05),
    ]
    dial.visual(
        _front_profile_mesh(arrow, 0.00045, "timer_direction_arrow", assets),
        origin=Origin(
            xyz=(
                arc_radius * math.sin(math.radians(66)),
                -0.00082,
                arc_radius * math.cos(math.radians(66)),
            )
        ),
        material=mats["ink"],
        name="scale__direction_ring__arrow", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    return dial


def _scale_concentric_dual_build(model, body, r, mats, assets):
    dial = _new_dial(model, body, r, mats, "concentric_dual")
    _add_tick_ring(
        dial,
        r.dial_radius * 0.94,
        60,
        5,
        -0.00078,
        mats["ink"],
        "scale__concentric_dual__outer_tick",
    )
    _add_tick_ring(
        dial,
        r.dial_radius * 0.68,
        30,
        5,
        -0.00080,
        mats["ink"],
        "scale__concentric_dual__inner_tick",
        scale=0.82,
    )
    dial.visual(
        _front_annulus_mesh(
            r.dial_radius * 0.76,
            r.dial_radius * 0.745,
            0.00042,
            "timer_dual_scale_separator",
            assets,
        ),
        origin=Origin(xyz=(0.0, -0.00082, 0.0)),
        material=mats["ink"],
        name="scale__concentric_dual__separator_ring", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    return dial


_SCALE_BUILDERS = {
    "numbered_radial": _scale_numbered_radial_build,
    "direction_ring": _scale_direction_ring_build,
    "concentric_dual": _scale_concentric_dual_build,
}


def _build_pointer(model, body, r, mats):
    pointer = model.part("pointer__hand")
    pointer.visual(
        Box((r.dial_radius * 0.045, 0.00048, r.dial_radius * 0.90)),
        origin=Origin(xyz=(0.0, 0.0, r.dial_radius * 0.32)),
        material=mats["pointer"],
        name="pointer__hand__red_blade", material_class_id="metal.paint_coated",
    )
    pointer.visual(
        Box((r.dial_radius * 0.035, 0.00046, r.dial_radius * 0.34)),
        origin=Origin(xyz=(0.0, 0.0, -r.dial_radius * 0.18)),
        material=mats["metal"],
        name="pointer__hand__counter_tail", material_class_id="metal.brushed_silver",
    )
    pointer.visual(
        Cylinder(radius=r.dial_radius * 0.075, length=0.0012),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["face"],
        name="pointer__hand__hub", material_class_id="metal.paint_coated",
    )
    provider, consumer = _front_axis_interfaces(
        r,
        0.0042010,
        consumer_name="pointer.hand.axis",
    )
    _add_axis_mated_joint(
        model,
        name="pointer__hand__rotation",
        parent=body,
        child=pointer,
        provider=provider,
        consumer=consumer,
        motion_limits=MotionLimits(effort=0.08, velocity=4.0, lower=-math.pi, upper=math.pi),
    )
    return pointer


# ---------------------------------------------------------------------------
# Winding-control candidates
# ---------------------------------------------------------------------------


def _winding_control_center_paddle_build(model, body, r, mats, assets):
    control = model.part("winding_control__center_paddle__control")
    length = r.dial_radius * 1.35
    width = r.dial_radius * 0.19
    paddle = rounded_rect_profile(width, length, width * 0.46, corner_segments=10)
    control.visual(
        _front_profile_mesh(paddle, 0.0055, "timer_center_winding_paddle", assets),
        material=mats["face"],
        name="winding_control__center_paddle__grip", material_class_id="metal.paint_coated",
    )
    control.visual(
        Cylinder(radius=width * 0.65, length=0.0065),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="winding_control__center_paddle__hub", material_class_id="metal.chrome_polished",
    )
    provider, consumer = _front_axis_interfaces(
        r,
        0.0080515,
        consumer_name="winding_control.center_paddle.axis",
    )
    _add_axis_mated_joint(
        model,
        name="winding_control__center_paddle__rotation",
        parent=body,
        child=control,
        provider=provider,
        consumer=consumer,
        motion_limits=MotionLimits(effort=0.8, velocity=4.0, lower=-math.pi, upper=math.pi),
    )
    return control


def _winding_control_outer_bezel_build(model, body, r, mats, assets):
    control = model.part("winding_control__outer_bezel__control")
    outer = r.dial_radius * 1.13
    inner = r.dial_radius * 1.03
    grip_depth = r.dial_radius * 0.024
    segment_count = 24
    tangential = 2.0 * math.pi * inner / segment_count * 1.12
    for index in range(segment_count):
        angle = 2.0 * math.pi * index / segment_count
        segment_outer = outer if index % 2 == 0 else outer - grip_depth
        radial = segment_outer - inner
        center = inner + radial * 0.5
        control.visual(
            Box((tangential, 0.0032, radial)),
            origin=Origin(
                xyz=(center * math.sin(angle), 0.0, center * math.cos(angle)),
                rpy=(0.0, angle, 0.0),
            ),
            material=mats["metal"],
            name=f"winding_control__outer_bezel__grip_segment_{index:02d}", material_class_id="metal.chrome_polished",
        )
    control.visual(
        Box((r.dial_radius * 0.035, 0.0008, r.dial_radius * 0.10)),
        origin=Origin(xyz=(0.0, -0.0018, outer * 0.94)),
        material=mats["ink"],
        name="winding_control__outer_bezel__marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    provider, consumer = _front_axis_interfaces(
        r,
        0.0040005,
        consumer_name="winding_control.outer_bezel.axis",
    )
    _add_axis_mated_joint(
        model,
        name="winding_control__outer_bezel__rotation",
        parent=body,
        child=control,
        provider=provider,
        consumer=consumer,
        motion_limits=MotionLimits(effort=0.8, velocity=2.0, lower=-math.pi, upper=math.pi),
    )
    return control


_WINDING_BUILDERS = {
    "center_paddle": _winding_control_center_paddle_build,
    "outer_bezel": _winding_control_outer_bezel_build,
}


# ---------------------------------------------------------------------------
# Support candidates
# ---------------------------------------------------------------------------


def _support_tabletop_feet_build(model, body, r, mats, assets):
    support = model.part("support__tabletop_feet__support")
    for index, x in enumerate((-r.body_width * 0.31, r.body_width * 0.31)):
        support.visual(
            Box((r.body_width * 0.18, r.body_depth * 0.36, r.body_height * 0.07)),
            origin=Origin(xyz=(x, 0.0, 0.0)),
            material=mats["rubber"],
            name=f"support__tabletop_feet__foot_{index}", material_class_id="rubber.smooth_plain",
        )
    support.visual(
        Box((r.body_width * 0.62, r.body_depth * 0.18, r.body_height * 0.04)),
        material=mats["rubber"],
        name="support__tabletop_feet__bridge", material_class_id="rubber.smooth_plain",
    )
    model.articulation(
        "support__tabletop_feet__mount",
        ArticulationType.FIXED,
        parent=body,
        child=support,
        origin=Origin(xyz=(0.0, r.rear_y + r.body_depth * 0.14, -r.body_height * 0.445)),
    )
    return support


def _support_rear_plug_build(model, body, r, mats, assets):
    support = model.part("support__rear_plug__support")
    support.visual(
        Cylinder(radius=r.dial_radius * 0.34, length=0.005),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["shell"],
        name="support__rear_plug__boss", material_class_id="metal.paint_coated",
    )
    for index, x in enumerate((-0.008, 0.008)):
        support.visual(
            Box((0.004, 0.020, 0.012)),
            origin=Origin(xyz=(x * r.body_width / 0.12, 0.0125, -0.002)),
            material=mats["metal"],
            name=f"support__rear_plug__blade_{index}", material_class_id="metal.steel_bare",
        )
    model.articulation(
        "support__rear_plug__mount",
        ArticulationType.FIXED,
        parent=body,
        child=support,
        origin=Origin(xyz=(0.0, r.dial_rear_y + 0.01015, r.dial_center_z)),
    )
    return support


def _support_folding_magnetic_stand_build(model, body, r, mats, assets):
    support = model.part("support__folding_magnetic_stand__support")
    width = r.body_width * 0.62
    height = r.body_height * 0.62
    if r.body_form == "pedestal_round":
        hinge_z = r.dial_center_z + r.body_width * 0.18
        stand_offset_y = 0.004
    else:
        hinge_z = r.body_height * (0.36 if r.body_form == "round_puck" else 0.46)
        stand_offset_y = 0.0
    barrel_length = width * 0.84
    socket_length = width * 0.10
    panel = rounded_rect_profile(width, height, width * 0.07, corner_segments=10)
    support.visual(
        _front_profile_mesh(panel, 0.0035, "timer_folding_stand_panel", assets),
        origin=Origin(xyz=(0.0, 0.008, -height * 0.5)),
        material=mats["metal"],
        name="support__folding_magnetic_stand__panel", material_class_id="metal.stainless_matte",
    )
    support.visual(
        Box((width * 0.74, 0.010, 0.010)),
        origin=Origin(xyz=(0.0, 0.004, -0.004)),
        material=mats["metal"],
        name="support__folding_magnetic_stand__hinge_bridge", material_class_id="metal.stainless_matte",
    )
    for index, x in enumerate((-width * 0.28, width * 0.28)):
        support.visual(
            Box((width * 0.17, 0.006, width * 0.17)),
            origin=Origin(xyz=(x, 0.008, -height * 0.70)),
            material=mats["metal"],
            name=f"support__folding_magnetic_stand__magnet_seat_{index}", material_class_id="metal.stainless_matte",
        )
        support.visual(
            Cylinder(radius=width * 0.075, length=0.0015),
            origin=Origin(
                xyz=(x, 0.008, -height * 0.70),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["rubber"],
            name=f"support__folding_magnetic_stand__magnet_{index}", material_class_id="rubber.smooth_plain",
        )
    support.visual(
        Cylinder(radius=0.0025, length=barrel_length),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="support__folding_magnetic_stand__hinge_barrel", material_class_id="metal.stainless_matte",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        socket_x = sign * (barrel_length + socket_length) * 0.5
        body.visual(
            Box((socket_length, 0.008, 0.008)),
            origin=Origin(xyz=(socket_x, r.dial_rear_y - 0.001, hinge_z)),
            material=mats["shell"],
            name=f"support__folding_magnetic_stand__hinge_ear_{index}", material_class_id="metal.paint_coated",
        )
        body.visual(
            Cylinder(radius=0.004, length=socket_length),
            origin=Origin(
                xyz=(socket_x, r.dial_rear_y + 0.0015, hinge_z),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["metal"],
            name=f"support__folding_magnetic_stand__hinge_socket_{index}", material_class_id="metal.stainless_matte",
        )
    joint_name = "support__folding_magnetic_stand__hinge"
    provider = AxisInterface(
        name="body_form.rear_stand_hinge_axis",
        point=(0.0, r.dial_rear_y + 0.0015 + stand_offset_y, hinge_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
    )
    consumer = AxisInterface(
        name="support.folding_magnetic_stand.hinge_axis",
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
    )
    _add_axis_mated_joint(
        model,
        name=joint_name,
        parent=body,
        child=support,
        provider=provider,
        consumer=consumer,
        motion_limits=MotionLimits(effort=1.4, velocity=1.5, lower=0.0, upper=1.05),
    )
    return support


def _wall_bracket_shape(width: float, height: float):
    plate = cq.Workplane("XY").rect(width, height).extrude(0.0018).edges("|Z").fillet(0.003)
    for x in (-width * 0.28, width * 0.28):
        round_hole = cq.Workplane("XY").center(x, height * 0.23).circle(0.003).extrude(0.003)
        slot = cq.Workplane("XY").center(x, height * 0.06).rect(0.003, height * 0.30).extrude(0.003)
        plate = plate.cut(round_hole).cut(slot)
    for x in (-width * 0.43, width * 0.43):
        rib = cq.Workplane("XY").center(x, 0.0).rect(0.0018, height * 0.60).extrude(0.0024)
        plate = plate.union(rib)
    return plate.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)


def _support_wall_bracket_build(model, body, r, mats, assets):
    support = model.part("support__wall_bracket__support")
    width, height = r.body_width * 0.42, r.body_height * 0.46
    support.visual(
        mesh_from_cadquery(
            _wall_bracket_shape(width, height),
            "timer_wall_bracket",
            assets=assets,
            tolerance=0.0003,
        ),
        origin=Origin(xyz=(0.0, 0.006, 0.0)),
        material=mats["metal"],
        name="support__wall_bracket__plate", material_class_id="metal.paint_coated",
    )
    for index, x in enumerate((-width * 0.30, width * 0.30)):
        support.visual(
            Cylinder(radius=0.004, length=0.004),
            origin=Origin(xyz=(x, 0.004, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["shell"],
            name=f"support__wall_bracket__spacer_{index}", material_class_id="metal.paint_coated",
        )
    model.articulation(
        "support__wall_bracket__mount",
        ArticulationType.FIXED,
        parent=body,
        child=support,
        origin=Origin(xyz=(0.0, r.dial_rear_y + 0.004, r.dial_center_z - r.body_height * 0.12)),
    )
    return support


_SUPPORT_BUILDERS = {
    "tabletop_feet": _support_tabletop_feet_build,
    "rear_plug": _support_rear_plug_build,
    "folding_magnetic_stand": _support_folding_magnetic_stand_build,
    "wall_bracket": _support_wall_bracket_build,
}


# ---------------------------------------------------------------------------
# Optional alert-control candidates
# ---------------------------------------------------------------------------


def _alert_control_none_build(model, body, r, mats, assets):
    return None


def _alert_control_bell_silence_lever_build(model, body, r, mats, assets):
    if r.body_form in {"round_puck", "pedestal_round"}:
        track_x = r.body_width * 0.43
    elif r.body_form == "tall_program_case":
        track_x = r.body_width * 0.485
    else:
        track_x = r.body_width * 0.5 + 0.0012
    body.visual(
        Box((0.0025, 0.008, r.body_height * 0.20)),
        origin=Origin(xyz=(track_x, 0.0, r.body_height * 0.23)),
        material=mats["metal"],
        name="alert_control__bell_silence_lever__track", material_class_id="metal.steel_bare",
    )
    lever = model.part("alert_control__bell_silence_lever__control")
    lever.visual(
        Box((0.005, 0.005, r.body_height * 0.085)),
        origin=Origin(xyz=(0.004, 0.0, 0.0)),
        material=mats["metal"],
        name="alert_control__bell_silence_lever__slide", material_class_id="metal.steel_bare",
    )
    lever.visual(
        Box((0.010, 0.004, r.body_height * 0.055)),
        origin=Origin(xyz=(0.008, -0.001, 0.0)),
        material=mats["shell"],
        name="alert_control__bell_silence_lever__grip", material_class_id="metal.paint_coated",
    )
    model.articulation(
        "alert_control__bell_silence_lever__slide_joint",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lever,
        origin=Origin(xyz=(track_x - 0.00025, 0.0, r.body_height * 0.17)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.3, velocity=0.5, lower=0.0, upper=r.lever_travel),
    )
    return lever


_ALERT_BUILDERS = {
    "none": _alert_control_none_build,
    "bell_silence_lever": _alert_control_bell_silence_lever_build,
}


def build_mechanical_timer_with_rotating_dial(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r)

    body = _BODY_BUILDERS[r.body_form](model, r, mats, assets)
    _add_rear_spring_case(body, r, mats)
    _SCALE_BUILDERS[r.scale](model, body, r, mats, assets)
    _build_pointer(model, body, r, mats)
    _WINDING_BUILDERS[r.winding_control](model, body, r, mats, assets)
    _SUPPORT_BUILDERS[r.support](model, body, r, mats, assets)
    _ALERT_BUILDERS[r.alert_control](model, body, r, mats, assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["numeral_style"] = r.numeral_style
    model.meta["source_family"] = "pictureX/0611/mechanical_timer_with_rotating_dial"
    return model


def build_seeded_mechanical_timer_with_rotating_dial(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_mechanical_timer_with_rotating_dial(config_from_seed(seed), assets=assets)


def run_mechanical_timer_with_rotating_dial_tests(
    object_model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()

    parts = {part.name for part in object_model.parts}
    joints = {joint.name: joint for joint in object_model.articulations}
    body_name = f"body_form__{r.body_form}__housing"
    dial_name = f"scale__{r.scale}__dial"
    winding_name = f"winding_control__{r.winding_control}__control"
    support_name = f"support__{r.support}__support"

    ctx.check("selected body component exists", body_name in parts, details=str(sorted(parts)))
    ctx.check("selected scale component exists", dial_name in parts)
    ctx.check("pointer mechanism exists", "pointer__hand" in parts)
    ctx.check("selected winding control exists", winding_name in parts)
    ctx.check("selected support exists", support_name in parts)

    dial_joint = joints.get(f"scale__{r.scale}__dial_rotation")
    pointer_joint = joints.get("pointer__hand__rotation")
    winding_joint = joints.get(f"winding_control__{r.winding_control}__rotation")
    ctx.check(
        "dial pointer and winding controls are independently revolute",
        all(
            joint is not None and joint.articulation_type == ArticulationType.REVOLUTE
            for joint in (dial_joint, pointer_joint, winding_joint)
        ),
    )
    ctx.check(
        "face mechanisms share the source-backed front axis",
        all(
            joint is not None and joint.axis == (0.0, -1.0, 0.0)
            for joint in (dial_joint, pointer_joint, winding_joint)
        ),
    )
    ctx.check(
        "face mechanisms follow the selected body's front-plane tilt",
        all(
            joint is not None and math.isclose(joint.origin.rpy[0], r.front_tilt, abs_tol=1.0e-9)
            for joint in (dial_joint, pointer_joint, winding_joint)
        ),
    )

    support_joint = joints.get(
        "support__folding_magnetic_stand__hinge"
        if r.support == "folding_magnetic_stand"
        else f"support__{r.support}__mount"
    )
    ctx.check(
        "support joint type matches candidate",
        support_joint is not None
        and support_joint.articulation_type
        == (
            ArticulationType.REVOLUTE
            if r.support == "folding_magnetic_stand"
            else ArticulationType.FIXED
        ),
    )

    lever_name = "alert_control__bell_silence_lever__control"
    lever_joint = joints.get("alert_control__bell_silence_lever__slide_joint")
    if r.alert_control == "bell_silence_lever":
        ctx.check("bell silence lever part exists", lever_name in parts)
        ctx.check(
            "bell silence lever has finite prismatic travel",
            lever_joint is not None
            and lever_joint.articulation_type == ArticulationType.PRISMATIC
            and lever_joint.motion_limits is not None
            and lever_joint.motion_limits.lower == 0.0
            and lever_joint.motion_limits.upper == r.lever_travel,
        )
    else:
        ctx.check(
            "baseline has no alert-control part", lever_name not in parts and lever_joint is None
        )

    ctx.check(
        "domain choices are recorded on the model",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "compact_geometry_limits",
        {"body_scale": 0.85, "dial_ratio": 0.65, "detail_scale": 0.82},
        reason="lower continuous geometry boundaries",
    ),
    corner_case(
        "large_geometry_limits",
        {"body_scale": 1.15, "dial_ratio": 0.79, "detail_scale": 1.18},
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
    "build_mechanical_timer_with_rotating_dial",
    "build_seeded_mechanical_timer_with_rotating_dial",
    "run_mechanical_timer_with_rotating_dial_tests",
]
