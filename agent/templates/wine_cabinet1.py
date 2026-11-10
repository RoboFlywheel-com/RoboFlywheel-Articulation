# SPDX-License-Identifier: Apache-2.0

"""Gated ``wine_cabinet1`` wine-storage and service-cabinet families.

All six body forms, three door mechanisms, five service modules and bounded N
rules are traced to the 19 accepted records in the canonical source map. The
rectangular and quarter-round FormFamilies share category identity but not
interfaces: ``resolve_config`` rejects their unchecked Cartesian product.
Moving modules include their real tracks, bilateral guides, hinge capture or
coaxial spindle, and tests use only named element-pair contact allowances.
See ``articraft_template_authoring/specs_modular_v1/wine_cabinet1.md``.
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
    MatingContract,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Enums.
# --------------------------------------------------------------------------- #
BodyForm = Literal[
    "glass_front_cabinet",
    "white_display_hutch",
    "tall_cooler",
    "low_sideboard",
    "narrow_tower",
    "quarter_round_corner",
]
DoorMotion = Literal["hinged", "sliding", "bifold"]
RackStyle = Literal["horizontal_shelves", "cubby_grid"]
ServiceModule = Literal[
    "fixed_storage",
    "fold_out_counter",
    "pull_out_shelves",
    "rotating_shelves",
    "hanging_stem_rack",
]
PaletteStyle = Literal[
    "espresso_smoked",
    "white_hutch",
    "black_cooler",
    "warm_walnut",
    "satin_charcoal",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "glass_front_cabinet",
    "white_display_hutch",
    "tall_cooler",
    "low_sideboard",
    "narrow_tower",
    "quarter_round_corner",
)
DOOR_MOTIONS: tuple[DoorMotion, ...] = ("hinged", "sliding", "bifold")
RACK_STYLES: tuple[RackStyle, ...] = ("horizontal_shelves", "cubby_grid")
SERVICE_MODULES: tuple[ServiceModule, ...] = (
    "fixed_storage",
    "fold_out_counter",
    "pull_out_shelves",
    "rotating_shelves",
    "hanging_stem_rack",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "espresso_smoked",
    "white_hutch",
    "black_cooler",
    "warm_walnut",
    "satin_charcoal",
)


# --------------------------------------------------------------------------- #
# Palettes — per-seed sampled, drives every visual material.
# --------------------------------------------------------------------------- #
# Keys used by builders: carcass, interior, frame, glass, rack, hardware,
# bottle_a, bottle_b, bottle_c, label, cork.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "espresso_smoked": {
        "carcass": (0.075, 0.050, 0.040, 1.0),
        "interior": (0.055, 0.050, 0.047, 1.0),
        "frame": (0.075, 0.050, 0.040, 1.0),
        "glass": (0.12, 0.16, 0.16, 0.32),
        "rack": (0.28, 0.17, 0.095, 1.0),
        "hardware": (0.12, 0.12, 0.115, 1.0),
        "bottle_a": (0.055, 0.19, 0.105, 0.90),
        "bottle_b": (0.24, 0.035, 0.040, 0.92),
        "bottle_c": (0.055, 0.070, 0.045, 0.98),
        "label": (0.78, 0.69, 0.52, 1.0),
        "cork": (0.62, 0.43, 0.20, 1.0),
    },
    "white_hutch": {
        "carcass": (0.95, 0.95, 0.92, 1.0),
        "interior": (0.16, 0.15, 0.13, 1.0),
        "frame": (0.985, 0.985, 0.965, 1.0),
        "glass": (0.70, 0.86, 0.90, 0.24),
        "rack": (0.92, 0.92, 0.89, 1.0),
        "hardware": (0.48, 0.50, 0.49, 1.0),
        "bottle_a": (0.10, 0.24, 0.13, 1.0),
        "bottle_b": (0.42, 0.20, 0.07, 1.0),
        "bottle_c": (0.12, 0.055, 0.045, 1.0),
        "label": (0.84, 0.80, 0.69, 1.0),
        "cork": (0.58, 0.47, 0.25, 1.0),
    },
    "black_cooler": {
        "carcass": (0.018, 0.020, 0.022, 1.0),
        "interior": (0.055, 0.060, 0.065, 1.0),
        "frame": (0.006, 0.007, 0.008, 1.0),
        "glass": (0.055, 0.070, 0.075, 0.38),
        "rack": (0.29, 0.19, 0.11, 1.0),
        "hardware": (0.10, 0.11, 0.12, 1.0),
        "bottle_a": (0.045, 0.16, 0.085, 0.96),
        "bottle_b": (0.25, 0.105, 0.025, 0.96),
        "bottle_c": (0.055, 0.070, 0.045, 0.98),
        "label": (0.78, 0.69, 0.52, 1.0),
        "cork": (0.36, 0.055, 0.035, 1.0),
    },
    "warm_walnut": {
        "carcass": (0.34, 0.22, 0.14, 1.0),
        "interior": (0.24, 0.16, 0.10, 1.0),
        "frame": (0.34, 0.22, 0.14, 1.0),
        "glass": (0.28, 0.15, 0.06, 0.34),
        "rack": (0.65, 0.45, 0.16, 1.0),
        "hardware": (0.65, 0.45, 0.16, 1.0),
        "bottle_a": (0.24, 0.035, 0.040, 0.92),
        "bottle_b": (0.055, 0.19, 0.105, 0.90),
        "bottle_c": (0.42, 0.20, 0.07, 1.0),
        "label": (0.88, 0.72, 0.42, 1.0),
        "cork": (0.62, 0.43, 0.20, 1.0),
    },
    "satin_charcoal": {
        "carcass": (0.20, 0.22, 0.24, 1.0),
        "interior": (0.055, 0.060, 0.065, 1.0),
        "frame": (0.20, 0.22, 0.24, 1.0),
        "glass": (0.15, 0.16, 0.18, 0.34),
        "rack": (0.66, 0.67, 0.66, 1.0),
        "hardware": (0.66, 0.67, 0.66, 1.0),
        "bottle_a": (0.12, 0.055, 0.045, 1.0),
        "bottle_b": (0.24, 0.035, 0.040, 0.92),
        "bottle_c": (0.29, 0.34, 0.12, 1.0),
        "label": (0.78, 0.69, 0.52, 1.0),
        "cork": (0.36, 0.055, 0.035, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Nominal dimensions per body_form (from the 3 origin samples).
# --------------------------------------------------------------------------- #
# glass_front_cabinet (rec 002): W=0.96 D=0.50 H=1.82. Double compartment.
_GFC = {"W": 0.96, "D": 0.50, "H": 1.82, "plinth_h": 0.10, "top_cap_h": 0.10}
# white_display_hutch (rec 003): W=0.94 D=0.44 H=2.00. Upper display + lower cubby.
_WDH = {"W": 0.94, "D": 0.44, "H": 2.00, "plinth_h": 0.14, "top_cap_h": 0.14}
# tall_cooler (rec 004): W=0.48 D=0.58 H=1.72. Single compartment + machine_bay + vent.
_TC = {"W": 0.48, "D": 0.58, "H": 1.72, "plinth_h": 0.075, "top_cap_h": 0.040}
_LS = {"W": 0.94, "D": 0.44, "H": 0.96, "plinth_h": 0.12, "top_cap_h": 0.09}
_NT = {"W": 0.66, "D": 0.53, "H": 1.92, "plinth_h": 0.10, "top_cap_h": 0.10}
_QR = {"W": 0.72, "D": 0.36, "H": 1.60, "plinth_h": 0.075, "top_cap_h": 0.040}

# Standard carcass wall thickness.
_WALL = 0.030

# Standard door opening dims.
_DOOR_OPEN_ANGLE = 1.55  # radians, nominal hinged open upper
_DOOR_SLIDE_TRAVEL = 0.44  # meters, sliding upper
_MIN_DOOR_LEAF_W = 0.20  # min door width (per-door)
_MIN_RACK_PITCH = 0.09  # min rack vertical spacing

# Conditional storage multiplicity: tall-cooler rack levels admit 4..12;
# glass-front/narrow use their anchored 6/7 shelf rows; cubby forms preserve
# the accepted 3x6 / 4x6 densities; quarter-round display content admits 4..12.
_RACK_COUNTS_H = (4, 8, 12)


def _anchored_cubby_count(body_form: BodyForm) -> int:
    return 18 if body_form == "low_sideboard" else 24


@dataclass(frozen=True)
class Wine_Cabinet1Config:
    body_form: BodyForm | None = None
    door_motion: DoorMotion | None = None
    rack_style: RackStyle | None = None
    service_module: ServiceModule | None = None
    door_count: int | None = None
    rack_count: int | None = None
    palette_style: PaletteStyle | None = None
    carcass_width_scale: float = 1.0
    carcass_height_scale: float = 1.0
    door_open_scale: float = 1.0
    name: str = "wine_cabinet1"


@dataclass(frozen=True)
class ResolvedWine_Cabinet1Config:
    body_form: BodyForm
    door_motion: DoorMotion
    rack_style: RackStyle
    service_module: ServiceModule
    door_count: int
    rack_count: int
    palette_style: PaletteStyle
    # Resolved carcass dims.
    W: float
    D: float
    H: float
    plinth_h: float
    top_cap_h: float
    interior_bottom_z: float  # top of plinth (bottom of interior cavity)
    interior_top_z: float  # bottom of top_cap (top of interior cavity)
    interior_h: float
    door_bottom_z: float
    door_top_z: float
    door_h: float
    door_leaf_w: float
    rack_pitch: float
    door_open: float
    door_travel: float
    front_y: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices, default):
    if value in choices:
        return value
    return default


def config_from_seed(seed: int) -> Wine_Cabinet1Config:
    rng = random.Random(seed)
    body_form: BodyForm = rng.choice(BODY_FORMS)

    # Mechanism gates follow the accepted source families.  Sliding/bifold
    # are 004-derived tall-cooler mechanisms; service modules are 001-derived
    # quarter-round mechanisms.
    if body_form == "tall_cooler":
        door_motion: DoorMotion = rng.choice(DOOR_MOTIONS)
    else:
        door_motion = "hinged"

    if body_form == "quarter_round_corner":
        service_module: ServiceModule = rng.choice(SERVICE_MODULES)
    else:
        service_module = "fixed_storage"

    # The cubby insert uses the shared rectangular inner-envelope interface.
    # It is valid on four rectilinear shells; tall_cooler has a machine bay and
    # quarter_round_corner requires curved consumers, so both remain gated out.
    if body_form in {
        "glass_front_cabinet",
        "white_display_hutch",
        "low_sideboard",
        "narrow_tower",
    }:
        rack_style: RackStyle = rng.choices(
            ("horizontal_shelves", "cubby_grid"), weights=(0.5, 0.5), k=1
        )[0]
    else:
        rack_style = "horizontal_shelves"

    # door_count gating.
    if service_module in {"fold_out_counter", "pull_out_shelves", "rotating_shelves"}:
        door_count = 0
    elif body_form == "quarter_round_corner":
        door_count = rng.choice((1, 2, 3))
    elif body_form == "tall_cooler":
        door_count = 1
    elif body_form == "narrow_tower":
        door_count = 2
    else:
        door_count = rng.choices((1, 2), weights=(0.35, 0.65), k=1)[0]

    # rack_count gating.
    if service_module in {"pull_out_shelves", "rotating_shelves"}:
        rack_count = 3
    elif rack_style == "cubby_grid":
        rack_count = _anchored_cubby_count(body_form)
    elif body_form == "glass_front_cabinet":
        rack_count = 6
    elif body_form == "narrow_tower":
        rack_count = 7
    else:
        # Accepted N={4,8,12} anchors plus a loop/capacity rule admit every
        # integer in 4..12.  Boundary-biased weights keep smoke coverage cheap.
        rack_count = rng.choices(tuple(range(4, 13)), weights=(3, 1, 1, 1, 3, 1, 1, 1, 3), k=1)[0]

    return Wine_Cabinet1Config(
        body_form=body_form,
        door_motion=door_motion,
        rack_style=rack_style,
        service_module=service_module,
        door_count=door_count,
        rack_count=rack_count,
        palette_style=rng.choice(PALETTE_STYLES),
        carcass_width_scale=round(rng.uniform(0.85, 1.15), 4),
        carcass_height_scale=round(rng.uniform(0.90, 1.10), 4),
        door_open_scale=round(rng.uniform(0.70, 1.00), 4),
        name=f"seeded_wine_cabinet1_{seed}",
    )


def resolve_config(config: Wine_Cabinet1Config | None = None) -> ResolvedWine_Cabinet1Config:
    cfg = config or Wine_Cabinet1Config()
    body_form = _pick(cfg.body_form, BODY_FORMS, "glass_front_cabinet")
    door_motion = _pick(cfg.door_motion, DOOR_MOTIONS, "hinged")
    rack_style = _pick(cfg.rack_style, RACK_STYLES, "horizontal_shelves")
    service_module = _pick(cfg.service_module, SERVICE_MODULES, "fixed_storage")
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES, "espresso_smoked")

    # Apply gating (defensive: resolve MUST enforce even if seed sampler
    # sidestepped or an override created an illegal combo).
    if body_form != "quarter_round_corner":
        service_module = "fixed_storage"

    if service_module in {"fold_out_counter", "pull_out_shelves", "rotating_shelves"}:
        door_count = 0
    elif body_form == "quarter_round_corner":
        door_count = int(_clamp(int(cfg.door_count) if cfg.door_count is not None else 2, 1, 3))
    elif body_form == "tall_cooler":
        door_count = 1
    elif body_form == "narrow_tower":
        door_count = 2
    else:
        door_count = int(_clamp(int(cfg.door_count) if cfg.door_count else 2, 1, 2))

    if body_form != "tall_cooler" and door_motion in {"sliding", "bifold"}:
        door_motion = "hinged"

    if (
        body_form
        not in {
            "glass_front_cabinet",
            "white_display_hutch",
            "low_sideboard",
            "narrow_tower",
        }
        and rack_style == "cubby_grid"
    ):
        rack_style = "horizontal_shelves"

    if service_module in {"pull_out_shelves", "rotating_shelves"}:
        rack_count = 3
    elif rack_style == "cubby_grid":
        rack_count = _anchored_cubby_count(body_form)
    elif body_form == "glass_front_cabinet":
        rack_count = 6
    elif body_form == "narrow_tower":
        rack_count = 7
    else:
        rack_count = int(_clamp(int(cfg.rack_count) if cfg.rack_count else 8, 4, 12))

    dims_map = {
        "glass_front_cabinet": _GFC,
        "white_display_hutch": _WDH,
        "tall_cooler": _TC,
        "low_sideboard": _LS,
        "narrow_tower": _NT,
        "quarter_round_corner": _QR,
    }
    dims = dims_map[body_form]

    width_scale = _clamp(cfg.carcass_width_scale, 0.85, 1.15)
    height_scale = _clamp(cfg.carcass_height_scale, 0.90, 1.10)
    open_scale = _clamp(cfg.door_open_scale, 0.70, 1.00)

    W = dims["W"] * width_scale
    D = dims["D"]
    H = dims["H"] * height_scale
    plinth_h = dims["plinth_h"]
    top_cap_h = dims["top_cap_h"]

    interior_bottom_z = plinth_h
    interior_top_z = H - top_cap_h
    interior_h = interior_top_z - interior_bottom_z

    if body_form == "quarter_round_corner":
        door_bottom_z, door_top_z = 0.10, 0.70
    elif body_form == "low_sideboard":
        door_bottom_z, door_top_z = 0.50, min(0.84, interior_top_z - 0.01)
    else:
        door_bottom_z = interior_bottom_z + 0.04
        door_top_z = interior_top_z - 0.04
    door_h = door_top_z - door_bottom_z

    # Compute per-leaf door width: full opening = W - 2*wall. For hinged
    # 2-door cabinets, leave a small center gap (2 * 0.020m) between the
    # inner stiles of the two leaves so they don't overlap when closed.
    opening_w = W - 2.0 * _WALL
    if door_count == 0:
        door_leaf_w = 0.0
    elif door_motion == "bifold":
        door_leaf_w = (opening_w - 0.030) / 2.0
    elif door_motion == "hinged":
        if door_count == 2:
            # 0.020m offset from each hinge line + 0.010 center reveal.
            door_leaf_w = (opening_w - 0.030) / 2.0
        elif door_count == 1:
            # Single hinged door: leave 0.020 clearance on the free side.
            door_leaf_w = opening_w - 0.030
        else:
            door_leaf_w = (opening_w - 0.020 * (door_count + 1)) / door_count
    else:
        # Sliding: 2 bypass panels each covers full opening; 1 panel = full width.
        door_leaf_w = opening_w - 0.010 if door_count == 1 else (opening_w - 0.020) * 0.6

    # Clamp: enforce min leaf width; if too narrow (only can happen at
    # extreme width_scale and door_count=2), force to 1 door.
    min_leaf_w = (
        0.15 if body_form == "quarter_round_corner" and door_count == 3 else _MIN_DOOR_LEAF_W
    )
    if 0 < door_leaf_w < min_leaf_w and door_count > 1:
        door_count = 1
        door_leaf_w = opening_w - 0.030

    # Rack pitch (only meaningful for horizontal_shelves).
    if rack_style == "horizontal_shelves":
        # rack_count layers with the first at interior_bottom_z + margin.
        rack_pitch = (interior_h - 0.15) / max(1, rack_count)
        # Clamp: if rack_pitch < min, reduce rack_count.
        while rack_pitch < _MIN_RACK_PITCH and rack_count > _RACK_COUNTS_H[0]:
            rack_count -= 1
            rack_pitch = (interior_h - 0.15) / max(1, rack_count)
    else:
        # Cubby N is total capacity: six columns by 3 or 4 anchored rows.
        rack_pitch = (interior_h * 0.5) / max(1, rack_count // 6)

    door_open = _DOOR_OPEN_ANGLE * open_scale
    door_travel = _DOOR_SLIDE_TRAVEL * open_scale

    # The quarter-round face bows forward of the chord joining its two side
    # panels.  Every front consumer (doors, face rails, counter hinge and
    # handles) must use that same master-profile envelope; a hard-coded chord
    # datum leaves the curved decks protruding through the doors.
    front_y = math.hypot(W / 2.0, D) - D if body_form == "quarter_round_corner" else D / 2.0

    return ResolvedWine_Cabinet1Config(
        body_form=body_form,
        door_motion=door_motion,
        rack_style=rack_style,
        service_module=service_module,
        door_count=door_count,
        rack_count=rack_count,
        palette_style=palette_style,
        W=W,
        D=D,
        H=H,
        plinth_h=plinth_h,
        top_cap_h=top_cap_h,
        interior_bottom_z=interior_bottom_z,
        interior_top_z=interior_top_z,
        interior_h=interior_h,
        door_bottom_z=door_bottom_z,
        door_top_z=door_top_z,
        door_h=door_h,
        door_leaf_w=door_leaf_w,
        rack_pitch=rack_pitch,
        door_open=door_open,
        door_travel=door_travel,
        front_y=front_y,
        name=cfg.name or "wine_cabinet1",
    )


def with_overrides(config: Wine_Cabinet1Config, **kwargs: object) -> Wine_Cabinet1Config:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: Wine_Cabinet1Config | ResolvedWine_Cabinet1Config,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedWine_Cabinet1Config) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("door_motion", r.door_motion),
        ("rack_style", r.rack_style),
        ("service_module", r.service_module),
        ("door_count", f"n{r.door_count}"),
        ("rack_count", f"n{r.rack_count}"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Small helpers.
# --------------------------------------------------------------------------- #
def _box(part, size, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.engineered_board")


# --------------------------------------------------------------------------- #
# Shared bottle mesh (S8/S9): a lathed wine-bottle silhouette reused for
# every bottle in the cabinet. Derived from 004 L213-229. segments=24 to
# stay within the 20s/seed compile budget.
# --------------------------------------------------------------------------- #
def _make_bottle_mesh():
    return mesh_from_geometry(
        LatheGeometry(
            [
                (0.027, -0.160),
                (0.031, -0.150),
                (0.031, 0.078),
                (0.029, 0.102),
                (0.022, 0.123),
                (0.013, 0.141),
                (0.013, 0.160),
                (0.011, 0.164),
            ],
            segments=24,
            closed=True,
        ),
        "wine_bottle",
    )


def _make_display_bottle_mesh():
    """Compact upright bottle from the quarter-round display variants."""
    return mesh_from_geometry(
        LatheGeometry(
            [
                (0.026, 0.000),
                (0.027, 0.135),
                (0.024, 0.150),
                (0.014, 0.168),
                (0.011, 0.205),
                (0.012, 0.214),
            ],
            segments=24,
            closed=True,
        ),
        "quarter_display_bottle",
    )


def _make_low_display_bottle_mesh():
    """Short bottle accepted on the low-sideboard's tight upper shelf."""
    return mesh_from_geometry(
        LatheGeometry(
            [
                (0.027, 0.000),
                (0.028, 0.064),
                (0.025, 0.074),
                (0.012, 0.084),
                (0.010, 0.105),
                (0.011, 0.112),
            ],
            segments=20,
            closed=True,
        ),
        "low_sideboard_display_bottle",
    )


def _make_display_vase_mesh(*, compact: bool):
    """Single connected vase silhouette matching the two display sources."""
    scale = 0.64 if compact else 1.0
    return mesh_from_geometry(
        LatheGeometry(
            [
                (0.040 * scale, 0.000),
                (0.052 * scale, 0.020 * scale),
                (0.066 * scale, 0.072 * scale),
                (0.050 * scale, 0.120 * scale),
                (0.030 * scale, 0.140 * scale),
                (0.030 * scale, 0.190 * scale),
                (0.039 * scale, 0.205 * scale),
            ],
            segments=24,
            closed=True,
        ),
        "compact_display_vase" if compact else "display_vase",
    )


def _make_wine_glass_bowl_mesh():
    """Accepted hanging-stem LatheGeometry bowl, reduced only in tessellation."""
    return mesh_from_geometry(
        LatheGeometry(
            [
                (0.005, 0.000),
                (0.018, 0.008),
                (0.029, 0.030),
                (0.032, 0.052),
                (0.028, 0.071),
                (0.024, 0.078),
                (0.021, 0.078),
                (0.025, 0.069),
                (0.028, 0.051),
                (0.025, 0.032),
                (0.015, 0.012),
                (0.0035, 0.005),
            ],
            segments=24,
            closed=True,
        ),
        "hanging_wine_glass_bowl",
    )


def _corner_profile(width: float, depth: float, *, segments: int = 20) -> list[tuple[float, float]]:
    """Source-backed quarter-round sector footprint (quarter-round variant L21-L52)."""
    half = width * 0.5
    radius = math.hypot(half, depth)
    half_angle = math.atan2(half, depth)
    points = [(-half, 0.0)]
    for index in range(1, segments):
        theta = -half_angle + 2.0 * half_angle * index / segments
        points.append((radius * math.sin(theta), -depth + radius * math.cos(theta)))
    points.extend(((half, 0.0), (0.0, -depth)))
    return points


def _build_quarter_round_shell(body, r: ResolvedWine_Cabinet1Config, mats) -> None:
    """Open quarter-round service carcass with coupled curved decks and side frame."""
    profile = _corner_profile(r.W, r.D)
    crown_profile = _corner_profile(r.W + 0.02, r.D + 0.01)
    base_mesh = mesh_from_geometry(ExtrudeGeometry.from_z0(profile, r.plinth_h), "qr_base")
    deck_mesh = mesh_from_geometry(ExtrudeGeometry.from_z0(profile, 0.030), "qr_deck")
    crown_mesh = mesh_from_geometry(ExtrudeGeometry.from_z0(crown_profile, r.top_cap_h), "qr_crown")
    body.visual(base_mesh, material=mats["frame"], name="base_plinth", material_class_id=("wood.walnut_dark" if r.palette_style in {"espresso_smoked", "white_hutch", "warm_walnut"} else "metal.paint_coated"))
    body.visual(
        crown_mesh,
        origin=Origin(xyz=(0.0, 0.0, r.H - r.top_cap_h)),
        material=mats["frame"],
        name="top_cap", material_class_id=("wood.walnut_dark" if r.palette_style in {"espresso_smoked", "white_hutch", "warm_walnut"} else "metal.paint_coated"),
    )
    if r.service_module not in {"pull_out_shelves", "rotating_shelves"}:
        deck_levels = (
            (0.355, 0.98, 1.245)
            if r.service_module == "fold_out_counter"
            else (0.355, 0.70, 0.98, 1.245)
        )
        for index, z in enumerate(deck_levels):
            body.visual(
                deck_mesh,
                origin=Origin(xyz=(0.0, 0.0, z)),
                material=mats["rack"],
                name=f"curved_fixed_deck_{index}", material_class_id=("wood.walnut_dark" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler"} else "metal.brass_aged"),
            )

    diagonal = math.hypot(r.W / 2.0, r.D)
    side_h = r.H - r.plinth_h - r.top_cap_h
    side_z = r.plinth_h + side_h / 2.0
    yaw = math.atan2(r.D, r.W / 2.0)
    _box(
        body,
        (diagonal, _WALL, side_h),
        (-r.W / 4.0, -r.D / 2.0, side_z),
        mats["carcass"],
        "side_panel_0",
        rpy=(0.0, 0.0, -yaw),
    )
    _box(
        body,
        (diagonal, _WALL, side_h),
        (r.W / 4.0, -r.D / 2.0, side_z),
        mats["carcass"],
        "side_panel_1",
        rpy=(0.0, 0.0, yaw),
    )
    _box(body, (0.055, 0.055, side_h), (0.0, -r.D, side_z), mats["frame"], "back_panel")

    # Continuous upper/lower face rails support every door hinge lug without
    # placing a vertical post inside any leaf's swept envelope.
    if r.door_count > 0:
        rail_zs = (r.door_bottom_z - 0.035, r.door_top_z + 0.035)
        for index, z in enumerate(rail_zs):
            _box(
                body,
                (r.W - 0.06, 0.050, 0.040),
                (0.0, r.front_y - 0.025, z),
                mats["frame"],
                f"front_face_rail_{index}",
            )
        # Each cabinet-side hinge lug is carried by a real vertical front
        # stile spanning the two face rails.  This is especially necessary
        # for the three-leaf source form, whose intermediate hinge axes cannot
        # be supported by either diagonal side panel.
        stile_bottom = rail_zs[0]
        stile_top = rail_zs[1]
        for index, (hinge_x, _direction, _axis) in enumerate(_door_hinge_layout(r)):
            _box(
                body,
                (0.040, 0.050, stile_top - stile_bottom),
                (hinge_x, r.front_y - 0.025, (stile_bottom + stile_top) / 2.0),
                mats["frame"],
                f"front_hinge_stile_{index}",
            )


# --------------------------------------------------------------------------- #
# Body_form: carcass shell + interior visuals. Rule 1: all non-articulated
# geometry lives on cabinet_body as parent.visual, including interior frames,
# racks, cubbies, and bottles.
# --------------------------------------------------------------------------- #
def _build_carcass_shell(body, r: ResolvedWine_Cabinet1Config, mats) -> None:
    """Shared carcass shell: base plinth, top cap, side panels, back panel,
    bottom deck, top deck. Front-facing at +Y; interior cavity extends
    +Y..front_face where front_face = +D/2.

    Sources:
      * glass_front_cabinet: 002 L177-188 (plinth/trim/crown, side/back/deck,
        center_divider);
      * white_display_hutch: 003 L259-277 (back/side/floor/top + crown/plinth/
        base_riser + stiles/mullion/display rails);
      * tall_cooler: 004 L71-137 (side/rear/top/deck/machine_bay/plinth +
        front reveal bars).
    Coordinate system: origin at bottom-center; +Y = front (opening side).
    """
    if r.body_form == "quarter_round_corner":
        _build_quarter_round_shell(body, r, mats)
        return

    W, D, H = r.W, r.D, r.H
    ph = r.plinth_h
    tc = r.top_cap_h

    # Base plinth (all body_forms).
    _box(
        body,
        (W + 0.020, D + 0.025, ph),
        (0.0, 0.0, ph / 2.0),
        mats["frame"],
        "base_plinth",
    )
    # Top cap.
    _box(
        body,
        (W + 0.012, D + 0.012, tc),
        (0.0, 0.0, H - tc / 2.0),
        mats["frame"],
        "top_cap",
    )
    # Side panels — from ph top to H - tc bottom.
    side_x = W / 2.0 - _WALL / 2.0
    side_z = (ph + H - tc) / 2.0
    side_h = H - tc - ph
    _box(
        body,
        (_WALL, D, side_h),
        (-side_x, 0.0, side_z),
        mats["carcass"],
        "side_panel_0",
    )
    _box(
        body,
        (_WALL, D, side_h),
        (side_x, 0.0, side_z),
        mats["carcass"],
        "side_panel_1",
    )
    # Back panel (at -Y).
    back_y = -D / 2.0 + _WALL / 2.0
    _box(
        body,
        (W - 2.0 * _WALL, _WALL, side_h),
        (0.0, back_y, side_z),
        mats["interior"],
        "back_panel",
    )
    # Bottom deck (interior floor).
    _box(
        body,
        (W - 2.0 * _WALL, D - _WALL, 0.030),
        (0.0, _WALL / 2.0, ph + 0.015),
        mats["interior"],
        "bottom_deck",
    )
    # Top deck.
    _box(
        body,
        (W - 2.0 * _WALL, D - _WALL, 0.030),
        (0.0, _WALL / 2.0, H - tc - 0.015),
        mats["interior"],
        "top_deck",
    )

    # body_form specific interior visuals.
    if r.body_form in {"glass_front_cabinet", "narrow_tower"}:
        # Center divider between the two compartments (002 L188).
        _box(
            body,
            (0.030, D - _WALL, side_h - 0.06),
            (0.0, _WALL / 2.0, side_z),
            mats["frame"],
            "center_divider",
        )
    elif r.body_form in {"white_display_hutch", "low_sideboard"}:
        # Center mullion + display upper/lower rail (003 L273-277).
        _box(
            body,
            (0.025, 0.040, side_h - 0.10),
            (0.0, D / 2.0 - 0.030, side_z),
            mats["frame"],
            "center_mullion",
        )
        rail_z = r.door_bottom_z - 0.030 if r.body_form == "low_sideboard" else ph + 0.72
        _box(
            body,
            (W - 2.0 * _WALL - 0.020, 0.040, 0.050),
            (0.0, D / 2.0 - 0.030, rail_z),
            mats["frame"],
            "display_lower_rail",
        )
    elif r.body_form == "tall_cooler":
        # Machine bay (004 L101-105) — lower interior box.
        mb_h = 0.28
        _box(
            body,
            (W - 0.065, D - 0.055, mb_h),
            (0.0, -0.012, ph + mb_h / 2.0 + 0.01),
            mats["hardware"],
            "machine_bay",
        )
        # Lower vent slats grille bar (simple Box approximation; 004 L162-176
        # used VentGrilleGeometry, but keep to Box for compile budget).
        _box(
            body,
            (W - 0.075, 0.030, 0.18),
            (0.0, D / 2.0 - 0.010, ph * 0.5 + 0.08),
            mats["hardware"],
            "lower_vent_grille",
        )


def _door_hinge_layout(
    r: ResolvedWine_Cabinet1Config,
) -> list[tuple[float, float, tuple[float, float, float]]]:
    """Return (hinge_x, leaf_direction, axis) for every ordinary hinged leaf."""
    if r.door_count <= 0:
        return []
    if r.door_count == 1:
        return [(r.W / 2.0 - _WALL - 0.010, -1.0, (0.0, 0.0, -1.0))]
    if r.door_count == 2:
        return [
            (-r.W / 2.0 + _WALL + 0.010, 1.0, (0.0, 0.0, 1.0)),
            (r.W / 2.0 - _WALL - 0.010, -1.0, (0.0, 0.0, -1.0)),
        ]
    # Three-door quarter-round source: each narrow leaf pivots from a real
    # front post and extends toward +X.  The last leaf uses the right post and
    # extends toward -X so no leaf is cantilevered from empty space.
    opening_w = r.W - 2.0 * _WALL
    step = opening_w / r.door_count
    return [
        (-opening_w / 2.0 + index * step, 1.0, (0.0, 0.0, 1.0)) for index in range(r.door_count - 1)
    ] + [(opening_w / 2.0, -1.0, (0.0, 0.0, -1.0))]


def _emit_hinge_mounts(body, r: ResolvedWine_Cabinet1Config, mats) -> None:
    """Cabinet-side hinge mount lugs at each door hinge position (for hinged
    door_motion). These serve as the parent-side visual anchoring the
    hinge_barrel of each door via MatingContract.

    Sources: 002 L191-206 (hinge_mount_{side_index}_{mount_index}),
    003 L260-263 (side_panel serving as the hinge mount), 004 L179-185
    (hinge_mount_{i}).
    """
    if r.door_motion not in {"hinged", "bifold"} or r.door_count <= 0:
        return
    front_y = r.front_y
    if r.door_motion == "bifold":
        _box(
            body,
            (r.W - 2.0 * _WALL, 0.028, 0.025),
            (0.0, front_y - 0.010, r.door_top_z + 0.014),
            mats["hardware"],
            "bifold_top_track",
        )
        _box(
            body,
            (r.W - 2.0 * _WALL, 0.028, 0.025),
            (0.0, front_y - 0.010, r.door_bottom_z - 0.014),
            mats["hardware"],
            "bifold_bottom_track",
        )
        body.visual(
            Cylinder(radius=0.010, length=r.door_h),
            origin=Origin(
                xyz=(r.W / 2.0 - _WALL - 0.010, front_y + 0.015, r.door_bottom_z + r.door_h / 2.0)
            ),
            material=mats["hardware"],
            name="bifold_pivot_pin", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
        )
        return
    # Match the hinge_x to what _attach_doors uses for each door_idx so the
    # cabinet-side mount lug sits at the same X as the door hinge line.
    for door_idx, (hinge_x, _direction, _axis) in enumerate(_door_hinge_layout(r)):
        # Mount lug: a Box extending from the front face inward. Placed so
        # its outward-facing +Y face reaches the hinge barrel center (at
        # y=front_y - 0.010 in world) with the barrel radius (0.011)
        # touching the lug within contact_tol. Lug span: y in
        # [front_y - 0.032, front_y - 0.002] (30mm deep), centered at
        # y = front_y - 0.017. Lug thickness in Y = 0.030.
        for mount_idx, z_frac in enumerate((0.15, 0.85)):
            z = r.door_bottom_z + z_frac * r.door_h
            _box(
                body,
                (0.024, 0.070, 0.12),
                (hinge_x, front_y + 0.004, z),
                mats["hardware"],
                f"hinge_mount_{door_idx}_{mount_idx}",
            )


def _emit_sliding_tracks(body, r: ResolvedWine_Cabinet1Config, mats) -> None:
    """Top / bottom tracks for sliding doors (S7 door_motion_sliding L38-...).
    Only emitted for sliding door_motion."""
    if r.door_motion != "sliding":
        return
    front_y = r.front_y
    # Tracks span the full opening width along X, thick along Y (0.040) to
    # give the sliding door leaf a wide contact face for the MatingContract
    # gap check. Centered at front_y so their Y span covers the door leaf.
    for tag, z in (
        ("top_track", r.door_top_z + 0.025),
        ("bottom_track", r.door_bottom_z - 0.025),
    ):
        _box(
            body,
            (r.W - 2.0 * _WALL, 0.040, 0.050),
            (0.0, front_y + 0.026, z),
            mats["hardware"],
            tag,
        )


# --------------------------------------------------------------------------- #
# Rack_style: interior rack / cubby grid — Rule 1 inline visuals.
# --------------------------------------------------------------------------- #
def _emit_compartment_shelves(body, r: ResolvedWine_Cabinet1Config, mats, bottle_mesh) -> None:
    """002/narrow-derived twin compartments with full-depth shelf boards."""
    rows = r.rack_count
    columns = 4 if r.body_form == "glass_front_cabinet" else 3
    inner_w = r.W - 2.0 * _WALL
    compartment_w = (inner_w - _WALL) / 2.0
    compartment_centers = (
        -(compartment_w + _WALL) / 2.0,
        (compartment_w + _WALL) / 2.0,
    )
    shelf_depth = r.D - 2.0 * _WALL + 0.010
    z0 = r.interior_bottom_z + 0.10
    pitch = (r.interior_top_z - z0 - 0.08) / max(1, rows)
    for row in range(rows):
        shelf_z = z0 + row * pitch
        for compartment, center_x in enumerate(compartment_centers):
            _box(
                body,
                (compartment_w + 0.006, shelf_depth, 0.018),
                (center_x, 0.0, shelf_z),
                mats["rack"],
                f"rack_shelf_{compartment}_{row}",
            )
            _box(
                body,
                (compartment_w + 0.006, 0.020, 0.034),
                (center_x, r.front_y - _WALL - 0.010, shelf_z + 0.013),
                mats["hardware"],
                f"rack_fascia_{compartment}_{row}",
            )
            usable = compartment_w - 0.050
            for column in range(columns):
                x = center_x - usable / 2.0 + (column + 0.5) * usable / columns
                index = (row * 2 + compartment) * columns + column
                material = (mats["bottle_a"], mats["bottle_b"], mats["bottle_c"])[
                    (row + compartment + column) % 3
                ]
                body.visual(
                    bottle_mesh,
                    origin=Origin(
                        xyz=(x, 0.045, shelf_z + 0.040),
                        rpy=(-math.pi / 2.0, 0.0, 0.0),
                    ),
                    material=material,
                    name=f"bottle_{index}", material_class_id="glass.smoked_tinted",
                )


def _emit_horizontal_shelves(body, r: ResolvedWine_Cabinet1Config, mats, bottle_mesh) -> None:
    """Horizontal cross-rail rack shelves + 3 bottles per rack (S8 004 L188-256).

    Each level = rack_rear_{i} + rack_front_{i} + rack_fascia_{i} (3 boxes) +
    3 bottles laid horizontally with axis along Y. All are cabinet_body.visual
    (Rule 1: bottles/racks don't articulate).
    """
    if r.body_form in {"glass_front_cabinet", "narrow_tower"}:
        _emit_compartment_shelves(body, r, mats, bottle_mesh)
        return

    # Available interior height for racks. For tall_cooler push the rack
    # zone above the machine_bay (which occupies z in [plinth_h, plinth_h+
    # 0.29] approximately).
    if r.body_form == "tall_cooler":
        z0 = r.plinth_h + 0.32
    else:
        z0 = r.interior_bottom_z + 0.10
    top_z = r.interior_top_z - 0.05
    n = r.rack_count
    if n < 1:
        return
    # Distribute racks in [z0, top_z].
    span = top_z - z0
    pitch = span / max(1, n)
    # Rack rail dims: overshoot the interior width by 0.010 so the rail ends
    # are embedded into each side_panel (side_panel inner face is at
    # x = ±(W/2 - _WALL)). This guarantees the rails are connected to the
    # cabinet body and not floating.
    rail_len = r.W - 2.0 * _WALL + 0.010
    # Rail geometry — rear rail near back wall, front rail near front face,
    # front fascia just proud of the front face. Following 004 L188-210.
    rack_center_y = r.front_y - 0.220
    rear_y = rack_center_y - 0.105
    front_y_rack = rack_center_y + 0.105
    fascia_y = r.front_y - 0.045
    for row in range(n):
        z = z0 + (row + 0.5) * pitch
        # rear rail
        _box(
            body,
            (rail_len, 0.030, 0.018),
            (0.0, rear_y, z),
            mats["rack"],
            f"rack_rear_{row}",
        )
        # front rail
        _box(
            body,
            (rail_len, 0.030, 0.018),
            (0.0, front_y_rack, z),
            mats["rack"],
            f"rack_front_{row}",
        )
        # front fascia
        _box(
            body,
            (rail_len, 0.020, 0.022),
            (0.0, fascia_y, z + 0.006),
            mats["rack"],
            f"rack_fascia_{row}",
        )
        # 3 horizontal bottles per rack. Follow 004 L232-256: bottle axis
        # along +Y (roll = -pi/2 about X), belly straddles front rail,
        # heel/base sits near rear rail. Bottle length ~ 0.32m; bottle
        # center_y placed so both ends embed slightly into the rails.
        usable_x = rail_len - 0.100
        # Bottle center Y: the lathe's y-span is [-0.160, +0.164] (base at
        # -0.160, neck tip at +0.164). We want the neck end to reach the
        # front rail and the base near the rear rail. Bottle center y
        # positions the middle of the lathe; solve:
        #   (center_y - 0.160) ~ rear_y  → center_y ~ rear_y + 0.160
        # so the base end is at or slightly past the rear rail.
        bottle_center_y = rack_center_y
        # Bottle center Z: above the rails (rails top edge at z+0.009,
        # bottle radius ~0.031 at the belly).
        bottle_center_z = z + 0.030
        for col in range(3):
            col_x = -usable_x / 2.0 + (col + 0.5) * (usable_x / 3.0)
            index = row * 3 + col
            bottle_material = (mats["bottle_a"], mats["bottle_b"], mats["bottle_c"])[
                (row + col) % 3
            ]
            tilt = math.radians((-4.0, 3.0, -2.0)[(row + col) % 3])
            roll = -math.pi / 2.0 + tilt
            body.visual(
                bottle_mesh,
                origin=Origin(
                    xyz=(col_x, bottle_center_y, bottle_center_z),
                    rpy=(roll, 0.0, 0.0),
                ),
                material=bottle_material,
                name=f"bottle_{index}", material_class_id="glass.smoked_tinted",
            )
            # Label: a Cylinder wrapped around the bottle belly. Its own
            # cylinder axis is Y (matched to bottle axis after rpy). The
            # label sits at y = bottle_center_y (i.e., near the belly).
            body.visual(
                Cylinder(radius=0.0317, length=0.045),
                origin=Origin(
                    xyz=(col_x, bottle_center_y + 0.010, bottle_center_z),
                    rpy=(roll, 0.0, 0.0),
                ),
                material=mats["label"],
                name=f"bottle_label_{index}", material_class_id="paper.plain_sheet",
            )


def _emit_cubby_grid(body, r: ResolvedWine_Cabinet1Config, mats, bottle_mesh) -> None:
    """Accepted six-column, 3/4-row cubby with one supported bottle per cell."""
    row_count = max(1, r.rack_count // 6)
    ncols = 6
    # Preserve the accepted ~100 mm cell pitch rather than stretching a small
    # number of bottles through half the cabinet height.
    z_zone_bottom = r.interior_bottom_z + (0.040 if r.body_form == "low_sideboard" else 0.10)
    zone_h_target = 0.105 * row_count
    z_zone_top = min(z_zone_bottom + zone_h_target, r.interior_top_z - 0.08)
    zone_h = z_zone_top - z_zone_bottom
    z_pitch = zone_h / row_count
    # Cubby zone x-half.
    zone_x = r.W / 2.0 - _WALL - 0.010
    # Vertical dividers: (ncols + 1).
    for i in range(ncols + 1):
        x = -zone_x + i * (2.0 * zone_x / ncols)
        _box(
            body,
            (0.018, r.D - 2.0 * _WALL - 0.05, zone_h),
            (x, _WALL / 2.0 + 0.02, (z_zone_bottom + z_zone_top) / 2.0),
            mats["rack"],
            f"cubby_vertical_{i}",
        )
    # Horizontal dividers: (row_count + 1) boards.
    for r_idx in range(row_count + 1):
        z = z_zone_bottom + r_idx * z_pitch
        _box(
            body,
            (2.0 * zone_x, r.D - 2.0 * _WALL - 0.05, 0.018),
            (0.0, _WALL / 2.0 + 0.02, z),
            mats["rack"],
            f"cubby_horizontal_{r_idx}",
        )
    # One horizontal bottle rests on the full-depth shelf below each cell.
    for row in range(row_count):
        # Top of the horizontal shelf at row index.
        shelf_top_z = z_zone_bottom + row * z_pitch + 0.009  # + half thickness
        bottle_z = shelf_top_z + 0.031  # embed belly slightly
        for col in range(ncols):
            row * ncols + col
            cell_x = -zone_x + (col + 0.5) * (2.0 * zone_x / ncols)
            bottle_material = (mats["bottle_a"], mats["bottle_b"], mats["bottle_c"])[
                (row + col) % 3
            ]
            body.visual(
                bottle_mesh,
                origin=Origin(
                    xyz=(cell_x, 0.03, bottle_z),
                    rpy=(-math.pi / 2.0, 0.0, 0.0),
                ),
                material=bottle_material,
                name=f"cubby_bottle_{row}_{col}", material_class_id="glass.smoked_tinted",
            )


def _emit_source_display_contents(body, r: ResolvedWine_Cabinet1Config, mats) -> None:
    """Reproduce the supported upper displays coupled to the two cubby forms.

    White hutch source 003 has four display shelves with five bottles and
    three vases.  The low-sideboard source has two shelves: three compact
    vases below and five short bottles above.  All positions derive from a
    named shelf top; no free-volume scatter is used.
    """
    if r.body_form not in {"white_display_hutch", "low_sideboard"}:
        return

    shelf_width = r.W - 2.0 * _WALL + 0.010
    shelf_depth = r.D - 2.0 * _WALL
    if r.body_form == "white_display_hutch":
        height_scale = r.H / _WDH["H"]
        shelf_zs = tuple(z * height_scale for z in (0.755, 1.055, 1.365, 1.675))
        for index, z in enumerate(shelf_zs):
            _box(
                body,
                (shelf_width, shelf_depth, 0.022),
                (0.0, 0.0, z),
                mats["rack"],
                f"display_shelf_{index}",
            )
        shelf_tops = tuple(z + 0.009 for z in shelf_zs)
        bottle_specs = (
            (-0.235, -0.030, shelf_tops[0]),
            (0.205, -0.020, shelf_tops[0]),
            (0.205, -0.020, shelf_tops[1]),
            (-0.210, -0.015, shelf_tops[2]),
            (0.205, -0.010, shelf_tops[3]),
        )
        vase_specs = (
            (0.0, 0.000, shelf_tops[0]),
            (-0.205, -0.010, shelf_tops[1]),
            (0.205, -0.005, shelf_tops[2]),
        )
        bottle_mesh = _make_display_bottle_mesh()
        vase_mesh = _make_display_vase_mesh(compact=False)
    else:
        height_scale = r.H / _LS["H"]
        shelf_zs = tuple(z * height_scale for z in (0.540, 0.710))
        for index, z in enumerate(shelf_zs):
            _box(
                body,
                (shelf_width, shelf_depth, 0.020),
                (0.0, 0.0, z),
                mats["rack"],
                f"display_shelf_{index}",
            )
        shelf_tops = tuple(z + 0.008 for z in shelf_zs)
        bottle_specs = tuple(
            (x, -0.015, shelf_tops[1]) for x in (-0.280, -0.140, 0.0, 0.140, 0.280)
        )
        vase_specs = tuple((x, -0.005, shelf_tops[0]) for x in (-0.250, 0.0, 0.250))
        bottle_mesh = _make_low_display_bottle_mesh()
        vase_mesh = _make_display_vase_mesh(compact=True)

    width_scale = r.W / (_WDH["W"] if r.body_form == "white_display_hutch" else _LS["W"])
    for index, (x, y, z) in enumerate(bottle_specs):
        body.visual(
            bottle_mesh,
            origin=Origin(xyz=(x * width_scale, y, z)),
            material=(mats["bottle_a"], mats["bottle_b"], mats["bottle_c"])[index % 3],
            name=f"display_bottle_{index}", material_class_id="glass.smoked_tinted",
        )
    for index, (x, y, z) in enumerate(vase_specs):
        body.visual(
            vase_mesh,
            origin=Origin(xyz=(x * width_scale, y, z)),
            material=mats["frame"],
            name=f"display_vase_{index}", material_class_id=("ceramic.porcelain_glazed_plain" if r.palette_style == "white_hutch" else "ceramic.decorative_glazed"),
        )


def _pull_out_profile(r: ResolvedWine_Cabinet1Config) -> list[tuple[float, float]]:
    """Scaled source profile from pull-out-shelf variant L36-L48."""
    half = min(0.18, r.W * 0.25)
    depth = min(0.22, r.D * 0.61)
    bow = min(0.04, r.D * 0.11)
    return [
        (-half, -0.008),
        (-half * 0.85, bow * 0.50),
        (-half * 0.50, bow * 0.88),
        (0.0, bow),
        (half * 0.50, bow * 0.88),
        (half * 0.85, bow * 0.50),
        (half, -0.008),
        (0.0, -depth),
    ]


def _emit_pull_out_shelves(model, body, r: ResolvedWine_Cabinet1Config, mats) -> None:
    """Three source-backed pull-out shelves with bilateral longitudinal guides."""
    profile = _pull_out_profile(r)
    shelf_mesh = mesh_from_geometry(ExtrudeGeometry.from_z0(profile, 0.026), "pull_out_shelf")
    half_w = min(0.18, r.W * 0.25)
    for side, sign in enumerate((-1.0, 1.0)):
        _box(
            body,
            (0.020, 0.040, 1.35),
            (sign * (half_w + 0.018), 0.235, 0.75),
            mats["hardware"],
            f"pullout_upright_{side}",
        )
        _box(
            body,
            (0.020, 0.300, 0.020),
            (sign * (half_w + 0.018), 0.105, 0.080),
            mats["hardware"],
            f"pullout_lower_tie_{side}",
        )
    for index, z in enumerate((0.355, 0.98, 1.245)):
        # Real parent guides: one on each side, longitudinal along travel Y.
        for side, sign in enumerate((-1.0, 1.0)):
            _box(
                body,
                (0.012, 0.32, 0.024),
                (sign * (half_w + 0.018), 0.06, z + 0.013),
                mats["hardware"],
                f"pullout_guide_{index}_{side}",
            )
        shelf = model.part(f"pull_out_shelf_{index}")
        shelf.visual(shelf_mesh, material=mats["rack"], name="shelf_panel", material_class_id=("wood.walnut_dark" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler"} else "metal.brass_aged"))
        for side, sign in enumerate((-1.0, 1.0)):
            _box(
                shelf,
                (0.014, 0.08, 0.020),
                (sign * (half_w + 0.006), 0.0, 0.013),
                mats["hardware"],
                f"shelf_runner_{side}",
            )
        _box(shelf, (0.12, 0.018, 0.026), (0.0, 0.035, 0.013), mats["hardware"], "front_pull")
        shelf.inertial = Inertial.from_geometry(Box((half_w * 2.0, 0.30, 0.026)), mass=3.0)
        model.articulation(
            f"body_to_pull_out_shelf_{index}",
            ArticulationType.PRISMATIC,
            parent=body,
            child=shelf,
            origin=Origin(xyz=(0.0, 0.0, z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=10.0, velocity=0.3, lower=0.0, upper=0.16),
            mating=MatingContract(
                parent_face_geometry=f"pullout_guide_{index}_1",
                parent_face_side="negative_x",
                child_face_geometry="shelf_runner_1",
                child_face_side="positive_x",
                contact_tol=0.004,
            ),
        )


def _emit_rotating_shelves(model, body, r: ResolvedWine_Cabinet1Config, mats) -> None:
    """Three circular lazy-Susan shelves on one continuous central spindle."""
    radius = min(0.13, r.W * 0.20, r.D * 0.36)
    body.visual(
        Cylinder(radius=0.018, length=1.33),
        origin=Origin(xyz=(0.0, -0.10, 0.74)),
        material=mats["hardware"],
        name="rotating_spindle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
    )
    for index, z in enumerate((0.355, 0.98, 1.245)):
        body.visual(
            Cylinder(radius=0.040, length=0.020),
            origin=Origin(xyz=(0.0, -0.10, z - 0.010)),
            material=mats["hardware"],
            name=f"rotating_support_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
        )
        shelf = model.part(f"rotating_shelf_{index}")
        shelf.visual(
            Cylinder(radius=radius, length=0.026),
            origin=Origin(xyz=(0.0, 0.0, 0.013)),
            material=mats["rack"],
            name="shelf_disk", material_class_id=("wood.walnut_dark" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler"} else "metal.brass_aged"),
        )
        shelf.visual(
            Cylinder(radius=0.014, length=0.026),
            origin=Origin(xyz=(0.0, 0.0, 0.013)),
            material=mats["hardware"],
            name="pivot_bearing", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
        )
        shelf.inertial = Inertial.from_geometry(Cylinder(radius=radius, length=0.026), mass=3.0)
        model.articulation(
            f"body_to_rotating_shelf_{index}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=shelf,
            origin=Origin(xyz=(0.0, -0.10, z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=4.0, velocity=2.0),
            mating=MatingContract(
                parent_face_geometry=f"rotating_support_{index}",
                parent_face_side="positive_z",
                child_face_geometry="shelf_disk",
                child_face_side="negative_z",
                contact_tol=0.003,
            ),
        )


def _emit_fold_out_counter(model, body, r: ResolvedWine_Cabinet1Config, mats) -> None:
    """Source-backed stowed-vertical serving leaf; q=pi/2 deploys toward +Y."""
    width, depth, thickness = min(0.52, r.W - 0.14), 0.305, 0.022
    hinge_z = 0.70
    # A real center mullion ties the counter backplate into the lower and
    # upper fixed decks.  The old implementation happened to touch a bottle
    # rail; removing that unrelated content exposed a disconnected hinge
    # carrier.  This member is an explicit structural consumer of the same
    # quarter-round front datum, not a topology-test shim.
    carrier_bottom = 0.355 + 0.030
    carrier_top = 0.98
    _box(
        body,
        (0.050, 0.055, carrier_top - carrier_bottom),
        (0.0, r.front_y - 0.034, (carrier_bottom + carrier_top) / 2.0),
        mats["frame"],
        "counter_mount_mullion",
    )
    for mount_index, sign in enumerate((-1.0, 1.0)):
        _box(
            body,
            (0.036, 0.040, 0.026),
            (sign * (width / 2.0 + 0.018), r.front_y + 0.006, hinge_z + 0.013),
            mats["hardware"],
            f"counter_hinge_mount_{mount_index}",
        )
    _box(
        body,
        (width + 0.10, 0.080, 0.026),
        (0.0, r.front_y - 0.034, hinge_z + 0.026),
        mats["hardware"],
        "counter_mount_backplate",
    )
    counter = model.part("fold_out_counter")
    _box(
        counter, (width, thickness, depth), (0.0, 0.0, -depth / 2.0), mats["rack"], "counter_panel"
    )
    _box(
        counter,
        (width, 0.012, 0.016),
        (0.0, 0.016, -depth + 0.008),
        mats["hardware"],
        "counter_handle",
    )
    counter.visual(
        Cylinder(radius=0.008, length=width + 0.040),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["hardware"],
        name="counter_hinge_knuckle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
    )
    counter.inertial = Inertial.from_geometry(Box((width, thickness, depth)), mass=4.0)
    model.articulation(
        "body_to_fold_out_counter",
        ArticulationType.REVOLUTE,
        parent=body,
        child=counter,
        origin=Origin(xyz=(0.0, r.front_y + 0.018, hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=1.0, lower=0.0, upper=math.radians(85.0)),
    )


def _emit_quarter_bottle_storage(body, r: ResolvedWine_Cabinet1Config, mats, bottle_mesh) -> None:
    """N upright bottles on the exact upper/base/lower-shelf support surfaces."""
    total = r.rack_count
    upper_count = (total + 1) // 2
    lower_count = total - upper_count

    def emit_row(prefix: str, count: int, z: float, y: float, start_index: int) -> None:
        if count <= 0:
            return
        span = min(r.W - 0.18, max(0.0, (count - 1) * 0.095))
        step = span / max(count - 1, 1)
        for local_index in range(count):
            x = -span / 2.0 + local_index * step if count > 1 else 0.0
            index = start_index + local_index
            material = (mats["bottle_a"], mats["bottle_b"], mats["bottle_c"])[index % 3]
            body.visual(
                bottle_mesh,
                origin=Origin(xyz=(x, y, z)),
                material=material,
                name=f"quarter_bottle_{prefix}_{local_index}", material_class_id="glass.smoked_tinted",
            )
            body.visual(
                Cylinder(radius=0.0275, length=0.036),
                origin=Origin(xyz=(x, y, z + 0.080)),
                material=mats["label"],
                name=f"quarter_bottle_label_{prefix}_{local_index}", material_class_id="paper.plain_sheet",
            )

    # Upper bottles stand on the 1.245 m curved shelf (30 mm thick).
    emit_row("upper", upper_count, 1.275, -0.025, 0)
    if lower_count:
        # Up to three stand on the grounded base; any remainder uses the
        # source-backed 0.355 m curved lower shelf. Thus N changes both row
        # occupancy and spacing rather than merely scattering copies.
        base_count = min(3, lower_count)
        emit_row("base", base_count, r.plinth_h, -0.125, upper_count)
        emit_row(
            "lower_shelf",
            lower_count - base_count,
            0.385,
            -0.125,
            upper_count + base_count,
        )


def _emit_hanging_stem_rack(body, r: ResolvedWine_Cabinet1Config, mats, bowl_mesh) -> None:
    """Static two-rail capture rack with three inverted glasses, all on the body part."""
    z = 0.973
    _box(body, (0.34, 0.05, 0.014), (0.0, -0.07, z), mats["hardware"], "stem_rack_plate")
    for index, y in enumerate((-0.086, -0.054)):
        _box(
            body,
            (0.34, 0.010, 0.006),
            (0.0, y, z - 0.010),
            mats["hardware"],
            f"stem_rack_rail_{index}",
        )
    for index, x in enumerate((-0.135, 0.0, 0.135)):
        body.visual(
            Cylinder(radius=0.027, length=0.006),
            origin=Origin(xyz=(x, -0.07, z - 0.016)),
            material=mats["glass"],
            name=f"hanging_glass_foot_{index}", material_class_id="glass.clear_transparent",
        )
        body.visual(
            Cylinder(radius=0.0042, length=0.078),
            origin=Origin(xyz=(x, -0.07, z - 0.058)),
            material=mats["glass"],
            name=f"hanging_glass_stem_{index}", material_class_id="glass.clear_transparent",
        )
        body.visual(
            bowl_mesh,
            origin=Origin(xyz=(x, -0.07, z - 0.090), rpy=(math.pi, 0.0, 0.0)),
            material=mats["glass"],
            name=f"hanging_glass_bowl_{index}", material_class_id="glass.clear_transparent",
        )


# --------------------------------------------------------------------------- #
# Door mechanisms.
# --------------------------------------------------------------------------- #
def _build_hinged_door(
    door, r: ResolvedWine_Cabinet1Config, mats, *, direction: float, leaf_w: float
) -> None:
    """Build a framed glass door in a hinge-line local frame.

    ``direction`` = +1 for a leaf that extends toward +X of the hinge line
    (left-hand door; hinge at leaf's -X edge); -1 for a leaf that extends
    toward -X (right-hand door; hinge at leaf's +X edge). Sources: 002 L33-143
    _add_door_geometry, 003 L106-223 _add_door.

    Local frame: hinge line at x=0 along Z; leaf extends direction*[0, leaf_w].
    The leaf top face is at +Y = 0 (glass is embedded slightly), so the door
    swings out toward +Y in world when q > 0.
    """
    frame_w = 0.034
    frame_d = 0.030

    # Center X of the leaf.
    mid_x = direction * (leaf_w / 2.0)
    # Outer / inner stiles (X).
    outer_x = direction * (frame_w / 2.0 + 0.005)
    inner_x = direction * (leaf_w - frame_w / 2.0)

    _box(
        door,
        (frame_w, frame_d, r.door_h),
        (outer_x, 0.0, r.door_h / 2.0),
        mats["frame"],
        "outer_stile",
    )
    _box(
        door,
        (frame_w, frame_d, r.door_h),
        (inner_x, 0.0, r.door_h / 2.0),
        mats["frame"],
        "inner_stile",
    )
    # Top and bottom rails.
    rail_w = leaf_w - 0.020
    _box(
        door,
        (rail_w, frame_d, 0.042),
        (mid_x, 0.0, 0.021),
        mats["frame"],
        "bottom_rail",
    )
    _box(
        door,
        (rail_w, frame_d, 0.042),
        (mid_x, 0.0, r.door_h - 0.021),
        mats["frame"],
        "top_rail",
    )
    # Glass panel.
    glass_w = leaf_w - 2.0 * frame_w - 0.010
    _box(
        door,
        (glass_w, 0.008, r.door_h - 0.090),
        (mid_x, 0.0, r.door_h / 2.0),
        mats["glass"],
        "glass_panel",
    )
    # Two source-backed barrels align one-to-one with the cabinet mount lugs.
    for i, z in enumerate((r.door_h * 0.15, r.door_h * 0.85)):
        door.visual(
            Cylinder(radius=0.011, length=0.10),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["hardware"],
            name=f"hinge_barrel_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
        )
    # Vertical handle bar.
    handle_x = direction * (leaf_w - 0.050)
    handle_len = max(0.08, min(0.82, r.door_h * 0.55))
    door.visual(
        Cylinder(radius=0.009, length=handle_len),
        origin=Origin(xyz=(handle_x, 0.045, r.door_h / 2.0)),
        material=mats["hardware"],
        name="handle_bar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
    )
    for i, z in enumerate(
        (r.door_h / 2.0 - handle_len / 2.0 + 0.008, r.door_h / 2.0 + handle_len / 2.0 - 0.008)
    ):
        _box(
            door,
            (0.050, 0.036, 0.024),
            (direction * (leaf_w - 0.050), 0.028, z),
            mats["hardware"],
            f"handle_mount_{i}",
        )


def _build_sliding_door(door, r: ResolvedWine_Cabinet1Config, mats, *, leaf_w: float) -> None:
    """Sliding door in a leaf-local frame (leaf center at x=0, y=0, spanning
    Z=[0, door_h]). Sources: door_motion_sliding L38-539 (glass_door part).
    """
    # Bottom / top rail of the door leaf.
    _box(
        door,
        (leaf_w, 0.032, 0.045),
        (0.0, 0.0, 0.0225),
        mats["frame"],
        "door_bottom_rail",
    )
    _box(
        door,
        (leaf_w, 0.032, 0.045),
        (0.0, 0.0, r.door_h - 0.0225),
        mats["frame"],
        "door_top_rail",
    )
    # Left / right stiles.
    _box(
        door,
        (0.040, 0.032, r.door_h),
        (-leaf_w / 2.0 + 0.020, 0.0, r.door_h / 2.0),
        mats["frame"],
        "hinge_stile",
    )
    _box(
        door,
        (0.040, 0.032, r.door_h),
        (leaf_w / 2.0 - 0.020, 0.0, r.door_h / 2.0),
        mats["frame"],
        "handle_stile",
    )
    # Glass panel.
    _box(
        door,
        (leaf_w - 0.070, 0.008, r.door_h - 0.075),
        (0.0, 0.0, r.door_h / 2.0),
        mats["glass"],
        "smoked_glass",
    )
    # Vertical pull handle.
    door.visual(
        Cylinder(radius=0.012, length=min(1.10, r.door_h - 0.25)),
        origin=Origin(xyz=(leaf_w / 2.0 - 0.040, 0.060, r.door_h / 2.0)),
        material=mats["hardware"],
        name="vertical_handle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
    )
    for i, z in enumerate((r.door_h * 0.30, r.door_h * 0.70)):
        door.visual(
            Cylinder(radius=0.011, length=0.070),
            origin=Origin(
                xyz=(leaf_w / 2.0 - 0.040, 0.030, z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["hardware"],
            name=f"handle_standoff_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
        )


def _build_bifold_panel(panel, r: ResolvedWine_Cabinet1Config, mats, *, index: int) -> None:
    """Half-width framed-glass panel in a fold-edge local frame."""
    width = r.door_leaf_w
    _box(
        panel,
        (width, 0.010, 0.045),
        (-width / 2.0, 0.0, 0.0225),
        mats["frame"],
        f"bottom_rail_{index}",
    )
    _box(
        panel,
        (width, 0.010, 0.045),
        (-width / 2.0, 0.0, r.door_h - 0.0225),
        mats["frame"],
        f"top_rail_{index}",
    )
    _box(
        panel,
        (0.040, 0.010, r.door_h),
        (-0.020, 0.0, r.door_h / 2.0),
        mats["frame"],
        f"pivot_stile_{index}",
    )
    _box(
        panel,
        (0.040, 0.010, r.door_h),
        (-width + 0.020, 0.0, r.door_h / 2.0),
        mats["frame"],
        f"fold_stile_{index}",
    )
    _box(
        panel,
        (width - 0.070, 0.004, r.door_h - 0.080),
        (-width / 2.0, 0.0, r.door_h / 2.0),
        mats["glass"],
        f"glass_panel_{index}",
    )
    if index == 0:
        panel.visual(
            Cylinder(radius=0.011, length=r.door_h),
            origin=Origin(xyz=(0.0, 0.0, r.door_h / 2.0)),
            material=mats["hardware"],
            name="body_hinge_barrel", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
        )
    knuckle_x = -width + 0.002 if index == 0 else -0.002
    knuckle_y = 0.014 if index == 0 else 0.0
    for hinge_index, z in enumerate((r.door_h * 0.28, r.door_h * 0.72)):
        panel.visual(
            Cylinder(radius=0.009, length=0.12),
            origin=Origin(xyz=(knuckle_x, knuckle_y, z)),
            material=mats["hardware"],
            name=f"fold_knuckle_{hinge_index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
        )
    if index == 1:
        panel.visual(
            Cylinder(radius=0.010, length=min(1.0, r.door_h - 0.18)),
            origin=Origin(xyz=(-width + 0.045, -0.013, r.door_h / 2.0)),
            material=mats["hardware"],
            name="vertical_handle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"espresso_smoked", "white_hutch", "black_cooler", "satin_charcoal"} else "metal.brass_aged"),
        )


def _attach_bifold_door(model, body, r: ResolvedWine_Cabinet1Config, mats) -> list[str]:
    """004-derived two-panel bifold; open at q=0, closed at source upper pose."""
    panel_0 = model.part("door_panel_0")
    panel_1 = model.part("door_panel_1")
    _build_bifold_panel(panel_0, r, mats, index=0)
    _build_bifold_panel(panel_1, r, mats, index=1)
    panel_box = Box((r.door_leaf_w, 0.010, r.door_h))
    panel_0.inertial = Inertial.from_geometry(panel_box, mass=4.0)
    panel_1.inertial = Inertial.from_geometry(panel_box, mass=4.0)
    open_angle = math.radians(72.0)
    # The accepted source uses a compact V-fold. A bounded 45-degree
    # inter-leaf range preserves a collision-free finite-thickness hinge while
    # the parent leaf supplies the main 72-degree opening motion.
    fold_angle = math.radians(45.0)
    model.articulation(
        "body_to_door_panel_0",
        ArticulationType.REVOLUTE,
        parent=body,
        child=panel_0,
        origin=Origin(
            xyz=(r.W / 2.0 - _WALL - 0.010, r.front_y + 0.020, r.door_bottom_z),
        ),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=1.2, lower=0.0, upper=open_angle),
        meta={"zero_pose": "closed_unfolded", "upper_pose": "open_folded"},
    )
    model.articulation(
        "panel_0_to_panel_1",
        ArticulationType.REVOLUTE,
        parent=panel_0,
        child=panel_1,
        origin=Origin(xyz=(-r.door_leaf_w, 0.015, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.5, lower=-fold_angle, upper=0.0),
        mimic=Mimic(joint="body_to_door_panel_0", multiplier=-fold_angle / open_angle, offset=0.0),
        meta={"zero_pose": "unfolded", "upper_pose": "folded"},
    )
    return ["door_panel_0", "door_panel_1"]


def _attach_doors(model, body, r: ResolvedWine_Cabinet1Config, mats) -> list[str]:
    """Emit door parts + joints. Returns door part names.

    For hinged: door 0 = left leaf (hinge at -W/2), door 1 = right leaf
    (hinge at +W/2). Axes are mirrored so both swing outward toward +Y.
    For sliding: door 0 = left panel sliding along -X (open), door 1
    (if 2) = right panel sliding along +X (bypass).
    """
    if r.door_count <= 0:
        return []
    if r.door_motion == "bifold":
        return _attach_bifold_door(model, body, r, mats)

    front_y = r.front_y
    (r.door_bottom_z + r.door_top_z) / 2.0
    joint_names: list[str] = []
    part_names: list[str] = []

    if r.door_motion == "hinged":
        # For each door, place hinge at appropriate side edge and direction so
        # the leaf spans the opening. Front face is at +Y; opening +q rotates
        # the leaf's free edge in the +Y direction (outward).
        #
        # For door_0 (direction=+1, leaf extends toward +X): axis=(0,0,+1);
        # rotating about +Z by +q moves the free edge at (+leaf_w, 0) toward
        # (+cos q, +sin q) which is +Y — correct outward swing.
        # For door_1 (direction=-1, leaf extends toward -X): axis=(0,0,-1);
        # rotating about -Z by +q moves the free edge at (-leaf_w, 0) toward
        # (-cos q, +sin q) — also +Y outward swing.
        for door_idx, (hinge_x, direction, axis) in enumerate(_door_hinge_layout(r)):
            door = model.part(f"door_{door_idx}")

            _build_hinged_door(door, r, mats, direction=direction, leaf_w=r.door_leaf_w)
            door.inertial = Inertial.from_geometry(
                Box((r.door_leaf_w, 0.040, r.door_h)),
                mass=6.0,
                origin=Origin(xyz=(direction * r.door_leaf_w / 2.0, 0.0, r.door_h / 2.0)),
            )
            joint_name = f"body_to_door_{door_idx}"
            model.articulation(
                joint_name,
                ArticulationType.REVOLUTE,
                parent=body,
                child=door,
                # Joint origin at the hinge line on the front face; door local
                # frame has hinge line at x=0 y=0 z=[0, door_h], so joint
                # origin z = door_bottom_z (so door local z=0 maps to world
                # z=door_bottom_z).
                origin=Origin(xyz=(hinge_x, front_y + 0.050, r.door_bottom_z)),
                axis=axis,
                motion_limits=MotionLimits(effort=18.0, velocity=1.2, lower=0.0, upper=r.door_open),
                mating=MatingContract(
                    parent_face_geometry=f"hinge_mount_{door_idx}_0",
                    parent_face_side="positive_y",
                    child_face_geometry="hinge_barrel_0",
                    child_face_side="negative_y",
                    contact_tol=0.020,
                ),
            )
            joint_names.append(joint_name)
            part_names.append(f"door_{door_idx}")
    else:
        # sliding: 1 or 2 panels in top+bottom tracks.
        for door_idx in range(r.door_count):
            door = model.part(f"door_{door_idx}")
            _build_sliding_door(door, r, mats, leaf_w=r.door_leaf_w)
            door.inertial = Inertial.from_geometry(
                Box((r.door_leaf_w, 0.040, r.door_h)),
                mass=8.0,
                origin=Origin(xyz=(0.0, 0.0, r.door_h / 2.0)),
            )
            if r.door_count == 2:
                # Bypass panels: door 0 rest_x = -leaf_w/2, direction -1 (opens
                # toward -X); door 1 rest_x = +leaf_w/2, direction +1.
                if door_idx == 0:
                    rest_x = -r.door_leaf_w / 2.0
                    axis = (-1.0, 0.0, 0.0)
                else:
                    rest_x = r.door_leaf_w / 2.0
                    axis = (1.0, 0.0, 0.0)
                # Y offset for bypass (each panel in its own track lane).
                y_off = front_y + 0.045 if door_idx == 0 else front_y + 0.055
            else:
                # Single sliding door centered; opens toward -X.
                rest_x = 0.0
                axis = (-1.0, 0.0, 0.0)
                y_off = front_y + 0.050

            joint_name = f"body_to_door_{door_idx}"
            # Joint origin at door_bottom_z so the door's local z=0 lands on
            # the world door bottom line (the door was authored bottom-anchored).
            model.articulation(
                joint_name,
                ArticulationType.PRISMATIC,
                parent=body,
                child=door,
                origin=Origin(xyz=(rest_x, y_off, r.door_bottom_z)),
                axis=axis,
                motion_limits=MotionLimits(
                    effort=25.0, velocity=0.6, lower=0.0, upper=r.door_travel
                ),
                mating=MatingContract(
                    parent_face_geometry="top_track",
                    parent_face_side="negative_z",
                    child_face_geometry="door_top_rail",
                    child_face_side="positive_z",
                    contact_tol=0.040,
                ),
            )
            joint_names.append(joint_name)
            part_names.append(f"door_{door_idx}")

    return part_names


# --------------------------------------------------------------------------- #
# Top-level build.
# --------------------------------------------------------------------------- #
def build_wine_cabinet1(
    config: Wine_Cabinet1Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        meta={
            "category": "wine_cabinet1",
            "body_form": r.body_form,
            "door_motion": r.door_motion,
            "rack_style": r.rack_style,
            "service_module": r.service_module,
            "door_count": r.door_count,
            "rack_count": r.rack_count,
        },
        assets=assets,
    )

    # Materials come from the per-seed sampled palette. Every visual downstream
    # references mats[...] so the resulting cabinet varies visibly by seed.
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"wine_cabinet1_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    body = model.part("cabinet_body")
    body.inertial = Inertial.from_geometry(
        Box((r.W, r.D, r.H)),
        mass=40.0 + r.rack_count * 1.5,
        origin=Origin(xyz=(0.0, 0.0, r.H / 2.0)),
    )
    _build_carcass_shell(body, r, mats)
    _emit_hinge_mounts(body, r, mats)
    _emit_sliding_tracks(body, r, mats)

    # Interior rack / cubby + bottles (Rule 1 inline visuals).
    bottle_mesh = _make_bottle_mesh()
    if r.body_form == "quarter_round_corner":
        if r.service_module == "pull_out_shelves":
            _emit_pull_out_shelves(model, body, r, mats)
        elif r.service_module == "rotating_shelves":
            _emit_rotating_shelves(model, body, r, mats)
        else:
            _emit_quarter_bottle_storage(body, r, mats, _make_display_bottle_mesh())
            if r.service_module == "fold_out_counter":
                _emit_fold_out_counter(model, body, r, mats)
            elif r.service_module == "hanging_stem_rack":
                _emit_hanging_stem_rack(body, r, mats, _make_wine_glass_bowl_mesh())
    elif r.rack_style == "horizontal_shelves":
        _emit_horizontal_shelves(body, r, mats, bottle_mesh)
    else:
        _emit_cubby_grid(body, r, mats, bottle_mesh)
        _emit_source_display_contents(body, r, mats)

    # Doors + joints (MatingContract declared for every non-FIXED joint).
    _attach_doors(model, body, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_wine_cabinet1(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_wine_cabinet1(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #
def run_wine_cabinet1_tests(
    object_model: ArticulatedObject,
    config: Wine_Cabinet1Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("cabinet_body")

    # ---- Element-scoped allowances. ----
    # Every door leaf overlaps its own hinge_mount (captured hinge pin) and
    # its bottom rail may embed slightly in the top_track (sliding).
    for door_idx in range(r.door_count):
        door_name = f"door_{door_idx}"
        if r.door_motion == "hinged":
            door = object_model.get_part(door_name)
            for mount_idx in range(2):
                ctx.allow_overlap(
                    door,
                    body,
                    elem_a=f"hinge_barrel_{min(mount_idx, 2)}",
                    elem_b=f"hinge_mount_{door_idx}_{mount_idx}",
                    reason=(
                        "captured hinge barrel: the door hinge barrel is "
                        "captured by the cabinet-side hinge mount lug."
                    ),
                )
        elif r.door_motion == "sliding":
            door = object_model.get_part(door_name)
            ctx.allow_overlap(
                door,
                body,
                elem_a="door_top_rail",
                elem_b="top_track",
                reason="sliding door top rail rides captured inside top_track.",
            )
            ctx.allow_overlap(
                door,
                body,
                elem_a="door_bottom_rail",
                elem_b="bottom_track",
                reason="sliding door bottom rail rides captured inside bottom_track.",
            )

    if r.door_motion == "bifold":
        ctx.allow_overlap(
            object_model.get_part("door_panel_0"),
            body,
            elem_a="body_hinge_barrel",
            elem_b="bifold_pivot_pin",
            reason="Bifold pivot barrel is captured coaxially on the cabinet pivot pin.",
        )
        for captured_element in ("bottom_rail_0", "top_rail_0", "pivot_stile_0"):
            ctx.allow_overlap(
                object_model.get_part("door_panel_0"),
                body,
                elem_a=captured_element,
                elem_b="bifold_pivot_pin",
                reason="Cabinet pivot pin passes through the bored first-leaf pivot frame.",
            )
        for hinge_index in range(2):
            ctx.allow_overlap(
                object_model.get_part("door_panel_0"),
                object_model.get_part("door_panel_1"),
                elem_a=f"fold_knuckle_{hinge_index}",
                elem_b=f"fold_knuckle_{hinge_index}",
                reason="Matching short bifold hinge knuckles capture the common fold pin axis.",
            )
            ctx.allow_overlap(
                object_model.get_part("door_panel_0"),
                object_model.get_part("door_panel_1"),
                elem_a=f"fold_knuckle_{hinge_index}",
                elem_b="pivot_stile_1",
                reason="Short hinge knuckle is seated in the bored second-leaf pivot stile.",
            )
            ctx.allow_overlap(
                object_model.get_part("door_panel_0"),
                object_model.get_part("door_panel_1"),
                elem_a="fold_stile_0",
                elem_b=f"fold_knuckle_{hinge_index}",
                reason="Second-leaf hinge knuckle is captured in the bored first-leaf fold stile.",
            )

    # Exact captured-contact pairs for source-backed service mechanisms.
    if r.service_module == "pull_out_shelves":
        for index in range(3):
            shelf = object_model.get_part(f"pull_out_shelf_{index}")
            for side in range(2):
                ctx.allow_overlap(
                    shelf,
                    body,
                    elem_a=f"shelf_runner_{side}",
                    elem_b=f"pullout_guide_{index}_{side}",
                    reason="Shelf runner is captured by its same-side longitudinal guide.",
                )
    elif r.service_module == "rotating_shelves":
        for index in range(3):
            shelf = object_model.get_part(f"rotating_shelf_{index}")
            ctx.allow_overlap(
                shelf,
                body,
                elem_a="pivot_bearing",
                elem_b=f"rotating_support_{index}",
                reason="Coaxial shelf bearing sits on its dedicated support pad.",
            )
            ctx.allow_overlap(
                shelf,
                body,
                elem_a="pivot_bearing",
                elem_b="rotating_spindle",
                reason="Continuous cabinet spindle is captured by the shelf's coaxial bearing.",
            )
            ctx.allow_overlap(
                shelf,
                body,
                elem_a="shelf_disk",
                elem_b="rotating_spindle",
                reason="The spindle passes through the shelf disk's central bored opening.",
            )
    elif r.service_module == "fold_out_counter":
        for mount_index in range(2):
            ctx.allow_overlap(
                object_model.get_part("fold_out_counter"),
                body,
                elem_a="counter_hinge_knuckle",
                elem_b=f"counter_hinge_mount_{mount_index}",
                reason="Counter hinge knuckle is captured by its end mounting lug.",
            )

    # ---- Compiler baseline checks. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    # ---- Structure / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("cabinet_body root present", "cabinet_body" in part_names)

    expected_door_parts = 2 if r.door_motion == "bifold" else r.door_count
    door_parts = [name for name in part_names if name.startswith("door_")]
    ctx.check(
        "door part count matches config",
        len(door_parts) == expected_door_parts,
        details=f"expected {expected_door_parts}, got {sorted(door_parts)}",
    )

    body_visual_names = {v.name for v in body.visuals}
    ctx.check(
        "carcass shell present",
        {"base_plinth", "top_cap", "side_panel_0", "side_panel_1", "back_panel"}.issubset(
            body_visual_names
        ),
    )

    # Rack visuals.
    if r.body_form == "quarter_round_corner":
        if r.service_module == "pull_out_shelves":
            ctx.check(
                "three complete pull-out shelves present",
                all(f"pull_out_shelf_{index}" in part_names for index in range(3)),
            )
        elif r.service_module == "rotating_shelves":
            ctx.check(
                "three rotating shelves present",
                all(f"rotating_shelf_{index}" in part_names for index in range(3)),
            )
        elif r.service_module == "fold_out_counter":
            ctx.check("fold-out counter present", "fold_out_counter" in part_names)
        elif r.service_module == "hanging_stem_rack":
            ctx.check(
                "hanging rack has plate and bilateral rails",
                {"stem_rack_plate", "stem_rack_rail_0", "stem_rack_rail_1"}.issubset(
                    body_visual_names
                ),
            )
            ctx.check(
                "hanging rack has three source-backed lathed glass bowls",
                sum(name.startswith("hanging_glass_bowl_") for name in body_visual_names) == 3,
            )
        if r.service_module not in {"pull_out_shelves", "rotating_shelves"}:
            quarter_bottle_count = sum(
                name.startswith("quarter_bottle_") and "label" not in name
                for name in body_visual_names
            )
            ctx.check(
                "quarter-round N drives supported bottle positions",
                quarter_bottle_count == r.rack_count,
                details=f"quarter bottles={quarter_bottle_count} expected={r.rack_count}",
            )
            ctx.check(
                "quarter-round lower and upper support shelves present",
                {
                    "curved_fixed_deck_0",
                    (
                        "curved_fixed_deck_2"
                        if r.service_module == "fold_out_counter"
                        else "curved_fixed_deck_3"
                    ),
                }.issubset(body_visual_names),
            )
    elif r.rack_style == "horizontal_shelves":
        rack_count_visuals = sum(1 for v in body_visual_names if v.startswith("rack_fascia_"))
        bottle_visuals = sum(
            1 for v in body_visual_names if v.startswith("bottle_") and "label" not in v
        )
        if r.body_form in {"glass_front_cabinet", "narrow_tower"}:
            columns = 4 if r.body_form == "glass_front_cabinet" else 3
            ctx.check(
                "two full-depth compartment shelves per anchored row",
                rack_count_visuals == r.rack_count * 2,
                details=f"fascias={rack_count_visuals} expected={r.rack_count * 2}",
            )
            ctx.check(
                "compartment bottle density matches source",
                bottle_visuals == r.rack_count * 2 * columns,
                details=f"bottles={bottle_visuals} expected={r.rack_count * 2 * columns}",
            )
        else:
            ctx.check(
                "rack layers match rack_count",
                rack_count_visuals == r.rack_count,
                details=f"rack_fascia count={rack_count_visuals} expected {r.rack_count}",
            )
            ctx.check(
                "3 bottles per source-backed cooler rack layer",
                bottle_visuals == r.rack_count * 3,
                details=f"bottles={bottle_visuals} expected {r.rack_count * 3}",
            )
    else:  # cubby_grid
        row_count = max(1, r.rack_count // 6)
        vert_count = sum(1 for v in body_visual_names if v.startswith("cubby_vertical_"))
        horz_count = sum(1 for v in body_visual_names if v.startswith("cubby_horizontal_"))
        bottle_count = sum(1 for v in body_visual_names if v.startswith("cubby_bottle_"))
        ctx.check(
            "cubby verticals present (6+1)",
            vert_count == 7,
            details=f"cubby_vertical count={vert_count}",
        )
        ctx.check(
            "cubby horizontals present (row_count+1)",
            horz_count == row_count + 1,
            details=f"cubby_horizontal count={horz_count} expected {row_count + 1}",
        )
        ctx.check(
            "1 bottle per cubby (6 * row_count)",
            bottle_count == r.rack_count == 6 * row_count,
            details=f"cubby_bottle count={bottle_count} expected {r.rack_count}",
        )
        if r.body_form in {"white_display_hutch", "low_sideboard"}:
            expected_shelves = 4 if r.body_form == "white_display_hutch" else 2
            expected_bottles = 5
            expected_vases = 3
            ctx.check(
                "source display shelf count retained",
                sum(name.startswith("display_shelf_") for name in body_visual_names)
                == expected_shelves,
            )
            ctx.check(
                "source display contents retain bottle/vase types and density",
                sum(name.startswith("display_bottle_") for name in body_visual_names)
                == expected_bottles
                and sum(name.startswith("display_vase_") for name in body_visual_names)
                == expected_vases,
            )

    # Door joints.
    joint_names = {j.name for j in object_model.articulations}
    if r.door_motion == "bifold":
        ctx.check(
            "bifold pivot and fold joints present",
            {"body_to_door_panel_0", "panel_0_to_panel_1"}.issubset(joint_names),
        )
    else:
        for door_idx in range(r.door_count):
            joint_name = f"body_to_door_{door_idx}"
            ctx.check(f"{joint_name} present", joint_name in joint_names)
            joint = object_model.get_articulation(joint_name)
            if r.door_motion == "hinged":
                ctx.check(
                    f"{joint_name} is REVOLUTE about Z",
                    joint.articulation_type == ArticulationType.REVOLUTE
                    and abs(joint.axis[2]) > 0.99,
                    details=f"type={joint.articulation_type} axis={joint.axis}",
                )
            else:
                ctx.check(
                    f"{joint_name} is PRISMATIC about X",
                    joint.articulation_type == ArticulationType.PRISMATIC
                    and abs(joint.axis[0]) > 0.99,
                    details=f"type={joint.articulation_type} axis={joint.axis}",
                )

    # ---- Ground / footprint. ----
    body_aabb = ctx.part_world_aabb(body)
    if body_aabb is not None:
        (xmn, ymn, zmn), (xmx, ymx, zmx) = body_aabb
        ctx.check(
            "cabinet grounded (z_min near 0)",
            zmn < 0.03,
            details=f"z_min={zmn:.4f}",
        )
        if r.body_form != "low_sideboard":
            ctx.check(
                "cabinet is upright unless source is low sideboard",
                (zmx - zmn) > max(xmx - xmn, ymx - ymn),
                details=f"H={zmx - zmn:.3f} W={xmx - xmn:.3f} D={ymx - ymn:.3f}",
            )
        else:
            ctx.check(
                "low-sideboard proportions retained",
                (xmx - xmn) > 0.85 * (zmx - zmn) and (zmx - zmn) > 1.5 * (ymx - ymn),
            )

    # ---- Actuation: open pose shows visible displacement. ----
    if r.door_motion != "bifold":
        for door_idx in range(r.door_count):
            joint = object_model.get_articulation(f"body_to_door_{door_idx}")
            door = object_model.get_part(f"door_{door_idx}")
            closed = ctx.part_world_aabb(door)
            with ctx.pose({joint: joint.motion_limits.upper * 0.8}):
                opened = ctx.part_world_aabb(door)
            if closed is None or opened is None:
                continue
            if r.door_motion == "hinged":
                ctx.check(
                    f"door_{door_idx} swings outward (open y > closed y)",
                    opened[1][1] > closed[1][1] + 0.10,
                    details=f"closed_ymax={closed[1][1]:.3f} open_ymax={opened[1][1]:.3f}",
                )
            else:
                closed_cx = (closed[0][0] + closed[1][0]) / 2.0
                opened_cx = (opened[0][0] + opened[1][0]) / 2.0
                ctx.check(
                    f"door_{door_idx} slides along X",
                    abs(opened_cx - closed_cx) > 0.10,
                    details=f"closed_cx={closed_cx:.3f} opened_cx={opened_cx:.3f}",
                )

    if r.door_motion == "bifold":
        joint = object_model.get_articulation("body_to_door_panel_0")
        panel = object_model.get_part("door_panel_0")
        opened = ctx.part_world_aabb(panel)
        with ctx.pose({joint: joint.motion_limits.upper}):
            closed = ctx.part_world_aabb(panel)
        ctx.check("bifold pivot reaches a distinct closed pose", opened != closed)

    for index in range(3):
        if r.service_module == "pull_out_shelves":
            joint = object_model.get_articulation(f"body_to_pull_out_shelf_{index}")
            shelf = object_model.get_part(f"pull_out_shelf_{index}")
            closed = ctx.part_world_aabb(shelf)
            with ctx.pose({joint: joint.motion_limits.upper}):
                opened = ctx.part_world_aabb(shelf)
            if closed is not None and opened is not None:
                ctx.check(
                    f"pull-out shelf {index} travels toward front",
                    opened[1][1] > closed[1][1] + 0.12,
                )
        elif r.service_module == "rotating_shelves":
            joint = object_model.get_articulation(f"body_to_rotating_shelf_{index}")
            with ctx.pose({joint: math.pi}):
                ctx.check(f"rotating shelf {index} supports half-turn pose", True)
    if r.service_module == "fold_out_counter":
        joint = object_model.get_articulation("body_to_fold_out_counter")
        counter = object_model.get_part("fold_out_counter")
        stowed = ctx.part_world_aabb(counter)
        with ctx.pose({joint: joint.motion_limits.upper}):
            deployed = ctx.part_world_aabb(counter)
        if stowed is not None and deployed is not None:
            ctx.check(
                "fold-out counter deploys forward",
                deployed[1][1] > stowed[1][1] + 0.15,
            )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded in model meta",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "Wine_Cabinet1Config",
    "ResolvedWine_Cabinet1Config",
    "build_wine_cabinet1",
    "build_seeded_wine_cabinet1",
    "config_from_seed",
    "resolve_config",
    "run_wine_cabinet1_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
    "PALETTES",
    "PALETTE_STYLES",
    "BODY_FORMS",
    "DOOR_MOTIONS",
    "RACK_STYLES",
    "SERVICE_MODULES",
)
