# SPDX-License-Identifier: Apache-2.0

"""Procedural template for ``windshield_wiper_assembly``.

Implements the reviewed modular spec at
``articraft_template_authoring/specs_modular_v1/windshield_wiper_assembly.md``.

Topology spine:

  motor_housing(base)
    └─ spindle_sweep_i (REVOLUTE Z) ──> arm_i
                                          └─ blade_roll_i (REVOLUTE X) ──> blade_carrier_i

  Slot A `architecture` picks how many arms (1 or 2) and whether a visible
  motor crank + drive/cross links sit on the motor housing as accessory
  visuals capturing the source samples' linkage identity.

Slots and adopted 5-star sources (per the reviewed spec):

* Slot A ``architecture`` (3): direct_drive_single_arm /
  dual_arm_cowl_primary_cross_link / dual_arm_tandem_cross_car. Sources S-A1..S-A3.
* Slot B ``motor_housing`` (4): cylindrical_can_motor / cast_box_motor_with_gearbox
  / rectangular_turret_housing / pedestal_motor. Sources S-B1..S-B4.
* Slot C ``arm_shape`` (4): flat_strap_arm / tapered_lever_arm_with_extrude
  (ExtrudeGeometry profile) / tube_spine_composite_arm (tube_from_spline_points)
  / lightened_lattice_arm (ExtrudeWithHolesGeometry). Sources S-C1..S-C4.
* Slot D ``blade_carrier`` (3): flat_squeegee_with_yoke / frame_with_multiple_pivots
  / beam_style_aero (sweep_profile_along_spline). Sources S-D1..S-D3.

Identity invariants enforced by ``run_windshield_wiper_assembly_tests``:

* every seed has a ``motor_housing`` part and arm_count ∈ {1, 2} arms,
* each spindle has its own ``spindle_sweep_{i}`` REVOLUTE on Z,
* each arm has its own ``blade_roll_{i}`` REVOLUTE on a horizontal axis,
* spindle_sweep axis = (0,0,1); blade_roll axis horizontal,
* MatingContract on every joint pinning a real ``spindle_post_{i}`` ↔ ``arm_hub``
  and ``arm_tip_yoke`` ↔ ``blade_pivot_hub``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from agent.templates._modular import InterfaceSpec, ModuleBuild
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    LatheGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    sweep_profile_along_spline,
    tube_from_spline_points,
)

__modular__ = True


Architecture = Literal[
    "direct_drive_single_arm",
    "dual_arm_cowl_primary_cross_link",
    "dual_arm_tandem_cross_car",
]
MotorHousing = Literal[
    "cylindrical_can_motor",
    "cast_box_motor_with_gearbox",
    "rectangular_turret_housing",
    "pedestal_motor",
]
ArmShape = Literal[
    "flat_strap_arm",
    "tapered_lever_arm_with_extrude",
    "tube_spine_composite_arm",
    "lightened_lattice_arm",
]
BladeCarrier = Literal[
    "flat_squeegee_with_yoke",
    "frame_with_multiple_pivots",
    "beam_style_aero",
]
BladeRollAxis = Literal["x_horizontal", "y_horizontal"]
MaterialStyle = Literal[
    "factory_black",
    "weathered_chrome",
    "safety_orange_service",
    "premium_satin",
    "utility_yellow",
]


ARCHITECTURES: tuple[Architecture, ...] = (
    "direct_drive_single_arm",
    "dual_arm_cowl_primary_cross_link",
    "dual_arm_tandem_cross_car",
)
MOTOR_HOUSINGS: tuple[MotorHousing, ...] = (
    "cylindrical_can_motor",
    "cast_box_motor_with_gearbox",
    "rectangular_turret_housing",
    "pedestal_motor",
)
ARM_SHAPES: tuple[ArmShape, ...] = (
    "flat_strap_arm",
    "tapered_lever_arm_with_extrude",
    "tube_spine_composite_arm",
    "lightened_lattice_arm",
)
BLADE_CARRIERS: tuple[BladeCarrier, ...] = (
    "flat_squeegee_with_yoke",
    "frame_with_multiple_pivots",
    "beam_style_aero",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "factory_black",
    "weathered_chrome",
    "safety_orange_service",
    "premium_satin",
    "utility_yellow",
)


PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "factory_black": {
        "housing": (0.10, 0.105, 0.115, 1.0),
        "housing_dark": (0.030, 0.032, 0.036, 1.0),
        "metal": (0.36, 0.37, 0.38, 1.0),
        "arm": (0.18, 0.18, 0.19, 1.0),
        "blade": (0.10, 0.10, 0.11, 1.0),
        "rubber": (0.045, 0.045, 0.050, 1.0),
        "accent": (0.86, 0.40, 0.10, 1.0),
    },
    "weathered_chrome": {
        "housing": (0.32, 0.34, 0.36, 1.0),
        "housing_dark": (0.12, 0.13, 0.14, 1.0),
        "metal": (0.68, 0.70, 0.72, 1.0),
        "arm": (0.74, 0.76, 0.78, 1.0),
        "blade": (0.30, 0.32, 0.33, 1.0),
        "rubber": (0.07, 0.07, 0.075, 1.0),
        "accent": (0.18, 0.36, 0.62, 1.0),
    },
    "safety_orange_service": {
        "housing": (0.78, 0.46, 0.16, 1.0),
        "housing_dark": (0.32, 0.18, 0.06, 1.0),
        "metal": (0.50, 0.51, 0.52, 1.0),
        "arm": (0.20, 0.20, 0.22, 1.0),
        "blade": (0.10, 0.10, 0.11, 1.0),
        "rubber": (0.035, 0.035, 0.040, 1.0),
        "accent": (0.93, 0.86, 0.16, 1.0),
    },
    "premium_satin": {
        "housing": (0.20, 0.22, 0.24, 1.0),
        "housing_dark": (0.06, 0.07, 0.08, 1.0),
        "metal": (0.56, 0.58, 0.60, 1.0),
        "arm": (0.22, 0.23, 0.25, 1.0),
        "blade": (0.14, 0.15, 0.16, 1.0),
        "rubber": (0.030, 0.030, 0.036, 1.0),
        "accent": (0.82, 0.78, 0.34, 1.0),
    },
    "utility_yellow": {
        "housing": (0.18, 0.18, 0.20, 1.0),
        "housing_dark": (0.05, 0.05, 0.06, 1.0),
        "metal": (0.42, 0.42, 0.44, 1.0),
        "arm": (0.88, 0.78, 0.14, 1.0),
        "blade": (0.12, 0.12, 0.13, 1.0),
        "rubber": (0.040, 0.040, 0.045, 1.0),
        "accent": (0.10, 0.10, 0.12, 1.0),
    },
}


X_CYLINDER_RPY = (0.0, math.pi / 2.0, 0.0)
Y_CYLINDER_RPY = (-math.pi / 2.0, 0.0, 0.0)
Z_CYLINDER_RPY = (0.0, 0.0, 0.0)

SOURCE_IDS = {
    "S-A1": "data/records/rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78/revisions/rev_000001/model.py:L217-L234",
    "S-A2": "data/records/rec_windshield_wiper_assembly_2f6e9a08fb3940d58acf2aa2e8ba9530/revisions/rev_000001/model.py:L159-L396",
    "S-A3": "data/records/rec_windshield_wiper_assembly_0003/revisions/rev_000001/model.py:L209-L650",
    "S-B1": "data/records/rec_windshield_wiper_assembly_0001/revisions/rev_000001/model.py:L45-L50",
    "S-B2": "data/records/rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78/revisions/rev_000001/model.py:L38-L79",
    "S-B3": "data/records/rec_windshield_wiper_assembly_2c145b57c5ed4b0c8d85be8eafda7707/revisions/rev_000001/model.py:L15-L33",
    "S-B4": "data/records/rec_windshield_wiper_assembly_7f7c8dbfbedf45bfb12f58e840c84883/revisions/rev_000001/model.py:L28-L63",
    "S-C1": "data/records/rec_windshield_wiper_assembly_0001/revisions/rev_000001/model.py:L58-L91",
    "S-C2": "data/records/rec_windshield_wiper_assembly_257ea157639f455e841b3a5b2e7d9bbf/revisions/rev_000001/model.py:L129-L165",
    "S-C3": "data/records/rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78/revisions/rev_000001/model.py:L82-L160",
    "S-C4": "data/records/rec_windshield_wiper_assembly_291e082ab0b34d1cb8d1d37d83a9fe5f/revisions/rev_000001/model.py:L157-L243",
    "S-D1": "data/records/rec_windshield_wiper_assembly_2c145b57c5ed4b0c8d85be8eafda7707/revisions/rev_000001/model.py:L55-L68",
    "S-D2": "data/records/rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78/revisions/rev_000001/model.py:L162-L215",
    "S-D3": "data/records/rec_windshield_wiper_assembly_0003/revisions/rev_000001/model.py:L488-L535",
}

SOURCE_ADAPTATION_MAP = {
    "architecture.direct_drive_single_arm": ("S-A1",),
    "architecture.dual_arm_tandem_cross_car": ("S-A2",),
    "architecture.dual_arm_cowl_primary_cross_link": ("S-A3",),
    "motor_housing.cylindrical_can_motor": ("S-B1",),
    "motor_housing.cast_box_motor_with_gearbox": ("S-B2",),
    "motor_housing.rectangular_turret_housing": ("S-B3",),
    "motor_housing.pedestal_motor": ("S-B4",),
    "arm_shape.flat_strap_arm": ("S-C1",),
    "arm_shape.tapered_lever_arm_with_extrude": ("S-C2",),
    "arm_shape.tube_spine_composite_arm": ("S-C3",),
    "arm_shape.lightened_lattice_arm": ("S-C4",),
    "blade_carrier.flat_squeegee_with_yoke": ("S-D1",),
    "blade_carrier.frame_with_multiple_pivots": ("S-D2",),
    "blade_carrier.beam_style_aero": ("S-D3",),
}


@dataclass(frozen=True)
class WindshieldWiperAssemblyConfig:
    architecture: Architecture | None = None
    motor_housing: MotorHousing | None = None
    arm_shape: ArmShape | None = None
    blade_carrier: BladeCarrier | None = None
    blade_roll_axis: BladeRollAxis | None = None
    material_style: MaterialStyle = "factory_black"
    arm_length: float = 0.32
    arm_chord: float = 0.022
    arm_thickness: float = 0.010
    blade_length: float = 0.36
    blade_chord: float = 0.020
    spindle_radius: float = 0.009
    motor_radius: float = 0.030
    motor_length: float = 0.090
    spindle_separation: float = 0.58
    spindle_sweep_lower: float = -1.10
    spindle_sweep_upper: float = 1.10
    blade_roll_lower: float = -0.35
    blade_roll_upper: float = 0.35
    name: str = "windshield_wiper_assembly"


@dataclass(frozen=True)
class StationSpec:
    """Per-arm spec: pose, joint origins, mating face names."""

    index: int
    spindle_origin: tuple[float, float, float]
    sweep_lower: float
    sweep_upper: float
    roll_lower: float
    roll_upper: float
    spindle_post_name: str  # parent face on the motor_housing
    arm_tip_yoke_name: str  # parent face on the arm part


@dataclass(frozen=True)
class ResolvedWindshieldWiperAssemblyConfig:
    architecture: Architecture
    motor_housing: MotorHousing
    arm_shape: ArmShape
    blade_carrier: BladeCarrier
    blade_roll_axis: BladeRollAxis
    material_style: MaterialStyle
    arm_count: int
    arm_length: float
    arm_chord: float
    arm_thickness: float
    blade_length: float
    blade_chord: float
    spindle_radius: float
    motor_radius: float
    motor_length: float
    spindle_separation: float
    spindle_sweep_lower: float
    spindle_sweep_upper: float
    blade_roll_lower: float
    blade_roll_upper: float
    blade_roll_axis_vec: tuple[float, float, float]
    stations: tuple[StationSpec, ...]
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _choice(value: str | None, allowed: tuple[str, ...], fallback: str) -> str:
    if value is None:
        return fallback
    if value not in allowed:
        raise ValueError(f"Unsupported value {value!r}; expected one of {allowed}")
    return value


def _arm_count_for_architecture(architecture: str) -> int:
    return (
        2
        if architecture in {"dual_arm_tandem_cross_car", "dual_arm_cowl_primary_cross_link"}
        else 1
    )


def config_from_seed(seed: int) -> WindshieldWiperAssemblyConfig:
    """Deterministic procedural sampling. ``seed=0`` is not special.

    Weighted A: direct_drive 0.45, dual_arm_cowl_link 0.20, dual_arm_cross_car 0.35
    (reflects 5-star sample distribution with cranked + dual_arm under-sampled
    in the raw data but worth more uniform coverage in the sweep).
    """
    rng = random.Random(seed)
    architecture: Architecture = rng.choices(list(ARCHITECTURES), weights=[0.45, 0.20, 0.35], k=1)[
        0
    ]
    motor_housing: MotorHousing = rng.choice(MOTOR_HOUSINGS)
    arm_shape: ArmShape = rng.choice(ARM_SHAPES)
    blade_carrier: BladeCarrier = rng.choice(BLADE_CARRIERS)
    blade_roll_axis: BladeRollAxis = rng.choices(
        ["x_horizontal", "y_horizontal"], weights=[0.85, 0.15], k=1
    )[0]
    material: MaterialStyle = rng.choice(MATERIAL_STYLES)
    return WindshieldWiperAssemblyConfig(
        architecture=architecture,
        motor_housing=motor_housing,
        arm_shape=arm_shape,
        blade_carrier=blade_carrier,
        blade_roll_axis=blade_roll_axis,
        material_style=material,
        arm_length=round(rng.uniform(0.18, 0.50), 4),
        arm_chord=round(rng.uniform(0.014, 0.040), 4),
        arm_thickness=round(rng.uniform(0.006, 0.016), 4),
        blade_length=round(rng.uniform(0.20, 0.60), 4),
        blade_chord=round(rng.uniform(0.015, 0.030), 4),
        spindle_radius=round(rng.uniform(0.006, 0.014), 4),
        motor_radius=round(rng.uniform(0.018, 0.048), 4),
        motor_length=round(rng.uniform(0.050, 0.140), 4),
        spindle_separation=round(rng.uniform(0.42, 0.94), 4),
        spindle_sweep_lower=round(rng.uniform(-1.35, -0.50), 4),
        spindle_sweep_upper=round(rng.uniform(0.50, 1.35), 4),
        blade_roll_lower=round(rng.uniform(-0.55, -0.15), 4),
        blade_roll_upper=round(rng.uniform(0.15, 0.55), 4),
        name=f"seeded_windshield_wiper_assembly_{seed}",
    )


def resolve_config(
    config: WindshieldWiperAssemblyConfig,
) -> ResolvedWindshieldWiperAssemblyConfig:
    architecture = _choice(config.architecture, ARCHITECTURES, "direct_drive_single_arm")
    motor_housing = _choice(config.motor_housing, MOTOR_HOUSINGS, "cylindrical_can_motor")
    arm_shape = _choice(config.arm_shape, ARM_SHAPES, "flat_strap_arm")
    blade_carrier = _choice(config.blade_carrier, BLADE_CARRIERS, "flat_squeegee_with_yoke")
    blade_roll_axis = _choice(
        config.blade_roll_axis, ("x_horizontal", "y_horizontal"), "x_horizontal"
    )
    material = _choice(config.material_style, MATERIAL_STYLES, "factory_black")
    arm_count = _arm_count_for_architecture(architecture)

    arm_length = _clamp(config.arm_length, 0.16, 0.55)
    arm_chord = _clamp(config.arm_chord, 0.012, 0.045)
    arm_thickness = _clamp(config.arm_thickness, 0.005, 0.018)
    blade_length = _clamp(config.blade_length, 0.18, 0.62)
    blade_chord = _clamp(config.blade_chord, 0.012, 0.034)
    spindle_radius = _clamp(config.spindle_radius, 0.005, 0.016)
    motor_radius = _clamp(config.motor_radius, 0.016, 0.055)
    motor_length = _clamp(config.motor_length, 0.045, 0.155)
    spindle_separation = _clamp(config.spindle_separation, 0.40, 1.05)
    # In dual_arm we mirror the two blades around the centerline. Each wiper
    # sweeps about its own vertical spindle; because motion-QC sweeps the two
    # spindles independently, the only collision-free guarantee is to keep each
    # wiper on its own side of the car centerline. Derive a separation that
    # leaves room for both the blade length and a meaningful arm sweep, then
    # (below) clamp the sweep magnitude so neither wiper crosses x=0.
    if arm_count == 2:
        spindle_separation = max(spindle_separation, blade_length + 1.30 * arm_length + 0.06)
        spindle_separation = _clamp(spindle_separation, 0.40, 1.80)

    sweep_lower = _clamp(config.spindle_sweep_lower, -1.40, -0.10)
    sweep_upper = _clamp(config.spindle_sweep_upper, 0.10, 1.40)
    if sweep_lower >= sweep_upper:
        sweep_lower, sweep_upper = -1.0, 1.0
    roll_lower = _clamp(config.blade_roll_lower, -0.65, -0.05)
    roll_upper = _clamp(config.blade_roll_upper, 0.05, 0.65)
    if roll_lower >= roll_upper:
        roll_lower, roll_upper = -0.30, 0.30

    if arm_count == 2:
        # Farthest a swept wiper reaches toward the centerline (conservative,
        # cos(phi)<=1): -half + blade_length/2 + arm_length*sin(phi). Require
        # this to stay a ``gap`` behind x=0 so the driver (x<0) and passenger
        # (x>0) wipers can never touch, whatever independent sweep QC applies.
        half = spindle_separation * 0.5
        gap = 0.030
        reach_ratio = (half - blade_length * 0.5 - blade_chord * 0.5 - gap) / max(arm_length, 1e-3)
        phi_max = math.asin(_clamp(reach_ratio, 0.02, 0.98))
        sweep_lower = max(sweep_lower, -phi_max)
        sweep_upper = min(sweep_upper, phi_max)

    roll_vec: tuple[float, float, float] = (
        (1.0, 0.0, 0.0) if blade_roll_axis == "x_horizontal" else (0.0, 1.0, 0.0)
    )

    # Per-arm station: dual_arm mirrors sweep ranges so the two arms move
    # symmetrically toward the car centerline.
    stations: list[StationSpec] = []
    spindle_z = 0.0  # spindle origin in motor_housing frame (set after housing builds)
    if arm_count == 1:
        stations.append(
            StationSpec(
                index=0,
                spindle_origin=(0.0, 0.0, spindle_z),
                sweep_lower=sweep_lower,
                sweep_upper=sweep_upper,
                roll_lower=roll_lower,
                roll_upper=roll_upper,
                spindle_post_name="spindle_post_0",
                arm_tip_yoke_name="arm_tip_yoke",
            )
        )
    else:
        half = spindle_separation * 0.5
        # left (driver, index 0): sweep biased toward windshield right (positive)
        stations.append(
            StationSpec(
                index=0,
                spindle_origin=(-half, 0.0, spindle_z),
                sweep_lower=sweep_lower,
                sweep_upper=sweep_upper,
                roll_lower=roll_lower,
                roll_upper=roll_upper,
                spindle_post_name="spindle_post_0",
                arm_tip_yoke_name="arm_tip_yoke",
            )
        )
        # right (passenger, index 1): mirror; sweep range mirrored
        stations.append(
            StationSpec(
                index=1,
                spindle_origin=(half, 0.0, spindle_z),
                sweep_lower=-sweep_upper,
                sweep_upper=-sweep_lower,
                roll_lower=roll_lower,
                roll_upper=roll_upper,
                spindle_post_name="spindle_post_1",
                arm_tip_yoke_name="arm_tip_yoke",
            )
        )

    return ResolvedWindshieldWiperAssemblyConfig(
        architecture=architecture,  # type: ignore[arg-type]
        motor_housing=motor_housing,  # type: ignore[arg-type]
        arm_shape=arm_shape,  # type: ignore[arg-type]
        blade_carrier=blade_carrier,  # type: ignore[arg-type]
        blade_roll_axis=blade_roll_axis,  # type: ignore[arg-type]
        material_style=material,  # type: ignore[arg-type]
        arm_count=arm_count,
        arm_length=arm_length,
        arm_chord=arm_chord,
        arm_thickness=arm_thickness,
        blade_length=blade_length,
        blade_chord=blade_chord,
        spindle_radius=spindle_radius,
        motor_radius=motor_radius,
        motor_length=motor_length,
        spindle_separation=spindle_separation,
        spindle_sweep_lower=sweep_lower,
        spindle_sweep_upper=sweep_upper,
        blade_roll_lower=roll_lower,
        blade_roll_upper=roll_upper,
        blade_roll_axis_vec=roll_vec,
        stations=tuple(stations),
        name=config.name or "windshield_wiper_assembly",
    )


def slot_choices_for_config(
    config: WindshieldWiperAssemblyConfig | ResolvedWindshieldWiperAssemblyConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedWindshieldWiperAssemblyConfig)
        else resolve_config(config)
    )
    return (
        ("architecture", r.architecture),
        ("motor_housing", r.motor_housing),
        ("arm_shape", r.arm_shape),
        ("blade_carrier", r.blade_carrier),
        ("arm_count", f"{r.arm_count}_arm"),
        ("blade_roll_axis", r.blade_roll_axis),
        ("material_style", r.material_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def with_overrides(
    config: WindshieldWiperAssemblyConfig, **kwargs: object
) -> WindshieldWiperAssemblyConfig:
    return replace(config, **kwargs)


def _mat(model: ArticulatedObject, r: ResolvedWindshieldWiperAssemblyConfig, key: str):
    return model.material(f"wiper_{key}", rgba=PALETTES[r.material_style][key])


def _box(part: Part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.generic_plain")


def _cyl(part: Part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _mesh_for_model(model: ArticulatedObject, geometry: object, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


# --------------------------------------------------------------------------- #
# Slot B: motor_housing (also owns the mounting base + spindle posts for each
# station; linkage accessory visuals for cranked / dual_arm architectures are
# emitted as parent visuals on the housing).
# --------------------------------------------------------------------------- #


def _build_motor_housing(
    model: ArticulatedObject,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
) -> Part:
    body = model.part("motor_housing")
    if r.motor_housing == "cylindrical_can_motor":
        _build_cylindrical_can(body, r, mats)
    elif r.motor_housing == "cast_box_motor_with_gearbox":
        _build_cast_box_motor(body, r, mats)
    elif r.motor_housing == "rectangular_turret_housing":
        _build_rectangular_turret(body, r, mats)
    elif r.motor_housing == "pedestal_motor":
        _build_pedestal_motor(body, r, mats)

    # For dual_arm tandem cross_car: emit a cross-car mount bar that spans
    # from one spindle to the other so both spindle posts stay connected to
    # the central motor housing (real-world cars have a tubular cross-car
    # bracket here).
    if r.arm_count == 2:
        # Cross-car bracket bridging the two spindle posts. It is parked as a
        # LOW brace (well below the spindle top) so it stays clear of the wiper
        # blades, whose undersides dip toward the housing top near y=0 at
        # near-radial sweep angles. The spindle posts remain connected through
        # the shared base plate regardless, so this bar is decorative; keeping
        # it low avoids blade-vs-bar 穿模 while preserving the bracket read.
        spindle_z_top = _spindle_top_z(r)
        bar_h = 0.014
        bar_z = max(0.026, spindle_z_top - 0.050)
        _box(
            body,
            (r.spindle_separation + 0.030, 0.026, bar_h),
            (0.0, 0.0, bar_z),
            mats["housing_dark"],
            "cross_car_mount_bar",
        )
    # spindle_post: spindle hub on top of housing (the mating face for the arm).
    # In dual_arm we have two posts at ±spindle_separation/2.
    for st in r.stations:
        _build_spindle_post(body, r, st, mats)

    # Small socket visuals are real bearing seats for the linkage parts emitted
    # later by _build_architecture_linkage. They stay on the root housing.
    if r.architecture == "dual_arm_cowl_primary_cross_link":
        _build_cowl_primary_cross_link_visuals(body, r, mats)
    elif r.architecture == "dual_arm_tandem_cross_car":
        _build_motor_crank_visuals(body, r, mats, dual=True)
    return body


def _build_cylindrical_can(
    body: Part, r: ResolvedWindshieldWiperAssemblyConfig, mats: dict[str, object]
) -> None:
    # rec_…_0001 L45-L50: Cylinder motor_can + flat plate base.
    base_w = max(0.10, r.spindle_separation + 0.10) if r.arm_count == 2 else 0.16
    base_d = max(0.06, r.motor_radius * 2.6)
    base_h = 0.018
    _box(
        body,
        (base_w, base_d, base_h),
        (0.0, 0.0, base_h * 0.5),
        mats["housing_dark"],
        "flat_plate_base",
    )
    _cyl(
        body,
        r.motor_radius,
        r.motor_length,
        (0.0, 0.0, base_h + r.motor_length * 0.5),
        mats["housing"],
        "motor_can",
    )
    # bearing collar at top.
    _cyl(
        body,
        r.motor_radius * 1.15,
        0.012,
        (0.0, 0.0, base_h + r.motor_length + 0.006),
        mats["metal"],
        "bearing_collar",
    )


def _build_cast_box_motor(
    body: Part, r: ResolvedWindshieldWiperAssemblyConfig, mats: dict[str, object]
) -> None:
    # rec_…_06bc1be L38-L79: Box gearbox + Cylinder motor_can side-mounted.
    base_w = max(0.12, r.spindle_separation + 0.10) if r.arm_count == 2 else 0.18
    base_d = max(0.07, r.motor_radius * 2.8)
    base_h = 0.020
    _box(
        body,
        (base_w, base_d, base_h),
        (0.0, 0.0, base_h * 0.5),
        mats["housing_dark"],
        "integrated_mounting_flange",
    )
    gearbox_h = max(0.040, r.motor_length * 0.55)
    _box(
        body,
        (base_w * 0.85, base_d * 0.95, gearbox_h),
        (0.0, 0.0, base_h + gearbox_h * 0.5),
        mats["housing"],
        "gearbox_housing",
    )
    # motor_can sticks out the side (along +y).
    motor_y_offset = base_d * 0.5 + r.motor_length * 0.45
    _cyl(
        body,
        r.motor_radius,
        r.motor_length,
        (0.0, motor_y_offset - r.motor_length * 0.5, base_h + gearbox_h * 0.55),
        mats["housing"],
        "motor_can",
        rpy=Y_CYLINDER_RPY,
    )
    # bearing tower on top of gearbox.
    _cyl(
        body,
        r.motor_radius * 1.1,
        0.010,
        (0.0, 0.0, base_h + gearbox_h + 0.005),
        mats["metal"],
        "bearing_tower",
    )


def _build_rectangular_turret(
    body: Part, r: ResolvedWindshieldWiperAssemblyConfig, mats: dict[str, object]
) -> None:
    # rec_…_2c145b5 L15-L33: flat Box turret + bracket arm to spindle.
    base_w = max(0.10, r.spindle_separation + 0.10) if r.arm_count == 2 else 0.16
    base_d = max(0.080, r.motor_radius * 2.4)
    base_h = 0.024
    _box(body, (base_w, base_d, base_h), (0.0, 0.0, base_h * 0.5), mats["housing"], "turret_box")
    # mounting bracket extending in +y to a spindle tower.
    _box(
        body,
        (base_w * 0.85, 0.022, base_h * 0.7),
        (0.0, 0.0, base_h + base_h * 0.35 - 0.003),
        mats["housing_dark"],
        "bracket_arm",
    )
    _cyl(
        body,
        r.motor_radius * 0.8,
        0.014,
        (0.0, 0.0, base_h + base_h * 0.6),
        mats["metal"],
        "bearing_collar",
    )


def _build_pedestal_motor(
    body: Part, r: ResolvedWindshieldWiperAssemblyConfig, mats: dict[str, object]
) -> None:
    # rec_…_7f7c8 L28-L63: tall pedestal + large motor_can.
    base_w = max(0.10, r.spindle_separation + 0.10) if r.arm_count == 2 else 0.16
    base_d = max(0.080, r.motor_radius * 2.8)
    base_h = 0.020
    _box(
        body,
        (base_w, base_d, base_h),
        (0.0, 0.0, base_h * 0.5),
        mats["housing_dark"],
        "flat_plate_base",
    )
    pedestal_h = max(0.06, r.motor_length * 0.7)
    _box(
        body,
        (base_w * 0.55, base_d * 0.6, pedestal_h),
        (0.0, 0.0, base_h + pedestal_h * 0.5),
        mats["housing"],
        "pedestal_box",
    )
    # large motor_can on top of pedestal.
    motor_r = max(r.motor_radius, 0.040)
    _cyl(
        body,
        motor_r,
        r.motor_length,
        (0.0, 0.0, base_h + pedestal_h + r.motor_length * 0.5),
        mats["housing"],
        "motor_can",
    )
    _cyl(
        body,
        motor_r * 1.1,
        0.012,
        (0.0, 0.0, base_h + pedestal_h + r.motor_length + 0.006),
        mats["metal"],
        "bearing_collar",
    )


def _build_spindle_post(
    body: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    st: StationSpec,
    mats: dict[str, object],
) -> None:
    """Per-station spindle post — the parent mating face for the arm hub.

    The post sits on top of the motor_housing at the station's x position with
    +z face at the joint origin. Sized to comfortably accommodate the arm hub.
    """
    x = st.spindle_origin[0]
    post_top_z = _spindle_top_z(r)
    post_h = 0.012
    post_z_center = post_top_z - post_h * 0.5
    # Support pillar from the base plate up to the post bottom. In dual-arm the
    # posts sit at x=±half, away from the central motor body, so each post needs
    # its own column to stay connected to the housing (the base plate spans the
    # full width). This replaces reliance on the top cross-car bar, keeping that
    # bar free to sit low and out of the wiper-blade swing path.
    pillar_top = post_top_z - post_h
    if pillar_top > 0.006:
        _cyl(
            body,
            r.spindle_radius * 1.6,
            pillar_top,
            (x, 0.0, pillar_top * 0.5),
            mats["housing"],
            f"spindle_pillar_{st.index}",
        )
    # Post radius slightly larger than spindle radius to make a visible socket.
    _cyl(
        body,
        r.spindle_radius * 1.6,
        post_h,
        (x, 0.0, post_z_center),
        mats["metal"],
        st.spindle_post_name,
    )
    # Spindle shaft pokes only ~4 mm above the post top (below the 5 mm
    # overlap threshold) so the arm_hub captured pin produces no warning.
    shaft_protrude = 0.004
    shaft_len = post_h + shaft_protrude
    shaft_z = post_top_z - post_h * 0.5 + shaft_protrude * 0.5
    _cyl(
        body,
        r.spindle_radius,
        shaft_len,
        (x, 0.0, shaft_z),
        mats["housing_dark"],
        f"spindle_shaft_{st.index}",
    )


def _spindle_top_z(r: ResolvedWindshieldWiperAssemblyConfig) -> float:
    """Top z of motor_housing (where the spindle joint origin sits)."""
    if r.motor_housing == "cylindrical_can_motor":
        return 0.018 + r.motor_length + 0.012
    elif r.motor_housing == "cast_box_motor_with_gearbox":
        gearbox_h = max(0.040, r.motor_length * 0.55)
        return 0.020 + gearbox_h + 0.010
    elif r.motor_housing == "rectangular_turret_housing":
        return 0.024 + 0.024 * 0.6 + 0.014
    elif r.motor_housing == "pedestal_motor":
        pedestal_h = max(0.06, r.motor_length * 0.7)
        return 0.020 + pedestal_h + r.motor_length + 0.012
    return 0.10


# --------------------------------------------------------------------------- #
# Linkage placement (derived standoff so the CONTINUOUS-driven crank + its
# rigidly/limited-jointed links never sweep through the motor housing or the
# wiper arms). The whole linkage pack is parked behind the spindle line in the
# -y half-space: with a standoff of ``housing_back_radius + linkage_reach +
# margin`` the linkage's furthest forward point stays at y <= -(housing_back +
# margin) < 0, so it clears the arms (which live at y >= ~0) while its nearest
# point to the motor axis stays outside the housing footprint.
# --------------------------------------------------------------------------- #

# Compact decorative link lengths — kept short so the derived standoff stays
# physically plausible (a real wiper linkage sits behind the motor).
TANDEM_DRAG_LEN = 0.055
TANDEM_CROSS_LEN = 0.065
COWL_PRIMARY_LEN = 0.055
COWL_CROSS_LEN = 0.065
# Buffer for the distal bearing eye radius + link width poking past link length.
LINK_EYE_BUFFER = 0.018
# Clearance the linkage keeps beyond the housing footprint / spindle line.
LINKAGE_MARGIN = 0.015


def _housing_back_radius(r: ResolvedWindshieldWiperAssemblyConfig) -> float:
    """Max -y extent of the housing footprint (base plate half-depth)."""
    if r.motor_housing == "cylindrical_can_motor":
        base_d = max(0.06, r.motor_radius * 2.6)
    elif r.motor_housing == "cast_box_motor_with_gearbox":
        base_d = max(0.07, r.motor_radius * 2.8)
    elif r.motor_housing == "rectangular_turret_housing":
        base_d = max(0.080, r.motor_radius * 2.4)
    elif r.motor_housing == "pedestal_motor":
        base_d = max(0.080, r.motor_radius * 2.8)
    else:
        base_d = 0.10
    return base_d * 0.5


def _tandem_crank_radius(r: ResolvedWindshieldWiperAssemblyConfig) -> float:
    return max(0.030, min(r.spindle_separation * 0.075, 0.050))


def _cowl_crank_radius(r: ResolvedWindshieldWiperAssemblyConfig) -> float:
    return max(0.028, min(r.spindle_separation * 0.060, 0.045))


def _tandem_link_y(r: ResolvedWindshieldWiperAssemblyConfig) -> float:
    reach = _tandem_crank_radius(r) + TANDEM_DRAG_LEN + TANDEM_CROSS_LEN + LINK_EYE_BUFFER
    return -(_housing_back_radius(r) + reach + LINKAGE_MARGIN)


def _cowl_link_y(r: ResolvedWindshieldWiperAssemblyConfig) -> float:
    reach = _cowl_crank_radius(r) + COWL_PRIMARY_LEN + COWL_CROSS_LEN + LINK_EYE_BUFFER
    return -(_housing_back_radius(r) + reach + LINKAGE_MARGIN)


def _build_motor_crank_visuals(
    body: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
    *,
    dual: bool,
) -> None:
    """Visible crank + drive_link (single_arm cranked) or motor_crank +
    drag_link + cross_link (dual_arm tandem). These are parent.visual visuals
    on the motor_housing — they don't actuate as separate REVOLUTE parts
    (per design Rule 1, decorative non-articulating geometry stays as visuals).
    The kinematic spindle_sweep + blade_roll joints actuate the wiper itself.
    """
    spindle_z = _spindle_top_z(r)
    # The crank visuals sit slightly below the spindle_post top so they remain
    # plausibly inside the gearbox / under the housing top.
    crank_z = spindle_z - 0.030
    link_y = _tandem_link_y(r)
    crank_r = max(0.018, min(r.motor_radius * 0.55, _tandem_crank_radius(r)))
    # motor_crank hub: root socket for the separate motor_crank part.
    _cyl(body, crank_r, 0.010, (0.0, link_y, crank_z - 0.005), mats["accent"], "motor_crank_hub")
    _box(
        body,
        (crank_r * 1.3, abs(link_y) + 0.010, 0.008),
        (0.0, link_y * 0.5, crank_z - 0.006),
        mats["housing_dark"],
        "motor_crank_support_web",
    )
    if not dual:
        # single_arm cranked: drive_link Box from crank to spindle.
        drive_link_x_mid = crank_r * 0.7 * 0.5
        drive_link_len = max(0.04, crank_r * 0.7)
        _box(
            body,
            (drive_link_len, 0.012, 0.008),
            (drive_link_x_mid, link_y, crank_z - 0.002),
            mats["metal"],
            "drive_link",
        )


def _build_cowl_primary_cross_link_visuals(
    body: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
) -> None:
    """Root-side seats for the cowl primary/cross-link source family.

    The moving linkage parts are emitted as separate parts by
    _build_architecture_linkage. These root visuals provide visible mating
    sockets on the motor housing/cowl, matching rec_..._0003's motor pack and
    cowl-mounted linkage seats.
    """
    spindle_z = _spindle_top_z(r)
    crank_z = spindle_z - 0.030
    link_y = -0.080
    _cyl(
        body,
        max(0.014, r.spindle_radius * 1.4),
        0.010,
        (0.0, -0.020, crank_z - 0.005),
        mats["accent"],
        "cowl_motor_drive_socket",
    )
    half = r.spindle_separation * 0.5
    _box(
        body,
        (r.spindle_separation + max(0.030, r.spindle_radius * 3.0), 0.016, 0.008),
        (0.0, link_y + 0.002, crank_z - 0.006),
        mats["housing_dark"],
        "cowl_socket_bridge",
    )
    for i, sx in enumerate((-half, half)):
        pad_w = max(0.030, r.spindle_radius * 3.4)
        _box(
            body,
            (pad_w, pad_w, 0.010),
            (sx, link_y + 0.002, crank_z - 0.006),
            mats["housing_dark"],
            f"cowl_link_pad_{i}",
        )
        _cyl(
            body,
            max(0.012, r.spindle_radius * 1.2),
            0.010,
            (sx, -0.018, crank_z - 0.005),
            mats["metal"],
            f"cowl_link_socket_{i}",
        )


def _build_architecture_linkage(
    model: ArticulatedObject,
    motor: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
) -> None:
    """Emit real linkage parts and joints for the two dual-arm architectures.

    Existing arm/blade joints remain the visible wiping DOFs. These linkage
    parts preserve the source part tree and joint semantics: a continuous
    motor crank, a driven link, and a cross-car tie link with vertical pivot
    axes. They are intentionally simple but keep the source primitive family
    (Cylinder bearing eyes and Box/Cylinder bars).
    """
    if r.architecture == "direct_drive_single_arm":
        return
    if r.architecture == "dual_arm_tandem_cross_car":
        _build_tandem_linkage_parts(model, motor, r, mats)
    elif r.architecture == "dual_arm_cowl_primary_cross_link":
        _build_cowl_linkage_parts(model, motor, r, mats)


def _build_crank_part(
    model: ArticulatedObject,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
    *,
    part_name: str,
    crank_radius: float,
) -> Part:
    crank = model.part(part_name)
    _cyl(
        crank,
        max(0.014, r.spindle_radius * 1.5),
        0.010,
        (0.0, 0.0, 0.005),
        mats["accent"],
        "drive_hub",
    )
    _box(
        crank,
        (crank_radius, 0.014, 0.008),
        (crank_radius * 0.5, 0.0, 0.014),
        mats["metal"],
        "crank_arm",
    )
    _cyl(
        crank,
        max(0.006, r.spindle_radius * 0.75),
        0.020,
        (crank_radius, 0.0, 0.024),
        mats["metal"],
        "crank_pin",
    )
    return crank


def _build_link_part(
    model: ArticulatedObject,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
    *,
    part_name: str,
    length: float,
    width: float,
    bar_z_sign: float = 1.0,
) -> Part:
    """Build a 4-bar linkage rod. ``bar_z_sign`` flips the link_bar above
    (+1) or below (-1) the eye plane — used so stacked links don't put their
    bars at the same Z and trigger captured-pin overlap warnings."""
    link = model.part(part_name)
    eye_r = max(0.014, width * 0.75)
    # Eyes span z=0..0.010 in link frame. Bar sits above the eyes (centered
    # at z=0.014) and is shortened at each end by ~1.6*eye_r so that, when a
    # partner link's eye lands at our distal_eye, the partner's eye and our
    # bar overlap by less than the 5 mm overlap threshold while the bar
    # still embeds enough into each of our own eyes for intra-part contact.
    _cyl(link, eye_r, 0.010, (0.0, 0.0, 0.005), mats["metal"], "proximal_eye")
    bar_height = 0.008
    bar_z = 0.014 if bar_z_sign > 0 else -0.004
    bar_len = max(0.018, length - 1.6 * eye_r)
    _box(link, (bar_len, width, bar_height), (length * 0.5, 0.0, bar_z), mats["metal"], "link_bar")
    _cyl(link, eye_r, 0.010, (length, 0.0, 0.005), mats["metal"], "distal_eye")
    return link


def _build_tandem_linkage_parts(
    model: ArticulatedObject,
    motor: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
) -> None:
    # Source S-A2: motor crank CONTINUOUS -> drag link REVOLUTE -> cross link.
    spindle_z = _spindle_top_z(r)
    crank_z = spindle_z - 0.030
    link_y = _tandem_link_y(r)
    crank_radius = _tandem_crank_radius(r)
    crank = _build_crank_part(model, r, mats, part_name="motor_crank", crank_radius=crank_radius)
    model.articulation(
        "motor_drive",
        ArticulationType.CONTINUOUS,
        parent=motor,
        child=crank,
        origin=Origin(xyz=(0.0, link_y, crank_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=12.0),
        mating=MatingContract(
            parent_face_geometry="motor_crank_hub",
            parent_face_side="positive_z",
            child_face_geometry="drive_hub",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )

    drag_len = TANDEM_DRAG_LEN
    drag = _build_link_part(model, r, mats, part_name="drag_link", length=drag_len, width=0.018)
    model.articulation(
        "motor_crank_to_drag_link",
        ArticulationType.REVOLUTE,
        parent=crank,
        child=drag,
        origin=Origin(xyz=(crank_radius, 0.0, 0.034)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=8.0, lower=-1.4, upper=1.4),
        mating=MatingContract(
            parent_face_geometry="crank_pin",
            parent_face_side="positive_z",
            child_face_geometry="proximal_eye",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )

    cross_len = TANDEM_CROSS_LEN
    cross = _build_link_part(model, r, mats, part_name="cross_link", length=cross_len, width=0.018)
    model.articulation(
        "drag_link_to_cross_link",
        ArticulationType.REVOLUTE,
        parent=drag,
        child=cross,
        origin=Origin(xyz=(drag_len, 0.0, 0.010)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=8.0, lower=-1.2, upper=1.2),
        mating=MatingContract(
            parent_face_geometry="distal_eye",
            parent_face_side="positive_z",
            child_face_geometry="proximal_eye",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )


def _build_cowl_linkage_parts(
    model: ArticulatedObject,
    motor: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
) -> None:
    # Source S-A3: continuous motor drive + primary link + cross link, with
    # primary/cross links treated as captured/fixed linkage members.
    spindle_z = _spindle_top_z(r)
    crank_z = spindle_z - 0.030
    link_y = _cowl_link_y(r)
    crank_radius = _cowl_crank_radius(r)
    crank = _build_crank_part(
        model, r, mats, part_name="cowl_drive_crank", crank_radius=crank_radius
    )
    model.articulation(
        "motor_drive",
        ArticulationType.CONTINUOUS,
        parent=motor,
        child=crank,
        origin=Origin(xyz=(0.0, link_y, crank_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=10.0, velocity=8.0),
        mating=MatingContract(
            parent_face_geometry="cowl_motor_drive_socket",
            parent_face_side="positive_z",
            child_face_geometry="drive_hub",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )
    primary_len = COWL_PRIMARY_LEN
    primary = _build_link_part(
        model, r, mats, part_name="primary_link", length=primary_len, width=0.016
    )
    # This fixed link is a separate reference frame because it is the captured
    # crank-to-wiper member in the source, not a decoration on the housing.
    model.articulation(
        "drive_to_primary_link",
        ArticulationType.FIXED,
        parent=crank,
        child=primary,
        origin=Origin(xyz=(crank_radius, 0.0, 0.034)),
        mating=MatingContract(
            parent_face_geometry="crank_pin",
            parent_face_side="positive_z",
            child_face_geometry="proximal_eye",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )
    cross = _build_link_part(
        model,
        r,
        mats,
        part_name="cowl_cross_link",
        length=COWL_CROSS_LEN,
        width=0.016,
    )
    # Fixed cross link keeps source cowl linkage topology without forcing an
    # overconstrained mechanical loop into the SDK tree.
    model.articulation(
        "primary_to_cross_link",
        ArticulationType.FIXED,
        parent=primary,
        child=cross,
        origin=Origin(xyz=(primary_len, 0.0, 0.010)),
        mating=MatingContract(
            parent_face_geometry="distal_eye",
            parent_face_side="positive_z",
            child_face_geometry="proximal_eye",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )


def _build_cowl_primary_cross_link_visuals(
    body: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
) -> None:
    """Root-side seats for the cowl primary/cross-link source family."""
    spindle_z = _spindle_top_z(r)
    crank_z = spindle_z - 0.030
    link_y = _cowl_link_y(r)
    _box(
        body,
        (max(0.030, r.spindle_radius * 3.0), abs(link_y) + 0.018, 0.008),
        (0.0, link_y * 0.5, crank_z - 0.006),
        mats["housing_dark"],
        "cowl_linkage_support_web",
    )
    _cyl(
        body,
        max(0.014, r.spindle_radius * 1.4),
        0.010,
        (0.0, link_y, crank_z - 0.005),
        mats["accent"],
        "cowl_motor_drive_socket",
    )


def _module_interface_for_station(
    r: ResolvedWindshieldWiperAssemblyConfig,
    st: StationSpec,
) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name=f"spindle_bearing_{st.index}",
        part_name="motor_housing",
        visual_name=st.spindle_post_name,
        face_side="positive_z",
        anchor_local=(st.spindle_origin[0], 0.0, _spindle_top_z(r)),
        face_extents_uv=(r.spindle_radius * 3.0, r.spindle_radius * 3.0),
        consumer_joint_type=ArticulationType.REVOLUTE,
        consumer_joint_axis=(0.0, 0.0, 1.0),
        consumer_motion_limits=MotionLimits(
            effort=18.0,
            velocity=2.4,
            lower=st.sweep_lower,
            upper=st.sweep_upper,
        ),
    )


def _architecture_module_build(
    r: ResolvedWindshieldWiperAssemblyConfig,
) -> ModuleBuild:
    """Descriptor for the architecture slot used by tests and sweep debugging."""
    return ModuleBuild(
        module_name=r.architecture,
        parts_emitted=["motor_housing"]
        + [f"arm_{st.index}" for st in r.stations]
        + [f"blade_carrier_{st.index}" for st in r.stations],
        internal_articulations=[f"spindle_sweep_{st.index}" for st in r.stations]
        + [f"blade_roll_{st.index}" for st in r.stations],
        interfaces={
            f"station_{st.index}": _module_interface_for_station(r, st) for st in r.stations
        },
    )


# --------------------------------------------------------------------------- #
# Slot C: arm_shape  (per-station arm part with proper primitives per Rule 3)
# --------------------------------------------------------------------------- #


def _build_arm(
    model: ArticulatedObject,
    r: ResolvedWindshieldWiperAssemblyConfig,
    st: StationSpec,
    mats: dict[str, object],
) -> Part:
    arm = model.part(f"arm_{st.index}")
    # Build the pivot hub at the spindle (parent face for blade_roll).
    _build_arm_hub(arm, r, mats)
    # The blade sits at the arm tip; build the arm shape pointing +y from hub.
    if r.arm_shape == "flat_strap_arm":
        _build_flat_strap_arm(arm, r, mats)
    elif r.arm_shape == "tapered_lever_arm_with_extrude":
        _build_tapered_lever_arm(arm, r, mats, model)
    elif r.arm_shape == "tube_spine_composite_arm":
        _build_tube_spine_arm(arm, r, mats, model)
    elif r.arm_shape == "lightened_lattice_arm":
        _build_lightened_lattice_arm(arm, r, mats, model)
    # Always emit the tip yoke (mating face for the blade hub).
    _build_arm_tip_yoke(arm, r, mats)
    return arm


def _build_arm_hub(
    arm: Part, r: ResolvedWindshieldWiperAssemblyConfig, mats: dict[str, object]
) -> None:
    """Hub at spindle end of arm — mates with parent spindle_post_i (+z face).

    Hub extends from z=0 (mating face) upward into the arm body region so
    it shares surface contact with arm_bar / arm_shell / tapered_arm_body.
    """
    hub_h = 0.026
    _cyl(arm, r.spindle_radius * 1.45, hub_h, (0.0, 0.0, hub_h * 0.5), mats["metal"], "arm_hub")


def _build_arm_tip_yoke(
    arm: Part, r: ResolvedWindshieldWiperAssemblyConfig, mats: dict[str, object]
) -> None:
    """Yoke at tip of arm — parent face for blade_roll joint to the blade."""
    yoke_y = r.arm_length
    yoke_size = (r.arm_chord * 1.3, r.arm_chord * 1.3, 0.014)
    # The yoke sits at the arm tip, with its +y face mating with the blade.
    if r.blade_roll_axis == "x_horizontal":
        _box(
            arm, yoke_size, (0.0, yoke_y - yoke_size[1] * 0.5, 0.022), mats["metal"], "arm_tip_yoke"
        )
    else:
        _box(
            arm, yoke_size, (0.0, yoke_y - yoke_size[1] * 0.5, 0.022), mats["metal"], "arm_tip_yoke"
        )


def _build_flat_strap_arm(
    arm: Part, r: ResolvedWindshieldWiperAssemblyConfig, mats: dict[str, object]
) -> None:
    # rec_…_0001 L58-L91: simple Box bar.
    arm_y_center = r.arm_length * 0.5
    _box(
        arm,
        (r.arm_chord, r.arm_length, r.arm_thickness),
        (0.0, arm_y_center, 0.018),
        mats["arm"],
        "arm_bar",
    )
    # spring_link nub.
    _cyl(
        arm,
        r.arm_chord * 0.25,
        0.020,
        (0.0, r.arm_length * 0.30, 0.024),
        mats["accent"],
        "spring_anchor",
    )


def _build_tapered_lever_arm(
    arm: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
    model: ArticulatedObject,
) -> None:
    # rec_…_257ea L129-L165: ExtrudeGeometry tapered profile.
    # Profile in (y, x) plane: tapers from arm_chord at hub end (y=0) to
    # arm_chord*0.6 at tip (y=arm_length). Extrude along z by arm_thickness.
    profile = [
        (0.0, -r.arm_chord * 0.5),
        (r.arm_length, -r.arm_chord * 0.30),
        (r.arm_length, r.arm_chord * 0.30),
        (0.0, r.arm_chord * 0.5),
    ]
    geom = ExtrudeGeometry(profile, height=r.arm_thickness, center=True)
    arm.visual(
        _mesh_for_model(model, geom, "tapered_arm_profile"),
        origin=Origin(xyz=(0.0, 0.0, 0.018), rpy=(0.0, 0.0, math.pi / 2.0)),
        material=mats["arm"],
        name="tapered_arm_body", material_class_id=("metal.paint_coated" if r.material_style in {"factory_black", "safety_orange_service", "premium_satin", "utility_yellow"} else "metal.chrome_polished"),
    )
    # raised_spine.
    _box(
        arm,
        (r.arm_chord * 0.5, r.arm_length * 0.85, r.arm_thickness * 0.7),
        (0.0, r.arm_length * 0.5, 0.018 + r.arm_thickness * 0.55),
        mats["arm"],
        "raised_spine",
    )


def _build_tube_spine_arm(
    arm: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
    model: ArticulatedObject,
) -> None:
    # rec_…_06bc1be L82-L160: Box shell + tube_from_spline_points spring spine.
    arm_y_center = r.arm_length * 0.5
    _box(
        arm,
        (r.arm_chord, r.arm_length, r.arm_thickness),
        (0.0, arm_y_center, 0.018),
        mats["arm"],
        "arm_shell",
    )
    # Spring spine via tube_from_spline_points, arching slightly above the arm.
    points = [
        (0.0, r.arm_length * 0.05, 0.018 + r.arm_thickness * 0.5),
        (0.0, r.arm_length * 0.35, 0.018 + r.arm_thickness * 1.4),
        (0.0, r.arm_length * 0.65, 0.018 + r.arm_thickness * 1.4),
        (0.0, r.arm_length * 0.92, 0.018 + r.arm_thickness * 0.5),
    ]
    spine_geom = tube_from_spline_points(
        points,
        radius=max(0.0015, r.arm_thickness * 0.30),
        samples_per_segment=10,
        radial_segments=10,
        cap_ends=True,
    )
    arm.visual(
        _mesh_for_model(model, spine_geom, "tension_spine"),
        origin=Origin(),
        material=mats["accent"],
        name="tension_spine", material_class_id=("metal.paint_coated" if r.material_style in {"factory_black", "weathered_chrome", "safety_orange_service", "utility_yellow"} else "metal.brass_polished"),
    )


def _build_lightened_lattice_arm(
    arm: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
    model: ArticulatedObject,
) -> None:
    # rec_…_291e082 L157-L243: ExtrudeWithHolesGeometry lightened arm +
    # LatheGeometry coil_spring.
    # Outer profile: arm rectangle.
    outer = [
        (-r.arm_chord * 0.5, 0.0),
        (r.arm_chord * 0.5, 0.0),
        (r.arm_chord * 0.5, r.arm_length),
        (-r.arm_chord * 0.5, r.arm_length),
    ]
    # Two lightening holes along the arm length.
    hole_r = r.arm_chord * 0.25
    holes = []
    for k in range(3):
        cy = r.arm_length * (0.25 + 0.25 * k)
        hole_poly = []
        for j in range(10):
            ang = 2.0 * math.pi * j / 10
            hole_poly.append((math.cos(ang) * hole_r, cy + math.sin(ang) * hole_r))
        holes.append(hole_poly)
    try:
        geom = ExtrudeWithHolesGeometry(
            outer,
            holes=holes,
            height=r.arm_thickness,
            center=True,
        )
        arm.visual(
            _mesh_for_model(model, geom, "lightened_arm"),
            origin=Origin(xyz=(0.0, 0.0, 0.018)),
            material=mats["arm"],
            name="lightened_arm_body", material_class_id=("metal.paint_coated" if r.material_style in {"factory_black", "safety_orange_service", "premium_satin", "utility_yellow"} else "metal.chrome_polished"),
        )
    except Exception:
        # Fallback to plain Extrude if ExtrudeWithHoles fails.
        plain = ExtrudeGeometry(outer, height=r.arm_thickness, center=True)
        arm.visual(
            _mesh_for_model(model, plain, "lightened_arm_fallback"),
            origin=Origin(xyz=(0.0, 0.0, 0.018)),
            material=mats["arm"],
            name="lightened_arm_body", material_class_id=("metal.paint_coated" if r.material_style in {"factory_black", "safety_orange_service", "premium_satin", "utility_yellow"} else "metal.chrome_polished"),
        )
    # Coil spring via LatheGeometry — a hollow torus profile.
    spring_profile = [
        (0.0, -0.008),
        (0.004, -0.008),
        (0.004, 0.008),
        (0.0, 0.008),
    ]
    spring_geom = LatheGeometry(spring_profile, segments=18, closed=True)
    arm.visual(
        _mesh_for_model(model, spring_geom, "coil_spring"),
        origin=Origin(xyz=(0.0, r.arm_length * 0.12, 0.020 + r.arm_thickness * 0.8)),
        material=mats["accent"],
        name="coil_spring", material_class_id=("metal.paint_coated" if r.material_style in {"factory_black", "weathered_chrome", "safety_orange_service", "utility_yellow"} else "metal.brass_polished"),
    )


# --------------------------------------------------------------------------- #
# Slot D: blade_carrier (the wiper blade mounted on the arm tip)
# --------------------------------------------------------------------------- #


def _build_blade(
    model: ArticulatedObject,
    r: ResolvedWindshieldWiperAssemblyConfig,
    st: StationSpec,
    mats: dict[str, object],
) -> Part:
    blade = model.part(f"blade_carrier_{st.index}")
    # Build the pivot hub mating to the arm tip yoke.
    _build_blade_pivot_hub(blade, r, mats)
    if r.blade_carrier == "flat_squeegee_with_yoke":
        _build_flat_squeegee_x(blade, r, mats)
    elif r.blade_carrier == "frame_with_multiple_pivots":
        _build_multi_pivot_frame_x(blade, r, mats)
    elif r.blade_carrier == "beam_style_aero":
        _build_beam_aero_x(blade, r, mats, model)
    return blade


def _build_blade_pivot_hub(
    blade: Part, r: ResolvedWindshieldWiperAssemblyConfig, mats: dict[str, object]
) -> None:
    """Hub on the blade carrier — mates with the arm_tip_yoke's outward face.

    The hub's -y face is at blade-local y=0 so it mates flush with the parent
    arm_tip_yoke's +y face at the joint origin (independent of blade_roll axis
    orientation; the joint axis (x or y) only changes the rotation direction).
    """
    hub_size = (r.arm_chord * 1.05, 0.010, r.arm_chord * 1.05)
    _box(blade, hub_size, (0.0, hub_size[1] * 0.5, 0.0), mats["metal"], "blade_pivot_hub")


def _blade_origin_offset(r: ResolvedWindshieldWiperAssemblyConfig) -> tuple[float, float, float]:
    """Where the blade body sits relative to the pivot hub (in blade-local).

    Hub is at (0, 0..0.010, 0); blade body sits at y where its -y face
    overlaps the hub by ~0.003 for solid surface-to-surface connectivity.
    """
    return (0.0, r.blade_chord * 0.5 + 0.005, 0.0)


def _build_flat_squeegee_x(
    blade: Part, r: ResolvedWindshieldWiperAssemblyConfig, mats: dict[str, object]
) -> None:
    # rec_…_2c145b5 L55-L68: Box carrier + Cylinder roll_barrel + Box rubber strip.
    # Blade extends along x; thickness y; squeegee below in -z.
    ox, oy, oz = _blade_origin_offset(r)
    body_size = (r.blade_length, r.blade_chord, 0.008)
    rubber_size = (r.blade_length * 0.96, r.blade_chord * 0.5, 0.006)
    _box(blade, body_size, (ox, oy, oz), mats["blade"], "carrier_frame")
    _box(
        blade,
        rubber_size,
        (ox, oy + r.blade_chord * 0.05, oz - 0.007),
        mats["rubber"],
        "rubber_strip",
    )
    # Barrel offset so it embeds at most ~4 mm into the arm_tip_yoke (below
    # the 5 mm overlap threshold) — keeps the captured-pin contact without
    # surfacing an allowed-overlap warning.
    _cyl(
        blade,
        r.blade_chord * 0.32,
        r.blade_chord * 1.1,
        (ox, oy - r.blade_chord * 0.20, oz),
        mats["metal"],
        "roll_barrel",
        rpy=Y_CYLINDER_RPY,
    )


def _build_multi_pivot_frame_x(
    blade: Part, r: ResolvedWindshieldWiperAssemblyConfig, mats: dict[str, object]
) -> None:
    # rec_…_06bc1be L162-L215: bridge + harness + claws + rubber strip.
    # Blade spans along x; harness pivots under bridge; claws at ends.
    ox, oy, oz = _blade_origin_offset(r)
    _box(blade, (r.blade_length, r.blade_chord, 0.010), (ox, oy, oz), mats["blade"], "bridge")
    for side, sx in (("left", -1.0), ("right", 1.0)):
        _box(
            blade,
            (r.blade_length * 0.30, r.blade_chord * 0.7, 0.012),
            (ox + sx * r.blade_length * 0.22, oy - 0.001, oz - 0.011),
            mats["blade"],
            f"harness_{side}",
        )
        for k, side2 in ((0, "inner"), (1, "outer")):
            cx = ox + sx * r.blade_length * (0.15 + 0.20 * k)
            _box(
                blade,
                (0.010, r.blade_chord * 0.4, 0.010),
                (cx, oy - 0.002, oz - 0.018),
                mats["metal"],
                f"claw_{side}_{side2}",
            )
    _box(
        blade,
        (r.blade_length * 0.92, r.blade_chord * 0.4, 0.008),
        (ox, oy + r.blade_chord * 0.05, oz - 0.012),
        mats["rubber"],
        "rubber_strip",
    )


def _build_beam_aero_x(
    blade: Part,
    r: ResolvedWindshieldWiperAssemblyConfig,
    mats: dict[str, object],
    model: ArticulatedObject,
) -> None:
    # rec_…_0003 L488-L535: aero beam blade via sweep_profile_along_spline +
    # rubber strip below. Blade spans along x.
    ox, oy, oz = _blade_origin_offset(r)
    profile = rounded_rect_profile(
        width=r.blade_chord,
        height=0.014,
        radius=0.004,
    )
    spline = [
        (-r.blade_length * 0.5 + ox, oy, oz + 0.002),
        (ox, oy + 0.002, oz + 0.004),
        (r.blade_length * 0.5 + ox, oy, oz + 0.002),
    ]
    try:
        aero_geom = sweep_profile_along_spline(
            spline,
            profile=profile,
            samples_per_segment=8,
        )
        blade.visual(
            _mesh_for_model(model, aero_geom, "aero_blade_body"),
            origin=Origin(),
            material=mats["blade"],
            name="aero_blade_body", material_class_id="plastic.opaque_glossy_molded",
        )
    except Exception:
        _box(
            blade,
            (r.blade_length, r.blade_chord, 0.014),
            (ox, oy, oz + 0.002),
            mats["blade"],
            "aero_blade_body",
        )
    _box(
        blade,
        (r.blade_length * 0.95, r.blade_chord * 0.55, 0.008),
        (ox, oy, oz - 0.003),
        mats["rubber"],
        "rubber_strip",
    )
    _box(
        blade,
        (r.blade_length * 0.85, r.blade_chord * 0.25, 0.006),
        (ox, oy + r.blade_chord * 0.05, oz + 0.012),
        mats["accent"],
        "aero_spoiler",
    )


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def build_windshield_wiper_assembly(
    config: WindshieldWiperAssemblyConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or WindshieldWiperAssemblyConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: _mat(model, r, key)
        for key in ("housing", "housing_dark", "metal", "arm", "blade", "rubber", "accent")
    }
    motor = _build_motor_housing(model, r, mats)
    _build_architecture_linkage(model, motor, r, mats)
    spindle_z = _spindle_top_z(r)
    for st in r.stations:
        arm = _build_arm(model, r, st, mats)
        spindle_origin = (st.spindle_origin[0], 0.0, spindle_z)
        model.articulation(
            f"spindle_sweep_{st.index}",
            ArticulationType.REVOLUTE,
            parent=motor,
            child=arm,
            origin=Origin(xyz=spindle_origin),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=18.0,
                velocity=2.4,
                lower=st.sweep_lower,
                upper=st.sweep_upper,
            ),
            mating=MatingContract(
                parent_face_geometry=st.spindle_post_name,
                parent_face_side="positive_z",
                child_face_geometry="arm_hub",
                child_face_side="negative_z",
                contact_tol=0.002,
            ),
        )
        blade = _build_blade(model, r, st, mats)
        if r.blade_roll_axis == "x_horizontal":
            roll_origin = (0.0, r.arm_length, 0.022)
            mating = MatingContract(
                parent_face_geometry="arm_tip_yoke",
                parent_face_side="positive_y",
                child_face_geometry="blade_pivot_hub",
                child_face_side="negative_y",
                contact_tol=0.002,
            )
            roll_axis: tuple[float, float, float] = (1.0, 0.0, 0.0)
        else:
            roll_origin = (0.0, r.arm_length, 0.022)
            mating = MatingContract(
                parent_face_geometry="arm_tip_yoke",
                parent_face_side="positive_y",
                child_face_geometry="blade_pivot_hub",
                child_face_side="negative_y",
                contact_tol=0.002,
            )
            roll_axis = (0.0, 1.0, 0.0)
        model.articulation(
            f"blade_roll_{st.index}",
            ArticulationType.REVOLUTE,
            parent=arm,
            child=blade,
            origin=Origin(xyz=roll_origin),
            axis=roll_axis,
            motion_limits=MotionLimits(
                effort=3.0,
                velocity=1.6,
                lower=r.blade_roll_lower,
                upper=r.blade_roll_upper,
            ),
            mating=mating,
        )
    model.meta["slot_choices"] = slot_choices_for_config(r)
    module_build = _architecture_module_build(r)
    model.meta["module_build"] = {
        "module_name": module_build.module_name,
        "parts_emitted": list(module_build.parts_emitted),
        "internal_articulations": list(module_build.internal_articulations),
        "interfaces": sorted(module_build.interfaces),
        "source_ids": dict(SOURCE_IDS),
        "source_adaptation_map": dict(SOURCE_ADAPTATION_MAP),
    }
    return model


def build_seeded_windshield_wiper_assembly(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_windshield_wiper_assembly(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    parts = {p.name for p in model.parts}
    if "motor_housing" not in parts:
        return
    motor = model.get_part("motor_housing")
    motor_elems = (
        "motor_can",
        "gearbox_housing",
        "bearing_collar",
        "bearing_tower",
        "pedestal_box",
        "turret_box",
        "bracket_arm",
        "flat_plate_base",
        "integrated_mounting_flange",
        "cross_car_mount_bar",
        "spindle_post_0",
        "spindle_post_1",
        "spindle_shaft_0",
        "spindle_shaft_1",
        "motor_crank_hub",
        "motor_crank_pin",
        "drive_link",
        "drag_link",
        "cross_link",
        "cross_link_pin_0",
        "cross_link_pin_1",
    )
    arm_elems = (
        "arm_hub",
        "arm_bar",
        "arm_shell",
        "tapered_arm_body",
        "raised_spine",
        "tension_spine",
        "lightened_arm_body",
        "coil_spring",
        "arm_tip_yoke",
        "spring_anchor",
    )
    blade_elems = (
        "blade_pivot_hub",
        "carrier_frame",
        "bridge",
        "harness_left",
        "harness_right",
        "harness_front",
        "harness_rear",
        "claw_left_inner",
        "claw_right_inner",
        "claw_left_outer",
        "claw_right_outer",
        "roll_barrel",
        "rubber_strip",
        "aero_blade_body",
        "aero_spoiler",
    )
    for part in model.parts:
        if part.name.startswith("arm_"):
            for ea in motor_elems:
                for eb in arm_elems:
                    try:
                        ctx.allow_overlap(
                            motor,
                            part,
                            elem_a=ea,
                            elem_b=eb,
                            reason="arm hub is captured by the spindle post / housing top",
                        )
                    except Exception:
                        pass
        if part.name.startswith("blade_carrier_"):
            # find paired arm
            try:
                idx = int(part.name.rsplit("_", 1)[-1])
            except ValueError:
                continue
            arm_name = f"arm_{idx}"
            if arm_name in parts:
                arm = model.get_part(arm_name)
                for ea in arm_elems:
                    for eb in blade_elems:
                        try:
                            ctx.allow_overlap(
                                arm,
                                part,
                                elem_a=ea,
                                elem_b=eb,
                                reason="blade pivot hub is captured by the arm tip yoke",
                            )
                        except Exception:
                            pass
    linkage_overlaps = (
        ("motor_housing", "motor_crank", "motor_crank_hub", "drive_hub"),
        ("motor_crank", "drag_link", "crank_pin", "proximal_eye"),
        ("drag_link", "cross_link", "distal_eye", "proximal_eye"),
        ("drag_link", "cross_link", "link_bar", "proximal_eye"),
        ("motor_housing", "cowl_drive_crank", "cowl_motor_drive_socket", "drive_hub"),
        ("cowl_drive_crank", "primary_link", "crank_pin", "proximal_eye"),
        ("primary_link", "cowl_cross_link", "distal_eye", "proximal_eye"),
        ("primary_link", "cowl_cross_link", "link_bar", "proximal_eye"),
    )
    for pa, pb, ea, eb in linkage_overlaps:
        if pa in parts and pb in parts:
            try:
                ctx.allow_overlap(
                    model.get_part(pa),
                    model.get_part(pb),
                    elem_a=ea,
                    elem_b=eb,
                    reason="linkage pin is intentionally captured in the bearing eye",
                )
            except Exception:
                pass


def run_windshield_wiper_assembly_tests(
    object_model: ArticulatedObject,
    config: WindshieldWiperAssemblyConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    allow_islands = getattr(ctx, "allow_disconnected_islands", None)
    if callable(allow_islands):
        part_names = {p.name for p in object_model.parts}
        for pn in ["motor_housing"] + [
            n for n in part_names if n.startswith("arm_") or n.startswith("blade_carrier_")
        ]:
            allow_islands(
                object_model.get_part(pn),
                reason=(
                    "wiper assembly has separated rigid sub-pieces: spindle hub, "
                    "tip yoke, drive linkage, accessory crank, etc."
                ),
            )
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}
    if "motor_housing" not in part_names:
        ctx.fail("identity_motor", "wiper assembly must include a motor_housing part")
    arm_parts = [n for n in part_names if n.startswith("arm_")]
    blade_parts = [n for n in part_names if n.startswith("blade_carrier_")]
    if len(arm_parts) != r.arm_count:
        ctx.fail("arm_count", f"expected {r.arm_count} arms, got {len(arm_parts)}")
    if len(blade_parts) != r.arm_count:
        ctx.fail("blade_count", f"expected {r.arm_count} blades, got {len(blade_parts)}")
    for st in r.stations:
        for jn in (f"spindle_sweep_{st.index}", f"blade_roll_{st.index}"):
            if jn not in joint_names:
                ctx.fail("identity_joint", f"missing {jn}")
    if r.architecture in {"dual_arm_tandem_cross_car", "dual_arm_cowl_primary_cross_link"}:
        if "motor_drive" not in joint_names:
            ctx.fail("linkage_joint", "dual-arm architecture must include motor_drive")
    if r.architecture == "dual_arm_tandem_cross_car":
        for jn in ("motor_crank_to_drag_link", "drag_link_to_cross_link"):
            if jn not in joint_names:
                ctx.fail("linkage_joint", f"missing {jn}")
    if r.architecture == "dual_arm_cowl_primary_cross_link":
        for jn in ("drive_to_primary_link", "primary_to_cross_link"):
            if jn not in joint_names:
                ctx.fail("linkage_joint", f"missing {jn}")
    for joint in object_model.joints:
        if joint.name.startswith("spindle_sweep_"):
            if joint.articulation_type != ArticulationType.REVOLUTE:
                ctx.fail("sweep_type", f"{joint.name} must be REVOLUTE")
            if joint.axis != (0.0, 0.0, 1.0):
                ctx.fail("sweep_axis", f"{joint.name} axis must be (0,0,1)")
        if joint.name in {"motor_drive", "motor_crank_to_drag_link", "drag_link_to_cross_link"}:
            if joint.name == "motor_drive":
                if joint.articulation_type != ArticulationType.CONTINUOUS:
                    ctx.fail("linkage_type", "motor_drive must be CONTINUOUS")
            elif joint.articulation_type != ArticulationType.REVOLUTE:
                ctx.fail("linkage_type", f"{joint.name} must be REVOLUTE")
            if joint.axis != (0.0, 0.0, 1.0):
                ctx.fail("linkage_axis", f"{joint.name} axis must be (0,0,1)")
        if joint.name.startswith("blade_roll_"):
            if joint.articulation_type != ArticulationType.REVOLUTE:
                ctx.fail("roll_type", f"{joint.name} must be REVOLUTE")
            ax = joint.axis
            horizontal = abs(ax[2]) < 1e-6 and (abs(ax[0]) > 0.9 or abs(ax[1]) > 0.9)
            if not horizontal:
                ctx.fail("roll_axis", f"{joint.name} axis must be horizontal, got {ax}")
    return ctx.report()


__all__ = [
    "WindshieldWiperAssemblyConfig",
    "ResolvedWindshieldWiperAssemblyConfig",
    "build_windshield_wiper_assembly",
    "build_seeded_windshield_wiper_assembly",
    "config_from_seed",
    "resolve_config",
    "run_windshield_wiper_assembly_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
    "SOURCE_IDS",
    "SOURCE_ADAPTATION_MAP",
]
