# SPDX-License-Identifier: Apache-2.0

"""Wall-mounted first-aid cabinet - Design-backed single-file template.

The root is a shallow, open-front sheet-metal cabinet with a carry handle,
equispaced shelves and first-aid identity marks.  One or two front leaves swing
about real vertical jamb axes.  The lower interior is either open, occupied by
one pull-out tray, or divided into an indexed bank of hollow pull-out trays.

Frame: +X right, +Y forward/out of the cabinet, +Z up; cabinet bottom is z=0.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AxisInterface,
    Box,
    Material,
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

DoorGroup = Literal["single_leaf", "double_leaf"]
DoorPanel = Literal["glazed_window", "solid_panel"]
InteriorFitment = Literal["open_shelves", "base_drawer", "drawer_bank"]

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("door_group", ("single_leaf", "double_leaf")),
        component_slot("door_panel", ("glazed_window", "solid_panel")),
        component_slot("interior_fitment", ("open_shelves", "base_drawer", "drawer_bank")),
        multiplicity_slot("shelf_count", (1, 2, 3), item_slot="interior_fitment"),
    )
)

_WALL_T = 0.010
_SHELF_T = 0.008
_SHELF_EMBED = 0.0
_DOOR_GAP = 0.002
_DOOR_REVEAL = 0.006
_HINGE_R = 0.006
_HINGE_BORE_R = 0.0045
_DRAWER_WALL_T = 0.004
_DRAWER_REVEAL = 0.004
_RAIL_W = 0.006
_RAIL_H = 0.007


@dataclass(frozen=True)
class Config:
    door_group: DoorGroup = "single_leaf"
    door_panel: DoorPanel = "glazed_window"
    interior_fitment: InteriorFitment = "open_shelves"
    shelf_count: int = 2
    body_width_m: float | None = None
    body_depth_m: float | None = None
    body_height_m: float | None = None
    bank_drawer_count: int | None = None
    door_swing_rad: float | None = None
    name: str = "Science_First_aid_cabinet"


@dataclass(frozen=True)
class ResolvedConfig:
    door_group: DoorGroup
    door_panel: DoorPanel
    interior_fitment: InteriorFitment
    shelf_count: int
    bank_drawer_count: int
    door_leaf_count: int
    drawer_count: int
    body_width_m: float
    body_depth_m: float
    body_height_m: float
    door_swing_rad: float
    inner_width_m: float
    inner_depth_m: float
    inner_height_m: float
    drawer_zone_height_m: float
    door_zone_bottom_m: float
    door_zone_height_m: float
    drawer_travel_m: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value: float | None, default: float) -> float:
    return default if value is None else float(value)


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    return Config(
        door_group=rng.choice(("single_leaf", "double_leaf")),
        door_panel=rng.choice(("glazed_window", "solid_panel")),
        interior_fitment=rng.choice(("open_shelves", "base_drawer", "drawer_bank")),
        shelf_count=rng.choice((1, 2, 3)),
        body_width_m=round(rng.uniform(0.30, 0.42), 3),
        body_depth_m=round(rng.uniform(0.12, 0.18), 3),
        body_height_m=round(rng.uniform(0.36, 0.52), 3),
        bank_drawer_count=rng.choice((2, 3, 4)),
        door_swing_rad=round(rng.uniform(1.35, 1.72), 3),
        name=f"Science_First_aid_cabinet_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    width = _clamp(_pick(config.body_width_m, 0.34), 0.30, 0.42)
    depth = _clamp(_pick(config.body_depth_m, 0.14), 0.12, 0.18)
    height = _clamp(_pick(config.body_height_m, 0.42), 0.36, 0.52)
    fitment = config.interior_fitment
    bank_n = int(_clamp(int(_pick(config.bank_drawer_count, 3)), 2, 4))
    drawer_count = 0 if fitment == "open_shelves" else (1 if fitment == "base_drawer" else bank_n)
    drawer_zone_h = 0.0 if drawer_count == 0 else (height - 2 * _WALL_T) * 0.42
    door_bottom = _WALL_T + drawer_zone_h
    door_height = height - _WALL_T - door_bottom
    return ResolvedConfig(
        door_group=config.door_group,
        door_panel=config.door_panel,
        interior_fitment=fitment,
        shelf_count=int(_clamp(int(config.shelf_count), 1, 3)),
        bank_drawer_count=bank_n,
        door_leaf_count=1 if config.door_group == "single_leaf" else 2,
        drawer_count=drawer_count,
        body_width_m=width,
        body_depth_m=depth,
        body_height_m=height,
        door_swing_rad=_clamp(_pick(config.door_swing_rad, 1.55), 1.35, 1.72),
        inner_width_m=width - 2 * _WALL_T,
        inner_depth_m=depth - _WALL_T,
        inner_height_m=height - 2 * _WALL_T,
        drawer_zone_height_m=drawer_zone_h,
        door_zone_bottom_m=door_bottom,
        door_zone_height_m=door_height,
        drawer_travel_m=(depth - _WALL_T - 0.012) * 0.58,
        name=config.name,
    )


def _body_shell_cq(r: ResolvedConfig) -> cq.Workplane:
    outer = cq.Workplane("XY").box(r.body_width_m, r.body_depth_m, r.body_height_m)
    cavity = (
        cq.Workplane("XY")
        .box(r.inner_width_m, r.body_depth_m, r.inner_height_m)
        .translate((0.0, _WALL_T / 2 + 0.002, 0.0))
    )
    shell = outer.cut(cavity)
    if r.drawer_count:
        lower_lo = -r.inner_height_m / 2
        lower_hi = lower_lo + r.drawer_zone_height_m
        panel_h = lower_hi - lower_lo
        panel_z = (lower_lo + lower_hi) / 2
        panel = (
            cq.Workplane("XY")
            .box(r.inner_width_m + 0.002, _WALL_T, panel_h)
            .translate((0.0, r.body_depth_m / 2 - _WALL_T / 2, panel_z))
        )
        slot_h = r.drawer_zone_height_m / r.drawer_count
        for index in range(r.drawer_count):
            z = lower_lo + slot_h * (index + 0.5)
            opening = (
                cq.Workplane("XY")
                .box(r.inner_width_m - 0.010, _WALL_T + 0.012, slot_h - _DRAWER_REVEAL)
                .translate((0.0, r.body_depth_m / 2 - _WALL_T / 2, z))
            )
            panel = panel.cut(opening)
        divider = (
            cq.Workplane("XY")
            .box(r.inner_width_m + 0.002, r.inner_depth_m, _WALL_T)
            .translate((0.0, _WALL_T / 2, lower_hi + _WALL_T / 2))
        )
        shell = shell.union(panel).union(divider)
    return shell


def _handle_cq() -> cq.Workplane:
    grip = cq.Workplane("XY").box(0.145, 0.014, 0.007).translate((0.0, 0.0, 0.025))
    left = cq.Workplane("XY").box(0.008, 0.014, 0.025).translate((-0.0685, 0.0, 0.0125))
    right = cq.Workplane("XY").box(0.008, 0.014, 0.025).translate((0.0685, 0.0, 0.0125))
    return grip.union(left).union(right).edges("|Y").fillet(0.002)


def _shelf_cq(r: ResolvedConfig) -> cq.Workplane:
    back = -r.body_depth_m / 2 + _WALL_T - _SHELF_EMBED
    front = r.body_depth_m / 2 - 0.018
    return cq.Workplane("XY").box(r.inner_width_m + 2 * _SHELF_EMBED, front - back, _SHELF_T)


def _knuckles_cq(stations: tuple[float, ...], length: float) -> cq.Workplane:
    result = None
    for station in stations:
        segment = cq.Workplane("XY").cylinder(length, _HINGE_R).translate((0.0, 0.0, station))
        result = segment if result is None else result.union(segment)
    assert result is not None
    return result


def _body_hinge_cq(
    stations: tuple[float, ...], length: float, inward: float
) -> cq.Workplane:
    hinge = _knuckles_cq(stations, length)
    for station in stations:
        strap = (
            cq.Workplane("XY")
            .box(0.010, 0.012, length * 0.72)
            .translate((inward * 0.005, -0.006, station))
        )
        hinge = hinge.union(strap)
    return hinge


def _panel_frame_cq(sign: float, width: float, height: float, thickness: float) -> cq.Workplane:
    center_x = sign * (_HINGE_R + width / 2)
    panel = cq.Workplane("XY").box(width, thickness, height).translate((center_x, 0.0, 0.0))
    border = min(0.038, width * 0.22, height * 0.16)
    opening = (
        cq.Workplane("XY")
        .box(max(width - 2 * border, 0.04), thickness + 0.012, max(height - 2 * border, 0.08))
        .translate((center_x, 0.0, -0.006))
    )
    return panel.cut(opening).edges("|Z").fillet(0.002)


def _solid_panel_cq(sign: float, width: float, height: float, thickness: float) -> cq.Workplane:
    center_x = sign * (_HINGE_R + width / 2)
    return (
        cq.Workplane("XY")
        .box(width, thickness, height)
        .translate((center_x, 0.0, 0.0))
        .edges("|Z")
        .fillet(0.002)
    )


def _cross_cq(sign: float, width: float, face_y: float) -> cq.Workplane:
    cx = sign * (_HINGE_R + width / 2)
    arm = min(0.026, width * 0.16)
    bar = min(0.018, width * 0.11)
    vertical = cq.Workplane("XY").box(bar, 0.0018, 2 * arm)
    horizontal = cq.Workplane("XY").box(2 * arm, 0.0018, bar)
    return vertical.union(horizontal).translate((cx, face_y + 0.0009, -0.012))


def _banner_cq(sign: float, width: float, height: float, thickness: float) -> cq.Workplane:
    cx = sign * (_HINGE_R + width / 2)
    return (
        cq.Workplane("XY")
        .box(max(width - 0.024, 0.045), 0.0018, min(0.018, height * 0.06))
        .translate((cx, thickness / 2 + 0.0009, height / 2 - 0.020))
    )


def _knob_cq(sign: float, width: float, thickness: float) -> cq.Workplane:
    x = sign * (_HINGE_R + width - 0.022)
    stem = cq.Workplane("XY").box(0.007, 0.016, 0.007).translate((x, thickness / 2 + 0.008, 0.0))
    grip = cq.Workplane("XY").sphere(0.010).translate((x, thickness / 2 + 0.022, 0.0))
    return stem.union(grip)


def _drawer_tray_cq(width: float, depth: float, height: float) -> cq.Workplane:
    t = _DRAWER_WALL_T
    floor = cq.Workplane("XY").box(width, depth, t).translate((0.0, -depth / 2, -height / 2 + t / 2))
    back = cq.Workplane("XY").box(width, t, height).translate((0.0, -depth + t / 2, 0.0))
    left = cq.Workplane("XY").box(t, depth, height).translate((-width / 2 + t / 2, -depth / 2, 0.0))
    right = cq.Workplane("XY").box(t, depth, height).translate((width / 2 - t / 2, -depth / 2, 0.0))
    front = cq.Workplane("XY").box(width + 0.008, 0.004, height + 0.004).translate((0.0, 0.002, 0.0))
    return floor.union(back).union(left).union(right).union(front).edges("|Z").fillet(0.0015)


def _drawer_pull_cq() -> cq.Workplane:
    bar = cq.Workplane("XY").box(0.095, 0.007, 0.008).translate((0.0, 0.018, 0.0))
    left = cq.Workplane("XY").box(0.007, 0.018, 0.008).translate((-0.044, 0.009, 0.0))
    right = cq.Workplane("XY").box(0.007, 0.018, 0.008).translate((0.044, 0.009, 0.0))
    return bar.union(left).union(right).edges("|Z").fillet(0.0015).translate((0.0, 0.004, 0.0))


def _axis_mate(name: str, point: tuple[float, float, float], axis: tuple[float, float, float]):
    radial = (1.0, 0.0, 0.0) if abs(axis[0]) < 0.5 else (0.0, 0.0, 1.0)
    provider = AxisInterface(name=f"carcass.{name}", point=point, axis=axis, radial=radial, radius=_HINGE_R)
    consumer = AxisInterface(name=f"moving.{name}", axis=axis, radial=radial, radius=_HINGE_BORE_R)
    return mate_axes(provider, consumer, require_fit=True)


def _interior_fitment_open_shelves_build(body, r: ResolvedConfig) -> None:
    _add_shelves(body, r)


def _interior_fitment_base_drawer_build(body, r: ResolvedConfig) -> None:
    _add_shelves(body, r)


def _interior_fitment_drawer_bank_build(body, r: ResolvedConfig) -> None:
    _add_shelves(body, r)


def _add_shelves(body, r: ResolvedConfig) -> None:
    shelf_mesh = mesh_from_cadquery(_shelf_cq(r), "first_aid_shelf")
    zone_lo = -r.inner_height_m / 2 + r.drawer_zone_height_m + (_WALL_T if r.drawer_count else 0.0)
    zone_hi = r.inner_height_m / 2
    for index in range(r.shelf_count):
        z_local = zone_lo + (index + 1) * (zone_hi - zone_lo) / (r.shelf_count + 1)
        body.visual(
            shelf_mesh,
            origin=Origin(xyz=(0.0, -0.004, r.body_height_m / 2 + z_local)),
            name=f"interior_fitment__{r.interior_fitment}__shelf_{index}", material_class_id="metal.paint_coated",
        )


def _door_panel_glazed_window_build(leaf, sign: float, width: float, height: float, thickness: float, tag: str) -> None:
    leaf.visual(mesh_from_cadquery(_panel_frame_cq(sign, width, height, thickness), f"{tag}_frame"), name=f"{tag}__frame", material_class_id="metal.paint_coated")
    cx = sign * (_HINGE_R + width / 2)
    border = min(0.038, width * 0.22, height * 0.16)
    leaf.visual(
        Box((max(width - 2 * border, 0.04), 0.004, max(height - 2 * border, 0.08))),
        origin=Origin(xyz=(cx, 0.0, -0.006)),
        name=f"{tag}__glass", material_class_id="glass.clear_transparent",
    )


def _door_panel_solid_panel_build(leaf, sign: float, width: float, height: float, thickness: float, tag: str) -> None:
    leaf.visual(mesh_from_cadquery(_solid_panel_cq(sign, width, height, thickness), f"{tag}_panel"), name=f"{tag}__panel", material_class_id="metal.paint_coated")


def _build_one_leaf(model, body, r: ResolvedConfig, index: int, sign: float, hinge_x: float, width: float) -> None:
    tag = f"door_panel__{r.door_panel}__leaf_{index}"
    leaf = model.part(f"door_group__{r.door_group}__leaf_{index}", meta={"role": "door_leaf"})
    leaf_h = r.door_zone_height_m - 2 * _DOOR_REVEAL
    door_t = 0.020
    panel_builder = _door_panel_glazed_window_build if r.door_panel == "glazed_window" else _door_panel_solid_panel_build
    panel_builder(leaf, sign, width, leaf_h, door_t, tag)
    cross_face_y = 0.002 if r.door_panel == "glazed_window" else door_t / 2
    leaf.visual(
        mesh_from_cadquery(_cross_cq(sign, width, cross_face_y), f"{tag}_cross"),
        name=f"{tag}__first_aid_cross",
        material=Material("first_aid_cross", rgba=(0.82, 0.04, 0.04, 1.0)),
        appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    leaf.visual(
        mesh_from_cadquery(_banner_cq(sign, width, leaf_h, door_t), f"{tag}_banner"),
        name=f"{tag}__banner",
        material=Material("first_aid_banner", rgba=(0.96, 0.96, 0.96, 1.0)),
        appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    leaf.visual(mesh_from_cadquery(_knob_cq(sign, width, door_t), f"{tag}_knob"), name=f"{tag}__knob", material_class_id="metal.stainless_matte")
    stations = (-leaf_h * 0.30, 0.0, leaf_h * 0.30)
    leaf.visual(mesh_from_cadquery(_knuckles_cq(stations, leaf_h * 0.18), f"{tag}_knuckles"), name=f"{tag}__hinge_knuckles", material_class_id="metal.stainless_matte")

    z = r.door_zone_bottom_m + r.door_zone_height_m / 2
    point = (hinge_x, r.body_depth_m / 2 + door_t / 2 + _DOOR_GAP, z)
    mate = _axis_mate(f"door_hinge_{index}", point, (0.0, 0.0, 1.0))
    joint_name = f"door_group__{r.door_group}__hinge_{index}"
    limits = MotionLimits(effort=12.0, velocity=1.4, lower=0.0, upper=r.door_swing_rad)
    if sign < 0:
        limits = MotionLimits(effort=12.0, velocity=1.4, lower=-r.door_swing_rad, upper=0.0)
    model.articulation(joint_name, ArticulationType.REVOLUTE, parent=body, child=leaf, origin=mate.origin, axis=mate.axis, motion_limits=limits)
    register_interface_mate(model, joint_name, mate)


def _door_group_single_leaf_build(model, body, r: ResolvedConfig) -> None:
    width = r.body_width_m - 2 * _DOOR_REVEAL - _HINGE_R
    _build_one_leaf(model, body, r, 0, 1.0, -r.body_width_m / 2, width)


def _door_group_double_leaf_build(model, body, r: ResolvedConfig) -> None:
    width = (r.body_width_m - 3 * _DOOR_REVEAL - 2 * _HINGE_R) / 2
    _build_one_leaf(model, body, r, 0, 1.0, -r.body_width_m / 2, width)
    _build_one_leaf(model, body, r, 1, -1.0, r.body_width_m / 2, width)


def _add_drawers(model, body, r: ResolvedConfig) -> None:
    if not r.drawer_count:
        return
    slot_h = r.drawer_zone_height_m / r.drawer_count
    tray_w = r.inner_width_m - 0.014
    tray_d = r.inner_depth_m - 0.012
    tray_h = slot_h - _DRAWER_REVEAL - 0.006
    rail_y = r.body_depth_m / 2 - tray_d / 2 - 0.006
    for index in range(r.drawer_count):
        z = _WALL_T + slot_h * (index + 0.5)
        drawer = model.part(f"interior_fitment__{r.interior_fitment}__drawer_{index}", meta={"role": "drawer"})
        drawer.visual(mesh_from_cadquery(_drawer_tray_cq(tray_w, tray_d, tray_h), f"drawer_{index}_tray"), name=f"interior_fitment__{r.interior_fitment}__drawer_{index}_hollow_tray", material_class_id="metal.paint_coated")
        drawer.visual(mesh_from_cadquery(_drawer_pull_cq(), f"drawer_{index}_pull"), name=f"interior_fitment__{r.interior_fitment}__drawer_{index}_pull", material_class_id="metal.stainless_matte")
        for side in (-1.0, 1.0):
            drawer_x = side * (tray_w / 2 + _RAIL_W / 2)
            body_x = side * (r.inner_width_m / 2 - _RAIL_W / 2)
            drawer.visual(Box((_RAIL_W, tray_d * 0.72, _RAIL_H)), origin=Origin(xyz=(drawer_x, -tray_d * 0.48, 0.0)), name=f"interior_fitment__{r.interior_fitment}__drawer_{index}_rail_{'left' if side < 0 else 'right'}", material_class_id="metal.stainless_matte")
            body.visual(Box((_RAIL_W, tray_d * 0.72, _RAIL_H)), origin=Origin(xyz=(body_x, rail_y, z)), name=f"interior_fitment__{r.interior_fitment}__body_rail_{index}_{'left' if side < 0 else 'right'}", material_class_id="metal.stainless_matte")
        point = (0.0, r.body_depth_m / 2 - 0.006, z)
        mate = _axis_mate(f"drawer_slide_{index}", point, (0.0, 1.0, 0.0))
        joint_name = f"interior_fitment__{r.interior_fitment}__drawer_joint_{index}"
        model.articulation(joint_name, ArticulationType.PRISMATIC, parent=body, child=drawer, origin=mate.origin, axis=mate.axis, motion_limits=MotionLimits(effort=30.0, velocity=0.45, lower=0.0, upper=r.drawer_travel_m))
        register_interface_mate(model, joint_name, mate)


_FITMENT_BUILDERS = {
    "open_shelves": _interior_fitment_open_shelves_build,
    "base_drawer": _interior_fitment_base_drawer_build,
    "drawer_bank": _interior_fitment_drawer_bank_build,
}
_DOOR_BUILDERS = {"single_leaf": _door_group_single_leaf_build, "double_leaf": _door_group_double_leaf_build}


def build_first_aid_cabinet(config: Config | None = None, *, assets=None) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    body = model.part("cabinet_body", meta={"role": "carcass"})
    body.visual(mesh_from_cadquery(_body_shell_cq(r), "cabinet_body_shell"), origin=Origin(xyz=(0.0, 0.0, r.body_height_m / 2)), name="interior_fitment__host__hollow_body_shell", material_class_id="metal.paint_coated")
    body.visual(mesh_from_cadquery(_handle_cq(), "cabinet_handle"), origin=Origin(xyz=(0.0, -0.012, r.body_height_m)), name="interior_fitment__host__carry_handle", material_class_id="metal.stainless_matte")
    _FITMENT_BUILDERS[r.interior_fitment](body, r)
    _add_drawers(model, body, r)

    knuckle_len = r.door_zone_height_m * 0.12
    body_stations = (-r.door_zone_height_m * 0.15, r.door_zone_height_m * 0.15)
    zc = r.door_zone_bottom_m + r.door_zone_height_m / 2
    for index, x in enumerate((-r.body_width_m / 2, r.body_width_m / 2) if r.door_leaf_count == 2 else (-r.body_width_m / 2,)):
        hinge_y = r.body_depth_m / 2 + 0.012
        inward = 1.0 if x < 0 else -1.0
        body.visual(
            mesh_from_cadquery(
                _body_hinge_cq(body_stations, knuckle_len, inward),
                f"body_hinge_{index}",
            ),
            origin=Origin(xyz=(x, hinge_y, zc)),
            name=f"door_group__{r.door_group}__body_hinge_{index}", material_class_id="metal.stainless_matte",
        )
    _DOOR_BUILDERS[r.door_group](model, body, r)
    model.meta["slot_choices"] = (("door_group", r.door_group), ("door_panel", r.door_panel), ("interior_fitment", r.interior_fitment), ("shelf_count", str(r.shelf_count)))
    return model


def build_seeded_first_aid_cabinet(seed: int) -> ArticulatedObject:
    return build_first_aid_cabinet(config_from_seed(seed))


def run_first_aid_cabinet_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    roles: dict[str, list[object]] = {}
    for part in object_model.parts:
        role = str(part.meta.get("role", ""))
        roles.setdefault(role, []).append(part)
    ctx.check("category_anchor: one hollow wall cabinet carcass", len(roles.get("carcass", [])) == 1)
    leaves = roles.get("door_leaf", [])
    leaf_joints = [joint for joint in object_model.articulations if joint.child in {leaf.name for leaf in leaves}]
    ctx.check("category_anchor: every door leaf hinges from a jamb", len(leaves) == r.door_leaf_count and len(leaf_joints) == r.door_leaf_count and all(j.articulation_type == ArticulationType.REVOLUTE for j in leaf_joints), details=f"leaves={len(leaves)} joints={len(leaf_joints)}")
    crosses = [visual.name for leaf in leaves for visual in leaf.visuals if "first_aid_cross" in str(visual.name)]
    ctx.check("category_anchor: first aid cross is present", len(crosses) == r.door_leaf_count, details=str(crosses))
    moved_forward = True
    for leaf, joint in zip(leaves, leaf_joints):
        rest = ctx.part_world_aabb(leaf)
        target = joint.motion_limits.upper if (joint.motion_limits.upper or 0.0) > 0 else joint.motion_limits.lower
        with ctx.pose({joint: target * 0.7}):
            opened = ctx.part_world_aabb(leaf)
        moved_forward = moved_forward and rest is not None and opened is not None and opened[1][1] > rest[1][1] + 0.015
    ctx.check("category_anchor: door free edges swing forward", moved_forward)

    drawers = roles.get("drawer", [])
    drawer_joints = [joint for joint in object_model.articulations if joint.child in {drawer.name for drawer in drawers}]
    ctx.check("category_anchor: every drawer is an independent moving child", len(drawers) == r.drawer_count and len(drawer_joints) == r.drawer_count and all(j.articulation_type == ArticulationType.PRISMATIC for j in drawer_joints), details=f"drawers={len(drawers)} expected={r.drawer_count}")
    hollow_named = all(any("hollow_tray" in str(v.name) for v in drawer.visuals) for drawer in drawers)
    ctx.check("category_anchor: drawer trays are hollow", hollow_named)
    rails_ok = all(sum("_rail_" in str(v.name) for v in drawer.visuals) == 2 for drawer in drawers)
    travel_ok = all(j.axis == (0.0, 1.0, 0.0) and (j.motion_limits.upper or 0.0) > 0 for j in drawer_joints)
    ctx.check("category_anchor: drawers extend forward on bilateral rails", rails_ok and travel_ok)

    shelves = [v.name for v in object_model.get_part("cabinet_body").visuals if "__shelf_" in str(v.name)]
    ctx.check("shelf ladder matches shelf_count", len(shelves) == r.shelf_count, details=str(shelves))
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)
    return ctx.report()


run_first_aid_cabinet_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case("small_double_glazed_bank_four", {"door_group": "double_leaf", "door_panel": "glazed_window", "interior_fitment": "drawer_bank", "shelf_count": 3, "bank_drawer_count": 4, "body_width_m": 0.30, "body_depth_m": 0.12, "body_height_m": 0.36, "door_swing_rad": 1.72}, reason="smallest host with maximum drawer and shelf counts and both glazed leaves at full swing"),
    corner_case("large_single_solid_base", {"door_group": "single_leaf", "door_panel": "solid_panel", "interior_fitment": "base_drawer", "shelf_count": 1, "bank_drawer_count": 2, "body_width_m": 0.42, "body_depth_m": 0.18, "body_height_m": 0.52, "door_swing_rad": 1.72}, reason="largest and deepest host with the widest single solid leaf and full travel"),
)


__all__ = ["TEMPLATE_CORNERS", "TEMPLATE_DOMAIN", "Config", "ResolvedConfig", "build_first_aid_cabinet", "build_seeded_first_aid_cabinet", "config_from_seed", "resolve_config", "run_first_aid_cabinet_tests"]
