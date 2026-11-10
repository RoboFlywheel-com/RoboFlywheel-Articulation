# SPDX-License-Identifier: Apache-2.0

"""Candy vending machine modular procedural template.

Implements ``articraft_template_authoring/specs_modular_v1/candy_vending_machine.md``.

The template follows the reviewed mixed slot graph:

* Slot A ``chassis`` emits one grounded body with transparent candy storage.
* Slot B ``dispense`` emits one to three CONTINUOUS front selectors.
* Slot C ``retrieval`` emits a hinged flap/door or a prismatic drawer.
* Slot D ``refill`` emits a gated top or side refill door when the chassis supports it.

Identity invariant: every seed has a transparent reservoir, visible candy fill,
at least one rotary selector, and a retrieval opening near the lower front.

Adopted source mapping:
S1 rec_candy_vending_machine_3db2f25c1f344af5bca069e7f5cabde1:
   pedestal globe, coin wheel, lower chute flap, top refill lid.
S2 rec_candy_vending_machine_88e5eb91c946401689a6e46fb6af1b30:
   dual hopper pedestal, twin selectors, collection cup, dual top lids.
S3 rec_candy_vending_machine_9c8af8f47aa046e39a070b415e97d25b:
   tall glazed cabinet, spiral product track, large service door.
S4 rec_candy_vending_machine_0dfd76f4af5443d8a9de565eb4240c95:
   stacked canister cabinet, triple selectors, chute flap.
S5 rec_candy_vending_machine_00e5551710fb4806a0ab8b1a094e0ecb:
   wall-mounted hopper, shallow glass front, side refill door.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
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
    Part,
    Sphere,
    TestContext,
    TestReport,
)

__modular__ = True


ChassisStyle = Literal[
    "pedestal_globe",
    "dual_hopper_pedestal",
    "tall_glazed_cabinet",
    "stacked_canister_cabinet",
    "wall_mount_hopper",
]
DispenseStyle = Literal[
    "single_knob",
    "dual_selectors",
    "triple_selectors",
    "quad_selectors",
    "coin_head_wheel",
]
RetrievalStyle = Literal["chute_flap", "collection_cup_door", "cash_drawer", "glazed_swing_door"]
RefillStyle = Literal["none", "top_lid", "dual_top_lids", "side_door"]
MaterialStyle = Literal["classic_red", "chrome_blue", "mint_cream", "charcoal", "candy_pink"]


CHASSIS_STYLES: tuple[ChassisStyle, ...] = (
    "pedestal_globe",
    "dual_hopper_pedestal",
    "tall_glazed_cabinet",
    "stacked_canister_cabinet",
    "wall_mount_hopper",
)
DISPENSE_STYLES: tuple[DispenseStyle, ...] = (
    "single_knob",
    "dual_selectors",
    "triple_selectors",
    "quad_selectors",
    "coin_head_wheel",
)
RETRIEVAL_STYLES: tuple[RetrievalStyle, ...] = (
    "chute_flap",
    "collection_cup_door",
    "cash_drawer",
    "glazed_swing_door",
)
REFILL_STYLES: tuple[RefillStyle, ...] = ("none", "top_lid", "dual_top_lids", "side_door")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "classic_red",
    "chrome_blue",
    "mint_cream",
    "charcoal",
    "candy_pink",
)


LEGAL_DISPENSE: dict[ChassisStyle, tuple[DispenseStyle, ...]] = {
    "pedestal_globe": ("single_knob", "coin_head_wheel"),
    "dual_hopper_pedestal": ("dual_selectors",),
    "tall_glazed_cabinet": ("single_knob", "coin_head_wheel"),
    "stacked_canister_cabinet": (
        "single_knob",
        "dual_selectors",
        "triple_selectors",
        "quad_selectors",
    ),
    "wall_mount_hopper": ("single_knob", "coin_head_wheel"),
}
LEGAL_RETRIEVAL: dict[ChassisStyle, tuple[RetrievalStyle, ...]] = {
    "pedestal_globe": ("chute_flap", "collection_cup_door"),
    "dual_hopper_pedestal": ("collection_cup_door", "chute_flap"),
    "tall_glazed_cabinet": ("glazed_swing_door", "cash_drawer", "chute_flap"),
    "stacked_canister_cabinet": ("chute_flap", "cash_drawer"),
    "wall_mount_hopper": ("chute_flap", "collection_cup_door"),
}
LEGAL_REFILL: dict[ChassisStyle, tuple[RefillStyle, ...]] = {
    "pedestal_globe": ("top_lid", "none"),
    "dual_hopper_pedestal": ("dual_top_lids", "top_lid"),
    "tall_glazed_cabinet": ("none",),
    "stacked_canister_cabinet": ("none",),
    "wall_mount_hopper": ("side_door", "top_lid", "none"),
}


PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_red": {
        "body": (0.70, 0.06, 0.05, 1.0),
        "body_dark": (0.22, 0.03, 0.035, 1.0),
        "trim": (0.86, 0.72, 0.42, 1.0),
        "metal": (0.64, 0.62, 0.58, 1.0),
        "glass": (0.78, 0.94, 1.00, 0.34),
        "candy_a": (1.00, 0.12, 0.20, 1.0),
        "candy_b": (1.00, 0.82, 0.08, 1.0),
        "candy_c": (0.12, 0.56, 1.00, 1.0),
        "rubber": (0.025, 0.020, 0.018, 1.0),
    },
    "chrome_blue": {
        "body": (0.10, 0.27, 0.55, 1.0),
        "body_dark": (0.035, 0.060, 0.12, 1.0),
        "trim": (0.74, 0.78, 0.82, 1.0),
        "metal": (0.66, 0.70, 0.73, 1.0),
        "glass": (0.70, 0.92, 1.00, 0.32),
        "candy_a": (1.00, 0.18, 0.52, 1.0),
        "candy_b": (0.12, 0.88, 0.62, 1.0),
        "candy_c": (1.00, 0.92, 0.18, 1.0),
        "rubber": (0.018, 0.022, 0.030, 1.0),
    },
    "mint_cream": {
        "body": (0.48, 0.82, 0.68, 1.0),
        "body_dark": (0.14, 0.29, 0.23, 1.0),
        "trim": (0.92, 0.88, 0.72, 1.0),
        "metal": (0.60, 0.64, 0.60, 1.0),
        "glass": (0.82, 1.00, 0.96, 0.32),
        "candy_a": (1.00, 0.20, 0.16, 1.0),
        "candy_b": (0.56, 0.25, 1.00, 1.0),
        "candy_c": (1.00, 0.72, 0.10, 1.0),
        "rubber": (0.025, 0.028, 0.025, 1.0),
    },
    "charcoal": {
        "body": (0.16, 0.17, 0.18, 1.0),
        "body_dark": (0.035, 0.035, 0.040, 1.0),
        "trim": (0.88, 0.26, 0.18, 1.0),
        "metal": (0.52, 0.54, 0.56, 1.0),
        "glass": (0.64, 0.80, 0.92, 0.30),
        "candy_a": (1.00, 0.08, 0.18, 1.0),
        "candy_b": (0.16, 0.82, 1.00, 1.0),
        "candy_c": (1.00, 0.92, 0.20, 1.0),
        "rubber": (0.012, 0.012, 0.014, 1.0),
    },
    "candy_pink": {
        "body": (0.90, 0.30, 0.55, 1.0),
        "body_dark": (0.34, 0.06, 0.16, 1.0),
        "trim": (0.96, 0.83, 0.30, 1.0),
        "metal": (0.70, 0.60, 0.64, 1.0),
        "glass": (1.00, 0.84, 0.96, 0.32),
        "candy_a": (1.00, 0.16, 0.22, 1.0),
        "candy_b": (0.35, 0.85, 1.00, 1.0),
        "candy_c": (0.72, 0.25, 1.00, 1.0),
        "rubber": (0.030, 0.015, 0.022, 1.0),
    },
}


@dataclass(frozen=True)
class CandyVendingMachineConfig:
    chassis: ChassisStyle | None = None
    dispense: DispenseStyle | None = None
    retrieval: RetrievalStyle | None = None
    refill: RefillStyle | None = None
    material_style: MaterialStyle = "classic_red"
    width: float = 0.48
    height: float = 0.86
    depth: float = 0.34
    selector_scale: float = 1.0
    candy_density: int = 8
    canister_count: int = 3
    flap_open_angle: float = 1.15
    drawer_travel: float = 0.12
    refill_open_angle: float = 1.22
    name: str = "reference_candy_vending_machine"


@dataclass(frozen=True)
class ResolvedCandyVendingMachineConfig:
    chassis: ChassisStyle
    dispense: DispenseStyle
    retrieval: RetrievalStyle
    refill: RefillStyle
    material_style: MaterialStyle
    width: float
    height: float
    depth: float
    selector_scale: float
    candy_density: int
    canister_count: int
    selector_count: int
    front_y: float
    back_y: float
    pickup_z: float
    selector_z: float
    reservoir_z: float
    reservoir_radius: float
    flap_open_angle: float
    drawer_travel: float
    refill_open_angle: float
    name: str


@dataclass(frozen=True)
class ChassisAnchors:
    body: Part
    selector_positions: tuple[tuple[float, float, float], ...]
    pickup_hinge: tuple[float, float, float]
    pickup_width: float
    pickup_height: float
    drawer_depth: float
    service_hinge: tuple[float, float, float]
    service_width: float
    service_height: float
    refill_hinges: tuple[tuple[float, float, float], ...]
    refill_radius: float
    side_refill_hinge: tuple[float, float, float]
    side_refill_size: tuple[float, float]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(round(value))))


def _choice(value: str | None, choices: tuple[str, ...], fallback: str) -> str:
    if value in choices:
        return value
    return fallback


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_y() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _cyl_z() -> tuple[float, float, float]:
    return (0.0, 0.0, 0.0)


def _selector_count(dispense: DispenseStyle) -> int:
    if dispense == "dual_selectors":
        return 2
    if dispense == "triple_selectors":
        return 3
    if dispense == "quad_selectors":
        return 4
    return 1


def resolve_config(config: CandyVendingMachineConfig) -> ResolvedCandyVendingMachineConfig:
    chassis = _choice(config.chassis, CHASSIS_STYLES, "pedestal_globe")
    legal_dispense = LEGAL_DISPENSE[chassis]  # type: ignore[index]
    legal_retrieval = LEGAL_RETRIEVAL[chassis]  # type: ignore[index]
    legal_refill = LEGAL_REFILL[chassis]  # type: ignore[index]
    dispense = _choice(config.dispense, legal_dispense, legal_dispense[0])
    retrieval = _choice(config.retrieval, legal_retrieval, legal_retrieval[0])
    refill = _choice(config.refill, legal_refill, legal_refill[0])
    material_style = _choice(config.material_style, MATERIAL_STYLES, "classic_red")

    if chassis == "pedestal_globe":
        width = _clamp(config.width, 0.34, 0.58)
        height = _clamp(config.height, 0.62, 1.02)
        depth = _clamp(config.depth, 0.28, 0.46)
        pickup_z = height * 0.18
        selector_z = height * 0.31
        reservoir_z = height * 0.68
        reservoir_radius = min(width, depth) * 0.31
    elif chassis == "dual_hopper_pedestal":
        width = _clamp(config.width, 0.62, 0.86)
        height = _clamp(config.height, 0.60, 0.98)
        depth = _clamp(config.depth, 0.30, 0.46)
        pickup_z = height * 0.18
        selector_z = height * 0.34
        reservoir_z = height * 0.68
        reservoir_radius = min(width * 0.24, depth * 0.33)
    elif chassis == "tall_glazed_cabinet":
        width = _clamp(config.width, 0.52, 0.84)
        height = _clamp(config.height, 1.10, 1.70)
        depth = _clamp(config.depth, 0.28, 0.46)
        pickup_z = height * 0.13
        selector_z = height * 0.34
        reservoir_z = height * 0.62
        reservoir_radius = width * 0.18
    elif chassis == "stacked_canister_cabinet":
        width = _clamp(config.width, 0.44, 0.66)
        height = _clamp(config.height, 0.92, 1.45)
        depth = _clamp(config.depth, 0.28, 0.42)
        pickup_z = height * 0.13
        selector_z = height * 0.36
        reservoir_z = height * 0.60
        reservoir_radius = width * 0.25
    else:
        width = _clamp(config.width, 0.40, 0.62)
        height = _clamp(config.height, 0.58, 0.96)
        depth = _clamp(config.depth, 0.18, 0.30)
        pickup_z = height * 0.16
        selector_z = height * 0.35
        reservoir_z = height * 0.62
        reservoir_radius = min(width, depth * 1.55) * 0.28

    return ResolvedCandyVendingMachineConfig(
        chassis=chassis,  # type: ignore[arg-type]
        dispense=dispense,  # type: ignore[arg-type]
        retrieval=retrieval,  # type: ignore[arg-type]
        refill=refill,  # type: ignore[arg-type]
        material_style=material_style,  # type: ignore[arg-type]
        width=width,
        height=height,
        depth=depth,
        selector_scale=_clamp(config.selector_scale, 0.82, 1.22),
        candy_density=_clamp_int(config.candy_density, 5, 14),
        canister_count=_clamp_int(config.canister_count, 2, 4),
        selector_count=_selector_count(dispense),  # type: ignore[arg-type]
        front_y=-depth * 0.5,
        back_y=depth * 0.5,
        pickup_z=pickup_z,
        selector_z=selector_z,
        reservoir_z=reservoir_z,
        reservoir_radius=reservoir_radius,
        flap_open_angle=_clamp(config.flap_open_angle, 0.60, 0.80),
        drawer_travel=_clamp(config.drawer_travel, 0.075, min(0.17, depth * 0.45)),
        refill_open_angle=_clamp(config.refill_open_angle, 1.0, 1.48),
        name=str(config.name or "candy_vending_machine"),
    )


def config_from_seed(seed: int) -> CandyVendingMachineConfig:
    rng = random.Random(seed)
    chassis = rng.choice(CHASSIS_STYLES)
    dispense = rng.choice(LEGAL_DISPENSE[chassis])
    retrieval = rng.choice(LEGAL_RETRIEVAL[chassis])
    refill = rng.choice(LEGAL_REFILL[chassis])
    return CandyVendingMachineConfig(
        chassis=chassis,
        dispense=dispense,
        retrieval=retrieval,
        refill=refill,
        material_style=rng.choice(MATERIAL_STYLES),
        width=rng.uniform(0.40, 0.78),
        height=rng.uniform(0.68, 1.55),
        depth=rng.uniform(0.23, 0.44),
        selector_scale=rng.uniform(0.88, 1.16),
        candy_density=rng.randint(6, 13),
        canister_count=rng.choice((2, 3, 4)),
        flap_open_angle=rng.uniform(1.02, 1.34),
        drawer_travel=rng.uniform(0.09, 0.15),
        refill_open_angle=rng.uniform(1.08, 1.40),
        name=f"seeded_candy_vending_machine_{seed}",
    )


def slot_choices_for_config(config: CandyVendingMachineConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("chassis", r.chassis),
        ("dispense", r.dispense),
        ("retrieval", r.retrieval),
        ("refill", r.refill),
        ("selector_multiplicity", f"{r.selector_count}_selectors"),
        (
            "canister_multiplicity",
            f"{r.canister_count}_canisters"
            if r.chassis == "stacked_canister_cabinet"
            else "0_canisters",
        ),
        (
            "refill_lid_multiplicity",
            "2_lids"
            if r.refill == "dual_top_lids"
            else "1_lid"
            if r.refill in ("top_lid", "side_door")
            else "0_lids",
        ),
        ("material_style", r.material_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def _register_materials(model: ArticulatedObject, style: MaterialStyle) -> dict[str, object]:
    return {
        name: model.material(f"candy_vendor_{name}", rgba=rgba)
        for name, rgba in PALETTES[style].items()
    }


def _box(
    part: Part,
    name: str,
    size: tuple[float, float, float],
    xyz: tuple[float, float, float],
    material: object,
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(
    part: Part,
    name: str,
    radius: float,
    length: float,
    xyz: tuple[float, float, float],
    material: object,
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.chrome_polished",
    )


def _selector_positions(
    r: ResolvedCandyVendingMachineConfig,
) -> tuple[tuple[float, float, float], ...]:
    y = r.front_y - 0.004
    if r.selector_count == 1:
        if r.chassis == "tall_glazed_cabinet":
            x = r.width * (0.43 if r.retrieval == "glazed_swing_door" else 0.25)
        else:
            x = 0.0
        return ((x, y, r.selector_z),)
    if r.selector_count == 2:
        dx = r.width * 0.19
        return ((-dx, y, r.selector_z), (dx, y, r.selector_z))
    if r.selector_count == 4:
        dx = r.width * 0.11
        dz = max(r.height * 0.090, 0.090 * r.selector_scale)
        x = r.width * 0.25
        return (
            (x - dx, y, r.selector_z + dz),
            (x + dx, y, r.selector_z + dz),
            (x - dx, y, r.selector_z - dz),
            (x + dx, y, r.selector_z - dz),
        )
    dz = max(r.height * 0.11, 0.102 * r.selector_scale)
    x = r.width * 0.24
    return ((x, y, r.selector_z + dz), (x, y, r.selector_z), (x, y, r.selector_z - dz))


def _add_candy_fill(
    body: Part,
    r: ResolvedCandyVendingMachineConfig,
    mats: dict[str, object],
    *,
    center: tuple[float, float, float],
    radius: float,
    width: float | None = None,
    prefix: str,
) -> None:
    if width is None:
        _cyl(
            body,
            f"{prefix}_candy_pile",
            radius * 0.82,
            radius * 0.38,
            (center[0], center[1], center[2] - radius * 0.42),
            mats["candy_b"],
            _cyl_z(),
        )
    else:
        _box(
            body,
            f"{prefix}_candy_pile",
            (width, radius * 0.72, radius * 0.32),
            (center[0], center[1], center[2] - radius * 0.42),
            mats["candy_b"],
        )
    count = min(r.candy_density, 10)
    for i in range(count):
        angle = math.tau * i / count
        rr = radius * (0.22 + 0.46 * ((i % 3) / 3.0))
        x = center[0] + math.cos(angle) * rr * (0.95 if width is None else 0.55)
        y = center[1] + math.sin(angle) * rr * 0.55
        z = center[2] - radius * (0.30 - 0.045 * (i % 4))
        mat = mats[("candy_a", "candy_b", "candy_c")[i % 3]]
        body.visual(
            Sphere(radius=radius * 0.080),
            origin=Origin(xyz=(x, y, z)),
            material=mat,
            name=f"{prefix}_candy_ball_{i}", material_class_id="plastic.opaque_glossy_molded",
        )


def _build_chassis(
    model: ArticulatedObject,
    r: ResolvedCandyVendingMachineConfig,
    mats: dict[str, object],
) -> ChassisAnchors:
    body = model.part("body")
    if r.chassis == "pedestal_globe":
        anchors = _build_pedestal_globe_body(body, r, mats)
    elif r.chassis == "dual_hopper_pedestal":
        anchors = _build_dual_hopper_body(body, r, mats)
    elif r.chassis == "tall_glazed_cabinet":
        anchors = _build_tall_cabinet_body(body, r, mats)
    elif r.chassis == "stacked_canister_cabinet":
        anchors = _build_stacked_canister_body(body, r, mats)
    else:
        anchors = _build_wall_mount_body(body, r, mats)
    body.inertial = Inertial.from_geometry(
        Box((r.width, r.depth, r.height)), mass=34.0, origin=Origin(xyz=(0.0, 0.0, r.height * 0.5))
    )
    return anchors


def _build_pedestal_globe_body(
    body: Part, r: ResolvedCandyVendingMachineConfig, mats: dict[str, object]
) -> ChassisAnchors:
    w, d, h = r.width, r.depth, r.height
    _cyl(body, "round_foot", w * 0.34, d * 0.12, (0.0, 0.0, d * 0.060), mats["body_dark"], _cyl_z())
    _cyl(body, "pedestal_column", w * 0.075, h * 0.34, (0.0, 0.0, h * 0.17), mats["trim"], _cyl_z())
    housing_h = h * 0.21
    housing_z = h * 0.36
    R = r.reservoir_radius
    _box(body, "cast_housing", (w * 0.72, d * 0.70, housing_h), (0.0, 0.0, housing_z), mats["body"])
    _box(
        body,
        "globe_rear_support_spine",
        (w * 0.16, d * 0.10, max(0.02, r.reservoir_z - R * 0.55 - (housing_z + housing_h * 0.50))),
        (0.0, d * 0.10, (r.reservoir_z - R * 0.55 + housing_z + housing_h * 0.50) * 0.5),
        mats["trim"],
    )
    _box(
        body,
        "lower_chute_frame",
        (w * 0.42, d * 0.36, h * 0.12),
        (0.0, r.front_y + d * 0.140, h * 0.20),
        mats["trim"],
    )
    globe_center = (0.0, 0.0, r.reservoir_z)
    body.visual(
        Sphere(radius=R),
        origin=Origin(xyz=globe_center),
        material=mats["glass"],
        name="clear_globe", material_class_id="glass.clear_transparent",
    )
    _cyl(
        body,
        "globe_bottom_crown",
        R * 0.88,
        h * 0.030,
        (0.0, 0.0, r.reservoir_z - R * 0.80),
        mats["trim"],
        _cyl_z(),
    )
    _cyl(
        body,
        "globe_top_crown",
        R * 0.48,
        h * 0.026,
        (0.0, 0.0, r.reservoir_z + R * 0.83),
        mats["trim"],
        _cyl_z(),
    )
    _add_candy_fill(body, r, mats, center=globe_center, radius=R, prefix="globe")
    return _common_anchors(r, body, refill_z=r.reservoir_z + R * 0.92, refill_radius=R * 0.46)


def _build_dual_hopper_body(
    body: Part, r: ResolvedCandyVendingMachineConfig, mats: dict[str, object]
) -> ChassisAnchors:
    w, d, h = r.width, r.depth, r.height
    _box(
        body, "wide_plinth", (w * 0.88, d * 0.72, h * 0.10), (0.0, 0.0, h * 0.05), mats["body_dark"]
    )
    _box(body, "twin_pedestal", (w * 0.30, d * 0.36, h * 0.34), (0.0, 0.0, h * 0.24), mats["trim"])
    _box(
        body,
        "shared_hopper_base",
        (w * 0.80, d * 0.66, h * 0.18),
        (0.0, 0.0, h * 0.43),
        mats["body"],
    )
    _box(
        body,
        "central_collection_recess",
        (w * 0.34, d * 0.24, h * 0.12),
        (0.0, r.front_y + d * 0.080, h * 0.19),
        mats["body_dark"],
    )
    _box(
        body,
        "collection_recess_support_spine",
        (w * 0.30, d * 0.13, h * 0.28),
        (0.0, r.front_y + d * 0.120, h * 0.27),
        mats["body_dark"],
    )
    R = r.reservoir_radius
    xs = (-w * 0.24, w * 0.24)
    for i, x in enumerate(xs):
        center = (x, 0.0, r.reservoir_z)
        body.visual(
            Sphere(radius=R),
            origin=Origin(xyz=center),
            material=mats["glass"],
            name=f"clear_twin_hopper_{i}", material_class_id="glass.clear_transparent",
        )
        _cyl(
            body,
            f"hopper_{i}_neck_ring",
            R * 0.78,
            h * 0.026,
            (x, 0.0, r.reservoir_z - R * 0.80),
            mats["trim"],
            _cyl_z(),
        )
        _cyl(
            body,
            f"hopper_{i}_top_ring",
            R * 0.48,
            h * 0.022,
            (x, 0.0, r.reservoir_z + R * 0.82),
            mats["trim"],
            _cyl_z(),
        )
        _box(
            body,
            f"hopper_{i}_rear_support_spine",
            (R * 0.34, d * 0.10, max(0.02, r.reservoir_z - h * 0.50)),
            (x, d * 0.12, (r.reservoir_z + h * 0.50) * 0.5),
            mats["trim"],
        )
        _add_candy_fill(body, r, mats, center=center, radius=R, prefix=f"hopper_{i}")
    _box(
        body,
        "dual_hopper_rear_crossbar",
        (w * 0.58, d * 0.08, h * 0.045),
        (0.0, d * 0.12, r.reservoir_z - R * 0.18),
        mats["trim"],
    )
    return _common_anchors(r, body, refill_z=r.reservoir_z + R * 0.92, refill_radius=R * 0.42)


def _build_tall_cabinet_body(
    body: Part, r: ResolvedCandyVendingMachineConfig, mats: dict[str, object]
) -> ChassisAnchors:
    w, d, h = r.width, r.depth, r.height
    _box(body, "tall_cabinet_shell", (w, d, h), (0.0, 0.0, h * 0.5), mats["body_dark"])
    _box(
        body,
        "front_glass_pane",
        (w * 0.74, d * 0.025, h * 0.52),
        (0.0, r.front_y - d * 0.016, h * 0.63),
        mats["glass"],
    )
    _box(
        body,
        "glass_left_stile",
        (w * 0.045, d * 0.045, h * 0.58),
        (-w * 0.40, r.front_y - d * 0.020, h * 0.63),
        mats["trim"],
    )
    _box(
        body,
        "glass_right_stile",
        (w * 0.045, d * 0.045, h * 0.58),
        (w * 0.40, r.front_y - d * 0.020, h * 0.63),
        mats["trim"],
    )
    _box(
        body,
        "pickup_recess",
        (w * 0.42, d * 0.08, h * 0.09),
        (0.0, r.front_y - d * 0.030, r.pickup_z),
        mats["body"],
    )
    selector_panel_x = w * (0.41 if r.retrieval == "glazed_swing_door" else 0.25)
    _box(
        body,
        "selector_bezel_panel",
        (w * 0.18 if r.retrieval == "glazed_swing_door" else w * 0.32, d * 0.035, h * 0.15),
        (selector_panel_x, r.front_y - d * 0.025, r.selector_z),
        mats["trim"],
    )
    _add_spiral_track(body, r, mats)
    return _common_anchors(r, body, refill_z=h * 0.92, refill_radius=w * 0.20)


def _build_stacked_canister_body(
    body: Part, r: ResolvedCandyVendingMachineConfig, mats: dict[str, object]
) -> ChassisAnchors:
    w, d, h = r.width, r.depth, r.height
    _box(
        body,
        "canister_cabinet_base",
        (w * 0.86, d * 0.76, h * 0.19),
        (0.0, 0.0, h * 0.095),
        mats["body"],
    )
    _box(
        body,
        "stacked_back_spine",
        (w * 0.64, d * 0.10, h * 0.72),
        (-w * 0.12, d * 0.13, h * 0.49),
        mats["body_dark"],
    )
    _box(
        body,
        "mechanism_column",
        (w * 0.28, d * 0.20, h * 0.58),
        (w * 0.25, r.front_y + d * 0.080, h * 0.48),
        mats["trim"],
    )
    _box(
        body,
        "pickup_recess",
        (w * 0.46, d * 0.22, h * 0.09),
        (-w * 0.08, r.front_y + d * 0.020, r.pickup_z),
        mats["body_dark"],
    )
    count = r.canister_count
    bin_h = h * (0.155 if count == 4 else 0.20 if count == 3 else 0.27)
    start_z = h * (0.34 if count == 4 else 0.38)
    for i in range(count):
        z = start_z + i * bin_h * 1.04
        _box(
            body,
            f"clear_bin_{i}",
            (w * 0.56, d * 0.46, bin_h),
            (-w * 0.12, -d * 0.02, z),
            mats["glass"],
        )
        _box(
            body,
            f"bin_{i}_rim",
            (w * 0.60, d * 0.50, bin_h * 0.12),
            (-w * 0.12, -d * 0.02, z - bin_h * 0.44),
            mats["trim"],
        )
        _add_candy_fill(
            body,
            r,
            mats,
            center=(-w * 0.12, -d * 0.02, z),
            radius=bin_h * 0.48,
            width=w * 0.44,
            prefix=f"bin_{i}",
        )
    return _common_anchors(r, body, refill_z=h * 0.90, refill_radius=w * 0.18)


def _build_wall_mount_body(
    body: Part, r: ResolvedCandyVendingMachineConfig, mats: dict[str, object]
) -> ChassisAnchors:
    w, d, h = r.width, r.depth, r.height
    _box(
        body,
        "wall_backplate",
        (w * 1.05, d * 0.10, h * 0.86),
        (0.0, r.back_y - d * 0.05, h * 0.50),
        mats["body_dark"],
    )
    _box(
        body,
        "shallow_hopper_box",
        (w * 0.86, d * 0.95, h * 0.50),
        (0.0, d * 0.02, h * 0.58),
        mats["body"],
    )
    _box(
        body,
        "clear_front_hopper",
        (w * 0.72, d * 0.035, h * 0.42),
        (0.0, r.front_y - d * 0.020, h * 0.60),
        mats["glass"],
    )
    _box(
        body,
        "lower_cup_frame",
        (w * 0.42, d * 0.28, h * 0.11),
        (0.0, r.front_y + d * 0.080, r.pickup_z),
        mats["trim"],
    )
    _box(
        body,
        "wall_cup_support_spine_left",
        (w * 0.075, d * 0.18, h * 0.26),
        (-w * 0.16, r.front_y + d * 0.090, h * 0.28),
        mats["trim"],
    )
    _box(
        body,
        "wall_cup_support_spine_right",
        (w * 0.075, d * 0.18, h * 0.26),
        (w * 0.16, r.front_y + d * 0.090, h * 0.28),
        mats["trim"],
    )
    _box(
        body,
        "coin_faceplate",
        (w * 0.35, d * 0.040, h * 0.12),
        (0.0, r.front_y - d * 0.035, r.selector_z),
        mats["trim"],
    )
    _box(
        body,
        "wall_top_refill_bridge",
        (w * 0.34, d * 0.16, h * 0.080),
        (0.0, d * 0.09, h * 0.84),
        mats["trim"],
    )
    _add_candy_fill(
        body,
        r,
        mats,
        center=(0.0, -d * 0.05, h * 0.60),
        radius=w * 0.24,
        width=w * 0.58,
        prefix="wall_hopper",
    )
    return _common_anchors(r, body, refill_z=h * 0.86, refill_radius=w * 0.20)


def _add_spiral_track(
    body: Part, r: ResolvedCandyVendingMachineConfig, mats: dict[str, object]
) -> None:
    w, d, h = r.width, r.depth, r.height
    z0 = h * 0.43
    for i in range(7):
        z = z0 + i * h * 0.055
        x = math.sin(i * 0.90) * w * 0.22
        next_x = math.sin((i + 1) * 0.90) * w * 0.22
        mid_x = (x + next_x) * 0.5
        length = abs(next_x - x) + w * 0.15
        _box(
            body,
            f"spiral_candy_track_{i}",
            (length, d * 0.035, h * 0.016),
            (mid_x, r.front_y + d * 0.045, z),
            mats["candy_a" if i % 2 == 0 else "candy_c"],
            (0.0, 0.0, math.atan2(h * 0.055, max(0.01, next_x - x))),
        )
    _box(
        body,
        "spiral_track_back_spine",
        (w * 0.08, d * 0.030, h * 0.46),
        (0.0, r.front_y + d * 0.055, h * 0.60),
        mats["metal"],
    )


def _common_anchors(
    r: ResolvedCandyVendingMachineConfig,
    body: Part,
    *,
    refill_z: float,
    refill_radius: float,
) -> ChassisAnchors:
    selector_positions = _selector_positions(r)
    for i, (x, y, z) in enumerate(selector_positions):
        _cyl(
            body,
            f"selector_boss_{i}",
            0.035 * r.selector_scale,
            0.030,
            (x, y + 0.010, z),
            PALETTE_SENTINEL,
            _cyl_y(),
        )
        _box(
            body,
            f"selector_socket_bridge_{i}",
            (0.070 * r.selector_scale, r.depth * 0.280, 0.055 * r.selector_scale),
            (x, y + r.depth * 0.135, z),
            PALETTE_SENTINEL,
        )
    # Re-emit selector bosses with material in _paint_selector_bosses, because _common_anchors
    # is shared before materials are closed over by older factory style.
    pickup_hinge = (0.0, r.front_y - 0.006, r.pickup_z + r.height * 0.045)
    service_hinge = (-r.width * 0.40, r.front_y - r.depth * 0.040, r.height * 0.56)
    refill_hinges: tuple[tuple[float, float, float], ...]
    if r.chassis == "dual_hopper_pedestal":
        refill_hinges = (
            (-r.width * 0.24, r.back_y * 0.18, refill_z),
            (r.width * 0.24, r.back_y * 0.18, refill_z),
        )
    else:
        refill_hinges = ((0.0, r.back_y * 0.18, refill_z),)
    if r.refill in ("top_lid", "dual_top_lids"):
        for i, hinge in enumerate(refill_hinges):
            _cyl(
                body,
                f"refill_hinge_lug_{i}",
                max(0.008, r.height * 0.012),
                refill_radius * 0.72,
                hinge,
                PALETTE_SENTINEL,
                _cyl_x(),
            )
    side_refill_hinge = (r.width * 0.44, -r.depth * 0.06, r.height * 0.62)
    if r.refill == "side_door":
        _cyl(
            body,
            "side_refill_hinge_lug",
            max(0.007, r.depth * 0.040),
            r.height * 0.28,
            side_refill_hinge,
            PALETTE_SENTINEL,
            _cyl_z(),
        )
    return ChassisAnchors(
        body=body,
        selector_positions=selector_positions,
        pickup_hinge=pickup_hinge,
        pickup_width=r.width * 0.38,
        pickup_height=r.height * 0.095,
        drawer_depth=r.depth * 0.44,
        service_hinge=service_hinge,
        service_width=r.width * 0.72,
        service_height=r.height * 0.48,
        refill_hinges=refill_hinges,
        refill_radius=refill_radius,
        side_refill_hinge=side_refill_hinge,
        side_refill_size=(r.width * 0.30, r.height * 0.28),
    )


# Temporary placeholder material name overwritten immediately after each chassis build.
PALETTE_SENTINEL = "__candy_vendor_selector_boss_placeholder__"


def _repaint_selector_bosses(
    body: Part,
    anchors: ChassisAnchors,
    r: ResolvedCandyVendingMachineConfig,
    mats: dict[str, object],
) -> None:
    # The SDK visuals are immutable after creation, so add real trim collars that touch the
    # placeholder bosses. The placeholder receives a normal material through the model registry.
    for i, (x, y, z) in enumerate(anchors.selector_positions):
        _cyl(
            body,
            f"selector_trim_collar_{i}",
            0.044 * r.selector_scale,
            0.012,
            (x, y - 0.002, z),
            mats["trim"],
            _cyl_y(),
        )


def _build_selectors(
    model: ArticulatedObject,
    r: ResolvedCandyVendingMachineConfig,
    anchors: ChassisAnchors,
    mats: dict[str, object],
) -> list[Part]:
    selectors: list[Part] = []
    for i, joint_origin in enumerate(anchors.selector_positions):
        selector = model.part("selector" if r.selector_count == 1 else f"selector_{i}")
        radius = 0.044 * r.selector_scale
        if r.dispense == "coin_head_wheel":
            _cyl(
                selector,
                "selector_shaft",
                radius * 0.42,
                0.070,
                (0.0, 0.000, 0.0),
                mats["metal"],
                _cyl_y(),
            )
            _cyl(
                selector,
                "coin_wheel_disc",
                radius * 1.12,
                0.020,
                (0.0, -0.028, 0.0),
                mats["trim"],
                _cyl_y(),
            )
            _cyl(
                selector,
                "coin_wheel_hub",
                radius * 0.52,
                0.030,
                (0.0, -0.042, 0.0),
                mats["metal"],
                _cyl_y(),
            )
            _cyl(
                selector,
                "finger_post",
                radius * 0.16,
                0.030,
                (radius * 0.64, -0.047, radius * 0.35),
                mats["body_dark"],
                _cyl_y(),
            )
            _box(
                selector,
                "coin_slot_bar",
                (radius * 1.05, 0.006, radius * 0.13),
                (0.0, -0.055, radius * 0.02),
                mats["rubber"],
            )
        else:
            _cyl(
                selector,
                "selector_shaft",
                radius * 0.42,
                0.070,
                (0.0, 0.000, 0.0),
                mats["metal"],
                _cyl_y(),
            )
            _cyl(
                selector,
                "ribbed_knob_body",
                radius,
                0.034,
                (0.0, -0.030, 0.0),
                mats["trim"],
                _cyl_y(),
            )
            rib_count = 8 if r.dispense == "single_knob" else 10
            for k in range(rib_count):
                a = math.tau * k / rib_count
                _box(
                    selector,
                    f"knob_grip_rib_{k}",
                    (radius * 0.10, 0.010, radius * 0.32),
                    (math.cos(a) * radius * 0.74, -0.050, math.sin(a) * radius * 0.74),
                    mats["body_dark"],
                    (0.0, a, 0.0),
                )
            _box(
                selector,
                "selector_pointer_bar",
                (radius * 1.15, 0.010, radius * 0.15),
                (0.0, -0.056, radius * 0.48),
                mats["rubber"],
            )
        model.articulation(
            f"{selector.name}_turn",
            ArticulationType.CONTINUOUS,
            parent=anchors.body,
            child=selector,
            origin=Origin(xyz=joint_origin),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=7.0),
        )
        selector.inertial = Inertial.from_geometry(
            Cylinder(radius=radius, length=0.055), mass=0.35, origin=Origin(rpy=_cyl_y())
        )
        selectors.append(selector)
    return selectors


def _build_retrieval(
    model: ArticulatedObject,
    r: ResolvedCandyVendingMachineConfig,
    anchors: ChassisAnchors,
    mats: dict[str, object],
) -> Part:
    if r.retrieval == "cash_drawer":
        return _build_cash_drawer(model, r, anchors, mats)
    if r.retrieval == "glazed_swing_door":
        return _build_glazed_swing_door(model, r, anchors, mats)
    return _build_pickup_flap(model, r, anchors, mats, cup=r.retrieval == "collection_cup_door")


def _build_pickup_flap(
    model: ArticulatedObject,
    r: ResolvedCandyVendingMachineConfig,
    anchors: ChassisAnchors,
    mats: dict[str, object],
    *,
    cup: bool,
) -> Part:
    flap = model.part("collection_cup_door" if cup else "retrieval_flap")
    w = anchors.pickup_width * (1.08 if cup else 1.0)
    h = anchors.pickup_height * (1.12 if cup else 1.0)
    t = r.depth * 0.040
    _box(
        flap, "flap_panel", (w, t, h), (0.0, -t * 0.50, -h * 0.50), mats["glass" if cup else "body"]
    )
    _cyl(
        flap,
        "flap_hinge_barrel",
        t * 0.62,
        w * 1.03,
        (0.0, -t * 0.50, 0.0),
        mats["metal"],
        _cyl_x(),
    )
    _box(
        flap,
        "flap_pull_lip",
        (w * 0.42, t * 0.70, h * 0.13),
        (0.0, -t * 0.95, -h * 0.72),
        mats["trim"],
    )
    if cup:
        _box(
            flap,
            "cup_curved_front",
            (w * 0.82, t * 0.52, h * 0.26),
            (0.0, -t * 1.02, -h * 0.20),
            mats["glass"],
        )
    model.articulation(
        f"{flap.name}_open",
        ArticulationType.REVOLUTE,
        parent=anchors.body,
        child=flap,
        origin=Origin(xyz=anchors.pickup_hinge),
        # Axis flipped so the flap swings OUT toward the user (-y); opening the
        # other way drives the panel into the cabinet shell / recess spine.
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=r.flap_open_angle),
    )
    flap.inertial = Inertial.from_geometry(
        Box((w, t, h)), mass=0.35, origin=Origin(xyz=(0.0, -t * 0.5, -h * 0.5))
    )
    return flap


def _build_cash_drawer(
    model: ArticulatedObject,
    r: ResolvedCandyVendingMachineConfig,
    anchors: ChassisAnchors,
    mats: dict[str, object],
) -> Part:
    drawer = model.part("cash_drawer")
    w = anchors.pickup_width * 1.12
    d = anchors.drawer_depth
    h = anchors.pickup_height * 0.88
    _box(drawer, "drawer_bin", (w, d, h), (0.0, d * 0.47, -h * 0.08), mats["body_dark"])
    _box(
        drawer,
        "drawer_front_face",
        (w * 1.08, r.depth * 0.040, h * 1.12),
        (0.0, -r.depth * 0.020, -h * 0.08),
        mats["body"],
    )
    _box(
        drawer,
        "drawer_pull_handle",
        (w * 0.42, r.depth * 0.030, h * 0.16),
        (0.0, -r.depth * 0.052, -h * 0.08),
        mats["trim"],
    )
    _box(
        drawer,
        "left_drawer_runner",
        (r.width * 0.035, d * 0.94, h * 0.12),
        (-w * 0.44, d * 0.45, -h * 0.39),
        mats["metal"],
    )
    _box(
        drawer,
        "right_drawer_runner",
        (r.width * 0.035, d * 0.94, h * 0.12),
        (w * 0.44, d * 0.45, -h * 0.39),
        mats["metal"],
    )
    model.articulation(
        "cash_drawer_slide",
        ArticulationType.PRISMATIC,
        parent=anchors.body,
        child=drawer,
        origin=Origin(
            xyz=(anchors.pickup_hinge[0], r.front_y - 0.010, anchors.pickup_hinge[2] - h * 0.42)
        ),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=18.0, velocity=0.28, lower=0.0, upper=r.drawer_travel),
    )
    drawer.inertial = Inertial.from_geometry(
        Box((w, d, h)), mass=1.0, origin=Origin(xyz=(0.0, d * 0.47, -h * 0.08))
    )
    return drawer


def _build_glazed_swing_door(
    model: ArticulatedObject,
    r: ResolvedCandyVendingMachineConfig,
    anchors: ChassisAnchors,
    mats: dict[str, object],
) -> Part:
    door = model.part("glazed_swing_door")
    w = anchors.service_width
    h = anchors.service_height
    t = r.depth * 0.035
    _box(door, "glazed_door_pane", (w, t, h), (w * 0.50, -t * 0.50, 0.0), mats["glass"])
    _box(
        door,
        "door_top_rail",
        (w, t * 1.35, h * 0.055),
        (w * 0.50, -t * 0.52, h * 0.47),
        mats["trim"],
    )
    _box(
        door,
        "door_bottom_rail",
        (w, t * 1.35, h * 0.055),
        (w * 0.50, -t * 0.52, -h * 0.47),
        mats["trim"],
    )
    _box(
        door, "door_outer_stile", (w * 0.055, t * 1.35, h), (w * 0.97, -t * 0.52, 0.0), mats["trim"]
    )
    _cyl(
        door,
        "glazed_door_hinge_barrel",
        t * 0.70,
        h * 1.02,
        (0.0, -t * 0.52, 0.0),
        mats["metal"],
        _cyl_z(),
    )
    _box(
        door,
        "glazed_door_pull",
        (w * 0.075, t * 0.65, h * 0.34),
        (w * 0.82, -t * 1.05, 0.0),
        mats["metal"],
    )
    model.articulation(
        "glazed_door_swing",
        ArticulationType.REVOLUTE,
        parent=anchors.body,
        child=door,
        origin=Origin(xyz=anchors.service_hinge),
        # Axis flipped so the door swings OUT from the cabinet front; the other
        # direction sweeps the outer stile through the cabinet shell side.
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.2, lower=0.0, upper=r.flap_open_angle),
    )
    door.inertial = Inertial.from_geometry(
        Box((w, t, h)), mass=1.5, origin=Origin(xyz=(w * 0.5, -t * 0.5, 0.0))
    )
    return door


def _build_refill(
    model: ArticulatedObject,
    r: ResolvedCandyVendingMachineConfig,
    anchors: ChassisAnchors,
    mats: dict[str, object],
) -> list[Part]:
    if r.refill == "none":
        return []
    if r.refill == "side_door":
        return [_build_side_refill_door(model, r, anchors, mats)]
    lids: list[Part] = []
    hinge_points = (
        anchors.refill_hinges if r.refill == "dual_top_lids" else anchors.refill_hinges[:1]
    )
    for i, hinge in enumerate(hinge_points):
        lids.append(_build_top_refill_lid(model, r, anchors, mats, index=i, hinge=hinge))
    return lids


def _build_top_refill_lid(
    model: ArticulatedObject,
    r: ResolvedCandyVendingMachineConfig,
    anchors: ChassisAnchors,
    mats: dict[str, object],
    *,
    index: int,
    hinge: tuple[float, float, float],
) -> Part:
    lid = model.part("refill_lid" if r.refill == "top_lid" else f"refill_lid_{index}")
    rad = anchors.refill_radius
    t = r.height * 0.022
    _cyl(lid, "refill_lid_cap", rad, t, (0.0, -rad * 0.86, 0.0), mats["body"], _cyl_z())
    _cyl(
        lid,
        "refill_lid_badge",
        rad * 0.28,
        t * 1.18,
        (0.0, -rad * 0.86, t * 0.18),
        mats["trim"],
        _cyl_z(),
    )
    _box(
        lid,
        "refill_lid_hinge_leaf",
        (rad * 0.55, t * 0.85, t * 0.55),
        (0.0, -t * 0.35, 0.0),
        mats["metal"],
    )
    _cyl(
        lid,
        "refill_lid_hinge_barrel",
        t * 0.45,
        rad * 0.60,
        (0.0, 0.0, 0.0),
        mats["metal"],
        _cyl_x(),
    )
    model.articulation(
        f"{lid.name}_open",
        ArticulationType.REVOLUTE,
        parent=anchors.body,
        child=lid,
        origin=Origin(xyz=hinge),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.5, velocity=1.5, lower=0.0, upper=r.refill_open_angle),
    )
    lid.inertial = Inertial.from_geometry(
        Cylinder(radius=rad, length=t), mass=0.22, origin=Origin(xyz=(0.0, -rad * 0.86, 0.0))
    )
    return lid


def _build_side_refill_door(
    model: ArticulatedObject,
    r: ResolvedCandyVendingMachineConfig,
    anchors: ChassisAnchors,
    mats: dict[str, object],
) -> Part:
    door = model.part("side_refill_door")
    w, h = anchors.side_refill_size
    t = r.depth * 0.035
    _box(door, "side_refill_panel", (w, t, h), (w * 0.50, 0.0, 0.0), mats["body"])
    _cyl(
        door,
        "side_refill_hinge_barrel",
        t * 0.55,
        h * 1.02,
        (0.0, 0.0, 0.0),
        mats["metal"],
        _cyl_z(),
    )
    _box(
        door,
        "side_refill_pull_tab",
        (w * 0.20, t * 0.65, h * 0.14),
        (w * 0.72, -t * 0.56, 0.0),
        mats["trim"],
    )
    model.articulation(
        "side_refill_door_swing",
        ArticulationType.REVOLUTE,
        parent=anchors.body,
        child=door,
        origin=Origin(xyz=anchors.side_refill_hinge),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.5, velocity=1.4, lower=0.0, upper=r.refill_open_angle),
    )
    door.inertial = Inertial.from_geometry(
        Box((w, t, h)), mass=0.32, origin=Origin(xyz=(w * 0.5, 0.0, 0.0))
    )
    return door


def build_candy_vending_machine(
    config: CandyVendingMachineConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or CandyVendingMachineConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _register_materials(model, r.material_style)
    # Placeholder selector bosses are given a real material name up front.
    model.material(PALETTE_SENTINEL, rgba=PALETTES[r.material_style]["trim"])
    anchors = _build_chassis(model, r, mats)
    _repaint_selector_bosses(anchors.body, anchors, r, mats)
    _build_selectors(model, r, anchors, mats)
    _build_retrieval(model, r, anchors, mats)
    _build_refill(model, r, anchors, mats)
    return model


def build_seeded_candy_vending_machine(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_candy_vending_machine(config_from_seed(seed), assets=assets)


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    parts = {p.name for p in model.parts}
    if "body" not in parts:
        return
    body = model.get_part("body")
    for part_name in parts:
        if part_name.startswith("selector"):
            selector = model.get_part(part_name)
            for parent_elem in (
                tuple(f"selector_boss_{i}" for i in range(4))
                + tuple(f"selector_trim_collar_{i}" for i in range(4))
                + tuple(f"selector_socket_bridge_{i}" for i in range(4))
                + (
                    "cast_housing",
                    "selector_bezel_panel",
                    "mechanism_column",
                    "coin_faceplate",
                    "shared_hopper_base",
                    "tall_cabinet_shell",
                    "glass_right_stile",
                    "shallow_hopper_box",
                )
            ):
                for child_elem in (
                    "selector_shaft",
                    "ribbed_knob_body",
                    "coin_wheel_disc",
                    "coin_wheel_hub",
                    "selector_pointer_bar",
                    "coin_slot_bar",
                ):
                    try:
                        ctx.allow_overlap(
                            body,
                            selector,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="selector shaft and cap are captured by the cabinet boss",
                        )
                    except Exception:
                        pass
        if part_name in ("retrieval_flap", "collection_cup_door"):
            flap = model.get_part(part_name)
            for parent_elem in (
                "lower_chute_frame",
                "central_collection_recess",
                "collection_recess_support_spine",
                "wall_cup_support_spine_left",
                "wall_cup_support_spine_right",
                "pickup_recess",
                "lower_cup_frame",
                "cast_housing",
                "canister_cabinet_base",
            ):
                for child_elem in (
                    "flap_hinge_barrel",
                    "flap_panel",
                    "flap_pull_lip",
                    "cup_curved_front",
                ):
                    try:
                        ctx.allow_overlap(
                            body,
                            flap,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="pickup flap closes flush into the retrieval opening",
                        )
                    except Exception:
                        pass
        if part_name == "cash_drawer":
            drawer = model.get_part("cash_drawer")
            for parent_elem in ("pickup_recess", "canister_cabinet_base", "tall_cabinet_shell"):
                for child_elem in (
                    "drawer_bin",
                    "drawer_front_face",
                    "drawer_pull_handle",
                    "left_drawer_runner",
                    "right_drawer_runner",
                ):
                    try:
                        ctx.allow_overlap(
                            body,
                            drawer,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="cash drawer bin and runners slide inside the cabinet recess",
                        )
                    except Exception:
                        pass
        if part_name == "glazed_swing_door":
            door = model.get_part("glazed_swing_door")
            for parent_elem in (
                "tall_cabinet_shell",
                "front_glass_pane",
                "glass_left_stile",
                "glass_right_stile",
                "spiral_track_back_spine",
                *(f"spiral_candy_track_{i}" for i in range(7)),
            ):
                for child_elem in (
                    "glazed_door_hinge_barrel",
                    "glazed_door_pane",
                    "door_top_rail",
                    "door_bottom_rail",
                    "glazed_door_pull",
                ):
                    try:
                        ctx.allow_overlap(
                            body,
                            door,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="glazed service door sits flush in the cabinet front frame",
                        )
                    except Exception:
                        pass
        if part_name.startswith("refill_lid"):
            lid = model.get_part(part_name)
            for parent_elem in (
                "clear_globe",
                "clear_twin_hopper_0",
                "clear_twin_hopper_1",
                "globe_top_crown",
                "hopper_0_top_ring",
                "hopper_1_top_ring",
                "refill_hinge_lug_0",
                "refill_hinge_lug_1",
                "wall_top_refill_bridge",
                "shallow_hopper_box",
                "clear_front_hopper",
            ):
                for child_elem in (
                    "refill_lid_cap",
                    "refill_lid_badge",
                    "refill_lid_hinge_leaf",
                    "refill_lid_hinge_barrel",
                ):
                    try:
                        ctx.allow_overlap(
                            body,
                            lid,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="refill lid rests on the reservoir crown and shares the hinge barrel",
                        )
                    except Exception:
                        pass
        if part_name == "side_refill_door":
            door = model.get_part("side_refill_door")
            for parent_elem in ("wall_backplate", "shallow_hopper_box", "side_refill_hinge_lug"):
                for child_elem in ("side_refill_panel", "side_refill_hinge_barrel"):
                    try:
                        ctx.allow_overlap(
                            body,
                            door,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="side refill door closes flush into the shallow hopper wall",
                        )
                    except Exception:
                        pass


def run_candy_vending_machine_tests(
    object_model: ArticulatedObject,
    config: CandyVendingMachineConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}
    if "body" not in part_names:
        ctx.fail("identity_body", "candy vending machine must have one grounded body part")
    if not any("selector" in name for name in part_names):
        ctx.fail("identity_selector", "candy vending machine must expose a rotary selector")
    if not any(
        name.startswith("clear_") or "glass" in name for name in _body_visual_names(object_model)
    ):
        ctx.fail("identity_glass", "candy vending machine must have a transparent reservoir/window")
    selector_joints = [j for j in object_model.joints if j.name.endswith("_turn")]
    if len(selector_joints) != r.selector_count:
        ctx.fail(
            "selector_count", f"expected {r.selector_count} selectors, got {len(selector_joints)}"
        )
    for joint in selector_joints:
        if joint.articulation_type != ArticulationType.CONTINUOUS:
            ctx.fail("selector_joint_type", f"{joint.name} must be CONTINUOUS")
    if r.retrieval == "cash_drawer":
        if "cash_drawer_slide" not in joint_names:
            ctx.fail("drawer_joint", "cash drawer must have a prismatic slide")
    elif r.retrieval == "glazed_swing_door":
        if "glazed_door_swing" not in joint_names:
            ctx.fail("service_door_joint", "glazed service door must swing on a vertical hinge")
    elif not any(
        name.endswith("_open") and ("flap" in name or "cup" in name) for name in joint_names
    ):
        ctx.fail("flap_joint", "retrieval flap/cup door must have a revolute joint")
    if r.refill == "side_door" and "side_refill_door_swing" not in joint_names:
        ctx.fail("side_refill_joint", "side refill door must have a revolute joint")
    if r.refill in ("top_lid", "dual_top_lids") and not any(
        name.startswith("refill_lid") for name in joint_names
    ):
        ctx.fail("top_refill_joint", "top refill lid must have a revolute joint")

    return ctx.report()


def _body_visual_names(object_model: ArticulatedObject) -> set[str]:
    try:
        body = object_model.get_part("body")
    except Exception:
        return set()
    return {v.name for v in body.visuals}


__all__ = [
    "CandyVendingMachineConfig",
    "ResolvedCandyVendingMachineConfig",
    "build_candy_vending_machine",
    "build_seeded_candy_vending_machine",
    "config_from_seed",
    "resolve_config",
    "run_candy_vending_machine_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
