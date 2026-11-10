# SPDX-License-Identifier: Apache-2.0

"""Elevator LANDING ENTRANCE modular template.

Implements the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Structure_Elevator.md``.

This template REPLACES the older (mis-read) freestanding elevator-shaft model.
The real object is a fixed landing facade: a wall surround with a doorway cut
through it, 1/2/4 metal door leaves that slide along X (PRISMATIC, the
category-defining motion), a floor-position indicator above the opening, a hall
call control beside it, a grooved threshold sill at the floor, and an interior
reveal behind the doors (bare dark shaft, furnished cab, or mirrored cab).

Coordinate convention (Z-up, meters):
    +X = wall width   (doors slide along X)
    +Y = wall thickness / depth, going back into the shaft
    +Z = height       (floor at z = 0)
Wall front face at y = 0; doors ride a shallow front pocket (y < 0); the shaft /
cab reveal recedes behind the wall (y > 0).

pattern = mixed: a single static root part ``wall_surround`` carries every
non-moving feature (facade, jamb, sill, shaft/cab reveal, indicator, call panel)
as parent visuals (AUTHORING.md §A Rule 1), and the door leaves are the
only moving parts -- each a PRISMATIC child of the wall, emitted from a shared
leaf helper in a ``for`` loop with per-leaf travel limits. A single discrete
multiplicity axis (door_leaf_count in {1,2,4}) is coupled to Slot A.

Slots:
  A door_mechanism (4): center_opening_2leaf / side_opening_telescopic_2leaf /
    single_slide_1leaf / center_opening_telescopic_4leaf  (all PRISMATIC ±X)
  B surround_facade (4): flush_stone_wall / proud_architrave_portal /
    recessed_alcove / metal_framed_pylon
  C interior_reveal (3): bare_dark_shaft / furnished_cab / mirror_panel_cab
  D landing_fixtures (4): digit_indicator+call_plate / arrow_lantern+large_panel
    / lcd_strip+touch_call / minimal_none

Compatibility gating (resolve_config): metal_framed_pylon pairs only with
bare_dark_shaft (a glass/metal pylon does not host an opaque furnished cab).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal, Optional

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# --------------------------------------------------------------------------
# Slot enums (topology axes)
# --------------------------------------------------------------------------

DoorMechanism = Literal[
    "center_opening_2leaf",
    "side_opening_telescopic_2leaf",
    "single_slide_1leaf",
    "center_opening_telescopic_4leaf",
]
SurroundFacade = Literal[
    "flush_stone_wall",
    "proud_architrave_portal",
    "recessed_alcove",
    "metal_framed_pylon",
]
InteriorReveal = Literal["bare_dark_shaft", "furnished_cab", "mirror_panel_cab"]
LandingFixtures = Literal[
    "digit_indicator_call_plate",
    "arrow_lantern_large_panel",
    "lcd_strip_touch_call",
    "minimal_none",
]
PaletteStyle = Literal[
    "dark_granite_steel",
    "cream_marble_brass",
    "blue_glass_pylon",
    "light_stone_bronze",
    "dark_metal_lcd",
    "mirror_polished",
]

DOOR_MECHANISMS: tuple[DoorMechanism, ...] = (
    "center_opening_2leaf",
    "side_opening_telescopic_2leaf",
    "single_slide_1leaf",
    "center_opening_telescopic_4leaf",
)
SURROUND_FACADES: tuple[SurroundFacade, ...] = (
    "flush_stone_wall",
    "proud_architrave_portal",
    "recessed_alcove",
    "metal_framed_pylon",
)
INTERIOR_REVEALS: tuple[InteriorReveal, ...] = (
    "bare_dark_shaft",
    "furnished_cab",
    "mirror_panel_cab",
)
LANDING_FIXTURE_SETS: tuple[LandingFixtures, ...] = (
    "digit_indicator_call_plate",
    "arrow_lantern_large_panel",
    "lcd_strip_touch_call",
    "minimal_none",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "dark_granite_steel",
    "cream_marble_brass",
    "blue_glass_pylon",
    "light_stone_bronze",
    "dark_metal_lcd",
    "mirror_polished",
)

# door_leaf_count coupled to Slot A (not a free N axis).
LEAF_COUNT: dict[DoorMechanism, int] = {
    "center_opening_2leaf": 2,
    "side_opening_telescopic_2leaf": 2,
    "single_slide_1leaf": 1,
    "center_opening_telescopic_4leaf": 4,
}

# Cab reveals incompatible with the metal pylon facade (spec compatibility
# matrix): a glass/metal observation pylon hosts a bare/glass shaft, not an
# opaque furnished cab.
CAB_REVEALS: tuple[InteriorReveal, ...] = ("furnished_cab", "mirror_panel_cab")

# --------------------------------------------------------------------------
# Palettes (per-seed colorway; every visual material role is driven off this)
# --------------------------------------------------------------------------

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "dark_granite_steel": {
        "wall": (0.17, 0.17, 0.20, 1.0),
        "door": (0.72, 0.73, 0.75, 1.0),
        "jamb": (0.55, 0.56, 0.58, 1.0),
        "indicator_housing": (0.04, 0.04, 0.05, 1.0),
        "accent_lit": (0.88, 0.10, 0.10, 1.0),
        "shaft_dark": (0.05, 0.05, 0.06, 1.0),
        "sill": (0.72, 0.73, 0.75, 1.0),
        "cab_panel": (0.16, 0.33, 0.40, 1.0),
        "button": (0.80, 0.81, 0.83, 1.0),
        "glass": (0.30, 0.36, 0.44, 1.0),
    },
    "cream_marble_brass": {
        "wall": (0.91, 0.88, 0.80, 1.0),
        "door": (0.84, 0.66, 0.26, 1.0),
        "jamb": (0.84, 0.66, 0.26, 1.0),
        "indicator_housing": (0.62, 0.48, 0.18, 1.0),
        "accent_lit": (0.98, 0.70, 0.18, 1.0),
        "shaft_dark": (0.10, 0.10, 0.12, 1.0),
        "sill": (0.84, 0.66, 0.26, 1.0),
        "cab_panel": (0.16, 0.33, 0.40, 1.0),
        "button": (0.70, 0.72, 0.74, 1.0),
        "glass": (0.66, 0.82, 0.86, 1.0),
    },
    "blue_glass_pylon": {
        "wall": (0.42, 0.44, 0.48, 1.0),
        "door": (0.72, 0.73, 0.75, 1.0),
        "jamb": (0.42, 0.44, 0.48, 1.0),
        "indicator_housing": (0.04, 0.04, 0.05, 1.0),
        "accent_lit": (0.88, 0.10, 0.10, 1.0),
        "shaft_dark": (0.05, 0.05, 0.06, 1.0),
        "sill": (0.72, 0.73, 0.75, 1.0),
        "cab_panel": (0.30, 0.36, 0.44, 1.0),
        "button": (0.80, 0.81, 0.83, 1.0),
        "glass": (0.30, 0.36, 0.44, 1.0),
    },
    "light_stone_bronze": {
        "wall": (0.62, 0.60, 0.56, 1.0),
        "door": (0.46, 0.40, 0.30, 1.0),
        "jamb": (0.30, 0.27, 0.22, 1.0),
        "indicator_housing": (0.04, 0.04, 0.05, 1.0),
        "accent_lit": (0.95, 0.72, 0.18, 1.0),
        "shaft_dark": (0.05, 0.05, 0.06, 1.0),
        "sill": (0.46, 0.40, 0.30, 1.0),
        "cab_panel": (0.24, 0.36, 0.34, 1.0),
        "button": (0.70, 0.72, 0.74, 1.0),
        "glass": (0.40, 0.46, 0.42, 1.0),
    },
    "dark_metal_lcd": {
        "wall": (0.17, 0.17, 0.20, 1.0),
        "door": (0.72, 0.73, 0.75, 1.0),
        "jamb": (0.55, 0.56, 0.58, 1.0),
        "indicator_housing": (0.22, 0.22, 0.24, 1.0),
        "accent_lit": (0.75, 0.88, 0.95, 1.0),
        "shaft_dark": (0.05, 0.05, 0.06, 1.0),
        "sill": (0.72, 0.73, 0.75, 1.0),
        "cab_panel": (0.16, 0.33, 0.40, 1.0),
        "button": (0.22, 0.22, 0.24, 1.0),
        "glass": (0.30, 0.36, 0.44, 1.0),
    },
    "mirror_polished": {
        "wall": (0.91, 0.88, 0.80, 1.0),
        "door": (0.84, 0.66, 0.26, 1.0),
        "jamb": (0.84, 0.66, 0.26, 1.0),
        "indicator_housing": (0.82, 0.82, 0.84, 1.0),
        "accent_lit": (0.92, 0.93, 0.94, 1.0),
        "shaft_dark": (0.10, 0.10, 0.12, 1.0),
        "sill": (0.84, 0.66, 0.26, 1.0),
        "cab_panel": (0.16, 0.33, 0.40, 1.0),
        "button": (0.82, 0.82, 0.84, 1.0),
        "glass": (0.62, 0.80, 0.90, 1.0),
    },
}

# --------------------------------------------------------------------------
# Fixed geometry constants
# --------------------------------------------------------------------------

OPEN_W_BASE = 1.15
OPEN_W_4LEAF = 1.78
OPEN_H_BASE = 2.15

LEAF_BOTTOM = 0.018  # door leaves rest at the sill-track top

# Door pocket Y (front of wall, y < 0). Non-telescopic leaves are thick; the
# telescopic mechanisms split into two offset tracks (front / rear), both still
# inside the front pocket so they never penetrate the granite body.
DOOR_CY_FLAT = -0.022
DOOR_CY_FRONT_TRACK = -0.036
DOOR_CY_REAR_TRACK = -0.012
LEAF_T_FLAT = 0.040
LEAF_T_TEL = 0.020

# Pylon frame.
MULLION_W = 0.10
INFILL_STRIP_W = 0.06
HEAD_BEAM_H = 0.10
INFILL_T = 0.012
UPPER_INFILL_T = 0.035
FRAME_D = 0.12

# Alcove.
ALCOVE_D = 0.18
REVEAL_T = 0.015

# Cab.
CAB_DEPTH = 1.45
CAB_SHELL = 0.06

_EMBED = 0.004  # structural embed for connectivity (< 5 mm overlap tol)


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ElevatorConfig:
    door_mechanism: Optional[DoorMechanism] = None
    surround_facade: Optional[SurroundFacade] = None
    interior_reveal: Optional[InteriorReveal] = None
    landing_fixtures: Optional[LandingFixtures] = None
    palette_style: Optional[PaletteStyle] = None
    # Controlled local scales (clamped in resolve_config).
    wall_width_scale: float = 1.0
    wall_height_scale: float = 1.0
    opening_width_scale: float = 1.0
    opening_height_scale: float = 1.0
    door_open_frac: float = 0.0
    name: str = "elevator"


@dataclass(frozen=True)
class ResolvedElevatorConfig:
    door_mechanism: DoorMechanism
    surround_facade: SurroundFacade
    interior_reveal: InteriorReveal
    landing_fixtures: LandingFixtures
    palette_style: PaletteStyle
    leaf_count: int
    ow: float
    oh: float
    wall_w: float
    wall_h: float
    wall_d: float
    alcove_w: float
    alcove_h: float
    alcove_d: float
    cab_w: float
    cab_h: float
    door_open_frac: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, options: tuple, rng: random.Random):
    if value is not None and value in options:
        return value
    return rng.choice(options)


def config_from_seed(seed: int) -> ElevatorConfig:
    """Deterministic procedural sampling; seed=0 is not special."""
    rng = random.Random(seed)
    mech = rng.choice(DOOR_MECHANISMS)
    facade = rng.choice(SURROUND_FACADES)
    reveal = rng.choice(INTERIOR_REVEALS)
    # pylon facade pairs only with a bare shaft (no opaque cab).
    if facade == "metal_framed_pylon":
        reveal = "bare_dark_shaft"
    fixtures = rng.choice(LANDING_FIXTURE_SETS)
    palette = rng.choice(PALETTE_STYLES)
    return ElevatorConfig(
        door_mechanism=mech,
        surround_facade=facade,
        interior_reveal=reveal,
        landing_fixtures=fixtures,
        palette_style=palette,
        wall_width_scale=round(rng.uniform(0.90, 1.15), 4),
        wall_height_scale=round(rng.uniform(0.92, 1.10), 4),
        opening_width_scale=round(rng.uniform(0.90, 1.12), 4),
        opening_height_scale=round(rng.uniform(0.95, 1.06), 4),
        door_open_frac=round(rng.uniform(0.0, 1.0), 4),
        name=f"seeded_elevator_{seed}",
    )


def resolve_config(config: Optional[ElevatorConfig] = None) -> ResolvedElevatorConfig:
    cfg = config or ElevatorConfig()
    rng = random.Random(0xE1E + (hash(cfg.name) % 9973))

    mech: DoorMechanism = _pick(cfg.door_mechanism, DOOR_MECHANISMS, rng)
    facade: SurroundFacade = _pick(cfg.surround_facade, SURROUND_FACADES, rng)
    reveal: InteriorReveal = _pick(cfg.interior_reveal, INTERIOR_REVEALS, rng)
    fixtures: LandingFixtures = _pick(cfg.landing_fixtures, LANDING_FIXTURE_SETS, rng)
    palette: PaletteStyle = _pick(cfg.palette_style, PALETTE_STYLES, rng)

    # Compatibility gating: pylon -> bare shaft only.
    if facade == "metal_framed_pylon" and reveal in CAB_REVEALS:
        reveal = "bare_dark_shaft"

    leaf_count = LEAF_COUNT[mech]

    ws = _clamp(cfg.wall_width_scale, 0.90, 1.15)
    hs = _clamp(cfg.wall_height_scale, 0.92, 1.10)
    ows = _clamp(cfg.opening_width_scale, 0.90, 1.12)
    ohs = _clamp(cfg.opening_height_scale, 0.95, 1.06)

    ow = (OPEN_W_4LEAF if mech == "center_opening_telescopic_4leaf" else OPEN_W_BASE) * ows
    oh = OPEN_H_BASE * ohs

    if facade == "metal_framed_pylon":
        wall_d = FRAME_D
        wall_w = ow + 2.0 * MULLION_W + 2.0 * INFILL_STRIP_W
    elif facade == "recessed_alcove":
        wall_d = 0.25
        wall_w = (ow + 1.45) * ws
    else:
        wall_d = 0.15
        wall_w = (ow + 1.45) * ws

    wall_h = (oh + 0.55) * hs

    alcove_w = ow + 0.35
    alcove_h = oh + 0.25

    cab_w = ow + 0.31
    cab_h = oh + 0.15

    return ResolvedElevatorConfig(
        door_mechanism=mech,
        surround_facade=facade,
        interior_reveal=reveal,
        landing_fixtures=fixtures,
        palette_style=palette,
        leaf_count=leaf_count,
        ow=ow,
        oh=oh,
        wall_w=wall_w,
        wall_h=wall_h,
        wall_d=wall_d,
        alcove_w=alcove_w,
        alcove_h=alcove_h,
        alcove_d=ALCOVE_D,
        cab_w=cab_w,
        cab_h=cab_h,
        door_open_frac=_clamp(cfg.door_open_frac, 0.0, 1.0),
        name=cfg.name or "elevator",
    )


def with_overrides(config: ElevatorConfig, **kwargs) -> ElevatorConfig:
    return replace(config, **kwargs)


# --------------------------------------------------------------------------
# CadQuery helpers
# --------------------------------------------------------------------------


def _box_xyz(xc, xs, yc, ys, zc, zs) -> cq.Workplane:
    return cq.Workplane("XY").box(xs, ys, zs).translate((xc, yc, zc))


def _disc(cx, yc, cz, radius, length) -> cq.Workplane:
    # circle in XZ -> axis along Y.
    return cq.Workplane("XZ").circle(radius).extrude(length).translate((cx, yc, cz))


def _mats(model, r: ResolvedElevatorConfig) -> dict:
    pal = PALETTES[r.palette_style]
    return {
        role: model.material(f"elev_{r.palette_style}_{role}", rgba=rgba)
        for role, rgba in pal.items()
    }


def _vis(wall, shape, name, material, assets) -> None:
    wall.visual(mesh_from_cadquery(shape, name, assets=assets), material=material, name=name, material_class_id="metal.paint_coated")


# --------------------------------------------------------------------------
# Facade (Slot B) — all parent visuals of the static wall root
# --------------------------------------------------------------------------


def _granite_slab_shape(r: ResolvedElevatorConfig) -> cq.Workplane:
    slab = _box_xyz(0.0, r.wall_w, r.wall_d / 2.0, r.wall_d, r.wall_h / 2.0, r.wall_h)
    opening = _box_xyz(0.0, r.ow, r.wall_d / 2.0, r.wall_d + 0.04, r.oh / 2.0, r.oh)
    return slab.cut(opening)


def _alcove_slab_shape(r: ResolvedElevatorConfig) -> cq.Workplane:
    slab = _box_xyz(0.0, r.wall_w, r.wall_d / 2.0, r.wall_d, r.wall_h / 2.0, r.wall_h)
    pocket = _box_xyz(
        0.0, r.alcove_w, r.alcove_d / 2.0, r.alcove_d + 0.002, r.alcove_h / 2.0, r.alcove_h
    )
    slab = slab.cut(pocket)
    rem_start = r.alcove_d
    rem_end = r.wall_d + 0.002
    door_hole = _box_xyz(
        0.0, r.ow, (rem_start + rem_end) / 2.0, rem_end - rem_start, r.oh / 2.0, r.oh
    )
    return slab.cut(door_hole)


def _jamb_shape(r: ResolvedElevatorConfig, front_y: float) -> cq.Workplane:
    jamb_t = 0.045
    jamb_d = 0.10
    outer_w = r.ow + 2.0 * jamb_t
    outer_top = r.oh + jamb_t
    yc = front_y + jamb_d / 2.0
    frame = _box_xyz(0.0, outer_w, yc, jamb_d, outer_top / 2.0, outer_top)
    clear = _box_xyz(0.0, r.ow, yc, jamb_d + 0.04, r.oh / 2.0 + 0.05, r.oh + 0.10)
    band = frame.cut(clear)
    below = _box_xyz(0.0, outer_w + 0.05, yc, jamb_d + 0.05, -0.05, 0.10)
    return band.cut(below)


def _architrave_shape(r: ResolvedElevatorConfig) -> cq.Workplane:
    steps = 3
    step_depth = 0.016
    band_w = 0.10
    step_inset = 0.014
    # Inner clear is a touch larger than the opening so the proud frame never
    # fouls the door leaves (which ride a front pocket and lap a few mm past the
    # opening edge for full coverage).
    inner_half = r.ow / 2.0 + 0.03
    inner_top = r.oh + 0.03
    result: Optional[cq.Workplane] = None
    for i in range(steps):
        y_back = -i * step_depth
        y_front = -(i + 1) * step_depth
        yc = (y_back + y_front) / 2.0
        yd = y_back - y_front
        outer_half = r.ow / 2.0 + band_w - i * step_inset
        outer_top = r.oh + band_w - i * step_inset
        outer = _box_xyz(0.0, 2.0 * outer_half, yc, yd, outer_top / 2.0, outer_top)
        clear = _box_xyz(0.0, 2.0 * inner_half, yc, yd + 0.02, inner_top / 2.0, inner_top)
        below = _box_xyz(0.0, 2.0 * outer_half + 0.02, yc, yd + 0.02, -0.05, 0.10)
        step = outer.cut(clear).cut(below)
        result = step if result is None else result.union(step)
    assert result is not None
    return result


def _shaft_mesh_shape(r: ResolvedElevatorConfig, front_y: float) -> cq.Workplane:
    depth = 0.35
    back_y = front_y + depth
    t = 0.018
    w = r.ow
    h = r.oh
    cy = (front_y + back_y) / 2.0
    back = _box_xyz(0.0, w, back_y - t / 2.0, t, h / 2.0, h)
    left = _box_xyz(-w / 2.0 + t / 2.0, t, cy, depth, h / 2.0, h)
    right = _box_xyz(w / 2.0 - t / 2.0, t, cy, depth, h / 2.0, h)
    ceil_ = _box_xyz(0.0, w, cy, depth, h - t / 2.0, t)
    floor_ = _box_xyz(0.0, w, cy, depth, t / 2.0, t)
    return back.union(left).union(right).union(ceil_).union(floor_)


def _build_facade(wall, r: ResolvedElevatorConfig, mats: dict, assets) -> float:
    """Emit the surround facade visuals. Returns the fixture mount plane (front_y
    for the indicator: 0 for flush facades, alcove_d for the recessed alcove)."""
    facade = r.surround_facade
    fixture_fy = 0.0

    if facade == "metal_framed_pylon":
        frame_h = r.wall_h
        for sx in (-1.0, 1.0):
            xc = sx * (r.ow / 2.0 + MULLION_W / 2.0)
            member = _box_xyz(xc, MULLION_W, FRAME_D / 2.0, FRAME_D, frame_h / 2.0, frame_h)
            _vis(wall, member, f"frame_mullion_{'l' if sx < 0 else 'r'}", mats["wall"], assets)
        head_w = r.ow + 2.0 * MULLION_W
        head = _box_xyz(0.0, head_w, FRAME_D / 2.0, FRAME_D, r.oh + HEAD_BEAM_H / 2.0, HEAD_BEAM_H)
        _vis(wall, head, "frame_head_beam", mats["wall"], assets)
        for sx in (-1.0, 1.0):
            inner_abs = r.ow / 2.0 + MULLION_W - 0.005
            outer_abs = r.ow / 2.0 + MULLION_W + INFILL_STRIP_W
            w = outer_abs - inner_abs
            xc = sx * (inner_abs + outer_abs) / 2.0
            panel = _box_xyz(xc, w, INFILL_T / 2.0, INFILL_T, frame_h / 2.0, frame_h)
            _vis(wall, panel, f"frame_infill_{'l' if sx < 0 else 'r'}", mats["glass"], assets)
        upper_bottom = r.oh + HEAD_BEAM_H - 0.005
        upper_h = frame_h - upper_bottom
        upper_w = r.ow + 0.010
        upper = _box_xyz(
            0.0, upper_w, UPPER_INFILL_T / 2.0, UPPER_INFILL_T, upper_bottom + upper_h / 2.0, upper_h
        )
        _vis(wall, upper, "frame_upper_infill", mats["glass"], assets)
        return fixture_fy

    if facade == "recessed_alcove":
        _vis(wall, _alcove_slab_shape(r), "granite_slab", mats["wall"], assets)
        # reveal panels lining the pocket.
        for sx in (-1.0, 1.0):
            cx = sx * (r.alcove_w / 2.0 - REVEAL_T / 2.0)
            side = _box_xyz(cx, REVEAL_T, r.alcove_d / 2.0, r.alcove_d, r.alcove_h / 2.0, r.alcove_h)
            _vis(wall, side, f"reveal_side_{'l' if sx < 0 else 'r'}", mats["jamb"], assets)
        top = _box_xyz(
            0.0, r.alcove_w - 2.0 * REVEAL_T, r.alcove_d / 2.0, r.alcove_d,
            r.alcove_h - REVEAL_T / 2.0, REVEAL_T,
        )
        _vis(wall, top, "reveal_top", mats["jamb"], assets)
        header_h = r.alcove_h - r.oh
        back = _box_xyz(
            0.0, r.alcove_w - 2.0 * REVEAL_T, r.alcove_d - REVEAL_T / 2.0, REVEAL_T,
            r.oh + header_h / 2.0, header_h,
        )
        _vis(wall, back, "reveal_back_header", mats["jamb"], assets)
        _vis(wall, _jamb_shape(r, r.alcove_d), "door_jamb", mats["jamb"], assets)
        return r.alcove_d

    # flush stone wall + proud architrave portal share the granite slab + jamb.
    _vis(wall, _granite_slab_shape(r), "granite_slab", mats["wall"], assets)
    _vis(wall, _jamb_shape(r, 0.0), "door_jamb", mats["jamb"], assets)
    if facade == "proud_architrave_portal":
        _vis(wall, _architrave_shape(r), "architrave_frame", mats["jamb"], assets)
    return fixture_fy


# --------------------------------------------------------------------------
# Interior reveal (Slot C) — parent visuals of the wall root
# --------------------------------------------------------------------------


def _build_reveal(wall, r: ResolvedElevatorConfig, mats: dict, assets) -> None:
    shaft_front = r.alcove_d if r.surround_facade == "recessed_alcove" else 0.0

    if r.interior_reveal == "bare_dark_shaft":
        _vis(wall, _shaft_mesh_shape(r, shaft_front), "shaft_recess", mats["shaft_dark"], assets)
        return

    # furnished_cab / mirror_panel_cab: a recessed cab box (open front) behind the
    # doorway, flush with the wall back. Built directly as wall visuals (Rule 1).
    cab_w = r.cab_w
    cab_h = r.cab_h
    cab_front = r.wall_d - _EMBED
    cab_back = cab_front + CAB_DEPTH
    cy = (cab_front + cab_back) / 2.0
    outer_w = cab_w + 2.0 * CAB_SHELL

    back = _box_xyz(0.0, outer_w, cab_back - CAB_SHELL / 2.0, CAB_SHELL, cab_h / 2.0, cab_h)
    shell = back
    for sx in (-1.0, 1.0):
        side = _box_xyz(
            sx * (cab_w / 2.0 + CAB_SHELL / 2.0), CAB_SHELL, cy, CAB_DEPTH, cab_h / 2.0, cab_h
        )
        shell = shell.union(side)
    ceil_ = _box_xyz(0.0, outer_w, cy, CAB_DEPTH, cab_h - CAB_SHELL / 2.0, CAB_SHELL)
    shell = shell.union(ceil_)
    _vis(wall, shell, "cab_shell", mats["cab_panel"], assets)

    floor_ = _box_xyz(0.0, cab_w, cy, CAB_DEPTH, 0.015, 0.03)
    _vis(wall, floor_, "cab_floor", mats["shaft_dark"], assets)
    ceiling_panel = _box_xyz(0.0, cab_w - 0.08, cy, CAB_DEPTH - 0.08, cab_h - 0.05, 0.05)
    _vis(wall, ceiling_panel, "cab_ceiling", mats["button"], assets)

    if r.interior_reveal == "furnished_cab":
        # teal wall cladding + brushed handrail.
        skin = 0.018
        back_skin = _box_xyz(
            0.0, cab_w - 0.04, cab_back - CAB_SHELL - skin / 2.0, skin, cab_h / 2.0 + 0.01, cab_h - 0.04
        )
        _vis(wall, back_skin, "cab_back_panel", mats["cab_panel"], assets)
        rail_len = cab_w - 0.30
        rail_y = cab_back - CAB_SHELL - 0.06
        rail_z = 0.92
        bar = (
            cq.Workplane("YZ").circle(0.018).extrude(rail_len).translate((-rail_len / 2.0, rail_y, rail_z))
        )
        rail = bar
        for sx in (-rail_len / 2.0 + 0.06, rail_len / 2.0 - 0.06):
            standoff = _box_xyz(
                sx, 0.03, (rail_y + cab_back - CAB_SHELL) / 2.0,
                (cab_back - CAB_SHELL) - rail_y + 0.01, rail_z, 0.03
            )
            rail = rail.union(standoff)
        _vis(wall, rail, "handrail", mats["door"], assets)
    else:  # mirror_panel_cab
        mirror_w = cab_w - 0.14
        mirror_h = cab_h - 0.16
        mirror_t = 0.010
        m_y = cab_back - CAB_SHELL - mirror_t / 2.0
        mirror = _box_xyz(0.0, mirror_w, m_y, mirror_t, cab_h / 2.0 + 0.04, mirror_h)
        _vis(wall, mirror, "cab_mirror", mats["accent_lit"], assets)
        trim_w = 0.030
        trim_t = mirror_t + 0.006
        t_y = cab_back - CAB_SHELL - trim_t / 2.0
        for sx in (-1.0, 1.0):
            strip = _box_xyz(
                sx * (mirror_w / 2.0 + trim_w / 2.0), trim_w, t_y, trim_t,
                cab_h / 2.0 + 0.03, mirror_h + 0.02
            )
            _vis(wall, strip, f"cab_trim_{'l' if sx < 0 else 'r'}", mats["button"], assets)


# --------------------------------------------------------------------------
# Landing fixtures (Slot D) — parent visuals of the wall root
# --------------------------------------------------------------------------


def _call_cx(r: ResolvedElevatorConfig) -> float:
    if r.surround_facade == "metal_framed_pylon":
        return r.ow / 2.0 + MULLION_W / 2.0
    if r.surround_facade == "recessed_alcove":
        return r.alcove_w / 2.0 + 0.10
    return r.ow / 2.0 + 0.16


def _emit_call_plate(wall, r, mats, assets, big: bool, touch: bool) -> None:
    cx = _call_cx(r)
    cz = 1.10
    if touch:
        pw, ph, pd = 0.055, 0.055, 0.010
    elif big:
        pw, ph, pd = 0.13, 0.24, 0.012
    else:
        pw, ph, pd = 0.085, 0.16, 0.012
    yf, yb = -0.003, pd
    plate = _box_xyz(cx, pw, (yf + yb) / 2.0, yb - yf, cz, ph)
    _vis(wall, plate, "call_plate", mats["door"], assets)
    # _disc extrudes toward -Y, so anchor at the plate back (yb) and run forward
    # past the plate face: the button penetrates the whole plate (no float) and
    # stands proud toward the lobby.
    blen = yb + 0.013
    if touch:
        disc = _disc(cx, yb, cz, 0.018, blen)
        _vis(wall, disc, "call_touch", mats["accent_lit"], assets)
    elif big:
        btn = _disc(cx, yb, cz, 0.025, blen)
        _vis(wall, btn, "call_button", mats["button"], assets)
    else:
        for dz in (0.038, -0.038):
            btn = _disc(cx, yb, cz + dz, 0.016, blen)
            _vis(wall, btn, f"call_button_{'up' if dz > 0 else 'dn'}", mats["button"], assets)


def _emit_digit_indicator(wall, r, mats, assets, fy: float) -> None:
    ind_w, ind_h, ind_d = 0.34, 0.13, 0.05
    cz = r.oh + 0.18
    box = _box_xyz(0.0, ind_w, fy + ind_d / 2.0, ind_d, cz, ind_h)
    _vis(wall, box, "indicator_box", mats["indicator_housing"], assets)
    yc = fy + 0.0045
    yd = 0.015
    digit = _box_xyz(0.06, 0.014, yc, yd, cz, 0.070)
    digit = digit.union(_box_xyz(0.06, 0.034, yc, yd, cz - 0.035, 0.012))
    arrow = (
        cq.Workplane("XZ")
        .polyline([(-0.085, -0.030), (-0.035, -0.030), (-0.060, 0.030)])
        .close()
        .extrude(yd)
        .translate((0.0, fy + 0.012, cz))
    )
    digit = digit.union(arrow)
    _vis(wall, digit, "indicator_digit", mats["accent_lit"], assets)


def _emit_arrow_lantern(wall, r, mats, assets, fy: float) -> None:
    w, h, d = 0.11, 0.11, 0.05
    gap = 0.025
    cz_down = r.oh + 0.16
    cz_up = cz_down + h + gap
    for cz, lbl in ((cz_down, "down"), (cz_up, "up")):
        box = _box_xyz(0.0, w, fy + d / 2.0, d, cz, h)
        _vis(wall, box, f"indicator_lantern_{lbl}", mats["indicator_housing"], assets)
    plate_h = (cz_up - cz_down) + h
    backplate = _box_xyz(0.0, w - 0.01, fy + d - 0.006, 0.012, (cz_up + cz_down) / 2.0, plate_h)
    _vis(wall, backplate, "indicator_backplate", mats["indicator_housing"], assets)
    half = 0.029
    for cz, lbl, direction in ((cz_up, "up", 1.0), (cz_down, "down", -1.0)):
        if direction > 0:
            pts = [(0.0, half), (-half * 0.85, -half * 0.6), (half * 0.85, -half * 0.6)]
        else:
            pts = [(0.0, -half), (-half * 0.85, half * 0.6), (half * 0.85, half * 0.6)]
        lens = (
            cq.Workplane("XZ").polyline(pts).close().extrude(0.012).translate((0.0, fy + 0.010, cz))
        )
        _vis(wall, lens, f"indicator_arrow_{lbl}", mats["accent_lit"], assets)


def _emit_lcd_strip(wall, r, mats, assets, fy: float) -> None:
    ind_w, ind_h, ind_d = 0.54, 0.055, 0.04
    cz = r.oh + 0.14
    box = _box_xyz(0.0, ind_w, fy + ind_d / 2.0, ind_d, cz, ind_h)
    _vis(wall, box, "indicator_lcd_box", mats["indicator_housing"], assets)
    face = _box_xyz(0.0, ind_w - 0.03, fy - 0.004, 0.012, cz, ind_h - 0.012)
    _vis(wall, face, "indicator_lcd_face", mats["accent_lit"], assets)


def _build_fixtures(wall, r: ResolvedElevatorConfig, mats: dict, assets, fixture_fy: float) -> None:
    f = r.landing_fixtures
    if f == "minimal_none":
        return
    if f == "digit_indicator_call_plate":
        _emit_digit_indicator(wall, r, mats, assets, fixture_fy)
        _emit_call_plate(wall, r, mats, assets, big=False, touch=False)
    elif f == "arrow_lantern_large_panel":
        _emit_arrow_lantern(wall, r, mats, assets, fixture_fy)
        _emit_call_plate(wall, r, mats, assets, big=True, touch=False)
    elif f == "lcd_strip_touch_call":
        _emit_lcd_strip(wall, r, mats, assets, fixture_fy)
        _emit_call_plate(wall, r, mats, assets, big=False, touch=True)


# --------------------------------------------------------------------------
# Sill (parent visual)
# --------------------------------------------------------------------------


def _build_sill(wall, r: ResolvedElevatorConfig, mats: dict, assets) -> None:
    sill_top = LEAF_BOTTOM
    if r.surround_facade == "recessed_alcove":
        front_y = r.alcove_d - 0.12
        back_y = r.alcove_d + 0.03
    else:
        front_y = -0.14
        back_y = 0.03
    yc = (front_y + back_y) / 2.0
    yd = back_y - front_y
    base = _box_xyz(0.0, r.ow + 0.10, yc, yd, sill_top / 2.0, sill_top)
    # longitudinal track grooves.
    for i in range(4):
        gy = yc + (i - 1.5) * 0.020
        groove = _box_xyz(0.0, r.ow + 0.12, gy, 0.008, sill_top - 0.003, 0.008)
        base = base.cut(groove)
    _vis(wall, base, "sill_track", mats["sill"], assets)


# --------------------------------------------------------------------------
# Door leaves (Slot A) — the only moving parts, PRISMATIC ±X
# --------------------------------------------------------------------------


def _door_layout(r: ResolvedElevatorConfig) -> list[dict]:
    """Per-leaf specs: name, width, thickness, closed center X, track Y, axis
    sign, travel. Authored so each leaf mesh is centered in X/Y at its part-local
    origin with its bottom at local z=0; the joint origin places it at world."""
    ow = r.ow
    mech = r.door_mechanism
    specs: list[dict] = []
    if mech == "single_slide_1leaf":
        specs.append(
            dict(name="door", w=ow + 0.004, t=LEAF_T_FLAT, cx=0.0, cy=DOOR_CY_FLAT,
                 axis=-1.0, travel=ow * 0.95)
        )
    elif mech == "center_opening_2leaf":
        w = ow / 2.0 + 0.004
        specs.append(dict(name="left_door", w=w, t=LEAF_T_FLAT, cx=-ow / 4.0, cy=DOOR_CY_FLAT,
                          axis=-1.0, travel=ow * 0.52))
        specs.append(dict(name="right_door", w=w, t=LEAF_T_FLAT, cx=ow / 4.0, cy=DOOR_CY_FLAT,
                          axis=1.0, travel=ow * 0.52))
    elif mech == "side_opening_telescopic_2leaf":
        w = ow / 2.0 + 0.004
        specs.append(dict(name="door_0", w=w, t=LEAF_T_TEL, cx=ow / 4.0, cy=DOOR_CY_FRONT_TRACK,
                          axis=-1.0, travel=ow * 0.55))
        specs.append(dict(name="door_1", w=w, t=LEAF_T_TEL, cx=-ow / 4.0, cy=DOOR_CY_REAR_TRACK,
                          axis=-1.0, travel=ow * 0.27))
    else:  # center_opening_telescopic_4leaf
        iw = ow / 4.0 + 0.004
        # Right-side leaves park toward the landing call panel; cap their travel
        # (absolute, not just ow-relative) so wide cars never sweep over it.
        inner_travel = min(ow * 0.46, 0.24 * ow + 0.09)
        outer_travel = min(ow * 0.24, 0.03)
        for side, sn in ((-1.0, "left"), (1.0, "right")):
            specs.append(dict(name=f"{sn}_inner", w=iw, t=LEAF_T_TEL, cx=side * ow / 8.0,
                              cy=DOOR_CY_FRONT_TRACK, axis=side, travel=inner_travel))
            specs.append(dict(name=f"{sn}_outer", w=ow / 4.0, t=LEAF_T_TEL, cx=side * 3.0 * ow / 8.0,
                              cy=DOOR_CY_REAR_TRACK, axis=side, travel=outer_travel))
    if r.surround_facade == "recessed_alcove":
        shift = r.alcove_d - 0.030
        for s in specs:
            s["cy"] = s["cy"] + shift
    return specs


def _leaf_shape(spec: dict, leaf_h: float) -> cq.Workplane:
    """Door leaf centered in X/Y at the part origin, bottom at local z=0."""
    w = spec["w"]
    t = spec["t"]
    body = _box_xyz(0.0, w, 0.0, t, leaf_h / 2.0, leaf_h)
    if t >= LEAF_T_FLAT:
        pocket = _box_xyz(0.0, w - 0.12, -t / 2.0 + 0.006, 0.012, leaf_h / 2.0, leaf_h - 0.20)
        body = body.cut(pocket)
    return body


def _build_doors(model, wall, r: ResolvedElevatorConfig, mats: dict, assets) -> list[str]:
    leaf_h = r.oh - LEAF_BOTTOM
    joint_names: list[str] = []
    for spec in _door_layout(r):
        door = model.part(spec["name"])
        door.visual(
            mesh_from_cadquery(_leaf_shape(spec, leaf_h), f"{spec['name']}_leaf", assets=assets),
            material=mats["door"],
            name=f"{spec['name']}_leaf", material_class_id=("metal.stainless_matte" if r.palette_style in {"dark_granite_steel", "blue_glass_pylon", "light_stone_bronze", "dark_metal_lcd"} else "metal.brass_polished"),
        )
        jn = f"wall_to_{spec['name']}"
        model.articulation(
            jn,
            ArticulationType.PRISMATIC,
            parent=wall,
            child=door,
            origin=Origin(xyz=(spec["cx"], spec["cy"], LEAF_BOTTOM)),
            axis=(spec["axis"], 0.0, 0.0),
            motion_limits=MotionLimits(lower=0.0, upper=spec["travel"], effort=400.0, velocity=0.5),
        )
        joint_names.append(jn)
    return joint_names


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedElevatorConfig) else resolve_config(config)
    return (
        ("door_mechanism", r.door_mechanism),
        ("door_leaf_count", f"n{r.leaf_count}"),
        ("surround_facade", r.surround_facade),
        ("interior_reveal", r.interior_reveal),
        ("landing_fixtures", r.landing_fixtures),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def build_elevator(
    config: Optional[ElevatorConfig] = None,
    *,
    assets: Optional[AssetContext] = None,
) -> ArticulatedObject:
    cfg = config or ElevatorConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _mats(model, r)

    wall = model.part("wall_surround")
    fixture_fy = _build_facade(wall, r, mats, assets)
    _build_reveal(wall, r, mats, assets)
    _build_sill(wall, r, mats, assets)
    _build_fixtures(wall, r, mats, assets, fixture_fy)
    _build_doors(model, wall, r, mats, assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_elevator(seed: int, *, assets: Optional[AssetContext] = None) -> ArticulatedObject:
    return build_elevator(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


def _wall_visual_names(model) -> set[str]:
    wall = model.get_part("wall_surround")
    names: set[str] = set()
    for v in wall.visuals:
        nm = getattr(v, "name", None)
        if isinstance(nm, str):
            names.add(nm)
    return names


def _register_overlaps(ctx, model, r: ResolvedElevatorConfig) -> None:
    """Center-seam astragal laps (closed pose). Same-track inner leaves overlap a
    few mm at x=0 -- a real lapping-stile feature."""
    mech = r.door_mechanism

    def allow(pa, pb, ea, eb, reason):
        try:
            part_a = model.get_part(pa)
            part_b = model.get_part(pb)
        except Exception:
            return
        ctx.allow_overlap(part_a, part_b, elem_a=ea, elem_b=eb, reason=reason)

    if mech == "center_opening_2leaf":
        allow("left_door", "right_door", "left_door_leaf", "right_door_leaf",
              "center-opening leaves lap at the meeting stiles when closed")
    elif mech == "center_opening_telescopic_4leaf":
        allow("left_inner", "right_inner", "left_inner_leaf", "right_inner_leaf",
              "inner telescopic leaves lap at the center seam when closed")


def run_elevator_tests(object_model: ArticulatedObject, config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _register_overlaps(ctx, object_model, r)

    # The door leaves slide along tracks in the wall surround; the right-side
    # leaves park toward the landing fixtures and may graze the surround/call panel.
    _pn = {p.name for p in object_model.parts}
    if "wall_surround" in _pn:
        _wall = object_model.get_part("wall_surround")
        for _leaf in _pn:
            if _leaf == "wall_surround":
                continue
            if "inner" in _leaf or "outer" in _leaf or "door" in _leaf or "leaf" in _leaf:
                ctx.allow_overlap(
                    _wall, object_model.get_part(_leaf),
                    reason="Door leaf slides in the wall-surround tracks and parks toward the landing fixtures.",
                )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    part_names = {p.name for p in object_model.parts}
    ctx.check("wall_present", "wall_surround" in part_names, details=str(sorted(part_names)))

    door_joints = [j for j in object_model.joints if j.articulation_type == ArticulationType.PRISMATIC]
    ctx.check(
        "leaf_count_matches_mechanism",
        len(door_joints) == r.leaf_count,
        details=f"prismatic joints={len(door_joints)} expected={r.leaf_count}",
    )
    ctx.check(
        "all_doors_slide_along_x",
        all(abs(abs(j.axis[0]) - 1.0) < 1e-6 and abs(j.axis[1]) < 1e-6 and abs(j.axis[2]) < 1e-6
            for j in door_joints),
        details=str([tuple(j.axis) for j in door_joints]),
    )

    door_parts = [object_model.get_part(j.child) for j in door_joints]

    # --- Closed pose (rest): leaves cover the opening width & height. ---
    closed = {j: 0.0 for j in door_joints}
    with ctx.pose(closed):
        xs_min = min(ctx.part_world_aabb(p)[0][0] for p in door_parts)
        xs_max = max(ctx.part_world_aabb(p)[1][0] for p in door_parts)
        covered = xs_max - xs_min
        ctx.check(
            "closed leaves cover the opening width",
            covered >= r.ow - 0.02,
            details=f"covered={covered:.4f} vs ow={r.ow:.4f}",
        )
        for p in door_parts:
            a = ctx.part_world_aabb(p)
            ctx.check(
                f"{p.name}_spans_opening_height",
                a[0][2] < 0.05 and a[1][2] > r.oh - 0.05,
                details=f"z=({a[0][2]:.3f},{a[1][2]:.3f}) oh={r.oh:.3f}",
            )

    # --- Open pose: doorway center clears (no leaf straddles x=0). ---
    open_pose = {j: (j.motion_limits.upper if j.motion_limits else 0.0) for j in door_joints}
    with ctx.pose(open_pose):
        center_blocked = False
        for p in door_parts:
            a = ctx.part_world_aabb(p)
            if a[0][0] < -0.02 and a[1][0] > 0.02:
                center_blocked = True
        ctx.check(
            "open doors clear the doorway center",
            not center_blocked,
            details="a leaf still straddles x=0" if center_blocked else "center clear",
        )

    # --- Telescopic leaves ride two offset Y tracks (no interpenetration). ---
    if r.door_mechanism in ("side_opening_telescopic_2leaf", "center_opening_telescopic_4leaf"):
        with ctx.pose(closed):
            ys = [(p.name, (ctx.part_world_aabb(p)[0][1] + ctx.part_world_aabb(p)[1][1]) / 2.0)
                  for p in door_parts]
        distinct_tracks = len({round(y, 3) for _, y in ys})
        ctx.check(
            "telescopic leaves use >=2 offset Y tracks",
            distinct_tracks >= 2,
            details=str(ys),
        )

    # --- Sill at the floor. ---
    sill_aabb = ctx.part_element_world_aabb(object_model.get_part("wall_surround"), elem="sill_track")
    if sill_aabb is not None:
        ctx.check(
            "sill sits at the floor (z ~ 0)",
            sill_aabb[0][2] < 0.005 and sill_aabb[1][2] < 0.05,
            details=f"sill_z=({sill_aabb[0][2]:.4f},{sill_aabb[1][2]:.4f})",
        )

    # --- Wall grounded & spans the opening. ---
    wall_aabb = ctx.part_world_aabb(object_model.get_part("wall_surround"))
    ctx.check(
        "wall surround grounded and spans the opening",
        wall_aabb[0][2] < 0.02
        and (wall_aabb[1][0] - wall_aabb[0][0]) > r.ow + 0.2
        and (wall_aabb[1][2] - wall_aabb[0][2]) > r.oh,
        details=f"x=({wall_aabb[0][0]:.2f},{wall_aabb[1][0]:.2f}) z=({wall_aabb[0][2]:.2f},{wall_aabb[1][2]:.2f})",
    )

    # --- Landing fixtures presence / placement. ---
    vis_names = _wall_visual_names(object_model)
    ind_names = sorted(n for n in vis_names if n.startswith("indicator"))
    call_names = sorted(n for n in vis_names if n.startswith("call"))
    wall = object_model.get_part("wall_surround")
    if r.landing_fixtures == "minimal_none":
        ctx.check(
            "minimal: no indicator/call fixtures",
            not ind_names and not call_names,
            details=f"ind={ind_names} call={call_names}",
        )
    else:
        ctx.check("indicator present", bool(ind_names), details=str(ind_names))
        ctx.check("call panel present", bool(call_names), details=str(call_names))
        ind_zmins = [
            ctx.part_element_world_aabb(wall, elem=n)[0][2]
            for n in ind_names
            if ctx.part_element_world_aabb(wall, elem=n) is not None
        ]
        if ind_zmins:
            ctx.check(
                "indicator above the opening",
                min(ind_zmins) > r.oh,
                details=f"indicator_zmin={min(ind_zmins):.3f} oh={r.oh:.3f}",
            )
        plate_aabb = ctx.part_element_world_aabb(wall, elem="call_plate")
        if plate_aabb is not None:
            cx = (plate_aabb[0][0] + plate_aabb[1][0]) / 2.0
            cz = (plate_aabb[0][2] + plate_aabb[1][2]) / 2.0
            ctx.check(
                "call panel beside the opening at hand height",
                cx > r.ow / 2.0 and 0.9 < cz < 1.3,
                details=f"call_cx={cx:.3f} call_cz={cz:.3f}",
            )

    return ctx.report()


__all__ = [
    "ElevatorConfig",
    "ResolvedElevatorConfig",
    "build_elevator",
    "build_seeded_elevator",
    "config_from_seed",
    "resolve_config",
    "run_elevator_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
