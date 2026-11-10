# SPDX-License-Identifier: Apache-2.0

"""Procedural template for category `camera_lens`."""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Material,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

LensProfile = Literal[
    "standard_zoom",
    "macro_extending",
    "telephoto_collar",
    "manual_prime",
    "cine_zoom",
    "tilt_shift",
    "retractable_kit",
]
BarrelProfile = Literal[
    "straight_cylinder", "stepped_zoom", "long_telephoto", "short_pancake", "tilt_shift_compact"
]
RingStyle = Literal["rubber_ribbed", "gear_teeth", "fine_knurl", "smooth_marked", "t_handle"]
RingLayout = Literal[
    "focus_only", "zoom_focus", "zoom_iris_focus", "aperture_focus", "unlock_zoom_focus"
]
ExtensionStyle = Literal["none", "macro_inner", "zoom_inner", "retractable_front"]
CollarStyle = Literal["smooth_collar", "collar_with_foot"]
HoodStyle = Literal["bayonet_petals", "shade_collar"]
MountStyle = Literal["bayonet", "cine_pl", "screw_mount"]
FrontElementStyle = Literal["flat_glass", "deep_recessed", "convex_coated"]
MaterialStyle = Literal["black", "white_telephoto", "cine_black"]

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "black": {
        "barrel": (0.01, 0.011, 0.012, 1.0),
        "ring": (0.005, 0.005, 0.006, 1.0),
        "metal": (0.62, 0.61, 0.57, 1.0),
        "anodized": (0.035, 0.035, 0.04, 1.0),
        "glass": (0.08, 0.16, 0.20, 0.46),
        "mark": (0.92, 0.92, 0.86, 1.0),
    },
    "white_telephoto": {
        "barrel": (0.86, 0.84, 0.76, 1.0),
        "ring": (0.10, 0.10, 0.10, 1.0),
        "metal": (0.48, 0.48, 0.45, 1.0),
        "anodized": (0.38, 0.38, 0.35, 1.0),
        "glass": (0.07, 0.28, 0.36, 0.55),
        "mark": (0.08, 0.08, 0.08, 1.0),
    },
    "cine_black": {
        "barrel": (0.015, 0.017, 0.019, 1.0),
        "ring": (0.02, 0.02, 0.018, 1.0),
        "metal": (0.52, 0.50, 0.43, 1.0),
        "anodized": (0.045, 0.044, 0.042, 1.0),
        "glass": (0.12, 0.42, 0.36, 0.58),
        "mark": (0.95, 0.88, 0.60, 1.0),
    },
}


@dataclass(frozen=True)
class CameraLensConfig:
    lens_profile: LensProfile = "standard_zoom"
    barrel_length: float | None = None
    barrel_radius: float = 0.054
    barrel_profile: BarrelProfile = "stepped_zoom"
    ring_style: RingStyle = "rubber_ribbed"
    ring_layout: RingLayout = "zoom_focus"
    zoom_ring_enabled: bool = True
    aperture_ring_enabled: bool = False
    extension_enabled: bool = True
    extension_length: float = 0.040
    extension_style: ExtensionStyle = "zoom_inner"
    tripod_collar_enabled: bool = False
    collar_style: CollarStyle = "collar_with_foot"
    hood_enabled: bool = False
    hood_style: HoodStyle = "bayonet_petals"
    tilt_shift_enabled: bool = False
    shift_travel: float = 0.012
    tilt_range_deg: float = 8.0
    unlock_ring_enabled: bool = False
    mount_style: MountStyle = "bayonet"
    front_element_style: FrontElementStyle = "convex_coated"
    material_style: MaterialStyle = "black"
    name: str = "reference_camera_lens"


@dataclass(frozen=True)
class ResolvedCameraLensConfig:
    lens_profile: LensProfile
    barrel_length: float
    barrel_radius: float
    barrel_profile: BarrelProfile
    ring_style: RingStyle
    ring_layout: RingLayout
    zoom_ring_enabled: bool
    aperture_ring_enabled: bool
    extension_enabled: bool
    extension_length: float
    extension_style: ExtensionStyle
    tripod_collar_enabled: bool
    collar_style: CollarStyle
    hood_enabled: bool
    hood_style: HoodStyle
    tilt_shift_enabled: bool
    shift_travel: float
    tilt_range_rad: float
    unlock_ring_enabled: bool
    mount_style: MountStyle
    front_element_style: FrontElementStyle
    material_style: MaterialStyle
    name: str


def config_from_seed(seed: int) -> CameraLensConfig:
    rng = random.Random(seed)
    profile: LensProfile = rng.choice(
        (
            "standard_zoom",
            "macro_extending",
            "telephoto_collar",
            "manual_prime",
            "cine_zoom",
            "tilt_shift",
            "retractable_kit",
        )
    )
    return CameraLensConfig(
        lens_profile=profile,
        barrel_length=round(rng.uniform(0.10, 0.48), 3),
        barrel_radius=round(rng.uniform(0.040, 0.090), 3),
        barrel_profile=rng.choice(
            (
                "straight_cylinder",
                "stepped_zoom",
                "long_telephoto",
                "short_pancake",
                "tilt_shift_compact",
            )
        ),
        ring_style=rng.choice(
            ("rubber_ribbed", "gear_teeth", "fine_knurl", "smooth_marked", "t_handle")
        ),
        ring_layout=rng.choice(
            ("focus_only", "zoom_focus", "zoom_iris_focus", "aperture_focus", "unlock_zoom_focus")
        ),
        zoom_ring_enabled=profile not in {"manual_prime", "tilt_shift"} and rng.random() < 0.85,
        aperture_ring_enabled=profile in {"manual_prime", "cine_zoom"} or rng.random() < 0.30,
        extension_enabled=False,
        extension_length=round(rng.uniform(0.020, 0.060), 3),
        extension_style=rng.choice(("macro_inner", "zoom_inner", "retractable_front")),
        tripod_collar_enabled=profile == "telephoto_collar" or rng.random() < 0.15,
        hood_enabled=profile in {"manual_prime", "cine_zoom"} or rng.random() < 0.35,
        tilt_shift_enabled=False,
        shift_travel=round(rng.uniform(0.008, 0.014), 3),
        tilt_range_deg=round(rng.uniform(6.0, 10.0), 1),
        unlock_ring_enabled=profile == "retractable_kit",
        mount_style=rng.choice(("bayonet", "cine_pl", "screw_mount")),
        front_element_style=rng.choice(("flat_glass", "deep_recessed", "convex_coated")),
        material_style=rng.choice(("black", "white_telephoto", "cine_black")),
        name=f"seeded_camera_lens_{seed}",
    )


def resolve_config(config: CameraLensConfig) -> ResolvedCameraLensConfig:
    if config.lens_profile not in {
        "standard_zoom",
        "macro_extending",
        "telephoto_collar",
        "manual_prime",
        "cine_zoom",
        "tilt_shift",
        "retractable_kit",
    }:
        raise ValueError(f"Unsupported lens_profile: {config.lens_profile}")
    if config.barrel_profile not in {
        "straight_cylinder",
        "stepped_zoom",
        "long_telephoto",
        "short_pancake",
        "tilt_shift_compact",
    }:
        raise ValueError(f"Unsupported barrel_profile: {config.barrel_profile}")
    if config.ring_style not in {
        "rubber_ribbed",
        "gear_teeth",
        "fine_knurl",
        "smooth_marked",
        "t_handle",
    }:
        raise ValueError(f"Unsupported ring_style: {config.ring_style}")
    if config.ring_layout not in {
        "focus_only",
        "zoom_focus",
        "zoom_iris_focus",
        "aperture_focus",
        "unlock_zoom_focus",
    }:
        raise ValueError(f"Unsupported ring_layout: {config.ring_layout}")
    if config.extension_style not in {"none", "macro_inner", "zoom_inner", "retractable_front"}:
        raise ValueError(f"Unsupported extension_style: {config.extension_style}")
    if config.collar_style not in {"smooth_collar", "collar_with_foot"}:
        raise ValueError(f"Unsupported collar_style: {config.collar_style}")
    if config.hood_style not in {"bayonet_petals", "shade_collar"}:
        raise ValueError(f"Unsupported hood_style: {config.hood_style}")
    if config.mount_style not in {"bayonet", "cine_pl", "screw_mount"}:
        raise ValueError(f"Unsupported mount_style: {config.mount_style}")
    if config.front_element_style not in {"flat_glass", "deep_recessed", "convex_coated"}:
        raise ValueError(f"Unsupported front_element_style: {config.front_element_style}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    profile_length = {
        "standard_zoom": 0.24,
        "macro_extending": 0.22,
        "telephoto_collar": 0.42,
        "manual_prime": 0.16,
        "cine_zoom": 0.30,
        "tilt_shift": 0.15,
        "retractable_kit": 0.18,
    }[config.lens_profile]
    length = config.barrel_length if config.barrel_length is not None else profile_length
    if config.lens_profile == "telephoto_collar":
        length = max(length, 0.32)
    if config.lens_profile == "tilt_shift":
        length = min(length, 0.22)
    # Keep this template rotation-only: no translational tilt-shift carriage.
    tilt_shift = False
    barrel_profile = config.barrel_profile
    if config.lens_profile == "telephoto_collar":
        barrel_profile = "long_telephoto"
    elif config.lens_profile in {"manual_prime", "retractable_kit"}:
        barrel_profile = (
            "short_pancake" if config.lens_profile == "manual_prime" else "stepped_zoom"
        )
    elif config.lens_profile in {"cine_zoom", "macro_extending"}:
        barrel_profile = "stepped_zoom"
    if tilt_shift:
        barrel_profile = "tilt_shift_compact"

    zoom = (
        not tilt_shift
        and config.lens_profile not in {"manual_prime", "telephoto_collar"}
        and config.zoom_ring_enabled
        and config.ring_layout in {"zoom_focus", "zoom_iris_focus", "unlock_zoom_focus"}
    )
    aperture = (
        config.aperture_ring_enabled
        or config.ring_layout in {"zoom_iris_focus", "aperture_focus"}
        or config.lens_profile in {"manual_prime", "cine_zoom"}
    )
    unlock = not tilt_shift and (
        config.unlock_ring_enabled
        or config.ring_layout == "unlock_zoom_focus"
        or config.lens_profile == "retractable_kit"
    )
    # Keep this template rotation-only: no barrel translation/extension.
    extension = False
    extension_style = "none"
    tripod = config.tripod_collar_enabled or config.lens_profile == "telephoto_collar"
    hood = (
        not tilt_shift
        and not extension
        and (config.hood_enabled or config.lens_profile in {"manual_prime", "cine_zoom"})
    )
    if tilt_shift:
        zoom = False
        unlock = False
        extension = False
        extension_style = "none"

    return ResolvedCameraLensConfig(
        lens_profile=config.lens_profile,
        barrel_length=max(0.10, min(0.52, length)),
        barrel_radius=max(0.035, min(0.105, config.barrel_radius)),
        barrel_profile=barrel_profile,
        ring_style=config.ring_style,
        ring_layout=config.ring_layout,
        zoom_ring_enabled=zoom,
        aperture_ring_enabled=aperture,
        extension_enabled=extension,
        extension_length=max(0.012, min(0.075, config.extension_length)),
        extension_style=extension_style,
        tripod_collar_enabled=tripod,
        collar_style=config.collar_style,
        hood_enabled=hood,
        hood_style=config.hood_style,
        tilt_shift_enabled=tilt_shift,
        shift_travel=max(0.004, min(0.020, config.shift_travel)),
        tilt_range_rad=math.radians(max(3.0, min(12.0, config.tilt_range_deg))),
        unlock_ring_enabled=unlock,
        mount_style=config.mount_style,
        front_element_style=config.front_element_style,
        material_style=config.material_style,
        name=config.name,
    )


def _tube_along_x(
    outer_radius: float,
    inner_radius: float,
    length: float,
    center_x: float,
) -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(length)
        .translate((center_x - length / 2.0, 0.0, 0.0))
    )


def _joint_meta(joint_type: ArticulationType, axis, origin, joint_range) -> dict[str, object]:
    return {"type": joint_type.value, "axis": axis, "origin": origin, "range": joint_range}


def _add_ring_grip(
    part, radius: float, width: float, style: RingStyle, *, ring_mat: Material
) -> None:
    wall = max(0.0035, radius * 0.075)
    part.visual(
        mesh_from_cadquery(
            _tube_along_x(radius, max(0.001, radius - wall), width, 0.0),
            "ring_shell",
        ),
        material=ring_mat,
        name="ring_shell", material_class_id="rubber.smooth_plain",
    )
    if style == "smooth_marked":
        return
    rib_count = {"rubber_ribbed": 36, "gear_teeth": 72, "fine_knurl": 48, "t_handle": 28}[style]
    rib_w = max(0.0024, radius * (0.030 if style == "gear_teeth" else 0.040))
    rib_h = max(0.0028, radius * (0.050 if style == "gear_teeth" else 0.040))
    rib_len = width * (0.92 if style == "gear_teeth" else 0.82)
    for i in range(rib_count):
        angle = math.tau * i / rib_count
        part.visual(
            Box((rib_len, rib_w, rib_h)),
            origin=Origin(
                xyz=(
                    0.0,
                    (radius + rib_h * 0.15) * math.sin(angle),
                    (radius + rib_h * 0.15) * math.cos(angle),
                ),
                rpy=(angle, 0.0, 0.0),
            ),
            material=ring_mat,
            name=f"grip_rib_{i}", material_class_id="rubber.directional_grooved",
        )


def _add_aperture_ring_radial(
    part,
    ring_radius: float,
    ring_width: float,
    *,
    anodized_mat: Material,
) -> None:
    part.visual(
        mesh_from_cadquery(
            _tube_along_x(ring_radius + 0.001, ring_radius - 0.002, ring_width, 0.0),
            "aperture_ring_body",
        ),
        material=anodized_mat,
        name="ring_body", material_class_id="metal.paint_coated",
    )
    rib_count = 24
    rib_h = max(0.003, ring_radius * 0.045)
    rib_w = max(0.003, ring_radius * 0.048)
    for i in range(rib_count):
        angle = math.tau * i / rib_count
        part.visual(
            Box((ring_width * 0.82, rib_w, rib_h)),
            origin=Origin(
                xyz=(
                    0.0,
                    (ring_radius + rib_h * 0.5) * math.sin(angle),
                    (ring_radius + rib_h * 0.5) * math.cos(angle),
                ),
                rpy=(angle, 0.0, 0.0),
            ),
            material=anodized_mat,
            name=f"grip_rail_{i}", material_class_id="metal.paint_coated",
        )


def _build_barrel(
    barrel,
    r: ResolvedCameraLensConfig,
    *,
    barrel_mat: Material,
    anodized_mat: Material,
    metal_mat: Material,
    glass_mat: Material,
    index_mat: Material,
) -> None:
    L, R = r.barrel_length, r.barrel_radius
    wall = max(0.004, R * 0.075)

    barrel.visual(
        mesh_from_cadquery(
            _tube_along_x(R, R - wall, L, L * 0.5 - L * 0.505),
            "outer_sleeve",
        ),
        material=barrel_mat,
        name="outer_sleeve", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black", "cine_black"} else "metal.paint_coated"),
    )
    barrel.visual(
        mesh_from_cadquery(
            _tube_along_x(R + wall * 0.6, R - wall, 0.012, L * 0.48),
            "front_lip",
        ),
        material=anodized_mat,
        name="front_lip", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black", "cine_black"} else "metal.paint_coated"),
    )
    barrel.visual(
        mesh_from_cadquery(
            _tube_along_x(R * 0.88, R * 0.60, 0.018, -L * 0.48),
            "rear_mount_sleeve",
        ),
        material=metal_mat,
        name="rear_mount_sleeve", material_class_id="metal.stainless_matte",
    )
    for i, x in enumerate((-L * 0.32, -L * 0.02, L * 0.22)):
        barrel.visual(
            mesh_from_cadquery(
                _tube_along_x(R + wall * 0.5, R - wall * 0.1, 0.005, x),
                f"ring_shoulder_{i}",
            ),
            material=anodized_mat,
            name=f"ring_shoulder_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black", "cine_black"} else "metal.paint_coated"),
        )

    if r.mount_style == "cine_pl":
        barrel.visual(
            Cylinder(radius=R * 1.08, length=0.012),
            origin=Origin(xyz=(-L * 0.50, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
            material=metal_mat,
            name="pl_mount_flange", material_class_id="metal.stainless_matte",
        )
    else:
        for i in range(6):
            barrel.visual(
                Cylinder(radius=R * (0.88 + i * 0.012), length=0.002),
                origin=Origin(xyz=(-L * 0.50 + i * 0.003, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
                material=metal_mat,
                name=f"screw_thread_{i}", material_class_id="metal.steel_bare",
            )

    if r.barrel_profile in {"stepped_zoom", "long_telephoto", "tilt_shift_compact"}:
        barrel.visual(
            Cylinder(radius=R * 1.08, length=L * 0.16),
            origin=Origin(xyz=(-L * 0.22, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
            material=barrel_mat,
            name="rear_step", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black", "cine_black"} else "metal.paint_coated"),
        )
        barrel.visual(
            Cylinder(radius=R * 1.0, length=L * 0.20),
            origin=Origin(xyz=(L * 0.36, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
            material=barrel_mat,
            name="front_step", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black", "cine_black"} else "metal.paint_coated"),
        )

    glass_radius = R * (0.58 if r.front_element_style == "deep_recessed" else 0.72)
    glass_x = L * 0.50
    barrel.visual(
        Cylinder(radius=R * 0.98, length=0.010),
        origin=Origin(xyz=(glass_x - 0.010, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
        material=anodized_mat,
        name="front_glass_retainer", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black", "cine_black"} else "metal.paint_coated"),
    )
    barrel.visual(
        Cylinder(radius=glass_radius, length=0.004),
        origin=Origin(xyz=(glass_x - 0.004, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
        material=glass_mat,
        name="front_glass", material_class_id="glass.clear_transparent",
    )
    barrel.visual(
        Cylinder(radius=glass_radius * 0.50, length=0.0025),
        origin=Origin(xyz=(glass_x - 0.010, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
        material=barrel_mat,
        name="dark_aperture_stop", material_class_id="metal.blackened_gunmetal",
    )
    barrel.visual(
        Cylinder(radius=R * 0.48, length=0.003),
        origin=Origin(xyz=(-L * 0.505, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
        material=glass_mat,
        name="rear_glass", material_class_id="glass.clear_transparent",
    )
    barrel.visual(
        Sphere(radius=max(0.002, R * 0.034)),
        origin=Origin(xyz=(-L * 0.50, 0.0, R * 0.60)),
        material=index_mat,
        name="mount_index_dot", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )


def _build_inner_barrel(
    part,
    r: ResolvedCameraLensConfig,
    *,
    barrel_mat: Material,
    anodized_mat: Material,
    glass_mat: Material,
    ring_mat: Material,
) -> None:
    R_outer = r.barrel_radius
    R = R_outer * (0.68 if r.extension_style != "retractable_front" else 0.76)
    wall = max(0.004, R * 0.082)
    L = max(0.040, r.extension_length + r.barrel_length * 0.10)

    part.visual(
        mesh_from_cadquery(
            _tube_along_x(R, R - wall, L, L * 0.50),
            "inner_sleeve",
        ),
        material=barrel_mat,
        name="inner_sleeve", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black", "cine_black"} else "metal.paint_coated"),
    )
    part.visual(
        mesh_from_cadquery(
            _tube_along_x(R + wall * 0.5, R - wall * 0.2, 0.014, L + 0.005),
            "front_filter_ring",
        ),
        material=anodized_mat,
        name="front_filter_ring", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black", "cine_black"} else "metal.paint_coated"),
    )
    part.visual(
        Cylinder(radius=R * 0.72, length=0.004),
        origin=Origin(xyz=(L + 0.002, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
        material=glass_mat,
        name="moving_front_glass", material_class_id="glass.clear_transparent",
    )
    rib_count = 32
    rib_h = max(0.003, R * 0.048)
    rib_w = max(0.003, R * 0.052)
    focus_band_x = L * 0.40
    focus_band_len = L * 0.52
    for i in range(rib_count):
        angle = math.tau * i / rib_count
        part.visual(
            Box((focus_band_len, rib_w, rib_h)),
            origin=Origin(
                xyz=(
                    focus_band_x,
                    (R + rib_h * 0.5) * math.sin(angle),
                    (R + rib_h * 0.5) * math.cos(angle),
                ),
                rpy=(angle, 0.0, 0.0),
            ),
            material=ring_mat,
            name=f"focus_rib_{i}", material_class_id="rubber.directional_grooved",
        )
    part.visual(
        Box((0.018, 0.0020, 0.0010)),
        origin=Origin(xyz=(L * 0.62, 0.0, R + rib_h + 0.001)),
        material=anodized_mat,
        name="focus_scale_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    for i, z in enumerate((-R * 0.78, R * 0.78)):
        part.visual(
            Box((L * 0.60, 0.006, 0.004)),
            origin=Origin(xyz=(L * 0.40, 0.0, z)),
            material=barrel_mat,
            name=f"extension_guide_key_{i}", material_class_id="metal.blackened_gunmetal",
        )


def build_camera_lens(
    config: CameraLensConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or CameraLensConfig()
    r = resolve_config(config)
    assets = assets or AssetContext(Path(tempfile.mkdtemp(prefix="articraft-camera-lens-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["adopted_source_ids"] = ("S1", "S2", "S3", "S4", "S5", "S6")
    pal = PALETTES[r.material_style]
    barrel_mat = model.material("lens_barrel", rgba=pal["barrel"])
    ring_mat = model.material("lens_ring", rgba=pal["ring"])
    metal_mat = model.material("lens_metal", rgba=pal["metal"])
    anodized_mat = model.material("lens_anodized", rgba=pal["anodized"])
    glass_mat = model.material("lens_glass", rgba=pal["glass"])
    index_mat = model.material("lens_red_index", rgba=(0.85, 0.04, 0.03, 1.0))

    barrel = model.part("barrel")
    _build_barrel(
        barrel,
        r,
        barrel_mat=barrel_mat,
        anodized_mat=anodized_mat,
        metal_mat=metal_mat,
        glass_mat=glass_mat,
        index_mat=index_mat,
    )

    optical_axis = (1.0, 0.0, 0.0)

    if r.extension_enabled:
        inner_barrel = model.part("inner_barrel")
        _build_inner_barrel(
            inner_barrel,
            r,
            barrel_mat=barrel_mat,
            anodized_mat=anodized_mat,
            glass_mat=glass_mat,
            ring_mat=ring_mat,
        )
        ext_origin = (r.barrel_length * 0.50, 0.0, 0.0)
        model.articulation(
            "barrel_extension",
            ArticulationType.PRISMATIC,
            parent=barrel,
            child=inner_barrel,
            origin=Origin(xyz=ext_origin),
            axis=optical_axis,
            motion_limits=MotionLimits(
                effort=20.0, velocity=0.18, lower=0.0, upper=r.extension_length
            ),
            meta=_joint_meta(
                ArticulationType.PRISMATIC, optical_axis, ext_origin, (0.0, r.extension_length)
            ),
        )

    if r.aperture_ring_enabled:
        aperture_ring = model.part("aperture_ring")
        aperture_x = r.barrel_length * (-0.02 if r.zoom_ring_enabled else -0.14)
        _add_aperture_ring_radial(
            aperture_ring,
            r.barrel_radius + 0.001,
            0.024,
            anodized_mat=anodized_mat,
        )
        aperture_origin = (aperture_x, 0.0, 0.0)
        model.articulation(
            "aperture_ring_turn",
            ArticulationType.CONTINUOUS,
            parent=barrel,
            child=aperture_ring,
            origin=Origin(xyz=aperture_origin),
            axis=optical_axis,
            motion_limits=MotionLimits(effort=0.6, velocity=4.0),
            meta=_joint_meta(
                ArticulationType.CONTINUOUS, optical_axis, aperture_origin, (None, None)
            ),
        )

    ring_specs: list[tuple[str, float, float, tuple[float, float] | None]] = []
    if r.unlock_ring_enabled:
        ring_specs.append(("unlock_ring", -r.barrel_length * 0.38, 0.030, (0.0, 0.65)))
    if r.zoom_ring_enabled:
        ring_specs.append(("zoom_ring", -r.barrel_length * 0.12, 0.056, (0.0, 1.25)))
    ring_specs.append(("focus_ring", r.barrel_length * 0.34, 0.052, (-2.35, 2.35)))

    for rname, x, width, limits in ring_specs:
        ring = model.part(rname)
        ring_radius = r.barrel_radius * (
            1.08
            if rname == "zoom_ring"
            and r.barrel_profile in {"stepped_zoom", "long_telephoto", "tilt_shift_compact"}
            else 1.02
        )
        _add_ring_grip(
            ring,
            ring_radius,
            width,
            r.ring_style,
            ring_mat=ring_mat,
        )
        joint_name = {
            "zoom_ring": "zoom_ring_turn",
            "focus_ring": "focus_ring_turn",
            "unlock_ring": "unlock_ring_turn",
        }[rname]
        lower, upper = limits if limits is not None else (None, None)
        jtype = ArticulationType.REVOLUTE if limits is not None else ArticulationType.CONTINUOUS
        origin_xyz = (x, 0.0, 0.0)
        model.articulation(
            joint_name,
            jtype,
            parent=barrel,
            child=ring,
            origin=Origin(xyz=origin_xyz),
            axis=optical_axis,
            motion_limits=MotionLimits(effort=1.4, velocity=1.5, lower=lower, upper=upper),
            meta=_joint_meta(jtype, optical_axis, origin_xyz, (lower, upper)),
        )

    if r.tripod_collar_enabled:
        collar = model.part("tripod_collar")
        collar_radius = r.barrel_radius * 1.02
        _add_ring_grip(
            collar,
            collar_radius,
            0.040,
            "smooth_marked",
            ring_mat=metal_mat,
        )
        collar_origin = (-r.barrel_length * 0.02, 0.0, 0.0)
        model.articulation(
            "tripod_collar_turn",
            ArticulationType.CONTINUOUS,
            parent=barrel,
            child=collar,
            origin=Origin(xyz=collar_origin),
            axis=optical_axis,
            motion_limits=MotionLimits(effort=4.0, velocity=1.0),
            meta=_joint_meta(
                ArticulationType.CONTINUOUS, optical_axis, collar_origin, (None, None)
            ),
        )

    if r.hood_enabled:
        hood = model.part("hood")
        hood_len = 0.052
        hood.visual(
            Cylinder(radius=r.barrel_radius * 0.80, length=hood_len),
            origin=Origin(xyz=(hood_len * 0.5, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
            material=barrel_mat,
            name="hood_collar", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black", "cine_black"} else "metal.paint_coated"),
        )
        for i, x in enumerate((0.018, 0.038)):
            hood.visual(
                Cylinder(radius=r.barrel_radius * (0.66 - i * 0.08), length=0.003),
                origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
                material=barrel_mat,
                name=f"hood_internal_baffle_{i}", material_class_id="metal.blackened_gunmetal",
            )
        hood_origin = (r.barrel_length * 0.50, 0.0, 0.0)
        model.articulation(
            "hood_twist",
            ArticulationType.REVOLUTE,
            parent=barrel,
            child=hood,
            origin=Origin(xyz=hood_origin),
            axis=optical_axis,
            motion_limits=MotionLimits(effort=1.2, velocity=1.0, lower=0.0, upper=0.80),
            meta=_joint_meta(ArticulationType.REVOLUTE, optical_axis, hood_origin, (0.0, 0.80)),
        )

    if r.tilt_shift_enabled:
        collar_width = 0.026
        ts_collar = model.part("tilt_shift_collar")
        _add_ring_grip(
            ts_collar,
            r.barrel_radius * 1.02,
            collar_width,
            "smooth_marked",
            ring_mat=metal_mat,
        )
        ts_origin = (r.barrel_length * 0.50 + collar_width * 0.50, 0.0, 0.0)
        model.articulation(
            "tilt_shift_rotate",
            ArticulationType.REVOLUTE,
            parent=barrel,
            child=ts_collar,
            origin=Origin(xyz=ts_origin),
            axis=optical_axis,
            motion_limits=MotionLimits(
                effort=5.0, velocity=1.0, lower=-math.pi / 2, upper=math.pi / 2
            ),
            meta=_joint_meta(
                ArticulationType.REVOLUTE, optical_axis, ts_origin, (-math.pi / 2, math.pi / 2)
            ),
        )
        carriage = model.part("shift_carriage")
        rail_x = max(0.032, r.barrel_length * 0.26)
        rail_thickness = max(0.005, r.barrel_radius * 0.08)
        rail_offset = r.barrel_radius + rail_thickness * 0.5
        for tag, yz in (
            ("pos_y", (0.0, rail_offset, 0.0)),
            ("neg_y", (0.0, -rail_offset, 0.0)),
            ("pos_z", (0.0, 0.0, rail_offset)),
            ("neg_z", (0.0, 0.0, -rail_offset)),
        ):
            carriage.visual(
                Box((rail_x, rail_thickness, rail_thickness)),
                origin=Origin(xyz=yz),
                material=metal_mat,
                name=f"carriage_side_rail_{tag}", material_class_id="metal.stainless_matte",
            )
        shift_axis = (0.0, 1.0, 0.0)
        shift_origin = (collar_width * 0.50 + rail_x * 0.50, 0.0, 0.0)
        model.articulation(
            "shift_slide",
            ArticulationType.PRISMATIC,
            parent=ts_collar,
            child=carriage,
            origin=Origin(xyz=shift_origin),
            axis=shift_axis,
            motion_limits=MotionLimits(
                effort=10.0, velocity=0.04, lower=-r.shift_travel, upper=r.shift_travel
            ),
            meta=_joint_meta(
                ArticulationType.PRISMATIC,
                shift_axis,
                shift_origin,
                (-r.shift_travel, r.shift_travel),
            ),
        )
        block = model.part("tilt_optical_block")
        block_length = r.barrel_length * 0.32
        block_radius = r.barrel_radius * 0.50
        block.visual(
            Cylinder(radius=block_radius, length=block_length),
            origin=Origin(rpy=(0.0, math.pi / 2, 0.0)),
            material=barrel_mat,
            name="optical_block", material_class_id="metal.blackened_gunmetal",
        )
        trunnion_span = max(0.004, r.barrel_radius - block_radius)
        trunnion_x = max(0.004, rail_thickness)
        for tag, y_sign in (("pos_y", 1.0), ("neg_y", -1.0)):
            block.visual(
                Box((trunnion_x, trunnion_span, rail_thickness)),
                origin=Origin(
                    xyz=(
                        -block_length * 0.5 + trunnion_x * 0.5,
                        y_sign * (block_radius + trunnion_span * 0.5),
                        0.0,
                    )
                ),
                material=metal_mat,
                name=f"tilt_trunnion_{tag}", material_class_id="metal.stainless_matte",
            )
        block.visual(
            Cylinder(radius=r.barrel_radius * 0.36, length=0.004),
            origin=Origin(xyz=(r.barrel_length * 0.17, 0.0, 0.0), rpy=(0.0, math.pi / 2, 0.0)),
            material=glass_mat,
            name="tilt_front_glass", material_class_id="glass.clear_transparent",
        )
        tilt_axis = (0.0, 0.0, 1.0)
        tilt_origin = (rail_x * 0.50 + block_length * 0.50, 0.0, 0.0)
        model.articulation(
            "tilt_axis",
            ArticulationType.REVOLUTE,
            parent=carriage,
            child=block,
            origin=Origin(xyz=tilt_origin),
            axis=tilt_axis,
            motion_limits=MotionLimits(
                effort=6.0, velocity=0.5, lower=-r.tilt_range_rad, upper=r.tilt_range_rad
            ),
            meta=_joint_meta(
                ArticulationType.REVOLUTE,
                tilt_axis,
                tilt_origin,
                (-r.tilt_range_rad, r.tilt_range_rad),
            ),
        )

    return model


def build_seeded_camera_lens(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_camera_lens(config_from_seed(seed), assets=assets)


def with_overrides(config: CameraLensConfig, **kwargs: object) -> CameraLensConfig:
    return replace(config, **kwargs)


def run_camera_lens_tests(object_model: ArticulatedObject, config: CameraLensConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}

    # The control rings (focus / zoom / unlock) rotate around the barrel they are
    # sleeved onto; that barrel<->ring interface is an intentional engagement.
    _barrel = object_model.get_part("barrel")
    _rings = [n for n in names if n.endswith("_ring") or n in ("tripod_collar",)]
    for _ring in _rings:
        ctx.allow_overlap(
            _barrel,
            object_model.get_part(_ring),
            reason="Control ring / collar is sleeved onto and rotates around the barrel.",
        )
        # A sleeved ring keeps running clearance from the barrel, so it reads as
        # geometrically isolated even though it is joint-mounted on the barrel.
        ctx.allow_isolated_part(
            object_model.get_part(_ring),
            reason="Control ring is joint-mounted on the barrel with running clearance.",
        )
    # The lens hood bayonets/twists onto the front with running clearance too.
    for _extra in ("hood", "lens_hood"):
        if _extra in names:
            ctx.allow_isolated_part(
                object_model.get_part(_extra),
                reason="Lens hood is joint-mounted on the barrel front with running clearance.",
            )
    for _i in range(len(_rings)):
        for _j in range(_i + 1, len(_rings)):
            ctx.allow_overlap(
                object_model.get_part(_rings[_i]), object_model.get_part(_rings[_j]),
                reason="Adjacent control rings sit side by side on the barrel.",
            )
    ctx.check(
        "identity parts present",
        {"barrel", "focus_ring"}.issubset(names),
        details=str(sorted(names)),
    )
    barrel_visuals = {v.name for v in object_model.get_part("barrel").visuals if v.name}
    ctx.check(
        "front glass exists", "front_glass" in barrel_visuals, details=str(sorted(barrel_visuals))
    )
    ring_joints = [
        j for j in object_model.articulations if j.name.endswith("_turn") and "ring" in j.name
    ]
    ctx.check(
        "at least one control ring joint",
        len(ring_joints) >= 1,
        details=f"rings={len(ring_joints)}",
    )
    for joint in ring_joints:
        ctx.check(
            f"{joint.name} axis optical", joint.axis == (1.0, 0.0, 0.0), details=f"{joint.axis}"
        )
        ctx.check(
            f"{joint.name} has metadata",
            {"type", "axis", "origin", "range"}.issubset(joint.meta),
            details=str(joint.meta),
        )
    if r.extension_enabled:
        ext = object_model.get_articulation("barrel_extension")
        ctx.check(
            "extension prismatic on optical axis",
            ext.articulation_type == ArticulationType.PRISMATIC and ext.axis == (1.0, 0.0, 0.0),
            details=f"{ext.articulation_type} {ext.axis}",
        )
    if r.tripod_collar_enabled:
        collar = object_model.get_articulation("tripod_collar_turn")
        ctx.check(
            "tripod collar turns on optical axis",
            collar.axis == (1.0, 0.0, 0.0),
            details=f"{collar.axis}",
        )
    if r.hood_enabled:
        hood = object_model.get_articulation("hood_twist")
        ctx.check("hood twist optical", hood.axis == (1.0, 0.0, 0.0), details=f"{hood.axis}")
    if r.tilt_shift_enabled:
        ctx.check(
            "tilt-shift rotate present",
            object_model.get_articulation("tilt_shift_rotate").parent == "barrel",
        )
        ctx.check(
            "tilt-shift shift present",
            object_model.get_articulation("shift_slide").parent == "tilt_shift_collar",
        )
        ctx.check(
            "tilt-shift tilt present",
            object_model.get_articulation("tilt_axis").parent == "shift_carriage",
        )
    for joint in object_model.articulations:
        if joint.articulation_type != ArticulationType.FIXED:
            ctx.check(
                f"{joint.name} has joint metadata",
                {"type", "axis", "origin", "range"}.issubset(joint.meta),
                details=str(joint.meta),
            )
    ctx.check(
        "rotation-only lens has no prismatic joints",
        all(
            joint.articulation_type != ArticulationType.PRISMATIC
            for joint in object_model.articulations
        ),
        details=str(
            [
                joint.name
                for joint in object_model.articulations
                if joint.articulation_type == ArticulationType.PRISMATIC
            ]
        ),
    )
    return ctx.report()
