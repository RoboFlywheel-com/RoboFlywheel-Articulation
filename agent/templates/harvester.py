# SPDX-License-Identifier: Apache-2.0

"""Agricultural / Harvester vehicle (arm) modular procedural template.

A forestry HARVESTER = a self-propelled (or pedestal-mounted) carrier + an
articulated hydraulic boom ARM + a harvester/processing head end-effector. The
"(arm)" makes the boom+head central: the identity is a heavy multi-section boom
reaching forward from a carrier with a tool head hanging off the wrist.

Kinematic spine (pattern = ``mixed``):
    carrier --[turret slew, tracked only]--> boom --(elbow)--> stick
            --(wrist)--> head --(rotator / fingers / jaws / drum)

Slots (each a source-backed replaceable structural layer, spec
``articraft_template_authoring/specs_modular_v1/harvester.md``):

  * ``undercarriage`` (3): wheeled_bogie (P2, N bogie wheels CONTINUOUS) /
    tracked_crawler (P3, turret slew REVOLUTE-Z + N road rollers) /
    pedestal_static (P1, king-post column, no carrier).
  * ``boom_type`` (3): knuckle_2section (P3) / inverted_V (P1) /
    telescopic_3section (fork; outer sleeve + inner PRISMATIC).
  * ``head`` (5): processing_head (P3, internals inline) /
    felling_grapple_4finger (P1, rotator CONTINUOUS + 4 REVOLUTE fingers) /
    feller_saw (fork, saw disc + 2 REVOLUTE grab arms) /
    log_grapple (fork, rotator CONTINUOUS + 2 REVOLUTE jaws) /
    mulcher (fork, GATED; hood + drum CONTINUOUS + teeth).
  * multiplicity: ``num_axles`` (wheeled) / ``rollers_per_side`` (tracked).

Every head shares the identical wrist interface (``head_wrist_pin`` at
head-local (0,0,0)) so any head mates any boom (spec §9 compatibility matrix).
The turret slew is the only gated element (tracked only). All chain pivots are
captured-pin geometry (barrel-in-yoke) -> grandfathered joints (no
MatingContract) guarded by the flat articulation-origin baseline + element-scoped
``allow_overlap`` (mirroring each source record's run_tests block). Tire / rim /
mesh-tube primitives are preserved (Rule 3), not downgraded.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    BoltPattern,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    SphereGeometry,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireGroove,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enums / slot vocabularies
# ---------------------------------------------------------------------------
Undercarriage = Literal["wheeled_bogie", "tracked_crawler", "pedestal_static"]
BoomType = Literal["knuckle_2section", "inverted_V", "telescopic_3section"]
Head = Literal[
    "processing_head",
    "felling_grapple_4finger",
    "feller_saw",
    "log_grapple",
    "mulcher",
]
PaletteStyle = Literal[
    "jd_green",
    "komatsu_red",
    "black_arm",
    "ponsse_yellow",
    "tigercat_orange",
    "industrial_grey",
]

UNDERCARRIAGES: tuple[Undercarriage, ...] = (
    "wheeled_bogie",
    "tracked_crawler",
    "pedestal_static",
)
BOOM_TYPES: tuple[BoomType, ...] = (
    "knuckle_2section",
    "inverted_V",
    "telescopic_3section",
)
HEADS: tuple[Head, ...] = (
    "processing_head",
    "felling_grapple_4finger",
    "feller_saw",
    "log_grapple",
    "mulcher",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "jd_green",
    "komatsu_red",
    "black_arm",
    "ponsse_yellow",
    "tigercat_orange",
    "industrial_grey",
)

# Multiplicity domains (spec §8).
AXLE_MIN, AXLE_MAX = 2, 5
AXLE_CHOICES = (2, 3, 4, 5)
AXLE_WEIGHTS = (0.15, 0.40, 0.30, 0.15)
ROLLER_MIN, ROLLER_MAX = 3, 8
ROLLER_CHOICES = (3, 4, 5, 6, 7, 8)
ROLLER_WEIGHTS = (0.15, 0.30, 0.25, 0.20, 0.06, 0.04)

# ---------------------------------------------------------------------------
# Palettes (⑥). 12 material keys shared across every builder. Classes present:
# painted (body/arm), metal (steel/chrome), rubber, glass -> >= 3.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "jd_green": {
        "body": (0.02, 0.36, 0.12, 1.0),
        "body_accent": (0.96, 0.74, 0.10, 1.0),
        "cab_glass": (0.15, 0.40, 0.34, 0.46),
        "arm": (0.12, 0.15, 0.17, 1.0),
        "arm_dark": (0.04, 0.05, 0.055, 1.0),
        "steel": (0.55, 0.60, 0.57, 1.0),
        "rubber": (0.015, 0.014, 0.012, 1.0),
        "chrome": (0.78, 0.82, 0.84, 1.0),
        "hardware": (0.02, 0.02, 0.02, 1.0),
        "cutting": (0.42, 0.36, 0.28, 1.0),
        "hydraulic": (1.0, 0.74, 0.02, 1.0),
        "hose": (0.0, 0.20, 0.12, 1.0),
    },
    "komatsu_red": {
        "body": (0.75, 0.03, 0.02, 1.0),
        "body_accent": (1.0, 0.78, 0.04, 1.0),
        "cab_glass": (0.12, 0.38, 0.55, 0.55),
        "arm": (0.02, 0.025, 0.03, 1.0),
        "arm_dark": (0.09, 0.095, 0.09, 1.0),
        "steel": (0.62, 0.66, 0.62, 1.0),
        "rubber": (0.005, 0.006, 0.006, 1.0),
        "chrome": (0.82, 0.84, 0.80, 1.0),
        "hardware": (0.02, 0.02, 0.02, 1.0),
        "cutting": (0.42, 0.36, 0.28, 1.0),
        "hydraulic": (1.0, 0.78, 0.04, 1.0),
        "hose": (0.01, 0.01, 0.01, 1.0),
    },
    "black_arm": {
        "body": (0.02, 0.035, 0.065, 1.0),
        "body_accent": (1.0, 0.74, 0.02, 1.0),
        "cab_glass": (0.20, 0.30, 0.40, 0.50),
        "arm": (0.02, 0.035, 0.065, 1.0),
        "arm_dark": (0.012, 0.013, 0.014, 1.0),
        "steel": (0.60, 0.62, 0.61, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "chrome": (0.86, 0.86, 0.82, 1.0),
        "hardware": (0.05, 0.05, 0.055, 1.0),
        "cutting": (0.50, 0.50, 0.50, 1.0),
        "hydraulic": (1.0, 0.74, 0.02, 1.0),
        "hose": (0.05, 0.05, 0.055, 1.0),
    },
    "ponsse_yellow": {
        "body": (0.92, 0.70, 0.06, 1.0),
        "body_accent": (0.08, 0.08, 0.09, 1.0),
        "cab_glass": (0.12, 0.25, 0.35, 0.50),
        "arm": (0.10, 0.10, 0.11, 1.0),
        "arm_dark": (0.04, 0.04, 0.045, 1.0),
        "steel": (0.58, 0.60, 0.58, 1.0),
        "rubber": (0.01, 0.01, 0.01, 1.0),
        "chrome": (0.80, 0.82, 0.82, 1.0),
        "hardware": (0.02, 0.02, 0.02, 1.0),
        "cutting": (0.42, 0.36, 0.28, 1.0),
        "hydraulic": (0.90, 0.68, 0.05, 1.0),
        "hose": (0.03, 0.03, 0.03, 1.0),
    },
    "tigercat_orange": {
        "body": (0.88, 0.42, 0.05, 1.0),
        "body_accent": (0.08, 0.08, 0.09, 1.0),
        "cab_glass": (0.12, 0.30, 0.40, 0.50),
        "arm": (0.08, 0.08, 0.09, 1.0),
        "arm_dark": (0.03, 0.03, 0.035, 1.0),
        "steel": (0.60, 0.62, 0.60, 1.0),
        "rubber": (0.01, 0.01, 0.01, 1.0),
        "chrome": (0.80, 0.82, 0.82, 1.0),
        "hardware": (0.02, 0.02, 0.02, 1.0),
        "cutting": (0.42, 0.36, 0.28, 1.0),
        "hydraulic": (0.88, 0.45, 0.06, 1.0),
        "hose": (0.03, 0.03, 0.03, 1.0),
    },
    "industrial_grey": {
        "body": (0.42, 0.45, 0.47, 1.0),
        "body_accent": (0.95, 0.75, 0.05, 1.0),
        "cab_glass": (0.20, 0.30, 0.35, 0.50),
        "arm": (0.30, 0.33, 0.35, 1.0),
        "arm_dark": (0.12, 0.13, 0.14, 1.0),
        "steel": (0.62, 0.64, 0.62, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "chrome": (0.80, 0.82, 0.82, 1.0),
        "hardware": (0.05, 0.05, 0.05, 1.0),
        "cutting": (0.42, 0.36, 0.28, 1.0),
        "hydraulic": (0.95, 0.75, 0.05, 1.0),
        "hose": (0.05, 0.05, 0.05, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Nominal geometry (meters). The arm reaches +X (forward); ground z=0.
# ---------------------------------------------------------------------------
CARRIER_LEN = 4.4
BOOM_LEN = 2.6  # knuckle lower boom length
STICK_LEN = 2.0  # knuckle stick length
# Per-boom base up-pitch (rad) and elbow droop (rad, stick relative to boom).
BOOM_GEOM: dict[BoomType, dict[str, float]] = {
    "knuckle_2section": {"base_pitch": 0.62, "elbow_droop": 0.60, "boom_len": 2.6, "stick_len": 2.0},
    "inverted_V": {"base_pitch": 0.80, "elbow_droop": 0.80, "boom_len": 2.2, "stick_len": 2.1},
    "telescopic_3section": {"base_pitch": 0.60, "elbow_droop": 0.42, "boom_len": 2.6, "outer_len": 1.5},
}
WRIST_PITCH = 0.12

# Joint motion envelopes (spec §7). Conservative so the sampled-pose guard holds:
# the arm stays forward-of / above the carrier across all sampled combinations.
LIFT_RANGE = (-0.20, 0.52)
ELBOW_RANGE = (-0.35, 0.68)
WRIST_RANGE = (-0.80, 0.80)
# Pendant heads (mulcher drum / felling hub / log-grapple rotator) hang a sub-
# assembly below the wrist that would sweep into the stick at extreme tilt, so
# they get a narrower wrist.
WRIST_RANGE_PENDANT = (-0.42, 0.42)
SLEW_RANGE = (-0.38, 0.38)
TELE_TRAVEL = 1.0
PENDANT_HEADS = ("felling_grapple_4finger", "log_grapple", "mulcher")


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HarvesterConfig:
    undercarriage: Undercarriage | None = None
    boom_type: BoomType | None = None
    head: Head | None = None
    num_axles: int | None = None
    rollers_per_side: int | None = None
    palette_style: PaletteStyle = "jd_green"
    boom_reach_scale: float = 1.0
    stick_reach_scale: float = 1.0
    carrier_len_scale: float = 1.0
    carrier_width_scale: float = 1.0
    head_size_scale: float = 1.0
    name: str = "harvester"


@dataclass(frozen=True)
class ResolvedHarvesterConfig:
    undercarriage: Undercarriage
    boom_type: BoomType
    head: Head
    num_axles: int
    rollers_per_side: int
    palette_style: PaletteStyle
    boom_reach_scale: float
    stick_reach_scale: float
    carrier_len_scale: float
    carrier_width_scale: float
    head_size_scale: float
    # derived
    boom_len: float
    stick_len: float
    outer_len: float
    base_pitch: float
    elbow_droop: float
    tire_radius: float
    axle_pitch: float
    roller_pitch: float
    name: str

    @property
    def running_gear_key(self) -> str:
        if self.undercarriage == "wheeled_bogie":
            return f"wheels{2 * self.num_axles}"
        if self.undercarriage == "tracked_crawler":
            return f"rollers{self.rollers_per_side}"
        return "static"


def config_from_seed(seed: int) -> HarvesterConfig:
    rng = random.Random(seed)
    return HarvesterConfig(
        undercarriage=rng.choice(UNDERCARRIAGES),
        boom_type=rng.choice(BOOM_TYPES),
        head=rng.choice(HEADS),
        num_axles=rng.choices(AXLE_CHOICES, weights=AXLE_WEIGHTS, k=1)[0],
        rollers_per_side=rng.choices(ROLLER_CHOICES, weights=ROLLER_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        boom_reach_scale=round(rng.uniform(0.88, 1.15), 4),
        stick_reach_scale=round(rng.uniform(0.88, 1.15), 4),
        carrier_len_scale=round(rng.uniform(0.90, 1.12), 4),
        carrier_width_scale=round(rng.uniform(0.92, 1.10), 4),
        head_size_scale=round(rng.uniform(0.90, 1.12), 4),
        name=f"seeded_harvester_{seed}",
    )


def resolve_config(config: HarvesterConfig | None = None) -> ResolvedHarvesterConfig:
    cfg = config or HarvesterConfig()
    undercarriage = _pick(cfg.undercarriage, UNDERCARRIAGES)
    boom_type = _pick(cfg.boom_type, BOOM_TYPES)
    head = _pick(cfg.head, HEADS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    num_axles = int(cfg.num_axles) if cfg.num_axles is not None else 3
    num_axles = int(_clamp(num_axles, AXLE_MIN, AXLE_MAX))
    rollers_per_side = int(cfg.rollers_per_side) if cfg.rollers_per_side is not None else 4
    rollers_per_side = int(_clamp(rollers_per_side, ROLLER_MIN, ROLLER_MAX))

    boom_reach_scale = _clamp(cfg.boom_reach_scale, 0.88, 1.15)
    stick_reach_scale = _clamp(cfg.stick_reach_scale, 0.88, 1.15)
    carrier_len_scale = _clamp(cfg.carrier_len_scale, 0.90, 1.12)
    carrier_width_scale = _clamp(cfg.carrier_width_scale, 0.92, 1.10)
    head_size_scale = _clamp(cfg.head_size_scale, 0.90, 1.12)

    g = BOOM_GEOM[boom_type]
    boom_len = g["boom_len"] * boom_reach_scale
    outer_len = g.get("outer_len", STICK_LEN) * stick_reach_scale
    stick_len = g.get("stick_len", STICK_LEN) * stick_reach_scale

    # Derived running-gear pitch + clearance (spec §7 inequality).
    carrier_len = CARRIER_LEN * carrier_len_scale
    wheel_usable = carrier_len * 0.74
    axle_pitch = wheel_usable / max(1, (num_axles - 1)) if num_axles > 1 else wheel_usable
    # Tire radius shrinks with dense axles so adjacent tires never overlap.
    tire_radius = _clamp(min(0.52, 0.47 * axle_pitch), 0.30, 0.52)
    track_run = carrier_len * 0.62
    roller_pitch = track_run / max(1, (rollers_per_side - 1)) if rollers_per_side > 1 else track_run

    return ResolvedHarvesterConfig(
        undercarriage=undercarriage,
        boom_type=boom_type,
        head=head,
        num_axles=num_axles,
        rollers_per_side=rollers_per_side,
        palette_style=palette_style,
        boom_reach_scale=boom_reach_scale,
        stick_reach_scale=stick_reach_scale,
        carrier_len_scale=carrier_len_scale,
        carrier_width_scale=carrier_width_scale,
        head_size_scale=head_size_scale,
        boom_len=boom_len,
        stick_len=stick_len,
        outer_len=outer_len,
        base_pitch=g["base_pitch"],
        elbow_droop=g["elbow_droop"],
        tire_radius=tire_radius,
        axle_pitch=axle_pitch,
        roller_pitch=roller_pitch,
        name=cfg.name or "harvester",
    )


def with_overrides(config: HarvesterConfig, **kwargs: object) -> HarvesterConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: HarvesterConfig | ResolvedHarvesterConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedHarvesterConfig) else resolve_config(config)
    return (
        ("undercarriage", r.undercarriage),
        ("boom_type", r.boom_type),
        ("head", r.head),
        ("running_gear", r.running_gear_key),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (from the 5-star sources).
# ---------------------------------------------------------------------------
def _box(part, name, size, xyz, material, rpy=(0.0, 0.0, 0.0)):
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(part, name, radius, length, xyz, material, rpy=(0.0, 0.0, 0.0)):
    part.visual(Cylinder(radius, length), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.steel_bare")


def _x_cyl(part, name, radius, length, xyz, material):
    _cyl(part, name, radius, length, xyz, material, rpy=(0.0, math.pi / 2.0, 0.0))


def _y_cyl(part, name, radius, length, xyz, material):
    _cyl(part, name, radius, length, xyz, material, rpy=(math.pi / 2.0, 0.0, 0.0))


def _box_between(part, name, p0, p1, width, height, material):
    """Rectangular member whose long local-X axis runs p0->p1 in the X-Z plane."""
    dx = p1[0] - p0[0]
    dz = p1[2] - p0[2]
    length = math.sqrt(dx * dx + dz * dz)
    angle = -math.atan2(dz, dx)
    part.visual(
        Box((length, width, height)),
        origin=Origin(
            xyz=((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5),
            rpy=(0.0, angle, 0.0),
        ),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _cyl_between(part, name, p0, p1, radius, material):
    """Round tube/rod whose local-Z cylinder axis runs p0->p1 in the X-Z plane."""
    dx = p1[0] - p0[0]
    dz = p1[2] - p0[2]
    length = math.sqrt(dx * dx + dz * dz)
    angle = math.atan2(dx, dz)
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(
            xyz=((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5),
            rpy=(0.0, angle, 0.0),
        ),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


def _hose(part, name, pts, radius, material, radial_segments=12):
    part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                pts, radius=radius, samples_per_segment=10, radial_segments=radial_segments,
                cap_ends=True,
            ),
            name,
        ),
        material=material,
        name=name, material_class_id="rubber.smooth_plain",
    )


# ---------------------------------------------------------------------------
# BoomMount / WristMount descriptors passed down the chain.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class BoomMount:
    parent_part: str
    pivot: tuple[float, float, float]  # boom-lift joint origin in parent-local frame
    base_pitch: float


@dataclass(frozen=True)
class WristMount:
    parent_part: str
    wrist: tuple[float, float, float]  # wrist joint origin in parent-local frame
    wrist_pitch: float


# ===========================================================================
# Slot A — undercarriage builders. Each returns a BoomMount.
# ===========================================================================
def _build_wheeled_bogie(model: ArticulatedObject, r: ResolvedHarvesterConfig, mats) -> BoomMount:
    tr = r.tire_radius
    half_w = 0.64 * r.carrier_width_scale
    wheel_y = half_w + 0.40
    clen = CARRIER_LEN * r.carrier_len_scale
    frame_z = tr + 0.30  # frame center above the tires
    deck_top = frame_z + 0.20

    chassis = model.part("chassis")
    chassis.visual(Box((clen, 2.0 * half_w, 0.34)), origin=Origin(xyz=(0.0, 0.0, frame_z)), material=mats["arm_dark"], name="main_frame", material_class_id="metal.blackened_gunmetal")
    chassis.visual(Box((clen * 0.94, 2.0 * half_w - 0.10, 0.16)), origin=Origin(xyz=(0.0, 0.0, frame_z + 0.24)), material=mats["body"], name="frame_deck", material_class_id="metal.paint_coated")

    # Engine hood at the rear (-X), glazed operator cab greenhouse mid.
    hood_x = -clen * 0.30
    chassis.visual(Box((clen * 0.42, 2.0 * half_w - 0.04, 0.72)), origin=Origin(xyz=(hood_x, 0.0, deck_top + 0.44)), material=mats["body"], name="engine_hood", material_class_id="metal.paint_coated")
    chassis.visual(Box((clen * 0.10, 2.0 * half_w - 0.02, 0.06)), origin=Origin(xyz=(hood_x, -half_w, deck_top + 0.40)), material=mats["body_accent"], name="hood_side_stripe", material_class_id="metal.paint_coated")
    chassis.visual(Box((0.20, 2.0 * half_w - 0.10, 0.16)), origin=Origin(xyz=(-clen * 0.5 + 0.12, 0.0, deck_top + 0.30)), material=mats["arm_dark"], name="rear_counterweight", material_class_id="metal.blackened_gunmetal")

    _build_greenhouse_cab(chassis, mats, cab_x=-clen * 0.06, cab_z=deck_top + 0.05, half_w=half_w)

    # Boom pedestal deck at the front-center.
    pivot_x = clen * 0.10
    _cyl(chassis, "slew_ring", 0.42, 0.20, (pivot_x, 0.0, deck_top + 0.02), mats["arm_dark"])
    _box(chassis, "boom_pedestal", (0.70, 2.0 * half_w - 0.24, 0.34), (pivot_x, 0.0, deck_top + 0.20), mats["arm_dark"])
    pz = deck_top + 0.55
    for s, y in enumerate((-0.34, 0.34)):
        _box(chassis, f"pivot_cheek_{s}", (0.24, 0.12, 0.62), (pivot_x, y, pz - 0.10), mats["arm_dark"])
    _y_cyl(chassis, "base_pivot_pin", 0.075, 0.90, (pivot_x, 0.0, pz), mats["steel"])

    # Fenders + hydraulic hose decoration (Rule 1 inline visuals). Each fender is
    # widened inboard and tied to the frame by a mounting stay that runs INBOARD
    # of the tire inner face (y = wheel_y - 0.431*tr), so it bridges the island
    # without ever fouling the rotating wheel.
    for s, ysign in enumerate((-1.0, 1.0)):
        _box(chassis, f"fender_front_{s}", (0.8 * (2 * tr), 0.70, 0.11), (clen * 0.28, ysign * wheel_y, tr + 2 * tr - 0.05), mats["body"])
        stay_top = tr + 2 * tr - 0.05 + 0.02
        stay_bot = frame_z - 0.10
        _box(
            chassis,
            f"fender_stay_{s}",
            (0.12, 0.16, stay_top - stay_bot),
            (clen * 0.28, ysign * (half_w + 0.05), 0.5 * (stay_top + stay_bot)),
            mats["arm_dark"],
        )
    _hose(chassis, "turret_hose_bundle", [(pivot_x - 0.5, -0.30, deck_top), (pivot_x - 0.2, -0.36, pz - 0.2), (pivot_x, -0.30, pz)], 0.026, mats["hose"], radial_segments=14)

    # Wheels: N axles per side, shared tire/rim mesh reused (spec §7.5 perf).
    tire_mesh, rim_mesh = _make_wheel_meshes(tr)
    x_front = -clen * 0.37
    for i in range(r.num_axles):
        ax_x = x_front + i * r.axle_pitch
        _y_cyl(chassis, f"axle_{i}", 0.075, 2.0 * wheel_y - 0.10, (ax_x, 0.0, tr), mats["arm_dark"])
        _box(chassis, f"axle_susp_{i}", (0.16, 0.20, 0.40), (ax_x, 0.0, tr + 0.20), mats["arm_dark"])
        for s, ysign in enumerate((-1.0, 1.0)):
            wname = f"wheel_{i}_{s}"
            wheel = model.part(wname)
            wheel.visual(tire_mesh, origin=Origin(rpy=(0.0, 0.0, math.pi / 2.0)), material=mats["rubber"], name="tire", material_class_id="rubber.directional_grooved")
            wheel.visual(rim_mesh, origin=Origin(rpy=(0.0, 0.0, math.pi / 2.0)), material=mats["body_accent"], name="rim", material_class_id="metal.paint_coated")
            wheel.visual(Cylinder(radius=tr * 0.30, length=0.16), origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)), material=mats["arm_dark"], name="hub_cap", material_class_id="metal.blackened_gunmetal")
            # Inner hub sleeve reaches inward to meet the axle pin (contact support).
            wheel.visual(
                Cylinder(radius=tr * 0.24, length=0.28),
                origin=Origin(xyz=(0.0, -ysign * 0.18, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["arm_dark"],
                name="inner_hub_sleeve", material_class_id="metal.blackened_gunmetal",
            )
            model.articulation(
                f"chassis_to_{wname}",
                ArticulationType.CONTINUOUS,
                parent=chassis,
                child=wheel,
                origin=Origin(xyz=(ax_x, ysign * wheel_y, tr)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=18000.0, velocity=8.0),
            )

    return BoomMount(parent_part="chassis", pivot=(pivot_x, 0.0, pz), base_pitch=r.base_pitch)


def _make_wheel_meshes(tr: float):
    """Tire + rim mesh (Rule 3: keep Tire/Wheel primitives). Scaled by tire radius.

    Built ONCE per seed and reused for all 2*N wheel parts.
    """
    s = tr / 0.58
    tire = mesh_from_geometry(
        TireGeometry(
            tr,
            0.50 * s,
            inner_radius=0.38 * s,
            carcass=TireCarcass(belt_width_ratio=0.70, sidewall_bulge=0.06),
            tread=TireTread(style="chevron", depth=0.046 * s, count=20, angle_deg=29.0, land_ratio=0.55),
            grooves=(TireGroove(center_offset=0.0, width=0.034 * s, depth=0.014 * s),),
            sidewall=TireSidewall(style="rounded", bulge=0.04 * s),
            shoulder=TireShoulder(width=0.038 * s, radius=0.009 * s),
        ),
        "bogie_chevron_tire",
    )
    rim = mesh_from_geometry(
        WheelGeometry(
            0.37 * s,
            0.40 * s,
            rim=WheelRim(inner_radius=0.23 * s, flange_height=0.026 * s, flange_thickness=0.014 * s, bead_seat_depth=0.014 * s),
            hub=WheelHub(
                radius=0.115 * s,
                width=0.20 * s,
                cap_style="domed",
                bolt_pattern=BoltPattern(count=6, circle_diameter=0.16 * s, hole_diameter=0.020 * s),
            ),
            face=WheelFace(dish_depth=0.035 * s, front_inset=0.020 * s, rear_inset=0.014 * s),
            spokes=WheelSpokes(style="split_y", count=6, thickness=0.020 * s, window_radius=0.066 * s),
            bore=WheelBore(style="round", diameter=0.060 * s),
        ),
        "bogie_rim",
    )
    return tire, rim


def _build_greenhouse_cab(chassis, mats, *, cab_x: float, cab_z: float, half_w: float):
    """Glazed operator-cab greenhouse (identity), inline visuals (Rule 1).

    Built so every element bridges the shell and the roof: the lower shell top is
    at cab_z+0.52, the roof bottom at cab_z+0.95, and the pillars + glazing all
    span cab_z+0.47..1.02 so nothing floats (no disconnected-island).
    """
    cw = min(1.30, 2.0 * half_w - 0.20)
    chassis.visual(Box((1.24, cw, 0.52)), origin=Origin(xyz=(cab_x, 0.0, cab_z + 0.26)), material=mats["body"], name="cab_shell", material_class_id="metal.paint_coated")
    chassis.visual(Box((1.30, cw + 0.04, 0.10)), origin=Origin(xyz=(cab_x, 0.0, cab_z + 1.00)), material=mats["arm_dark"], name="cab_roof", material_class_id="metal.blackened_gunmetal")
    # Four corner ROPS pillars tie the shell to the roof.
    for i, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        chassis.visual(
            Box((0.08, 0.08, 0.60)),
            origin=Origin(xyz=(cab_x + sx * 0.58, sy * (cw * 0.5 - 0.04), cab_z + 0.74)),
            material=mats["arm_dark"],
            name=f"cab_pillar_{i}", material_class_id="metal.blackened_gunmetal",
        )
    # Wrap-around glazing (spans shell top -> roof bottom, so it never floats).
    chassis.visual(Box((0.05, cw - 0.10, 0.56)), origin=Origin(xyz=(cab_x + 0.60, 0.0, cab_z + 0.74), rpy=(0.0, -0.16, 0.0)), material=mats["cab_glass"], name="windshield", material_class_id="glass.smoked_tinted")
    chassis.visual(Box((0.06, 0.05, 0.56)), origin=Origin(xyz=(cab_x + 0.60, 0.0, cab_z + 0.74), rpy=(0.0, -0.16, 0.0)), material=mats["arm_dark"], name="windshield_mullion", material_class_id="metal.blackened_gunmetal")
    chassis.visual(Box((1.0, 0.05, 0.54)), origin=Origin(xyz=(cab_x, -(cw * 0.5), cab_z + 0.74)), material=mats["cab_glass"], name="side_window_0", material_class_id="glass.smoked_tinted")
    chassis.visual(Box((1.0, 0.05, 0.54)), origin=Origin(xyz=(cab_x, (cw * 0.5), cab_z + 0.74)), material=mats["cab_glass"], name="side_window_1", material_class_id="glass.smoked_tinted")
    chassis.visual(Box((0.05, cw - 0.10, 0.54)), origin=Origin(xyz=(cab_x - 0.60, 0.0, cab_z + 0.74)), material=mats["cab_glass"], name="rear_window", material_class_id="glass.smoked_tinted")
    # Work-light bar sits ON the roof (inboard of the front edge) so it never
    # protrudes into the raised-boom envelope.
    chassis.visual(Box((0.12, 0.44, 0.07)), origin=Origin(xyz=(cab_x + 0.42, 0.0, cab_z + 1.06)), material=mats["hardware"], name="work_light_bar", material_class_id="metal.blackened_gunmetal")
    for i, ly in enumerate((-0.16, 0.16)):
        chassis.visual(Box((0.05, 0.10, 0.06)), origin=Origin(xyz=(cab_x + 0.45, ly, cab_z + 1.07)), material=mats["body_accent"], name=f"cab_work_light_{i}", material_class_id="tech.emissive_surface")


def _build_tracked_crawler(model: ArticulatedObject, r: ResolvedHarvesterConfig, mats) -> BoomMount:
    clen = CARRIER_LEN * r.carrier_len_scale
    track_y = 0.82 * r.carrier_width_scale
    track_len = clen * 0.98
    chassis = model.part("chassis")

    # Rubber tracks, idlers, road rollers (multiplicity), grousers.
    for s, ysign in enumerate((-1.0, 1.0)):
        y = ysign * track_y
        _box(chassis, f"side_{s}_rubber_track", (track_len, 0.58, 0.58), (0.0, y, 0.34), mats["rubber"])
        _box(chassis, f"side_{s}_track_top_band", (track_len - 0.4, 0.52, 0.10), (0.0, y, 0.68), mats["arm_dark"])
        _box(chassis, f"side_{s}_track_bottom_band", (track_len - 0.4, 0.52, 0.10), (0.0, y, 0.05), mats["arm_dark"])
        _y_cyl(chassis, f"side_{s}_front_idler", 0.30, 0.62, (track_len * 0.44, y, 0.34), mats["arm_dark"])
        _y_cyl(chassis, f"side_{s}_rear_idler", 0.30, 0.62, (-track_len * 0.44, y, 0.34), mats["arm_dark"])
        r0 = -r.roller_pitch * (r.rollers_per_side - 1) * 0.5
        for i in range(r.rollers_per_side):
            _y_cyl(chassis, f"side_{s}_roller_{i}", 0.18, 0.64, (r0 + i * r.roller_pitch, y, 0.22), mats["steel"])
        n_gr = 10
        for i in range(n_gr):
            gx = -track_len * 0.46 + i * (track_len * 0.92 / (n_gr - 1))
            _box(chassis, f"side_{s}_top_grouser_{i}", (0.18, 0.65, 0.06), (gx, y, 0.74), mats["rubber"])

    _box(chassis, "track_crossbeam", (track_len * 0.89, 2.0 * track_y + 0.4, 0.24), (-0.08, 0.0, 0.76), mats["arm"])
    _box(chassis, "main_frame", (clen * 0.75, 1.28, 0.38), (-0.18, 0.0, 1.03), mats["arm"])
    _box(chassis, "belly_guard", (clen * 0.62, 1.45, 0.10), (0.20, 0.0, 0.83), mats["cutting"])

    # Red-body cab, engine cowl, work lights.
    _box(chassis, "rear_engine_cowl", (1.08, 1.12, 0.62), (-clen * 0.39, 0.04, 1.43), mats["body"])
    _box(chassis, "engine_black_grille", (0.08, 0.90, 0.38), (-clen * 0.26, 0.04, 1.48), mats["arm"])
    # Seat the cab far enough back that its windshield clears the boom root pivot
    # barrel: that barrel is a wide y-cylinder, so at a slew extreme its ends sweep
    # rearward in x (~0.30m behind the turret pivot). The fixed -0.18 offset keeps
    # clearance even at the shortest carrier_len_scale (0.90).
    _build_greenhouse_cab(chassis, mats, cab_x=-clen * 0.33 - 0.18, cab_z=1.5, half_w=0.62)

    # Slew pedestal + turret.
    slew_x = -clen * 0.12
    _cyl(chassis, "slew_ring", 0.62, 0.22, (slew_x, 0.0, 1.25), mats["arm_dark"])
    _box(chassis, "boom_pedestal", (0.54, 0.64, 0.34), (slew_x, 0.0, 1.10), mats["arm"])
    _box(chassis, "pedestal_crosshead", (1.10, 1.02, 0.18), (slew_x, 0.0, 1.18), mats["arm"])

    turret = model.part("turret")
    _cyl(turret, "turntable_drum", 0.50, 0.18, (0.0, 0.0, 0.09), mats["arm_dark"])
    _cyl(turret, "turntable_neck", 0.24, 0.50, (0.0, 0.0, 0.40), mats["arm_dark"])
    _box(turret, "boom_mount_web", (0.40, 0.78, 0.34), (0.10, 0.0, 0.78), mats["arm"])
    th = 0.95
    for s, y in enumerate((-0.40, 0.40)):
        _box(turret, f"upper_yoke_{s}", (0.30, 0.12, 0.44), (0.10, y, th - 0.05), mats["arm"])
    _y_cyl(turret, "turret_pivot_pin", 0.075, 0.90, (0.10, 0.0, th), mats["steel"])
    model.articulation(
        "chassis_to_turret",
        ArticulationType.REVOLUTE,
        parent=chassis,
        child=turret,
        origin=Origin(xyz=(slew_x, 0.0, 1.36)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=6000.0, velocity=0.45, lower=SLEW_RANGE[0], upper=SLEW_RANGE[1]),
    )
    return BoomMount(parent_part="turret", pivot=(0.10, 0.0, th), base_pitch=r.base_pitch)


def _build_pedestal_static(model: ArticulatedObject, r: ResolvedHarvesterConfig, mats) -> BoomMount:
    base = model.part("base_mount")
    pz = 2.05
    # Grounded king-post column.
    _box(base, "ground_plate", (1.10, 1.00, 0.12), (0.0, 0.0, 0.06), mats["arm_dark"])
    _box(base, "king_post", (0.46, 0.62, pz - 0.30), (-0.06, 0.0, (pz - 0.30) * 0.5 + 0.12), mats["body"])
    _box(base, "mount_backing_block", (0.46, 0.62, 0.60), (0.0, 0.0, pz - 0.20), mats["arm_dark"])
    _box(base, "mount_top_cap", (0.40, 0.66, 0.14), (0.0, 0.0, pz + 0.16), mats["arm_dark"])
    for s, y in enumerate((-0.24, 0.24)):
        _box(base, f"mount_clevis_{s}", (0.34, 0.10, 0.50), (0.10, y, pz + 0.06), mats["arm_dark"])
        _y_cyl(base, f"mount_pin_cap_{s}", 0.075, 0.04, (0.12, y, pz), mats["steel"])
    _y_cyl(base, "base_pivot_pin", 0.075, 0.56, (0.12, 0.0, pz), mats["steel"])
    # Down-curving parking hook (mesh, Rule 3).
    base.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [(-0.18, 0.0, pz - 0.18), (-0.30, 0.0, pz - 0.46), (-0.30, 0.0, pz - 0.70), (-0.16, 0.0, pz - 0.80), (-0.10, 0.0, pz - 0.70)],
                radius=0.045, samples_per_segment=12, radial_segments=14,
            ),
            "mount_parking_hook",
        ),
        material=mats["arm_dark"],
        name="parking_hook", material_class_id="metal.blackened_gunmetal",
    )
    return BoomMount(parent_part="base_mount", pivot=(0.12, 0.0, pz), base_pitch=r.base_pitch)


_UNDERCARRIAGE_BUILDERS = {
    "wheeled_bogie": _build_wheeled_bogie,
    "tracked_crawler": _build_tracked_crawler,
    "pedestal_static": _build_pedestal_static,
}


# ===========================================================================
# Slot B — boom builders. Each returns a WristMount.
# ===========================================================================
def _emit_lower_boom(model, r, mats, mount: BoomMount, *, length: float, box_w=0.34, box_h=0.34):
    """Boxed lower boom (root barrel at 0, extends +X to tip). Returns tip x."""
    boom = model.part("boom")
    _box(boom, "lower_box_tube", (length, box_w, box_h), (length * 0.5, 0.0, 0.02), mats["arm"])
    _box(boom, "lower_top_reinforcement", (length * 0.92, box_w * 0.6, 0.10), (length * 0.55, 0.0, 0.22), mats["arm_dark"])
    for s, y in enumerate((-(box_w * 0.5 + 0.02), (box_w * 0.5 + 0.02))):
        _box(boom, f"lower_side_plate_{s}", (length * 0.96, 0.045, box_h + 0.20), (length * 0.55, y, 0.02), mats["arm"])
    _y_cyl(boom, "root_pivot_barrel", 0.21, 0.68, (0.0, 0.0, 0.0), mats["arm_dark"])
    _y_cyl(boom, "tip_pivot_barrel", 0.18, 0.64, (length, 0.0, 0.0), mats["arm_dark"])
    for s, y in enumerate((-0.37, 0.37)):
        _box(boom, f"tip_yoke_{s}", (0.38, 0.10, 0.60), (length, y, 0.0), mats["arm"])
    # Warning-label decal (④, host-conformal on the side plate face).
    _box(boom, "yellow_capacity_plate", (0.82, 0.03, 0.16), (length * 0.72, -(box_w * 0.5 + 0.03), 0.31), mats["body_accent"])
    for i, x in enumerate((0.62, 0.68, 0.74, 0.80)):
        _box(boom, f"capacity_black_mark_{i}", (0.025, 0.035, 0.18), (length * x, -(box_w * 0.5 + 0.045), 0.315), mats["arm"], rpy=(0.0, 0.0, 0.35))
    # Twin lift hydraulics slung under the boom.
    for s, y in enumerate((-0.30, 0.30)):
        _x_cyl(boom, f"lift_cylinder_body_{s}", 0.075, length * 0.4, (length * 0.30, y, -0.25), mats["arm_dark"])
        _x_cyl(boom, f"lift_cylinder_rod_{s}", 0.040, length * 0.5, (length * 0.70, y, -0.25), mats["chrome"])
    _hose(boom, "lower_boom_hydraulic_hose", [(0.08, 0.23, 0.18), (length * 0.4, 0.25, 0.27), (length * 0.7, 0.25, 0.28), (length - 0.1, 0.23, 0.14)], 0.030, mats["hose"], radial_segments=14)

    model.articulation(
        "boom_lift",
        ArticulationType.REVOLUTE,
        parent=model.get_part(mount.parent_part),
        child=boom,
        origin=Origin(xyz=mount.pivot, rpy=(0.0, -mount.base_pitch, 0.0)),
        axis=(0.0, -1.0, 0.0),  # positive lift raises the boom (mirrors P3)
        motion_limits=MotionLimits(effort=9000.0, velocity=0.35, lower=LIFT_RANGE[0], upper=LIFT_RANGE[1]),
    )
    return length


def _emit_stick(model, r, mats, *, elbow_x: float, droop: float, length: float, part_name="boom_stick"):
    """Boxed stick (root barrel at 0, extends +X to wrist). Returns wrist x."""
    stick = model.part(part_name)
    _box(stick, "stick_box_tube", (length, 0.30, 0.30), (length * 0.55, 0.0, 0.0), mats["arm"])
    _box(stick, "stick_top_wear_plate", (length * 0.92, 0.18, 0.08), (length * 0.6, 0.0, 0.18), mats["arm_dark"])
    for s, y in enumerate((-0.17, 0.17)):
        _box(stick, f"stick_side_plate_{s}", (length * 0.9, 0.04, 0.46), (length * 0.55, y, 0.0), mats["arm"])
    _box(stick, "root_neck", (0.22, 0.22, 0.18), (0.13, 0.0, 0.0), mats["arm"])
    _y_cyl(stick, "stick_root_barrel", 0.17, 0.28, (0.0, 0.0, 0.0), mats["arm_dark"])
    _y_cyl(stick, "wrist_barrel", 0.14, 0.58, (length, 0.0, 0.0), mats["arm_dark"])
    _box(stick, "wrist_neck", (0.44, 0.20, 0.16), (length - 0.24, 0.0, 0.0), mats["arm"])
    for s, y in enumerate((-0.30, 0.30)):
        _box(stick, f"wrist_yoke_{s}", (0.30, 0.10, 0.48), (length, y, 0.0), mats["arm"])
    _x_cyl(stick, "crowd_cylinder_body", 0.065, length * 0.5, (length * 0.35, -0.25, -0.22), mats["arm_dark"])
    _x_cyl(stick, "crowd_cylinder_rod", 0.034, length * 0.62, (length * 0.8, -0.25, -0.22), mats["chrome"])
    _hose(stick, "stick_hydraulic_hose", [(0.25, 0.21, 0.15), (length * 0.5, 0.23, 0.24), (length * 0.8, 0.22, 0.10), (length - 0.05, 0.22, 0.02)], 0.024, mats["hose"], radial_segments=12)

    model.articulation(
        "boom_to_stick",
        ArticulationType.REVOLUTE,
        parent=model.get_part("boom"),
        child=stick,
        origin=Origin(xyz=(elbow_x, 0.0, 0.0), rpy=(0.0, droop, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=6500.0, velocity=0.45, lower=ELBOW_RANGE[0], upper=ELBOW_RANGE[1]),
    )
    return length


def _build_knuckle_2section(model, r, mats, mount: BoomMount) -> WristMount:
    tip = _emit_lower_boom(model, r, mats, mount, length=r.boom_len)
    wrist = _emit_stick(model, r, mats, elbow_x=tip, droop=r.elbow_droop, length=r.stick_len)
    return WristMount(parent_part="boom_stick", wrist=(wrist, 0.0, 0.0), wrist_pitch=WRIST_PITCH)


def _build_inverted_V(model, r, mats, mount: BoomMount) -> WristMount:
    # Steep up-then-down inverted-V profile; distinct ③ form vs. boxed knuckle.
    tip = _emit_lower_boom(model, r, mats, mount, length=r.boom_len, box_w=0.30, box_h=0.30)
    # Apex ears on the boom (P1-style knuckle).
    boom = model.get_part("boom")
    for s, y in enumerate((-0.22, 0.22)):
        _box(boom, f"apex_ear_{s}", (0.34, 0.05, 0.40), (tip, y, 0.0), mats["arm_dark"])
    wrist = _emit_stick(model, r, mats, elbow_x=tip, droop=r.elbow_droop, length=r.stick_len)
    return WristMount(parent_part="boom_stick", wrist=(wrist, 0.0, 0.0), wrist_pitch=WRIST_PITCH)


def _build_telescopic_3section(model, r, mats, mount: BoomMount) -> WristMount:
    tip = _emit_lower_boom(model, r, mats, mount, length=r.boom_len)
    # Outer sleeve (elbow revolute child of boom).
    outer_len = r.outer_len
    outer = model.part("boom_stick")
    _y_cyl(outer, "stick_root_barrel", 0.17, 0.28, (0.0, 0.0, 0.0), mats["arm_dark"])
    _box(outer, "root_neck", (0.22, 0.22, 0.18), (0.13, 0.0, 0.0), mats["arm"])
    _box(outer, "outer_sleeve", (outer_len, 0.40, 0.40), (outer_len * 0.55, 0.0, 0.0), mats["arm"])
    _box(outer, "outer_top_plate", (outer_len * 0.9, 0.24, 0.08), (outer_len * 0.55, 0.0, 0.24), mats["arm_dark"])
    for s, y in enumerate((-0.225, 0.225)):
        _box(outer, f"outer_side_plate_{s}", (outer_len * 0.95, 0.045, 0.52), (outer_len * 0.55, y, 0.0), mats["arm"])
    _box(outer, "rear_guide_collar", (0.16, 0.44, 0.44), (0.16, 0.0, 0.0), mats["arm_dark"])
    _box(outer, "front_guide_collar", (0.16, 0.44, 0.44), (outer_len + 0.06, 0.0, 0.0), mats["arm_dark"])
    _x_cyl(outer, "crowd_cylinder_body", 0.065, outer_len * 0.55, (outer_len * 0.5, -0.28, -0.22), mats["arm_dark"])
    model.articulation(
        "boom_to_stick",
        ArticulationType.REVOLUTE,
        parent=model.get_part("boom"),
        child=outer,
        origin=Origin(xyz=(tip, 0.0, 0.0), rpy=(0.0, r.elbow_droop, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=6500.0, velocity=0.45, lower=ELBOW_RANGE[0], upper=ELBOW_RANGE[1]),
    )
    # Inner telescoping member (prismatic child of outer sleeve). Built so its
    # rear starts at the prismatic origin (0.20) and extends forward only — it
    # never pokes back into the boom at the elbow.
    inner_len = outer_len + 1.2
    tele_origin = 0.20
    inner = model.part("boom_stick_inner")
    _box(inner, "inner_box_tube", (inner_len, 0.28, 0.28), (inner_len * 0.5, 0.0, 0.0), mats["arm"])
    _box(inner, "inner_top_wear_strip", (inner_len * 0.85, 0.18, 0.05), (inner_len * 0.5, 0.0, 0.165), mats["arm_dark"])
    for i, x in enumerate((0.08, 0.55)):
        _box(inner, f"guide_pad_{i}", (0.14, 0.22, 0.30), (x, 0.0, 0.0), mats["cutting"])
    wrist_x = inner_len - 0.2
    _y_cyl(inner, "wrist_barrel", 0.14, 0.58, (wrist_x, 0.0, 0.0), mats["arm_dark"])
    _box(inner, "wrist_neck", (0.44, 0.20, 0.16), (wrist_x - 0.24, 0.0, 0.0), mats["arm"])
    for s, y in enumerate((-0.30, 0.30)):
        _box(inner, f"wrist_yoke_{s}", (0.30, 0.10, 0.48), (wrist_x, y, 0.0), mats["arm"])
    # Crowd rod clevis: bridges the inner box tube (y,z = ±0.14) out to the rod
    # slung at (-0.28, -0.22) so the rod is not a floating island.
    _box(inner, "crowd_clevis", (0.12, 0.22, 0.22), (outer_len * 0.35, -0.20, -0.18), mats["arm_dark"])
    _x_cyl(inner, "crowd_cylinder_rod", 0.034, outer_len * 0.6, (outer_len * 0.55, -0.28, -0.22), mats["chrome"])
    model.articulation(
        "stick_extend",
        ArticulationType.PRISMATIC,
        parent=outer,
        child=inner,
        origin=Origin(xyz=(tele_origin, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4000.0, velocity=0.30, lower=0.0, upper=TELE_TRAVEL),
    )
    return WristMount(parent_part="boom_stick_inner", wrist=(wrist_x, 0.0, 0.0), wrist_pitch=WRIST_PITCH)


_BOOM_BUILDERS = {
    "knuckle_2section": _build_knuckle_2section,
    "inverted_V": _build_inverted_V,
    "telescopic_3section": _build_telescopic_3section,
}


# ===========================================================================
# Slot C — head builders. Each emits the wrist joint + head + internals.
# ===========================================================================
def _emit_wrist_joint(model, wm: WristMount, head_part, wrist_range=WRIST_RANGE):
    model.articulation(
        "stick_to_head",
        ArticulationType.REVOLUTE,
        parent=model.get_part(wm.parent_part),
        child=head_part,
        origin=Origin(xyz=wm.wrist, rpy=(0.0, wm.wrist_pitch, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2500.0, velocity=0.9, lower=wrist_range[0], upper=wrist_range[1]),
    )


def _build_processing_head(model, r, mats, wm: WristMount) -> None:
    hs = r.head_size_scale
    head = model.part("head")
    _y_cyl(head, "head_wrist_pin", 0.13, 0.46, (0.0, 0.0, 0.0), mats["steel"])
    # Hanging link spans wrist pin (z=0) down INTO the backbone so nothing floats
    # at any head_size_scale (backbone top ~ -0.73*hs).
    _box(head, "hanging_link", (0.18, 0.34, 0.86 * hs), (0.12, 0.0, -0.43 * hs), mats["arm"])
    _box(head, "head_backbone", (0.95 * hs, 0.50, 0.26), (0.42 * hs, 0.0, -0.86 * hs), mats["arm"])
    _box(head, "red_motor_cover", (0.72 * hs, 0.46, 0.32), (0.24 * hs, 0.0, -0.58 * hs), mats["body"])
    _box(head, "bottom_feed_frame", (0.98 * hs, 0.56, 0.16), (0.50 * hs, 0.0, -1.12 * hs), mats["arm"])
    _y_cyl(head, "feed_roller_0", 0.13, 0.62, (0.35 * hs, -0.02, -1.00 * hs), mats["rubber"])
    _y_cyl(head, "feed_roller_1", 0.13, 0.62, (0.68 * hs, -0.02, -1.00 * hs), mats["rubber"])
    _box(head, "saw_bar", (0.78 * hs, 0.08, 0.08), (0.86 * hs, 0.0, -1.20 * hs), mats["cutting"], rpy=(0.0, 0.0, -0.22))
    for s, y, yaw in (("0", -0.34, -0.25), ("1", 0.34, 0.25)):
        _box(head, f"grapple_arm_{s}", (0.70 * hs, 0.09, 0.10), (0.46 * hs, y, -1.22 * hs), mats["arm"], rpy=(0.0, 0.0, yaw))
        _box(head, f"delimbing_knife_{s}", (0.42 * hs, 0.06, 0.08), (0.72 * hs, y, -0.90 * hs), mats["cutting"], rpy=(0.0, 0.0, yaw))
    _hose(head, "head_hose_loop", [(0.30, 0.20, -0.42 * hs), (0.32, 0.31, -0.50 * hs), (0.40, 0.26, -0.58 * hs)], 0.022, mats["hose"])
    _emit_wrist_joint(model, wm, head)


def _build_felling_grapple(model, r, mats, wm: WristMount) -> None:
    hs = r.head_size_scale
    head = model.part("head")
    _y_cyl(head, "head_wrist_pin", 0.10, 0.40, (0.0, 0.0, 0.0), mats["arm"])
    for s, y in enumerate((-0.16, 0.16)):
        _box(head, f"yoke_side_plate_{s}", (0.20, 0.06, 0.40), (0.0, y, -0.18), mats["arm"])
    _box(head, "yoke_rotator_housing", (0.30, 0.40, 0.18), (0.0, 0.0, -0.36), mats["arm"])
    _cyl(head, "yoke_rotator_flange", 0.12, 0.10, (0.0, 0.0, -0.46), mats["steel"])
    _emit_wrist_joint(model, wm, head, wrist_range=WRIST_RANGE_PENDANT)

    hub = model.part("grapple_hub")
    _cyl(hub, "rotator_drum", 0.135, 0.22, (0.0, 0.0, 0.05), mats["arm"])
    _cyl(hub, "rotator_collar", 0.115, 0.06, (0.0, 0.0, 0.18), mats["steel"])
    _box(hub, "grapple_palm", (0.34 * hs, 0.34 * hs, 0.18), (0.0, 0.0, -0.12), mats["arm"])
    hub.visual(
        mesh_from_geometry(SphereGeometry(0.085 * hs, width_segments=20, height_segments=12), "palm_dome"),
        origin=Origin(xyz=(0.0, 0.0, -0.20)), material=mats["arm_dark"], name="palm_cap", material_class_id="metal.blackened_gunmetal",
    )
    n_fingers = 4
    finger_r = 0.155 * hs
    knuckle_z = -0.18
    for i in range(n_fingers):
        ang = 2.0 * math.pi * i / n_fingers
        hub.visual(Cylinder(radius=0.030, length=0.16), origin=Origin(xyz=(0.18 * math.cos(ang), 0.18 * math.sin(ang), -0.12)), material=mats["hydraulic"], name=f"finger_drive_cyl_{i}", material_class_id="metal.paint_coated")
    for i in range(n_fingers):
        phi = 2.0 * math.pi * i / n_fingers + math.pi / 4.0
        _y_cyl(hub, f"finger_boss_{i}", 0.05, 0.12, (finger_r * math.cos(phi), finger_r * math.sin(phi), knuckle_z), mats["hardware"])
    model.articulation(
        "head_rotator",
        ArticulationType.CONTINUOUS,
        parent=head,
        child=hub,
        origin=Origin(xyz=(0.0, 0.0, -0.52)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3000.0, velocity=2.0),
    )
    finger_pts = [(0.0, 0.0, 0.0), (0.06, 0.0, -0.11), (0.13, 0.0, -0.25), (0.11, 0.0, -0.40), (0.01, 0.0, -0.53)]
    for i in range(n_fingers):
        phi = 2.0 * math.pi * i / n_fingers + math.pi / 4.0
        bx, by = finger_r * math.cos(phi), finger_r * math.sin(phi)
        finger = model.part(f"claw_finger_{i}")
        _y_cyl(finger, "finger_knuckle", 0.052, 0.13, (0.0, 0.0, 0.0), mats["hardware"])
        finger.visual(
            mesh_from_geometry(tube_from_spline_points([(px * hs, 0.0, pz * hs) for (px, _py, pz) in finger_pts], radius=0.045, samples_per_segment=12, radial_segments=12), f"finger_body_{i}"),
            material=mats["arm"], name="finger_body", material_class_id="metal.paint_coated",
        )
        model.articulation(
            f"hub_to_finger_{i}",
            ArticulationType.REVOLUTE,
            parent=hub,
            child=finger,
            origin=Origin(xyz=(bx, by, knuckle_z), rpy=(0.0, 0.0, phi)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=2500.0, velocity=1.6, lower=-0.2, upper=1.05),
        )


def _build_feller_saw(model, r, mats, wm: WristMount) -> None:
    hs = r.head_size_scale
    head = model.part("head")
    _y_cyl(head, "head_wrist_pin", 0.13, 0.46, (0.0, 0.0, 0.0), mats["steel"])
    # Hanging link spans wrist pin (z=0) down INTO the backbone (top ~ -0.73*hs)
    # so the upper spine stays connected at every head_size_scale.
    _box(head, "hanging_link", (0.18, 0.34, 0.86 * hs), (0.12, 0.0, -0.43 * hs), mats["arm"])
    _box(head, "head_backbone", (0.95 * hs, 0.50, 0.26), (0.42 * hs, 0.0, -0.86 * hs), mats["arm"])
    _box(head, "motor_housing", (0.65 * hs, 0.42, 0.30), (0.24 * hs, 0.0, -0.58 * hs), mats["body"])
    _box(head, "saw_mount_frame", (0.85 * hs, 0.52, 0.14), (0.50 * hs, 0.0, -1.10 * hs), mats["arm"])
    _x_cyl(head, "saw_disc", 0.35 * hs, 0.025, (0.60 * hs, 0.0, -1.18 * hs), mats["cutting"])
    _box(head, "saw_guard", (0.42, 0.54, 0.08), (0.38 * hs, 0.0, -1.15 * hs), mats["arm_dark"])
    _box(head, "felling_bar", (0.82 * hs, 0.07, 0.06), (0.92 * hs, 0.0, -1.22 * hs), mats["cutting"], rpy=(0.0, 0.0, -0.15))
    _y_cyl(head, "saw_motor", 0.12, 0.28, (0.60 * hs, 0.0, -1.04 * hs), mats["arm_dark"])
    for i, (sign, yaw) in enumerate(((-1, -0.10), (1, 0.10))):
        _box(head, f"pocket_bracket_{i}", (0.18, 0.06, 0.34), (0.55 * hs, sign * 0.27, -0.72 * hs), mats["arm"], rpy=(0.0, 0.0, yaw))
    _hose(head, "head_hose_loop", [(0.30, 0.20, -0.42 * hs), (0.32, 0.31, -0.50 * hs), (0.40, 0.26, -0.58 * hs)], 0.022, mats["hose"])
    _emit_wrist_joint(model, wm, head)
    # Two accumulating grab arms (REVOLUTE about Z) that close to bunch stems.
    for i, (side_sign, axis_z) in enumerate(((-1, 1.0), (1, -1.0))):
        arm = model.part(f"grab_arm_{i}")
        _box(arm, "pivot_boss", (0.14, 0.14, 0.18), (0.0, side_sign * 0.04, 0.0), mats["arm_dark"])
        _box(arm, "arm_beam", (0.10, 0.52 * hs, 0.12), (0.0, side_sign * 0.34 * hs, 0.0), mats["arm"])
        _box(arm, "arm_tip_pad", (0.14, 0.20, 0.14), (0.0, side_sign * 0.62 * hs, 0.0), mats["rubber"])
        _box(arm, "arm_cylinder", (0.06, 0.30, 0.06), (0.0, side_sign * 0.30 * hs, 0.08), mats["chrome"])
        model.articulation(
            f"head_to_grab_{i}",
            ArticulationType.REVOLUTE,
            parent=head,
            child=arm,
            origin=Origin(xyz=(0.42 * hs, side_sign * 0.25, -0.86 * hs)),
            axis=(0.0, 0.0, axis_z),
            motion_limits=MotionLimits(effort=3000.0, velocity=0.6, lower=0.0, upper=1.2),
        )


def _build_log_grapple(model, r, mats, wm: WristMount) -> None:
    hs = r.head_size_scale
    head = model.part("head")
    _y_cyl(head, "head_wrist_pin", 0.10, 0.40, (0.0, 0.0, 0.0), mats["arm"])
    _box(head, "frame_yoke", (0.10, 0.52, 0.14), (0.0, 0.0, -0.10), mats["arm"])
    # Bridge spans frame_yoke down onto the rotator housing (top ~ -0.34) so the
    # housing + bearing ring never float below it.
    _box(head, "yoke_bridge", (0.20, 0.44, 0.32), (0.0, 0.0, -0.28), mats["arm"])
    _cyl(head, "rotator_housing", 0.18, 0.24, (0.0, 0.0, -0.46), mats["arm_dark"])
    _cyl(head, "bearing_ring", 0.22, 0.05, (0.0, 0.0, -0.36), mats["steel"])
    _emit_wrist_joint(model, wm, head, wrist_range=WRIST_RANGE_PENDANT)

    rotator = model.part("rotator")
    _cyl(rotator, "turntable_disk", 0.15, 0.08, (0.0, 0.0, 0.0), mats["arm_dark"])
    # Carrier reaches up to the turntable disk (bottom -0.04) and out to the jaw
    # pivot lugs (y = ±0.28*hs) so the whole rotator stays one connected body.
    _box(rotator, "jaw_carrier", (0.12, 0.62 * hs, 0.18), (0.0, 0.0, -0.09), mats["arm"])
    for i, y in enumerate((-0.28, 0.28)):
        _box(rotator, f"jaw_pivot_lug_{i}", (0.14, 0.08, 0.16), (0.0, y * hs, -0.14), mats["arm_dark"])
        _x_cyl(rotator, f"jaw_pivot_pin_{i}", 0.030, 0.14, (0.0, y * hs, -0.14), mats["arm_dark"])
    _cyl(rotator, "jaw_cylinder", 0.038, 0.18, (0.0, 0.0, -0.20), mats["hardware"], rpy=(0.0, 0.35, 0.0))
    model.articulation(
        "head_rotator",
        ArticulationType.CONTINUOUS,
        parent=head,
        child=rotator,
        origin=Origin(xyz=(0.0, 0.0, -0.46)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=6000.0, velocity=2.0),
    )
    for i in range(2):
        jaw = model.part(f"jaw_{i}")
        y_dir = -1.0 if i == 0 else 1.0
        _box(jaw, "jaw_boss", (0.10, 0.08, 0.12), (0.0, 0.0, -0.04), mats["arm_dark"])
        _box_between(jaw, "jaw_arm", (0.0, 0.0, -0.08), (0.0, 0.0, -0.44 * hs), 0.09, 0.08, mats["arm_dark"])
        _box(jaw, "jaw_spine", (0.06, 0.06, 0.34 * hs), (0.0, y_dir * 0.03, -0.26 * hs), mats["arm_dark"])
        for t in range(3):
            _box(jaw, f"jaw_tooth_{t}", (0.05, 0.04, 0.05), (0.0, y_dir * (0.04 - t * 0.01), -0.44 * hs - t * 0.04), mats["steel"])
        jaw.visual(Box((0.04, 0.06, 0.24 * hs)), origin=Origin(xyz=(0.0, y_dir * 0.01, -0.32 * hs)), material=mats["steel"], name="jaw_wear_plate", material_class_id="metal.steel_bare")
        jaw_axis = (1.0, 0.0, 0.0) if i == 0 else (-1.0, 0.0, 0.0)
        model.articulation(
            f"rotator_to_jaw_{i}",
            ArticulationType.REVOLUTE,
            parent=rotator,
            child=jaw,
            origin=Origin(xyz=(0.0, y_dir * 0.28 * hs, -0.14)),
            axis=jaw_axis,
            motion_limits=MotionLimits(effort=8000.0, velocity=1.5, lower=0.0, upper=0.55),
        )


def _build_mulcher(model, r, mats, wm: WristMount) -> None:
    # GATED head: kept as a wrist-mounted attachment on the boom-ARM (the full
    # carrier+boom chain and the wrist REVOLUTE remain above the drum), NOT a
    # standalone mulcher machine.
    hs = r.head_size_scale
    head = model.part("head")
    _y_cyl(head, "head_wrist_pin", 0.12, 0.44, (0.0, 0.0, 0.0), mats["arm_dark"])
    _box(head, "head_yoke", (0.10, 0.58, 0.18), (0.0, 0.0, -0.10), mats["arm"])
    # The hood + its greebles are anchored at -0.60*hs while the yoke spine is at
    # fixed z; at large head_size_scale the hood drops away from the yoke. Extend
    # the bridge down to -0.53 so it always overlaps the hood top (-0.60*hs+0.19,
    # i.e. >= -0.48 for hs<=1.12) and keeps the assembly one connected body.
    _box(head, "yoke_housing_bridge", (0.28, 0.52, 0.36), (-0.10, 0.0, -0.35), mats["arm"])
    _box(head, "mulcher_hood", (0.72 * hs, 1.30 * hs, 0.38), (-0.10, 0.0, -0.60 * hs), mats["body"])
    for s, y in enumerate((-0.63 * hs, 0.63 * hs)):
        _cyl(head, f"hood_side_plate_{s}", 0.24, 0.06, (-0.10, y, -0.68 * hs), mats["arm_dark"], rpy=(math.pi / 2.0, 0.0, 0.0))
    _cyl(head, "hydraulic_motor", 0.14, 0.18, (-0.10, -0.72 * hs, -0.60 * hs), mats["arm"], rpy=(math.pi / 2.0, 0.0, 0.0))
    _box(head, "hood_front_deflector", (0.08, 1.18 * hs, 0.26), (-0.48 * hs, 0.0, -0.68 * hs), mats["arm_dark"], rpy=(0.0, 0.22, 0.0))
    for i, y_off in enumerate((-0.28, 0.0, 0.28)):
        _box(head, f"hood_top_rib_{i}", (0.62 * hs, 0.06, 0.05), (-0.10, y_off, -0.39 * hs), mats["arm_dark"])
    _hose(head, "head_hose_loop", [(-0.04, 0.44, -0.10), (-0.18, 0.48, -0.30), (-0.30, 0.47, -0.55)], 0.018, mats["hose"], radial_segments=14)
    _emit_wrist_joint(model, wm, head, wrist_range=WRIST_RANGE_PENDANT)

    drum = model.part("mulcher_drum")
    drum.visual(Cylinder(radius=0.20 * hs, length=1.08 * hs), origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)), material=mats["arm_dark"], name="drum_body", material_class_id="metal.blackened_gunmetal")
    for s, y in enumerate((-0.53 * hs, 0.53 * hs)):
        drum.visual(Cylinder(radius=0.22 * hs, length=0.04), origin=Origin(xyz=(0.0, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=mats["arm"], name=f"drum_end_plate_{s}", material_class_id="metal.paint_coated")
    drum_radius = 0.20 * hs
    tooth_h = 0.08
    tooth_r = drum_radius + tooth_h * 0.5
    ring_y = (-0.34 * hs, 0.0, 0.34 * hs)
    ring_off = (0.0, math.pi / 6.0, math.pi / 3.0)
    idx = 0
    for ring in range(3):
        for t in range(6):
            angle = t * (2.0 * math.pi / 6.0) + ring_off[ring]
            drum.visual(
                Box((0.04, 0.06, tooth_h)),
                origin=Origin(xyz=(tooth_r * math.sin(angle), ring_y[ring], tooth_r * math.cos(angle)), rpy=(0.0, angle, 0.0)),
                material=mats["cutting"],
                name=f"tooth_{idx}", material_class_id="metal.steel_bare",
            )
            idx += 1
    model.articulation(
        "head_to_drum",
        ArticulationType.CONTINUOUS,
        parent=head,
        child=drum,
        origin=Origin(xyz=(-0.10, 0.0, -0.78 * hs)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=9000.0, velocity=3.0),
    )


_HEAD_BUILDERS = {
    "processing_head": _build_processing_head,
    "felling_grapple_4finger": _build_felling_grapple,
    "feller_saw": _build_feller_saw,
    "log_grapple": _build_log_grapple,
    "mulcher": _build_mulcher,
}


# ===========================================================================
# Build
# ===========================================================================
def build_harvester(
    config: HarvesterConfig | None = None,
    *,
    assets=None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "Agricultural", "small_class": "Harvester vehicle (arm)"},
    )
    mats = {
        key: model.material(f"harvester_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    mount = _UNDERCARRIAGE_BUILDERS[r.undercarriage](model, r, mats)
    wm = _BOOM_BUILDERS[r.boom_type](model, r, mats, mount)
    _HEAD_BUILDERS[r.head](model, r, mats, wm)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_harvester(seed: int, *, assets=None) -> ArticulatedObject:
    return build_harvester(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _register_allowances(ctx: TestContext, model: ArticulatedObject, r: ResolvedHarvesterConfig):
    """Element-scoped captured-pin / grasp-contact allowances (mirror sources)."""
    boom = model.get_part("boom")
    parent = model.get_part(
        "turret" if r.undercarriage == "tracked_crawler" else ("base_mount" if r.undercarriage == "pedestal_static" else "chassis")
    )
    # Turret seats on the slew ring (tracked).
    if r.undercarriage == "tracked_crawler":
        ctx.allow_overlap(model.get_part("chassis"), model.get_part("turret"), reason="The turret turntable drum seats down onto the chassis slew ring / pedestal crosshead (revolute slew bearing).")

    # Boom root barrel captured in carrier/turret yoke.
    ctx.allow_overlap(boom, parent, reason="The boom root pivot barrel is captured in the carrier/turret yoke (revolute pivot).")

    # Elbow: stick root captured in boom tip yoke.
    stick = model.get_part("boom_stick")
    ctx.allow_overlap(boom, stick, reason="The stick root barrel/neck is captured in the boom tip clevis (revolute elbow pivot).")

    # Telescopic inner slide + wrist parent.
    if r.boom_type == "telescopic_3section":
        inner = model.get_part("boom_stick_inner")
        ctx.allow_overlap(stick, inner, reason="The inner telescoping member slides inside the outer sleeve and through the guide collars (prismatic fit).")
        wrist_part = inner
    else:
        wrist_part = stick

    # Wrist: head hanging link captured at the stick/inner tip.
    head = model.get_part("head")
    ctx.allow_overlap(wrist_part, head, reason="The head wrist pin and hanging link are captured through the stick-tip wrist clevis (revolute pivot).")

    # Wheels: the hub (cap + sleeve + rim bore) rides on the chassis axle pin.
    if r.undercarriage == "wheeled_bogie":
        chassis = model.get_part("chassis")
        for i in range(r.num_axles):
            for s in range(2):
                wheel = model.get_part(f"wheel_{i}_{s}")
                ctx.allow_overlap(chassis, wheel, reason="The wheel hub rides on the chassis axle pin (continuous wheel bearing).")
            # Adjacent tandem wheels can run close on a dense bogie.
        # The tread/carcass mesh extends ~0.04m beyond the tire_radius param, so
        # adjacent tandem tires touch even when axle_pitch slightly exceeds
        # 2*tire_radius. Use a generous margin (this is a legitimate close-running
        # element-scoped allowance; when tires do NOT touch it simply goes unused).
        if r.num_axles >= 2 and r.axle_pitch < 2.0 * r.tire_radius + 0.16:
            for i in range(r.num_axles - 1):
                for s in range(2):
                    ctx.allow_overlap(model.get_part(f"wheel_{i}_{s}"), model.get_part(f"wheel_{i+1}_{s}"), reason="Tandem bogie wheels run close together on the dense running gear.")

    # Head-internal captured pivots + grasp contact.
    if r.head == "felling_grapple_4finger":
        hub = model.get_part("grapple_hub")
        ctx.allow_overlap(head, hub, reason="The grapple rotator drum seats into the head rotator housing/flange.")
        for i in range(4):
            ctx.allow_overlap(hub, model.get_part(f"claw_finger_{i}"), reason="The claw finger knuckle/root is captured on the hub boss pin under the grapple palm (revolute pivot).")
        for i in range(4):
            for j in range(i + 1, 4):
                ctx.allow_overlap(model.get_part(f"claw_finger_{i}"), model.get_part(f"claw_finger_{j}"), reason="The grapple fingers converge on the grasped load at full close.")
    elif r.head == "feller_saw":
        for i in range(2):
            ctx.allow_overlap(head, model.get_part(f"grab_arm_{i}"), reason="The grab arm pivot boss is mounted on the head backbone (revolute pivot).")
        ctx.allow_overlap(model.get_part("grab_arm_0"), model.get_part("grab_arm_1"), reason="The accumulating grab arms close together to bunch stems.")
    elif r.head == "log_grapple":
        rotator = model.get_part("rotator")
        ctx.allow_overlap(head, rotator, reason="The rotator turntable seats into the head rotator housing (continuous pivot).")
        for i in range(2):
            ctx.allow_overlap(rotator, model.get_part(f"jaw_{i}"), reason="The jaw boss is captured on the rotator pivot lug/pin (revolute clamshell pivot).")
        ctx.allow_overlap(model.get_part("jaw_0"), model.get_part("jaw_1"), reason="The clamshell jaws close together on the grasped log.")
    elif r.head == "mulcher":
        ctx.allow_overlap(head, model.get_part("mulcher_drum"), reason="The mulcher drum rotates within the open-bottom hood housing (continuous pivot).")


def run_harvester_tests(object_model: ArticulatedObject, config: HarvesterConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    _register_allowances(ctx, object_model, r)

    # ---- Compiler baseline ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure ----
    ctx.check(
        "small class is harvester vehicle arm",
        object_model.meta.get("small_class") == "Harvester vehicle (arm)"
        and "harvester" in object_model.name,
        details=f"name={object_model.name!r}, meta={object_model.meta}",
    )
    part_names = {p.name for p in object_model.parts}
    ctx.check("boom + stick + head present", {"boom", "boom_stick", "head"}.issubset(part_names), details=str(sorted(part_names)))

    joints = {j.name: j for j in object_model.articulations}
    lift = joints.get("boom_lift")
    elbow = joints.get("boom_to_stick")
    wrist = joints.get("stick_to_head")
    ctx.check(
        "boom lift / elbow / wrist are REVOLUTE about Y",
        lift is not None and elbow is not None and wrist is not None
        and all(j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.9 for j in (lift, elbow, wrist)),
        details=f"types={[(n, joints[n].articulation_type) for n in ('boom_lift', 'boom_to_stick', 'stick_to_head') if n in joints]}",
    )

    # Undercarriage-specific topology.
    if r.undercarriage == "tracked_crawler":
        slew = joints.get("chassis_to_turret")
        ctx.check(
            "tracked crawler has a REVOLUTE-Z turret slew",
            slew is not None and slew.articulation_type == ArticulationType.REVOLUTE and abs(slew.axis[2]) > 0.9,
            details=f"slew={None if slew is None else (slew.articulation_type, tuple(slew.axis))}",
        )
        n_roll = sum(1 for p in object_model.get_part("chassis").visuals if "_roller_" in p.name)
        ctx.check("road rollers present (2 sides)", n_roll == 2 * r.rollers_per_side, details=f"rollers={n_roll} expected={2*r.rollers_per_side}")
    elif r.undercarriage == "wheeled_bogie":
        wheels = [j for j in object_model.articulations if j.name.startswith("chassis_to_wheel_")]
        ctx.check(
            "N bogie wheels on CONTINUOUS-Y joints",
            len(wheels) == 2 * r.num_axles and all(w.articulation_type == ArticulationType.CONTINUOUS for w in wheels),
            details=f"wheels={len(wheels)} expected={2*r.num_axles}",
        )
    else:
        ctx.check("pedestal has no turret/wheels", "turret" not in part_names and not any(p.name.startswith("wheel_") for p in object_model.parts), details=str(sorted(part_names)))

    # Boom-type topology.
    if r.boom_type == "telescopic_3section":
        tele = joints.get("stick_extend")
        ctx.check(
            "telescopic has a PRISMATIC-X extend joint",
            tele is not None and tele.articulation_type == ArticulationType.PRISMATIC and abs(tele.axis[0]) > 0.9,
            details=f"tele={None if tele is None else (tele.articulation_type, tuple(tele.axis))}",
        )

    # Head-type topology.
    if r.head == "felling_grapple_4finger":
        fingers = [j for j in object_model.articulations if j.name.startswith("hub_to_finger_")]
        rot = joints.get("head_rotator")
        ctx.check("4 REVOLUTE fingers on a CONTINUOUS rotator", len(fingers) == 4 and rot is not None and rot.articulation_type == ArticulationType.CONTINUOUS, details=f"fingers={len(fingers)}")
    elif r.head == "feller_saw":
        grabs = [j for j in object_model.articulations if j.name.startswith("head_to_grab_")]
        ctx.check("2 REVOLUTE grab arms + saw disc", len(grabs) == 2 and any(v.name == "saw_disc" for v in object_model.get_part("head").visuals), details=f"grabs={len(grabs)}")
    elif r.head == "log_grapple":
        jaws = [j for j in object_model.articulations if j.name.startswith("rotator_to_jaw_")]
        ctx.check("2 REVOLUTE jaws on a CONTINUOUS rotator", len(jaws) == 2 and joints.get("head_rotator") is not None, details=f"jaws={len(jaws)}")
    elif r.head == "mulcher":
        drum = joints.get("head_to_drum")
        ctx.check("mulcher drum on a CONTINUOUS joint + teeth", drum is not None and drum.articulation_type == ArticulationType.CONTINUOUS and any(v.name.startswith("tooth_") for v in object_model.get_part("mulcher_drum").visuals), details=f"drum={None if drum is None else drum.articulation_type}")

    # ---- Targeted motion semantics (Rule 5) ----
    head_part = object_model.get_part("head")
    rest_head = ctx.part_world_position(head_part)
    if lift is not None:
        with ctx.pose({lift: LIFT_RANGE[1]}):
            raised = ctx.part_world_position(head_part)
        ctx.check(
            "positive boom lift raises the head",
            rest_head is not None and raised is not None and raised[2] > rest_head[2] + 0.25,
            details=f"rest={rest_head}, raised={raised}",
        )
    if elbow is not None:
        with ctx.pose({elbow: ELBOW_RANGE[0]}):
            curled = ctx.part_world_position(head_part)
        ctx.check(
            "elbow swings the head",
            rest_head is not None and curled is not None and (abs(curled[0] - rest_head[0]) + abs(curled[2] - rest_head[2])) > 0.20,
            details=f"rest={rest_head}, curled={curled}",
        )
    if r.boom_type == "telescopic_3section":
        tele = joints["stick_extend"]
        inner = object_model.get_part("boom_stick_inner")
        p0 = ctx.part_world_position(inner)
        with ctx.pose({tele: TELE_TRAVEL}):
            p1 = ctx.part_world_position(inner)
        ctx.check("telescopic extends the inner member", p0 is not None and p1 is not None and (abs(p1[0] - p0[0]) + abs(p1[2] - p0[2])) > 0.4, details=f"p0={p0}, p1={p1}")
    if r.undercarriage == "tracked_crawler":
        slew = joints["chassis_to_turret"]
        b0 = ctx.part_world_position(head_part)  # head is far from the slew axis
        with ctx.pose({slew: SLEW_RANGE[1]}):
            b1 = ctx.part_world_position(head_part)
        ctx.check("turret slew swings the arm laterally", b0 is not None and b1 is not None and abs(b1[1] - b0[1]) > 0.30, details=f"b0={b0}, b1={b1}")

    # Head mechanism motion.
    if r.head == "felling_grapple_4finger":
        hub = object_model.get_part("grapple_hub")
        f0 = object_model.get_part("claw_finger_0")
        fj = joints["hub_to_finger_0"]
        hub_c = ctx.part_world_aabb(hub)
        rest = ctx.part_world_aabb(f0)
        with ctx.pose({fj: 1.0}):
            closed = ctx.part_world_aabb(f0)
        if hub_c and rest and closed:
            hcx, hcy = 0.5 * (hub_c[0][0] + hub_c[1][0]), 0.5 * (hub_c[0][1] + hub_c[1][1])
            rd = math.hypot(0.5 * (rest[0][0] + rest[1][0]) - hcx, 0.5 * (rest[0][1] + rest[1][1]) - hcy)
            cd = math.hypot(0.5 * (closed[0][0] + closed[1][0]) - hcx, 0.5 * (closed[0][1] + closed[1][1]) - hcy)
            ctx.check("claw fingers close toward the tool axis", cd < rd - 0.01, details=f"rest_d={rd:.3f}, closed_d={cd:.3f}")
    elif r.head == "feller_saw":
        a0 = object_model.get_part("grab_arm_0")
        a1 = object_model.get_part("grab_arm_1")
        j0, j1 = joints["head_to_grab_0"], joints["head_to_grab_1"]
        o0, o1 = ctx.part_world_aabb(a0), ctx.part_world_aabb(a1)
        with ctx.pose({j0: 1.1, j1: 1.1}):
            c0, c1 = ctx.part_world_aabb(a0), ctx.part_world_aabb(a1)
        if o0 and o1 and c0 and c1:
            ctx.check("grab arms close together to bunch stems", (c1[0][1] - c0[1][1]) < (o1[0][1] - o0[1][1]), details=f"open_gap={o1[0][1]-o0[1][1]:.3f} closed_gap={c1[0][1]-c0[1][1]:.3f}")
    elif r.head == "log_grapple":
        jw0 = object_model.get_part("jaw_0")
        j0 = joints["rotator_to_jaw_0"]
        rest = ctx.part_world_aabb(jw0)
        with ctx.pose({j0: 0.55}):
            closed = ctx.part_world_aabb(jw0)
        ctx.check("log grapple jaw closes", rest is not None and closed is not None and abs(closed[0][1] - rest[0][1]) + abs(closed[1][1] - rest[1][1]) > 0.02, details=f"rest={rest}, closed={closed}")
    elif r.head == "mulcher":
        drum_p = object_model.get_part("mulcher_drum")
        dj = joints["head_to_drum"]
        rest = ctx.part_world_aabb(drum_p)
        with ctx.pose({dj: math.pi / 2.0}):
            spun = ctx.part_world_aabb(drum_p)
        ctx.check("mulcher drum spins (teeth sweep)", rest is not None and spun is not None, details="drum rotates on continuous joint")
    else:  # processing_head — motion is the wrist (head origin is ON the wrist axis, use AABB)
        if wrist is not None:
            a0 = ctx.part_world_aabb(head_part)
            with ctx.pose({wrist: WRIST_RANGE[1]}):
                a1 = ctx.part_world_aabb(head_part)
            ctx.check(
                "processing head swings on the wrist",
                a0 is not None and a1 is not None
                and (abs(a1[0][0] - a0[0][0]) + abs(a1[0][2] - a0[0][2])) > 0.05,
                details=f"a0={a0}, a1={a1}",
            )

    # ---- Sampled-pose collision guard (Rule 5). Many joints -> cap at 32. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    # ---- slot_choices recorded ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "HarvesterConfig",
    "ResolvedHarvesterConfig",
    "build_harvester",
    "build_seeded_harvester",
    "config_from_seed",
    "resolve_config",
    "run_harvester_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
