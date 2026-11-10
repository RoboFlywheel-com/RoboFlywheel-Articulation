# SPDX-License-Identifier: Apache-2.0

"""Draft Wagon — modular procedural template.

A wooden draft / farm wagon or hand cart: a plank cargo bed/box riding on big
spoked wooden wheels that roll about the lateral (world +Y) axis. Four mature
domains in one family:

  * ``single_axle_two_wheel`` — 2-wheel hand cart / dray: one rear axle, two
    spoked wheels, front prop legs + pull shafts (no steering bolster).
  * ``four_wheel_steered`` — 4-wheel open farm wagon: a steerable ``front_bolster``
    (REVOLUTE yaw about world +Z) carrying the front wheel pair + draw poles,
    fixed rear axle on the body.
  * ``six_wheel_triple_axle`` — same steered front bolster + a mid + rear fixed
    axle, 6 wheels total.

DEFINING MOTION (always present): every wheel rolls = CONTINUOUS spin about
world +Y. 4/6-wheel members add a steering ``front_steer`` REVOLUTE about world
+Z (the bolster carries the front wheel pair + draw poles).

This is a direct-build modular template (like ``bicycle.py`` /
``wheelbarrow.py``): one ``body`` root part (chassis/bed) plus parallel wheel
parts, an optional ``front_bolster`` part, and an optional ``tailgate`` part.
Wheels / spokes / planks / stakes / hoops are loop-emitted multiplicity.
``slot_choices_for_seed`` records the slot/module picks for the
``module_topology_diversity`` gate.

Slots (see spec):
  * Slot A wheel_config — wheel/axle station topology + bolster presence.
  * Slot B spoke_count — wheel-internal spoke multiplicity {8,10,12,16}.
  * Slot C bed_sidewall — plank/board/stake wall multiplicity on the body.
  * Slot D top_cover — open / gabled roof / canvas bow tilt / drop tailgate.

3 hard rules honoured:
  * Decorations (iron strapping, rope tie, swingletree, hub band, prop legs,
    draw poles) are ``parent.visual`` — only the wheels, steering bolster and
    drop tailgate are real articulated parts.
  * Every non-FIXED joint (wheel spins, steer, tailgate) declares a
    MatingContract / captured-overlap allowance.
  * Spoked wheels use a lathe/mesh spoke loop (Cylinder spokes through a torus
    felloe + hub), never a Box downgrade.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from math import cos, pi, sin
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    CylinderGeometry,
    Inertial,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


# --------------------------------------------------------------------------- #
# Module enums
# --------------------------------------------------------------------------- #

WheelConfig = Literal[
    "single_axle_two_wheel",
    "four_wheel_steered",
    "six_wheel_triple_axle",
]
BedSidewall = Literal[
    "low_three_plank_rails",
    "tall_back_wall",
    "high_sided_grain_box",
    "flat_rack_stake_bed",
]
TopCover = Literal[
    "open_none",
    "gabled_plank_roof",
    "canvas_bow_tilt_cover",
    "drop_tailgate_open_box",
]
PaletteStyle = Literal[
    "oak_natural",
    "weathered_grey",
    "dark_walnut",
    "painted_red",
    "pine_blond",
    "green_painted_iron",
]


# palette_style colorways (>=3): each drives every .visual via the `mats` map.
# Keys: wood (planks/felloe), dark (dark wood/trim), plank (bright plank face),
#       iron (straps/hubs), canvas (tilt cloth), rope (tie/rope).
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "oak_natural": {
        "wood": (0.74, 0.58, 0.36, 1.0),
        "dark": (0.45, 0.33, 0.20, 1.0),
        "plank": (0.80, 0.65, 0.43, 1.0),
        "iron": (0.16, 0.16, 0.17, 1.0),
        "canvas": (0.88, 0.84, 0.74, 1.0),
        "rope": (0.72, 0.64, 0.42, 1.0),
    },
    "weathered_grey": {
        "wood": (0.62, 0.55, 0.45, 1.0),
        "dark": (0.40, 0.34, 0.27, 1.0),
        "plank": (0.68, 0.60, 0.49, 1.0),
        "iron": (0.17, 0.17, 0.18, 1.0),
        "canvas": (0.84, 0.82, 0.76, 1.0),
        "rope": (0.70, 0.63, 0.45, 1.0),
    },
    "dark_walnut": {
        "wood": (0.46, 0.32, 0.20, 1.0),
        "dark": (0.30, 0.21, 0.13, 1.0),
        "plank": (0.52, 0.38, 0.24, 1.0),
        "iron": (0.15, 0.15, 0.16, 1.0),
        "canvas": (0.82, 0.78, 0.68, 1.0),
        "rope": (0.66, 0.57, 0.38, 1.0),
    },
    "painted_red": {
        "wood": (0.66, 0.50, 0.30, 1.0),
        "dark": (0.30, 0.10, 0.08, 1.0),
        "plank": (0.62, 0.18, 0.14, 1.0),
        "iron": (0.12, 0.12, 0.13, 1.0),
        "canvas": (0.86, 0.82, 0.72, 1.0),
        "rope": (0.70, 0.62, 0.42, 1.0),
    },
    "pine_blond": {
        "wood": (0.82, 0.70, 0.48, 1.0),
        "dark": (0.55, 0.44, 0.28, 1.0),
        "plank": (0.86, 0.74, 0.52, 1.0),
        "iron": (0.20, 0.20, 0.21, 1.0),
        "canvas": (0.90, 0.86, 0.76, 1.0),
        "rope": (0.74, 0.66, 0.46, 1.0),
    },
    "green_painted_iron": {
        "wood": (0.60, 0.46, 0.30, 1.0),
        "dark": (0.14, 0.24, 0.16, 1.0),
        "plank": (0.24, 0.40, 0.26, 1.0),
        "iron": (0.13, 0.13, 0.14, 1.0),
        "canvas": (0.85, 0.83, 0.74, 1.0),
        "rope": (0.70, 0.63, 0.43, 1.0),
    },
}
PALETTE_STYLES: tuple[PaletteStyle, ...] = tuple(PALETTES.keys())  # type: ignore[assignment]


_WHEEL_CONFIGS: tuple[WheelConfig, ...] = (
    "single_axle_two_wheel",
    "four_wheel_steered",
    "six_wheel_triple_axle",
)
_SIDEWALLS: tuple[BedSidewall, ...] = (
    "low_three_plank_rails",
    "tall_back_wall",
    "high_sided_grain_box",
    "flat_rack_stake_bed",
)
_TOP_COVERS: tuple[TopCover, ...] = (
    "open_none",
    "gabled_plank_roof",
    "canvas_bow_tilt_cover",
    "drop_tailgate_open_box",
)

# Spoke-count weighted sampling (spec Multiplicity axis 1).
_SPOKE_CHOICES: tuple[int, ...] = (8, 10, 12, 16)
_SPOKE_WEIGHTS: tuple[float, ...] = (0.30, 0.30, 0.30, 0.10)

# Fixed geometric constants.
RIM_TUBE_R = 0.030  # felloe (rim) tube radius; wheel touches ground at z=0.
FLOOR_THK = 0.05
HUB_R = 0.060


# --------------------------------------------------------------------------- #
# Compatibility gating (spec compatibility matrix).
# --------------------------------------------------------------------------- #
def _legal_top_covers(wheel_config: WheelConfig, sidewall: BedSidewall) -> tuple[TopCover, ...]:
    """Resolve the legal top_cover subset for a wheel_config + sidewall.

    * 2-wheel hand-cart/dray never carries a gabled/canvas cabin (identity)
      → only {open, drop_tailgate}.
    * gabled needs a symmetric continuous wall top: tall_back_wall (asymmetric)
      and flat_rack_stake_bed (no continuous wall) degrade gabled→open.
    * drop_tailgate needs a rear end wall: flat_rack has none → degrade open.
    * canvas needs a continuous wall top to arch over; flat_rack allows it
      (hoops bridge the deck), tall_back_wall allows it.
    """
    covers: list[TopCover] = ["open_none"]
    is_two_wheel = wheel_config == "single_axle_two_wheel"

    # gabled
    if not is_two_wheel and sidewall in ("low_three_plank_rails", "high_sided_grain_box"):
        covers.append("gabled_plank_roof")
    # canvas
    if not is_two_wheel:
        covers.append("canvas_bow_tilt_cover")
    # drop tailgate
    if sidewall != "flat_rack_stake_bed":
        covers.append("drop_tailgate_open_box")
    return tuple(covers)


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class DraftWagonConfig:
    wheel_config: WheelConfig | None = None
    spoke_count: int | None = None
    bed_sidewall: BedSidewall | None = None
    top_cover: TopCover | None = None
    palette_style: PaletteStyle = "weathered_grey"

    # Multiplicity counts (gated by module).
    side_board_count: int = 3
    n_side_stakes: int = 4
    n_end_stakes: int = 2
    bow_hoop_count: int = 5

    # Continuous local scales.
    wheel_radius_scale: float = 1.0
    front_rear_radius_ratio: float = 0.76
    half_track_scale: float = 1.0
    bed_len_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedDraftWagonConfig:
    wheel_config: WheelConfig
    spoke_count: int
    bed_sidewall: BedSidewall
    top_cover: TopCover
    palette_style: PaletteStyle

    side_board_count: int
    n_side_stakes: int
    n_end_stakes: int
    bow_hoop_count: int

    wheel_radius_scale: float
    front_rear_radius_ratio: float
    half_track_scale: float
    bed_len_scale: float

    # Derived geometry.
    n_axles: int
    has_bolster: bool
    bed_len: float
    bed_width: float
    half_track: float
    rear_wheel_r: float
    front_wheel_r: float
    rear_axle_z: float
    front_axle_z: float
    bed_floor_z: float
    side_wall_h: float
    axle_x: tuple[float, ...]  # per station, front→rear
    front_axle_x: float
    bolster_z: float


# --------------------------------------------------------------------------- #
# Seed sampling
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> DraftWagonConfig:
    """Deterministic procedural sampling for a draft wagon (seed=0 not special)."""
    rng = random.Random(seed)

    # (1) wheel_config — four_wheel high frequency.
    wheel_config = rng.choices(
        _WHEEL_CONFIGS, weights=(0.34, 0.46, 0.20), k=1
    )[0]
    # (3) spoke_count (axis 1, weighted).
    spoke_count = rng.choices(_SPOKE_CHOICES, weights=_SPOKE_WEIGHTS, k=1)[0]
    # (4) bed_sidewall.
    bed_sidewall = rng.choice(_SIDEWALLS)
    # (5) top_cover — resolve legal subset then weighted draw.
    legal = _legal_top_covers(wheel_config, bed_sidewall)
    top_cover = rng.choice(legal)
    palette_style = rng.choice(PALETTE_STYLES)

    # (6) multiplicity axes (only the relevant one matters per module, but we
    #     sample all so resolve_config is deterministic).
    side_board_count = rng.choices((2, 3, 4, 5, 6, 7), weights=(0.08, 0.30, 0.28, 0.16, 0.12, 0.06), k=1)[0]
    n_side_stakes = rng.choices((2, 3, 4, 5), weights=(0.15, 0.35, 0.30, 0.20), k=1)[0]
    n_end_stakes = rng.choices((1, 2, 3), weights=(0.40, 0.45, 0.15), k=1)[0]
    bow_hoop_count = rng.choices((3, 4, 5, 6, 7), weights=(0.10, 0.30, 0.30, 0.18, 0.12), k=1)[0]

    wheel_radius_scale = round(rng.uniform(0.85, 1.15), 4)
    front_rear_radius_ratio = round(rng.uniform(0.70, 0.82), 4)
    half_track_scale = round(rng.uniform(0.9, 1.1), 4)
    bed_len_scale = round(rng.uniform(0.85, 1.2), 4)

    return DraftWagonConfig(
        wheel_config=wheel_config,
        spoke_count=spoke_count,
        bed_sidewall=bed_sidewall,
        top_cover=top_cover,
        palette_style=palette_style,
        side_board_count=side_board_count,
        n_side_stakes=n_side_stakes,
        n_end_stakes=n_end_stakes,
        bow_hoop_count=bow_hoop_count,
        wheel_radius_scale=wheel_radius_scale,
        front_rear_radius_ratio=front_rear_radius_ratio,
        half_track_scale=half_track_scale,
        bed_len_scale=bed_len_scale,
    )


def _pick(value, choices, default):
    return value if value in choices else default


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(config: DraftWagonConfig | None = None) -> ResolvedDraftWagonConfig:
    cfg = config or DraftWagonConfig()

    wheel_config = _pick(cfg.wheel_config, _WHEEL_CONFIGS, "four_wheel_steered")
    spoke_count = int(_clamp(cfg.spoke_count if cfg.spoke_count is not None else 12, 6, 16))
    bed_sidewall = _pick(cfg.bed_sidewall, _SIDEWALLS, "low_three_plank_rails")

    # Resolve top_cover against the compatibility matrix; degrade illegal → open.
    legal = _legal_top_covers(wheel_config, bed_sidewall)
    top_cover = cfg.top_cover if cfg.top_cover in legal else "open_none"

    palette_style = _pick(cfg.palette_style, PALETTE_STYLES, "weathered_grey")

    side_board_count = int(_clamp(cfg.side_board_count, 2, 7))
    n_side_stakes = int(_clamp(cfg.n_side_stakes, 2, 8))
    n_end_stakes = int(_clamp(cfg.n_end_stakes, 1, 3))
    bow_hoop_count = int(_clamp(cfg.bow_hoop_count, 3, 7))

    wheel_radius_scale = _clamp(cfg.wheel_radius_scale, 0.85, 1.15)
    front_rear_radius_ratio = _clamp(cfg.front_rear_radius_ratio, 0.70, 0.82)
    half_track_scale = _clamp(cfg.half_track_scale, 0.9, 1.1)
    bed_len_scale = _clamp(cfg.bed_len_scale, 0.85, 1.2)

    # Derived station topology.
    if wheel_config == "single_axle_two_wheel":
        n_axles = 1
        has_bolster = False
    elif wheel_config == "four_wheel_steered":
        n_axles = 2
        has_bolster = True
    else:  # six_wheel_triple_axle
        n_axles = 3
        has_bolster = True

    # Bed footprint.
    base_len = 1.30
    bed_len = base_len * bed_len_scale
    bed_width = 0.78
    half_track = 0.50 * half_track_scale

    # Wheel radii. Rear is the big wheel; front (steered) smaller for identity.
    rear_wheel_r = 0.34 * wheel_radius_scale
    if has_bolster:
        front_wheel_r = rear_wheel_r * front_rear_radius_ratio
        # Guarantee front visually smaller than rear by >= 0.05.
        front_wheel_r = min(front_wheel_r, rear_wheel_r - 0.05)
    else:
        front_wheel_r = rear_wheel_r

    # axle_z = wheel_r + RIM_TUBE_R so the rim touches ground at z=0.
    rear_axle_z = rear_wheel_r + RIM_TUBE_R
    front_axle_z = front_wheel_r + RIM_TUBE_R

    # Bed floor sits above the tallest axle + clearance.
    bed_floor_z = max(rear_axle_z, front_axle_z) + rear_wheel_r * 0.55 + 0.06

    # Side wall height per module.
    side_wall_h = {
        "low_three_plank_rails": 0.30,
        "tall_back_wall": 0.34,
        "high_sided_grain_box": 0.55,
        "flat_rack_stake_bed": 0.28,
    }[bed_sidewall]

    # Axle station X positions (front→rear). Spacing inequality: every adjacent
    # axle gap must exceed the sum of the adjacent wheel radii + 2*RIM_TUBE_R so
    # rims never collide. We lay out from the rear, marching forward, and extend
    # the bed if the required wheelbase exceeds the nominal footprint.
    rear_axle_x = -bed_len * 0.5 + 0.22

    def _need(ra: float, rb: float) -> float:
        return ra + rb + 2.0 * RIM_TUBE_R + 0.04

    if n_axles == 1:
        axle_x = (rear_axle_x,)
    elif n_axles == 2:
        front_axle_x0 = rear_axle_x + _need(front_wheel_r, rear_wheel_r)
        front_axle_x0 = max(front_axle_x0, bed_len * 0.5 - 0.22)
        axle_x = (front_axle_x0, rear_axle_x)
    else:
        mid_axle_x = rear_axle_x + _need(rear_wheel_r, rear_wheel_r)
        front_axle_x0 = mid_axle_x + _need(front_wheel_r, rear_wheel_r)
        axle_x = (front_axle_x0, mid_axle_x, rear_axle_x)
        # Grow the bed so the front axle stays inside the footprint.
        bed_len = max(bed_len, (front_axle_x0 + 0.22) * 2.0)

    front_axle_x = axle_x[0]

    bolster_z = bed_floor_z - 0.06

    return ResolvedDraftWagonConfig(
        wheel_config=wheel_config,
        spoke_count=spoke_count,
        bed_sidewall=bed_sidewall,
        top_cover=top_cover,
        palette_style=palette_style,
        side_board_count=side_board_count,
        n_side_stakes=n_side_stakes,
        n_end_stakes=n_end_stakes,
        bow_hoop_count=bow_hoop_count,
        wheel_radius_scale=wheel_radius_scale,
        front_rear_radius_ratio=front_rear_radius_ratio,
        half_track_scale=half_track_scale,
        bed_len_scale=bed_len_scale,
        n_axles=n_axles,
        has_bolster=has_bolster,
        bed_len=bed_len,
        bed_width=bed_width,
        half_track=half_track,
        rear_wheel_r=rear_wheel_r,
        front_wheel_r=front_wheel_r,
        rear_axle_z=rear_axle_z,
        front_axle_z=front_axle_z,
        bed_floor_z=bed_floor_z,
        side_wall_h=side_wall_h,
        axle_x=axle_x,
        front_axle_x=front_axle_x,
        bolster_z=bolster_z,
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Slot/module picks for module_topology_diversity. Includes the N
    multiplicity buckets that change the part/visual count."""
    r = resolve_config(config_from_seed(seed))
    spoke_bucket = (
        "spokes_low" if r.spoke_count <= 8 else "spokes_mid" if r.spoke_count <= 12 else "spokes_high"
    )
    if r.bed_sidewall == "flat_rack_stake_bed":
        wall_bucket = f"stakes_{r.n_side_stakes}x{r.n_end_stakes}"
    else:
        wall_bucket = f"boards_{r.side_board_count}"
    cover_bucket = r.top_cover
    if r.top_cover == "canvas_bow_tilt_cover":
        cover_bucket = f"canvas_hoops_{r.bow_hoop_count}"
    return [
        ("wheel_config", r.wheel_config),
        ("spoke_count", spoke_bucket),
        ("bed_sidewall", f"{r.bed_sidewall}:{wall_bucket}"),
        ("top_cover", cover_bucket),
    ]


# --------------------------------------------------------------------------- #
# Wheel construction — shared spoked-wheel helper (Slot B spoke_count).
# Felloe (rim) = torus in XZ plane; radial Cylinder spokes hub→felloe; hub +
# hub band + off-axis marker. Spin axis = local +Y.
# --------------------------------------------------------------------------- #
def _wheel_visuals(part, prefix: str, radius: float, spoke_count: int, mats) -> None:
    """Author a spoked wooden wheel centered on the axle (spins about +Y)."""
    # Felloe rim: torus around XZ plane (axle along Y).
    felloe = TorusGeometry(radius - RIM_TUBE_R, RIM_TUBE_R, radial_segments=12, tubular_segments=40)
    felloe = felloe.rotate_x(pi / 2.0)
    part.visual(mesh_from_geometry(felloe, f"{prefix}_felloe"), material=mats["wood"], name=f"{prefix}_felloe", material_class_id="wood.natural_generic")

    # Iron tyre band: thin torus just outside the felloe (parent visual decoration).
    tyre = TorusGeometry(radius - RIM_TUBE_R, RIM_TUBE_R * 0.45, radial_segments=10, tubular_segments=40)
    tyre = tyre.rotate_x(pi / 2.0)
    part.visual(mesh_from_geometry(tyre, f"{prefix}_tyre"), material=mats["iron"], name=f"{prefix}_tyre", material_class_id="metal.cast_iron_bare")

    # Hub: short cylinder along the axle (Y).
    hub = CylinderGeometry(HUB_R, 0.14, radial_segments=18).rotate_x(pi / 2.0)
    part.visual(mesh_from_geometry(hub, f"{prefix}_hub"), material=mats["dark"], name=f"{prefix}_hub", material_class_id="wood.walnut_dark")
    # Iron hub band (decoration → visual on the wheel part).
    hub_band = CylinderGeometry(HUB_R * 1.12, 0.05, radial_segments=18).rotate_x(pi / 2.0)
    part.visual(mesh_from_geometry(hub_band, f"{prefix}_hub_band"), material=mats["iron"], name=f"{prefix}_hub_band", material_class_id="metal.cast_iron_bare")

    # Spokes: radial cylinders hub flange → felloe inner. Inner end embeds inside
    # the hub radius so hub→spokes→felloe is one connected island.
    spoke_inner = HUB_R - 0.012
    spoke_outer = radius - RIM_TUBE_R - 0.004
    length = spoke_outer - spoke_inner
    r_mid = (spoke_inner + spoke_outer) * 0.5
    spoke_r = max(0.012, radius * 0.045)
    for i in range(spoke_count):
        a = 2.0 * pi * i / spoke_count + 0.13  # offset so none lies on an axis
        cx, cz = cos(a) * r_mid, sin(a) * r_mid
        sp = CylinderGeometry(spoke_r, length, radial_segments=6)
        sp = sp.rotate_y(pi / 2.0 - a)
        sp = sp.translate(cx, 0.0, cz)
        part.visual(mesh_from_geometry(sp, f"{prefix}_spoke_{i}"), material=mats["wood"], name=f"{prefix}_spoke_{i}", material_class_id="wood.natural_generic")

    # Off-axis marker so roll is detectable by AABB (and identity-distinct).
    part.visual(
        Box((0.026, 0.026, 0.05)),
        origin=Origin(xyz=(0.0, 0.0, spoke_outer)),
        material=mats["iron"],
        name=f"{prefix}_marker", material_class_id="metal.cast_iron_bare",
    )
    # Hub end-cap on the axle centerline so the roll-joint origin carries solid
    # geometry (the bare hub is hollow on its axis).
    part.visual(
        Cylinder(radius=0.030, length=0.16),
        origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}_hub_cap", material_class_id="wood.walnut_dark",
    )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=radius, length=0.14), mass=6.0, origin=Origin(rpy=(pi / 2.0, 0.0, 0.0))
    )


# --------------------------------------------------------------------------- #
# Bed / chassis (root body) construction.
# --------------------------------------------------------------------------- #
def _build_body_core(body, r: ResolvedDraftWagonConfig, mats) -> None:
    """Floor planks + frame rails + axle stubs (Slot C-independent core)."""
    floor_top = r.bed_floor_z + FLOOR_THK
    half_w = r.bed_width * 0.5
    half_l = r.bed_len * 0.5

    body.inertial = Inertial.from_geometry(
        Box((r.bed_len, r.bed_width, 0.30)),
        mass=40.0,
        origin=Origin(xyz=(0.0, 0.0, r.bed_floor_z + 0.10)),
    )

    # Floor planks running along X (loop-emitted multiplicity, but fixed count =
    # structural floor, not a sampled axis).
    n_floor = 6
    plank_w = r.bed_width / n_floor
    for i in range(n_floor):
        y = -half_w + plank_w * (i + 0.5)
        body.visual(
            Box((r.bed_len, plank_w * 0.94, FLOOR_THK)),
            origin=Origin(xyz=(0.0, y, r.bed_floor_z + FLOOR_THK * 0.5)),
            material=mats["plank"],
            name=f"floor_plank_{i}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.plank_floor"),
        )

    # Two longitudinal under-bed frame rails (carry the axles).
    for sign, sfx in ((1.0, "0"), (-1.0, "1")):
        body.visual(
            Box((r.bed_len * 1.02, 0.07, 0.09)),
            origin=Origin(xyz=(0.0, sign * half_w * 0.7, r.bed_floor_z - 0.02)),
            material=mats["dark"],
            name=f"frame_rail_{sfx}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
        )

    # Rear (and mid) axle stubs ON the body. Front station axle lives on the
    # bolster (or, for 2-wheel, the single rear axle is here).
    body_stations = range(1, r.n_axles) if r.has_bolster else range(r.n_axles)
    for idx in body_stations:
        ax = r.axle_x[idx]
        # axle beam across the track at axle height. It ends just inboard of the
        # wheel hubs, then short stubs reach into each hub bore (captured pin).
        body.visual(
            Cylinder(radius=0.045, length=r.half_track * 2.0 - 0.14),
            origin=Origin(xyz=(ax, 0.0, r.rear_axle_z), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["dark"],
            name=f"axle_beam_{idx}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
        )
        for sign in (1.0, -1.0):
            body.visual(
                Cylinder(radius=0.034, length=0.20),
                origin=Origin(
                    xyz=(ax, sign * r.half_track, r.rear_axle_z), rpy=(pi / 2.0, 0.0, 0.0)
                ),
                material=mats["iron"],
                name=f"axle_stub_{idx}_{'l' if sign > 0 else 'r'}", material_class_id="metal.cast_iron_bare",
            )
        # iron bolster strap over the rail at the axle (decoration → visual).
        body.visual(
            Box((0.10, r.bed_width * 0.9, 0.03)),
            origin=Origin(xyz=(ax, 0.0, r.bed_floor_z - 0.05)),
            material=mats["iron"],
            name=f"axle_clamp_{idx}", material_class_id="metal.cast_iron_bare",
        )
        # Axle hanger: vertical post tying the axle beam UP into the floor planks
        # so the axle is one connected island with the body.
        hang_top = r.bed_floor_z + FLOOR_THK
        hang_h = hang_top - r.rear_axle_z
        body.visual(
            Box((0.10, 0.12, hang_h)),
            origin=Origin(xyz=(ax, 0.0, (hang_top + r.rear_axle_z) * 0.5)),
            material=mats["dark"],
            name=f"axle_hanger_{idx}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
        )


def _build_kingpin(body, r: ResolvedDraftWagonConfig, mats) -> None:
    """Kingpin boss under the front of the bed (turntable seat for the bolster)."""
    body.visual(
        Cylinder(radius=0.10, length=0.10),
        origin=Origin(xyz=(r.front_axle_x, 0.0, r.bolster_z + 0.05)),
        material=mats["iron"],
        name="kingpin_boss", material_class_id="metal.cast_iron_bare",
    )
    # Front body cross-beam the bolster turntable rides under.
    body.visual(
        Box((0.14, r.bed_width * 0.92, 0.08)),
        origin=Origin(xyz=(r.front_axle_x, 0.0, r.bed_floor_z - 0.04)),
        material=mats["dark"],
        name="front_cross_beam", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
    )


# --- Slot C: bed sidewall modules (all body visuals; loop-emitted) ----------
def _build_sidewall(body, r: ResolvedDraftWagonConfig, mats) -> None:
    floor_top = r.bed_floor_z + FLOOR_THK
    half_w = r.bed_width * 0.5
    half_l = r.bed_len * 0.5
    wall = r.bed_sidewall

    if wall == "flat_rack_stake_bed":
        _build_stake_bed(body, r, mats)
        return

    # Plank/board walls: horizontal planks stacked to side_wall_h.
    n = r.side_board_count
    board_h = r.side_wall_h / n
    board_t = 0.035
    # Side walls (along X).
    for side, sy in (("left", half_w - board_t * 0.5), ("right", -(half_w - board_t * 0.5))):
        n_here = n
        for k in range(n_here):
            z = floor_top + board_h * (k + 0.5)
            body.visual(
                Box((r.bed_len * 0.98, board_t, board_h * 0.94)),
                origin=Origin(xyz=(0.0, sy, z)),
                material=mats["plank"],
                name=f"{side}_side_plank_{k}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.plank_floor"),
            )
    # End walls (along Y). A drop-tailgate wagon must NOT also have a fixed
    # rear wall; the tailgate part is the rear closure.  We keep only a low
    # hinge sill on the body for the tailgate to mate to.
    if r.top_cover == "drop_tailgate_open_box":
        body.visual(
            Box((0.06, r.bed_width * 0.98, 0.055)),
            origin=Origin(xyz=(-(half_l - 0.015), 0.0, floor_top + 0.0275)),
            material=mats["dark"],
            name="tailgate_hinge_sill", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
        )

    # End walls (along Y). tall_back_wall: front low (3) + back tall (n+1).
    if wall == "tall_back_wall":
        ends = (("front", half_l - board_t * 0.5, 2), ("back", -(half_l - board_t * 0.5), n + 1))
    else:
        ends = (("front", half_l - board_t * 0.5, n), ("back", -(half_l - board_t * 0.5), n))
    for end, ex, n_end in ends:
        if end == "back" and r.top_cover == "drop_tailgate_open_box":
            continue
        for k in range(n_end):
            z = floor_top + board_h * (k + 0.5)
            body.visual(
                Box((board_t, r.bed_width * 0.98, board_h * 0.94)),
                origin=Origin(xyz=(ex, 0.0, z)),
                material=mats["plank"],
                name=f"{end}_end_plank_{k}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.plank_floor"),
            )
    # Corner posts. Back posts grow taller when the back wall is raised so the
    # top back plank stays anchored (tall_back_wall).
    back_h = r.side_wall_h
    if wall == "tall_back_wall":
        back_h = board_h * (n + 1) + board_t
    for cx, cxn, ph in ((half_l - 0.03, "f", r.side_wall_h), (-(half_l - 0.03), "b", back_h)):
        for cy, cyn in ((half_w - 0.03, "l"), (-(half_w - 0.03), "r")):
            body.visual(
                Box((0.05, 0.05, ph)),
                origin=Origin(xyz=(cx, cy, floor_top + ph * 0.5)),
                material=mats["dark"],
                name=f"corner_post_{cxn}{cyn}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
            )


def _build_stake_bed(body, r: ResolvedDraftWagonConfig, mats) -> None:
    """Flat-rack stake deck: low edge rails plus sparse removable stakes.

    This is intentionally not a forest of tall round posts.  Real flat racks
    have edge pockets and a few stakes on the perimeter, leaving the cargo deck
    usable and readable as an open wagon bed.
    """
    floor_top = r.bed_floor_z + FLOOR_THK
    half_w = r.bed_width * 0.5
    half_l = r.bed_len * 0.5
    h = r.side_wall_h

    # Low perimeter rub rails give the rack a purpose and keep the deck from
    # reading as a bare plank with random vertical cylinders.
    rail_h = 0.055
    for side, sy in (("left", half_w - 0.025), ("right", -(half_w - 0.025))):
        body.visual(
            Box((r.bed_len * 0.96, 0.045, rail_h)),
            origin=Origin(xyz=(0.0, sy, floor_top + rail_h * 0.5)),
            material=mats["dark"],
            name=f"{side}_rack_edge_rail", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
        )
    for end, ex in (("front", half_l - 0.025), ("back", -(half_l - 0.025))):
        body.visual(
            Box((0.045, r.bed_width * 0.92, rail_h)),
            origin=Origin(xyz=(ex, 0.0, floor_top + rail_h * 0.5)),
            material=mats["dark"],
            name=f"{end}_rack_edge_rail", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
        )

    def _stake(x: float, y: float, name: str) -> None:
        body.visual(
            Box((0.055, 0.055, h)),
            origin=Origin(xyz=(x, y, floor_top + h * 0.5)),
            material=mats["wood"],
            name=name, material_class_id="wood.natural_generic",
        )
        body.visual(
            Box((0.075, 0.075, 0.030)),
            origin=Origin(xyz=(x, y, floor_top + 0.015)),
            material=mats["iron"],
            name=f"{name}_stake_pocket", material_class_id="metal.cast_iron_bare",
        )

    side_count = max(2, min(r.n_side_stakes, 4))
    side_xs = [
        -half_l + (2.0 * half_l) * (s + 1) / (side_count + 1)
        for s in range(side_count)
    ]
    for side, sy in (("left", half_w - 0.055), ("right", -(half_w - 0.055))):
        for s, x in enumerate(side_xs):
            _stake(x, sy, f"{side}_stake_{s}")
        body.visual(
            Box((r.bed_len * 0.82, 0.038, 0.045)),
            origin=Origin(xyz=(0.0, sy, floor_top + h * 0.72)),
            material=mats["wood"],
            name=f"{side}_upper_stake_rail", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "dark_walnut", "painted_red", "pine_blond", "green_painted_iron"} else "wood.oak"),
        )

    for end, ex in (("front", half_l - 0.055), ("back", -(half_l - 0.055))):
        for side, sy in (("left", half_w - 0.055), ("right", -(half_w - 0.055))):
            _stake(ex, sy, f"{end}_{side}_corner_stake")


# --- Slot D: top cover modules ----------------------------------------------
def _build_top_cover(body, r: ResolvedDraftWagonConfig, mats) -> None:
    """gabled/canvas covers are body visuals; open/tailgate emit nothing here."""
    floor_top = r.bed_floor_z + FLOOR_THK
    wall_top_z = floor_top + r.side_wall_h
    half_w = r.bed_width * 0.5
    half_l = r.bed_len * 0.5

    if r.top_cover == "gabled_plank_roof":
        rise = 0.30
        ridge_z = wall_top_z + rise
        # ridge beam at the apex.
        body.visual(
            Box((r.bed_len * 0.92, 0.06, 0.06)),
            origin=Origin(xyz=(0.0, 0.0, ridge_z)),
            material=mats["dark"],
            name="ridge_beam", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
        )
        # Roof panels: each spans from the eave (at the wall top, y=±half_w) up to
        # the ridge (y=0, z=ridge_z). Center + tilt so the lower edge sits ON the
        # wall top (overlap) and the upper edge meets the ridge.
        run = half_w
        panel_len = (run * run + rise * rise) ** 0.5 + 0.04
        slope = -1.0 * (rise / run)  # roll so +y side drops outward
        from math import atan2
        roll = atan2(rise, run)
        for side, sy in (("left", 1.0), ("right", -1.0)):
            body.visual(
                Box((r.bed_len * 0.92, panel_len, 0.04)),
                origin=Origin(
                    xyz=(0.0, sy * half_w * 0.5, wall_top_z + rise * 0.5),
                    rpy=(-sy * roll, 0.0, 0.0),
                ),
                material=mats["wood"],
                name=f"{side}_roof_panel", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "dark_walnut", "painted_red", "pine_blond", "green_painted_iron"} else "wood.oak"),
            )
        # Gable end triangles (plank fills) reaching from the wall top to the ridge.
        for end, ex in (("front", half_l * 0.9), ("back", -half_l * 0.9)):
            body.visual(
                Box((0.05, r.bed_width * 0.5, rise + 0.06)),
                origin=Origin(xyz=(ex, 0.0, wall_top_z + rise * 0.5)),
                material=mats["wood"],
                name=f"{end}_gable", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "dark_walnut", "painted_red", "pine_blond", "green_painted_iron"} else "wood.oak"),
            )

    elif r.top_cover == "canvas_bow_tilt_cover":
        bow_r = half_w
        n = r.bow_hoop_count
        hoop_span = r.bed_len * 0.84
        for i in range(n):
            if n > 1:
                x = -hoop_span * 0.5 + hoop_span * i / (n - 1)
            else:
                x = 0.0
            # True semicircular bow from left wall top to right wall top.
            pts = [
                (x, bow_r * cos(pi * t / 12.0), wall_top_z + bow_r * sin(pi * t / 12.0))
                for t in range(13)
            ]
            hoop = tube_from_spline_points(
                pts,
                radius=0.018,
                samples_per_segment=2,
                radial_segments=8,
                closed_spline=False,
                up_hint=(1.0, 0.0, 0.0),
            )
            body.visual(mesh_from_geometry(hoop, f"hoop_{i}"), material=mats["wood"], name=f"hoop_{i}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "dark_walnut", "painted_red", "pine_blond", "green_painted_iron"} else "wood.oak"))

        # Curved canvas skin over the upper half of the bow, with modest side
        # skirts.  This avoids the old hard rectangular cap and the full-ring
        # hoops that punched visual "holes" through the sides.
        x0 = -hoop_span * 0.55
        x1 = hoop_span * 0.55
        theta_steps = 14
        vertices: list[tuple[float, float, float]] = []
        for x in (x0, x1):
            for t in range(theta_steps + 1):
                theta = pi * t / theta_steps
                y = bow_r * cos(theta)
                z = wall_top_z + bow_r * sin(theta) + 0.018
                vertices.append((x, y, z))
        faces: list[tuple[int, int, int]] = []
        row = theta_steps + 1
        for t in range(theta_steps):
            a = t
            b = t + 1
            c = row + t + 1
            d = row + t
            faces.append((a, b, c))
            faces.append((a, c, d))
        canvas = MeshGeometry(vertices=vertices, faces=faces)
        body.visual(mesh_from_geometry(canvas, "canvas_tilt"), material=mats["canvas"], name="canvas_tilt", material_class_id="fabric.canvas")

        skirt_h = bow_r * 0.42
        for side, sy in (("left", 1.0), ("right", -1.0)):
            body.visual(
                Box((hoop_span * 1.10, 0.035, skirt_h)),
                origin=Origin(xyz=(0.0, sy * half_w, wall_top_z - skirt_h * 0.5)),
                material=mats["canvas"],
                name=f"canvas_{side}_skirt", material_class_id="fabric.canvas",
            )


# --------------------------------------------------------------------------- #
# Bolster (steered front axle carrier) + draw poles. REVOLUTE about +Z.
# --------------------------------------------------------------------------- #
def _build_bolster(bolster, r: ResolvedDraftWagonConfig, mats) -> None:
    """Front bolster part authored in its own local frame (origin = kingpin).

    Carries: bolster beam (turntable plate), front axle beam, draw poles +
    swingletree + rope tie (all bolster visuals so they steer with it). Front
    wheels chain onto this part."""
    # Local frame: origin at kingpin (front_axle_x, 0, bolster_z) in world.
    # Turntable plate straddling the joint origin (local 0,0,0) so the origin
    # carries geometry and it seats under the kingpin boss.
    bolster.inertial = Inertial.from_geometry(
        Box((0.40, r.half_track * 2.2, 0.20)),
        mass=10.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    bolster.visual(
        Cylinder(radius=0.11, length=0.06),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["iron"],
        name="bolster_beam", material_class_id="metal.cast_iron_bare",
    )
    # Front axle beam across the track at the front-wheel axle height. Ends just
    # inboard of the front wheels; short stubs reach into each hub bore.
    axle_local_z = r.front_axle_z - r.bolster_z
    bolster.visual(
        Cylinder(radius=0.042, length=r.half_track * 2.0 - 0.14),
        origin=Origin(xyz=(0.0, 0.0, axle_local_z), rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="front_axle", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
    )
    for sign in (1.0, -1.0):
        bolster.visual(
            Cylinder(radius=0.034, length=0.20),
            origin=Origin(xyz=(0.0, sign * r.half_track, axle_local_z), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["iron"],
            name=f"front_stub_{'l' if sign > 0 else 'r'}", material_class_id="metal.cast_iron_bare",
        )
    # Bolster vertical post tying the turntable plate (z≈0) UP to the front axle
    # (z=axle_local_z): one connected island. Spans the full height and overlaps
    # both ends. Kept narrow in Y so it stays inboard of the front wheel spokes.
    bolster.visual(
        Box((0.12, 0.16, abs(axle_local_z) + 0.06)),
        origin=Origin(xyz=(0.0, 0.0, axle_local_z * 0.5)),
        material=mats["dark"],
        name="bolster_cross", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
    )
    # Draw poles reaching forward from the axle (decoration on bolster → steer
    # with it). They start AT the axle (x=0) so they weld to the bolster.
    fwd_x = r.bed_len * 0.5
    for sign, sfx in ((1.0, "0"), (-1.0, "1")):
        bolster.visual(
            Box((fwd_x, 0.05, 0.05)),
            origin=Origin(xyz=(fwd_x * 0.5 - 0.02, sign * 0.10, axle_local_z)),
            material=mats["wood"],
            name=f"draw_pole_{sfx}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "dark_walnut", "painted_red", "pine_blond", "green_painted_iron"} else "wood.oak"),
        )
    # Swingletree + rope tie spanning the two poles (decoration; overlaps both).
    bolster.visual(
        Box((0.05, 0.34, 0.05)),
        origin=Origin(xyz=(fwd_x - 0.06, 0.0, axle_local_z)),
        material=mats["dark"],
        name="swingletree", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
    )
    bolster.visual(
        Cylinder(radius=0.02, length=0.30),
        origin=Origin(xyz=(fwd_x * 0.5, 0.0, axle_local_z + 0.04), rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["rope"],
        name="rope_tie", material_class_id="organic.woven_plant_fiber",
    )


# --------------------------------------------------------------------------- #
# Drop tailgate (Slot D=drop_tailgate). REVOLUTE about -Y at rear bottom edge.
# --------------------------------------------------------------------------- #
def _build_tailgate(tailgate, r: ResolvedDraftWagonConfig, mats) -> None:
    """Rear tailgate authored in local frame: hinge at local (0,0,0) along the
    rear bottom edge; planks rise in +Z (closed pose seals the rear opening)."""
    h = r.side_wall_h
    n = 3
    plank_h = h / n
    plank_t = 0.04
    tailgate.inertial = Inertial.from_geometry(
        Box((plank_t, r.bed_width, h)),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
    )
    for k in range(n):
        z = plank_h * (k + 0.5)
        tailgate.visual(
            Box((plank_t, r.bed_width * 0.98, plank_h * 0.94)),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["plank"],
            name=f"tailgate_plank_{k}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.plank_floor"),
        )
    # Battens + iron hinge straps (decoration on the tailgate part).
    for sign, sfx in ((1.0, "0"), (-1.0, "1")):
        tailgate.visual(
            Box((plank_t * 0.6, 0.05, h * 0.9)),
            origin=Origin(xyz=(plank_t * 0.5, sign * r.bed_width * 0.35, h * 0.5)),
            material=mats["dark"],
            name=f"batten_{sfx}", material_class_id=("wood.rustic_weathered" if r.palette_style in {"weathered_grey", "painted_red", "green_painted_iron"} else "wood.walnut_dark"),
        )
        tailgate.visual(
            Box((plank_t * 1.2, 0.04, 0.10)),
            origin=Origin(xyz=(0.0, sign * r.bed_width * 0.30, 0.02)),
            material=mats["iron"],
            name=f"hinge_strap_{sfx}", material_class_id="metal.cast_iron_bare",
        )


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #
def build_draft_wagon(
    config: DraftWagonConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="draft_wagon", assets=assets)

    mats: dict[str, object] = {}
    for token, rgba in PALETTES[r.palette_style].items():
        mats[token] = model.material(token, rgba=rgba)

    # ---- BODY (root: chassis/bed) ----
    body = model.part("body")
    _build_body_core(body, r, mats)
    _build_sidewall(body, r, mats)
    _build_top_cover(body, r, mats)
    if r.has_bolster:
        _build_kingpin(body, r, mats)

    # ---- BOLSTER (steered) ----
    bolster = None
    if r.has_bolster:
        bolster = model.part("front_bolster")
        _build_bolster(bolster, r, mats)
        model.articulation(
            "front_steer",
            ArticulationType.REVOLUTE,
            parent=body,
            child=bolster,
            origin=Origin(xyz=(r.front_axle_x, 0.0, r.bolster_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=60.0, velocity=2.0, lower=-0.6, upper=0.6),
            mating=MatingContract(
                parent_face_geometry="kingpin_boss",
                parent_face_side="negative_z",
                child_face_geometry="bolster_beam",
                child_face_side="positive_z",
                contact_tol=0.06,
            ),
        )

    # ---- WHEELS (loop-emitted per station × 2 sides) ----
    for i in range(r.n_axles):
        ax = r.axle_x[i]
        is_front_station = r.has_bolster and i == 0
        radius = r.front_wheel_r if is_front_station else r.rear_wheel_r
        axle_z = r.front_axle_z if is_front_station else r.rear_axle_z
        for side, sy in (("l", 1.0), ("r", -1.0)):
            wheel = model.part(f"wheel_{i}_{side}")
            _wheel_visuals(wheel, f"wheel_{i}_{side}", radius, r.spoke_count, mats)
            if is_front_station:
                # Child of bolster: origin in bolster LOCAL frame.
                parent = bolster
                local_z = axle_z - r.bolster_z
                origin = Origin(xyz=(0.0, sy * r.half_track, local_z))
            else:
                parent = body
                origin = Origin(xyz=(ax, sy * r.half_track, axle_z))
            model.articulation(
                f"spin_{i}_{side}",
                ArticulationType.CONTINUOUS,
                parent=parent,
                child=wheel,
                origin=origin,
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=10.0, velocity=40.0),
            )

    # ---- TAILGATE (Slot D=drop_tailgate) ----
    if r.top_cover == "drop_tailgate_open_box":
        tailgate = model.part("tailgate")
        _build_tailgate(tailgate, r, mats)
        floor_top = r.bed_floor_z + FLOOR_THK
        model.articulation(
            "tailgate_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=tailgate,
            origin=Origin(xyz=(-r.bed_len * 0.5, 0.0, floor_top)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=30.0, velocity=2.0, lower=0.0, upper=pi / 2.0),
            mating=MatingContract(
                parent_face_geometry="tailgate_hinge_sill",
                parent_face_side="negative_x",
                child_face_geometry="tailgate_plank_0",
                child_face_side="positive_x",
                contact_tol=0.08,
            ),
        )

    return model


def build_seeded_draft_wagon(seed: int) -> ArticulatedObject:
    return build_draft_wagon(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _center(aabb):
    mn, mx = aabb
    return ((mn[0] + mx[0]) * 0.5, (mn[1] + mx[1]) * 0.5, (mn[2] + mx[2]) * 0.5)


def run_draft_wagon_tests(model: ArticulatedObject, config: DraftWagonConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    body = model.get_part("body")

    # --- Declare captured/seated overlaps (hub on axle, kingpin turntable). ---
    # Each wheel hub is captured on its parent's axle stub (the stub runs through
    # the hub bore — an intentional captured pin).
    for i in range(r.n_axles):
        is_front = r.has_bolster and i == 0
        parent_name = "front_bolster" if is_front else "body"
        for side in ("l", "r"):
            wp = f"wheel_{i}_{side}"
            ctx.allow_overlap(
                model.get_part(parent_name),
                model.get_part(wp),
                reason="Wheel hub is captured on the axle stub — the stub runs through the hub bore.",
            )

    if r.has_bolster:
        bolster = model.get_part("front_bolster")
        # Kingpin turntable: bolster beam seats into the body kingpin boss.
        for elem_a, elem_b, why in (
            ("kingpin_boss", "bolster_beam", "Kingpin boss seats into the bolster turntable plate."),
            ("kingpin_boss", "front_cross_beam", "Kingpin boss is captured in the front cross beam."),
        ):
            ctx.allow_overlap(body, bolster, elem_a=elem_a, elem_b=elem_b, reason=why)
        # Bolster turntable rides under the front of the bed (captured).
        ctx.allow_overlap(
            body, bolster, reason="Front bolster turntable rides captured under the front of the bed."
        )

    if r.top_cover == "drop_tailgate_open_box":
        ctx.allow_overlap(
            body, model.get_part("tailgate"),
            reason="Tailgate hinge straps wrap the rear bottom edge of the bed (captured barrel).",
        )

    # --- Baseline hard QC. ---
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.060)
    ctx.fail_if_joint_mating_has_gap()

    # --- Identity checks. ---
    # Wheel count matches the station topology.
    wheel_parts = sorted(p.name for p in model.parts if p.name.startswith("wheel_"))
    ctx.check(
        "wheel_count_matches_config",
        len(wheel_parts) == r.n_axles * 2,
        details=f"wheels={wheel_parts}, expected {r.n_axles * 2}",
    )

    # Every wheel spin is CONTINUOUS about world +Y, unbounded, and rolls in place.
    for i in range(r.n_axles):
        for side in ("l", "r"):
            jn = f"spin_{i}_{side}"
            joint = model.get_articulation(jn)
            ctx.check(
                f"{jn}_is_continuous_Y",
                joint.articulation_type == ArticulationType.CONTINUOUS
                and tuple(joint.axis) == (0.0, 1.0, 0.0),
                details=f"type={joint.articulation_type}, axis={joint.axis}",
            )
            lim = joint.motion_limits
            ctx.check(
                f"{jn}_unbounded",
                lim is None or (lim.lower is None and lim.upper is None),
                details=f"limits={lim}",
            )
            # Roll: rim marker swings about the axle.
            wp = f"wheel_{i}_{side}"
            m0 = _center(ctx.part_element_world_aabb(model.get_part(wp), elem=f"{wp}_marker"))
            with ctx.pose({joint: pi / 2.0}):
                m1 = _center(ctx.part_element_world_aabb(model.get_part(wp), elem=f"{wp}_marker"))
            moved = ((m1[0] - m0[0]) ** 2 + (m1[2] - m0[2]) ** 2) ** 0.5
            ctx.check(f"{wp}_rolls", moved > 0.10, details=f"marker moved {moved:.3f}")

    # Wheels touch ground at z≈0.
    for i in range(r.n_axles):
        for side in ("l", "r"):
            wp = f"wheel_{i}_{side}"
            aabb = ctx.part_world_aabb(model.get_part(wp))
            ctx.check(
                f"{wp}_touches_ground",
                aabb[0][2] < 0.05,
                details=f"wheel bottom z={aabb[0][2]:.3f}",
            )

    # Steering: REVOLUTE about +Z, yaws the front wheels.
    if r.has_bolster:
        steer = model.get_articulation("front_steer")
        ctx.check(
            "front_steer_is_revolute_Z",
            steer.articulation_type == ArticulationType.REVOLUTE
            and tuple(steer.axis) == (0.0, 0.0, 1.0),
            details=f"type={steer.articulation_type}, axis={steer.axis}",
        )
        fw = model.get_part("wheel_0_l")
        c0 = _center(ctx.part_world_aabb(fw))
        with ctx.pose({steer: 0.6}):
            c1 = _center(ctx.part_world_aabb(fw))
        moved = ((c1[0] - c0[0]) ** 2 + (c1[1] - c0[1]) ** 2) ** 0.5
        ctx.check("steering_yaws_front_wheels", moved > 0.05, details=f"front wheel moved {moved:.3f}")

        # Front wheels visually smaller than rear (>= 0.05 diameter).
        fw_ext = _ext(ctx.part_world_aabb(model.get_part("wheel_0_l")))
        rw_ext = _ext(ctx.part_world_aabb(model.get_part(f"wheel_{r.n_axles - 1}_l")))
        fw_d = max(fw_ext[0], fw_ext[2])
        rw_d = max(rw_ext[0], rw_ext[2])
        ctx.check(
            "front_wheel_smaller_than_rear",
            rw_d - fw_d > 0.08,
            details=f"front_d={fw_d:.3f}, rear_d={rw_d:.3f}",
        )

    # Tailgate: REVOLUTE about -Y, drops down.
    if r.top_cover == "drop_tailgate_open_box":
        body_visual_names = {visual.name for visual in body.visuals}
        ctx.check(
            "drop_tailgate_has_no_fixed_rear_wall",
            not any(name.startswith("back_end_plank_") for name in body_visual_names),
            details="drop-tailgate variants must leave the rear opening to the articulated tailgate",
        )
        ctx.check(
            "drop_tailgate_has_body_hinge_sill",
            "tailgate_hinge_sill" in body_visual_names,
            details=f"body visuals include {sorted(body_visual_names)}",
        )
        hinge = model.get_articulation("tailgate_hinge")
        ctx.check(
            "tailgate_hinge_is_revolute_Y",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and tuple(hinge.axis) == (0.0, -1.0, 0.0),
            details=f"type={hinge.articulation_type}, axis={hinge.axis}",
        )
        tg = model.get_part("tailgate")
        t0 = _center(ctx.part_world_aabb(tg))
        with ctx.pose({hinge: pi / 2.0}):
            t1 = _center(ctx.part_world_aabb(tg))
        moved = ((t1[0] - t0[0]) ** 2 + (t1[2] - t0[2]) ** 2) ** 0.5
        ctx.check("tailgate_drops", moved > 0.05, details=f"tailgate moved {moved:.3f}")

    # Human-readability checks for modules that otherwise pass pure joint QC.
    if r.top_cover == "canvas_bow_tilt_cover":
        wall_top_z = r.bed_floor_z + FLOOR_THK + r.side_wall_h
        for i in range(r.bow_hoop_count):
            aabb = ctx.part_element_world_aabb(body, elem=f"hoop_{i}")
            ctx.check(
                f"hoop_{i}_is_upper_semicircle_not_full_ring",
                aabb[0][2] >= wall_top_z - 0.04,
                details=f"hoop bottom z={aabb[0][2]:.3f}, wall_top_z={wall_top_z:.3f}",
            )

    if r.bed_sidewall == "flat_rack_stake_bed":
        body_visual_names = {visual.name for visual in body.visuals}
        ctx.check(
            "flat_rack_has_edge_rails",
            {
                "left_rack_edge_rail",
                "right_rack_edge_rail",
                "front_rack_edge_rail",
                "back_rack_edge_rail",
            }.issubset(body_visual_names),
            details="flat racks need low perimeter rails so stake posts read as useful rack hardware",
        )
        vertical_stakes = [
            name for name in body_visual_names
            if name.endswith("_corner_stake")
            or (
                name.startswith(("left_stake_", "right_stake_"))
                and not name.endswith("_stake_pocket")
            )
        ]
        ctx.check(
            "flat_rack_sparse_perimeter_stakes",
            len(vertical_stakes) <= 12,
            details=f"vertical stakes={sorted(vertical_stakes)}",
        )

    return ctx.report()


__all__ = [
    "DraftWagonConfig",
    "ResolvedDraftWagonConfig",
    "WheelConfig",
    "BedSidewall",
    "TopCover",
    "PaletteStyle",
    "build_draft_wagon",
    "build_seeded_draft_wagon",
    "config_from_seed",
    "resolve_config",
    "run_draft_wagon_tests",
    "slot_choices_for_seed",
]
