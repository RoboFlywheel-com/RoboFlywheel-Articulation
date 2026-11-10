# SPDX-License-Identifier: Apache-2.0

"""Aquarium (glass fish-tank) — modular procedural template.

Category identity: a transparent hollow glass basin (separately-held panes/walls,
reads water-tight, NOT a solid block) in a black plastic rim/base frame, a top
lid (hinged hood + feed flap / sliding canopy / bifold twin leaves), filtration
hardware (hang-on-back / submerged internal / floor canister), a gravel substrate
bed, and rooted aquascape (rocks + N plant clusters).

Pattern: mixed — single ``tank_frame`` root; ``substrate`` and ``filter`` parent
to it (parallel children, FIXED); the lid parents to it (REVOLUTE/PRISMATIC) with
a nested ``feed_flap`` REVOLUTE for the hinged hood; ``plant_count`` is the one
multiplicity axis (plant clusters copied onto ``substrate``).

Slots (see specs_modular_v1/aquarium.md):
  A body_form (③ Primary Form Family, headline): rect / rounded / bowfront /
      cylinder / hexagon.
  B lid (② mechanism): hinged_hood / sliding_cover / bifold_canopy.
  C filter (① skeleton): hob / internal / canister.
  D aquascape multiplicity: plant_count N in [2, 8].

Body_form ↔ lid are coupled (lid shape derives from the tank's top opening):
sliding_cover / bifold_canopy are rect-family only; cylinder / hexagon force
hinged_hood; hob (needs a flat rear rim) is excluded on cylinder. See
``_compatible_lids`` / ``_compatible_filters``.

Sources (data/records/): ``..._001_...`` (rect HOB hood/flap), ``..._002_...``
(rounded internal hood/flap plants), ``rec_aquarium_var_bowfront`` / ``_cylinder``
/ ``_hexagon`` (③ forms), ``rec_aquarium_var_filter_canister``,
``rec_aquarium_var_lid_sliding`` / ``_lid_bifold``, ``rec_aquarium_var_plants_n2``
/ ``_plants_n7``.

Hinges are captured-pin barrels seated ~2 mm into ``hinge_mount`` ledges (both
geometric contact — guaranteeing support — and the rotational joint axis lands on
that hinge hardware); MatingContract intentionally omitted (grandfathered
pin-through-sleeve, AUTHORING §A Rule 2). Non-articulating detail (led, control
panel, buttons, gravel ridges, rocks, plants) is host-part ``visual(...)``
(Rule 1). No solid water block — an independent block would 穿 the separate
substrate/filter/plant parts (source 001 likewise carries no water volume).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

BodyForm = Literal["rect", "rounded", "bowfront", "cylinder", "hexagon"]
LidType = Literal["hinged_hood", "sliding_cover", "bifold_canopy"]
FilterType = Literal["hob", "internal", "canister"]
PaletteStyle = Literal["classic_warm", "cool_blue", "planted_green", "mono_black"]

BODY_FORMS: tuple[BodyForm, ...] = ("rect", "rounded", "bowfront", "cylinder", "hexagon")
LID_TYPES: tuple[LidType, ...] = ("hinged_hood", "sliding_cover", "bifold_canopy")
FILTER_TYPES: tuple[FilterType, ...] = ("hob", "internal", "canister")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_warm",
    "cool_blue",
    "planted_green",
    "mono_black",
)

# --- shared frame constants (real absolute dims; one-line basis each) ---------
GLASS_T = 0.005  # glass pane thickness
BASE_H = 0.035   # black base frame height
RIM_H = 0.026    # top rim frame height
RAIL_W = 0.026   # base/rim rail radial width
POST = 0.018     # corner post section
HOOD_T = 0.030   # molded hood shell thickness
BARREL_R = 0.008  # hinge barrel radius (standardized hardware)
LID_REAR_GAP = 0.040  # every closed lid stops this far forward of the inner rear
#                       wall, leaving an exposed rear strip for filtration hardware
#                       (real aquarium hoods carry a rear filter/cord cutout).

# plant multiplicity band (spec §8): small N frequent, large N rare.
PLANT_N_VALUES = (2, 3, 4, 5, 6, 7, 8)
PLANT_N_WEIGHTS = (0.10, 0.22, 0.26, 0.18, 0.12, 0.08, 0.04)

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "classic_warm": {
        "glass": (0.72, 0.92, 1.0, 0.32),
        "frame": (0.02, 0.02, 0.02, 1.0),
        "dark": (0.030, 0.032, 0.035, 1.0),
        "led": (1.0, 0.94, 0.68, 0.80),
        "gravel": (0.64, 0.58, 0.45, 1.0),
        "gravel_dark": (0.34, 0.33, 0.29, 1.0),
        "rock": (0.42, 0.42, 0.40, 1.0),
        "plant_a": (0.12, 0.60, 0.20, 1.0),
        "plant_b": (0.42, 0.90, 0.25, 1.0),
        "plant_c": (0.88, 0.30, 0.20, 1.0),
        "canister": (0.06, 0.12, 0.08, 1.0),
        "hose": (0.28, 0.30, 0.30, 1.0),
        "red": (0.85, 0.08, 0.04, 1.0),
        "orange": (0.95, 0.42, 0.05, 1.0),
        "green": (0.12, 0.68, 0.18, 1.0),
    },
    "cool_blue": {
        "glass": (0.70, 0.86, 1.0, 0.30),
        "frame": (0.03, 0.04, 0.06, 1.0),
        "dark": (0.02, 0.03, 0.05, 1.0),
        "led": (0.25, 0.90, 1.0, 0.75),
        "gravel": (0.10, 0.45, 0.78, 1.0),
        "gravel_dark": (0.06, 0.28, 0.52, 1.0),
        "rock": (0.36, 0.40, 0.44, 1.0),
        "plant_a": (0.10, 0.58, 0.30, 1.0),
        "plant_b": (0.40, 0.88, 0.55, 1.0),
        "plant_c": (0.88, 0.08, 0.45, 1.0),
        "canister": (0.10, 0.12, 0.16, 1.0),
        "hose": (0.20, 0.24, 0.30, 1.0),
        "red": (0.90, 0.20, 0.20, 1.0),
        "orange": (0.98, 0.55, 0.10, 1.0),
        "green": (0.10, 0.72, 0.55, 1.0),
    },
    "planted_green": {
        "glass": (0.74, 0.94, 0.90, 0.30),
        "frame": (0.05, 0.05, 0.04, 1.0),
        "dark": (0.04, 0.05, 0.04, 1.0),
        "led": (0.85, 1.0, 0.70, 0.78),
        "gravel": (0.28, 0.22, 0.16, 1.0),
        "gravel_dark": (0.16, 0.13, 0.10, 1.0),
        "rock": (0.30, 0.32, 0.30, 1.0),
        "plant_a": (0.14, 0.55, 0.16, 1.0),
        "plant_b": (0.36, 0.82, 0.22, 1.0),
        "plant_c": (0.66, 0.80, 0.20, 1.0),
        "canister": (0.08, 0.14, 0.08, 1.0),
        "hose": (0.26, 0.30, 0.24, 1.0),
        "red": (0.80, 0.20, 0.10, 1.0),
        "orange": (0.92, 0.50, 0.08, 1.0),
        "green": (0.16, 0.70, 0.20, 1.0),
    },
    "mono_black": {
        "glass": (0.86, 0.90, 0.94, 0.28),
        "frame": (0.015, 0.015, 0.017, 1.0),
        "dark": (0.05, 0.05, 0.05, 1.0),
        "led": (0.95, 0.95, 0.95, 0.78),
        "gravel": (0.20, 0.20, 0.21, 1.0),
        "gravel_dark": (0.10, 0.10, 0.11, 1.0),
        "rock": (0.45, 0.45, 0.46, 1.0),
        "plant_a": (0.18, 0.52, 0.22, 1.0),
        "plant_b": (0.44, 0.80, 0.34, 1.0),
        "plant_c": (0.70, 0.72, 0.74, 1.0),
        "canister": (0.12, 0.12, 0.13, 1.0),
        "hose": (0.22, 0.22, 0.23, 1.0),
        "red": (0.85, 0.30, 0.30, 1.0),
        "orange": (0.90, 0.60, 0.30, 1.0),
        "green": (0.30, 0.70, 0.40, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class AquariumConfig:
    body_form: BodyForm = "rect"
    lid: LidType = "hinged_hood"
    filter: FilterType = "hob"
    plant_count: int = 4
    palette_style: PaletteStyle = "classic_warm"
    glass_h: float = 0.34
    foot_w: float = 0.52
    foot_d: float = 0.32
    radius: float = 0.20
    hood_open_scale: float = 1.0
    flap_open_scale: float = 1.0
    slide_travel_scale: float = 1.0
    name: str = "reference_aquarium"


@dataclass(frozen=True)
class ResolvedAquariumConfig:
    body_form: BodyForm
    lid: LidType
    filter: FilterType
    plant_count: int
    palette_style: PaletteStyle
    glass_h: float
    foot_w: float
    foot_d: float
    radius: float
    hood_open_scale: float
    flap_open_scale: float
    slide_travel_scale: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _lid_rear_edge(g: "TankGeom") -> float:
    """World Y where a closed lid's rear edge stops (forward of the exposed rear
    filter strip). All lid builders and the rear filter routing share this datum
    so lids never cover the rim/tubes that filtration mounts on."""
    return g.inner_rear_y - LID_REAR_GAP


def _compatible_lids(body_form: BodyForm) -> tuple[LidType, ...]:
    # Sliding rails / split canopy leaves are rectangular-footprint mechanisms;
    # round + hex tanks carry a shaped disc/prism hood on the rear hinge.
    if body_form in ("rect", "rounded", "bowfront"):
        return ("hinged_hood", "sliding_cover", "bifold_canopy")
    return ("hinged_hood",)


def _compatible_filters(body_form: BodyForm) -> tuple[FilterType, ...]:
    # A hang-on-back filter needs a flat rear rim to hook over; the round column
    # uses only submerged internal / floor canister (matches the source records).
    if body_form == "cylinder":
        return ("internal", "canister")
    return ("hob", "internal", "canister")


def config_from_seed(seed: int) -> AquariumConfig:
    rng = random.Random(seed)
    body_form: BodyForm = rng.choice(BODY_FORMS)
    lid: LidType = rng.choice(_compatible_lids(body_form))
    filt: FilterType = rng.choice(_compatible_filters(body_form))
    plant_count = rng.choices(PLANT_N_VALUES, weights=PLANT_N_WEIGHTS, k=1)[0]
    palette_style: PaletteStyle = rng.choice(PALETTE_STYLES)

    return AquariumConfig(
        body_form=body_form,
        lid=lid,
        filter=filt,
        plant_count=plant_count,
        palette_style=palette_style,
        glass_h=round(rng.uniform(0.26, 0.40), 4),
        foot_w=round(rng.uniform(0.44, 0.60), 4),
        foot_d=round(rng.uniform(0.28, 0.36), 4),
        radius=round(rng.uniform(0.17, 0.24), 4),
        hood_open_scale=round(rng.uniform(0.85, 1.05), 4),
        flap_open_scale=round(rng.uniform(0.85, 1.05), 4),
        slide_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_aquarium_{seed}",
    )


def _pick(value, choices):
    return value if value in choices else choices[0]


def resolve_config(config: AquariumConfig | None = None) -> ResolvedAquariumConfig:
    cfg = config or AquariumConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    # conditional legality resolved before geometry (spec §7 sampling contract).
    lid = _pick(cfg.lid, _compatible_lids(body_form))
    filt = _pick(cfg.filter, _compatible_filters(body_form))
    plant_count = int(_clamp(float(cfg.plant_count), 2, 8))
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    return ResolvedAquariumConfig(
        body_form=body_form,
        lid=lid,
        filter=filt,
        plant_count=plant_count,
        palette_style=palette_style,
        glass_h=_clamp(cfg.glass_h, 0.26, 0.40),
        foot_w=_clamp(cfg.foot_w, 0.44, 0.60),
        foot_d=_clamp(cfg.foot_d, 0.28, 0.36),
        radius=_clamp(cfg.radius, 0.17, 0.24),
        hood_open_scale=_clamp(cfg.hood_open_scale, 0.85, 1.05),
        flap_open_scale=_clamp(cfg.flap_open_scale, 0.85, 1.05),
        slide_travel_scale=_clamp(cfg.slide_travel_scale, 0.85, 1.10),
        name=cfg.name or "aquarium",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedAquariumConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("lid", r.lid),
        ("filter", r.filter),
        ("plant_count", f"n{r.plant_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tank geometry descriptor (produced by a body_form builder, consumed by lid /
# filter / substrate builders).
# --------------------------------------------------------------------------- #
@dataclass
class TankGeom:
    shape: str          # "rect" | "round" | "hex"
    top_z: float        # top of the glass wall
    rim_top: float      # top of the rim frame
    inner_bottom_z: float  # top of bottom_glass (gravel rests here)
    hinge_y: float      # world Y of the rear hinge axis
    hinge_z: float      # world Z of the rear hinge axis
    front_y: float      # inner front opening edge (most -Y)
    rear_y: float       # inner rear opening edge (most +Y)
    open_half_w: float  # interior half-width in X (plants/lid)
    open_half_d: float  # interior half-depth in Y
    open_r: float       # inscribed interior radius (round/hex); 0 for rect
    rim_half_w: float   # rim outer half-width in X (0 for round)
    rim_half_d: float   # rim outer half-depth in Y (0 for round)
    rim_outer_r: float  # rim outer radius (round); hex circumradius; 0 for rect
    rear_rim_y: float   # world Y of the rear rim outer edge
    inner_rear_y: float # inner rear wall Y (internal filter mount)


# --------------------------------------------------------------------------- #
# world -> local visual helper
# --------------------------------------------------------------------------- #
def _wv(part, shape, wxyz, base, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    """Add ``shape`` at WORLD center ``wxyz`` onto ``part`` whose frame origin
    (the part's joint origin) is ``base`` — so the authored local origin is
    ``wxyz - base``."""
    part.visual(
        shape,
        origin=Origin(
            xyz=(wxyz[0] - base[0], wxyz[1] - base[1], wxyz[2] - base[2]), rpy=rpy
        ),
        material=material,
        name=name, material_class_id=_material_class_id(material.name),
    )


# --------------------------------------------------------------------------- #
# cadquery helpers
# --------------------------------------------------------------------------- #
def _rounded_shell_mesh(w: float, d: float, h: float, wall: float, z0: float, fillet: float):
    # Single profile-with-hole extrude (outer + inner wire in one solid, like the
    # cylinder ring) so the result is a true hollow tube whose interior cavity is
    # respected by collision — a boolean cut() here meshes as a filled solid.
    shell = (
        cq.Workplane("XY")
        .rect(w, d)
        .rect(w - 2 * wall, d - 2 * wall)
        .extrude(h)
        .edges("|Z")
        .fillet(fillet)
    )
    return shell.translate((0.0, 0.0, z0))


def _bow_front_panel_mesh(w: float, d: float, h: float, t: float, bow: float, z0: float):
    half_w = w / 2.0
    front_y = -d / 2.0
    back_y = front_y + t + 0.004
    outer = (
        cq.Workplane("XY")
        .moveTo(-half_w, back_y)
        .lineTo(-half_w, front_y)
        .threePointArc((0.0, front_y - bow), (half_w, front_y))
        .lineTo(half_w, back_y)
        .close()
        .extrude(h)
    )
    inner_front = front_y + t
    inner = (
        cq.Workplane("XY")
        .moveTo(-half_w, back_y)
        .lineTo(-half_w, inner_front)
        .threePointArc((0.0, inner_front - bow), (half_w, inner_front))
        .lineTo(half_w, back_y)
        .close()
        .extrude(h)
    )
    return outer.cut(inner).translate((0.0, 0.0, z0))


def _ring_mesh(r_outer: float, r_inner: float, h: float, z0: float):
    return (
        cq.Workplane("XY").circle(r_outer).circle(r_inner).extrude(h).translate((0.0, 0.0, z0))
    )


def _disc_mesh(r: float, h: float, z0: float):
    return cq.Workplane("XY").circle(r).extrude(h).translate((0.0, 0.0, z0))


def _hex_plate_mesh(circumradius: float, h: float, z0: float):
    return (
        cq.Workplane("XY").polygon(6, 2 * circumradius).extrude(h).translate((0.0, 0.0, z0))
    )


# --------------------------------------------------------------------------- #
# Body_form builders  (emit tank_frame, return TankGeom)
# --------------------------------------------------------------------------- #
def _rect_family_walls(tank, r, mats, *, rounded: bool, bow: float) -> TankGeom:
    W, D, H = r.foot_w, r.foot_d, r.glass_h
    hw, hd = W / 2.0, D / 2.0
    top_z = BASE_H + H
    rim_top = top_z + RIM_H
    glass = mats["glass"]
    frame = mats["frame"]
    base = (0.0, 0.0, 0.0)

    if rounded:
        # Flat glass panes (like the plain rect) so the interior cavity is real
        # for collision; the "rounded" identity comes from the cylindrical corner
        # columns emitted below. (A single hollow-shell mesh meshes as a filled
        # solid and reports the whole substrate/interior as an overlap.)
        _wv(tank, Box((W, GLASS_T, H)), (0.0, -hd - GLASS_T / 2.0, BASE_H + H / 2.0),
            base, glass, "front_glass")
        _wv(tank, Box((W, GLASS_T, H)), (0.0, hd + GLASS_T / 2.0, BASE_H + H / 2.0),
            base, glass, "rear_glass")
        _wv(tank, Box((GLASS_T, D, H)), (-hw - GLASS_T / 2.0, 0.0, BASE_H + H / 2.0),
            base, glass, "side_glass_0")
        _wv(tank, Box((GLASS_T, D, H)), (hw + GLASS_T / 2.0, 0.0, BASE_H + H / 2.0),
            base, glass, "side_glass_1")
        # a named glass_wall element (tests key on it) — the front corner column band
        _wv(tank, Box((W, D, GLASS_T)), (0.0, 0.0, BASE_H + GLASS_T / 2.0),
            base, glass, "bottom_glass")
    elif bow > 0.0:
        tank.visual(
            mesh_from_cadquery(
                _bow_front_panel_mesh(W, D, H, GLASS_T, bow, BASE_H), "bow_front_glass"
            ),
            origin=Origin(),
            material=glass,
            name="front_glass", material_class_id="glass.clear_transparent",
        )
        _wv(tank, Box((W, GLASS_T, H)), (0.0, hd + GLASS_T / 2.0, BASE_H + H / 2.0),
            base, glass, "rear_glass")
        _wv(tank, Box((GLASS_T, D, H)), (-hw - GLASS_T / 2.0, 0.0, BASE_H + H / 2.0),
            base, glass, "side_glass_0")
        _wv(tank, Box((GLASS_T, D, H)), (hw + GLASS_T / 2.0, 0.0, BASE_H + H / 2.0),
            base, glass, "side_glass_1")
        _wv(tank, Box((W, D, GLASS_T)), (0.0, 0.0, BASE_H + GLASS_T / 2.0),
            base, glass, "bottom_glass")
    else:
        _wv(tank, Box((W, GLASS_T, H)), (0.0, -hd - GLASS_T / 2.0, BASE_H + H / 2.0),
            base, glass, "front_glass")
        _wv(tank, Box((W, GLASS_T, H)), (0.0, hd + GLASS_T / 2.0, BASE_H + H / 2.0),
            base, glass, "rear_glass")
        _wv(tank, Box((GLASS_T, D, H)), (-hw - GLASS_T / 2.0, 0.0, BASE_H + H / 2.0),
            base, glass, "side_glass_0")
        _wv(tank, Box((GLASS_T, D, H)), (hw + GLASS_T / 2.0, 0.0, BASE_H + H / 2.0),
            base, glass, "side_glass_1")
        _wv(tank, Box((W, D, GLASS_T)), (0.0, 0.0, BASE_H + GLASS_T / 2.0),
            base, glass, "bottom_glass")

    rail_x = W + 2 * RAIL_W
    rail_y = D + 2 * RAIL_W
    # base rails
    _wv(tank, Box((rail_x, RAIL_W, BASE_H)), (0.0, -hd - RAIL_W / 2.0, BASE_H / 2.0),
        base, frame, "base_front_rail")
    _wv(tank, Box((rail_x, RAIL_W, BASE_H)), (0.0, hd + RAIL_W / 2.0, BASE_H / 2.0),
        base, frame, "base_rear_rail")
    _wv(tank, Box((RAIL_W, rail_y, BASE_H)), (-hw - RAIL_W / 2.0, 0.0, BASE_H / 2.0),
        base, frame, "base_side_0")
    _wv(tank, Box((RAIL_W, rail_y, BASE_H)), (hw + RAIL_W / 2.0, 0.0, BASE_H / 2.0),
        base, frame, "base_side_1")
    # top rim rails (front rail named top_front_rail — hood-coverage test anchor)
    _wv(tank, Box((rail_x, RAIL_W, RIM_H)), (0.0, -hd - RAIL_W / 2.0, top_z + RIM_H / 2.0),
        base, frame, "top_front_rail")
    _wv(tank, Box((rail_x, RAIL_W, RIM_H)), (0.0, hd + RAIL_W / 2.0, top_z + RIM_H / 2.0),
        base, frame, "top_rear_rail")
    _wv(tank, Box((RAIL_W, rail_y, RIM_H)), (-hw - RAIL_W / 2.0, 0.0, top_z + RIM_H / 2.0),
        base, frame, "top_side_0")
    _wv(tank, Box((RAIL_W, rail_y, RIM_H)), (hw + RAIL_W / 2.0, 0.0, top_z + RIM_H / 2.0),
        base, frame, "top_side_1")
    # corner posts — square for rect/bowfront, rounded columns for the rounded form
    idx = 0
    for sx in (-hw - POST / 2.0, hw + POST / 2.0):
        for sy in (-hd - POST / 2.0, hd + POST / 2.0):
            if rounded:
                _wv(tank, Cylinder(radius=POST * 0.72, length=H + RIM_H),
                    (sx, sy, BASE_H + (H + RIM_H) / 2.0), base, frame, f"corner_post_{idx}")
            else:
                _wv(tank, Box((POST, POST, H + RIM_H)), (sx, sy, BASE_H + (H + RIM_H) / 2.0),
                    base, frame, f"corner_post_{idx}")
            idx += 1

    rim_half_w = hw + RAIL_W
    rim_half_d = hd + RAIL_W
    return TankGeom(
        shape="rect",
        top_z=top_z,
        rim_top=rim_top,
        inner_bottom_z=BASE_H + GLASS_T,
        hinge_y=rim_half_d - 0.002,
        hinge_z=rim_top + 0.034,  # raised so the hood hinge barrel clears rim-mounted filter hardware
        front_y=-hd,
        rear_y=hd,
        open_half_w=hw - GLASS_T - 0.012,
        open_half_d=hd - GLASS_T - 0.012,
        open_r=0.0,
        rim_half_w=rim_half_w,
        rim_half_d=rim_half_d,
        rim_outer_r=0.0,
        rear_rim_y=rim_half_d,
        inner_rear_y=hd - GLASS_T,
    )


def _build_tank_rect(tank, r, mats) -> TankGeom:
    return _rect_family_walls(tank, r, mats, rounded=False, bow=0.0)


def _build_tank_rounded(tank, r, mats) -> TankGeom:
    return _rect_family_walls(tank, r, mats, rounded=True, bow=0.0)


def _build_tank_bowfront(tank, r, mats) -> TankGeom:
    bow = _clamp(0.10 * r.foot_d, 0.024, 0.045)
    return _rect_family_walls(tank, r, mats, rounded=False, bow=bow)


def _build_tank_cylinder(tank, r, mats) -> TankGeom:
    R = r.radius
    H = r.glass_h
    top_z = BASE_H + H
    rim_top = top_z + RIM_H
    glass = mats["glass"]
    frame = mats["frame"]
    base = (0.0, 0.0, 0.0)

    tank.visual(
        mesh_from_cadquery(_ring_mesh(R, R - GLASS_T, H, BASE_H), "cyl_glass_wall"),
        origin=Origin(), material=glass, name="glass_wall", material_class_id="glass.clear_transparent",
    )
    tank.visual(
        mesh_from_cadquery(_disc_mesh(R - GLASS_T, GLASS_T, BASE_H), "cyl_bottom_disc"),
        origin=Origin(), material=glass, name="bottom_glass", material_class_id="glass.clear_transparent",
    )
    tank.visual(
        mesh_from_cadquery(_ring_mesh(R + RAIL_W, R - RAIL_W, BASE_H, 0.0), "cyl_base_ring"),
        origin=Origin(), material=frame, name="base_ring", material_class_id="plastic.opaque_glossy_molded",
    )
    tank.visual(
        mesh_from_cadquery(_ring_mesh(R + RAIL_W, R - RAIL_W, RIM_H, top_z), "cyl_top_ring"),
        origin=Origin(), material=frame, name="top_front_rail", material_class_id="plastic.opaque_glossy_molded",
    )
    for i in range(4):
        ang = math.pi / 4 + i * math.pi / 2
        rx = (R + RAIL_W * 0.5) * math.cos(ang)
        ry = (R + RAIL_W * 0.5) * math.sin(ang)
        _wv(tank, Cylinder(radius=0.009, length=H + RIM_H), (rx, ry, BASE_H + (H + RIM_H) / 2.0),
            base, frame, f"rib_{i}")

    return TankGeom(
        shape="round",
        top_z=top_z,
        rim_top=rim_top,
        inner_bottom_z=BASE_H + GLASS_T,
        hinge_y=(R + RAIL_W) - 0.002,
        hinge_z=rim_top + 0.034,  # raised so the hood hinge barrel clears rim-mounted filter hardware
        front_y=-(R - GLASS_T),
        rear_y=(R - GLASS_T),
        open_half_w=R - GLASS_T - 0.012,
        open_half_d=R - GLASS_T - 0.012,
        open_r=R - GLASS_T - 0.012,
        rim_half_w=0.0,
        rim_half_d=0.0,
        rim_outer_r=R + RAIL_W,
        rear_rim_y=R + RAIL_W,
        inner_rear_y=R - GLASS_T,
    )


def _build_tank_hexagon(tank, r, mats) -> TankGeom:
    R = r.radius + 0.04  # circumradius
    inradius = R * math.cos(math.pi / 6.0)
    side = R
    H = r.glass_h
    top_z = BASE_H + H
    rim_top = top_z + RIM_H
    glass = mats["glass"]
    frame = mats["frame"]
    base = (0.0, 0.0, 0.0)

    def face_angle(i):  # face 0 -> -Y front, face 3 -> +Y rear
        return -math.pi / 2.0 + i * math.pi / 3.0

    def vertex_angle(j):
        return -math.pi / 3.0 + j * math.pi / 3.0

    for i in range(6):
        ang = face_angle(i)
        gr = inradius + GLASS_T / 2.0
        _wv(tank, Box((side, GLASS_T, H)),
            (gr * math.cos(ang), gr * math.sin(ang), BASE_H + H / 2.0),
            base, glass, f"wall_glass_{i}", rpy=(0.0, 0.0, ang - math.pi / 2.0))
    tank.visual(
        mesh_from_cadquery(_hex_plate_mesh(R, GLASS_T, BASE_H), "hex_bottom_glass"),
        origin=Origin(), material=glass, name="bottom_glass", material_class_id="glass.clear_transparent",
    )
    for i in range(6):
        ang = face_angle(i)
        rr = inradius + RAIL_W / 2.0
        nm = "top_front_rail" if i == 0 else f"top_rail_{i}"
        _wv(tank, Box((side + RAIL_W, RAIL_W, RIM_H)),
            (rr * math.cos(ang), rr * math.sin(ang), top_z + RIM_H / 2.0),
            base, frame, nm, rpy=(0.0, 0.0, ang - math.pi / 2.0))
        nb = "base_front_rail" if i == 0 else f"base_rail_{i}"
        _wv(tank, Box((side + RAIL_W, RAIL_W, BASE_H)),
            (rr * math.cos(ang), rr * math.sin(ang), BASE_H / 2.0),
            base, frame, nb, rpy=(0.0, 0.0, ang - math.pi / 2.0))
    for j in range(6):
        ang = vertex_angle(j)
        _wv(tank, Box((POST, POST, H + RIM_H)),
            (R * math.cos(ang), R * math.sin(ang), BASE_H + (H + RIM_H) / 2.0),
            base, frame, f"corner_post_{j}")

    return TankGeom(
        shape="hex",
        top_z=top_z,
        rim_top=rim_top,
        inner_bottom_z=BASE_H + GLASS_T,
        hinge_y=(inradius + RAIL_W) - 0.002,
        hinge_z=rim_top + 0.034,  # raised so the hood hinge barrel clears rim-mounted filter hardware
        front_y=-inradius,
        rear_y=inradius,
        open_half_w=inradius - GLASS_T - 0.02,
        open_half_d=inradius - GLASS_T - 0.02,
        open_r=inradius - GLASS_T - 0.02,
        rim_half_w=R,
        rim_half_d=inradius + RAIL_W,
        rim_outer_r=R,
        rear_rim_y=inradius + RAIL_W,
        inner_rear_y=inradius - GLASS_T,
    )


_BODY_BUILDERS = {
    "rect": _build_tank_rect,
    "rounded": _build_tank_rounded,
    "bowfront": _build_tank_bowfront,
    "cylinder": _build_tank_cylinder,
    "hexagon": _build_tank_hexagon,
}


# --------------------------------------------------------------------------- #
# Hinge hardware (shared): mounts on the tank rim + connectivity barrel on lid
# --------------------------------------------------------------------------- #
def _emit_hinge_mounts(tank, g: TankGeom, mats, half_span: float, tag: str) -> float:
    """Two ledges straddling the rear hinge line, bridging the rim up to just
    under the barrel; the lid barrel seats ~2 mm into them (support + the joint
    axis lands on this hinge hardware). Returns the mount X half-offset."""
    mx = min(0.35 * half_span, half_span - 0.03)
    mount_bot = g.rim_top - 0.003
    # ledge tops seat ~1.5 mm into the barrel underside: captured-pin contact for
    # support connectivity, well under the 5 mm overlap tolerance.
    mount_top = g.hinge_z - BARREL_R + 0.0015
    cz = (mount_bot + mount_top) / 2.0
    hh = max(mount_top - mount_bot, 0.006)
    base = (0.0, 0.0, 0.0)
    for i, sx in enumerate((-mx, mx)):
        _wv(tank, Box((0.05, 0.024, hh)), (sx, g.hinge_y, cz), base, mats["frame"],
            f"{tag}_mount_{i}")
    return mx


def _hood_shell_local(g: TankGeom, r, aperture):
    """Build the molded hood shell (cadquery) in the hood-LOCAL frame (origin at
    the rear hinge). Shape follows the tank top opening. ``aperture`` = (cx, cy,
    aw, ad) world feed hole (or None)."""
    hy, hz = g.hinge_y, g.hinge_z
    cz_local = (g.rim_top + 0.006 + HOOD_T / 2.0) - hz  # shell center z (local)
    cy_local = -hy  # tank center Y in local frame
    rear_edge = _lid_rear_edge(g)  # world Y where the shell stops (filter strip aft)
    if g.shape == "round":
        rr = g.rim_outer_r + 0.03
        shell = cq.Workplane("XY").circle(rr).extrude(HOOD_T)
        shell = shell.translate((0.0, cy_local, cz_local - HOOD_T / 2.0))
    elif g.shape == "hex":
        rr = g.rim_outer_r + 0.03
        shell = cq.Workplane("XY").polygon(6, 2 * rr).extrude(HOOD_T)
        shell = shell.edges("|Z").chamfer(0.006)
        shell = shell.translate((0.0, cy_local, cz_local - HOOD_T / 2.0))
    else:
        # rectangular hood: overhang front + sides.
        front_edge = -g.rim_half_d - 0.035
        hw = g.rim_half_w + 0.035
        depth = rear_edge - front_edge
        center_y = (front_edge + rear_edge) / 2.0
        shell = cq.Workplane("XY").box(2 * hw, depth, HOOD_T)
        shell = shell.edges("|Z").chamfer(0.010)
        shell = shell.translate((0.0, center_y - hy, cz_local))
    if g.shape in ("round", "hex"):
        # slice the rear off the disc/prism at the shared lid rear edge so the
        # exposed rear strip (filter clips / tubing / over-rim plumbing) is clear.
        big = 4.0 * (g.rim_outer_r + 0.10)
        cutter = cq.Workplane("XY").box(4.0 * (g.rim_outer_r + 0.10), big, HOOD_T * 6.0)
        cutter = cutter.translate((0.0, (rear_edge - hy) + big / 2.0, cz_local))
        shell = shell.cut(cutter)
    # rear-centre slot: a channel down the middle of the hood's back half so the
    # centred filter plumbing (intake / down-tube / arch) passes through it at ANY
    # hood-open angle without the swinging shell striking it. Side wings stay joined
    # to the shell at the front; the hinge arms tie those wings to the barrel.
    slot_hw = 0.045
    slot_front_world = -0.02
    slot_len = 2.0
    slot = cq.Workplane("XY").box(2 * slot_hw, slot_len, HOOD_T * 6.0)
    slot = slot.translate((0.0, (slot_front_world - hy) + slot_len / 2.0, cz_local))
    shell = shell.cut(slot)
    if aperture is not None:
        acx, acy, aw, ad = aperture
        cutter = cq.Workplane("XY").box(aw, ad, HOOD_T * 4.0)
        cutter = cutter.translate((acx, acy - hy, cz_local))
        shell = shell.cut(cutter)
    return shell


# --------------------------------------------------------------------------- #
# Lid builders
# --------------------------------------------------------------------------- #
def _build_lid_hinged_hood(model, tank, g: TankGeom, r, mats) -> None:
    frame = mats["frame"]
    dark = mats["dark"]
    led = mats["led"]
    lid_half_w = (g.rim_outer_r + 0.03) if g.shape != "rect" else (g.rim_half_w + 0.035)
    _emit_hinge_mounts(tank, g, mats, lid_half_w, "hood")

    hood = model.part("hood")
    hbase = (0.0, g.hinge_y, g.hinge_z)
    hood_top_z = g.rim_top + 0.006 + HOOD_T

    # feed aperture toward the front of the hood
    ay = g.front_y * 0.55
    aw = min(0.14, 2 * g.open_half_w * 0.55)
    ad = 0.09
    aperture = (0.0, ay, aw, ad)

    hood.visual(
        # _hood_shell_local already authors the mesh in the hood-local frame.
        mesh_from_cadquery(_hood_shell_local(g, r, aperture), "hood_shell"),
        origin=Origin(),
        material=frame,
        name="hood_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    # hinge barrel (connectivity + axis hardware), full width, on the axis
    hood.visual(
        Cylinder(radius=BARREL_R, length=2 * (0.35 * lid_half_w) + 0.08),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=frame,
        name="hood_hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )
    # two hinge arms bridge the (rear-cleared) shell to the barrel so the hood is
    # one connected body; placed inboard of the rim hinge mounts and clear of the
    # centre-line filter tubing.
    arm_x = 0.060  # outboard of the rear-centre shell slot, inboard of the barrel ends
    arm_y0 = _lid_rear_edge(g)
    arm_y1 = g.hinge_y
    for i, sx in enumerate((-arm_x, arm_x)):
        _wv(hood, Box((0.018, (arm_y1 - arm_y0) + 0.010, 0.010)),
            (sx, (arm_y0 + arm_y1) / 2.0, g.hinge_z), hbase, frame, f"hinge_arm_{i}")
    # led strip + control panel + status buttons (host-derived decoration)
    _wv(hood, Box((min(0.30, 2 * g.open_half_w * 0.8), 0.024, 0.006)),
        (0.0, ay + ad, g.rim_top + 0.006 - 0.001), hbase, led, "light_diffuser")
    _wv(hood, Box((0.17, 0.06, 0.004)), (0.0, g.rear_y * 0.35, hood_top_z + 0.002),
        hbase, dark, "control_panel")
    for i, (dx, key) in enumerate(((-0.045, "red"), (-0.015, "orange"), (0.02, "green"))):
        _wv(hood, Cylinder(radius=0.006, length=0.004),
            (dx, g.rear_y * 0.35, hood_top_z + 0.006), hbase, mats[key], f"status_button_{i}")
    # feed-flap socket (barrel seat): sits on the shell just behind the aperture
    # rear lip, its top touching the barrel underside (connectivity) while staying
    # clear of the flap panel through the full swing.
    panel_w = aw - 0.008
    panel_d = ad - 0.016
    # hinge sits just inside the aperture rear lip, right at the panel's rear edge.
    fy = ay + panel_d / 2.0 + 0.003
    feed_hinge_z = hood_top_z + 0.006
    _wv(hood, Box((0.06, 0.016, 0.012)), (0.0, fy + 0.006, hood_top_z - 0.0045),
        hbase, frame, "feed_socket")

    model.articulation(
        "tank_to_hood",
        ArticulationType.REVOLUTE,
        parent=tank,
        child=hood,
        origin=Origin(xyz=(0.0, g.hinge_y, g.hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=6.0, velocity=2.2, lower=0.0, upper=_clamp(1.15 * r.hood_open_scale, 0.0, 1.25)
        ),
    )

    # nested feed flap. Panel is slightly SMALLER than the aperture so it swings
    # up through the hole without catching the surrounding shell lip.
    flap = model.part("feed_flap")
    fbase = (0.0, fy, feed_hinge_z)
    _wv(flap, Box((panel_w, panel_d, 0.006)), (0.0, ay, feed_hinge_z), fbase, dark,
        "flap_panel")
    # finger lip overlaps the panel front edge (kept connected to the panel)
    _wv(flap, Box((0.05, 0.010, 0.006)),
        (0.0, ay - panel_d / 2.0 + 0.004, feed_hinge_z + 0.004),
        fbase, frame, "finger_lip")
    _wv(flap, Cylinder(radius=0.0045, length=panel_w + 0.02),
        (0.0, fy, feed_hinge_z), fbase, frame, "flap_hinge_barrel",
        rpy=(0.0, math.pi / 2.0, 0.0))
    model.articulation(
        "hood_to_feed_flap",
        ArticulationType.REVOLUTE,
        parent=hood,
        child=flap,
        # joint origin is expressed in the parent (hood) LOCAL frame.
        origin=Origin(xyz=(0.0, fy - g.hinge_y, feed_hinge_z - g.hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=1.0, velocity=3.0, lower=0.0, upper=_clamp(1.3 * r.flap_open_scale, 0.0, 1.45)
        ),
    )


def _build_lid_sliding_cover(model, tank, g: TankGeom, r, mats) -> None:
    frame = mats["frame"]
    led = mats["led"]
    dark = mats["dark"]
    slide = mats["glass"]
    panel_t = 0.006
    # panel seats ~2 mm onto the top rim rails it rides on (support contact + <5 mm
    # overlap); it slides fore-aft in that grooved seat.
    panel_z = g.rim_top - 0.002 + panel_t / 2.0
    # the panel overhangs the front rim (covers top_front_rail) and its CLOSED rear
    # edge stops short enough that even fully slid open (+Y) it never reaches the
    # rear filter strip at `_lid_rear_edge`.
    travel = _clamp(0.12 * r.slide_travel_scale, 0.08, 0.15)
    front_edge = -g.rim_half_d - 0.008
    closed_rear = _lid_rear_edge(g) - travel
    panel_w = 2 * g.rim_half_w - 0.008
    panel_d = max(closed_rear - front_edge, 0.10)
    center_y = front_edge + panel_d / 2.0

    # capture guide lips on the top rim so the panel edges track fore-aft
    guide_h = panel_t + 0.006
    base = (0.0, 0.0, 0.0)
    for i, sx in enumerate((-1.0, 1.0)):
        _wv(tank, Box((0.006, panel_d + travel, guide_h)),
            (sx * (panel_w / 2.0 + 0.004), center_y + travel / 2.0, g.rim_top + guide_h / 2.0),
            base, frame, f"slide_guide_{i}")

    hood = model.part("hood")
    sbase = (0.0, center_y, panel_z)
    # panel bottom seats ~2mm into the top rim rails (support + <5mm overlap)
    _wv(hood, Box((panel_w, panel_d, panel_t)), (0.0, center_y, panel_z - 0.002), sbase, slide,
        "hood_shell")
    _wv(hood, Box((min(0.30, panel_w * 0.7), 0.024, 0.006)),
        (0.0, center_y, panel_z - panel_t / 2.0 - 0.001), sbase, led, "light_diffuser")
    _wv(hood, Box((0.17, 0.06, 0.004)), (0.0, front_edge + 0.06, panel_z + panel_t / 2.0),
        sbase, dark, "control_panel")
    _wv(hood, Box((0.08, 0.012, 0.012)),
        (0.0, front_edge - 0.004, panel_z + panel_t / 2.0 + 0.002), sbase, frame, "front_grip")

    model.articulation(
        "tank_to_hood",
        ArticulationType.PRISMATIC,
        parent=tank,
        child=hood,
        origin=Origin(xyz=(0.0, center_y, panel_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.4, lower=0.0, upper=travel),
    )


def _build_lid_bifold_canopy(model, tank, g: TankGeom, r, mats) -> None:
    frame = mats["frame"]
    led = mats["led"]
    canopy = mats["glass"]
    leaf_t = 0.005
    leaf_w = 2 * g.rim_half_w - 0.012
    half_span = g.rim_half_w
    upper = _clamp(1.15 * r.hood_open_scale, 0.0, 1.25)

    # Each leaf hinges on a full-width cross-brace that ties into the side rails at
    # both ends. The front brace is on the centre line; the rear brace sits at the
    # shared lid rear edge so the closed rear leaf clears the filter strip. The leaf
    # panels are held forward of the hinge (below) so they never butt the braces.
    front_hinge_y = 0.0
    front_hinge_z = g.rim_top + 0.016
    rear_hinge_y = _lid_rear_edge(g)
    rear_hinge_z = front_hinge_z
    base = (0.0, 0.0, 0.0)

    mx = 0.35 * half_span
    brace_bot = g.top_z
    brace_top = front_hinge_z - BARREL_R  # barrel rests tangent on the brace top
    for by, bd, tag in (
        (front_hinge_y, 0.030, "center_cross_brace"),
        (rear_hinge_y, 0.016, "rear_cross_brace"),
    ):
        _wv(tank, Box((2 * half_span, bd, max(brace_top - brace_bot, 0.006))),
            (0.0, by, (brace_bot + brace_top) / 2.0), base, frame, tag)

    # panel rear edge is held this far forward of the hinge so it clears the mounts;
    # a slim centre-line connector bridges the barrel back to the panel.
    off = 0.020
    # near_gap keeps the rear leaf's forward edge clear of the front leaf's centre
    # hinge barrel (which sits on the axis at y=0 and does not move when opened).
    for leaf_name, hinge_y, hinge_z, leaf_depth, near_gap in (
        ("lid_leaf_front", front_hinge_y, front_hinge_z, abs(g.front_y) - 0.004, 0.0),
        ("lid_leaf_rear", rear_hinge_y, rear_hinge_z, (rear_hinge_y - front_hinge_y) - 0.004, 0.016),
    ):
        leaf = model.part(leaf_name)
        lbase = (0.0, hinge_y, hinge_z)
        body_depth = max(leaf_depth - off - near_gap, 0.03)
        panel_cy = hinge_y - off - body_depth / 2.0  # extends forward (-Y)
        _wv(leaf, Box((leaf_w, body_depth, leaf_t)), (0.0, panel_cy, hinge_z - 0.004),
            lbase, canopy, f"{leaf_name}_panel")
        _wv(leaf, Box((leaf_w, 0.012, leaf_t + 0.003)),
            (0.0, panel_cy - body_depth / 2.0 + 0.006, hinge_z - 0.004),
            lbase, frame, f"{leaf_name}_trim")
        # slim centre connector barrel->panel (clear of the side mounts)
        _wv(leaf, Box((0.04, off + 0.008, leaf_t)), (0.0, hinge_y - off / 2.0, hinge_z - 0.004),
            lbase, frame, f"{leaf_name}_link")
        _wv(leaf, Cylinder(radius=BARREL_R, length=2 * mx + 0.08),
            (0.0, hinge_y, hinge_z), lbase, frame, f"{leaf_name}_barrel",
            rpy=(0.0, math.pi / 2.0, 0.0))
        model.articulation(
            f"tank_to_{leaf_name}",
            ArticulationType.REVOLUTE,
            parent=tank,
            child=leaf,
            origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=2.5, lower=0.0, upper=upper),
        )

    lid_front = model.get_part("lid_leaf_front")
    lf_base = (0.0, front_hinge_y, front_hinge_z)
    _wv(lid_front, Box((min(0.30, leaf_w * 0.7), 0.024, 0.006)),
        (0.0, -off - (abs(g.front_y) - 0.004 - off) * 0.5,
         front_hinge_z - 0.004 - leaf_t / 2.0 - 0.003),
        lf_base, led, "light_diffuser")


_LID_BUILDERS = {
    "hinged_hood": _build_lid_hinged_hood,
    "sliding_cover": _build_lid_sliding_cover,
    "bifold_canopy": _build_lid_bifold_canopy,
}


# --------------------------------------------------------------------------- #
# Filter builders  (emit `filter` part; return the FIXED joint origin)
# --------------------------------------------------------------------------- #
def _rear_interior_y(g: TankGeom) -> float:
    """A rear-of-tank point that stays safely inside the glass footprint."""
    return (g.open_r if g.open_r > 0.0 else g.open_half_d) * 0.55


def _gravel_top(g: TankGeom) -> float:
    return g.inner_bottom_z + 0.040


def _build_filter_hob(model, tank, g: TankGeom, r, mats):
    frame = mats["frame"]
    filt = model.part("filter")
    # centred on the rear rail: sits between the symmetric hinge mounts (±mx) and
    # under the raised hood barrel, clear of both.
    rear = g.rear_rim_y
    in_y = g.inner_rear_y - 0.02       # intake column just inside the rear wall
    contact = (0.0, rear - RAIL_W / 2.0, g.rim_top)
    base = contact
    # external hang-on-back housing, its top just under the rim
    htop = g.rim_top + 0.006
    hh = 0.15
    _wv(filt, Box((0.070, 0.075, hh)), (0.0, rear + 0.05, htop - hh / 2.0), base, frame,
        "filter_housing")
    # hanger bar over the rear rail, from the housing forward to above the intake
    _wv(filt, Box((0.05, (rear + 0.05) - in_y, 0.016)),
        (0.0, ((rear + 0.05) + in_y) / 2.0, g.rim_top + 0.006), base, frame, "rim_hanger")
    # intake column down into the tank to the strainer (touches the hanger on top)
    strainer_cz = _gravel_top(g) + 0.035
    intake_top = g.rim_top + 0.006
    intake_bot = strainer_cz + 0.01
    _wv(filt, Cylinder(radius=0.007, length=max(intake_top - intake_bot, 0.05)),
        (0.0, in_y, (intake_top + intake_bot) / 2.0), base, frame, "intake_tube")
    _wv(filt, Cylinder(radius=0.0085, length=0.05), (0.0, in_y, strainer_cz), base, frame,
        "strainer_tip")
    # outlet spout curling back into the tank near the surface (joins the intake)
    _wv(filt, Cylinder(radius=0.006, length=0.05), (0.02, in_y - 0.005, g.top_z - 0.02),
        base, frame, "outlet_elbow", rpy=(0.0, math.pi / 2.0, 0.0))
    return contact


def _build_filter_internal(model, tank, g: TankGeom, r, mats):
    frame = mats["frame"]
    filt = model.part("filter")
    in_y = g.inner_rear_y - 0.030     # housing hugs the inner rear wall
    rear = g.rear_rim_y
    # submerged housing -> neck up to the rim -> clip hooking over the (lid-exposed)
    # rear rail: one connected chain that contacts the rail top for support.
    contact = (0.0, rear - RAIL_W / 2.0, g.rim_top)
    base = contact
    htop = g.top_z - 0.02
    hh = 0.09
    _wv(filt, Box((0.060, 0.045, hh)), (0.0, in_y, htop - hh / 2.0), base, frame,
        "filter_housing")
    # neck: housing top up to rim level. Kept slim so it rises between the rim's
    # inner edge and the hood's rear edge (a ~19 mm band) without clipping either.
    neck_bot = htop - 0.005
    neck_top = g.rim_top + 0.006
    _wv(filt, Box((0.014, 0.012, neck_top - neck_bot)),
        (0.0, in_y, (neck_bot + neck_top) / 2.0), base, frame, "clip_neck")
    # hook bar: from the neck back over the rear rail top (~2 mm seat -> contact)
    clip_y1 = rear + 0.004
    _wv(filt, Box((0.05, clip_y1 - in_y, 0.016)),
        (0.0, (in_y + clip_y1) / 2.0, g.rim_top + 0.006), base, frame, "filter_clip")
    strainer_cz = _gravel_top(g) + 0.035
    intake_top = htop - hh + 0.01
    intake_bot = strainer_cz + 0.01
    _wv(filt, Cylinder(radius=0.007, length=max(intake_top - intake_bot, 0.04)),
        (0.0, in_y, (intake_top + intake_bot) / 2.0), base, frame, "intake_tube")
    _wv(filt, Cylinder(radius=0.0085, length=0.05), (0.0, in_y, strainer_cz), base, frame,
        "strainer_tip")
    return contact


def _build_filter_canister(model, tank, g: TankGeom, r, mats):
    canister = mats["canister"]
    frame = mats["frame"]
    hose = mats["hose"]
    filt = model.part("filter")
    can_h = 0.24
    cy = g.rear_rim_y + 0.11          # canister body behind the tank on the floor
    rear = g.rear_rim_y
    # interior tube entry. Round/hex have a continuous top-rim ring, so the tube
    # must drop inside its inner edge (forward); rect-family have a bifold rear
    # barrel at the lid rear edge, so the tube drops just behind it (aft) instead.
    if g.shape in ("round", "hex"):
        entry_y = g.inner_rear_y - 0.030
    else:
        entry_y = g.inner_rear_y - 0.015
    contact = (0.0, rear - RAIL_W / 2.0, g.rim_top)
    base = contact

    _wv(filt, Cylinder(radius=0.05, length=can_h), (0.0, cy, can_h / 2.0), base, canister,
        "canister_body")
    _wv(filt, Cylinder(radius=0.048, length=0.008), (0.0, cy, can_h + 0.004), base, frame,
        "canister_lid")
    arch_z = g.rim_top + 0.058  # clears the raised hood hinge barrel (top ~rim+0.042)
    # riser link: canister lid up to the arch (intra-part chain)
    _wv(filt, Cylinder(radius=0.008, length=(arch_z - (can_h + 0.008)) + 0.02),
        (0.0, cy, (arch_z + can_h + 0.008) / 2.0), base, hose, "riser")
    # arch over the rear rim into the rear strip (all aft of the lid rear edge)
    arch_len = (cy - entry_y) + 0.02
    _wv(filt, Cylinder(radius=0.008, length=arch_len),
        (0.0, (cy + entry_y) / 2.0, arch_z), base, hose, "arch_tube", rpy=(math.pi / 2.0, 0.0, 0.0))
    # saddle seating on the rear rail top (~3mm) + a low horizontal arm back to the
    # canister riser (passes UNDER the raised hood barrel, behind the rim) so the
    # whole canister assembly is one connected chain touching the tank.
    _wv(filt, Box((0.024, 0.030, 0.020)), (0.0, rear - RAIL_W / 2.0, g.rim_top + 0.007),
        base, frame, "rim_saddle")
    _wv(filt, Box((0.020, cy - (rear - RAIL_W / 2.0), 0.016)),
        (0.0, (cy + rear - RAIL_W / 2.0) / 2.0, g.rim_top + 0.007), base, frame, "saddle_arm")
    # down-tube into the tank (in the rear strip, behind every lid) + strainer
    strainer_cz = _gravel_top(g) + 0.035
    dt_top = arch_z
    dt_bot = strainer_cz + 0.01
    _wv(filt, Cylinder(radius=0.007, length=dt_top - dt_bot),
        (0.0, entry_y, (dt_top + dt_bot) / 2.0), base, frame, "down_tube")
    _wv(filt, Cylinder(radius=0.011, length=0.05), (0.0, entry_y, strainer_cz), base, frame,
        "strainer")
    # spray bar low inside, along X (well below every lid). Length is bounded by
    # the tank's interior half-width AT the rear entry so it never pierces the
    # side/curved walls of round or hex tanks.
    if g.open_r > 0.0:
        avail = math.sqrt(max(g.open_r ** 2 - entry_y ** 2, 0.0))
    else:
        avail = g.open_half_w
    spray_len = 2.0 * max(avail - 0.012, 0.015)
    _wv(filt, Cylinder(radius=0.008, length=min(0.12, spray_len)),
        (0.0, entry_y, g.top_z - 0.02), base, frame, "spray_bar", rpy=(0.0, math.pi / 2.0, 0.0))
    return contact


_FILTER_BUILDERS = {
    "hob": _build_filter_hob,
    "internal": _build_filter_internal,
    "canister": _build_filter_canister,
}


# --------------------------------------------------------------------------- #
# Substrate + aquascape (multiplicity)
# --------------------------------------------------------------------------- #
def _emit_plant(sub, base, x, y, z_top, h, mats, i) -> None:
    """One plant cluster (stem + 2 leaves), rooted at gravel top ``z_top``."""
    key = ("plant_a", "plant_b", "plant_c")[i % 3]
    mat = mats[key]
    _wv(sub, Cylinder(radius=0.010, length=h), (x, y, z_top + h / 2.0 - 0.006), base, mat,
        f"plant_stem_{i}")
    _wv(sub, Box((0.060, 0.010, 0.030)), (x + 0.012, y, z_top + h * 0.9), base, mat,
        f"plant_leaf_{i}_0", rpy=(0.0, 0.45, 0.65))
    _wv(sub, Box((0.052, 0.010, 0.028)), (x - 0.012, y, z_top + h * 0.78), base, mat,
        f"plant_leaf_{i}_1", rpy=(0.0, -0.40, -0.65))


def _build_substrate(model, tank, g: TankGeom, r, mats) -> None:
    sub = model.part("substrate")
    base = (0.0, 0.0, g.inner_bottom_z)
    gravel = mats["gravel"]
    gravel_dark = mats["gravel_dark"]
    rock = mats["rock"]
    bed_h = 0.040
    z0 = g.inner_bottom_z  # gravel bed bottom ~ here (world)
    gravel_top = z0 + bed_h

    # substrate part frame is already at (0,0,inner_bottom_z) via its FIXED joint;
    # author gravel meshes in that LOCAL frame (bottom 2mm below the frame origin).
    if g.shape == "round":
        sub.visual(
            mesh_from_cadquery(_disc_mesh(g.open_r, bed_h, -0.002), "round_gravel_bed"),
            origin=Origin(), material=gravel, name="gravel_bed", material_class_id="stone.aggregate_ground",
        )
    elif g.shape == "hex":
        sub.visual(
            mesh_from_cadquery(_hex_plate_mesh(g.open_r + 0.01, bed_h, -0.002), "hex_gravel_bed"),
            origin=Origin(), material=gravel, name="gravel_bed", material_class_id="stone.aggregate_ground",
        )
    else:
        _wv(sub, Box((2 * g.open_half_w, 2 * g.open_half_d, bed_h)),
            (0.0, 0.0, z0 - 0.002 + bed_h / 2.0), base, gravel, "gravel_bed")

    # embedded pebble ridges (host-derived decoration)
    ridge_spots = (
        (-0.10, -0.05, gravel_dark), (0.05, 0.04, gravel), (0.10, -0.06, gravel_dark),
    )
    lim_w = g.open_half_w - 0.03
    lim_d = g.open_half_d - 0.03
    for i, (rx, ry, mat) in enumerate(ridge_spots):
        _wv(sub, Box((0.045, 0.024, 0.012)),
            (_clamp(rx, -lim_w, lim_w), _clamp(ry, -lim_d, lim_d), gravel_top - 0.004),
            base, mat, f"gravel_ridge_{i}")
    # two rocks (front/center)
    _wv(sub, Cylinder(radius=0.028, length=0.026),
        (_clamp(-0.02, -lim_w, lim_w), _clamp(-0.03, -lim_d, lim_d), gravel_top + 0.006),
        base, rock, "front_rock", rpy=(math.pi / 2.0, 0.0, 0.0))
    _wv(sub, Cylinder(radius=0.036, length=0.036),
        (_clamp(0.05, -lim_w, lim_w), _clamp(0.02, -lim_d, lim_d), gravel_top + 0.010),
        base, rock, "center_rock", rpy=(math.pi / 2.0, 0.0, 0.0))

    # N rooted plants distributed over the front ~240deg, inside the footprint,
    # away from the rear filter zone.
    n = r.plant_count
    place_r = min(g.open_half_w, g.open_half_d) * 0.62
    max_h = _clamp(r.glass_h * 0.5, 0.09, 0.16)
    for i in range(n):
        ang = math.radians(150.0 + (i / max(n - 1, 1)) * 240.0)  # front-weighted spread
        px = _clamp(place_r * math.cos(ang), -lim_w + 0.02, lim_w - 0.02)
        py = _clamp(place_r * math.sin(ang) - 0.02, -lim_d + 0.02, g.open_half_d * 0.25)
        h = max_h * (0.75 + 0.25 * ((i % 3) / 2.0))
        _emit_plant(sub, base, px, py, gravel_top, h, mats, i)

    model.articulation(
        "tank_to_substrate",
        ArticulationType.FIXED,
        parent=tank,
        child=sub,
        origin=Origin(xyz=(0.0, 0.0, g.inner_bottom_z)),
    )


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #
def build_aquarium(
    config: AquariumConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {key: model.material(f"aq_{key}_{r.palette_style}", rgba=rgba) for key, rgba in palette.items()}

    tank = model.part("tank_frame")
    g = _BODY_BUILDERS[r.body_form](tank, r, mats)

    _build_substrate(model, tank, g, r, mats)

    filt_origin = _FILTER_BUILDERS[r.filter](model, tank, g, r, mats)
    model.articulation(
        "tank_to_filter",
        ArticulationType.FIXED,
        parent=tank,
        child=model.get_part("filter"),
        origin=Origin(xyz=tuple(float(c) for c in filt_origin)),
    )

    _LID_BUILDERS[r.lid](model, tank, g, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["tank_geom"] = {"shape": g.shape, "top_z": g.top_z, "rim_top": g.rim_top}
    return model


def build_seeded_aquarium(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_aquarium(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def run_aquarium_tests(object_model: ArticulatedObject, config: AquariumConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    tank = object_model.get_part("tank_frame")
    substrate = object_model.get_part("substrate")
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("tank_frame present", "tank_frame" in part_names)
    ctx.check("substrate present", "substrate" in part_names)
    ctx.check("filter present", "filter" in part_names)
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )
    # transparent hollow basin: a glass element exists
    tank_visuals = {v.name for v in tank.visuals}
    ctx.check(
        "hollow glass basin modeled",
        any(
            v == "glass_wall" or v == "front_glass" or v.startswith("wall_glass")
            for v in tank_visuals
        ),
        details=f"tank visuals: {sorted(tank_visuals)[:6]}",
    )
    ctx.check("bottom_glass present", "bottom_glass" in tank_visuals)

    # gravel bed rests on the glass bottom
    ctx.expect_contact(
        substrate, tank, elem_a="gravel_bed", elem_b="bottom_glass",
        contact_tol=0.004, name="gravel bed rests on the glass bottom",
    )

    # plant multiplicity present + rooted within footprint
    sub_visuals = {v.name for v in substrate.visuals}
    ctx.check(
        f"all {r.plant_count} plant clusters present",
        all(
            f"plant_stem_{i}" in sub_visuals
            and f"plant_leaf_{i}_0" in sub_visuals
            and f"plant_leaf_{i}_1" in sub_visuals
            for i in range(r.plant_count)
        ),
        details=f"stems: {sorted(n for n in sub_visuals if n.startswith('plant_stem_'))}",
    )

    # --- lid mechanism, per type ---
    if r.lid == "hinged_hood":
        hood = object_model.get_part("hood")
        flap = object_model.get_part("feed_flap")
        hood_joint = object_model.get_articulation("tank_to_hood")
        flap_joint = object_model.get_articulation("hood_to_feed_flap")
        ctx.check(
            "hood hinge is revolute -X",
            hood_joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(hood_joint.axis) == (-1.0, 0.0, 0.0),
            details=f"{hood_joint.articulation_type}, axis={hood_joint.axis}",
        )
        ctx.expect_overlap(
            hood, tank, axes="xy", min_overlap=0.02, elem_a="hood_shell",
            elem_b="top_front_rail", name="hood covers the top frame footprint",
        )
        closed = ctx.part_element_world_aabb(hood, elem="hood_shell")
        with ctx.pose({hood_joint: hood_joint.motion_limits.upper}):
            opened = ctx.part_element_world_aabb(hood, elem="hood_shell")
        ctx.check(
            "hood hinge opens upward",
            closed is not None and opened is not None and opened[1][2] > closed[1][2] + 0.08,
            details=f"closed={closed}, open={opened}",
        )
        cflap = ctx.part_element_world_aabb(flap, elem="flap_panel")
        with ctx.pose({flap_joint: flap_joint.motion_limits.upper}):
            oflap = ctx.part_element_world_aabb(flap, elem="flap_panel")
        ctx.check(
            "feed flap opens upward",
            cflap is not None and oflap is not None and oflap[1][2] > cflap[1][2] + 0.03,
            details=f"closed={cflap}, open={oflap}",
        )
    elif r.lid == "sliding_cover":
        hood = object_model.get_part("hood")
        slide = object_model.get_articulation("tank_to_hood")
        ctx.check(
            "sliding cover is prismatic +Y",
            slide.articulation_type == ArticulationType.PRISMATIC
            and tuple(slide.axis) == (0.0, 1.0, 0.0),
            details=f"{slide.articulation_type}, axis={slide.axis}",
        )
        ctx.expect_overlap(
            hood, tank, axes="xy", min_overlap=0.02, elem_a="hood_shell",
            elem_b="top_front_rail", name="canopy covers the top frame footprint",
        )
        closed = ctx.part_world_position(hood)
        with ctx.pose({slide: slide.motion_limits.upper}):
            opened = ctx.part_world_position(hood)
        ctx.check(
            "canopy slides fore-aft along +Y at constant height",
            closed is not None and opened is not None
            and opened[1] > closed[1] + slide.motion_limits.upper - 0.005
            and abs(opened[2] - closed[2]) < 0.003,
            details=f"closed={closed}, open={opened}",
        )
    else:  # bifold_canopy
        lf = object_model.get_part("lid_leaf_front")
        lr = object_model.get_part("lid_leaf_rear")
        jf = object_model.get_articulation("tank_to_lid_leaf_front")
        jr = object_model.get_articulation("tank_to_lid_leaf_rear")
        for nm, leaf, joint in (("front", lf, jf), ("rear", lr, jr)):
            closed = ctx.part_element_world_aabb(leaf, elem=f"lid_leaf_{nm}_panel")
            with ctx.pose({joint: joint.motion_limits.upper}):
                opened = ctx.part_element_world_aabb(leaf, elem=f"lid_leaf_{nm}_panel")
            ctx.check(
                f"{nm} leaf opens upward",
                closed is not None and opened is not None and opened[1][2] > closed[1][2] + 0.06,
                details=f"closed={closed}, open={opened}",
            )
        # independence: opening the front leaf does not lift the rear leaf
        rest_rear = ctx.part_element_world_aabb(lr, elem="lid_leaf_rear_panel")
        with ctx.pose({jf: jf.motion_limits.upper}):
            rear_when_front_open = ctx.part_element_world_aabb(lr, elem="lid_leaf_rear_panel")
        ctx.check(
            "rear leaf stays closed when front leaf opens",
            rest_rear is not None and rear_when_front_open is not None
            and abs(rear_when_front_open[1][2] - rest_rear[1][2]) < 0.006,
            details=f"rest={rest_rear}, with_front_open={rear_when_front_open}",
        )

    ctx.check(
        "asset focuses on aquarium hardware not animals",
        all("fish" not in p.name and "animal" not in p.name for p in object_model.parts),
        details="No animal/character parts should be authored for this asset.",
    )

    # --- baseline + dynamic motion QC (Rule 5) ---
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


__all__ = (
    "AquariumConfig",
    "ResolvedAquariumConfig",
    "build_aquarium",
    "build_seeded_aquarium",
    "config_from_seed",
    "resolve_config",
    "run_aquarium_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)


def _material_class_id(material_name: str) -> str:
    if material_name.startswith("aq_glass_"):
        return "glass.clear_transparent"
    if material_name.startswith(("aq_frame_", "aq_dark_", "aq_canister_")):
        return "plastic.opaque_glossy_molded"
    if material_name.startswith(("aq_led_", "aq_red_", "aq_orange_", "aq_green_")):
        return "tech.emissive_surface"
    if material_name.startswith(("aq_gravel_", "aq_gravel_dark_")):
        return "stone.aggregate_ground"
    if material_name == "aq_rock_cool_blue":
        return "organic.coral_reef"
    if material_name.startswith("aq_rock_"):
        return "stone.rough_rock"
    if material_name.startswith(("aq_plant_a_", "aq_plant_b_", "aq_plant_c_")):
        return "organic.plant_leaf"
    if material_name.startswith("aq_hose_"):
        return "rubber.smooth_plain"
    raise ValueError(f"Unsupported aquarium material role: {material_name!r}")
