# SPDX-License-Identifier: Apache-2.0

"""Air blower — modular procedural template (pictureX / 0611 / Air_blower).

A device that moves air via a driven impeller OR a squeezed bellows, with an
outlet/nozzle. Two structurally different form FAMILIES, gated at config-resolve
time by a compatibility matrix (illegal body×motion combos are downgraded to the
family default, never built and failed):

  BELLOWS family
    - bellows_boards : two hinged teardrop boards + N accordion folds + brass
                       nozzle + one-way flap valve + board handle (root
                       ``lower_board``).  Motion: board_squeeze REVOLUTE(+Y) or
                       foot_pump PRISMATIC(-Z), folds mimic the driver.
    - rubber_bulb    : single ovoid rubber bulb + prismatic squeeze wall + brass
                       nozzle + flap (root ``bulb_body``).
  BLOWER family (root ``housing``; parallel-children drivetrain)
    - volute_drum / axial_barrel / canister_tank / spherical_pod : the P2
      centrifugal drivetrain (crank CONTINUOUS +Y -> mimic shaft + mimic
      squirrel-cage/axial fan wheel) + adjustable_tube|flex_duct outlet
      (REVOLUTE +X twist) + spoked_grille|filter_cap intake + top|pistol grip.

Every seed has >= 1 real non-FIXED joint driving the air-mover (impeller
CONTINUOUS or bellows/bulb PRISMATIC/REVOLUTE) + an outlet + an intake.

Source records (5-star), adapted per AUTHORING.md §A Rule 3 (loft / mesh /
BlowerWheelGeometry / FanRotorGeometry primitives preserved, literals
parameterised by scale and multiplicity):
  S1  bellows_boards + board_squeeze + brass_nozzle + flap_valve + board_handle
      rec_...__air_blower__001                                L32-L459
  S2  volute_drum + centrifugal_wheel + adjustable_tube + spoked_grille + top_grip
      rec_...__air_blower__002                                L145-L517
  S3  axial_impeller   rec_air_blower_var_axial_impeller       L429-L470
  S4  axial_barrel     rec_air_blower_var_axial_inline_barrel  L149-L215
  S5  canister_tank    rec_air_blower_var_canister_tank        L52-L215
  S6  spherical_pod    rec_air_blower_var_spherical_turbine_pod L84-L215
  S7  rubber_bulb + bulb_squeeze  rec_air_blower_var_rubber_bulb L84-L300
  S8  foot_pump        rec_air_blower_var_foot_pump_prismatic  L439-L478
  S9  flex_duct        rec_air_blower_var_flex_duct_outlet     L84-L122
  S10 filter_cap       rec_air_blower_var_filter_intake        L84-L161
  S11 pistol_grip      rec_air_blower_var_pistol_grip          L158-L230
  S12 fan_blades_8     rec_air_blower_var_fan_blades_8         L427-L436
  S13 fan_blades_32    rec_air_blower_var_fan_blades_32        L429-L436
  S14 bellows_folds_2  rec_air_blower_var_bellows_folds_2      L32-L37
  S15 bellows_folds_6  rec_air_blower_var_bellows_folds_6      L32-L37

Grandfather note (AUTHORING §A Rule 2): every non-FIXED joint here is a
pin-through-sleeve / captured-trunnion / journal-bearing / prismatic-slide type
(impeller-in-volute, crank-on-shaft, hinge-pin, bellows squeeze) whose mating
geometry is not two static axis-aligned faces, so it OMITS ``mating=`` and is
grandfathered with element-scoped ``allow_overlap`` — matching the
Bathroom_Hair_dryer reference template.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BlowerWheelGeometry,
    Box,
    Cylinder,
    FanRotorBlade,
    FanRotorGeometry,
    FanRotorHub,
    Inertial,
    KnobGeometry,
    KnobGrip,
    Mimic,
    MotionLimits,
    MotionProperties,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums / families / compatibility matrix.
# --------------------------------------------------------------------------- #

BodyForm = Literal[
    "bellows_boards", "rubber_bulb", "volute_drum", "axial_barrel",
    "canister_tank", "spherical_pod",
]
Motion = Literal[
    "centrifugal_wheel", "axial_impeller", "board_squeeze", "foot_pump", "bulb_squeeze",
]
Outlet = Literal["brass_nozzle", "adjustable_tube", "flex_duct"]
Intake = Literal["flap_valve", "spoked_grille", "filter_cap"]
Grip = Literal["board_handle", "bulb_grip", "top_grip", "pistol_grip"]
PaletteStyle = Literal[
    "walnut_brass", "painted_steel", "matte_black", "safety_orange", "patina_copper",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "bellows_boards", "rubber_bulb", "volute_drum", "axial_barrel",
    "canister_tank", "spherical_pod",
)
_BODY_WEIGHTS = (0.20, 0.10, 0.22, 0.16, 0.16, 0.16)

# body_form -> family
FAMILY_OF: dict[str, str] = {
    "bellows_boards": "bellows",
    "rubber_bulb": "bellows",
    "volute_drum": "blower",
    "axial_barrel": "blower",
    "canister_tank": "blower",
    "spherical_pod": "blower",
}

# Compatibility matrix: which motion / outlet / intake / grip modules are legal
# for a given body_form. resolve_config downgrades to element [0] on any illegal
# combination (never builds+fails an illegal body×motion).
MOTION_BY_BODY: dict[str, tuple[Motion, ...]] = {
    "bellows_boards": ("board_squeeze", "foot_pump"),
    "rubber_bulb": ("bulb_squeeze",),
    "volute_drum": ("centrifugal_wheel", "axial_impeller"),
    "axial_barrel": ("centrifugal_wheel", "axial_impeller"),
    "canister_tank": ("centrifugal_wheel", "axial_impeller"),
    "spherical_pod": ("centrifugal_wheel", "axial_impeller"),
}
OUTLET_BY_FAMILY: dict[str, tuple[Outlet, ...]] = {
    "bellows": ("brass_nozzle",),
    "blower": ("adjustable_tube", "flex_duct"),
}
INTAKE_BY_FAMILY: dict[str, tuple[Intake, ...]] = {
    "bellows": ("flap_valve",),
    "blower": ("spoked_grille", "filter_cap"),
}
GRIP_BY_BODY: dict[str, tuple[Grip, ...]] = {
    "bellows_boards": ("board_handle",),
    "rubber_bulb": ("bulb_grip",),
    "volute_drum": ("top_grip", "pistol_grip"),
    "axial_barrel": ("top_grip", "pistol_grip"),
    "canister_tank": ("top_grip", "pistol_grip"),
    "spherical_pod": ("top_grip", "pistol_grip"),
}

FAN_BLADE_COUNTS: tuple[int, ...] = (8, 18, 32)
_FAN_WEIGHTS = (0.34, 0.40, 0.26)
BELLOWS_FOLD_COUNTS: tuple[int, ...] = (2, 4, 6)
_FOLD_WEIGHTS = (0.30, 0.44, 0.26)

PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "walnut_brass", "painted_steel", "matte_black", "safety_orange", "patina_copper",
)

# Palette roles (drive EVERY .visual across BOTH families; palette is sampled
# independently of family — a walnut blower or a steel bellows are legitimate
# retro colorways, never family-special-cased):
#   body   = main shell / boards / bulb / drum
#   accent = leather / plastic collars / dark trim / rubber
#   metal  = brass nozzle / aluminum tube / flex duct (the shiny outlet + hardware)
#   mech   = gunmetal crank / shaft / fan wheel / pivot pin
#   detail = screws / rim / seam / tacks / grille edge
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "walnut_brass": {
        "body": (0.33, 0.105, 0.045, 1.0),
        "accent": (0.055, 0.050, 0.050, 1.0),
        "metal": (0.68, 0.48, 0.18, 1.0),
        "mech": (0.30, 0.25, 0.15, 1.0),
        "detail": (0.38, 0.25, 0.09, 1.0),
    },
    "painted_steel": {
        "body": (0.30, 0.36, 0.44, 1.0),
        "accent": (0.05, 0.06, 0.07, 1.0),
        "metal": (0.66, 0.68, 0.69, 1.0),
        "mech": (0.16, 0.17, 0.18, 1.0),
        "detail": (0.27, 0.29, 0.30, 1.0),
    },
    "matte_black": {
        "body": (0.11, 0.11, 0.12, 1.0),
        "accent": (0.03, 0.03, 0.035, 1.0),
        "metal": (0.55, 0.57, 0.60, 1.0),
        "mech": (0.20, 0.22, 0.24, 1.0),
        "detail": (0.30, 0.30, 0.32, 1.0),
    },
    "safety_orange": {
        "body": (0.80, 0.35, 0.05, 1.0),
        "accent": (0.06, 0.06, 0.07, 1.0),
        "metal": (0.66, 0.68, 0.69, 1.0),
        "mech": (0.18, 0.19, 0.20, 1.0),
        "detail": (0.12, 0.12, 0.13, 1.0),
    },
    "patina_copper": {
        "body": (0.30, 0.52, 0.46, 1.0),
        "accent": (0.10, 0.09, 0.08, 1.0),
        "metal": (0.72, 0.45, 0.20, 1.0),
        "mech": (0.35, 0.28, 0.18, 1.0),
        "detail": (0.20, 0.16, 0.10, 1.0),
    },
}


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


# --------------------------------------------------------------------------- #
# Config.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class PictureX0611AirBlowerConfig:
    """Public configuration sampled by ``config_from_seed`` or supplied directly."""

    body_form: BodyForm = "volute_drum"
    motion_mechanism: Motion = "centrifugal_wheel"
    outlet: Outlet = "adjustable_tube"
    intake: Intake = "spoked_grille"
    grip: Grip = "top_grip"
    palette_style: PaletteStyle = "walnut_brass"

    fan_blade_count: int = 18       # blower only
    bellows_fold_count: int = 4     # bellows_boards only

    # controlled local scales (clamped in resolve_config)
    body_len_scale: float = 1.0     # blower envelope length (grow-only)
    outlet_len_scale: float = 1.0   # blower nozzle / duct length
    crank_radius_scale: float = 1.0 # blower crank arm reach
    chamber_scale: float = 1.0      # bellows chamber height / fold spread
    squeeze_travel_scale: float = 1.0  # bellows / bulb joint travel

    name: str = "reference_pictureX_0611_Air_blower"


@dataclass(frozen=True)
class ResolvedPictureX0611AirBlowerConfig:
    body_form: BodyForm
    family: str
    motion_mechanism: Motion
    outlet: Outlet
    intake: Intake
    grip: Grip
    palette_style: PaletteStyle

    fan_blade_count: int
    bellows_fold_count: int

    body_len_scale: float
    outlet_len_scale: float
    crank_radius_scale: float
    chamber_scale: float
    squeeze_travel_scale: float

    name: str
    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> PictureX0611AirBlowerConfig:
    """Deterministic per-seed sampling. ``seed=0`` is NOT special.

    Order: body_form -> family -> gated motion/outlet/intake/grip -> the one
    multiplicity axis that exists for the family -> palette + continuous scales.
    """
    rng = random.Random(seed)

    body: BodyForm = rng.choices(BODY_FORMS, weights=_BODY_WEIGHTS, k=1)[0]
    family = FAMILY_OF[body]
    motion: Motion = rng.choice(MOTION_BY_BODY[body])
    outlet: Outlet = rng.choice(OUTLET_BY_FAMILY[family])
    intake: Intake = rng.choice(INTAKE_BY_FAMILY[family])
    grip: Grip = rng.choice(GRIP_BY_BODY[body])
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)

    fan_blade_count = rng.choices(FAN_BLADE_COUNTS, weights=_FAN_WEIGHTS, k=1)[0]
    bellows_fold_count = rng.choices(BELLOWS_FOLD_COUNTS, weights=_FOLD_WEIGHTS, k=1)[0]

    return PictureX0611AirBlowerConfig(
        body_form=body,
        motion_mechanism=motion,
        outlet=outlet,
        intake=intake,
        grip=grip,
        palette_style=palette,
        fan_blade_count=fan_blade_count,
        bellows_fold_count=bellows_fold_count,
        body_len_scale=round(rng.uniform(1.0, 1.15), 4),
        outlet_len_scale=round(rng.uniform(0.85, 1.15), 4),
        crank_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        chamber_scale=round(rng.uniform(0.90, 1.10), 4),
        squeeze_travel_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_pictureX_0611_Air_blower_{seed}",
    )


def resolve_config(
    config: PictureX0611AirBlowerConfig,
) -> ResolvedPictureX0611AirBlowerConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    body = _pick(config.body_form, BODY_FORMS)
    family = FAMILY_OF[body]

    # --- COMPATIBILITY MATRIX GATE: downgrade illegal combos to family default,
    #     never build+fail an illegal body×motion / family×outlet/intake body×grip.
    motion = _pick(config.motion_mechanism, MOTION_BY_BODY[body])
    outlet = _pick(config.outlet, OUTLET_BY_FAMILY[family])
    intake = _pick(config.intake, INTAKE_BY_FAMILY[family])
    grip = _pick(config.grip, GRIP_BY_BODY[body])

    fan_blade_count = int(config.fan_blade_count)
    if fan_blade_count not in FAN_BLADE_COUNTS:
        fan_blade_count = min(FAN_BLADE_COUNTS, key=lambda n: abs(n - fan_blade_count))
    bellows_fold_count = int(config.bellows_fold_count)
    if bellows_fold_count not in BELLOWS_FOLD_COUNTS:
        bellows_fold_count = min(
            BELLOWS_FOLD_COUNTS, key=lambda n: abs(n - bellows_fold_count)
        )

    return ResolvedPictureX0611AirBlowerConfig(
        body_form=body,
        family=family,
        motion_mechanism=motion,
        outlet=outlet,
        intake=intake,
        grip=grip,
        palette_style=config.palette_style,
        fan_blade_count=fan_blade_count,
        bellows_fold_count=bellows_fold_count,
        body_len_scale=_clamp(config.body_len_scale, 1.0, 1.15),
        outlet_len_scale=_clamp(config.outlet_len_scale, 0.85, 1.15),
        crank_radius_scale=_clamp(config.crank_radius_scale, 0.90, 1.12),
        chamber_scale=_clamp(config.chamber_scale, 0.90, 1.10),
        squeeze_travel_scale=_clamp(config.squeeze_travel_scale, 0.85, 1.15),
        name=config.name,
        palette=dict(PALETTES[config.palette_style]),
    )


def _materials(model: ArticulatedObject, r: ResolvedPictureX0611AirBlowerConfig):
    ps = r.palette_style
    p = r.palette
    return {
        "body": model.material(f"ab_body_{ps}", rgba=p["body"]),
        "accent": model.material(f"ab_accent_{ps}", rgba=p["accent"]),
        "metal": model.material(f"ab_metal_{ps}", rgba=p["metal"]),
        "mech": model.material(f"ab_mech_{ps}", rgba=p["mech"]),
        "detail": model.material(f"ab_detail_{ps}", rgba=p["detail"]),
    }


# =========================================================================== #
# BLOWER family (S2 drivetrain + S3/S4/S5/S6/S9/S10/S11 form modules).
# =========================================================================== #

# P2 nominal stations (verbatim frame; Y = rotation axis, +X = outlet).
# FRONT face is FIXED for every body_form so the crank/shaft/fan drivetrain
# (authored at nominal Y) always has a real contact path to the housing; only
# the REAR extent varies per form (the ③ envelope difference).
_OUTLET_X = 0.079
_OUTLET_Z = 0.045
_CAVITY_R = 0.062
_FRONT_WALL = 0.004
_FRONT_Y = -0.033


def _cyl_y(radius: float, length: float, center=(0.0, 0.0, 0.0)):
    """Cylinder centered on the global Y axis (S2 _cylinder_y, L30-38)."""
    return (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(length / 2.0, both=True)
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
        .translate(center)
    )


def _cyl_x(radius: float, length: float, center=(0.0, 0.0, 0.0)):
    """Cylinder centered on the global X axis (S2 _cylinder_x, L41-49)."""
    return (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(length / 2.0, both=True)
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
        .translate(center)
    )


def _xz_profile(points, depth: float):
    """Extrude an X/Z silhouette symmetrically along Y (S2 _extruded_xz_profile)."""
    return cq.Workplane("XZ").polyline(points).close().extrude(depth / 2.0, both=True)


def _capsule_y(radius: float, cyl_length: float, center=(0.0, 0.0, 0.0)):
    """Capsule along Y: cylinder + hemisphere end caps (S5 _capsule_y L52-62)."""
    body = _cyl_y(radius, cyl_length, center=center)
    top = cq.Workplane("XY").sphere(radius).translate(
        (center[0], center[1] + cyl_length / 2.0, center[2])
    )
    bot = cq.Workplane("XY").sphere(radius).translate(
        (center[0], center[1] - cyl_length / 2.0, center[2])
    )
    return body.union(top).union(bot)


def _ovoid_pod_y(equatorial_r: float, polar_half: float, center=(0.0, 0.0, 0.0)):
    """Revolved oblate spheroid centered on Y (S6 _ovoid_pod_y L84-101)."""
    n = 16
    pts = []
    for i in range(n + 1):
        t = math.pi * i / n
        pts.append((equatorial_r * math.sin(t), polar_half * math.cos(t)))
    profile = cq.Workplane("XY").spline(pts).close()
    pod = profile.revolve(360, (0.0, -polar_half), (0.0, polar_half))
    return pod.translate(center)


def _tapered_tube_x(x0, length, outer_start, outer_end, wall):
    """Open-ended tapered tube along +X (S2 _tapered_tube_x L57-81)."""
    outer = (
        cq.Workplane("YZ").workplane(offset=x0).circle(outer_start)
        .workplane(offset=length).circle(outer_end).loft(combine=True)
    )
    inner = (
        cq.Workplane("YZ").workplane(offset=x0 - 0.001).circle(outer_start - wall)
        .workplane(offset=length + 0.002).circle(outer_end - wall).loft(combine=True)
    )
    return outer.cut(inner)


def _corrugated_duct_x(x_start, x_end, inner_radius, peak_radius, valley_radius, rib_count):
    """Corrugated flexible duct along +X (S9 _corrugated_duct_x L84-122)."""
    duct_length = x_end - x_start
    x_center = (x_start + x_end) / 2.0
    tube_outer = _cyl_x(valley_radius, duct_length, center=(x_center, 0.0, 0.0))
    tube_bore = _cyl_x(inner_radius, duct_length + 0.002, center=(x_center, 0.0, 0.0))
    duct = tube_outer.cut(tube_bore)
    rib_width = duct_length / (rib_count * 2.5)
    spacing = duct_length / (rib_count + 1)
    for i in range(rib_count):
        rib_x = x_start + spacing * (i + 1)
        ring = _cyl_x(peak_radius, rib_width, center=(rib_x, 0.0, 0.0))
        hole = _cyl_x(valley_radius - 0.0003, rib_width + 0.0005, center=(rib_x, 0.0, 0.0))
        duct = duct.union(ring.cut(hole))
    return duct


def _rear_grille():
    """Spoked rear intake grille (S2 _rear_grille L84-100)."""
    ring = _cyl_y(0.066, 0.004, center=(0.0, 0.0295, 0.0)).cut(
        _cyl_y(0.057, 0.006, center=(0.0, 0.0295, 0.0))
    )
    hub = _cyl_y(0.014, 0.004, center=(0.0, 0.0295, 0.0))
    grille = ring.union(hub)
    spoke = (
        cq.Workplane("XZ").rect(0.124, 0.0045).extrude(0.002, both=True)
        .translate((0.0, 0.0295, 0.0))
    )
    for angle in range(0, 180, 30):
        grille = grille.union(spoke.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), float(angle)))
    return grille


def _filter_cap_sleeve(hole_count: int = 24):
    """Perforated cylindrical mesh filter sleeve (S10 _filter_cap_outer_sleeve L84-149)."""
    outer_r = 0.064
    wall = 0.0018
    length = 0.040
    cy = 0.030 + length / 2.0
    sleeve = _cyl_y(outer_r, length, center=(0.0, cy, 0.0)).cut(
        _cyl_y(outer_r - wall, length + 0.002, center=(0.0, cy, 0.0))
    )
    hole_r = 0.0028
    for row_offset, y_frac in ((0.0, 0.35), (math.pi / hole_count, 0.65)):
        y_pos = 0.030 + length * y_frac
        for i in range(hole_count):
            angle = row_offset + 2.0 * math.pi * i / hole_count
            hx = (outer_r - wall / 2.0) * math.cos(angle)
            hz = (outer_r - wall / 2.0) * math.sin(angle)
            hole_y = (
                cq.Workplane("XZ").workplane(offset=-0.002).circle(hole_r)
                .extrude(wall + 0.004).translate((hx, y_pos, hz))
            )
            sleeve = sleeve.cut(hole_y)
    end_cap = _cyl_y(outer_r, 0.002, center=(0.0, 0.030 + length + 0.001, 0.0)).cut(
        _cyl_y(outer_r - wall - 0.001, 0.004, center=(0.0, 0.030 + length + 0.001, 0.0))
    )
    sleeve = sleeve.union(end_cap)
    flange = _cyl_y(outer_r + 0.004, 0.003, center=(0.0, 0.0315, 0.0)).cut(
        _cyl_y(outer_r - 0.001, 0.005, center=(0.0, 0.0315, 0.0))
    )
    return sleeve.union(flange)


def _filter_cap_foam():
    """Foam pre-filter core press-fit in the sleeve (S10 _filter_cap_foam_core L152-161)."""
    foam_r = 0.0620
    foam_length = 0.036
    cy = 0.030 + foam_length / 2.0 + 0.002
    return _cyl_y(foam_r, foam_length, center=(0.0, cy, 0.0))


def _top_grip_solids():
    """Molded horizontal top grip + top rib (S2 handle/top_rib L154-178)."""
    handle = _xz_profile(
        (
            (-0.058, 0.063), (-0.083, 0.078), (-0.194, 0.076), (-0.211, 0.067),
            (-0.218, 0.042), (-0.211, 0.010), (-0.199, -0.013), (-0.190, 0.009),
            (-0.181, 0.027), (-0.083, 0.030), (-0.059, 0.041),
        ),
        0.038,
    )
    top_rib = _xz_profile(
        ((-0.066, 0.066), (-0.050, 0.086), (-0.039, 0.083), (-0.031, 0.067)),
        0.014,
    )
    return handle.union(top_rib)


def _pistol_grip_solid():
    """Vertical pistol grip + finger ridges + junction rib (S11 L158-230)."""
    grip = _xz_profile(
        (
            (-0.054, -0.060), (-0.063, -0.086), (-0.061, -0.120), (-0.056, -0.148),
            (-0.046, -0.166), (-0.032, -0.174), (-0.016, -0.170), (-0.009, -0.148),
            (-0.007, -0.115), (-0.013, -0.086), (-0.026, -0.068), (-0.040, -0.060),
        ),
        0.038,
    )
    for band in (
        ((-0.014, -0.100), (-0.003, -0.100), (-0.001, -0.104), (-0.003, -0.108), (-0.014, -0.108)),
        ((-0.014, -0.116), (-0.002, -0.116), (0.000, -0.120), (-0.002, -0.124), (-0.014, -0.124)),
        ((-0.014, -0.132), (-0.001, -0.132), (0.001, -0.136), (-0.001, -0.140), (-0.014, -0.140)),
    ):
        grip = grip.union(_xz_profile(band, 0.032))
    top_rib = _xz_profile(
        ((-0.058, -0.060), (-0.044, -0.046), (-0.030, -0.046), (-0.020, -0.060)),
        0.016,
    )
    return grip.union(top_rib)


def _front_spider(front_far_y: float, spoke_y: float):
    """Central bearing spine (on the Y axis) + 3 radial spokes to the shell inner
    wall. Unioned into main_body so the on-axis crank/shaft have a real support
    path to the shell for EVERY body_form (mirrors hair_dryer _front_mount_hub).
    The spine runs from the crank hub (front_far_y) back past the fan to the spoke
    ring; the spokes sit BEHIND the fan (spoke_y) so a spinning wheel never hits
    them."""
    spine_center = 0.5 * (front_far_y + (spoke_y + 0.002))
    spine_len = (spoke_y + 0.002) - front_far_y
    spider = _cyl_y(0.011, spine_len, center=(0.0, spine_center, 0.0))
    for i in range(3):
        ang = i * 2.0 * math.pi / 3.0
        spoke = (
            cq.Workplane("XZ").rect(0.010, 2.0 * 0.063).extrude(0.002, both=True)
            .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), math.degrees(ang))
            .translate((0.0, spoke_y, 0.0))
        )
        spider = spider.union(spoke)
    return spider


def _blower_body_geometry(r: ResolvedPictureX0611AirBlowerConfig):
    """Per body_form outer solid + fixed front face + per-form rear + radius +
    intake station + flat-front flag. All forms share the same cavity + tangential
    outlet passage + drivetrain (S2/S4/S5/S6)."""
    # Bodies are CENTERED on y=0 so their widest cross-section (where the top /
    # pistol grip and the outlet attach) is always full radius; the front bearing
    # spider (built in _build_blower) reconnects the on-axis drivetrain to the
    # shell regardless of how far the front sits. All forms use radius >= 0.073 at
    # the equator (the P2 grip attaches there).
    s = r.body_len_scale
    if r.body_form == "volute_drum":
        length = 0.062 * s
        radius = 0.073
        outer = _cyl_y(radius, length)
        half = length / 2.0
        return outer, -half, half, radius, half - 0.006, True
    if r.body_form == "axial_barrel":
        length = 0.104 * s
        radius = 0.073
        outer = _cyl_y(radius, length)
        half = length / 2.0
        return outer, -half, half, radius, half - 0.006, True
    if r.body_form == "canister_tank":
        # Prolate (elongated) smooth ovoid tank — a single revolved surface (no
        # cap/cylinder junction to sever under the cavity cut, unlike a capsule).
        polar = 0.082 * s
        radius = 0.074
        outer = _ovoid_pod_y(radius, polar)
        intake_y = polar * math.sqrt(max(0.0, 1.0 - (_CAVITY_R / radius) ** 2)) - 0.004
        return outer, -polar, polar, radius, intake_y, False
    # spherical_pod — oblate (rounder) ovoid.
    polar = 0.056 * s
    radius = 0.080
    outer = _ovoid_pod_y(radius, polar)
    # rear breakthrough: ovoid radius == cavity radius.
    intake_y = polar * math.sqrt(max(0.0, 1.0 - (_CAVITY_R / radius) ** 2)) - 0.004
    return outer, -polar, polar, radius, intake_y, False


def _build_blower(model, r, mats):
    body_mat = mats["body"]
    accent = mats["accent"]
    metal = mats["metal"]
    mech = mats["mech"]
    detail = mats["detail"]

    housing = model.part(
        "housing",
        meta={"construction": f"molded hollow {r.body_form} centrifugal casing"},
    )
    outer, front_y, rear_y, radius, intake_y, flat = _blower_body_geometry(r)

    # Fuse the (non-articulating) grip into the housing shell (Rule 1).
    if r.grip == "pistol_grip":
        outer = outer.union(_pistol_grip_solid())
    else:
        outer = outer.union(_top_grip_solids())
    # Front bulge ring on the flat front face (drum/barrel only).
    if flat:
        outer = outer.union(
            _cyl_y(min(0.069, radius - 0.003), 0.006, center=(0.0, front_y + 0.001, 0.0))
        )

    # Rear cavity: retain a 4 mm front wall, open the rear (all forms are single
    # revolved/extruded surfaces, so the cut never severs a piece).
    cavity_front = front_y + _FRONT_WALL
    cavity_len = (rear_y - cavity_front) + 0.020
    cavity_center = cavity_front + cavity_len / 2.0
    body = outer.cut(_cyl_y(_CAVITY_R, cavity_len, center=(0.0, cavity_center, 0.0)))
    # Central bearing spider: reconnects the on-axis drivetrain to the shell for
    # every body_form (the wide cavity otherwise severs a domed front cap). Spine
    # front reaches the crank hub; spokes sit behind the fan.
    cy_crank = front_y - 0.027
    # Spine front stops at the crank hub REAR (cy_crank + 0.005) so it never pokes
    # forward into the radial crank-arm sweep; the hub (axisymmetric) bridges it.
    body = body.union(_front_spider(cy_crank + 0.005, 0.025))
    # Drive-shaft bore down the spine (0.004 < shaft 0.0045 -> journal contact).
    body = body.cut(_cyl_y(0.0040, 0.160, center=(0.0, 0.0, 0.0)))
    # (The tangential outlet is the outlet_socket boss below; cutting a full
    # passage through domed bodies severed a wall chunk, so the outlet is
    # represented by the protruding socket seated on the outer surface.)

    housing.visual(
        mesh_from_cadquery(body, "blower_main_body", tolerance=0.0009),
        material=body_mat,
        name="main_body", material_class_id=("metal.copper_patinated" if r.palette_style in {"walnut_brass", "painted_steel", "patina_copper"} else "plastic.opaque_generic"),
    )

    outlet_socket = _cyl_x(0.026, 0.058, center=(_OUTLET_X, 0.0, _OUTLET_Z)).cut(
        _cyl_x(0.0195, 0.064, center=(_OUTLET_X + 0.003, 0.0, _OUTLET_Z))
    )
    housing.visual(
        mesh_from_cadquery(outlet_socket, "blower_outlet_socket", tolerance=0.0008),
        material=accent,
        name="outlet_socket", material_class_id="metal.blackened_gunmetal",
    )

    # --- Slot D intake (fused body visual): spoked grille OR filter cap ---
    # Mounted at the rear breakthrough (behind the fan) so its rim seats on the
    # cavity opening annulus (contact, no float island).
    grille_dy = intake_y - 0.0295
    if r.intake == "filter_cap":
        housing.visual(
            mesh_from_cadquery(_filter_cap_sleeve(), "blower_filter_sleeve", tolerance=0.0009),
            origin=Origin(xyz=(0.0, grille_dy, 0.0)),
            material=detail,
            name="intake_grille", material_class_id="metal.mesh_chainmail",
        )
        housing.visual(
            mesh_from_cadquery(_filter_cap_foam(), "blower_filter_foam", tolerance=0.0011),
            origin=Origin(xyz=(0.0, grille_dy, 0.0)),
            material=accent,
            name="intake_foam", material_class_id="fabric.flexible_foam",
        )
    else:
        housing.visual(
            mesh_from_cadquery(_rear_grille(), "blower_intake_grille", tolerance=0.0008),
            origin=Origin(xyz=(0.0, grille_dy, 0.0)),
            material=detail,
            name="intake_grille", material_class_id="metal.mesh_chainmail",
        )

    # Front seam + cover screws (host-conformal decoration on flat fronts, Rule 4).
    if flat:
        seam_outer = min(0.0705, radius - 0.0025)
        front_seam = _cyl_y(seam_outer, 0.0040, center=(0.0, front_y + 0.0005, 0.0)).cut(
            _cyl_y(seam_outer - 0.0025, 0.0080, center=(0.0, front_y + 0.0005, 0.0))
        )
        housing.visual(
            mesh_from_cadquery(front_seam, "blower_front_seam", tolerance=0.0006),
            material=detail,
            name="front_seam", material_class_id="metal.generic_plain",
        )
        screw_r = radius - 0.017
        for index, angle_deg in enumerate((28.0, 118.0, 208.0, 298.0)):
            angle = math.radians(angle_deg)
            housing.visual(
                Cylinder(radius=0.0030, length=0.006),
                origin=Origin(
                    xyz=(screw_r * math.cos(angle), front_y + 0.0005, screw_r * math.sin(angle)),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=detail,
                name=f"cover_screw_{index}", material_class_id="metal.steel_bare",
            )
    # Rubber foot embedded into the body underside (tied to the body radius).
    housing.visual(
        Box((0.028, 0.034, 0.008)),
        origin=Origin(xyz=(-0.010, 0.0, -radius + 0.003)),
        material=accent,
        name="housing_foot", material_class_id="rubber.smooth_plain",
    )
    housing.inertial = Inertial.from_geometry(
        Box((0.16, rear_y - front_y + 0.02, 0.18)), mass=0.55
    )

    # --- Slot C outlet: adjustable aluminum tube OR corrugated flex duct ------ #
    nozzle = model.part("nozzle", meta={"construction": f"{r.outlet} outlet"})
    tube_len = 0.168 * r.outlet_len_scale
    if r.outlet == "flex_duct":
        duct = _corrugated_duct_x(-0.015, -0.015 + tube_len, 0.0156, 0.0210, 0.0183, 7)
        nozzle.visual(
            mesh_from_cadquery(duct, "blower_nozzle_duct", tolerance=0.0007),
            material=metal,
            name="metal_tube", material_class_id="metal.aluminum_bare",
        )
    else:  # adjustable_tube
        tube = _tapered_tube_x(-0.015, tube_len, 0.0183, 0.0156, 0.00125)
        nozzle.visual(
            mesh_from_cadquery(tube, "blower_nozzle_tube", tolerance=0.0006),
            material=metal,
            name="metal_tube", material_class_id="metal.aluminum_bare",
        )
    base_sleeve = _cyl_x(0.0187, 0.028, center=(-0.004, 0.0, 0.0)).cut(
        _cyl_x(0.0158, 0.032, center=(-0.004, 0.0, 0.0))
    )
    nozzle.visual(
        mesh_from_cadquery(base_sleeve, "blower_nozzle_sleeve", tolerance=0.0005),
        material=accent,
        name="base_sleeve", material_class_id="metal.blackened_gunmetal",
    )
    retaining_ring = _cyl_x(0.0197, 0.004, center=(-0.009, 0.0, 0.0)).cut(
        _cyl_x(0.0160, 0.006, center=(-0.009, 0.0, 0.0))
    )
    nozzle.visual(
        mesh_from_cadquery(retaining_ring, "blower_nozzle_ring", tolerance=0.0005),
        material=accent,
        name="retaining_ring", material_class_id="metal.blackened_gunmetal",
    )
    nozzle.visual(
        Box((0.018, 0.004, 0.004)),
        origin=Origin(xyz=(0.025, 0.0, 0.0173)),
        material=accent,
        name="adjustment_rib", material_class_id="metal.blackened_gunmetal",
    )
    nozzle.inertial = Inertial.from_geometry(Box((tube_len, 0.04, 0.04)), mass=0.05)
    model.articulation(
        "housing_to_nozzle",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=nozzle,
        origin=Origin(xyz=(0.105, 0.0, _OUTLET_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=2.0, lower=-0.35, upper=0.35),
        motion_properties=MotionProperties(damping=0.08, friction=0.15),
        meta={"function": "friction-adjustable outlet twist"},
    )

    # --- Slot B motion: hand crank (grip fused) -> mimic shaft + mimic wheel -- #
    # cy_crank + the central bearing spine are built in the main_body block above;
    # the crank hub seats against the spine front (contact), the shaft rides in
    # the spine bore (journal), and the fan spins around the spine.
    crank = model.part("crank")
    crank.visual(
        Cylinder(radius=0.0115, length=0.014),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mech,
        name="crank_hub", material_class_id="metal.blackened_gunmetal",
    )
    reach = 0.086 * r.crank_radius_scale
    crank_end = (-reach * 0.79, -reach * 0.60)
    crank_radius = math.hypot(*crank_end)
    start_fraction = 0.010 / crank_radius
    crank_start = (crank_end[0] * start_fraction, crank_end[1] * start_fraction)
    crank_length = crank_radius - 0.010
    crank_angle = math.atan2(-crank_end[1], crank_end[0])
    crank.visual(
        Box((crank_length, 0.008, 0.010)),
        origin=Origin(
            xyz=((crank_start[0] + crank_end[0]) / 2.0, -0.002, (crank_start[1] + crank_end[1]) / 2.0),
            rpy=(0.0, crank_angle, 0.0),
        ),
        material=mech,
        name="crank_arm", material_class_id="metal.blackened_gunmetal",
    )
    # Grip pin spans from the arm out to the rotating grip so both connect.
    crank.visual(
        Cylinder(radius=0.0048, length=0.050),
        origin=Origin(xyz=(crank_end[0], -0.022, crank_end[1]), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mech,
        name="grip_pin", material_class_id="metal.blackened_gunmetal",
    )
    # Rotating hand grip fused onto the crank (turns with the arm; Rule 1). Placed
    # over the grip pin (which spans y[-0.047, 0.003]) so it is a connected solid.
    grip_geometry = KnobGeometry(
        0.017, 0.040, body_style="cylindrical", edge_radius=0.0015,
        grip=KnobGrip(style="ribbed", count=14, depth=0.0007, width=0.0014), center=True,
    )
    crank.visual(
        mesh_from_geometry(grip_geometry, "blower_crank_grip"),
        origin=Origin(xyz=(crank_end[0], -0.030, crank_end[1]), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=accent,
        name="rotating_grip", material_class_id="rubber.pebbled",
    )
    crank.inertial = Inertial.from_geometry(Box((0.10, 0.05, 0.10)), mass=0.06)
    model.articulation(
        "housing_to_crank",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=crank,
        origin=Origin(xyz=(0.0, cy_crank, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=12.0),
        motion_properties=MotionProperties(damping=0.03, friction=0.04),
        meta={"function": "manual drive input"},
    )

    drive_shaft = model.part("drive_shaft")
    drive_shaft.visual(
        Cylinder(radius=0.0045, length=0.090),
        origin=Origin(xyz=(0.0, 0.010, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mech,
        name="drive_shaft", material_class_id="metal.blackened_gunmetal",
    )
    drive_shaft.visual(
        Cylinder(radius=0.0080, length=0.006),
        origin=Origin(xyz=(0.0, 0.036, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mech,
        name="drive_collar", material_class_id="metal.blackened_gunmetal",
    )
    drive_shaft.inertial = Inertial.from_geometry(Box((0.02, 0.09, 0.02)), mass=0.02)
    model.articulation(
        "housing_to_shaft",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=drive_shaft,
        origin=Origin(xyz=(0.0, -0.032, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=12.0),
        mimic=Mimic(joint="housing_to_crank", multiplier=1.0),
        meta={"function": "coaxial crank shaft"},
    )

    fan_rotor = model.part("fan_rotor", meta={"blade_count": r.fan_blade_count})
    if r.motion_mechanism == "axial_impeller":
        # S3: axial propeller. Blade count clamped to a propeller-realistic band.
        axial_blades = int(_clamp(round(r.fan_blade_count / 4.0) + 2, 3, 9))
        fan_geometry = FanRotorGeometry(
            0.048, 0.018, axial_blades,
            thickness=0.012, blade_pitch_deg=32.0, blade_sweep_deg=18.0,
            blade=FanRotorBlade(shape="broad", tip_pitch_deg=14.0, camber=0.12),
            hub=FanRotorHub(style="domed", bore_diameter=0.017), center=True,
        )
    else:
        # S2/S12/S13: centrifugal squirrel-cage wheel, N vanes loop-emitted.
        fan_geometry = BlowerWheelGeometry(
            0.050, 0.018, 0.028, r.fan_blade_count,
            blade_thickness=0.0016, blade_sweep_deg=28.0,
            backplate=True, shroud=True, center=True,
        )
    fan_rotor.visual(
        mesh_from_geometry(fan_geometry, "blower_internal_fan"),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mech,
        name="fan_wheel", material_class_id="metal.blackened_gunmetal",
    )
    fan_hub = _cyl_y(0.020, 0.006).cut(_cyl_y(0.0055, 0.008))
    fan_rotor.visual(
        mesh_from_cadquery(fan_hub, "blower_fan_hub", tolerance=0.0005),
        material=mech,
        name="fan_hub", material_class_id="metal.blackened_gunmetal",
    )
    fan_rotor.inertial = Inertial.from_geometry(Box((0.10, 0.03, 0.10)), mass=0.05)
    model.articulation(
        "housing_to_rotor",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=fan_rotor,
        origin=Origin(xyz=(0.0, 0.004, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=12.0),
        mimic=Mimic(joint="housing_to_crank", multiplier=1.0),
        meta={"function": f"{r.motion_mechanism} fan wheel"},
    )


# =========================================================================== #
# BELLOWS_BOARDS family (S1 boards + folds + nozzle + flap; S8 foot-pump).
# =========================================================================== #

_BOARD_THICKNESS = 0.012
_PIVOT_X = -0.220
_UPPER_Z_NOM = 0.080
_BOARD_CLOSE_ANGLE = math.radians(5.0)
_NOZZLE_INSERT_X = -0.165
_NOZZLE_THROAT_X = -0.255
_NOZZLE_THROAT_LENGTH = 0.105


def _outline_points(*, local=False, body_only=False, y_scale=1.0):
    """Image-matched pear board / leather-body perimeter (S1 _outline_points L40-83)."""
    if body_only:
        points = [
            (-0.213, 0.000), (-0.185, 0.057), (-0.112, 0.102), (-0.010, 0.116),
            (0.090, 0.098), (0.160, 0.064), (0.205, 0.030), (0.216, 0.000),
            (0.205, -0.030), (0.160, -0.064), (0.090, -0.098), (-0.010, -0.116),
            (-0.112, -0.102), (-0.185, -0.057),
        ]
    else:
        points = [
            (-0.220, 0.000), (-0.190, 0.056), (-0.112, 0.103), (-0.010, 0.117),
            (0.092, 0.099), (0.163, 0.064), (0.215, 0.040), (0.300, 0.032),
            (0.410, 0.030), (0.462, 0.021), (0.480, 0.000), (0.462, -0.021),
            (0.410, -0.030), (0.300, -0.032), (0.215, -0.040), (0.163, -0.064),
            (0.092, -0.099), (-0.010, -0.117), (-0.112, -0.103), (-0.190, -0.056),
        ]
    x_shift = -_PIVOT_X if local else 0.0
    return [(x + x_shift, y * y_scale) for x, y in points]


def _wire_on(wp, points):
    return wp.moveTo(*points[0]).spline(points[1:], includeCurrent=True).close()


def _board_shape(*, local, intake_hole):
    """Shaped walnut board (S1 _board_shape L90-104)."""
    shape = _wire_on(
        cq.Workplane("XY").workplane(offset=-_BOARD_THICKNESS / 2.0),
        _outline_points(local=local),
    ).extrude(_BOARD_THICKNESS)
    if intake_hole:
        cutter = (
            cq.Workplane("XY").workplane(offset=-_BOARD_THICKNESS)
            .center(-0.020, 0.0).circle(0.014).extrude(_BOARD_THICKNESS * 2.0)
        )
        shape = shape.cut(cutter)
    return shape


def _loft_solid(z0, z1, scale0, scale1, *, local=False):
    """Loft between two body-only sections (S1 _loft_solid L107-123)."""
    loft = _wire_on(
        cq.Workplane("XY").workplane(offset=z0),
        _outline_points(local=local, body_only=True, y_scale=scale0),
    )
    loft = _wire_on(
        loft.workplane(offset=z1 - z0),
        _outline_points(local=local, body_only=True, y_scale=scale1),
    )
    return loft.loft(combine=True)


def _bellows_fold(height, scale0, scale1, *, local=False, throat_z=0.0):
    """One leather accordion fold shell with nozzle throat (S1 _bellows_fold L126-152)."""
    half = height / 2.0
    outer = _loft_solid(-half, half, scale0, scale1, local=local)
    inner = _loft_solid(-half - 0.003, half + 0.003, scale0 - 0.115, scale1 - 0.115, local=local)
    shell = outer.cut(inner)
    throat_x = _NOZZLE_THROAT_X - (_PIVOT_X if local else 0.0)
    throat = (
        cq.Workplane("YZ").workplane(offset=throat_x).center(0.0, throat_z)
        .circle(0.0235).extrude(_NOZZLE_THROAT_LENGTH)
    )
    return shell.cut(throat)


def _nozzle_shell():
    """Tapered brass nozzle shell (S1 _nozzle_shell L155-172)."""
    outer = (
        cq.Workplane("YZ").workplane(offset=-0.395).circle(0.0115)
        .workplane(offset=_NOZZLE_INSERT_X + 0.395).circle(0.0270).loft(combine=True)
    )
    inner = (
        cq.Workplane("YZ").workplane(offset=-0.398).circle(0.0080)
        .workplane(offset=_NOZZLE_INSERT_X + 0.405).circle(0.0220).loft(combine=True)
    )
    return outer.cut(inner)


def _nozzle_rim():
    return cq.Workplane("YZ").workplane(offset=-0.399).circle(0.0130).circle(0.0075).extrude(0.006)


def _wrist_loop():
    """Leather wrist strap loop (S1 _wrist_loop L179-194)."""
    outer = (
        cq.Workplane("XY").workplane(offset=0.0).center(0.395, -0.047)
        .ellipse(0.057, 0.021).extrude(0.004)
    )
    inner = (
        cq.Workplane("XY").workplane(offset=-0.001).center(0.395, -0.047)
        .ellipse(0.044, 0.011).extrude(0.006)
    )
    return outer.cut(inner)


def _make_folds(n: int, chamber_scale: float):
    """Procedurally generate N accordion folds (multiplicity axis, S1/S14/S15).

    rest_z strictly increases and ratio = (i+1)/n strictly increases -> the folds
    telescope monotonically. Named ``bellows_fold_{i}``.
    """
    upper_z = _UPPER_Z_NOM * chamber_scale
    folds = []
    for i in range(n):
        frac = (i + 1) / (n + 1)
        rest_z = (0.020 + frac * (upper_z - 0.030))
        height = 0.020
        taper = 0.95 + 0.05 * (1.0 - i / max(n, 1))
        ratio = (i + 1) / n
        folds.append((f"bellows_fold_{i}", rest_z, height, taper, taper - 0.01, ratio))
    return folds, upper_z


def _build_bellows_boards(model, r, mats):
    body_mat = mats["body"]
    accent = mats["accent"]
    metal = mats["metal"]
    detail = mats["detail"]

    folds_spec, upper_z = _make_folds(r.bellows_fold_count, r.chamber_scale)
    nozzle_center_z = upper_z / 2.0
    foot_pump = r.motion_mechanism == "foot_pump"
    stroke = 0.030 * r.squeeze_travel_scale

    lower_board = model.part("lower_board", meta={"construction": "shaped walnut board + nozzle"})
    lower_board.visual(
        mesh_from_cadquery(_board_shape(local=False, intake_hole=True), "lower_wood_panel"),
        material=body_mat, name="wood_panel", material_class_id=("wood.painted_clean" if r.palette_style in {"painted_steel", "matte_black", "safety_orange", "patina_copper"} else "wood.walnut_dark"),
    )
    lower_board.visual(
        mesh_from_cadquery(
            _bellows_fold(0.020, 0.94, 1.02, throat_z=nozzle_center_z - 0.013),
            "bellows_lower_collar",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.013)), material=accent, name="bellows_lower_collar", material_class_id="leather.aged_distressed",
    )
    lower_board.visual(
        mesh_from_cadquery(_nozzle_shell(), "brass_nozzle"),
        origin=Origin(xyz=(0.0, 0.0, nozzle_center_z)), material=metal, name="nozzle_shell", material_class_id="metal.brass_polished",
    )
    lower_board.visual(
        mesh_from_cadquery(_nozzle_rim(), "nozzle_mouth_rim"),
        origin=Origin(xyz=(0.0, 0.0, nozzle_center_z)), material=detail, name="nozzle_rim", material_class_id="metal.brass_aged",
    )
    # The rear neck block carries the pivot barrel. Its top stops ~8 mm below the
    # upper board's underside (upper_z - 0.006) so the boards do not bury into it
    # at rest, while still overlapping the barrel (single-sourced on upper_z).
    support_top = upper_z - 0.008
    support_bot = 0.005
    support_h = support_top - support_bot
    support_cz = 0.5 * (support_top + support_bot)
    for index, y in enumerate((-0.070, 0.070)):
        lower_board.visual(
            Box((0.050, 0.030, support_h)),
            origin=Origin(xyz=(-0.190, y, support_cz)), material=accent,
            name=f"hinge_support_{index}", material_class_id=("wood.painted_clean" if r.palette_style in {"painted_steel", "matte_black", "safety_orange", "patina_copper"} else "wood.walnut_dark"),
        )
        lower_board.visual(
            Cylinder(radius=0.011, length=0.024),
            origin=Origin(xyz=(-0.210, y, upper_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=metal, name=f"hinge_barrel_{index}", material_class_id="metal.brass_aged",
        )
    lower_tacks = [
        (-0.178, 0.055), (-0.110, 0.097), (-0.015, 0.110), (0.080, 0.095), (0.150, 0.064),
        (0.198, 0.034), (-0.178, -0.055), (-0.110, -0.097), (-0.015, -0.110), (0.080, -0.095),
        (0.150, -0.064), (0.198, -0.034),
    ]
    for index, (x, y) in enumerate(lower_tacks):
        lower_board.visual(
            Sphere(radius=0.0042), origin=Origin(xyz=(x, y, -0.0077)),
            material=detail, name=f"perimeter_tack_{index}", material_class_id="metal.brass_aged",
        )
    # Board handle + wrist strap (Slot E board_handle; fused, Rule 1).
    lower_board.visual(
        mesh_from_cadquery(_wrist_loop(), "wrist_loop"),
        origin=Origin(xyz=(0.0, 0.0, -0.009)), material=accent, name="wrist_strap", material_class_id="leather.aged_distressed",
    )
    lower_board.visual(
        Sphere(radius=0.0050), origin=Origin(xyz=(0.360, -0.027, -0.0070)),
        material=detail, name="strap_rivet", material_class_id="metal.brass_aged",
    )
    lower_board.inertial = Inertial.from_geometry(Box((0.70, 0.24, 0.10)), mass=0.6)

    upper_board = model.part("upper_board", meta={"construction": "matching walnut board"})
    upper_board.visual(
        mesh_from_cadquery(_board_shape(local=True, intake_hole=False), "upper_wood_panel"),
        material=body_mat, name="wood_panel", material_class_id=("wood.painted_clean" if r.palette_style in {"painted_steel", "matte_black", "safety_orange", "patina_copper"} else "wood.walnut_dark"),
    )
    upper_board.visual(
        Cylinder(radius=0.0048, length=0.180),
        origin=Origin(xyz=(0.010, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=detail, name="pivot_pin", material_class_id="metal.blackened_gunmetal",
    )
    for index, (x, y) in enumerate(lower_tacks):
        upper_board.visual(
            Sphere(radius=0.0042), origin=Origin(xyz=(x - _PIVOT_X, y, 0.0077)),
            material=detail, name=f"perimeter_tack_{index}", material_class_id="metal.brass_aged",
        )
    upper_board.inertial = Inertial.from_geometry(Box((0.70, 0.24, 0.05)), mass=0.4)

    intake_flap = model.part("intake_flap", meta={"construction": "one-way leather valve"})
    intake_flap.visual(
        Cylinder(radius=0.017, length=0.0018), origin=Origin(xyz=(0.0, -0.017, 0.0)),
        material=accent, name="flap_leaf", material_class_id="leather.aged_distressed",
    )
    intake_flap.visual(
        Cylinder(radius=0.0030, length=0.028), origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal, name="flap_hinge", material_class_id="metal.steel_bare",
    )
    intake_flap.inertial = Inertial.from_geometry(Box((0.03, 0.03, 0.005)), mass=0.005)

    bellows_parts = []
    for index, (name, rest_z, height, s0, s1, _ratio) in enumerate(folds_spec):
        fold = model.part(name, meta={"construction": "leather accordion fold"})
        fold.visual(
            mesh_from_cadquery(
                _bellows_fold(height, s0, s1, local=True, throat_z=nozzle_center_z - rest_z),
                f"{name}_shell",
            ),
            material=accent if index % 2 else detail, name="fold_shell", material_class_id="leather.aged_distressed",
        )
        fold.inertial = Inertial.from_geometry(Box((0.42, 0.22, height + 0.01)), mass=0.03)
        bellows_parts.append((fold, rest_z))

    if foot_pump:
        board_pivot = model.articulation(
            "board_pivot", ArticulationType.PRISMATIC, parent=lower_board, child=upper_board,
            origin=Origin(xyz=(_PIVOT_X, 0.0, upper_z)), axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=120.0, velocity=0.5, lower=-stroke, upper=0.0),
            meta={"motion": "negative stroke compresses the bellows vertically"},
        )
        for (fold, rest_z), (_n, _rz, _h, _s0, _s1, ratio) in zip(bellows_parts, folds_spec):
            model.articulation(
                f"{fold.name}_compression", ArticulationType.PRISMATIC,
                parent=lower_board, child=fold,
                origin=Origin(xyz=(_PIVOT_X, 0.0, rest_z)), axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=8.0, velocity=0.5, lower=-stroke * ratio, upper=0.0),
                mimic=Mimic(joint=board_pivot.name, multiplier=ratio),
                meta={"motion": "derived accordion-fold vertical compression"},
            )
    else:  # board_squeeze (REVOLUTE)
        board_pivot = model.articulation(
            "board_pivot", ArticulationType.REVOLUTE, parent=lower_board, child=upper_board,
            origin=Origin(xyz=(_PIVOT_X, 0.0, upper_z)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=28.0, velocity=1.4, lower=0.0, upper=_BOARD_CLOSE_ANGLE),
            meta={"motion": "positive motion closes the handles and compresses the bellows"},
        )
        for (fold, rest_z), (_n, _rz, _h, _s0, _s1, ratio) in zip(bellows_parts, folds_spec):
            model.articulation(
                f"{fold.name}_compression", ArticulationType.REVOLUTE,
                parent=lower_board, child=fold,
                origin=Origin(xyz=(_PIVOT_X, 0.0, rest_z)), axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(
                    effort=8.0, velocity=1.4, lower=0.0, upper=_BOARD_CLOSE_ANGLE * ratio
                ),
                mimic=Mimic(joint=board_pivot.name, multiplier=ratio),
                meta={"motion": "derived accordion-fold compression"},
            )

    model.articulation(
        "intake_hinge", ArticulationType.REVOLUTE, parent=lower_board, child=intake_flap,
        origin=Origin(xyz=(-0.020, 0.017, -0.009), rpy=(0.32, 0.0, 0.0)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.4, velocity=5.0, lower=-0.24, upper=0.55),
        meta={"motion": "one-way leather valve opens away from the intake hole"},
    )


# =========================================================================== #
# RUBBER_BULB family (S7).
# =========================================================================== #

_BULB_MAX_R = 0.030
_BULB_POLAR = 0.045
_INTAKE_R = 0.010
_INTAKE_X = 0.020
_SQUEEZE_X = 0.015
_WALL = 0.006


def _cyl_z(radius: float, length: float, center=(0.0, 0.0, 0.0)):
    return (
        cq.Workplane("XY").circle(radius).extrude(length / 2.0, both=True).translate(center)
    )


def _ovoid_x(equatorial_r: float, polar_half: float):
    """Revolved ovoid with its axial axis along X (S6/S7 pattern; ovoid_pod_y rotated)."""
    n = 16
    pts = [
        (equatorial_r * math.sin(math.pi * i / n), polar_half * math.cos(math.pi * i / n))
        for i in range(n + 1)
    ]
    profile = cq.Workplane("XY").spline(pts).close()
    pod = profile.revolve(360, (0.0, -polar_half), (0.0, polar_half))
    return pod.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 90.0)


def _bulb_shell():
    """Hollow ovoid rubber bulb shell (axial X) with intake + squeeze openings (S7)."""
    outer = _ovoid_x(_BULB_MAX_R, _BULB_POLAR)
    inner = _ovoid_x(_BULB_MAX_R - _WALL, _BULB_POLAR - _WALL)
    shell = outer.cut(inner)
    # Intake hole on the bottom (-Z), not through the top.
    shell = shell.cut(_cyl_z(_INTAKE_R, 0.040, center=(_INTAKE_X, 0.0, -0.020)))
    # The squeeze wall is a raised pad seated ON the intact top surface (it
    # presses inward), so no window is cut — that keeps the pad in real contact.
    return shell


def _intake_ring():
    """Reinforcing ring around the intake hole (S7 _intake_ring)."""
    return _cyl_z(_INTAKE_R + 0.004, 0.004, center=(_INTAKE_X, 0.0, -_BULB_MAX_R + 0.005)).cut(
        _cyl_z(_INTAKE_R, 0.008, center=(_INTAKE_X, 0.0, -_BULB_MAX_R + 0.005))
    )


def _bulb_nozzle_tube():
    """Tapered brass nozzle extending -X from the bulb throat (S7 _nozzle_tube)."""
    outer = (
        cq.Workplane("YZ").workplane(offset=-0.085).circle(0.0075)
        .workplane(offset=0.050).circle(0.0140).loft(combine=True)
    )
    inner = (
        cq.Workplane("YZ").workplane(offset=-0.088).circle(0.0050)
        .workplane(offset=0.056).circle(0.0105).loft(combine=True)
    )
    return outer.cut(inner)


def _bulb_nozzle_rim():
    return cq.Workplane("YZ").workplane(offset=-0.086).circle(0.0100).circle(0.0060).extrude(0.005)


def _bulb_nozzle_collar():
    return _cyl_x(0.0150, 0.010, center=(-0.030, 0.0, 0.0)).cut(
        _cyl_x(0.0120, 0.014, center=(-0.030, 0.0, 0.0))
    )


def _squeeze_panel():
    """Movable rubber squeeze wall, centered at local origin (S7 _squeeze_panel).

    Slightly larger than the bulb squeeze window (0.028 x 0.024) so its rim rests
    on the surrounding wall (real contact, not floating inside the opening).
    """
    return (
        cq.Workplane("XY").rect(0.034, 0.030)
        .workplane(offset=0.012).rect(0.030, 0.026).loft(combine=True)
    )


def _build_rubber_bulb(model, r, mats):
    body_mat = mats["body"]
    accent = mats["accent"]
    metal = mats["metal"]
    detail = mats["detail"]
    travel = _clamp(0.011 * r.squeeze_travel_scale, 0.008, 0.015)

    bulb_body = model.part("bulb_body", meta={"construction": "hollow ovoid rubber bulb"})
    bulb_body.visual(
        mesh_from_cadquery(_bulb_shell(), "bulb_shell", tolerance=0.0007),
        material=body_mat, name="bulb_shell", material_class_id="rubber.smooth_plain",
    )
    bulb_body.visual(
        mesh_from_cadquery(_intake_ring(), "intake_ring"), material=accent, name="intake_ring", material_class_id="metal.blackened_gunmetal",
    )
    bulb_body.visual(
        mesh_from_cadquery(_bulb_nozzle_tube(), "bulb_nozzle"),
        material=metal, name="nozzle_shell", material_class_id="metal.brass_polished",
    )
    bulb_body.visual(
        mesh_from_cadquery(_bulb_nozzle_rim(), "bulb_nozzle_rim"),
        material=detail, name="nozzle_rim", material_class_id="metal.brass_aged",
    )
    bulb_body.visual(
        mesh_from_cadquery(_bulb_nozzle_collar(), "bulb_nozzle_collar"),
        material=detail, name="nozzle_collar", material_class_id="metal.brass_aged",
    )
    bulb_body.visual(
        Cylinder(radius=_BULB_MAX_R + 0.0005, length=0.001),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=accent, name="mold_seam", material_class_id="rubber.smooth_plain",
    )
    bulb_body.inertial = Inertial.from_geometry(Box((2 * _BULB_POLAR, 0.06, 0.06)), mass=0.08)

    # Slot B bulb_squeeze: movable top wall (PRISMATIC -Z). Grip = ribs (Slot E).
    # The part link frame sits at the joint origin (bulb top); visuals are
    # authored RELATIVE to it (the pad embeds 12 mm down into the shell wall).
    squeeze_wall = model.part("squeeze_wall", meta={"construction": "movable squeeze wall"})
    squeeze_wall.visual(
        mesh_from_cadquery(_squeeze_panel(), "squeeze_panel"),
        origin=Origin(xyz=(0.0, 0.0, -0.012)),
        material=accent, name="squeeze_panel", material_class_id="rubber.smooth_plain",
    )
    for i, dx in enumerate((-0.006, 0.0, 0.006)):
        squeeze_wall.visual(
            Box((0.002, 0.014, 0.002)),
            origin=Origin(xyz=(dx, 0.0, -0.0005)),
            material=body_mat, name=f"grip_rib_{i}", material_class_id="rubber.pebbled",
        )
    squeeze_wall.inertial = Inertial.from_geometry(Box((0.03, 0.026, 0.006)), mass=0.006)
    model.articulation(
        "bulb_squeeze", ArticulationType.PRISMATIC, parent=bulb_body, child=squeeze_wall,
        origin=Origin(xyz=(_SQUEEZE_X, 0.0, _BULB_MAX_R), rpy=(0.0, 0.0, 0.0)), axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=40.0, velocity=0.5, lower=0.0, upper=travel),
        meta={"motion": "squeeze wall moves inward (compresses bulb volume)"},
    )

    intake_flap = model.part("intake_flap", meta={"construction": "one-way rubber valve"})
    intake_flap.visual(
        Cylinder(radius=_INTAKE_R + 0.001, length=0.0015),
        origin=Origin(xyz=(0.0, -_INTAKE_R, 0.0)), material=accent, name="flap_leaf", material_class_id="rubber.smooth_plain",
    )
    intake_flap.visual(
        Cylinder(radius=0.0025, length=0.020), origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal, name="flap_hinge", material_class_id="metal.steel_bare",
    )
    intake_flap.inertial = Inertial.from_geometry(Box((0.022, 0.022, 0.004)), mass=0.003)
    model.articulation(
        "intake_hinge", ArticulationType.REVOLUTE, parent=bulb_body, child=intake_flap,
        origin=Origin(xyz=(_INTAKE_X, 0.0, -_BULB_MAX_R + 0.003), rpy=(0.30, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.4, velocity=5.0, lower=-0.20, upper=0.50),
        meta={"motion": "one-way valve opens away from the intake hole"},
    )


# --------------------------------------------------------------------------- #
# Top-level build.
# --------------------------------------------------------------------------- #


def build_pictureX_0611_Air_blower(
    config: PictureX0611AirBlowerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or PictureX0611AirBlowerConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-air-blower-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]
    mats = _materials(model, r)

    if r.body_form == "bellows_boards":
        _build_bellows_boards(model, r, mats)
    elif r.body_form == "rubber_bulb":
        _build_rubber_bulb(model, r, mats)
    else:
        _build_blower(model, r, mats)
    return model


def build_seeded_pictureX_0611_Air_blower(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_Air_blower(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices.
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedPictureX0611AirBlowerConfig):
    choices = [
        ("body_form", r.body_form),
        ("motion_mechanism", r.motion_mechanism),
        ("outlet", r.outlet),
        ("intake", r.intake),
        ("grip", r.grip),
        ("palette_style", r.palette_style),
    ]
    if r.family == "blower":
        choices.append(("fan_blade_count", str(r.fan_blade_count)))
    elif r.body_form == "bellows_boards":
        choices.append(("bellows_fold_count", str(r.bellows_fold_count)))
    return tuple(choices)


def slot_choices_for_seed(seed: int):
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _declare_blower_allowances(ctx, model, r):
    housing = model.get_part("housing")
    nozzle = model.get_part("nozzle")
    crank = model.get_part("crank")
    drive_shaft = model.get_part("drive_shaft")
    fan_rotor = model.get_part("fan_rotor")

    # Nozzle tube/sleeve/ring captured in the tangential outlet throat (pin-in-sleeve).
    for elem in ("metal_tube", "base_sleeve", "retaining_ring"):
        for host in ("outlet_socket", "main_body"):
            ctx.allow_overlap(
                nozzle, housing, elem_a=elem, elem_b=host,
                reason="Nozzle is inserted/retained in the outlet throat + tangential passage.",
            )
    # Coaxial captured drivetrain: shaft in crank hub + drive collar keyed in fan hub.
    ctx.allow_overlap(
        drive_shaft, crank, elem_a="drive_shaft", elem_b="crank_hub",
        reason="Metal shaft is captured inside the crank hub.",
    )
    ctx.allow_overlap(
        drive_shaft, fan_rotor, elem_a="drive_collar", elem_b="fan_hub",
        reason="Keyed drive collar engages the fan wheel hub.",
    )
    # Shaft + fan hub ride inside the open casing cavity (journal bearing).
    for part, elem in (
        (drive_shaft, "drive_shaft"), (drive_shaft, "drive_collar"),
        (fan_rotor, "fan_hub"), (fan_rotor, "fan_wheel"),
    ):
        ctx.allow_overlap(
            part, housing, elem_a=elem, elem_b="main_body",
            reason="Rotating drivetrain spins inside the casing cavity (journal fit).",
        )
    ctx.allow_overlap(
        crank, housing, elem_a="crank_hub", elem_b="main_body",
        reason="Crank hub seats against the front bearing boss of the casing.",
    )


def _declare_bellows_allowances(ctx, model, r):
    lower = model.get_part("lower_board")
    upper = model.get_part("upper_board")
    folds = [model.get_part(name) for name, *_ in _make_folds(r.bellows_fold_count, r.chamber_scale)[0]]

    for fold in folds:
        ctx.allow_overlap(
            fold, lower, elem_a="fold_shell", elem_b="bellows_lower_collar",
            reason="Accordion folds overlap the fixed lower leather collar during compression.",
        )
    # Every fold pair may interpenetrate as the whole accordion telescopes shut.
    for i in range(len(folds)):
        for j in range(i + 1, len(folds)):
            ctx.allow_overlap(
                folds[i], folds[j], elem_a="fold_shell", elem_b="fold_shell",
                reason="Leather folds telescope into each other during compression.",
            )
    for fold in folds:
        ctx.allow_overlap(
            fold, lower, elem_a="fold_shell", elem_b="nozzle_shell",
            reason="The brass nozzle is inserted into the leather bellows throat.",
        )
        for index in range(2):
            ctx.allow_overlap(
                fold, lower, elem_a="fold_shell", elem_b=f"hinge_support_{index}",
                reason="Leather bellows body wraps the fixed rear neck block.",
            )
    for index in range(2):
        ctx.allow_overlap(
            upper, lower, elem_a="pivot_pin", elem_b=f"hinge_barrel_{index}",
            reason="Cross-pin is captured inside the brass pivot barrel.",
        )
        ctx.allow_overlap(
            upper, lower, elem_a="wood_panel", elem_b=f"hinge_support_{index}",
            reason="Upper board descends over the rear neck block as the chamber compresses.",
        )
        ctx.allow_overlap(
            upper, lower, elem_a="pivot_pin", elem_b=f"hinge_support_{index}",
            reason="Cross-pin rides down through the neck block on the foot-pump stroke.",
        )
    # On the foot-pump (prismatic) stroke the whole upper board (incl. cross-pin)
    # descends over the fixed collar/nozzle chamber.
    for elem in ("bellows_lower_collar", "nozzle_shell"):
        ctx.allow_overlap(
            upper, lower, elem_a="pivot_pin", elem_b=elem,
            reason="Cross-pin descends over the fixed chamber collar/nozzle during the stroke.",
        )
    # As the boards squeeze together the upper board telescopes over the fixed
    # collar / nozzle / folds (the compression stroke).
    for elem in ("bellows_lower_collar", "nozzle_shell"):
        ctx.allow_overlap(
            upper, lower, elem_a="wood_panel", elem_b=elem,
            reason="Upper board closes over the fixed chamber collar/nozzle during squeeze.",
        )
    for fold in folds:
        ctx.allow_overlap(
            upper, fold, elem_a="wood_panel", elem_b="fold_shell",
            reason="Upper board presses onto the accordion folds during compression.",
        )
    flap = model.get_part("intake_flap")
    for elem in ("flap_hinge", "flap_leaf"):
        ctx.allow_overlap(
            flap, lower, elem_a=elem, elem_b="wood_panel",
            reason="Intake flap hinge/leaf is captured at the board intake opening.",
        )


def _declare_bulb_allowances(ctx, model, r):
    bulb = model.get_part("bulb_body")
    squeeze = model.get_part("squeeze_wall")
    flap = model.get_part("intake_flap")
    ctx.allow_overlap(
        bulb, bulb, elem_a="nozzle_shell", elem_b="nozzle_collar",
        reason="Nozzle collar seats against the bulb throat wall.",
    )
    ctx.allow_overlap(
        squeeze, bulb, elem_a="squeeze_panel", elem_b="bulb_shell",
        reason="Squeeze wall seats in the bulb top window and presses inward.",
    )
    # One-way intake flap hinge pin + leaf are captured against the bulb intake.
    for elem, host in (
        ("flap_hinge", "bulb_shell"), ("flap_leaf", "bulb_shell"),
        ("flap_leaf", "intake_ring"), ("flap_hinge", "intake_ring"),
    ):
        ctx.allow_overlap(
            flap, bulb, elem_a=elem, elem_b=host,
            reason="Intake flap hinge/leaf is captured at the bulb intake opening.",
        )


def run_pictureX_0611_Air_blower_tests(
    object_model: ArticulatedObject, config: PictureX0611AirBlowerConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}

    # --- Identity: >= 1 real non-FIXED joint driving the air-mover ---------- #
    independent = [
        j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED and j.mimic is None
    ]
    ctx.check(
        "at least one real non-fixed air-mover joint",
        len(independent) >= 1,
        details=f"independent joints={[j.name for j in independent]}",
    )
    ctx.check(
        "slot_choices match resolved family",
        slot_choices_for_config(r)[0] == ("body_form", r.body_form),
        details=str(slot_choices_for_config(r)),
    )

    if r.family == "blower":
        _declare_blower_allowances(ctx, object_model, r)
        housing = object_model.get_part("housing")
        crank_j = object_model.get_articulation("housing_to_crank")
        rotor_j = object_model.get_articulation("housing_to_rotor")
        nozzle_j = object_model.get_articulation("housing_to_nozzle")
        ctx.check(
            "single supported root housing",
            [p.name for p in object_model.root_parts()] == ["housing"],
            details=str([p.name for p in object_model.root_parts()]),
        )
        ctx.check(
            "crank drives a CONTINUOUS impeller about +Y",
            crank_j.articulation_type == ArticulationType.CONTINUOUS
            and abs(crank_j.axis[1]) > 0.99
            and rotor_j.articulation_type == ArticulationType.CONTINUOUS
            and rotor_j.mimic is not None and rotor_j.mimic.joint == "housing_to_crank",
            details=f"crank={crank_j.axis}, rotor_mimic={rotor_j.mimic}",
        )
        ctx.check(
            "outlet twist is REVOLUTE about +X",
            nozzle_j.articulation_type == ArticulationType.REVOLUTE and abs(nozzle_j.axis[0]) > 0.99,
            details=f"axis={nozzle_j.axis}",
        )
        crank = object_model.get_part("crank")
        fan_rotor = object_model.get_part("fan_rotor")
        ctx.expect_within(
            fan_rotor, housing, axes="xz", inner_elem="fan_wheel", outer_elem="main_body",
            margin=0.0, name="fan wheel fits inside the casing",
        )
        # targeted motion: crank quarter turn sweeps the handle around the axis.
        rest = ctx.part_world_aabb(crank)
        with ctx.pose({crank_j: math.pi / 2.0}):
            turned = ctx.part_world_aabb(crank)
        rc = tuple((rest[0][i] + rest[1][i]) / 2.0 for i in range(3))
        tc = tuple((turned[0][i] + turned[1][i]) / 2.0 for i in range(3))
        ctx.check(
            "crank quarter turn moves the handle around the axis",
            math.dist(rc, tc) > 0.04, details=f"rest={rc}, turned={tc}",
        )
        # targeted motion: nozzle twist reorients the adjustment rib.
        rest_n = ctx.part_element_world_aabb(object_model.get_part("nozzle"), elem="adjustment_rib")
        with ctx.pose({nozzle_j: 0.30}):
            adj_n = ctx.part_element_world_aabb(object_model.get_part("nozzle"), elem="adjustment_rib")
        ctx.check(
            "nozzle twist reorients the outlet rib",
            rest_n is not None and adj_n is not None
            and (abs(rest_n[0][1] - adj_n[0][1]) > 0.002 or abs(rest_n[0][2] - adj_n[0][2]) > 0.002),
            details=f"rest={rest_n}, adjusted={adj_n}",
        )

    elif r.body_form == "bellows_boards":
        _declare_bellows_allowances(ctx, object_model, r)
        lower = object_model.get_part("lower_board")
        upper = object_model.get_part("upper_board")
        flap = object_model.get_part("intake_flap")
        pivot = object_model.get_articulation("board_pivot")
        flap_j = object_model.get_articulation("intake_hinge")
        ctx.check(
            "single supported root lower_board",
            [p.name for p in object_model.root_parts()] == ["lower_board"],
            details=str([p.name for p in object_model.root_parts()]),
        )
        expect_type = (
            ArticulationType.PRISMATIC if r.motion_mechanism == "foot_pump"
            else ArticulationType.REVOLUTE
        )
        ctx.check(
            "bellows squeeze joint has the family-correct type",
            pivot.articulation_type == expect_type,
            details=f"type={pivot.articulation_type}, expected={expect_type}",
        )
        fold_joints = [
            object_model.get_articulation(f"bellows_fold_{i}_compression")
            for i in range(r.bellows_fold_count)
        ]
        ctx.check(
            "every accordion fold mimics the board pivot",
            all(j.mimic is not None and j.mimic.joint == "board_pivot" for j in fold_joints),
            details=f"folds={[j.name for j in fold_joints]}",
        )
        # targeted motion: driving the pivot lowers the upper board.
        rest_u = ctx.part_element_world_aabb(upper, elem="wood_panel")
        drive_q = pivot.motion_limits.lower if r.motion_mechanism == "foot_pump" else pivot.motion_limits.upper
        with ctx.pose({pivot: drive_q}):
            moved_u = ctx.part_element_world_aabb(upper, elem="wood_panel")
        rest_cz = 0.5 * (rest_u[0][2] + rest_u[1][2])
        moved_cz = 0.5 * (moved_u[0][2] + moved_u[1][2])
        ctx.check(
            "driving the bellows lowers the upper board",
            moved_cz < rest_cz - 0.010, details=f"rest_cz={rest_cz}, moved_cz={moved_cz}",
        )
        # targeted motion: intake flap opens away from the board.
        rest_f = ctx.part_element_world_aabb(flap, elem="flap_leaf")
        with ctx.pose({flap_j: 0.45}):
            open_f = ctx.part_element_world_aabb(flap, elem="flap_leaf")
        ctx.check(
            "intake flap opens away from the board",
            0.5 * (open_f[0][2] + open_f[1][2]) < 0.5 * (rest_f[0][2] + rest_f[1][2]) - 0.003,
            details=f"rest={rest_f}, open={open_f}",
        )

    else:  # rubber_bulb
        _declare_bulb_allowances(ctx, object_model, r)
        bulb = object_model.get_part("bulb_body")
        squeeze = object_model.get_part("squeeze_wall")
        flap = object_model.get_part("intake_flap")
        sq_j = object_model.get_articulation("bulb_squeeze")
        flap_j = object_model.get_articulation("intake_hinge")
        ctx.check(
            "single supported root bulb_body",
            [p.name for p in object_model.root_parts()] == ["bulb_body"],
            details=str([p.name for p in object_model.root_parts()]),
        )
        ctx.check(
            "bulb squeeze is PRISMATIC about -Z",
            sq_j.articulation_type == ArticulationType.PRISMATIC and abs(sq_j.axis[2] + 1.0) < 0.02,
            details=f"type={sq_j.articulation_type}, axis={sq_j.axis}",
        )
        rest_s = ctx.part_element_world_aabb(squeeze, elem="squeeze_panel")
        with ctx.pose({sq_j: sq_j.motion_limits.upper}):
            sq_s = ctx.part_element_world_aabb(squeeze, elem="squeeze_panel")
        ctx.check(
            "squeeze wall moves inward (Z decreases)",
            0.5 * (sq_s[0][2] + sq_s[1][2]) < 0.5 * (rest_s[0][2] + rest_s[1][2]) - 0.006,
            details=f"rest={rest_s}, squeezed={sq_s}",
        )
        rest_f = ctx.part_element_world_aabb(flap, elem="flap_leaf")
        with ctx.pose({flap_j: 0.40}):
            open_f = ctx.part_element_world_aabb(flap, elem="flap_leaf")
        ctx.check(
            "intake flap opens away from the bulb",
            0.5 * (open_f[0][2] + open_f[1][2]) < 0.5 * (rest_f[0][2] + rest_f[1][2]) - 0.002,
            details=f"rest={rest_f}, open={open_f}",
        )

    # --- Palette drives every material role -------------------------------- #
    ctx.check(
        "palette_style resolved to a known colorway",
        r.palette_style in PALETTES, details=r.palette_style,
    )

    # --- Rule 5: full-range sampled-pose overlap sweep --------------------- #
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "BodyForm",
    "Motion",
    "Outlet",
    "Intake",
    "Grip",
    "PaletteStyle",
    "PictureX0611AirBlowerConfig",
    "ResolvedPictureX0611AirBlowerConfig",
    "build_pictureX_0611_Air_blower",
    "build_seeded_pictureX_0611_Air_blower",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_pictureX_0611_Air_blower_tests",
    "__modular__",
]
