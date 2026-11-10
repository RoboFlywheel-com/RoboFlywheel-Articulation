# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Modular procedural template for category ``car_axles``.

Based on ``rec_car_axles_0001``: a differential carrier (``axle_housing``)
with mirrored driven hubs (``left_hub`` / ``right_hub``) spinning about ±Y, and
an optional ``pinion_flange`` spinning about +X. Spoke studs on each hub are
visual-only (no joints) and reported via ``spoke_multiplicity``.

Geometry policy: Box and Cylinder primitives only (no mesh lofts).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/car_axles.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

HousingStyle = Literal["ribbed_pumpkin", "boxed_carrier", "tube_axle", "heavy_cast"]
HubStyle = Literal["machined_disk", "flanged_drum", "open_face", "stud_plate"]
MaterialStyle = Literal["cast_iron", "machined_steel", "fleet_gray", "matte_black"]

HOUSING_STYLES: tuple[HousingStyle, ...] = (
    "ribbed_pumpkin",
    "boxed_carrier",
    "tube_axle",
    "heavy_cast",
)
HUB_STYLES: tuple[HubStyle, ...] = ("machined_disk", "flanged_drum", "open_face", "stud_plate")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "cast_iron",
    "machined_steel",
    "fleet_gray",
    "matte_black",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "cast_iron": {
        "housing": (0.20, 0.20, 0.22, 1.0),
        "steel": (0.58, 0.60, 0.62, 1.0),
        "hardware": (0.73, 0.75, 0.78, 1.0),
        "rubber": (0.09, 0.09, 0.10, 1.0),
        "oxide": (0.14, 0.14, 0.15, 1.0),
    },
    "machined_steel": {
        "housing": (0.42, 0.43, 0.45, 1.0),
        "steel": (0.70, 0.72, 0.74, 1.0),
        "hardware": (0.82, 0.84, 0.86, 1.0),
        "rubber": (0.08, 0.08, 0.09, 1.0),
        "oxide": (0.22, 0.23, 0.25, 1.0),
    },
    "fleet_gray": {
        "housing": (0.34, 0.35, 0.36, 1.0),
        "steel": (0.56, 0.57, 0.58, 1.0),
        "hardware": (0.68, 0.69, 0.70, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
        "oxide": (0.18, 0.19, 0.20, 1.0),
    },
    "matte_black": {
        "housing": (0.10, 0.10, 0.11, 1.0),
        "steel": (0.28, 0.29, 0.30, 1.0),
        "hardware": (0.48, 0.49, 0.50, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
        "oxide": (0.08, 0.08, 0.09, 1.0),
    },
}

Y_CYL_RPY = (math.pi / 2.0, 0.0, 0.0)
X_CYL_RPY = (0.0, math.pi / 2.0, 0.0)
HUB_JOINT_Y = 0.828
PINION_JOINT_X = 0.292


@dataclass(frozen=True)
class CarAxlesConfig:
    housing_style: HousingStyle | None = None
    hub_style: HubStyle | None = None
    material_style: MaterialStyle = "cast_iron"
    has_pinion: bool = True
    spoke_count: int = 6
    axle_track_scale: float = 1.0
    hub_diameter_scale: float = 1.0
    name: str = "car_axle_assembly"


@dataclass(frozen=True)
class ResolvedCarAxlesConfig:
    housing_style: HousingStyle
    hub_style: HubStyle
    material_style: MaterialStyle
    has_pinion: bool
    spoke_count: int
    axle_track_scale: float
    hub_diameter_scale: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def _clamp_float(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _choice(value: str | None, allowed: tuple[str, ...], fallback: str, field: str) -> str:
    if value is None:
        return fallback
    if value not in allowed:
        raise ValueError(f"Unsupported {field}: {value}")
    return value


def config_from_seed(seed: int) -> CarAxlesConfig:
    if seed == 0:
        return CarAxlesConfig(
            housing_style="ribbed_pumpkin",
            hub_style="machined_disk",
            material_style="cast_iron",
            has_pinion=True,
            spoke_count=6,
            axle_track_scale=1.0,
            hub_diameter_scale=1.0,
            name="car_axle_assembly",
        )
    rng = random.Random(seed)
    return CarAxlesConfig(
        housing_style=rng.choice(HOUSING_STYLES),
        hub_style=rng.choice(HUB_STYLES),
        material_style=rng.choice(MATERIAL_STYLES),
        has_pinion=rng.random() < 0.72,
        spoke_count=rng.randint(4, 8),
        axle_track_scale=round(rng.uniform(0.85, 1.15), 3),
        hub_diameter_scale=round(rng.uniform(0.90, 1.10), 3),
        name=f"seeded_car_axles_{seed}",
    )


def resolve_config(config: CarAxlesConfig) -> ResolvedCarAxlesConfig:
    housing = _choice(config.housing_style, HOUSING_STYLES, "ribbed_pumpkin", "housing_style")
    hub = _choice(config.hub_style, HUB_STYLES, "machined_disk", "hub_style")
    material = _choice(config.material_style, MATERIAL_STYLES, "cast_iron", "material_style")
    spoke_count = _clamp_int(config.spoke_count, 4, 8)
    return ResolvedCarAxlesConfig(
        housing_style=housing,
        hub_style=hub,
        material_style=material,
        has_pinion=config.has_pinion,
        spoke_count=spoke_count,
        axle_track_scale=_clamp_float(config.axle_track_scale, 0.85, 1.15),
        hub_diameter_scale=_clamp_float(config.hub_diameter_scale, 0.90, 1.10),
        name=config.name or "car_axle_assembly",
        palette=dict(PALETTES[material]),
    )


def with_overrides(config: CarAxlesConfig, **kwargs: object) -> CarAxlesConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CarAxlesConfig | ResolvedCarAxlesConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCarAxlesConfig) else resolve_config(config)
    return (
        ("axle_housing", r.housing_style),
        ("hub_multiplicity", "2_driven_hubs"),
        ("pinion_module", "pinion_spin" if r.has_pinion else "none"),
        ("spoke_multiplicity", f"{r.spoke_count}_spokes"),
        ("material_palette", r.material_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _mat(model: ArticulatedObject, r: ResolvedCarAxlesConfig, key: str):
    return model.material(f"axle_{key}", rgba=r.palette[key])


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.cast_iron_bare")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


def _add_cover_bolts(part, sign_x: float, hardware) -> None:
    bolt_circle_radius = 0.104
    for idx in range(12):
        angle = (2.0 * math.pi * idx) / 12.0
        y = bolt_circle_radius * math.cos(angle)
        z = bolt_circle_radius * math.sin(angle)
        _cyl(part, 0.008, 0.014, (sign_x, y, z), hardware, f"cover_bolt_{idx}", X_CYL_RPY)


def _build_ribbed_pumpkin_housing(part, mats: dict[str, object]) -> None:
    sections = [
        (-0.220, 0.086, 0.160, 0.098),
        (-0.145, 0.112, 0.248, 0.136),
        (-0.060, 0.144, 0.332, 0.170),
        (0.060, 0.152, 0.304, 0.162),
        (0.155, 0.112, 0.224, 0.124),
        (0.220, 0.086, 0.160, 0.094),
    ]
    for idx, (x, h, w, d) in enumerate(sections):
        _box(part, (w, d, h), (x, 0.0, -0.020), mats["housing"], f"pumpkin_section_{idx}")
    _cyl(part, 0.132, 0.046, (-0.145, 0.0, 0.0), mats["housing"], "cover_barrel", X_CYL_RPY)
    _cyl(part, 0.146, 0.012, (-0.120, 0.0, 0.0), mats["housing"], "cover_flange", X_CYL_RPY)
    _add_cover_bolts(part, -0.168, mats["hardware"])


def _build_boxed_carrier_housing(part, mats: dict[str, object]) -> None:
    _box(part, (0.46, 0.34, 0.28), (0.0, 0.0, 0.0), mats["housing"], "carrier_core")
    _box(part, (0.34, 0.22, 0.18), (-0.14, 0.0, 0.04), mats["housing"], "cover_block")
    _cyl(part, 0.118, 0.040, (-0.14, 0.0, 0.0), mats["housing"], "cover_barrel", X_CYL_RPY)
    _add_cover_bolts(part, -0.168, mats["hardware"])
    for side in (-1.0, 1.0):
        _box(
            part,
            (0.12, 0.08, 0.10),
            (0.02, side * 0.08, -0.10),
            mats["housing"],
            f"mount_ear_{side}",
        )


def _build_tube_axle_housing(part, mats: dict[str, object]) -> None:
    _cyl(part, 0.148, 0.36, (0.0, 0.0, 0.0), mats["housing"], "center_tube", Y_CYL_RPY)
    _box(part, (0.30, 0.26, 0.20), (0.0, 0.0, -0.02), mats["housing"], "saddle_block")
    _cyl(part, 0.110, 0.034, (-0.14, 0.0, 0.0), mats["housing"], "cover_barrel", X_CYL_RPY)
    _box(part, (0.18, 0.14, 0.08), (-0.14, 0.0, 0.06), mats["housing"], "inspection_plate")


def _build_heavy_cast_housing(part, mats: dict[str, object]) -> None:
    _box(part, (0.52, 0.38, 0.30), (0.0, 0.0, 0.0), mats["housing"], "heavy_core")
    _box(part, (0.40, 0.30, 0.16), (0.0, 0.0, 0.18), mats["housing"], "upper_rib")
    _box(part, (0.36, 0.28, 0.12), (0.0, 0.0, -0.16), mats["housing"], "lower_rib")
    _cyl(part, 0.140, 0.050, (-0.15, 0.0, 0.0), mats["housing"], "cover_barrel", X_CYL_RPY)
    _add_cover_bolts(part, -0.170, mats["hardware"])


def _build_housing_sides(part, mats: dict[str, object], track: float) -> None:
    for side in (-1.0, 1.0):
        tag = "neg" if side < 0 else "pos"
        _cyl(
            part,
            0.092,
            0.58 * track,
            (0.0, side * 0.29 * track, 0.0),
            mats["housing"],
            f"axle_tunnel_{tag}",
            Y_CYL_RPY,
        )
        _box(
            part,
            (0.26, 0.12 * track, 0.18),
            (0.0, side * 0.40 * track, 0.02),
            mats["housing"],
            f"axle_saddle_{tag}",
        )
        _cyl(
            part,
            0.055,
            0.034 * track,
            (0.0, side * 0.811 * track, 0.0),
            mats["steel"],
            f"hub_bearing_boss_{tag}",
            Y_CYL_RPY,
        )
        _cyl(
            part,
            0.050,
            0.640 * track,
            (0.0, side * 0.500 * track, 0.0),
            mats["housing"],
            f"axle_tube_{tag}",
            Y_CYL_RPY,
        )
        _cyl(
            part,
            0.058,
            0.060 * track,
            (0.0, side * 0.770 * track, 0.0),
            mats["housing"],
            f"tube_boss_{tag}",
            Y_CYL_RPY,
        )
        _cyl(
            part,
            0.110,
            0.010 * track,
            (0.0, side * 0.802 * track, 0.0),
            mats["oxide"],
            f"seal_ring_{tag}",
            Y_CYL_RPY,
        )
        _box(
            part,
            (0.190, 0.120 * track, 0.014),
            (0.0, side * 0.340 * track, 0.057),
            mats["housing"],
            f"spring_pad_{tag}",
        )
        _box(
            part,
            (0.160, 0.090 * track, 0.008),
            (0.0, side * 0.340 * track, 0.068),
            mats["rubber"],
            f"isolator_{tag}",
        )
        _box(
            part,
            (0.050, 0.120 * track, 0.025),
            (0.0, side * 0.340 * track, 0.074),
            mats["housing"],
            f"mount_block_{tag}",
        )
        _box(
            part,
            (0.012, 0.050 * track, 0.110),
            (-0.036, side * 0.520 * track, 0.090),
            mats["housing"],
            f"strap_a_{tag}",
        )
        _box(
            part,
            (0.012, 0.050 * track, 0.110),
            (0.036, side * 0.520 * track, 0.090),
            mats["housing"],
            f"strap_b_{tag}",
        )
        _box(
            part,
            (0.012, 0.060 * track, 0.100),
            (-0.040, side * 0.205 * track, -0.070),
            mats["housing"],
            f"lower_strut_a_{tag}",
        )
        _box(
            part,
            (0.012, 0.060 * track, 0.100),
            (0.040, side * 0.205 * track, -0.070),
            mats["housing"],
            f"lower_strut_b_{tag}",
        )
        _box(
            part,
            (0.092, 0.040 * track, 0.014),
            (0.0, side * 0.205 * track, -0.120),
            mats["housing"],
            f"skid_plate_{tag}",
        )


def _build_pinion_neck(part, mats: dict[str, object]) -> None:
    _cyl(part, 0.072, 0.104, (0.170, 0.0, 0.0), mats["housing"], "pinion_neck", X_CYL_RPY)
    _cyl(part, 0.048, 0.080, (0.245, 0.0, 0.0), mats["housing"], "pinion_stub", X_CYL_RPY)
    _box(part, (0.112, 0.030, 0.118), (0.012, -0.075, -0.010), mats["housing"], "pinion_gusset_neg")
    _box(part, (0.112, 0.030, 0.118), (0.012, 0.075, -0.010), mats["housing"], "pinion_gusset_pos")
    _box(part, (0.128, 0.080, 0.022), (0.020, 0.0, -0.112), mats["housing"], "pinion_bridge")
    _box(part, (0.110, 0.070, 0.130), (0.095, 0.0, -0.040), mats["housing"], "pinion_bridge_core")
    _box(part, (0.050, 0.040, 0.080), (0.050, -0.015, 0.100), mats["housing"], "vent_boss")
    _cyl(part, 0.018, 0.020, (0.050, -0.015, 0.142), mats["oxide"], "vent_port")
    _box(part, (0.040, 0.034, 0.060), (-0.150, 0.040, 0.070), mats["housing"], "service_boss_a")
    _cyl(part, 0.010, 0.016, (-0.172, 0.042, 0.072), mats["hardware"], "service_bolt_a", X_CYL_RPY)
    _box(part, (0.090, 0.050, 0.120), (-0.125, 0.000, -0.030), mats["housing"], "service_bridge_b")
    _box(part, (0.040, 0.034, 0.060), (-0.150, 0.000, -0.080), mats["housing"], "service_boss_b")
    _cyl(part, 0.011, 0.018, (-0.172, 0.000, -0.108), mats["hardware"], "service_bolt_b", X_CYL_RPY)


def _build_housing(model: ArticulatedObject, r: ResolvedCarAxlesConfig, mats: dict[str, object]):
    housing = model.part("axle_housing")
    builders = {
        "ribbed_pumpkin": _build_ribbed_pumpkin_housing,
        "boxed_carrier": _build_boxed_carrier_housing,
        "tube_axle": _build_tube_axle_housing,
        "heavy_cast": _build_heavy_cast_housing,
    }
    builders[r.housing_style](housing, mats)
    _build_housing_sides(housing, mats, r.axle_track_scale)
    if r.has_pinion:
        _build_pinion_neck(housing, mats)
    housing.inertial = Inertial.from_geometry(
        Box((0.56, 1.66 * r.axle_track_scale, 0.38)),
        mass=92.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    return housing


def _add_hub_journal(part, sign: float, steel, *, seat_y: float) -> None:
    """Embed a journal that bridges the hub barrel and the carrier seat."""
    _cyl(
        part,
        0.048,
        max(0.050, abs(seat_y) * 1.35),
        (0.0, sign * (seat_y * 0.52), 0.0),
        steel,
        "hub_journal",
        Y_CYL_RPY,
    )


def _add_hub_spokes(
    part,
    sign: float,
    spoke_count: int,
    stud_radius: float,
    hardware,
    *,
    ring_y: float,
) -> None:
    _cyl(
        part,
        stud_radius * 0.92,
        0.014,
        (0.0, sign * ring_y, 0.0),
        hardware,
        "spoke_ring",
        Y_CYL_RPY,
    )
    for idx in range(spoke_count):
        angle = (2.0 * math.pi * idx) / spoke_count
        x = stud_radius * math.cos(angle)
        z = stud_radius * math.sin(angle)
        _cyl(
            part,
            0.007,
            0.030,
            (x, sign * ring_y, z),
            hardware,
            f"spoke_stud_{idx}",
            Y_CYL_RPY,
        )


def _build_machined_disk_hub(
    part, sign: float, r: ResolvedCarAxlesConfig, mats: dict[str, object]
) -> None:
    d = r.hub_diameter_scale
    _cyl(part, 0.042 * d, 0.058, (0.0, sign * 0.029, 0.0), mats["steel"], "hub_barrel", Y_CYL_RPY)
    _cyl(part, 0.055 * d, 0.018, (0.0, sign * 0.022, 0.0), mats["oxide"], "bearing_seat", Y_CYL_RPY)
    _cyl(part, 0.152 * d, 0.012, (0.0, sign * 0.050, 0.0), mats["steel"], "flange_plate", Y_CYL_RPY)
    _cyl(part, 0.073 * d, 0.034, (0.0, sign * 0.050, 0.0), mats["steel"], "center_boss", Y_CYL_RPY)
    _cyl(part, 0.095 * d, 0.024, (0.0, sign * 0.070, 0.0), mats["steel"], "outer_barrel", Y_CYL_RPY)
    _cyl(part, 0.030 * d, 0.040, (0.0, sign * 0.100, 0.0), mats["oxide"], "spindle_sleeve", Y_CYL_RPY)
    _cyl(part, 0.024 * d, 0.020, (0.0, sign * 0.114, 0.0), mats["oxide"], "spindle_cap", Y_CYL_RPY)
    _add_hub_spokes(part, sign, r.spoke_count, 0.062 * d, mats["hardware"], ring_y=0.062)
    _add_hub_journal(part, sign, mats["steel"], seat_y=0.032)


def _build_flanged_drum_hub(
    part, sign: float, r: ResolvedCarAxlesConfig, mats: dict[str, object]
) -> None:
    d = r.hub_diameter_scale
    _cyl(part, 0.050 * d, 0.070, (0.0, sign * 0.035, 0.0), mats["steel"], "drum_core", Y_CYL_RPY)
    _cyl(part, 0.120 * d, 0.018, (0.0, sign * 0.060, 0.0), mats["steel"], "wide_flange", Y_CYL_RPY)
    _cyl(part, 0.082 * d, 0.040, (0.0, sign * 0.082, 0.0), mats["steel"], "outer_barrel", Y_CYL_RPY)
    _box(part, (0.12 * d, 0.010, 0.12 * d), (0.0, sign * 0.102, 0.0), mats["oxide"], "face_plate")
    _add_hub_spokes(part, sign, r.spoke_count, 0.070 * d, mats["hardware"], ring_y=0.070)
    _add_hub_journal(part, sign, mats["steel"], seat_y=0.038)


def _build_open_face_hub(
    part, sign: float, r: ResolvedCarAxlesConfig, mats: dict[str, object]
) -> None:
    d = r.hub_diameter_scale
    _cyl(part, 0.038 * d, 0.050, (0.0, sign * 0.025, 0.0), mats["steel"], "hub_barrel", Y_CYL_RPY)
    _cyl(part, 0.100 * d, 0.010, (0.0, sign * 0.048, 0.0), mats["steel"], "thin_flange", Y_CYL_RPY)
    _cyl(part, 0.060 * d, 0.028, (0.0, sign * 0.066, 0.0), mats["steel"], "center_ring", Y_CYL_RPY)
    _box(part, (0.08 * d, 0.010, 0.08 * d), (0.0, sign * 0.078, 0.0), mats["oxide"], "open_face")
    _add_hub_spokes(part, sign, r.spoke_count, 0.054 * d, mats["hardware"], ring_y=0.054)
    _add_hub_journal(part, sign, mats["steel"], seat_y=0.026)


def _build_stud_plate_hub(
    part, sign: float, r: ResolvedCarAxlesConfig, mats: dict[str, object]
) -> None:
    d = r.hub_diameter_scale
    _box(part, (0.18 * d, 0.014, 0.18 * d), (0.0, sign * 0.050, 0.0), mats["steel"], "lug_plate")
    _cyl(part, 0.040 * d, 0.084, (0.0, sign * 0.044, 0.0), mats["steel"], "inner_barrel", Y_CYL_RPY)
    _add_hub_spokes(part, sign, r.spoke_count, 0.058 * d, mats["hardware"], ring_y=0.072)
    _cyl(part, 0.028 * d, 0.030, (0.0, sign * 0.090, 0.0), mats["oxide"], "spindle_stub", Y_CYL_RPY)
    _add_hub_journal(part, sign, mats["steel"], seat_y=0.034)


def _build_hub(
    model: ArticulatedObject,
    name: str,
    sign: float,
    r: ResolvedCarAxlesConfig,
    mats: dict[str, object],
):
    part = model.part(name)
    builders = {
        "machined_disk": _build_machined_disk_hub,
        "flanged_drum": _build_flanged_drum_hub,
        "open_face": _build_open_face_hub,
        "stud_plate": _build_stud_plate_hub,
    }
    builders[r.hub_style](part, sign, r, mats)
    part.inertial = Inertial.from_geometry(
        Box((0.32 * r.hub_diameter_scale, 0.14, 0.32 * r.hub_diameter_scale)),
        mass=14.5,
        origin=Origin(xyz=(0.0, sign * 0.072, 0.0)),
    )
    return part


def _build_pinion(model: ArticulatedObject, mats: dict[str, object]):
    pinion = model.part("pinion_flange")
    _cyl(pinion, 0.048, 0.054, (-0.003, 0.0, 0.0), mats["steel"], "pinion_journal", X_CYL_RPY)
    _cyl(pinion, 0.034, 0.042, (0.021, 0.0, 0.0), mats["steel"], "pinion_shaft", X_CYL_RPY)
    _cyl(pinion, 0.062, 0.016, (0.046, 0.0, 0.0), mats["steel"], "pinion_flange_disc", X_CYL_RPY)
    _cyl(pinion, 0.024, 0.030, (0.066, 0.0, 0.0), mats["oxide"], "pinion_sleeve", X_CYL_RPY)
    _cyl(pinion, 0.018, 0.018, (0.086, 0.0, 0.0), mats["oxide"], "pinion_nose", X_CYL_RPY)
    for idx, (dy, dz) in enumerate(((0.034, 0.0), (-0.034, 0.0), (0.0, 0.034), (0.0, -0.034))):
        _cyl(
            pinion, 0.010, 0.018, (0.052, dy, dz), mats["hardware"], f"pinion_bolt_{idx}", X_CYL_RPY
        )
    pinion.inertial = Inertial.from_geometry(
        Box((0.11, 0.14, 0.14)),
        mass=3.4,
        origin=Origin(xyz=(0.050, 0.0, 0.0)),
    )
    return pinion


def build_car_axles(
    config: CarAxlesConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or CarAxlesConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {key: _mat(model, r, key) for key in ("housing", "steel", "hardware", "rubber", "oxide")}

    housing = _build_housing(model, r, mats)
    left_hub = _build_hub(model, "left_hub", -1.0, r, mats)
    right_hub = _build_hub(model, "right_hub", 1.0, r, mats)

    hub_joint_y = HUB_JOINT_Y * r.axle_track_scale
    model.articulation(
        "left_hub_spin",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=left_hub,
        origin=Origin(xyz=(0.0, -hub_joint_y, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1800.0, velocity=40.0),
    )
    model.articulation(
        "right_hub_spin",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=right_hub,
        origin=Origin(xyz=(0.0, hub_joint_y, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1800.0, velocity=40.0),
    )

    if r.has_pinion:
        pinion = _build_pinion(model, mats)
        model.articulation(
            "pinion_spin",
            ArticulationType.CONTINUOUS,
            parent=housing,
            child=pinion,
            origin=Origin(xyz=(PINION_JOINT_X, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=650.0, velocity=90.0),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_car_axles(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_car_axles(config_from_seed(seed), assets=assets)


def _allow_bearing_contacts(ctx: TestContext, has_pinion: bool) -> None:
    for hub, tube_tag in (("left_hub", "neg"), ("right_hub", "pos")):
        ctx.allow_overlap(
            "axle_housing",
            hub,
            elem_a=f"hub_bearing_boss_{tube_tag}",
            elem_b="hub_journal",
            reason="hub journal seats in the carrier bearing boss",
        )
        ctx.allow_overlap(
            "axle_housing",
            hub,
            elem_a=f"axle_tube_{tube_tag}",
            elem_b="hub_journal",
            reason="hub journal rides the axle tube at the outboard bearing",
        )
        ctx.allow_overlap(
            "axle_housing",
            hub,
            elem_a=f"tube_boss_{tube_tag}",
            elem_b="hub_journal",
            reason="hub journal captures the tube end boss",
        )
        ctx.allow_overlap(
            "axle_housing",
            hub,
            elem_a=f"seal_ring_{tube_tag}",
            elem_b="hub_journal",
            reason="hub journal seats against the outboard seal ring",
        )
    if has_pinion:
        ctx.allow_overlap(
            "axle_housing",
            "pinion_flange",
            elem_a="pinion_stub",
            elem_b="pinion_journal",
            reason="pinion journal seats in the carrier neck",
        )
        ctx.allow_overlap(
            "axle_housing",
            "pinion_flange",
            reason="pinion flange overlaps the forward carrier envelope at the bearing",
        )


def run_car_axles_tests(object_model: ArticulatedObject, config: CarAxlesConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_bearing_contacts(ctx, r.has_pinion)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    part_names = {part.name for part in object_model.parts}
    ctx.check("housing_present", "axle_housing" in part_names, details=str(sorted(part_names)))
    ctx.check("left_hub_present", "left_hub" in part_names, details=str(sorted(part_names)))
    ctx.check("right_hub_present", "right_hub" in part_names, details=str(sorted(part_names)))
    if r.has_pinion:
        ctx.check("pinion_present", "pinion_flange" in part_names, details=str(sorted(part_names)))
    else:
        ctx.check(
            "pinion_absent", "pinion_flange" not in part_names, details=str(sorted(part_names))
        )

    left_joint = object_model.get_articulation("left_hub_spin")
    right_joint = object_model.get_articulation("right_hub_spin")
    ctx.check("left_hub_continuous", left_joint.articulation_type == ArticulationType.CONTINUOUS)
    ctx.check("right_hub_continuous", right_joint.articulation_type == ArticulationType.CONTINUOUS)
    ctx.check(
        "left_hub_axis", tuple(left_joint.axis) == (0.0, 1.0, 0.0), details=str(left_joint.axis)
    )
    ctx.check(
        "right_hub_axis", tuple(right_joint.axis) == (0.0, 1.0, 0.0), details=str(right_joint.axis)
    )

    if r.has_pinion:
        pinion_joint = object_model.get_articulation("pinion_spin")
        ctx.check(
            "pinion_continuous", pinion_joint.articulation_type == ArticulationType.CONTINUOUS
        )
        ctx.check(
            "pinion_axis",
            tuple(pinion_joint.axis) == (1.0, 0.0, 0.0),
            details=str(pinion_joint.axis),
        )

    housing_pos = ctx.part_world_position("axle_housing")
    left_pos = ctx.part_world_position("left_hub")
    right_pos = ctx.part_world_position("right_hub")
    ctx.check("housing_centered", abs(housing_pos[0]) < 1e-6 and abs(housing_pos[1]) < 1e-6)
    ctx.check("left_hub_outboard", left_pos[1] < -0.80 * r.axle_track_scale)
    ctx.check("right_hub_outboard", right_pos[1] > 0.80 * r.axle_track_scale)
    ctx.check("hubs_mirrored", abs(left_pos[1] + right_pos[1]) < 1e-6)

    if r.has_pinion:
        pinion_pos = ctx.part_world_position("pinion_flange")
        ctx.check("pinion_forward", pinion_pos[0] > housing_pos[0] + 0.28)
        ctx.check("pinion_centered", abs(pinion_pos[1] - housing_pos[1]) < 1e-6)

    spoke_names = [
        v.name
        for v in object_model.get_part("left_hub").visuals
        if v.name.startswith("spoke_stud_")
    ]
    ctx.check(
        "spoke_count",
        len(spoke_names) == r.spoke_count,
        details=f"expected {r.spoke_count}, got {len(spoke_names)}",
    )

    expected_slots = dict(slot_choices_for_config(r))
    recorded = dict(object_model.meta.get("slot_choices", ()))
    ctx.check(
        "slot_choices_recorded",
        recorded == expected_slots,
        details=f"{recorded} vs {expected_slots}",
    )

    return ctx.report()


__all__ = [
    "CarAxlesConfig",
    "ResolvedCarAxlesConfig",
    "build_car_axles",
    "build_seeded_car_axles",
    "config_from_seed",
    "resolve_config",
    "run_car_axles_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
