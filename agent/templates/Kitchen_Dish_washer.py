# SPDX-License-Identifier: Apache-2.0

"""Freestanding dishwasher modular template.

NOTE on the slug: ``dish_washer`` here = a **freestanding dishwasher** -- a
hollow brushed-steel ``cabinet`` carcass (recessed kick plinth + brushed shell +
polished tub liner + side rack rails + overhanging top slab, ~0.60 W x 0.62 D x
0.85 H grounded at z=0) with an opening mechanism (a bottom-hinged drop-down
door OR a single pull-out dish-drawer), N slide-out chrome racks, and a control
strip / handle on the moving panel. It is NOT a refrigerator / freezer (side-
hinged upright door + storage shelves, no wash tub / no slide-out racks), NOT an
oven / microwave (cavity + grill, no chrome racks / no tub liner), NOT a plain
cabinet / chest of drawers (no wash tub / no control panel), and NOT a washing
machine (round porthole + drum). Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Kitchen_Dish_washer.md`` and the
``picture/Kitchen/Dish washer`` 5-star pool (1 parent + 6 slot / multiplicity
fork variants), all synced under ``data/records/``.

Structure (pattern = ``mixed``; defining motion = the opening mechanism, the
slide-out rack stack is the multiplicity axis on the door branch):

  * Root ``cabinet`` part: kick plinth + brushed shell (side / back walls,
    floor, ceiling) + polished tub liner + side ``rack_rail_{i}`` rails +
    overhanging ``top_slab``.
  * Slot A ``opening_mechanism`` (defining motion, mutually exclusive):
      - ``drop_down_door``: a ``front_door`` part (``door_panel`` + Slot C
        control visuals) on a ``door_hinge`` REVOLUTE at the bottom front edge
        (axis -X, 0..pi/2 folds flat forward) + N independent slide-out
        ``rack_{i}`` racks (PRISMATIC +Y) -- the multiplicity carrier.
      - ``dish_drawer``: one ``drawer`` part (panel + tub liner + single fixed
        rack + runners) on a ``drawer_slide`` PRISMATIC +Y; the cabinet grows a
        ``lower_front_panel`` + ``cabinet_rail_{i}`` channels. rack_count
        resolves to a trivial n1 (the single rack is fixed inside the drawer).
  * rack_count multiplicity (Slot, drop_down_door only): N in [2, 3] racks
    emitted via a ``for i in range(N)`` loop (``rack_{i}`` + ``rack_slide_{i}``
    PRISMATIC), rack_0 = lower (wheels on tub floor), rack_1 = upper (runners on
    rails), rack_2 = shallow cutlery tray (runners). Loop form from
    racks_3_cutlery / handle_recessed_tall, NOT the parent's hand-written racks.
  * Slot B ``rack_geometry`` (rack visual vocabulary, mutually exclusive):
      - ``wire_grid``: open chrome wire-frame basket (many thin Box rods).
      - ``fused_basket``: a single molded CadQuery ``basket_body`` (tray floor +
        4 walls + tine grid via ``mesh_from_cadquery``).
  * Slot C ``control_handle`` (visual on the moving panel, mutually exclusive):
      - ``front_fascia``: proud control strip + recessed pocket handle + LCD +
        buttons on the panel front (visible head-on when closed).
      - ``top_hidden``: control panel recessed into the door TOP edge (hidden
        under the slab when closed, rotates forward when open). drop_down_door
        only (needs the door's REVOLUTE rotation to expose it).
      - ``proud_bar_handle``: control strip + a full-width ``bar_handle``
        Cylinder on two ``handle_standoff_{i}`` brackets + LCD + buttons.

Compatibility (spec §9): rack_count expands [2, 3] only on drop_down_door;
dish_drawer resolves rack_count to trivial n1. top_hidden is gated to
drop_down_door only. wire_grid / fused_basket are orthogonal to everything.

All door-hinge / rack-slide / drawer-slide / runner-in-rail fits are captured
geometry, so those joints omit ``MatingContract`` (grandfathered) and are
guarded by the flat 0.015 m articulation-origin baseline plus element-scoped
``allow_overlap`` and the ``expect_contact`` / ``expect_gap`` / ``expect_within``
/ ``expect_overlap`` static-pose checks mirroring each source's run_tests block.

PERFORMANCE: the wire racks are many thin boxes and the fused baskets are
CadQuery meshes -- both are heavy. The wire rod counts are kept moderate (the
parent's vocabulary) and the fused baskets use a coarse tessellation tolerance.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

OpeningMechanism = Literal["drop_down_door", "dish_drawer"]
RackGeometry = Literal["wire_grid", "fused_basket"]
ControlHandle = Literal["front_fascia", "top_hidden", "proud_bar_handle"]
PaletteStyle = Literal[
    "stainless_brushed",
    "glossy_white",
    "matte_black",
    "steel_blue",
    "graphite_chrome",
]

OPENING_MECHANISMS: tuple[OpeningMechanism, ...] = ("drop_down_door", "dish_drawer")
RACK_GEOMETRIES: tuple[RackGeometry, ...] = ("wire_grid", "fused_basket")
CONTROL_HANDLES: tuple[ControlHandle, ...] = (
    "front_fascia",
    "top_hidden",
    "proud_bar_handle",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "stainless_brushed",
    "glossy_white",
    "matte_black",
    "steel_blue",
    "graphite_chrome",
)

# control_handle x opening_mechanism gate (spec §9 #2): top_hidden depends on
# the door's REVOLUTE rotation to expose the recessed top-edge controls, so it
# is only valid on drop_down_door.
_DOOR_ONLY_HANDLES: tuple[ControlHandle, ...] = ("top_hidden",)

# rack_count multiplicity domain (spec §8). Real dishwashers = lower + upper
# (+ optional shallow cutlery tray); >3 stacked racks are not real, so [2, 3].
N_RACK_MIN, N_RACK_MAX = 2, 3
_RACK_COUNT_CHOICES = (2, 3)
_RACK_COUNT_WEIGHTS = (0.62, 0.38)  # N=2 baseline high, N=3 cutlery common

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). From the parent (c2d628fd) carcass.
# X = width, Y = depth (front = +Y), Z = up; grounded at z = 0.
# ---------------------------------------------------------------------------
TOP_W = 0.60  # top slab width (X)
TOP_D = 0.62  # top slab depth (Y)
TOTAL_H = 0.85  # overall height (Z)

BODY_W = 0.58  # cabinet body width
BODY_FRONT_Y = 0.27  # cabinet body front face
BODY_BACK_Y = -0.29  # cabinet body back face
WALL_T = 0.02

PLINTH_H = 0.07
BODY_TOP_Z = 0.82  # underside of the top slab
SLAB_T = 0.03

DOOR_T = 0.022
SLAB_BOTTOM_Z = BODY_TOP_Z - 0.005
DOOR_H = SLAB_BOTTOM_Z - PLINTH_H - 0.002  # 0.743
HINGE_Z = PLINTH_H

RACK_W = 0.50
RACK_D = 0.48
WIRE = 0.006
RACK_TRAVEL = 0.45
TUB_FLOOR_TOP = 0.095  # top surface of the polished tub floor liner
WHEEL_R = 0.012
LINER_T = 0.008
LINER_H = 0.68

# Rack rest heights (world z of each rack's PRISMATIC origin), bottom -> top.
# rack_0 lower (wheels on tub floor), rack_1 upper (runners), rack_2 cutlery.
RACK_REST_Z = (TUB_FLOOR_TOP + 0.010, 0.45, 0.62)
RACK_BASE_HEIGHT = (0.13, 0.12, 0.04)
RACK_SUPPORT = ("wheels", "runners", "runners")

# dish_drawer geometry (spec S4).
DRAWER_BOTTOM_Z = 0.40
DRAWER_PANEL_H = BODY_TOP_Z - DRAWER_BOTTOM_Z  # 0.42
DRAWER_PANEL_T = 0.022
DRAWER_TRAVEL = 0.42
TUB_DEPTH = 0.46
TUB_WALL_T = 0.008
TUB_INTERIOR_H = DRAWER_PANEL_H - 0.04  # 0.38
DRAWER_RACK_W = 0.48
DRAWER_RACK_D = 0.40
DRAWER_RACK_H = 0.14
DRAWER_RACK_BASE_Z = 0.02 + TUB_WALL_T

# Fused-basket tessellation: coarse so the CadQuery mesh stays light.
_BASKET_MESH_TOL = 0.004
_BASKET_TINES_X = 6
_BASKET_TINES_Y = 4

# ---------------------------------------------------------------------------
# Palettes (5 colorways from the 7 source records, spec §7).
# Keys: shell (brushed body), top (top slab), tub (polished liner),
# plinth (kick plinth), strip (control strip / panel), handle (pocket / bar),
# lcd (display), button (round buttons), wire (chrome racks),
# basket (molded fused basket).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "stainless_brushed": {
        "shell": (0.72, 0.73, 0.75, 1.0),
        "top": (0.66, 0.67, 0.69, 1.0),
        "tub": (0.82, 0.83, 0.85, 1.0),
        "plinth": (0.28, 0.29, 0.30, 1.0),
        "strip": (0.20, 0.21, 0.23, 1.0),
        "handle": (0.10, 0.10, 0.11, 1.0),
        "lcd": (0.25, 0.50, 0.92, 1.0),
        "button": (0.55, 0.56, 0.58, 1.0),
        "wire": (0.85, 0.86, 0.88, 1.0),
        "basket": (0.78, 0.78, 0.76, 1.0),
    },
    "glossy_white": {
        "shell": (0.93, 0.93, 0.94, 1.0),
        "top": (0.80, 0.81, 0.83, 1.0),
        "tub": (0.84, 0.85, 0.87, 1.0),
        "plinth": (0.40, 0.41, 0.43, 1.0),
        "strip": (0.22, 0.23, 0.25, 1.0),
        "handle": (0.80, 0.81, 0.83, 1.0),
        "lcd": (0.25, 0.50, 0.92, 1.0),
        "button": (0.60, 0.61, 0.63, 1.0),
        "wire": (0.86, 0.87, 0.89, 1.0),
        "basket": (0.90, 0.90, 0.88, 1.0),
    },
    "matte_black": {
        "shell": (0.13, 0.13, 0.15, 1.0),
        "top": (0.10, 0.10, 0.12, 1.0),
        "tub": (0.78, 0.79, 0.81, 1.0),
        "plinth": (0.08, 0.08, 0.09, 1.0),
        "strip": (0.18, 0.18, 0.20, 1.0),
        "handle": (0.62, 0.63, 0.65, 1.0),
        "lcd": (0.25, 0.50, 0.92, 1.0),
        "button": (0.45, 0.46, 0.48, 1.0),
        "wire": (0.82, 0.83, 0.85, 1.0),
        "basket": (0.30, 0.30, 0.31, 1.0),
    },
    "steel_blue": {
        "shell": (0.55, 0.62, 0.70, 1.0),
        "top": (0.48, 0.55, 0.63, 1.0),
        "tub": (0.82, 0.83, 0.85, 1.0),
        "plinth": (0.24, 0.27, 0.31, 1.0),
        "strip": (0.18, 0.20, 0.24, 1.0),
        "handle": (0.80, 0.81, 0.83, 1.0),
        "lcd": (0.30, 0.60, 0.95, 1.0),
        "button": (0.55, 0.58, 0.62, 1.0),
        "wire": (0.85, 0.86, 0.88, 1.0),
        "basket": (0.74, 0.77, 0.80, 1.0),
    },
    "graphite_chrome": {
        "shell": (0.30, 0.31, 0.33, 1.0),
        "top": (0.26, 0.27, 0.29, 1.0),
        "tub": (0.80, 0.81, 0.83, 1.0),
        "plinth": (0.16, 0.17, 0.18, 1.0),
        "strip": (0.80, 0.81, 0.83, 1.0),
        "handle": (0.80, 0.81, 0.83, 1.0),
        "lcd": (0.25, 0.50, 0.92, 1.0),
        "button": (0.55, 0.56, 0.58, 1.0),
        "wire": (0.85, 0.86, 0.88, 1.0),
        "basket": (0.72, 0.73, 0.74, 1.0),
    },
}


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class DishWasherConfig:
    opening_mechanism: OpeningMechanism | None = None
    rack_geometry: RackGeometry | None = None
    control_handle: ControlHandle | None = None
    rack_count: int | None = None
    palette_style: PaletteStyle = "stainless_brushed"
    cabinet_width_scale: float = 1.0
    cabinet_depth_scale: float = 1.0
    cabinet_height_scale: float = 1.0
    rack_travel_scale: float = 1.0
    drawer_travel_scale: float = 1.0
    rack_height_scale: float = 1.0
    name: str = "dish_washer"


@dataclass(frozen=True)
class ResolvedDishWasherConfig:
    opening_mechanism: OpeningMechanism
    rack_geometry: RackGeometry
    control_handle: ControlHandle
    rack_count: int  # resolved (n1 for dish_drawer)
    palette_style: PaletteStyle
    # Derived / scaled geometry.
    width_scale: float
    depth_scale: float
    height_scale: float
    rack_heights: tuple[float, ...]
    rack_rest_z: tuple[float, ...]
    rack_travel: float
    drawer_travel: float
    name: str

    @property
    def body_w(self) -> float:
        return BODY_W * self.width_scale

    @property
    def top_w(self) -> float:
        return TOP_W * self.width_scale

    @property
    def rack_w(self) -> float:
        return RACK_W * self.width_scale

    @property
    def rack_d(self) -> float:
        return RACK_D * self.depth_scale


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> DishWasherConfig:
    rng = random.Random(seed)
    opening = rng.choice(OPENING_MECHANISMS)
    rack_geom = rng.choice(RACK_GEOMETRIES)
    if opening == "dish_drawer":
        # top_hidden gated off the drawer (no REVOLUTE rotation to expose it).
        handle = rng.choice(tuple(h for h in CONTROL_HANDLES if h not in _DOOR_ONLY_HANDLES))
        rack_count = 1
    else:
        handle = rng.choice(CONTROL_HANDLES)
        rack_count = rng.choices(_RACK_COUNT_CHOICES, weights=_RACK_COUNT_WEIGHTS, k=1)[0]
    return DishWasherConfig(
        opening_mechanism=opening,
        rack_geometry=rack_geom,
        control_handle=handle,
        rack_count=rack_count,
        palette_style=rng.choice(PALETTE_STYLES),
        cabinet_width_scale=round(rng.uniform(0.90, 1.10), 4),
        cabinet_depth_scale=round(rng.uniform(0.90, 1.12), 4),
        cabinet_height_scale=round(rng.uniform(0.92, 1.10), 4),
        rack_travel_scale=round(rng.uniform(0.85, 1.05), 4),
        drawer_travel_scale=round(rng.uniform(0.85, 1.05), 4),
        rack_height_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_dish_washer_{seed}",
    )


def resolve_config(
    config: DishWasherConfig | None = None,
) -> ResolvedDishWasherConfig:
    cfg = config or DishWasherConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    opening = _pick(cfg.opening_mechanism, OPENING_MECHANISMS)
    rack_geom = _pick(cfg.rack_geometry, RACK_GEOMETRIES)
    handle = _pick(cfg.control_handle, CONTROL_HANDLES)

    # --- control_handle x opening_mechanism gate (spec §9 #2). ---
    if opening == "dish_drawer" and handle in _DOOR_ONLY_HANDLES:
        handle = "front_fascia"

    # --- rack_count: clamp + compatibility (dish_drawer -> trivial n1). ---
    if opening == "dish_drawer":
        rack_count = 1
    else:
        rc = int(cfg.rack_count) if cfg.rack_count is not None else 2
        rack_count = int(_clamp(rc, N_RACK_MIN, N_RACK_MAX))

    # --- continuous scales (clamped to declared ranges). ---
    width_scale = _clamp(cfg.cabinet_width_scale, 0.90, 1.10)
    depth_scale = _clamp(cfg.cabinet_depth_scale, 0.90, 1.12)
    height_scale = _clamp(cfg.cabinet_height_scale, 0.92, 1.10)
    travel_scale = _clamp(cfg.rack_travel_scale, 0.85, 1.05)
    drawer_travel_scale = _clamp(cfg.drawer_travel_scale, 0.85, 1.05)
    rack_height_scale = _clamp(cfg.rack_height_scale, 0.85, 1.15)

    # --- per-rack heights + rest z, scaled by cabinet_height (spec §7). ---
    # Rest z scales with cabinet height so racks track the taller tub; rack_0
    # lower stays pinned to the tub floor (wheels), upper racks ride higher.
    rack_heights = tuple(RACK_BASE_HEIGHT[i] * rack_height_scale for i in range(rack_count))
    rest_z = []
    for i in range(rack_count):
        if i == 0:
            rest_z.append(RACK_REST_Z[0])  # lower rack sits on the tub floor
        else:
            rest_z.append(RACK_REST_Z[i] * height_scale)
    rack_rest_z = tuple(rest_z)

    # --- inequality: rack stack must fit under the tub ceiling (spec §7). ---
    # Top of the highest rack must clear the cabinet ceiling underside.
    liner_top = (PLINTH_H + WALL_T + LINER_H - 0.004) * 1.0  # base liner top
    ceiling_z = (BODY_TOP_Z - WALL_T) * height_scale
    if rack_count > 0:
        top_rack_top = rack_rest_z[-1] + rack_heights[-1]
        avail_top = ceiling_z - 0.01
        if top_rack_top > avail_top:
            # Shrink rack heights uniformly so the stack fits.
            shrink = max(0.4, (avail_top - rack_rest_z[-1]) / max(rack_heights[-1], 1e-6))
            shrink = min(1.0, shrink)
            rack_heights = tuple(h * shrink for h in rack_heights)
    _ = liner_top  # documented derivation, not otherwise needed

    # --- travel: clamp below tub depth so racks stay partly retained. ---
    tub_depth = (BODY_FRONT_Y - (BODY_BACK_Y + WALL_T)) * depth_scale
    rack_travel = min(RACK_TRAVEL * travel_scale, 0.95 * tub_depth)
    drawer_tub_depth = TUB_DEPTH * depth_scale
    drawer_travel = min(DRAWER_TRAVEL * drawer_travel_scale, 0.95 * drawer_tub_depth)

    return ResolvedDishWasherConfig(
        opening_mechanism=opening,
        rack_geometry=rack_geom,
        control_handle=handle,
        rack_count=rack_count,
        palette_style=palette_style,
        width_scale=width_scale,
        depth_scale=depth_scale,
        height_scale=height_scale,
        rack_heights=rack_heights,
        rack_rest_z=rack_rest_z,
        rack_travel=rack_travel,
        drawer_travel=drawer_travel,
        name=cfg.name or "dish_washer",
    )


def with_overrides(config: DishWasherConfig, **kwargs: object) -> DishWasherConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: DishWasherConfig | ResolvedDishWasherConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedDishWasherConfig) else resolve_config(config)
    return (
        ("opening_mechanism", r.opening_mechanism),
        ("rack_geometry", r.rack_geometry),
        ("control_handle", r.control_handle),
        ("rack_count", f"n{r.rack_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Derived layout helpers
# ===========================================================================
def _cabinet_geom(r: ResolvedDishWasherConfig) -> dict[str, float]:
    """Scaled cabinet key dimensions."""
    hs = r.height_scale
    body_top_z = BODY_TOP_Z * hs
    slab_bottom_z = body_top_z - 0.005
    door_h = slab_bottom_z - PLINTH_H - 0.002
    return {
        "body_w": r.body_w,
        "top_w": r.top_w,
        "top_d": TOP_D * r.depth_scale,
        "body_front_y": BODY_FRONT_Y * r.depth_scale,
        "body_back_y": BODY_BACK_Y * r.depth_scale,
        "body_top_z": body_top_z,
        "total_h": TOTAL_H * hs,
        "door_h": door_h,
        "drawer_bottom_z": DRAWER_BOTTOM_Z * hs,
        "drawer_panel_h": (BODY_TOP_Z - DRAWER_BOTTOM_Z) * hs,
    }


# ===========================================================================
# Cabinet (root)
# ===========================================================================
def _build_cabinet(model: ArticulatedObject, r: ResolvedDishWasherConfig, mats):
    cab = model.part("cabinet")
    g = _cabinet_geom(r)
    body_w = g["body_w"]
    body_front_y = g["body_front_y"]
    body_back_y = g["body_back_y"]
    body_top_z = g["body_top_z"]

    plinth_w = 0.52 * r.width_scale
    plinth_d = 0.52 * r.depth_scale
    cab.visual(
        Box((plinth_w, plinth_d, PLINTH_H + 0.005)),
        origin=Origin(xyz=(0.0, -0.02 * r.depth_scale, (PLINTH_H + 0.005) / 2)),
        material=mats["plinth"],
        name="kick_plinth", material_class_id="metal.paint_coated",
    )

    wall_h = body_top_z - PLINTH_H
    wall_zc = PLINTH_H + wall_h / 2
    body_d = body_front_y - body_back_y
    body_yc = (body_front_y + body_back_y) / 2

    for sx, tag in ((-1.0, "side_wall_0"), (1.0, "side_wall_1")):
        cab.visual(
            Box((WALL_T, body_d, wall_h)),
            origin=Origin(xyz=(sx * (body_w / 2 - WALL_T / 2), body_yc, wall_zc)),
            material=mats["shell"],
            name=tag, material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_brushed", "glossy_white", "matte_black", "steel_blue"} else "metal.blackened_gunmetal"),
        )
    cab.visual(
        Box((body_w - 2 * WALL_T, WALL_T, wall_h)),
        origin=Origin(xyz=(0.0, body_back_y + WALL_T / 2, wall_zc)),
        material=mats["shell"],
        name="back_wall", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_brushed", "glossy_white", "matte_black", "steel_blue"} else "metal.blackened_gunmetal"),
    )
    cab.visual(
        Box((body_w - 2 * WALL_T, body_d, WALL_T)),
        origin=Origin(xyz=(0.0, body_yc, PLINTH_H + WALL_T / 2)),
        material=mats["shell"],
        name="cabinet_floor", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_brushed", "glossy_white", "matte_black", "steel_blue"} else "metal.blackened_gunmetal"),
    )
    cab.visual(
        Box((body_w - 2 * WALL_T, body_d, WALL_T)),
        origin=Origin(xyz=(0.0, body_yc, body_top_z - WALL_T / 2)),
        material=mats["shell"],
        name="cabinet_ceiling", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_brushed", "glossy_white", "matte_black", "steel_blue"} else "metal.blackened_gunmetal"),
    )

    # Polished stainless tub liner.
    liner_h = LINER_H * r.height_scale
    liner_zc = PLINTH_H + WALL_T + liner_h / 2 - 0.004
    tub_back = body_back_y + WALL_T
    liner_d = body_front_y - tub_back - 0.01
    liner_yc = tub_back + liner_d / 2 - 0.002
    for sx, tag in ((-1.0, "tub_wall_0"), (1.0, "tub_wall_1")):
        cab.visual(
            Box((LINER_T, liner_d, liner_h)),
            origin=Origin(
                xyz=(sx * (body_w / 2 - WALL_T - LINER_T / 2 + 0.002), liner_yc, liner_zc)
            ),
            material=mats["tub"],
            name=tag, material_class_id="metal.stainless_matte",
        )
    cab.visual(
        Box((body_w - 2 * WALL_T, LINER_T, liner_h)),
        origin=Origin(xyz=(0.0, tub_back + LINER_T / 2 - 0.002, liner_zc)),
        material=mats["tub"],
        name="tub_back_panel", material_class_id="metal.stainless_matte",
    )
    cab.visual(
        Box((body_w - 2 * WALL_T - 0.01, liner_d, LINER_T)),
        origin=Origin(xyz=(0.0, liner_yc, TUB_FLOOR_TOP - LINER_T / 2)),
        material=mats["tub"],
        name="tub_floor", material_class_id="metal.stainless_matte",
    )

    cab.inertial = Inertial.from_geometry(
        Box((body_w, body_d, body_top_z)),
        mass=35.0,
        origin=Origin(xyz=(0.0, body_yc, body_top_z / 2)),
    )
    return cab


def _add_rack_rails(cab, r: ResolvedDishWasherConfig, mats) -> None:
    """Side rails for every runner-supported drop_down_door rack (loop-emit
    ``rack_rail_{rail_idx}``). rail top surface aligns with the rack local z=0
    so the runner rests on it (racks_3_cutlery L186-198)."""
    g = _cabinet_geom(r)
    body_w = g["body_w"]
    tub_inner_x = body_w / 2 - WALL_T - LINER_T + 0.002
    rail_d = 0.50 * r.depth_scale
    rail_idx = 0
    for i in range(r.rack_count):
        if RACK_SUPPORT[i] != "runners":
            continue
        rail_z = r.rack_rest_z[i] - 0.004
        for sx in (-1.0, 1.0):
            cab.visual(
                Box((0.014, rail_d, 0.008)),
                origin=Origin(xyz=(sx * (tub_inner_x - 0.005), -0.01, rail_z)),
                material=mats["tub"],
                name=f"rack_rail_{rail_idx}", material_class_id="metal.stainless_matte",
            )
            rail_idx += 1
        # Thin center cross-bar spanning the full tub width at the rail height,
        # centered on the joint origin Y so the rack_slide_{i} joint origin
        # (0, rack_yc, rest_z) sits on real cabinet hardware (the side rails are
        # off to the sides; the origin baseline measures surface distance, not
        # AABB containment). Its ends embed into both side rails to stay
        # connected to the cabinet body; it is thin in Z and 2 mm below the rail
        # top, so it sits just under the resting rack and never blocks the slide.
        cab.visual(
            Box((2 * (tub_inner_x + 0.003), 0.014, 0.004)),
            origin=Origin(xyz=(0.0, -0.01, rail_z)),
            material=mats["tub"],
            name=f"rack_cross_support_{rail_idx}", material_class_id="metal.stainless_matte",
        )


def _add_top_slab(cab, r: ResolvedDishWasherConfig, mats) -> None:
    g = _cabinet_geom(r)
    if r.opening_mechanism == "dish_drawer":
        # Slab bottom sits flush AT body_top_z so it contacts (not overlaps) the
        # drawer panel top, which reaches up to body_top_z (dishdrawer source).
        cab.visual(
            Box((g["top_w"], g["top_d"], SLAB_T)),
            origin=Origin(xyz=(0.0, 0.0, g["body_top_z"] + SLAB_T / 2)),
            material=mats["top"],
            name="top_slab", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_brushed", "glossy_white", "matte_black", "steel_blue"} else "metal.blackened_gunmetal"),
        )
    else:
        # Door variant: slab visual dips 5 mm below body_top_z (parent source).
        # The door top (door_h) clears the slab underside by ~2 mm.
        cab.visual(
            Box((g["top_w"], g["top_d"], SLAB_T + 0.005)),
            origin=Origin(xyz=(0.0, 0.0, g["body_top_z"] + (SLAB_T - 0.005) / 2)),
            material=mats["top"],
            name="top_slab", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_brushed", "glossy_white", "matte_black", "steel_blue"} else "metal.blackened_gunmetal"),
        )


# ===========================================================================
# Slot C: control_handle visuals (mounted on the moving panel)
# ===========================================================================
def _add_control_handle(part, r: ResolvedDishWasherConfig, mats, *, panel_h: float) -> None:
    """Emit the Slot C control visuals onto the moving panel part (door or
    drawer). Local frame: panel front face is at +Y (panel thickness DOOR_T),
    panel spans z in [0, panel_h]."""
    handle = r.control_handle
    body_w = r.body_w

    if handle == "top_hidden":
        # Controls recessed into the panel TOP edge (z ~ panel_h), facing up so
        # they hide under the slab when closed and rotate forward when open.
        ctrl_top_z = panel_h
        part.visual(
            Box((body_w - 0.04, DOOR_T - 0.004, 0.005)),
            origin=Origin(xyz=(0.0, DOOR_T / 2, ctrl_top_z - 0.005 / 2)),
            material=mats["strip"],
            name="control_panel", material_class_id="tech.control_interface",
        )
        part.visual(
            Box((0.22, 0.016, 0.004)),
            origin=Origin(xyz=(0.0, DOOR_T / 2, ctrl_top_z - 0.003)),
            material=mats["handle"],
            name="pocket_handle", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Box((0.085, 0.022, 0.003)),
            origin=Origin(xyz=(0.155, DOOR_T / 2, ctrl_top_z - 0.002)),
            material=mats["lcd"],
            name="display_lcd", material_class_id="tech.emissive_surface",
        )
        for i, bx in enumerate((-0.215, -0.180, -0.145, -0.110)):
            part.visual(
                Cylinder(radius=0.0075, length=0.005),
                origin=Origin(xyz=(bx, DOOR_T / 2, ctrl_top_z - 0.0025)),
                material=mats["button"],
                name=f"button_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        return

    # front_fascia / proud_bar_handle share the proud control strip.
    strip_h = 0.07
    strip_zc = panel_h - 0.005 - strip_h / 2
    part.visual(
        Box((body_w, 0.010, strip_h)),
        origin=Origin(xyz=(0.0, DOOR_T + 0.003, strip_zc)),
        material=mats["strip"],
        name="control_strip", material_class_id="tech.control_interface",
    )
    strip_face = DOOR_T + 0.008

    if handle == "proud_bar_handle":
        # Full-width grab bar (>0.40 m span) on two standoff brackets (>0.02 m).
        standoff_depth = 0.032
        bar_z = strip_zc - 0.008
        for i, sx in enumerate((-1.0, 1.0)):
            part.visual(
                Box((0.028, standoff_depth, 0.022)),
                origin=Origin(xyz=(sx * 0.20, DOOR_T + standoff_depth / 2, bar_z)),
                material=mats["shell"],
                name=f"handle_standoff_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_brushed", "glossy_white", "matte_black", "steel_blue"} else "metal.blackened_gunmetal"),
            )
        bar_len = 0.50
        part.visual(
            Cylinder(radius=0.010, length=bar_len),
            origin=Origin(
                xyz=(0.0, DOOR_T + standoff_depth, bar_z),
                rpy=(0.0, math.pi / 2, 0.0),
            ),
            material=mats["handle"],
            name="bar_handle", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        # front_fascia: recessed pocket handle, inset bar proud of the strip.
        part.visual(
            Box((0.20, 0.005, 0.026)),
            origin=Origin(xyz=(0.0, strip_face + 0.0015, strip_zc - 0.006)),
            material=mats["handle"],
            name="pocket_handle", material_class_id="plastic.opaque_glossy_molded",
        )

    part.visual(
        Box((0.085, 0.004, 0.024)),
        origin=Origin(xyz=(0.155, strip_face + 0.001, strip_zc + 0.004)),
        material=mats["lcd"],
        name="display_lcd", material_class_id="tech.emissive_surface",
    )
    for i, bx in enumerate((-0.215, -0.180, -0.145, -0.110)):
        part.visual(
            Cylinder(radius=0.0075, length=0.008),
            origin=Origin(
                xyz=(bx, strip_face, strip_zc + 0.004),
                rpy=(math.pi / 2, 0.0, 0.0),
            ),
            material=mats["button"],
            name=f"button_{i}", material_class_id="plastic.opaque_glossy_molded",
        )


# ===========================================================================
# Slot A: drop_down_door
# ===========================================================================
def _build_door(model: ArticulatedObject, r: ResolvedDishWasherConfig, mats):
    """Door authored in its hinge frame: hinge axis through local origin, panel
    vertical at q=0, extending +Z (up) and +Y (thickness)."""
    g = _cabinet_geom(r)
    door_h = g["door_h"]
    body_w = g["body_w"]
    door = model.part("front_door")
    door.visual(
        Box((body_w, DOOR_T, door_h)),
        origin=Origin(xyz=(0.0, DOOR_T / 2, door_h / 2)),
        material=mats["shell"],
        name="door_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_brushed", "glossy_white", "matte_black", "steel_blue"} else "metal.blackened_gunmetal"),
    )
    _add_control_handle(door, r, mats, panel_h=door_h)
    door.inertial = Inertial.from_geometry(
        Box((body_w, DOOR_T, door_h)),
        mass=6.0,
        origin=Origin(xyz=(0.0, DOOR_T / 2, door_h / 2)),
    )
    return door


# ===========================================================================
# Slot B: rack geometry (wire_grid / fused_basket)
# ===========================================================================
def _linspace(lo: float, hi: float, n: int) -> list[float]:
    if n == 1:
        return [(lo + hi) * 0.5]
    step = (hi - lo) / (n - 1)
    return [lo + i * step for i in range(n)]


def _add_wire_basket(rack, r: ResolvedDishWasherConfig, mats, *, height: float) -> None:
    """Open chrome wire-frame basket in the rack local frame (parent
    _populate_rack vocabulary). Moderate rod counts for performance."""
    rw = r.rack_w
    rd = r.rack_d
    hw = rw / 2
    hd = rd / 2

    # Floor longitudinal rods (along Y) + lateral rods (along X).
    n_long = 9 if height > 0.06 else 7
    for i, x in enumerate(_linspace(-hw + 0.01, hw - 0.01, n_long)):
        rack.visual(
            Box((WIRE, rd - 0.004, WIRE)),
            origin=Origin(xyz=(x, 0.0, 0.003)),
            material=mats["wire"],
            name=f"floor_rod_y_{i}", material_class_id="metal.chrome_polished",
        )
    n_cross = 5 if height > 0.06 else 4
    cross_ys = _linspace(-hd + 0.003, hd - 0.003, n_cross)
    for i, y in enumerate(cross_ys):
        rack.visual(
            Box((rw, WIRE, WIRE)),
            origin=Origin(xyz=(0.0, y, 0.007)),
            material=mats["wire"],
            name=f"floor_rod_x_{i}", material_class_id="metal.chrome_polished",
        )

    # Top perimeter rail.
    rail_z = height - WIRE / 2
    for i, y in enumerate((-hd + 0.003, hd - 0.003)):
        rack.visual(
            Box((rw, WIRE, WIRE)),
            origin=Origin(xyz=(0.0, y, rail_z)),
            material=mats["wire"],
            name=f"top_rail_xy_{i}", material_class_id="metal.chrome_polished",
        )
    for i, x in enumerate((-hw + 0.003, hw - 0.003)):
        rack.visual(
            Box((WIRE, rd, WIRE)),
            origin=Origin(xyz=(x, 0.0, rail_z)),
            material=mats["wire"],
            name=f"top_rail_side_{i}", material_class_id="metal.chrome_polished",
        )

    # Vertical wires (sides aligned with cross rods so every wire lands on a wire).
    for j, y in enumerate(cross_ys):
        for k, x in enumerate((-hw + 0.003, hw - 0.003)):
            rack.visual(
                Box((WIRE, WIRE, height)),
                origin=Origin(xyz=(x, y, height / 2)),
                material=mats["wire"],
                name=f"side_wire_{k}_{j}", material_class_id="metal.chrome_polished",
            )
    n_face = 7 if height > 0.06 else 5
    for j, x in enumerate(_linspace(-hw + 0.01, hw - 0.01, n_face)):
        for k, y in enumerate((-hd + 0.003, hd - 0.003)):
            rack.visual(
                Box((WIRE, WIRE, height)),
                origin=Origin(xyz=(x, y, height / 2)),
                material=mats["wire"],
                name=f"face_wire_{k}_{j}", material_class_id="metal.chrome_polished",
            )


def _build_fused_basket_mesh(w: float, d: float, height: float, *, assets):
    """A single molded basket as one CadQuery solid: floor plate + 4 perimeter
    walls + a grid of cylindrical tine prongs (fused_basket source S5). Coarse
    tessellation for performance. Local frame: bottom center at origin."""
    floor_t = 0.008
    wall_t = 0.006
    hw = w / 2
    hd = d / 2
    wall_h = height - floor_t
    tine_r = 0.003
    tine_h = max(0.004, height - floor_t - 0.004)

    basket = cq.Workplane("XY").box(w, d, floor_t, centered=(True, True, False))
    basket = basket.union(
        cq.Workplane("XY")
        .box(w, wall_t, wall_h)
        .translate((0.0, hd - wall_t / 2, floor_t + wall_h / 2))
    )
    basket = basket.union(
        cq.Workplane("XY")
        .box(w, wall_t, wall_h)
        .translate((0.0, -hd + wall_t / 2, floor_t + wall_h / 2))
    )
    basket = basket.union(
        cq.Workplane("XY")
        .box(wall_t, d - 2 * wall_t, wall_h)
        .translate((-hw + wall_t / 2, 0.0, floor_t + wall_h / 2))
    )
    basket = basket.union(
        cq.Workplane("XY")
        .box(wall_t, d - 2 * wall_t, wall_h)
        .translate((hw - wall_t / 2, 0.0, floor_t + wall_h / 2))
    )

    inner_w = w - 2 * wall_t - 0.02
    inner_d = d - 2 * wall_t - 0.02
    if _BASKET_TINES_X > 0 and _BASKET_TINES_Y > 0:
        spacing_x = inner_w / (_BASKET_TINES_X + 1)
        spacing_y = inner_d / (_BASKET_TINES_Y + 1)
        tines = (
            cq.Workplane("XY")
            .workplane(offset=floor_t)
            .rarray(spacing_x, spacing_y, _BASKET_TINES_X, _BASKET_TINES_Y)
            .circle(tine_r)
            .extrude(tine_h)
        )
        basket = basket.union(tines)

    return mesh_from_cadquery(basket, "basket_body", assets=assets, tolerance=_BASKET_MESH_TOL)


def _add_rack_support(rack, r: ResolvedDishWasherConfig, mats, *, index: int) -> None:
    """Wheels (lower rack, rolls on tub floor) or runners (upper racks)."""
    rw = r.rack_w
    rd = r.rack_d
    support = RACK_SUPPORT[index]
    if support == "wheels":
        wheel_zc = (TUB_FLOOR_TOP + WHEEL_R) - r.rack_rest_z[index]  # local
        idx = 0
        for wy in (-0.20 * r.depth_scale, 0.20 * r.depth_scale):
            for wx in (-0.18 * r.width_scale, 0.18 * r.width_scale):
                rack.visual(
                    Cylinder(radius=WHEEL_R, length=0.010),
                    origin=Origin(xyz=(wx, wy, wheel_zc), rpy=(0.0, math.pi / 2, 0.0)),
                    material=mats["button"],
                    name=f"wheel_{idx}", material_class_id="plastic.opaque_glossy_molded",
                )
                idx += 1
    else:
        # Runner outer face just past the basket's outermost vertical wires
        # (at rack_w/2 - 0.003) so the runner always embeds into the basket
        # body regardless of width_scale (parent placed it at rack_w/2 + 0.0035).
        runner_x = rw / 2 + 0.0035
        for k, sx in enumerate((-1.0, 1.0)):
            rack.visual(
                Box((0.011, rd, 0.006)),
                origin=Origin(xyz=(sx * runner_x, 0.0, 0.003)),
                material=mats["wire"],
                name=f"side_runner_{k}", material_class_id="metal.chrome_polished",
            )


def _populate_rack(
    rack, r: ResolvedDishWasherConfig, mats, *, index: int, height: float, assets
) -> None:
    """Populate one drop_down_door rack: support + Slot B basket geometry."""
    _add_rack_support(rack, r, mats, index=index)
    if r.rack_geometry == "fused_basket":
        rack.visual(
            _build_fused_basket_mesh(r.rack_w, r.rack_d, height, assets=assets),
            material=mats["basket"],
            name="basket_body", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        _add_wire_basket(rack, r, mats, height=height)


# ===========================================================================
# Slot A: dish_drawer
# ===========================================================================
def _build_cabinet_drawer_extras(cab, r: ResolvedDishWasherConfig, mats) -> None:
    """dish_drawer cabinet additions: lower_front_panel + cabinet_rail_{i}."""
    g = _cabinet_geom(r)
    body_w = g["body_w"]
    body_front_y = g["body_front_y"]
    body_back_y = g["body_back_y"]
    drawer_bottom_z = g["drawer_bottom_z"]
    drawer_panel_h = g["drawer_panel_h"]
    body_yc = (body_front_y + body_back_y) / 2

    lower_panel_h = drawer_bottom_z - PLINTH_H
    cab.visual(
        Box((body_w - 2 * WALL_T, WALL_T, lower_panel_h)),
        origin=Origin(xyz=(0.0, body_front_y - WALL_T / 2, PLINTH_H + lower_panel_h / 2)),
        material=mats["shell"],
        name="lower_front_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_brushed", "glossy_white", "matte_black", "steel_blue"} else "metal.blackened_gunmetal"),
    )
    rail_h = 0.032
    rail_d = 0.52 * r.depth_scale
    rail_zc = drawer_bottom_z + drawer_panel_h / 2
    for i, sx in enumerate((-1.0, 1.0)):
        cab.visual(
            Box((0.014, rail_d, rail_h)),
            origin=Origin(xyz=(sx * (body_w / 2 - WALL_T - 0.005), body_yc + 0.02, rail_zc)),
            material=mats["tub"],
            name=f"cabinet_rail_{i}", material_class_id="metal.stainless_matte",
        )


def _add_drawer_wire_basket(part, r: ResolvedDishWasherConfig, mats, *, rack_yc: float) -> None:
    """Prefixed wire basket inside the drawer body (dishdrawer _add_rack_wires)."""
    hw = (DRAWER_RACK_W * r.width_scale) / 2
    hd = (DRAWER_RACK_D * r.depth_scale) / 2
    base_z = DRAWER_RACK_BASE_Z
    height = DRAWER_RACK_H
    for i, x in enumerate(_linspace(-hw + 0.01, hw - 0.01, 9)):
        part.visual(
            Box((WIRE, 2 * hd - 0.004, WIRE)),
            origin=Origin(xyz=(x, rack_yc, base_z + 0.003)),
            material=mats["wire"],
            name=f"rack_floor_rod_y_{i}", material_class_id="metal.chrome_polished",
        )
    cross_ys = _linspace(rack_yc - hd + 0.003, rack_yc + hd - 0.003, 5)
    for i, y in enumerate(cross_ys):
        part.visual(
            Box((2 * hw, WIRE, WIRE)),
            origin=Origin(xyz=(0.0, y, base_z + 0.007)),
            material=mats["wire"],
            name=f"rack_floor_rod_x_{i}", material_class_id="metal.chrome_polished",
        )
    rail_z = base_z + height - WIRE / 2
    for i, y in enumerate((rack_yc - hd + 0.003, rack_yc + hd - 0.003)):
        part.visual(
            Box((2 * hw, WIRE, WIRE)),
            origin=Origin(xyz=(0.0, y, rail_z)),
            material=mats["wire"],
            name=f"rack_top_rail_xy_{i}", material_class_id="metal.chrome_polished",
        )
    for i, x in enumerate((-hw + 0.003, hw - 0.003)):
        part.visual(
            Box((WIRE, 2 * hd, WIRE)),
            origin=Origin(xyz=(x, rack_yc, rail_z)),
            material=mats["wire"],
            name=f"rack_top_rail_side_{i}", material_class_id="metal.chrome_polished",
        )
    for j, y in enumerate(cross_ys):
        for k, x in enumerate((-hw + 0.003, hw - 0.003)):
            part.visual(
                Box((WIRE, WIRE, height)),
                origin=Origin(xyz=(x, y, base_z + height / 2)),
                material=mats["wire"],
                name=f"rack_side_wire_{k}_{j}", material_class_id="metal.chrome_polished",
            )
    for j, x in enumerate(_linspace(-hw + 0.01, hw - 0.01, 7)):
        for k, y in enumerate((rack_yc - hd + 0.003, rack_yc + hd - 0.003)):
            part.visual(
                Box((WIRE, WIRE, height)),
                origin=Origin(xyz=(x, y, base_z + height / 2)),
                material=mats["wire"],
                name=f"rack_face_wire_{k}_{j}", material_class_id="metal.chrome_polished",
            )


def _build_drawer(model: ArticulatedObject, r: ResolvedDishWasherConfig, mats, *, assets):
    """Pull-out drawer: front panel + Slot C control + tub liner + single rack +
    runners, all one moving body. Local origin at the bottom center of the front
    face (coincides with the joint origin at q=0)."""
    g = _cabinet_geom(r)
    body_w = g["body_w"]
    drawer_panel_h = g["drawer_panel_h"]
    drawer = model.part("drawer")

    drawer.visual(
        Box((body_w, DRAWER_PANEL_T, drawer_panel_h)),
        origin=Origin(xyz=(0.0, DRAWER_PANEL_T / 2, drawer_panel_h / 2)),
        material=mats["shell"],
        name="drawer_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_brushed", "glossy_white", "matte_black", "steel_blue"} else "metal.blackened_gunmetal"),
    )
    _add_control_handle(drawer, r, mats, panel_h=drawer_panel_h)

    # Tub liner carried by the drawer.
    tub_depth = TUB_DEPTH * r.depth_scale
    tub_wall_xc = body_w / 2 - WALL_T - TUB_WALL_T / 2 - 0.018
    tub_interior_h = TUB_INTERIOR_H * r.height_scale
    tub_zc = tub_interior_h / 2 + 0.02
    for i, sx in enumerate((-1.0, 1.0)):
        drawer.visual(
            Box((TUB_WALL_T, tub_depth, tub_interior_h)),
            origin=Origin(xyz=(sx * tub_wall_xc, -tub_depth / 2, tub_zc)),
            material=mats["tub"],
            name=f"tub_wall_{i}", material_class_id="metal.stainless_matte",
        )
    drawer.visual(
        Box((body_w - 2 * WALL_T - 0.02, TUB_WALL_T, tub_interior_h)),
        origin=Origin(xyz=(0.0, -tub_depth + TUB_WALL_T / 2, tub_zc)),
        material=mats["tub"],
        name="tub_back_panel", material_class_id="metal.stainless_matte",
    )
    drawer.visual(
        Box((body_w - 2 * WALL_T - 0.02, tub_depth, TUB_WALL_T)),
        origin=Origin(xyz=(0.0, -tub_depth / 2, 0.02 + TUB_WALL_T / 2)),
        material=mats["tub"],
        name="tub_floor", material_class_id="metal.stainless_matte",
    )

    # Slide runners (moving members on the drawer sides).
    runner_w = 0.012
    runner_h = 0.026
    runner_d = tub_depth + 0.02
    runner_xc = body_w / 2 - WALL_T - runner_w / 2 - 0.006
    for i, sx in enumerate((-1.0, 1.0)):
        drawer.visual(
            Box((runner_w, runner_d, runner_h)),
            origin=Origin(xyz=(sx * runner_xc, -tub_depth / 2 + 0.01, drawer_panel_h / 2)),
            material=mats["tub"],
            name=f"drawer_runner_{i}", material_class_id="metal.stainless_matte",
        )

    # Single fixed rack inside the tub (Slot B vocabulary).
    rack_yc = -tub_depth / 2
    if r.rack_geometry == "fused_basket":
        basket_mesh = _build_fused_basket_mesh(
            DRAWER_RACK_W * r.width_scale,
            DRAWER_RACK_D * r.depth_scale,
            DRAWER_RACK_H,
            assets=assets,
        )
        drawer.visual(
            basket_mesh,
            material=mats["basket"],
            name="basket_body", material_class_id="plastic.opaque_glossy_molded",
            origin=Origin(xyz=(0.0, rack_yc, DRAWER_RACK_BASE_Z)),
        )
    else:
        _add_drawer_wire_basket(drawer, r, mats, rack_yc=rack_yc)

    drawer.inertial = Inertial.from_geometry(
        Box((body_w, tub_depth, drawer_panel_h)),
        mass=8.0,
        origin=Origin(xyz=(0.0, -tub_depth / 3, drawer_panel_h / 2)),
    )
    return drawer


# ===========================================================================
# Build
# ===========================================================================
def build_dish_washer(
    config: DishWasherConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"dish_washer_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in pal.items()
    }

    g = _cabinet_geom(r)
    cabinet = _build_cabinet(model, r, mats)

    if r.opening_mechanism == "dish_drawer":
        _build_cabinet_drawer_extras(cabinet, r, mats)
        _add_top_slab(cabinet, r, mats)
        drawer = _build_drawer(model, r, mats, assets=assets)
        model.articulation(
            "drawer_slide",
            ArticulationType.PRISMATIC,
            parent=cabinet,
            child=drawer,
            origin=Origin(xyz=(0.0, g["body_front_y"], g["drawer_bottom_z"])),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=40.0, velocity=0.5, lower=0.0, upper=r.drawer_travel),
        )
    else:
        _add_rack_rails(cabinet, r, mats)
        _add_top_slab(cabinet, r, mats)
        door = _build_door(model, r, mats)
        model.articulation(
            "door_hinge",
            ArticulationType.REVOLUTE,
            parent=cabinet,
            child=door,
            origin=Origin(xyz=(0.0, g["body_front_y"], HINGE_Z)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=30.0, velocity=1.5, lower=0.0, upper=math.pi / 2),
        )

        # Multiplicity axis: N independent slide-out racks (loop-emit).
        rack_yc = -0.01 * r.depth_scale
        for i in range(r.rack_count):
            rack = model.part(f"rack_{i}")
            height = r.rack_heights[i]
            _populate_rack(rack, r, mats, index=i, height=height, assets=assets)
            rack.inertial = Inertial.from_geometry(
                Box((r.rack_w, r.rack_d, max(height, 0.02))),
                mass=1.5,
                origin=Origin(xyz=(0.0, 0.0, height / 2)),
            )
            model.articulation(
                f"rack_slide_{i}",
                ArticulationType.PRISMATIC,
                parent=cabinet,
                child=rack,
                origin=Origin(xyz=(0.0, rack_yc, r.rack_rest_z[i])),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(
                    effort=20.0, velocity=0.5, lower=0.0, upper=r.rack_travel
                ),
            )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_dish_washer(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_dish_washer(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_dish_washer_tests(
    object_model: ArticulatedObject,
    config: DishWasherConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    g = _cabinet_geom(r)

    cabinet = object_model.get_part("cabinet")

    # --- overall envelope grounded at z=0, roughly cabinet-sized. ---
    aabb = ctx.part_world_aabb(cabinet)
    ctx.check("cabinet present with world AABB", aabb is not None, details=f"aabb={aabb}")
    if aabb is not None:
        (x0, y0, z0), (x1, y1, z1) = aabb
        ext_x = x1 - x0
        ctx.check(
            "cabinet roughly cabinet-sized in X",
            0.50 < ext_x < 0.70,
            details=f"ext_x={ext_x:.3f}",
        )
        ctx.check(
            "cabinet grounded at z=0",
            abs(z0) < 1e-3,
            details=f"z0={z0:.5f}",
        )

    if r.opening_mechanism == "drop_down_door":
        _check_door_branch(ctx, object_model, r, g, cabinet)
    else:
        _check_drawer_branch(ctx, object_model, r, g, cabinet)

    return ctx.report()


def _check_door_branch(ctx, object_model, r, g, cabinet) -> None:
    door = object_model.get_part("front_door")
    hinge = object_model.get_articulation("door_hinge")
    n = r.rack_count
    racks = [object_model.get_part(f"rack_{i}") for i in range(n)]
    slides = [object_model.get_articulation(f"rack_slide_{i}") for i in range(n)]
    body_front_y = g["body_front_y"]

    # --- door hinge: revolute about horizontal X, 0..pi/2, bottom front edge.
    ctx.check(
        "door hinge is revolute about a horizontal X axis, 0..~90deg",
        hinge.articulation_type == ArticulationType.REVOLUTE
        and abs(abs(hinge.axis[0]) - 1.0) < 1e-6
        and abs(hinge.axis[1]) < 1e-6
        and abs(hinge.axis[2]) < 1e-6
        and hinge.motion_limits is not None
        and abs(hinge.motion_limits.lower) < 1e-9
        and abs(hinge.motion_limits.upper - math.pi / 2) < 1e-6,
        details=f"axis={hinge.axis}, limits={hinge.motion_limits}",
    )
    ctx.check(
        "hinge sits at the bottom front edge of the cabinet",
        abs(hinge.origin.xyz[1] - body_front_y) < 1e-6
        and abs(hinge.origin.xyz[2] - PLINTH_H) < 1e-6,
        details=f"hinge origin = {hinge.origin.xyz}",
    )

    # --- N racks, loop-emitted, all prismatic +Y. ---
    ctx.check(
        "at least two slide-out racks authored (multiplicity axis)",
        n >= 2 and all(racks[i] is not None for i in range(n)),
        details=f"rack_count={n}",
    )
    for i, slide in enumerate(slides):
        ctx.check(
            f"rack_slide_{i} is prismatic along +Y with positive travel",
            slide.articulation_type == ArticulationType.PRISMATIC
            and abs(slide.axis[1] - 1.0) < 1e-6
            and abs(slide.axis[0]) < 1e-6
            and abs(slide.axis[2]) < 1e-6
            and slide.motion_limits is not None
            and abs(slide.motion_limits.lower) < 1e-9
            and slide.motion_limits.upper > 0.02,
            details=f"axis={slide.axis}, limits={slide.motion_limits}",
        )
    for i in range(n - 1):
        ctx.check(
            f"rack_{i + 1} mounted above rack_{i}",
            slides[i + 1].origin.xyz[2] > slides[i].origin.xyz[2] + 0.03,
            details=f"z[{i + 1}]={slides[i + 1].origin.xyz[2]:.3f}, z[{i}]={slides[i].origin.xyz[2]:.3f}",
        )

    # --- closed door: vertical full-height panel at the cabinet front. ---
    door_aabb = ctx.part_world_aabb(door)
    if door_aabb is not None:
        (dx0, dy0, dz0), (dx1, dy1, dz1) = door_aabb
        ctx.check(
            "closed door is a vertical full-height panel at the cabinet front",
            (dz1 - dz0) > 0.60
            and (dy1 - dy0) < 0.10
            and dy0 >= body_front_y - 1e-3
            and abs(dz0 - PLINTH_H) < 0.02,
            details=f"door aabb = {door_aabb}",
        )
    ctx.expect_contact(
        door,
        cabinet,
        elem_a="door_panel",
        elem_b="side_wall_0",
        contact_tol=2e-3,
        name="closed door panel seats flush on the cabinet front face",
    )

    # --- racks nest inside the tub when closed. ---
    for i in range(n):
        ctx.expect_within(
            racks[i],
            cabinet,
            axes="xy",
            margin=0.0,
            name=f"rack_{i} stays inside the cabinet footprint when stowed",
        )
        ctx.expect_gap(
            door,
            racks[i],
            axis="y",
            min_gap=0.003,
            name=f"closed door clears the stowed rack_{i}",
        )
    # rack_0 wheels rest on the tub floor; upper racks runners rest on rails.
    ctx.expect_contact(
        racks[0],
        cabinet,
        elem_a="wheel_0",
        elem_b="tub_floor",
        contact_tol=2e-3,
        name="rack_0 (lower) wheels rest on the tub floor",
    )
    if n >= 2:
        ctx.expect_contact(
            racks[1],
            cabinet,
            elem_a="side_runner_0",
            elem_b="rack_rail_0",
            contact_tol=2e-3,
            name="rack_1 (upper) runners rest on the tub side rails",
        )

    # --- open poses: door folds flat forward above the floor. ---
    with ctx.pose({hinge: math.pi / 2}):
        open_aabb = ctx.part_world_aabb(door)
        if open_aabb is not None:
            (ox0, oy0, oz0), (ox1, oy1, oz1) = open_aabb
            ctx.check(
                "fully open door lies horizontal in front of the cabinet, above the floor",
                oz1 < 0.16 and oy1 > 0.90 and oz0 > -1e-3,
                details=f"open door aabb = {open_aabb}",
            )

    # --- Sequenced mechanism: a real dishwasher's racks only slide out over the
    # fully-open (flat) drop door. "door shut + rack out" is an unphysical pose
    # a pose-setter can request but never occurs in operation — it is the user's
    # responsibility, not a geometry defect. So the racks keep their FULL
    # designed travel (no worst-case door-shut clamp that strangled it to ~3cm)
    # and each rack↔door pair is whitelisted for overlap with a reason. The
    # allowance is scoped to exactly the rack↔front_door pair; rack↔cabinet
    # (tub / cavity walls) is NOT allowed and is still checked at full travel
    # below. The REAL riskiest operating pose — door flat + every rack at FULL
    # travel — is asserted collision-free separately.
    solved_travels = [float(slides[i].motion_limits.upper) for i in range(n)]
    for i in range(n):
        ctx.allow_overlap(
            door,
            racks[i],
            reason=(
                f"Sequenced mechanism: rack_{i} slides out (+Y) only over the OPEN "
                f"(flat) drop door; the sampled 'door shut + rack out' pose is an "
                f"unphysical pose-setter combo, not a real operating state, so the "
                f"rack passing through the closed door_panel plane is allowed. Scoped "
                f"to rack_{i}↔front_door only — rack↔cabinet (tub walls) stays checked."
            ),
        )
        ctx.check(
            f"rack_slide_{i} keeps the full designed travel",
            solved_travels[i] >= r.rack_travel - 1e-6,
            details=f"travel={solved_travels[i]:.4f} vs designed {r.rack_travel:.4f}",
        )
    all_at_travel = {slides[i]: solved_travels[i] for i in range(n)}
    with ctx.pose({**all_at_travel, hinge: math.pi / 2}):
        ctx.fail_if_parts_overlap_in_current_pose(
            name="racks_at_full_travel_clear_the_open_door",
        )
    # Racks still visibly pull forward (+Y) and stay partly retained in the tub.
    rest_pos = ctx.part_world_position(racks[0])
    with ctx.pose({**all_at_travel, hinge: math.pi / 2}):
        ext_pos = ctx.part_world_position(racks[0])
        ctx.check(
            "rack_0 slides forward along +Y",
            rest_pos is not None
            and ext_pos is not None
            and (ext_pos[1] - rest_pos[1]) > solved_travels[0] * 0.5,
            details=f"rest={rest_pos}, ext={ext_pos}",
        )
        for i in range(n):
            ctx.expect_overlap(
                racks[i],
                cabinet,
                axes="y",
                min_overlap=0.02,
                name=f"extended rack_{i} stays partly retained in the tub",
            )

    # top_hidden: controls hidden under the slab when closed.
    if r.control_handle == "top_hidden":
        panel_aabb = ctx.part_element_world_aabb(door, elem="control_panel")
        ctx.check(
            "top_hidden controls tucked under the countertop slab when closed",
            panel_aabb is not None and panel_aabb[1][2] < g["body_top_z"] + 0.01,
            details=f"control_panel aabb = {panel_aabb}",
        )


def _check_drawer_branch(ctx, object_model, r, g, cabinet) -> None:
    drawer = object_model.get_part("drawer")
    slide = object_model.get_articulation("drawer_slide")
    body_front_y = g["body_front_y"]

    ctx.check(
        "drawer slide is prismatic along +Y with positive travel",
        slide.articulation_type == ArticulationType.PRISMATIC
        and abs(slide.axis[1] - 1.0) < 1e-6
        and abs(slide.axis[0]) < 1e-6
        and abs(slide.axis[2]) < 1e-6
        and slide.motion_limits is not None
        and abs(slide.motion_limits.lower) < 1e-9
        and slide.motion_limits.upper > 0.10,
        details=f"axis={slide.axis}, limits={slide.motion_limits}",
    )
    ctx.check(
        "slide origin sits at the cabinet front at the drawer opening bottom",
        abs(slide.origin.xyz[1] - body_front_y) < 1e-6
        and abs(slide.origin.xyz[2] - g["drawer_bottom_z"]) < 1e-6,
        details=f"slide origin = {slide.origin.xyz}",
    )

    drawer_aabb = ctx.part_world_aabb(drawer)
    if drawer_aabb is not None:
        (dx0, dy0, dz0), (dx1, dy1, dz1) = drawer_aabb
        ctx.check(
            "closed drawer sits at the opening with its front panel at the cabinet front",
            (dz1 - dz0) > 0.30
            and dy1 >= body_front_y - 0.01
            and abs(dz0 - g["drawer_bottom_z"]) < 0.02,
            details=f"drawer aabb = {drawer_aabb}",
        )
    ctx.expect_within(
        drawer,
        cabinet,
        axes="xy",
        margin=0.03,
        name="closed drawer tub stays inside the cabinet footprint",
    )

    tub_floor_aabb = ctx.part_element_world_aabb(drawer, elem="tub_floor")
    ctx.check(
        "drawer contains a polished tub floor above the plinth",
        tub_floor_aabb is not None and tub_floor_aabb[0][2] > PLINTH_H + 0.25,
        details=f"tub_floor aabb = {tub_floor_aabb}",
    )

    # runner-in-rail telescoping captured slide (allow_overlap + contact).
    for i in range(2):
        ctx.allow_overlap(
            drawer,
            cabinet,
            elem_a=f"drawer_runner_{i}",
            elem_b=f"cabinet_rail_{i}",
            reason=(
                f"Drawer runner {i} slides inside the stationary cabinet rail {i} "
                f"channel -- a telescoping captured slide mechanism."
            ),
        )
        ctx.expect_contact(
            drawer,
            cabinet,
            elem_a=f"drawer_runner_{i}",
            elem_b=f"cabinet_rail_{i}",
            contact_tol=0.008,
            name=f"drawer_runner_{i} stays in contact with cabinet_rail_{i}",
        )

    rest_pos = ctx.part_world_position(drawer)
    with ctx.pose({slide: r.drawer_travel}):
        ext_pos = ctx.part_world_position(drawer)
        ctx.check(
            "drawer slides forward by its travel distance",
            rest_pos is not None and ext_pos is not None and (ext_pos[1] - rest_pos[1]) > 0.10,
            details=f"rest={rest_pos}, ext={ext_pos}",
        )
        ctx.expect_overlap(
            drawer,
            cabinet,
            axes="y",
            min_overlap=0.02,
            name="extended drawer stays partly retained in the cabinet",
        )
        ext_aabb = ctx.part_world_aabb(drawer)
        ctx.check(
            "extended drawer front projects well past the cabinet front",
            ext_aabb is not None and ext_aabb[1][1] > body_front_y + 0.20,
            details=f"extended drawer aabb = {ext_aabb}",
        )
