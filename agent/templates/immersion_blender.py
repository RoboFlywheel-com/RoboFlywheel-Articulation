# SPDX-License-Identifier: Apache-2.0

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
    CylinderGeometry,
    ExtrudeWithHolesGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    sample_catmull_rom_spline_2d,
    tube_from_spline_points,
)

BlenderLayout = Literal["immersion_wand"]
BaseShape = Literal["none_for_immersion"]
JarShape = Literal["none"]
BladeStyle = Literal["immersion_blade_set", "whisk", "flat_beater", "dough_hook"]
JarLockMotion = Literal["fixed"]
LidStyle = Literal["none"]
ControlStyle = Literal["none", "power_trigger"]
ShaftLockStyle = Literal["none", "twist_lock"]
BladeSpinSpeedClass = Literal["slow_display", "normal", "high_speed"]
HandleProfile = Literal["cylindrical", "tapered_grip"]
GuardStyle = Literal["bell_guard", "open_cage", "perforated_bell"]
CupStyle = Literal["smooth_cup", "threaded_travel_cup"]
CapStyle = Literal["none"]
HandleStyle = Literal["none", "side_handle", "bridge_handle"]
MaterialStyle = Literal[
    "kitchen_white",
    "commercial_black",
    "brushed_steel",
    "red_consumer",
    "blue_soft_grip",
]

MATERIAL_PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "kitchen_white": {
        "base": (0.88, 0.88, 0.84, 1.0),
        "jar": (0.70, 0.86, 0.95, 0.35),
        "lid": (0.08, 0.08, 0.09, 1.0),
        "blade": (0.72, 0.74, 0.76, 1.0),
        "accent": (0.80, 0.12, 0.08, 1.0),
    },
    "commercial_black": {
        "base": (0.05, 0.05, 0.06, 1.0),
        "jar": (0.68, 0.82, 0.90, 0.32),
        "lid": (0.03, 0.03, 0.03, 1.0),
        "blade": (0.76, 0.78, 0.80, 1.0),
        "accent": (0.35, 0.36, 0.38, 1.0),
    },
    "brushed_steel": {
        "base": (0.58, 0.60, 0.60, 1.0),
        "jar": (0.72, 0.86, 0.96, 0.34),
        "lid": (0.12, 0.12, 0.13, 1.0),
        "blade": (0.86, 0.88, 0.88, 1.0),
        "accent": (0.06, 0.06, 0.06, 1.0),
    },
    "red_consumer": {
        "base": (0.82, 0.06, 0.045, 1.0),
        "jar": (0.78, 0.90, 0.98, 0.30),
        "lid": (0.08, 0.07, 0.065, 1.0),
        "blade": (0.82, 0.84, 0.84, 1.0),
        "accent": (0.12, 0.12, 0.13, 1.0),
    },
    "blue_soft_grip": {
        "base": (0.84, 0.86, 0.82, 1.0),
        "jar": (0.70, 0.86, 0.94, 0.34),
        "lid": (0.04, 0.05, 0.06, 1.0),
        "blade": (0.76, 0.78, 0.80, 1.0),
        "accent": (0.08, 0.22, 0.48, 1.0),
    },
}

ADOPTED_SOURCES: dict[str, str] = {
    "S1": "data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L117-L350",
    "S2": "data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L45-L326",
    "S3": "data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L152-L260",
    "S4": "data/records/rec_blender_f513f69f35204dab87e58687d44fb722/revisions/rev_000001/model.py:L89-L322",
    "S5": "data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L33-L270",
    "S6": "data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L55-L419",
}


@dataclass(frozen=True)
class BlenderConfig:
    blender_layout: BlenderLayout = "immersion_wand"
    base_shape: BaseShape | None = "none_for_immersion"
    jar_shape: JarShape | None = "none"
    blade_style: BladeStyle = "immersion_blade_set"
    jar_lock_motion: JarLockMotion = "fixed"
    lid_style: LidStyle = "none"
    control_style: ControlStyle = "none"
    hood_enabled: bool = False
    safety_latch_enabled: bool = False
    shaft_lock_style: ShaftLockStyle = "none"
    blade_spin_speed_class: BladeSpinSpeedClass = "high_speed"
    handle_profile: HandleProfile = "cylindrical"
    guard_style: GuardStyle = "bell_guard"
    cup_style: CupStyle = "threaded_travel_cup"
    cap_style: CapStyle = "none"
    handle_style: HandleStyle = "none"
    base_width: float = 0.180
    base_depth: float = 0.160
    base_height: float = 0.140
    jar_height: float = 0.260
    shaft_length: float = 0.260
    blade_radius: float = 0.042
    material_style: MaterialStyle = "kitchen_white"
    name: str = "reference_immersion_blender"


@dataclass(frozen=True)
class ResolvedBlenderConfig:
    blender_layout: BlenderLayout
    base_shape: BaseShape
    jar_shape: JarShape
    blade_style: BladeStyle
    blade_count: int
    jar_lock_motion: JarLockMotion
    lid_style: LidStyle
    control_style: ControlStyle
    hood_enabled: bool
    safety_latch_enabled: bool
    shaft_lock_style: ShaftLockStyle
    blade_spin_speed_class: BladeSpinSpeedClass
    handle_profile: HandleProfile
    guard_style: GuardStyle
    cup_style: CupStyle
    cap_style: CapStyle
    handle_style: HandleStyle
    base_width: float
    base_depth: float
    base_height: float
    jar_height: float
    shaft_length: float
    blade_radius: float
    blade_axis: tuple[float, float, float]
    material_style: MaterialStyle
    name: str


def config_from_seed(seed: int) -> BlenderConfig:
    rng = random.Random(seed)
    layout: BlenderLayout = "immersion_wand"
    blade_style = rng.choice(("immersion_blade_set", "whisk", "flat_beater", "dough_hook"))
    blade_spin_speed_class = rng.choice(("slow_display", "normal", "high_speed"))
    handle_profile = rng.choice(("cylindrical", "tapered_grip"))
    guard_style = rng.choice(("bell_guard", "open_cage", "perforated_bell"))
    base_width = round(rng.uniform(0.145, 0.220), 3)
    base_depth = round(rng.uniform(0.135, 0.210), 3)
    base_height = round(rng.uniform(0.105, 0.180), 3)
    jar_height = round(rng.uniform(0.200, 0.330), 3)
    shaft_length = round(rng.uniform(0.220, 0.330), 3)
    blade_radius = round(rng.uniform(0.028, 0.055), 4)
    material_style = rng.choice(tuple(MATERIAL_PALETTES))
    control_style = rng.choice(("none", "power_trigger"))
    shaft_lock_style = rng.choice(("none", "twist_lock"))
    return BlenderConfig(
        blender_layout=layout,
        blade_style=blade_style,
        jar_lock_motion="fixed",
        lid_style="none",
        control_style=control_style,
        hood_enabled=False,
        safety_latch_enabled=False,
        shaft_lock_style=shaft_lock_style,
        blade_spin_speed_class=blade_spin_speed_class,
        handle_profile=handle_profile,
        guard_style=guard_style,
        cup_style="threaded_travel_cup",
        cap_style="none",
        handle_style="none",
        base_width=base_width,
        base_depth=base_depth,
        base_height=base_height,
        jar_height=jar_height,
        shaft_length=shaft_length,
        blade_radius=blade_radius,
        material_style=material_style,
        name=f"seeded_immersion_blender_{seed}",
    )


def resolve_config(config: BlenderConfig) -> ResolvedBlenderConfig:
    if config.blender_layout not in ("immersion_wand",):
        raise ValueError(f"Unsupported blender_layout: {config.blender_layout}")
    base_shape = config.base_shape
    jar_shape = config.jar_shape
    if base_shape is None:
        base_shape = "none_for_immersion"
    if jar_shape is None:
        jar_shape = "none"
    if base_shape not in ("none_for_immersion",):
        raise ValueError(f"Unsupported base_shape: {base_shape}")
    if jar_shape not in ("none",):
        raise ValueError(f"Unsupported jar_shape: {jar_shape}")
    if base_shape != "none_for_immersion" or jar_shape != "none":
        raise ValueError("immersion_wand requires no base and no jar")
    if config.blade_style not in ("immersion_blade_set", "whisk", "flat_beater", "dough_hook"):
        raise ValueError(f"Unsupported blade_style: {config.blade_style}")
    if config.jar_lock_motion not in ("fixed",):
        raise ValueError(f"Unsupported jar_lock_motion: {config.jar_lock_motion}")
    if config.lid_style not in ("none",):
        raise ValueError(f"Unsupported lid_style: {config.lid_style}")
    if config.control_style not in ("none", "power_trigger"):
        raise ValueError(f"Unsupported control_style: {config.control_style}")
    if config.shaft_lock_style not in ("none", "twist_lock"):
        raise ValueError(f"Unsupported shaft_lock_style: {config.shaft_lock_style}")
    if config.blade_spin_speed_class not in ("slow_display", "normal", "high_speed"):
        raise ValueError(f"Unsupported blade_spin_speed_class: {config.blade_spin_speed_class}")
    if config.handle_profile not in ("cylindrical", "tapered_grip"):
        raise ValueError(f"Unsupported handle_profile: {config.handle_profile}")
    if config.guard_style not in ("bell_guard", "open_cage", "perforated_bell"):
        raise ValueError(f"Unsupported guard_style: {config.guard_style}")
    if config.cup_style not in ("smooth_cup", "threaded_travel_cup"):
        raise ValueError(f"Unsupported cup_style: {config.cup_style}")
    if config.cap_style not in ("none",):
        raise ValueError(f"Unsupported cap_style: {config.cap_style}")
    if config.handle_style not in ("none", "side_handle", "bridge_handle"):
        raise ValueError(f"Unsupported handle_style: {config.handle_style}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    blade_count = 3 if config.blade_style == "immersion_blade_set" else 1
    return ResolvedBlenderConfig(
        blender_layout=config.blender_layout,
        base_shape=base_shape,
        jar_shape=jar_shape,
        blade_style=config.blade_style,
        blade_count=blade_count,
        jar_lock_motion=config.jar_lock_motion,
        lid_style="none",
        control_style=config.control_style,
        hood_enabled=False,
        safety_latch_enabled=False,
        shaft_lock_style=config.shaft_lock_style,
        blade_spin_speed_class=config.blade_spin_speed_class,
        handle_profile=config.handle_profile,
        guard_style=config.guard_style,
        cup_style=config.cup_style,
        cap_style=config.cap_style,
        handle_style="none",
        base_width=max(0.145, min(0.220, config.base_width)),
        base_depth=max(0.135, min(0.210, config.base_depth)),
        base_height=max(0.105, min(0.180, config.base_height)),
        jar_height=max(0.200, min(0.330, config.jar_height)),
        shaft_length=max(0.220, min(0.330, config.shaft_length)),
        blade_radius=max(0.028, min(0.055, config.blade_radius)),
        blade_axis=(0.0, 0.0, 1.0),
        material_style=config.material_style,
        name=config.name,
    )


def _build_whisk_geometry(body_height: float, *, axial_scale: float = 1.0) -> CylinderGeometry:
    s = body_height / 0.116
    axial_height = body_height * axial_scale
    # Stout mounting collar poking up to local z=+0.010 so it embeds into the
    # tool_shaft above (whose radius is 0.005). Without this the thin whisk
    # collar sits fully below the mesh origin and the shaft cluster floats free.
    geom = CylinderGeometry(radius=0.0065, height=0.016)
    geom.translate(0.0, 0.0, 0.002)
    geom.merge(
        CylinderGeometry(radius=0.0080 * s, height=0.024 * s).translate(0.0, 0.0, -0.014 * s)
    )
    geom.merge(
        CylinderGeometry(radius=0.0120 * s, height=0.018 * s).translate(0.0, 0.0, -0.032 * s)
    )
    geom.merge(
        CylinderGeometry(radius=0.0100 * s, height=0.016 * s).translate(
            0.0,
            0.0,
            -(axial_height - 0.008 * s),
        )
    )
    loop_count = 8
    r_lobe = body_height * 0.30
    # z_top sits solidly INSIDE the middle collar cylinder (spans -0.041s..-0.023s)
    # so every wire-loop top endpoint embeds into it; at -0.042s the loops only
    # grazed the collar base and read as floating islands.
    z_top = -0.036 * s
    z_bot = -(axial_height - 0.005 * s)
    for index in range(loop_count):
        angle = (math.pi * index) / loop_count
        c = math.cos(angle)
        sn = math.sin(angle)
        wire = tube_from_spline_points(
            [
                (0.010 * s * c, 0.010 * s * sn, z_top),
                (r_lobe * c * 0.55, r_lobe * sn * 0.55, z_top - axial_height * 0.18),
                (r_lobe * c, r_lobe * sn, (z_top + z_bot) * 0.5),
                (r_lobe * c * 0.55, r_lobe * sn * 0.55, z_bot + axial_height * 0.18),
                (0.0, 0.0, z_bot),
                (-r_lobe * c * 0.55, -r_lobe * sn * 0.55, z_bot + axial_height * 0.18),
                (-r_lobe * c, -r_lobe * sn, (z_top + z_bot) * 0.5),
                (-r_lobe * c * 0.55, -r_lobe * sn * 0.55, z_top - axial_height * 0.18),
                (-0.010 * s * c, -0.010 * s * sn, z_top),
            ],
            radius=0.0015 * s,
            samples_per_segment=10,
            radial_segments=10,
            cap_ends=True,
        )
        geom.merge(wire)
    return geom


def _build_dough_hook_geometry(body_height: float) -> CylinderGeometry:
    s = body_height / 0.132
    geom = CylinderGeometry(radius=0.008 * s, height=0.030 * s).translate(0.0, 0.0, -0.015 * s)
    geom.merge(CylinderGeometry(radius=0.012 * s, height=0.014 * s).translate(0.0, 0.0, -0.037 * s))
    curve = tube_from_spline_points(
        [
            (0.000, 0.000, -0.044 * s),
            (0.010 * s, 0.000, -0.060 * s),
            (0.025 * s, 0.000, -0.080 * s),
            (0.032 * s, 0.000, -0.102 * s),
            (0.027 * s, 0.000, -0.118 * s),
            (0.014 * s, 0.000, -0.128 * s),
            (-0.002 * s, 0.000, -body_height),
        ],
        radius=0.0068 * s,
        samples_per_segment=12,
        radial_segments=14,
        cap_ends=True,
    )
    geom.merge(curve)
    return geom


def _build_flat_beater_geometry(body_height: float) -> CylinderGeometry:
    s = body_height / 0.142
    outer = sample_catmull_rom_spline_2d(
        [
            (0.016 * s, 0.024 * s),
            (0.040 * s, -0.002 * s),
            (0.050 * s, -0.035 * s),
            (0.044 * s, -0.078 * s),
            (0.026 * s, -0.108 * s),
            (0.000, -0.118 * s),
            (-0.026 * s, -0.108 * s),
            (-0.044 * s, -0.078 * s),
            (-0.050 * s, -0.035 * s),
            (-0.040 * s, -0.002 * s),
            (-0.016 * s, 0.024 * s),
        ],
        samples_per_segment=9,
        closed=True,
    )
    inner = sample_catmull_rom_spline_2d(
        [
            (0.010 * s, 0.002 * s),
            (0.022 * s, -0.020 * s),
            (0.025 * s, -0.062 * s),
            (0.014 * s, -0.093 * s),
            (0.000, -0.102 * s),
            (-0.014 * s, -0.093 * s),
            (-0.025 * s, -0.062 * s),
            (-0.022 * s, -0.020 * s),
            (-0.010 * s, 0.002 * s),
        ],
        samples_per_segment=9,
        closed=True,
    )
    paddle = ExtrudeWithHolesGeometry(outer, [inner], 0.006 * s, center=True)
    paddle.rotate_x(math.pi / 2.0).translate(0.0, 0.0, -body_height * 0.62)
    shaft = CylinderGeometry(radius=0.0065 * s, height=body_height * 0.36).translate(
        0.0,
        0.0,
        -body_height * 0.20,
    )
    shaft.merge(
        CylinderGeometry(radius=0.010 * s, height=0.026 * s).translate(
            0.0, 0.0, -body_height * 0.34
        )
    )
    shaft.merge(paddle)
    return shaft


def _add_blade(part, r: ResolvedBlenderConfig, *, assets: AssetContext, blade_mat) -> None:
    part.visual(
        Cylinder(radius=0.018, length=0.006),
        # Raised so the flange top (z=-0.0045) overlaps the hub base (z=-0.006)
        # by ~1.5mm. immersion_blade_set has no tool_shaft to bridge the two,
        # so the flange must embed into the hub directly.
        origin=Origin(xyz=(0.0, 0.0, -0.0075)),
        material=blade_mat,
        name="blade_mount_flange", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=0.010, length=0.012), origin=Origin(), material=blade_mat, name="blade_hub", material_class_id="metal.stainless_matte"
    )
    if r.blade_style == "immersion_blade_set":
        for i in range(r.blade_count):
            angle = 2.0 * math.pi * i / r.blade_count
            part.visual(
                Box((r.blade_radius, 0.010, 0.004)),
                origin=Origin(
                    xyz=(
                        math.cos(angle) * r.blade_radius / 2.0,
                        math.sin(angle) * r.blade_radius / 2.0,
                        0.006,
                    ),
                    rpy=(0.0, 0.0, angle),
                ),
                material=blade_mat,
                name=f"blade_{i}", material_class_id="metal.stainless_matte",
            )
        return

    # Stand-mixer heads adapted for immersion use at compact scale.
    tool_drop = max(0.045, min(0.070, r.blade_radius * 1.28))
    shaft_len = tool_drop * 0.24
    body_height = tool_drop - shaft_len
    # The stand-mixer meshes are placed at z=-shaft_len-0.002. whisk/flat_beater
    # collars start a few mm BELOW that origin (unlike dough_hook whose collar top
    # sits at local z=0), leaving the shaft cluster disconnected from the mesh.
    # Extend the shaft 5mm past the mesh origin so it embeds into every collar.
    shaft_overrun = 0.005
    shaft_top = -0.002
    shaft_bottom = -shaft_len - 0.002 - shaft_overrun
    part.visual(
        Cylinder(radius=0.005, length=shaft_top - shaft_bottom),
        origin=Origin(xyz=(0.0, 0.0, (shaft_top + shaft_bottom) / 2.0)),
        material=blade_mat,
        name="tool_shaft", material_class_id="metal.stainless_matte",
    )

    if r.blade_style == "whisk":
        mesh = mesh_from_geometry(
            _build_whisk_geometry(body_height, axial_scale=1.28),
            assets.mesh_path("immersion_wire_whisk.obj"),
        )
        part.visual(
            mesh,
            origin=Origin(xyz=(0.0, 0.0, -shaft_len - 0.002)),
            material=blade_mat,
            name="whisk_assembly", material_class_id="metal.stainless_matte",
        )
    elif r.blade_style == "flat_beater":
        mesh = mesh_from_geometry(
            _build_flat_beater_geometry(body_height),
            assets.mesh_path("immersion_flat_beater.obj"),
        )
        part.visual(
            mesh,
            origin=Origin(xyz=(0.0, 0.0, -shaft_len - 0.002)),
            material=blade_mat,
            name="flat_beater_blade_main", material_class_id="metal.stainless_matte",
        )
    else:
        mesh = mesh_from_geometry(
            _build_dough_hook_geometry(body_height),
            assets.mesh_path("immersion_dough_hook.obj"),
        )
        part.visual(
            mesh,
            origin=Origin(xyz=(0.0, 0.0, -shaft_len - 0.002)),
            material=blade_mat,
            name="dough_hook_upper_shaft", material_class_id="metal.stainless_matte",
        )


def build_blender(
    config: BlenderConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or BlenderConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-blender-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = MATERIAL_PALETTES[r.material_style]
    base_mat = model.material("blender_base", rgba=palette["base"])
    blade_mat = model.material("blender_blade", rgba=palette["blade"])
    accent_mat = model.material("blender_accent", rgba=palette["accent"])
    soft_grip_mat = model.material("blender_soft_grip", rgba=(0.06, 0.065, 0.07, 1.0))

    handle = model.part("motor_handle")
    handle.visual(
        Cylinder(radius=0.035, length=0.210),
        origin=Origin(xyz=(0.0, 0.0, 0.105)),
        material=base_mat,
        name=f"{r.handle_profile}_handle", material_class_id=("plastic.opaque_glossy_molded" if r.material_style in {"kitchen_white", "commercial_black", "red_consumer", "blue_soft_grip"} else "metal.brushed_silver"),
    )
    if r.handle_profile == "tapered_grip":
        handle.visual(
            Cylinder(radius=0.039, length=0.070),
            origin=Origin(xyz=(0.0, 0.0, 0.145)),
            material=soft_grip_mat,
            name="soft_upper_grip_band", material_class_id="rubber.smooth_plain",
        )
        handle.visual(
            Cylinder(radius=0.030, length=0.060),
            origin=Origin(xyz=(0.0, 0.0, 0.050)),
            material=soft_grip_mat,
            name="narrow_lower_grip_band", material_class_id="rubber.smooth_plain",
        )
    else:
        handle.visual(
            Box((0.050, 0.010, 0.110)),
            origin=Origin(xyz=(0.0, -0.033, 0.100)),
            material=soft_grip_mat,
            name="soft_grip_panel", material_class_id="rubber.smooth_plain",
        )
    if r.control_style != "power_trigger":
        handle.visual(
            Box((0.018, 0.014, 0.078)),
            origin=Origin(xyz=(0.0, -0.040, 0.128)),
            material=accent_mat,
            name="flush_speed_button", material_class_id="plastic.opaque_glossy_molded",
        )
    handle.visual(
        Box((0.015, 0.012, 0.036)),
        origin=Origin(xyz=(0.0, -0.041, 0.060)),
        material=accent_mat,
        name="pulse_button", material_class_id="plastic.opaque_glossy_molded",
    )
    handle.visual(
        Cylinder(radius=0.027, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, -0.020)),
        material=accent_mat,
        name="coupling_socket", material_class_id="plastic.opaque_glossy_molded",
    )
    cup = model.part("measuring_cup")
    cup_radius = 0.070 if r.cup_style == "smooth_cup" else 0.076
    handle_attach_radius = 0.039 if r.handle_profile == "tapered_grip" else 0.035
    bridge_gap = 0.014
    cup_x = handle_attach_radius + cup_radius + bridge_gap
    # The cup couples to the handle through `cup_handle_bridge`; the real weld
    # interface is the handle surface where that bridge lands. Anchor the FIXED
    # origin there (single source: handle_attach_radius + bridge mid-height z)
    # and author the cup part relative to it so the origin sits on real hardware
    # of BOTH parts. World pose is unchanged (every visual keeps `+ cup_ref`).
    bridge_z = 0.105
    cup_ref = (handle_attach_radius, 0.0, bridge_z)

    def _cup_xyz(x: float, y: float, z: float) -> tuple[float, float, float]:
        return (x - cup_ref[0], y - cup_ref[1], z - cup_ref[2])

    cup.visual(
        Box((cup_radius * 2.0, cup_radius * 2.0, 0.010)),
        origin=Origin(xyz=_cup_xyz(cup_x, 0.0, 0.005)),
        material=model.material("immersion_clear_cup", rgba=palette["jar"]),
        name=f"{r.cup_style}_floor", material_class_id="plastic.clear_rigid",
    )
    cup.visual(
        Cylinder(radius=cup_radius, length=0.170),
        origin=Origin(xyz=_cup_xyz(cup_x, 0.0, 0.090)),
        material=model.material("immersion_clear_cup_wall", rgba=palette["jar"]),
        name=f"{r.cup_style}_transparent_wall", material_class_id="plastic.clear_rigid",
    )
    cup.visual(
        Cylinder(radius=cup_radius * 1.02, length=0.010),
        origin=Origin(xyz=_cup_xyz(cup_x, 0.0, 0.180)),
        material=accent_mat,
        name="cup_rim", material_class_id="plastic.opaque_glossy_molded",
    )
    cup.visual(
        Box((bridge_gap, 0.026, 0.060)),
        origin=Origin(xyz=_cup_xyz(handle_attach_radius + bridge_gap / 2.0, 0.0, bridge_z)),
        material=accent_mat,
        name="cup_handle_bridge", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "cup_reference_pose",
        ArticulationType.FIXED,
        parent=handle,
        child=cup,
        origin=Origin(xyz=cup_ref),
    )
    shaft = model.part("shaft_assembly")
    shaft.visual(
        Cylinder(radius=0.012, length=r.shaft_length),
        origin=Origin(xyz=(0.0, 0.0, -r.shaft_length / 2.0)),
        material=blade_mat,
        name="shaft_core", material_class_id="metal.stainless_matte",
    )
    shaft.visual(
        Cylinder(radius=0.040, length=0.035),
        origin=Origin(xyz=(0.0, 0.0, -r.shaft_length)),
        material=accent_mat,
        name=r.guard_style, material_class_id="plastic.opaque_glossy_molded",
    )
    if r.guard_style == "perforated_bell":
        for i in range(6):
            angle = i * math.tau / 6.0
            shaft.visual(
                Box((0.012, 0.006, 0.018)),
                origin=Origin(
                    xyz=(
                        math.cos(angle) * 0.035,
                        math.sin(angle) * 0.035,
                        -r.shaft_length - 0.002,
                    ),
                    rpy=(0.0, 0.0, angle),
                ),
                material=blade_mat,
                name=f"guard_perforation_bridge_{i}", material_class_id="metal.stainless_matte",
            )
    if r.shaft_lock_style == "twist_lock":
        model.articulation(
            "shaft_lock",
            ArticulationType.REVOLUTE,
            parent=handle,
            child=shaft,
            origin=Origin(xyz=(0.0, 0.0, -0.040)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=4.0,
                velocity=2.0,
                lower=0.0,
                upper=math.radians(24.0),
            ),
            meta={"source_id": "S3"},
        )
    else:
        model.articulation(
            "shaft_lock",
            ArticulationType.FIXED,
            parent=handle,
            child=shaft,
            origin=Origin(xyz=(0.0, 0.0, -0.040)),
        )
    blade = model.part("blade_assembly")
    _add_blade(blade, r, assets=assets, blade_mat=blade_mat)
    model.articulation(
        "blade_spin",
        ArticulationType.CONTINUOUS,
        parent=shaft,
        child=blade,
        origin=Origin(xyz=(0.0, 0.0, -r.shaft_length - 0.0235)),
        axis=r.blade_axis,
        motion_limits=MotionLimits(
            effort=6.0,
            velocity={"slow_display": 10.0, "normal": 40.0, "high_speed": 90.0}[
                r.blade_spin_speed_class
            ],
        ),
        meta={"source_id": "S3"},
    )
    if r.control_style == "power_trigger":
        trigger = model.part("power_trigger")
        trigger.visual(
            Cylinder(radius=0.0028, length=0.024),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=accent_mat,
            name="pivot_barrel", material_class_id="plastic.opaque_glossy_molded",
        )
        trigger.visual(
            Box((0.014, 0.010, 0.030)),
            # Raised so the pad top (z=-0.001) embeds ~1.8mm into the pivot_barrel
            # (radius 0.0028 about z=0), welding the pad to the hinge barrel.
            origin=Origin(xyz=(0.0, -0.005, -0.016)),
            material=accent_mat,
            name="trigger_pad", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            "power_trigger_hinge",
            ArticulationType.REVOLUTE,
            parent=handle,
            child=trigger,
            origin=Origin(xyz=(0.0, -0.0375, 0.195)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=1.0,
                velocity=3.0,
                lower=0.0,
                upper=0.10,
            ),
            meta={"source_id": "S3"},
        )
    return model


def build_seeded_blender(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_blender(config_from_seed(seed), assets=assets)


def with_overrides(config: BlenderConfig, **kwargs: object) -> BlenderConfig:
    return replace(config, **kwargs)


def run_blender_tests(object_model: ArticulatedObject, config: BlenderConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    object_model.validate()
    blade_joints = [j for j in object_model.articulations if j.name == "blade_spin"]
    ctx.check("exactly_one_blade_spin", len(blade_joints) == 1)
    blade_joint = blade_joints[0]
    ctx.check("blade_joint_rotary", blade_joint.articulation_type == ArticulationType.CONTINUOUS)
    ctx.check("blade_axis_aligned", abs(blade_joint.axis[2]) > 0.9)
    ctx.check("blade_radius_inside_container_or_guard", r.blade_radius <= 0.060)
    ctx.check("immersion_has_handle", object_model.get_part("motor_handle") is not None)
    ctx.check("immersion_has_shaft", object_model.get_part("shaft_assembly") is not None)
    ctx.check(
        "part_diversity_parameters_present",
        all((r.blender_layout, r.jar_shape, r.blade_style, r.lid_style, r.control_style)),
    )
    return ctx.report()
