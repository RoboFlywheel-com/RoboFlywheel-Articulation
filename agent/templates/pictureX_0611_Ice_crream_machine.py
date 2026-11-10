# SPDX-License-Identifier: Apache-2.0

"""Self-contained batch ice-cream freezer template.

One grounded ``vessel`` part carries the body and the freezing cavity of the
active vessel candidate.  Every candidate exports the same three numbers --
mouth height, rim radius and cavity depth -- so the lid, mount, dasher and
drive fit without a compatibility gate.  A ``drive_mount`` part is FIXED on the
rim and carries a bored bearing sleeve on the axis; the ``drive`` (hand crank
or motor spindle) turns CONTINUOUS in that sleeve and the ``dasher`` turns
CONTINUOUS on the same axis, mimicking the drive.  ``dasher_blade_count``
blades are set at even yaws and staggered heights, each reaching to 4 mm from
the wall.

Five slots vary without touching that chain: ``vessel_body`` (countertop bowl,
coopered bucket, upright tub), ``dasher_form`` (paddles, full-width scraper
bars, radial plates), ``drive_mount`` (bridge yoke or cast arch),
``access_form`` (lift-off lid or hinged cap) and ``drive_form`` (hand crank or
motor pod).
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
    Mimic,
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

VesselBody = Literal["countertop_bowl", "coopered_bucket", "upright_tub"]
DasherForm = Literal["paddle_blades", "scraper_bars", "radial_plates"]
DriveMount = Literal["arch_frame", "bridge_yoke", "bearing_web"]
AccessForm = Literal["lift_off_lid", "hinged_cap"]
DriveForm = Literal["hand_crank", "motor_pod"]
PaletteStyle = Literal["cream_enamel", "oak_and_steel", "stainless", "mint_appliance"]

VESSEL_BODIES: tuple[VesselBody, ...] = ("countertop_bowl", "coopered_bucket", "upright_tub")
DASHER_FORMS: tuple[DasherForm, ...] = ("paddle_blades", "scraper_bars", "radial_plates")
DRIVE_MOUNTS: tuple[DriveMount, ...] = ("arch_frame", "bridge_yoke", "bearing_web")
ACCESS_FORMS: tuple[AccessForm, ...] = ("lift_off_lid", "hinged_cap")
DRIVE_FORMS: tuple[DriveForm, ...] = ("hand_crank", "motor_pod")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "cream_enamel",
    "oak_and_steel",
    "stainless",
    "mint_appliance",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("vessel_body", VESSEL_BODIES),
        component_slot("dasher_form", DASHER_FORMS),
        component_slot("drive_mount", DRIVE_MOUNTS),
        component_slot("access_form", ACCESS_FORMS),
        component_slot("drive_form", DRIVE_FORMS),
        multiplicity_slot("dasher_blade_count", (2, 3, 4), item_slot="dasher_form"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cream_enamel": {
        "body": (0.90, 0.87, 0.76, 1.0),
        "trim": (0.30, 0.32, 0.34, 1.0),
        "steel": (0.76, 0.78, 0.80, 1.0),
        "dark": (0.13, 0.13, 0.14, 1.0),
        "wood": (0.62, 0.44, 0.26, 1.0),
        "accent": (0.55, 0.16, 0.14, 1.0),
    },
    "oak_and_steel": {
        "body": (0.66, 0.48, 0.28, 1.0),
        "trim": (0.44, 0.31, 0.18, 1.0),
        "steel": (0.72, 0.74, 0.76, 1.0),
        "dark": (0.16, 0.14, 0.12, 1.0),
        "wood": (0.74, 0.57, 0.35, 1.0),
        "accent": (0.35, 0.36, 0.38, 1.0),
    },
    "stainless": {
        "body": (0.78, 0.79, 0.81, 1.0),
        "trim": (0.52, 0.54, 0.56, 1.0),
        "steel": (0.84, 0.86, 0.88, 1.0),
        "dark": (0.12, 0.12, 0.13, 1.0),
        "wood": (0.58, 0.42, 0.26, 1.0),
        "accent": (0.24, 0.36, 0.52, 1.0),
    },
    "mint_appliance": {
        "body": (0.60, 0.80, 0.72, 1.0),
        "trim": (0.36, 0.56, 0.50, 1.0),
        "steel": (0.80, 0.82, 0.84, 1.0),
        "dark": (0.11, 0.13, 0.13, 1.0),
        "wood": (0.66, 0.49, 0.31, 1.0),
        "accent": (0.90, 0.88, 0.84, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
WALL = 0.006              # vessel wall thickness
FLOOR_T = 0.010           # vessel floor thickness
SHAFT_R = 0.006           # dasher shaft radius
BLADE_GAP = 0.004         # clear gap between a blade tip and the wall
LID_T = 0.010
LID_TRAVEL = 0.024
# Radial running fit, under the 1 mm assembly-gap tolerance: the shaft is
# journalled in its sleeve and lid bore with no penetration.
FIT = 0.0008
SEAT = 0.0006             # sub-millimetre seating lap
SLEEVE_R = SHAFT_R + FIT + 0.006
POST_OUTSET = 0.014       # mount post stand-off outside the rim, clear of the lid
DRIVE_RISE = 0.075        # drive axis height above the mouth
BRIDGE_T = 0.014
HATCH_OPEN = 1.2          # hinged rim-hatch opening angle
# The dasher shaft stops 1 mm under the drive spindle: both run in the same
# sleeve, so the pair reads as coupled without either cutting into the other.
SHAFT_TOP_LOCAL = -0.010
# Top of the mount's bearing sleeve, in the drive frame: all drive hardware
# stands above it so nothing rotates inside the bore it is journalled in.
SLEEVE_TOP_LOCAL = 0.016


@dataclass(frozen=True)
class Config:
    vessel_body: VesselBody = "countertop_bowl"
    dasher_form: DasherForm = "paddle_blades"
    drive_mount: DriveMount = "bridge_yoke"
    access_form: AccessForm = "lift_off_lid"
    drive_form: DriveForm = "hand_crank"
    dasher_blade_count: int = 3
    vessel_radius_m: float | None = None
    vessel_depth_m: float | None = None
    crank_throw_m: float | None = None
    palette_style: PaletteStyle = "cream_enamel"
    name: str = "pictureX_0611_Ice_crream_machine"


@dataclass(frozen=True)
class ResolvedConfig:
    vessel_body: VesselBody
    dasher_form: DasherForm
    drive_mount: DriveMount
    access_form: AccessForm
    drive_form: DriveForm
    dasher_blade_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    vessel_radius_m: float
    vessel_depth_m: float
    crank_throw_m: float
    rim_radius_m: float
    lid_radius_m: float
    outer_x_m: float
    outer_y_m: float
    mount_leg_m: float
    blade_reach_m: float
    body_base_z: float
    cavity_floor_z: float
    mouth_z: float
    drive_axis_z_m: float
    yoke_span_m: float
    bridge_z: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x1C_E9_C2_4A)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        vessel_body=choices["vessel_body"],
        dasher_form=choices["dasher_form"],
        drive_mount=choices["drive_mount"],
        access_form=choices["access_form"],
        drive_form=choices["drive_form"],
        dasher_blade_count=choices["dasher_blade_count"],
        vessel_radius_m=round(rng.uniform(0.070, 0.150), 4),
        vessel_depth_m=round(rng.uniform(0.120, 0.320), 4),
        crank_throw_m=round(rng.uniform(0.060, 0.130), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"ice_crream_machine_seed_{int(seed)}",
    )


_BODY_LIFT = {"countertop_bowl": 0.026, "coopered_bucket": 0.014, "upright_tub": 0.020}
# Outer envelope of each vessel body beyond the rim, in x and y.  The drive
# mount stands its legs outside this envelope and clamps back onto it.
_VESSEL_OUTER = {
    "countertop_bowl": (0.030, 0.022),
    "coopered_bucket": (0.024, 0.024),
    "upright_tub": (0.005, 0.005),
}


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "vessel_body": config.vessel_body,
            "dasher_form": config.dasher_form,
            "drive_mount": config.drive_mount,
            "access_form": config.access_form,
            "drive_form": config.drive_form,
            "dasher_blade_count": config.dasher_blade_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.vessel_radius_m is not None and not 0.070 <= float(config.vessel_radius_m) <= 0.150:
        raise ValueError("vessel_radius_m must be in [0.070, 0.150]")
    if config.vessel_depth_m is not None and not 0.120 <= float(config.vessel_depth_m) <= 0.320:
        raise ValueError("vessel_depth_m must be in [0.120, 0.320]")
    if config.crank_throw_m is not None and not 0.060 <= float(config.crank_throw_m) <= 0.130:
        raise ValueError("crank_throw_m must be in [0.060, 0.130]")

    radius = (
        _clamp(config.vessel_radius_m, 0.070, 0.150)
        if config.vessel_radius_m is not None
        else 0.100
    )
    depth = (
        _clamp(config.vessel_depth_m, 0.120, 0.320)
        if config.vessel_depth_m is not None
        else 0.200
    )
    throw = (
        _clamp(config.crank_throw_m, 0.060, 0.130)
        if config.crank_throw_m is not None
        else 0.090
    )

    rim = radius + WALL
    outer_x, outer_y = _VESSEL_OUTER[config.vessel_body]
    outer_x += rim
    outer_y += rim
    base_z = _BODY_LIFT[config.vessel_body]
    cavity_floor = base_z + FLOOR_T
    mouth = cavity_floor + depth
    # A hinged rim hatch sweeps up in front of the drive, so the mount has to
    # stand above that swing; a lift-off lid only needs its own travel.
    lid_r = rim - 0.002
    drive_rise = (
        DRIVE_RISE
        if config.access_form == "lift_off_lid"
        else 0.042 + math.sin(HATCH_OPEN) * lid_r
    )
    return ResolvedConfig(
        vessel_body=config.vessel_body,
        dasher_form=config.dasher_form,
        drive_mount=config.drive_mount,
        access_form=config.access_form,
        drive_form=config.drive_form,
        dasher_blade_count=int(config.dasher_blade_count),
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        vessel_radius_m=radius,
        vessel_depth_m=depth,
        crank_throw_m=throw,
        rim_radius_m=rim,
        lid_radius_m=rim - 0.002,
        outer_x_m=outer_x,
        outer_y_m=outer_y,
        mount_leg_m=max(outer_x, outer_y) + POST_OUTSET,
        blade_reach_m=radius - BLADE_GAP - SHAFT_R,
        body_base_z=base_z,
        cavity_floor_z=cavity_floor,
        mouth_z=mouth,
        drive_axis_z_m=mouth + drive_rise,
        yoke_span_m=2.0 * rim + 0.030,
        bridge_z=mouth + drive_rise,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("vessel_body", config.vessel_body),
        ("dasher_form", config.dasher_form),
        ("drive_mount", config.drive_mount),
        ("access_form", config.access_form),
        ("drive_form", config.drive_form),
        ("dasher_blade_count", config.dasher_blade_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"icm_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _cyl(z0: float, z1: float, radius: float):
    return (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, 0.5 * (z0 + z1)))
        .cylinder(height=z1 - z0, radius=radius, direct=(0.0, 0.0, 1.0))
    )


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float):
    return (
        cq.Workplane("XY")
        .transformed(offset=(0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1)))
        .box(x1 - x0, y1 - y0, z1 - z0)
    )


def _rounded_box(w: float, d: float, h: float, radius: float, z0: float):
    return (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, z0 + 0.5 * h))
        .box(w, d, h)
        .edges("|Z")
        .fillet(radius)
    )


# --- vessel body candidates ---------------------------------------------------
def _vessel_countertop_bowl_build(vessel, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Rounded appliance base with a bowl recess, seating collar and feet."""
    half = r.rim_radius_m + 0.030
    body = _rounded_box(2.0 * half, 2.0 * (r.rim_radius_m + 0.022), r.mouth_z - r.body_base_z,
                        0.018, r.body_base_z)
    # Real freezing cavity plus the recess the bowl seats into.
    body = body.cut(_cyl(r.cavity_floor_z, r.mouth_z + 0.01, r.vessel_radius_m))
    body = body.union(_cyl(r.mouth_z - 0.016, r.mouth_z, r.rim_radius_m + 0.006))
    body = body.cut(_cyl(r.mouth_z - 0.02, r.mouth_z + 0.02, r.vessel_radius_m))
    # Control-panel recess on the front face.
    body = body.cut(
        cq.Workplane("XY")
        .transformed(offset=(0.0, -(r.rim_radius_m + 0.022) + 0.004, r.body_base_z + 0.5 * (r.mouth_z - r.body_base_z)))
        .box(0.062, 0.008, 0.032)
    )
    vessel.visual(
        mesh_from_cadquery(body, "icm_countertop_body"),
        material=mats["body"],
        name="vessel_body__countertop_bowl__housing", material_class_id=("metal.paint_coated" if r.palette_style in {"cream_enamel", "stainless", "mint_appliance"} else "wood.oak"),
    )
    for index, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        vessel.visual(
            Cylinder(radius=0.011, length=r.body_base_z + 0.006),
            origin=Origin(
                xyz=(sx * (half - 0.030), sy * (r.rim_radius_m - 0.006),
                     0.5 * (r.body_base_z + 0.006)),
            ),
            material=mats["dark"],
            name=f"vessel_body__countertop_bowl__foot_{index}", material_class_id="rubber.smooth_plain",
        )


def _vessel_coopered_bucket_build(vessel, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Staved wooden churn bucket with indexed seams and steel bands."""
    outer = r.rim_radius_m + 0.024
    shell = _cyl(r.body_base_z, r.mouth_z, outer)
    shell = shell.cut(_cyl(r.cavity_floor_z, r.mouth_z + 0.01, r.vessel_radius_m))
    vessel.visual(
        mesh_from_cadquery(shell, "icm_bucket_shell"),
        material=mats["wood"],
        name="vessel_body__coopered_bucket__bucket_shell", material_class_id="wood.oak",
    )
    seam_r = outer - 0.001
    for index in range(16):
        angle = 2.0 * math.pi * index / 16.0
        vessel.visual(
            Box((0.0026, 0.0060, (r.mouth_z - r.body_base_z) * 0.92)),
            origin=Origin(
                xyz=(seam_r * math.cos(angle), seam_r * math.sin(angle),
                     0.5 * (r.body_base_z + r.mouth_z)),
                rpy=(0.0, 0.0, angle + math.pi * 0.5),
            ),
            material=mats["trim"],
            name=f"vessel_body__coopered_bucket__stave_seam_{index}", material_class_id="metal.paint_coated",
        )
    for index, frac in enumerate((0.18, 0.82)):
        band = _cyl(0.0, 0.016, outer + 0.0025).cut(_cyl(-0.01, 0.03, outer - 0.002))
        vessel.visual(
            mesh_from_cadquery(band, f"icm_bucket_band_{index}"),
            origin=Origin(
                xyz=(0.0, 0.0, r.body_base_z + frac * (r.mouth_z - r.body_base_z) - 0.008)
            ),
            material=mats["steel"],
            name=f"vessel_body__coopered_bucket__band_{index}", material_class_id="metal.stainless_matte",
        )


def _vessel_upright_tub_build(vessel, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Revolved tapered freezer pail with a sealed floor and a rolled edge."""
    foot_r = r.vessel_radius_m + 0.014
    section = [
        (0.0, r.body_base_z),
        (foot_r, r.body_base_z),
        (foot_r, r.body_base_z + 0.020),
        (r.rim_radius_m, r.mouth_z),
        (r.vessel_radius_m, r.mouth_z),
        (r.vessel_radius_m, r.cavity_floor_z),
        (0.0, r.cavity_floor_z),
    ]
    shell = (
        cq.Workplane("XZ")
        .polyline(section)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )
    vessel.visual(
        mesh_from_cadquery(shell, "icm_tub_shell"),
        material=mats["body"],
        name="vessel_body__upright_tub__tub_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"cream_enamel", "oak_and_steel", "mint_appliance"} else "metal.stainless_matte"),
    )
    roll = _cyl(r.mouth_z - 0.010, r.mouth_z, r.rim_radius_m + 0.005).cut(
        _cyl(r.mouth_z - 0.02, r.mouth_z + 0.01, r.rim_radius_m - 0.002)
    )
    vessel.visual(
        mesh_from_cadquery(roll, "icm_tub_roll"),
        material=mats["steel"],
        name="vessel_body__upright_tub__rolled_edge", material_class_id="metal.stainless_matte",
    )
    vessel.visual(
        Cylinder(radius=foot_r + 0.010, length=r.body_base_z + 0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (r.body_base_z + 0.006))),
        material=mats["trim"],
        name="vessel_body__upright_tub__foot_ring", material_class_id="metal.paint_coated",
    )


_VESSEL_BUILDERS = {
    "countertop_bowl": _vessel_countertop_bowl_build,
    "coopered_bucket": _vessel_coopered_bucket_build,
    "upright_tub": _vessel_upright_tub_build,
}


def _build_vessel(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    vessel = model.part("vessel", meta={"role": "vessel"})
    _VESSEL_BUILDERS[r.vessel_body](vessel, r, mats)
    return vessel


# --- drive mount candidates ---------------------------------------------------
def _sleeve_mesh(name: str, z0: float, z1: float):
    sleeve = _cyl(z0, z1, SLEEVE_R).cut(_cyl(z0 - 0.01, z1 + 0.01, SHAFT_R + FIT))
    return mesh_from_cadquery(sleeve, name)


def _local_origin(
    origin: Origin | None, offset: tuple[float, float, float]
) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(value - shift for value, shift in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


def _drive_mount_bridge_yoke_build(
    part, offset, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """A bored bridge plate on two rim posts, with clamp tabs on the rim."""
    post_r = r.mount_leg_m
    for index, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.026, 0.024, r.bridge_z - r.mouth_z + 0.036)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        0.0,
                        sy * post_r,
                        0.5 * (r.mouth_z - 0.026 + r.bridge_z + 0.010),
                    )
                ),
                offset,
            ),
            material=mats["steel"],
            name=f"drive_mount__bridge_yoke__post_{index}", material_class_id="metal.stainless_matte",
        )
        # The clamp tab reaches back to the vessel wall with a 0.6 mm seat.
        tab_len = post_r + 0.013 - (r.outer_y_m + SEAT)
        part.visual(
            Box((0.030, tab_len, 0.012)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        0.0,
                        sy * (r.outer_y_m + SEAT + 0.5 * tab_len),
                        r.mouth_z - 0.008,
                    )
                )
                , offset
            ),
            material=mats["trim"],
            name=f"drive_mount__bridge_yoke__clamp_tab_{index}", material_class_id="metal.paint_coated",
        )
    plate = _box(
        -0.020, 0.020, -(post_r + 0.013), post_r + 0.013, r.bridge_z - BRIDGE_T, r.bridge_z
    ).cut(_cyl(r.bridge_z - 0.05, r.bridge_z + 0.05, SLEEVE_R - 0.001))
    part.visual(
        mesh_from_cadquery(plate, "icm_yoke_bridge_plate"),
        origin=_local_origin(None, offset),
        material=mats["steel"],
        name="drive_mount__bridge_yoke__bridge_plate", material_class_id="metal.stainless_matte",
    )
    part.visual(
        _sleeve_mesh("icm_yoke_sleeve", r.bridge_z - BRIDGE_T - 0.010, r.bridge_z + 0.016),
        origin=_local_origin(None, offset),
        material=mats["steel"],
        name="drive_mount__bridge_yoke__bearing_sleeve", material_class_id="metal.stainless_matte",
    )


def _drive_mount_arch_frame_build(
    part, offset, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """Two cast shoulder plates rising from the rim to a bored gearbox block."""
    shoulder_r = r.mount_leg_m
    top_z = r.bridge_z - 0.010
    for index, sx in enumerate((-1.0, 1.0)):
        profile = [
            (sx * (r.outer_x_m + SEAT), r.mouth_z - 0.026),
            (sx * (shoulder_r + 0.012), r.mouth_z - 0.026),
            (sx * (shoulder_r + 0.006), r.mouth_z + 0.044),
            (sx * 0.024, top_z),
            (sx * 0.024, top_z - 0.020),
            (sx * (shoulder_r - 0.006), r.mouth_z + 0.040),
        ]
        plate = (
            cq.Workplane("XZ").polyline(profile).close().extrude(0.016, both=True)
        )
        part.visual(
            mesh_from_cadquery(plate, f"icm_arch_shoulder_{index}"),
            origin=_local_origin(None, offset),
            material=mats["trim"],
            name=f"drive_mount__arch_frame__shoulder_{index}", material_class_id="metal.paint_coated",
        )
        foot_len = shoulder_r + 0.012 - (r.outer_x_m + SEAT)
        part.visual(
            Box((foot_len, 0.032, 0.012)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sx * (r.outer_x_m + SEAT + 0.5 * foot_len),
                        0.0,
                        r.mouth_z - 0.008,
                    )
                ),
                offset,
            ),
            material=mats["trim"],
            name=f"drive_mount__arch_frame__clamp_foot_{index}", material_class_id="metal.paint_coated",
        )
    gearbox = _box(-0.029, 0.029, -0.019, 0.019, top_z - 0.021, top_z + 0.009).cut(
        _cyl(top_z - 0.05, top_z + 0.05, SLEEVE_R - 0.001)
    )
    part.visual(
        mesh_from_cadquery(gearbox, "icm_arch_gearbox"),
        origin=_local_origin(None, offset),
        material=mats["trim"],
        name="drive_mount__arch_frame__gearbox", material_class_id="metal.paint_coated",
    )
    part.visual(
        _sleeve_mesh("icm_arch_sleeve", top_z - 0.024, r.bridge_z + 0.016),
        origin=_local_origin(None, offset),
        material=mats["steel"],
        name="drive_mount__arch_frame__bearing_sleeve", material_class_id="metal.stainless_matte",
    )


def _drive_mount_bearing_web_build(
    part, offset, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """A low bored bearing web: one flat bridge across the mouth carrying a
    small ring on the axis, with no posts or cast shoulders at all."""
    span = r.mount_leg_m
    web = _box(-0.015, 0.015, -span, span, r.bridge_z - 0.010, r.bridge_z).cut(
        _cyl(r.bridge_z - 0.05, r.bridge_z + 0.05, SLEEVE_R - 0.001)
    )
    part.visual(
        mesh_from_cadquery(web, "icm_bearing_web_bridge"),
        origin=_local_origin(None, offset),
        material=mats["steel"],
        name="drive_mount__bearing_web__web_bridge", material_class_id="metal.stainless_matte",
    )
    for index, sy in enumerate((-1.0, 1.0)):
        tab_len = span + 0.013 - (r.outer_y_m + SEAT)
        part.visual(
            Box((0.030, tab_len, 0.012)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        0.0,
                        sy * (r.outer_y_m + SEAT + 0.5 * tab_len),
                        r.mouth_z - 0.008,
                    )
                )
                , offset
            ),
            material=mats["trim"],
            name=f"drive_mount__bearing_web__web_foot_{index}", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((0.020, 0.014, r.bridge_z - r.mouth_z + 0.002)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        0.0,
                        sy * (span - 0.007),
                        0.5 * (r.mouth_z - 0.008 + r.bridge_z),
                    )
                )
                , offset
            ),
            material=mats["steel"],
            name=f"drive_mount__bearing_web__web_leg_{index}", material_class_id="metal.stainless_matte",
        )
    part.visual(
        _sleeve_mesh("icm_web_sleeve", r.bridge_z - 0.012, r.bridge_z + 0.016),
        origin=_local_origin(None, offset),
        material=mats["steel"],
        name="drive_mount__bearing_web__bearing_sleeve", material_class_id="metal.stainless_matte",
    )


_MOUNT_BUILDERS = {
    "bridge_yoke": _drive_mount_bridge_yoke_build,
    "arch_frame": _drive_mount_arch_frame_build,
    "bearing_web": _drive_mount_bearing_web_build,
}


def _mount_offset(r: ResolvedConfig) -> tuple[float, float, float]:
    """The mount's local origin: on its own leg, beside the vessel wall."""
    if r.drive_mount == "arch_frame":
        return (r.outer_x_m + 0.004, 0.0, r.mouth_z - 0.008)
    return (0.0, r.outer_y_m + 0.004, r.mouth_z - 0.008)


def _axis_point_in_mount(r: ResolvedConfig) -> tuple[float, float, float]:
    """The vessel axis expressed in the mount's own local frame."""
    off = _mount_offset(r)
    return (-off[0], -off[1], r.drive_axis_z_m - off[2])


def _build_mount(model: ArticulatedObject, vessel, r: ResolvedConfig, mats: dict[str, str]):
    mount = model.part("drive_mount", meta={"role": "drive_mount"})
    off = _mount_offset(r)
    _MOUNT_BUILDERS[r.drive_mount](mount, off, r, mats)
    model.articulation(
        "vessel_to_drive_mount",
        ArticulationType.FIXED,
        parent=vessel,
        child=mount,
        origin=Origin(xyz=off),
    )
    return mount


# --- dasher candidates --------------------------------------------------------
def _dasher_shaft(part, r: ResolvedConfig, mats: dict[str, str], top_local: float) -> float:
    """The common shaft, authored in the dasher frame (origin on the drive axis)."""
    bottom = r.cavity_floor_z + 0.006 - r.drive_axis_z_m
    part.visual(
        Cylinder(radius=SHAFT_R, length=top_local - bottom),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (bottom + top_local))),
        material=mats["steel"],
        name="dasher__shaft", material_class_id="metal.stainless_matte",
    )
    return bottom


def _blade_zs(r: ResolvedConfig, bottom: float, top: float) -> tuple[float, ...]:
    n = r.dasher_blade_count
    span = top - bottom
    return tuple(bottom + span * (0.18 + 0.64 * i / max(1, n - 1)) for i in range(n))


def _dasher_paddle_blades_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    bottom = _dasher_shaft(part, r, mats, SHAFT_TOP_LOCAL)
    hub_top = bottom + 0.9 * (r.mouth_z - r.drive_axis_z_m - bottom)
    part.visual(
        Cylinder(radius=SHAFT_R + 0.005, length=hub_top - bottom),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (bottom + hub_top))),
        material=mats["steel"],
        name="dasher_form__paddle_blades__hub", material_class_id="metal.stainless_matte",
    )
    reach = r.blade_reach_m
    offset = SHAFT_R + 0.5 * reach
    for index, z in enumerate(_blade_zs(r, bottom, hub_top)):
        yaw = 2.0 * math.pi * index / r.dasher_blade_count
        part.visual(
            Box((reach, 0.010, 0.030)),
            origin=Origin(
                xyz=(offset * math.cos(yaw), offset * math.sin(yaw), z), rpy=(0.0, 0.0, yaw)
            ),
            material=mats["dark"],
            name=f"dasher_form__paddle_blades__paddle_{index}", material_class_id="plastic.opaque_generic",
        )


def _dasher_scraper_bars_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    bottom = _dasher_shaft(part, r, mats, SHAFT_TOP_LOCAL)
    top = r.mouth_z - r.drive_axis_z_m - 0.020
    part.visual(
        Cylinder(radius=SHAFT_R + 0.003, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, SHAFT_TOP_LOCAL - 0.004)),
        material=mats["steel"],
        name="dasher_form__scraper_bars__thrust_collar", material_class_id="metal.stainless_matte",
    )
    width = 2.0 * (SHAFT_R + r.blade_reach_m)
    for index, z in enumerate(_blade_zs(r, bottom, top)):
        yaw = math.pi * index / max(1, r.dasher_blade_count)
        part.visual(
            Box((width, 0.012, 0.026)),
            origin=Origin(xyz=(0.0, 0.0, z), rpy=(0.0, 0.0, yaw)),
            material=mats["dark"],
            name=f"dasher_form__scraper_bars__bar_{index}", material_class_id="plastic.opaque_generic",
        )


def _dasher_radial_plates_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    bottom = _dasher_shaft(part, r, mats, SHAFT_TOP_LOCAL)
    top = r.mouth_z - r.drive_axis_z_m - 0.024
    part.visual(
        Cylinder(radius=SHAFT_R + 0.004, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, bottom + 0.008)),
        material=mats["steel"],
        name="dasher_form__radial_plates__bearing_collar", material_class_id="metal.stainless_matte",
    )
    reach = r.blade_reach_m
    offset = SHAFT_R + 0.5 * reach
    height = (top - bottom) * 0.82
    for index in range(r.dasher_blade_count):
        yaw = 2.0 * math.pi * index / r.dasher_blade_count
        part.visual(
            Box((reach, 0.004, height)),
            origin=Origin(
                xyz=(
                    offset * math.cos(yaw),
                    offset * math.sin(yaw),
                    bottom + 0.010 + 0.5 * height,
                ),
                rpy=(0.0, 0.0, yaw),
            ),
            material=mats["dark"],
            name=f"dasher_form__radial_plates__plate_{index}", material_class_id="plastic.opaque_generic",
        )


_DASHER_BUILDERS = {
    "paddle_blades": _dasher_paddle_blades_build,
    "scraper_bars": _dasher_scraper_bars_build,
    "radial_plates": _dasher_radial_plates_build,
}


def _axis_joint(model, *, name, parent, child, point, mimic=None, meta=None) -> None:
    provider = AxisInterface(
        name=f"{name}__provider", point=point, axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    consumer = AxisInterface(
        name=f"{name}__consumer", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.CONTINUOUS,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=45.0, velocity=3.0),
        mimic=mimic,
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


def _build_dasher(model, mount, r: ResolvedConfig, mats: dict[str, str]):
    dasher = model.part("dasher", meta={"role": "dasher"})
    _DASHER_BUILDERS[r.dasher_form](dasher, r, mats)
    _axis_joint(
        model,
        name="drive_mount_to_dasher",
        parent=mount,
        child=dasher,
        point=_axis_point_in_mount(r),
        mimic=Mimic(joint="drive_mount_to_drive", multiplier=1.0, offset=0.0),
    )
    return dasher


# --- drive candidates ---------------------------------------------------------
def _drive_hand_crank_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    part.visual(
        Cylinder(radius=SHAFT_R + 0.004, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, SLEEVE_TOP_LOCAL + 0.010)),
        material=mats["steel"],
        name="drive_form__hand_crank__hub", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Box((r.crank_throw_m, 0.014, 0.010)),
        origin=Origin(xyz=(0.5 * r.crank_throw_m - 0.004, 0.0, SLEEVE_TOP_LOCAL + 0.022)),
        material=mats["steel"],
        name="drive_form__hand_crank__crank_arm", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=0.008, length=0.052),
        origin=Origin(xyz=(r.crank_throw_m - 0.008, 0.0, SLEEVE_TOP_LOCAL + 0.046)),
        material=mats["wood"],
        name="drive_form__hand_crank__grip", material_class_id="wood.polished_varnished",
    )


def _drive_motor_pod_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    pod_r = 0.020 + 0.16 * r.crank_throw_m
    pod = _cyl(SLEEVE_TOP_LOCAL + 0.006, SLEEVE_TOP_LOCAL + 0.061, pod_r)
    for i in range(4):
        pod = pod.cut(
            cq.Workplane("XY")
            .transformed(offset=(0.0, pod_r - 0.003, SLEEVE_TOP_LOCAL + 0.018 + i * 0.010))
            .box(2.0 * pod_r * 0.7, 0.012, 0.004)
        )
    part.visual(
        mesh_from_cadquery(pod, "icm_motor_pod"),
        material=mats["body"],
        name="drive_form__motor_pod__pod", material_class_id=("metal.paint_coated" if r.palette_style in {"cream_enamel", "oak_and_steel", "mint_appliance"} else "metal.stainless_matte"),
    )
    part.visual(
        Cylinder(radius=SHAFT_R + 0.006, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, SLEEVE_TOP_LOCAL + 0.010)),
        material=mats["steel"],
        name="drive_form__motor_pod__coupling_collar", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=pod_r * 0.55, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, SLEEVE_TOP_LOCAL + 0.064)),
        material=mats["accent"],
        name="drive_form__motor_pod__cap", material_class_id="plastic.opaque_glossy_molded",
    )


_DRIVE_BUILDERS = {
    "hand_crank": _drive_hand_crank_build,
    "motor_pod": _drive_motor_pod_build,
}


def _build_drive(model, mount, r: ResolvedConfig, mats: dict[str, str]):
    drive = model.part("drive", meta={"role": "drive"})
    drive.visual(
        Cylinder(radius=SHAFT_R, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material=mats["steel"],
        name="drive__spindle", material_class_id="metal.stainless_matte",
    )
    _DRIVE_BUILDERS[r.drive_form](drive, r, mats)
    _axis_joint(
        model,
        name="drive_mount_to_drive",
        parent=mount,
        child=drive,
        point=_axis_point_in_mount(r),
        meta={"positive_motion": "turns the dasher through the freezing charge"},
    )
    return drive


# --- access candidates --------------------------------------------------------
def _lid_mesh(r: ResolvedConfig, name: str):
    disc = _cyl(0.0, LID_T, r.lid_radius_m)
    skirt = _cyl(-0.010, 0.0, r.vessel_radius_m - FIT).cut(
        _cyl(-0.03, 0.01, r.vessel_radius_m - 0.008)
    )
    lid = disc.union(skirt)
    lid = lid.union(_cyl(LID_T, LID_T + 0.012, SHAFT_R + FIT + 0.008))
    lid = lid.cut(_cyl(-0.03, 0.05, SHAFT_R + FIT))
    return mesh_from_cadquery(lid, name)


def _build_access(model, vessel, r: ResolvedConfig, mats: dict[str, str]):
    lid = model.part("access_lid", meta={"role": "access_lid"})
    if r.access_form == "lift_off_lid":
        off = (0.0, 0.0, r.mouth_z)
        lid.visual(
            _lid_mesh(r, "icm_lift_off_lid"),
            material=mats["steel"],
            name="access_form__lift_off_lid__lid_disc", material_class_id="metal.stainless_matte",
        )
        lid.visual(
            Box((0.030, 0.008, 0.012)),
            origin=Origin(xyz=(0.0, r.lid_radius_m - 0.018, LID_T + 0.006)),
            material=mats["trim"],
            name="access_form__lift_off_lid__lift_tab", material_class_id="metal.paint_coated",
        )
        model.articulation(
            "vessel_to_access_lid",
            ArticulationType.PRISMATIC,
            parent=vessel,
            child=lid,
            origin=Origin(xyz=off),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=20.0, velocity=0.15, lower=0.0, upper=LID_TRAVEL),
            meta={"positive_motion": "lifts the lid off the rim"},
        )
    else:
        # The hinge sits on the free azimuth: the yoke stands its legs on y, the
        # arch stands its shoulders on x, so the cap swings on the other one.
        # Only the cast arch stands its legs on x; the yoke and the web both
        # use y, so the hatch takes whichever azimuth is left free.
        if r.drive_mount == "arch_frame":
            u = (0.0, 1.0, 0.0)
            w = (-1.0, 0.0, 0.0)
            reach = r.outer_y_m
        else:
            u = (1.0, 0.0, 0.0)
            w = (0.0, 1.0, 0.0)
            reach = r.outer_x_m
        hinge_r = reach + 0.008
        off = (hinge_r * u[0], hinge_r * u[1], r.mouth_z + 0.006)
        # The vessel carries a fixed cover over the inner half of the mouth and
        # the lower half of the hinge, so the hatch keeps real contact with the
        # grounded body at every opening angle and never sweeps over the axis.
        hinge_r = reach + 0.008
        hinge_z = r.mouth_z + 0.014
        off = (hinge_r * u[0], hinge_r * u[1], hinge_z)

        def _outer_half(z0: float, z1: float):
            if u[0] > 0.5:
                return _box(0.010, 1.0, -1.0, 1.0, z0, z1)
            return _box(-1.0, 1.0, 0.010, 1.0, z0, z1)

        cover = _cyl(r.mouth_z - 0.002, r.mouth_z + 0.008, r.lid_radius_m)
        cover = cover.cut(_cyl(r.mouth_z - 0.02, r.mouth_z + 0.05, SHAFT_R + FIT))
        cover = cover.cut(_outer_half(r.mouth_z - 0.02, r.mouth_z + 0.05))
        vessel.visual(
            mesh_from_cadquery(cover, "icm_fixed_cover"),
            material=mats["steel"],
            name="access_form__hinged_cap__fixed_cover", material_class_id="metal.stainless_matte",
        )
        bracket_len = hinge_r + 0.006 - (reach - 0.006)
        bracket_c = reach - 0.006 + 0.5 * bracket_len
        vessel.visual(
            Box(
                (bracket_len, 0.070, 0.012)
                if u[0] > 0.5
                else (0.070, bracket_len, 0.012)
            ),
            origin=Origin(xyz=(u[0] * bracket_c, u[1] * bracket_c, r.mouth_z - 0.004)),
            material=mats["trim"],
            name="access_form__hinged_cap__hinge_bracket", material_class_id="metal.paint_coated",
        )
        for knuckle, sk in enumerate((-1.0, 1.0)):
            vessel.visual(
                Cylinder(radius=0.020, length=0.012),
                origin=Origin(
                    xyz=(
                        off[0] + sk * 0.0266 * w[0],
                        off[1] + sk * 0.0266 * w[1],
                        off[2],
                    ),
                    rpy=(math.pi / 2.0, 0.0, 0.0)
                    if abs(w[1]) > 0.5
                    else (0.0, math.pi / 2.0, 0.0),
                ),
                material=mats["trim"],
                name=f"access_form__hinged_cap__hinge_knuckle_{knuckle}", material_class_id="metal.paint_coated",
            )

        # Authored with the hatch on local -x and the hinge axis on local +y;
        # local +x maps to the outward radial direction of the hinge.
        hatch = _cyl(hinge_z - 0.005, hinge_z + 0.005, r.lid_radius_m).translate(
            (-hinge_r, 0.0, 0.0)
        )
        hatch = hatch.intersect(
            _box(0.010 - hinge_r, 1.0, -1.0, 1.0, hinge_z - 0.05, hinge_z + 0.05)
        )
        hatch = hatch.translate((0.0, 0.0, -hinge_z))
        lid.visual(
            mesh_from_cadquery(hatch, "icm_hinged_hatch"),
            material=mats["steel"],
            name="access_form__hinged_cap__cap_disc", material_class_id="metal.stainless_matte",
        )
        # The strap carries the hatch back to the hinge barrel: the hatch edge
        # stops one rim offset short of the hinge line.
        strap_x0 = r.lid_radius_m - hinge_r
        lid.visual(
            Box((0.012 - strap_x0, 0.030, 0.010)),
            origin=Origin(xyz=(0.5 * (strap_x0 - 0.004 + 0.008), 0.0, 0.0)),
            material=mats["trim"],
            name="access_form__hinged_cap__hinge_strap", material_class_id="metal.paint_coated",
        )
        lid.visual(
            Cylinder(radius=0.008, length=0.040),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["trim"],
            name="access_form__hinged_cap__hinge_barrel", material_class_id="metal.paint_coated",
        )
        provider = AxisInterface(
            name="vessel_to_access_lid__provider",
            point=off,
            axis=w,
            radial=(-u[0], -u[1], 0.0),
        )
        consumer = AxisInterface(
            name="vessel_to_access_lid__consumer",
            axis=(0.0, 1.0, 0.0),
            radial=(-1.0, 0.0, 0.0),
        )
        mate = mate_axes(provider, consumer)
        model.articulation(
            "vessel_to_access_lid",
            ArticulationType.REVOLUTE,
            parent=vessel,
            child=lid,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=20.0, velocity=1.5, lower=0.0, upper=HATCH_OPEN),
            meta={"positive_motion": "swings the rim hatch up off the mouth"},
        )
        register_interface_mate(model, "vessel_to_access_lid", mate)
    return lid


# --- assembly -----------------------------------------------------------------
def build_picturex_0611_ice_crream_machine(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Ice_crream_machine",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "wall-scraping dasher turning in a freezing vessel",
        },
    )
    mats = _materials(model, r)
    vessel = _build_vessel(model, r, mats)
    mount = _build_mount(model, vessel, r, mats)
    _build_drive(model, mount, r, mats)
    _build_dasher(model, mount, r, mats)
    _build_access(model, vessel, r, mats)

    lid_open = LID_TRAVEL if r.access_form == "lift_off_lid" else HATCH_OPEN
    model.meta["risk_poses"] = (
        {"drive_mount_to_drive": 0.0, "vessel_to_access_lid": 0.0},
        {"drive_mount_to_drive": math.pi, "vessel_to_access_lid": lid_open},
        {"drive_mount_to_drive": math.pi / 2.0, "vessel_to_access_lid": lid_open},
    )
    model.meta["coupled_joint_pairs"] = (("drive_mount_to_drive", "vessel_to_access_lid"),)
    return model


def build_seeded_picturex_0611_ice_crream_machine(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_ice_crream_machine(config_from_seed(seed), assets=assets)


# --- authored tests -----------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_ice_crream_machine_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    vessels = _parts_by_role(model, "vessel")
    dashers = _parts_by_role(model, "dasher")
    lids = _parts_by_role(model, "access_lid")
    drives = _parts_by_role(model, "drive")
    mounts = _parts_by_role(model, "drive_mount")
    joints = {j.name: j for j in model.articulations}

    def _is_cont_z(name: str) -> bool:
        j = joints.get(name)
        return (
            j is not None
            and j.articulation_type == ArticulationType.CONTINUOUS
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 0.0, 1.0)
        )

    ctx.check(
        "category_anchor: batch freezer vessel, dasher and drive chain",
        len(vessels) == 1
        and len(dashers) == 1
        and len(lids) == 1
        and len(drives) == 1
        and len(mounts) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "vessel"
        and joints["vessel_to_drive_mount"].articulation_type == ArticulationType.FIXED
        and _is_cont_z("drive_mount_to_drive")
        and _is_cont_z("drive_mount_to_dasher")
        and joints["drive_mount_to_dasher"].mimic is not None
        and joints["drive_mount_to_dasher"].mimic.joint == "drive_mount_to_drive"
        and joints["vessel_to_access_lid"].parent == "vessel",
        details=(
            f"vessels={len(vessels)} dashers={len(dashers)} lids={len(lids)} "
            f"drives={len(drives)} mounts={len(mounts)} joints={sorted(joints)}"
        ),
    )

    ctx.check(
        "category_anchor: the dasher scrapes the wall without cutting it",
        0.0 < FIT <= 0.001
        and abs(r.blade_reach_m - (r.vessel_radius_m - BLADE_GAP - SHAFT_R)) < 1e-9
        and r.blade_reach_m > 0.020
        and SHAFT_R + r.blade_reach_m < r.vessel_radius_m
        and r.rim_radius_m == r.vessel_radius_m + WALL
        and abs((r.mouth_z - r.cavity_floor_z) - r.vessel_depth_m) < 1e-9
        and r.drive_axis_z_m > r.mouth_z + LID_TRAVEL,
        details=(
            f"reach={r.blade_reach_m} radius={r.vessel_radius_m} depth={r.vessel_depth_m} "
            f"mouth={r.mouth_z} drive_z={r.drive_axis_z_m}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    vessel_ok = {
        "countertop_bowl": any("countertop_bowl__housing" in n for n in visual_names)
        and sum(1 for n in visual_names if "countertop_bowl__foot" in n) == 4,
        "coopered_bucket": sum(1 for n in visual_names if "coopered_bucket__stave_seam" in n) == 16
        and sum(1 for n in visual_names if "coopered_bucket__band" in n) == 2,
        "upright_tub": any("upright_tub__tub_shell" in n for n in visual_names)
        and any("upright_tub__rolled_edge" in n for n in visual_names),
    }[r.vessel_body]
    ctx.check(
        "category_anchor: vessel_body identity", vessel_ok, details=f"vessel_body={r.vessel_body}"
    )

    dasher_ok = {
        "paddle_blades": sum(1 for n in visual_names if "paddle_blades__paddle_" in n)
        == r.dasher_blade_count
        and any("paddle_blades__hub" in n for n in visual_names),
        "scraper_bars": sum(1 for n in visual_names if "scraper_bars__bar_" in n)
        == r.dasher_blade_count
        and any("scraper_bars__thrust_collar" in n for n in visual_names),
        "radial_plates": sum(1 for n in visual_names if "radial_plates__plate_" in n)
        == r.dasher_blade_count
        and any("radial_plates__bearing_collar" in n for n in visual_names),
    }[r.dasher_form]
    ctx.check(
        "category_anchor: dasher_form identity",
        dasher_ok,
        details=f"dasher_form={r.dasher_form} n={r.dasher_blade_count}",
    )

    mount_ok = {
        "bridge_yoke": sum(1 for n in visual_names if "bridge_yoke__post" in n) == 2
        and any("bridge_yoke__bearing_sleeve" in n for n in visual_names),
        "arch_frame": sum(1 for n in visual_names if "arch_frame__shoulder" in n) == 2
        and any("arch_frame__gearbox" in n for n in visual_names),
        "bearing_web": any("bearing_web__web_bridge" in n for n in visual_names)
        and sum(1 for n in visual_names if "bearing_web__web_leg" in n) == 2
        and sum(1 for n in visual_names if "bearing_web__web_foot" in n) == 2,
    }[r.drive_mount]
    ctx.check(
        "category_anchor: drive_mount identity", mount_ok, details=f"drive_mount={r.drive_mount}"
    )

    access_ok = {
        "lift_off_lid": joints["vessel_to_access_lid"].articulation_type
        == ArticulationType.PRISMATIC
        and any("lift_off_lid__lift_tab" in n for n in visual_names),
        "hinged_cap": joints["vessel_to_access_lid"].articulation_type
        == ArticulationType.REVOLUTE
        and any("hinged_cap__hinge_barrel" in n for n in visual_names)
        and sum(1 for n in visual_names if "hinged_cap__hinge_knuckle" in n) == 2
        and any("hinged_cap__fixed_cover" in n for n in visual_names),
    }[r.access_form]
    ctx.check(
        "category_anchor: access_form identity", access_ok, details=f"access_form={r.access_form}"
    )

    drive_ok = {
        "hand_crank": any("hand_crank__grip" in n for n in visual_names)
        and any("hand_crank__crank_arm" in n for n in visual_names),
        "motor_pod": any("motor_pod__pod" in n for n in visual_names)
        and any("motor_pod__coupling_collar" in n for n in visual_names),
    }[r.drive_form]
    ctx.check(
        "category_anchor: drive_form identity", drive_ok, details=f"drive_form={r.drive_form}"
    )

    # Motion evidence: turning the drive turns the dasher with it.
    drive_joint = joints["drive_mount_to_drive"]
    rest = ctx.part_world_aabb(dashers[0])
    # A quarter turn is the worst case for every admissible blade count: a bar,
    # a tripod and a cross all present a clearly different footprint at 45 deg.
    with ctx.pose({drive_joint: math.pi / 4.0}):
        turned = ctx.part_world_aabb(dashers[0])
    ctx.check(
        "the drive turns the dasher on the vessel axis",
        rest is not None
        and turned is not None
        and abs(turned[0][2] - rest[0][2]) < 1e-6
        and abs(turned[1][0] - rest[1][0]) + abs(turned[1][1] - rest[1][1]) > 1e-4,
        details=f"rest={rest} turned={turned}",
    )

    # Motion evidence: the access really opens the vessel mouth.
    lid_joint = joints["vessel_to_access_lid"]
    closed = ctx.part_world_aabb(lids[0])
    target = LID_TRAVEL if r.access_form == "lift_off_lid" else HATCH_OPEN
    with ctx.pose({lid_joint: target}):
        opened = ctx.part_world_aabb(lids[0])
    ctx.check(
        "the access clears the vessel mouth when opened",
        closed is not None
        and opened is not None
        and (
            opened[0][2] > closed[0][2] + 0.020
            if r.access_form == "lift_off_lid"
            else opened[1][2] > closed[1][2] + 0.4 * r.vessel_radius_m
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
        "min_vessel_two_blades_countertop_motor",
        {
            "vessel_body": "countertop_bowl",
            "dasher_form": "paddle_blades",
            "drive_mount": "bridge_yoke",
            "access_form": "lift_off_lid",
            "drive_form": "motor_pod",
            "dasher_blade_count": 2,
            "vessel_radius_m": 0.070,
            "vessel_depth_m": 0.120,
            "crank_throw_m": 0.060,
        },
        reason="smallest, shallowest cavity with the fewest blades — tightest blade clearance",
    ),
    corner_case(
        "max_vessel_four_blades_bucket_crank",
        {
            "vessel_body": "coopered_bucket",
            "dasher_form": "scraper_bars",
            "drive_mount": "arch_frame",
            "access_form": "hinged_cap",
            "drive_form": "hand_crank",
            "dasher_blade_count": 4,
            "vessel_radius_m": 0.150,
            "vessel_depth_m": 0.320,
            "crank_throw_m": 0.130,
        },
        reason="largest cavity, most full-width bars and the longest crank on the cast arch",
    ),
    corner_case(
        "narrow_deep_tub_radial_plates",
        {
            "vessel_body": "upright_tub",
            "dasher_form": "radial_plates",
            "drive_mount": "arch_frame",
            "access_form": "lift_off_lid",
            "drive_form": "hand_crank",
            "dasher_blade_count": 4,
            "vessel_radius_m": 0.070,
            "vessel_depth_m": 0.320,
            "crank_throw_m": 0.130,
        },
        reason="narrowest but deepest pail with four full-height plates — the longest slender dasher",
    ),
    corner_case(
        "wide_shallow_bucket_hinged_motor",
        {
            "vessel_body": "coopered_bucket",
            "dasher_form": "radial_plates",
            "drive_mount": "bearing_web",
            "access_form": "hinged_cap",
            "drive_form": "motor_pod",
            "dasher_blade_count": 2,
            "vessel_radius_m": 0.150,
            "vessel_depth_m": 0.120,
            "crank_throw_m": 0.060,
        },
        reason="widest, shallowest vessel with the largest hinged cap swing",
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
    "build_picturex_0611_ice_crream_machine",
    "build_seeded_picturex_0611_ice_crream_machine",
    "run_picturex_0611_ice_crream_machine_tests",
]
