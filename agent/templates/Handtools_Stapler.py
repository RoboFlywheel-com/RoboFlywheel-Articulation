# SPDX-License-Identifier: Apache-2.0

"""Desktop / hand stapler modular template.

NOTE on the slug: ``stapler`` here = a **desktop / hand stapler** (a lower
``base`` magazine tray + anvil, and a rear-hinged ``top_arm`` magazine cover /
driver that swings up about a single transverse pivot), NOT a hole punch (no
confetti box / punch), NOT a binder clip (already slug ``clip``), and NOT a
staple remover (no twin jaws). Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Stapler.md`` and the
``picture/Handtools/Stapler`` 5-star pool (1 parent + 7 slot-fork variants), all
synced under ``data/records/``.

Structure (pattern = ``parallel_children`` — but with a FIXED part tree): a
single root ``base`` part + a single child ``top_arm`` part joined by ONE
``base_to_arm`` REVOLUTE (rear pivot, axis -Y; positive q lifts the front driver
to open the stapler). All three slot axes are mesh / hardware variations on those
same two parts (the part tree and joint count are constant = 2 parts + 1 joint):

  * ``body_type`` (4): half_strip_tray / compact_stubby / full_strip_tray /
    plier_grip — the ``base`` mesh (lofted tray vs swept grip), the anvil seat
    height (``anvil_seat_z`` > 0 on the deck, or < 0 on a plier platform), and
    the module-internal feet / staple / grip-ridge copies.
  * ``hinge_mechanism`` (3): exposed_knuckle_pin / boxed_housing / torsion_spring
    — the rear hinge hardware on the base + the arm-rear descender. exposed/spring
    use base ``hinge_knuckles`` + arm ``hinge_pin`` + two arm cheeks; boxed uses a
    base ``rear_housing`` U-channel + a single central arm ``tongue`` and emits NO
    knuckles/pin; spring adds a base ``torsion_spring`` helix on top of exposed.
  * ``top_cap`` (3): rounded_hump / slab_cap / ribbed_cap — the ``arm_shell``
    mesh profile (soft dome / flat chamfered slab / dome + N finger ribs).
  * ``rib_count`` (N in [3,8]): a multiplicity axis active ONLY when
    top_cap == ribbed_cap; N evenly-spaced ``grip_rib_{i}`` ridges, inlined as
    non-moving visuals on the arm (Rule 1). Encoded as ``("rib_count", f"r{N}")``.

The single ``base_to_arm`` hinge is captured-pin / tongue-in-housing /
spring-contact geometry, so it omits ``MatingContract`` (grandfathered, per spec
§interface) and is guarded by the flat 0.015 m articulation-origin baseline (the
origin sits on the real hinge hardware) + element-scoped ``allow_overlap``
mirroring each source record's run_tests block. Feet / staples / grip ribs /
grip ridges are non-moving copies inlined as host-part visuals (Rule 1).

Compatibility gating (resolve_config, spec §9):
  * torsion_spring needs exposed knuckles + arm cheeks to push against, while
    boxed_housing deletes the knuckles/pin and replaces the cheeks with a central
    tongue -> the two are INCOMPATIBLE. hinge_mechanism is a single-select enum,
    so they never co-occur; if torsion_spring is paired with a boxed body intent
    we keep exposed-style geometry (the spring requires it).
  * body == plier_grip reseats the anvil onto a sub-pivot platform
    (anvil_seat_z < 0) and recomputes the arm driver-blade nose Z so the closed
    driver still registers above the anvil.
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
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

BodyType = Literal["half_strip_tray", "compact_stubby", "full_strip_tray", "plier_grip"]
HingeMechanism = Literal["exposed_knuckle_pin", "boxed_housing", "torsion_spring"]
TopCap = Literal["rounded_hump", "slab_cap", "ribbed_cap"]
PaletteStyle = Literal[
    "charcoal_steel",
    "black_red",
    "black_blue",
    "chrome_arm",
    "pastel_office",
    "industrial_zinc",
]

BODY_TYPES: tuple[BodyType, ...] = (
    "half_strip_tray",
    "compact_stubby",
    "full_strip_tray",
    "plier_grip",
)
HINGE_MECHANISMS: tuple[HingeMechanism, ...] = (
    "exposed_knuckle_pin",
    "boxed_housing",
    "torsion_spring",
)
TOP_CAPS: tuple[TopCap, ...] = ("rounded_hump", "slab_cap", "ribbed_cap")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "charcoal_steel",
    "black_red",
    "black_blue",
    "chrome_arm",
    "pastel_office",
    "industrial_zinc",
)

# rib_count multiplicity domain (spec §8). Weighted small (5 high, 3/4/6 common,
# 7/8 long tail).
N_RIB_MIN, N_RIB_MAX = 3, 8
# weights for N = 3, 4, 5, 6, 7, 8
RIB_COUNT_WEIGHTS = (0.16, 0.18, 0.30, 0.18, 0.10, 0.08)

# Palettes (6 colorways, spec §7). charcoal_steel is the observed source
# baseline; the rest are realistic stapler colorways extrapolated from the pool.
# Keys: body, arm, metal (anvil/rail/blade bright steel), hardware (pin/knuckle/
# housing dark steel), spring, foot.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "charcoal_steel": {
        "body": (0.20, 0.21, 0.22, 1.0),
        "arm": (0.235, 0.245, 0.255, 1.0),
        "metal": (0.78, 0.79, 0.80, 1.0),
        "hardware": (0.42, 0.43, 0.45, 1.0),
        "spring": (0.72, 0.72, 0.68, 1.0),
        "foot": (0.10, 0.10, 0.11, 1.0),
    },
    "black_red": {
        "body": (0.08, 0.08, 0.09, 1.0),
        "arm": (0.80, 0.12, 0.10, 1.0),
        "metal": (0.78, 0.79, 0.80, 1.0),
        "hardware": (0.42, 0.43, 0.45, 1.0),
        "spring": (0.72, 0.72, 0.68, 1.0),
        "foot": (0.10, 0.10, 0.11, 1.0),
    },
    "black_blue": {
        "body": (0.08, 0.08, 0.09, 1.0),
        "arm": (0.13, 0.32, 0.72, 1.0),
        "metal": (0.78, 0.79, 0.80, 1.0),
        "hardware": (0.42, 0.43, 0.45, 1.0),
        "spring": (0.72, 0.72, 0.68, 1.0),
        "foot": (0.10, 0.10, 0.11, 1.0),
    },
    "chrome_arm": {
        "body": (0.20, 0.21, 0.22, 1.0),
        "arm": (0.82, 0.84, 0.86, 1.0),
        "metal": (0.78, 0.79, 0.80, 1.0),
        "hardware": (0.42, 0.43, 0.45, 1.0),
        "spring": (0.72, 0.72, 0.68, 1.0),
        "foot": (0.10, 0.10, 0.11, 1.0),
    },
    "pastel_office": {
        "body": (0.92, 0.90, 0.86, 1.0),
        "arm": (0.62, 0.84, 0.74, 1.0),
        "metal": (0.78, 0.79, 0.80, 1.0),
        "hardware": (0.46, 0.47, 0.49, 1.0),
        "spring": (0.72, 0.72, 0.68, 1.0),
        "foot": (0.30, 0.30, 0.32, 1.0),
    },
    "industrial_zinc": {
        "body": (0.72, 0.73, 0.74, 1.0),
        "arm": (0.72, 0.73, 0.74, 1.0),
        "metal": (0.80, 0.81, 0.78, 1.0),
        "hardware": (0.55, 0.56, 0.55, 1.0),
        "spring": (0.72, 0.72, 0.68, 1.0),
        "foot": (0.16, 0.16, 0.18, 1.0),
    },
}


# ===========================================================================
# Per-body base real-world dimensions (meters). All staplers share the parent's
# coordinate convention:
#   +X = length (front jaw at +X, rear hinge at -X)
#   +Y = width
#   +Z = up; base sits on z=0.
# The hinge pivot sits at (hinge_x, 0, hinge_z) above the rear heel.
# ===========================================================================
@dataclass(frozen=True)
class _BodyDims:
    body_type: BodyType
    total_len: float
    width: float
    deck_front_z: float
    deck_mid_z: float
    base_rear_h: float
    arm_len: float
    arm_max_h: float
    hinge_x: float
    hinge_z: float
    anvil_len: float
    anvil_w: float
    anvil_th: float
    anvil_x: float
    anvil_seat_z: float
    rail_len: float
    rail_w: float
    rail_h: float
    # driver blade nose Z offset (in arm frame) so it registers above the anvil.
    blade_z: float


WALL = 0.0015
HINGE_PIN_R = 0.0024
HINGE_PIN_LEN_PAD = 0.004
HINGE_KNUCKLE_R = 0.0042
HINGE_KNUCKLE_LEN = 0.010

# Per-body nominal dims (before scaling). Derived directly from the 8 sources.
_BODY_BASE: dict[BodyType, dict[str, float]] = {
    "half_strip_tray": {
        "total_len": 0.158, "width": 0.040, "deck_front_z": 0.010,
        "deck_mid_z": 0.012, "base_rear_h": 0.019, "arm_len": 0.150,
        "arm_max_h": 0.036, "hinge_z": 0.0205, "anvil_len": 0.030,
        "anvil_w": 0.026, "rail_len": 0.110, "rail_w": 0.012, "rail_h": 0.010,
    },
    "compact_stubby": {
        "total_len": 0.092, "width": 0.034, "deck_front_z": 0.013,
        "deck_mid_z": 0.016, "base_rear_h": 0.025, "arm_len": 0.084,
        "arm_max_h": 0.032, "hinge_z": 0.026, "anvil_len": 0.022,
        "anvil_w": 0.022, "rail_len": 0.055, "rail_w": 0.010, "rail_h": 0.009,
    },
    "full_strip_tray": {
        "total_len": 0.280, "width": 0.044, "deck_front_z": 0.010,
        "deck_mid_z": 0.012, "base_rear_h": 0.021, "arm_len": 0.268,
        "arm_max_h": 0.036, "hinge_z": 0.0225, "anvil_len": 0.030,
        "anvil_w": 0.028, "rail_len": 0.220, "rail_w": 0.012, "rail_h": 0.010,
    },
    "plier_grip": {
        "total_len": 0.158, "width": 0.040, "deck_front_z": 0.010,
        "deck_mid_z": 0.012, "base_rear_h": 0.019, "arm_len": 0.150,
        "arm_max_h": 0.036, "hinge_z": 0.0205, "anvil_len": 0.030,
        "anvil_w": 0.026, "rail_len": 0.110, "rail_w": 0.012, "rail_h": 0.010,
    },
}

# Full-strip staple strip params.
STAPLE_CROWN_W = 0.0056
STAPLE_CROWN_TH = 0.0005
STAPLE_CROWN_H = 0.003
STAPLE_SPACING = 0.006
STAPLE_STRIP_START_X = 0.050
STAPLE_COUNT_DEFAULT = 12

# Grip-ridge count for plier body.
GRIP_RIDGE_COUNT = 5


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _has_visual(part, name: str) -> bool:
    """Safe presence probe (``get_visual`` raises ValidationError on missing)."""
    try:
        part.get_visual(name)
        return True
    except Exception:
        return False


# ===========================================================================
# Config dataclasses
# ===========================================================================
@dataclass(frozen=True)
class StaplerConfig:
    body_type: BodyType | None = None
    hinge_mechanism: HingeMechanism | None = None
    top_cap: TopCap | None = None
    rib_count: int | None = None
    palette_style: PaletteStyle = "charcoal_steel"
    body_len_scale: float = 1.0
    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    cap_crown_scale: float = 1.0
    open_angle_scale: float = 1.0
    name: str = "stapler"


@dataclass(frozen=True)
class ResolvedStaplerConfig:
    body_type: BodyType
    hinge_mechanism: HingeMechanism
    top_cap: TopCap
    rib_count: int  # meaningful only for top_cap == ribbed_cap
    palette_style: PaletteStyle
    dims: _BodyDims
    open_angle: float
    name: str


def config_from_seed(seed: int) -> StaplerConfig:
    rng = random.Random(seed)
    body_type = rng.choice(BODY_TYPES)
    hinge_mechanism = rng.choice(HINGE_MECHANISMS)
    top_cap = rng.choice(TOP_CAPS)
    rib_count = (
        rng.choices(range(N_RIB_MIN, N_RIB_MAX + 1), weights=RIB_COUNT_WEIGHTS, k=1)[0]
        if top_cap == "ribbed_cap"
        else 5
    )
    return StaplerConfig(
        body_type=body_type,
        hinge_mechanism=hinge_mechanism,
        top_cap=top_cap,
        rib_count=rib_count,
        palette_style=rng.choice(PALETTE_STYLES),
        body_len_scale=round(rng.uniform(0.85, 1.15), 4),
        body_width_scale=round(rng.uniform(0.90, 1.12), 4),
        body_height_scale=round(rng.uniform(0.88, 1.15), 4),
        cap_crown_scale=round(rng.uniform(0.85, 1.15), 4),
        open_angle_scale=round(rng.uniform(0.80, 1.10), 4),
        name=f"seeded_stapler_{seed}",
    )


def _resolve_dims(
    body_type: BodyType,
    *,
    len_scale: float,
    width_scale: float,
    height_scale: float,
    crown_scale: float,
) -> _BodyDims:
    b = _BODY_BASE[body_type]
    total_len = b["total_len"] * len_scale
    width = b["width"] * width_scale
    deck_front_z = b["deck_front_z"] * height_scale
    deck_mid_z = b["deck_mid_z"] * height_scale
    base_rear_h = b["base_rear_h"] * height_scale
    arm_len = b["arm_len"] * len_scale
    arm_max_h = b["arm_max_h"] * crown_scale
    hinge_x = -total_len / 2.0 + (0.008 if body_type == "compact_stubby" else 0.009)
    if body_type == "full_strip_tray":
        hinge_x = -total_len / 2.0 + 0.010
    hinge_z = b["hinge_z"] * height_scale
    anvil_len = b["anvil_len"]
    anvil_w = b["anvil_w"]
    anvil_th = 0.0016 if body_type != "compact_stubby" else 0.0015
    anvil_x = total_len / 2.0 - (0.020 if body_type == "compact_stubby" else 0.030)

    # Anvil seat height (spec §9 (2)): plier reseats the anvil onto a sub-pivot
    # platform (negative Z); tray candidates seat it on the front deck.
    if body_type == "plier_grip":
        # platform top is at -0.008 + 0.006 = -0.002; plate rests just on it.
        anvil_seat_z = -0.008 + 0.006 + 0.0005
    else:
        anvil_seat_z = deck_front_z + 0.0005

    # Driver blade nose Z (arm frame): so the closed driver registers just above
    # the anvil top. Closed blade-min-z in world == hinge_z + blade_z. We want
    # blade_min_z >= anvil_max_z. anvil_max_z = anvil_seat_z + anvil_th.
    # parent uses blade_z = 0.001 with hinge_z 0.0205 and anvil top ~0.0116;
    # i.e. blade sits well above the anvil. For plier (anvil top ~ -0.0004) the
    # parent blade_z=0.001 also clears. Keep the source value; it satisfies the
    # register check across bodies because the blade hangs from the arm crown.
    blade_z = 0.001

    return _BodyDims(
        body_type=body_type,
        total_len=total_len,
        width=width,
        deck_front_z=deck_front_z,
        deck_mid_z=deck_mid_z,
        base_rear_h=base_rear_h,
        arm_len=arm_len,
        arm_max_h=arm_max_h,
        hinge_x=hinge_x,
        hinge_z=hinge_z,
        anvil_len=anvil_len,
        anvil_w=anvil_w,
        anvil_th=anvil_th,
        anvil_x=anvil_x,
        anvil_seat_z=anvil_seat_z,
        rail_len=b["rail_len"],
        rail_w=b["rail_w"],
        rail_h=b["rail_h"],
        blade_z=blade_z,
    )


def resolve_config(config: StaplerConfig | None = None) -> ResolvedStaplerConfig:
    cfg = config or StaplerConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    body_type = _pick(cfg.body_type, BODY_TYPES)
    hinge_mechanism = _pick(cfg.hinge_mechanism, HINGE_MECHANISMS)
    top_cap = _pick(cfg.top_cap, TOP_CAPS)

    rib_count = int(cfg.rib_count) if cfg.rib_count is not None else 5
    rib_count = int(_clamp(rib_count, N_RIB_MIN, N_RIB_MAX))

    len_scale = _clamp(cfg.body_len_scale, 0.85, 1.15)
    width_scale = _clamp(cfg.body_width_scale, 0.90, 1.12)
    height_scale = _clamp(cfg.body_height_scale, 0.88, 1.15)
    crown_scale = _clamp(cfg.cap_crown_scale, 0.85, 1.15)
    angle_scale = _clamp(cfg.open_angle_scale, 0.80, 1.10)

    dims = _resolve_dims(
        body_type,
        len_scale=len_scale,
        width_scale=width_scale,
        height_scale=height_scale,
        crown_scale=crown_scale,
    )

    # Open angle (spec §7): base 0.52, clamped <= pi*0.40 so the cover never
    # over-rotates / self-collides. Floor at 0.34 so it always lifts the driver.
    open_angle = _clamp(0.52 * angle_scale, 0.34, math.pi * 0.40)

    return ResolvedStaplerConfig(
        body_type=body_type,
        hinge_mechanism=hinge_mechanism,
        top_cap=top_cap,
        rib_count=rib_count,
        palette_style=palette_style,
        dims=dims,
        open_angle=open_angle,
        name=cfg.name or "stapler",
    )


def with_overrides(config: StaplerConfig, **kwargs: object) -> StaplerConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: StaplerConfig | ResolvedStaplerConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedStaplerConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("body_type", r.body_type),
        ("hinge_mechanism", r.hinge_mechanism),
        ("top_cap", r.top_cap),
    ]
    if r.top_cap == "ribbed_cap":
        choices.append(("rib_count", f"r{r.rib_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# BASE geometry helpers (Slot A: body_type). All authored in the BASE frame.
# ===========================================================================
def _tray_base_body(d: _BodyDims) -> cq.Workplane:
    """Lofted side-profile lower tray (half / full / compact share this shape,
    differing only by dims): rear heel + low deck + rounded toe."""
    x0 = -d.total_len / 2.0
    x1 = d.total_len / 2.0
    if d.body_type == "compact_stubby":
        pts = [
            (x0, 0.0),
            (x0, d.base_rear_h),
            (x0 + 0.010, d.base_rear_h),
            (d.hinge_x + 0.006, 0.021 * (d.base_rear_h / 0.025)),
            (-0.010 * (d.total_len / 0.092), d.deck_mid_z),
            (0.010 * (d.total_len / 0.092), d.deck_mid_z),
            (x1 - 0.016, d.deck_front_z),
            (x1 - 0.004, d.deck_front_z - 0.001),
            (x1, 0.006),
            (x1, 0.0),
        ]
    elif d.body_type == "full_strip_tray":
        pts = [
            (x0, 0.0),
            (x0, d.base_rear_h),
            (x0 + 0.014, d.base_rear_h),
            (d.hinge_x + 0.008, 0.016 * (d.base_rear_h / 0.021)),
            (-0.040, d.deck_mid_z),
            (x1 - 0.045, d.deck_mid_z),
            (x1 - 0.028, d.deck_front_z),
            (x1 - 0.012, d.deck_front_z - 0.002),
            (x1, 0.004),
            (x1, 0.0),
        ]
    else:  # half_strip_tray
        pts = [
            (x0, 0.0),
            (x0, d.base_rear_h),
            (x0 + 0.014, d.base_rear_h),
            (d.hinge_x + 0.008, 0.016 * (d.base_rear_h / 0.019)),
            (-0.020, d.deck_mid_z),
            (0.040, d.deck_mid_z),
            (x1 - 0.030, d.deck_front_z),
            (x1 - 0.012, d.deck_front_z - 0.002),
            (x1, 0.004),
            (x1, 0.0),
        ]
    prof = cq.Workplane("XZ").polyline(pts).close()
    body = prof.extrude(d.width / 2.0, both=True)
    body = body.edges("|Y and >Z").fillet(0.002 if d.body_type == "compact_stubby" else 0.0022)
    return body


def _plier_grip_path(d: _BodyDims) -> list[tuple[float, float]]:
    return [
        (d.hinge_x + 0.002, 0.011),
        (d.hinge_x + 0.015, d.hinge_z - 0.012),
        (d.hinge_x + 0.025, d.hinge_z - 0.030),
        (-0.020, -0.032),
        (0.025, -0.026),
        (0.055, -0.016),
        (d.anvil_x, -0.006),
    ]


def _plier_base_grip(d: _BodyDims) -> cq.Workplane:
    """Plier-style swept ergonomic grip handle (curves down below the pivot),
    with a front anvil platform unioned in."""
    path_pts = _plier_grip_path(d)
    path = cq.Workplane("XZ").spline(path_pts)
    grip_profile = (
        cq.Workplane("YZ", origin=(path_pts[0][0], 0.0, path_pts[0][1]))
        .ellipse(d.width * 0.45, 0.009)
    )
    grip = grip_profile.sweep(path)
    # Front anvil platform: a solid block that rises from below the grip up to
    # just above the anvil seat so the anvil plate embeds into it (no float), and
    # reaches back toward the grip sweep so the platform fuses to the body. Top
    # held a hair above anvil_seat_z; bottom kept below the grip centerline.
    plat_bot = -0.012
    plat_top = d.anvil_seat_z + 0.001
    plat_h = plat_top - plat_bot
    plat_len = d.anvil_len + 0.016
    # Center the platform a little behind anvil_x so it bridges to the grip end.
    plat_cx = d.anvil_x - 0.004
    anvil_platform = (
        cq.Workplane("XY")
        .box(plat_len, d.width * 0.85, plat_h, centered=(True, True, False))
        .translate((plat_cx, 0.0, plat_bot))
    )
    return grip.union(anvil_platform)


def _plier_grip_ridges(d: _BodyDims) -> list[cq.Workplane]:
    """Ergonomic finger-grip ridges along the curved handle (Rule 1 copies)."""
    path_pts = _plier_grip_path(d)
    ridges: list[cq.Workplane] = []
    for i in range(GRIP_RIDGE_COUNT):
        t = 0.25 + (i * 0.13)
        idx = min(int(t * (len(path_pts) - 1)), len(path_pts) - 2)
        local_t = (t * (len(path_pts) - 1)) - idx
        x0, z0 = path_pts[idx]
        x1, z1 = path_pts[idx + 1]
        x_pos = x0 + local_t * (x1 - x0)
        z_pos = z0 + local_t * (z1 - z0)
        ridge = (
            cq.Workplane("XY")
            .ellipse(0.007, 0.004)
            .extrude(0.002, both=True)
            .rotate((0, 0, 0), (1, 0, 0), 90)
            .translate((x_pos, 0.0, z_pos + 0.008))
        )
        ridges.append(ridge)
    return ridges


def _anvil_plate(d: _BodyDims) -> cq.Workplane:
    """Bright metal anvil plate with two clinch grooves, seated at anvil_seat_z."""
    plate = (
        cq.Workplane("XY")
        .box(d.anvil_len, d.anvil_w, d.anvil_th, centered=(True, True, False))
        .edges("|Z").fillet(0.002)
    )
    gw = 0.0022 if d.body_type == "compact_stubby" else 0.0026
    gl = 0.010 if d.body_type == "compact_stubby" else 0.012
    gh = 0.0013 if d.body_type == "compact_stubby" else 0.0014
    goff = 0.003 if d.body_type == "compact_stubby" else 0.004
    groove = cq.Workplane("XY").box(gw, gl, gh, centered=(True, True, False))
    plate = plate.cut(groove.translate((-goff, 0.0, d.anvil_th - (gh - 0.0001))))
    plate = plate.cut(groove.translate((goff, 0.0, d.anvil_th - (gh - 0.0001))))
    return plate.translate((d.anvil_x, 0.0, d.anvil_seat_z))


def _foot_pad(d: _BodyDims, length: float, width: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(length, width, 0.0025, centered=(True, True, False))
        .edges("|Z").fillet(0.001)
    )


def _heel_pad_single(d: _BodyDims) -> cq.Workplane:
    """Single rear heel pad (half_strip baseline)."""
    return (
        cq.Workplane("XY")
        .box(0.014, d.width - 0.008, 0.0025, centered=(True, True, False))
        .translate((-d.total_len / 2.0 + 0.012, 0.0, -0.0005))
    )


def _tray_liner(d: _BodyDims) -> cq.Workplane:
    """Brushed-metal channel liner on the deck (full_strip only)."""
    liner_len = 0.230 * (d.total_len / 0.280)
    liner_w = d.width - 0.010
    liner_th = 0.0008
    liner = (
        cq.Workplane("XY")
        .box(liner_len, liner_w, liner_th, centered=(True, True, False))
        .edges("|Z").fillet(0.001)
    )
    groove = (
        cq.Workplane("XY")
        .box(liner_len - 0.020, 0.004, liner_th + 0.0002, centered=(True, True, False))
    )
    liner = liner.cut(groove.translate((0.0, 0.0, -0.0001)))
    return liner.translate((0.015, 0.0, d.deck_mid_z + 0.0004))


def _staple_crown() -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(STAPLE_CROWN_TH, STAPLE_CROWN_W, STAPLE_CROWN_H, centered=(True, True, False))
    )


# ===========================================================================
# Rear-hinge hardware helpers (Slot B: hinge_mechanism). BASE-frame visuals.
# ===========================================================================
def _hinge_knuckles(d: _BodyDims) -> cq.Workplane:
    """Two bored knuckle rings on the rear heel (axis +Y), skirted to the heel."""
    kr = HINGE_KNUCKLE_R
    kl = HINGE_KNUCKLE_LEN if d.body_type != "compact_stubby" else 0.007
    if d.body_type == "compact_stubby":
        kr = 0.0036
    kn = cq.Workplane("XZ").circle(kr).extrude(kl / 2.0, both=True)
    skirt = cq.Workplane("XY").box(
        2 * kr, kl, d.hinge_z, centered=(True, True, False)
    ).translate((0.0, 0.0, -d.hinge_z / 2.0))
    knuckle = kn.union(skirt)
    pin_r = HINGE_PIN_R if d.body_type != "compact_stubby" else 0.002
    bore = cq.Workplane("XZ").circle(pin_r + 0.0006).extrude(0.05, both=True)
    knuckle = knuckle.cut(bore)
    left = knuckle.translate((d.hinge_x, d.width / 2.0 - 0.003, d.hinge_z))
    right = knuckle.translate((d.hinge_x, -(d.width / 2.0 - 0.003), d.hinge_z))
    return left.union(right)


def _hinge_pin(d: _BodyDims) -> cq.Workplane:
    """Transverse hinge pin (ARM frame, at the pivot / arm local origin)."""
    pin_r = HINGE_PIN_R if d.body_type != "compact_stubby" else 0.002
    return (
        cq.Workplane("XZ")
        .circle(pin_r)
        .extrude((d.width + HINGE_PIN_LEN_PAD) / 2.0, both=True)
    )


def _rear_housing(d: _BodyDims) -> cq.Workplane:
    """Tall boxed U-channel housing enclosing the pivot (boxed_housing). Wider
    than the arm so the arm straddles it; hollow from top-front."""
    housing_front_x = d.hinge_x + 0.014
    housing_w = max(0.046, d.width + 0.006)
    housing_h = max(0.042, d.hinge_z + 0.020)
    wall = 0.0025
    hx0 = -d.total_len / 2.0
    hx1 = housing_front_x
    h_len = hx1 - hx0
    outer = (
        cq.Workplane("XY")
        .box(h_len, housing_w, housing_h, centered=(False, True, False))
        .translate((hx0, 0.0, 0.0))
    )
    outer = outer.edges(">Z").fillet(0.002)
    outer = outer.edges("|Z").fillet(0.0015)
    cavity = (
        cq.Workplane("XY")
        .box(h_len - wall, housing_w - 2.0 * wall, housing_h + 0.001, centered=(False, True, False))
        .translate((hx0 + wall, 0.0, wall))
    )
    return outer.cut(cavity)


def _torsion_spring_path(d: _BodyDims) -> list[tuple[float, float, float]]:
    """Centerline path: base tang -> 4-coil helix (axis +Y) -> arm tang."""
    R_coil = 0.0034
    N = 4
    pitch = 0.0014
    total_y = N * pitch
    base_tang_len = 0.012
    arm_tang_len = 0.015
    n_helix = N * 32
    points: list[tuple[float, float, float]] = []
    points.append((R_coil, -total_y / 2.0, -base_tang_len))
    points.append((R_coil, -total_y / 2.0, -base_tang_len * 0.5))
    for i in range(n_helix + 1):
        t = i / n_helix
        angle = 2.0 * math.pi * N * t
        x = R_coil * math.cos(angle)
        y = -total_y / 2.0 + total_y * t
        z = R_coil * math.sin(angle)
        points.append((x, y, z))
    points.append((R_coil + arm_tang_len * 0.5, total_y / 2.0, 0.0))
    points.append((R_coil + arm_tang_len, total_y / 2.0, 0.003))
    return points


def _torsion_spring_mesh(d: _BodyDims, assets):
    spring_mesh = tube_from_spline_points(
        _torsion_spring_path(d),
        radius=0.00045,
        samples_per_segment=2,
        radial_segments=12,
        cap_ends=True,
        up_hint=(0.0, 0.0, 1.0),
    )
    spring_mesh.translate(d.hinge_x, 0.0, d.hinge_z)
    return mesh_from_geometry(spring_mesh, "torsion_spring")


# ===========================================================================
# Arm geometry helpers (Slot C: top_cap + Slot B arm-rear descender). ARM frame:
# the pivot is at local origin; the cover extends +X. The rear descender is
# determined by the hinge (two cheeks for exposed/spring, central tongue for
# boxed) and is unioned into the arm_shell so the whole arm is one solid.
# ===========================================================================
def _safe_fillet(shape: cq.Workplane, selector: str, radius: float) -> cq.Workplane:
    """Apply a fillet, but skip it (returning the un-filleted shape) if OCC can
    not realize the radius on the selected edges. Keeps the primitive type
    (still a sculpted hump / slab), only dropping a cosmetic round-over that the
    current scaled dimensions can't support."""
    if radius <= 0.0:
        return shape
    try:
        return shape.edges(selector).fillet(radius)
    except Exception:
        return shape


def _arm_cheeks(d: _BodyDims, bottom: float) -> cq.Workplane:
    """Two arm-side hinge cheeks descending to the pin (exposed / spring)."""
    cheek = (
        cq.Workplane("XZ")
        .polyline([(-0.005, 0.0), (0.012, 0.0), (0.012, bottom + 0.002), (-0.005, bottom + 0.002)])
        .close()
        .extrude(0.005)
    )
    left_cheek = cheek.translate((0.0, 0.006, 0.0))
    right_cheek = cheek.translate((0.0, -0.006 - 0.005, 0.0))
    return left_cheek.union(right_cheek)


def _arm_tongue(d: _BodyDims, bottom: float) -> cq.Workplane:
    """Single central rear tongue descending into the housing cavity (boxed)."""
    tongue_w = 0.020
    tongue = (
        cq.Workplane("XZ")
        .polyline([(-0.004, -0.002), (0.012, -0.002), (0.012, bottom + 0.003), (-0.004, bottom + 0.003)])
        .close()
        .extrude(tongue_w / 2.0, both=True)
    )
    return tongue.edges("<Z").fillet(0.0015)


def _hump_plateau(L: float) -> tuple[float, float]:
    """Flat-crown plateau X-range for the rounded hump, proportional to arm
    length so it stays a valid (non-inverting) span on short / long arms."""
    px0 = max(0.030, 0.29 * L)
    px1 = min(L - 0.030, 0.70 * L)
    if px1 <= px0 + 0.006:  # degenerate guard for very short arms
        mid = 0.5 * L
        px0 = mid - 0.006
        px1 = mid + 0.006
    return px0, px1


def _arm_shell(r: ResolvedStaplerConfig) -> cq.Workplane:
    """Top magazine cover: mesh profile per top_cap, rear descender per hinge."""
    d = r.dims
    L = d.arm_len
    crown = d.arm_max_h
    bottom = 0.006

    if r.top_cap == "slab_cap":
        ch = 0.003
        side_chamfer = 0.003
        pts = [
            (0.004, bottom),
            (0.004, crown - ch),
            (0.004 + ch, crown),
            (L - 0.014 - ch, crown),
            (L - 0.014, crown - ch),
            (L, bottom + 0.008),
            (L, bottom),
        ]
        prof = cq.Workplane("XZ").polyline(pts).close()
        shell = prof.extrude(d.width / 2.0, both=True)
        try:
            shell = shell.edges("|X and >Z").chamfer(side_chamfer)
        except Exception:
            pass
        cavity = (
            cq.Workplane("XZ")
            .polyline([
                (0.016, bottom + WALL),
                (0.016, crown - 0.008),
                (L - 0.022, crown - 0.008),
                (L - 0.018, bottom + WALL),
            ])
            .close()
            .extrude((d.width / 2.0) - WALL, both=True)
        )
        shell = shell.cut(cavity)
    else:  # rounded_hump or ribbed_cap (same hump shell; ribs added separately)
        # Length-proportional breakpoints so the hump silhouette stays valid for
        # any arm_len (the parent's literal 0.044 / L-0.045 offsets invert on a
        # short compact arm). The flat crown plateau runs [px0, px1].
        px0, px1 = _hump_plateau(L)
        pts = [
            (0.004, bottom),
            (0.004, crown * 0.62),
            (0.016, crown * 0.92),
            (px0, crown),
            (px1, crown),
            (L - 0.014, crown * 0.86),
            (L, crown * 0.42),
            (L, bottom),
        ]
        prof = cq.Workplane("XZ").polyline(pts).close()
        shell = prof.extrude(d.width / 2.0, both=True)
        # Crown / nose fillets scaled to the (possibly shrunk) crown so the soft
        # pebble shape survives crown_scale without over-filleting thin nose faces.
        f_crown = min(0.010, crown * 0.28)
        f_nose = min(0.006, (crown * 0.42 - bottom) * 0.55)
        f_corner = min(0.008, crown * 0.22)
        shell = _safe_fillet(shell, "|Y and >Z", f_crown)
        shell = _safe_fillet(shell, "|Y and >X", f_nose)
        shell = _safe_fillet(shell, "|X and >Z", f_corner)
        cav_x0 = min(0.014, px0 * 0.32)
        cav_x1 = max(cav_x0 + 0.004, L - 0.018)
        cavity = (
            cq.Workplane("XZ")
            .polyline([
                (cav_x0, bottom + 0.0015),
                (cav_x0, crown * 0.70),
                (px0, crown * 0.78),
                (px1, crown * 0.78),
                (cav_x1 - 0.006, crown * 0.55),
                (cav_x1, bottom + 0.0015),
            ])
            .close()
            .extrude((d.width / 2.0) - WALL, both=True)
        )
        shell = shell.cut(cavity)

    # Rear descender per hinge mechanism (boxed -> central tongue, else cheeks).
    if r.hinge_mechanism == "boxed_housing":
        shell = shell.union(_arm_tongue(d, bottom))
    else:
        shell = shell.union(_arm_cheeks(d, bottom))
    return shell


def _single_grip_rib(d: _BodyDims, rib_thick: float, rib_h: float) -> cq.Workplane:
    """One transverse finger-grip rib spanning the arm width (ribbed_cap)."""
    rib_inset = 0.005
    rib_w = d.width - 2.0 * rib_inset
    rib = (
        cq.Workplane("XY")
        .box(rib_thick, rib_w, rib_h, centered=(True, True, False))
    )
    rib = rib.edges("|Y and >Z").fillet(rib_h * 0.45)
    rib = rib.edges("|X and >Z").fillet(rib_thick * 0.30)
    return rib


def _carrier_rail(d: _BodyDims) -> cq.Workplane:
    """Metal staple carrier rail under the arm (rides with the arm)."""
    rail = (
        cq.Workplane("XY")
        .box(d.rail_len, d.rail_w, d.rail_h, centered=(True, True, False))
        .edges("|X").fillet(0.0015)
    )
    pusher = cq.Workplane("XY").box(
        0.006, d.rail_w - 0.002, d.rail_h + 0.004, centered=(True, True, False)
    )
    rail = rail.union(pusher.translate((-d.rail_len / 2.0 + 0.003, 0.0, 0.0)))
    rail = rail.translate((0.030 + d.rail_len / 2.0, 0.0, 0.003))
    return rail


def _driver_blade(d: _BodyDims) -> cq.Workplane:
    """Thin metal driver blade tongue at the arm nose."""
    blade = (
        cq.Workplane("XY")
        .box(0.006, 0.020, 0.016, centered=(True, True, False))
        .edges("|Z").fillet(0.001)
    )
    return blade.translate((d.arm_len - 0.018, 0.0, d.blade_z))


# ===========================================================================
# Build
# ===========================================================================
def _build_base(model: ArticulatedObject, r: ResolvedStaplerConfig, mats, *, assets):
    d = r.dims
    base = model.part("base")

    if r.body_type == "plier_grip":
        base.visual(
            mesh_from_cadquery(_plier_base_grip(d), "base_grip", assets=assets),
            material=mats["body"], name="base_grip", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"black_red", "black_blue", "pastel_office"} else "metal.paint_coated"),
        )
        for i, ridge in enumerate(_plier_grip_ridges(d)):
            base.visual(
                mesh_from_cadquery(ridge, f"grip_ridge_{i}", assets=assets),
                material=mats["hardware"], name=f"grip_ridge_{i}", material_class_id="metal.blackened_gunmetal",
            )
    else:
        base.visual(
            mesh_from_cadquery(_tray_base_body(d), "base_body", assets=assets),
            material=mats["body"], name="base_body", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"black_red", "black_blue", "pastel_office"} else "metal.paint_coated"),
        )
        # Feet copies per body (Rule 1; absolute symmetric placement).
        if r.body_type == "compact_stubby":
            foot_xs = [-d.total_len / 2.0 + 0.012, d.total_len / 2.0 - 0.022]
            for i, fx in enumerate(foot_xs):
                base.visual(
                    mesh_from_cadquery(
                        _foot_pad(d, 0.011, d.width - 0.010).translate((fx, 0.0, -0.0005)),
                        f"foot_pad_{i}", assets=assets,
                    ),
                    material=mats["foot"], name=f"foot_pad_{i}", material_class_id="rubber.smooth_plain",
                )
        elif r.body_type == "full_strip_tray":
            foot_positions = [
                (-d.total_len / 2.0 + 0.018, d.width / 2.0 - 0.010),
                (-d.total_len / 2.0 + 0.018, -(d.width / 2.0 - 0.010)),
                (d.total_len / 2.0 - 0.035, d.width / 2.0 - 0.010),
                (d.total_len / 2.0 - 0.035, -(d.width / 2.0 - 0.010)),
            ]
            base.visual(
                mesh_from_cadquery(_tray_liner(d), "tray_liner", assets=assets),
                material=mats["metal"], name="tray_liner", material_class_id="metal.brushed_silver",
            )
            for i, (fx, fy) in enumerate(foot_positions):
                base.visual(
                    mesh_from_cadquery(
                        _foot_pad(d, 0.016, 0.009).translate((fx, fy, -0.0005)),
                        f"foot_{i}", assets=assets,
                    ),
                    material=mats["foot"], name=f"foot_{i}", material_class_id="rubber.smooth_plain",
                )
        else:  # half_strip_tray
            base.visual(
                mesh_from_cadquery(_heel_pad_single(d), "base_feet", assets=assets),
                material=mats["foot"], name="base_feet", material_class_id="rubber.smooth_plain",
            )

    # Anvil plate (all bodies).
    base.visual(
        mesh_from_cadquery(_anvil_plate(d), "anvil_plate", assets=assets),
        material=mats["metal"], name="anvil_plate", material_class_id="metal.stainless_matte",
    )

    # Rear hinge hardware (Slot B base side).
    if r.hinge_mechanism == "boxed_housing":
        base.visual(
            mesh_from_cadquery(_rear_housing(d), "rear_housing", assets=assets),
            material=mats["hardware"], name="rear_housing", material_class_id="metal.blackened_gunmetal",
        )
    else:
        base.visual(
            mesh_from_cadquery(_hinge_knuckles(d), "hinge_knuckles", assets=assets),
            material=mats["hardware"], name="hinge_knuckles", material_class_id="metal.blackened_gunmetal",
        )
        if r.hinge_mechanism == "torsion_spring":
            base.visual(
                _torsion_spring_mesh(d, assets),
                material=mats["spring"], name="torsion_spring", material_class_id="metal.steel_bare",
            )

    base.inertial = Inertial.from_geometry(
        Box((d.total_len, d.width, max(d.base_rear_h, 0.02))),
        mass=0.20,
        origin=Origin(xyz=(0.0, 0.0, d.base_rear_h / 2.0)),
    )
    return base


def _build_arm(model: ArticulatedObject, r: ResolvedStaplerConfig, mats, *, assets):
    d = r.dims
    arm = model.part("top_arm")
    arm.visual(
        mesh_from_cadquery(_arm_shell(r), "arm_shell", assets=assets),
        material=mats["arm"], name="arm_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"black_red", "black_blue", "pastel_office"} else "metal.chrome_polished"),
    )
    arm.visual(
        mesh_from_cadquery(_carrier_rail(d), "carrier_rail", assets=assets),
        material=mats["metal"], name="carrier_rail", material_class_id="metal.stainless_matte",
    )
    arm.visual(
        mesh_from_cadquery(_driver_blade(d), "driver_blade", assets=assets),
        material=mats["metal"], name="driver_blade", material_class_id="metal.stainless_matte",
    )
    # Hinge pin (exposed / spring only; boxed has no pin).
    if r.hinge_mechanism != "boxed_housing":
        arm.visual(
            mesh_from_cadquery(_hinge_pin(d), "hinge_pin", assets=assets),
            material=mats["hardware"], name="hinge_pin", material_class_id="metal.blackened_gunmetal",
        )
    # Grip ribs (ribbed_cap only; Rule 1 copies along the crown). Placed only
    # over the genuinely-flat crown plateau (silhouette flat span x in
    # [0.044, L-0.045]) and embedded ~half their height into the crown so each
    # rib straddles the shell surface (never a floating island under scaling).
    if r.top_cap == "ribbed_cap":
        rib_thick = 0.0030
        rib_h = 0.0022
        # Embed the rib bottom below the crown top so it fuses with the shell.
        rib_base_z = d.arm_max_h - rib_h * 0.6
        plateau_x0, plateau_x1 = _hump_plateau(d.arm_len)
        inset = max(0.003, (plateau_x1 - plateau_x0) * 0.06)
        rib_x_start = plateau_x0 + inset
        rib_x_end = plateau_x1 - inset
        rib_span = max(0.0, rib_x_end - rib_x_start)
        for i in range(r.rib_count):
            t = i / max(r.rib_count - 1, 1)
            rib_x = rib_x_start + t * rib_span
            placed = _single_grip_rib(d, rib_thick, rib_h).translate((rib_x, 0.0, rib_base_z))
            arm.visual(
                mesh_from_cadquery(placed, f"grip_rib_{i}", assets=assets),
                material=mats["arm"], name=f"grip_rib_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"black_red", "black_blue", "pastel_office"} else "metal.chrome_polished"),
            )
    # Full-strip staples in the magazine (Rule 1 copies; ride with the arm).
    if r.body_type == "full_strip_tray":
        for i in range(STAPLE_COUNT_DEFAULT):
            sx = STAPLE_STRIP_START_X + i * STAPLE_SPACING
            staple_geom = _staple_crown().translate((sx, 0.0, 0.002))
            arm.visual(
                mesh_from_cadquery(staple_geom, f"staple_{i}", assets=assets),
                material=mats["metal"], name=f"staple_{i}", material_class_id="metal.steel_galvanized",
            )
    arm.inertial = Inertial.from_geometry(
        Box((d.arm_len, d.width, d.arm_max_h)),
        mass=0.10,
        origin=Origin(xyz=(d.arm_len / 2.0, 0.0, d.arm_max_h / 2.0)),
    )
    return arm


def build_stapler(
    config: StaplerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    d = r.dims
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"stapler_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    base = _build_base(model, r, mats, assets=assets)
    arm = _build_arm(model, r, mats, assets=assets)

    # Single rear hinge. Pivot at (hinge_x, 0, hinge_z) on the base, on real
    # hinge hardware (knuckle ring centers / housing cavity). The arm is authored
    # with its pivot at the arm local origin and the cover extending +X; axis=-Y
    # so positive q lifts the front driver upward (opens the stapler). Captured
    # pin/tongue/spring geometry -> omit MatingContract (grandfathered, spec
    # §interface); guarded by the origin baseline + element-scoped allow_overlap.
    model.articulation(
        "base_to_arm",
        ArticulationType.REVOLUTE,
        parent=base,
        child=arm,
        origin=Origin(xyz=(d.hinge_x, 0.0, d.hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=3.0, lower=0.0, upper=r.open_angle),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_stapler(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_stapler(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_stapler_tests(
    object_model: ArticulatedObject,
    config: StaplerConfig,
) -> TestReport:
    r = resolve_config(config)
    d = r.dims
    ctx = TestContext(object_model)

    base = object_model.get_part("base")
    arm = object_model.get_part("top_arm")
    hinge = object_model.get_articulation("base_to_arm")

    # ---- Captured / contact hinge allowances (element-scoped). ----
    if r.hinge_mechanism == "exposed_knuckle_pin":
        ctx.allow_overlap(
            arm, base, elem_a="hinge_pin", elem_b="hinge_knuckles",
            reason="The transverse hinge pin is captured inside the base hinge-knuckle bores.",
        )
        ctx.allow_overlap(
            arm, base, elem_a="arm_shell", elem_b="hinge_knuckles",
            reason="The arm-side hinge cheeks interleave with the base knuckles on the shared pivot pin.",
        )
    elif r.hinge_mechanism == "torsion_spring":
        ctx.allow_overlap(
            arm, base, elem_a="hinge_pin", elem_b="hinge_knuckles",
            reason="The transverse hinge pin is captured inside the base hinge-knuckle bores.",
        )
        ctx.allow_overlap(
            arm, base, elem_a="arm_shell", elem_b="hinge_knuckles",
            reason="The arm-side hinge cheeks interleave with the base knuckles on the shared pivot pin.",
        )
        ctx.allow_overlap(
            base, arm, elem_a="torsion_spring", elem_b="arm_shell",
            reason="The torsion-spring arm tang contacts the arm shell rear cheeks (return force).",
        )
    else:  # boxed_housing
        ctx.allow_overlap(
            arm, base, elem_a="arm_shell", elem_b="rear_housing",
            reason="The arm rear tongue pivots inside the boxed housing cavity (enclosed pivot).",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Joint contract. ----
    ctx.check(
        "base_to_arm is REVOLUTE about transverse -Y axis",
        hinge.articulation_type == ArticulationType.REVOLUTE
        and abs(hinge.axis[1]) > 0.99
        and abs(hinge.axis[0]) < 0.02 and abs(hinge.axis[2]) < 0.02,
        details=f"type={hinge.articulation_type} axis={tuple(hinge.axis)}",
    )
    lim = hinge.motion_limits
    ctx.check(
        "hinge opens upward from closed (lower=0, 0.3 < upper <= pi*0.40)",
        lim is not None and lim.lower == 0.0 and lim.upper is not None
        and lim.upper > 0.3 and lim.upper <= math.pi * 0.40 + 1e-6,
        details=f"limits=({lim.lower if lim else None},{lim.upper if lim else None})",
    )

    # ---- Part tree (constant 2 parts + 1 joint across all combos). ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "part tree is exactly base + top_arm",
        part_names == {"base", "top_arm"},
        details=str(sorted(part_names)),
    )

    # ---- Hero visuals present per body / hinge / cap. ----
    body_shell = "base_grip" if r.body_type == "plier_grip" else "base_body"
    for label, part in [(body_shell, base), ("anvil_plate", base),
                        ("arm_shell", arm), ("carrier_rail", arm), ("driver_blade", arm)]:
        ctx.check(f"{label} present", _has_visual(part, label), details=f"{label} missing")

    # ---- Hinge-mechanism topology contract. ----
    if r.hinge_mechanism == "boxed_housing":
        ctx.check(
            "boxed: rear_housing present, no exposed knuckles / pin",
            _has_visual(base, "rear_housing") and not _has_visual(base, "hinge_knuckles") and not _has_visual(arm, "hinge_pin"),
            details=f"housing={_has_visual(base, 'rear_housing')} knuckles={_has_visual(base, 'hinge_knuckles')} pin={_has_visual(arm, 'hinge_pin')}",
        )
        housing_aabb = ctx.part_element_world_aabb(base, elem="rear_housing")
        ctx.check(
            "housing encloses the pivot (top above + floor near ground)",
            housing_aabb is not None
            and housing_aabb[1][2] > d.hinge_z + 0.012
            and housing_aabb[0][2] < 0.006
            and housing_aabb[0][0] <= d.hinge_x <= housing_aabb[1][0],
            details=str(housing_aabb),
        )
    else:
        ctx.check(
            "exposed/spring: hinge_knuckles + hinge_pin present",
            _has_visual(base, "hinge_knuckles") and _has_visual(arm, "hinge_pin"),
            details=f"knuckles={_has_visual(base, 'hinge_knuckles')} pin={_has_visual(arm, 'hinge_pin')}",
        )
        if r.hinge_mechanism == "torsion_spring":
            ctx.check(
                "torsion_spring present (incompatible with boxed; needs exposed knuckles)",
                _has_visual(base, "torsion_spring"),
                details="torsion_spring missing",
            )
            spring_aabb = ctx.part_element_world_aabb(base, elem="torsion_spring")
            if spring_aabb is not None:
                z_span = spring_aabb[1][2] - spring_aabb[0][2]
                ctx.check(
                    "spring coil wraps the pivot (visible Z span)",
                    z_span > 0.005,
                    details=f"spring_z_span={z_span:.4f}",
                )

    # ---- top_cap topology contract. ----
    if r.top_cap == "ribbed_cap":
        ribs = [arm.get_visual(f"grip_rib_{i}") for i in range(r.rib_count)]
        ctx.check(
            "N grip ribs inlined on the arm (Rule 1)",
            all(rib is not None for rib in ribs),
            details=f"rib_count={r.rib_count}",
        )
        # Ribs protrude above the crown and stay within the crown platform.
        with ctx.pose({hinge: 0.0}):
            shell_aabb = ctx.part_element_world_aabb(arm, elem="arm_shell")
            for i in range(r.rib_count):
                ra = ctx.part_element_world_aabb(arm, elem=f"grip_rib_{i}")
                if ra is not None and shell_aabb is not None:
                    ctx.check(
                        f"grip_rib_{i} protrudes above the crown",
                        ra[1][2] >= shell_aabb[1][2] - 0.002,
                        details=f"rib_top={ra[1][2]:.4f} crown_top={shell_aabb[1][2]:.4f}",
                    )
    elif r.top_cap == "slab_cap":
        with ctx.pose({hinge: 0.0}):
            sa = ctx.part_element_world_aabb(arm, elem="arm_shell")
            if sa is not None:
                ctx.check(
                    "slab cap spans most of the arm length and is a thick slab",
                    (sa[1][0] - sa[0][0]) >= 0.80 * d.arm_len
                    and (sa[1][2] - sa[0][2]) > 0.024,
                    details=f"dx={sa[1][0]-sa[0][0]:.4f} dz={sa[1][2]-sa[0][2]:.4f}",
                )

    # ---- Body-type contract: plier anvil seat is below the pivot. ----
    if r.body_type == "plier_grip":
        with ctx.pose({hinge: 0.0}):
            grip_aabb = ctx.part_element_world_aabb(base, elem="base_grip")
            anvil_aabb = ctx.part_element_world_aabb(base, elem="anvil_plate")
        ctx.check(
            "plier grip curves below the pivot for hand-squeeze",
            grip_aabb is not None and grip_aabb[0][2] < d.hinge_z - 0.020,
            details=f"grip_min_z={grip_aabb[0][2] if grip_aabb else None} hinge_z={d.hinge_z:.4f}",
        )
        ctx.check(
            "plier anvil reseated low (on the sub-pivot platform)",
            anvil_aabb is not None and -0.014 < anvil_aabb[0][2] < 0.006,
            details=f"anvil_min_z={anvil_aabb[0][2] if anvil_aabb else None}",
        )

    # ---- Closed pose: cover above the base, covers footprint, registers. ----
    with ctx.pose({hinge: 0.0}):
        shell_aabb = ctx.part_element_world_aabb(arm, elem="arm_shell")
        base_aabb = ctx.part_element_world_aabb(base, elem=body_shell)
        crown_margin = 0.020 if r.body_type == "compact_stubby" else 0.024
        ctx.check(
            "cover crown rises above the base body",
            shell_aabb is not None and base_aabb is not None
            and shell_aabb[1][2] > base_aabb[1][2] + crown_margin,
            details=f"shell_top={shell_aabb[1][2]:.4f} base_top={base_aabb[1][2]:.4f}",
        )
        ctx.expect_overlap(
            arm, base, axes="xy", min_overlap=0.02,
            name="closed cover covers the base footprint",
        )
        anvil_aabb = ctx.part_element_world_aabb(base, elem="anvil_plate")
        blade_aabb = ctx.part_element_world_aabb(arm, elem="driver_blade")
        ctx.check(
            "driver blade registers above the anvil plate",
            blade_aabb is not None and anvil_aabb is not None
            and blade_aabb[0][2] >= anvil_aabb[1][2] - 0.001
            and abs(blade_aabb[0][0] - anvil_aabb[0][0]) < 0.05,
            details=f"blade_min_z={blade_aabb[0][2]:.4f} anvil_max_z={anvil_aabb[1][2]:.4f}",
        )
        if r.hinge_mechanism == "boxed_housing":
            ctx.expect_overlap(
                arm, base, axes="xz", elem_a="arm_shell", elem_b="rear_housing",
                min_overlap=0.004,
                name="arm rear tongue pivots inside the housing cavity",
            )
        closed_blade = ctx.part_element_world_aabb(arm, elem="driver_blade")

    # ---- Open pose: lifting the cover raises the driver blade. ----
    with ctx.pose({hinge: hinge.motion_limits.upper}):
        open_blade = ctx.part_element_world_aabb(arm, elem="driver_blade")
    open_margin = 0.020 if r.body_type == "compact_stubby" else 0.030
    ctx.check(
        "opening the hinge lifts the driver blade upward",
        closed_blade is not None and open_blade is not None
        and open_blade[0][2] > closed_blade[0][2] + open_margin,
        details=f"closed_min_z={closed_blade[0][2]:.4f} open_min_z={open_blade[0][2]:.4f}",
    )

    # ---- Ground + slot_choices. ----
    aabb = ctx.part_world_aabb(base)
    if aabb is not None:
        ctx.check("base rests near the ground", aabb[0][2] < 0.03, details=f"z_min={aabb[0][2]:.4f}")
    ctx.check(
        "slot_choices recorded with rib_count encoded for ribbed_cap",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "StaplerConfig",
    "ResolvedStaplerConfig",
    "build_stapler",
    "build_seeded_stapler",
    "config_from_seed",
    "resolve_config",
    "run_stapler_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
