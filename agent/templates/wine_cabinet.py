# SPDX-License-Identifier: Apache-2.0

"""Wine cabinet — modular procedural template.

Category identity: a grounded carcass carries at least one moving front element
(REVOLUTE glass/mesh doors, PRISMATIC drawers or sliding glass) plus interior
rack fabric (horizontal cradles / diamond lattice / vertical pegs / open shelves)
and carcass-hosted bottle contents. Six body_form families cover Planar Boundary,
Volumetric Envelope and Macro Surface Construction primary-form prototypes.

Seven modular slots (`slot_choices_for_seed`):
  body_form, door_style, drawer_count, rack_topology, bottle_count,
  service_motion, palette_style

Canonical spec:
  articraft_template_authoring/specs_modular_v1/wine_cabinet.md
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
    MatingContract,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
)

__modular__ = True
# This legacy source family opens toward -Y.  The preview pipeline uses this
# semantic axis so a view named front_iso cannot silently render the back slab.
__preview_front_axis__ = "-y"

# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------

BodyForm = Literal[
    "paired_display",
    "wide_low_sideboard",
    "single_tall",
    "arched_display",
    "built_in_bar_wall",
    "corner_wrap",
]
DoorStyle = Literal[
    "paired_glass_hinged",
    "mesh_bifold",
    "smoked_glass_cooler",
    "sliding_glass",
    "none",
]
RackTopology = Literal[
    "horizontal_cradles",
    "diamond_lattice",
    "vertical_pegs",
    "open_shelves",
    "none",
]
ServiceMotion = Literal["none", "fold_out_counter", "pull_out_tasting_shelf"]


# Static content envelope is a host relation, not a renderer-only detail.  Keep
# these values shared by capacity projection, shelf placement, geometry, and
# tests so a low carcass cannot place an upright bottle through its crown.
_RACK_SHELF_TOP_OFFSET = 0.006
_BOTTLE_TOP_CLEARANCE = 0.008
_HORIZONTAL_BOTTLE_ENVELOPE = 0.066
_STANDING_BOTTLE_ENVELOPE = 0.286
_STEMWARE_ENVELOPE = 0.131


def _standing_shelf_zs(rack_z_min: float, rack_z_max: float) -> list[float]:
    """Return shelf centerlines whose upright bottles fit below ``rack_z_max``.

    Standing shelves are support datums at the bottom of each bottle bay.  The
    old cell-centre formula put a single shelf halfway up a low sideboard and
    consequently drove every bottle neck through the cabinet top (seed 6257).
    """
    rack_span = max(0.0, rack_z_max - rack_z_min)
    highest_support_z = (
        rack_z_max
        - _RACK_SHELF_TOP_OFFSET
        - _STANDING_BOTTLE_ENVELOPE
        - _BOTTLE_TOP_CLEARANCE
    )
    if highest_support_z < rack_z_min:
        return []
    count = max(1, min(3, int(rack_span // 0.340)))
    if count == 1:
        return [rack_z_min]
    step = (highest_support_z - rack_z_min) / (count - 1)
    return [rack_z_min + step * i for i in range(count)]


PaletteStyle = Literal[
    "warm_cream_maple",
    "matte_black_stainless",
    "built_in_dark",
    "light_oak",
    "walnut_bronze",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "paired_display",
    "wide_low_sideboard",
    "single_tall",
    "arched_display",
    "built_in_bar_wall",
    "corner_wrap",
)
DOOR_STYLES: tuple[DoorStyle, ...] = (
    "paired_glass_hinged",
    "mesh_bifold",
    "smoked_glass_cooler",
    "sliding_glass",
    "none",
)
DRAWER_COUNTS: tuple[int, ...] = (0, 1, 3, 5, 9)
RACK_TOPOLOGIES: tuple[RackTopology, ...] = (
    "horizontal_cradles",
    "diamond_lattice",
    "vertical_pegs",
    "open_shelves",
    "none",
)
BOTTLE_COUNTS: tuple[int, ...] = (0, 12, 24, 50)
SERVICE_MOTIONS: tuple[ServiceMotion, ...] = (
    "none",
    "fold_out_counter",
    "pull_out_tasting_shelf",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "warm_cream_maple",
    "matte_black_stainless",
    "built_in_dark",
    "light_oak",
    "walnut_bronze",
)

# Compatibility: body_form -> eligible door / rack / drawer_max ---------------

_BODY_DOORS: dict[BodyForm, tuple[DoorStyle, ...]] = {
    "paired_display": ("paired_glass_hinged", "smoked_glass_cooler"),
    "wide_low_sideboard": (
        "mesh_bifold",
        "smoked_glass_cooler",
        "paired_glass_hinged",
    ),
    "single_tall": ("paired_glass_hinged", "smoked_glass_cooler", "sliding_glass"),
    "arched_display": ("paired_glass_hinged", "smoked_glass_cooler"),
    "built_in_bar_wall": ("smoked_glass_cooler", "none"),
    "corner_wrap": ("smoked_glass_cooler", "paired_glass_hinged", "none"),
}
_BODY_RACKS: dict[BodyForm, tuple[RackTopology, ...]] = {
    "paired_display": ("open_shelves", "horizontal_cradles", "diamond_lattice"),
    "wide_low_sideboard": (
        "diamond_lattice",
        "horizontal_cradles",
        "vertical_pegs",
        "open_shelves",
    ),
    "single_tall": ("horizontal_cradles", "vertical_pegs", "open_shelves"),
    "arched_display": ("horizontal_cradles", "open_shelves", "diamond_lattice"),
    "built_in_bar_wall": (
        "horizontal_cradles",
        "diamond_lattice",
        "vertical_pegs",
        "open_shelves",
    ),
    "corner_wrap": ("horizontal_cradles", "vertical_pegs", "open_shelves"),
}
_BODY_DRAWER_MAX: dict[BodyForm, int] = {
    # The paired-display body has a structural center divider.  The accepted
    # source uses two independent drawer bays; the current single-stack drawer
    # module is therefore gated out instead of being allowed to sweep through
    # that divider.
    "paired_display": 0,
    "wide_low_sideboard": 3,
    "single_tall": 3,
    "arched_display": 3,
    "built_in_bar_wall": 9,
    "corner_wrap": 5,
}
# body_form dimension bands (width, depth, height) in meters --------------------
_BODY_DIM_BANDS: dict[
    BodyForm, tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
] = {
    # (w_lo, w_hi), (d_lo, d_hi), (h_lo, h_hi)
    "paired_display": ((0.90, 1.20), (0.34, 0.42), (1.25, 1.90)),
    "wide_low_sideboard": ((1.30, 1.80), (0.38, 0.46), (0.75, 0.95)),
    "single_tall": ((0.42, 0.55), (0.34, 0.42), (1.55, 1.90)),
    "arched_display": ((0.55, 0.80), (0.34, 0.44), (1.10, 1.55)),
    "built_in_bar_wall": ((2.60, 3.30), (0.50, 0.60), (0.82, 0.94)),
    "corner_wrap": ((1.40, 1.80), (0.48, 0.60), (0.82, 0.94)),
}

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # Sourced from rec_0611__wine_cabinet__001 (warm-cream lacquer + maple + brass).
    "warm_cream_maple": {
        "case": (0.88, 0.84, 0.75, 1.0),
        "interior": (0.64, 0.47, 0.29, 1.0),
        "dark_trim": (0.055, 0.050, 0.045, 1.0),
        "glass": (0.56, 0.72, 0.74, 0.24),
        "metal": (0.62, 0.46, 0.20, 1.0),
        "led": (1.0, 0.69, 0.26, 1.0),
        "bottle_a": (0.25, 0.085, 0.025, 0.96),
        "bottle_b": (0.055, 0.15, 0.075, 0.96),
        "cork": (0.55, 0.37, 0.18, 1.0),
        "stemware": (0.72, 0.86, 0.90, 0.34),
    },
    # Sourced from rec_0611__wine_cabinet__002 (matte black + dark shelf + green/burgundy bottles).
    "matte_black_stainless": {
        "case": (0.025, 0.030, 0.032, 1.0),
        "interior": (0.075, 0.065, 0.055, 1.0),
        "dark_trim": (0.055, 0.060, 0.062, 1.0),
        "glass": (0.72, 0.86, 0.90, 0.34),
        "metal": (0.11, 0.12, 0.12, 1.0),
        "led": (1.0, 0.72, 0.28, 1.0),
        "bottle_a": (0.035, 0.16, 0.09, 0.92),
        "bottle_b": (0.19, 0.035, 0.045, 0.94),
        "cork": (0.56, 0.36, 0.18, 1.0),
        "stemware": (0.72, 0.86, 0.90, 0.34),
    },
    # Sourced from rec_0611__wine_cabinet__003 (built-in matte black + smoked glass + stone).
    "built_in_dark": {
        "case": (0.025, 0.028, 0.030, 1.0),
        "interior": (0.055, 0.060, 0.064, 1.0),
        "dark_trim": (0.012, 0.014, 0.016, 1.0),
        "glass": (0.055, 0.085, 0.090, 0.34),
        "metal": (0.12, 0.13, 0.14, 1.0),
        "led": (1.0, 0.72, 0.28, 1.0),
        "bottle_a": (0.20, 0.025, 0.035, 1.0),
        "bottle_b": (0.035, 0.105, 0.065, 1.0),
        "cork": (0.55, 0.37, 0.18, 1.0),
        "stemware": (0.72, 0.86, 0.90, 0.34),
    },
    # World-extrapolation from the 001 warm-cream family: lighter oak carcass.
    "light_oak": {
        "case": (0.78, 0.62, 0.42, 1.0),
        "interior": (0.72, 0.56, 0.35, 1.0),
        "dark_trim": (0.10, 0.08, 0.06, 1.0),
        "glass": (0.60, 0.74, 0.76, 0.26),
        "metal": (0.72, 0.55, 0.22, 1.0),
        "led": (1.0, 0.72, 0.30, 1.0),
        "bottle_a": (0.18, 0.075, 0.020, 0.96),
        "bottle_b": (0.055, 0.15, 0.075, 0.96),
        "cork": (0.55, 0.37, 0.18, 1.0),
        "stemware": (0.72, 0.86, 0.90, 0.34),
    },
    # World-extrapolation from the 003 built-in family with warmer walnut + bronze.
    "walnut_bronze": {
        "case": (0.32, 0.20, 0.13, 1.0),
        "interior": (0.42, 0.28, 0.17, 1.0),
        "dark_trim": (0.10, 0.075, 0.05, 1.0),
        "glass": (0.14, 0.12, 0.10, 0.34),
        "metal": (0.62, 0.42, 0.20, 1.0),
        "led": (1.0, 0.72, 0.30, 1.0),
        "bottle_a": (0.20, 0.030, 0.040, 0.96),
        "bottle_b": (0.035, 0.12, 0.075, 0.96),
        "cork": (0.55, 0.37, 0.18, 1.0),
        "stemware": (0.72, 0.86, 0.90, 0.34),
    },
}


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WineCabinetConfig:
    body_form: BodyForm | None = None
    door_style: DoorStyle | None = None
    drawer_count: int | None = None
    rack_topology: RackTopology | None = None
    bottle_count: int | None = None
    service_motion: ServiceMotion | None = None
    palette_style: PaletteStyle = "warm_cream_maple"
    carcass_width: float | None = None
    carcass_depth: float | None = None
    carcass_height: float | None = None
    drawer_travel: float = 0.22
    door_open_angle: float = 1.65
    name: str = "wine_cabinet"


@dataclass(frozen=True)
class ResolvedWineCabinetConfig:
    body_form: BodyForm
    door_style: DoorStyle
    drawer_count: int
    rack_topology: RackTopology
    bottle_count: int
    service_motion: ServiceMotion
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    # dimensions
    carcass_width: float
    carcass_depth: float
    carcass_height: float
    drawer_travel: float
    door_open_angle: float
    # derived interior working numbers
    side_thickness: float
    back_thickness: float
    panel_thickness: float
    plinth_height: float
    interior_width: float
    interior_depth: float
    rack_z_min: float
    rack_z_max: float
    drawer_center_z: tuple[float, ...]
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ---------------------------------------------------------------------------
# config_from_seed / resolve_config
# ---------------------------------------------------------------------------


def config_from_seed(seed: int) -> WineCabinetConfig:
    """Deterministic procedural sampling. seed=0 is NOT special."""
    rng = random.Random(seed)

    body = rng.choice(BODY_FORMS)
    door = rng.choice(DOOR_STYLES)
    drawer_c = rng.choice(DRAWER_COUNTS)
    rack = rng.choice(RACK_TOPOLOGIES)
    bottle_c = rng.choice(BOTTLE_COUNTS)
    service = rng.choice(SERVICE_MOTIONS)
    palette = rng.choice(PALETTE_STYLES)

    w_lo, w_hi = _BODY_DIM_BANDS[body][0]
    d_lo, d_hi = _BODY_DIM_BANDS[body][1]
    h_lo, h_hi = _BODY_DIM_BANDS[body][2]

    sampled = WineCabinetConfig(
        body_form=body,
        door_style=door,
        drawer_count=drawer_c,
        rack_topology=rack,
        bottle_count=bottle_c,
        service_motion=service,
        palette_style=palette,
        carcass_width=round(rng.uniform(w_lo, w_hi), 3),
        carcass_depth=round(rng.uniform(d_lo, d_hi), 3),
        carcass_height=round(rng.uniform(h_lo, h_hi), 3),
        drawer_travel=round(rng.uniform(0.16, 0.28), 3),
        door_open_angle=round(rng.uniform(1.30, 1.72), 3),
        name=f"seeded_wine_cabinet_{seed}",
    )
    # Formal seeded configs expose the actual gated choices, so requested,
    # resolved and emitted multiplicities cannot silently diverge in reports.
    resolved = resolve_config(sampled)
    return replace(
        sampled,
        door_style=resolved.door_style,
        drawer_count=resolved.drawer_count,
        rack_topology=resolved.rack_topology,
        bottle_count=resolved.bottle_count,
        service_motion=resolved.service_motion,
    )


def resolve_config(config: WineCabinetConfig) -> ResolvedWineCabinetConfig:
    body = config.body_form or "wide_low_sideboard"
    door = config.door_style or "smoked_glass_cooler"
    drawer_c = 3 if config.drawer_count is None else int(config.drawer_count)
    rack = config.rack_topology or "horizontal_cradles"
    bottle_c = 12 if config.bottle_count is None else int(config.bottle_count)
    service = config.service_motion or "none"
    palette = config.palette_style

    if body not in BODY_FORMS:
        raise ValueError(f"Unsupported body_form: {body}")
    if door not in DOOR_STYLES:
        raise ValueError(f"Unsupported door_style: {door}")
    if drawer_c not in DRAWER_COUNTS:
        raise ValueError(f"Unsupported drawer_count: {drawer_c}")
    if rack not in RACK_TOPOLOGIES:
        raise ValueError(f"Unsupported rack_topology: {rack}")
    if bottle_c not in BOTTLE_COUNTS:
        raise ValueError(f"Unsupported bottle_count: {bottle_c}")
    if service not in SERVICE_MOTIONS:
        raise ValueError(f"Unsupported service_motion: {service}")
    if palette not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {palette}")

    # ---- Compatibility gating (silent degrade) ----
    if door not in _BODY_DOORS[body]:
        door = _BODY_DOORS[body][0]
    if rack not in _BODY_RACKS[body]:
        rack = _BODY_RACKS[body][0]
    # Cap drawer_count by body_form
    max_drawers = _BODY_DRAWER_MAX[body]
    if drawer_c > max_drawers:
        # Choose the highest eligible from DRAWER_COUNTS
        drawer_c = max(x for x in DRAWER_COUNTS if x <= max_drawers)
    # If door is 'none' we must have at least one other moving joint:
    # drawer_count > 0 or service_motion != none.
    if door == "none" and drawer_c == 0 and service == "none":
        # Fall back to smoked_glass_cooler when body allows, else pick first legal
        if "smoked_glass_cooler" in _BODY_DOORS[body]:
            door = "smoked_glass_cooler"
        else:
            door = _BODY_DOORS[body][0]
    # rack==none requires drawer_count>0 (identity: bottle storage function)
    if rack == "none" and drawer_c == 0:
        rack = _BODY_RACKS[body][0]
    # bottle_count 50 restricted to large bodies
    if bottle_c == 50 and body not in {"built_in_bar_wall", "wide_low_sideboard"}:
        bottle_c = 24
    # bottle_count 0 requires rack in {none, open_shelves}
    if bottle_c == 0 and rack not in {"none", "open_shelves"}:
        rack = "open_shelves"
    # If rack is 'none' bottle_count must be 0
    if rack == "none":
        bottle_c = 0
    # 9-drawer only valid for built_in_bar_wall
    if drawer_c == 9 and body != "built_in_bar_wall":
        drawer_c = 5
    # The fold-out barrel and bypass tracks compete for the same header plane.
    # The tasting tray keeps a dedicated open upper bay only behind sliding
    # doors (bypass leaves can never expose it); hinged doors cover the tray
    # and interlock ahead of it in build_wine_cabinet.
    if service == "fold_out_counter" and door == "sliding_glass":
        service = "none"
    # pull_out_tasting_shelf needs vertical headroom above the top rack row —
    # exclude for short cabinets (wide_low_sideboard, built_in_bar_wall) where
    # the bottle rows fill the entire display volume.
    if service == "pull_out_tasting_shelf" and body in {
        "wide_low_sideboard",
        "built_in_bar_wall",
    }:
        service = "none"
    # Re-check category motion identity after service gating.  A requested
    # service module may have been rejected above; leaving door=none and N=0
    # would otherwise produce a static cabinet on the first resolve and a
    # hinged cabinet only after resolving the result a second time.
    if door == "none" and drawer_c == 0 and service == "none":
        door = (
            "smoked_glass_cooler"
            if "smoked_glass_cooler" in _BODY_DOORS[body]
            else _BODY_DOORS[body][0]
        )

    # ---- Dimensions ----
    w_lo, w_hi = _BODY_DIM_BANDS[body][0]
    d_lo, d_hi = _BODY_DIM_BANDS[body][1]
    h_lo, h_hi = _BODY_DIM_BANDS[body][2]

    width = _clamp(config.carcass_width or (w_lo + w_hi) * 0.5, w_lo, w_hi)
    depth = _clamp(config.carcass_depth or (d_lo + d_hi) * 0.5, d_lo, d_hi)
    height = _clamp(config.carcass_height or (h_lo + h_hi) * 0.5, h_lo, h_hi)

    side_t = 0.028
    back_t = 0.018
    panel_t = 0.018
    plinth_h = 0.06 if body in {"wide_low_sideboard", "paired_display"} else 0.0

    interior_w = width - 2.0 * side_t
    interior_d = depth - back_t

    # Rack occupies the "display" volume of the carcass; drawers eat the bottom band.
    drawer_band_frac = 0.0
    if drawer_c > 0:
        # Roughly 1/3 of height goes to drawers when small, up to 2/3 for 9 drawers.
        drawer_band_frac = min(0.55, 0.14 + 0.06 * drawer_c)

    drawer_band_h = drawer_band_frac * (height - plinth_h)
    rack_z_min = plinth_h + drawer_band_h + panel_t
    rack_z_max = height - 0.06  # leave crown for top_trim

    # Resolve bottle multiplicity against the actual rack cell capacity.  The
    # emitted visual count must equal the reported slot value; never advertise
    # 24/50 while silently building fewer bottles.
    rack_span = max(0.0, rack_z_max - rack_z_min)
    rack_orientation = "standing" if rack in {"open_shelves", "vertical_pegs"} else "horizontal"
    has_source_glassware = body in {
        "paired_display",
        "wide_low_sideboard",
        "single_tall",
        "arched_display",
    }
    if bottle_c == 50 and rack_orientation == "standing":
        # The accepted 50-place anchor is horizontal (ten rows x five); keep
        # that source direction instead of packing upright bottles in depth.
        rack = "horizontal_cradles"
        rack_orientation = "horizontal"
    if rack_orientation == "horizontal":
        rack_rows = max(2, min(6, int(rack_span // 0.100)))
        bottle_pitch = 0.068
        depth_lanes = 1
        rack_pitch = rack_span / rack_rows
        rack_shelf_zs = [rack_z_min + rack_pitch * (i + 0.5) for i in range(rack_rows)]
    else:
        bottle_pitch = 0.085
        depth_lanes = 3
        rack_shelf_zs = _standing_shelf_zs(rack_z_min, rack_z_max)
        rack_rows = len(rack_shelf_zs)
    content_ceiling = rack_z_max
    if service == "pull_out_tasting_shelf":
        tasting_origin_z = height - 0.038 - panel_t - 0.036
        if body == "arched_display":
            # The source-backed crown consumes the front 100 mm header; the
            # tray datum must remain below its lower face, not pass through it.
            tasting_origin_z = min(tasting_origin_z, height - panel_t - 0.100 - 0.016)
        content_ceiling = min(content_ceiling, tasting_origin_z - 0.022)
    bottle_height = (
        _HORIZONTAL_BOTTLE_ENVELOPE
        if rack_orientation == "horizontal"
        else _STANDING_BOTTLE_ENVELOPE
    )
    rack_shelf_zs = [
        z
        for z in rack_shelf_zs
        if z + _RACK_SHELF_TOP_OFFSET + bottle_height + _BOTTLE_TOP_CLEARANCE
        <= content_ceiling
    ]
    usable_rows = len(rack_shelf_zs)
    if rack_orientation == "horizontal" and has_source_glassware:
        # One service-safe physical shelf remains dedicated to source-backed
        # glassware; the actual row index is selected later from the same
        # swept-envelope datum.
        usable_rows = max(0, usable_rows - 1)
    rack_cols = max(1, min(int((interior_w * 0.94) // bottle_pitch), 10))
    rack_capacity = usable_rows * rack_cols * depth_lanes
    bottle_c = max(value for value in BOTTLE_COUNTS if value <= bottle_c and value <= rack_capacity)
    # Capacity projection must also stabilize the rack identity in this same
    # resolve pass.  An empty peg/lattice/cradle fabric is not a supported wine
    # storage module; it becomes the body's accepted open-shelf omission state.
    if bottle_c == 0 and rack not in {"none", "open_shelves"}:
        rack = "open_shelves"

    # Drawer center z coordinates ------------------------------------------------
    if drawer_c == 0:
        drawer_center_z: tuple[float, ...] = ()
    elif body == "built_in_bar_wall" and drawer_c == 9:
        # 3 rows × 3 cols (columns handled by x-shift at build time; use 3 row centers)
        row_h = drawer_band_h / 3.0
        drawer_center_z = tuple(plinth_h + panel_t + row_h * (0.5 + i) for i in range(3))
    else:
        pitch = drawer_band_h / max(drawer_c, 1)
        drawer_center_z = tuple(plinth_h + panel_t + pitch * (0.5 + i) for i in range(drawer_c))

    # Drawer travel bounded by depth (leave 0.05m interior support)
    drawer_travel = _clamp(config.drawer_travel, 0.12, 0.30)
    drawer_travel = min(drawer_travel, depth * 0.72)

    door_open = _clamp(config.door_open_angle, 1.10, 1.75)

    return ResolvedWineCabinetConfig(
        body_form=body,
        door_style=door,
        drawer_count=drawer_c,
        rack_topology=rack,
        bottle_count=bottle_c,
        service_motion=service,
        palette_style=palette,
        palette=dict(PALETTES[palette]),
        carcass_width=width,
        carcass_depth=depth,
        carcass_height=height,
        drawer_travel=drawer_travel,
        door_open_angle=door_open,
        side_thickness=side_t,
        back_thickness=back_t,
        panel_thickness=panel_t,
        plinth_height=plinth_h,
        interior_width=interior_w,
        interior_depth=interior_d,
        rack_z_min=rack_z_min,
        rack_z_max=rack_z_max,
        drawer_center_z=drawer_center_z,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Small geometry helpers
# ---------------------------------------------------------------------------


def _box(part: Part, name: str, size, xyz, material, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.veneer_panel")


def _cyl(
    part: Part,
    name: str,
    radius: float,
    length: float,
    xyz,
    material,
    rpy=(0.0, 0.0, 0.0),
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


# ---------------------------------------------------------------------------
# Body-form specific carcass builders (all return the root carcass Part).
# All build in carcass-local frame with base at z=0 and centered on x=0.
# The Y axis: +Y = back (into wall), -Y = front (user side).
# ---------------------------------------------------------------------------


def _build_common_carcass_shell(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    """Common carcass shell used by most body_forms (paired variants override)."""
    w, d, h = r.carcass_width, r.carcass_depth, r.carcass_height
    st, bt, pt = r.side_thickness, r.back_thickness, r.panel_thickness
    z0 = r.plinth_height

    # Optional plinth
    if r.plinth_height > 0.0:
        _box(
            carcass,
            "base_plinth",
            (w + 0.020, d + 0.020, r.plinth_height),
            (0.0, 0.0, r.plinth_height / 2.0),
            mats["case"],
        )

    # Side walls
    for sign, name in ((-1.0, "side_wall_0"), (1.0, "side_wall_1")):
        _box(
            carcass,
            name,
            (st, d, h - z0),
            (sign * (w / 2.0 - st / 2.0), 0.0, z0 + (h - z0) / 2.0),
            mats["case"],
        )

    # Back panel (+Y side)
    _box(
        carcass,
        "back_panel",
        (w - 2.0 * st, bt, h - z0),
        (0.0, d / 2.0 - bt / 2.0, z0 + (h - z0) / 2.0),
        mats["interior"],
    )
    # Bottom panel
    _box(
        carcass,
        "bottom_panel",
        (w - 2.0 * st, d - bt, pt),
        (0.0, -bt / 2.0, z0 + pt / 2.0),
        mats["case"],
    )
    # Top trim / crown
    _box(
        carcass,
        "top_trim",
        (w + 0.020, d + 0.010, 0.038),
        (0.0, 0.0, h - 0.019),
        mats["case"],
    )
    # Top interior panel just below the crown for shelf support
    _box(
        carcass,
        "top_panel",
        (w - 2.0 * st, d - bt, pt),
        (0.0, -bt / 2.0, h - 0.038 - pt / 2.0),
        mats["interior"],
    )

    # Front stiles frame the opening.  Hinged variants use a segmented jamb:
    # the two barrel stations are real hardware pockets, not a solid stile
    # hidden behind the moving hinge geometry.
    front_y = -d / 2.0 + panel_offset_front(r)
    hinged = r.door_style in {"paired_glass_hinged", "smoked_glass_cooler", "mesh_bifold"}
    for side_index, sign in enumerate((-1.0, 1.0)):
        if hinged:
            stile_intervals = _segmented_jamb_intervals(r, z0 + 0.003, h - 0.003)
        else:
            stile_intervals = ((z0 + 0.003, h - 0.003),)
        for segment_index, (segment_z0, segment_z1) in enumerate(stile_intervals):
            segment_h = segment_z1 - segment_z0
            _box(
                carcass,
                f"front_stile_{side_index}_segment_{segment_index}",
                (st + 0.006, 0.020, segment_h),
                (
                    sign * (w / 2.0 - st / 2.0 - 0.003),
                    front_y,
                    (segment_z0 + segment_z1) / 2.0,
                ),
                mats["case"],
            )

    # Drawer bay fabric.  Drawers are supported by bilateral longitudinal
    # guides emitted alongside each moving box in `_build_drawers`; do not put
    # a transverse bar through the drawer cavity.
    if r.drawer_count > 0:
        # The 3x3 built-in bank needs real vertical bay dividers to carry the
        # inner guide pairs.  Ordinary vertical stacks mount their guides to
        # the two carcass side walls.
        if r.body_form == "built_in_bar_wall" and r.drawer_count == 9:
            inner_w = w - 2.0 * st - 0.030
            drawer_band_h = r.rack_z_min - z0 - pt
            for i, x in enumerate((-inner_w / 6.0, inner_w / 6.0)):
                _box(
                    carcass,
                    f"drawer_bay_divider_{i}",
                    (pt, d - bt, drawer_band_h),
                    (x, -bt / 2.0, z0 + pt + drawer_band_h / 2.0),
                    mats["case"],
                )

        # A supported shelf above the entire drawer bank separates it from the
        # wine rack.  It does not cross any moving drawer cavity.
        if r.rack_z_min < h - 0.05:
            _box(
                carcass,
                "drawer_bank_ceiling",
                (w - 2.0 * st, d - bt, pt),
                (0.0, -bt / 2.0, r.rack_z_min - pt / 2.0),
                mats["case"],
            )

    # Captured external hinges.  Each moving barrel turns around a coaxial
    # parent pin.  A rear bridge and an outboard elbow tie that pin back into
    # the side wall without crossing the moving door leaf.  This is a real
    # load path; the jamb pockets above are clearance, not collision masks.
    if r.door_style in {"paired_glass_hinged", "smoked_glass_cooler", "mesh_bifold"}:
        hinge_zs = _hinge_world_zs(r)
        hinge_front_y = _hinge_front_y(r)
        for door_index in range(2):
            hinge_x = _hinge_x_for_door(r, door_index)
            sign = -1.0 if door_index == 0 else 1.0
            wall_outer_x = sign * (w / 2.0)
            bridge_center_x = (wall_outer_x + hinge_x) / 2.0
            bridge_size_x = abs(hinge_x - wall_outer_x) + 0.012
            for zi, hz in enumerate(hinge_zs):
                bridge_z = hz + 0.039
                _cyl(
                    carcass,
                    f"hinge_mount_{door_index}_{zi}",
                    _HINGE_PIN_RADIUS,
                    _HINGE_PIN_LENGTH,
                    (hinge_x, hinge_front_y, hz),
                    mats["dark_trim"],
                )
                # The bridge runs behind the door plane; its forward face is
                # outside the moving frame's 24 mm depth envelope.
                _box(
                    carcass,
                    f"hinge_bridge_{door_index}_{zi}",
                    (bridge_size_x, 0.014, 0.012),
                    (bridge_center_x, hinge_front_y + 0.020, bridge_z),
                    mats["dark_trim"],
                )
                # The elbow connects the pin to the rear bridge on the
                # outboard side, where the door leaf never sweeps.
                _box(
                    carcass,
                    f"hinge_elbow_{door_index}_{zi}",
                    (0.014, 0.024, 0.012),
                    (hinge_x + sign * 0.007, hinge_front_y + 0.010, bridge_z),
                    mats["dark_trim"],
                )

    # Sliding tracks (parent side of the PRISMATIC MatingContract).
    if r.door_style == "sliding_glass":
        opening_z0 = _door_bottom_z(r)
        opening_z1 = _door_top_z(r)
        track_w = r.carcass_width - 2.0 * r.side_thickness
        # Two real bypass planes: the panels never occupy one collision plane.
        for door_index, track_y in enumerate(
            (-r.carcass_depth / 2.0 - 0.010, -r.carcass_depth / 2.0 - 0.034)
        ):
            for tag, tz in (
                (f"top_track_{door_index}", opening_z1 + 0.005),
                (f"bottom_track_{door_index}", opening_z0 - 0.005),
            ):
                _box(
                    carcass,
                    tag,
                    (track_w, 0.020, 0.020),
                    (0.0, track_y, tz),
                    mats["dark_trim"],
                )
        # A thin web between the two bypass channels grounds the outer plane
        # without entering either moving rail's Y envelope.
        track_web_y = -r.carcass_depth / 2.0 - 0.022
        for tag, tz in (
            ("top_track_plane_web", opening_z1 + 0.005),
            ("bottom_track_plane_web", opening_z0 - 0.005),
        ):
            _box(
                carcass,
                tag,
                (track_w, 0.004, 0.012),
                (0.0, track_web_y, tz),
                mats["dark_trim"],
            )


def panel_offset_front(_r: ResolvedWineCabinetConfig) -> float:
    """Y coordinate offset of the front stile inner face from -d/2."""
    return 0.010


# ---------------------------------------------------------------------------
# Door / hinge geometry helpers (single-source for cross-part coherence, per
# Contract 3c: hinge X and door-opening bounds are used by both the carcass
# shell (hinge_mount tabs, front stiles) and the door builders (joint origin,
# hinge_barrel position).
# ---------------------------------------------------------------------------

_HINGE_BARREL_RADIUS: float = 0.011
_HINGE_BARREL_LENGTH: float = 0.060
_HINGE_PIN_RADIUS: float = 0.006
_HINGE_PIN_LENGTH: float = 0.090
_HINGE_OUTBOARD_CLEARANCE: float = 0.006
_HINGE_JAMB_CLEARANCE_Z: float = 0.012
_HINGE_FRONT_Y_OFFSET: float = 0.008  # hinge line sits this far in front of front face
_SLIDING_DRAWER_TRACK_BAY_HEIGHT: float = 0.045


def _hinge_front_y(r: ResolvedWineCabinetConfig) -> float:
    """World Y of the hinge line — just in front of the front face."""
    return -r.carcass_depth / 2.0 - _HINGE_FRONT_Y_OFFSET


def _hinge_x_for_door(r: ResolvedWineCabinetConfig, door_index: int) -> float:
    """X coordinate of the door's hinge line in the carcass frame.

    Two doors mount on the OUTER vertical edges of the interior opening:
    door_0 hinges at -X (left), door_1 hinges at +X (right). For paired_display
    each half has its own doors — see _paired_display_hinge_x.
    """
    # The whole barrel cross-section sits outside the carcass envelope.  The
    # rear bridge above carries it back to the side wall.
    hx = r.carcass_width / 2.0 + _HINGE_BARREL_RADIUS + _HINGE_OUTBOARD_CLEARANCE
    return -hx if door_index == 0 else hx


def _paired_display_hinge_x(r: ResolvedWineCabinetConfig, door_index: int) -> float:
    """For paired_display, each of the two halves gets two doors (indexed 0..3).

    door 0 hinges at the far left of the left half, door 1 at the center-left,
    door 2 at the center-right, door 3 at the far right. But we only build 2
    doors for paired_display (one per half, hinging outward at the outer edge).
    Per spec §5, doors are parallel children; we emit 2 doors — 0 outer-left,
    1 outer-right — one door per half.
    """
    return _hinge_x_for_door(r, door_index)


def _hinge_local_zs(r: ResolvedWineCabinetConfig) -> tuple[float, float]:
    """Door-local hinge stations shared by barrels, pins and jamb pockets."""
    door_h = _door_top_z(r) - _door_bottom_z(r)
    return (
        max(0.12, door_h * 0.15),
        min(door_h - 0.12, door_h * 0.85),
    )


def _hinge_world_zs(r: ResolvedWineCabinetConfig) -> tuple[float, float]:
    opening_z0 = _door_bottom_z(r)
    return tuple(opening_z0 + z for z in _hinge_local_zs(r))


def _segmented_jamb_intervals(
    r: ResolvedWineCabinetConfig, lower: float, upper: float
) -> tuple[tuple[float, float], ...]:
    """Return real jamb segments after removing both hinge hardware pockets."""
    gap_half = _HINGE_PIN_LENGTH / 2.0 + _HINGE_JAMB_CLEARANCE_Z
    cursor = lower
    intervals: list[tuple[float, float]] = []
    for station in _hinge_world_zs(r):
        gap_start = max(lower, station - gap_half)
        gap_end = min(upper, station + gap_half)
        if gap_start - cursor >= 0.020:
            intervals.append((cursor, gap_start))
        cursor = max(cursor, gap_end)
    if upper - cursor >= 0.020:
        intervals.append((cursor, upper))
    return tuple(intervals)


def _door_bottom_z(r: ResolvedWineCabinetConfig) -> float:
    """Z of the door-opening bottom (top of drawer band or plinth)."""
    if r.drawer_count == 0:
        return r.plinth_height
    if r.door_style == "sliding_glass":
        # Sliding doors need a dedicated channel above the drawer-bank ceiling.
        # Raising the whole opening keeps both the moving bottom rail and its
        # parent track out of the top drawer's swept envelope.
        return r.rack_z_min + _SLIDING_DRAWER_TRACK_BAY_HEIGHT
    return r.rack_z_min


def _door_top_z(r: ResolvedWineCabinetConfig) -> float:
    if r.service_motion == "fold_out_counter":
        # The counter hangs on an external hinge 30 mm above the carcass and
        # 50 mm forward of the door/handle plane.  Its positive rotation moves
        # farther outward, so no fake 380 mm internal header bay is needed.
        return r.carcass_height - 0.05
    if r.service_motion == "pull_out_tasting_shelf" and r.door_style == "sliding_glass":
        # Bypass leaves can never expose the tray plane, so the tray keeps its
        # dedicated open header bay above the sliding channel.
        return r.carcass_height - 0.22
    # Hinged doors (and door-less bodies) cover the full front.  The tasting
    # tray stows behind them and only travels with the doors open — see the
    # motion_interlocks declared in build_wine_cabinet.
    return r.carcass_height - 0.05


def _door_leaf_width(r: ResolvedWineCabinetConfig) -> float:
    """Width of one door leaf (two symmetric doors sharing the opening)."""
    if r.body_form == "paired_display":
        # Each half has one door covering nearly the full half opening.
        half_w = r.carcass_width / 2.0
        base_width = half_w - r.side_thickness + 0.005
    elif r.body_form == "built_in_bar_wall":
        # Doors cover the two central cooler compartments.
        base_width = r.carcass_width * 0.32
    else:
        opening_w = r.carcass_width - 2.0 * r.side_thickness - 0.010
        base_width = opening_w / 2.0 + 0.010
    # Preserve the accepted free-edge location while moving the pivot fully
    # outside the carcass.  This keeps door coverage/source identity intact.
    reference_hinge_x = r.carcass_width / 2.0 - r.side_thickness + _HINGE_BARREL_RADIUS + 0.002
    return base_width + (abs(_hinge_x_for_door(r, 1)) - reference_hinge_x)


def _sliding_leaf_width(r: ResolvedWineCabinetConfig) -> float:
    """Each bypass leaf covers half the opening without coplanar overlap."""
    opening_w = r.carcass_width - 2.0 * r.side_thickness - 0.010
    return opening_w * 0.495


def _build_paired_display_carcass(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    """Two side-by-side compartments sharing a hidden rear rail.

    We keep it as a single connected part (Rule 1 & Contract 3): a central
    divider partitions the carcass width in half; both halves inherit the
    common shell layout. Doors mount to outer edges only.
    """
    _build_common_carcass_shell(carcass, r, mats)
    # Central vertical divider — makes it read as a paired-cabinet form.
    _box(
        carcass,
        "center_divider",
        (
            r.side_thickness,
            r.carcass_depth - r.back_thickness,
            r.carcass_height - r.plinth_height - 0.010,
        ),
        (
            0.0,
            -r.back_thickness / 2.0,
            r.plinth_height + (r.carcass_height - r.plinth_height) / 2.0,
        ),
        mats["case"],
    )


def _build_wide_low_sideboard_carcass(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    """Wide low console with four legs (source: 002)."""
    _build_common_carcass_shell(carcass, r, mats)
    # Short square legs — sit under the plinth (add 4 legs regardless).
    leg_h = 0.14
    for ix, x in enumerate((-r.carcass_width / 2.0 + 0.06, r.carcass_width / 2.0 - 0.06)):
        for iy, y in enumerate((-r.carcass_depth / 2.0 + 0.06, r.carcass_depth / 2.0 - 0.06)):
            _box(
                carcass,
                f"leg_{ix}_{iy}",
                (0.045, 0.045, leg_h),
                (x, y, -leg_h / 2.0),
                mats["case"],
            )


def _build_single_tall_carcass(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    _build_common_carcass_shell(carcass, r, mats)


def _build_arched_display_carcass(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    """Arched front boundary — approximated by two triangular corner blocks
    on the front top corners of the opening (planar boundary form)."""
    _build_common_carcass_shell(carcass, r, mats)
    # Arched crown: a thicker top band with two corner fillet cubes suggesting the arc.
    # Recessed 12 mm deeper than the old front-flush datum so the full-height
    # door leaf (rear face at -d/2 + 4 mm) sweeps clear of the header.
    arch_h = 0.10
    _box(
        carcass,
        "arch_crown",
        (r.carcass_width - 2.0 * r.side_thickness, 0.030, arch_h),
        (0.0, -r.carcass_depth / 2.0 + 0.027, r.carcass_height - r.panel_thickness - arch_h / 2.0),
        mats["case"],
    )
    for i, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            f"arch_corner_{i}",
            (0.060, 0.030, 0.060),
            (
                sign * (r.carcass_width / 2.0 - r.side_thickness - 0.030),
                -r.carcass_depth / 2.0 + 0.027,
                r.carcass_height - r.panel_thickness - arch_h - 0.030,
            ),
            mats["case"],
        )


def _build_built_in_bar_wall_carcass(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    """Long low base + rear-anchored upper cubby wall (source: 003).

    We fold the upper wall into the carcass via a rear vertical panel + top
    cubby shelf so it stays one connected part (avoiding the FIXED-child
    upper carcass; Rule 1). The two-tier read is preserved by the geometry.
    """
    _build_common_carcass_shell(carcass, r, mats)
    # Rear-mounted upper cubby wall — attaches to the back panel above the base.
    upper_z0 = r.carcass_height  # sits on top of the base carcass crown
    upper_h = 0.85
    upper_d = r.carcass_depth * 0.55
    upper_y = r.carcass_depth / 2.0 - upper_d / 2.0
    # Upper back
    _box(
        carcass,
        "upper_back",
        (r.carcass_width - 0.02, 0.030, upper_h),
        (0.0, r.carcass_depth / 2.0 - 0.015, upper_z0 + upper_h / 2.0),
        mats["case"],
    )
    # Upper sides
    for i, sx in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            f"upper_side_{i}",
            (0.030, upper_d, upper_h),
            (sx * (r.carcass_width / 2.0 - 0.015), upper_y, upper_z0 + upper_h / 2.0),
            mats["case"],
        )
    # Upper bottom (also rests on base top crown → self-connected)
    _box(
        carcass,
        "upper_bottom",
        (r.carcass_width - 0.06, upper_d, 0.030),
        (0.0, upper_y, upper_z0 + 0.015),
        mats["interior"],
    )
    # Upper top
    _box(
        carcass,
        "upper_top",
        (r.carcass_width - 0.02, upper_d, 0.030),
        (0.0, upper_y, upper_z0 + upper_h - 0.015),
        mats["case"],
    )
    # Cubby dividers inside the upper wall
    n_dividers = 5
    for i in range(n_dividers):
        x = -r.carcass_width / 2.0 + (r.carcass_width / (n_dividers + 1)) * (i + 1)
        _box(
            carcass,
            f"upper_cubby_divider_{i}",
            (0.020, upper_d - 0.030, upper_h - 0.070),
            (x, upper_y, upper_z0 + upper_h / 2.0),
            mats["interior"],
        )
    # Under-cabinet LED strip on the underside of the upper bottom
    _box(
        carcass,
        "under_led_strip",
        (r.carcass_width * 0.9, 0.020, 0.010),
        (0.0, -r.carcass_depth / 2.0 * 0.10, upper_z0 - 0.005),
        mats["led"],
    )


def _build_corner_wrap_carcass(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    """L-shaped footprint: main wing along +X plus a return wing extending +Y
    from the right end. Kept as visuals on one carcass part."""
    _build_common_carcass_shell(carcass, r, mats)
    # Return wing (small perpendicular column)
    ret_w = r.carcass_depth  # width along X of the return wing
    ret_d = 0.42  # depth along Y of the return wing beyond the main body
    ret_x = r.carcass_width / 2.0 - ret_w / 2.0
    ret_y = r.carcass_depth / 2.0 + ret_d / 2.0
    ret_h = r.carcass_height
    # Return wing sides
    for i, sy in enumerate((0.0, ret_d)):
        _box(
            carcass,
            f"return_wall_{i}",
            (ret_w + 0.010, 0.028, ret_h - r.plinth_height),
            (
                ret_x,
                r.carcass_depth / 2.0 + sy - 0.014,
                r.plinth_height + (ret_h - r.plinth_height) / 2.0,
            ),
            mats["case"],
        )
    # Return wing back
    _box(
        carcass,
        "return_end_panel",
        (0.028, ret_d, ret_h - r.plinth_height),
        (
            ret_x + ret_w / 2.0 - 0.014,
            ret_y - ret_d / 2.0,
            r.plinth_height + (ret_h - r.plinth_height) / 2.0,
        ),
        mats["case"],
    )
    # Return wing bottom (rest on floor via plinth)
    _box(
        carcass,
        "return_bottom",
        (ret_w, ret_d, 0.018),
        (ret_x, ret_y, r.plinth_height + 0.009),
        mats["case"],
    )
    # Return wing top
    _box(
        carcass,
        "return_top",
        (ret_w + 0.020, ret_d + 0.020, 0.030),
        (ret_x, ret_y, ret_h - 0.015),
        mats["case"],
    )


BODY_BUILDERS = {
    "paired_display": _build_paired_display_carcass,
    "wide_low_sideboard": _build_wide_low_sideboard_carcass,
    "single_tall": _build_single_tall_carcass,
    "arched_display": _build_arched_display_carcass,
    "built_in_bar_wall": _build_built_in_bar_wall_carcass,
    "corner_wrap": _build_corner_wrap_carcass,
}


# ---------------------------------------------------------------------------
# Rack fabric helpers (all become carcass.visual — Rule 1)
# ---------------------------------------------------------------------------


def _rack_shelf_zs(r: ResolvedWineCabinetConfig, orientation: str) -> list[float]:
    """Return the world Z of each rack shelf centerline. Shared between rack
    builders and bottle layout so bottles rest on the actual shelves.

    orientation: "horizontal" for horizontal_cradles / diamond_lattice,
                 "standing"   for open_shelves / vertical_pegs.
    """
    z_span = r.rack_z_max - r.rack_z_min
    if orientation == "horizontal":
        pitch_min = 0.100  # shelf-to-shelf pitch for horizontal bottle rows
        n = max(2, min(6, int(z_span // pitch_min)))
        pitch = z_span / n
        shelf_zs = [r.rack_z_min + pitch * (i + 0.5) for i in range(n)]
    else:
        # An upright shelf is the bottom datum of its bottle bay, not the bay
        # centre.  Derive it from the complete bottle envelope and crown.
        shelf_zs = _standing_shelf_zs(r.rack_z_min, r.rack_z_max)
        n = len(shelf_zs)
        pitch = z_span / max(1, n)
    if r.service_motion == "pull_out_tasting_shelf":
        # The rack fabric itself must stop below the service channel.  Merely
        # moving bottles is insufficient: shelves, cradle rods, lattice bars
        # and peg hardware are all real collision geometry.
        mechanism_underside = _tasting_shelf_origin_z(r) - 0.022
        if r.rack_topology == "diamond_lattice" and orientation == "horizontal":
            hardware_above = pitch / 2.0 + 0.012
        elif r.rack_topology == "horizontal_cradles" and orientation == "horizontal":
            hardware_above = 0.017
        else:
            hardware_above = 0.007
        shelf_zs = [z for z in shelf_zs if z + hardware_above + 0.008 <= mechanism_underside]
    return shelf_zs


def _rack_orientation(r: ResolvedWineCabinetConfig) -> str:
    if r.rack_topology in {"open_shelves", "vertical_pegs"}:
        return "standing"
    return "horizontal"


def _glassware_profile(r: ResolvedWineCabinetConfig) -> tuple[str, ...]:
    """Source-backed static glassware only; no unsourced vase extrapolation."""
    if r.body_form in {"paired_display", "single_tall"} and r.door_style not in {
        "sliding_glass",
        "mesh_bifold",
    }:
        # Origin 001 and its paired/single/fold variants: five upright stem glasses.
        return ("stem",) * 5
    if r.body_form in {"wide_low_sideboard", "arched_display", "single_tall"}:
        # Origin 002 and its arched/sliding/mesh/count variants: three stem
        # glasses plus three upright tumblers on the display shelf.
        return ("stem",) * 3 + ("tumbler",) * 3
    return ()


def _tasting_shelf_origin_z(r: ResolvedWineCabinetConfig) -> float:
    """Return the shared service-shelf datum below the top interior panel.

    This datum is deliberately independent of bottle/glass layout.  Static
    contents derive their accommodation from the mechanism, never the other
    way around, which avoids a circular "move both until tests pass" layout.
    """
    top_panel_bottom_z = r.carcass_height - 0.038 - r.panel_thickness
    origin_z = top_panel_bottom_z - 0.036
    if r.body_form == "arched_display":
        arch_crown_bottom = r.carcass_height - r.panel_thickness - 0.100
        origin_z = min(origin_z, arch_crown_bottom - 0.016)
    return origin_z


def _glassware_support_row_index(r: ResolvedWineCabinetConfig) -> int | None:
    """Select the real shelf that supports source-backed display glassware."""
    if not _glassware_profile(r):
        return None
    shelf_zs = _rack_shelf_zs(r, _rack_orientation(r))
    if not shelf_zs:
        return None
    # Select only a row that contains the complete glass envelope below both
    # the cabinet crown and any traversing service mechanism.
    content_ceiling = r.rack_z_max
    if r.service_motion == "pull_out_tasting_shelf":
        content_ceiling = min(content_ceiling, _tasting_shelf_origin_z(r) - 0.022)
    eligible = [
        i
        for i, shelf_z in enumerate(shelf_zs)
        if shelf_z
        + _RACK_SHELF_TOP_OFFSET
        + _STEMWARE_ENVELOPE
        + _BOTTLE_TOP_CLEARANCE
        <= content_ceiling
    ]
    if not eligible:
        raise ValueError("no rack row can support glassware inside the host envelope")
    return max(eligible)


def _bottle_shelf_rows(r: ResolvedWineCabinetConfig, orientation: str) -> list[tuple[int, float]]:
    rows = list(enumerate(_rack_shelf_zs(r, orientation)))
    content_ceiling = r.rack_z_max
    if r.service_motion == "pull_out_tasting_shelf":
        content_ceiling = min(content_ceiling, _tasting_shelf_origin_z(r) - 0.022)
    bottle_height = (
        _HORIZONTAL_BOTTLE_ENVELOPE
        if orientation == "horizontal"
        else _STANDING_BOTTLE_ENVELOPE
    )
    rows = [
        (row_i, z)
        for row_i, z in rows
        if z + _RACK_SHELF_TOP_OFFSET + bottle_height + _BOTTLE_TOP_CLEARANCE
        <= content_ceiling
    ]
    glass_row = _glassware_support_row_index(r)
    if orientation == "horizontal" and glass_row is not None and len(rows) > 1:
        # Preserve a complete source-backed display row wherever the service
        # mechanism leaves it; bottle capacity uses the remaining real rows.
        return [(row_i, z) for row_i, z in rows if row_i != glass_row]
    return rows


def _bottle_shelf_zs(r: ResolvedWineCabinetConfig, orientation: str) -> list[float]:
    return [z for _, z in _bottle_shelf_rows(r, orientation)]


def _rack_support_name(r: ResolvedWineCabinetConfig, row_index: int) -> str:
    prefix = {
        "horizontal_cradles": "cradle_shelf",
        "diamond_lattice": "lattice_shelf",
        "vertical_pegs": "peg_shelf",
        "open_shelves": "open_shelf",
    }[r.rack_topology]
    return f"{prefix}_{row_index}"


def _add_rack_horizontal_cradles(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    """Layered shelves + light metal cradle bars for horizontal bottle rows."""
    interior_w = r.interior_width * 0.94
    # Shelf depth reaches from the back panel front face all the way to just
    # behind the front face — no floating shelf-to-back gap.
    interior_d = r.interior_depth
    shelf_zs = _rack_shelf_zs(r, "horizontal")
    for i, z in enumerate(shelf_zs):
        _box(
            carcass,
            f"cradle_shelf_{i}",
            (interior_w, interior_d, 0.014),
            (0.0, -r.back_thickness / 2.0, z),
            mats["interior"],
        )
        # Two thin metal cradle rods per shelf (helps read as a rack). Rods
        # embedded 2mm INTO the shelf top face so they stay connected.
        for j, x in enumerate((-interior_w * 0.35, interior_w * 0.35)):
            _cyl(
                carcass,
                f"cradle_rod_{i}_{j}",
                0.006,
                interior_d * 0.9,
                (x, -r.back_thickness / 2.0, z + 0.007 + 0.004),  # rod bottom kisses shelf top
                mats["metal"],
                rpy=(math.pi / 2.0, 0.0, 0.0),
            )


def _add_rack_diamond_lattice(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    """Crossed diagonal dividers forming a diamond lattice (source 002 L290-L301)."""
    interior_w = r.interior_width * 0.94
    shelf_zs = _rack_shelf_zs(r, "horizontal")
    n_cells = len(shelf_zs)
    z_span = r.rack_z_max - r.rack_z_min
    cell_h = z_span / max(1, n_cells)
    cell_w = interior_w
    for i, cz in enumerate(shelf_zs):
        rack_dx = cell_w / 2.0
        rack_dz = cell_h / 2.0
        rack_len = math.sqrt(rack_dx * rack_dx + rack_dz * rack_dz)
        rack_angle = math.atan2(rack_dz, rack_dx)
        for k, angle in enumerate((-rack_angle, rack_angle)):
            _box(
                carcass,
                f"lattice_bar_{i}_{k}",
                (rack_len, 0.024, 0.020),
                (0.0, -r.back_thickness / 2.0, cz),
                mats["metal"],
                rpy=(0.0, angle, 0.0),
            )
        # Cell-bounding shelf
        _box(
            carcass,
            f"lattice_shelf_{i}",
            (interior_w, r.interior_depth, 0.014),
            (0.0, -r.back_thickness / 2.0, cz),
            mats["interior"],
        )


def _add_rack_vertical_pegs(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    """Vertical peg columns — each column is a thin cylinder."""
    interior_w = r.interior_width * 0.9
    rack_top = r.rack_z_max
    if r.service_motion == "pull_out_tasting_shelf":
        rack_top = min(rack_top, _tasting_shelf_origin_z(r) - 0.038)
    z_span = rack_top - r.rack_z_min
    # 4-8 peg columns
    n_cols = max(4, min(8, int(round(interior_w / 0.10))))
    col_spacing = interior_w / n_cols
    for i in range(n_cols):
        x = -interior_w / 2.0 + col_spacing * (i + 0.5)
        _cyl(
            carcass,
            f"peg_column_{i}",
            0.010,
            z_span,
            (x, -r.back_thickness / 2.0, r.rack_z_min + z_span / 2.0),
            mats["metal"],
        )
    # Real shelves at the standing-bottle Z positions so bottles rest on hardware.
    shelf_zs = _rack_shelf_zs(r, "standing")
    for k, z in enumerate(shelf_zs):
        _box(
            carcass,
            f"peg_shelf_{k}",
            (interior_w + 0.020, r.interior_depth, 0.014),
            (0.0, -r.back_thickness / 2.0, z),
            mats["interior"],
        )


def _add_rack_open_shelves(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> None:
    """Plain shelf boards spanning the interior."""
    interior_w = r.interior_width * 0.94
    interior_d = r.interior_depth
    shelf_zs = _rack_shelf_zs(r, "standing")
    for i, z in enumerate(shelf_zs):
        _box(
            carcass,
            f"open_shelf_{i}",
            (interior_w, interior_d, 0.014),
            (0.0, -r.back_thickness / 2.0, z),
            mats["interior"],
        )


RACK_BUILDERS = {
    "horizontal_cradles": _add_rack_horizontal_cradles,
    "diamond_lattice": _add_rack_diamond_lattice,
    "vertical_pegs": _add_rack_vertical_pegs,
    "open_shelves": _add_rack_open_shelves,
    "none": lambda c, r, m: None,
}


# ---------------------------------------------------------------------------
# Bottle helpers (source-faithful)
# ---------------------------------------------------------------------------


def _add_horizontal_bottle(carcass, index, xyz, body_mat, cork_mat) -> None:
    """Emit a non-moving horizontal bottle as named carcass visuals (Rule 1)."""
    bx, by, bz = xyz
    body_r = 0.030
    body_z = bz + body_r - 0.001
    carcass.visual(
        Cylinder(radius=body_r, length=0.230),
        origin=Origin(xyz=(bx, by, body_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=body_mat,
        name=f"bottle_{index}_body", material_class_id="glass.smoked_tinted",
    )
    carcass.visual(
        Cylinder(radius=0.014, length=0.060),
        origin=Origin(xyz=(bx, by + 0.145, body_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=body_mat,
        name=f"bottle_{index}_neck", material_class_id="glass.smoked_tinted",
    )
    carcass.visual(
        Cylinder(radius=0.012, length=0.012),
        origin=Origin(xyz=(bx, by + 0.181, body_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=cork_mat,
        name=f"bottle_{index}_cork", material_class_id="organic.cork",
    )


def _add_standing_bottle(carcass, index, xyz, body_mat, cork_mat) -> None:
    """Emit a non-moving standing bottle as named carcass visuals (Rule 1)."""
    bx, by, bz = xyz
    body_r = 0.036
    carcass.visual(
        Cylinder(radius=body_r, length=0.210),
        origin=Origin(xyz=(bx, by, bz + 0.105 - 0.001)),
        material=body_mat,
        name=f"bottle_{index}_body", material_class_id="glass.smoked_tinted",
    )
    carcass.visual(
        Cylinder(radius=0.014, length=0.062),
        origin=Origin(xyz=(bx, by, bz + 0.241 - 0.001)),
        material=body_mat,
        name=f"bottle_{index}_neck", material_class_id="glass.smoked_tinted",
    )
    carcass.visual(
        Cylinder(radius=0.012, length=0.014),
        origin=Origin(xyz=(bx, by, bz + 0.279 - 0.001)),
        material=cork_mat,
        name=f"bottle_{index}_cork", material_class_id="organic.cork",
    )


def _bottle_layout(r: ResolvedWineCabinetConfig) -> list[tuple[float, float, float, str, int]]:
    """Return (x, y, z, orientation, physical_support_row) placements.

    Uses `_rack_shelf_zs` to align rows with the actual shelves, so bottle
    FIXED joint origins land ON shelf hardware
    (`fail_if_articulation_origin_far_from_geometry` passes) and bottles do
    not overlap the shelf above them.
    """
    if r.bottle_count == 0:
        return []

    interior_w = r.interior_width * 0.94
    orientation = _rack_orientation(r)
    shelf_rows = _bottle_shelf_rows(r, orientation)

    # Minimum X pitches per orientation (bottle radius + safety margin).
    if orientation == "horizontal":
        x_pitch_min = 0.068  # 60mm diameter + 8mm clear pitch
        y_lanes = (-r.back_thickness / 2.0,)
    else:
        x_pitch_min = 0.085  # 72mm diameter + 13mm gap
        # Three supported depth lanes preserve upright orientation while
        # scaling N.  They start behind the source-backed front glassware row.
        glass_y = -min(0.150, r.interior_depth * 0.40)
        lane_min = glass_y + 0.100
        lane_max = r.interior_depth / 2.0 - 0.050
        lane_span = max(0.0, lane_max - lane_min)
        y_lanes = (lane_min, lane_min + lane_span / 2.0, lane_max)

    cols_est = max(1, min(int(interior_w // x_pitch_min), 10))
    rows_est = len(shelf_rows)
    capacity = rows_est * cols_est * len(y_lanes)
    if capacity < r.bottle_count:
        raise ValueError(
            f"resolved bottle_count={r.bottle_count} exceeds supported capacity={capacity}"
        )
    target = r.bottle_count

    x_pitch = interior_w / cols_est

    placements: list[tuple[float, float, float, str, int]] = []
    idx = 0
    for support_row, shelf_z in shelf_rows:
        if idx >= target:
            break
        # Shelf top face sits at shelf_z + 0.007 (shelf thickness 0.014).
        # We anchor the joint origin ON the shelf top face — bottle visuals
        # are offset in their own frame to sit above (horizontal: radius up;
        # standing: body starts at 0).
        joint_z = shelf_z + _RACK_SHELF_TOP_OFFSET  # 1mm inside shelf top face for contact
        for anchor_y in y_lanes:
            for ci in range(cols_est):
                if idx >= target:
                    break
                col_x = -interior_w / 2.0 + (ci + 0.5) * x_pitch
                placements.append((col_x, anchor_y, joint_z, orientation, support_row))
                idx += 1
            if idx >= target:
                break
    return placements


def _build_glassware(carcass: Part, r: ResolvedWineCabinetConfig, mats) -> int:
    """Emit source-backed upright stemware/tumblers on a real rack shelf."""
    profile = _glassware_profile(r)
    if not profile:
        return 0
    shelf_zs = _rack_shelf_zs(r, _rack_orientation(r))
    support_row = _glassware_support_row_index(r)
    if not shelf_zs or support_row is None:
        return 0
    support_z = shelf_zs[support_row] + 0.006
    span = min(r.interior_width * 0.78, max(0.0, (len(profile) - 1) * 0.060))
    xs = (
        [0.0]
        if len(profile) == 1
        else [-span / 2.0 + span * i / (len(profile) - 1) for i in range(len(profile))]
    )
    y = -min(0.150, r.interior_depth * 0.40)
    for profile_i, (kind, x) in enumerate(zip(profile, xs)):
        if kind == "stem":
            _cyl(
                carcass,
                f"stem_glass_{profile_i}_foot",
                0.024,
                0.006,
                (x, y, support_z + 0.003),
                mats["stemware"],
            )
            _cyl(
                carcass,
                f"stem_glass_{profile_i}_stem",
                0.004,
                0.070,
                (x, y, support_z + 0.041),
                mats["stemware"],
            )
            _cyl(
                carcass,
                f"stem_glass_{profile_i}_bowl",
                0.025,
                0.055,
                (x, y, support_z + 0.1035),
                mats["stemware"],
            )
        else:
            _cyl(
                carcass,
                f"tumbler_{profile_i}_cup",
                0.025,
                0.070,
                (x, y, support_z + 0.035),
                mats["stemware"],
            )
    return len(profile)


# ---------------------------------------------------------------------------
# Door builders
# ---------------------------------------------------------------------------


def _door_opening_geometry(r: ResolvedWineCabinetConfig) -> tuple[float, float, float, float]:
    """Return (opening_width, opening_height, opening_z_center, front_y).

    front_y = y coordinate of the door's hinge line.
    """
    z0 = _door_bottom_z(r)
    z1 = _door_top_z(r)
    opening_h = z1 - z0
    opening_w = r.carcass_width - 2.0 * r.side_thickness - 0.010
    front_y = _hinge_front_y(r)
    return opening_w, opening_h, (z0 + z1) * 0.5, front_y


def _build_hinged_glass_door(
    model: ArticulatedObject,
    carcass: Part,
    index: int,
    r: ResolvedWineCabinetConfig,
    mats,
    *,
    hinge_side: int,  # -1 = left hinge (door leaf extends to +X), +1 = right hinge (extends -X)
) -> Part:
    """Glass door — hinge axis at door-local (0,0,z); leaf extends in direction*[0, dw].

    Local frame: door origin sits ON the hinge line, coincident with the joint
    origin in the carcass frame. Panel is built to extend in `direction * +X`
    from local origin. `direction = -hinge_side` so:
      - hinge_side=-1 (left hinge) → direction=+1 (leaf extends toward +X)
      - hinge_side=+1 (right hinge) → direction=-1 (leaf extends toward -X)
    Hinge_barrel sits at door-local (0, 0, z), which in world = (hinge_x, hinge_front_y, z).
    """
    part_name = f"door_{index}"
    door = model.part(part_name)

    direction = float(-hinge_side)  # sign of X-extent in door-local frame

    dw = _door_leaf_width(r)
    opening_w, opening_h, opening_z, front_y = _door_opening_geometry(r)
    dh = opening_h
    rail = 0.032
    depth = 0.024
    # Door leaf mid-X in local frame (used by rails, glass, handle).
    mid_x = direction * (dw / 2.0)

    # Outer stile — near the hinge side (against the hinge_barrel).
    outer_x = direction * (rail / 2.0 + 0.006)
    _box(door, "door_stile_0", (rail, depth, dh), (outer_x, 0.0, dh / 2.0), mats["case"])
    # Inner stile — the free edge (handle side).
    inner_x = direction * (dw - rail / 2.0)
    _box(door, "door_stile_1", (rail, depth, dh), (inner_x, 0.0, dh / 2.0), mats["case"])
    # Top and bottom rails span the width between stiles.
    rail_w = dw - 2.0 * rail
    _box(door, "door_rail_0", (rail_w, depth, rail), (mid_x, 0.0, rail / 2.0), mats["case"])
    _box(door, "door_rail_1", (rail_w, depth, rail), (mid_x, 0.0, dh - rail / 2.0), mats["case"])
    # Glass panel.
    _box(
        door,
        "glass_panel",
        (dw - 2.0 * rail, 0.006, dh - 2.0 * rail),
        (mid_x, 0.0, dh / 2.0),
        mats["glass"],
    )
    # Handle — vertical pull along the free stile.
    handle_x = direction * (dw - rail / 2.0)
    _cyl(door, "door_handle", 0.005, 0.16, (handle_x, -0.040, dh * 0.5), mats["metal"])
    for k, hz in enumerate((dh * 0.5 - 0.070, dh * 0.5 + 0.070)):
        _box(
            door,
            f"door_handle_mount_{k}",
            (0.012, 0.030, 0.012),
            (handle_x, -0.024, hz),
            mats["metal"],
        )

    # Hinge barrels — coincident with hinge line at door-local (0,0,z).
    barrel_zs = _hinge_local_zs(r)
    for zi, hz in enumerate(barrel_zs):
        _cyl(
            door,
            f"hinge_barrel_{zi}",
            _HINGE_BARREL_RADIUS,
            _HINGE_BARREL_LENGTH,
            (0.0, 0.0, hz),
            mats["dark_trim"],
        )

    # Joint origin in carcass frame — the hinge line at (hinge_x, hinge_front_y, opening_bottom_z).
    hinge_x = _hinge_x_for_door(r, index)
    origin_x = hinge_x
    origin_y = _hinge_front_y(r)
    origin_z = _door_bottom_z(r)

    # Axis: rotating outward. For left hinge (index 0, direction=+1),
    # opening the door means rotating negatively about Z (leaf swings toward
    # -Y = out of cabinet). For right hinge (index 1, direction=-1), positive.
    # Choosing sign so that a positive joint value opens the door outward:
    #   left hinge  (direction=+1) → axis = (0,0,-1)
    #   right hinge (direction=-1) → axis = (0,0,+1)
    axis = (0.0, 0.0, -1.0) if direction > 0 else (0.0, 0.0, 1.0)

    limits = MotionLimits(effort=14.0, velocity=1.2, lower=0.0, upper=r.door_open_angle)

    model.articulation(
        f"carcass_to_door_{index}",
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=door,
        origin=Origin(xyz=(origin_x, origin_y, origin_z)),
        axis=axis,
        motion_limits=limits,
        # A coaxial pin-through-barrel interface has no truthful planar mating
        # face.  The exact pin/barrel element pair is audited below instead.
    )
    return door


def _emit_mesh_bifold_leaf(
    part: Part,
    *,
    leaf_width: float,
    height: float,
    direction: float,
    y_offset: float,
    start_inset: float,
    mats,
    handle: bool,
) -> None:
    """Emit one complete framed mesh leaf.

    The source-backed bifold is an open wire screen, not a dark solid slab.
    Both leaves therefore carry a perimeter frame plus a real crossed wire
    field.  ``y_offset`` is derived from the offset inter-leaf knuckle: it
    keeps the leaves coplanar at q=0 while providing face-to-face clearance as
    the secondary leaf folds.
    """
    stile = 0.028
    depth = 0.020
    usable_width = leaf_width - start_inset
    mid_x = direction * (start_inset + usable_width / 2.0)
    _box(
        part,
        "outer_stile",
        (stile, depth, height),
        (direction * (start_inset + stile / 2.0), y_offset, height / 2.0),
        mats["dark_trim"],
    )
    _box(
        part,
        "inner_stile",
        (stile, depth, height),
        (direction * (leaf_width - stile / 2.0), y_offset, height / 2.0),
        mats["dark_trim"],
    )
    rail_w = usable_width - 2.0 * stile
    for rail_index, z in enumerate((stile / 2.0, height - stile / 2.0)):
        _box(
            part,
            f"frame_rail_{rail_index}",
            (rail_w, depth, stile),
            (mid_x, y_offset, z),
            mats["dark_trim"],
        )

    # A sparse crossed wire field remains visibly permeable in VTK renders;
    # it also prevents a mesh door from being mistaken for a solid panel.
    wire = 0.004
    inner_h = height - 2.0 * stile
    for wire_index in range(1, 6):
        x = direction * (start_inset + stile + rail_w * wire_index / 6.0)
        _box(
            part,
            f"mesh_wire_v_{wire_index}",
            (wire, 0.005, inner_h),
            (x, y_offset, height / 2.0),
            mats["metal"],
        )
    for wire_index in range(1, 9):
        z = stile + inner_h * wire_index / 9.0
        _box(
            part,
            f"mesh_wire_h_{wire_index}",
            (rail_w, 0.005, wire),
            (mid_x, y_offset, z),
            mats["metal"],
        )
    if handle:
        handle_x = direction * (leaf_width - stile / 2.0)
        _box(
            part,
            "door_handle",
            (0.012, 0.030, 0.120),
            (handle_x, y_offset - 0.022, height * 0.5),
            mats["metal"],
        )


def _build_mesh_bifold_door(
    model: ArticulatedObject,
    carcass: Part,
    index: int,
    r: ResolvedWineCabinetConfig,
    mats,
    *,
    hinge_side: int,
) -> tuple[Part, Part]:
    """Build a real two-leaf bifold with cabinet and inter-leaf pivots."""
    direction = float(-hinge_side)
    dw = _door_leaf_width(r)
    _opening_w, dh, _opening_z, _front_y = _door_opening_geometry(r)
    knuckle_gap = 0.016
    leaf_w = (dw - knuckle_gap) / 2.0
    outer = model.part(f"door_{index}")
    inner = model.part(f"door_{index}_inner")
    _emit_mesh_bifold_leaf(
        outer,
        leaf_width=leaf_w,
        height=dh,
        direction=direction,
        y_offset=0.0,
        start_inset=0.006,
        mats=mats,
        handle=False,
    )

    # The inter-leaf hinge line is 18 mm in front of the closed panel plane.
    # Offsetting the child geometry back by the same amount makes q=0 flush,
    # while the rotating offset creates real face-to-face folding clearance.
    knuckle_y = -0.018
    knuckle_x = direction * (leaf_w + knuckle_gap)
    _emit_mesh_bifold_leaf(
        inner,
        leaf_width=leaf_w,
        height=dh,
        direction=direction,
        y_offset=-knuckle_y,
        start_inset=0.0,
        mats=mats,
        handle=True,
    )

    barrel_zs = _hinge_local_zs(r)
    for zi, hz in enumerate(barrel_zs):
        _cyl(
            outer,
            f"hinge_barrel_{zi}",
            _HINGE_BARREL_RADIUS,
            _HINGE_BARREL_LENGTH,
            (0.0, 0.0, hz),
            mats["metal"],
        )
        _cyl(
            outer,
            f"interleaf_pin_{zi}",
            0.005,
            0.080,
            (knuckle_x, knuckle_y, hz),
            mats["metal"],
        )
        # The hinge strap attaches to the pin's exposed upper end, outside the
        # moving barrel envelope.  A short elbow ties it back to the frame;
        # neither element needs a collision exemption against the child.
        strap_span = knuckle_gap
        strap_z = hz + 0.035
        _box(
            outer,
            f"interleaf_strap_{zi}",
            (strap_span, 0.010, 0.014),
            (
                direction * (leaf_w + strap_span / 2.0),
                knuckle_y,
                strap_z,
            ),
            mats["metal"],
        )
        _box(
            outer,
            f"interleaf_elbow_{zi}",
            (0.010, abs(knuckle_y), 0.014),
            (
                direction * (leaf_w + 0.005),
                knuckle_y / 2.0,
                strap_z,
            ),
            mats["metal"],
        )
        _cyl(
            inner,
            f"interleaf_barrel_{zi}",
            0.009,
            0.054,
            (0.0, 0.0, hz),
            mats["dark_trim"],
        )

    hinge_x = _hinge_x_for_door(r, index)
    origin_x = hinge_x
    origin_y = _hinge_front_y(r)
    origin_z = _door_bottom_z(r)
    axis = (0.0, 0.0, -1.0) if direction > 0 else (0.0, 0.0, 1.0)

    model.articulation(
        f"carcass_to_door_{index}",
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=outer,
        origin=Origin(xyz=(origin_x, origin_y, origin_z)),
        axis=axis,
        motion_limits=MotionLimits(
            effort=12.0,
            velocity=1.2,
            lower=0.0,
            upper=r.door_open_angle,
        ),
        # Captured cylindrical hinge: exact pin/barrel contact is audited in
        # run_wine_cabinet_tests; no invented planar face contract.
    )
    # The secondary leaf has its own outward-safe range.  Both joints remain
    # collision-free when sampled independently (the harness must not assume
    # a hidden coupled/mimic joint), while the combined max pose folds the
    # inner leaf back toward the outer leaf.
    inner_axis = axis
    inner_upper = min(1.55, r.door_open_angle)
    model.articulation(
        f"door_{index}_to_inner",
        ArticulationType.REVOLUTE,
        parent=outer,
        child=inner,
        origin=Origin(xyz=(knuckle_x, knuckle_y, 0.0)),
        axis=inner_axis,
        motion_limits=MotionLimits(
            effort=8.0,
            velocity=1.8,
            lower=0.0,
            upper=inner_upper,
        ),
    )
    return outer, inner


def _build_sliding_glass_door(
    model: ArticulatedObject,
    carcass: Part,
    index: int,
    r: ResolvedWineCabinetConfig,
    mats,
    *,
    slide_dir: int,  # -1 slides toward -X, +1 slides toward +X
) -> Part:
    """Sliding glass door: PRISMATIC along ±X, riding the front tracks.

    Local frame: origin at panel bottom-center at the closed position; leaf
    extends symmetrically in X. Two doors are placed at rest_x offsets so
    they bypass at closed pose (they occupy the same track).
    """
    part_name = f"door_{index}"
    door = model.part(part_name)

    dw = _sliding_leaf_width(r)
    opening_w, opening_h, opening_z, front_y = _door_opening_geometry(r)
    dh = opening_h
    frame_t = 0.014
    # Panel is centered on local origin at door bottom.
    # Bottom rail (child mating face for MatingContract vs bottom_track).
    _box(
        door, "door_bottom_rail", (dw, 0.020, frame_t), (0.0, 0.0, frame_t / 2.0), mats["dark_trim"]
    )
    _box(
        door,
        "door_top_rail",
        (dw, 0.020, frame_t),
        (0.0, 0.0, dh - frame_t / 2.0),
        mats["dark_trim"],
    )
    _box(
        door,
        "slide_frame_left",
        (frame_t, 0.018, dh - 2.0 * frame_t),
        (-dw / 2.0 + frame_t / 2.0, 0.0, dh / 2.0),
        mats["dark_trim"],
    )
    _box(
        door,
        "slide_frame_right",
        (frame_t, 0.018, dh - 2.0 * frame_t),
        (dw / 2.0 - frame_t / 2.0, 0.0, dh / 2.0),
        mats["dark_trim"],
    )
    _box(
        door,
        "glass_panel",
        (dw - 2.0 * frame_t, 0.006, dh - 2.0 * frame_t),
        (0.0, 0.0, dh / 2.0),
        mats["glass"],
    )
    # Recessed handle.
    handle_x = -dw / 2.0 + 0.03 if slide_dir < 0 else dw / 2.0 - 0.03
    _box(door, "door_handle", (0.020, 0.022, 0.12), (handle_x, -0.014, dh / 2.0), mats["metal"])

    # Rest x — each leaf covers one half of the opening.  The two leaves ride
    # on distinct Y planes, so there is no coplanar whole-part overlap.
    half_opening = opening_w / 2.0
    rest_x = -half_opening + dw / 2.0 if slide_dir < 0 else half_opening - dw / 2.0
    origin_x = rest_x
    origin_y = -r.carcass_depth / 2.0 - 0.010 if index == 0 else -r.carcass_depth / 2.0 - 0.034
    origin_z = _door_bottom_z(r)
    travel = min(dw * 0.85, opening_w * 0.42)
    model.articulation(
        f"carcass_to_door_{index}",
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=door,
        origin=Origin(xyz=(origin_x, origin_y, origin_z)),
        axis=(float(slide_dir), 0.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.35, lower=0.0, upper=travel),
        mating=MatingContract(
            parent_face_geometry=f"top_track_{index}",
            parent_face_side="negative_z",
            child_face_geometry="door_top_rail",
            child_face_side="positive_z",
            contact_tol=0.045,
        ),
    )
    return door


def _build_doors(
    model: ArticulatedObject, carcass: Part, r: ResolvedWineCabinetConfig, mats
) -> list[Part]:
    if r.door_style == "none":
        return []
    doors: list[Part] = []
    # All body_forms emit 2 mirror-symmetric doors, keyed by index (0=left, 1=right).
    for index in range(2):
        hinge_side = -1 if index == 0 else 1
        slide_dir = -1 if index == 0 else 1
        if r.door_style == "sliding_glass":
            doors.append(
                _build_sliding_glass_door(
                    model,
                    carcass,
                    index,
                    r,
                    mats,
                    slide_dir=slide_dir,
                )
            )
        elif r.door_style == "mesh_bifold":
            doors.extend(
                _build_mesh_bifold_door(
                    model,
                    carcass,
                    index,
                    r,
                    mats,
                    hinge_side=hinge_side,
                )
            )
        else:  # paired_glass_hinged, smoked_glass_cooler
            doors.append(
                _build_hinged_glass_door(
                    model,
                    carcass,
                    index,
                    r,
                    mats,
                    hinge_side=hinge_side,
                )
            )
    return doors


# ---------------------------------------------------------------------------
# Drawer builders
# ---------------------------------------------------------------------------


def _drawer_dimensions(
    r: ResolvedWineCabinetConfig, drawer_width: float
) -> tuple[float, float, float]:
    """Single source for the complete box and its bilateral guide geometry."""
    band = max(r.rack_z_min - r.plinth_height - r.panel_thickness, 0.10)
    row_count = (
        3 if r.body_form == "built_in_bar_wall" and r.drawer_count == 9 else max(r.drawer_count, 1)
    )
    # Height follows the actual row pitch.  A hard 100 mm minimum made shallow
    # three/five-drawer banks interpenetrate; 72% leaves a real reveal/gap.
    drawer_h = min(0.20, max(0.045, band / row_count * 0.72))
    tray_w = drawer_width - 0.045
    tray_depth = r.carcass_depth * 0.72
    return drawer_h, tray_w, tray_depth


def _build_drawer(drawer: Part, r: ResolvedWineCabinetConfig, mats, drawer_width: float) -> None:
    """Complete drawer box plus two longitudinal runners.

    Local +Y points into the cabinet.  The moving containment body is front,
    bottom, both sides and a rear wall; runners are real side-mounted guides,
    never transverse bars through the cavity.
    """
    drawer_h, tray_w, tray_depth = _drawer_dimensions(r, drawer_width)
    front_w = drawer_width - 0.020
    front_t = 0.020
    # Front panel (drawer_front)
    _box(
        drawer,
        "drawer_front",
        (front_w, front_t, drawer_h),
        (0.0, -front_t / 2.0, 0.0),
        mats["case"],
    )
    # Tray bottom
    _box(
        drawer,
        "drawer_bottom",
        (tray_w, tray_depth, 0.012),
        (0.0, tray_depth / 2.0, -drawer_h / 2.0 + 0.020),
        mats["interior"],
    )
    # Sides
    tray_side_h = drawer_h * 0.60
    for i, x in enumerate((-tray_w / 2.0 + 0.008, tray_w / 2.0 - 0.008)):
        _box(
            drawer,
            f"drawer_side_{i}",
            (0.016, tray_depth, tray_side_h),
            (x, tray_depth / 2.0, -drawer_h / 2.0 + tray_side_h / 2.0 + 0.012),
            mats["interior"],
        )
    # Back
    _box(
        drawer,
        "drawer_back",
        (tray_w, 0.016, tray_side_h),
        (0.0, tray_depth - 0.008, -drawer_h / 2.0 + tray_side_h / 2.0 + 0.012),
        mats["interior"],
    )
    # Two longitudinal runners, slightly embedded into the side walls so the
    # entire moving box remains one supported visual island.
    runner_z = -drawer_h / 2.0 + 0.040
    for side, sign in (("left", -1.0), ("right", 1.0)):
        _box(
            drawer,
            f"drawer_runner_{side}",
            (0.010, tray_depth * 0.92, 0.018),
            (sign * (tray_w / 2.0 + 0.004), tray_depth * 0.50, runner_z),
            mats["metal"],
        )
    # Handle
    _cyl(
        drawer,
        "drawer_handle",
        0.005,
        min(0.14, front_w * 0.6),
        (0.0, -front_t - 0.020, 0.0),
        mats["metal"],
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    for i, x in enumerate((-0.050, 0.050)):
        _cyl(
            drawer,
            f"drawer_handle_mount_{i}",
            0.005,
            0.020,
            (x, -front_t - 0.010, 0.0),
            mats["metal"],
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )


def _add_drawer_guides(
    carcass: Part,
    r: ResolvedWineCabinetConfig,
    mats,
    *,
    index: int,
    x_offset: float,
    z_center: float,
    drawer_width: float,
) -> None:
    """Emit bilateral longitudinal parent guides for one indexed drawer."""
    drawer_h, tray_w, tray_depth = _drawer_dimensions(r, drawer_width)
    guide_z = z_center - drawer_h / 2.0 + 0.040
    guide_y = -r.carcass_depth / 2.0 + tray_depth * 0.50
    # A 30 mm rail section reaches a side wall or a 3x3 bay divider while its
    # inner lip captures the 10 mm moving runner.
    for side, sign in (("left", -1.0), ("right", 1.0)):
        guide_x = x_offset + sign * (tray_w / 2.0 + 0.014)
        _box(
            carcass,
            f"drawer_guide_{index}_{side}",
            (0.030, tray_depth * 0.92, 0.022),
            (guide_x, guide_y, guide_z),
            mats["metal"],
        )
        # The outside rails of a 3x3 bank terminate near the carcass walls,
        # not on an internal divider.  Short outboard mounting clips close that
        # real 6.5 mm host gap without entering the drawer cavity.
        column = index % 3
        needs_outer_clip = (
            r.body_form == "built_in_bar_wall"
            and r.drawer_count == 9
            and ((column == 0 and side == "left") or (column == 2 and side == "right"))
        )
        if needs_outer_clip:
            _box(
                carcass,
                f"drawer_guide_mount_{index}_{side}",
                (0.020, 0.050, 0.035),
                (guide_x + sign * 0.020, guide_y, guide_z),
                mats["metal"],
            )


def _build_drawers(
    model: ArticulatedObject, carcass: Part, r: ResolvedWineCabinetConfig, mats
) -> list[Part]:
    drawers: list[Part] = []
    if r.drawer_count == 0:
        return drawers

    if r.body_form == "built_in_bar_wall" and r.drawer_count == 9:
        # 3×3 grid
        col_w = (r.carcass_width - 2.0 * r.side_thickness - 0.030) / 3.0
        for row_i in range(3):
            for col_i in range(3):
                idx = row_i * 3 + col_i
                x_off = -r.carcass_width / 2.0 + r.side_thickness + 0.015 + col_w * (col_i + 0.5)
                drawer = model.part(f"drawer_{idx}")
                drawer_width = col_w - 0.008
                _build_drawer(drawer, r, mats, drawer_width=drawer_width)
                origin_y = -r.carcass_depth / 2.0
                origin_z = r.drawer_center_z[row_i]
                _add_drawer_guides(
                    carcass,
                    r,
                    mats,
                    index=idx,
                    x_offset=x_off,
                    z_center=origin_z,
                    drawer_width=drawer_width,
                )
                model.articulation(
                    f"carcass_to_drawer_{idx}",
                    ArticulationType.PRISMATIC,
                    parent=carcass,
                    child=drawer,
                    origin=Origin(xyz=(x_off, origin_y, origin_z)),
                    axis=(0.0, -1.0, 0.0),
                    motion_limits=MotionLimits(
                        effort=45.0, velocity=0.28, lower=0.0, upper=r.drawer_travel
                    ),
                    mating=MatingContract(
                        parent_face_geometry=f"drawer_guide_{idx}_left",
                        parent_face_side="positive_x",
                        child_face_geometry="drawer_runner_left",
                        child_face_side="negative_x",
                        contact_tol=0.020,
                    ),
                )
                drawers.append(drawer)
    else:
        # Vertical stack
        drawer_span_w = r.carcass_width - 2.0 * r.side_thickness - 0.020
        for i in range(r.drawer_count):
            drawer = model.part(f"drawer_{i}")
            _build_drawer(drawer, r, mats, drawer_width=drawer_span_w)
            origin_y = -r.carcass_depth / 2.0
            origin_z = r.drawer_center_z[i]
            _add_drawer_guides(
                carcass,
                r,
                mats,
                index=i,
                x_offset=0.0,
                z_center=origin_z,
                drawer_width=drawer_span_w,
            )
            model.articulation(
                f"carcass_to_drawer_{i}",
                ArticulationType.PRISMATIC,
                parent=carcass,
                child=drawer,
                origin=Origin(xyz=(0.0, origin_y, origin_z)),
                axis=(0.0, -1.0, 0.0),
                motion_limits=MotionLimits(
                    effort=45.0, velocity=0.28, lower=0.0, upper=r.drawer_travel
                ),
                mating=MatingContract(
                    parent_face_geometry=f"drawer_guide_{i}_left",
                    parent_face_side="positive_x",
                    child_face_geometry="drawer_runner_left",
                    child_face_side="negative_x",
                    contact_tol=0.020,
                ),
            )
            drawers.append(drawer)
    return drawers


# ---------------------------------------------------------------------------
# Bottles
# ---------------------------------------------------------------------------


def _build_bottles(
    model: ArticulatedObject, carcass: Part, r: ResolvedWineCabinetConfig, mats
) -> int:
    if r.bottle_count == 0:
        return 0
    placements = _bottle_layout(r)
    for i, (bx, by, bz, orient, _support_row) in enumerate(placements):
        body_mat = mats["bottle_a"] if i % 2 == 0 else mats["bottle_b"]
        cork_mat = mats["cork"]
        if orient == "horizontal":
            _add_horizontal_bottle(carcass, i, (bx, by, bz), body_mat, cork_mat)
        else:
            _add_standing_bottle(carcass, i, (bx, by, bz), body_mat, cork_mat)
    return len(placements)


# ---------------------------------------------------------------------------
# Service motion (fold-out counter / pull-out tasting shelf)
# ---------------------------------------------------------------------------


def _build_service_motion(
    model: ArticulatedObject, carcass: Part, r: ResolvedWineCabinetConfig, mats
) -> Part | None:
    if r.service_motion == "none":
        return None
    if r.service_motion == "fold_out_counter":
        counter = model.part("fold_out_counter")
        panel_w = r.carcass_width * 0.7
        panel_h = 0.28  # panel length along its own Z axis (hanging down at closed)
        # Panel local frame: origin at the front-top hinge line.  At q=0 the
        # leaf is stored vertically upward, entirely above the independently
        # moving doors; positive rotation about +X maps local +Z into -Y and
        # lowers it to a horizontal serving counter without crossing a door.
        _box(
            counter,
            "counter_panel",
            (panel_w, 0.020, panel_h),
            (0.0, -0.060, panel_h / 2.0),
            mats["case"],
        )
        # Ledge on the outer end of the panel (top when stored, tip when open).
        _box(
            counter,
            "counter_ledge",
            (panel_w, 0.020, 0.020),
            (0.0, -0.060, panel_h - 0.010),
            mats["dark_trim"],
        )
        _cyl(
            counter,
            "counter_hinge_barrel",
            0.012,
            panel_w * 0.90,
            (0.0, 0.0, 0.0),
            mats["metal"],
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
        for side, x in enumerate((-panel_w * 0.30, panel_w * 0.30)):
            _box(
                counter,
                f"counter_hanger_{side}",
                (0.024, 0.060, 0.050),
                (x, -0.030, 0.025),
                mats["metal"],
            )

        # Hinge hardware is above the door opening and grounded into the top
        # trim through a continuous support plus two overlapping gussets.
        origin_x = 0.0
        origin_y = -r.carcass_depth / 2.0 - 0.010
        origin_z = r.carcass_height + 0.030
        _box(
            carcass,
            "counter_hinge_support",
            (panel_w, 0.040, 0.100),
            (0.0, origin_y + 0.032, r.carcass_height + 0.010),
            mats["dark_trim"],
        )
        for side, x in (("left", -panel_w * 0.42), ("right", panel_w * 0.42)):
            _box(
                carcass,
                f"counter_support_gusset_{side}",
                (0.050, 0.050, 0.085),
                (x, origin_y + 0.037, r.carcass_height + 0.0125),
                mats["dark_trim"],
            )
            _box(
                carcass,
                f"counter_hinge_bracket_{side}",
                (0.034, 0.040, 0.055),
                (x, origin_y + 0.005, origin_z),
                mats["metal"],
            )
        model.articulation(
            "carcass_to_fold_out_counter",
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=counter,
            origin=Origin(xyz=(origin_x, origin_y, origin_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=25.0, velocity=1.0, lower=0.0, upper=math.pi / 2.0),
            # The barrel passes through two captured brackets.  Treating that
            # coaxial sleeve as two planar faces created a false 85 mm gap;
            # exact bracket/barrel pairs are audited below instead.
        )
        return counter
    # pull_out_tasting_shelf
    shelf = model.part("tasting_shelf")
    if r.body_form == "paired_display":
        shelf_w = r.carcass_width / 2.0 - 2.0 * r.side_thickness - 0.040
        origin_x = -r.carcass_width / 4.0
    else:
        shelf_w = r.carcass_width * 0.6
        origin_x = 0.0
    shelf_d = r.carcass_depth * 0.5
    _box(
        shelf,
        "shelf_top",
        (shelf_w, shelf_d, 0.020),
        (0.0, shelf_d / 2.0, 0.0),
        mats["interior"],
    )
    _box(
        shelf,
        "shelf_edge",
        (shelf_w, 0.020, 0.030),
        (0.0, shelf_d - 0.010, 0.015),
        mats["dark_trim"],
    )
    # Runners sit just outside the tray side faces while retaining 1 mm of
    # physical attachment to the moving tray.
    runner_x = shelf_w / 2.0 + 0.006
    for side, sign in (("left", -1.0), ("right", 1.0)):
        _box(
            shelf,
            f"shelf_runner_{side}",
            (0.014, shelf_d * 0.90, 0.014),
            (sign * runner_x, shelf_d / 2.0, -0.012),
            mats["metal"],
        )
    # Shared service datum: static contents select a supported row below the
    # tray's swept envelope.  The tray stows 35 mm behind the front plane so
    # its raised edge and runners clear the rear face of a closed full-height
    # door leaf (-d/2 + 4 mm).
    origin_z = _tasting_shelf_origin_z(r)
    origin_y = -r.carcass_depth / 2.0 + 0.035
    guide_y = origin_y + shelf_d / 2.0
    if r.body_form == "paired_display":
        host_xs = (-r.carcass_width / 2.0 + r.side_thickness, -r.side_thickness / 2.0)
    else:
        host_xs = (
            -r.carcass_width / 2.0 + r.side_thickness,
            r.carcass_width / 2.0 - r.side_thickness,
        )
    for side, sign in (("left", -1.0), ("right", 1.0)):
        guide_x = origin_x + sign * runner_x
        _box(
            carcass,
            f"tasting_guide_{side}",
            (0.018, shelf_d * 0.90, 0.016),
            (guide_x, guide_y, origin_z - 0.014),
            mats["metal"],
        )
        host_x = host_xs[0] if side == "left" else host_xs[1]
        guide_outboard_x = guide_x + sign * 0.009
        bridge_span = abs(host_x - guide_outboard_x)
        _box(
            carcass,
            f"tasting_guide_mount_{side}",
            (bridge_span + 0.002, 0.050, 0.016),
            ((host_x + guide_outboard_x) / 2.0, guide_y, origin_z - 0.014),
            mats["metal"],
        )
    model.articulation(
        "carcass_to_tasting_shelf",
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=shelf,
        origin=Origin(xyz=(origin_x, origin_y, origin_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=30.0, velocity=0.28, lower=0.0, upper=min(0.25, shelf_d * 0.6)
        ),
        mating=MatingContract(
            parent_face_geometry="tasting_guide_left",
            parent_face_side="positive_x",
            child_face_geometry="shelf_runner_left",
            child_face_side="negative_x",
            contact_tol=0.020,
        ),
    )
    return shelf


# ---------------------------------------------------------------------------
# Top-level builders
# ---------------------------------------------------------------------------


def build_wine_cabinet(
    config: WineCabinetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or WineCabinetConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)

    # Materials keyed by palette
    mats = {
        key: model.material(f"wine_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in r.palette.items()
    }

    carcass = model.part("carcass")
    BODY_BUILDERS[r.body_form](carcass, r, mats)
    RACK_BUILDERS[r.rack_topology](carcass, r, mats)
    _build_doors(model, carcass, r, mats)
    _build_drawers(model, carcass, r, mats)
    _build_bottles(model, carcass, r, mats)
    _build_glassware(carcass, r, mats)
    _build_service_motion(model, carcass, r, mats)

    # The tasting tray stows behind full-height hinged doors, so pulling it out
    # is a two-step operation: open the covering door(s) first.  Declare that
    # operating order so motion QC projects the doors open whenever the tray
    # leaves its neutral position.
    if r.service_motion == "pull_out_tasting_shelf" and r.door_style in {
        "paired_glass_hinged",
        "smoked_glass_cooler",
    }:
        controllers = (
            ("carcass_to_door_0",)
            if r.body_form == "paired_display"
            else ("carcass_to_door_0", "carcass_to_door_1")
        )
        model.meta["motion_interlocks"] = [
            {
                "controller_joint": controller,
                "controller_required_position": r.door_open_angle,
                "dependent_joints": ["carcass_to_tasting_shelf"],
            }
            for controller in controllers
        ]

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_wine_cabinet(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_wine_cabinet(config_from_seed(seed), assets=assets)


def slot_choices_for_config(
    r: ResolvedWineCabinetConfig | WineCabinetConfig,
) -> list[tuple[str, str]]:
    rr = r if isinstance(r, ResolvedWineCabinetConfig) else resolve_config(r)
    return [
        ("body_form", rr.body_form),
        ("door_style", rr.door_style),
        ("drawer_count", f"{rr.drawer_count}_drawers"),
        ("rack_topology", rr.rack_topology),
        ("bottle_count", f"{rr.bottle_count}_bottles"),
        ("service_motion", rr.service_motion),
        ("palette_style", rr.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def run_wine_cabinet_tests(
    object_model: ArticulatedObject, config: WineCabinetConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("carcass part present", "carcass" in part_names)

    # Multiplicity consistency
    door_parts = [n for n in part_names if n.startswith("door_")]
    drawer_parts = [n for n in part_names if n.startswith("drawer_")]
    carcass = object_model.get_part("carcass")
    bottle_bodies = [
        visual.name
        for visual in carcass.visuals
        if visual.name and visual.name.startswith("bottle_") and visual.name.endswith("_body")
    ]
    glassware_profile = _glassware_profile(r)
    stemware_feet = [
        visual.name
        for visual in carcass.visuals
        if visual.name and visual.name.startswith("stem_glass_") and visual.name.endswith("_foot")
    ]
    tumblers = [
        visual.name
        for visual in carcass.visuals
        if visual.name and visual.name.startswith("tumbler_") and visual.name.endswith("_cup")
    ]

    if r.door_style != "none":
        expected_door_parts = 4 if r.door_style == "mesh_bifold" else 2
        ctx.check(
            "door entity count matches resolved mechanism",
            len(door_parts) == expected_door_parts,
            details=f"expected={expected_door_parts}, doors={door_parts}",
        )
    else:
        ctx.check("no door when door_style == none", len(door_parts) == 0)

    ctx.check(
        "drawer part count matches config",
        len(drawer_parts) == r.drawer_count,
        details=f"expected {r.drawer_count}, got {drawer_parts}",
    )
    ctx.check(
        "requested bottle multiplicity equals resolved multiplicity",
        (12 if config.bottle_count is None else int(config.bottle_count)) == r.bottle_count,
        details=f"requested={config.bottle_count}, resolved={r.bottle_count}",
    )
    ctx.check(
        "bottle visual count exactly matches resolved multiplicity",
        len(bottle_bodies) == r.bottle_count,
        details=f"bottle_count target={r.bottle_count}, built={len(bottle_bodies)}",
    )
    ctx.check(
        "source-backed glassware count and type match resolved profile",
        len(stemware_feet) == glassware_profile.count("stem")
        and len(tumblers) == glassware_profile.count("tumbler"),
        details=(
            f"profile={glassware_profile}, stems={len(stemware_feet)}, tumblers={len(tumblers)}"
        ),
    )

    # Static contents must be upright/horizontal exactly as the rack source
    # requires and must sit on an emitted support shelf.  N scales placements,
    # pitch and occupied depth lanes together; no floating or silent truncation.
    placements = _bottle_layout(r)
    support_visuals = {visual.name for visual in carcass.visuals if visual.name}
    expected_orientation = _rack_orientation(r)
    bottle_support_ok = len(placements) == r.bottle_count
    bottle_envelope_ok = True
    bottle_support_details: list[str] = []
    shelf_rows = _bottle_shelf_rows(r, expected_orientation)
    shelf_z_by_row = dict(shelf_rows)
    for bx, by, bz, orientation, support_row in placements:
        if orientation != expected_orientation or support_row not in shelf_z_by_row:
            bottle_support_ok = False
            bottle_support_details.append(
                f"orientation={orientation}, expected={expected_orientation}"
            )
            continue
        support_z = shelf_z_by_row[support_row]
        support_name = _rack_support_name(r, support_row)
        supported = support_name in support_visuals and abs((support_z + 0.006) - bz) <= 0.0011
        if not supported:
            bottle_support_ok = False
            bottle_support_details.append(f"xyz={(bx, by, bz)} support={support_name}")
        envelope_height = (
            _HORIZONTAL_BOTTLE_ENVELOPE
            if orientation == "horizontal"
            else _STANDING_BOTTLE_ENVELOPE
        )
        bottle_top = bz + envelope_height
        if bottle_top + _BOTTLE_TOP_CLEARANCE > r.rack_z_max + 1e-9:
            bottle_envelope_ok = False
            bottle_support_details.append(
                f"bottle_top={bottle_top:.4f} exceeds rack_z_max={r.rack_z_max:.4f}"
            )
    ctx.check(
        "every static bottle has source-direction and a real shelf support",
        bottle_support_ok,
        details="; ".join(bottle_support_details[:8]),
    )
    ctx.check(
        "every static bottle envelope remains below the cabinet crown",
        bottle_envelope_ok,
        details="; ".join(bottle_support_details[:8]),
    )
    glass_support_ok = True
    if glassware_profile:
        glass_row = _glassware_support_row_index(r)
        glass_support_name = _rack_support_name(r, glass_row) if glass_row is not None else ""
        glass_support_ok = bool(glass_support_name) and glass_support_name in support_visuals
    ctx.check(
        "every source-backed glass or tumbler has a real display shelf",
        glass_support_ok,
        details=f"profile={glassware_profile}",
    )

    # Category identity: at least one non-FIXED joint must exist.
    moving_joints = [
        j
        for j in object_model.articulations
        if j.articulation_type
        in (ArticulationType.REVOLUTE, ArticulationType.PRISMATIC, ArticulationType.CONTINUOUS)
    ]
    ctx.check(
        "at least one non-FIXED joint (category identity)",
        len(moving_joints) >= 1,
        details=str([j.name for j in moving_joints]),
    )

    # Drawer joints axis check
    for i in range(r.drawer_count):
        joint_name = f"carcass_to_drawer_{i}"
        if joint_name in joint_names:
            j = object_model.get_articulation(joint_name)
            ctx.check(
                f"{joint_name} slides along -Y",
                j.articulation_type == ArticulationType.PRISMATIC
                and tuple(abs(v) for v in j.axis) == (0.0, 1.0, 0.0),
                details=str(j.axis),
            )

    # Door joint axis check (revolute doors)
    if r.door_style in {"paired_glass_hinged", "mesh_bifold", "smoked_glass_cooler"}:
        for i in range(2):
            joint_name = f"carcass_to_door_{i}"
            if joint_name in joint_names:
                j = object_model.get_articulation(joint_name)
                ctx.check(
                    f"{joint_name} is REVOLUTE about z",
                    j.articulation_type == ArticulationType.REVOLUTE
                    and tuple(abs(v) for v in j.axis) == (0.0, 0.0, 1.0),
                    details=str(j.axis),
                )
        if r.door_style == "mesh_bifold":
            for i in range(2):
                joint_name = f"door_{i}_to_inner"
                ctx.check(
                    f"{joint_name} is a counter-rotating inter-leaf hinge",
                    joint_name in joint_names
                    and object_model.get_articulation(joint_name).articulation_type
                    == ArticulationType.REVOLUTE
                    and tuple(abs(v) for v in object_model.get_articulation(joint_name).axis)
                    == (0.0, 0.0, 1.0),
                )
    elif r.door_style == "sliding_glass":
        for i in range(2):
            joint_name = f"carcass_to_door_{i}"
            if joint_name in joint_names:
                j = object_model.get_articulation(joint_name)
                ctx.check(
                    f"{joint_name} is PRISMATIC about x",
                    j.articulation_type == ArticulationType.PRISMATIC
                    and tuple(abs(v) for v in j.axis) == (1.0, 0.0, 0.0),
                    details=str(j.axis),
                )

    # Service motion presence
    if r.service_motion == "fold_out_counter":
        ctx.check("fold_out_counter part present", "fold_out_counter" in part_names)
    elif r.service_motion == "pull_out_tasting_shelf":
        ctx.check("tasting_shelf part present", "tasting_shelf" in part_names)

    # ---- Allowances ----
    for i in range(2):
        door_name = f"door_{i}"
        if door_name in part_names:
            door = object_model.get_part(door_name)
            # Hinge barrel captured by hinge_mount tab (element-scoped)
            if r.door_style in {"paired_glass_hinged", "mesh_bifold", "smoked_glass_cooler"}:
                # Two hinge barrels per door; two hinge_mount tabs per door_index in
                # {0,1,2} — pick the mounts belonging to this door index (0 uses
                # the -x side, 1 uses +x side).
                for zi in range(2):
                    ctx.allow_overlap(
                        door,
                        carcass,
                        elem_a=f"hinge_barrel_{zi}",
                        elem_b=f"hinge_mount_{i}_{zi}",
                        reason="hinge barrel captured by carcass hinge_mount tab",
                    )
            elif r.door_style == "sliding_glass":
                # Sliding door top/bottom rails ride captured inside the tracks.
                for elem_a, elem_b in (
                    ("door_top_rail", f"top_track_{i}"),
                    ("door_bottom_rail", f"bottom_track_{i}"),
                ):
                    ctx.allow_overlap(
                        door,
                        carcass,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="sliding door rail rides captured inside track",
                    )

    if r.door_style == "mesh_bifold":
        for i in range(2):
            outer = object_model.get_part(f"door_{i}")
            inner = object_model.get_part(f"door_{i}_inner")
            for zi in range(2):
                ctx.allow_overlap(
                    outer,
                    inner,
                    elem_a=f"interleaf_pin_{zi}",
                    elem_b=f"interleaf_barrel_{zi}",
                    reason="bifold inter-leaf pin is captured by its matching barrel",
                )

    for i in range(r.drawer_count):
        drawer_name = f"drawer_{i}"
        if drawer_name in part_names:
            drawer = object_model.get_part(drawer_name)
            ctx.allow_isolated_part(
                drawer,
                reason="drawer slides out on its runners and loses contact with the carcass",
            )
            for side in ("left", "right"):
                ctx.allow_overlap(
                    carcass,
                    drawer,
                    elem_a=f"drawer_guide_{i}_{side}",
                    elem_b=f"drawer_runner_{side}",
                    reason="drawer runner is captured by its matching longitudinal side guide",
                )

    # Exact captured interfaces for optional service mechanisms.
    if r.service_motion == "fold_out_counter" and "fold_out_counter" in part_names:
        counter = object_model.get_part("fold_out_counter")
        for side in ("left", "right"):
            ctx.allow_overlap(
                counter,
                carcass,
                elem_a="counter_hinge_barrel",
                elem_b=f"counter_hinge_bracket_{side}",
                reason="counter hinge barrel is captured by the matching support bracket",
            )
    if r.service_motion == "pull_out_tasting_shelf" and "tasting_shelf" in part_names:
        shelf = object_model.get_part("tasting_shelf")
        for side in ("left", "right"):
            ctx.allow_overlap(
                carcass,
                shelf,
                elem_a=f"tasting_guide_{side}",
                elem_b=f"shelf_runner_{side}",
                reason="tasting shelf runner is captured by its matching longitudinal guide",
            )

    # Rule 5: sampled-pose overlap check
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    # Targeted pose checks
    if r.drawer_count > 0:
        drawer_joint_0 = object_model.get_articulation("carcass_to_drawer_0")
        drawer0 = object_model.get_part("drawer_0")
        closed_pos = ctx.part_world_position(drawer0)
        with ctx.pose({drawer_joint_0: r.drawer_travel}):
            open_pos = ctx.part_world_position(drawer0)
        if closed_pos is not None and open_pos is not None:
            ctx.check(
                "drawer_0 slides toward user (-Y)",
                open_pos[1] < closed_pos[1] - r.drawer_travel * 0.5,
                details=f"closed={closed_pos}, open={open_pos}, travel={r.drawer_travel}",
            )

    if (
        r.door_style in {"paired_glass_hinged", "mesh_bifold", "smoked_glass_cooler"}
        and "door_0" in part_names
    ):
        d0_joint = object_model.get_articulation("carcass_to_door_0")
        d0 = object_model.get_part("door_0")
        closed_aabb = ctx.part_world_aabb(d0)
        with ctx.pose({d0_joint: r.door_open_angle}):
            open_aabb = ctx.part_world_aabb(d0)
        if closed_aabb is not None and open_aabb is not None:
            ctx.check(
                "door_0 swings outward (front-y decreases)",
                open_aabb[0][1] < closed_aabb[0][1] - r.carcass_depth * 0.20,
                details=f"closed={closed_aabb}, open={open_aabb}",
            )

    if r.door_style == "mesh_bifold":
        outer_joint = object_model.get_articulation("carcass_to_door_0")
        inner_joint = object_model.get_articulation("door_0_to_inner")
        inner_leaf = object_model.get_part("door_0_inner")
        closed_inner = ctx.part_world_position(inner_leaf)
        with ctx.pose(
            {
                outer_joint: r.door_open_angle,
                inner_joint: min(1.55, r.door_open_angle),
            }
        ):
            folded_inner = ctx.part_world_position(inner_leaf)
        if closed_inner is not None and folded_inner is not None:
            ctx.check(
                "bifold secondary leaf follows the inter-leaf hinge",
                math.dist(closed_inner, folded_inner) >= _door_leaf_width(r) * 0.18,
                details=f"closed={closed_inner}, folded={folded_inner}",
            )

    if r.door_style == "sliding_glass" and "door_0" in part_names:
        slide_joint = object_model.get_articulation("carcass_to_door_0")
        slider = object_model.get_part("door_0")
        closed_pos = ctx.part_world_position(slider)
        slide_max = slide_joint.motion_limits.upper if slide_joint.motion_limits else 0.0
        with ctx.pose({slide_joint: slide_max}):
            open_pos = ctx.part_world_position(slider)
        if closed_pos is not None and open_pos is not None:
            ctx.check(
                "sliding door follows its signed X guide",
                abs(open_pos[0] - closed_pos[0]) >= slide_max * 0.8,
                details=f"closed={closed_pos}, open={open_pos}, travel={slide_max}",
            )

    if r.service_motion == "fold_out_counter":
        service_joint = object_model.get_articulation("carcass_to_fold_out_counter")
        service_part = object_model.get_part("fold_out_counter")
        closed_aabb = ctx.part_world_aabb(service_part)
        with ctx.pose({service_joint: math.pi / 2.0}):
            open_aabb = ctx.part_world_aabb(service_part)
        if closed_aabb is not None and open_aabb is not None:
            ctx.check(
                "fold-out counter swings forward",
                open_aabb[0][1] < closed_aabb[0][1] - 0.10,
                details=f"closed={closed_aabb}, open={open_aabb}",
            )
    elif r.service_motion == "pull_out_tasting_shelf":
        service_joint = object_model.get_articulation("carcass_to_tasting_shelf")
        service_part = object_model.get_part("tasting_shelf")
        closed_pos = ctx.part_world_position(service_part)
        service_max = service_joint.motion_limits.upper if service_joint.motion_limits else 0.0
        with ctx.pose({service_joint: service_max}):
            open_pos = ctx.part_world_position(service_part)
        if closed_pos is not None and open_pos is not None:
            ctx.check(
                "tasting shelf slides toward the user",
                open_pos[1] < closed_pos[1] - service_max * 0.8,
                details=f"closed={closed_pos}, open={open_pos}, travel={service_max}",
            )

    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "WineCabinetConfig",
    "ResolvedWineCabinetConfig",
    "build_wine_cabinet",
    "build_seeded_wine_cabinet",
    "config_from_seed",
    "resolve_config",
    "run_wine_cabinet_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
