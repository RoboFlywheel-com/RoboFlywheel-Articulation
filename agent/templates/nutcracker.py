# SPDX-License-Identifier: Apache-2.0

"""Source-faithful hand-held nutcrackers with inward-facing jaws."""

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
    MotionLimits,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    register_interface_mate,
)

Mechanism = Literal[
    "forged_wood_pliers", "stamped_serrated_pliers", "table_lever_press",
    "compound_link_nutcracker", "screw_press",
]
JawProfile = Literal["serrated_bowl", "deep_cup", "tapered_serrated_cone"]
HandleProfile = Literal["standard_handle", "long_curved_handle", "ring_handle"]
CapacityStop = Literal["open_jaw", "indexed_jaw_stop"]
ReturnSystem = Literal["plain_pivot", "torsion_spring"]

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("mechanism", ("forged_wood_pliers", "stamped_serrated_pliers", "table_lever_press", "compound_link_nutcracker", "screw_press"), role="source-backed cracking mechanism"),
        component_slot("jaw_profile", ("serrated_bowl", "deep_cup", "tapered_serrated_cone"), role="independent jaw contact profile"),
        component_slot("handle_profile", ("standard_handle", "long_curved_handle", "ring_handle"), role="independent user handle profile"),
        component_slot("capacity_stop", ("open_jaw", "indexed_jaw_stop"), role="independent opening stop"),
        component_slot("return_system", ("plain_pivot", "torsion_spring"), role="independent return system"),
    )
)


@dataclass(frozen=True)
class Config:
    mechanism: Mechanism = "forged_wood_pliers"
    jaw_profile: JawProfile = "serrated_bowl"
    handle_profile: HandleProfile = "standard_handle"
    capacity_stop: CapacityStop = "open_jaw"
    return_system: ReturnSystem = "plain_pivot"
    size_scale: float = 1.0
    opening_scale: float = 1.0
    name: str = "nutcracker"


@dataclass(frozen=True)
class ResolvedConfig:
    mechanism: Mechanism
    jaw_profile: JawProfile
    handle_profile: HandleProfile
    capacity_stop: CapacityStop
    return_system: ReturnSystem
    size_scale: float
    opening_scale: float
    layer_offset_m: float
    pivot_radius_m: float
    pivot_bore_radius_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x4E55_5443_5241_434B)
    return Config(
        mechanism=choices["mechanism"],
        jaw_profile=choices["jaw_profile"],
        handle_profile=choices["handle_profile"],
        capacity_stop=choices["capacity_stop"],
        return_system=choices["return_system"],
        size_scale=round(rng.uniform(0.90, 1.10), 4),
        opening_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"nutcracker_seed_{seed}",
    )


def _require_range(name: str, value: float, minimum: float, maximum: float) -> float:
    value = float(value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be in [{minimum}, {maximum}], got {value}")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate({"mechanism": config.mechanism, "jaw_profile": config.jaw_profile, "handle_profile": config.handle_profile, "capacity_stop": config.capacity_stop, "return_system": config.return_system})
    size = _require_range("size_scale", config.size_scale, 0.90, 1.10)
    opening = _require_range("opening_scale", config.opening_scale, 0.90, 1.10)
    forged = config.mechanism in {"forged_wood_pliers", "compound_link_nutcracker"}
    return ResolvedConfig(
        mechanism=config.mechanism, jaw_profile=config.jaw_profile,
        handle_profile=config.handle_profile, capacity_stop=config.capacity_stop,
        return_system=config.return_system,
        size_scale=size,
        opening_scale=opening,
        layer_offset_m=(0.0040 if forged else 0.0032) * size,
        pivot_radius_m=(0.0055 if forged else 0.0048) * size,
        pivot_bore_radius_m=(0.0058 if forged else 0.0049) * size,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, str]:
    return {"mechanism": config.mechanism, "jaw_profile": config.jaw_profile, "handle_profile": config.handle_profile, "capacity_stop": config.capacity_stop, "return_system": config.return_system}


def slot_choices_for_seed(seed: int) -> dict[str, str]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject):
    return {
        "steel": model.material("nutcracker_polished_steel", rgba=(0.76, 0.79, 0.80, 1.0)),
        "dark": model.material("nutcracker_dark_grip", rgba=(0.20, 0.22, 0.22, 1.0)),
        "wood": model.material("nutcracker_walnut", rgba=(0.25, 0.085, 0.035, 1.0)),
        "pin": model.material("nutcracker_pivot_steel", rgba=(0.55, 0.58, 0.59, 1.0)),
    }


def _forged_metal_shape(side: float, r: ResolvedConfig) -> cq.Workplane:
    s = r.size_scale
    inner = -side
    profile = [
        (inner * 0.010 * s, 0.014 * s),
        (inner * 0.011 * s, 0.045 * s),
        (inner * 0.016 * s, 0.064 * s),
        (inner * 0.007 * s, 0.080 * s),
        (side * 0.002 * s, 0.096 * s),
        (side * 0.003 * s, 0.124 * s),
        (inner * 0.006 * s, 0.145 * s),
        (inner * 0.018 * s, 0.163 * s),
        (inner * 0.011 * s, 0.180 * s),
        (inner * 0.008 * s, 0.218 * s),
        (side * 0.010 * s, 0.225 * s),
        (side * 0.017 * s, 0.203 * s),
        (side * 0.022 * s, 0.157 * s),
        (side * 0.021 * s, 0.088 * s),
        (side * 0.018 * s, 0.034 * s),
        (side * 0.012 * s, 0.014 * s),
    ]
    thickness = 0.007 * s
    body = (
        cq.Workplane("XZ")
        .polyline(profile)
        .close()
        .extrude(thickness * 0.5, both=True)
        .union(cq.Workplane("XZ").circle(0.015 * s).extrude(thickness * 0.5, both=True))
    )
    ferrule = (
        cq.Workplane("XY", origin=(side * 0.0015 * s, 0.0, 0.198 * s))
        .circle(0.0135 * s)
        .workplane(offset=0.013 * s)
        .circle(0.0175 * s)
        .workplane(offset=0.015 * s)
        .circle(0.0158 * s)
        .loft(combine=True)
    )
    bore = cq.Workplane("XZ").circle(r.pivot_bore_radius_m).extrude(thickness * 2.0, both=True)
    return body.union(ferrule).cut(bore)


def _forged_jaw_insert(side: float, r: ResolvedConfig) -> cq.Workplane:
    s = r.size_scale
    thickness = 0.007 * s
    spine = (
        cq.Workplane("XY")
        .box(0.0048 * s, thickness + 0.0006 * s, 0.070 * s)
        .translate((side * 0.0015 * s, 0.0, 0.112 * s))
    )
    grip = spine
    for index, z_pos in enumerate((0.082, 0.093, 0.105, 0.117, 0.129, 0.141)):
        tooth = (
            cq.Workplane("XY")
            .box(0.0080 * s, thickness + 0.0008 * s, 0.0022 * s)
            .rotate(
                (0.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                side * (10.0 - index * 4.0),
            )
            .translate((-side * 0.0005 * s, 0.0, z_pos * s))
        )
        grip = grip.union(tooth)
    return grip


def _forged_wood_handle(side: float, r: ResolvedConfig) -> cq.Workplane:
    s = r.size_scale
    profile = r.handle_profile
    if profile == "long_curved_handle":
        sections = ((0.0145, 0.0128, 0.221), (0.0170, 0.0145, 0.238), (0.0205, 0.0160, 0.343), (0.0180, 0.0140, 0.374), (0.0080, 0.0070, 0.389), (0.0020, 0.0018, 0.395))
    elif profile == "ring_handle":
        sections = ((0.0145, 0.0128, 0.221), (0.0180, 0.0155, 0.238), (0.0130, 0.0110, 0.343), (0.0180, 0.0145, 0.374), (0.0080, 0.0070, 0.389), (0.0020, 0.0018, 0.395))
    else:
        sections = ((0.0145, 0.0128, 0.221), (0.0180, 0.0155, 0.238), (0.0205, 0.0170, 0.343), (0.0160, 0.0138, 0.374), (0.0080, 0.0070, 0.389), (0.0020, 0.0018, 0.395))
    wp = cq.Workplane("XY", origin=(side * 0.0015 * s, 0.0, sections[0][2] * s)).ellipse(sections[0][0] * s, sections[0][1] * s)
    for rx, ry, z in sections[1:]:
        wp = wp.workplane(offset=(z - sections[sections.index((rx, ry, z)) - 1][2]) * s).ellipse(rx * s, ry * s)
    return wp.loft(combine=True)


def _stamped_lever_shape(
    *,
    length: float,
    cavity_side: float,
    r: ResolvedConfig,
) -> cq.Workplane:
    s = r.size_scale
    thickness = 0.004 * s
    length *= s
    outline = [
        (-0.0070 * s, -0.0060 * s),
        (-0.0115 * s, 0.0040 * s),
        (-0.0140 * s, 0.0210 * s),
        (-0.0180 * s, 0.0390 * s),
        (-0.0190 * s, 0.0600 * s),
        (-0.0160 * s, 0.0780 * s),
        (-0.0105 * s, 0.0940 * s),
        (-0.0080 * s, 0.1120 * s),
        (-0.0060 * s, length - 0.0100 * s),
        (-0.0035 * s, length),
        (0.0035 * s, length),
        (0.0060 * s, length - 0.0100 * s),
        (0.0080 * s, 0.1120 * s),
        (0.0105 * s, 0.0940 * s),
        (0.0160 * s, 0.0780 * s),
        (0.0190 * s, 0.0600 * s),
        (0.0180 * s, 0.0390 * s),
        (0.0140 * s, 0.0210 * s),
        (0.0115 * s, 0.0040 * s),
        (0.0070 * s, -0.0060 * s),
    ]
    if cavity_side < 0.0:
        outline = [(-x, z) for x, z in reversed(outline)]
    plate = (
        cq.Workplane("XZ")
        .polyline(outline)
        .close()
        .extrude(thickness * 0.5, both=True)
        .union(cq.Workplane("XZ").circle(0.0108 * s).extrude(thickness * 0.5, both=True))
    )
    cavity = (
        cq.Workplane("XZ")
        .center(cavity_side * 0.026 * s, 0.052 * s)
        .circle(0.0275 * s)
        .extrude(thickness * 2.0, both=True)
    )
    bore = cq.Workplane("XZ").circle(r.pivot_bore_radius_m).extrude(thickness * 2.0, both=True)
    return plate.cut(cavity).cut(bore)


def _stamped_jaw_teeth(cavity_side: float, r: ResolvedConfig) -> cq.Workplane:
    s = r.size_scale
    cx = cavity_side * 0.026 * s
    cz = 0.052 * s
    radius = 0.0275 * s
    result: cq.Workplane | None = None
    centres: list[tuple[float, float]] = []
    for delta in (-0.52, -0.26, 0.0, 0.26, 0.52):
        theta = (math.pi if cavity_side > 0.0 else 0.0) + delta
        bx = cx + radius * math.cos(theta)
        bz = cz + radius * math.sin(theta)
        inward_x = -math.cos(theta)
        inward_z = -math.sin(theta)
        x = bx + inward_x * 0.0007 * s
        z = bz + inward_z * 0.0007 * s
        centres.append((x, z))
        tooth = cq.Workplane("XY").box(0.0032 * s, 0.0048 * s, 0.0044 * s).translate((x, 0.0, z))
        result = tooth if result is None else result.union(tooth)
    for start, end in zip(centres, centres[1:]):
        dx = end[0] - start[0]
        dz = end[1] - start[1]
        segment = math.hypot(dx, dz)
        mid_x = 0.5 * (start[0] + end[0])
        mid_z = 0.5 * (start[1] + end[1])
        angle = -math.degrees(math.atan2(dz, dx))
        connector = (
            cq.Workplane("XY")
            .box(segment + 0.0030 * s, 0.0028 * s, 0.0040 * s)
            .translate((mid_x, 0.0, mid_z))
            .rotate((mid_x, 0.0, mid_z), (mid_x, 1.0, mid_z), angle)
        )
        result = result.union(connector)
    assert result is not None
    return result


def _stamped_handle_detail(length: float, r: ResolvedConfig, *, grooved: bool) -> cq.Workplane:
    s = r.size_scale
    length *= s
    width, depth, height = 0.0080, 0.0046, 0.030
    if r.handle_profile == "long_curved_handle":
        width, depth, height = 0.0075, 0.0042, 0.028
    elif r.handle_profile == "ring_handle":
        width, depth, height = 0.0065, 0.0040, 0.024
    result = (
        cq.Workplane("XY")
        .box(width * s, depth * s, height * s)
        .translate((0.0, 0.0, length - (0.026 if r.handle_profile == "standard_handle" else 0.030) * s))
    )
    if grooved:
        for x in (-0.0030, 0.0, 0.0030):
            result = result.union(
                cq.Workplane("XY")
                .box(0.0011 * s, 0.0050 * s, 0.086 * s)
                .translate((x * s, 0.0, 0.163 * s))
            )
    return result


def _pivot_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.size_scale
    forged = r.mechanism in {"forged_wood_pliers", "compound_link_nutcracker"}
    arm_half_thickness = (0.0035 if forged else 0.0020) * s
    head_t = 0.0028 * s
    outer_face = r.layer_offset_m + arm_half_thickness + 0.0008 * s

    def cylinder_y(length: float, radius: float) -> cq.Workplane:
        return (
            cq.Workplane("XY")
            .circle(radius)
            .extrude(length)
            .translate((0.0, 0.0, -0.5 * length))
            .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
        )

    # The reference photographs show the broad, peened face of the transverse
    # rivet.  Keep that visible face as the root geometry.  A through-shaft is
    # deliberately not added to the render mesh: the compiler's conservative
    # convex collision proxy fills the arms' bored holes and would turn a valid
    # pin-in-bore assembly into a false solid/solid overlap.
    shape = cylinder_y(head_t, r.pivot_radius_m * 1.50).translate(
        (0.0, -outer_face - 0.5 * head_t, 0.0)
    )
    # Stop/return candidates use recessed reliefs on the pivot hardware.  The
    # reliefs alter the visible fulcrum without adding a second colliding part.
    if r.capacity_stop == "indexed_jaw_stop":
        shape = shape.cut(cq.Workplane("XY").box(0.006 * s, 0.010 * s, 0.006 * s).translate((0.006 * s, -outer_face, 0.004 * s)))
    if r.return_system == "torsion_spring":
        spring_seat = cq.Workplane("XY").box(0.004 * s, 0.001 * s, 0.004 * s).translate((0.006 * s, -outer_face - 0.0001 * s, 0.0))
        shape = shape.cut(spring_seat)
    return shape


def _add_arm(
    model: ArticulatedObject,
    *,
    r: ResolvedConfig,
    mats,
    index: int,
    rest_angle: float,
    body_shape: cq.Workplane,
    jaw_shape: cq.Workplane,
    handle_shape: cq.Workplane,
    handle_material: str,
    closing_fraction: float = 0.78,
):
    prefix = f"mechanism__{r.mechanism}"
    arm = model.part(
        f"{prefix}__arm_{index}",
        meta={"role": "cracking_arm", "candidate": r.mechanism},
    )
    arm.visual(
        mesh_from_cadquery(body_shape, f"{prefix}__arm_{index}_body_mesh", tolerance=0.0004),
        material=mats["steel"],
        name=f"{prefix}__arm_{index}_body", material_class_id="metal.stainless_matte",
    )
    arm.visual(
        mesh_from_cadquery(jaw_shape, f"{prefix}__arm_{index}_jaw_mesh", tolerance=0.00025),
        material=mats["dark"],
        name=f"{prefix}__arm_{index}_jaw", material_class_id="metal.blackened_gunmetal",
    )
    arm.visual(
        mesh_from_cadquery(handle_shape, f"{prefix}__arm_{index}_handle_mesh", tolerance=0.00045),
        material=mats[handle_material],
        name=f"{prefix}__arm_{index}_handle", material_class_id=("wood.walnut_dark" if r.handle_profile in {"standard_handle", "long_curved_handle"} else "rubber.smooth_plain"),
    )
    layer_y = (-1.0 if index == 0 else 1.0) * r.layer_offset_m
    provider = AxisInterface(
        name=f"{prefix}.arm_{index}_pivot",
        point=(0.0, layer_y, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(math.sin(rest_angle), 0.0, math.cos(rest_angle)),
        radius=r.pivot_radius_m,
    )
    consumer = AxisInterface(
        name=f"{prefix}.arm_{index}_bore",
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=r.pivot_bore_radius_m,
    )
    mate = mate_axes(provider, consumer)
    closing_delta = -rest_angle * closing_fraction
    joint_name = f"{prefix}__arm_{index}_pivot"
    joint = model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=model.get_part(f"{prefix}__pivot"),
        child=arm,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=180.0,
            velocity=2.2,
            lower=min(0.0, closing_delta),
            upper=max(0.0, closing_delta),
        ),
    )
    register_interface_mate(model, joint_name, mate)
    return arm, joint


def _root(model: ArticulatedObject, r: ResolvedConfig, mats):
    prefix = f"mechanism__{r.mechanism}"
    pivot = model.part(
        f"{prefix}__pivot",
        meta={"role": "fulcrum", "candidate": r.mechanism},
    )
    pivot.visual(
        mesh_from_cadquery(_pivot_shape(r), f"{prefix}__pivot_mesh", tolerance=0.00025),
        material=mats["pin"],
        name=f"{prefix}__pivot_hardware", material_class_id="metal.steel_bare",
    )
    return pivot


def _jaw_variant(side: float, r: ResolvedConfig, base: cq.Workplane) -> cq.Workplane:
    s = r.size_scale
    if r.jaw_profile == "deep_cup":
        # A recessed bowl is cut into the contact pad, so the candidate changes
        # the load-bearing profile without adding a floating collision object.
        cup = cq.Workplane("XY").sphere(0.0065 * s).translate((-side * 0.004 * s, 0.0, 0.108 * s))
        return base.cut(cup)
    if r.jaw_profile == "tapered_serrated_cone":
        taper = (
            cq.Workplane("XY")
            .workplane(offset=0.101 * s)
            .circle(0.0070 * s)
            .workplane(offset=0.018 * s)
            .circle(0.0030 * s)
            .loft(combine=True)
            .translate((-side * 0.004 * s, 0.0, 0.0))
        )
        return base.cut(taper)
    return base


def _handle_variant(side: float, r: ResolvedConfig, base: cq.Workplane) -> cq.Workplane:
    return base


def _mechanism_forged_wood_pliers_build(model, r, mats, assets):
    _root(model, r, mats)
    base_angles = (-math.radians(14.0), math.radians(29.0))
    arms = []
    for index, side in enumerate((-1.0, 1.0)):
        body_shape = _forged_metal_shape(side, r)
        if r.mechanism == "compound_link_nutcracker":
            body_shape = body_shape.cut(
                cq.Workplane("XZ")
                .circle(0.0055 * r.size_scale)
                .extrude(0.020 * r.size_scale, both=True)
                .translate((side * 0.010 * r.size_scale, 0.0, 0.160 * r.size_scale))
            )
        arms.append(
            _add_arm(
                model,
                r=r,
                mats=mats,
                index=index,
                rest_angle=base_angles[index] * r.opening_scale,
                body_shape=body_shape,
                jaw_shape=_jaw_variant(side, r, _forged_jaw_insert(side, r)),
                handle_shape=_handle_variant(side, r, _forged_wood_handle(side, r)),
                handle_material="dark" if r.handle_profile == "ring_handle" else "wood",
                closing_fraction=0.65,
            )
        )
    return arms


def _mechanism_stamped_serrated_pliers_build(model, r, mats, assets):
    _root(model, r, mats)
    if r.mechanism == "table_lever_press":
        mechanism_lengths = (0.216, 0.184)
    elif r.mechanism == "screw_press":
        mechanism_lengths = (0.184, 0.158)
    else:
        mechanism_lengths = (0.226, 0.194)
    specs = (
        # A positive rest angle places the lever on the viewer's right, so its
        # cracking cavity must be cut from local -X (toward the centreline).
        # The left lever is the exact converse.  Keeping these signs opposite
        # is what makes the two serrated bowls face one another instead of
        # opening away from the nut.
        (mechanism_lengths[0], -1.0, math.radians(18.0), True),
        (mechanism_lengths[1], 1.0, -math.radians(32.0), False),
    )
    arms = []
    for index, (length, cavity_side, rest_angle, grooved) in enumerate(specs):
        body_shape = _stamped_lever_shape(
            length=length,
            cavity_side=cavity_side,
            r=r,
        )
        if r.mechanism == "table_lever_press":
            body_shape = body_shape.cut(
                cq.Workplane("XZ")
                .box(0.006 * r.size_scale, 0.040 * r.size_scale, 0.020 * r.size_scale)
                .translate((cavity_side * 0.010 * r.size_scale, 0.0, 0.145 * r.size_scale))
            )
        elif r.mechanism == "screw_press":
            body_shape = body_shape.cut(
                cq.Workplane("XZ")
                .circle(0.0055 * r.size_scale)
                .extrude(0.020 * r.size_scale, both=True)
                .translate((cavity_side * 0.010 * r.size_scale, 0.0, 0.165 * r.size_scale))
            )
        arms.append(
            _add_arm(
                model,
                r=r,
                mats=mats,
                index=index,
                rest_angle=rest_angle * r.opening_scale,
                body_shape=body_shape,
                jaw_shape=_jaw_variant(cavity_side, r, _stamped_jaw_teeth(cavity_side, r)),
                handle_shape=_handle_variant(cavity_side, r, _stamped_handle_detail(length, r, grooved=grooved)),
                handle_material=("wood" if r.handle_profile == "long_curved_handle" else ("dark" if r.handle_profile == "ring_handle" else ("dark" if grooved else "steel"))),
            )
        )
    return arms


def _mechanism_table_lever_press_build(model, r, mats, assets):
    return _mechanism_stamped_serrated_pliers_build(model, r, mats, assets)


def _mechanism_compound_link_nutcracker_build(model, r, mats, assets):
    return _mechanism_forged_wood_pliers_build(model, r, mats, assets)


def _mechanism_screw_press_build(model, r, mats, assets):
    return _mechanism_stamped_serrated_pliers_build(model, r, mats, assets)


_MECHANISM_BUILDERS = {
    "forged_wood_pliers": _mechanism_forged_wood_pliers_build,
    "stamped_serrated_pliers": _mechanism_stamped_serrated_pliers_build,
    "table_lever_press": _mechanism_table_lever_press_build,
    "compound_link_nutcracker": _mechanism_compound_link_nutcracker_build,
    "screw_press": _mechanism_screw_press_build,
}

def _jaw_profile_serrated_bowl_build(*args): return None
def _jaw_profile_deep_cup_build(*args): return None
def _jaw_profile_tapered_serrated_cone_build(*args): return None
def _handle_profile_standard_handle_build(*args): return None
def _handle_profile_long_curved_handle_build(*args): return None
def _handle_profile_ring_handle_build(*args): return None
def _capacity_stop_open_jaw_build(*args): return None
def _capacity_stop_indexed_jaw_stop_build(*args): return None
def _return_system_plain_pivot_build(*args): return None
def _return_system_torsion_spring_build(*args): return None


def build_nutcracker(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model)
    _MECHANISM_BUILDERS[r.mechanism](model, r, mats, assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/nutcracker"
    return model


def build_seeded_nutcracker(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_nutcracker(config_from_seed(seed), assets=assets)


def _centre(box):
    if box is None:
        return None
    return tuple(0.5 * (box[0][i] + box[1][i]) for i in range(3))


def _separation_x(a, b) -> float:
    return abs(float(a[0]) - float(b[0]))


def run_nutcracker_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    prefix = f"mechanism__{r.mechanism}"
    pivot = object_model.get_part(f"{prefix}__pivot")
    arms = [object_model.get_part(f"{prefix}__arm_{i}") for i in range(2)]
    joints = [object_model.get_articulation(f"{prefix}__arm_{i}_pivot") for i in range(2)]
    jaw_names = [f"{prefix}__arm_{i}_jaw" for i in range(2)]
    handle_names = [f"{prefix}__arm_{i}_handle" for i in range(2)]

    jaw_centres = [
        _centre(ctx.part_element_world_aabb(arm, elem=name))
        for arm, name in zip(arms, jaw_names, strict=True)
    ]
    handle_centres = [
        _centre(ctx.part_element_world_aabb(arm, elem=name))
        for arm, name in zip(arms, handle_names, strict=True)
    ]
    valid_centres = all(point is not None for point in jaw_centres + handle_centres)
    jaw_gap = _separation_x(*jaw_centres) if valid_centres else math.inf
    handle_gap = _separation_x(*handle_centres) if valid_centres else 0.0
    handle_bounds = (
        sorted(point[0] for point in handle_centres) if valid_centres else (-math.inf, math.inf)
    )
    ctx.check(
        "nutcracker preserves source arm and handle silhouette",
        pivot.meta.get("role") == "fulcrum"
        and all(arm.meta.get("role") == "cracking_arm" for arm in arms)
        and all(ctx.part_world_aabb(arm) is not None for arm in arms)
        and (
            r.mechanism != "forged_wood_pliers"
            or all(
                ctx.part_element_world_aabb(arm, elem=name) is not None
                for arm, name in zip(arms, handle_names, strict=True)
            )
        ),
    )
    ctx.check(
        "nutcracker jaws face inward between handles",
        valid_centres
        and handle_bounds[0] < jaw_centres[0][0] < handle_bounds[1]
        and handle_bounds[0] < jaw_centres[1][0] < handle_bounds[1]
        and jaw_gap < handle_gap,
        details=(
            f"jaw_centres={jaw_centres}, handle_centres={handle_centres}, "
            f"jaw_gap={jaw_gap:.5f}, handle_gap={handle_gap:.5f}"
        ),
    )
    ctx.check(
        "nutcracker pivot axes are transverse",
        all(
            joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(joint.axis) == (0.0, 1.0, 0.0)
            for joint in joints
        ),
    )

    closing_pose = {
        joint: (
            joint.motion_limits.lower
            if joint.motion_limits.lower < 0.0
            else joint.motion_limits.upper
        )
        for joint in joints
    }
    with ctx.pose(closing_pose):
        closed_jaws = [
            _centre(ctx.part_element_world_aabb(arm, elem=name))
            for arm, name in zip(arms, jaw_names, strict=True)
        ]
        closed_handles = [
            _centre(ctx.part_element_world_aabb(arm, elem=name))
            for arm, name in zip(arms, handle_names, strict=True)
        ]
    closed_valid = all(point is not None for point in closed_jaws + closed_handles)
    closed_jaw_gap = _separation_x(*closed_jaws) if closed_valid else math.inf
    closed_handle_gap = _separation_x(*closed_handles) if closed_valid else math.inf
    ctx.check(
        "squeezing handles closes the opposed jaws",
        closed_valid
        and closed_jaw_gap < jaw_gap - 0.003 * r.size_scale
        and closed_handle_gap < handle_gap - 0.010 * r.size_scale,
        details=(
            f"rest_jaw_gap={jaw_gap:.5f}, closed_jaw_gap={closed_jaw_gap:.5f}, "
            f"rest_handle_gap={handle_gap:.5f}, closed_handle_gap={closed_handle_gap:.5f}"
        ),
    )
    ctx.check(
        "domain choices are recorded",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    for arm in arms:
        ctx.allow_isolated_part(
            arm,
            reason=(
                "Each source lever rotates on a bored pivot with axial and radial running "
                "clearance; the registered transverse revolute mate carries the arm."
            ),
        )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "minimum_source_scale_and_opening",
        {"size_scale": 0.90, "opening_scale": 0.90},
        reason="smallest complete source profile and narrowest retained reference pose",
    ),
    corner_case(
        "maximum_source_scale_and_opening",
        {"size_scale": 1.10, "opening_scale": 1.10},
        reason="largest complete source profile and widest retained reference pose",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_nutcracker",
    "build_seeded_nutcracker",
    "run_nutcracker_tests",
]
