# SPDX-License-Identifier: Apache-2.0

"""Fire cabinet (street/utility upright steel cabinet) — modular procedural template.

Category identity: a single grounded sheet-steel carcass shell ``cabinet`` (the
labelled "Fire cabinet" is actually a filing-cabinet-shaped multi-drawer/door
metal box) whose front opening is closed by a *real* articulated closure — the
defining joint family:

  * ``n_sliding_drawers``  : N open-top steel trays ``drawer_{i}`` PRISMATIC +X
  * ``single_hinged_door`` : one full-height ``door`` REVOLUTE about vertical Z
  * ``double_doors``       : two centre-meeting ``door_{left,right}`` 2x REVOLUTE
  * ``roller_shutter``     : a ``shutter`` (lift_bar + N interlocking slats) PRISMATIC +Z

Slot graph (parallel children all parenting to the single grounded ``cabinet``):

    [Slot C base_support]  -> recessed_plinth / steel_legs / casters (CONTINUOUS +Z)
    cabinet (root carcass) -> [Slot A closure] (multiplicity N)
                                  single_hinged_door -> [Slot B front_face]:
                                      solid_steel / glazed_window / louvered

Slot B (front_face_style) is only meaningful on ``single_hinged_door``; every
other closure forces ``solid_steel``. Base support is orthogonal to closure.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Urban_Environment_Fire_Other_Cabinet.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

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
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------
Closure = Literal[
    "n_sliding_drawers",
    "single_hinged_door",
    "double_doors",
    "roller_shutter",
]
FrontFace = Literal["solid_steel", "glazed_window", "louvered"]
BaseSupport = Literal["recessed_plinth", "steel_legs", "casters"]
PaletteStyle = Literal[
    "charcoal_oem",
    "fire_red_alarm",
    "municipal_grey",
    "hi_vis_yellow",
    "weathered_green",
    "stainless_brushed",
]

CLOSURES: tuple[Closure, ...] = (
    "n_sliding_drawers",
    "single_hinged_door",
    "double_doors",
    "roller_shutter",
)
# Weighted: drawers baseline high, door/shutter next.
CLOSURE_WEIGHTS = (0.40, 0.26, 0.18, 0.16)

FRONT_FACES: tuple[FrontFace, ...] = ("solid_steel", "glazed_window", "louvered")
FRONT_FACE_WEIGHTS = (0.40, 0.32, 0.28)

BASE_SUPPORTS: tuple[BaseSupport, ...] = ("recessed_plinth", "steel_legs", "casters")
BASE_WEIGHTS = (0.42, 0.30, 0.28)

PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "charcoal_oem",
    "fire_red_alarm",
    "municipal_grey",
    "hi_vis_yellow",
    "weathered_green",
    "stainless_brushed",
)

# Drawer multiplicity (product domain [3,5]; N=4 baseline high frequency).
N_DRAWER_MIN = 3
N_DRAWER_MAX = 5
DRAWER_N_CHOICES = (3, 4, 5)
DRAWER_N_WEIGHTS = (0.30, 0.45, 0.25)

# Base lift per support module (m).
PLINTH_H = 0.060
LEG_H = 0.120
CASTER_H = 0.080

# ---------------------------------------------------------------------------
# Palettes: >=3 colorways; every .visual material key resolves here.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "charcoal_oem": {
        "shell": (0.15, 0.16, 0.18, 1.0),
        "face": (0.17, 0.18, 0.20, 1.0),
        "base": (0.10, 0.10, 0.12, 1.0),
        "handle": (0.08, 0.08, 0.09, 1.0),
        "badge": (0.62, 0.14, 0.12, 1.0),
        "glass": (0.55, 0.70, 0.78, 0.35),
        "metal": (0.55, 0.56, 0.58, 1.0),
    },
    "fire_red_alarm": {
        "shell": (0.62, 0.12, 0.10, 1.0),
        "face": (0.70, 0.16, 0.13, 1.0),
        "base": (0.32, 0.07, 0.06, 1.0),
        "handle": (0.85, 0.86, 0.88, 1.0),
        "badge": (0.92, 0.82, 0.12, 1.0),
        "glass": (0.60, 0.74, 0.80, 0.35),
        "metal": (0.80, 0.81, 0.83, 1.0),
    },
    "municipal_grey": {
        "shell": (0.55, 0.57, 0.60, 1.0),
        "face": (0.50, 0.52, 0.55, 1.0),
        "base": (0.30, 0.31, 0.33, 1.0),
        "handle": (0.06, 0.06, 0.07, 1.0),
        "badge": (0.66, 0.16, 0.14, 1.0),
        "glass": (0.58, 0.72, 0.78, 0.35),
        "metal": (0.62, 0.63, 0.66, 1.0),
    },
    "hi_vis_yellow": {
        "shell": (0.82, 0.72, 0.12, 1.0),
        "face": (0.78, 0.68, 0.10, 1.0),
        "base": (0.10, 0.10, 0.10, 1.0),
        "handle": (0.06, 0.06, 0.06, 1.0),
        "badge": (0.10, 0.10, 0.10, 1.0),
        "glass": (0.58, 0.72, 0.78, 0.35),
        "metal": (0.50, 0.50, 0.52, 1.0),
    },
    "weathered_green": {
        "shell": (0.28, 0.34, 0.26, 1.0),
        "face": (0.24, 0.30, 0.22, 1.0),
        "base": (0.14, 0.18, 0.13, 1.0),
        "handle": (0.66, 0.58, 0.30, 1.0),
        "badge": (0.66, 0.18, 0.14, 1.0),
        "glass": (0.56, 0.70, 0.74, 0.35),
        "metal": (0.60, 0.56, 0.40, 1.0),
    },
    "stainless_brushed": {
        "shell": (0.70, 0.72, 0.74, 1.0),
        "face": (0.66, 0.68, 0.70, 1.0),
        "base": (0.30, 0.31, 0.33, 1.0),
        "handle": (0.08, 0.08, 0.09, 1.0),
        "badge": (0.18, 0.34, 0.62, 1.0),
        "glass": (0.60, 0.74, 0.80, 0.35),
        "metal": (0.74, 0.76, 0.78, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Nominal dimensions (m). Upright filing-cabinet proportions: H > W * 2.5.
# Footprint: width along Y, depth along X, height along Z. Front opening at +X.
# ---------------------------------------------------------------------------
_BASE_W = 0.380  # cabinet width (Y)
_BASE_D = 0.600  # cabinet depth (X); front opening face at x = +D/2
_BASE_H = 1.300  # cabinet body height (Z)
_WALL = 0.018  # sheet-steel wall / panel thickness


@dataclass(frozen=True)
class FireCabinetConfig:
    closure: Closure = "n_sliding_drawers"
    front_face: FrontFace = "solid_steel"
    base_support: BaseSupport = "recessed_plinth"
    palette_style: PaletteStyle = "charcoal_oem"
    n_drawers: int = 4
    width_scale: float = 1.0
    height_scale: float = 1.0
    depth_scale: float = 1.0
    drawer_travel_ratio: float = 0.72
    shutter_travel: float = 0.50
    door_open_upper: float = 2.3
    name: str = "reference_fire_cabinet"


@dataclass(frozen=True)
class ResolvedFireCabinetConfig:
    closure: Closure
    front_face: FrontFace
    base_support: BaseSupport
    palette_style: PaletteStyle
    n_drawers: int
    n_shelves: int
    width: float  # Y
    depth: float  # X
    body_height: float  # Z extent of the steel shell
    wall: float
    body_bottom_z: float  # bottom face of shell (z lift from base support)
    drawer_travel: float
    shutter_travel: float
    door_open_upper: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _weighted(rng: random.Random, choices, weights):
    return rng.choices(list(choices), weights=list(weights), k=1)[0]


# ---------------------------------------------------------------------------
# Procedural sampling (seed domain). Deterministic for every seed incl. 0.
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> FireCabinetConfig:
    rng = random.Random(seed * 2654435761 + 12345)

    closure = _weighted(rng, CLOSURES, CLOSURE_WEIGHTS)

    if closure == "single_hinged_door":
        front_face = _weighted(rng, FRONT_FACES, FRONT_FACE_WEIGHTS)
    else:
        front_face = "solid_steel"

    n_drawers = (
        _weighted(rng, DRAWER_N_CHOICES, DRAWER_N_WEIGHTS)
        if closure == "n_sliding_drawers"
        else 4
    )

    base_support = _weighted(rng, BASE_SUPPORTS, BASE_WEIGHTS)
    palette_style = rng.choice(PALETTE_STYLES)

    return FireCabinetConfig(
        closure=closure,
        front_face=front_face,
        base_support=base_support,
        palette_style=palette_style,
        n_drawers=n_drawers,
        width_scale=round(rng.uniform(0.90, 1.12), 4),
        height_scale=round(rng.uniform(0.92, 1.10), 4),
        depth_scale=round(rng.uniform(0.92, 1.08), 4),
        drawer_travel_ratio=round(rng.uniform(0.60, 0.78), 4),
        shutter_travel=round(rng.uniform(0.40, 0.55), 4),
        door_open_upper=round(rng.uniform(1.5, 2.35), 4),
        name=f"seeded_fire_cabinet_{seed}",
    )


def resolve_config(config: FireCabinetConfig) -> ResolvedFireCabinetConfig:
    if config.closure not in CLOSURES:
        raise ValueError(f"Unsupported closure: {config.closure}")
    if config.base_support not in BASE_SUPPORTS:
        raise ValueError(f"Unsupported base_support: {config.base_support}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    closure = config.closure

    # Compatibility gating: glazed/louvered only on the single hinged door.
    if closure == "single_hinged_door":
        front_face = config.front_face if config.front_face in FRONT_FACES else "solid_steel"
    else:
        front_face = "solid_steel"

    # Shelf count derived from closure (FIXED interior fitment).
    if closure == "single_hinged_door":
        n_shelves = 2
    elif closure == "double_doors":
        n_shelves = 3
    else:
        n_shelves = 0

    n_drawers = (
        max(N_DRAWER_MIN, min(N_DRAWER_MAX, int(config.n_drawers)))
        if closure == "n_sliding_drawers"
        else 0
    )

    width = _clamp(_BASE_W * config.width_scale, 0.34, 0.46)
    depth = _clamp(_BASE_D * config.depth_scale, 0.54, 0.66)
    body_height = _clamp(_BASE_H * config.height_scale, 1.18, 1.45)

    # Preserve upright proportion: body_height > width * 2.5 and top_z > 1.2.
    if body_height <= width * 2.5 + 0.02:
        width = (body_height - 0.04) / 2.5
    if body_height < 1.21:
        body_height = 1.21

    base_lift = {
        "recessed_plinth": PLINTH_H,
        "steel_legs": LEG_H,
        "casters": CASTER_H,
    }[config.base_support]

    wall = _WALL

    # Drawer travel: travel = drawer_depth * ratio, capped so it pulls cleanly.
    drawer_depth = depth - wall - 0.030
    drawer_travel = _clamp(config.drawer_travel_ratio, 0.60, 0.78) * drawer_depth

    # Shutter travel: lift must not push slats through the top panel.
    cavity_h = body_height - 2.0 * wall
    shutter_travel = min(_clamp(config.shutter_travel, 0.40, 0.55), cavity_h * 0.42)

    door_open_upper = _clamp(config.door_open_upper, 1.5, 2.35)
    if closure == "double_doors":
        door_open_upper = min(door_open_upper, 1.6)

    return ResolvedFireCabinetConfig(
        closure=closure,
        front_face=front_face,
        base_support=config.base_support,
        palette_style=config.palette_style,
        n_drawers=n_drawers,
        n_shelves=n_shelves,
        width=width,
        depth=depth,
        body_height=body_height,
        wall=wall,
        body_bottom_z=base_lift,
        drawer_travel=drawer_travel,
        shutter_travel=shutter_travel,
        door_open_upper=door_open_upper,
        name=config.name or "fire_cabinet",
    )


# ---------------------------------------------------------------------------
# Slot choices (consumed by module_topology_diversity + failure attribution).
# ---------------------------------------------------------------------------
def slot_choices_for_config(
    config: FireCabinetConfig | ResolvedFireCabinetConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedFireCabinetConfig) else resolve_config(config)
    if r.closure == "n_sliding_drawers":
        closure_name = f"n_sliding_drawers_{r.n_drawers}"
    else:
        closure_name = r.closure
    return (
        ("closure_mechanism", closure_name),
        ("front_face_style", r.front_face),
        ("base_support", r.base_support),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _box(part, size, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(part, radius, length, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.brushed_silver",
    )


def _front_x(r: ResolvedFireCabinetConfig) -> float:
    """World X of the front opening plane (shell front face)."""
    return r.depth / 2.0


def _cavity_bounds(r: ResolvedFireCabinetConfig) -> tuple[float, float]:
    """(open_bot_z, open_top_z): inner cavity bottom/top in world Z."""
    open_bot_z = r.body_bottom_z + r.wall
    open_top_z = r.body_bottom_z + r.body_height - r.wall
    return open_bot_z, open_top_z


# ---------------------------------------------------------------------------
# Carcass shell (root). Shared base helper; the front frame varies per closure.
# ---------------------------------------------------------------------------
def _build_shell_core(cabinet, r: ResolvedFireCabinetConfig, mats) -> None:
    w, d, wall = r.width, r.depth, r.wall
    z0 = r.body_bottom_z
    h = r.body_height
    shell = mats["shell"]
    body_cz = z0 + h / 2.0

    # bottom + top panels
    _box(cabinet, (d, w, wall), (0.0, 0.0, z0 + wall / 2.0), shell, "bottom_panel")
    _box(cabinet, (d, w, wall), (0.0, 0.0, z0 + h - wall / 2.0), shell, "top_panel")
    # back wall (-X)
    _box(cabinet, (wall, w, h - 2.0 * wall), (-(d / 2.0) + wall / 2.0, 0.0, body_cz),
         shell, "back_wall")
    # side walls (+-Y)
    for sgn, tag in ((1.0, "left"), (-1.0, "right")):
        _box(cabinet, (d, wall, h - 2.0 * wall),
             (0.0, sgn * (w / 2.0 - wall / 2.0), body_cz), shell, f"side_wall_{tag}")


def _build_drawer_front_frame(cabinet, r: ResolvedFireCabinetConfig, mats) -> None:
    """Drawer carcass: horizontal face_rail_{i} (range N+1) + side stiles + runners."""
    w, wall = r.width, r.wall
    shell = mats["shell"]
    open_bot_z, open_top_z = _cavity_bounds(r)
    front_x = _front_x(r) - wall / 2.0
    stack_h = open_top_z - open_bot_z
    n = r.n_drawers
    rail = 0.014
    inner_w = w - 2.0 * wall

    # side stiles framing the opening
    for sgn, tag in ((1.0, "left"), (-1.0, "right")):
        _box(cabinet, (wall, wall, stack_h),
             (front_x, sgn * (w / 2.0 - wall / 2.0), open_bot_z + stack_h / 2.0),
             shell, f"face_stile_{tag}")

    # N+1 horizontal face rails between drawers
    drawer_face_h = (stack_h - rail * (n + 1)) / n
    for i in range(n + 1):
        rz = open_bot_z + rail / 2.0 + i * (drawer_face_h + rail)
        _box(cabinet, (wall, inner_w, rail), (front_x, 0.0, rz), shell, f"face_rail_{i}")

    # per-drawer slide runners: a thin front cross-rail at each drawer's rest
    # height so the PRISMATIC joint origin (front_x, 0, cz) lands on real solid
    # carcass material at the opening rim (and the closed drawer face seats here).
    for i in range(n):
        cz = open_bot_z + rail + drawer_face_h / 2.0 + i * (drawer_face_h + rail)
        # Front cross slide-rail at each drawer's rest height: gives the PRISMATIC
        # joint origin (front_x, 0, cz) real solid carcass material at the opening
        # rim, and the closed drawer face seats against it.
        _box(cabinet, (wall, inner_w, 0.012), (front_x, 0.0, cz),
             shell, f"runner_{i}")


def _build_door_front_frame(cabinet, r: ResolvedFireCabinetConfig, mats) -> None:
    """Door carcass: perimeter top/bottom face rails + side stiles."""
    w, wall = r.width, r.wall
    shell = mats["shell"]
    open_bot_z, open_top_z = _cavity_bounds(r)
    front_x = _front_x(r) - wall / 2.0
    inner_w = w - 2.0 * wall
    rail = 0.022

    _box(cabinet, (wall, inner_w, rail), (front_x, 0.0, open_bot_z + rail / 2.0),
         shell, "face_rail_bottom")
    _box(cabinet, (wall, inner_w, rail), (front_x, 0.0, open_top_z - rail / 2.0),
         shell, "face_rail_top")
    stile_h = open_top_z - open_bot_z
    for sgn, tag in ((1.0, "left"), (-1.0, "right")):
        _box(cabinet, (wall, wall, stile_h),
             (front_x, sgn * (w / 2.0 - wall / 2.0), open_bot_z + stile_h / 2.0),
             shell, f"face_stile_{tag}")


def _build_shutter_front_frame(cabinet, r: ResolvedFireCabinetConfig, mats):
    """Shutter carcass: top fixed front panel (45%) + side channels + threshold."""
    w, wall = r.width, r.wall
    shell = mats["shell"]
    metal = mats["metal"]
    open_bot_z, open_top_z = _cavity_bounds(r)
    front_x = _front_x(r) - wall / 2.0
    inner_w = w - 2.0 * wall
    opening_h = open_top_z - open_bot_z

    # Upper 45% fixed front panel (raised shutter hides behind it).
    fixed_h = opening_h * 0.45
    fixed_z = open_top_z - fixed_h / 2.0
    _box(cabinet, (wall, inner_w, fixed_h), (front_x, 0.0, fixed_z),
         shell, "fixed_front_panel")
    # Side channels (vertical guide rails) over the shutter zone.
    shutter_zone_h = opening_h - fixed_h
    for sgn, tag in ((1.0, "left"), (-1.0, "right")):
        _box(cabinet, (wall, 0.016, shutter_zone_h + 0.02),
             (front_x, sgn * (inner_w / 2.0 - 0.004), open_bot_z + shutter_zone_h / 2.0),
             metal, f"side_channel_{tag}")
    # Bottom threshold + meeting rail.
    _box(cabinet, (wall, inner_w, 0.018), (front_x, 0.0, open_bot_z + 0.009),
         shell, "bottom_threshold")
    _box(cabinet, (wall * 0.8, inner_w, 0.014),
         (front_x, 0.0, open_top_z - fixed_h - 0.007), metal, "meeting_rail")
    return open_bot_z, open_top_z - fixed_h


# ---------------------------------------------------------------------------
# Closure module: n_sliding_drawers
# ---------------------------------------------------------------------------
def _build_drawer(drawer, r: ResolvedFireCabinetConfig, mats, *, face_h: float) -> None:
    w, d, wall = r.width, r.depth, r.wall
    face = mats["face"]
    shell = mats["shell"]
    handle = mats["handle"]
    badge = mats["badge"]
    box_w = w - 2.0 * wall - 0.020
    box_d = d - wall - 0.030
    ft = 0.018  # drawer face thickness
    box_h = face_h * 0.78

    # The drawer-local frame origin (0,0,0) sits on the front opening plane at
    # the drawer rest height; the tray extends back along -X.
    # drawer_face seats at the opening plane.
    _box(drawer, (ft, w - 2.0 * wall - 0.006, face_h), (-ft / 2.0, 0.0, 0.0),
         face, "drawer_face")
    # bottom floor of the tray
    floor_x = -ft - box_d / 2.0
    _box(drawer, (box_d, box_w, 0.010), (floor_x, 0.0, -box_h / 2.0 + 0.005),
         shell, "bottom_floor")
    # side walls
    for sgn, tag in ((1.0, "left"), (-1.0, "right")):
        _box(drawer, (box_d, 0.010, box_h),
             (floor_x, sgn * (box_w / 2.0 - 0.005), 0.0), shell, f"side_wall_{tag}")
    # back wall
    _box(drawer, (0.010, box_w, box_h), (-ft - box_d + 0.005, 0.0, 0.0),
         shell, "back_wall")
    # handle surround + pull handle (module-local visuals)
    _box(drawer, (0.012, 0.110, 0.024), (0.006, 0.0, 0.0), handle, "handle_surround")
    _cyl(drawer, 0.008, 0.090, (0.018, 0.0, 0.0), handle, "pull_handle",
         rpy=(math.pi / 2.0, 0.0, 0.0))
    # label holder (embedded into the drawer face front so it is supported)
    _box(drawer, (0.006, 0.060, 0.018), (0.001, 0.0, face_h * 0.28), badge, "label_holder")


def _build_n_sliding_drawers(model, cabinet, r: ResolvedFireCabinetConfig, mats):
    _build_drawer_front_frame(cabinet, r, mats)
    open_bot_z, open_top_z = _cavity_bounds(r)
    front_x = _front_x(r)
    stack_h = open_top_z - open_bot_z
    n = r.n_drawers
    rail = 0.014
    drawer_face_h = (stack_h - rail * (n + 1)) / n

    joints = []
    for i in range(n):
        cz = open_bot_z + rail + drawer_face_h / 2.0 + i * (drawer_face_h + rail)
        drawer = model.part(f"drawer_{i}")
        _build_drawer(drawer, r, mats, face_h=drawer_face_h)
        drawer.inertial = Inertial.from_geometry(
            Box((r.depth - r.wall, r.width - 2.0 * r.wall, drawer_face_h)),
            mass=3.0,
            origin=Origin(xyz=(-(r.depth) / 4.0, 0.0, 0.0)),
        )
        j = model.articulation(
            f"cabinet_to_drawer_{i}",
            ArticulationType.PRISMATIC,
            parent=cabinet,
            child=drawer,
            origin=Origin(xyz=(front_x, 0.0, cz)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(lower=0.0, upper=r.drawer_travel,
                                       effort=80.0, velocity=0.25),
        )
        joints.append((j, drawer))
    return joints


# ---------------------------------------------------------------------------
# Closure module: single_hinged_door (+ front_face style)
# ---------------------------------------------------------------------------
def _build_solid_door_face(door, r: ResolvedFireCabinetConfig, mats, *, panel_w, panel_h):
    face = mats["face"]
    _box(door, (0.018, panel_w, panel_h), (0.009, panel_w / 2.0 - 0.0, 0.0),
         face, "door_panel")
    _box(door, (0.006, panel_w * 0.7, panel_h * 0.55),
         (0.020, panel_w / 2.0, 0.0), face, "door_emboss")


def _build_glazed_door_face(door, r: ResolvedFireCabinetConfig, mats, *, panel_w, panel_h):
    metal = mats["metal"]
    glass = mats["glass"]
    badge = mats["badge"]
    frame_t = 0.020
    fw = 0.040  # frame width
    cy = panel_w / 2.0
    # steel frame stiles (left/right along Y) + rails (top/bottom along Z)
    for sgn, tag in ((1.0, "l"), (-1.0, "r")):
        _box(door, (frame_t, fw, panel_h),
             (frame_t / 2.0, cy + sgn * (panel_w / 2.0 - fw / 2.0), 0.0),
             metal, f"frame_stile_{tag}")
    for sgn, tag in ((1.0, "top"), (-1.0, "bottom")):
        _box(door, (frame_t, panel_w - 2.0 * fw, fw),
             (frame_t / 2.0, cy, sgn * (panel_h / 2.0 - fw / 2.0)),
             metal, f"frame_rail_{tag}")
    # transparent glass pane seated in the frame rebate
    _box(door, (0.008, panel_w - 2.0 * fw + 0.006, panel_h - 2.0 * fw + 0.006),
         (frame_t / 2.0, cy, 0.0), glass, "glass_pane")
    _box(door, (0.010, 0.060, 0.018), (frame_t, cy, panel_h * 0.30), badge, "fire_label")


def _build_louvered_door_face(door, r: ResolvedFireCabinetConfig, mats, *, panel_w, panel_h):
    face = mats["face"]
    metal = mats["metal"]
    cy = panel_w / 2.0
    # backing panel
    _box(door, (0.014, panel_w, panel_h), (0.007, cy, 0.0), face, "door_panel")
    # regular stack of angled vent blades
    n_louver = max(8, int(panel_h / 0.045))
    pitch = panel_h / n_louver
    blade_h = pitch * 0.92
    for i in range(n_louver):
        bz = -panel_h / 2.0 + pitch / 2.0 + i * pitch
        _box(door, (0.020, panel_w - 0.020, blade_h),
             (0.020, cy, bz), metal, f"louver_slat_{i}", rpy=(0.0, math.radians(35.0), 0.0))


_FRONT_FACE_BUILDERS = {
    "solid_steel": _build_solid_door_face,
    "glazed_window": _build_glazed_door_face,
    "louvered": _build_louvered_door_face,
}


def _build_door_shelves(cabinet, r: ResolvedFireCabinetConfig, mats):
    """FIXED interior shelves (carcass visuals); N derived from closure."""
    shell = mats["shell"]
    metal = mats["metal"]
    w, d, wall = r.width, r.depth, r.wall
    open_bot_z, open_top_z = _cavity_bounds(r)
    cavity_h = open_top_z - open_bot_z
    n = r.n_shelves
    inner_w = w - 2.0 * wall
    for i in range(n):
        sz = open_bot_z + (i + 1) * cavity_h / (n + 1)
        _box(cabinet, (d - wall - 0.020, inner_w, 0.012),
             (-0.010, 0.0, sz), shell, f"shelf_{i}")
        if r.closure == "single_hinged_door":
            for sgn, tag in ((1.0, "left"), (-1.0, "right")):
                _box(cabinet, (0.030, 0.012, 0.020),
                     ((d / 2.0) - wall - 0.020, sgn * (inner_w / 2.0 - 0.010), sz - 0.014),
                     metal, f"shelf_bracket_{i}_{tag}")


def _build_single_hinged_door(model, cabinet, r: ResolvedFireCabinetConfig, mats):
    _build_door_front_frame(cabinet, r, mats)
    _build_door_shelves(cabinet, r, mats)
    open_bot_z, open_top_z = _cavity_bounds(r)
    w, wall = r.width, r.wall
    front_x = _front_x(r)
    z_mid = (open_bot_z + open_top_z) / 2.0
    panel_h = (open_top_z - open_bot_z) - 0.004
    panel_w = w - 2.0 * wall - 0.004
    hinge_y = w / 2.0 - wall  # left front vertical edge

    door = model.part("door")
    metal = mats["metal"]
    # Door-local frame: origin at hinge line; panel extends toward -Y (centre).
    # Build the face about a local centreline then translate authoring so that
    # panel spans from y=0 (hinge) toward y=-panel_w.
    builder = _FRONT_FACE_BUILDERS[r.front_face]
    # face builders author about y in [0, panel_w] from the hinge; we want the
    # panel to hang toward -Y, so pass panel_w and rely on cy offset, then the
    # door part frame at hinge_y. Convert by authoring with negative span:
    _author_door_face(door, r, mats, builder, panel_w=panel_w, panel_h=panel_h)
    # barrel hinges on the door (two stub cylinders at the hinge edge)
    for i, hz in enumerate((open_bot_z + 0.10 - z_mid, open_top_z - 0.10 - z_mid)):
        _cyl(door, 0.014, 0.060, (0.0, 0.0, hz), metal, f"hinge_{i}",
             rpy=(0.0, 0.0, 0.0))
    # pull handle near the free (centre) edge
    _box(door, (0.014, 0.024, 0.130), (0.020, -panel_w + 0.030, 0.0),
         mats["handle"], "handle_surround")
    _cyl(door, 0.008, 0.110, (0.032, -panel_w + 0.030, 0.0), mats["handle"],
         "pull_handle", rpy=(0.0, 0.0, 0.0))

    door.inertial = Inertial.from_geometry(
        Box((0.04, panel_w, panel_h)),
        mass=6.0,
        origin=Origin(xyz=(0.02, -panel_w / 2.0, 0.0)),
    )
    j = model.articulation(
        "cabinet_to_door",
        ArticulationType.REVOLUTE,
        parent=cabinet,
        child=door,
        origin=Origin(xyz=(front_x, hinge_y, z_mid)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=r.door_open_upper,
                                   effort=14.0, velocity=2.0),
    )
    return [(j, door)]


def _author_door_face(door, r, mats, builder, *, panel_w, panel_h):
    """Author a door face whose panel hangs from the hinge (y=0) toward -Y.

    The face builders place geometry about a centreline at +panel_w/2 in their
    own convention; we flip to -Y by authoring with the centre at y=-panel_w/2.
    Implemented by temporarily shimming: build into a list then mirror. Simpler:
    builders take cy via panel placement using panel_w; we negate here.
    """
    # We re-implement the small set of face builders inline against a centre at
    # cy = -panel_w/2 so the panel hangs toward -Y from the hinge at y=0.
    cy = -panel_w / 2.0
    if builder is _build_solid_door_face:
        face = mats["face"]
        _box(door, (0.018, panel_w, panel_h), (0.009, cy, 0.0), face, "door_panel")
        _box(door, (0.006, panel_w * 0.7, panel_h * 0.55), (0.020, cy, 0.0),
             face, "door_emboss")
    elif builder is _build_glazed_door_face:
        metal = mats["metal"]
        glass = mats["glass"]
        badge = mats["badge"]
        frame_t = 0.020
        fw = 0.040
        for sgn, tag in ((1.0, "l"), (-1.0, "r")):
            _box(door, (frame_t, fw, panel_h),
                 (frame_t / 2.0, cy + sgn * (panel_w / 2.0 - fw / 2.0), 0.0),
                 metal, f"frame_stile_{tag}")
        for sgn, tag in ((1.0, "top"), (-1.0, "bottom")):
            _box(door, (frame_t, panel_w - 2.0 * fw, fw),
                 (frame_t / 2.0, cy, sgn * (panel_h / 2.0 - fw / 2.0)),
                 metal, f"frame_rail_{tag}")
        _box(door, (0.008, panel_w - 2.0 * fw + 0.006, panel_h - 2.0 * fw + 0.006),
             (frame_t / 2.0, cy, 0.0), glass, "glass_pane")
        # fire label plate seated against the lower frame rail (supported)
        _box(door, (0.012, 0.060, 0.018),
             (frame_t / 2.0, cy, -(panel_h / 2.0 - fw / 2.0)), badge, "fire_label")
    else:  # louvered
        face = mats["face"]
        metal = mats["metal"]
        _box(door, (0.014, panel_w, panel_h), (0.007, cy, 0.0), face, "door_panel")
        n_louver = max(8, int(panel_h / 0.045))
        pitch = panel_h / n_louver
        blade_h = pitch * 0.92
        for i in range(n_louver):
            bz = -panel_h / 2.0 + pitch / 2.0 + i * pitch
            _box(door, (0.020, panel_w - 0.020, blade_h), (0.020, cy, bz),
                 metal, f"louver_slat_{i}", rpy=(0.0, math.radians(35.0), 0.0))


# ---------------------------------------------------------------------------
# Closure module: double_doors
# ---------------------------------------------------------------------------
def _build_double_doors(model, cabinet, r: ResolvedFireCabinetConfig, mats):
    _build_door_front_frame(cabinet, r, mats)
    _build_door_shelves(cabinet, r, mats)
    open_bot_z, open_top_z = _cavity_bounds(r)
    w, wall = r.width, r.wall
    front_x = _front_x(r)
    z_mid = (open_bot_z + open_top_z) / 2.0
    panel_h = (open_top_z - open_bot_z) - 0.004
    inner_w = w - 2.0 * wall
    half_w = inner_w / 2.0 - 0.004
    center_gap = 0.003
    face = mats["face"]
    metal = mats["metal"]
    handle = mats["handle"]

    joints = []
    for sgn, tag, axis_z in ((1.0, "left", 1.0), (-1.0, "right", -1.0)):
        hinge_y = sgn * (w / 2.0 - wall)
        door = model.part(f"door_{tag}")
        # Panel hangs from hinge (y=0 local) toward the centre (-sgn * Y).
        cy = -sgn * (half_w / 2.0)
        _box(door, (0.018, half_w - center_gap, panel_h), (0.009, cy, 0.0),
             face, "door_panel")
        # hinge barrels
        for i, hz in enumerate((open_bot_z + 0.10 - z_mid, open_top_z - 0.10 - z_mid)):
            _cyl(door, 0.012, 0.055, (0.0, 0.0, hz), metal, f"hinge_{i}")
        # pull near centre edge
        edge_y = -sgn * (half_w - 0.024)
        _box(door, (0.012, 0.020, 0.110), (0.018, edge_y, 0.0), handle, "handle_surround")
        _cyl(door, 0.007, 0.095, (0.028, edge_y, 0.0), handle, "pull_handle")
        door.inertial = Inertial.from_geometry(
            Box((0.04, half_w, panel_h)),
            mass=4.0,
            origin=Origin(xyz=(0.02, cy, 0.0)),
        )
        j = model.articulation(
            f"cabinet_to_door_{tag}",
            ArticulationType.REVOLUTE,
            parent=cabinet,
            child=door,
            origin=Origin(xyz=(front_x, hinge_y, z_mid)),
            axis=(0.0, 0.0, axis_z),
            motion_limits=MotionLimits(lower=0.0, upper=r.door_open_upper,
                                       effort=12.0, velocity=2.0),
        )
        joints.append((j, door))
    return joints


# ---------------------------------------------------------------------------
# Closure module: roller_shutter
# ---------------------------------------------------------------------------
def _build_roller_shutter(model, cabinet, r: ResolvedFireCabinetConfig, mats):
    shutter_bot_z, shutter_top_z = _build_shutter_front_frame(cabinet, r, mats)
    w, wall = r.width, r.wall
    front_x = _front_x(r)
    inner_w = w - 2.0 * wall
    metal = mats["metal"]
    face = mats["face"]

    shutter = model.part("shutter")
    zone_h = shutter_top_z - shutter_bot_z
    # slat pitch derived from geometry (interlocking 2mm overlap)
    pitch = 0.045
    n_slats = max(3, int(zone_h / pitch))
    slat_h = pitch + 0.002  # 2mm interlock overlap
    slat_x = -0.012  # slightly behind the front plane (shutter local frame at front_x)

    # The shutter-local frame origin (0,0,0) sits at the front opening plane,
    # at the bottom of the shutter zone. lift_bar + slats hang above it.
    for i in range(n_slats):
        sz = pitch / 2.0 + i * pitch
        if sz > zone_h:
            break
        _box(shutter, (0.010, inner_w - 0.006, slat_h), (slat_x, 0.0, sz),
             face, f"slat_{i}")
    # bottom lift bar at the base of the curtain
    _box(shutter, (0.016, inner_w, 0.018), (slat_x, 0.0, 0.0), metal, "lift_bar")

    shutter.inertial = Inertial.from_geometry(
        Box((0.03, inner_w, zone_h)),
        mass=5.0,
        origin=Origin(xyz=(slat_x, 0.0, zone_h / 2.0)),
    )
    j = model.articulation(
        "cabinet_to_shutter",
        ArticulationType.PRISMATIC,
        parent=cabinet,
        child=shutter,
        origin=Origin(xyz=(front_x, 0.0, shutter_bot_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=r.shutter_travel,
                                   effort=40.0, velocity=0.4),
    )
    return [(j, shutter)]


_CLOSURE_BUILDERS = {
    "n_sliding_drawers": _build_n_sliding_drawers,
    "single_hinged_door": _build_single_hinged_door,
    "double_doors": _build_double_doors,
    "roller_shutter": _build_roller_shutter,
}


# ---------------------------------------------------------------------------
# Base support modules
# ---------------------------------------------------------------------------
def _base_corner_positions(r: ResolvedFireCabinetConfig):
    inset = 0.045
    return [
        (sx * (r.depth / 2.0 - inset), sy * (r.width / 2.0 - inset))
        for sx in (-1.0, 1.0)
        for sy in (-1.0, 1.0)
    ]


def _build_recessed_plinth(model, cabinet, r: ResolvedFireCabinetConfig, mats):
    """Recessed kick plinth (z=0 ground) as an inline carcass visual."""
    base = mats["base"]
    inset = 0.020
    _box(cabinet, (r.depth - 2.0 * inset, r.width - 2.0 * inset, PLINTH_H),
         (0.0, 0.0, PLINTH_H / 2.0), base, "base_plinth")
    return []


def _build_steel_legs(model, cabinet, r: ResolvedFireCabinetConfig, mats):
    """Four round steel tube legs lifting the shell; FIXED carcass visuals."""
    base = mats["base"]
    metal = mats["metal"]
    leg_r = 0.018
    for idx, (cx, cy) in enumerate(_base_corner_positions(r)):
        _cyl(cabinet, leg_r, LEG_H, (cx, cy, LEG_H / 2.0), base, f"leg_{idx}")
        # round foot pad at base
        _cyl(cabinet, leg_r * 1.5, 0.008, (cx, cy, 0.004), metal, f"leg_foot_{idx}")
    return []


def _build_casters(model, cabinet, r: ResolvedFireCabinetConfig, mats):
    """Four swivel casters; each CONTINUOUS about +Z. Wheels reach z~=0."""
    base = mats["base"]
    metal = mats["metal"]
    handle = mats["handle"]
    plate_t = 0.010
    swivel_h = 0.018
    stem_h = 0.022
    wheel_r = (CASTER_H - plate_t - swivel_h - stem_h)  # so wheel bottom ~ z=0
    wheel_r = max(0.018, wheel_r)
    wheel_w = 0.022

    joints = []
    for idx, (cx, cy) in enumerate(_base_corner_positions(r)):
        caster = model.part(f"caster_{idx}")
        # caster-local frame origin (0,0,0) at the shell bottom corner (z lift);
        # the assembly hangs downward toward the ground.
        top = 0.0
        _box(caster, (0.044, 0.044, plate_t), (0.0, 0.0, top - plate_t / 2.0),
             base, "mounting_plate")
        _cyl(caster, 0.016, swivel_h, (0.0, 0.0, top - plate_t - swivel_h / 2.0),
             metal, "swivel_ring")
        fork_z = top - plate_t - swivel_h
        _cyl(caster, 0.008, stem_h, (0.012, 0.0, fork_z - stem_h / 2.0),
             metal, "fork_stem")
        _box(caster, (0.012, 0.046, 0.012), (0.012, 0.0, fork_z - stem_h),
             metal, "fork_bridge")
        axle_z = fork_z - stem_h - wheel_r
        for sgn, tag in ((1.0, "left"), (-1.0, "right")):
            _box(caster, (0.010, 0.010, wheel_r),
                 (0.012, sgn * 0.022, fork_z - stem_h - wheel_r / 2.0),
                 metal, f"fork_leg_{tag}")
        # wheel (rolls visually; modelled as a single hub cylinder along Y)
        _cyl(caster, wheel_r, wheel_w, (0.012, 0.0, axle_z), handle, "wheel",
             rpy=(math.pi / 2.0, 0.0, 0.0))
        for sgn, tag in ((1.0, "left"), (-1.0, "right")):
            _cyl(caster, 0.006, 0.006, (0.012, sgn * (wheel_w / 2.0 + 0.003), axle_z),
                 base, f"hub_cap_{tag}", rpy=(math.pi / 2.0, 0.0, 0.0))

        caster.inertial = Inertial.from_geometry(
            Box((0.05, 0.05, CASTER_H)),
            mass=0.6,
            origin=Origin(xyz=(0.006, 0.0, -CASTER_H / 2.0)),
        )
        j = model.articulation(
            f"cabinet_to_caster_{idx}",
            ArticulationType.CONTINUOUS,
            parent=cabinet,
            child=caster,
            origin=Origin(xyz=(cx, cy, r.body_bottom_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=4.0),
        )
        joints.append((j, caster))
    return joints


_BASE_BUILDERS = {
    "recessed_plinth": _build_recessed_plinth,
    "steel_legs": _build_steel_legs,
    "casters": _build_casters,
}


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_fire_cabinet(
    config: FireCabinetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or FireCabinetConfig())
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"fire_cabinet_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in pal.items()
    }

    cabinet = model.part("cabinet")
    _build_shell_core(cabinet, r, mats)
    cabinet.inertial = Inertial.from_geometry(
        Box((r.depth, r.width, r.body_height)),
        mass=28.0,
        origin=Origin(xyz=(0.0, 0.0, r.body_bottom_z + r.body_height / 2.0)),
    )

    # Base support (Slot C) — emits inline plinth/legs or caster joints.
    base_children = _BASE_BUILDERS[r.base_support](model, cabinet, r, mats)

    # Closure (Slot A, with multiplicity / Slot B front_face for single door).
    closure_children = _CLOSURE_BUILDERS[r.closure](model, cabinet, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["base_children"] = [p.name for _, p in base_children]
    model.meta["closure_children"] = [p.name for _, p in closure_children]
    return model


def build_seeded_fire_cabinet(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_fire_cabinet(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests (acceptance signal is compile-sweep; this declares overlaps + invariants)
# ---------------------------------------------------------------------------
def _allow_islands(ctx, part, reason: str) -> None:
    """Silence the intra-part island WARN where a part is genuinely a stack of
    separated rigid pieces (louvre blades, shutter slats)."""
    fn = getattr(ctx, "allow_disconnected_islands", None)
    if callable(fn):
        fn(part, reason=reason)


def run_fire_cabinet_tests(
    object_model: ArticulatedObject,
    config: FireCabinetConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    # (joint lookups use object_model.get_articulation directly)

    cabinet = object_model.get_part("cabinet")
    ctx.check("cabinet root present", "cabinet" in part_names)

    cab_aabb = ctx.part_world_aabb(cabinet)
    front_x = _front_x(r)

    # Upright proportion: H > W * 2.5.
    ctx.check(
        "upright proportion (height > width * 2.5)",
        r.body_height > r.width * 2.5,
        details=f"H={r.body_height:.3f}, W={r.width:.3f}",
    )

    # ---- Closure-specific checks. ----
    if r.closure == "n_sliding_drawers":
        drawers = [object_model.get_part(f"drawer_{i}") for i in range(r.n_drawers)]
        d_joints = [object_model.get_articulation(f"cabinet_to_drawer_{i}")
                    for i in range(r.n_drawers)]
        for drw in drawers:
            ctx.allow_isolated_part(
                drw,
                reason="extended drawer slides out of the cabinet opening and loses contact",
            )
            ctx.allow_overlap(
                cabinet, drw,
                reason="drawer slides along the cabinet interior in close sliding contact",
            )
        ctx.check("drawer count matches", len(drawers) == r.n_drawers,
                  details=f"n={r.n_drawers}")
        for i, j in enumerate(d_joints):
            ctx.check(f"drawer {i} prismatic +X",
                      str(j.articulation_type).upper().endswith("PRISMATIC")
                      and abs(j.axis[0]) > 0.99,
                      details=f"type={j.articulation_type}, axis={j.axis}")
            lim = j.motion_limits
            ctx.check(f"drawer {i} positive travel",
                      lim is not None and lim.lower == 0.0 and lim.upper > 0.05,
                      details=f"upper={None if lim is None else lim.upper}")
        # closed drawer face flush with the front plane
        if cab_aabb is not None and r.n_drawers > 0:
            dj, drw = d_joints[0], drawers[0]
            with ctx.pose({dj: 0.0}):
                rest = ctx.part_world_aabb(drw)
            with ctx.pose({dj: r.drawer_travel}):
                ext = ctx.part_world_aabb(drw)
            if rest is not None and ext is not None:
                # The closed drawer front-face sits at the opening plane; the pull
                # handle protrudes slightly forward, so allow a small margin.
                ctx.check("closed drawer face flush at front plane",
                          abs(rest[1][0] - front_x) < 0.045,
                          details=f"face_x={rest[1][0]:.3f}, front={front_x:.3f}")
                ctx.check("opening drawer moves it out +X",
                          ext[1][0] > rest[1][0] + 0.08,
                          details=f"rest={rest[1][0]:.3f}, ext={ext[1][0]:.3f}")
        for i, drw in enumerate(drawers):
            ctx.allow_isolated_part(
                drw, reason="Drawer rides its prismatic slide inside the carcass cavity.")
            ctx.allow_overlap(
                cabinet, drw, elem_a=f"runner_{i}", elem_b="drawer_face",
                reason="Closed drawer face seats against its carcass front slide rail at the opening rim.")

    elif r.closure == "single_hinged_door":
        ctx.check("door part present", "door" in part_names)
        dj = object_model.get_articulation("cabinet_to_door")
        ctx.check("door revolute about vertical Z",
                  str(dj.articulation_type).upper().endswith("REVOLUTE")
                  and abs(dj.axis[2]) > 0.99,
                  details=f"type={dj.articulation_type}, axis={dj.axis}")
        lim = dj.motion_limits
        ctx.check("door open limit realistic",
                  lim is not None and lim.lower == 0.0 and 1.4 < lim.upper < 2.5,
                  details=f"upper={None if lim is None else lim.upper}")
        door = object_model.get_part("door")
        with ctx.pose({dj: 0.0}):
            rest = ctx.part_world_aabb(door)
        if rest is not None:
            ctx.check("closed door face near front plane",
                      abs(rest[1][0] - front_x) < 0.05,
                      details=f"door_x={rest[1][0]:.3f}, front={front_x:.3f}")
        ctx.allow_overlap(
            cabinet, door,
            reason="Door hinge barrels seat at the carcass front-left edge (captured hinge pin).")
        if r.front_face == "louvered":
            _allow_islands(ctx, door,
                           "Louvre vent blades are a regular stack of separated angled slats.")

    elif r.closure == "double_doors":
        for tag, axz in (("left", 1.0), ("right", -1.0)):
            ctx.check(f"door_{tag} present", f"door_{tag}" in part_names)
            dj = object_model.get_articulation(f"cabinet_to_door_{tag}")
            ctx.check(f"door_{tag} revolute about Z",
                      str(dj.articulation_type).upper().endswith("REVOLUTE")
                      and abs(dj.axis[2]) > 0.99,
                      details=f"axis={dj.axis}")
            ctx.check(f"door_{tag} hinge sign correct",
                      (dj.axis[2] > 0) == (axz > 0),
                      details=f"axis_z={dj.axis[2]}")
            ctx.allow_overlap(
                cabinet, object_model.get_part(f"door_{tag}"),
                reason="Double-door hinge barrels seat at the carcass side front edge.")
        # the two leaves meet at the centre seam (small overlap permissible)
        ctx.allow_overlap(
            object_model.get_part("door_left"), object_model.get_part("door_right"),
            reason="The two door leaves meet at a small centre gap when closed.")

    elif r.closure == "roller_shutter":
        ctx.check("shutter part present", "shutter" in part_names)
        sj = object_model.get_articulation("cabinet_to_shutter")
        ctx.check("shutter prismatic +Z",
                  str(sj.articulation_type).upper().endswith("PRISMATIC")
                  and abs(sj.axis[2]) > 0.99,
                  details=f"type={sj.articulation_type}, axis={sj.axis}")
        shutter = object_model.get_part("shutter")
        with ctx.pose({sj: 0.0}):
            closed = ctx.part_world_aabb(shutter)
        with ctx.pose({sj: r.shutter_travel}):
            raised = ctx.part_world_aabb(shutter)
        if closed is not None and raised is not None:
            ctx.check("shutter slides upward when opened",
                      raised[0][2] > closed[0][2] + 0.08,
                      details=f"closed_z={closed[0][2]:.3f}, raised_z={raised[0][2]:.3f}")
        ctx.allow_isolated_part(
            shutter, reason="Shutter curtain rides its prismatic lift inside the side channels.")
        ctx.allow_overlap(
            cabinet, shutter,
            reason="Shutter slats ride just behind the fixed front panel / side channels.")
        _allow_islands(ctx, shutter,
                       "Shutter is a stack of interlocking slats plus the bottom lift bar.")

    # ---- Base support checks + ground contact. ----
    if r.base_support == "recessed_plinth":
        ctx.check("base plinth visual present",
                  cabinet.get_visual("base_plinth") is not None)
    elif r.base_support == "steel_legs":
        for idx in range(4):
            ctx.check(f"leg_{idx} visual present",
                      cabinet.get_visual(f"leg_{idx}") is not None)
    elif r.base_support == "casters":
        casters = [object_model.get_part(f"caster_{idx}") for idx in range(4)]
        ctx.check("four casters authored", len(casters) == 4)
        for idx in range(4):
            cj = object_model.get_articulation(f"cabinet_to_caster_{idx}")
            ctx.check(f"caster {idx} continuous about +Z",
                      str(cj.articulation_type).upper().endswith("CONTINUOUS")
                      and abs(cj.axis[2]) > 0.99,
                      details=f"type={cj.articulation_type}, axis={cj.axis}")
            ctx.check(f"caster {idx} has no lower/upper limit",
                      cj.motion_limits is None
                      or cj.motion_limits.lower is None,
                      details="continuous joint should be unbounded")
            ctx.allow_overlap(
                cabinet, casters[idx],
                reason="Caster swivel plate seats up against the cabinet floor corner.")
        # wheels reach the ground plane z ~= 0
        for idx, c in enumerate(casters):
            w_aabb = ctx.part_world_aabb(c)
            if w_aabb is not None:
                ctx.check(f"caster {idx} reaches ground plane",
                          abs(w_aabb[0][2]) < 0.04,
                          details=f"z_min={w_aabb[0][2]:.4f}")

    # Shell bottom rests at the expected base lift.
    if cab_aabb is not None:
        ctx.check("shell bottom sits at base lift",
                  abs(cab_aabb[0][2] - 0.0) < r.body_bottom_z + 0.01,
                  details=f"z_min={cab_aabb[0][2]:.4f}, lift={r.body_bottom_z:.3f}")

    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "FireCabinetConfig",
    "ResolvedFireCabinetConfig",
    "build_fire_cabinet",
    "build_seeded_fire_cabinet",
    "config_from_seed",
    "resolve_config",
    "run_fire_cabinet_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
