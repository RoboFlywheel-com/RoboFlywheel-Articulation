# SPDX-License-Identifier: Apache-2.0

"""Seated-height dressing tables (pictureX/0611).

The category host is always one vanity carcass carrying N pull-out drawers under
a worktop plus exactly one mirror assembly standing on that worktop.  Three
slots vary: the carcass and its support (`body_form`), the drawer front hardware
(`drawer_front`) and the mirror assembly (`mirror_form`); `drawer_count` is the
multiplicity applied to `drawer_front`.

Source evidence lives in
`articraft_template_authoring/source_maps/pictureX_0611_Dressing_table.md`.
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

BodyForm = Literal[
    "rect_carcass_tapered_legs",
    "kidney_plan_cabriole",
    "d_panel_carcass",
    "pedestal_knee_hole",
]
DrawerFront = Literal["knob_front", "bar_handle_front"]
MirrorForm = Literal[
    "swing_ring_mirror",
    "trunnion_oval_mirror",
    "lift_top_mirror",
    "sliding_mirror_storage",
    "jewellery_door_mirror",
]

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "body_form",
            (
                "rect_carcass_tapered_legs",
                "kidney_plan_cabriole",
                "d_panel_carcass",
                "pedestal_knee_hole",
            ),
            role="source-backed carcass plan and support family",
        ),
        component_slot(
            "drawer_front",
            ("knob_front", "bar_handle_front"),
            role="source-backed drawer front hardware",
        ),
        component_slot(
            "mirror_form",
            (
                "swing_ring_mirror",
                "trunnion_oval_mirror",
                "lift_top_mirror",
                "sliding_mirror_storage",
                "jewellery_door_mirror",
            ),
            role="source-backed mirror assembly",
        ),
        multiplicity_slot(
            "drawer_count",
            (2, 3, 4, 5, 6),
            role="number of pull-out drawers",
            item_slot="drawer_front",
        ),
    )
)

_TOP_THICKNESS = 0.024
_PANEL = 0.016


@dataclass(frozen=True)
class Config:
    body_form: BodyForm = "rect_carcass_tapered_legs"
    drawer_front: DrawerFront = "knob_front"
    mirror_form: MirrorForm = "swing_ring_mirror"
    drawer_count: int = 3
    body_width_m: float = 1.00
    body_depth_m: float = 0.44
    leg_height_m: float = 0.40
    carcass_height_m: float = 0.22
    mirror_width_m: float = 0.55
    mirror_height_m: float = 0.60
    name: str = "dressing_table"


@dataclass(frozen=True)
class ResolvedConfig:
    body_form: BodyForm
    drawer_front: DrawerFront
    mirror_form: MirrorForm
    drawer_count: int
    body_width_m: float
    body_depth_m: float
    leg_height_m: float
    carcass_height_m: float
    mirror_width_m: float
    mirror_height_m: float
    name: str
    # derived
    carcass_z0_m: float
    carcass_z1_m: float
    top_z_m: float
    drawer_travel_m: float


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0611_D7A5_1E22)
    return Config(
        body_form=choices["body_form"],
        drawer_front=choices["drawer_front"],
        mirror_form=choices["mirror_form"],
        drawer_count=int(choices["drawer_count"]),
        body_width_m=round(rng.uniform(0.84, 1.26), 5),
        body_depth_m=round(rng.uniform(0.38, 0.50), 5),
        leg_height_m=round(rng.uniform(0.30, 0.44), 5),
        carcass_height_m=round(rng.uniform(0.17, 0.29), 5),
        mirror_width_m=round(rng.uniform(0.38, 0.76), 5),
        mirror_height_m=round(rng.uniform(0.42, 0.76), 5),
        name=f"dressing_table_seed_{seed}",
    )


def _require_range(name: str, value: float, minimum: float, maximum: float) -> float:
    value = float(value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be in [{minimum}, {maximum}], got {value}")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "body_form": config.body_form,
            "drawer_front": config.drawer_front,
            "mirror_form": config.mirror_form,
            "drawer_count": int(config.drawer_count),
        }
    )
    width = _require_range("body_width_m", config.body_width_m, 0.80, 1.30)
    depth = _require_range("body_depth_m", config.body_depth_m, 0.36, 0.52)
    leg_h = _require_range("leg_height_m", config.leg_height_m, 0.28, 0.46)
    carcass_h = _require_range("carcass_height_m", config.carcass_height_m, 0.16, 0.30)
    mirror_w = _require_range("mirror_width_m", config.mirror_width_m, 0.36, 0.78)
    mirror_h = _require_range("mirror_height_m", config.mirror_height_m, 0.40, 0.78)
    count = int(config.drawer_count)

    pedestal = config.body_form == "pedestal_knee_hole"
    carcass_z0 = 0.06 if pedestal else leg_h
    carcass_z1 = leg_h + carcass_h
    return ResolvedConfig(
        body_form=config.body_form,
        drawer_front=config.drawer_front,
        mirror_form=config.mirror_form,
        drawer_count=count,
        body_width_m=width,
        body_depth_m=depth,
        leg_height_m=leg_h,
        carcass_height_m=carcass_h,
        mirror_width_m=mirror_w,
        mirror_height_m=mirror_h,
        name=config.name,
        carcass_z0_m=carcass_z0,
        carcass_z1_m=carcass_z1,
        top_z_m=carcass_z1 + _TOP_THICKNESS,
        drawer_travel_m=depth * 0.62,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, object]:
    return {
        "body_form": config.body_form,
        "drawer_front": config.drawer_front,
        "mirror_form": config.mirror_form,
        "drawer_count": int(config.drawer_count),
    }


def slot_choices_for_seed(seed: int) -> dict[str, object]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject) -> dict[str, object]:
    return {
        "case": model.material("vanity_walnut", rgba=(0.29, 0.16, 0.09, 1.0)),
        "front": model.material("vanity_front", rgba=(0.35, 0.21, 0.12, 1.0)),
        "trim": model.material("vanity_trim", rgba=(0.22, 0.12, 0.07, 1.0)),
        "brass": model.material("vanity_brass", rgba=(0.72, 0.58, 0.26, 1.0)),
        "glass": model.material("vanity_mirror_glass", rgba=(0.80, 0.85, 0.88, 1.0)),
        "lining": model.material("vanity_lining", rgba=(0.42, 0.36, 0.32, 1.0)),
    }


# ---------------------------------------------------------------------------
# shared CadQuery profiles
# ---------------------------------------------------------------------------


def _rounded_slab(width: float, depth: float, thickness: float,
                  radius: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(width, depth, thickness)
        .edges("|Z")
        .fillet(min(radius, 0.45 * min(width, depth)))
    )


def _kidney_slab(width: float, depth: float, thickness: float) -> cq.Workplane:
    """Waisted kidney plan: a rounded slab with a real concave front bite."""

    slab = _rounded_slab(width, depth, thickness, 0.06)
    bite = (
        cq.Workplane("XY")
        .circle(width * 0.42)
        .extrude(thickness, both=True)
        .translate((0.0, -0.5 * depth - width * 0.36, 0.0))
    )
    return slab.cut(bite)


def _tapered_leg(height: float, top: float, bottom: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .rect(top, top)
        .workplane(offset=height)
        .rect(bottom, bottom)
        .loft(combine=True)
    )


def _cabriole_leg(height: float) -> cq.Workplane:
    """Curved cabriole leg swept from a real S profile."""

    steps = 9
    result: cq.Workplane | None = None
    for index in range(steps):
        t = index / (steps - 1.0)
        z = height * t
        radius = 0.020 - 0.010 * math.sin(math.pi * t)
        offset = 0.030 * math.sin(math.pi * t) - 0.014 * t
        disc = (
            cq.Workplane("XY")
            .circle(max(radius, 0.007))
            .extrude(height / (steps - 1.0) + 0.004)
            .translate((offset, offset, z))
        )
        result = disc if result is None else result.union(disc)
    assert result is not None
    return result


def _d_panel(height: float, depth: float, thickness: float) -> cq.Workplane:
    """Solid end panel with a curved outer profile and a cut-out foot arch."""

    panel = (
        cq.Workplane("YZ")
        .rect(depth, height)
        .extrude(thickness * 0.5, both=True)
        .edges("|X")
        .fillet(min(0.055, 0.4 * min(depth, height)))
    )
    arch = (
        cq.Workplane("YZ")
        .circle(depth * 0.30)
        .extrude(thickness, both=True)
        .translate((0.0, 0.0, -0.5 * height + depth * 0.06))
    )
    return panel.cut(arch)


def _drawer_box_shape(width: float, height: float, depth: float) -> cq.Workplane:
    """A real hollow tray: front, back, two sides and a bottom."""

    outer = cq.Workplane("XY").box(width, depth, height)
    cavity = (
        cq.Workplane("XY")
        .box(width - 2.0 * 0.010, depth - 2.0 * 0.010, height)
        .translate((0.0, 0.0, 0.012))
    )
    return outer.cut(cavity)


def _mirror_frame_shape(width: float, height: float, *, oval: bool) -> cq.Workplane:
    """Framed glass: a real ring with a genuinely open aperture."""

    if oval:
        outer = (
            cq.Workplane("XZ")
            .ellipse(0.5 * width, 0.5 * height)
            .extrude(0.011, both=True)
        )
        inner = (
            cq.Workplane("XZ")
            .ellipse(0.5 * width - 0.030, 0.5 * height - 0.030)
            .extrude(0.020, both=True)
        )
    else:
        outer = (
            cq.Workplane("XZ")
            .rect(width, height)
            .extrude(0.011, both=True)
            .edges("|Y")
            .fillet(min(0.030, 0.2 * min(width, height)))
        )
        inner = (
            cq.Workplane("XZ")
            .rect(width - 0.060, height - 0.060)
            .extrude(0.020, both=True)
        )
    return outer.cut(inner)


def _bored_boss(outer: float, bore: float, length: float, axis: str) -> cq.Workplane:
    """Hinge boss with a real bore, so its pin runs inside instead of through solid."""

    plane = {"x": "YZ", "y": "XZ", "z": "XY"}[axis]
    body = cq.Workplane(plane).circle(outer).extrude(length * 0.5, both=True)
    hole = cq.Workplane(plane).circle(bore).extrude(length, both=True)
    return body.cut(hole)


def _cabinet_shell_shape(width: float, depth: float, height: float) -> cq.Workplane:
    """Jewellery cabinet: an open-fronted box with real walls."""

    outer = cq.Workplane("XY").box(width, depth, height)
    cavity = (
        cq.Workplane("XY")
        .box(width - 2.0 * 0.012, depth, height - 2.0 * 0.012)
        .translate((0.0, 0.014, 0.0))
    )
    return outer.cut(cavity)


# ---------------------------------------------------------------------------
# drawer zones (host adaptation per body_form)
# ---------------------------------------------------------------------------


def _drawer_slots(r: ResolvedConfig) -> list[dict]:
    """Return one geometric slot per drawer for the selected body form."""

    count = r.drawer_count
    depth = r.body_depth_m
    if r.body_form == "pedestal_knee_hole":
        ped_w = max(0.20, r.body_width_m * 0.26)
        left = max(0, count // 2)
        right = count - left
        slots: list[dict] = []
        for side, n_side in ((-1.0, left), (1.0, right)):
            if n_side <= 0:
                continue
            zone_h = (r.carcass_z1_m - 0.02) - (r.carcass_z0_m + 0.02)
            pitch = zone_h / n_side
            for k in range(n_side):
                z = r.carcass_z0_m + 0.02 + pitch * (k + 0.5)
                slots.append(
                    {
                        "x": side * (0.5 * r.body_width_m - 0.5 * ped_w),
                        "z": z,
                        "width": ped_w - 0.040,
                        "height": pitch - 0.018,
                        "depth": depth - 0.030,
                    }
                )
        return slots[:count]

    usable = r.body_width_m - 0.070
    if r.body_form == "kidney_plan_cabriole":
        usable = r.body_width_m * 0.74
    gap = 0.012
    span = (usable - gap * (count - 1)) / count
    z = 0.5 * (r.carcass_z0_m + r.carcass_z1_m)
    height = (r.carcass_z1_m - r.carcass_z0_m) - 0.036
    return [
        {
            "x": -0.5 * usable + span * (i + 0.5) + gap * i,
            "z": z,
            "width": span - 0.014,
            "height": height,
            "depth": depth - 0.030,
        }
        for i in range(count)
    ]


# ---------------------------------------------------------------------------
# body_form candidates
# ---------------------------------------------------------------------------


def _add_top(body, r: ResolvedConfig, mats, *, kidney: bool) -> None:
    shape = (
        _kidney_slab(r.body_width_m + 0.030, r.body_depth_m + 0.020, _TOP_THICKNESS)
        if kidney
        else _rounded_slab(
            r.body_width_m + 0.030, r.body_depth_m + 0.020, _TOP_THICKNESS, 0.022
        )
    )
    body.visual(
        mesh_from_cadquery(shape, f"vanity__top_{'kidney' if kidney else 'rect'}",
                           tolerance=0.0012),
        origin=Origin(xyz=(0.0, 0.0, r.carcass_z1_m + 0.5 * _TOP_THICKNESS)),
        material=mats["case"],
        name="vanity__body__worktop", material_class_id="wood.walnut_dark",
    )


def _add_drawer_cavities(shape: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    for slot in _drawer_slots(r):
        shape = shape.cut(
            cq.Workplane("XY")
            .box(slot["width"] + 0.0016, r.body_depth_m + 0.004, slot["height"] + 0.0016)
            .translate((slot["x"], 0.0, slot["z"]))
        )
    return shape


def _body_form_rect_carcass_tapered_legs_build(model, r, mats):
    body = model.part("vanity__body", meta={"role": "vanity_body", "candidate": r.body_form})
    carcass = _rounded_slab(
        r.body_width_m, r.body_depth_m, r.carcass_z1_m - r.carcass_z0_m, 0.018
    ).translate((0.0, 0.0, 0.5 * (r.carcass_z0_m + r.carcass_z1_m)))
    carcass = _add_drawer_cavities(carcass, r)
    body.visual(
        mesh_from_cadquery(carcass, "vanity__rect_carcass", tolerance=0.0012),
        material=mats["case"],
        name="vanity__body__carcass", material_class_id="wood.walnut_dark",
    )
    for index, (sx, sy) in enumerate(
        ((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))
    ):
        body.visual(
            mesh_from_cadquery(
                _tapered_leg(r.leg_height_m, 0.048, 0.030), f"vanity__leg_{index}",
                tolerance=0.0010,
            ),
            origin=Origin(
                xyz=(
                    sx * (0.5 * r.body_width_m - 0.038),
                    sy * (0.5 * r.body_depth_m - 0.038),
                    0.0,
                )
            ),
            material=mats["trim"],
            name=f"vanity__body__leg_{index}", material_class_id="wood.polished_varnished",
        )
    _add_top(body, r, mats, kidney=False)
    return body


def _body_form_kidney_plan_cabriole_build(model, r, mats):
    body = model.part("vanity__body", meta={"role": "vanity_body", "candidate": r.body_form})
    carcass = _kidney_slab(
        r.body_width_m, r.body_depth_m, r.carcass_z1_m - r.carcass_z0_m
    ).translate((0.0, 0.0, 0.5 * (r.carcass_z0_m + r.carcass_z1_m)))
    carcass = _add_drawer_cavities(carcass, r)
    body.visual(
        mesh_from_cadquery(carcass, "vanity__kidney_carcass", tolerance=0.0012),
        material=mats["case"],
        name="vanity__body__carcass", material_class_id="wood.walnut_dark",
    )
    for index, (sx, sy) in enumerate(
        ((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))
    ):
        body.visual(
            mesh_from_cadquery(
                _cabriole_leg(r.leg_height_m), f"vanity__cabriole_{index}",
                tolerance=0.0012,
            ),
            origin=Origin(
                xyz=(
                    sx * (0.5 * r.body_width_m - 0.055),
                    sy * (0.5 * r.body_depth_m - 0.050),
                    0.0,
                ),
                rpy=(0.0, 0.0, math.atan2(sy, sx) - math.pi * 0.75),
            ),
            material=mats["trim"],
            name=f"vanity__body__leg_{index}", material_class_id="wood.polished_varnished",
        )
    _add_top(body, r, mats, kidney=True)
    return body


def _body_form_d_panel_carcass_build(model, r, mats):
    body = model.part("vanity__body", meta={"role": "vanity_body", "candidate": r.body_form})
    carcass = _rounded_slab(
        r.body_width_m - 0.060, r.body_depth_m, r.carcass_z1_m - r.carcass_z0_m, 0.014
    ).translate((0.0, 0.0, 0.5 * (r.carcass_z0_m + r.carcass_z1_m)))
    carcass = _add_drawer_cavities(carcass, r)
    body.visual(
        mesh_from_cadquery(carcass, "vanity__panel_carcass", tolerance=0.0012),
        material=mats["case"],
        name="vanity__body__carcass", material_class_id="wood.walnut_dark",
    )
    for index, sx in enumerate((-1.0, 1.0)):
        body.visual(
            mesh_from_cadquery(
                _d_panel(r.carcass_z1_m, r.body_depth_m, 0.028),
                f"vanity__d_panel_{index}",
                tolerance=0.0012,
            ),
            origin=Origin(
                xyz=(sx * (0.5 * r.body_width_m - 0.014), 0.0, 0.5 * r.carcass_z1_m)
            ),
            material=mats["case"],
            name=f"vanity__body__side_panel_{index}", material_class_id="wood.walnut_dark",
        )
    _add_top(body, r, mats, kidney=False)
    return body


def _body_form_pedestal_knee_hole_build(model, r, mats):
    body = model.part("vanity__body", meta={"role": "vanity_body", "candidate": r.body_form})
    ped_w = max(0.20, r.body_width_m * 0.26)
    for index, sx in enumerate((-1.0, 1.0)):
        pedestal = _rounded_slab(
            ped_w, r.body_depth_m, r.carcass_z1_m - r.carcass_z0_m, 0.014
        ).translate(
            (
                sx * (0.5 * r.body_width_m - 0.5 * ped_w),
                0.0,
                0.5 * (r.carcass_z0_m + r.carcass_z1_m),
            )
        )
        body.visual(
            mesh_from_cadquery(
                _add_drawer_cavities(pedestal, r), f"vanity__pedestal_{index}",
                tolerance=0.0012,
            ),
            material=mats["case"],
            name=f"vanity__body__pedestal_{index}", material_class_id="wood.walnut_dark",
        )
        body.visual(
            Box((ped_w - 0.020, r.body_depth_m - 0.030, r.carcass_z0_m)),
            origin=Origin(
                xyz=(
                    sx * (0.5 * r.body_width_m - 0.5 * ped_w),
                    0.0,
                    0.5 * r.carcass_z0_m,
                )
            ),
            material=mats["trim"],
            name=f"vanity__body__plinth_{index}", material_class_id="wood.polished_varnished",
        )
    _add_top(body, r, mats, kidney=False)
    return body


_BODY_BUILDERS = {
    "rect_carcass_tapered_legs": _body_form_rect_carcass_tapered_legs_build,
    "kidney_plan_cabriole": _body_form_kidney_plan_cabriole_build,
    "d_panel_carcass": _body_form_d_panel_carcass_build,
    "pedestal_knee_hole": _body_form_pedestal_knee_hole_build,
}


# ---------------------------------------------------------------------------
# drawer_front candidates
# ---------------------------------------------------------------------------


def _drawer_front_knob_front_build(drawer, r, mats, *, prefix, slot, front_y):
    drawer.visual(
        Box((slot["width"], 0.018, slot["height"])),
        origin=Origin(xyz=(0.0, front_y, 0.0)),
        material=mats["front"],
        name=f"{prefix}__front_panel", material_class_id="wood.veneer_panel",
    )
    drawer.visual(
        Cylinder(radius=0.016, length=0.020),
        origin=Origin(xyz=(0.0, front_y - 0.019, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["brass"],
        name=f"{prefix}__knob", material_class_id="metal.brass_polished",
    )


def _drawer_front_bar_handle_front_build(drawer, r, mats, *, prefix, slot, front_y):
    drawer.visual(
        Box((slot["width"], 0.018, slot["height"])),
        origin=Origin(xyz=(0.0, front_y, 0.0)),
        material=mats["front"],
        name=f"{prefix}__front_panel", material_class_id="wood.veneer_panel",
    )
    bar_span = slot["width"] * 0.68
    for index, sx in enumerate((-1.0, 1.0)):
        drawer.visual(
            Cylinder(radius=0.006, length=0.024),
            origin=Origin(
                xyz=(sx * 0.5 * bar_span, front_y - 0.021, 0.0),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["brass"],
            name=f"{prefix}__bar_post_{index}", material_class_id="metal.brass_polished",
        )
    drawer.visual(
        Cylinder(radius=0.006, length=bar_span),
        origin=Origin(
            xyz=(0.0, front_y - 0.031, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)
        ),
        material=mats["brass"],
        name=f"{prefix}__bar", material_class_id="metal.brass_polished",
    )


_FRONT_BUILDERS = {
    "knob_front": _drawer_front_knob_front_build,
    "bar_handle_front": _drawer_front_bar_handle_front_build,
}


def _build_drawers(model, r, mats, body):
    drawers = []
    for index, slot in enumerate(_drawer_slots(r)):
        prefix = f"drawer_front__{r.drawer_front}__drawer_{index}"
        drawer = model.part(prefix, meta={"role": "drawer", "candidate": r.drawer_front})
        box_depth = slot["depth"]
        drawer.visual(
            mesh_from_cadquery(
                _drawer_box_shape(slot["width"], slot["height"], box_depth),
                f"{prefix}__tray",
                tolerance=0.0010,
            ),
            origin=Origin(),
            material=mats["lining"],
            name=f"{prefix}__tray", material_class_id="fabric.felt",
        )
        front_y = -0.5 * box_depth - 0.006
        _FRONT_BUILDERS[r.drawer_front](
            drawer, r, mats, prefix=prefix, slot=slot, front_y=front_y
        )
        model.articulation(
            f"{prefix}__slide",
            ArticulationType.PRISMATIC,
            parent=body,
            child=drawer,
            origin=Origin(xyz=(slot["x"], 0.0, slot["z"])),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(
                effort=180.0, velocity=0.2, lower=0.0, upper=r.drawer_travel_m
            ),
            meta={"mechanism": "drawer pull-out"},
        )
        drawers.append(drawer)
    return drawers


# ---------------------------------------------------------------------------
# mirror_form candidates
# ---------------------------------------------------------------------------


def _mirror_panel(part, r, mats, *, prefix: str, width: float, height: float,
                  oval: bool, origin: Origin) -> None:
    part.visual(
        mesh_from_cadquery(
            _mirror_frame_shape(width, height, oval=oval),
            f"{prefix}__frame_mesh",
            tolerance=0.0012,
        ),
        origin=origin,
        material=mats["trim"],
        name=f"{prefix}__frame", material_class_id="wood.polished_varnished",
    )
    glass_geom = (
        Cylinder(radius=0.5 * min(width, height) - 0.026, length=0.006)
        if oval
        else Box((width - 0.052, 0.006, height - 0.052))
    )
    glass_origin = Origin(
        xyz=origin.xyz,
        rpy=(math.pi / 2.0, 0.0, 0.0) if oval else origin.rpy,
    )
    part.visual(
        glass_geom,
        origin=glass_origin,
        material=mats["glass"],
        name=f"{prefix}__glass", material_class_id="glass.mirror",
    )


def _mirror_form_swing_ring_mirror_build(model, r, mats, body):
    candidate = "swing_ring_mirror"
    prefix = f"mirror_form__{candidate}"
    width = min(r.mirror_width_m, r.body_width_m - 0.10)
    height = r.mirror_height_m
    hinge_y = 0.5 * r.body_depth_m - 0.050
    hinge_z = r.top_z_m + 0.032
    body.visual(
        Box((width * 0.72, 0.030, 0.020)),
        origin=Origin(xyz=(0.0, hinge_y, r.top_z_m + 0.010)),
        material=mats["trim"],
        name="vanity__body__mirror_cleat", material_class_id="wood.polished_varnished",
    )
    for index, sx in enumerate((-1.0, 1.0)):
        body.visual(
            mesh_from_cadquery(
                _bored_boss(0.0125, 0.0106, 0.014, "x"), f"vanity__mirror_boss_{index}",
                tolerance=0.0006,
            ),
            origin=Origin(xyz=(sx * (0.5 * width * 0.72 + 0.007), hinge_y, hinge_z)),
            material=mats["brass"],
            name=f"vanity__body__mirror_boss_{index}", material_class_id="metal.brass_polished",
        )
    mirror = model.part(f"{prefix}__mirror", meta={"role": "mirror", "candidate": candidate})
    mirror.visual(
        Cylinder(radius=0.0096, length=width * 0.72 + 0.026),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["brass"],
        name=f"{prefix}__hinge_pin", material_class_id="metal.brass_polished",
    )
    mirror.visual(
        Box((width * 0.50, 0.014, 0.022)),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        material=mats["trim"],
        name=f"{prefix}__hinge_stile", material_class_id="wood.polished_varnished",
    )
    _mirror_panel(
        mirror, r, mats, prefix=prefix, width=width, height=height, oval=False,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * height + 0.018)),
    )
    provider = AxisInterface(
        name=f"{prefix}.hinge_seat",
        point=(0.0, hinge_y, hinge_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0106,
    )
    consumer = AxisInterface(
        name=f"{prefix}.hinge_pin",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0096,
    )
    mate = mate_axes(provider, consumer)
    joint = f"{prefix}__mirror_tilt"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=body,
        child=mirror,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=40.0, velocity=1.0, lower=-0.30, upper=0.30),
        meta={"mechanism": "swing mirror tilt"},
    )
    register_interface_mate(model, joint, mate)
    return mirror


def _mirror_form_trunnion_oval_mirror_build(model, r, mats, body):
    candidate = "trunnion_oval_mirror"
    prefix = f"mirror_form__{candidate}"
    width = min(r.mirror_width_m, r.body_width_m - 0.16)
    height = r.mirror_height_m
    post_h = height * 0.86
    post_x = 0.5 * width + 0.038
    hinge_z = r.top_z_m + post_h * 0.72
    hinge_y = 0.5 * r.body_depth_m - 0.060
    for index, sx in enumerate((-1.0, 1.0)):
        body.visual(
            Cylinder(radius=0.018, length=0.026),
            origin=Origin(xyz=(sx * post_x, hinge_y, r.top_z_m + 0.013)),
            material=mats["trim"],
            name=f"vanity__body__post_foot_{index}", material_class_id="wood.polished_varnished",
        )
        body.visual(
            Cylinder(radius=0.013, length=post_h),
            origin=Origin(xyz=(sx * post_x, hinge_y, r.top_z_m + 0.5 * post_h)),
            material=mats["trim"],
            name=f"vanity__body__turned_post_{index}", material_class_id="wood.polished_varnished",
        )
        body.visual(
            mesh_from_cadquery(
                _bored_boss(0.0134, 0.0114, 0.012, "x"), f"vanity__trunnion_boss_{index}",
                tolerance=0.0006,
            ),
            origin=Origin(xyz=(sx * (post_x - 0.019), hinge_y, hinge_z)),
            material=mats["brass"],
            name=f"vanity__body__trunnion_boss_{index}", material_class_id="metal.brass_polished",
        )
    mirror = model.part(f"{prefix}__mirror", meta={"role": "mirror", "candidate": candidate})
    mirror.visual(
        Cylinder(radius=0.0104, length=2.0 * post_x - 0.030),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["brass"],
        name=f"{prefix}__trunnion_pin", material_class_id="metal.brass_polished",
    )
    _mirror_panel(
        mirror, r, mats, prefix=prefix, width=width, height=height, oval=True,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    provider = AxisInterface(
        name=f"{prefix}.trunnion_seat",
        point=(0.0, hinge_y, hinge_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0114,
    )
    consumer = AxisInterface(
        name=f"{prefix}.trunnion_pin",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0104,
    )
    mate = mate_axes(provider, consumer)
    joint = f"{prefix}__mirror_tilt"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=body,
        child=mirror,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=40.0, velocity=1.0, lower=-0.34, upper=0.34),
        meta={"mechanism": "oval mirror trunnion tilt"},
    )
    register_interface_mate(model, joint, mate)
    return mirror


def _mirror_form_lift_top_mirror_build(model, r, mats, body):
    candidate = "lift_top_mirror"
    prefix = f"mirror_form__{candidate}"
    lid_w = min(r.mirror_width_m, r.body_width_m - 0.12)
    lid_d = min(r.body_depth_m - 0.10, r.mirror_height_m * 0.70)
    hinge_y = 0.5 * r.body_depth_m - 0.060
    hinge_z = r.top_z_m + 0.046
    for index, sx in enumerate((-1.0, 1.0)):
        body.visual(
            mesh_from_cadquery(
                _bored_boss(0.0125, 0.0106, 0.014, "x"), f"vanity__lid_boss_{index}",
                tolerance=0.0006,
            ),
            origin=Origin(xyz=(sx * (0.5 * lid_w - 0.014), hinge_y, hinge_z)),
            material=mats["brass"],
            name=f"vanity__body__lid_boss_{index}", material_class_id="metal.brass_polished",
        )
    body.visual(
        Box((lid_w, 0.030, 0.042)),
        origin=Origin(xyz=(0.0, hinge_y, r.top_z_m + 0.019)),
        material=mats["trim"],
        name="vanity__body__lid_cleat", material_class_id="wood.polished_varnished",
    )

    lid = model.part(f"{prefix}__lid", meta={"role": "mirror_lid", "candidate": candidate})
    lid.visual(
        Cylinder(radius=0.0096, length=lid_w - 0.010),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["brass"],
        name=f"{prefix}__lid_hinge_pin", material_class_id="metal.brass_polished",
    )
    lid.visual(
        Box((lid_w - 0.070, lid_d, 0.016)),
        origin=Origin(xyz=(0.0, -0.5 * lid_d - 0.004, 0.0)),
        material=mats["case"],
        name=f"{prefix}__lid_panel", material_class_id="wood.walnut_dark",
    )
    for index, sx in enumerate((-1.0, 1.0)):
        lid.visual(
            mesh_from_cadquery(
                _bored_boss(0.0116, 0.0088, 0.012, "x"), f"{prefix}__mirror_boss_{index}",
                tolerance=0.0006,
            ),
            origin=Origin(xyz=(sx * (0.5 * lid_w - 0.048), -0.026, 0.019)),
            material=mats["brass"],
            name=f"{prefix}__lid_mirror_boss_{index}", material_class_id="metal.brass_polished",
        )
    lid_provider = AxisInterface(
        name=f"{prefix}.lid_seat",
        point=(0.0, hinge_y, hinge_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0106,
    )
    lid_consumer = AxisInterface(
        name=f"{prefix}.lid_pin",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0096,
    )
    lid_mate = mate_axes(lid_provider, lid_consumer)
    lid_joint = f"{prefix}__lid_lift"
    model.articulation(
        lid_joint,
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=lid_mate.origin,
        axis=lid_mate.axis,
        motion_limits=MotionLimits(effort=40.0, velocity=1.0, lower=-1.10, upper=0.0),
        meta={"mechanism": "lift-top lid"},
    )
    register_interface_mate(model, lid_joint, lid_mate)

    mirror = model.part(f"{prefix}__mirror", meta={"role": "mirror", "candidate": candidate})
    mirror.visual(
        Cylinder(radius=0.0080, length=lid_w - 0.084),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["brass"],
        name=f"{prefix}__mirror_hinge_pin", material_class_id="metal.brass_polished",
    )
    mirror.visual(
        Box((lid_w * 0.40, 0.012, 0.028)),
        origin=Origin(xyz=(0.0, 0.0, 0.011)),
        material=mats["trim"],
        name=f"{prefix}__hinge_stile", material_class_id="wood.polished_varnished",
    )
    _mirror_panel(
        mirror, r, mats, prefix=prefix,
        width=lid_w - 0.110, height=min(lid_d * 1.4, r.mirror_height_m), oval=False,
        origin=Origin(
            xyz=(0.0, 0.0, 0.5 * min(lid_d * 1.4, r.mirror_height_m) + 0.020)
        ),
    )
    m_provider = AxisInterface(
        name=f"{prefix}.mirror_seat",
        point=(0.0, -0.026, 0.019),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0088,
    )
    m_consumer = AxisInterface(
        name=f"{prefix}.mirror_pin",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0080,
    )
    m_mate = mate_axes(m_provider, m_consumer)
    m_joint = f"{prefix}__mirror_tilt"
    model.articulation(
        m_joint,
        ArticulationType.REVOLUTE,
        parent=lid,
        child=mirror,
        origin=m_mate.origin,
        axis=m_mate.axis,
        motion_limits=MotionLimits(effort=30.0, velocity=1.0, lower=-0.26, upper=0.26),
        meta={"mechanism": "mirror hinged inside the lid"},
    )
    register_interface_mate(model, m_joint, m_mate)
    return mirror


def _mirror_form_sliding_mirror_storage_build(model, r, mats, body):
    candidate = "sliding_mirror_storage"
    prefix = f"mirror_form__{candidate}"
    width = min(r.mirror_width_m, r.body_width_m * 0.46)
    height = r.mirror_height_m
    rail_y = 0.5 * r.body_depth_m - 0.055
    rail_len = r.body_width_m - 0.08
    stroke = max(0.05, 0.5 * (rail_len - width) - 0.02)
    body.visual(
        Box((rail_len, 0.026, 0.020)),
        origin=Origin(xyz=(0.0, rail_y, r.top_z_m + 0.010)),
        material=mats["trim"],
        name="vanity__body__slide_rail", material_class_id="wood.polished_varnished",
    )
    body.visual(
        Box((rail_len, 0.014, 0.012)),
        origin=Origin(xyz=(0.0, rail_y - 0.020, r.top_z_m + 0.014)),
        material=mats["brass"],
        name="vanity__body__slide_lip", material_class_id="metal.brass_polished",
    )
    mirror = model.part(f"{prefix}__mirror", meta={"role": "mirror", "candidate": candidate})
    mirror.visual(
        Box((width, 0.014, 0.016)),
        origin=Origin(xyz=(0.0, -0.0075, 0.0)),
        material=mats["trim"],
        name=f"{prefix}__shoe", material_class_id="wood.polished_varnished",
    )
    _mirror_panel(
        mirror, r, mats, prefix=prefix, width=width, height=height, oval=False,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * height + 0.006)),
    )
    model.articulation(
        f"{prefix}__mirror_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=mirror,
        origin=Origin(xyz=(0.0, rail_y - 0.007, r.top_z_m + 0.028)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.2, lower=-stroke, upper=stroke),
        meta={"mechanism": "sliding mirror over storage"},
    )
    return mirror


def _mirror_form_jewellery_door_mirror_build(model, r, mats, body):
    candidate = "jewellery_door_mirror"
    prefix = f"mirror_form__{candidate}"
    width = min(r.mirror_width_m, r.body_width_m * 0.50)
    height = r.mirror_height_m
    cab_d = min(0.11, r.body_depth_m * 0.32)
    cab_y = 0.5 * r.body_depth_m - 0.5 * cab_d - 0.030
    body.visual(
        mesh_from_cadquery(
            _cabinet_shell_shape(width, cab_d, height),
            "vanity__jewellery_cabinet",
            tolerance=0.0012,
        ),
        origin=Origin(xyz=(0.0, cab_y, r.top_z_m + 0.5 * height)),
        material=mats["case"],
        name="vanity__body__jewellery_cabinet", material_class_id="wood.walnut_dark",
    )
    hinge_x = -0.5 * width - 0.010
    for index, sz in enumerate((-1.0, 1.0)):
        body.visual(
            mesh_from_cadquery(
                _bored_boss(0.0125, 0.0106, 0.014, "z"), f"vanity__door_boss_{index}",
                tolerance=0.0006,
            ),
            origin=Origin(
                xyz=(
                    hinge_x,
                    cab_y - 0.5 * cab_d - 0.006,
                    r.top_z_m + 0.5 * height + sz * (0.5 * height - 0.006),
                )
            ),
            material=mats["brass"],
            name=f"vanity__body__door_boss_{index}", material_class_id="metal.brass_polished",
        )
    door = model.part(f"{prefix}__mirror", meta={"role": "mirror", "candidate": candidate})
    door.visual(
        Cylinder(radius=0.0096, length=height - 0.010),
        origin=Origin(),
        material=mats["brass"],
        name=f"{prefix}__door_hinge_pin", material_class_id="metal.brass_polished",
    )
    door.visual(
        Box((0.028, 0.014, height - 0.044)),
        origin=Origin(xyz=(0.016, 0.0, 0.0)),
        material=mats["trim"],
        name=f"{prefix}__hinge_stile", material_class_id="wood.polished_varnished",
    )
    _mirror_panel(
        door, r, mats, prefix=prefix, width=width, height=height - 0.010, oval=False,
        origin=Origin(xyz=(0.5 * width + 0.026, 0.0, 0.0)),
    )
    provider = AxisInterface(
        name=f"{prefix}.door_seat",
        point=(hinge_x, cab_y - 0.5 * cab_d - 0.006, r.top_z_m + 0.5 * height),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0106,
    )
    consumer = AxisInterface(
        name=f"{prefix}.door_pin",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0096,
    )
    mate = mate_axes(provider, consumer)
    joint = f"{prefix}__door_swing"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=40.0, velocity=1.2, lower=-1.30, upper=0.0),
        meta={"mechanism": "mirrored jewellery cabinet door"},
    )
    register_interface_mate(model, joint, mate)
    return door


_MIRROR_BUILDERS = {
    "swing_ring_mirror": _mirror_form_swing_ring_mirror_build,
    "trunnion_oval_mirror": _mirror_form_trunnion_oval_mirror_build,
    "lift_top_mirror": _mirror_form_lift_top_mirror_build,
    "sliding_mirror_storage": _mirror_form_sliding_mirror_storage_build,
    "jewellery_door_mirror": _mirror_form_jewellery_door_mirror_build,
}


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def build_picturex_0611_dressing_table(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model)
    body = _BODY_BUILDERS[r.body_form](model, r, mats)
    _build_drawers(model, r, mats, body)
    _MIRROR_BUILDERS[r.mirror_form](model, r, mats, body)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/Dressing_table"
    return model


def build_seeded_picturex_0611_dressing_table(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_picturex_0611_dressing_table(config_from_seed(seed), assets=assets)


def _centre(box):
    if box is None:
        return None
    return tuple(0.5 * (box[0][i] + box[1][i]) for i in range(3))


def run_picturex_0611_dressing_table_tests(
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
        "dressing table keeps one carcass, N drawers and one mirror",
        len(roles.get("vanity_body", [])) == 1
        and len(roles.get("drawer", [])) == r.drawer_count
        and len(roles.get("mirror", [])) == 1,
        details=(
            f"body={len(roles.get('vanity_body', []))}, "
            f"drawers={len(roles.get('drawer', []))}/{r.drawer_count}, "
            f"mirrors={len(roles.get('mirror', []))}"
        ),
    )
    ctx.check(
        "domain choices are recorded",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )

    body = object_model.get_part("vanity__body")
    drawers = roles.get("drawer", [])
    ctx.check(
        "every drawer belongs to the selected front family",
        all(part.meta.get("candidate") == r.drawer_front for part in drawers),
    )

    for index, drawer in enumerate(drawers):
        joint = object_model.get_articulation(f"{drawer.name}__slide")
        closed = _centre(
            ctx.part_element_world_aabb(drawer, elem=f"{drawer.name}__front_panel")
        )
        with ctx.pose({joint: joint.motion_limits.upper}):
            opened = _centre(
                ctx.part_element_world_aabb(drawer, elem=f"{drawer.name}__front_panel")
            )
        ctx.check(
            f"drawer {index} pulls forward out of the carcass",
            closed is not None
            and opened is not None
            and opened[1] < closed[1] - 0.5 * r.drawer_travel_m
            and abs(opened[2] - closed[2]) < 0.002,
            details=f"closed={closed}, opened={opened}",
        )

    fronts = [
        ctx.part_element_world_aabb(drawer, elem=f"{drawer.name}__front_panel")
        for drawer in drawers
    ]
    ctx.check(
        "drawer fronts stay inside the carcass footprint",
        all(box is not None for box in fronts)
        and all(
            abs(_centre(box)[0]) < 0.5 * r.body_width_m + 0.001 for box in fronts if box
        ),
        details=f"width={r.body_width_m}",
    )

    mirror = roles.get("mirror", [None])[0]
    mirror_box = ctx.part_world_aabb(mirror) if mirror is not None else None
    ctx.check(
        "mirror assembly stands above the worktop",
        mirror_box is not None and mirror_box[1][2] > r.top_z_m + 0.10,
        details=f"mirror_box={mirror_box}, top_z={r.top_z_m}",
    )
    ctx.check(
        "worktop sits at a seated dressing-table height",
        0.44 < r.top_z_m < 0.80,
        details=f"top_z={r.top_z_m}",
    )

    mirror_name = mirror.name if mirror is not None else ""
    mirror_joint = next(
        (
            joint
            for joint in object_model.articulations
            if getattr(joint.child, "name", joint.child) == mirror_name
        ),
        None,
    )
    if True:
        limits = mirror_joint.motion_limits if mirror_joint is not None else None
        target = (
            0.0
            if limits is None
            else (limits.upper if abs(limits.upper) >= abs(limits.lower) else limits.lower)
        )
        rest_box = ctx.part_world_aabb(mirror)
        moved_box = None
        if mirror_joint is not None:
            with ctx.pose({mirror_joint: target}):
                moved_box = ctx.part_world_aabb(mirror)
        rest_span = None if rest_box is None else rest_box[1][1] - rest_box[0][1]
        moved_span = None if moved_box is None else moved_box[1][1] - moved_box[0][1]
        rest_c = _centre(rest_box)
        moved_c = _centre(moved_box)
        ctx.check(
            "the mirror assembly really moves on its source joint",
            rest_span is not None
            and moved_span is not None
            and rest_c is not None
            and moved_c is not None
            and (
                abs(moved_span - rest_span) > 0.008
                or max(abs(moved_c[i] - rest_c[i]) for i in range(3)) > 0.008
            ),
            details=f"rest_span={rest_span}, moved_span={moved_span}",
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
        "smallest_body_most_drawers",
        {
            "body_width_m": 0.80,
            "body_depth_m": 0.36,
            "leg_height_m": 0.46,
            "carcass_height_m": 0.16,
            "drawer_count": 6,
            "mirror_width_m": 0.36,
            "mirror_height_m": 0.40,
        },
        reason="narrowest shallowest carcass carrying the largest drawer count",
    ),
    corner_case(
        "largest_body_fewest_drawers",
        {
            "body_width_m": 1.30,
            "body_depth_m": 0.52,
            "leg_height_m": 0.28,
            "carcass_height_m": 0.30,
            "drawer_count": 2,
            "mirror_width_m": 0.78,
            "mirror_height_m": 0.78,
        },
        reason="widest deepest carcass with the fewest, largest drawers and the biggest mirror",
    ),
    corner_case(
        "largest_mirror_on_smallest_body",
        {
            "body_width_m": 0.80,
            "body_depth_m": 0.36,
            "leg_height_m": 0.46,
            "carcass_height_m": 0.16,
            "drawer_count": 2,
            "mirror_width_m": 0.78,
            "mirror_height_m": 0.78,
        },
        reason="the largest mirror assembly on the smallest worktop",
    ),
    corner_case(
        "tall_shallow_carcass_with_six_drawers",
        {
            "body_width_m": 1.30,
            "body_depth_m": 0.36,
            "leg_height_m": 0.28,
            "carcass_height_m": 0.30,
            "drawer_count": 6,
            "mirror_width_m": 0.36,
            "mirror_height_m": 0.78,
        },
        reason="deepest drawer bank at the shallowest box depth",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_picturex_0611_dressing_table",
    "build_seeded_picturex_0611_dressing_table",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_dressing_table_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
