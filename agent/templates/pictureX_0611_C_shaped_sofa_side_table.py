# SPDX-License-Identifier: Apache-2.0

"""C-shaped sofa side tables and their host seating group (pictureX/0611).

The host is always the same: one sofa frame, N C-shaped side tables that slide
in along the seat, and the low front platform that slides toward the sofa.  Four
slots vary: the table frame topology (`table_frame`), the top plan
(`table_top`), the table base (`base_form`) and the seating body (`sofa_form`);
`side_table_count` is the multiplicity applied to `table_frame`.

Source evidence lives in
`articraft_template_authoring/source_maps/pictureX_0611_C_shaped_sofa_side_table.md`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mesh_from_cadquery,
    multiplicity_slot,
)

TableFrame = Literal["c_bracket", "loop_frame", "l_bracket", "u_straddle"]
TableTop = Literal["rect_top", "round_top", "kidney_top"]
BaseForm = Literal["sled_foot", "caster_base", "height_column"]
SofaForm = Literal["two_seat_sofa", "backless_bench", "daybed_chaise"]

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "table_frame",
            ("c_bracket", "loop_frame", "l_bracket", "u_straddle"),
            role="source-backed side-table frame topology",
        ),
        component_slot(
            "table_top",
            ("rect_top", "round_top", "kidney_top"),
            role="source-backed table top plan",
        ),
        component_slot(
            "base_form",
            ("sled_foot", "caster_base", "height_column"),
            role="source-backed table base",
        ),
        component_slot(
            "sofa_form",
            ("two_seat_sofa", "backless_bench", "daybed_chaise"),
            role="source-backed seating body",
        ),
        multiplicity_slot(
            "side_table_count",
            (1, 2),
            role="number of C-shaped side tables on the group",
            item_slot="table_frame",
        ),
    )
)

_TUBE = 0.030
_PLINTH_H = 0.130
_TRACK_H = 0.012
_FLOOR_Z = _TRACK_H + 0.0008


@dataclass(frozen=True)
class Config:
    table_frame: TableFrame = "c_bracket"
    table_top: TableTop = "rect_top"
    base_form: BaseForm = "sled_foot"
    sofa_form: SofaForm = "two_seat_sofa"
    side_table_count: int = 1
    sofa_width_m: float = 1.45
    sofa_depth_m: float = 0.90
    seat_height_m: float = 0.38
    table_top_width_m: float = 0.42
    table_reach_m: float = 0.30
    name: str = "c_shaped_sofa_side_table"


@dataclass(frozen=True)
class ResolvedConfig:
    table_frame: TableFrame
    table_top: TableTop
    base_form: BaseForm
    sofa_form: SofaForm
    side_table_count: int
    sofa_width_m: float
    sofa_depth_m: float
    seat_height_m: float
    table_top_width_m: float
    table_reach_m: float
    name: str
    # derived
    seat_top_m: float
    arm_height_m: float
    arm_top_m: float
    deck_depth_m: float
    table_height_m: float
    table_x_m: float
    table_stroke_m: float
    platform_y_m: float
    platform_stroke_m: float


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0611_C5A0_F4A2)
    return Config(
        table_frame=choices["table_frame"],
        table_top=choices["table_top"],
        base_form=choices["base_form"],
        sofa_form=choices["sofa_form"],
        side_table_count=int(choices["side_table_count"]),
        sofa_width_m=round(rng.uniform(1.16, 1.74), 5),
        sofa_depth_m=round(rng.uniform(0.78, 1.02), 5),
        seat_height_m=round(rng.uniform(0.33, 0.45), 5),
        table_top_width_m=round(rng.uniform(0.32, 0.50), 5),
        table_reach_m=round(rng.uniform(0.24, 0.38), 5),
        name=f"c_shaped_sofa_side_table_seed_{seed}",
    )


def _require_range(name: str, value: float, minimum: float, maximum: float) -> float:
    value = float(value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be in [{minimum}, {maximum}], got {value}")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "table_frame": config.table_frame,
            "table_top": config.table_top,
            "base_form": config.base_form,
            "sofa_form": config.sofa_form,
            "side_table_count": int(config.side_table_count),
        }
    )
    width = _require_range("sofa_width_m", config.sofa_width_m, 1.10, 1.80)
    depth = _require_range("sofa_depth_m", config.sofa_depth_m, 0.75, 1.05)
    seat_h = _require_range("seat_height_m", config.seat_height_m, 0.32, 0.46)
    top_w = _require_range("table_top_width_m", config.table_top_width_m, 0.30, 0.52)
    reach = _require_range("table_reach_m", config.table_reach_m, 0.22, 0.40)
    count = int(config.side_table_count)

    cushion_t = 0.115
    seat_top = seat_h + cushion_t
    arm_h = {"two_seat_sofa": 0.150, "daybed_chaise": 0.160, "backless_bench": 0.0}[
        config.sofa_form
    ]
    arm_top = seat_top + arm_h
    deck_depth = depth * (1.28 if config.sofa_form == "daybed_chaise" else 1.0)
    # The top clears the cushions, and the arms too when the host has them.
    table_h = arm_top + 0.055
    # Each table parks just outside the sofa end and slides in over the seat.
    table_x = 0.5 * width + 0.5 * top_w + 0.030
    return ResolvedConfig(
        table_frame=config.table_frame,
        table_top=config.table_top,
        base_form=config.base_form,
        sofa_form=config.sofa_form,
        side_table_count=count,
        sofa_width_m=width,
        sofa_depth_m=depth,
        seat_height_m=seat_h,
        table_top_width_m=top_w,
        table_reach_m=reach,
        name=config.name,
        seat_top_m=seat_top,
        arm_height_m=arm_h,
        arm_top_m=arm_top,
        deck_depth_m=deck_depth,
        table_height_m=table_h,
        table_x_m=table_x,
        table_stroke_m=reach,
        platform_y_m=-0.5 * deck_depth - 0.300,
        platform_stroke_m=0.120,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, object]:
    return {
        "table_frame": config.table_frame,
        "table_top": config.table_top,
        "base_form": config.base_form,
        "sofa_form": config.sofa_form,
        "side_table_count": int(config.side_table_count),
    }


def slot_choices_for_seed(seed: int) -> dict[str, object]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject) -> dict[str, object]:
    return {
        "steel": model.material("cst_black_steel", rgba=(0.11, 0.115, 0.12, 1.0)),
        "oak": model.material("cst_light_oak", rgba=(0.79, 0.61, 0.42, 1.0)),
        "fabric": model.material("cst_grey_fabric", rgba=(0.60, 0.61, 0.62, 1.0)),
        "deck": model.material("cst_deck_fabric", rgba=(0.52, 0.53, 0.54, 1.0)),
        "wheel": model.material("cst_wheel_black", rgba=(0.07, 0.07, 0.08, 1.0)),
    }


# ---------------------------------------------------------------------------
# table top plans
# ---------------------------------------------------------------------------


def _table_top_rect_top_build(r: ResolvedConfig) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(r.table_top_width_m, r.table_top_width_m * 0.78, 0.026)
        .edges("|Z")
        .fillet(0.018)
    )


def _table_top_round_top_build(r: ResolvedConfig) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(0.5 * r.table_top_width_m)
        .extrude(0.013, both=True)
    )


def _table_top_kidney_top_build(r: ResolvedConfig) -> cq.Workplane:
    w = r.table_top_width_m
    slab = (
        cq.Workplane("XY").box(w, w * 0.80, 0.026).edges("|Z").fillet(0.030)
    )
    bite = (
        cq.Workplane("XY")
        .circle(w * 0.44)
        .extrude(0.040, both=True)
        .translate((0.0, -0.5 * w * 0.80 - w * 0.36, 0.0))
    )
    return slab.cut(bite)


_TOP_BUILDERS = {
    "rect_top": _table_top_rect_top_build,
    "round_top": _table_top_round_top_build,
    "kidney_top": _table_top_kidney_top_build,
}


# ---------------------------------------------------------------------------
# table frames
# ---------------------------------------------------------------------------


def _bar(length: float, width: float, height: float) -> cq.Workplane:
    return cq.Workplane("XY").box(length, width, height)


def _table_frame_c_bracket_build(r: ResolvedConfig, side: float) -> cq.Workplane:
    """Upright at the outer edge, a return foot under the seat, a top rail."""

    h = r.table_height_m
    reach = r.table_reach_m
    upright = _bar(_TUBE, _TUBE, h).translate((side * (reach - 0.5 * _TUBE), 0.0, 0.5 * h))
    foot = _bar(reach + _TUBE, _TUBE * 1.6, 0.020).translate(
        (side * 0.5 * (reach - _TUBE) + side * 0.5 * _TUBE, 0.0, 0.010)
    )
    rail = _bar(reach + _TUBE, _TUBE, 0.022).translate(
        (side * 0.5 * (reach - _TUBE) + side * 0.5 * _TUBE, 0.0, h - 0.011)
    )
    return upright.union(foot).union(rail)


def _table_frame_loop_frame_build(r: ResolvedConfig, side: float) -> cq.Workplane:
    """Closed loop standing outside the sofa, with a real slot and a top rail."""

    h = r.table_height_m
    reach = r.table_reach_m
    loop_w = min(0.150, reach * 0.55)
    cx = side * (reach - 0.5 * loop_w)
    outer = _bar(loop_w, _TUBE * 1.2, h).translate((cx, 0.0, 0.5 * h))
    window = _bar(loop_w - 2.0 * _TUBE, _TUBE * 2.0, h - 2.0 * _TUBE).translate(
        (cx, 0.0, 0.5 * h)
    )
    slot = _bar(loop_w * 0.34, _TUBE * 2.0, 0.014).translate(
        (cx, 0.0, h - _TUBE - 0.024)
    )
    rail = _bar(reach + _TUBE, _TUBE, 0.022).translate(
        (side * 0.5 * (reach - _TUBE) + side * 0.5 * _TUBE, 0.0, h - 0.011)
    )
    foot = _bar(reach + _TUBE, _TUBE * 1.6, 0.020).translate(
        (side * 0.5 * (reach - _TUBE) + side * 0.5 * _TUBE, 0.0, 0.010)
    )
    return outer.cut(window).cut(slot).union(rail).union(foot)


def _table_frame_l_bracket_build(r: ResolvedConfig, side: float) -> cq.Workplane:
    """Single upright on a weighted pad; no return foot under the seat."""

    h = r.table_height_m
    reach = r.table_reach_m
    upright = _bar(_TUBE, _TUBE, h).translate((side * (reach - 0.5 * _TUBE), 0.0, 0.5 * h))
    pad = _bar(_TUBE * 3.4, _TUBE * 3.0, 0.024).translate(
        (side * (reach - 0.5 * _TUBE), 0.0, 0.012)
    )
    rail = _bar(reach + _TUBE, _TUBE, 0.022).translate(
        (side * 0.5 * (reach - _TUBE) + side * 0.5 * _TUBE, 0.0, h - 0.011)
    )
    return upright.union(pad).union(rail)


def _table_frame_u_straddle_build(r: ResolvedConfig, side: float) -> cq.Workplane:
    """A U in plan: the second upright stands clear in front of the seat."""

    h = r.table_height_m
    reach = r.table_reach_m
    front_y = 0.5 * r.deck_depth_m + 0.070
    body: cq.Workplane | None = None
    for offset_x, offset_y in ((side * (reach - 0.5 * _TUBE), 0.0), (0.0, front_y)):
        leg = _bar(_TUBE, _TUBE, h).translate((offset_x, offset_y, 0.5 * h))
        foot = _bar(_TUBE * 1.6, _TUBE * 1.6, 0.020).translate(
            (offset_x, offset_y, 0.010)
        )
        piece = leg.union(foot)
        body = piece if body is None else body.union(piece)
    rail_x = _bar(reach + _TUBE, _TUBE, 0.022).translate(
        (side * 0.5 * (reach - _TUBE) + side * 0.5 * _TUBE, 0.0, h - 0.011)
    )
    rail_y = _bar(_TUBE, abs(front_y) + _TUBE, 0.022).translate(
        (0.0, 0.5 * front_y, h - 0.011)
    )
    assert body is not None
    return body.union(rail_x).union(rail_y)


_FRAME_BUILDERS = {
    "c_bracket": _table_frame_c_bracket_build,
    "loop_frame": _table_frame_loop_frame_build,
    "l_bracket": _table_frame_l_bracket_build,
    "u_straddle": _table_frame_u_straddle_build,
}

_FRAME_HAS_UNDER_FOOT = {
    "c_bracket": True,
    "loop_frame": True,
    "l_bracket": False,
    "u_straddle": True,
}


# ---------------------------------------------------------------------------
# table base
# ---------------------------------------------------------------------------


def _base_form_sled_foot_build(table, r, mats, *, prefix: str, side: float) -> None:
    table.visual(
        Box((_TUBE * 2.6, _TUBE * 2.8, 0.016)),
        origin=Origin(xyz=(side * (r.table_reach_m - 0.5 * _TUBE), 0.0, 0.008)),
        material=mats["steel"],
        name=f"{prefix}__sled_pad", material_class_id="metal.blackened_gunmetal",
    )


def _base_form_caster_base_build(table, r, mats, *, prefix: str, side: float) -> None:
    hub_x = side * (r.table_reach_m - 0.5 * _TUBE)
    table.visual(
        Box((_TUBE * 2.4, _TUBE * 2.6, 0.014)),
        origin=Origin(xyz=(hub_x, 0.0, 0.049)),
        material=mats["steel"],
        name=f"{prefix}__caster_plate", material_class_id="metal.blackened_gunmetal",
    )
    for index, (dx, dy) in enumerate(((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))):
        table.visual(
            Box((0.014, 0.020, 0.030)),
            origin=Origin(
                xyz=(hub_x + dx * _TUBE * 0.80, dy * _TUBE * 0.80, 0.042)
            ),
            material=mats["steel"],
            name=f"{prefix}__caster_yoke_{index}", material_class_id="metal.blackened_gunmetal",
        )
        table.visual(
            Cylinder(radius=0.026, length=0.016),
            origin=Origin(
                xyz=(hub_x + dx * _TUBE * 0.80, dy * _TUBE * 0.80, 0.026),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["wheel"],
            name=f"{prefix}__caster_wheel_{index}", material_class_id="rubber.smooth_plain",
        )


def _base_form_height_column_build(table, r, mats, *, prefix: str, side: float) -> None:
    hub_x = side * (r.table_reach_m - 0.5 * _TUBE)
    table.visual(
        mesh_from_cadquery(
            _column_sleeve_shape(r.table_height_m * 0.44),
            f"{prefix}__column_sleeve",
            tolerance=0.0010,
        ),
        origin=Origin(xyz=(hub_x, 0.0, r.table_height_m * 0.30)),
        material=mats["steel"],
        name=f"{prefix}__height_sleeve", material_class_id="metal.blackened_gunmetal",
    )
    table.visual(
        Box((_TUBE * 2.8, _TUBE * 3.0, 0.018)),
        origin=Origin(xyz=(hub_x, 0.0, 0.009)),
        material=mats["steel"],
        name=f"{prefix}__column_foot", material_class_id="metal.blackened_gunmetal",
    )


def _column_sleeve_shape(height: float) -> cq.Workplane:
    sleeve = cq.Workplane("XY").box(_TUBE * 1.7, _TUBE * 1.7, height)
    bore = cq.Workplane("XY").box(_TUBE - 0.002, _TUBE - 0.002, height + 0.02)
    return sleeve.cut(bore)


_BASE_BUILDERS = {
    "sled_foot": _base_form_sled_foot_build,
    "caster_base": _base_form_caster_base_build,
    "height_column": _base_form_height_column_build,
}


# ---------------------------------------------------------------------------
# sofa bodies
# ---------------------------------------------------------------------------


def _add_floor_track(sofa, r, mats) -> None:
    """Floor rail the C-table feet run on, so the tables are always carried."""

    span = 2.0 * (r.table_x_m + r.table_reach_m) + 0.100
    sofa.visual(
        Box((span, 0.034, _TRACK_H)),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * _TRACK_H)),
        material=mats["steel"],
        name="sofa__frame__floor_track", material_class_id="metal.blackened_gunmetal",
    )
    for index, sx in enumerate((-1.0, 1.0)):
        sofa.visual(
            Box((0.034, r.deck_depth_m - 0.060, _TRACK_H)),
            origin=Origin(
                xyz=(sx * (0.5 * r.sofa_width_m - 0.030), 0.0, 0.5 * _TRACK_H)
            ),
            material=mats["steel"],
            name=f"sofa__frame__track_tie_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _add_plinth(sofa, r, mats, *, width: float, depth: float) -> None:
    """Open steel underframe: the table foot slides beneath it."""

    for index, sy in enumerate((-1.0, 1.0)):
        sofa.visual(
            Box((width, 0.040, 0.036)),
            origin=Origin(xyz=(0.0, sy * (0.5 * depth - 0.030), _PLINTH_H - 0.018)),
            material=mats["steel"],
            name=f"sofa__frame__rail_{index}", material_class_id="metal.blackened_gunmetal",
        )
    for index, (sx, sy) in enumerate(
        ((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))
    ):
        leg_h = r.seat_height_m - 0.030
        sofa.visual(
            Box((0.036, 0.036, leg_h)),
            origin=Origin(
                xyz=(
                    sx * (0.5 * width - 0.030),
                    sy * (0.5 * depth - 0.030),
                    0.5 * leg_h,
                )
            ),
            material=mats["steel"],
            name=f"sofa__frame__leg_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _add_seat_deck(sofa, r, mats, *, width: float, depth: float, cushions: int) -> None:
    sofa.visual(
        Box((width, depth, 0.030)),
        origin=Origin(xyz=(0.0, 0.0, r.seat_height_m - 0.015)),
        material=mats["steel"],
        name="sofa__frame__seat_deck", material_class_id="metal.blackened_gunmetal",
    )
    span = (width - 0.030) / cushions
    for index in range(cushions):
        sofa.visual(
            mesh_from_cadquery(
                _cushion_shape(span - 0.018, depth - 0.030, 0.115),
                f"sofa__cushion_{index}",
                tolerance=0.0016,
            ),
            origin=Origin(
                xyz=(
                    -0.5 * width + 0.015 + span * (index + 0.5),
                    0.0,
                    r.seat_height_m + 0.0575,
                )
            ),
            material=mats["fabric"],
            name=f"sofa__frame__seat_cushion_{index}", material_class_id=("fabric.jacquard" if r.sofa_form == "two_seat_sofa" else "fabric.upholstery_plain"),
        )


def _cushion_shape(width: float, depth: float, height: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(width, depth, height)
        .edges("|Z")
        .fillet(0.022)
        .edges(">Z")
        .fillet(0.014)
    )


def _sofa_form_two_seat_sofa_build(model, r, mats):
    sofa = model.part("sofa__frame", meta={"role": "sofa_frame", "candidate": r.sofa_form})
    width, depth = r.sofa_width_m, r.sofa_depth_m
    _add_floor_track(sofa, r, mats)
    _add_plinth(sofa, r, mats, width=width, depth=depth)
    _add_seat_deck(sofa, r, mats, width=width, depth=depth, cushions=2)
    sofa.visual(
        mesh_from_cadquery(
            _cushion_shape(width - 0.030, 0.140, r.arm_height_m + 0.010),
            "sofa__back_cushion",
            tolerance=0.0016,
        ),
        origin=Origin(
            xyz=(
                0.0,
                0.5 * depth - 0.075,
                r.seat_top_m + 0.5 * (r.arm_height_m + 0.010),
            )
        ),
        material=mats["fabric"],
        name="sofa__frame__back_cushion", material_class_id="fabric.upholstery_plain",
    )
    for index, sx in enumerate((-1.0, 1.0)):
        sofa.visual(
            mesh_from_cadquery(
                _cushion_shape(0.110, depth - 0.060, r.arm_height_m),
                f"sofa__arm_{index}",
                tolerance=0.0016,
            ),
            origin=Origin(
                xyz=(
                    sx * (0.5 * width - 0.055),
                    -0.020,
                    r.seat_top_m + 0.5 * r.arm_height_m,
                )
            ),
            material=mats["fabric"],
            name=f"sofa__frame__arm_{index}", material_class_id="fabric.upholstery_plain",
        )
    return sofa


def _sofa_form_backless_bench_build(model, r, mats):
    sofa = model.part("sofa__frame", meta={"role": "sofa_frame", "candidate": r.sofa_form})
    width, depth = r.sofa_width_m, r.sofa_depth_m
    _add_floor_track(sofa, r, mats)
    _add_plinth(sofa, r, mats, width=width, depth=depth)
    _add_seat_deck(sofa, r, mats, width=width, depth=depth, cushions=3)
    return sofa


def _sofa_form_daybed_chaise_build(model, r, mats):
    sofa = model.part("sofa__frame", meta={"role": "sofa_frame", "candidate": r.sofa_form})
    width, depth = r.sofa_width_m, r.deck_depth_m
    _add_floor_track(sofa, r, mats)
    _add_plinth(sofa, r, mats, width=width, depth=depth)
    _add_seat_deck(sofa, r, mats, width=width, depth=depth, cushions=2)
    sofa.visual(
        mesh_from_cadquery(
            _cushion_shape(0.110, depth - 0.060, r.arm_height_m),
            "sofa__single_arm",
            tolerance=0.0016,
        ),
        origin=Origin(
            xyz=(-(0.5 * width - 0.055), 0.0, r.seat_top_m + 0.5 * r.arm_height_m)
        ),
        material=mats["fabric"],
        name="sofa__frame__arm_0", material_class_id="fabric.upholstery_plain",
    )
    sofa.visual(
        mesh_from_cadquery(
            _cushion_shape(width * 0.46, 0.130, r.arm_height_m + 0.010),
            "sofa__chaise_back",
            tolerance=0.0016,
        ),
        origin=Origin(
            xyz=(
                -width * 0.22,
                0.5 * depth - 0.070,
                r.seat_top_m + 0.5 * (r.arm_height_m + 0.010),
            )
        ),
        material=mats["fabric"],
        name="sofa__frame__back_cushion", material_class_id="fabric.upholstery_plain",
    )
    return sofa


_SOFA_BUILDERS = {
    "two_seat_sofa": _sofa_form_two_seat_sofa_build,
    "backless_bench": _sofa_form_backless_bench_build,
    "daybed_chaise": _sofa_form_daybed_chaise_build,
}


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def _build_side_tables(model, r, mats, sofa):
    tables = []
    sides = (1.0,) if r.side_table_count == 1 else (1.0, -1.0)
    for index, side in enumerate(sides):
        prefix = f"table_frame__{r.table_frame}__table_{index}"
        table = model.part(prefix, meta={"role": "side_table", "candidate": r.table_frame})
        table.visual(
            mesh_from_cadquery(
                _FRAME_BUILDERS[r.table_frame](r, side), f"{prefix}_frame", tolerance=0.0016
            ),
            material=mats["steel"],
            name=f"{prefix}__frame", material_class_id="metal.blackened_gunmetal",
        )
        table.visual(
            mesh_from_cadquery(
                _TOP_BUILDERS[r.table_top](r), f"{prefix}_top", tolerance=0.0016
            ),
            origin=Origin(xyz=(0.0, 0.0, r.table_height_m + 0.013)),
            material=mats["oak"],
            name=f"{prefix}__top", material_class_id="wood.oak",
        )
        _BASE_BUILDERS[r.base_form](table, r, mats, prefix=prefix, side=side)
        model.articulation(
            f"{prefix}__slide",
            ArticulationType.PRISMATIC,
            parent=sofa,
            child=table,
            origin=Origin(xyz=(side * r.table_x_m, 0.0, _FLOOR_Z)),
            axis=(-side, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=200.0, velocity=0.3, lower=0.0, upper=r.table_stroke_m
            ),
            meta={"mechanism": "C table sliding in over the seat"},
        )
        tables.append(table)
    return tables


def _build_front_platform(model, r, mats, sofa):
    platform = model.part("platform__front", meta={"role": "front_platform"})
    width = r.sofa_width_m * 0.86
    depth = 0.34
    top_z = r.seat_height_m - 0.062
    guide_z = r.seat_height_m - 0.045
    runner_x = min(r.sofa_width_m * 0.5 - 0.100, r.sofa_width_m * 0.43 - 0.034)
    runner_len = r.deck_depth_m * 0.86
    for index, sx in enumerate((-1.0, 1.0)):
        sofa.visual(
            Box((0.024, runner_len, 0.030)),
            origin=Origin(xyz=(sx * runner_x, 0.0, guide_z)),
            material=mats["steel"],
            name=f"sofa__frame__deck_guide_{index}", material_class_id="metal.blackened_gunmetal",
        )
    platform.visual(
        Box((width, depth, 0.030)),
        origin=Origin(xyz=(0.0, 0.0, top_z - 0.015)),
        material=mats["oak"],
        name="platform__front__top", material_class_id="wood.oak",
    )
    # Two runner arms stay engaged under the sofa guides at every stroke.
    arm_len = r.deck_depth_m * 0.70
    for index, sx in enumerate((-1.0, 1.0)):
        platform.visual(
            Box((0.022, arm_len, 0.024)),
            origin=Origin(
                xyz=(
                    sx * runner_x,
                    0.5 * depth + 0.5 * arm_len - 0.020,
                    guide_z - 0.015 - 0.0008 - 0.012,
                )
            ),
            material=mats["steel"],
            name=f"platform__front__runner_{index}", material_class_id="metal.blackened_gunmetal",
        )
    for index, (sx, sy) in enumerate(
        ((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))
    ):
        platform.visual(
            Box((0.030, 0.030, top_z - 0.030)),
            origin=Origin(
                xyz=(
                    sx * (0.5 * width - 0.025),
                    sy * (0.5 * depth - 0.025),
                    0.5 * (top_z - 0.030),
                )
            ),
            material=mats["steel"],
            name=f"platform__front__leg_{index}", material_class_id="metal.blackened_gunmetal",
        )
    for index, sy in enumerate((-1.0, 1.0)):
        platform.visual(
            Box((width - 0.040, 0.026, 0.026)),
            origin=Origin(xyz=(0.0, sy * (0.5 * depth - 0.025), 0.062)),
            material=mats["steel"],
            name=f"platform__front__stretcher_{index}", material_class_id="metal.blackened_gunmetal",
        )
    model.articulation(
        "platform__front_slide",
        ArticulationType.PRISMATIC,
        parent=sofa,
        child=platform,
        origin=Origin(xyz=(0.0, r.platform_y_m, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=200.0, velocity=0.3, lower=0.0, upper=r.platform_stroke_m
        ),
        meta={"mechanism": "front platform sliding toward the sofa"},
    )
    return platform


def build_picturex_0611_c_shaped_sofa_side_table(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model)
    sofa = _SOFA_BUILDERS[r.sofa_form](model, r, mats)
    _build_side_tables(model, r, mats, sofa)
    _build_front_platform(model, r, mats, sofa)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/C-shaped_sofa_side_table"
    return model


def build_seeded_picturex_0611_c_shaped_sofa_side_table(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_picturex_0611_c_shaped_sofa_side_table(
        config_from_seed(seed), assets=assets
    )


def _centre(box):
    if box is None:
        return None
    return tuple(0.5 * (box[0][i] + box[1][i]) for i in range(3))


def run_picturex_0611_c_shaped_sofa_side_table_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()

    roles: dict[str | None, list] = {}
    for part in object_model.parts:
        roles.setdefault(part.meta.get("role"), []).append(part)

    ctx.check(
        "group keeps one sofa, N sliding C tables and one front platform",
        len(roles.get("sofa_frame", [])) == 1
        and len(roles.get("side_table", [])) == r.side_table_count
        and len(roles.get("front_platform", [])) == 1,
        details=(
            f"sofa={len(roles.get('sofa_frame', []))}, "
            f"tables={len(roles.get('side_table', []))}/{r.side_table_count}, "
            f"platform={len(roles.get('front_platform', []))}"
        ),
    )
    ctx.check(
        "domain choices are recorded",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )

    sofa = object_model.get_part("sofa__frame")
    tables = roles.get("side_table", [])
    ctx.check(
        "every side table belongs to the selected frame family",
        all(part.meta.get("candidate") == r.table_frame for part in tables),
    )

    for index, table in enumerate(tables):
        joint = object_model.get_articulation(f"{table.name}__slide")
        top = ctx.part_element_world_aabb(table, elem=f"{table.name}__top")
        parked = _centre(top)
        with ctx.pose({joint: joint.motion_limits.upper}):
            slid = _centre(ctx.part_element_world_aabb(table, elem=f"{table.name}__top"))
        ctx.check(
            f"side table {index} slides in over the seat",
            parked is not None
            and slid is not None
            and abs(slid[0]) < abs(parked[0]) - 0.5 * r.table_stroke_m
            and abs(slid[2] - parked[2]) < 0.002,
            details=f"parked={parked}, slid={slid}",
        )

    tops = [
        ctx.part_element_world_aabb(table, elem=f"{table.name}__top") for table in tables
    ]
    ctx.check(
        "the table top clears the seat cushions",
        all(box is not None for box in tops)
        and all(box[0][2] > r.seat_top_m + 0.020 for box in tops if box),
        details=f"seat_top={r.seat_top_m}, tops={[b[0][2] if b else None for b in tops]}",
    )

    platform = roles.get("front_platform", [None])[0]
    platform_box = (
        ctx.part_element_world_aabb(platform, elem="platform__front__top")
        if platform is not None
        else None
    )
    sofa_box = ctx.part_world_aabb(sofa)
    ctx.check(
        "the front platform sits low and in front of the sofa",
        platform_box is not None
        and sofa_box is not None
        and platform_box[1][2] < r.seat_top_m
        and _centre(platform_box)[1] < -0.5 * r.deck_depth_m,
        details=f"platform={platform_box}, sofa={sofa_box}",
    )

    slide = object_model.get_articulation("platform__front_slide")
    rest = _centre(platform_box)
    with ctx.pose({slide: slide.motion_limits.upper}):
        moved = _centre(
            ctx.part_element_world_aabb(platform, elem="platform__front__top")
        )
    ctx.check(
        "the front platform really slides toward the sofa",
        rest is not None
        and moved is not None
        and moved[1] > rest[1] + 0.5 * r.platform_stroke_m,
        details=f"rest={rest}, moved={moved}",
    )

    ctx.check(
        "the seating group keeps a plausible seated scale",
        0.30 < r.seat_height_m < 0.50 and 1.05 < r.sofa_width_m < 1.85,
        details=f"seat_h={r.seat_height_m}, width={r.sofa_width_m}",
    )

    for joint in object_model.articulations:
        limits = joint.motion_limits
        ctx.check(
            f"{joint.name} keeps a real bounded range",
            limits is not None
            and limits.lower is not None
            and limits.upper is not None
            and limits.upper > limits.lower,
            details=f"limits={limits}",
        )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "smallest_group_two_tables",
        {
            "sofa_width_m": 1.10,
            "sofa_depth_m": 0.75,
            "seat_height_m": 0.32,
            "table_top_width_m": 0.30,
            "table_reach_m": 0.22,
            "side_table_count": 2,
        },
        reason="narrowest sofa carrying two tables with the shortest reach",
    ),
    corner_case(
        "largest_group_single_table",
        {
            "sofa_width_m": 1.80,
            "sofa_depth_m": 1.05,
            "seat_height_m": 0.46,
            "table_top_width_m": 0.52,
            "table_reach_m": 0.40,
            "side_table_count": 1,
        },
        reason="widest deepest sofa with the largest top and the longest reach",
    ),
    corner_case(
        "largest_top_on_smallest_sofa",
        {
            "sofa_width_m": 1.10,
            "sofa_depth_m": 0.75,
            "seat_height_m": 0.46,
            "table_top_width_m": 0.52,
            "table_reach_m": 0.40,
            "side_table_count": 2,
        },
        reason="two of the largest tops with the longest reach on the narrowest sofa",
    ),
    corner_case(
        "lowest_seat_shortest_reach",
        {
            "sofa_width_m": 1.80,
            "sofa_depth_m": 1.05,
            "seat_height_m": 0.32,
            "table_top_width_m": 0.30,
            "table_reach_m": 0.22,
            "side_table_count": 1,
        },
        reason="lowest seat and shortest reach on the deepest sofa",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_picturex_0611_c_shaped_sofa_side_table",
    "build_seeded_picturex_0611_c_shaped_sofa_side_table",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_c_shaped_sofa_side_table_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
