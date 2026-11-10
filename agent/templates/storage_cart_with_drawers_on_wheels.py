# SPDX-License-Identifier: Apache-2.0

"""Storage cart with drawers on wheels — modular procedural template.

Category identity: a grounded rolling **storage cart** whose primary use is
stowing items in one or more banks of pull-out drawers, standing on **four
caster wheels**. Not an office desk (no worktop), not a shopping trolley (no
open basket), not a filing cabinet (no wheels), not a bare platform cart
(has drawers).

Sources (5-star, 12 records): 6 origin anchors
``rec_picturex_0611__storage_cart_with_drawers_on_wheels__00{1..6}__png_*`` and
6 slot-fork variants ``rec_0611_storage_cart_with_drawers_on_w_var_*``. Local
inspection of ``_var_caster_braked_swivel``, ``_var_drawer_count_3``,
``_var_drawer_layout_twin_bank`` model.py files.

Slot graph (pattern = ``mixed``; parallel-children + multiplicity):

    body (root, floats above ground on caster gap)
      ├── PRISMATIC (0,-1,0) drawer_{bank}_{i}   (N per bank; up to 2 banks)
      └── caster_{j} subtree  (j in [0,4))
            fork/bracket                          (REVOLUTE/CONTINUOUS +Z, or FIXED)
              └── wheel_{j}                        (CONTINUOUS +X)
            (braked variant) brake_lever_{j}      (REVOLUTE +X on fork)

Slots (all discrete; per spec §8.5 axis map):
  * ``frame_form`` (③ Primary Form Family): open_tubular_cart / rounded_tower
    / rectangular_cabinet / slim_service_stand
  * ``caster`` (② mechanism): swivel_caster / fixed_caster / mixed_swivel_fixed
    / braked_swivel_caster
  * ``drawer_layout`` (①): single_bank / twin_bank
  * ``drawer_count`` (multiplicity, N ∈ [2, 8] per bank; clamp N≤5 when twin_bank)
  * ``palette_style`` (⑥): 5 palettes covering metal / painted / wood / stainless

Canonical spec: ``articraft_template_authoring/specs_modular_v1/storage_cart_with_drawers_on_wheels.md``
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
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

FrameForm = Literal[
    "open_tubular_cart",
    "rounded_tower",
    "rectangular_cabinet",
    "slim_service_stand",
]
Caster = Literal[
    "swivel_caster",
    "fixed_caster",
    "mixed_swivel_fixed",
    "braked_swivel_caster",
]
DrawerLayout = Literal["single_bank", "twin_bank"]
PaletteStyle = Literal[
    "medical_white",
    "industrial_gray",
    "warm_oak_utility",
    "safety_yellow",
    "stainless_steel",
]

FRAME_FORMS: tuple[FrameForm, ...] = (
    "open_tubular_cart",
    "rounded_tower",
    "rectangular_cabinet",
    "slim_service_stand",
)
CASTERS: tuple[Caster, ...] = (
    "swivel_caster",
    "fixed_caster",
    "mixed_swivel_fixed",
    "braked_swivel_caster",
)
DRAWER_LAYOUTS: tuple[DrawerLayout, ...] = ("single_bank", "twin_bank")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "medical_white",
    "industrial_gray",
    "warm_oak_utility",
    "safety_yellow",
    "stainless_steel",
)

# Per-role rgba materials. Every `.visual(material=mats[...])` sources from
# `PALETTES[palette_style][role]`.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "medical_white": {
        "shell": (0.94, 0.94, 0.95, 1.0),
        "drawer_front": (0.88, 0.90, 0.94, 1.0),
        "drawer_box": (0.78, 0.80, 0.82, 1.0),
        "accent": (0.35, 0.36, 0.40, 1.0),
        "fork": (0.30, 0.31, 0.34, 1.0),
        "wheel": (0.12, 0.12, 0.13, 1.0),
        "hardware": (0.75, 0.76, 0.78, 1.0),
    },
    "industrial_gray": {
        "shell": (0.42, 0.44, 0.47, 1.0),
        "drawer_front": (0.32, 0.34, 0.37, 1.0),
        "drawer_box": (0.55, 0.56, 0.58, 1.0),
        "accent": (0.72, 0.12, 0.10, 1.0),
        "fork": (0.14, 0.14, 0.16, 1.0),
        "wheel": (0.09, 0.09, 0.10, 1.0),
        "hardware": (0.15, 0.15, 0.17, 1.0),
    },
    "warm_oak_utility": {
        "shell": (0.63, 0.44, 0.26, 1.0),
        "drawer_front": (0.72, 0.51, 0.32, 1.0),
        "drawer_box": (0.55, 0.42, 0.28, 1.0),
        "accent": (0.16, 0.17, 0.20, 1.0),
        "fork": (0.14, 0.14, 0.16, 1.0),
        "wheel": (0.10, 0.10, 0.11, 1.0),
        "hardware": (0.30, 0.31, 0.34, 1.0),
    },
    "safety_yellow": {
        "shell": (0.90, 0.74, 0.10, 1.0),
        "drawer_front": (0.24, 0.24, 0.26, 1.0),
        "drawer_box": (0.20, 0.20, 0.22, 1.0),
        "accent": (0.12, 0.12, 0.13, 1.0),
        "fork": (0.14, 0.14, 0.16, 1.0),
        "wheel": (0.09, 0.09, 0.10, 1.0),
        "hardware": (0.16, 0.16, 0.18, 1.0),
    },
    "stainless_steel": {
        "shell": (0.78, 0.80, 0.83, 1.0),
        "drawer_front": (0.72, 0.74, 0.78, 1.0),
        "drawer_box": (0.68, 0.70, 0.73, 1.0),
        "accent": (0.30, 0.31, 0.34, 1.0),
        "fork": (0.16, 0.16, 0.18, 1.0),
        "wheel": (0.09, 0.09, 0.10, 1.0),
        "hardware": (0.55, 0.56, 0.58, 1.0),
    },
}

DRAWER_MIN, DRAWER_MAX = 2, 8
_DRAWER_CHOICES = (2, 3, 4, 5, 6, 7, 8)
_DRAWER_WEIGHTS = (0.08, 0.20, 0.22, 0.20, 0.14, 0.09, 0.07)

# Base geometry constants (m).
WALL = 0.014
PLINTH_H = 0.028
TOP_CAP_T = 0.020
FRONT_STILE_T = 0.014
BACK_T = 0.014

# Wheels (chosen so 4 wheels always fit under smallest cart footprint).
WHEEL_R = 0.052
WHEEL_W = 0.030
FORK_DROP = 0.030
BRAKE_LEVER_W = 0.018
BRAKE_LEVER_T = 0.008
BRAKE_LEVER_LEN = 0.055
BRAKE_PIVOT_R = 0.006
CASTER_GAP = WHEEL_R * 2.0 + FORK_DROP + 0.014  # ~0.148 default; wheel bottom @ z=0.


@dataclass(frozen=True)
class StorageCartWithDrawersOnWheelsConfig:
    frame_form: FrameForm = "rectangular_cabinet"
    caster: Caster = "swivel_caster"
    drawer_layout: DrawerLayout = "single_bank"
    drawer_count: int = 4
    palette_style: PaletteStyle = "industrial_gray"
    cart_width: float = 0.56
    cart_depth: float = 0.44
    cart_height: float = 0.78
    drawer_travel_scale: float = 1.0
    swivel_range: float = math.pi
    brake_angle: float = 0.55
    name: str = "storage_cart_with_drawers_on_wheels"


@dataclass(frozen=True)
class ResolvedStorageCartConfig:
    frame_form: FrameForm
    caster: Caster
    drawer_layout: DrawerLayout
    drawer_count: int  # per bank (or total if single_bank)
    palette_style: PaletteStyle
    cart_width: float
    cart_depth: float
    cart_height: float
    caster_gap: float
    # Derived layout
    plinth_h: float
    top_cap_t: float
    wall_t: float
    front_stile_t: float
    bank_x_centers: tuple[float, ...]  # X centers for each bank
    bank_width: float  # width of each drawer bank pedestal
    drawer_front_width: float
    drawer_box_width: float
    drawer_box_depth: float
    drawer_front_height: float
    drawer_box_height: float
    drawer_travel: float
    drawer_center_z: tuple[float, ...]  # Z centers of each drawer face top->bottom
    # Casters
    caster_positions: tuple[tuple[float, float], ...]  # 4 (x,y)
    caster_kinds: tuple[Literal["swivel", "fixed", "braked"], ...]  # per-caster kind
    swivel_range: float
    brake_angle: float
    # Frame
    frame_is_open_tubular: bool
    frame_has_rounded_corners: bool
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def config_from_seed(seed: int) -> StorageCartWithDrawersOnWheelsConfig:
    rng = random.Random(seed)
    frame_form = rng.choice(FRAME_FORMS)
    caster = rng.choice(CASTERS)
    layout = rng.choice(DRAWER_LAYOUTS)
    drawer_count = rng.choices(_DRAWER_CHOICES, weights=_DRAWER_WEIGHTS, k=1)[0]
    palette = rng.choice(PALETTE_STYLES)
    # Slim service stand nudges dimensions narrower & taller (still Volumetric
    # Envelope Form of rectangular family; Rule 3 preserved).
    if frame_form == "slim_service_stand":
        cart_width = round(rng.uniform(0.36, 0.46), 3)
        cart_depth = round(rng.uniform(0.34, 0.42), 3)
        cart_height = round(rng.uniform(0.78, 0.95), 3)
    else:
        cart_width = round(rng.uniform(0.46, 0.72), 3)
        cart_depth = round(rng.uniform(0.38, 0.58), 3)
        cart_height = round(rng.uniform(0.64, 0.90), 3)
    return StorageCartWithDrawersOnWheelsConfig(
        frame_form=frame_form,
        caster=caster,
        drawer_layout=layout,
        drawer_count=drawer_count,
        palette_style=palette,
        cart_width=cart_width,
        cart_depth=cart_depth,
        cart_height=cart_height,
        drawer_travel_scale=round(rng.uniform(0.85, 1.10), 3),
        swivel_range=round(rng.uniform(2.0, 3.0), 3),
        brake_angle=round(rng.uniform(0.45, 0.65), 3),
        name=f"seeded_storage_cart_with_drawers_on_wheels_{seed}",
    )


def resolve_config(
    config: StorageCartWithDrawersOnWheelsConfig | None = None,
) -> ResolvedStorageCartConfig:
    cfg = config or StorageCartWithDrawersOnWheelsConfig()
    if cfg.frame_form not in FRAME_FORMS:
        raise ValueError(f"Unsupported frame_form: {cfg.frame_form}")
    if cfg.caster not in CASTERS:
        raise ValueError(f"Unsupported caster: {cfg.caster}")
    if cfg.drawer_layout not in DRAWER_LAYOUTS:
        raise ValueError(f"Unsupported drawer_layout: {cfg.drawer_layout}")
    if cfg.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {cfg.palette_style}")

    frame_form = cfg.frame_form
    caster = cfg.caster
    layout = cfg.drawer_layout
    palette = cfg.palette_style

    # Clamp drawer_count and enforce twin_bank ≤ 5.
    drawer_count = int(_clamp(cfg.drawer_count, DRAWER_MIN, DRAWER_MAX))
    if layout == "twin_bank":
        drawer_count = min(drawer_count, 5)

    cart_width = _clamp(cfg.cart_width, 0.34, 0.80)
    cart_depth = _clamp(cfg.cart_depth, 0.32, 0.62)
    cart_height = _clamp(cfg.cart_height, 0.58, 0.98)

    # Enforce twin_bank needs enough width for two side-by-side pedestals.
    if layout == "twin_bank":
        cart_width = max(cart_width, 0.48)

    # Bank layout.
    if layout == "single_bank":
        bank_width = cart_width - 2 * WALL - 0.010
        bank_x_centers = (0.0,)
    else:
        # Two banks with a thin divider between.
        divider = 0.010
        bank_width = (cart_width - 2 * WALL - divider - 0.010) / 2.0
        cx = (bank_width + divider) / 2.0
        bank_x_centers = (-cx, cx)
    bank_width = max(bank_width, 0.22)

    drawer_front_width = bank_width - 2 * FRONT_STILE_T - 0.006
    drawer_box_width = drawer_front_width - 0.012
    drawer_box_depth = cart_depth - BACK_T - 0.040
    drawer_box_depth = max(drawer_box_depth, 0.22)

    # Vertical drawer stack fits in usable height between plinth and top cap.
    usable_h = cart_height - PLINTH_H - TOP_CAP_T - 0.010
    pitch = usable_h / max(drawer_count, 1)
    drawer_front_height = _clamp(pitch * 0.86, 0.08, 0.22)
    drawer_box_height = drawer_front_height * 0.80
    first_z = PLINTH_H + pitch * 0.5
    drawer_center_z = tuple(first_z + i * pitch for i in range(drawer_count))

    drawer_travel_base = drawer_box_depth * 0.85
    drawer_travel = _clamp(
        drawer_travel_base * _clamp(cfg.drawer_travel_scale, 0.80, 1.15),
        0.16,
        drawer_box_depth * 0.92,
    )

    # Caster positions: 4 corners, inset so wheel/fork fit inside the footprint.
    caster_inset_x = WHEEL_W / 2.0 + 0.012 + WALL
    caster_inset_y = WHEEL_R + 0.010 + WALL
    # Insets must not exceed half the footprint.
    caster_inset_x = min(caster_inset_x, cart_width / 2.0 - 0.010)
    caster_inset_y = min(caster_inset_y, cart_depth / 2.0 - 0.010)
    corners: list[tuple[float, float]] = []
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            corners.append(
                (sx * (cart_width / 2.0 - caster_inset_x), sy * (cart_depth / 2.0 - caster_inset_y))
            )
    caster_positions = tuple(corners)

    # Per-caster kind based on Slot B choice. Ordering matches corners:
    # 0=(-x,-y) front-left; 1=(-x,+y) rear-left; 2=(+x,-y) front-right; 3=(+x,+y) rear-right.
    # For mixed_swivel_fixed: front (y<0) swivel, rear (y>0) fixed.
    if caster == "swivel_caster":
        kinds: tuple = ("swivel", "swivel", "swivel", "swivel")
    elif caster == "fixed_caster":
        kinds = ("fixed", "fixed", "fixed", "fixed")
    elif caster == "mixed_swivel_fixed":
        # index 0=(-x,-y) front-left swivel; 1=(-x,+y) rear-left fixed;
        # 2=(+x,-y) front-right swivel; 3=(+x,+y) rear-right fixed
        kinds = ("swivel", "fixed", "swivel", "fixed")
    else:  # braked_swivel_caster
        kinds = ("braked", "braked", "braked", "braked")

    return ResolvedStorageCartConfig(
        frame_form=frame_form,
        caster=caster,
        drawer_layout=layout,
        drawer_count=drawer_count,
        palette_style=palette,
        cart_width=cart_width,
        cart_depth=cart_depth,
        cart_height=cart_height,
        caster_gap=CASTER_GAP,
        plinth_h=PLINTH_H,
        top_cap_t=TOP_CAP_T,
        wall_t=WALL,
        front_stile_t=FRONT_STILE_T,
        bank_x_centers=bank_x_centers,
        bank_width=bank_width,
        drawer_front_width=drawer_front_width,
        drawer_box_width=drawer_box_width,
        drawer_box_depth=drawer_box_depth,
        drawer_front_height=drawer_front_height,
        drawer_box_height=drawer_box_height,
        drawer_travel=drawer_travel,
        drawer_center_z=drawer_center_z,
        caster_positions=caster_positions,
        caster_kinds=kinds,  # type: ignore[arg-type]
        swivel_range=_clamp(cfg.swivel_range, 1.20, math.pi),
        brake_angle=_clamp(cfg.brake_angle, 0.30, 0.75),
        frame_is_open_tubular=(frame_form == "open_tubular_cart"),
        frame_has_rounded_corners=(frame_form == "rounded_tower"),
        name=cfg.name or "storage_cart_with_drawers_on_wheels",
    )


def with_overrides(
    config: StorageCartWithDrawersOnWheelsConfig, **kwargs: object
) -> StorageCartWithDrawersOnWheelsConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: StorageCartWithDrawersOnWheelsConfig | ResolvedStorageCartConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedStorageCartConfig) else resolve_config(config)
    return (
        ("frame_form", r.frame_form),
        ("caster", r.caster),
        ("drawer_layout", r.drawer_layout),
        ("drawer_count", f"{r.drawer_count}_drawers"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _joint_meta(joint_type, axis, origin, limits) -> dict[str, object]:
    return {
        "type": joint_type.value,
        "axis": axis,
        "origin": origin,
        "range": None if limits is None else (limits.lower, limits.upper),
    }


def _box(part, size, xyz, material, name: str) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.paint_coated")


# ---------------------------------------------------------------------------
# Body (frame) construction as parent visuals.
# ---------------------------------------------------------------------------
def _body_z_mid(r: ResolvedStorageCartConfig) -> float:
    """Z center of carcass in world coords (floor_z + cart_height/2)."""
    return r.caster_gap + r.cart_height / 2.0


def _build_pedestal(
    body,
    r: ResolvedStorageCartConfig,
    mats: dict[str, object],
    *,
    center_x: float,
    prefix: str,
) -> None:
    """Emit a pedestal carcass (walls, back, floor, top cap, plinth) at center_x.
    Front is open (drawers slide out toward -Y)."""
    w = r.bank_width
    d = r.cart_depth
    ped_h = r.cart_height - r.top_cap_t - r.plinth_h
    st = r.wall_t
    z_body_mid = r.caster_gap + r.plinth_h + ped_h / 2.0

    # Plinth (below).
    _box(
        body,
        (w * 0.94, d * 0.90, r.plinth_h),
        (center_x, 0.0, r.caster_gap + r.plinth_h / 2.0),
        mats["shell"],
        f"{prefix}_plinth",
    )
    # Side walls.
    for sign, name in ((1.0, "wall_right"), (-1.0, "wall_left")):
        _box(
            body,
            (st, d, ped_h),
            (center_x + sign * (w / 2.0 - st / 2.0), 0.0, z_body_mid),
            mats["shell"],
            f"{prefix}_{name}",
        )
    # Back panel.
    _box(
        body,
        (w - 2.0 * st, BACK_T, ped_h),
        (center_x, d / 2.0 - BACK_T / 2.0, z_body_mid),
        mats["shell"],
        f"{prefix}_back",
    )
    # Floor.
    _box(
        body,
        (w - 2.0 * st, d - BACK_T, 0.014),
        (center_x, -BACK_T / 2.0, r.caster_gap + r.plinth_h + 0.007),
        mats["shell"],
        f"{prefix}_floor",
    )
    # Top cap.
    _box(
        body,
        (w - 2.0 * st, d - BACK_T, r.top_cap_t),
        (center_x, -BACK_T / 2.0, r.caster_gap + r.plinth_h + ped_h + r.top_cap_t / 2.0),
        mats["shell"],
        f"{prefix}_top_cap",
    )
    # Front stiles (thin vertical strips at front-face corners); anchor drawer fronts.
    front_y = -d / 2.0 + 0.010
    for sign, name in ((1.0, "front_stile_right"), (-1.0, "front_stile_left")):
        _box(
            body,
            (r.front_stile_t, 0.020, ped_h - 0.010),
            (center_x + sign * (w / 2.0 - r.front_stile_t / 2.0), front_y, z_body_mid),
            mats["shell"],
            f"{prefix}_{name}",
        )
    # Per-drawer slide rail (thin horizontal strip at each drawer Z).
    # Rail spans the full inner width so its ends touch the side walls
    # (fixes disconnected-island warning between rail and wall_left/right).
    for i, cz in enumerate(r.drawer_center_z):
        _box(
            body,
            (w - 2.0 * st, 0.014, 0.010),
            (center_x, front_y, r.caster_gap + cz),
            mats["hardware"],
            f"{prefix}_slide_rail_{i}",
        )


def _build_top_hardware(
    body,
    r: ResolvedStorageCartConfig,
    mats: dict[str, object],
) -> None:
    """Top ornaments: purely body visuals (Rule 1). All top hardware embeds
    slightly into the top_cap so no disconnected islands appear."""
    z_top = r.caster_gap + r.cart_height
    # Sit each ornament flush against the top cap (top face at z_top). Center
    # the ornament so its lower face embeds ~1mm into the cap surface.
    if r.frame_form == "open_tubular_cart":
        # Top tray sits on the cap.
        tray_t = 0.010
        _box(
            body,
            (r.cart_width * 0.94, r.cart_depth * 0.92, tray_t),
            (0.0, 0.0, z_top + tray_t / 2.0 - 0.002),
            mats["accent"],
            "top_tray",
        )
        # Two vertical handle risers (connect tray to horizontal bar).
        riser_h = 0.050
        for sign, name in ((1.0, "riser_right"), (-1.0, "riser_left")):
            _box(
                body,
                (0.016, 0.016, riser_h),
                (
                    sign * (r.cart_width * 0.38),
                    r.cart_depth / 2.0 - 0.014,
                    z_top + tray_t + riser_h / 2.0 - 0.003,
                ),
                mats["accent"],
                f"push_handle_{name}",
            )
        # Horizontal push handle bar spanning the risers.
        _box(
            body,
            (r.cart_width * 0.80, 0.020, 0.018),
            (0.0, r.cart_depth / 2.0 - 0.014, z_top + tray_t + riser_h - 0.005),
            mats["accent"],
            "push_handle_bar",
        )
    elif r.frame_form == "rounded_tower":
        # Overhanging top rim band, embed into the top cap.
        band_t = 0.010
        _box(
            body,
            (r.cart_width + 0.014, r.cart_depth + 0.014, band_t),
            (0.0, 0.0, z_top + band_t / 2.0 - 0.003),
            mats["accent"],
            "top_rim_band",
        )
    elif r.frame_form == "slim_service_stand":
        # Full-width top handle plate flush on the top cap; spanning the full
        # cart_width ensures it touches every pedestal's top_cap (avoids
        # disconnected island in twin_bank layout).
        strap_t = 0.014
        _box(
            body,
            (r.cart_width * 0.96, r.cart_depth * 0.60, strap_t),
            (0.0, 0.0, z_top + strap_t / 2.0 - 0.003),
            mats["accent"],
            "top_service_handle",
        )
    else:  # rectangular_cabinet — just a slim top rim.
        rim_t = 0.008
        _box(
            body,
            (r.cart_width * 0.96, r.cart_depth * 0.94, rim_t),
            (0.0, 0.0, z_top + rim_t / 2.0 - 0.002),
            mats["accent"],
            "top_rim",
        )


def _build_body(
    body,
    r: ResolvedStorageCartConfig,
    mats: dict[str, object],
) -> None:
    # For each bank X center, build a pedestal.
    for i, cx in enumerate(r.bank_x_centers):
        prefix = "ped" if r.drawer_layout == "single_bank" else (f"ped_{'l' if i == 0 else 'r'}")
        _build_pedestal(body, r, mats, center_x=cx, prefix=prefix)
    # For twin_bank fill the outer walls too (so the cart still has a real outer
    # shell in +/-X direction beyond the two pedestals; small connecting strip).
    if r.drawer_layout == "twin_bank":
        # Divider between the two banks.
        div_x = 0.0
        div_w = 0.010
        ped_h = r.cart_height - r.top_cap_t - r.plinth_h
        z_body_mid = r.caster_gap + r.plinth_h + ped_h / 2.0
        _box(
            body,
            (div_w, r.cart_depth - BACK_T, ped_h),
            (div_x, -BACK_T / 2.0, z_body_mid),
            mats["shell"],
            "bank_divider",
        )
    _build_top_hardware(body, r, mats)


# ---------------------------------------------------------------------------
# Drawer part construction.
# ---------------------------------------------------------------------------
def _build_drawer(
    drawer,
    r: ResolvedStorageCartConfig,
    mats: dict[str, object],
) -> None:
    """Build a drawer part in its rest-pose local frame.

    Drawer local origin sits at the joint origin (pedestal front face at drawer Z).
    Front panel outer face is at y=0; box extends into +y (into the pedestal).
    Drawer slides toward -Y in the body frame; child-local +Y == body -Y direction
    because the joint's axis is (0,-1,0). So drawer-local +Y = "into pedestal".
    """
    ft = 0.016
    fw = r.drawer_front_width
    fh = r.drawer_front_height
    bw = r.drawer_box_width
    bd = r.drawer_box_depth
    bh = r.drawer_box_height

    # Front panel — the visible face. Panel outer face at y=0, extends into +y.
    _box(drawer, (fw, ft, fh), (0.0, ft / 2.0, 0.0), mats["drawer_front"], "front_panel")
    # Drawer box behind the front panel, extending further into +y.
    box_y_center = ft + bd / 2.0
    for sign, name in ((1.0, "box_side_right"), (-1.0, "box_side_left")):
        _box(
            drawer,
            (0.010, bd, bh),
            (sign * (bw / 2.0 - 0.005), box_y_center, 0.0),
            mats["drawer_box"],
            name,
        )
    _box(
        drawer,
        (bw - 0.020, 0.010, bh),
        (0.0, ft + bd - 0.005, 0.0),
        mats["drawer_box"],
        "box_back",
    )
    _box(
        drawer,
        (bw - 0.020, bd - 0.020, 0.008),
        (0.0, box_y_center, -bh / 2.0 + 0.004),
        mats["drawer_box"],
        "box_bottom",
    )
    # Pull handle centered near top of front panel.
    _box(
        drawer,
        (fw * 0.55, 0.010, 0.012),
        (0.0, -0.005, fh * 0.28),
        mats["hardware"],
        "drawer_pull",
    )


# ---------------------------------------------------------------------------
# Caster parts.
# ---------------------------------------------------------------------------
def _build_fork(fork, r: ResolvedStorageCartConfig, mats: dict[str, object]) -> None:
    """Swivel fork. Local origin is at the swivel joint (body-floor contact).
    The wheel joint child origin lives at (0, FORK_DROP, axle_z), so the axle
    shaft must be authored at that same (x=0, y=FORK_DROP, z=axle_z) point in
    fork-local coords for the geometry-origin gate to pass on the wheel joint.
    Legs and post must also form a single connected island (no gaps).
    """
    axle_z = -r.caster_gap + WHEEL_R
    # Top mount plate.
    _box(fork, (0.048, 0.048, 0.010), (0.0, 0.0, -0.005), mats["fork"], "fork_plate")
    # Vertical post (down from plate) — thicker so it links directly into legs.
    post_bot = axle_z + 0.006
    post_top = -0.010
    post_h = max(post_top - post_bot, 0.010)
    post_w = WHEEL_W + 0.024  # wider than legs so the plate → legs are one solid
    _box(
        fork,
        (post_w, 0.020, post_h),
        (0.0, FORK_DROP * 0.4, (post_top + post_bot) / 2.0),
        mats["fork"],
        "fork_post",
    )
    # Side legs — cantilever from post outer face down to axle Z; embed 1mm into
    # post to guarantee connectedness.
    leg_x = WHEEL_W / 2.0 + 0.010
    leg_top = post_top
    leg_bot = axle_z - 0.006
    for sign, name in ((1.0, "leg_right"), (-1.0, "leg_left")):
        _box(
            fork,
            (0.014, 0.026, leg_top - leg_bot),
            (sign * leg_x, FORK_DROP * 0.6, (leg_top + leg_bot) / 2.0),
            mats["fork"],
            name,
        )
    # Axle shaft along X through wheel. Placed at (0, FORK_DROP, axle_z) so the
    # wheel joint origin (0, FORK_DROP, axle_z) sits inside the axle geometry.
    _box(
        fork,
        (WHEEL_W + 0.020, 0.014, 0.014),
        (0.0, FORK_DROP, axle_z),
        mats["hardware"],
        "fork_axle",
    )


def _build_bracket(bracket, r: ResolvedStorageCartConfig, mats: dict[str, object]) -> None:
    """Fixed (non-swivel) bracket. Everything hangs directly below body; the
    wheel joint child origin lives at (0, 0, axle_z), so the axle shaft is
    authored at (0, 0, axle_z). All visuals form one connected island.
    """
    axle_z = -r.caster_gap + WHEEL_R
    _box(bracket, (0.048, 0.048, 0.010), (0.0, 0.0, -0.005), mats["fork"], "bracket_plate")
    post_bot = axle_z + 0.006
    post_top = -0.010
    post_h = max(post_top - post_bot, 0.010)
    post_w = WHEEL_W + 0.024
    _box(
        bracket,
        (post_w, 0.020, post_h),
        (0.0, 0.0, (post_top + post_bot) / 2.0),
        mats["fork"],
        "bracket_post",
    )
    leg_x = WHEEL_W / 2.0 + 0.010
    leg_top = post_top
    leg_bot = axle_z - 0.006
    for sign, name in ((1.0, "leg_right"), (-1.0, "leg_left")):
        _box(
            bracket,
            (0.014, 0.026, leg_top - leg_bot),
            (sign * leg_x, 0.0, (leg_top + leg_bot) / 2.0),
            mats["fork"],
            name,
        )
    # Axle at wheel joint origin (0, 0, axle_z).
    _box(
        bracket,
        (WHEEL_W + 0.020, 0.014, 0.014),
        (0.0, 0.0, axle_z),
        mats["hardware"],
        "bracket_axle",
    )


def _build_wheel(wheel, r: ResolvedStorageCartConfig, mats: dict[str, object]) -> None:
    """Wheel part; local origin at wheel center. Tire is a box (roll about +X).

    Asymmetric spoke/tread lug breaks Y/Z symmetry so rolling about +X actually
    shifts the world-frame AABB (required by Rule 5 motion QC).
    """
    # Tire as a thin flat box — collision friendly; simulates a wheel.
    _box(
        wheel,
        (WHEEL_W, 2 * WHEEL_R, 2 * WHEEL_R),
        (0.0, 0.0, 0.0),
        mats["wheel"],
        "tire",
    )
    # Hub cap band.
    _box(
        wheel,
        (WHEEL_W + 0.002, 0.024, 0.024),
        (0.0, 0.0, 0.0),
        mats["hardware"],
        "hub_cap",
    )
    # A single spoke/lug offset from center (breaks Y/Z symmetry so that
    # rotation about +X produces a visible AABB change; this stands in for
    # tread pattern / valve stem geometry in the source records).
    _box(
        wheel,
        (WHEEL_W + 0.001, 0.008, WHEEL_R * 1.4),
        (0.0, WHEEL_R * 0.55, 0.0),
        mats["hardware"],
        "wheel_spoke",
    )


def _build_brake_lever(lever, r: ResolvedStorageCartConfig, mats: dict[str, object]) -> None:
    """Brake lever pivoting about +X on the fork's outer boss."""
    _box(
        lever,
        (BRAKE_LEVER_W, BRAKE_LEVER_T, BRAKE_LEVER_LEN),
        (0.0, 0.010, -BRAKE_LEVER_LEN / 2.0 + BRAKE_PIVOT_R),
        mats["accent"],
        "brake_arm",
    )
    # Foot toe pad.
    _box(
        lever,
        (BRAKE_LEVER_W, BRAKE_LEVER_T + 0.004, 0.010),
        (0.0, 0.010, -BRAKE_LEVER_LEN + BRAKE_PIVOT_R),
        mats["accent"],
        "brake_toe",
    )


# ---------------------------------------------------------------------------
# Top-level build.
# ---------------------------------------------------------------------------
def build_storage_cart_with_drawers_on_wheels(
    config: StorageCartWithDrawersOnWheelsConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or StorageCartWithDrawersOnWheelsConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {
        role: model.material(f"storage_cart_{role}", rgba=palette[role])
        for role in ("shell", "drawer_front", "drawer_box", "accent", "fork", "wheel", "hardware")
    }

    body = model.part("body")
    _build_body(body, r, mats)
    body.inertial = Inertial.from_geometry(
        Box((r.cart_width, r.cart_depth, r.cart_height)),
        mass=32.0,
        origin=Origin(xyz=(0.0, 0.0, _body_z_mid(r))),
    )

    # Drawers: for each bank X center, N drawers.
    for bank_idx, cx in enumerate(r.bank_x_centers):
        bank_prefix = (
            "" if r.drawer_layout == "single_bank" else (f"{'l' if bank_idx == 0 else 'r'}_")
        )
        for i, cz in enumerate(r.drawer_center_z):
            dname = f"drawer_{bank_prefix}{i}"
            drawer = model.part(dname)
            _build_drawer(drawer, r, mats)
            drawer.inertial = Inertial.from_geometry(
                Box((r.drawer_front_width, r.drawer_box_depth, r.drawer_front_height)),
                mass=2.4,
                origin=Origin(xyz=(0.0, r.drawer_box_depth / 2.0, 0.0)),
            )
            joint_origin = (cx, -r.cart_depth / 2.0, r.caster_gap + cz)
            axis = (0.0, -1.0, 0.0)
            limits = MotionLimits(
                lower=0.0,
                upper=r.drawer_travel,
                effort=60.0,
                velocity=0.30,
            )
            model.articulation(
                f"body_to_{dname}",
                ArticulationType.PRISMATIC,
                parent=body,
                child=drawer,
                origin=Origin(xyz=joint_origin),
                axis=axis,
                motion_limits=limits,
                meta=_joint_meta(ArticulationType.PRISMATIC, axis, joint_origin, limits),
            )

    # Casters — 4 corner subtrees. Each has a swivel or fixed head + a wheel.
    for j, (cx, cy) in enumerate(r.caster_positions):
        kind = r.caster_kinds[j]
        head_name = f"caster_fork_{j}" if kind != "fixed" else f"caster_bracket_{j}"
        head = model.part(head_name)
        if kind == "fixed":
            _build_bracket(head, r, mats)
            head_bbox = Box((0.048, 0.048, r.caster_gap))
        else:
            _build_fork(head, r, mats)
            head_bbox = Box((0.048, 0.048, r.caster_gap))
        head.inertial = Inertial.from_geometry(
            head_bbox, mass=0.35, origin=Origin(xyz=(0.0, 0.0, -r.caster_gap / 2.0))
        )
        # Head joint (body -> head).
        head_origin = (cx, cy, r.caster_gap)  # on floor bottom (world z = caster_gap).
        if kind == "fixed":
            model.articulation(
                f"body_to_{head_name}",
                ArticulationType.FIXED,
                parent=body,
                child=head,
                origin=Origin(xyz=head_origin),
            )
        else:
            # Swivel: use REVOLUTE with a full-range so joint origin gate is met
            # while still giving finite bounds (source records used REVOLUTE).
            swivel_limits = MotionLimits(
                lower=-r.swivel_range, upper=r.swivel_range, effort=8.0, velocity=6.0
            )
            axis = (0.0, 0.0, 1.0)
            model.articulation(
                f"body_to_{head_name}",
                ArticulationType.REVOLUTE,
                parent=body,
                child=head,
                origin=Origin(xyz=head_origin),
                axis=axis,
                motion_limits=swivel_limits,
                meta=_joint_meta(ArticulationType.REVOLUTE, axis, head_origin, swivel_limits),
            )

        # Wheel part.
        wname = f"caster_wheel_{j}"
        wheel = model.part(wname)
        _build_wheel(wheel, r, mats)
        wheel.inertial = Inertial.from_geometry(
            Box((WHEEL_W, 2 * WHEEL_R, 2 * WHEEL_R)),
            mass=0.5,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        # Small Y offset (fork drop equivalent) so a swivel joint about +Z at
        # the head origin actually translates the wheel center — necessary for
        # the swivel-motion pose check to detect rotation.
        wheel_y_offset = FORK_DROP if kind != "fixed" else 0.0
        wheel_origin = (0.0, wheel_y_offset, -r.caster_gap + WHEEL_R)
        w_axis = (1.0, 0.0, 0.0)
        model.articulation(
            f"{head_name}_to_{wname}",
            ArticulationType.CONTINUOUS,
            parent=head,
            child=wheel,
            origin=Origin(xyz=wheel_origin),
            axis=w_axis,
            motion_limits=MotionLimits(effort=4.0, velocity=20.0),
            meta=_joint_meta(ArticulationType.CONTINUOUS, w_axis, wheel_origin, None),
        )

        # Optional brake lever for braked_swivel_caster.
        if kind == "braked":
            lname = f"brake_lever_{j}"
            lever = model.part(lname)
            _build_brake_lever(lever, r, mats)
            lever.inertial = Inertial.from_geometry(
                Box((BRAKE_LEVER_W, BRAKE_LEVER_T, BRAKE_LEVER_LEN)),
                mass=0.05,
                origin=Origin(xyz=(0.0, 0.010, -BRAKE_LEVER_LEN / 2.0)),
            )
            lever_origin = (
                WHEEL_W / 2.0 + 0.020,
                0.0,
                -r.caster_gap + WHEEL_R + 0.020,
            )
            l_axis = (1.0, 0.0, 0.0)
            l_limits = MotionLimits(lower=0.0, upper=r.brake_angle, effort=20.0, velocity=2.0)
            model.articulation(
                f"{head_name}_to_{lname}",
                ArticulationType.REVOLUTE,
                parent=head,
                child=lever,
                origin=Origin(xyz=lever_origin),
                axis=l_axis,
                motion_limits=l_limits,
                meta=_joint_meta(ArticulationType.REVOLUTE, l_axis, lever_origin, l_limits),
            )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_storage_cart_with_drawers_on_wheels(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_storage_cart_with_drawers_on_wheels(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------
def run_storage_cart_with_drawers_on_wheels_tests(
    object_model: ArticulatedObject,
    config: StorageCartWithDrawersOnWheelsConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("body part present", "body" in part_names)
    body = object_model.get_part("body")

    # --- Drawer inventory (per bank). ---
    drawer_prefixes = [""] if r.drawer_layout == "single_bank" else ["l_", "r_"]
    total_drawers_expected = r.drawer_count * len(drawer_prefixes)
    drawer_parts = sorted(n for n in part_names if n.startswith("drawer_"))
    ctx.check(
        "drawer part count matches config",
        len(drawer_parts) == total_drawers_expected,
        details=f"expected {total_drawers_expected}, got {drawer_parts}",
    )
    for bank_prefix in drawer_prefixes:
        for i in range(r.drawer_count):
            dname = f"drawer_{bank_prefix}{i}"
            jname = f"body_to_{dname}"
            ctx.check(f"{jname} joint present", jname in joint_names)
            j = object_model.get_articulation(jname)
            ctx.check(
                f"{jname} is PRISMATIC along -Y",
                j.articulation_type == ArticulationType.PRISMATIC
                and tuple(j.axis) == (0.0, -1.0, 0.0),
                details=f"type={j.articulation_type}, axis={j.axis}",
            )
            lim = j.motion_limits
            ctx.check(
                f"{jname} has positive pull-out travel",
                lim is not None and lim.lower == 0.0 and lim.upper > 0.10,
                details=f"limits={lim}",
            )

    # --- Caster inventory. ---
    for j_idx in range(4):
        kind = r.caster_kinds[j_idx]
        head_name = f"caster_fork_{j_idx}" if kind != "fixed" else f"caster_bracket_{j_idx}"
        wname = f"caster_wheel_{j_idx}"
        ctx.check(f"{head_name} present", head_name in part_names)
        ctx.check(f"{wname} present", wname in part_names)
        head_joint = object_model.get_articulation(f"body_to_{head_name}")
        wheel_joint = object_model.get_articulation(f"{head_name}_to_{wname}")
        if kind == "fixed":
            ctx.check(
                f"{head_name} is FIXED to body",
                head_joint.articulation_type == ArticulationType.FIXED,
                details=f"type={head_joint.articulation_type}",
            )
        else:
            ctx.check(
                f"{head_name} swivels about +Z (REVOLUTE)",
                head_joint.articulation_type == ArticulationType.REVOLUTE
                and abs(head_joint.axis[2]) > 0.99,
                details=f"type={head_joint.articulation_type}, axis={head_joint.axis}",
            )
        ctx.check(
            f"{wname} rolls CONTINUOUS about +X",
            wheel_joint.articulation_type == ArticulationType.CONTINUOUS
            and abs(wheel_joint.axis[0]) > 0.99,
            details=f"type={wheel_joint.articulation_type}, axis={wheel_joint.axis}",
        )
        if kind == "braked":
            lname = f"brake_lever_{j_idx}"
            ctx.check(f"{lname} present", lname in part_names)
            brake_joint = object_model.get_articulation(f"{head_name}_to_{lname}")
            ctx.check(
                f"{lname} pivots REVOLUTE about +X",
                brake_joint.articulation_type == ArticulationType.REVOLUTE
                and abs(brake_joint.axis[0]) > 0.99,
                details=f"axis={brake_joint.axis}",
            )

    # --- Overlap allowances: captured-pin / sliding cavity. ---
    # Drawer body sides overlap the pedestal cavity when closed.
    for bank_prefix in drawer_prefixes:
        for i in range(r.drawer_count):
            drawer = object_model.get_part(f"drawer_{bank_prefix}{i}")
            ctx.allow_overlap(
                body,
                drawer,
                reason="drawer box nests inside pedestal cavity when closed",
            )
        # Adjacent stacked drawer fronts share the pedestal opening plane.
        for i in range(r.drawer_count - 1):
            ctx.allow_overlap(
                object_model.get_part(f"drawer_{bank_prefix}{i}"),
                object_model.get_part(f"drawer_{bank_prefix}{i + 1}"),
                reason="adjacent stacked drawer fronts share the opening plane",
            )
    # Caster overlaps: the swivel post + axle + wheel are captured pin geometry.
    for j_idx in range(4):
        kind = r.caster_kinds[j_idx]
        head_name = f"caster_fork_{j_idx}" if kind != "fixed" else f"caster_bracket_{j_idx}"
        wname = f"caster_wheel_{j_idx}"
        head_part = object_model.get_part(head_name)
        wheel_part = object_model.get_part(wname)
        ctx.allow_overlap(
            head_part,
            wheel_part,
            reason="captured axle: fork/bracket axle passes through wheel hub",
        )
        # Body vs caster head: swivel plate touches body floor.
        ctx.allow_overlap(
            body,
            head_part,
            reason="caster mount plate seats against body floor bottom",
        )
        if kind == "braked":
            lname = f"brake_lever_{j_idx}"
            lever_part = object_model.get_part(lname)
            ctx.allow_overlap(
                head_part,
                lever_part,
                reason="brake lever pivots on the fork outer boss (captured pin)",
            )
            ctx.allow_overlap(
                wheel_part,
                lever_part,
                reason="brake lever toe contacts the tire when engaged",
            )
    # Isolated-part relief for wheels (they connect only via joint; small
    # sliding clearance keeps them from touching parent geometry at rest).
    for j_idx in range(4):
        ctx.allow_isolated_part(
            object_model.get_part(f"caster_wheel_{j_idx}"),
            reason=(
                "Wheel is joined by CONTINUOUS +X to the fork/bracket axle; small "
                "clearance keeps the tire from bearing on parent geometry."
            ),
        )

    # --- Targeted pose motion semantics (Rule 5). ---
    # 1) Drawer 0 moves toward -Y when opened.
    first_drawer_name = f"drawer_{drawer_prefixes[0]}0"
    if r.drawer_count > 0:
        j0 = object_model.get_articulation(f"body_to_{first_drawer_name}")
        drawer0 = object_model.get_part(first_drawer_name)
        rest = ctx.part_world_position(drawer0)
        with ctx.pose({j0: j0.motion_limits.upper}):
            extended = ctx.part_world_position(drawer0)
        ctx.check(
            f"{first_drawer_name} extends toward -Y",
            rest is not None and extended is not None and extended[1] < rest[1] - 0.05,
            details=f"rest={rest}, extended={extended}",
        )
    # 2) Wheel rotates: the wheel_spoke element (offset from wheel center) shifts
    # when the wheel rolls about +X.
    w0 = object_model.get_part("caster_wheel_0")
    wj0 = object_model.get_articulation(
        f"{'caster_fork_0' if r.caster_kinds[0] != 'fixed' else 'caster_bracket_0'}_to_caster_wheel_0"
    )
    rest_spoke = ctx.part_element_world_aabb(w0, elem="wheel_spoke")
    with ctx.pose({wj0: math.pi / 2.0}):
        spin_spoke = ctx.part_element_world_aabb(w0, elem="wheel_spoke")
    ctx.check(
        "wheel 0 spins about +X (spoke shifts visibly)",
        rest_spoke is not None
        and spin_spoke is not None
        and (
            abs(spin_spoke[0][2] - rest_spoke[0][2]) > 1e-3
            or abs(spin_spoke[0][1] - rest_spoke[0][1]) > 1e-3
        ),
        details=f"rest={rest_spoke}, spin={spin_spoke}",
    )
    # 3) Swivel semantics: for swivel casters, yawing the fork rotates the wheel
    # position off the local Y axis.
    if r.caster_kinds[0] in ("swivel", "braked"):
        head_name = "caster_fork_0"
        sw_joint = object_model.get_articulation(f"body_to_{head_name}")
        w0_rest = ctx.part_world_position(w0)
        with ctx.pose({sw_joint: r.swivel_range * 0.6}):
            w0_yaw = ctx.part_world_position(w0)
        ctx.check(
            "caster_fork_0 yaws (wheel translates around swivel axis)",
            w0_rest is not None
            and w0_yaw is not None
            and math.hypot(w0_yaw[0] - w0_rest[0], w0_yaw[1] - w0_rest[1]) > 0.005,
            details=f"rest={w0_rest}, yaw={w0_yaw}",
        )

    # Baseline sampled-pose motion QC & geometry-origin gate.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    return ctx.report()


__all__ = [
    "StorageCartWithDrawersOnWheelsConfig",
    "ResolvedStorageCartConfig",
    "build_storage_cart_with_drawers_on_wheels",
    "build_seeded_storage_cart_with_drawers_on_wheels",
    "config_from_seed",
    "resolve_config",
    "run_storage_cart_with_drawers_on_wheels_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
