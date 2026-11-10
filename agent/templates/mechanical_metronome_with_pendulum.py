# SPDX-License-Identifier: Apache-2.0

"""Source-backed mechanical metronomes with a visible escapement pendulum."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
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
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

CaseForm = Literal["pyramid_case", "rectangular_case", "arched_case"]
FrontClosure = Literal["open_scale", "hinged_cover"]
TempoModule = Literal["plain_slider", "bell_beat_slider"]
WindingSystem = Literal["fixed_side_key", "folding_side_key"]
CarryHandle = Literal["no_handle", "swing_handle"]
BaseSupport = Literal["flat_plinth", "leveling_feet"]

_PENDULUM_ROD_RADIUS_M = 0.0018
_SLIDER_BORE_CLEARANCE_M = 0.0003
_PENDULUM_ROD_OUTWARD_OFFSET_M = -0.0025
# Uniform mechanical clearances (tolerance constants, valid across every sampled
# config); mating positions are derived from these plus the resolved dimensions.
_PIVOT_BEARING_BORE_RADIUS_M = 0.0035
_PIVOT_AXLE_RADIAL_CLEARANCE_M = 0.0007
_PIVOT_AXLE_RADIUS_M = _PIVOT_BEARING_BORE_RADIUS_M - _PIVOT_AXLE_RADIAL_CLEARANCE_M
_KEY_SHAFT_RADIUS_M = 0.0032
_ROSETTE_BORE_CLEARANCE_M = 0.0003
_WINDING_ROSETTE_BORE_RADIUS_M = _KEY_SHAFT_RADIUS_M + _ROSETTE_BORE_CLEARANCE_M
_WINDING_ROSETTE_OUTER_RADIUS_M = 0.010
_WINDING_ROSETTE_LENGTH_M = 0.012
_KEY_BOW_X_M = 0.024
_KEY_JOINT_STANDOFF_M = 0.008  # winding joint axis stands this far off the wall face
_HINGE_PIN_RADIUS_M = 0.004
_HINGE_TUBE_RADIAL_CLEARANCE_M = 0.0005
_HINGE_TUBE_BORE_RADIUS_M = _HINGE_PIN_RADIUS_M + _HINGE_TUBE_RADIAL_CLEARANCE_M
_HINGE_TUBE_WALL_M = 0.0025
_HINGE_TUBE_OUTER_RADIUS_M = _HINGE_TUBE_BORE_RADIUS_M + _HINGE_TUBE_WALL_M
_SCALE_PANEL_LOWER_OFFSET_M = 0.018
_CASE_FRONT_OUTSET_M = 0.010  # front_y_m sits this far in front of the shell face
_PIVOT_STANDOFF_M = 0.004  # pivot axis stands this far in front of front_y_m
_BEARING_DEPTH_M = 0.008
_BEARING_FRONT_INSET_M = 0.002  # bearing front face sits this far behind the shell face
_AXLE_BORE_ENGAGEMENT_M = 0.001  # axle reaches this far into the bearing bore

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot(
            "case_form",
            ("pyramid_case", "rectangular_case", "arched_case"),
        ),
        component_slot("front_closure", ("open_scale", "hinged_cover")),
        component_slot("tempo_module", ("plain_slider", "bell_beat_slider")),
        component_slot("winding_system", ("fixed_side_key", "folding_side_key")),
        component_slot("carry_handle", ("no_handle", "swing_handle")),
        component_slot("base_support", ("flat_plinth", "leveling_feet")),
        multiplicity_slot(
            "tempo_weight_count",
            (1, 2),
            item_slot="tempo_module",
        ),
    )
)


@dataclass(frozen=True)
class Config:
    case_form: CaseForm = "pyramid_case"
    front_closure: FrontClosure = "open_scale"
    tempo_module: TempoModule = "plain_slider"
    winding_system: WindingSystem = "fixed_side_key"
    carry_handle: CarryHandle = "no_handle"
    base_support: BaseSupport = "flat_plinth"
    tempo_weight_count: int = 1
    pendulum_length_m: float | None = None
    swing_limit_rad: float | None = None
    name: str = "mechanical_metronome_with_pendulum"


@dataclass(frozen=True)
class ResolvedConfig:
    case_form: CaseForm
    front_closure: FrontClosure
    tempo_module: TempoModule
    winding_system: WindingSystem
    carry_handle: CarryHandle
    base_support: BaseSupport
    tempo_weight_count: int
    pendulum_length_m: float
    swing_limit_rad: float
    case_width_m: float
    case_depth_m: float
    case_height_m: float
    pivot_height_m: float
    front_y_m: float
    slider_travel_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x4D37)
    return Config(
        case_form=choices["case_form"],
        front_closure=choices["front_closure"],
        tempo_module=choices["tempo_module"],
        winding_system=choices["winding_system"],
        carry_handle=choices["carry_handle"],
        base_support=choices["base_support"],
        tempo_weight_count=choices["tempo_weight_count"],
        pendulum_length_m=round(rng.uniform(0.26, 0.36), 4),
        swing_limit_rad=round(rng.uniform(0.28, 0.50), 4),
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "case_form": config.case_form,
            "front_closure": config.front_closure,
            "tempo_module": config.tempo_module,
            "winding_system": config.winding_system,
            "carry_handle": config.carry_handle,
            "base_support": config.base_support,
            "tempo_weight_count": config.tempo_weight_count,
        }
    )
    length = 0.315 if config.pendulum_length_m is None else float(config.pendulum_length_m)
    swing = 0.39 if config.swing_limit_rad is None else float(config.swing_limit_rad)
    if not 0.26 <= length <= 0.36:
        raise ValueError("pendulum_length_m must be in [0.26, 0.36]")
    if not 0.28 <= swing <= 0.50:
        raise ValueError("swing_limit_rad must be in [0.28, 0.50]")
    height = length + 0.087
    width = 0.138 + 0.14 * (length - 0.26)
    depth = 0.088 + 0.08 * (length - 0.26)
    pivot_height = 0.41 * height
    return ResolvedConfig(
        case_form=config.case_form,
        front_closure=config.front_closure,
        tempo_module=config.tempo_module,
        winding_system=config.winding_system,
        carry_handle=config.carry_handle,
        base_support=config.base_support,
        tempo_weight_count=config.tempo_weight_count,
        pendulum_length_m=length,
        swing_limit_rad=swing,
        case_width_m=width,
        case_depth_m=depth,
        case_height_m=height,
        pivot_height_m=pivot_height,
        front_y_m=-0.5 * depth - 0.010,
        slider_travel_m=0.16 * length,
        name=config.name,
    )


def _materials(model: ArticulatedObject) -> dict[str, str]:
    return {
        "wood": model.material("dark_walnut", rgba=(0.27, 0.075, 0.045, 1.0)),
        "wood_edge": model.material(
            "walnut_edge_highlight", rgba=(0.48, 0.20, 0.095, 1.0)
        ),
        "wood_shadow": model.material(
            "walnut_grain", rgba=(0.105, 0.025, 0.018, 1.0)
        ),
        "black": model.material("scale_black", rgba=(0.018, 0.022, 0.024, 1.0)),
        "scale": model.material(
            "scale_white", rgba=(0.84, 0.86, 0.82, 1.0)
        ),
        "silver": model.material(
            "pendulum_silver", rgba=(0.78, 0.80, 0.78, 1.0)
        ),
        "ivory": model.material(
            "tempo_weight_ivory", rgba=(0.90, 0.89, 0.82, 1.0)
        ),
        "nickel": model.material(
            "winding_key_nickel", rgba=(0.72, 0.73, 0.70, 1.0)
        ),
        "brass": model.material("aged_brass", rgba=(0.69, 0.53, 0.20, 1.0)),
        "glass": model.material(
            "smoked_cover_glass", rgba=(0.28, 0.34, 0.36, 0.30)
        ),
        "rubber": model.material(
            "foot_rubber", rgba=(0.025, 0.020, 0.018, 1.0)
        ),
    }


def _xz_prism(
    points: list[tuple[float, float]],
    depth: float,
    *,
    fillet: float = 0.0,
) -> cq.Workplane:
    solid = cq.Workplane("XZ").polyline(points).close().extrude(depth / 2.0, both=True)
    if fillet > 0.0:
        try:
            solid = solid.edges().fillet(fillet)
        except Exception:
            pass
    return solid.clean()


def _ring_y(outer_radius: float, inner_radius: float, depth: float) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(depth / 2.0, both=True)
        .clean()
    )


def _ring_x(outer_radius: float, inner_radius: float, length: float) -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(length / 2.0, both=True)
        .clean()
    )


def _case_side_half_width_at(r: ResolvedConfig, z: float) -> float:
    """Half-width of the case silhouette (world x extent) at height ``z``."""

    half = 0.5 * r.case_width_m
    height = r.case_height_m
    if r.case_form == "arched_case":
        shoulder = 0.78 * height
        if z <= shoulder:
            return half
        fraction = min(1.0, max(0.0, (z - shoulder) / (height - shoulder)))
        return half * math.cos(math.asin(fraction))
    if r.case_form == "pyramid_case":
        crown_half = 0.21 * r.case_width_m
        stops = (
            (0.0, half),
            (0.24 * height, 0.92 * half),
            (0.61 * height, 0.70 * half),
            (0.97 * height, crown_half),
            (height, 0.72 * crown_half),
        )
        for (z0, w0), (z1, w1) in zip(stops, stops[1:]):
            if z <= z1:
                fraction = (z - z0) / (z1 - z0)
                return w0 + fraction * (w1 - w0)
        return stops[-1][1]
    return half


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent: object,
    child: object,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    articulation_type: ArticulationType,
    limits: MotionLimits,
) -> None:
    mate = mate_axes(
        AxisInterface(name=f"{name}_provider", point=point, axis=axis, radial=radial),
        AxisInterface(name=f"{name}_consumer", axis=axis, radial=radial),
    )
    model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
    )
    register_interface_mate(model, name, mate)


def _case_profile(r: ResolvedConfig) -> list[tuple[float, float]]:
    half = 0.5 * r.case_width_m
    if r.case_form == "rectangular_case":
        return [
            (-half, 0.0),
            (-half, r.case_height_m),
            (half, r.case_height_m),
            (half, 0.0),
        ]
    if r.case_form == "arched_case":
        shoulder = 0.78 * r.case_height_m
        points = [(-half, 0.0)]
        radius_x = half
        crown_height = r.case_height_m - shoulder
        for index in range(9):
            theta = math.pi - math.pi * index / 8.0
            points.append(
                (
                    radius_x * math.cos(theta),
                    shoulder + crown_height * math.sin(theta),
                )
            )
        points.append((half, 0.0))
        return points
    crown_half = 0.21 * r.case_width_m
    return [
        (-half, 0.0),
        (-0.92 * half, 0.24 * r.case_height_m),
        (-0.70 * half, 0.61 * r.case_height_m),
        (-crown_half, 0.97 * r.case_height_m),
        (-0.72 * crown_half, r.case_height_m),
        (0.72 * crown_half, r.case_height_m),
        (crown_half, 0.97 * r.case_height_m),
        (0.70 * half, 0.61 * r.case_height_m),
        (0.92 * half, 0.24 * r.case_height_m),
        (half, 0.0),
    ]


def _add_scale_details(
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> None:
    lower_z = r.pivot_height_m - _SCALE_PANEL_LOWER_OFFSET_M
    upper_z = r.case_height_m - 0.034
    lower_half = 0.255 * r.case_width_m
    upper_half = 0.18 * r.case_width_m
    scale_profile = [
        (-lower_half, lower_z),
        (-upper_half, upper_z),
        (upper_half, upper_z),
        (lower_half, lower_z),
    ]
    # Front-face decorations are embedded into the shell front by derived
    # offsets so no pair overlap remains (case front sits at front_y + outset).
    case_front_y = r.front_y_m + _CASE_FRONT_OUTSET_M
    panel_depth = 0.005
    panel_center_y = case_front_y + 0.001 - 0.5 * panel_depth
    tick_thickness = 0.0012
    tick_center_y = panel_center_y - 0.5 * panel_depth + 0.0005
    bearing_depth = _BEARING_DEPTH_M
    bearing_center_y = case_front_y + _BEARING_FRONT_INSET_M - 0.5 * bearing_depth
    badge_thickness = 0.002
    badge_center_y = case_front_y + 0.0005 - 0.5 * badge_thickness
    case.visual(
        mesh_from_cadquery(
            _xz_prism(scale_profile, panel_depth, fillet=0.0015).translate(
                (0.0, panel_center_y, 0.0)
            ),
            f"{r.case_form}_tempo_scale",
            assets=assets,
            tolerance=0.0005,
        ),
        material=mats["black"],
        name="tempo_scale_panel", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    tick_count = 15
    for index in range(tick_count):
        fraction = index / (tick_count - 1)
        z = lower_z + 0.030 + fraction * (upper_z - lower_z - 0.050)
        half_width = lower_half + (upper_half - lower_half) * fraction
        tick_length = 0.010 if index % 3 == 0 else 0.006
        for side in (-1.0, 1.0):
            case.visual(
                Box((tick_length, tick_thickness, 0.0010)),
                origin=Origin(
                    xyz=(
                        side * (half_width - 0.5 * tick_length - 0.004),
                        tick_center_y,
                        z,
                    )
                ),
                material=mats["scale"],
                name=f"tempo_tick_{index}_{0 if side < 0 else 1}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
    case.visual(
        mesh_from_cadquery(
            _ring_y(0.010, _PIVOT_BEARING_BORE_RADIUS_M, bearing_depth).translate(
                (0.0, bearing_center_y, r.pivot_height_m)
            ),
            f"{r.case_form}_pivot_bearing",
            assets=assets,
            tolerance=0.0004,
        ),
        material=mats["nickel"],
        name="pendulum_pivot_bearing", material_class_id="metal.brushed_silver",
    )
    case.visual(
        Box((0.026, badge_thickness, 0.007)),
        origin=Origin(
            xyz=(0.20 * r.case_width_m, badge_center_y, 0.075 * r.case_height_m)
        ),
        material=mats["brass"],
        name="maker_badge", material_class_id="metal.brass_aged",
    )


def _build_case(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> object:
    case = model.part(
        "case",
        meta={
            "role": "case_body",
            "case_form": r.case_form,
            "source_silhouette": True,
            "tempo_scale": "inset_tapered_scale",
        },
    )
    case.visual(
        mesh_from_cadquery(
            _xz_prism(_case_profile(r), r.case_depth_m, fillet=0.003),
            f"{r.case_form}_continuous_shell",
            assets=assets,
            tolerance=0.0008,
        ),
        material=mats["wood"],
        name=f"{r.case_form}_shell", material_class_id="wood.walnut_dark",
    )
    lower_cover_height = 0.41 * r.case_height_m
    case.visual(
        Box((0.88 * r.case_width_m, r.case_depth_m + 0.008, lower_cover_height)),
        origin=Origin(xyz=(0.0, -0.002, 0.5 * lower_cover_height)),
        material=mats["wood_edge"],
        name="lower_spring_cover", material_class_id="wood.walnut_dark",
    )
    # Grain inlays embed 1mm into the shell front face.
    inlay_thickness = 0.0015
    inlay_center_y = -0.5 * r.case_depth_m + 0.001 - 0.5 * inlay_thickness
    for index, x in enumerate(
        (-0.34 * r.case_width_m, -0.12 * r.case_width_m, 0.13 * r.case_width_m, 0.35 * r.case_width_m)
    ):
        case.visual(
            Box((inlay_thickness, inlay_thickness, 0.31 * r.case_height_m)),
            origin=Origin(
                xyz=(x, inlay_center_y, 0.18 * r.case_height_m)
            ),
            material=mats["wood_shadow"],
            name=f"wood_grain_inlay_{index}", material_class_id="wood.patterned_decorative",
        )
    _add_scale_details(case, r, mats, assets=assets)
    return case


def _case_form_pyramid_case_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> object:
    return _build_case(model, r, mats, assets=assets)


def _case_form_rectangular_case_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> object:
    return _build_case(model, r, mats, assets=assets)


def _case_form_arched_case_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> object:
    return _build_case(model, r, mats, assets=assets)


_CASE_BUILDERS = {
    "pyramid_case": _case_form_pyramid_case_build,
    "rectangular_case": _case_form_rectangular_case_build,
    "arched_case": _case_form_arched_case_build,
}


def _build_pendulum(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> object:
    pendulum = model.part(
        "pendulum",
        meta={
            "role": "pendulum",
            "visible_rod_length_m": r.pendulum_length_m,
            "escapement_axis": "horizontal_y",
        },
    )
    pendulum.visual(
        Cylinder(radius=_PENDULUM_ROD_RADIUS_M, length=r.pendulum_length_m),
        origin=Origin(
            xyz=(
                0.0,
                _PENDULUM_ROD_OUTWARD_OFFSET_M,
                0.5 * r.pendulum_length_m,
            )
        ),
        material=mats["silver"],
        name="spring_steel_pendulum_rod", material_class_id="metal.brushed_silver",
    )
    # Axle half-length reaches from the pivot axis into the bearing bore:
    # pivot->bearing-front separation plus a fixed engagement depth.
    bearing_front_rel = (
        _CASE_FRONT_OUTSET_M + _BEARING_FRONT_INSET_M - _BEARING_DEPTH_M
    )
    axle_length = 2.0 * (bearing_front_rel + _PIVOT_STANDOFF_M + _AXLE_BORE_ENGAGEMENT_M)
    pendulum.visual(
        Cylinder(radius=_PIVOT_AXLE_RADIUS_M, length=axle_length),
        origin=Origin(
            xyz=(0.0, 0.0, 0.0),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["nickel"],
        name="captured_pivot_axle", material_class_id="metal.brushed_silver",
    )
    _axis_joint(
        model,
        name="pendulum_swing",
        parent=case,
        child=pendulum,
        point=(0.0, r.front_y_m - _PIVOT_STANDOFF_M, r.pivot_height_m),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(
            effort=0.35,
            velocity=5.0,
            lower=-r.swing_limit_rad,
            upper=r.swing_limit_rad,
        ),
    )
    return pendulum


def _slider_bore_radius_m() -> float:
    return _PENDULUM_ROD_RADIUS_M + _SLIDER_BORE_CLEARANCE_M


def _slider_bore() -> cq.Workplane:
    return cq.Workplane("XY").center(
        0.0, _PENDULUM_ROD_OUTWARD_OFFSET_M
    ).circle(_slider_bore_radius_m())


def _plain_slider_shape() -> cq.Workplane:
    body = cq.Workplane("XY").box(0.027, 0.010, 0.024).edges("|Z").fillet(0.0025)
    for z in (-0.007, 0.0, 0.007):
        body = body.union(
            cq.Workplane("XY").box(0.029, 0.0115, 0.0028).translate((0.0, 0.0, z))
        )
    return body.cut(
        _slider_bore().extrude(0.030, both=True)
    ).clean()


def _bell_slider_shape() -> cq.Workplane:
    body = cq.Workplane("XY").box(0.034, 0.012, 0.026).edges("|Z").fillet(0.002)
    for index in range(5):
        body = body.union(
            cq.Workplane("XY")
            .box(0.004, 0.014, 0.003)
            .translate((-0.012 + index * 0.006, 0.0, 0.014))
        )
    return body.cut(
        _slider_bore().extrude(0.032, both=True)
    ).clean()


def _build_tempo_weights(
    model: ArticulatedObject,
    pendulum: object,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> None:
    shape = (
        _plain_slider_shape()
        if r.tempo_module == "plain_slider"
        else _bell_slider_shape()
    )
    for index in range(r.tempo_weight_count):
        start = (0.34 + 0.30 * index) * r.pendulum_length_m
        weight = model.part(
            f"tempo_weight_{index}",
            meta={
                "role": "tempo_weight",
                "tempo_module": r.tempo_module,
                "index": index,
                "captured_on_rod": True,
            },
        )
        weight.visual(
            mesh_from_cadquery(
                shape,
                f"{r.tempo_module}_weight_{index}",
                assets=assets,
                tolerance=0.0004,
            ),
            material=(
                mats["ivory"]
                if r.tempo_module == "plain_slider"
                else mats["brass"]
            ),
            name=f"{r.tempo_module}_body", material_class_id=("metal.brass_aged" if r.tempo_module == "bell_beat_slider" else "plastic.opaque_glossy_molded"),
        )
        if r.tempo_module == "bell_beat_slider":
            weight.visual(
                Cylinder(radius=0.005, length=0.012),
                origin=Origin(
                    xyz=(0.020, 0.0, 0.0),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=mats["black"],
                name="beat_selector_knob", material_class_id="metal.blackened_gunmetal",
            )
        model.articulation(
            f"tempo_weight_slide_{index}",
            ArticulationType.PRISMATIC,
            parent=pendulum,
            child=weight,
            origin=Origin(xyz=(0.0, 0.0, start)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=4.0,
                velocity=0.12,
                lower=-0.5 * r.slider_travel_m,
                upper=0.5 * r.slider_travel_m,
            ),
        )


def _front_closure_open_scale_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None = None,
) -> None:
    bezel = model.part("open_scale_bezel", meta={"role": "front_closure"})
    bezel_height = 0.012
    bezel.visual(
        Box((0.60 * r.case_width_m, 0.012, bezel_height)),
        material=mats["brass"],
        name="open_scale_lower_bezel", material_class_id="metal.brass_aged",
    )
    # Bezel top sits just below the scale panel bottom, in front of the lower
    # spring cover face it rests against (no overlap, contact supports it).
    panel_bottom_z = r.pivot_height_m - _SCALE_PANEL_LOWER_OFFSET_M
    bezel_gap_z = 0.0008
    model.articulation(
        "open_scale_bezel_mount",
        ArticulationType.FIXED,
        parent=case,
        child=bezel,
        origin=Origin(
            xyz=(0.0, r.front_y_m - 0.002, panel_bottom_z - bezel_gap_z - 0.5 * bezel_height)
        ),
    )


def _front_closure_hinged_cover_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None = None,
) -> None:
    cover = model.part("hinged_front_cover", meta={"role": "front_closure"})
    cover_height = 0.34 * r.case_height_m
    cover_width = 0.84 * r.case_width_m
    # The lower spring cover protrudes 6mm in front of the shell front; the
    # hinge axis sits one panel half-thickness ahead of that face so the
    # closed panel rests flush against it (contact, no overlap).
    lower_cover_front_y = -0.5 * r.case_depth_m - 0.006
    panel_thickness = 0.006
    hinge_y = lower_cover_front_y - 0.5 * panel_thickness
    hinge_z = 0.030
    knuckle_width_x = 0.016
    knuckle_outset = 0.013
    pin_end_cap = 0.002
    pin_length = cover_width + 2.0 * (
        knuckle_outset + 0.5 * knuckle_width_x + pin_end_cap
    )
    case.visual(
        Cylinder(radius=_HINGE_PIN_RADIUS_M, length=pin_length),
        origin=Origin(
            xyz=(0.0, hinge_y, hinge_z),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["brass"],
        name="front_cover_hinge_pin", material_class_id="metal.brass_aged",
    )
    knuckle_depth_y = 0.012
    knuckle_embed = 0.005
    knuckle_center_y = -0.5 * r.case_depth_m + 0.5 * knuckle_depth_y - knuckle_embed
    for side, x in enumerate(
        (-0.5 * cover_width - knuckle_outset, 0.5 * cover_width + knuckle_outset)
    ):
        case.visual(
            Box((knuckle_width_x, knuckle_depth_y, 0.018)),
            origin=Origin(xyz=(x, knuckle_center_y, hinge_z)),
            material=mats["brass"],
            name=f"front_cover_hinge_knuckle_{side}",
            material_class_id="metal.brass_aged",
        )
    cover.visual(
        mesh_from_cadquery(
            _ring_x(
                _HINGE_TUBE_OUTER_RADIUS_M, _HINGE_TUBE_BORE_RADIUS_M, cover_width
            ).translate((0.0, 0.0, 0.0)),
            "hinged_cover_hinge_tube",
            assets=assets,
            tolerance=0.0004,
        ),
        material=mats["brass"],
        name="cover_hinge_rail", material_class_id="metal.brass_aged",
    )
    cover.visual(
        Box((cover_width, panel_thickness, cover_height)),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * cover_height)),
        material=mats["glass"],
        name="smoked_cover_panel", material_class_id="glass.smoked_tinted",
    )
    for side, x in enumerate((-0.5 * cover_width, 0.5 * cover_width)):
        cover.visual(
            Box((0.010, 0.010, cover_height)),
            origin=Origin(xyz=(x, 0.0, 0.5 * cover_height)),
            material=mats["brass"],
            name=f"cover_side_rail_{side}", material_class_id="metal.brass_aged",
        )
    _axis_joint(
        model,
        name="front_cover_hinge",
        parent=case,
        child=cover,
        point=(0.0, hinge_y, hinge_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(
            effort=4.0,
            velocity=1.0,
            lower=0.0,
            upper=math.radians(105.0),
        ),
    )


_CLOSURE_BUILDERS = {
    "open_scale": _front_closure_open_scale_build,
    "hinged_cover": _front_closure_hinged_cover_build,
}


def _key_bow_shape() -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .circle(0.014)
        .circle(0.009)
        .extrude(0.0025, both=True)
        .translate((_KEY_BOW_X_M, 0.0, 0.0))
        .clean()
    )


def _key_mount_x(r: ResolvedConfig) -> float:
    return _case_side_half_width_at(r, 0.28 * r.case_height_m)


def _add_winding_rosette(
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> None:
    """Bored rosette embedded in the case side wall; the key shaft runs in its bore."""

    case.visual(
        mesh_from_cadquery(
            _ring_x(
                _WINDING_ROSETTE_OUTER_RADIUS_M,
                _WINDING_ROSETTE_BORE_RADIUS_M,
                _WINDING_ROSETTE_LENGTH_M,
            ).translate((_key_mount_x(r), 0.010, 0.28 * r.case_height_m)),
            f"{r.case_form}_winding_rosette",
            assets=assets,
            tolerance=0.0004,
        ),
        material=mats["nickel"],
        name="winding_key_rosette", material_class_id="metal.brushed_silver",
    )


def _winding_system_fixed_side_key_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None = None,
) -> None:
    _add_winding_rosette(case, r, mats, assets=assets)
    key = model.part(
        "winding_key",
        meta={"role": "winding_key", "winding_system": "fixed_side_key"},
    )
    # Shaft tip stands 0.5mm proud of the wall face; the rest runs in the
    # rosette bore (radial clearance) and reaches the bow plane.
    shaft_start = 0.0005 - _KEY_JOINT_STANDOFF_M
    shaft_length = _KEY_BOW_X_M - shaft_start
    key.visual(
        Cylinder(radius=_KEY_SHAFT_RADIUS_M, length=shaft_length),
        origin=Origin(
            xyz=(0.5 * (shaft_start + _KEY_BOW_X_M), 0.0, 0.0),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["nickel"],
        name="key_shaft", material_class_id="metal.brushed_silver",
    )
    key.visual(
        mesh_from_cadquery(
            _key_bow_shape(),
            "fixed_winding_key_bow",
            assets=assets,
            tolerance=0.0004,
        ),
        material=mats["nickel"],
        name="key_bow", material_class_id="metal.brushed_silver",
    )
    key.visual(
        Box((0.006, 0.006, 0.014)),
        origin=Origin(xyz=(_KEY_BOW_X_M, 0.0, 0.007)),
        material=mats["nickel"],
        name="key_bow_spoke", material_class_id="metal.brushed_silver",
    )
    _axis_joint(
        model,
        name="winding_key_turn",
        parent=case,
        child=key,
        point=(_key_mount_x(r) + _KEY_JOINT_STANDOFF_M, 0.010, 0.28 * r.case_height_m),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=1.2, velocity=6.0, lower=None, upper=None),
    )


def _winding_system_folding_side_key_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None = None,
) -> None:
    _add_winding_rosette(case, r, mats, assets=assets)
    hub = model.part(
        "winding_key",
        meta={"role": "winding_key", "winding_system": "folding_side_key"},
    )
    # Hub floats just proud of the rosette face; the tab hinge sits on the hub
    # barrel, offset so the leaf hangs and folds beside the hub. All offsets
    # derive from the rosette length, joint standoff and member sizes.
    rosette_face_local = 0.5 * _WINDING_ROSETTE_LENGTH_M - _KEY_JOINT_STANDOFF_M
    hub_start = rosette_face_local + 0.0005
    hub_length = 0.040
    hub_radius = 0.007
    hub.visual(
        Cylinder(radius=hub_radius, length=hub_length),
        origin=Origin(
            xyz=(hub_start + 0.5 * hub_length, 0.0, 0.0),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["nickel"],
        name="folding_key_hub", material_class_id="metal.brushed_silver",
    )
    _axis_joint(
        model,
        name="winding_key_turn",
        parent=case,
        child=hub,
        point=(_key_mount_x(r) + _KEY_JOINT_STANDOFF_M, 0.010, 0.28 * r.case_height_m),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=1.2, velocity=6.0, lower=None, upper=None),
    )
    tab = model.part("folding_key_tab", meta={"role": "key_tab"})
    leaf_thickness = 0.010
    leaf_length = 0.055
    leaf_top_gap = 0.001
    leaf_gap = 0.0008
    # Hinge knuckle sits on the hub barrel, offset in +y so the leaf hangs —
    # and folds at the joint limit — beside the hub with uniform clearance;
    # the leaf top stays near the hinge plane so the tab remains within
    # support distance (<=1mm) of the hub at every sampled pose.
    hinge_x = hub_start + hub_length - 0.0045
    hinge_y = hub_radius + leaf_gap + 0.5 * leaf_thickness
    tab.visual(
        Box((leaf_thickness, leaf_thickness, leaf_length)),
        origin=Origin(xyz=(0.0, 0.0, -(leaf_top_gap + 0.5 * leaf_length))),
        material=mats["nickel"],
        name="folding_key_leaf", material_class_id="metal.brushed_silver",
    )
    _axis_joint(
        model,
        name="folding_key_hinge",
        parent=hub,
        child=tab,
        point=(hinge_x, hinge_y, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(
            effort=0.5,
            velocity=2.0,
            lower=-math.radians(95.0),
            upper=0.0,
        ),
    )


_WINDING_BUILDERS = {
    "fixed_side_key": _winding_system_fixed_side_key_build,
    "folding_side_key": _winding_system_folding_side_key_build,
}


def _carry_handle_no_handle_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> None:
    cap = model.part("top_cap", meta={"role": "carry_handle"})
    cap_height = 0.014
    cap.visual(
        Box((0.36 * r.case_width_m, r.case_depth_m + 0.006, cap_height)),
        material=mats["wood_edge"],
        name="source_top_cap", material_class_id="wood.walnut_dark",
    )
    # Cap sits on top of the case (contact, no interpenetration).
    model.articulation(
        "top_cap_mount",
        ArticulationType.FIXED,
        parent=case,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, r.case_height_m + 0.5 * cap_height)),
    )


def _carry_handle_swing_handle_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> None:
    handle = model.part("swing_handle", meta={"role": "carry_handle"})
    span = r.case_width_m + 0.022
    rise = 0.085
    # Lug bridge embeds 0.2mm into the case top; legs pivot above the bridge
    # top with clearance, and run beside the lug plates with a uniform gap —
    # all offsets derive from the resolved case height and member sizes.
    bridge_thickness = 0.009
    bridge_embed = 0.0002
    bridge_center_z = r.case_height_m - bridge_embed + 0.5 * bridge_thickness
    bridge_top_z = bridge_center_z + 0.5 * bridge_thickness
    leg_clearance = 0.0072
    pivot_z = bridge_top_z + leg_clearance
    leg_size = 0.009
    plate_thickness = 0.004
    plate_gap = 0.0008
    plate_y = 0.5 * leg_size + plate_gap + 0.5 * plate_thickness
    plate_drop = 0.002
    handle.visual(
        Box((span, leg_size, leg_size)),
        origin=Origin(xyz=(0.0, 0.0, rise)),
        material=mats["brass"],
        name="carry_grip", material_class_id="metal.brass_aged",
    )
    case.visual(
        Box((span + 0.014, 0.014, bridge_thickness)),
        origin=Origin(xyz=(0.0, 0.0, bridge_center_z)),
        material=mats["brass"],
        name="handle_lug_bridge", material_class_id="metal.brass_aged",
    )
    for side, x in enumerate((-0.5 * span, 0.5 * span)):
        handle.visual(
            Box((leg_size, leg_size, rise)),
            origin=Origin(xyz=(x, 0.0, 0.5 * rise)),
            material=mats["brass"],
            name=f"handle_leg_{side}", material_class_id="metal.brass_aged",
        )
        for plate_side, y in enumerate((-plate_y, plate_y)):
            case.visual(
                Box((0.014, plate_thickness, 0.020)),
                origin=Origin(xyz=(x, y, pivot_z - plate_drop)),
                material=mats["brass"],
                name=f"handle_pivot_lug_{side}_{plate_side}",
                material_class_id="metal.brass_aged",
            )
    _axis_joint(
        model,
        name="carry_handle_swing",
        parent=case,
        child=handle,
        point=(0.0, 0.0, pivot_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(
            effort=2.0,
            velocity=1.2,
            lower=0.0,
            upper=math.radians(105.0),
        ),
    )


_HANDLE_BUILDERS = {
    "no_handle": _carry_handle_no_handle_build,
    "swing_handle": _carry_handle_swing_handle_build,
}


def _base_support_flat_plinth_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> None:
    base = model.part("base_support", meta={"role": "base_support"})
    plinth_height = 0.018
    base.visual(
        Box((r.case_width_m + 0.025, r.case_depth_m + 0.020, plinth_height)),
        material=mats["wood_edge"],
        name="weighted_flat_plinth", material_class_id="wood.walnut_dark",
    )
    # Plinth top touches the case bottom; the rubber pad embeds into the
    # plinth underside. Offsets derive from the member heights.
    rubber_height = 0.004
    rubber_embed = 0.0005
    base.visual(
        Box((r.case_width_m + 0.010, r.case_depth_m + 0.010, rubber_height)),
        origin=Origin(
            xyz=(0.0, 0.0, -0.5 * plinth_height + rubber_embed - 0.5 * rubber_height)
        ),
        material=mats["rubber"],
        name="rubber_underside", material_class_id="rubber.smooth_plain",
    )
    model.articulation(
        "base_support_mount",
        ArticulationType.FIXED,
        parent=case,
        child=base,
        origin=Origin(xyz=(0.0, 0.0, -0.5 * plinth_height)),
    )


def _base_support_leveling_feet_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> None:
    base = model.part("base_support", meta={"role": "base_support"})
    plinth_height = 0.016
    base.visual(
        Box((r.case_width_m + 0.025, r.case_depth_m + 0.020, plinth_height)),
        material=mats["wood_edge"],
        name="raised_plinth", material_class_id="wood.walnut_dark",
    )
    # Feet embed into the plinth underside; offsets derive from member heights.
    foot_height = 0.012
    foot_embed = 0.0005
    foot_center_z = -0.5 * plinth_height + foot_embed - 0.5 * foot_height
    for index, (x, y) in enumerate(
        (
            (-0.43 * r.case_width_m, -0.40 * r.case_depth_m),
            (0.43 * r.case_width_m, -0.40 * r.case_depth_m),
            (-0.43 * r.case_width_m, 0.40 * r.case_depth_m),
            (0.43 * r.case_width_m, 0.40 * r.case_depth_m),
        )
    ):
        base.visual(
            Cylinder(radius=0.009, length=foot_height),
            origin=Origin(xyz=(x, y, foot_center_z)),
            material=mats["rubber"],
            name=f"leveling_foot_{index}", material_class_id="rubber.smooth_plain",
        )
    model.articulation(
        "base_support_mount",
        ArticulationType.FIXED,
        parent=case,
        child=base,
        origin=Origin(xyz=(0.0, 0.0, -0.5 * plinth_height)),
    )


_BASE_BUILDERS = {
    "flat_plinth": _base_support_flat_plinth_build,
    "leveling_feet": _base_support_leveling_feet_build,
}


def build_mechanical_metronome_with_pendulum(
    config: Config,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "mechanical_metronome_with_pendulum",
            "slot_choices": (
                ("case_form", r.case_form),
                ("front_closure", r.front_closure),
                ("tempo_module", r.tempo_module),
                ("winding_system", r.winding_system),
                ("carry_handle", r.carry_handle),
                ("base_support", r.base_support),
                ("tempo_weight_count", r.tempo_weight_count),
            ),
            "source_identity": "wood case, inset scale, visible pendulum, sliding weight, winding key",
        },
    )
    mats = _materials(model)
    case = _CASE_BUILDERS[r.case_form](model, r, mats, assets=assets)
    pendulum = _build_pendulum(model, case, r, mats)
    _build_tempo_weights(model, pendulum, r, mats, assets=assets)
    _CLOSURE_BUILDERS[r.front_closure](model, case, r, mats, assets=assets)
    _WINDING_BUILDERS[r.winding_system](
        model,
        case,
        r,
        mats,
        assets=assets,
    )
    _HANDLE_BUILDERS[r.carry_handle](model, case, r, mats)
    _BASE_BUILDERS[r.base_support](model, case, r, mats)
    return model


def _parts_by_role(model: ArticulatedObject, role: str) -> list[object]:
    return [part for part in model.parts if part.meta.get("role") == role]


def run_mechanical_metronome_with_pendulum_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    cases = _parts_by_role(model, "case_body")
    pendulums = _parts_by_role(model, "pendulum")
    weights = _parts_by_role(model, "tempo_weight")
    keys = _parts_by_role(model, "winding_key")
    case = cases[0] if cases else None
    pendulum = pendulums[0] if pendulums else None
    key = keys[0] if keys else None
    swing = model.get_articulation("pendulum_swing")
    key_turn = model.get_articulation("winding_key_turn")
    weight_slides = [
        joint
        for joint in model.articulations
        if joint.name.startswith("tempo_weight_slide_")
    ]

    ctx.check(
        "category_anchor: mechanical metronome identity",
        len(cases) == len(pendulums) == len(keys) == 1
        and len(weights) == r.tempo_weight_count
        and case is not None
        and pendulum is not None
        and key is not None
        and swing is not None
        and swing.parent == case.name
        and swing.child == pendulum.name
        and key_turn is not None
        and key_turn.parent == case.name
        and key_turn.child == key.name,
        details=f"roles={{case:{len(cases)}, pendulum:{len(pendulums)}, weights:{len(weights)}, key:{len(keys)}}}",
    )
    ctx.check(
        "category_anchor: source-like tempo scale and pendulum",
        case is not None
        and case.get_visual("tempo_scale_panel") is not None
        and case.get_visual("pendulum_pivot_bearing") is not None
        and pendulum is not None
        and pendulum.get_visual("spring_steel_pendulum_rod") is not None
        and all(weight.meta.get("captured_on_rod") is True for weight in weights),
        details=f"case_form={r.case_form}",
    )
    ctx.check(
        f"category_anchor: {r.case_form} identity",
        case is not None
        and case.get_visual(f"{r.case_form}_shell") is not None
        and case.meta.get("source_silhouette") is True,
        details=f"case_meta={getattr(case, 'meta', None)}",
    )
    ctx.check(
        "multiplicity emits exact sliding tempo-weight count",
        len(weights) == r.tempo_weight_count
        and len(weight_slides) == r.tempo_weight_count
        and all(
            joint.parent == "pendulum"
            and joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(joint.axis) == (0.0, 0.0, 1.0)
            for joint in weight_slides
        ),
        details=f"weights={[part.name for part in weights]}",
    )
    ctx.check(
        "pendulum range and winding axis are source-correct",
        swing is not None
        and tuple(swing.axis) == (0.0, 1.0, 0.0)
        and swing.motion_limits is not None
        and math.isclose(swing.motion_limits.lower, -r.swing_limit_rad)
        and math.isclose(swing.motion_limits.upper, r.swing_limit_rad)
        and key_turn is not None
        and tuple(key_turn.axis) == (1.0, 0.0, 0.0),
        details=f"swing={swing}, key={key_turn}",
    )

    if pendulum is not None:
        for weight in weights:
            ctx.allow_isolated_part(
                weight,
                reason=(
                    "Tempo weight is retained by its prismatic joint on the pendulum rod; "
                    "the enlarged bore intentionally leaves running clearance for downstream motion."
                ),
            )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "long_dual_bell_hinged_arch",
        {
            "case_form": "arched_case",
            "front_closure": "hinged_cover",
            "tempo_module": "bell_beat_slider",
            "winding_system": "folding_side_key",
            "carry_handle": "swing_handle",
            "base_support": "leveling_feet",
            "tempo_weight_count": 2,
            "pendulum_length_m": 0.36,
            "swing_limit_rad": 0.50,
        },
        reason="maximum visible pendulum, two sliders and all moving accessories",
    ),
    corner_case(
        "short_plain_open_pyramid",
        {
            "case_form": "pyramid_case",
            "front_closure": "open_scale",
            "tempo_module": "plain_slider",
            "winding_system": "fixed_side_key",
            "carry_handle": "no_handle",
            "base_support": "flat_plinth",
            "tempo_weight_count": 1,
            "pendulum_length_m": 0.26,
            "swing_limit_rad": 0.28,
        },
        reason="smallest source-like shell and shortest slider clearances",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_mechanical_metronome_with_pendulum",
    "config_from_seed",
    "resolve_config",
    "run_mechanical_metronome_with_pendulum_tests",
]
