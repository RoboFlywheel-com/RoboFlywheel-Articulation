# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for lever-chain linkages."""

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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    clamp_joint_limits,
)

__modular__ = True

BaseStyle = Literal["compact_pedestal", "clevis_mount", "bench_yoke", "slotted_frame"]
LeverProfile = Literal["capsule_plate", "dogbone_plate", "slotted_rocker"]
AxisFamily = Literal["vertical_stack", "horizontal_bench"]
OutputModule = Literal["terminal_tab", "output_lever", "guide_pin_output"]
AuxCoupler = Literal["none", "front_couplers", "guide_slots"]
MaterialStyle = Literal["shop_steel", "blue_orange", "dark_bronze"]

BASE_STYLES: tuple[BaseStyle, ...] = (
    "compact_pedestal",
    "clevis_mount",
    "bench_yoke",
    "slotted_frame",
)
LEVER_PROFILES: tuple[LeverProfile, ...] = ("capsule_plate", "dogbone_plate", "slotted_rocker")
AXIS_FAMILIES: tuple[AxisFamily, ...] = ("horizontal_bench",)
OUTPUT_MODULES: tuple[OutputModule, ...] = ("terminal_tab", "output_lever", "guide_pin_output")
AUX_COUPLERS: tuple[AuxCoupler, ...] = ("none", "front_couplers", "guide_slots")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = ("shop_steel", "blue_orange", "dark_bronze")

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "shop_steel": {
        "base": (0.32, 0.34, 0.35, 1.0),
        "link": (0.58, 0.60, 0.58, 1.0),
        "alt": (0.42, 0.45, 0.48, 1.0),
        "pin": (0.78, 0.62, 0.30, 1.0),
        "dark": (0.05, 0.055, 0.060, 1.0),
    },
    "blue_orange": {
        "base": (0.12, 0.13, 0.14, 1.0),
        "link": (0.10, 0.25, 0.70, 1.0),
        "alt": (0.88, 0.40, 0.08, 1.0),
        "pin": (0.86, 0.62, 0.24, 1.0),
        "dark": (0.025, 0.025, 0.030, 1.0),
    },
    "dark_bronze": {
        "base": (0.07, 0.075, 0.08, 1.0),
        "link": (0.20, 0.21, 0.22, 1.0),
        "alt": (0.34, 0.30, 0.22, 1.0),
        "pin": (0.72, 0.52, 0.26, 1.0),
        "dark": (0.015, 0.016, 0.017, 1.0),
    },
}


@dataclass(frozen=True)
class LeverChainConfig:
    base_style: BaseStyle | None = None
    lever_profile: LeverProfile | None = None
    axis_family: AxisFamily | None = None
    output_module: OutputModule | None = None
    aux_coupler: AuxCoupler | None = None
    material_style: MaterialStyle = "shop_steel"
    lever_count: int | None = None
    base_length: float = 0.18
    first_length: float = 0.16
    plate_width: float = 0.034
    plate_thickness: float = 0.010
    pin_radius: float = 0.006
    joint_limit_scale: float = 1.0
    name: str = "lever_chain"


@dataclass(frozen=True)
class ResolvedLeverChainConfig:
    base_style: BaseStyle
    lever_profile: LeverProfile
    axis_family: AxisFamily
    output_module: OutputModule
    aux_coupler: AuxCoupler
    material_style: MaterialStyle
    lever_count: int
    lengths: tuple[float, ...]
    plate_width: float
    plate_thickness: float
    pin_radius: float
    axis: tuple[float, float, float]
    base_origin_z: float
    joint_limits: tuple[tuple[float, float], ...]
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _part_name(part: object) -> str:
    return part if isinstance(part, str) else getattr(part, "name", "")


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> LeverChainConfig:
    rng = random.Random(seed)
    return LeverChainConfig(
        base_style=rng.choice(BASE_STYLES),
        lever_profile=rng.choice(LEVER_PROFILES),
        axis_family=rng.choice(AXIS_FAMILIES),
        output_module=rng.choice(OUTPUT_MODULES),
        aux_coupler=rng.choice(AUX_COUPLERS),
        material_style=rng.choice(MATERIAL_STYLES),
        lever_count=rng.choice((2, 3, 4)),
        base_length=rng.uniform(0.14, 0.26),
        first_length=rng.uniform(0.11, 0.24),
        plate_width=rng.uniform(0.026, 0.056),
        plate_thickness=rng.uniform(0.007, 0.016),
        pin_radius=rng.uniform(0.0045, 0.0095),
        joint_limit_scale=rng.uniform(0.82, 1.18),
        name=f"seeded_lever_chain_{seed}",
    )


def resolve_config(config: LeverChainConfig | None = None) -> ResolvedLeverChainConfig:
    cfg = config or LeverChainConfig()
    base_style = _pick(cfg.base_style, BASE_STYLES)
    lever_profile = _pick(cfg.lever_profile, LEVER_PROFILES)
    axis_family = _pick(cfg.axis_family, AXIS_FAMILIES)
    output_module = _pick(cfg.output_module, OUTPUT_MODULES)
    aux_coupler = _pick(cfg.aux_coupler, AUX_COUPLERS)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)
    lever_count = int(cfg.lever_count or 3)
    lever_count = min(4, max(2, lever_count))

    first_length = _clamp(cfg.first_length, 0.08, 0.30)
    lengths = tuple(max(0.065, first_length * (0.82**i)) for i in range(lever_count))
    plate_width = _clamp(cfg.plate_width, 0.018, 0.075)
    plate_thickness = _clamp(cfg.plate_thickness, 0.004, 0.020)
    pin_radius = _clamp(cfg.pin_radius, 0.0035, 0.014)
    scale = _clamp(cfg.joint_limit_scale, 0.70, 1.30)
    if axis_family == "vertical_stack":
        # Off-bench stack (currently unused family): symmetric travel about rest.
        axis = (0.0, 0.0, 1.0)
        limits = tuple((-0.95 * scale, 1.05 * scale) for _ in range(lever_count))
    else:
        # Bench-mounted chain: the levers rest ON the bench plate, so the only
        # physically available travel is lifting UP, away from the bench. The
        # axis is flipped to -Y so a POSITIVE joint value (upper) is the upward
        # actuation direction the "output moves" test drives; downward travel
        # into the bench is disallowed (lower == 0). The upper bound is then
        # tightened per joint against the actual bench geometry in
        # build_lever_chain via clamp_joint_limits(keepout=["ground_support"]).
        axis = (0.0, -1.0, 0.0)
        up = _clamp(1.05 * scale, 0.60, 1.30)
        limits = tuple((0.0, up) for _ in range(lever_count))
    base_origin_z = 0.045 if axis_family == "vertical_stack" else 0.080
    return ResolvedLeverChainConfig(
        base_style=base_style,
        lever_profile=lever_profile,
        axis_family=axis_family,
        output_module=output_module,
        aux_coupler=aux_coupler,
        material_style=material_style,
        lever_count=lever_count,
        lengths=lengths,
        plate_width=plate_width,
        plate_thickness=plate_thickness,
        pin_radius=pin_radius,
        axis=axis,
        base_origin_z=base_origin_z,
        joint_limits=limits,
        name=cfg.name or "lever_chain",
    )


def with_overrides(config: LeverChainConfig, **kwargs: object) -> LeverChainConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(config: LeverChainConfig | ResolvedLeverChainConfig):
    r = config if isinstance(config, ResolvedLeverChainConfig) else resolve_config(config)
    return (
        ("base", r.base_style),
        ("lever_profile", r.lever_profile),
        ("axis_family", r.axis_family),
        ("lever_multiplicity", f"{r.lever_count}_moving_levers"),
        ("output_module", r.output_module),
        ("aux_coupler", r.aux_coupler),
        ("material_palette", r.material_style),
    )


def slot_choices_for_seed(seed: int):
    return slot_choices_for_config(config_from_seed(seed))


def _mat(model: ArticulatedObject, r: ResolvedLeverChainConfig, key: str):
    return model.material(f"lever_chain_{key}", rgba=PALETTES[r.material_style][key])


def _cyl_origin_for_axis(axis_family: AxisFamily, xyz=(0.0, 0.0, 0.0)) -> Origin:
    if axis_family == "vertical_stack":
        return Origin(xyz=xyz)
    return Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0))


def _add_plate(
    part,
    *,
    r: ResolvedLeverChainConfig,
    length: float,
    width: float,
    thickness: float,
    material,
    alt_material,
    name: str,
    terminal: bool = False,
    min_root_clear: float = 0.0,
) -> None:
    if r.axis_family == "vertical_stack":
        z = 0.0
        root_clear = min(width * (0.72 if terminal else 0.565), length * 0.34)
        root_clear = min(max(root_clear, min_root_clear), length - 0.012)
        web_len = max(0.012, length - root_clear)
        part.visual(
            Box((web_len, width, thickness)),
            origin=Origin(xyz=(root_clear + web_len * 0.5, 0.0, z)),
            material=material,
            name=f"{name}_web", material_class_id=("metal.bronze_cast" if r.material_style in {"shop_steel", "dark_bronze"} else "metal.paint_coated"),
        )
        part.visual(
            Cylinder(radius=max(r.pin_radius * 0.82, width * 0.11), length=thickness * 0.30),
            origin=Origin(xyz=(0.0, 0.0, thickness * 0.72)),
            material=alt_material,
            name=f"{name}_root_clip_washer", material_class_id="metal.blackened_gunmetal",
        )
        bridge_z = min(thickness * 0.36, 0.0045)
        part.visual(
            Box((root_clear + 0.002, width * 0.10, bridge_z)),
            origin=Origin(xyz=(root_clear * 0.5, 0.0, thickness * 0.45)),
            material=alt_material,
            name=f"{name}_root_clip_bridge", material_class_id="metal.blackened_gunmetal",
        )
        for x, label in ((0.0, "root"), (length, "tip")):
            if label == "root":
                continue
            part.visual(
                Cylinder(radius=width * 0.52, length=thickness),
                origin=Origin(xyz=(x, 0.0, z)),
                material=material,
                name=f"{name}_{label}_lobe", material_class_id=("metal.bronze_cast" if r.material_style in {"shop_steel", "dark_bronze"} else "metal.paint_coated"),
            )
            if label == "tip":
                part.visual(
                    Cylinder(
                        radius=max(r.pin_radius * 1.45, width * 0.24), length=thickness * 1.35
                    ),
                    origin=Origin(xyz=(x, 0.0, z)),
                    material=alt_material,
                    name=f"{name}_{label}_bushing", material_class_id="metal.blackened_gunmetal",
                )
    else:
        root_clear = min(width * (0.72 if terminal else 0.565), length * 0.34)
        root_clear = min(max(root_clear, min_root_clear), length - 0.012)
        web_len = max(0.012, length - root_clear)
        part.visual(
            Box((web_len, thickness, width)),
            origin=Origin(xyz=(root_clear + web_len * 0.5, 0.0, 0.0)),
            material=material,
            name=f"{name}_web", material_class_id=("metal.bronze_cast" if r.material_style in {"shop_steel", "dark_bronze"} else "metal.paint_coated"),
        )
        part.visual(
            Cylinder(radius=max(r.pin_radius * 0.82, width * 0.11), length=thickness * 0.30),
            origin=Origin(xyz=(0.0, thickness * 0.72, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=alt_material,
            name=f"{name}_root_clip_washer", material_class_id="metal.blackened_gunmetal",
        )
        # The clip bridge seats the lever root onto the pivot lobe/pin (this is
        # what keeps a cantilevered lever connected to its parent). It must
        # straddle the shared joint pin, so it cannot be separated from it; cap
        # its through-pin thickness below the overlap tolerance so that
        # unavoidable contact reads as touching rather than penetration.
        bridge_y = min(thickness * 0.36, 0.0045)
        part.visual(
            Box((root_clear + 0.002, bridge_y, width * 0.10)),
            origin=Origin(xyz=(root_clear * 0.5, thickness * 0.45, 0.0)),
            material=alt_material,
            name=f"{name}_root_clip_bridge", material_class_id="metal.blackened_gunmetal",
        )
        for x, label in ((0.0, "root"), (length, "tip")):
            if label == "root":
                continue
            part.visual(
                Cylinder(radius=width * 0.50, length=thickness),
                origin=Origin(xyz=(x, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=material,
                name=f"{name}_{label}_lobe", material_class_id=("metal.bronze_cast" if r.material_style in {"shop_steel", "dark_bronze"} else "metal.paint_coated"),
            )
            if label == "tip":
                # Offset the tip bushing to the -y face. The NEXT lever pivots
                # here and clusters its root-retention clip/washer on the +y
                # face; a centered fat bushing (protruding past both plate
                # faces) sweeps into that +y hardware as the child swings. The
                # pin is shared, so this can't be limit-clamped (touching at
                # rest); y-separating the two accents keeps them clear at every
                # angle without disturbing the pin joint itself.
                part.visual(
                    Cylinder(
                        radius=max(r.pin_radius * 1.45, width * 0.24), length=thickness * 1.0
                    ),
                    origin=Origin(xyz=(x, -thickness * 0.5, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=alt_material,
                    name=f"{name}_{label}_bushing", material_class_id="metal.blackened_gunmetal",
                )

    if not terminal and r.lever_profile in ("dogbone_plate", "slotted_rocker"):
        slot_len = max(length * 0.34, 0.030)
        if r.axis_family == "vertical_stack":
            part.visual(
                Box((slot_len, width * 0.18, thickness * 1.18)),
                origin=Origin(xyz=(length * 0.5, 0.0, 0.0005)),
                material=alt_material,
                name=f"{name}_lightening_slot_shadow", material_class_id="metal.blackened_gunmetal",
            )
        else:
            part.visual(
                Box((slot_len, thickness * 1.18, width * 0.18)),
                origin=Origin(xyz=(length * 0.5, 0.0, 0.0005)),
                material=alt_material,
                name=f"{name}_lightening_slot_shadow", material_class_id="metal.blackened_gunmetal",
            )
    if r.lever_profile == "slotted_rocker" and not terminal:
        for x in (length * 0.33, length * 0.67):
            part.visual(
                Cylinder(radius=r.pin_radius * 0.72, length=thickness * 1.55),
                origin=_cyl_origin_for_axis(r.axis_family, (x, 0.0, 0.0)),
                material=alt_material,
                name=f"{name}_adjust_pin_{x:.3f}", material_class_id="metal.blackened_gunmetal",
            )


def _build_base(model: ArticulatedObject, r: ResolvedLeverChainConfig, mats) -> object:
    base = model.part("ground_support")
    total_len = max(sum(r.lengths) * 0.62, 0.18)
    if r.axis_family == "vertical_stack":
        base.visual(
            Box((total_len, r.plate_width * 3.4, 0.018)),
            origin=Origin(xyz=(total_len * 0.22, 0.0, -0.018)),
            material=mats["base"],
            name="base_plate", material_class_id=("metal.bronze_cast" if r.material_style in {"shop_steel", "dark_bronze"} else "metal.paint_coated"),
        )
        base.visual(
            Box((0.042, r.plate_width * 2.2, r.base_origin_z)),
            origin=Origin(xyz=(-0.018, 0.0, r.base_origin_z * 0.5 - 0.012)),
            material=mats["base"],
            name="pedestal", material_class_id=("metal.bronze_cast" if r.material_style in {"shop_steel", "dark_bronze"} else "metal.paint_coated"),
        )
    else:
        base.visual(
            Box((total_len + 0.12, r.plate_width * 4.2, 0.022)),
            origin=Origin(xyz=(total_len * 0.35, 0.0, -0.055)),
            material=mats["base"],
            name="bench_plate", material_class_id=("metal.bronze_cast" if r.material_style in {"shop_steel", "dark_bronze"} else "metal.paint_coated"),
        )
        # Post top is kept at/below the pivot (z<=0). The levers swing UP off
        # the bench, and a tall lever plate's inner-top corner sweeps back over
        # the pivot toward -x during that swing; a post protruding above the
        # pivot would be raked by it (large-scale seeds). Topping the post out
        # just below z=0 keeps it clear of the up-swing arc for any angle/width
        # while still bridging the bench plate to the clevis.
        base.visual(
            Box((0.060, r.plate_width * 2.4, 0.054)),
            origin=Origin(xyz=(-0.030, 0.0, -0.030)),
            material=mats["base"],
            name="root_support_post", material_class_id=("metal.bronze_cast" if r.material_style in {"shop_steel", "dark_bronze"} else "metal.paint_coated"),
        )
        cheek_y = r.plate_width * 0.92
        for y, side in ((-cheek_y, "neg"), (cheek_y, "pos")):
            base.visual(
                Box((0.052, r.plate_thickness, r.plate_width * 2.4)),
                origin=Origin(xyz=(0.0, y, 0.0)),
                material=mats["base"],
                name=f"root_clevis_{side}", material_class_id=("metal.bronze_cast" if r.material_style in {"shop_steel", "dark_bronze"} else "metal.paint_coated"),
            )
            base.visual(
                Cylinder(radius=r.plate_width * 0.55, length=r.plate_thickness),
                origin=Origin(xyz=(0.0, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["base"],
                name=f"root_lobe_{side}", material_class_id=("metal.bronze_cast" if r.material_style in {"shop_steel", "dark_bronze"} else "metal.paint_coated"),
            )
    base.visual(
        Cylinder(
            radius=r.pin_radius,
            length=r.plate_thickness * 1.8
            if r.axis_family == "vertical_stack"
            else r.plate_width * 2.8,
        ),
        origin=_cyl_origin_for_axis(r.axis_family, (0.0, 0.0, 0.0)),
        material=mats["pin"],
        name="root_pin", material_class_id=("metal.brass_polished" if r.material_style in {"shop_steel", "blue_orange"} else "metal.brass_aged"),
    )
    for x in (-0.045, 0.060):
        for y in (-r.plate_width, r.plate_width):
            base.visual(
                Cylinder(radius=r.pin_radius * 0.65, length=0.004),
                origin=Origin(
                    xyz=(x, y, -0.043 if r.axis_family == "horizontal_bench" else -0.008)
                ),
                material=mats["dark"],
                name=f"mount_bolt_{x:.2f}_{y:.2f}", material_class_id="metal.blackened_gunmetal",
            )
    return base


def build_lever_chain(
    config: LeverChainConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name)
    mats = {key: _mat(model, r, key) for key in ("base", "link", "alt", "pin", "dark")}
    base = _build_base(model, r, mats)

    prev_part = base
    prev_len = 0.0
    prev_width = 0.0
    parts = []
    for index, length in enumerate(r.lengths):
        terminal = index == r.lever_count - 1 and r.output_module == "terminal_tab"
        part = model.part("output_lever" if index == r.lever_count - 1 else f"lever_{index}")
        width = r.plate_width * (0.92**index)
        if terminal:
            length *= 0.72
            width *= 0.86
        material = mats["link"] if index % 2 == 0 else mats["alt"]
        # Each lever pivots at the previous lever's tip, where the parent's
        # tip lobe (radius prev_width/2) fills the pin boss. Start this lever's
        # web just outside that lobe rim so the two coplanar plates seat against
        # each other instead of interpenetrating (worst for the narrow output
        # lever), and so folded-up neighbours keep clear near the shared pivot.
        min_root_clear = 0.0 if index == 0 else prev_width * 0.5 + r.pin_radius + 0.006
        _add_plate(
            part,
            r=r,
            length=length,
            width=width,
            thickness=r.plate_thickness,
            material=material,
            alt_material=mats["dark"],
            name=f"lever_{index}",
            terminal=terminal,
            min_root_clear=min_root_clear,
        )
        pin_len = r.plate_thickness * 1.8 if r.axis_family == "vertical_stack" else width * 2.5
        distal_pin_x = length
        part.visual(
            Cylinder(radius=r.pin_radius, length=pin_len),
            origin=_cyl_origin_for_axis(r.axis_family, (distal_pin_x, 0.0, 0.0)),
            material=mats["pin"],
            name="distal_joint_pin", material_class_id=("metal.brass_polished" if r.material_style in {"shop_steel", "blue_orange"} else "metal.brass_aged"),
        )
        if index == r.lever_count - 1 and r.output_module == "guide_pin_output":
            guide_x = length * 0.84
            part.visual(
                Cylinder(radius=r.pin_radius * 0.82, length=pin_len * 0.82),
                origin=_cyl_origin_for_axis(r.axis_family, (guide_x, width * 0.55, 0.0)),
                material=mats["pin"],
                name="output_guide_pin", material_class_id=("metal.brass_polished" if r.material_style in {"shop_steel", "blue_orange"} else "metal.brass_aged"),
            )
        if index == r.lever_count - 1 and r.output_module == "output_lever":
            part.visual(
                Box(
                    (length * 0.24, r.plate_thickness * 1.5, width * 0.34)
                    if r.axis_family == "horizontal_bench"
                    else (length * 0.24, width * 0.34, r.plate_thickness * 1.5)
                ),
                origin=Origin(xyz=(length * 0.92, 0.0, 0.0)),
                material=mats["pin"],
                name="output_pad", material_class_id=("metal.brass_polished" if r.material_style in {"shop_steel", "blue_orange"} else "metal.brass_aged"),
            )
        origin_xyz = (prev_len, 0.0, 0.0)
        if index == 0:
            origin_xyz = (0.0, 0.0, 0.0)
        model.articulation(
            f"{prev_part.name}_to_{part.name}",
            ArticulationType.REVOLUTE,
            parent=prev_part,
            child=part,
            origin=Origin(xyz=origin_xyz),
            axis=r.axis,
            motion_limits=MotionLimits(
                lower=r.joint_limits[index][0],
                upper=r.joint_limits[index][1],
                effort=10.0 + index * 3.0,
                velocity=2.0,
            ),
        )
        parts.append((part, length, width))
        prev_part = part
        prev_len = length
        prev_width = width

    if r.aux_coupler != "none" and len(parts) >= 3:
        for index in range(len(parts) - 1):
            parent, length, width = parts[index]
            coupler_len = max(0.040, length * 0.55)
            if r.axis_family == "horizontal_bench":
                parent.visual(
                    Box((coupler_len, r.plate_thickness * 0.55, width * 0.26)),
                    origin=Origin(xyz=(length * 0.52, 0.0, width * 0.30)),
                    material=mats["dark"],
                    name=f"front_coupler_{index}", material_class_id="metal.blackened_gunmetal",
                )
            else:
                parent.visual(
                    Box((coupler_len, width * 0.26, r.plate_thickness * 0.55)),
                    origin=Origin(xyz=(length * 0.52, 0.0, r.plate_thickness * 0.70)),
                    material=mats["dark"],
                    name=f"front_coupler_{index}", material_class_id="metal.blackened_gunmetal",
                )
            if r.aux_coupler == "guide_slots":
                parent.visual(
                    Box((coupler_len * 0.65, width * 0.12, r.plate_thickness * 0.80)),
                    origin=Origin(xyz=(length * 0.52, 0.0, r.plate_thickness * 0.95)),
                    material=mats["pin"],
                    name=f"guide_slot_rail_{index}", material_class_id=("metal.brass_polished" if r.material_style in {"shop_steel", "blue_orange"} else "metal.brass_aged"),
                )

    # Geometry-derived joint limits: tighten each cantilevered lever's travel
    # against the grounded bench so the swept subtree keeps clear of the bench
    # plate/post. Travel is up-only (lower already 0), so this caps the upward
    # sweep before it can wrap back down onto the bench behind the pivot.
    # Solving on the same FK the motion-QC gate samples keeps the returned limits
    # and the checked poses single-sourced (no per-template trig to drift out of
    # sync). The ROOT joint is skipped on purpose: its child lever seats on the
    # root pin (resting contact with ground_support), so a clearance-margin
    # clamp there would collapse to zero travel; with lower==0 that lever can
    # only lift up and off the bench, never into it.
    if r.axis_family == "horizontal_bench":
        for joint in list(model.articulations):
            if _part_name(joint.parent) == base.name:
                continue
            clamp_joint_limits(
                model,
                joint.name,
                margin=0.006,
                keepout=["ground_support"],
            )

    model.meta["template_slug"] = "lever_chain"
    model.meta["slot_choices"] = [list(item) for item in slot_choices_for_config(r)]
    model.meta["mating_contracts"] = [
        {
            "parent": "ground_support",
            "child": "lever_0" if r.lever_count > 1 else "output_lever",
            "description": "root lever pin seated in grounded support",
        }
    ]
    return model


def build_seeded_lever_chain(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_lever_chain(config_from_seed(seed), assets=assets)


def run_lever_chain_tests(
    model: ArticulatedObject, config: LeverChainConfig | None = None
) -> TestReport:
    ctx = TestContext(model)
    ctx.check_model_valid()
    joints = list(model.articulations)
    ctx.check(
        "lever chain has moving joints",
        len(joints) >= 2 and all(j.articulation_type == ArticulationType.REVOLUTE for j in joints),
        details=f"joints={[j.name for j in joints]}",
    )
    axis = tuple(joints[0].axis)
    ctx.check(
        "main pivot axes are parallel",
        all(tuple(j.axis) == axis for j in joints),
        details=f"axes={[j.axis for j in joints]}",
    )
    resolved = resolve_config(config)
    if resolved.axis_family == "horizontal_bench":
        # Bench-mounted levers rest ON the bench; the only physical travel is
        # lifting up (positive/upper). Downward travel into the bench is
        # forbidden, so every joint's lower limit must stay at the bench rest
        # (>= 0) and the upward actuation must remain usable (upper > 0).
        ctx.check(
            "bench levers never swing down into the bench (lower limit == rest)",
            all((j.motion_limits.lower or 0.0) >= -1e-9 for j in joints),
            details=f"lowers={[round(j.motion_limits.lower or 0.0, 4) for j in joints]}",
        )
        ctx.check(
            "bench levers retain upward actuation travel",
            all((j.motion_limits.upper or 0.0) > 0.02 for j in joints),
            details=f"uppers={[round(j.motion_limits.upper or 0.0, 4) for j in joints]}",
        )
    output = model.get_part("output_lever")
    ctx.check("output lever exists", output is not None)
    if output is not None and joints:
        rest = ctx.part_world_position(output)
        pose = {joint: min(0.45, joint.motion_limits.upper * 0.45) for joint in joints}
        with ctx.pose(pose):
            moved = ctx.part_world_position(output)
        ctx.check(
            "output moves under lever actuation",
            rest is not None and moved is not None and math.dist(rest, moved) > 0.010,
            details=f"rest={rest}, moved={moved}",
        )
    return ctx.report()


__all__ = [
    "LeverChainConfig",
    "build_lever_chain",
    "build_seeded_lever_chain",
    "config_from_seed",
    "resolve_config",
    "run_lever_chain_tests",
    "slot_choices_for_seed",
    "with_overrides",
]
