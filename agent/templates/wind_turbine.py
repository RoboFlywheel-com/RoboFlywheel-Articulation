# SPDX-License-Identifier: Apache-2.0

"""Wind turbine — modular procedural template."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    LatheGeometry,
    LoftGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True

SupportModule = Literal[
    "monopole_tower", "tower_with_foundation", "bearing_module_stack", "braced_short_mast"
]
NacelleModule = Literal["yaw_continuous", "yaw_revolute_bounded", "yaw_fixed"]
RotorModule = Literal["monolithic_rotor", "pitching_blades", "fixed_socket_blades"]
BladeRootModule = Literal["integrated_root_cuff", "captured_pitch_socket", "wear_ring_socket"]
SpinnerStyle = Literal["cone", "ogive", "sphere_cap", "exposed_flange"]
NacelleDetail = Literal["smooth_shell", "service_box", "vented_rear", "roof_mast"]
TowerDetail = Literal["ladder", "section_rings", "warning_band", "access_door"]
BladeTipStyle = Literal["plain", "swept_tip"]
AccessoryModule = Literal["tail_vane", "access_hatch", "root_guard", "lock_pin"]
PaletteTheme = Literal["utility_white", "offshore_gray", "small_farm", "safety_orange"]

SUPPORT_MODULES: tuple[SupportModule, ...] = (
    "monopole_tower",
    "tower_with_foundation",
    "bearing_module_stack",
    "braced_short_mast",
)
NACELLE_MODULES: tuple[NacelleModule, ...] = ("yaw_continuous", "yaw_revolute_bounded", "yaw_fixed")
ROTOR_MODULES: tuple[RotorModule, ...] = (
    "monolithic_rotor",
    "pitching_blades",
    "fixed_socket_blades",
)
ROOT_MODULES: tuple[BladeRootModule, ...] = (
    "integrated_root_cuff",
    "captured_pitch_socket",
    "wear_ring_socket",
)
SPINNER_STYLES: tuple[SpinnerStyle, ...] = ("cone", "ogive", "sphere_cap", "exposed_flange")
NACELLE_DETAILS: tuple[NacelleDetail, ...] = (
    "smooth_shell",
    "service_box",
    "vented_rear",
    "roof_mast",
)
TOWER_DETAILS: tuple[TowerDetail, ...] = (
    "ladder",
    "section_rings",
    "warning_band",
    "access_door",
)
BLADE_TIP_STYLES: tuple[BladeTipStyle, ...] = ("plain", "swept_tip")
ACCESSORY_MODULES: tuple[AccessoryModule, ...] = (
    "tail_vane",
    "access_hatch",
    "root_guard",
    "lock_pin",
)

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "utility_white": {
        "tower": (0.82, 0.84, 0.82, 1),
        "nacelle": (0.90, 0.91, 0.88, 1),
        "blade": (0.88, 0.90, 0.88, 1),
        "steel": (0.60, 0.62, 0.64, 1),
        "dark": (0.08, 0.09, 0.10, 1),
        "warning": (0.86, 0.15, 0.07, 1),
    },
    "offshore_gray": {
        "tower": (0.55, 0.58, 0.60, 1),
        "nacelle": (0.70, 0.72, 0.73, 1),
        "blade": (0.76, 0.78, 0.78, 1),
        "steel": (0.45, 0.47, 0.49, 1),
        "dark": (0.06, 0.07, 0.08, 1),
        "warning": (0.82, 0.12, 0.08, 1),
    },
    "small_farm": {
        "tower": (0.38, 0.42, 0.38, 1),
        "nacelle": (0.82, 0.82, 0.76, 1),
        "blade": (0.86, 0.84, 0.76, 1),
        "steel": (0.52, 0.52, 0.48, 1),
        "dark": (0.10, 0.09, 0.07, 1),
        "warning": (0.92, 0.38, 0.10, 1),
    },
    "safety_orange": {
        "tower": (0.78, 0.78, 0.74, 1),
        "nacelle": (0.91, 0.74, 0.22, 1),
        "blade": (0.92, 0.88, 0.74, 1),
        "steel": (0.55, 0.57, 0.58, 1),
        "dark": (0.10, 0.07, 0.04, 1),
        "warning": (0.95, 0.18, 0.05, 1),
    },
}


@dataclass(frozen=True)
class WindTurbineConfig:
    support_module: SupportModule | None = None
    nacelle_module: NacelleModule | None = None
    rotor_module: RotorModule | None = None
    blade_root_module: BladeRootModule | None = None
    spinner_style: SpinnerStyle | None = None
    nacelle_detail: NacelleDetail | None = None
    tower_detail: TowerDetail | None = None
    blade_tip_style: BladeTipStyle | None = None
    accessory_modules: tuple[AccessoryModule, ...] | None = None
    blade_count: int = 3
    palette_theme: PaletteTheme = "utility_white"
    tower_height: float = 1.05
    tower_base_radius: float = 0.075
    tower_top_radius: float = 0.042
    nacelle_length: float = 0.34
    nacelle_width: float = 0.135
    nacelle_height: float = 0.115
    blade_span: float = 0.40
    hub_radius: float = 0.050
    pin_stroke: float = 0.10
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["utility_white"])
    )


@dataclass(frozen=True)
class ResolvedWindTurbineConfig:
    support_module: SupportModule
    nacelle_module: NacelleModule
    rotor_module: RotorModule
    blade_root_module: BladeRootModule
    spinner_style: SpinnerStyle
    nacelle_detail: NacelleDetail
    tower_detail: TowerDetail
    blade_tip_style: BladeTipStyle
    accessory_modules: tuple[AccessoryModule, ...]
    blade_count: int
    palette_theme: PaletteTheme
    tower_height: float
    tower_base_radius: float
    tower_top_radius: float
    nacelle_length: float
    nacelle_width: float
    nacelle_height: float
    blade_span: float
    hub_radius: float
    pin_stroke: float
    yaw_parent: str
    yaw_origin: tuple[float, float, float]
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_z() -> tuple[float, float, float]:
    return (0.0, 0.0, 0.0)


def _weighted_blade_count(rng: random.Random) -> int:
    return rng.choices((2, 3, 4, 5), weights=(0.15, 0.50, 0.25, 0.10), k=1)[0]


def _mesh(model: ArticulatedObject, geometry: MeshGeometry, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


def _lathe_along_x(profile: list[tuple[float, float]], *, segments: int = 48) -> MeshGeometry:
    return LatheGeometry(profile, segments=segments).rotate_y(math.pi / 2.0)


def _oval_section(
    x: float,
    width: float,
    height: float,
    *,
    z_center: float = 0.0,
    segments: int = 28,
) -> list[tuple[float, float, float]]:
    return [
        (
            x,
            math.cos(math.tau * i / segments) * width * 0.5,
            z_center + math.sin(math.tau * i / segments) * height * 0.5,
        )
        for i in range(segments)
    ]


def _loft_sections_raw(sections: list[list[tuple[float, float, float]]]) -> MeshGeometry:
    geom = MeshGeometry()
    rings: list[list[int]] = []
    for section in sections:
        rings.append([geom.add_vertex(x, y, z) for x, y, z in section])
    for a, b in zip(rings[:-1], rings[1:]):
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            geom.add_face(a[i], a[j], b[j])
            geom.add_face(a[i], b[j], b[i])
    for ring, reverse in ((rings[0], True), (rings[-1], False)):
        cx = sum(sections[0 if reverse else -1][i][0] for i in range(len(ring))) / len(ring)
        cy = sum(sections[0 if reverse else -1][i][1] for i in range(len(ring))) / len(ring)
        cz = sum(sections[0 if reverse else -1][i][2] for i in range(len(ring))) / len(ring)
        center = geom.add_vertex(cx, cy, cz)
        for i in range(len(ring)):
            j = (i + 1) % len(ring)
            if reverse:
                geom.add_face(center, ring[j], ring[i])
            else:
                geom.add_face(center, ring[i], ring[j])
    return geom


def _tower_shell_geometry(r: ResolvedWindTurbineConfig) -> MeshGeometry:
    h = r.tower_height
    return LatheGeometry(
        [
            (0.0, 0.0),
            (r.tower_base_radius * 1.10, 0.0),
            (r.tower_base_radius, h * 0.06),
            ((r.tower_base_radius + r.tower_top_radius) * 0.53, h * 0.58),
            (r.tower_top_radius, h),
            (0.0, h),
        ],
        segments=56,
    )


def _nacelle_shell_geometry(r: ResolvedWindTurbineConfig) -> MeshGeometry:
    L, W, H = r.nacelle_length, r.nacelle_width, r.nacelle_height
    sections = [
        _oval_section(-L * 0.34, W * 0.58, H * 0.62, z_center=H * 0.09),
        _oval_section(-L * 0.18, W * 0.92, H * 0.96, z_center=H * 0.11),
        _oval_section(L * 0.24, W, H, z_center=H * 0.12),
        _oval_section(L * 0.55, W * 0.78, H * 0.76, z_center=H * 0.10),
        _oval_section(L * 0.70, W * 0.44, H * 0.44, z_center=H * 0.06),
    ]
    return _loft_sections_raw(sections)


def _hub_shell_geometry(r: ResolvedWindTurbineConfig) -> MeshGeometry:
    hr = r.hub_radius
    return _lathe_along_x(
        [
            (0.0, -hr * 0.95),
            (hr * 0.72, -hr * 0.90),
            (hr * 1.10, -hr * 0.30),
            (hr * 1.18, hr * 0.34),
            (hr * 0.78, hr * 0.92),
            (0.0, hr * 1.08),
        ],
        segments=56,
    )


def _spinner_geometry(r: ResolvedWindTurbineConfig) -> MeshGeometry:
    hr = r.hub_radius
    return _lathe_along_x(
        [
            (0.0, hr * 0.28),
            (hr * 0.58, hr * 0.26),
            (hr * 0.86, hr * 0.48),
            (hr * 0.70, hr * 0.78),
            (hr * 0.28, hr * 1.05),
            (0.0, hr * 1.16),
        ],
        segments=56,
    )


def _cone_spinner_geometry(r: ResolvedWindTurbineConfig) -> MeshGeometry:
    hr = r.hub_radius
    return _lathe_along_x(
        [
            (0.0, hr * 0.16),
            (hr * 0.82, hr * 0.18),
            (hr * 0.92, hr * 0.42),
            (hr * 0.40, hr * 0.92),
            (0.0, hr * 1.22),
        ],
        segments=52,
    )


def _blade_shell_geometry(r: ResolvedWindTurbineConfig) -> MeshGeometry:
    span = r.blade_span
    root_chord = max(r.hub_radius * 1.55, span * 0.13)
    tip_chord = max(r.hub_radius * 0.28, span * 0.035)
    root_thickness = root_chord * 0.22
    loop = [
        (-0.18, -0.50),
        (0.30, -0.42),
        (0.50, -0.10),
        (0.34, 0.32),
        (0.06, 0.50),
        (-0.20, 0.44),
        (-0.38, 0.12),
        (-0.32, -0.34),
    ]
    stations = [
        (r.hub_radius * 0.20, root_chord, root_thickness, 16.0, 0.00),
        (span * 0.24, root_chord * 0.86, root_thickness * 0.74, 12.0, -0.01),
        (span * 0.52, root_chord * 0.60, root_thickness * 0.52, 7.5, -0.02),
        (span * 0.79, root_chord * 0.36, root_thickness * 0.34, 4.0, -0.03),
        (
            span,
            tip_chord,
            root_thickness * 0.19,
            1.5,
            -0.065 if r.blade_tip_style == "swept_tip" else -0.04,
        ),
    ]
    profiles: list[list[tuple[float, float, float]]] = []
    for z, chord, thickness, twist_deg, sweep_y in stations:
        twist = math.radians(twist_deg)
        c = math.cos(twist)
        s = math.sin(twist)
        section = []
        for x_factor, y_factor in loop:
            x = x_factor * thickness
            y = y_factor * chord + sweep_y
            section.append((x * c - y * s + r.hub_radius * 0.06, x * s + y * c, z))
        profiles.append(section)
    return LoftGeometry(profiles, cap=True, closed=True)


def _blade_mount_origin(angle: float, radial_distance: float, *, x_pos: float = 0.0) -> Origin:
    return Origin(
        xyz=(
            x_pos,
            -math.sin(angle) * radial_distance,
            math.cos(angle) * radial_distance,
        ),
        rpy=(angle, 0.0, 0.0),
    )


def _add_hub_socket_visual(part, r: ResolvedWindTurbineConfig, *, index: int, angle: float) -> None:
    hr = r.hub_radius
    base_radius = hr * 0.34
    if r.blade_root_module == "integrated_root_cuff":
        part.visual(
            Cylinder(radius=base_radius, length=hr * 1.55),
            origin=_blade_mount_origin(angle, hr * 0.82),
            material="steel",
            name=f"blade_root_cuff_{index}", material_class_id="metal.steel_bare",
        )
    elif r.blade_root_module == "captured_pitch_socket":
        part.visual(
            Cylinder(radius=hr * 0.31, length=hr * 1.52),
            origin=_blade_mount_origin(angle, hr * 0.88),
            material="steel",
            name=f"pitch_socket_sleeve_{index}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Cylinder(radius=hr * 0.46, length=hr * 0.28),
            origin=_blade_mount_origin(angle, hr * 1.45),
            material="dark",
            name=f"pitch_socket_outer_lip_{index}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=hr * 0.41, length=hr * 0.20),
            origin=_blade_mount_origin(angle, hr * 0.34),
            material="dark",
            name=f"pitch_socket_inner_lip_{index}", material_class_id="metal.blackened_gunmetal",
        )
    else:
        part.visual(
            Cylinder(radius=hr * 0.28, length=hr * 1.32),
            origin=_blade_mount_origin(angle, hr * 0.76),
            material="dark",
            name=f"root_bearing_sleeve_{index}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=hr * 0.47, length=hr * 0.22),
            origin=_blade_mount_origin(angle, hr * 1.30),
            material="steel",
            name=f"socket_wear_ring_{index}", material_class_id="metal.steel_bare",
        )


def _add_blade_root_visual(part, r: ResolvedWindTurbineConfig) -> None:
    hr = r.hub_radius
    if r.blade_root_module == "captured_pitch_socket":
        part.visual(
            Cylinder(radius=hr * 0.24, length=hr * 1.12),
            origin=Origin(xyz=(0.0, 0.0, hr * 0.22)),
            material="dark",
            name="root_spindle", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=hr * 0.36, length=hr * 0.24),
            origin=Origin(xyz=(0.0, 0.0, hr * 0.72)),
            material="steel",
            name="root_flange", material_class_id="metal.steel_bare",
        )
    elif r.blade_root_module == "wear_ring_socket":
        part.visual(
            Cylinder(radius=hr * 0.23, length=hr * 1.00),
            origin=Origin(xyz=(0.0, 0.0, hr * 0.18)),
            material="dark",
            name="root_bearing", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=hr * 0.34, length=hr * 0.20),
            origin=Origin(xyz=(0.0, 0.0, hr * 0.66)),
            material="steel",
            name="root_wear_collar", material_class_id="metal.steel_bare",
        )
    else:
        part.visual(
            Cylinder(radius=hr * 0.25, length=hr * 1.05),
            origin=Origin(xyz=(0.0, 0.0, hr * 0.24)),
            material="steel",
            name="root_cuff", material_class_id="metal.steel_bare",
        )


def _add_tower_detail(tower, r: ResolvedWindTurbineConfig) -> None:
    h = r.tower_height
    if r.tower_detail == "ladder":
        # Rails sit on the tower surface (radial distance < base radius) so the
        # rails and rungs embed into the hollow shell instead of floating off it.
        rail_y = -r.tower_base_radius * 0.90
        rail_span = min(h * 0.58, 0.72)
        rail_z = max(0.18, rail_span * 0.5 + 0.10)
        for side, x in enumerate((-r.tower_base_radius * 0.32, r.tower_base_radius * 0.32)):
            tower.visual(
                Cylinder(radius=r.tower_base_radius * 0.045, length=rail_span),
                origin=Origin(xyz=(x, rail_y, rail_z)),
                material="steel",
                name=f"ladder_rail_{side}", material_class_id="metal.steel_galvanized",
            )
        for i in range(6):
            z = rail_z - rail_span * 0.42 + i * rail_span * 0.16
            tower.visual(
                Cylinder(radius=r.tower_base_radius * 0.038, length=r.tower_base_radius * 0.68),
                origin=Origin(xyz=(0.0, rail_y, z), rpy=_cyl_x()),
                material="steel",
                name=f"ladder_rung_{i}", material_class_id="metal.steel_galvanized",
            )
    elif r.tower_detail == "section_rings":
        # Ring radius must follow the actual lathe taper (which bulges above a
        # straight base->top line in the mid-section); a linearly interpolated
        # radius is too small there and leaves the ring floating inside the
        # hollow tower shell.
        b, t = r.tower_base_radius, r.tower_top_radius
        mid_r, mid_z = (b + t) * 0.53, 0.58

        def _tower_radius_at(f: float) -> float:
            if f <= 0.06:
                return b
            if f <= mid_z:
                return b + (mid_r - b) * (f - 0.06) / (mid_z - 0.06)
            return mid_r + (t - mid_r) * (f - mid_z) / (1.0 - mid_z)

        for i, z_frac in enumerate((0.25, 0.48, 0.70)):
            z = h * z_frac
            radius = _tower_radius_at(z_frac)
            tower.visual(
                Cylinder(radius=radius * 1.06, length=0.014),
                origin=Origin(xyz=(0.0, 0.0, z)),
                material="steel",
                name=f"section_ring_{i}", material_class_id="metal.paint_coated",
            )
    elif r.tower_detail == "warning_band":
        tower.visual(
            Cylinder(radius=(r.tower_base_radius + r.tower_top_radius) * 0.60, length=0.026),
            origin=Origin(xyz=(0.0, 0.0, h * 0.42)),
            material="warning",
            name="warning_band", material_class_id="metal.paint_coated",
        )
    else:
        tower.visual(
            Box((r.tower_base_radius * 0.52, 0.010, min(h * 0.17, 0.24))),
            origin=Origin(xyz=(0.0, -r.tower_base_radius * 1.03, min(h * 0.20, 0.28))),
            material="dark",
            name="tower_access_door", material_class_id="metal.paint_coated",
        )


def _add_nacelle_detail(nacelle, r: ResolvedWindTurbineConfig) -> None:
    L, W, H = r.nacelle_length, r.nacelle_width, r.nacelle_height
    if r.nacelle_detail == "smooth_shell":
        return
    if r.nacelle_detail == "service_box":
        nacelle.visual(
            Box((L * 0.30, 0.018, H * 0.34)),
            origin=Origin(xyz=(L * 0.16, -W * 0.50, H * 0.14)),
            material="steel",
            name="service_panel_frame", material_class_id="metal.paint_coated",
        )
        nacelle.visual(
            Box((L * 0.22, W * 0.12, H * 0.07)),
            origin=Origin(xyz=(L * 0.18, 0.0, H * 0.68 - 0.010)),
            material="dark",
            name="roof_lift_lug", material_class_id="metal.blackened_gunmetal",
        )
    elif r.nacelle_detail == "vented_rear":
        for i in range(4):
            nacelle.visual(
                Box((0.014, W * 0.58, H * 0.040)),
                origin=Origin(xyz=(-L * 0.34, 0.0, H * (0.02 + i * 0.11))),
                material="dark",
                name=f"rear_louver_{i}", material_class_id="metal.paint_coated",
            )
        nacelle.visual(
            Cylinder(radius=H * 0.20, length=0.028),
            origin=Origin(xyz=(-L * 0.34, 0.0, H * 0.18), rpy=_cyl_x()),
            material="dark",
            name="rear_cooling_port", material_class_id="metal.blackened_gunmetal",
        )
    else:
        nacelle.visual(
            Cylinder(radius=H * 0.035, length=H * 0.80),
            origin=Origin(xyz=(-L * 0.08, 0.0, H * 0.82)),
            material="dark",
            name="weather_mast", material_class_id="metal.blackened_gunmetal",
        )
        nacelle.visual(
            Box((L * 0.30, W * 0.035, H * 0.04)),
            origin=Origin(xyz=(-L * 0.08, 0.0, H * 1.24)),
            material="dark",
            name="wind_vane_boom", material_class_id="metal.blackened_gunmetal",
        )
        nacelle.visual(
            Box((L * 0.12, W * 0.030, H * 0.18)),
            origin=Origin(xyz=(-L * 0.22, 0.0, H * 1.24)),
            material="dark",
            name="wind_vane_tail", material_class_id="metal.blackened_gunmetal",
        )


def config_from_seed(seed: int) -> WindTurbineConfig:
    if seed == 0:
        return WindTurbineConfig(
            support_module="monopole_tower",
            nacelle_module="yaw_continuous",
            rotor_module="monolithic_rotor",
            blade_root_module="captured_pitch_socket",
            spinner_style="ogive",
            nacelle_detail="smooth_shell",
            tower_detail="section_rings",
            blade_tip_style="plain",
            accessory_modules=("tail_vane",),
            blade_count=3,
        )
    rng = random.Random(seed)
    accessories = tuple(a for a in ACCESSORY_MODULES if rng.random() < 0.42)
    if not accessories:
        accessories = (rng.choice(ACCESSORY_MODULES),)
    return WindTurbineConfig(
        support_module=rng.choice(SUPPORT_MODULES),  # type: ignore[arg-type]
        nacelle_module=rng.choice(NACELLE_MODULES),  # type: ignore[arg-type]
        rotor_module=rng.choice(ROTOR_MODULES),  # type: ignore[arg-type]
        blade_root_module=rng.choice(ROOT_MODULES),  # type: ignore[arg-type]
        spinner_style=rng.choice(SPINNER_STYLES),  # type: ignore[arg-type]
        nacelle_detail=rng.choice(NACELLE_DETAILS),  # type: ignore[arg-type]
        tower_detail=rng.choice(TOWER_DETAILS),  # type: ignore[arg-type]
        blade_tip_style=rng.choice(BLADE_TIP_STYLES),  # type: ignore[arg-type]
        accessory_modules=accessories,  # type: ignore[arg-type]
        blade_count=_weighted_blade_count(rng),
        palette_theme=rng.choice(tuple(PALETTES.keys())),  # type: ignore[arg-type]
        tower_height=rng.uniform(0.55, 1.65),
        tower_base_radius=rng.uniform(0.055, 0.12),
        tower_top_radius=rng.uniform(0.035, 0.070),
        nacelle_length=rng.uniform(0.26, 0.45),
        nacelle_width=rng.uniform(0.105, 0.17),
        nacelle_height=rng.uniform(0.09, 0.15),
        blade_span=rng.uniform(0.28, 0.62),
        hub_radius=rng.uniform(0.038, 0.070),
        pin_stroke=rng.uniform(0.05, 0.18),
    )


def resolve_config(config: WindTurbineConfig) -> ResolvedWindTurbineConfig:
    support = config.support_module or "monopole_tower"
    nacelle = config.nacelle_module or "yaw_continuous"
    rotor = config.rotor_module or "monolithic_rotor"
    blade_root = config.blade_root_module or "captured_pitch_socket"
    spinner = config.spinner_style or "ogive"
    nacelle_detail = config.nacelle_detail or "smooth_shell"
    tower_detail = config.tower_detail or "section_rings"
    blade_tip = config.blade_tip_style or "plain"
    accessories = config.accessory_modules or ("tail_vane",)
    if support not in SUPPORT_MODULES:
        raise ValueError(f"Unsupported support_module: {support!r}")
    if nacelle not in NACELLE_MODULES:
        raise ValueError(f"Unsupported nacelle_module: {nacelle!r}")
    if rotor not in ROTOR_MODULES:
        raise ValueError(f"Unsupported rotor_module: {rotor!r}")
    if blade_root not in ROOT_MODULES:
        raise ValueError(f"Unsupported blade_root_module: {blade_root!r}")
    if spinner not in SPINNER_STYLES:
        raise ValueError(f"Unsupported spinner_style: {spinner!r}")
    if nacelle_detail not in NACELLE_DETAILS:
        raise ValueError(f"Unsupported nacelle_detail: {nacelle_detail!r}")
    if tower_detail not in TOWER_DETAILS:
        raise ValueError(f"Unsupported tower_detail: {tower_detail!r}")
    if blade_tip not in BLADE_TIP_STYLES:
        raise ValueError(f"Unsupported blade_tip_style: {blade_tip!r}")
    if any(a not in ACCESSORY_MODULES for a in accessories):
        raise ValueError(f"Unsupported accessory_modules: {accessories!r}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")
    h = _clamp(config.tower_height, 0.34, 2.0)
    base_r = _clamp(config.tower_base_radius, 0.045, 0.14)
    top_r = min(_clamp(config.tower_top_radius, 0.030, 0.090), base_r * 0.82)
    yaw_parent = "bearing_module" if support == "bearing_module_stack" else "tower"
    yaw_origin = (0.0, 0.0, 0.0675) if yaw_parent == "bearing_module" else (0.0, 0.0, h)
    return ResolvedWindTurbineConfig(
        support_module=support,
        nacelle_module=nacelle,
        rotor_module=rotor,
        blade_root_module=blade_root,
        spinner_style=spinner,
        nacelle_detail=nacelle_detail,
        tower_detail=tower_detail,
        blade_tip_style=blade_tip,
        accessory_modules=tuple(dict.fromkeys(accessories)),
        blade_count=max(2, min(5, int(config.blade_count))),
        palette_theme=config.palette_theme,
        tower_height=h,
        tower_base_radius=base_r,
        tower_top_radius=top_r,
        nacelle_length=_clamp(config.nacelle_length, 0.22, 0.55),
        nacelle_width=_clamp(config.nacelle_width, 0.08, 0.20),
        nacelle_height=_clamp(config.nacelle_height, 0.07, 0.18),
        blade_span=_clamp(config.blade_span, 0.22, 0.75),
        hub_radius=_clamp(config.hub_radius, 0.030, 0.085),
        pin_stroke=_clamp(config.pin_stroke, 0.03, 0.07),
        yaw_parent=yaw_parent,
        yaw_origin=yaw_origin,
        palette=dict(PALETTES[config.palette_theme]),
    )


def _build_support(model: ArticulatedObject, r: ResolvedWindTurbineConfig) -> None:
    tower = model.part("tower")
    h = r.tower_height
    tower.visual(
        Cylinder(radius=r.tower_base_radius * 1.20, length=0.055),
        origin=Origin(xyz=(0, 0, 0.0275)),
        material="steel",
        name="foundation_pad", material_class_id="metal.steel_bare",
    )
    tower.visual(
        _mesh(model, _tower_shell_geometry(r), "wind_turbine_tapered_tower"),
        material="tower",
        name="tapered_tower", material_class_id="metal.paint_coated",
    )
    tower.visual(
        Cylinder(radius=r.tower_top_radius * 1.35, length=0.060),
        origin=Origin(xyz=(0, 0, h - 0.012)),
        material="steel",
        name="head_flange", material_class_id="metal.steel_bare",
    )
    _add_tower_detail(tower, r)
    if r.support_module == "braced_short_mast":
        tower.visual(
            Cylinder(radius=r.tower_base_radius * 1.55, length=0.075),
            origin=Origin(xyz=(0, 0, 0.075)),
            material="steel",
            name="short_mast_base_collar", material_class_id="metal.steel_bare",
        )
        for i, angle in enumerate((0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)):
            x = math.cos(angle) * r.tower_base_radius * 1.65
            y = math.sin(angle) * r.tower_base_radius * 1.65
            tower.visual(
                Cylinder(radius=r.tower_base_radius * 0.13, length=0.12),
                origin=Origin(xyz=(x, y, 0.060)),
                material="steel",
                name=f"anchor_post_{i}", material_class_id="metal.steel_galvanized",
            )
    if r.support_module == "tower_with_foundation":
        foundation = model.part("foundation")
        foundation.visual(
            Cylinder(radius=r.tower_base_radius * 2.4, length=0.060),
            origin=Origin(xyz=(0, 0, -0.030)),
            material="steel",
            name="concrete_puck", material_class_id="concrete.smooth_cast",
        )
        foundation.visual(
            Box((r.tower_base_radius * 3.8, r.tower_base_radius * 3.8, 0.040)),
            origin=Origin(xyz=(0, 0, -0.070)),
            material="steel",
            name="square_footing", material_class_id="concrete.smooth_cast",
        )
        model.articulation(
            "tower_to_foundation",
            ArticulationType.FIXED,
            parent=tower,
            child=foundation,
            origin=Origin(xyz=(0, 0, 0.0)),
        )
    if r.support_module == "bearing_module_stack":
        bearing = model.part("bearing_module")
        bearing.visual(
            Cylinder(radius=r.tower_top_radius * 1.55, length=0.095),
            origin=Origin(xyz=(0, 0, 0)),
            material="steel",
            name="yaw_bearing_drum", material_class_id="metal.steel_bare",
        )
        bearing.visual(
            Cylinder(radius=r.tower_top_radius * 1.25, length=0.045),
            origin=Origin(xyz=(0, 0, 0.045)),
            material="dark",
            name="slew_ring", material_class_id="metal.blackened_gunmetal",
        )
        model.articulation(
            "tower_to_bearing",
            ArticulationType.FIXED,
            parent=tower,
            child=bearing,
            origin=Origin(xyz=(0, 0, h)),
        )


def _build_nacelle(model: ArticulatedObject, r: ResolvedWindTurbineConfig) -> None:
    nacelle = model.part("nacelle")
    L, W, H = r.nacelle_length, r.nacelle_width, r.nacelle_height
    nacelle.visual(
        Cylinder(radius=r.tower_top_radius * 1.20, length=0.060),
        origin=Origin(rpy=_cyl_z()),
        material="steel",
        name="yaw_collar", material_class_id="metal.steel_bare",
    )
    nacelle.visual(
        _mesh(model, _nacelle_shell_geometry(r), "wind_turbine_nacelle_shell"),
        material="nacelle",
        name="nacelle_shell", material_class_id="metal.paint_coated",
    )
    nacelle.visual(
        Box((L * 0.62, W * 0.70, H * 0.28)),
        origin=Origin(xyz=(L * 0.42, 0, -H * 0.28)),
        material="steel",
        name="bedplate", material_class_id="metal.steel_bare",
    )
    nacelle.visual(
        Cylinder(radius=H * 0.34, length=0.090),
        origin=Origin(xyz=(L * 0.82, 0, H * 0.03), rpy=_cyl_x()),
        material="steel",
        name="front_bearing_collar", material_class_id="metal.steel_bare",
    )
    nacelle.visual(
        Cylinder(radius=H * 0.26, length=0.070),
        origin=Origin(xyz=(L * 0.94, 0, H * 0.03), rpy=_cyl_x()),
        material="dark",
        name="shaft_housing", material_class_id="metal.blackened_gunmetal",
    )
    _add_nacelle_detail(nacelle, r)
    if "tail_vane" in r.accessory_modules:
        nacelle.visual(
            Box((L * 0.55, W * 0.16, H * 0.18)),
            origin=Origin(xyz=(-L * 0.30, 0, H * 0.10)),
            material="steel",
            name="tail_boom", material_class_id="metal.paint_coated",
        )
        nacelle.visual(
            Box((L * 0.18, W * 0.08, H * 0.88)),
            origin=Origin(xyz=(-L * 0.60, 0, H * 0.26)),
            material="blade",
            name="tail_vane", material_class_id="plastic.opaque_glossy_molded",
        )
    parent = model.get_part(r.yaw_parent)
    joint_type = {
        "yaw_continuous": ArticulationType.CONTINUOUS,
        "yaw_revolute_bounded": ArticulationType.REVOLUTE,
        "yaw_fixed": ArticulationType.FIXED,
    }[r.nacelle_module]
    limits = None
    if joint_type == ArticulationType.REVOLUTE:
        limits = MotionLimits(effort=80, velocity=0.8, lower=-1.25, upper=1.25)
    elif joint_type == ArticulationType.CONTINUOUS:
        limits = MotionLimits(effort=80, velocity=0.8)
    model.articulation(
        "tower_to_nacelle",
        joint_type,
        parent=parent,
        child=nacelle,
        origin=Origin(xyz=r.yaw_origin),
        axis=(0, 0, 1),
        motion_limits=limits,
    )


def _build_rotor(model: ArticulatedObject, r: ResolvedWindTurbineConfig) -> None:
    hub = model.part("rotor")
    hub.visual(
        Cylinder(radius=r.hub_radius * 0.52, length=0.11),
        origin=Origin(xyz=(-r.hub_radius * 1.10, 0, 0), rpy=_cyl_x()),
        material="dark",
        name="main_shaft", material_class_id="metal.blackened_gunmetal",
    )
    hub.visual(
        _mesh(model, _hub_shell_geometry(r), "wind_turbine_hub_shell"),
        material="steel",
        name="hub_barrel", material_class_id="metal.steel_bare",
    )
    if r.spinner_style == "cone":
        hub.visual(
            _mesh(model, _cone_spinner_geometry(r), "wind_turbine_cone_spinner"),
            material="nacelle",
            name="cone_spinner", material_class_id="metal.paint_coated",
        )
    elif r.spinner_style == "ogive":
        hub.visual(
            _mesh(model, _spinner_geometry(r), "wind_turbine_ogive_spinner"),
            material="nacelle",
            name="ogive_spinner", material_class_id="metal.paint_coated",
        )
    elif r.spinner_style == "sphere_cap":
        hub.visual(
            Sphere(radius=r.hub_radius * 0.78),
            origin=Origin(xyz=(r.hub_radius * 0.72, 0, 0)),
            material="nacelle",
            name="sphere_spinner_cap", material_class_id="metal.paint_coated",
        )
    else:
        hub.visual(
            Cylinder(radius=r.hub_radius * 1.02, length=r.hub_radius * 0.26),
            origin=Origin(xyz=(r.hub_radius * 0.62, 0, 0), rpy=_cyl_x()),
            material="steel",
            name="exposed_front_flange", material_class_id="metal.steel_bare",
        )
        for bolt_i in range(8):
            bolt_angle = math.tau * bolt_i / 8.0
            hub.visual(
                Cylinder(radius=r.hub_radius * 0.055, length=r.hub_radius * 0.10),
                origin=Origin(
                    xyz=(
                        r.hub_radius * 0.78,
                        math.cos(bolt_angle) * r.hub_radius * 0.70,
                        math.sin(bolt_angle) * r.hub_radius * 0.70,
                    ),
                    rpy=_cyl_x(),
                ),
                material="dark",
                name=f"flange_bolt_{bolt_i}", material_class_id="metal.blackened_gunmetal",
            )
    blade_mesh = _mesh(model, _blade_shell_geometry(r), "wind_turbine_blade_airfoil")
    root_distance = r.hub_radius * 1.02
    for i in range(r.blade_count):
        angle = 2.0 * math.pi * i / r.blade_count
        _add_hub_socket_visual(hub, r, index=i, angle=angle)
        if r.rotor_module == "monolithic_rotor":
            hub.visual(
                blade_mesh,
                origin=_blade_mount_origin(angle, root_distance),
                material="blade",
                name=f"blade_shell_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
    model.articulation(
        "nacelle_to_rotor",
        ArticulationType.CONTINUOUS,
        parent=model.get_part("nacelle"),
        child=hub,
        origin=Origin(xyz=(r.nacelle_length * 0.96, 0, r.nacelle_height * 0.03)),
        axis=(1, 0, 0),
        motion_limits=MotionLimits(effort=90, velocity=20),
    )
    if r.rotor_module != "monolithic_rotor":
        for i in range(r.blade_count):
            angle = 2.0 * math.pi * i / r.blade_count
            blade = model.part(f"blade_{i}")
            _add_blade_root_visual(blade, r)
            blade.visual(
                blade_mesh,
                material="blade",
                name="blade_shell", material_class_id="plastic.opaque_glossy_molded",
            )
            joint_type = (
                ArticulationType.REVOLUTE
                if r.rotor_module == "pitching_blades"
                else ArticulationType.FIXED
            )
            limits = (
                MotionLimits(effort=6, velocity=1.0, lower=-0.35, upper=1.30)
                if joint_type == ArticulationType.REVOLUTE
                else None
            )
            model.articulation(
                f"hub_to_blade_{i}",
                joint_type,
                parent=hub,
                child=blade,
                origin=_blade_mount_origin(angle, root_distance),
                axis=(0.0, 0.0, 1.0),
                motion_limits=limits,
            )


def _build_accessories(model: ArticulatedObject, r: ResolvedWindTurbineConfig) -> None:
    nacelle = model.get_part("nacelle")
    L, W, H = r.nacelle_length, r.nacelle_width, r.nacelle_height
    if "access_hatch" in r.accessory_modules:
        hatch = model.part("access_hatch")
        hatch.visual(
            Box((L * 0.24, 0.020, H * 0.46)),
            origin=Origin(xyz=(0, 0, 0)),
            material="dark",
            name="hatch_panel", material_class_id="metal.paint_coated",
        )
        model.articulation(
            "nacelle_to_hatch",
            ArticulationType.REVOLUTE,
            parent=nacelle,
            child=hatch,
            origin=Origin(xyz=(L * 0.42, -W * 0.46, H * 0.12)),
            axis=(0, 0, -1),
            motion_limits=MotionLimits(effort=2, velocity=1.4, lower=0, upper=1.75),
        )
    if "root_guard" in r.accessory_modules:
        guard = model.part("root_guard")
        guard.visual(
            Cylinder(radius=r.hub_radius * 1.55, length=0.020),
            origin=Origin(rpy=_cyl_x()),
            material="steel",
            name="guard_ring", material_class_id="metal.steel_galvanized",
        )
        guard.visual(
            Box((0.018, r.hub_radius * 2.8, 0.018)),
            origin=Origin(),
            material="steel",
            name="guard_crossbar", material_class_id="metal.steel_galvanized",
        )
        model.articulation(
            "nacelle_to_guard",
            ArticulationType.FIXED,
            parent=nacelle,
            child=guard,
            origin=Origin(xyz=(L + 0.012, 0, 0)),
        )
    if "lock_pin" in r.accessory_modules:
        pin = model.part("lock_pin")
        pin.visual(
            Cylinder(radius=0.012, length=0.12),
            origin=Origin(rpy=_cyl_x()),
            material="dark",
            name="sliding_lock_pin", material_class_id="metal.blackened_gunmetal",
        )
        pin.visual(
            Box((0.025, 0.045, 0.030)),
            origin=Origin(xyz=(-0.045, 0, 0)),
            material="steel",
            name="pin_handle", material_class_id="metal.steel_bare",
        )
        model.articulation(
            "nacelle_to_lock_pin",
            ArticulationType.PRISMATIC,
            parent=nacelle,
            child=pin,
            origin=Origin(xyz=(L * 0.92, 0, -H * 0.20)),
            axis=(1, 0, 0),
            motion_limits=MotionLimits(effort=8, velocity=0.15, lower=0, upper=r.pin_stroke),
        )


def build_wind_turbine(
    config: WindTurbineConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="wind_turbine", assets=assets)
    for name, rgba in r.palette.items():
        model.material(name, rgba=rgba)
    _build_support(model, r)
    _build_nacelle(model, r)
    _build_rotor(model, r)
    _build_accessories(model, r)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_wind_turbine(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_wind_turbine(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedWindTurbineConfig) -> list[tuple[str, str]]:
    return [
        ("support", r.support_module),
        ("nacelle", r.nacelle_module),
        ("rotor", r.rotor_module),
        ("blade_root", r.blade_root_module),
        ("spinner", r.spinner_style),
        ("nacelle_detail", r.nacelle_detail),
        ("tower_detail", r.tower_detail),
        ("blade_tip", r.blade_tip_style),
        ("blade_multiplicity", f"{r.blade_count}_blade"),
        ("accessories", "+".join(r.accessory_modules)),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def run_wind_turbine_tests(
    object_model: ArticulatedObject, config: WindTurbineConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}
    ctx.check("tower_present", "tower" in names)
    ctx.check("nacelle_present", "nacelle" in names)
    ctx.check("rotor_present", "rotor" in names)
    ctx.check("yaw_axis_z", joints["tower_to_nacelle"].axis == (0, 0, 1))
    ctx.check("spin_axis_x", joints["nacelle_to_rotor"].axis == (1, 0, 0))
    if r.rotor_module != "monolithic_rotor":
        blade_names = {f"blade_{i}" for i in range(r.blade_count)}
        ctx.check(
            "blade_part_count",
            blade_names.issubset(names),
            details=f"missing={sorted(blade_names - names)}",
        )
        blade_joints = [joints.get(f"hub_to_blade_{i}") for i in range(r.blade_count)]
        ctx.check("blade_joint_count", all(j is not None for j in blade_joints))
        if r.rotor_module == "pitching_blades":
            ctx.check(
                "all_blades_pitch",
                all(
                    j.articulation_type == ArticulationType.REVOLUTE
                    for j in blade_joints
                    if j is not None
                ),
            )
            ctx.check(
                "pitch_axis_is_blade_local_axis",
                all(j.axis == (0.0, 0.0, 1.0) for j in blade_joints if j is not None),
                details="Each blade part extends along local +Z; the joint frame phase rotates that axis onto the hub radial direction.",
            )
        else:
            ctx.check(
                "all_blades_fixed_socket",
                all(
                    j.articulation_type == ArticulationType.FIXED
                    for j in blade_joints
                    if j is not None
                ),
            )
    else:
        ctx.check(
            "monolithic_has_no_blade_joints",
            not any(name.startswith("hub_to_blade_") for name in joints),
        )
    for a, b in (
        ("tower", "foundation"),
        ("tower", "bearing_module"),
        (r.yaw_parent, "nacelle"),
        ("tower", "nacelle"),
        ("nacelle", "rotor"),
        ("nacelle", "access_hatch"),
        ("nacelle", "root_guard"),
        ("nacelle", "lock_pin"),
    ):
        if a in names and b in names:
            ctx.allow_overlap(
                object_model.get_part(a),
                object_model.get_part(b),
                reason="Captured turbine support, yaw, rotor, or service hardware overlaps at its bearing interface.",
            )
    if r.rotor_module != "monolithic_rotor":
        for i in range(r.blade_count):
            if f"blade_{i}" in names:
                ctx.allow_overlap(
                    object_model.get_part("rotor"),
                    object_model.get_part(f"blade_{i}"),
                    reason="Blade root flange is captured inside the hub socket.",
                )
                ctx.allow_overlap(
                    object_model.get_part("nacelle"),
                    object_model.get_part(f"blade_{i}"),
                    reason="Blade root sits inside the nacelle shaft housing at zero pose.",
                )
                if "lock_pin" in names:
                    ctx.allow_overlap(
                        object_model.get_part("lock_pin"),
                        object_model.get_part(f"blade_{i}"),
                        reason="Rotor lock pin passes through the blade-root capture region.",
                    )
                if "root_guard" in names:
                    ctx.allow_overlap(
                        object_model.get_part("root_guard"),
                        object_model.get_part(f"blade_{i}"),
                        reason="Root guard surrounds the blade-root capture region.",
                    )
        for i in range(r.blade_count):
            for j in range(i + 1, r.blade_count):
                a = f"blade_{i}"
                b = f"blade_{j}"
                if a in names and b in names:
                    ctx.allow_overlap(
                        object_model.get_part(a),
                        object_model.get_part(b),
                        reason="Blade root flanges share the captured hub center volume.",
                    )
    if "root_guard" in names:
        ctx.allow_overlap(
            object_model.get_part("root_guard"),
            object_model.get_part("rotor"),
            reason="Root guard ring wraps around the rotor hub.",
        )
    if "lock_pin" in names:
        ctx.allow_overlap(
            object_model.get_part("lock_pin"),
            object_model.get_part("rotor"),
            reason="Lock pin enters the rotor hub capture region.",
        )
    if "lock_pin" in names and "root_guard" in names:
        ctx.allow_overlap(
            object_model.get_part("lock_pin"),
            object_model.get_part("root_guard"),
            reason="Rotor lock pin passes through the root guard ring.",
        )
    return ctx.report()


__all__ = [
    "WindTurbineConfig",
    "ResolvedWindTurbineConfig",
    "config_from_seed",
    "resolve_config",
    "build_wind_turbine",
    "build_seeded_wind_turbine",
    "slot_choices_for_seed",
    "run_wind_turbine_tests",
]
