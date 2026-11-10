# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'industrial_crane_featuring_advanced_hydraulic' template.

Rebuilt from the two ``pictureX/0611/industrial_crane_featuring_advanced_hydraulic``
origin records and the five accepted forks listed in
``articraft_template_authoring/source_maps/pictureX_0611_industrial_crane_featuring_advanced_hydraulic.md``.

Category identity: a mobile hydraulic shop crane — a wheeled floor frame with a
mast, a boom that luffs on a hydraulic ram fed by a hand pump, and a swivel hook
at the boom tip.  Two independent structural axes plus the caster multiplicity:

* ``frame_style``  — long A-frame base, compact welded shop base, ballasted
  counterweight base, folding shop base, or a base with swing-out outriggers.
* ``boom_style``   — one sliding extension, a telescoping stage chain, or a
  knuckle jib on its own ram.
* ``caster_count`` — 4 or 6 swivel caster stations.

Coordinate frame: the floor is z = 0, the mast stands at x = 0 and the legs and
the boom reach forward along +X.

This file is the only runtime truth.  It imports the stdlib and the Articraft
``sdk`` only.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    MotionLimits,
    MotionProperties,
    Origin,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    multiplicity_slot,
    register_interface_mate,
)

FrameStyle = Literal[
    "a_frame_base",
    "compact_shop_base",
    "counterweight_base",
    "foldable_shop_base",
]
Stabilizer = Literal["fixed_stance", "swing_out_outriggers"]
BoomStyle = Literal["single_extension", "telescoping_stages", "knuckle_jib"]
HookStyle = Literal["chain_hook", "ball_hook"]

FRAME_STYLES: tuple[FrameStyle, ...] = (
    "a_frame_base",
    "compact_shop_base",
    "counterweight_base",
    "foldable_shop_base",
)
STABILIZERS: tuple[Stabilizer, ...] = ("fixed_stance", "swing_out_outriggers")
BOOM_STYLES: tuple[BoomStyle, ...] = ("single_extension", "telescoping_stages", "knuckle_jib")
HOOK_STYLES: tuple[HookStyle, ...] = ("chain_hook", "ball_hook")
CASTER_COUNTS: tuple[int, ...] = (4, 6)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("frame_style", FRAME_STYLES),
        component_slot("stabilizer", STABILIZERS),
        component_slot("boom_style", BOOM_STYLES),
        component_slot("hook_style", HOOK_STYLES),
        multiplicity_slot("caster_count", CASTER_COUNTS, item_slot="frame_style"),
    )
)

_MAST_HEIGHT_RANGE = (0.60, 1.15)
_LEG_LENGTH_RANGE = (0.70, 1.40)
_BOOM_LENGTH_RANGE = (0.70, 1.50)
_TRACK_WIDTH_RANGE = (0.44, 0.90)
_CASTER_RADIUS_RANGE = (0.036, 0.075)

_LEG = 0.060  # leg box section
_MAST = 0.080  # mast box section
_BOOM = 0.070  # boom box section
_WALL = 0.010  # section wall thickness
_PIN_R = 0.014
_WELD = 0.0010
_CLEAR = 0.0015
_SLIDE_FIT = 0.0016  # running fit between a section and the one sliding in it


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Config:
    frame_style: FrameStyle = "a_frame_base"
    stabilizer: Stabilizer = "fixed_stance"
    boom_style: BoomStyle = "single_extension"
    hook_style: HookStyle = "chain_hook"
    caster_count: int = 4
    mast_height_m: float | None = None
    leg_length_m: float | None = None
    boom_length_m: float | None = None
    track_width_m: float | None = None
    caster_radius_m: float | None = None
    name: str = "pictureX_0611_industrial_crane_featuring_advanced_hydraulic"


@dataclass(frozen=True)
class ResolvedConfig:
    frame_style: FrameStyle
    stabilizer: Stabilizer
    boom_style: BoomStyle
    hook_style: HookStyle
    caster_count: int
    mast_height_m: float
    leg_length_m: float
    boom_length_m: float
    track_width_m: float
    caster_radius_m: float
    # derived
    leg_z_m: float
    pivot_z_m: float
    ram_foot_x_m: float
    ram_foot_z_m: float
    ram_boom_x_m: float
    boom_rise_rad: float
    boom_drop_rad: float
    station_pitch_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x0C7A2E)
    return Config(
        frame_style=choices["frame_style"],
        stabilizer=choices["stabilizer"],
        boom_style=choices["boom_style"],
        hook_style=choices["hook_style"],
        caster_count=choices["caster_count"],
        mast_height_m=round(rng.uniform(*_MAST_HEIGHT_RANGE), 5),
        leg_length_m=round(rng.uniform(*_LEG_LENGTH_RANGE), 5),
        boom_length_m=round(rng.uniform(*_BOOM_LENGTH_RANGE), 5),
        track_width_m=round(rng.uniform(*_TRACK_WIDTH_RANGE), 5),
        caster_radius_m=round(rng.uniform(*_CASTER_RADIUS_RANGE), 5),
    )


def _range_check(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "frame_style": config.frame_style,
            "stabilizer": config.stabilizer,
            "boom_style": config.boom_style,
            "hook_style": config.hook_style,
            "caster_count": config.caster_count,
        }
    )
    mast = 0.860 if config.mast_height_m is None else float(config.mast_height_m)
    leg = 1.050 if config.leg_length_m is None else float(config.leg_length_m)
    boom = 1.100 if config.boom_length_m is None else float(config.boom_length_m)
    track = 0.640 if config.track_width_m is None else float(config.track_width_m)
    caster = 0.052 if config.caster_radius_m is None else float(config.caster_radius_m)
    _range_check("mast_height_m", mast, _MAST_HEIGHT_RANGE)
    _range_check("leg_length_m", leg, _LEG_LENGTH_RANGE)
    _range_check("boom_length_m", boom, _BOOM_LENGTH_RANGE)
    _range_check("track_width_m", track, _TRACK_WIDTH_RANGE)
    _range_check("caster_radius_m", caster, _CASTER_RADIUS_RANGE)

    count = int(config.caster_count)
    # Host capacity: every caster station needs its own run of leg, so a
    # six-station base lengthens its legs rather than crowding the wheels.
    stations = max(count // 2, 1)
    min_leg = 0.24 * float(stations - 1) + 0.34
    leg = max(leg, min_leg)
    leg_z = 2.0 * caster + 0.030
    pivot_z = leg_z + mast
    ram_foot_x = _MAST / 2.0 + 0.032
    ram_foot_z = leg_z + mast * 0.20
    ram_boom_x = _clamp(boom * 0.34, 0.16, 0.46)
    return ResolvedConfig(
        frame_style=config.frame_style,
        stabilizer=config.stabilizer,
        boom_style=config.boom_style,
        hook_style=config.hook_style,
        caster_count=count,
        mast_height_m=mast,
        leg_length_m=leg,
        boom_length_m=boom,
        track_width_m=track,
        caster_radius_m=caster,
        leg_z_m=leg_z,
        pivot_z_m=pivot_z,
        ram_foot_x_m=ram_foot_x,
        ram_foot_z_m=ram_foot_z,
        ram_boom_x_m=ram_boom_x,
        boom_rise_rad=0.72,
        boom_drop_rad=0.24,
        station_pitch_m=(leg - 0.34) / float(max(stations - 1, 1)),
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("frame_style", config.frame_style),
        ("stabilizer", config.stabilizer),
        ("boom_style", config.boom_style),
        ("hook_style", config.hook_style),
        ("caster_count", int(config.caster_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Materials and primitive helpers
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("crane_red", rgba=(0.62, 0.11, 0.10, 1.0))
    model.material("crane_grey", rgba=(0.32, 0.33, 0.34, 1.0))
    model.material("chrome_rod", rgba=(0.82, 0.84, 0.86, 1.0))
    model.material("black_poly", rgba=(0.08, 0.08, 0.08, 1.0))
    model.material("hook_steel", rgba=(0.66, 0.62, 0.30, 1.0))
    return {
        "body": "crane_red",
        "steel": "crane_grey",
        "rod": "chrome_rod",
        "poly": "black_poly",
        "hook": "hook_steel",
    }


def _box(part, size, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(part, radius, length, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


_Y_AXIS_RPY = (math.pi / 2.0, 0.0, 0.0)
_X_AXIS_RPY = (0.0, math.pi / 2.0, 0.0)


def _hollow_section(
    part,
    mats,
    *,
    x0: float,
    x1: float,
    y: float,
    z: float,
    section: float,
    wall: float,
    material: str,
    prefix: str,
) -> None:
    """A hollow square section running along X, open for whatever slides in it."""
    length = abs(x1 - x0)
    xm = (x0 + x1) / 2.0
    half = section / 2.0
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (length, wall, section),
            (xm, y + sign * (half - wall / 2.0), z),
            material,
            f"{prefix}_web_{index}",
        )
        _box(
            part,
            (length, section - 2.0 * wall + 2.0 * _WELD, wall),
            (xm, y, z + sign * (half - wall / 2.0)),
            material,
            f"{prefix}_flange_{index}",
        )


def _hollow_tube(
    part,
    mats,
    *,
    z0: float,
    z1: float,
    x: float,
    y: float,
    radius: float,
    wall: float,
    segments: int,
    material: str,
    prefix: str,
) -> None:
    """A hollow round section running along Z, open for a rod."""
    length = abs(z1 - z0)
    zm = (z0 + z1) / 2.0
    for index in range(segments):
        angle = 2.0 * math.pi * float(index) / float(segments)
        tangential = 2.0 * math.pi * radius / float(segments) * 1.35 + wall
        _box(
            part,
            (tangential, wall, length),
            (x + radius * math.sin(angle), y + radius * math.cos(angle), zm),
            material,
            f"{prefix}_{index}",
            rpy=(0.0, 0.0, -angle),
        )


def _spin_joint(
    model: ArticulatedObject,
    parent,
    child,
    *,
    name: str,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    radius: float,
    joint_type: ArticulationType,
    limits: MotionLimits,
    child_radial: tuple[float, float, float] | None = None,
    meta: dict | None = None,
) -> str:
    provider = AxisInterface(
        name=f"{name}__provider",
        point=point,
        axis=axis,
        radial=radial,
        radius=radius + _CLEAR,
    )
    consumer = AxisInterface(
        name=f"{name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=axis,
        radial=radial if child_radial is None else child_radial,
        radius=radius,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        joint_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        motion_properties=MotionProperties(damping=2.0, friction=1.0),
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)
    return name


# --------------------------------------------------------------------------- #
# Shared host: rolling casters, lift ram, pump handle and hook
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _Frame:
    part: object
    stations: tuple[tuple[float, float], ...]  # caster mount (x, y)
    mast_top_z: float


def _caster_stations(r: ResolvedConfig, leg_span: float) -> tuple[tuple[float, float], ...]:
    """Caster stations spread along whatever leg run the frame candidate built."""
    stations = max(r.caster_count // 2, 1)
    half = r.track_width_m / 2.0
    first = 0.090
    last = max(0.040 + leg_span - 0.060, first + 0.10)
    out: list[tuple[float, float]] = []
    for index in range(stations):
        frac = 0.0 if stations == 1 else float(index) / float(stations - 1)
        x = first + (last - first) * frac
        for sign in (-1.0, 1.0):
            out.append((x, sign * half))
    return tuple(out[: r.caster_count])


def _build_casters(model, r: ResolvedConfig, mats, frame: _Frame) -> list[str]:
    joints: list[str] = []
    for index, (x, y) in enumerate(frame.stations):
        caster = model.part(f"caster_{index}", meta={"role": "caster", "index": index})
        _cyl(caster, 0.020, 0.014, (0.0, 0.0, -0.007), mats["steel"], "swivel_plate")
        for cheek, sign in enumerate((-1.0, 1.0)):
            _box(
                caster,
                (r.caster_radius_m * 1.5, 0.010, 2.0 * r.caster_radius_m + 0.014),
                (0.012, sign * (r.caster_radius_m * 0.42 + 0.007), -r.caster_radius_m - 0.012),
                mats["steel"],
                f"fork_cheek_{cheek}",
            )
        _box(
            caster,
            (r.caster_radius_m * 1.5, 2.0 * r.caster_radius_m * 0.42 + 0.024, 0.012),
            (0.012, 0.0, -0.008),
            mats["steel"],
            "fork_crown",
        )
        joints.append(
            _spin_joint(
                model,
                frame.part,
                caster,
                name=f"caster_{index}__swivel",
                point=(x, y, r.leg_z_m - 0.004),
                axis=(0.0, 0.0, 1.0),
                radial=(1.0, 0.0, 0.0),
                radius=0.020,
                joint_type=ArticulationType.CONTINUOUS,
                limits=MotionLimits(effort=18.0, velocity=4.0),
                meta={"mechanism": "caster swivel"},
            )
        )
        wheel = model.part(f"wheel_{index}", meta={"role": "wheel", "index": index})
        _cyl(
            wheel,
            r.caster_radius_m,
            r.caster_radius_m * 0.72,
            (0.0, 0.0, 0.0),
            mats["poly"],
            "tyre",
            rpy=_Y_AXIS_RPY,
        )
        _cyl(
            wheel,
            r.caster_radius_m * 0.38,
            r.caster_radius_m * 0.80,
            (0.0, 0.0, 0.0),
            mats["steel"],
            "hub",
            rpy=_Y_AXIS_RPY,
        )
        joints.append(
            _spin_joint(
                model,
                caster,
                wheel,
                name=f"wheel_{index}__spin",
                point=(0.012, 0.0, -r.caster_radius_m - 0.014),
                axis=(0.0, 1.0, 0.0),
                radial=(1.0, 0.0, 0.0),
                radius=r.caster_radius_m,
                joint_type=ArticulationType.CONTINUOUS,
                limits=MotionLimits(effort=10.0, velocity=12.0),
                meta={"mechanism": "caster wheel spin"},
            )
        )
    return joints


def _build_ram(model, r: ResolvedConfig, mats, frame: _Frame) -> list[str]:
    """The lift ram and its hand pump, both anchored on the frame."""
    barrel = model.part("hydraulic_cylinder", meta={"role": "ram", "construction": "lift cylinder"})
    length = (r.pivot_z_m - r.ram_foot_z_m) * 0.62
    _cyl(barrel, 0.022, 0.020, (0.0, 0.0, 0.008), mats["steel"], "barrel_foot")
    _hollow_tube(
        barrel,
        mats,
        z0=0.018,
        z1=length,
        x=0.0,
        y=0.0,
        radius=0.026,
        wall=0.010,
        segments=10,
        material=mats["body"],
        prefix="barrel_wall",
    )
    _hollow_tube(
        barrel,
        mats,
        z0=length - 0.014,
        z1=length,
        x=0.0,
        y=0.0,
        radius=0.0265,
        wall=0.011,
        segments=10,
        material=mats["steel"],
        prefix="barrel_gland",
    )
    pitch = math.atan2(r.pivot_z_m - r.ram_foot_z_m, r.ram_boom_x_m - r.ram_foot_x_m)
    barrel_joint = _spin_joint(
        model,
        frame.part,
        barrel,
        name="hydraulic_cylinder__foot",
        point=(r.ram_foot_x_m, 0.0, r.ram_foot_z_m),
        axis=(0.0, 1.0, 0.0),
        radial=(math.cos(pitch), 0.0, math.sin(pitch)),
        child_radial=(0.0, 0.0, 1.0),
        radius=0.030,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=9000.0, velocity=0.25, lower=-0.14, upper=0.14),
        meta={"mechanism": "ram foot pin"},
    )
    rod = model.part("cylinder_rod", meta={"role": "ram_rod", "construction": "chrome ram rod"})
    stroke = (r.pivot_z_m - r.ram_foot_z_m) * 0.26
    _cyl(rod, 0.0202, length * 0.70, (0.0, 0.0, length * 0.35), mats["rod"], "rod_shaft")
    _cyl(rod, 0.026, 0.018, (0.0, 0.0, length * 0.70), mats["steel"], "rod_eye_boss")
    rod_joint = "cylinder_rod__extend"
    model.articulation(
        rod_joint,
        ArticulationType.PRISMATIC,
        parent=barrel,
        child=rod,
        origin=Origin(xyz=(0.0, 0.0, length * 0.20)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=14000.0, velocity=0.12, lower=0.0, upper=stroke),
        motion_properties=MotionProperties(damping=3.0, friction=1.5),
        meta={"mechanism": "ram extension"},
    )
    pump = model.part("pump_handle", meta={"role": "pump", "construction": "hand pump handle"})
    _cyl(pump, 0.016, 0.058, (0.0, 0.0, 0.0), mats["steel"], "pump_hub", rpy=_Y_AXIS_RPY)
    handle = r.leg_length_m * 0.42
    _cyl(pump, 0.013, handle, (-handle / 2.0, 0.0, 0.0), mats["steel"], "pump_bar", rpy=_X_AXIS_RPY)
    _cyl(
        pump, 0.019, 0.100, (-handle + 0.050, 0.0, 0.0), mats["poly"], "pump_grip", rpy=_X_AXIS_RPY
    )
    pump_joint = _spin_joint(
        model,
        frame.part,
        pump,
        name="pump_handle__stroke",
        point=(-(_MAST / 2.0 + 0.026), 0.0, r.ram_foot_z_m + 0.060),
        axis=(0.0, 1.0, 0.0),
        radial=(-1.0, 0.0, 0.0),
        radius=0.016,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=180.0, velocity=3.0, lower=-0.22, upper=0.50),
        meta={"mechanism": "hand pump stroke"},
    )
    return [barrel_joint, rod_joint, pump_joint]


def _hook_style_chain_hook_build(hook, mats) -> None:
    """001 L369-L400: a slender zig-zag chain run curling into a small hook.

    The source builds one continuous spline tube; here the same silhouette is a
    chain of short links that stay welded to each other, so the part is a single
    connected island.
    """
    path = (
        (0.0, -0.018),
        (0.012, -0.070),
        (-0.012, -0.120),
        (0.012, -0.170),
        (-0.010, -0.220),
        (0.0, -0.275),
        (0.0, -0.315),
        (0.012, -0.345),
        (0.040, -0.365),
        (0.068, -0.353),
        (0.078, -0.325),
        (0.072, -0.298),
    )
    for index in range(len(path) - 1):
        x0, z0 = path[index]
        x1, z1 = path[index + 1]
        dx, dz = x1 - x0, z1 - z0
        span = math.hypot(dx, dz)
        _cyl(
            hook,
            0.0075,
            span + 0.006,
            ((x0 + x1) / 2.0, 0.0, (z0 + z1) / 2.0),
            mats["hook"],
            f"chain_link_{index}",
            rpy=(0.0, math.atan2(dx, dz), 0.0),
        )
    _cyl(hook, 0.021, 0.040, (0.0, 0.0, -0.020), mats["steel"], "swivel_body")


def _hook_style_ball_hook_build(hook, mats) -> None:
    """002 L281-L296: a rigid shank with a ball swivel and a heavy forged hook."""
    _cyl(hook, 0.018, 0.060, (0.0, 0.0, -0.030), mats["steel"], "swivel_boss")
    _cyl(hook, 0.009, 0.155, (0.0, 0.0, -0.1325), mats["steel"], "chain_shank")
    hook.visual(
        Sphere(radius=0.026),
        origin=Origin(xyz=(0.0, 0.0, -0.215)),
        material=mats["steel"],
        name="hook_bowl", material_class_id="metal.steel_bare",
    )
    for index, (p0, p1, radius) in enumerate(
        (
            ((0.0, -0.215), (0.055, -0.265), 0.015),
            ((0.055, -0.265), (0.088, -0.205), 0.014),
            ((0.088, -0.205), (0.065, -0.175), 0.012),
        )
    ):
        dx, dz = p1[0] - p0[0], p1[1] - p0[1]
        span = math.hypot(dx, dz)
        _cyl(
            hook,
            radius,
            span + 0.004,
            ((p0[0] + p1[0]) / 2.0, 0.0, (p0[1] + p1[1]) / 2.0),
            mats["hook"],
            f"forged_bend_{index}",
            rpy=(0.0, math.atan2(dx, dz), 0.0),
        )


_HOOK_BUILDERS = {
    "chain_hook": _hook_style_chain_hook_build,
    "ball_hook": _hook_style_ball_hook_build,
}


def _add_hook(model, r, mats, parent, tip_x: float, section: float = _BOOM) -> str:
    """Hang the hook the hook_style slot chose on whichever boom section carries the tip."""
    hook = model.part(
        f"hook_style__{r.hook_style}__hook",
        meta={"role": "hook", "construction": f"{r.hook_style} load hook"},
    )
    _HOOK_BUILDERS[r.hook_style](hook, mats)
    return _spin_joint(
        model,
        parent,
        hook,
        name=f"hook_style__{r.hook_style}__hook__swivel",
        point=(tip_x, 0.0, -section / 2.0 - 0.0005),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.018,
        joint_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=30.0, velocity=5.0),
        meta={"mechanism": "hook swivel"},
    )


# --------------------------------------------------------------------------- #
# frame_style candidates
# --------------------------------------------------------------------------- #
def _base_legs(part, r: ResolvedConfig, mats, *, length: float, prefix: str) -> None:
    half = r.track_width_m / 2.0
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (length, _LEG, _LEG),
            (length / 2.0 + 0.040, sign * half, r.leg_z_m + _LEG / 2.0 - 0.004),
            mats["body"],
            f"{prefix}_leg_{index}",
        )
    _box(
        part,
        (_LEG, r.track_width_m + _LEG, _LEG),
        (0.040, 0.0, r.leg_z_m + _LEG / 2.0 - 0.004),
        mats["body"],
        f"{prefix}_cross_beam",
    )


def _mast(part, r: ResolvedConfig, mats, *, prefix: str) -> None:
    top = r.pivot_z_m - 0.040
    bottom = r.leg_z_m - _LEG
    _box(
        part,
        (_MAST, _MAST, top - bottom),
        (0.0, 0.0, (bottom + top) / 2.0),
        mats["body"],
        f"{prefix}_mast",
    )
    _box(
        part,
        (0.076, 2.0 * (_BOOM / 2.0 + 0.028), 0.026),
        (0.012, 0.0, top - 0.024),
        mats["body"],
        f"{prefix}_mast_crown",
    )
    # A clevis at the mast top carries the boom pin.
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.070, 0.014, 0.100),
            (0.012, sign * (_BOOM / 2.0 + 0.020), r.pivot_z_m - 0.036),
            mats["steel"],
            f"{prefix}_boom_cheek_{index}",
        )
    eye_half = (_BOOM + 0.024) / 2.0
    for index, sign in enumerate((-1.0, 1.0)):
        _cyl(
            part,
            _PIN_R,
            0.018,
            (0.0, sign * (eye_half + 0.007), r.pivot_z_m),
            mats["steel"],
            f"{prefix}_boom_pin_{index}",
            rpy=_Y_AXIS_RPY,
        )
    # The ram foot clevis on the mast front.
    _box(
        part,
        (r.ram_foot_x_m - _MAST / 2.0 + 0.020, 0.090, 0.032),
        ((_MAST / 2.0 - 0.010 + r.ram_foot_x_m) / 2.0, 0.0, r.ram_foot_z_m - 0.038),
        mats["body"],
        f"{prefix}_ram_bracket",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.052, 0.012, 0.070),
            (r.ram_foot_x_m, sign * 0.042, r.ram_foot_z_m),
            mats["steel"],
            f"{prefix}_ram_cheek_{index}",
        )
        _cyl(
            part,
            0.012,
            0.016,
            (r.ram_foot_x_m, sign * 0.030, r.ram_foot_z_m),
            mats["steel"],
            f"{prefix}_ram_pin_{index}",
            rpy=_Y_AXIS_RPY,
        )
    pump_x = -(_MAST / 2.0 + 0.026)
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.056, 0.014, 0.060),
            (pump_x, sign * 0.035, r.ram_foot_z_m + 0.060),
            mats["steel"],
            f"{prefix}_pump_cheek_{index}",
        )
    _box(
        part,
        (0.100, 0.084, 0.020),
        (pump_x + 0.024, 0.0, r.ram_foot_z_m + 0.024),
        mats["steel"],
        f"{prefix}_pump_body",
    )


def _frame_style_a_frame_base_build(model, r, mats) -> _Frame:
    """001 L161-L295: the long welded A-frame base and mast."""
    part = model.part(
        "frame_style__a_frame_base__frame",
        meta={"role": "frame", "construction": "long A-frame base"},
    )
    leg_span = r.leg_length_m
    _base_legs(part, r, mats, length=leg_span, prefix="a_frame")
    half = r.track_width_m / 2.0
    for index, sign in enumerate((-1.0, 1.0)):
        # A horizontal stiffener running from the cross beam out along each leg.
        _box(
            part,
            (r.leg_length_m * 0.44, 0.040, 0.040),
            (0.040 + r.leg_length_m * 0.22, sign * half * 0.62, r.leg_z_m + _LEG + 0.010),
            mats["body"],
            f"a_frame_brace_{index}",
        )
        _box(
            part,
            (0.040, half * 0.40 + 0.040, 0.040),
            (0.040, sign * half * 0.80, r.leg_z_m + _LEG + 0.010),
            mats["body"],
            f"a_frame_brace_tie_{index}",
        )
    _mast(part, r, mats, prefix="a_frame")
    return _Frame(part=part, stations=_caster_stations(r, leg_span), mast_top_z=r.pivot_z_m)


def _frame_style_compact_shop_base_build(model, r, mats) -> _Frame:
    """002 L146-L219: one short welded box frame with a low mast."""
    part = model.part(
        "frame_style__compact_shop_base__frame",
        meta={"role": "frame", "construction": "compact welded shop base"},
    )
    leg_span = r.leg_length_m * 0.80
    _base_legs(part, r, mats, length=leg_span, prefix="compact")
    _box(
        part,
        (r.leg_length_m * 0.34, r.track_width_m + _LEG, 0.030),
        (r.leg_length_m * 0.30, 0.0, r.leg_z_m + _LEG + 0.010),
        mats["body"],
        "compact_deck",
    )
    _mast(part, r, mats, prefix="compact")
    return _Frame(part=part, stations=_caster_stations(r, leg_span), mast_top_z=r.pivot_z_m)


def _frame_style_counterweight_base_build(model, r, mats) -> _Frame:
    """counterweight fork L165-L335: a ballast box behind the mast."""
    part = model.part(
        "frame_style__counterweight_base__frame",
        meta={"role": "frame", "construction": "ballasted base"},
    )
    leg_span = r.leg_length_m
    _base_legs(part, r, mats, length=leg_span, prefix="ballast")
    # The ballast stack is capped by the pump-handle sweep: the bar strokes down
    # over the box, and its clearance is set by the mast height that carries the
    # pump pivot, so a low mast gets a lower ballast box rather than a clash.
    box_bottom = r.leg_z_m + 0.005
    box_top = r.leg_z_m + min(0.155, 0.2 * r.mast_height_m - 0.014)
    _box(
        part,
        (0.170, r.track_width_m * 0.86, box_top - box_bottom),
        (-0.120, 0.0, 0.5 * (box_bottom + box_top)),
        mats["steel"],
        "counterweight_box",
    )
    _box(
        part,
        (0.190, _LEG, _LEG),
        (-0.070, 0.0, r.leg_z_m + _LEG / 2.0 - 0.004),
        mats["body"],
        "rear_beam",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.150, 0.030, 0.030),
            (-0.090, sign * r.track_width_m * 0.30, box_top - 0.012),
            mats["body"],
            f"ballast_strap_{index}",
        )
    _mast(part, r, mats, prefix="ballast")
    return _Frame(part=part, stations=_caster_stations(r, leg_span), mast_top_z=r.pivot_z_m)


def _frame_style_foldable_shop_base_build(model, r, mats) -> _Frame:
    """foldable fork L162-L314: short stowable legs and a braced mast strut."""
    part = model.part(
        "frame_style__foldable_shop_base__frame",
        meta={"role": "frame", "construction": "folding shop base"},
    )
    leg_span = r.leg_length_m * 0.74
    _base_legs(part, r, mats, length=leg_span, prefix="folding")
    # The fold hinge lugs and the diagonal mast strut of the folding frame.
    for index, sign in enumerate((-1.0, 1.0)):
        _cyl(
            part,
            0.020,
            0.030,
            (r.leg_length_m * 0.30, sign * r.track_width_m / 2.0, r.leg_z_m + _LEG / 2.0),
            mats["steel"],
            f"fold_lug_{index}",
            rpy=_Y_AXIS_RPY,
        )
    strut_len = math.hypot(r.leg_length_m * 0.42, (r.pivot_z_m - r.leg_z_m) * 0.52)
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (strut_len, 0.036, 0.036),
            (
                r.leg_length_m * 0.21,
                sign * (r.track_width_m / 2.0 - 0.020),
                r.leg_z_m + (r.pivot_z_m - r.leg_z_m) * 0.26 + 0.020,
            ),
            mats["body"],
            f"mast_strut_{index}",
            rpy=(0.0, math.atan2((r.pivot_z_m - r.leg_z_m) * 0.52, r.leg_length_m * 0.42), 0.0),
        )
    _mast(part, r, mats, prefix="folding")
    return _Frame(part=part, stations=_caster_stations(r, leg_span), mast_top_z=r.pivot_z_m)


def _stabilizer_fixed_stance_build(model, r, mats, frame: _Frame) -> None:
    """001/002: the base stands on its own legs and casters, with no outriggers."""

    return None


def _stabilizer_swing_out_outriggers_build(model, r, mats, frame: _Frame) -> None:
    """outrigger fork L152-L221: swing-out legs that widen any base's footprint.

    The brackets bolt to the outer face of the leg run, outboard of every base
    member (braces, ballast straps, fold lugs and mast struts stay inboard), so
    the same stabilizer mounts on every frame candidate.
    """

    part = frame.part
    half = r.track_width_m / 2.0
    for index, sign in enumerate((-1.0, 1.0)):
        pivot_x = 0.044
        pivot = (pivot_x, sign * (half + 0.076), r.leg_z_m + 0.026)
        _box(
            part,
            (0.050, 0.076, 0.020),
            (pivot_x, sign * (half + 0.038), r.leg_z_m + 0.0005),
            mats["body"],
            f"stabilizer__swing_out_outriggers__bracket_{index}",
        )
        _cyl(
            part,
            0.020,
            0.014,
            (pivot[0], pivot[1], pivot[2] - 0.019),
            mats["steel"],
            f"stabilizer__swing_out_outriggers__seat_{index}",
        )
        leg = model.part(
            f"stabilizer__swing_out_outriggers__outrigger_{index}",
            meta={"role": "outrigger", "index": index},
        )
        reach = r.leg_length_m * 0.40
        _cyl(leg, 0.014, 0.030, (0.0, 0.0, 0.0), mats["steel"], "outrigger_eye")
        _box(
            leg,
            (reach, 0.040, 0.040),
            (reach / 2.0 + 0.014, 0.0, 0.0),
            mats["body"],
            "outrigger_arm",
        )
        _cyl(leg, 0.026, 0.040, (reach + 0.014, 0.0, -0.018), mats["poly"], "outrigger_foot")
        _spin_joint(
            model,
            part,
            leg,
            name=f"stabilizer__swing_out_outriggers__outrigger_{index}__swing",
            point=pivot,
            axis=(0.0, 0.0, 1.0),
            radial=(0.0, sign, 0.0),
            child_radial=(1.0, 0.0, 0.0),
            radius=0.014,
            joint_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=120.0, velocity=0.8, lower=-1.10, upper=0.0),
            meta={"mechanism": "outrigger swing"},
        )


_STABILIZER_BUILDERS = {
    "fixed_stance": _stabilizer_fixed_stance_build,
    "swing_out_outriggers": _stabilizer_swing_out_outriggers_build,
}


_FRAME_BUILDERS = {
    "a_frame_base": _frame_style_a_frame_base_build,
    "compact_shop_base": _frame_style_compact_shop_base_build,
    "counterweight_base": _frame_style_counterweight_base_build,
    "foldable_shop_base": _frame_style_foldable_shop_base_build,
}


# --------------------------------------------------------------------------- #
# boom_style candidates
# --------------------------------------------------------------------------- #
def _boom_root(model, r, mats, frame: _Frame, candidate: str, *, length: float):
    """The luffing boom section pinned at the mast top."""
    part = model.part(
        f"boom_style__{candidate}__boom",
        meta={"role": "boom", "construction": "luffing boom"},
    )
    _cyl(part, 0.026, _BOOM + 0.024, (0.0, 0.0, 0.0), mats["steel"], "boom_eye", rpy=_Y_AXIS_RPY)
    neck_x1 = _MAST / 2.0 + 0.012
    _box(
        part,
        (neck_x1, _BOOM - 0.006, _BOOM - 0.006),
        (neck_x1 / 2.0, 0.0, 0.0),
        mats["body"],
        "boom_neck",
    )
    _hollow_section(
        part,
        mats,
        x0=_MAST / 2.0 + 0.008,
        x1=length,
        y=0.0,
        z=0.0,
        section=_BOOM,
        wall=_WALL,
        material=mats["body"],
        prefix="boom_section",
    )
    # The ram eye lug under the boom.
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.060, 0.012, 0.056),
            (r.ram_boom_x_m, sign * 0.030, -_BOOM / 2.0 - 0.020),
            mats["steel"],
            f"ram_lug_{index}",
        )
    _cyl(
        part,
        0.012,
        0.060,
        (r.ram_boom_x_m, 0.0, -_BOOM / 2.0 - 0.034),
        mats["steel"],
        "ram_lug_pin",
        rpy=_Y_AXIS_RPY,
    )
    joint = _spin_joint(
        model,
        frame.part,
        part,
        name=f"boom_style__{candidate}__luff",
        point=(0.0, 0.0, r.pivot_z_m),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.026,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(
            effort=9000.0, velocity=0.35, lower=-r.boom_drop_rad, upper=r.boom_rise_rad
        ),
        meta={"mechanism": "boom luff", "positive_motion": "raises the boom"},
    )
    return part, joint


def _boom_style_single_extension_build(model, r, mats, frame) -> list[str]:
    """001 L296-L410: one boom with a single sliding extension and the hook."""
    root_len = r.boom_length_m * 0.66
    boom, luff = _boom_root(model, r, mats, frame, "single_extension", length=root_len)
    ext = model.part(
        "boom_style__single_extension__extension",
        meta={"role": "boom_extension", "construction": "sliding boom extension"},
    )
    ext_len = r.boom_length_m * 0.46
    section = _BOOM - 2.0 * _WALL - _SLIDE_FIT
    _hollow_section(
        ext,
        mats,
        x0=0.0,
        x1=ext_len,
        y=0.0,
        z=0.0,
        section=section,
        wall=0.008,
        material=mats["steel"],
        prefix="ext_section",
    )
    _box(ext, (0.040, section, section), (ext_len, 0.0, 0.0), mats["steel"], "ext_nose")
    travel = ext_len * 0.42
    name = "boom_style__single_extension__slide"
    model.articulation(
        name,
        ArticulationType.PRISMATIC,
        parent=boom,
        child=ext,
        origin=Origin(xyz=(root_len - ext_len * 0.55, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=16000.0, velocity=0.2, lower=0.0, upper=travel),
        motion_properties=MotionProperties(damping=3.0, friction=1.5),
        meta={"mechanism": "boom extension"},
    )
    hook = _add_hook(model, r, mats, ext, ext_len, section=section)
    return [luff, name, hook]


def _boom_style_telescoping_stages_build(model, r, mats, frame) -> list[str]:
    """telescoping fork L373-L479: a chain of prismatic boom stages."""
    root_len = r.boom_length_m * 0.60
    boom, luff = _boom_root(model, r, mats, frame, "telescoping_stages", length=root_len)
    joints = [luff]
    parent = boom
    section = _BOOM
    parent_len = root_len
    stage_len = r.boom_length_m * 0.40
    for index in range(2):
        section = section - 2.0 * (_WALL if index == 0 else 0.007) - _SLIDE_FIT
        stage = model.part(
            f"boom_style__telescoping_stages__stage_{index}",
            meta={"role": "boom_extension", "index": index},
        )
        _hollow_section(
            stage,
            mats,
            x0=0.0,
            x1=stage_len,
            y=0.0,
            z=0.0,
            section=section,
            wall=0.007,
            material=mats["steel"] if index else mats["body"],
            prefix=f"stage_{index}_section",
        )
        name = f"boom_style__telescoping_stages__stage_{index}__slide"
        model.articulation(
            name,
            ArticulationType.PRISMATIC,
            parent=parent,
            child=stage,
            origin=Origin(xyz=(parent_len - stage_len * 0.62, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=16000.0, velocity=0.2, lower=0.0, upper=stage_len * 0.52
            ),
            motion_properties=MotionProperties(damping=3.0, friction=1.5),
            meta={"mechanism": "boom extension"},
        )
        joints.append(name)
        parent = stage
        parent_len = stage_len
        stage_len = stage_len * 0.92
    _box(parent, (0.036, section, section), (parent_len, 0.0, 0.0), mats["steel"], "stage_nose")
    joints.append(_add_hook(model, r, mats, parent, parent_len, section=section))
    return joints


def _boom_style_knuckle_jib_build(model, r, mats, frame) -> list[str]:
    """knuckle fork L374-L593: a folding jib on its own hydraulic ram."""
    root_len = r.boom_length_m * 0.58
    boom, luff = _boom_root(model, r, mats, frame, "knuckle_jib", length=root_len - 0.034)
    # The knuckle clevis at the boom nose.
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            boom,
            (0.070, 0.013, 0.080),
            (root_len - 0.014, sign * ((_BOOM - 0.006) / 2.0 + 0.0075), 0.0),
            mats["steel"],
            f"knuckle_cheek_{index}",
        )
    jib_eye_half = (_BOOM - 0.006) / 2.0
    for index, sign in enumerate((-1.0, 1.0)):
        _cyl(
            boom,
            0.020,
            0.018,
            (root_len - 0.006, sign * (jib_eye_half + 0.007), 0.0),
            mats["steel"],
            f"knuckle_pin_{index}",
            rpy=_Y_AXIS_RPY,
        )
    jib = model.part(
        "boom_style__knuckle_jib__jib",
        meta={"role": "boom_extension", "construction": "folding secondary jib"},
    )
    jib_len = r.boom_length_m * 0.44
    section = _BOOM - 0.012
    _cyl(jib, 0.020, _BOOM - 0.006, (0.0, 0.0, 0.0), mats["steel"], "jib_eye", rpy=_Y_AXIS_RPY)
    _hollow_section(
        jib,
        mats,
        x0=0.014,
        x1=jib_len,
        y=0.0,
        z=0.0,
        section=section,
        wall=0.009,
        material=mats["steel"],
        prefix="jib_section",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            jib,
            (0.052, 0.011, 0.048),
            (jib_len * 0.30, sign * 0.026, section / 2.0 + 0.018),
            mats["steel"],
            f"jib_lug_{index}",
        )
    _cyl(
        jib,
        0.011,
        0.052,
        (jib_len * 0.30, 0.0, section / 2.0 + 0.032),
        mats["steel"],
        "jib_lug_pin",
        rpy=_Y_AXIS_RPY,
    )
    knuckle = _spin_joint(
        model,
        boom,
        jib,
        name="boom_style__knuckle_jib__knuckle",
        point=(root_len - 0.006, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.020,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=7000.0, velocity=0.35, lower=-0.85, upper=0.10),
        meta={"mechanism": "jib knuckle"},
    )
    jib_barrel = model.part(
        "boom_style__knuckle_jib__jib_cylinder",
        meta={"role": "jib_ram", "construction": "jib cylinder"},
    )
    barrel_len = r.boom_length_m * 0.20
    _cyl(jib_barrel, 0.019, 0.018, (0.0, 0.0, 0.007), mats["steel"], "jib_barrel_foot")
    _hollow_tube(
        jib_barrel,
        mats,
        z0=0.014,
        z1=barrel_len,
        x=0.0,
        y=0.0,
        radius=0.019,
        wall=0.008,
        segments=8,
        material=mats["body"],
        prefix="jib_barrel_wall",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            boom,
            (0.056, 0.012, 0.056),
            (root_len * 0.42, sign * 0.028, _BOOM / 2.0 + 0.024),
            mats["steel"],
            f"jib_ram_lug_{index}",
        )
    for index, sign in enumerate((-1.0, 1.0)):
        _cyl(
            boom,
            0.012,
            0.014,
            (root_len * 0.42, sign * 0.027, _BOOM / 2.0 + 0.042),
            mats["steel"],
            f"jib_ram_lug_pin_{index}",
            rpy=_Y_AXIS_RPY,
        )
    jib_ram = _spin_joint(
        model,
        boom,
        jib_barrel,
        name="boom_style__knuckle_jib__jib_ram_foot",
        point=(root_len * 0.42, 0.0, _BOOM / 2.0 + 0.042),
        axis=(0.0, 1.0, 0.0),
        radial=(math.cos(0.34), 0.0, math.sin(0.34)),
        child_radial=(0.0, 0.0, 1.0),
        radius=0.022,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=6000.0, velocity=0.3, lower=-0.10, upper=0.10),
        meta={"mechanism": "jib ram foot"},
    )
    jib_rod = model.part(
        "boom_style__knuckle_jib__jib_rod",
        meta={"role": "jib_ram_rod", "construction": "jib ram rod"},
    )
    _cyl(jib_rod, 0.0142, barrel_len * 0.72, (0.0, 0.0, barrel_len * 0.36), mats["rod"], "jib_rod")
    _cyl(jib_rod, 0.019, 0.014, (0.0, 0.0, barrel_len * 0.72), mats["steel"], "jib_rod_eye")
    jib_slide = "boom_style__knuckle_jib__jib_ram_extend"
    model.articulation(
        jib_slide,
        ArticulationType.PRISMATIC,
        parent=jib_barrel,
        child=jib_rod,
        origin=Origin(xyz=(0.0, 0.0, barrel_len * 0.24)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=10000.0, velocity=0.12, lower=0.0, upper=barrel_len * 0.34
        ),
        motion_properties=MotionProperties(damping=3.0, friction=1.5),
        meta={"mechanism": "jib ram extension"},
    )
    hook = _add_hook(model, r, mats, jib, jib_len, section=section)
    return [luff, knuckle, jib_ram, jib_slide, hook]


_BOOM_BUILDERS = {
    "single_extension": _boom_style_single_extension_build,
    "telescoping_stages": _boom_style_telescoping_stages_build,
    "knuckle_jib": _boom_style_knuckle_jib_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_industrial_crane_featuring_advanced_hydraulic(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_industrial_crane_featuring_advanced_hydraulic",
            "identified_object": "mobile hydraulic shop crane",
            "slot_choices": slot_choices_for_config(r),
            "source_layout": (
                "a wheeled frame and mast, a luffing boom on a hydraulic ram, a hand pump "
                "and a swivel hook"
            ),
        },
    )
    mats = _materials(model)
    frame = _FRAME_BUILDERS[r.frame_style](model, r, mats)
    _STABILIZER_BUILDERS[r.stabilizer](model, r, mats, frame)
    _build_casters(model, r, mats, frame)
    _build_ram(model, r, mats, frame)
    _BOOM_BUILDERS[r.boom_style](model, r, mats, frame)
    return model


# --------------------------------------------------------------------------- #
# Author tests / category anchors
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def run_pictureX_0611_industrial_crane_featuring_advanced_hydraulic_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "frame")
    casters = _parts_by_role(model, "caster")
    wheels = _parts_by_role(model, "wheel")
    booms = _parts_by_role(model, "boom")
    rams = _parts_by_role(model, "ram")
    hooks = _parts_by_role(model, "hook")
    pumps = _parts_by_role(model, "pump")

    ctx.check(
        "category_anchor: one wheeled frame carries the crane",
        len(frames) == 1,
        details=f"frames={[part.name for part in frames]}",
    )
    ctx.check(
        "category_anchor: N swivel caster stations roll the base",
        len(casters) == r.caster_count and len(wheels) == r.caster_count,
        details=f"casters={len(casters)}, wheels={len(wheels)}, expected={r.caster_count}",
    )
    outriggers = _parts_by_role(model, "outrigger")
    expected_outriggers = 2 if r.stabilizer == "swing_out_outriggers" else 0
    ctx.check(
        "category_anchor: the stabilizer matches the selected stance",
        len(outriggers) == expected_outriggers,
        details=f"stabilizer={r.stabilizer}, outriggers={[p.name for p in outriggers]}",
    )
    if outriggers:
        swing = next(
            joint
            for joint in model.articulations
            if joint.meta.get("mechanism") == "outrigger swing"
        )
        # The arm rests deployed (q=0) and swings back along the base at its
        # lower limit, so stowing it must pull the footprint back in.
        deployed = ctx.part_world_aabb(model.get_part(swing.child))
        with ctx.pose({swing: swing.motion_limits.lower}):
            stowed = ctx.part_world_aabb(model.get_part(swing.child))
        narrowed = None
        if stowed is not None and deployed is not None:
            narrowed = max(abs(deployed[0][1]), abs(deployed[1][1])) - max(
                abs(stowed[0][1]), abs(stowed[1][1])
            )
        ctx.check(
            "swinging an outrigger out really widens the footprint",
            narrowed is not None and narrowed > 0.020,
            details=f"deployed={deployed}, stowed={stowed}, narrowed={narrowed}",
        )

    ctx.check(
        "category_anchor: a luffing boom pivots on the mast",
        len(booms) == 1,
        details=f"booms={[part.name for part in booms]}",
    )
    ctx.check(
        "category_anchor: a hydraulic ram and its hand pump drive the boom",
        len(rams) == 1 and len(pumps) == 1,
        details=f"rams={[p.name for p in rams]}, pumps={[p.name for p in pumps]}",
    )
    ctx.check(
        "category_anchor: a swivel hook hangs at the boom tip",
        len(hooks) == 1,
        details=f"hooks={[part.name for part in hooks]}",
    )

    luff = next(
        joint for joint in model.articulations if joint.meta.get("mechanism") == "boom luff"
    )
    boom = booms[0]
    rest = ctx.part_world_aabb(boom)
    with ctx.pose({luff: luff.motion_limits.upper}):
        raised = ctx.part_world_aabb(boom)
    lifted = None
    if rest is not None and raised is not None:
        lifted = raised[1][2] - rest[1][2]
    ctx.check(
        "category_anchor: luffing the boom really raises its tip",
        lifted is not None and lifted > 0.020,
        details=f"rest={rest}, raised={raised}, lift={lifted}",
    )

    ram_slide = next(
        joint for joint in model.articulations if joint.meta.get("mechanism") == "ram extension"
    )
    rod = model.get_part(ram_slide.child)
    low = ctx.part_world_aabb(rod)
    with ctx.pose({ram_slide: ram_slide.motion_limits.upper}):
        high = ctx.part_world_aabb(rod)
    ctx.check(
        "the ram rod really extends out of its barrel",
        low is not None
        and high is not None
        and high[1][2] - low[1][2] > 0.4 * ram_slide.motion_limits.upper,
        details=f"retracted={low}, extended={high}",
    )

    extensions = [
        joint for joint in model.articulations if joint.meta.get("mechanism") == "boom extension"
    ]
    expected = {"single_extension": 1, "telescoping_stages": 2, "knuckle_jib": 0}[r.boom_style]
    ctx.check(
        "category_anchor: the boom reaches out the way its family does",
        len(extensions) == expected,
        details=f"extension joints={[joint.name for joint in extensions]}",
    )
    if r.boom_style == "knuckle_jib":
        knuckle = next(
            joint for joint in model.articulations if joint.meta.get("mechanism") == "jib knuckle"
        )
        ctx.check(
            "category_anchor: the knuckle jib folds on a real revolute joint",
            knuckle.articulation_type == ArticulationType.REVOLUTE,
            details=f"knuckle={knuckle.name}",
        )

    ctx.check(
        "the base is long enough for its caster stations",
        r.leg_length_m >= 0.24 * float(max(r.caster_count // 2 - 1, 0)) + 0.34,
        details=f"leg={r.leg_length_m:.4f}, casters={r.caster_count}",
    )
    ctx.check(
        "the mast lifts the boom pin above the wheels",
        r.pivot_z_m > 2.0 * r.caster_radius_m + 0.30,
        details=f"pivot_z={r.pivot_z_m:.4f}, caster_r={r.caster_radius_m:.4f}",
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "tallest_longest_knuckle_six_casters",
        {
            "frame_style": "a_frame_base",
            "boom_style": "knuckle_jib",
            "hook_style": "chain_hook",
            "caster_count": 6,
            "mast_height_m": 1.15,
            "leg_length_m": 1.40,
            "boom_length_m": 1.50,
            "track_width_m": 0.90,
            "caster_radius_m": 0.075,
        },
        reason="the tallest mast with the longest knuckle boom on six casters",
    ),
    corner_case(
        "smallest_compact_single_extension",
        {
            "frame_style": "compact_shop_base",
            "boom_style": "single_extension",
            "hook_style": "ball_hook",
            "caster_count": 4,
            "mast_height_m": 0.60,
            "leg_length_m": 0.70,
            "boom_length_m": 0.70,
            "track_width_m": 0.44,
            "caster_radius_m": 0.036,
        },
        reason="the smallest compact crane where the ram and the boom crowd the mast",
    ),
    corner_case(
        "outriggers_six_casters_telescoping",
        {
            "frame_style": "a_frame_base",
            "stabilizer": "swing_out_outriggers",
            "boom_style": "telescoping_stages",
            "hook_style": "chain_hook",
            "caster_count": 6,
            "mast_height_m": 0.90,
            "leg_length_m": 1.40,
            "boom_length_m": 1.50,
            "track_width_m": 0.44,
            "caster_radius_m": 0.075,
        },
        reason="outriggers swinging out of the narrowest track with six caster stations",
    ),
    corner_case(
        "counterweight_short_legs_telescoping",
        {
            "frame_style": "counterweight_base",
            "boom_style": "telescoping_stages",
            "hook_style": "ball_hook",
            "caster_count": 4,
            "mast_height_m": 1.15,
            "leg_length_m": 0.70,
            "boom_length_m": 1.50,
            "track_width_m": 0.90,
            "caster_radius_m": 0.036,
        },
        reason="the heaviest ballast on the shortest legs under the longest boom",
    ),
    corner_case(
        "foldable_base_knuckle_min_mast",
        {
            "frame_style": "foldable_shop_base",
            "stabilizer": "swing_out_outriggers",
            "boom_style": "knuckle_jib",
            "hook_style": "chain_hook",
            "caster_count": 4,
            "mast_height_m": 0.60,
            "leg_length_m": 1.40,
            "boom_length_m": 0.70,
            "track_width_m": 0.44,
            "caster_radius_m": 0.075,
        },
        reason="the folding strut and the jib ram share the lowest mast",
    ),
    corner_case(
        "outriggers_wide_track_single_extension",
        {
            "frame_style": "counterweight_base",
            "stabilizer": "swing_out_outriggers",
            "boom_style": "single_extension",
            "hook_style": "ball_hook",
            "caster_count": 4,
            "mast_height_m": 0.60,
            "leg_length_m": 0.70,
            "boom_length_m": 1.50,
            "track_width_m": 0.90,
            "caster_radius_m": 0.036,
        },
        reason="the widest track with the longest reach on the shortest base",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_industrial_crane_featuring_advanced_hydraulic",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_industrial_crane_featuring_advanced_hydraulic_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
