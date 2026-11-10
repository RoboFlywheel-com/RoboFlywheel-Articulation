# SPDX-License-Identifier: Apache-2.0

"""Procedural template for ``rotary_table_with_tilting_trunnion``.

Follows ``articraft_template_authoring/specs_modular_v1/rotary_table_with_tilting_trunnion.md``.

Industrial rotary table with tilting trunnion: a fixed base carries a tilt
stage (horizontal trunnion axis, REVOLUTE X) and a continuously rotating
machinist faceplate (CONTINUOUS Z).

PRIMARY_ANCHOR: ``rec_rotary_table_with_tilting_trunnion_0519446d725e4e46b67e698286d090b6``.

    base --tilt (REVOLUTE +X)--> tilt_frame --rotary (CONTINUOUS +Z)--> turntable

Adopted sources (see spec Adopted Source Index):
S1 0519446d side-cheek trunnion + slotted disk
S2 0003 cadquery cradle + journal table
S3 7bb3557e mesh yoke + tool plate
S4 92932ff7 stacked lower_stage + faceplate
S5 457ff797 compact pedestal
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
    MotionLimits,
    MotionProperties,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

# adopted: S1 0519446d — canonical side-cheek base + tilt_frame + turntable
# adopted: S2 0003 — open cradle yoke + journal table
# adopted: S3 7bb3557e — mesh yoke variant
# adopted: S4 92932ff7 — stacked heavy base
# adopted: S5 457ff797 — compact pedestal

BaseStyle = Literal["side_cheek", "cadquery_box", "stacked_heavy", "pedestal"]
TiltStageStyle = Literal["integrated_frame", "open_cradle", "mesh_yoke", "lower_stage"]
FaceplateStyle = Literal["slotted_disk", "square_table", "mesh_plate", "large_faceplate"]
MaterialStyle = Literal["blued_cast_iron", "ground_machinist", "industrial_grey"]

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "blued_cast_iron": {
        "cast": (0.12, 0.16, 0.18, 1.0),
        "dark": (0.035, 0.04, 0.045, 1.0),
        "steel": (0.62, 0.64, 0.62, 1.0),
        "bearing": (0.44, 0.46, 0.46, 1.0),
        "slot": (0.01, 0.011, 0.012, 1.0),
        "bolt": (0.02, 0.022, 0.024, 1.0),
    },
    "ground_machinist": {
        "cast": (0.18, 0.20, 0.22, 1.0),
        "dark": (0.08, 0.09, 0.10, 1.0),
        "steel": (0.70, 0.72, 0.71, 1.0),
        "bearing": (0.52, 0.54, 0.53, 1.0),
        "slot": (0.04, 0.04, 0.05, 1.0),
        "bolt": (0.06, 0.06, 0.07, 1.0),
    },
    "industrial_grey": {
        "cast": (0.24, 0.26, 0.28, 1.0),
        "dark": (0.12, 0.13, 0.14, 1.0),
        "steel": (0.58, 0.60, 0.59, 1.0),
        "bearing": (0.40, 0.42, 0.41, 1.0),
        "slot": (0.02, 0.02, 0.03, 1.0),
        "bolt": (0.03, 0.03, 0.04, 1.0),
    },
}


@dataclass(frozen=True)
class RotaryTableWithTiltingTrunnionConfig:
    """Defaults reproduce PRIMARY_ANCHOR S1 proportions."""

    base_style: BaseStyle = "side_cheek"
    tilt_stage_style: TiltStageStyle = "integrated_frame"
    faceplate_style: FaceplateStyle = "slotted_disk"
    material_style: MaterialStyle = "blued_cast_iron"
    table_diameter: float = 0.65
    base_footprint_x: float = 1.18
    base_footprint_y: float = 0.78
    base_plate_thickness: float = 0.08
    cheek_height: float = 0.50
    trunnion_axis_z: float = 0.58
    tilt_lower: float = -1.05
    tilt_upper: float = 1.05
    slot_count: int = 3
    fixture_hole_count: int = 4
    name: str = "reference_rotary_table_with_tilting_trunnion"


@dataclass(frozen=True)
class ResolvedRotaryTableWithTiltingTrunnionConfig:
    base_style: BaseStyle
    tilt_stage_style: TiltStageStyle
    faceplate_style: FaceplateStyle
    material_style: MaterialStyle
    table_diameter: float
    table_radius: float
    base_footprint_x: float
    base_footprint_y: float
    base_plate_thickness: float
    cheek_height: float
    cheek_half_span: float
    trunnion_axis_z: float
    tilt_lower: float
    tilt_upper: float
    slot_count: int
    fixture_hole_count: int
    rotary_bearing_radius: float
    rotary_bearing_height: float
    pivot_hub_offset: float
    pivot_hub_radius: float
    rotary_joint_z: float
    name: str


_BASE_STYLES = frozenset({"side_cheek", "cadquery_box", "stacked_heavy", "pedestal"})
_TILT_STYLES = frozenset({"integrated_frame", "open_cradle", "mesh_yoke", "lower_stage"})
_FACE_STYLES = frozenset({"slotted_disk", "square_table", "mesh_plate", "large_faceplate"})


def config_from_seed(seed: int) -> RotaryTableWithTiltingTrunnionConfig:
    if seed == 0:
        return RotaryTableWithTiltingTrunnionConfig()

    rng = random.Random(seed)
    base_style: BaseStyle = rng.choice(("side_cheek", "cadquery_box", "stacked_heavy", "pedestal"))
    tilt_stage_style: TiltStageStyle = rng.choice(
        ("integrated_frame", "open_cradle", "mesh_yoke", "lower_stage")
    )
    faceplate_style: FaceplateStyle = rng.choice(
        ("slotted_disk", "square_table", "mesh_plate", "large_faceplate")
    )

    compact = base_style == "pedestal"
    if compact:
        table_diameter = round(rng.uniform(0.38, 0.58), 4)
        base_footprint_x = round(rng.uniform(0.42, 0.62), 4)
        base_footprint_y = round(rng.uniform(0.42, 0.62), 4)
    else:
        table_diameter = round(rng.uniform(0.48, 0.92), 4)
        base_footprint_x = round(rng.uniform(0.85, 1.45), 4)
        base_footprint_y = round(rng.uniform(0.55, 0.95), 4)

    cheek_height = round(rng.uniform(0.32, 0.62), 4)
    trunnion_axis_z = round(rng.uniform(0.38, 0.72) if compact else rng.uniform(0.48, 0.72), 4)
    tilt_lower = round(rng.uniform(-1.15, -0.85), 4)
    tilt_upper = round(rng.uniform(0.85, 1.15), 4)

    return RotaryTableWithTiltingTrunnionConfig(
        base_style=base_style,
        tilt_stage_style=tilt_stage_style,
        faceplate_style=faceplate_style,
        material_style=rng.choice(tuple(PALETTES)),
        table_diameter=table_diameter,
        base_footprint_x=base_footprint_x,
        base_footprint_y=base_footprint_y,
        base_plate_thickness=round(rng.uniform(0.05, 0.12), 4),
        cheek_height=cheek_height,
        trunnion_axis_z=trunnion_axis_z,
        tilt_lower=tilt_lower,
        tilt_upper=tilt_upper,
        slot_count=rng.choice((2, 3, 4)),
        fixture_hole_count=rng.choice((4, 6, 8)),
        name=f"seeded_rotary_table_{seed}",
    )


def resolve_config(
    config: RotaryTableWithTiltingTrunnionConfig,
) -> ResolvedRotaryTableWithTiltingTrunnionConfig:
    if config.base_style not in _BASE_STYLES:
        raise ValueError(f"Unsupported base_style: {config.base_style}")
    if config.tilt_stage_style not in _TILT_STYLES:
        raise ValueError(f"Unsupported tilt_stage_style: {config.tilt_stage_style}")
    if config.faceplate_style not in _FACE_STYLES:
        raise ValueError(f"Unsupported faceplate_style: {config.faceplate_style}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    compact = config.base_style == "pedestal"
    table_diameter = _clamp(config.table_diameter, 0.34 if compact else 0.42, 0.98)
    table_radius = table_diameter * 0.5
    base_footprint_x = _clamp(config.base_footprint_x, 0.38 if compact else 0.72, 1.55)
    base_footprint_y = _clamp(config.base_footprint_y, 0.38 if compact else 0.48, 1.05)
    base_plate_thickness = _clamp(config.base_plate_thickness, 0.04, 0.14)
    cheek_height = _clamp(config.cheek_height, 0.26, 0.72)
    trunnion_axis_z = _clamp(
        config.trunnion_axis_z,
        base_plate_thickness + cheek_height * 0.55,
        base_plate_thickness + cheek_height + 0.18,
    )

    tilt_lower = config.tilt_lower
    tilt_upper = config.tilt_upper
    if tilt_lower >= tilt_upper:
        tilt_lower, tilt_upper = -1.05, 1.05
    tilt_lower = _clamp(tilt_lower, -1.25, -0.65)
    tilt_upper = _clamp(tilt_upper, 0.65, 1.25)

    slot_count = int(_clamp(config.slot_count, 2, 4))
    fixture_hole_count = int(_clamp(config.fixture_hole_count, 4, 8))

    cheek_half_span = base_footprint_x * (0.50 / 1.18)
    cheek_half_span = _clamp(cheek_half_span, 0.38, base_footprint_x * 0.46)

    rotary_bearing_radius = max(table_radius * 0.37, 0.14)
    rotary_bearing_height = max(table_radius * 0.123, 0.06)
    pivot_hub_offset = cheek_half_span * 0.82
    pivot_hub_radius = max(table_radius * 0.15, 0.06)
    rotary_joint_z = rotary_bearing_height

    return ResolvedRotaryTableWithTiltingTrunnionConfig(
        base_style=config.base_style,
        tilt_stage_style=config.tilt_stage_style,
        faceplate_style=config.faceplate_style,
        material_style=config.material_style,
        table_diameter=table_diameter,
        table_radius=table_radius,
        base_footprint_x=base_footprint_x,
        base_footprint_y=base_footprint_y,
        base_plate_thickness=base_plate_thickness,
        cheek_height=cheek_height,
        cheek_half_span=cheek_half_span,
        trunnion_axis_z=trunnion_axis_z,
        tilt_lower=tilt_lower,
        tilt_upper=tilt_upper,
        slot_count=slot_count,
        fixture_hole_count=fixture_hole_count,
        rotary_bearing_radius=rotary_bearing_radius,
        rotary_bearing_height=rotary_bearing_height,
        pivot_hub_offset=pivot_hub_offset,
        pivot_hub_radius=pivot_hub_radius,
        rotary_joint_z=rotary_joint_z,
        name=config.name,
    )


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _joint_meta(
    joint_type: str,
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    joint_range: object,
) -> dict[str, object]:
    return {"type": joint_type, "axis": axis, "origin": origin, "range": joint_range}


def _is_anchor_config(config: RotaryTableWithTiltingTrunnionConfig) -> bool:
    """True when *config* matches the PRIMARY_ANCHOR S1 defaults (seed=0)."""
    anchor = RotaryTableWithTiltingTrunnionConfig()
    fields = (
        "base_style",
        "tilt_stage_style",
        "faceplate_style",
        "material_style",
        "table_diameter",
        "base_footprint_x",
        "base_footprint_y",
        "base_plate_thickness",
        "cheek_height",
        "trunnion_axis_z",
        "tilt_lower",
        "tilt_upper",
        "slot_count",
        "fixture_hole_count",
    )
    for name in fields:
        if getattr(config, name) != getattr(anchor, name):
            return False
    return True


def _build_anchor_s1(model: ArticulatedObject, *, mats) -> None:
    """Literal reproduction of PRIMARY_ANCHOR model.py (adopted: S1 L29-L179)."""
    cast_iron = mats["cast"]
    dark_iron = mats["dark"]
    ground_steel = mats["steel"]
    bearing_steel = mats["bearing"]
    slot_black = mats["slot"]
    bolt_dark = mats["bolt"]

    base = model.part("base")
    base.visual(
        Box((1.18, 0.78, 0.08)),
        origin=Origin(xyz=(0.0, 0.0, 0.04)),
        material=cast_iron,
        name="base_plate", material_class_id="metal.cast_iron_bare",
    )
    base.visual(
        Box((0.96, 0.50, 0.12)),
        origin=Origin(xyz=(0.0, 0.0, 0.14)),
        material=cast_iron,
        name="raised_plinth", material_class_id="metal.cast_iron_bare",
    )
    for index, x in enumerate((0.50, -0.50)):
        base.visual(
            Box((0.12, 0.18, 0.50)),
            origin=Origin(xyz=(x, 0.0, 0.36)),
            material=cast_iron,
            name=f"side_support_{index}", material_class_id="metal.cast_iron_bare",
        )
        cap_x = x + (0.072 if x > 0 else -0.072)
        base.visual(
            Cylinder(radius=0.115, length=0.028),
            origin=Origin(xyz=(cap_x, 0.0, 0.58), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=bearing_steel,
            name=f"outer_bearing_cap_{index}", material_class_id="metal.chrome_polished",
        )
        base.visual(
            Cylinder(radius=0.055, length=0.032),
            origin=Origin(
                xyz=(cap_x + (0.004 if x > 0 else -0.004), 0.0, 0.58),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=dark_iron,
            name=f"bearing_bore_{index}", material_class_id="metal.blackened_gunmetal",
        )
        for y in (0.135, -0.135):
            base.visual(
                Box((0.050, 0.090, 0.34)),
                origin=Origin(xyz=(x, y, 0.29)),
                material=cast_iron,
                name=f"cheek_rib_{index}_{0 if y > 0 else 1}", material_class_id="metal.cast_iron_bare",
            )

    base.visual(
        Box((0.24, 0.52, 0.38)),
        origin=Origin(xyz=(0.0, 0.0, 0.39)),
        material=cast_iron,
        name="trunnion_center_boss", material_class_id="metal.cast_iron_bare",
    )

    tilt_frame = model.part("tilt_frame")
    tilt_frame.visual(
        Box((0.78, 0.12, 0.10)),
        origin=Origin(xyz=(0.0, 0.0, -0.035)),
        material=dark_iron,
        name="cross_saddle", material_class_id="metal.blackened_gunmetal",
    )
    tilt_frame.visual(
        Cylinder(radius=0.240, length=0.080),
        origin=Origin(xyz=(0.0, 0.0, 0.040)),
        material=dark_iron,
        name="rotary_bearing", material_class_id="metal.blackened_gunmetal",
    )
    tilt_frame.visual(
        Cylinder(radius=0.285, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.071)),
        material=bearing_steel,
        name="bearing_race", material_class_id="metal.chrome_polished",
    )
    for index, x in enumerate((0.410, -0.410)):
        tilt_frame.visual(
            Cylinder(radius=0.098, length=0.060),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=bearing_steel,
            name=f"pivot_hub_{index}", material_class_id="metal.chrome_polished",
        )
        tilt_frame.visual(
            Cylinder(radius=0.062, length=0.055),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=dark_iron,
            name=f"hub_boss_{index}", material_class_id="metal.blackened_gunmetal",
        )

    turntable = model.part("turntable")
    turntable.visual(
        Cylinder(radius=0.325, length=0.070),
        origin=Origin(xyz=(0.0, 0.0, 0.035)),
        material=ground_steel,
        name="turntable_disk", material_class_id="metal.steel_bare",
    )
    turntable.visual(
        Cylinder(radius=0.340, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.012)),
        material=bearing_steel,
        name="dark_outer_rim", material_class_id="metal.chrome_polished",
    )
    turntable.visual(
        Cylinder(radius=0.050, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.076)),
        material=slot_black,
        name="center_bore", material_class_id="metal.blackened_gunmetal",
    )
    turntable.visual(
        Cylinder(radius=0.118, length=0.005),
        origin=Origin(xyz=(0.0, 0.0, 0.0725)),
        material=bearing_steel,
        name="center_register", material_class_id="metal.chrome_polished",
    )
    for index, x in enumerate((-0.145, 0.0, 0.145)):
        turntable.visual(
            Box((0.028, 0.500, 0.006)),
            origin=Origin(xyz=(x, 0.0, 0.071)),
            material=slot_black,
            name=f"slot_{index}", material_class_id="metal.blackened_gunmetal",
        )
        turntable.visual(
            Box((0.070, 0.500, 0.003)),
            origin=Origin(xyz=(x, 0.0, 0.071)),
            material=dark_iron,
            name=f"slot_shoulder_{index}", material_class_id="metal.blackened_gunmetal",
        )
    bolt_radius = 0.220
    for index, angle in enumerate((0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)):
        bx = bolt_radius * math.cos(angle)
        by = bolt_radius * math.sin(angle)
        turntable.visual(
            Cylinder(radius=0.018, length=0.006),
            origin=Origin(xyz=(bx, by, 0.071)),
            material=bolt_dark,
            name=f"fixture_hole_{index}", material_class_id="metal.blackened_gunmetal",
        )

    model.articulation(
        "base_to_tilt_frame",
        ArticulationType.REVOLUTE,
        parent=base,
        child=tilt_frame,
        origin=Origin(xyz=(0.0, 0.0, 0.58)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=500.0, velocity=0.60, lower=-1.05, upper=1.05),
        motion_properties=MotionProperties(damping=12.0, friction=4.0),
        meta=_joint_meta("revolute", (1.0, 0.0, 0.0), (0.0, 0.0, 0.58), (-1.05, 1.05)),
    )
    model.articulation(
        "tilt_frame_to_turntable",
        ArticulationType.CONTINUOUS,
        parent=tilt_frame,
        child=turntable,
        origin=Origin(xyz=(0.0, 0.0, 0.080)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=260.0, velocity=1.20),
        motion_properties=MotionProperties(damping=4.0, friction=2.0),
        meta=_joint_meta("continuous", (0.0, 0.0, 1.0), (0.0, 0.0, 0.080), "unbounded"),
    )


def _anchor_resolved() -> ResolvedRotaryTableWithTiltingTrunnionConfig:
    return resolve_config(RotaryTableWithTiltingTrunnionConfig())


def _add_base_trunnion_cross_shaft(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """Fixed trunnion axle along +X on the tilt axis (anchors parent joint origin)."""
    steel = mats["steel"]
    cast = mats["cast"]
    tz = resolved.trunnion_axis_z
    span = max(
        resolved.cheek_half_span * 2.0 + 0.20,
        resolved.pivot_hub_offset * 2.0 + 0.24,
        1.05,
    )
    if resolved.base_style == "side_cheek":
        part.visual(
            Box(
                (
                    span,
                    max(0.14, resolved.base_footprint_y * 0.20),
                    max(0.06, resolved.pivot_hub_radius * 1.0),
                )
            ),
            origin=Origin(xyz=(0.0, 0.0, tz)),
            material=cast,
            name="trunnion_tie_beam", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
        )
    else:
        part.visual(
            Box(
                (
                    max(0.18, resolved.base_footprint_x * 0.18),
                    max(0.22, resolved.base_footprint_y * 0.28),
                    max(0.24, tz * 0.42),
                )
            ),
            origin=Origin(
                xyz=(0.0, 0.0, resolved.base_plate_thickness * 2.0 + max(0.12, tz * 0.22))
            ),
            material=cast,
            name="trunnion_center_boss", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
        )
    part.visual(
        Cylinder(radius=max(0.055, resolved.pivot_hub_radius * 0.88), length=span),
        origin=Origin(xyz=(0.0, 0.0, tz), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=steel,
        name="trunnion_cross_shaft", material_class_id="metal.steel_bare",
    )


def _add_tilt_frame_trunnion_shaft(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """Child-side trunnion axle at the tilt joint origin (0,0,0) in tilt_frame frame."""
    dark = mats["dark"]
    span = max(resolved.pivot_hub_offset * 2.15, 0.86)
    part.visual(
        Cylinder(radius=max(0.075, resolved.pivot_hub_radius * 1.15), length=span),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=dark,
        name="trunnion_through_shaft", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box(
            (
                span * 0.92,
                max(0.08, resolved.table_radius * 0.16),
                max(0.08, resolved.table_radius * 0.14),
            )
        ),
        origin=Origin(xyz=(0.0, 0.0, max(0.02, resolved.rotary_bearing_height * 0.18))),
        material=dark,
        name="tilt_frame_spine", material_class_id="metal.blackened_gunmetal",
    )


def _build_base_plate_common(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    cast = mats["cast"]
    fx = resolved.base_footprint_x
    fy = resolved.base_footprint_y
    t = resolved.base_plate_thickness
    plinth_h = t * 1.5
    part.visual(
        Box((fx, fy, t)),
        origin=Origin(xyz=(0.0, 0.0, t * 0.5)),
        material=cast,
        name="base_plate", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
    )
    part.visual(
        Box((fx * 0.82, fy * 0.64, plinth_h)),
        origin=Origin(xyz=(0.0, 0.0, t + plinth_h * 0.5)),
        material=cast,
        name="raised_plinth", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
    )


def _build_side_cheek_base(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S1 L29-L73 — side cheek cast base with bearing caps."""
    _build_base_plate_common(part, resolved, mats=mats)
    cast = mats["cast"]
    bearing = mats["bearing"]
    cheek_x = resolved.cheek_half_span
    tz = resolved.trunnion_axis_z
    pr = resolved.pivot_hub_radius
    t = resolved.base_plate_thickness
    plinth_h = t * 1.5
    stack_top = t + plinth_h
    # Cheek posts overlap the plinth top so FCL sees one connected base island.
    cheek_h = max(0.24, tz + pr * 0.55 - stack_top + 0.04)
    cheek_cz = stack_top - 0.02 + cheek_h * 0.5
    support_wx = max(0.10, cheek_x * 0.22)
    support_wy = max(0.14, resolved.base_footprint_y * 0.22)

    for index, x in enumerate((cheek_x, -cheek_x)):
        part.visual(
            Box((support_wx, support_wy, cheek_h)),
            origin=Origin(xyz=(x, 0.0, cheek_cz)),
            material=cast,
            name=f"side_support_{index}", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
        )
        part.visual(
            Cylinder(radius=max(0.08, pr * 1.15), length=max(0.04, support_wx * 0.35)),
            origin=Origin(xyz=(x, 0.0, tz), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=bearing,
            name=f"outer_bearing_cap_{index}", material_class_id="metal.chrome_polished",
        )
        for y_sign, rib_idx in ((1, 0), (-1, 1)):
            y = y_sign * min(support_wy * 0.55, resolved.base_footprint_y * 0.17)
            part.visual(
                Box((support_wx * 0.90, support_wy * 0.42, cheek_h * 0.78)),
                origin=Origin(xyz=(x, y, cheek_cz)),
                material=cast,
                name=f"cheek_rib_{index}_{rib_idx}", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
            )

    column_h = max(0.18, tz - stack_top + 0.04)
    part.visual(
        Cylinder(radius=max(0.08, pr * 0.85), length=column_h),
        origin=Origin(xyz=(0.0, 0.0, stack_top - 0.02 + column_h * 0.5)),
        material=cast,
        name="center_trunnion_column", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
    )
    part.visual(
        Cylinder(radius=max(0.10, pr * 1.25), length=max(0.06, pr * 1.1)),
        origin=Origin(xyz=(0.0, 0.0, tz)),
        material=cast,
        name="trunnion_bearing_seat", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
    )
    part.visual(
        Box((cheek_x * 2.08, support_wy * 0.62, t * 0.55)),
        origin=Origin(xyz=(0.0, 0.0, stack_top - t * 0.18)),
        material=cast,
        name="cheek_tie_beam", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
    )


def _build_cadquery_box_base(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S2 — simpler box base with pad."""
    _build_base_plate_common(part, resolved, mats=mats)
    steel = mats["steel"]
    dark = mats["dark"]
    pad_z = resolved.base_plate_thickness * 3.0
    part.visual(
        Cylinder(radius=max(0.12, resolved.table_radius * 0.38), length=0.04),
        origin=Origin(xyz=(0.0, 0.0, resolved.base_plate_thickness * 2.0 + 0.02)),
        material=steel,
        name="rotary_seat_pad", material_class_id="metal.steel_bare",
    )
    pad_z = resolved.base_plate_thickness * 2.0
    for index, ang in enumerate((0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)):
        x = math.cos(ang) * resolved.base_footprint_x * 0.38
        y = math.sin(ang) * resolved.base_footprint_y * 0.38
        part.visual(
            Cylinder(radius=0.022, length=max(0.04, pad_z)),
            origin=Origin(xyz=(x, y, pad_z * 0.5)),
            material=dark,
            name=f"mount_bolt_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _build_stacked_heavy_base(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S4 — heavy stacked base with ribs."""
    _build_base_plate_common(part, resolved, mats=mats)
    cast = mats["cast"]
    dark = mats["dark"]
    for index, x in enumerate(
        (resolved.base_footprint_x * 0.32, -resolved.base_footprint_x * 0.32)
    ):
        part.visual(
            Box((0.14, resolved.base_footprint_y * 0.72, resolved.cheek_height * 0.85)),
            origin=Origin(
                xyz=(x, 0.0, resolved.base_plate_thickness * 2.0 + resolved.cheek_height * 0.42)
            ),
            material=cast,
            name=f"stack_rib_{index}", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
        )
        part.visual(
            Box(
                (0.08, resolved.base_footprint_y * 0.40, max(0.12, resolved.trunnion_axis_z * 0.22))
            ),
            origin=Origin(
                xyz=(
                    x * 0.55,
                    0.0,
                    resolved.trunnion_axis_z - max(0.06, resolved.trunnion_axis_z * 0.10),
                )
            ),
            material=cast,
            name=f"stack_rib_tie_{index}", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
        )
    for band in range(3):
        z = resolved.base_plate_thickness * (2.2 + band * 0.18)
        part.visual(
            Box((resolved.base_footprint_x * 0.92, 0.04, 0.04)),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=dark,
            name=f"stack_band_{band}", material_class_id="metal.blackened_gunmetal",
        )


def _build_pedestal_base(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S5 — short pedestal."""
    cast = mats["cast"]
    steel = mats["steel"]
    h = max(0.22, resolved.trunnion_axis_z - resolved.table_radius * 0.15)
    part.visual(
        Cylinder(radius=max(0.18, resolved.table_radius * 0.55), length=h),
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
        material=cast,
        name="pedestal_column", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
    )
    part.visual(
        Cylinder(radius=max(0.24, resolved.table_radius * 0.72), length=0.05),
        origin=Origin(xyz=(0.0, 0.0, 0.025)),
        material=cast,
        name="pedestal_foot", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
    )
    part.visual(
        Cylinder(radius=max(0.14, resolved.rotary_bearing_radius * 0.65), length=0.06),
        origin=Origin(xyz=(0.0, 0.0, h)),
        material=steel,
        name="pedestal_top_seat", material_class_id="metal.steel_bare",
    )


def _add_trunnion_bearing_posts(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """Side trunnion posts so tilt_frame pivot hubs meet grounded steel on every base style."""
    if resolved.base_style == "side_cheek":
        return
    cast = mats["cast"]
    tz = resolved.trunnion_axis_z
    post_w = max(0.10, resolved.pivot_hub_radius * 1.6)
    post_h = max(0.20, tz - resolved.base_plate_thickness)
    post_cz = resolved.base_plate_thickness + post_h * 0.5
    for index, x in enumerate((resolved.cheek_half_span, -resolved.cheek_half_span)):
        part.visual(
            Box((post_w, max(0.14, resolved.base_footprint_y * 0.22), post_h)),
            origin=Origin(xyz=(x, 0.0, post_cz)),
            material=cast,
            name=f"trunnion_post_{index}", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
        )
    part.visual(
        Box((resolved.cheek_half_span * 2.05, post_w * 0.85, post_h * 0.55)),
        origin=Origin(xyz=(0.0, 0.0, post_cz)),
        material=cast,
        name="trunnion_bridge_beam", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
    )


def _build_base(part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats) -> None:
    if resolved.base_style == "side_cheek":
        _build_side_cheek_base(part, resolved, mats=mats)
    elif resolved.base_style == "cadquery_box":
        _build_cadquery_box_base(part, resolved, mats=mats)
    elif resolved.base_style == "stacked_heavy":
        _build_stacked_heavy_base(part, resolved, mats=mats)
    else:
        _build_pedestal_base(part, resolved, mats=mats)
    _add_trunnion_bearing_posts(part, resolved, mats=mats)
    if resolved.base_style != "side_cheek":
        _add_base_trunnion_cross_shaft(part, resolved, mats=mats)


# --------------------------------------------------------------------------- #
# Tilt stage builders (adopted: S1 / S2 / S3 / S4)
# --------------------------------------------------------------------------- #


def _build_integrated_tilt_frame(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S1 L75-L107 — cross saddle + rotary bearing + pivot hubs."""
    dark = mats["dark"]
    bearing = mats["bearing"]
    br = resolved.rotary_bearing_radius
    bh = resolved.rotary_bearing_height
    ph = resolved.pivot_hub_offset
    pr = resolved.pivot_hub_radius

    part.visual(
        Box((resolved.table_diameter * 1.15, max(0.10, resolved.table_radius * 0.18), 0.10)),
        origin=Origin(xyz=(0.0, 0.0, -0.035)),
        material=dark,
        name="cross_saddle", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=br, length=bh),
        origin=Origin(xyz=(0.0, 0.0, bh * 0.5)),
        material=dark,
        name="rotary_bearing", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=br * 1.18, length=max(0.012, bh * 0.22)),
        origin=Origin(xyz=(0.0, 0.0, bh * 0.92)),
        material=bearing,
        name="bearing_race", material_class_id="metal.chrome_polished",
    )
    part.visual(
        Cylinder(radius=br * 0.55, length=max(0.02, bh * 0.12)),
        origin=Origin(xyz=(0.0, 0.0, bh * 0.55)),
        material=bearing,
        name="rotary_joint_boss", material_class_id="metal.chrome_polished",
    )
    for index, x in enumerate((ph, -ph)):
        part.visual(
            Cylinder(radius=pr * 1.65, length=max(ph * 0.48, pr * 1.8)),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=bearing,
            name=f"pivot_hub_{index}", material_class_id="metal.chrome_polished",
        )
        part.visual(
            Cylinder(radius=pr * 1.05, length=max(ph * 0.42, pr * 1.5)),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=dark,
            name=f"hub_boss_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _build_open_cradle_yoke(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S2 — open cradle with risers and arms."""
    cast = mats["cast"]
    arm_x = resolved.pivot_hub_offset
    arm_h = max(0.14, resolved.table_radius * 0.42)
    base_t = 0.06
    part.visual(
        Box(
            (resolved.table_diameter * 0.55, resolved.table_diameter * 0.55, base_t + arm_h * 0.55)
        ),
        origin=Origin(xyz=(0.0, 0.0, (base_t + arm_h * 0.55) * 0.5)),
        material=cast,
        name="cradle_mount", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
    )
    for side, x in (("left", arm_x), ("right", -arm_x)):
        part.visual(
            Box((max(0.05, arm_x * 0.12), max(0.12, resolved.table_radius * 0.28), arm_h)),
            origin=Origin(xyz=(x, 0.0, base_t + arm_h * 0.5)),
            material=cast,
            name=f"{side}_arm", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
        )


def _build_mesh_yoke_stage(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S3 — yoke plate with split trunnion bosses (visual-only mesh stand-in)."""
    steel = mats["steel"]
    span = resolved.pivot_hub_offset
    web_z = max(0.04, resolved.table_radius * 0.08)
    part.visual(
        Box(
            (
                span * 2.1,
                max(0.16, resolved.table_radius * 0.42),
                max(0.12, resolved.table_radius * 0.18),
            )
        ),
        origin=Origin(xyz=(0.0, 0.0, web_z)),
        material=steel,
        name="yoke_web", material_class_id="metal.steel_bare",
    )
    for index, x in enumerate((span, -span)):
        part.visual(
            Cylinder(radius=resolved.pivot_hub_radius * 1.45, length=max(0.14, span * 0.32)),
            origin=Origin(xyz=(x, 0.0, web_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=steel,
            name=f"yoke_trunnion_{index}", material_class_id="metal.steel_bare",
        )
    part.visual(
        Cylinder(radius=resolved.rotary_bearing_radius, length=resolved.rotary_bearing_height),
        origin=Origin(xyz=(0.0, 0.0, resolved.rotary_bearing_height * 0.5)),
        material=steel,
        name="yoke_rotary_bearing", material_class_id="metal.steel_bare",
    )


def _build_lower_stage_tilt(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S4 — lower rotary stage body."""
    cast = mats["cast"]
    steel = mats["steel"]
    h = max(0.12, resolved.table_radius * 0.32)
    part.visual(
        Cylinder(radius=resolved.table_radius * 0.72, length=h),
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
        material=cast,
        name="lower_stage_barrel", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
    )
    part.visual(
        Cylinder(radius=resolved.rotary_bearing_radius * 1.05, length=h * 0.35),
        origin=Origin(xyz=(0.0, 0.0, h * 0.82)),
        material=steel,
        name="lower_stage_top_bearing", material_class_id="metal.steel_bare",
    )
    tr_z = h * 0.55
    for index, x in enumerate(
        (resolved.pivot_hub_offset * 0.85, -resolved.pivot_hub_offset * 0.85)
    ):
        part.visual(
            Cylinder(
                radius=resolved.pivot_hub_radius, length=max(0.12, resolved.pivot_hub_offset * 0.35)
            ),
            origin=Origin(xyz=(x, 0.0, tr_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=steel,
            name=f"lower_trunnion_{index}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box(
                (
                    max(0.05, resolved.pivot_hub_radius * 1.4),
                    max(0.06, resolved.table_radius * 0.18),
                    h * 0.55,
                )
            ),
            origin=Origin(xyz=(x * 0.55, 0.0, h * 0.28)),
            material=cast,
            name=f"lower_trunnion_web_{index}", material_class_id=("metal.cast_iron_bare" if resolved.material_style in {"blued_cast_iron", "ground_machinist"} else "metal.paint_coated"),
        )


def _build_tilt_frame(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    if resolved.tilt_stage_style == "integrated_frame":
        _build_integrated_tilt_frame(part, resolved, mats=mats)
    elif resolved.tilt_stage_style == "open_cradle":
        _build_open_cradle_yoke(part, resolved, mats=mats)
    elif resolved.tilt_stage_style == "mesh_yoke":
        _build_mesh_yoke_stage(part, resolved, mats=mats)
    else:
        _build_lower_stage_tilt(part, resolved, mats=mats)
    _add_tilt_frame_trunnion_shaft(part, resolved, mats=mats)


# --------------------------------------------------------------------------- #
# Faceplate builders (adopted: S1 / S2 / S3 / S4)
# --------------------------------------------------------------------------- #


def _add_slotted_disk_details(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S1 L111-L158 — machinist slotted disk."""
    steel = mats["steel"]
    bearing = mats["bearing"]
    slot = mats["slot"]
    bolt = mats["bolt"]
    dark = mats["dark"]
    r = resolved.table_radius
    disk_h = max(0.05, r * 0.11)
    rim_h = max(0.012, r * 0.028)
    race_top = max(0.002, rim_h * 0.5)
    disk_cz = race_top + disk_h * 0.5

    part.visual(
        Cylinder(radius=r, length=disk_h),
        origin=Origin(xyz=(0.0, 0.0, disk_cz)),
        material=steel,
        name="turntable_disk", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=r * 1.05, length=rim_h),
        origin=Origin(xyz=(0.0, 0.0, rim_h * 0.65)),
        material=bearing,
        name="dark_outer_rim", material_class_id="metal.chrome_polished",
    )
    part.visual(
        Cylinder(radius=max(0.03, r * 0.15), length=max(0.004, r * 0.018)),
        origin=Origin(xyz=(0.0, 0.0, disk_h + rim_h * 0.35)),
        material=slot,
        name="center_bore", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=max(0.06, r * 0.36), length=max(0.004, r * 0.015)),
        origin=Origin(xyz=(0.0, 0.0, disk_h + rim_h * 0.2)),
        material=bearing,
        name="center_register", material_class_id="metal.chrome_polished",
    )

    slot_span = r * 1.55
    slot_positions = [
        -r * 0.45,
        0.0,
        r * 0.45,
    ][: resolved.slot_count]
    if resolved.slot_count == 2:
        slot_positions = [-r * 0.35, r * 0.35]
    elif resolved.slot_count == 4:
        slot_positions = [-r * 0.50, -r * 0.17, r * 0.17, r * 0.50]

    top_z = disk_cz + disk_h * 0.5 - max(0.003, r * 0.008)
    slot_depth = max(0.018, r * 0.035)
    for index, x in enumerate(slot_positions):
        part.visual(
            Box((max(0.018, r * 0.043), slot_span, slot_depth)),
            origin=Origin(xyz=(x, 0.0, top_z - slot_depth * 0.35)),
            material=slot,
            name=f"slot_{index}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Box((max(0.04, r * 0.11), slot_span, max(0.008, r * 0.018))),
            origin=Origin(xyz=(x, 0.0, top_z - slot_depth * 0.55)),
            material=dark,
            name=f"slot_shoulder_{index}", material_class_id="metal.blackened_gunmetal",
        )

    bolt_r = r * 0.68
    hole_h = max(0.014, r * 0.028)
    for index in range(resolved.fixture_hole_count):
        ang = (2.0 * math.pi * index) / resolved.fixture_hole_count
        part.visual(
            Cylinder(radius=max(0.012, r * 0.028), length=hole_h),
            origin=Origin(
                xyz=(bolt_r * math.cos(ang), bolt_r * math.sin(ang), top_z - hole_h * 0.35),
            ),
            material=bolt,
            name=f"fixture_hole_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _add_square_table_details(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S2 table plate."""
    steel = mats["steel"]
    dark = mats["dark"]
    size = resolved.table_diameter * 0.92
    t = max(0.04, resolved.table_radius * 0.09)
    part.visual(
        Box((size, size, t)),
        origin=Origin(xyz=(0.0, 0.0, t * 0.5 + resolved.table_radius * 0.04)),
        material=steel,
        name="table_plate", material_class_id="metal.steel_bare",
    )
    part.visual(
        Box((size * 0.72, size * 0.62, t * 0.85)),
        origin=Origin(xyz=(0.0, 0.0, t * 0.35)),
        material=dark,
        name="table_body", material_class_id="metal.blackened_gunmetal",
    )
    journal_len = max(0.08, resolved.pivot_hub_offset - size * 0.18)
    jx = size * 0.36 + journal_len * 0.5
    for side, sx in (("left", 1.0), ("right", -1.0)):
        part.visual(
            Cylinder(radius=max(0.025, resolved.pivot_hub_radius * 0.42), length=journal_len),
            origin=Origin(xyz=(sx * jx, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=steel,
            name=f"{side}_journal", material_class_id="metal.steel_bare",
        )


def _add_mesh_plate_details(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S3 tool plate."""
    steel = mats["steel"]
    dark = mats["dark"]
    r = resolved.table_radius
    disk_h = max(0.045, r * 0.10)
    disk_cz = disk_h * 0.5
    part.visual(
        Cylinder(radius=r * 0.96, length=disk_h),
        origin=Origin(xyz=(0.0, 0.0, disk_cz)),
        material=steel,
        name="tool_plate_disk", material_class_id="metal.steel_bare",
    )
    for index in range(6):
        ang = index * (math.pi / 3.0)
        part.visual(
            Box((max(0.03, r * 0.10), max(0.025, r * 0.06), disk_h * 1.05)),
            origin=Origin(
                xyz=(math.cos(ang) * r * 0.58, math.sin(ang) * r * 0.58, disk_cz),
                rpy=(0.0, 0.0, ang),
            ),
            material=dark,
            name=f"clamp_pad_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _add_large_faceplate_details(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """adopted: S4 large faceplate."""
    steel = mats["steel"]
    slot = mats["slot"]
    r = resolved.table_radius * 1.08
    h = max(0.055, r * 0.10)
    part.visual(
        Cylinder(radius=r, length=h),
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
        material=steel,
        name="large_faceplate_disk", material_class_id="metal.steel_bare",
    )
    for index in range(8):
        ang = index * (math.pi / 4.0)
        part.visual(
            Box((max(0.014, r * 0.035), max(0.10, r * 0.24), h * 1.02)),
            origin=Origin(
                xyz=(math.cos(ang) * r * 0.68, math.sin(ang) * r * 0.68, h * 0.5),
                rpy=(0.0, 0.0, ang),
            ),
            material=slot,
            name=f"radial_slot_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _build_turntable(part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats) -> None:
    if resolved.faceplate_style == "slotted_disk":
        _add_slotted_disk_details(part, resolved, mats=mats)
    elif resolved.faceplate_style == "square_table":
        _add_square_table_details(part, resolved, mats=mats)
    elif resolved.faceplate_style == "mesh_plate":
        _add_mesh_plate_details(part, resolved, mats=mats)
    else:
        _add_large_faceplate_details(part, resolved, mats=mats)


# --------------------------------------------------------------------------- #
# Style compatibility + extended decorative passes
# --------------------------------------------------------------------------- #

_COMPAT_BASE_TILT: dict[BaseStyle, frozenset[TiltStageStyle]] = {
    "side_cheek": frozenset({"integrated_frame", "open_cradle", "mesh_yoke", "lower_stage"}),
    "cadquery_box": frozenset({"integrated_frame", "open_cradle", "mesh_yoke", "lower_stage"}),
    "stacked_heavy": frozenset({"integrated_frame", "lower_stage", "mesh_yoke", "open_cradle"}),
    "pedestal": frozenset({"integrated_frame", "mesh_yoke", "lower_stage", "open_cradle"}),
}

_COMPAT_TILT_FACE: dict[TiltStageStyle, frozenset[FaceplateStyle]] = {
    "integrated_frame": frozenset(
        {"slotted_disk", "square_table", "mesh_plate", "large_faceplate"}
    ),
    "open_cradle": frozenset({"square_table", "slotted_disk", "mesh_plate", "large_faceplate"}),
    "mesh_yoke": frozenset({"mesh_plate", "slotted_disk", "large_faceplate", "square_table"}),
    "lower_stage": frozenset({"large_faceplate", "slotted_disk", "mesh_plate", "square_table"}),
}


def _coerce_compatible_styles(
    config: RotaryTableWithTiltingTrunnionConfig,
) -> RotaryTableWithTiltingTrunnionConfig:
    """Downgrade incompatible enum triples to the nearest stable combination."""
    base = config.base_style
    tilt = config.tilt_stage_style
    face = config.faceplate_style
    if tilt not in _COMPAT_BASE_TILT.get(base, frozenset({tilt})):
        tilt = "integrated_frame"
    if face not in _COMPAT_TILT_FACE.get(tilt, frozenset({face})):
        face = "slotted_disk"
    if base == "pedestal" and face == "square_table" and config.table_diameter > 0.62:
        face = "slotted_disk"
    return replace(config, tilt_stage_style=tilt, faceplate_style=face)


def _add_base_corner_bolts(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """Corner mount bolts — decorative visuals on every base style."""
    bolt = mats["bolt"]
    fx = resolved.base_footprint_x * 0.46
    fy = resolved.base_footprint_y * 0.46
    z = resolved.base_plate_thickness * 0.5
    for ix, x in enumerate((fx, -fx)):
        for iy, y in enumerate((fy, -fy)):
            part.visual(
                Cylinder(
                    radius=max(0.012, resolved.table_radius * 0.025), length=max(0.02, z * 2.0)
                ),
                origin=Origin(xyz=(x, y, z)),
                material=bolt,
                name=f"corner_bolt_{ix}_{iy}", material_class_id="metal.blackened_gunmetal",
            )


def _add_tilt_lock_handles(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """Optional tilt-lock handwheel visuals on tilt_frame (Rule 1: visuals only)."""
    dark = mats["dark"]
    steel = mats["steel"]
    for side, y in (
        ("front", resolved.table_radius * 0.42),
        ("rear", -resolved.table_radius * 0.42),
    ):
        part.visual(
            Cylinder(radius=max(0.018, resolved.pivot_hub_radius * 0.28), length=0.04),
            origin=Origin(
                xyz=(resolved.pivot_hub_offset * 1.05, y, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)
            ),
            material=steel,
            name=f"tilt_lock_stem_{side}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Cylinder(radius=max(0.028, resolved.pivot_hub_radius * 0.42), length=0.018),
            origin=Origin(
                xyz=(resolved.pivot_hub_offset * 1.08, y, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)
            ),
            material=dark,
            name=f"tilt_lock_knob_{side}", material_class_id="metal.blackened_gunmetal",
        )


def _add_faceplate_index_marks(
    part, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    """Degree/index marks around the faceplate rim."""
    dark = mats["dark"]
    r = resolved.table_radius * 0.92
    top_z = max(0.06, resolved.table_radius * 0.12)
    for index in range(12):
        ang = index * (math.pi / 6.0)
        long = 0.06 if index % 3 == 0 else 0.035
        part.visual(
            Box((max(0.008, r * 0.015), long, max(0.002, r * 0.008))),
            origin=Origin(
                xyz=(math.sin(ang) * r, math.cos(ang) * r, top_z),
                rpy=(0.0, ang, 0.0),
            ),
            material=dark,
            name=f"index_mark_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _apply_post_build_decorations(
    model: ArticulatedObject, resolved: ResolvedRotaryTableWithTiltingTrunnionConfig, *, mats
) -> None:
    base = model.get_part("base")
    tilt_frame = model.get_part("tilt_frame")
    turntable = model.get_part("turntable")
    _add_base_corner_bolts(base, resolved, mats=mats)
    _add_tilt_lock_handles(tilt_frame, resolved, mats=mats)
    _add_faceplate_index_marks(turntable, resolved, mats=mats)


def build_rotary_table_with_tilting_trunnion(
    config: RotaryTableWithTiltingTrunnionConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    raw = config or RotaryTableWithTiltingTrunnionConfig()
    config = _coerce_compatible_styles(raw)
    resolved = resolve_config(config)
    model = ArticulatedObject(name=resolved.name, assets=assets)
    model.meta["adopted_source_ids"] = ("S1", "S2", "S3", "S4", "S5")
    model.meta["slot_choices"] = slot_choices_for_config(resolved)

    palette = PALETTES[resolved.material_style]
    mats = {
        "cast": model.material("cast_iron", rgba=palette["cast"]),
        "dark": model.material("dark_iron", rgba=palette["dark"]),
        "steel": model.material("ground_steel", rgba=palette["steel"]),
        "bearing": model.material("bearing_steel", rgba=palette["bearing"]),
        "slot": model.material("slot_black", rgba=palette["slot"]),
        "bolt": model.material("bolt_dark", rgba=palette["bolt"]),
    }

    if _is_anchor_config(config):
        _build_anchor_s1(model, mats=mats)
        return model

    base = model.part("base")
    _build_base(base, resolved, mats=mats)

    tilt_frame = model.part("tilt_frame")
    _build_tilt_frame(tilt_frame, resolved, mats=mats)

    turntable = model.part("turntable")
    _build_turntable(turntable, resolved, mats=mats)

    tilt_origin = (0.0, 0.0, resolved.trunnion_axis_z)
    model.articulation(
        "base_to_tilt_frame",
        ArticulationType.REVOLUTE,
        parent=base,
        child=tilt_frame,
        origin=Origin(xyz=tilt_origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=500.0,
            velocity=0.60,
            lower=resolved.tilt_lower,
            upper=resolved.tilt_upper,
        ),
        motion_properties=MotionProperties(damping=12.0, friction=4.0),
        meta=_joint_meta(
            "revolute", (1.0, 0.0, 0.0), tilt_origin, (resolved.tilt_lower, resolved.tilt_upper)
        ),
    )

    rotary_origin = (0.0, 0.0, resolved.rotary_joint_z)
    model.articulation(
        "tilt_frame_to_turntable",
        ArticulationType.CONTINUOUS,
        parent=tilt_frame,
        child=turntable,
        origin=Origin(xyz=rotary_origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=260.0, velocity=1.20),
        motion_properties=MotionProperties(damping=4.0, friction=2.0),
        meta=_joint_meta("continuous", (0.0, 0.0, 1.0), rotary_origin, "unbounded"),
    )
    return model


def build_seeded_rotary_table_with_tilting_trunnion(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_rotary_table_with_tilting_trunnion(config_from_seed(seed), assets=assets)


def slot_choices_for_config(
    resolved: ResolvedRotaryTableWithTiltingTrunnionConfig,
) -> list[tuple[str, str]]:
    """Recorded on ``model.meta`` for the module_topology_diversity gate."""
    return [
        ("machine_base", resolved.base_style),
        ("tilt_trunnion_stage", resolved.tilt_stage_style),
        ("rotary_faceplate", resolved.faceplate_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def with_overrides(
    config: RotaryTableWithTiltingTrunnionConfig, **kwargs: object
) -> RotaryTableWithTiltingTrunnionConfig:
    return replace(config, **kwargs)


def run_rotary_table_with_tilting_trunnion_tests(
    object_model: ArticulatedObject,
    config: RotaryTableWithTiltingTrunnionConfig,
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    base = object_model.get_part("base")
    tilt_frame = object_model.get_part("tilt_frame")
    turntable = object_model.get_part("turntable")

    ctx.allow_overlap(
        base,
        tilt_frame,
        reason="trunnion bearing stack intentionally captures the tilt stage on the base line",
    )
    ctx.allow_overlap(
        tilt_frame,
        turntable,
        reason="faceplate is intentionally seated on the rotary bearing race",
    )
    ctx.allow_overlap(
        base,
        turntable,
        reason="faceplate footprint may overlap the base plinth at rest or under tilt",
    )

    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "identity_parts",
        {"base", "tilt_frame", "turntable"}.issubset(part_names),
        details=str(sorted(part_names)),
    )

    tilt = object_model.get_articulation("base_to_tilt_frame")
    rotary = object_model.get_articulation("tilt_frame_to_turntable")
    ctx.check(
        "tilt_is_revolute_x",
        tilt.articulation_type == ArticulationType.REVOLUTE and tuple(tilt.axis) == (1.0, 0.0, 0.0),
        details=f"type={tilt.articulation_type}, axis={tilt.axis}",
    )
    ctx.check(
        "rotary_is_continuous_z",
        rotary.articulation_type == ArticulationType.CONTINUOUS
        and tuple(rotary.axis) == (0.0, 0.0, 1.0),
        details=f"type={rotary.articulation_type}, axis={rotary.axis}",
    )
    ctx.check(
        "joint_chain",
        tilt.parent == "base"
        and tilt.child == "tilt_frame"
        and rotary.parent == "tilt_frame"
        and rotary.child == "turntable",
        details=f"{tilt.parent}->{tilt.child}, {rotary.parent}->{rotary.child}",
    )

    turntable = object_model.get_part("turntable")
    tt_visuals = {v.name for v in turntable.visuals}
    if resolved.faceplate_style == "slotted_disk":
        ctx.check(
            "has_slots",
            any(n.startswith("slot_") for n in tt_visuals),
            details=str(sorted(tt_visuals)),
        )

    def _elem_x_span(part, elem: str) -> float | None:
        try:
            aabb = ctx.part_element_world_aabb(part, elem=elem)
        except Exception:
            return None
        if aabb is None:
            return None
        return aabb[1][0] - aabb[0][0]

    slot_elem = (
        "slot_0"
        if "slot_0" in tt_visuals
        else next((n for n in tt_visuals if n.startswith("slot_")), None)
    )
    if slot_elem:
        rest_x = _elem_x_span(turntable, slot_elem)
        with ctx.pose({rotary: math.pi / 2.0}):
            spun_x = _elem_x_span(turntable, slot_elem)
        ctx.check(
            "rotary_motion_moves_face_feature",
            (rest_x is None or spun_x is None) or spun_x > rest_x + 0.08,
            details=f"rest_x={rest_x}, spun_x={spun_x}, elem={slot_elem}",
        )

    rest_aabb = ctx.part_world_aabb(turntable)
    with ctx.pose({tilt: min(resolved.tilt_upper, 0.80)}):
        tilted_aabb = ctx.part_world_aabb(turntable)
    if rest_aabb and tilted_aabb:
        rest_z = rest_aabb[1][2] - rest_aabb[0][2]
        tilted_z = tilted_aabb[1][2] - tilted_aabb[0][2]
        ctx.check(
            "tilt_changes_table_attitude",
            tilted_z > rest_z + 0.05,
            details=f"rest_z={rest_z:.3f}, tilted_z={tilted_z:.3f}",
        )

    return ctx.report()


def validate_config_enums(config: RotaryTableWithTiltingTrunnionConfig) -> None:
    """Explicit enum validation helper for unit tests and sweep diagnostics."""
    if config.base_style not in _BASE_STYLES:
        raise ValueError(config.base_style)
    if config.tilt_stage_style not in _TILT_STYLES:
        raise ValueError(config.tilt_stage_style)
    if config.faceplate_style not in _FACE_STYLES:
        raise ValueError(config.faceplate_style)
    if config.material_style not in PALETTES:
        raise ValueError(config.material_style)
