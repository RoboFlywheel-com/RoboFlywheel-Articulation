# SPDX-License-Identifier: Apache-2.0

"""Self-contained demonstration-gyroscope template.

Every rotation in this category has to pass through one point — the gimbal
centre — so the whole object is authored in a chain of *ring-local* frames that
make that structural, not incidental:

* a gimbal member's own trunnion (hold) axis is its local **+Z**, and its pole
  pins sit at local +-Z;
* the axis it hands to its child is its local **+X**;
* a pure gimbal ring and an ``opposed_bearings`` carrier therefore lie in their
  local **XZ** plane, which is the only plane that contains both axes, while a
  ``bearing_spider`` carrier lies in its local **YZ** plane because there the
  spin axis is the ring's own normal;
* the rotor's spin axis is its local **+Z** with the flywheel in local XY.

Every joint is solved with ``mate_axes`` between an ``AxisInterface`` on the
parent and one on the child, both anchored at their own frame origin, and is
registered with ``register_interface_mate``.  Because both interface points are
the gimbal centre, every joint after the base has origin ``(0, 0, 0)`` exactly,
and consecutive joint axes come out mutually orthogonal by construction.

Seven slots vary without touching that chain: ``support_base`` (weighted cast
pedestal, slender tapered column, splayed tripod, or a wall bracket that turns
the first axis horizontal), ``ring_stack`` (two nested rings and three joints,
or three nested rings and four joints with an extra roll axis), ``ring_section``
(flat machined band with an edge bead, round tube hoop with bearing seat rings,
or a rectangular window carrier frame for the innermost member),
``spindle_support`` (two opposed in-plane pole bearings on a through axle, or a
central race carried on a spider across the bore), ``rotor_form`` (crowned drum,
shaped disc with a proud perimeter band, spoked inertia rim, or plain bevelled
solid disc), ``index_hardware`` (plain pole trunnion or a slender pointer mast)
and ``gimbal_motion`` (free swing or a mechanically limited swing with real end
stops).

Deliberate deviations from the source pool, also recorded in the SourceMap:

1. Every shaft/bearing fit is a real bore on a ``BEARING_FIT`` running clearance
   instead of the pool's solid-into-solid ``ctx.allow_overlap``.
2. The rotor axle is capped inside the innermost member's envelope.  Family A's
   205 mm through-axle leaves the outer ring and only survives in the source
   because that record's rest pose keeps the tilt joint far from zero.
3. The ``bearing_spider`` struts run from short rim posts down to the race
   instead of lying flat across the bore, so the spider can never reach outside
   the carrier's own envelope at any rotor size.
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
    LatheGeometry,
    MotionLimits,
    MotionProperties,
    Origin,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    TorusGeometry,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    register_interface_mate,
)

SupportBase = Literal["weighted_pedestal", "slender_column", "tripod_legs", "wall_bracket"]
RingStack = Literal["two_ring_gimbal", "three_ring_gimbal"]
RingSection = Literal["flat_band", "tubular_hoop", "carrier_frame"]
SpindleSupport = Literal["opposed_bearings", "bearing_spider"]
RotorForm = Literal["crowned_drum", "shaped_disc", "spoked_rim", "solid_disc"]
IndexHardware = Literal["plain_trunnion", "pointer_mast"]
GimbalMotion = Literal["free_swing", "limited_stops"]
PaletteStyle = Literal["blackened_iron", "aged_steel", "dark_chrome", "brass_accent"]

SUPPORT_BASES: tuple[SupportBase, ...] = (
    "weighted_pedestal",
    "slender_column",
    "tripod_legs",
    "wall_bracket",
)
RING_STACKS: tuple[RingStack, ...] = ("two_ring_gimbal", "three_ring_gimbal")
RING_SECTIONS: tuple[RingSection, ...] = ("flat_band", "tubular_hoop", "carrier_frame")
SPINDLE_SUPPORTS: tuple[SpindleSupport, ...] = ("opposed_bearings", "bearing_spider")
ROTOR_FORMS: tuple[RotorForm, ...] = (
    "crowned_drum",
    "shaped_disc",
    "spoked_rim",
    "solid_disc",
)
INDEX_HARDWARES: tuple[IndexHardware, ...] = ("plain_trunnion", "pointer_mast")
GIMBAL_MOTIONS: tuple[GimbalMotion, ...] = ("free_swing", "limited_stops")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "blackened_iron",
    "aged_steel",
    "dark_chrome",
    "brass_accent",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("support_base", SUPPORT_BASES),
        component_slot("ring_stack", RING_STACKS),
        component_slot("ring_section", RING_SECTIONS),
        component_slot("spindle_support", SPINDLE_SUPPORTS),
        component_slot("rotor_form", ROTOR_FORMS),
        component_slot("index_hardware", INDEX_HARDWARES),
        component_slot("gimbal_motion", GIMBAL_MOTIONS),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # Family A colourway (001.png): blackened cast iron, aged steel, chrome.
    "blackened_iron": {
        "body": (0.075, 0.070, 0.064, 1.0),
        "ring": (0.105, 0.105, 0.100, 1.0),
        "edge": (0.190, 0.200, 0.200, 1.0),
        "bright": (0.72, 0.75, 0.76, 1.0),
        "bearing": (0.43, 0.45, 0.45, 1.0),
        "accent": (0.035, 0.035, 0.032, 1.0),
    },
    "aged_steel": {
        "body": (0.150, 0.150, 0.145, 1.0),
        "ring": (0.245, 0.250, 0.245, 1.0),
        "edge": (0.330, 0.340, 0.340, 1.0),
        "bright": (0.640, 0.665, 0.670, 1.0),
        "bearing": (0.400, 0.415, 0.420, 1.0),
        "accent": (0.310, 0.025, 0.045, 1.0),
    },
    # Family B colourway (002.png): dark chrome hoops, brushed flywheel.
    "dark_chrome": {
        "body": (0.035, 0.038, 0.043, 1.0),
        "ring": (0.220, 0.230, 0.240, 1.0),
        "edge": (0.300, 0.310, 0.315, 1.0),
        "bright": (0.480, 0.500, 0.510, 1.0),
        "bearing": (0.560, 0.580, 0.560, 1.0),
        "accent": (0.310, 0.025, 0.045, 1.0),
    },
    "brass_accent": {
        "body": (0.090, 0.085, 0.075, 1.0),
        "ring": (0.200, 0.190, 0.160, 1.0),
        "edge": (0.300, 0.270, 0.180, 1.0),
        "bright": (0.560, 0.575, 0.580, 1.0),
        "bearing": (0.480, 0.420, 0.220, 1.0),
        "accent": (0.120, 0.100, 0.060, 1.0),
    },
}


# --- fixed manufacturing constants (surface detail, not core/raw) -----------------
BEARING_FIT = 0.0006  # radial running clearance in every bore, m
BOSS_WALL = 0.0040  # bearing sleeve wall over its bore, m
CAP_T = 0.0030  # retaining cap thickness, m
POLE_INSET = 0.0040  # how far a pole pin starts inside its own member, m
PIN_BACKOFF = 0.0040  # how far a pole pin stops short of its sleeve end, m
BASE_STANDOFF = 0.0050  # clear gap between a ring pole and the base bearing, m
RING_SEG = 84  # revolution segments for a gimbal ring
BOSS_SEG = 40  # revolution segments for a bearing sleeve
DISC_SEG = 72  # revolution segments for a flywheel
SPOKE_COUNT = 6  # radial spokes on the spoked rim (source value)
ROTOR_ENVELOPE_FACTOR = 1.12  # rotor reach allowance over the flywheel radius
MAST_RATIO = 0.52  # pointer mast length as a fraction of the outer radius
STOP_MARGIN = 0.14  # extra arc past a joint limit before the stop block, rad

# Normalised lathe profiles, (radius / R, z / R), read off the source records.
CROWNED_DRUM_PROFILE = (
    (0.0000, -0.3273),
    (0.2545, -0.3273),
    (0.7818, -0.3091),
    (0.9273, -0.2545),
    (1.0000, -0.1273),
    (1.0000, 0.1273),
    (0.9273, 0.2545),
    (0.7818, 0.3091),
    (0.2545, 0.3273),
    (0.0000, 0.3273),
)
SOLID_DISC_PROFILE = (
    (0.0000, -0.3091),
    (0.8364, -0.3091),
    (0.9455, -0.2727),
    (1.0000, -0.2000),
    (1.0000, 0.2000),
    (0.9455, 0.2727),
    (0.8364, 0.3091),
    (0.0000, 0.3091),
)
SHAPED_DISC_PROFILE = (
    (0.0000, -0.0619),
    (0.2062, -0.0619),
    (0.4639, -0.0495),
    (0.8041, -0.0464),
    (0.9072, -0.0722),
    (0.9691, -0.0619),
    (1.0000, -0.0206),
    (1.0000, 0.0309),
    (0.9485, 0.0722),
    (0.6289, 0.0670),
    (0.3093, 0.0464),
    (0.0000, 0.0464),
)
# Weighted cast base (001) and slender column (002), (radius / R, z / H).
WEIGHTED_BASE_PROFILE = (
    (0.000, 0.000),
    (0.667, 0.000),
    (0.869, 0.096),
    (0.980, 0.250),
    (1.000, 0.385),
    (0.960, 0.558),
    (0.808, 0.750),
    (0.525, 0.904),
    (0.303, 1.000),
    (0.000, 1.000),
)
SLENDER_COLUMN_PROFILE = (
    (0.000, 0.000),
    (0.833, 0.000),
    (0.967, 0.036),
    (1.000, 0.086),
    (0.933, 0.150),
    (0.717, 0.186),
    (0.533, 0.250),
    (0.417, 0.429),
    (0.333, 0.707),
    (0.267, 0.864),
    (0.200, 1.000),
    (0.000, 1.000),
)
# Rotor axial reach on the -spin side, as a fraction of the flywheel radius.
ROTOR_BACK_REACH = {
    "crowned_drum": 0.36,
    "solid_disc": 0.34,
    "shaped_disc": 0.11,
    "spoked_rim": 0.10,
}
ROTOR_FRONT_REACH = {
    "crowned_drum": 0.36,
    "solid_disc": 0.34,
    "shaped_disc": 0.40,
    "spoked_rim": 0.36,
}


@dataclass(frozen=True)
class Config:
    support_base: SupportBase = "weighted_pedestal"
    ring_stack: RingStack = "two_ring_gimbal"
    ring_section: RingSection = "flat_band"
    spindle_support: SpindleSupport = "opposed_bearings"
    rotor_form: RotorForm = "crowned_drum"
    index_hardware: IndexHardware = "plain_trunnion"
    gimbal_motion: GimbalMotion = "free_swing"
    outer_ring_radius_m: float | None = None
    ring_width_ratio: float | None = None
    rotor_radius_ratio: float | None = None
    gimbal_rise_m: float | None = None
    palette_style: PaletteStyle = "blackened_iron"
    name: str = "pictureX_0611_gyroscope_with_spinning_wheel_and_gimbal_rings"


@dataclass(frozen=True)
class ResolvedConfig:
    support_base: SupportBase
    ring_stack: RingStack
    ring_section: RingSection
    spindle_support: SpindleSupport
    rotor_form: RotorForm
    index_hardware: IndexHardware
    gimbal_motion: GimbalMotion
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    outer_ring_radius_m: float
    ring_width_ratio: float
    rotor_radius_ratio: float
    gimbal_rise_m: float
    # derived
    ring_count: int
    mid_ring_count: int
    ring_gap_m: float
    ring_outer_m: tuple[float, ...]
    ring_inner_m: tuple[float, ...]
    ring_thick_m: tuple[float, ...]
    pole_pin_radius_m: tuple[float, ...]
    pole_reach_m: tuple[float, ...]
    carrier_half_pole_m: float
    carrier_half_spin_m: float
    carrier_bar_m: float
    carrier_depth_m: float
    spin_seat_m: float
    rotor_bore_m: float
    rotor_clear_m: float
    flywheel_radius_m: float
    axle_radius_m: float
    axle_half_m: float
    race_offset_m: float
    race_len_m: float
    rotor_envelope_m: float
    gimbal_center_z_m: float
    mount_station_m: float
    housing_len_m: float
    housing_outer_m: float
    support_axis: tuple[float, float, float]
    support_radial: tuple[float, float, float]
    azimuth_limit_rad: float
    tilt_limit_rad: float
    stop_radius_m: float
    stop_block_half_rad: float
    stop_pin_half_rad: float
    stop_block_angle_rad: float
    mast_len_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x67_59_03_11)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        support_base=choices["support_base"],
        ring_stack=choices["ring_stack"],
        ring_section=choices["ring_section"],
        spindle_support=choices["spindle_support"],
        rotor_form=choices["rotor_form"],
        index_hardware=choices["index_hardware"],
        gimbal_motion=choices["gimbal_motion"],
        outer_ring_radius_m=round(rng.uniform(0.110, 0.160), 4),
        ring_width_ratio=round(rng.uniform(0.10, 0.17), 4),
        rotor_radius_ratio=round(rng.uniform(0.62, 0.88), 4),
        gimbal_rise_m=round(rng.uniform(0.075, 0.220), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"gyroscope_with_spinning_wheel_and_gimbal_rings_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "support_base": config.support_base,
            "ring_stack": config.ring_stack,
            "ring_section": config.ring_section,
            "spindle_support": config.spindle_support,
            "rotor_form": config.rotor_form,
            "index_hardware": config.index_hardware,
            "gimbal_motion": config.gimbal_motion,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if (
        config.outer_ring_radius_m is not None
        and not 0.110 <= float(config.outer_ring_radius_m) <= 0.160
    ):
        raise ValueError("outer_ring_radius_m must be in [0.110, 0.160]")
    if config.ring_width_ratio is not None and not 0.10 <= float(config.ring_width_ratio) <= 0.17:
        raise ValueError("ring_width_ratio must be in [0.10, 0.17]")
    if (
        config.rotor_radius_ratio is not None
        and not 0.62 <= float(config.rotor_radius_ratio) <= 0.88
    ):
        raise ValueError("rotor_radius_ratio must be in [0.62, 0.88]")
    if config.gimbal_rise_m is not None and not 0.075 <= float(config.gimbal_rise_m) <= 0.220:
        raise ValueError("gimbal_rise_m must be in [0.075, 0.220]")

    r_out = (
        _clamp(config.outer_ring_radius_m, 0.110, 0.160)
        if config.outer_ring_radius_m is not None
        else 0.132
    )
    width_ratio = (
        _clamp(config.ring_width_ratio, 0.10, 0.17)
        if config.ring_width_ratio is not None
        else 0.132
    )
    rotor_ratio = (
        _clamp(config.rotor_radius_ratio, 0.62, 0.88)
        if config.rotor_radius_ratio is not None
        else 0.760
    )
    rise = _clamp(config.gimbal_rise_m, 0.075, 0.220) if config.gimbal_rise_m is not None else 0.140

    ring_count = 3 if config.ring_stack == "three_ring_gimbal" else 2
    gap = max(0.014, 0.10 * r_out)
    width_scale = (1.0, 0.72, 0.55)

    outer: list[float] = []
    inner: list[float] = []
    thick: list[float] = []
    base_width = width_ratio * r_out
    cursor = r_out
    for index in range(ring_count):
        width = base_width * width_scale[index]
        outer.append(cursor)
        inner.append(cursor - width)
        thick.append(max(0.006, 0.58 * width))
        cursor = cursor - width - gap

    carrier = ring_count - 1
    is_carrier_frame = config.ring_section == "carrier_frame"
    spider = config.spindle_support == "bearing_spider"

    carrier_bar = max(0.0060, 0.13 * outer[carrier])
    carrier_depth = max(0.0060, 0.58 * (outer[carrier] - inner[carrier]))
    if spider:
        half_pole = 0.70 * outer[carrier]
        half_spin = 0.70 * outer[carrier]
    else:
        half_pole = 0.82 * outer[carrier]
        half_spin = 0.55 * outer[carrier]

    if is_carrier_frame:
        rotor_bore = min(half_pole, half_spin) - carrier_bar if spider else half_pole - carrier_bar
        pole_reach_carrier = half_pole
        spin_seat = half_spin - carrier_bar
    else:
        rotor_bore = inner[carrier]
        pole_reach_carrier = outer[carrier]
        spin_seat = inner[carrier]

    pole_reach = [outer[index] for index in range(ring_count)]
    pole_reach[carrier] = pole_reach_carrier

    pin_radius = [max(0.0035, 0.055 * r_out)]
    for index in range(1, ring_count):
        pin_radius.append(max(0.0030, 0.050 * outer[index]))

    rotor_clear = max(0.0040, 0.06 * rotor_bore)
    flywheel_r = rotor_ratio * (rotor_bore - rotor_clear) / ROTOR_ENVELOPE_FACTOR
    axle_r = _clamp(0.052 * flywheel_r, 0.0026, 0.0065)

    back = ROTOR_BACK_REACH[config.rotor_form] * flywheel_r
    front = ROTOR_FRONT_REACH[config.rotor_form] * flywheel_r
    race_len = max(0.010, 0.16 * outer[carrier])
    race_offset = -(back + 0.008 + 0.5 * race_len)
    if spider:
        axle_half = 0.0
        rotor_env = max(
            ROTOR_ENVELOPE_FACTOR * flywheel_r,
            abs(race_offset) + 0.5 * race_len + 0.004,
            front,
        )
    else:
        axle_half = spin_seat - PIN_BACKOFF
        rotor_env = max(ROTOR_ENVELOPE_FACTOR * flywheel_r, axle_half + 0.002, front, back)

    if config.support_base == "wall_bracket":
        support_axis = (0.0, -1.0, 0.0)
        support_radial = (0.0, 0.0, 1.0)
    else:
        support_axis = (0.0, 0.0, 1.0)
        support_radial = (1.0, 0.0, 0.0)

    mount_station = r_out + BASE_STANDOFF
    housing_len = max(0.016, 0.13 * r_out)
    housing_outer = pin_radius[0] + BEARING_FIT + 0.0065

    limited = config.gimbal_motion == "limited_stops"
    azimuth_limit = 1.00 if limited else math.pi
    tilt_limit = 0.75 if limited else 1.35

    stop_radius = housing_outer + 0.013
    stop_pin_r = 0.0035
    stop_block_half = math.atan2(0.0060, stop_radius)
    stop_pin_half = math.atan2(stop_pin_r, stop_radius)
    stop_block_angle = azimuth_limit + stop_pin_half + stop_block_half + STOP_MARGIN

    return ResolvedConfig(
        support_base=config.support_base,
        ring_stack=config.ring_stack,
        ring_section=config.ring_section,
        spindle_support=config.spindle_support,
        rotor_form=config.rotor_form,
        index_hardware=config.index_hardware,
        gimbal_motion=config.gimbal_motion,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        outer_ring_radius_m=r_out,
        ring_width_ratio=width_ratio,
        rotor_radius_ratio=rotor_ratio,
        gimbal_rise_m=rise,
        ring_count=ring_count,
        mid_ring_count=ring_count - 2,
        ring_gap_m=gap,
        ring_outer_m=tuple(outer),
        ring_inner_m=tuple(inner),
        ring_thick_m=tuple(thick),
        pole_pin_radius_m=tuple(pin_radius),
        pole_reach_m=tuple(pole_reach),
        carrier_half_pole_m=half_pole,
        carrier_half_spin_m=half_spin,
        carrier_bar_m=carrier_bar,
        carrier_depth_m=carrier_depth,
        spin_seat_m=spin_seat,
        rotor_bore_m=rotor_bore,
        rotor_clear_m=rotor_clear,
        flywheel_radius_m=flywheel_r,
        axle_radius_m=axle_r,
        axle_half_m=axle_half,
        race_offset_m=race_offset,
        race_len_m=race_len,
        rotor_envelope_m=rotor_env,
        gimbal_center_z_m=r_out + rise,
        mount_station_m=mount_station,
        housing_len_m=housing_len,
        housing_outer_m=housing_outer,
        support_axis=support_axis,
        support_radial=support_radial,
        azimuth_limit_rad=azimuth_limit,
        tilt_limit_rad=tilt_limit,
        stop_radius_m=stop_radius,
        stop_block_half_rad=stop_block_half,
        stop_pin_half_rad=stop_pin_half,
        stop_block_angle_rad=stop_block_angle,
        mast_len_m=MAST_RATIO * r_out,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("support_base", config.support_base),
        ("ring_stack", config.ring_stack),
        ("ring_section", config.ring_section),
        ("spindle_support", config.spindle_support),
        ("rotor_form", config.rotor_form),
        ("index_hardware", config.index_hardware),
        ("gimbal_motion", config.gimbal_motion),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"gyro_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


# --- generic revolved / swept primitives ------------------------------------------
def _lathe(profile, name: str, segments: int):
    return mesh_from_geometry(LatheGeometry(list(profile), segments=segments), name)


def _tube_profile(r_in: float, r_out: float, z0: float, z1: float):
    """Closed annular section, revolved into a bored tube about local +Z."""

    return ((r_in, z0), (r_out, z0), (r_out, z1), (r_in, z1))


def _dir_rpy(direction: tuple[float, float, float]) -> tuple[float, float, float]:
    """RPY that carries a primitive's local +Z onto ``direction``."""

    dx, dy, dz = direction
    norm = math.sqrt(dx * dx + dy * dy + dz * dz)
    if norm <= 1e-12:
        return (0.0, 0.0, 0.0)
    dx, dy, dz = dx / norm, dy / norm, dz / norm
    pitch = math.acos(_clamp(dz, -1.0, 1.0))
    yaw = math.atan2(dy, dx) if (abs(dx) + abs(dy)) > 1e-12 else 0.0
    return (0.0, pitch, yaw)


def _strut(host, p0, p1, radius: float, material: str, name: str) -> None:
    """One cylindrical member spanning two points, used for legs and spiders."""

    direction = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    length = math.sqrt(sum(component * component for component in direction))
    if length <= 1e-9:
        return
    host.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(
            xyz=(0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]), 0.5 * (p0[2] + p1[2])),
            rpy=_dir_rpy(direction),
        ),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _rpy_matrix(rpy: tuple[float, float, float]) -> tuple[tuple[float, float, float], ...]:
    roll, pitch, yaw = rpy
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return (
        (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
        (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
        (-sp, cp * sr, cp * cr),
    )


def _mat_mul(a, b):
    return tuple(
        tuple(sum(a[row][k] * b[k][col] for k in range(3)) for col in range(3)) for row in range(3)
    )


def _mat_vec(a, v):
    return tuple(sum(a[row][k] * v[k] for k in range(3)) for row in range(3))


# --- support base candidates -------------------------------------------------------
def _base_station(r: ResolvedConfig, station: float) -> tuple[float, float, float]:
    """A point ``station`` metres from the gimbal centre, back along the support axis."""

    ax, ay, az = r.support_axis
    return (-station * ax, -station * ay, r.gimbal_center_z_m - station * az)


def _base_polar(
    r: ResolvedConfig, station: float, radius: float, angle: float
) -> tuple[float, float, float]:
    """A point at ``radius``/``angle`` about the support axis, measured from its radial."""

    rd = r.support_radial
    ax, ay, az = r.support_axis
    tangential = (
        ay * rd[2] - az * rd[1],
        az * rd[0] - ax * rd[2],
        ax * rd[1] - ay * rd[0],
    )
    base = _base_station(r, station)
    ca, sa = math.cos(angle), math.sin(angle)
    return (
        base[0] + radius * (ca * rd[0] + sa * tangential[0]),
        base[1] + radius * (ca * rd[1] + sa * tangential[1]),
        base[2] + radius * (ca * rd[2] + sa * tangential[2]),
    )


def _base_bearing(host, r: ResolvedConfig, mats: dict[str, str], prefix: str) -> None:
    """Bored azimuth bearing plus its closing cap, on the support axis."""

    bore = r.pole_pin_radius_m[0] + BEARING_FIT
    axis_rpy = _dir_rpy((-r.support_axis[0], -r.support_axis[1], -r.support_axis[2]))
    host.visual(
        _lathe(
            _tube_profile(bore, r.housing_outer_m, 0.0, r.housing_len_m),
            f"{prefix}bearing_bore",
            BOSS_SEG,
        ),
        origin=Origin(xyz=_base_station(r, r.mount_station_m), rpy=axis_rpy),
        material=mats["bearing"],
        name=f"{prefix}bearing_housing", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    host.visual(
        Cylinder(radius=r.housing_outer_m, length=CAP_T),
        origin=Origin(
            xyz=_base_station(r, r.mount_station_m + r.housing_len_m + 0.5 * CAP_T),
            rpy=axis_rpy,
        ),
        material=mats["bright"],
        name=f"{prefix}bearing_cap", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
    )


def _base_stop_track(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Azimuth end-stop collar and its two travel blocks (limited_stops only)."""

    prefix = "gimbal_motion__limited_stops__"
    collar_station = r.mount_station_m + r.housing_len_m + CAP_T + 0.003
    axis_rpy = _dir_rpy((-r.support_axis[0], -r.support_axis[1], -r.support_axis[2]))
    host.visual(
        _lathe(
            _tube_profile(r.housing_outer_m + 0.001, r.stop_radius_m + 0.008, 0.0, 0.004),
            f"{prefix}stop_collar_ring",
            BOSS_SEG,
        ),
        origin=Origin(xyz=_base_station(r, collar_station), rpy=axis_rpy),
        material=mats["ring"],
        name=f"{prefix}stop_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    for index, sign in enumerate((1.0, -1.0)):
        host.visual(
            Cylinder(radius=0.0060, length=0.013),
            origin=Origin(
                xyz=_base_polar(
                    r,
                    collar_station - 0.0065,
                    r.stop_radius_m,
                    sign * r.stop_block_angle_rad,
                ),
                rpy=axis_rpy,
            ),
            material=mats["edge"],
            name=f"{prefix}azimuth_stop_{index}", material_class_id=("metal.brass_aged" if r.palette_style in {"blackened_iron", "dark_chrome", "brass_accent"} else "metal.brushed_silver"),
        )


def _support_base_weighted_pedestal_build(model, r: ResolvedConfig, mats: dict[str, str]):
    part = model.part("support_base", meta={"role": "support_base"})
    prefix = "support_base__weighted_pedestal__"
    mount_z = r.gimbal_center_z_m - r.mount_station_m
    body_r = 0.90 * r.outer_ring_radius_m
    body_h = min(0.42 * body_r, 0.45 * mount_z)
    part.visual(
        _lathe(
            [(pr * body_r, pz * body_h) for pr, pz in WEIGHTED_BASE_PROFILE],
            f"{prefix}weighted_body",
            96,
        ),
        material=mats["body"],
        name=f"{prefix}weighted_base", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.cast_iron_bare"),
    )
    collar_r = min(0.34 * body_r, 3.2 * r.housing_outer_m)
    part.visual(
        Cylinder(radius=collar_r, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, body_h + 0.004)),
        material=mats["ring"],
        name=f"{prefix}pedestal_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    # The azimuth bore is drilled right through the pedestal, so the solid upright
    # has to start below the housing instead of filling the bore column.
    upright_top = mount_z - r.housing_len_m + 0.002
    upright_bottom = body_h - 0.004
    part.visual(
        Cylinder(radius=1.35 * r.housing_outer_m, length=max(0.010, upright_top - upright_bottom)),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (upright_top + upright_bottom))),
        material=mats["body"],
        name=f"{prefix}upright_support", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.cast_iron_bare"),
    )
    _base_bearing(part, r, mats, prefix)
    if r.gimbal_motion == "limited_stops":
        _base_stop_track(part, r, mats)
    return part


def _support_base_slender_column_build(model, r: ResolvedConfig, mats: dict[str, str]):
    part = model.part("support_base", meta={"role": "support_base"})
    prefix = "support_base__slender_column__"
    mount_z = r.gimbal_center_z_m - r.mount_station_m
    body_r = 0.62 * r.outer_ring_radius_m
    body_h = mount_z - r.housing_len_m + 0.002
    part.visual(
        _lathe(
            [(pr * body_r, pz * body_h) for pr, pz in SLENDER_COLUMN_PROFILE],
            f"{prefix}column_body",
            80,
        ),
        material=mats["body"],
        name=f"{prefix}weighted_column", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.cast_iron_bare"),
    )
    part.visual(
        Cylinder(radius=1.85 * r.housing_outer_m, length=0.005),
        origin=Origin(xyz=(0.0, 0.0, mount_z - r.housing_len_m + 0.003)),
        material=mats["ring"],
        name=f"{prefix}bearing_flange", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    _base_bearing(part, r, mats, prefix)
    if r.gimbal_motion == "limited_stops":
        _base_stop_track(part, r, mats)
    return part


def _support_base_tripod_legs_build(model, r: ResolvedConfig, mats: dict[str, str]):
    part = model.part("support_base", meta={"role": "support_base"})
    prefix = "support_base__tripod_legs__"
    mount_z = r.gimbal_center_z_m - r.mount_station_m
    hub_z = 0.42 * mount_z
    hub_r = 0.22 * r.outer_ring_radius_m
    foot_r = 0.72 * r.outer_ring_radius_m
    leg_r = max(0.0042, 0.045 * r.outer_ring_radius_m)
    part.visual(
        Cylinder(radius=hub_r, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, hub_z)),
        material=mats["body"],
        name=f"{prefix}hub_plate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.cast_iron_bare"),
    )
    for index in range(3):
        theta = index * (2.0 * math.pi / 3.0)
        _strut(
            part,
            (0.30 * hub_r * math.cos(theta), 0.30 * hub_r * math.sin(theta), hub_z + 0.002),
            (foot_r * math.cos(theta), foot_r * math.sin(theta), 0.007),
            leg_r,
            mats["body"],
            f"{prefix}leg_{index}",
        )
        part.visual(
            Cylinder(radius=1.7 * leg_r, length=0.007),
            origin=Origin(xyz=(foot_r * math.cos(theta), foot_r * math.sin(theta), 0.0035)),
            material=mats["edge"],
            name=f"{prefix}foot_pad_{index}", material_class_id=("metal.brass_aged" if r.palette_style in {"blackened_iron", "dark_chrome", "brass_accent"} else "metal.brushed_silver"),
        )
    collar_r = min(1.15 * hub_r, 3.0 * r.housing_outer_m)
    part.visual(
        Cylinder(radius=collar_r, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, hub_z + 0.008)),
        material=mats["ring"],
        name=f"{prefix}pedestal_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    upright_top = mount_z - r.housing_len_m + 0.002
    upright_bottom = hub_z + 0.004
    part.visual(
        Cylinder(radius=1.35 * r.housing_outer_m, length=max(0.010, upright_top - upright_bottom)),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (upright_top + upright_bottom))),
        material=mats["body"],
        name=f"{prefix}upright_support", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.cast_iron_bare"),
    )
    _base_bearing(part, r, mats, prefix)
    if r.gimbal_motion == "limited_stops":
        _base_stop_track(part, r, mats)
    return part


def _support_base_wall_bracket_build(model, r: ResolvedConfig, mats: dict[str, str]):
    part = model.part("support_base", meta={"role": "support_base"})
    prefix = "support_base__wall_bracket__"
    yoke_y = r.mount_station_m + r.housing_len_m + 0.004
    wall_y = r.mount_station_m + r.housing_len_m + 0.058
    arm_dx = r.housing_outer_m + 0.016
    plate_hx = 0.85 * r.outer_ring_radius_m
    plate_top = r.gimbal_center_z_m + 1.15 * r.outer_ring_radius_m
    part.visual(
        Box((2.0 * plate_hx, 0.011, plate_top)),
        origin=Origin(xyz=(0.0, wall_y + 0.0055, 0.5 * plate_top)),
        material=mats["body"],
        name=f"{prefix}wall_plate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.cast_iron_bare"),
    )
    for index, sign in enumerate((1.0, -1.0)):
        part.visual(
            Box((2.0 * plate_hx - 0.010, 0.012, 0.011)),
            origin=Origin(
                xyz=(0.0, wall_y - 0.004, r.gimbal_center_z_m + sign * 0.86 * r.outer_ring_radius_m)
            ),
            material=mats["ring"],
            name=f"{prefix}mounting_rail_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )
        arm_len = wall_y + 0.004 - (r.mount_station_m + 0.004)
        part.visual(
            Box((0.016, arm_len, 0.021)),
            origin=Origin(
                xyz=(
                    sign * arm_dx,
                    r.mount_station_m + 0.004 + 0.5 * arm_len,
                    r.gimbal_center_z_m,
                )
            ),
            material=mats["body"],
            name=f"{prefix}support_arm_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.cast_iron_bare"),
        )
        part.visual(
            Box((0.013, 0.030, 0.048)),
            origin=Origin(xyz=(sign * arm_dx, wall_y - 0.013, r.gimbal_center_z_m - 0.033)),
            material=mats["body"],
            name=f"{prefix}arm_gusset_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.cast_iron_bare"),
        )
    part.visual(
        Box((2.0 * arm_dx + 0.018, 0.013, 0.032)),
        origin=Origin(xyz=(0.0, yoke_y, r.gimbal_center_z_m)),
        material=mats["bearing"],
        name=f"{prefix}bearing_yoke", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    for index, (dx, dz) in enumerate(((-0.70, 0.86), (0.70, 0.86), (-0.70, -0.86), (0.70, -0.86))):
        part.visual(
            Cylinder(radius=0.0052, length=0.004),
            origin=Origin(
                xyz=(
                    dx * plate_hx,
                    wall_y - 0.002,
                    r.gimbal_center_z_m + dz * r.outer_ring_radius_m,
                ),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["accent"],
            name=f"{prefix}mounting_screw_{index}", material_class_id=("metal.paint_coated" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.blackened_gunmetal"),
        )
    _base_bearing(part, r, mats, prefix)
    if r.gimbal_motion == "limited_stops":
        _base_stop_track(part, r, mats)
    return part


_SUPPORT_BUILDERS = {
    "weighted_pedestal": _support_base_weighted_pedestal_build,
    "slender_column": _support_base_slender_column_build,
    "tripod_legs": _support_base_tripod_legs_build,
    "wall_bracket": _support_base_wall_bracket_build,
}


# --- gimbal ring members -----------------------------------------------------------
_PLANE_XZ = (math.pi / 2.0, 0.0, 0.0)  # revolve about local Z -> annulus in local XZ
_PLANE_YZ = (0.0, math.pi / 2.0, 0.0)  # revolve about local Z -> annulus in local YZ
_ALONG_X = (0.0, math.pi / 2.0, 0.0)  # primitive local +Z -> local +X


def _child_radial(r: ResolvedConfig, index: int) -> tuple[float, float, float]:
    """Radial reference handed to ring ``index + 1``; it fixes that ring's plane.

    ``(0, 0, 1)`` keeps the child's plane in the parent's own plane (the classic
    coplanar two-gimbal pair, and the only way a ``bearing_spider`` carrier ends
    up perpendicular to its parent).  ``(0, 1, 0)`` swings the child's plane onto
    the parent's normal, which is what an orthogonal three-ring stack needs.
    """

    child_is_carrier = index + 1 == r.ring_count - 1
    if not child_is_carrier:
        return (0.0, 1.0, 0.0)
    if r.ring_count == 2:
        return (0.0, 0.0, 1.0)
    return (0.0, 1.0, 0.0) if r.spindle_support == "opposed_bearings" else (0.0, 0.0, 1.0)


def _ring_plane_rpy(r: ResolvedConfig, index: int) -> tuple[float, float, float]:
    is_carrier = index == r.ring_count - 1
    if is_carrier and r.spindle_support == "bearing_spider":
        return _PLANE_YZ
    return _PLANE_XZ


def _ring_band(host, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    """The ring member itself, in whichever cross-section the slot selected."""

    is_carrier = index == r.ring_count - 1
    section = r.ring_section
    if section == "carrier_frame" and not is_carrier:
        # Source `two_axis_cage` keeps the outer hoop annular and only rebuilds the
        # innermost member as a cage, so outer members stay flat bands here too.
        section = "flat_band"
    prefix = f"ring_section__{r.ring_section}__"
    r_out = r.ring_outer_m[index]
    r_in = r.ring_inner_m[index]
    thick = r.ring_thick_m[index]
    plane = _ring_plane_rpy(r, index)

    if section == "flat_band":
        host.visual(
            _lathe(
                _tube_profile(r_in, r_out, -0.5 * thick, 0.5 * thick),
                f"{prefix}band_{index}",
                RING_SEG,
            ),
            origin=Origin(rpy=plane),
            material=mats["ring"],
            name=f"{prefix}ring_band_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )
        host.visual(
            _lathe(
                _tube_profile(r_out - 0.0022, r_out + 0.0005, -0.58 * thick, 0.58 * thick),
                f"{prefix}bead_{index}",
                RING_SEG,
            ),
            origin=Origin(rpy=plane),
            material=mats["edge"],
            name=f"{prefix}edge_bead_{index}", material_class_id=("metal.brass_aged" if r.palette_style in {"blackened_iron", "dark_chrome", "brass_accent"} else "metal.brushed_silver"),
        )
    elif section == "tubular_hoop":
        tube = 0.5 * (r_out - r_in)
        host.visual(
            mesh_from_geometry(
                TorusGeometry(
                    radius=r_out - tube,
                    tube=tube,
                    radial_segments=20,
                    tubular_segments=RING_SEG,
                ),
                f"{prefix}hoop_{index}",
            ),
            origin=Origin(rpy=plane),
            material=mats["ring"],
            name=f"{prefix}ring_band_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )
    else:
        half_pole = r.carrier_half_pole_m
        half_span = r.carrier_half_spin_m
        bar = r.carrier_bar_m
        depth = r.carrier_depth_m
        spider = r.spindle_support == "bearing_spider"
        # Four welded bars.  The two pole bars carry the trunnions, the two side
        # bars carry the spindle bearings (opposed) or the spider posts.
        if spider:
            pole_box = (depth, 2.0 * half_span, bar)
            side_box = (depth, bar, 2.0 * half_pole)
            side_offset = (0.0, 1.0, 0.0)
        else:
            pole_box = (2.0 * half_span, depth, bar)
            side_box = (bar, depth, 2.0 * half_pole)
            side_offset = (1.0, 0.0, 0.0)
        for suffix, sign in enumerate((1.0, -1.0)):
            host.visual(
                Box(pole_box),
                origin=Origin(xyz=(0.0, 0.0, sign * (half_pole - 0.5 * bar))),
                material=mats["ring"],
                name=(
                    f"{prefix}ring_band_{index}"
                    if suffix == 0
                    else f"{prefix}carrier_pole_bar_{index}"
                ), material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
            )
            host.visual(
                Box(side_box),
                origin=Origin(
                    xyz=(
                        sign * side_offset[0] * (half_span - 0.5 * bar),
                        sign * side_offset[1] * (half_span - 0.5 * bar),
                        0.0,
                    )
                ),
                material=mats["edge"],
                name=f"{prefix}carrier_side_bar_{index}_{suffix}", material_class_id=("metal.brass_aged" if r.palette_style in {"blackened_iron", "dark_chrome", "brass_accent"} else "metal.brushed_silver"),
            )


def _ring_pole_pins(host, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    """The trunnion pins on this member's own hold axis (local +-Z)."""

    prefix = f"ring_section__{r.ring_section}__"
    pin_r = r.pole_pin_radius_m[index]
    inner_end = r.pole_reach_m[index] - POLE_INSET
    if index == 0:
        outer_end = r.mount_station_m + r.housing_len_m - PIN_BACKOFF
        signs = ((-1.0, 0),)
    else:
        outer_end = r.ring_inner_m[index - 1] - PIN_BACKOFF
        signs = ((1.0, 0), (-1.0, 1))
    length = max(0.006, outer_end - inner_end)
    for sign, suffix in signs:
        host.visual(
            Cylinder(radius=pin_r, length=length),
            origin=Origin(xyz=(0.0, 0.0, sign * (inner_end + 0.5 * length))),
            material=mats["bright"],
            name=f"{prefix}pole_pin_{index}_{suffix}", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
        )
        host.visual(
            Cylinder(radius=pin_r + 0.0035, length=0.006),
            origin=Origin(xyz=(0.0, 0.0, sign * (inner_end + 0.004))),
            material=mats["bearing"],
            name=f"{prefix}pole_collar_{index}_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )


def _ring_child_bearings(host, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    """Bored trunnion housings on local +-X that carry the next ring."""

    prefix = f"ring_section__{r.ring_section}__"
    bore = r.pole_pin_radius_m[index + 1] + BEARING_FIT
    sleeve_out = bore + BOSS_WALL
    r_out = r.ring_outer_m[index]
    r_in = r.ring_inner_m[index]
    sleeve_x0 = r.pole_reach_m[index + 1] + 0.004
    sleeve_x1 = r_in - 0.0015
    body_x0 = r_in - 0.0030
    body_x1 = r_out + 0.005
    for suffix, sign in enumerate((1.0, -1.0)):
        host.visual(
            _lathe(
                _tube_profile(bore, sleeve_out, 0.0, max(0.004, sleeve_x1 - sleeve_x0)),
                f"{prefix}tsleeve_{index}_{suffix}",
                BOSS_SEG,
            ),
            origin=Origin(
                xyz=(sign * sleeve_x0, 0.0, 0.0),
                rpy=_ALONG_X if sign > 0 else (0.0, -math.pi / 2.0, 0.0),
            ),
            material=mats["bearing"],
            name=f"{prefix}trunnion_sleeve_{index}_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )
        host.visual(
            Cylinder(radius=sleeve_out, length=body_x1 - body_x0),
            origin=Origin(xyz=(sign * 0.5 * (body_x0 + body_x1), 0.0, 0.0), rpy=_ALONG_X),
            material=mats["bearing"],
            name=f"{prefix}trunnion_bearing_{index}_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )
        host.visual(
            Cylinder(radius=sleeve_out + 0.0022, length=CAP_T),
            origin=Origin(xyz=(sign * (body_x1 + 0.5 * CAP_T), 0.0, 0.0), rpy=_ALONG_X),
            material=mats["bright"],
            name=f"{prefix}trunnion_cap_{index}_{suffix}", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
        )
        if r.ring_section == "tubular_hoop":
            host.visual(
                mesh_from_geometry(
                    TorusGeometry(
                        radius=sleeve_out + 0.0016,
                        tube=0.0015,
                        radial_segments=10,
                        tubular_segments=28,
                    ),
                    f"{prefix}tseat_{index}_{suffix}",
                ),
                origin=Origin(xyz=(sign * (r_in + 0.001), 0.0, 0.0), rpy=_ALONG_X),
                material=mats["bright"],
                name=f"{prefix}bearing_seat_{index}_{suffix}", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
            )


def _tangent_of(radial: tuple[float, float, float]) -> tuple[float, float, float]:
    """Tangential direction completing (+X, radial, tangent) about the local +X axis."""

    return (0.0, -radial[2], radial[1])


def _tilt_stop_radius(r: ResolvedConfig, index: int) -> float:
    return r.pole_pin_radius_m[index + 1] + BEARING_FIT + 0.010


def _ring_tilt_stops(host, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    """Parent-side end stops on the primary tilt trunnion (limited_stops only).

    A collar on the trunnion sleeve mouth carries two posts.  Their arc position
    is solved from the joint limit plus both half-widths plus STOP_MARGIN, so the
    travelling lug always stops short of them instead of striking them.
    """

    prefix = "gimbal_motion__limited_stops__"
    bore = r.pole_pin_radius_m[index + 1] + BEARING_FIT
    stop_r = _tilt_stop_radius(r, index)
    mouth = r.pole_reach_m[index + 1]
    radial = _child_radial(r, index)
    tangent = _tangent_of(radial)
    block = r.tilt_limit_rad + math.atan2(0.0033, stop_r) + math.atan2(0.0035, stop_r) + STOP_MARGIN
    host.visual(
        _lathe(
            _tube_profile(bore + 0.002, stop_r + 0.005, 0.0, 0.004),
            f"{prefix}tilt_collar_mesh",
            BOSS_SEG,
        ),
        origin=Origin(xyz=(mouth + 0.003, 0.0, 0.0), rpy=_ALONG_X),
        material=mats["bearing"],
        name=f"{prefix}tilt_shoulder_collar", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    for suffix, sign in enumerate((1.0, -1.0)):
        angle = sign * block
        ca, sa = math.cos(angle), math.sin(angle)
        host.visual(
            Cylinder(radius=0.0035, length=0.009),
            origin=Origin(
                xyz=(
                    mouth + 0.0005,
                    stop_r * (ca * radial[1] + sa * tangent[1]),
                    stop_r * (ca * radial[2] + sa * tangent[2]),
                ),
                rpy=_ALONG_X,
            ),
            material=mats["edge"],
            name=f"{prefix}tilt_stop_{suffix}", material_class_id=("metal.brass_aged" if r.palette_style in {"blackened_iron", "dark_chrome", "brass_accent"} else "metal.brushed_silver"),
        )


def _ring_tilt_lug(host, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    """The travelling lug on the child trunnion that runs between its parent's stops."""

    prefix = "gimbal_motion__limited_stops__"
    stop_r = _tilt_stop_radius(r, index - 1)
    station = r.pole_reach_m[index] - 0.002
    _strut(
        host,
        (0.0, 0.0, station),
        (stop_r, 0.0, station),
        0.0033,
        mats["bright"],
        f"{prefix}tilt_lug_0",
    )


def _ring_index_hardware(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Free-pole hardware on the outer ring: plain trunnion stub or pointer mast."""

    reach = r.pole_reach_m[0]
    if r.index_hardware == "plain_trunnion":
        prefix = "index_hardware__plain_trunnion__"
        pin_r = r.pole_pin_radius_m[0]
        host.visual(
            Cylinder(radius=pin_r * 1.15, length=0.014),
            origin=Origin(xyz=(0.0, 0.0, reach + 0.002)),
            material=mats["bearing"],
            name=f"{prefix}pole_trunnion", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )
        host.visual(
            Cylinder(radius=pin_r * 1.75, length=CAP_T),
            origin=Origin(xyz=(0.0, 0.0, reach + 0.0080 + 0.5 * CAP_T)),
            material=mats["bright"],
            name=f"{prefix}pole_cap", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
        )
    else:
        prefix = "index_hardware__pointer_mast__"
        host.visual(
            Cylinder(radius=r.pole_pin_radius_m[0] * 1.55, length=0.011),
            origin=Origin(xyz=(0.0, 0.0, reach + 0.0015)),
            material=mats["ring"],
            name=f"{prefix}pointer_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )
        mast = r.mast_len_m
        host.visual(
            Cylinder(radius=max(0.0026, 0.024 * r.outer_ring_radius_m), length=mast),
            origin=Origin(xyz=(0.0, 0.0, reach + 0.005 + 0.5 * mast)),
            material=mats["bright"],
            name=f"{prefix}index_pointer", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
        )
        host.visual(
            Sphere(radius=max(0.0032, 0.030 * r.outer_ring_radius_m)),
            origin=Origin(xyz=(0.0, 0.0, reach + 0.004 + mast)),
            material=mats["accent"],
            name=f"{prefix}pointer_tip", material_class_id=("metal.paint_coated" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.blackened_gunmetal"),
        )


def _ring_azimuth_stop_pin(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Outer-ring stop pin that travels between the base stop blocks."""

    prefix = "gimbal_motion__limited_stops__"
    reach = r.pole_reach_m[0]
    host.visual(
        Box((r.stop_radius_m, 0.009, 0.011)),
        origin=Origin(xyz=(0.5 * r.stop_radius_m, 0.0, -(reach - 0.007))),
        material=mats["ring"],
        name=f"{prefix}stop_arm", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    top = reach - 0.002
    bottom = r.mount_station_m + r.housing_len_m + CAP_T + 0.0015
    length = max(0.006, bottom - top)
    host.visual(
        Cylinder(radius=0.0035, length=length),
        origin=Origin(xyz=(r.stop_radius_m, 0.0, -(top + 0.5 * length))),
        material=mats["bright"],
        name=f"{prefix}azimuth_stop_pin", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
    )


def _spindle_support_opposed_bearings_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Two bored pole bearings on the carrier's own plane, holding a through axle."""

    prefix = "spindle_support__opposed_bearings__"
    bore = r.axle_radius_m + BEARING_FIT
    sleeve_out = bore + BOSS_WALL
    seat = r.spin_seat_m
    reach = r.carrier_half_spin_m if r.ring_section == "carrier_frame" else r.ring_outer_m[-1]
    sleeve_len = max(0.014, 0.17 * seat)
    for suffix, sign in enumerate((1.0, -1.0)):
        host.visual(
            _lathe(
                _tube_profile(bore, sleeve_out, 0.0, sleeve_len),
                f"{prefix}sleeve_{suffix}",
                BOSS_SEG,
            ),
            origin=Origin(
                xyz=(sign * (seat - sleeve_len - 0.002), 0.0, 0.0),
                rpy=_ALONG_X if sign > 0 else (0.0, -math.pi / 2.0, 0.0),
            ),
            material=mats["bearing"],
            name=f"{prefix}spin_sleeve_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )
        host.visual(
            Cylinder(radius=sleeve_out, length=(reach + 0.005) - (seat - 0.003)),
            origin=Origin(
                xyz=(sign * 0.5 * ((seat - 0.003) + reach + 0.005), 0.0, 0.0), rpy=_ALONG_X
            ),
            material=mats["bearing"],
            name=f"{prefix}spin_bearing_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )
        host.visual(
            Cylinder(radius=sleeve_out + 0.0025, length=CAP_T),
            origin=Origin(xyz=(sign * (reach + 0.005 + 0.5 * CAP_T), 0.0, 0.0), rpy=_ALONG_X),
            material=mats["bright"],
            name=f"{prefix}spin_bearing_cap_{suffix}", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
        )


def _spindle_support_bearing_spider_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """A single central race carried on two rim posts and two inclined struts."""

    prefix = "spindle_support__bearing_spider__"
    bore = r.axle_radius_m + BEARING_FIT
    strut_r = max(0.0030, 0.040 * r.ring_outer_m[-1])
    race_out = bore + max(0.0040, 1.6 * strut_r)
    seat = r.spin_seat_m
    post_r = max(0.0035, 0.05 * r.ring_outer_m[-1])
    post_x = _spider_post_x(r)
    host.visual(
        _lathe(
            _tube_profile(bore, race_out, -0.5 * r.race_len_m, 0.5 * r.race_len_m),
            f"{prefix}race",
            BOSS_SEG,
        ),
        origin=Origin(xyz=(r.race_offset_m, 0.0, 0.0), rpy=_ALONG_X),
        material=mats["bearing"],
        name=f"{prefix}spindle_race", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    for suffix, sign in enumerate((1.0, -1.0)):
        host.visual(
            Cylinder(radius=post_r, length=abs(post_x) + 0.004),
            origin=Origin(xyz=(0.5 * post_x, sign * seat, 0.0), rpy=_ALONG_X),
            material=mats["ring"],
            name=f"{prefix}bearing_post_{suffix}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )
        _strut(
            host,
            (post_x, sign * seat, 0.0),
            (r.race_offset_m, sign * (race_out - 0.5 * strut_r), 0.0),
            strut_r,
            mats["ring"],
            f"{prefix}bearing_arm_{suffix}",
        )


_SPINDLE_BUILDERS = {
    "opposed_bearings": _spindle_support_opposed_bearings_build,
    "bearing_spider": _spindle_support_bearing_spider_build,
}


def _build_ring(model, r: ResolvedConfig, mats: dict[str, str], index: int, parent, provider):
    is_carrier = index == r.ring_count - 1
    if index == 0:
        part_name, role = "outer_gimbal_ring", "outer_gimbal_ring"
    elif is_carrier:
        part_name, role = "spindle_carrier", "spindle_carrier"
    else:
        part_name, role = "mid_gimbal_ring", "mid_gimbal_ring"
    part = model.part(part_name, meta={"role": role})

    _ring_band(part, r, mats, index)
    _ring_pole_pins(part, r, mats, index)
    if is_carrier:
        _SPINDLE_BUILDERS[r.spindle_support](part, r, mats)
    else:
        _ring_child_bearings(part, r, mats, index)
    if index == 0:
        _ring_index_hardware(part, r, mats)
        if r.gimbal_motion == "limited_stops":
            _ring_azimuth_stop_pin(part, r, mats)
            _ring_tilt_stops(part, r, mats, index)
    if index == 1 and r.gimbal_motion == "limited_stops":
        _ring_tilt_lug(part, r, mats, index)

    consumer = AxisInterface(
        name=f"ring_{index}_pole_axis",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    mate = mate_axes(provider, consumer)
    joint = f"gimbal_axis_{index}"
    limit = r.azimuth_limit_rad if index == 0 else r.tilt_limit_rad
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=part,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=4.0 if index == 0 else 2.0,
            velocity=2.0 if index == 0 else 3.0,
            lower=-limit,
            upper=limit,
        ),
        motion_properties=MotionProperties(
            damping=0.02 if index == 0 else 0.01,
            friction=0.01 if index == 0 else 0.005,
        ),
        meta={
            "mechanism": (
                "azimuth trunnion on the support axis"
                if index == 0
                else "orthogonal gimbal trunnion pair"
            ),
            "positive_motion": "swings the nested gimbal stack about this trunnion axis",
        },
    )
    register_interface_mate(model, joint, mate)

    if is_carrier:
        next_provider = AxisInterface(
            name="spindle_axis",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
        )
    else:
        next_provider = AxisInterface(
            name=f"ring_{index}_child_axis",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=_child_radial(r, index),
        )
    return part, next_provider


# --- rotor candidates ---------------------------------------------------------------
def _rotor_back(r: ResolvedConfig) -> float:
    return ROTOR_BACK_REACH[r.rotor_form] * r.flywheel_radius_m


def _spider_post_x(r: ResolvedConfig) -> float:
    """Axial station of the spider rim posts, clear of the rotor's own back reach."""

    return -(_rotor_back(r) + 0.006)


def _rotor_balance_arm(
    host, r: ResolvedConfig, mats: dict[str, str], prefix: str, z_level: float, thick: float
) -> None:
    radius = r.flywheel_radius_m
    host.visual(
        Box((0.78 * radius, 0.052 * radius + 0.0015, thick)),
        origin=Origin(xyz=(0.49 * radius, 0.0, z_level)),
        material=mats["accent"],
        name=f"{prefix}balance_pointer", material_class_id=("metal.paint_coated" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.blackened_gunmetal"),
    )
    host.visual(
        Sphere(radius=0.10 * radius),
        origin=Origin(xyz=(0.94 * radius, 0.0, z_level)),
        material=mats["edge"],
        name=f"{prefix}balance_weight", material_class_id=("metal.brass_aged" if r.palette_style in {"blackened_iron", "dark_chrome", "brass_accent"} else "metal.brushed_silver"),
    )


def _rotor_form_crowned_drum_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    prefix = "rotor_form__crowned_drum__"
    radius = r.flywheel_radius_m
    host.visual(
        _lathe(
            [(pr * radius, pz * radius) for pr, pz in CROWNED_DRUM_PROFILE],
            f"{prefix}drum",
            DISC_SEG,
        ),
        material=mats["bright"],
        name=f"{prefix}flywheel", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
    )
    host.visual(
        Cylinder(radius=0.24 * radius, length=0.55 * radius),
        material=mats["bearing"],
        name=f"{prefix}flywheel_hub", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    _rotor_balance_arm(host, r, mats, prefix, 0.325 * radius, 0.055 * radius)


def _rotor_form_solid_disc_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    prefix = "rotor_form__solid_disc__"
    radius = r.flywheel_radius_m
    host.visual(
        _lathe(
            [(pr * radius, pz * radius) for pr, pz in SOLID_DISC_PROFILE],
            f"{prefix}disc",
            DISC_SEG,
        ),
        material=mats["bright"],
        name=f"{prefix}flywheel", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
    )
    host.visual(
        Cylinder(radius=0.26 * radius, length=0.60 * radius),
        material=mats["bearing"],
        name=f"{prefix}flywheel_hub", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    host.visual(
        Cylinder(radius=0.09 * radius, length=0.024 * radius),
        origin=Origin(xyz=(0.70 * radius, 0.0, 0.309 * radius)),
        material=mats["accent"],
        name=f"{prefix}disc_phase_mark", material_class_id=("metal.paint_coated" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.blackened_gunmetal"),
    )


def _rotor_form_shaped_disc_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    prefix = "rotor_form__shaped_disc__"
    radius = r.flywheel_radius_m
    host.visual(
        _lathe(
            [(pr * radius, pz * radius) for pr, pz in SHAPED_DISC_PROFILE],
            f"{prefix}disc",
            DISC_SEG,
        ),
        material=mats["bright"],
        name=f"{prefix}flywheel", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
    )
    host.visual(
        mesh_from_geometry(
            TorusGeometry(
                radius=0.943 * radius,
                tube=0.062 * radius,
                radial_segments=16,
                tubular_segments=DISC_SEG,
            ),
            f"{prefix}band",
        ),
        material=mats["bearing"],
        name=f"{prefix}perimeter_band", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    host.visual(
        Cylinder(radius=0.148 * radius, length=0.20 * radius),
        origin=Origin(xyz=(0.0, 0.0, 0.12 * radius)),
        material=mats["accent"],
        name=f"{prefix}flywheel_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.blackened_gunmetal"),
    )
    host.visual(
        _lathe(
            [
                (0.000, 0.000),
                (0.062 * radius, 0.000),
                (0.062 * radius, 0.041 * radius),
                (0.041 * radius, 0.082 * radius),
                (0.021 * radius, 0.113 * radius),
                (0.000, 0.124 * radius),
            ],
            f"{prefix}cap",
            40,
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.215 * radius)),
        material=mats["bright"],
        name=f"{prefix}spindle_cap", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
    )
    _rotor_balance_arm(host, r, mats, prefix, 0.17 * radius, 0.030 * radius)


def _rotor_form_spoked_rim_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    prefix = "rotor_form__spoked_rim__"
    radius = r.flywheel_radius_m
    host.visual(
        mesh_from_geometry(
            TorusGeometry(
                radius=0.907 * radius,
                tube=0.046 * radius,
                radial_segments=16,
                tubular_segments=DISC_SEG,
            ),
            f"{prefix}rim",
        ),
        material=mats["bright"],
        name=f"{prefix}inertia_rim", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
    )
    host.visual(
        mesh_from_geometry(
            TorusGeometry(
                radius=0.943 * radius,
                tube=0.062 * radius,
                radial_segments=16,
                tubular_segments=DISC_SEG,
            ),
            f"{prefix}band",
        ),
        material=mats["bearing"],
        name=f"{prefix}perimeter_band", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
    )
    hub_r = 0.150 * radius
    rim_inner = 0.907 * radius - 0.046 * radius
    for index in range(SPOKE_COUNT):
        theta = index * (2.0 * math.pi / SPOKE_COUNT)
        _strut(
            host,
            (0.6 * hub_r * math.cos(theta), 0.6 * hub_r * math.sin(theta), 0.0),
            (
                (rim_inner + 0.010 * radius) * math.cos(theta),
                (rim_inner + 0.010 * radius) * math.sin(theta),
                0.0,
            ),
            0.027 * radius,
            mats["bright"],
            f"{prefix}spoke_{index}",
        )
    host.visual(
        Cylinder(radius=hub_r, length=0.18 * radius),
        material=mats["accent"],
        name=f"{prefix}flywheel_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.blackened_gunmetal"),
    )
    _rotor_balance_arm(host, r, mats, prefix, 0.075 * radius, 0.030 * radius)


_ROTOR_BUILDERS = {
    "crowned_drum": _rotor_form_crowned_drum_build,
    "shaped_disc": _rotor_form_shaped_disc_build,
    "spoked_rim": _rotor_form_spoked_rim_build,
    "solid_disc": _rotor_form_solid_disc_build,
}


def _build_rotor(model, r: ResolvedConfig, mats: dict[str, str], carrier, provider):
    part = model.part("rotor", meta={"role": "rotor"})
    _ROTOR_BUILDERS[r.rotor_form](part, r, mats)

    if r.spindle_support == "opposed_bearings":
        part.visual(
            Cylinder(radius=r.axle_radius_m, length=2.0 * r.axle_half_m),
            material=mats["bright"],
            name="spindle_support__opposed_bearings__rotor_axle", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
        )
        for suffix, sign in enumerate((1.0, -1.0)):
            part.visual(
                Cylinder(radius=r.axle_radius_m + 0.0016, length=0.006),
                origin=Origin(xyz=(0.0, 0.0, sign * (r.axle_half_m - 0.010))),
                material=mats["bearing"],
                name=f"spindle_support__opposed_bearings__axle_journal_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
            )
    else:
        top = 0.10 * r.flywheel_radius_m
        bottom = r.race_offset_m - 0.5 * r.race_len_m - 0.003
        part.visual(
            Cylinder(radius=r.axle_radius_m, length=top - bottom),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * (top + bottom))),
            material=mats["bright"],
            name="spindle_support__bearing_spider__rotor_axle", material_class_id=("metal.brushed_silver" if r.palette_style in {"aged_steel", "dark_chrome", "brass_accent"} else "metal.chrome_polished"),
        )
        part.visual(
            Cylinder(radius=r.axle_radius_m + 0.0016, length=0.006),
            origin=Origin(xyz=(0.0, 0.0, bottom + 0.005)),
            material=mats["bearing"],
            name="spindle_support__bearing_spider__axle_journal_0", material_class_id=("metal.stainless_matte" if r.palette_style in {"blackened_iron", "aged_steel", "dark_chrome"} else "metal.brass_aged"),
        )

    consumer = AxisInterface(
        name="rotor_spin_axis",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "rotor_spin",
        ArticulationType.CONTINUOUS,
        parent=carrier,
        child=part,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=1.2, velocity=140.0),
        motion_properties=MotionProperties(damping=0.001, friction=0.0005),
        meta={
            "mechanism": "flywheel spindle running in the innermost gimbal bearing",
            "positive_motion": "spins the flywheel about the innermost ring's spin axis",
        },
    )
    register_interface_mate(model, "rotor_spin", mate)
    return part


def build_pictureX_0611_gyroscope_with_spinning_wheel_and_gimbal_rings(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_gyroscope_with_spinning_wheel_and_gimbal_rings",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": (
                "a flywheel rotor spinning in a stack of nested gimbal rings whose "
                "trunnion axes all pass through one gimbal centre"
            ),
        },
    )
    mats = _materials(model, r)
    base = _SUPPORT_BUILDERS[r.support_base](model, r, mats)
    provider = AxisInterface(
        name="gimbal_pole_axis",
        point=(0.0, 0.0, r.gimbal_center_z_m),
        axis=r.support_axis,
        radial=r.support_radial,
    )
    parent = base
    for index in range(r.ring_count):
        parent, provider = _build_ring(model, r, mats, index, parent, provider)
    _build_rotor(model, r, mats, parent, provider)

    tilt = r.tilt_limit_rad
    azimuth = r.azimuth_limit_rad
    risk: list[dict[str, float]] = [
        {"gimbal_axis_1": tilt, "rotor_spin": math.pi / 2.0},
        {"gimbal_axis_1": -tilt, "rotor_spin": -math.pi / 2.0},
        {"gimbal_axis_0": azimuth, "gimbal_axis_1": tilt},
        {"gimbal_axis_0": -azimuth, "gimbal_axis_1": -tilt},
        {"gimbal_axis_1": 0.0, "rotor_spin": math.pi},
    ]
    if r.ring_count == 3:
        risk.append({"gimbal_axis_1": tilt, "gimbal_axis_2": tilt, "rotor_spin": 1.0})
        risk.append({"gimbal_axis_1": -tilt, "gimbal_axis_2": tilt, "rotor_spin": -1.0})
    model.meta["risk_poses"] = tuple(risk)
    model.meta["coupled_joint_pairs"] = (
        ("gimbal_axis_0", "gimbal_axis_1"),
        ("gimbal_axis_1", "rotor_spin"),
    )
    return model


def build_seeded_pictureX_0611_gyroscope_with_spinning_wheel_and_gimbal_rings(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_gyroscope_with_spinning_wheel_and_gimbal_rings(
        config_from_seed(seed), assets=assets
    )


# --- authored tests -------------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _meshes_materialized(model: ArticulatedObject) -> bool:
    """False while the preflight probe stands in for real mesh assets."""

    for part in model.parts:
        for visual in getattr(part, "visuals", []):
            filename = getattr(getattr(visual, "geometry", None), "filename", None)
            if filename and "__preflight_probe__" in str(filename):
                return False
    return True


def _chain_joint_names(r: ResolvedConfig) -> tuple[str, ...]:
    names = [f"gimbal_axis_{index}" for index in range(r.ring_count)]
    names.append("rotor_spin")
    return tuple(names)


def _world_axes(model: ArticulatedObject, r: ResolvedConfig):
    """World-frame direction of every chain axis at the neutral pose."""

    rotation = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    joints = {joint.name: joint for joint in model.articulations}
    axes = []
    for name in _chain_joint_names(r):
        joint = joints.get(name)
        if joint is None:
            return []
        rotation = _mat_mul(rotation, _rpy_matrix(tuple(joint.origin.rpy)))
        axes.append(_mat_vec(rotation, tuple(joint.axis)))
    return axes


def run_pictureX_0611_gyroscope_with_spinning_wheel_and_gimbal_rings_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    bases = _parts_by_role(model, "support_base")
    outers = _parts_by_role(model, "outer_gimbal_ring")
    mids = _parts_by_role(model, "mid_gimbal_ring")
    carriers = _parts_by_role(model, "spindle_carrier")
    rotors = _parts_by_role(model, "rotor")
    joints = {joint.name: joint for joint in model.articulations}
    chain = _chain_joint_names(r)
    visual_names = {visual.name or "" for part in model.parts for visual in part.visuals}

    def count(fragment: str) -> int:
        return sum(1 for name in visual_names if fragment in name)

    spin_joint = joints.get("rotor_spin")
    azimuth_joint = joints.get("gimbal_axis_0")
    ctx.check(
        "category_anchor: a flywheel rotor spins in a nested gimbal stack on one grounded support",
        len(bases) == 1
        and len(outers) == 1
        and len(mids) == r.mid_ring_count
        and len(carriers) == 1
        and len(rotors) == 1
        and len(model.parts) == r.ring_count + 2
        and len(model.articulations) == r.ring_count + 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "support_base"
        and all(name in joints for name in chain)
        and azimuth_joint is not None
        and azimuth_joint.articulation_type == ArticulationType.REVOLUTE
        and azimuth_joint.parent == "support_base"
        and spin_joint is not None
        and spin_joint.articulation_type == ArticulationType.CONTINUOUS
        and spin_joint.parent == "spindle_carrier"
        and spin_joint.child == "rotor",
        details=(
            f"parts={[part.name for part in model.parts]} joints={sorted(joints)} "
            f"ring_count={r.ring_count}"
        ),
    )

    axes = _world_axes(model, r)
    origins_ok = all(
        max(abs(value) for value in joints[name].origin.xyz) < 1e-9 for name in chain[1:]
    )
    base_origin = joints[chain[0]].origin.xyz if chain[0] in joints else (9.0, 9.0, 9.0)
    orthogonal = len(axes) == len(chain) and all(
        abs(sum(axes[k][i] * axes[k + 1][i] for i in range(3))) < 1e-6 for k in range(len(axes) - 1)
    )
    registered = all((joints[name].meta or {}).get("interface_mate") is not None for name in chain)
    ctx.check(
        "category_anchor: every gimbal axis passes through the common centre and is "
        "orthogonal to its parent",
        origins_ok
        and orthogonal
        and registered
        and abs(base_origin[2] - r.gimbal_center_z_m) < 1e-9
        and abs(base_origin[0]) < 1e-9
        and abs(base_origin[1]) < 1e-9
        and all(abs(sum(value * value for value in axis) - 1.0) < 1e-9 for axis in axes),
        details=(
            f"base_origin={base_origin} world_axes={axes} "
            f"nested_origins_at_centre={origins_ok} registered={registered}"
        ),
    )

    carrier_index = r.ring_count - 1
    nesting_ok = all(
        r.ring_outer_m[k + 1] + 1e-9 <= r.ring_inner_m[k] - r.ring_gap_m + 1e-6
        for k in range(r.ring_count - 1)
    )
    ctx.check(
        "category_anchor: every nested member keeps a real running clearance inside its parent",
        nesting_ok
        and r.ring_gap_m >= 0.014
        and r.ring_inner_m[carrier_index] > 0.0
        and r.rotor_bore_m > r.rotor_clear_m
        and ROTOR_ENVELOPE_FACTOR * r.flywheel_radius_m <= r.rotor_bore_m - r.rotor_clear_m + 1e-9
        and r.rotor_envelope_m <= r.ring_outer_m[carrier_index] + 1e-9
        and (r.spindle_support == "bearing_spider" or r.axle_half_m + 0.002 <= r.spin_seat_m),
        details=(
            f"ring_outer={r.ring_outer_m} ring_inner={r.ring_inner_m} gap={r.ring_gap_m} "
            f"bore={r.rotor_bore_m} flywheel={r.flywheel_radius_m} "
            f"rotor_envelope={r.rotor_envelope_m}"
        ),
    )

    support_prefix = f"support_base__{r.support_base}__"
    if r.support_base == "tripod_legs":
        support_ok = (
            count(f"{support_prefix}leg_") == 3 and count(f"{support_prefix}foot_pad_") == 3
        )
    elif r.support_base == "wall_bracket":
        support_ok = (
            f"{support_prefix}wall_plate" in visual_names
            and count(f"{support_prefix}support_arm_") == 2
            and count(f"{support_prefix}mounting_screw_") == 4
            and f"{support_prefix}bearing_yoke" in visual_names
            and abs(r.support_axis[1] + 1.0) < 1e-9
        )
    elif r.support_base == "weighted_pedestal":
        support_ok = (
            f"{support_prefix}weighted_base" in visual_names
            and f"{support_prefix}pedestal_collar" in visual_names
            and f"{support_prefix}upright_support" in visual_names
        )
    else:
        support_ok = (
            f"{support_prefix}weighted_column" in visual_names
            and f"{support_prefix}bearing_flange" in visual_names
        )
    ctx.check(
        "category_anchor: support_base identity",
        support_ok
        and f"{support_prefix}bearing_housing" in visual_names
        and (r.support_base == "wall_bracket") == (abs(r.support_axis[2]) < 0.5),
        details=f"support_base={r.support_base} axis={r.support_axis}",
    )

    ctx.check(
        "category_anchor: ring_stack identity",
        (r.ring_count == 3) == (r.ring_stack == "three_ring_gimbal")
        and len(mids) == (1 if r.ring_stack == "three_ring_gimbal" else 0)
        and (
            r.ring_stack == "two_ring_gimbal"
            or (
                joints["gimbal_axis_1"].parent == "outer_gimbal_ring"
                and joints["gimbal_axis_1"].child == "mid_gimbal_ring"
                and joints["gimbal_axis_2"].parent == "mid_gimbal_ring"
                and joints["gimbal_axis_2"].child == "spindle_carrier"
            )
        )
        and (
            r.ring_stack == "three_ring_gimbal"
            or (
                joints["gimbal_axis_1"].parent == "outer_gimbal_ring"
                and joints["gimbal_axis_1"].child == "spindle_carrier"
            )
        ),
        details=f"ring_stack={r.ring_stack} mids={len(mids)} joints={sorted(joints)}",
    )

    section_prefix = f"ring_section__{r.ring_section}__"
    section_ok = count(f"{section_prefix}ring_band_") == r.ring_count
    if r.ring_section == "flat_band":
        section_ok = section_ok and count(f"{section_prefix}edge_bead_") == r.ring_count
    elif r.ring_section == "tubular_hoop":
        section_ok = section_ok and count(f"{section_prefix}bearing_seat_") == 2 * (
            r.ring_count - 1
        )
    else:
        section_ok = (
            section_ok
            and count(f"{section_prefix}carrier_pole_bar_") == 1
            and count(f"{section_prefix}carrier_side_bar_") == 2
            and r.carrier_bar_m > 0.0
            and r.rotor_bore_m > 0.0
        )
    ctx.check(
        "category_anchor: ring_section identity",
        section_ok and count(f"{section_prefix}pole_pin_") == 2 * r.ring_count - 1,
        details=(
            f"ring_section={r.ring_section} bands={count(f'{section_prefix}ring_band_')} "
            f"pins={count(f'{section_prefix}pole_pin_')}"
        ),
    )

    spindle_prefix = f"spindle_support__{r.spindle_support}__"
    if r.spindle_support == "opposed_bearings":
        spindle_ok = (
            count(f"{spindle_prefix}spin_sleeve_") == 2
            and count(f"{spindle_prefix}spin_bearing_cap_") == 2
            and f"{spindle_prefix}rotor_axle" in visual_names
            and r.axle_half_m > 0.0
        )
    else:
        spindle_ok = (
            f"{spindle_prefix}spindle_race" in visual_names
            and count(f"{spindle_prefix}bearing_arm_") == 2
            and count(f"{spindle_prefix}bearing_post_") == 2
            and r.race_offset_m < 0.0
        )
    ctx.check(
        "category_anchor: spindle_support identity",
        spindle_ok,
        details=f"spindle_support={r.spindle_support} race_offset={r.race_offset_m}",
    )

    rotor_prefix = f"rotor_form__{r.rotor_form}__"
    if r.rotor_form == "spoked_rim":
        rotor_ok = (
            count(f"{rotor_prefix}spoke_") == SPOKE_COUNT
            and f"{rotor_prefix}inertia_rim" in visual_names
            and f"{rotor_prefix}perimeter_band" in visual_names
        )
    elif r.rotor_form == "shaped_disc":
        rotor_ok = (
            f"{rotor_prefix}flywheel" in visual_names
            and f"{rotor_prefix}perimeter_band" in visual_names
            and f"{rotor_prefix}spindle_cap" in visual_names
        )
    elif r.rotor_form == "solid_disc":
        rotor_ok = (
            f"{rotor_prefix}flywheel" in visual_names
            and f"{rotor_prefix}disc_phase_mark" in visual_names
            and f"{rotor_prefix}balance_weight" not in visual_names
        )
    else:
        rotor_ok = (
            f"{rotor_prefix}flywheel" in visual_names
            and f"{rotor_prefix}flywheel_hub" in visual_names
            and f"{rotor_prefix}balance_weight" in visual_names
        )
    ctx.check(
        "category_anchor: rotor_form identity",
        rotor_ok and r.flywheel_radius_m > 0.005,
        details=f"rotor_form={r.rotor_form} flywheel_radius={r.flywheel_radius_m}",
    )

    index_prefix = f"index_hardware__{r.index_hardware}__"
    if r.index_hardware == "pointer_mast":
        index_ok = (
            f"{index_prefix}index_pointer" in visual_names
            and f"{index_prefix}pointer_tip" in visual_names
            and r.mast_len_m > 0.4 * r.outer_ring_radius_m
        )
    else:
        index_ok = (
            f"{index_prefix}pole_trunnion" in visual_names
            and f"{index_prefix}pole_cap" in visual_names
            and count("index_hardware__pointer_mast__") == 0
        )
    ctx.check(
        "category_anchor: index_hardware identity",
        index_ok,
        details=f"index_hardware={r.index_hardware} mast_len={r.mast_len_m}",
    )

    stop_prefix = "gimbal_motion__limited_stops__"
    if r.gimbal_motion == "limited_stops":
        motion_ok = (
            f"{stop_prefix}stop_collar" in visual_names
            and f"{stop_prefix}tilt_shoulder_collar" in visual_names
            and f"{stop_prefix}azimuth_stop_0" in visual_names
            and f"{stop_prefix}azimuth_stop_1" in visual_names
            and f"{stop_prefix}azimuth_stop_pin" in visual_names
            and count(f"{stop_prefix}tilt_stop_") == 2
            and f"{stop_prefix}tilt_lug_0" in visual_names
            and abs(r.azimuth_limit_rad - 1.0) < 1e-9
            and abs(r.tilt_limit_rad - 0.75) < 1e-9
            and r.stop_block_angle_rad
            > r.azimuth_limit_rad + r.stop_pin_half_rad + r.stop_block_half_rad
        )
    else:
        motion_ok = (
            count(stop_prefix) == 0
            and abs(r.azimuth_limit_rad - math.pi) < 1e-9
            and abs(r.tilt_limit_rad - 1.35) < 1e-9
        )
    ctx.check(
        "category_anchor: gimbal_motion identity",
        motion_ok
        and abs(joints[chain[0]].motion_limits.upper - r.azimuth_limit_rad) < 1e-9
        and abs(joints[chain[1]].motion_limits.upper - r.tilt_limit_rad) < 1e-9,
        details=(
            f"gimbal_motion={r.gimbal_motion} azimuth={r.azimuth_limit_rad} "
            f"tilt={r.tilt_limit_rad} block={r.stop_block_angle_rad}"
        ),
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )

    meshes_ready = _meshes_materialized(model)
    if meshes_ready:
        ctx.fail_if_isolated_parts()
        ctx.warn_if_part_contains_disconnected_geometry_islands()
        ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.002)

        def _centre(bounds):
            if bounds is None:
                return None
            return tuple(0.5 * (bounds[0][i] + bounds[1][i]) for i in range(3))

        def _moved(part, elem, joint, value):
            rest = _centre(ctx.part_element_world_aabb(part, elem=elem))
            with ctx.pose({joint: value}):
                moved = _centre(ctx.part_element_world_aabb(part, elem=elem))
            if rest is None or moved is None:
                return None
            return math.dist(rest, moved)

        # A world AABB is a degenerate motion proxy for a solid of revolution: on a
        # rotor whose axle half length happens to match its flywheel radius the box is
        # almost invariant under a real tilt.  Track named off-axis elements instead.
        trunnion = f"ring_section__{r.ring_section}__trunnion_bearing_0_0"
        swing = _moved(outers[0], trunnion, joints[chain[0]], 0.45 * r.azimuth_limit_rad)
        ctx.check(
            "the azimuth joint really swings the whole nested stack",
            swing is not None and swing > 0.15 * r.outer_ring_radius_m,
            details=f"trunnion travel={swing} outer_radius={r.outer_ring_radius_m}",
        )

        journal = f"spindle_support__{r.spindle_support}__axle_journal_0"
        marker = f"rotor_form__{r.rotor_form}__" + (
            "disc_phase_mark" if r.rotor_form == "solid_disc" else "balance_weight"
        )
        tilt_travel = [
            _moved(rotors[0], elem, joints[chain[1]], r.tilt_limit_rad)
            for elem in (journal, marker)
        ]
        ctx.check(
            "the first gimbal joint tilts the rotor out of its rest plane",
            any(value is not None and value > 0.25 * r.flywheel_radius_m for value in tilt_travel),
            details=f"tilt travel={tilt_travel} flywheel_radius={r.flywheel_radius_m}",
        )

        spin_travel = _moved(rotors[0], marker, joints["rotor_spin"], math.pi / 2.0)
        ctx.check(
            "the flywheel spins independently on its own spindle",
            spin_travel is not None and spin_travel > 0.5 * r.flywheel_radius_m,
            details=f"spin travel={spin_travel} flywheel_radius={r.flywheel_radius_m}",
        )

    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "tightest_three_ring_cage_on_a_wall",
        {
            "support_base": "wall_bracket",
            "ring_stack": "three_ring_gimbal",
            "ring_section": "carrier_frame",
            "spindle_support": "bearing_spider",
            "rotor_form": "spoked_rim",
            "index_hardware": "pointer_mast",
            "gimbal_motion": "limited_stops",
            "outer_ring_radius_m": 0.110,
            "ring_width_ratio": 0.17,
            "rotor_radius_ratio": 0.62,
            "gimbal_rise_m": 0.075,
        },
        reason="smallest outer ring with the widest bands, three nested members and a "
        "rectangular carrier, so the innermost bore and the spider are at their tightest, "
        "hung on the horizontal wall axis at the lowest mounting height",
    ),
    corner_case(
        "widest_three_ring_opposed_carrier_frame",
        {
            "support_base": "tripod_legs",
            "ring_stack": "three_ring_gimbal",
            "ring_section": "carrier_frame",
            "spindle_support": "opposed_bearings",
            "rotor_form": "crowned_drum",
            "index_hardware": "plain_trunnion",
            "gimbal_motion": "limited_stops",
            "outer_ring_radius_m": 0.160,
            "ring_width_ratio": 0.17,
            "rotor_radius_ratio": 0.88,
            "gimbal_rise_m": 0.220,
        },
        reason="largest rotor the rectangular carrier can hold, on the deepest crowned "
        "drum, with three rings and both end-stop mechanisms present on a tripod",
    ),
    corner_case(
        "max_rotor_in_a_tubular_spider",
        {
            "support_base": "slender_column",
            "ring_stack": "two_ring_gimbal",
            "ring_section": "tubular_hoop",
            "spindle_support": "bearing_spider",
            "rotor_form": "shaped_disc",
            "index_hardware": "pointer_mast",
            "gimbal_motion": "free_swing",
            "outer_ring_radius_m": 0.160,
            "ring_width_ratio": 0.10,
            "rotor_radius_ratio": 0.88,
            "gimbal_rise_m": 0.220,
        },
        reason="the biggest flywheel and the deepest spider offset in the thinnest tube "
        "hoops, with the full +-pi azimuth and +-1.35 rad tilt travel",
    ),
    corner_case(
        "shortest_support_under_the_largest_ring",
        {
            "support_base": "weighted_pedestal",
            "ring_stack": "two_ring_gimbal",
            "ring_section": "flat_band",
            "spindle_support": "opposed_bearings",
            "rotor_form": "solid_disc",
            "index_hardware": "pointer_mast",
            "gimbal_motion": "free_swing",
            "outer_ring_radius_m": 0.160,
            "ring_width_ratio": 0.10,
            "rotor_radius_ratio": 0.88,
            "gimbal_rise_m": 0.075,
        },
        reason="the cast base and its bearing pedestal have the least height to work with "
        "while carrying the largest hoop and the heaviest solid disc",
    ),
    corner_case(
        "wall_mounted_opposed_solid_disc",
        {
            "support_base": "wall_bracket",
            "ring_stack": "two_ring_gimbal",
            "ring_section": "carrier_frame",
            "spindle_support": "opposed_bearings",
            "rotor_form": "solid_disc",
            "index_hardware": "plain_trunnion",
            "gimbal_motion": "free_swing",
            "outer_ring_radius_m": 0.132,
            "ring_width_ratio": 0.14,
            "rotor_radius_ratio": 0.88,
            "gimbal_rise_m": 0.150,
        },
        reason="the rectangular carrier's spin bars carry the widest solid disc on the "
        "horizontal wall axis, where the whole stack cantilevers off one arm",
    ),
    corner_case(
        "three_ring_tube_stack_with_stops",
        {
            "support_base": "slender_column",
            "ring_stack": "three_ring_gimbal",
            "ring_section": "tubular_hoop",
            "spindle_support": "opposed_bearings",
            "rotor_form": "spoked_rim",
            "index_hardware": "plain_trunnion",
            "gimbal_motion": "limited_stops",
            "outer_ring_radius_m": 0.110,
            "ring_width_ratio": 0.10,
            "rotor_radius_ratio": 0.88,
            "gimbal_rise_m": 0.075,
        },
        reason="thin tube hoops at the smallest ring size with a third member and the "
        "full stop package on the slenderest column",
    ),
    corner_case(
        "three_ring_flat_band_spider",
        {
            "support_base": "tripod_legs",
            "ring_stack": "three_ring_gimbal",
            "ring_section": "flat_band",
            "spindle_support": "bearing_spider",
            "rotor_form": "crowned_drum",
            "index_hardware": "pointer_mast",
            "gimbal_motion": "free_swing",
            "outer_ring_radius_m": 0.110,
            "ring_width_ratio": 0.17,
            "rotor_radius_ratio": 0.88,
            "gimbal_rise_m": 0.120,
        },
        reason="the deepest rotor back-reach (crowned drum) hung on a spider inside the "
        "smallest three-ring stack, where the race offset is closest to the carrier rim",
    ),
    corner_case(
        "smallest_flywheel_in_the_widest_ring",
        {
            "support_base": "weighted_pedestal",
            "ring_stack": "two_ring_gimbal",
            "ring_section": "tubular_hoop",
            "spindle_support": "opposed_bearings",
            "rotor_form": "shaped_disc",
            "index_hardware": "plain_trunnion",
            "gimbal_motion": "limited_stops",
            "outer_ring_radius_m": 0.160,
            "ring_width_ratio": 0.17,
            "rotor_radius_ratio": 0.62,
            "gimbal_rise_m": 0.220,
        },
        reason="the longest spin sleeves and axle relative to the flywheel, so the "
        "bearing seats reach furthest inboard past the disc",
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
    "build_pictureX_0611_gyroscope_with_spinning_wheel_and_gimbal_rings",
    "build_seeded_pictureX_0611_gyroscope_with_spinning_wheel_and_gimbal_rings",
    "run_pictureX_0611_gyroscope_with_spinning_wheel_and_gimbal_rings_tests",
]
