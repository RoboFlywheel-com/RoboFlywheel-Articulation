# SPDX-License-Identifier: Apache-2.0

"""Self-contained benchtop laboratory centrifuge template.

The grounded ``housing`` part is a CadQuery body with a real recessed rotor
well, a drive boss on the well floor bored for the rotor shaft, a moulded well
rim and a front control panel.  The ``rotor`` turns CONTINUOUS about +z on that
boss and carries ``tube_holder_count`` holders on one derived circle; the well
radius is the rotor radius plus a running gap, so the swept envelope never
touches the wall.  The ``lid`` closes over the rim and either swings REVOLUTE on
a rear hinge line or slides PRISMATIC back on side rails.

Three slots vary without touching that chain: ``housing_form`` (lofted benchtop
shell, squared clinical cabinet, compact microfuge), ``rotor_form`` (drilled
fixed-angle wells or hung swing-bucket carriers) and ``lid_action``.
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

HousingForm = Literal["benchtop_shell", "clinical_box", "microfuge", "plinth_shell"]
RotorForm = Literal["fixed_angle", "swing_bucket"]
LidAction = Literal["hinged_lid", "sliding_lid", "lift_lid"]
PanelControl = Literal["latch_lever", "push_button"]
PaletteStyle = Literal["lab_white", "cool_grey", "teal_panel", "graphite"]

HOUSING_FORMS: tuple[HousingForm, ...] = (
    "benchtop_shell",
    "clinical_box",
    "microfuge",
    "plinth_shell",
)
ROTOR_FORMS: tuple[RotorForm, ...] = ("fixed_angle", "swing_bucket")
LID_ACTIONS: tuple[LidAction, ...] = ("hinged_lid", "sliding_lid", "lift_lid")
PANEL_CONTROLS: tuple[PanelControl, ...] = ("latch_lever", "push_button")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("lab_white", "cool_grey", "teal_panel", "graphite")


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("housing_form", HOUSING_FORMS),
        component_slot("rotor_form", ROTOR_FORMS),
        component_slot("lid_action", LID_ACTIONS),
        component_slot("panel_control", PANEL_CONTROLS),
        multiplicity_slot("tube_holder_count", (8, 12, 24), item_slot="rotor_form"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "lab_white": {
        "shell": (0.92, 0.92, 0.90, 1.0),
        "trim": (0.70, 0.71, 0.72, 1.0),
        "panel": (0.20, 0.22, 0.26, 1.0),
        "metal": (0.74, 0.76, 0.78, 1.0),
        "dark": (0.13, 0.13, 0.14, 1.0),
        "accent": (0.20, 0.52, 0.72, 1.0),
        "tube": (0.78, 0.88, 0.90, 0.42),
        "tube_cap": (0.90, 0.92, 0.90, 1.0),
    },
    "cool_grey": {
        "shell": (0.72, 0.74, 0.76, 1.0),
        "trim": (0.54, 0.56, 0.58, 1.0),
        "panel": (0.16, 0.18, 0.20, 1.0),
        "metal": (0.80, 0.82, 0.84, 1.0),
        "dark": (0.11, 0.12, 0.13, 1.0),
        "accent": (0.86, 0.62, 0.16, 1.0),
        "tube": (0.72, 0.80, 0.84, 0.42),
        "tube_cap": (0.86, 0.88, 0.88, 1.0),
    },
    "teal_panel": {
        "shell": (0.88, 0.89, 0.88, 1.0),
        "trim": (0.24, 0.52, 0.52, 1.0),
        "panel": (0.14, 0.30, 0.32, 1.0),
        "metal": (0.76, 0.78, 0.80, 1.0),
        "dark": (0.10, 0.14, 0.14, 1.0),
        "accent": (0.92, 0.90, 0.86, 1.0),
        "tube": (0.68, 0.88, 0.88, 0.42),
        "tube_cap": (0.90, 0.92, 0.88, 1.0),
    },
    "graphite": {
        "shell": (0.26, 0.27, 0.28, 1.0),
        "trim": (0.18, 0.19, 0.20, 1.0),
        "panel": (0.10, 0.11, 0.12, 1.0),
        "metal": (0.78, 0.80, 0.82, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.84, 0.28, 0.20, 1.0),
        "tube": (0.52, 0.66, 0.70, 0.42),
        "tube_cap": (0.82, 0.84, 0.84, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
WELL_GAP = 0.010          # clear gap between the rotor rim and the well wall
RIM_T = 0.008             # moulded well rim
SHAFT_R = 0.009
HUB_R = 0.024
HOLDER_R = 0.008
LID_T = 0.012
# Radial running fit, under the 1 mm assembly-gap tolerance.
FIT = 0.0008
SEAT = 0.0006
BOSS_H = 0.014
PANEL_H = 0.046


@dataclass(frozen=True)
class Config:
    housing_form: HousingForm = "benchtop_shell"
    rotor_form: RotorForm = "fixed_angle"
    lid_action: LidAction = "hinged_lid"
    panel_control: PanelControl = "latch_lever"
    tube_holder_count: int = 12
    rotor_radius_m: float | None = None
    body_height_m: float | None = None
    holder_depth_m: float | None = None
    palette_style: PaletteStyle = "lab_white"
    name: str = "pictureX_0611_centrifuge_machine1"


@dataclass(frozen=True)
class ResolvedConfig:
    housing_form: HousingForm
    rotor_form: RotorForm
    lid_action: LidAction
    panel_control: PanelControl
    tube_holder_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    rotor_radius_m: float
    body_height_m: float
    holder_depth_m: float
    well_radius_m: float
    holder_circle_m: float
    body_half_x: float
    body_half_y: float
    well_floor_z: float
    body_top_z: float
    rotor_height_m: float
    lid_clear_z_m: float
    lid_travel_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x5C_31_7E_08)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        housing_form=choices["housing_form"],
        rotor_form=choices["rotor_form"],
        lid_action=choices["lid_action"],
        panel_control=choices["panel_control"],
        tube_holder_count=choices["tube_holder_count"],
        rotor_radius_m=round(rng.uniform(0.060, 0.130), 4),
        body_height_m=round(rng.uniform(0.130, 0.290), 4),
        holder_depth_m=round(rng.uniform(0.030, 0.070), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"centrifuge_machine1_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "housing_form": config.housing_form,
            "rotor_form": config.rotor_form,
            "lid_action": config.lid_action,
            "panel_control": config.panel_control,
            "tube_holder_count": config.tube_holder_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.rotor_radius_m is not None and not 0.060 <= float(config.rotor_radius_m) <= 0.130:
        raise ValueError("rotor_radius_m must be in [0.060, 0.130]")
    if config.body_height_m is not None and not 0.130 <= float(config.body_height_m) <= 0.290:
        raise ValueError("body_height_m must be in [0.130, 0.290]")
    if config.holder_depth_m is not None and not 0.030 <= float(config.holder_depth_m) <= 0.070:
        raise ValueError("holder_depth_m must be in [0.030, 0.070]")

    radius = (
        _clamp(config.rotor_radius_m, 0.060, 0.130)
        if config.rotor_radius_m is not None
        else 0.090
    )
    height = (
        _clamp(config.body_height_m, 0.130, 0.290) if config.body_height_m is not None else 0.190
    )
    depth = (
        _clamp(config.holder_depth_m, 0.030, 0.070)
        if config.holder_depth_m is not None
        else 0.048
    )
    well_r = radius + WELL_GAP
    body_half_x = well_r + RIM_T + 0.030
    body_half_y = well_r + RIM_T + 0.046
    rotor_h = depth + 0.014
    # The well is deep enough to swallow the rotor and its holders.
    well_depth = BOSS_H + rotor_h + 0.014
    # The body is lifted when a deep well would otherwise leave no base under it.
    body_top = max(height, well_depth + 0.045)
    well_floor = body_top - well_depth
    return ResolvedConfig(
        housing_form=config.housing_form,
        rotor_form=config.rotor_form,
        lid_action=config.lid_action,
        panel_control=config.panel_control,
        tube_holder_count=int(config.tube_holder_count),
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        rotor_radius_m=radius,
        body_height_m=body_top,
        holder_depth_m=depth,
        well_radius_m=well_r,
        holder_circle_m=radius - HOLDER_R - 0.006,
        body_half_x=body_half_x,
        body_half_y=body_half_y,
        well_floor_z=well_floor,
        body_top_z=body_top,
        rotor_height_m=rotor_h,
        lid_clear_z_m=well_floor + BOSS_H + rotor_h + 0.012,
        lid_travel_m=2.0 * well_r + 0.030,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("housing_form", config.housing_form),
        ("rotor_form", config.rotor_form),
        ("lid_action", config.lid_action),
        ("panel_control", config.panel_control),
        ("tube_holder_count", config.tube_holder_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"cfg_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _z_cyl(z0: float, z1: float, radius: float, x: float = 0.0, y: float = 0.0):
    return (
        cq.Workplane("XY")
        .transformed(offset=(x, y, 0.5 * (z0 + z1)))
        .cylinder(height=z1 - z0, radius=radius, direct=(0.0, 0.0, 1.0))
    )


def _box_at(x0, x1, y0, y1, z0, z1):
    return (
        cq.Workplane("XY")
        .transformed(offset=(0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1)))
        .box(x1 - x0, y1 - y0, z1 - z0)
    )


def _test_tube_shell(length: float):
    """A thin-wall centrifuge tube with a tapered, rounded-looking bottom.

    The source asset reads as capped conical tubes rather than empty cylindrical
    holes.  Keep the mouth open under the cap so the rim and the narrowing bore
    remain legible from the open-lid view.
    """
    tip_h = min(0.007, 0.18 * length)
    neck_h = min(0.005, 0.12 * length)
    outer_r = 0.0068
    inner_r = 0.0050
    outer = (
        cq.Workplane("XY")
        .workplane(offset=0.0)
        .circle(0.0018)
        .workplane(offset=tip_h)
        .circle(outer_r)
        .loft(ruled=True)
    )
    outer = outer.union(
        cq.Workplane("XY")
        .workplane(offset=tip_h)
        .circle(outer_r)
        .extrude(max(0.001, length - tip_h - neck_h))
    )
    outer = outer.union(
        cq.Workplane("XY")
        .workplane(offset=length - neck_h)
        .circle(outer_r)
        .workplane(offset=neck_h)
        .circle(outer_r * 1.04)
        .loft(ruled=True)
    )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=tip_h + 0.0012)
        .circle(inner_r)
        .extrude(max(0.001, length - tip_h - 0.0012))
    )
    shell = outer.cut(bore)
    mouth = (
        cq.Workplane("XY")
        .workplane(offset=length - 0.0015)
        .circle(outer_r * 1.04)
        .circle(inner_r)
        .extrude(0.0015)
    )
    return shell.union(mouth)


def _local_origin(
    origin: Origin | None, offset: tuple[float, float, float]
) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(a - b for a, b in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


def _add_test_tube(
    part,
    offset: tuple[float, float, float],
    *,
    x: float,
    y: float,
    base_z: float,
    length: float,
    tilt: float,
    yaw: float,
    mats: dict[str, str],
    name: str,
) -> None:
    """Place one source-like tapered tube along a radial, slightly tilted axis."""
    part.visual(
        mesh_from_cadquery(_test_tube_shell(length), f"cfg_{name}_tube"),
        origin=_local_origin(
            Origin(xyz=(x, y, base_z), rpy=(0.0, tilt, yaw)), offset
        ),
        material=mats["tube"],
        name=f"{name}__tube_body", material_class_id="plastic.clear_rigid",
    )
    axis = (
        math.sin(tilt) * math.cos(yaw),
        math.sin(tilt) * math.sin(yaw),
        math.cos(tilt),
    )
    cap_center = tuple(
        (x, y, base_z)[i] + axis[i] * (length + 0.0015) for i in range(3)
    )
    part.visual(
        Cylinder(radius=0.0077, length=0.0035),
        origin=_local_origin(
            Origin(xyz=cap_center, rpy=(0.0, tilt, yaw)), offset
        ),
        material=mats["tube_cap"],
        name=f"{name}__tube_cap", material_class_id="plastic.opaque_glossy_molded",
    )
# --- housing candidates ---------------------------------------------------------
def _housing_benchtop_shell_build(r: ResolvedConfig):
    """A lofted benchtop shell: a rounded body swelling toward the well."""
    body = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, 0.5 * r.body_top_z))
        .box(2.0 * r.body_half_x, 2.0 * r.body_half_y, r.body_top_z)
        .edges("|Z")
        .fillet(min(0.040, r.body_half_x * 0.45))
    )
    # Moulded waist: the shell is drawn in at the base rather than a plain box.
    body = body.cut(
        _z_cyl(-0.01, 0.030, r.body_half_x * 2.4, 0.0, -(r.body_half_y + r.body_half_x * 2.25))
    )
    return body, "housing_form__benchtop_shell__shell_body"


def _housing_clinical_box_build(r: ResolvedConfig):
    """A squared clinical cabinet with a stepped front shelf."""
    body = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, 0.5 * r.body_top_z))
        .box(2.0 * r.body_half_x, 2.0 * r.body_half_y, r.body_top_z)
        .edges("|Z")
        .fillet(0.010)
    )
    body = body.cut(
        _box_at(
            -r.body_half_x - 0.01,
            r.body_half_x + 0.01,
            -r.body_half_y - 0.01,
            -r.body_half_y + 0.030,
            r.body_top_z - 0.060,
            r.body_top_z + 0.01,
        )
    )
    return body, "housing_form__clinical_box__cabinet_body"


def _housing_microfuge_build(r: ResolvedConfig):
    """A compact microfuge: a small round body under a narrow well."""
    body = _z_cyl(0.0, r.body_top_z, r.body_half_x)
    body = body.union(
        _z_cyl(0.0, 0.020, r.body_half_x + 0.010)
    )
    return body, "housing_form__microfuge__drum_body"


def _housing_plinth_shell_build(r: ResolvedConfig):
    """The same shell standing on a continuous moulded pedestal skirt."""
    skirt_h = min(0.055, 0.30 * r.body_top_z)
    body = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, skirt_h + 0.5 * (r.body_top_z - skirt_h)))
        .box(2.0 * r.body_half_x, 2.0 * r.body_half_y, r.body_top_z - skirt_h)
        .edges("|Z")
        .fillet(min(0.030, r.body_half_x * 0.40))
    )
    # The skirt is drawn in on every side and meets the bench as one moulding.
    body = body.union(
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, 0.5 * (skirt_h + 0.004)))
        .box(
            2.0 * (r.body_half_x - 0.018),
            2.0 * (r.body_half_y - 0.018),
            skirt_h + 0.004,
        )
        .edges("|Z")
        .fillet(min(0.020, r.body_half_x * 0.30))
    )
    return body, "housing_form__plinth_shell__plinth_body"


_HOUSING_BUILDERS = {
    "benchtop_shell": _housing_benchtop_shell_build,
    "plinth_shell": _housing_plinth_shell_build,
    "clinical_box": _housing_clinical_box_build,
    "microfuge": _housing_microfuge_build,
}


def _build_housing(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    housing = model.part("housing", meta={"role": "housing"})
    body, body_name = _HOUSING_BUILDERS[r.housing_form](r)
    # The rotor well is a real recess, and the drive boss stands on its floor.
    body = body.cut(_z_cyl(r.well_floor_z, r.body_top_z + 0.01, r.well_radius_m))
    body = body.union(_z_cyl(r.well_floor_z, r.well_floor_z + BOSS_H, HUB_R - 0.004))
    body = body.cut(
        _z_cyl(r.well_floor_z - 0.030, r.well_floor_z + BOSS_H + 0.01, SHAFT_R + FIT)
    )
    housing.visual(mesh_from_cadquery(body, "cfg_housing_body"), material=mats["shell"], name=body_name, material_class_id="plastic.opaque_glossy_molded")
    # Moulded rim around the well mouth.
    rim = _z_cyl(
        r.body_top_z - 0.010, r.body_top_z, r.well_radius_m + RIM_T
    ).cut(_z_cyl(r.body_top_z - 0.02, r.body_top_z + 0.01, r.well_radius_m))
    housing.visual(mesh_from_cadquery(rim, "cfg_well_rim"), material=mats["trim"], name="well_rim", material_class_id="plastic.opaque_glossy_molded")
    # Front control panel, on whichever face the active housing presents.
    panel_y = r.body_half_x if r.housing_form == "microfuge" else r.body_half_y
    housing.visual(
        Box((min(0.120, 1.4 * r.body_half_x), 0.010, PANEL_H)),
        origin=Origin(
            xyz=(0.0, -(panel_y - 0.004), r.body_top_z - 0.030 - 0.5 * PANEL_H)
        ),
        material=mats["panel"],
        name="control_panel", material_class_id="tech.control_interface",
    )
    for index, sx in enumerate((-1.0, 1.0)):
        housing.visual(
            Cylinder(radius=0.010, length=0.008),
            origin=Origin(
                xyz=(
                    sx * 0.030,
                    -(panel_y - 0.006),
                    r.body_top_z - 0.030 - 0.5 * PANEL_H,
                ),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["accent"],
            name=f"panel_knob_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    return housing


# --- rotor candidates ------------------------------------------------------------
def _rotor_fixed_angle_build(
    part, offset: tuple[float, float, float], r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """A solid conical rotor drilled with evenly indexed angled tube wells."""
    z0 = r.well_floor_z + BOSS_H
    z1 = z0 + r.rotor_height_m
    body = _z_cyl(z0, z1, r.rotor_radius_m)
    body = body.cut(
        _z_cyl(z0 + 0.006, z1 + 0.01, r.rotor_radius_m - 0.006).cut(
            _z_cyl(z0, z1 + 0.02, HUB_R)
        )
    )
    part.visual(
        mesh_from_cadquery(body, "cfg_fixed_angle_rotor"),
        origin=_local_origin(None, offset),
        material=mats["metal"],
        name="rotor_form__fixed_angle__rotor_body", material_class_id="metal.aluminum_bare",
    )
    for index in range(r.tube_holder_count):
        a = 2.0 * math.pi * index / r.tube_holder_count
        x = r.holder_circle_m * math.cos(a)
        y = r.holder_circle_m * math.sin(a)
        well = _z_cyl(z0 + 0.004, z1 + 0.004, HOLDER_R + 0.002, x, y).cut(
            _z_cyl(z0 + 0.008, z1 + 0.02, HOLDER_R, x, y)
        )
        part.visual(
            mesh_from_cadquery(well, f"cfg_fixed_well_{index}"),
            origin=_local_origin(None, offset),
            material=mats["metal"],
            name=f"rotor_form__fixed_angle__tube_well_{index}", material_class_id="metal.aluminum_bare",
        )
        _add_test_tube(
            part,
            offset,
            x=x,
            y=y,
            base_z=z0 + 0.003,
            length=r.holder_depth_m + 0.007,
            # A shallow radial lean keeps the tapered tube inside the smallest
            # rotor while preserving the source asset's visibly non-vertical feel.
            tilt=math.radians(4.0),
            yaw=a,
            mats=mats,
            name=f"rotor_form__fixed_angle__tube_{index}",
        )


def _rotor_swing_bucket_build(
    part, offset: tuple[float, float, float], r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """A spider rotor with indexed bucket carriers hung off its arms."""
    z0 = r.well_floor_z + BOSS_H
    z1 = z0 + r.rotor_height_m
    part.visual(
        Cylinder(radius=HUB_R, length=r.rotor_height_m),
        origin=_local_origin(Origin(xyz=(0.0, 0.0, 0.5 * (z0 + z1))), offset),
        material=mats["metal"],
        name="rotor_form__swing_bucket__hub", material_class_id="metal.aluminum_bare",
    )
    for index in range(r.tube_holder_count):
        a = 2.0 * math.pi * index / r.tube_holder_count
        x = r.holder_circle_m * math.cos(a)
        y = r.holder_circle_m * math.sin(a)
        # The radial carrier terminates before the bucket/tube envelope.  The
        # previous full-radius bar reached the tube centre and visibly pierced
        # the cap; keep a short radial clearance at the outer end instead.
        arm_end = max(0.012, r.holder_circle_m - HOLDER_R - 0.004)
        part.visual(
            Box((arm_end, 0.008, 0.008)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        0.5 * arm_end * math.cos(a),
                        0.5 * arm_end * math.sin(a),
                        z0 + 0.010,
                    ),
                    rpy=(0.0, 0.0, a),
                ),
                offset,
            ),
            material=mats["metal"],
            name=f"rotor_form__swing_bucket__arm_{index}", material_class_id="metal.aluminum_bare",
        )
        # A forked side yoke transfers the arm load into the bucket wall.  It
        # stays outside the tube radius, so the support remains connected
        # without becoming a bar through the tube centre.
        connector_start = arm_end
        connector_end = r.holder_circle_m - 0.006
        connector_len = max(0.002, connector_end - connector_start)
        connector_center = 0.5 * (connector_start + connector_end)
        for side in (-1.0, 1.0):
            tangent = side * 0.008
            part.visual(
                Box((connector_len, 0.003, 0.006)),
                origin=_local_origin(
                    Origin(
                        xyz=(
                            connector_center * math.cos(a) - tangent * math.sin(a),
                            connector_center * math.sin(a) + tangent * math.cos(a),
                            z0 + 0.010,
                        ),
                        rpy=(0.0, 0.0, a),
                    ),
                    offset,
                ),
                material=mats["metal"],
                name=f"rotor_form__swing_bucket__arm_yoke_{index}_{int(side)}", material_class_id="metal.aluminum_bare",
            )
        part.visual(
            Box((0.006, 0.020, 0.006)),
            origin=_local_origin(
                Origin(
                    xyz=(arm_end * math.cos(a), arm_end * math.sin(a), z0 + 0.010),
                    rpy=(0.0, 0.0, a),
                ),
                offset,
            ),
            material=mats["metal"],
            name=f"rotor_form__swing_bucket__arm_crossbar_{index}", material_class_id="metal.aluminum_bare",
        )
        bucket = _z_cyl(z0 + 0.002, z1 - 0.002, HOLDER_R + 0.003, x, y).cut(
            _z_cyl(z0 + 0.006, z1 + 0.02, HOLDER_R, x, y)
        )
        part.visual(
            mesh_from_cadquery(bucket, f"cfg_bucket_{index}"),
            origin=_local_origin(None, offset),
            material=mats["dark"],
            name=f"rotor_form__swing_bucket__bucket_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Cylinder(radius=HOLDER_R + 0.004, length=0.004),
            origin=_local_origin(Origin(xyz=(x, y, z1 - 0.001)), offset),
            material=mats["tube_cap"],
            name=f"rotor_form__swing_bucket__tube_cap_{index}", material_class_id="plastic.opaque_glossy_molded",
        )


_ROTOR_BUILDERS = {
    "fixed_angle": _rotor_fixed_angle_build,
    "swing_bucket": _rotor_swing_bucket_build,
}


def _build_rotor(model: ArticulatedObject, housing, r: ResolvedConfig, mats: dict[str, str]):
    rotor = model.part("rotor", meta={"role": "rotor"})
    off = (0.0, 0.0, r.well_floor_z + BOSS_H)
    _ROTOR_BUILDERS[r.rotor_form](rotor, off, r, mats)
    rotor.visual(
        Cylinder(radius=SHAFT_R, length=BOSS_H + 0.010),
        origin=_local_origin(
            Origin(
                xyz=(
                    0.0,
                    0.0,
                    r.well_floor_z
                    + BOSS_H
                    - 0.5 * (BOSS_H + 0.010)
                    + 0.004,
                )
            ),
            off,
        ),
        material=mats["metal"],
        name="rotor__shaft", material_class_id="metal.stainless_matte",
    )
    provider = AxisInterface(
        name="housing_to_rotor__provider",
        point=off,
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name="housing_to_rotor__consumer", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "housing_to_rotor",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=rotor,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=30.0, velocity=200.0),
        meta={"positive_motion": "spins the rotor in the well"},
    )
    register_interface_mate(model, "housing_to_rotor", mate)
    return rotor


# --- lid candidates ---------------------------------------------------------------
def _lid_plate(r: ResolvedConfig, name: str, *, skirt: bool):
    plate = _z_cyl(0.0, LID_T, r.well_radius_m + RIM_T)
    if skirt:
        plate = plate.union(_z_cyl(-0.006, 0.0, r.well_radius_m - FIT))
    if skirt:
        plate = plate.cut(_z_cyl(-0.02, LID_T - 0.004, r.well_radius_m - 0.012))
    return mesh_from_cadquery(plate, name)


def _build_lid(model: ArticulatedObject, housing, r: ResolvedConfig, mats: dict[str, str]):
    lid = model.part("lid", meta={"role": "lid"})
    # A hinged cover rests straight on the rim; a sliding cover runs on rails
    # that stand proud of the housing top.
    lid_z = r.body_top_z + (SEAT if r.lid_action == "hinged_lid" else 0.012)
    if r.lid_action == "hinged_lid":
        hinge_y = r.well_radius_m + RIM_T + 0.004
        off = (0.0, hinge_y, lid_z + 0.5 * LID_T)
        lid.visual(
            _lid_plate(r, "cfg_hinged_lid", skirt=True),
            origin=_local_origin(Origin(xyz=(0.0, 0.0, lid_z)), off),
            material=mats["trim"],
            name="lid_action__hinged_lid__cover_plate", material_class_id="plastic.opaque_glossy_molded",
        )
        lid.visual(
            Cylinder(radius=0.008, length=0.060),
            origin=_local_origin(
                Origin(
                    xyz=(0.0, hinge_y, lid_z + 0.5 * LID_T),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                off,
            ),
            material=mats["metal"],
            name="lid_action__hinged_lid__hinge_barrel", material_class_id="metal.stainless_matte",
        )
        # Knuckles on the housing keep the open lid in contact with the body.
        for index, sx in enumerate((-1.0, 1.0)):
            housing.visual(
                Cylinder(radius=0.012, length=0.014),
                origin=Origin(
                    xyz=(sx * 0.038, hinge_y, lid_z + 0.5 * LID_T),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                material=mats["trim"],
                name=f"lid_action__hinged_lid__hinge_knuckle_{index}", material_class_id="plastic.opaque_glossy_molded",
            )
        provider = AxisInterface(
            name="housing_to_lid__provider",
            point=off,
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, -1.0, 0.0),
        )
        consumer = AxisInterface(
            name="housing_to_lid__consumer", axis=(1.0, 0.0, 0.0), radial=(0.0, -1.0, 0.0)
        )
        mate = mate_axes(provider, consumer)
        model.articulation(
            "housing_to_lid",
            ArticulationType.REVOLUTE,
            parent=housing,
            child=lid,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=20.0, velocity=2.0, lower=-1.4, upper=0.0),
            meta={"positive_motion": "swings the lid up off the well"},
        )
        register_interface_mate(model, "housing_to_lid", mate)
    elif r.lid_action == "lift_lid":
        off = (0.0, 0.0, lid_z + 0.5 * LID_T)
        lid.visual(
            _lid_plate(r, "cfg_lift_lid", skirt=True),
            origin=_local_origin(Origin(xyz=(0.0, 0.0, lid_z)), off),
            material=mats["trim"],
            name="lid_action__lift_lid__dome_plate", material_class_id="plastic.opaque_glossy_molded",
        )
        post_x = r.well_radius_m + RIM_T + 0.014
        for index, sx in enumerate((-1.0, 1.0)):
            # The collar rides the guide post with a running fit.
            collar = _z_cyl(lid_z, lid_z + 0.022, 0.016, sx * post_x, 0.0).cut(
                _z_cyl(lid_z - 0.01, lid_z + 0.04, 0.008 + FIT, sx * post_x, 0.0)
            )
            lid.visual(
                mesh_from_cadquery(collar, f"cfg_lift_collar_{index}"),
                origin=_local_origin(None, off),
                material=mats["metal"],
                name=f"lid_action__lift_lid__guide_collar_{index}", material_class_id="metal.stainless_matte",
            )
            arm_x0 = r.well_radius_m - 0.006
            arm_x1 = post_x - 0.010
            lid.visual(
                Box((arm_x1 - arm_x0, 0.020, 0.010)),
                origin=_local_origin(
                    Origin(
                        xyz=(sx * 0.5 * (arm_x0 + arm_x1), 0.0, lid_z + 0.006)
                    ),
                    off,
                ),
                material=mats["trim"],
                name=f"lid_action__lift_lid__collar_arm_{index}", material_class_id="plastic.opaque_glossy_molded",
            )
            housing.visual(
                Cylinder(radius=0.008, length=r.lid_travel_m + 0.050),
                origin=Origin(
                    xyz=(
                        sx * post_x,
                        0.0,
                        r.body_top_z + 0.5 * (r.lid_travel_m + 0.050) - 0.010,
                    )
                ),
                material=mats["metal"],
                name=f"lid_action__lift_lid__guide_post_{index}", material_class_id="metal.stainless_matte",
            )
        model.articulation(
            "housing_to_lid",
            ArticulationType.PRISMATIC,
            parent=housing,
            child=lid,
            origin=Origin(xyz=off),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=20.0, velocity=0.25, lower=0.0, upper=r.lid_travel_m
            ),
            meta={"positive_motion": "lifts the dome off the well"},
        )
    else:
        off = (0.0, 0.0, lid_z + 0.5 * LID_T)
        lid.visual(
            _lid_plate(r, "cfg_sliding_lid", skirt=False),
            origin=_local_origin(Origin(xyz=(0.0, 0.0, lid_z)), off),
            material=mats["trim"],
            name="lid_action__sliding_lid__cover_plate", material_class_id="plastic.opaque_glossy_molded",
        )
        for index, sx in enumerate((-1.0, 1.0)):
            lid.visual(
                Box((0.014, 2.0 * (r.well_radius_m + RIM_T), 0.008)),
                origin=_local_origin(
                    Origin(
                        xyz=(
                            sx * (r.well_radius_m + RIM_T - 0.007),
                            0.0,
                            lid_z - 0.004,
                        )
                    ),
                    off,
                ),
                material=mats["metal"],
                name=f"lid_action__sliding_lid__slider_{index}", material_class_id="metal.aluminum_bare",
            )
            # The rails the slider runs on belong to the housing.
            housing.visual(
                Box((0.010, 2.0 * (r.well_radius_m + RIM_T) + r.lid_travel_m, 0.012)),
                origin=Origin(
                    xyz=(
                        sx * (r.well_radius_m + RIM_T + 0.006),
                        0.5 * r.lid_travel_m,
                        r.body_top_z + 0.006,
                    )
                ),
                material=mats["trim"],
                name=f"lid_action__sliding_lid__rail_{index}", material_class_id="plastic.opaque_glossy_molded",
            )
            rail_x = sx * (r.well_radius_m + RIM_T + 0.006)
            rail_start = -(r.well_radius_m + RIM_T) - 0.005
            rail_end = r.well_radius_m + RIM_T + r.lid_travel_m + 0.005
            for end_name, rail_y in (("front", rail_start), ("rear", rail_end)):
                housing.visual(
                    Box((0.024, 0.020, 0.020)),
                    origin=Origin(xyz=(rail_x, rail_y, r.body_top_z + 0.010)),
                    material=mats["dark"],
                    name=f"lid_action__sliding_lid__stop_block_{end_name}_{index}", material_class_id="rubber.smooth_plain",
                )
        model.articulation(
            "housing_to_lid",
            ArticulationType.PRISMATIC,
            parent=housing,
            child=lid,
            origin=Origin(xyz=off),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=20.0, velocity=0.25, lower=0.0, upper=r.lid_travel_m
            ),
            meta={"positive_motion": "slides the lid back off the well"},
        )
    return lid


# --- panel control candidates ------------------------------------------------------
def _control_seat(r: ResolvedConfig) -> tuple[float, float, float]:
    """Front-right of the control panel, on whichever face the housing shows."""
    panel_y = r.body_half_x if r.housing_form == "microfuge" else r.body_half_y
    return (
        min(0.060, 0.6 * r.body_half_x),
        -(panel_y - 0.002),
        r.body_top_z - 0.030 - 0.5 * PANEL_H,
    )


def _panel_control_latch_lever_build(model, housing, r, mats):
    """A shafted lever with a tipped handle swinging on the housing front."""
    seat = _control_seat(r)
    latch = model.part("panel_control__latch_lever__latch", meta={"role": "panel_control"})
    latch.visual(
        Cylinder(radius=0.0065, length=0.022),
        origin=_local_origin(
            Origin(
                xyz=(seat[0], seat[1] - 0.008, seat[2]),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            seat,
        ),
        material=mats["metal"],
        name="panel_control__latch_lever__latch_shaft", material_class_id="metal.stainless_matte",
    )
    latch.visual(
        Box((0.018, 0.010, 0.044)),
        origin=_local_origin(
            Origin(xyz=(seat[0], seat[1] - 0.021, seat[2] + 0.018)), seat
        ),
        material=mats["trim"],
        name="panel_control__latch_lever__latch_handle", material_class_id="plastic.opaque_glossy_molded",
    )
    latch.visual(
        Cylinder(radius=0.010, length=0.012),
        origin=_local_origin(
            Origin(
                xyz=(seat[0], seat[1] - 0.021, seat[2] + 0.040),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            seat,
        ),
        material=mats["trim"],
        name="panel_control__latch_lever__latch_tip", material_class_id="plastic.opaque_glossy_molded",
    )
    provider = AxisInterface(
        name="housing_to_panel_control__provider", point=seat, axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
    )
    consumer = AxisInterface(
        name="housing_to_panel_control__consumer", axis=(0.0, 1.0, 0.0), radial=(0.0, 0.0, 1.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "housing_to_panel_control",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=latch,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=3.0, velocity=3.0, lower=-0.42, upper=0.42),
        meta={"positive_motion": "swings the latch off the lid"},
    )
    register_interface_mate(model, "housing_to_panel_control", mate)
    return latch


def _panel_control_push_button_build(model, housing, r, mats):
    """A momentary button on a short travel into its own housing recess."""
    seat = _control_seat(r)
    # A real bezel with an opening the button travels through, not a solid pad.
    bezel = _box_at(
        seat[0] - 0.015,
        seat[0] + 0.015,
        seat[1] - 0.008,
        seat[1] + 0.002,
        seat[2] - 0.012,
        seat[2] + 0.012,
    ).cut(
        _box_at(
            seat[0] - 0.008 - FIT,
            seat[0] + 0.008 + FIT,
            seat[1] - 0.03,
            seat[1] + 0.03,
            seat[2] - 0.006 - FIT,
            seat[2] + 0.006 + FIT,
        )
    )
    housing.visual(
        mesh_from_cadquery(bezel, "cfg_button_bezel"),
        material=mats["dark"],
        name="panel_control__push_button__button_recess", material_class_id="plastic.opaque_glossy_molded",
    )
    button = model.part("panel_control__push_button__button", meta={"role": "panel_control"})
    button.visual(
        Box((0.016, 0.010, 0.012)),
        origin=_local_origin(Origin(xyz=(seat[0], seat[1] - 0.010, seat[2])), seat),
        material=mats["accent"],
        name="panel_control__push_button__button_body", material_class_id="plastic.opaque_glossy_molded",
    )
    button.visual(
        Box((0.020, 0.004, 0.016)),
        origin=_local_origin(Origin(xyz=(seat[0], seat[1] - 0.016, seat[2])), seat),
        material=mats["trim"],
        name="panel_control__push_button__button_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "housing_to_panel_control",
        ArticulationType.PRISMATIC,
        parent=housing,
        child=button,
        origin=Origin(xyz=seat),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.05, lower=0.0, upper=0.005),
        meta={"positive_motion": "presses the button into its recess"},
    )
    return button


_PANEL_CONTROL_BUILDERS = {
    "latch_lever": _panel_control_latch_lever_build,
    "push_button": _panel_control_push_button_build,
}


# --- assembly ---------------------------------------------------------------------
def build_picturex_0611_centrifuge_machine1(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_centrifuge_machine1",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "tube-holder rotor spinning in a recessed well under a lid",
        },
    )
    mats = _materials(model, r)
    housing = _build_housing(model, r, mats)
    _build_rotor(model, housing, r, mats)
    _build_lid(model, housing, r, mats)
    _PANEL_CONTROL_BUILDERS[r.panel_control](model, housing, r, mats)

    lid_open = -1.4 if r.lid_action == "hinged_lid" else r.lid_travel_m
    model.meta["risk_poses"] = (
        {"housing_to_rotor": 0.0, "housing_to_lid": 0.0},
        {"housing_to_rotor": math.pi, "housing_to_lid": lid_open},
        {"housing_to_rotor": math.pi / 2.0, "housing_to_lid": 0.5 * lid_open},
    )
    model.meta["coupled_joint_pairs"] = (("housing_to_rotor", "housing_to_lid"),)
    return model


def build_seeded_picturex_0611_centrifuge_machine1(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_centrifuge_machine1(config_from_seed(seed), assets=assets)


# --- authored tests ----------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_centrifuge_machine1_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    housings = _parts_by_role(model, "housing")
    rotors = _parts_by_role(model, "rotor")
    lids = _parts_by_role(model, "lid")
    joints = {j.name: j for j in model.articulations}
    rotor_joint = joints.get("housing_to_rotor")
    lid_joint = joints.get("housing_to_lid")

    ctx.check(
        "category_anchor: recessed rotor well with a spinning holder ring",
        len(housings) == 1
        and len(rotors) == 1
        and len(lids) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "housing"
        and rotor_joint is not None
        and rotor_joint.articulation_type == ArticulationType.CONTINUOUS
        and tuple(round(abs(v), 6) for v in rotor_joint.axis) == (0.0, 0.0, 1.0)
        and rotor_joint.parent == "housing"
        and lid_joint is not None
        and lid_joint.parent == "housing",
        details=(
            f"housings={len(housings)} rotors={len(rotors)} lids={len(lids)} "
            f"joints={sorted(joints)}"
        ),
    )

    ctx.check(
        "category_anchor: the rotor turns clear of the well and under the closed lid",
        0.0 < FIT <= 0.001
        and abs(r.well_radius_m - (r.rotor_radius_m + WELL_GAP)) < 1e-9
        and r.holder_circle_m + HOLDER_R < r.rotor_radius_m
        and r.holder_circle_m > HUB_R
        and r.well_floor_z > 0.020
        and r.lid_clear_z_m <= r.body_top_z
        and r.tube_holder_count >= 8,
        details=(
            f"well={r.well_radius_m} rotor={r.rotor_radius_m} circle={r.holder_circle_m} "
            f"floor={r.well_floor_z} lid_clear={r.lid_clear_z_m} top={r.body_top_z}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    housing_ok = {
        "benchtop_shell": any("benchtop_shell__shell_body" in n for n in visual_names),
        "plinth_shell": any("plinth_shell__plinth_body" in n for n in visual_names),
        "clinical_box": any("clinical_box__cabinet_body" in n for n in visual_names),
        "microfuge": any("microfuge__drum_body" in n for n in visual_names),
    }[r.housing_form]
    ctx.check(
        "category_anchor: housing_form identity",
        housing_ok
        and any("well_rim" in n for n in visual_names)
        and any("control_panel" in n for n in visual_names),
        details=f"housing={r.housing_form}",
    )

    rotor_ok = {
        "fixed_angle": sum(1 for n in visual_names if "fixed_angle__tube_well_" in n)
        == r.tube_holder_count
        and sum(1 for n in visual_names if "fixed_angle__tube_" in n and "__tube_body" in n)
        == r.tube_holder_count
        and sum(1 for n in visual_names if "fixed_angle__tube_" in n and "__tube_cap" in n)
        == r.tube_holder_count
        and any("fixed_angle__rotor_body" in n for n in visual_names),
        "swing_bucket": sum(1 for n in visual_names if "swing_bucket__bucket_" in n)
        == r.tube_holder_count
        and sum(
            1
            for n in visual_names
            if "swing_bucket__arm_" in n
            and "arm_yoke_" not in n
            and "arm_crossbar_" not in n
        )
        == r.tube_holder_count
        and sum(1 for n in visual_names if "swing_bucket__arm_yoke_" in n)
        == 2 * r.tube_holder_count
        and sum(1 for n in visual_names if "swing_bucket__arm_crossbar_" in n)
        == r.tube_holder_count
        and sum(1 for n in visual_names if "swing_bucket__tube_cap_" in n)
        == r.tube_holder_count,
    }[r.rotor_form]
    ctx.check(
        "category_anchor: rotor_form identity",
        rotor_ok,
        details=f"rotor={r.rotor_form} n={r.tube_holder_count}",
    )

    lid_ok = {
        "hinged_lid": lid_joint.articulation_type == ArticulationType.REVOLUTE
        and any("hinged_lid__hinge_barrel" in n for n in visual_names)
        and sum(1 for n in visual_names if "hinged_lid__hinge_knuckle" in n) == 2,
        "sliding_lid": lid_joint.articulation_type == ArticulationType.PRISMATIC
        and sum(1 for n in visual_names if "sliding_lid__rail_" in n) == 2
        and sum(1 for n in visual_names if "sliding_lid__slider_" in n) == 2
        and sum(1 for n in visual_names if "sliding_lid__stop_block_" in n) == 4,
        "lift_lid": lid_joint.articulation_type == ArticulationType.PRISMATIC
        and sum(1 for n in visual_names if "lift_lid__guide_post_" in n) == 2
        and sum(1 for n in visual_names if "lift_lid__guide_collar_" in n) == 2,
    }[r.lid_action]
    ctx.check("category_anchor: lid_action identity", lid_ok, details=f"lid={r.lid_action}")

    control_ok = {
        "latch_lever": any("latch_lever__latch_tip" in n for n in visual_names)
        and joints["housing_to_panel_control"].articulation_type == ArticulationType.REVOLUTE,
        "push_button": any("push_button__button_cap" in n for n in visual_names)
        and any("push_button__button_recess" in n for n in visual_names)
        and joints["housing_to_panel_control"].articulation_type == ArticulationType.PRISMATIC,
    }[r.panel_control]
    ctx.check(
        "category_anchor: panel_control identity",
        control_ok,
        details=f"control={r.panel_control}",
    )

    # Motion evidence: the rotor really turns about the well axis.
    rest = ctx.part_world_aabb(rotors[0])
    # pi/7 is not a symmetry angle of any admissible holder count, so the
    # footprint really has to move.
    with ctx.pose({rotor_joint: math.pi / 7.0}):
        turned = ctx.part_world_aabb(rotors[0])
    ctx.check(
        "the rotor spins about the well axis without leaving the well",
        rest is not None
        and turned is not None
        and abs(turned[0][2] - rest[0][2]) < 1e-6
        and abs(turned[1][2] - rest[1][2]) < 1e-6
        and max(abs(turned[1][0]), abs(turned[1][1]))
        < math.sqrt(2.0) * r.rotor_radius_m + 1e-6,
        details=f"rest={rest} turned={turned}",
    )

    # Motion evidence: the lid really uncovers the well.
    closed = ctx.part_world_aabb(lids[0])
    target = -1.4 if r.lid_action == "hinged_lid" else r.lid_travel_m
    with ctx.pose({lid_joint: target}):
        opened = ctx.part_world_aabb(lids[0])
    ctx.check(
        "the lid uncovers the rotor well when opened",
        closed is not None
        and opened is not None
        and (
            opened[1][2] > closed[1][2] + 0.4 * r.well_radius_m
            if r.lid_action == "hinged_lid"
            else (
                opened[0][2] > closed[0][2] + 0.8 * r.well_radius_m
                if r.lid_action == "lift_lid"
                else opened[0][1] > closed[0][1] + 0.8 * r.well_radius_m
            )
        ),
        details=f"closed={closed} opened={opened}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_rotor_eight_holders_microfuge_hinged",
        {
            "housing_form": "microfuge",
            "rotor_form": "fixed_angle",
            "lid_action": "hinged_lid",
            "panel_control": "latch_lever",
            "tube_holder_count": 8,
            "rotor_radius_m": 0.060,
            "body_height_m": 0.130,
            "holder_depth_m": 0.030,
        },
        reason="smallest rotor in the shortest body with the fewest holders",
    ),
    corner_case(
        "max_rotor_24_holders_clinical_sliding",
        {
            "housing_form": "clinical_box",
            "rotor_form": "swing_bucket",
            "lid_action": "sliding_lid",
            "panel_control": "push_button",
            "tube_holder_count": 24,
            "rotor_radius_m": 0.130,
            "body_height_m": 0.290,
            "holder_depth_m": 0.070,
        },
        reason="largest rotor with twenty-four buckets and the longest sliding lid",
    ),
    corner_case(
        "min_rotor_24_holders_bench_sliding",
        {
            "housing_form": "plinth_shell",
            "rotor_form": "swing_bucket",
            "lid_action": "lift_lid",
            "panel_control": "push_button",
            "tube_holder_count": 24,
            "rotor_radius_m": 0.060,
            "body_height_m": 0.290,
            "holder_depth_m": 0.030,
        },
        reason="twenty-four holders on the smallest holder circle — the tightest arc",
    ),
    corner_case(
        "max_rotor_eight_holders_microfuge_hinged",
        {
            "housing_form": "microfuge",
            "rotor_form": "fixed_angle",
            "lid_action": "hinged_lid",
            "panel_control": "latch_lever",
            "tube_holder_count": 8,
            "rotor_radius_m": 0.130,
            "body_height_m": 0.130,
            "holder_depth_m": 0.070,
        },
        reason="widest, deepest rotor in the shortest body — the deepest well",
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
    "build_picturex_0611_centrifuge_machine1",
    "build_seeded_picturex_0611_centrifuge_machine1",
    "run_picturex_0611_centrifuge_machine1_tests",
]
