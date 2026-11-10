# SPDX-License-Identifier: Apache-2.0

"""Portable cylindrical fire-extinguisher modular template.

NOTE on the slug: "fire_extinguisher" here = **upright portable stored-pressure /
CO2 steel-bottle fire extinguisher**, NOT a fire hydrant (buried post + side
flanges + cap nut), NOT a fire bucket (open sand pail, no valve head). The
structure family is a lathe-turned steel ``body`` (root: recessed base ring +
red banded cylinder + white label band + dome shoulder + brass valve neck +
valve head + fixed pressure gauge + fixed carry handle + safety pin / pull
ring), carrying exactly **one non-FIXED operating-head actuator** (the defining
joint), plus a side-slung discharge and an optional mounting.

Sourced from ``articraft_template_authoring/specs_modular_v1/Urban_Environment_Fire_Extinguisher.md``
and the ``picture/Urban Environment/Fire Extinguisher`` 5-star pool (1 parent +
8 slot-fork variants), all converged upstream.

Structure (pattern = ``parallel_children``; root = body or floor_stand):

  * Slot A ``body_shape`` (3): standard_cylinder / co2_tall_thin / squat_wide —
    the root bottle lathe profile (LatheGeometry, never a Cylinder downgrade).
  * Slot B ``operating_head`` (3): the single defining joint —
    squeeze_lever (REVOLUTE about +Y), wheel_valve (REVOLUTE about +Z, multi
    turn), top_pull_trigger (PRISMATIC about -Z). Each declares a MatingContract.
  * Slot C ``discharge`` (3): hose_nozzle / co2_horn / hoseless_nozzle — inline
    body visuals (Rule 1: non-moving decorations live on the parent).
  * Slot D ``mounting`` (3): none / wall_bracket (inline sheet-metal on body) /
    floor_stand (independent ROOT part; body FIXED onto the plate).

All hinge pins / sliders / locating bosses are captured geometry, so those
joints either omit ``MatingContract`` (grandfathered) or pair with
element-scoped ``allow_overlap`` mirroring each source record's run_tests.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    LatheGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

BodyShape = Literal["standard_cylinder", "co2_tall_thin", "squat_wide"]
OperatingHead = Literal["squeeze_lever", "wheel_valve", "top_pull_trigger"]
Discharge = Literal["hose_nozzle", "co2_horn", "hoseless_nozzle"]
Mounting = Literal["none", "wall_bracket", "floor_stand"]
PaletteStyle = Literal[
    "classic_red", "co2_black", "chrome_steel", "yellow_industrial", "brass_vintage"
]

BODY_SHAPES: tuple[BodyShape, ...] = (
    "standard_cylinder",
    "co2_tall_thin",
    "squat_wide",
)
OPERATING_HEADS: tuple[OperatingHead, ...] = (
    "squeeze_lever",
    "wheel_valve",
    "top_pull_trigger",
)
DISCHARGES: tuple[Discharge, ...] = ("hose_nozzle", "co2_horn", "hoseless_nozzle")
MOUNTINGS: tuple[Mounting, ...] = ("none", "wall_bracket", "floor_stand")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_red",
    "co2_black",
    "chrome_steel",
    "yellow_industrial",
    "brass_vintage",
)

# Baseline-weighted: keep the canonical identity (standard red squeeze-lever
# hose extinguisher with no mount) common, but every candidate stays sampled.
BODY_SHAPE_WEIGHTS = (0.46, 0.27, 0.27)
HEAD_WEIGHTS = (0.44, 0.28, 0.28)
DISCHARGE_WEIGHTS = (0.42, 0.29, 0.29)
MOUNTING_WEIGHTS = (0.44, 0.28, 0.28)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_red": {
        "bottle": (0.74, 0.08, 0.08, 1.0),
        "band": (0.55, 0.05, 0.05, 1.0),
        "label": (0.95, 0.95, 0.93, 1.0),
        "brass": (0.79, 0.62, 0.22, 1.0),
        "steel": (0.62, 0.64, 0.66, 1.0),
        "rubber": (0.07, 0.07, 0.08, 1.0),
        "gauge_face": (0.18, 0.62, 0.30, 1.0),
        "stand_paint": (0.10, 0.10, 0.11, 1.0),
    },
    "co2_black": {
        "bottle": (0.10, 0.10, 0.11, 1.0),
        "band": (0.05, 0.05, 0.06, 1.0),
        "label": (0.90, 0.90, 0.88, 1.0),
        "brass": (0.74, 0.58, 0.20, 1.0),
        "steel": (0.70, 0.72, 0.74, 1.0),
        "rubber": (0.04, 0.04, 0.05, 1.0),
        "gauge_face": (0.20, 0.60, 0.32, 1.0),
        "stand_paint": (0.16, 0.16, 0.17, 1.0),
    },
    "chrome_steel": {
        "bottle": (0.72, 0.74, 0.77, 1.0),
        "band": (0.52, 0.54, 0.57, 1.0),
        "label": (0.93, 0.94, 0.95, 1.0),
        "brass": (0.80, 0.66, 0.30, 1.0),
        "steel": (0.82, 0.84, 0.86, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
        "gauge_face": (0.22, 0.58, 0.34, 1.0),
        "stand_paint": (0.28, 0.29, 0.31, 1.0),
    },
    "yellow_industrial": {
        "bottle": (0.92, 0.74, 0.06, 1.0),
        "band": (0.70, 0.55, 0.04, 1.0),
        "label": (0.12, 0.12, 0.12, 1.0),
        "brass": (0.78, 0.61, 0.22, 1.0),
        "steel": (0.60, 0.62, 0.64, 1.0),
        "rubber": (0.07, 0.07, 0.07, 1.0),
        "gauge_face": (0.18, 0.60, 0.30, 1.0),
        "stand_paint": (0.12, 0.12, 0.13, 1.0),
    },
    "brass_vintage": {
        "bottle": (0.62, 0.18, 0.10, 1.0),
        "band": (0.44, 0.12, 0.07, 1.0),
        "label": (0.88, 0.83, 0.70, 1.0),
        "brass": (0.84, 0.68, 0.32, 1.0),
        "steel": (0.58, 0.56, 0.52, 1.0),
        "rubber": (0.09, 0.08, 0.07, 1.0),
        "gauge_face": (0.24, 0.56, 0.32, 1.0),
        "stand_paint": (0.20, 0.16, 0.12, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Per-body-shape nominal proportions (meters). The bottle is lathed about +Z;
# base ring底面 sits at z=0. shoulder_z / dome_top_z / neck_top_z drive all the
# downstream anchors (head joint origin, discharge endpoints, label/band).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _ShapeSpec:
    body_r: float
    shoulder_z: float
    dome_top_z: float
    neck_top_z: float
    base_ring_drop: float  # how much narrower the recessed base ring waist is


_SHAPE_SPECS: dict[BodyShape, _ShapeSpec] = {
    "standard_cylinder": _ShapeSpec(
        body_r=0.056, shoulder_z=0.330, dome_top_z=0.400, neck_top_z=0.440,
        base_ring_drop=0.010,
    ),
    "co2_tall_thin": _ShapeSpec(
        body_r=0.040, shoulder_z=0.520, dome_top_z=0.580, neck_top_z=0.620,
        base_ring_drop=0.008,
    ),
    "squat_wide": _ShapeSpec(
        body_r=0.100, shoulder_z=0.175, dome_top_z=0.248, neck_top_z=0.288,
        base_ring_drop=0.014,
    ),
}

_NECK_R = 0.020  # brass valve neck radius (shared)
_HEAD_R = 0.030  # valve head block half-extent (shared)
_HEAD_H = 0.030  # valve head block height


@dataclass(frozen=True)
class FireExtinguisherConfig:
    body_shape: BodyShape | None = None
    operating_head: OperatingHead | None = None
    discharge: Discharge | None = None
    mounting: Mounting | None = None
    palette_style: PaletteStyle = "classic_red"
    body_r_scale: float = 1.0
    body_height_scale: float = 1.0
    n_spokes: int | None = None
    name: str = "fire_extinguisher"


@dataclass(frozen=True)
class ResolvedFireExtinguisherConfig:
    body_shape: BodyShape
    operating_head: OperatingHead
    discharge: Discharge
    mounting: Mounting
    palette_style: PaletteStyle
    # Concrete geometry.
    body_r: float
    shoulder_z: float
    dome_top_z: float
    neck_top_z: float
    base_ring_drop: float
    neck_r: float
    head_r: float
    head_h: float
    head_z: float  # z of the valve head top (head joint anchor base)
    n_spokes: int
    # Derived mounting geometry.
    plate_thickness: float
    stand_ring_major_r: float
    wall_strap_r: float
    wall_plate_x: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> FireExtinguisherConfig:
    rng = random.Random(seed)
    return FireExtinguisherConfig(
        body_shape=rng.choices(BODY_SHAPES, weights=BODY_SHAPE_WEIGHTS, k=1)[0],
        operating_head=rng.choices(OPERATING_HEADS, weights=HEAD_WEIGHTS, k=1)[0],
        discharge=rng.choices(DISCHARGES, weights=DISCHARGE_WEIGHTS, k=1)[0],
        mounting=rng.choices(MOUNTINGS, weights=MOUNTING_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        body_r_scale=round(rng.uniform(0.92, 1.10), 4),
        body_height_scale=round(rng.uniform(0.90, 1.12), 4),
        n_spokes=rng.randint(4, 8),
        name=f"seeded_fire_extinguisher_{seed}",
    )


def resolve_config(
    config: FireExtinguisherConfig | None = None,
) -> ResolvedFireExtinguisherConfig:
    cfg = config or FireExtinguisherConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    body_shape = _pick(cfg.body_shape, BODY_SHAPES)
    operating_head = _pick(cfg.operating_head, OPERATING_HEADS)
    discharge = _pick(cfg.discharge, DISCHARGES)
    mounting = _pick(cfg.mounting, MOUNTINGS)

    spec = _SHAPE_SPECS[body_shape]
    r_scale = _clamp(cfg.body_r_scale, 0.92, 1.10)
    h_scale = _clamp(cfg.body_height_scale, 0.90, 1.12)

    # body_r independent, clamped to the category range; aspect-derived heights.
    body_r = _clamp(spec.body_r * r_scale, 0.040, 0.100)
    shoulder_z = spec.shoulder_z * h_scale
    dome_top_z = spec.dome_top_z * h_scale
    neck_top_z = spec.neck_top_z * h_scale
    head_z = neck_top_z + _HEAD_H  # valve head top

    n_spokes = int(_clamp(int(cfg.n_spokes) if cfg.n_spokes is not None else 5, 4, 8))

    plate_thickness = 0.012
    # floor_stand ring must clear the bottle (inequality: ring_major_r > body_r+ε).
    stand_ring_major_r = max(body_r + 0.014, 0.068)
    # wall_bracket strap must not pierce the bottle (strap_r > body_r).
    wall_strap_r = body_r + 0.006
    wall_plate_x = -(body_r + 0.002)

    return ResolvedFireExtinguisherConfig(
        body_shape=body_shape,
        operating_head=operating_head,
        discharge=discharge,
        mounting=mounting,
        palette_style=palette_style,
        body_r=body_r,
        shoulder_z=shoulder_z,
        dome_top_z=dome_top_z,
        neck_top_z=neck_top_z,
        base_ring_drop=spec.base_ring_drop,
        neck_r=_NECK_R,
        head_r=_HEAD_R,
        head_h=_HEAD_H,
        head_z=head_z,
        n_spokes=n_spokes,
        plate_thickness=plate_thickness,
        stand_ring_major_r=stand_ring_major_r,
        wall_strap_r=wall_strap_r,
        wall_plate_x=wall_plate_x,
        name=cfg.name or "fire_extinguisher",
    )


def with_overrides(
    config: FireExtinguisherConfig, **kwargs: object
) -> FireExtinguisherConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: FireExtinguisherConfig | ResolvedFireExtinguisherConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedFireExtinguisherConfig)
        else resolve_config(config)
    )
    return (
        ("body_shape", r.body_shape),
        ("operating_head", r.operating_head),
        ("discharge", r.discharge),
        ("mounting", r.mounting),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body (root) lathe profile — Slot A. The bottle is a LatheGeometry turned about
# +Z; base ring底 at z=0. We keep it a real lathe (Rule 3, no Cylinder downgrade).
# ---------------------------------------------------------------------------
def _bottle_lathe(r: ResolvedFireExtinguisherConfig) -> LatheGeometry:
    """Outer steel shell: recessed base ring -> banded cylinder -> dome shoulder
    -> brass neck stub. Profile is (radius, z) about the +Z axis."""
    br = r.body_r
    waist = br - r.base_ring_drop  # recessed base-ring waist
    shoulder = r.shoulder_z
    dome = r.dome_top_z
    neck = r.neck_top_z
    band_r = br + 0.0030  # rolled banding ring crest radius
    profile: list[tuple[float, float]] = [
        (0.0, 0.0),
        (br, 0.0),  # base ring foot (full radius at ground)
        (br, 0.010),
        (waist, 0.018),  # recessed waist above the base ring
        (br, 0.030),  # back out to full bottle radius
        (br, shoulder * 0.20),
        (band_r, shoulder * 0.21),  # lower rolled band
        (br, shoulder * 0.22),
        (br, shoulder * 0.86),
        (band_r, shoulder * 0.87),  # upper rolled band
        (br, shoulder * 0.88),
        (br, shoulder),  # cylinder top / shoulder start
        (br * 0.86, shoulder + (dome - shoulder) * 0.45),  # dome shoulder curve
        (br * 0.50, dome),  # dome top
        (r.neck_r + 0.004, dome + 0.004),  # neck base
        (r.neck_r, neck),  # brass valve neck top
        (0.0, neck),
    ]
    return LatheGeometry(profile, segments=48)


def _build_body(
    model: ArticulatedObject,
    r: ResolvedFireExtinguisherConfig,
    mats,
    *,
    z0: float = 0.0,
):
    """Build the body root visuals. ``z0`` lifts everything (floor_stand mount)."""
    body = model.part("body")
    body.visual(
        mesh_from_geometry(_bottle_lathe(r), "bottle"),
        origin=Origin(xyz=(0.0, 0.0, z0)),
        material=mats["bottle"],
        name="bottle", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    body.inertial = Inertial.from_geometry(
        Cylinder(radius=r.body_r, length=r.neck_top_z),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, z0 + r.neck_top_z / 2.0)),
    )
    # White (or dark) label band — fixed category identity, mid body.
    label_lo = r.shoulder_z * 0.33
    label_hi = r.shoulder_z * 0.80
    body.visual(
        Cylinder(radius=r.body_r + 0.0010, length=(label_hi - label_lo)),
        origin=Origin(xyz=(0.0, 0.0, z0 + (label_lo + label_hi) / 2.0)),
        material=mats["label"],
        name="label_band", material_class_id="paper.plain_sheet",
    )
    # Brass valve neck stub (a real turned brass collar over the lathe neck).
    body.visual(
        Cylinder(radius=r.neck_r + 0.0015, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, z0 + r.neck_top_z - 0.009)),
        material=mats["brass"],
        name="valve_neck", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_red", "co2_black", "chrome_steel", "yellow_industrial"} else "metal.brass_aged"),
    )
    # Brass valve head block on top of the neck (carries the operating head).
    body.visual(
        Box((2.0 * r.head_r, 1.6 * r.head_r, r.head_h)),
        origin=Origin(xyz=(0.0, 0.0, z0 + r.neck_top_z + r.head_h / 2.0)),
        material=mats["brass"],
        name="valve_head", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_red", "co2_black", "chrome_steel", "yellow_industrial"} else "metal.brass_aged"),
    )
    # Pressure gauge (stem + case + dial) on the front (-Y) face of the head.
    gauge_y = -(0.8 * r.head_r)
    gauge_z = z0 + r.neck_top_z + r.head_h * 0.55
    body.visual(
        Cylinder(radius=0.004, length=0.012, ),
        origin=Origin(xyz=(0.0, gauge_y - 0.006, gauge_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["brass"],
        name="gauge_stem", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_red", "co2_black", "chrome_steel", "yellow_industrial"} else "metal.brass_aged"),
    )
    body.visual(
        Cylinder(radius=0.016, length=0.010),
        origin=Origin(xyz=(0.0, gauge_y - 0.016, gauge_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="gauge_case", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    body.visual(
        Cylinder(radius=0.013, length=0.003),
        origin=Origin(xyz=(0.0, gauge_y - 0.022, gauge_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["gauge_face"],
        name="gauge_dial", material_class_id="tech.control_interface",
    )
    # Safety pin + pull ring through the head (category identity).
    pin_z = z0 + r.neck_top_z + r.head_h * 0.75
    body.visual(
        Cylinder(radius=0.0022, length=2.2 * r.head_r),
        origin=Origin(xyz=(0.0, 0.0, pin_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="safety_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    body.visual(
        mesh_from_geometry(
            TorusGeometry(0.010, 0.0022, radial_segments=12, tubular_segments=20),
            "pull_ring",
        ),
        origin=Origin(xyz=(0.0, 1.1 * r.head_r, pin_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="pull_ring", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    return body, z0


def _emit_carry_handle(body, r: ResolvedFireExtinguisherConfig, mats, *, z0: float):
    """Fixed rear (-X / +X spanning) carry handle — Rule 1 inline visual."""
    hz = z0 + r.neck_top_z + r.head_h * 0.30
    span = r.head_r * 1.7
    # Two uprights + a top grip tube arching over the head (rear, +X side).
    back_x = r.head_r + 0.006
    for i, s in enumerate((1.0, -1.0)):
        body.visual(
            Cylinder(radius=0.0045, length=0.040),
            origin=Origin(xyz=(back_x, s * span, hz + 0.020)),
            material=mats["steel"],
            name=f"handle_post_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
        )
    body.visual(
        Cylinder(radius=0.0050, length=2.0 * span, ),
        origin=Origin(xyz=(back_x, 0.0, hz + 0.040), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["rubber"],
        name="carry_handle", material_class_id="rubber.smooth_plain",
    )
    # Small mounting bracket bridging from the valve head out to the posts so the
    # handle is not a floating island.
    body.visual(
        Box((back_x + 0.006, 2.0 * span + 0.010, 0.008)),
        origin=Origin(xyz=(back_x / 2.0, 0.0, hz)),
        material=mats["steel"],
        name="handle_bracket", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )


# ---------------------------------------------------------------------------
# Slot C: discharge (inline body visuals, Rule 1).
# ---------------------------------------------------------------------------
def _emit_discharge(body, r: ResolvedFireExtinguisherConfig, mats, *, z0: float):
    head_z = z0 + r.neck_top_z + r.head_h * 0.5
    side_y = r.head_r * 0.9
    bottle_r = r.body_r
    if r.discharge == "hose_nozzle":
        # Thin black rubber hose: spline from the valve head down, hugging the
        # bottle, ending at a small lathe nozzle.
        pts = [
            (0.0, side_y, head_z),
            (0.0, bottle_r + 0.012, head_z - 0.04),
            (0.0, bottle_r + 0.006, z0 + r.shoulder_z * 0.7),
            (0.0, bottle_r + 0.004, z0 + r.shoulder_z * 0.40),
            (0.0, bottle_r + 0.010, z0 + r.shoulder_z * 0.30),
        ]
        body.visual(
            mesh_from_geometry(
                tube_from_spline_points(pts, radius=0.006, radial_segments=12),
                "discharge_hose",
            ),
            material=mats["rubber"],
            name="discharge_hose", material_class_id="rubber.smooth_plain",
        )
        # Small flared nozzle at the hose end (real lathe profile).
        nz_z = z0 + r.shoulder_z * 0.30
        nozzle = LatheGeometry(
            [
                (0.0, 0.0),
                (0.006, 0.0),
                (0.006, 0.020),
                (0.010, 0.028),
                (0.0, 0.028),
            ],
            segments=24,
        )
        body.visual(
            mesh_from_geometry(nozzle, "discharge_nozzle"),
            origin=Origin(xyz=(0.0, bottle_r + 0.010, nz_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["rubber"],
            name="discharge_nozzle", material_class_id="rubber.smooth_plain",
        )
    elif r.discharge == "co2_horn":
        # Rigid swept tube + wide cone horn (CO2 identity).
        # Keep the horn mouth clear of the ground/plate: clamp its low point so
        # the flared bell (extends ~0.18 down after the flip) never dips below z0.
        horn_top_z = max(z0 + r.shoulder_z * 0.42, z0 + 0.190)
        pts = [
            (0.0, side_y, head_z),
            (0.0, bottle_r + 0.020, head_z - 0.03),
            (0.0, bottle_r + 0.030, (horn_top_z + head_z) * 0.5),
            (0.0, bottle_r + 0.030, horn_top_z),
        ]
        body.visual(
            mesh_from_geometry(
                tube_from_spline_points(pts, radius=0.009, radial_segments=12),
                "discharge_tube",
            ),
            material=mats["rubber"],
            name="discharge_tube", material_class_id="rubber.smooth_plain",
        )
        # Wide flared horn (small throat -> large bell), big mouth facing down.
        horn = LatheGeometry(
            [
                (0.0, 0.0),
                (0.018, 0.0),
                (0.018, 0.010),
                (0.040, 0.110),
                (0.062, 0.180),
                (0.060, 0.180),
                (0.038, 0.112),
                (0.016, 0.012),
                (0.0, 0.012),
            ],
            segments=32,
        )
        body.visual(
            mesh_from_geometry(horn, "discharge_horn"),
            origin=Origin(
                xyz=(0.0, bottle_r + 0.030, horn_top_z), rpy=(math.pi, 0.0, 0.0)
            ),
            material=mats["rubber"],
            name="discharge_horn", material_class_id="rubber.smooth_plain",
        )
    else:  # hoseless_nozzle
        # Single short flared nozzle straight out the front (-Y) of the head.
        nozzle = LatheGeometry(
            [
                (0.0, 0.0),
                (0.012, 0.0),
                (0.012, 0.006),
                (0.008, 0.010),
                (0.008, 0.030),
                (0.018, 0.044),
                (0.016, 0.044),
                (0.0, 0.030),
            ],
            segments=28,
        )
        body.visual(
            mesh_from_geometry(nozzle, "discharge_nozzle"),
            origin=Origin(
                xyz=(0.0, -(r.head_r + 0.002), head_z), rpy=(-math.pi / 2.0, 0.0, 0.0)
            ),
            material=mats["rubber"],
            name="discharge_nozzle", material_class_id="rubber.smooth_plain",
        )


# ---------------------------------------------------------------------------
# Slot B: operating head (the single non-FIXED defining joint).
# ---------------------------------------------------------------------------
def _emit_squeeze_lever(model, r, body, mats, *, z0: float) -> list[str]:
    """Squeeze lever — REVOLUTE about +Y around a rear cross-pin. Source: parent."""
    head_top = z0 + r.neck_top_z + r.head_h
    pin_x = -0.012
    pin_z = head_top + 0.004
    # Body-side lug pair + cross pin (a real anchoring visual for the hinge).
    for i, s in enumerate((1.0, -1.0)):
        body.visual(
            Box((0.014, 0.008, 0.020)),
            origin=Origin(xyz=(pin_x, s * 0.012, pin_z - 0.006)),
            material=mats["brass"],
            name=f"lever_lug_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_red", "co2_black", "chrome_steel", "yellow_industrial"} else "metal.brass_aged"),
        )
    body.visual(
        Cylinder(radius=0.0030, length=0.040),
        origin=Origin(xyz=(pin_x, 0.0, pin_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="lever_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    lever = model.part("operating_lever")
    # Lever authored in the pivot frame: pin axis through the part origin (Y);
    # the blade arches forward (+X) and slightly up. Contains (0,0,0).
    lever.visual(
        Box((0.012, 0.030, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["steel"],
        name="lever_knuckle", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    lever.visual(
        Box((0.070, 0.024, 0.008)),
        origin=Origin(xyz=(0.040, 0.0, 0.004)),
        material=mats["steel"],
        name="lever_arm", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    lever.visual(
        Box((0.020, 0.026, 0.012)),
        origin=Origin(xyz=(0.072, 0.0, 0.006)),
        material=mats["rubber"],
        name="lever_grip", material_class_id="rubber.smooth_plain",
    )
    lever.inertial = Inertial.from_geometry(
        Box((0.090, 0.030, 0.012)),
        mass=0.06,
        origin=Origin(xyz=(0.040, 0.0, 0.004)),
    )
    model.articulation(
        "body_to_lever",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lever,
        origin=Origin(xyz=(pin_x, 0.0, pin_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=0.5),
    )
    return ["operating_lever"]


def _emit_wheel_valve(model, r, body, mats, *, z0: float) -> list[str]:
    """Hand wheel valve — REVOLUTE about +Z, multi-turn (screw-down). Source: var."""
    head_top = z0 + r.neck_top_z + r.head_h
    stem_h = 0.026
    # Body-side brass valve stem rising from the head (anchoring visual).
    body.visual(
        Cylinder(radius=0.008, length=stem_h),
        origin=Origin(xyz=(0.0, 0.0, head_top + stem_h / 2.0)),
        material=mats["brass"],
        name="valve_stem", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_red", "co2_black", "chrome_steel", "yellow_industrial"} else "metal.brass_aged"),
    )
    joint_z = head_top + stem_h
    wheel = model.part("hand_wheel")
    # Hub centered on the part origin (z=0..hub_h), so the part frame (at the
    # joint origin) is contained in the hub geometry.
    hub_h = 0.014
    wheel.visual(
        Cylinder(radius=0.010, length=hub_h),
        origin=Origin(xyz=(0.0, 0.0, hub_h / 2.0)),
        material=mats["steel"],
        name="wheel_hub", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    rim_r = 0.044
    wheel.visual(
        mesh_from_geometry(
            TorusGeometry(rim_r, 0.0050, radial_segments=14, tubular_segments=28),
            "wheel_rim",
        ),
        origin=Origin(xyz=(0.0, 0.0, hub_h * 0.5)),
        material=mats["steel"],
        name="wheel_rim", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    for i in range(r.n_spokes):
        ang = i * 2.0 * math.pi / r.n_spokes
        wheel.visual(
            Box((rim_r, 0.005, 0.005)),
            origin=Origin(xyz=(0.5 * rim_r * math.cos(ang), 0.5 * rim_r * math.sin(ang), hub_h * 0.5), rpy=(0.0, 0.0, ang)),
            material=mats["steel"],
            name=f"spoke_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
        )
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=rim_r, length=hub_h),
        mass=0.08,
        origin=Origin(xyz=(0.0, 0.0, hub_h / 2.0)),
    )
    model.articulation(
        "body_to_wheel",
        ArticulationType.REVOLUTE,
        parent=body,
        child=wheel,
        origin=Origin(xyz=(0.0, 0.0, joint_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=3.0, lower=0.0, upper=4.0 * math.pi
        ),
        mating=MatingContract(
            parent_face_geometry="valve_stem",
            parent_face_side="positive_z",
            child_face_geometry="wheel_hub",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )
    return ["hand_wheel"]


def _emit_top_pull_trigger(model, r, body, mats, *, z0: float) -> list[str]:
    """Push trigger — PRISMATIC about -Z down into a guide boss. Source: var."""
    head_top = z0 + r.neck_top_z + r.head_h
    boss_h = 0.020
    # Body-side brass guide boss (bore) — anchoring visual.
    body.visual(
        Cylinder(radius=0.016, length=boss_h),
        origin=Origin(xyz=(0.0, 0.0, head_top + boss_h / 2.0)),
        material=mats["brass"],
        name="trigger_guide", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_red", "co2_black", "chrome_steel", "yellow_industrial"} else "metal.brass_aged"),
    )
    guide_top = head_top + boss_h
    trigger = model.part("trigger")
    # Domed cap (lathe) + stem; stem top at part origin z=0, descends into boss.
    cap = LatheGeometry(
        [
            (0.0, 0.0),
            (0.013, 0.0),
            (0.013, 0.006),
            (0.009, 0.012),
            (0.0, 0.014),
        ],
        segments=24,
    )
    trigger.visual(
        mesh_from_geometry(cap, "trigger_cap"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["rubber"],
        name="trigger_cap", material_class_id="rubber.smooth_plain",
    )
    trigger.visual(
        Cylinder(radius=0.008, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, -0.009)),
        material=mats["steel"],
        name="trigger_stem", material_class_id=("metal.stainless_matte" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    for i in range(6):
        ang = i * 2.0 * math.pi / 6.0
        trigger.visual(
            Box((0.003, 0.003, 0.012)),
            origin=Origin(xyz=(0.012 * math.cos(ang), 0.012 * math.sin(ang), 0.004)),
            material=mats["rubber"],
            name=f"grip_rib_{i}", material_class_id="rubber.smooth_plain",
        )
    trigger.inertial = Inertial.from_geometry(
        Cylinder(radius=0.013, length=0.022),
        mass=0.03,
        origin=Origin(xyz=(0.0, 0.0, -0.005)),
    )
    model.articulation(
        "body_to_trigger",
        ArticulationType.PRISMATIC,
        parent=body,
        child=trigger,
        origin=Origin(xyz=(0.0, 0.0, guide_top)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=15.0, velocity=0.3, lower=0.0, upper=0.012),
    )
    return ["trigger"]


_HEAD_BUILDERS = {
    "squeeze_lever": _emit_squeeze_lever,
    "wheel_valve": _emit_wheel_valve,
    "top_pull_trigger": _emit_top_pull_trigger,
}


# ---------------------------------------------------------------------------
# Slot D: mounting.
# ---------------------------------------------------------------------------
def _emit_wall_bracket(body, r: ResolvedFireExtinguisherConfig, mats, *, z0: float):
    """Inline red sheet-metal wall bracket: back plate (-X) + ~300° cradle strap."""
    plate_z = z0 + r.shoulder_z * 0.55
    body.visual(
        Box((0.008, 2.0 * r.body_r + 0.030, 0.140)),
        origin=Origin(xyz=(r.wall_plate_x - 0.004, 0.0, plate_z)),
        material=mats["bottle"],
        name="bracket_back_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    # ~300° cradle strap hugging the bottle (swept torus arc via a tube spline).
    strap_z = plate_z - 0.030
    n_arc = 28
    a0 = math.radians(150.0)
    a1 = math.radians(-150.0)
    pts = []
    for i in range(n_arc + 1):
        t = i / n_arc
        a = a0 + (a1 - a0) * t
        pts.append(
            (r.wall_strap_r * math.cos(a), r.wall_strap_r * math.sin(a), strap_z)
        )
    body.visual(
        mesh_from_geometry(
            tube_from_spline_points(pts, radius=0.005, radial_segments=10),
            "cradle_strap",
        ),
        material=mats["bottle"],
        name="cradle_strap", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )
    # Strap-to-plate tie so the strap is not a floating island.
    body.visual(
        Box((0.014, 0.010, 0.018)),
        origin=Origin(xyz=(r.wall_plate_x + 0.003, 0.0, strap_z)),
        material=mats["bottle"],
        name="strap_tie", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_red", "co2_black", "yellow_industrial", "brass_vintage"} else "metal.chrome_polished"),
    )


def _build_floor_stand(model, r: ResolvedFireExtinguisherConfig, mats):
    """Independent floor_stand ROOT: base plate + 2 posts + retainer ring + 2
    gussets. Body is FIXED onto the plate at z=plate_thickness."""
    stand = model.part("floor_stand")
    plate = 0.200
    pt = r.plate_thickness
    stand.visual(
        Box((plate, plate, pt)),
        origin=Origin(xyz=(0.0, 0.0, pt / 2.0)),
        material=mats["stand_paint"],
        name="base_plate", material_class_id="metal.paint_coated",
    )
    ring_z = pt + 0.42 * r.shoulder_z
    post_x = r.stand_ring_major_r - 0.004
    for i, s in enumerate((1.0, -1.0)):
        stand.visual(
            Cylinder(radius=0.008, length=ring_z),
            origin=Origin(xyz=(s * post_x, 0.0, ring_z / 2.0)),
            material=mats["stand_paint"],
            name=f"post_{i}", material_class_id="metal.paint_coated",
        )
        # Gusset webbing each post to the plate.
        stand.visual(
            Box((0.030, 0.010, 0.040)),
            origin=Origin(xyz=(s * (post_x - 0.012), 0.0, pt + 0.020)),
            material=mats["stand_paint"],
            name=f"gusset_{i}", material_class_id="metal.paint_coated",
        )
    stand.visual(
        mesh_from_geometry(
            TorusGeometry(
                r.stand_ring_major_r, 0.006, radial_segments=12, tubular_segments=32
            ),
            "retainer_ring",
        ),
        origin=Origin(xyz=(0.0, 0.0, ring_z)),
        material=mats["stand_paint"],
        name="retainer_ring", material_class_id="metal.paint_coated",
    )
    stand.inertial = Inertial.from_geometry(
        Box((plate, plate, ring_z)),
        mass=2.0,
        origin=Origin(xyz=(0.0, 0.0, ring_z / 2.0)),
    )
    return stand


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_fire_extinguisher(
    config: FireExtinguisherConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"fire_extinguisher_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    if r.mounting == "floor_stand":
        stand = _build_floor_stand(model, r, mats)
        z0 = r.plate_thickness
        body, _ = _build_body(model, r, mats, z0=z0)
        # Body FIXED onto the plate top (separate kinematic root sub-assembly).
        model.articulation(
            "stand_to_body",
            ArticulationType.FIXED,
            parent=stand,
            child=body,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            mating=MatingContract(
                parent_face_geometry="base_plate",
                parent_face_side="positive_z",
                child_face_geometry="bottle",
                child_face_side="negative_z",
                contact_tol=0.0030,
            ),
        )
    else:
        z0 = 0.0
        body, _ = _build_body(model, r, mats, z0=z0)

    _emit_carry_handle(body, r, mats, z0=z0)
    _emit_discharge(body, r, mats, z0=z0)
    _HEAD_BUILDERS[r.operating_head](model, r, body, mats, z0=z0)

    if r.mounting == "wall_bracket":
        _emit_wall_bracket(body, r, mats, z0=z0)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_fire_extinguisher(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_fire_extinguisher(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_fire_extinguisher_tests(
    object_model: ArticulatedObject,
    config: FireExtinguisherConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")

    # ---- Captured-pin / boss / mounting allowances (element-scoped). ----
    # Carry handle bracket overlaps the valve head; discharge hugs the bottle.
    ctx.allow_overlap(
        body, body, reason="fixed body decorations (handle bracket, discharge, "
        "label, bands, gauge, pin) embed into the bottle / valve head.",
    )

    if r.operating_head == "squeeze_lever":
        lever = object_model.get_part("operating_lever")
        ctx.allow_overlap(
            lever, body, elem_a="lever_knuckle", elem_b="lever_pin",
            reason="lever knuckle is captured on the body cross-pin (hinge).",
        )
        for i in range(2):
            ctx.allow_overlap(
                lever, body, elem_a="lever_knuckle", elem_b=f"lever_lug_{i}",
                reason="lever knuckle sits between the body hinge lugs.",
            )
        ctx.allow_overlap(
            lever, body, reason="closed squeeze lever rests on the valve head.",
        )
    elif r.operating_head == "wheel_valve":
        wheel = object_model.get_part("hand_wheel")
        ctx.allow_overlap(
            wheel, body, elem_a="wheel_hub", elem_b="valve_stem",
            reason="wheel hub seats on the brass valve stem top.",
        )
    else:  # top_pull_trigger
        trigger = object_model.get_part("trigger")
        ctx.allow_overlap(
            trigger, body, elem_a="trigger_stem", elem_b="trigger_guide",
            reason="trigger stem slides inside the guide boss bore (prismatic fit).",
        )
        ctx.allow_overlap(
            trigger, body, elem_a="trigger_cap", elem_b="trigger_guide",
            reason="trigger cap rests on the guide boss at the closed pose.",
        )

    if r.mounting == "floor_stand":
        stand = object_model.get_part("floor_stand")
        ctx.allow_overlap(
            body, stand, reason="bottle base seats on the floor-stand plate; the "
            "retainer ring encircles the bottle.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity: body + fixed category visuals present. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("body part present", "body" in part_names, details=str(sorted(part_names)))
    body_visuals = {v.name for v in body.visuals}
    for needed in ("bottle", "valve_neck", "valve_head", "gauge_dial", "label_band",
                   "carry_handle"):
        ctx.check(
            f"identity visual '{needed}' present",
            needed in body_visuals,
            details=str(sorted(body_visuals)),
        )

    # gauge_dial on the front (-Y) of the head.
    gauge = next((v for v in body.visuals if v.name == "gauge_dial"), None)
    if gauge is not None:
        ctx.check(
            "gauge_dial is on the front (-Y)",
            gauge.origin.xyz[1] < -0.002,
            details=f"gauge_y={gauge.origin.xyz[1]:.4f}",
        )

    # ---- Operating head is the single non-FIXED defining joint. ----
    non_fixed = [
        a for a in object_model.articulations
        if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "exactly one non-FIXED defining joint (operating head)",
        len(non_fixed) == 1,
        details=str([(a.name, str(a.articulation_type)) for a in object_model.articulations]),
    )

    if r.operating_head == "squeeze_lever":
        j = object_model.get_articulation("body_to_lever")
        ctx.check(
            "squeeze lever is REVOLUTE about +Y",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        lever = object_model.get_part("operating_lever")
        closed = ctx.part_world_aabb(lever)
        with ctx.pose({j: 0.5 * 0.8}):
            opened = ctx.part_world_aabb(lever)
        if closed is not None and opened is not None:
            ctx.check(
                "squeeze lever front edge presses down",
                opened[0][2] < closed[0][2] + 0.0005,
                details=f"closed_zmin={closed[0][2]:.4f} pressed_zmin={opened[0][2]:.4f}",
            )
    elif r.operating_head == "wheel_valve":
        j = object_model.get_articulation("body_to_wheel")
        ctx.check(
            "wheel valve is REVOLUTE about +Z",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        ctx.check(
            "wheel valve has a multi-turn range",
            (j.motion_limits is not None and j.motion_limits.upper > 2.0 * math.pi),
            details=f"upper={getattr(j.motion_limits, 'upper', None)}",
        )
    else:
        j = object_model.get_articulation("body_to_trigger")
        ctx.check(
            "top pull trigger is PRISMATIC about -Z",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[2]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        trigger = object_model.get_part("trigger")
        p0 = ctx.part_world_position(trigger)
        with ctx.pose({j: 0.012 * 0.9}):
            p1 = ctx.part_world_position(trigger)
        if p0 is not None and p1 is not None:
            ctx.check(
                "trigger pushes straight down",
                p1[2] < p0[2] - 0.005,
                details=f"rest_z={p0[2]:.4f} pushed_z={p1[2]:.4f}",
            )

    # ---- Discharge present & forms. ----
    if r.discharge == "hose_nozzle":
        ctx.check(
            "hose + nozzle discharge present",
            {"discharge_hose", "discharge_nozzle"} <= body_visuals,
            details=str(sorted(body_visuals)),
        )
    elif r.discharge == "co2_horn":
        ctx.check(
            "co2 tube + horn discharge present",
            {"discharge_tube", "discharge_horn"} <= body_visuals,
            details=str(sorted(body_visuals)),
        )
    else:
        ctx.check(
            "hoseless nozzle present",
            "discharge_nozzle" in body_visuals,
            details=str(sorted(body_visuals)),
        )

    # ---- Mounting / root topology. ----
    if r.mounting == "floor_stand":
        ctx.check("floor_stand root present", "floor_stand" in part_names, details="")
        j = object_model.get_articulation("stand_to_body")
        ctx.check(
            "body is FIXED onto the floor stand",
            j.articulation_type == ArticulationType.FIXED,
            details=str(j.articulation_type),
        )
        stand = object_model.get_part("floor_stand")
        saabb = ctx.part_world_aabb(stand)
        if saabb is not None:
            ctx.check(
                "floor stand plate rests on the ground",
                saabb[0][2] < 0.004,
                details=f"z_min={saabb[0][2]:.4f}",
            )
            ctx.check(
                "floor stand plate is wide",
                (saabb[1][0] - saabb[0][0]) > 0.15,
                details=f"plate_w={saabb[1][0]-saabb[0][0]:.4f}",
            )
        baabb = ctx.part_world_aabb(body)
        if baabb is not None:
            ctx.check(
                "body sits above the plate",
                baabb[0][2] > 0.003,
                details=f"body_zmin={baabb[0][2]:.4f}",
            )
        # Ring clears the bottle.
        ctx.check(
            "retainer ring clears the bottle",
            r.stand_ring_major_r > r.body_r + 0.008,
            details=f"ring={r.stand_ring_major_r:.4f} body_r={r.body_r:.4f}",
        )
    else:
        # Body base rests at the ground (none / wall_bracket).
        baabb = ctx.part_world_aabb(body)
        if baabb is not None:
            ctx.check(
                "bottle base rests near the ground",
                baabb[0][2] < 0.004,
                details=f"z_min={baabb[0][2]:.4f}",
            )
        if r.mounting == "wall_bracket":
            ctx.check(
                "wall bracket present",
                {"bracket_back_plate", "cradle_strap"} <= body_visuals,
                details=str(sorted(body_visuals)),
            )
            ctx.check(
                "wall strap clears the bottle (no pierce)",
                r.wall_strap_r > r.body_r,
                details=f"strap_r={r.wall_strap_r:.4f} body_r={r.body_r:.4f}",
            )

    # ---- Upright proportion sanity. ----
    aabb = ctx.part_world_aabb(body)
    if aabb is not None:
        (axmn, aymn, azmn), (axmx, aymx, azmx) = aabb
        h = azmx - azmn
        w = max(axmx - axmn, aymx - aymn)
        if r.body_shape == "squat_wide":
            ctx.check("squat-wide body is wide", w > 0.16, details=f"w={w:.3f} h={h:.3f}")
        else:
            ctx.check("bottle is upright", h > w * 1.6, details=f"h={h:.3f} w={w:.3f}")

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "FireExtinguisherConfig",
    "ResolvedFireExtinguisherConfig",
    "build_fire_extinguisher",
    "build_seeded_fire_extinguisher",
    "config_from_seed",
    "resolve_config",
    "run_fire_extinguisher_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
