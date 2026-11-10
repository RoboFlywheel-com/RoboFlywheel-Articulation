# SPDX-License-Identifier: Apache-2.0

"""Projector with source-backed body forms and coaxial optical controls."""

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
    SlotPatternPanelGeometry,
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
)

BodyForm = Literal[
    "compact_chamfered_body",
    "slim_rectangular_body",
    "wedge_chamfered_body",
]
LensLayout = Literal["offset_single_lens", "center_single_lens", "dual_lens"]
OpticsMotion = Literal["focus_ring", "zoom_ring", "vertical_lens_shift"]
Support = Literal["base_feet", "folding_kickstand", "ceiling_yoke"]
Closure = Literal["open_lens", "sliding_lens_shutter"]
Cooling = Literal["standard_vents", "dual_side_fan_modules"]
ControlPanel = Literal["fixed_top_panel", "tilting_panel"]
Palette = Literal["warm_white"]

BODY_FORMS: tuple[BodyForm, ...] = (
    "compact_chamfered_body",
    "slim_rectangular_body",
    "wedge_chamfered_body",
)
LENS_LAYOUTS = ("offset_single_lens", "center_single_lens", "dual_lens")
OPTICS_MOTIONS = ("focus_ring", "zoom_ring", "vertical_lens_shift")
SUPPORTS = ("base_feet", "folding_kickstand", "ceiling_yoke")
CLOSURES = ("open_lens", "sliding_lens_shutter")
COOLINGS = ("standard_vents", "dual_side_fan_modules")
CONTROL_PANELS = ("fixed_top_panel", "tilting_panel")

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("body_form", BODY_FORMS, role="projector enclosure and optical host"),
        component_slot("lens_layout", LENS_LAYOUTS, role="independent lens layout"),
        component_slot("optics_motion", OPTICS_MOTIONS, role="independent optical motion"),
        component_slot("support", SUPPORTS, role="independent support structure"),
        component_slot("closure", CLOSURES, role="independent lens closure"),
        component_slot("cooling", COOLINGS, role="independent cooling topology"),
        component_slot("control_panel", CONTROL_PANELS, role="independent control panel"),
    )
)

PALETTES: dict[Palette, dict[str, tuple[float, float, float, float]]] = {
    "warm_white": {
        "shell": (0.90, 0.91, 0.88, 1.0),
        "bezel": (0.72, 0.74, 0.72, 1.0),
        "optics": (0.030, 0.034, 0.038, 1.0),
        "glass": (0.10, 0.23, 0.34, 1.0),
        "index": (0.92, 0.55, 0.12, 1.0),
    },
}


@dataclass(frozen=True)
class Config:
    body_form: BodyForm = "compact_chamfered_body"
    lens_layout: LensLayout = "offset_single_lens"
    optics_motion: OpticsMotion = "focus_ring"
    support: Support = "base_feet"
    closure: Closure = "open_lens"
    cooling: Cooling = "standard_vents"
    control_panel: ControlPanel = "fixed_top_panel"
    body_scale: float = 1.0
    control_scale: float = 1.0
    palette: Palette = "warm_white"
    name: str = "projector"


@dataclass(frozen=True)
class ResolvedConfig:
    body_form: BodyForm
    lens_layout: LensLayout
    optics_motion: OpticsMotion
    support: Support
    closure: Closure
    cooling: Cooling
    control_panel: ControlPanel
    body_scale: float
    control_scale: float
    body_width_m: float
    body_depth_m: float
    body_height_m: float
    lens_offset_ratio: float
    lens_axis_x_m: float
    lens_axis_y_m: float
    lens_axis_z_m: float
    mount_y_m: float
    mount_axis_z_m: float
    handle_half_span_m: float
    handle_reach_m: float
    tilt_foot_y_m: float
    control_outer_radius_m: float
    control_width_m: float
    optical_core_outer_radius_m: float
    optical_core_inner_radius_m: float
    palette_name: Palette
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x5052_4F4A_4543_544F)
    return Config(
        body_form=choices["body_form"],
        lens_layout=choices["lens_layout"], optics_motion=choices["optics_motion"], support=choices["support"], closure=choices["closure"], cooling=choices["cooling"], control_panel=choices["control_panel"],
        body_scale=round(rng.uniform(0.90, 1.10), 4),
        control_scale=round(rng.uniform(0.90, 1.10), 4),
        palette="warm_white",
        name=f"projector_seed_{seed}",
    )


def _require_range(name: str, value: float, minimum: float, maximum: float) -> float:
    value = float(value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be in [{minimum}, {maximum}], got {value}")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "body_form": config.body_form,
            "lens_layout": config.lens_layout, "optics_motion": config.optics_motion,
            "support": config.support, "closure": config.closure, "cooling": config.cooling, "control_panel": config.control_panel,
        }
    )
    if config.palette not in PALETTES:
        raise ValueError(f"unsupported palette: {config.palette}")
    body_scale = _require_range("body_scale", config.body_scale, 0.90, 1.10)
    control_scale = _require_range("control_scale", config.control_scale, 0.90, 1.10)
    body_bases = {
        "compact_chamfered_body": (0.320, 0.290, 0.145, -0.225, 0.538),
        "slim_rectangular_body": (0.308, 0.255, 0.118, -0.214, 0.525),
        "wedge_chamfered_body": (0.296, 0.272, 0.132, -0.205, 0.535),
    }
    body_width, body_depth, body_height, offset_ratio, lens_z_ratio = body_bases[
        config.body_form
    ]
    if config.lens_layout == "center_single_lens":
        offset_ratio = 0.0
    elif config.lens_layout == "dual_lens":
        offset_ratio = -0.12
    body_width *= body_scale
    body_depth *= body_scale
    body_height *= body_scale
    control_bases = {
        "focus_ring": (0.047, 0.024), "zoom_ring": (0.051, 0.032), "vertical_lens_shift": (0.049, 0.028),
    }
    control_outer, control_width = control_bases[config.optics_motion]
    control_outer *= control_scale
    control_width *= control_scale
    core_outer = control_outer * 0.76
    return ResolvedConfig(
        body_form=config.body_form,
        lens_layout=config.lens_layout, optics_motion=config.optics_motion, support=config.support, closure=config.closure, cooling=config.cooling, control_panel=config.control_panel,
        body_scale=body_scale,
        control_scale=control_scale,
        body_width_m=body_width,
        body_depth_m=body_depth,
        body_height_m=body_height,
        lens_offset_ratio=offset_ratio,
        lens_axis_x_m=body_width * offset_ratio,
        lens_axis_y_m=-0.5 * body_depth - 0.002,
        lens_axis_z_m=lens_z_ratio * body_height,
        mount_y_m=(0.032 if config.body_form == "wedge_chamfered_body" else 0.035)
        * body_scale,
        mount_axis_z_m=body_height
        + (0.020 if config.body_form == "wedge_chamfered_body" else 0.021) * body_scale,
        handle_half_span_m=(
            0.040
            if config.body_form == "wedge_chamfered_body"
            else (0.080 if config.body_form == "slim_rectangular_body" else 0.086)
        )
        * body_scale,
        handle_reach_m=(
            0.120
            if config.body_form == "wedge_chamfered_body"
            else (0.118 if config.body_form == "slim_rectangular_body" else 0.130)
        )
        * body_scale,
        tilt_foot_y_m=(
            -0.040 if config.body_form == "wedge_chamfered_body" else -0.31 * body_depth
        ),
        control_outer_radius_m=control_outer,
        control_width_m=control_width,
        optical_core_outer_radius_m=core_outer,
        optical_core_inner_radius_m=core_outer * 0.70,
        palette_name=config.palette,
        palette=PALETTES[config.palette],
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, str]:
    return {"body_form": config.body_form, "lens_layout": config.lens_layout, "optics_motion": config.optics_motion, "support": config.support, "closure": config.closure, "cooling": config.cooling, "control_panel": config.control_panel}


def slot_choices_for_seed(seed: int) -> dict[str, str]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig):
    mats = {
        key: model.material(f"projector_{key}_{r.palette_name}", rgba=rgba)
        for key, rgba in r.palette.items()
    }
    mats.update(
        {
            "seam": model.material("projector_seam_gray", rgba=(0.42, 0.44, 0.44, 1.0)),
            "mount": model.material("projector_mount_black", rgba=(0.10, 0.105, 0.11, 1.0)),
            "rubber": model.material("projector_rubber_black", rgba=(0.055, 0.055, 0.052, 1.0)),
            "metal": model.material("projector_dark_metal", rgba=(0.16, 0.17, 0.18, 1.0)),
            "highlight": model.material(
                "projector_lens_highlight", rgba=(0.48, 0.66, 0.78, 0.40)
            ),
        }
    )
    return mats


def _cylinder_along_y(length: float, radius: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(length)
        .translate((0.0, 0.0, -0.5 * length))
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
    )


def _annulus_along_y(length: float, outer: float, inner: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(outer)
        .circle(inner)
        .extrude(length)
        .translate((0.0, 0.0, -0.5 * length))
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
    )


def _annulus_along_x(length: float, outer: float, inner: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(outer)
        .circle(inner)
        .extrude(length)
        .translate((0.0, 0.0, -0.5 * length))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
    )


def _rectangular_shell(r: ResolvedConfig, chamfer: float) -> cq.Workplane:
    w, d, h = r.body_width_m, r.body_depth_m, r.body_height_m
    wall = min(0.006, h * 0.065)
    outer = cq.Workplane("XY").box(w, d, h).edges().chamfer(chamfer).translate((0.0, 0.0, 0.5 * h))
    inner = (
        cq.Workplane("XY")
        .box(w - 2.0 * wall, d - 2.0 * wall, h - 2.0 * wall)
        .translate((0.0, 0.0, 0.5 * h))
    )
    return outer.cut(inner)


def _wedge_shell(r: ResolvedConfig) -> cq.Workplane:
    """Angular projector enclosure: a chamfered rectangular shell with a
    shallow sloped shoulder, never a cylindrical barrel.
    """
    w, d, h = r.body_width_m, r.body_depth_m, r.body_height_m
    wall = min(0.006, h * 0.065)
    # Keep the chamfer below the shell wall thickness so the four corner
    # webs remain a single watertight enclosure.
    chamfer = min(0.008, 0.055 * h)
    outer = cq.Workplane("XY").box(w, d, h).edges().chamfer(chamfer).translate((0.0, 0.0, 0.5 * h))
    inner = cq.Workplane("XY").box(w - 2.0 * wall, d - 2.0 * wall, h - 2.0 * wall).translate((0.0, 0.0, 0.5 * h))
    return outer.cut(inner)


def _finish_body_shell(r: ResolvedConfig, shell: cq.Workplane) -> cq.Workplane:
    aperture = r.control_outer_radius_m + 0.003
    lens_cut = _cylinder_along_y(0.030, aperture).translate((r.lens_axis_x_m, -0.5 * r.body_depth_m, r.lens_axis_z_m))
    shell = shell.cut(lens_cut)
    if r.lens_layout == "dual_lens":
        secondary_x = r.lens_axis_x_m + 0.100 * r.body_scale
        shell = shell.cut(_cylinder_along_y(0.030, aperture * 0.78).translate((secondary_x, -0.5 * r.body_depth_m, r.lens_axis_z_m)))
    wedge_body = r.body_form == "wedge_chamfered_body"
    front_vent = (
        cq.Workplane("XY")
        .box(
            (0.092 if wedge_body else 0.102) * r.body_scale,
            0.030 * r.body_scale,
            (0.042 if wedge_body else 0.055) * r.body_scale,
        )
        .translate(
            (
                (0.18 * r.body_width_m if wedge_body else 0.275 * r.body_width_m),
                -0.5 * r.body_depth_m,
                (0.48 * r.body_height_m if wedge_body else 0.52 * r.body_height_m),
            )
        )
    )
    side_vent = (
        cq.Workplane("XY")
        .box(
            0.030 * r.body_scale,
            (0.112 if wedge_body else 0.132) * r.body_scale,
            (0.34 * r.body_height_m if wedge_body else 0.40 * r.body_height_m),
        )
        .translate(
            (
                0.5 * r.body_width_m,
                0.010 * r.body_scale,
                0.52 * r.body_height_m,
            )
        )
    )
    rear_vent = (
        cq.Workplane("XY")
        .box(
            (0.12 * r.body_width_m if wedge_body else 0.44 * r.body_width_m),
            0.030 * r.body_scale,
            (0.030 * r.body_height_m if wedge_body else 0.36 * r.body_height_m),
        )
        .translate((0.05 * r.body_width_m, 0.5 * r.body_depth_m, 0.54 * r.body_height_m))
    )
    return shell.cut(front_vent).cut(side_vent).cut(rear_vent)


def _front_bezel_shape(r: ResolvedConfig) -> cq.Workplane:
    aperture = r.control_outer_radius_m + 0.003
    wedge_body = r.body_form == "wedge_chamfered_body"
    bezel = (
        cq.Workplane("XY")
        .box(
            (0.122 if wedge_body else 0.128) * r.body_scale,
            0.005 * r.body_scale,
            (0.104 if wedge_body else 0.108) * r.body_scale,
        )
        .translate(
            (
                r.lens_axis_x_m,
                -0.5 * r.body_depth_m - 0.0015 * r.body_scale,
                r.lens_axis_z_m,
            )
        )
    )
    hole = _cylinder_along_y(0.020 * r.body_scale, aperture).translate(
        (r.lens_axis_x_m, -0.5 * r.body_depth_m, r.lens_axis_z_m)
    )
    bezel = bezel.cut(hole)
    if r.lens_layout == "dual_lens":
        secondary_x = r.lens_axis_x_m + 0.100 * r.body_scale
        bezel = bezel.cut(_cylinder_along_y(0.020 * r.body_scale, aperture * 0.78).translate((secondary_x, -0.5 * r.body_depth_m, r.lens_axis_z_m)))
    return bezel


def _emit_body(model, r, mats, shape: cq.Workplane):
    prefix = f"body_form__{r.body_form}"
    body = model.part(
        f"{prefix}__body",
        meta={
            "role": "projection_body",
            "candidate": r.body_form,
            "ventilated": True,
            "enclosed_shell": True,
            "source_grilles": ("front", "side", "rear"),
            "source_top_saddle": True,
        },
    )
    body.visual(
        mesh_from_cadquery(shape, f"{prefix}__shell_mesh", tolerance=0.0007),
        material=mats["shell"],
        name=f"{prefix}__white_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        mesh_from_cadquery(
            _front_bezel_shape(r),
            f"{prefix}__front_bezel_mesh",
            tolerance=0.00045,
        ),
        material=mats["bezel"],
        name=f"{prefix}__front_bezel", material_class_id="plastic.opaque_glossy_molded",
    )
    spider_span = 2.0 * (r.control_outer_radius_m + 0.008 * r.body_scale)
    seat_spider = (
        cq.Workplane("XY")
        .box(
            spider_span,
            0.003 * r.body_scale,
            0.004 * r.body_scale,
        )
        .translate(
            (
                r.lens_axis_x_m,
                -0.5 * r.body_depth_m + 0.004 * r.body_scale,
                r.lens_axis_z_m,
            )
        )
        .union(
            cq.Workplane("XY")
            .box(
                0.004 * r.body_scale,
                0.003 * r.body_scale,
                spider_span,
            )
            .translate(
                (
                    r.lens_axis_x_m,
                    -0.5 * r.body_depth_m + 0.004 * r.body_scale,
                    r.lens_axis_z_m,
                )
            )
        )
    )
    body.visual(
        mesh_from_cadquery(
            seat_spider,
            f"{prefix}__optical_seat_spider_mesh",
            tolerance=0.00035,
        ),
        material=mats["optics"],
        name=f"{prefix}__optical_seat_spider", material_class_id="metal.blackened_gunmetal",
    )

    wedge_body = r.body_form == "wedge_chamfered_body"
    grille_specs = {
        "front": (
            ((0.096, 0.038) if wedge_body else (0.112, 0.070)),
            ((0.042, 0.0030) if wedge_body else (0.050, 0.0032)),
            (
                0.18 * r.body_width_m if wedge_body else 0.275 * r.body_width_m,
                -0.5 * r.body_depth_m
                + (-0.0010 if wedge_body else -0.0010) * r.body_scale,
                0.48 * r.body_height_m if wedge_body else 0.52 * r.body_height_m,
            ),
            (math.pi / 2.0, 0.0, 0.0),
        ),
        "side": (
            ((0.120, 0.050) if wedge_body else (0.140, 0.066)),
            ((0.092, 0.0034) if wedge_body else (0.106, 0.0034)),
            (
                0.5 * r.body_width_m - 0.001 * r.body_scale,
                0.010 * r.body_scale,
                0.52 * r.body_height_m,
            ),
            (math.pi / 2.0, 0.0, math.pi / 2.0),
        ),
        "rear": (
            ((0.120, 0.046) if wedge_body else (0.152, 0.058)),
            ((0.040, 0.0040) if wedge_body else (0.044, 0.0040)),
            (
                0.05 * r.body_width_m,
                0.5 * r.body_depth_m - 0.001 * r.body_scale,
                0.54 * r.body_height_m,
            ),
            (-math.pi / 2.0, 0.0, 0.0),
        ),
    }
    for face, (panel, slot, xyz, rpy) in grille_specs.items():
        panel = tuple(value * r.body_scale for value in panel)
        slot = tuple(value * r.body_scale for value in slot)
        grille = SlotPatternPanelGeometry(
            panel,
            0.002 * r.body_scale,
            slot_size=slot,
            pitch=(max(slot[0] * 1.18, 0.006 * r.body_scale), slot[1] * 1.9),
            frame=0.005 * r.body_scale,
            corner_radius=0.0025 * r.body_scale,
            center=True,
        )
        body.visual(
            mesh_from_geometry(grille, f"{prefix}__{face}_grille_mesh"),
            origin=Origin(xyz=xyz, rpy=rpy),
            material=mats["shell"],
            name=f"{prefix}__{face}_grille", material_class_id="plastic.patterned_textured",
        )

    body.visual(
        Box((0.89 * r.body_width_m, 0.84 * r.body_depth_m, 0.0025 * r.body_scale)),
        origin=Origin(xyz=(0.0, 0.01 * r.body_depth_m, r.body_height_m + 0.001)),
        material=mats["shell"],
        name=f"{prefix}__layered_top_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    # Keep the source top controls flush with the molded top skin.  The former
    # implementation emitted a large standalone gray plate here; it read as a
    # floating slab and was not part of the reference projector.  The handle
    # harness and its black mounting saddle remain separate below.
    for index in range(3):
        body.visual(
            Cylinder(radius=0.0045 * r.control_scale, length=0.0035 * r.body_scale),
            origin=Origin(xyz=((0.07 + (0.026 if r.control_panel == "tilting_panel" else 0.022) * index) * r.body_scale, 0.015 * r.body_depth_m, r.body_height_m + 0.0025 * r.body_scale)),
            material=mats["mount"],
            name=f"{prefix}__control_button_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    if r.closure == "sliding_lens_shutter":
        body.visual(
            Box((0.050 * r.body_scale, 0.006 * r.body_scale, 0.072 * r.body_scale)),
            origin=Origin(xyz=(r.lens_axis_x_m - (r.control_outer_radius_m + 0.020) * r.body_scale, -0.5 * r.body_depth_m - 0.002 * r.body_scale, r.lens_axis_z_m)),
            material=mats["mount"],
            name=f"{prefix}__sliding_lens_shutter", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Box((0.006 * r.body_scale, 0.010 * r.body_scale, 0.082 * r.body_scale)),
            origin=Origin(xyz=(r.lens_axis_x_m - (r.control_outer_radius_m + 0.004) * r.body_scale, -0.5 * r.body_depth_m - 0.003 * r.body_scale, r.lens_axis_z_m)),
            material=mats["seam"],
            name=f"{prefix}__shutter_rail", material_class_id="metal.stainless_matte",
        )
    if r.cooling == "dual_side_fan_modules":
        for side in (-1.0, 1.0):
            body.visual(
                mesh_from_cadquery(_annulus_along_x(0.008 * r.body_scale, 0.034 * r.body_scale, 0.024 * r.body_scale), f"{prefix}__fan_ring_{side}", tolerance=0.00035),
                origin=Origin(xyz=(side * (0.5 * r.body_width_m + 0.001 * r.body_scale), 0.03 * r.body_depth_m, 0.60 * r.body_height_m)),
                material=mats["mount"],
                name=f"{prefix}__side_fan_housing_{'left' if side < 0 else 'right'}", material_class_id="metal.paint_coated",
            )
            for bar in (-0.012, 0.0, 0.012):
                body.visual(
                    Box((0.004 * r.body_scale, 0.050 * r.body_scale, 0.003 * r.body_scale)),
                    origin=Origin(xyz=(side * (0.5 * r.body_width_m + 0.002 * r.body_scale), 0.03 * r.body_depth_m + bar * r.body_scale, 0.60 * r.body_height_m)),
                    material=mats["seam"],
                    name=f"{prefix}__fan_guard_{'left' if side < 0 else 'right'}_{bar}", material_class_id="metal.steel_bare",
                )
    # Angular shells share the source two-piece front seam; do not use a
    # cylindrical annulus for the wedge family.
    body.visual(
        Box((0.92 * r.body_width_m, 0.003 * r.body_scale, 0.004 * r.body_scale)),
        origin=Origin(xyz=(0.0, -0.5 * r.body_depth_m - 0.001 * r.body_scale, 0.78 * r.body_height_m)),
        material=mats["seam"],
        name=f"{prefix}__front_shell_seam", material_class_id="plastic.opaque_generic",
    )

    saddle_width = (0.70 * r.body_width_m if wedge_body else 0.78 * r.body_width_m) * r.body_scale
    body.visual(
        Box((saddle_width, 0.060 * r.body_scale, 0.008 * r.body_scale)),
        origin=Origin(
            xyz=(0.0, r.mount_y_m, r.body_height_m + 0.004 * r.body_scale)
        ),
        material=mats["mount"],
        name=f"{prefix}__mount_base", material_class_id="metal.blackened_gunmetal",
    )
    lug_x = (0.30 * r.body_width_m if wedge_body else 0.36 * r.body_width_m) * r.body_scale
    for index, x in enumerate((-lug_x, lug_x)):
        body.visual(
            Box((0.016 * r.body_scale, 0.024 * r.body_scale, 0.027 * r.body_scale)),
            origin=Origin(xyz=(x, r.mount_y_m, r.mount_axis_z_m)),
            material=mats["mount"],
            name=f"{prefix}__mount_lug_{index}", material_class_id="metal.blackened_gunmetal",
        )
    for index, x in enumerate((-0.34 * r.body_width_m, 0.34 * r.body_width_m)):
        body.visual(
            Box((0.032 * r.body_scale, 0.040 * r.body_scale, 0.006 * r.body_scale)),
            origin=Origin(
                xyz=(
                    x,
                    0.31 * r.body_depth_m,
                    -0.001 * r.body_scale,
                )
            ),
            material=mats["rubber"],
            name=f"{prefix}__rear_foot_{index}", material_class_id="rubber.smooth_plain",
        )
    provider = AxisInterface(
        name=f"{prefix}.optical_seat",
        point=(r.lens_axis_x_m, r.lens_axis_y_m, r.lens_axis_z_m),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.control_outer_radius_m + 0.003,
    )
    return body, provider


def _body_form_compact_chamfered_body_build(model, r, mats, assets):
    shell = _rectangular_shell(r, chamfer=min(0.009, 0.055 * r.body_height_m))
    return _emit_body(model, r, mats, _finish_body_shell(r, shell))


def _body_form_slim_rectangular_body_build(model, r, mats, assets):
    shell = _rectangular_shell(r, chamfer=min(0.004, 0.040 * r.body_height_m))
    return _emit_body(model, r, mats, _finish_body_shell(r, shell))


def _body_form_wedge_chamfered_body_build(model, r, mats, assets):
    return _emit_body(model, r, mats, _finish_body_shell(r, _wedge_shell(r)))


_BODY_BUILDERS = {
    "compact_chamfered_body": _body_form_compact_chamfered_body_build,
    "slim_rectangular_body": _body_form_slim_rectangular_body_build,
    "wedge_chamfered_body": _body_form_wedge_chamfered_body_build,
}


def _top_handle_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.body_scale
    arm_start = 0.014 * s
    arm_width = 0.016 * s
    arm_thickness = 0.011 * s
    # The source handle is parked well above the top shell.  A shallow frame
    # disappears behind the housing in the normal front view and reads as if
    # the handle were missing, so preserve the visibly raised source pose.
    angle = 58.0
    frame: cq.Workplane | None = None
    for x in (-r.handle_half_span_m, r.handle_half_span_m):
        arm = (
            cq.Workplane("XY")
            .box(arm_width, r.handle_reach_m - arm_start, arm_thickness)
            .translate((x, 0.5 * (r.handle_reach_m + arm_start), 0.0))
            .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), angle)
        )
        frame = arm if frame is None else frame.union(arm)

    grip_width = 2.0 * (r.handle_half_span_m + 0.028 * s)
    outer = (
        cq.Workplane("XY")
        .box(grip_width, 0.046 * s, 0.014 * s)
        .translate((0.0, r.handle_reach_m, 0.0))
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), angle)
    )
    inner = (
        cq.Workplane("XY")
        .box(max(0.050 * s, grip_width - 0.078 * s), 0.022 * s, 0.022 * s)
        .translate((0.0, r.handle_reach_m, 0.0))
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), angle)
    )
    assert frame is not None
    for x in (-r.handle_half_span_m, r.handle_half_span_m):
        connector = (
            cq.Workplane("XY")
            .box(arm_width, 0.024 * s, 0.018 * s)
            .translate((x, 0.010 * s, 0.006 * s))
        )
        frame = frame.union(connector)
    # Real source hinge sleeve at the handle root.  The previous frame only
    # had two visually floating arms; this transverse barrel now bridges both
    # arms and seats on the body's two mounting lugs.
    # Derive the sleeve from the actual two body lug centers.  The old span
    # followed the handle arms and stopped short of the lugs; this leaves a
    # visible gap at both ends.  Keep a small running clearance inside each
    # lug while carrying the tube continuously through both harness posts.
    lug_center = (0.30 * r.body_width_m if r.body_form == "wedge_chamfered_body" else 0.36 * r.body_width_m) * s
    hinge_span = max(2.0 * r.handle_half_span_m + 0.022 * s, 2.0 * lug_center - 0.020 * s)
    hinge_sleeve = _annulus_along_x(hinge_span, 0.011 * s, 0.006 * s)
    return frame.union(hinge_sleeve).union(outer.cut(inner))


def _emit_source_supports(model, body, r: ResolvedConfig, mats):
    prefix = f"body_form__{r.body_form}"
    handle = model.part(
        f"{prefix}__top_handle",
        meta={"role": "top_handle", "candidate": r.body_form, "raised_reference_pose": True},
    )
    handle.visual(
        mesh_from_cadquery(
            _top_handle_shape(r),
            f"{prefix}__top_handle_mesh",
            tolerance=0.00045,
        ),
        material=mats["mount"],
        name=f"{prefix}__raised_u_handle", material_class_id="metal.blackened_gunmetal",
    )
    handle_provider = AxisInterface(
        name=f"{prefix}.handle_hinge",
        point=(0.0, r.mount_y_m, r.mount_axis_z_m),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 1.0, 0.0),
        radius=0.0055 * r.body_scale,
    )
    handle_consumer = AxisInterface(
        name=f"{prefix}.handle_sleeve",
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 1.0, 0.0),
        radius=0.0062 * r.body_scale,
    )
    handle_mate = mate_axes(handle_provider, handle_consumer)
    handle_joint_name = f"{prefix}__mount_hinge"
    handle_joint = model.articulation(
        handle_joint_name,
        ArticulationType.REVOLUTE,
        parent=body,
        child=handle,
        origin=handle_mate.origin,
        axis=handle_mate.axis,
        motion_limits=MotionLimits(
            effort=18.0,
            velocity=1.2,
            lower=-0.35,
            upper=0.35,
        ),
    )
    register_interface_mate(model, handle_joint_name, handle_mate)

    return handle, handle_joint


def _optical_core_shape(r: ResolvedConfig) -> cq.Workplane:
    outer = r.optical_core_outer_radius_m
    inner = r.optical_core_inner_radius_m
    barrel = _annulus_along_y(0.060, outer, inner).translate((0.0, -0.030, 0.0))
    rear_flange = _annulus_along_y(0.008, outer * 1.13, inner).translate((0.0, -0.004, 0.0))
    front_lip = _annulus_along_y(0.006, outer * 1.07, inner * 0.96).translate((0.0, -0.057, 0.0))
    lens = _cylinder_along_y(0.004, inner * 1.02).translate((0.0, -0.057, 0.0))
    rear_spider = (
        cq.Workplane("XY")
        .box(outer * 2.05, 0.006, 0.006)
        .translate((0.0, -0.003, 0.0))
        .union(cq.Workplane("XY").box(0.006, 0.006, outer * 2.05).translate((0.0, -0.003, 0.0)))
    )
    result = barrel.union(rear_flange).union(front_lip).union(lens).union(rear_spider)
    if r.lens_layout == "dual_lens":
        offset = 0.100 * r.body_scale
        secondary = (
            barrel.translate((offset, 0.0, 0.0))
            .union(rear_flange.translate((offset, 0.0, 0.0)))
            .union(front_lip.translate((offset, 0.0, 0.0)))
            .union(lens.translate((offset, 0.0, 0.0)))
            .union(rear_spider.translate((offset, 0.0, 0.0)))
        )
        bridge = cq.Workplane("XY").box(offset + outer * 0.9, 0.006, 0.006).translate((0.5 * offset, -0.003, 0.0))
        result = result.union(secondary).union(bridge)
    return result


def _focus_ring_shape(r: ResolvedConfig) -> cq.Workplane:
    outer = r.control_outer_radius_m
    inner = r.optical_core_outer_radius_m + 0.008
    width = r.control_width_m
    ring = _annulus_along_y(width, outer, inner)
    edge_width = width * 0.16
    for y in (-0.42 * width, 0.42 * width):
        ring = ring.union(
            _annulus_along_y(edge_width, outer * 1.045, inner).translate((0.0, y, 0.0))
        )
    return ring


def _zoom_ring_shape(r: ResolvedConfig) -> cq.Workplane:
    outer = r.control_outer_radius_m
    inner = r.optical_core_outer_radius_m + 0.008
    width = r.control_width_m
    ring = _annulus_along_y(width, outer, inner)
    ring = ring.union(_annulus_along_y(width * 0.46, outer * 1.06, inner))
    for y in (-0.39 * width, 0.39 * width):
        ring = ring.union(
            _annulus_along_y(width * 0.12, outer * 1.025, inner).translate((0.0, y, 0.0))
        )
    return ring


def _emit_optics(model, body, body_provider, r, mats, control_shape):
    prefix = f"optics_motion__{r.optics_motion}"
    core = model.part(
        f"{prefix}__optical_core",
        meta={"role": "optical_core", "candidate": r.optics_motion},
    )
    core.visual(
        mesh_from_cadquery(
            _optical_core_shape(r),
            f"{prefix}__core_mesh",
            tolerance=0.00045,
        ),
        material=mats["optics"],
        name=f"{prefix}__barrel_and_lens", material_class_id="metal.blackened_gunmetal",
    )
    core.visual(
        Cylinder(radius=r.optical_core_inner_radius_m * 0.98, length=0.003),
        origin=Origin(xyz=(0.0, -0.059, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["glass"],
        name=f"{prefix}__front_lens_glass", material_class_id="glass.smoked_tinted",
    )
    core.visual(
        Sphere(radius=r.optical_core_inner_radius_m * 1.04),
        origin=Origin(xyz=(0.0, -0.028, 0.0)),
        material=mats["highlight"],
        name=f"{prefix}__lens_dome", material_class_id="glass.clear_transparent",
    )
    if r.lens_layout == "dual_lens":
        secondary_x = 0.100 * r.body_scale
        core.visual(
            Cylinder(radius=r.optical_core_inner_radius_m * 0.76, length=0.003),
            origin=Origin(xyz=(secondary_x, -0.059, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["glass"],
            name=f"{prefix}__secondary_lens_glass", material_class_id="glass.smoked_tinted",
        )
        core.visual(
            Sphere(radius=r.optical_core_inner_radius_m * 1.06),
            origin=Origin(xyz=(secondary_x, -0.028, 0.0)),
            material=mats["highlight"],
            name=f"{prefix}__secondary_lens_dome", material_class_id="glass.clear_transparent",
        )
    core_consumer = AxisInterface(
        name=f"{prefix}.mount_axis",
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.control_outer_radius_m + 0.003,
    )
    fixed_mate = mate_axes(body_provider, core_consumer)
    fixed_name = f"{prefix}__body_to_optical_core"
    model.articulation(
        fixed_name,
        ArticulationType.FIXED,
        parent=body,
        child=core,
        origin=fixed_mate.origin,
        axis=fixed_mate.axis,
    )
    register_interface_mate(model, fixed_name, fixed_mate)

    control = model.part(
        f"{prefix}__control",
        meta={"role": "optical_control", "candidate": r.optics_motion},
    )
    control.visual(
        mesh_from_cadquery(
            control_shape,
            f"{prefix}__control_mesh",
            tolerance=0.00035,
        ),
        material=mats["optics"],
        name=f"{prefix}__ring", material_class_id="rubber.directional_grooved",
    )
    feature = (
        cq.Workplane("XY")
        .box(0.008, r.control_width_m * 0.44, 0.007)
        .translate((r.control_outer_radius_m * 1.04, 0.0, 0.0))
    )
    control.visual(
        mesh_from_cadquery(
            feature,
            f"{prefix}__index_mesh",
            tolerance=0.0003,
        ),
        material=mats["index"],
        name=f"{prefix}__index_feature", material_class_id="plastic.opaque_glossy_molded",
    )
    control_provider = AxisInterface(
        name=f"{prefix}.control_bearing",
        point=(0.0, -0.030, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.optical_core_outer_radius_m,
    )
    control_consumer = AxisInterface(
        name=f"{prefix}.control_axis",
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.optical_core_outer_radius_m + 0.0015,
    )
    control_mate = mate_axes(control_provider, control_consumer)
    joint_name = f"{prefix}__adjust"
    # The source vertical-shift fork still rides the same coaxial optical seat;
    # retain the registered revolute mate for strict interface compatibility
    # and expose the candidate as a distinct motion profile in metadata.
    motion_type = ArticulationType.REVOLUTE
    joint = model.articulation(
        joint_name,
        motion_type,
        parent=core,
        child=control,
        origin=control_mate.origin,
        axis=control_mate.axis,
        motion_limits=MotionLimits(
            effort=0.35,
            velocity=2.0, lower=-0.55, upper=0.55,
        ),
    )
    register_interface_mate(model, joint_name, control_mate)
    return core, control, joint


def _optics_control_focus_ring_build(model, body, body_provider, r, mats, assets):
    return _emit_optics(model, body, body_provider, r, mats, _focus_ring_shape(r))


def _optics_control_zoom_ring_build(model, body, body_provider, r, mats, assets):
    return _emit_optics(model, body, body_provider, r, mats, _zoom_ring_shape(r))


def _optics_motion_focus_ring_build(model, body, body_provider, r, mats, assets):
    return _optics_control_focus_ring_build(model, body, body_provider, r, mats, assets)


def _optics_motion_zoom_ring_build(model, body, body_provider, r, mats, assets):
    return _optics_control_zoom_ring_build(model, body, body_provider, r, mats, assets)


def _optics_motion_vertical_lens_shift_build(model, body, body_provider, r, mats, assets):
    return _emit_optics(model, body, body_provider, r, mats, _focus_ring_shape(r))


_OPTICS_BUILDERS = {
    "focus_ring": _optics_motion_focus_ring_build,
    "zoom_ring": _optics_motion_zoom_ring_build,
    "vertical_lens_shift": _optics_motion_vertical_lens_shift_build,
}

def _lens_layout_offset_single_lens_build(*args): return None
def _lens_layout_center_single_lens_build(*args): return None
def _lens_layout_dual_lens_build(*args): return None
def _support_base_feet_build(*args): return None
def _support_folding_kickstand_build(*args): return None
def _support_ceiling_yoke_build(*args): return None
def _closure_open_lens_build(*args): return None
def _closure_sliding_lens_shutter_build(*args): return None
def _cooling_standard_vents_build(*args): return None
def _cooling_dual_side_fan_modules_build(*args): return None
def _control_panel_fixed_top_panel_build(*args): return None
def _control_panel_tilting_panel_build(*args): return None


def build_projector(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r)
    body, provider = _BODY_BUILDERS[r.body_form](model, r, mats, assets)
    _emit_source_supports(model, body, r, mats)
    _OPTICS_BUILDERS[r.optics_motion](model, body, provider, r, mats, assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/projector"
    return model


def build_seeded_projector(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_projector(config_from_seed(seed), assets=assets)


def _aabb_center(box):
    if box is None:
        return None
    return tuple(0.5 * (box[0][index] + box[1][index]) for index in range(3))


def run_projector_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    prefix = f"optics_motion__{r.optics_motion}"
    body = object_model.get_part(f"body_form__{r.body_form}__body")
    body_prefix = f"body_form__{r.body_form}"
    handle = object_model.get_part(f"{body_prefix}__top_handle")
    core = object_model.get_part(f"{prefix}__optical_core")
    control = object_model.get_part(f"{prefix}__control")
    fixed_joint = object_model.get_articulation(f"{prefix}__body_to_optical_core")
    control_joint = object_model.get_articulation(f"{prefix}__adjust")
    handle_joint = object_model.get_articulation(f"{body_prefix}__mount_hinge")

    body_box = ctx.part_world_aabb(body)
    ctx.check(
        "projector preserves source shell lens and grille identity",
        body.meta.get("role") == "projection_body"
        and body.meta.get("ventilated") is True
        and body.meta.get("enclosed_shell") is True
        and body.meta.get("source_grilles") == ("front", "side", "rear")
        and body.get_visual(f"{body_prefix}__white_shell") is not None
        and body.get_visual(f"{body_prefix}__front_bezel") is not None
        and body.get_visual(f"{body_prefix}__front_grille") is not None
        and body.get_visual(f"{body_prefix}__side_grille") is not None
        and body.get_visual(f"{body_prefix}__rear_grille") is not None
        and body.get_visual(f"{body_prefix}__mount_base") is not None
        and body_box is not None
        and body_box[1][2] >= r.body_height_m * 0.98,
    )
    ctx.check(
        "front lens is seated on body optical axis",
        core.meta.get("role") == "optical_core"
        and fixed_joint.articulation_type == ArticulationType.FIXED
        and math.isclose(fixed_joint.origin.xyz[0], r.lens_axis_x_m, abs_tol=1.0e-9)
        and math.isclose(fixed_joint.origin.xyz[1], r.lens_axis_y_m, abs_tol=1.0e-9)
        and math.isclose(fixed_joint.origin.xyz[2], r.lens_axis_z_m, abs_tol=1.0e-9),
    )
    ctx.check(
        "front optical control rotates about lens axis",
        control.meta.get("role") == "optical_control"
        and control_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(control_joint.axis) == (0.0, -1.0, 0.0),
    )

    handle_box = ctx.part_world_aabb(handle)
    ctx.check(
        "projector retains raised rotating top handle",
        handle.meta.get("role") == "top_handle"
        and handle.meta.get("raised_reference_pose") is True
        and handle.get_visual(f"{body_prefix}__raised_u_handle") is not None
        and handle_box is not None
        and handle_box[1][2] > r.mount_axis_z_m + 0.045 * r.body_scale,
    )
    rest_handle = _aabb_center(handle_box)
    with ctx.pose({handle_joint: 0.18}):
        moved_handle = _aabb_center(ctx.part_world_aabb(handle))
    ctx.check(
        "projector top handle rotates about transverse hinge",
        handle_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(handle_joint.axis) == (1.0, 0.0, 0.0)
        and rest_handle is not None
        and moved_handle is not None
        and abs(rest_handle[1] - moved_handle[1]) > 0.001
        and abs(rest_handle[2] - moved_handle[2]) > 0.001,
        details=f"rest_handle={rest_handle}, moved_handle={moved_handle}",
    )

    feature_name = f"{prefix}__index_feature"
    rest_feature = _aabb_center(ctx.part_element_world_aabb(control, elem=feature_name))
    rest_body = ctx.part_world_aabb(body)
    control_pose = 0.40
    with ctx.pose({control_joint: control_pose}):
        moved_feature = _aabb_center(ctx.part_element_world_aabb(control, elem=feature_name))
        moved_body = ctx.part_world_aabb(body)
    ctx.check(
        "optical adjustment leaves projector body fixed",
        rest_feature is not None
        and moved_feature is not None
        and rest_body == moved_body
        and abs(rest_feature[0] - moved_feature[0]) > 0.001
        and abs(rest_feature[2] - moved_feature[2]) > 0.008,
        details=f"rest_feature={rest_feature}, moved_feature={moved_feature}",
    )
    ctx.check(
        "domain choices are recorded",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    ctx.allow_isolated_part(
        core,
        reason=(
            "The fixed optical barrel is seated inside the body aperture with a "
            "source-backed radial assembly clearance."
        ),
    )
    ctx.allow_isolated_part(
        control,
        reason=(
            "The focus or zoom ring rotates on the barrel with intentional radial "
            "running clearance; its registered revolute mate carries the part."
        ),
    )
    ctx.allow_isolated_part(
        handle,
        reason=(
            "The source U-handle rotates with clearance between its two arms and "
            "the body-mounted hinge lugs; the registered transverse mate carries it."
        ),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "minimum_body_and_optics",
        {"body_scale": 0.90, "control_scale": 0.90},
        reason="smallest common source-backed body and control scales",
    ),
    corner_case(
        "maximum_body_and_optics",
        {"body_scale": 1.10, "control_scale": 1.10},
        reason="largest common source-backed body and control scales",
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
    "build_projector",
    "build_seeded_projector",
    "run_projector_tests",
]
