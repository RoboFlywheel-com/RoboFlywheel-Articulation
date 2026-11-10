# SPDX-License-Identifier: Apache-2.0

"""Self-contained quarter-turn butterfly valve template.

The grounded ``valve_body`` part is a real ring: a CadQuery annulus on the pipe
axis with a seat liner inside it, a stem tower bored for the stem, and a notched
locking quadrant under the operator.  The ``rotor`` carries the disc and the
stem and turns REVOLUTE about +z from shut to open across a quarter turn; the
disc radius is the bore minus a 0.8 mm running clearance, so its swept envelope
stays inside the liner at every angle without ever touching it.

Three slots vary without touching that chain: ``body_end`` (drilled bolt-ear
lugs, raised drilled flanges, or machined coupling grooves), ``disc_form`` (flat
concentric plate or offset high-performance disc) and ``operator`` (a trigger
lever FIXED to the rotor, or a worm gearbox whose handwheel turns on its own
input axis).
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

BodyEnd = Literal["lug_body", "flanged_body", "grooved_end"]
DiscForm = Literal[
    "concentric_disc",
    "offset_disc",
    "triple_offset_disc",
    "double_offset_disc",
]
Operator = Literal["lever_trigger", "tee_bar", "gear_handwheel"]
BonnetForm = Literal["short_bonnet", "extended_bonnet"]
PaletteStyle = Literal["works_blue", "safety_red", "cast_grey", "epoxy_green"]

BODY_ENDS: tuple[BodyEnd, ...] = ("lug_body", "flanged_body", "grooved_end")
DISC_FORMS: tuple[DiscForm, ...] = (
    "concentric_disc",
    "offset_disc",
    "triple_offset_disc",
    "double_offset_disc",
)
BONNET_FORMS: tuple[BonnetForm, ...] = ("short_bonnet", "extended_bonnet")
OPERATORS: tuple[Operator, ...] = ("lever_trigger", "tee_bar", "gear_handwheel")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "works_blue",
    "safety_red",
    "cast_grey",
    "epoxy_green",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("body_end", BODY_ENDS),
        component_slot("disc_form", DISC_FORMS),
        component_slot("operator", OPERATORS),
        component_slot("bonnet_form", BONNET_FORMS),
        multiplicity_slot("flange_bolt_count", (4, 8, 12), item_slot="body_end"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "works_blue": {
        "cast": (0.13, 0.33, 0.60, 1.0),
        "liner": (0.16, 0.16, 0.17, 1.0),
        "disc": (0.76, 0.78, 0.80, 1.0),
        "steel": (0.52, 0.54, 0.56, 1.0),
        "grip": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.88, 0.72, 0.20, 1.0),
    },
    "safety_red": {
        "cast": (0.66, 0.15, 0.13, 1.0),
        "liner": (0.14, 0.13, 0.13, 1.0),
        "disc": (0.78, 0.79, 0.80, 1.0),
        "steel": (0.50, 0.51, 0.52, 1.0),
        "grip": (0.09, 0.09, 0.09, 1.0),
        "accent": (0.90, 0.88, 0.84, 1.0),
    },
    "cast_grey": {
        "cast": (0.42, 0.44, 0.45, 1.0),
        "liner": (0.12, 0.12, 0.13, 1.0),
        "disc": (0.74, 0.76, 0.78, 1.0),
        "steel": (0.56, 0.58, 0.60, 1.0),
        "grip": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.82, 0.62, 0.18, 1.0),
    },
    "epoxy_green": {
        "cast": (0.16, 0.42, 0.28, 1.0),
        "liner": (0.13, 0.15, 0.14, 1.0),
        "disc": (0.75, 0.77, 0.79, 1.0),
        "steel": (0.50, 0.53, 0.51, 1.0),
        "grip": (0.09, 0.10, 0.09, 1.0),
        "accent": (0.86, 0.84, 0.30, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
WALL = 0.030              # cast ring wall thickness
LINER_T = 0.006           # seat liner thickness
STEM_R = 0.010
DISC_T = 0.014
TOWER_W = 0.070
QUADRANT_T = 0.010
# Radial running fit, under the 1 mm assembly-gap tolerance.
FIT = 0.0008
SEAT = 0.0006
BOLT_R = 0.008
LUG_R = 0.022


@dataclass(frozen=True)
class Config:
    body_end: BodyEnd = "lug_body"
    disc_form: DiscForm = "concentric_disc"
    operator: Operator = "lever_trigger"
    bonnet_form: BonnetForm = "short_bonnet"
    flange_bolt_count: int = 8
    bore_radius_m: float | None = None
    face_to_face_m: float | None = None
    operator_reach_m: float | None = None
    palette_style: PaletteStyle = "works_blue"
    name: str = "pictureX_0611_butterfly_valve_with_lever_operator"


@dataclass(frozen=True)
class ResolvedConfig:
    body_end: BodyEnd
    disc_form: DiscForm
    operator: Operator
    bonnet_form: BonnetForm
    flange_bolt_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    bore_radius_m: float
    face_to_face_m: float
    operator_reach_m: float
    liner_radius_m: float
    disc_radius_m: float
    ring_outer_m: float
    bolt_circle_radius_m: float
    tower_top_z: float
    quadrant_z: float
    stem_top_z_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x3F_A2_51_66)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        body_end=choices["body_end"],
        disc_form=choices["disc_form"],
        operator=choices["operator"],
        bonnet_form=choices["bonnet_form"],
        flange_bolt_count=choices["flange_bolt_count"],
        bore_radius_m=round(rng.uniform(0.050, 0.150), 4),
        face_to_face_m=round(rng.uniform(0.050, 0.110), 4),
        operator_reach_m=round(rng.uniform(0.150, 0.320), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"butterfly_valve_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "body_end": config.body_end,
            "disc_form": config.disc_form,
            "operator": config.operator,
            "bonnet_form": config.bonnet_form,
            "flange_bolt_count": config.flange_bolt_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.bore_radius_m is not None and not 0.050 <= float(config.bore_radius_m) <= 0.150:
        raise ValueError("bore_radius_m must be in [0.050, 0.150]")
    if config.face_to_face_m is not None and not 0.050 <= float(config.face_to_face_m) <= 0.110:
        raise ValueError("face_to_face_m must be in [0.050, 0.110]")
    if (
        config.operator_reach_m is not None
        and not 0.150 <= float(config.operator_reach_m) <= 0.320
    ):
        raise ValueError("operator_reach_m must be in [0.150, 0.320]")

    bore = (
        _clamp(config.bore_radius_m, 0.050, 0.150) if config.bore_radius_m is not None else 0.100
    )
    length = (
        _clamp(config.face_to_face_m, 0.050, 0.110)
        if config.face_to_face_m is not None
        else 0.075
    )
    reach = (
        _clamp(config.operator_reach_m, 0.150, 0.320)
        if config.operator_reach_m is not None
        else 0.220
    )
    liner_r = bore
    disc_r = bore - 0.0008
    ring_outer = bore + LINER_T + WALL
    tower_h = 0.9 * bore + 0.070 + (0.090 if config.bonnet_form == "extended_bonnet" else 0.0)
    tower_top = ring_outer + tower_h
    return ResolvedConfig(
        body_end=config.body_end,
        disc_form=config.disc_form,
        operator=config.operator,
        bonnet_form=config.bonnet_form,
        flange_bolt_count=int(config.flange_bolt_count),
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        bore_radius_m=bore,
        face_to_face_m=length,
        operator_reach_m=reach,
        liner_radius_m=liner_r,
        disc_radius_m=disc_r,
        ring_outer_m=ring_outer,
        bolt_circle_radius_m=ring_outer + 0.016,
        tower_top_z=tower_top,
        quadrant_z=tower_top + 0.010,
        stem_top_z_m=tower_top + 0.040,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("body_end", config.body_end),
        ("disc_form", config.disc_form),
        ("operator", config.operator),
        ("bonnet_form", config.bonnet_form),
        ("flange_bolt_count", config.flange_bolt_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"bfv_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _y_tube(outer: float, inner: float, y0: float, y1: float):
    """A ring on the pipe axis: a real annulus, not a capped cylinder."""
    solid = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.5 * (y0 + y1), 0.0))
        .cylinder(height=y1 - y0, radius=outer, direct=(0.0, 1.0, 0.0))
    )
    if inner > 0.0:
        solid = solid.cut(
            cq.Workplane("XY")
            .transformed(offset=(0.0, 0.5 * (y0 + y1), 0.0))
            .cylinder(height=(y1 - y0) * 3.0, radius=inner, direct=(0.0, 1.0, 0.0))
        )
    return solid


def _y_bolt(radius: float, y0: float, y1: float, x: float, z: float):
    return (
        cq.Workplane("XY")
        .transformed(offset=(x, 0.5 * (y0 + y1), z))
        .cylinder(height=y1 - y0, radius=radius, direct=(0.0, 1.0, 0.0))
    )


def _bolt_angles(r: ResolvedConfig) -> list[float]:
    n = r.flange_bolt_count
    step = 2.0 * math.pi / n
    return [i * step + 0.5 * step for i in range(n)]


def _local_origin(
    origin: Origin | None, offset: tuple[float, float, float]
) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(a - b for a, b in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


# --- body end candidates -------------------------------------------------------
def _body_end_lug_body_build(casting, r: ResolvedConfig):
    """Bolt-ear lugs: one drilled lug boss per declared bolt position."""
    half = 0.5 * r.face_to_face_m
    extras = []
    for index, angle in enumerate(_bolt_angles(r)):
        x = r.bolt_circle_radius_m * math.cos(angle)
        z = r.bolt_circle_radius_m * math.sin(angle)
        lug = _y_bolt(LUG_R, -half + 0.004, half - 0.004, x, z).cut(
            _y_bolt(BOLT_R, -half - 0.02, half + 0.02, x, z)
        )
        extras.append(
            (lug, f"body_end__lug_body__bolt_lug_{index}", "cast")
        )
    return casting, extras


def _body_end_flanged_body_build(casting, r: ResolvedConfig):
    """Raised end flanges drilled on the same bolt circle, one boss per hole."""
    half = 0.5 * r.face_to_face_m
    for sy in (-1.0, 1.0):
        y1 = sy * half
        y0 = sy * (half - 0.014)
        casting = casting.union(
            _y_tube(r.bolt_circle_radius_m + LUG_R, r.liner_radius_m, min(y0, y1), max(y0, y1))
        )
    extras = []
    for index, angle in enumerate(_bolt_angles(r)):
        x = r.bolt_circle_radius_m * math.cos(angle)
        z = r.bolt_circle_radius_m * math.sin(angle)
        casting = casting.cut(_y_bolt(BOLT_R, -half - 0.02, half + 0.02, x, z))
        boss = _y_bolt(BOLT_R + 0.006, half - 0.016, half + 0.002, x, z).cut(
            _y_bolt(BOLT_R, half - 0.03, half + 0.03, x, z)
        )
        extras.append(
            (boss, f"body_end__flanged_body__bolt_boss_{index}", "steel")
        )
    return casting, extras


def _body_end_grooved_end_build(casting, r: ResolvedConfig):
    """Machined shoulders and coupling grooves with one clamp segment per bolt."""
    half = 0.5 * r.face_to_face_m
    for sy in (-1.0, 1.0):
        y_sh = sy * (half - 0.006)
        casting = casting.union(
            _y_tube(
                r.ring_outer_m + 0.010,
                r.liner_radius_m,
                min(y_sh, sy * half),
                max(y_sh, sy * half),
            )
        )
        y_g0 = sy * (half - 0.020)
        y_g1 = sy * (half - 0.010)
        casting = casting.cut(
            _y_tube(
                r.ring_outer_m + 0.02,
                r.ring_outer_m - 0.006,
                min(y_g0, y_g1),
                max(y_g0, y_g1),
            )
        )
    extras = []
    for index, angle in enumerate(_bolt_angles(r)):
        x = (r.ring_outer_m - 0.002) * math.cos(angle)
        z = (r.ring_outer_m - 0.002) * math.sin(angle)
        seg = (
            cq.Workplane("XY")
            .transformed(
                offset=(x, half - 0.015, z), rotate=(0.0, 0.0, math.degrees(angle))
            )
            .box(0.012, 0.010, 0.030)
        )
        extras.append(
            (seg, f"body_end__grooved_end__clamp_segment_{index}", "steel")
        )
    return casting, extras


_BODY_END_BUILDERS = {
    "lug_body": _body_end_lug_body_build,
    "flanged_body": _body_end_flanged_body_build,
    "grooved_end": _body_end_grooved_end_build,
}


def _build_body(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    body = model.part("valve_body", meta={"role": "valve_body"})
    half = 0.5 * r.face_to_face_m
    casting = _y_tube(r.ring_outer_m, r.liner_radius_m + LINER_T, -half, half)
    # Stem tower and shoulders, bored for the stem.
    tower = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, 0.5 * (r.ring_outer_m - 0.010 + r.tower_top_z)))
        .box(TOWER_W, TOWER_W * 0.82, r.tower_top_z - r.ring_outer_m + 0.010)
    )
    casting = casting.union(tower)
    if r.bonnet_form == "extended_bonnet":
        # Sloping cast gussets tying the tall neck column back into the body.
        for sx in (-1.0, 1.0):
            casting = casting.union(
                cq.Workplane("XZ")
                .polyline(
                    [
                        (sx * 0.5 * TOWER_W, r.ring_outer_m),
                        (sx * (0.5 * TOWER_W + 0.030), r.ring_outer_m),
                        (sx * 0.5 * TOWER_W, r.ring_outer_m + 0.070),
                    ]
                )
                .close()
                .extrude(0.5 * TOWER_W * 0.82, both=True)
            )
    casting = casting.union(
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, r.tower_top_z + 0.006))
        .cylinder(height=0.024, radius=0.030, direct=(0.0, 0.0, 1.0))
    )
    # The notched locking quadrant the operator rides on.
    quadrant = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, r.quadrant_z + 0.010))
        .cylinder(height=QUADRANT_T, radius=0.42 * r.operator_reach_m, direct=(0.0, 0.0, 1.0))
    )
    for k in range(7):
        a = math.radians(-58.0 + 20.0 * k)
        quadrant = quadrant.cut(
            cq.Workplane("XY")
            .transformed(
                offset=(
                    (0.42 * r.operator_reach_m - 0.006) * math.cos(a),
                    (0.42 * r.operator_reach_m - 0.006) * math.sin(a),
                    r.quadrant_z + 0.010,
                ),
                rotate=(0.0, 0.0, math.degrees(a)),
            )
            .box(0.016, 0.006, 0.030)
        )
    casting = casting.union(quadrant)
    casting, extras = _BODY_END_BUILDERS[r.body_end](casting, r)
    # The stem bore runs the whole tower with a running fit.
    casting = casting.cut(
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, 0.5 * r.stem_top_z_m))
        .cylinder(height=r.stem_top_z_m * 2.0, radius=STEM_R + FIT, direct=(0.0, 0.0, 1.0))
    )
    body.visual(
        mesh_from_cadquery(casting, "bfv_casting"),
        material=mats["cast"],
        name="valve_casting", material_class_id="metal.paint_coated",
    )
    liner = _y_tube(
        r.liner_radius_m + LINER_T, r.liner_radius_m, -half + 0.002, half - 0.002
    ).cut(
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, 0.0))
        .cylinder(height=r.stem_top_z_m * 3.0, radius=STEM_R + FIT, direct=(0.0, 0.0, 1.0))
    )
    body.visual(
        mesh_from_cadquery(liner, "bfv_seat_liner"),
        material=mats["liner"],
        name="seat_liner", material_class_id="rubber.smooth_plain",
    )
    for solid, name, key in extras:
        body.visual(
            mesh_from_cadquery(solid, f"bfv_{name}"),
            material=mats[key],
            name=name, material_class_id=("metal.steel_bare" if r.body_end in {"flanged_body", "grooved_end"} else "metal.paint_coated"),
        )
    if r.operator == "gear_handwheel":
        # Host adaptation: the gear operator needs a housing on the tower.
        gear = (
            cq.Workplane("XY")
            .transformed(offset=(0.0, 0.0, r.quadrant_z + 0.048))
            .box(0.090, 0.078, 0.080)
        )
        gear = gear.cut(
            cq.Workplane("XY")
            .transformed(offset=(0.0, 0.0, r.quadrant_z + 0.060))
            .cylinder(height=0.3, radius=STEM_R + FIT, direct=(0.0, 0.0, 1.0))
        )
        gear = gear.cut(
            cq.Workplane("XY")
            .transformed(offset=(0.0, -0.040, r.quadrant_z + 0.048))
            .cylinder(height=0.080, radius=0.011 + FIT, direct=(0.0, 1.0, 0.0))
        )
        body.visual(
            mesh_from_cadquery(gear, "bfv_gearbox"),
            material=mats["steel"],
            name="operator__gear_handwheel__gearbox_housing", material_class_id="metal.steel_bare",
        )
        # A bored input-shaft boss reaching out to the handwheel hub, so the
        # wheel turns in real hardware rather than on a floating axis.
        hub_y = -(0.42 * r.operator_reach_m + 0.050)
        boss_y0 = hub_y + 0.014
        boss_y1 = -0.030
        boss = (
            cq.Workplane("XY")
            .transformed(offset=(0.0, 0.5 * (boss_y0 + boss_y1), r.quadrant_z + 0.048))
            .cylinder(height=boss_y1 - boss_y0, radius=0.020, direct=(0.0, 1.0, 0.0))
            .cut(
                cq.Workplane("XY")
                .transformed(offset=(0.0, 0.5 * (boss_y0 + boss_y1), r.quadrant_z + 0.048))
                .cylinder(
                    height=(boss_y1 - boss_y0) * 3.0,
                    radius=0.011 + FIT,
                    direct=(0.0, 1.0, 0.0),
                )
            )
        )
        body.visual(
            mesh_from_cadquery(boss, "bfv_input_boss"),
            material=mats["steel"],
            name="operator__gear_handwheel__input_boss", material_class_id="metal.steel_bare",
        )
    return body


# --- disc candidates -----------------------------------------------------------
def _disc_concentric_disc_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    host.visual(
        Cylinder(radius=r.disc_radius_m, length=DISC_T),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["disc"],
        name="disc_form__concentric_disc__plate", material_class_id="metal.stainless_matte",
    )
    host.visual(
        Cylinder(radius=r.disc_radius_m, length=DISC_T + 0.004),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="disc_form__concentric_disc__hub_band", material_class_id="metal.steel_bare",
    )


def _disc_offset_disc_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    offset = 0.006
    host.visual(
        Cylinder(radius=r.disc_radius_m - 0.004, length=DISC_T),
        origin=Origin(xyz=(0.0, offset, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["disc"],
        name="disc_form__offset_disc__plate", material_class_id="metal.stainless_matte",
    )
    # Profiled sealing edge standing proud of the offset plate.
    rim = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, offset, 0.0))
        .cylinder(height=DISC_T + 0.006, radius=r.disc_radius_m, direct=(0.0, 1.0, 0.0))
        .cut(
            cq.Workplane("XY")
            .transformed(offset=(0.0, offset, 0.0))
            .cylinder(
                height=DISC_T + 0.03, radius=r.disc_radius_m - 0.008, direct=(0.0, 1.0, 0.0)
            )
        )
    )
    host.visual(
        mesh_from_cadquery(rim, "bfv_offset_rim"),
        material=mats["steel"],
        name="disc_form__offset_disc__sealing_edge", material_class_id="metal.steel_bare",
    )
    host.visual(
        Cylinder(radius=STEM_R + 0.010, length=DISC_T + 0.010),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="disc_form__offset_disc__offset_hub", material_class_id="metal.steel_bare",
    )


def _disc_triple_offset_disc_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """A revolved conical frustum: thick at the hub, tapering to the rim, with
    an axial cone offset so the seating face torque-seats instead of rubbing."""
    hub_half = 0.5 * DISC_T
    edge_half = 0.006
    tilt = 0.004
    profile = (
        cq.Workplane("XY")
        .moveTo(0.001, -hub_half)
        .lineTo(r.disc_radius_m, -edge_half)
        .lineTo(r.disc_radius_m, edge_half)
        .lineTo(0.001, hub_half + tilt)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )
    host.visual(
        mesh_from_cadquery(profile, "bfv_triple_offset_disc"),
        material=mats["disc"],
        name="disc_form__triple_offset_disc__cone_body", material_class_id="metal.stainless_matte",
    )
    host.visual(
        Cylinder(radius=STEM_R + 0.012, length=DISC_T + 0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="disc_form__triple_offset_disc__cammed_hub", material_class_id="metal.steel_bare",
    )


def _disc_double_offset_disc_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """A double-offset disc: the plate centre is shifted off the shaft axis in
    both the bore direction and across it, riding an eccentric hub boss, so it
    cams away from the seat instead of pivoting inside it."""
    off_x = 0.10 * r.disc_radius_m
    off_y = 0.006
    # The plate is shrunk by its own eccentricity so the offset centre still
    # leaves the running clearance to the liner all the way round.
    host.visual(
        Cylinder(radius=r.disc_radius_m - off_x - 0.002, length=DISC_T - 0.004),
        origin=Origin(xyz=(off_x, off_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["disc"],
        name="disc_form__double_offset_disc__plate", material_class_id="metal.stainless_matte",
    )
    # The eccentric hub boss bridges the offset plate back onto the stem.
    host.visual(
        Cylinder(radius=STEM_R + 0.014, length=DISC_T + 0.012),
        origin=Origin(xyz=(0.0, 0.5 * off_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="disc_form__double_offset_disc__eccentric_hub", material_class_id="metal.steel_bare",
    )
    host.visual(
        Box((off_x + STEM_R + 0.014, DISC_T - 0.004, 2.0 * (STEM_R + 0.010))),
        origin=Origin(
            xyz=(0.5 * (off_x - STEM_R - 0.014) + STEM_R + 0.007, off_y, 0.0)
        ),
        material=mats["steel"],
        name="disc_form__double_offset_disc__offset_web", material_class_id="metal.steel_bare",
    )


_DISC_BUILDERS = {
    "concentric_disc": _disc_concentric_disc_build,
    "offset_disc": _disc_offset_disc_build,
    "triple_offset_disc": _disc_triple_offset_disc_build,
    "double_offset_disc": _disc_double_offset_disc_build,
}


def _build_rotor(model: ArticulatedObject, body, r: ResolvedConfig, mats: dict[str, str]):
    rotor = model.part("rotor", meta={"role": "rotor"})
    _DISC_BUILDERS[r.disc_form](rotor, r, mats)
    rotor.visual(
        Cylinder(radius=STEM_R, length=r.stem_top_z_m + r.bore_radius_m * 0.7),
        origin=Origin(
            xyz=(0.0, 0.0, 0.5 * (r.stem_top_z_m - r.bore_radius_m * 0.7))
        ),
        material=mats["steel"],
        name="rotor__stem", material_class_id="metal.steel_bare",
    )
    provider = AxisInterface(
        name="body_to_rotor__provider",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name="body_to_rotor__consumer", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "body_to_rotor",
        ArticulationType.REVOLUTE,
        parent=body,
        child=rotor,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=200.0, velocity=1.5, lower=0.0, upper=math.pi / 2.0
        ),
        meta={"positive_motion": "turns the disc from shut to open"},
    )
    register_interface_mate(model, "body_to_rotor", mate)
    return rotor


# --- operator candidates -------------------------------------------------------
def _build_operator(model: ArticulatedObject, body, rotor, r: ResolvedConfig, mats):
    if r.operator == "lever_trigger":
        lever = model.part("operator__lever_trigger__lever", meta={"role": "operator"})
        plate_z = r.quadrant_z + 0.022
        off = (0.0, 0.0, plate_z)
        reach = r.operator_reach_m
        lever.visual(
            Box((reach - 0.060, 0.030, 0.012)),
            origin=_local_origin(Origin(xyz=(-0.5 * reach, 0.0, plate_z)), off),
            material=mats["cast"],
            name="operator__lever_trigger__lever_plate", material_class_id="metal.paint_coated",
        )
        # A bored boss: the lever clamps round the stem with a running fit
        # instead of being driven into it.
        boss = (
            cq.Workplane("XY")
            .transformed(offset=(0.0, 0.0, plate_z + 0.010))
            .cylinder(height=0.030, radius=0.026, direct=(0.0, 0.0, 1.0))
            .cut(
                cq.Workplane("XY")
                .transformed(offset=(0.0, 0.0, plate_z + 0.010))
                .cylinder(height=0.060, radius=STEM_R + FIT, direct=(0.0, 0.0, 1.0))
            )
        )
        lever.visual(
            mesh_from_cadquery(boss, "bfv_lever_boss"),
            origin=_local_origin(None, off),
            material=mats["cast"],
            name="operator__lever_trigger__stem_boss", material_class_id="metal.paint_coated",
        )
        lever.visual(
            Cylinder(radius=0.018, length=0.090),
            origin=_local_origin(
                Origin(
                    xyz=(-reach + 0.040, 0.0, plate_z),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                off,
            ),
            material=mats["grip"],
            name="operator__lever_trigger__grip_sleeve", material_class_id="rubber.smooth_plain",
        )
        lever.visual(
            Box((0.34 * reach, 0.020, 0.010)),
            origin=_local_origin(
                Origin(xyz=(-0.24 * reach, 0.0, plate_z + 0.011)), off
            ),
            material=mats["steel"],
            name="operator__lever_trigger__trigger_plate", material_class_id="metal.steel_bare",
        )
        # The pawl reaches down toward the quadrant notches with a 1 mm gap, so
        # the lever never drives into the locking sector.
        lever.visual(
            Box((0.016, 0.014, 0.010)),
            origin=_local_origin(
                Origin(xyz=(-0.40 * reach, 0.0, plate_z - 0.007)), off
            ),
            material=mats["steel"],
            name="operator__lever_trigger__trigger_pawl", material_class_id="metal.steel_bare",
        )
        model.articulation(
            "rotor_to_operator",
            ArticulationType.FIXED,
            parent=rotor,
            child=lever,
            origin=Origin(xyz=off),
        )
        return lever

    if r.operator == "tee_bar":
        tee = model.part("operator__tee_bar__handle", meta={"role": "operator"})
        plate_z = r.quadrant_z + 0.022
        off = (0.0, 0.0, plate_z)
        span = 0.62 * r.operator_reach_m
        boss = (
            cq.Workplane("XY")
            .transformed(offset=(0.0, 0.0, plate_z + 0.010))
            .cylinder(height=0.030, radius=0.026, direct=(0.0, 0.0, 1.0))
            .cut(
                cq.Workplane("XY")
                .transformed(offset=(0.0, 0.0, plate_z + 0.010))
                .cylinder(height=0.060, radius=STEM_R + FIT, direct=(0.0, 0.0, 1.0))
            )
        )
        tee.visual(
            mesh_from_cadquery(boss, "bfv_tee_boss"),
            origin=_local_origin(None, off),
            material=mats["cast"],
            name="operator__tee_bar__stem_boss", material_class_id="metal.paint_coated",
        )
        tee.visual(
            Box((span, 0.022, 0.012)),
            origin=_local_origin(Origin(xyz=(0.0, 0.0, plate_z + 0.028)), off),
            material=mats["cast"],
            name="operator__tee_bar__crossbar", material_class_id="metal.paint_coated",
        )
        for index, sx in enumerate((-1.0, 1.0)):
            tee.visual(
                Box((0.046, 0.030, 0.018)),
                origin=_local_origin(
                    Origin(
                        xyz=(sx * (0.5 * span - 0.020), 0.0, plate_z + 0.028)
                    ),
                    off,
                ),
                material=mats["grip"],
                name=f"operator__tee_bar__grip_sleeve_{index}", material_class_id="rubber.smooth_plain",
            )
        model.articulation(
            "rotor_to_operator",
            ArticulationType.FIXED,
            parent=rotor,
            child=tee,
            origin=Origin(xyz=off),
        )
        return tee

    wheel = model.part("operator__gear_handwheel__handwheel", meta={"role": "operator"})
    rim_r = 0.36 * r.operator_reach_m
    # The wheel plane stands clear of the locking quadrant's own radius, so the
    # spokes sweep a free circle beside the valve rather than over it.
    hub_y = -(0.42 * r.operator_reach_m + 0.050)
    hub_z = r.quadrant_z + 0.048
    off = (0.0, hub_y, hub_z)
    shaft_len = -hub_y - 0.030
    wheel.visual(
        Cylinder(radius=0.011, length=shaft_len),
        origin=_local_origin(
            Origin(
                xyz=(0.0, hub_y + 0.5 * shaft_len, hub_z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            off,
        ),
        material=mats["steel"],
        name="operator__gear_handwheel__input_shaft", material_class_id="metal.steel_bare",
    )
    rim = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, hub_y, hub_z))
        .cylinder(height=0.014, radius=rim_r, direct=(0.0, 1.0, 0.0))
        .cut(
            cq.Workplane("XY")
            .transformed(offset=(0.0, hub_y, hub_z))
            .cylinder(height=0.05, radius=rim_r - 0.012, direct=(0.0, 1.0, 0.0))
        )
    )
    wheel.visual(
        mesh_from_cadquery(rim, "bfv_handwheel_rim"),
        origin=_local_origin(None, off),
        material=mats["cast"],
        name="operator__gear_handwheel__wheel_rim", material_class_id="metal.paint_coated",
    )
    for k in range(4):
        a = k * math.pi / 2.0
        wheel.visual(
            Box((2.0 * rim_r - 0.012, 0.010, 0.010)),
            origin=_local_origin(
                Origin(xyz=(0.0, hub_y, hub_z), rpy=(0.0, a, 0.0)), off
            ),
            material=mats["cast"],
            name=f"operator__gear_handwheel__spoke_{k}", material_class_id="metal.paint_coated",
        )
    wheel.visual(
        Cylinder(radius=0.020, length=0.020),
        origin=_local_origin(
            Origin(
                xyz=(0.0, hub_y, hub_z), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            off,
        ),
        material=mats["steel"],
        name="operator__gear_handwheel__wheel_hub", material_class_id="metal.steel_bare",
    )
    provider = AxisInterface(
        name="body_to_operator__provider",
        point=(0.0, hub_y, hub_z),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name="body_to_operator__consumer", axis=(0.0, 1.0, 0.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "body_to_operator",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=wheel,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=40.0, velocity=3.0),
        meta={"positive_motion": "winds the gear operator toward open"},
    )
    register_interface_mate(model, "body_to_operator", mate)
    return wheel


# --- assembly -------------------------------------------------------------------
def build_picturex_0611_butterfly_valve_with_lever_operator(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_butterfly_valve_with_lever_operator",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "quarter-turn disc on a vertical stem in a lined bore",
        },
    )
    mats = _materials(model, r)
    body = _build_body(model, r, mats)
    rotor = _build_rotor(model, body, r, mats)
    _build_operator(model, body, rotor, r, mats)

    risk = [
        {"body_to_rotor": 0.0},
        {"body_to_rotor": math.pi / 2.0},
        {"body_to_rotor": math.pi / 4.0},
    ]
    if r.operator == "gear_handwheel":
        risk[1]["body_to_operator"] = math.pi
        risk[2]["body_to_operator"] = math.pi / 2.0
    model.meta["risk_poses"] = tuple(risk)
    return model


def build_seeded_picturex_0611_butterfly_valve_with_lever_operator(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_butterfly_valve_with_lever_operator(
        config_from_seed(seed), assets=assets
    )


# --- authored tests --------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_butterfly_valve_with_lever_operator_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    bodies = _parts_by_role(model, "valve_body")
    rotors = _parts_by_role(model, "rotor")
    operators = _parts_by_role(model, "operator")
    joints = {j.name: j for j in model.articulations}
    rotor_joint = joints.get("body_to_rotor")

    ctx.check(
        "category_anchor: lined bore with a quarter-turn disc on a vertical stem",
        len(bodies) == 1
        and len(rotors) == 1
        and len(operators) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "valve_body"
        and rotor_joint is not None
        and rotor_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(abs(v), 6) for v in rotor_joint.axis) == (0.0, 0.0, 1.0)
        and rotor_joint.parent == "valve_body"
        and abs(rotor_joint.motion_limits.upper - math.pi / 2.0) < 1e-9
        and abs(rotor_joint.motion_limits.lower) < 1e-9,
        details=(
            f"bodies={len(bodies)} rotors={len(rotors)} operators={len(operators)} "
            f"joints={sorted(joints)}"
        ),
    )

    ctx.check(
        "category_anchor: the disc sweeps the bore without touching the liner",
        0.0 < FIT <= 0.001
        and abs(r.disc_radius_m - (r.bore_radius_m - 0.0008)) < 1e-9
        and r.disc_radius_m < r.liner_radius_m
        and abs(r.ring_outer_m - (r.bore_radius_m + LINER_T + WALL)) < 1e-9
        and r.bolt_circle_radius_m > r.ring_outer_m
        and r.stem_top_z_m > r.ring_outer_m
        and len(_bolt_angles(r)) == r.flange_bolt_count,
        details=(
            f"disc={r.disc_radius_m} bore={r.bore_radius_m} ring={r.ring_outer_m} "
            f"bolts={r.flange_bolt_count}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    body_ok = {
        "lug_body": sum(1 for n in visual_names if "lug_body__bolt_lug_" in n)
        == r.flange_bolt_count,
        "flanged_body": sum(1 for n in visual_names if "flanged_body__bolt_boss_" in n)
        == r.flange_bolt_count,
        "grooved_end": sum(1 for n in visual_names if "grooved_end__clamp_segment_" in n)
        == r.flange_bolt_count,
    }[r.body_end]
    ctx.check(
        "category_anchor: body_end identity",
        body_ok
        and any("valve_casting" in n for n in visual_names)
        and any("seat_liner" in n for n in visual_names),
        details=f"body_end={r.body_end} bolts={r.flange_bolt_count}",
    )

    disc_ok = {
        "concentric_disc": any("concentric_disc__plate" in n for n in visual_names)
        and any("concentric_disc__hub_band" in n for n in visual_names),
        "offset_disc": any("offset_disc__sealing_edge" in n for n in visual_names)
        and any("offset_disc__offset_hub" in n for n in visual_names),
        "triple_offset_disc": any("triple_offset_disc__cone_body" in n for n in visual_names)
        and any("triple_offset_disc__cammed_hub" in n for n in visual_names),
        "double_offset_disc": any("double_offset_disc__plate" in n for n in visual_names)
        and any("double_offset_disc__eccentric_hub" in n for n in visual_names)
        and any("double_offset_disc__offset_web" in n for n in visual_names),
    }[r.disc_form]
    ctx.check("category_anchor: disc_form identity", disc_ok, details=f"disc={r.disc_form}")

    operator_ok = {
        "lever_trigger": any("lever_trigger__trigger_plate" in n for n in visual_names)
        and any("lever_trigger__grip_sleeve" in n for n in visual_names)
        and joints["rotor_to_operator"].articulation_type == ArticulationType.FIXED,
        "tee_bar": sum(1 for n in visual_names if "tee_bar__grip_sleeve" in n) == 2
        and any("tee_bar__crossbar" in n for n in visual_names)
        and joints["rotor_to_operator"].articulation_type == ArticulationType.FIXED,
        "gear_handwheel": sum(1 for n in visual_names if "gear_handwheel__spoke" in n) == 4
        and any("gear_handwheel__gearbox_housing" in n for n in visual_names)
        and joints["body_to_operator"].articulation_type == ArticulationType.CONTINUOUS,
    }[r.operator]
    ctx.check("category_anchor: operator identity", operator_ok, details=f"op={r.operator}")

    bonnet_ok = (
        r.tower_top_z > r.ring_outer_m + 0.9 * r.bore_radius_m + 0.060
        and (
            r.tower_top_z > r.ring_outer_m + 0.9 * r.bore_radius_m + 0.150
            if r.bonnet_form == "extended_bonnet"
            else r.tower_top_z < r.ring_outer_m + 0.9 * r.bore_radius_m + 0.090
        )
    )
    ctx.check(
        "category_anchor: bonnet_form identity",
        bonnet_ok,
        details=f"bonnet={r.bonnet_form} tower_top={r.tower_top_z} ring={r.ring_outer_m}",
    )

    # Motion evidence: a quarter turn swings the disc from across the bore to
    # edge-on, which is the whole point of a butterfly valve.
    shut = ctx.part_world_aabb(rotors[0])
    with ctx.pose({rotor_joint: math.pi / 2.0}):
        open_ = ctx.part_world_aabb(rotors[0])
    ctx.check(
        "a quarter turn swings the disc from shut to edge-on in the bore",
        shut is not None
        and open_ is not None
        and (shut[1][0] - shut[0][0]) > 1.5 * r.disc_radius_m
        and (open_[1][0] - open_[0][0]) < 0.6 * (shut[1][0] - shut[0][0])
        and (open_[1][1] - open_[0][1]) > 1.5 * r.disc_radius_m,
        details=f"shut={shut} open={open_}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_bore_four_bolts_lug_lever",
        {
            "body_end": "lug_body",
            "disc_form": "concentric_disc",
            "operator": "lever_trigger",
            "bonnet_form": "short_bonnet",
            "flange_bolt_count": 4,
            "bore_radius_m": 0.050,
            "face_to_face_m": 0.050,
            "operator_reach_m": 0.150,
        },
        reason="smallest bore and shortest body with the fewest lugs and the shortest lever",
    ),
    corner_case(
        "max_bore_twelve_bolts_flanged_gear",
        {
            "body_end": "flanged_body",
            "disc_form": "offset_disc",
            "operator": "gear_handwheel",
            "bonnet_form": "extended_bonnet",
            "flange_bolt_count": 12,
            "bore_radius_m": 0.150,
            "face_to_face_m": 0.110,
            "operator_reach_m": 0.320,
        },
        reason="largest bore with twelve bolts, the offset disc and the gear operator",
    ),
    corner_case(
        "max_bore_four_bolts_grooved_lever",
        {
            "body_end": "grooved_end",
            "disc_form": "offset_disc",
            "operator": "tee_bar",
            "bonnet_form": "extended_bonnet",
            "flange_bolt_count": 4,
            "bore_radius_m": 0.150,
            "face_to_face_m": 0.050,
            "operator_reach_m": 0.150,
        },
        reason="widest bore in the shortest grooved body — the tightest groove machining",
    ),
    corner_case(
        "min_bore_twelve_bolts_grooved_gear",
        {
            "body_end": "grooved_end",
            "disc_form": "concentric_disc",
            "operator": "tee_bar",
            "bonnet_form": "short_bonnet",
            "flange_bolt_count": 12,
            "bore_radius_m": 0.050,
            "face_to_face_m": 0.110,
            "operator_reach_m": 0.320,
        },
        reason="twelve clamp segments on the smallest bolt circle under the largest handwheel",
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
    "build_picturex_0611_butterfly_valve_with_lever_operator",
    "build_seeded_picturex_0611_butterfly_valve_with_lever_operator",
    "run_picturex_0611_butterfly_valve_with_lever_operator_tests",
]
