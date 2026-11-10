# SPDX-License-Identifier: Apache-2.0

"""Wine cabinet2 — modular procedural template.

Category identity: upright storage-grade wine cabinet with a real cabinetry
carcass (sides + back + top/base + toe-kick or plinth), at least one non-fixed
operable front (glass / paneled / cooler door, and/or PRISMATIC drawers), and
one or more display zones (glass-shelf bay, X/diamond bottle rack, or open
horizontal bar rack) holding wine bottles as FIXED contents. See
`articraft_template_authoring/specs_modular_v1/wine_cabinet2.md`.

Structure (pattern = ``parallel_children``): a single root ``cabinet`` part
holds the entire carcass as inlined visuals (Rule 1). Doors, drawers, and
FIXED bottle/glass/serving decor attach as parallel children.

Slots (procedural, deterministic per seed; seed=0 is not special):

  * ``body_form`` (4): contemporary_bookcase / freestanding_hutch /
    modular_light_wood / built_in_wall — a ③ Primary Form Family slot.
  * ``door_mechanism`` (6): four REVOLUTE swing families plus bypass sliding
    glass and captured pocket glass mechanisms.
  * ``rack_topology`` (5): glass shelves / diamond lattice / horizontal bars /
    backed vertical pegs / source-matched hybrid display-rack-cooler bundle —
    controls bottle type, layout, support, and honest capacity.
  * ``drawer_bank`` (2 modules, but multiplicity N ∈ {0,2,3,4}).
  * ``palette_style`` (6): warm_oak / walnut_reddish / pale_ash / brown_hutch /
    painted_white / walnut_stain — drives EVERY material in the build.
  * Multiplicity axes: ``door_count`` [1..4], ``drawer_count`` [0..4],
    ``bottle_count`` [6..20].  Every procedural seed samples N within its
    resolved body×rack capacity; only the accepted modular hybrid reaches 20.

Swing doors go through ``hinged_panel(open_toward=(0,1,0), ...)``; sliding
doors, complete drawers, and the optional tasting shelf use real PRISMATIC
articulations with bilateral guides.  Captured swing hinges use coaxial barrel
and socket elements; their exact element pair is the only collision exemption.
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
    Cylinder,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    hinged_panel,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value literals + canonical tuples.
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "contemporary_bookcase",
    "freestanding_hutch",
    "modular_light_wood",
    "built_in_wall",
]
DoorMechanism = Literal[
    "swing_glass",
    "swing_divided_glass",
    "swing_paneled",
    "swing_cooler",
    "sliding_glass",
    "pocket_glass",
]
RackTopology = Literal[
    "glass_shelf_bay",
    "diamond_lattice",
    "horizontal_bar_rack",
    "vertical_peg_rack",
    "hybrid_display_rack",
]
ServiceMotion = Literal["none", "pull_out_tasting_shelf"]
PaletteStyle = Literal[
    "warm_oak",
    "walnut_reddish",
    "pale_ash",
    "brown_hutch",
    "painted_white",
    "walnut_stain",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "contemporary_bookcase",
    "freestanding_hutch",
    "modular_light_wood",
    "built_in_wall",
)
DOOR_MECHANISMS: tuple[DoorMechanism, ...] = (
    "swing_glass",
    "swing_divided_glass",
    "swing_paneled",
    "swing_cooler",
    "sliding_glass",
    "pocket_glass",
)
RACK_TOPOLOGIES: tuple[RackTopology, ...] = (
    "glass_shelf_bay",
    "diamond_lattice",
    "horizontal_bar_rack",
    "vertical_peg_rack",
    "hybrid_display_rack",
)
SERVICE_MOTIONS: tuple[ServiceMotion, ...] = ("none", "pull_out_tasting_shelf")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "warm_oak",
    "walnut_reddish",
    "pale_ash",
    "brown_hutch",
    "painted_white",
    "walnut_stain",
)

# ---------------------------------------------------------------------------
# Palettes — each covers ≥3 material buckets (wood, glass, metal, ceramic, etc.).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_oak": {
        "wood": (0.70, 0.55, 0.36, 1.0),
        "dark_wood": (0.48, 0.34, 0.20, 1.0),
        "edge_wood": (0.60, 0.44, 0.28, 1.0),
        "back": (0.42, 0.34, 0.22, 1.0),
        "metal": (0.16, 0.16, 0.17, 1.0),
        "glass": (0.60, 0.75, 0.78, 0.28),
        "ceramic": (0.86, 0.80, 0.70, 1.0),
        "bottle_a": (0.09, 0.24, 0.14, 0.94),
        "bottle_b": (0.36, 0.14, 0.06, 0.94),
        "cork": (0.62, 0.42, 0.24, 1.0),
        "warm_light": (0.98, 0.72, 0.32, 1.0),
    },
    "walnut_reddish": {
        "wood": (0.44, 0.17, 0.075, 1.0),
        "dark_wood": (0.26, 0.09, 0.05, 1.0),
        "edge_wood": (0.55, 0.24, 0.11, 1.0),
        "back": (0.20, 0.09, 0.05, 1.0),
        "metal": (0.55, 0.36, 0.12, 1.0),
        "glass": (0.55, 0.72, 0.75, 0.28),
        "ceramic": (0.90, 0.86, 0.76, 1.0),
        "bottle_a": (0.06, 0.16, 0.09, 0.94),
        "bottle_b": (0.22, 0.04, 0.05, 0.95),
        "cork": (0.62, 0.39, 0.18, 1.0),
        "warm_light": (0.98, 0.70, 0.30, 1.0),
    },
    "pale_ash": {
        "wood": (0.76, 0.64, 0.48, 1.0),
        "dark_wood": (0.36, 0.27, 0.18, 1.0),
        "edge_wood": (0.86, 0.76, 0.60, 1.0),
        "back": (0.20, 0.16, 0.12, 1.0),
        "metal": (0.58, 0.60, 0.60, 1.0),
        "glass": (0.70, 0.88, 0.92, 0.28),
        "ceramic": (0.92, 0.90, 0.83, 1.0),
        "bottle_a": (0.08, 0.24, 0.12, 0.94),
        "bottle_b": (0.34, 0.12, 0.045, 0.95),
        "cork": (0.70, 0.48, 0.25, 1.0),
        "warm_light": (0.98, 0.86, 0.55, 1.0),
    },
    "brown_hutch": {
        "wood": (0.36, 0.16, 0.065, 1.0),
        "dark_wood": (0.20, 0.075, 0.025, 1.0),
        "edge_wood": (0.27, 0.11, 0.035, 1.0),
        "back": (0.14, 0.06, 0.03, 1.0),
        "metal": (0.18, 0.14, 0.10, 1.0),
        "glass": (0.62, 0.82, 0.86, 0.28),
        "ceramic": (0.91, 0.89, 0.80, 1.0),
        "bottle_a": (0.055, 0.17, 0.085, 0.92),
        "bottle_b": (0.34, 0.13, 0.025, 0.95),
        "cork": (0.62, 0.40, 0.22, 1.0),
        "warm_light": (0.99, 0.75, 0.35, 1.0),
    },
    "painted_white": {
        "wood": (0.94, 0.92, 0.87, 1.0),
        "dark_wood": (0.62, 0.60, 0.56, 1.0),
        "edge_wood": (0.82, 0.80, 0.75, 1.0),
        "back": (0.68, 0.68, 0.66, 1.0),
        "metal": (0.28, 0.30, 0.32, 1.0),
        "glass": (0.72, 0.88, 0.94, 0.30),
        "ceramic": (0.95, 0.93, 0.86, 1.0),
        "bottle_a": (0.08, 0.24, 0.12, 0.94),
        "bottle_b": (0.30, 0.10, 0.05, 0.94),
        "cork": (0.62, 0.42, 0.24, 1.0),
        "warm_light": (0.98, 0.90, 0.72, 1.0),
    },
    "walnut_stain": {
        "wood": (0.34, 0.22, 0.14, 1.0),
        "dark_wood": (0.20, 0.13, 0.08, 1.0),
        "edge_wood": (0.42, 0.28, 0.17, 1.0),
        "back": (0.14, 0.09, 0.05, 1.0),
        "metal": (0.68, 0.70, 0.72, 1.0),
        "glass": (0.62, 0.80, 0.84, 0.28),
        "ceramic": (0.86, 0.80, 0.70, 1.0),
        "bottle_a": (0.08, 0.22, 0.11, 0.94),
        "bottle_b": (0.34, 0.11, 0.045, 0.95),
        "cork": (0.62, 0.39, 0.18, 1.0),
        "warm_light": (0.98, 0.70, 0.32, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base carcass dimensions per body_form (in meters). Scales in Config multiply
# these; then clamps apply. All origins are cabinet-local: X = long axis
# (width), Y = depth (front is +Y), Z = height (base at z=0).
# ---------------------------------------------------------------------------
_BODY_BASE = {
    "contemporary_bookcase": {"W": 2.00, "D": 0.40, "H": 2.00, "shelf_z": 0.53},
    "freestanding_hutch": {"W": 0.88, "D": 0.43, "H": 1.79, "shelf_z": 0.40},
    "modular_light_wood": {"W": 1.42, "D": 0.42, "H": 1.82, "shelf_z": 0.69},
    "built_in_wall": {"W": 1.52, "D": 0.56, "H": 2.35, "shelf_z": 0.68},
}

_DOOR_UPPER_BASE = {
    "swing_glass": 1.45,
    "swing_divided_glass": 1.72,
    "swing_paneled": 1.72,
    "swing_cooler": 1.75,
}

# Multiplicity sampling weights (spec §8).
DOOR_COUNT_CANDIDATES = (1, 2, 3, 4)
DOOR_COUNT_WEIGHTS = (0.16, 0.42, 0.28, 0.14)
DRAWER_COUNT_CANDIDATES = (0, 2, 3, 4)
DRAWER_COUNT_WEIGHTS = (0.30, 0.20, 0.28, 0.22)

# Bottle count band edges.
BOTTLE_COUNT_MIN = 6
BOTTLE_COUNT_MAX = 20

# Rack capacity by admitted (body_form, rack_topology).  This table is the
# single source of truth used by the resolver, slot reporting, emitters, and
# tests.  Do not put fictional capacity on a topology whose support geometry
# has fewer seats: N is a count of complete, supported bottles, not a request
# that the emitter may silently truncate.
_RACK_CAPACITY: dict[tuple[BodyForm, RackTopology], int] = {
    ("contemporary_bookcase", "glass_shelf_bay"): 12,
    ("freestanding_hutch", "glass_shelf_bay"): 8,
    ("freestanding_hutch", "horizontal_bar_rack"): 12,
    ("modular_light_wood", "glass_shelf_bay"): 10,
    ("modular_light_wood", "diamond_lattice"): 20,
    ("modular_light_wood", "vertical_peg_rack"): 12,
    # The accepted N=20 source is a modular host with one coordinated support
    # bundle: four upright display positions, nine diamond cells, and seven
    # cooler-shelf positions.  This is the only admitted N=20 rack family.
    ("modular_light_wood", "hybrid_display_rack"): 20,
    ("built_in_wall", "glass_shelf_bay"): 12,
    ("built_in_wall", "diamond_lattice"): 20,
    ("built_in_wall", "vertical_peg_rack"): 12,
}


# ---------------------------------------------------------------------------
# Config dataclasses.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WineCabinet2Config:
    body_form: BodyForm = "contemporary_bookcase"
    door_mechanism: DoorMechanism = "swing_glass"
    rack_topology: RackTopology = "glass_shelf_bay"
    service_motion: ServiceMotion = "none"
    palette_style: PaletteStyle = "warm_oak"
    door_count: int = 2
    drawer_count: int = 0
    bottle_count: int = 8
    cabinet_width_scale: float = 1.0
    cabinet_height_scale: float = 1.0
    cabinet_depth_scale: float = 1.0
    door_open_scale: float = 1.0
    drawer_travel_scale: float = 1.0
    name: str = "wine_cabinet2"


@dataclass(frozen=True)
class ResolvedWineCabinet2Config:
    body_form: BodyForm
    door_mechanism: DoorMechanism
    rack_topology: RackTopology
    service_motion: ServiceMotion
    palette_style: PaletteStyle
    door_count: int
    drawer_count: int
    requested_bottle_count: int
    bottle_count: int
    rack_capacity: int
    # Dimensions.
    W: float
    D: float
    H: float
    plinth_h: float
    shelf_z: float  # top face of the drawer/lower band and start of upper display
    side_t: float
    back_t: float
    panel_t: float
    # Door band.
    door_bottom: float
    door_height: float
    door_width: float  # per-door width of the front opening reserved for doors
    door_open: float
    # Drawer band.
    drawer_band_top: float
    drawer_band_bot: float
    drawer_travel: float
    drawer_box_depth: float
    drawer_box_height: float
    tasting_shelf_travel: float
    # Rack region.
    rack_z_min: float
    rack_z_max: float
    rack_x_min: float
    rack_x_max: float
    name: str


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------
def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _weighted_choice(rng: random.Random, choices, weights):
    return rng.choices(choices, weights=weights, k=1)[0]


def _apply_gating(
    body_form: BodyForm,
    door_mechanism: DoorMechanism,
    rack_topology: RackTopology,
    service_motion: ServiceMotion,
    door_count: int,
    drawer_count: int,
    bottle_count: int,
) -> tuple[DoorMechanism, RackTopology, ServiceMotion, int, int, int, int]:
    """Resolve compatibility gating from spec §9. Rewrites illegal combos."""
    # Paneled leaves in the accepted redo-002 source are *lower cupboard
    # doors*, not a generic full-height facade.  Reusing that leaf on another
    # carcass caused it to cover the display/rack bay and produced cabinets
    # that no longer resembled any accepted source.  Keep the complete
    # paneled-front bundle on its built-in host; other bodies use their own
    # source-backed glass facade.
    if door_mechanism == "swing_paneled" and body_form != "built_in_wall":
        door_mechanism = (
            "swing_divided_glass" if body_form == "freestanding_hutch" else "swing_glass"
        )
    if door_mechanism == "swing_paneled" and body_form == "built_in_wall":
        # Redo-002 and the reviewed N variants establish a three/four-leaf
        # lower bank.  One/two oversized paneled leaves are not in the source
        # vocabulary and collapse the built-in wall into a tall wardrobe.
        door_count = max(3, door_count)
    # (1) horizontal_bar_rack lives on freestanding_hutch's bar layout only.
    if rack_topology == "horizontal_bar_rack" and body_form != "freestanding_hutch":
        rack_topology = "glass_shelf_bay"
    # (2) diamond_lattice needs a wide body_form.
    if rack_topology == "diamond_lattice" and body_form not in {
        "modular_light_wood",
        "built_in_wall",
    }:
        rack_topology = "glass_shelf_bay"
    # The accepted pegboard/vertical-peg anchor is the modular light-wood
    # carcass.  Built-in wall bays expose the same deep backed interface; the
    # narrow hutch and open bookcase do not.
    if rack_topology == "vertical_peg_rack" and body_form not in {
        "modular_light_wood",
        "built_in_wall",
    }:
        rack_topology = "glass_shelf_bay"
    # N=20 is anchored by one coordinated modular display/rack/cooler bundle;
    # it is not a free rack insert for the other three carcasses.
    if rack_topology == "hybrid_display_rack" and body_form != "modular_light_wood":
        rack_topology = "glass_shelf_bay"
    # (3) swing_cooler is a single wide door.
    if door_mechanism == "swing_cooler":
        door_count = 1
    if door_mechanism in {"sliding_glass", "pocket_glass"}:
        door_count = 2
    # Pocket leaves require a real side well at least as wide as the admitted
    # travel.  Only the wide carcasses have that envelope.
    if door_mechanism == "pocket_glass" and body_form not in {
        "contemporary_bookcase",
        "modular_light_wood",
        "built_in_wall",
    }:
        door_mechanism = "sliding_glass"
    # (4) narrow hutch supports at most 2 doors.
    if body_form == "freestanding_hutch":
        door_count = min(door_count, 2)
    # (4b) The accepted 3/4-door anchors are paneled lower-bank installations.
    # Other leaf families remain at one or two doors until their narrower
    # multi-leaf interfaces receive their own compatibility probe.
    if door_count >= 3 and not (
        door_mechanism == "swing_paneled"
        and body_form == "built_in_wall"
    ):
        door_count = 2
    # (6) drawers require a body_form with a drawer band.
    if body_form in {"freestanding_hutch", "modular_light_wood"}:
        drawer_count = 0
    # A pocket door well and a drawer bank compete for the same side framing.
    if door_mechanism == "pocket_glass":
        drawer_count = 0
    # The tasting shelf anchor belongs to the modular light-wood service bay.
    # It replaces the lower open shelf, so it is mutually exclusive with a
    # drawer bank and with the unprobed pocket-door front.
    if service_motion == "pull_out_tasting_shelf":
        if body_form != "modular_light_wood" or door_mechanism == "pocket_glass":
            service_motion = "none"
        else:
            drawer_count = 0
    # The source-matched hybrid uses the lower band for its seven cooler-shelf
    # positions, so a tasting shelf cannot occupy that same volume.
    if rack_topology == "hybrid_display_rack":
        service_motion = "none"
    # (7) bottle_count clamp by rack capacity.
    cap = _RACK_CAPACITY[(body_form, rack_topology)]
    bottle_count = max(BOTTLE_COUNT_MIN, min(bottle_count, cap))
    return (
        door_mechanism,
        rack_topology,
        service_motion,
        door_count,
        drawer_count,
        bottle_count,
        cap,
    )


def config_from_seed(seed: int) -> WineCabinet2Config:
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    door_mechanism = rng.choice(DOOR_MECHANISMS)
    rack_topology = rng.choice(RACK_TOPOLOGIES)
    service_motion = rng.choice(SERVICE_MOTIONS)
    door_count = _weighted_choice(rng, DOOR_COUNT_CANDIDATES, DOOR_COUNT_WEIGHTS)
    drawer_count = _weighted_choice(rng, DRAWER_COUNT_CANDIDATES, DRAWER_COUNT_WEIGHTS)
    # Sample N from the *resolved* body×rack capacity.  Direct configs above a
    # rack's capacity are still projected safely by resolve_config, but normal
    # procedural seeds never hide a requested N behind a smaller emitted N.
    (
        _resolved_door,
        resolved_rack,
        _resolved_service,
        _resolved_door_count,
        _resolved_drawer_count,
        _resolved_bottle_count,
        rack_capacity,
    ) = _apply_gating(
        body_form,
        door_mechanism,
        rack_topology,
        service_motion,
        door_count,
        drawer_count,
        BOTTLE_COUNT_MIN,
    )
    del _resolved_door, _resolved_service, _resolved_door_count, _resolved_drawer_count
    del _resolved_bottle_count, resolved_rack
    bottle_count = rng.randint(BOTTLE_COUNT_MIN, rack_capacity)
    palette_style = rng.choice(PALETTE_STYLES)
    return WineCabinet2Config(
        body_form=body_form,
        door_mechanism=door_mechanism,
        rack_topology=rack_topology,
        service_motion=service_motion,
        palette_style=palette_style,
        door_count=door_count,
        drawer_count=drawer_count,
        bottle_count=bottle_count,
        cabinet_width_scale=round(rng.uniform(0.90, 1.12), 3),
        cabinet_height_scale=round(rng.uniform(0.90, 1.12), 3),
        cabinet_depth_scale=round(rng.uniform(0.92, 1.10), 3),
        door_open_scale=round(rng.uniform(0.88, 1.05), 3),
        drawer_travel_scale=round(rng.uniform(0.85, 1.05), 3),
        name=f"seeded_wine_cabinet2_{seed}",
    )


def resolve_config(config: WineCabinet2Config | None = None) -> ResolvedWineCabinet2Config:
    cfg = config or WineCabinet2Config()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    door_mechanism = _pick(cfg.door_mechanism, DOOR_MECHANISMS)
    rack_topology = _pick(cfg.rack_topology, RACK_TOPOLOGIES)
    service_motion = _pick(cfg.service_motion, SERVICE_MOTIONS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    door_count = int(_clamp(cfg.door_count, 1, 4))
    drawer_count = int(cfg.drawer_count)
    if drawer_count not in (0, 2, 3, 4):
        drawer_count = 0
    requested_bottle_count = int(
        _clamp(cfg.bottle_count, BOTTLE_COUNT_MIN, BOTTLE_COUNT_MAX)
    )
    bottle_count = requested_bottle_count

    (
        door_mechanism,
        rack_topology,
        service_motion,
        door_count,
        drawer_count,
        bottle_count,
        rack_capacity,
    ) = _apply_gating(
        body_form,
        door_mechanism,
        rack_topology,
        service_motion,
        door_count,
        drawer_count,
        bottle_count,
    )

    ws = _clamp(cfg.cabinet_width_scale, 0.88, 1.15)
    hs = _clamp(cfg.cabinet_height_scale, 0.88, 1.15)
    ds = _clamp(cfg.cabinet_depth_scale, 0.90, 1.12)
    do_scale = _clamp(cfg.door_open_scale, 0.85, 1.05)
    dt_scale = _clamp(cfg.drawer_travel_scale, 0.80, 1.05)

    base = _BODY_BASE[body_form]
    W = base["W"] * ws
    D = base["D"] * ds
    H = base["H"] * hs
    shelf_z = base["shelf_z"] * hs  # top of drawer band / bottom of upper display

    side_t = 0.030
    back_t = 0.018
    panel_t = 0.024
    plinth_h = 0.06

    # Facade zoning is a FormFamily consumer, not an independent placement.
    # The built-in paneled anchor has lower cupboard doors, a shallow drawer
    # band immediately above them, and the diamond/display rack above both.
    # All other anchors keep their source layout of lower drawer/service band
    # with the glazed display-door band above it.
    paneled_lower_bank = body_form == "built_in_wall" and door_mechanism == "swing_paneled"
    if paneled_lower_bank:
        door_bottom = 0.18 * hs
        door_height = 0.49 * hs
        drawer_band_bot = door_bottom + door_height + 0.025 * hs
        drawer_band_top = 0.88 * hs
        rack_z_min = 0.95 * hs
    else:
        drawer_band_bot = plinth_h + 0.02
        drawer_band_top = shelf_z
        door_bottom = drawer_band_top + 0.02
        rack_z_min = door_bottom

    # Rack region: upper display bay.
    rack_z_max = H - panel_t - 0.02
    rack_x_min = -W / 2.0 + side_t + 0.02
    rack_x_max = W / 2.0 - side_t - 0.02

    door_height_max = rack_z_max - door_bottom - 0.02
    if not paneled_lower_bank:
        door_height = max(0.35, min(door_height_max, base["H"] * 0.55))
    else:
        door_height = min(door_height, drawer_band_bot - door_bottom - 0.012)

    # Per-door width: split the front opening among door_count. The hinge sits at
    # the outer edge of each band with a 3cm inset for the jamb; leaf extends
    # inward and must stop 5mm before the band's inner edge so neighbouring doors
    # don't collide at closed pose.
    door_zone_w = W - 2.0 * side_t - 0.02
    per_door_w = door_zone_w / door_count
    if door_mechanism == "pocket_glass":
        # The central clear opening is 48% of the inner width; each leaf is a
        # little wider than half that opening, while each side pocket remains
        # wider than the leaf's admitted travel.
        central_opening_w = door_zone_w * 0.48
        door_width = central_opening_w / 2.0 - 0.006
        pocket_w = (door_zone_w - central_opening_w) / 2.0
        door_open = min(door_width * 0.88, pocket_w - 0.018)
    elif door_mechanism == "sliding_glass":
        door_width = door_zone_w * 0.52
        door_open = min(door_zone_w * 0.25, door_width * 0.82)
    else:
        door_width = max(
            0.24, min(per_door_w - 0.035, 0.90 if door_mechanism == "swing_cooler" else 0.60)
        )
        door_open = _clamp(_DOOR_UPPER_BASE[door_mechanism] * do_scale, 0.9, 1.9)
    # With multiple doors sharing a front, their arcs overlap; cap open angle so
    # each leaf's arc stays within its per-door band width.
    if door_mechanism.startswith("swing_") and door_count >= 2 and door_width > 0.05:
        # Leaf tip at angle θ has y-swing = door_width * sin(θ). To keep leaves
        # from clipping the neighbor band (width = per_door_w), require
        # door_width * sin(θ) <= per_door_w - reveal.
        per_door_w = door_zone_w / door_count
        reveal = 0.03
        max_reach = max(per_door_w - reveal, 0.02)
        if door_width > 0:
            ratio = min(1.0, max_reach / door_width)
            max_safe = math.asin(ratio) if ratio < 1.0 else math.pi / 2.0
            door_open = min(door_open, max_safe * 0.85)
        if door_count >= 3:
            # Interior leaves share sweep boundaries at neighboring mullions;
            # the accepted three/four-door probes are clean through 0.80 rad.
            door_open = min(door_open, 0.80)

    # Drawer geometry.
    drawer_box_depth = min(D - back_t - 0.06, D * 0.72)
    drawer_box_h_max = 0.14
    drawer_box_height = min(
        drawer_box_h_max,
        max(0.08, (drawer_band_top - drawer_band_bot - 0.02) / max(1, drawer_count) * 0.7)
        if drawer_count > 0
        else 0.10,
    )
    drawer_travel = min(_clamp(0.24 * dt_scale, 0.14, 0.32), drawer_box_depth * 0.68)
    tasting_shelf_travel = min(0.30 * dt_scale, max(0.18, D * 0.72))

    return ResolvedWineCabinet2Config(
        body_form=body_form,
        door_mechanism=door_mechanism,
        rack_topology=rack_topology,
        service_motion=service_motion,
        palette_style=palette_style,
        door_count=door_count,
        drawer_count=drawer_count,
        requested_bottle_count=requested_bottle_count,
        bottle_count=bottle_count,
        rack_capacity=rack_capacity,
        W=W,
        D=D,
        H=H,
        plinth_h=plinth_h,
        shelf_z=shelf_z,
        side_t=side_t,
        back_t=back_t,
        panel_t=panel_t,
        door_bottom=door_bottom,
        door_height=door_height,
        door_width=door_width,
        door_open=door_open,
        drawer_band_top=drawer_band_top,
        drawer_band_bot=drawer_band_bot,
        drawer_travel=drawer_travel,
        drawer_box_depth=drawer_box_depth,
        drawer_box_height=drawer_box_height,
        tasting_shelf_travel=tasting_shelf_travel,
        rack_z_min=rack_z_min,
        rack_z_max=rack_z_max,
        rack_x_min=rack_x_min,
        rack_x_max=rack_x_max,
        name=cfg.name or "wine_cabinet2",
    )


def with_overrides(config: WineCabinet2Config, **kwargs: object) -> WineCabinet2Config:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: WineCabinet2Config | ResolvedWineCabinet2Config,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedWineCabinet2Config) else resolve_config(config)
    # Encode multiplicity axes with `n{K}` per §C axis_realization visibility.
    return (
        ("body_form", r.body_form),
        ("door_mechanism", r.door_mechanism),
        ("rack_topology", r.rack_topology),
        ("service_motion", r.service_motion),
        ("drawer_bank", "none" if r.drawer_count == 0 else f"drawer_bank_n{r.drawer_count}"),
        ("palette_style", r.palette_style),
        ("door_count", f"n{r.door_count}"),
        ("drawer_count", f"n{r.drawer_count}"),
        (
            "facade_zoning",
            (
                "lower_paneled_drawer_upper_rack"
                if r.body_form == "built_in_wall" and r.door_mechanism == "swing_paneled"
                else "lower_service_upper_display"
            ),
        ),
        ("bottle_count_requested", f"n{r.requested_bottle_count}"),
        ("bottle_count", f"n{r.bottle_count}"),
        ("rack_capacity", f"n{r.rack_capacity}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared cadquery meshes (built once per build; reused across N).
# ---------------------------------------------------------------------------
def _wine_glass_shape() -> cq.Workplane:
    foot = cq.Workplane("XY").circle(0.023).extrude(0.003)
    stem = cq.Workplane("XY").workplane(offset=0.002).circle(0.0035).extrude(0.062)
    outer = (
        cq.Workplane("XY")
        .workplane(offset=0.060)
        .circle(0.017)
        .workplane(offset=0.050)
        .circle(0.032)
        .loft(combine=True)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=0.066)
        .circle(0.013)
        .workplane(offset=0.046)
        .circle(0.028)
        .loft(combine=True)
    )
    return foot.union(stem).union(outer.cut(inner))


def _serving_bowl_shape() -> cq.Workplane:
    base = cq.Workplane("XY").circle(0.042).extrude(0.010)
    foot = cq.Workplane("XY").circle(0.020).extrude(0.028)
    outer = cq.Workplane("XY").circle(0.086).extrude(0.062).translate((0.0, 0.0, 0.028))
    inner = cq.Workplane("XY").circle(0.078).extrude(0.060).translate((0.0, 0.0, 0.036))
    return base.union(foot).union(outer.cut(inner))


# ---------------------------------------------------------------------------
# Carcass builders (Slot A modules). Each fills `cabinet.visual(...)` and
# returns a small dict of carcass anchor faces:
#   ``door_jamb_x[i]``  — X of the hinge line for door i (front face)
#   ``drawer_sill_x[i]`` — X center of drawer i on the drawer band
#   ``rack_shelf_zs``   — list of z heights of glass shelves (glass_shelf_bay)
#   ``rack_bar_rows``   — list of z heights of horizontal bar rows
#   ``diamond_cells``   — list of (cx, cz, cell_w, cell_h) cells
# ---------------------------------------------------------------------------
def _cbox(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)):
    part.visual(
        Box(size),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="wood.veneer_panel",
    )


def _ccyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)):
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.brushed_silver",
    )


def _emit_common_carcass_shell(cabinet, r: ResolvedWineCabinet2Config, mats):
    """Continuous load-bearing shell: back, sides, top, base, plinth, toe-kick."""
    # Base plinth.
    _cbox(
        cabinet,
        (r.W, r.D, r.plinth_h),
        (0.0, 0.0, r.plinth_h / 2.0),
        mats["edge_wood"],
        "base_plinth",
    )
    # Sides.
    side_z0 = r.plinth_h
    side_h = r.H - r.plinth_h - r.panel_t
    for idx, xs in enumerate((-r.W / 2.0 + r.side_t / 2.0, r.W / 2.0 - r.side_t / 2.0)):
        _cbox(
            cabinet,
            (r.side_t, r.D, side_h),
            (xs, 0.0, side_z0 + side_h / 2.0),
            mats["wood"],
            f"side_panel_{idx}",
        )
    # Top panel.
    _cbox(
        cabinet,
        (r.W, r.D, r.panel_t),
        (0.0, 0.0, r.H - r.panel_t / 2.0),
        mats["wood"],
        "top_panel",
    )
    # Back panel.
    _cbox(
        cabinet,
        (r.W - 2.0 * r.side_t, r.back_t, r.H - r.plinth_h - r.panel_t),
        (0.0, -r.D / 2.0 + r.back_t / 2.0, side_z0 + side_h / 2.0),
        mats["back"],
        "back_panel",
    )
    # Toe-kick (dark strip).
    _cbox(
        cabinet,
        (r.W - 0.06, 0.03, 0.05),
        (0.0, -r.D / 2.0 + 0.05, 0.05),
        mats["dark_wood"],
        "toe_kick",
    )
    # Crown molding (host-conformal ④).
    _cbox(
        cabinet,
        (r.W - 0.02, r.D - 0.02, 0.012),
        (0.0, 0.0, r.H - r.panel_t - 0.006),
        mats["edge_wood"],
        "crown_molding",
    )


def _emit_drawer_band(cabinet, r: ResolvedWineCabinet2Config, mats) -> list[float]:
    """Emit real drawer bays with bilateral longitudinal guides.

    The old template placed one wide transverse ``drawer_sill`` through every
    cavity.  It made the drawer appear supported only by penetrating its box.
    Each bay now has a small rear-of-front stop plus left/right longitudinal
    rails outside the moving drawer sides.  The rails remain engaged in
    projection through max travel without occupying the containment cavity.
    """
    if r.drawer_count == 0:
        return []
    band_h = r.drawer_band_top - r.drawer_band_bot
    # Full drawer_band width extends BEYOND side_t so it embeds into side_panels.
    band_w = r.W - r.side_t
    zone_w = r.W - 2.0 * r.side_t - 0.02
    per_w = zone_w / r.drawer_count
    xs = [(-zone_w / 2.0) + (i + 0.5) * per_w for i in range(r.drawer_count)]
    ft = 0.024
    front_plane = r.D / 2.0
    # Deck at bottom, extending to the side panels via band_w > zone_w.  Its
    # front edge stops behind the drawer facade; a shelf penetrating the
    # closed front is not a support interface.
    band_depth = r.D - r.back_t - 0.06
    band_y = -r.D / 2.0 + r.back_t + band_depth / 2.0
    band_front_y = band_y + band_depth / 2.0
    _cbox(
        cabinet,
        (band_w, band_depth, 0.020),
        (0.0, band_y, r.drawer_band_bot + 0.010),
        mats["dark_wood"],
        "drawer_deck",
    )
    # Top rail closing the band above.
    _cbox(
        cabinet,
        (band_w, band_depth, 0.020),
        (0.0, band_y, r.drawer_band_top - 0.010),
        mats["wood"],
        "drawer_band_top_rail",
    )
    drawer_width = max(0.10, per_w - 0.026)
    drawer_z = r.drawer_band_bot + band_h / 2.0
    front_h = min(0.20, max(0.10, band_h - 0.03))
    box_h = min(front_h * 0.82, r.drawer_box_height)
    guide_len = max(0.12, r.drawer_box_depth - 0.045)
    guide_y = front_plane - ft - guide_len / 2.0 - 0.006
    guide_z = drawer_z - box_h / 2.0 + 0.010
    divider_depth = r.D - r.back_t - 0.035
    divider_y = -r.D / 2.0 + r.back_t + divider_depth / 2.0
    for boundary in range(r.drawer_count + 1):
        boundary_x = -zone_w / 2.0 + boundary * per_w
        _cbox(
            cabinet,
            (0.012, divider_depth, band_h - 0.040),
            (boundary_x, divider_y, r.drawer_band_bot + band_h / 2.0),
            mats["wood"],
            f"drawer_bay_wall_{boundary}",
        )
    for i, x in enumerate(xs):
        # A real closed-position stop contacts only the top rear strip of the
        # drawer front.  It does not cross the drawer cavity.
        _cbox(
            cabinet,
            (min(0.12, drawer_width * 0.34), 0.014, 0.024),
            (x, front_plane - ft - 0.007, drawer_z + front_h / 2.0 - 0.012),
            mats["wood"],
            f"drawer_stop_{i}",
        )
        side_x = (drawer_width - 0.030) / 2.0
        for side, sign in enumerate((-1.0, 1.0)):
            rail_x = x + sign * (side_x + 0.012)
            _cbox(
                cabinet,
                (0.010, guide_len, 0.014),
                (rail_x, guide_y, guide_z),
                mats["metal"],
                f"drawer_rail_{i}_{side}",
            )
            boundary_x = x + sign * per_w / 2.0
            bracket_w = abs(boundary_x - rail_x) + 0.012
            for bracket_index, by in enumerate(
                (guide_y - guide_len * 0.32, guide_y + guide_len * 0.32)
            ):
                _cbox(
                    cabinet,
                    (bracket_w, 0.024, 0.044),
                    ((boundary_x + rail_x) / 2.0, by, guide_z - 0.029),
                    mats["metal"],
                    f"drawer_rail_bracket_{i}_{side}_{bracket_index}",
                )
        stop_top = drawer_z + front_h / 2.0
        top_rail_bottom = r.drawer_band_top - 0.020
        stop_bracket_h = max(0.020, top_rail_bottom - stop_top + 0.006)
        stop_y = front_plane - ft - 0.007
        # Narrow longitudinal cantilever: joins the front stop to the recessed
        # top rail without crossing the drawer width or its containment cavity.
        stop_bracket_depth = abs(stop_y - band_front_y) + 0.012
        _cbox(
            cabinet,
            (0.024, stop_bracket_depth, stop_bracket_h),
            (
                x,
                0.5 * (stop_y + band_front_y),
                stop_top + stop_bracket_h / 2.0 - 0.003,
            ),
            mats["wood"],
            f"drawer_stop_bracket_{i}",
        )
    return xs


def _hinge_hardware_dimensions(h: float) -> tuple[float, float, float, float]:
    """Scale a three-piece butt hinge so two stations remain disjoint."""
    barrel_len = min(0.060, max(0.038, h * 0.090))
    socket_len = min(0.044, max(0.028, h * 0.070))
    socket_offset = (barrel_len + socket_len) / 2.0
    axle_len = barrel_len + 2.0 * socket_len
    return barrel_len, socket_len, socket_offset, axle_len


def _emit_door_jambs(cabinet, r: ResolvedWineCabinet2Config, mats) -> list[tuple[float, float]]:
    """Emit captured hinge jambs. Returns ``[(hinge_x, sign)]``.

    The rear spine connects every jamb to the carcass while the front jamb is
    segmented around two real hinge sockets.  This creates the rotational
    clearance a barrel needs instead of hiding barrel/jamb penetration behind
    a whole-part overlap allowance.
    """
    zone_w = r.W - 2.0 * r.side_t - 0.02
    per_w = zone_w / r.door_count
    door_top = min(r.rack_z_max, r.door_bottom + r.door_height)
    # Emit the horizontal head rail BEFORE the jambs so jamb bottoms embed into
    # its top surface (guarantees a real contact edge, not a 1µm gap). Extend
    # 8mm into each side panel so the rail welds to the carcass side panels.
    _cbox(
        cabinet,
        (r.W - 2.0 * r.side_t + 0.016, r.panel_t, 0.028),
        (0.0, r.D / 2.0 - r.panel_t / 2.0, r.door_bottom - 0.010),
        mats["wood"],
        "door_head_rail_lower",
    )
    jambs: list[tuple[float, float]] = []
    for i in range(r.door_count):
        # Alternating hinge sign so paired doors mirror. Door local +X points away
        # from the hinge, so the hinge belongs at the band's OUTER edge and the
        # leaf sweeps toward the band's center.
        sign = 1.0 if i % 2 == 0 else -1.0
        band_center_x = -zone_w / 2.0 + (i + 0.5) * per_w
        # For sign=+1 (leaf goes +X): hinge at band_center - per_w/2 + margin (left edge).
        # For sign=-1 (leaf goes -X): hinge at band_center + per_w/2 - margin (right edge).
        hinge_x = band_center_x - sign * (per_w / 2.0 - 0.03)
        # Clamp so the jamb never overlaps the carcass side panel.
        max_abs_x = r.W / 2.0 - r.side_t - 0.024
        hinge_x = max(-max_abs_x, min(max_abs_x, hinge_x))
        jambs.append((hinge_x, sign))
        # Jamb rear spine stays behind the rotating leaf and connects the two
        # socket stations to the head rail and cabinet frame.
        jamb_bot = r.door_bottom - 0.008
        jamb_h = door_top - jamb_bot
        _cbox(
            cabinet,
            (0.036, 0.010, jamb_h),
            (hinge_x, r.D / 2.0 - 0.014, jamb_bot + jamb_h / 2.0),
            mats["dark_wood"],
            f"door_jamb_spine_{i}",
        )

        hinge_zs = (r.door_bottom + 0.18, door_top - 0.18)
        barrel_len, socket_len, socket_offset, axle_len = _hinge_hardware_dimensions(r.door_height)
        gap_half = axle_len / 2.0 + 0.008
        cursor = jamb_bot
        segment_index = 0
        for hinge_index, hinge_z in enumerate(hinge_zs):
            segment_top = hinge_z - gap_half
            if segment_top > cursor + 0.010:
                segment_h = segment_top - cursor
                _cbox(
                    cabinet,
                    (0.036, r.panel_t, segment_h),
                    (
                        hinge_x,
                        r.D / 2.0 - r.panel_t / 2.0,
                        cursor + segment_h / 2.0,
                    ),
                    mats["dark_wood"],
                    f"door_jamb_segment_{i}_{segment_index}",
                )
                segment_index += 1
            # Three-piece butt hinge: two cabinet knuckles capture a shorter
            # door barrel, while a slender cabinet axle passes through all
            # three.  Only axle↔barrel is an intentional inter-part overlap.
            for knuckle_name, z_offset in (
                ("lower", -socket_offset),
                ("upper", socket_offset),
            ):
                _ccyl(
                    cabinet,
                    0.010,
                    socket_len,
                    (hinge_x, r.D / 2.0, hinge_z + z_offset),
                    mats["metal"],
                    f"hinge_socket_{i}_{hinge_index}_{knuckle_name}",
                )
            _ccyl(
                cabinet,
                0.0035,
                axle_len,
                (hinge_x, r.D / 2.0, hinge_z),
                mats["metal"],
                f"hinge_axle_{i}_{hinge_index}",
            )
            cursor = hinge_z + gap_half
        if door_top > cursor + 0.010:
            segment_h = door_top - cursor
            _cbox(
                cabinet,
                (0.036, r.panel_t, segment_h),
                (
                    hinge_x,
                    r.D / 2.0 - r.panel_t / 2.0,
                    cursor + segment_h / 2.0,
                ),
                mats["dark_wood"],
                f"door_jamb_segment_{i}_{segment_index}",
            )
    return jambs


def _emit_rack_glass_shelf_bay(cabinet, r: ResolvedWineCabinet2Config, mats) -> list[float]:
    """Emit 2-4 glass shelves in the upper display bay. Returns their z tops."""
    span = r.rack_z_max - r.rack_z_min - 0.05
    n_shelves = 3
    dz = span / (n_shelves + 1)
    shelf_w = r.rack_x_max - r.rack_x_min - 0.05
    # Full-depth shelves that embed into the back stiffener by ~5mm.
    shelf_d = r.D - r.back_t - 0.005
    shelf_y = 0.005  # bias so back edge overlaps the stiffener
    zs: list[float] = []
    # Glass shelves are transparent panels inside the upper bay.
    for i in range(n_shelves):
        z = r.rack_z_min + dz * (i + 1)
        _cbox(
            cabinet,
            (shelf_w, shelf_d, 0.010),
            (0.0, shelf_y, z),
            mats["glass"],
            f"glass_shelf_{i}",
        )
        zs.append(z + 0.005)
    # A slim wooden back stiffener the shelves rest against so they weld to the
    # carcass connectivity graph. Placed thick enough to embed the shelf back edges.
    stiffener_t = 0.020
    _cbox(
        cabinet,
        (shelf_w, stiffener_t, r.rack_z_max - r.rack_z_min - 0.05),
        (0.0, -r.D / 2.0 + r.back_t + stiffener_t / 2.0, (r.rack_z_min + r.rack_z_max) / 2.0),
        mats["edge_wood"],
        "display_bay_stiffener",
    )
    return zs


def _full_depth_rack_board_span(
    r: ResolvedWineCabinet2Config,
    *,
    front_clearance: float = 0.036,
) -> tuple[float, float]:
    """Return ``(depth, center_y)`` for a real front-to-back rack divider.

    The accepted wine-cabinet sources use the diagonal members as shelf boards,
    not as a shallow X applique on the back wall.  Their rear edges embed into
    the back panel and their front edges reach the rack mouth while retaining a
    small clearance to any closed facade.
    """
    y_back = -r.D / 2.0 + r.back_t - 0.006
    y_front = r.D / 2.0 - front_clearance
    return y_front - y_back, (y_front + y_back) / 2.0


def _diamond_bottle_origin_z(
    cell_z: float,
    angle: float,
    board_t: float,
    *,
    bottle_radius: float = 0.033,
) -> float:
    """Seat a horizontal bottle tangentially in the lower V of a diamond cell."""
    tangent_center_offset = (bottle_radius + board_t / 2.0 + 0.0000005) / math.cos(angle)
    # _add_horizontal_bottle places its cylindrical center bottle_radius above
    # the child origin, so convert the desired center height to joint-origin Z.
    return cell_z + tangent_center_offset - bottle_radius


def _diamond_bottle_origin_y(r: ResolvedWineCabinet2Config) -> float:
    """Place the bottle neck at the rack mouth while its body stays in the V."""
    _depth, _center_y = _full_depth_rack_board_span(r)
    rack_front_y = r.D / 2.0 - 0.036
    # The horizontal bottle helper reaches 0.148 m forward from its origin.
    # Retain an 18 mm front reveal, matching the accepted full-depth sources.
    return rack_front_y - 0.166


def _emit_rack_diamond_lattice(
    cabinet, r: ResolvedWineCabinet2Config, mats
) -> list[tuple[float, float, float, float, int, int]]:
    """Emit a full-depth N×N diamond rack.

    Returns ``(cx, cz, cw, ch, col, row)`` per lower-V bottle seat.

    Connectivity (Contract 3): all lattice boards physically touch the carcass
    via a full-width ``rack_back_board`` that overlaps the back_panel's front
    face AND provides the surface every lattice board's back edge embeds into.
    Without this, the entire lattice floats and every carcass visual reports as
    a disconnected island against the lattice cluster.
    """
    cols = 3
    rows = 3
    xmin = r.rack_x_min + 0.02
    xmax = r.rack_x_max - 0.02
    zmin = r.rack_z_min + 0.05
    zmax = r.rack_z_max - 0.03
    cw = (xmax - xmin) / cols
    ch = (zmax - zmin) / rows
    board_t = 0.028
    # Source-backed shelf boards run from the back panel to the rack mouth.  A
    # shallow board plus a forward saddle is specifically forbidden here: the
    # two lower diagonal boards themselves form the bottle-bearing V trough.
    board_d, board_cy = _full_depth_rack_board_span(r)
    y_back_front = -r.D / 2.0 + r.back_t

    # Support/back board that spans the rack region and embeds the lattice into
    # the carcass. Its -Y face overlaps the back_panel's +Y face by ~5mm; its
    # +Y face sits at the same plane the lattice boards' back edges embed into.
    back_board_t = 0.014
    _cbox(
        cabinet,
        (xmax - xmin + 0.04, back_board_t, zmax - zmin + 0.04),
        (
            (xmin + xmax) / 2.0,
            y_back_front + back_board_t / 2.0 - 0.005,
            (zmin + zmax) / 2.0,
        ),
        mats["back"],
        "rack_back_board",
    )

    # Verticals + horizontals frame the grid. Their back edge overlaps
    # rack_back_board's +Y face by 6mm.
    for c in range(1, cols):
        x = xmin + c * cw
        _cbox(
            cabinet,
            (0.032, board_d, zmax - zmin),
            (x, board_cy, (zmin + zmax) / 2.0),
            mats["wood"],
            f"rack_vertical_{c}",
        )
    for rr in range(1, rows):
        z = zmin + rr * ch
        _cbox(
            cabinet,
            (xmax - xmin, board_d, 0.032),
            ((xmin + xmax) / 2.0, board_cy, z),
            mats["wood"],
            f"rack_horizontal_{rr}",
        )

    # Also add side infill so the outermost cells' diagonals also touch the
    # carcass side panels (Contract 3: no floating lattice edge cells).
    for c_idx, side_x in ((0, xmin - 0.006), (1, xmax + 0.006)):
        _cbox(
            cabinet,
            (0.020, board_d, zmax - zmin),
            (side_x, board_cy, (zmin + zmax) / 2.0),
            mats["wood"],
            f"rack_side_infill_{c_idx}",
        )

    # Diamond diagonals within each cell.
    angle = math.atan2(ch, cw)
    length = math.hypot(cw, ch) + 0.03
    cells: list[tuple[float, float, float, float, int, int]] = []
    for c in range(cols):
        for rr in range(rows):
            cx = xmin + (c + 0.5) * cw
            cz = zmin + (rr + 0.5) * ch
            _cbox(
                cabinet,
                (length, board_d, board_t),
                (cx, board_cy, cz),
                mats["edge_wood"],
                f"cell_{c}_{rr}_slash",
                rpy=(0.0, -angle, 0.0),
            )
            _cbox(
                cabinet,
                (length, board_d, board_t),
                (cx, board_cy, cz),
                mats["edge_wood"],
                f"cell_{c}_{rr}_backslash",
                rpy=(0.0, angle, 0.0),
            )
            cells.append((cx, cz, cw, ch, c, rr))
    return cells


def _emit_rack_horizontal_bar(cabinet, r: ResolvedWineCabinet2Config, mats) -> list[float]:
    """Two rows of metal bars carrying horizontal bottles. Returns row z-centers.

    Connectivity: bars extend from side_panel to side_panel (embedded 15mm each
    end) so each bar cylinder touches the carcass side panels. Backstops embed
    into the back_panel (5mm overlap). Otherwise the entire rack cluster floats
    as an island.
    """
    zs = []
    span = r.rack_z_max - r.rack_z_min - 0.05
    n_rows = 3
    dz = span / (n_rows + 1)
    # Bars span the full inner width and embed 15mm into each side panel.
    bar_len = r.W - r.side_t + 0.005
    for i in range(n_rows):
        z = r.rack_z_min + dz * (i + 1)
        for depth_idx, y in enumerate((-r.D / 4.0, r.D / 4.0 - 0.05)):
            _ccyl(
                cabinet,
                0.010,
                bar_len,
                (0.0, y, z - 0.010),
                mats["metal"],
                f"rack_bar_{i}_{depth_idx}",
                rpy=(0.0, math.pi / 2.0, 0.0),
            )
        # Wooden support ledge along the back for containment; overlap the
        # back_panel front face by 6mm so it welds to the carcass.
        backstop_t = 0.020
        _cbox(
            cabinet,
            (r.W - 2.0 * r.side_t, backstop_t, 0.014),
            (
                0.0,
                -r.D / 2.0 + r.back_t + backstop_t / 2.0 - 0.006,
                z + 0.008,
            ),
            mats["dark_wood"],
            f"rack_backstop_{i}",
        )
        zs.append(z)
    return zs


def _emit_rack_vertical_pegs(
    cabinet, r: ResolvedWineCabinet2Config, mats
) -> list[tuple[float, float, float]]:
    """Emit a backed peg rack and return bottle cradle centers.

    The accepted vertical-peg variant supplies a perforated back and cylindrical
    dowels.  Here the pegs remain supports: actual bottles rest on paired pegs;
    the pegs never replace the bottles themselves.
    """
    panel_w = r.rack_x_max - r.rack_x_min - 0.06
    panel_h = r.rack_z_max - r.rack_z_min - 0.08
    panel_y = -r.D / 2.0 + r.back_t + 0.010
    _cbox(
        cabinet,
        (panel_w, 0.020, panel_h),
        (0.0, panel_y, (r.rack_z_min + r.rack_z_max) / 2.0),
        mats["back"],
        "pegboard_back",
    )
    cols = 4
    rows = 3
    dx = panel_w / cols
    dz = panel_h / rows
    supports: list[tuple[float, float, float]] = []
    peg_len = min(0.22, r.D - r.back_t - 0.09)
    for row in range(rows):
        z = r.rack_z_min + 0.08 + (row + 0.5) * dz
        for col in range(cols):
            x = -panel_w / 2.0 + (col + 0.5) * dx
            # Paired front-to-back dowels are captured in the backed panel.
            for side, sx in enumerate((-0.026, 0.026)):
                _ccyl(
                    cabinet,
                    0.010,
                    peg_len,
                    (x + sx, panel_y + peg_len / 2.0, z),
                    mats["metal"],
                    f"bottle_peg_{row}_{col}_{side}",
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                )
            # A shallow saddle joins the two pegs and gives the horizontal
            # bottle a stable, inspectable support face.
            _cbox(
                cabinet,
                (0.072, 0.036, 0.012),
                (x, panel_y + peg_len * 0.72, z + 0.010),
                mats["dark_wood"],
                f"peg_saddle_{row}_{col}",
            )
            supports.append((x, panel_y + peg_len * 0.72, z + 0.016))
    return supports


def _emit_rack_hybrid_display(
    cabinet, r: ResolvedWineCabinet2Config, mats
) -> list[tuple[str, float, float, float]]:
    """Emit the accepted modular N=20 support bundle.

    The source is not twenty interchangeable bottles on one generic shelf.  It
    has four upright display bottles, nine horizontal bottles in a diamond
    lattice, and seven horizontal bottles on cooler shelves.  We preserve that
    support/type sequence so N=20 is a real source-matched configuration; lower
    N values are bounded prefixes of the same coordinated layout.
    """
    if r.body_form != "modular_light_wood":
        raise ValueError("hybrid_display_rack requires modular_light_wood")

    upper_x_min = r.rack_x_min + 0.025
    upper_x_max = r.rack_x_max - 0.025
    upper_z_min = r.rack_z_min + 0.045
    upper_z_max = r.rack_z_max - 0.035
    upper_w = upper_x_max - upper_x_min
    split_x = upper_x_min + upper_w * 0.42
    y_back_front = -r.D / 2.0 + r.back_t

    # A shared backed divider makes the two upper support families part of one
    # cabinet insert rather than disconnected decorative clusters.
    back_t = 0.016
    _cbox(
        cabinet,
        (upper_w, back_t, upper_z_max - upper_z_min),
        (
            (upper_x_min + upper_x_max) / 2.0,
            y_back_front + back_t / 2.0 - 0.005,
            (upper_z_min + upper_z_max) / 2.0,
        ),
        mats["back"],
        "hybrid_upper_back",
    )
    _cbox(
        cabinet,
        (0.022, r.D - r.back_t - 0.060, upper_z_max - upper_z_min),
        (split_x, -0.010, (upper_z_min + upper_z_max) / 2.0),
        mats["edge_wood"],
        "hybrid_upper_divider",
    )

    # Four upright display positions: two on each of two real glass shelves.
    upright_supports: list[tuple[str, float, float, float]] = []
    left_min = upper_x_min + 0.025
    left_max = split_x - 0.035
    for row, fraction in enumerate((0.27, 0.62)):
        z = upper_z_min + (upper_z_max - upper_z_min) * fraction
        shelf_w = left_max - left_min
        shelf_d = r.D - r.back_t - 0.055
        shelf_y = y_back_front + shelf_d / 2.0 - 0.005
        _cbox(
            cabinet,
            (shelf_w, shelf_d, 0.010),
            ((left_min + left_max) / 2.0, shelf_y, z),
            mats["glass"],
            f"hybrid_glass_shelf_{row}",
        )
        for col in range(2):
            x = left_min + shelf_w * (col + 0.5) / 2.0
            upright_supports.append(("upright", x, 0.0, z + 0.005))

    # Nine source-matched diamond cells in the upper-right bay.  As in the
    # accepted full-depth source rack, the diagonal shelf boards themselves
    # carry each bottle in their lower V; there is no forward fake saddle.
    diamond_supports: list[tuple[str, float, float, float]] = []
    right_min = split_x + 0.035
    right_max = upper_x_max - 0.010
    cols = rows = 3
    cw = (right_max - right_min) / cols
    ch = (upper_z_max - upper_z_min) / rows
    board_d, board_y = _full_depth_rack_board_span(r)
    angle = math.atan2(ch, cw)
    diagonal_len = math.hypot(cw, ch) + 0.025
    for col in range(cols):
        for row in range(rows):
            index = col * rows + row
            cx = right_min + (col + 0.5) * cw
            cz = upper_z_min + (row + 0.5) * ch
            for slash, sign in (("slash", -1.0), ("backslash", 1.0)):
                _cbox(
                    cabinet,
                    (diagonal_len, board_d, 0.026),
                    (cx, board_y, cz),
                    mats["edge_wood"],
                    f"hybrid_cell_{index}_{slash}",
                    rpy=(0.0, sign * angle, 0.0),
                )
            diamond_supports.append(
                (
                    "rack",
                    cx,
                    _diamond_bottle_origin_y(r),
                    _diamond_bottle_origin_z(cz, angle, 0.026),
                )
            )

    # Seven horizontal cooler positions in the lower band: 2+2+1+1+1.
    # The five shelves are tied into the back panel and sit below the middle
    # deck, matching the accepted modular source rather than stealing capacity
    # from the upper rack.
    cooler_supports: list[tuple[str, float, float, float]] = []
    cooler_x_min = r.rack_x_min + 0.035
    cooler_x_max = min(split_x - 0.025, cooler_x_min + r.W * 0.40)
    cooler_w = cooler_x_max - cooler_x_min
    lower_z_min = r.plinth_h + 0.085
    # Keep the top bottle's 66 mm diameter below the middle deck while leaving
    # enough pitch for five supported rows.
    lower_z_max = r.shelf_z - 0.105
    shelf_d = r.D - r.back_t - 0.065
    shelf_y = y_back_front + shelf_d / 2.0 - 0.005
    row_counts = (2, 2, 1, 1, 1)
    for row, count in enumerate(row_counts):
        z = lower_z_min + (lower_z_max - lower_z_min) * row / (len(row_counts) - 1)
        _cbox(
            cabinet,
            (cooler_w, shelf_d, 0.012),
            ((cooler_x_min + cooler_x_max) / 2.0, shelf_y, z),
            mats["dark_wood"],
            f"hybrid_cooler_shelf_{row}",
        )
        for col in range(count):
            x = cooler_x_min + cooler_w * (col + 0.5) / count
            # Horizontal bottle local z=0 is its tangent plane, so the FIXED
            # origin must coincide with the shelf top (not float above it).
            cooler_supports.append(("cooler", x, 0.0, z + 0.006))

    supports = upright_supports + diamond_supports + cooler_supports
    if len(supports) != 20:
        raise AssertionError(f"hybrid rack emitted {len(supports)} seats, expected 20")
    return supports


# ---------------------------------------------------------------------------
# Door mechanism helpers. Each builds visuals in the door part's local frame
# such that (0,0,0) sits on the hinge line at the door mid-height, +Y is
# outside the cabinet (opens forward), and +X points away from the hinge along
# the leaf.
# ---------------------------------------------------------------------------
def _emit_door_hinge_barrels(door, h: float, mats, *, direction: float) -> None:
    """Emit two door-side barrels and short straps clear of the hinge axle."""
    barrel_len, _socket_len, _socket_offset, _axle_len = _hinge_hardware_dimensions(h)
    for idx, dz in enumerate((-h / 2.0 + 0.18, h / 2.0 - 0.18)):
        _ccyl(
            door,
            0.008,
            barrel_len,
            (0.0, 0.0, dz),
            mats["metal"],
            f"hinge_barrel_{idx}",
        )
        _cbox(
            door,
            (0.008, 0.012, 0.050),
            (direction * 0.010, 0.006, dz),
            mats["metal"],
            f"hinge_strap_{idx}",
        )


def _door_swing_glass(door, r, mats, *, direction: float):
    w = r.door_width
    h = r.door_height
    d = 0.024
    s = direction
    yc = d / 2.0  # so hinge_stile's -Y face lands at y=0 (mates jamb +Y face).
    # Perimeter frame.
    _cbox(door, (0.038, d, h), (s * 0.031, yc, 0.0), mats["wood"], "hinge_stile")
    _cbox(door, (0.038, d, h), (s * (w - 0.019), yc, 0.0), mats["wood"], "handle_stile")
    _cbox(
        door,
        (w - 0.076, d, 0.044),
        (s * w / 2.0, yc, -h / 2.0 + 0.022),
        mats["wood"],
        "bottom_rail",
    )
    _cbox(door, (w - 0.076, d, 0.044), (s * w / 2.0, yc, h / 2.0 - 0.022), mats["wood"], "top_rail")
    _cbox(
        door,
        (w - 0.070, 0.006, h - 0.084),
        (s * w / 2.0, yc + 0.003, 0.0),
        mats["glass"],
        "glass_panel",
    )
    # Slim vertical pull with two mounts. Mounts are horizontal cylinders that
    # bridge the +Y face of the handle_stile (yc + d/2 = 0.024) to the handle
    # cylinder axis (yc + 0.030). Mount length spans that gap plus small embeds.
    handle_x = s * (w - 0.019)  # keep on handle_stile centerline
    mount_len = 0.024
    _ccyl(
        door,
        0.006,
        min(0.34, h * 0.55),
        (handle_x, yc + d / 2.0 + mount_len - 0.002, 0.0),
        mats["metal"],
        "door_handle",
    )
    for idx, dz in enumerate((-0.13, 0.13)):
        _ccyl(
            door,
            0.0065,
            mount_len,
            (handle_x, yc + d / 2.0 + mount_len / 2.0, dz),
            mats["metal"],
            f"handle_mount_{idx}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
    _emit_door_hinge_barrels(door, h, mats, direction=s)


def _door_swing_divided_glass(door, r, mats, *, direction: float):
    w = r.door_width
    h = r.door_height
    d = 0.026
    s = direction
    yc = d / 2.0
    stile = 0.038
    rail = 0.042
    mullion = 0.022
    x_mid = s * w / 2.0
    x_hinge = s * (0.012 + stile / 2.0)
    x_free = s * (w - stile / 2.0)
    _cbox(door, (stile, d, h), (x_hinge, yc, 0.0), mats["wood"], "hinge_stile")
    _cbox(door, (stile, d, h), (x_free, yc, 0.0), mats["wood"], "handle_stile")
    _cbox(door, (w, d, rail), (x_mid, yc, h / 2.0 - rail / 2.0), mats["wood"], "top_rail")
    _cbox(door, (w, d, rail), (x_mid, yc, -h / 2.0 + rail / 2.0), mats["wood"], "bottom_rail")
    _cbox(door, (mullion, d, h - 2.0 * rail), (x_mid, yc, 0.0), mats["wood"], "vertical_mullion")
    for i, dz in enumerate((-h * 0.17, h * 0.17)):
        _cbox(
            door,
            (w - 2.0 * stile, d, mullion),
            (x_mid, yc, dz),
            mats["wood"],
            f"cross_mullion_{i}",
        )
    # Six panes.
    pane_w = (w - 2.0 * stile - mullion) / 2.0 + 0.002
    pane_h = (h - 2.0 * rail - 2.0 * mullion) / 3.0 + 0.002
    x0 = stile + pane_w / 2.0 - 0.001
    x1 = w - stile - pane_w / 2.0 + 0.001
    zs = (-h * 0.32, 0.0, h * 0.32)
    idx = 0
    for x_abs in (x0, x1):
        for dz in zs:
            _cbox(
                door,
                (pane_w, 0.005, pane_h),
                (s * x_abs, yc + 0.006, dz),
                mats["glass"],
                f"glass_pane_{idx}",
            )
            idx += 1
    # Handle: mount sits on the +Y face of the handle_stile.
    handle_x = s * (w - stile / 2.0)
    mount_len = 0.026
    _ccyl(
        door,
        0.007,
        min(0.16, h * 0.30),
        (handle_x, yc + d / 2.0 + mount_len - 0.002, -0.005),
        mats["metal"],
        "door_handle",
    )
    for i, dz in enumerate((-0.06, 0.05)):
        _cbox(
            door,
            (0.014, mount_len, 0.014),
            (handle_x, yc + d / 2.0 + mount_len / 2.0, dz),
            mats["metal"],
            f"handle_mount_{i}",
        )
    _emit_door_hinge_barrels(door, h, mats, direction=s)


def _door_swing_paneled(door, r, mats, *, direction: float):
    w = r.door_width
    h = r.door_height
    s = direction
    d_frame = 0.042
    yc = d_frame / 2.0  # so hinge_stile -Y face at y=0.
    stile_w = 0.055
    rail_w = 0.055
    # Face frame.
    _cbox(
        door,
        (stile_w, d_frame, h),
        (s * (0.012 + stile_w / 2.0), yc, 0.0),
        mats["wood"],
        "hinge_stile",
    )
    _cbox(
        door,
        (stile_w, d_frame, h),
        (s * (w - stile_w / 2.0), yc, 0.0),
        mats["wood"],
        "handle_stile",
    )
    _cbox(
        door,
        (w, d_frame, rail_w),
        (s * w / 2.0, yc, -h / 2.0 + rail_w / 2.0),
        mats["wood"],
        "lower_rail",
    )
    _cbox(
        door,
        (w, d_frame, rail_w),
        (s * w / 2.0, yc, h / 2.0 - rail_w / 2.0),
        mats["wood"],
        "upper_rail",
    )
    # Recessed panel — inset into the frame so it stays within the frame envelope.
    _cbox(
        door,
        (w - 2.0 * stile_w, 0.022, h - 2.0 * rail_w),
        (s * w / 2.0, yc - 0.004, 0.0),
        mats["dark_wood"],
        "recessed_panel",
    )
    # Brass knob mounted on the +Y face of the handle_stile.
    knob_len = 0.028
    _ccyl(
        door,
        0.012,
        knob_len,
        (s * (w - stile_w / 2.0), yc + d_frame / 2.0 + knob_len / 2.0 - 0.002, h * 0.08),
        mats["metal"],
        "door_knob",
        rpy=(-math.pi / 2.0, 0.0, 0.0),
    )
    _ccyl(
        door,
        0.018,
        0.010,
        (s * (w - stile_w / 2.0), yc + d_frame / 2.0 + 0.003, h * 0.08),
        mats["metal"],
        "knob_backplate",
        rpy=(-math.pi / 2.0, 0.0, 0.0),
    )
    # Hinge barrels straddling the door hinge line (embedded in hinge_stile).
    _emit_door_hinge_barrels(door, h, mats, direction=s)


def _door_swing_cooler(door, r, mats, *, direction: float):
    w = r.door_width
    h = r.door_height
    d = 0.024
    s = direction
    yc = d / 2.0
    _cbox(door, (0.038, d, h), (s * 0.031, yc, 0.0), mats["wood"], "hinge_stile")
    _cbox(door, (0.038, d, h), (s * (w - 0.019), yc, 0.0), mats["wood"], "handle_stile")
    _cbox(door, (w, d, 0.040), (s * w / 2.0, yc, h / 2.0 - 0.020), mats["wood"], "top_rail")
    _cbox(door, (w, d, 0.040), (s * w / 2.0, yc, -h / 2.0 + 0.020), mats["wood"], "bottom_rail")
    _cbox(
        door,
        (w - 0.076, 0.006, h - 0.080),
        (s * w / 2.0, yc + 0.001, 0.0),
        mats["glass"],
        "door_glass",
    )
    _emit_door_hinge_barrels(door, h, mats, direction=s)
    # Long vertical brushed pull with two mounts spanning the handle_stile front.
    handle_x = s * (w - 0.019)
    mount_len = 0.030
    _ccyl(
        door,
        0.009,
        min(0.28, h * 0.55),
        (handle_x, yc + d / 2.0 + mount_len - 0.003, 0.0),
        mats["metal"],
        "door_handle",
    )
    for idx, dz in enumerate((-0.09, 0.09)):
        _ccyl(
            door,
            0.006,
            mount_len,
            (handle_x, yc + d / 2.0 + mount_len / 2.0, dz),
            mats["metal"],
            f"handle_mount_{idx}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )


def _door_sliding_glass(door, r, mats, *, direction: float):
    """Centered framed glass leaf for bypass and pocket tracks."""
    del direction
    w = r.door_width
    h = r.door_height
    d = 0.018
    stile = 0.034
    rail = 0.040
    _cbox(door, (stile, d, h), (-w / 2.0 + stile / 2.0, 0.0, 0.0), mats["wood"], "left_stile")
    _cbox(door, (stile, d, h), (w / 2.0 - stile / 2.0, 0.0, 0.0), mats["wood"], "right_stile")
    _cbox(door, (w, d, rail), (0.0, 0.0, -h / 2.0 + rail / 2.0), mats["wood"], "bottom_rail")
    _cbox(door, (w, d, rail), (0.0, 0.0, h / 2.0 - rail / 2.0), mats["wood"], "top_rail")
    _cbox(
        door,
        (w - 2.0 * stile, 0.005, h - 2.0 * rail),
        (0.0, 0.0, 0.0),
        mats["glass"],
        "glass_panel",
    )
    shoe_h = 0.012
    for name, z in (
        ("track_shoe_bottom", -h / 2.0 - shoe_h / 2.0),
        ("track_shoe_top", h / 2.0 + shoe_h / 2.0),
    ):
        _cbox(door, (0.070, 0.022, shoe_h), (0.0, 0.0, z), mats["metal"], name)
    # Flush pull remains within the pocket/bypass envelope.
    _cbox(
        door,
        (0.040, 0.014, 0.040),
        (w * 0.34, 0.0, 0.0),
        mats["metal"],
        "flush_pull_backplate",
    )
    _ccyl(
        door,
        0.015,
        0.004,
        (w * 0.34, d / 2.0, 0.0),
        mats["metal"],
        "flush_pull",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )


def _emit_sliding_door_tracks(
    cabinet, r: ResolvedWineCabinet2Config, mats
) -> list[tuple[float, float, tuple[float, float, float]]]:
    """Emit real upper/lower tracks and optional side pocket wells.

    Returns ``(start_x, lane_y, axis)`` for the two leaves.
    """
    zone_w = r.W - 2.0 * r.side_t - 0.02
    door_top = r.door_bottom + r.door_height
    if r.door_mechanism == "sliding_glass":
        lane_ys = (r.D / 2.0 + 0.018, r.D / 2.0 + 0.048)
        start_xs = (-zone_w * 0.25, zone_w * 0.25)
        axes = ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    else:
        # The leaf plane sits just ahead of the shelf fronts, while the side
        # cheek pair forms a shallow furniture pocket around it.
        lane_y = r.D / 2.0 + 0.018
        lane_ys = (lane_y, lane_y)
        central_opening_w = zone_w * 0.48
        start_xs = (-central_opening_w * 0.25, central_opening_w * 0.25)
        axes = ((-1.0, 0.0, 0.0), (1.0, 0.0, 0.0))
        # Side pocket wells: two thin cheeks bound a channel in Y; their X
        # span is wider than admitted travel, and their mouth remains open.
        pocket_w = (zone_w - central_opening_w) / 2.0
        for side, sign in enumerate((-1.0, 1.0)):
            pocket_x = sign * (central_opening_w / 2.0 + pocket_w / 2.0)
            for cheek, y in enumerate((lane_y - 0.016, lane_y + 0.016)):
                _cbox(
                    cabinet,
                    (pocket_w, 0.008, r.door_height + 0.050),
                    (pocket_x, y, r.door_bottom + r.door_height / 2.0),
                    mats["wood"],
                    f"pocket_cheek_{side}_{cheek}",
                )
    track_w = zone_w + 0.020
    for lane, lane_y in enumerate(lane_ys):
        for level, z in (
            ("bottom", r.door_bottom - 0.018),
            ("top", door_top + 0.018),
        ):
            _cbox(
                cabinet,
                (track_w, 0.024, 0.012),
                (0.0, lane_y, z),
                mats["metal"],
                f"door_{level}_track_{lane}",
            )
            side_front_y = r.D / 2.0 - 0.006
            connector_d = abs(lane_y - side_front_y) + 0.024
            connector_y = (lane_y + side_front_y) / 2.0
            for side, x in enumerate((-r.W / 2.0 + r.side_t / 2.0, r.W / 2.0 - r.side_t / 2.0)):
                _cbox(
                    cabinet,
                    (r.side_t, connector_d, 0.018),
                    (x, connector_y, z),
                    mats["metal"],
                    f"door_{level}_track_bracket_{lane}_{side}",
                )
    return [(start_xs[i], lane_ys[i], axes[i]) for i in range(2)]


_DOOR_BUILDERS = {
    "swing_glass": _door_swing_glass,
    "swing_divided_glass": _door_swing_divided_glass,
    "swing_paneled": _door_swing_paneled,
    "swing_cooler": _door_swing_cooler,
    "sliding_glass": _door_sliding_glass,
    "pocket_glass": _door_sliding_glass,
}


# ---------------------------------------------------------------------------
# Drawer helper (shared across drawer_count values).
# ---------------------------------------------------------------------------
def _build_drawer(drawer, r: ResolvedWineCabinet2Config, mats, *, width: float):
    """Drawer local frame: (0,0,0) = the joint origin. drawer_front's -Y face is at y=0
    (mates the carcass ``drawer_sill_i`` +Y face). Drawer front extends OUTWARD from
    the carcass on opening (joint axis = (0,1,0), so q>0 moves +Y). Interior box
    extends INTO the carcass (-Y)."""
    ft = 0.024
    front_h = min(0.20, max(0.10, (r.drawer_band_top - r.drawer_band_bot - 0.03)))
    box_h = min(front_h * 0.82, r.drawer_box_height)
    box_d = r.drawer_box_depth
    # Front panel (thickness ft) — its -Y face at y=0, so its center at -ft/2 (into
    # the cabinet). At closed pose (q=0) the front panel occupies -ft..0 in world Y
    # relative to the sill; opening the joint pulls it forward.
    _cbox(drawer, (width, ft, front_h), (0.0, -ft / 2.0, 0.0), mats["wood"], "drawer_front")
    # Interior box: sides / back / bottom behind the front. Sides extend from
    # y=-ft (inner face of drawer_front) into -Y, overlapping drawer_front by 1mm
    # so the part's internal geometry-island check finds real contact.
    side_len = box_d - ft
    side_y = -ft - side_len / 2.0 + 0.001  # 1mm overlap with drawer_front's -Y face
    _cbox(
        drawer,
        (0.014, side_len, box_h),
        (-(width - 0.030) / 2.0, side_y, -0.010),
        mats["dark_wood"],
        "drawer_side_0",
    )
    _cbox(
        drawer,
        (0.014, side_len, box_h),
        ((width - 0.030) / 2.0, side_y, -0.010),
        mats["dark_wood"],
        "drawer_side_1",
    )
    _cbox(
        drawer,
        (width - 0.030, 0.014, box_h),
        (0.0, -ft - side_len, -0.010),
        mats["dark_wood"],
        "drawer_back",
    )
    _cbox(
        drawer,
        (width - 0.036, side_len - 0.010, 0.014),
        (0.0, side_y, -0.010 - box_h / 2.0 + 0.007),
        mats["dark_wood"],
        "drawer_bottom",
    )
    # Paired moving glides sit on the cabinet's two longitudinal rails.  They
    # are outside the containment cavity and stay engaged in plan view through
    # the admitted travel.
    guide_len = max(0.12, r.drawer_box_depth - 0.045)
    guide_y = -ft - guide_len / 2.0 - 0.006
    side_x = (width - 0.030) / 2.0
    for side, sign in enumerate((-1.0, 1.0)):
        _cbox(
            drawer,
            (0.010, guide_len, 0.008),
            (sign * (side_x + 0.012), guide_y, -box_h / 2.0 + 0.021),
            mats["metal"],
            f"drawer_glide_{side}",
        )
    # Brass pull mounted on the +Y face of the front panel.
    _ccyl(
        drawer,
        0.006,
        min(0.14, width * 0.34),
        (0.0, 0.012, 0.02),
        mats["metal"],
        "drawer_pull",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    for i, dx in enumerate((-0.04, 0.04)):
        _ccyl(
            drawer,
            0.006,
            0.026,
            (dx, 0.006, 0.02),
            mats["metal"],
            f"pull_post_{i}",
            rpy=(-math.pi / 2.0, 0.0, 0.0),
        )


# ---------------------------------------------------------------------------
# Bottle helpers — inlined visuals on FIXED child parts.
# ---------------------------------------------------------------------------
def _add_upright_bottle(part, mats, *, glass_key: str):
    body_mat = mats[glass_key]
    _ccyl(part, 0.034, 0.010, (0.0, 0.0, 0.005), body_mat, "bottle_base")
    _ccyl(part, 0.032, 0.130, (0.0, 0.0, 0.065), body_mat, "bottle_body")
    part.visual(
        Sphere(radius=0.032),
        origin=Origin(xyz=(0.0, 0.0, 0.135)),
        material=body_mat,
        name="bottle_shoulder", material_class_id="glass.smoked_tinted",
    )
    _ccyl(part, 0.012, 0.050, (0.0, 0.0, 0.170), body_mat, "bottle_neck")
    # Cork embeds 2mm into the neck top to guarantee real contact.
    _ccyl(part, 0.013, 0.012, (0.0, 0.0, 0.201), mats["cork"], "bottle_cork")


def _add_horizontal_bottle(
    part,
    mats,
    *,
    glass_key: str,
    name_prefix: str = "",
    xyz: tuple[float, float, float] = (0.0, 0.0, 0.0),
    body_radius: float = 0.033,
):
    body_mat = mats[glass_key]
    rpy = (math.pi / 2.0, 0.0, 0.0)
    ox, oy, oz = xyz

    def element_name(stem: str) -> str:
        return f"{name_prefix}{stem}" if name_prefix else stem

    # Local z=0 is the rack contact plane; the bottle body is tangent above it.
    zc = body_radius
    _ccyl(
        part,
        body_radius,
        0.180,
        (ox, oy - 0.005, oz + zc),
        body_mat,
        element_name("bottle_body"),
        rpy=rpy,
    )
    part.visual(
        Sphere(radius=body_radius),
        origin=Origin(xyz=(ox, oy + 0.072, oz + zc)),
        material=body_mat,
        name=element_name("bottle_shoulder"), material_class_id="glass.smoked_tinted",
    )
    _ccyl(
        part,
        0.012,
        0.052,
        (ox, oy + 0.108, oz + zc),
        body_mat,
        element_name("bottle_neck"),
        rpy=rpy,
    )
    _ccyl(
        part,
        0.013,
        0.016,
        (ox, oy + 0.140, oz + zc),
        mats["cork"],
        element_name("bottle_cork"),
        rpy=rpy,
    )


def _emit_pull_out_tasting_shelf(model, cabinet, r: ResolvedWineCabinet2Config, mats) -> None:
    """Source-backed pull-out serving shelf with bilateral guides."""
    shelf_w = min(r.W * 0.44, 0.66)
    shelf_d = min(r.D * 0.78, 0.39)
    x = r.W * 0.22
    z = max(r.plinth_h + 0.16, r.shelf_z - 0.19)
    front_plane = r.D / 2.0 + 0.006
    track_y = front_plane - shelf_d / 2.0 - 0.012
    # A structural lower deck ties the guide brackets to the carcass.
    _cbox(
        cabinet,
        (shelf_w + 0.05, r.D - r.back_t - 0.03, 0.018),
        (x, -0.006, z - 0.035),
        mats["wood"],
        "tasting_bay_deck",
    )
    for side, sign in enumerate((-1.0, 1.0)):
        gx = x + sign * (shelf_w / 2.0 - 0.012)
        _cbox(
            cabinet,
            (0.012, shelf_d - 0.035, 0.012),
            (gx, track_y, z - 0.014),
            mats["metal"],
            f"tasting_track_{side}",
        )
        _cbox(
            cabinet,
            (0.034, 0.028, 0.050),
            (gx, track_y - shelf_d * 0.28, z - 0.045),
            mats["metal"],
            f"tasting_track_bracket_{side}",
        )
    _cbox(
        cabinet,
        (2.0 * (r.W / 2.0 - r.side_t - x) + 0.010, 0.014, 0.016),
        (x, front_plane - 0.024 - 0.007, z + 0.030),
        mats["wood"],
        "tasting_front_stop",
    )

    shelf = model.part("tasting_shelf")
    _cbox(
        shelf,
        (shelf_w, shelf_d, 0.024),
        (0.0, -shelf_d / 2.0, 0.0),
        mats["edge_wood"],
        "shelf_board",
    )
    _cbox(shelf, (shelf_w, 0.024, 0.050), (0.0, -0.012, 0.013), mats["wood"], "front_lip")
    for side, sign in enumerate((-1.0, 1.0)):
        _cbox(
            shelf,
            (0.012, shelf_d - 0.035, 0.008),
            (sign * (shelf_w / 2.0 - 0.012), -shelf_d / 2.0 - 0.012, -0.004),
            mats["metal"],
            f"shelf_glide_{side}",
        )
    model.articulation(
        "cabinet_to_tasting_shelf",
        ArticulationType.PRISMATIC,
        parent=cabinet,
        child=shelf,
        origin=Origin(xyz=(x, front_plane, z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            lower=0.0,
            upper=r.tasting_shelf_travel,
            effort=35.0,
            velocity=0.35,
        ),
        mating=MatingContract(
            parent_face_geometry="tasting_front_stop",
            parent_face_side="positive_y",
            child_face_geometry="front_lip",
            child_face_side="negative_y",
            contact_tol=0.002,
        ),
    )


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_wine_cabinet2(
    config: WineCabinet2Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or WineCabinet2Config()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {key: model.material(f"mat_{key}", rgba=rgba) for key, rgba in palette.items()}

    # ---- Carcass ----
    cabinet = model.part("cabinet")
    _emit_common_carcass_shell(cabinet, r, mats)
    # Body-form-specific side towers / extras (④ decoration + slot A form).
    if r.body_form == "contemporary_bookcase":
        # Warm-light strips embedded into the crown_molding (its z range is at
        # r.H - r.panel_t - 0.006 ± 0.006 = [r.H - r.panel_t - 0.012, r.H - r.panel_t]).
        crown_bot_z = r.H - r.panel_t - 0.012
        for idx, (x, w) in enumerate(
            ((-r.W / 3.5, r.W / 3.5), (0.0, r.W / 3.0), (r.W / 3.5, r.W / 3.5))
        ):
            _cbox(
                cabinet,
                (abs(w), 0.014, 0.014),
                (x, r.D / 2.0 - 0.06, crown_bot_z - 0.001),
                mats["warm_light"],
                f"top_light_{idx}",
            )
    elif r.body_form == "freestanding_hutch":
        # Extra crown molding band.
        _cbox(
            cabinet,
            (r.W - 0.05, r.D - 0.05, 0.030),
            (0.0, 0.0, r.H - r.panel_t - 0.040),
            mats["edge_wood"],
            "crown_band",
        )
    elif r.body_form == "modular_light_wood":
        # Middle deck between lower band and upper display.
        _cbox(
            cabinet,
            (r.W - 2.0 * r.side_t, r.D - r.back_t - 0.02, 0.024),
            (0.0, 0.0, r.rack_z_min - 0.010),
            mats["edge_wood"],
            "middle_deck",
        )
    elif r.body_form == "built_in_wall":
        # Thick side stiles.
        for idx, xs in enumerate((-r.W / 2.0 + 0.06, r.W / 2.0 - 0.06)):
            _cbox(
                cabinet,
                (0.05, r.D - 0.05, 0.05),
                (xs, 0.0, r.H - r.panel_t - 0.032),
                mats["edge_wood"],
                f"crown_stile_{idx}",
            )
        if r.door_mechanism == "swing_paneled":
            # Source redo-002 has a real horizontal zoning stack: lower
            # paneled cupboard, shallow drawer band, then the wine rack.  Tie
            # those three interfaces to the same resolved Z boundaries.
            door_top = r.door_bottom + r.door_height
            _cbox(
                cabinet,
                (r.W - 2.0 * r.side_t + 0.016, r.D - r.back_t - 0.02, 0.024),
                (0.0, 0.0, door_top + 0.012),
                mats["edge_wood"],
                "paneled_bank_top_rail",
            )
            _cbox(
                cabinet,
                (r.W - 2.0 * r.side_t + 0.016, r.D - r.back_t - 0.02, 0.030),
                (0.0, 0.0, r.rack_z_min - 0.015),
                mats["edge_wood"],
                "upper_rack_support_deck",
            )

    # ---- Door support + drawer guides on the carcass ----
    jambs = _emit_door_jambs(cabinet, r, mats) if r.door_mechanism.startswith("swing_") else []
    slide_mounts = (
        _emit_sliding_door_tracks(cabinet, r, mats)
        if r.door_mechanism in {"sliding_glass", "pocket_glass"}
        else []
    )
    drawer_xs = _emit_drawer_band(cabinet, r, mats)

    # ---- Rack topology (all as cabinet visuals + FIXED bottle content children) ----
    shelf_zs: list[float] = []
    diamond_cells: list[tuple[float, float, float, float, int, int]] = []
    bar_rows: list[float] = []
    peg_supports: list[tuple[float, float, float]] = []
    hybrid_supports: list[tuple[str, float, float, float]] = []
    if r.rack_topology == "glass_shelf_bay":
        shelf_zs = _emit_rack_glass_shelf_bay(cabinet, r, mats)
    elif r.rack_topology == "diamond_lattice":
        diamond_cells = _emit_rack_diamond_lattice(cabinet, r, mats)
    elif r.rack_topology == "horizontal_bar_rack":
        bar_rows = _emit_rack_horizontal_bar(cabinet, r, mats)
    elif r.rack_topology == "vertical_peg_rack":
        peg_supports = _emit_rack_vertical_pegs(cabinet, r, mats)
    else:  # hybrid_display_rack
        hybrid_supports = _emit_rack_hybrid_display(cabinet, r, mats)

    # Inertial.
    cabinet.inertial = Inertial.from_geometry(
        Box((r.W, r.D, r.H)),
        mass=40.0 + 4.0 * r.door_count + 3.0 * r.drawer_count,
        origin=Origin(xyz=(0.0, 0.0, r.H / 2.0)),
    )

    # ---- Doors (parallel children of cabinet) ----
    (r.W - 2.0 * r.side_t - 0.02) / r.door_count
    door_builder = _DOOR_BUILDERS[r.door_mechanism]
    door_z_center = r.door_bottom + r.door_height / 2.0
    for i, (hinge_x, sign) in enumerate(jambs):
        door_part = model.part(f"door_{i}")
        door_builder(door_part, r, mats, direction=sign)
        # Hinge origin in cabinet frame: at the hinge line, ON the +Y face of the jamb
        # so the child's hinge_stile -Y face kisses it at closed pose.
        hinge_origin = (
            hinge_x,
            r.D / 2.0,
            door_z_center,
        )
        # Axis sign per side so both doors swing outward (+Y).
        axis = (0.0, 0.0, sign)
        # The coaxial barrel/socket pair captures the leaf.  It is validated as
        # an exact element contact below; no fictitious planar jamb mating is
        # declared for this rotational interface.
        mating = None
        # `hinged_panel` verifies open_toward and clamps the range.
        try:
            hinged_panel(
                model,
                joint_name=f"door_hinge_{i}",
                parent="cabinet",
                panel=door_part.name,
                hinge_origin=hinge_origin,
                axis=axis,
                open_toward=(0.0, 1.0, 0.0),
                max_open=r.door_open,
                margin=0.008,
                mating=mating,
                effort=14.0,
                velocity=1.2,
            )
        except ValueError:
            # If the clearance solver collapses, retry with a conservative
            # source-backed angle; never replace the hinge with fake geometry.
            hinged_panel(
                model,
                joint_name=f"door_hinge_{i}",
                parent="cabinet",
                panel=door_part.name,
                hinge_origin=hinge_origin,
                axis=axis,
                open_toward=(0.0, 1.0, 0.0),
                max_open=min(0.9, r.door_open),
                margin=0.006,
                mating=mating,
                effort=14.0,
                velocity=1.2,
                solve_clearance=False,
            )

    for i, (start_x, lane_y, axis) in enumerate(slide_mounts):
        door_part = model.part(f"door_{i}")
        door_builder(door_part, r, mats, direction=1.0)
        model.articulation(
            f"door_slide_{i}",
            ArticulationType.PRISMATIC,
            parent=cabinet,
            child=door_part,
            origin=Origin(xyz=(start_x, lane_y, r.door_bottom + r.door_height / 2.0)),
            axis=axis,
            motion_limits=MotionLimits(
                lower=0.0,
                upper=r.door_open,
                effort=20.0,
                velocity=0.35,
            ),
            mating=MatingContract(
                parent_face_geometry=f"door_bottom_track_{i}",
                parent_face_side="positive_z",
                child_face_geometry="track_shoe_bottom",
                child_face_side="negative_z",
                contact_tol=0.002,
            ),
        )

    # ---- Drawers (parallel children of cabinet) ----
    per_dw = (r.W - 2.0 * r.side_t - 0.02) / max(1, r.drawer_count) if r.drawer_count else 0.0
    # Mullion outer half-thickness = 0.010; leave a further 3mm reveal on each side
    # so the drawer_front never clips the mullion pillars.
    for i, x in enumerate(drawer_xs):
        drawer_width = max(0.10, per_dw - 2.0 * 0.010 - 0.006)
        drawer_part = model.part(f"drawer_{i}")
        _build_drawer(drawer_part, r, mats, width=drawer_width)
        # Joint origin at the cabinet front plane. drawer_front's -Y face at world
        # y = D/2 - ft matches sill's +Y face. Then intentionally embed 0.5mm so
        # the connectivity check (FCL) finds solid contact between the two boxes.
        drawer_z = r.drawer_band_bot + (r.drawer_band_top - r.drawer_band_bot) / 2.0
        origin_xyz = (x, r.D / 2.0, drawer_z)
        mating = MatingContract(
            parent_face_geometry=f"drawer_stop_{i}",
            parent_face_side="positive_y",
            child_face_geometry="drawer_front",
            child_face_side="negative_y",
            contact_tol=0.003,
        )
        # Raw PRISMATIC articulation: the complete drawer rides on bilateral
        # guides and the closed front seats on a small real stop.
        model.articulation(
            f"drawer_slide_{i}",
            ArticulationType.PRISMATIC,
            parent=cabinet,
            child=drawer_part,
            origin=Origin(xyz=origin_xyz),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(lower=0.0, upper=r.drawer_travel, effort=30.0, velocity=0.3),
            mating=mating,
        )

    # ---- FIXED bottle contents based on rack_topology ----
    _emit_fixed_bottles(
        model,
        cabinet,
        r,
        mats,
        shelf_zs,
        diamond_cells,
        bar_rows,
        peg_supports,
        hybrid_supports,
        assets,
    )

    if r.service_motion == "pull_out_tasting_shelf":
        _emit_pull_out_tasting_shelf(model, cabinet, r, mats)

    # Store slot choices in meta for axis_realization.
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["bottle_capacity_contract"] = {
        "body_form": r.body_form,
        "rack_topology": r.rack_topology,
        "requested": r.requested_bottle_count,
        "resolved": r.bottle_count,
        "capacity": r.rack_capacity,
    }
    return model


def _emit_fixed_bottles(
    model: ArticulatedObject,
    cabinet,
    r: ResolvedWineCabinet2Config,
    mats,
    shelf_zs: list[float],
    diamond_cells: list[tuple[float, float, float, float, int, int]],
    bar_rows: list[float],
    peg_supports: list[tuple[float, float, float]],
    hybrid_supports: list[tuple[str, float, float, float]],
    assets: AssetContext | None,
):
    """Populate exactly the resolved number of supported bottles."""
    if r.rack_topology == "glass_shelf_bay":
        # Upright bottles across shelves.
        placed = 0
        # Also add a couple of hollow wine glasses on the top shelf as ceramic accent.
        try:
            goblet_mesh = mesh_from_cadquery(_wine_glass_shape(), "wine_goblet", assets=assets)
        except Exception:
            goblet_mesh = None
        for si, z_top in enumerate(shelf_zs):
            if placed >= r.bottle_count:
                break
            shelf_w = r.rack_x_max - r.rack_x_min - 0.05
            # Max bottles per shelf given ~0.10 m spacing.
            per_shelf = max(2, int(shelf_w / 0.10))
            for j in range(per_shelf):
                if placed >= r.bottle_count:
                    break
                x = r.rack_x_min + 0.05 + shelf_w * (j + 0.5) / per_shelf
                bottle = model.part(f"display_bottle_{placed}")
                glass_key = "bottle_a" if placed % 2 == 0 else "bottle_b"
                _add_upright_bottle(bottle, mats, glass_key=glass_key)
                model.articulation(
                    f"cabinet_to_display_bottle_{placed}",
                    ArticulationType.FIXED,
                    parent=cabinet,
                    child=bottle,
                    origin=Origin(xyz=(x, 0.0, z_top)),
                )
                placed += 1
        # A couple of goblets on the top shelf (decoration).
        if goblet_mesh is not None and shelf_zs:
            top_z = shelf_zs[-1]
            for k in range(2):
                x = r.rack_x_min + 0.10 + k * 0.10
                gl = model.part(f"glassware_{k}")
                gl.visual(goblet_mesh, material=mats["glass"], name="wine_goblet_body", material_class_id="glass.clear_transparent")
                model.articulation(
                    f"cabinet_to_glassware_{k}",
                    ArticulationType.FIXED,
                    parent=cabinet,
                    child=gl,
                    origin=Origin(xyz=(x, 0.05, top_z)),
                )
    elif r.rack_topology == "diamond_lattice":
        # Allocate the sampled global N into stable 2/3-bottle inverted-pyramid
        # piles distributed across the diamond cells.  One bottom bottle seats
        # at the V apex; the next two climb the left/right boards while touching
        # the bottom bottle.  This is the source-derived repeated-bottle rule
        # extended as bounded multiplicity -- no fake saddle/arm.
        _board_d, _board_cy = _full_depth_rack_board_span(r)
        bottle_y = _diamond_bottle_origin_y(r)
        cell_by_grid = {(col, row): cell for cell in diamond_cells for *_, col, row in [cell]}
        spread_order = (
            (1, 1),
            (0, 0),
            (2, 2),
            (2, 0),
            (0, 2),
            (1, 0),
            (1, 2),
            (0, 1),
            (2, 1),
        )
        ordered_cells = [cell_by_grid[key] for key in spread_order if key in cell_by_grid]
        active_cells = min(len(ordered_cells), max(1, math.ceil(r.bottle_count / 3.0)))
        base_count, remainder = divmod(r.bottle_count, active_cells)
        cell_counts = [base_count + (1 if i < remainder else 0) for i in range(active_cells)]
        if any(count < 1 or count > 3 for count in cell_counts):
            raise ValueError(f"diamond bottle distribution cannot realize N={r.bottle_count}")

        bottle_radius = 0.031
        # Seat neighbouring bottles with a 0.2 mm compression allowance so
        # tessellated cylinders form one supported static stack rather than
        # numerical 0.5 mm air gaps between nominally tangent bottles.
        bottle_pitch = 2.0 * bottle_radius - 0.0002
        placed = 0
        for stack_index, ((cx, cz, cw, ch, col, row), stack_count) in enumerate(
            zip(ordered_cells[:active_cells], cell_counts, strict=True)
        ):
            angle = math.atan2(ch, cw)
            support_names = (f"cell_{col}_{row}_slash", f"cell_{col}_{row}_backslash")
            bottom_origin_z = _diamond_bottle_origin_z(
                cz,
                angle,
                0.028,
                bottle_radius=bottle_radius,
            )
            bottle_world_origins = [(cx, bottle_y, bottom_origin_z)]
            side_signs = (-1.0, 1.0) if stack_count == 3 else (
                (-1.0,) if stack_index % 2 == 0 else (1.0,)
            )
            for side_sign in side_signs:
                bottle_world_origins.append(
                    (
                        cx + side_sign * bottle_pitch * math.cos(angle),
                        bottle_y,
                        bottom_origin_z + bottle_pitch * math.sin(angle),
                    )
                )

            # Rebase the stack part on its first bottom bottle's actual rack
            # contact.  The FIXED joint is therefore close to real geometry on
            # both parent and child, while every other bottle is local to it.
            stack_world_x, stack_world_y, stack_world_z = bottle_world_origins[0]
            bottle_origins = [
                (wx - stack_world_x, wy - stack_world_y, wz - stack_world_z)
                for wx, wy, wz in bottle_world_origins
            ]

            stack = model.part(
                f"rack_bottle_stack_{stack_index}",
                meta={
                    "contents": "horizontal wine bottle stack",
                    "bottle_units": stack_count,
                    "support_boards": support_names,
                    "neck_direction": "front",
                    "cell": (col, row),
                    "stack_count": stack_count,
                },
            )
            for local_index, (dx, dy, dz) in enumerate(bottle_origins):
                glass_key = "bottle_a" if placed % 2 == 0 else "bottle_b"
                _add_horizontal_bottle(
                    stack,
                    mats,
                    glass_key=glass_key,
                    name_prefix=f"bottle_{local_index}_",
                    xyz=(dx, dy, dz),
                    body_radius=bottle_radius,
                )
                placed += 1
            model.articulation(
                f"cabinet_to_rack_bottle_stack_{stack_index}",
                ArticulationType.FIXED,
                parent=cabinet,
                child=stack,
                origin=Origin(xyz=(stack_world_x, stack_world_y, stack_world_z)),
            )
        if placed != r.bottle_count:
            raise AssertionError(f"diamond rack emitted {placed} bottles, expected {r.bottle_count}")
    elif r.rack_topology == "horizontal_bar_rack":
        placed = 0
        rack_w = r.rack_x_max - r.rack_x_min - 0.04
        per_row = max(3, min(6, int(rack_w / 0.11)))
        # Bar Y positions (mirror _emit_rack_horizontal_bar): front bar at
        # y = r.D/4 - 0.05, back bar at y = -r.D/4. Anchor bottle joint origin
        # on the BACK bar's top surface so the bottle body + shoulder + neck
        # (extending +Y in the bottle's local frame; see _add_horizontal_bottle)
        # stays INSIDE the cabinet cavity (else neck+cork punch through the
        # door's glass panel at closed pose). Also keeps
        # fail_if_articulation_origin_far_from_geometry happy — the back bar
        # cylinder (radius 0.010, top at z=row_z) is right under the joint origin.
        back_bar_y = -r.D / 4.0
        bottle_support_y = back_bar_y + 0.012
        for row_z in bar_rows:
            for j in range(per_row):
                if placed >= r.bottle_count:
                    break
                x = r.rack_x_min + 0.05 + rack_w * (j + 0.5) / per_row
                bottle = model.part(f"bar_bottle_{placed}")
                glass_key = "bottle_a" if placed % 2 == 0 else "bottle_b"
                _add_horizontal_bottle(bottle, mats, glass_key=glass_key)
                _cbox(
                    cabinet,
                    (0.078, 0.050, 0.012),
                    (x, bottle_support_y, row_z + 0.006),
                    mats["dark_wood"],
                    f"bar_saddle_{placed}",
                )
                model.articulation(
                    f"cabinet_to_bar_bottle_{placed}",
                    ArticulationType.FIXED,
                    parent=cabinet,
                    child=bottle,
                    origin=Origin(xyz=(x, bottle_support_y, row_z + 0.012)),
                )
                placed += 1
            if placed >= r.bottle_count:
                break
    elif r.rack_topology == "vertical_peg_rack":
        for placed, (x, y, z_contact) in enumerate(peg_supports[: r.bottle_count]):
            bottle = model.part(f"peg_bottle_{placed}")
            glass_key = "bottle_a" if placed % 2 == 0 else "bottle_b"
            _add_horizontal_bottle(bottle, mats, glass_key=glass_key)
            model.articulation(
                f"cabinet_to_peg_bottle_{placed}",
                ArticulationType.FIXED,
                parent=cabinet,
                child=bottle,
                origin=Origin(xyz=(x, y, z_contact)),
            )
    elif r.rack_topology == "hybrid_display_rack":
        for placed, (kind, x, y, z_contact) in enumerate(
            hybrid_supports[: r.bottle_count]
        ):
            if kind == "upright":
                bottle = model.part(f"hybrid_upright_bottle_{placed}")
                _add_upright_bottle(
                    bottle,
                    mats,
                    glass_key="bottle_a" if placed % 2 == 0 else "bottle_b",
                )
            else:
                family = "rack" if kind == "rack" else "cooler"
                bottle = model.part(f"hybrid_{family}_bottle_{placed}")
                local_z_rebase = 0.003 if kind == "rack" else 0.0
                _add_horizontal_bottle(
                    bottle,
                    mats,
                    glass_key="bottle_a" if placed % 2 == 0 else "bottle_b",
                    xyz=(0.0, 0.0, local_z_rebase),
                )
                if kind == "rack":
                    # Move only the FIXED datum 3 mm toward the real V board and
                    # compensate in child-local geometry.  The bottle's world
                    # pose remains exactly tangent; no penetration/allowance is
                    # introduced, while both sides of the joint have nearby
                    # physical geometry on the shallowest admitted bay.
                    z_contact -= local_z_rebase
            model.articulation(
                f"cabinet_to_hybrid_bottle_{placed}",
                ArticulationType.FIXED,
                parent=cabinet,
                child=bottle,
                origin=Origin(xyz=(x, y, z_contact)),
            )


def build_seeded_wine_cabinet2(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_wine_cabinet2(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------
def run_wine_cabinet2_tests(
    object_model: ArticulatedObject,
    config: WineCabinet2Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    {j.name for j in object_model.articulations}
    cabinet = object_model.get_part("cabinet")

    # ---- Identity: cabinet is present, has bay/rack visuals. ----
    ctx.check("cabinet part present", "cabinet" in part_names)

    # ---- Door / drawer counts + joint types. ----
    door_joints = [
        j for j in object_model.articulations if j.name.startswith(("door_hinge_", "door_slide_"))
    ]
    drawer_joints = [j for j in object_model.articulations if j.name.startswith("drawer_slide_")]
    ctx.check(
        "door part count matches config",
        len([n for n in part_names if n.startswith("door_")]) == r.door_count,
        details=f"expected {r.door_count}",
    )
    expected_door_type = (
        ArticulationType.REVOLUTE
        if r.door_mechanism.startswith("swing_")
        else ArticulationType.PRISMATIC
    )
    ctx.check(
        "door joint type matches mechanism",
        len(door_joints) == r.door_count
        and all(j.articulation_type == expected_door_type for j in door_joints)
        and all(j.motion_limits is not None for j in door_joints),
    )
    ctx.check(
        "drawer joints PRISMATIC + slide along +Y",
        len(drawer_joints) == r.drawer_count
        and all(j.articulation_type == ArticulationType.PRISMATIC for j in drawer_joints)
        and all(tuple(abs(v) for v in j.axis) == (0.0, 1.0, 0.0) for j in drawer_joints),
    )
    if r.body_form == "built_in_wall" and r.door_mechanism == "swing_paneled":
        door_aabbs = [
            ctx.part_world_aabb(object_model.get_part(f"door_{i}"))
            for i in range(r.door_count)
        ]
        door_geometry_below_drawers = all(
            aabb is not None and aabb[1][2] <= r.drawer_band_bot + 0.004
            for aabb in door_aabbs
        )
        ctx.check(
            "built-in paneled facade preserves source lower-door/drawer/upper-rack zoning",
            door_geometry_below_drawers
            and r.door_bottom + r.door_height < r.drawer_band_bot
            and r.drawer_band_bot < r.drawer_band_top < r.rack_z_min,
            details=(
                f"door=[{r.door_bottom:.3f},{r.door_bottom + r.door_height:.3f}], "
                f"drawer=[{r.drawer_band_bot:.3f},{r.drawer_band_top:.3f}], "
                f"rack_min={r.rack_z_min:.3f}, door_aabbs={door_aabbs}"
            ),
        )

    # ---- Bottle capacity is exact, never an emitter-side truncation. ----
    bottle_parts = [p for p in object_model.parts if "bottle_" in p.name]
    emitted_bottle_count = sum(int(p.meta.get("bottle_units", 1)) for p in bottle_parts)
    fixed_bottles = [p.name for p in bottle_parts]
    ctx.check(
        "emitted bottle count matches resolved N",
        emitted_bottle_count == r.bottle_count,
        details=(
            f"requested={r.requested_bottle_count}, resolved={r.bottle_count}, "
            f"capacity={r.rack_capacity}, emitted={emitted_bottle_count}"
        ),
    )
    ctx.check(
        "resolved N respects body-rack capacity",
        BOTTLE_COUNT_MIN <= r.bottle_count <= r.rack_capacity,
        details=f"body={r.body_form}, rack={r.rack_topology}, capacity={r.rack_capacity}",
    )
    ctx.check(
        "bottle capacity contract recorded",
        object_model.meta.get("bottle_capacity_contract")
        == {
            "body_form": r.body_form,
            "rack_topology": r.rack_topology,
            "requested": r.requested_bottle_count,
            "resolved": r.bottle_count,
            "capacity": r.rack_capacity,
        },
    )
    if r.bottle_count == 20:
        ctx.check(
            "N=20 uses a validated high-capacity rack bundle",
            (
                r.rack_topology == "diamond_lattice"
                and emitted_bottle_count == 20
            )
            or (
                r.body_form == "modular_light_wood"
                and r.rack_topology == "hybrid_display_rack"
                and len([n for n in fixed_bottles if "hybrid_upright_bottle_" in n]) == 4
                and len([n for n in fixed_bottles if "hybrid_rack_bottle_" in n]) == 9
                and len([n for n in fixed_bottles if "hybrid_cooler_bottle_" in n]) == 7
            ),
        )

    if r.rack_topology == "diamond_lattice":
        stacks = [p for p in object_model.parts if p.name.startswith("rack_bottle_stack_")]
        cabinet_visual_names = {v.name for v in cabinet.visuals}
        fake_supports = {
            name
            for name in cabinet_visual_names
            if "diamond_saddle" in name or "diamond_support_arm" in name
        }
        ctx.check(
            "diamond rack uses full-depth V boards without forward fake supports",
            not fake_supports
            and all(
                (box := ctx.part_element_world_aabb(cabinet, elem=f"cell_{col}_{row}_slash"))
                is not None
                and box[1][1] - box[0][1] >= r.D - r.back_t - 0.07
                for col in range(3)
                for row in range(3)
            ),
            details=f"fake_supports={sorted(fake_supports)}",
        )
        ctx.check(
            "diamond N is distributed as per-cell inverted-pyramid multiplicity",
            sum(int(stack.meta.get("bottle_units", 0)) for stack in stacks) == r.bottle_count
            and all(int(stack.meta.get("stack_count", 0)) in {2, 3} for stack in stacks)
            and all(
                len([v for v in stack.visuals if v.name.endswith("bottle_body")])
                == int(stack.meta.get("stack_count", 0))
                for stack in stacks
            ),
            details=f"N={r.bottle_count}, stacks={[p.meta.get('stack_count') for p in stacks]}",
        )
        for stack in stacks:
            support_a, support_b = stack.meta["support_boards"]
            ctx.expect_contact(
                stack,
                cabinet,
                contact_tol=0.002,
                elem_a="bottle_0_bottle_body",
                elem_b=support_a,
                name=f"{stack.name} bottom bottle contacts first V board",
            )
            ctx.expect_contact(
                stack,
                cabinet,
                contact_tol=0.002,
                elem_a="bottle_0_bottle_body",
                elem_b=support_b,
                name=f"{stack.name} bottom bottle contacts second V board",
            )

    # ---- Mechanism structure: no whole-part allowances are declared. ----
    if expected_door_type == ArticulationType.REVOLUTE:
        for i in range(r.door_count):
            for hinge_index in range(2):
                ctx.allow_overlap(
                    f"door_{i}",
                    "cabinet",
                    elem_a=f"hinge_barrel_{hinge_index}",
                    elem_b=f"hinge_axle_{i}_{hinge_index}",
                    reason="coaxial cabinet axle passes through the captured door hinge barrel",
                )
    for i in range(r.drawer_count):
        drawer = object_model.get_part(f"drawer_{i}")
        visual_names = {v.name for v in drawer.visuals}
        ctx.check(
            f"drawer_{i} is a complete guided container",
            {
                "drawer_front",
                "drawer_bottom",
                "drawer_side_0",
                "drawer_side_1",
                "drawer_back",
                "drawer_glide_0",
                "drawer_glide_1",
            }.issubset(visual_names)
            and cabinet.get_visual(f"drawer_rail_{i}_0") is not None
            and cabinet.get_visual(f"drawer_rail_{i}_1") is not None,
        )

    # ---- Grounded silhouette. ----
    aabb = ctx.part_world_aabb(cabinet)
    if aabb is not None:
        (_, _, zmin), (_, _, zmax) = aabb
        ctx.check("cabinet rests near ground", zmin < 0.03, details=f"z_min={zmin:.4f}")
        ctx.check("cabinet is upright", (zmax - zmin) >= 1.3, details=f"height={zmax - zmin:.3f}")

    # ---- Targeted motion pose checks (Rule 5). ----
    if door_joints:
        j = door_joints[0]
        door = object_model.get_part("door_0")
        closed_aabb = ctx.part_world_aabb(door)
        target = float(j.motion_limits.upper or 0.0) * 0.6
        with ctx.pose({j: target}):
            open_aabb = ctx.part_world_aabb(door)
        if closed_aabb is not None and open_aabb is not None:
            if expected_door_type == ArticulationType.REVOLUTE:
                moved = open_aabb[1][1] > closed_aabb[1][1] + 0.05
                label = "door_0 swings forward (+Y)"
            else:
                moved = abs(open_aabb[0][0] - closed_aabb[0][0]) > 0.05
                label = "door_0 translates along its real track"
            ctx.check(label, moved, details=f"closed={closed_aabb} open={open_aabb}")
    if drawer_joints:
        j = drawer_joints[0]
        drawer = object_model.get_part("drawer_0")
        p0 = ctx.part_world_position(drawer)
        with ctx.pose({j: float(j.motion_limits.upper or 0.0) * 0.7}):
            p1 = ctx.part_world_position(drawer)
        if p0 is not None and p1 is not None:
            ctx.check(
                "drawer_0 slides forward (+Y)",
                p1[1] > p0[1] + 0.05,
                details=f"rest={p0}, extended={p1}",
            )
    if r.service_motion == "pull_out_tasting_shelf":
        tasting_joint = object_model.get_articulation("cabinet_to_tasting_shelf")
        tasting_part = object_model.get_part("tasting_shelf")
        p0 = ctx.part_world_position(tasting_part)
        with ctx.pose({tasting_joint: float(tasting_joint.motion_limits.upper or 0.0)}):
            p1 = ctx.part_world_position(tasting_part)
        ctx.check(
            "tasting shelf extends forward on bilateral guides",
            tasting_joint.articulation_type == ArticulationType.PRISMATIC
            and p0 is not None
            and p1 is not None
            and p1[1] > p0[1] + 0.15
            and cabinet.get_visual("tasting_track_0") is not None
            and cabinet.get_visual("tasting_track_1") is not None,
        )

    # ---- Baseline checks (motion sampled + islands + mating + origin). ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    # Multi-joint sampled sweep — capped at 32 for many-joint variants.
    sample_cap = 32 if (r.door_count + r.drawer_count) >= 5 else 64
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=sample_cap,
        ignore_fixed=True,
    )

    # ---- slot_choices persisted. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
    )
    return ctx.report()


__all__ = [
    "WineCabinet2Config",
    "ResolvedWineCabinet2Config",
    "build_wine_cabinet2",
    "build_seeded_wine_cabinet2",
    "config_from_seed",
    "resolve_config",
    "run_wine_cabinet2_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
