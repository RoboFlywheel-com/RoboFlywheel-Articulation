# SPDX-License-Identifier: Apache-2.0

"""Upholstered single-seat armchair (lounge / office / gaming / pod) modular template.

NOTE on the slug: "armchair" here = an upholstered single-seat lounge / office /
gaming / pod chair = soft seat + backrest + a pair of armrests + a support /
swivel / recline mechanism. It is NOT a folding_chair (scissor fold), a sofa
(multi-seat), or a backless stool.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_armchair.md`` and the
``picture/Other/armchair`` 5-star sample pool (4 parents + 6 slot-fork
variants), all synced under ``data/records/``.

Structure (pattern = ``mixed``). A serial spine ``support(root) -> seat ->
backrest`` with four named axes plus a caster multiplicity axis:

  * ``chair_form`` (4): winged_lounge / egg_pod / office_mesh / racing_bucket —
    chooses the seat + backrest shell/cushion mesh family. ``office_mesh`` is
    the absorbed blue-mesh ergonomic office-chair baseline (mesh back, lumbar
    support, adjustable-arm compatibility). This is a mesh-helper dimension; it
    does not add a cross-slot joint.
  * ``base_support`` (3): the ROOT mechanism.
      - five_star_caster: ``pedestal_anchor`` root -> 1 CONTINUOUS pedestal
        swivel for only the wheeled star base, plus an independent gas-lift
        branch: ``base`` (5-spoke star + caster hardware) -> N CONTINUOUS
        caster wheels, and ``pedestal_anchor`` -> 1 PRISMATIC gas lift -> 1
        CONTINUOUS swivel under the seat.
      - four_wood_legs: ``seat`` is the root (4 splayed legs are inline
        visuals, no support joint).
      - cantilever_sled: ``sled_base`` root (bent tubular frame) -> 1
        CONTINUOUS swivel under the seat.
  * ``recline_mechanism`` (3): the seat<->backrest joint topology.
      - swivel_tilt: backrest REVOLUTE +Y recline.
      - rocker_glider: backrest REVOLUTE +Y recline + 1 extra REVOLUTE rocker
        ``rocker`` (a low transverse rock axis between root and seat region).
      - full_recliner_footrest: backrest REVOLUTE +Y (extended travel) + 1
        extra PRISMATIC ``footrest`` sliding out from the seat front.
  * ``armrest`` (3): the armrest part/joint topology.
      - fixed_arms: armrests are inline ``seat`` visuals (Rule 1, no joint).
      - flip_up: 2 ``armrest_{i}`` parts, REVOLUTE -Y, flip upward (mirrored).
      - height_adjust: 2 ``armrest_{i}`` parts, PRISMATIC +Z, post-in-sleeve.
  * ``caster_count`` (N in [3,6]): multiplicity axis on the caster base only;
    N caster wheels (each a moving CONTINUOUS part). Encoded into the
    slot_choice tuple as ``("caster_count", f"c{N}")`` (only on the caster
    base; ``c0`` sentinel otherwise so the topology dimension is explicit).

All caster axle / piston-in-tube / swivel boss / hinge pin / post-in-sleeve /
footrest rail / sled riser couplings are captured / nested geometry, so those
joints omit ``MatingContract`` (grandfathered) and are guarded by the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests allow_overlap block).

Compatibility gating (resolve_config, spec §9):
  * caster_count is meaningful only on five_star_caster (legs / sled have no
    star) -> encoded as ``c0`` otherwise.
  * rocker_glider supplies its own low rocker spine -> it is gated to the
    caster / sled bases (which expose a swivel) only; on four_wood_legs the
    rocker would have no swivel column to mount under, so wood legs degrade
    rocker_glider -> swivel_tilt.
  * egg_pod is an integral lathe-style shell -> its backrest is split out as a
    real upper-shell child so recline still works, but its sealed sides have no
    armrest anchor -> egg_pod forces armrest = fixed_arms.
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
    CapsuleGeometry,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    LoftGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

ChairForm = Literal["winged_lounge", "egg_pod", "office_mesh", "racing_bucket"]
BaseSupport = Literal["five_star_caster", "four_wood_legs", "cantilever_sled"]
ReclineMechanism = Literal["swivel_tilt", "rocker_glider", "full_recliner_footrest"]
Armrest = Literal["fixed_arms", "flip_up", "height_adjust"]
PaletteStyle = Literal[
    "tan_leather_grey_fabric",
    "blue_mesh_teal",
    "matte_black_office",
    "racing_black_orange",
    "cream_boucle",
    "sage_velvet_walnut",
]

CHAIR_FORMS: tuple[ChairForm, ...] = (
    "winged_lounge",
    "egg_pod",
    "office_mesh",
    "racing_bucket",
)
BASE_SUPPORTS: tuple[BaseSupport, ...] = (
    "five_star_caster",
    "four_wood_legs",
    "cantilever_sled",
)
RECLINE_MECHANISMS: tuple[ReclineMechanism, ...] = (
    "swivel_tilt",
    "rocker_glider",
    "full_recliner_footrest",
)
ARMRESTS: tuple[Armrest, ...] = ("fixed_arms", "flip_up", "height_adjust")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "tan_leather_grey_fabric",
    "blue_mesh_teal",
    "matte_black_office",
    "racing_black_orange",
    "cream_boucle",
    "sage_velvet_walnut",
)

DEFAULT_ARMCHAIR_PALETTE: PaletteStyle = "tan_leather_grey_fabric"

N_MIN = 3
N_MAX = 6
# Caster-count sampling weights (spec §8: 5 high-frequency, 4/6 common, 3 tail).
CASTER_COUNT_WEIGHTS = (0.15, 0.30, 0.40, 0.15)  # for (3, 4, 5, 6)

# Bases that expose a swivel column under the seat (rocker_glider needs one).
SWIVEL_BASES: tuple[BaseSupport, ...] = ("five_star_caster", "cantilever_sled")


# ---------------------------------------------------------------------------
# Palette colorways (Accessories_Cushion.md idiom). Every .visual(material=...) draws from
# one of these keys; palette never enters the slot_choice tuple.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "tan_leather_grey_fabric": {
        "shell": (0.55, 0.40, 0.28, 1.0),
        "cushion": (0.52, 0.52, 0.55, 1.0),
        "frame": (0.20, 0.20, 0.22, 1.0),
        "metal": (0.72, 0.73, 0.75, 1.0),
        "accent": (0.40, 0.28, 0.18, 1.0),
        "wood": (0.46, 0.31, 0.18, 1.0),
        "rubber": (0.07, 0.07, 0.08, 1.0),
    },
    "blue_mesh_teal": {
        "shell": (0.13, 0.28, 0.44, 1.0),
        "cushion": (0.16, 0.34, 0.56, 1.0),
        "frame": (0.07, 0.30, 0.34, 1.0),
        "metal": (0.70, 0.72, 0.74, 1.0),
        "accent": (0.14, 0.46, 0.52, 1.0),
        "wood": (0.24, 0.18, 0.12, 1.0),
        "rubber": (0.05, 0.06, 0.07, 1.0),
    },
    "matte_black_office": {
        "shell": (0.10, 0.10, 0.11, 1.0),
        "cushion": (0.085, 0.085, 0.09, 1.0),
        "frame": (0.05, 0.05, 0.055, 1.0),
        "metal": (0.72, 0.73, 0.75, 1.0),
        "accent": (0.28, 0.29, 0.31, 1.0),
        "wood": (0.30, 0.22, 0.14, 1.0),
        "rubber": (0.06, 0.06, 0.065, 1.0),
    },
    "racing_black_orange": {
        "shell": (0.08, 0.08, 0.09, 1.0),
        "cushion": (0.12, 0.12, 0.13, 1.0),
        "frame": (0.05, 0.05, 0.055, 1.0),
        "metal": (0.74, 0.75, 0.77, 1.0),
        "accent": (0.92, 0.45, 0.10, 1.0),
        "wood": (0.30, 0.22, 0.14, 1.0),
        "rubber": (0.05, 0.05, 0.055, 1.0),
    },
    "cream_boucle": {
        "shell": (0.90, 0.86, 0.78, 1.0),
        "cushion": (0.93, 0.90, 0.83, 1.0),
        "frame": (0.34, 0.30, 0.26, 1.0),
        "metal": (0.78, 0.76, 0.72, 1.0),
        "accent": (0.72, 0.64, 0.52, 1.0),
        "wood": (0.58, 0.42, 0.26, 1.0),
        "rubber": (0.20, 0.18, 0.16, 1.0),
    },
    "sage_velvet_walnut": {
        "shell": (0.46, 0.52, 0.42, 1.0),
        "cushion": (0.40, 0.47, 0.38, 1.0),
        "frame": (0.30, 0.24, 0.18, 1.0),
        "metal": (0.66, 0.64, 0.60, 1.0),
        "accent": (0.34, 0.40, 0.32, 1.0),
        "wood": (0.40, 0.27, 0.16, 1.0),
        "rubber": (0.16, 0.15, 0.14, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Seat-frame numbers shared across all
# chair_forms (the seat pan / cushion / mech are identical across the source
# variants); chair_form only swaps the shell + cushion + backrest mesh.
# ---------------------------------------------------------------------------
# Caster base (P_office cb37c340).
_CASTER_RADIUS_POS = 0.295
_WHEEL_RADIUS = 0.030
_WHEEL_HALF_W = 0.026  # half the twin-wheel + hubcap span (self-collision)
_SPOKE_TIP_R = 0.30
_LIFT_TUBE_TOP = 0.360
_LIFT_TRAVEL = 0.12
_PISTON_TOP = 0.062
_SEAT_FRAME_Z_CASTER = _LIFT_TUBE_TOP + _PISTON_TOP  # 0.422

# Sled base (549d8992).
_SLED_MOUNT_Z = 0.40
_SLED_RUNNER_Y = 0.22
_TUBE_R = 0.015

# Wood legs (78b0bb00).
_WOOD_SEAT_Z = 0.42  # seat-frame height above floor (legs reach to floor)
_LEG_SPLAY = 0.30  # leg foot half-spread

# Recline (shared).
_RECLINE_PIVOT = (-0.21, 0.0, -0.02)
_RECLINE_RANGE = 0.30
_RECLINE_FULL = 1.2  # full-recliner travel

# Armrest (flip_up 68a45f62 / height_adjust 75232ed3).
_ARMREST_HINGE_X = -0.15
_ARMREST_HINGE_Y = 0.22
_ARMREST_HINGE_Z = 0.13
_ARMREST_FLIP_UPPER = 1.4
_ARMREST_TRAVEL = 0.05
_ARMREST_JOINT_Z = 0.120
_ARMREST_SLEEVE_Y = 0.248

# Footrest (ad4e3477).
_FOOTREST_TRAVEL = 0.26

# Rocker (84c9e022).
_ROCK_LIMIT = 0.22
_ROCK_JOINT_Z = 0.10

_OFFICE_MESH_H_COUNT = 9
_OFFICE_MESH_V_COUNT = 7


@dataclass(frozen=True)
class ArmchairConfig:
    chair_form: ChairForm | None = None
    base_support: BaseSupport | None = None
    recline_mechanism: ReclineMechanism | None = None
    armrest: Armrest | None = None
    caster_count: int | None = None
    palette_style: PaletteStyle = DEFAULT_ARMCHAIR_PALETTE
    seat_height_scale: float = 1.0
    seat_width_scale: float = 1.0
    back_height_scale: float = 1.0
    recline_range_scale: float = 1.0
    caster_radius_scale: float = 1.0
    name: str = "armchair"


@dataclass(frozen=True)
class ResolvedArmchairConfig:
    chair_form: ChairForm
    base_support: BaseSupport
    recline_mechanism: ReclineMechanism
    armrest: Armrest
    caster_count: int  # 0 when not a caster base
    palette_style: PaletteStyle
    # Derived geometry.
    seat_frame_z: float  # seat origin height above floor (q=0)
    seat_z0: float  # z added to seat-local geometry (0 when seat is lifted by a joint;
    #                 == seat_frame_z for wood legs where seat itself is the root)
    seat_half_w: float  # seat half-width (Y), scaled
    back_scale: float  # backrest height scale
    recline_lower: float  # recline joint lower limit (negative)
    caster_radius_pos: float
    wheel_radius: float
    lift_tube_top: float
    lift_travel: float
    piston_top: float
    name: str

    @property
    def has_swivel(self) -> bool:
        return self.base_support in SWIVEL_BASES

    @property
    def is_caster(self) -> bool:
        return self.base_support == "five_star_caster"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ArmchairConfig:
    rng = random.Random(seed)
    return ArmchairConfig(
        chair_form=rng.choice(CHAIR_FORMS),
        base_support=rng.choice(BASE_SUPPORTS),
        recline_mechanism=rng.choice(RECLINE_MECHANISMS),
        armrest=rng.choice(ARMRESTS),
        caster_count=rng.choices((3, 4, 5, 6), weights=CASTER_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        seat_height_scale=round(rng.uniform(0.85, 1.12), 4),
        seat_width_scale=round(rng.uniform(0.85, 1.20), 4),
        back_height_scale=round(rng.uniform(0.80, 1.15), 4),
        recline_range_scale=round(rng.uniform(0.85, 1.10), 4),
        caster_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_armchair_{seed}",
    )


def resolve_config(config: ArmchairConfig | None = None) -> ResolvedArmchairConfig:
    cfg = config or ArmchairConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    chair_form = _pick(cfg.chair_form, CHAIR_FORMS)
    base_support = _pick(cfg.base_support, BASE_SUPPORTS)
    recline_mechanism = _pick(cfg.recline_mechanism, RECLINE_MECHANISMS)
    armrest = _pick(cfg.armrest, ARMRESTS)

    # --- Compatibility gating (spec §9). ---
    # (1) rocker_glider needs the compact gas-lift pedestal. On sled/wood bases
    #     it reads as an odd extra board under the chair, so degrade it there.
    if recline_mechanism == "rocker_glider" and base_support != "five_star_caster":
        recline_mechanism = "swivel_tilt"
    # (1b) the source full recliner is still a pedestal recliner. On wood/sled
    #      visitors it produces an implausible under-seat rail pack, so keep
    #      those bases on the simpler tilt path.
    if recline_mechanism == "full_recliner_footrest" and base_support != "five_star_caster":
        recline_mechanism = "swivel_tilt"
    # (2) office/gaming forms should stay on task-chair mechanisms; wood legs
    #     are reserved for lounge upholstery so random seeds do not produce the
    #     "gaming bucket on dining legs" mismatch.
    if base_support == "four_wood_legs" and chair_form in ("office_mesh", "racing_bucket"):
        chair_form = "winged_lounge"
    # (3) egg_pod is a pedestal/pod family, not a cantilever visitor-chair.
    if chair_form == "egg_pod" and base_support != "five_star_caster":
        base_support = "five_star_caster"
    # (4) egg_pod's sealed sides have no armrest anchor -> fixed_arms only.
    if chair_form == "egg_pod":
        armrest = "fixed_arms"
    # office_mesh defaults to the absorbed blue-mesh office expression unless a
    # non-default palette was chosen explicitly.
    if chair_form == "office_mesh" and cfg.palette_style == DEFAULT_ARMCHAIR_PALETTE:
        palette_style = "blue_mesh_teal"

    # Scales.
    height_scale = _clamp(cfg.seat_height_scale, 0.85, 1.12)
    width_scale = _clamp(cfg.seat_width_scale, 0.85, 1.20)
    back_scale = _clamp(cfg.back_height_scale, 0.80, 1.15)
    recline_scale = _clamp(cfg.recline_range_scale, 0.85, 1.10)
    caster_radius_scale = _clamp(cfg.caster_radius_scale, 0.90, 1.10)

    # Caster count: only meaningful on the caster base.
    if base_support == "five_star_caster":
        caster_count = int(cfg.caster_count) if cfg.caster_count is not None else 5
        caster_count = int(_clamp(caster_count, N_MIN, N_MAX))
    else:
        caster_count = 0

    # Seat-frame height per base.
    if base_support == "five_star_caster":
        base_seat_z = _SEAT_FRAME_Z_CASTER
    elif base_support == "cantilever_sled":
        base_seat_z = _SLED_MOUNT_Z
    else:  # four_wood_legs
        base_seat_z = _WOOD_SEAT_Z
    seat_frame_z = base_seat_z * height_scale
    # Wood legs make the seat the root, so seat geometry must be lifted to
    # seat_frame_z (no joint provides the lift). Other bases lift via a joint.
    seat_z0 = seat_frame_z if base_support == "four_wood_legs" else 0.0

    seat_half_w = 0.23 * width_scale

    # Recline travel: full_recliner_footrest reclines deep; others moderate.
    if recline_mechanism == "full_recliner_footrest":
        recline_lower = -_clamp(_RECLINE_FULL * recline_scale, 1.0, 1.25)
    else:
        recline_lower = -_clamp(_RECLINE_RANGE * recline_scale, 0.20, 0.35)

    # Caster geometry derived from scale; guard self-collision at large N.
    caster_radius_pos = _CASTER_RADIUS_POS * caster_radius_scale
    wheel_radius = _WHEEL_RADIUS
    if caster_count >= 3:
        # Self-collision inequality (spec §7): N * (2*half_w) <= circumference - margin.
        margin = 0.02
        for _ in range(40):
            avail = 2.0 * math.pi * caster_radius_pos - margin
            need = caster_count * (2.0 * _WHEEL_HALF_W)
            if need <= avail:
                break
            caster_radius_pos += 0.01  # widen the star to fit the wheels

    # Lift geometry scales with seat height (keeps retained piston insertion).
    lift_tube_top = _LIFT_TUBE_TOP * height_scale
    lift_travel = _LIFT_TRAVEL
    piston_top = _PISTON_TOP

    return ResolvedArmchairConfig(
        chair_form=chair_form,
        base_support=base_support,
        recline_mechanism=recline_mechanism,
        armrest=armrest,
        caster_count=caster_count,
        palette_style=palette_style,
        seat_frame_z=seat_frame_z,
        seat_z0=seat_z0,
        seat_half_w=seat_half_w,
        back_scale=back_scale,
        recline_lower=recline_lower,
        caster_radius_pos=caster_radius_pos,
        wheel_radius=wheel_radius,
        lift_tube_top=lift_tube_top,
        lift_travel=lift_travel,
        piston_top=piston_top,
        name=cfg.name or "armchair",
    )


def with_overrides(config: ArmchairConfig, **kwargs: object) -> ArmchairConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ArmchairConfig | ResolvedArmchairConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedArmchairConfig) else resolve_config(config)
    return (
        ("chair_form", r.chair_form),
        ("base_support", r.base_support),
        ("recline_mechanism", r.recline_mechanism),
        ("armrest", r.armrest),
        ("caster_count", f"c{r.caster_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Seat mesh helpers (chair_form). Each preserves its source primitive family:
# winged = cadquery-ish bucket (rounded box), egg_pod = open upholstered shell,
# office = extruded rounded-rect pan, racing = rounded pan + bolsters.
# All emit visuals onto the (already-created) seat part, centered on the seat
# frame origin (pan top near z=0.09). Returns nothing.
# ---------------------------------------------------------------------------
def _emit_seat_pan(seat, r: ResolvedArmchairConfig, mats):
    """Shared seat pan + cushion (office/winged/racing). Source: P_office L197-210."""
    w = 2.0 * r.seat_half_w
    z0 = r.seat_z0
    pan_geom = ExtrudeGeometry(rounded_rect_profile(0.50, w * 1.0, 0.10), 0.07, center=True)
    pan_geom.translate(0.01, 0.0, z0 + 0.043)
    seat.visual(mesh_from_geometry(pan_geom, "seat_pan"), material=mats["shell"], name="seat_pan", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "racing_black_orange"} else "fabric.upholstery_plain"))
    cush_geom = ExtrudeGeometry(rounded_rect_profile(0.44, w * 0.91, 0.09), 0.03, center=True)
    cush_geom.translate(0.02, 0.0, z0 + 0.088)
    seat.visual(
        mesh_from_geometry(cush_geom, "seat_cushion"),
        material=mats["cushion"],
        name="seat_cushion", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
    )


def _profile_section(width: float, depth: float, radius: float, z: float) -> list[tuple[float, float, float]]:
    return [(x, y, z) for x, y in rounded_rect_profile(width, depth, radius, corner_segments=10)]


def _office_seat_cushion_mesh(r: ResolvedArmchairConfig):
    w = 2.0 * r.seat_half_w
    sections = [
        _profile_section(0.34, w * 0.72, 0.060, 0.0),
        _profile_section(0.42, w * 0.88, 0.082, 0.016),
        _profile_section(0.47, w * 0.95, 0.100, 0.042),
        _profile_section(0.49, w * 0.97, 0.102, 0.066),
        _profile_section(0.45, w * 0.90, 0.082, 0.082),
    ]
    return mesh_from_geometry(LoftGeometry(sections, cap=True, closed=True), "office_seat_cushion")


def _office_seat_piping_mesh(r: ResolvedArmchairConfig):
    w = 2.0 * r.seat_half_w
    pts = [(x, y, 0.058) for x, y in rounded_rect_profile(0.485, w * 0.97, 0.098, corner_segments=12)]
    return mesh_from_geometry(
        tube_from_spline_points(
            pts,
            radius=0.0048,
            closed_spline=True,
            samples_per_segment=6,
            radial_segments=10,
            cap_ends=False,
        ),
        "office_seat_piping",
    )


def _office_back_x(z: float, bs: float) -> float:
    samples = (
        (0.14, 0.010),
        (0.24, -0.006),
        (0.38, -0.032),
        (0.54, -0.070),
        (0.72, -0.108),
    )
    z = max(samples[0][0], min(samples[-1][0] * bs, z))
    scaled = [(zz * bs, xx) for zz, xx in samples]
    for (z0, x0), (z1, x1) in zip(scaled, scaled[1:]):
        if z <= z1:
            t = 0.0 if z1 == z0 else (z - z0) / (z1 - z0)
            return x0 + (x1 - x0) * t
    return scaled[-1][1]


def _office_back_half_w(z: float, bs: float, seat_half_w: float) -> float:
    width = seat_half_w * 1.02
    top = seat_half_w * 0.68
    bottom = seat_half_w * 0.72
    mid0 = 0.28 * bs
    mid1 = 0.52 * bs
    top_z = 0.72 * bs
    if z <= mid0:
        t = z / max(mid0, 1e-6)
        return bottom + (width - bottom) * t
    if z <= mid1:
        return width
    t = (z - mid1) / max(top_z - mid1, 1e-6)
    return width + (top - width) * t


def _office_mesh_point(r: ResolvedArmchairConfig, bs: float, u: float, z: float, x_bias: float = 0.0) -> tuple[float, float, float]:
    return (
        _office_back_x(z, bs) + x_bias,
        u * _office_back_half_w(z, bs, r.seat_half_w),
        z,
    )


def _office_back_frame_mesh(r: ResolvedArmchairConfig, bs: float):
    pts = [
        _office_mesh_point(r, bs, 0.76, 0.14 * bs, 0.0),
        _office_mesh_point(r, bs, 0.96, 0.23 * bs, 0.0),
        _office_mesh_point(r, bs, 1.00, 0.39 * bs, 0.0),
        _office_mesh_point(r, bs, 0.90, 0.60 * bs, 0.0),
        _office_mesh_point(r, bs, 0.54, 0.72 * bs, 0.0),
        _office_mesh_point(r, bs, 0.0, 0.75 * bs, 0.0),
        _office_mesh_point(r, bs, -0.54, 0.72 * bs, 0.0),
        _office_mesh_point(r, bs, -0.90, 0.60 * bs, 0.0),
        _office_mesh_point(r, bs, -1.00, 0.39 * bs, 0.0),
        _office_mesh_point(r, bs, -0.96, 0.23 * bs, 0.0),
        _office_mesh_point(r, bs, -0.76, 0.14 * bs, 0.0),
        _office_mesh_point(r, bs, 0.0, 0.12 * bs, 0.0),
    ]
    return mesh_from_geometry(
        tube_from_spline_points(
            pts,
            radius=0.0165,
            closed_spline=True,
            samples_per_segment=10,
            radial_segments=12,
            cap_ends=False,
        ),
        "office_back_frame",
    )


def _office_back_line(points: list[tuple[float, float, float]], radius: float, name: str):
    return mesh_from_geometry(
        tube_from_spline_points(
            points,
            radius=radius,
            samples_per_segment=8,
            radial_segments=9,
            cap_ends=True,
        ),
        name,
    )


def _emit_seat_form(seat, r: ResolvedArmchairConfig, mats):
    """Emit the chair_form-specific seat shell + cushion on the seat part.

    The mech housing (swivel/recline mount hardware) is added separately by the
    base/recline builders so they share the captured-overlap geometry.
    """
    form = r.chair_form
    w = 2.0 * r.seat_half_w
    z0 = r.seat_z0
    if form == "egg_pod":
        # Egg/pod: use an open upholstered basin, not a full lathe barrel. The
        # old revolved shell looked like a bulky closed bucket; these low side
        # bolsters leave a clear seat opening and read as an armchair.
        basin = ExtrudeGeometry(rounded_rect_profile(0.48, w * 0.96, 0.14), 0.075, center=True)
        basin.translate(0.00, 0.0, z0 + 0.040)
        seat.visual(mesh_from_geometry(basin, "pod_shell"), material=mats["shell"], name="pod_shell", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "racing_black_orange"} else "fabric.upholstery_plain"))
        rear = ExtrudeGeometry(rounded_rect_profile(0.12, w * 0.96, 0.045), 0.12, center=True)
        rear.translate(-0.225, 0.0, z0 + 0.110)
        seat.visual(mesh_from_geometry(rear, "pod_rear_lip"), material=mats["shell"], name="pod_rear_lip", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "racing_black_orange"} else "fabric.upholstery_plain"))
        for label, sign in (("left", 1.0), ("right", -1.0)):
            side = ExtrudeGeometry(rounded_rect_profile(0.38, 0.055, 0.024), 0.075, center=True)
            side.translate(-0.015, sign * (r.seat_half_w + 0.010), z0 + 0.110)
            seat.visual(
                mesh_from_geometry(side, f"pod_side_bolster_{label}"),
                material=mats["shell"],
                name=f"pod_side_bolster_{label}", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "racing_black_orange"} else "fabric.upholstery_plain"),
            )
        cush = ExtrudeGeometry(rounded_rect_profile(0.40, w * 0.78, 0.12), 0.035, center=True)
        cush.translate(0.025, 0.0, z0 + 0.098)
        seat.visual(
            mesh_from_geometry(cush, "pod_cushion"),
            material=mats["cushion"],
            name="seat_cushion", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
        )
        return
    if form == "winged_lounge":
        # Leather bucket: a rounded box shell with a recessed cushion. Source:
        # P_winged _seat_bucket.
        bucket = ExtrudeGeometry(rounded_rect_profile(0.52, w * 1.05, 0.16), 0.13, center=True)
        bucket.translate(-0.02, 0.0, z0 + 0.02)
        seat.visual(
            mesh_from_geometry(bucket, "seat_bucket"),
            material=mats["shell"],
            name="seat_bucket", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "racing_black_orange"} else "fabric.upholstery_plain"),
        )
        _emit_seat_pan(seat, r, mats)
        return
    if form == "racing_bucket":
        _emit_seat_pan(seat, r, mats)
        # Side bolsters along the seat edges (racing wrap).
        for label, sign in (("left", 1.0), ("right", -1.0)):
            bol = ExtrudeGeometry(rounded_rect_profile(0.42, 0.07, 0.03), 0.06, center=True)
            bol.translate(0.0, sign * (r.seat_half_w - 0.01), z0 + 0.085)
            seat.visual(
                mesh_from_geometry(bol, f"seat_bolster_{label}"),
                material=mats["accent"],
                name=f"seat_bolster_{label}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
            )
        return
    # office_mesh (default): sculpted cushion + piping, closer to the absorbed
    # blue-mesh task-chair asset than the earlier flat rounded slab.
    shell = ExtrudeGeometry(rounded_rect_profile(0.50, w * 0.99, 0.10, corner_segments=10), 0.062, center=True)
    shell.translate(0.01, 0.0, z0 + 0.035)
    seat.visual(mesh_from_geometry(shell, "seat_pan"), material=mats["shell"], name="seat_pan", material_class_id="plastic.opaque_generic")
    seat.visual(
        _office_seat_cushion_mesh(r),
        origin=Origin(xyz=(0.018, 0.0, z0 + 0.055)),
        material=mats["cushion"],
        name="seat_cushion", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
    )
    seat.visual(
        _office_seat_piping_mesh(r),
        origin=Origin(xyz=(0.018, 0.0, z0 + 0.055)),
        material=mats["metal"],
        name="seat_piping", material_class_id="metal.chrome_polished",
    )


def _emit_seat_mech(seat, r: ResolvedArmchairConfig, mats):
    """The mechanism housing under the seat (swivel / recline mount). Shared by
    all forms; source: P_office L182-195."""
    z0 = r.seat_z0
    if r.base_support == "four_wood_legs":
        seat.visual(
            Box((0.14, min(0.15, 2.0 * r.seat_half_w * 0.55), 0.035)),
            origin=Origin(xyz=(-0.165, 0.0, z0 + 0.005)),
            material=mats["frame"],
            name="mech_rear_bracket", material_class_id="metal.paint_coated",
        )
        return
    if r.base_support == "cantilever_sled":
        housing_y = min(0.13, 2.0 * r.seat_half_w * 0.70)
        seat.visual(
            Box((0.18, housing_y, 0.028)),
            origin=Origin(xyz=(0.005, 0.0, z0 - 0.004)),
            material=mats["frame"],
            name="mech_housing", material_class_id="metal.paint_coated",
        )
        seat.visual(
            Box((0.120, 0.11, 0.040)),
            origin=Origin(xyz=(-0.165, 0.0, z0 + 0.004)),
            material=mats["frame"],
            name="mech_rear_bracket", material_class_id="metal.paint_coated",
        )
        return
    housing_z = 0.075
    housing_y = min(0.20, 2.0 * r.seat_half_w * 0.82)
    seat.visual(
        Box((0.22, housing_y, housing_z)),
        origin=Origin(xyz=(0.01, 0.0, z0 - 0.020)),
        material=mats["frame"],
        name="mech_housing", material_class_id="metal.paint_coated",
    )
    seat.visual(
        Box((0.120, 0.12, 0.050)),
        origin=Origin(xyz=(-0.165, 0.0, z0 + 0.000)),
        material=mats["frame"],
        name="mech_rear_bracket", material_class_id="metal.paint_coated",
    )


# ---------------------------------------------------------------------------
# Backrest mesh helpers (chair_form). Backrest is always a real part so recline
# always has a moving child (egg_pod's backrest = split upper shell).
# Built in the backrest's pivot frame: pivot barrel at local origin.
# ---------------------------------------------------------------------------
def _emit_backrest_form(backrest, r: ResolvedArmchairConfig, mats):
    bs = r.back_scale
    # Pivot barrel + arms (shared hinge hardware, in the backrest pivot frame).
    backrest.visual(
        Cylinder(radius=0.022, length=0.140),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["frame"],
        name="pivot_barrel", material_class_id="metal.paint_coated",
    )
    for label, sign in (("left", 1.0), ("right", -1.0)):
        backrest.visual(
            Box((0.090, 0.030, 0.040)),
            origin=Origin(xyz=(-0.045, sign * 0.045, 0.0)),
            material=mats["frame"],
            name=f"{label}_pivot_arm", material_class_id="metal.paint_coated",
        )
    w = 2.0 * r.seat_half_w
    form = r.chair_form
    if form == "egg_pod":
        # Split pod back: a broad, shallow shell with a waist and head bulge,
        # rather than a revolved blob.
        shell = ExtrudeGeometry(rounded_rect_profile(0.075, w * 0.88, 0.032), 0.42 * bs, center=True)
        shell.rotate_y(-0.18)
        shell.translate(-0.065, 0.0, 0.29 * bs)
        backrest.visual(
            mesh_from_geometry(shell, "pod_back_shell"),
            material=mats["shell"],
            name="back_shell", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "racing_black_orange"} else "fabric.upholstery_plain"),
        )
        cushion = ExtrudeGeometry(rounded_rect_profile(0.045, w * 0.72, 0.018), 0.32 * bs, center=True)
        cushion.rotate_y(-0.18)
        cushion.translate(-0.035, 0.0, 0.30 * bs)
        backrest.visual(
            mesh_from_geometry(cushion, "pod_back_cushion"),
            material=mats["cushion"],
            name="back_cushion", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
        )
        backrest.visual(
            Box((0.045, w * 0.42, 0.17)),
            origin=Origin(xyz=(-0.05, 0.0, 0.06)),
            material=mats["frame"],
            name="spine", material_class_id="metal.paint_coated",
        )
        return
    if form == "winged_lounge":
        # Spine column (connects pivot region to upper backrest).
        backrest.visual(
            Box((0.050, 0.100, 0.180 * bs + 0.06)),
            origin=Origin(xyz=(-0.060, 0.0, (0.070 * bs) + 0.03)),
            material=mats["frame"],
            name="spine", material_class_id="metal.paint_coated",
        )
        # Layered contour panels: lower lumbar comes forward, shoulder rolls
        # back, and the cushion follows the same outline instead of a flat slab.
        for i, (z, h, x, yy) in enumerate(
            ((0.15, 0.15, -0.035, 0.88), (0.29, 0.18, -0.060, 0.96), (0.45, 0.16, -0.095, 0.82))
        ):
            backrest.visual(
                Box((0.055, w * yy, h * bs)),
                origin=Origin(xyz=(x, 0.0, z * bs)),
                material=mats["shell"],
                name=f"back_panel_{i}", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "racing_black_orange"} else "fabric.upholstery_plain"),
            )
            backrest.visual(
                Box((0.036, w * (yy - 0.10), h * bs * 0.82)),
                origin=Origin(xyz=(x + 0.030, 0.0, z * bs)),
                material=mats["cushion"],
                name=f"back_cushion_{i}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
            )
        for label, sign in (("left", 1.0), ("right", -1.0)):
            backrest.visual(
                Box((0.070, 0.040, 0.34 * bs)),
                origin=Origin(xyz=(-0.075, sign * (r.seat_half_w + 0.000), 0.34 * bs)),
                material=mats["shell"],
                name=f"wing_{label}", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "racing_black_orange"} else "fabric.upholstery_plain"),
            )
        return
    if form == "racing_bucket":
        backrest.visual(
            Box((0.050, 0.100, 0.180 * bs + 0.06)),
            origin=Origin(xyz=(-0.060, 0.0, (0.070 * bs) + 0.03)),
            material=mats["frame"],
            name="spine", material_class_id="metal.paint_coated",
        )
        for i, (z, h, x, yy) in enumerate(
            ((0.14, 0.16, -0.035, 0.72), (0.31, 0.20, -0.070, 0.88), (0.50, 0.18, -0.105, 0.68))
        ):
            backrest.visual(
                Box((0.050, w * yy, h * bs)),
                origin=Origin(xyz=(x, 0.0, z * bs)),
                material=mats["shell"],
                name=f"back_panel_{i}", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "racing_black_orange"} else "fabric.upholstery_plain"),
            )
            backrest.visual(
                Box((0.034, w * (yy - 0.14), h * bs * 0.78)),
                origin=Origin(xyz=(x + 0.030, 0.0, z * bs)),
                material=mats["cushion"],
                name=f"back_cushion_{i}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
            )
        for label, sign in (("left", 1.0), ("right", -1.0)):
            backrest.visual(
                Box((0.060, 0.05, 0.48 * bs)),
                origin=Origin(xyz=(-0.080, sign * (r.seat_half_w - 0.018), 0.36 * bs)),
                material=mats["accent"],
                name=f"shoulder_wing_{label}", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
            )
        # Headrest pillow.
        head = CapsuleGeometry(radius=0.06, length=0.16, radial_segments=16)
        head.rotate_x(math.pi / 2.0)
        head.translate(-0.05, 0.0, 0.56 * bs)
        backrest.visual(
            mesh_from_geometry(head, "headrest"),
            material=mats["cushion"],
            name="headrest", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
        )
        return
    # office_mesh (default): rounded perimeter + real grid. The back stays open:
    # no center spine, bridge strip, or floating lumbar plate.
    backrest.visual(
        Box((0.050, w * 0.95, 0.050)),
        origin=Origin(xyz=(-0.020, 0.0, 0.135)),
        material=mats["frame"],
        name="bottom_rail", material_class_id="metal.paint_coated",
    )
    backrest.visual(
        _office_back_frame_mesh(r, bs),
        material=mats["frame"],
        name="backrest_frame", material_class_id="metal.paint_coated",
    )
    for label, sign in (("left", 1.0), ("right", -1.0)):
        backrest.visual(
            _office_back_line(
                [
                    (-0.012, sign * 0.058, 0.020),
                    _office_mesh_point(r, bs, sign * 0.55, 0.15 * bs, -0.004),
                    _office_mesh_point(r, bs, sign * 0.80, 0.22 * bs, -0.004),
                ],
                0.009,
                f"frame_strut_{label}",
            ),
            material=mats["frame"],
            name=f"frame_strut_{label}", material_class_id="metal.paint_coated",
        )
    for i in range(_OFFICE_MESH_H_COUNT):
        t = i / max(1, _OFFICE_MESH_H_COUNT - 1)
        z = (0.18 + 0.48 * t) * bs
        x_bias = 0.002 + 0.004 * t
        pts = [_office_mesh_point(r, bs, -0.86 + 1.72 * (j / 14.0), z, x_bias) for j in range(15)]
        backrest.visual(
            _office_back_line(pts, 0.0016, f"mesh_h_{i}"),
            material=mats["accent"],
            name=f"mesh_h_{i}", material_class_id="fabric.open_mesh",
        )
    for i in range(_OFFICE_MESH_V_COUNT):
        u = -0.78 + 1.56 * (i / max(1, _OFFICE_MESH_V_COUNT - 1))
        pts = []
        for j in range(13):
            t = j / 12.0
            z = (0.18 + 0.48 * t) * bs
            x_bias = (0.002 + 0.004 * t) + 0.007 * math.sin(math.pi * t) * (1.0 - abs(u))
            pts.append(_office_mesh_point(r, bs, u, z, x_bias))
        backrest.visual(
            _office_back_line(pts, 0.0014, f"mesh_v_{i}"),
            material=mats["accent"],
            name=f"mesh_v_{i}", material_class_id="fabric.open_mesh",
        )
    for tag, z, x_bias, u_span in (
        ("bottom", 0.20 * bs, 0.001, 0.78),
        ("top", 0.66 * bs, 0.006, 0.86),
    ):
        edge_pts = [_office_mesh_point(r, bs, -u_span + (2.0 * u_span) * (j / 14.0), z, x_bias) for j in range(15)]
        backrest.visual(
            _office_back_line(edge_pts, 0.0042, f"mesh_{tag}_tension_edge"),
            material=mats["accent"],
            name=f"mesh_{tag}_tension_edge", material_class_id="fabric.open_mesh",
        )
    for side, u in (("left", 0.86), ("right", -0.86)):
        edge_pts = [
            _office_mesh_point(r, bs, u, (0.20 + 0.46 * (j / 12.0)) * bs, 0.002 + 0.004 * (j / 12.0))
            for j in range(13)
        ]
        backrest.visual(
            _office_back_line(edge_pts, 0.0045, f"mesh_{side}_tension_edge"),
            material=mats["accent"],
            name=f"mesh_{side}_tension_edge", material_class_id="fabric.open_mesh",
        )
    head = ExtrudeGeometry(rounded_rect_profile(0.11, w * 0.38, 0.038, corner_segments=10), 0.035, center=True)
    head.translate(_office_back_x(0.73 * bs, bs) + 0.010, 0.0, 0.73 * bs)
    backrest.visual(
        mesh_from_geometry(head, "headrest"),
        material=mats["cushion"],
        name="headrest", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
    )


# ---------------------------------------------------------------------------
# Inline armrest visuals (fixed_arms, Rule 1: no joint).
# ---------------------------------------------------------------------------
def _emit_fixed_armrests(seat, r: ResolvedArmchairConfig, mats):
    """Closed-loop armrests as seat inline visuals. Source: P_office L214-239."""
    if r.chair_form == "egg_pod":
        # Pod walls are the armrests; emit a low inner shelf only (no loops).
        return
    z0 = r.seat_z0
    for label, sign in (("left", 1.0), ("right", -1.0)):
        y = sign * (r.seat_half_w + 0.018)
        stem_geom = tube_from_spline_points(
            [(0.11, y, z0 + 0.020), (0.04, y, z0 + 0.105), (-0.11, y, z0 + 0.120)],
            radius=0.012,
            samples_per_segment=12,
            radial_segments=12,
            cap_ends=True,
        )
        seat.visual(mesh_from_geometry(stem_geom, f"armrest_stem_{label}"), material=mats["frame"], name=f"armrest_stem_{label}", material_class_id="metal.paint_coated")
        seat.visual(
            Box((0.060, 0.055, 0.040)),
            origin=Origin(xyz=(0.090, sign * r.seat_half_w, z0 + 0.030)),
            material=mats["frame"],
            name=f"armrest_root_{label}", material_class_id="metal.paint_coated",
        )
        seat.visual(
            Box((0.25, 0.045, 0.030)),
            origin=Origin(xyz=(0.005, y, z0 + 0.145)),
            material=mats["frame"],
            name=f"armrest_pad_fixed_{label}", material_class_id="metal.paint_coated",
        )


# ---------------------------------------------------------------------------
# Base builders. Each emits its root part + support joints, then creates the
# `seat` part (via _build_seat) and the seat-mount joint. Returns the seat part.
# ---------------------------------------------------------------------------
def _spoke_mesh(r: ResolvedArmchairConfig, angle: float, index: int):
    # Spoke tip reaches the caster stem radius so the stem/yoke always touch it
    # (caster_radius_pos may be widened by the self-collision projection).
    tip_r = r.caster_radius_pos + 0.01
    profile = [
        (0.020, -0.034),
        (tip_r, -0.019),
        (tip_r, 0.019),
        (0.020, 0.034),
    ]
    geom = ExtrudeGeometry(profile, 0.034, cap=True, center=True)
    geom.rotate_y(0.07)
    geom.translate(0.0, 0.0, 0.115)
    geom.rotate_z(angle)
    return mesh_from_geometry(geom, f"spoke_{index}")


def _build_seat(model, r: ResolvedArmchairConfig, mats) -> object:
    seat = model.part("seat")
    _emit_seat_mech(seat, r, mats)
    _emit_seat_form(seat, r, mats)
    if r.armrest == "fixed_arms":
        _emit_fixed_armrests(seat, r, mats)
    seat.inertial = Inertial.from_geometry(
        Box((0.50, 2.0 * r.seat_half_w, 0.20)),
        mass=6.0,
        origin=Origin(xyz=(0.0, 0.0, 0.04)),
    )
    return seat


def _build_caster_base(model, r: ResolvedArmchairConfig, mats):
    """five_star_caster: pedestal swivel + star base + gas lift + seat swivel."""
    pedestal_anchor = model.part("pedestal_anchor")
    pedestal_anchor.visual(
        Cylinder(radius=0.010, length=0.072),
        origin=Origin(xyz=(0.0, 0.0, 0.036)),
        material=mats["hidden"],
        name="pedestal_spindle", material_class_id="metal.paint_coated",
    )
    pedestal_anchor.visual(
        Cylinder(radius=0.008, length=0.155),
        origin=Origin(xyz=(0.0, 0.0, 0.0775)),
        material=mats["hidden"],
        name="pedestal_hidden_core", material_class_id="metal.paint_coated",
    )
    # Gas-lift outer tube + collar stay on the fixed pedestal branch so the
    # wheeled star base can rotate independently from the seat.
    tube_h = r.lift_tube_top - 0.155
    pedestal_anchor.visual(
        Cylinder(radius=0.027, length=tube_h),
        origin=Origin(xyz=(0.0, 0.0, 0.155 + tube_h / 2.0)),
        material=mats["frame"],
        name="lift_tube", material_class_id="metal.paint_coated",
    )
    pedestal_anchor.visual(
        Cylinder(radius=0.0285, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, r.lift_tube_top - 0.009)),
        material=mats["metal"],
        name="lift_collar", material_class_id="metal.chrome_polished",
    )
    pedestal_anchor.inertial = Inertial.from_geometry(
        Box((0.06, 0.06, r.lift_tube_top)),
        mass=1.0,
        origin=Origin(xyz=(0.0, 0.0, r.lift_tube_top / 2.0)),
    )
    base = model.part("base")
    base.visual(
        Cylinder(radius=0.014, length=0.090),
        origin=Origin(xyz=(0.0, 0.0, 0.045)),
        material=mats["hidden"],
        name="pedestal_socket", material_class_id="metal.paint_coated",
    )
    base.visual(
        Cylinder(radius=0.048, length=0.090),
        origin=Origin(xyz=(0.0, 0.0, 0.120)),
        material=mats["frame"],
        name="star_hub", material_class_id="metal.paint_coated",
    )
    n = r.caster_count
    angles = [2.0 * math.pi * i / n + math.pi / 5.0 for i in range(n)]
    for i, ang in enumerate(angles):
        cx = r.caster_radius_pos * math.cos(ang)
        cy = r.caster_radius_pos * math.sin(ang)
        base.visual(_spoke_mesh(r, ang, i), material=mats["frame"], name=f"spoke_{i}", material_class_id="metal.paint_coated")
        base.visual(
            Cylinder(radius=0.009, length=0.042),
            origin=Origin(xyz=(cx, cy, 0.061)),
            material=mats["frame"],
            name=f"caster_stem_{i}", material_class_id="metal.paint_coated",
        )
        base.visual(
            Box((0.032, 0.014, 0.026)),
            origin=Origin(xyz=(cx, cy, 0.042), rpy=(0.0, 0.0, ang)),
            material=mats["frame"],
            name=f"caster_yoke_{i}", material_class_id="metal.paint_coated",
        )
    base.inertial = Inertial.from_geometry(
        Box((2.0 * r.caster_radius_pos, 2.0 * r.caster_radius_pos, 0.18)),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, 0.09)),
    )
    model.articulation(
        "pedestal_anchor_to_base",
        ArticulationType.CONTINUOUS,
        parent=pedestal_anchor,
        child=base,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=3.0),
    )

    # Caster wheels (each a CONTINUOUS moving part).
    for i, ang in enumerate(angles):
        wheel = model.part(f"caster_wheel_{i}")
        for side, sy in (("0", -0.0165), ("1", 0.0165)):
            wheel.visual(
                Cylinder(radius=r.wheel_radius, length=0.013),
                origin=Origin(xyz=(0.0, sy, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["rubber"],
                name=f"wheel_{side}", material_class_id="rubber.smooth_plain",
            )
        wheel.visual(
            Cylinder(radius=0.005, length=0.046),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name="axle", material_class_id="metal.paint_coated",
        )
        for side, sy in (("0", -0.0245), ("1", 0.0245)):
            wheel.visual(
                Cylinder(radius=0.019, length=0.005),
                origin=Origin(xyz=(0.0, sy, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["metal"],
                name=f"hub_cap_{side}", material_class_id="metal.chrome_polished",
            )
        wheel.inertial = Inertial.from_geometry(
            Box((2.0 * r.wheel_radius, 0.05, 2.0 * r.wheel_radius)),
            mass=0.2,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            f"base_to_caster_wheel_{i}",
            ArticulationType.CONTINUOUS,
            parent=base,
            child=wheel,
            origin=Origin(
                xyz=(
                    r.caster_radius_pos * math.cos(ang),
                    r.caster_radius_pos * math.sin(ang),
                    r.wheel_radius,
                ),
                rpy=(0.0, 0.0, ang),
            ),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=20.0),
        )

    # Gas piston (PRISMATIC +Z).
    lift_piston = model.part("lift_piston")
    lift_piston.visual(
        Cylinder(radius=0.0165, length=0.252),
        origin=Origin(xyz=(0.0, 0.0, -0.064)),
        material=mats["accent"],
        name="piston_rod", material_class_id="metal.chrome_polished",
    )
    lift_piston.inertial = Inertial.from_geometry(
        Box((0.033, 0.033, 0.25)),
        mass=0.6,
        origin=Origin(xyz=(0.0, 0.0, -0.06)),
    )
    model.articulation(
        "base_to_lift_piston",
        ArticulationType.PRISMATIC,
        parent=pedestal_anchor,
        child=lift_piston,
        origin=Origin(xyz=(0.0, 0.0, r.lift_tube_top)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=900.0, velocity=0.10, lower=0.0, upper=r.lift_travel),
    )

    seat = _build_seat(model, r, mats)
    model.articulation(
        "lift_piston_to_seat",
        ArticulationType.CONTINUOUS,
        parent=lift_piston,
        child=seat,
        origin=Origin(xyz=(0.0, 0.0, r.piston_top)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=3.0),
    )
    return seat


def _build_sled_base(model, r: ResolvedArmchairConfig, mats):
    """cantilever_sled: bent tubular root + swivel plate -> swivel seat."""
    sled = model.part("sled_base")
    mount_z = r.seat_frame_z
    for i, sign in enumerate((1.0, -1.0)):
        pts = [
            (0.24, sign * _SLED_RUNNER_Y, 0.015),
            (-0.20, sign * _SLED_RUNNER_Y, 0.015),
            (-0.26, sign * (_SLED_RUNNER_Y - 0.01), 0.08),
            (-0.24, sign * 0.18, mount_z * 0.55),
            (-0.16, sign * 0.14, mount_z * 0.85),
            (-0.02, sign * 0.06, mount_z - 0.01),
        ]
        geom = tube_from_spline_points(
            pts, radius=_TUBE_R, samples_per_segment=14, radial_segments=12, cap_ends=True
        )
        sled.visual(mesh_from_geometry(geom, f"sled_side_{i}"), material=mats["metal"], name=f"sled_side_{i}", material_class_id="metal.chrome_polished")
    for x, nm in ((0.24, "front_crossbar"), (-0.20, "rear_crossbar")):
        geom = tube_from_spline_points(
            [(x, -_SLED_RUNNER_Y, 0.015), (x, _SLED_RUNNER_Y, 0.015)],
            radius=_TUBE_R, samples_per_segment=8, radial_segments=12, cap_ends=True,
        )
        sled.visual(mesh_from_geometry(geom, nm), material=mats["metal"], name=nm, material_class_id="metal.chrome_polished")
    geom = tube_from_spline_points(
        [(-0.24, -0.18, mount_z * 0.5), (-0.24, 0.18, mount_z * 0.5)],
        radius=_TUBE_R, samples_per_segment=8, radial_segments=12, cap_ends=True,
    )
    sled.visual(mesh_from_geometry(geom, "mid_crossbar"), material=mats["metal"], name="mid_crossbar", material_class_id="metal.chrome_polished")
    sled.visual(
        Cylinder(radius=0.055, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, mount_z - 0.006)),
        material=mats["metal"],
        name="swivel_plate", material_class_id="metal.chrome_polished",
    )
    for sx in (0.24, -0.20):
        for sy in (_SLED_RUNNER_Y, -_SLED_RUNNER_Y):
            sled.visual(
                Cylinder(radius=0.018, length=0.006),
                origin=Origin(xyz=(sx, sy, 0.003)),
                material=mats["rubber"],
                name=f"foot_{('f' if sx > 0 else 'r')}_{('l' if sy > 0 else 'r')}", material_class_id="rubber.smooth_plain",
            )
    sled.inertial = Inertial.from_geometry(
        Box((0.5, 2.0 * _SLED_RUNNER_Y, mount_z)),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, mount_z / 2.0)),
    )
    seat = _build_seat(model, r, mats)
    model.articulation(
        "sled_to_seat",
        ArticulationType.CONTINUOUS,
        parent=sled,
        child=seat,
        origin=Origin(xyz=(0.0, 0.0, mount_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=3.0),
    )
    return seat


def _build_wood_legs_base(model, r: ResolvedArmchairConfig, mats):
    """four_wood_legs: seat is the root; 4 splayed legs are inline visuals."""
    seat = _build_seat(model, r, mats)
    z0 = r.seat_z0  # seat plane height above the floor (legs span z0 -> 0)
    # 4 splayed legs reaching from the seat underside down to the floor.
    leg_corners = (
        (0.18, r.seat_half_w - 0.02),
        (0.18, -(r.seat_half_w - 0.02)),
        (-0.18, r.seat_half_w - 0.02),
        (-0.18, -(r.seat_half_w - 0.02)),
    )
    # Apron rails tie the four leg mounts into the central seat pan so the legs
    # are not disconnected islands. The apron straddles the seat_pan underside.
    apron_z = z0
    front_x = leg_corners[0][0]
    rail_y = leg_corners[0][1]
    for nm, sx, sy, sz, ox, oy in (
        ("apron_front", 0.06, 2.0 * rail_y, 0.05, front_x, 0.0),
        ("apron_rear", 0.06, 2.0 * rail_y, 0.05, -front_x, 0.0),
        ("apron_left", 2.0 * front_x, 0.06, 0.05, 0.0, rail_y),
        ("apron_right", 2.0 * front_x, 0.06, 0.05, 0.0, -rail_y),
    ):
        seat.visual(
            Box((sx, sy, sz)),
            origin=Origin(xyz=(ox, oy, apron_z)),
            material=mats["wood"],
            name=nm, material_class_id=("wood.walnut_dark" if r.palette_style in {"blue_mesh_teal", "matte_black_office", "racing_black_orange", "sage_velvet_walnut"} else "wood.oak"),
        )
    for i, (lx, ly) in enumerate(leg_corners):
        fx = lx * (1.0 + _LEG_SPLAY)
        fy = ly * (1.0 + _LEG_SPLAY)
        leg_geom = tube_from_spline_points(
            [
                (lx, ly, z0 + 0.0),
                (lx * 1.05 + (fx - lx) * 0.5, ly * 1.05 + (fy - ly) * 0.5, z0 * 0.5),
                (fx, fy, 0.03),
            ],
            radius=0.018,
            samples_per_segment=12,
            radial_segments=12,
            cap_ends=True,
        )
        seat.visual(mesh_from_geometry(leg_geom, f"leg_{i}"), material=mats["wood"], name=f"leg_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"blue_mesh_teal", "matte_black_office", "racing_black_orange", "sage_velvet_walnut"} else "wood.oak"))
        # Tenon mount block joining the leg top into the apron.
        seat.visual(
            Box((0.05, 0.05, 0.05)),
            origin=Origin(xyz=(lx, ly, apron_z)),
            material=mats["wood"],
            name=f"leg_mount_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"blue_mesh_teal", "matte_black_office", "racing_black_orange", "sage_velvet_walnut"} else "wood.oak"),
        )
        # Floor glide (top reaches the leg foot at z=0.03, bottom rests on floor).
        seat.visual(
            Cylinder(radius=0.020, length=0.036),
            origin=Origin(xyz=(fx, fy, 0.018)),
            material=mats["rubber"],
            name=f"leg_glide_{i}", material_class_id="rubber.smooth_plain",
        )
    return seat


_BASE_BUILDERS = {
    "five_star_caster": _build_caster_base,
    "four_wood_legs": _build_wood_legs_base,
    "cantilever_sled": _build_sled_base,
}


# ---------------------------------------------------------------------------
# Recline builders. Emit the backrest part (+ optional footrest / rocker) and
# the recline joint(s). Take the already-built seat.
# ---------------------------------------------------------------------------
def _build_backrest(model, r: ResolvedArmchairConfig, mats, seat) -> object:
    backrest = model.part("backrest")
    _emit_backrest_form(backrest, r, mats)
    backrest.inertial = Inertial.from_geometry(
        Box((0.10, 2.0 * r.seat_half_w, 0.6 * r.back_scale)),
        mass=3.0,
        origin=Origin(xyz=(-0.05, 0.0, 0.3 * r.back_scale)),
    )
    px, py, pz = _RECLINE_PIVOT
    model.articulation(
        "seat_to_backrest",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=backrest,
        origin=Origin(xyz=(px, py, pz + r.seat_z0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=200.0, velocity=1.0, lower=r.recline_lower, upper=0.0),
    )
    return backrest


def _build_swivel_tilt(model, r: ResolvedArmchairConfig, mats, seat):
    _build_backrest(model, r, mats, seat)


def _build_rocker_glider(model, r: ResolvedArmchairConfig, mats, seat):
    """Recline + an extra low transverse REVOLUTE rocker. The rocker rail part
    hangs off the seat as a visible cradle that rocks the assembly. Source:
    84c9e022."""
    _build_backrest(model, r, mats, seat)
    # A seat-side pivot stub reaching down to the rock axis so the joint origin
    # sits on real seat geometry (mech bottom is only ~-0.06).
    seat.visual(
        Box((0.12, 2.0 * r.seat_half_w * 0.5, _ROCK_JOINT_Z)),
        origin=Origin(xyz=(0.0, 0.0, -_ROCK_JOINT_Z / 2.0)),
        material=mats["frame"],
        name="rocker_mount", material_class_id="metal.paint_coated",
    )
    # Rocker carriage: an arc rail mounted under the seat, rocking about +Y.
    carriage = model.part("rocker_carriage")
    for label, sign in (("left", 1.0), ("right", -1.0)):
        rail_geom = tube_from_spline_points(
            [
                (0.24, sign * (r.seat_half_w - 0.02), -0.02),
                (0.0, sign * (r.seat_half_w - 0.02), -0.05),
                (-0.24, sign * (r.seat_half_w - 0.02), -0.02),
            ],
            radius=0.016,
            samples_per_segment=14,
            radial_segments=12,
            cap_ends=True,
        )
        carriage.visual(
            mesh_from_geometry(rail_geom, f"rocker_rail_{label}"),
            material=mats["wood"],
            name=f"rocker_rail_{label}", material_class_id=("wood.walnut_dark" if r.palette_style in {"blue_mesh_teal", "matte_black_office", "racing_black_orange", "sage_velvet_walnut"} else "wood.oak"),
        )
    carriage.visual(
        Box((0.40, 2.0 * r.seat_half_w - 0.02, 0.03)),
        origin=Origin(xyz=(0.0, 0.0, -0.02)),
        material=mats["wood"],
        name="rocker_deck", material_class_id=("wood.walnut_dark" if r.palette_style in {"blue_mesh_teal", "matte_black_office", "racing_black_orange", "sage_velvet_walnut"} else "wood.oak"),
    )
    carriage.inertial = Inertial.from_geometry(
        Box((0.5, 2.0 * r.seat_half_w, 0.06)),
        mass=1.0,
        origin=Origin(xyz=(0.0, 0.0, -0.03)),
    )
    model.articulation(
        "seat_to_rocker",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, -_ROCK_JOINT_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=2.0, lower=-_ROCK_LIMIT, upper=_ROCK_LIMIT),
    )


def _build_full_recliner_footrest(model, r: ResolvedArmchairConfig, mats, seat):
    """Deep recline + a PRISMATIC footrest sliding out from the seat front.
    Source: ad4e3477."""
    _build_backrest(model, r, mats, seat)
    z0 = r.seat_z0
    # Hollow U-channel guide under the seat front so the sliding plate has a
    # believable open guide sleeve instead of a solid block. The guide is long
    # enough (x out to 0.45) that the rail tail stays nested at the full
    # _FOOTREST_TRAVEL extension (the original short guide let the footrest
    # float 0.14 m clear of the seat). Side guides ride higher than the panel
    # so the retracted panel never clips them.
    seat.visual(
        Box((0.40, 0.18, 0.012)),
        origin=Origin(xyz=(0.25, 0.0, z0 - 0.022)),
        material=mats["frame"],
        name="footrest_guide_top", material_class_id="metal.paint_coated",
    )
    for label, sign in (("left", 1.0), ("right", -1.0)):
        seat.visual(
            Box((0.40, 0.020, 0.024)),
            origin=Origin(xyz=(0.25, sign * 0.070, z0 - 0.016)),
            material=mats["frame"],
            name=f"footrest_guide_{label}", material_class_id="metal.paint_coated",
        )
    footrest = model.part("footrest")
    # Center rail spanning the part origin so the joint origin lies on geometry.
    # Authored clear of the seat mech housing (x<=0.12) at rest while nesting
    # in the seat-side guide across the whole slide travel.
    footrest.visual(
        Box((0.30, 0.06, 0.030)),
        origin=Origin(xyz=(0.015, 0.0, 0.0)),
        material=mats["frame"],
        name="footrest_center_rail", material_class_id="metal.paint_coated",
    )
    # Footrest authored at the seat-front guide frame (rail at part origin).
    footrest.visual(
        Box((0.10, 2.0 * r.seat_half_w * 0.8, 0.020)),
        origin=Origin(xyz=(0.16, 0.0, 0.0)),
        material=mats["cushion"],
        name="footrest_panel", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
    )
    for label, sign in (("left", 1.0), ("right", -1.0)):
        footrest.visual(
            Box((0.30, 0.03, 0.030)),
            origin=Origin(xyz=(0.015, sign * 0.07, 0.0)),
            material=mats["frame"],
            name=f"footrest_rail_{label}", material_class_id="metal.paint_coated",
        )
    footrest.inertial = Inertial.from_geometry(
        Box((0.24, 2.0 * r.seat_half_w * 0.8, 0.05)),
        mass=1.0,
        origin=Origin(xyz=(0.1, 0.0, 0.0)),
    )
    model.articulation(
        "seat_to_footrest",
        ArticulationType.PRISMATIC,
        parent=seat,
        child=footrest,
        origin=Origin(xyz=(0.26, 0.0, z0 - 0.04)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.10, lower=0.0, upper=_FOOTREST_TRAVEL),
    )


_RECLINE_BUILDERS = {
    "swivel_tilt": _build_swivel_tilt,
    "rocker_glider": _build_rocker_glider,
    "full_recliner_footrest": _build_full_recliner_footrest,
}


# ---------------------------------------------------------------------------
# Armrest builders (moving variants). fixed_arms is handled inline in the seat.
# ---------------------------------------------------------------------------
def _armrest_arm_geom(sign: float, name: str):
    pts = [
        (0.0, 0.0, 0.0),
        (0.10, sign * 0.01, 0.02),
        (0.20, sign * 0.0, 0.03),
    ]
    geom = tube_from_spline_points(
        pts, radius=0.018, samples_per_segment=10, radial_segments=12, cap_ends=True
    )
    return mesh_from_geometry(geom, name)


def _build_flip_up_armrests(model, r: ResolvedArmchairConfig, mats, seat):
    """2 armrest parts, REVOLUTE -Y, flip upward (mirrored). Source: 68a45f62."""
    z0 = r.seat_z0
    # Wide sculpted cushions (office_mesh loft tops out at z0+0.137, half-width
    # ~0.253) swallow the fixed hinge point, so push the hinge outward/upward
    # past the actual cushion envelope instead of the historical constant.
    hinge_y = max(_ARMREST_HINGE_Y, r.seat_half_w + 0.05)
    hinge_z = max(_ARMREST_HINGE_Z, 0.16)
    for i, sign in enumerate((1.0, -1.0)):
        # Mount bracket on the seat (visible anchor for the hinge). Long enough
        # to root in the seat body so it never floats beside the cushion.
        seat.visual(
            Box((0.050, 0.12, 0.085)),
            origin=Origin(xyz=(_ARMREST_HINGE_X, sign * (hinge_y - 0.05), z0 + hinge_z - 0.035)),
            material=mats["frame"],
            name=f"armrest_mount_{i}", material_class_id="metal.paint_coated",
        )
        armrest = model.part(f"armrest_{i}")
        armrest.visual(
            Cylinder(radius=0.015, length=0.050),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name="hinge_barrel", material_class_id="metal.paint_coated",
        )
        armrest.visual(
            _armrest_arm_geom(sign, "support_arm"),
            material=mats["frame"],
            name="support_arm", material_class_id="metal.paint_coated",
        )
        armrest.visual(
            Box((0.22, 0.06, 0.025)),
            origin=Origin(xyz=(0.20, 0.0, 0.03)),
            material=mats["cushion"],
            name="armrest_pad", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
        )
        armrest.inertial = Inertial.from_geometry(
            Box((0.30, 0.06, 0.06)),
            mass=0.4,
            origin=Origin(xyz=(0.15, 0.0, 0.02)),
        )
        model.articulation(
            f"seat_to_armrest_{i}",
            ArticulationType.REVOLUTE,
            parent=seat,
            child=armrest,
            origin=Origin(xyz=(_ARMREST_HINGE_X, sign * hinge_y, z0 + hinge_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=_ARMREST_FLIP_UPPER),
        )


def _build_height_adjust_armrests(model, r: ResolvedArmchairConfig, mats, seat):
    """2 armrest parts, PRISMATIC +Z, post slides in a seat sleeve. Source: 75232ed3."""
    z0 = r.seat_z0
    sleeve_y = max(_ARMREST_SLEEVE_Y, r.seat_half_w + 0.018)
    for i, sign in enumerate((1.0, -1.0)):
        # Bracket bridging the seat side out to the sleeve (so the sleeve is
        # supported, not a floating island when the seat is narrow).
        seat.visual(
            Box((0.10, sleeve_y - 0.05, 0.04)),
            origin=Origin(xyz=(0.02, sign * (sleeve_y / 2.0 + 0.02), z0 + _ARMREST_JOINT_Z - 0.04)),
            material=mats["frame"],
            name=f"armrest_bracket_{i}", material_class_id="metal.paint_coated",
        )
        # Sleeve on the seat (captures the sliding post).
        seat.visual(
            Cylinder(radius=0.020, length=0.10),
            origin=Origin(xyz=(0.02, sign * sleeve_y, z0 + _ARMREST_JOINT_Z - 0.04)),
            material=mats["frame"],
            name=f"armrest_sleeve_{i}", material_class_id="metal.paint_coated",
        )
        armrest = model.part(f"armrest_{i}")
        armrest.visual(
            Cylinder(radius=0.014, length=0.12),
            origin=Origin(xyz=(0.0, 0.0, 0.02)),
            material=mats["accent"],
            name="post", material_class_id="metal.paint_coated",
        )
        armrest.visual(
            Cylinder(radius=0.022, length=0.02),
            origin=Origin(xyz=(0.0, 0.0, 0.085)),
            material=mats["frame"],
            name="pad_mount", material_class_id="metal.paint_coated",
        )
        armrest.visual(
            Box((0.20, 0.06, 0.025)),
            origin=Origin(xyz=(0.0, 0.0, 0.105)),
            material=mats["cushion"],
            name="armrest_pad", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"tan_leather_grey_fabric", "blue_mesh_teal", "matte_black_office", "cream_boucle", "sage_velvet_walnut"} else "leather.smooth_plain"),
        )
        armrest.inertial = Inertial.from_geometry(
            Box((0.20, 0.06, 0.16)),
            mass=0.4,
            origin=Origin(xyz=(0.0, 0.0, 0.05)),
        )
        model.articulation(
            f"seat_to_armrest_{i}",
            ArticulationType.PRISMATIC,
            parent=seat,
            child=armrest,
            origin=Origin(xyz=(0.02, sign * sleeve_y, z0 + _ARMREST_JOINT_Z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=200.0, velocity=0.05, lower=0.0, upper=_ARMREST_TRAVEL),
        )


_ARMREST_BUILDERS = {
    "flip_up": _build_flip_up_armrests,
    "height_adjust": _build_height_adjust_armrests,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_armchair(
    config: ArmchairConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"armchair_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    mats["hidden"] = model.material("armchair_hidden_joint_helpers", rgba=(0.0, 0.0, 0.0, 0.0))

    seat = _BASE_BUILDERS[r.base_support](model, r, mats)
    _RECLINE_BUILDERS[r.recline_mechanism](model, r, mats, seat)
    if r.armrest in _ARMREST_BUILDERS:
        _ARMREST_BUILDERS[r.armrest](model, r, mats, seat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_armchair(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_armchair(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_armchair_tests(
    object_model: ArticulatedObject,
    config: ArmchairConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    seat = object_model.get_part("seat")

    # ---- Captured-pin / slide allowances (element-scoped). ----
    if r.base_support == "five_star_caster":
        pedestal_anchor = object_model.get_part("pedestal_anchor")
        base = object_model.get_part("base")
        lift_piston = object_model.get_part("lift_piston")
        ctx.allow_overlap(
            pedestal_anchor, base, elem_a="pedestal_spindle", elem_b="pedestal_socket",
            reason="The hidden pedestal spindle is captured concentrically inside the rotating base socket.",
        )
        ctx.allow_overlap(
            pedestal_anchor, base, elem_a="pedestal_hidden_core", elem_b="pedestal_socket",
            reason="The hidden pedestal core passes through the rotating base socket.",
        )
        ctx.allow_overlap(
            pedestal_anchor, base, elem_a="pedestal_hidden_core", elem_b="star_hub",
            reason="The hidden pedestal core is nested through the center of the star hub.",
        )
        ctx.allow_overlap(
            pedestal_anchor, base, elem_a="lift_tube", elem_b="star_hub",
            reason="The fixed gas-lift tube rises through the rotating star hub bore.",
        )
        ctx.allow_overlap(
            pedestal_anchor, lift_piston, elem_a="lift_tube", elem_b="piston_rod",
            reason="Gas-lift piston rod slides inside the solid outer tube proxy.",
        )
        ctx.allow_overlap(
            pedestal_anchor, lift_piston, elem_a="pedestal_hidden_core", elem_b="piston_rod",
            reason="The piston rod continues through the hidden central pedestal core.",
        )
        ctx.allow_overlap(
            pedestal_anchor, lift_piston, elem_a="lift_collar", elem_b="piston_rod",
            reason="Piston rod passes through the chrome collar ring at the tube mouth.",
        )
        ctx.allow_overlap(
            pedestal_anchor, seat, elem_a="lift_tube", elem_b="mech_housing",
            reason="Seat mechanism socket nests over the gas-lift tube mouth.",
        )
        ctx.allow_overlap(
            base, lift_piston, elem_a="star_hub", elem_b="piston_rod",
            reason="Piston rod bottoms out into the star hub bore at a low seat height.",
        )
        ctx.allow_overlap(
            lift_piston, seat, elem_a="piston_rod", elem_b="mech_housing",
            reason="Piston top is seated in the tilt-mechanism socket under the seat.",
        )
        for el in ("pod_shell", "seat_bucket", "mech_housing"):
            ctx.allow_overlap(
                pedestal_anchor, seat, elem_a="lift_collar", elem_b=el,
                reason="Seat shell seats over the gas-lift collar at the swivel mount.",
            )
            ctx.allow_overlap(
                lift_piston, seat, elem_a="piston_rod", elem_b=el,
                reason="Piston rod seats into the seat shell underside at the swivel.",
            )
        for i in range(r.caster_count):
            ctx.allow_overlap(
                base, object_model.get_part(f"caster_wheel_{i}"),
                elem_a=f"caster_yoke_{i}", elem_b="axle",
                reason="Twin-wheel axle is captured through the caster yoke hub.",
            )
    elif r.base_support == "cantilever_sled":
        sled = object_model.get_part("sled_base")
        ctx.allow_overlap(
            sled, seat, elem_a="swivel_plate", elem_b="mech_housing",
            reason="Seat mech housing rests on the sled swivel bearing plate.",
        )
        for i in range(2):
            for el in ("mech_housing", "pod_shell", "seat_bucket", "seat_pan"):
                ctx.allow_overlap(
                    sled, seat, elem_a=f"sled_side_{i}", elem_b=el,
                    reason="Sled top risers meet the seat shell at the swivel mount.",
                )
            ctx.allow_overlap(
                sled, seat, elem_a="swivel_plate", elem_b="pod_shell",
                reason="Egg-pod seat shell seats on the sled swivel plate.",
            )

    # Backrest pivot captured in the seat rear bracket; backrest base meets the
    # seat at the recline seam (upholstery junction).
    backrest = object_model.get_part("backrest")
    ctx.allow_overlap(
        seat, backrest, elem_a="mech_rear_bracket", elem_b="pivot_barrel",
        reason="Backrest pivot barrel is captured in the mechanism rear bracket clevis.",
    )
    _seat_lower = (
        "seat_pan", "seat_cushion", "seat_piping", "mech_housing", "mech_rear_bracket",
        "apron_front", "apron_rear", "apron_left", "apron_right",
        "pod_shell", "pod_rear_lip", "pod_side_bolster_left", "pod_side_bolster_right",
        "seat_bucket", "seat_bolster_left", "seat_bolster_right",
    )
    _back_lower = (
        "back_panel", "back_cushion", "back_panel_0", "back_panel_1", "back_panel_2",
        "back_cushion_0", "back_cushion_1", "back_cushion_2",
        "mesh_panel", "mesh_panel_mid", "mesh_panel_upper", "mesh_bridge",
        "spine", "bottom_rail", "back_shell", "backrest_frame", "frame_strut_left", "frame_strut_right",
        "pivot_barrel", "left_pivot_arm", "right_pivot_arm",
    )
    for sa in _seat_lower:
        for bb in _back_lower:
            ctx.allow_overlap(
                seat, backrest, elem_a=sa, elem_b=bb,
                reason="Backrest base meets the seat rear at the recline seam.",
            )

    # Recline-mechanism allowances.
    if r.recline_mechanism == "rocker_glider":
        carriage = object_model.get_part("rocker_carriage")
        ctx.allow_overlap(
            seat, carriage,
            reason="Rocker carriage cradles under the seat at the low rock axis.",
        )
        # Rocker carriage dips down toward the base/sled at the low rock axis.
        if r.base_support == "five_star_caster":
            base = object_model.get_part("base")
            pedestal_anchor = object_model.get_part("pedestal_anchor")
            piston = object_model.get_part("lift_piston")
            for el in ("lift_tube", "lift_collar"):
                ctx.allow_overlap(
                    carriage, pedestal_anchor,
                    elem_a="rocker_deck", elem_b=el,
                    reason="Rocker carriage straddles the gas-lift column at the rock axis.",
                )
            ctx.allow_overlap(
                carriage, base,
                elem_a="rocker_deck", elem_b="star_hub",
                reason="Rocker carriage straddles the star hub at the rock axis.",
            )
            ctx.allow_overlap(
                carriage, piston, elem_a="rocker_deck", elem_b="piston_rod",
                reason="Rocker carriage straddles the gas-lift piston at the rock axis.",
            )
            ctx.allow_overlap(
                seat, piston, elem_a="rocker_mount", elem_b="piston_rod",
                reason="Seat rocker mount sleeves over the gas-lift piston top.",
            )
            for el in ("lift_collar", "lift_tube"):
                ctx.allow_overlap(
                    seat, pedestal_anchor, elem_a="rocker_mount", elem_b=el,
                    reason="Seat rocker mount reaches down past the gas-lift column.",
                )
            ctx.allow_overlap(
                seat, base, elem_a="rocker_mount", elem_b="star_hub",
                reason="Seat rocker mount reaches down past the star hub.",
            )
        elif r.base_support == "cantilever_sled":
            root = object_model.get_part("sled_base")
            for i in range(2):
                ctx.allow_overlap(
                    carriage, root,
                    elem_a="rocker_deck", elem_b=f"sled_side_{i}",
                    reason="Rocker carriage straddles the sled risers at the rock axis.",
                )
                ctx.allow_overlap(
                    carriage, root,
                    elem_a="rocker_deck", elem_b="swivel_plate",
                    reason="Rocker carriage straddles the sled swivel plate at the rock axis.",
                )
                ctx.allow_overlap(
                    seat, root, elem_a="rocker_mount", elem_b=f"sled_side_{i}",
                    reason="Seat rocker mount reaches down past the sled risers.",
                )
            ctx.allow_overlap(
                seat, root, elem_a="rocker_mount", elem_b="swivel_plate",
                reason="Seat rocker mount sleeves over the sled swivel plate.",
            )
            for label in ("left", "right"):
                for i in range(2):
                    ctx.allow_overlap(
                        carriage, root,
                        elem_a=f"rocker_rail_{label}", elem_b=f"sled_side_{i}",
                        reason="Rocker rails clear the sled risers at the rock axis.",
                    )
    elif r.recline_mechanism == "full_recliner_footrest":
        footrest = object_model.get_part("footrest")
        for guide_el in ("footrest_guide_top", "footrest_guide_left", "footrest_guide_right"):
            for el in ("footrest_rail_left", "footrest_rail_right", "footrest_center_rail"):
                ctx.allow_overlap(
                    seat, footrest, elem_a=guide_el, elem_b=el,
                    reason="Footrest rails slide inside the hollow seat-front guide channel.",
                )
            for sel in ("seat_bucket", "seat_pan", "seat_cushion", "pod_shell",
                        "seat_bolster_left", "seat_bolster_right"):
                for el in ("footrest_rail_left", "footrest_rail_right", "footrest_center_rail"):
                    ctx.allow_overlap(
                        seat, footrest, elem_a=sel, elem_b=el,
                        reason="Footrest rails tuck under the seat shell front at the guide.",
                    )

    # Armrest allowances.
    if r.armrest == "flip_up":
        for i in range(2):
            ctx.allow_overlap(
                object_model.get_part(f"armrest_{i}"), seat,
                elem_a="hinge_barrel", elem_b=f"armrest_mount_{i}",
                reason="Armrest hinge barrel is captured in the seat mount bracket.",
            )
            ctx.allow_overlap(
                object_model.get_part(f"armrest_{i}"), seat,
                elem_a="support_arm", elem_b=f"armrest_mount_{i}",
                reason="Armrest support arm root meets the seat mount bracket at the hinge.",
            )
    elif r.armrest == "height_adjust":
        for i in range(2):
            arm = object_model.get_part(f"armrest_{i}")
            ctx.allow_overlap(
                arm, seat, elem_a="post", elem_b=f"armrest_sleeve_{i}",
                reason="Armrest post slides inside the seat-mounted sleeve for height adjust.",
            )
            ctx.allow_overlap(
                arm, seat, elem_a="post", elem_b=f"armrest_bracket_{i}",
                reason="Armrest post passes down through the seat-side sleeve bracket.",
            )
            for el in (
                "seat_bucket", "seat_pan", "seat_cushion", "mech_housing",
                "seat_bolster_left", "seat_bolster_right",
            ):
                ctx.allow_overlap(
                    arm, seat, elem_a="post", elem_b=el,
                    reason="Armrest post passes alongside the seat shell at the sleeve.",
                )
                ctx.allow_overlap(
                    arm, seat, elem_a="pad_mount", elem_b=el,
                    reason="Armrest pad mount passes alongside the seat shell at the sleeve.",
                )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=32,
        overlap_tol=0.005,
        overlap_volume_tol=0.0,
        ignore_adjacent=False,
        ignore_fixed=True,
    )
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("seat part present", "seat" in part_names, details=str(sorted(part_names)))
    ctx.check("backrest part present", "backrest" in part_names, details=str(sorted(part_names)))

    # Recline joint topology.
    rec = object_model.get_articulation("seat_to_backrest")
    ctx.check(
        "recline is REVOLUTE about +Y",
        rec.articulation_type == ArticulationType.REVOLUTE and abs(rec.axis[1]) > 0.99,
        details=f"type={rec.articulation_type} axis={tuple(rec.axis)}",
    )

    # Base-support joint topology.
    if r.base_support == "five_star_caster":
        pj = object_model.get_articulation("pedestal_anchor_to_base")
        ctx.check(
            "pedestal swivel is CONTINUOUS about +Z",
            pj.articulation_type == ArticulationType.CONTINUOUS and abs(pj.axis[2]) > 0.99,
            details=f"axis={tuple(pj.axis)}",
        )
        ctx.check(
            "pedestal swivel only drives the wheeled base branch",
            pj.parent == "pedestal_anchor" and pj.child == "base",
            details=f"parent={pj.parent} child={pj.child}",
        )
        wj = object_model.get_articulation("base_to_caster_wheel_0")
        ctx.check(
            "caster wheel is CONTINUOUS about a horizontal axle",
            wj.articulation_type == ArticulationType.CONTINUOUS and abs(wj.axis[2]) < 1e-9,
            details=f"axis={tuple(wj.axis)}",
        )
        lj = object_model.get_articulation("base_to_lift_piston")
        ctx.check(
            "gas lift is PRISMATIC about +Z",
            lj.articulation_type == ArticulationType.PRISMATIC and abs(lj.axis[2]) > 0.99,
            details=f"axis={tuple(lj.axis)}",
        )
        ctx.check(
            "gas lift is separate from the rotating wheeled base",
            lj.parent == "pedestal_anchor" and lj.child == "lift_piston",
            details=f"parent={lj.parent} child={lj.child}",
        )
        sj = object_model.get_articulation("lift_piston_to_seat")
        ctx.check(
            "swivel is CONTINUOUS about +Z",
            sj.articulation_type == ArticulationType.CONTINUOUS and abs(sj.axis[2]) > 0.99,
            details=f"axis={tuple(sj.axis)}",
        )
        ctx.check(
            "seat swivel stays on the lift-piston branch",
            sj.parent == "lift_piston" and sj.child == "seat",
            details=f"parent={sj.parent} child={sj.child}",
        )
        # caster count of wheel parts.
        wheels = [p for p in part_names if p.startswith("caster_wheel_")]
        ctx.check(
            "N caster wheels emitted",
            len(wheels) == r.caster_count,
            details=f"wheels={len(wheels)} N={r.caster_count}",
        )
    elif r.base_support == "cantilever_sled":
        sj = object_model.get_articulation("sled_to_seat")
        ctx.check(
            "sled swivel is CONTINUOUS about +Z",
            sj.articulation_type == ArticulationType.CONTINUOUS and abs(sj.axis[2]) > 0.99,
            details=f"axis={tuple(sj.axis)}",
        )
    else:  # four_wood_legs: seat is root (no support joint).
        roots = [p.name for p in object_model.root_parts()]
        ctx.check(
            "wood-legs seat is the root part",
            roots == ["seat"],
            details=f"roots={roots}",
        )

    # Recline-mechanism extra joint topology.
    if r.recline_mechanism == "rocker_glider":
        rj = object_model.get_articulation("seat_to_rocker")
        ctx.check(
            "rocker is an extra REVOLUTE about +Y",
            rj.articulation_type == ArticulationType.REVOLUTE and abs(rj.axis[1]) > 0.99,
            details=f"axis={tuple(rj.axis)}",
        )
    elif r.recline_mechanism == "full_recliner_footrest":
        fj = object_model.get_articulation("seat_to_footrest")
        ctx.check(
            "footrest is an extra PRISMATIC about +X",
            fj.articulation_type == ArticulationType.PRISMATIC and abs(fj.axis[0]) > 0.99,
            details=f"axis={tuple(fj.axis)}",
        )

    # Armrest joint topology.
    if r.armrest == "flip_up":
        a0 = object_model.get_articulation("seat_to_armrest_0")
        a1 = object_model.get_articulation("seat_to_armrest_1")
        ctx.check(
            "flip-up armrests are 2 REVOLUTE -Y joints",
            a0.articulation_type == ArticulationType.REVOLUTE
            and a1.articulation_type == ArticulationType.REVOLUTE
            and abs(a0.axis[1]) > 0.99 and abs(a1.axis[1]) > 0.99,
            details=f"a0={tuple(a0.axis)} a1={tuple(a1.axis)}",
        )
    elif r.armrest == "height_adjust":
        a0 = object_model.get_articulation("seat_to_armrest_0")
        ctx.check(
            "height-adjust armrests are PRISMATIC +Z",
            a0.articulation_type == ArticulationType.PRISMATIC and abs(a0.axis[2]) > 0.99,
            details=f"axis={tuple(a0.axis)}",
        )
    else:  # fixed_arms: no armrest joint.
        ctx.check(
            "fixed_arms has no armrest joint",
            not any(a.name.startswith("seat_to_armrest_") for a in object_model.articulations),
            details="fixed_arms",
        )

    # ---- Recline actuation tips the backrest backward. ----
    closed = ctx.part_world_aabb(backrest)
    with ctx.pose({rec: r.recline_lower}):
        reclined = ctx.part_world_aabb(backrest)
    if closed is not None and reclined is not None:
        ctx.check(
            "backrest reclines backward (top moves toward -X)",
            reclined[0][0] < closed[0][0] - 0.02,
            details=f"closed_xmin={closed[0][0]:.3f} reclined_xmin={reclined[0][0]:.3f}",
        )

    if r.chair_form == "office_mesh":
        frame_aabb = ctx.part_element_world_aabb(backrest, elem="backrest_frame")
        seat_cushion_aabb = ctx.part_element_world_aabb(seat, elem="seat_cushion")
        piping_aabb = ctx.part_element_world_aabb(seat, elem="seat_piping")
        lumbar_aabb = ctx.part_element_world_aabb(backrest, elem="lumbar_pad")
        top_edge_aabb = ctx.part_element_world_aabb(backrest, elem="mesh_top_tension_edge")
        bottom_edge_aabb = ctx.part_element_world_aabb(backrest, elem="mesh_bottom_tension_edge")
        left_edge_aabb = ctx.part_element_world_aabb(backrest, elem="mesh_left_tension_edge")
        right_edge_aabb = ctx.part_element_world_aabb(backrest, elem="mesh_right_tension_edge")
        mid_h_aabb = ctx.part_element_world_aabb(backrest, elem=f"mesh_h_{_OFFICE_MESH_H_COUNT // 2}")
        assert frame_aabb and seat_cushion_aabb and piping_aabb
        assert top_edge_aabb and bottom_edge_aabb and left_edge_aabb and right_edge_aabb and mid_h_aabb
        ctx.check(
            "office seat piping rides proud of the seat cushion edge",
            piping_aabb[1][2] > seat_cushion_aabb[0][2] + 0.04
            and piping_aabb[0][0] < seat_cushion_aabb[0][0] + 0.01
            and piping_aabb[1][0] > seat_cushion_aabb[1][0] - 0.01
            and piping_aabb[0][1] < seat_cushion_aabb[0][1] + 0.01
            and piping_aabb[1][1] > seat_cushion_aabb[1][1] - 0.01,
            details=f"piping={piping_aabb} cushion={seat_cushion_aabb}",
        )
        ctx.check(
            "office mesh grid visuals are emitted",
            all(ctx.part_element_world_aabb(backrest, elem=f"mesh_h_{i}") is not None for i in range(_OFFICE_MESH_H_COUNT))
            and all(ctx.part_element_world_aabb(backrest, elem=f"mesh_v_{i}") is not None for i in range(_OFFICE_MESH_V_COUNT)),
            details=f"expected {_OFFICE_MESH_H_COUNT} horizontal and {_OFFICE_MESH_V_COUNT} vertical strands",
        )
        ctx.check(
            "office back narrows toward the top instead of staying a flat slab",
            (mid_h_aabb[1][1] - mid_h_aabb[0][1]) > (top_edge_aabb[1][1] - top_edge_aabb[0][1]) + 0.06
            and (mid_h_aabb[1][1] - mid_h_aabb[0][1]) > (bottom_edge_aabb[1][1] - bottom_edge_aabb[0][1]) + 0.03,
            details=f"mid={mid_h_aabb} top={top_edge_aabb} bottom={bottom_edge_aabb}",
        )
        ctx.check(
            "office mesh omits center spine and lumbar plate",
            ctx.part_element_world_aabb(backrest, elem="spine") is None
            and ctx.part_element_world_aabb(backrest, elem="mesh_bridge") is None
            and lumbar_aabb is None,
            details="office_mesh should stay visually open behind the grid",
        )

    # ---- Footprint / ground / proportion. ----
    z_min = None
    for p in object_model.parts:
        pa = ctx.part_world_aabb(p)
        if pa is not None:
            z_min = pa[0][2] if z_min is None else min(z_min, pa[0][2])
    if z_min is not None:
        ctx.check("chair rests near the ground", z_min < 0.03, details=f"z_min={z_min:.4f}")
    ctx.check(
        "seat sits at chair height (0.30-0.70 m)",
        0.25 <= r.seat_frame_z <= 0.70,
        details=f"seat_frame_z={r.seat_frame_z:.3f}",
    )

    # Casters on the floor (caster base).
    if r.base_support == "five_star_caster":
        for i in range(r.caster_count):
            wa = ctx.part_world_aabb(object_model.get_part(f"caster_wheel_{i}"))
            ctx.check(
                f"caster wheel {i} rests on the floor",
                wa is not None and abs(wa[0][2]) <= 0.004,
                details=f"wheel {i} z_min={None if wa is None else wa[0][2]:.4f}",
            )

    # ---- slot_choices recorded with caster_count encoded. ----
    ctx.check(
        "slot_choices recorded with caster_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "ArmchairConfig",
    "ResolvedArmchairConfig",
    "build_armchair",
    "build_seeded_armchair",
    "config_from_seed",
    "resolve_config",
    "run_armchair_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
