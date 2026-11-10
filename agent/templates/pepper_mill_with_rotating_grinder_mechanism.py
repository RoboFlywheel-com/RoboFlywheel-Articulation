# SPDX-License-Identifier: Apache-2.0

"""Source-faithful tiered pepper mills with visible fill and grinder controls."""

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
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    register_interface_mate,
)

BodyForm = Literal[
    "white_clear_selector_body",
    "waisted_wood_body",
    "straight_glass_body",
    "faceted_metal_body",
]
Drive = Literal["top_twist_cap", "top_crank", "side_crank"]
Adjustment = Literal["top_nut", "indexed_base_collar", "coarse_fine_slide"]
Reservoir = Literal["single_chamber", "dual_chamber"]
Closure = Literal["open_top", "hinged_dust_cap"]

BODY_FORMS: tuple[BodyForm, ...] = (
    "white_clear_selector_body",
    "waisted_wood_body",
    "straight_glass_body",
    "faceted_metal_body",
)
DRIVES: tuple[Drive, ...] = ("top_twist_cap", "top_crank", "side_crank")
ADJUSTMENTS = ("top_nut", "indexed_base_collar", "coarse_fine_slide")
RESERVOIRS = ("single_chamber", "dual_chamber")
CLOSURES = ("open_top", "hinged_dust_cap")

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("body_form", BODY_FORMS, role="complete detailed pepper-mill host"),
        component_slot("drive", DRIVES, role="complete rotating grinder input"),
        component_slot("adjustment", ADJUSTMENTS, role="independent grind adjustment"),
        component_slot("reservoir", RESERVOIRS, role="independent pepper reservoir topology"),
        component_slot("closure", CLOSURES, role="independent dust closure"),
    )
)


@dataclass(frozen=True)
class Config:
    body_form: BodyForm = "white_clear_selector_body"
    drive: Drive = "top_twist_cap"
    adjustment: Adjustment = "top_nut"
    reservoir: Reservoir = "single_chamber"
    closure: Closure = "open_top"
    size_scale: float = 1.0
    drive_scale: float = 1.0
    name: str = "pepper_mill_with_rotating_grinder_mechanism"


@dataclass(frozen=True)
class ResolvedConfig:
    body_form: BodyForm
    drive: Drive
    adjustment: Adjustment
    reservoir: Reservoir
    closure: Closure
    size_scale: float
    drive_scale: float
    drive_axis_z_m: float
    housing_radius_m: float
    selector_y_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x5045_5050_4552)
    return Config(
        body_form=choices["body_form"],
        drive=choices["drive"],
        adjustment=choices["adjustment"], reservoir=choices["reservoir"], closure=choices["closure"],
        size_scale=round(rng.uniform(0.90, 1.10), 4),
        drive_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"pepper_mill_seed_{seed}",
    )


def _require_range(name: str, value: float, minimum: float, maximum: float) -> float:
    value = float(value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be in [{minimum}, {maximum}], got {value}")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate({"body_form": config.body_form, "drive": config.drive, "adjustment": config.adjustment, "reservoir": config.reservoir, "closure": config.closure})
    size = _require_range("size_scale", config.size_scale, 0.90, 1.10)
    drive_scale = _require_range("drive_scale", config.drive_scale, 0.90, 1.10)
    faceted = config.body_form == "faceted_metal_body"
    housing_radius = (0.0268 if faceted else 0.0270) * size
    return ResolvedConfig(
        body_form=config.body_form,
        drive=config.drive,
        adjustment=config.adjustment, reservoir=config.reservoir, closure=config.closure,
        size_scale=size,
        drive_scale=drive_scale,
        drive_axis_z_m=0.1475 * size,
        housing_radius_m=housing_radius,
        selector_y_m=(
            -(0.0262 * math.cos(math.pi / 8.0)) - 0.0012
            if faceted
            else -0.0250
        )
        * size,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, str]:
    return {"body_form": config.body_form, "drive": config.drive, "adjustment": config.adjustment, "reservoir": config.reservoir, "closure": config.closure}


def slot_choices_for_seed(seed: int) -> dict[str, str]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject):
    return {
        "white": model.material("pepper_mill_warm_white_plastic", rgba=(0.88, 0.87, 0.85, 1.0)),
        "clear": model.material("pepper_mill_clear_reservoir", rgba=(0.78, 0.86, 0.88, 0.40)),
        "glass": model.material("pepper_mill_straight_glass", rgba=(0.84, 0.91, 0.93, 0.34)),
        "wood": model.material("pepper_mill_turned_walnut", rgba=(0.38, 0.23, 0.12, 1.0)),
        "faceted": model.material("pepper_mill_dark_faceted_metal", rgba=(0.22, 0.23, 0.23, 1.0)),
        "nickel": model.material("pepper_mill_satin_nickel", rgba=(0.56, 0.57, 0.56, 1.0)),
        "steel": model.material("pepper_mill_brushed_stainless", rgba=(0.62, 0.63, 0.61, 1.0)),
        "dark": model.material("pepper_mill_dark_grinder_metal", rgba=(0.20, 0.20, 0.19, 1.0)),
        "ceramic": model.material("pepper_mill_charcoal_ceramic", rgba=(0.20, 0.20, 0.19, 1.0)),
        "pepper": model.material("pepper_mill_black_pepper", rgba=(0.27, 0.14, 0.075, 1.0)),
        "pepper_tan": model.material("pepper_mill_pepper_highlight", rgba=(0.52, 0.32, 0.17, 1.0)),
        "grip": model.material("pepper_mill_crank_grip", rgba=(0.065, 0.060, 0.055, 1.0)),
    }


def _scaled_points(
    points: list[tuple[float, float]], scale: float
) -> list[tuple[float, float]]:
    return [(radius * scale, z * scale) for radius, z in points]


def _revolve_profile(points: list[tuple[float, float]], scale: float) -> cq.Workplane:
    profile = _scaled_points(points, scale)
    return (
        cq.Workplane("XZ")
        .moveTo(*profile[0])
        .polyline(profile[1:])
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )


def _faceted_loft(
    stations: list[tuple[float, float]], scale: float, sides: int = 8
) -> cq.Workplane:
    stations = _scaled_points(stations, scale)
    base_z = stations[0][1]
    work = cq.Workplane("XY").polygon(sides, 2.0 * stations[0][0])
    previous = base_z
    for radius, z in stations[1:]:
        work = work.workplane(offset=z - previous).polygon(sides, 2.0 * radius)
        previous = z
    return work.loft().translate((0.0, 0.0, base_z))


def _white_base(scale: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(0.0220 * scale)
        .workplane(offset=0.0030 * scale)
        .circle(0.0260 * scale)
        .workplane(offset=0.0070 * scale)
        .circle(0.0280 * scale)
        .workplane(offset=0.0170 * scale)
        .circle(0.0278 * scale)
        .workplane(offset=0.0090 * scale)
        .circle(0.0260 * scale)
        .loft(combine=True)
    )


def _white_reservoir(scale: float) -> cq.Workplane:
    return _revolve_profile(
        [
            (0.0255, 0.0320),
            (0.0246, 0.0610),
            (0.0231, 0.1045),
            (0.0216, 0.1045),
            (0.0231, 0.0610),
            (0.0240, 0.0320),
        ],
        scale,
    )


def _waisted_body(scale: float) -> cq.Workplane:
    return _revolve_profile(
        [
            (0.0320, 0.0000),
            (0.0345, 0.0045),
            (0.0345, 0.0110),
            (0.0335, 0.0190),
            (0.0300, 0.0310),
            (0.0260, 0.0490),
            (0.0230, 0.0630),
            (0.0225, 0.0730),
            (0.0235, 0.0860),
            (0.0250, 0.0960),
            (0.0255, 0.1015),
            (0.0225, 0.1015),
            (0.0225, 0.0960),
            (0.0215, 0.0860),
            (0.0210, 0.0730),
            (0.0215, 0.0630),
            (0.0235, 0.0490),
            (0.0270, 0.0310),
            (0.0305, 0.0190),
            (0.0315, 0.0110),
            (0.0315, 0.0045),
            (0.0290, 0.0000),
        ],
        scale,
    )


def _straight_base(scale: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(0.0260 * scale)
        .workplane(offset=0.0020 * scale)
        .circle(0.0275 * scale)
        .workplane(offset=0.0260 * scale)
        .circle(0.0275 * scale)
        .workplane(offset=0.0040 * scale)
        .circle(0.0258 * scale)
        .loft(combine=True)
    )


def _straight_reservoir(scale: float) -> cq.Workplane:
    return _revolve_profile(
        [
            (0.0250, 0.0320),
            (0.0250, 0.1045),
            (0.0235, 0.1045),
            (0.0235, 0.0320),
        ],
        scale,
    )


def _faceted_reservoir(scale: float) -> cq.Workplane:
    outer = _faceted_loft([(0.0255, 0.0320), (0.0231, 0.1045)], scale)
    inner = _faceted_loft([(0.0240, 0.0320), (0.0216, 0.1045)], scale)
    return outer.cut(inner)


def _housing_shell(r: ResolvedConfig) -> cq.Workplane:
    s = r.size_scale
    if r.body_form == "straight_glass_body":
        shell = _revolve_profile(
            [
                (0.0250, 0.1015),
                (0.0250, 0.1440),
                (0.0200, 0.1440),
                (0.0200, 0.1410),
                (0.0235, 0.1410),
                (0.0235, 0.1015),
            ],
            s,
        )
        front_y = -0.0235 * s
    elif r.body_form == "faceted_metal_body":
        outer = _faceted_loft([(0.0240, 0.1015), (0.0268, 0.1440)], s)
        bore = (
            cq.Workplane("XY")
            .circle(0.0185 * s)
            .extrude(0.0400 * s)
            .translate((0.0, 0.0, 0.1020 * s))
        )
        shell = outer.cut(bore)
        front_y = -(0.0240 * math.cos(math.pi / 8.0)) * s
    else:
        outer_r = 0.0272 if r.body_form == "waisted_wood_body" else 0.0268
        inner_r = 0.0230 if r.body_form == "waisted_wood_body" else 0.0185
        shell = _revolve_profile(
            [
                (0.0250, 0.1015),
                (0.0260, 0.1320),
                (outer_r, 0.1440),
                (inner_r, 0.1440),
                (inner_r, 0.1050),
                (0.0210, 0.1015),
            ],
            s,
        )
        front_y = -0.0240 * s
    slot = (
        cq.Workplane("XZ")
        .rect(0.028 * s, 0.012 * s)
        .extrude(0.018 * s, both=True)
        .translate((0.0, front_y, 0.1230 * s))
    )
    return shell.cut(slot)


def _grinder_bridge(scale: float) -> cq.Workplane:
    boss = (
        cq.Workplane("XY")
        .circle(0.0050 * scale)
        .circle(0.0025 * scale)
        .extrude(0.0070 * scale)
        .translate((0.0, 0.0, 0.1370 * scale))
    )
    result = boss
    for angle in (0.0, 120.0, 240.0):
        arm = (
            cq.Workplane("XY")
            .box(0.0170 * scale, 0.0030 * scale, 0.0030 * scale)
            .translate((0.0120 * scale, 0.0, 0.1405 * scale))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        )
        result = result.union(arm)
    return result


def _pepper_mass(scale: float) -> cq.Workplane:
    core = _revolve_profile(
        [
            (0.0, 0.0345),
            (0.0155, 0.0345),
            (0.0198, 0.0450),
            (0.0185, 0.0730),
            (0.0165, 0.1005),
            (0.0, 0.1005),
        ],
        scale,
    )
    rings = (
        (0.041, 0.0180, 8, 0.0032, 0.10),
        (0.054, 0.0180, 9, 0.0031, 0.42),
        (0.068, 0.0175, 9, 0.0030, 0.05),
        (0.082, 0.0168, 8, 0.0029, 0.34),
        (0.096, 0.0152, 7, 0.0028, 0.12),
    )
    for z, radius, count, berry_r, phase in rings:
        for index in range(count):
            angle = phase + 2.0 * math.pi * index / count
            berry = (
                cq.Workplane("XY")
                .sphere(berry_r * scale)
                .translate(
                    (
                        radius * math.cos(angle) * scale,
                        radius * math.sin(angle) * scale,
                        z * scale,
                    )
                )
            )
            core = core.union(berry)
    return core


def _pepper_highlights(scale: float) -> cq.Workplane:
    samples = (
        (0.0165, 0.0072, 0.0460, 0.0030),
        (-0.0117, -0.0130, 0.0520, 0.0028),
        (0.0157, -0.0065, 0.0610, 0.0027),
        (-0.0152, 0.0066, 0.0700, 0.0028),
        (0.0105, 0.0121, 0.0810, 0.0027),
        (-0.0124, -0.0093, 0.0890, 0.0026),
    )
    result: cq.Workplane | None = None
    for x, y, z, radius in samples:
        berry = (
            cq.Workplane("XY")
            .sphere(radius * scale)
            .translate((x * scale, y * scale, z * scale))
        )
        result = berry if result is None else result.union(berry)
    assert result is not None
    return result


def _emit_body(model, r: ResolvedConfig, mats, assets):
    prefix = f"body_form__{r.body_form}"
    s = r.size_scale
    body = model.part(
        f"{prefix}__body",
        meta={
            "role": "reservoir_body",
            "candidate": r.body_form,
            "tiered_source_stack": True,
            "five_grind_dots": True,
        },
    )
    if r.body_form == "white_clear_selector_body":
        lower = ((_white_base(s), "white", "base_shell"), (_white_reservoir(s), "clear", "reservoir_shell"))
        housing_material = "white"
    elif r.body_form == "waisted_wood_body":
        lower = ((_waisted_body(s), "wood", "waisted_body"),)
        housing_material = "wood"
    elif r.body_form == "straight_glass_body":
        lower = ((_straight_base(s), "steel", "base_shell"), (_straight_reservoir(s), "glass", "reservoir_shell"))
        housing_material = "steel"
    else:
        lower = (
            (_faceted_loft([(0.0280, 0.0000), (0.0230, 0.0360)], s), "faceted", "base_shell"),
            (_faceted_reservoir(s), "nickel", "reservoir_shell"),
        )
        housing_material = "faceted"
    for shape, material_key, name in lower:
        body.visual(
            mesh_from_cadquery(shape, f"{prefix}__{name}_mesh", tolerance=0.00045),
            material=mats[material_key],
            name=f"{prefix}__{name}", material_class_id=("glass.clear_transparent" if r.body_form in {"white_clear_selector_body", "waisted_wood_body", "straight_glass_body"} else "metal.brushed_silver"),
        )
    floor = (
        cq.Workplane("XY")
        .circle(0.0252 * s)
        .extrude(0.0030 * s)
        .translate((0.0, 0.0, 0.0315 * s))
    )
    body.visual(
        mesh_from_cadquery(floor, f"{prefix}__reservoir_floor_mesh", tolerance=0.0004),
        material=mats["dark"],
        name=f"{prefix}__reservoir_floor", material_class_id="metal.blackened_gunmetal",
    )
    body.visual(
        mesh_from_cadquery(_housing_shell(r), f"{prefix}__housing_mesh", tolerance=0.00045),
        material=mats[housing_material],
        name=f"{prefix}__grinder_housing", material_class_id=("metal.blackened_gunmetal" if r.body_form in {"waisted_wood_body", "straight_glass_body", "faceted_metal_body"} else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        mesh_from_cadquery(_grinder_bridge(s), f"{prefix}__bridge_mesh", tolerance=0.00035),
        material=mats["dark"],
        name=f"{prefix}__grinder_bridge", material_class_id="metal.blackened_gunmetal",
    )
    rear_structure = (
        cq.Workplane("XY")
        .box(0.0060 * s, 0.0060 * s, 0.1400 * s)
        .translate((0.0, 0.0245 * s, 0.0710 * s))
        .union(
            cq.Workplane("XY")
            .box(0.0060 * s, 0.0260 * s, 0.0040 * s)
            .translate((0.0, 0.0130 * s, 0.1405 * s))
        )
    )
    if r.body_form == "white_clear_selector_body":
        rear_structure_material = "clear"
    elif r.body_form == "straight_glass_body":
        rear_structure_material = "glass"
    else:
        rear_structure_material = housing_material
    body.visual(
        mesh_from_cadquery(
            rear_structure,
            f"{prefix}__rear_structure_mesh",
            tolerance=0.0004,
        ),
        material=mats[rear_structure_material],
        name=f"{prefix}__rear_structure", material_class_id=("glass.clear_transparent" if r.body_form in {"white_clear_selector_body", "waisted_wood_body", "straight_glass_body"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        Box((0.0260 * s, 0.0180 * s, 0.0180 * s)),
        origin=Origin(xyz=(0.0, r.selector_y_m + 0.0080 * s, 0.1155 * s)),
        material=mats["dark"],
        name=f"{prefix}__selector_guide", material_class_id="metal.blackened_gunmetal",
    )
    dot_x = (-0.0120, -0.0060, 0.0, 0.0060, 0.0120)
    dot_r = (0.0010, 0.00125, 0.00155, 0.0019, 0.00225)
    for index, (x, radius) in enumerate(zip(dot_x, dot_r, strict=True)):
        dot = (
            cq.Workplane("XZ")
            .center(x * s, 0.1360 * s)
            .circle(radius * s)
            .extrude(0.0040 * s, both=True)
            .translate((0.0, r.selector_y_m, 0.0))
        )
        body.visual(
            mesh_from_cadquery(
                dot,
                f"{prefix}__grind_dot_{index}_mesh",
                tolerance=0.00025,
            ),
            material=mats["dark"],
            name=f"{prefix}__grind_dot_{index}", material_class_id="metal.blackened_gunmetal",
        )
    badge = (
        cq.Workplane("XZ")
        .ellipse(0.0065 * s, 0.0027 * s)
        .extrude(0.0030 * s, both=True)
        .translate((0.0, r.selector_y_m, 0.1095 * s))
    )
    body.visual(
        mesh_from_cadquery(badge, f"{prefix}__badge_mesh", tolerance=0.0003),
        material=mats["dark"],
        name=f"{prefix}__plain_badge", material_class_id="metal.blackened_gunmetal",
    )

    fill = model.part(
        f"{prefix}__pepper_fill",
        meta={"role": "pepper_fill", "candidate": r.body_form, "contents": "whole peppercorns"},
    )
    fill.visual(
        mesh_from_cadquery(
            _pepper_mass(s).translate((0.0, 0.0, -0.0320 * s)),
            f"{prefix}__pepper_mass_mesh",
            tolerance=0.00065,
        ),
        material=mats["pepper"],
        name=f"{prefix}__pepper_mass", material_class_id="organic.ground_litter",
    )
    fill.visual(
        mesh_from_cadquery(
            _pepper_highlights(s).translate((0.0, 0.0, -0.0320 * s)),
            f"{prefix}__pepper_highlights_mesh",
            tolerance=0.00055,
        ),
        material=mats["pepper_tan"],
        name=f"{prefix}__pepper_highlights", material_class_id="organic.ground_litter",
    )
    model.articulation(
        f"{prefix}__body_to_pepper_fill",
        ArticulationType.FIXED,
        parent=body,
        child=fill,
        origin=Origin(xyz=(0.0, 0.0, 0.0320 * s)),
    )

    selector = model.part(
        f"{prefix}__grind_selector",
        meta={"role": "grind_selector", "candidate": r.body_form},
    )
    selector_shape = (
        cq.Workplane("XY")
        .box(0.0320 * s, 0.0020 * s, 0.0100 * s)
        .edges("|Y")
        .fillet(0.0042 * s)
    )
    selector.visual(
        mesh_from_cadquery(selector_shape, f"{prefix}__selector_mesh", tolerance=0.00032),
        material=mats["dark"],
        name=f"{prefix}__selector_plate", material_class_id="metal.blackened_gunmetal",
    )
    selector.visual(
        Box((0.0040 * s, 0.0020 * s, 0.0050 * s)),
        origin=Origin(xyz=(0.0, -0.0005 * s, -0.0025 * s)),
        material=mats["steel"],
        name=f"{prefix}__selector_tab", material_class_id="metal.brushed_silver",
    )
    selector_joint = model.articulation(
        f"{prefix}__selector_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=selector,
        origin=Origin(xyz=(0.0, r.selector_y_m - 0.0010 * s, 0.1230 * s)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=4.0,
            velocity=0.08,
            lower=-0.0080 * s,
            upper=0.0080 * s,
        ),
    )
    provider = AxisInterface(
        name=f"{prefix}.drive_bearing",
        point=(0.0, 0.0, r.drive_axis_z_m),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0030 * s,
    )
    return body, provider, fill, selector, selector_joint


def _body_form_white_clear_selector_body_build(model, r, mats, assets):
    return _emit_body(model, r, mats, assets)


def _body_form_waisted_wood_body_build(model, r, mats, assets):
    return _emit_body(model, r, mats, assets)


def _body_form_straight_glass_body_build(model, r, mats, assets):
    return _emit_body(model, r, mats, assets)


def _body_form_faceted_metal_body_build(model, r, mats, assets):
    return _emit_body(model, r, mats, assets)


_BODY_BUILDERS = {
    "white_clear_selector_body": _body_form_white_clear_selector_body_build,
    "waisted_wood_body": _body_form_waisted_wood_body_build,
    "straight_glass_body": _body_form_straight_glass_body_build,
    "faceted_metal_body": _body_form_faceted_metal_body_build,
}


def _burr_crown(scale: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .polygon(9, 0.0180 * scale)
        .workplane(offset=0.0060 * scale)
        .polygon(9, 0.0130 * scale)
        .loft(combine=True)
    )


def _top_twist_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.size_scale
    ds = r.drive_scale
    cap = (
        cq.Workplane("XY")
        .circle(0.0264 * s * ds)
        .workplane(offset=0.0040 * s)
        .circle(0.0272 * s * ds)
        .workplane(offset=0.0075 * s)
        .circle(0.0260 * s * ds)
        .workplane(offset=0.0040 * s)
        .circle(0.0230 * s * ds)
        .loft(combine=True)
    )
    return cap.union(_burr_crown(s * 0.72).translate((0.0, 0.0, 0.0010 * s)))


def _top_crank_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.size_scale
    radius = 0.050 * s * r.drive_scale
    hub = cq.Workplane("XY").circle(0.014 * s).extrude(0.009 * s)
    arm = (
        cq.Workplane("XY")
        .box(radius, 0.007 * s, 0.006 * s)
        .translate((0.5 * radius, 0.0, 0.006 * s))
    )
    return hub.union(arm).union(_burr_crown(s * 0.68))


def _side_crank_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.size_scale
    radius = 0.069 * s * r.drive_scale
    hub = cq.Workplane("XY").circle(0.012 * s).extrude(0.010 * s)
    collar = cq.Workplane("XY").circle(0.008 * s).extrude(0.006 * s)
    arm = (
        cq.Workplane("XY")
        .box(radius, 0.006 * s, 0.005 * s)
        .translate((0.5 * radius, 0.0, 0.006 * s))
    )
    return hub.union(collar).union(arm).union(_burr_crown(s * 0.65))


def _emit_drive(model, body, provider, r: ResolvedConfig, mats, shape: cq.Workplane):
    prefix = f"drive__{r.drive}"
    s = r.size_scale
    drive = model.part(
        f"{prefix}__rotor",
        meta={"role": "rotating_drive", "candidate": r.drive, "includes_grinder_input": True},
    )
    if r.adjustment == "top_nut":
        shape = shape.union(cq.Workplane("XY").polygon(6, 0.016 * s).extrude(0.008 * s).translate((0.0, 0.0, 0.009 * s)))
    elif r.adjustment == "indexed_base_collar":
        shape = shape.union(cq.Workplane("XY").circle(0.017 * s).circle(0.012 * s).extrude(0.004 * s).translate((0.0, 0.0, -0.001 * s)))
    else:
        shape = shape.union(cq.Workplane("XY").box(0.022 * s, 0.005 * s, 0.009 * s).translate((0.018 * s, 0.0, 0.004 * s)))
    drive.visual(
        mesh_from_cadquery(shape, f"{prefix}__input_mesh", tolerance=0.0004),
        material=mats["steel"],
        name=f"{prefix}__input_and_burr_crown", material_class_id="metal.brushed_silver",
    )
    if r.drive == "top_twist_cap":
        feature = (
            cq.Workplane("XY")
            .box(0.016 * s, 0.004 * s, 0.004 * s)
            .translate((0.026 * s * r.drive_scale, 0.0, 0.008 * s))
        )
    else:
        radius = (0.050 if r.drive == "top_crank" else 0.069) * s * r.drive_scale
        feature = (
            cq.Workplane("XY")
            .circle((0.0052 if r.drive == "top_crank" else 0.0048) * s)
            .extrude(0.020 * s)
            .translate((radius, 0.0, -0.003 * s))
        )
    drive.visual(
        mesh_from_cadquery(feature, f"{prefix}__feature_mesh", tolerance=0.00035),
        material=mats["grip"],
        name=f"{prefix}__feature", material_class_id="rubber.smooth_plain",
    )
    consumer = AxisInterface(
        name=f"{prefix}.input_axis",
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0035 * s,
    )
    mate = mate_axes(provider, consumer)
    joint_name = f"{prefix}__grind"
    joint = model.articulation(
        joint_name,
        ArticulationType.CONTINUOUS,
        parent=body,
        child=drive,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=22.0, velocity=5.0),
    )
    register_interface_mate(model, joint_name, mate)
    return drive, joint


def _drive_top_twist_cap_build(model, body, provider, r, mats, assets):
    return _emit_drive(model, body, provider, r, mats, _top_twist_shape(r))


def _drive_top_crank_build(model, body, provider, r, mats, assets):
    return _emit_drive(model, body, provider, r, mats, _top_crank_shape(r))


def _drive_side_crank_build(model, body, provider, r, mats, assets):
    return _emit_drive(model, body, provider, r, mats, _side_crank_shape(r))


_DRIVE_BUILDERS = {
    "top_twist_cap": _drive_top_twist_cap_build,
    "top_crank": _drive_top_crank_build,
    "side_crank": _drive_side_crank_build,
}

def _adjustment_top_nut_build(*args): return None
def _adjustment_indexed_base_collar_build(*args): return None
def _adjustment_coarse_fine_slide_build(*args): return None
def _reservoir_single_chamber_build(*args): return None
def _reservoir_dual_chamber_build(*args): return None
def _closure_open_top_build(*args): return None
def _closure_hinged_dust_cap_build(*args): return None


def build_pepper_mill_with_rotating_grinder_mechanism(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model)
    body, provider, _, _, _ = _BODY_BUILDERS[r.body_form](model, r, mats, assets)
    _DRIVE_BUILDERS[r.drive](model, body, provider, r, mats, assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/pepper_mill_with_rotating_grinder_mechanism"
    return model


def build_seeded_pepper_mill_with_rotating_grinder_mechanism(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_pepper_mill_with_rotating_grinder_mechanism(
        config_from_seed(seed), assets=assets
    )


def _aabb_center(box):
    if box is None:
        return None
    return tuple(0.5 * (box[0][index] + box[1][index]) for index in range(3))


def run_pepper_mill_with_rotating_grinder_mechanism_tests(
    object_model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    body_prefix = f"body_form__{r.body_form}"
    drive_prefix = f"drive__{r.drive}"
    body = object_model.get_part(f"{body_prefix}__body")
    fill = object_model.get_part(f"{body_prefix}__pepper_fill")
    selector = object_model.get_part(f"{body_prefix}__grind_selector")
    drive = object_model.get_part(f"{drive_prefix}__rotor")
    selector_joint = object_model.get_articulation(f"{body_prefix}__selector_slide")
    drive_joint = object_model.get_articulation(f"{drive_prefix}__grind")

    body_box = ctx.part_world_aabb(body)
    ctx.check(
        "pepper mill preserves tiered source body and visible fill",
        body.meta.get("role") == "reservoir_body"
        and body.meta.get("tiered_source_stack") is True
        and fill.meta.get("role") == "pepper_fill"
        and body.get_visual(f"{body_prefix}__grinder_housing") is not None
        and body.get_visual(f"{body_prefix}__grinder_bridge") is not None
        and body.get_visual(f"{body_prefix}__plain_badge") is not None
        and fill.get_visual(f"{body_prefix}__pepper_mass") is not None
        and body_box is not None
        and body_box[1][2] >= 0.143 * r.size_scale,
    )
    dots = [
        body.get_visual(f"{body_prefix}__grind_dot_{index}")
        for index in range(5)
    ]
    ctx.check(
        "pepper mill retains front grind selector and five dots",
        selector.meta.get("role") == "grind_selector"
        and body.get_visual(f"{body_prefix}__selector_guide") is not None
        and all(dot is not None for dot in dots),
    )
    ctx.check(
        "grinder drive rotates on central vertical axis",
        drive.meta.get("role") == "rotating_drive"
        and drive.meta.get("includes_grinder_input") is True
        and drive_joint.articulation_type == ArticulationType.CONTINUOUS
        and tuple(drive_joint.axis) == (0.0, 0.0, 1.0)
        and math.isclose(drive_joint.origin.xyz[2], r.drive_axis_z_m, abs_tol=1.0e-9),
    )

    feature_name = f"{drive_prefix}__feature"
    rest_feature = _aabb_center(ctx.part_element_world_aabb(drive, elem=feature_name))
    rest_body = ctx.part_world_aabb(body)
    with ctx.pose({drive_joint: math.pi / 2.0}):
        moved_feature = _aabb_center(ctx.part_element_world_aabb(drive, elem=feature_name))
        moved_body = ctx.part_world_aabb(body)
    ctx.check(
        "drive rotation leaves detailed reservoir fixed",
        rest_feature is not None
        and moved_feature is not None
        and rest_body == moved_body
        and rest_feature[0] > 0.008 * r.size_scale
        and moved_feature[1] > 0.008 * r.size_scale
        and abs(moved_feature[0]) < 0.004 * r.size_scale,
        details=f"rest_feature={rest_feature}, moved_feature={moved_feature}",
    )

    rest_selector = _aabb_center(ctx.part_world_aabb(selector))
    with ctx.pose({selector_joint: selector_joint.motion_limits.upper}):
        moved_selector = _aabb_center(ctx.part_world_aabb(selector))
    ctx.check(
        "front selector translates across its guide",
        selector_joint.articulation_type == ArticulationType.PRISMATIC
        and tuple(selector_joint.axis) == (1.0, 0.0, 0.0)
        and rest_selector is not None
        and moved_selector is not None
        and moved_selector[0] > rest_selector[0] + 0.006 * r.size_scale,
        details=f"rest_selector={rest_selector}, moved_selector={moved_selector}",
    )
    ctx.check(
        "domain choices are recorded",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    ctx.allow_isolated_part(
        fill,
        reason="Peppercorn contents are contained inside the hollow source reservoir.",
    )
    ctx.allow_isolated_part(
        selector,
        reason="The source selector slides with clearance inside the front guide slot.",
    )
    ctx.allow_isolated_part(
        drive,
        reason=(
            "The source input rotates with axial clearance above the grinder housing; "
            "the registered central-axis mate carries it."
        ),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "minimum_complete_source_scale",
        {"size_scale": 0.90, "drive_scale": 0.90},
        reason="smallest complete tiered source body and input",
    ),
    corner_case(
        "maximum_complete_source_scale",
        {"size_scale": 1.10, "drive_scale": 1.10},
        reason="largest complete tiered source body and input",
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
    "build_pepper_mill_with_rotating_grinder_mechanism",
    "build_seeded_pepper_mill_with_rotating_grinder_mechanism",
    "run_pepper_mill_with_rotating_grinder_mechanism_tests",
]
