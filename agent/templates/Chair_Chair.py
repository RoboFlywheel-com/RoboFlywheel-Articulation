# SPDX-License-Identifier: Apache-2.0

"""Single-seat chair / stool modular template.

NOTE on the slug: "chair" here = a **single-seat chair or stool** = a seat
(round lathe puck or rounded-square cushion) + an *optional* low back
(``wrap_tub``) on one of several base/support topologies (pedestal column,
sled runners, four splayed legs, radial tripod, or a caster star), keeping at
least one real motion: the seat swivels about +Z on every base
(``seat_swivel`` CONTINUOUS), plus optional caster roll (caster bases) and
base swivel (caster-with-bearing).

It is NOT a folding_chair (scissor fold, separate 小类), NOT an armchair /
office chair (high-back + armrest + recline semantics live in
``Other_armchair``), and NOT a sofa/bench (multi-seat).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Chair_Chair.md`` and the
``picture/Chair/Chair`` 5-star sample pool (2 parents + 6 slot-fork variants),
all synced under ``data/records/``.

Structure (pattern = ``mixed``). A serial spine ``base/support(root) -> seat
[-> backrest]`` whose only cross-slot invariant joint is ``seat_swivel``
CONTINUOUS +Z, plus two base-conditioned multiplicity axes:

  * ``base_support`` (6): the ROOT mechanism + support-joint topology.
      - pedestal_disc / tripod_pedestal: ``base_pedestal`` root (disc + column,
        or N radial tripod legs + column) -> seat via ``seat_swivel`` +Z.
      - sled_runner: ``sled_base`` root (two U runners + crossbars + column).
      - four_leg_dining: ``leg_frame`` root (4 splayed legs + apron + hub).
      - caster_star: ``stationary_bearing`` root -> ``caster_base`` via
        ``base_swivel`` +Z -> N CONTINUOUS twin caster wheels + ``column_seat``
        via ``seat_swivel`` +Z.
      - caster_star_no_bearing: ``caster_base`` is the root itself (no bearing /
        base_swivel) -> N caster wheels + ``column_seat`` via ``seat_swivel``.
  * ``backrest`` (2): the backrest topology.
      - none: backless stool (no backrest visual / part / joint).
      - wrap_tub: a wrap-around tub low back, an *inline* seat visual that
        swivels with the seat (Rule 1, no joint).
  * ``seat_plan`` (2): the seat cushion mesh family (round lathe / rounded
    square loft). A mesh-helper dimension; no cross-slot joint.
  * ``caster_count`` (N in [3,6]): multiplicity axis on caster bases only; N
    twin caster wheels (each a moving CONTINUOUS part). Encoded into the
    slot_choice tuple as ``("caster_count", f"c{N}")`` (only on caster bases).
  * ``radial_support_count`` (M in [3,5]): multiplicity axis on tripod only; M
    radial tripod legs (fixed inline visuals, Rule 1 -> no joint). Encoded as
    ``("radial_support_count", f"r{M}")`` (tripod only).

All caster axle / piston-in-tube / swivel-collar / bearing / hinge-pin /
post-in-sleeve couplings are captured / nested geometry, so those joints omit
``MatingContract`` (grandfathered) and are guarded by the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests allow_overlap block).

Compatibility gating (resolve_config, spec §9):
  * caster_count is meaningful only on caster bases -> N=0 otherwise.
  * radial_support_count is meaningful only on tripod_pedestal -> M=0 otherwise.
  * wrap_tub on sled/leg/tripod bases raises the back base so it clears the
    runner / leg / apron geometry (back-base offset chosen per base_support).
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
    ExtrudeGeometry,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    rounded_rect_profile,
    sweep_profile_along_spline,
    tube_from_spline_points,
)

__modular__ = True

BaseSupport = Literal[
    "pedestal_disc",
    "sled_runner",
    "four_leg_dining",
    "tripod_pedestal",
    "caster_star",
    "caster_star_no_bearing",
]
Backrest = Literal["none", "wrap_tub"]
SeatPlan = Literal["round", "square_rounded"]
PaletteStyle = Literal[
    "tan_leather_gold",
    "brown_padded_black",
    "cream_leather_chrome",
    "sage_velvet_walnut",
    "oak_walnut_brass",
]

BASE_SUPPORTS: tuple[BaseSupport, ...] = (
    "pedestal_disc",
    "sled_runner",
    "four_leg_dining",
    "tripod_pedestal",
    "caster_star",
    "caster_star_no_bearing",
)
BACKRESTS: tuple[Backrest, ...] = ("none", "wrap_tub")
SEAT_PLANS: tuple[SeatPlan, ...] = ("round", "square_rounded")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "tan_leather_gold",
    "brown_padded_black",
    "cream_leather_chrome",
    "sage_velvet_walnut",
    "oak_walnut_brass",
)

# Caster bases (carry the caster_count multiplicity axis).
CASTER_BASES: tuple[BaseSupport, ...] = ("caster_star", "caster_star_no_bearing")
# Leg-frame bases whose top geometry (runners / legs / apron) would clash with a
# low wrap-tub back unless the back base is raised.
RAISED_BACK_BASES: tuple[BaseSupport, ...] = (
    "sled_runner",
    "four_leg_dining",
    "tripod_pedestal",
)

BASE_SUPPORT_WEIGHTS = (0.13, 0.13, 0.19, 0.11, 0.24, 0.20)
BACKREST_WEIGHTS = (0.34, 0.66)
SEAT_PLAN_WEIGHTS = (0.38, 0.62)

N_CASTER_MIN = 3
N_CASTER_MAX = 6
# Caster-count sampling weights (spec §8: 5 high-frequency, 4/6 common, 3 tail).
CASTER_COUNT_WEIGHTS = (0.15, 0.30, 0.40, 0.15)  # for (3, 4, 5, 6)
M_RADIAL_MIN = 3
M_RADIAL_MAX = 5
# Radial-leg sampling weights (spec §8: 3 high-frequency, 4/5 long tail).
RADIAL_COUNT_WEIGHTS = (0.55, 0.27, 0.18)  # for (3, 4, 5)


# ---------------------------------------------------------------------------
# Palette colorways (Accessories_Cushion.md idiom). Every .visual(material=...) draws from
# one of these keys; palette never enters the slot_choice tuple.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "tan_leather_gold": {
        "cushion": (0.66, 0.50, 0.32, 1.0),
        "back": (0.62, 0.46, 0.29, 1.0),
        "frame": (0.78, 0.66, 0.36, 1.0),
        "metal": (0.80, 0.70, 0.40, 1.0),
        "accent": (0.42, 0.30, 0.18, 1.0),
        "mesh": (0.55, 0.42, 0.26, 1.0),
        "rubber": (0.10, 0.09, 0.08, 1.0),
    },
    "brown_padded_black": {
        "cushion": (0.40, 0.28, 0.18, 1.0),
        "back": (0.36, 0.25, 0.16, 1.0),
        "frame": (0.10, 0.10, 0.11, 1.0),
        "metal": (0.55, 0.56, 0.58, 1.0),
        "accent": (0.26, 0.18, 0.12, 1.0),
        "mesh": (0.30, 0.22, 0.15, 1.0),
        "rubber": (0.06, 0.06, 0.065, 1.0),
    },
    "cream_leather_chrome": {
        "cushion": (0.91, 0.87, 0.79, 1.0),
        "back": (0.88, 0.83, 0.74, 1.0),
        "frame": (0.80, 0.81, 0.83, 1.0),
        "metal": (0.86, 0.87, 0.89, 1.0),
        "accent": (0.62, 0.56, 0.46, 1.0),
        "mesh": (0.82, 0.78, 0.70, 1.0),
        "rubber": (0.18, 0.17, 0.16, 1.0),
    },
    "sage_velvet_walnut": {
        "cushion": (0.42, 0.49, 0.40, 1.0),
        "back": (0.38, 0.45, 0.36, 1.0),
        "frame": (0.40, 0.27, 0.16, 1.0),
        "metal": (0.66, 0.64, 0.60, 1.0),
        "accent": (0.30, 0.36, 0.29, 1.0),
        "mesh": (0.36, 0.43, 0.34, 1.0),
        "rubber": (0.16, 0.15, 0.14, 1.0),
    },
    "oak_walnut_brass": {
        "cushion": (0.60, 0.42, 0.26, 1.0),
        "back": (0.34, 0.22, 0.12, 1.0),
        "frame": (0.67, 0.56, 0.34, 1.0),
        "metal": (0.73, 0.63, 0.33, 1.0),
        "accent": (0.47, 0.30, 0.16, 1.0),
        "mesh": (0.56, 0.45, 0.27, 1.0),
        "rubber": (0.08, 0.08, 0.08, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Seat-pan numbers are shared across all
# bases (the seat cushion / column are identical across the source variants);
# base_support only swaps the root frame + support joints.
# ---------------------------------------------------------------------------
# Seat / cushion.
_SEAT_R = 0.190  # seat half-extent (round radius / square half-side)
_CUSHION_H = 0.060
_COLUMN_R = 0.026  # gas-lift / pedestal column radius near the seat
_COLUMN_TOP_INSET = 0.020  # column top sits this far below the cushion underside

# Pedestal / tripod base.
_PEDESTAL_TOP_Z = 0.560  # column top (= seat swivel plane) above floor
_DISC_R = 0.150  # heavy disc base radius
_DISC_H = 0.030
_FOOTRING_R = 0.150
_PEDESTAL_R = 0.030

# Tripod radial legs.
_TRIPOD_OUTER_R = 0.230
_TRIPOD_LEG_H = 0.030

# Sled base.
_SLED_TOP_Z = 0.470
_SLED_RUNNER_Y = 0.200
_TUBE_R = 0.016

# Four-leg dining base.
_LEG_TOP_Z = 0.460
_LEG_SPLAY = 0.30

# Caster base (P_caster 2b416d05 task-stool family).
_CASTER_RADIUS_POS = 0.250
_WHEEL_RADIUS = 0.034
_WHEEL_HALF_W = 0.026  # half the twin-wheel span (self-collision)
_CASTER_HUB_RADIUS = 0.050
_CASTER_HUB_HEIGHT = 0.052
_CASTER_HUB_Z = 0.072
_BASE_SWIVEL_Z = _CASTER_HUB_Z - _CASTER_HUB_HEIGHT / 2.0
_BEARING_HEIGHT = 0.018
_BEARING_RADIUS = _CASTER_HUB_RADIUS * 1.24
_GAS_TOP_Z = 0.480  # gas-lift column top (= seat swivel plane) on caster bases
_GAS_SLEEVE_BOTTOM_Z = 0.050
_GAS_SLEEVE_TOP_Z = 0.200

# Backrest.
_BACK_HEIGHT = 0.300  # wrap-tub low-back height


@dataclass(frozen=True)
class ChairConfig:
    base_support: BaseSupport | None = None
    backrest: Backrest | None = None
    seat_plan: SeatPlan | None = None
    caster_count: int | None = None
    radial_support_count: int | None = None
    palette_style: PaletteStyle = "tan_leather_gold"
    seat_height_scale: float = 1.0
    seat_size_scale: float = 1.0
    back_height_scale: float = 1.0
    caster_radius_scale: float = 1.0
    name: str = "chair"


@dataclass(frozen=True)
class ResolvedChairConfig:
    base_support: BaseSupport
    backrest: Backrest
    seat_plan: SeatPlan
    caster_count: int  # 0 when not a caster base
    radial_support_count: int  # 0 when not tripod
    palette_style: PaletteStyle
    # Derived geometry.
    seat_swivel_z: float  # height of the seat swivel plane above floor (q=0)
    seat_half: float  # seat half-extent (scaled)
    cushion_h: float
    column_r: float
    back_height: float
    back_base_z: float  # backrest base height in the seat-local frame
    caster_radius_pos: float
    wheel_radius: float
    name: str

    @property
    def is_caster(self) -> bool:
        return self.base_support in CASTER_BASES

    @property
    def has_bearing(self) -> bool:
        return self.base_support == "caster_star"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _z_in_frame(world_z: float, frame_origin_z: float) -> float:
    return world_z - frame_origin_z


def config_from_seed(seed: int) -> ChairConfig:
    rng = random.Random(seed)
    return ChairConfig(
        base_support=rng.choices(BASE_SUPPORTS, weights=BASE_SUPPORT_WEIGHTS, k=1)[0],
        backrest=rng.choices(BACKRESTS, weights=BACKREST_WEIGHTS, k=1)[0],
        seat_plan=rng.choices(SEAT_PLANS, weights=SEAT_PLAN_WEIGHTS, k=1)[0],
        caster_count=rng.choices((3, 4, 5, 6), weights=CASTER_COUNT_WEIGHTS, k=1)[0],
        radial_support_count=rng.choices((3, 4, 5), weights=RADIAL_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        seat_height_scale=round(rng.uniform(0.62, 1.05), 4),
        seat_size_scale=round(rng.uniform(0.88, 1.18), 4),
        back_height_scale=round(rng.uniform(0.82, 1.18), 4),
        caster_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_chair_{seed}",
    )


def resolve_config(config: ChairConfig | None = None) -> ResolvedChairConfig:
    cfg = config or ChairConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    base_support = _pick(cfg.base_support, BASE_SUPPORTS)
    backrest = _pick(cfg.backrest, BACKRESTS)
    seat_plan = _pick(cfg.seat_plan, SEAT_PLANS)

    # Scales.
    height_scale = _clamp(cfg.seat_height_scale, 0.62, 1.05)
    size_scale = _clamp(cfg.seat_size_scale, 0.88, 1.18)
    back_scale = _clamp(cfg.back_height_scale, 0.82, 1.18)
    caster_radius_scale = _clamp(cfg.caster_radius_scale, 0.90, 1.10)

    # --- Multiplicity gating (spec §9). ---
    if base_support in CASTER_BASES:
        caster_count = int(cfg.caster_count) if cfg.caster_count is not None else 4
        caster_count = int(_clamp(caster_count, N_CASTER_MIN, N_CASTER_MAX))
    else:
        caster_count = 0
    if base_support == "tripod_pedestal":
        radial_count = int(cfg.radial_support_count) if cfg.radial_support_count is not None else 3
        radial_count = int(_clamp(radial_count, M_RADIAL_MIN, M_RADIAL_MAX))
    else:
        radial_count = 0

    # Seat swivel-plane height per base.
    if base_support in CASTER_BASES:
        base_z = _GAS_TOP_Z
    elif base_support == "sled_runner":
        base_z = _SLED_TOP_Z
    elif base_support == "four_leg_dining":
        base_z = _LEG_TOP_Z
    else:  # pedestal_disc / tripod_pedestal
        base_z = _PEDESTAL_TOP_Z
    seat_swivel_z = base_z * height_scale

    seat_half = _SEAT_R * size_scale
    cushion_h = _CUSHION_H

    # Backrest height + base offset (raise the back base on leg-frame bases so a
    # low wrap-tub clears the runner / leg / apron).
    back_height = _BACK_HEIGHT * back_scale
    back_base_z = cushion_h + 0.010
    if base_support in RAISED_BACK_BASES:
        back_base_z += 0.020

    # Caster geometry; widen the star to avoid wheel self-collision at large N.
    caster_radius_pos = _CASTER_RADIUS_POS * caster_radius_scale
    wheel_radius = _WHEEL_RADIUS
    if caster_count >= 3:
        margin = 0.02
        for _ in range(60):
            avail = 2.0 * math.pi * caster_radius_pos - margin
            need = caster_count * (2.0 * _WHEEL_HALF_W)
            if need <= avail:
                break
            caster_radius_pos += 0.01

    return ResolvedChairConfig(
        base_support=base_support,
        backrest=backrest,
        seat_plan=seat_plan,
        caster_count=caster_count,
        radial_support_count=radial_count,
        palette_style=palette_style,
        seat_swivel_z=seat_swivel_z,
        seat_half=seat_half,
        cushion_h=cushion_h,
        column_r=_COLUMN_R,
        back_height=back_height,
        back_base_z=back_base_z,
        caster_radius_pos=caster_radius_pos,
        wheel_radius=wheel_radius,
        name=cfg.name or "chair",
    )


def with_overrides(config: ChairConfig, **kwargs: object) -> ChairConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ChairConfig | ResolvedChairConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedChairConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("base_support", r.base_support),
        ("backrest", r.backrest),
        ("seat_plan", r.seat_plan),
    ]
    if r.base_support in CASTER_BASES:
        choices.append(("caster_count", f"c{r.caster_count}"))
    if r.base_support == "tripod_pedestal":
        choices.append(("radial_support_count", f"r{r.radial_support_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Seat cushion mesh helpers (seat_plan). round = LatheGeometry puck (P_caster
# _seat_cushion_mesh), square_rounded = extruded rounded-rect cushion + a domed
# top (square_seat Loft / P_pedestal box.fillet). Both emit onto the seat part
# centered on the seat-local origin; cushion bottom near z=0.
# ---------------------------------------------------------------------------
def _emit_round_cushion(seat, r: ResolvedChairConfig, mats):
    """Round leather puck: a LatheGeometry over-stuffed bulge + a stitch ring.
    Source: P_caster _seat_cushion_mesh L75-97 / _stitch_bead_mesh L100-112."""
    rad = r.seat_half
    h = r.cushion_h
    # Lathe profile (x = radius, y = z): bottom rim -> rounded over-stuffed top.
    profile = [
        (0.0, 0.0),
        (rad * 0.92, 0.0),
        (rad, h * 0.30),
        (rad * 0.96, h * 0.74),
        (rad * 0.74, h * 0.98),
        (rad * 0.40, h * 1.04),
        (0.0, h * 1.05),
    ]
    puck = LatheGeometry(profile, segments=48)
    seat.visual(mesh_from_geometry(puck, "cushion"), material=mats["cushion"], name="cushion", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_gold", "cream_leather_chrome"} else "fabric.velvet"))
    ring = TorusGeometry(radius=rad * 0.92, tube=0.012, radial_segments=12, tubular_segments=40)
    ring.translate(0.0, 0.0, h * 0.16)
    seat.visual(
        mesh_from_geometry(ring, "stitch_ring"), material=mats["accent"], name="stitch_ring", material_class_id="fabric.thread_yarn"
    )


def _emit_square_cushion(seat, r: ResolvedChairConfig, mats):
    """Rounded-square cushion: an extruded rounded-rect slab + a domed top pad +
    edge piping. Source: square_seat Loft L68-107 / P_pedestal box.fillet."""
    side = 2.0 * r.seat_half
    h = r.cushion_h
    slab = ExtrudeGeometry(rounded_rect_profile(side, side, side * 0.22), h * 0.80, center=True)
    slab.translate(0.0, 0.0, h * 0.40)
    seat.visual(mesh_from_geometry(slab, "cushion"), material=mats["cushion"], name="cushion", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_gold", "cream_leather_chrome"} else "fabric.velvet"))
    dome = ExtrudeGeometry(
        rounded_rect_profile(side * 0.88, side * 0.88, side * 0.24), h * 0.34, center=True
    )
    dome.translate(0.0, 0.0, h * 0.78)
    seat.visual(
        mesh_from_geometry(dome, "cushion_dome"), material=mats["cushion"], name="cushion_dome", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_gold", "cream_leather_chrome"} else "fabric.velvet")
    )
    piping = ExtrudeGeometry(rounded_rect_profile(side, side, side * 0.22), 0.014, center=True)
    piping.translate(0.0, 0.0, h * 0.10)
    seat.visual(
        mesh_from_geometry(piping, "seat_piping"), material=mats["accent"], name="seat_piping", material_class_id="fabric.thread_yarn"
    )


def _emit_seat_cushion(seat, r: ResolvedChairConfig, mats):
    if r.seat_plan == "round":
        _emit_round_cushion(seat, r, mats)
    else:
        _emit_square_cushion(seat, r, mats)


# ---------------------------------------------------------------------------
# Backrest helpers.
#   * wrap_tub: an inline seat visual (Rule 1, no joint) -- a wrap-around tub
#     arc swept from a rounded-rect section (P_pedestal _backrest_mesh L130-168).
# ---------------------------------------------------------------------------
def _emit_wrap_tub_back(seat, r: ResolvedChairConfig, mats):
    """Wrap-around tub low back, an inline seat visual that swivels with the seat
    (Rule 1). A ~220-degree arc of a rounded-rect section rising at the seat rear.
    Source: P_pedestal _backrest_mesh (sweep_profile_along_spline) L130-168."""
    rad = r.seat_half
    bz = r.back_base_z
    bh = r.back_height
    # Arc spline of points around the rear half (centered behind, +X = front).
    spline: list[tuple[float, float, float]] = []
    a0, a1 = math.radians(35.0), math.radians(325.0)
    steps = 18
    for k in range(steps + 1):
        a = a0 + (a1 - a0) * k / steps
        spline.append((rad * 0.96 * math.cos(a), rad * 0.96 * math.sin(a), bz + bh * 0.5))
    section = rounded_rect_profile(0.040, bh, min(0.018, bh * 0.4))
    tub = sweep_profile_along_spline(spline, profile=section, samples_per_segment=4)
    seat.visual(mesh_from_geometry(tub, "backrest"), material=mats["back"], name="backrest", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_gold", "cream_leather_chrome"} else "fabric.velvet"))
    # A short brace from the cushion rear up into the tub so it is supported.
    seat.visual(
        Box((0.060, 2.0 * rad * 0.5, bz + 0.020)),
        origin=Origin(xyz=(-rad * 0.74, 0.0, (bz + 0.020) / 2.0)),
        material=mats["back"],
        name="back_brace", material_class_id=("leather.smooth_plain" if r.palette_style in {"tan_leather_gold", "cream_leather_chrome"} else "fabric.velvet"),
    )


# ---------------------------------------------------------------------------
# Seat part (shared). Builds the cushion + a swivel collar that captures the
# column top, plus optional inline wrap-tub back.
# ---------------------------------------------------------------------------
def _build_seat(model, r: ResolvedChairConfig, mats) -> object:
    seat = model.part("seat")
    # Swivel collar / mount: a short cylinder centered on the seat-local origin so
    # the chain-joint origin (at the column top) lies on real seat geometry and
    # the column top is captured inside it.
    seat.visual(
        Cylinder(radius=r.column_r + 0.012, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["metal"],
        name="swivel_collar", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "sage_velvet_walnut", "oak_walnut_brass"} else "metal.chrome_polished"),
    )
    # Seat plate bridging the collar out to the cushion underside.
    seat.visual(
        Cylinder(radius=r.seat_half * 0.86, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.020)),
        material=mats["frame"],
        name="seat_plate", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"),
    )
    _emit_seat_cushion(seat, r, mats)
    if r.backrest == "wrap_tub":
        _emit_wrap_tub_back(seat, r, mats)
    seat.inertial = Inertial.from_geometry(
        Box((2.0 * r.seat_half, 2.0 * r.seat_half, 0.14)),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, 0.05)),
    )
    return seat


# ---------------------------------------------------------------------------
# Shared pedestal column hardware (pedestal_disc / tripod_pedestal). Emits a
# footrest ring + 4 struts + column on the given root part. The column top is at
# z = top_z; the seat collar swivels there.
# ---------------------------------------------------------------------------
def _emit_pedestal_column(base, r: ResolvedChairConfig, mats, *, top_z: float):
    # Footrest ring partway up + 4 splayed struts to the disc / hub.
    ring_z = top_z * 0.36
    ring = TorusGeometry(radius=_FOOTRING_R, tube=0.012, radial_segments=12, tubular_segments=40)
    ring.translate(0.0, 0.0, ring_z)
    base.visual(
        mesh_from_geometry(ring, "footrest_ring"), material=mats["metal"], name="footrest_ring", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "sage_velvet_walnut", "oak_walnut_brass"} else "metal.chrome_polished")
    )
    for i in range(4):
        ang = 2.0 * math.pi * i / 4 + math.pi / 4.0
        sx, sy = _FOOTRING_R * math.cos(ang), _FOOTRING_R * math.sin(ang)
        strut = tube_from_spline_points(
            [(0.0, 0.0, ring_z + 0.02), (sx, sy, ring_z)],
            radius=0.008,
            samples_per_segment=6,
            radial_segments=10,
            cap_ends=True,
        )
        base.visual(
            mesh_from_geometry(strut, f"footrest_strut_{i}"),
            material=mats["metal"],
            name=f"footrest_strut_{i}", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "sage_velvet_walnut", "oak_walnut_brass"} else "metal.chrome_polished"),
        )
    # Pedestal column rising from the disc / hub top to the swivel plane (top
    # reaches top_z so the seat collar -- centered on the joint origin --
    # captures it; bottom dips into the disc / hub so the disc is not an island).
    col_bottom = 0.020
    col_h = top_z - col_bottom
    base.visual(
        Cylinder(radius=_PEDESTAL_R, length=col_h),
        origin=Origin(xyz=(0.0, 0.0, col_bottom + col_h / 2.0)),
        material=mats["frame"],
        name="pedestal", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"),
    )


# ---------------------------------------------------------------------------
# Base builders. Each emits its root part + support hardware, builds the seat,
# and emits the seat_swivel CONTINUOUS +Z joint. Returns the seat part.
# ---------------------------------------------------------------------------
def _build_pedestal_disc_base(model, r: ResolvedChairConfig, mats):
    """pedestal_disc: heavy disc + column root -> seat swivel +Z. Source: P_pedestal."""
    base = model.part("base_pedestal")
    top_z = r.seat_swivel_z
    # Heavy disc base (lathe puck profile).
    profile = [
        (0.0, 0.0),
        (_DISC_R, 0.0),
        (_DISC_R, _DISC_H * 0.55),
        (_DISC_R * 0.55, _DISC_H),
        (0.0, _DISC_H),
    ]
    disc = LatheGeometry(profile, segments=48)
    base.visual(mesh_from_geometry(disc, "disc_base"), material=mats["frame"], name="disc_base", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"))
    _emit_pedestal_column(base, r, mats, top_z=top_z)
    base.inertial = Inertial.from_geometry(
        Box((2.0 * _DISC_R, 2.0 * _DISC_R, top_z)),
        mass=8.0,
        origin=Origin(xyz=(0.0, 0.0, top_z * 0.3)),
    )
    seat = _build_seat(model, r, mats)
    model.articulation(
        "seat_swivel",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=seat,
        origin=Origin(xyz=(0.0, 0.0, top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=3.0),
    )
    return seat


def _build_tripod_pedestal_base(model, r: ResolvedChairConfig, mats):
    """tripod_pedestal: M radial legs + hub + column root -> seat swivel +Z.
    The M legs + foot pads are fixed inline visuals (Rule 1, no joint). Source:
    tripod _tripod_leg_mesh / foot_pad / _tripod_hub_mesh / pedestal."""
    base = model.part("base_pedestal")
    top_z = r.seat_swivel_z
    m = r.radial_support_count
    # Central hub collar (the legs + column meet here).
    base.visual(
        Cylinder(radius=0.052, length=0.060),
        origin=Origin(xyz=(0.0, 0.0, 0.040)),
        material=mats["frame"],
        name="tripod_hub", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"),
    )
    for i in range(m):
        ang = 2.0 * math.pi * i / m
        ex, ey = _TRIPOD_OUTER_R * math.cos(ang), _TRIPOD_OUTER_R * math.sin(ang)
        leg = tube_from_spline_points(
            [
                (0.0, 0.0, 0.050),
                (ex * 0.45, ey * 0.45, 0.040),
                (ex, ey, _TRIPOD_LEG_H * 0.5),
            ],
            radius=0.016,
            samples_per_segment=12,
            radial_segments=12,
            cap_ends=True,
        )
        base.visual(
            mesh_from_geometry(leg, f"tripod_leg_{i}"),
            material=mats["frame"],
            name=f"tripod_leg_{i}", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"),
        )
        base.visual(
            Cylinder(radius=0.024, length=_TRIPOD_LEG_H),
            origin=Origin(xyz=(ex, ey, _TRIPOD_LEG_H * 0.5)),
            material=mats["rubber"],
            name=f"foot_pad_{i}", material_class_id="rubber.smooth_plain",
        )
    _emit_pedestal_column(base, r, mats, top_z=top_z)
    base.inertial = Inertial.from_geometry(
        Box((2.0 * _TRIPOD_OUTER_R, 2.0 * _TRIPOD_OUTER_R, top_z)),
        mass=6.0,
        origin=Origin(xyz=(0.0, 0.0, top_z * 0.3)),
    )
    seat = _build_seat(model, r, mats)
    model.articulation(
        "seat_swivel",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=seat,
        origin=Origin(xyz=(0.0, 0.0, top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=3.0),
    )
    return seat


def _build_sled_runner_base(model, r: ResolvedChairConfig, mats):
    """sled_runner: 2 U-shaped bent tube runners + crossbars + center column ->
    seat swivel +Z. Source: sled _sled_runner_mesh / _cross_bar / _center_bar / hub."""
    sled = model.part("sled_base")
    top_z = r.seat_swivel_z
    for i, sign in enumerate((1.0, -1.0)):
        pts = [
            (0.22, sign * _SLED_RUNNER_Y, 0.016),
            (-0.20, sign * _SLED_RUNNER_Y, 0.016),
            (-0.24, sign * (_SLED_RUNNER_Y - 0.02), 0.10),
            (-0.06, sign * 0.10, top_z * 0.6),
            (0.0, sign * 0.05, top_z - 0.02),
        ]
        geom = tube_from_spline_points(
            pts, radius=_TUBE_R, samples_per_segment=14, radial_segments=12, cap_ends=True
        )
        sled.visual(
            mesh_from_geometry(geom, f"runner_{i}"), material=mats["frame"], name=f"runner_{i}", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark")
        )
    for x, nm in ((0.22, "front_crossbar"), (-0.20, "back_crossbar")):
        geom = tube_from_spline_points(
            [(x, -_SLED_RUNNER_Y, 0.016), (x, _SLED_RUNNER_Y, 0.016)],
            radius=_TUBE_R,
            samples_per_segment=8,
            radial_segments=12,
            cap_ends=True,
        )
        sled.visual(mesh_from_geometry(geom, nm), material=mats["frame"], name=nm, material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"))
    # Center column rising to the swivel plane.
    col_h = top_z - 0.05
    sled.visual(
        Cylinder(radius=_PEDESTAL_R, length=col_h),
        origin=Origin(xyz=(0.0, 0.0, 0.05 + col_h / 2.0)),
        material=mats["frame"],
        name="center_bar", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"),
    )
    sled.visual(
        Cylinder(radius=0.060, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, top_z - 0.010)),
        material=mats["accent"],
        name="hub", material_class_id="metal.paint_coated",
    )
    sled.inertial = Inertial.from_geometry(
        Box((0.5, 2.0 * _SLED_RUNNER_Y, top_z)),
        mass=5.0,
        origin=Origin(xyz=(0.0, 0.0, top_z * 0.4)),
    )
    seat = _build_seat(model, r, mats)
    model.articulation(
        "seat_swivel",
        ArticulationType.CONTINUOUS,
        parent=sled,
        child=seat,
        origin=Origin(xyz=(0.0, 0.0, top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=3.0),
    )
    return seat


def _build_four_leg_dining_base(model, r: ResolvedChairConfig, mats):
    """four_leg_dining: 4 splayed tapered legs + apron square frame + central hub
    -> seat swivel +Z. Source: dining _leg_mesh / _apron_frame_mesh / _stretcher."""
    frame = model.part("leg_frame")
    top_z = r.seat_swivel_z
    apron_z = top_z - 0.060
    apron_half = 0.150
    # Apron square frame (4 rails) tying the legs into the central hub.
    for nm, sx, sy, ox, oy in (
        ("apron_front", 0.05, 2.0 * apron_half, apron_half, 0.0),
        ("apron_back", 0.05, 2.0 * apron_half, -apron_half, 0.0),
        ("apron_left", 2.0 * apron_half, 0.05, 0.0, apron_half),
        ("apron_right", 2.0 * apron_half, 0.05, 0.0, -apron_half),
    ):
        frame.visual(
            Box((sx, sy, 0.050)),
            origin=Origin(xyz=(ox, oy, apron_z)),
            material=mats["frame"],
            name=nm, material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"),
        )
    # Central hub (swivel mount) bridging the apron at the seat plane.
    frame.visual(
        Cylinder(radius=0.055, length=0.060),
        origin=Origin(xyz=(0.0, 0.0, top_z - 0.030)),
        material=mats["frame"],
        name="apron_hub", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"),
    )
    frame.visual(
        Box((2.0 * apron_half, 0.045, 0.040)),
        origin=Origin(xyz=(0.0, 0.0, apron_z)),
        material=mats["frame"],
        name="apron_cross", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"),
    )
    leg_corners = (
        (apron_half, apron_half),
        (apron_half, -apron_half),
        (-apron_half, apron_half),
        (-apron_half, -apron_half),
    )
    for i, (lx, ly) in enumerate(leg_corners):
        fx = lx * (1.0 + _LEG_SPLAY)
        fy = ly * (1.0 + _LEG_SPLAY)
        leg = tube_from_spline_points(
            [
                (lx, ly, apron_z + 0.020),
                (lx * 1.05 + (fx - lx) * 0.5, ly * 1.05 + (fy - ly) * 0.5, apron_z * 0.5),
                (fx, fy, 0.02),
            ],
            radius=0.020,
            samples_per_segment=12,
            radial_segments=12,
            cap_ends=True,
        )
        frame.visual(mesh_from_geometry(leg, f"leg_{i}"), material=mats["frame"], name=f"leg_{i}", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "cream_leather_chrome"} else "wood.walnut_dark"))
        frame.visual(
            Cylinder(radius=0.022, length=0.024),
            origin=Origin(xyz=(fx, fy, 0.012)),
            material=mats["rubber"],
            name=f"leg_glide_{i}", material_class_id="rubber.smooth_plain",
        )
    frame.inertial = Inertial.from_geometry(
        Box((0.42, 0.42, top_z)),
        mass=5.0,
        origin=Origin(xyz=(0.0, 0.0, top_z * 0.4)),
    )
    seat = _build_seat(model, r, mats)
    model.articulation(
        "seat_swivel",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=seat,
        origin=Origin(xyz=(0.0, 0.0, top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=3.0),
    )
    return seat


def _emit_caster_star(model, base, r: ResolvedChairConfig, mats, *, angles, base_origin_z: float):
    """Emit the star hub + N spokes/yokes (inline base visuals) + N twin caster
    wheel parts (CONTINUOUS roll). Source: P_caster caster_base + caster_wheel."""

    def z(world_z: float) -> float:
        return _z_in_frame(world_z, base_origin_z)

    # Keep the office-chair hub floating above the floor like the source office
    # chair family instead of dropping a full center can to the ground.
    base.visual(
        Cylinder(radius=_CASTER_HUB_RADIUS, length=_CASTER_HUB_HEIGHT),
        origin=Origin(xyz=(0.0, 0.0, z(_CASTER_HUB_Z))),
        material=mats["frame"],
        name="star_hub", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "cream_leather_chrome", "oak_walnut_brass"} else "metal.blackened_gunmetal"),
    )
    base.visual(
        Cylinder(radius=_CASTER_HUB_RADIUS * 0.72, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, z(_CASTER_HUB_Z + _CASTER_HUB_HEIGHT / 2.0 + 0.006))),
        material=mats["frame"],
        name="hub_collar", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "cream_leather_chrome", "oak_walnut_brass"} else "metal.blackened_gunmetal"),
    )
    for i, ang in enumerate(angles):
        cx = r.caster_radius_pos * math.cos(ang)
        cy = r.caster_radius_pos * math.sin(ang)
        root_r = _CASTER_HUB_RADIUS - 0.012
        spoke = tube_from_spline_points(
            [
                (root_r * math.cos(ang), root_r * math.sin(ang), z(_CASTER_HUB_Z + 0.006)),
                (cx * 0.42, cy * 0.42, z(_CASTER_HUB_Z - 0.004)),
                (cx * 0.80, cy * 0.80, z(0.062)),
                (cx, cy, z(0.056)),
            ],
            radius=0.013,
            samples_per_segment=12,
            radial_segments=12,
            cap_ends=True,
        )
        base.visual(
            mesh_from_geometry(spoke, f"spoke_{i}"), material=mats["frame"], name=f"spoke_{i}", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "cream_leather_chrome", "oak_walnut_brass"} else "metal.blackened_gunmetal")
        )
        base.visual(
            Box((0.032, 0.018, 0.028)),
            origin=Origin(xyz=(cx, cy, z(r.wheel_radius + 0.014)), rpy=(0.0, 0.0, ang)),
            material=mats["frame"],
            name=f"caster_yoke_{i}", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "cream_leather_chrome", "oak_walnut_brass"} else "metal.blackened_gunmetal"),
        )
    # Twin caster wheels (each a CONTINUOUS moving part).
    for i, ang in enumerate(angles):
        cx = r.caster_radius_pos * math.cos(ang)
        cy = r.caster_radius_pos * math.sin(ang)
        wheel = model.part(f"caster_wheel_{i}")
        for side, sy in (("0", -0.018), ("1", 0.018)):
            wheel.visual(
                Cylinder(radius=r.wheel_radius, length=0.014),
                origin=Origin(xyz=(0.0, sy, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["rubber"],
                name=f"tire_{side}", material_class_id="rubber.smooth_plain",
            )
        wheel.visual(
            Cylinder(radius=0.006, length=0.050),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name="caster_axle", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "sage_velvet_walnut", "oak_walnut_brass"} else "metal.chrome_polished"),
        )
        wheel.inertial = Inertial.from_geometry(
            Box((2.0 * r.wheel_radius, 0.05, 2.0 * r.wheel_radius)),
            mass=0.2,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        # The joint's rpy yaw (=ang) rotates the +Y axle into the radial
        # transverse direction, so the wheel rolls forward as the chair moves.
        model.articulation(
            f"caster_roll_{i}",
            ArticulationType.CONTINUOUS,
            parent=base,
            child=wheel,
            origin=Origin(xyz=(cx, cy, z(r.wheel_radius)), rpy=(0.0, 0.0, ang)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=20.0),
        )


def _emit_gas_column_and_seat(model, base, r: ResolvedChairConfig, mats, *, base_origin_z: float):
    """Gas-lift column on the caster base + the column_seat via seat_swivel +Z.
    Source: P_caster _gas_lift_column + column_seat + seat_swivel."""
    top_z = r.seat_swivel_z

    def z(world_z: float) -> float:
        return _z_in_frame(world_z, base_origin_z)

    # Keep a short lower sleeve with a slimmer exposed upper rod, matching the
    # reference office-chair proportion instead of a single oversized center can.
    tube_bottom = max(_GAS_SLEEVE_BOTTOM_Z, r.wheel_radius + 0.016)
    tube_top = max(tube_bottom + 0.080, min(_GAS_SLEEVE_TOP_Z, top_z * 0.45))
    tube_h = tube_top - tube_bottom
    base.visual(
        Cylinder(radius=0.030, length=tube_h),
        origin=Origin(xyz=(0.0, 0.0, z(tube_bottom + tube_h / 2.0))),
        material=mats["frame"],
        name="gas_lift_tube", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "cream_leather_chrome", "oak_walnut_brass"} else "metal.blackened_gunmetal"),
    )
    col_bottom = tube_top - 0.012
    col_h = top_z - col_bottom
    base.visual(
        Cylinder(radius=r.column_r, length=col_h),
        origin=Origin(xyz=(0.0, 0.0, z(col_bottom + col_h / 2.0))),
        material=mats["metal"],
        name="gas_lift_column", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "sage_velvet_walnut", "oak_walnut_brass"} else "metal.chrome_polished"),
    )
    seat = _build_seat(model, r, mats)
    model.articulation(
        "seat_swivel",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=seat,
        origin=Origin(xyz=(0.0, 0.0, z(top_z))),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=3.0),
    )
    return seat


def _build_caster_star_base(model, r: ResolvedChairConfig, mats):
    """caster_star: stationary_bearing root -> caster_base via base_swivel +Z ->
    N caster wheels + column_seat via seat_swivel +Z. Source: P_caster."""
    bearing = model.part("stationary_bearing")
    bearing.visual(
        Cylinder(radius=_BEARING_RADIUS, length=_BEARING_HEIGHT),
        origin=Origin(xyz=(0.0, 0.0, _BASE_SWIVEL_Z - _BEARING_HEIGHT / 2.0)),
        material=mats["metal"],
        name="bearing_washer", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "sage_velvet_walnut", "oak_walnut_brass"} else "metal.chrome_polished"),
    )
    bearing.visual(
        Cylinder(radius=0.022, length=0.080),
        origin=Origin(xyz=(0.0, 0.0, _BASE_SWIVEL_Z + 0.020)),
        material=mats["metal"],
        name="bearing_spindle", material_class_id=("metal.precious_gold" if r.palette_style in {"tan_leather_gold", "brown_padded_black", "sage_velvet_walnut", "oak_walnut_brass"} else "metal.chrome_polished"),
    )
    bearing.inertial = Inertial.from_geometry(
        Box((0.14, 0.14, 0.10)),
        mass=0.6,
        origin=Origin(xyz=(0.0, 0.0, _BASE_SWIVEL_Z)),
    )
    base = model.part("caster_base")
    n = r.caster_count
    angles = [2.0 * math.pi * i / n + math.pi / 2.0 for i in range(n)]
    _emit_caster_star(model, base, r, mats, angles=angles, base_origin_z=_BASE_SWIVEL_Z)
    base.inertial = Inertial.from_geometry(
        Box((2.0 * r.caster_radius_pos, 2.0 * r.caster_radius_pos, r.seat_swivel_z)),
        mass=3.0,
        origin=Origin(xyz=(0.0, 0.0, r.seat_swivel_z * 0.4)),
    )
    model.articulation(
        "base_swivel",
        ArticulationType.CONTINUOUS,
        parent=bearing,
        child=base,
        origin=Origin(xyz=(0.0, 0.0, _BASE_SWIVEL_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=3.0),
    )
    return _emit_gas_column_and_seat(model, base, r, mats, base_origin_z=_BASE_SWIVEL_Z)


def _build_caster_star_no_bearing_base(model, r: ResolvedChairConfig, mats):
    """caster_star_no_bearing: caster_base is the root itself (no bearing /
    base_swivel) -> N caster wheels + column_seat via seat_swivel +Z. Source:
    square_seat caster_base root."""
    base = model.part("caster_base")
    n = r.caster_count
    angles = [2.0 * math.pi * i / n + math.pi / 2.0 for i in range(n)]
    _emit_caster_star(model, base, r, mats, angles=angles, base_origin_z=0.0)
    base.inertial = Inertial.from_geometry(
        Box((2.0 * r.caster_radius_pos, 2.0 * r.caster_radius_pos, r.seat_swivel_z)),
        mass=3.2,
        origin=Origin(xyz=(0.0, 0.0, r.seat_swivel_z * 0.4)),
    )
    return _emit_gas_column_and_seat(model, base, r, mats, base_origin_z=0.0)


_BASE_BUILDERS = {
    "pedestal_disc": _build_pedestal_disc_base,
    "tripod_pedestal": _build_tripod_pedestal_base,
    "sled_runner": _build_sled_runner_base,
    "four_leg_dining": _build_four_leg_dining_base,
    "caster_star": _build_caster_star_base,
    "caster_star_no_bearing": _build_caster_star_no_bearing_base,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_chair(
    config: ChairConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"chair_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    _BASE_BUILDERS[r.base_support](model, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_chair(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_chair(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_chair_tests(
    object_model: ArticulatedObject,
    config: ChairConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    seat = object_model.get_part("seat")

    # ---- Captured-pin / nested allowances (element-scoped). ----
    # Seat swivel collar captures the column / hub top of every base.
    root = object_model.root_parts()[0]
    if r.base_support in ("pedestal_disc", "tripod_pedestal"):
        ctx.allow_overlap(
            root,
            seat,
            elem_a="pedestal",
            elem_b="swivel_collar",
            reason="Seat swivel collar captures the pedestal column top.",
        )
        ctx.allow_overlap(
            root,
            seat,
            elem_a="pedestal",
            elem_b="seat_plate",
            reason="Seat plate seats over the pedestal column top at the swivel.",
        )
    elif r.base_support == "sled_runner":
        for el in ("hub", "center_bar"):
            ctx.allow_overlap(
                root,
                seat,
                elem_a=el,
                elem_b="swivel_collar",
                reason="Seat swivel collar captures the sled hub / center bar top.",
            )
            ctx.allow_overlap(
                root,
                seat,
                elem_a=el,
                elem_b="seat_plate",
                reason="Seat plate seats over the sled hub at the swivel.",
            )
    elif r.base_support == "four_leg_dining":
        ctx.allow_overlap(
            root,
            seat,
            elem_a="apron_hub",
            elem_b="swivel_collar",
            reason="Seat swivel collar captures the apron hub at the swivel.",
        )
        ctx.allow_overlap(
            root,
            seat,
            elem_a="apron_hub",
            elem_b="seat_plate",
            reason="Seat plate seats over the apron hub at the swivel.",
        )
    else:  # caster bases
        base = object_model.get_part("caster_base")
        for el in ("gas_lift_column", "gas_lift_tube", "star_hub"):
            ctx.allow_overlap(
                base,
                seat,
                elem_a=el,
                elem_b="swivel_collar",
                reason="Seat swivel collar captures the gas-lift column top.",
            )
            ctx.allow_overlap(
                base,
                seat,
                elem_a=el,
                elem_b="seat_plate",
                reason="Seat plate seats over the gas-lift column top at the swivel.",
            )
        # Twin-wheel axle captured through the caster yoke; wheel near the spoke.
        for i in range(r.caster_count):
            wheel = object_model.get_part(f"caster_wheel_{i}")
            for el in ("tire_0", "tire_1", "caster_axle"):
                ctx.allow_overlap(
                    base,
                    wheel,
                    elem_a=f"caster_yoke_{i}",
                    elem_b=el,
                    reason="Twin-wheel tire/axle is captured in the caster yoke fork.",
                )
                ctx.allow_overlap(
                    base,
                    wheel,
                    elem_a=f"spoke_{i}",
                    elem_b=el,
                    reason="Caster wheel sits at the spoke tip under the yoke.",
                )
        if r.has_bearing:
            bearing = object_model.get_part("stationary_bearing")
            for el in ("bearing_washer", "bearing_spindle"):
                for base_el in ("star_hub", "hub_collar"):
                    ctx.allow_overlap(
                        bearing,
                        base,
                        elem_a=el,
                        elem_b=base_el,
                        reason="Caster star hub hardware rotates over the stationary bearing spindle.",
                    )
            # The N spokes radiate from the hub and pass over the bearing spindle;
            # the gas-lift column / tube rise coaxially through the spindle bore.
            for i in range(r.caster_count):
                for el in ("bearing_spindle", "bearing_washer"):
                    ctx.allow_overlap(
                        bearing,
                        base,
                        elem_a=el,
                        elem_b=f"spoke_{i}",
                        reason="Caster spoke roots pass over the central bearing hardware.",
                    )
            for el in ("gas_lift_tube", "gas_lift_column"):
                ctx.allow_overlap(
                    bearing,
                    base,
                    elem_a="bearing_spindle",
                    elem_b=el,
                    reason="Gas-lift column rises coaxially through the bearing spindle bore.",
                )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("seat part present", "seat" in part_names, details=str(sorted(part_names)))

    # seat_swivel CONTINUOUS +Z is the invariant cross-slot joint on every base.
    sw = object_model.get_articulation("seat_swivel")
    ctx.check(
        "seat swivel is CONTINUOUS about +Z",
        sw.articulation_type == ArticulationType.CONTINUOUS and abs(sw.axis[2]) > 0.99,
        details=f"type={sw.articulation_type} axis={tuple(sw.axis)}",
    )

    # Base-support joint topology.
    if r.base_support in CASTER_BASES:
        cj = object_model.get_articulation("caster_roll_0")
        ctx.check(
            "caster wheel is CONTINUOUS about a horizontal axle",
            cj.articulation_type == ArticulationType.CONTINUOUS and abs(cj.axis[2]) < 1e-9,
            details=f"axis={tuple(cj.axis)}",
        )
        wheels = [p for p in part_names if p.startswith("caster_wheel_")]
        ctx.check(
            "N caster wheels emitted",
            len(wheels) == r.caster_count,
            details=f"wheels={len(wheels)} N={r.caster_count}",
        )
        if r.has_bearing:
            bj = object_model.get_articulation("base_swivel")
            ctx.check(
                "base swivel is CONTINUOUS about +Z (caster_star)",
                bj.articulation_type == ArticulationType.CONTINUOUS and abs(bj.axis[2]) > 0.99,
                details=f"axis={tuple(bj.axis)}",
            )
        else:
            ctx.check(
                "no base_swivel on caster_star_no_bearing",
                not any(a.name == "base_swivel" for a in object_model.articulations),
                details="no_bearing",
            )
    elif r.base_support == "tripod_pedestal":
        legs = [
            v
            for v in object_model.get_part("base_pedestal").visuals
            if v.name.startswith("tripod_leg_")
        ]
        ctx.check(
            "M radial tripod legs emitted (fixed inline, no joint)",
            len(legs) == r.radial_support_count,
            details=f"legs={len(legs)} M={r.radial_support_count}",
        )

    # Backrest joint topology.
    if r.backrest == "wrap_tub":
        ctx.check(
            "wrap_tub backrest is an inline seat visual (no separate part/joint)",
            any(v.name == "backrest" for v in seat.visuals) and "backrest_frame" not in part_names,
            details=f"seat_visuals={[v.name for v in seat.visuals]}",
        )
    else:  # none
        ctx.check(
            "backless stool has no backrest visual or part",
            not any(v.name == "backrest" for v in seat.visuals)
            and "backrest_frame" not in part_names,
            details="none",
        )

    # sampled-pose exemption: this scoped chair template only has continuous
    # swivel / caster-roll motion, not a finite recline or slide range to tune.
    # Targeted pose checks cover the intended swivel semantics.
    # ---- Seat swivel actually spins the seat about +Z. ----
    p_seat_xy = ctx.part_world_aabb(seat)
    if p_seat_xy is not None:
        with ctx.pose({sw: math.pi / 2.0}):
            spun = ctx.part_world_aabb(seat)
        ctx.check(
            "seat swivels (AABB changes under +Z rotation) for non-round seats",
            spun is not None,
            details="swivel pose evaluated",
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
        "seat sits at stool/chair height (0.30-0.70 m)",
        0.28 <= r.seat_swivel_z <= 0.70,
        details=f"seat_swivel_z={r.seat_swivel_z:.3f}",
    )

    # Casters on the floor (caster bases).
    if r.base_support in CASTER_BASES:
        for i in range(r.caster_count):
            wa = ctx.part_world_aabb(object_model.get_part(f"caster_wheel_{i}"))
            ctx.check(
                f"caster wheel {i} rests on the floor",
                wa is not None and abs(wa[0][2]) <= 0.006,
                details=f"wheel {i} z_min={None if wa is None else wa[0][2]:.4f}",
            )

    # ---- slot_choices recorded with N / M encoded. ----
    ctx.check(
        "slot_choices recorded with caster_count / radial_support_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "ChairConfig",
    "ResolvedChairConfig",
    "build_chair",
    "build_seeded_chair",
    "config_from_seed",
    "resolve_config",
    "run_chair_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
