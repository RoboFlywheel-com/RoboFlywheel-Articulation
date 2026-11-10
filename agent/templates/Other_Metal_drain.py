# SPDX-License-Identifier: Apache-2.0

"""Metal drain (square / round / hex stainless-steel bathroom floor drain) modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_Metal_drain.md`` and the
``picture/Other/Metal drain`` 5-star sample pool (6 synced fork variants; the
source-map square parent was never synced, so the square / pinwheel / twist_lock
baselines are recovered from the square-body fork variants as the spec documents).

"Metal drain" here = a **bathroom floor drain**: a flat polished outer flange
(square / round / hex footprint, ~0.12 m, ~0.005 m thick, beveled top edges)
seated on a shallow open-bottomed tapered drain cup with a dark cavity liner,
the flange's circular opening (~0.095 m) holding a round perforated grate disc
with a removal / opening mechanism.

Structure (pattern = ``mixed``): a single root ``drain_body`` part (footprint
mesh chosen by ``flange_shape``), with three named module axes plus one
multiplicity axis:

  * ``flange_shape`` (3): square / round_circular / hexagonal — the shared
    footprint of the flange + cup + liner mesh. A mesh-helper dimension; it does
    not add a joint (the central opening is always circular, so the grate /
    mechanism are orthogonal to the footprint).
  * ``grate_pattern`` (3): pinwheel_slots / concentric_rings / square_grid_holes
    — the cut pattern inside the grate disc's ``_grate_solid``. The disc is a
    single part; the pattern adds no joint.
  * ``grate_mechanism`` (3): the ONLY real joint-topology axis —
    twist_lock_lift_out (PRISMATIC +Z lift + REVOLUTE +Z twist, 3 parts / 2
    joints / depth 2), hinged_flip_grate (single REVOLUTE +X flip, 2 parts / 1
    joint / depth 1, the seat ring fuses into the body), popup_center_plug
    (twist+lift baseline + a center plug PRISMATIC +Z, 4 parts / 3 joints /
    depth 3).
  * ``perf_count`` (bucket {sparse, medium, dense}): perforation-unit
    multiplicity inside the grate disc (pinwheel slots-per-group, concentric
    ring count, grid hole count). Encoded into the slot_choice tuple as
    ``("perf", f"n{bucket}")``; continuous N is nudged by ``perf_density_scale``
    within the bucket.

All seat / lip / bore / hinge-pin contacts are captured-seat / captured-bore /
captured-pin geometry, so the mechanism joints omit ``MatingContract``
(grandfathered) and are guarded by the flat articulation-origin baseline +
element-scoped ``allow_overlap`` (mirroring each source record's run_tests
allow_overlap block).

Compatibility gating (resolve_config, spec §9):
  * The three main axes are near-orthogonal (opening always circular, grate
    always circular, mechanism independent of footprint / pattern) — no mutual
    exclusion gate.
  * popup_center_plug needs a clear center web for the plug bore: concentric_rings
    raises its inner-ring start radius above the bore, and square_grid_holes drops
    the central grid point, so the plug stem never collides with a perforation.
  * dense perf is clamped to each pattern's field capacity.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

FlangeShape = Literal["square", "round_circular", "hexagonal"]
GratePattern = Literal["pinwheel_slots", "concentric_rings", "square_grid_holes"]
GrateMechanism = Literal["twist_lock_lift_out", "hinged_flip_grate", "popup_center_plug"]
PerfBucket = Literal["sparse", "medium", "dense"]
PaletteStyle = Literal[
    "brushed_stainless",
    "polished_chrome",
    "matte_black",
    "antique_brass",
    "oil_rubbed_bronze",
]

FLANGE_SHAPES: tuple[FlangeShape, ...] = ("square", "round_circular", "hexagonal")
GRATE_PATTERNS: tuple[GratePattern, ...] = (
    "pinwheel_slots",
    "concentric_rings",
    "square_grid_holes",
)
GRATE_MECHANISMS: tuple[GrateMechanism, ...] = (
    "twist_lock_lift_out",
    "hinged_flip_grate",
    "popup_center_plug",
)
PERF_BUCKETS: tuple[PerfBucket, ...] = ("sparse", "medium", "dense")
# Bucket weights: sparse high-frequency, dense long tail (spec §8).
PERF_BUCKET_WEIGHTS = (0.45, 0.35, 0.20)

PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_stainless",
    "polished_chrome",
    "matte_black",
    "antique_brass",
    "oil_rubbed_bronze",
)

# Per-pattern perforation multiplicity by bucket. The cut multiplicity is the
# topology dimension; continuous N within a bucket is nudged by density scale.
#   pinwheel: SLOTS_PER_GROUP (N_GROUPS=4 fixed) -> total slots = 4 * spg.
#   concentric: N_RINGS (N_BRIDGES=4 fixed).
#   grid: implicit via GRID_PITCH; bucket sets the pitch (sparse=large pitch).
_PINWHEEL_SPG = {"sparse": 3, "medium": 5, "dense": 8}
_RING_COUNT = {"sparse": 3, "medium": 5, "dense": 8}
_GRID_PITCH = {"sparse": 0.0120, "medium": 0.0090, "dense": 0.0070}

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_stainless": {
        "polished": (0.81, 0.82, 0.84, 1.0),
        "brushed": (0.74, 0.75, 0.77, 1.0),
        "accent": (0.66, 0.67, 0.70, 1.0),
        "cavity": (0.05, 0.05, 0.06, 1.0),
    },
    "polished_chrome": {
        "polished": (0.90, 0.91, 0.93, 1.0),
        "brushed": (0.80, 0.82, 0.85, 1.0),
        "accent": (0.72, 0.74, 0.78, 1.0),
        "cavity": (0.04, 0.04, 0.05, 1.0),
    },
    "matte_black": {
        "polished": (0.16, 0.16, 0.17, 1.0),
        "brushed": (0.11, 0.11, 0.12, 1.0),
        "accent": (0.22, 0.22, 0.24, 1.0),
        "cavity": (0.02, 0.02, 0.02, 1.0),
    },
    "antique_brass": {
        "polished": (0.72, 0.58, 0.30, 1.0),
        "brushed": (0.62, 0.49, 0.24, 1.0),
        "accent": (0.80, 0.66, 0.36, 1.0),
        "cavity": (0.07, 0.05, 0.03, 1.0),
    },
    "oil_rubbed_bronze": {
        "polished": (0.32, 0.24, 0.18, 1.0),
        "brushed": (0.25, 0.19, 0.14, 1.0),
        "accent": (0.42, 0.32, 0.24, 1.0),
        "cavity": (0.04, 0.03, 0.02, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters); baselines from the synced fork variants
# (round b8d32e6f / square+concentric d68de668 / hinged 3cfbbefa / popup
# a0a6918d / hex 4b1ebd24 / grid e214b2de). The flange is centered on z; the
# cup mouth sits on the ground at z=0 and the flange top is at TOTAL_H.
# ---------------------------------------------------------------------------
_TOTAL_H = 0.030  # overall height (cup bottom z=0 -> flange top)
_FLANGE_HALF = 0.060  # half footprint (square half-side / round radius / hex inscribed)
_FLANGE_T = 0.005  # flange plate thickness
_FLANGE_CHAMFER = 0.0015
_HOLE_R = 0.0476  # circular flange opening radius (~0.095 m dia)

_CUP_TOP_HALF = 0.055  # cup outer half at the top (under the flange)
_CUP_BOT_HALF = 0.0425  # cup outer half at the open bottom
_CUP_WALL = 0.005
_SEAT_PLATE_T = 0.0035
_SEAT_PLATE_HALF = 0.053
_SEAT_HOLE_R = 0.034
_HUB_R = 0.004  # central strainer-support boss radius (lands grate joint origin)
_RIB_W = 0.0025  # spider rib width connecting the hub to the seat plate

_LINER_WALL = 0.0015
_LINER_Z0 = 0.002
_LINER_EMBED = 0.0005

# Grate seat ring (twist_lock / popup).
_RIM_OUT_R = 0.0472
_RIM_IN_R = 0.0420
_RIM_H = 0.0053
_LIP_IN_R = 0.0360
_LIP_H = 0.0015
_RIM_SEAT_EMBED = 0.0003

_GRATE_R = 0.0415  # grate disc radius
_GRATE_T = 0.004

# Pinwheel pattern field.
_FIELD_R = 0.0335
_N_GROUPS = 4
_SLOT_W = 0.004
_SLOT_PITCH = 0.0062
_SLOT_Y0 = 0.0048
_CENTER_GAP = 0.0022

# Concentric pattern.
_RING_WIDTH = 0.003
_RING_GAP = 0.003
_RING_R0 = 0.007
_N_BRIDGES = 4
_BRIDGE_W = 0.002
_BRIDGE_INNER_R = 0.004

# Grid pattern.
_GRID_FIELD_R = 0.034
_GRID_HOLE_R = 0.003

# Hinge (hinged_flip) hardware.
_HINGE_R = 0.002
_HINGE_LEN = 0.030
_KNUCKLE_R = _HINGE_R + 0.001
_KNUCKLE_LEN = 0.018
_BRACKET_W = 0.006
_BRACKET_DROP = 0.005
_BRACKET_T = 0.004
_FLIP_UPPER = 2.0

# Popup plug.
_PLUG_BORE_R = 0.003
_PLUG_CAP_R = 0.007
_PLUG_CAP_T = 0.003
_PLUG_STEM_R = 0.0025
_PLUG_STEM_H = 0.013
_PLUG_TRAVEL = 0.008

_LIFT_TRAVEL = 0.030
_TWIST_LIMIT = math.pi / 2.0

_HEX_COS30 = math.cos(math.pi / 6.0)


@dataclass(frozen=True)
class MetalDrainConfig:
    flange_shape: FlangeShape | None = None
    grate_pattern: GratePattern | None = None
    grate_mechanism: GrateMechanism | None = None
    perf_bucket: PerfBucket | None = None
    palette_style: PaletteStyle = "brushed_stainless"
    flange_size_scale: float = 1.0
    cup_depth_scale: float = 1.0
    grate_open_ratio: float = 0.79
    perf_density_scale: float = 1.0
    flip_angle_scale: float = 1.0
    twist_range_scale: float = 1.0
    plug_travel_scale: float = 1.0
    name: str = "metal_drain"


@dataclass(frozen=True)
class ResolvedMetalDrainConfig:
    flange_shape: FlangeShape
    grate_pattern: GratePattern
    grate_mechanism: GrateMechanism
    perf_bucket: PerfBucket
    palette_style: PaletteStyle
    # Concrete geometry (scaled).
    total_h: float
    flange_half: float  # square half-side / round radius / hex inscribed radius
    flange_t: float
    hole_r: float
    cup_top_half: float
    cup_bot_half: float
    cup_wall: float
    seat_plate_t: float
    seat_plate_half: float
    seat_hole_r: float
    flange_bot_z: float
    cup_h: float
    seat_top_z: float
    rim_rest_z: float
    rim_out_r: float
    rim_in_r: float
    rim_h: float
    lip_in_r: float
    lip_h: float
    disc_local_z: float
    grate_r: float
    grate_t: float
    # Pattern multiplicity (resolved).
    slots_per_group: int
    n_rings: int
    grid_pitch: float
    # Mechanism ranges.
    lift_travel: float
    twist_limit: float
    flip_upper: float
    plug_travel: float
    # Hinge hardware.
    hinge_z: float
    hinge_y: float
    disc_cy: float
    disc_cz: float
    name: str

    @property
    def hex_circum_d(self) -> float:
        return 2.0 * self.flange_half / _HEX_COS30


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> MetalDrainConfig:
    rng = random.Random(seed)
    return MetalDrainConfig(
        flange_shape=rng.choice(FLANGE_SHAPES),
        grate_pattern=rng.choice(GRATE_PATTERNS),
        grate_mechanism=rng.choice(GRATE_MECHANISMS),
        perf_bucket=rng.choices(PERF_BUCKETS, weights=PERF_BUCKET_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        flange_size_scale=round(rng.uniform(0.85, 1.20), 4),
        cup_depth_scale=round(rng.uniform(0.85, 1.25), 4),
        grate_open_ratio=round(rng.uniform(0.70, 0.86), 4),
        perf_density_scale=round(rng.uniform(0.80, 1.20), 4),
        flip_angle_scale=round(rng.uniform(0.80, 1.10), 4),
        twist_range_scale=round(rng.uniform(0.80, 1.05), 4),
        plug_travel_scale=round(rng.uniform(0.80, 1.20), 4),
        name=f"seeded_metal_drain_{seed}",
    )


def resolve_config(config: MetalDrainConfig | None = None) -> ResolvedMetalDrainConfig:
    cfg = config or MetalDrainConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    flange_shape = _pick(cfg.flange_shape, FLANGE_SHAPES)
    grate_pattern = _pick(cfg.grate_pattern, GRATE_PATTERNS)
    grate_mechanism = _pick(cfg.grate_mechanism, GRATE_MECHANISMS)
    perf_bucket = _pick(cfg.perf_bucket, PERF_BUCKETS)

    size_scale = _clamp(cfg.flange_size_scale, 0.85, 1.20)
    depth_scale = _clamp(cfg.cup_depth_scale, 0.85, 1.25)
    open_ratio = _clamp(cfg.grate_open_ratio, 0.70, 0.86)
    density_scale = _clamp(cfg.perf_density_scale, 0.80, 1.20)
    flip_scale = _clamp(cfg.flip_angle_scale, 0.80, 1.10)
    twist_scale = _clamp(cfg.twist_range_scale, 0.80, 1.05)
    plug_scale = _clamp(cfg.plug_travel_scale, 0.80, 1.20)

    # --- Footprint main dimension. ---
    flange_half = _FLANGE_HALF * size_scale
    flange_t = _FLANGE_T

    # --- Cup depth -> total height (flange thickness is fixed). ---
    total_h = _TOTAL_H * depth_scale
    flange_bot_z = total_h - flange_t
    cup_h = flange_bot_z
    seat_top_z = flange_bot_z

    # --- Circular opening from open_ratio of the flange half-footprint. The hole
    #     + a margin must stay inside the flange's inscribed radius. ---
    hole_r = open_ratio * flange_half
    # Margin so the flange remains a ring around the opening (>= ~6 mm rim).
    max_hole = flange_half - 0.0085
    hole_r = min(hole_r, max_hole)

    # --- Grate / rim radii derive from the hole (captured-seat clearances). ---
    rim_out_r = hole_r - 0.0004  # 0.4 mm radial clearance in the hole
    rim_in_r = rim_out_r - 0.0052
    lip_in_r = rim_in_r - 0.0060
    grate_r = rim_in_r - 0.0005  # 0.5 mm radial clearance in the ring
    # Keep the disc comfortably solid (avoid degenerate small discs).
    grate_r = max(grate_r, 0.030)

    rim_h = _RIM_H
    lip_h = _LIP_H
    grate_t = _GRATE_T
    disc_local_z = rim_h - grate_t
    rim_rest_z = seat_top_z - _RIM_SEAT_EMBED

    # Cup outer footprint follows the flange size (slightly inboard of the rim).
    cup_top_half = min(_CUP_TOP_HALF * size_scale, flange_half - 0.004)
    cup_bot_half = _CUP_BOT_HALF * size_scale
    seat_plate_half = min(_SEAT_PLATE_HALF * size_scale, cup_top_half - 0.001)
    seat_plate_half = max(seat_plate_half, hole_r + 0.003)

    # --- Perforation multiplicity per pattern + bucket, nudged by density. ---
    field_r = min(_FIELD_R, grate_r - 0.006)
    spg = _PINWHEEL_SPG[perf_bucket]
    # density_scale<1 -> sparser; clamp slot count so the field never overflows.
    spg = int(round(spg * density_scale))
    spg = max(3, min(spg, 8))
    # Ensure SLOT_Y0 + (spg-1)*pitch + slot stays inside field_r.
    while spg > 3 and (_SLOT_Y0 + (spg - 1) * _SLOT_PITCH + _SLOT_W / 2.0) >= field_r:
        spg -= 1

    n_rings = _RING_COUNT[perf_bucket]
    n_rings = int(round(n_rings * density_scale))
    n_rings = max(3, min(n_rings, 8))
    ring_pitch = _RING_WIDTH + _RING_GAP
    # popup needs a clear center web -> push the inner ring start out past the bore.
    ring_r0 = _RING_R0
    if grate_mechanism == "popup_center_plug" and grate_pattern == "concentric_rings":
        ring_r0 = max(ring_r0, _PLUG_BORE_R + 0.004)
    while n_rings > 3 and (ring_r0 + (n_rings - 1) * ring_pitch + _RING_WIDTH) >= grate_r - 0.001:
        n_rings -= 1

    grid_pitch = _GRID_PITCH[perf_bucket] / density_scale
    grid_pitch = _clamp(grid_pitch, 0.006, 0.016)

    # --- Mechanism ranges. ---
    lift_travel = _LIFT_TRAVEL
    twist_limit = _clamp(_TWIST_LIMIT * twist_scale, 0.8, _TWIST_LIMIT * 1.05)
    flip_upper = _clamp(_FLIP_UPPER * flip_scale, 1.4, 2.2)
    plug_travel = _clamp(_PLUG_TRAVEL * plug_scale, 0.005, 0.012)

    # Hinge hardware (hinged_flip): pin on the -Y seat edge at the seat surface.
    hinge_z = seat_top_z
    hinge_y = -grate_r
    disc_cy = grate_r
    disc_cz = grate_t / 2.0 + 0.001

    return ResolvedMetalDrainConfig(
        flange_shape=flange_shape,
        grate_pattern=grate_pattern,
        grate_mechanism=grate_mechanism,
        perf_bucket=perf_bucket,
        palette_style=palette_style,
        total_h=total_h,
        flange_half=flange_half,
        flange_t=flange_t,
        hole_r=hole_r,
        cup_top_half=cup_top_half,
        cup_bot_half=cup_bot_half,
        cup_wall=_CUP_WALL,
        seat_plate_t=_SEAT_PLATE_T,
        seat_plate_half=seat_plate_half,
        seat_hole_r=min(_SEAT_HOLE_R, lip_in_r),
        flange_bot_z=flange_bot_z,
        cup_h=cup_h,
        seat_top_z=seat_top_z,
        rim_rest_z=rim_rest_z,
        rim_out_r=rim_out_r,
        rim_in_r=rim_in_r,
        rim_h=rim_h,
        lip_in_r=lip_in_r,
        lip_h=lip_h,
        disc_local_z=disc_local_z,
        grate_r=grate_r,
        grate_t=grate_t,
        slots_per_group=spg,
        n_rings=n_rings,
        grid_pitch=grid_pitch,
        lift_travel=lift_travel,
        twist_limit=twist_limit,
        flip_upper=flip_upper,
        plug_travel=plug_travel,
        hinge_z=hinge_z,
        hinge_y=hinge_y,
        disc_cy=disc_cy,
        disc_cz=disc_cz,
        name=cfg.name or "metal_drain",
    )


def with_overrides(config: MetalDrainConfig, **kwargs: object) -> MetalDrainConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: MetalDrainConfig | ResolvedMetalDrainConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedMetalDrainConfig)
        else resolve_config(config)
    )
    return (
        ("flange", r.flange_shape),
        ("pattern", r.grate_pattern),
        ("mechanism", r.grate_mechanism),
        ("perf", f"n{r.perf_bucket}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Footprint mesh helpers (flange_shape). Each tube/flange/cup/liner shares the
# same footprint primitive (square box / round cylinder / hex polygon). The
# central opening is always circular, so the grate / mechanism are unaffected.
# ---------------------------------------------------------------------------
def _tapered_round_tube(r_bot: float, r_top: float, wall: float, z0: float, z1: float):
    h = z1 - z0
    outer = (
        cq.Workplane("XY").workplane(offset=z0).circle(r_bot)
        .workplane(offset=h).circle(r_top).loft(combine=True)
    )
    slope = (r_top - r_bot) / h
    ext = 0.002
    rb = r_bot - wall - slope * ext
    rt = r_top - wall + slope * ext
    inner = (
        cq.Workplane("XY").workplane(offset=z0 - ext).circle(rb)
        .workplane(offset=h + 2.0 * ext).circle(rt).loft(combine=True)
    )
    return outer.cut(inner)


def _tapered_square_tube(hb: float, ht: float, wall: float, z0: float, z1: float):
    h = z1 - z0
    outer = (
        cq.Workplane("XY").workplane(offset=z0).rect(2.0 * hb, 2.0 * hb)
        .workplane(offset=h).rect(2.0 * ht, 2.0 * ht).loft(combine=True)
    )
    slope = (ht - hb) / h
    ext = 0.002
    ib = hb - wall - slope * ext
    it = ht - wall + slope * ext
    inner = (
        cq.Workplane("XY").workplane(offset=z0 - ext).rect(2.0 * ib, 2.0 * ib)
        .workplane(offset=h + 2.0 * ext).rect(2.0 * it, 2.0 * it).loft(combine=True)
    )
    return outer.cut(inner)


def _hex_d(inscribed: float) -> float:
    return 2.0 * inscribed / _HEX_COS30


def _tapered_hex_tube(ib: float, it: float, wall: float, z0: float, z1: float):
    h = z1 - z0
    outer = (
        cq.Workplane("XY").workplane(offset=z0).polygon(6, _hex_d(ib))
        .workplane(offset=h).polygon(6, _hex_d(it)).loft(combine=True)
    )
    slope = (it - ib) / h
    ext = 0.002
    eb = ib - wall - slope * ext
    et = it - wall + slope * ext
    inner = (
        cq.Workplane("XY").workplane(offset=z0 - ext).polygon(6, _hex_d(eb))
        .workplane(offset=h + 2.0 * ext).polygon(6, _hex_d(et)).loft(combine=True)
    )
    return outer.cut(inner)


def _tapered_tube(r: ResolvedMetalDrainConfig, hb: float, ht: float, wall: float, z0: float, z1: float):
    if r.flange_shape == "round_circular":
        return _tapered_round_tube(hb, ht, wall, z0, z1)
    if r.flange_shape == "hexagonal":
        return _tapered_hex_tube(hb, ht, wall, z0, z1)
    return _tapered_square_tube(hb, ht, wall, z0, z1)


def _flange_plate(r: ResolvedMetalDrainConfig):
    """Footprint flange plate (z = flange_bot_z .. total_h) with the round
    opening and beveled top edges."""
    zc = r.flange_bot_z + r.flange_t / 2.0
    if r.flange_shape == "round_circular":
        plate = cq.Workplane("XY").cylinder(r.flange_t, r.flange_half).translate((0, 0, zc))
    elif r.flange_shape == "hexagonal":
        plate = (
            cq.Workplane("XY").workplane(offset=r.flange_bot_z)
            .polygon(6, r.hex_circum_d).extrude(r.flange_t)
        )
    else:
        plate = (
            cq.Workplane("XY")
            .box(2.0 * r.flange_half, 2.0 * r.flange_half, r.flange_t)
            .translate((0, 0, zc))
        )
    hole = cq.Workplane("XY").cylinder(r.flange_t + 0.01, r.hole_r).translate((0, 0, zc))
    plate = plate.cut(hole)
    plate = plate.faces(">Z").edges().chamfer(_FLANGE_CHAMFER)
    return plate


def _cup_solid(r: ResolvedMetalDrainConfig):
    """Open-bottomed tapered cup + inward seat plate (z = 0 .. flange_bot_z)."""
    shell = _tapered_tube(r, r.cup_bot_half, r.cup_top_half, r.cup_wall, 0.0, r.cup_h)
    if r.flange_shape == "round_circular":
        plate = (
            cq.Workplane("XY").cylinder(r.seat_plate_t, r.seat_plate_half)
            .translate((0, 0, r.cup_h - r.seat_plate_t / 2.0))
        )
    elif r.flange_shape == "hexagonal":
        plate = (
            cq.Workplane("XY").workplane(offset=r.cup_h - r.seat_plate_t)
            .polygon(6, _hex_d(r.seat_plate_half)).extrude(r.seat_plate_t)
        )
    else:
        plate = (
            cq.Workplane("XY")
            .box(2.0 * r.seat_plate_half, 2.0 * r.seat_plate_half, r.seat_plate_t)
            .translate((0, 0, r.cup_h - r.seat_plate_t / 2.0))
        )
    throat = (
        cq.Workplane("XY").cylinder(r.seat_plate_t + 0.01, r.seat_hole_r)
        .translate((0, 0, r.cup_h - r.seat_plate_t / 2.0))
    )
    plate = plate.cut(throat)
    body = shell.union(plate)
    # Central strainer-support boss + spider ribs across the throat. Real floor
    # drains carry a small central hub that supports the grate spindle; here it
    # also lands the grate joint origin (0,0,seat_top) on real body geometry
    # (the throat is otherwise an open hole, which would float the joint origin).
    hub_z0 = r.cup_h - r.seat_plate_t
    hub = (
        cq.Workplane("XY").cylinder(r.seat_plate_t, _HUB_R)
        .translate((0, 0, r.cup_h - r.seat_plate_t / 2.0))
    )
    body = body.union(hub)
    rib_len = r.seat_hole_r + 0.001
    for i in range(4):
        ang = 90.0 * i
        rib = (
            cq.Workplane("XY").box(rib_len, _RIB_W, r.seat_plate_t)
            .translate((rib_len / 2.0, 0.0, hub_z0 + r.seat_plate_t / 2.0))
            .rotate((0, 0, 0), (0, 0, 1), ang)
        )
        body = body.union(rib)
    return body


def _liner_solid(r: ResolvedMetalDrainConfig):
    """Dark cavity liner embedded against the cup inner walls."""
    liner_z1 = r.flange_bot_z - r.seat_plate_t

    def inner_half(z: float) -> float:
        return (r.cup_bot_half - r.cup_wall) + (r.cup_top_half - r.cup_bot_half) * (z / r.cup_h)

    hb = inner_half(_LINER_Z0) + _LINER_EMBED
    ht = inner_half(liner_z1) + _LINER_EMBED
    return _tapered_tube(r, hb, ht, _LINER_WALL, _LINER_Z0, liner_z1)


def _rim_solid(r: ResolvedMetalDrainConfig):
    """Grate seat ring (L-section: outer wall + inward bottom lip). Local frame
    bottom at z = 0."""
    wall = (
        cq.Workplane("XY").cylinder(r.rim_h, r.rim_out_r).translate((0, 0, r.rim_h / 2.0))
        .cut(cq.Workplane("XY").cylinder(r.rim_h + 0.01, r.rim_in_r).translate((0, 0, r.rim_h / 2.0)))
    )
    lip = (
        cq.Workplane("XY").cylinder(r.lip_h, r.rim_in_r + 0.0002).translate((0, 0, r.lip_h / 2.0))
        .cut(cq.Workplane("XY").cylinder(r.lip_h + 0.01, r.lip_in_r).translate((0, 0, r.lip_h / 2.0)))
    )
    ring = wall.union(lip)
    # Central spindle boss + spider ribs across the lip opening, at the lip level.
    # The grate disc rests on the lip and pivots on this hub; it also lands the
    # rim_to_grate joint origin (0,0,disc_local_z ~ lip top) on real rim geometry.
    hub = cq.Workplane("XY").cylinder(r.lip_h, _HUB_R).translate((0, 0, r.lip_h / 2.0))
    ring = ring.union(hub)
    rib_len = r.lip_in_r + 0.001
    for i in range(4):
        ang = 45.0 + 90.0 * i
        rib = (
            cq.Workplane("XY").box(rib_len, _RIB_W, r.lip_h)
            .translate((rib_len / 2.0, 0.0, r.lip_h / 2.0))
            .rotate((0, 0, 0), (0, 0, 1), ang)
        )
        ring = ring.union(rib)
    return ring


# ---------------------------------------------------------------------------
# Grate disc cut patterns (grate_pattern). The disc is one part; the pattern is
# a cut, with the perforation multiplicity = perf bucket. Optional center bore
# for popup. ``disc_origin_z`` is the disc-bottom Z in the grate's part frame.
# ---------------------------------------------------------------------------
def _pinwheel_disc(r: ResolvedMetalDrainConfig, *, cx0: float, cy0: float, cz0: float, bore: bool):
    field_r = min(_FIELD_R, r.grate_r - 0.006)
    disc = cq.Workplane("XY").cylinder(r.grate_t, r.grate_r).translate((cx0, cy0, cz0 + r.grate_t / 2.0))
    cutters = None
    for group in range(_N_GROUPS):
        angle = 90.0 * group
        for i in range(r.slots_per_group):
            y = _SLOT_Y0 + i * _SLOT_PITCH
            y_out = y + _SLOT_W / 2.0
            x_outer = math.sqrt(max(field_r**2 - y_out**2, 1e-6))
            length = x_outer - _CENTER_GAP
            if length <= 0.0:
                continue
            cxs = -(x_outer + _CENTER_GAP) / 2.0
            slot = (
                cq.Workplane("XY").box(length, _SLOT_W, r.grate_t + 0.006)
                .translate((cxs, y, 0.0))
                .rotate((0, 0, 0), (0, 0, 1), angle)
                .translate((cx0, cy0, cz0 + r.grate_t / 2.0))
            )
            cutters = slot if cutters is None else cutters.union(slot)
    if cutters is not None:
        disc = disc.cut(cutters)
    if bore:
        b = cq.Workplane("XY").cylinder(r.grate_t + 0.006, _PLUG_BORE_R).translate((cx0, cy0, cz0 + r.grate_t / 2.0))
        disc = disc.cut(b)
    return disc


def _concentric_disc(r: ResolvedMetalDrainConfig, *, cx0: float, cy0: float, cz0: float, bore: bool):
    disc = cq.Workplane("XY").cylinder(r.grate_t, r.grate_r).translate((cx0, cy0, cz0 + r.grate_t / 2.0))
    ring_pitch = _RING_WIDTH + _RING_GAP
    ring_r0 = _RING_R0
    if bore:
        ring_r0 = max(ring_r0, _PLUG_BORE_R + 0.004)
    cutters = None
    for i in range(r.n_rings):
        inner_r = ring_r0 + i * ring_pitch
        outer_r = inner_r + _RING_WIDTH
        if outer_r >= r.grate_r - 0.001:
            break
        ring = (
            cq.Workplane("XY").cylinder(r.grate_t + 0.006, outer_r).translate((cx0, cy0, cz0 + r.grate_t / 2.0))
            .cut(cq.Workplane("XY").cylinder(r.grate_t + 0.008, inner_r).translate((cx0, cy0, cz0 + r.grate_t / 2.0)))
        )
        cutters = ring if cutters is None else cutters.union(ring)
    if cutters is not None:
        disc = disc.cut(cutters)
    # Radial bridge bars reconnect the rings.
    bridges = None
    length = (r.grate_r - 0.001) - _BRIDGE_INNER_R
    cxb = (_BRIDGE_INNER_R + (r.grate_r - 0.001)) / 2.0
    for i in range(_N_BRIDGES):
        angle = 360.0 * i / _N_BRIDGES
        bar = (
            cq.Workplane("XY").box(length, _BRIDGE_W, r.grate_t)
            .translate((cxb, 0.0, 0.0))
            .rotate((0, 0, 0), (0, 0, 1), angle)
            .translate((cx0, cy0, cz0 + r.grate_t / 2.0))
        )
        bridges = bar if bridges is None else bridges.union(bar)
    if bridges is not None:
        disc = disc.union(bridges)
    if bore:
        b = cq.Workplane("XY").cylinder(r.grate_t + 0.006, _PLUG_BORE_R).translate((cx0, cy0, cz0 + r.grate_t / 2.0))
        disc = disc.cut(b)
    return disc


def _grid_disc(r: ResolvedMetalDrainConfig, *, cx0: float, cy0: float, cz0: float, bore: bool):
    disc = cq.Workplane("XY").cylinder(r.grate_t, r.grate_r).translate((cx0, cy0, cz0 + r.grate_t / 2.0))
    field_r = min(_GRID_FIELD_R, r.grate_r - 0.006)
    max_r = field_r - _GRID_HOLE_R
    n = int(math.ceil(field_r / r.grid_pitch)) + 1
    cutters = None
    for row in range(-n, n + 1):
        for col in range(-n, n + 1):
            x = col * r.grid_pitch
            y = row * r.grid_pitch
            d = math.hypot(x, y)
            if d > max_r:
                continue
            # popup: drop the central grid point so the plug bore stays clear.
            if bore and d < _PLUG_BORE_R + 0.003:
                continue
            hole = (
                cq.Workplane("XY").cylinder(r.grate_t + 0.006, _GRID_HOLE_R)
                .translate((cx0 + x, cy0 + y, cz0 + r.grate_t / 2.0))
            )
            cutters = hole if cutters is None else cutters.union(hole)
    if cutters is not None:
        disc = disc.cut(cutters)
    if bore:
        b = cq.Workplane("XY").cylinder(r.grate_t + 0.006, _PLUG_BORE_R).translate((cx0, cy0, cz0 + r.grate_t / 2.0))
        disc = disc.cut(b)
    return disc


def _grate_disc(r: ResolvedMetalDrainConfig, *, cx0: float = 0.0, cy0: float = 0.0, cz0: float = 0.0, bore: bool = False):
    if r.grate_pattern == "concentric_rings":
        return _concentric_disc(r, cx0=cx0, cy0=cy0, cz0=cz0, bore=bore)
    if r.grate_pattern == "square_grid_holes":
        return _grid_disc(r, cx0=cx0, cy0=cy0, cz0=cz0, bore=bore)
    return _pinwheel_disc(r, cx0=cx0, cy0=cy0, cz0=cz0, bore=bore)


def _hinge_bracket_solid(r: ResolvedMetalDrainConfig):
    """Two bracket ears on the body carrying the hinge pin at the -Y seat edge."""
    ear_half_gap = _HINGE_LEN / 2.0 - _BRACKET_T / 2.0
    ears = None
    for sign in (-1.0, 1.0):
        ear = (
            cq.Workplane("XY").box(_BRACKET_T, _BRACKET_W, _BRACKET_DROP)
            .translate((sign * (ear_half_gap + _BRACKET_T / 2.0), r.hinge_y, r.hinge_z - _BRACKET_DROP / 2.0))
        )
        cap = (
            cq.Workplane("YZ").cylinder(_BRACKET_T, _BRACKET_W / 2.0)
            .translate((sign * (ear_half_gap + _BRACKET_T / 2.0), r.hinge_y, r.hinge_z))
        )
        ear = ear.union(cap)
        hole = (
            cq.Workplane("YZ").cylinder(_BRACKET_T + 0.01, _HINGE_R * 1.1)
            .translate((sign * (ear_half_gap + _BRACKET_T / 2.0), r.hinge_y, r.hinge_z))
        )
        ear = ear.cut(hole)
        ears = ear if ears is None else ears.union(ear)
    pin = cq.Workplane("YZ").cylinder(_HINGE_LEN, _HINGE_R).translate((0.0, r.hinge_y, r.hinge_z))
    return ears.union(pin)


def _hinged_grate_solid(r: ResolvedMetalDrainConfig):
    """Hinged grate disc + knuckle + connecting tab, authored in the hinge-pin
    frame (origin at the pin center; disc center at (0, disc_cy, disc_cz))."""
    disc = _grate_disc(r, cx0=0.0, cy0=r.disc_cy, cz0=r.disc_cz - r.grate_t / 2.0, bore=False)
    knuckle = cq.Workplane("YZ").cylinder(_KNUCKLE_LEN, _KNUCKLE_R)
    pin_hole = cq.Workplane("YZ").cylinder(_KNUCKLE_LEN + 0.01, _HINGE_R * 1.1)
    knuckle = knuckle.cut(pin_hole)
    tab_dy = r.disc_cy - r.grate_r
    tab_h = r.disc_cz + r.grate_t / 2.0
    tab = (
        cq.Workplane("XY").box(_KNUCKLE_LEN * 0.6, abs(tab_dy) + _KNUCKLE_R, tab_h)
        .translate((0.0, tab_dy / 2.0, tab_h / 2.0))
    )
    return disc.union(knuckle).union(tab)


def _plug_solid(r: ResolvedMetalDrainConfig):
    """Pop-up center plug: cap + guide stem. Local frame: cap bottom at z=0."""
    cap = cq.Workplane("XY").cylinder(_PLUG_CAP_T, _PLUG_CAP_R).translate((0, 0, _PLUG_CAP_T / 2.0))
    cap = cap.faces(">Z").edges().chamfer(0.0008)
    stem = cq.Workplane("XY").cylinder(_PLUG_STEM_H, _PLUG_STEM_R).translate((0, 0, -_PLUG_STEM_H / 2.0))
    return cap.union(stem)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def _body_inertial(r: ResolvedMetalDrainConfig) -> Inertial:
    return Inertial.from_geometry(
        Box((2.0 * r.flange_half, 2.0 * r.flange_half, r.total_h)),
        mass=0.6,
        origin=Origin(xyz=(0.0, 0.0, r.total_h / 2.0)),
    )


def _build_drain_body(model: ArticulatedObject, r: ResolvedMetalDrainConfig, mats, *, assets):
    body = model.part("drain_body")
    body.visual(
        mesh_from_cadquery(_flange_plate(r), "flange_plate", assets=assets),
        material=mats["polished"], name="flange_plate", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_stainless", "matte_black", "antique_brass", "oil_rubbed_bronze"} else "metal.chrome_polished"),
    )
    body.visual(
        mesh_from_cadquery(_cup_solid(r), "drain_cup", assets=assets),
        material=mats["brushed"], name="drain_cup", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_stainless", "polished_chrome", "antique_brass", "oil_rubbed_bronze"} else "metal.paint_coated"),
    )
    body.visual(
        mesh_from_cadquery(_liner_solid(r), "cavity_liner", assets=assets),
        material=mats["cavity"], name="cavity_liner", material_class_id="metal.blackened_gunmetal",
    )
    body.inertial = _body_inertial(r)
    return body


def _emit_twist_lock(model, r: ResolvedMetalDrainConfig, body, mats, *, assets, with_plug: bool):
    rim = model.part("grate_rim")
    rim.visual(
        mesh_from_cadquery(_rim_solid(r), "grate_rim", assets=assets),
        material=mats["brushed"], name="rim_ring", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_stainless", "polished_chrome", "antique_brass", "oil_rubbed_bronze"} else "metal.paint_coated"),
    )
    rim.inertial = Inertial.from_geometry(
        Box((2.0 * r.rim_out_r, 2.0 * r.rim_out_r, r.rim_h)),
        mass=0.05, origin=Origin(xyz=(0.0, 0.0, r.rim_h / 2.0)),
    )
    grate = model.part("grate")
    grate.visual(
        mesh_from_cadquery(_grate_disc(r, bore=with_plug), "grate_disc", assets=assets),
        material=mats["polished"], name="grate_disc", material_class_id="metal.mesh_chainmail",
    )
    grate.inertial = Inertial.from_geometry(
        Box((2.0 * r.grate_r, 2.0 * r.grate_r, r.grate_t)),
        mass=0.05, origin=Origin(xyz=(0.0, 0.0, r.grate_t / 2.0)),
    )
    model.articulation(
        "body_to_grate_rim",
        ArticulationType.PRISMATIC,
        parent=body, child=rim,
        origin=Origin(xyz=(0.0, 0.0, r.rim_rest_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.2, lower=0.0, upper=r.lift_travel),
    )
    model.articulation(
        "rim_to_grate",
        ArticulationType.REVOLUTE,
        parent=rim, child=grate,
        origin=Origin(xyz=(0.0, 0.0, r.disc_local_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=-r.twist_limit, upper=r.twist_limit),
    )
    names = ["grate_rim", "grate"]
    if with_plug:
        plug = model.part("center_plug")
        plug.visual(
            mesh_from_cadquery(_plug_solid(r), "center_plug", assets=assets),
            material=mats["accent"], name="plug_cap", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_stainless", "matte_black", "antique_brass", "oil_rubbed_bronze"} else "metal.chrome_polished"),
        )
        plug.inertial = Inertial.from_geometry(
            Box((2.0 * _PLUG_CAP_R, 2.0 * _PLUG_CAP_R, _PLUG_CAP_T + _PLUG_STEM_H)),
            mass=0.01, origin=Origin(xyz=(0.0, 0.0, _PLUG_CAP_T / 2.0)),
        )
        model.articulation(
            "grate_to_plug",
            ArticulationType.PRISMATIC,
            parent=grate, child=plug,
            origin=Origin(xyz=(0.0, 0.0, r.grate_t)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=20.0, velocity=0.1, lower=0.0, upper=r.plug_travel),
        )
        names.append("center_plug")
    return names


def _emit_hinged_flip(model, r: ResolvedMetalDrainConfig, body, mats, *, assets):
    # Seat ring fuses into the body as a fixed visual; body gets the hinge bracket.
    rim_mesh = _rim_solid(r).translate((0.0, 0.0, r.rim_rest_z))
    body.visual(
        mesh_from_cadquery(rim_mesh, "seat_ring", assets=assets),
        material=mats["brushed"], name="seat_ring", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_stainless", "polished_chrome", "antique_brass", "oil_rubbed_bronze"} else "metal.paint_coated"),
    )
    body.visual(
        mesh_from_cadquery(_hinge_bracket_solid(r), "hinge_bracket", assets=assets),
        material=mats["accent"], name="hinge_bracket", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_stainless", "matte_black", "antique_brass", "oil_rubbed_bronze"} else "metal.chrome_polished"),
    )
    grate = model.part("grate")
    grate.visual(
        mesh_from_cadquery(_hinged_grate_solid(r), "grate_disc", assets=assets),
        material=mats["polished"], name="grate_disc", material_class_id="metal.mesh_chainmail",
    )
    grate.inertial = Inertial.from_geometry(
        Box((2.0 * r.grate_r, 2.0 * r.grate_r, r.grate_t)),
        mass=0.05, origin=Origin(xyz=(0.0, r.disc_cy, r.disc_cz)),
    )
    model.articulation(
        "body_to_grate",
        ArticulationType.REVOLUTE,
        parent=body, child=grate,
        origin=Origin(xyz=(0.0, r.hinge_y, r.hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.5, lower=0.0, upper=r.flip_upper),
    )
    return ["grate"]


def build_metal_drain(
    config: MetalDrainConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"drain_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_drain_body(model, r, mats, assets=assets)

    if r.grate_mechanism == "hinged_flip_grate":
        _emit_hinged_flip(model, r, body, mats, assets=assets)
    elif r.grate_mechanism == "popup_center_plug":
        _emit_twist_lock(model, r, body, mats, assets=assets, with_plug=True)
    else:  # twist_lock_lift_out
        _emit_twist_lock(model, r, body, mats, assets=assets, with_plug=False)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_metal_drain(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_metal_drain(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_metal_drain_tests(
    object_model: ArticulatedObject,
    config: MetalDrainConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("drain_body")

    # ---- Captured-seat / bore / pin allowances (element-scoped). ----
    if r.grate_mechanism in ("twist_lock_lift_out", "popup_center_plug"):
        rim = object_model.get_part("grate_rim")
        grate = object_model.get_part("grate")
        ctx.allow_overlap(
            rim, body,
            reason="Seat ring bottoms into the cup's seat plate (seated insertion).",
        )
        ctx.allow_overlap(
            grate, rim,
            reason="Grate disc rests embedded on the seat ring's inner lip (seated).",
        )
        if r.grate_mechanism == "popup_center_plug":
            plug = object_model.get_part("center_plug")
            ctx.allow_overlap(
                plug, grate, elem_a="plug_cap", elem_b="grate_disc",
                reason="Plug cap bottom seats on the grate top surface (captured-bore).",
            )
            ctx.allow_overlap(
                plug, rim, elem_a="plug_cap", elem_b="rim_ring",
                reason="Plug guide stem passes down through the rim spindle hub (captured-bore).",
            )
            ctx.allow_overlap(
                plug, body, elem_a="plug_cap", elem_b="drain_cup",
                reason="Plug guide stem reaches into the cup throat below the grate (captured-bore).",
            )
    else:  # hinged_flip_grate
        grate = object_model.get_part("grate")
        ctx.allow_overlap(
            grate, body, elem_a="grate_disc", elem_b="seat_ring",
            reason="Grate disc seats inside the seat ring opening on the inner lip.",
        )
        ctx.allow_overlap(
            grate, body, elem_a="grate_disc", elem_b="hinge_bracket",
            reason="Grate knuckle wraps the hinge pin barrel (captured pin fit).",
        )

    if r.grate_mechanism in ("twist_lock_lift_out", "popup_center_plug"):
        ctx.allow_isolated_part(
            object_model.get_part("grate_rim"),
            reason="grate rim lifts out of the drain cup and loses body contact",
        )
        ctx.allow_isolated_part(
            object_model.get_part("grate"),
            reason="grate lifts out of the drain cup and loses body contact",
        )
        if r.grate_mechanism == "popup_center_plug":
            ctx.allow_isolated_part(
                object_model.get_part("center_plug"),
                reason="center plug lifts out of the drain and loses contact",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("drain_body present", "drain_body" in part_names, details=str(sorted(part_names)))

    body_aabb = ctx.part_world_aabb(body)
    if body_aabb is not None:
        ctx.check(
            "cup mouth on the ground, flange top near total_h",
            abs(body_aabb[0][2]) <= 0.002 and abs(body_aabb[1][2] - r.total_h) <= 0.002,
            details=str(body_aabb),
        )

    # Dark cavity liner present (reads dark through the grate).
    ctx.check("dark cavity liner authored", body.get_visual("cavity_liner") is not None)

    # ---- Mechanism joint topology. ----
    if r.grate_mechanism == "twist_lock_lift_out":
        lift = object_model.get_articulation("body_to_grate_rim")
        twist = object_model.get_articulation("rim_to_grate")
        ctx.check(
            "twist_lock: PRISMATIC +Z lift + REVOLUTE +Z twist",
            lift.articulation_type == ArticulationType.PRISMATIC and abs(lift.axis[2]) > 0.99
            and twist.articulation_type == ArticulationType.REVOLUTE and abs(twist.axis[2]) > 0.99,
            details=f"lift={tuple(lift.axis)} twist={tuple(twist.axis)}",
        )
    elif r.grate_mechanism == "popup_center_plug":
        lift = object_model.get_articulation("body_to_grate_rim")
        twist = object_model.get_articulation("rim_to_grate")
        popup = object_model.get_articulation("grate_to_plug")
        ctx.check(
            "popup: PRISMATIC +Z + REVOLUTE +Z + PRISMATIC +Z (3 joints, depth 3)",
            lift.articulation_type == ArticulationType.PRISMATIC and abs(lift.axis[2]) > 0.99
            and twist.articulation_type == ArticulationType.REVOLUTE and abs(twist.axis[2]) > 0.99
            and popup.articulation_type == ArticulationType.PRISMATIC and abs(popup.axis[2]) > 0.99,
            details=f"lift={tuple(lift.axis)} twist={tuple(twist.axis)} plug={tuple(popup.axis)}",
        )
    else:  # hinged_flip_grate
        hinge = object_model.get_articulation("body_to_grate")
        ctx.check(
            "hinged_flip: single REVOLUTE about horizontal +X",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.99,
            details=f"type={hinge.articulation_type} axis={tuple(hinge.axis)}",
        )

    # ---- Actuation: grate opens / lifts / flips out of the seat. ----
    if r.grate_mechanism in ("twist_lock_lift_out", "popup_center_plug"):
        lift = object_model.get_articulation("body_to_grate_rim")
        grate = object_model.get_part("grate")
        rest = ctx.part_world_position(grate)
        with ctx.pose({lift: r.lift_travel}):
            up = ctx.part_world_position(grate)
        if rest is not None and up is not None:
            ctx.check(
                "grate lifts straight up by the full travel",
                abs((up[2] - rest[2]) - r.lift_travel) <= 0.002
                and abs(up[0] - rest[0]) <= 1e-5 and abs(up[1] - rest[1]) <= 1e-5,
                details=f"rest={rest} up={up}",
            )
        if r.grate_mechanism == "popup_center_plug":
            popup = object_model.get_articulation("grate_to_plug")
            plug = object_model.get_part("center_plug")
            p0 = ctx.part_world_position(plug)
            with ctx.pose({popup: r.plug_travel}):
                p1 = ctx.part_world_position(plug)
            if p0 is not None and p1 is not None:
                ctx.check(
                    "center plug pops up",
                    p1[2] > p0[2] + r.plug_travel * 0.6,
                    details=f"seated_z={p0[2]:.4f} popped_z={p1[2]:.4f}",
                )
    else:
        hinge = object_model.get_articulation("body_to_grate")
        grate = object_model.get_part("grate")
        closed = ctx.part_world_aabb(grate)
        with ctx.pose({hinge: r.flip_upper * 0.7}):
            opened = ctx.part_world_aabb(grate)
        if closed is not None and opened is not None:
            ctx.check(
                "hinged grate flips up to expose the cavity",
                opened[1][2] > closed[1][2] + 0.020,
                details=f"closed_top={closed[1][2]:.3f} flipped_top={opened[1][2]:.3f}",
            )

    # ---- Perforation cut proven (the grate disc is actually perforated). ----
    disc = _grate_disc(r, bore=(r.grate_mechanism == "popup_center_plug"))
    try:
        disc_vol = float(disc.val().Volume())
        solid_vol = math.pi * r.grate_r**2 * r.grate_t
        ctx.check(
            "grate pattern perforates the disc",
            0.3 * solid_vol < disc_vol < 0.95 * solid_vol,
            details=f"disc_vol={disc_vol:.3e} solid_vol={solid_vol:.3e}",
        )
    except Exception as exc:  # noqa: BLE001
        ctx.check("grate disc solid builds", False, details=str(exc))

    # ---- Clearance inequalities (proven from authored dims). ----
    ctx.check(
        "circular opening fits inside the flange footprint",
        r.hole_r + 0.006 <= r.flange_half,
        details=f"hole_r={r.hole_r:.4f} flange_half={r.flange_half:.4f}",
    )
    ctx.check(
        "grate / rim seat inside the opening (radial clearance)",
        r.rim_out_r < r.hole_r and r.grate_r < r.rim_in_r,
        details=f"rim_out={r.rim_out_r:.4f} hole={r.hole_r:.4f} grate={r.grate_r:.4f} rim_in={r.rim_in_r:.4f}",
    )

    # ---- slot_choices recorded with perf bucket encoded. ----
    ctx.check(
        "slot_choices recorded with perf bucket encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "MetalDrainConfig",
    "ResolvedMetalDrainConfig",
    "build_metal_drain",
    "build_seeded_metal_drain",
    "config_from_seed",
    "resolve_config",
    "run_metal_drain_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
