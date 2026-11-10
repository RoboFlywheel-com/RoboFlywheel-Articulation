# SPDX-License-Identifier: Apache-2.0

"""Electrical cable/hose reel — modular procedural template.

A frame (FIXED, grounded) carries a round drum reel that spins freely about a
horizontal +X axle (the PRIMARY continuous joint, present in every frame form).
The reel = a round annular drum barrel + two flange cheek discs + hub + a single
wound-cable helix. An optional hand crank drives it; on the free-grip drive the
crank end carries a second continuous free-spinning grip.

Pattern = ``mixed`` (grounded frame + 1 spinning reel child + optional spinning
grip child; flange/drive emitted in parallel onto reel/frame). Three structural
slots + one multiplicity axis:

  * ``frame_form`` (5, the ③ Primary-Form-Family slot, grounded ``frame``):
    solid_stand / open_cage / closed_housing / wall_bracket / wheeled_cart —
    mount folded in (they cannot share a mating face). A shared
    ``_emit_axle_hardware`` gives every form the identical fixed-X axle interface.
  * ``flange_form`` (2): solid_disc / spoked_disc — the reel cheek discs (round
    annular / torus meshes only, never Box).
  * ``drive_type`` (3): crank_free_grip (2nd CONTINUOUS grip joint) /
    crank_fixed_knob (no 2nd joint) / motorized (motor+gearbox on frame + driven
    gear on reel, no crank).
  * ``flange_feature_count`` (N in [4,8]): spoke count / bolt-circle count.

Sources (all 7 read): origins ``..._ea686860`` (cream solid-stand 002),
``..._83201f3e`` (orange open-cage 001) + forks closed_housing / spoked_flange /
motorized_drive / wall_bracket / wheeled_cart. Spec:
``articraft_template_authoring/specs_modular_v1/cable_reel.md``.

The ``frame_to_reel`` and ``reel_to_crank_grip`` joints are captured journal /
pin bearings (axle captured in bearing races; grip sleeve around the crank pin) —
no clean axis-aligned face pair, so both are grandfathered (``mating`` omitted)
and guarded by element-scoped ``allow_overlap`` in run_tests, mirroring the
sources and Machinery_Watermill.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeWithHolesGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

TAU = 2.0 * math.pi


# --------------------------------------------------------------------------- #
# Shared profile / mesh helpers (adopted verbatim from the 5-star sources).    #
# --------------------------------------------------------------------------- #
def circle_profile(radius: float, segments: int = 64) -> list[tuple[float, float]]:
    return [
        (radius * math.cos(TAU * i / segments), radius * math.sin(TAU * i / segments))
        for i in range(segments)
    ]


def offset_profile(profile, dy: float, dz: float):
    return [(y + dy, z + dz) for (y, z) in profile]


def sector_profile(inner_r, outer_r, start_angle, end_angle, segments: int = 12):
    """Closed pie-slice between two radii and two angles (radians)."""
    pts: list[tuple[float, float]] = []
    for i in range(segments + 1):
        a = start_angle + (end_angle - start_angle) * i / segments
        pts.append((outer_r * math.cos(a), outer_r * math.sin(a)))
    for i in range(segments + 1):
        a = end_angle - (end_angle - start_angle) * i / segments
        pts.append((inner_r * math.cos(a), inner_r * math.sin(a)))
    return pts


def _map_yz(geom):
    """Map Extrude*/Torus local (a, b, thickness) -> world (thickness->x, a->y, b->z)."""
    mapped = geom.copy()
    mapped.vertices = [(z, x, y) for (x, y, z) in mapped.vertices]
    return mapped


def annular_yz(radius, hole_radius, thickness_x, *, segments: int = 64):
    geom = ExtrudeWithHolesGeometry(
        circle_profile(radius, segments),
        [circle_profile(hole_radius, segments)],
        thickness_x,
        center=True,
    )
    return _map_yz(geom)


def plate_yz(outer, holes, thickness_x):
    return _map_yz(ExtrudeWithHolesGeometry(outer, holes, thickness_x, center=True))


def spoked_disc_yz(outer_r, hub_hole_r, thickness_x, *, n_spokes, spoke_width_angle,
                   gap_inner_r, gap_outer_r, segments: int = 72, arc_segments: int = 12):
    """Spoked flange: outer rim ring + hub ring joined by N radial spokes."""
    outer = circle_profile(outer_r, segments)
    holes = [circle_profile(hub_hole_r, segments)]
    spoke_spacing = TAU / n_spokes
    gap_angular_width = spoke_spacing - spoke_width_angle
    for i in range(n_spokes):
        gap_center = spoke_spacing * i + spoke_spacing / 2.0
        holes.append(
            sector_profile(gap_inner_r, gap_outer_r,
                           gap_center - gap_angular_width / 2.0,
                           gap_center + gap_angular_width / 2.0, arc_segments)
        )
    return _map_yz(ExtrudeWithHolesGeometry(outer, holes, thickness_x, center=True))


def torus_around_x(radius, tube, *, radial_segments: int = 14, tubular_segments: int = 48):
    return _map_yz(TorusGeometry(radius, tube, radial_segments=radial_segments,
                                 tubular_segments=tubular_segments))


def _axc(part, name, radius, length, xyz, material):
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


# --------------------------------------------------------------------------- #
# Slot enums                                                                   #
# --------------------------------------------------------------------------- #
FrameForm = Literal["solid_stand", "open_cage", "closed_housing", "wall_bracket", "wheeled_cart"]
FlangeForm = Literal["solid_disc", "spoked_disc"]
DriveType = Literal["crank_free_grip", "crank_fixed_knob", "motorized"]
PaletteStyle = Literal[
    "safety_cream", "safety_orange", "industrial_yellow",
    "graphite_black", "galvanized_raw", "hose_reel_red",
]

FRAME_FORMS: tuple[FrameForm, ...] = (
    "solid_stand", "open_cage", "closed_housing", "wall_bracket", "wheeled_cart")
FLANGE_FORMS: tuple[FlangeForm, ...] = ("solid_disc", "spoked_disc")
DRIVE_TYPES: tuple[DriveType, ...] = ("crank_free_grip", "crank_fixed_knob", "motorized")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "safety_cream", "safety_orange", "industrial_yellow",
    "graphite_black", "galvanized_raw", "hose_reel_red")

N_MIN, N_MAX = 4, 8
_N_VALUES: tuple[int, ...] = tuple(range(N_MIN, N_MAX + 1))
_N_WEIGHTS: tuple[float, ...] = tuple(1.0 / (1.0 + abs(n - 6)) for n in _N_VALUES)


# --------------------------------------------------------------------------- #
# Palette (>=3 realistic colorways; keys drive every .visual material).        #
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "safety_cream": {
        "body": (0.78, 0.74, 0.62, 1.0), "body_dark": (0.60, 0.57, 0.48, 1.0),
        "drum": (0.05, 0.05, 0.055, 1.0), "cheek": (0.78, 0.74, 0.62, 1.0),
        "cable": (0.03, 0.03, 0.035, 1.0), "hardware": (0.68, 0.70, 0.68, 1.0),
        "dark_metal": (0.10, 0.10, 0.11, 1.0), "brass": (0.95, 0.72, 0.28, 1.0),
        "label": (0.95, 0.92, 0.72, 1.0), "accent": (0.82, 0.10, 0.06, 1.0),
    },
    "safety_orange": {
        "body": (0.98, 0.35, 0.05, 1.0), "body_dark": (0.60, 0.20, 0.03, 1.0),
        "drum": (0.03, 0.03, 0.035, 1.0), "cheek": (0.05, 0.05, 0.06, 1.0),
        "cable": (0.05, 0.10, 0.20, 1.0), "hardware": (0.62, 0.64, 0.62, 1.0),
        "dark_metal": (0.05, 0.05, 0.06, 1.0), "brass": (0.80, 0.55, 0.18, 1.0),
        "label": (0.92, 0.96, 1.0, 1.0), "accent": (1.0, 0.82, 0.05, 1.0),
    },
    "industrial_yellow": {
        "body": (0.90, 0.72, 0.10, 1.0), "body_dark": (0.55, 0.44, 0.06, 1.0),
        "drum": (0.07, 0.07, 0.08, 1.0), "cheek": (0.90, 0.72, 0.10, 1.0),
        "cable": (0.03, 0.03, 0.035, 1.0), "hardware": (0.62, 0.64, 0.62, 1.0),
        "dark_metal": (0.08, 0.08, 0.09, 1.0), "brass": (0.85, 0.60, 0.20, 1.0),
        "label": (0.96, 0.96, 0.90, 1.0), "accent": (0.06, 0.06, 0.07, 1.0),
    },
    "graphite_black": {
        "body": (0.17, 0.17, 0.19, 1.0), "body_dark": (0.08, 0.08, 0.09, 1.0),
        "drum": (0.05, 0.05, 0.06, 1.0), "cheek": (0.22, 0.22, 0.24, 1.0),
        "cable": (0.62, 0.10, 0.06, 1.0), "hardware": (0.55, 0.56, 0.58, 1.0),
        "dark_metal": (0.10, 0.10, 0.11, 1.0), "brass": (0.90, 0.70, 0.30, 1.0),
        "label": (0.85, 0.85, 0.86, 1.0), "accent": (0.78, 0.12, 0.07, 1.0),
    },
    "galvanized_raw": {
        "body": (0.66, 0.68, 0.70, 1.0), "body_dark": (0.48, 0.50, 0.52, 1.0),
        "drum": (0.10, 0.10, 0.11, 1.0), "cheek": (0.60, 0.62, 0.64, 1.0),
        "cable": (0.03, 0.03, 0.035, 1.0), "hardware": (0.74, 0.76, 0.78, 1.0),
        "dark_metal": (0.12, 0.12, 0.13, 1.0), "brass": (0.90, 0.70, 0.30, 1.0),
        "label": (0.90, 0.90, 0.92, 1.0), "accent": (0.78, 0.12, 0.07, 1.0),
    },
    "hose_reel_red": {
        "body": (0.70, 0.11, 0.09, 1.0), "body_dark": (0.44, 0.06, 0.05, 1.0),
        "drum": (0.06, 0.06, 0.06, 1.0), "cheek": (0.76, 0.15, 0.11, 1.0),
        "cable": (0.03, 0.03, 0.035, 1.0), "hardware": (0.65, 0.66, 0.68, 1.0),
        "dark_metal": (0.08, 0.08, 0.09, 1.0), "brass": (0.85, 0.60, 0.20, 1.0),
        "label": (0.96, 0.96, 0.90, 1.0), "accent": (0.98, 0.90, 0.10, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Nominal dimensions (meters, pre-scale). Axle along world +X at z = AXLE_Z.   #
# ``ls`` scales all X (axle-direction) coords; ``rs`` scales reel radial feats.#
# --------------------------------------------------------------------------- #
AXLE_Z = 0.36
SUPPORT_X = 0.385   # side-support outer face |x|
RACE_X = 0.400      # bearing race center |x|
SHAFT_X = 0.435     # axle shaft/stub center |x|
NUT_X = 0.475
CHEEK_X = 0.269     # flange cheek center |x|
HUBCOLLAR_X = 0.299
HUBNECK_X = 0.375
DRUM_LEN = 0.530
DRUM_R = 0.150
DRUM_BORE = 0.052
CHEEK_R = 0.232
CHEEK_BORE = 0.055
CHEEK_THICK = 0.038
HELIX_R = 0.159
HELIX_HALF = 0.228


# --------------------------------------------------------------------------- #
# Config                                                                       #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class CableReelConfig:
    frame_form: FrameForm | None = None
    flange_form: FlangeForm | None = None
    drive_type: DriveType | None = None
    flange_feature_count: int | None = None
    palette_style: PaletteStyle = "safety_cream"
    reel_radius_scale: float = 1.0
    drum_len_scale: float = 1.0
    name: str = "cable_reel"


@dataclass(frozen=True)
class ResolvedCableReelConfig:
    frame_form: FrameForm
    flange_form: FlangeForm
    drive_type: DriveType
    n: int
    palette_style: PaletteStyle
    rs: float          # reel radial scale
    ls: float          # axle-length scale
    name: str


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> CableReelConfig:
    rng = random.Random(seed)
    return CableReelConfig(
        frame_form=rng.choice(FRAME_FORMS),
        flange_form=rng.choice(FLANGE_FORMS),
        drive_type=rng.choice(DRIVE_TYPES),
        flange_feature_count=rng.choices(_N_VALUES, weights=_N_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        reel_radius_scale=round(rng.uniform(0.92, 1.08), 4),
        drum_len_scale=round(rng.uniform(0.94, 1.06), 4),
        name=f"seeded_cable_reel_{seed}",
    )


def resolve_config(config: CableReelConfig | None = None) -> ResolvedCableReelConfig:
    cfg = config or CableReelConfig()
    n = int(cfg.flange_feature_count) if cfg.flange_feature_count is not None else 6
    return ResolvedCableReelConfig(
        frame_form=_pick(cfg.frame_form, FRAME_FORMS),
        flange_form=_pick(cfg.flange_form, FLANGE_FORMS),
        drive_type=_pick(cfg.drive_type, DRIVE_TYPES),
        n=int(_clamp(n, N_MIN, N_MAX)),
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        rs=_clamp(cfg.reel_radius_scale, 0.92, 1.08),
        ls=_clamp(cfg.drum_len_scale, 0.94, 1.06),
        name=cfg.name or "cable_reel",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCableReelConfig) else resolve_config(config)
    return (
        ("frame_form", r.frame_form),
        ("flange_form", r.flange_form),
        ("drive_type", r.drive_type),
        ("flange_n", f"n{r.n}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Shared axle hardware — the fixed-X reel-support interface (Contract 3c).     #
# --------------------------------------------------------------------------- #
def _emit_axle_hardware(frame, r, mats):
    ls = r.ls
    for suffix, sx in (("front", -1.0), ("rear", 1.0)):
        _axc(frame, f"{suffix}_bearing_race", 0.078, 0.034 * ls,
             (sx * RACE_X * ls, 0.0, AXLE_Z), mats["hardware"])
    _axc(frame, "axle_shaft", 0.032, 0.090 * ls, (-SHAFT_X * ls, 0.0, AXLE_Z), mats["hardware"])
    _axc(frame, "rear_axle_stub", 0.032, 0.090 * ls, (SHAFT_X * ls, 0.0, AXLE_Z), mats["hardware"])
    _axc(frame, "front_axle_nut", 0.045, 0.030 * ls, (-NUT_X * ls, 0.0, AXLE_Z), mats["dark_metal"])
    _axc(frame, "rear_axle_nut", 0.045, 0.030 * ls, (NUT_X * ls, 0.0, AXLE_Z), mats["dark_metal"])
    # Front rating/warning label on the front support (host-derived: on the axle face).
    # Thick enough (x) to straddle the side-support outer face across all frame forms
    # (support half-thickness varies 0.010-0.017*ls) without floating or poking through.
    frame.visual(
        Box((0.022, 0.080, 0.052)),
        origin=Origin(xyz=(-(SUPPORT_X + 0.006) * ls, 0.120, AXLE_Z + 0.070)),
        material=mats["label"], name="rating_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )


# --------------------------------------------------------------------------- #
# Frame form modules (Slot A) — grounded ``frame`` part.                       #
# --------------------------------------------------------------------------- #
def _emit_skid_base(frame, r, mats):
    """Skid U-base: two rails + rubber feet + four uprights (solid_stand/open_cage)."""
    ls = r.ls
    for idx, y in ((0, -0.235), (1, 0.235)):
        frame.visual(Box((0.86 * ls, 0.035, 0.045)), origin=Origin(xyz=(0.0, y, 0.045)),
                     material=mats["body"], name=f"base_rail_{idx}", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
    for idx, (x, y) in enumerate(((-0.39, -0.235), (-0.39, 0.235), (0.39, -0.235), (0.39, 0.235))):
        frame.visual(Box((0.085 * ls, 0.075, 0.018)), origin=Origin(xyz=(x * ls, y, 0.014)),
                     material=mats["body_dark"], name=f"rubber_foot_{idx}", material_class_id="rubber.smooth_plain")
    for idx, (x, y) in enumerate(((-SUPPORT_X, -0.205), (-SUPPORT_X, 0.205),
                                  (SUPPORT_X, -0.205), (SUPPORT_X, 0.205))):
        frame.visual(Box((0.050 * ls, 0.040, 0.230)), origin=Origin(xyz=(x * ls, y, 0.148)),
                     material=mats["body"], name=f"rail_upright_{idx}", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))


def _solid_side_profile():
    # (y, z)-about-axle solid side plate with lightening holes.
    outer = [(-0.315, -0.205), (-0.315, 0.185), (-0.150, 0.165), (0.145, 0.095),
             (0.285, 0.020), (0.235, -0.115), (0.055, -0.190)]
    holes = [circle_profile(0.066, 48),
             offset_profile(circle_profile(0.045, 24), -0.235, -0.105),
             offset_profile(circle_profile(0.030, 20), -0.205, 0.132)]
    return outer, holes


def _build_solid_stand(frame, r, mats):
    ls = r.ls
    _emit_skid_base(frame, r, mats)
    outer, holes = _solid_side_profile()
    mesh = plate_yz(outer, holes, 0.034 * ls)
    for suffix, sx in (("front", -1.0), ("rear", 1.0)):
        frame.visual(mesh_from_geometry(mesh, f"{suffix}_support_mesh"),
                     origin=Origin(xyz=(sx * SUPPORT_X * ls, 0.0, AXLE_Z)),
                     material=mats["body"], name=f"{suffix}_support", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))


def _cage_side_profile():
    outer = [(-0.310, -0.280), (0.310, -0.280), (0.292, -0.195), (0.248, 0.110),
             (0.162, 0.200), (-0.162, 0.200), (-0.248, 0.110), (-0.292, -0.195)]
    holes = [circle_profile(0.050, 40),
             [(-0.242, -0.188), (-0.184, 0.076), (-0.046, 0.004)],
             [(0.046, 0.004), (0.184, 0.076), (0.242, -0.188)],
             [(-0.190, -0.232), (-0.036, -0.062), (-0.004, -0.228)],
             [(0.004, -0.228), (0.036, -0.062), (0.190, -0.232)],
             [(-0.105, 0.130), (0.105, 0.130), (0.105, 0.175), (-0.105, 0.175)]]  # top carry handle
    return outer, holes


def _build_open_cage(frame, r, mats):
    ls = r.ls
    _emit_skid_base(frame, r, mats)
    outer, holes = _cage_side_profile()
    mesh = plate_yz(outer, holes, 0.020 * ls)
    for suffix, sx in (("front", -1.0), ("rear", 1.0)):
        frame.visual(mesh_from_geometry(mesh, f"{suffix}_support_mesh"),
                     origin=Origin(xyz=(sx * SUPPORT_X * ls, 0.0, AXLE_Z)),
                     material=mats["body"], name=f"{suffix}_support", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
    # Tie-rod cage joining the two cheeks (galvanized), spanning the width.
    rod_len = 2.0 * (SUPPORT_X - 0.010) * ls
    # Only the lower cross-rods: the upper rods cannot sit on the narrowing plate top
    # AND clear the spinning spool cheek at once, so they are dropped (sides stay joined
    # by the lower rods + skid base).
    for idx, (y, zrel) in enumerate(((-0.250, -0.220), (0.250, -0.220))):
        _axc(frame, f"tie_rod_{idx}", 0.011, rod_len, (0.0, y, AXLE_Z + zrel), mats["hardware"])


def _build_wheeled_cart(frame, r, mats):
    ls = r.ls
    # Solid side plates (same interface as solid_stand).
    outer, holes = _solid_side_profile()
    mesh = plate_yz(outer, holes, 0.034 * ls)
    for suffix, sx in (("front", -1.0), ("rear", 1.0)):
        frame.visual(mesh_from_geometry(mesh, f"{suffix}_support_mesh"),
                     origin=Origin(xyz=(sx * SUPPORT_X * ls, 0.0, AXLE_Z)),
                     material=mats["body"], name=f"{suffix}_support", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
    # Raised cart base + uprights.
    base_z = 0.150
    for idx, y in ((0, -0.235), (1, 0.235)):
        frame.visual(Box((0.80 * ls, 0.040, 0.050)), origin=Origin(xyz=(0.0, y, base_z)),
                     material=mats["body"], name=f"base_rail_{idx}", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
    for idx, (x, y) in enumerate(((-SUPPORT_X, -0.205), (-SUPPORT_X, 0.205),
                                  (SUPPORT_X, -0.205), (SUPPORT_X, 0.205))):
        frame.visual(Box((0.048 * ls, 0.040, 0.100)), origin=Origin(xyz=(x * ls, y, base_z + 0.075)),
                     material=mats["body"], name=f"rail_upright_{idx}", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
    # Two wheels on a cross axle (cylinder rim + rubber tire torus).
    wheel_r, wheel_y, wheel_x = 0.075, 0.300, -0.060
    frame.visual(Cylinder(radius=0.014, length=2.0 * wheel_y + 0.050),
                 origin=Origin(xyz=(wheel_x * ls, 0.0, wheel_r), rpy=(math.pi / 2.0, 0.0, 0.0)),
                 material=mats["hardware"], name="cross_axle_bar", material_class_id="metal.steel_bare")
    for idx, ysign in ((0, -1.0), (1, 1.0)):
        # fork leg from base rail down to wheel axle
        frame.visual(Box((0.040 * ls, 0.050, base_z - wheel_r + 0.030)),
                     origin=Origin(xyz=(wheel_x * ls, ysign * 0.235, (base_z + wheel_r) / 2.0)),
                     material=mats["body"], name=f"wheel_fork_{idx}", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
        frame.visual(Cylinder(radius=wheel_r * 0.62, length=0.034),
                     origin=Origin(xyz=(wheel_x * ls, ysign * wheel_y, wheel_r),
                                   rpy=(0.0, math.pi / 2.0, 0.0)),
                     material=mats["hardware"], name=f"wheel_rim_{idx}", material_class_id="metal.steel_bare")
        frame.visual(mesh_from_geometry(torus_around_x(wheel_r * 0.86, wheel_r * 0.20,
                                                       tubular_segments=40), f"wheel_tire_{idx}_m"),
                     origin=Origin(xyz=(wheel_x * ls, ysign * wheel_y, wheel_r)),
                     material=mats["cable"], name=f"wheel_tire_{idx}", material_class_id="rubber.smooth_plain")
    # Trolley push-handle behind the reel.
    for idx, ysign in ((0, -1.0), (1, 1.0)):
        post_path = [(0.40 * ls, ysign * 0.205, base_z),
                     (0.47 * ls, ysign * 0.205, 0.42),
                     (0.49 * ls, ysign * 0.205, 0.60)]
        frame.visual(mesh_from_geometry(tube_from_spline_points(
            post_path, radius=0.013, samples_per_segment=6, radial_segments=10),
            f"trolley_post_{idx}_m"), origin=Origin(), material=mats["body"],
            name=f"trolley_post_{idx}", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
    frame.visual(Cylinder(radius=0.015, length=0.44),
                 origin=Origin(xyz=(0.49 * ls, 0.0, 0.60), rpy=(math.pi / 2.0, 0.0, 0.0)),
                 material=mats["cable"], name="trolley_grip_bar", material_class_id="rubber.smooth_plain")


def _build_closed_housing(frame, r, mats):
    ls = r.ls
    rim_out, rim_in = 0.285, 0.262
    panel_t = 0.022
    hw = SUPPORT_X  # shell face at |x|=SUPPORT_X
    for suffix, sx in (("front", -1.0), ("rear", 1.0)):
        profile = circle_profile(rim_out, 72)
        holes = [circle_profile(0.054, 48)]
        if sx < 0:  # cable exit slot on the front shell
            holes.append([(-0.036, -0.230), (0.036, -0.230), (0.036, -0.130), (-0.036, -0.130)])
        else:  # ventilation slots on the rear shell
            for i in range(4):
                a = math.pi / 4.0 + i * math.pi / 2.0
                holes.append(offset_profile(circle_profile(0.018, 16),
                                            0.180 * math.cos(a), 0.180 * math.sin(a)))
        mesh = plate_yz(profile, holes, panel_t * ls)
        frame.visual(mesh_from_geometry(mesh, f"{suffix}_support_mesh"),
                     origin=Origin(xyz=(sx * (hw - panel_t / 2.0) * ls, 0.0, AXLE_Z)),
                     material=mats["body"], name=f"{suffix}_support", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
    rim_span = 2.0 * (hw - panel_t) * ls
    frame.visual(mesh_from_geometry(annular_yz(rim_out, rim_in, rim_span, segments=72), "rim_mesh"),
                 origin=Origin(xyz=(0.0, 0.0, AXLE_Z)), material=mats["body"], name="housing_rim", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
    # Two feet from the housing bottom to the ground.
    foot_h = AXLE_Z - rim_out
    for idx, x in ((0, -0.160), (1, 0.160)):
        frame.visual(Box((0.062 * ls, 0.180, foot_h)),
                     origin=Origin(xyz=(x * ls, 0.0, foot_h / 2.0)),
                     material=mats["body"], name=f"base_foot_{idx}", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
        frame.visual(Box((0.072 * ls, 0.192, 0.010)),
                     origin=Origin(xyz=(x * ls, 0.0, 0.005)),
                     material=mats["body_dark"], name=f"base_plate_{idx}", material_class_id="metal.paint_coated")


def _build_wall_bracket(frame, r, mats):
    ls = r.ls
    wall_y = 0.310
    plate_t = 0.014
    # Flat wall mounting plate (spans past both brackets).
    frame.visual(Box((0.84 * ls, plate_t, 0.46)),
                 origin=Origin(xyz=(0.0, wall_y + plate_t / 2.0, 0.30)),
                 material=mats["hardware"], name="wall_mounting_plate", material_class_id="metal.steel_galvanized")
    # Two trapezoidal A-brackets (front/rear) reaching from the wall to the axle.
    for suffix, sx in (("front", -1.0), ("rear", 1.0)):
        outer = [(wall_y, 0.150), (0.030, 0.055), (0.030, -0.055), (wall_y, -0.190)]
        holes = [[(wall_y - 0.060, 0.060), (0.120, 0.030), (0.120, -0.040)]]  # lightening
        mesh = plate_yz([(y, z) for (y, z) in outer], holes, 0.012 * ls)
        frame.visual(mesh_from_geometry(mesh, f"{suffix}_support_mesh"),
                     origin=Origin(xyz=(sx * SUPPORT_X * ls, 0.0, AXLE_Z)),
                     material=mats["hardware"], name=f"{suffix}_support", material_class_id="metal.steel_galvanized")
        # Bearing saddle block at the arm tip cradling the axle.
        frame.visual(Box((0.030 * ls, 0.058, 0.070)),
                     origin=Origin(xyz=(sx * SUPPORT_X * ls, 0.020, AXLE_Z)),
                     material=mats["hardware"], name=f"bearing_saddle_{suffix}", material_class_id="metal.steel_galvanized")
    # Wall anchor bolts.
    bi = 0
    for x in (-0.300, 0.0, 0.300):
        for z in (0.48, 0.12):
            frame.visual(Cylinder(radius=0.009, length=0.008),
                         origin=Origin(xyz=(x * ls, wall_y - 0.001, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                         material=mats["dark_metal"], name=f"wall_bolt_{bi}", material_class_id="metal.blackened_gunmetal")
            bi += 1
    frame.visual(Cylinder(radius=0.010, length=0.006),
                 origin=Origin(xyz=(-0.250 * ls, wall_y - 0.001, 0.150), rpy=(math.pi / 2.0, 0.0, 0.0)),
                 material=mats["brass"], name="grounding_lug", material_class_id="metal.brass_polished")


_FRAME_BUILDERS = {
    "solid_stand": _build_solid_stand,
    "open_cage": _build_open_cage,
    "closed_housing": _build_closed_housing,
    "wall_bracket": _build_wall_bracket,
    "wheeled_cart": _build_wheeled_cart,
}


# --------------------------------------------------------------------------- #
# Reel core (drum + hub + wound cable + outlet) — always emitted.              #
# --------------------------------------------------------------------------- #
def _emit_reel_core(reel, r, mats):
    ls, rs = r.ls, r.rs
    # Round annular drum barrel (never a Box).
    reel.visual(mesh_from_geometry(annular_yz(DRUM_R * rs, DRUM_BORE * rs, DRUM_LEN * ls, segments=64),
                                   "drum_core_mesh"),
                origin=Origin(), material=mats["drum"], name="drum_core", material_class_id="metal.paint_coated")
    # Hub collars + hub necks (align with the bearing races, pass the supports).
    for suffix, sx in (("front", -1.0), ("rear", 1.0)):
        reel.visual(mesh_from_geometry(annular_yz(0.088 * rs, 0.044 * rs, 0.052 * ls, segments=48),
                                       f"{suffix}_hub_collar_mesh"),
                    origin=Origin(xyz=(sx * HUBCOLLAR_X * ls, 0.0, 0.0)),
                    material=mats["cheek"], name=f"{suffix}_hub_collar", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
        _axc(reel, f"{suffix}_hub_neck", 0.026 * rs, 0.164 * ls,
             (sx * HUBNECK_X * ls, 0.0, 0.0), mats["hardware"])
    # Single wound-cable helix.
    turns = 18
    samples = turns * 8 + 1
    pts = []
    for i in range(samples):
        t = i / (samples - 1)
        x = (-HELIX_HALF + 2.0 * HELIX_HALF * t) * ls
        a = TAU * turns * t
        pts.append((x, HELIX_R * rs * math.cos(a), HELIX_R * rs * math.sin(a)))
    reel.visual(mesh_from_geometry(tube_from_spline_points(
        pts, radius=0.0085 * rs, samples_per_segment=2, radial_segments=12, cap_ends=True),
        "wound_cable_mesh"), origin=Origin(), material=mats["cable"], name="wound_cable", material_class_id="tech.cable_pipe_bundle")
    # Electrical outlet block on the front cheek (rotates with reel).
    reel.visual(Box((0.040 * ls, 0.094 * rs, 0.066 * rs)),
                origin=Origin(xyz=(-0.300 * ls, -0.108 * rs, 0.080 * rs)),
                material=mats["drum"], name="outlet_block", material_class_id="plastic.opaque_glossy_molded")
    for i, dz in enumerate((-0.018, 0.018)):
        _axc(reel, f"socket_face_{i}", 0.014 * rs, 0.006 * ls,
             (-0.322 * ls, -0.108 * rs, (0.080 + dz) * rs), mats["dark_metal"])
        _axc(reel, f"brass_terminal_{i}", 0.004 * rs, 0.006 * ls,
             (-0.326 * ls, -0.108 * rs, (0.080 + dz) * rs), mats["brass"])
    reel.visual(Box((0.004 * ls, 0.070 * rs, 0.022 * rs)),
                origin=Origin(xyz=(-0.320 * ls, -0.108 * rs, 0.034 * rs)),
                material=mats["label"], name="warning_label", appearance_only=AppearanceOnlySpec(kind="decal"))


# --------------------------------------------------------------------------- #
# Flange modules (Slot B) — the reel cheek discs (round meshes only).          #
# --------------------------------------------------------------------------- #
def _emit_flange_common(reel, r, mats, cheek_mesh):
    ls, rs = r.ls, r.rs
    for suffix, sx in (("front", -1.0), ("rear", 1.0)):
        reel.visual(mesh_from_geometry(cheek_mesh, f"{suffix}_spool_cheek_mesh"),
                    origin=Origin(xyz=(sx * CHEEK_X * ls, 0.0, 0.0)),
                    material=mats["cheek"], name=f"{suffix}_spool_cheek", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))
        reel.visual(mesh_from_geometry(torus_around_x(0.220 * rs, 0.012 * rs, tubular_segments=48),
                                       f"{suffix}_rolled_lip_mesh"),
                    origin=Origin(xyz=(sx * (CHEEK_X + 0.002) * ls, 0.0, 0.0)),
                    material=mats["cheek"], name=f"{suffix}_rolled_lip", material_class_id=("metal.steel_galvanized" if r.palette_style == "galvanized_raw" else "metal.paint_coated"))


def _emit_solid_disc(reel, r, mats):
    ls, rs = r.ls, r.rs
    cheek_mesh = annular_yz(CHEEK_R * rs, CHEEK_BORE * rs, CHEEK_THICK * ls, segments=72)
    _emit_flange_common(reel, r, mats, cheek_mesh)
    for i in range(r.n):
        a = TAU * i / r.n + math.radians(12.0)
        _axc(reel, f"flange_bolt_{i}", 0.007 * rs, 0.008 * ls,
             (-(CHEEK_X + 0.022) * ls, 0.150 * rs * math.cos(a), 0.150 * rs * math.sin(a)),
             mats["hardware"])


def _emit_spoked_disc(reel, r, mats):
    ls, rs = r.ls, r.rs
    cheek_mesh = spoked_disc_yz(CHEEK_R * rs, CHEEK_BORE * rs, CHEEK_THICK * ls,
                                n_spokes=r.n, spoke_width_angle=math.radians(13.0),
                                gap_inner_r=0.088 * rs, gap_outer_r=0.205 * rs,
                                segments=72, arc_segments=12)
    _emit_flange_common(reel, r, mats, cheek_mesh)
    for i in range(r.n):
        a = TAU * i / r.n
        _axc(reel, f"spoke_bolt_{i}", 0.007 * rs, 0.008 * ls,
             (-(CHEEK_X + 0.022) * ls, 0.072 * rs * math.cos(a), 0.072 * rs * math.sin(a)),
             mats["hardware"])


_FLANGE_BUILDERS = {"solid_disc": _emit_solid_disc, "spoked_disc": _emit_spoked_disc}


# --------------------------------------------------------------------------- #
# Drive modules (Slot C).                                                      #
# --------------------------------------------------------------------------- #
# Crank pin location in reel-local coords (pre-scale nominal offsets).
_PIN = (-0.500, -0.130, -0.170)


def _emit_crank_arm(reel, r, mats):
    ls, rs = r.ls, r.rs
    _axc(reel, "crank_root_boss", 0.034 * rs, 0.030 * ls, (-0.436 * ls, 0.0, 0.0), mats["hardware"])
    pts = [(-0.420 * ls, 0.0, 0.0), (-0.430 * ls, -0.045 * rs, -0.055 * rs),
           (-0.462 * ls, -0.100 * rs, -0.132 * rs), (_PIN[0] * ls, _PIN[1] * rs, _PIN[2] * rs)]
    reel.visual(mesh_from_geometry(tube_from_spline_points(
        pts, radius=0.0075 * rs, samples_per_segment=10, radial_segments=12), "crank_arm_mesh"),
        origin=Origin(), material=mats["hardware"], name="crank_arm", material_class_id="metal.steel_bare")
    _axc(reel, "crank_pin", 0.008 * rs, 0.110 * ls,
         (-0.555 * ls, _PIN[1] * rs, _PIN[2] * rs), mats["hardware"])
    _axc(reel, "crank_washer", 0.020 * rs, 0.012 * ls,
         (-0.506 * ls, _PIN[1] * rs, _PIN[2] * rs), mats["hardware"])


def _emit_fixed_knob(reel, r, mats):
    ls, rs = r.ls, r.rs
    _axc(reel, "crank_knob", 0.019 * rs, 0.052 * ls,
         (-0.585 * ls, _PIN[1] * rs, _PIN[2] * rs), mats["cable"])
    reel.visual(Box((0.006 * ls, 0.006 * rs, 0.052 * rs)),
                origin=Origin(xyz=(-0.585 * ls, _PIN[1] * rs, (_PIN[2] + 0.0) * rs)),
                material=mats["body_dark"], name="knob_rib", material_class_id="plastic.opaque_generic")


def _emit_grip(grip, r, mats):
    ls, rs = r.ls, r.rs
    _axc(grip, "rubber_sleeve", 0.018 * rs, 0.086 * ls, (-0.056 * ls, 0.0, 0.0), mats["cable"])
    grip.visual(Box((0.075 * ls, 0.006 * rs, 0.006 * rs)),
                origin=Origin(xyz=(-0.056 * ls, 0.0, 0.018 * rs)),
                material=mats["body_dark"], name="grip_rib", material_class_id="rubber.smooth_plain")
    _axc(grip, "end_cap", 0.019 * rs, 0.006 * ls, (-0.102 * ls, 0.0, 0.0), mats["dark_metal"])


def _emit_motor(frame, r, mats):
    """Electric motor + gearbox on the +X frame side (outboard of the rear support)."""
    ls = r.ls
    base_x = SUPPORT_X + 0.020  # just outside the rear support
    frame.visual(Box((0.010 * ls, 0.105, 0.105)),
                 origin=Origin(xyz=((base_x + 0.005) * ls, 0.0, AXLE_Z)),
                 material=mats["hardware"], name="motor_mount_plate", material_class_id="metal.steel_galvanized")
    gb_x0 = base_x + 0.010
    gb_len = 0.058
    frame.visual(Box((gb_len * ls, 0.084, 0.084)),
                 origin=Origin(xyz=((gb_x0 + gb_len / 2.0) * ls, 0.0, AXLE_Z)),
                 material=mats["dark_metal"], name="gearbox_housing", material_class_id="metal.blackened_gunmetal")
    frame.visual(Box((0.006 * ls, 0.092, 0.092)),
                 origin=Origin(xyz=((gb_x0 + gb_len / 2.0) * ls, 0.0, AXLE_Z)),
                 material=mats["hardware"], name="gearbox_flange", material_class_id="metal.steel_bare")
    # Output shaft reaching inward toward the reel drive gear.
    shaft_in, shaft_out = 0.285, gb_x0
    frame.visual(Cylinder(radius=0.013, length=(shaft_out - shaft_in) * ls),
                 origin=Origin(xyz=((shaft_in + shaft_out) / 2.0 * ls, 0.0, AXLE_Z),
                               rpy=(0.0, math.pi / 2.0, 0.0)),
                 material=mats["hardware"], name="gearbox_output_shaft", material_class_id="metal.stainless_matte")
    _axc(frame, "shaft_bearing_collar", 0.022, 0.012 * ls, ((base_x + 0.001) * ls, 0.0, AXLE_Z),
         mats["hardware"])
    motor_x0 = gb_x0 + gb_len
    motor_len, motor_r = 0.105, 0.044
    frame.visual(Cylinder(radius=motor_r, length=motor_len * ls),
                 origin=Origin(xyz=((motor_x0 + motor_len / 2.0) * ls, 0.0, AXLE_Z),
                               rpy=(0.0, math.pi / 2.0, 0.0)),
                 material=mats["dark_metal"], name="motor_body", material_class_id="metal.blackened_gunmetal")
    for i in range(8):
        a = TAU * i / 8.0
        fin_r = motor_r + 0.002
        frame.visual(Box(((motor_len - 0.010) * ls, 0.004, 0.006)),
                     origin=Origin(xyz=((motor_x0 + motor_len / 2.0) * ls,
                                        fin_r * math.cos(a), AXLE_Z + fin_r * math.sin(a)),
                                   rpy=(a, 0.0, 0.0)),
                     material=mats["dark_metal"], name=f"motor_fin_{i}", material_class_id="metal.blackened_gunmetal")
    _axc(frame, "motor_end_bell", motor_r + 0.004, 0.016 * ls,
         ((motor_x0 + motor_len + 0.008) * ls, 0.0, AXLE_Z), mats["hardware"])
    frame.visual(Box((0.042 * ls, 0.028, 0.030)),
                 origin=Origin(xyz=((motor_x0 + motor_len * 0.38) * ls, 0.0, AXLE_Z + motor_r + 0.014)),
                 material=mats["dark_metal"], name="motor_terminal_box", material_class_id="metal.blackened_gunmetal")
    frame.visual(Box((0.048 * ls, 0.003, 0.022)),
                 origin=Origin(xyz=((motor_x0 + motor_len * 0.45) * ls, motor_r + 0.001, AXLE_Z)),
                 material=mats["label"], name="motor_nameplate", appearance_only=AppearanceOnlySpec(kind="decal"))


def _emit_drive_gear(reel, r, mats):
    ls, rs = r.ls, r.rs
    gear_x = 0.300
    reel.visual(mesh_from_geometry(annular_yz(0.044 * rs, 0.020 * rs, 0.014 * ls, segments=40),
                                   "drive_gear_mesh"),
                origin=Origin(xyz=(gear_x * ls, 0.0, 0.0)), material=mats["hardware"], name="drive_gear", material_class_id="metal.steel_bare")
    for i in range(16):
        a = TAU * i / 16.0
        reel.visual(Box((0.012 * ls, 0.008 * rs, 0.010 * rs)),
                    origin=Origin(xyz=(gear_x * ls, 0.046 * rs * math.cos(a), 0.046 * rs * math.sin(a)),
                                  rpy=(a, 0.0, 0.0)),
                    material=mats["hardware"], name=f"gear_tooth_{i}", material_class_id="metal.steel_bare")


# --------------------------------------------------------------------------- #
# Build                                                                        #
# --------------------------------------------------------------------------- #
def build_cable_reel(config: CableReelConfig | None = None, *,
                     assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets,
                              meta={"domain": "Electrical_Wiring", "small_class": "Cable reel"})
    mats = {k: model.material(f"cr_{k}_{r.palette_style}", rgba=rgba)
            for k, rgba in PALETTES[r.palette_style].items()}

    frame = model.part("frame")
    _FRAME_BUILDERS[r.frame_form](frame, r, mats)
    _emit_axle_hardware(frame, r, mats)
    if r.drive_type == "motorized":
        _emit_motor(frame, r, mats)

    reel = model.part("reel")
    _emit_reel_core(reel, r, mats)
    _FLANGE_BUILDERS[r.flange_form](reel, r, mats)
    if r.drive_type in ("crank_free_grip", "crank_fixed_knob"):
        _emit_crank_arm(reel, r, mats)
        if r.drive_type == "crank_fixed_knob":
            _emit_fixed_knob(reel, r, mats)
    elif r.drive_type == "motorized":
        _emit_drive_gear(reel, r, mats)

    # Primary joint: reel spins freely about the +X axle (captured journal).
    model.articulation(
        "frame_to_reel", ArticulationType.CONTINUOUS, parent=frame, child=reel,
        origin=Origin(xyz=(0.0, 0.0, AXLE_Z)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=5.0),
    )

    if r.drive_type == "crank_free_grip":
        grip = model.part("crank_grip")
        _emit_grip(grip, r, mats)
        model.articulation(
            "reel_to_crank_grip", ArticulationType.CONTINUOUS, parent=reel, child=grip,
            origin=Origin(xyz=(_PIN[0] * r.ls, _PIN[1] * r.rs, _PIN[2] * r.rs)),
            axis=(1.0, 0.0, 0.0), motion_limits=MotionLimits(effort=2.0, velocity=8.0),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_cable_reel(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_cable_reel(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests                                                                        #
# --------------------------------------------------------------------------- #
def _allow_captured(ctx, model, r):
    frame = model.get_part("frame")
    reel = model.get_part("reel")
    # Reel hub necks captured in the bearing races / axle stubs / supports.
    for suffix, race, shaft in (("front", "front_bearing_race", "axle_shaft"),
                                ("rear", "rear_bearing_race", "rear_axle_stub")):
        for elem_a in (race, shaft, f"{suffix}_support"):
            ctx.allow_overlap(frame, reel, elem_a=elem_a, elem_b=f"{suffix}_hub_neck",
                              reason="Rotating hub neck is journaled through the bearing/support (captured).")
    if r.frame_form == "wall_bracket":
        for suffix in ("front", "rear"):
            ctx.allow_overlap(frame, reel, elem_a=f"bearing_saddle_{suffix}", elem_b=f"{suffix}_hub_neck",
                              reason="Rotating hub neck is cradled in the wall-bracket bearing saddle (captured).")
    if r.frame_form == "closed_housing":
        for suffix in ("front", "rear"):
            ctx.allow_overlap(frame, reel, elem_a="housing_rim", elem_b=f"{suffix}_hub_neck",
                              reason="Drum hub neck passes through the enclosed housing rim opening (journal).")
    if r.drive_type in ("crank_free_grip", "crank_fixed_knob"):
        for elem_a in ("axle_shaft", "front_bearing_race"):
            ctx.allow_overlap(frame, reel, elem_a=elem_a, elem_b="crank_arm",
                              reason="Crank arm root is keyed onto the projecting front axle/bearing.")
            ctx.allow_overlap(frame, reel, elem_a=elem_a, elem_b="crank_root_boss",
                              reason="Crank root boss clamps around the front axle end.")
    if r.drive_type == "crank_free_grip":
        grip = model.get_part("crank_grip")
        ctx.allow_overlap(grip, reel, elem_a="rubber_sleeve", elem_b="crank_pin",
                          reason="Free-spinning rubber grip sleeve rides on its metal handle pin.")
        ctx.allow_overlap(grip, reel, elem_a="end_cap", elem_b="crank_pin",
                          reason="Molded end cap retains the grip on the pin.")
    if r.drive_type == "motorized":
        ctx.allow_overlap(frame, reel, elem_a="gearbox_output_shaft", elem_b="rear_hub_neck",
                          reason="Gearbox output shaft couples into the rear hub (captured drive).")
        ctx.allow_overlap(frame, reel, elem_a="gearbox_output_shaft", elem_b="drive_gear",
                          reason="Gearbox output pinion meshes with the reel-side driven gear.")
        for elem_a in ("gearbox_housing", "gearbox_flange", "gearbox_output_shaft",
                       "motor_mount_plate", "drive_gear", "shaft_bearing_collar"):
            for elem_b in ("rear_hub_neck", "rear_hub_collar"):
                ctx.allow_overlap(frame, reel, elem_a=elem_a, elem_b=elem_b,
                                  reason="Motorized gearbox/mount couples the rear hub (captured drive).")


def _aabb_center(aabb):
    if aabb is None:
        return None
    lo, hi = aabb
    return tuple((lo[i] + hi[i]) * 0.5 for i in range(3))


def run_cable_reel_tests(object_model: ArticulatedObject, config: CableReelConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    reel = object_model.get_part("reel")
    spin = object_model.get_articulation("frame_to_reel")

    _allow_captured(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # --- Identity ---
    ctx.check(
        "small class is Cable reel",
        object_model.meta.get("small_class") == "Cable reel" and "cable_reel" in object_model.name,
        details=f"name={object_model.name}, meta={object_model.meta}",
    )

    # --- Primary spin joint: CONTINUOUS about +X in every frame form ---
    ctx.check(
        "reel spins freely on the +X axle (CONTINUOUS)",
        spin.articulation_type == ArticulationType.CONTINUOUS
        and tuple(round(v, 3) for v in spin.axis) == (1.0, 0.0, 0.0),
        details=f"type={spin.articulation_type}, axis={spin.axis}",
    )

    # --- Reel is a round drum + two flange cheeks + wound cable ---
    reel_names = {v.name for v in reel.visuals}
    ctx.check(
        "round drum + two cheeks + wound cable present",
        {"drum_core", "front_spool_cheek", "rear_spool_cheek", "wound_cable"} <= reel_names,
        details=f"reel visuals={sorted(reel_names)}",
    )
    # Drum barrel reads round (square-ish yz AABB, ~ 2*drum_radius).
    drum_aabb = ctx.part_element_world_aabb(reel, elem="drum_core")
    if drum_aabb is not None:
        dy = drum_aabb[1][1] - drum_aabb[0][1]
        dz = drum_aabb[1][2] - drum_aabb[0][2]
        ctx.check(
            "drum barrel is round (annular, not a box)",
            dy > 0.24 and dz > 0.24 and abs(dy - dz) < 0.03,
            details=f"dy={dy:.3f} dz={dz:.3f}",
        )

    # --- Frame form realized its signature support ---
    frame_names = {v.name for v in frame.visuals}
    ctx.check(
        "frame form provides front/rear reel supports",
        {"front_support", "rear_support"} <= frame_names,
        details=f"frame_form={r.frame_form} visuals={sorted(frame_names)[:12]}",
    )

    # --- Drive type structural expectations ---
    if r.drive_type == "crank_free_grip":
        grip = object_model.get_part("crank_grip")
        grip_joint = object_model.get_articulation("reel_to_crank_grip")
        ctx.check(
            "free grip is a second CONTINUOUS joint on the crank pin",
            grip_joint.articulation_type == ArticulationType.CONTINUOUS
            and tuple(round(v, 3) for v in grip_joint.axis) == (1.0, 0.0, 0.0)
            and grip.get_visual("rubber_sleeve") is not None,
            details=f"type={grip_joint.articulation_type}, axis={grip_joint.axis}",
        )
    elif r.drive_type == "crank_fixed_knob":
        ctx.check(
            "fixed-knob crank has no second joint",
            "crank_knob" in reel_names
            and all(a.name != "reel_to_crank_grip" for a in object_model.articulations),
            details=f"reel={sorted(reel_names)}",
        )
    else:  # motorized
        ctx.check(
            "motorized drive: motor+gearbox on frame, driven gear on reel, no crank",
            {"motor_body", "gearbox_housing"} <= frame_names
            and "drive_gear" in reel_names
            and "crank_arm" not in reel_names,
            details=f"frame={sorted(frame_names)[:10]} reel_has_gear={'drive_gear' in reel_names}",
        )

    # --- Flange multiplicity realized ---
    if r.flange_form == "spoked_disc":
        n_bolts = sum(1 for v in reel.visuals if v.name.startswith("spoke_bolt_"))
    else:
        n_bolts = sum(1 for v in reel.visuals if v.name.startswith("flange_bolt_"))
    ctx.check(
        "flange feature multiplicity N realized",
        n_bolts == r.n,
        details=f"flange_form={r.flange_form} count={n_bolts} N={r.n}",
    )

    # --- Frame is grounded (rests near z=0), except wall_bracket (wall-mounted) ---
    if r.frame_form != "wall_bracket":
        f_aabb = ctx.part_world_aabb(frame)
        ctx.check(
            "reel stand rests on the ground",
            f_aabb is not None and f_aabb[0][2] < 0.03,
            details=f"frame aabb min z={None if f_aabb is None else f_aabb[0][2]:.3f}",
        )

    # --- Off-axis proof: a quarter turn carries the outlet block around the axle ---
    rest = _aabb_center(ctx.part_element_world_aabb(reel, elem="outlet_block"))
    with ctx.pose({spin: math.pi / 2.0}):
        turned = _aabb_center(ctx.part_element_world_aabb(reel, elem="outlet_block"))
    ctx.check(
        "reel spin visibly carries the outlet block around the axle",
        rest is not None and turned is not None
        and abs(rest[1] - turned[1]) + abs(rest[2] - turned[2]) > 0.05,
        details=f"rest={rest}, turned={turned}",
    )

    # --- Grip spin proof (free-grip drive) ---
    if r.drive_type == "crank_free_grip":
        grip = object_model.get_part("crank_grip")
        grip_joint = object_model.get_articulation("reel_to_crank_grip")
        base_rib = _aabb_center(ctx.part_element_world_aabb(grip, elem="grip_rib"))
        with ctx.pose({grip_joint: math.pi / 2.0}):
            spun_rib = _aabb_center(ctx.part_element_world_aabb(grip, elem="grip_rib"))
        ctx.check(
            "crank grip rib moves when the handle spins",
            base_rib is not None and spun_rib is not None
            and abs(base_rib[1] - spun_rib[1]) + abs(base_rib[2] - spun_rib[2]) > 0.008,
            details=f"rest={base_rib}, spun={spun_rib}",
        )

    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )
    return ctx.report()


__all__ = (
    "CableReelConfig",
    "ResolvedCableReelConfig",
    "build_cable_reel",
    "build_seeded_cable_reel",
    "config_from_seed",
    "resolve_config",
    "run_cable_reel_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
