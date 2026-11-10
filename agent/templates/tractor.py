# SPDX-License-Identifier: Apache-2.0

"""Agricultural / Tractor modular parametric template.

A farm TRACTOR: a rolling traction chassis with **large rear wheels + smaller
front wheels** (rear tire Ø > 1.55x front), a long engine hood in front, a
radiator grille, a vertical exhaust stack, an operator station at the rear, and
a rear implement. Kinematics: **every wheel spins on its own real axle
(CONTINUOUS)**, the **front axle / steering mechanism pivots about a vertical
pin (REVOLUTE, mimicking the rotating steering wheel)**, and the rear implement
(3-point hitch lift / front-loader boom+curl / towed-trailer yaw) is REVOLUTE.

Sourced from spec ``specs_modular_v1/tractor.md`` and the 5-star pool
(2 origins + 6 slot-fork variants), all under ``data/records/``:

  * ``operator_station`` (3): enclosed_cab (A) / open_bare (B) / open_ROPS (rops var)
  * ``front_axle`` (3): wide_standard (B) / narrow_tricycle (tricycle var) /
    single_front (singlefront var — 1 centered wheel in a steering yoke; 4->3 wheels)
  * ``implement`` (4): plain_drawbar (A/B inline) / three_point_hitch (B) /
    front_loader (loader var) / towed_trailer (A)
  * ``hood_form`` (3, ③ Primary Form Family / Volumetric Envelope): long_flat (B) /
    rounded_vintage (roundhood var, cadquery) / stepped_modern (world-knowledge
    extrapolation — same part tree/primitive/mount, stepped wedge envelope)
  * ``n_grille_slats`` (N in [4,16]): FIXED vertical grille slats inlined on the
    grille panel (Rule 1), N encoded in the slot_choice tuple.

Structure (pattern = ``mixed``): single root ``chassis`` part; the station /
hood / grille slats are inline chassis visuals (Rule 1, non-moving). The front
axle is a REVOLUTE child of the chassis carrying its front wheel(s) as
CONTINUOUS children; rear wheels are CONTINUOUS children of the chassis; the
implement adds an optional child part (hitch / loader boom+bucket / trailer).
A separate rotating ``steering_wheel`` part is always present; the front steer
joint mimics ``steering_wheel_turn``. All wheel spins mimic the rear driver so
the wheels roll together (each still on its own axle joint).

All axle-in-hub / pivot-in-casting / hitch-pin joints are captured-pin geometry,
so those joints omit ``MatingContract`` (grandfathered) and are guarded by the
flat articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring
each source record's run_tests block). Wheels/tires ALWAYS use
``TireGeometry``/``WheelGeometry``/``BoltPattern`` (Rule 3, never Box/Cylinder).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BoltPattern,
    Box,
    Cylinder,
    Material,
    MeshGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireShoulder,
    TireSidewall,
    TireTread,
    TorusGeometry,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

OperatorStation = Literal["enclosed_cab", "open_bare", "open_ROPS"]
FrontAxle = Literal["wide_standard", "narrow_tricycle", "single_front"]
Implement = Literal["plain_drawbar", "three_point_hitch", "front_loader", "towed_trailer"]
HoodForm = Literal["long_flat", "rounded_vintage", "stepped_modern"]
PaletteStyle = Literal[
    "jd_green",
    "belarus_blue",
    "massey_red",
    "kubota_orange",
    "newholland_blue",
    "vintage_grey",
]

OPERATOR_STATIONS: tuple[OperatorStation, ...] = ("enclosed_cab", "open_bare", "open_ROPS")
FRONT_AXLES: tuple[FrontAxle, ...] = ("wide_standard", "narrow_tricycle", "single_front")
IMPLEMENTS: tuple[Implement, ...] = (
    "plain_drawbar",
    "three_point_hitch",
    "front_loader",
    "towed_trailer",
)
HOOD_FORMS: tuple[HoodForm, ...] = ("long_flat", "rounded_vintage", "stepped_modern")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "jd_green",
    "belarus_blue",
    "massey_red",
    "kubota_orange",
    "newholland_blue",
    "vintage_grey",
)

N_MIN = 4
N_MAX = 16
# Grille-slat N sampling: small N high-frequency, large N rare (spec §8).
_N_VALUES = tuple(range(N_MIN, N_MAX + 1))
_N_WEIGHTS = tuple(max(1.0, 14.0 - (n - N_MIN) * 1.6) for n in _N_VALUES)

# ---------------------------------------------------------------------------
# Palettes (⑥). body/body2/accent/rim vary per make; the rest are shared.
# ---------------------------------------------------------------------------
_COMMON_MATS: dict[str, tuple[float, float, float, float]] = {
    "tire": (0.02, 0.02, 0.02, 1.0),
    "metal": (0.45, 0.46, 0.42, 1.0),
    "dark_metal": (0.08, 0.09, 0.08, 1.0),
    "glass": (0.65, 0.83, 0.90, 0.4),
    "chrome": (0.78, 0.78, 0.72, 1.0),
    "exhaust": (0.20, 0.22, 0.21, 1.0),
    "wood": (0.28, 0.22, 0.17, 1.0),
    "amber": (1.0, 0.58, 0.12, 1.0),
}
_PALETTE_BODY: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "jd_green": {
        "body": (0.02, 0.48, 0.13, 1.0),
        "body2": (0.01, 0.22, 0.08, 1.0),
        "accent": (0.93, 0.86, 0.52, 1.0),
        "rim": (0.93, 0.86, 0.18, 1.0),
    },
    "belarus_blue": {
        "body": (0.18, 0.38, 0.55, 1.0),
        "body2": (0.07, 0.16, 0.27, 1.0),
        "accent": (0.78, 0.82, 0.86, 1.0),
        "rim": (0.58, 0.13, 0.10, 1.0),
    },
    "massey_red": {
        "body": (0.62, 0.10, 0.09, 1.0),
        "body2": (0.30, 0.05, 0.05, 1.0),
        "accent": (0.76, 0.77, 0.74, 1.0),
        "rim": (0.80, 0.80, 0.78, 1.0),
    },
    "kubota_orange": {
        "body": (0.86, 0.42, 0.05, 1.0),
        "body2": (0.44, 0.20, 0.02, 1.0),
        "accent": (0.16, 0.16, 0.16, 1.0),
        "rim": (0.80, 0.80, 0.78, 1.0),
    },
    "newholland_blue": {
        "body": (0.10, 0.28, 0.55, 1.0),
        "body2": (0.05, 0.14, 0.30, 1.0),
        "accent": (0.92, 0.92, 0.90, 1.0),
        "rim": (0.74, 0.75, 0.73, 1.0),
    },
    "vintage_grey": {
        "body": (0.52, 0.53, 0.50, 1.0),
        "body2": (0.29, 0.30, 0.28, 1.0),
        "accent": (0.46, 0.13, 0.10, 1.0),
        "rim": (0.56, 0.15, 0.11, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). X forward, Y across axle, Z up. Ground
# at z=0 (tire bottoms rest at 0).
# ---------------------------------------------------------------------------
_REAR_R = 0.58  # base rear tire radius
_HOOD_CX = 0.56  # hood center X
_HOOD_LEN = 1.72
_HOOD_W = 0.58
_HOOD_H = 0.42
_HOOD_Z = 1.02  # hood body center Z
_GRILLE_Z = 0.98
_GRILLE_PANEL = (0.090, 0.60, 0.50)  # (x,y,z)
_FRONT_PIVOT_X = 1.28
_REAR_AXLE_X = -1.02
_WIDE_TRACK_Y = 0.66  # wide front half-track
_REAR_TRACK_Y = 0.80  # rear half-track (wide enough to clear the cab side glass)
# The block/rib lugs protrude past the tire `radius`, so wheel centers ride a
# little higher than `radius` to keep the lug bottoms on the ground plane.
_REAR_TIRE_LIFT = 0.030
_FRONT_TIRE_LIFT = 0.012


@dataclass(frozen=True)
class TractorConfig:
    operator_station: OperatorStation | None = None
    front_axle: FrontAxle | None = None
    implement: Implement | None = None
    hood_form: HoodForm | None = None
    n_grille_slats: int | None = None
    palette_style: PaletteStyle = "jd_green"
    rear_wheel_scale: float = 1.0
    front_wheel_frac: float = 0.52
    wheelbase_scale: float = 1.0
    rear_track_scale: float = 1.0
    front_track_scale: float = 1.0
    hood_length_scale: float = 1.0
    steer_limit_scale: float = 1.0
    hitch_lift_scale: float = 1.0
    loader_range_scale: float = 1.0
    name: str = "tractor"


@dataclass(frozen=True)
class ResolvedTractorConfig:
    operator_station: OperatorStation
    front_axle: FrontAxle
    implement: Implement
    hood_form: HoodForm
    n_grille_slats: int
    palette_style: PaletteStyle
    # Derived geometry.
    rear_r: float
    front_r: float
    rear_w: float
    front_w: float
    rear_rim_r: float
    front_rim_r: float
    front_pivot_x: float
    front_pivot_z: float
    rear_axle_x: float
    rear_track_y: float
    front_track_y: float
    hood_len: float
    hood_front_x: float
    grille_x: float
    steer_limit: float
    hitch_lift_scale: float
    loader_range_scale: float
    name: str


def _single_front_radius(front_r: float) -> float:
    """Single centered front wheel: capped so its raised steer yoke clears the hood."""
    return min(front_r, 0.26)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


def config_from_seed(seed: int) -> TractorConfig:
    rng = random.Random(seed)
    return TractorConfig(
        operator_station=rng.choice(OPERATOR_STATIONS),
        front_axle=rng.choice(FRONT_AXLES),
        implement=rng.choice(IMPLEMENTS),
        hood_form=rng.choice(HOOD_FORMS),
        n_grille_slats=rng.choices(_N_VALUES, weights=_N_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        rear_wheel_scale=round(rng.uniform(0.88, 1.12), 4),
        front_wheel_frac=round(rng.uniform(0.48, 0.56), 4),
        wheelbase_scale=round(rng.uniform(0.93, 1.07), 4),
        rear_track_scale=round(rng.uniform(0.92, 1.08), 4),
        front_track_scale=round(rng.uniform(0.92, 1.08), 4),
        hood_length_scale=round(rng.uniform(0.85, 1.15), 4),
        steer_limit_scale=round(rng.uniform(0.85, 1.10), 4),
        hitch_lift_scale=round(rng.uniform(0.85, 1.12), 4),
        loader_range_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_tractor_{seed}",
    )


def resolve_config(config: TractorConfig | None = None) -> ResolvedTractorConfig:
    cfg = config or TractorConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    station = _pick(cfg.operator_station, OPERATOR_STATIONS)
    front_axle = _pick(cfg.front_axle, FRONT_AXLES)
    implement = _pick(cfg.implement, IMPLEMENTS)
    hood_form = _pick(cfg.hood_form, HOOD_FORMS)

    n = int(cfg.n_grille_slats) if cfg.n_grille_slats is not None else 10
    n = int(_clamp(n, N_MIN, N_MAX))

    rear_scale = _clamp(cfg.rear_wheel_scale, 0.88, 1.12)
    front_frac = _clamp(cfg.front_wheel_frac, 0.48, 0.56)
    wb = _clamp(cfg.wheelbase_scale, 0.93, 1.07)
    rear_track_s = _clamp(cfg.rear_track_scale, 0.92, 1.08)
    front_track_s = _clamp(cfg.front_track_scale, 0.92, 1.08)
    hood_len_s = _clamp(cfg.hood_length_scale, 0.85, 1.15)
    steer_s = _clamp(cfg.steer_limit_scale, 0.85, 1.10)

    # --- Wheel dims (single-sourced; equation: front derived from rear). ---
    rear_r = _REAR_R * rear_scale
    front_r = rear_r * front_frac  # ratio 1/front_frac in [1.79, 2.08] > 1.55
    rear_w = rear_r * 0.586
    front_w = front_r * 0.533
    rear_rim_r = rear_r * 0.569
    front_rim_r = front_r * 0.667
    # Steer-axis frame origin height. wide/tricycle drop the wheel 0.10 below the
    # pivot. The single-front yoke must sit its kingpin above the (capped) wheel
    # top yet below the hood underside, so it uses a smaller dedicated wheel.
    if front_axle == "single_front":
        sf_r = _single_front_radius(front_r)
        front_pivot_z = 2.0 * sf_r + _FRONT_TIRE_LIFT + 0.05
    else:
        front_pivot_z = front_r + _FRONT_TIRE_LIFT + 0.10

    rear_axle_x = _REAR_AXLE_X * wb
    front_pivot_x = _FRONT_PIVOT_X * wb
    rear_track_y = _REAR_TRACK_Y * rear_track_s

    # front track: only wide_standard varies; tricycle close-coupled (but spaced
    # so the two front tires clear each other + the center pin); single centered.
    front_w = (rear_r * front_frac) * 0.533
    if front_axle == "wide_standard":
        front_track_y = _WIDE_TRACK_Y * front_track_s
    elif front_axle == "narrow_tricycle":
        front_track_y = front_w / 2.0 + 0.09
    else:
        front_track_y = 0.0

    # --- Front-steer clearance (inequality): steered front wheels must clear the
    #     hood/body. For wide/tricycle the wheel must be outboard of the hood
    #     half-width so a ±steer swing never enters the body. Push the track out
    #     if too narrow. ---
    hood_half = _HOOD_W / 2.0
    if front_axle == "wide_standard":
        front_track_y = max(front_track_y, hood_half + front_r + 0.06)

    hood_len = _HOOD_LEN * hood_len_s
    hood_front_x = _HOOD_CX + hood_len / 2.0
    grille_x = hood_front_x + 0.01

    steer_limit = _clamp(0.45 * steer_s, 0.30, 0.52)

    return ResolvedTractorConfig(
        operator_station=station,
        front_axle=front_axle,
        implement=implement,
        hood_form=hood_form,
        n_grille_slats=n,
        palette_style=palette_style,
        rear_r=rear_r,
        front_r=front_r,
        rear_w=rear_w,
        front_w=front_w,
        rear_rim_r=rear_rim_r,
        front_rim_r=front_rim_r,
        front_pivot_x=front_pivot_x,
        front_pivot_z=front_pivot_z,
        rear_axle_x=rear_axle_x,
        rear_track_y=rear_track_y,
        front_track_y=front_track_y,
        hood_len=hood_len,
        hood_front_x=hood_front_x,
        grille_x=grille_x,
        steer_limit=steer_limit,
        hitch_lift_scale=_clamp(cfg.hitch_lift_scale, 0.85, 1.12),
        loader_range_scale=_clamp(cfg.loader_range_scale, 0.85, 1.10),
        name=cfg.name or "tractor",
    )


def with_overrides(config: TractorConfig, **kwargs: object) -> TractorConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: TractorConfig | ResolvedTractorConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTractorConfig) else resolve_config(config)
    return (
        ("operator_station", r.operator_station),
        ("front_axle", r.front_axle),
        ("implement", r.implement),
        ("hood_form", r.hood_form),
        ("grille_slat_count", f"n{r.n_grille_slats}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Small cylinder-orientation helpers.
# ---------------------------------------------------------------------------
def _cx(part, radius, length, xyz, material, name):
    part.visual(Cylinder(radius=radius, length=length),
                origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
                material=material, name=name, material_class_id="metal.generic_plain")


def _cy(part, radius, length, xyz, material, name):
    part.visual(Cylinder(radius=radius, length=length),
                origin=Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=material, name=name, material_class_id="metal.generic_plain")


def _cz(part, radius, length, xyz, material, name):
    part.visual(Cylinder(radius=radius, length=length),
                origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.generic_plain")


# ---------------------------------------------------------------------------
# Fender arc mesh (from B/_arc_fender_geometry L35-74). Coarsened segments.
# ---------------------------------------------------------------------------
def _arc_fender_geometry(*, inner_radius, thickness, width, start_deg, end_deg, segments=24):
    geom = MeshGeometry()
    angles = [start_deg * math.pi / 180.0 + (end_deg - start_deg) * math.pi / 180.0 * i / segments
              for i in range(segments + 1)]
    for theta in angles:
        for radius in (inner_radius, inner_radius + thickness):
            for y in (-width / 2.0, width / 2.0):
                geom.add_vertex(radius * math.cos(theta), y, radius * math.sin(theta))

    def vid(i, radial, side):
        return i * 4 + radial * 2 + side

    for i in range(segments):
        geom.add_face(vid(i, 0, 0), vid(i + 1, 0, 0), vid(i + 1, 0, 1))
        geom.add_face(vid(i, 0, 0), vid(i + 1, 0, 1), vid(i, 0, 1))
        geom.add_face(vid(i, 1, 0), vid(i, 1, 1), vid(i + 1, 1, 1))
        geom.add_face(vid(i, 1, 0), vid(i + 1, 1, 1), vid(i + 1, 1, 0))
        geom.add_face(vid(i, 0, 0), vid(i, 1, 0), vid(i + 1, 1, 0))
        geom.add_face(vid(i, 0, 0), vid(i + 1, 1, 0), vid(i + 1, 0, 0))
        geom.add_face(vid(i, 0, 1), vid(i + 1, 0, 1), vid(i + 1, 1, 1))
        geom.add_face(vid(i, 0, 1), vid(i + 1, 1, 1), vid(i, 1, 1))
    for i in (0, segments):
        geom.add_face(vid(i, 0, 0), vid(i, 0, 1), vid(i, 1, 1))
        geom.add_face(vid(i, 0, 0), vid(i, 1, 1), vid(i, 1, 0))
    return geom


# ---------------------------------------------------------------------------
# Wheel meshes (Rule 3: TireGeometry/WheelGeometry/BoltPattern; never boxes).
# Generated once per type and reused across parts to keep the compile budget.
# ---------------------------------------------------------------------------
def _wheel_meshes(prefix, *, radius, width, rim_radius, large):
    # Ag-tire tread: big block lugs on the driven rear, fine shallow block lugs up
    # front. Both use "block" so the tread stays a single connected shell on the
    # carcass belt; the "rib" style emits axially-separated circumferential bands
    # that read as disconnected-geometry islands on the front wheel part.
    # Tessellation kept cheap (block + disc wheel) to hold the compile budget;
    # chevron/split_y are ~5x slower (see spec §7.5).
    tire = TireGeometry(
        radius,
        width,
        inner_radius=rim_radius * 1.02,
        carcass=TireCarcass(belt_width_ratio=0.70, sidewall_bulge=0.08),
        tread=TireTread(
            style="block",
            depth=0.036 if large else 0.012,
            count=10 if large else 10,
            angle_deg=18.0 if large else 0.0,
            land_ratio=0.55,
        ),
        sidewall=TireSidewall(style="rounded", bulge=0.055),
        shoulder=TireShoulder(width=0.030 if large else 0.012, radius=0.010),
    )
    wheel = WheelGeometry(
        rim_radius,
        # Rim well width. The narrow front wheel needs a wider rim shell (0.80 vs
        # 0.72) or the inner bead-seat ring pinches off as a disconnected island
        # (it stays connected on the wide rear rim at 0.72). 0.78 is the connect
        # threshold across the front-scale range; 0.80 keeps margin while staying
        # below 0.88, where WheelGeometry degenerates (axial extent blows up ~2.5x
        # for some rim_radius/width combos and collides the tricycle front rims).
        width * (0.72 if large else 0.80),
        rim=WheelRim(
            inner_radius=rim_radius * 0.70,
            flange_height=0.030 if large else 0.015,
            flange_thickness=0.012,
            bead_seat_depth=0.010,
        ),
        hub=WheelHub(
            radius=rim_radius * 0.33,
            width=width * 0.54,
            cap_style="domed",
            bolt_pattern=BoltPattern(
                count=6 if large else 5,  # all-positive (never count<=0 / cd<=0)
                circle_diameter=rim_radius * 0.42,
                hole_diameter=0.018,
            ),
        ),
        face=WheelFace(dish_depth=0.018, front_inset=0.008, rear_inset=0.006),
        spokes=WheelSpokes(style="disc"),
        bore=WheelBore(style="round", diameter=rim_radius * 0.18),
    )
    return mesh_from_geometry(tire, f"{prefix}_tire"), mesh_from_geometry(wheel, f"{prefix}_rim")


def _emit_wheel(model, part_name, *, tire_mesh, rim_mesh, rim_radius, mats, add_valve=False):
    wheel = model.part(part_name)
    wheel_origin = Origin(rpy=(0.0, 0.0, math.pi / 2.0))
    wheel.visual(tire_mesh, origin=wheel_origin, material=mats["tire"], name="tire", material_class_id="rubber.directional_grooved")
    wheel.visual(rim_mesh, origin=wheel_origin, material=mats["rim"], name="rim", material_class_id="metal.paint_coated")
    # Off-center valve stem on the rim so wheel rotation is visibly readable and
    # provable (Rule 1: a visual on the moving wheel part, not a FIXED-joint part).
    # Only on the rear (driver) wheels, whose sweep is clear of the front casting.
    if add_valve:
        wheel.visual(
            Cylinder(radius=rim_radius * 0.10, length=0.045),
            origin=Origin(xyz=(rim_radius * 0.82, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name="valve_stem", material_class_id="metal.stainless_matte",
        )
    return wheel


# ---------------------------------------------------------------------------
# Hood forms (③ Primary Form Family). Emitted as inline chassis visuals (Rule 1).
# ---------------------------------------------------------------------------
def _emit_hood(chassis, r: ResolvedTractorConfig, mats, *, assets):
    cx, w, h, z = _HOOD_CX, _HOOD_W, _HOOD_H, _HOOD_Z
    ln = r.hood_len
    if r.hood_form == "long_flat":
        chassis.visual(Box((ln, w, h)), origin=Origin(xyz=(cx, 0.0, z)),
                       material=mats["body"], name="hood_long_flat", material_class_id="metal.paint_coated")
        chassis.visual(Box((ln * 0.93, w * 0.72, 0.105)),
                       origin=Origin(xyz=(cx - 0.06, 0.0, z + 0.185)),
                       material=mats["body"], name="hood_raised_spine", material_class_id="metal.paint_coated")
    elif r.hood_form == "rounded_vintage":
        shape = (cq.Workplane("XY").box(ln, w, h).edges("|Z").fillet(0.090).edges(">Z").fillet(0.028))
        chassis.visual(
            mesh_from_cadquery(shape, "hood_rounded_vintage", assets=assets,
                               tolerance=0.0012, angular_tolerance=0.2),
            origin=Origin(xyz=(cx, 0.0, z + 0.04)), material=mats["body"], name="hood_rounded_vintage", material_class_id="metal.paint_coated",
        )
    else:  # stepped_modern — stepped wedge envelope (same single-shell hood mesh).
        lower = cq.Workplane("XY").box(ln, w, h * 0.66)
        upper = (cq.Workplane("XY", origin=(-ln * 0.16, 0.0, h * 0.40))
                 .box(ln * 0.66, w * 0.86, h * 0.52).edges("|Z").fillet(0.05))
        shape = lower.union(upper).edges(">Z").fillet(0.02)
        chassis.visual(
            mesh_from_cadquery(shape, "hood_stepped_modern", assets=assets,
                               tolerance=0.0012, angular_tolerance=0.2),
            origin=Origin(xyz=(cx, 0.0, z)), material=mats["body"], name="hood_stepped_modern", material_class_id="metal.paint_coated",
        )
    # Cream side stripes + brand lettering + wear stripe (④ decoration, host-derived
    # off the hood side faces; move with hood length/position).
    stripe_x = cx - 0.02
    for side, ys in enumerate((-1.0, 1.0)):
        chassis.visual(
            Box((ln * 0.92, 0.05, 0.08)),
            origin=Origin(xyz=(stripe_x, ys * (w / 2.0 - 0.006), z + 0.06)),
            material=mats["accent"], name=f"side_stripe_{side}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    for idx, fx in enumerate((-0.30, -0.19, -0.08, 0.03, 0.18, 0.29, 0.40, 0.51)):
        lx = stripe_x + fx * (ln / _HOOD_LEN)
        chassis.visual(
            Box((0.020, 0.020, 0.050)),
            origin=Origin(xyz=(lx, -(w / 2.0 + 0.006), z + 0.063)),
            material=mats["body2"], name=f"brand_letter_{idx}", appearance_only=AppearanceOnlySpec(kind="decal"),
        )


# ---------------------------------------------------------------------------
# Grille panel + N vertical slats (multiplicity, FIXED inline; Rule 1).
# ---------------------------------------------------------------------------
def _emit_grille(chassis, r: ResolvedTractorConfig, mats):
    px, py, pz = _GRILLE_PANEL
    gx = r.grille_x
    chassis.visual(Box((px, py, pz)), origin=Origin(xyz=(gx, 0.0, _GRILLE_Z)),
                   material=mats["accent"], name="front_grille_panel", material_class_id="metal.paint_coated")
    n = r.n_grille_slats
    usable = py / 2.0 - 0.05  # inset from panel edge
    slat_h = pz * 0.74
    if n == 1:
        ys = [0.0]
    else:
        ys = [-usable + i * (2.0 * usable / (n - 1)) for i in range(n)]
    pitch = (2.0 * usable / (n - 1)) if n > 1 else 2.0 * usable
    slat_w = min(0.020, pitch * 0.55)
    for idx, y in enumerate(ys):
        chassis.visual(
            Box((0.030, slat_w, slat_h)),
            origin=Origin(xyz=(gx + 0.055, y, _GRILLE_Z)),
            material=mats["body2"], name=f"grille_slat_{idx}", material_class_id="metal.paint_coated",
        )
    # Round headlamps flanking the grille (④ decoration).
    for side, ys in enumerate((-1.0, 1.0)):
        _cx(chassis, 0.055, 0.045, (gx - 0.02, ys * (py / 2.0 - 0.06), _GRILLE_Z + 0.12),
            mats["glass"], f"headlight_{side}")
        _cx(chassis, 0.066, 0.022, (gx - 0.028, ys * (py / 2.0 - 0.06), _GRILLE_Z + 0.12),
            mats["chrome"], f"headlight_bezel_{side}")


# ---------------------------------------------------------------------------
# Shared chassis core (frame / driveline / castings / exhaust / rear mount).
# ---------------------------------------------------------------------------
def _build_chassis(model, r: ResolvedTractorConfig, mats, *, assets):
    chassis = model.part("chassis")
    rax = r.rear_axle_x
    fpx, fpz = r.front_pivot_x, r.front_pivot_z

    # Ladder frame rails: rear structure only (end behind the engine at x~0.30 so
    # they never intersect the front wheels regardless of track). The front is
    # bridged by engine_block -> hood -> front_pedestal -> front_bolster.
    frame_front = 0.30
    frame_rear = rax - 0.30
    frame_len = frame_front - frame_rear
    frame_cx = (frame_front + frame_rear) / 2.0
    for side, ys in enumerate((-0.20, 0.20)):
        chassis.visual(Box((frame_len, 0.07, 0.16)), origin=Origin(xyz=(frame_cx, ys, 0.48)),
                       material=mats["body2"], name=f"ladder_frame_{side}", material_class_id="metal.paint_coated")
    chassis.visual(Box((0.78, 0.58, 0.42)), origin=Origin(xyz=(rax + 0.36, 0.0, 0.70)),
                   material=mats["body"], name="transmission_case", material_class_id="metal.paint_coated")
    chassis.visual(Box((0.62, 0.46, 0.34)), origin=Origin(xyz=(-0.05, 0.0, 0.74)),
                   material=mats["body"], name="engine_block", material_class_id="metal.paint_coated")

    # Hood + grille (③ form family / ④ decoration).
    _emit_hood(chassis, r, mats, assets=assets)
    _emit_grille(chassis, r, mats)

    # Rear axle housing (large cylinder along Y at the rear-wheel line).
    rear_cz = r.rear_r + _REAR_TIRE_LIFT
    rear_housing_len = 2.0 * r.rear_track_y - 0.10
    _cy(chassis, 0.105, rear_housing_len, (rax, 0.0, rear_cz), mats["body"], "rear_axle_housing")

    # Front pivot casting (captures the front-axle vertical pivot pin / kingpin
    # stem). The pedestal reaches up to meet the hood so the front axle is tied
    # to the grounded body. Bolster straddles the pivot z-band.
    # Underside raised (bottom fpz-0.02, was fpz-0.08) to clear the front tire crown
    # while still straddling the pivot z-band; top unchanged so it meets the pedestal.
    chassis.visual(Box((0.24, 0.50, 0.22)),
                   origin=Origin(xyz=(fpx - 0.03, 0.0, fpz + 0.09)),
                   material=mats["body"], name="front_bolster", material_class_id="metal.paint_coated")
    # Reach the hood underside for EVERY form + embed. stepped_modern's lower step is
    # only _HOOD_H*0.66 tall, so its underside sits at _HOOD_Z - _HOOD_H*0.33 (higher
    # than the flat/rounded hoods at -_HOOD_H/2); size to that highest underside so
    # the pedestal never gaps (the front casting islanded under stepped_modern).
    ped_top = _HOOD_Z - _HOOD_H * 0.33 + 0.06
    ped_bot = fpz - 0.02
    chassis.visual(Box((0.16, 0.24, ped_top - ped_bot)),
                   origin=Origin(xyz=(fpx + 0.02, 0.0, (ped_top + ped_bot) / 2.0)),
                   material=mats["body"], name="front_pedestal", material_class_id="metal.paint_coated")

    # Rear fenders arch over the big rear tires (host-conformal to rear_r).
    fender_mesh = mesh_from_geometry(
        _arc_fender_geometry(inner_radius=r.rear_r + 0.06, thickness=0.055,
                             width=r.rear_w + 0.08, start_deg=18.0, end_deg=162.0),
        "rear_fender",
    )
    for side, ys in enumerate((-1.0, 1.0)):
        chassis.visual(fender_mesh, origin=Origin(xyz=(rax, ys * (r.rear_track_y + 0.02), rear_cz)),
                       material=mats["body"], name=f"rear_fender_{side}", material_class_id="metal.paint_coated")

    # Fender support stay: inboard vertical web from the rear_axle_housing up to
    # the fender inboard edge. The fender is 0.08 wider than the tire (per side
    # +0.04) so its inboard edge sits 0.06 inboard of the tire's inboard face; the
    # web lives entirely inboard of that face and so clears the rear tire's swept
    # disc — a straight-up stay at the fender crown would pass through the tire and
    # create a chassis<->rear_wheel overlap.
    fw = r.rear_w + 0.08
    y_in_abs = (r.rear_track_y + 0.02) - fw / 2.0  # fender inboard edge |y|
    stay_bot = rear_cz - 0.02                       # embed into the axle housing (r=0.105)
    stay_top = rear_cz + r.rear_r + 0.09            # embed into the fender crown wall
    for side, ys in enumerate((-1.0, 1.0)):
        chassis.visual(
            Box((0.12, 0.05, stay_top - stay_bot)),
            origin=Origin(xyz=(rax, ys * (y_in_abs - 0.005), (stay_top + stay_bot) / 2.0)),
            material=mats["body2"], name=f"rear_fender_stay_{side}", material_class_id="metal.paint_coated",
        )

    # Vertical exhaust stack (strong identity). Bottom lowered to z~1.08 (was 1.16)
    # so it embeds into the hood regardless of form: the stepped_modern hood is only
    # its lower step (top z~1.16) at the exhaust x, which left the stack floating
    # 1.5mm as a chassis island. Top unchanged (1.94) so the muffler still mates.
    _cz(chassis, 0.040, 0.86, (0.92, -0.18, 1.51), mats["exhaust"], "vertical_exhaust")
    _cz(chassis, 0.052, 0.22, (0.92, -0.18, 1.92), mats["metal"], "exhaust_muffler")
    _cz(chassis, 0.050, 0.055, (0.92, -0.18, 1.205), mats["chrome"], "exhaust_base_collar")

    # Rear implement mount blocks (used by hitch/trailer/drawbar).
    chassis.visual(Box((0.50, 0.46, 0.13)), origin=Origin(xyz=(rax - 0.23, 0.0, 0.47)),
                   material=mats["body2"], name="rear_crossmember", material_class_id="metal.paint_coated")
    # Extends to x=rax-0.56 so the chassis_to_hitch revolute origin (rax-0.54, 0, 0.42)
    # sits on the mount hardware (was 0.02m proud of the 0.18-wide block, > 0.015 tol).
    chassis.visual(Box((0.24, 0.40, 0.14)), origin=Origin(xyz=(rax - 0.44, 0.0, 0.45)),
                   material=mats["body2"], name="rear_hitch_mount", material_class_id="metal.paint_coated")
    return chassis


# ---------------------------------------------------------------------------
# Operator station (Slot A). Inline chassis visuals (Rule 1) + shared steering.
# ---------------------------------------------------------------------------
def _emit_seat_and_column(chassis, r, mats, *, seat_x, seat_z, col_base):
    chassis.visual(Box((0.56, 0.52, 0.10)), origin=Origin(xyz=(seat_x, 0.0, seat_z)),
                   material=mats["accent"], name="seat_cushion", material_class_id="fabric.upholstery_plain")
    chassis.visual(Box((0.10, 0.56, 0.36)), origin=Origin(xyz=(seat_x - 0.27, 0.0, seat_z + 0.19)),
                   material=mats["accent"], name="seat_back", material_class_id="fabric.upholstery_plain")
    chassis.visual(Box((0.24, 0.54, 0.34)), origin=Origin(xyz=(col_base[0], 0.0, col_base[2])),
                   material=mats["body"], name="dash_cowl", material_class_id="metal.paint_coated")
    chassis.visual(Box((0.17, 0.16, 0.12)), origin=Origin(xyz=(col_base[0], 0.0, col_base[2] + 0.08)),
                   material=mats["body"], name="steering_column_base", material_class_id="metal.paint_coated")


def _emit_station(model, chassis, r: ResolvedTractorConfig, mats):
    """Returns (steering_wheel_origin_xyz, steering_column_dash_anchor)."""
    if r.operator_station == "enclosed_cab":
        seat_x, seat_z = -0.44, 1.20
        col_base = (-0.20, 0.0, 1.02)
        # Platform.
        chassis.visual(Box((0.92, 1.02, 0.16)), origin=Origin(xyz=(-0.35, 0.0, 0.94)),
                       material=mats["body"], name="operator_platform", material_class_id="metal.paint_coated")
        _emit_seat_and_column(chassis, r, mats, seat_x=seat_x, seat_z=seat_z, col_base=col_base)
        # Cab: roof, posts, glass (inline, Rule 1).
        chassis.visual(Box((1.10, 1.18, 0.13)), origin=Origin(xyz=(-0.35, 0.0, 2.24)),
                       material=mats["body2"], name="cab_roof", material_class_id="metal.paint_coated")
        chassis.visual(Box((1.18, 1.25, 0.04)), origin=Origin(xyz=(-0.35, 0.0, 2.325)),
                       material=mats["metal"], name="cab_roof_cap", material_class_id="metal.aluminum_bare")
        for ix, x in enumerate((-0.82, 0.12)):
            for iy, y in enumerate((-0.50, 0.50)):
                chassis.visual(Box((0.075, 0.075, 1.30)), origin=Origin(xyz=(x, y, 1.58)),
                               material=mats["body2"], name=f"cab_post_{ix}_{iy}", material_class_id="metal.paint_coated")
        chassis.visual(Box((0.06, 0.96, 0.90)), origin=Origin(xyz=(0.115, 0.0, 1.62)),
                       material=mats["glass"], name="front_windshield", material_class_id="glass.clear_transparent")
        chassis.visual(Box((0.06, 0.96, 0.82)), origin=Origin(xyz=(-0.82, 0.0, 1.60)),
                       material=mats["glass"], name="rear_cab_glass", material_class_id="glass.clear_transparent")
        for side, y in enumerate((0.515, -0.515)):
            chassis.visual(Box((0.94, 0.045, 0.92)), origin=Origin(xyz=(-0.35, y, 1.62)),
                           material=mats["glass"], name=f"side_window_{side}", material_class_id="glass.clear_transparent")
        return (-0.28, 0.0, 1.52), (-0.14, 0.0, 1.16)
    elif r.operator_station == "open_bare":
        col_base = (-0.31, 0.0, 1.03)
        chassis.visual(Box((0.62, 0.70, 0.09)), origin=Origin(xyz=(-0.82, 0.0, 0.935)),
                       material=mats["body"], name="operator_platform", material_class_id="metal.paint_coated")
        _emit_seat_and_column(chassis, r, mats, seat_x=-0.91, seat_z=1.015, col_base=col_base)
        return (-0.42, 0.0, 1.45), (-0.26, 0.0, 1.14)
    else:  # open_ROPS — open station + a continuous 2-post ROPS roll-bar arch.
        col_base = (-0.31, 0.0, 1.03)
        chassis.visual(Box((0.62, 0.70, 0.09)), origin=Origin(xyz=(-0.82, 0.0, 0.935)),
                       material=mats["body"], name="operator_platform", material_class_id="metal.paint_coated")
        _emit_seat_and_column(chassis, r, mats, seat_x=-0.91, seat_z=1.015, col_base=col_base)
        arch_pts = [
            (-1.10, -0.30, 0.98), (-1.14, -0.30, 1.40), (-1.16, -0.30, 1.80),
            (-1.16, -0.30, 2.10), (-1.16, -0.15, 2.14), (-1.16, 0.00, 2.15),
            (-1.16, 0.15, 2.14), (-1.16, 0.30, 2.10), (-1.16, 0.30, 1.80),
            (-1.14, 0.30, 1.40), (-1.10, 0.30, 0.98),
        ]
        arch = mesh_from_geometry(
            tube_from_spline_points(arch_pts, radius=0.035, samples_per_segment=8,
                                    radial_segments=12, cap_ends=True),
            "rops_arch_tube",
        )
        chassis.visual(arch, origin=Origin(), material=mats["dark_metal"], name="rops_arch", material_class_id="metal.blackened_gunmetal")
        for side, y in enumerate((-0.30, 0.30)):
            chassis.visual(Box((0.12, 0.12, 0.025)), origin=Origin(xyz=(-1.10, y, 0.97)),
                           material=mats["metal"], name=f"rops_base_plate_{side}", material_class_id="metal.steel_bare")
        return (-0.42, 0.0, 1.45), (-0.26, 0.0, 1.14)


def _emit_steering_wheel(model, chassis, r: ResolvedTractorConfig, mats, *, wheel_xyz, dash_anchor):
    # Steering column: a single cylinder from the dash anchor up into the wheel
    # hub so the rotating wheel physically touches the grounded body (single
    # source of the column geometry; guarantees contact + the hub allow_overlap).
    bx, _, bz = dash_anchor
    wx, _, wz = wheel_xyz
    dx, dz = wx - bx, wz - bz
    length = math.hypot(dx, dz) + 0.06
    pitch = math.atan2(dx, dz)
    chassis.visual(
        Cylinder(radius=0.026, length=length),
        origin=Origin(xyz=((bx + wx) / 2.0, 0.0, (bz + wz) / 2.0), rpy=(0.0, pitch, 0.0)),
        material=mats["body"], name="steering_column", material_class_id="metal.paint_coated",
    )
    steering_wheel = model.part("steering_wheel")
    steering_wheel.visual(
        mesh_from_geometry(
            TorusGeometry(radius=0.185, tube=0.010, radial_segments=12, tubular_segments=48),
            "steering_wheel_ring"),
        origin=Origin(), material=mats["dark_metal"], name="steering_wheel_ring", material_class_id="metal.blackened_gunmetal",
    )
    for idx, yaw in enumerate((0.0, 2.094, 4.188)):
        steering_wheel.visual(
            Box((0.24, 0.012, 0.012)),
            origin=Origin(xyz=(0.072 * math.cos(yaw), 0.072 * math.sin(yaw), 0.0), rpy=(0.0, 0.0, yaw)),
            material=mats["dark_metal"], name=f"steering_spoke_{idx}", material_class_id="metal.blackened_gunmetal",
        )
    _cz(steering_wheel, 0.036, 0.050, (0.0, 0.0, 0.0), mats["dark_metal"], "steering_hub")
    model.articulation(
        "steering_wheel_turn",
        ArticulationType.REVOLUTE,
        parent=chassis,
        child=steering_wheel,
        origin=Origin(xyz=wheel_xyz, rpy=(0.0, -0.55, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=10.0, velocity=4.0,
                                   lower=-1.25 * r.steer_limit / 0.45, upper=1.25 * r.steer_limit / 0.45),
    )


# ---------------------------------------------------------------------------
# Front axle (Slot B): builds the steering part + front wheel(s) + spins.
# The steer joint mimics steering_wheel_turn.
# ---------------------------------------------------------------------------
def _emit_front_axle(model, chassis, r: ResolvedTractorConfig, mats, *, small_tire, small_rim):
    fpx, fpz = r.front_pivot_x, r.front_pivot_z
    steer_mult = 0.36
    front_names: list[str] = []

    if r.front_axle == "single_front":
        sf_r = _single_front_radius(r.front_r)
        sf_w = sf_r * 0.533
        sf_rim = sf_r * 0.667
        sf_tire, sf_wheel = _wheel_meshes("single_front", radius=sf_r, width=sf_w,
                                          rim_radius=sf_rim, large=False)
        wheel_local_z = -(fpz - (sf_r + _FRONT_TIRE_LIFT))  # wheel center below the pivot
        # Real tire crown reaches wheel_local_z + ~1.04*sf_r (sidewall/shoulder bulge
        # past sf_r), so the yoke crown/link sit a clear ~0.035 above it. crown_z=+0.02
        # (was -0.02) lifts the plate bottom to -0.005, clear of the tire top ~-0.04.
        fork_top = wheel_local_z + sf_r + 0.08  # reach up into the raised crown
        fork_len = (fork_top - (wheel_local_z - 0.04))
        crown_z = 0.02
        yoke = model.part("steering_yoke")
        _cz(yoke, 0.042, 0.12, (0.0, 0.0, 0.03), mats["metal"], "kingpin_stem")
        yoke.visual(Box((0.11, 2.0 * sf_rim + 0.10, 0.050)), origin=Origin(xyz=(0.0, 0.0, crown_z)),
                    material=mats["body"], name="yoke_crown", material_class_id="metal.paint_coated")
        for side, ysgn in enumerate((-1.0, 1.0)):
            yoke.visual(Box((0.055, 0.045, fork_len)),
                        origin=Origin(xyz=(0.0, ysgn * (sf_w / 2.0 + 0.03), (fork_top + wheel_local_z - 0.04) / 2.0)),
                        material=mats["body"], name=f"fork_arm_{side}", material_class_id="metal.paint_coated")
        _cy(yoke, 0.022, sf_w + 0.10, (0.0, 0.0, wheel_local_z), mats["metal"], "front_axle_shaft")
        yoke.visual(Box((0.16, 0.028, 0.028)), origin=Origin(xyz=(-0.12, 0.0, crown_z - 0.01)),
                    material=mats["metal"], name="drag_link", material_class_id="metal.steel_bare")
        model.articulation(
            "chassis_to_front_axle", ArticulationType.REVOLUTE, parent=chassis, child=yoke,
            origin=Origin(xyz=(fpx, 0.0, fpz)), axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=120.0, velocity=1.2, lower=-r.steer_limit, upper=r.steer_limit),
            mimic=Mimic(joint="steering_wheel_turn", multiplier=steer_mult),
        )
        _emit_wheel(model, "front_wheel_0", tire_mesh=sf_tire, rim_mesh=sf_wheel,
                    rim_radius=sf_rim, mats=mats)
        model.articulation(
            "front_wheel_0_spin", ArticulationType.CONTINUOUS, parent=yoke, child="front_wheel_0",
            origin=Origin(xyz=(0.0, 0.0, wheel_local_z)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=80.0, velocity=18.0),
            mimic=Mimic(joint="rear_wheel_0_spin", multiplier=1.9),
        )
        front_names.append("front_wheel_0")
        return front_names, "steering_yoke"

    # wide_standard / narrow_tricycle: solid beam pivots as one piece.
    axle = model.part("front_axle")
    ty = r.front_track_y
    wide = r.front_axle == "wide_standard"
    # Wide wheels sit outboard of the spindle end; narrow wheels ride at the beam.
    wheel_y = (ty + 0.12) if wide else ty
    # Wide beam stays inboard of the wheels (spindles bridge out to the hubs);
    # narrow beam spans between the closely-spaced wheels.
    beam_w = (2.0 * ty - 0.16) if wide else (2.0 * ty + 0.10)
    spindle_len = 0.34 if wide else 0.16
    axle.visual(Box((0.16, beam_w, 0.11)), origin=Origin(xyz=(0.0, 0.0, -0.10)),
                material=mats["body"], name="front_axle_beam", material_class_id="metal.paint_coated")
    _cz(axle, 0.060, 0.24, (0.0, 0.0, -0.02), mats["metal"], "center_pivot_pin")
    _cy(axle, 0.018, max(0.14, 2.0 * ty - 0.10), (0.07, 0.0, -0.165), mats["metal"], "tie_rod")
    for side, ysgn in enumerate((-1.0, 1.0)):
        _cy(axle, 0.035, spindle_len, (0.0, ysgn * ty, -0.10), mats["metal"], f"spindle_{side}")
        axle.visual(Box((0.10, 0.10, 0.18)), origin=Origin(xyz=(0.0, ysgn * max(0.0, ty - 0.10), -0.06)),
                    material=mats["body2"], name=f"knuckle_boss_{side}", material_class_id="metal.paint_coated")
    model.articulation(
        "chassis_to_front_axle", ArticulationType.REVOLUTE, parent=chassis, child=axle,
        origin=Origin(xyz=(fpx, 0.0, fpz)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=1.2, lower=-r.steer_limit, upper=r.steer_limit),
        mimic=Mimic(joint="steering_wheel_turn", multiplier=steer_mult),
    )
    for side, ysgn in enumerate((-1.0, 1.0)):
        name = f"front_wheel_{side}"
        _emit_wheel(model, name, tire_mesh=small_tire, rim_mesh=small_rim,
                    rim_radius=r.front_rim_r, mats=mats)
        model.articulation(
            f"{name}_spin", ArticulationType.CONTINUOUS, parent=axle, child=name,
            origin=Origin(xyz=(0.0, ysgn * wheel_y, -0.10)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=80.0, velocity=18.0),
            mimic=Mimic(joint="rear_wheel_0_spin", multiplier=1.9),
        )
        front_names.append(name)
    return front_names, "front_axle"


# ---------------------------------------------------------------------------
# Rear wheels (always 2, CONTINUOUS; rear_wheel_0 is the spin driver).
# ---------------------------------------------------------------------------
def _emit_rear_wheels(model, chassis, r, mats, *, rear_tire, rear_rim):
    rax = r.rear_axle_x
    rear_cz = r.rear_r + _REAR_TIRE_LIFT
    for side, ysgn in enumerate((-1.0, 1.0)):
        name = f"rear_wheel_{side}"
        _emit_wheel(model, name, tire_mesh=rear_tire, rim_mesh=rear_rim,
                    rim_radius=r.rear_rim_r, mats=mats, add_valve=True)
        mimic = None if side == 0 else Mimic(joint="rear_wheel_0_spin", multiplier=1.0)
        model.articulation(
            f"{name}_spin", ArticulationType.CONTINUOUS, parent=chassis, child=name,
            origin=Origin(xyz=(rax, ysgn * (r.rear_track_y + 0.02), rear_cz)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=300.0, velocity=12.0), mimic=mimic,
        )


# ---------------------------------------------------------------------------
# Implements (Slot C).
# ---------------------------------------------------------------------------
def _emit_implement(model, chassis, r: ResolvedTractorConfig, mats, *, small_tire, small_rim):
    rax = r.rear_axle_x
    hitch_x = rax - 0.52
    if r.implement == "plain_drawbar":
        # Simple fixed drawbar + clevis (inline chassis visuals; Rule 1, no joint).
        chassis.visual(Box((0.66, 0.12, 0.09)), origin=Origin(xyz=(hitch_x + 0.20, 0.0, 0.45)),
                       material=mats["metal"], name="drawbar", material_class_id="metal.steel_bare")
        chassis.visual(Box((0.14, 0.24, 0.025)), origin=Origin(xyz=(hitch_x - 0.14, 0.0, 0.505)),
                       material=mats["dark_metal"], name="drawbar_clevis_top", material_class_id="metal.blackened_gunmetal")
        chassis.visual(Box((0.14, 0.24, 0.025)), origin=Origin(xyz=(hitch_x - 0.14, 0.0, 0.395)),
                       material=mats["dark_metal"], name="drawbar_clevis_bottom", material_class_id="metal.blackened_gunmetal")
        _cz(chassis, 0.033, 0.15, (hitch_x - 0.14, 0.0, 0.45), mats["metal"], "hitch_pin_lug")
        return []

    if r.implement == "three_point_hitch":
        hitch = model.part("hitch")
        hitch.visual(Box((0.70, 0.10, 0.055)), origin=Origin(xyz=(-0.35, 0.0, 0.0)),
                     material=mats["metal"], name="drawbar", material_class_id="metal.steel_bare")
        for side, ysgn in enumerate((-1.0, 1.0)):
            hitch.visual(Box((0.44, 0.055, 0.055)),
                         origin=Origin(xyz=(-0.23, ysgn * 0.18, 0.09), rpy=(0.0, 0.22, 0.0)),
                         material=mats["metal"], name=f"lift_arm_{side}", material_class_id="metal.steel_bare")
        _cy(hitch, 0.030, 0.46, (0.0, 0.0, 0.0), mats["metal"], "hitch_pivot_pin")
        hitch.visual(Box((0.10, 0.30, 0.08)), origin=Origin(xyz=(-0.70, 0.0, 0.0)),
                     material=mats["dark_metal"], name="hitch_clevis", material_class_id="metal.blackened_gunmetal")
        lo = -0.30 * r.hitch_lift_scale
        hi = 0.42 * r.hitch_lift_scale
        model.articulation(
            "chassis_to_hitch", ArticulationType.REVOLUTE, parent=chassis, child=hitch,
            origin=Origin(xyz=(hitch_x - 0.02, 0.0, 0.42)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=220.0, velocity=0.7, lower=lo, upper=hi),
        )
        return ["hitch"]

    if r.implement == "front_loader":
        # Loader tower = inline chassis visuals (avoids a FIXED joint); the boom
        # pivots directly off the chassis. Tower straddles the hood at ~x=0.40.
        tower_x, pivot_z = 0.40, 1.75
        for side, y in enumerate((-0.52, 0.52)):
            ysign = 1.0 if y > 0 else -1.0
            chassis.visual(Box((0.07, 0.06, 0.42)), origin=Origin(xyz=(tower_x, y, 1.55)),
                           material=mats["dark_metal"], name=f"loader_tower_upright_{side}", material_class_id="metal.blackened_gunmetal")
            chassis.visual(Box((0.14, 0.12, 0.20)), origin=Origin(xyz=(tower_x, y, 1.30)),
                           material=mats["body2"], name=f"loader_tower_bracket_{side}", material_class_id="metal.paint_coated")
            # Mounting foot: the tower legs sit outboard of the hood (y=+-0.52 vs
            # hood y=+-0.29), so bolt each bracket down-and-inboard onto the hood
            # side (present at y=+-0.29 up to z~1.16 for every hood form). Without
            # it the whole tower is a disconnected chassis island.
            chassis.visual(Box((0.12, 0.30, 0.16)), origin=Origin(xyz=(tower_x, ysign * 0.42, 1.16)),
                           material=mats["body2"], name=f"loader_tower_foot_{side}", material_class_id="metal.paint_coated")
        chassis.visual(Box((0.07, 1.10, 0.06)), origin=Origin(xyz=(tower_x, 0.0, pivot_z + 0.02)),
                       material=mats["dark_metal"], name="loader_tower_crossbar", material_class_id="metal.blackened_gunmetal")
        _cy(chassis, 0.030, 1.10, (tower_x, 0.0, pivot_z), mats["metal"], "loader_tower_pivot_pin")

        boom = model.part("loader_boom")
        for side, y in enumerate((-0.52, 0.52)):
            boom.visual(Box((1.50, 0.05, 0.08)), origin=Origin(xyz=(0.75, y, 0.0)),
                        material=mats["body"], name=f"boom_arm_{side}", material_class_id="metal.paint_coated")
            boom.visual(Box((0.08, 0.06, 0.14)), origin=Origin(xyz=(0.0, y, -0.03)),
                        material=mats["dark_metal"], name=f"boom_pivot_bracket_{side}", material_class_id="metal.blackened_gunmetal")
        boom.visual(Box((0.06, 1.04, 0.06)), origin=Origin(xyz=(0.30, 0.0, 0.0)),
                    material=mats["dark_metal"], name="boom_cross_tube", material_class_id="metal.blackened_gunmetal")
        _cy(boom, 0.025, 1.10, (1.50, 0.0, 0.0), mats["metal"], "bucket_curl_pin")
        _cx(boom, 0.035, 1.00, (0.65, 0.0, -0.06), mats["metal"], "lift_cylinder")
        # Down-travel capped at -0.28 (was -0.35): at the old limit the lift cylinder
        # on the boom swept into the tall rounded_vintage hood crown; -0.28*1.10 max
        # keeps the boom clear of every hood form with margin.
        lo = -0.28 * r.loader_range_scale
        hi = 0.60 * r.loader_range_scale
        model.articulation(
            "chassis_to_loader_boom", ArticulationType.REVOLUTE, parent=chassis, child=boom,
            origin=Origin(xyz=(tower_x, 0.0, pivot_z)), axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=2000.0, velocity=0.5, lower=lo, upper=hi),
        )

        bucket = model.part("loader_bucket")
        bucket.visual(Box((0.04, 0.76, 0.50)), origin=Origin(xyz=(-0.02, 0.0, -0.25)),
                      material=mats["dark_metal"], name="bucket_back", material_class_id="metal.blackened_gunmetal")
        bucket.visual(Box((0.50, 0.76, 0.04)), origin=Origin(xyz=(0.23, 0.0, -0.50)),
                      material=mats["dark_metal"], name="bucket_floor", material_class_id="metal.blackened_gunmetal")
        for side, y in enumerate((-0.36, 0.36)):
            bucket.visual(Box((0.50, 0.04, 0.52)), origin=Origin(xyz=(0.23, y, -0.25)),
                          material=mats["metal"], name=f"bucket_side_{side}", material_class_id="metal.steel_bare")
        bucket.visual(Box((0.03, 0.80, 0.025)), origin=Origin(xyz=(0.47, 0.0, -0.50)),
                      material=mats["metal"], name="bucket_cutting_edge", material_class_id="metal.steel_bare")
        clo = -0.55 * r.loader_range_scale
        chi = 0.80 * r.loader_range_scale
        model.articulation(
            "boom_to_loader_bucket", ArticulationType.REVOLUTE, parent=boom, child=bucket,
            origin=Origin(xyz=(1.50, 0.0, 0.0)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1500.0, velocity=0.6, lower=clo, upper=chi),
        )
        return ["loader_boom", "loader_bucket"]

    # towed_trailer — trailer frame + bed yaws about the rear hitch pin; 2 wheels.
    chassis.visual(Box((0.66, 0.12, 0.09)), origin=Origin(xyz=(hitch_x + 0.20, 0.0, 0.45)),
                   material=mats["metal"], name="drawbar", material_class_id="metal.steel_bare")
    _cz(chassis, 0.033, 0.16, (hitch_x - 0.14, 0.0, 0.45), mats["metal"], "hitch_pin_lug")
    trailer = model.part("trailer_frame")
    trailer.visual(Box((0.62, 0.14, 0.07)), origin=Origin(xyz=(-0.30, 0.0, 0.0)),
                   material=mats["dark_metal"], name="trailer_tongue", material_class_id="metal.blackened_gunmetal")
    trailer.visual(Box((0.20, 0.24, 0.09)), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                   material=mats["dark_metal"], name="trailer_coupler", material_class_id="metal.blackened_gunmetal")
    trailer.visual(Box((1.30, 1.02, 0.09)), origin=Origin(xyz=(-1.02, 0.0, 0.02)),
                   material=mats["dark_metal"], name="trailer_underframe", material_class_id="metal.blackened_gunmetal")
    trailer.visual(Box((1.34, 0.98, 0.09)), origin=Origin(xyz=(-1.02, 0.0, 0.11)),
                   material=mats["wood"], name="cargo_bed_floor", material_class_id="wood.plank_floor")
    for side, ysgn in enumerate((-1.0, 1.0)):
        trailer.visual(Box((1.36, 0.07, 0.42)), origin=Origin(xyz=(-1.02, ysgn * 0.50, 0.35)),
                       material=mats["wood"], name=f"cargo_bed_side_{side}", material_class_id="wood.plank_floor")
    trailer.visual(Box((0.07, 0.98, 0.40)), origin=Origin(xyz=(-0.36, 0.0, 0.34)),
                   material=mats["wood"], name="cargo_bed_front", material_class_id="wood.plank_floor")
    trailer.visual(Box((0.07, 0.98, 0.40)), origin=Origin(xyz=(-1.68, 0.0, 0.34)),
                   material=mats["wood"], name="cargo_bed_tailgate", material_class_id="wood.plank_floor")
    trailer_joint_z = 0.47
    wheel_local_z = (r.front_r + _FRONT_TIRE_LIFT) - trailer_joint_z  # tires rest on ground
    trailer_wheel_y = 0.50 + r.front_w / 2.0 + 0.06  # outboard of the cargo-bed sides
    _cy(trailer, 0.040, 2.0 * trailer_wheel_y + 0.06, (-1.02, 0.0, wheel_local_z),
        mats["dark_metal"], "trailer_axle")
    # Spring hangers: the axle rides below the underframe (bottom z~-0.025), so drop
    # a hanger on each side from the underframe down onto the axle, else the axle is
    # a disconnected island in the trailer_frame part.
    for side, ysgn in enumerate((-1.0, 1.0)):
        trailer.visual(Box((0.09, 0.09, 0.03 - wheel_local_z)),
                       origin=Origin(xyz=(-1.02, ysgn * 0.30, (0.03 + wheel_local_z) / 2.0)),
                       material=mats["dark_metal"], name=f"trailer_spring_hanger_{side}", material_class_id="metal.blackened_gunmetal")
    model.articulation(
        "chassis_to_trailer_frame", ArticulationType.REVOLUTE, parent=chassis, child=trailer,
        origin=Origin(xyz=(hitch_x - 0.14, 0.0, trailer_joint_z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=450.0, velocity=0.45, lower=-0.24, upper=0.24),
    )
    for side, ysgn in enumerate((-1.0, 1.0)):
        name = f"trailer_wheel_{side}"
        _emit_wheel(model, name, tire_mesh=small_tire, rim_mesh=small_rim,
                    rim_radius=r.front_rim_r, mats=mats)
        model.articulation(
            f"{name}_spin", ArticulationType.CONTINUOUS, parent=trailer, child=name,
            origin=Origin(xyz=(-1.02, ysgn * trailer_wheel_y, wheel_local_z), rpy=(0.0, 0.0, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=450.0, velocity=14.0),
            mimic=Mimic(joint="rear_wheel_0_spin", multiplier=1.9),
        )
    return ["trailer_frame", "trailer_wheel_0", "trailer_wheel_1"]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_tractor(
    config: TractorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "Agricultural", "small_class": "Tractor"},
    )
    palette = dict(_COMMON_MATS)
    palette.update(_PALETTE_BODY[r.palette_style])
    mats = {key: model.material(f"tractor_{key}_{r.palette_style}", rgba=rgba)
            for key, rgba in palette.items()}

    # Wheel meshes: one rear-type + one small-type (shared across all parts).
    rear_tire, rear_rim = _wheel_meshes("rear", radius=r.rear_r, width=r.rear_w,
                                        rim_radius=r.rear_rim_r, large=True)
    small_tire, small_rim = _wheel_meshes("front", radius=r.front_r, width=r.front_w,
                                          rim_radius=r.front_rim_r, large=False)

    chassis = _build_chassis(model, r, mats, assets=assets)
    wheel_xyz, dash_anchor = _emit_station(model, chassis, r, mats)
    _emit_steering_wheel(model, chassis, r, mats, wheel_xyz=wheel_xyz, dash_anchor=dash_anchor)
    _emit_rear_wheels(model, chassis, r, mats, rear_tire=rear_tire, rear_rim=rear_rim)
    _emit_front_axle(model, chassis, r, mats, small_tire=small_tire, small_rim=small_rim)
    _emit_implement(model, chassis, r, mats, small_tire=small_tire, small_rim=small_rim)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_tractor(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_tractor(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _allow_captured_pins(ctx, object_model, r: ResolvedTractorConfig):
    parts = {p.name for p in object_model.parts}
    # Rear wheel hub on rear axle housing.
    for side in (0, 1):
        wn = f"rear_wheel_{side}"
        if wn in parts:
            ctx.allow_overlap("chassis", wn, elem_a="rear_axle_housing", elem_b="rim",
                              reason="rear axle housing/stub seats inside the rotating rear wheel hub.")
    # Steering wheel hub on the steering column.
    ctx.allow_overlap("chassis", "steering_wheel", elem_a="steering_column", elem_b="steering_hub",
                      reason="steering wheel hub is mounted on the steering column tip.")
    for i in range(3):
        ctx.allow_overlap("chassis", "steering_wheel", elem_a="steering_column",
                          elem_b=f"steering_spoke_{i}",
                          reason="steering column tip meets the wheel where the spokes radiate.")
    # Front axle pivot captured in the front casting + front wheels on spindles.
    if r.front_axle == "single_front":
        for elem in ("front_bolster", "front_pedestal"):
            for stem in ("kingpin_stem", "yoke_crown", "fork_arm_0", "fork_arm_1", "drag_link"):
                ctx.allow_overlap("chassis", "steering_yoke", elem_a=elem, elem_b=stem,
                                  reason="the yoke kingpin/crown/fork/drag-link is captured inside the front casting.")
        ctx.allow_overlap("steering_yoke", "front_wheel_0", elem_a="front_axle_shaft", elem_b="rim",
                          reason="the front axle shaft passes through the single front wheel hub.")
        for side in (0, 1):
            ctx.allow_overlap("steering_yoke", "front_wheel_0", elem_a=f"fork_arm_{side}", elem_b="tire",
                              reason="the steering fork arms straddle the single front tire.")
    else:
        casting_pins = ("center_pivot_pin", "front_axle_beam", "spindle_0", "spindle_1",
                        "knuckle_boss_0", "knuckle_boss_1")
        for elem in ("front_bolster", "front_pedestal"):
            for pin in casting_pins:
                ctx.allow_overlap("chassis", "front_axle", elem_a=elem, elem_b=pin,
                                  reason="the front axle pivot/beam/spindle is captured inside the front casting.")
        for side in (0, 1):
            wn = f"front_wheel_{side}"
            for elem in ("spindle_0", "spindle_1", "front_axle_beam", "center_pivot_pin",
                         "tie_rod", "knuckle_boss_0", "knuckle_boss_1"):
                for target in ("rim", "tire"):
                    ctx.allow_overlap("front_axle", wn, elem_a=elem, elem_b=target,
                                      reason="the front axle spindle/beam/linkage is captured at the front wheel hub.")
            if r.front_axle == "narrow_tricycle":
                for elem in ("front_bolster", "front_pedestal"):
                    for target in ("rim", "tire"):
                        ctx.allow_overlap("chassis", wn, elem_a=elem, elem_b=target,
                                          reason="narrow row-crop front tires sit close under the front casting.")
    # Implement pins.
    if r.implement == "three_point_hitch":
        ctx.allow_overlap("chassis", "hitch", elem_a="rear_hitch_mount", elem_b="hitch_pivot_pin",
                          reason="the hitch pivot pin is seated through the rear hitch bracket.")
        # The drawbar/lift-arm roots reach the pivot, so their front ends are
        # captured a few mm inside the rear hitch bracket (which extends past the
        # pivot to seat the joint origin). Local pin/bracket mating overlap.
        for elem in ("drawbar", "lift_arm_0", "lift_arm_1"):
            ctx.allow_overlap("chassis", "hitch", elem_a="rear_hitch_mount", elem_b=elem,
                              reason="the three-point-hitch drawbar/lift arms bolt to the rear hitch bracket at the pivot.")
    elif r.implement == "towed_trailer":
        ctx.allow_overlap("chassis", "trailer_frame", elem_a="hitch_pin_lug", elem_b="trailer_coupler",
                          reason="the trailer coupler wraps around the drawbar hitch pin lug.")
        ctx.allow_overlap("chassis", "trailer_frame", elem_a="hitch_pin_lug", elem_b="trailer_tongue",
                          reason="the trailer tongue is captured around the hitch pin lug.")
        ctx.allow_overlap("chassis", "trailer_frame", elem_a="drawbar", elem_b="trailer_tongue",
                          reason="the trailer tongue overlaps the drawbar at the hitch connection.")
        ctx.allow_overlap("chassis", "trailer_frame", elem_a="drawbar", elem_b="trailer_coupler",
                          reason="the trailer coupler seats against the drawbar at the hitch connection.")
        ctx.allow_overlap("chassis", "trailer_frame", elem_a="rear_hitch_mount", elem_b="trailer_coupler",
                          reason="the trailer coupler wraps the rear hitch bracket at the yaw pivot.")
        for side in (0, 1):
            ctx.allow_overlap("trailer_frame", f"trailer_wheel_{side}", elem_a="trailer_axle", elem_b="rim",
                              reason="the trailer axle passes through the trailer wheel hub.")
    elif r.implement == "front_loader":
        for side in (0, 1):
            for tower_elem in ("loader_tower_pivot_pin", "loader_tower_crossbar",
                               f"loader_tower_upright_{side}"):
                ctx.allow_overlap("loader_boom", "chassis", elem_a=f"boom_pivot_bracket_{side}",
                                  elem_b=tower_elem,
                                  reason="the boom pivot bracket wraps the tower pivot hardware as a hinge.")
            for tower_elem in ("loader_tower_pivot_pin", "loader_tower_crossbar",
                               f"loader_tower_upright_{side}"):
                ctx.allow_overlap("loader_boom", "chassis", elem_a=f"boom_arm_{side}",
                                  elem_b=tower_elem,
                                  reason="the boom arm root is captured on the tower pivot pin / passes the crossbar-upright at the hinge.")
        # boom & bucket share the curl pin as a captured hinge across the curl range.
        ctx.allow_overlap("loader_boom", "loader_bucket",
                          reason="the loader bucket is captured on the boom-tip curl pin (hinge barrel).")


def run_tractor_tests(object_model: ArticulatedObject, config: TractorConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    parts = {p.name for p in object_model.parts}

    _allow_captured_pins(ctx, object_model, r)

    # ---- Compiler baseline (belt-and-suspenders). ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    # ---- Rule 5: swept-pose overlap across all joint DOF. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=24, ignore_fixed=True)

    # ---- Identity. ----
    ctx.check("small class is Tractor",
              object_model.meta.get("small_class") == "Tractor",
              details=str(object_model.meta))
    for req in ("chassis", "steering_wheel", "rear_wheel_0", "rear_wheel_1", "front_wheel_0"):
        ctx.check(f"part {req} present", req in parts, details=str(sorted(parts)))

    # Rear tires visibly larger than front.
    rear_aabb = ctx.part_world_aabb("rear_wheel_0")
    front_aabb = ctx.part_world_aabb("front_wheel_0")
    if rear_aabb and front_aabb:
        rear_d = rear_aabb[1][2] - rear_aabb[0][2]
        front_d = front_aabb[1][2] - front_aabb[0][2]
        ctx.check("rear tires are visibly larger than front wheels",
                  rear_d > front_d * 1.55, details=f"rear_d={rear_d:.3f} front_d={front_d:.3f}")

    # All tires rest on the ground plane (z~0).
    wheel_parts = [p for p in parts if p.startswith(("rear_wheel", "front_wheel", "trailer_wheel"))]
    bottoms = []
    for wp in wheel_parts:
        a = ctx.part_element_world_aabb(wp, elem="tire")
        if a is not None:
            bottoms.append(a[0][2])
    ctx.check("all tires sit on the ground plane",
              len(bottoms) == len(wheel_parts) and max(abs(b) for b in bottoms) < 0.025,
              details=f"bottoms={bottoms}")

    # ---- Joint topology / axes. ----
    steer = object_model.get_articulation("steering_wheel_turn")
    front_steer = object_model.get_articulation("chassis_to_front_axle")
    rear_spin = object_model.get_articulation("rear_wheel_0_spin")
    ctx.check("steering wheel turn is REVOLUTE about z",
              steer.articulation_type == ArticulationType.REVOLUTE and abs(steer.axis[2]) > 0.99,
              details=f"axis={tuple(steer.axis)}")
    ctx.check("front axle steer is REVOLUTE z and mimics the steering wheel",
              front_steer.articulation_type == ArticulationType.REVOLUTE
              and abs(front_steer.axis[2]) > 0.99
              and front_steer.mimic is not None
              and front_steer.mimic.joint == "steering_wheel_turn",
              details=f"axis={tuple(front_steer.axis)} mimic={front_steer.mimic}")
    ctx.check("rear wheel spin is CONTINUOUS about y",
              rear_spin.articulation_type == ArticulationType.CONTINUOUS and abs(rear_spin.axis[1]) > 0.99,
              details=f"axis={tuple(rear_spin.axis)}")

    # ---- Targeted motions. ----
    # Rear wheel rotation carries its valve stem around (proves spin).
    v0 = ctx.part_element_world_aabb("rear_wheel_0", elem="valve_stem")
    with ctx.pose({rear_spin: math.pi / 2.0}):
        v1 = ctx.part_element_world_aabb("rear_wheel_0", elem="valve_stem")
    if v0 is not None and v1 is not None:
        cz0 = (v0[0][2] + v0[1][2]) * 0.5
        cz1 = (v1[0][2] + v1[1][2]) * 0.5
        ctx.check("rear wheel rotation visibly carries the valve stem",
                  abs(cz1 - cz0) > 0.05, details=f"z {cz0:.3f}->{cz1:.3f}")

    # Steering yaws the front assembly (via mimic).
    if r.front_axle == "single_front":
        d0 = ctx.part_element_world_aabb("steering_yoke", elem="drag_link")
        with ctx.pose({steer: 1.0}):
            d1 = ctx.part_element_world_aabb("steering_yoke", elem="drag_link")
        if d0 is not None and d1 is not None:
            moved = max(abs((d1[k][j]) - (d0[k][j])) for k in range(2) for j in (0, 1))
            ctx.check("steering yaws the single-front yoke", moved > 0.02,
                      details=f"drag_link move={moved:.3f}")
    else:
        f0 = ctx.part_world_position("front_wheel_0")
        f1p = ctx.part_world_position("front_wheel_1")
        with ctx.pose({steer: 1.0}):
            g0 = ctx.part_world_position("front_wheel_0")
            g1 = ctx.part_world_position("front_wheel_1")
        if f0 and g0 and f1p and g1:
            ctx.check("steering yaws the front wheels fore/aft in opposite directions",
                      abs(g0[0] - f0[0]) > 0.02 and (g0[0] - f0[0]) * (g1[0] - f1p[0]) < 0.0,
                      details=f"w0 dx={g0[0]-f0[0]:.3f} w1 dx={g1[0]-f1p[0]:.3f}")

    # Implement motion.
    if r.implement == "three_point_hitch":
        j = object_model.get_articulation("chassis_to_hitch")
        a0 = ctx.part_world_aabb("hitch")
        with ctx.pose({j: 0.42 * r.hitch_lift_scale * 0.9}):
            a1 = ctx.part_world_aabb("hitch")
        if a0 and a1:
            ctx.check("3-point hitch lifts up about its rear pivot", a1[1][2] > a0[1][2] + 0.08,
                      details=f"top {a0[1][2]:.3f}->{a1[1][2]:.3f}")
    elif r.implement == "front_loader":
        jb = object_model.get_articulation("chassis_to_loader_boom")
        jc = object_model.get_articulation("boom_to_loader_bucket")
        ctx.check("loader lift & curl are REVOLUTE",
                  jb.articulation_type == ArticulationType.REVOLUTE
                  and jc.articulation_type == ArticulationType.REVOLUTE)
        a0 = ctx.part_world_aabb("loader_bucket")
        with ctx.pose({jb: 0.60 * r.loader_range_scale * 0.9}):
            a1 = ctx.part_world_aabb("loader_bucket")
        if a0 and a1:
            ctx.check("loader boom raises the bucket", a1[1][2] > a0[1][2] + 0.10,
                      details=f"top {a0[1][2]:.3f}->{a1[1][2]:.3f}")
    elif r.implement == "towed_trailer":
        j = object_model.get_articulation("chassis_to_trailer_frame")
        ctx.check("trailer yaw is REVOLUTE about z with a small swing",
                  j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99)
        w0 = ctx.part_world_position("trailer_wheel_0")
        with ctx.pose({j: 0.20}):
            w1 = ctx.part_world_position("trailer_wheel_0")
        if w0 and w1:
            ctx.check("trailer yaws about the hitch pin", abs(w1[1] - w0[1]) > 0.08,
                      details=f"wheel dy={w1[1]-w0[1]:.3f}")

    # ---- Grille slat multiplicity present. ----
    slats = [v.name for v in object_model.get_part("chassis").visuals
             if v.name.startswith("grille_slat_")]
    ctx.check("N grille slats inlined on the grille panel (Rule 1)",
              len(slats) == r.n_grille_slats, details=f"slats={len(slats)} N={r.n_grille_slats}")

    # ---- slot_choices recorded. ----
    ctx.check("slot_choices recorded",
              tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
              details=str(object_model.meta.get("slot_choices")))

    return ctx.report()


__all__ = (
    "TractorConfig",
    "ResolvedTractorConfig",
    "build_tractor",
    "build_seeded_tractor",
    "config_from_seed",
    "resolve_config",
    "run_tractor_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
