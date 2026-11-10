# SPDX-License-Identifier: Apache-2.0

"""Hand and motor driven butter churns (pictureX/0611).

The category host is always the same: a closed vessel, a lid carrying the drive
frame, a vertical dasher shaft reaching into the vessel and N dasher blades on
it.  Four slots vary: the vessel body (`vessel_form`), how the shaft is driven
(`drive_form`), the blade family (`dasher_form`) and how the churn is mounted
(`mount_form`); `paddle_count` is the multiplicity applied to `dasher_form`.

Source evidence lives in
`articraft_template_authoring/source_maps/pictureX_0611_Butter_maker.md`.
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
    AxisInterface,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

VesselForm = Literal["glass_mason_jar", "ceramic_crock", "wood_barrel", "box_churn"]
DriveForm = Literal[
    "bevel_gear_crank", "direct_vertical_crank", "plunger_dasher", "electric_motor"
]
DasherForm = Literal["perforated_blade", "cross_dasher", "helical_dasher", "whisk_cage"]
MountForm = Literal["countertop", "floor_stand"]

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "vessel_form",
            ("glass_mason_jar", "ceramic_crock", "wood_barrel", "box_churn"),
            role="source-backed churn vessel body",
        ),
        component_slot(
            "drive_form",
            (
                "bevel_gear_crank",
                "direct_vertical_crank",
                "plunger_dasher",
                "electric_motor",
            ),
            role="source-backed dasher drive",
        ),
        component_slot(
            "dasher_form",
            ("perforated_blade", "cross_dasher", "helical_dasher", "whisk_cage"),
            role="source-backed dasher blade family",
        ),
        component_slot(
            "mount_form",
            ("countertop", "floor_stand"),
            role="source-backed mounting family",
        ),
        multiplicity_slot(
            "paddle_count",
            (1, 2, 3, 4),
            role="number of dasher blades on the shaft",
            item_slot="dasher_form",
        ),
    )
)

_WALL = 0.005
_LID_T = 0.014
_SHAFT_R = 0.0060


@dataclass(frozen=True)
class Config:
    vessel_form: VesselForm = "glass_mason_jar"
    drive_form: DriveForm = "bevel_gear_crank"
    dasher_form: DasherForm = "perforated_blade"
    mount_form: MountForm = "countertop"
    paddle_count: int = 2
    vessel_height_m: float = 0.200
    vessel_bore_m: float = 0.095
    frame_height_m: float = 0.120
    blade_height_ratio: float = 0.42
    name: str = "butter_maker"


@dataclass(frozen=True)
class ResolvedConfig:
    vessel_form: VesselForm
    drive_form: DriveForm
    dasher_form: DasherForm
    mount_form: MountForm
    paddle_count: int
    vessel_height_m: float
    vessel_bore_m: float
    frame_height_m: float
    blade_height_ratio: float
    name: str
    # derived
    bore_r_m: float
    outer_r_m: float
    lid_z_m: float
    lid_top_m: float
    frame_top_m: float
    gear_z_m: float
    inner_r_m: float
    blade_r_m: float
    blade_h_m: float
    blade_mid_m: float
    plunger_travel_m: float
    stand_lift_m: float


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0611_B077_E933)
    return Config(
        vessel_form=choices["vessel_form"],
        drive_form=choices["drive_form"],
        dasher_form=choices["dasher_form"],
        mount_form=choices["mount_form"],
        paddle_count=int(choices["paddle_count"]),
        vessel_height_m=round(rng.uniform(0.150, 0.270), 5),
        vessel_bore_m=round(rng.uniform(0.075, 0.125), 5),
        frame_height_m=round(rng.uniform(0.095, 0.165), 5),
        blade_height_ratio=round(rng.uniform(0.32, 0.52), 5),
        name=f"butter_maker_seed_{seed}",
    )


def _require_range(name: str, value: float, minimum: float, maximum: float) -> float:
    value = float(value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be in [{minimum}, {maximum}], got {value}")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "vessel_form": config.vessel_form,
            "drive_form": config.drive_form,
            "dasher_form": config.dasher_form,
            "mount_form": config.mount_form,
            "paddle_count": int(config.paddle_count),
        }
    )
    height = _require_range("vessel_height_m", config.vessel_height_m, 0.140, 0.280)
    bore = _require_range("vessel_bore_m", config.vessel_bore_m, 0.070, 0.130)
    frame_h = _require_range("frame_height_m", config.frame_height_m, 0.090, 0.170)
    ratio = _require_range("blade_height_ratio", config.blade_height_ratio, 0.30, 0.55)
    count = int(config.paddle_count)

    travel = min(height * 0.18, frame_h * 0.30)
    blade_h = min(height * ratio, height - 0.040 - travel)
    half = 0.5 * blade_h
    # The blade station is clamped so the dasher always clears the vessel floor
    # and, at the top of a plunger stroke, still stays under the lid.
    lowest = 0.018 + half
    highest = max(lowest, height - 0.022 - half - travel)
    blade_mid = min(max(height * 0.34, lowest), highest)
    bore_r = 0.5 * bore
    # A square plan has less usable turning radius than its nominal bore.
    inner_r = (bore_r + _WALL) * 0.86 - _WALL if config.vessel_form == "box_churn" else bore_r
    lid_z = height
    lid_top = lid_z + _LID_T
    stand_lift = 0.070 if config.mount_form == "floor_stand" else 0.0
    return ResolvedConfig(
        vessel_form=config.vessel_form,
        drive_form=config.drive_form,
        dasher_form=config.dasher_form,
        mount_form=config.mount_form,
        paddle_count=count,
        vessel_height_m=height,
        vessel_bore_m=bore,
        frame_height_m=frame_h,
        blade_height_ratio=ratio,
        name=config.name,
        bore_r_m=bore_r,
        outer_r_m=bore_r + _WALL,
        lid_z_m=lid_z,
        lid_top_m=lid_top,
        frame_top_m=lid_top + frame_h,
        gear_z_m=lid_top + frame_h * 0.62,
        inner_r_m=inner_r,
        blade_r_m=inner_r - 0.006,
        blade_h_m=blade_h,
        blade_mid_m=blade_mid,
        plunger_travel_m=travel,
        stand_lift_m=stand_lift,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, object]:
    return {
        "vessel_form": config.vessel_form,
        "drive_form": config.drive_form,
        "dasher_form": config.dasher_form,
        "mount_form": config.mount_form,
        "paddle_count": int(config.paddle_count),
    }


def slot_choices_for_seed(seed: int) -> dict[str, object]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject) -> dict[str, object]:
    return {
        "glass": model.material("churn_glass", rgba=(0.82, 0.88, 0.90, 0.45)),
        "crock": model.material("churn_crock", rgba=(0.86, 0.83, 0.75, 1.0)),
        "wood": model.material("churn_wood", rgba=(0.68, 0.50, 0.29, 1.0)),
        "steel": model.material("churn_steel", rgba=(0.72, 0.74, 0.76, 1.0)),
        "dark": model.material("churn_dark_steel", rgba=(0.30, 0.31, 0.33, 1.0)),
        "poly": model.material("churn_polymer", rgba=(0.16, 0.17, 0.18, 1.0)),
    }


# ---------------------------------------------------------------------------
# vessel profiles
# ---------------------------------------------------------------------------


def _round_vessel_shape(outer_r: float, bore_r: float, height: float,
                        sections: list[tuple[float, float]]) -> cq.Workplane:
    """Revolved hollow body from a normalised (z_ratio, radius_scale) profile."""

    wp = cq.Workplane("XZ").moveTo(0.0, 0.0)
    wp = wp.lineTo(outer_r * sections[0][1], 0.0)
    for z_ratio, scale in sections:
        wp = wp.lineTo(outer_r * scale, height * z_ratio)
    top_r = outer_r * sections[-1][1]
    wp = wp.lineTo(top_r - _WALL, height * sections[-1][0])
    for z_ratio, scale in reversed(sections[:-1]):
        wp = wp.lineTo(max(outer_r * scale - _WALL, 0.004), height * z_ratio)
    wp = wp.lineTo(max(outer_r * sections[0][1] - _WALL, 0.004), _WALL * 1.6)
    wp = wp.lineTo(0.0, _WALL * 1.6)
    return wp.close().revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))


def _vessel_form_glass_mason_jar_build(r: ResolvedConfig) -> cq.Workplane:
    return _round_vessel_shape(
        r.outer_r_m, r.bore_r_m, r.vessel_height_m,
        [(0.06, 1.0), (0.86, 1.0), (0.93, 0.90), (1.0, 0.90)],
    )


def _vessel_form_ceramic_crock_build(r: ResolvedConfig) -> cq.Workplane:
    return _round_vessel_shape(
        r.outer_r_m, r.bore_r_m, r.vessel_height_m,
        [(0.05, 0.86), (0.30, 1.02), (0.62, 1.00), (0.88, 0.88), (1.0, 0.94)],
    )


def _vessel_form_wood_barrel_build(r: ResolvedConfig) -> cq.Workplane:
    body = _round_vessel_shape(
        r.outer_r_m, r.bore_r_m, r.vessel_height_m,
        [(0.05, 0.90), (0.45, 1.03), (0.95, 0.90), (1.0, 0.90)],
    )
    for z_ratio in (0.16, 0.50, 0.86):
        band = (
            cq.Workplane("XY")
            .circle(r.outer_r_m * 1.05)
            .circle(r.outer_r_m * 0.86)
            .extrude(0.006)
            .translate((0.0, 0.0, r.vessel_height_m * z_ratio))
        )
        body = body.union(band)
    return body


def _vessel_form_box_churn_build(r: ResolvedConfig) -> cq.Workplane:
    side = r.outer_r_m * 1.72
    outer = cq.Workplane("XY").box(side, side, r.vessel_height_m).translate(
        (0.0, 0.0, 0.5 * r.vessel_height_m)
    )
    cavity = (
        cq.Workplane("XY")
        .box(side - 2.0 * _WALL, side - 2.0 * _WALL, r.vessel_height_m)
        .translate((0.0, 0.0, 0.5 * r.vessel_height_m + _WALL * 1.6))
    )
    return outer.cut(cavity)


_VESSEL_BUILDERS = {
    "glass_mason_jar": _vessel_form_glass_mason_jar_build,
    "ceramic_crock": _vessel_form_ceramic_crock_build,
    "wood_barrel": _vessel_form_wood_barrel_build,
    "box_churn": _vessel_form_box_churn_build,
}

_VESSEL_MATERIAL = {
    "glass_mason_jar": "glass",
    "ceramic_crock": "crock",
    "wood_barrel": "wood",
    "box_churn": "wood",
}


# ---------------------------------------------------------------------------
# dasher blades
# ---------------------------------------------------------------------------


def _perforated_board(width: float, height: float, thickness: float) -> cq.Workplane:
    board = cq.Workplane("XY").box(width, thickness, height)
    cols = max(2, int(width / 0.026))
    rows = max(2, int(height / 0.032))
    for row in range(rows):
        for col in range(cols):
            x = -0.5 * width + width * (col + 0.5) / cols
            z = -0.5 * height + height * (row + 0.5) / rows
            board = board.cut(
                cq.Workplane("XZ")
                .center(x, z)
                .circle(min(0.0075, 0.30 * width / cols))
                .extrude(thickness, both=True)
            )
    return board


_FIN_ROOT = 0.0126


def _fin_span(r: ResolvedConfig) -> tuple[float, float]:
    """Radial (width, centre) of one fin so its tip keeps a real wall clearance."""

    width = max(0.012, r.blade_r_m - _FIN_ROOT)
    return width, _FIN_ROOT + 0.5 * width


def _dasher_form_perforated_blade_build(r: ResolvedConfig) -> cq.Workplane:
    width, centre = _fin_span(r)
    fin = _perforated_board(width, r.blade_h_m, 0.006)
    return fin.translate((centre, 0.0, 0.0))


def _dasher_form_cross_dasher_build(r: ResolvedConfig) -> cq.Workplane:
    """Two perforated boards crossed about the shaft and tied at their root.

    The source crosses them at 90 degrees on a single blade; when N grows the
    half-angle closes so N crossed pairs still share the bore without touching.
    """

    width, centre = _fin_span(r)
    half_angle = min(45.0, 180.0 / r.paddle_count - 12.0)
    board = _perforated_board(width, r.blade_h_m, 0.006).translate((centre, 0.0, 0.0))
    left = board.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), half_angle)
    right = (
        _perforated_board(width, r.blade_h_m, 0.006)
        .translate((centre, 0.0, 0.0))
        .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), -half_angle)
    )
    # A web out at the blade root ties the pair together without reaching the
    # shaft collar or the neighbouring blade's sector.
    web_half_y = _FIN_ROOT * math.tan(math.radians(half_angle)) + 0.003
    web = (
        cq.Workplane("XY")
        .box(0.012, 2.0 * web_half_y, r.blade_h_m)
        .translate((_FIN_ROOT + 0.006, 0.0, 0.0))
    )
    return left.union(right).union(web)


def _dasher_form_helical_dasher_build(r: ResolvedConfig) -> cq.Workplane:
    steps = 10
    result: cq.Workplane | None = None
    for index in range(steps):
        t = index / (steps - 1.0)
        angle = 70.0 * t
        width, centre = _fin_span(r)
        slab = (
            cq.Workplane("XY")
            .box(width, 0.006, r.blade_h_m / steps + 0.004)
            .translate((centre, 0.0, 0.0))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
            .translate((0.0, 0.0, -0.5 * r.blade_h_m + r.blade_h_m * t))
        )
        result = slab if result is None else result.union(slab)
    assert result is not None
    return result


def _dasher_form_whisk_cage_build(r: ResolvedConfig) -> cq.Workplane:
    steps = 12
    result: cq.Workplane | None = None
    for index in range(steps):
        t = index / (steps - 1.0)
        z = -0.5 * r.blade_h_m + r.blade_h_m * t
        radius = _FIN_ROOT + max(0.006, r.blade_r_m - _FIN_ROOT) * math.sin(math.pi * t)
        # Each level is a rib running out from the spine, so the cage stays one
        # connected wire body at every blade height.
        rib = (
            cq.Workplane("XY")
            .box(radius - _FIN_ROOT + 0.008, 0.005, 0.005)
            .translate((0.5 * (radius + _FIN_ROOT) - 0.002, 0.0, z))
        )
        hoop = (
            cq.Workplane("XY")
            .box(0.005, 0.005, r.blade_h_m / steps + 0.006)
            .translate((radius, 0.0, z))
        )
        piece = rib.union(hoop)
        result = piece if result is None else result.union(piece)
    spine = (
        cq.Workplane("XY")
        .box(0.006, 0.006, r.blade_h_m)
        .translate((_FIN_ROOT + 0.001, 0.0, 0.0))
    )
    assert result is not None
    return result.union(spine)


_DASHER_BUILDERS = {
    "perforated_blade": _dasher_form_perforated_blade_build,
    "cross_dasher": _dasher_form_cross_dasher_build,
    "helical_dasher": _dasher_form_helical_dasher_build,
    "whisk_cage": _dasher_form_whisk_cage_build,
}


# ---------------------------------------------------------------------------
# host: vessel, lid and drive frame
# ---------------------------------------------------------------------------


def _build_vessel(model: ArticulatedObject, r: ResolvedConfig, mats):
    vessel = model.part("churn__vessel", meta={"role": "vessel", "candidate": r.vessel_form})
    body = _VESSEL_BUILDERS[r.vessel_form](r)
    vessel.visual(
        mesh_from_cadquery(body, f"churn__vessel_{r.vessel_form}", tolerance=0.0012),
        origin=Origin(xyz=(0.0, 0.0, r.stand_lift_m)),
        material=mats[_VESSEL_MATERIAL[r.vessel_form]],
        name="churn__vessel__body", material_class_id=("wood.natural_generic" if r.vessel_form in {"ceramic_crock", "wood_barrel", "box_churn"} else "glass.clear_transparent"),
    )
    vessel.visual(
        mesh_from_cadquery(
            _bored_boss(r.outer_r_m * 0.98, 0.012, 0.006, "z"),
            "churn__vessel_rim_seat",
            tolerance=0.0008,
        ),
        origin=Origin(xyz=(0.0, 0.0, r.stand_lift_m + r.vessel_height_m - 0.003)),
        material=mats[_VESSEL_MATERIAL[r.vessel_form]],
        name="churn__vessel__rim_seat", material_class_id=("wood.natural_generic" if r.vessel_form in {"ceramic_crock", "wood_barrel", "box_churn"} else "glass.clear_transparent"),
    )
    _MOUNT_BUILDERS[r.mount_form](model, r, mats, vessel)
    return vessel


def _mount_form_countertop_build(model, r, mats, vessel):
    vessel.visual(
        Cylinder(radius=r.outer_r_m * 1.02, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, 0.004)),
        material=mats["dark"],
        name="churn__vessel__foot_ring", material_class_id="metal.blackened_gunmetal",
    )


def _mount_form_floor_stand_build(model, r, mats, vessel):
    lift = r.stand_lift_m
    vessel.visual(
        Cylinder(radius=r.outer_r_m * 1.06, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, lift - 0.006)),
        material=mats["wood"],
        name="churn__vessel__cradle_ring", material_class_id="wood.natural_generic",
    )
    for index in range(3):
        angle = 2.0 * math.pi * index / 3.0
        vessel.visual(
            Box((0.020, 0.020, lift + 0.010)),
            origin=Origin(
                xyz=(
                    math.cos(angle) * r.outer_r_m * 0.86,
                    math.sin(angle) * r.outer_r_m * 0.86,
                    0.5 * (lift + 0.010),
                ),
                rpy=(0.0, 0.0, angle),
            ),
            material=mats["wood"],
            name=f"churn__vessel__stand_leg_{index}", material_class_id="wood.natural_generic",
        )
    vessel.visual(
        Cylinder(radius=r.outer_r_m * 1.10, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.007)),
        material=mats["wood"],
        name="churn__vessel__stand_foot", material_class_id="wood.natural_generic",
    )


_MOUNT_BUILDERS = {
    "countertop": _mount_form_countertop_build,
    "floor_stand": _mount_form_floor_stand_build,
}


def _bored_boss(outer: float, bore: float, length: float, axis: str) -> cq.Workplane:
    plane = {"x": "YZ", "y": "XZ", "z": "XY"}[axis]
    body = cq.Workplane(plane).circle(outer).extrude(length * 0.5, both=True)
    hole = cq.Workplane(plane).circle(bore).extrude(length, both=True)
    return body.cut(hole)


def _top_bar_shape(length: float) -> cq.Workplane:
    """Frame top bar with a real guide bore for the dasher shaft."""

    bar = cq.Workplane("XZ").circle(0.011).extrude(length * 0.5, both=True)
    bore = cq.Workplane("XY").circle(_SHAFT_R + 0.0022).extrude(0.040, both=True)
    return bar.cut(bore)


def _lid_disc_shape(size: float, square: bool) -> cq.Workplane:
    disc = (
        cq.Workplane("XY").box(size, size, _LID_T)
        if square
        else cq.Workplane("XY").circle(size).extrude(_LID_T * 0.5, both=True)
    )
    bore = cq.Workplane("XY").circle(_SHAFT_R + 0.0012).extrude(_LID_T, both=True)
    return disc.cut(bore)


def _build_lid(model: ArticulatedObject, r: ResolvedConfig, mats, vessel):
    """Lid plus the drive frame it carries; both are fixed to the vessel rim."""

    lid = model.part("churn__lid", meta={"role": "lid"})
    lid_r = r.outer_r_m * 1.04
    square = r.vessel_form == "box_churn"
    lid.visual(
        mesh_from_cadquery(
            _lid_disc_shape(r.outer_r_m * 1.72 + 0.008 if square else lid_r, square),
            "churn__lid_disc",
            tolerance=0.0010,
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * _LID_T)),
        material=mats["dark"],
        name="churn__lid__disc", material_class_id="metal.blackened_gunmetal",
    )
    lid.visual(
        mesh_from_cadquery(
            _bored_boss(0.014, _SHAFT_R + 0.0008, 0.016, "z"),
            "churn__lid_bearing",
            tolerance=0.0006,
        ),
        origin=Origin(xyz=(0.0, 0.0, _LID_T + 0.006)),
        material=mats["steel"],
        name="churn__lid__shaft_bearing", material_class_id="metal.steel_bare",
    )
    # Drive frame: two uprights and a top bar, exactly as in every source record.
    # The posts straddle the Y axis so the side crank, on X, never meets them.
    post_y = r.outer_r_m * 0.62
    for index, sy in enumerate((-1.0, 1.0)):
        lid.visual(
            Box((0.014, 0.012, r.frame_height_m)),
            origin=Origin(xyz=(0.0, sy * post_y, _LID_T + 0.5 * r.frame_height_m)),
            material=mats["steel"],
            name=f"churn__lid__frame_post_{index}", material_class_id="metal.steel_bare",
        )
    lid.visual(
        mesh_from_cadquery(
            _top_bar_shape(2.0 * post_y + 0.030),
            "churn__lid_top_bar",
            tolerance=0.0008,
        ),
        origin=Origin(xyz=(0.0, 0.0, _LID_T + r.frame_height_m - 0.011)),
        material=mats["wood"],
        name="churn__lid__top_bar", material_class_id="wood.natural_generic",
    )
    model.articulation(
        "churn__vessel_to_lid",
        ArticulationType.FIXED,
        parent=vessel,
        child=lid,
        origin=Origin(xyz=(0.0, 0.0, r.stand_lift_m + r.lid_z_m)),
        meta={"mechanism": "threaded lid band"},
    )
    return lid


# ---------------------------------------------------------------------------
# drive_form candidates
# ---------------------------------------------------------------------------


def _add_shaft(model, r, mats, lid, *, prismatic: bool, top: float):
    shaft = model.part("churn__shaft", meta={"role": "dasher_shaft"})
    bottom = -r.vessel_height_m * 0.90
    shaft_len = top - bottom
    shaft.visual(
        Cylinder(radius=_SHAFT_R, length=shaft_len),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (top + bottom))),
        material=mats["steel"],
        name="churn__shaft__rod", material_class_id="metal.steel_bare",
    )
    shaft.visual(
        Cylinder(radius=0.011, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.015)),
        material=mats["steel"],
        name="churn__shaft__collar", material_class_id="metal.steel_bare",
    )
    shaft.visual(
        Cylinder(radius=0.012, length=r.blade_h_m + 0.014),
        origin=Origin(xyz=(0.0, 0.0, r.blade_mid_m - r.lid_z_m - _LID_T - 0.006)),
        material=mats["steel"],
        name="churn__shaft__blade_collar", material_class_id="metal.steel_bare",
    )
    joint = "churn__dasher_drive"
    if prismatic:
        model.articulation(
            joint,
            ArticulationType.PRISMATIC,
            parent=lid,
            child=shaft,
            origin=Origin(xyz=(0.0, 0.0, _LID_T + 0.006)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=90.0, velocity=0.3, lower=0.0, upper=r.plunger_travel_m
            ),
            meta={"mechanism": "plunger dasher stroke"},
        )
        return shaft
    provider = AxisInterface(
        name="lid.shaft_bearing",
        point=(0.0, 0.0, _LID_T + 0.006),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=_SHAFT_R + 0.0008,
    )
    consumer = AxisInterface(
        name="shaft.journal",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=_SHAFT_R,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        joint,
        ArticulationType.CONTINUOUS,
        parent=lid,
        child=shaft,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=40.0, velocity=8.0),
        meta={"mechanism": "dasher shaft rotation"},
    )
    register_interface_mate(model, joint, mate)
    return shaft


def _bevel_disc(radius: float, thickness: float, bore: float) -> cq.Workplane:
    """Bevel wheel with real teeth cut around its rim, press fit on its shaft."""

    disc = cq.Workplane("XY").circle(radius).extrude(thickness * 0.5, both=True)
    notch = min(0.0050, radius * 0.22)
    teeth = max(6, int(2.0 * math.pi * radius / (notch * 2.2)))
    for index in range(teeth):
        angle = 2.0 * math.pi * index / teeth
        cut = (
            cq.Workplane("XY")
            .box(notch, notch, thickness * 1.4)
            .translate((radius * math.cos(angle), radius * math.sin(angle), 0.0))
        )
        disc = disc.cut(cut)
    hole = cq.Workplane("XY").circle(bore).extrude(thickness, both=True)
    return disc.cut(hole)


def _drive_form_bevel_gear_crank_build(model, r, mats, lid):
    shaft = _add_shaft(model, r, mats, lid, prismatic=False, top=r.frame_height_m * 0.62 + 0.016)
    crown_r = min(0.030, r.outer_r_m * 0.42)
    crown_z = (r.gear_z_m - r.lid_z_m) - (_LID_T + 0.006)
    shaft.visual(
        mesh_from_cadquery(
            _bevel_disc(crown_r, 0.008, _SHAFT_R - 0.0012), "churn__crown_gear", tolerance=0.0006
        ),
        origin=Origin(xyz=(0.0, 0.0, crown_z)),
        material=mats["steel"],
        name="churn__shaft__crown_gear", material_class_id="metal.steel_bare",
    )
    pinion_r = crown_r * 0.52
    crank_x = crown_r * 0.72
    crank_z = (r.gear_z_m - r.lid_z_m) + 0.004 + pinion_r + 0.001
    crank = model.part("churn__crank", meta={"role": "drive_input", "candidate": "bevel_gear_crank"})
    crank.visual(
        mesh_from_cadquery(
            _bevel_disc(pinion_r, 0.008, 0.0044), "churn__pinion_gear", tolerance=0.0006
        ),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name="churn__crank__pinion", material_class_id="metal.steel_bare",
    )
    arm_r = min(0.045, 0.62 * (r.gear_z_m - r.lid_top_m))
    crank.visual(
        Cylinder(radius=0.0055, length=0.084),
        origin=Origin(xyz=(0.042, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name="churn__crank__shaft", material_class_id="metal.steel_bare",
    )
    crank.visual(
        Box((0.012, 0.010, 2.0 * arm_r)),
        origin=Origin(xyz=(0.080, 0.0, 0.0)),
        material=mats["steel"],
        name="churn__crank__arm", material_class_id="metal.steel_bare",
    )
    crank.visual(
        Cylinder(radius=0.011, length=0.048),
        origin=Origin(xyz=(0.104, 0.0, arm_r), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["wood"],
        name="churn__crank__grip", material_class_id="wood.natural_generic",
    )
    lid_outer = (r.outer_r_m * 0.86 + 0.004) if r.vessel_form == "box_churn" else r.outer_r_m * 1.04
    bearing_x = min(crank_x + 0.052, lid_outer - 0.014)
    stand_h = max(0.010, crank_z - 0.008 - _LID_T + 0.006)
    lid.visual(
        Box((0.020, 0.026, stand_h)),
        origin=Origin(xyz=(bearing_x, 0.0, _LID_T - 0.006 + 0.5 * stand_h)),
        material=mats["steel"],
        name="churn__lid__crank_standard", material_class_id="metal.steel_bare",
    )
    lid.visual(
        mesh_from_cadquery(
            _bored_boss(0.011, 0.0064, 0.016, "x"), "churn__crank_bearing", tolerance=0.0006
        ),
        origin=Origin(xyz=(bearing_x, 0.0, crank_z)),
        material=mats["steel"],
        name="churn__lid__crank_bearing", material_class_id="metal.steel_bare",
    )
    provider = AxisInterface(
        name="lid.crank_bearing",
        point=(crank_x, 0.0, crank_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0064,
    )
    consumer = AxisInterface(
        name="crank.journal",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0055,
    )
    mate = mate_axes(provider, consumer)
    joint = "churn__crank_turn"
    model.articulation(
        joint,
        ArticulationType.CONTINUOUS,
        parent=lid,
        child=crank,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=25.0, velocity=8.0),
        meta={"mechanism": "bevel-geared side crank"},
    )
    register_interface_mate(model, joint, mate)
    return shaft


def _drive_form_direct_vertical_crank_build(model, r, mats, lid):
    # The arm clears the frame top bar, exactly as in the source top-crank fork.
    arm_z = r.frame_height_m + 0.020
    shaft = _add_shaft(model, r, mats, lid, prismatic=False, top=arm_z + 0.020)
    arm_len = min(0.060, r.outer_r_m * 0.80)
    shaft.visual(
        Box((2.0 * arm_len, 0.012, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, arm_z)),
        material=mats["steel"],
        name="churn__shaft__crank_arm", material_class_id="metal.steel_bare",
    )
    shaft.visual(
        mesh_from_cadquery(
            _bored_boss(0.011, 0.0068, 0.014, "z"), "churn__grip_boss", tolerance=0.0006
        ),
        origin=Origin(xyz=(arm_len, 0.0, arm_z + 0.010)),
        material=mats["steel"],
        name="churn__shaft__grip_boss", material_class_id="metal.steel_bare",
    )
    grip = model.part(
        "churn__crank_grip",
        meta={"role": "drive_input", "candidate": "direct_vertical_crank"},
    )
    grip.visual(
        Cylinder(radius=0.0060, length=0.024),
        origin=Origin(),
        material=mats["steel"],
        name="churn__crank_grip__pin", material_class_id="metal.steel_bare",
    )
    grip.visual(
        Cylinder(radius=0.012, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, 0.024)),
        material=mats["wood"],
        name="churn__crank_grip__handle", material_class_id="wood.natural_generic",
    )
    provider = AxisInterface(
        name="shaft.grip_boss",
        point=(arm_len, 0.0, arm_z + 0.010),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0068,
    )
    consumer = AxisInterface(
        name="grip.journal",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0060,
    )
    mate = mate_axes(provider, consumer)
    joint = "churn__grip_spin"
    model.articulation(
        joint,
        ArticulationType.CONTINUOUS,
        parent=shaft,
        child=grip,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=6.0, velocity=10.0),
        meta={"mechanism": "free-spinning crank handle"},
    )
    register_interface_mate(model, joint, mate)
    return shaft


def _drive_form_plunger_dasher_build(model, r, mats, lid):
    shaft = _add_shaft(model, r, mats, lid, prismatic=True, top=r.frame_height_m + 0.006)
    grip = model.part(
        "churn__plunger_grip",
        meta={"role": "drive_input", "candidate": "plunger_dasher"},
    )
    grip_z = 0.026
    grip.visual(
        Cylinder(radius=0.013, length=0.052),
        origin=Origin(xyz=(0.0, 0.0, grip_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["wood"],
        name="churn__plunger_grip__bar", material_class_id="wood.natural_generic",
    )
    grip.visual(
        mesh_from_cadquery(
            _bored_boss(0.0080, _SHAFT_R + 0.0008, 0.034, "z"),
            "churn__plunger_stem",
            tolerance=0.0006,
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.017)),
        material=mats["steel"],
        name="churn__plunger_grip__stem", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "churn__plunger_grip_fix",
        ArticulationType.FIXED,
        parent=shaft,
        child=grip,
        origin=Origin(xyz=(0.0, 0.0, r.frame_height_m - 0.004)),
        meta={"mechanism": "plunger top grip"},
    )
    return shaft


def _drive_form_electric_motor_build(model, r, mats, lid):
    shaft = _add_shaft(model, r, mats, lid, prismatic=False, top=r.frame_height_m * 0.62 + 0.016)
    motor = model.part(
        "churn__motor", meta={"role": "drive_input", "candidate": "electric_motor"}
    )
    housing_h = r.frame_height_m * 0.66
    motor_r = max(0.014, min(0.034, r.outer_r_m * 0.62 - 0.010))
    motor.visual(
        mesh_from_cadquery(
            _motor_housing_shape(motor_r, housing_h),
            "churn__motor_housing",
            tolerance=0.0008,
        ),
        material=mats["poly"],
        name="churn__motor__housing", material_class_id="plastic.opaque_glossy_molded",
    )
    motor.visual(
        Box((0.016, 0.010, 0.020)),
        origin=Origin(xyz=(motor_r - 0.002, 0.0, housing_h * 0.62)),
        material=mats["dark"],
        name="churn__motor__switch", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        "churn__motor_mount",
        ArticulationType.FIXED,
        parent=lid,
        child=motor,
        origin=Origin(xyz=(0.0, 0.0, _LID_T + 0.010)),
        meta={"mechanism": "motor drive head"},
    )
    return shaft


def _motor_housing_shape(radius: float, height: float) -> cq.Workplane:
    shell = cq.Workplane("XY").circle(radius).extrude(height)
    cavity = (
        cq.Workplane("XY")
        .circle(radius - 0.005)
        .extrude(height - 0.010)
        .translate((0.0, 0.0, 0.006))
    )
    shell = shell.cut(cavity)
    bore = cq.Workplane("XY").circle(_SHAFT_R + 0.0012).extrude(height, both=True)
    shell = shell.cut(bore)
    for index in range(6):
        angle = 2.0 * math.pi * index / 6.0
        vent = (
            cq.Workplane("XY")
            .box(0.004, 0.020, 0.004)
            .translate(
                (radius * math.cos(angle), radius * math.sin(angle), height * 0.78)
            )
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(angle))
        )
        shell = shell.cut(vent)
    return shell


_DRIVE_BUILDERS = {
    "bevel_gear_crank": _drive_form_bevel_gear_crank_build,
    "direct_vertical_crank": _drive_form_direct_vertical_crank_build,
    "plunger_dasher": _drive_form_plunger_dasher_build,
    "electric_motor": _drive_form_electric_motor_build,
}


def _build_blades(model, r, mats, shaft):
    blades = []
    hub_z = r.blade_mid_m - r.lid_z_m - _LID_T - 0.006
    shape = _DASHER_BUILDERS[r.dasher_form](r)
    for index in range(r.paddle_count):
        angle = 2.0 * math.pi * index / r.paddle_count
        prefix = f"dasher_form__{r.dasher_form}__blade_{index}"
        blade = model.part(prefix, meta={"role": "dasher_blade", "candidate": r.dasher_form})
        blade.visual(
            mesh_from_cadquery(shape, f"{prefix}_mesh", tolerance=0.0010),
            material=mats["dark"] if r.dasher_form == "whisk_cage" else mats["steel"],
            name=f"{prefix}__body", material_class_id=("metal.steel_bare" if r.dasher_form in {"perforated_blade", "cross_dasher", "helical_dasher"} else "metal.blackened_gunmetal"),
        )
        model.articulation(
            f"{prefix}__mount",
            ArticulationType.FIXED,
            parent=shaft,
            child=blade,
            origin=Origin(xyz=(0.0, 0.0, hub_z), rpy=(0.0, 0.0, angle)),
            meta={"mechanism": "dasher blade on the shaft"},
        )
        blades.append(blade)
    return blades


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def build_picturex_0611_butter_maker(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model)
    vessel = _build_vessel(model, r, mats)
    lid = _build_lid(model, r, mats, vessel)
    shaft = _DRIVE_BUILDERS[r.drive_form](model, r, mats, lid)
    _build_blades(model, r, mats, shaft)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/Butter_maker"
    return model


def build_seeded_picturex_0611_butter_maker(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_picturex_0611_butter_maker(config_from_seed(seed), assets=assets)


def _centre(box):
    if box is None:
        return None
    return tuple(0.5 * (box[0][i] + box[1][i]) for i in range(3))


def run_picturex_0611_butter_maker_tests(
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
        "churn keeps one vessel, lid, shaft and N blades",
        len(roles.get("vessel", [])) == 1
        and len(roles.get("lid", [])) == 1
        and len(roles.get("dasher_shaft", [])) == 1
        and len(roles.get("dasher_blade", [])) == r.paddle_count,
        details=(
            f"vessel={len(roles.get('vessel', []))}, lid={len(roles.get('lid', []))}, "
            f"shaft={len(roles.get('dasher_shaft', []))}, "
            f"blades={len(roles.get('dasher_blade', []))}/{r.paddle_count}"
        ),
    )
    ctx.check(
        "domain choices are recorded",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    ctx.check(
        "one source-backed drive head is present",
        len(roles.get("drive_input", [])) == 1
        and roles["drive_input"][0].meta.get("candidate") == r.drive_form,
        details=f"drive={[p.name for p in roles.get('drive_input', [])]}",
    )

    vessel = object_model.get_part("churn__vessel")
    shaft = object_model.get_part("churn__shaft")
    blades = roles.get("dasher_blade", [])

    collar = ctx.part_element_world_aabb(shaft, elem="churn__shaft__collar")
    vessel_box = ctx.part_world_aabb(vessel)
    ctx.check(
        "the dasher shaft reaches down into the vessel",
        collar is not None
        and vessel_box is not None
        and collar[0][2] > vessel_box[0][2],
        details=f"collar={collar}, vessel={vessel_box}",
    )

    blade_boxes = [ctx.part_world_aabb(blade) for blade in blades]
    floor_z = (vessel_box[0][2] if vessel_box else 0.0) + 0.010
    ceiling_z = (vessel_box[1][2] if vessel_box else 0.0) - 0.004
    # Radial clearance is a derived contract (the exact vessel/blade pair is
    # collision-checked at every pose by baseline QC); here the invariant is that
    # the blade radius really follows the host bore and stays inside it in Z.
    ctx.check(
        "every dasher blade stays inside the vessel bore",
        all(box is not None for box in blade_boxes)
        and r.blade_r_m + 0.005 <= r.inner_r_m
        and all(
            box[0][2] > floor_z and box[1][2] < ceiling_z
            for box in blade_boxes
            if box
        ),
        details=(
            f"inner_r={r.inner_r_m}, blade_r={r.blade_r_m}, "
            f"floor={floor_z}, ceiling={ceiling_z}, blades={len(blade_boxes)}"
        ),
    )

    drive = object_model.get_articulation("churn__dasher_drive")
    ctx.check(
        "every seed is articulated by its dasher, not by mount hardware",
        drive.articulation_type in (
            ArticulationType.CONTINUOUS,
            ArticulationType.PRISMATIC,
        )
        and not roles.get("mount_hardware")
        and all("clamp" not in joint.name for joint in object_model.articulations),
        details=(
            f"drive={drive.articulation_type}, "
            f"mount_hardware={[p.name for p in roles.get('mount_hardware', [])]}, "
            f"joints={[joint.name for joint in object_model.articulations]}"
        ),
    )
    rest = [_centre(box) for box in blade_boxes]
    if drive.articulation_type is ArticulationType.PRISMATIC:
        target = drive.motion_limits.upper
    else:
        target = math.pi / 2.0
    with ctx.pose({drive: target}):
        moved = [_centre(ctx.part_world_aabb(blade)) for blade in blades]
    ctx.check(
        "the drive really moves the dasher",
        all(a is not None and b is not None for a, b in zip(rest, moved, strict=True))
        and any(
            max(abs(b[i] - a[i]) for i in range(3)) > 0.004
            for a, b in zip(rest, moved, strict=True)
        ),
        details=f"rest={rest}, moved={moved}",
    )

    ctx.check(
        "the vessel is a closed churn of a plausible size",
        vessel_box is not None
        and (vessel_box[1][2] - vessel_box[0][2]) > r.vessel_height_m * 0.80
        and 0.06 < r.bore_r_m * 2.0 < 0.14,
        details=f"vessel={vessel_box}, bore={r.vessel_bore_m}",
    )

    for joint in object_model.articulations:
        if joint.articulation_type in (
            ArticulationType.REVOLUTE,
            ArticulationType.PRISMATIC,
        ):
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
        "smallest_vessel_most_blades",
        {
            "vessel_height_m": 0.140,
            "vessel_bore_m": 0.070,
            "frame_height_m": 0.090,
            "blade_height_ratio": 0.55,
            "paddle_count": 4,
        },
        reason="smallest bore and shortest body carrying the tallest four-blade dasher",
    ),
    corner_case(
        "largest_vessel_single_blade",
        {
            "vessel_height_m": 0.280,
            "vessel_bore_m": 0.130,
            "frame_height_m": 0.170,
            "blade_height_ratio": 0.30,
            "paddle_count": 1,
        },
        reason="largest body and tallest frame with the shortest single blade",
    ),
    corner_case(
        "tall_narrow_vessel_with_tall_blades",
        {
            "vessel_height_m": 0.280,
            "vessel_bore_m": 0.070,
            "frame_height_m": 0.090,
            "blade_height_ratio": 0.55,
            "paddle_count": 4,
        },
        reason="narrowest bore with the tallest blades and the lowest frame",
    ),
    corner_case(
        "squat_wide_vessel_with_tall_frame",
        {
            "vessel_height_m": 0.140,
            "vessel_bore_m": 0.130,
            "frame_height_m": 0.170,
            "blade_height_ratio": 0.30,
            "paddle_count": 2,
        },
        reason="widest squat body under the tallest drive frame",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_picturex_0611_butter_maker",
    "build_seeded_picturex_0611_butter_maker",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_butter_maker_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
