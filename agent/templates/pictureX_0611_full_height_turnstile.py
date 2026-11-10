# SPDX-License-Identifier: Apache-2.0

"""Self-contained full-height security turnstile template.

The grounded ``guard_frame`` part carries a real floor bearing race and a real
overhead bearing race on one vertical spindle line — both are CadQuery annuli
with a running bore, so the rotor spindle passes through them instead of into
them.  Both races are tied back to the guard by a floor ring and a head ring
plus radial braces, so the fixed structure is one welded body whatever the guard
candidate builds.  The ``rotor`` part turns REVOLUTE about +z between the two
races through one full wing sector either way.  The rotor reach is the guard
radius minus an 80 mm running clearance, so the swept envelope stays inside the
guard at every angle for every guard candidate.

Five slots vary without touching that chain: ``guard_frame`` (open four-post
portal, barred portal, arc-rail cage, cylindrical bar cage, twin curved panels),
``header_form`` (flat slab housing or a double-rib circular arch on posts),
``rotor_form`` (arm ladder, braced arm ladder, stile-and-rung ladder, dense
curved-bar ladder, vertical-bar palisade), ``access_control`` (post box,
stand-off bracket with keypad, free-standing reader post, header indicator
panel) and ``second_mechanism`` (hinged service guard leaf, breakaway rotor
wing, ratchet ring with release pawl, overhead indexing cam with follower).
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
    MotionProperties,
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

GuardFrame = Literal[
    "portal_post_frame",
    "barred_portal_frame",
    "arc_rail_cage",
    "cylindrical_bar_cage",
    "curved_panel_cage",
]
HeaderForm = Literal["flat_header", "arched_header"]
RotorForm = Literal[
    "arm_tier_rotor",
    "braced_arm_rotor",
    "stile_rung_rotor",
    "curved_bar_rotor",
    "vertical_bar_rotor",
]
AccessControl = Literal[
    "post_reader_box",
    "bracket_reader_keypad",
    "standalone_reader_post",
    "header_indicator_panel",
]
SecondMechanism = Literal[
    "service_guard_leaf",
    "emergency_breakaway_wing",
    "locking_pawl_hub",
    "overhead_indexing_cam",
]
ServiceLeafHingeSide = Literal["left", "right"]
PaletteStyle = Literal["galvanized", "dark_zinc", "painted_blue", "stainless"]

GUARD_FRAMES: tuple[GuardFrame, ...] = (
    "portal_post_frame",
    "barred_portal_frame",
    "arc_rail_cage",
    "cylindrical_bar_cage",
    "curved_panel_cage",
)
HEADER_FORMS: tuple[HeaderForm, ...] = ("flat_header", "arched_header")
ROTOR_FORMS: tuple[RotorForm, ...] = (
    "arm_tier_rotor",
    "braced_arm_rotor",
    "stile_rung_rotor",
    "curved_bar_rotor",
    "vertical_bar_rotor",
)
ACCESS_CONTROLS: tuple[AccessControl, ...] = (
    "post_reader_box",
    "bracket_reader_keypad",
    "standalone_reader_post",
    "header_indicator_panel",
)
SECOND_MECHANISMS: tuple[SecondMechanism, ...] = (
    "service_guard_leaf",
    "emergency_breakaway_wing",
    "locking_pawl_hub",
    "overhead_indexing_cam",
)
SERVICE_LEAF_HINGE_SIDES: tuple[ServiceLeafHingeSide, ...] = ("left", "right")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "galvanized",
    "dark_zinc",
    "painted_blue",
    "stainless",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("guard_frame", GUARD_FRAMES),
        component_slot("header_form", HEADER_FORMS),
        component_slot("rotor_form", ROTOR_FORMS),
        component_slot("access_control", ACCESS_CONTROLS),
        component_slot("second_mechanism", SECOND_MECHANISMS),
        multiplicity_slot("wing_count", (3, 4), item_slot="rotor_form"),
        multiplicity_slot("tier_count", (6, 8, 11), item_slot="rotor_form"),
        multiplicity_slot("guard_member_count", (5, 8, 12), item_slot="guard_frame"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "galvanized": {
        "steel": (0.66, 0.69, 0.70, 1.0),
        "light": (0.75, 0.78, 0.79, 1.0),
        "dark": (0.22, 0.24, 0.25, 1.0),
        "housing": (0.58, 0.62, 0.64, 1.0),
        "reader": (0.06, 0.07, 0.075, 1.0),
        "accent": (0.12, 0.62, 0.25, 1.0),
    },
    "dark_zinc": {
        "steel": (0.44, 0.47, 0.49, 1.0),
        "light": (0.58, 0.61, 0.63, 1.0),
        "dark": (0.16, 0.17, 0.18, 1.0),
        "housing": (0.36, 0.39, 0.41, 1.0),
        "reader": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.85, 0.62, 0.14, 1.0),
    },
    "painted_blue": {
        "steel": (0.16, 0.32, 0.55, 1.0),
        "light": (0.28, 0.46, 0.70, 1.0),
        "dark": (0.10, 0.14, 0.22, 1.0),
        "housing": (0.20, 0.36, 0.58, 1.0),
        "reader": (0.06, 0.06, 0.08, 1.0),
        "accent": (0.90, 0.84, 0.24, 1.0),
    },
    "stainless": {
        "steel": (0.78, 0.79, 0.80, 1.0),
        "light": (0.86, 0.87, 0.88, 1.0),
        "dark": (0.30, 0.31, 0.32, 1.0),
        "housing": (0.70, 0.72, 0.73, 1.0),
        "reader": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.20, 0.55, 0.85, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
ROTOR_GUARD_CLEARANCE = 0.080   # rotor envelope to guard member inner face
FLOOR_BEARING_TOP = 0.120
BEARING_BORE_FIT = 0.0015       # running fit, well under the 1 mm assembly gap
HEADER_SLAB = 0.220
ARCH_RISE = 0.300
CAM_ROOM = 0.240                # clear height between top bearing and header
GUARD_HALF_ARC = math.radians(55.0)
ACCESS_ANGLE = math.radians(-46.0)
ACCESS_STANDOFF = 0.055
MECHANISM_STANDOFF = 0.110
CURVED_LEAF_STANDOFF = 0.075
CURVED_LEAF_SEGMENTS = 8
WING_FOOT_Z = 0.185             # rotor wing structure starts above the lower collar
WING_HEAD_DROP = 0.130          # and stops below the ratchet/bearing room
MEMBER_HALF_MAX = 0.030
RING_FRACTION = 0.98            # floor/head tie rings sit just inside the guard radius
RING_TUBE = 0.020
FLOOR_RING_Z = 0.030
RATCHET_TEETH = 24
HUB_DRUM_RADIUS = 0.100         # rotor hub drum used when a wing breaks away
FIT_GAP = 0.001                 # running gap that still counts as supported


@dataclass(frozen=True)
class Config:
    guard_frame: GuardFrame = "portal_post_frame"
    header_form: HeaderForm = "flat_header"
    rotor_form: RotorForm = "arm_tier_rotor"
    access_control: AccessControl = "post_reader_box"
    second_mechanism: SecondMechanism = "service_guard_leaf"
    service_leaf_hinge_side: ServiceLeafHingeSide = "right"
    wing_count: int = 3
    tier_count: int = 11
    guard_member_count: int = 5
    guard_radius_m: float | None = None
    overall_height_m: float | None = None
    spindle_radius_m: float | None = None
    palette_style: PaletteStyle = "galvanized"
    name: str = "pictureX_0611_full_height_turnstile"


@dataclass(frozen=True)
class ResolvedConfig:
    guard_frame: GuardFrame
    header_form: HeaderForm
    rotor_form: RotorForm
    access_control: AccessControl
    second_mechanism: SecondMechanism
    service_leaf_hinge_side: ServiceLeafHingeSide
    wing_count: int
    tier_count: int
    guard_member_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    guard_radius_m: float
    overall_height_m: float
    spindle_radius_m: float
    header_height_m: float
    header_face_y_m: float
    guard_top_z_m: float
    bearing_top_z_m: float
    ring_radius_m: float
    rotor_radius_m: float
    wing_z0_m: float
    wing_z1_m: float
    tier_pitch_m: float
    wing_pitch_rad: float
    guard_member_pitch_rad: float
    guard_member_half_m: float
    guard_depth_m: float
    access_z_m: float
    mechanism_radius_m: float
    ratchet_z_m: float
    ratchet_tip_radius_m: float
    cam_z_m: float
    rigid_wing_count: int
    wing_inner_radius_m: float
    hub_drum: bool
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x5F_11_A3_07)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        guard_frame=choices["guard_frame"],
        header_form=choices["header_form"],
        rotor_form=choices["rotor_form"],
        access_control=choices["access_control"],
        second_mechanism=choices["second_mechanism"],
        wing_count=choices["wing_count"],
        tier_count=choices["tier_count"],
        guard_member_count=choices["guard_member_count"],
        guard_radius_m=round(rng.uniform(0.45, 0.78), 4),
        overall_height_m=round(rng.uniform(2.10, 2.60), 4),
        spindle_radius_m=round(rng.uniform(0.026, 0.046), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        service_leaf_hinge_side=rng.choice(SERVICE_LEAF_HINGE_SIDES),
        name=f"full_height_turnstile_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "guard_frame": config.guard_frame,
            "header_form": config.header_form,
            "rotor_form": config.rotor_form,
            "access_control": config.access_control,
            "second_mechanism": config.second_mechanism,
            "wing_count": config.wing_count,
            "tier_count": config.tier_count,
            "guard_member_count": config.guard_member_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.service_leaf_hinge_side not in SERVICE_LEAF_HINGE_SIDES:
        raise ValueError(
            f"unsupported service_leaf_hinge_side: {config.service_leaf_hinge_side}"
        )
    if config.guard_radius_m is not None and not 0.45 <= float(config.guard_radius_m) <= 0.78:
        raise ValueError("guard_radius_m must be in [0.45, 0.78]")
    if config.overall_height_m is not None and not 2.10 <= float(config.overall_height_m) <= 2.60:
        raise ValueError("overall_height_m must be in [2.10, 2.60]")
    if (
        config.spindle_radius_m is not None
        and not 0.026 <= float(config.spindle_radius_m) <= 0.046
    ):
        raise ValueError("spindle_radius_m must be in [0.026, 0.046]")

    guard_r = (
        _clamp(config.guard_radius_m, 0.45, 0.78) if config.guard_radius_m is not None else 0.60
    )
    height = (
        _clamp(config.overall_height_m, 2.10, 2.60)
        if config.overall_height_m is not None
        else 2.32
    )
    spindle_r = (
        _clamp(config.spindle_radius_m, 0.026, 0.046)
        if config.spindle_radius_m is not None
        else 0.036
    )

    arched = config.header_form == "arched_header"
    header_h = ARCH_RISE if arched else HEADER_SLAB
    guard_top = height - header_h
    bearing_top = guard_top - CAM_ROOM
    rotor_r = guard_r - ROTOR_GUARD_CLEARANCE
    wing_z0 = WING_FOOT_Z
    wing_z1 = bearing_top - WING_HEAD_DROP
    tier_pitch = (wing_z1 - wing_z0) / max(1, int(config.tier_count) - 1)
    wing_pitch = 2.0 * math.pi / int(config.wing_count)
    member_pitch = 2.0 * GUARD_HALF_ARC / max(1, int(config.guard_member_count) - 1)
    member_half = min(MEMBER_HALF_MAX, 0.45 * guard_r * member_pitch)
    header_face = -0.36 * (2.0 * guard_r + 0.10)
    breakaway = config.second_mechanism == "emergency_breakaway_wing"
    rigid_wings = int(config.wing_count) - 1 if breakaway else int(config.wing_count)
    wing_inner = HUB_DRUM_RADIUS - 0.008 if breakaway else spindle_r - 0.006
    return ResolvedConfig(
        guard_frame=config.guard_frame,
        header_form=config.header_form,
        rotor_form=config.rotor_form,
        access_control=config.access_control,
        second_mechanism=config.second_mechanism,
        service_leaf_hinge_side=config.service_leaf_hinge_side,
        wing_count=int(config.wing_count),
        tier_count=int(config.tier_count),
        guard_member_count=int(config.guard_member_count),
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        guard_radius_m=guard_r,
        overall_height_m=height,
        spindle_radius_m=spindle_r,
        header_height_m=header_h,
        header_face_y_m=header_face,
        guard_top_z_m=guard_top,
        bearing_top_z_m=bearing_top,
        ring_radius_m=RING_FRACTION * guard_r,
        rotor_radius_m=rotor_r,
        wing_z0_m=wing_z0,
        wing_z1_m=wing_z1,
        tier_pitch_m=tier_pitch,
        wing_pitch_rad=wing_pitch,
        guard_member_pitch_rad=member_pitch,
        guard_member_half_m=member_half,
        guard_depth_m=guard_r * 1.05,
        access_z_m=0.52 * bearing_top,
        mechanism_radius_m=guard_r + MECHANISM_STANDOFF,
        ratchet_z_m=bearing_top - 0.075,
        ratchet_tip_radius_m=spindle_r + 0.070,
        cam_z_m=bearing_top + 0.075,
        rigid_wing_count=rigid_wings,
        wing_inner_radius_m=wing_inner,
        hub_drum=breakaway,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("guard_frame", config.guard_frame),
        ("header_form", config.header_form),
        ("rotor_form", config.rotor_form),
        ("access_control", config.access_control),
        ("second_mechanism", config.second_mechanism),
        ("wing_count", config.wing_count),
        ("tier_count", config.tier_count),
        ("guard_member_count", config.guard_member_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"fht_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _local_origin(
    origin: Origin | None, offset: tuple[float, float, float]
) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(value - shift for value, shift in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


def _tube_between(
    part,
    start,
    end,
    radius,
    material,
    name,
    offset: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    """One straight round member between two world points."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-6:
        return
    pitch = math.acos(_clamp(dz / length, -1.0, 1.0))
    yaw = math.atan2(dy, dx)
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=_local_origin(
            Origin(
                xyz=(
                    start[0] + 0.5 * dx,
                    start[1] + 0.5 * dy,
                    start[2] + 0.5 * dz,
                ),
                rpy=(0.0, pitch, yaw),
            ),
            offset,
        ),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _annulus(outer: float, inner: float, height: float, z0: float):
    """A real bearing race: the spindle runs through the bore, not into the ring."""
    return (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, z0 + 0.5 * height))
        .cylinder(height=height, radius=outer, direct=(0.0, 0.0, 1.0))
        .cut(
            cq.Workplane("XY")
            .transformed(offset=(0.0, 0.0, z0 + 0.5 * height))
            .cylinder(height=height * 3.0, radius=inner, direct=(0.0, 0.0, 1.0))
        )
    )


def _guard_stations(r: ResolvedConfig) -> list[tuple[float, float, float]]:
    """Repeated guard member stations as (x, y, yaw) for the active guard candidate.

    Both guard families repeat ``guard_member_count`` members per panel: the arc
    families spread them over the guard arc, the portal families spread them
    along the two straight side runs.
    """
    stations: list[tuple[float, float, float]] = []
    count = r.guard_member_count
    if r.guard_frame in ("portal_post_frame", "barred_portal_frame"):
        depth = r.guard_depth_m
        step = 2.0 * depth / max(1, count - 1)
        for side in (-1.0, 1.0):
            for k in range(count):
                stations.append((side * r.guard_radius_m, -depth + k * step, 0.0))
        return stations
    for panel in (0.0, math.pi):
        for k in range(count):
            angle = panel - GUARD_HALF_ARC + k * r.guard_member_pitch_rad
            stations.append(
                (
                    r.guard_radius_m * math.cos(angle),
                    r.guard_radius_m * math.sin(angle),
                    angle,
                )
            )
    return stations


def _arc_points(r: ResolvedConfig, panel: float, samples: int):
    step = 2.0 * GUARD_HALF_ARC / (samples - 1)
    return [
        (
            r.guard_radius_m * math.cos(panel - GUARD_HALF_ARC + i * step),
            r.guard_radius_m * math.sin(panel - GUARD_HALF_ARC + i * step),
        )
        for i in range(samples)
    ]


def _access_anchor(r: ResolvedConfig) -> tuple[float, float, float]:
    """Where the reader hardware clamps onto the guard the frame slot built."""
    if r.guard_frame in ("portal_post_frame", "barred_portal_frame"):
        return (r.guard_radius_m, -0.65 * r.guard_depth_m, 0.0)
    return (
        r.guard_radius_m * math.cos(ACCESS_ANGLE),
        r.guard_radius_m * math.sin(ACCESS_ANGLE),
        ACCESS_ANGLE,
    )


# --- guard frame candidates -----------------------------------------------------
def _guard_common(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Bearing races, tie rings and the reader strap shared by every guard."""
    host.visual(
        mesh_from_cadquery(
            _annulus(
                r.spindle_radius_m + 0.036,
                r.spindle_radius_m + BEARING_BORE_FIT,
                0.100,
                0.020,
            ),
            "fht_floor_bearing",
            tolerance=0.0018,
        ),
        material=mats["dark"],
        name="guard_frame__floor_bearing", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        mesh_from_cadquery(
            _annulus(
                r.spindle_radius_m + 0.034,
                r.spindle_radius_m + BEARING_BORE_FIT,
                0.090,
                r.bearing_top_z_m - 0.045,
            ),
            "fht_top_bearing",
            tolerance=0.0018,
        ),
        material=mats["dark"],
        name="guard_frame__top_bearing", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Box((0.200, 0.200, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, 0.012)),
        material=mats["steel"],
        name="guard_frame__floor_pivot_plate", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    # Floor and head tie rings: the two bearing races are welded back to the
    # guard members whatever arc or perimeter the guard candidate builds.
    for ring_index, (z, inner) in enumerate(
        ((FLOOR_RING_Z, 0.060), (r.bearing_top_z_m, r.spindle_radius_m + 0.030))
    ):
        ring_pts = [
            (
                r.ring_radius_m * math.cos(2.0 * math.pi * i / 24.0),
                r.ring_radius_m * math.sin(2.0 * math.pi * i / 24.0),
            )
            for i in range(25)
        ]
        for seg in range(24):
            _tube_between(
                host,
                (ring_pts[seg][0], ring_pts[seg][1], z),
                (ring_pts[seg + 1][0], ring_pts[seg + 1][1], z),
                RING_TUBE,
                mats["steel"],
                f"guard_frame__tie_ring_{ring_index}_{seg}",
            )
        for brace_index in range(4):
            angle = brace_index * math.pi / 2.0 + math.pi / 4.0
            _tube_between(
                host,
                (inner * math.cos(angle), inner * math.sin(angle), z),
                (r.ring_radius_m * math.cos(angle), r.ring_radius_m * math.sin(angle), z),
                0.018,
                mats["steel"],
                f"guard_frame__hub_brace_{ring_index}_{brace_index}",
            )
    # Every repeated guard member is stitched to both rings.
    for index, (sx, sy, _yaw) in enumerate(_guard_stations(r)):
        norm = math.hypot(sx, sy)
        ux, uy = sx / norm, sy / norm
        for ring_index, z in enumerate((FLOOR_RING_Z, r.bearing_top_z_m)):
            _tube_between(
                host,
                (ux * r.ring_radius_m, uy * r.ring_radius_m, z),
                (sx, sy, z),
                0.016,
                mats["steel"],
                f"guard_frame__member_tie_{ring_index}_{index}",
            )
    ax, ay, yaw = _access_anchor(r)
    host.visual(
        Box((0.050, 0.050, r.guard_top_z_m - 0.06)),
        origin=Origin(
            xyz=(ax, ay, 0.020 + 0.5 * (r.guard_top_z_m - 0.06)), rpy=(0.0, 0.0, yaw)
        ),
        material=mats["steel"],
        name="guard_frame__access_strap", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )


def _guard_frame_portal_post_frame_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Open four-post portal on a rectangular base-rail perimeter."""
    depth = r.guard_depth_m
    half = r.guard_member_half_m
    for index, (x, y, _yaw) in enumerate(_guard_stations(r)):
        host.visual(
            Box((2.0 * half, 2.0 * half, r.guard_top_z_m)),
            origin=Origin(xyz=(x, y, 0.5 * r.guard_top_z_m)),
            material=mats["steel"],
            name=f"guard_frame__portal_post_frame__post_{index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
        host.visual(
            Box((2.6 * half, 2.6 * half, 0.020)),
            origin=Origin(xyz=(x, y, 0.010)),
            material=mats["dark"],
            name=f"guard_frame__portal_post_frame__footplate_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    for side_index, sx in enumerate((-1.0, 1.0)):
        host.visual(
            Box((0.070, 2.0 * depth + 0.070, 0.060)),
            origin=Origin(xyz=(sx * r.guard_radius_m, 0.0, 0.030)),
            material=mats["steel"],
            name=f"guard_frame__portal_post_frame__base_rail_{side_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
        host.visual(
            Box((0.060, 2.0 * depth + 0.060, 0.055)),
            origin=Origin(xyz=(sx * r.guard_radius_m, 0.0, r.guard_top_z_m - 0.030)),
            material=mats["steel"],
            name=f"guard_frame__portal_post_frame__head_rail_{side_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    for end_index, sy in enumerate((-1.0, 1.0)):
        host.visual(
            Box((2.0 * r.guard_radius_m, 0.070, 0.060)),
            origin=Origin(xyz=(0.0, sy * depth, 0.030)),
            material=mats["steel"],
            name=f"guard_frame__portal_post_frame__threshold_{end_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )


def _guard_frame_barred_portal_frame_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """The same portal skeleton infilled with horizontal side bars."""
    depth = r.guard_depth_m
    half = r.guard_member_half_m
    for index, (x, y, _yaw) in enumerate(_guard_stations(r)):
        host.visual(
            Box((2.0 * half, 2.0 * half, r.guard_top_z_m)),
            origin=Origin(xyz=(x, y, 0.5 * r.guard_top_z_m)),
            material=mats["steel"],
            name=f"guard_frame__barred_portal_frame__post_{index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    span = r.guard_top_z_m - 0.16
    for side_index, sx in enumerate((-1.0, 1.0)):
        host.visual(
            Box((0.070, 2.0 * depth + 0.070, 0.060)),
            origin=Origin(xyz=(sx * r.guard_radius_m, 0.0, 0.030)),
            material=mats["steel"],
            name=f"guard_frame__barred_portal_frame__base_rail_{side_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
        for bar_index in range(10):
            z = 0.100 + (bar_index + 0.5) * span / 10.0
            host.visual(
                Cylinder(radius=0.014, length=2.0 * depth),
                origin=Origin(
                    xyz=(sx * r.guard_radius_m, 0.0, z), rpy=(math.pi / 2.0, 0.0, 0.0)
                ),
                material=mats["light"],
                name=f"guard_frame__barred_portal_frame__side_bar_{side_index}_{bar_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
            )
    for end_index, sy in enumerate((-1.0, 1.0)):
        host.visual(
            Box((2.0 * r.guard_radius_m, 0.070, 0.060)),
            origin=Origin(xyz=(0.0, sy * depth, 0.030)),
            material=mats["steel"],
            name=f"guard_frame__barred_portal_frame__threshold_{end_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )


def _guard_frame_arc_rail_cage_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Curved welded arc rails carried on box uprights."""
    for index, (x, y, yaw) in enumerate(_guard_stations(r)):
        host.visual(
            Box((2.0 * r.guard_member_half_m, 2.0 * r.guard_member_half_m, r.guard_top_z_m)),
            origin=Origin(xyz=(x, y, 0.5 * r.guard_top_z_m), rpy=(0.0, 0.0, yaw)),
            material=mats["steel"],
            name=f"guard_frame__arc_rail_cage__upright_{index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
        host.visual(
            Box((0.090, 0.090, 0.026)),
            origin=Origin(xyz=(x, y, 0.013), rpy=(0.0, 0.0, yaw)),
            material=mats["dark"],
            name=f"guard_frame__arc_rail_cage__shoe_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    rail_span = r.guard_top_z_m - 0.24
    for panel_index, panel in enumerate((0.0, math.pi)):
        pts = _arc_points(r, panel, 9)
        for level in range(9):
            z = 0.160 + (level + 0.5) * rail_span / 9.0
            for seg in range(len(pts) - 1):
                _tube_between(
                    host,
                    (pts[seg][0], pts[seg][1], z),
                    (pts[seg + 1][0], pts[seg + 1][1], z),
                    0.014,
                    mats["light"],
                    f"guard_frame__arc_rail_cage__rail_{panel_index}_{level}_{seg}",
                )


def _guard_frame_cylindrical_bar_cage_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """The arc cage closed into a cylinder by intermediate vertical bars."""
    for index, (x, y, yaw) in enumerate(_guard_stations(r)):
        host.visual(
            Box((2.0 * r.guard_member_half_m, 2.0 * r.guard_member_half_m, r.guard_top_z_m)),
            origin=Origin(xyz=(x, y, 0.5 * r.guard_top_z_m), rpy=(0.0, 0.0, yaw)),
            material=mats["steel"],
            name=f"guard_frame__cylindrical_bar_cage__upright_{index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    bar_z0 = 0.140
    bar_z1 = r.guard_top_z_m - 0.060
    for panel_index, panel in enumerate((0.0, math.pi)):
        step = 2.0 * GUARD_HALF_ARC / 24.0
        for bar_index in range(25):
            angle = panel - GUARD_HALF_ARC + bar_index * step
            host.visual(
                Cylinder(radius=0.011, length=bar_z1 - bar_z0),
                origin=Origin(
                    xyz=(
                        r.guard_radius_m * math.cos(angle),
                        r.guard_radius_m * math.sin(angle),
                        0.5 * (bar_z0 + bar_z1),
                    )
                ),
                material=mats["light"],
                name=f"guard_frame__cylindrical_bar_cage__cage_bar_{panel_index}_{bar_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
            )
        pts = _arc_points(r, panel, 13)
        for ring_index, z in enumerate((bar_z0 + 0.020, bar_z1 - 0.020)):
            for seg in range(len(pts) - 1):
                _tube_between(
                    host,
                    (pts[seg][0], pts[seg][1], z),
                    (pts[seg + 1][0], pts[seg + 1][1], z),
                    0.016,
                    mats["steel"],
                    f"guard_frame__cylindrical_bar_cage__hoop_{panel_index}_{ring_index}_{seg}",
                )


def _guard_frame_curved_panel_cage_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Twin curved rail panels on alternating heavy/light uprights and a floor rail."""
    for index, (x, y, yaw) in enumerate(_guard_stations(r)):
        heavy = index % 2 == 0
        host.visual(
            Cylinder(
                radius=r.guard_member_half_m if heavy else 0.65 * r.guard_member_half_m,
                length=r.guard_top_z_m,
            ),
            origin=Origin(xyz=(x, y, 0.5 * r.guard_top_z_m), rpy=(0.0, 0.0, yaw)),
            material=mats["steel"],
            name=f"guard_frame__curved_panel_cage__upright_{index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
        if heavy:
            host.visual(
                Box((0.080, 0.080, 0.020)),
                origin=Origin(xyz=(x, y, 0.010), rpy=(0.0, 0.0, yaw)),
                material=mats["dark"],
                name=f"guard_frame__curved_panel_cage__shoe_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
            )
    rail_span = r.guard_top_z_m - 0.26
    for panel_index, panel in enumerate((0.0, math.pi)):
        pts = _arc_points(r, panel, 11)
        for level in range(12):
            z = 0.180 + (level + 0.5) * rail_span / 12.0
            for seg in range(len(pts) - 1):
                _tube_between(
                    host,
                    (pts[seg][0], pts[seg][1], z),
                    (pts[seg + 1][0], pts[seg + 1][1], z),
                    0.012,
                    mats["light"],
                    f"guard_frame__curved_panel_cage__rail_{panel_index}_{level}_{seg}",
                )
    host.visual(
        Box((2.0 * r.guard_radius_m + 0.06, 0.075, 0.040)),
        origin=Origin(xyz=(0.0, 0.0, 0.020)),
        material=mats["steel"],
        name="guard_frame__curved_panel_cage__floor_mount_rail", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )


_GUARD_FRAME_BUILDERS = {
    "portal_post_frame": _guard_frame_portal_post_frame_build,
    "barred_portal_frame": _guard_frame_barred_portal_frame_build,
    "arc_rail_cage": _guard_frame_arc_rail_cage_build,
    "cylindrical_bar_cage": _guard_frame_cylindrical_bar_cage_build,
    "curved_panel_cage": _guard_frame_curved_panel_cage_build,
}


# --- header candidates ----------------------------------------------------------
def _header_form_flat_header_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Flat slab drive housing with a bottom plate and a front fascia."""
    span = 2.0 * r.guard_radius_m + 0.10
    depth = span * 0.72
    host.visual(
        Box((span, depth, HEADER_SLAB + 0.020)),
        origin=Origin(xyz=(0.0, 0.0, r.guard_top_z_m + 0.5 * HEADER_SLAB - 0.010)),
        material=mats["housing"],
        name="header_form__flat_header__housing_slab", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Box((span - 0.080, depth - 0.080, 0.030)),
        origin=Origin(xyz=(0.0, 0.0, r.guard_top_z_m - 0.010)),
        material=mats["dark"],
        name="header_form__flat_header__housing_bottom", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Box((span, 0.045, 0.090)),
        origin=Origin(
            xyz=(0.0, r.header_face_y_m - 0.015, r.guard_top_z_m + HEADER_SLAB - 0.060)
        ),
        material=mats["steel"],
        name="header_form__flat_header__fascia", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )


def _header_form_arched_header_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Double-rib circular arch springing off two posts over the same housing."""
    span = 2.0 * r.guard_radius_m + 0.10
    depth = span * 0.72
    host.visual(
        Box((span, depth, HEADER_SLAB + 0.020)),
        origin=Origin(xyz=(0.0, 0.0, r.guard_top_z_m + 0.5 * HEADER_SLAB - 0.010)),
        material=mats["housing"],
        name="header_form__arched_header__housing_slab", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Box((span - 0.080, depth - 0.080, 0.030)),
        origin=Origin(xyz=(0.0, 0.0, r.guard_top_z_m - 0.010)),
        material=mats["dark"],
        name="header_form__arched_header__housing_bottom", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    span_half = r.guard_radius_m
    radius = (span_half * span_half + ARCH_RISE * ARCH_RISE) / (2.0 * ARCH_RISE)
    center_z = r.guard_top_z_m - (radius - ARCH_RISE)
    half_angle = math.asin(_clamp(span_half / radius, -1.0, 1.0))
    segments = 10
    profile = [
        (
            radius * math.sin(-half_angle + 2.0 * half_angle * i / segments),
            center_z + radius * math.cos(-half_angle + 2.0 * half_angle * i / segments),
        )
        for i in range(segments + 1)
    ]
    for rib_index, y_off in enumerate((-0.055, 0.055)):
        for seg in range(segments):
            _tube_between(
                host,
                (profile[seg][0], y_off, profile[seg][1]),
                (profile[seg + 1][0], y_off, profile[seg + 1][1]),
                0.022,
                mats["steel"],
                f"header_form__arched_header__arch_rib_{rib_index}_{seg}",
            )
    for tie_index in (2, 5, 8):
        x, z = profile[tie_index]
        _tube_between(
            host,
            (x, -0.055, z),
            (x, 0.055, z),
            0.014,
            mats["steel"],
            f"header_form__arched_header__arch_tie_{tie_index}",
        )
    for side_index, sx in enumerate((-1.0, 1.0)):
        host.visual(
            Box((0.080, 0.150, r.guard_top_z_m)),
            origin=Origin(xyz=(sx * span_half, 0.0, 0.5 * r.guard_top_z_m)),
            material=mats["steel"],
            name=f"header_form__arched_header__arch_post_{side_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
        host.visual(
            Box((0.100, 0.170, 0.030)),
            origin=Origin(xyz=(sx * span_half, 0.0, r.guard_top_z_m - 0.015)),
            material=mats["dark"],
            name=f"header_form__arched_header__arch_cap_plate_{side_index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )


_HEADER_FORM_BUILDERS = {
    "flat_header": _header_form_flat_header_build,
    "arched_header": _header_form_arched_header_build,
}


# --- access control candidates --------------------------------------------------
def _access_control_post_reader_box_build(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    ax, ay, yaw = _access_anchor(r)
    ux, uy = math.cos(yaw), math.sin(yaw)
    host.visual(
        Box((0.170, 0.110, 0.300)),
        origin=Origin(xyz=(ax + ux * 0.070, ay + uy * 0.070, r.access_z_m), rpy=(0.0, 0.0, yaw)),
        material=mats["housing"],
        name="access_control__post_reader_box__enclosure", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Box((0.018, 0.090, 0.200)),
        origin=Origin(
            xyz=(ax + ux * 0.152, ay + uy * 0.152, r.access_z_m + 0.010), rpy=(0.0, 0.0, yaw)
        ),
        material=mats["reader"],
        name="access_control__post_reader_box__reader_face", material_class_id="tech.control_interface",
    )
    host.visual(
        Box((0.014, 0.050, 0.016)),
        origin=Origin(
            xyz=(ax + ux * 0.162, ay + uy * 0.162, r.access_z_m + 0.075), rpy=(0.0, 0.0, yaw)
        ),
        material=mats["accent"],
        name="access_control__post_reader_box__indicator", material_class_id="tech.emissive_surface",
    )


def _access_control_bracket_reader_keypad_build(
    host, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    ax, ay, yaw = _access_anchor(r)
    ux, uy = math.cos(yaw), math.sin(yaw)
    host.visual(
        Box((0.090, 0.105, 0.055)),
        origin=Origin(xyz=(ax + ux * 0.045, ay + uy * 0.045, r.access_z_m), rpy=(0.0, 0.0, yaw)),
        material=mats["steel"],
        name="access_control__bracket_reader_keypad__bracket", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Box((0.060, 0.100, 0.150)),
        origin=Origin(
            xyz=(ax + ux * 0.108, ay + uy * 0.108, r.access_z_m + 0.020), rpy=(0.0, 0.0, yaw)
        ),
        material=mats["housing"],
        name="access_control__bracket_reader_keypad__reader_body", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Box((0.016, 0.062, 0.084)),
        origin=Origin(
            xyz=(ax + ux * 0.140, ay + uy * 0.140, r.access_z_m + 0.005), rpy=(0.0, 0.0, yaw)
        ),
        material=mats["reader"],
        name="access_control__bracket_reader_keypad__keypad", material_class_id="tech.control_interface",
    )


def _access_control_standalone_reader_post_build(
    host, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    ax, ay, yaw = _access_anchor(r)
    ux, uy = math.cos(yaw), math.sin(yaw)
    px = ax + ux * 0.290
    py = ay + uy * 0.290
    post_top = 1.30 * r.access_z_m
    host.visual(
        Cylinder(radius=0.045, length=post_top),
        origin=Origin(xyz=(px, py, 0.5 * post_top)),
        material=mats["steel"],
        name="access_control__standalone_reader_post__post", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Cylinder(radius=0.090, length=0.026),
        origin=Origin(xyz=(px, py, 0.013)),
        material=mats["dark"],
        name="access_control__standalone_reader_post__post_base", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Cylinder(radius=0.055, length=0.024),
        origin=Origin(xyz=(px, py, post_top - 0.012)),
        material=mats["dark"],
        name="access_control__standalone_reader_post__post_cap", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Box((0.080, 0.130, 0.190)),
        origin=Origin(
            xyz=(px - ux * 0.050, py - uy * 0.050, r.access_z_m + 0.060), rpy=(0.0, 0.0, yaw)
        ),
        material=mats["housing"],
        name="access_control__standalone_reader_post__reader_housing", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Box((0.016, 0.086, 0.120)),
        origin=Origin(
            xyz=(px - ux * 0.088, py - uy * 0.088, r.access_z_m + 0.060), rpy=(0.0, 0.0, yaw)
        ),
        material=mats["reader"],
        name="access_control__standalone_reader_post__reader_screen", material_class_id="tech.emissive_surface",
    )
    conduit_h = max(0.10, r.access_z_m - 0.060)
    host.visual(
        Cylinder(radius=0.014, length=conduit_h),
        origin=Origin(xyz=(px + ux * 0.036, py + uy * 0.036, 0.020 + 0.5 * conduit_h)),
        material=mats["dark"],
        name="access_control__standalone_reader_post__conduit", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    for bracket_index, z in ((0, 0.42 * post_top), (1, 0.82 * post_top)):
        _tube_between(
            host,
            (ax + ux * 0.010, ay + uy * 0.010, z),
            (px - ux * 0.030, py - uy * 0.030, z),
            0.016,
            mats["steel"],
            f"access_control__standalone_reader_post__post_bracket_{bracket_index}",
        )


def _access_control_header_indicator_panel_build(
    host, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    face_y = r.header_face_y_m
    z = r.guard_top_z_m + 0.5 * HEADER_SLAB
    host.visual(
        Box((0.300, 0.070, 0.150)),
        origin=Origin(xyz=(0.0, face_y - 0.030, z)),
        material=mats["housing"],
        name="access_control__header_indicator_panel__control_box", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    host.visual(
        Box((0.250, 0.018, 0.110)),
        origin=Origin(xyz=(0.0, face_y - 0.070, z)),
        material=mats["reader"],
        name="access_control__header_indicator_panel__box_face", material_class_id="tech.control_interface",
    )
    for lamp_index in range(3):
        x = -0.080 + lamp_index * 0.080
        host.visual(
            Cylinder(radius=0.024, length=0.016),
            origin=Origin(xyz=(x, face_y - 0.082, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["dark"],
            name=f"access_control__header_indicator_panel__indicator_bezel_{lamp_index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
        host.visual(
            Cylinder(radius=0.016, length=0.012),
            origin=Origin(xyz=(x, face_y - 0.092, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name=f"access_control__header_indicator_panel__indicator_lens_{lamp_index}", material_class_id="tech.emissive_surface",
        )


_ACCESS_CONTROL_BUILDERS = {
    "post_reader_box": _access_control_post_reader_box_build,
    "bracket_reader_keypad": _access_control_bracket_reader_keypad_build,
    "standalone_reader_post": _access_control_standalone_reader_post_build,
    "header_indicator_panel": _access_control_header_indicator_panel_build,
}


# --- rotor candidates -----------------------------------------------------------
def _rotor_form_arm_tier_rotor_build(part, offset, r, mats, angle, wing, inner):
    """Horizontal arm ladder cantilevered off the spindle with a tip post."""
    ux, uy = math.cos(angle), math.sin(angle)
    outer = r.rotor_radius_m - 0.020
    for tier in range(r.tier_count):
        z = r.wing_z0_m + tier * r.tier_pitch_m
        _tube_between(
            part,
            (ux * inner, uy * inner, z),
            (ux * outer, uy * outer, z),
            0.014,
            mats["light"],
            f"rotor_form__arm_tier_rotor__arm_{wing}_{tier}",
            offset,
        )
    part.visual(
        Cylinder(radius=0.020, length=r.wing_z1_m - r.wing_z0_m + 0.06),
        origin=_local_origin(
            Origin(xyz=(ux * outer, uy * outer, 0.5 * (r.wing_z0_m + r.wing_z1_m))),
            offset,
        ),
        material=mats["steel"],
        name=f"rotor_form__arm_tier_rotor__wing_tip_{wing}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    part.visual(
        Cylinder(radius=0.026, length=0.060),
        origin=_local_origin(
            Origin(xyz=(ux * outer, uy * outer, r.wing_z0_m - 0.050)), offset
        ),
        material=mats["dark"],
        name=f"rotor_form__arm_tier_rotor__wing_cap_{wing}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )


def _rotor_form_braced_arm_rotor_build(part, offset, r, mats, angle, wing, inner):
    """Arm ladder stiffened by a heavy outer post and two diagonal braces."""
    ux, uy = math.cos(angle), math.sin(angle)
    outer = r.rotor_radius_m - 0.026
    for tier in range(r.tier_count):
        z = r.wing_z0_m + tier * r.tier_pitch_m
        _tube_between(
            part,
            (ux * inner, uy * inner, z),
            (ux * outer, uy * outer, z),
            0.016,
            mats["light"],
            f"rotor_form__braced_arm_rotor__arm_{wing}_{tier}",
            offset,
        )
    part.visual(
        Cylinder(radius=0.026, length=r.wing_z1_m - r.wing_z0_m + 0.08),
        origin=_local_origin(
            Origin(xyz=(ux * outer, uy * outer, 0.5 * (r.wing_z0_m + r.wing_z1_m))),
            offset,
        ),
        material=mats["steel"],
        name=f"rotor_form__braced_arm_rotor__wing_post_{wing}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    reach = r.wing_z1_m - r.wing_z0_m
    for brace_index, (z0, z1) in enumerate(
        (
            (r.wing_z0_m, r.wing_z0_m + 0.30 * reach),
            (r.wing_z1_m, r.wing_z1_m - 0.30 * reach),
        )
    ):
        _tube_between(
            part,
            (ux * (inner + 0.010), uy * (inner + 0.010), z0),
            (ux * outer, uy * outer, z1),
            0.018,
            mats["steel"],
            f"rotor_form__braced_arm_rotor__brace_{wing}_{brace_index}",
            offset,
        )


def _rotor_form_stile_rung_rotor_build(part, offset, r, mats, angle, wing, inner):
    """Welded ladder of flat rungs between a hub bar and a full-height stile."""
    ux, uy = math.cos(angle), math.sin(angle)
    outer = r.rotor_radius_m - 0.022
    reach = outer - inner
    for tier in range(r.tier_count):
        z = r.wing_z0_m + tier * r.tier_pitch_m
        part.visual(
            Box((reach, 0.048, 0.016)),
            origin=_local_origin(
                Origin(
                    xyz=(ux * (inner + 0.5 * reach), uy * (inner + 0.5 * reach), z),
                    rpy=(0.0, 0.0, angle),
                ),
                offset,
            ),
            material=mats["light"],
            name=f"rotor_form__stile_rung_rotor__rung_{wing}_{tier}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    part.visual(
        Cylinder(radius=0.022, length=r.wing_z1_m - r.wing_z0_m + 0.10),
        origin=_local_origin(
            Origin(xyz=(ux * outer, uy * outer, 0.5 * (r.wing_z0_m + r.wing_z1_m))),
            offset,
        ),
        material=mats["steel"],
        name=f"rotor_form__stile_rung_rotor__wing_stile_{wing}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    part.visual(
        Box((0.060, 0.060, r.wing_z1_m - r.wing_z0_m + 0.10)),
        origin=_local_origin(
            Origin(
                xyz=(
                    ux * (inner + 0.026),
                    uy * (inner + 0.026),
                    0.5 * (r.wing_z0_m + r.wing_z1_m),
                ),
                rpy=(0.0, 0.0, angle),
            ),
            offset,
        ),
        material=mats["steel"],
        name=f"rotor_form__stile_rung_rotor__hub_bar_{wing}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )


def _rotor_form_curved_bar_rotor_build(part, offset, r, mats, angle, wing, inner):
    """Dense ladder whose rails bow forward, closed by a stile and diagonals."""
    outer = r.rotor_radius_m - 0.020
    bow = 0.16 * r.wing_pitch_rad
    mid = 0.5 * (inner + outer)

    def _point(rad: float, z: float) -> tuple[float, float, float]:
        a = angle + bow * (rad / max(1e-6, outer))
        return (rad * math.cos(a), rad * math.sin(a), z)

    for tier in range(r.tier_count):
        z = r.wing_z0_m + tier * r.tier_pitch_m
        pts = [_point(inner, z), _point(mid, z), _point(outer, z)]
        for seg in range(2):
            _tube_between(
                part,
                pts[seg],
                pts[seg + 1],
                0.013,
                mats["light"],
                f"rotor_form__curved_bar_rotor__bar_{wing}_{tier}_{seg}",
                offset,
            )
    tip = _point(outer, 0.5 * (r.wing_z0_m + r.wing_z1_m))
    part.visual(
        Cylinder(radius=0.020, length=r.wing_z1_m - r.wing_z0_m + 0.08),
        origin=_local_origin(Origin(xyz=tip), offset),
        material=mats["steel"],
        name=f"rotor_form__curved_bar_rotor__wing_stile_{wing}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    for brace_index, frac in enumerate((0.30, 0.70)):
        z = r.wing_z0_m + frac * (r.wing_z1_m - r.wing_z0_m)
        _tube_between(
            part,
            _point(inner + 0.010, r.wing_z0_m),
            _point(outer, z),
            0.014,
            mats["steel"],
            f"rotor_form__curved_bar_rotor__brace_{wing}_{brace_index}",
            offset,
        )


def _rotor_form_vertical_bar_rotor_build(part, offset, r, mats, angle, wing, inner):
    """Palisade: repeated vertical bars spanning a bottom and top wing rail."""
    ux, uy = math.cos(angle), math.sin(angle)
    outer = r.rotor_radius_m - 0.020
    first = inner + 0.034
    for rail_index, z in ((0, r.wing_z0_m), (1, r.wing_z1_m)):
        _tube_between(
            part,
            (ux * inner, uy * inner, z),
            (ux * outer, uy * outer, z),
            0.020,
            mats["steel"],
            f"rotor_form__vertical_bar_rotor__wing_rail_{wing}_{rail_index}",
            offset,
        )
    step = (outer - first) / max(1, r.tier_count - 1)
    for bar in range(r.tier_count):
        rad = first + bar * step
        part.visual(
            Cylinder(radius=0.012, length=r.wing_z1_m - r.wing_z0_m),
            origin=_local_origin(
                Origin(
                    xyz=(ux * rad, uy * rad, 0.5 * (r.wing_z0_m + r.wing_z1_m))
                ),
                offset,
            ),
            material=mats["light"],
            name=f"rotor_form__vertical_bar_rotor__bar_{wing}_{bar}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    part.visual(
        Cylinder(radius=0.022, length=r.wing_z1_m - r.wing_z0_m + 0.08),
        origin=_local_origin(
            Origin(xyz=(ux * outer, uy * outer, 0.5 * (r.wing_z0_m + r.wing_z1_m))),
            offset,
        ),
        material=mats["steel"],
        name=f"rotor_form__vertical_bar_rotor__wing_stile_{wing}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )


_ROTOR_FORM_BUILDERS = {
    "arm_tier_rotor": _rotor_form_arm_tier_rotor_build,
    "braced_arm_rotor": _rotor_form_braced_arm_rotor_build,
    "stile_rung_rotor": _rotor_form_stile_rung_rotor_build,
    "curved_bar_rotor": _rotor_form_curved_bar_rotor_build,
    "vertical_bar_rotor": _rotor_form_vertical_bar_rotor_build,
}


def _build_guard(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    guard = model.part("guard_frame", meta={"role": "guard_frame"})
    _GUARD_FRAME_BUILDERS[r.guard_frame](guard, r, mats)
    _guard_common(guard, r, mats)
    _HEADER_FORM_BUILDERS[r.header_form](guard, r, mats)
    _ACCESS_CONTROL_BUILDERS[r.access_control](guard, r, mats)
    return guard


def _ratchet_ring(rotor, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Toothed indexing ring carried on the rotor, under the release pawl."""
    rotor.visual(
        Cylinder(radius=r.spindle_radius_m + 0.050, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, r.ratchet_z_m)),
        material=mats["dark"],
        name="second_mechanism__locking_pawl_hub__ratchet_ring", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    for tooth in range(RATCHET_TEETH):
        angle = tooth * 2.0 * math.pi / RATCHET_TEETH
        radius = r.spindle_radius_m + 0.058
        rotor.visual(
            Box((0.024, 0.010, 0.022)),
            origin=Origin(
                xyz=(radius * math.cos(angle), radius * math.sin(angle), r.ratchet_z_m),
                rpy=(0.0, 0.0, angle),
            ),
            material=mats["dark"],
            name=f"second_mechanism__locking_pawl_hub__ratchet_tooth_{tooth}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )


def _build_rotor(model: ArticulatedObject, guard, r: ResolvedConfig, mats: dict[str, str]):
    rotor = model.part("rotor", meta={"role": "rotor"})
    spindle_top = r.bearing_top_z_m + 0.030
    rotor.visual(
        Cylinder(radius=r.spindle_radius_m, length=spindle_top - 0.100),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (0.100 + spindle_top))),
        material=mats["steel"],
        name="rotor__spindle", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    rotor.visual(
        Cylinder(radius=r.spindle_radius_m + 0.020, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, FLOOR_BEARING_TOP + 0.015)),
        material=mats["dark"],
        name="rotor__lower_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    rotor.visual(
        Cylinder(radius=r.spindle_radius_m + 0.020, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z_m - 0.060)),
        material=mats["dark"],
        name="rotor__upper_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    if r.hub_drum:
        # Host adaptation: a breakaway wing needs a real hub drum to hinge on, so
        # every wing on this rotor starts from the drum instead of the spindle.
        rotor.visual(
            Cylinder(
                radius=HUB_DRUM_RADIUS,
                length=r.wing_z1_m - r.wing_z0_m + 0.10,
            ),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * (r.wing_z0_m + r.wing_z1_m))),
            material=mats["steel"],
            name="rotor__hub_drum", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    builder = _ROTOR_FORM_BUILDERS[r.rotor_form]
    for wing in range(r.rigid_wing_count):
        builder(
            rotor,
            (0.0, 0.0, 0.0),
            r,
            mats,
            wing * r.wing_pitch_rad,
            wing,
            r.wing_inner_radius_m,
        )
    if r.second_mechanism == "locking_pawl_hub":
        _ratchet_ring(rotor, r, mats)

    provider = AxisInterface(
        name="guard_spindle_axis",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name="rotor_spindle_axis", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "guard_to_rotor",
        ArticulationType.REVOLUTE,
        parent=guard,
        child=rotor,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=180.0,
            velocity=0.9,
            lower=-r.wing_pitch_rad,
            upper=r.wing_pitch_rad,
        ),
        motion_properties=MotionProperties(damping=1.8, friction=2.5),
        meta={"positive_motion": "indexes the rotor one wing sector counter-clockwise"},
    )
    register_interface_mate(model, "guard_to_rotor", mate)
    return rotor


# --- second mechanism candidates ------------------------------------------------
def _service_leaf_path(
    r: ResolvedConfig,
) -> tuple[float, list[tuple[float, float]]]:
    """Closed gate path from hinge edge to latch edge and its outward axis sign."""
    side_sign = -1.0 if r.service_leaf_hinge_side == "left" else 1.0
    if r.guard_frame in ("portal_post_frame", "barred_portal_frame"):
        hinge_x = side_sign * r.guard_radius_m
        latch_x = -side_sign * r.guard_radius_m
        return (
            side_sign,
            [
                (
                    hinge_x + (latch_x - hinge_x) * index / CURVED_LEAF_SEGMENTS,
                    -r.mechanism_radius_m,
                )
                for index in range(CURVED_LEAF_SEGMENTS + 1)
            ],
        )

    # The two fixed cage panels stop at +/-GUARD_HALF_ARC around the front
    # opening.  Complete the missing front arc at a small radial running gap.
    right_angle = -GUARD_HALF_ARC
    left_angle = -math.pi + GUARD_HALF_ARC
    hinge_angle, latch_angle = (
        (left_angle, right_angle)
        if r.service_leaf_hinge_side == "left"
        else (right_angle, left_angle)
    )
    curve_radius = r.guard_radius_m + CURVED_LEAF_STANDOFF
    return (
        side_sign,
        [
            (
                curve_radius * math.cos(
                    hinge_angle
                    + (latch_angle - hinge_angle) * index / CURVED_LEAF_SEGMENTS
                ),
                curve_radius * math.sin(
                    hinge_angle
                    + (latch_angle - hinge_angle) * index / CURVED_LEAF_SEGMENTS
                ),
            )
            for index in range(CURVED_LEAF_SEGMENTS + 1)
        ],
    )


def _second_mechanism_service_guard_leaf_build(
    model: ArticulatedObject, guard, rotor, r: ResolvedConfig, mats: dict[str, str]
):
    """Host-shaped service leaf with either edge hinged to open outward."""
    axis_sign, path = _service_leaf_path(r)
    curved_leaf = r.guard_frame not in (
        "portal_post_frame",
        "barred_portal_frame",
    )
    hinge_xy = path[0]
    latch_xy = path[-1]
    hinge = (hinge_xy[0], hinge_xy[1], 0.5 * r.guard_top_z_m)
    leaf = model.part(
        "second_mechanism__service_guard_leaf__leaf", meta={"role": "mechanism_primary"}
    )
    z_mid = 0.5 * r.guard_top_z_m
    for stile_index, (x, y) in enumerate((hinge_xy, latch_xy)):
        leaf.visual(
            Cylinder(radius=0.012 if stile_index == 0 else 0.020, length=r.guard_top_z_m - 0.12),
            origin=_local_origin(Origin(xyz=(x, y, z_mid)), hinge),
            material=mats["steel"],
            name=f"second_mechanism__service_guard_leaf__stile_{stile_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    for upright, path_index in enumerate((2, 4, 6)):
        x, y = path[path_index]
        leaf.visual(
            Cylinder(radius=0.014, length=r.guard_top_z_m - 0.14),
            origin=_local_origin(Origin(xyz=(x, y, z_mid)), hinge),
            material=mats["light"],
            name=f"second_mechanism__service_guard_leaf__upright_{upright}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    for rail_index, z in ((0, 0.18), (1, r.guard_top_z_m - 0.10)):
        rail_points = (
            path
            if r.guard_frame
            not in ("portal_post_frame", "barred_portal_frame")
            else (path[0], path[-1])
        )
        for segment_index in range(len(rail_points) - 1):
            _tube_between(
                leaf,
                (rail_points[segment_index][0], rail_points[segment_index][1], z),
                (
                    rail_points[segment_index + 1][0],
                    rail_points[segment_index + 1][1],
                    z,
                ),
                0.018,
                mats["steel"],
                (
                    "second_mechanism__service_guard_leaf__rail_"
                    f"{rail_index}_{segment_index}"
                ),
                hinge,
            )
    latch_yaw = math.atan2(
        latch_xy[1] - path[-2][1],
        latch_xy[0] - path[-2][0],
    )
    leaf.visual(
        Box((0.040, 0.040, 0.120) if curved_leaf else (0.050, 0.070, 0.120)),
        origin=_local_origin(
            Origin(
                xyz=(latch_xy[0], latch_xy[1], z_mid + 0.10),
                rpy=(0.0, 0.0, latch_yaw),
            ),
            hinge,
        ),
        material=mats["dark"],
        name="second_mechanism__service_guard_leaf__latch_receiver", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    # A flat leaf uses an outboard jamb.  On a curved cage the first rail
    # sweeps radially outward, so its fixed hinge post belongs radially inward
    # at the cage endpoint; short radial forks bridge from that post to the
    # joint axis without occupying the opening sweep.
    if curved_leaf:
        curve_radius = math.hypot(hinge[0], hinge[1])
        radial = (hinge[0] / curve_radius, hinge[1] / curve_radius)
        tangent = (-radial[1], radial[0])
        post_x = radial[0] * r.guard_radius_m
        post_y = radial[1] * r.guard_radius_m
        guard.visual(
            Cylinder(radius=0.025, length=r.guard_top_z_m - 0.06),
            origin=Origin(
                xyz=(post_x, post_y, 0.5 * (r.guard_top_z_m - 0.06))
            ),
            material=mats["steel"],
            name="second_mechanism__service_guard_leaf__hinge_post", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
        bridge_length = curve_radius - r.guard_radius_m + 0.030
        bridge_center = (
            0.5 * (post_x + hinge[0]) + radial[0] * 0.015,
            0.5 * (post_y + hinge[1]) + radial[1] * 0.015,
        )
        knuckle_yaw = math.atan2(radial[1], radial[0])
    else:
        post_x = hinge[0] + axis_sign * 0.056
        post_y = hinge[1]
        guard.visual(
            Box((0.070, 0.070, r.guard_top_z_m - 0.06)),
            origin=Origin(
                xyz=(post_x, post_y, 0.5 * (r.guard_top_z_m - 0.06))
            ),
            material=mats["steel"],
            name="second_mechanism__service_guard_leaf__hinge_post", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
        bridge_length = 0.070
        bridge_center = (hinge[0] + axis_sign * 0.020, post_y)
        tangent = (0.0, 1.0)
        knuckle_yaw = 0.0
    knuckle_zs = (0.330, 0.5 * r.guard_top_z_m, r.guard_top_z_m - 0.330)
    for knuckle_index, kz in enumerate(knuckle_zs):
        for side in (-1.0, 1.0):
            guard.visual(
                Box((bridge_length, 0.024, 0.090)),
                origin=Origin(
                    xyz=(
                        bridge_center[0] + side * 0.022 * tangent[0],
                        bridge_center[1] + side * 0.022 * tangent[1],
                        kz,
                    ),
                    rpy=(0.0, 0.0, knuckle_yaw),
                ),
                material=mats["steel"],
                name=(
                    "second_mechanism__service_guard_leaf__hinge_knuckle_"
                    f"{knuckle_index}_{0 if side < 0 else 1}"
                ), material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
            )
    if not curved_leaf:
        for tie_index, z in enumerate((FLOOR_RING_Z, r.bearing_top_z_m)):
            elbow = (post_x, -r.ring_radius_m, z)
            _tube_between(
                guard,
                (0.0, -r.ring_radius_m, z),
                elbow,
                0.016,
                mats["steel"],
                f"second_mechanism__service_guard_leaf__hinge_tie_{tie_index}_lateral",
            )
            _tube_between(
                guard,
                elbow,
                (post_x, post_y, z),
                0.016,
                mats["steel"],
                f"second_mechanism__service_guard_leaf__hinge_tie_{tie_index}_outboard",
            )
    axis = (0.0, 0.0, axis_sign)
    provider = AxisInterface(
        name="mechanism_mount_axis", point=hinge, axis=axis, radial=(1.0, 0.0, 0.0)
    )
    consumer = AxisInterface(
        name="mechanism_pivot_axis", axis=axis, radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "guard_to_service_leaf",
        ArticulationType.REVOLUTE,
        parent=guard,
        child=leaf,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=45.0, velocity=1.0, lower=0.0, upper=math.pi / 2.0),
        motion_properties=MotionProperties(damping=2.0, friction=1.0),
        meta={
            "positive_motion": "swings the service leaf outward from the passage",
            "hinge_side": r.service_leaf_hinge_side,
            "leaf_profile": (
                "flat"
                if r.guard_frame in ("portal_post_frame", "barred_portal_frame")
                else "curved"
            ),
        },
    )
    register_interface_mate(model, "guard_to_service_leaf", mate)
    return (leaf,)


def _second_mechanism_emergency_breakaway_wing_build(
    model: ArticulatedObject, guard, rotor, r: ResolvedConfig, mats: dict[str, str]
):
    """The last rotor wing becomes its own part and folds toward the spindle."""
    wing = model.part(
        "second_mechanism__emergency_breakaway_wing__wing",
        meta={"role": "mechanism_primary"},
    )
    angle = (r.wing_count - 1) * r.wing_pitch_rad
    inner = HUB_DRUM_RADIUS + 0.011
    ux, uy = math.cos(angle), math.sin(angle)
    stile_radius = HUB_DRUM_RADIUS + 0.011
    hinge = (ux * stile_radius, uy * stile_radius, 0.5 * (r.wing_z0_m + r.wing_z1_m))
    _ROTOR_FORM_BUILDERS[r.rotor_form](
        wing, hinge, r, mats, angle, r.wing_count - 1, inner
    )
    wing.visual(
        Cylinder(radius=0.014, length=r.wing_z1_m - r.wing_z0_m + 0.06),
        origin=_local_origin(Origin(xyz=hinge), hinge),
        material=mats["dark"],
        name="second_mechanism__emergency_breakaway_wing__hinge_stile", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    marker_r = stile_radius + 0.040
    wing.visual(
        Box((0.060, 0.030, 0.110)),
        origin=_local_origin(
            Origin(
                xyz=(
                    ux * marker_r,
                    uy * marker_r,
                    r.wing_z0_m + 0.55 * (r.wing_z1_m - r.wing_z0_m),
                ),
                rpy=(0.0, 0.0, angle),
            ),
            hinge,
        ),
        material=mats["accent"],
        name="second_mechanism__emergency_breakaway_wing__release_marker", material_class_id="plastic.opaque_glossy_molded",
    )
    provider = AxisInterface(
        name="mechanism_mount_axis",
        point=hinge,
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name="mechanism_pivot_axis", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "rotor_to_breakaway_wing",
        ArticulationType.REVOLUTE,
        parent=rotor,
        child=wing,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=60.0,
            velocity=1.5,
            lower=0.0,
            upper=min(1.20, 0.75 * r.wing_pitch_rad),
        ),
        motion_properties=MotionProperties(damping=3.0, friction=1.2),
        meta={"positive_motion": "folds the breakaway wing toward the next wing sector"},
    )
    register_interface_mate(model, "rotor_to_breakaway_wing", mate)
    return (wing,)


def _second_mechanism_locking_pawl_hub_build(
    model: ArticulatedObject, guard, rotor, r: ResolvedConfig, mats: dict[str, str]
):
    """Release pawl on a horizontal pivot over the rotor's ratchet ring."""
    pivot_x = r.ratchet_tip_radius_m + 0.085
    pivot_z = r.ratchet_z_m + 0.026
    pawl = model.part(
        "second_mechanism__locking_pawl_hub__pawl", meta={"role": "mechanism_primary"}
    )
    pawl.visual(
        Box((0.090, 0.016, 0.012)),
        origin=Origin(xyz=(-0.028, 0.0, 0.0)),
        material=mats["steel"],
        name="second_mechanism__locking_pawl_hub__pawl_lever", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    pawl.visual(
        Box((0.018, 0.012, 0.024)),
        origin=Origin(xyz=(-0.068, 0.0, -0.010)),
        material=mats["dark"],
        name="second_mechanism__locking_pawl_hub__pawl_tip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    pawl.visual(
        Box((0.024, 0.016, 0.012)),
        origin=Origin(xyz=(0.024, 0.0, 0.0)),
        material=mats["steel"],
        name="second_mechanism__locking_pawl_hub__pawl_tail", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    pawl.visual(
        Cylinder(radius=0.009, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="second_mechanism__locking_pawl_hub__pawl_bushing", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    # Fork bracket: two ears straddle the bushing with a 1 mm running gap and a
    # radial arm carries the fork back to the head ring above every rotor member.
    for ear_index, sy in enumerate((-1.0, 1.0)):
        guard.visual(
            Box((0.034, 0.014, 0.044)),
            origin=Origin(xyz=(pivot_x, sy * 0.018, pivot_z + 0.005)),
            material=mats["steel"],
            name=f"second_mechanism__locking_pawl_hub__fork_ear_{ear_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    guard.visual(
        Box((0.044, 0.052, 0.040)),
        origin=Origin(xyz=(pivot_x + 0.008, 0.0, pivot_z + 0.036)),
        material=mats["steel"],
        name="second_mechanism__locking_pawl_hub__bracket_boss", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    _tube_between(
        guard,
        (pivot_x, 0.0, pivot_z + 0.044),
        (r.ring_radius_m, 0.0, pivot_z + 0.044),
        0.016,
        mats["steel"],
        "second_mechanism__locking_pawl_hub__bracket_arm",
    )
    _tube_between(
        guard,
        (r.ring_radius_m, 0.0, pivot_z + 0.044),
        (r.ring_radius_m, 0.0, r.bearing_top_z_m),
        0.016,
        mats["steel"],
        "second_mechanism__locking_pawl_hub__bracket_drop",
    )
    provider = AxisInterface(
        name="mechanism_mount_axis",
        point=(pivot_x, 0.0, pivot_z),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name="mechanism_pivot_axis", axis=(0.0, 1.0, 0.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "guard_to_release_pawl",
        ArticulationType.REVOLUTE,
        parent=guard,
        child=pawl,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=0.55),
        motion_properties=MotionProperties(damping=0.6, friction=0.4),
        meta={"positive_motion": "lifts the pawl tip clear of the ratchet teeth"},
    )
    register_interface_mate(model, "guard_to_release_pawl", mate)
    return (pawl,)


def _second_mechanism_overhead_indexing_cam_build(
    model: ArticulatedObject, guard, rotor, r: ResolvedConfig, mats: dict[str, str]
):
    """Overhead eccentric cam mimicking the rotor, with its own roller follower."""
    cam_thickness = 0.022
    # Guard-side pedestal that the cam hub runs on, standing on the top bearing.
    guard.visual(
        Cylinder(radius=r.spindle_radius_m + 0.034, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z_m + 0.053)),
        material=mats["dark"],
        name="second_mechanism__overhead_indexing_cam__cam_pedestal", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    cam = model.part(
        "second_mechanism__overhead_indexing_cam__cam", meta={"role": "mechanism_primary"}
    )
    cam.visual(
        Cylinder(radius=0.075, length=cam_thickness),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["dark"],
        name="second_mechanism__overhead_indexing_cam__cam_disk", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    cam.visual(
        Cylinder(radius=0.032, length=cam_thickness),
        origin=Origin(xyz=(0.062, 0.0, 0.0)),
        material=mats["dark"],
        name="second_mechanism__overhead_indexing_cam__cam_lobe", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    cam.visual(
        Cylinder(radius=0.026, length=cam_thickness + 0.022),
        origin=Origin(xyz=(0.0, 0.0, 0.011)),
        material=mats["steel"],
        name="second_mechanism__overhead_indexing_cam__cam_hub", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    provider = AxisInterface(
        name="mechanism_mount_axis",
        point=(0.0, 0.0, r.cam_z_m),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name="mechanism_pivot_axis", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "guard_to_index_cam",
        ArticulationType.REVOLUTE,
        parent=guard,
        child=cam,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=60.0, velocity=0.9, lower=-r.wing_pitch_rad, upper=r.wing_pitch_rad
        ),
        mimic=Mimic(joint="guard_to_rotor", multiplier=1.0, offset=0.0),
        meta={"positive_motion": "mirrors the rotor so the cam indexes with it"},
    )
    register_interface_mate(model, "guard_to_index_cam", mate)

    pivot_x = 0.185
    pivot_z = r.cam_z_m + 0.5 * cam_thickness + 0.030
    follower = model.part(
        "second_mechanism__overhead_indexing_cam__roller_arm",
        meta={"role": "mechanism_follower"},
    )
    follower.visual(
        Box((0.100, 0.016, 0.009)),
        origin=Origin(xyz=(-0.050, 0.0, 0.0)),
        material=mats["steel"],
        name="second_mechanism__overhead_indexing_cam__arm_bar", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    follower.visual(
        Cylinder(radius=0.010, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="second_mechanism__overhead_indexing_cam__arm_bushing", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    follower.visual(
        Cylinder(radius=0.011, length=0.018),
        origin=Origin(xyz=(-0.098, 0.0, -0.004), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["light"],
        name="second_mechanism__overhead_indexing_cam__contact_roller", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    for ear_index, sy in enumerate((-1.0, 1.0)):
        guard.visual(
            Box((0.030, 0.014, 0.040)),
            origin=Origin(xyz=(pivot_x, sy * 0.021, pivot_z + 0.005)),
            material=mats["steel"],
            name=f"second_mechanism__overhead_indexing_cam__fork_ear_{ear_index}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
        )
    guard.visual(
        Box((0.040, 0.056, 0.036)),
        origin=Origin(xyz=(pivot_x + 0.006, 0.0, pivot_z + 0.034)),
        material=mats["steel"],
        name="second_mechanism__overhead_indexing_cam__bracket_boss", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized", "dark_zinc", "stainless"} else "metal.paint_coated"),
    )
    _tube_between(
        guard,
        (pivot_x, 0.0, pivot_z + 0.046),
        (r.ring_radius_m, 0.0, pivot_z + 0.046),
        0.016,
        mats["steel"],
        "second_mechanism__overhead_indexing_cam__bracket_arm",
    )
    _tube_between(
        guard,
        (r.ring_radius_m, 0.0, pivot_z + 0.046),
        (r.ring_radius_m, 0.0, r.bearing_top_z_m),
        0.016,
        mats["steel"],
        "second_mechanism__overhead_indexing_cam__bracket_drop",
    )
    provider_f = AxisInterface(
        name="mechanism_follower_mount_axis",
        point=(pivot_x, 0.0, pivot_z),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer_f = AxisInterface(
        name="mechanism_follower_axis", axis=(0.0, 1.0, 0.0), radial=(1.0, 0.0, 0.0)
    )
    mate_f = mate_axes(provider_f, consumer_f)
    model.articulation(
        "guard_to_roller_arm",
        ArticulationType.REVOLUTE,
        parent=guard,
        child=follower,
        origin=mate_f.origin,
        axis=mate_f.axis,
        motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=-0.06, upper=0.24),
        motion_properties=MotionProperties(damping=0.6, friction=0.4),
        meta={"positive_motion": "the cam lobe lifts the roller end of the follower"},
    )
    register_interface_mate(model, "guard_to_roller_arm", mate_f)
    return (cam, follower)


_SECOND_MECHANISM_BUILDERS = {
    "service_guard_leaf": _second_mechanism_service_guard_leaf_build,
    "emergency_breakaway_wing": _second_mechanism_emergency_breakaway_wing_build,
    "locking_pawl_hub": _second_mechanism_locking_pawl_hub_build,
    "overhead_indexing_cam": _second_mechanism_overhead_indexing_cam_build,
}


# --- assembly -------------------------------------------------------------------
def build_pictureX_0611_full_height_turnstile(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_full_height_turnstile",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "full-height rotor indexing on a vertical spindle in a fixed guard",
        },
    )
    mats = _materials(model, r)
    guard = _build_guard(model, r, mats)
    rotor = _build_rotor(model, guard, r, mats)
    _SECOND_MECHANISM_BUILDERS[r.second_mechanism](model, guard, rotor, r, mats)

    risk: list[dict[str, float]] = [
        {"guard_to_rotor": 0.0},
        {"guard_to_rotor": r.wing_pitch_rad},
        {"guard_to_rotor": -r.wing_pitch_rad},
        {"guard_to_rotor": 0.5 * r.wing_pitch_rad},
    ]
    if r.second_mechanism == "service_guard_leaf":
        risk[1]["guard_to_service_leaf"] = math.pi / 2.0
        risk[3]["guard_to_service_leaf"] = math.pi / 4.0
    elif r.second_mechanism == "emergency_breakaway_wing":
        fold = min(1.20, 0.75 * r.wing_pitch_rad)
        risk[1]["rotor_to_breakaway_wing"] = fold
        risk[3]["rotor_to_breakaway_wing"] = 0.5 * fold
    elif r.second_mechanism == "locking_pawl_hub":
        risk[1]["guard_to_release_pawl"] = 0.55
        risk[3]["guard_to_release_pawl"] = 0.25
    else:
        risk[1]["guard_to_roller_arm"] = 0.24
        risk[3]["guard_to_roller_arm"] = -0.06
    model.meta["risk_poses"] = tuple(risk)
    return model


def build_seeded_pictureX_0611_full_height_turnstile(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_full_height_turnstile(config_from_seed(seed), assets=assets)


# --- authored tests --------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_pictureX_0611_full_height_turnstile_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    guards = _parts_by_role(model, "guard_frame")
    rotors = _parts_by_role(model, "rotor")
    primaries = _parts_by_role(model, "mechanism_primary")
    followers = _parts_by_role(model, "mechanism_follower")
    joints = {j.name: j for j in model.articulations}
    rotor_joint = joints.get("guard_to_rotor")

    ctx.check(
        "category_anchor: a full-height rotor turns on the vertical spindle of a grounded guard",
        len(guards) == 1
        and len(rotors) == 1
        and len(primaries) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "guard_frame"
        and rotor_joint is not None
        and rotor_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(abs(v), 6) for v in rotor_joint.axis) == (0.0, 0.0, 1.0)
        and rotor_joint.parent == "guard_frame"
        and rotor_joint.child == "rotor"
        and abs(rotor_joint.motion_limits.upper - r.wing_pitch_rad) < 1e-9
        and abs(rotor_joint.motion_limits.lower + r.wing_pitch_rad) < 1e-9,
        details=(
            f"guards={len(guards)} rotors={len(rotors)} primaries={len(primaries)} "
            f"followers={len(followers)} joints={sorted(joints)}"
        ),
    )

    ctx.check(
        "category_anchor: the rotor sweeps inside the guard with a real running clearance",
        abs(r.rotor_radius_m - (r.guard_radius_m - ROTOR_GUARD_CLEARANCE)) < 1e-9
        and r.rotor_radius_m > 0.30
        and r.guard_member_half_m <= MEMBER_HALF_MAX
        and r.rotor_radius_m + 0.030 < r.guard_radius_m - r.guard_member_half_m
        and r.wing_z1_m > r.wing_z0_m + 0.60
        and r.wing_z1_m < r.bearing_top_z_m - 0.10
        and r.bearing_top_z_m < r.guard_top_z_m
        and abs(r.guard_top_z_m + r.header_height_m - r.overall_height_m) < 1e-9,
        details=(
            f"rotor_r={r.rotor_radius_m} guard_r={r.guard_radius_m} "
            f"member_half={r.guard_member_half_m} wing=({r.wing_z0_m}, {r.wing_z1_m}) "
            f"bearing_top={r.bearing_top_z_m} guard_top={r.guard_top_z_m}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}

    def count(fragment: str) -> int:
        return sum(1 for n in visual_names if fragment in n)

    members = 2 * r.guard_member_count
    guard_ok = {
        "portal_post_frame": count("portal_post_frame__post_") == members
        and count("portal_post_frame__footplate_") == members
        and count("portal_post_frame__threshold_") == 2,
        "barred_portal_frame": count("barred_portal_frame__post_") == members
        and count("barred_portal_frame__side_bar_") == 20,
        "arc_rail_cage": count("arc_rail_cage__upright_") == members
        and count("arc_rail_cage__shoe_") == members
        and count("arc_rail_cage__rail_") == 2 * 9 * 8,
        "cylindrical_bar_cage": count("cylindrical_bar_cage__upright_") == members
        and count("cylindrical_bar_cage__cage_bar_") == 50,
        "curved_panel_cage": count("curved_panel_cage__upright_") == members
        and count("curved_panel_cage__rail_") == 2 * 12 * 10,
    }[r.guard_frame]
    ctx.check(
        "category_anchor: guard_frame identity",
        guard_ok
        and count("guard_frame__member_tie_") == 2 * members
        and any("guard_frame__floor_bearing" in n for n in visual_names)
        and any("guard_frame__top_bearing" in n for n in visual_names),
        details=f"guard_frame={r.guard_frame} members={r.guard_member_count}",
    )

    header_ok = {
        "flat_header": any("flat_header__housing_slab" in n for n in visual_names)
        and any("flat_header__fascia" in n for n in visual_names)
        and abs(r.header_height_m - HEADER_SLAB) < 1e-9,
        "arched_header": count("arched_header__arch_rib_") == 20
        and count("arched_header__arch_post_") == 2
        and count("arched_header__arch_tie_") == 3
        and abs(r.header_height_m - ARCH_RISE) < 1e-9,
    }[r.header_form]
    ctx.check(
        "category_anchor: header_form identity",
        header_ok,
        details=f"header_form={r.header_form} header_height={r.header_height_m}",
    )

    wings = r.wing_count
    rungs = r.tier_count * wings
    rotor_ok = {
        "arm_tier_rotor": count("arm_tier_rotor__arm_") == rungs
        and count("arm_tier_rotor__wing_tip_") == wings,
        "braced_arm_rotor": count("braced_arm_rotor__arm_") == rungs
        and count("braced_arm_rotor__brace_") == 2 * wings,
        "stile_rung_rotor": count("stile_rung_rotor__rung_") == rungs
        and count("stile_rung_rotor__hub_bar_") == wings,
        "curved_bar_rotor": count("curved_bar_rotor__bar_") == 2 * rungs
        and count("curved_bar_rotor__brace_") == 2 * wings,
        "vertical_bar_rotor": count("vertical_bar_rotor__bar_") == rungs
        and count("vertical_bar_rotor__wing_rail_") == 2 * wings,
    }[r.rotor_form]
    ctx.check(
        "category_anchor: rotor_form identity",
        rotor_ok
        and any("rotor__spindle" in n for n in visual_names)
        and any("rotor__lower_collar" in n for n in visual_names)
        and any("rotor__upper_collar" in n for n in visual_names),
        details=(
            f"rotor_form={r.rotor_form} wings={wings} rigid={r.rigid_wing_count} "
            f"tiers={r.tier_count}"
        ),
    )

    access_ok = {
        "post_reader_box": any("post_reader_box__reader_face" in n for n in visual_names)
        and any("post_reader_box__enclosure" in n for n in visual_names),
        "bracket_reader_keypad": any("bracket_reader_keypad__keypad" in n for n in visual_names)
        and any("bracket_reader_keypad__bracket" in n for n in visual_names),
        "standalone_reader_post": any(
            "standalone_reader_post__conduit" in n for n in visual_names
        )
        and count("standalone_reader_post__post_bracket_") == 2,
        "header_indicator_panel": count("header_indicator_panel__indicator_lens_") == 3
        and any("header_indicator_panel__control_box" in n for n in visual_names),
    }[r.access_control]
    ctx.check(
        "category_anchor: access_control identity",
        access_ok and any("guard_frame__access_strap" in n for n in visual_names),
        details=f"access_control={r.access_control}",
    )

    if r.second_mechanism == "service_guard_leaf":
        leaf_joint = joints.get("guard_to_service_leaf")
        axis_sign, leaf_path = _service_leaf_path(r)
        expected_hinge = leaf_path[0]
        expected_latch_local = (
            leaf_path[-1][0] - expected_hinge[0],
            leaf_path[-1][1] - expected_hinge[1],
        )
        curved_leaf = r.guard_frame not in (
            "portal_post_frame",
            "barred_portal_frame",
        )
        leaf_part = primaries[0] if primaries else None
        latch = (
            next(
                (
                    visual
                    for visual in leaf_part.visuals
                    if visual.name
                    == "second_mechanism__service_guard_leaf__latch_receiver"
                ),
                None,
            )
            if leaf_part is not None
            else None
        )
        closed_latch_y = (
            leaf_joint.origin.xyz[1] + latch.origin.xyz[1]
            if leaf_joint is not None and latch is not None
            else math.inf
        )
        open_latch_y = (
            leaf_joint.origin.xyz[1]
            + math.sin(axis_sign * math.pi / 2.0) * latch.origin.xyz[0]
            + math.cos(axis_sign * math.pi / 2.0) * latch.origin.xyz[1]
            if leaf_joint is not None and latch is not None
            else math.inf
        )
        mechanism_ok = (
            len(followers) == 0
            and leaf_joint is not None
            and leaf_joint.articulation_type == ArticulationType.REVOLUTE
            and leaf_joint.parent == "guard_frame"
            and count("service_guard_leaf__upright_") == 3
            and count("service_guard_leaf__rail_")
            == (2 * CURVED_LEAF_SEGMENTS if curved_leaf else 2)
            and latch is not None
            and abs(leaf_joint.origin.xyz[0] - expected_hinge[0]) < 1e-9
            and abs(leaf_joint.origin.xyz[1] - expected_hinge[1]) < 1e-9
            and abs(leaf_joint.axis[2] - axis_sign) < 1e-9
            and abs(latch.origin.xyz[0] - expected_latch_local[0]) < 1e-9
            and abs(latch.origin.xyz[1] - expected_latch_local[1]) < 1e-9
            and open_latch_y < closed_latch_y - 0.5 * r.guard_radius_m
        )
    elif r.second_mechanism == "emergency_breakaway_wing":
        fold_joint = joints.get("rotor_to_breakaway_wing")
        mechanism_ok = (
            len(followers) == 0
            and fold_joint is not None
            and fold_joint.parent == "rotor"
            and fold_joint.motion_limits.upper > 0.9
            and r.rigid_wing_count == r.wing_count - 1
            and any("emergency_breakaway_wing__hinge_stile" in n for n in visual_names)
        )
    elif r.second_mechanism == "locking_pawl_hub":
        pawl_joint = joints.get("guard_to_release_pawl")
        mechanism_ok = (
            len(followers) == 0
            and pawl_joint is not None
            and pawl_joint.articulation_type == ArticulationType.REVOLUTE
            and count("locking_pawl_hub__ratchet_tooth_") == RATCHET_TEETH
            and any("locking_pawl_hub__pawl_tip" in n for n in visual_names)
        )
    else:
        cam_joint = joints.get("guard_to_index_cam")
        arm_joint = joints.get("guard_to_roller_arm")
        mechanism_ok = (
            len(followers) == 1
            and cam_joint is not None
            and cam_joint.mimic is not None
            and arm_joint is not None
            and arm_joint.articulation_type == ArticulationType.REVOLUTE
            and any("overhead_indexing_cam__cam_lobe" in n for n in visual_names)
        )
    ctx.check(
        "category_anchor: second_mechanism identity",
        mechanism_ok,
        details=f"second_mechanism={r.second_mechanism} joints={sorted(joints)}",
    )

    # Motion evidence: one sector of rotor travel really swings the wings round
    # the spindle instead of leaving a static cage.
    rest = ctx.part_world_aabb(rotors[0])
    with ctx.pose({rotor_joint: 0.5 * r.wing_pitch_rad}):
        turned = ctx.part_world_aabb(rotors[0])
    ctx.check(
        "half a sector of travel swings the rotor wings around the spindle",
        rest is not None
        and turned is not None
        and max(
            abs(turned[0][0] - rest[0][0]),
            abs(turned[0][1] - rest[0][1]),
            abs(turned[1][0] - rest[1][0]),
            abs(turned[1][1] - rest[1][1]),
        )
        > 0.04 * r.rotor_radius_m,
        details=f"rest={rest} turned={turned}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_guard_dense_members_arched_cam",
        {
            "guard_frame": "cylindrical_bar_cage",
            "header_form": "arched_header",
            "rotor_form": "curved_bar_rotor",
            "access_control": "header_indicator_panel",
            "second_mechanism": "overhead_indexing_cam",
            "wing_count": 4,
            "tier_count": 11,
            "guard_member_count": 12,
            "guard_radius_m": 0.45,
            "overall_height_m": 2.10,
            "spindle_radius_m": 0.046,
        },
        reason="smallest guard and lowest turnstile with the densest cage, four wings, "
        "eleven tiers and the tallest header",
    ),
    corner_case(
        "max_guard_sparse_members_flat_leaf",
        {
            "guard_frame": "portal_post_frame",
            "header_form": "flat_header",
            "rotor_form": "arm_tier_rotor",
            "access_control": "standalone_reader_post",
            "second_mechanism": "service_guard_leaf",
            "service_leaf_hinge_side": "left",
            "wing_count": 3,
            "tier_count": 6,
            "guard_member_count": 5,
            "guard_radius_m": 0.78,
            "overall_height_m": 2.60,
            "spindle_radius_m": 0.026,
        },
        reason="widest open portal at full height with the thinnest spindle, the fewest "
        "members and the left-hinged flat service leaf opening outward",
    ),
    corner_case(
        "max_curved_guard_right_hinged_arc_leaf",
        {
            "guard_frame": "curved_panel_cage",
            "header_form": "arched_header",
            "rotor_form": "stile_rung_rotor",
            "access_control": "header_indicator_panel",
            "second_mechanism": "service_guard_leaf",
            "service_leaf_hinge_side": "right",
            "wing_count": 4,
            "tier_count": 11,
            "guard_member_count": 12,
            "guard_radius_m": 0.78,
            "overall_height_m": 2.60,
            "spindle_radius_m": 0.046,
        },
        reason="widest cylindrical guard with the complementary curved service leaf "
        "right-hinged at the outlet edge and opening outward",
    ),
    corner_case(
        "max_guard_breakaway_four_wing",
        {
            "guard_frame": "curved_panel_cage",
            "header_form": "arched_header",
            "rotor_form": "vertical_bar_rotor",
            "access_control": "bracket_reader_keypad",
            "second_mechanism": "emergency_breakaway_wing",
            "wing_count": 4,
            "tier_count": 11,
            "guard_member_count": 12,
            "guard_radius_m": 0.78,
            "overall_height_m": 2.10,
            "spindle_radius_m": 0.046,
        },
        reason="the tightest breakaway fold angle — four wings on the widest guard in the "
        "shortest frame with the densest palisade",
    ),
    corner_case(
        "min_guard_pawl_thin_spindle",
        {
            "guard_frame": "arc_rail_cage",
            "header_form": "flat_header",
            "rotor_form": "stile_rung_rotor",
            "access_control": "post_reader_box",
            "second_mechanism": "locking_pawl_hub",
            "wing_count": 3,
            "tier_count": 6,
            "guard_member_count": 5,
            "guard_radius_m": 0.45,
            "overall_height_m": 2.60,
            "spindle_radius_m": 0.026,
        },
        reason="the smallest ratchet ring on the thinnest spindle under the tallest "
        "rotor span, with the pawl bracket reaching furthest inward",
    ),
    corner_case(
        "barred_portal_max_height_cam",
        {
            "guard_frame": "barred_portal_frame",
            "header_form": "arched_header",
            "rotor_form": "braced_arm_rotor",
            "access_control": "standalone_reader_post",
            "second_mechanism": "overhead_indexing_cam",
            "wing_count": 3,
            "tier_count": 8,
            "guard_member_count": 8,
            "guard_radius_m": 0.78,
            "overall_height_m": 2.60,
            "spindle_radius_m": 0.036,
        },
        reason="the longest cam bracket reach — widest barred portal, arched header and "
        "the overhead indexer",
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
    "build_pictureX_0611_full_height_turnstile",
    "build_seeded_pictureX_0611_full_height_turnstile",
    "run_pictureX_0611_full_height_turnstile_tests",
]
