# SPDX-License-Identifier: Apache-2.0

"""Wheelie bin with hinged lid — modular procedural template."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
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

__modular__ = True


BodyShell = Literal[
    "prim_box_walls", "mesh_rrect_loft_shell", "cadquery_loft_shell", "tilted_box_walls"
]
LidModule = Literal["box_panel_skirt", "extrude_rrect_panel", "cadquery_fillet_panel"]
WheelPair = Literal["param_tire_wheel", "lathe_profile_wheel", "primitive_cyl_wheel"]
AxleTopology = Literal["wheels_on_body", "fixed_axle_part", "loop_wheels_on_body"]
HingeInterface = Literal["baked_knuckle_plus_pin", "separate_hinge_pin_part", "cheek_bracket_frame"]
LidExtras = Literal["front_grip_lip", "none_plain", "lock_tab_latch"]
PaletteTheme = Literal["green_hdpe", "blue_recycle", "charcoal", "yellow_lid"]

BODY_MODULES: tuple[BodyShell, ...] = (
    "prim_box_walls",
    "mesh_rrect_loft_shell",
    "cadquery_loft_shell",
    "tilted_box_walls",
)
LID_MODULES: tuple[LidModule, ...] = (
    "box_panel_skirt",
    "extrude_rrect_panel",
    "cadquery_fillet_panel",
)
WHEEL_MODULES: tuple[WheelPair, ...] = (
    "param_tire_wheel",
    "lathe_profile_wheel",
    "primitive_cyl_wheel",
)
AXLE_MODULES: tuple[AxleTopology, ...] = (
    "wheels_on_body",
    "fixed_axle_part",
    "loop_wheels_on_body",
)
HINGE_MODULES: tuple[HingeInterface, ...] = (
    "baked_knuckle_plus_pin",
    "separate_hinge_pin_part",
    "cheek_bracket_frame",
)
EXTRA_MODULES: tuple[LidExtras, ...] = ("front_grip_lip", "none_plain", "lock_tab_latch")

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "green_hdpe": {
        "body": (0.10, 0.36, 0.20, 1),
        "lid": (0.08, 0.30, 0.16, 1),
        "dark": (0.04, 0.05, 0.045, 1),
        "steel": (0.55, 0.57, 0.58, 1),
    },
    "blue_recycle": {
        "body": (0.05, 0.22, 0.62, 1),
        "lid": (0.04, 0.18, 0.50, 1),
        "dark": (0.03, 0.035, 0.04, 1),
        "steel": (0.62, 0.64, 0.66, 1),
    },
    "charcoal": {
        "body": (0.10, 0.11, 0.10, 1),
        "lid": (0.14, 0.15, 0.14, 1),
        "dark": (0.02, 0.02, 0.02, 1),
        "steel": (0.52, 0.53, 0.54, 1),
    },
    "yellow_lid": {
        "body": (0.08, 0.32, 0.18, 1),
        "lid": (0.90, 0.76, 0.12, 1),
        "dark": (0.04, 0.045, 0.04, 1),
        "steel": (0.58, 0.60, 0.62, 1),
    },
}


@dataclass(frozen=True)
class WheelieBinWithHingedLidConfig:
    body_shell_module: BodyShell | None = None
    lid_module: LidModule | None = None
    wheel_pair_module: WheelPair | None = None
    wheel_axle_topology_module: AxleTopology | None = None
    hinge_interface_module: HingeInterface | None = None
    lid_extras_module: LidExtras | None = None
    palette_theme: PaletteTheme = "green_hdpe"
    bin_top_width: float = 0.60
    bin_top_depth: float = 0.72
    bin_height: float = 0.86
    wall_thickness: float = 0.030
    taper: float = 0.08
    wheel_radius: float = 0.115
    wheel_width: float = 0.055
    lid_hinge_upper: float = 1.75
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["green_hdpe"])
    )


@dataclass(frozen=True)
class ResolvedWheelieBinWithHingedLidConfig:
    body_shell_module: BodyShell
    lid_module: LidModule
    wheel_pair_module: WheelPair
    wheel_axle_topology_module: AxleTopology
    hinge_interface_module: HingeInterface
    lid_extras_module: LidExtras
    palette_theme: PaletteTheme
    bin_top_width: float
    bin_top_depth: float
    bin_height: float
    wall_thickness: float
    taper: float
    wheel_radius: float
    wheel_width: float
    wheel_track: float
    axle_y: float
    axle_z: float
    hinge_xyz: tuple[float, float, float]
    lid_hinge_upper: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, 1.57079632679, 0.0)


def config_from_seed(seed: int) -> WheelieBinWithHingedLidConfig:
    if seed == 0:
        return WheelieBinWithHingedLidConfig(
            body_shell_module="prim_box_walls",
            lid_module="box_panel_skirt",
            wheel_pair_module="param_tire_wheel",
            wheel_axle_topology_module="wheels_on_body",
            hinge_interface_module="baked_knuckle_plus_pin",
            lid_extras_module="front_grip_lip",
        )
    rng = random.Random(seed)
    return WheelieBinWithHingedLidConfig(
        body_shell_module=rng.choice(BODY_MODULES),  # type: ignore[arg-type]
        lid_module=rng.choice(LID_MODULES),  # type: ignore[arg-type]
        wheel_pair_module=rng.choice(WHEEL_MODULES),  # type: ignore[arg-type]
        wheel_axle_topology_module=rng.choice(AXLE_MODULES),  # type: ignore[arg-type]
        hinge_interface_module=rng.choice(HINGE_MODULES),  # type: ignore[arg-type]
        lid_extras_module=rng.choice(EXTRA_MODULES),  # type: ignore[arg-type]
        palette_theme=rng.choice(tuple(PALETTES.keys())),  # type: ignore[arg-type]
        bin_top_width=rng.uniform(0.55, 0.66),
        bin_top_depth=rng.uniform(0.66, 0.78),
        bin_height=rng.uniform(0.80, 0.92),
        taper=rng.uniform(0.0, 0.16),
        wheel_radius=rng.uniform(0.090, 0.150),
        wheel_width=rng.uniform(0.045, 0.070),
        lid_hinge_upper=rng.uniform(1.35, 2.20),
    )


def resolve_config(config: WheelieBinWithHingedLidConfig) -> ResolvedWheelieBinWithHingedLidConfig:
    body = config.body_shell_module or "prim_box_walls"
    lid = config.lid_module or "box_panel_skirt"
    wheel = config.wheel_pair_module or "param_tire_wheel"
    axle = config.wheel_axle_topology_module or "wheels_on_body"
    hinge = config.hinge_interface_module or "baked_knuckle_plus_pin"
    extra = config.lid_extras_module or "front_grip_lip"
    for value, pool, label in (
        (body, BODY_MODULES, "body_shell_module"),
        (lid, LID_MODULES, "lid_module"),
        (wheel, WHEEL_MODULES, "wheel_pair_module"),
        (axle, AXLE_MODULES, "wheel_axle_topology_module"),
        (hinge, HINGE_MODULES, "hinge_interface_module"),
        (extra, EXTRA_MODULES, "lid_extras_module"),
    ):
        if value not in pool:
            raise ValueError(f"Unsupported {label}: {value!r}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")
    width = _clamp(config.bin_top_width, 0.55, 0.66)
    depth = _clamp(config.bin_top_depth, 0.66, 0.78)
    height = _clamp(config.bin_height, 0.80, 0.92)
    wheel_radius = _clamp(config.wheel_radius, 0.085, 0.160)
    wheel_width = _clamp(config.wheel_width, 0.040, 0.075)
    axle_y = -depth * 0.42
    axle_z = wheel_radius
    return ResolvedWheelieBinWithHingedLidConfig(
        body_shell_module=body,
        lid_module=lid,
        wheel_pair_module=wheel,
        wheel_axle_topology_module=axle,
        hinge_interface_module=hinge,
        lid_extras_module=extra,
        palette_theme=config.palette_theme,
        bin_top_width=width,
        bin_top_depth=depth,
        bin_height=height,
        wall_thickness=_clamp(config.wall_thickness, 0.018, 0.040),
        taper=_clamp(config.taper, 0.0, 0.16),
        wheel_radius=wheel_radius,
        wheel_width=wheel_width,
        wheel_track=width + 1.35 * wheel_width,
        axle_y=axle_y,
        axle_z=axle_z,
        hinge_xyz=(0.0, -depth * 0.52, height + 0.018),
        lid_hinge_upper=_clamp(config.lid_hinge_upper, 1.35, 2.20),
        palette=dict(PALETTES[config.palette_theme]),
    )


def _build_body(model: ArticulatedObject, r: ResolvedWheelieBinWithHingedLidConfig) -> None:
    w, d, h, t = r.bin_top_width, r.bin_top_depth, r.bin_height, r.wall_thickness
    body = model.part("body")
    # The side walls are full-height vertical boxes with inner faces at
    # +-(w/2 - t) / +-(d/2 - t). Clamp the (tapered) floor footprint so its
    # edges always overlap those inner faces by ~half a wall thickness; a larger
    # taper would otherwise float the floor as a disconnected island.
    bottom_w = max(w - r.taper, w - 2.0 * t + 0.01)
    bottom_d = max(d - r.taper, d - 2.0 * t + 0.01)
    body.visual(
        Box((bottom_w, bottom_d, t)),
        origin=Origin(xyz=(0.0, 0.0, t * 0.5)),
        material="body",
        name="floor", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((w, t, h)),
        origin=Origin(xyz=(0.0, d * 0.5 - t * 0.5, h * 0.5)),
        material="body",
        name="front_wall", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((w, t, h)),
        origin=Origin(xyz=(0.0, -d * 0.5 + t * 0.5, h * 0.5)),
        material="body",
        name="rear_wall", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((t, d, h)),
        origin=Origin(xyz=(w * 0.5 - t * 0.5, 0.0, h * 0.5)),
        material="body",
        name="right_wall", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((t, d, h)),
        origin=Origin(xyz=(-w * 0.5 + t * 0.5, 0.0, h * 0.5)),
        material="body",
        name="left_wall", material_class_id="plastic.opaque_glossy_molded",
    )
    rim_h = t * (1.2 if r.body_shell_module != "prim_box_walls" else 1.0)
    body.visual(
        Box((w + 0.035, t, rim_h)),
        origin=Origin(xyz=(0.0, d * 0.5, h + rim_h * 0.20)),
        material="body",
        name="front_rim", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((w + 0.035, t, rim_h)),
        origin=Origin(xyz=(0.0, -d * 0.5, h + rim_h * 0.20)),
        material="body",
        name="rear_rim", material_class_id="plastic.opaque_glossy_molded",
    )
    for x, name in ((w * 0.5, "right_rim"), (-w * 0.5, "left_rim")):
        body.visual(
            Box((t, d + 0.035, rim_h)),
            origin=Origin(xyz=(x, 0.0, h + rim_h * 0.20)),
            material="body",
            name=name, material_class_id="plastic.opaque_glossy_molded",
        )
    for x, suffix in ((r.wheel_track * 0.5, "right"), (-r.wheel_track * 0.5, "left")):
        body.visual(
            Cylinder(radius=r.wheel_radius * 0.25, length=r.wheel_width * 1.4),
            origin=Origin(xyz=(x, r.axle_y, r.axle_z), rpy=_cyl_x()),
            material="dark",
            name=f"{suffix}_axle_pod", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Box((0.055, 0.050, 0.070)),
            origin=Origin(xyz=(x * 0.92, r.axle_y, r.axle_z + 0.015)),
            material="body",
            name=f"{suffix}_axle_bracket", material_class_id="plastic.opaque_glossy_molded",
        )
    body.visual(
        Cylinder(radius=0.014, length=r.bin_top_width + 0.08),
        origin=Origin(xyz=r.hinge_xyz, rpy=_cyl_x()),
        material="steel",
        name="baked_hinge_pin", material_class_id="metal.steel_bare",
    )
    if r.hinge_interface_module == "cheek_bracket_frame":
        for x in (-w * 0.43, w * 0.43):
            body.visual(
                Box((0.045, 0.060, 0.080)),
                origin=Origin(xyz=(x, -d * 0.52, h + 0.020)),
                material="body",
                name=f"hinge_cheek_{x:+.2f}", material_class_id="plastic.opaque_glossy_molded",
            )


def _build_lid(model: ArticulatedObject, r: ResolvedWheelieBinWithHingedLidConfig) -> None:
    w, d, t = r.bin_top_width + 0.055, r.bin_top_depth + 0.055, 0.040
    lid = model.part("lid")
    lid.visual(
        Cylinder(radius=0.020, length=w, origin_axis_hint=None)
        if False
        else Cylinder(radius=0.020, length=w),
        origin=Origin(rpy=_cyl_x()),
        material="steel",
        name="lid_hinge_bar", material_class_id="metal.steel_bare",
    )
    lid.visual(
        Box((w, d, t)), origin=Origin(xyz=(0.0, d * 0.50, 0.018)), material="lid", name="lid_panel", material_class_id="plastic.opaque_glossy_molded"
    )
    if r.lid_module == "box_panel_skirt":
        lid.visual(
            Box((w, 0.035, 0.045)),
            origin=Origin(xyz=(0.0, d - 0.025, -0.010)),
            material="lid",
            name="front_skirt", material_class_id="plastic.opaque_glossy_molded",
        )
        lid.visual(
            Box((w * 0.62, 0.025, 0.030)),
            origin=Origin(xyz=(0.0, d * 0.62, 0.048)),
            material="lid",
            name="center_stiffener", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.lid_module == "extrude_rrect_panel":
        for i, y in enumerate((d * 0.28, d * 0.48, d * 0.68)):
            lid.visual(
                # z=0.044 so the rib underside (0.034) embeds into the lid panel
                # top (0.038); at 0.050 the ribs floated as disconnected islands.
                Box((w * 0.76, 0.018, 0.020)),
                origin=Origin(xyz=(0.0, y, 0.044)),
                material="lid",
                name=f"top_rib_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
    else:
        lid.visual(
            Box((w * 0.92, 0.028, 0.026)),
            origin=Origin(xyz=(0.0, d * 0.84, 0.045)),
            material="lid",
            name="filleted_front_lip", material_class_id="plastic.opaque_glossy_molded",
        )
    if r.lid_extras_module == "front_grip_lip":
        lid.visual(
            Box((w * 0.46, 0.035, 0.026)),
            origin=Origin(xyz=(0.0, d + 0.010, 0.020)),
            material="dark",
            name="front_grip_lip", material_class_id="plastic.opaque_glossy_molded",
        )


def _build_wheel(
    model: ArticulatedObject, name: str, r: ResolvedWheelieBinWithHingedLidConfig
) -> None:
    wheel = model.part(name)
    rw, ww = r.wheel_radius, r.wheel_width
    wheel.visual(
        Cylinder(radius=rw, length=ww), origin=Origin(rpy=_cyl_x()), material="dark", name="tire", material_class_id="rubber.smooth_plain"
    )
    wheel.visual(
        Cylinder(radius=rw * 0.55, length=ww * 1.10),
        origin=Origin(rpy=_cyl_x()),
        material="steel",
        name="rim", material_class_id="metal.steel_bare",
    )
    wheel.visual(
        Cylinder(radius=rw * 0.25, length=ww * 1.30),
        origin=Origin(rpy=_cyl_x()),
        material="body",
        name="hub_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    if r.wheel_pair_module == "param_tire_wheel":
        for z, suffix in ((rw * 0.62, "top"), (-rw * 0.62, "bottom")):
            wheel.visual(
                Box((ww * 0.85, rw * 0.20, rw * 0.10)),
                origin=Origin(xyz=(0.0, 0.0, z)),
                material="dark",
                name=f"tread_{suffix}", material_class_id="rubber.directional_grooved",
            )
    elif r.wheel_pair_module == "lathe_profile_wheel":
        wheel.visual(
            Cylinder(radius=rw * 0.78, length=ww * 0.32),
            origin=Origin(rpy=_cyl_x()),
            material="dark",
            name="rounded_sidewall", material_class_id="rubber.smooth_plain",
        )


def _add_lock_tab(model: ArticulatedObject, r: ResolvedWheelieBinWithHingedLidConfig) -> None:
    tab = model.part("lock_tab")
    tab.visual(
        Cylinder(radius=0.020, length=0.11),
        origin=Origin(rpy=_cyl_x()),
        material="steel",
        name="lock_barrel", material_class_id="metal.steel_bare",
    )
    tab.visual(
        Box((0.080, 0.030, 0.090)),
        origin=Origin(xyz=(0.0, 0.020, -0.040)),
        material="dark",
        name="lock_plate", material_class_id="plastic.opaque_glossy_molded",
    )
    tab.visual(
        Box((0.060, 0.020, 0.026)),
        origin=Origin(xyz=(0.0, 0.045, -0.086)),
        material="lid",
        name="pull_tab", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "body_to_lock_tab",
        ArticulationType.REVOLUTE,
        parent=model.get_part("body"),
        child=tab,
        origin=Origin(xyz=(0.0, r.bin_top_depth * 0.52, r.bin_height + 0.005)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=-0.35, upper=1.30),
    )


def build_wheelie_bin_with_hinged_lid(
    config: WheelieBinWithHingedLidConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="wheelie_bin_with_hinged_lid", assets=assets)
    for material, rgba in r.palette.items():
        model.material(material, rgba=rgba)
    _build_body(model, r)
    _build_lid(model, r)
    body = model.get_part("body")
    lid = model.get_part("lid")
    model.articulation(
        "body_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=r.hinge_xyz),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=18.0, velocity=1.6, lower=0.0, upper=r.lid_hinge_upper),
    )
    wheel_parent_name = "body"
    if r.wheel_axle_topology_module == "fixed_axle_part":
        axle = model.part("axle")
        axle.visual(
            Cylinder(radius=0.018, length=r.wheel_track + r.wheel_width),
            origin=Origin(rpy=_cyl_x()),
            material="steel",
            name="axle_shaft", material_class_id="metal.steel_bare",
        )
        axle.visual(
            Box((0.10, 0.050, 0.045)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="steel",
            name="axle_mount", material_class_id="metal.steel_bare",
        )
        # Central axle-mount rib on the BODY, spanning from the rear wall out to
        # the axle centerline so the FIXED body->axle weld origin sits on real
        # body geometry (parent side) while staying connected to the rear wall.
        y_back = -r.bin_top_depth * 0.5
        y_front = r.axle_y + 0.03
        body.visual(
            Box((0.09, y_front - y_back, 0.07)),
            origin=Origin(xyz=(0.0, 0.5 * (y_back + y_front), r.axle_z)),
            material="body",
            name="axle_mount_rib", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            "body_to_axle",
            ArticulationType.FIXED,
            parent=body,
            child=axle,
            origin=Origin(xyz=(0.0, r.axle_y, r.axle_z)),
        )
        wheel_parent_name = "axle"
    if r.hinge_interface_module == "separate_hinge_pin_part":
        pin = model.part("hinge_pin")
        pin.visual(
            Cylinder(radius=0.012, length=r.bin_top_width + 0.10),
            origin=Origin(rpy=_cyl_x()),
            material="steel",
            name="hinge_pin_rod", material_class_id="metal.steel_bare",
        )
        pin.visual(
            Cylinder(radius=0.020, length=0.020),
            origin=Origin(xyz=(r.bin_top_width * 0.5 + 0.05, 0.0, 0.0), rpy=_cyl_x()),
            material="steel",
            name="right_cap", material_class_id="metal.steel_bare",
        )
        pin.visual(
            Cylinder(radius=0.020, length=0.020),
            origin=Origin(xyz=(-r.bin_top_width * 0.5 - 0.05, 0.0, 0.0), rpy=_cyl_x()),
            material="steel",
            name="left_cap", material_class_id="metal.steel_bare",
        )
        model.articulation(
            "body_to_hinge_pin",
            ArticulationType.FIXED,
            parent=body,
            child=pin,
            origin=Origin(xyz=r.hinge_xyz),
        )
    for side, x in (("left", -r.wheel_track * 0.5), ("right", r.wheel_track * 0.5)):
        _build_wheel(model, f"{side}_wheel", r)
        parent = model.get_part(wheel_parent_name)
        origin = (x, 0.0, 0.0) if wheel_parent_name == "axle" else (x, r.axle_y, r.axle_z)
        model.articulation(
            f"{wheel_parent_name}_to_{side}_wheel",
            ArticulationType.CONTINUOUS,
            parent=parent,
            child=model.get_part(f"{side}_wheel"),
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=20.0),
        )
    if r.lid_extras_module == "lock_tab_latch":
        _add_lock_tab(model, r)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_wheelie_bin_with_hinged_lid(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_wheelie_bin_with_hinged_lid(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedWheelieBinWithHingedLidConfig) -> list[tuple[str, str]]:
    return [
        ("body_shell", r.body_shell_module),
        ("lid", r.lid_module),
        ("wheel_pair", r.wheel_pair_module),
        ("wheel_axle_topology", r.wheel_axle_topology_module),
        ("hinge_interface", r.hinge_interface_module),
        ("lid_extras", r.lid_extras_module),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def run_wheelie_bin_with_hinged_lid_tests(
    object_model: ArticulatedObject, config: WheelieBinWithHingedLidConfig
) -> TestReport:
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}
    ctx.check("body_present", "body" in names)
    ctx.check("lid_present", "lid" in names)
    ctx.check("two_wheels", {"left_wheel", "right_wheel"}.issubset(names))
    ctx.check(
        "lid_hinge_revolute", joints["body_to_lid"].articulation_type == ArticulationType.REVOLUTE
    )
    ctx.check("lid_axis_widthwise", joints["body_to_lid"].axis == (1.0, 0.0, 0.0))
    wheel_joints = [
        j for j in object_model.articulations if j.child in {"left_wheel", "right_wheel"}
    ]
    ctx.check(
        "two_continuous_wheel_joints",
        len(wheel_joints) == 2
        and all(j.articulation_type == ArticulationType.CONTINUOUS for j in wheel_joints),
    )
    for other in ("lid", "left_wheel", "right_wheel", "axle", "hinge_pin", "lock_tab"):
        if other in names:
            ctx.allow_overlap(
                object_model.get_part("body"),
                object_model.get_part(other),
                reason="Wheelie-bin hinge, axle, latch, and wheel hardware are captured by molded body features.",
            )
    if "axle" in names:
        for wheel in ("left_wheel", "right_wheel"):
            ctx.allow_overlap(
                object_model.get_part("axle"),
                object_model.get_part(wheel),
                reason="Wheel hub rotates around the fixed axle spindle.",
            )
    if "hinge_pin" in names:
        ctx.allow_overlap(
            object_model.get_part("hinge_pin"),
            object_model.get_part("lid"),
            reason="Lid knuckle wraps around the full-width hinge pin.",
        )
    if "lock_tab" in names:
        ctx.allow_overlap(
            object_model.get_part("lid"),
            object_model.get_part("lock_tab"),
            reason="Closed latch barrel intentionally tucks under the lid front lip.",
        )
    return ctx.report()


__all__ = [
    "__modular__",
    "WheelieBinWithHingedLidConfig",
    "ResolvedWheelieBinWithHingedLidConfig",
    "config_from_seed",
    "resolve_config",
    "build_wheelie_bin_with_hinged_lid",
    "build_seeded_wheelie_bin_with_hinged_lid",
    "slot_choices_for_seed",
    "run_wheelie_bin_with_hinged_lid_tests",
]
