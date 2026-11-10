# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
)

FanLayout = Literal["rod_canopy", "flush_plate", "showroom_downrod"]
BladeShape = Literal["straight_plank", "tapered_paddle", "rounded_airfoil", "long_rectangular"]
HousingStyle = Literal["smooth_drum", "tiered_drum", "vented_band", "rounded_stack"]
MountStyle = Literal["bell_canopy", "flat_plate", "wide_ceiling_plate"]
BladeVariant = Literal["rigid_fixed"]
LightKitStyle = Literal["none", "finial", "integrated_tray"]
GuardStyle = Literal["none"]
MaterialStyle = Literal[
    "brushed_metal", "wood_traditional", "warm_bronze", "matte_white", "industrial_gray"
]

MATERIAL_PALETTES: dict[
    MaterialStyle,
    tuple[
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
    ],
] = {
    "brushed_metal": (
        (0.64, 0.65, 0.62, 1.0),
        (0.30, 0.31, 0.30, 1.0),
        (0.58, 0.37, 0.17, 1.0),
        (0.10, 0.08, 0.06, 1.0),
        (0.05, 0.045, 0.04, 1.0),
    ),
    "wood_traditional": (
        (0.22, 0.13, 0.055, 1.0),
        (0.08, 0.055, 0.035, 1.0),
        (0.55, 0.31, 0.12, 1.0),
        (0.25, 0.12, 0.045, 1.0),
        (0.035, 0.028, 0.022, 1.0),
    ),
    "warm_bronze": (
        (0.34, 0.22, 0.11, 1.0),
        (0.12, 0.075, 0.035, 1.0),
        (0.58, 0.34, 0.14, 1.0),
        (0.23, 0.11, 0.040, 1.0),
        (0.025, 0.020, 0.016, 1.0),
    ),
    "matte_white": (
        (0.82, 0.82, 0.78, 1.0),
        (0.55, 0.55, 0.51, 1.0),
        (0.48, 0.31, 0.17, 1.0),
        (0.20, 0.14, 0.09, 1.0),
        (0.06, 0.055, 0.050, 1.0),
    ),
    "industrial_gray": (
        (0.48, 0.49, 0.46, 1.0),
        (0.26, 0.27, 0.25, 1.0),
        (0.50, 0.36, 0.23, 1.0),
        (0.18, 0.14, 0.10, 1.0),
        (0.035, 0.035, 0.032, 1.0),
    ),
}

LEGACY_LAYOUTS = {
    "standard_downrod": "rod_canopy",
    "hugger_low_profile": "flush_plate",
    "industrial_hvls": "showroom_downrod",
    "retractable": "rod_canopy",
    "dual_head_crossbar": "rod_canopy",
}
LEGACY_BLADES = {
    "flat_rectangular": "straight_plank",
    "palm_leaf": "tapered_paddle",
    "curved_airfoil": "rounded_airfoil",
    "wide_hvls": "long_rectangular",
    "guarded_small_rotor": "rounded_airfoil",
}
LEGACY_HOUSINGS = {
    "cylindrical": "smooth_drum",
    "drum": "tiered_drum",
    "disc_hugger": "rounded_stack",
    "wicker": "vented_band",
    "rectangular_dual": "smooth_drum",
    "storage_ring": "smooth_drum",
}
LEGACY_MOUNTS = {
    "short_downrod": "bell_canopy",
    "long_downrod": "wide_ceiling_plate",
    "angled_downrod": "bell_canopy",
    "hugger_plate": "flat_plate",
    "crossbar_mount": "bell_canopy",
}


@dataclass(frozen=True)
class CeilingFanConfig:
    fan_layout: FanLayout = "rod_canopy"
    blade_count: int = 5
    blade_shape: BladeShape = "rounded_airfoil"
    housing_style: HousingStyle = "tiered_drum"
    mount_style: MountStyle = "bell_canopy"
    downrod_length: float = 0.36
    blade_variant: BladeVariant = "rigid_fixed"
    blade_span: float = 0.78
    blade_pitch_deg: float = 7.0
    light_kit_style: LightKitStyle = "none"
    guard_style: GuardStyle = "none"
    material_style: MaterialStyle = "wood_traditional"
    name: str = "reference_ceiling_fan"


@dataclass(frozen=True)
class ResolvedCeilingFanConfig:
    fan_layout: FanLayout
    blade_count: int
    blade_shape: BladeShape
    housing_style: HousingStyle
    mount_style: MountStyle
    downrod_length: float
    blade_variant: BladeVariant
    blade_span: float
    blade_pitch_rad: float
    light_kit_style: LightKitStyle
    guard_style: GuardStyle
    housing_radius: float
    housing_height: float
    motor_z: float
    material_style: MaterialStyle
    name: str


def config_from_seed(seed: int) -> CeilingFanConfig:
    rng = random.Random(seed)
    fan_layout: FanLayout = rng.choice(("rod_canopy", "flush_plate", "showroom_downrod"))
    mount_style: MountStyle = {
        "rod_canopy": rng.choice(("bell_canopy", "wide_ceiling_plate")),
        "flush_plate": "flat_plate",
        "showroom_downrod": "wide_ceiling_plate",
    }[fan_layout]
    housing_style: HousingStyle = rng.choice(
        ("smooth_drum", "tiered_drum", "vented_band", "rounded_stack")
    )
    blade_shape: BladeShape = rng.choice(
        ("straight_plank", "tapered_paddle", "rounded_airfoil", "long_rectangular")
    )
    if fan_layout == "flush_plate":
        span = rng.uniform(0.58, 0.86)
    elif blade_shape == "long_rectangular":
        span = rng.uniform(0.90, 1.18)
    else:
        span = rng.uniform(0.66, 1.02)
    return CeilingFanConfig(
        fan_layout=fan_layout,
        blade_count=rng.choice((3, 4, 5, 6)),
        blade_shape=blade_shape,
        housing_style=housing_style,
        mount_style=mount_style,
        downrod_length=round(rng.uniform(0.22, 0.72), 3),
        blade_variant="rigid_fixed",
        blade_span=round(span, 3),
        blade_pitch_deg=round(rng.uniform(4.0, 11.0), 2),
        light_kit_style=rng.choice(("none", "none", "finial", "integrated_tray")),
        guard_style="none",
        material_style=rng.choice(
            ("brushed_metal", "wood_traditional", "warm_bronze", "matte_white", "industrial_gray")
        ),
        name=f"seeded_ceiling_fan_{seed}",
    )


def _alias(value: str, aliases: dict[str, str]) -> str:
    return aliases.get(value, value)


def resolve_config(config: CeilingFanConfig) -> ResolvedCeilingFanConfig:
    fan_layout = _alias(str(config.fan_layout), LEGACY_LAYOUTS)
    blade_shape = _alias(str(config.blade_shape), LEGACY_BLADES)
    housing_style = _alias(str(config.housing_style), LEGACY_HOUSINGS)
    mount_style = _alias(str(config.mount_style), LEGACY_MOUNTS)

    if fan_layout not in {"rod_canopy", "flush_plate", "showroom_downrod"}:
        raise ValueError(f"Unsupported fan_layout: {config.fan_layout}")
    if not 3 <= config.blade_count <= 8:
        raise ValueError("blade_count must be between 3 and 8")
    if blade_shape not in {
        "straight_plank",
        "tapered_paddle",
        "rounded_airfoil",
        "long_rectangular",
    }:
        raise ValueError(f"Unsupported blade_shape: {config.blade_shape}")
    if housing_style not in {"smooth_drum", "tiered_drum", "vented_band", "rounded_stack"}:
        raise ValueError(f"Unsupported housing_style: {config.housing_style}")
    if mount_style not in {"bell_canopy", "flat_plate", "wide_ceiling_plate"}:
        raise ValueError(f"Unsupported mount_style: {config.mount_style}")
    if str(config.blade_variant) != "rigid_fixed":
        raise ValueError(f"Unsupported blade_variant: {config.blade_variant}")
    if config.light_kit_style not in {"none", "finial", "integrated_tray", "globe"}:
        raise ValueError(f"Unsupported light_kit_style: {config.light_kit_style}")
    if str(config.guard_style) != "none":
        raise ValueError(f"Unsupported guard_style: {config.guard_style}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    if fan_layout == "flush_plate":
        mount_style = "flat_plate"
        downrod_length = 0.0
    else:
        downrod_length = max(0.18, min(0.78, config.downrod_length))
    if fan_layout == "showroom_downrod":
        mount_style = "wide_ceiling_plate"

    housing_radius = {
        "smooth_drum": 0.175,
        "tiered_drum": 0.190,
        "vented_band": 0.205,
        "rounded_stack": 0.215,
    }[housing_style]
    housing_height = {
        "smooth_drum": 0.150,
        "tiered_drum": 0.176,
        "vented_band": 0.168,
        "rounded_stack": 0.190,
    }[housing_style]
    canopy_h = 0.028 if mount_style == "flat_plate" else 0.082
    motor_top_z = -canopy_h - downrod_length - 0.004
    motor_z = motor_top_z - housing_height * 0.5
    if fan_layout == "flush_plate":
        motor_z = -0.036 - housing_height * 0.5

    blade_span = max(0.52, min(1.22, config.blade_span))
    if fan_layout == "flush_plate":
        blade_span = min(blade_span, 0.90)

    return ResolvedCeilingFanConfig(
        fan_layout=fan_layout,  # type: ignore[arg-type]
        blade_count=config.blade_count,
        blade_shape=blade_shape,  # type: ignore[arg-type]
        housing_style=housing_style,  # type: ignore[arg-type]
        mount_style=mount_style,  # type: ignore[arg-type]
        downrod_length=downrod_length,
        blade_variant="rigid_fixed",
        blade_span=blade_span,
        blade_pitch_rad=math.radians(max(0.0, min(15.0, config.blade_pitch_deg))),
        light_kit_style="finial" if config.light_kit_style == "globe" else config.light_kit_style,
        guard_style="none",
        housing_radius=housing_radius,
        housing_height=housing_height,
        motor_z=motor_z,
        material_style=config.material_style,
        name=config.name,
    )


def _merge_geometries(geometries: list[MeshGeometry]) -> MeshGeometry:
    merged = MeshGeometry()
    for geometry in geometries:
        merged.merge(geometry)
    return merged


def _box(part, size, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cylinder(
    part, radius: float, length: float, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _mesh(part, geometry: MeshGeometry, assets: AssetContext, xyz, material, name: str) -> None:
    part.visual(
        mesh_from_geometry(geometry, assets.mesh_path(f"{part.name}_{name}.obj")),
        origin=Origin(xyz=xyz),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _bell_canopy_geometry(radius: float, height: float) -> MeshGeometry:
    profile = [
        (0.000, 0.000),
        (radius, 0.000),
        (radius, -0.012),
        (radius * 0.82, -height * 0.34),
        (radius * 0.58, -height * 0.78),
        (radius * 0.26, -height),
        (0.000, -height),
    ]
    return LatheGeometry(profile, segments=80)


def _tiered_motor_geometry(radius: float, height: float, style: HousingStyle) -> MeshGeometry:
    h = height * 0.5
    if style == "rounded_stack":
        profile = [
            (0.000, -h),
            (radius * 0.54, -h),
            (radius * 0.96, -h * 0.66),
            (radius * 1.08, -h * 0.18),
            (radius * 1.02, h * 0.36),
            (radius * 0.70, h * 0.78),
            (radius * 0.38, h),
            (0.000, h),
        ]
    elif style == "tiered_drum":
        profile = [
            (0.000, -h),
            (radius * 0.64, -h),
            (radius * 0.90, -h * 0.74),
            (radius, -h * 0.42),
            (radius, h * 0.42),
            (radius * 0.86, h * 0.76),
            (radius * 0.54, h),
            (0.000, h),
        ]
    else:
        profile = [
            (0.000, -h),
            (radius * 0.78, -h),
            (radius, -h * 0.72),
            (radius, h * 0.72),
            (radius * 0.78, h),
            (0.000, h),
        ]
    return LatheGeometry(profile, segments=96)


def _blade_dims(r: ResolvedCeilingFanConfig) -> tuple[float, float, float, float]:
    if r.blade_shape == "long_rectangular":
        return (r.blade_span, 0.095, 0.012, 0.095)
    if r.blade_shape == "straight_plank":
        return (r.blade_span, 0.105, 0.012, 0.105)
    if r.blade_shape == "tapered_paddle":
        return (r.blade_span, 0.135, 0.014, 0.080)
    return (r.blade_span, 0.126, 0.013, 0.106)


def _blade_geometry(r: ResolvedCeilingFanConfig) -> MeshGeometry:
    span, root_w, thick, tip_w = _blade_dims(r)
    if r.blade_shape == "straight_plank":
        return ExtrudeGeometry(rounded_rect_profile(span, root_w, 0.010, corner_segments=6), thick)
    if r.blade_shape == "long_rectangular":
        return ExtrudeGeometry(rounded_rect_profile(span, root_w, 0.004, corner_segments=2), thick)
    if r.blade_shape == "rounded_airfoil":
        blade = ExtrudeGeometry(
            rounded_rect_profile(span, root_w, root_w * 0.45, corner_segments=12), thick
        )
        rib = ExtrudeGeometry(
            rounded_rect_profile(span * 0.82, 0.014, 0.006, corner_segments=4),
            thick * 0.42,
        ).translate(0.0, 0.0, thick * 0.60)
        return _merge_geometries([blade, rib])
    profile = [
        (-span * 0.5, -root_w * 0.5),
        (span * 0.44, -tip_w * 0.5),
        (span * 0.5, -tip_w * 0.36),
        (span * 0.5, tip_w * 0.36),
        (span * 0.44, tip_w * 0.5),
        (-span * 0.5, root_w * 0.5),
    ]
    return ExtrudeGeometry(profile, thick)


def _add_mount(part, r: ResolvedCeilingFanConfig, metal, dark, assets: AssetContext) -> None:
    if r.mount_style == "flat_plate":
        _cylinder(part, 0.230, 0.014, (0.0, 0.0, -0.007), metal, "ceiling_plate")
        # Tall enough to bridge the ceiling_plate (bottom -0.014) down to the
        # motor top (world -0.036, the mount_to_motor weld interface).
        _cylinder(part, 0.115, 0.024, (0.0, 0.0, -0.024), dark, "short_mount_collar")
        return

    canopy_r = 0.150 if r.mount_style == "bell_canopy" else 0.220
    canopy_h = 0.078 if r.mount_style == "bell_canopy" else 0.046
    if r.mount_style == "wide_ceiling_plate":
        _box(
            part,
            (canopy_r * 2.05, canopy_r * 2.05, 0.012),
            (0.0, 0.0, -0.006),
            metal,
            "square_ceiling_plate",
        )
        _cylinder(
            part, canopy_r * 0.56, canopy_h, (0.0, 0.0, -canopy_h * 0.5), metal, "flat_canopy_boss"
        )
    else:
        _mesh(
            part,
            _bell_canopy_geometry(canopy_r, canopy_h),
            assets,
            (0.0, 0.0, 0.0),
            metal,
            "bell_canopy",
        )
    _cylinder(part, canopy_r * 0.28, 0.022, (0.0, 0.0, -canopy_h - 0.011), dark, "upper_rod_collar")

    rod_top = -canopy_h - 0.022
    rod_bottom = r.motor_z + r.housing_height * 0.5
    rod_len = max(0.030, rod_top - rod_bottom)
    _cylinder(part, 0.019, rod_len, (0.0, 0.0, rod_top - rod_len * 0.5), dark, "downrod")
    _cylinder(part, 0.052, 0.018, (0.0, 0.0, rod_bottom + 0.014), dark, "lower_rod_collar")
    for i, angle in enumerate((math.pi / 4.0, math.pi * 5.0 / 4.0)):
        _cylinder(
            part,
            0.006,
            0.006,
            (canopy_r * 0.58 * math.cos(angle), canopy_r * 0.58 * math.sin(angle), -0.002),
            dark,
            f"ceiling_plate_mounting_screw_{i}",
        )


def _add_motor(part, r: ResolvedCeilingFanConfig, metal, dark, assets: AssetContext) -> None:
    hr = r.housing_radius
    hh = r.housing_height
    # The motor link frame origin sits at the mount interface (the motor top,
    # where the downrod welds on), so its geometry is authored with the drum
    # centered z0 = -hh/2 below the link origin. This keeps the FIXED
    # mount_to_motor weld honest (origin on real hardware for both parts).
    z0 = -hh * 0.5
    if r.housing_style == "smooth_drum":
        _cylinder(part, hr, hh, (0.0, 0.0, z0), metal, "motor_shell")
    else:
        _mesh(
            part,
            _tiered_motor_geometry(hr, hh, r.housing_style),
            assets,
            (0.0, 0.0, z0),
            metal,
            "motor_shell",
        )
    _cylinder(part, hr * 1.05, 0.010, (0.0, 0.0, z0 + hh * 0.50 - 0.010), dark, "upper_trim_ring")
    _cylinder(part, hr * 1.03, 0.014, (0.0, 0.0, z0 - hh * 0.50 - 0.007), dark, "lower_trim_ring")
    _cylinder(part, hr * 0.48, 0.020, (0.0, 0.0, z0 + hh * 0.50 - 0.014), dark, "top_motor_collar")
    if r.housing_style == "vented_band":
        for i in range(10):
            angle = i * math.tau / 10.0
            _box(
                part,
                (0.030, 0.008, 0.020),
                (hr * 1.012 * math.cos(angle), hr * 1.012 * math.sin(angle), z0 + 0.010),
                dark,
                f"vent_window_{i}",
                (0.0, 0.0, angle),
            )
    else:
        # Reach the shell wall so the band contacts it. The tiered/rounded
        # shells are hollow lathes (open interior); a 0.70*hr disc would float
        # ~0.06m off the wall. smooth_drum is a solid cylinder (disc enclosed).
        band_r = {
            "smooth_drum": hr * 0.70,
            "tiered_drum": hr * 1.02,
            "rounded_stack": hr * 1.08,
        }[r.housing_style]
        _cylinder(part, band_r, 0.008, (0.0, 0.0, z0), dark, "center_shadow_band")


def _add_blades_and_hub(
    part, r: ResolvedCeilingFanConfig, blade_mat, grain_mat, dark, assets: AssetContext
) -> None:
    span, root_w, thick, _tip_w = _blade_dims(r)
    hub_r = r.housing_radius * 0.62
    hub_h = 0.052
    blade_inner_r = hub_r + 0.030
    clamp_r = blade_inner_r + 0.045
    bracket_end_r = blade_inner_r + 0.082
    blade_z = -0.014
    bracket_z = -0.006

    _cylinder(part, hub_r, hub_h, (0.0, 0.0, -0.008), dark, "rotor_hub")
    _cylinder(part, hub_r * 0.78, 0.016, (0.0, 0.0, 0.026), dark, "upper_contact_collar")
    _cylinder(part, hub_r * 0.82, 0.020, (0.0, 0.0, -0.044), dark, "lower_spinner_cap")
    _cylinder(part, hub_r * 0.36, 0.018, (0.0, 0.0, -0.063), dark, "bottom_finial_socket")

    blade_geom = mesh_from_geometry(_blade_geometry(r), assets.mesh_path("blade_surface_mesh.obj"))
    for i in range(r.blade_count):
        angle = i * math.tau / r.blade_count
        c = math.cos(angle)
        s = math.sin(angle)
        tangent = (-s, c)

        bracket_len = bracket_end_r + 0.012
        _box(
            part,
            (bracket_len, 0.026, 0.014),
            (bracket_len * 0.5 * c, bracket_len * 0.5 * s, bracket_z),
            dark,
            f"blade_{i}_iron_arm",
            (0.0, 0.0, angle),
        )
        _box(
            part,
            (0.112, root_w * 0.66, 0.018),
            (clamp_r * c, clamp_r * s, blade_z + thick * 0.55),
            dark,
            f"blade_{i}_root_clamp",
            (0.0, r.blade_pitch_rad, angle),
        )
        for offset, label in ((root_w * 0.20, "left"), (-root_w * 0.20, "right")):
            bx = clamp_r * c + offset * tangent[0]
            by = clamp_r * s + offset * tangent[1]
            _cylinder(
                part,
                0.006,
                0.006,
                (bx, by, blade_z + thick * 1.40),
                dark,
                f"blade_{i}_{label}_bolt",
            )

        blade_center_r = blade_inner_r + span * 0.5
        part.visual(
            blade_geom,
            origin=Origin(
                xyz=(blade_center_r * c, blade_center_r * s, blade_z),
                rpy=(r.blade_pitch_rad, 0.0, angle),
            ),
            material=blade_mat,
            name=f"blade_surface_{i}", material_class_id="wood.natural_generic",
        )
    if r.light_kit_style == "integrated_tray":
        _cylinder(part, hub_r * 0.70, 0.018, (0.0, 0.0, -0.077), blade_mat, "integrated_light_tray")
    elif r.light_kit_style == "finial":
        part.visual(
            Sphere(radius=0.022),
            origin=Origin(xyz=(0.0, 0.0, -0.076)),
            material=dark,
            name="decorative_bottom_finial", material_class_id="metal.blackened_gunmetal",
        )


def build_ceiling_fan(
    config: CeilingFanConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or CeilingFanConfig()
    r = resolve_config(config)
    assets = assets or AssetContext(Path(tempfile.mkdtemp(prefix="articraft-ceiling-fan-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    metal_rgba, dark_rgba, blade_rgba, grain_rgba, black_rgba = MATERIAL_PALETTES[r.material_style]
    metal = model.material(f"fan_metal_{r.material_style}", rgba=metal_rgba)
    dark = model.material(f"fan_dark_{r.material_style}", rgba=dark_rgba)
    blade_mat = model.material(f"fan_blade_{r.material_style}", rgba=blade_rgba)
    grain_mat = model.material(f"fan_blade_grain_{r.material_style}", rgba=grain_rgba)
    black = model.material("black_screw_detail", rgba=black_rgba)

    mount = model.part("ceiling_mount")
    _add_mount(mount, r, metal, dark, assets)

    motor = model.part("motor_housing")
    _add_motor(motor, r, metal, black, assets)
    model.articulation(
        "mount_to_motor",
        ArticulationType.FIXED,
        parent=mount,
        child=motor,
        # Weld at the interface: downrod bottom == motor top == motor_top_z.
        origin=Origin(xyz=(0.0, 0.0, r.motor_z + r.housing_height * 0.5)),
    )

    rotor = model.part("blade_assembly")
    _add_blades_and_hub(rotor, r, blade_mat, grain_mat, black, assets)
    # Motor link frame origin is now the motor top; the rotor hangs below the
    # drum, so shift the spin joint down by the same hh/2 the motor mesh moved.
    fan_spin_z = -r.housing_height - 0.048
    model.articulation(
        "fan_spin",
        ArticulationType.CONTINUOUS,
        parent=motor,
        child=rotor,
        origin=Origin(xyz=(0.0, 0.0, fan_spin_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=20.0),
        meta={
            "type": "continuous",
            "axis": (0.0, 0.0, 1.0),
            "origin": "motor lower bearing and blade hub centerline",
            "range": "continuous",
        },
    )
    return model


def run_ceiling_fan_tests(object_model: ArticulatedObject, config: CeilingFanConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {part.name for part in object_model.parts}
    ctx.check(
        "required_parts",
        {"ceiling_mount", "motor_housing", "blade_assembly"}.issubset(part_names),
        details=str(sorted(part_names)),
    )
    spin = object_model.get_articulation("fan_spin")
    ctx.check(
        "fan_spin_continuous",
        spin.articulation_type == ArticulationType.CONTINUOUS,
        details=str(spin.articulation_type),
    )
    ctx.check(
        "fan_spin_axis_vertical",
        tuple(round(v, 6) for v in spin.axis) == (0.0, 0.0, 1.0),
        details=str(spin.axis),
    )
    rotor = object_model.get_part("blade_assembly")
    blade_visuals = [
        visual
        for visual in rotor.visuals
        if visual.name and visual.name.startswith("blade_surface_")
    ]
    ctx.check(
        "blade_count_matches",
        len(blade_visuals) == r.blade_count,
        details=str([visual.name for visual in blade_visuals]),
    )
    hub_r = r.housing_radius * 0.62
    span, _, _, _ = _blade_dims(r)
    for visual in blade_visuals:
        x, y, _ = visual.origin.xyz
        inner_r = math.hypot(x, y) - span * 0.5
        ctx.check(
            f"{visual.name}_root_tucks_under_clamp",
            inner_r <= hub_r + 0.040,
            details=f"inner_r={inner_r:.4f}, hub_r={hub_r:.4f}",
        )
    ctx.check(
        "hub_and_clamps_exist",
        rotor.get_visual("rotor_hub") is not None
        and all(
            rotor.get_visual(f"blade_{i}_root_clamp") is not None for i in range(r.blade_count)
        ),
    )
    ctx.check(
        "seeded_family_is_five_star_style",
        r.fan_layout in {"rod_canopy", "flush_plate", "showroom_downrod"}
        and r.blade_shape
        in {"straight_plank", "tapered_paddle", "rounded_airfoil", "long_rectangular"}
        and r.housing_style in {"smooth_drum", "tiered_drum", "vented_band", "rounded_stack"}
        and r.blade_variant == "rigid_fixed"
        and r.guard_style == "none",
        details=f"{r.fan_layout}, {r.blade_shape}, {r.housing_style}",
    )
    return ctx.report()


def build_seeded_ceiling_fan(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_ceiling_fan(config_from_seed(seed), assets=assets)
